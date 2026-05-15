"""Tests for seal.verifier — verification pipeline."""

import os
import unittest

from seal.verifier import verify, VALID_METHOD_LEVELS

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestMethodLevelValidation(unittest.TestCase):

    def test_all_valid_combinations(self):
        # v0.4.0: VALID_METHOD_LEVELS is now a dict of lists (multiple valid levels per method)
        self.assertIn("1-behavioral", VALID_METHOD_LEVELS["behavioral"])
        # gpg-signature can be Level 2 (session-signed), 3 (provider), or 4 (identity-bound)
        self.assertIn("4-identity-bound", VALID_METHOD_LEVELS["gpg-signature"])
        self.assertIn("2-session-signed", VALID_METHOD_LEVELS["gpg-signature"])
        # TEE can be Level 5 (new) or Level 4 (backwards compat)
        self.assertIn("5-environment-bound", VALID_METHOD_LEVELS["tee-attested"])
        # Backwards compatibility: old level numbers still accepted
        self.assertIn("3-identity-bound", VALID_METHOD_LEVELS["gpg-signature"])
        self.assertIn("4-environment-bound", VALID_METHOD_LEVELS["tee-attested"])


class TestVerifyRecord002(unittest.TestCase):

    def test_verify_with_preimage(self):
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        preimage_path = os.path.join(FIXTURES, "record-002-preimage.txt")
        report = verify(record_path, preimage_path=preimage_path)

        # Record should parse
        check_names = {c.name: c for c in report.checks}
        self.assertEqual(check_names["record-parse"].status, "pass")

        # Record-Hash should match preimage
        self.assertEqual(check_names["record-hash"].status, "pass")

        # Method/Level should be consistent
        self.assertEqual(check_names["Party-A-method-level"].status, "pass")
        self.assertEqual(check_names["Party-B-method-level"].status, "pass")

        # Timestamp should be valid UTC
        self.assertEqual(check_names["timestamp-utc"].status, "pass")

    def test_verify_without_preimage_skips_hash(self):
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        # Use a nonexistent preimage path
        report = verify(record_path, preimage_path="/nonexistent/preimage.txt")
        check_names = {c.name: c for c in report.checks}
        self.assertEqual(check_names["record-hash"].status, "skip")

    def test_verify_content_hash(self):
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        # Content is spec/foundations.md + spec/protocol.md at commit 32d139e
        # We can't verify against current files (they've changed), so skip
        report = verify(record_path, content_paths=None)
        check_names = {c.name: c for c in report.checks}
        self.assertEqual(check_names["content-hash"].status, "skip")


class TestTimestampPlausibility(unittest.TestCase):

    def test_record_002_plausibility(self):
        """Record-002 timestamp is recent enough to pass plausibility."""
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        preimage_path = os.path.join(FIXTURES, "record-002-preimage.txt")
        report = verify(record_path, preimage_path=preimage_path)
        check_names = {c.name: c for c in report.checks}
        # Record is from 2026-04-16 — should be plausible (within 1 year)
        self.assertIn(check_names["timestamp-plausibility"].status, ("pass", "warn"))


class TestSessionNonceFormat(unittest.TestCase):

    def test_record_002_nonce_format(self):
        """Record-002 should have a valid session nonce."""
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}
        self.assertEqual(check_names["session-nonce"].status, "pass")


class TestVerifyRecord001(unittest.TestCase):

    def test_verify_record_001(self):
        record_path = os.path.join(FIXTURES, "record-001.mcap")
        preimage_path = os.path.join(FIXTURES, "record-001-preimage.txt")
        report = verify(record_path, preimage_path=preimage_path)

        check_names = {c.name: c for c in report.checks}
        self.assertEqual(check_names["record-parse"].status, "pass")
        self.assertEqual(check_names["record-hash"].status, "pass")
        self.assertEqual(check_names["timestamp-utc"].status, "pass")


if __name__ == "__main__":
    unittest.main()
