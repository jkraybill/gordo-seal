"""Full verification pipeline for SEAL records."""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from seal.canon import check_canonical
from seal.hasher import hash_record, hash_content, format_hash
from seal.record import parse_record, find_preimage
from seal.signer import verify_signature, extract_signed_content


@dataclass
class CheckResult:
    name: str
    status: str  # pass, fail, skip, warn
    detail: str


@dataclass
class VerificationReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.status in ("pass", "skip", "warn") for c in self.checks)

    def add(self, name: str, status: str, detail: str):
        self.checks.append(CheckResult(name, status, detail))


# Valid attestation method -> level combinations per spec v0.4.0
# Note: gpg-signature can be Level 2 (session-signed), 3 (provider-verified with sig),
# or 4 (identity-bound). The method alone doesn't determine level; trust root qualifiers
# and custody model determine whether it's session-signed vs identity-bound.
#
# BACKWARDS COMPATIBILITY: Also accepts old level numbers from v0.1.0-v0.3.0:
# - Old "2-provider-verified" -> now "3-provider-verified"
# - Old "3-identity-bound" -> now "4-identity-bound"
# - Old "4-environment-bound" -> now "5-environment-bound"
VALID_METHOD_LEVELS = {
    # Level 1: No cryptographic binding
    "behavioral": ["1-behavioral"],
    # Level 2: Session-signed (new in v0.4.0) - GPG with co-custody or session-bound key
    # Level 3: Provider-verified - provider signs/verifies (was Level 2 in v0.3.0)
    "provider-signed": ["3-provider-verified", "2-provider-verified"],
    "model-canary": ["3-provider-verified", "2-provider-verified"],
    "conversation-verified": ["3-provider-verified", "2-provider-verified"],
    # GPG can be Level 2 (session-signed), Level 3/4 (identity-bound)
    # Also accepts old "3-identity-bound" from v0.3.0
    "gpg-signature": ["2-session-signed", "3-provider-verified", "4-identity-bound", "3-identity-bound"],
    # Level 5: Environment-bound (TEE) - was Level 4 in v0.3.0
    "tee-attested": ["5-environment-bound", "4-environment-bound"],
}

