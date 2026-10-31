#!/usr/bin/env python3
"""
Apple DeviceTree Binary Generator for MediaTek MT6895 (Dimensity 8200)
Spoofs iPhone X (D22AP / iPhone10,3) for Darwin XNU 8796 on Infinix GT 20 Pro (X6871).

Constructs the Mach-O Apple DeviceTree with full hardware mapping:
- chosen (boot-args: "-v debug=0x14e keepsyms=1 amfi_get_out_of_my_way=1 cs_enforcement_disable=1")
- memory (8GB/12GB LPDDR5 at physical DRAM base 0x40000000)
- arm-io (GIC-600 distributor 0x0C000000, redistributor 0x0C040000, UART0 0x11002000, UFS 0x112B0000)
- display / framebuffer (1080x2436 @ 32bpp linear scanout at 0x70000000)
- cpus (8 ARMv8.2-A cores: 4x Cortex-A78 + 4x Cortex-A55)
- gpu (Mali-G610 MC6 Valhall v10 interface at 0x13000000)
"""

import os
import sys
import struct
import argparse
from pathlib import Path

def align4(n: int) -> int:
    return (n + 3) & ~3

def pack_property(name: str, value: bytes) -> bytes:
    name_bytes = name.encode("utf-8") + b"\x00"
    name_padded = name_bytes.ljust(align4(len(name_bytes)), b"\x00")
    val_padded = value.ljust(align4(len(value)), b"\x00")
    # In Apple Device Tree: length has MSB set to 0x80000000 for placeholder or length
    header = struct.pack("<I", len(value))
    return name_padded + header + val_padded

def build_node(name: str, properties: dict, children: list = None) -> bytes:
    name_bytes = name.encode("utf-8") + b"\x00"
    name_padded = name_bytes.ljust(align4(len(name_bytes)), b"\x00")

    num_props = len(properties)
    num_children = len(children) if children else 0
    header = struct.pack("<II", num_props, num_children)

    props_data = b""
    for k, v in properties.items():
        if isinstance(v, str):
            v_bytes = v.encode("utf-8") + b"\x00"
        elif isinstance(v, int):
            v_bytes = struct.pack("<I", v)
        elif isinstance(v, bytes):
            v_bytes = v
        else:
            raise TypeError(f"Unsupported property type: {type(v)}")
        props_data += pack_property(k, v_bytes)

    children_data = b"".join(children) if children else b""
    return name_padded + header + props_data + children_data

def generate_mt6895_devicetree() -> bytes:
    # 1. Chosen node (boot parameters)
    chosen_props = {
        "boot-args": "-v debug=0x14e keepsyms=1 amfi_get_out_of_my_way=1 cs_enforcement_disable=1 serial=3 cpus=1",
        "firmware-version": "iBoot-8419.140.9",
        "random-seed": b"\x5a" * 32,
        "clock-frequency": struct.pack("<I", 26000000)
    }
    chosen_node = build_node("chosen", chosen_props)

    # 2. Memory node (DRAM physical base 0x40000000, 8GB size)
    memory_props = {
        "name": "memory",
        "device_type": "memory",
        "reg": struct.pack("<QQ", 0x40000000, 0x200000000) # 8GB LPDDR5
    }
    memory_node = build_node("memory", memory_props)

    # 3. Framebuffer node (AMOLED 1080x2436 @ 32bpp)
    fb_props = {
        "name": "framebuffer",
        "device_type": "display",
        "width": 1080,
        "height": 2436,
        "depth": 32,
        "linebytes": 1080 * 4,
        "base-address": struct.pack("<Q", 0x70000000)
    }
    fb_node = build_node("framebuffer", fb_props)

    # 4. GIC Interrupt Controller & Peripherals under arm-io
    gic_props = {
        "name": "interrupt-controller",
        "interrupt-controller": b"",
        "reg": struct.pack("<QQQQ", 0x0C000000, 0x10000, 0x0C040000, 0x200000)
    }
    gic_node = build_node("interrupt-controller", gic_props)

    uart_props = {
        "name": "uart0",
        "device_type": "serial",
        "reg": struct.pack("<QQ", 0x11002000, 0x1000),
        "clock-frequency": struct.pack("<I", 26000000),
        "current-speed": struct.pack("<I", 921600)
    }
    uart_node = build_node("uart0", uart_props)

    ufs_props = {
        "name": "ufs",
        "device_type": "storage",
        "reg": struct.pack("<QQ", 0x112B0000, 0x10000),
        "compatible": b"mediatek,mt8183-ufshci\x00jedec,ufs-2.0\x00"
    }
    ufs_node = build_node("ufs", ufs_props)

    gpu_props = {
        "name": "mali-gpu",
        "device_type": "gpu",
        "reg": struct.pack("<QQ", 0x13000000, 0x100000),
        "compatible": b"arm,mali-valhall\x00arm,mali-g610\x00"
    }
    gpu_node = build_node("mali-gpu", gpu_props)

    arm_io_props = {
        "name": "arm-io",
        "ranges": b"",
        "device_type": "soc"
    }
    arm_io_node = build_node("arm-io", arm_io_props, [gic_node, uart_node, ufs_node, gpu_node])

    # 5. CPUs Node (8 cores: 4x Cortex-A78 + 4x Cortex-A55)
    cpu_nodes = []
    for i in range(8):
        c_name = f"cpu{i}"
        is_big = (i >= 4)
        c_props = {
            "name": c_name,
            "device_type": "cpu",
            "reg": struct.pack("<I", i),
            "clock-frequency": struct.pack("<I", 3100000000 if is_big else 2000000000),
            "timebase-frequency": struct.pack("<I", 26000000),
            "state": "running" if i == 0 else "disabled"
        }
        cpu_nodes.append(build_node(c_name, c_props))

    cpus_node = build_node("cpus", {"name": "cpus"}, cpu_nodes)

    # 6. Root Device Tree
    root_props = {
        "compatible": b"Apple,iPhone10,3\x00Apple,A11\x00Apple,D22AP\x00",
        "model": "D22AP",
        "target-type": "D22AP",
        "serial-number": "MT6895-X6871-DARWIN",
        "platform-name": "t8015",
        "clock-frequency": struct.pack("<I", 3100000000)
    }

    return build_node("device-tree", root_props, [chosen_node, memory_node, fb_node, arm_io_node, cpus_node])

def main():
    parser = argparse.ArgumentParser(description="Apple DeviceTree Binary Generator for MT6895")
    parser.add_argument("--output", default="output/DeviceTree.bin", help="Path to write compiled DeviceTree.bin")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    dtb_bytes = generate_mt6895_devicetree()
    with open(args.output, "wb") as f:
        f.write(dtb_bytes)
    print(f"[+] Successfully built Darwin DeviceTree: {args.output} ({len(dtb_bytes):,} bytes)")

if __name__ == "__main__":
    main()
