#!/usr/bin/env python3
"""
GoFile Automated Distribution Uploader
Discovers active GoFile ingestion nodes and uploads distributable artifacts.
Generates SHA-256 checksums and public download links.
"""

import os
import sys
import json
import time
import hashlib
import argparse
import urllib.request
import urllib.error

def calculate_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def get_best_server() -> str:
    url = "https://api.gofile.io/servers"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "ok":
                servers = data.get("data", {}).get("servers", [])
                if servers:
                    return servers[0]["name"]
    except Exception as e:
        print(f"[!] Warning: Failed to query GoFile servers API ({e}). Falling back to 'store1'.")
    return "store1"

def upload_file(filepath: str, token: str = "") -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Target file does not exist: {filepath}")

    filesize = os.path.getsize(filepath)
    sha256 = calculate_sha256(filepath)
    filename = os.path.basename(filepath)
    server = get_best_server()

    upload_url = f"https://{server}.gofile.io/contents/uploadfile"
    print(f"[*] Uploading '{filename}' ({filesize:,} bytes) to GoFile node '{server}'...")
    print(f"    SHA-256: {sha256}")

    boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
    body = bytearray()

    # Add token field if available
    if token:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="token"\r\n\r\n')
        body.extend(f"{token}\r\n".encode("utf-8"))

    # Add file field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")

    with open(filepath, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }

    req = urllib.request.Request(upload_url, data=bytes(body), headers=headers)
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("status") == "ok":
                    data = res.get("data", {})
                    download_page = data.get("downloadPage", "")
                    direct_link = data.get("directLink", "")
                    file_id = data.get("fileId", "")
                    print(f"[+] Upload complete! Download URL: {download_page}")
                    return {
                        "filename": filename,
                        "filesize": filesize,
                        "sha256": sha256,
                        "download_page": download_page,
                        "direct_link": direct_link,
                        "file_id": file_id
                    }
                else:
                    print(f"[!] Upload returned error: {res}")
        except Exception as e:
            print(f"[!] Attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(3)

    raise RuntimeError("Failed to upload file to GoFile after 3 attempts.")

def main():
    parser = argparse.ArgumentParser(description="Upload release artifacts to GoFile")
    parser.add_argument("file", help="Path to artifact file to upload")
    parser.add_argument("--token", default=os.getenv("GOFILE_TOKEN", ""), help="Optional GoFile account API token")
    parser.add_argument("--manifest-out", default="", help="Optional path to write release manifest JSON")
    args = parser.parse_args()

    res = upload_file(args.file, args.token)
    if args.manifest_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.manifest_out)), exist_ok=True)
        with open(args.manifest_out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"[+] Manifest saved to {args.manifest_out}")

if __name__ == "__main__":
    main()
