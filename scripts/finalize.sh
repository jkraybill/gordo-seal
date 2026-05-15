#!/usr/bin/env bash
# SEAL Finalization Script (templatized per #164)
# Usage: bash ~/gordo-seal/scripts/finalize.sh <record-number> [repo-path]
# Example: bash ~/gordo-seal/scripts/finalize.sh 020
# Example: bash ~/gordo-seal/scripts/finalize.sh 003 ~/project-gordo
#
# Prerequisites:
# - Preimage exists at <repo>/ratification/record-<N>-preimage.txt
# - Party-A signature exists at <repo>/ratification/party-a-signature-<N>.asc
# - Timestamp-Local is set in preimage
#
# This script:
# 1. Validates preimage and signature exist
# 2. Runs seal finalize (computes Record-Hash, creates .mcap)
# 3. Runs seal stamp (creates OTS timestamp)
# 4. Runs seal verify (validates everything)

set -euo pipefail

RECORD_NUM="${1:-}"
if [[ -z "$RECORD_NUM" ]]; then
    echo "Usage: bash ~/gordo-seal/scripts/finalize.sh <record-number> [repo-path]"
    echo "Example: bash ~/gordo-seal/scripts/finalize.sh 020"
    echo "Example: bash ~/gordo-seal/scripts/finalize.sh 003 ~/project-gordo"
    exit 1
fi

# Paths — repo defaults to cwd
REPO_ROOT="${2:-$(pwd)}"
SEAL_DIR="${HOME}/gordo-seal"
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
    echo "  Run: bash ~/gordo-seal/scripts/sign-party-a.sh ${RECORD_NUM} ${REPO_ROOT}"
    exit 1
fi
echo "✓ Party-A signature found"

# Step 2: Check Timestamp-Local is set
if grep -q "^Timestamp-Local:$" "$PREIMAGE"; then
    echo "ERROR: Timestamp-Local is empty in preimage."
    exit 1
fi
echo "✓ Timestamp-Local set"

# Step 3: Run seal finalize
echo ""
echo "Running seal finalize..."
cd "${SEAL_DIR}"
./seal finalize "$PREIMAGE" -o "$MCAP_FILE"
echo "✓ seal finalize complete"

# Step 4: Run seal stamp
echo ""
echo "Running seal stamp..."
./seal stamp "$MCAP_FILE" --force
echo "✓ seal stamp complete"

# Step 5: Run seal verify
echo ""
echo "Running seal verify..."
./seal verify "$MCAP_FILE" --preimage "$PREIMAGE"

# Step 6: Summary
echo ""
echo "=== Finalization complete ==="
echo "MCAP file: ${MCAP_FILE}"
echo "OTS file: ${MCAP_FILE}.ots"
echo ""
echo "Next: git add, commit, push"
echo "  git add ratification/record-${RECORD_NUM}.mcap ratification/record-${RECORD_NUM}.mcap.ots ratification/party-a-signature-${RECORD_NUM}.asc"
