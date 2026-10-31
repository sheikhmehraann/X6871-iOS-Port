import os
import io
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from tools.packaging.upload_gofile import calculate_sha256, get_best_server, upload_file

class TestGoFileUpload(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_calculate_sha256(self):
        test_file = os.path.join(self.temp_dir.name, "test_file.bin")
        data = b"HELLO_DARWIN_XNU_PORT_MT6895"
        with open(test_file, "wb") as f:
            f.write(data)

        expected_hash = "b23a533da421962f340d4dacf86dd379d026b3118555e8ba1411f86463ecab9e"
        self.assertEqual(calculate_sha256(test_file), expected_hash)

    @patch("urllib.request.urlopen")
    def test_get_best_server(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "ok",
            "data": {
                "servers": [{"name": "store3"}]
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        server = get_best_server()
        self.assertEqual(server, "store3")

    @patch("urllib.request.urlopen")
    def test_upload_file_success(self, mock_urlopen):
        test_file = os.path.join(self.temp_dir.name, "sample_package.tar.gz")
        with open(test_file, "wb") as f:
            f.write(b"SAMPLE_RELEASE_PACKAGE_CONTENT")

        # Mock servers call then upload call
        resp_servers = MagicMock()
        resp_servers.read.return_value = json.dumps({
            "status": "ok",
            "data": {"servers": [{"name": "store3"}]}
        }).encode("utf-8")

        resp_upload = MagicMock()
        resp_upload.read.return_value = json.dumps({
            "status": "ok",
            "data": {
                "downloadPage": "https://gofile.io/d/TEST1234",
                "directLink": "https://store3.gofile.io/download/direct/test",
                "fileId": "file-1234-abcd"
            }
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [resp_servers, resp_upload]

        result = upload_file(test_file, token="mock_token")
        self.assertEqual(result["download_page"], "https://gofile.io/d/TEST1234")
        self.assertEqual(result["file_id"], "file-1234-abcd")
        self.assertEqual(result["filename"], "sample_package.tar.gz")

if __name__ == "__main__":
    unittest.main()
