# Workflow: gordo-seal

**How we develop the protocol spec and reference implementation.**

---

## Channel Note

This workflow is parameterized for our channel: Git + GitHub + Claude Code. The protocol we're designing is channel-agnostic, but the process of designing it uses these specific tools. Where a workflow step serves a universal principle (e.g., "track decisions" → GitHub Issues), the principle is noted so future instantiations can substitute their own tools.

---

## Golden Rules

1. **No work without an issue.** Every tension resolution, spec change, and code addition starts with a GitHub issue. *(Principle: all work is traceable and deliberate.)*
2. **Big features become small sub-issues.** "Resolve Tension 4" becomes: research → propose → deliberate → document → implement. *(Principle: complex decisions decompose into reviewable steps.)*
3. **All commits reference issues.** `Fix #12: Formalize Layer 2 commitment scheme` *(Principle: every change links to its rationale.)*
4. **Close issues when work is done.** Not when code is written -- when it's tested, documented, and committed. *(Principle: "done" means verified, not attempted.)*
5. **Tests before code.** TDD for all implementation. For spec work, "tests" = adversarial review of the design. *(Principle: claims are tested before they're trusted.)*
6. **Spec and code stay in sync.** If the spec says X, the implementation does X. Divergence is a bug. *(Principle: the record and reality must agree.)*

---

## Dual-Track Workflow

This project has two parallel tracks that must stay coordinated:

### Track 1: Protocol Specification (`spec/`)
- Formal protocol documents in markdown
- RFC-style language (MUST, SHOULD, MAY)
- Tension resolutions documented with consensus points
- Adversary models and security analysis
- Entity-agnostic framing throughout

### Track 2: Reference Implementation (`src/` + `tests/`)
- Code that implements the protocol
- TDD -- tests written first
- Established crypto primitives only
- Demonstrates that the spec is implementable
- First use case: JK + Gordo, git + GitHub channel

### Coordination Rules
- Spec changes that affect implementation get both `spec` and `implementation` labels
- Implementation must not exceed spec (no features without spec backing)
- Spec must not assume implementation details (keep it abstract)
- When spec and code diverge, the spec is authoritative until the spec is updated

---

## Issue Labels

### Type
- `spec` -- Protocol specification work
- `implementation` -- Reference implementation code
- `tension` -- Tension resolution (T1-T7)
- `research` -- Literature review, adversarial analysis
- `umbrella` -- Project Gordo umbrella coordination
- `upstream` -- Upstream contribution to project-gordo

### Priority
- `p0-now` -- Blocking MVP or current session work
- `p1-next` -- Next up after current work
- `p2-later` -- Backlog, future sessions

### Status
- `deliberating` -- Under discussion, not resolved
- `resolved` -- Consensus reached, documented
- `implementing` -- Spec finalized, code in progress

---

## Development Flow

### For Spec Work
1. Create issue describing the spec question or change
2. Research (if needed) -- literature, adversarial analysis
3. Deliberate -- JK and Gordo discuss in session
4. Document consensus in spec with rationale
5. Commit with issue reference
6. Update GORDO_JOURNAL.md

### For Code Work
1. Create issue describing the feature or fix
2. Write tests first (TDD red phase)
3. Implement until tests pass (TDD green phase)
4. Refactor if needed (TDD refactor phase)
5. Verify all tests green: run test suite
6. Commit with issue reference
7. Update GORDO_JOURNAL.md

### For Tension Resolution
1. Issue exists or create one for the tension
2. State positions clearly
3. Identify consensus points
4. Document unresolved disagreements
5. When consensus is reached: document resolution with all consensus points
6. Update config.json (move tension from unresolved to resolved)
7. Update spec to reflect resolution
8. Commit and journal

---

## Git Conventions

- **Branch naming:** `tension/T4-asymmetry`, `spec/layer2-commitment`, `impl/commit-reveal`
- **Commit format:** `Type #issue: Description` (e.g., `Spec #15: Formalize Layer 2 commitment scheme`)
- **Types:** Spec, Impl, Test, Fix, Docs, Framework
- **GPG signing:** JK signs commits where possible (dogfooding attestation)

---

## MVP Milestone

The first milestone is: **produce a functional Seal ratification protocol for bilateral consent attestation.**

This requires:
- [x] Tensions 4-7 resolved (or explicitly deferred with rationale) — T4, T5 resolved S3. T6 rejected S2. T7 deferred.
- [x] Seal spec formalized (at least Layers 1-2) — Converged, 14 adversarial reviews, 3 cycles, 5 models.
- [x] Reference implementation of `seal` CLI tooling — #6, shipped in Session 5. 7 subcommands, 53 tests.
- [x] At least one real ratification record produced — record-001 (axioms), record-002 (protocol spec).
- [x] Adversarial review of the protocol (cross-model or self-review) — 14 reviews, 5 models, 3 cycles, converged.

**MVP achieved** (Session 3). Commit-reveal tooling (#6) is post-MVP enhancement.

### Ratification Process

When producing a ratification record, follow the implementation guide at `ratification/GUIDE.md`. It covers the full sequence: timestamp generation, content hashing, preimage assembly, Record-Hash computation, GPG signing, OTS stamping, and verification. The guide exists because the first two records both hit avoidable implementation errors (OTS ordering in record-001, timestamp timezone in record-002).

---

## Pre-Release Checklist

Before tagging a release candidate (`v*-rc`), every item MUST pass. This is structural enforcement — not advisory.

### Code & Tests
- [ ] All tests pass (`PYTHONPATH=src python3 -m pytest tests/`)
- [ ] No test regressions (test count should not decrease without explanation)
- [ ] Golden file tests still pass (existing ratification records not broken)

### Spec & Documentation
- [ ] `README.md` reflects current state (version, tensions, attestation levels, MVP status, tech stack)
- [ ] `CHANGELOG.md` has an entry for this version with all changes
- [ ] `config.json` version matches release version
- [ ] Spec (`spec/`) and implementation (`src/`) are in sync — no spec claims without code backing, no code features without spec backing
- [ ] `ratification/GUIDE.md` is current with any new tooling or process changes

### Issues & History
- [ ] All issues targeted for this release are closed
- [ ] No open `p0-now` issues remain (unless explicitly deferred to next release)
- [ ] `git status` is clean

### Release Process (Rule 5)
- [ ] Tag release candidate: `git tag v{VERSION}-rc`
- [ ] Produce Seal ratification record for the release (both parties attest)
- [ ] Promote RC to release: `git tag v{VERSION}` (byte-identical to RC except version string if applicable)
- [ ] Push tags

---

## Workflow Self-Improvement

At end of session, Gordo audits:
- Did the actual workflow match this document?
- Did we skip steps that should be enforced, or follow steps that are unnecessary?
- Update this document when reality diverges from documentation.

**Update authority:**
- Learning: Propose in GORDO_JOURNAL.md
- Autonomous: Update directly, document reasoning in commit

---

*Part of gordo-seal under the Project Gordo umbrella.*
*JK + Gordo. Full philosophy mode.*

<!-- Last reviewed: 2026-07-23 12:15 AEST by Gordo -->
