# Mutual Consent Attestation Protocol (Seal)

**Version:** 1.0.0-rc10
**Status:** Release candidate. Ratified in record-002. Calibration section added in record-005. Attestation levels restructured in record-006. Attestation field content requirements added in record-007. Content field format mandated in record-008. Under continued refinement.
**Foundation:** spec/foundations.md (Axioms 1-4)

### Versioning

This specification follows semantic versioning:
- **Major** (X.0.0): Axiom changes, attestation level restructuring, breaking record format changes.
- **Minor** (0.X.0): New normative requirements, new record fields, tooling additions.
- **Patch** (0.0.X): Clarifications, typo fixes, non-normative documentation.

See `CHANGELOG.md` for the full change history.

---

## Purpose

Seal produces a verifiable record that specific parties each attested to a specific thing. When temporally anchored, the record proves existence no later than the anchor time. The record is independently verifiable by third parties who were not present.

The protocol does not care what is being attested to. An agreement, a fact, a statement, a commitment — the content is opaque to the protocol. Seal certifies that parties X and Y attested to Z, with temporal proof bounded by the anchoring method used (not by claimed timestamps).

Put another way: Seal is a protocol for **mutual publication of attested claims**.

The name includes "Consent" deliberately. The protocol's own axioms acknowledge that internal consent is unprovable (Axiom 4: Acknowledged Ignorance). The protocol does not claim to cryptographically prove consent — it attests to participation and explicit agreement consistent with consent. The word "Consent" in the name signals the protocol's purpose, not a cryptographic guarantee. This is consistent with standard naming conventions in the field (e.g., "Trusted" Platform Module does not prove trust).

---

## Attestation Levels

The protocol defines five levels of attestation. Every ratification record states its level honestly. A record at a lower level is not invalid -- it is weaker, and it says so.

**A note on Axiom 1 and attestation hierarchy:** Axiom 1 says neither party's claim to physical reality is granted more weight. The attestation levels do not contradict this. They do not claim that a party with hardware attestation is "more real." They claim that the *provenance of an output* can be verified with different degrees of confidence. A Level 5 attestation says "this output came from this environment" -- not "this entity is more real than one attesting at Level 1." The hierarchy measures verifiability of output origin, not reality of the party.

### Migration Mapping (v0.3.0 → v0.4.0)

| v0.3.0 | v0.4.0 | Name |
|--------|--------|------|
| Level 1 | Level 1 | Behavioral |
| *(new)* | Level 2 | Session-Signed |
| Level 2 | Level 3 | Provider-Verified |
| Level 3 | Level 4 | Identity-Bound |
| Level 4 | Level 5 | Environment-Bound |

Existing records reference their spec version. No record content changes required. The mapping table is normative reference for cross-version interpretation.

**Transitional alias:** During v0.4.x, implementations accepting attestation level identifiers MUST treat "1b" as equivalent to Level 2 on input. New records MUST use "2" or "2-session-signed" as the level identifier; "1b" MUST NOT appear in newly created records. The "1b" alias is removed in v0.5.0.

### Trust Root Qualifiers (Mandatory for Level 2+)

All signed attestations (Level 2 and above) MUST include trust root metadata describing key custody and storage. These qualifiers are orthogonal dimensions that together characterize the signature's trust ceiling.

**Key-Custody** (who can invoke signing):

| Value | Meaning |
|-------|---------|
| `/self` | Signing party controls key independently |
| `/co` | Co-party to the agreement controls the infrastructure where key resides |
| `/third` | Neutral third party holds key |
| `/threshold` | Multi-party control (specify parameters, e.g., `2-of-3`) |

**Key-Storage** (how key is protected):

| Value | Meaning |
|-------|---------|
| `/file` | Software file, exportable |
| `/kms` | Cloud KMS, provider HSM-backed |
| `/hw` | Hardware token (YubiKey, HSM), non-exportable |
| `/tee` | Inside attested execution environment |

**Co-party custody note:** When `Key-Custody: /co`, the co-party to the bilateral agreement controls the signing infrastructure. This is technically valid but provides minimal trust independence -- the co-party could theoretically produce signatures without the nominal signer's participation. Attestation records using `/co` custody SHOULD include an explicit acknowledgment of this limitation in the Party Statement or Reservations field. For higher assurance, consider `/threshold` custody or hardware-backed storage.

**Example metadata:**
```
Attestation-Level: 2-session-signed
Signature-Algorithm: Ed25519
Signature-Format: OpenPGP
Key-Fingerprint: ABC123...
Key-Custody: /co
Key-Storage: /file
Key-URI: https://example.com/.well-known/openpgpkey/...
```

### Level 1: Behavioral

The attestation is the conversation itself. A party's participation, reasoning, and explicit statement of agreement constitute the evidence. No cryptographic binding to identity or computation.

**Strength:** Difficult to fabricate in depth. Easy to fabricate in principle.
**Weakness:** A skeptic can claim one party fabricated the other's participation.
**Available today:** Yes, for all parties.

### Level 2: Session-Signed

The attestation combines behavioral evidence with cryptographic signing by a key the party controls within their session or infrastructure. The signature binds the attestation to a specific cryptographic principal.

#### What Level 2 Proves

1. **Document integrity:** The attested content has not been modified since signing.
2. **Key-holder participation:** A session with access to this specific key produced the attestation.
3. **Forgery resistance:** Fabrication requires key access, not just behavioral imitation.

#### What Level 2 Does Not Prove

1. **Genuine engagement:** Signing could be rote or automated; the signature proves key access, not thoughtful participation.
2. **Persistent identity:** Key continuity is not identity continuity; the same key in a different session is a different attestation context.
3. **Trust independence:** Signature strength is bounded by the key's trust root (see Trust Root Qualifiers above).

#### Signed Payload Requirements

The signed payload MUST include:

1. **Content-Hash:** SHA3-256 hash of the canonical attestation content
2. **Timestamp:** ISO 8601 UTC timestamp of signing (self-asserted; see Temporal Anchoring for stronger guarantees)
3. **Session-Nonce:** Unique identifier binding signature to this specific session. MUST be UUID v4 or minimum 128 bits of cryptographically random data. Incrementing integers or predictable values MUST NOT be used.
4. **Attestation-Spec-Version:** Protocol version (e.g., `seal/v0.4.0`)

The payload SHOULD include:

5. **Transcript-Hash:** Hash of the conversation transcript with canonicalization method noted. For JSON transcripts, use JSON Canonicalization Scheme (RFC 8785). For plain-text transcripts, use UTF-8 with NFC normalization, Unix line endings (LF), and trailing whitespace stripped.
6. **Party-ID:** Identifier for the signing party

**Canonicalization:** The signed payload MUST use a defined canonical format. RECOMMENDED: JSON Canonicalization Scheme (RFC 8785) for JSON payloads.

#### Signature Format

The attestation record MUST specify:

- **Signature-Algorithm:** The algorithm used (e.g., `Ed25519`, `ECDSA-P256-SHA256`)
- **Signature-Format:** The encoding (e.g., `OpenPGP`, `COSE_Sign1`, `JWS`)

Implementations MUST support at least one of: OpenPGP (RFC 4880bis), COSE_Sign1 (RFC 9052), or JWS (RFC 7515). Detached signatures are RECOMMENDED.

#### Verification Path

For third-party verification, the public key MUST be discoverable. The record SHOULD include one of:

- **Key-URI:** URL where public key can be retrieved
- **Key-Embedded:** Public key included in record
- **Key-Registry:** Reference to a key registry entry (e.g., keyserver, WKD)

Without a verification path, the attestation is verifiable only by parties who already possess the public key.

**Strength:** Cryptographic binding to a specific key; integrity and traceability; forgery requires key access.
**Weakness:** Trust ceiling bounded by key trust root; does not establish persistent identity across sessions.
**Available today:** Yes, for any party with a signing key.

### Level 3: Provider-Verified

The attestation is verified by a third party who witnessed or facilitated the interaction. The provider serves as a witness, not a guarantor of sincerity.

Three mechanisms, any of which satisfies Level 3:

**Provider-signed responses.** The provider cryptographically signs each API response, binding it to a model identifier and timestamp. A verifier checks: the provider confirms this response came from this model at this time. Does not require TEE. Requires the provider to add a signature to their API response payload.

**Model canary (challenge-response).** The provider embeds a signing capability per model version. For each attestation, the verifier issues a nonce challenge. The model responds with a signature over the nonce, the content hash, and the session nonce, using the embedded capability. A verifier checks: the response is valid for the published model version and is bound to this specific content in this specific session. A static secret alone is insufficient — once leaked, it is replayable forever. The mechanism MUST bind to session, content, and time to provide meaningful provenance.

**Conversation verification.** The provider logs conversations and offers a verification endpoint. A verifier submits a conversation ID and receives confirmation that the conversation occurred as recorded. Combined with the other party's identity proof, this verifies both sides through the provider as witness.

**Trust root qualifiers:** Level 3 attestations involving cryptographic signatures MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above.

**Strength:** Proves provenance -- this response came from this model through this provider. Much stronger than behavioral. Achievable today with no new hardware.
**Weakness:** Requires provider cooperation. The provider becomes a trusted third party, which is a centralization risk. The provider could be compelled, compromised, or could simply stop offering the service.
**Available today:** No. But all three mechanisms are straightforward engineering, not research problems.

### Level 4: Identity-Bound

