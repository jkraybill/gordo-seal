"""MCAP error hierarchy."""


class McapError(Exception):
    """Base error for all MCAP operations."""


class CanonError(McapError):
    """Canonicalization failure."""


class RecordParseError(McapError):
    """Malformed record."""


class HashMismatchError(McapError):
    """Hash verification failure."""


class SigningError(McapError):
    """GPG signing failure."""


class StampError(McapError):
    """OpenTimestamps failure."""
