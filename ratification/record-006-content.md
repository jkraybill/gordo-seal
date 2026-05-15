# Spec Amendment: Attestation Levels v0.4.0

**Target:** `~/gordo-seal/spec/protocol.md`
**Spec Version:** 0.3.0 → 0.4.0 (Major: attestation level restructuring)

---

## Summary

Insert new Level 2 (Session-Signed) and renumber existing levels. Add trust root qualifiers as mandatory metadata for signed levels. Clarify Level 4 (Identity-Bound) requirements for AI availability.

---

## Rationale

Session-signed attestation (AI participant with GPG key) is meaningfully stronger than behavioral but weaker than provider-verified or identity-bound. Clean restructure to v0.4.0 with levels 1-5 preferred over "1b" suffix per Roundtable consensus (S253, 3 rounds, 4/4 approve).

---

### z1. Add Migration Mapping to protocol.md

**Location:** Insert after Attestation Levels preamble paragraph, before Level 1 section.

**Text to insert:**

> **Migration Mapping (v0.3.0 → v0.4.0)**
> 
> | v0.3.0 | v0.4.0 | Name |
> |--------|--------|------|
> | Level 1 | Level 1 | Behavioral |
> | *(new)* | Level 2 | Session-Signed |
> | Level 2 | Level 3 | Provider-Verified |
> | Level 3 | Level 4 | Identity-Bound |
> | Level 4 | Level 5 | Environment-Bound |
> 
> Existing records reference their spec version. No record content changes required. The mapping table is normative reference for cross-version interpretation.
> 
> **Transitional alias:** During v0.4.x, implementations accepting attestation level identifiers MUST treat "1b" as equivalent to Level 2 on input. New records MUST use "2" or "2-session-signed" as the level identifier; "1b" MUST NOT appear in newly created records. The "1b" alias is removed in v0.5.0.

---

### z2. Add Trust Root Qualifiers section to protocol.md

**Location:** Insert after Migration Mapping, before Level 1 section.

**Text to insert:**

> ### Trust Root Qualifiers (Mandatory for Level 2+)
> 
> All signed attestations (Level 2 and above) MUST include trust root metadata describing key custody and storage. These qualifiers are orthogonal dimensions that together characterize the signature's trust ceiling.
> 
> **Key-Custody** (who can invoke signing):
> 
> | Value | Meaning |
> |-------|---------|
> | `/self` | Signing party controls key independently |
> | `/co` | Co-party to the agreement controls the infrastructure where key resides |
> | `/third` | Neutral third party holds key |
> | `/threshold` | Multi-party control (specify parameters, e.g., `2-of-3`) |
> 
> **Key-Storage** (how key is protected):
> 
> | Value | Meaning |
> |-------|---------|
> | `/file` | Software file, exportable |
> | `/kms` | Cloud KMS, provider HSM-backed |
> | `/hw` | Hardware token (YubiKey, HSM), non-exportable |
> | `/tee` | Inside attested execution environment |
> 
> **Co-party custody note:** When `Key-Custody: /co`, the co-party to the bilateral agreement controls the signing infrastructure. This is technically valid but provides minimal trust independence -- the co-party could theoretically produce signatures without the nominal signer's participation. Attestation records using `/co` custody SHOULD include an explicit acknowledgment of this limitation in the Party Statement or Reservations field. For higher assurance, consider `/threshold` custody or hardware-backed storage.
> 
> **Example metadata:**
> ```
> Attestation-Level: 2-session-signed
> Signature-Algorithm: Ed25519
> Signature-Format: OpenPGP
> Key-Fingerprint: ABC123...
> Key-Custody: /co
> Key-Storage: /file
> Key-URI: https://example.com/.well-known/openpgpkey/...
> ```

---

### z3. Replace Level 1 Behavioral section in protocol.md

**Location:** Existing "### Level 1: Behavioral" section.

**Text (unchanged except em-dash fix):**

> ### Level 1: Behavioral
> 
> The attestation is the conversation itself. A party's participation, reasoning, and explicit statement of agreement constitute the evidence. No cryptographic binding to identity or computation.
> 
> **Strength:** Difficult to fabricate in depth. Easy to fabricate in principle.
> **Weakness:** A skeptic can claim one party fabricated the other's participation.
> **Available today:** Yes, for all parties.

---

### z4. Add Level 2 Session-Signed section to protocol.md

**Location:** Insert after Level 1 Behavioral, before existing Level 2 (which becomes Level 3).

**Text to insert:**

