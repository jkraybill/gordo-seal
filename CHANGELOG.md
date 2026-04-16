# Changelog

All notable changes to the MCAP protocol specification and tooling.

Versioning policy: Major = axiom changes, attestation level restructuring, breaking record format changes. Minor = new normative requirements, new record fields, tooling. Patch = clarifications, typo fixes, non-normative documentation.

## 0.2.0 (2026-04-16)

### Specification
- **Statement authorship requirement** (normative): each party MUST author their own Statement
- **Preimage placeholder normalization** (#67): normative placeholder text for Record-Hash field in preimages
- **UTC timestamp requirement** (#72): Timestamp-Local MUST use UTC time source
- Versioning policy added

### Tooling
- **`mcap` CLI tool** (#6): 7 subcommands — hash-content, hash-record, sign, finalize, verify, stamp
- Python 3 stdlib only, zero external dependencies
- 53 tests including golden file verification against record-001 and record-002
- `ratification/GUIDE.md` implementation guide (#73)

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
