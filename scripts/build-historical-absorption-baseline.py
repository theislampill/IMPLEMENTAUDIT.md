#!/usr/bin/env python3
"""Build the frozen read-only historical absorption baseline."""

from __future__ import annotations

import argparse
from pathlib import Path

from historical_absorption import build_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    baseline = build_baseline(args.root, args.source)
    counts = baseline["counts"]
    print(f"HISTORICAL_PROPERTIES={counts['properties']}/658")
    for key, value in counts["historical_classifications"].items():
        print(f"{key}={value}")
    for key, value in counts["constraint_indicators"].items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