# ISO 8601 UTC pattern
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def verify(record_path: str, content_paths: list[str] | None = None,
           preimage_path: str | None = None) -> VerificationReport:
    """Run all verification checks on an SEAL record."""
    report = VerificationReport()

    # Read the record
    try:
        with open(record_path) as f:
            record_text = f.read()
        record = parse_record(record_text)
    except Exception as e:
        report.add("record-parse", "fail", f"Cannot parse record: {e}")
        return report

    report.add("record-parse", "pass", "Record parsed successfully")

    # 1. Canonical form check on record
    with open(record_path, "rb") as f:
        record_bytes = f.read()
    issues = check_canonical(record_bytes)
    if issues:
        detail = "; ".join(f"{i.issue}" for i in issues)
        report.add("canonical-form", "warn", f"Record has canonicalization issues: {detail}")
    else:
        report.add("canonical-form", "pass", "Record is in canonical form")

    # 2. Record-Hash check
    if preimage_path is None:
        preimage_path = find_preimage(record_path)

    if preimage_path and os.path.exists(preimage_path):
        # Check preimage canonical form
        with open(preimage_path, "rb") as f:
            preimage_bytes = f.read()
        preimage_issues = check_canonical(preimage_bytes)
        if preimage_issues:
            detail = "; ".join(f"{i.issue}" for i in preimage_issues)
            report.add("preimage-canonical", "warn", f"Preimage has issues: {detail}")
        else:
            report.add("preimage-canonical", "pass", "Preimage is in canonical form")

        computed_hash = hash_record(preimage_path)
        stored_hash = record.get("Record-Hash", "")
        if stored_hash.startswith("SHA3-256:"):
            stored_hex = stored_hash.split("SHA3-256:")[1]
            if computed_hash == stored_hex:
                report.add("record-hash", "pass",
                           f"Record-Hash matches preimage: {computed_hash[:16]}...")
            else:
                report.add("record-hash", "fail",
                           f"Record-Hash mismatch. Computed: {computed_hash}, stored: {stored_hex}")
        else:
            report.add("record-hash", "skip",
                       f"Record-Hash not in expected format: {stored_hash[:50]}")
    else:
        report.add("record-hash", "skip",
                   "No preimage found. Use --preimage to specify.")

    # 3. Content-Hash check
    if content_paths:
        computed = format_hash(hash_content(content_paths))
        stored = record.get("Content-Hash", "")
        if computed == stored:
            report.add("content-hash", "pass",
                       f"Content-Hash matches: {computed[:30]}...")
        else:
            report.add("content-hash", "fail",
                       f"Content-Hash mismatch. Computed: {computed}, stored: {stored}")
    else:
        report.add("content-hash", "skip",
                   "No content files specified. Use --content to verify.")

    # 4. Attestation Method/Level consistency (updated for v0.4.0)
    for party_key in ("Party-A", "Party-B"):
        party = record.get(party_key)
        if not isinstance(party, dict):
            continue
        method = party.get("Attestation-Method", "")
        level = party.get("Attestation-Level", "")
        valid_levels = VALID_METHOD_LEVELS.get(method)
        if valid_levels is None:
            report.add(f"{party_key}-method-level", "warn",
                       f"Unknown attestation method: {method}")
        elif level in valid_levels:
            report.add(f"{party_key}-method-level", "pass",
                       f"{party_key}: {method} -> {level} (valid)")
        else:
            report.add(f"{party_key}-method-level", "fail",
                       f"{party_key}: {method} should be one of {valid_levels}, got {level}")

    # 4b. Trust Root Qualifiers check (v0.4.0 - mandatory for Level 2+)
    SIGNED_LEVELS = ["2-session-signed", "3-provider-verified", "4-identity-bound", "5-environment-bound"]
    VALID_CUSTODY = ["/self", "/co", "/third", "/threshold"]
    VALID_STORAGE = ["/file", "/kms", "/hw", "/tee"]

    for party_key in ("Party-A", "Party-B"):
        party = record.get(party_key)
        if not isinstance(party, dict):
            continue
        level = party.get("Attestation-Level", "")
        if level in SIGNED_LEVELS:
            custody = party.get("Key-Custody", "")
            storage = party.get("Key-Storage", "")

            if not custody:
                report.add(f"{party_key}-trust-root", "warn",
                           f"{party_key} at {level} missing Key-Custody (required for Level 2+)")
            elif custody not in VALID_CUSTODY and not custody.startswith("/threshold"):
                report.add(f"{party_key}-trust-root", "warn",
                           f"{party_key} Key-Custody '{custody}' not in {VALID_CUSTODY}")
            else:
                # For Level 4, /co is not acceptable
                if level == "4-identity-bound" and custody == "/co":
                    report.add(f"{party_key}-trust-root", "fail",
                               f"{party_key} at Level 4 cannot use /co custody (defeats identity independence)")
                else:
                    report.add(f"{party_key}-trust-root", "pass",
                               f"{party_key} Key-Custody: {custody}")

            if not storage:
                report.add(f"{party_key}-key-storage", "warn",
                           f"{party_key} at {level} missing Key-Storage (required for Level 2+)")
            elif storage not in VALID_STORAGE:
                report.add(f"{party_key}-key-storage", "warn",
                           f"{party_key} Key-Storage '{storage}' not in {VALID_STORAGE}")
            else:
                report.add(f"{party_key}-key-storage", "pass",
                           f"{party_key} Key-Storage: {storage}")

    # 4c. Attestation Field Content check (v0.5.0)
    # Level 2+ requires non-empty Attestation field
    # Pre-v0.5.0 records get warning, not failure (backwards compat)
    record_version = record.get("Version", "")
    is_pre_v050 = record_version and record_version < "0.5.0"

    for party_key in ("Party-A", "Party-B"):
        party = record.get(party_key)
        if not isinstance(party, dict):
            continue
        level = party.get("Attestation-Level", "")
        attestation = party.get("Attestation", "").strip()

        if level in SIGNED_LEVELS:
            if not attestation:
                if is_pre_v050:
                    report.add(f"{party_key}-attestation-required", "warn",
                               f"{party_key} at {level} has empty Attestation field "
                               f"(pre-v0.5.0 record; treated as effective Level 1)")
                else:
                    report.add(f"{party_key}-attestation-required", "fail",
                               f"{party_key} at {level} has empty Attestation field "
                               f"(required for Level 2+)")
            elif attestation.startswith("See "):
                # Validate path security
                sig_ref = attestation[4:].split()[0]  # Handle optional hash suffix
                if ".." in sig_ref:
                    report.add(f"{party_key}-attestation-path", "fail",
                               f"{party_key} Attestation path contains '..': {sig_ref}")
                elif sig_ref.startswith("/"):
                    report.add(f"{party_key}-attestation-path", "fail",
                               f"{party_key} Attestation path is absolute: {sig_ref}")
                else:
                    report.add(f"{party_key}-attestation-required", "pass",
                               f"{party_key} Attestation field populated")

    # 5. Timestamp-Local check
    ts = record.get("Timestamp-Local", "")
    if not ts:
        report.add("timestamp-utc", "warn", "No Timestamp-Local field")
    elif not UTC_PATTERN.match(ts):
        report.add("timestamp-utc", "fail",
                   f"Timestamp-Local not in UTC format (expected YYYY-MM-DDTHH:MM:SSZ): {ts}")
    else:
        report.add("timestamp-utc", "pass", f"Timestamp-Local is valid UTC: {ts}")

    # 6. Timestamp plausibility check
    if ts and UTC_PATTERN.match(ts):
        try:
            record_time = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = abs((now - record_time).total_seconds())
            if delta > 86400 * 365:  # > 1 year
                report.add("timestamp-plausibility", "warn",
                           f"Timestamp-Local is {delta / 86400:.0f} days from current time")
            else:
                report.add("timestamp-plausibility", "pass",
                           f"Timestamp-Local within plausible range ({delta / 3600:.1f} hours ago)")
        except ValueError:
            report.add("timestamp-plausibility", "skip", "Could not parse timestamp for plausibility check")

    # 7. Session-Nonce format check
    nonce = record.get("Session-Nonce", "")
    if not nonce:
        report.add("session-nonce", "warn", "No Session-Nonce field")
    elif re.fullmatch(r"[0-9a-f]{64}", nonce):
        report.add("session-nonce", "pass", f"Session-Nonce is valid format: {nonce[:16]}...")
    else:
        detail = f"Expected 64 lowercase hex chars, got {len(nonce)} chars"
        if re.fullmatch(r"[0-9a-fA-F]{64}", nonce):
            detail = "Contains uppercase hex — must be lowercase"
        report.add("session-nonce", "fail", f"Session-Nonce format invalid. {detail}")

    # 8. GPG signature check
    for party_key in ("Party-A", "Party-B"):
        party = record.get(party_key)
        if not isinstance(party, dict):
            continue
        attestation = party.get("Attestation", "")
        if attestation.startswith("See "):
            sig_ref = attestation[4:]
            # Resolve relative to record directory
            record_dir = os.path.dirname(record_path)
            # Handle paths relative to repo root
            if sig_ref.startswith("ratification/"):
                sig_path = os.path.join(os.path.dirname(record_dir), sig_ref)
            else:
                sig_path = os.path.join(record_dir, sig_ref)

            if not os.path.exists(sig_path):
                # Try relative to record dir directly
                sig_path = os.path.join(record_dir, os.path.basename(sig_ref))

            if os.path.exists(sig_path):
                try:
                    sig_result = verify_signature(sig_path)
                    if sig_result.valid:
                        # Also check that the signed content matches Record-Hash
                        signed_content = extract_signed_content(sig_path)
                        stored_hash = record.get("Record-Hash", "")
                        if stored_hash.startswith("SHA3-256:"):
                            stored_hex = stored_hash.split("SHA3-256:")[1]
                            if signed_content.strip() == stored_hex:
                                report.add(f"{party_key}-gpg", "pass",
                                           f"{party_key} GPG signature valid, covers Record-Hash")
                            else:
                                report.add(f"{party_key}-gpg", "fail",
                                           f"{party_key} GPG signature valid but covers wrong hash. "
                                           f"Signed: {signed_content.strip()[:16]}..., "
                                           f"Record-Hash: {stored_hex[:16]}...")
                        else:
                            report.add(f"{party_key}-gpg", "pass",
                                       f"{party_key} GPG signature valid")
                    else:
                        report.add(f"{party_key}-gpg", "fail",
                                   f"{party_key} GPG signature invalid: {sig_result.error}")
                except Exception as e:
                    report.add(f"{party_key}-gpg", "fail", f"GPG verification error: {e}")
            else:
                report.add(f"{party_key}-gpg", "warn",
                           f"Signature file not found: {sig_ref}")

    # 9. OTS proof exists
    ots_path = record_path + ".ots"
    if os.path.exists(ots_path):
        report.add("ots-exists", "pass", f"OTS proof file exists: {os.path.basename(ots_path)}")
    else:
        report.add("ots-exists", "warn", "No .ots proof file found")

    return report
