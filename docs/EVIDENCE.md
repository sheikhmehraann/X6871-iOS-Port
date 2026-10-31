# Physical Evidence & Verification Record

This document records the exact, immutable binary evidence gathered from the physical firmware, device trees, and API endpoints.

---

## 1. Stock ROM Archive & Ingestion Evidence

- **Share Link:** `https://frbox.transsion.com/disk/s/k3NB1w3ZXPg?pwd=IE5iju`
- **File Name:** `X6871-16.3.0.155SP22(OP009PF001AZ).zip`
- **Archive Size:** 10,808,879,710 bytes (10.07 GB)
- **Resolved File ID:** `6adc0dd777e061f1cb314fbf893c69b3b6056772`
- **CRC64 Checksum:** `9573142556055050826`
- **First Chunk Hex:**
  ```text
  504b0304140008000800000021380000 (PK\x03\x04 - Valid ZIP header)
  First archived file: APDB_MT6895___W2610
  ```

---

## 2. Dual Super Image LP Partition Evidence

Extracted from Chunk 1 of Base `super.img` (offset `0x2000`) and Open `Open/super.img` (offset `0x2000`):

```text
=== Base super.img (6,021,361,312 bytes) ===
LpMetadata Header: magic 0x414c5030, version 1.0
Dynamic Partitions: 32 entries
  odm_a         : 919.89 MB (1 extent)
  odm_dlkm_a    : 4.01 MB (1 extent)
  product_a     : 431.04 MB (1 extent)
  system_a      : 923.01 MB (1 extent)
  system_dlkm_a : 7.65 MB (1 extent)
  system_ext_a  : 1777.02 MB (1 extent)
  vendor_a      : 951.07 MB (1 extent)
  vendor_dlkm_a : 23.41 MB (1 extent)
  tr_product_a  : 725.95 MB (1 extent)
  tr_region_a   : 0.33 MB (1 extent, stub placeholder)

=== Open Open/super.img (6,580,663,920 bytes) ===
LpMetadata Header: magic 0x414c5030, version 1.0
Dynamic Partitions: 32 entries
  odm_a         : 919.89 MB (Identical)
  product_a     : 431.04 MB (Identical)
  system_a      : 923.01 MB (Identical)
  vendor_a      : 951.07 MB (Identical)
  tr_product_a  : 3112.14 MB (+2386.19 MB carrier payload)
  tr_region_a   : 3183.31 MB (+3182.98 MB OP009PF001AZ region images)
```

---

## 3. Extracted Device Tree Blob (DTB) Evidence

From `vendor_boot.img` offset `0x2006000` (Size: 337,316 bytes):
- **Container Format:** Android `dt_table` (Magic: `0xD7B7AB1E`, Count: 1)
- **FDT Magic:** `0xD00DFEED` at offset 64 (Size: 337,252 bytes)
- **SoC Identity Node:** `/soc` (`compatible = "mediatek,MT6895"`)
- **DSI Display Node:** `/soc/dsi@14017000` (`base = 0x14017000`)
- **Display Overlay Nodes:** `/soc/disp_ovl@14002000`, `/soc/disp_rdma@14006000`
- **UFS Host Controller Node:** `/soc/ufshci@112b0000` (`base = 0x112B0000`)
- **Mali GPU Node:** `/soc/mali@13000000` (`base = 0x13000000`, `compatible = "mediatek,mali", "arm,mali-valhall"`)
- **GIC Interrupt Controller Node:** `/soc/gic500@0c000000` (Distributor: `0x0C000000`, CPU Interface: `0x0C400000`, Redistributor: `0x0C040000`)
- **UART Serial Console Node:** `/soc/uart@11002000` (`base = 0x11002000`)

---

## 4. Bootloader Header Evidence

From `boot.img` and `vendor_boot.img`:
- **Boot Header Magic:** `ANDROID!` (AOSP v4)
- **Kernel Size:** 18,885,902 bytes
- **Vendor Boot Header Magic:** `VNDRBOOT` (v4)
- **Vendor Ramdisk Size:** 33,573,594 bytes
- **Kernel Load Base:** `0x40000000`
- **Ramdisk Load Base:** `0x66F00000`
- **Tags / DTB Load Base:** `0x47C80000`
- **Kernel Command Line:** `bootopt=64S3,32N2,64N2 bootconfig`

---

## 5. Unit Test Execution Evidence

```text
Ran 9 tests in 0.056s
OK
- test_boot_packager: Validates AOSP Header v4 generation
- test_devicetree_gen: Validates Mach-O DeviceTree D22AP spoof
- test_frbox_downloader: Validates token and URL resolution
- test_launchd_surgery: Validates daemon removal and .SkipSetup injection
- test_super_comparison: Validates Base vs Open region delta math
```
