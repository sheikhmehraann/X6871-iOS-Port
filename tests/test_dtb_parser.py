import unittest
import struct
from tools.firmware.dtb_parser import FDTParser, extract_hardware_topology, FDT_MAGIC

class TestDTBParser(unittest.TestCase):
    def _create_minimal_fdt(self):
        # Build minimal valid FDT binary
        # strings block
        strings = b"compatible\x00reg\x00#address-cells\x00#size-cells\x00"
        
        # struct block
        # FDT_BEGIN_NODE (root "")
        struct_data = bytearray()
        struct_data.extend(struct.pack(">I", 1)) # BEGIN_NODE
        struct_data.extend(b"\x00\x00\x00\x00")  # name "" aligned to 4
        
        # prop: compatible = "mediatek,mt6895"
        val = b"mediatek,mt6895\x00"
        val_padded = val.ljust((len(val) + 3) & ~3, b"\x00")
        struct_data.extend(struct.pack(">3I", 3, len(val), 0)) # FDT_PROP, len, nameoff (compatible)
        struct_data.extend(val_padded)

        # child node "mali@13000000"
        struct_data.extend(struct.pack(">I", 1)) # BEGIN_NODE
        name_mali = b"mali@13000000\x00"
        struct_data.extend(name_mali.ljust((len(name_mali) + 3) & ~3, b"\x00"))
        
        # prop in child: compatible = "arm,mali-valhall"
        mali_val = b"arm,mali-valhall\x00"
        mali_padded = mali_val.ljust((len(mali_val) + 3) & ~3, b"\x00")
        struct_data.extend(struct.pack(">3I", 3, len(mali_val), 0))
        struct_data.extend(mali_padded)
        
        # END_NODE for mali
        struct_data.extend(struct.pack(">I", 2))
        
        # END_NODE for root
        struct_data.extend(struct.pack(">I", 2))
        
        # FDT_END
        struct_data.extend(struct.pack(">I", 9))
        
        off_mem_rsvmap = 48
        off_struct = 64
        off_strings = off_struct + len(struct_data)
        total_size = off_strings + len(strings)
        
        header = struct.pack(
            ">7I",
            FDT_MAGIC,
            total_size,
            off_struct,
            off_strings,
            off_mem_rsvmap,
            17, # version
            16  # last comp version
        )
        header = header.ljust(off_struct, b"\x00")
        
        return bytes(header) + bytes(struct_data) + strings

    def test_fdt_parse_nodes_does_not_drop_root(self):
        fdt_bytes = self._create_minimal_fdt()
        parser = FDTParser(fdt_bytes)
        root = parser.parse_nodes()
        
        self.assertIsNotNone(root)
        self.assertIn("_name", root)
        self.assertIn("_children", root)
        self.assertIn("mali@13000000", root["_children"])
        mali_node = root["_children"]["mali@13000000"]
        self.assertIn("compatible", mali_node["_properties"])
        self.assertEqual(mali_node["_properties"]["compatible"], "arm,mali-valhall")

    def test_extract_hardware_topology_dynamic(self):
        fdt_bytes = self._create_minimal_fdt()
        parser = FDTParser(fdt_bytes)
        root = parser.parse_nodes()
        topo = extract_hardware_topology(root)
        
        self.assertTrue(topo["verified_from_dtb"])
        self.assertEqual(topo["gpu"]["dtb_path"], "/mali@13000000")
        self.assertEqual(topo["gpu"]["compatible"], "arm,mali-valhall")

if __name__ == "__main__":
    unittest.main()
