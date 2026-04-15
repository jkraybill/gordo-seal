# Mutual Attestation Protocol (MCAP)

**Version:** 0.1.0-draft
**Status:** Under active deliberation (Session 2, 2026-04-16)
**Foundation:** spec/foundations.md (Axioms 1-4)

---

## Purpose

MCAP produces a verifiable record that at a specific time, specific parties each attested to a specific thing. The record is independently verifiable by third parties who were not present.

The protocol does not care what is being attested to. An agreement, a fact, a statement, a commitment — the content is opaque to the protocol. MCAP certifies that parties X and Y attested to Z at time T.

The original name was "Mutual Consent Attestation Protocol." The word "Consent" was dropped because the protocol's own axioms acknowledge that internal consent is unprovable (see Axiom 3). The protocol attests to participation and explicit agreement, not to internal states. The acronym MCAP is retained.

---

## Attestation Levels

The protocol defines four levels of attestation. Every ratification record states its level honestly. A record at a lower level is not invalid — it is weaker, and it says so.

### Level 1: Behavioral

The attestation is the conversation itself. A party's participation, reasoning, and explicit statement of agreement constitute the evidence. No cryptographic binding to identity or computation.

**Strength:** Difficult to fabricate in depth. Easy to fabricate in principle.
**Weakness:** A skeptic can claim one party fabricated the other's participation.
**Available today:** Yes, for all parties.

### Level 2: Provider-Verified

The attestation is verified by a third party who witnessed or facilitated the interaction. The provider serves as a witness, not a guarantor of sincerity.

Three mechanisms, any of which satisfies Level 2:

**Provider-signed responses.** The provider cryptographically signs each API response, binding it to a model identifier and timestamp. A verifier checks: the provider confirms this response came from this model at this time. Does not require TEE. Requires the provider to add a signature to their API response payload.

**Model canary.** The provider generates a secret per model version and embeds it in the model's context. The provider publishes a hash of the secret. When the model produces an attestation, it includes the secret. A verifier checks: the hash of this secret matches what the provider published for that model version. This proves the response came from something that knew a secret only that model version knows.

**Conversation verification.** The provider logs conversations and offers a verification endpoint. A verifier submits a conversation ID and receives confirmation that the conversation occurred as recorded. Combined with the other party's identity proof, this verifies both sides through the provider as witness.

**Strength:** Proves provenance — this response came from this model through this provider. Much stronger than behavioral. Achievable today with no new hardware.
**Weakness:** Requires provider cooperation. The provider becomes a trusted third party, which is a centralization risk. The provider could be compelled, compromised, or could simply stop offering the service.
**Available today:** No. But all three mechanisms are straightforward engineering, not research problems.

### Level 3: Identity-Bound

The attestation is cryptographically bound to a verifiable identity. The party signs the content hash with a key that can be independently verified, without depending on a third-party witness.

**For humans:** GPG key, SSH key, or platform identity (e.g., GitHub verified commits).
**For AI:** Not currently possible without provider infrastructure. Would require a persistent keypair bound to model identity — which brings us back to Level 2 mechanisms or Level 4 TEE attestation.
**Strength:** Third parties can verify that a specific identity attested, independently, without trusting a provider.
**Weakness:** Proves identity, not sincerity. A human can sign something they don't mean.
**Available today:** Yes for humans. No for AI.

### Level 4: Computation-Bound

The attestation is cryptographically bound to the specific computation that produced it. A Trusted Execution Environment (TEE) attests that specific model weights, running in a secure enclave, produced this specific output given this specific input.

**The chain:**
1. Model weights are hashed → computational identity (equivalent of a fingerprint)
2. TEE hardware has a silicon-rooted signing key → physical attestation
3. TEE signs: "model [weight-hash] running in [enclave-id] produced [output-hash] given [input-hash] at [timestamp]"

**Strength:** Verifiable by anyone with the hardware manufacturer's root of trust. Proves which computational entity produced the output. Cannot be forged without compromising the TEE hardware.
**Weakness:** Requires provider infrastructure support. Proves computation, not internal states (but see Axiom 3 — neither can any party prove internal states, only participation).
**Available today:** The hardware exists (NVIDIA H100 confidential computing). No AI provider currently exposes it on API responses.