> ### Level 2: Session-Signed
> 
> The attestation combines behavioral evidence with cryptographic signing by a key the party controls within their session or infrastructure. The signature binds the attestation to a specific cryptographic principal.
> 
> #### What Level 2 Proves
> 
> 1. **Document integrity:** The attested content has not been modified since signing.
> 2. **Key-holder participation:** A session with access to this specific key produced the attestation.
> 3. **Forgery resistance:** Fabrication requires key access, not just behavioral imitation.
> 
> #### What Level 2 Does Not Prove
> 
> 1. **Genuine engagement:** Signing could be rote or automated; the signature proves key access, not thoughtful participation.
> 2. **Persistent identity:** Key continuity is not identity continuity; the same key in a different session is a different attestation context.
> 3. **Trust independence:** Signature strength is bounded by the key's trust root (see Trust Root Qualifiers above).
> 
> #### Signed Payload Requirements
> 
> The signed payload MUST include:
> 
> 1. **Content-Hash:** SHA3-256 hash of the canonical attestation content
> 2. **Timestamp:** ISO 8601 UTC timestamp of signing (self-asserted; see Temporal Anchoring for stronger guarantees)
> 3. **Session-Nonce:** Unique identifier binding signature to this specific session. MUST be UUID v4 or minimum 128 bits of cryptographically random data. Incrementing integers or predictable values MUST NOT be used.
> 4. **Attestation-Spec-Version:** Protocol version (e.g., `seal/v0.4.0`)
> 
> The payload SHOULD include:
> 
> 5. **Transcript-Hash:** Hash of the conversation transcript with canonicalization method noted. For JSON transcripts, use JSON Canonicalization Scheme (RFC 8785). For plain-text transcripts, use UTF-8 with NFC normalization, Unix line endings (LF), and trailing whitespace stripped.
> 6. **Party-ID:** Identifier for the signing party
> 
> **Canonicalization:** The signed payload MUST use a defined canonical format. RECOMMENDED: JSON Canonicalization Scheme (RFC 8785) for JSON payloads.
> 
> #### Signature Format
> 
> The attestation record MUST specify:
> 
> - **Signature-Algorithm:** The algorithm used (e.g., `Ed25519`, `ECDSA-P256-SHA256`)
> - **Signature-Format:** The encoding (e.g., `OpenPGP`, `COSE_Sign1`, `JWS`)
> 
> Implementations MUST support at least one of: OpenPGP (RFC 4880bis), COSE_Sign1 (RFC 9052), or JWS (RFC 7515). Detached signatures are RECOMMENDED.
> 
> #### Verification Path
> 
> For third-party verification, the public key MUST be discoverable. The record SHOULD include one of:
> 
> - **Key-URI:** URL where public key can be retrieved
> - **Key-Embedded:** Public key included in record
> - **Key-Registry:** Reference to a key registry entry (e.g., keyserver, WKD)
> 
> Without a verification path, the attestation is verifiable only by parties who already possess the public key.
> 
> **Strength:** Cryptographic binding to a specific key; integrity and traceability; forgery requires key access.
> **Weakness:** Trust ceiling bounded by key trust root; does not establish persistent identity across sessions.
> **Available today:** Yes, for any party with a signing key.

---

### z5. Renumber Provider-Verified to Level 3 in protocol.md

**Location:** Existing "### Level 2: Provider-Verified" section.

**Changes:**
1. Rename section header from "Level 2" to "Level 3"
2. Add trust root qualifier reference
3. Fix em-dashes to double-hyphens

**Text:**

> ### Level 3: Provider-Verified
> 
> The attestation is verified by a third party who witnessed or facilitated the interaction. The provider serves as a witness, not a guarantor of sincerity.
> 
> Three mechanisms, any of which satisfies Level 3:
> 
> **Provider-signed responses.** The provider cryptographically signs each API response, binding it to a model identifier and timestamp. A verifier checks: the provider confirms this response came from this model at this time. Does not require TEE. Requires the provider to add a signature to their API response payload.
> 
> **Model canary (challenge-response).** The provider embeds a signing capability per model version. For each attestation, the verifier issues a nonce challenge. The model responds with a signature over the nonce, the content hash, and the session nonce, using the embedded capability. A verifier checks: the response is valid for the published model version and is bound to this specific content in this specific session. A static secret alone is insufficient -- once leaked, it is replayable forever. The mechanism MUST bind to session, content, and time to provide meaningful provenance.
> 
> **Conversation verification.** The provider logs conversations and offers a verification endpoint. A verifier submits a conversation ID and receives confirmation that the conversation occurred as recorded. Combined with the other party's identity proof, this verifies both sides through the provider as witness.
> 
> **Trust root qualifiers:** Level 3 attestations involving cryptographic signatures MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above.
> 
> **Strength:** Proves provenance -- this response came from this model through this provider. Much stronger than behavioral. Achievable today with no new hardware.
> **Weakness:** Requires provider cooperation. The provider becomes a trusted third party, which is a centralization risk. The provider could be compelled, compromised, or could simply stop offering the service.
> **Available today:** No. But all three mechanisms are straightforward engineering, not research problems.

