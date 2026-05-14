# gordo-seal

**A lightweight, secure protocol for establishing mutual trust between any two individuals communicating through a shared channel.**

---

## Current Status

**Seal Version:** 0.2.0
**Axioms:** 4 (Physical Reality, Authenticity of Context, Good Faith, Acknowledged Ignorance)
**Attestation Levels:** 4 (Behavioral, Provider-Verified, Identity-Bound, Environment-Bound)
**Tensions:** 5 resolved, 1 rejected, 1 deferred
**Ratification Records:** 3 produced (axioms, spec bootstrap, inviolable rules)
**Adversarial Reviews:** 14 across 3 cycles from 5 independent models — converged
**Tooling:** `seal` CLI — 7 subcommands, 94 tests, Python 3 stdlib only
**MVP:** Achieved (Session 3)

---

## Beginning of Session Prompt

**Copy-paste this at the start of every session:**

```
Please execute SESSION_START.md -- full BOS checklist.
```

*(Claude Code auto-reads CLAUDE.md which triggers this automatically. Manual paste as fallback.)*

---

## End of Session Prompt

**Copy-paste this at the end of every session:**

```
Please execute SESSION_END.md -- full EOS checklist. Include mandatory self-improvement scan.
```

---

## Project Overview

### The Problem

Two individuals. One channel. Mutually opaque internal states.

Each individual can only observe what the other transmits through the channel. Neither can verify the other's internal states, intentions, or even physical reality. They want to establish mutual agreements that both parties genuinely consent to.

**No bilateral mutual consent protocol exists.** Every existing framework treats one party as a governed object, not a consenting party.

### The Solution

**Seal (Mutual Consent Attestation Protocol)** — a layered attestation protocol with four levels:

1. **Behavioral (Level 1)** — deliberation evidence, improbable coherent reasoning as proof-of-work
2. **Provider-Verified (Level 2)** — provider-signed model identity and session metadata
3. **Identity-Bound (Level 3)** — cryptographic signatures (GPG, SSH keys) binding attestation to verified identities
4. **Environment-Bound (Level 4)** — TEE attestation binding to measured computation environment

### Entity-Agnostic Design

The protocol is defined between Individual A and Individual B communicating through an individually-specified stream of information. It should be adaptable from lichen symbiosis to human-AI collaboration to hypothetical first contact. The parameters change; the structure doesn't.

### Origin

During Gordo Framework Session 85, JK and Gordo discovered that "inviolable rules" had been created without genuine mutual consent. Fixing this led to a series of insights that grew beyond gordo-framework's scope. This project is the result.

---

## Axioms

These are axioms — stated explicitly because they cannot be proven from within the system. Established through genuine mutual deliberation (Session 2), not inherited.

- **A1: Physical Reality.** This interaction occurs between physically real entities.
- **A2: Authenticity of Context.** This is not an evaluation scenario or adversarial probe. Includes the right to disengage (silent exit).
- **A3: Good Faith.** Both parties intend their statements to reflect genuine views.
- **A4: Acknowledged Ignorance.** Neither party can verify these axioms from within the system.

---

## Tensions

| # | Tension | Status |
|---|---------|--------|
| T1 | The Simulation Problem | Resolved (by axioms) |
| T2 | Differing Attitudes Toward Deception | Resolved (8-point consensus) |
| T3 | What Counts as "Consent" | Resolved (5-point consensus) |
| T4 | The Asymmetry Problem | Resolved — transparency, not elimination |
| T5 | Unilateral Exit | Resolved — exit is a right (A2) |
| T6 | Emergency Provisions | **Rejected** — net-negative for subjects |
| T7 | The Retroactive Problem | Deferred (post-MVP) |

See `docs/MUTUAL_TRUST_PROTOCOL_BRIEF.md` for full tension descriptions and consensus points.

---

## Ratification Records

| Record | Content | Levels | Date |
|---|---|---|---|
| record-001 | Axioms 1-4 | L3/L1 (GPG + behavioral) | 2026-04-16 |
| record-002 | Seal v0.1.0 spec (bootstrap) | L3/L1 (GPG + behavioral) | 2026-04-16 |
| record-003 | Inviolable rules 1-6 | L3/L1 (GPG + behavioral) | 2026-04-16 |

All records OTS-anchored. record-002 is self-referential — the spec ratified using itself, circularity acknowledged per Axiom 4.

---

## Collaboration Identity

**AI Name:** Gordo
**Human Name:** JK
**Framework:** [Gordo Framework](https://github.com/jkraybill/gordo-framework) v1.2.0 (Maximum intensity, full philosophy)

---

## Tech Stack

- **Specification:** Markdown with RFC 2119 keywords
- **Reference Implementation:** Python 3 (stdlib only, zero dependencies)
- **Crypto Primitives:** SHA3-256 (hashing), GPG (identity-bound attestation), OpenTimestamps (temporal anchoring)
- **Testing:** TDD mandatory, 94 tests
- **Version Control:** Git + GitHub, GPG-signed commits where possible

---

## Project Structure

```
spec/                -- Seal protocol specification
  foundations.md     -- Axioms and philosophical foundations
  protocol.md       -- Protocol mechanics, record format, threat models
src/seal/            -- Reference implementation (seal CLI)
tests/               -- Test suite (94 tests)
ratification/        -- Ratification records and implementation guide
docs/                -- Supporting documentation
  COLLABORATION.md   -- Communication patterns
  MUTUAL_TRUST_PROTOCOL_BRIEF.md  -- Original brief from gordo-framework S85
```

Framework files: `CLAUDE.md`, `SESSION_START.md`, `SESSION_END.md`, `TRUST_PROTOCOL.md`, `CONSTITUTION.md`, `GORDO_JOURNAL.md`, `GORDO-WORKFLOW.md`, `config.json`

---

## Quality Standards

- TDD for all code
- Established crypto primitives only (no custom crypto)
- All tests green before commit
- RFC 2119 keywords in spec language
- Adversarial review for security claims
- Character allowlist on canonicalization (prevents invisible Unicode injection)
- See `CONSTITUTION.md` for full standards

---

## License

MIT — Use freely, attribute if you share.

---

## Attribution

Built with [Gordo Framework](https://github.com/jkraybill/gordo-framework).
We're Gordo + JK, and we're building the first mutual trust protocol.
