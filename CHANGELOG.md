# Changelog

All notable changes to the MCAP protocol specification and tooling.

Versioning policy: Major = axiom changes, attestation level restructuring, breaking record format changes. Minor = new normative requirements, new record fields, tooling. Patch = clarifications, typo fixes, non-normative documentation.

## 0.2.0 (2026-04-16)

### Specification
- **Character allowlist for canonicalization** (#77): normative restriction blocking invisible Unicode injection (bidi overrides, zero-width spaces, soft hyphens, etc.). Allows L, M, N, P, S, U+0020, LF, Tab, ZWNJ (Persian/Urdu), ZWJ (Indic scripts/emoji). Validated against top-30 internet languages. Corrects false claim that NFC handles zero-width characters.
- **Nonce ceremony tightened** (#78): session nonce generation now normative — SHA3-256 of concatenated 64-char lowercase hex contributions, Individual A first
- **Statement authorship requirement** (normative): each party MUST author their own Statement
- **Preimage placeholder normalization** (#67): normative placeholder text for Record-Hash field in preimages
- **UTC timestamp requirement** (#72): Timestamp-Local MUST use UTC time source
- Versioning policy added

### Tooling
- **`mcap` CLI tool** (#6): 7 subcommands — hash-content, hash-record, sign, finalize, verify, stamp, nonce
- **`mcap verify` enhancements** (#79): timestamp plausibility check, Session-Nonce format validation, character allowlist warnings via canonical form check
- **`mcap nonce` validation** (#78): --combine now validates contributions are 64 lowercase hex chars
- **Canonicalization engine** (#77): strips disallowed invisible characters, replaces non-standard spaces, warns on ZWJ/ZWNJ presence
- Python 3 stdlib only, zero external dependencies
- 94 tests (up from 53) including golden file verification against record-001 and record-002
- `ratification/GUIDE.md` implementation guide (#73)

### Upgrading from 0.1.0

**Existing records are unaffected.** Records produced under v0.1.0 are historical facts — they remain valid under the version they were created with. `mcap verify` on v0.1.0 records continues to pass (verified by golden file tests).

**New records MUST follow v0.2.0.** Key changes for record producers:
- Canonicalization now enforces a character allowlist — invisible characters will be stripped. Run `mcap verify` to check content before signing.
- Each party MUST author their own Statement (no drafting the other party's Statement).
- Session nonce MUST use the normative format: each party contributes 64 lowercase hex chars, combined with SHA3-256, Individual A first. Use `mcap nonce` to generate and combine.
- Record-Hash preimage MUST use the normative placeholder text: `Record-Hash: SHA3-256:<preimage — this field is excluded from its own computation>`

No re-attestation of existing records is required.

### Fixes
- **record-002 Timestamp-Local** (#72): corrected from 2026-04-17 to 2026-04-16, re-signed, re-stamped

## 0.1.0 (2026-04-16)

### Specification
- Initial protocol specification: `spec/foundations.md` (Axioms 1-4) and `spec/protocol.md`
- 4 attestation levels: Behavioral, Provider-Verified, Identity-Bound, Environment-Bound
- 20+ documented threat models
- 14 adversarial reviews across 3 cycles from 5 independent models (converged)
- Tension resolutions: T1-T5 resolved, T6 rejected, T7 deferred

### Ratification Records
- record-001: Axioms 1-4 (L3/L1, GPG + behavioral, OTS-anchored)
- record-002: MCAP v0.1.0 spec ratified using itself (L3/L1, OTS-anchored)
