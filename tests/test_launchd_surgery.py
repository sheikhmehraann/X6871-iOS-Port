#!/usr/bin/env python3
import unittest
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from userspace.launchd_surgery import apply_surgery

class TestLaunchdSurgery(unittest.TestCase):
    def test_apply_surgery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            daemons_dir = root / "System" / "Library" / "LaunchDaemons"
            daemons_dir.mkdir(parents=True)

            wd = daemons_dir / "com.apple.watchdogd.plist"
            wd.write_text("<plist></plist>")
            cc = daemons_dir / "com.apple.CommCenter.plist"
            cc.write_text("<plist></plist>")

            apply_surgery(root)

            # Assert daemons removed
            self.assertFalse(wd.exists())
            self.assertFalse(cc.exists())

            # Assert .SkipSetup created
            skip_token = root / "private" / "var" / "mobile" / "Library" / "Preferences" / ".SkipSetup"
            self.assertTrue(skip_token.exists())

if __name__ == "__main__":
    unittest.main()