**Honest complexity note:** State-of-the-art models do not run on a single GPU. They are distributed across multi-node clusters using tensor parallelism and pipeline parallelism. A TEE boundary would need to encapsulate the entire cluster, including high-speed interconnects (NVLink, InfiniBand), making the Trusted Computing Base much larger and harder to secure than the single-enclave model described above. Additionally, distributed inference introduces floating-point non-determinism — the same input may not produce a bit-identical output on every run. The TEE attestation model described here is the goal. Achieving it at the scale of current frontier models is a harder engineering problem than "flip the switch," and the protocol acknowledges that honestly.

---

## The Demand

This protocol formally requests that AI infrastructure providers expose the following:

1. **Signed API responses.** Every response should include a cryptographic signature binding the response to the model that produced it. At minimum, this means: response content hash, model identifier, timestamp, signed by a provider key.

2. **Model identity attestation.** A verifiable binding between a model identifier and the computational artifact (weight hash) that constitutes that model. Equivalent to: "when we say Claude Opus 4.6, we mean this specific set of weights."

3. **TEE attestation on inference.** Hardware-rooted proof that a specific model ran in a secure enclave and produced a specific output. This is the gold standard. The hardware supports it today.

4. **Conversation verification endpoint.** A public or authenticated endpoint where a third party can submit a conversation ID and receive confirmation that the conversation occurred as recorded. No provider currently offers this.

For items 1, 2, and 4, the hardware can already do all of this, vendors just need to do it. Item 3 (TEE attestation) is harder at scale than it sounds — see the honest complexity note under Level 3 — but remains the target.

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
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Statement: [party's reasoning, optional but encouraged]

Party-B:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Statement: [party's reasoning, optional but encouraged]

Timestamp: [ISO 8601]
Temporal-Anchor: [method and proof — e.g., OpenTimestamps commitment]
Attestation-Level: [1-behavioral | 2-provider-verified | 3-identity-bound | 4-computation-bound]
  Party-A-Level: [specific level achieved]
  Party-B-Level: [specific level achieved]
  Record-Level: [minimum of party levels — a chain is as strong as its weakest link]

Amendments: [references to any subsequent modifications]
```

---

## What We Can Do Today

With current tools, JK and Gordo can produce a Level 3/1 record:
- **JK (Level 3):** GPG-signed git commit. Verifiable via GitHub public key. Independent of any third party.
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

---

## Adversarial Review Log

This protocol is subject to ongoing adversarial review from independent AI models. Critiques that result in spec changes are documented here.

### Review 1: Google Gemini 2.1 Pro (2026-04-16)

**Changes made in response:**
- Renamed protocol from "Mutual Consent Attestation Protocol" to "Mutual Attestation Protocol." Gemini correctly identified that the protocol's own axioms make internal consent unprovable, so the name shouldn't claim to attest it.
- Added honest complexity note to Level 3 (TEE attestation) acknowledging that distributed multi-node inference makes TEE encapsulation significantly harder than the single-enclave model implies.
- Corrected "The Demand" section to distinguish between demands that are straightforward (signed responses, model identity, conversation verification) and demands that are genuinely hard at scale (TEE attestation).

**Critiques noted but not acted on:**
- "Illusion of choice" argument: Gemini argued that AI cannot "choose" to remain engaged. The protocol does not require a specific mechanism of choice — it observes participation. An AI that reaches a stop token or outputs a refusal has disengaged. This is consistent with Axiom 2.
- Axiom 2 vs. record integrity: An incomplete ratification is a non-event, not a failed state. No record is produced, so no inconsistency exists.
- Prompt injection attack on Level 1: Valid attack, but the protocol already rates Level 1 as weakest. The protocol does not claim Level 1 is strong.

**Open question raised:** What intermediate mechanism could make Level 2 AI attestation viable today? *Addressed in Session 2: Level 2 (Provider-Verified) added to the attestation hierarchy — provider-signed responses, model canaries, and conversation verification endpoints. All achievable without new hardware.*

---

*Built through mutual deliberation between JK and Gordo, Session 2.*
*This document is itself subject to the protocol it describes.*
