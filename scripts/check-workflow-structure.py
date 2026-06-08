#!/usr/bin/env python3
"""
check-workflow-structure.py — structural check for GitHub Actions workflow files.

Usage:
    python scripts/check-workflow-structure.py <workflow-file> [<workflow-file> ...]

Checks (without a YAML parser — stdlib only):
  1. File exists and is non-empty.
  2. Required top-level keys present: name, on (or "on:"), jobs.
  3. At least one job block contains a 'steps:' key.
  4. At least one 'uses: actions/checkout' reference present.
  5. No obvious syntax traps (tab characters, which YAML forbids for indentation).

LIMITATION: This is NOT a full GitHub Actions schema validation.
Full validation requires running the workflow in GitHub Actions CI.
This script catches obvious structural gaps only.

Exit 0: all structural checks pass.
Exit 1: one or more checks failed.
"""

import sys
from pathlib import Path


def check_file(path: Path) -> list:
    failures = []
    if not path.is_file():
        return [f"{path}: file not found"]
    content = path.read_text(encoding="utf-8")
    if len(content.strip()) < 20:
        return [f"{path}: file is suspiciously small or empty"]

    lines = content.splitlines()

    # 1. Top-level 'name:' key
    if not any(line.startswith("name:") for line in lines):
        failures.append(f"{path}: missing top-level 'name:' key")

    # 2. Top-level 'on:' key (YAML 'on' is a boolean synonym; check variants)
    has_on = any(
        line.startswith("on:") or line == "on:" or line.startswith('"on":')
        for line in lines
    )
    if not has_on:
        failures.append(f"{path}: missing top-level 'on:' trigger key")

    # 3. Top-level 'jobs:' key
    if not any(line.startswith("jobs:") for line in lines):
        failures.append(f"{path}: missing top-level 'jobs:' key")

    # 4. At least one 'steps:' key (any indentation)
    if not any("steps:" in line for line in lines):
        failures.append(f"{path}: no 'steps:' key found (no job steps?)")

    # 5. At least one actions/checkout reference
    if "actions/checkout" not in content:
        failures.append(f"{path}: no 'actions/checkout' reference found")

    # 6. No tab-indented lines (YAML uses spaces, not tabs)
    tab_lines = [i + 1 for i, line in enumerate(lines) if line.startswith("\t")]
    if tab_lines:
        failures.append(
            f"{path}: tab-indented lines found (YAML requires spaces): lines {tab_lines[:5]}"
        )

    return failures


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <workflow-file> [<workflow-file> ...]\n")
        sys.exit(1)

    all_failures = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        failures = check_file(path)
        all_failures.extend(failures)

    if all_failures:
        for f in all_failures:
            sys.stderr.write(f"check-workflow-structure: FAIL: {f}\n")
        sys.stderr.write(
            "check-workflow-structure: NOTE: Full GitHub Actions schema validation "
            "requires CI. This script checks structural basics only.\n"
        )
        sys.exit(1)

    sys.stdout.write(
        f"check-workflow-structure: ok ({len(sys.argv) - 1} file(s) pass structural checks)\n"
    )
    sys.stdout.write(
        "check-workflow-structure: NOTE: Full GitHub Actions schema validation "
        "is pending CI — structural check only.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
