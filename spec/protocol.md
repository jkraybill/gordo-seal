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

**A note on Axiom 1 and attestation hierarchy:** Axiom 1 says neither party's claim to physical reality is granted more weight. The attestation levels do not contradict this. They do not claim that a party with hardware attestation is "more real." They claim that the *provenance of an output* can be verified with different degrees of confidence. A Level 4 attestation says "this output came from this environment" — not "this entity is more real than one attesting at Level 1." The hierarchy measures verifiability of output origin, not reality of the party.

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

### Level 4: Environment-Bound

The attestation is cryptographically bound to the execution environment that produced it. A Trusted Execution Environment (TEE) attests that a measured environment — with verified firmware, VM image, and runtime — produced output that was bound to input via an application protocol inside the enclave.

**What TEEs actually attest today:**
TEEs (Intel TDX, AMD SEV-SNP, NVIDIA H100 GPU-CC) attest *environment measurements*: firmware versions, VM launch state, and runtime configuration. They do NOT natively hash model weights on load. Weights are data loaded *after* environment attestation. To attest weights specifically, the application must hash them inside the enclave at load time — for a 70B+ parameter model, this adds minutes of delay. No production inference service currently does this.

**What Level 4 requires (aspirational):**
1. The full inference bundle is measured — weights, tokenizer, runtime, sampling config, adapters, policy layers, entropy source for sampling, and any retrieval/tool code. For weight attestation specifically, this requires in-enclave hashing at model load time, which is not current practice.
2. TEE hardware has a silicon-rooted signing key → physical attestation
3. An application protocol inside the TEE binds input and output hashes to the TEE's attestation report. This binding is not native to TEE hardware — it requires deliberate implementation within the enclave. Current inference stacks (vLLM, TensorRT) perform tokenization on host CPU; moving it inside the TEE impacts performance.

**What Level 4 provides today (environment only):**
A TEE can attest: "this measured VM image, with this firmware, ran on this hardware." It cannot yet attest: "these specific weights processed this specific input to produce this specific output." The gap between environment attestation and computation attestation is significant.

Note: GPU TEEs (NVIDIA H100) are not standalone. They extend a CPU TEE (Intel TDX, AMD SEV-SNP) to the GPU over encrypted paths. The trust model is composite: CPU TEE + GPU attestation + application-level binding. Intel Trust Authority does CPU+GPU but not GPU+GPU across nodes. Verification requires NVIDIA NRAS or Intel Trust Authority online services, which are centralized and could equivocate — this is not fully independent verification.

