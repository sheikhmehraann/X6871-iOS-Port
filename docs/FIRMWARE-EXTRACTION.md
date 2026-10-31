# Stock Firmware Extraction & Super Image Dissection

**Target Device:** Infinix GT 20 Pro (`X6871` / `x6871_h962`)  
**Stock Build:** `X6871-16.3.0.155SP22(OP009PF001AZ)`  
**Platform:** MediaTek MT6895 (Dimensity 8200 Ultimate)

---

## 1. Official FRBox Download Mechanism

The stock firmware is hosted on Transsion's FRBox cloud storage:
- **Share Link:** `https://frbox.transsion.com/disk/s/k3NB1w3ZXPg?pwd=IE5iju`
- **Archive Filename:** `X6871-16.3.0.155SP22(OP009PF001AZ).zip`
- **File Size:** 10,808,879,710 bytes (10.07 GB)
- **Backend Infrastructure:** Alibaba Cloud PDS (`https://fra315.api.aliyunpds.com/v2`)
- **Resolved File ID:** `6adc0dd777e061f1cb314fbf893c69b3b6056772`
- **CRC64 Checksum:** `9573142556055050826`

Automated ingestion is implemented in [frbox_downloader.py](file:///tools/download/frbox_downloader.py). It queries `/v2/share_link/get_share_token` with the share password, acquires an ephemeral session token, resolves the Aliyun OSS presigned redirect URL via `/v2/file/get_download_url`, and streams chunks using HTTP `Range` requests for resumable downloads.

---

## 2. The Dual Super Image Investigation

The unpacked factory firmware contains two distinct dynamic partition super images:
1. **Base Super Image:** `super.img` (6,021,361,312 bytes / 5.61 GB)
2. **Open Market Super Image:** `Open/super.img` (6,580,663,920 bytes / 6.13 GB)

Both files are Android sparse images (`magic: 0xED26FF3A`) containing an embedded `LpMetadata` table (`magic: 0x414C5030`, version 1.0).

### Exact Partition Size Comparison

Extracted by [region_analyzer.py](file:///tools/extract/region_analyzer.py):

| Partition | Base `super.img` (MB) | Open `Open/super.img` (MB) | Delta (MB) | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **`odm_a`** | 919.89 | 919.89 | 0.00 | Core Hardware HALs (Identical) |
| **`odm_dlkm_a`** | 4.01 | 4.01 | 0.00 | Touch & Camera Kernel Modules |
| **`product_a`** | 431.04 | 431.04 | 0.00 | Base Android Product Apps |
| **`system_a`** | 923.01 | 923.01 | 0.00 | Core System Frameworks |
| **`system_dlkm_a`** | 7.65 | 7.65 | 0.00 | GKI System Kernel Modules |
| **`system_ext_a`** | 1777.02 | 1777.02 | 0.00 | System Extension Frameworks |
| **`vendor_a`** | 951.07 | 951.07 | 0.00 | MediaTek Hardware Drivers |
| **`vendor_dlkm_a`** | 23.41 | 23.41 | 0.00 | Mali & MTK Core Kernel Drivers |
| **`tr_product_a`** | 725.95 | **3112.14** | **+2386.19** | **Carrier / Open Market Product Apps** |
| **`tr_region_a`** | 0.33 (stub) | **3183.31** | **+3182.98** | **Open Market Regional Customization** |

### Reverse Engineering Conclusion
- The core operating system partitions (`system`, `vendor`, `odm`, `product`, `dlkm`) are bit-for-bit identical between both super images.
- Base `super.img` contains a minimal carrier-agnostic payload.
- `Open/super.img` contains the full 3.18 GB regional customization (`tr_region_a`) and 3.11 GB carrier product image (`tr_product_a`) for the `OP009PF001AZ` open market channel.

---

## 3. Extracted Boot Components

| File | Format | Size | Extracted Artifacts |
| :--- | :--- | :--- | :--- |
| **`boot.img`** | AOSP v4 Boot | 67,108,864 bytes | ARM64 Linux Kernel Image (18,885,902 bytes, LZ4-compressed) |
| **`vendor_boot.img`** | AOSP v4 Vendor Boot | 67,108,864 bytes | Flattened Device Tree `dtb.img` (337,316 bytes) + Vendor Ramdisk (33,573,594 bytes) |
| **`dtbo.img`** | Android DTBO | 8,388,608 bytes | Device Tree Overlays |
| **`lk.img`** | MediaTek Bootloader | 3,182,736 bytes | Little Kernel Bootloader Binary |
| **`vbmeta.img`** | Android Verified Boot | 12,288 bytes | AVB Hash Trees and Public Keys |
