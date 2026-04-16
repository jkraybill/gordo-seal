"""OpenTimestamps wrapper for MCAP."""

import os
import shutil
import subprocess
from dataclasses import dataclass

from mcap.errors import StampError


@dataclass
class StampResult:
    verified: bool
    timestamp: str | None
    error: str | None


def check_ots_available() -> bool:
    """Check if the ots command is available."""
    return shutil.which("ots") is not None


def stamp(file_path: str) -> str:
    """Invoke ots stamp on a file. Returns path to .ots proof file."""
    if not check_ots_available():
        raise StampError("ots command not found. Install OpenTimestamps: pip install opentimestamps-client")

    result = subprocess.run(
        ["ots", "stamp", file_path],
        capture_output=True, timeout=120
    )
    if result.returncode != 0:
        raise StampError(f"ots stamp failed: {result.stderr.decode().strip()}")

    ots_path = file_path + ".ots"
    if not os.path.exists(ots_path):
        raise StampError(f"Expected .ots file not created: {ots_path}")
    return ots_path


def verify_stamp(ots_path: str) -> StampResult:
    """Invoke ots verify on a proof file."""
    if not check_ots_available():
        raise StampError("ots command not found")

    result = subprocess.run(
        ["ots", "verify", ots_path],
        capture_output=True, timeout=120
    )
    output = result.stdout.decode() + result.stderr.decode()

    if result.returncode == 0 and "Success" in output:
        timestamp = ""
        for line in output.splitlines():
            if "Bitcoin" in line or "block" in line:
                timestamp = line.strip()
        return StampResult(verified=True, timestamp=timestamp, error=None)

    return StampResult(verified=False, timestamp=None, error=output.strip())


def check_completeness(record_path: str) -> list[str]:
    """Check if a record looks complete enough to stamp."""
    warnings = []
    with open(record_path) as f:
        text = f.read()

    if "Attestation:" not in text:
        warnings.append("No Attestation fields found")

    # Check for empty attestation (preimage pattern)
    lines = text.splitlines()
    for line in lines:
        if line.strip() == "Attestation:" and "Attestation-" not in line:
            warnings.append("Empty Attestation field found — record may be a preimage, not a final record")
            break

    if "Record-Hash:" not in text:
        warnings.append("No Record-Hash field found")
    elif PLACEHOLDER_MARKER in text:
        warnings.append("Record-Hash still contains placeholder — not finalized")

    return warnings


# Import here to avoid circular dependency
PLACEHOLDER_MARKER = "<preimage"