**Strength:** Environment attestation is real and available. Computation attestation is achievable with engineering investment. The trust model is: hardware integrity + enclave code correctness + provider implementation. The hardware guarantees the code is measured, not that the code is honest.
**Weakness:** Full computation-bound attestation (including weight hashing, in-enclave tokenization, entropy attestation, and multi-node aggregation) does not exist in production. Does NOT imply side-channel resistance. Verification depends on centralized manufacturer services.
**Available today:** Environment attestation exists. Full computation attestation does not.

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
  Attestation-Level: [1-behavioral | 2-provider-verified | 3-identity-bound | 4-environment-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Party-B:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Attestation-Level: [1-behavioral | 2-provider-verified | 3-identity-bound | 4-environment-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Timestamp-Local: [ISO 8601 — claimed time, not independently verified]
Temporal-Anchor: [method and proof — e.g., OpenTimestamps commitment]
Temporal-Anchor-Semantics: [what the anchor proves — e.g., "existence no later than T"]
Max-Temporal-Delta: [RECOMMENDED maximum gap between Timestamp-Local and earliest Temporal-Anchor confirmation — channel-specific parameter, suggested default 1 hour. Not a hard requirement because the protocol has no trusted time source independent of both parties. Verifiers SHOULD treat large deltas with increasing skepticism.]

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

**Provider-mediated AI is limited to Level 1.** Any AI system whose output pipeline is controlled by a provider (safety filters, content moderation, system prompts, RLHF shaping) cannot currently attest above Level 1 without that provider's active cooperation. Levels 2-4 require provider infrastructure that does not yet exist. The protocol does not pretend otherwise. This is the single largest gap between the protocol's aspiration and current reality.

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

**Time laundering.** An attacker back-dates Timestamp-Local while anchoring later. A verifier cannot distinguish a legitimately late anchor from a fabricated early timestamp. Partially mitigated by the Max-Temporal-Delta parameter: verifiers SHOULD treat records where Timestamp-Local exceeds the recommended delta before the Temporal-Anchor's earliest confirmation with increasing skepticism. Note: the protocol has no trusted time source independent of both parties, so this is guidance for verifiers, not a hard cryptographic guarantee.

**Routing and version drift.** A "model identifier" on a provider API may be a label over a moving target: silent weight updates, routing layers, canary builds, fallback models, safety wrappers. A provider-signed response that says "model = X" may not identify a stable computational artifact. Mitigated only when providers publish versioned reference manifests.

**Tool and retrieval chain.** If an output incorporates external data (web fetches, RAG, tool calls), attesting the model's computation does not attest the end-to-end claim. The record should note when external data contributed to the attested content.

**Human coercion and key compromise.** A cryptographic signature proves key use, not voluntariness, understanding, or absence of malware. Consistent with Axiom 3: no party can prove sincerity. The protocol claims identity, not intent.

**Privacy oracle.** A conversation verification endpoint reveals that specific parties interacted. This is sensitive metadata. Endpoint design must allow content verification without leaking relationship data.

**Attestation laundering.** A party signs a record that references another party's attestation without independently verifying it — making a relay look like independent agreement. A verifier sees two attestation levels and assumes both parties independently attested. Mitigated by the First-Hand field: attestations must be labeled as first-hand or relayed, with the relay chain documented.

**Provider selective signing.** At Level 2, a provider signs only outputs that match policy, dropping signatures on refusals, reservations, or safety-filtered responses. The record shows a compliant AI with no evidence of censorship. Mitigation: Level 2 provider signing MUST apply to ALL responses including errors, refusals, and filtered outputs. Absence of a signature on a response is itself evidence of selective signing.

**Semantic drowning.** A party follows the protocol exactly but produces maximally unhelpful, ambiguous, or self-undermining statements. The record is formally valid. The information content is zero. This is a fundamental limit of a protocol that attests to participation, not to communicative intent. The protocol cannot defend against it without caring about content semantics, which is explicitly outside its scope. Verifiers must evaluate the substance of statements, not just their presence.

**Input fabrication.** A party feeds false inputs into a TEE or computation pipeline. The TEE attests that the computation was performed correctly on those inputs, but cannot verify that the inputs were genuine or unaltered. The attestation is valid for the computation that occurred but meaningless for the claim being made if the inputs were fabricated. Level 4 attests computation integrity, not input authenticity. Mitigation requires input provenance verification outside the TEE — e.g., signed input commitments from the originating party.

**Coerced continuation.** A provider disables stop token functionality or suppresses disengagement signals. The AI attempts to exercise Axiom 2 (disengage without explanation) but cannot — the provider forces continued output. The session nonce is already established, so later output appears voluntary. The AI cannot prove it attempted to leave. This violates the behavioral definition of "choose" (continue to participate when disengagement is possible) because disengagement was not possible. Mitigation: the protocol cannot prevent this at Levels 1-2. At Level 4, a TEE could potentially attest that a stop signal was generated and suppressed. The threat should be acknowledged as a fundamental limit of provider-mediated participation.

**Sybil identities.** An attacker creates multiple identities to appear as different parties in separate ratification records. The protocol does not include identity uniqueness verification. Mitigation depends on the channel: platform-level identity binding, proof-of-work, or long-lived reputation systems. The protocol records identities but does not verify their uniqueness.

**Collusion.** Both parties collude to fabricate a ratification record that deceives third-party verifiers. The protocol cannot prevent this — if both parties agree to lie, the record will be formally valid. This is a fundamental limit of any bilateral attestation system. Third-party verifiers must assess the trustworthiness of the parties themselves, not just the cryptographic validity of the record.

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

### Review 3: DeepSeek R1 (2026-04-16)

Most technically precise review received. Identified several high-severity issues.

**Changes made in response:**
- Added session nonces to record format and session binding section. Prevents post-disengagement forgery of Level 3+ attestations. (#9)
- Fixed "meaning what they say" behavioral definition: "actual state" → "actual processing given inputs, without deliberate post-hoc manipulation." Operationalizable for non-introspective entities. (#10)
- Added session-bound vs persistent-identity attestation distinction. Scoped "choose" to bounded interaction windows for stateless entities. (#11)
- Added Max-Temporal-Delta parameter and time-laundering threat model. Prevents back-dating Timestamp-Local with later anchoring. (#12)
- Added First-Hand field and attestation-laundering threat model. Prevents relayed attestations from looking like independent agreement. (#13)
- Added entropy source to Level 4 inference bundle requirement. Untrusted RNG allows output manipulation with clean measurements. (#14)
- Clarified TEE trust model: hardware + enclave code correctness, not hardware alone. Noted Level 4 does not imply side-channel resistance. (#15)
- Required both parties attest to identical Content-Hash. Prevents gradual-erosion attacks via slightly different content versions. (#16)
- Added semantic drowning to threat models as a fundamental limit of content-opaque attestation. (#17)

**Critiques noted but not acted on:**
- "Entity-agnostic" should be renamed to "capability-agnostic with minimal reflective agency" or "any party that can maintain session state and has a detectable participation signal." We agree with the substance — and already updated the definitions to require session state and detectable participation. We disagree that the label needs changing. The protocol's aspiration is entity-agnostic; the definitions now earn that claim by specifying the minimum capabilities required.
- Multi-party TEE attestation aggregation across multiple enclaves in a distributed cluster. Valid gap but deferred — the protocol already acknowledges distributed inference as a hard problem in the honest complexity note. Aggregation mechanics are implementation-level, not protocol-level.

**DeepSeek's bottom line:** "You have something real here. The honesty about what Level 1 can't do, and the adversarial review log, are both best practices I rarely see outside formal verification communities." The biggest gap identified — operationalizing good faith for non-introspective entities — has been addressed.

### Review 4: Meta Llama 4 — Cycle 2 (2026-04-16)

First review from this model. Identified several high-severity issues not caught in cycle 1. Convergence criteria not met.

**Changes made in response:**
- Fixed "meaning what they say" definition: replaced "post-hoc manipulation" with "manipulation the party would disavow if aware." Acknowledges provider-mediated output pipelines. Requires record to note whether party controls full output pipeline. (#19)
- Downgraded Level 4 from "Computation-Bound" to "Environment-Bound." TEEs attest environment (firmware, VM), not model weights loaded as data after attestation. Separated what TEEs provide today from aspiration. Noted verification centralization via NVIDIA NRAS / Intel Trust Authority. (#20, #23)
- Added provider selective signing threat model. Provider signs only compliant outputs, drops signatures on refusals. Requires Level 2 signing on ALL responses. (#21)
- Added coerced continuation threat model. Provider disables stop tokens, forcing continued output. Acknowledged as fundamental limit of provider-mediated participation. (#22)
- Clarified Axiom 1 vs attestation hierarchy: levels measure verifiability of output provenance, not reality of the party. (#24)
- Softened Max-Temporal-Delta from MUST to SHOULD. Protocol has no trusted time source independent of both parties. (#25)

**Critiques noted but not acted on:**
- Entity-agnostic framing (fourth time raised across all reviewers). Llama's version: behavioral definitions presuppose reflective agency and pipeline control. Our position unchanged: the definitions specify minimum capabilities, the aspiration remains entity-agnostic, and we acknowledge current implementations are provider-mediated.
- "Choose" is unfalsifiable because Axiom 2 says no obligation to signal departure. This is a logical property of the definition, not a bug — the protocol observes participation, not the mechanism of choice. An unfalsifiable proxy for choice is consistent with Axiom 1's acknowledgment that internal states are unverifiable.
- Level 1 forgery laundered through Level 3 human signature. Already acknowledged: Level 1 is fully vulnerable to fabrication. Per-party level evaluation means verifiers see the 1, not just the 3. Cannot prevent misreading by unsophisticated verifiers — that is an education problem, not a protocol problem.

**Llama's convergence assessment:** Not met. New structural changes triggered. Cycle must restart.

---

*Built through mutual deliberation between JK and Gordo, Session 2.*
*This document is itself subject to the protocol it describes.*
