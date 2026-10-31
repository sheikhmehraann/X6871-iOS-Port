#!/usr/bin/env python3
import unittest
import struct
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.packaging.package_boot import build_boot_img_v4, align

class TestBootPackager(unittest.TestCase):
    def test_align(self):
        self.assertEqual(align(4096), 4096)
        self.assertEqual(align(4097), 8192)

    def test_build_boot_img_v4(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_boot.img")
            k_bytes = b"\x00" * 4096
            rd_bytes = b"\x01" * 2048
            build_boot_img_v4(k_bytes, rd_bytes, out_path)

            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "rb") as f:
                magic = f.read(8)
                self.assertEqual(magic, b"ANDROID!")
                k_sz, rd_sz, os_ver, hdr_sz = struct.unpack("<4I", f.read(16))
                self.assertEqual(k_sz, 4096)
                self.assertEqual(rd_sz, 2048)
                self.assertEqual(hdr_sz, 4096)
                f.seek(40)
                hdr_ver, = struct.unpack("<I", f.read(4))
                self.assertEqual(hdr_ver, 4)

if __name__ == "__main__":
    unittest.main()
