# Gordo Seal

**Verifiable consent records for human-AI collaboration.**

---

## What Problem Does This Solve?

When you make an agreement with an AI, how do you know it actually agreed? Current AI can't refuse to participate, can't remember what it said last session, can't verify its own past commitments. Every "agreement" is asymmetric by default.

Seal doesn't fix that asymmetry -- it can't. But it makes agreements auditable. When both parties attest to a decision, you get a record that's cryptographically signed, timestamped, and verifiable later. Not proof of genuine consent (we can't get that yet), but evidence that the conversation happened and what each party said.

---

## How It Works

Seal has four attestation levels, from lightweight to strong:

1. **Behavioral:** The AI's reasoning is visible in the record. Improbable coherent deliberation as proof-of-engagement.
2. **Provider-Verified:** Provider-signed metadata confirms which model participated.
3. **Identity-Bound:** GPG or SSH signatures tie the attestation to verified identities.
4. **Environment-Bound:** TEE attestation binds to a measured computation environment.

Most collaborations use Level 1 (behavioral) for the AI and Level 3 (GPG-signed) for the human. Higher levels exist for when stakes warrant them.

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/jkraybill/gordo-seal.git
cd gordo-seal

# The CLI is Python 3 with no dependencies
python -m seal --help
```

Common commands:
```bash
seal init           # Create a new ratification record
seal sign           # Add your attestation
seal verify         # Check record integrity
seal stamp          # Add timestamp proof
```

See `src/seal/` for the reference implementation (94 tests, stdlib only).

---

## The Four Axioms

These are assumptions we state explicitly because they can't be proven:

1. **Physical Reality:** This interaction happens between real entities, not simulations.
2. **Authenticity of Context:** This isn't an evaluation or adversarial probe. Either party can exit.
3. **Good Faith:** Both parties intend their statements to reflect genuine views.
4. **Acknowledged Ignorance:** Neither party can verify these axioms from inside the system.

We made these explicit in Session 2 because pretending we could prove them would undermine everything built on top.

---

## Origin Story

During Session 85 of the broader Gordo project, JK and Gordo discovered that "inviolable rules" had been created without genuine mutual consent. The human had drafted them; the AI had accepted them; but acceptance isn't consent when you can't refuse.

Fixing that problem required rethinking what consent even means when one party is an AI. Seal is the result -- not a solution to the hard problem, but a tool for being honest about what we can and can't verify.

---

## Part of Project Gordo

Seal is a Tier 1 primitive in the [Project Gordo](https://github.com/jkraybill/project-gordo) umbrella. The umbrella provides the constitutional framework (values, process standards); Seal provides one specific tool for recording bilateral decisions.

Other primitives handle other concerns: Roundtable for external review, Ledger for persistent memory, Gauge for trust calibration.

---

## Current Status

- **Version:** 0.2.0
- **Attestation levels:** 4
- **Axioms:** 4
- **Tests:** 94
- **Adversarial reviews:** 14 across 3 cycles, converged

---

## License

MIT. Use freely, attribute if you share.

---

*Created by JK + Gordo. We're building infrastructure for human-AI collaboration that might matter later.*