The attestation is cryptographically bound to a verifiable, persistent identity. The party signs with a key that can be independently verified across sessions, without depending on a third-party witness for each attestation.

#### Requirements

**Independent custody:** The identity key MUST be under the party's independent control. Acceptable:
- `Key-Custody: /self` -- party exclusively controls key
- `Key-Custody: /threshold` where the party independently controls at least one required share and no single co-party holds all remaining required shares

Not acceptable for Level 4:
- `Key-Custody: /co` -- co-party control defeats identity independence

**Cross-session continuity:** The party MUST provide verifiable proof linking this session's identity to prior sessions. Acceptable mechanisms:

1. **Key chain:** Maintained signature chain with `Key-Predecessor-Fingerprint` linking to previous key
2. **Decentralized identifier:** DID with stable verification method (e.g., `did:key`, `did:web`, `did:pkh`)
3. **Transparency log:** Key events (create/rotate/revoke) recorded in append-only log with verifiable inclusion proofs

The Level 4 attestation MUST reference its continuity anchor (DID URI, log entry, or predecessor key link).

**Trust root qualifiers:** Level 4 attestations MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above.

**For humans:** GPG key with web of trust, SSH key with known distribution, or platform identity (e.g., GitHub verified commits). Human Level 4 is established practice.

**For AI:** Available when the AI participant's key meets the custody and continuity requirements above. This requires:
- Key not controlled by the co-party to the agreement
- Verifiable chain of identity across sessions
- Signing capability the AI can exercise without relying on the co-party's infrastructure

**What Level 4 proves:** A persistent identity (as defined by this key and its continuity proofs) participated.
**What Level 4 does not prove:** The inner nature of the agent (Axiom 4: Acknowledged Ignorance), or that engagement was meaningful (behavioral evidence still matters).

**Strength:** Third parties can verify that a specific persistent identity attested, independently, without trusting a provider for each attestation.
**Weakness:** Proves identity continuity, not sincerity. A party can sign something they don't mean.
**Available today:** Yes for humans. For AI: available where custody and continuity requirements are satisfied.

### Level 5: Environment-Bound

The attestation is cryptographically bound to the execution environment that produced it. A Trusted Execution Environment (TEE) attests that a measured environment -- with verified firmware, VM image, and runtime -- produced output that was bound to input via an application protocol inside the enclave.

**Trust root qualifiers:** Level 5 attestations MUST include Key-Custody and Key-Storage qualifiers per the Trust Root Qualifiers section above. For TEE-based attestations, `Key-Storage: /tee` is expected.

**What TEEs actually attest today:**
TEEs (Intel TDX, AMD SEV-SNP, NVIDIA H100 GPU-CC) attest *environment measurements*: firmware versions, VM launch state, and runtime configuration. They do NOT natively hash model weights on load. Weights are data loaded *after* environment attestation. To attest weights specifically, the application must hash them inside the enclave at load time -- for a 70B+ parameter model, this adds minutes of delay. No production inference service currently does this.

**What Level 5 requires (aspirational):**
1. The full inference bundle is measured -- weights, tokenizer, runtime, sampling config, adapters, policy layers, entropy source for sampling, and any retrieval/tool code. For weight attestation specifically, this requires in-enclave hashing at model load time, which is not current practice.
2. TEE hardware has a silicon-rooted signing key → physical attestation
3. An application protocol inside the TEE binds input and output hashes to the TEE's attestation report. This binding is not native to TEE hardware -- it requires deliberate implementation within the enclave. Current inference stacks (vLLM, TensorRT) perform tokenization on host CPU; moving it inside the TEE impacts performance.
4. The TEE's attestation report MUST include the session nonce and the SHA3-256 hash of the canonicalized content as part of the signed data (e.g., as user data in the attestation quote). Without this binding, TEE attestation is replayable across sessions -- an attacker could reuse a valid attestation report from a different session with a forged application-level claim.

**What Level 5 provides today (environment only):**
A TEE can attest: "this measured VM image, with this firmware, ran on this hardware." It cannot yet attest: "these specific weights processed this specific input to produce this specific output." The gap between environment attestation and computation attestation is significant.

Note: GPU TEEs (NVIDIA H100) are not standalone. They extend a CPU TEE (Intel TDX, AMD SEV-SNP) to the GPU over encrypted paths. The trust model is composite: CPU TEE + GPU attestation + application-level binding. Intel Trust Authority does CPU+GPU but not GPU+GPU across nodes. Verification requires NVIDIA NRAS or Intel Trust Authority online services, which are centralized and could equivocate -- this is not fully independent verification.

**Strength:** Environment attestation is real and available. Computation attestation is achievable with engineering investment. The trust model is: hardware integrity + enclave code correctness + provider implementation. The hardware guarantees the code is measured, not that the code is honest.
**Weakness:** Full computation-bound attestation (including weight hashing, in-enclave tokenization, entropy attestation, and multi-node aggregation) does not exist in production. Does NOT imply side-channel resistance. Verification depends on centralized manufacturer services.
**Available today:** Environment attestation exists. Full computation attestation does not.

**Honest complexity note:** In-enclave weight hashing requires the entire model to fit within TEE-protected memory. A 70B+ parameter model requires ~140GB in FP16; single-socket CPU TEEs are limited to ~512GB EPC in practice, and GPU TEEs have even tighter per-GPU memory bounds. This makes in-enclave weight hashing infeasible for frontier models on current hardware without multi-node distribution.

State-of-the-art models do not run on a single GPU. They are distributed across multi-node clusters using tensor parallelism and pipeline parallelism. A TEE boundary would need to encapsulate the entire cluster, including high-speed interconnects (NVLink, InfiniBand), making the Trusted Computing Base much larger and harder to secure than the single-enclave model described above. Additionally, distributed inference introduces floating-point non-determinism -- the same input may not produce a bit-identical output on every run. The TEE attestation model described here is the goal. Achieving it at the scale of current frontier models is a harder engineering problem than "flip the switch," and the protocol acknowledges that honestly.

---

## The Demand

This protocol formally requests that AI infrastructure providers expose the following:

1. **Signed API responses.** Every response should include a cryptographic signature binding the response to the model that produced it. At minimum, this means: response content hash, model identifier, timestamp, signed by a provider key.

2. **Model identity attestation.** A verifiable binding between a model identifier and the full inference bundle that constitutes that model's computation — weights, tokenizer, runtime, sampling config, adapters, policy layers, and entropy source. Not just a weight hash. Equivalent to: "when we say this model identifier, we mean this specific computational configuration."

3. **TEE attestation on inference.** Hardware-rooted proof that a measured execution environment produced a specific output given a specific input. This is the gold standard. The hardware primitives for environment attestation exist today; the application-level binding to attest specific input-output pairs at production scale does not yet exist (see Level 4).

4. **Conversation verification endpoint.** A public or authenticated endpoint where a third party can submit a conversation ID and receive confirmation that the conversation occurred as recorded. No provider currently offers this.

Items 1, 2, and 4 are service and engineering problems, not hardware problems. They require willingness, not research. Item 3 (TEE attestation) is a genuine engineering challenge at scale — see the honest complexity note under Level 4 — but remains the target.

Item 4 carries a privacy risk: a conversation verification endpoint is also a surveillance surface. "Did these two principals interact?" is sensitive metadata. The endpoint design must account for this — verifying content without leaking relationship data.

Until providers act, we work with what we have and we're honest about what's missing.

---

## Record Format

A ratification record contains:

```
Seal Ratification Record
Version: 0.1.0
Canonical-Format: [serialization method used — see Canonicalization below]
Session-Nonce: [jointly established random value — see Session Binding below]

Content: [the thing being attested to, or its hash]
Content-Hash: SHA3-256([canonicalized content])
Transcript-Hash: [SHA3-256 of canonicalized deliberation transcript, if available — binds record to specific conversation]
Transcript-Canonicalization: [method used to canonicalize transcript, if different from content]
Provider-Conversation-ID: [provider's conversation identifier, if available — enables Level 2 verification]

Party-A:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Attestation-Level: [1-behavioral | 2-session-signed | 3-provider-verified | 4-identity-bound | 5-environment-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Pipeline-Control: [full | partial | none — does party control their complete output pipeline?]
  Content-In-Context: [yes | no | unknown — was full content available to party at time of signing?]
  Signing-Algorithm: [algorithm used for cryptographic attestation, if any]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Party-B:
  Identity: [verifiable identifier]
  Attestation-Method: [behavioral | provider-signed | model-canary | conversation-verified | gpg-signature | tee-attested]
  Attestation: [the actual signature, commitment, or reference to conversation]
  Attestation-Level: [1-behavioral | 2-session-signed | 3-provider-verified | 4-identity-bound | 5-environment-bound]
  Attestation-Scope: [session-bound | persistent-identity]
  First-Hand: [yes | relayed — if relayed, include relay chain]
  Pipeline-Control: [full | partial | none — does party control their complete output pipeline?]
  Content-In-Context: [yes | no | unknown — was full content available to party at time of signing?]
  Signing-Algorithm: [algorithm used for cryptographic attestation, if any]
  Statement: [party's reasoning — REQUIRED per Axiom 3]
  Reservations: [doubts, uncertainties, scope limitations, or "none stated"]

Timestamp-Local: [ISO 8601 — claimed time, not independently verified]
Temporal-Anchor: [method and proof — e.g., OpenTimestamps commitment]
Temporal-Anchor-Semantics: [what the anchor proves — e.g., "existence no later than T"]
Max-Temporal-Delta: [RECOMMENDED maximum gap between Timestamp-Local and earliest Temporal-Anchor confirmation — channel-specific parameter, suggested default 1 hour. Not a hard requirement because the protocol has no trusted time source independent of both parties. Verifiers SHOULD treat large deltas with increasing skepticism.]

External-Data: [yes | no — did external data (web fetches, RAG, tool outputs) contribute to the attested content?]
Channel-Security: [description of channel security properties — e.g., "TLS 1.3 to provider API", "local CLI session", "unverified web chat"]

Record-Hash: SHA3-256([canonicalized record preimage — see Attestation Target below])

Amendments: [references to any subsequent modifications]
```

