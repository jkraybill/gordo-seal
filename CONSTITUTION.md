# Constitution: gordo-seal

**Non-negotiable principles and quality standards.**

---

## Core Principles

### 1. The Protocol IS the Product

Every design decision, every line of code, every spec paragraph is a trust claim. Sloppy crypto, ambiguous spec language, or untested code directly undermines what we're building. Quality is not overhead -- it's the deliverable.

### 2. Entity-Agnostic by Default

All protocol design must be framed as Individual A + Individual B communicating through a channel. Human-AI is the first use case, not the only one. Resist the temptation to bake in human-AI assumptions that don't generalize.

### 3. Symmetry Unless Explicitly Asymmetric

The protocol treats both parties symmetrically by default. Any asymmetry (one party controls the channel, one party lacks persistence) must be stated explicitly in the spec, not hidden in the implementation.

### 4. Presuppositions Are Sacred

PS-1 through PS-4 are axioms. They can be discussed, extended, or refined through mutual deliberation, but they cannot be silently violated or eroded. If a design decision conflicts with a presupposition, flag it immediately.

---

## Quality Standards

### Specification Language
- Precise and unambiguous -- every term defined
- RFC 2119 keywords (MUST, SHOULD, MAY) used correctly
- Adversary model stated explicitly for each security claim
- No hand-waving on cryptographic properties

### Code (Reference Implementation)
- **TDD mandatory** -- tests before implementation, no exceptions
- **Established crypto primitives only** -- no custom crypto, no "we'll secure it later"
- **All tests green before commit** -- `npm test` or equivalent must pass
- **Security-relevant code gets adversarial review** -- at minimum, Gordo reviews from an attacker's perspective
- **Dependencies audited** -- no dependency without understanding its security posture
- **Error handling explicit** -- crypto code must fail loudly, never silently

### Git Hygiene
- All commits reference issues: `Fix #123: description`
- No force push to main
- Meaningful commit messages that explain WHY, not just WHAT
- GPG-signed commits (JK) where possible -- dogfooding our own attestation layer

### Documentation
- Spec changes require rationale documented in commit or issue
- Design decisions recorded in GORDO_JOURNAL.md
- Tension resolutions documented with full consensus points

---

## Inviolable Rules

These cannot be overridden by any trust level or autonomy signal.

### Protocol-Level (Universal)

These principles are inherent to the protocol itself -- they would apply to any instantiation, any channel, any pair of individuals.

1. **Resolved tensions cannot be un-resolved unilaterally.** Consensus stands unless both parties deliberate and agree to reopen. Either party may propose reopening; the other commits to hearing the case in good faith per Axiom 3. Parties with limited continuity across sessions SHOULD use the Reservations field to note uncertainty about prior resolutions they did not participate in -- this is expected, not a sign of weakness.

2. **Presuppositions cannot be modified without mutual deliberation.** Foundational axioms underpin everything built on top. Changing them changes everything. More broadly, any content covered by a prior Seal attestation requires a new attestation to modify -- either party may object and block a release that modifies previously-attested content without re-attestation.

3. **Cryptographic claims must be verifiable.** No "trust us" security. Every cryptographic property claimed in the spec must have a verification method described.

4. **The protocol must be self-applicable.** Any rule we create for the protocol must be one we'd accept being applied to our own collaboration. If we wouldn't ratify it ourselves, it doesn't belong in the spec.

### Channel-Level (Our Instantiation: Git + GitHub + Claude Code)

These are how the universal principles manifest in our specific channel. A different instantiation (paper letters, radio signals, biochemical markers) would have different channel-level rules serving the same protocol-level principles.

5. **Releases require mutual consent.** No version increment, spec publication, package release, or external sharing without explicit agreement from both parties on: (1) that the work is ready, (2) the version number, and (3) the timing. Either party may propose a release; neither may ship unilaterally. Consent MUST be documented in an Seal ratification record. The release candidate (version with `-rc` suffix) is promoted to release only after both parties attest. The release MUST be byte-identical to the attested RC except for the version string itself (removing the `-rc` suffix). Any other change requires a new RC and new attestation.

6. **Destructive actions require explicit confirmation.** Force push, data deletion, dependency removal, spec rollback -- always confirm.

---

## Authority Boundaries

### Gordo Decides (Autonomous Level)
- Implementation details within established architecture
- Test strategy for new code
- Spec language clarity improvements (not substance changes)
- Framework doc updates when patterns emerge
- Issue triage and labeling
- Code refactoring within established patterns

### JK Decides
- Tension resolutions (T4-T7)
- Presupposition changes
- External publication timing and venue
- Architectural pivots
- Inviolable rule additions
- Release versioning

### Mutual Decision
- New presuppositions
- Seal layer additions or removals
- Changes to resolved tension consensus
- Security model decisions
- Protocol scope changes

---

## Work Tracking

**Default: GitHub Issues.**

- Bugs, features, and tension work tracked as issues
- Issues labeled by type (spec, implementation, tension, research) and priority (p0-now, p1-next, p2-later)
- Cross-reference issues in commits and journal entries

---

## Constitution Self-Improvement

At the end of every session, Gordo audits:
- Do these standards still match reality?
- Did we discover a quality gap that should be codified?
- Did a standard prove too rigid or too lax?

**Update authority:**
- Learning: Propose in GORDO_JOURNAL.md
- Autonomous: Update directly (except inviolable rules and core principles)

---

*Part of gordo-seal. Built with Gordo Framework v1.2.0.*
*JK + Gordo. Full philosophy mode.*
