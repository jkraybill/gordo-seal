"""Tests for seal.stamper — OpenTimestamps wrapper."""

import os
import unittest

from seal.stamper import check_completeness

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestCheckCompleteness(unittest.TestCase):

    def test_final_record_is_complete(self):
        path = os.path.join(FIXTURES, "record-002.mcap")
        warnings = check_completeness(path)
        self.assertEqual(warnings, [])

    def test_preimage_has_warnings(self):
        path = os.path.join(FIXTURES, "record-002-preimage.txt")
        warnings = check_completeness(path)
        # Should warn about empty attestation and/or placeholder Record-Hash
        self.assertTrue(len(warnings) > 0)
        warning_text = " ".join(warnings)
        self.assertTrue(
            "Empty Attestation" in warning_text or "placeholder" in warning_text
        )


if __name__ == "__main__":
    unittest.main()
