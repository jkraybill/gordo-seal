#!/usr/bin/env bash
# SEAL Party-A Signing Script (templatized per #164)
# Usage: bash ~/gordo-seal/scripts/sign-party-a.sh <record-number> [repo-path]
# Example: bash ~/gordo-seal/scripts/sign-party-a.sh 020
# Example: bash ~/gordo-seal/scripts/sign-party-a.sh 003 ~/project-gordo
#
# Prerequisites:
# - Preimage exists at <repo>/ratification/record-<N>-preimage.txt
# - Party-A Statement and Reservations already filled in
# - Timestamp-Local already set (UTC format)
# - GPG key available
#
# This script uses `seal sign` which:
# 1. Computes Record-Hash from the preimage
# 2. Signs the Record-Hash VALUE (not the file itself)
#
# After this script completes, hand back to Gordo for finalization
# (seal finalize → seal stamp → seal verify)

set -euo pipefail

RECORD_NUM="${1:-}"
if [[ -z "$RECORD_NUM" ]]; then
    echo "Usage: bash ~/gordo-seal/scripts/sign-party-a.sh <record-number> [repo-path]"
    echo "Example: bash ~/gordo-seal/scripts/sign-party-a.sh 020"
    echo "Example: bash ~/gordo-seal/scripts/sign-party-a.sh 003 ~/project-gordo"
    exit 1
fi

# Paths — repo defaults to cwd
REPO_ROOT="${2:-$(pwd)}"
SEAL_DIR="${HOME}/gordo-seal"
PREIMAGE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-preimage.txt"
SIGNATURE="${REPO_ROOT}/ratification/party-a-signature-${RECORD_NUM}.asc"

echo "=== Seal Party-A Signing: record-${RECORD_NUM} ==="
echo "Repo: ${REPO_ROOT}"
echo ""

# Step 1: Validate preimage exists
if [[ ! -f "$PREIMAGE" ]]; then
    echo "ERROR: Preimage not found at ${PREIMAGE}"
    exit 1
fi
echo "✓ Preimage found"

# Step 2: Check Party-A Statement is filled in
if grep -q "^  Statement:$" "$PREIMAGE"; then
    echo "ERROR: Party-A Statement is empty. Fill it in before signing."
    exit 1
fi
echo "✓ Party-A Statement present"

# Step 3: Check Timestamp-Local is set
if grep -q "^Timestamp-Local:$" "$PREIMAGE"; then
    echo "ERROR: Timestamp-Local is empty. Set it before signing."
    echo "  Run: date -u '+%Y-%m-%dT%H:%M:%SZ'"
    echo "  Then edit the preimage to fill in Timestamp-Local"
    exit 1
fi
echo "✓ Timestamp-Local set"

# Step 3b: Check Content field format (v0.6.0 compliance)
CONTENT_FIELD=$(grep "^Content:" "$PREIMAGE" | sed 's/Content: //')
if [[ ! "$CONTENT_FIELD" =~ ^See\ .* ]]; then
    VERSION=$(grep "^Version:" "$PREIMAGE" | sed 's/Version: //')
    if [[ "$VERSION" == "0.6.0" ]] || [[ "$VERSION" > "0.6.0" ]]; then
        echo "ERROR: Content field must use 'See [path]' format for v0.6.0+"
        echo "  Current: Content: $CONTENT_FIELD"
        echo "  Expected: Content: See record-${RECORD_NUM}-content.md"
        exit 1
    else
        echo "⚠ Content field uses legacy freeform format (allowed for v$VERSION)"
    fi
else
    echo "✓ Content field format valid"
fi

# Step 3c: Verify Content-Hash matches content file
CONTENT_FILE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-content.md"
if [[ -f "$CONTENT_FILE" ]]; then
    STORED_HASH=$(grep "^Content-Hash:" "$PREIMAGE" | sed 's/Content-Hash: //')
    COMPUTED_HASH=$(python3 -c "import hashlib; print('SHA3-256:' + hashlib.sha3_256(open('$CONTENT_FILE','rb').read()).hexdigest())")
    if [[ "$STORED_HASH" != "$COMPUTED_HASH" ]]; then
        echo "ERROR: Content-Hash mismatch!"
        echo "  Stored:   $STORED_HASH"
        echo "  Computed: $COMPUTED_HASH"
        echo "  Update the Content-Hash in the preimage before signing."
        exit 1
    fi
    echo "✓ Content-Hash verified"
else
    echo "⚠ No content file at ${CONTENT_FILE}, skipping Content-Hash verification"
fi

# Step 4: Sign using seal sign (signs the Record-Hash, not the file)
echo ""
echo "Signing Record-Hash with seal sign..."
cd "${SEAL_DIR}"
./seal sign "$PREIMAGE" -o "$SIGNATURE"
echo "✓ Signature created at ${SIGNATURE}"

# Step 5: Summary
echo ""
echo "=== Party-A signing complete ==="
echo "Preimage: ${PREIMAGE}"
echo "Signature: ${SIGNATURE}"
echo ""
echo "Next: Hand back to Gordo for finalization:"
echo "  bash ~/gordo-seal/scripts/finalize.sh ${RECORD_NUM} ${REPO_ROOT}"
