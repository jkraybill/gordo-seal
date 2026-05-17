# Seal Ratification Record: Implementation Guide

Step-by-step commands for creating, signing, verifying, and stamping MCAP ratification records. All commands assume you are in the repository root.

See `spec/protocol.md` for the normative specification. This guide is a companion for implementers.

---

## Prerequisites

- Python 3 with `hashlib` (SHA3-256 support)
- GnuPG (`gpg`) for Level 3 identity-bound attestation
- OpenTimestamps CLI (`ots`) for temporal anchoring
- `git` for version control

---

## Record Creation Sequence

The spec defines a strict ordering (spec/protocol.md, "Ordering of operations"):

1. **Assemble** all non-Attestation, non-Temporal-Anchor fields
2. **Set Temporal-Anchor** to its final descriptive value
3. **Compute Record-Hash** from the assembled preimage
4. **Sign** — each party signs the Record-Hash
5. **Stamp** — create the temporal anchor on the completed record file

**The record file MUST NOT be modified after step 5.** Any edit invalidates the temporal proof.

---

## Step 1: Generate Timestamp-Local (UTC)

The Timestamp-Local field MUST be in UTC (ISO 8601 with `Z` suffix). This is the most common source of errors.

```bash
# Correct: UTC time
date -u +%Y-%m-%dT%H:%M:%SZ
# Example output: 2026-04-16T03:01:00Z

# WRONG: local time — do NOT use without conversion
date +%Y-%m-%dT%H:%M:%SZ   # This outputs local time with a Z suffix!
```

**Pitfall:** `date` without `-u` returns local time. Appending `Z` to local time produces an incorrect UTC timestamp. On a machine in AEST (UTC+10), this results in a timestamp ~10 hours in the future.

**Verification:** Compare against a known UTC source:
```bash
# Cross-check: these should agree within seconds
date -u +%Y-%m-%dT%H:%M:%SZ
python3 -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
```

---

## Step 2: Compute Content-Hash

The Content-Hash covers the canonicalized content being attested to.

```bash
# For a single file:
python3 -c "
import hashlib
with open('path/to/content.md', 'rb') as f:
    print('SHA3-256:' + hashlib.sha3_256(f.read()).hexdigest())
"

# For concatenated files (e.g., foundations.md + protocol.md):
python3 -c "
import hashlib
h = hashlib.sha3_256()
for path in ['spec/foundations.md', 'spec/protocol.md']:
    with open(path, 'rb') as f:
        h.update(f.read())
print('SHA3-256:' + h.hexdigest())
"
```

**Verify canonicalization** before hashing:
```bash
python3 -c "
with open('path/to/content.md', 'rb') as f:
    data = f.read()
print(f'BOM: {data[:3] == b\"\xef\xbb\xbf\"}')     # Must be False
print(f'CR bytes: {data.count(b\"\r\")}')             # Must be 0
lines = data.decode('utf-8').split('\n')
trailing = [i+1 for i, l in enumerate(lines) if l != l.rstrip()]
print(f'Lines with trailing whitespace: {trailing}')  # Must be empty
"
```

---

## Step 3: Assemble the Preimage

The preimage is the full record with:
- All `Attestation:` fields **present but empty** (the key exists, the value is blank)
- `Record-Hash:` field contains a placeholder (excluded from its own computation)

Save as `ratification/record-NNN-preimage.txt`.

**Verify the preimage is canonical:**
```bash
python3 -c "
with open('ratification/record-NNN-preimage.txt', 'rb') as f:
    data = f.read()
print(f'Size: {len(data)} bytes')
print(f'BOM: {data[:3] == b\"\xef\xbb\xbf\"}')
print(f'CR: {b\"\r\" in data}')
print(f'Ends with LF: {data[-1:] == b\"\n\"}')
lines = data.decode('utf-8').split('\n')
trailing = [i+1 for i, l in enumerate(lines) if l != l.rstrip()]
print(f'Trailing whitespace on lines: {trailing}')
"
```

---

## Step 4: Compute Record-Hash

```bash
python3 -c "
import hashlib
with open('ratification/record-NNN-preimage.txt', 'rb') as f:
    data = f.read()
print('SHA3-256:' + hashlib.sha3_256(data).hexdigest())
"
```

Place this value in the `Record-Hash:` field of the final record (not the preimage — the preimage retains its placeholder).

