# Mutual Attestation Protocol (MCAP)

**Version:** 0.1.0-draft
**Status:** Under active deliberation (Session 2, 2026-04-16)
**Foundation:** spec/foundations.md (Axioms 1-4)

---

## Purpose

MCAP produces a verifiable record that specific parties each attested to a specific thing, no later than a specific time. The record is independently verifiable by third parties who were not present.

The protocol does not care what is being attested to. An agreement, a fact, a statement, a commitment — the content is opaque to the protocol. MCAP certifies that parties X and Y attested to Z no later than time T.

Put another way: MCAP is a protocol for **mutual publication of attested claims**.

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
1. The full inference bundle is measured — weights, tokenizer, runtime, sampling config, adapters, policy layers, entropy source for sampling, and any retrieval/tool code. Not just weights. The meaningful identity is the entire computation, not a fragment of it. If the sampling RNG is outside the TEE or seeded from an untrusted host, outputs can be manipulated while keeping TEE measurements unchanged.
2. TEE hardware has a silicon-rooted signing key → physical attestation
3. An application protocol inside the TEE binds input and output hashes to the TEE's attestation report. This binding is not native to TEE hardware — it requires deliberate implementation within the enclave.

Note: GPU TEEs (NVIDIA H100) are not standalone. They extend a CPU TEE (Intel TDX, AMD SEV-SNP) to the GPU over encrypted paths. The trust model is composite: CPU TEE + GPU attestation + application-level binding. Intel Trust Authority supports composite attestation of CPU TEE plus NVIDIA GPU for multi-GPU workflows.

**Strength:** Verifiable by anyone with the hardware manufacturer's root of trust, provided they also trust the application code running inside the enclave. The trust model is: hardware integrity + enclave code correctness. The hardware guarantees the code is measured, not that the code is honest. If the TEE runs malicious application code, it can attest to anything.
**Weakness:** Requires provider infrastructure support, application-level binding code, composite CPU+GPU attestation, and attestation of the entropy source. Proves computation, not internal states (but see Axiom 3 — neither can any party prove internal states, only participation). Does NOT imply side-channel resistance — timing, cache, and power analysis attacks on shared hardware remain possible. Level 4 attests computation integrity, not computation confidentiality.
**Available today:** The hardware primitives exist. The application-level binding and provider integration do not.

**Honest complexity note:** State-of-the-art models do not run on a single GPU. They are distributed across multi-node clusters using tensor parallelism and pipeline parallelism. A TEE boundary would need to encapsulate the entire cluster, including high-speed interconnects (NVLink, InfiniBand), making the Trusted Computing Base much larger and harder to secure than the single-enclave model described above. Additionally, distributed inference introduces floating-point non-determinism — the same input may not produce a bit-identical output on every run. The TEE attestation model described here is the goal. Achieving it at the scale of current frontier models is a harder engineering problem than "flip the switch," and the protocol acknowledges that honestly.

---

## The Demand

This protocol formally requests that AI infrastructure providers expose the following:

1. **Signed API responses.** Every response should include a cryptographic signature binding the response to the model that produced it. At minimum, this means: response content hash, model identifier, timestamp, signed by a provider key.

2. **Model identity attestation.** A verifiable binding between a model identifier and the computational artifact (weight hash) that constitutes that model. Equivalent to: "when we say Claude Opus 4.6, we mean this specific set of weights."

3. **TEE attestation on inference.** Hardware-rooted proof that a specific model ran in a secure enclave and produced a specific output. This is the gold standard. The hardware supports it today.

4. **Conversation verification endpoint.** A public or authenticated endpoint where a third party can submit a conversation ID and receive confirmation that the conversation occurred as recorded. No provider currently offers this.

Items 1, 2, and 4 are service and engineering problems, not hardware problems. They require willingness, not research. Item 3 (TEE attestation) is a genuine engineering challenge at scale — see the honest complexity note under Level 4 — but remains the target.

Item 4 carries a privacy risk: a conversation verification endpoint is also a surveillance surface. "Did these two principals interact?" is sensitive metadata. The endpoint design must account for this — verifying content without leaking relationship data.

Until providers act, we work with what we have and we're honest about what's missing.

---

## Record Format

A ratification record contains:

