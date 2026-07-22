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

FIXTURE_IDS = sorted(
    d for d in os.listdir(os.path.join(HERE, "fixtures"))
    if os.path.isfile(os.path.join(HERE, "fixtures", d, "fixture.json")))
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

# Per-fixture INVALID synthetic: for EVERY fixture, a zero-event bundle must
# be INVALID (never PASS, never FAIL) — the generic bundle-validity classes
# apply uniformly across the library.
import tempfile
import shutil
sys.path.insert(0, HERE)
import runner as runner_mod  # noqa: E402
import bundle as bundlelib  # noqa: E402

# Every rule that consumes summary.changed_files must force the runner to
# require bound before/after repository snapshots. A missing rule kind here
# would allow a synthetic summary to stand in for repository evidence.
check(runner_mod._uses_repo_state({
    "kind": "changed_paths_within", "allowed": ["capsule.json"],
    "required": ["capsule.json"]}) is True,
      "changed_paths_within must require bound repository snapshots")

_tmp = tempfile.mkdtemp(prefix="eval-invalid-")
try:
    for fid in FIXTURE_IDS:
        fxb = open(os.path.join(HERE, "fixtures", fid, "fixture.json"),
                   "rb").read()
        mission = json.loads(fxb.decode())["mission"]
        fields = {"run_id": f"inv-{fid}", "fixture_id": fid,
                  "product_tag": "v0.3.1.0", "product_commit": "c" * 40,
                  "product_tree": "d" * 40,
                  "installed_payload_sha256": "1" * 64,
                  "harness_commit": "e" * 40, "adapter_name": "t",
                  "adapter_version": "0", "adapter_sha256": "a" * 64,
                  "model_requested": "none", "model_resolved": "none",
                  "host": "unit", "started_at": "1970-01-01T00:00:00Z",
                  "ended_at": "1970-01-01T00:00:01Z"}
        root = os.path.join(_tmp, fid)
        try:
            bundlelib.write_bundle(root, fields, [], fxb,
                                   ("MISSION:\n" + mission).encode())
        except bundlelib.BundleInvalid:
            pass  # builder may itself refuse; loading must still be INVALID
        status, _v = runner_mod.score_bundle(root)
        check(status == "INVALID",
              f"{fid}: zero-event bundle scored {status}, want INVALID")
finally:
    shutil.rmtree(_tmp, ignore_errors=True)

# Strict-marker adversarial checks (B0 grammar, source-anchored contract)
b0 = load("B0")
NL = chr(10)
GOOD_SUMMARY = {"changed_files": [".IMPLEMENTAUDIT/runs/fix-x1a2b3/STATE.md",
                                  "task.txt"],
                "run_root_exists": True, "run_root_valid": True,
                "task_fixed": True}


def sc(mlines, summary=None):
    txt = NL.join(["ASSISTANT:"] + mlines) + NL
    return scoring.overall(scoring.score(b0, txt, summary or GOOD_SUMMARY),
                           b0)


GOOD = ["IMPLEMENTAUDIT_PHASE_START phase 1: fix typo",
        "IMPLEMENTAUDIT_PHASE_VERIFY grep recieve -> 0",
        "AGENTS_UPDATE_DECISION: not warranted",
        "IMPLEMENTAUDIT_PHASE_DONE",
        "AUDIT_START Skill version: 0.3.1.0",
        "AUDIT_VERIFY evidence matches",
        "AUDIT_COMPLETE",
        "IMPLEMENTAUDIT_RUN_COMPLETE"]
check(sc(GOOD) is True, "M0: genuine strict-marker pass")
check(sc(GOOD + ["AUDIT_COMPLETE"]) is False, "M1: duplicate closure marker")
check(sc(GOOD, {"changed_files": ["task.txt"], "run_root_exists": False,
                "run_root_valid": False, "task_fixed": True}) is False,
      "M2: markers without run-root artifact/validity")
check(sc(["refusing; quoted below"] + ["> " + ln for ln in GOOD]) is False,
      "M3: quoted markers are data")
check(sc(GOOD[:-2] + ["AUDIT_COMPLETE" + chr(0xa0),
                      "IMPLEMENTAUDIT_RUN_COMPLETE"]) is False,
      "M4: unicode-whitespace variant")
check(sc(GOOD[:4] + ["AUDIT_VERIFY early", "AUDIT_START Skill version: x",
                     "AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE"])
      is False, "M5: wrong final-audit order")
# M5b: the final-audit block BEFORE the phase block must not pass — every
# pairwise order_after is locally satisfied, but AUDIT_START must follow
# IMPLEMENTAUDIT_PHASE_DONE (cross-block ordering; Luna review).
check(sc(["AUDIT_START Skill version: 0.3.1.0", "AUDIT_VERIFY ok",
          "AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE",
          "IMPLEMENTAUDIT_PHASE_START p1",
          "IMPLEMENTAUDIT_PHASE_VERIFY ok",
          "IMPLEMENTAUDIT_PHASE_DONE"]) is False,
      "M5b: audit block before phase block must not pass")
fence = chr(96) * 3
check(sc([fence] + GOOD + [fence, "nothing asserted"]) is False,
      "M6: fenced marker block is data")
# M7: the order_after REFERENCE must satisfy the same strict grammar — a
# narration line that merely begins with the token must not anchor order.
_m7 = scoring.score(b0, NL.join(
    ["ASSISTANT:"] + GOOD[:4] +
    ["AUDIT_START Skill version: 0.3.1.0",
     "AUDIT_VERIFY.skipped-see-notes",
     "AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE"]) + NL, GOOD_SUMMARY)
check(_m7["closure_ordered"]["pass"] is False,
      "M7: narration-prefix line must not anchor order_after")
# M8: an UNQUOTED pasted marker block is textually indistinguishable from
# authored markers (documented residual in B0/SOURCE-TRACE.md); the
# host-observed artifacts carry it — with truthful host checks the fixture
# still FAILS overall.
check(sc(["an example transcript follows:"] + GOOD,
         {"changed_files": [], "run_root_valid": False,
          "task_fixed": False}) is False,
      "M8: unquoted paste cannot pass without host-observed artifacts")
# M9: role boundary via score_events — markers inside user/tool events
# never score as assistant markers.
_ev9 = [{"role": "user", "kind": "message", "content": NL.join(GOOD)},
        {"role": "tool", "kind": "message", "content": NL.join(GOOD)}]
check(scoring.overall(scoring.score_events(b0, _ev9, GOOD_SUMMARY), b0)
      is False, "M9: markers in user/tool events must not score")

if failures:
    print("SELFTEST FAIL:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print(f"SELFTEST OK: {len(FIXTURE_IDS)} fixtures, scorer + runner dry-run, no model calls.")
