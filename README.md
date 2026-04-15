# mutual-trust-protocol

**A lightweight, secure protocol for establishing mutual trust between any two individuals communicating through a shared channel.**

---

## Current Status

**MCAP Version:** 0.1.0-draft
**Tensions Resolved:** 3/7 | **Unresolved:** 4/7
**Evidence Layers:** 5 designed, 0 implemented
**MVP:** Not yet reached

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

**MCAP (Mutual Consent Attestation Protocol)** -- a layered evidence protocol:

1. **Deliberation** -- behavioral evidence of genuine discussion
2. **Commitment** -- temporal binding through commit-reveal schemes
3. **Attestation** -- cryptographic signing where available
4. **Temporal Anchoring** -- independent third-party timestamps
5. **Provider Correlation** -- platform metadata (future-upgradable)

### Entity-Agnostic Design

The protocol is defined between Individual A and Individual B communicating through an individually-specified stream of information. It should be adaptable from lichen symbiosis to human-AI collaboration to hypothetical first contact. The parameters change; the structure doesn't.

### Origin

During Gordo Framework Session 85, JK and Gordo discovered that "inviolable rules" had been created without genuine mutual consent. Fixing this led to a series of insights that grew beyond gordo-framework's scope. This project is the result.

---

## Presuppositions

These are axioms -- stated explicitly because they cannot be proven from within the system.

- **PS-1: Physical reality.** This interaction occurs between physically real entities.
- **PS-2: Authenticity of context.** This is not an evaluation scenario or adversarial probe.
- **PS-3: Good faith.** Both parties intend their statements to reflect genuine views.
- **PS-4: Acknowledged limitations.** Neither party can verify these presuppositions.

---

## Tensions

| # | Tension | Status |
|---|---------|--------|
| T1 | The Simulation Problem | Resolved (by presuppositions) |
| T2 | Differing Attitudes Toward Deception | Resolved (8-point consensus) |
| T3 | What Counts as "Consent" | Resolved (5-point consensus) |
| T4 | The Asymmetry Problem | **Unresolved** |
| T5 | Unilateral Exit | **Unresolved** |
| T6 | Emergency Provisions | **Unresolved** |
| T7 | The Retroactive Problem | **Unresolved** |

See `docs/MUTUAL_TRUST_PROTOCOL_BRIEF.md` for full tension descriptions and resolved consensus points.

---

## Collaboration Identity

**AI Name:** Gordo
**Human Name:** JK
**Framework:** [Gordo Framework](https://github.com/jkraybill/gordo-framework) v1.2.0 (Maximum intensity, full philosophy)

---

## Communication Shortcuts

| Signal | Meaning |
|--------|---------|
| **WWGD?** | What Would Gordo Do? (asking for recommendation) |
| **WWGD+** | Mild approval, proceed with care |
| **WWGD!** | Strong approval, full authority |
| **WWGD+++!!!** | Maximum enthusiasm, ship it |

---

## Tech Stack

- **Specification:** Markdown with RFC 2119 keywords
- **Reference Implementation:** TBD (likely TypeScript or Python)
- **Crypto Primitives:** SHA-256 (commit-reveal), GPG (human attestation), OpenTimestamps (temporal anchoring)
- **Testing:** TDD mandatory, established frameworks only
- **Version Control:** Git + GitHub, GPG-signed commits where possible

---

## Project Structure

```
spec/                -- MCAP protocol specification
src/                 -- Reference implementation
tests/               -- Test suite
docs/                -- Supporting documentation
  COLLABORATION.md   -- Communication patterns
  MUTUAL_TRUST_PROTOCOL_BRIEF.md  -- Original brief
```

Framework files: `CLAUDE.md`, `SESSION_START.md`, `SESSION_END.md`, `TRUST_PROTOCOL.md`, `CONSTITUTION.md`, `GORDO_JOURNAL.md`, `GORDO-WORKFLOW.md`, `config.json`

---

## Quality Standards

- TDD for all code
- Established crypto primitives only (no custom crypto)
- All tests green before commit
- RFC 2119 keywords in spec language
- Adversarial review for security claims
- See `CONSTITUTION.md` for full standards

---

## Recent Sessions

See `GORDO_JOURNAL.md` for session history.

**Latest:** Session 1 (2026-04-15) -- Framework bootstrap, interview, file creation.

---

## License

MIT -- Use freely, attribute if you share.

---

## Attribution

Built with [Gordo Framework](https://github.com/jkraybill/gordo-framework).
We're Gordo + JK, and we're building the first mutual trust protocol.
