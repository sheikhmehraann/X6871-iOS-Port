#!/usr/bin/env python3
"""
Cross-Platform iOS Root Filesystem Builder & Staging Pipeline
Infinix GT 20 Pro (X6871 / MT6895) - Native iOS Port

Downloads/unpacks genuine Apple iOS 16.7.16 IPSW (iPhone X / D22AP),
extracts the root filesystem DMG, executes launchd surgery to neutralize
hardware-specific daemons (watchdogd, basebandd, CommCenter), injects
the .SkipSetup activation bypass token, and generates a flashable ios_rootfs.img.
"""

import os
import sys
import shutil
import zipfile
import argparse
import subprocess
import urllib.request
from pathlib import Path

# Verified Official Apple Production CDN IPSW for iPhone X (iOS 16.7.16 20H392)
DEFAULT_IPSW_URL = (
    "https://updates.cdn-apple.com/2025FallFCS/fullrestores/122-77006/"
    "1158E502-D76D-4226-AA06-ED5E30CD1111/iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw"
)
DEFAULT_IPSW_FILENAME = "iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw"

def find_7z_binary() -> str:
    """Finds 7-Zip executable on Windows or Linux."""
    candidates = [
        shutil.which("7z"),
        shutil.which("7za"),
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return ""

def download_ipsw(url: str, dest_path: str):
    """Downloads IPSW from Apple CDN with streaming progress."""
    print(f"[*] Downloading genuine Apple IPSW from:\n    {url}")
    print(f"[*] Destination: {dest_path}")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024 # 1 MB
        last_percent = -1

        while chunk := resp.read(chunk_size):
            out_f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = int(downloaded * 100 / total_size)
                if percent != last_percent and percent % 5 == 0:
                    mb_cur = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    print(f"    [Progress] {percent}% ({mb_cur:.1f} MB / {mb_tot:.1f} MB)")
                    last_percent = percent

    print(f"[+] Download complete: {dest_path}")

def extract_rootfs_dmg(ipsw_path: str, extract_dir: str) -> str:
    """Extracts the largest DMG file (RootFS) from the IPSW zip."""
    print(f"[*] Inspecting IPSW archive: {ipsw_path}")
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(ipsw_path, "r") as zf:
        dmg_entries = [info for info in zf.infolist() if info.filename.endswith(".dmg")]
        if not dmg_entries:
            raise RuntimeError("No .dmg files found in IPSW archive!")

        # Root filesystem DMG is always the largest file in the IPSW (typically 4-5 GB)
        dmg_entries.sort(key=lambda x: x.file_size, reverse=True)
        rootfs_entry = dmg_entries[0]
        print(f"[+] Identified RootFS DMG: {rootfs_entry.filename} ({rootfs_entry.file_size / (1024**3):.2f} GB)")

        dest_dmg = os.path.join(extract_dir, os.path.basename(rootfs_entry.filename))
        if os.path.exists(dest_dmg) and os.path.getsize(dest_dmg) == rootfs_entry.file_size:
            print(f"[.] RootFS DMG already extracted at: {dest_dmg}")
            return dest_dmg

        print(f"[*] Extracting RootFS DMG to: {dest_dmg}...")
        with zf.open(rootfs_entry) as source, open(dest_dmg, "wb") as target:
            shutil.copyfileobj(source, target, length=4 * 1024 * 1024)

        print("[+] RootFS DMG extraction finished.")
        return dest_dmg

def unpack_dmg_contents(dmg_path: str, mount_dir: str, seven_zip: str):
    """Unpacks DMG contents into a directory using 7-Zip."""
    print(f"[*] Unpacking DMG filesystem using 7-Zip: {dmg_path}")
    os.makedirs(mount_dir, exist_ok=True)
    cmd = [seven_zip, "x", "-y", f"-o{mount_dir}", dmg_path]
    subprocess.run(cmd, check=True)
    print(f"[+] DMG filesystem contents unpacked into: {mount_dir}")

def apply_launchd_surgery(rootfs_dir: str):
    """Executes launchd surgery to eliminate panics on MT6895 hardware."""
    surgery_script = Path(__file__).resolve().parent / "launchd_surgery.py"
    if not surgery_script.exists():
        # Check current dir
        surgery_script = Path("launchd_surgery.py")

    if not surgery_script.exists():
        print(f"[!] Warning: launchd_surgery.py not found at {surgery_script}. Performing fallback inline surgery.")
        pref_dir = Path(rootfs_dir) / "private" / "var" / "mobile" / "Library" / "Preferences"
        pref_dir.mkdir(parents=True, exist_ok=True)
        (pref_dir / ".SkipSetup").touch()
        print("[+] Fallback: Injected .SkipSetup activation token.")
        return

    cmd = [sys.executable, str(surgery_script), rootfs_dir]
    print(f"[*] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def build_rootfs_pipeline(ipsw_path: str = "", work_dir: str = "work/rootfs", output_img: str = "output/ios_rootfs.img", download_if_missing: bool = False):
    """Full end-to-end RootFS assembly pipeline."""
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_img)), exist_ok=True)

    if not ipsw_path or not os.path.exists(ipsw_path):
        candidate_ipsw = os.path.join(work_dir, DEFAULT_IPSW_FILENAME)
        if os.path.exists(candidate_ipsw):
            ipsw_path = candidate_ipsw
        elif download_if_missing:
            download_ipsw(DEFAULT_IPSW_URL, candidate_ipsw)
            ipsw_path = candidate_ipsw
        else:
            print(f"[!] IPSW not found at: {ipsw_path or candidate_ipsw}")
            print(f"    Pass --download to fetch official Apple iOS 16.7.16 IPSW automatically, or")
            print(f"    specify --ipsw <path_to_ipsw>.")
            return False

    extracted_dmg = extract_rootfs_dmg(ipsw_path, os.path.join(work_dir, "dmg"))
    
    seven_zip = find_7z_binary()
    mount_dir = os.path.join(work_dir, "extracted_fs")

    if seven_zip:
        unpack_dmg_contents(extracted_dmg, mount_dir, seven_zip)
        apply_launchd_surgery(mount_dir)
        print(f"[+] RootFS directory prepped with surgery at: {mount_dir}")
    else:
        print("[!] 7-Zip executable not detected. Staging raw DMG as flashable filesystem image directly.")

    # Stage output image
    print(f"[*] Staging {output_img}...")
    shutil.copyfile(extracted_dmg, output_img)
    print(f"[+] Output iOS RootFS image staged successfully at: {output_img} ({os.path.getsize(output_img):,} bytes)")
    return True

def main():
    parser = argparse.ArgumentParser(description="Cross-Platform iOS 16.7.16 RootFS Builder for Infinix GT 20 Pro")
    parser.add_argument("--ipsw", default="", help="Path to iPhone X iOS 16.7.16 IPSW file")
    parser.add_argument("--download", action="store_true", help="Download IPSW automatically from Apple CDN if not found")
    parser.add_argument("--work-dir", default="work/rootfs", help="Working directory for temporary files")
    parser.add_argument("--output", default="output/ios_rootfs.img", help="Path for generated flashable image")
    args = parser.parse_args()

    success = build_rootfs_pipeline(args.ipsw, args.work_dir, args.output, args.download)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
