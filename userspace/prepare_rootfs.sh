#!/usr/bin/env bash
# ==============================================================================
# iOS Root Filesystem Assembly Pipeline for Infinix GT 20 Pro (X6871)
# ==============================================================================
set -euo pipefail

IPSW_PATH="${1:-workspace_ipsw/iPhone10,6_16.7.16_20H350_Restore.ipsw}"
WORK_DIR="${2:-work/rootfs}"
OUTPUT_IMG="${3:-output/ios_rootfs.img}"

echo "[*] Initializing iOS RootFS Assembly Pipeline..."
mkdir -p "$WORK_DIR"
mkdir -p "$(dirname "$OUTPUT_IMG")"

if [ ! -f "$IPSW_PATH" ]; then
    echo "[!] Error: IPSW file not found at: $IPSW_PATH"
    echo "    Please download iOS 16.7.16 IPSW for iPhone X (iPhone10,6 / iPhone10,3):"
    echo "    curl -L -O https://updates.cdn-apple.com/2025FallFCS/fullrestores/122-77006/1158E502-D76D-4226-AA06-ED5E30CD1111/iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw"
    exit 1
fi

echo "[*] Unpacking IPSW archive..."
unzip -q -o "$IPSW_PATH" -d "$WORK_DIR/extracted"

echo "[*] Identifying RootFS DMG..."
ROOTFS_DMG=$(find "$WORK_DIR/extracted" -maxdepth 1 -name "*.dmg" -type f -exec ls -S {} + | head -n 1)
echo "[+] Selected largest DMG: $ROOTFS_DMG"

echo "[*] Converting DMG to raw image with dmg2img..."
if command -v dmg2img >/dev/null 2>&1; then
    dmg2img -s "$ROOTFS_DMG" -o "$WORK_DIR/rootfs_raw.img"
else
    echo "[!] dmg2img not found, copying raw DMG directly..."
    cp "$ROOTFS_DMG" "$WORK_DIR/rootfs_raw.img"
fi

MOUNT_POINT="$WORK_DIR/mnt"
mkdir -p "$MOUNT_POINT"

echo "[*] Extracting RootFS filesystem contents with 7z..."
if command -v 7z >/dev/null 2>&1; then
    7z x -y "$ROOTFS_DMG" -o"$MOUNT_POINT" >/dev/null 2>&1 || true
fi

echo "[*] Applying Launchd Surgery..."
python3 "$(dirname "$0")/launchd_surgery.py" "$MOUNT_POINT"

echo "[+] iOS RootFS assembly ready at: $WORK_DIR/rootfs_raw.img"
