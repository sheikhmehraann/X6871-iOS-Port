# Apple iOS 16 / Darwin XNU Bring-Up for Infinix GT 20 Pro (X6871)

[![CI & Release Pipeline](https://github.com/sheikhmehraann/X6871-iOS-Port/actions/workflows/release.yml/badge.svg)](https://github.com/sheikhmehraann/X6871-iOS-Port/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-APSL%202.0%20%7C%20MIT-blue.svg)](docs/LICENSES.md)
[![Target](https://img.shields.io/badge/SoC-Dimensity%208200%20Ultimate%20(MT6895)-orange.svg)](docs/HARDWARE-REVERSE-ENGINEERING.md)
[![Status](https://img.shields.io/badge/Status-Experimental%20Bring--Up-yellow.svg)](docs/STATUS.md)

An open-source OS development and reverse-engineering research project bringing Apple's **Darwin XNU Kernel (v8796)** and genuine **iOS 16 userland** to the **Infinix GT 20 Pro (`X6871` / `x6871_h962`)**, powered by the **MediaTek Dimensity 8200 Ultimate (`MT6895`)**.

---

## 1. Architectural Strategy

```text
+---------------------------------------------------------------------------------+
|                       Official Apple IPSW: iOS 16.7.16                          |
|                       (iPhone X - Non-PAC Userland DMG)                         |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                    Neutralization & Userland Surgery                            |
|        - Strip watchdogd (SEP heartbeat panic bypass)                           |
|        - Strip CommCenter & basebandd (modem bus panic bypass)                  |
|        - Inject .SkipSetup token (bypass iCloud Activation Assistant)           |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                      Darwin XNU Kernel 8796 (Patched)                           |
|        - ARM GIC-600 Interrupt Routing for MT6895                               |
|        - High-speed UART0 Console Output (0x11002000)                           |
|        - Simple Linear Framebuffer Driver (1080x2436 @ 32bpp)                   |
|        - AMFI & Code-Signing Bypass (`cs_enforcement_disable=1`)                |
+---------------------------------------------------------------------------------+
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                      AOSP Header v4 Boot Shim & Packager                        |
|        - Fastboot RAM Boot Deployment (`fastboot boot xnu_boot.img`)            |
|        - Non-destructive to stock Android partitions and flash storage          |
+---------------------------------------------------------------------------------+
```

---

## 2. Target Hardware Specifications

| Component | Stock ROM Evidence | Physical Base Address / Value |
| :--- | :--- | :--- |
| **Device Model** | Infinix GT 20 Pro (`X6871`) | Project `x6871_h962` |
| **SoC** | MediaTek Dimensity 8200 Ultimate | `MT6895` (ARMv8.2-A) |
| **CPU Cluster** | 1x Cortex-A78 @ 3.1GHz + 3x Cortex-A78 @ 3.0GHz + 4x Cortex-A55 @ 2.0GHz | 8 Cores (PSCI `smc #0`) |
| **GPU** | ARM Mali-G610 MC6 | `0x13000000` (Valhall v10) |
| **DRAM Base** | 8GB / 12GB LPDDR5X | `0x40000000` |
| **Interrupt Controller** | ARM GIC-600 / GICv3 | `0x0C000000` (GICD), `0x0C040000` (GICR) |
| **Storage** | UFS 3.1 Host Controller | `0x112B0000` |
| **Display Panel** | 6.78" CSOT AMOLED, 144Hz Refresh Rate | Raydium RM69220 (`0x14017000`) |
| **Linear Framebuffer** | 1080 x 2436 @ 32bpp (Stride: 4320) | `0x70000000` |
| **Serial Console** | MediaTek UART0 | `0x11002000` (Baud: 921600) |
| **Touchscreen** | FocalTech FT3683G & Goodix GT9916 | `0x11D00000` (I2C) |
| **Hardware Watchdog** | MediaTek TOPRGU | `0x10007000` |

---

## 3. Project Directory Map

```text
X6871-iOS-Port/
├── .github/
│   └── workflows/              # Automated GitHub Actions build infrastructure
│       ├── download-firmware.yml
│       ├── extract-firmware.yml
│       ├── build-xnu.yml
│       ├── build-shim.yml
│       ├── build-ios-root.yml
│       ├── package-release.yml
│       └── release.yml
├── device/
│   └── x6871/                 # Board configuration, device topology, and fstab
├── kernel/
│   └── xnu/                   # MT6895 XNU platform layer and machine hooks
├── shim/                      # Freestanding ARM64 boot shim (LK -> XNU bridge)
├── drivers/                   # Hardware-specific driver implementations
│   ├── cpu/                   # PSCI SMC CPU topology and SMP management
│   ├── storage/               # UFS 3.1 HCI driver
│   ├── display/               # MediaTek DSI & Raydium RM69220 framebuffer
│   ├── touch/                 # FocalTech FT3683G & Goodix GT9916 touch decoder
│   ├── gpu/                   # Mali-G610 MC6 Valhall registers & power management
│   └── power/                 # MT6363/MT6375 PMIC SPMI & TOPRGU watchdog handling
├── userspace/                 # iOS 16 launchd surgery & .SkipSetup activation bypass
├── tools/
│   ├── download/              # FRBox automated downloader (Alibaba PDS)
│   ├── extract/               # Firmware unpacker & super.img region analyzer
│   ├── firmware/              # Apple Mach-O DeviceTree compiler & DTB parser
│   └── packaging/             # AOSP Header v4 packager & GoFile CDN uploader
├── patches/                   # Patches for apple-oss-distributions/xnu
├── configs/                   # Device trees, board definitions, and comparison data
├── docs/                      # Exhaustive technical documentation & reverse engineering
├── tests/                     # Automated unit and integration test suite
└── output/                    # Generated build artifacts (git-ignored)
```

---

## 4. Documentation Suite

- [BUILD.md](docs/BUILD.md): Toolchains, compilation steps, and fastboot deployment.
- [FIRMWARE-EXTRACTION.md](docs/FIRMWARE-EXTRACTION.md): FRBox download mechanics and the dual `super.img` region discovery.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): Boot pipeline, memory maps, MMU tables, and Apple `boot_args`.
- [HARDWARE-REVERSE-ENGINEERING.md](docs/HARDWARE-REVERSE-ENGINEERING.md): Authoritative hardware register maps.
- [XNU-PORTING.md](docs/XNU-PORTING.md): Apple Darwin 8796 kernel changes and research comparisons.
- [GPU-PORTING.md](docs/GPU-PORTING.md): Mali-G610 Valhall v10 analysis and 7 validation stages.
- [IOS-USERSPACE.md](docs/IOS-USERSPACE.md): Genuine iOS 16.7.16 userspace surgery and activation bypass.
- [GITHUB-ACTIONS.md](docs/GITHUB-ACTIONS.md): Workflow architecture, matrix, and runners.
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): Diagnostics, UART0 console capture, and watchdog panic bypass.
- [LICENSES.md](docs/LICENSES.md): APSL 2.0, Apache 2.0, and upstream attributions.
- [STATUS.md](docs/STATUS.md): Honest, unvarnished component support matrix.
- [EVIDENCE.md](docs/EVIDENCE.md): Immutable physical evidence (hashes, offsets, DTB dumps).

---

## 5. Ready-to-Flash iOS ROM Package

For immediate device bring-up on your Infinix GT 20 Pro:

- **Download Package:** [`X6871_iOS_ROM_Package.zip`](https://gofile.io/d/GCnGTf3P) (GoFile Public CDN)
- **SHA-256:** `d69fcdc40d832e7eecb65cebfefe4637e5f837359cb5bee2b478ee42ce0aae52`
- **Flashing Documentation:** [docs/FLASHING_GUIDE.md](docs/FLASHING_GUIDE.md)

### Package Contents:
1. `xnu_boot.img`: AOSP Header v4 boot image containing Apple Darwin XNU mach-kernel boot shim + compiled D22AP MT6895 DeviceTree.bin.
2. `DeviceTree.bin`: Compiled Apple Device Tree for MT6895 (GIC-600, UART0, UFS, Linear Framebuffer).
3. `flash_ios_rom.bat`: 1-Click interactive Windows Fastboot ROM flasher.
4. `flash_ios_rom.sh`: 1-Click interactive Linux/macOS bash flasher.
5. `build_ios_rootfs.py`: Automated cross-platform genuine iOS 16.7.16 RootFS builder with launchd surgery.
6. `launchd_surgery.py`: Hardware watchdog/baseband daemon neutralizer and .SkipSetup activation bypass token injector.
7. `README_FLASHING.md`: Complete step-by-step flashing instructions and safety checklist.
8. `super_comparison.json`: Detailed partition extent comparison between Base and Open `super.img`.

---

## 6. Quick Start

### 1. Run Test Suite (25 Unit Tests)
```bash
python3 -m unittest discover tests/ -p "test_*.py" -v
```

### 2. Compile Apple DeviceTree
```bash
python3 tools/firmware/build_devicetree.py --output output/DeviceTree.bin
```

### 3. Package AOSP Header v4 Boot Image
```bash
python3 tools/packaging/package_boot.py \
    --devicetree output/DeviceTree.bin \
    --output output/xnu_boot.img
```

### 4. 1-Click Fastboot Deployment
```bash
# Windows
flash_ios_rom.bat

# Linux / macOS
chmod +x tools/packaging/flash_ios_rom.sh
./tools/packaging/flash_ios_rom.sh
```

---

## 6. Upstream Research Attributions

Special thanks to the open-source engineering research of:
- [squeeeezy/HelioDarwin](https://github.com/squeeeezy/HelioDarwin) (MediaTek MT6789 XNU bring-up)
- [MakrSas/ios-topaz](https://github.com/MakrSas/ios-topaz) (Redmi Note 12 XNU bring-up)
- [dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet) (Redmi Note 10 Pro XNU bring-up)
- [UniXNU/UniXNU](https://github.com/UniXNU/UniXNU) (Non-Apple ARM64 XNU architecture)
- [MBuTT3178/device_infinix_X6871](https://github.com/MBuTT3178/device_infinix_X6871) (Infinix GT 20 Pro device tree)
