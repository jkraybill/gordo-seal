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


class TestCanonicalizeCharacterAllowlist(unittest.TestCase):
    """Tests for invisible/disallowed character stripping in canonicalize()."""

    def test_strips_zero_width_space(self):
        text = "Hello\u200BWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_zero_width_non_breaking_space(self):
        # U+FEFF when not at start of file (BOM position) is ZWNBSP
        text = "Hello\uFEFFWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_soft_hyphen(self):
        text = "Hel\u00ADlo\n"
        self.assertEqual(canonicalize(text), "Hello\n")

    def test_strips_word_joiner(self):
        text = "Hello\u2060World\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_bidi_override_rtl(self):
        text = "Hello\u202EWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_bidi_override_ltr(self):
        text = "Hello\u202DWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_bidi_embedding(self):
        text = "Hello\u202AWorld\u202C\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_bidi_isolates(self):
        text = "Hello\u2066World\u2069\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_ltr_mark(self):
        text = "Hello\u200EWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_rtl_mark(self):
        text = "Hello\u200FWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_arabic_letter_mark(self):
        text = "Hello\u061CWorld\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_tag_characters(self):
        text = "Hello\U000E0001World\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_control_chars_except_lf_tab(self):
        # Bell, null, vertical tab, form feed
        text = "Hel\x07\x00\x0B\x0Clo\n"
        self.assertEqual(canonicalize(text), "Hello\n")

    def test_preserves_tab(self):
        # Tab is trailing whitespace on a line, so rstrip removes it at EOL
        # but mid-line tabs should survive allowlist (then rstrip handles EOL)
        text = "Hello\tWorld\n"
        self.assertEqual(canonicalize(text), "Hello\tWorld\n")

    def test_preserves_zwj(self):
        """ZWJ (U+200D) is allowed — required for Malayalam, Sinhala, emoji."""
        text = "Hello\u200DWorld\n"
        self.assertEqual(canonicalize(text), "Hello\u200DWorld\n")

    def test_preserves_zwnj(self):
        """ZWNJ (U+200C) is allowed — required for Persian/Urdu orthography."""
        text = "Hello\u200CWorld\n"
        self.assertEqual(canonicalize(text), "Hello\u200CWorld\n")

    def test_preserves_latin(self):
        text = "Hello World 123 !@#$%\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_cjk(self):
        text = "你好世界\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_arabic(self):
        text = "مرحبا بالعالم\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_devanagari_with_combining_marks(self):
        """Hindi text with category M marks must survive."""
        text = "हिन्दी\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_thai(self):
        """Thai relies entirely on combining marks (category M)."""
        text = "ภาษาไทย\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_korean(self):
        text = "안녕하세요\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_persian_with_zwnj(self):
        """Persian orthography requires ZWNJ — must not be stripped."""
        text = "می\u200Cخواهم\n"
        self.assertEqual(canonicalize(text), text)

    def test_preserves_emoji(self):
        text = "Hello 🌍🎉\n"
        self.assertEqual(canonicalize(text), text)

    def test_strips_nonstandard_spaces(self):
        """Non-breaking space (U+00A0), em space (U+2003), etc. replaced."""
        text = "Hello\u00A0World\n"
        # Non-standard Zs should be replaced with standard space
        self.assertEqual(canonicalize(text), "Hello World\n")

    def test_strips_private_use(self):
        text = "Hello\uE000World\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_line_separator(self):
        text = "Hello\u2028World\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")

    def test_strips_paragraph_separator(self):
        text = "Hello\u2029World\n"
        self.assertEqual(canonicalize(text), "HelloWorld\n")


class TestCheckCanonicalCharacterAllowlist(unittest.TestCase):
    """Tests for check_canonical detecting disallowed characters."""

    def test_detects_zero_width_space(self):
        data = "Hello\u200BWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("disallowed" in i.issue.lower() or "character" in i.issue.lower()
                            for i in issues))

    def test_detects_bidi_override(self):
        data = "Hello\u202EWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("disallowed" in i.issue.lower() or "character" in i.issue.lower()
                            for i in issues))

    def test_warns_on_zwj(self):
        """ZWJ is allowed but should produce a warning."""
        data = "Hello\u200DWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("zwj" in i.issue.lower() or "u+200d" in i.issue.lower()
                            for i in issues))

    def test_warns_on_zwnj(self):
        """ZWNJ is allowed but should produce a warning."""
        data = "Hello\u200CWorld\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("zwnj" in i.issue.lower() or "u+200c" in i.issue.lower()
                            for i in issues))

    def test_detects_nonstandard_space(self):
        data = "Hello\u00A0World\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertTrue(any("space" in i.issue.lower() or "disallowed" in i.issue.lower()
                            for i in issues))

    def test_no_issues_for_clean_multilingual(self):
        """Clean multilingual text should produce no issues."""
        data = "Hello 你好 مرحبا हिन्दी ภาษาไทย\n".encode("utf-8")
        issues = check_canonical(data)
        self.assertEqual(issues, [])


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
