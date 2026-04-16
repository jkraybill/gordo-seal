"""CLI integration tests — test via subprocess."""

import os
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
MCAP = os.path.join(REPO_ROOT, "mcap")


def run_mcap(*args):
    """Run the mcap CLI and return the result."""
    return subprocess.run(
        [MCAP] + list(args),
        capture_output=True, text=True, timeout=30
    )


class TestHashContentCLI(unittest.TestCase):

    def test_hash_single_file(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_mcap("hash-content", path)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().startswith("SHA3-256:"))

    def test_hash_multiple_files(self):
        path1 = os.path.join(FIXTURES, "record-001-preimage.txt")
        path2 = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_mcap("hash-content", path1, path2)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().startswith("SHA3-256:"))


class TestHashRecordCLI(unittest.TestCase):

    def test_hash_record_001(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_mcap("hash-record", path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("77cb1db1d715d904f2780db76214410000796287f6caee6b1bb4942896369bc8",
                       result.stdout)

    def test_hash_record_002(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_mcap("hash-record", path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("83cd95f390b2e01507ba19cba6f1f89008e345b4d7a04f4d6dd5c048d7960ca3",
                       result.stdout)


class TestVerifyCLI(unittest.TestCase):

    def test_verify_record_002(self):
        record = os.path.join(FIXTURES, "record-002.mcap")
        preimage = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_mcap("verify", record, "--preimage", preimage)
        self.assertIn("[PASS] record-hash", result.stdout)
        self.assertIn("[PASS] timestamp-utc", result.stdout)

    def test_verify_record_001(self):
        record = os.path.join(FIXTURES, "record-001.mcap")
        preimage = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_mcap("verify", record, "--preimage", preimage)
        self.assertIn("[PASS] record-hash", result.stdout)

    def test_verify_missing_file(self):
        result = run_mcap("verify", "/nonexistent/record.mcap")
        self.assertNotEqual(result.returncode, 0)


class TestVersionCLI(unittest.TestCase):

    def test_version(self):
        result = run_mcap("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.2.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
