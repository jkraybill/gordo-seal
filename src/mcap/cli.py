"""MCAP CLI — command-line interface for the Mutual Consent Attestation Protocol."""

import argparse
import os
import sys

from mcap import __version__
from mcap.canon import check_canonical
from mcap.hasher import hash_content, hash_record, format_hash
from mcap.record import find_preimage, fill_record_hash, fill_attestation
from mcap.signer import sign_hash, verify_signature, extract_signed_content
from mcap.stamper import stamp, check_completeness, check_ots_available
from mcap.verifier import verify
from mcap.errors import McapError


def cmd_hash_content(args):
    """Compute SHA3-256 of canonicalized content files."""
    # Check canonical form first
    for path in args.files:
        with open(path, "rb") as f:
            data = f.read()
        issues = check_canonical(data)
        if issues:
            for issue in issues:
                prefix = f"  line {issue.line}: " if issue.line else "  "
                print(f"WARNING ({os.path.basename(path)}): {prefix}{issue.issue}", file=sys.stderr)

    result = hash_content(args.files)
    print(format_hash(result))
    return 0


def cmd_hash_record(args):
    """Compute Record-Hash from preimage file."""
    path = args.preimage
    with open(path, "rb") as f:
        data = f.read()

    issues = check_canonical(data)
    if issues:
        for issue in issues:
            prefix = f"  line {issue.line}: " if issue.line else "  "
            print(f"WARNING: {prefix}{issue.issue}", file=sys.stderr)

    result = hash_record(path)
    print(format_hash(result))
    return 0


def cmd_sign(args):
    """GPG clearsign the Record-Hash of a preimage."""
    record_hash = hash_record(args.preimage)
    print(f"Record-Hash: {format_hash(record_hash)}", file=sys.stderr)

    output = args.output
    if not output:
        base = os.path.splitext(args.preimage)[0]
        output = base.replace("-preimage", "") + "-signature.asc"
        # If file exists, ask
        if os.path.exists(output):
            print(f"Output file exists: {output}", file=sys.stderr)
            response = input("Overwrite? (y/N) ")
            if response.lower() != "y":
                print("Aborted.", file=sys.stderr)
                return 1

    sign_hash(record_hash, output, key_id=args.key)
    print(f"Signature written to: {output}")
    return 0


def cmd_finalize(args):
    """Produce final .mcap record from preimage and signature(s)."""
    with open(args.preimage) as f:
        text = f.read()

    # Compute Record-Hash
    record_hash = hash_record(args.preimage)

    # Fill Record-Hash
    result = fill_record_hash(text, record_hash)

    # Fill attestations
    for sig_spec in args.attestation:
        parts = sig_spec.split("=", 1)
        if len(parts) != 2 or parts[0] not in ("Party-A", "Party-B"):
            print(f"ERROR: --attestation must be Party-A=<value> or Party-B=<value>", file=sys.stderr)
            return 2
        party, value = parts
        result = fill_attestation(result, party, value)

    # Write output
    output = args.output
    if not output:
        output = args.preimage.replace("-preimage.txt", ".mcap")

    with open(output, "w") as f:
        f.write(result)

    print(f"Record-Hash: {format_hash(record_hash)}", file=sys.stderr)
    print(f"Finalized record written to: {output}")
    return 0


def cmd_verify(args):
    """Verify an MCAP record."""
    report = verify(
        args.record,
        content_paths=args.content,
        preimage_path=args.preimage,
    )

    # Display results
    status_symbols = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP", "warn": "WARN"}
    for check in report.checks:
        symbol = status_symbols.get(check.status, "????")
        print(f"  [{symbol}] {check.name}: {check.detail}")

    if report.passed:
        print("\nVerification: ALL CHECKS PASSED")
        return 0
    else:
        failed = [c for c in report.checks if c.status == "fail"]
        print(f"\nVerification: {len(failed)} CHECK(S) FAILED")
        return 1


