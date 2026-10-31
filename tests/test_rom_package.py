#!/usr/bin/env python3
"""
Unit tests for Infinix GT 20 Pro iOS ROM Package and RootFS Builder
"""

import os
import sys
import zipfile
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "userspace"))
import build_ios_rootfs

class TestRomPackage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_mock_ipsw_dmg_extraction(self):
        """Validates that build_ios_rootfs identifies and extracts the largest DMG."""
        ipsw_path = os.path.join(self.temp_dir.name, "test_restore.ipsw")
        extract_dir = os.path.join(self.temp_dir.name, "extracted")

        with zipfile.ZipFile(ipsw_path, "w") as zf:
            zf.writestr("small.dmg", b"SMALL_DMG" * 10)
            zf.writestr("large_rootfs.dmg", b"ROOTFS_DMG_CONTENT" * 1000)
            zf.writestr("BuildManifest.plist", b"<plist></plist>")

        extracted_dmg = build_ios_rootfs.extract_rootfs_dmg(ipsw_path, extract_dir)
        self.assertTrue(os.path.exists(extracted_dmg))
        self.assertTrue(extracted_dmg.endswith("large_rootfs.dmg"))
        self.assertEqual(os.path.getsize(extracted_dmg), 1000 * len(b"ROOTFS_DMG_CONTENT"))

    def test_rom_package_zip_structure(self):
        """Verifies that X6871_iOS_ROM_Package.zip contains all necessary deployment files."""
        zip_path = REPO_ROOT / "output" / "X6871_iOS_ROM_Package.zip"
        if not zip_path.exists():
            self.skipTest("ROM Package zip not yet built in output/")

        expected_files = [
            "xnu_boot.img",
            "DeviceTree.bin",
            "flash_ios_rom.bat",
            "flash_ios_rom.sh",
            "build_ios_rootfs.py",
            "launchd_surgery.py",
            "README_FLASHING.md",
            "super_comparison.json"
        ]

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = [os.path.basename(n) for n in zf.namelist()]
            for exp in expected_files:
                self.assertIn(exp, names, f"Missing {exp} in ROM Package zip")

            # Check xnu_boot.img magic
            boot_data = None
            for n in zf.namelist():
                if os.path.basename(n) == "xnu_boot.img":
                    boot_data = zf.read(n)
                    break
            self.assertIsNotNone(boot_data)
            self.assertTrue(boot_data.startswith(b"ANDROID!"), "xnu_boot.img missing ANDROID! magic")

if __name__ == "__main__":
    unittest.main()
