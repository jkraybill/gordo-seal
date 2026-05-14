"""Record parsing, preimage assembly, and finalization for SEAL."""

from collections import OrderedDict

# Normative placeholder per spec (em-dash U+2014)
RECORD_HASH_PLACEHOLDER = "SHA3-256:<preimage \u2014 this field is excluded from its own computation>"

STATEMENT_PLACEHOLDER_A = "<to be authored by Party-A>"
STATEMENT_PLACEHOLDER_B = "<to be authored by Party-B>"

# Fields that contain party sub-blocks
PARTY_KEYS = ("Party-A", "Party-B")

# The first line of the record is a fixed header, not a key-value pair
HEADER_LINE = "SEAL Ratification Record"
HEADER_LINE_LEGACY = "MCAP Ratification Record"  # backwards compat

# Sentinel prefix for blank line markers in the OrderedDict
_BLANK = "_blank_"


def parse_record(text: str) -> OrderedDict:
    """Parse an SEAL record (preimage or final) into an ordered dict.

    Top-level fields are key-value pairs separated by ': '.
    Party-A and Party-B contain indented sub-fields (two-space prefix).
    The first line is the fixed header 'SEAL Ratification Record'.
    Blank lines are preserved as '_blank_N' sentinel keys.

    Returns an OrderedDict preserving field order. Party blocks are
    nested OrderedDicts.
    """
    lines = text.split("\n")
    record: OrderedDict = OrderedDict()
    record["_header"] = HEADER_LINE  # always output new format

    i = 0
    blank_count = 0

    # Skip the header line (accept both legacy and new format)
    if lines[i].strip() in (HEADER_LINE, HEADER_LINE_LEGACY):
        i += 1

    current_party = None
    current_party_key = None

    while i < len(lines):
        line = lines[i]

        # Skip the final empty string from trailing newline split
        if i == len(lines) - 1 and line == "":
            break

        # Empty line
        if line == "":
            if current_party is not None:
                # Check if we're leaving the party block: next non-empty
                # line is not indented
                j = i + 1
                while j < len(lines) and lines[j] == "":
                    j += 1
                if j < len(lines) and lines[j].startswith("  "):
                    # Still in party block — shouldn't happen in practice
                    i += 1
                    continue
                else:
                    record[current_party_key] = current_party
                    current_party = None
                    current_party_key = None
            record[f"{_BLANK}{blank_count}"] = ""
            blank_count += 1
            i += 1
            continue

        # Indented line — part of a party block
        if line.startswith("  ") and current_party is not None:
            stripped = line[2:]  # Remove two-space indent
            colon_pos = stripped.find(": ")
            if colon_pos == -1 and stripped.endswith(":"):
                key = stripped[:-1]
                current_party[key] = ""
            elif colon_pos != -1:
                key = stripped[:colon_pos]
                value = stripped[colon_pos + 2:]
                current_party[key] = value
            i += 1
            continue

        # Top-level key-value
        colon_pos = line.find(": ")
        if colon_pos == -1 and line.endswith(":"):
            key = line[:-1]
            value = ""
        elif colon_pos != -1:
            key = line[:colon_pos]
            value = line[colon_pos + 2:]
        else:
            i += 1
            continue

        if key in PARTY_KEYS:
            current_party_key = key
            current_party = OrderedDict()
            i += 1
            continue

        record[key] = value
        i += 1

    # Close any open party block
    if current_party is not None:
        record[current_party_key] = current_party

    return record


def serialize_record(record: OrderedDict) -> str:
    """Serialize a parsed record back to text. Must produce byte-identical output."""
    lines = []

    for key, value in record.items():
        if key == "_header":
            lines.append(HEADER_LINE)
            continue

        if key.startswith(_BLANK):
            lines.append("")
            continue

        if key in PARTY_KEYS:
            lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                if sub_value == "":
                    lines.append(f"  {sub_key}:")
                else:
                    lines.append(f"  {sub_key}: {sub_value}")
            continue

        if value == "":
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {value}")

    # Trailing newline
    return "\n".join(lines) + "\n"


def find_preimage(record_path: str) -> str | None:
    """Convention-based preimage lookup: record-NNN.seal -> record-NNN-preimage.txt."""
    import os
    base = record_path
    if base.endswith(".seal"):
        preimage = base[:-5] + "-preimage.txt"
        if os.path.exists(preimage):
            return preimage
    return None


def fill_record_hash(preimage_text: str, hash_hex: str) -> str:
    """Replace the Record-Hash placeholder line with the actual hash value."""
    lines = preimage_text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Record-Hash:"):
            lines[i] = f"Record-Hash: SHA3-256:{hash_hex}"
            break
    return "\n".join(lines)


def fill_attestation(record_text: str, party: str, value: str) -> str:
    """Fill the Attestation field for a party."""
    lines = record_text.split("\n")
    in_party = False
    for i, line in enumerate(lines):
        if line.startswith(f"{party}:"):
            in_party = True
            continue
        if in_party and line.startswith("  Attestation:") and "Attestation-" not in line:
            lines[i] = f"  Attestation: {value}"
            break
        if in_party and not line.startswith("  ") and line != "":
            break
    return "\n".join(lines)
