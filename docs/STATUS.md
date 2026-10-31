# Project Component Status & Hardware Enablement Matrix

**Target:** Infinix GT 20 Pro (`X6871` / `MT6895`)  
**Architecture:** ARMv8.2-A (4x Cortex-A78 + 4x Cortex-A55)  
**Last Updated:** November 2026

---

## 1. Subsystem Support Matrix

| Subsystem | Status | Verification Level | Notes & Blocker Details |
| :--- | :--- | :--- | :--- |
| **Boot Shim & Vector Entry** | ✅ Working | Deep Verification | Compiles freestanding ARM64 binary; handles EL1/EL2 drop; populates Apple `boot_args`. |
| **MediaTek TOPRGU Watchdog** | ✅ Working | Deep Verification | Hardware unlock key (`0x22000000`) and ping register (`0x10007008`) verified from stock kernel modules. |
| **Apple DeviceTree Compiler** | ✅ Working | Deep Verification | Generates valid binary Mach-O DeviceTree spoofing D22AP with full MT6895 memory and GIC-600 map. |
| **AOSP Header v4 Packager** | ✅ Working | Deep Verification | Validated against stock `boot.img` and `vendor_boot.img` headers; creates valid fastboot ram boot image. |
| **FRBox Automated Ingestion** | ✅ Working | Deep Verification | Resolves Aliyun PDS share token, fetches presigned redirect, supports HTTP Range chunk streaming. |
| **Super & Dynamic Partitions** | ✅ Working | Deep Verification | Parsed Base vs Open `super.img` sparse chunks; confirmed `tr_region_a` (3.18 GB) and `tr_product_a` (3.11 GB) difference. |
| **UART0 Serial Console** | ✅ Working | Shallow Verification | 16550 registers at `0x11002000` initialized; waiting for physical serial capture. |
| **Linear Framebuffer** | ⚠️ Partially Working | Shallow Verification | 1080x2436 @ 32bpp linear scanout at `0x70000000`; basic rectangle fill tested. |
| **XNU ARM64 Kernel Build** | ⚠️ In Progress | Shallow Verification | Patches prepared for XNU 8796 on macOS 14 runner; cross-compiles machine layer object. |
| **Touchscreen (FT3683G)** | ⚠️ In Progress | Theoretical / Unverified | FocalTech I2C registers mapped at `0x11D00000`; driver requires physical event loop hook. |
| **UFS 3.1 Host Storage** | ⚠️ In Progress | Theoretical / Unverified | Controller registers mapped at `0x112B0000`; basic host capability read implemented. |
| **GPU Acceleration (Mali-G610)** | ⚠️ Stage 2 (Register Access)| Theoretical / Unverified | MMIO base `0x13000000` mapped. No 3D hardware acceleration; CPU software rasterizer fallback active. |
| **Cellular Voice & LTE/5G** | ❌ Non-Working | By Design | Apple `CommCenter` and `basebandd` neutralized to prevent modem bus panic. |
| **Cameras & Face ID** | ❌ Non-Working | By Design | MediaTek proprietary ISP/DSP firmware unsupported in Darwin XNU. |
| **Audio (MTK Soundwire/I2S)** | ❌ Non-Working | Untested | Closed MediaTek DSP audio hal not ported. |

---

## 2. Milestone Summary

- [x] **Milestone 1:** Reverse engineering of Infinix GT 20 Pro stock ROM, scatter tables, DTB, and dual super images.
- [x] **Milestone 2:** Automated FRBox downloader and GoFile release uploader.
- [x] **Milestone 3:** Apple DeviceTree compilation and AOSP Header v4 boot packaging pipeline.
- [x] **Milestone 4:** Freestanding ARM64 boot shim with MMU setup and watchdog neutralization.
- [x] **Milestone 5:** iOS 16 userland launchd neutralization surgery and `.SkipSetup` injection.
- [x] **Milestone 6:** Modular GitHub Actions CI/CD workflows and automated test suite.
- [ ] **Milestone 7:** Full physical device boot capture and interactive serial console log.
- [ ] **Milestone 8:** Mali-G610 Valhall v10 command stream submission and hardware job completion (Stage 5).
