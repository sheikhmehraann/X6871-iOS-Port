# Technical Architecture: Native Darwin XNU on MediaTek MT6895

This document details the low-level system architecture for booting Apple's open-source **Darwin XNU kernel (v8796)** and unmodified **iOS 16 userland** on the **Infinix GT 20 Pro (X6871 / MT6895)**.

---

## 1. Boot Execution Pipeline

```
+-------------------------------------------------------------------------+
|                  MediaTek Little Kernel (LK) Bootloader                 |
|      - Initializes DRAM controller, clocks, PMIC, and Raydium DSI       |
|      - Loads AOSP Header v4 boot.img into RAM                           |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                      X6871 Boot Shim (shim/start.S)                     |
|      - Entry at physical base 0x40080000 in EL1 / EL2                   |
|      - Disables MediaTek TOPRGU Watchdog (0x10007000)                   |
|      - Initializes UART0 Serial Console (0x11002000)                    |
|      - Establishes TTBR0 translation tables for identity/MMIO mapping   |
|      - Populates Apple boot_args v2 structure                           |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                    Apple DeviceTree (DeviceTree.bin)                    |
|      - Passed in memory at physical address 0x66f00000                  |
|      - Spoofs iPhone X (D22AP / Apple,A11) target identity              |
|      - Exposes MT6895 GIC-600, UART0, UFS, and linear framebuffer      |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                        Darwin XNU Kernel (8796)                         |
|      - High-half virtual base 0xFFFFFFF007004000                        |
|      - GIC-600 interrupt routing & ARM Generic Timer                    |
|      - Unsealed HFS+ RootFS mount with AMFI code-signing bypass         |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                      Neutralized iOS 16 Userland                        |
|      - launchd (PID 1) executes with neutralized panic daemons          |
|      - .SkipSetup token bypasses Apple Setup Assistant                  |
|      - Framebuffer UI rendered via software rasterizer                  |
+-------------------------------------------------------------------------+
```

---

## 2. Memory Topology & Translation Tables

| Memory Region | Physical Address Range | Size | Mapping Attribute | Description |
| :--- | :--- | :--- | :--- | :--- |
| **SoC Peripherals** | `0x00000000 - 0x3FFFFFFF` | 1 GB | Device-nGnRE | MMIO (GIC, UART, UFS, DSI, GPU, PMIC) |
| **DRAM Base** | `0x40000000 - 0x4007FFFF` | 512 KB | Normal Cacheable | Reserved for Little Kernel and TrustZone |
| **Boot Shim** | `0x40080000 - 0x400FFFFF` | 512 KB | Normal Cacheable | Freestanding ARM64 boot shim |
| **XNU mach_kernel**| `0x40100000 - 0x44000000` | 63 MB | Normal Cacheable | Patched Darwin XNU Mach-O kernel binary |
| **Apple DeviceTree** | `0x66F00000 - 0x66F0FFFF` | 64 KB | Normal Cacheable | Binary DeviceTree passed via boot_args |
| **Framebuffer** | `0x70000000 - 0x70A00000` | 10 MB | Normal Non-Cache | Linear 1080x2436 @ 32bpp AMOLED scanout |
| **DRAM Space** | `0x40000000 - 0x23FFFFFFF`| 8 GB | Normal Cacheable | Total physical LPDDR5X RAM |

---

## 3. Apple Boot Arguments Protocol (`boot_args`)

The XNU kernel expects register `x0` to contain a pointer to `struct boot_args`:

```c
struct boot_args {
    uint16_t Revision;           /* 1 */
    uint16_t Version;            /* 2 */
    uint64_t virtBase;           /* 0xFFFFFFF007004000ULL */
    uint64_t physBase;           /* 0x40000000ULL (MT6895 DRAM base) */
    uint64_t memSize;            /* 0x200000000ULL (8GB) */
    uint64_t topOfKernelData;    /* End of kernel segments */
    struct Boot_Video video;     /* 1080x2436 @ 32bpp, stride 4320 */
    uint32_t machineType;        /* 'D22A' */
    uint64_t deviceTreeP;        /* 0x66F00000ULL */
    uint32_t deviceTreeLength;   /* Size of DeviceTree.bin */
    char CommandLine[1024];      /* "-v debug=0x14e keepsyms=1 amfi_get_out_of_my_way=1 cs_enforcement_disable=1" */
};
```
