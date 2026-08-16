#!/usr/bin/env python3
"""Validate the self-contained historical absorption baseline projection."""

from __future__ import annotations

import argparse
from pathlib import Path

from historical_absorption import check_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = check_baseline(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("HISTORICAL_ABSORPTION_BASELINE=658/658 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
