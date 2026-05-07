#!/usr/bin/env bash
# MCAP Party-A Signing Script (templatized per #164)
# Usage: bash ~/mcap-protocol/scripts/sign-party-a.sh <record-number> [repo-path]
# Example: bash ~/mcap-protocol/scripts/sign-party-a.sh 020
# Example: bash ~/mcap-protocol/scripts/sign-party-a.sh 003 ~/project-gordo
#
# Prerequisites:
# - Preimage exists at <repo>/ratification/record-<N>-preimage.txt
# - Party-A Statement and Reservations already filled in
# - GPG key available (fingerprint ending 74269E1ED0FCE0B0)
#
# This script does:
# 1. Validates preimage exists and has Party-A Statement filled in
# 2. Signs the preimage with GPG
# 3. Verifies the signature
#
# After this script completes, hand back to Gordo for finalization
# (timestamp, record hash, stamp, verify, rename to .mcap)

set -euo pipefail

RECORD_NUM="${1:-}"
if [[ -z "$RECORD_NUM" ]]; then
    echo "Usage: bash ~/mcap-protocol/scripts/sign-party-a.sh <record-number> [repo-path]"
    echo "Example: bash ~/mcap-protocol/scripts/sign-party-a.sh 020"
    echo "Example: bash ~/mcap-protocol/scripts/sign-party-a.sh 003 ~/project-gordo"
    exit 1
fi

# Paths — repo defaults to cwd
REPO_ROOT="${2:-$(pwd)}"
PREIMAGE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-preimage.txt"
SIGNATURE="${REPO_ROOT}/ratification/party-a-signature-${RECORD_NUM}.asc"

echo "=== MCAP Party-A Signing: record-${RECORD_NUM} ==="
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

# Step 3: Sign with GPG
echo ""
echo "Signing preimage with GPG..."
gpg --armor --detach-sign -o "$SIGNATURE" "$PREIMAGE"
echo "✓ Signature created at ${SIGNATURE}"

# Step 4: Verify signature
echo ""
echo "Verifying signature..."
gpg --verify "$SIGNATURE" "$PREIMAGE"
echo ""
echo "✓ Signature verified"

# Step 5: Summary
echo ""
echo "=== Party-A signing complete ==="
echo "Preimage: ${PREIMAGE}"
echo "Signature: ${SIGNATURE}"
echo ""
echo "Next: Hand back to Gordo for finalization (timestamp, record hash, stamp, verify, rename to .mcap)"
