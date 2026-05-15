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
# (mcap finalize → mcap stamp → mcap verify)

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

echo "=== MCAP Party-A Signing: record-${RECORD_NUM} ==="
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

# Step 4: Sign using mcap sign (signs the Record-Hash, not the file)
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
