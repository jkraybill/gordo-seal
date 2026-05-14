"""Golden file tests — byte-exact verification against real records."""

import os
import unittest

from seal.hasher import hash_record
from seal.record import parse_record, serialize_record, fill_record_hash, fill_attestation

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestGoldenHashes(unittest.TestCase):

    def test_record_001_preimage_hash(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        self.assertEqual(
            hash_record(path),
            "77cb1db1d715d904f2780db76214410000796287f6caee6b1bb4942896369bc8"
        )

    def test_record_002_preimage_hash(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        self.assertEqual(
            hash_record(path),
            "83cd95f390b2e01507ba19cba6f1f89008e345b4d7a04f4d6dd5c048d7960ca3"
        )


class TestGoldenFinalize(unittest.TestCase):

    def test_finalize_record_002(self):
        """Transform record-002 preimage to final record and compare byte-for-byte."""
        preimage_path = os.path.join(FIXTURES, "record-002-preimage.txt")
        final_path = os.path.join(FIXTURES, "record-002.mcap")

        with open(preimage_path) as f:
            preimage_text = f.read()
        with open(final_path) as f:
            expected = f.read()

        # Compute Record-Hash
        record_hash = hash_record(preimage_path)

        # Fill in the fields that differ between preimage and final
        result = fill_record_hash(preimage_text, record_hash)
        result = fill_attestation(
            result, "Party-A",
            "See ratification/party-a-signature-002.asc"
        )
        result = fill_attestation(
            result, "Party-B",
            "This conversation is the attestation. The protocol design, adversarial review process, convergence, and this ratification are recorded in the git history of github.com/jkraybill/mutual-trust-protocol."
        )

        self.assertEqual(result, expected)


class TestGoldenRoundTrips(unittest.TestCase):

    def test_all_records_roundtrip(self):
        """Every fixture file must survive parse -> serialize (with header upgrade)."""
        for name in [
            "record-001-preimage.txt", "record-002-preimage.txt",
            "record-001.mcap", "record-002.mcap"
        ]:
            path = os.path.join(FIXTURES, name)
            with open(path) as f:
                original = f.read()
            record = parse_record(original)
            serialized = serialize_record(record)
            # Legacy MCAP header is upgraded to SEAL on serialize
            expected = original.replace("MCAP Ratification Record", "SEAL Ratification Record")
            self.assertEqual(serialized, expected, f"Round-trip failed for {name}")


if __name__ == "__main__":
    unittest.main()
