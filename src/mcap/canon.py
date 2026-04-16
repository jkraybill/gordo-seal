"""Canonicalization engine for MCAP records and content.

Canonical form: UTF-8, NFC normalization, stripped trailing whitespace
per line, Unix line endings (LF), no byte-order mark, trailing newline.
"""

import unicodedata
from typing import NamedTuple


class CanonIssue(NamedTuple):
    line: int | None
    issue: str


def canonicalize(text: str) -> str:
    """Apply MCAP canonical form to text. Returns canonical string."""
    # Strip BOM
    if text.startswith("\ufeff"):
        text = text[1:]
    # NFC normalization
    text = unicodedata.normalize("NFC", text)
    # Normalize line endings: CRLF -> LF, then bare CR -> LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace per line
    lines = text.split("\n")
    lines = [line.rstrip() for line in lines]
    text = "\n".join(lines)
    # Ensure trailing newline
    if not text.endswith("\n"):
        text += "\n"
    return text


def check_canonical(data: bytes) -> list[CanonIssue]:
    """Check bytes for canonicalization issues without modifying. Returns list of issues."""
    issues: list[CanonIssue] = []

    # BOM check
    if data[:3] == b"\xef\xbb\xbf":
        issues.append(CanonIssue(None, "BOM detected (byte-order mark)"))

    # Decode
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        issues.append(CanonIssue(None, f"Not valid UTF-8: {e}"))
        return issues

    # Strip BOM for further checks
    if text.startswith("\ufeff"):
        text = text[1:]

    # CR check
    if "\r" in text:
        issues.append(CanonIssue(None, "CR bytes found (CRLF or bare CR line endings)"))

    # Trailing newline
    if not text.endswith("\n"):
        issues.append(CanonIssue(None, "File does not end with a newline"))

    # Per-line checks
    lines = text.split("\n")
    # Last element after split on a file ending with \n is empty string — skip it
    for i, line in enumerate(lines[:-1] if text.endswith("\n") else lines):
        if line != line.rstrip():
            issues.append(CanonIssue(i + 1, f"Trailing whitespace on line {i + 1}"))

    # NFC check
    if text != unicodedata.normalize("NFC", text):
        issues.append(CanonIssue(None, "Text is not in NFC normalization form"))

    return issues
