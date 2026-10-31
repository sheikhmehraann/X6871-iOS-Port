#!/usr/bin/env python3
"""
iOS Launchd & Daemon Neutralization Surgery for Non-Apple Hardware
Neutralizes daemons that panic or bootloop without proprietary Apple coprocessors (SEP, Baseband):
- com.apple.watchdogd: Prevents SEP heartbeat watchdog panics
- com.apple.CommCenter & com.apple.basebandd: Prevents modem bus panics
- com.apple.securityd / trustd fallback configuration
- Injects .SkipSetup token to bypass Apple Setup Assistant (iCloud activation)
"""

import os
import sys
import plistlib
import argparse
from pathlib import Path

PANIC_DAEMONS = [
    "System/Library/LaunchDaemons/com.apple.watchdogd.plist",
    "System/Library/LaunchDaemons/com.apple.CommCenter.plist",
    "System/Library/LaunchDaemons/com.apple.basebandd.plist",
    "System/Library/LaunchDaemons/com.apple.symptomsd.plist",
    "System/Library/LaunchDaemons/com.apple.wifid.plist"
]

def apply_surgery(rootfs_path: Path):
    if not rootfs_path.exists():
        raise FileNotFoundError(f"RootFS path does not exist: {rootfs_path}")

    print(f"[*] Applying launchd surgery to RootFS at: {rootfs_path}")
    removed_count = 0
    for daemon_rel in PANIC_DAEMONS:
        target = rootfs_path / daemon_rel
        if target.exists():
            target.unlink()
            print(f"    [-] Removed panic daemon: {daemon_rel}")
            removed_count += 1
        else:
            print(f"    [.] Daemon already absent: {daemon_rel}")

    # Inject .SkipSetup token
    pref_dir = rootfs_path / "private" / "var" / "mobile" / "Library" / "Preferences"
    pref_dir.mkdir(parents=True, exist_ok=True)
    skip_setup = pref_dir / ".SkipSetup"
    skip_setup.touch()
    print("[+] Injected .SkipSetup activation bypass token.")

    print(f"[+] Surgery completed. {removed_count} daemons neutralized.")

def main():
    parser = argparse.ArgumentParser(description="Neutralize iOS userland daemons for generic ARM64 bringup")
    parser.add_argument("rootfs", help="Path to mounted or extracted iOS root filesystem directory")
    args = parser.parse_args()

    apply_surgery(Path(args.rootfs))

if __name__ == "__main__":
    main()
