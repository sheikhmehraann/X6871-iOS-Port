#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import io
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.download.frbox_downloader import get_share_token, list_share_files, get_download_url

class TestFRBoxDownloader(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_get_share_token_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"share_token": "mock_token_123"}).encode()
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        token = get_share_token("test_share", "test_pwd")
        self.assertEqual(token, "mock_token_123")

    @patch("urllib.request.urlopen")
    def test_list_share_files_success(self, mock_urlopen):
        mock_resp = MagicMock()
        items = [{"name": "test.zip", "size": 1000, "file_id": "fid_123"}]
        mock_resp.read.return_value = json.dumps({"items": items}).encode()
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = list_share_files("test_share", "token_123")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "test.zip")

    @patch("urllib.request.urlopen")
    def test_get_download_url_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "url": "https://cdn.example.com/file.zip",
            "size": 10808879710,
            "crc64_hash": "12345"
        }).encode()
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        url, size, crc64 = get_download_url("test_share", "token_123", "fid_123")
        self.assertEqual(url, "https://cdn.example.com/file.zip")
        self.assertEqual(size, 10808879710)
        self.assertEqual(crc64, "12345")

if __name__ == "__main__":
    unittest.main()
