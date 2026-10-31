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

def main():
    parser = argparse.ArgumentParser(description="Extract and inspect Infinix GT 20 Pro firmware binaries")
    parser.add_argument("--rom-dir", default=r"C:\Users\Admin\Music\Mehrnn\Roms\X6871-16.3.0.155SP22(OP009PF001AZ)", help="Path to unpacked stock ROM directory")
    parser.add_argument("--out-dir", default="output/extracted", help="Directory to save extracted artifacts")
    args = parser.parse_args()

    print("[*] Inspecting firmware at:", args.rom_dir)
    manifest = {"partitions": [], "boot": {}, "vendor_boot": {}}

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

    manifest_path = os.path.join(args.out_dir, "firmware_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Extraction manifest written to {manifest_path}")

if __name__ == "__main__":
    main()
