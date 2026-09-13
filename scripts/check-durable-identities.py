#!/usr/bin/env python3
"""Reject stale maintained durable-identity spellings while preserving history."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


# A bare RNN token is the durable Rockstar namespace.  RNN-F1, DOG-RNN-case,
# RNN_TEST_GATE, and similar composites are local fixture/test identifiers and
# intentionally remain outside the migration unless their own owner says
# otherwise.  Treating every prefixed composite as a Rockstar reference makes
# a local label silently acquire durable identity semantics.
LEGACY_ROCKSTAR = re.compile(
    r"(?<![A-Za-z0-9])R(?:0[1-9]|[1-4][0-9]|5[0-5])(?![0-9A-Za-z_-])"
)
CANONICAL_ROCKSTAR = re.compile(r"(?<![A-Za-z0-9])R([0-9A-F]{4})(?![0-9A-Za-z])")
LEGACY_GENERATION_PATTERNS = [
    re.compile(r"(?m)^Current (?:epoch|generation):\s*e[1-9][0-9]*\s*$"),
    re.compile(r"(?m)^\|\s*e[1-9][0-9]*\s*\|"),
    re.compile(r"--epoch\s+e[1-9][0-9]*\b"),
    re.compile(r"continuity-receipts/[^/\s]+/e[1-9][0-9]*\b"),
    re.compile(r"host-event:e[1-9][0-9]*\b"),
    re.compile(r"\b(?:epoch|generation)\s+e[1-9][0-9]*\b", re.IGNORECASE),
]
HISTORICAL_PREFIXES = (
    "docs/audits/archive/",
    "docs/research/genealogy/",
    "docs/research/implementaudit/historical-absorption-baseline/",
    "docs/reviews/",
)
COMPATIBILITY_FILES = {
    "skills/implementaudit/references/identity-namespaces.json",
    "tests/durable-identity-contract.test.sh",
}


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise SystemExit("check-durable-identities: scan root must be a Git worktree")
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def active_changelog(text: str, current_family: str) -> str:
    """Select canonical maintained sections from the independent package owner."""
    lines = text.splitlines(keepends=True)
    headings = []
    fence = None
    comment = False
    for number, line in enumerate(lines):
        value = line.rstrip("\r\n")
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", value):
                fence = None
            continue
        if comment:
            comment = "-->" not in value
            continue
        opening = re.match(r" {0,3}(`{3,}|~{3,})", value)
        if opening:
            fence = (opening.group(1)[0], len(opening.group(1)))
            continue
        if "<!--" in value:
            value, tail = value.split("<!--", 1)
            comment = "-->" not in tail
            value = value.rstrip()
        heading = re.fullmatch(r" {0,3}##[ \t]+(.+?)[ \t]*", value)
        if heading:
            title = re.match(r"\[([^\]]+)\](?:[ \t]|$)", heading.group(1))
            headings.append((number, title.group(1) if title else None))
    maintained = {"Unreleased", current_family}
    seen = set()
    selected = []
    for index, (start, name) in enumerate(headings):
        if name not in maintained:
            continue
        if name in seen:
            raise ValueError("duplicate maintained changelog section: " + name)
        seen.add(name)
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        selected.append((start, end))
    if not selected:
        raise ValueError("no maintained changelog section: expected [Unreleased] or [" + current_family + "]")
    # Blank historical text without changing diagnostic line numbers or bytes
    # on disk. Existing per-line legacy/unallocated exceptions remain below.
    masked = [line[len(line.rstrip("\r\n")):] for line in lines]
    for start, end in selected:
        masked[start:end] = lines[start:end]
    return "".join(masked)


def explicitly_legacy(line: str) -> bool:
    lowered = line.lower()
    return "legacy alias" in lowered or "legacy spelling" in lowered or "historical" in lowered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-root", default=None)
    args = parser.parse_args()
    source_root = Path(__file__).resolve().parent.parent
    root = Path(args.scan_root).resolve() if args.scan_root else source_root
    registry_path = source_root / "skills/implementaudit/references/identity-namespaces.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        allocated_max = registry["namespaces"]["R"]["allocated_ordinal_max"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise SystemExit(f"check-durable-identities: invalid registry: {exc}") from exc
    try:
        contract = json.loads((source_root / "package/implementaudit-package.json").read_text(encoding="utf-8"))
        current_family = contract["release_family"]
        if not isinstance(current_family, str) or not re.fullmatch(r"v\d+\.\d+\.\d+\.\d+", current_family):
            raise ValueError("release_family must be a four-component public identity")
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"check-durable-identities: invalid current package identity: {exc}") from exc

    failures: list[str] = []
    for rel in tracked_files(root):
        normalized = rel.replace("\\", "/")
        if normalized.startswith(HISTORICAL_PREFIXES) or normalized in COMPATIBILITY_FILES:
            continue
        path = root / rel
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        try:
            scan_text = active_changelog(text, current_family) if normalized == "CHANGELOG.md" else text
        except ValueError as exc:
            failures.append(f"{normalized}: {exc}")
            continue
        for number, line in enumerate(scan_text.splitlines(), 1):
            if not explicitly_legacy(line):
                for match in LEGACY_ROCKSTAR.finditer(line):
                    failures.append(f"{normalized}:{number}: stale maintained Rockstar {match.group(0)}")
            for match in CANONICAL_ROCKSTAR.finditer(line):
                ordinal = int(match.group(1), 16)
                if ordinal > allocated_max and "unallocated" not in line.lower() and "next" not in line.lower():
                    failures.append(f"{normalized}:{number}: unallocated Rockstar presented as current {match.group(0)}")
        for pattern in LEGACY_GENERATION_PATTERNS:
            for match in pattern.finditer(scan_text):
                line_number = scan_text.count("\n", 0, match.start()) + 1
                line = scan_text.splitlines()[line_number - 1]
                if not explicitly_legacy(line):
                    failures.append(f"{normalized}:{line_number}: stale maintained continuity generation {match.group(0).strip()}")

        for segment in normalized.split("/"):
            if LEGACY_ROCKSTAR.search(segment):
                failures.append(f"{normalized}: stale Rockstar in maintained path")

    if failures:
        sys.stderr.write("\n".join(dict.fromkeys(failures)) + "\n")
        return 1
    print("check-durable-identities: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