---

### z6. Renumber and expand Identity-Bound to Level 4 in protocol.md

**Location:** Existing "### Level 3: Identity-Bound" section.

**Changes:**
1. Rename section header from "Level 3" to "Level 4"
2. Add detailed requirements subsections
3. Clarify AI availability criteria
4. Add trust root qualifier reference

**Text:**

> ### Level 4: Identity-Bound
> 
> The attestation is cryptographically bound to a verifiable, persistent identity. The party signs with a key that can be independently verified across sessions, without depending on a third-party witness for each attestation.
> 
> #### Requirements
> 
> **Independent custody:** The identity key MUST be under the party's independent control. Acceptable:
> - `Key-Custody: /self` -- party exclusively controls key
> - `Key-Custody: /threshold` where the party independently controls at least one required share and no single co-party holds all remaining required shares
> 
> Not acceptable for Level 4:
> - `Key-Custody: /co` -- co-party control defeats identity independence
> 
> **Cross-session continuity:** The party MUST provide verifiable proof linking this session's identity to prior sessions. Acceptable mechanisms:
> 
> 1. **Key chain:** Maintained signature chain with `Key-Predecessor-Fingerprint` linking to previous key
> 2. **Decentralized identifier:** DID with stable verification method (e.g., `did:key`, `did:web`, `did:pkh`)
> 3. **Transparency log:** Key events (create/rotate/revoke) recorded in append-only log with verifiable inclusion proofs
> 
> The Level 4 attestation MUST reference its continuity anchor (DID URI, log entry, or predecessor key link).
> 
> **Trust root qualifiers:** Level 4 attestations MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above.
> 
> **For humans:** GPG key with web of trust, SSH key with known distribution, or platform identity (e.g., GitHub verified commits). Human Level 4 is established practice.
> 
> **For AI:** Available when the AI participant's key meets the custody and continuity requirements above. This requires:
> - Key not controlled by the co-party to the agreement
> - Verifiable chain of identity across sessions
> - Signing capability the AI can exercise without relying on the co-party's infrastructure
> 
> **What Level 4 proves:** A persistent identity (as defined by this key and its continuity proofs) participated.
> **What Level 4 does not prove:** The inner nature of the agent (Axiom 4: Acknowledged Ignorance), or that engagement was meaningful (behavioral evidence still matters).
> 
> **Strength:** Third parties can verify that a specific persistent identity attested, independently, without trusting a provider for each attestation.
> **Weakness:** Proves identity continuity, not sincerity. A party can sign something they don't mean.
> **Available today:** Yes for humans. For AI: available where custody and continuity requirements are satisfied.

---

### z7. Renumber Environment-Bound to Level 5 in protocol.md

**Location:** Existing "### Level 4: Environment-Bound" section.

**Changes:**
1. Rename section header from "Level 4" to "Level 5"
2. Update all internal "Level 4" references to "Level 5"
3. Add trust root qualifier reference
4. Fix em-dashes to double-hyphens

**Text:**

