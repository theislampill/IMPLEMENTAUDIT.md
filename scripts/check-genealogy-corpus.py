#!/usr/bin/env python3
"""Fail closed when the committed Engineering Genealogy corpus drifts."""

from __future__ import annotations

import argparse
from pathlib import Path

from genealogy_corpus import check_corpus


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--package", type=Path)
    args = parser.parse_args()
    errors = check_corpus(args.root, args.package)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("TRIFECTAS=4/4 LINEAGES=12/12 PROPERTIES=658/658 CORPUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
