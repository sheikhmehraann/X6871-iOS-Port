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

            # Check xnu_boot.img magic and real boot shim code
            boot_data = None
            for n in zf.namelist():
                if os.path.basename(n) == "xnu_boot.img":
                    boot_data = zf.read(n)
                    break
            self.assertIsNotNone(boot_data)
            self.assertTrue(boot_data.startswith(b"ANDROID!"), "xnu_boot.img missing ANDROID! magic")
            # Ensure kernel section contains real ARM64 instructions, not just stub
            kernel_magic = boot_data[4096:4100]
            self.assertEqual(kernel_magic, b"\xdf\x4f\x03\xd5", "xnu_boot.img must contain compiled boot shim entry code")

    def test_mock_build_rootfs_pipeline(self):
        """Tests build_rootfs_pipeline end-to-end with mock IPSW."""
        ipsw_path = os.path.join(self.temp_dir.name, "test_restore.ipsw")
        work_dir = os.path.join(self.temp_dir.name, "work")
        out_img = os.path.join(self.temp_dir.name, "output_rootfs.img")

        with zipfile.ZipFile(ipsw_path, "w") as zf:
            zf.writestr("mock_rootfs.dmg", b"DMG_RAW_DATA" * 500)

        success = build_ios_rootfs.build_rootfs_pipeline(
            ipsw_path=ipsw_path,
            work_dir=work_dir,
            output_img=out_img,
            download_if_missing=False
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_img))
        self.assertEqual(os.path.getsize(out_img), 500 * len(b"DMG_RAW_DATA"))

    def test_package_rom_assembly(self):
        """Validates that package_rom.assemble_rom_package creates valid archive."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "packaging"))
        import package_rom
        temp_out = os.path.join(self.temp_dir.name, "rom_out")
        res = package_rom.assemble_rom_package(output_dir=temp_out, upload_gofile=False)

        self.assertTrue(os.path.exists(res["zip_path"]))
        self.assertTrue(os.path.exists(res["sha_manifest"]))
        self.assertEqual(len(res["sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
