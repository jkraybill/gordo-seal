# record-007: Attestation Field Content Requirements

**Class:** Spec Amendment (protocol.md)
**Origin:** gordo-seal #86, Roundtable R1 (4/4 consensus)

---

## Rationale

The v0.4.0 spec says `Attestation: [the actual signature, commitment, or reference to conversation]` but does not specify concrete formats per attestation method. This ambiguity led to an implementation gap where all 38+ ratification records have empty Attestation fields despite the spec implying they should be populated.

The spec also says "Detached signatures are RECOMMENDED" (line 132), creating apparent tension with "signatures are placed in the respective Attestation fields" (line 414). This amendment resolves that tension by specifying that references to detached signature files satisfy the requirement.

Roundtable review (4/4 consensus) identified four paramount findings that have been integrated: path convention for file references, minimum structure for provider-signed attestations, security considerations, and TEE format requirements.

---

## z-Statements

### z1. Add "Attestation Field Content" subsection to spec/protocol.md

**Location:** Insert after line 308 (end of "Statement authorship" paragraph), before "Channel Security" section.

**Text to insert:**

> ### Attestation Field Content
>
> The `Attestation` field contains the attestation artifact or a reference to it. Content requirements depend on the attestation method.
>
> #### For `behavioral` (Level 1)
>
> The `Attestation` field MAY be empty. Level 1 attestation strength derives from the Statement and the deliberation itself, not from a cryptographic artifact.
>
> The field MAY contain a reference to the deliberation transcript (e.g., `Transcript-Hash: <hash>` or a conversation identifier). Including such a reference is RECOMMENDED for auditability but is not required.
>
> #### For `gpg-signature` (Levels 2-4)
>
> **Detached signatures (RECOMMENDED):** The field contains a reference in the format:
>
> `See <relative-path>`
>
> or, for archival robustness:
>
> `See <relative-path> (sha256:<hex>)`
>
> Where:
> - `<relative-path>` is a path relative to the directory containing the record file
> - The path MUST NOT contain `..` segments or be absolute
> - The path MUST resolve to an existing file at verification time
> - The `sha256:<hex>` suffix is OPTIONAL but RECOMMENDED for archived records; when present, verifiers MUST validate the signature file against this hash before use
>
> RECOMMENDED convention: Place detached signature files in a sibling directory (e.g., `attestations/party-a-signature-001.asc`) or use the naming pattern `<record-basename>.<party>.asc`.
>
> **Embedded signatures (OPTIONAL):** If the signature is embedded rather than detached, the field contains the ASCII-armored signature beginning with `-----BEGIN PGP SIGNATURE-----`. The signature MUST be indented to preserve the record's YAML-ish structure. Implementations MUST support the `See <relative-path>` format; support for embedded signatures is OPTIONAL.
>
> #### For `provider-signed`, `model-canary`, `conversation-verified` (Levels 2-3)
>
> The `Attestation` field MUST contain at minimum:
>
> - `Provider: <canonical-provider-name>`
> - `Artifact-Type: <conversation | signature | claim | canary>`
> - `Artifact-ID: <provider-specific-identifier>`
>
> The field SHOULD also include:
>
> - `URL: <verification-endpoint>`
>
> or:
>
> - `Hash: <sha256-of-artifact>`
>
> Providers may extend beyond these fields, but the minimum structure MUST be present. Verifiers use this information to locate and validate the attestation against the provider's verification endpoint or artifact store.
>
> #### For `tee-attested` (Level 5)
>
> The `Attestation` field MUST contain at minimum:
>
> - `TEE-Type: <Intel-SGX | AMD-SEV-SNP | AWS-Nitro | ...>`
>
> And one of:
>
> - `Quote: <base64-encoded-attestation-quote>`
>
> or:
>
> - `Quote-Path: See <relative-path>`
>
> The `Quote-Path` reference follows the same path resolution rules as GPG signature references above.

---

### z2. Add validation rules to spec/protocol.md

**Location:** Insert after the new "Attestation Field Content" subsection from z1, before "Channel Security" section.

**Text to insert:**

> ### Attestation Field Validation
>
> 1. **Level 2+ requires non-empty Attestation.** For attestations at Level 2 or higher, an empty `Attestation` field is a verification FAILURE (not a warning). Level 1 (behavioral) MAY have an empty `Attestation` field.
>
> 2. **File references must resolve.** For `See <relative-path>` references, the file MUST exist and be readable at verification time. Verifiers MUST resolve paths relative to the record file's directory and MUST NOT follow paths outside this base directory. If a `sha256:<hex>` suffix is present, the file's hash MUST match before the signature is used.
>
> 3. **Signatures must cover Record-Hash.** For detached signatures, the signature file MUST cover the Record-Hash (as defined in the "Attestation Target" section), not merely the Content-Hash. A signature covering only the Content-Hash does not prove the signer approved the surrounding record claims and is insufficient for Level 2+ attestation.
>
> #### Security Considerations
>
> Implementations MUST guard against:
>
> - **Path traversal:** Reject paths containing `..` segments or absolute path prefixes
> - **Symlink attacks:** Verifiers SHOULD NOT follow symbolic links that resolve outside the record's base directory
> - **File substitution:** When the `sha256:<hex>` suffix is present, validate the hash before trusting the file contents

---

### z3. Add backwards compatibility note to spec/protocol.md

**Location:** Insert after the validation rules from z2, before "Channel Security" section.

**Text to insert:**

> ### Backwards Compatibility (Attestation Field)
>
> Records created under spec versions prior to v0.5.0 may have empty `Attestation` fields for cryptographic attestation methods. For such records:
>
> - Verifiers MUST NOT fail verification solely due to an empty `Attestation` field when the record's `Version` field indicates v0.4.0 or earlier
> - Verifiers MUST emit a warning noting the record predates this requirement
> - For effective-level calculations and quorum evaluation, verifiers SHOULD treat such attestations as Level 1 (behavioral) rather than their claimed cryptographic level
> - Implementations MAY offer a strict mode that fails verification for such records

---

## Provenance

- **Origin issue:** gordo-seal #85 (S254 discovery)
- **Decomposition:** gordo-seal #86 (spec amendment), #87 (implementation, blocked)
- **Roundtable:** 2026-05-15 S255, DeepSeek-R1 + Gemini-2.5-Pro + GPT-5 + Claude Sonnet 4.6
- **Consensus:** 4/4 revision required; P1-P4 findings integrated
- **Working docs:** `gordo-roundtable/reviews/86-attestation-field-spec/`