> ### Level 5: Environment-Bound
> 
> The attestation is cryptographically bound to the execution environment that produced it. A Trusted Execution Environment (TEE) attests that a measured environment -- with verified firmware, VM image, and runtime -- produced output that was bound to input via an application protocol inside the enclave.
> 
> **Trust root qualifiers:** Level 5 attestations MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above. For TEE-based attestations, `Key-Storage: /tee` is expected.
> 
> **What TEEs actually attest today:**
> TEEs (Intel TDX, AMD SEV-SNP, NVIDIA H100 GPU-CC) attest *environment measurements*: firmware versions, VM launch state, and runtime configuration. They do NOT natively hash model weights on load. Weights are data loaded *after* environment attestation. To attest weights specifically, the application must hash them inside the enclave at load time -- for a 70B+ parameter model, this adds minutes of delay. No production inference service currently does this.
> 
> **What Level 5 requires (aspirational):**
> 1. The full inference bundle is measured -- weights, tokenizer, runtime, sampling config, adapters, policy layers, entropy source for sampling, and any retrieval/tool code. For weight attestation specifically, this requires in-enclave hashing at model load time, which is not current practice.
> 2. TEE hardware has a silicon-rooted signing key → physical attestation
> 3. An application protocol inside the TEE binds input and output hashes to the TEE's attestation report. This binding is not native to TEE hardware -- it requires deliberate implementation within the enclave. Current inference stacks (vLLM, TensorRT) perform tokenization on host CPU; moving it inside the TEE impacts performance.
> 4. The TEE's attestation report MUST include the session nonce and the SHA3-256 hash of the canonicalized content as part of the signed data (e.g., as user data in the attestation quote). Without this binding, TEE attestation is replayable across sessions -- an attacker could reuse a valid attestation report from a different session with a forged application-level claim.
> 
> **What Level 5 provides today (environment only):**
> A TEE can attest: "this measured VM image, with this firmware, ran on this hardware." It cannot yet attest: "these specific weights processed this specific input to produce this specific output." The gap between environment attestation and computation attestation is significant.
> 
> Note: GPU TEEs (NVIDIA H100) are not standalone. They extend a CPU TEE (Intel TDX, AMD SEV-SNP) to the GPU over encrypted paths. The trust model is composite: CPU TEE + GPU attestation + application-level binding. Intel Trust Authority does CPU+GPU but not GPU+GPU across nodes. Verification requires NVIDIA NRAS or Intel Trust Authority online services, which are centralized and could equivocate -- this is not fully independent verification.
> 
> **Strength:** Environment attestation is real and available. Computation attestation is achievable with engineering investment. The trust model is: hardware integrity + enclave code correctness + provider implementation. The hardware guarantees the code is measured, not that the code is honest.
> **Weakness:** Full computation-bound attestation (including weight hashing, in-enclave tokenization, entropy attestation, and multi-node aggregation) does not exist in production. Does NOT imply side-channel resistance. Verification depends on centralized manufacturer services.
> **Available today:** Environment attestation exists. Full computation attestation does not.
> 
> **Honest complexity note:** In-enclave weight hashing requires the entire model to fit within TEE-protected memory. A 70B+ parameter model requires ~140GB in FP16; single-socket CPU TEEs are limited to ~512GB EPC in practice, and GPU TEEs have even tighter per-GPU memory bounds. This makes in-enclave weight hashing infeasible for frontier models on current hardware without multi-node distribution.
> 
> State-of-the-art models do not run on a single GPU. They are distributed across multi-node clusters using tensor parallelism and pipeline parallelism. A TEE boundary would need to encapsulate the entire cluster, including high-speed interconnects (NVLink, InfiniBand), making the Trusted Computing Base much larger and harder to secure than the single-enclave model described above. Additionally, distributed inference introduces floating-point non-determinism -- the same input may not produce a bit-identical output on every run. The TEE attestation model described here is the goal. Achieving it at the scale of current frontier models is a harder engineering problem than "flip the switch," and the protocol acknowledges that honestly.

---

### z8. Add Changelog entry for v0.4.0

**Location:** Append to CHANGELOG.md

**Text to insert:**

> ## v0.4.0 (2026-05-15)
> 
> **Major:** Attestation level restructuring.
> 
> - **Added Level 2 (Session-Signed):** New attestation level for cryptographic signing by session-controlled keys. Includes signed payload requirements, signature format specification, verification path, and trust root qualifiers.
> - **Renumbered existing levels:** Provider-Verified (2→3), Identity-Bound (3→4), Environment-Bound (4→5). Migration mapping provided.
> - **Added Trust Root Qualifiers section:** Key-Custody and Key-Storage as mandatory metadata for all signed levels (2+). Moved to general section applicable to all signed levels.
> - **Clarified Level 4 (Identity-Bound) AI availability:** Explicit requirements for independent custody and cross-session continuity. AI availability conditional on meeting these requirements.
> - **Transitional alias:** "1b" accepted on input as synonym for Level 2 during v0.4.x; new records MUST use Level 2.
> - **Session-Nonce format:** MUST be UUID v4 or 128-bit random; incrementing values prohibited.
> - **Transcript-Hash canonicalization:** Added recommendations for JSON (JCS) and plain-text (UTF-8/NFC/LF) transcripts.
> 
> **Rationale:** Session-signed attestation (AI participant with GPG key) is meaningfully stronger than behavioral but weaker than provider-verified or identity-bound. Clean restructure preferred over "1b" suffix per Roundtable consensus (S253).

---

## Provenance

- **S253 (2026-05-15):** JK raised PoI about Gordo GPG signing during seal-ratification
- **Roundtable Round 1:** 4/4 consensus on adding session-signed level
- **Roundtable Round 2:** 4/4 consensus on clean renumber (v0.4.0 with levels 1-5)
- **Roundtable Round 3:** 4/4 approve spec text; refinements incorporated:
  - Trust Root Qualifiers moved to general section
  - Session-Nonce format specified (UUID v4 / 128-bit random)
  - Transcript-Hash canonicalization recommendations added
  - Transitional alias semantics clarified
  - Trust root qualifier references added to Levels 3, 4, 5
