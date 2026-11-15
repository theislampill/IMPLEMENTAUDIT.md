#!/usr/bin/env python3
"""Run three existing deterministic fixture cases; no native episode or grant."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time


ENCODING_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
CASES = (
    ("token-claim", "token_admission_test.py",
     "TokenClaimAdmission.test_claim_cli_publishes_token_only_rotation_and_keeps_fourteen_field_receipt", 1),
    ("c02-cli", "c02_cli_test.py", "CorrectionCLI", 2),
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--encoding", type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    report = json.loads(Path(__file__).with_name("SOURCE_QUALIFICATION.json").read_text())
    out = args.output.absolute()
    out.mkdir(parents=True, exist_ok=True)
    failures = []
    checked = []
    for pin in report["source_pins"]:
        relative = Path(pin["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("source pin path is not repository-relative")
        raw = (root / relative).read_bytes()
        matches = len(raw) == pin["bytes"] and digest(raw) == pin["sha256"]
        checked.append({"path": pin["path"], "matched": matches})
        if not matches:
            failures.append("SOURCE_PIN_CHANGED:" + pin["path"])
    tree_checks = []
    for pin in report["ci_source_tree_pins"]:
        relative = Path(pin["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("source tree path is not repository-relative")
        actual = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD:" + pin["path"]], text=True).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all",
             "--", pin["path"]], text=True)
        matches = actual == pin["git_tree"] and not dirty
        tree_checks.append({"path": pin["path"], "git_tree": actual, "matched": matches})
        if not matches:
            failures.append("SOURCE_TREE_CHANGED:" + pin["path"])
    executable = Path(sys.executable).resolve(strict=True)
    reference = Path("/usr/bin/python3").resolve(strict=True)
    if not executable.samefile(reference):
        failures.append("SYSTEM_PYTHON_REFERENCE_REQUIRED")
    custody = []
    for path in (executable, *executable.parents):
        info = path.stat()
        custody.append({"path": str(path), "uid": info.st_uid,
                        "mode": oct(stat.S_IMODE(info.st_mode))})
        if info.st_uid != 0 or stat.S_IMODE(info.st_mode) & 0o022:
            failures.append("ROOT_OWNED_NONWRITABLE_PYTHON_PATH_REQUIRED")
            break
    preflight = {"schema": "implementaudit.dg18.source-cli-preflight.v1",
                 "authority_ceiling": "SOURCE_FIXTURES_ONLY_NO_NATIVE_ACCEPTANCE",
                 "source_commit": subprocess.check_output(
                     ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                 "python": str(executable), "python_version": sys.version,
                 "source_pins": checked, "source_trees": tree_checks, "python_custody": custody,
                 "failures": failures}
    if args.preflight:
        save(out / "PREFLIGHT.json", preflight)
        print(json.dumps({"stage": "preflight", "failures": failures}))
        return bool(failures)
    if failures:
        save(out / "RESULT.json", {"status": "PREFLIGHT_REFUSED", **preflight})
        return 1
    if args.encoding is None or digest(args.encoding.read_bytes()) != ENCODING_SHA256:
        raise ValueError("the exact pinned tokenizer encoding is required")
    tmp = out / "fixture-tmp"
    claims = tmp / "claim-evidence"
    claims.mkdir(parents=True, exist_ok=False)
    environment = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1",
                   "TMPDIR": str(tmp), "R0039_C02_TEST_TMPDIR": str(tmp),
                   "R0039_CLAIM_EVIDENCE_DIR": str(claims),
                   "R0039_TOKENIZER_ENCODING": str(args.encoding.absolute())}
    results = []
    for label, filename, selection, expected_tests in CASES:
        command = [str(executable), str(root / "fixtures/canonical-state-rotation" / filename),
                   selection, "-v"]
        started = time.monotonic()
        timed_out = False
        try:
            result = subprocess.run(command, cwd=root, env=environment, capture_output=True, timeout=180)
            exit_code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code, stdout, stderr = 124, exc.stdout or b"", exc.stderr or b""
            timed_out = True
        for stream, raw in (("stdout", stdout), ("stderr", stderr)):
            with (out / ("test-" + label + "." + stream + ".txt")).open("xb") as target:
                target.write(raw)
        summaries = re.findall(rb"^Ran (\d+) tests? in .+$", stderr, re.MULTILINE)
        reported_tests = int(summaries[0]) if len(summaries) == 1 else None
        qualified = (exit_code == 0 and reported_tests == expected_tests
                     and re.search(rb"^OK$", stderr, re.MULTILINE) is not None)
        results.append({"case": label, "command": command, "exit_code": exit_code,
                        "expected_tests": expected_tests, "reported_tests": reported_tests,
                        "source_cases_passed_without_skip": qualified,
                        "timeout_root_killed_descendants_unverified": timed_out,
                        "elapsed_seconds": round(time.monotonic() - started, 6),
                        "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr)})
        print(json.dumps(results[-1]), flush=True)
        if timed_out:
            break
    save(out / "RESULT.json", {"schema": "implementaudit.dg18.source-cli-results.v1",
         "authority_ceiling": "SOURCE_FIXTURES_ONLY_NO_NATIVE_ACCEPTANCE",
         "native_episode": False, "model_turn": False, "production_grant": False,
         "original_acceptance_delta": 0, "preflight": preflight, "results": results})
    return int(len(results) != len(CASES)
               or any(not row["source_cases_passed_without_skip"] for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
