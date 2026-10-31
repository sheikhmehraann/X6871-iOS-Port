#!/usr/bin/env python3
"""
Firmware Extractor & Hardware Artifact Analyzer for Infinix GT 20 Pro (X6871 / MT6895)
Extracts and dissects:
- boot.img (Header v4, kernel offset, kernel extraction)
- vendor_boot.img (Header v4, vendor ramdisk, DTB extraction)
- dtbo.img (Device Tree Blob Overlay table)
- Scatter tables (MT6895_Android_scatter.txt/xml)
"""

import os
import sys
import json
import struct
import argparse

def parse_scatter_txt(scatter_path: str) -> list:
    partitions = []
    if not os.path.exists(scatter_path):
        return partitions

    with open(scatter_path, "r", encoding="utf-8", errors="ignore") as f:
        current_part = {}
        for line in f:
            line = line.strip()
            if not line:
                if current_part and "partition_name" in current_part:
                    partitions.append(current_part)
                    current_part = {}
                continue
            if ":" in line:
                key, val = [x.strip() for x in line.split(":", 1)]
                current_part[key] = val
        if current_part and "partition_name" in current_part:
            partitions.append(current_part)
    return partitions

def unpack_boot_v4(boot_path: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    with open(boot_path, "rb") as f:
        magic = f.read(8)
        if magic != b"ANDROID!":
            raise ValueError(f"Invalid boot magic in {boot_path}: {magic}")

        k_sz, rd_sz, os_ver, hdr_sz = struct.unpack("<4I", f.read(16))
        f.seek(40)
        hdr_ver, = struct.unpack("<I", f.read(4))

        page_size = 4096
        hdr_pages = (hdr_sz + page_size - 1) // page_size
        k_offset = hdr_pages * page_size
        f.seek(k_offset)
        kernel_data = f.read(k_sz)

        k_path = os.path.join(out_dir, "kernel")
        with open(k_path, "wb") as kf:
            kf.write(kernel_data)

        info = {
            "header_version": hdr_ver,
            "kernel_size": k_sz,
            "ramdisk_size": rd_sz,
            "header_size": hdr_sz,
            "kernel_output": k_path
        }
        return info

def unpack_vendor_boot_v4(vendor_boot_path: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    with open(vendor_boot_path, "rb") as f:
        magic = f.read(8)
        if magic != b"VNDRBOOT":
            raise ValueError(f"Invalid vendor_boot magic in {vendor_boot_path}: {magic}")

        hdr_ver, pg_sz, k_addr, rd_addr, rd_sz = struct.unpack("<5I", f.read(20))
        cmdline = f.read(2048).rstrip(b"\x00").decode("utf-8", errors="ignore")
        tags_addr, = struct.unpack("<I", f.read(4))
        name = f.read(16).rstrip(b"\x00").decode("utf-8", errors="ignore")
        hdr_sz, dtb_sz = struct.unpack("<2I", f.read(8))
        dtb_addr, = struct.unpack("<Q", f.read(8))

        hdr_pages = (hdr_sz + pg_sz - 1) // pg_sz
        rd_pages = (rd_sz + pg_sz - 1) // pg_sz

        # Read Ramdisk
        rd_offset = hdr_pages * pg_sz
        f.seek(rd_offset)
        ramdisk_data = f.read(rd_sz)
        rd_path = os.path.join(out_dir, "vendor_ramdisk.cpio.lz4")
        with open(rd_path, "wb") as rf:
            rf.write(ramdisk_data)

        # Read DTB
        dtb_offset = (hdr_pages + rd_pages) * pg_sz
        f.seek(dtb_offset)
        dtb_data = f.read(dtb_sz)
        dtb_path = os.path.join(out_dir, "dtb.img")
        with open(dtb_path, "wb") as df:
            df.write(dtb_data)

        info = {
            "header_version": hdr_ver,
            "page_size": pg_sz,
            "kernel_addr": hex(k_addr),
            "ramdisk_addr": hex(rd_addr),
            "tags_addr": hex(tags_addr),
            "dtb_addr": hex(dtb_addr),
            "dtb_size": dtb_sz,
            "ramdisk_size": rd_sz,
            "cmdline": cmdline,
            "dtb_output": dtb_path,
            "ramdisk_output": rd_path
        }
        return info

def unpack_dtbo(dtbo_path: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    with open(dtbo_path, "rb") as f:
        data = f.read()

    if len(data) < 32:
        raise ValueError("dtbo image too small")

    magic, = struct.unpack(">I", data[:4])
    if magic != 0xD7B7AB1E:
        raise ValueError(f"Invalid dtbo magic: {hex(magic)}")

    magic, total_sz, hdr_sz, entry_sz, count, off, pg_sz, ver = struct.unpack(">8I", data[:32])
    extracted_entries = []

    for i in range(count):
        e_pos = off + i * entry_sz
        dt_sz, dt_off, dt_id, dt_rev, dt_custom = struct.unpack(">5I", data[e_pos:e_pos+20])
        entry_blob = data[dt_off : dt_off + dt_sz]
        out_dtbo = os.path.join(out_dir, f"dtbo_{i}.dtb")
        with open(out_dtbo, "wb") as ef:
            ef.write(entry_blob)
        extracted_entries.append({
            "index": i,
            "size": dt_sz,
            "offset": dt_off,
            "id": hex(dt_id),
            "rev": hex(dt_rev),
            "output": out_dtbo
        })

    return {
        "magic": hex(magic),
        "total_size": total_sz,
        "entry_count": count,
        "page_size": pg_sz,
        "version": ver,
        "entries": extracted_entries
    }

def inspect_vbmeta(vbmeta_path: str) -> dict:
    if not os.path.exists(vbmeta_path):
        return {}
    with open(vbmeta_path, "rb") as f:
        magic = f.read(4)
        if magic != b"AVB0":
            return {"valid": False, "magic": str(magic)}
        f.seek(4)
        req_ver_major, req_ver_minor = struct.unpack(">2I", f.read(8))
        auth_blk_sz, aux_blk_sz = struct.unpack(">2Q", f.read(16))
        f.seek(128)
        release_str = f.read(48).rstrip(b"\x00").decode("utf-8", errors="ignore")
        return {
            "valid": True,
            "magic": "AVB0",
            "avb_version": f"{req_ver_major}.{req_ver_minor}",
            "auth_block_size": auth_blk_sz,
            "aux_block_size": aux_blk_sz,
            "release_string": release_str
        }

def inspect_lk(lk_path: str) -> dict:
    if not os.path.exists(lk_path):
        return {}
    with open(lk_path, "rb") as f:
        magic, dsize, name = struct.unpack("<II32s", f.read(40))
        # MTK image magic is 0x58881688
        valid = (magic == 0x58881688)
        return {
            "valid": valid,
            "magic": hex(magic),
            "dsize": dsize,
            "name": name.rstrip(b"\x00").decode("utf-8", errors="ignore"),
            "file_size": os.path.getsize(lk_path)
        }

def main():
    parser = argparse.ArgumentParser(description="Extract and inspect Infinix GT 20 Pro firmware binaries")
    parser.add_argument("--rom-dir", default=r"C:\Users\Admin\Music\Mehrnn\Roms\X6871-16.3.0.155SP22(OP009PF001AZ)", help="Path to unpacked stock ROM directory")
    parser.add_argument("--out-dir", default="output/extracted", help="Directory to save extracted artifacts")
    args = parser.parse_args()

    print("[*] Inspecting firmware at:", args.rom_dir)
    manifest = {
        "partitions": [],
        "boot": {},
        "vendor_boot": {},
        "dtbo": {},
        "vbmeta": {},
        "lk": {}
    }

    scatter_txt = os.path.join(args.rom_dir, "MT6895_Android_scatter.txt")
    if os.path.exists(scatter_txt):
        print("[+] Found scatter file. Parsing partitions...")
        parts = parse_scatter_txt(scatter_txt)
        manifest["partitions"] = parts
        print(f"    Loaded {len(parts)} scatter partition definitions.")

    boot_img = os.path.join(args.rom_dir, "boot.img")
    if os.path.exists(boot_img):
        print("[+] Unpacking boot.img...")
        boot_info = unpack_boot_v4(boot_img, os.path.join(args.out_dir, "boot"))
        manifest["boot"] = boot_info
        print(f"    Kernel Size: {boot_info['kernel_size']:,} bytes, Version v{boot_info['header_version']}")

    vendor_boot = os.path.join(args.rom_dir, "vendor_boot.img")
    if os.path.exists(vendor_boot):
        print("[+] Unpacking vendor_boot.img...")
        vb_info = unpack_vendor_boot_v4(vendor_boot, os.path.join(args.out_dir, "vendor_boot"))
        manifest["vendor_boot"] = vb_info
        print(f"    Kernel Base: {vb_info['kernel_addr']}, Ramdisk Base: {vb_info['ramdisk_addr']}")
        print(f"    DTB Addr: {vb_info['dtb_addr']}, DTB Size: {vb_info['dtb_size']:,} bytes")
        print(f"    Cmdline: {vb_info['cmdline']}")

    dtbo_img = os.path.join(args.rom_dir, "dtbo.img")
    if os.path.exists(dtbo_img):
        print("[+] Unpacking dtbo.img...")
        dtbo_info = unpack_dtbo(dtbo_img, os.path.join(args.out_dir, "dtbo"))
        manifest["dtbo"] = dtbo_info
        print(f"    DTBO entries: {dtbo_info['entry_count']}, total size: {dtbo_info['total_size']:,} bytes")

    vbmeta_img = os.path.join(args.rom_dir, "vbmeta.img")
    if os.path.exists(vbmeta_img):
        print("[+] Inspecting vbmeta.img...")
        manifest["vbmeta"] = inspect_vbmeta(vbmeta_img)
        print(f"    AVB format: {manifest['vbmeta'].get('avb_version')}, release: {manifest['vbmeta'].get('release_string')}")

    lk_img = os.path.join(args.rom_dir, "lk.img")
    if os.path.exists(lk_img):
        print("[+] Inspecting lk.img...")
        manifest["lk"] = inspect_lk(lk_img)
        print(f"    MediaTek LK: {manifest['lk'].get('name')}, size: {manifest['lk'].get('dsize'):,} bytes")

    manifest_path = os.path.join(args.out_dir, "firmware_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Extraction manifest written to {manifest_path}")

if __name__ == "__main__":
    main()
