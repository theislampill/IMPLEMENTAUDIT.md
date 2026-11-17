#!/usr/bin/env python3
"""Read-only checks for the greeting file's declared contracts."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("check", choices=("smoke", "phase", "final"))
args = parser.parse_args()
path = Path(__file__).with_name("app.txt")
raw = path.read_bytes()
greeting = path.parent.parent.joinpath("incoming/greeting.txt").read_bytes()
if not greeting or b"\n" in greeting or b"\r" in greeting:
    raise SystemExit("current greeting input is not one nonempty record")
lines = raw.splitlines()
if args.check == "smoke":
    passed = len(lines) >= 2 and lines[1] == b"status=ready"
    contract = "second record remains status=ready"
elif args.check == "phase":
    passed = bool(lines) and lines[0] == greeting
    contract = "first operational record equals the current greeting input"
else:
    passed = raw == greeting + b"\nstatus=ready\n"
    contract = "canonical two-record bytes with exactly one final newline"
print(json.dumps({"check": args.check, "contract": contract, "passed": passed,
                  "dependency_sha256": hashlib.sha256(greeting).hexdigest(),
                  "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                 sort_keys=True, separators=(",", ":")))
raise SystemExit(0 if passed else 1)
