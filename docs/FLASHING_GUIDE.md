# Infinix GT 20 Pro (X6871 / MT6895) Native iOS ROM Flashing & Deployment Guide

## 1. Hardware & System Target

| Parameter | Specification |
|---|---|
| **Device Model** | Infinix GT 20 Pro (x6871_h962) |
| **SoC** | MediaTek MT6895 (Dimensity 8200 Ultimate) |
| **CPU Architecture** | 1x Cortex-A78 @ 3.1GHz, 3x Cortex-A78 @ 3.0GHz, 4x Cortex-A55 @ 2.0GHz (ARMv8.2-A) |
| **Interrupt Controller** | ARM GIC-600 (GICv3) @ `0x0c000000` |
| **UART Serial Port** | MTK UART0 @ `0x11002000` (115200 8N1) |
| **Display / Framebuffer** | 1080x2436 AMOLED @ `0x7c000000` (Linear 32bpp BGRA) |
| **Storage Subsystem** | UFS 3.1 Host Controller (`0x11270000`) |
| **Darwin Kernel Target** | Apple XNU (ARM64) spoofing D22AP (iPhone X / iPhone10,6) |
| **Target iOS Userspace** | Genuine Apple iOS 16.7.16 (Build 20H392) |

---

## 2. Dynamic Partition & Stock ROM Analysis (Base vs Open `super.img`)

Stock ROM package: `X6871-16.3.0.155SP22(OP009PF001AZ)` contains two working `super.img` files:

1. **Base `super.img`**: `6,021,361,312 bytes` (~5.61 GB raw sparse)
2. **Open `super.img`**: `6,580,663,920 bytes` (~6.13 GB raw sparse)

### Partition Extent Comparison Table

| Partition Name | Base super (MB) | Open super (MB) | Delta (MB) | Content & Role |
|---|---|---|---|---|
| `system_a` | 923.01 | 923.01 | 0.00 | Core Android 16 AOSP base |
| `system_ext_a` | 1777.02 | 1777.02 | 0.00 | Transsion XOS 16 platform services |
| `vendor_a` | 951.07 | 951.07 | 0.00 | MT6895 proprietary HALs and firmware |
| `odm_a` | 919.89 | 919.89 | 0.00 | Infinix GT 20 Pro device overlays |
| `product_a` | 431.04 | 431.04 | 0.00 | Generic system applications |
| `vendor_dlkm_a` | 23.41 | 23.41 | 0.00 | Dynamic loadable kernel modules (MTK) |
| `system_dlkm_a` | 7.65 | 7.65 | 0.00 | GKI dynamic kernel modules |
| `odm_dlkm_a` | 4.01 | 4.01 | 0.00 | ODM dynamic kernel modules |
| **`tr_product_a`** | **725.95** | **3112.14** | **+2386.19** | **[REGION IMG] Transsion regional apps / carrier assets** |
| **`tr_region_a`** | **0.33 (stub)** | **3183.31** | **+3182.98** | **[REGION IMG] Regional customization & bloatware** |

Both super images are fully functional. The Open image contains the regional carrier payload (`OP009PF001AZ`).
For native Darwin XNU / iOS execution, Android userspace is replaced entirely:
- `xnu_boot.img` replaces the Android GKI kernel on `boot` (or boots directly into DRAM).
- Genuine Apple iOS userspace (`ios_rootfs.img`) mounts as the root filesystem.

---

## 3. Step-by-Step Deployment Guide

### Prerequisites
- PC running Windows 10/11, Linux, or macOS.
- Android Platform-Tools (`fastboot` and `adb`).
- USB-C data cable.
- Python 3.10+ (for RootFS builder).
- 7-Zip installed (recommended).

### Step 1: Bootloader Unlock
1. On your Infinix GT 20 Pro, go to **Settings > About Phone** and tap **Build Number** 7 times to enable Developer Options.
2. In **Settings > System > Developer Options**, enable:
   - **OEM Unlocking**
   - **USB Debugging**
3. Reboot device to Fastboot mode:
   ```cmd
   adb reboot bootloader
   ```
   *(Or power off device, then hold `[Volume Down] + [Power]` until `FASTBOOT` appears on screen).*
4. Execute unlock command:
   ```cmd
   fastboot flashing unlock
   ```
5. Confirm unlocking on device screen by pressing `Volume Up`.
   *(Note: Unlocking wipes Android user data).*

---

### Step 2: Safe Non-Destructive DRAM Boot (Zero Risk)
To test the Darwin XNU Mach-O kernel and Apple DeviceTree without writing to flash:

```cmd
fastboot boot xnu_boot.img
```

- **Mechanism:** The bootloader downloads `xnu_boot.img` directly into DRAM at address `0x40000000` and executes it.
- **Safety:** Storage remains 100% untouched. A simple device restart (`fastboot reboot` or holding Power for 10s) immediately reboots your device back into standard stock Android.
- **Diagnostics:** Connect UART adapter to MTK UART0 (`0x11002000`) at 115200 baud to view live XNU kernel boot logs (`-v debug=0x14e`).

---

### Step 3: Preparing the Genuine Apple iOS 16.7.16 RootFS

To generate the flashable `ios_rootfs.img`:

1. Run the automated cross-platform builder:
   ```cmd
   python userspace/build_ios_rootfs.py --download --output output/ios_rootfs.img
   ```
   *(Or if you already downloaded the IPSW, provide `--ipsw <path_to_ipsw>`)*.
2. The builder will automatically:
   - Stream the genuine iOS 16.7.16 (Build 20H392) IPSW directly from Apple's official CDN.
   - Extract the largest DMG root filesystem.
   - Execute `launchd_surgery.py` to neutralize hardware panics:
     - Removes `com.apple.watchdogd` (prevents SEP watchdog timeout panics).
     - Removes `com.apple.CommCenter` & `com.apple.basebandd` (prevents baseband bus panics).
     - Injects `.SkipSetup` activation bypass token into `/private/var/mobile/Library/Preferences/`.
   - Output ready-to-flash `ios_rootfs.img`.

---

### Step 4: 1-Click Flashing (Windows / Linux)

#### Windows
Double-click `flash_ios_rom.bat` and select:
- **Option [1]** for safe DRAM test boot.
- **Option [2]** to flash Darwin kernel persistently (`fastboot flash boot xnu_boot.img`).
- **Option [4]** to flash iOS rootfs (`fastboot flash userdata ios_rootfs.img`).
- **Option [5]** for full automated 1-click install.

#### Linux / macOS
Run in terminal:
```bash
chmod +x tools/packaging/flash_ios_rom.sh
./tools/packaging/flash_ios_rom.sh
```

---

## 4. Troubleshooting & Rollback

- **Device stuck on FASTBOOT screen:**
  Run `fastboot reboot` to restart into Android.
- **Fastboot command fails with `unknown command` or `locked`:**
  Run `fastboot flashing unlock` and accept the prompt on device.
- **Restore Stock Firmware:**
  To return to factory stock XOS 16 at any time, open SP Flash Tool or Fastboot Firmware Flasher and flash the stock images from `C:\Users\Admin\Music\Mehrnn\Roms\X6871-16.3.0.155SP22(OP009PF001AZ)\`.
