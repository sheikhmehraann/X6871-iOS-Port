#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.extract.region_analyzer import compare_supers

class TestSuperComparison(unittest.TestCase):
    def test_compare_supers(self):
        base_info = {
            "file_size": 6021361312,
            "partitions": {
                "system_a": {"size_mb": 923.01, "size_bytes": 967843840},
                "tr_region_a": {"size_mb": 0.33, "size_bytes": 346112},
                "tr_product_a": {"size_mb": 725.95, "size_bytes": 761217024}
            }
        }
        open_info = {
            "file_size": 6580663920,
            "partitions": {
                "system_a": {"size_mb": 923.01, "size_bytes": 967843840},
                "tr_region_a": {"size_mb": 3183.31, "size_bytes": 3337854976},
                "tr_product_a": {"size_mb": 3112.14, "size_bytes": 3263307776}
            }
        }
        report = compare_supers(base_info, open_info)
        self.assertEqual(report["partitions_comparison"]["system_a"]["diff_mb"], 0.0)
        self.assertFalse(report["partitions_comparison"]["system_a"]["has_region_payload"])
        self.assertTrue(report["partitions_comparison"]["tr_region_a"]["has_region_payload"])
        self.assertTrue(report["partitions_comparison"]["tr_product_a"]["has_region_payload"])
        self.assertAlmostEqual(report["partitions_comparison"]["tr_region_a"]["diff_mb"], 3182.98, places=1)

if __name__ == "__main__":
    unittest.main()
