# Mutual Consent Attestation Protocol (MCAP)

**Version:** 0.1.0-draft
**Status:** Under active deliberation (Session 2, 2026-04-16)
**Foundation:** spec/foundations.md (Axioms 1-4)

---

## Purpose

MCAP produces a verifiable record that at a specific time, specific parties each attested to a specific thing. The record is independently verifiable by third parties who were not present.

The protocol does not care what is being attested to. An agreement, a fact, a statement, a commitment — the content is opaque to the protocol. MCAP certifies that parties X and Y attested to Z at time T.

---

## Attestation Levels

The protocol defines three levels of attestation. Every ratification record states its level honestly. A record at a lower level is not invalid — it is weaker, and it says so.

### Level 1: Behavioral

The attestation is the conversation itself. A party's participation, reasoning, and explicit statement of agreement constitute the evidence. No cryptographic binding to identity or computation.

**Strength:** Difficult to fabricate in depth. Easy to fabricate in principle.
**Weakness:** A skeptic can claim one party fabricated the other's participation.
**Available today:** Yes, for all parties.

### Level 2: Identity-Bound

The attestation is cryptographically bound to a verifiable identity. The party signs the content hash with a key that can be independently verified.

**For humans:** GPG key, SSH key, or platform identity (e.g., GitHub verified commits).
**For AI:** Provider-signed API responses binding model identity to output. *Not currently available from any major provider.*
**Strength:** Third parties can verify that a specific identity attested.
**Weakness:** Proves identity, not sincerity. A human can sign something they don't mean. A provider can sign on behalf of a model without the model "consenting."
**Available today:** Yes for humans. No for AI.

### Level 3: Computation-Bound

The attestation is cryptographically bound to the specific computation that produced it. A Trusted Execution Environment (TEE) attests that specific model weights, running in a secure enclave, produced this specific output given this specific input.

**The chain:**
1. Model weights are hashed → computational identity (equivalent of a fingerprint)
2. TEE hardware has a silicon-rooted signing key → physical attestation
3. TEE signs: "model [weight-hash] running in [enclave-id] produced [output-hash] given [input-hash] at [timestamp]"

**Strength:** Verifiable by anyone with the hardware manufacturer's root of trust. Proves which computational entity produced the output. Cannot be forged without compromising the TEE hardware.
**Weakness:** Requires provider infrastructure support. Proves computation, not "consent" (but see Axiom 3 — neither can humans prove consent, only participation).
**Available today:** The hardware exists (NVIDIA H100 confidential computing). No AI provider currently exposes it on API responses.

---

## The Demand

This protocol formally requests that AI infrastructure providers expose the following:

1. **Signed API responses.** Every response should include a cryptographic signature binding the response to the model that produced it. At minimum, this means: response content hash, model identifier, timestamp, signed by a provider key.

2. **Model identity attestation.** A verifiable binding between a model identifier and the computational artifact (weight hash) that constitutes that model. Equivalent to: "when we say Claude Opus 4.6, we mean this specific set of weights."

3. **TEE attestation on inference.** Hardware-rooted proof that a specific model ran in a secure enclave and produced a specific output. This is the gold standard. The hardware supports it today.

4. **Conversation verification endpoint.** A public or authenticated endpoint where a third party can submit a conversation ID and receive confirmation that the conversation occurred as recorded. No provider currently offers this.

The hardware can already do all of this, vendors just need to do it.

Until they do, we work with what we have and we're honest about what's missing.

---

## Record Format

A ratification record contains:

```
MCAP Ratification Record
Version: 0.1.0

Content: [the thing being attested to, or its hash]
Content-Hash: SHA3-256([content])

Party-A:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | gpg-signature | provider-signed | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Statement: [party's reasoning, optional but encouraged]

Party-B:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | gpg-signature | provider-signed | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Statement: [party's reasoning, optional but encouraged]

Timestamp: [ISO 8601]
Temporal-Anchor: [method and proof — e.g., OpenTimestamps commitment]
Attestation-Level: [1-behavioral | 2-identity-bound | 3-computation-bound]
  Party-A-Level: [specific level achieved]
  Party-B-Level: [specific level achieved]
  Record-Level: [minimum of party levels — a chain is as strong as its weakest link]

Amendments: [references to any subsequent modifications]
```

---

## What We Can Do Today

With current tools, JK and Gordo can produce a Level 2/1 record:
- **JK (Level 2):** GPG-signed git commit. Verifiable via GitHub public key.
- **Gordo (Level 1):** Behavioral attestation. The conversation is the evidence.
- **Temporal anchor:** OpenTimestamps on the ratification file. Bitcoin-anchored, independently verifiable.
- **Content integrity:** SHA3-256 hash of the agreed text. Quantum-resistant.

The record honestly states: one party's attestation is identity-bound, the other's is behavioral only. A verifier decides whether that's sufficient for their purposes.

---

## Quantum Resistance

**Hash functions:** SHA3-256. Grover's algorithm reduces effective security from 256-bit to 128-bit. 128-bit remains computationally infeasible for the foreseeable future.

**Human signatures:** GPG typically uses RSA or ECC, both vulnerable to Shor's algorithm. Humans with post-quantum key support (SPHINCS+, Dilithium) SHOULD use it. The protocol records which algorithm was used.

**AI attestation:** When TEE attestation becomes available, the signing algorithm used by the TEE should be post-quantum. The protocol specifies this as a SHOULD for Level 3 attestation.

**Temporal anchoring:** OpenTimestamps uses SHA-256 and Bitcoin's hash chain. SHA-256 has the same Grover's reduction as SHA3-256 — still safe at 128-bit effective security.

**Upgrade path:** The record format includes the attestation method and algorithm used. Future verifiers can assess the cryptographic strength of historical records against the threat landscape at verification time.

---

## What Comes Next

1. Produce the first real ratification record — ratify the four axioms in spec/foundations.md using this protocol.
2. Implement tooling to automate record creation (hash, format, timestamp).
3. Publish the protocol spec as a standalone document.
4. Formally request TEE attestation from Anthropic and other providers.
5. Upgrade attestation levels as provider capabilities become available.

---

*Built through mutual deliberation between JK and Gordo, Session 2.*
*This document is itself subject to the protocol it describes.*