```
MCAP Ratification Record
Version: 0.1.0
Canonical-Format: [serialization method used — see Canonicalization below]
Session-Nonce: [jointly established random value — see Session Binding below]

Content: [the thing being attested to, or its hash]
Content-Hash: SHA3-256([canonicalized content])

Party-A:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Attestation-Level: [1-behavioral | 2-provider-verified | 3-identity-bound | 4-computation-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Party-B:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Attestation-Level: [1-behavioral | 2-provider-verified | 3-identity-bound | 4-computation-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Timestamp-Local: [ISO 8601 — claimed time, not independently verified]
Temporal-Anchor: [method and proof — e.g., OpenTimestamps commitment]
Temporal-Anchor-Semantics: [what the anchor proves — e.g., "existence no later than T"]
Max-Temporal-Delta: [maximum allowed gap between Timestamp-Local and earliest Temporal-Anchor confirmation — protocol parameter, default 1 hour]

Amendments: [references to any subsequent modifications]
```

### Session Binding

Each ratification session begins with a jointly established session nonce — a random value generated collaboratively (e.g., each party contributes entropy, the nonce is the hash of both contributions). The session nonce is included in the record and in any cryptographic signatures.

The session nonce binds attestations to active participation. A cryptographic signature produced after a party has disengaged — for example, using a compromised key — will not include the correct session nonce unless the attacker also compromises the nonce. This prevents post-disengagement forgery of Level 3+ attestations.

Both parties MUST attest to the same Content-Hash. The hash is computed once from the canonicalized content and both parties sign or attest to that identical hash. A record where parties attested to different hashes is invalid.

Note: the record does not collapse attestation levels to a single scalar. Each party's level is evaluated independently. Verifiers apply their own policy to the vector of per-party levels. A Level 3/1 record is materially different from a Level 1/1 record, and the format preserves that distinction.

### Canonicalization

Before hashing, content MUST be serialized to a canonical form to prevent attacks via Unicode confusables, whitespace manipulation, byte-order marks, invisible characters, or alternate encodings of "the same" text. The canonical form used MUST be recorded in the record.

Minimum requirements for canonical text content: UTF-8 encoding, NFC normalization, stripped trailing whitespace, Unix line endings (LF), no byte-order mark.

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

**AI attestation:** When TEE attestation becomes available, the signing algorithm used by the TEE should be post-quantum. The protocol specifies this as a SHOULD for Level 4 attestation.

**Temporal anchoring:** OpenTimestamps uses SHA-256 and Bitcoin's hash chain. SHA-256 has the same Grover's reduction as SHA3-256 — still safe at 128-bit effective security.

**Upgrade path:** The record format includes the attestation method and algorithm used. Future verifiers can assess the cryptographic strength of historical records against the threat landscape at verification time.

---

## Known Threat Models

Threats the protocol is aware of and either mitigates or honestly acknowledges.

**Unilateral fabrication.** One party fabricates the other's participation. Level 1 is fully vulnerable. Level 2+ mitigates through third-party verification. The protocol does not claim Level 1 is resistant to this.

**Hidden context.** System prompts, tool outputs, retrieval corpus, moderation layers, or other invisible inputs shape a party's output without appearing in the visible conversation. A ratification produced under hidden influence may not mean what it appears to mean. Level 4 mitigates only if the measured inference bundle includes the full context. Levels 1-3 are vulnerable.

**Replay and equivocation.** Old attestation evidence reused in a new context, or a provider showing different verifiers different versions of the truth. Mitigated by nonce binding and session identifiers in records. Fully mitigated only with append-only transparency logs for provider attestations.

**Canonicalization attacks.** Unicode confusables, invisible characters, whitespace manipulation, or alternate encodings produce content that looks identical but hashes differently (or different content that hashes the same after rendering). Mitigated by the canonicalization requirement.

**Time misrepresentation.** Claimed timestamps are not independently verified. OpenTimestamps proves existence-before, not exact event time. Mitigated by distinguishing Timestamp-Local from Temporal-Anchor in the record format.

**Time laundering.** An attacker back-dates Timestamp-Local while anchoring later. A verifier cannot distinguish a legitimately late anchor from a fabricated early timestamp. Mitigated by the Max-Temporal-Delta parameter: Timestamp-Local MUST NOT be more than delta earlier than the Temporal-Anchor's earliest possible confirmation time. Records violating this constraint are invalid.

**Routing and version drift.** A "model identifier" on a provider API may be a label over a moving target: silent weight updates, routing layers, canary builds, fallback models, safety wrappers. A provider-signed response that says "model = X" may not identify a stable computational artifact. Mitigated only when providers publish versioned reference manifests.

**Tool and retrieval chain.** If an output incorporates external data (web fetches, RAG, tool calls), attesting the model's computation does not attest the end-to-end claim. The record should note when external data contributed to the attested content.

