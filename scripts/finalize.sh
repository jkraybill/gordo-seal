#!/usr/bin/env bash
# MCAP Finalization Script (templatized per #164)
# Usage: bash ~/mcap-protocol/scripts/finalize.sh <record-number>
# Example: bash ~/mcap-protocol/scripts/finalize.sh 020
#
# Prerequisites:
# - Preimage exists at ratification/record-<N>-preimage.txt
# - Party-A signature exists at ratification/party-a-signature-<N>.asc
# - Timestamp-Local is empty (will be filled by this script)
# - Record-Hash is empty (will be filled by this script)
#
# This script does:
# 1. Validates preimage and signature exist
# 2. Sets Timestamp-Local to current UTC time
# 3. Computes and sets Record-Hash
# 4. Renames preimage to .mcap
# 5. Runs mcap stamp (with --force for cosmetic verifier quirk)
# 6. Runs mcap verify

set -euo pipefail

RECORD_NUM="${1:-}"
if [[ -z "$RECORD_NUM" ]]; then
    echo "Usage: bash ~/mcap-protocol/scripts/finalize.sh <record-number>"
    echo "Example: bash ~/mcap-protocol/scripts/finalize.sh 020"
    exit 1
fi

# Paths
REPO_ROOT="${HOME}/project-gordo-backchannel"
PREIMAGE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-preimage.txt"
SIGNATURE="${REPO_ROOT}/ratification/party-a-signature-${RECORD_NUM}.asc"
MCAP_FILE="${REPO_ROOT}/ratification/record-${RECORD_NUM}.mcap"
OTS_FILE="${MCAP_FILE}.ots"

echo "=== MCAP Finalization: record-${RECORD_NUM} ==="
echo ""

# Step 1: Validate files exist
if [[ ! -f "$PREIMAGE" ]]; then
    echo "ERROR: Preimage not found at ${PREIMAGE}"
    exit 1
fi
echo "✓ Preimage found"

if [[ ! -f "$SIGNATURE" ]]; then
    echo "ERROR: Party-A signature not found at ${SIGNATURE}"
    echo "  Run: bash ~/mcap-protocol/scripts/sign-party-a.sh ${RECORD_NUM}"
    exit 1
fi
echo "✓ Party-A signature found"

# Step 2: Set Timestamp-Local
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
echo ""
echo "Setting Timestamp-Local to: ${TIMESTAMP}"

# Use sed to replace empty Timestamp-Local
if grep -q "^Timestamp-Local:$" "$PREIMAGE"; then
    sed -i "s/^Timestamp-Local:$/Timestamp-Local: ${TIMESTAMP}/" "$PREIMAGE"
    echo "✓ Timestamp-Local set"
elif grep -q "^Timestamp-Local: " "$PREIMAGE"; then
    echo "! Timestamp-Local already set, skipping"
else
    echo "ERROR: Timestamp-Local field not found in preimage"
    exit 1
fi

# Step 3: Compute and set Record-Hash
echo ""
echo "Computing Record-Hash..."
RECORD_HASH=$(cat "$PREIMAGE" | openssl dgst -sha3-256 | awk '{print $2}')
echo "Record-Hash: SHA3-256:${RECORD_HASH}"

if grep -q "^Record-Hash:$" "$PREIMAGE"; then
    sed -i "s/^Record-Hash:$/Record-Hash: SHA3-256:${RECORD_HASH}/" "$PREIMAGE"
    echo "✓ Record-Hash set"
elif grep -q "^Record-Hash: $" "$PREIMAGE"; then
    # Handle case where there's a trailing space
    sed -i "s/^Record-Hash: $/Record-Hash: SHA3-256:${RECORD_HASH}/" "$PREIMAGE"
    echo "✓ Record-Hash set"
else
    echo "! Record-Hash field already has value or not found"
    echo "  Current value: $(grep '^Record-Hash:' "$PREIMAGE")"
fi

# Step 4: Rename to .mcap
echo ""
echo "Renaming preimage to .mcap..."
mv "$PREIMAGE" "$MCAP_FILE"
echo "✓ Renamed to ${MCAP_FILE}"

# Step 5: Run mcap stamp
echo ""
echo "Running mcap stamp..."
cd "${HOME}/mcap-protocol"
node dist/mcap.js stamp "$MCAP_FILE" --force
echo "✓ mcap stamp complete"

# Step 6: Run mcap verify
echo ""
echo "Running mcap verify..."
node dist/mcap.js verify "$MCAP_FILE"

# Step 7: Summary
echo ""
echo "=== Finalization complete ==="
echo "MCAP file: ${MCAP_FILE}"
echo "OTS file: ${OTS_FILE}"
echo ""
echo "Next: git add, commit, push"