def cmd_nonce(args):
    """Generate entropy for session nonce, or combine two contributions.

    Per spec: each party contributes 32 bytes (64 lowercase hex chars).
    Nonce = SHA3-256(Individual-A-contribution || Individual-B-contribution).
    Individual A contributes first.
    """
    import hashlib
    if args.combine:
        parts = args.combine
        if len(parts) != 2:
            print("ERROR: --combine requires exactly 2 hex strings (Individual A first, then B)",
                  file=sys.stderr)
            return 2
        import re
        for i, part in enumerate(parts):
            label = "Individual A" if i == 0 else "Individual B"
            if not re.fullmatch(r"[0-9a-f]{64}", part):
                if re.fullmatch(r"[0-9a-fA-F]{64}", part):
                    print(f"ERROR: {label} contribution must be lowercase hex", file=sys.stderr)
                    return 2
                print(f"ERROR: {label} contribution must be exactly 64 lowercase hex characters "
                      f"(got {len(part)} chars)", file=sys.stderr)
                return 2
        combined = (parts[0] + parts[1]).encode()
        nonce = hashlib.sha3_256(combined).hexdigest()
        print(f"Session-Nonce: {nonce}")
    else:
        entropy = os.urandom(32).hex()
        print(entropy)
    return 0


def cmd_stamp(args):
    """OTS stamp a finalized record."""
    if not check_ots_available():
        print("ERROR: ots command not found. Install: pip install opentimestamps-client", file=sys.stderr)
        return 3

    # Check completeness
    warnings = check_completeness(args.record)
    if warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)
        if not args.force:
            print("Record appears incomplete. Use --force to stamp anyway.", file=sys.stderr)
            return 1

    ots_path = stamp(args.record)
    print(f"Stamped: {ots_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcap",
        description=f"MCAP — Mutual Consent Attestation Protocol tooling v{__version__}",
    )
    parser.add_argument("--version", action="version", version=f"mcap {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # hash-content
    p = sub.add_parser("hash-content", help="SHA3-256 hash of content file(s)")
    p.add_argument("files", nargs="+", help="Content file(s) to hash (concatenated in order)")

    # hash-record
    p = sub.add_parser("hash-record", help="Compute Record-Hash from preimage")
    p.add_argument("preimage", help="Preimage file path")

    # sign
    p = sub.add_parser("sign", help="GPG clearsign the Record-Hash")
    p.add_argument("preimage", help="Preimage file path")
    p.add_argument("-o", "--output", help="Output signature file path")
    p.add_argument("-k", "--key", help="GPG key ID to sign with")

    # finalize
    p = sub.add_parser("finalize", help="Produce final record from preimage")
    p.add_argument("preimage", help="Preimage file path")
    p.add_argument("-a", "--attestation", action="append", default=[],
                   help="Party attestation: Party-A='See path/to/sig.asc' (repeatable)")
    p.add_argument("-o", "--output", help="Output .mcap file path")

    # verify
    p = sub.add_parser("verify", help="Verify an MCAP record")
    p.add_argument("record", help="Record .mcap file path")
    p.add_argument("--content", nargs="+", help="Content file(s) for Content-Hash verification")
    p.add_argument("--preimage", help="Preimage file path (auto-detected if not specified)")

    # nonce
    p = sub.add_parser("nonce", help="Generate entropy or combine nonce contributions")
    p.add_argument("--combine", nargs=2, metavar="HEX",
                   help="Combine two entropy contributions into a session nonce (SHA3-256)")

    # stamp
    p = sub.add_parser("stamp", help="OTS timestamp a finalized record")
    p.add_argument("record", help="Record .mcap file path")
    p.add_argument("--force", action="store_true", help="Stamp even if record appears incomplete")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = {
        "hash-content": cmd_hash_content,
        "hash-record": cmd_hash_record,
        "sign": cmd_sign,
        "finalize": cmd_finalize,
        "verify": cmd_verify,
        "nonce": cmd_nonce,
        "stamp": cmd_stamp,
    }

    try:
        return commands[args.command](args)
    except McapError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
