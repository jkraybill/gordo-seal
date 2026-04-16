"""GPG signing wrapper for MCAP."""

import os
import subprocess
from dataclasses import dataclass

from mcap.errors import SigningError


@dataclass
class SignatureResult:
    valid: bool
    key_id: str
    fingerprint: str
    timestamp: str
    error: str | None


def sign_hash(hash_hex: str, output_path: str, key_id: str | None = None) -> None:
    """GPG clearsign the Record-Hash hex string."""
    env = os.environ.copy()
    if "GPG_TTY" not in env:
        try:
            tty = os.ttyname(0)
            env["GPG_TTY"] = tty
        except OSError:
            pass  # Not a TTY — GPG may still work with pinentry

    cmd = ["gpg", "--clearsign", "-o", output_path]
    if key_id:
        cmd.extend(["--local-user", key_id])

    result = subprocess.run(
        cmd, input=hash_hex.encode() + b"\n", env=env,
        capture_output=True, timeout=60
    )
    if result.returncode != 0:
        raise SigningError(
            f"GPG signing failed: {result.stderr.decode().strip()}"
        )


def verify_signature(sig_path: str) -> SignatureResult:
    """Verify a GPG clearsigned file. Returns result with parsed fields."""
    result = subprocess.run(
        ["gpg", "--verify", sig_path],
        capture_output=True, timeout=30
    )
    stderr = result.stderr.decode()

    valid = result.returncode == 0
    key_id = ""
    fingerprint = ""
    timestamp = ""

    for line in stderr.splitlines():
        if "using" in line and "key" in line:
            parts = line.strip().split()
            # "using EDDSA key D3A0C61F..."
            for j, part in enumerate(parts):
                if part == "key":
                    key_id = parts[j + 1] if j + 1 < len(parts) else ""
        if "Signature made" in line:
            # "Signature made Thu Apr 16 13:43:43 2026 AEST"
            timestamp = line.split("Signature made")[-1].strip()

    return SignatureResult(
        valid=valid, key_id=key_id, fingerprint=fingerprint,
        timestamp=timestamp,
        error=None if valid else stderr.strip()
    )


def extract_signed_content(sig_path: str) -> str:
    """Extract the clearsigned message body (the hash hex)."""
    with open(sig_path) as f:
        lines = f.readlines()
    in_body = False
    content_lines = []
    for line in lines:
        if line.startswith("-----BEGIN PGP SIGNATURE-----"):
            break
        if in_body and line.strip():
            content_lines.append(line.strip())
        if line.startswith("Hash:"):
            in_body = True
    return "\n".join(content_lines)
