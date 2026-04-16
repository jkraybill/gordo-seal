"""Tests for mcap.hasher — SHA3-256 hashing."""

import hashlib
import os
import tempfile
import unittest

from mcap.hasher import hash_bytes, hash_content, hash_record, format_hash

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestHashBytes(unittest.TestCase):

    def test_known_answer(self):
        # Verify against stdlib directly
        data = b"hello world"
        expected = hashlib.sha3_256(data).hexdigest()
        self.assertEqual(hash_bytes(data), expected)

    def test_empty(self):
        expected = hashlib.sha3_256(b"").hexdigest()
        self.assertEqual(hash_bytes(b""), expected)


class TestFormatHash(unittest.TestCase):

    def test_format(self):
        self.assertEqual(format_hash("abc123"), "SHA3-256:abc123")


class TestHashContent(unittest.TestCase):

    def test_single_file(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"Hello\n")
            path = f.name
        try:
            result = hash_content([path])
            expected = hashlib.sha3_256(b"Hello\n").hexdigest()
            self.assertEqual(result, expected)
        finally:
            os.unlink(path)

    def test_multi_file_concatenation(self):
        paths = []
        try:
            for content in [b"AAA\n", b"BBB\n"]:
                f = tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False)
                f.write(content)
                f.close()
                paths.append(f.name)
            result = hash_content(paths)
            expected = hashlib.sha3_256(b"AAA\nBBB\n").hexdigest()
            self.assertEqual(result, expected)
        finally:
            for p in paths:
                os.unlink(p)


class TestHashRecord(unittest.TestCase):

    def test_record_001_golden(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = hash_record(path)
        self.assertEqual(result, "77cb1db1d715d904f2780db76214410000796287f6caee6b1bb4942896369bc8")

    def test_record_002_golden(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = hash_record(path)
        self.assertEqual(result, "83cd95f390b2e01507ba19cba6f1f89008e345b4d7a04f4d6dd5c048d7960ca3")


if __name__ == "__main__":
    unittest.main()
