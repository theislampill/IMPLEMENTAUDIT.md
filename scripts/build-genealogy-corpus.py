#!/usr/bin/env python3
"""Build exact extracted members and deterministic genealogy indexes."""

from __future__ import annotations

import argparse
from pathlib import Path

from genealogy_corpus import build_corpus


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    models = build_corpus(args.root)
    counts = models["corpus_manifest"]["counts"]
    print(
        f"TRIFECTAS={counts['trifectas']}/4 "
        f"LINEAGES={counts['lineages']}/12 "
        f"PROPERTIES={counts['properties']}/658"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
