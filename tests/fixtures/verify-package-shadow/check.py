#!/usr/bin/env python3
"""Deterministic subprocess fixture for shadow-verifier behavioural tests."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--id", required=True)
parser.add_argument(
    "--status",
    choices=("pass", "fail", "not-applicable", "sleep", "spawn-child"),
    required=True,
)
parser.add_argument("--log", type=Path, required=True)
parser.add_argument("--seconds", type=float, default=0.0)
parser.add_argument("--sentinel", type=Path)
args = parser.parse_args()

with args.log.open("a", encoding="utf-8", newline="\n") as handle:
    handle.write(args.id + "\n")

if args.status == "spawn-child":
    if args.sentinel is None:
        raise SystemExit("--sentinel is required for spawn-child")
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import pathlib,time; "
                f"time.sleep(0.25); pathlib.Path({str(args.sentinel)!r}).write_text('leaked')"
            ),
        ]
    )
    time.sleep(2)
elif args.status == "sleep":
    time.sleep(args.seconds)
elif args.status == "not-applicable":
    print("SHADOW_NOT_APPLICABLE")
elif args.status == "fail":
    print(f"{args.id}: product failure")
    raise SystemExit(1)
else:
    print(f"{args.id}: pass")
