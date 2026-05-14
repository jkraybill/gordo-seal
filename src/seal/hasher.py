"""SHA3-256 hashing for SEAL content and records."""

import hashlib


def hash_bytes(data: bytes) -> str:
    """SHA3-256 hex digest of raw bytes."""
    return hashlib.sha3_256(data).hexdigest()


def hash_content(paths: list[str]) -> str:
    """Read files, concatenate raw bytes, return SHA3-256 hex digest."""
    h = hashlib.sha3_256()
    for path in paths:
        with open(path, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def hash_record(preimage_path: str) -> str:
    """Read preimage file as bytes, return SHA3-256 hex digest."""
    with open(preimage_path, "rb") as f:
        data = f.read()
    return hash_bytes(data)


def format_hash(hex_digest: str) -> str:
    """Format as 'SHA3-256:<hex>'."""
    return f"SHA3-256:{hex_digest}"