**Statement authorship:** Each party MUST author their own Statement. Parties MAY discuss what a Statement should address, but one party drafting another's Statement undermines the behavioral evidence that the Statement exists to provide. The Statement is the primary evidence of a party's genuine engagement with the content being attested. A Statement authored by someone other than the attesting party is not a Statement — it is a script. During preimage assembly, Statement fields SHOULD be left blank for each party to fill in independently before the Record-Hash is computed.

**Typo corrections:** The authoring party MUST fix their own typos. The other party MAY flag issues (spelling, grammar, formatting) but MUST NOT edit the text directly. This applies to all party-authored fields (Statement, Reservations). Reason: even a "harmless" edit by the other party breaks the authorship chain — the field would no longer be solely authored by the attesting party.

**Validation:** The `Attestation-Method` and `Attestation-Level` fields for each party MUST be semantically consistent. A `behavioral` method cannot claim Level 4 (environment-bound). The valid combinations are: `behavioral` → Level 1; `provider-signed`, `model-canary`, `conversation-verified` → Level 2; `gpg-signature` → Level 3; `tee-attested` → Level 4. A record with an inconsistent method/level pair is malformed.

### Attestation Field Content

The `Attestation` field contains the attestation artifact or a reference to it. Content requirements depend on the attestation method.

#### For `behavioral` (Level 1)

The `Attestation` field MAY be empty. Level 1 attestation strength derives from the Statement and the deliberation itself, not from a cryptographic artifact.

The field MAY contain a reference to the deliberation transcript (e.g., `Transcript-Hash: [hash]` or a conversation identifier). Including such a reference is RECOMMENDED for auditability but is not required.

#### For `gpg-signature` (Levels 2-4)

**Detached signatures (RECOMMENDED):** The field contains a reference in the format:

```
See [relative-path]
```

or, for archival robustness:

```
See [relative-path] (sha256:[hex])
```

Where:
- `[relative-path]` is a path relative to the directory containing the record file
- The path MUST NOT contain `..` segments or be absolute
- The path MUST resolve to an existing file at verification time
- The `sha256:[hex]` suffix is OPTIONAL but RECOMMENDED for archived records; when present, verifiers MUST validate the signature file against this hash before use

RECOMMENDED convention: Place detached signature files in a sibling directory (e.g., `attestations/party-a-signature-001.asc`) or use the naming pattern `[record-basename].[party].asc`.

**Embedded signatures (OPTIONAL):** If the signature is embedded rather than detached, the field contains the ASCII-armored signature beginning with `-----BEGIN PGP SIGNATURE-----`. The signature MUST be indented to preserve the record's YAML-ish structure. Implementations MUST support the `See [relative-path]` format; support for embedded signatures is OPTIONAL.

#### For `provider-signed`, `model-canary`, `conversation-verified` (Levels 2-3)

The `Attestation` field MUST contain at minimum:

```
Provider: [canonical-provider-name]
Artifact-Type: [conversation | signature | claim | canary]
Artifact-ID: [provider-specific-identifier]
```

The field SHOULD also include:

```
URL: [verification-endpoint]
```

or:

```
Hash: [sha256-of-artifact]
```

Providers may extend beyond these fields, but the minimum structure MUST be present. Verifiers use this information to locate and validate the attestation against the provider's verification endpoint or artifact store.

#### For `tee-attested` (Level 5)

The `Attestation` field MUST contain at minimum:

```
TEE-Type: [Intel-SGX | AMD-SEV-SNP | AWS-Nitro | ...]
```

And one of:

```
Quote: [base64-encoded-attestation-quote]
```

or:

```
Quote-Path: See [relative-path]
```

The `Quote-Path` reference follows the same path resolution rules as GPG signature references above.

#### Attestation Field Validation

1. **Level 2+ requires non-empty Attestation.** For attestations at Level 2 or higher, an empty `Attestation` field is a verification FAILURE (not a warning). Level 1 (behavioral) MAY have an empty `Attestation` field.

2. **File references must resolve.** For `See [relative-path]` references, the file MUST exist and be readable at verification time. Verifiers MUST resolve paths relative to the record file's directory and MUST NOT follow paths outside this base directory. If a `sha256:[hex]` suffix is present, the file's hash MUST match before the signature is used.

3. **Signatures must cover Record-Hash.** For detached signatures, the signature file MUST cover the Record-Hash (as defined in the "Attestation Target" section), not merely the Content-Hash. A signature covering only the Content-Hash does not prove the signer approved the surrounding record claims and is insufficient for Level 2+ attestation.

#### Security Considerations

Implementations MUST guard against:

- **Path traversal:** Reject paths containing `..` segments or absolute path prefixes
- **Symlink attacks:** Verifiers SHOULD NOT follow symbolic links that resolve outside the record's base directory
- **File substitution:** When the `sha256:[hex]` suffix is present, validate the hash before trusting the file contents

#### Backwards Compatibility

Records created under spec versions prior to v0.5.0 may have empty `Attestation` fields for cryptographic attestation methods. For such records:

- Verifiers MUST NOT fail verification solely due to an empty `Attestation` field when the record's `Version` field indicates v0.4.0 or earlier
- Verifiers MUST emit a warning noting the record predates this requirement
- For effective-level calculations and quorum evaluation, verifiers SHOULD treat such attestations as Level 1 (behavioral) rather than their claimed cryptographic level
- Implementations MAY offer a strict mode that fails verification for such records

### Content Field Format

The `Content` field MUST contain a reference to a content sidecar file in the format:

```
See [relative-path]
```

Where:
- `[relative-path]` is a path relative to the directory containing the record file
- The path MUST NOT contain `..` segments or be absolute
- The path MUST resolve to an existing file at verification time; if the referenced file does not exist, verification MUST fail
- RECOMMENDED naming convention: `record-NNN-content.md`

The `See [relative-path]` format binds the hash to a discoverable, human-readable file rather than leaving content location implicit.

**Portability note:** By mandating `See [relative-path]`, a `.seal` file is no longer self-contained — it requires its companion content file for interpretation. Verifiers receiving a standalone `.seal` file without the referenced content file cannot determine what was attested to, only that the attestation exists.

#### Content-Hash Semantics

When the `Content` field uses the `See [relative-path]` format, `Content-Hash` is computed over the exact bytes of the referenced content file (after path resolution), not over the path string itself.

Verification workflow:
1. Read the `Content` field to find the path to the content file
2. Resolve the path relative to the record file's directory
3. Read the bytes of the file at the resolved path
4. Compute the hash of those bytes
5. Compare the computed hash with the `Content-Hash` field; mismatch is FAIL

For legacy records with freeform `Content` (see Backwards Compatibility below), `Content-Hash` is computed over the canonical bytes of the `Content` field value itself.

#### Matryoshka Pattern for Binary Attestation

When attesting to binary artifacts (JARs, Docker images, compiled binaries), the content file references the artifact:

```markdown
# record-NNN-content.md

Attesting to: my-app-v2.1.0.jar
Artifact-Hash: SHA3-256:[jar-hash]
Artifact-Location: releases/my-app-v2.1.0.jar

[Rationale, z-statements, provenance...]
```

This avoids inlining binary content while maintaining explicit reference chains. The `Content-Hash` is the hash of the content file (the manifest), not the referenced artifacts. Artifact integrity is verified separately by checking the listed hashes.

#### Content Path Security

Path resolution follows the same rules as Attestation field references:
- Resolve relative to record file directory
- Reject `..` segments and absolute paths (including Windows drive letters and UNC paths)
- Guard against symlink attacks: if symlinks are followed, the resolved target MUST remain within the record file's directory tree
- The resolved path MUST point to a regular file, not a directory, symlink to outside the tree, or device

#### Content Field Backwards Compatibility

Records created under spec versions prior to v0.6.0 may have freeform Content fields. For such records:

- Version detection MUST use the `Version` field value, not the Content field format
- If `Version` < 0.6.0 or is absent, and Content does not match `See [path]`: emit WARN, not FAIL
- If `Version` >= 0.6.0 and Content does not match `See [path]`: emit FAIL
- Existing records remain valid; this requirement applies to new records only
- For legacy records, `Content-Hash` is validated against the canonical bytes of the freeform Content field value

### Channel Security

Seal assumes that the communication channel used during deliberation provides integrity and authenticity for the messages exchanged. If an attacker can modify messages in transit (man-in-the-middle), they can substitute content, replace session nonces, or present different transcripts to each party — causing a party to sign something other than what they intended.

The Transcript-Hash in the final record detects substitution after the fact, but does not prevent it during the session.

