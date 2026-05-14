"""Tests for seal.signer — GPG signing wrapper."""

import os
import unittest
from unittest.mock import patch, MagicMock

from seal.signer import extract_signed_content


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestExtractSignedContent(unittest.TestCase):

    def test_extract_from_record_001_sig(self):
        path = os.path.join(FIXTURES, "party-a-signature.asc")
        content = extract_signed_content(path)
        # record-001 Record-Hash
        self.assertEqual(content, "77cb1db1d715d904f2780db76214410000796287f6caee6b1bb4942896369bc8")

    def test_extract_from_record_002_sig(self):
        path = os.path.join(FIXTURES, "party-a-signature-002.asc")
        content = extract_signed_content(path)
        # record-002 Record-Hash
        self.assertEqual(content, "83cd95f390b2e01507ba19cba6f1f89008e345b4d7a04f4d6dd5c048d7960ca3")


class TestSignHash(unittest.TestCase):

    @patch("seal.signer.subprocess.run")
    def test_sign_calls_gpg_clearsign(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        from seal.signer import sign_hash
        sign_hash("abc123", "/tmp/test.asc")
        mock_run.assert_called_once()
        args = mock_run.call_args
        cmd = args[0][0]
        self.assertIn("--clearsign", cmd)
        self.assertIn("/tmp/test.asc", cmd)

    @patch("seal.signer.subprocess.run")
    def test_sign_with_key_id(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        from seal.signer import sign_hash
        sign_hash("abc123", "/tmp/test.asc", key_id="DEADBEEF")
        cmd = mock_run.call_args[0][0]
        self.assertIn("--local-user", cmd)
        self.assertIn("DEADBEEF", cmd)


if __name__ == "__main__":
    unittest.main()
