"""SEAL error hierarchy."""


class SealError(Exception):
    """Base error for all SEAL operations."""


class CanonError(SealError):
    """Canonicalization failure."""


class RecordParseError(SealError):
    """Malformed record."""


class HashMismatchError(SealError):
    """Hash verification failure."""


class SigningError(SealError):
    """GPG signing failure."""


class StampError(SealError):
    """OpenTimestamps failure."""
