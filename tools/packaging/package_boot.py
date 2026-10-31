#!/usr/bin/env python3
"""
Android Boot Image v4 Packager for MediaTek MT6895 (Dimensity 8200)
Packages Apple Darwin XNU mach_kernel / boot shim + DeviceTree.bin into
an AOSP Header Version 4 boot image for fastboot boot testing.
"""

import os
import sys
import struct
import argparse
from pathlib import Path

PAGE_SIZE = 4096
DEFAULT_CMDLINE = (
    "debug=0x14e serial=3 -v keepsyms=1 "
    "amfi_get_out_of_my_way=1 cs_enforcement_disable=1 "
    "bootopt=64S3,32N2,64N2"
)

def align(size: int, page_size: int = PAGE_SIZE) -> int:
    return (size + page_size - 1) & ~(page_size - 1)

def build_boot_img_v4(kernel_bytes: bytes, ramdisk_bytes: bytes, output_path: str, cmdline: str = DEFAULT_CMDLINE):
    magic = b"ANDROID!"
    kernel_size = len(kernel_bytes)
    ramdisk_size = len(ramdisk_bytes)
    os_version = 0
    header_size = 4096
    header_version = 4

    cmdline_bytes = cmdline.encode("utf-8")[:1535] + b"\x00"
    cmdline_padded = cmdline_bytes.ljust(1536, b"\x00")

    header = struct.pack(
        "<8sIIII4s4s4s4sI1536s",
        magic,
        kernel_size,
        ramdisk_size,
        os_version,
        header_size,
        b"\x00"*4, b"\x00"*4, b"\x00"*4, b"\x00"*4,
        header_version,
        cmdline_padded
    )
    header = header.ljust(header_size, b"\x00")

    kernel_padded = kernel_bytes.ljust(align(kernel_size), b"\x00")
    ramdisk_padded = ramdisk_bytes.ljust(align(ramdisk_size), b"\x00")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(kernel_padded)
        f.write(ramdisk_padded)

    total_sz = os.path.getsize(output_path)
    print(f"[+] Successfully generated Android Boot Image (v4): {output_path}")
    print(f"    Total Size: {total_sz:,} bytes")
    print(f"    Kernel Size: {kernel_size:,} bytes")
    print(f"    Ramdisk/DeviceTree: {ramdisk_size:,} bytes")
    print(f"    Cmdline: {cmdline}")

def main():
    parser = argparse.ArgumentParser(description="Package XNU / Boot shim and DeviceTree into AOSP v4 boot.img")
    parser.add_argument("--kernel", default="", help="Path to compiled mach_kernel or boot shim ELF/binary")
    parser.add_argument("--devicetree", default="output/DeviceTree.bin", help="Path to compiled Apple DeviceTree.bin")
    parser.add_argument("--cmdline", default=DEFAULT_CMDLINE, help="Kernel command line string")
    parser.add_argument("--output", default="output/xnu_boot.img", help="Output boot.img path")
    args = parser.parse_args()

    # Kernel resolution: use provided or fallback to stub
    if args.kernel and os.path.exists(args.kernel):
        with open(args.kernel, "rb") as f:
            kernel_bytes = f.read()
    else:
        print("[!] No kernel binary specified or found. Using Mach-O 64-bit verification stub.")
        kernel_bytes = b"\xCF\xFA\xED\xFE" + b"\x00" * 4092

    # DeviceTree resolution
    if os.path.exists(args.devicetree):
        with open(args.devicetree, "rb") as f:
            dt_bytes = f.read()
    else:
        print("[!] DeviceTree.bin not found. Compiling automatically...")
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "firmware"))
        import build_devicetree
        dt_bytes = build_devicetree.generate_mt6895_devicetree()

    build_boot_img_v4(kernel_bytes, dt_bytes, args.output, args.cmdline)

if __name__ == "__main__":
    main()
