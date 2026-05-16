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
# 2. Runs seal finalize (computes Record-Hash, creates .seal)
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
SEAL_FILE="${REPO_ROOT}/ratification/record-${RECORD_NUM}.seal"

echo "=== Seal Finalization: record-${RECORD_NUM} ==="
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

# Step 3: Build attestation flags based on existing signature files
ATTESTATION_FLAGS=""

# Party-A attestation (always required for signed records)
PARTY_A_SIG="${REPO_ROOT}/ratification/party-a-signature-${RECORD_NUM}.asc"
if [[ -f "$PARTY_A_SIG" ]]; then
    ATTESTATION_FLAGS="--attestation Party-A='See party-a-signature-${RECORD_NUM}.asc'"
fi

# Party-B attestation (optional — only for Level 2+ Party-B)
PARTY_B_SIG="${REPO_ROOT}/ratification/party-b-signature-${RECORD_NUM}.asc"
if [[ -f "$PARTY_B_SIG" ]]; then
    ATTESTATION_FLAGS="${ATTESTATION_FLAGS} --attestation Party-B='See party-b-signature-${RECORD_NUM}.asc'"
fi

# Step 4: Run seal finalize
echo ""
echo "Running seal finalize..."
cd "${SEAL_DIR}"
if [[ -n "$ATTESTATION_FLAGS" ]]; then
    echo "  Attestation flags: ${ATTESTATION_FLAGS}"
    eval ./seal finalize "$PREIMAGE" $ATTESTATION_FLAGS -o "$SEAL_FILE"
else
    ./seal finalize "$PREIMAGE" -o "$SEAL_FILE"
fi
echo "✓ seal finalize complete"

# Step 5: Run seal stamp
echo ""
echo "Running seal stamp..."
./seal stamp "$SEAL_FILE" --force
echo "✓ seal stamp complete"

# Step 6: Run seal verify (with content file if it exists)
echo ""
echo "Running seal verify..."
CONTENT_FILE="${REPO_ROOT}/ratification/record-${RECORD_NUM}-content.md"
if [[ -f "$CONTENT_FILE" ]]; then
    ./seal verify "$SEAL_FILE" --preimage "$PREIMAGE" --content "$CONTENT_FILE"
else
    echo "Note: No content file found at ${CONTENT_FILE}, skipping Content-Hash verification"
    ./seal verify "$SEAL_FILE" --preimage "$PREIMAGE"
fi

# Step 7: Summary
echo ""
echo "=== Finalization complete ==="
echo "Seal file: ${SEAL_FILE}"
echo "OTS file: ${SEAL_FILE}.ots"
echo ""
echo "Next: git add, commit, push"
echo "  git add ratification/record-${RECORD_NUM}.seal ratification/record-${RECORD_NUM}.seal.ots ratification/party-a-signature-${RECORD_NUM}.asc"
