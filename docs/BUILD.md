# Building the Native iOS Port for Infinix GT 20 Pro (X6871)

This document describes how to compile the Boot Shim, Apple DeviceTree, Darwin XNU Kernel, and package the AOSP Header v4 boot image.

---

## 1. Prerequisites

### Host System
- **Linux:** Ubuntu 22.04 LTS, Debian 12, or Windows WSL2
- **macOS:** macOS 14 Sonoma (for full native Darwin XNU compilation with Apple Xcode 15 / iig)
- **Windows:** PowerShell 7+ for packaging and deployment scripts

### Toolchain Dependencies
```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y git build-essential gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu \
    python3 python3-pip cmake ninja-build ccache dmg2img

# macOS
brew install cmake ninja ccache jq gum bash
```

---

## 2. Compiling the ARM64 Boot Shim

The boot shim is freestanding ARM64 code that executes at physical DRAM base `0x40080000`, initializes the serial console, sets up identity MMU mapping, populates Apple `boot_args`, and jumps to XNU.

```bash
cd shim
make CROSS_COMPILE=aarch64-linux-gnu-
```

Expected outputs:
- `shim/boot_shim.elf`: ELF executable with symbols
- `shim/boot_shim.bin`: Raw flat binary (~8 KB)

---

## 3. Generating Apple DeviceTree

Compile the binary Apple DeviceTree spoofing iPhone X (`D22AP` / `Apple,A11`) with MediaTek MT6895 register addresses:

```bash
python3 tools/firmware/build_devicetree.py --output output/DeviceTree.bin
```

Validation:
- Output size: ~2,488 bytes
- Contains nodes: `/chosen`, `/memory`, `/framebuffer`, `/arm-io`, `/arm-io/interrupt-controller`, `/arm-io/uart0`, `/arm-io/ufs`, `/arm-io/mali-gpu`, `/cpus`.

---

## 4. Packaging the Boot Image (Header Version 4)

Package the boot shim (or compiled `mach_kernel`) and the Apple `DeviceTree.bin` into an Android Boot Image Header v4:

```bash
python3 tools/packaging/package_boot.py \
    --kernel shim/boot_shim.bin \
    --devicetree output/DeviceTree.bin \
    --output output/xnu_boot.img
```

Validation:
- Magic: `ANDROID!`
- Header Version: 4
- Page alignment: 4096 bytes
- Output size: 16,384 bytes (or size with kernel)

---

## 5. Running the Automated Test Suite

Run all verification tests across downloader, DTB parsing, DeviceTree generator, boot packager, and userspace surgery:

```bash
python3 -m unittest discover tests/ -p "test_*.py" -v
```

---

## 6. Fastboot RAM Boot Deployment (Non-Destructive)

Ensure your bootloader is unlocked (`fastboot flashing unlock`), place the device in Fastboot mode, and boot into DRAM:

```bash
# Windows
tools\packaging\flash_port.bat

# Linux / macOS
fastboot boot output/xnu_boot.img
```
*Note: This command loads the image into volatile memory and does not flash internal storage.*