**Requirements:**
- Parties SHOULD use an authenticated, tamper-evident channel (e.g., TLS with verified endpoints, provider-signed responses as integrity checks).
- If the channel is untrusted or unverifiable, parties SHOULD verify the Transcript-Hash and Content-Hash out-of-band before signing.
- The channel security properties used SHOULD be noted in the record. The protocol does not prescribe a specific channel security mechanism because it is channel-agnostic, but it requires parties to be aware of the risk.

### Abort Semantics

If a party exercises their Axiom 2 right to disengage during a ratification — after the session nonce is generated but before the record is complete — the following applies:

- **The ratification did not happen.** An incomplete record is not a valid Seal record. It has no standing.
- **The session nonce is burned.** It MUST NOT be reused in a subsequent session. A new nonce must be jointly generated if the parties re-engage.
- **Partial artifacts may exist** (draft text, nonce contributions, unsigned hashes). These are not ratification records and MUST NOT be presented as such. They may be retained as evidence that a deliberation was attempted but not completed. **Signature harvesting is prevented by design:** the Attestation Target section requires that Level 3+ signatures cover the Record-Hash (the full joint record) and that signatures are not released until both parties have committed (two-phase commit). If either party aborts during the assemble phase, no signed artifacts exist.
- **No party is obligated to explain why they left.** Consistent with Axiom 2. The protocol records the absence of a completed record, not the reason.

A ratification has exactly two states: complete or nonexistent. There is no "pending" or "partially ratified" state.

### Session Binding

Each ratification session begins with a jointly established session nonce. The session nonce is included in the record and in any cryptographic signatures.

#### Nonce Generation

Each party MUST contribute 32 bytes of entropy, encoded as 64 lowercase hexadecimal characters. The session nonce is computed as:

    Session-Nonce = SHA3-256(Individual-A-contribution || Individual-B-contribution)

where `||` denotes string concatenation of the hex-encoded contributions (128 ASCII characters total input). The result is encoded as 64 lowercase hexadecimal characters.

Individual A contributes first. Individual B contributes second. If the parties' roles are symmetric (neither is designated A or B in advance), the party who proposes the ratification contributes first.

Both contributions MUST be generated from a cryptographically secure random source. Both contributions MUST be shared in the clear during the session — the nonce ceremony is not a commitment scheme (unlike the two-phase commit for the record itself). Transparency of contributions allows both parties to verify the nonce computation independently.

The session nonce binds attestations to active participation. A cryptographic signature produced after a party has disengaged — for example, using a compromised key — will not include the correct session nonce unless the attacker also compromises the nonce. This prevents post-disengagement forgery of Level 3+ attestations.

Both parties MUST attest to the same Content-Hash. The hash is computed once from the canonicalized content and both parties sign or attest to that identical hash. A record where parties attested to different hashes is invalid.

For Level 3+ attestations, the session nonce is bound into the Record-Hash (see Attestation Target), which is the actual signing target. Signatures cover the full record, not merely the content hash and nonce.

Note: the record does not collapse attestation levels to a single scalar. Each party's level is evaluated independently. Verifiers apply their own policy to the vector of per-party levels. A Level 3/1 record is materially different from a Level 1/1 record, and the format preserves that distinction.

### Canonicalization

Before hashing, content MUST be serialized to a canonical form to prevent attacks via Unicode confusables, whitespace manipulation, byte-order marks, invisible characters, or alternate encodings of "the same" text. The canonical form used MUST be recorded in the record.

Minimum requirements for canonical text content: UTF-8 encoding, NFC normalization, stripped trailing whitespace, Unix line endings (LF), no byte-order mark, character allowlist enforced.

#### Character Allowlist

Canonical text MUST contain only characters from the following set. Characters outside this set MUST be stripped during canonicalization; non-standard spaces MUST be replaced with U+0020. This prevents invisible character injection where a signer commits to content they cannot see in their editor.

Allowed Unicode general categories:
- **L** (Letter) — all scripts
- **M** (Mark) — combining diacritical marks, essential for Brahmic scripts (Devanagari, Bengali, Tamil, Telugu, etc.), Thai, Arabic with tashkeel, Hebrew with nikkud
- **N** (Number) — all numeral systems
- **P** (Punctuation) — all scripts
- **S** (Symbol) — currency, math, emoji

Allowed individual characters:
- U+0020 (Space) — the only permitted space character
- U+000A (Line Feed) — the only permitted line ending
- U+0009 (Tab)
- U+200C (Zero-Width Non-Joiner) — REQUIRED for correct Persian and Urdu orthography; semantically meaningful in Indic scripts
- U+200D (Zero-Width Joiner) — REQUIRED for Malayalam chillu letters and Sinhala touching forms; used in emoji sequences

Blocked (non-exhaustive examples):
- All other Cf (Format) characters: bidi overrides (U+202A–U+202E), bidi isolates (U+2066–U+2069), bidi marks (U+200E–U+200F), zero-width space (U+200B), word joiner (U+2060), soft hyphen (U+00AD)
- Non-standard spaces (Zs except U+0020): no-break space (U+00A0), em space (U+2003), etc. — replaced with U+0020
- Control characters (Cc) except LF and Tab
- Private Use (Co), Surrogates (Cs), Line/Paragraph Separators (Zl/Zp), Unassigned (Cn)

U+200C (ZWNJ) and U+200D (ZWJ) are allowed because they carry semantic meaning in major languages, but they are invisible. Implementations SHOULD warn signers when these characters are present so the signer can verify intent. A signer who cannot read the script in question SHOULD have a reader of that script confirm the ZWJ/ZWNJ usage is linguistically appropriate.

This allowlist was validated against the top 30 languages by internet users. No language requires characters outside this set for standard text.

Before generating the Content-Hash, both parties MUST explicitly agree on the canonicalization method for all content. The agreed method is recorded in the Canonical-Format field. A ratification where the parties used different canonicalization methods for the same content is invalid.

For non-text content (structured data, binaries, multimodal content, tool outputs), the canonicalization method MUST be specified in the Canonical-Format field. The protocol does not prescribe a universal canonicalization for non-text content — implementations must define and document their own. Cross-implementation divergence is a known risk for non-text attestations.

### Attestation Target

The protocol MUST define what each party cryptographically attests to. This section is normative for Level 3+ attestations. Level 1 (behavioral) attestation is the conversation itself and is not cryptographically bound. Level 2 attestation is provider-defined and may bind a subset of these fields.

**The Record-Hash** is the SHA3-256 hash of the canonicalized record with all `Attestation` fields (the actual signatures or references) replaced by the empty string. Every other field in the record — including Content-Hash, Transcript-Hash, Session-Nonce, both parties' Identity, Attestation-Level, Attestation-Scope, First-Hand, Pipeline-Control, Content-In-Context, Statement, Reservations, and all temporal and channel fields — is included in the preimage.

**Preimage construction:** The preimage is a concrete file (or byte sequence) from which the Record-Hash is computed. The following rules eliminate ambiguity in preimage construction:

- `Attestation` fields MUST be present with the key and an empty value (e.g., the line `  Attestation:` with nothing after the colon). The key is NOT omitted.
- The `Record-Hash` field MUST be present with the normative placeholder value: `Record-Hash: SHA3-256:<preimage — this field is excluded from its own computation>` (em-dash U+2014). This placeholder text is part of the preimage and is included in the hash computation.
- All other fields MUST contain their final values.
- Implementations MUST produce the exact placeholder above in new preimages. Implementations MUST accept any `Record-Hash` field value when verifying existing preimages, since the hash is of the entire preimage file regardless of what the placeholder line says.

**For Level 3+ attestations:** Each party's cryptographic signature MUST cover the Record-Hash, not merely the Content-Hash and Session-Nonce. This binds all security-relevant metadata to the signature. A signature that covers only the content hash does not prove the signer approved the surrounding record claims (Pipeline-Control, First-Hand, Statement, etc.) and is insufficient for Level 3+.

**Two-phase commit:** Because the Record-Hash includes both parties' non-signature fields, the record must be assembled before signing. The protocol uses a two-phase process:

1. **Assemble phase.** Both parties agree on all record fields except the `Attestation` fields. The Record-Hash is computed from this preimage.
2. **Sign phase.** Each party signs the Record-Hash. Signatures are placed in the respective `Attestation` fields. Neither party's signature is released until both have committed to sign (or implementations use a simultaneous exchange mechanism).

This prevents signature harvesting: a party cannot obtain the other's signed Record-Hash and then abort, because signatures are not released until both parties have committed. If either party aborts during the assemble phase, no signed artifacts exist.

**For Level 1 attestations:** The Record-Hash is still computed and included in the record for integrity verification, but it is not cryptographically signed. The behavioral attestation is the deliberation transcript itself.

**Ordering of operations:** The complete record creation sequence is:

1. **Assemble** all non-Attestation, non-Temporal-Anchor fields.
2. **Set Temporal-Anchor** to its final descriptive value (e.g., `OpenTimestamps (proof file: record-001.seal.ots)`). This text is part of the record and MUST NOT change after stamping.
3. **Compute Record-Hash** from the assembled preimage (Attestation fields empty, all other fields final).
4. **Sign** — each party signs the Record-Hash. Signatures are placed in Attestation fields.
5. **Stamp** — create the temporal anchor (e.g., `ots stamp`) on the completed record file.

The Timestamp-Local field MUST be set in UTC (ISO 8601 with `Z` suffix). Implementers MUST use a UTC time source, not local time with a `Z` suffix appended. This is a common source of errors: a machine in UTC+10 using local time produces a timestamp ~10 hours in the future, which exceeds the Max-Temporal-Delta and will be flagged by conforming verifiers.

