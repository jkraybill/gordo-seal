"""Tests for mcap.canon — canonicalization engine."""

import unittest

from mcap.canon import canonicalize, check_canonical


class TestCanonicalize(unittest.TestCase):

    def test_already_canonical(self):
        text = "Hello\nWorld\n"
        self.assertEqual(canonicalize(text), text)

    def test_strips_bom(self):
        text = "\ufeffHello\n"
        self.assertEqual(canonicalize(text), "Hello\n")

    def test_converts_crlf_to_lf(self):
        text = "Hello\r\nWorld\r\n"
        self.assertEqual(canonicalize(text), "Hello\nWorld\n")

    def test_converts_bare_cr_to_lf(self):
        text = "Hello\rWorld\r"
        self.assertEqual(canonicalize(text), "Hello\nWorld\n")

    def test_strips_trailing_whitespace(self):
        text = "Hello   \nWorld\t\n"
        self.assertEqual(canonicalize(text), "Hello\nWorld\n")

    def test_nfc_normalization(self):
        # e + combining acute (NFD) -> e-acute (NFC)
        nfd = "caf\u0065\u0301\n"
        nfc = "caf\u00e9\n"
        self.assertEqual(canonicalize(nfd), nfc)

    def test_ensures_trailing_newline(self):
        text = "Hello"
        self.assertEqual(canonicalize(text), "Hello\n")

    def test_empty_string(self):
        self.assertEqual(canonicalize(""), "\n")

    def test_mixed_issues(self):
        text = "\ufeffHello \r\nWorld\t\r"
        self.assertEqual(canonicalize(text), "Hello\nWorld\n")


class TestCheckCanonical(unittest.TestCase):

    def test_canonical_file_no_issues(self):
        data = "Hello\nWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertEqual(issues, [])

    def test_detects_bom(self):
        data = b"\xef\xbb\xbfHello\n"
        issues = check_canonical(data)
        self.assertTrue(any("BOM" in i.issue for i in issues))

    def test_detects_cr(self):
        data = "Hello\r\nWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("CR" in i.issue or "CRLF" in i.issue for i in issues))

    def test_detects_trailing_whitespace(self):
        data = "Hello   \nWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("trailing" in i.issue.lower() for i in issues))

    def test_detects_non_nfc(self):
        data = "caf\u0065\u0301\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("NFC" in i.issue for i in issues))

    def test_detects_missing_trailing_newline(self):
        data = "Hello".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("newline" in i.issue.lower() for i in issues))


if __name__ == "__main__":
    unittest.main()
