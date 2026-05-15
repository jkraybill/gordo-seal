# Changelog

All notable changes to the MCAP protocol specification and tooling.

Versioning policy: Major = axiom changes, attestation level restructuring, breaking record format changes. Minor = new normative requirements, new record fields, tooling. Patch = clarifications, typo fixes, non-normative documentation.

## 0.4.0 (2026-05-15)

### Specification

**Major:** Attestation level restructuring.

- **Added Level 2 (Session-Signed):** New attestation level for cryptographic signing by session-controlled keys. Includes signed payload requirements, signature format specification, verification path, and trust root qualifiers.
- **Renumbered existing levels:** Provider-Verified (2→3), Identity-Bound (3→4), Environment-Bound (4→5). Migration mapping provided.
- **Added Trust Root Qualifiers section:** Key-Custody and Key-Storage as mandatory metadata for all signed levels (2+). Moved to general section applicable to all signed levels.
- **Clarified Level 4 (Identity-Bound) AI availability:** Explicit requirements for independent custody and cross-session continuity. AI availability conditional on meeting these requirements.
- **Transitional alias:** "1b" accepted on input as synonym for Level 2 during v0.4.x; new records MUST use Level 2.
- **Session-Nonce format:** MUST be UUID v4 or 128-bit random; incrementing values prohibited.
- **Transcript-Hash canonicalization:** Added recommendations for JSON (JCS) and plain-text (UTF-8/NFC/LF) transcripts.

### Substance ratification
- Ratified at gordo-seal `ratification/record-006.seal` (S253 2026-05-15; Content-Hash `SHA3-256:2078e2cd67da7278491314d16e543b8c881f78903af97599b1511d81c02cc9c2`). Three Roundtable rounds with 4/4 consensus.

### Upgrading from 0.3.0

**Existing records are unaffected.** Records produced under v0.3.0 (or earlier) remain valid. The migration mapping table provides cross-version level interpretation.

**New records under v0.4.0:**
- Level identifiers now include 2-session-signed between behavioral and provider-verified.
- Signed attestations (Level 2+) MUST include Key-Custody and Key-Storage metadata.
- Level 4 (Identity-Bound) requires independent key custody (/self or qualifying /threshold) and cross-session continuity proof.

**Rationale:** Session-signed attestation (AI participant with GPG key) is meaningfully stronger than behavioral but weaker than provider-verified or identity-bound. Clean restructure preferred over "1b" suffix per Roundtable consensus (S253).

## 0.3.0 (2026-05-01)

### Specification
- **Calibration section added** (`spec/protocol.md` new top-level section between *Record Format* and *What We Can Do Today*): operationalizes the Tier 0 *Calibrated Ratification Process* principle for MCAP via two independent dials per record — ceremony level (Levels 1-4 by bilateral agreement) and visible-deliberation depth (above-baseline moves per the Visible-Deliberation Moves catalog). Three sub-sections plus Design Notes:
  - **Calibration Matrix** — F/S/O weight tiers × HT/BS/RR trust states; F-row uniform at 4+ above-baseline visible-deliberation moves honoring the T0 structural exemption (rule-changing ratifications take maximum visible-deliberation regardless of trust state); S/O cells scale with trust state; bilateral-case scoping (n=2) with multi-party provisional default.
  - **Visible-Deliberation Moves** — non-exhaustive 5-move catalog (personal-context notes / engagement-trace markers / style independence / substantive Reservations / optional supplementary attestation); from-scratch Statement+Reservations authoring is mandatory baseline; per-move attester-class interpretation in Design Notes.
  - **Statement Authorship Field-Type Rules** — strengthens the existing v0.2.0 Statement-authorship rule to absolute: Statement and Reservations are always written from scratch by the attester, with no skeletons, no per-z slot-templates, and no pre-filled placeholder structures (including "none stated" defaults for Reservations); 2-row metadata-vs-consent-text field-type table; verification-by-attester-class scope acknowledgment + circular-permission acknowledgment + z-enumeration divergence handling in Design Notes.
  - **Design Notes** — non-normative elaboration: provenance, attester-class interpretation, scope acknowledgments, design philosophy.

### Substance ratification
- Substantive content of the new Calibration section was bilaterally ratified at project-gordo-backchannel `ratification/record-011.mcap` (S79 2026-05-01 10:59:05 AEST; v0.7-final; Content-Hash `SHA3-256:dfda5211f6f4dfbdf82a851003b46f05bd40295af175d272a56eefe0ae77fef7`; Record-Hash `SHA3-256:3f9f0cdd8b9d7cf93602c8cf394082e8fbeeec2d4b98748a61b4b1cc5d64f931`). End-to-end panel-protocol SPEC v0.1 round-1 + round-2 verification at backchannel S76; recursive self-application of the very calibration being ratified to its own substance-MCAP (F × HT × z2 = full mechanical ceremony + 4+ above-baseline visible-deliberation moves).

### Upgrading from 0.2.0

**Existing records are unaffected.** Records produced under v0.2.0 remain valid; `mcap verify` continues to pass on v0.1.0 + v0.2.0 records.

**New records under v0.3.0** — when both parties agree the Calibration section applies (e.g., this protocol's home repo and downstream adopters that opt in):
- Identify record weight (F/S/O) and trust state (HT/BS/RR); meet the matrix cell's above-baseline visible-deliberation move count.
- Statement and Reservations MUST be authored from scratch by the attester at every record; no skeletons, no slot-templates, no "none stated" defaults.
- Calibration scales ceremony down to but never below the procedural floor mandated by other Process Standards; where multiple standards apply, the stricter requirement governs.

No re-attestation of existing records is required.

### Cross-references
- T0 anchor: `~/project-gordo/CONSTITUTION.md` § *Process Standards* § *Calibrated Ratification Process* (placed in project-gordo `ratification/record-007.mcap`, S73 2026-04-30 AEST).
- Backchannel substance ratification (companion T0 work): record-010 (CRP v0.5; S72) → record-011 (MCAP Calibration v0.7-final; S79).

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