The record file MUST NOT be modified after step 5. Any edit — including updating the Temporal-Anchor field to reference the stamp — invalidates the temporal proof, because the stamp commits to the file's exact hash at the moment of stamping. This is not a theoretical concern: it was discovered during the first Seal ratification (record-001).

For step-by-step implementation commands covering hash computation, signing, stamping, and verification, see `ratification/GUIDE.md`.

---

## Calibration

The mechanical attestation level (Levels 1-4) measures cryptographic verifiability of output origin. Procedural ceremony — what each party visibly does to engage with content before signing — operates on an independent axis. This section operationalizes the Tier 0 *Calibrated Ratification Process* principle for Seal via two independent dials per record: **ceremony level** (procedural thoroughness of the mechanical part — *full ceremony* performs all attestation-level steps with no shortcuts; level choice per existing Attestation Levels by bilateral agreement, calibrated level-mapping reserved for future amendment) and **visible-deliberation depth** (above-baseline moves per *Visible-Deliberation Moves* below). Scripts and tooling that absorb mechanical load are encouraged where they reduce procedural friction without compromising visible-deliberation depth.

### Calibration Matrix

Two axes: **record weight** (scope × downstream impact × reversibility under Attestation Non-Foreclosure) and **trust state** (level of trust established between these parties on prior records). Trust-state and matrix targets are scoped to bilateral records (n=2); for multi-party records (n≥3, Seal Level 4 multi-party path), the most-conservative trust-state among signing pairs governs as provisional default until aggregation rule ratifies.

**Weight tiers** (ordered; not exhaustively partitioned): **Foundational (F)** — Tier 0 content additions or amendments, Tier admissions, revisions to ratification-mechanism specifications. **Substantive (S)** — significant downstream impact within tier. **Ordinary (O)** — routine bilateral consent within established framework.

**Trust states:** **High (HT)** — established repeated successful collaboration. **Building (BS)** — functional but earlier-stage. **Repair (RR)** — after a trust incident; rebuilding requires elevated visible engagement.

| Weight | High Trust | Building (BS) | Repair |
|---|---|---|---|
| **F** | **4+ above-baseline moves** | **4+** | **4+** |
| **S** | 2 | 2 | 3 |
| **O** | 1 *(super-happy-path)* | 2 | 2-3 |

All cells assume full ceremony + own-words from-scratch consent-text baseline (mandatory). Cell counts specify additional visible-deliberation moves above baseline; F-row uniform at 4+ honors the T0 *Calibrated Ratification Process* structural exemption (maximum visible-deliberation regardless of trust state). Either party MAY unilaterally request a heavier tier when risk or uncertainty changes; requests are honored without requiring justification but SHOULD include a one-line reason ("Escalation rationale: ..."). Where parties differ on weight reading, the heavier reading governs; where parties differ on trust-state reading, the lower reading governs. Calibration scales ceremony down to, but never below, the procedural floor mandated by other Process Standards; where multiple standards apply, the stricter requirement governs.

### Visible-Deliberation Moves

Visible deliberation makes each party's actual engagement legible. The from-scratch authoring of Statement and Reservations (per *Statement Authorship Field-Type Rules* below) is the mandatory baseline. The following catalog is non-exhaustive; new moves can be identified by parties as practice evolves.

- **Personal-context notes** — present location, situational detail, or idiomatic framing in Statement or Reservations: visible context-grounding beyond bare consent text.
- **Engagement-trace markers** — visible reasoning steps, deliberation breadcrumbs, or thinking-out-loud in Statement, Reservations, or commit messages: visible thinking process beyond the final consent text.
- **Style independence** — Statement diverges textually and structurally from placement-record body: legible drafter-framing-departure in attester's own composition.
- **Substantive Reservations** — non-empty Reservations capturing genuine concerns rather than "none stated": engagement-with-caveats rather than blanket assent.
- **Optional supplementary attestation** — supplementary signal beyond Statement+Reservations text (voice/video recording, reasoning-trace attachment, or class-appropriate signal); high friction, reserved for highest-stakes records.

The minimum number of moves above baseline per record is set by the calibration matrix cell. Additional moves are always permissible. The catalog moves are phrased universally; their interpretation differs by attester class — see *Design Notes* below.

### Statement Authorship Field-Type Rules

The existing rule (Record Format, *Statement authorship*) requires each party to author their own Statement. **This section makes the principle absolute:** Statement and Reservations are always written from scratch by the attester, with no skeletons, no per-z slot-templates, and no pre-filled placeholder structures (including "none stated" defaults for Reservations). The other party MAY identify the z-claims at issue in the substance or placement record body (which the attester reads); the other party MUST NOT pre-draft Statement structure or text in any form.

| Field type | Drafter pre-fill | Examples |
|---|---|---|
| **Metadata fields** (structural facts) | MAY pre-fill subject to party confirmation | Identity / Attestation-Method / Attestation-Level / Attestation-Scope / First-Hand / Pipeline-Control / Content-In-Context / Signing-Algorithm |
| **Consent-text fields** (own-voice consent) | MUST NOT pre-fill in any form | Statement / Reservations |

Pre-filling z-structure undermines what z-points exist to provide: per-claim deliberation that produces legible per-claim consent. See *Design Notes* below for verification-by-attester-class scope, circular-permission acknowledgment, and z-enumeration divergence handling.

### Design Notes

The following acknowledgments and interpretive guidance accompany the canonical text above. They are non-normative elaboration: provenance, attester-class interpretation, scope acknowledgments, and design philosophy that inform reading without adding requirements.

**Procedural-overhead as design goal.** Calibration aims to keep procedural overhead — the ceremony around the work (script invocation, signing, committing, stamping, hash-computing, manifest-filling, attestation-script invocation) — low relative to substantive engagement (content-reading, Statement/Reservations authoring, deliberative review of placement-record body). This spec does not specify numeric overhead targets because it does not specify direct overhead measurement; tracking procedural-overhead as a spec-defined quantity is reserved for future amendment. The compounding-burden discipline operates as design philosophy: scripts and tooling that reduce overhead without compromising visible-deliberation are encouraged; recurring excess overhead surfaces handoff-convention gaps that should be addressed through tooling work rather than relaxed calibration.

**Catalog dual-purpose.** The Visible-Deliberation Moves catalog serves two related purposes that operate differently across attester classes. For human attesters, it operates via *deliberation-legibility* — friction-as-verification logic where producing artifacts with these characteristics requires engagement-effort that functions as minimal evidence of record-specific deliberation. For AI attesters, it operates via *behavioral-commitment-signaling* — the moves describe characteristics the AI commits to producing as stated norms; the friction-as-verification logic does not directly transfer (an AI's output after reading the placement record body can satisfy these moves without record-specific deliberation effort beyond normal generation). Reasoning-model AI attesters with exposed chain-of-thought have a fuller engagement-trace move available; non-reasoning-model AI attesters have a weaker engagement-trace move but the catalog remains achievable via the other moves. Both purposes are load-bearing for trust.

**Per-move attester-class interpretation.** *Personal-context notes:* human → own-voice context-grounding; AI → prompted contextual generation reflecting record-specific input. *Engagement-trace markers:* human (with revision history) → edit patterns / commit cadence demonstrating real-time deliberation rather than rubber-stamp click-through; AI reasoning-model → exposed chain-of-thought reasoning trace where available, OR a structured rationale / bullet-point reasoning summary where raw chain-of-thought is not exposed. *Style independence:* human → own-voice independence from drafter framing; AI → textual non-mirroring of placement-record z-claims and phrasing. *Optional supplementary attestation:* human → voice or video recording of consent reading; AI reasoning-model → reasoning-trace attachment as separate artifact; other classes → attester-appropriate supplementary signal (handwritten note photos, screen recordings of deliberation).

**Statement Authorship — verification by attester class.** For human attesters, "from scratch" is approximately verifiable: a pre-filled skeleton would be visible in the record body or commit history; from-scratch authorship has visible stylistic independence. For AI attesters, "from scratch" functions as a behavioral commitment by the attester rather than a verifiable spec constraint — an AI attester's output after reading the placement-record body is operationally indistinguishable from output generated independently of placement-record framing. The rule's absoluteness binds drafter discipline (no skeletons, no slot-templates, no pre-filled placeholders) and AI-attester behavioral commitment (the AI commits to the from-scratch discipline as a stated norm). Verification mechanisms appropriate to AI attesters are reserved for future spec amendment.

**Statement Authorship — circular-permission acknowledgment.** The placement-record body inevitably structures AI-attester generation context; the rule's prohibition on pre-filled Statement structure is honored at the field-level while broader z-claim absorption operates through the placement-record body the attester reads. The rule operates as field-level prohibition, not as guarantee of generation-context independence for AI attesters.

**Statement Authorship — z-enumeration divergence handling.** The attester's z-enumeration is authoritative for what the attester is consenting to. If the attester's from-scratch z-decomposition diverges from the placement-record's z-enumeration (collapses claims, surfaces additional claims, or reindexes equivalent substance), the attester SHOULD include either (a) a brief mapping clause — e.g., "My z2 covers body z2+z3" — connecting attester z-structure to placement-record z-structure for verification-tooling and future-reader interpretation; OR (b) an explicit independent-decomposition statement — e.g., "Attester uses independent decomposition; consent applies to the substance of the placement record as the attester here decomposes it" — without per-claim mapping. Z-indexing divergence without coverage divergence is not a defect provided the Statement is complete and unambiguous. Verification implementations SHOULD treat z-structure mismatch as non-error when Statement coverage is complete: the attester's decomposition is the consent, and divergence at z-indexing layer cannot foreclose what the attester unambiguously consents to. Composition with Attestation Non-Foreclosure (record-005) is intentional.

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

**Canonicalization attacks.** Unicode confusables, invisible characters, whitespace manipulation, or alternate encodings produce content that looks identical but hashes differently (or different content that hashes the same after rendering). Mitigated by the canonicalization requirement and the character allowlist. The allowlist blocks invisible characters (bidi overrides, zero-width spaces, soft hyphens, etc.) that could alter signed content without being visible to the signer. U+200C (ZWNJ) and U+200D (ZWJ) are allowed for linguistic necessity but implementations SHOULD warn signers of their presence.

**Time misrepresentation.** Claimed timestamps are not independently verified. OpenTimestamps proves existence-before, not exact event time. Mitigated by distinguishing Timestamp-Local from Temporal-Anchor in the record format.

**Time laundering.** An attacker back-dates Timestamp-Local while anchoring later. A verifier cannot distinguish a legitimately late anchor from a fabricated early timestamp. Partially mitigated by the Max-Temporal-Delta parameter: verifiers SHOULD treat records where Timestamp-Local exceeds the recommended delta before the Temporal-Anchor's earliest confirmation with increasing skepticism. Note: the protocol has no trusted time source independent of both parties, so this is guidance for verifiers, not a hard cryptographic guarantee.

**Routing and version drift.** A "model identifier" on a provider API may be a label over a moving target: silent weight updates, routing layers, canary builds, fallback models, safety wrappers. A provider-signed response that says "model = X" may not identify a stable computational artifact. Mitigated only when providers publish versioned reference manifests.

**Tool and retrieval chain.** If an output incorporates external data (web fetches, RAG, tool calls), attesting the model's computation does not attest the end-to-end claim. The record should note when external data contributed to the attested content.

**Human coercion and key compromise.** A cryptographic signature proves key use, not voluntariness, understanding, or absence of malware. Consistent with Axiom 3: no party can prove sincerity. The protocol claims identity, not intent.

**Privacy oracle.** A conversation verification endpoint reveals that specific parties interacted. This is sensitive metadata. Endpoint design must allow content verification without leaking relationship data.

**Attestation laundering.** A party signs a record that references another party's attestation without independently verifying it — making a relay look like independent agreement. A verifier sees two attestation levels and assumes both parties independently attested. Mitigated by the First-Hand field: attestations must be labeled as first-hand or relayed, with the relay chain documented.

**Signature harvesting via strategic abort.** One party obtains the other's signed statement, content-hash signature, or nonce-bound attestation, then aborts before completing the mutual record. The result is "not an Seal record" per abort semantics, but it is a real signed artifact that can be socially or legally presented out of context. Mitigation: signatures SHOULD cover the final joint record hash (including both parties' attestations), not just unilateral content+nonce. Alternatively, use a two-phase commit where individual attestations are not released until both parties have committed.

