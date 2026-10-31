# Hardware Reverse Engineering: Infinix GT 20 Pro (X6871)

Authoritative hardware analysis derived directly from factory scatter files, extracted Device Tree Blobs (`dtb.img`), kernel module dependencies (`vendor_dlkm` / `odm_dlkm`), and Little Kernel bootloader configurations.

---

## 1. SoC & CPU Subsystem

| Parameter | Specification | Physical Address / Implementation |
| :--- | :--- | :--- |
| **SoC** | MediaTek MT6895 (Dimensity 8200 Ultimate) | 4nm TSMC Process |
| **CPU Cluster 0** | 1x ARM Cortex-A78 (Prime) | Up to 3.10 GHz, 512KB L2 |
| **CPU Cluster 1** | 3x ARM Cortex-A78 (Performance) | Up to 3.00 GHz, 512KB L2 per core |
| **CPU Cluster 2** | 4x ARM Cortex-A55 (Efficiency) | Up to 2.00 GHz, 128KB L2 per core |
| **Total L3 Cache** | 4 MB System Level Cache (SLC) | Shared across all 8 cores |
| **PSCI Method** | ARM PSCI v0.2+ | `smc #0` (Function IDs: `0xC4000003` for `CPU_ON`) |

---

## 2. Interrupt Controller (GIC-600)

The SoC incorporates an ARM Generic Interrupt Controller v3 (GIC-600):
- **GIC Distributor (`GICD`):** `0x0C000000` (64 KB)
- **GIC Redistributor (`GICR`):** `0x0C040000` (2 MB, 128 KB per CPU interface)
- **GIC CPU Interface (`GICC`):** `0x0C400000`
- **Timer PPI Interrupt:** IRQ 27 (Virtual Timer), IRQ 30 (Physical Timer)

---

## 3. Storage Architecture (UFS 3.1)

- **Controller Base:** `0x112B0000`
- **Compatible String:** `mediatek,mt8183-ufshci`, `jedec,ufs-2.0`
- **Bus Speed:** UFS 3.1 Gear 4 2-Lane
- **PMIC Regulators:** `mt6363_vufs18` (1.8V IO), `mt6363_vufs12` (1.2V Core)

---

## 4. Display Subsystem (144Hz AMOLED)

- **Display Panel:** 6.78-inch CSOT AMOLED, 144Hz Refresh Rate
- **Display Driver IC (DDIC):** Raydium RM69220
- **Resolution:** 1080 x 2436 pixels (392 PPI)
- **Color Depth:** 32-bit ARGB8888 (24-bit RGB + 8-bit Alpha)
- **Hardware Controller Bases:**
  - `MTK DSI Controller`: `0x14017000`
  - `Display Overlay (OVL0)`: `0x14002000`
  - `Display RDMA0`: `0x14006000`
- **Linear Framebuffer Base:** `0x70000000` (passed by Little Kernel)

---

## 5. Touchscreen Subsystem

Extracted from `/odm_dlkm/lib/modules/`:
- **Primary Driver:** `focaltech_ft3683g.ko` (FocalTech FT3683G I2C touch controller)
- **Secondary Driver:** `gt9916_common.ko` (Goodix GT9916 alternate touch controller)
- **I2C Bus Base:** `0x11D00000` (MTK I2C0)
- **Protocol:** Multi-touch point packets with coordinates, touch weight, and event flags

---

## 6. Power Management & Watchdog

- **PMIC Architecture:** Dual MediaTek PMICs: `MT6363` (Main) + `MT6375` (Sub/Charger)
- **SPMI Bus Base:** `0x1C804000`
- **MediaTek TOPRGU Watchdog:** `0x10007000`
  - `WDT_MODE`: `0x10007000` (Magic unlock key: `0x22000000`)
  - `WDT_RESTART`: `0x10007008` (Magic ping key: `0x1971`)
