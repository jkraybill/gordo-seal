"""Canonicalization engine for SEAL records and content.

Canonical form: UTF-8, NFC normalization, stripped trailing whitespace
per line, Unix line endings (LF), no byte-order mark, trailing newline,
character allowlist enforced.

Character allowlist (normative):
  Allowed: L (Letter), M (Mark), N (Number), P (Punctuation), S (Symbol),
           U+0020 (space), U+000A (LF), U+0009 (Tab),
           U+200C (ZWNJ — Persian/Urdu orthography),
           U+200D (ZWJ — Indic scripts, emoji sequences)
  Non-standard spaces (Zs except U+0020): replaced with U+0020
  All other characters: stripped
"""

import unicodedata
from typing import NamedTuple


class CanonIssue(NamedTuple):
    line: int | None
    issue: str


# Characters with specific allowlist exceptions (category Cf but linguistically required)
_ALLOWED_CF = frozenset([
    "\u200c",  # ZWNJ — required for Persian/Urdu orthography
    "\u200d",  # ZWJ — required for Malayalam, Sinhala, emoji sequences
])

# Allowed Unicode general categories
_ALLOWED_CATEGORIES = frozenset(["L", "M", "N", "P", "S"])

# Explicitly allowed control characters
_ALLOWED_CONTROLS = frozenset([
    "\n",    # U+000A LF
    "\t",    # U+0009 Tab
])


def _is_allowed(ch: str) -> bool:
    """Check if a character is in the SEAL allowlist."""
    # Explicit control character allowlist
    if ch in _ALLOWED_CONTROLS:
        return True
    # Standard space
    if ch == " ":  # U+0020
        return True
    # Allowed Cf exceptions (ZWJ, ZWNJ)
    if ch in _ALLOWED_CF:
        return True
    # Check Unicode general category (first letter: L, M, N, P, S)
    cat = unicodedata.category(ch)
    if cat[0] in _ALLOWED_CATEGORIES:
        return True
    return False


def _is_nonstandard_space(ch: str) -> bool:
    """Check if a character is a non-standard space (Zs but not U+0020)."""
    return ch != " " and unicodedata.category(ch) == "Zs"


def canonicalize(text: str) -> str:
    """Apply SEAL canonical form to text. Returns canonical string."""
    # Strip BOM
    if text.startswith("\ufeff"):
        text = text[1:]
    # NFC normalization
    text = unicodedata.normalize("NFC", text)
    # Normalize line endings: CRLF -> LF, then bare CR -> LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Character allowlist: replace non-standard spaces, strip disallowed
    result = []
    for ch in text:
        if _is_nonstandard_space(ch):
            result.append(" ")  # Replace with standard space
        elif _is_allowed(ch):
            result.append(ch)
        # else: strip (disallowed character)
    text = "".join(result)
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
    check_lines = lines[:-1] if text.endswith("\n") else lines
    for i, line in enumerate(check_lines):
        if line != line.rstrip():
            issues.append(CanonIssue(i + 1, f"Trailing whitespace on line {i + 1}"))
        # Character allowlist checks per line
        for j, ch in enumerate(line):
            if ch in _ALLOWED_CF:
                # Allowed but warn — invisible characters signer should know about
                name = unicodedata.name(ch, f"U+{ord(ch):04X}")
                issues.append(CanonIssue(i + 1,
                    f"Invisible character {name} (U+{ord(ch):04X}) on line {i + 1} col {j + 1} "
                    f"— allowed but verify intent"))
            elif _is_nonstandard_space(ch):
                name = unicodedata.name(ch, f"U+{ord(ch):04X}")
                issues.append(CanonIssue(i + 1,
                    f"Non-standard space {name} (U+{ord(ch):04X}) on line {i + 1} col {j + 1} "
                    f"— will be replaced with U+0020"))
            elif not _is_allowed(ch):
                name = unicodedata.name(ch, f"U+{ord(ch):04X}")
                issues.append(CanonIssue(i + 1,
                    f"Disallowed character {name} (U+{ord(ch):04X}) on line {i + 1} col {j + 1}"))

    # NFC check
    if text != unicodedata.normalize("NFC", text):
        issues.append(CanonIssue(None, "Text is not in NFC normalization form"))

    return issues