---

## Step 5: GPG Sign the Record-Hash (Level 3)

The `seal sign` command computes the Record-Hash from the preimage and invokes GPG clearsign in one step, with GPG_TTY handling built in:

```bash
./seal sign ratification/record-NNN-preimage.txt -o ratification/party-a-signature-NNN.asc
```

To verify the signature:
```bash
gpg --verify ratification/party-a-signature-NNN.asc
```

Update the final record's `Attestation:` field to reference the signature file:
```
Attestation: See ratification/party-a-signature-NNN.asc
```

---

## Step 6: Create Temporal Anchor (OpenTimestamps)

```bash
ots stamp ratification/record-NNN.seal
```

This creates `ratification/record-NNN.seal.ots`. **Do not modify the .seal file after this point.**

**Verify the stamp later** (after Bitcoin confirmation, typically hours):
```bash
ots verify ratification/record-NNN.seal.ots
```

---

## Full Verification Checklist

Run these commands to verify an existing record:

```bash
# 1. Verify Content-Hash matches content
python3 -c "
import hashlib
h = hashlib.sha3_256()
for path in ['spec/foundations.md', 'spec/protocol.md']:  # adjust paths per record
    with open(path, 'rb') as f:
        h.update(f.read())
computed = 'SHA3-256:' + h.hexdigest()
print(f'Computed: {computed}')
# Compare against Content-Hash in the record
"

# 2. Verify Record-Hash matches preimage
python3 -c "
import hashlib
with open('ratification/record-NNN-preimage.txt', 'rb') as f:
    data = f.read()
computed = 'SHA3-256:' + hashlib.sha3_256(data).hexdigest()
print(f'Computed: {computed}')
# Compare against Record-Hash in the final record
"

# 3. Verify GPG signature
gpg --verify ratification/party-a-signature-NNN.asc

# 4. Verify signed hash matches Record-Hash
# The clearsigned message body should equal the Record-Hash hex value

# 5. Verify OTS timestamp
ots verify ratification/record-NNN.seal.ots

# 6. Verify Timestamp-Local is plausible
# Compare Timestamp-Local against:
#   - Git commit timestamp: git log --format='%aI' -1 COMMIT_HASH
#   - OTS anchor time (from ots verify output)
#   - Max-Temporal-Delta (default 1 hour)
```

---

## Cross-Record References

When one MCAP record references z-statements from another record (common in two-layer ratification scenarios), use qualified references:

- **Same-repo:** `r###/z#` (e.g., `r015/z1`)
- **Cross-repo:** `<repo>/r###/z#` (e.g., `project-gordo-backchannel/r025/z1`)

Use full repo names (no aliases) for grep-ability and self-documentation.

**Example labeling note:**
> The amendments below use labels from Layer-1 substance record project-gordo-backchannel/r025 (z1 through z13). Convention: same-repo references use `r###/z#`; cross-repo references use `<repo>/r###/z#`.

---

## Common Pitfalls

### Timezone errors
The `Z` suffix in ISO 8601 means UTC. Always use `date -u` or equivalent. Local time with a `Z` suffix is wrong and will produce a Timestamp-Local that fails Max-Temporal-Delta verification.

### Modifying files after OTS stamping
`ots stamp` commits to the file's exact SHA-256 hash. Any edit — even adding a newline — invalidates the proof. The spec's ordering of operations (assemble, hash, sign, stamp) exists to prevent this.

### Preimage vs. final record confusion
The preimage has empty Attestation fields and a Record-Hash placeholder. The final record has filled Attestation fields and the actual Record-Hash. The Record-Hash is computed from the *preimage*, not the final record.

### GPG "Inappropriate ioctl for device"
GPG needs a TTY to prompt for the passphrase. When signing from piped input (`echo ... | gpg --clearsign`), the TTY association can be lost. Run `export GPG_TTY=$(tty)` before signing. This is a one-time per-shell fix — add it to your shell profile to avoid hitting it repeatedly.

### Content-Hash computed on wrong file version
Content-Hash must reference a specific commit. Verify you are hashing the files at the correct commit:
```bash
git show COMMIT:spec/foundations.md | python3 -c "
import sys, hashlib
print(hashlib.sha3_256(sys.stdin.buffer.read()).hexdigest())
"
```

---

*Part of gordo-seal. See spec/protocol.md for the normative specification.*