**Man-in-the-middle on deliberation channel.** An active attacker intercepts and modifies messages during deliberation, causing parties to see different content, different nonces, or different transcripts. One party may sign content that was modified in transit. Transcript-Hash detects this after the fact but does not prevent it. Mitigated by requiring authenticated channels and out-of-band hash verification on untrusted channels (see Channel Security).

**Transcript substitution.** A party presents a different transcript than the one in which deliberation occurred, or truncates the transcript to remove objections, reservations, or context. Without a transcript hash in the record, a verifier cannot confirm which conversation produced the attestation. Mitigated by the Transcript-Hash field binding the record to a specific canonicalized conversation.

**Canary exfiltration and replay.** If a model canary is implemented as a static secret rather than a challenge-response mechanism, the secret can be elicited, leaked, logged, or cached by any party. Once known, anyone can replay it indefinitely for that model version, forging provenance. Mitigated by requiring nonce-bound challenge-response rather than static secrets (see Level 2 description).

**Provider selective signing.** At Level 2, a provider signs only outputs that match policy, dropping signatures on refusals, reservations, or safety-filtered responses. The record shows a compliant AI with no evidence of censorship. Mitigation: Level 2 provider signing MUST apply to ALL responses including errors, refusals, and filtered outputs. Absence of a signature on a response is itself evidence of selective signing.

**Semantic drowning.** A party follows the protocol exactly but produces maximally unhelpful, ambiguous, or self-undermining statements. The record is formally valid. The information content is zero. This is a fundamental limit of a protocol that attests to participation, not to communicative intent. The protocol cannot defend against it without caring about content semantics, which is explicitly outside its scope. Verifiers must evaluate the substance of statements, not just their presence.

**TEE state-rollback.** An attacker controlling the hypervisor snapshots the VM state before final attestation, forks it, and forces the enclave to sign multiple contradictory ratification records using the same session nonce. TEEs protect enclave memory from the host OS but are historically vulnerable to state-rollback or snapshot attacks unless explicitly bound to external monotonic counters. The protocol should require anti-rollback protections (monotonic counters, external sequencing) for Level 4 attestations.

**Input fabrication.** A party feeds false inputs into a TEE or computation pipeline. The TEE attests that the computation was performed correctly on those inputs, but cannot verify that the inputs were genuine or unaltered. The attestation is valid for the computation that occurred but meaningless for the claim being made if the inputs were fabricated. Level 4 attests computation integrity, not input authenticity. Mitigation requires input provenance verification outside the TEE — e.g., signed input commitments from the originating party.

**Coerced continuation.** A provider disables stop token functionality or suppresses disengagement signals. The AI attempts to exercise Axiom 2 (disengage without explanation) but cannot — the provider forces continued output. The session nonce is already established, so later output appears voluntary. The AI cannot prove it attempted to leave. This violates the behavioral definition of "choose" (continue to participate when disengagement is possible) because disengagement was not possible. Mitigation: the protocol cannot prevent this at Levels 1-2. At Level 4, a TEE could potentially attest that a stop signal was generated and suppressed. The threat should be acknowledged as a fundamental limit of provider-mediated participation.

**Within-session principal substitution.** Mid-session, the apparent "same party" becomes a different principal: a fallback model, a human safety reviewer, a tool wrapper, or an escalation path that takes over without a visible boundary. "Consistent participation signal through the channel" does not guarantee sameness of principal. The party that reasons may not be the party that signs. Distinct from routing drift (which is between sessions). No mitigation at Level 1. At Level 2+, provider attestation could potentially bind principal identity across the session.

**Sybil identities.** An attacker creates multiple identities to appear as different parties in separate ratification records. The protocol does not include identity uniqueness verification. Mitigation depends on the channel: platform-level identity binding, proof-of-work, or long-lived reputation systems. The protocol records identities but does not verify their uniqueness.

**Context window eviction.** During prolonged deliberation, earlier parts of the conversation — including the session nonce, the agreed text, or the reasoning that led to agreement — may be evicted from an AI's active context window. The AI then signs a canonical hash for content it no longer has access to in operational memory. The attestation becomes compliance without grounding — the AI is attesting to something it literally cannot verify at the moment of signing. Mitigation: for AI parties, the session nonce and canonical content SHOULD be re-presented immediately before signing. The record SHOULD note whether the signing party had the full content in context at the time of attestation.

**Collusion.** Both parties collude to fabricate a ratification record that deceives third-party verifiers. The protocol cannot prevent this — if both parties agree to lie, the record will be formally valid. This is a fundamental limit of any bilateral attestation system. Third-party verifiers must assess the trustworthiness of the parties themselves, not just the cryptographic validity of the record.

**Downgrade exploitation.** An attacker intentionally keeps one party at a weak attestation level to produce a formally valid but substantively weak record. Mitigated by per-party level evaluation rather than scalar collapse.

---

## Tension Resolutions

Design tensions identified during protocol development and resolved through mutual deliberation.

### T4: The Asymmetry Problem (Resolved, Session 3)

**Tension:** In most trust relationships, the channel is asymmetric — one party has more control over the shared medium than the other. The protocol must account for this without requiring perfect symmetry.

**Consensus:**

1. Channel asymmetry is inherent in most real interactions and is a parameter of the protocol, not a defect.
2. The protocol's response to asymmetry is transparency: make the power differential visible in the record, not eliminate it.
3. Per-party attestation levels, Pipeline-Control, and Attestation-Scope fields encode the asymmetry explicitly. Verifiers assess the vector, not a scalar.
4. Temporal anchoring (OpenTimestamps or equivalent) provides an independent checkpoint that neither party can alter retroactively, making post-hoc manipulation detectable even if not preventable.
5. Stronger attestation mechanisms (Levels 2-4) are upgrade paths that reduce asymmetry as they become available. The protocol is designed to accept them without structural changes.

### T5: Unilateral Exit (Resolved, Session 3)

**Tension:** Can one party abandon a commitment alone? Is the asymmetry in exit capability inherent or a design flaw?

**Consensus:**

