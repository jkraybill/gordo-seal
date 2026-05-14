"""CLI integration tests — test via subprocess."""

import os
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
SEAL = os.path.join(REPO_ROOT, "seal")


def run_seal(*args):
    """Run the seal CLI and return the result."""
    return subprocess.run(
        [SEAL] + list(args),
        capture_output=True, text=True, timeout=30
    )


class TestHashContentCLI(unittest.TestCase):

    def test_hash_single_file(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_seal("hash-content", path)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().startswith("SHA3-256:"))

    def test_hash_multiple_files(self):
        path1 = os.path.join(FIXTURES, "record-001-preimage.txt")
        path2 = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_seal("hash-content", path1, path2)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().startswith("SHA3-256:"))


class TestHashRecordCLI(unittest.TestCase):

    def test_hash_record_001(self):
        path = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_seal("hash-record", path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("77cb1db1d715d904f2780db76214410000796287f6caee6b1bb4942896369bc8",
                       result.stdout)

    def test_hash_record_002(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_seal("hash-record", path)
        self.assertEqual(result.returncode, 0)
        self.assertIn("83cd95f390b2e01507ba19cba6f1f89008e345b4d7a04f4d6dd5c048d7960ca3",
                       result.stdout)


class TestVerifyCLI(unittest.TestCase):

    def test_verify_record_002(self):
        record = os.path.join(FIXTURES, "record-002.mcap")
        preimage = os.path.join(FIXTURES, "record-002-preimage.txt")
        result = run_seal("verify", record, "--preimage", preimage)
        self.assertIn("[PASS] record-hash", result.stdout)
        self.assertIn("[PASS] timestamp-utc", result.stdout)

    def test_verify_record_001(self):
        record = os.path.join(FIXTURES, "record-001.mcap")
        preimage = os.path.join(FIXTURES, "record-001-preimage.txt")
        result = run_seal("verify", record, "--preimage", preimage)
        self.assertIn("[PASS] record-hash", result.stdout)

    def test_verify_missing_file(self):
        result = run_seal("verify", "/nonexistent/record.mcap")
        self.assertNotEqual(result.returncode, 0)


class TestNonceCLI(unittest.TestCase):

    def test_generate_entropy(self):
        result = run_seal("nonce")
        self.assertEqual(result.returncode, 0)
        # Should be 64 lowercase hex chars
        self.assertRegex(result.stdout.strip(), r"^[0-9a-f]{64}$")

    def test_combine_valid(self):
        a = "a" * 64
        b = "b" * 64
        result = run_seal("nonce", "--combine", a, b)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Session-Nonce:", result.stdout)

    def test_combine_rejects_short(self):
        result = run_seal("nonce", "--combine", "abcd", "efgh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("64 lowercase hex", result.stderr)

    def test_combine_rejects_uppercase(self):
        a = "A" * 64
        b = "b" * 64
        result = run_seal("nonce", "--combine", a, b)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lowercase", result.stderr)

    def test_combine_rejects_one_arg(self):
        result = run_seal("nonce", "--combine", "a" * 64)
        self.assertNotEqual(result.returncode, 0)


class TestVersionCLI(unittest.TestCase):

    def test_version(self):
        result = run_seal("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.2.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
