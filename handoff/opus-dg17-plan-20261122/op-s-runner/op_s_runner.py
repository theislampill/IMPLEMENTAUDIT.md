#!/usr/bin/env python3
"""DRAFT Op S skeleton (adviser): run DG17 structural checks, one record per case.

Usage: python op_s_runner.py --repo <checkout of the candidate> [--suites]
Writes one JSON object per check to stdout and a summary line last. Never pools
failures and never awards anything: a record is evidence for independent
receiving by someone other than the author (#211 per-case oracle discipline).
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def record(case, check, ok, detail):
    print(json.dumps({"schema": "draft.op-s-case-record.v1", "case": case, "check": check,
                      "result": "PASS" if ok else "FAIL", "detail": detail}, sort_keys=True))
    return ok


def unittest_file(path):
    run = subprocess.run([sys.executable, "-B", "-m", "unittest", path.stem], cwd=path.parent,
                         capture_output=True, text=True, timeout=300)
    return run.returncode == 0, run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ""


def cheap_path_cases(repo):
    spec = importlib.util.spec_from_file_location("cwg", repo / "skills/implementaudit/scripts/compile-work-graph.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    results = []
    for args, expected in [((0, 0, 4), "CHEAP_SERIAL"), ((1, 1, 4), "CHEAP_SERIAL"), ((2, 2, 4), "CHEAP_SERIAL"),
                           ((3, 2, 2), "GRAPH_CANDIDATE"), ((3, 2, 1), "CHEAP_SERIAL")]:
        got = module.cheap_path_v1(*args)["mode"]
        results.append(record("M14", "cheap_path_v1%s" % (args,), got == expected, got))
    try:
        module.cheap_path_v1(2, 3, 1); results.append(record("M14", "contradiction refusal", False, "accepted"))
    except module.WorkGraphError as error:
        results.append(record("M14", "contradiction refusal", True, str(error)))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--suites", action="store_true", help="also run the existing repo test bases")
    args = parser.parse_args()
    repo = args.repo.resolve()
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    started = time.time(); results = []
    for case, path in [("N04/N05/H07/M11", HERE / "draft-andon-return/test_validate_audit_andon_return.py"),
                       ("N07/M06", HERE / "draft-jidoka/test_check_jidoka_andon.py")]:
        ok, tail = unittest_file(path)
        results.append(record(case, path.name, ok, tail))
    results += cheap_path_cases(repo)
    if args.suites:
        for case, suite in [("N01/N12/H08/M05", "tests/e2e-mini-audit-loop.test.sh"),
                            ("terminal-cap", "tests/no-terminal-cap.test.sh"),
                            ("B06", "tests/closure-surface-contract.test.sh"),
                            ("N01/N12 base", "tests/run-root-validation.test.sh")]:
            run = subprocess.run(["bash", suite], cwd=repo, capture_output=True, text=True, timeout=600)
            results.append(record(case, suite, run.returncode == 0, (run.stdout + run.stderr).strip().splitlines()[-1:]))
    print(json.dumps({"schema": "draft.op-s-summary.v1", "candidate_head": head,
                      "checks": len(results), "passed": sum(results), "failed": len(results) - sum(results),
                      "seconds": round(time.time() - started, 2), "award": None}))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