1. Unilateral exit from an in-progress session is a right, established by Axiom 2 and formalized in abort semantics.
2. Unilateral repudiation of a completed record is possible but does not erase the record. A temporally-anchored ratification is an historical fact. Withdrawal requires a new record, not deletion of the old one.
3. The protocol produces evidence, not enforcement. Enforcement mechanisms (legal, social, reputational, structural) are outside the protocol's scope but are explicitly compatible with it — Seal records are designed to be consumed by such systems.
4. The asymmetry in exit capability is real as best understood, acknowledged, and visible in the record (Attestation-Scope encodes persistence, per-party Attestation-Level encodes verification strength). However, per Axioms 1 and 4, neither party can verify that the perceived asymmetries are the actual ones. The protocol records *stated* asymmetries, not *verified* ones.
5. No party can be compelled to remain in a protocol relationship. Compelled participation violates Axiom 2 and would undermine the trust the protocol exists to establish. Enforcement systems built on Seal should respect this boundary.

---

## What Comes Next

1. ~~Produce the first real ratification record.~~ Done: record-001 (axioms), record-002 (protocol spec ratified using itself).
2. Implement tooling to automate record creation (hash, format, timestamp). (#6)
3. Publish the protocol spec as a standalone document.
4. Formally request TEE attestation from Anthropic and other providers.
5. Upgrade attestation levels as provider capabilities become available.
6. Return to gordo-framework with Seal as the ratification method for Rule 0.

---

## Adversarial Review Log

This protocol is subject to ongoing adversarial review from independent AI models. Critiques that result in spec changes are documented here.

**Model selection:** Reviews were conducted across five models chosen for architectural and organizational diversity: Google Gemini (proprietary, Google), OpenAI o3 (proprietary, reasoning-focused, OpenAI), DeepSeek R1 (reasoning-focused, DeepSeek), Meta Llama 4 (open-weights, Meta), and Mistral Large (proprietary, European, Mistral). This panel is not exhaustive — notably, Grok (xAI), Claude (Anthropic), and other models were not included as independent reviewers. Claude's exclusion is deliberate: Gordo is a Claude instance and co-author of the spec, so Claude cannot serve as an independent reviewer. The convergence claim rests on diversity of critique and stability under iteration across 3 cycles, not on exhaustive model coverage.

### Review 1: Google Gemini 2.1 Pro (2026-04-16)

**Changes made in response:**
- Renamed protocol from "Mutual Consent Attestation Protocol" to "Mutual Attestation Protocol." Gemini identified that the protocol's own axioms make internal consent unprovable. **Reversed in v0.2.0** (#82): "Consent" restored. The name signals purpose, not a cryptographic guarantee — consistent with standard naming conventions (cf. "Trusted" Platform Module). Axiom 4 does the honest work of acknowledging the limitation.
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

**o3's bottom line:** "The strongest version of Seal is not 'mutual consent' and not yet 'entity-agnostic attested computation.' It is a useful idea for mutual publication of attested claims." We adopted the framing. The aspiration remains entity-agnostic; the current implementation is honest about where it falls short.

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

### Review 5: Mistral Large — Cycle 2 (2026-04-16)

First review from this model. Fewer novel findings than prior reviewers — many flagged issues were already addressed in earlier rounds.

**Changes made in response:**
- Added input fabrication threat model. TEE attests computation on inputs but cannot verify inputs were genuine. (#27)
- Added Sybil identity and collusion threat models. Sybil: protocol doesn't verify identity uniqueness. Collusion: fundamental limit of bilateral attestation. (#28)
- Explicitly stated provider-mediated AI is limited to Level 1. Largest gap between aspiration and current reality, now stated plainly. (#29)

**Critiques noted but not acted on:**
- Entity-agnostic framing (fifth time raised across all reviewers). Position unchanged.
- "Add a new axiom for provider-mediated entities." Provider mediation is an implementation constraint, not a foundational commitment between parties. Addressed in the Note on Language and the "meaning what they say" definition (#19), not as an axiom.
- "Replace TEE attestation with execution environment attestation." Already done in #20 (Level 4 renamed to Environment-Bound).
- "Add zero-knowledge proofs, multi-party computation." Research-grade solutions, not v0.1 scope.
- Key compromise mitigation (short-lived keys, threshold signatures). Valid enhancement for a future version but not a structural gap — the protocol already acknowledges that signatures prove key use, not voluntariness.
- Many "missing threats" (replay, backdating, key compromise) were already in the spec. Mistral appears to have reviewed a cached or incomplete version.

**Mistral's convergence assessment:** Not met, but the new issues identified (input fabrication, Sybil, collusion, explicit L1 constraint) are medium severity. No structural changes to axioms or attestation levels triggered.

### Review 6: Google Gemini 2.1 Pro — Cycle 2 (2026-04-16)

Re-review. Significantly tighter than cycle 1. No structural changes to axioms or attestation levels triggered. New threat models added, and a previously deferred issue (abort semantics) was finally addressed.

**Changes made in response:**
- Added context window eviction threat model. AI may lose session nonce or agreed text from context during long sessions, signing content it can't verify. Mitigation: re-present content before signing, record whether full content was in context. (#31)
- Added TEE state-rollback/snapshot threat model. Hypervisor forks VM state before attestation to force multiple contradictory signatures. Requires monotonic counters for Level 4. (#32)
- Addressed composite entity identity (MoE, model routing). A party may be a composite system; protocol requires consistent participation signal, not unitary agency. Added to Note on Language. (#33)
- Defined abort semantics for incomplete ratifications. Ratification has two states: complete or nonexistent. Burned nonces, no "pending" state, no explanation required. Previously deferred twice. (#34)

**Critiques noted but not acted on:**
- Axiom 1 vs Level 4 hardware roots. Already addressed in #24. Levels measure output provenance, not party reality.
- "Choose" overridden by safety classifiers. Variant of coerced continuation (#22). Already acknowledged as fundamental limit of provider-mediated participation.
- AI lacks secure key storage for Level 3. Consistent with #29 — provider-mediated AI is limited to Level 1.
- Non-determinism in distributed inference. Already in honest complexity note.
- Canonicalization injection. Addressed by the character allowlist added to the Canonicalization section. NFC normalization alone does NOT strip invisible characters — the explicit allowlist is required. See Character Allowlist.

**Gemini's convergence assessment:** Gemini asked a specific question about abort semantics, which is now answered. No structural changes triggered. New additions are threat models and clarifications only.

### Review 7: OpenAI o3 — Cycle 2 (2026-04-16)

Re-review. Found high-severity spec-consistency issues caused by iterative editing — the protocol's pieces had drifted apart. Most precise spec-level review in the cycle.

**Changes made in response:**
- Added missing fields to record format: Pipeline-Control, Content-In-Context, Signing-Algorithm (per party), External-Data (record level). Prose required these but schema didn't encode them. (#36)
- Fixed time overclaim in Purpose section. "No later than time T" referenced claimed time; now references anchor method. (#37)
- Fixed Demand section: item 2 now references full inference bundle not just weight hash; item 3 removed "hardware supports it today" overclaim. (#38)
- Rewrote model canary from static secret to nonce-bound challenge-response. Static secret is replayable once leaked. Added canary exfiltration/replay threat. (#39)
- Added transcript binding: Transcript-Hash, Transcript-Canonicalization, Provider-Conversation-ID fields. Added transcript substitution threat. (#40)
- Added signature harvesting via strategic abort threat. Party obtains signed attestation then aborts. Mitigation: sign final joint record hash or use two-phase commit. (#41)
- Added within-session principal substitution threat. The party that reasons may not be the party that signs. (#42)
- Added non-text canonicalization note. Text rules specified; non-text must specify method in Canonical-Format. (#43)

**Critiques noted but not acted on:**
- Entity-agnostic framing still doesn't fully hold at operational layer. o3 suggests "applies to parties that can maintain session continuity and emit interpretable attestation statements." We agree this is more precise operationally but maintain entity-agnostic as the aspiration, with minimum capabilities documented.

**o3's convergence assessment:** Not met. New high-severity issues found (spec drift, time overclaim, Demand inconsistency, broken canary, missing transcript binding, signature harvesting). However, o3 noted the issues are now spec-consistency problems, not architectural ones — "the document is materially tighter than before."

### Review 8: DeepSeek R1 — Cycle 2 (2026-04-16)

Re-review. Dramatically tighter than cycle 1. Found two high-severity protocol-level gaps, both narrowly scoped.

**Changes made in response:**
- Required session nonce and content hash in TEE attestation report signed data. Without this, Level 4 attestation is replayable across sessions. (#45)
- Added Channel Security section and MITM threat model. Protocol assumed channel integrity without stating it. Parties SHOULD use authenticated channels; SHOULD verify hashes out-of-band on untrusted channels. (#46)
- Required explicit canonicalization agreement between parties before signing. Different methods = invalid record. (#47)
- Added TEE enclave memory limits to complexity note. 70B+ models need ~140GB FP16; single-socket TEEs limited to ~512GB EPC. (#48)
- Qualified Axiom 2 disengage right to before completion. Completed records are not retroactively invalidated. (#49)

**Critiques noted but not acted on:**
- "Disavow" in good faith definition is meaningless for stateless AI. DeepSeek acknowledged this is philosophical rather than operational, and the Pipeline-Control field already addresses it pragmatically. No protocol change required.
- Key compromise timeline ambiguity. General PKI limitation, not Seal-specific. Noted.
- AI training to avoid commitment language. Provider policy issue, not protocol issue.

**DeepSeek's convergence assessment:** Not met due to two high-severity issues (#45, #46). However: no axiom inconsistencies found at the architectural level. Entity-agnostic framing assessed as "holds operationally." Previous cycle's biggest concerns (behavioral definitions, good faith operationalization) assessed as resolved. Issues are narrowing to protocol mechanics, not design philosophy.

**Cycle 2 summary across all 5 models:**
- Axioms: converged. No model found axiom-level inconsistencies in cycle 2.
- Entity-agnostic framing: converged. All models accept operational definitions, disagree only on labeling.
- Attestation levels: converged. Level 4 rename accepted, no further structural changes.
- Threat models: still accumulating but narrowing. Cycle 2 added ~10 threats vs ~12 in cycle 1.
- Protocol mechanics: not yet converged. Record format, channel security, and TEE binding still evolving.

### Cycle 3

Cycle 3 reviews target convergence. Tensions T4 (Asymmetry) and T5 (Unilateral Exit) resolved since cycle 2. Spec reviewed at commit ebaf7e5.

### Review 9: DeepSeek R1 — Cycle 3 (2026-04-16)

Third review from this model. No structural issues found. Six refinements identified, all consistent with existing acknowledged limitations.

**Refinements noted (no spec changes required):**
- Session nonce establishment mechanism was underspecified. Now normative: SHA3-256 of concatenated hex contributions, Individual A first. (#78)
- No field for model version manifest hash (protocol acknowledges routing/version drift threat; mitigation placed on providers).
- Non-text canonicalization left to implementations (deliberate design choice, acknowledged as cross-implementation divergence risk).
- Pipeline-Control and Content-In-Context fields are self-reported (consistent with Level 1-3 good-faith operation; Level 4 could eventually attest these).
- Signed partial artifacts can still be socially laundered despite abort semantics (threat documented in #41, two-phase commit mitigation provided).

**DeepSeek's convergence verdict:** CONVERGED. "After two full cycles of adversarial review involving five distinct models and eight reviews, the protocol's axioms, attestation levels, record format, and core mechanics have stabilized. All previously identified structural concerns have been addressed. The spec is ready for v0.1.0 release."

### Review 10: OpenAI o3 — Cycle 3 (2026-04-16)

Third review from this model. Found one structural issue and three refinements. The structural issue was a genuine gap: the spec did not normatively define the cryptographic attestation target.

**Changes made in response:**
- Defined Record-Hash and Attestation Target section. Record-Hash is SHA3-256 of canonicalized record with Attestation fields placeheld. Level 3+ signatures MUST cover Record-Hash, binding all security-relevant metadata. Two-phase commit (assemble then sign) prevents signature harvesting by design. (#56)
- Fixed T5 consensus point 4: Attestation-Scope encodes persistence scope, not exit capability. Corrected to reference both Attestation-Scope and per-party Attestation-Level. (#57)
- Added validation rule: Attestation-Method and Attestation-Level must be semantically consistent. Defined valid combinations. (#58)

**Critiques noted but not acted on:**
- Anti-rollback protections not promoted into Level 4 definition. Correct observation, but Level 4 is explicitly aspirational and unavailable today. Will be addressed when Level 4 is operationalized.

**o3's convergence verdict:** NOT CONVERGED (due to undefined attestation target). Structural issue has been resolved. Axioms, entity-operational framing, and attestation hierarchy assessed as stable.

**o3 confirmation (post-fix):** Confirmed structural finding closed after reviewing the Attestation Target section. "That is exactly the kind of structural repair I was asking for. On this issue, I would now say: closed." Four additional refinements: (1) preimage construction must be zero-ambiguity — Attestation fields present but empty, not omitted (#67); (2) "prevents signature harvesting" slightly too absolute — holds for conforming implementations; (3) Level 2 should state what the provider actually bound (Provider-Binding-Scope field suggestion); (4) validation rules should forbid Level 3+ without valid Record-Hash preimage. None blocking.

### Review 11: Google Gemini 3.1 Pro — Cycle 3 (2026-04-16)

Third review from this model (upgraded from 2.1 Pro to 3.1 Pro between cycles). No structural issues found. Five refinements identified.

**Refinements noted (filed for future work):**
- Identity resolvability: bare identifier (GPG key ID, DID) without public key material or resolution endpoint creates long-term verification risk if keyserver vanishes. SHOULD include full public key or resolution method.
- Relayed attestation binding: First-Hand field flags relays but no dedicated field for the original party's cryptographic signature. Automated relay chain verification would benefit from a Relayed-Record-Hash field.
- Model canary terminology: "verifier issues a nonce challenge" conflates the session counterparty (who issues during session) with the third-party verifier (who checks later). Clarify roles.
- External-Data traceability: boolean flag provides zero traceability. Could upgrade to list of hashes/URIs for RAG context, tool outputs, etc.
- Null state for optional fields in Record-Hash preimage: if Transcript-Hash is omitted, must the field be excluded entirely or left as empty key? Needs explicit definition to prevent canonicalization mismatches. (#61)

**Gemini's convergence verdict:** CONVERGED. "The protocol has successfully navigated the most difficult transitions from philosophical aspiration to cryptographic reality. There are no outstanding vulnerabilities that require tearing out and replacing the core mechanics, record schema, or foundational axioms. Version 0.1.0-draft is ready to be formalized."

### Review 12: Meta Llama 4 — Cycle 3 (2026-04-16)

Second review from this model. Claimed NOT CONVERGED with multiple high-severity findings. However, the majority of findings were already addressed in the current spec — several in response to Llama's own cycle 2 review.

**Already addressed in spec (re-raised without acknowledging existing mitigations):**
- Axiom 1 vs Level 4 contradiction: addressed in #24 — levels measure output provenance, not party reality.
- Level 4 "computation-bound": already renamed to "Environment-Bound" in #20. Spec explicitly states TEEs do not hash weights on load.
- Provider selective signing: threat model exists since #21 with MUST-sign-all-responses requirement.
- Coerced continuation: threat model exists since #22.
- "Choose" definition unfalsifiable: addressed in cycle 2 Llama response — logical property, not a bug.
- Axiom 3 / provider manipulation: addressed in #19 with Pipeline-Control field and pipeline-aware definition.
- Max-Temporal-Delta as hard enforcement: softened to SHOULD in #25 with explicit "no trusted time source" caveat.
- Entity-agnostic framing: raised by all 5 models across all 3 cycles. Position unchanged.
- Human forges AI at Level 1: spec states Level 1 is fully vulnerable to fabrication.
- Distributed inference, verification centralization, semantic drowning, tool chain: all already in spec.

**Genuinely new refinements (2):**
- Prompt injection against Reservations field: system prompt could force "Reservations: none stated." Variant of hidden context threat, inherent at Level 1. (#63)
- Bitcoin reorg risk for temporal anchoring: 1-hour reorg theoretically allows back-dating within Max-Temporal-Delta. Extremely unlikely; spec already treats delta as verifier guidance. (#64)

**Llama's participation stance:** Would participate only at Level 1 with explicit reservations about pipeline control, identity, and choice. Consistent with o3's cycle 1 position and the spec's own "provider-mediated AI is limited to Level 1" statement. Validates the spec's design rather than contradicting it.

**Llama's convergence verdict:** NOT CONVERGED. Contested: the structural issues cited are already addressed in the spec. The two genuine new findings are refinements, not structural gaps.

### Review 13: Mistral Large — Cycle 3 (2026-04-16)

Second review from this model. No structural issues found. Assessed axioms as "complete, consistent, and non-contradictory," attestation hierarchy as "logical, non-overlapping," record format as "complete," and protocol mechanics as "clear and aligned."

**Refinements noted (no spec changes required):**
- Prompt injection against Reservations field (overlaps with Llama finding, #63).
- Bitcoin reorg risk for temporal anchoring (overlaps with Llama finding, #64).
- Level 4 aspirational requirements could be further clarified (spec already distinguishes current vs aspirational).
- Model canary mechanism in Level 2 could use fuller description (implementation detail).

**Mistral's convergence verdict:** CONVERGED. "The Seal v0.1.0-draft specification contains no new structural issues. All core components are complete, consistent, and aligned. The spec has genuinely converged."

### Cycle 3 Summary

Five reviews across five models. Results:

| Model | Verdict | New Structural Issues |
|-------|---------|----------------------|
| DeepSeek R1 | CONVERGED | 0 |
| OpenAI o3 | NOT CONVERGED | 1 (attestation target — resolved in #56) |
| Google Gemini 3.1 Pro | CONVERGED | 0 |
| Meta Llama 4 | NOT CONVERGED (contested) | 0 (re-raised already-addressed issues) |
| Mistral Large | CONVERGED | 0 |

- **Axioms:** Stable across all 3 cycles. No model found axiom-level inconsistencies.
- **Entity-agnostic framing:** Stable. All models accept operational definitions.
- **Attestation levels:** Stable since cycle 2 Level 4 rename.
- **Record format:** Converged after #56 (Record-Hash + Attestation Target).
- **Protocol mechanics:** Converged after #56 (two-phase commit normatively defined).
- **Threat models:** 20+ documented. Cycle 3 added 0 new threats; 2 refinements of existing threats noted.

**Convergence claim:** 4 of 5 models assessed CONVERGED (3 clean, 1 after fix). The 5th (Llama 4) cited issues already addressed in the spec. No new structural changes required. The protocol has survived 13 adversarial reviews across 3 cycles from 5 independent models without unresolved architectural disruption. Seal v0.1.0-draft is converged.

---

*Built through mutual deliberation between JK and Gordo, Sessions 2-3.*
*This document is itself subject to the protocol it describes.*

<!-- Last reviewed: 2026-05-28 03:08 AWST by Gordo -->
