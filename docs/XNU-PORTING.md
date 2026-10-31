# XNU Kernel Porting: Adapting Apple Darwin 8796 to MediaTek MT6895

This document details the adaptation of Apple's open-source **Darwin XNU kernel (v8796)** to the MediaTek Dimensity 8200 on Infinix GT 20 Pro (X6871).

---

## 1. Upstream Research Projects & Comparative Analysis

Before porting, four key open-source research efforts were analyzed:

| Project | Target SoC | Target GPU | Upstream Base | Relevance to X6871 |
| :--- | :--- | :--- | :--- | :--- |
| **[HelioDarwin](https://github.com/squeeeezy/HelioDarwin)** | MediaTek MT6789 | Mali-G57 (Valhall v7) | ios-topaz / sweet | **Direct MTK ancestor**. Proves XNU bring-up on MediaTek LK, MTCMOS, and PWRAP. However, MT6895 uses Mali-G610 (v10) and GIC-600 rather than older GIC-500. |
| **[ios-topaz](https://github.com/MakrSas/ios-topaz)** | Snapdragon 685 (SM6225) | Adreno 610 | ios-sweet | Proved non-PAC ARMv8.0 XNU builds and unsealed userland surgery. |
| **[ios-sweet](https://github.com/dipa-studio/ios-sweet)** | Snapdragon 730G (SM7150) | Adreno 618 | XNU 8796 | Origin of builtin pthread, mockfs ramdisk root, and AMFI bypass. |
| **[UniXNU](https://github.com/UniXNU/UniXNU)** | Generic ARM64 | Various | EDK2 / UEFI | Demonstrates UEFI boot path, whereas X6871 uses direct Little Kernel ramdisk boot. |

---

## 2. Platform Architecture Differences: MT6789 vs MT6895

| Subsystem | HelioDarwin (MT6789) | X6871 Port (MT6895) | Engineering Implication |
| :--- | :--- | :--- | :--- |
| **CPU Architecture** | 2x Cortex-A76 + 6x Cortex-A55 | 4x Cortex-A78 + 4x Cortex-A55 | MT6895 requires `-mcpu=cortex-a78` compiler target and updated cache line definitions. |
| **Interrupt Controller** | ARM GIC-500 (GICv2/v3 hybrid) | ARM GIC-600 (Pure GICv3) | Requires GICv3 system register access (`ICC_*_EL1`) rather than memory-mapped GICC registers. |
| **GPU Architecture** | Mali-G57 MC2 (Valhall v7) | Mali-G610 MC6 (Valhall v10) | Completely different register layout and job submission rings; cannot reuse G57 driver directly. |
| **Storage Host** | eMMC 5.1 / UFS 2.2 | UFS 3.1 Gear 4 | Faster command completion rings and different PMIC voltage rails. |
| **Display DDIC** | FocalTech / Novatek 60/120Hz | Raydium RM69220 144Hz AMOLED | High-bandwidth MIPI DSI timing and linear framebuffer stride. |

---

## 3. Required Kernel Modifications in XNU 8796

### 1. ARM GIC-600 Interrupt Support
In standard Apple Silicon (`t8015` / `t8101`), Apple uses proprietary AIC (Apple Interrupt Controller). Our patch routes interrupts through standard ARM GICv3 system registers:
- `ICC_PMR_EL1`: Priority Mask
- `ICC_CTLR_EL1`: Controller Control
- `ICC_IGRPEN1_EL1`: Group 1 Enable
- `ICC_IAR1_EL1` / `ICC_EOIR1_EL1`: Interrupt Acknowledge & End Of Interrupt

### 2. High-Speed UART0 Console Hook
Redirect early panic output and `kprintf` to MTK UART0 at physical address `0x11002000` via [kernel/xnu/mt6895_platform.c](file:///kernel/xnu/mt6895_platform.c).

### 3. AMFI & Code-Signing Enforcement Bypass
Patched `bsd/kern/kern_exec.c` to parse `cs_enforcement_disable=1` from `boot-args`. This bypasses strict Mach-O CDHash verification and allows running neutralized binaries without valid Apple certificates.

### 4. Unsealed HFS+ / APFS Root Volume Mount
Patched `bsd/vfs/vfs_mount.c` to permit mounting unsealed filesystems when `amfi_get_out_of_my_way=1` is passed, avoiding boot panics caused by missing Apple SEP trust cache signatures.
