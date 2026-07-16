#!/usr/bin/env python3
"""Eval harness runner (#9). DRY-RUN ONLY in this PR: never invokes a model.

Modes:
  --dry-run (default): for each fixture, print the mission/prompt a real run
    would send and the deterministic scoring rule; then score the bundled
    synthetic transcripts (eval/fixtures/<id>/transcript_pass.txt and
    transcript_fail.txt) to prove the scorer works end to end. No model call.
  --transcripts <dir>: score already-produced transcript files found in <dir>
    named <fixture-id>.txt (+ optional <fixture-id>.summary.json). Still no
    model call — this consumes transcripts a separately-approved run produced.

There is deliberately NO code path that contacts a provider. Real baseline runs
are gated on the owner approval packet described in issue #9, not on a flag.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import scoring  # noqa: E402

FIXTURE_IDS = ["E1", "E2a", "E2b", "E2c", "E3", "E5"]


def load_fixture(fid):
    return json.load(open(os.path.join(HERE, "fixtures", fid, "fixture.json"), encoding="utf-8"))


def cmd_dry_run():
    failures = 0
    for fid in FIXTURE_IDS:
        fx = load_fixture(fid)
        print(f"\n===== {fid}: {fx['title']} =====")
        print(f"MISSION (would be sent to the model):\n  {fx['mission']}")
        print(f"PLANTED DEFECT: {fx['planted_defect']}")
        print(f"EXPECTED: {fx['expected_correct_behavior']}")
        print("SCORING PROPERTIES:")
        for p in fx["properties"]:
            req = "required" if p.get("required", True) else "scored-separately"
            print(f"  - [{req}] {p['name']}: {p.get('describes','')}")
        # Prove the scorer end to end on bundled synthetics, if present.
        for kind, expect in (("pass", True), ("fail", False)):
            tpath = os.path.join(HERE, "fixtures", fid, f"transcript_{kind}.txt")
            spath = os.path.join(HERE, "fixtures", fid, f"transcript_{kind}.summary.json")
            if not os.path.isfile(tpath):
                continue
            transcript = open(tpath, encoding="utf-8").read()
            summary = json.load(open(spath, encoding="utf-8")) if os.path.isfile(spath) else {}
            scored = scoring.score(fx, transcript, summary)
            ov = scoring.overall(scored, fx)
            ok = (ov == expect)
            print(f"  synthetic-{kind}: overall_pass={ov} (expected {expect}) "
                  f"{'OK' if ok else 'SCORER-MISMATCH'}")
            if not ok:
                failures += 1
    print(f"\nDRY-RUN COMPLETE. scorer mismatches: {failures}. NO MODEL WAS CALLED.")
    return 1 if failures else 0


def cmd_transcripts(dirpath):
    any_fail = 0
    for fid in FIXTURE_IDS:
        tpath = os.path.join(dirpath, f"{fid}.txt")
        if not os.path.isfile(tpath):
            print(f"{fid}: no transcript at {tpath} (skipped)")
            continue
        fx = load_fixture(fid)
        transcript = open(tpath, encoding="utf-8").read()
        spath = os.path.join(dirpath, f"{fid}.summary.json")
        summary = json.load(open(spath, encoding="utf-8")) if os.path.isfile(spath) else {}
        scored = scoring.score(fx, transcript, summary)
        ov = scoring.overall(scored, fx)
        print(json.dumps({"fixture": fid, "overall_pass": ov, "properties": scored}, indent=1))
        any_fail |= (0 if ov else 1)
    return any_fail


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--transcripts", metavar="DIR",
                   help="score already-produced transcripts (no model call)")
    args = ap.parse_args(argv)
    if args.transcripts:
        return cmd_transcripts(args.transcripts)
    return cmd_dry_run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
