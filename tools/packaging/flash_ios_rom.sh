#!/usr/bin/env bash
# ==============================================================================
# Infinix GT 20 Pro (X6871 / MT6895) - Native iOS ROM 1-Click Flasher
# Darwin XNU Kernel + iOS 16 Userspace Deployment (Linux / macOS)
# ==============================================================================
cd "$(dirname "$0")"

echo "==============================================================================="
echo "       INFINIX GT 20 PRO (X6871 / MT6895) - NATIVE iOS ROM 1-CLICK FLASHER"
echo "                 Darwin XNU Kernel + iOS 16 Userspace Deployment"
echo "==============================================================================="
echo ""

# 1. Locate fastboot binary
FASTBOOT_BIN=""
if command -v fastboot >/dev/null 2>&1; then
    FASTBOOT_BIN="fastboot"
elif [ -f "./platform-tools/fastboot" ]; then
    FASTBOOT_BIN="./platform-tools/fastboot"
else
    echo "[!] ERROR: fastboot executable not found in PATH!"
    echo "    Please install Android platform-tools (e.g., sudo apt install android-sdk-platform-tools)"
    exit 1
fi

echo "[*] Fastboot binary located: $FASTBOOT_BIN"
echo ""

# 2. Check connected Fastboot devices
echo "[*] Polling for connected device in Fastboot / Bootloader mode..."
FB_DEVICES=$($FASTBOOT_BIN devices 2>/dev/null || true)
if [ -z "$FB_DEVICES" ]; then
    echo "[!] WARNING: No device detected in Fastboot mode!"
    echo "    1. Power off your Infinix GT 20 Pro."
    echo "    2. Hold [Volume Down + Power] until FASTBOOT appears."
    echo "    3. Connect USB cable to PC."
    echo ""
    read -rp "Press Enter once connected to continue..."
fi

echo "[*] Querying device bootloader parameters..."
$FASTBOOT_BIN getvar product 2>&1 || true
$FASTBOOT_BIN getvar unlocked 2>&1 || true
echo ""

show_menu() {
    echo "==============================================================================="
    echo "                            ROM DEPLOYMENT MENU"
    echo "==============================================================================="
    echo " [1] Non-Destructive RAM Boot (SAFE - Boots xnu_boot.img in DRAM, leaves ROM intact)"
    echo " [2] Flash Darwin XNU Boot Partition (fastboot flash boot xnu_boot.img)"
    echo " [3] Build / Stage iOS RootFS Image (Runs build_ios_rootfs.py)"
    echo " [4] Flash iOS RootFS to Storage (fastboot flash userdata / dynamic partition)"
    echo " [5] 1-Click Complete Install (Flash XNU Boot + Flash iOS RootFS + Reboot)"
    echo " [6] Bootloader Unlock Helper (fastboot flashing unlock)"
    echo " [7] Query Device Hardware Diagnostics (fastboot getvar all)"
    echo " [8] Exit"
    echo "==============================================================================="
    read -rp "Select an option [1-8]: " CHOICE
}

find_boot_img() {
    for candidate in "xnu_boot.img" "output/xnu_boot.img" "../output/xnu_boot.img"; do
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

find_rootfs_img() {
    for candidate in "ios_rootfs.img" "output/ios_rootfs.img" "../output/ios_rootfs.img"; do
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

find_builder_script() {
    for candidate in "build_ios_rootfs.py" "userspace/build_ios_rootfs.py" "../userspace/build_ios_rootfs.py"; do
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

while true; do
    show_menu
    case "$CHOICE" in
        1)
            echo ""
            echo "[*] Selected: [1] Non-Destructive DRAM Boot"
            BOOT_IMG=$(find_boot_img || true)
            if [ -z "$BOOT_IMG" ]; then
                echo "[!] ERROR: xnu_boot.img not found!"
            else
                echo "[*] Streaming $BOOT_IMG to DRAM..."
                $FASTBOOT_BIN boot "$BOOT_IMG" || echo "[!] Fastboot boot failed."
            fi
            ;;
        2)
            echo ""
            echo "[*] Selected: [2] Flash Darwin XNU Boot Partition"
            BOOT_IMG=$(find_boot_img || true)
            if [ -z "$BOOT_IMG" ]; then
                echo "[!] ERROR: xnu_boot.img not found!"
            else
                read -rp "Are you sure you want to flash boot partition? (y/N): " CONFIRM
                if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                    $FASTBOOT_BIN flash boot "$BOOT_IMG" || echo "[!] Fastboot flash failed."
                fi
            fi
            ;;
        3)
            echo ""
            echo "[*] Selected: [3] Build / Stage iOS RootFS"
            BUILDER=$(find_builder_script || true)
            if [ -z "$BUILDER" ]; then
                echo "[!] ERROR: build_ios_rootfs.py not found!"
            elif ! command -v python3 >/dev/null 2>&1; then
                echo "[!] ERROR: python3 not found in PATH! Please install Python 3."
            else
                echo " [A] Provide existing IPSW file path"
                echo " [B] Automatically download iOS 16.7.16 IPSW from Apple CDN (~6.1 GB)"
                echo " [C] Back to Main Menu"
                read -rp "Select [A/B/C]: " RF_OPT
                if [[ "$RF_OPT" =~ ^[Aa]$ ]]; then
                    read -rp "Enter full path to iPhone X iOS 16.7.16 IPSW: " IPSW_FILE
                    python3 "$BUILDER" --ipsw "$IPSW_FILE" --output ios_rootfs.img || true
                elif [[ "$RF_OPT" =~ ^[Bb]$ ]]; then
                    python3 "$BUILDER" --download --output ios_rootfs.img || true
                fi
            fi
            ;;
        4)
            echo ""
            echo "[*] Selected: [4] Flash iOS RootFS"
            ROOTFS_IMG=$(find_rootfs_img || true)
            if [ -z "$ROOTFS_IMG" ]; then
                echo "[!] ERROR: ios_rootfs.img not found! Run option 3 first."
            else
                read -rp "Flash $ROOTFS_IMG to userdata? (y/N): " CONFIRM
                if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                    $FASTBOOT_BIN flash userdata "$ROOTFS_IMG"
                fi
            fi
            ;;
        5)
            echo ""
            echo "[*] Selected: [5] 1-Click Complete Install"
            BOOT_IMG=$(find_boot_img || true)
            ROOTFS_IMG=$(find_rootfs_img || true)
            if [ -z "$BOOT_IMG" ]; then
                echo "[!] ERROR: xnu_boot.img not found!"
            else
                $FASTBOOT_BIN flash boot "$BOOT_IMG"
                if [ -n "$ROOTFS_IMG" ]; then
                    $FASTBOOT_BIN flash userdata "$ROOTFS_IMG"
                fi
                read -rp "Reboot device now? (y/N): " CONFIRM
                if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                    $FASTBOOT_BIN reboot
                fi
            fi
            ;;
        6)
            echo ""
            echo "[*] Selected: [6] Bootloader Unlock Helper"
            read -rp "Run fastboot flashing unlock? (y/N): " CONFIRM
            if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                $FASTBOOT_BIN flashing unlock
            fi
            ;;
        7)
            echo ""
            echo "[*] Selected: [7] Query Device Hardware Diagnostics"
            $FASTBOOT_BIN getvar all || true
            ;;
        8)
            echo "Exiting. Goodbye!"
            exit 0
            ;;
        *)
            echo "[!] Invalid selection."
            ;;
    esac
    echo ""
done
