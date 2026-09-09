#!/usr/bin/env python3
"""Fail closed when the committed Engineering Genealogy corpus drifts."""

from __future__ import annotations

import argparse
from pathlib import Path

from genealogy_corpus import check_corpus, load_source_lock


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
    c = load_source_lock(args.root)["expected"]
    print(f"TRIFECTAS={c['trifectas']} LINEAGES={c['lineages']} PROPERTIES={c['properties']} CORPUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
