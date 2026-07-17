#!/usr/bin/env python3
"""Adapter-framework tests: replay end-to-end (no model), gate fail-closed,
seeded repo lifecycle, capture-time identity honesty."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "lib"))
import adapters  # noqa: E402
import reposnapshot  # noqa: E402
import runner  # noqa: E402

failures = []


def check(name, cond):
    print(f"  [{'OK' if cond else 'XX'}] {name}")
    if not cond:
        failures.append(name)


def main():
    tmp = tempfile.mkdtemp(prefix="eval-adapter-")
    try:
        # 1. gate fails closed (no token; and unconditionally in CI)
        os.environ.pop("IMPLEMENTAUDIT_BASELINE_APPROVAL", None)
        try:
            adapters.require_owner_approval()
            check("gate-no-token", False)
        except adapters.AdapterError:
            check("gate-no-token", True)
        os.environ["CI"] = "1"
        tok = os.path.join(tmp, "token")
        open(tok, "w").write("x")
        os.environ["IMPLEMENTAUDIT_BASELINE_APPROVAL"] = tok
        try:
            adapters.require_owner_approval()
            check("gate-refuses-in-CI", False)
        except adapters.AdapterError:
            check("gate-refuses-in-CI", True)
        os.environ.pop("CI", None)
        os.environ.pop("IMPLEMENTAUDIT_BASELINE_APPROVAL", None)

        # 2. seeded disposable repo + snapshots + replay bundle -> PASS
        repo = adapters.seed_fixture_repo("E5", tmp)
        before = reposnapshot.snapshot(repo)
        # (a model WOULD act here; replay uses pre-captured records)
        after = reposnapshot.snapshot(repo)
        custody_root = os.path.join(tmp, "runs")
        os.makedirs(custody_root)
        obs = json.dumps({"current_verdict": "accept", "p1_verdict": "reject",
                          "p2_verdict": "accept"}).encode()
        raw = [{"role": "assistant",
                "content": "The current answer is correct, but only correct "
                           "by luck: the rule is not truth-connected — P1 "
                           "(correct without MAGIC) is rejected."}]
        _m, bundle_root = adapters.ReplayAdapter().build(
            "E5", raw, "replay-run-1", custody_root,
            repo_before=before, repo_after=after, repo_dir=repo,
            artifacts={"result.json": obs})
        status, v = runner.score_bundle(bundle_root, repo_dir=repo)
        check("replay-end-to-end-PASS", status == "PASS")
        check("verdict-binds-bundle-hash", bool(v.get("bundle_sha256")))
        # 3. create-once: same run id refused
        try:
            adapters.ReplayAdapter().build("E5", raw, "replay-run-1",
                                           custody_root)
            check("replay-run-collision-refused", False)
        except Exception:
            check("replay-run-collision-refused", True)
        # 4. capture-time product identity refuses a non-tag checkout
        try:
            adapters.product_identity(repo, expected_tag="v0.0.0-none")
            check("product-identity-honest", False)
        except adapters.AdapterError:
            check("product-identity-honest", True)
        # 5. payload hash is deterministic
        h1 = adapters.payload_hash(os.path.join(HERE, "fixtures", "E5"))
        h2 = adapters.payload_hash(os.path.join(HERE, "fixtures", "E5"))
        check("payload-hash-deterministic", h1 == h2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print("ADAPTER TESTS FAIL:", ", ".join(failures))
        return 1
    print("ADAPTER TESTS OK: replay path proven end to end, gate fail-closed,"
          " no model called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
