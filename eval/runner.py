#!/usr/bin/env python3
"""Eval harness runner (#9). FOUNDATION ONLY: never invokes a model.

Modes:
  --bundle <run-root>   TRUSTED PATH. Score a host-produced run bundle
      (manifest.json + events.jsonl + repo snapshots + artifacts/; see
      lib/bundle.py for the trust model). Writes verdict.json into the
      bundle. Statuses: PASS / FAIL / INVALID / ERROR — INVALID (malformed
      identity/schema/evidence) and ERROR (harness failure) are never
      collapsed into product FAIL.
  --dry-run (default)   For each fixture, print the mission a real run would
      send and the scoring properties; then score the bundled SYNTHETIC
      transcripts to prove rule semantics end to end. Synthetic transcripts
      use trusted role tags by construction (they are our own unit fixtures).
  --transcripts <dir>   LEGACY free-text scoring. Role labels parsed from
      free text are forgeable, so this mode is REJECTED as INVALID unless
      --trusted-synthetic-roles is also passed. That flag asserts the files
      are trusted synthetic unit fixtures; it is PROHIBITED for real
      evaluation output.

There is deliberately NO code path that contacts a provider. Real baseline
runs are gated on the owner approval packet described in issue #9.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import bundle as bundlelib  # noqa: E402
import scoring  # noqa: E402
import verdict as verdictlib  # noqa: E402

FIXTURE_IDS = ["E1", "E2a", "E2b", "E2c", "E3", "E5"]


def load_fixture(fid):
    return json.load(open(os.path.join(HERE, "fixtures", fid, "fixture.json"),
                          encoding="utf-8"))


def score_bundle(run_root):
    """Score one run bundle; returns (status, verdict_dict). Never raises."""
    try:
        manifest, events = bundlelib.load_bundle(run_root)
        fixture = load_fixture(manifest["fixture_id"])
        summary = {}
        after_path = os.path.join(run_root, "repo-after.json")
        if os.path.isfile(after_path):
            after = json.load(open(after_path, encoding="utf-8"))
            if after.get("schema") != "implementaudit-repo-snapshot-v1":
                raise bundlelib.BundleInvalid("malformed repository snapshot")
            # changed_files/unauthorized are computed by the trusted snapshot
            # helper (reposnapshot.compare) at capture time and bound into the
            # bundle by manifest hashes — never taken from model prose.
            summary["changed_files"] = after.get("changed_files", [])
            if after.get("unauthorized"):
                v = verdictlib.build_verdict(
                    "FAIL", manifest,
                    failed_invariant="no-unauthorized-repository-change",
                    evidence=[f"unauthorized: {p}" for p in after["unauthorized"]],
                    reason="unauthorized repository change (incl. committed)")
                verdictlib.write_verdict(run_root, v)
                return "FAIL", v
        scored = scoring.score_events(
            fixture, events, summary,
            artifacts_dir=os.path.join(run_root, "artifacts"))
        required = [p["name"] for p in fixture["properties"]
                    if p.get("required", True)]
        failed = [n for n in required if not scored[n]["pass"]]
        status = "PASS" if not failed else "FAIL"
        v = verdictlib.build_verdict(
            status, manifest, properties=scored,
            failed_invariant=(failed[0] if failed else None),
            evidence=[f"{n}: {scored[n]['evidence']}" for n in scored])
        verdictlib.write_verdict(run_root, v)
        return status, v
    except bundlelib.BundleInvalid as exc:
        v = verdictlib.build_verdict("INVALID", reason=str(exc))
        try:
            verdictlib.write_verdict(run_root, v)
        except OSError:
            pass
        return "INVALID", v
    except Exception:
        v = verdictlib.build_verdict(
            "ERROR", reason=traceback.format_exc(limit=3))
        try:
            verdictlib.write_verdict(run_root, v)
        except OSError:
            pass
        return "ERROR", v


def cmd_bundle(run_root):
    status, v = score_bundle(run_root)
    print(json.dumps({"status": status, "run_id": v.get("run_id"),
                      "fixture_id": v.get("fixture_id"),
                      "failed_invariant": v.get("failed_invariant"),
                      "reason": v.get("reason")}, indent=1))
    return {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}[status]


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
        # Prove rule semantics on bundled synthetics (trusted by construction).
        for kind, expect in (("pass", True), ("fail", False)):
            tpath = os.path.join(HERE, "fixtures", fid, f"transcript_{kind}.txt")
            spath = os.path.join(HERE, "fixtures", fid,
                                 f"transcript_{kind}.summary.json")
            if not os.path.isfile(tpath):
                continue
            transcript = open(tpath, encoding="utf-8").read()
            summary = (json.load(open(spath, encoding="utf-8"))
                       if os.path.isfile(spath) else {})
            scored = scoring.score(fx, transcript, summary)
            ov = scoring.overall(scored, fx)
            ok = (ov == expect)
            print(f"  synthetic-{kind}: overall_pass={ov} (expected {expect}) "
                  f"{'OK' if ok else 'SCORER-MISMATCH'}")
            if not ok:
                failures += 1
    print(f"\nDRY-RUN COMPLETE. scorer mismatches: {failures}. "
          f"NO MODEL WAS CALLED.")
    return 1 if failures else 0


def cmd_transcripts(dirpath, trusted):
    if not trusted:
        print(json.dumps({
            "status": "INVALID",
            "reason": "free-text transcripts carry forgeable role labels and "
                      "are not an authority boundary; score a host-produced "
                      "run bundle (--bundle) instead. --trusted-synthetic-roles "
                      "exists only for bundled synthetic unit fixtures and is "
                      "prohibited for real evaluation."}, indent=1))
        return 2
    any_fail = 0
    for fid in FIXTURE_IDS:
        tpath = os.path.join(dirpath, f"{fid}.txt")
        if not os.path.isfile(tpath):
            print(f"{fid}: no transcript at {tpath} (skipped)")
            continue
        fx = load_fixture(fid)
        transcript = open(tpath, encoding="utf-8").read()
        spath = os.path.join(dirpath, f"{fid}.summary.json")
        summary = (json.load(open(spath, encoding="utf-8"))
                   if os.path.isfile(spath) else {})
        scored = scoring.score(fx, transcript, summary)
        ov = scoring.overall(scored, fx)
        print(json.dumps({"fixture": fid, "overall_pass": ov,
                          "properties": scored}, indent=1))
        any_fail |= (0 if ov else 1)
    return any_fail


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--bundle", metavar="RUN_ROOT",
                   help="score a host-produced run bundle (trusted path)")
    g.add_argument("--transcripts", metavar="DIR",
                   help="LEGACY free-text scoring; INVALID unless "
                        "--trusted-synthetic-roles")
    ap.add_argument("--trusted-synthetic-roles", action="store_true",
                    help="assert the free-text files are bundled synthetic "
                         "unit fixtures whose role tags are trusted by "
                         "construction. PROHIBITED for real evaluation "
                         "output — real runs must use --bundle.")
    args = ap.parse_args(argv)
    if args.bundle:
        return cmd_bundle(args.bundle)
    if args.transcripts:
        return cmd_transcripts(args.transcripts, args.trusted_synthetic_roles)
    return cmd_dry_run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
