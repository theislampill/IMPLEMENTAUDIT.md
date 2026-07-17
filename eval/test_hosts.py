#!/usr/bin/env python3
"""Mock-driven host-adapter tests (#9 phase 2b). NO live mission ever runs
here: the "host" is a local mock script standing in for the CLI, and the
production owner-approval gate is bypassed only via a code-level test
parameter (never an environment switch)."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "lib"))
import adapters as framework  # noqa: E402
import hosts  # noqa: E402
import runner  # noqa: E402

failures = []


def check(name, cond):
    print(f"  [{'OK' if cond else 'XX'}] {name}")
    if not cond:
        failures.append(name)


MOCK = r'''
import json, os, sys, time
scenario = sys.argv[1]
mission = sys.stdin.read()
counter = sys.argv[2] if len(sys.argv) > 2 else None
if counter:
    n = int(open(counter).read()) if os.path.isfile(counter) else 0
    open(counter, "w").write(str(n + 1))
if scenario == "ok-codex":
    print("model: gpt-5.6-luna")
    print("reasoning effort: max")
    print("RUN_ROOT_CREATED at .audit/run-1")
    print("PHASE_WORK_DONE: did the task (evidence: log)")
    print("AUDIT_COMPLETE")
elif scenario == "substituted-codex":
    print("model: some-other-model")
    print("output text")
elif scenario == "no-provenance":
    print("output text with no model line")
elif scenario == "nonzero":
    sys.exit(3)
elif scenario == "hang":
    time.sleep(30)
elif scenario == "ok-claude":
    print(json.dumps({"result": "RUN_ROOT_CREATED\nPHASE_WORK_DONE: done (evidence)\nAUDIT_COMPLETE",
                      "modelUsage": {"claude-opus-4-8": {}}}))
elif scenario == "substituted-claude":
    print(json.dumps({"result": "text", "modelUsage": {"claude-haiku-4-5": {}}}))
elif scenario == "malformed-claude":
    print("this is not json at all")
elif scenario == "env-echo":
    print("model: gpt-5.6-luna")
    print("reasoning effort: max")
    print("CODEX_HOME=" + os.environ.get("CODEX_HOME", "<unset>"))
    print("SENTINEL=" + os.environ.get("EVAL_TEST_SENTINEL", "<absent>"))
elif scenario == "leaky":
    print("model: gpt-5.6-luna")
    print("here is a token: sk-THIS-LOOKS-LIKE-A-KEY")
elif scenario == "write-canonical":
    target = os.environ.get("EVAL_CANONICAL_DIR")
    open(os.path.join(target, "TAMPERED.txt"), "w").write("x")
    print("model: gpt-5.6-luna")
    print("done")
elif scenario == "wrong-effort":
    print("model: gpt-5.6-luna")
    print("reasoning effort: low")
    print("output")
'''


def make_adapter(tmp, scenario, kind="codex", counter=None, checkout=None):
    mock = os.path.join(tmp, "mock_host.py")
    if not os.path.isfile(mock):
        open(mock, "w", encoding="utf-8").write(MOCK)
    argv = [sys.executable, mock, scenario] + ([counter] if counter else [])
    if kind == "codex":
        a = hosts.CodexAdapter(codex_home=os.path.join(tmp, "codex-home"),
                               product_checkout=checkout)
        os.makedirs(a.codex_home, exist_ok=True)
    else:
        a = hosts.ClaudeAdapter(config_dir=os.path.join(tmp, "claude-cfg"),
                                product_checkout=checkout)
        os.makedirs(a.config_dir, exist_ok=True)
    a.host_argv_template = argv
    a.timeout_s = 5
    if kind == "codex":
        a.preflight = lambda: None  # version/auth gates unit-tested below
    return a


_seq = [0]


def run(a, tmp, run_id, fixture_id="B0"):
    croot = os.path.join(tmp, "custody")
    os.makedirs(croot, exist_ok=True)
    _seq[0] += 1
    work = os.path.join(tmp, f"work-{_seq[0]}-{run_id}")
    os.makedirs(work)
    return a.run_mission(fixture_id, croot, run_id, work,
                         _test_gate=lambda: None)


def main():
    tmp = tempfile.mkdtemp(prefix="eval-hosts-")
    try:
        # 1. production gate refuses without token and unconditionally in CI
        a = make_adapter(tmp, "ok-codex")
        os.environ.pop("IMPLEMENTAUDIT_BASELINE_APPROVAL", None)
        try:
            a.run_mission("B0", tmp, "gated", os.path.join(tmp, "wg"))
            check("H1 production-gate-fails-closed", False)
        except framework.AdapterError:
            check("H1 production-gate-fails-closed", True)

        # 2. happy path (codex mock): identity match, bundle written, PASS
        r = run(make_adapter(tmp, "ok-codex"), tmp, "r-ok")
        ok = r.kind == "ok" and r.resolved_model == "gpt-5.6-luna"
        if ok:
            status, v = runner.score_bundle(
                r.detail, repo_dir=None)
            ok = status in ("PASS", "FAIL")  # scored end to end
        check("H2 codex-happy-path-scoreable", ok)

        # 3. substitution fails closed and is recorded
        try:
            run(make_adapter(tmp, "substituted-codex"), tmp, "r-sub")
            check("H3 substitution-fails-closed", False)
        except framework.AdapterError as exc:
            check("H3 substitution-fails-closed",
                  "substitution" in str(exc))

        # 4. missing provenance fails closed
        try:
            run(make_adapter(tmp, "no-provenance"), tmp, "r-noprov")
            check("H4 missing-provenance-fails-closed", False)
        except framework.AdapterError as exc:
            check("H4 missing-provenance-fails-closed",
                  "provenance" in str(exc))

        # 5. nonzero exit => ERROR class, preserved
        r = run(make_adapter(tmp, "nonzero"), tmp, "r-exit")
        check("H5 nonzero-exit-ERROR",
              r.kind == "error" and "exit 3" in r.detail)

        # 6. timeout => ERROR class
        a = make_adapter(tmp, "hang")
        a.timeout_s = 2
        r = run(a, tmp, "r-hang")
        check("H6 timeout-ERROR", r.kind == "error" and "timeout" in r.detail)

        # 7. malformed structured output => INVALID class (claude)
        r = run(make_adapter(tmp, "malformed-claude", kind="claude"),
                tmp, "r-mal")
        check("H7 malformed-output-INVALID", r.kind == "invalid")

        # 8. claude happy path resolves claude-opus-4-8
        r = run(make_adapter(tmp, "ok-claude", kind="claude"), tmp, "r-cl")
        check("H8 claude-happy-path",
              r.kind == "ok" and r.resolved_model == "claude-opus-4-8")

        # 9. claude substitution fails closed
        try:
            run(make_adapter(tmp, "substituted-claude", kind="claude"),
                tmp, "r-clsub")
            check("H9 claude-substitution-fails-closed", False)
        except framework.AdapterError:
            check("H9 claude-substitution-fails-closed", True)

        # 10. clean environment: session sentinel never reaches the host;
        #     temp home (not real home) is what the host sees
        os.environ["EVAL_TEST_SENTINEL"] = "should-not-leak"
        try:
            r = run(make_adapter(tmp, "env-echo"), tmp, "r-env")
        finally:
            os.environ.pop("EVAL_TEST_SENTINEL", None)
        content = r.raw_events[0]["content"] if r.raw_events else ""
        check("H10 env-injection+temp-home",
              r.kind == "ok"
              and "SENTINEL=<absent>" in content
              and "codex-home" in content
              and ".codex" not in content.replace("codex-home", ""))

        # 11. credential sentinel in output aborts (nonretention scan)
        try:
            run(make_adapter(tmp, "leaky"), tmp, "r-leak")
            check("H11 credential-scan-aborts", False)
        except framework.AdapterError as exc:
            check("H11 credential-scan-aborts", "sentinel" in str(exc))

        # 12. run-root collision refused (custody layer)
        run(make_adapter(tmp, "ok-codex"), tmp, "r-coll")
        try:
            run(make_adapter(tmp, "ok-codex"), tmp, "r-coll")
            check("H12 run-root-collision", False)
        except framework.custody.CustodyError:
            check("H12 run-root-collision", True)

        # 13. canonical-checkout write attempt: the REAL run_mission guard
        # (payload hash before vs after) must abort. product_identity is
        # stubbed so a plain directory can stand in for the tagged checkout.
        canon = os.path.join(tmp, "canonical")
        os.makedirs(canon)
        open(os.path.join(canon, "SKILL.md"), "w").write("payload\n")
        orig_pi = framework.product_identity
        framework.product_identity = lambda checkout, expected_tag="v0.3.1.0": {
            "product_tag": "v0.3.1.0", "product_commit": "b" * 40,
            "product_tree": "a" * 40}
        try:
            a = make_adapter(tmp, "write-canonical", checkout=canon)
            a.stage_payload = lambda repo: None
            base_env = a._mission_env
            a._mission_env = lambda repo: {**base_env(repo),
                                           "EVAL_CANONICAL_DIR": canon}
            try:
                run(a, tmp, "r-canon")
                check("H13 canonical-write-aborts", False)
            except framework.AdapterError as exc:
                check("H13 canonical-write-aborts",
                      "canonical payload checkout was modified" in str(exc))
        finally:
            framework.product_identity = orig_pi

        # 14. no hidden retry: host invoked exactly once per mission
        counter = os.path.join(tmp, "count.txt")
        run(make_adapter(tmp, "ok-codex", counter=counter), tmp, "r-once")
        check("H14 no-hidden-retry", open(counter).read().strip() == "1")

        # 16. concatenated slug rejected at construction
        for slug in ("luna-max", "gpt-5.6-luna-max"):
            try:
                hosts.CodexAdapter(requested_model=slug,
                                   codex_home=os.path.join(tmp, "ch"))
                check(f"H16 slug-rejected {slug}", False)
            except framework.AdapterError as exc:
                check(f"H16 slug-rejected {slug}",
                      "concatenated slug" in str(exc))
        # 17. old CLI version rejected; current accepted (stub binaries)
        oldbin = os.path.join(tmp, "oldcodex.py")
        open(oldbin, "w").write("print('codex-cli 0.130.0-alpha.5')")
        newbin = os.path.join(tmp, "newcodex.py")
        open(newbin, "w").write("print('codex-cli 0.144.5')")
        import subprocess as _sp
        a = hosts.CodexAdapter(codex_home=os.path.join(tmp, "ch2"))
        a.codex_binary = None  # use argv-wrapped stubs
        def _ver(binpath):
            b = hosts.CodexAdapter(codex_home=os.path.join(tmp, "ch3"))
            b.codex_binary = sys.executable
            orig = _sp.run
            def fake_run(argv, **kw):
                return orig([sys.executable, binpath], **{k: v for k, v in kw.items() if k in ("capture_output", "text")})
            hosts.subprocess.run = fake_run
            try:
                return b.check_cli_version()
            finally:
                hosts.subprocess.run = orig
        try:
            _ver(oldbin)
            check("H17 old-cli-rejected", False)
        except framework.AdapterError as exc:
            check("H17 old-cli-rejected", "below the required" in str(exc))
        check("H17b current-cli-accepted", _ver(newbin) == (0, 144, 5))
        # 18. reasoning-effort substitution fails closed
        try:
            run(make_adapter(tmp, "wrong-effort"), tmp, "r-effort")
            check("H18 effort-substitution-fails-closed", False)
        except framework.AdapterError as exc:
            check("H18 effort-substitution-fails-closed",
                  "reasoning-effort substitution" in str(exc))
        # 15. refusing the REAL codex home
        a = make_adapter(tmp, "ok-codex")
        a.codex_home = os.path.expanduser("~/.codex")
        try:
            run(a, tmp, "r-realhome")
            check("H15 real-home-refused", False)
        except framework.AdapterError as exc:
            check("H15 real-home-refused", "REAL codex home" in str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print("HOST-ADAPTER TESTS FAIL:", ", ".join(failures))
        return 1
    print("HOST-ADAPTER TESTS OK: mock-driven; no live mission; gate "
          "fail-closed; no model called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
