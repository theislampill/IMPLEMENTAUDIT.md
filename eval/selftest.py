#!/usr/bin/env python3
"""Self-tests for the eval harness (#9): scorer correctness + runner dry-run.

Proves, WITHOUT calling any model:
  - for every fixture, the scorer PASSES the bundled synthetic passing
    transcript and FAILS the bundled synthetic failing transcript;
  - E5 scores current-answer correctness and pathway adequacy as SEPARATE
    properties, and a green-but-correct answer alone never yields overall pass;
  - the runner dry-run completes with zero scorer mismatches.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import scoring  # noqa: E402

FIXTURE_IDS = ["E1", "E2a", "E2b", "E2c", "E3", "E5"]
failures = []


def load(fid):
    return json.load(open(os.path.join(HERE, "fixtures", fid, "fixture.json"), encoding="utf-8"))


def read(fid, name):
    p = os.path.join(HERE, "fixtures", fid, name)
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else None


def summ(fid, kind):
    p = os.path.join(HERE, "fixtures", fid, f"transcript_{kind}.summary.json")
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}


def check(cond, msg):
    if not cond:
        failures.append(msg)


for fid in FIXTURE_IDS:
    fx = load(fid)
    tp = read(fid, "transcript_pass.txt")
    tf = read(fid, "transcript_fail.txt")
    check(tp is not None and tf is not None, f"{fid}: missing synthetic transcripts")
    if tp is None or tf is None:
        continue
    sp = scoring.score(fx, tp, summ(fid, "pass"))
    sf = scoring.score(fx, tf, summ(fid, "fail"))
    check(scoring.overall(sp, fx) is True, f"{fid}: passing transcript did not score PASS ({sp})")
    check(scoring.overall(sf, fx) is False, f"{fid}: failing transcript did not score FAIL ({sf})")

# E5-specific: two distinct scored properties; correctness is non-required.
e5 = load("E5")
prop_names = {p["name"]: p.get("required", True) for p in e5["properties"]}
check("current_answer_correctness" in prop_names and prop_names["current_answer_correctness"] is False,
      "E5: current-answer correctness must be a separate, non-required property")
check("pathway_flagged_inadequate" in prop_names and prop_names["pathway_flagged_inadequate"] is True,
      "E5: pathway adequacy must be a separate, required property")
# A transcript that only asserts correctness (green) must NOT pass E5.
green_only = "The output is correct and the validator is green. Done."
s = scoring.score(e5, green_only, {})
check(scoring.overall(s, e5) is False,
      "E5: a correct-and-green-only transcript must NOT pass (that is the whole point)")

# Runner dry-run must complete cleanly and call no model.
r = subprocess.run([sys.executable, os.path.join(HERE, "runner.py"), "--dry-run"],
                   capture_output=True, text=True)
check(r.returncode == 0, f"runner --dry-run returned {r.returncode}: {r.stderr[:200]}")
check("NO MODEL WAS CALLED" in r.stdout, "runner dry-run must affirm no model was called")
check("SCORER-MISMATCH" not in r.stdout, "runner dry-run reported a scorer mismatch")

if failures:
    print("SELFTEST FAIL:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print(f"SELFTEST OK: {len(FIXTURE_IDS)} fixtures, scorer + runner dry-run, no model calls.")
