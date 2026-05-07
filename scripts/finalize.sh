#!/usr/bin/env bash
# MCAP Finalization Script (templatized per #164)
# Usage: bash ~/mcap-protocol/scripts/finalize.sh <record-number> [repo-path]
# Example: bash ~/mcap-protocol/scripts/finalize.sh 020
# Example: bash ~/mcap-protocol/scripts/finalize.sh 003 ~/project-gordo
#
# Prerequisites:
# - Preimage exists at <repo>/ratification/record-<N>-preimage.txt
# - Party-A signature exists at <repo>/ratification/party-a-signature-<N>.asc
# - Timestamp-Local is set in preimage
#
# This script:
# 1. Validates preimage and signature exist
# 2. Runs mcap finalize (computes Record-Hash, creates .mcap)
# 3. Runs mcap stamp (creates OTS timestamp)
# 4. Runs mcap verify (validates everything)

set -euo pipefail

RECORD_NUM="${1:-}"
if [[ -z "$RECORD_NUM" ]]; then
    echo "Usage: bash ~/mcap-protocol/scripts/finalize.sh <record-number> [repo-path]"
    echo "Example: bash ~/mcap-protocol/scripts/finalize.sh 020"
    echo "Example: bash ~/mcap-protocol/scripts/finalize.sh 003 ~/project-gordo"
    exit 1
fi

# Paths — repo defaults to cwd
REPO_ROOT="${2:-$(pwd)}"
MCAP_DIR="${HOME}/mcap-protocol"
PREIMAGE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-preimage.txt"
SIGNATURE="${REPO_ROOT}/ratification/party-a-signature-${RECORD_NUM}.asc"
MCAP_FILE="${REPO_ROOT}/ratification/record-${RECORD_NUM}.mcap"

echo "=== MCAP Finalization: record-${RECORD_NUM} ==="
echo "Repo: ${REPO_ROOT}"
echo ""

# Step 1: Validate files exist
if [[ ! -f "$PREIMAGE" ]]; then
    echo "ERROR: Preimage not found at ${PREIMAGE}"
    exit 1
fi
echo "✓ Preimage found"

if [[ ! -f "$SIGNATURE" ]]; then
    echo "ERROR: Party-A signature not found at ${SIGNATURE}"
    echo "  Run: bash ~/mcap-protocol/scripts/sign-party-a.sh ${RECORD_NUM} ${REPO_ROOT}"
    exit 1
fi
echo "✓ Party-A signature found"

# Step 2: Check Timestamp-Local is set
if grep -q "^Timestamp-Local:$" "$PREIMAGE"; then
    echo "ERROR: Timestamp-Local is empty in preimage."
    exit 1
fi
echo "✓ Timestamp-Local set"

# Step 3: Run mcap finalize
echo ""
echo "Running mcap finalize..."
cd "${MCAP_DIR}"
./mcap finalize "$PREIMAGE" -o "$MCAP_FILE"
echo "✓ mcap finalize complete"

# Step 4: Run mcap stamp
echo ""
echo "Running mcap stamp..."
./mcap stamp "$MCAP_FILE" --force
echo "✓ mcap stamp complete"

# Step 5: Run mcap verify
echo ""
echo "Running mcap verify..."
./mcap verify "$MCAP_FILE" --preimage "$PREIMAGE"

# Step 6: Summary
echo ""
echo "=== Finalization complete ==="
echo "MCAP file: ${MCAP_FILE}"
echo "OTS file: ${MCAP_FILE}.ots"
echo ""
echo "Next: git add, commit, push"
echo "  git add ratification/record-${RECORD_NUM}.mcap ratification/record-${RECORD_NUM}.mcap.ots ratification/party-a-signature-${RECORD_NUM}.asc"
