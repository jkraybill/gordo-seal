"""Full verification pipeline for MCAP records."""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from mcap.canon import check_canonical
from mcap.hasher import hash_record, hash_content, format_hash
from mcap.record import parse_record, find_preimage
from mcap.signer import verify_signature, extract_signed_content


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


# Valid attestation method -> level combinations per spec
VALID_METHOD_LEVELS = {
    "behavioral": "1-behavioral",
    "provider-signed": "2-provider-verified",
    "model-canary": "2-provider-verified",
    "conversation-verified": "2-provider-verified",
    "gpg-signature": "3-identity-bound",
    "tee-attested": "4-environment-bound",
}

# ISO 8601 UTC pattern
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def verify(record_path: str, content_paths: list[str] | None = None,
           preimage_path: str | None = None) -> VerificationReport:
    """Run all verification checks on an MCAP record."""
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

    # 4. Attestation Method/Level consistency
    for party_key in ("Party-A", "Party-B"):
        party = record.get(party_key)
        if not isinstance(party, dict):
            continue
        method = party.get("Attestation-Method", "")
        level = party.get("Attestation-Level", "")
        expected = VALID_METHOD_LEVELS.get(method)
        if expected is None:
            report.add(f"{party_key}-method-level", "warn",
                       f"Unknown attestation method: {method}")
        elif expected == level:
            report.add(f"{party_key}-method-level", "pass",
                       f"{party_key}: {method} -> {level} (valid)")
        else:
            report.add(f"{party_key}-method-level", "fail",
                       f"{party_key}: {method} should be {expected}, got {level}")

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
