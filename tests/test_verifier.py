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


class TestAttestationFieldContent(unittest.TestCase):
    """Tests for v0.5.0 Attestation Field Content requirements (spec amendment #86).

    Spec requirements:
    - Level 2+ MUST have non-empty Attestation field (FAIL if empty)
    - Level 1 (behavioral) MAY have empty Attestation field
    - See [path] references must resolve; path must be relative, no ..
    - Pre-v0.5.0 records get warning not failure (backwards compat)
    """

    def test_level2_empty_attestation_fails(self):
        """Level 2+ with empty Attestation field should FAIL verification."""
        record_path = os.path.join(FIXTURES, "record-empty-attestation-level2.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should have attestation-required check that FAILs
        self.assertIn("Party-A-attestation-required", check_names)
        self.assertEqual(check_names["Party-A-attestation-required"].status, "fail")

    def test_level1_empty_attestation_ok(self):
        """Level 1 (behavioral) with empty Attestation field is allowed."""
        record_path = os.path.join(FIXTURES, "record-empty-attestation-level1.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should NOT have a failing attestation-required check for behavioral
        for name, check in check_names.items():
            if "attestation-required" in name:
                self.assertNotEqual(check.status, "fail",
                    f"Level 1 should allow empty Attestation: {name}={check.status}")

    def test_v040_empty_attestation_warns(self):
        """Pre-v0.5.0 records with empty Attestation get warning, not failure."""
        record_path = os.path.join(FIXTURES, "record-v040-empty-attestation.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should be warn, not fail (backwards compat)
        if "Party-A-attestation-required" in check_names:
            self.assertIn(check_names["Party-A-attestation-required"].status, ("warn", "pass"))

    def test_asymmetric_attestation_no_gpg_fail_for_behavioral(self):
        """Asymmetric attestation (Party-A gpg, Party-B behavioral) should not fail GPG check on Party-B (#84)."""
        record_path = os.path.join(FIXTURES, "record-asymmetric-attestation.seal")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Party-B should NOT have a GPG check fail (behavioral method doesn't use GPG)
        party_b_gpg = check_names.get("Party-B-gpg")
        self.assertIsNone(party_b_gpg,
            f"Party-B with behavioral method should not have GPG check: {party_b_gpg}")

        # Party-B should have attestation-method pass indicating behavioral is valid
        party_b_method = check_names.get("Party-B-attestation-method")
        self.assertIsNotNone(party_b_method,
            "Party-B should have attestation-method check")
        self.assertEqual(party_b_method.status, "pass",
            f"Party-B behavioral attestation should pass: {party_b_method.detail}")

        # Overall verification should not have any FAILs except for missing signature files
        # (which is expected since we don't create actual GPG sigs for fixtures)
        for check in report.checks:
            if "Party-B" in check.name and check.status == "fail":
                self.fail(f"Party-B should not have fails: {check.name}={check.status}: {check.detail}")


class TestAttestationPathSecurity(unittest.TestCase):
    """Tests for path security in See [path] references."""

    def test_path_traversal_rejected(self):
        """Path containing .. should be rejected."""
        record_path = os.path.join(FIXTURES, "record-path-traversal.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should have a path-security check that FAILs
        path_checks = [c for n, c in check_names.items() if "path" in n.lower()]
        failed = [c for c in path_checks if c.status == "fail"]
        self.assertTrue(len(failed) > 0 or any(
            "path" in c.detail.lower() and c.status == "fail"
            for c in report.checks
        ), "Path traversal should be rejected")

    def test_absolute_path_rejected(self):
        """Absolute paths should be rejected."""
        record_path = os.path.join(FIXTURES, "record-absolute-path.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should fail due to absolute path
        path_checks = [c for n, c in check_names.items() if "path" in n.lower()]
        failed = [c for c in path_checks if c.status == "fail"]
        self.assertTrue(len(failed) > 0 or any(
            "path" in c.detail.lower() and c.status == "fail"
            for c in report.checks
        ), "Absolute path should be rejected")

    def test_valid_relative_path_accepted(self):
        """Valid relative path should be accepted."""
        # record-002 has valid See reference
        record_path = os.path.join(FIXTURES, "record-002.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should not have path security failures
        for name, check in check_names.items():
            if "path" in name.lower():
                self.assertNotEqual(check.status, "fail",
                    f"Valid relative path should be accepted: {check.detail}")


class TestAttestationHashValidation(unittest.TestCase):
    """Tests for optional sha256 suffix validation."""

    def test_hash_suffix_valid(self):
        """See [path] (sha256:[hex]) with matching hash should pass."""
        record_path = os.path.join(FIXTURES, "record-hash-suffix-valid.mcap")
        if not os.path.exists(record_path):
            self.skipTest("Fixture not yet created")
        report = verify(record_path)
        self.assertTrue(report.passed, "Valid hash suffix should pass")

    def test_hash_suffix_mismatch_fails(self):
        """See [path] (sha256:[hex]) with wrong hash should fail."""
        record_path = os.path.join(FIXTURES, "record-hash-suffix-mismatch.mcap")
        if not os.path.exists(record_path):
            self.skipTest("Fixture not yet created")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should have a hash validation failure
        failed = [c for c in report.checks if c.status == "fail" and "hash" in c.detail.lower()]
        self.assertTrue(len(failed) > 0, "Hash mismatch should fail")


class TestContentFieldFormat(unittest.TestCase):
    """Tests for v0.6.0 Content Field Format requirements.

    Spec requirements:
    - Content MUST use See [path] format
    - Content file MUST exist (FAIL if missing)
    - Pre-v0.6.0 records get warning not failure (backwards compat)
    """

    def test_v060_freeform_content_fails(self):
        """v0.6.0 record with freeform Content should FAIL."""
        record_path = os.path.join(FIXTURES, "record-v060-freeform-content.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should have content-format check that FAILs
        self.assertIn("content-format", check_names)
        self.assertEqual(check_names["content-format"].status, "fail")

    def test_v050_freeform_content_warns(self):
        """Pre-v0.6.0 record with freeform Content should WARN (backwards compat)."""
        record_path = os.path.join(FIXTURES, "record-v050-freeform-content.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should be warn, not fail
        if "content-format" in check_names:
            self.assertIn(check_names["content-format"].status, ("warn", "pass"))

    def test_content_file_missing_fails(self):
        """Content: See [path] where file doesn't exist should FAIL."""
        record_path = os.path.join(FIXTURES, "record-content-missing-file.mcap")
        report = verify(record_path)
        check_names = {c.name: c for c in report.checks}

        # Should fail because referenced file doesn't exist
        failed = [c for c in report.checks
                  if c.status == "fail" and "content" in c.name.lower()]
        self.assertTrue(len(failed) > 0 or any(
            "content" in c.detail.lower() and c.status == "fail"
            for c in report.checks
        ), "Missing content file should fail")

    def test_content_path_traversal_fails(self):
        """Content: See ../path should be rejected."""
        record_path = os.path.join(FIXTURES, "record-content-path-traversal.mcap")
        report = verify(record_path)

        # Should fail due to path traversal
        failed = [c for c in report.checks
                  if c.status == "fail" and ("path" in c.detail.lower() or "content" in c.name.lower())]
        self.assertTrue(len(failed) > 0, "Content path traversal should be rejected")


if __name__ == "__main__":
    unittest.main()
