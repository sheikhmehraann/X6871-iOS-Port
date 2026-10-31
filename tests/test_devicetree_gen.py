#!/usr/bin/env python3
import unittest
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.firmware.build_devicetree import generate_mt6895_devicetree, align4

class TestDeviceTreeGenerator(unittest.TestCase):
    def test_align4(self):
        self.assertEqual(align4(0), 0)
        self.assertEqual(align4(1), 4)
        self.assertEqual(align4(4), 4)
        self.assertEqual(align4(7), 8)

    def test_generate_mt6895_devicetree(self):
        dtb = generate_mt6895_devicetree()
        self.assertGreater(len(dtb), 1000)
        # Check presence of D22AP and MT6895 strings
        self.assertIn(b"D22AP", dtb)
        self.assertIn(b"iPhone10,3", dtb)
        self.assertIn(b"cs_enforcement_disable=1", dtb)
        self.assertIn(b"interrupt-controller", dtb)
        self.assertIn(b"framebuffer", dtb)
        self.assertIn(b"mali-gpu", dtb)

if __name__ == "__main__":
    unittest.main()
