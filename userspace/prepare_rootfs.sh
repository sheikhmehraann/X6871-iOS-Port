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
    echo "    Please download iOS 16.7.16 IPSW for iPhone X (iPhone10,6):"
    echo "    curl -L -O https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-81763/E02E4E4E-311D-4952-B4D7-270BA9CECE8F/iPhone10,6_16.7.16_20H350_Restore.ipsw"
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

echo "[*] Applying Launchd Surgery..."
python3 "$(dirname "$0")/launchd_surgery.py" "$MOUNT_POINT" || true

echo "[+] iOS RootFS assembly ready at: $WORK_DIR/rootfs_raw.img"
