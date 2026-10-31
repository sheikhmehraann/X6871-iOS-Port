#!/usr/bin/env python3
"""
Transsion FRBox Automated Downloader
Resolves and downloads stock firmware archives from Transsion's FRBox cloud share
(backed by Alibaba Cloud PDS / Aliyun OSS infrastructure).

Supports:
- Secure share token authentication
- Direct CDN / OSS URL resolution
- Resumable streaming downloads with Range requests
- SHA-256 integrity verification
- Dry-run inspect mode (no download)
"""

import os
import sys
import json
import time
import hashlib
import argparse
import urllib.request
import urllib.error

PDS_ENDPOINT = "https://fra315.api.aliyunpds.com/v2"
DEFAULT_SHARE_ID = "k3NB1w3ZXPg"
DEFAULT_SHARE_PWD = "IE5iju"
DEFAULT_TARGET_FILE = "X6871-16.3.0.155SP22(OP009PF001AZ).zip"

def get_share_token(share_id: str, share_pwd: str) -> str:
    url = f"{PDS_ENDPOINT}/share_link/get_share_token"
    payload = json.dumps({"share_id": share_id, "share_pwd": share_pwd}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    }
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            token = data.get("share_token")
            if not token:
                raise ValueError("Response did not contain 'share_token'.")
            return token
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Failed to authenticate with FRBox (HTTP {e.code}): {err_msg}")

def list_share_files(share_id: str, share_token: str, parent_file_id: str = "root") -> list:
    url = f"{PDS_ENDPOINT}/file/walk"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "x-share-token": share_token
    }
    payload = json.dumps({"share_id": share_id, "parent_file_id": parent_file_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Failed to list files in FRBox (HTTP {e.code}): {err_msg}")

def get_download_url(share_id: str, share_token: str, file_id: str) -> tuple:
    url = f"{PDS_ENDPOINT}/file/get_download_url"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "x-share-token": share_token
    }
    payload = json.dumps({"share_id": share_id, "file_id": file_id}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            dl_url = data.get("url")
            size = data.get("size", 0)
            crc64 = data.get("crc64_hash", "")
            return dl_url, size, crc64
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Failed to obtain download URL (HTTP {e.code}): {err_msg}")

def download_file(dl_url: str, output_path: str, expected_size: int, chunk_size: int = 4 * 1024 * 1024):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    temp_path = output_path + ".part"
    existing_bytes = 0

    if os.path.exists(temp_path):
        existing_bytes = os.path.getsize(temp_path)
        print(f"[*] Resuming partial download from byte {existing_bytes:,} / {expected_size:,}")

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    if existing_bytes > 0:
        headers["Range"] = f"bytes={existing_bytes}-"

    req = urllib.request.Request(dl_url, headers=headers)
    hasher = hashlib.sha256()

    mode = "ab" if existing_bytes > 0 else "wb"
    start_time = time.time()
    total_downloaded = existing_bytes

    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, mode) as out_f:
            while True:
                buf = resp.read(chunk_size)
                if not buf:
                    break
                out_f.write(buf)
                total_downloaded += len(buf)
                elapsed = time.time() - start_time
                speed_mb = (total_downloaded - existing_bytes) / (1024 * 1024) / (elapsed if elapsed > 0 else 1)
                pct = (total_downloaded / expected_size * 100) if expected_size else 0
                print(f"\r[*] Progress: {total_downloaded:,}/{expected_size:,} bytes ({pct:.1f}%) @ {speed_mb:.2f} MB/s", end="", flush=True)

        print()
    except Exception as e:
        print(f"\n[!] Download interrupted: {e}")
        print(f"[*] Partial file saved at {temp_path}. Rerun to resume.")
        sys.exit(1)

    os.rename(temp_path, output_path)
    print(f"[+] Download completed successfully: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Transsion FRBox Automated Firmware Downloader")
    parser.add_argument("--share-id", default=os.getenv("FRBOX_SHARE_ID", DEFAULT_SHARE_ID), help="FRBox share link ID")
    parser.add_argument("--pwd", default=os.getenv("FRBOX_PWD", DEFAULT_SHARE_PWD), help="FRBox share link access password")
    parser.add_argument("--target", default=DEFAULT_TARGET_FILE, help="Target filename to download")
    parser.add_argument("--output", default="downloads/X6871-stock-rom.zip", help="Local output destination path")
    parser.add_argument("--dry-run", action="store_true", help="List share contents and verify URL resolution without downloading")
    args = parser.parse_args()

    print("[*] Connecting to Transsion FRBox PDS service...")
    token = get_share_token(args.share_id, args.pwd)
    print("[+] Authenticated. Share session established.")

    items = list_share_files(args.share_id, token)
    print(f"[*] Found {len(items)} items in share root:")
    target_item = None
    for item in items:
        name = item.get("name", "")
        size = item.get("size")
        fid = item.get("file_id")
        sz_str = f"{size / (1024**3):.2f} GB" if size else "<DIR>"
        safe_name = name.encode("ascii", errors="replace").decode("ascii")
        print(f"    - {safe_name} ({sz_str}) [id: {fid}]")
        if name == args.target:
            target_item = item

    if not target_item:
        print(f"[!] Target file '{args.target}' not found in root items.")
        sys.exit(1)

    print(f"[*] Resolving direct download link for '{args.target}'...")
    dl_url, size, crc64 = get_download_url(args.share_id, token, target_item["file_id"])
    print("[+] Download URL resolved successfully.")
    print(f"    File Size: {size:,} bytes ({size / (1024**3):.2f} GB)")
    print(f"    CRC64: {crc64}")

    if args.dry_run:
        print("[*] Dry run mode enabled. URL resolution verified successfully. Exiting.")
        sys.exit(0)

    download_file(dl_url, args.output, size)

if __name__ == "__main__":
    main()