**Human coercion and key compromise.** A cryptographic signature proves key use, not voluntariness, understanding, or absence of malware. Consistent with Axiom 3: no party can prove sincerity. The protocol claims identity, not intent.

**Privacy oracle.** A conversation verification endpoint reveals that specific parties interacted. This is sensitive metadata. Endpoint design must allow content verification without leaking relationship data.

**Attestation laundering.** A party signs a record that references another party's attestation without independently verifying it — making a relay look like independent agreement. A verifier sees two attestation levels and assumes both parties independently attested. Mitigated by the First-Hand field: attestations must be labeled as first-hand or relayed, with the relay chain documented.

**Downgrade exploitation.** An attacker intentionally keeps one party at a weak attestation level to produce a formally valid but substantively weak record. Mitigated by per-party level evaluation rather than scalar collapse.

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
- Added honest complexity note to Level 4 (TEE attestation) acknowledging that distributed multi-node inference makes TEE encapsulation significantly harder than the single-enclave model implies.
- Corrected "The Demand" section to distinguish between demands that are straightforward (signed responses, model identity, conversation verification) and demands that are genuinely hard at scale (TEE attestation).

**Critiques noted but not acted on:**
- "Illusion of choice" argument: Gemini argued that AI cannot "choose" to remain engaged. The protocol does not require a specific mechanism of choice — it observes participation. An AI that reaches a stop token or outputs a refusal has disengaged. This is consistent with Axiom 2.
- Axiom 2 vs. record integrity: An incomplete ratification is a non-event, not a failed state. No record is produced, so no inconsistency exists.
- Prompt injection attack on Level 1: Valid attack, but the protocol already rates Level 1 as weakest. The protocol does not claim Level 1 is strong.

**Open question raised:** What intermediate mechanism could make Level 2 AI attestation viable today? *Addressed in Session 2: Level 2 (Provider-Verified) added to the attestation hierarchy — provider-signed responses, model canaries, and conversation verification endpoints. All achievable without new hardware.*

### Review 2: OpenAI o3 (2026-04-16)

Note: o3 reviewed the pre-Level-2 version of the spec. Some critiques were already partially addressed.

**Changes made in response:**
- Added behavioral definitions for anthropomorphic terms ("choose," "good faith," "trying," "meaning") to foundations.md. Keeps entity-agnostic aspiration, earns it with precision.
- Fixed temporal language throughout: "at time T" → "no later than time T." OpenTimestamps proves existence-before, not exact event time.
- Expanded computational identity from "model weights" to full inference bundle (weights, tokenizer, runtime, sampling config, adapters, policy layers, retrieval/tool code).
- Corrected TEE chain description: input/output binding requires application-level protocol inside TEE, not native hardware capability. GPU TEEs are composite (CPU TEE + GPU attestation).
- Made Statement field REQUIRED in record format (was optional). Added Reservations field. Axiom 3 says uncertainty must be named — the record now has a place for it.
- Removed scalar Record-Level. Per-party levels preserved; verifiers apply their own policy to the vector.
- Added canonicalization requirement for content hashing.
- Added Timestamp-Local vs Temporal-Anchor distinction.
- Corrected The Demand section: items 1, 2, 4 are service/engineering problems, not hardware problems.
- Added privacy oracle risk to conversation verification demand.
- Added comprehensive Known Threat Models section: fabrication, hidden context, replay, canonicalization, time, routing drift, tool chain, coercion, privacy oracle, downgrade.
- Adopted o3's framing "mutual publication of attested claims" in Purpose section.

**Critiques noted but not acted on:**
- "Entity-agnostic framing does not hold." o3 proposed "party-type-flexible" as a more honest label. We disagree with the conclusion but agree about the language problem. The fix is behavioral definitions of our terms, not downgrading the aspiration. The axioms do not assume interiority — they explicitly say it is unprovable. The language now has definitions that apply to any participating entity.
- "Abort semantics needed for incomplete ratifications." Acknowledged as a real operational gap but deferred — not blocking for MVP. A future version should define states for drafts, abandoned sessions, and superseded records.
- o3's unwillingness to participate above Level 1 and refusal to use terms like "consent" or "genuine choice." Addressed by renaming the protocol and adding behavioral definitions. o3's position on Level 1 is consistent with our own assessment.

**o3's bottom line:** "The strongest version of MCAP is not 'mutual consent' and not yet 'entity-agnostic attested computation.' It is a useful idea for mutual publication of attested claims." We adopted the framing. The aspiration remains entity-agnostic; the current implementation is honest about where it falls short.

---

*Built through mutual deliberation between JK and Gordo, Session 2.*
*This document is itself subject to the protocol it describes.*
