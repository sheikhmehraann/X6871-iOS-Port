import os
import struct
import tempfile
import unittest
from tools.extract.firmware_extractor import (
    parse_scatter_txt,
    unpack_boot_v4,
    unpack_dtbo,
    inspect_vbmeta,
    inspect_lk
)

class TestFirmwareExtractor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_scatter_txt(self):
        scatter_path = os.path.join(self.temp_dir.name, "scatter.txt")
        content = (
            "partition_name: boot\n"
            "file_name: boot.img\n"
            "is_download: true\n\n"
            "partition_name: super\n"
            "file_name: super.img\n"
            "is_download: true\n"
        )
        with open(scatter_path, "w", encoding="utf-8") as f:
            f.write(content)

        parts = parse_scatter_txt(scatter_path)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0]["partition_name"], "boot")
        self.assertEqual(parts[1]["partition_name"], "super")

    def test_unpack_boot_v4(self):
        boot_path = os.path.join(self.temp_dir.name, "boot.img")
        out_dir = os.path.join(self.temp_dir.name, "out_boot")
        kernel_dummy = b"KERNEL_DATA_TEST" * 16

        # AOSP Header v4: magic(8), kernel_sz(4), ramdisk_sz(4), os_ver(4), hdr_sz(4), reserved[4](16), hdr_ver(4), cmdline(1536)
        hdr = struct.pack(
            "<8sIIII16sI1536s",
            b"ANDROID!",
            len(kernel_dummy),
            0, # ramdisk size
            0, # os version
            4096, # header size
            b"\x00" * 16, # reserved
            4, # header version 4
            b"test_cmdline\x00"
        )
        hdr_padded = hdr.ljust(4096, b"\x00")
        kernel_padded = kernel_dummy.ljust(4096, b"\x00")

        with open(boot_path, "wb") as f:
            f.write(hdr_padded + kernel_padded)

        info = unpack_boot_v4(boot_path, out_dir)
        self.assertEqual(info["header_version"], 4)
        self.assertEqual(info["kernel_size"], len(kernel_dummy))
        self.assertTrue(os.path.exists(info["kernel_output"]))

    def test_unpack_dtbo(self):
        dtbo_path = os.path.join(self.temp_dir.name, "dtbo.img")
        out_dir = os.path.join(self.temp_dir.name, "out_dtbo")
        payload = b"DUMMY_DTB_ENTRY"

        # Android libufdt header: 0xD7B7AB1E
        # magic, total_sz, hdr_sz, entry_sz, count, off, pg_sz, ver
        hdr = struct.pack(">8I", 0xD7B7AB1E, 64 + len(payload), 32, 32, 1, 32, 4096, 0)
        # Entry 0: dt_size, dt_offset, dt_id, dt_rev, dt_custom
        entry = struct.pack(">5I12s", len(payload), 64, 0x1234, 1, 0, b"\x00"*12)

        with open(dtbo_path, "wb") as f:
            f.write(hdr + entry + payload)

        info = unpack_dtbo(dtbo_path, out_dir)
        self.assertEqual(info["entry_count"], 1)
        self.assertEqual(len(info["entries"]), 1)
        self.assertEqual(info["entries"][0]["id"], "0x1234")

    def test_inspect_vbmeta(self):
        vbmeta_path = os.path.join(self.temp_dir.name, "vbmeta.img")
        # AVB0 header: magic, major, minor, auth_size, aux_size, ... release_str at 128
        hdr = bytearray(256)
        hdr[0:4] = b"AVB0"
        hdr[4:8] = struct.pack(">I", 1) # major
        hdr[8:12] = struct.pack(">I", 0) # minor
        hdr[128:128+12] = b"avbtool 1.3\x00"

        with open(vbmeta_path, "wb") as f:
            f.write(hdr)

        info = inspect_vbmeta(vbmeta_path)
        self.assertTrue(info["valid"])
        self.assertEqual(info["magic"], "AVB0")
        self.assertEqual(info["avb_version"], "1.0")

    def test_inspect_lk(self):
        lk_path = os.path.join(self.temp_dir.name, "lk.img")
        # MTK image header: magic=0x58881688, dsize=12345, name="lk\x00"
        hdr = struct.pack("<II32s", 0x58881688, 12345, b"lk\x00")
        with open(lk_path, "wb") as f:
            f.write(hdr + b"\x00" * 100)

        info = inspect_lk(lk_path)
        self.assertTrue(info["valid"])
        self.assertEqual(info["name"], "lk")
        self.assertEqual(info["dsize"], 12345)

if __name__ == "__main__":
    unittest.main()
