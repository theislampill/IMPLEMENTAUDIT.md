#!/usr/bin/env python3
"""Reject stale maintained durable-identity spellings while preserving history."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


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
# These published issue carriers are documentary references, not additions to
# the canonical runtime namespace. The four-hex suffix/issue pairs are recorded
# in evolved-programme-v1/OWNERSHIP_RECONCILIATION_20261113.json's
# fresh_carrier_evidence. Keep the observed set explicit; gaps are not admitted.
DOCUMENTARY_PUBLISHED_CARRIERS = {
    "003B": 226, "003C": 228, "003D": 227,
    "003F": 225, "0040": 229, "0041": 230,
    "0043": 232, "0044": 231, "0045": 233,
}
HISTORICAL_DRAFT_ID = "R0042"  # unallocated historical container, not a carrier
DOCUMENTARY_DRAFT_CONTEXTS = (
    f"not a new {HISTORICAL_DRAFT_ID} issue.",
    f"not a new {HISTORICAL_DRAFT_ID}.",
    f"Old standalone {HISTORICAL_DRAFT_ID} draft is historical, not a current dependency or proposed new issue here.",
    f"The old standalone {HISTORICAL_DRAFT_ID} draft is explicitly historical, not an issue dependency.",
)


def documentary_source_reference(normalized: str, line: str, match: re.Match[str]) -> bool:
    path = PurePosixPath(normalized)
    portal = (
        path.parent.as_posix() == "docs/portal/pages"
        and path.name.startswith("research-lineage-")
        and path.suffix == ".html"
    )
    research = (
        normalized.startswith("docs/research/implementaudit/evolved-programme-v1/")
        and path.suffix in {".md", ".json"}
    )
    if not (portal or research):
        return False
    if match.group(1) in DOCUMENTARY_PUBLISHED_CARRIERS:
        return True
    if match.group(0) != HISTORICAL_DRAFT_ID:
        return False
    # Cover only this occurrence inside an existing exact historical/negative
    # clause. A second positive assertion on the same line must still refuse.
    for clause in DOCUMENTARY_DRAFT_CONTEXTS:
        for context in re.finditer(re.escape(clause), line):
            if match.start() == context.start() + clause.index(HISTORICAL_DRAFT_ID):
                return True
    return False


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise SystemExit("check-durable-identities: scan root must be a Git worktree")
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def active_changelog(text: str) -> str:
    match = re.search(r"(?m)^## \[v0\.4\.0\.0\].*$", text)
    if not match:
        return ""
    next_heading = re.search(r"(?m)^## \[v", text[match.end() :])
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.start() : end]


def explicitly_legacy(line: str) -> bool:
    lowered = line.lower()
    return "legacy alias" in lowered or "legacy spelling" in lowered or "historical" in lowered


def captured_title_alias(normalized: str, line: str, match: re.Match[str]) -> bool:
    if normalized != "docs/research/implementaudit/evolved-programme-v1/OWNERSHIP_RECONCILIATION_20261113.json":
        return False
    # Preserve the captured issue title only when its canonical/decimal pair
    # agrees. Other fields, additional aliases and runtime text still refuse.
    title = re.match(r'^\s*"title":\s*"R([0-9A-F]{4}) \(legacy (R[0-9]{2})\)', line)
    return (
        title is not None
        and title.span(2) == match.span()
        and int(title.group(1), 16) == int(title.group(2)[1:], 10)
    )


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
        scan_text = active_changelog(text) if normalized == "CHANGELOG.md" else text
        for number, line in enumerate(scan_text.splitlines(), 1):
            if not explicitly_legacy(line):
                for match in LEGACY_ROCKSTAR.finditer(line):
                    if not captured_title_alias(normalized, line, match):
                        failures.append(f"{normalized}:{number}: stale maintained Rockstar {match.group(0)}")
            for match in CANONICAL_ROCKSTAR.finditer(line):
                ordinal = int(match.group(1), 16)
                if (
                    ordinal > allocated_max
                    and "unallocated" not in line.lower()
                    and "next" not in line.lower()
                    and not documentary_source_reference(normalized, line, match)
                ):
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
