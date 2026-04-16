"""Tests for mcap.record — record parsing and assembly."""

import os
import unittest

from mcap.record import parse_record, serialize_record, RECORD_HASH_PLACEHOLDER

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestParseRecord(unittest.TestCase):

    def test_parse_record_001_preimage(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        with open(path) as f:
            record = parse_record(f.read())
        self.assertEqual(record["Version"], "0.1.0")
        self.assertEqual(record["Amendments"], "none")
        self.assertEqual(record["Party-A"]["Attestation-Method"], "gpg-signature")
        self.assertEqual(record["Party-A"]["Attestation"], "")
        self.assertEqual(record["Party-A"]["Attestation-Level"], "3-identity-bound")
        self.assertEqual(record["Party-B"]["Attestation-Method"], "behavioral")
        self.assertEqual(record["Party-B"]["Attestation-Level"], "1-behavioral")
        self.assertTrue(record["Party-A"]["Statement"].startswith("I consent"))

    def test_parse_record_002_preimage(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        with open(path) as f:
            record = parse_record(f.read())
        self.assertEqual(record["Version"], "0.1.0")
        self.assertIn("Session 4 instance", record["Party-B"]["Identity"])
        self.assertEqual(record["Timestamp-Local"], "2026-04-16T03:01:00Z")

    def test_parse_final_record_002(self):
        path = os.path.join(FIXTURES, "record-002.mcap")
        with open(path) as f:
            record = parse_record(f.read())
        self.assertIn("party-a-signature-002.asc", record["Party-A"]["Attestation"])
        self.assertIn("SHA3-256:", record["Record-Hash"])


class TestSerializeRecord(unittest.TestCase):

    def test_roundtrip_record_001_preimage(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        with open(path) as f:
            original = f.read()
        record = parse_record(original)
        serialized = serialize_record(record)
        self.assertEqual(serialized, original)

    def test_roundtrip_record_002_preimage(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        with open(path) as f:
            original = f.read()
        record = parse_record(original)
        serialized = serialize_record(record)
        self.assertEqual(serialized, original)

    def test_roundtrip_record_002_final(self):
        path = os.path.join(FIXTURES, "record-002.mcap")
        with open(path) as f:
            original = f.read()
        record = parse_record(original)
        serialized = serialize_record(record)
        self.assertEqual(serialized, original)


class TestRecordHashPlaceholder(unittest.TestCase):

    def test_placeholder_has_em_dash(self):
        self.assertIn("\u2014", RECORD_HASH_PLACEHOLDER)

    def test_placeholder_starts_with_sha3(self):
        self.assertTrue(RECORD_HASH_PLACEHOLDER.startswith("SHA3-256:"))


if __name__ == "__main__":
    unittest.main()
