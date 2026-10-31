#!/usr/bin/env python3
"""
Android LP Dynamic Partition & Region Image Analyzer
Compares Base super.img against Open super.img for Infinix GT 20 Pro (X6871 / MT6895).
Identifies regional customization images, partition groups, extents, and sizing differences.
"""

import os
import sys
import json
import struct
import argparse

LP_METADATA_MAGIC = 0x414C5030  # "0PLA" in ASCII little-endian
SPARSE_HEADER_MAGIC = 0xED26FF3A

def parse_sparse_and_lpm(img_path: str) -> dict:
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"File not found: {img_path}")

    file_size = os.path.getsize(img_path)
    result = {
        "path": img_path,
        "file_size": file_size,
        "partitions": {},
        "groups": [],
        "block_devices": []
    }

    with open(img_path, "rb") as f:
        magic, = struct.unpack("<I", f.read(4))
        f.seek(0)
        c1_data = None
        if magic == SPARSE_HEADER_MAGIC:
            header = f.read(28)
            magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, total_blks, total_chunks, _ = struct.unpack("<I4H4I", header)
            # Read first chunks to find LP metadata (typically chunk 1)
            for _ in range(min(5, total_chunks)):
                ch_hdr = f.read(12)
                c_type, reserved, c_sz, total_sz = struct.unpack("<2H2I", ch_hdr)
                data_sz = total_sz - 12
                if c_type == 0xCAC1: # Raw data chunk
                    chunk_data = f.read(data_sz)
                    if struct.pack("<I", LP_METADATA_MAGIC) in chunk_data:
                        c1_data = chunk_data
                        break
                else:
                    f.seek(data_sz, 1)
        else:
            # Raw super image
            f.seek(4096)
            c1_data = f.read(512 * 1024)

        if not c1_data:
            raise ValueError(f"Could not locate LP metadata header in {img_path}")

        meta_idx = c1_data.find(struct.pack("<I", LP_METADATA_MAGIC))
        if meta_idx == -1:
            raise ValueError(f"LP metadata signature not found in {img_path}")

        meta = c1_data[meta_idx:]
        magic, major, minor, hdr_sz = struct.unpack("<I2HI", meta[:12])
        # Descriptors: (offset, num_entries, entry_size)
        p_offset, p_num, p_size = struct.unpack("<3I", meta[80:92])
        e_offset, e_num, e_size = struct.unpack("<3I", meta[92:104])
        g_offset, g_num, g_size = struct.unpack("<3I", meta[104:116])

        p_base = meta_idx + hdr_sz + p_offset
        e_base = meta_idx + hdr_sz + e_offset
        g_base = meta_idx + hdr_sz + g_offset

        # Read Groups
        for i in range(g_num):
            g_entry = c1_data[g_base + i*g_size : g_base + (i+1)*g_size]
            g_name = g_entry[:36].rstrip(b"\x00").decode("utf-8", errors="ignore")
            max_size, = struct.unpack("<Q", g_entry[40:48])
            result["groups"].append({"name": g_name, "max_size_bytes": max_size})

        # Read Partitions & compute extent sizes
        for i in range(p_num):
            p_entry = c1_data[p_base + i*p_size : p_base + (i+1)*p_size]
            p_name = p_entry[:36].rstrip(b"\x00").decode("utf-8", errors="ignore")
            attrs, first_ext, num_ext, grp_idx = struct.unpack("<4I", p_entry[36:52])

            total_sectors = 0
            for ext_i in range(first_ext, first_ext + num_ext):
                ext_entry = c1_data[e_base + ext_i*e_size : e_base + (ext_i+1)*e_size]
                num_sec, target_type, target_data, target_src = struct.unpack("<Q2IQ", ext_entry[:24])
                total_sectors += num_sec

            size_bytes = total_sectors * 512
            size_mb = size_bytes / (1024 * 1024)
            result["partitions"][p_name] = {
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 2),
                "group_index": grp_idx,
                "num_extents": num_ext,
                "attributes": attrs
            }

    return result

def compare_supers(base_info: dict, open_info: dict) -> dict:
    diff_report = {
        "base_file_size": base_info["file_size"],
        "open_file_size": open_info["file_size"],
        "size_delta_bytes": open_info["file_size"] - base_info["file_size"],
        "size_delta_mb": round((open_info["file_size"] - base_info["file_size"]) / (1024 * 1024), 2),
        "partitions_comparison": {}
    }

    all_parts = sorted(set(base_info["partitions"].keys()) | set(open_info["partitions"].keys()))
    for p in all_parts:
        b = base_info["partitions"].get(p, {"size_mb": 0.0, "size_bytes": 0})
        o = open_info["partitions"].get(p, {"size_mb": 0.0, "size_bytes": 0})
        diff_mb = round(o["size_mb"] - b["size_mb"], 2)
        diff_report["partitions_comparison"][p] = {
            "base_mb": b["size_mb"],
            "open_mb": o["size_mb"],
            "diff_mb": diff_mb,
            "has_region_payload": diff_mb > 10.0 or (o["size_mb"] > 100.0 and b["size_mb"] < 1.0)
        }
    return diff_report

def main():
    parser = argparse.ArgumentParser(description="Analyze and compare Base and Open super.img partition structures")
    parser.add_argument("--base", default=r"C:\Users\Admin\Music\Mehrnn\Roms\X6871-16.3.0.155SP22(OP009PF001AZ)\super.img", help="Path to Base super.img")
    parser.add_argument("--open", default=r"C:\Users\Admin\Music\Mehrnn\Roms\X6871-16.3.0.155SP22(OP009PF001AZ)\Open\super.img", help="Path to Open super.img")
    parser.add_argument("--output-json", default="configs/super_comparison.json", help="Path to write JSON comparison")
    args = parser.parse_args()

    print("[*] Analyzing Base super image:", args.base)
    base_info = parse_sparse_and_lpm(args.base)
    print(f"    Base image: {base_info['file_size'] / (1024**3):.2f} GB, {len(base_info['partitions'])} dynamic partitions.")

    print("[*] Analyzing Open super image:", args.open)
    open_info = parse_sparse_and_lpm(args.open)
    print(f"    Open image: {open_info['file_size'] / (1024**3):.2f} GB, {len(open_info['partitions'])} dynamic partitions.")

    report = compare_supers(base_info, open_info)
    print("\n" + "=" * 70)
    print(f"{'Partition':<20} {'Base (MB)':<12} {'Open (MB)':<12} {'Delta (MB)':<12} {'Region Img?'}")
    print("=" * 70)
    for p, d in report["partitions_comparison"].items():
        if d["base_mb"] > 0 or d["open_mb"] > 0:
            reg = "[REGION IMG]" if d["has_region_payload"] else ""
            print(f"{p:<20} {d['base_mb']:<12.2f} {d['open_mb']:<12.2f} {d['diff_mb']:<12.2f} {reg}")
    print("=" * 70)

    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Detailed comparison report written to {args.output_json}")

if __name__ == "__main__":
    main()
