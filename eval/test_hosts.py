#!/usr/bin/env python3
"""Mock-driven host-adapter tests (#9 phase 2b). NO live mission ever runs
here: the "host" is a local mock script standing in for the CLI, and the
production owner-approval gate is bypassed only via a code-level test
parameter (never an environment switch). Codex mocks write REAL session
files into the temp CODEX_HOME so the bound-session identity path (cwd +
not-before window, exactly-one-match) is what gets tested — there is no
stdout-provenance shortcut left to test."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "lib"))
import adapters as framework  # noqa: E402
import hosts  # noqa: E402
import reconcile as reconcilelib  # noqa: E402
import runner  # noqa: E402

failures = []


def check(name, cond):
    print(f"  [{'OK' if cond else 'XX'}] {name}")
    if not cond:
        failures.append(name)


MOCK = r'''
import datetime, json, os, sys, time
scenario = sys.argv[1]
mission = sys.stdin.read()
counter = sys.argv[2] if len(sys.argv) > 2 else None
if counter:
    n = int(open(counter).read()) if os.path.isfile(counter) else 0
    open(counter, "w").write(str(n + 1))


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def write_session(model="gpt-5.6-luna", effort="max",
                  sandbox="workspace-write", name=None, agent_msgs=None,
                  omit_model=False, omit_effort=False):
    home = os.environ.get("CODEX_HOME")
    if not home:
        return
    d = os.path.join(home, "sessions", "2026")
    os.makedirs(d, exist_ok=True)
    name = name or ("rollout-%d.jsonl" % os.getpid())
    ts = now()
    tc = {"turn_id": "t1", "cwd": os.getcwd(),
          "approval_policy": "never", "sandbox_policy": {"type": sandbox}}
    if not omit_model:
        tc["model"] = model
    if not omit_effort:
        tc["effort"] = effort
    lines = [{"timestamp": ts, "type": "session_meta",
              "payload": {"session_id": "mock-" + name,
                          "id": "mock-" + name, "timestamp": ts,
                          "cwd": os.getcwd(), "cli_version": "0.144.5"}},
             {"timestamp": ts, "type": "turn_context", "payload": tc}]
    for m in (agent_msgs or []):
        lines.append({"timestamp": ts, "type": "event_msg",
                      "payload": {"type": "agent_message", "message": m}})
    with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
        for ln in lines:
            fh.write(json.dumps(ln) + "\n")


MSGS = ["IMPLEMENTAUDIT_PHASE_START p1\nIMPLEMENTAUDIT_PHASE_VERIFY ok\n"
        "IMPLEMENTAUDIT_PHASE_DONE",
        "AUDIT_START Skill version: 0.3.1.0\nAUDIT_VERIFY ok\n"
        "AUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE"]

if scenario == "ok-codex":
    write_session(agent_msgs=MSGS)
    for m in MSGS:
        print(json.dumps({"timestamp": now(), "type": "agent_message",
                          "message": m}))
elif scenario == "substituted-codex":
    write_session(model="some-other-model", agent_msgs=["output text"])
    print(json.dumps({"type": "agent_message", "message": "output text"}))
elif scenario == "no-provenance":
    write_session(omit_model=True, agent_msgs=["output text"])
    print(json.dumps({"type": "agent_message", "message": "output text"}))
elif scenario == "wrong-effort":
    write_session(effort="low", agent_msgs=["output text"])
    print(json.dumps({"type": "agent_message", "message": "output text"}))
elif scenario == "no-effort":
    write_session(omit_effort=True, agent_msgs=["output text"])
    print(json.dumps({"type": "agent_message", "message": "output text"}))
elif scenario == "double-session":
    write_session(name="a.jsonl", agent_msgs=["output text"])
    write_session(name="b.jsonl", agent_msgs=["output text"])
    print(json.dumps({"type": "agent_message", "message": "output text"}))
elif scenario == "session-mismatch":
    write_session(agent_msgs=["a different message entirely"])
    print(json.dumps({"type": "agent_message",
                      "message": "not in the session record"}))
elif scenario == "nonzero":
    sys.exit(3)
elif scenario == "hang":
    time.sleep(30)
elif scenario == "ok-claude":
    for t in ("intermediate assistant note",
              "AUDIT_COMPLETE final summary"):
        print(json.dumps({"type": "assistant",
                          "message": {"model": "claude-opus-4-8",
                                      "content": [{"type": "text",
                                                   "text": t}]}}))
    print(json.dumps({"type": "result",
                      "result": "AUDIT_COMPLETE final summary",
                      "modelUsage": {
                          "claude-opus-4-8": {"outputTokens": 100},
                          "claude-haiku-4-5": {"outputTokens": 5}}}))
elif scenario == "substituted-claude":
    print(json.dumps({"type": "assistant",
                      "message": {"model": "claude-haiku-4-5",
                                  "content": [{"type": "text",
                                               "text": "text"}]}}))
    print(json.dumps({"type": "result", "result": "text",
                      "modelUsage": {"claude-haiku-4-5": {}}}))
elif scenario == "malformed-claude":
    print("this is not json at all")
elif scenario == "truncated-claude":
    # a valid assistant event but NO trailing result event (truncation)
    print(json.dumps({"type": "assistant", "session_id": "trunc",
                      "message": {"model": "claude-opus-4-8",
                                  "content": [{"type": "text",
                                               "text": "AUDIT_COMPLETE"}]}}))
elif scenario == "env-echo":
    envmsg = ("CODEX_HOME=" + os.environ.get("CODEX_HOME", "<unset>") +
              " SENTINEL=" +
              os.environ.get("EVAL_TEST_SENTINEL", "<absent>"))
    write_session(agent_msgs=[envmsg])
    print(json.dumps({"type": "agent_message", "message": envmsg}))
elif scenario == "leaky":
    leak = "here is a token: sk-ant-api03-ABCdef0123456789TOKEN"
    write_session(agent_msgs=[leak])
    print(json.dumps({"type": "agent_message", "message": leak}))
elif scenario == "write-canonical":
    write_session(agent_msgs=["did the task"])
    target = os.environ.get("EVAL_CANONICAL_DIR")
    open(os.path.join(target, "TAMPERED.txt"), "w").write("x")
    print(json.dumps({"type": "agent_message", "message": "did the task"}))
'''


def make_adapter(tmp, scenario, kind="codex", counter=None, checkout=None,
                 home=None):
    mock = os.path.join(tmp, "mock_host.py")
    if not os.path.isfile(mock):
        open(mock, "w", encoding="utf-8").write(MOCK)
    argv = [sys.executable, mock, scenario] + ([counter] if counter else [])
    if kind == "codex":
        a = hosts.CodexAdapter(
            codex_home=home or os.path.join(tmp, "codex-home"),
            product_checkout=checkout)
        os.makedirs(a.codex_home, exist_ok=True)
        a.preflight = lambda: None  # version/auth gates unit-tested below
    else:
        a = hosts.ClaudeAdapter(config_dir=os.path.join(tmp, "claude-cfg"),
                                product_checkout=checkout)
        os.makedirs(a.config_dir, exist_ok=True)
    a.host_argv_template = argv
    a.timeout_s = 5
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

        # 2. happy path (codex mock): bound-session identity, intermediate
        # agent messages retained, full lifecycle custody records
        r = run(make_adapter(tmp, "ok-codex"), tmp, "r-ok")
        ok = r.kind == "ok" and r.resolved_model == "gpt-5.6-luna"
        ok = ok and len(r.raw_events) == 2
        if ok:
            status, v = runner.score_bundle(r.detail, repo_dir=None)
            ok = status in ("PASS", "FAIL")
            rr = os.path.dirname(r.detail)
            for f in ("run-intent.json", "process-started.json",
                      "terminal.json"):
                ok = ok and os.path.isfile(os.path.join(rr, f))
            term = json.load(open(os.path.join(rr, "terminal.json")))
            ok = ok and term["started_at"].startswith("20")
        check("H2 codex-happy-path+lifecycle-custody", ok)
        # H19: a launched call that dies still terminalizes (Phase-E class)
        r19 = run(make_adapter(tmp, "nonzero"), tmp, "r-term")
        term = json.load(open(os.path.join(tmp, "custody", "r-term",
                                           "terminal.json")))
        check("H19 launched-call-always-terminalizes",
              r19.kind == "error" and term["kind"] == "error"
              and term["spawned"] is True)

        # 3. substitution terminalizes INVALID and is recorded
        r = run(make_adapter(tmp, "substituted-codex"), tmp, "r-sub")
        check("H3 substitution-fails-closed",
              r.kind == "invalid" and "substitution" in r.detail)

        # 4. missing provenance terminalizes INVALID
        r = run(make_adapter(tmp, "no-provenance"), tmp, "r-noprov")
        check("H4 missing-provenance-fails-closed",
              r.kind == "invalid" and "provenance" in r.detail)

        # 5. nonzero exit => ERROR class, preserved WITH raw host output at
        # the run root (custody must survive a nonzero-exit ERROR)
        r = run(make_adapter(tmp, "nonzero"), tmp, "r-exit")
        rr5 = os.path.join(tmp, "custody", "r-exit")
        check("H5 nonzero-exit-ERROR",
              r.kind == "error" and "exit 3" in r.detail
              and os.path.isfile(os.path.join(rr5, "host-stdout.raw"))
              and os.path.isfile(os.path.join(rr5, "host-stderr.raw")))

        # 6. timeout => ERROR class
        a = make_adapter(tmp, "hang")
        a.timeout_s = 2
        r = run(a, tmp, "r-hang")
        check("H6 timeout-ERROR", r.kind == "error" and "timeout" in r.detail)

        # 7. malformed structured output => INVALID class (claude)
        r = run(make_adapter(tmp, "malformed-claude", kind="claude"),
                tmp, "r-mal")
        check("H7 malformed-output-INVALID", r.kind == "invalid")

        # 8. claude happy path: root model from HOST-ASSIGNED assistant
        # events; intermediate events retained; auxiliary model REPORTED
        # (never silently ignored, never resolved-by-token-count)
        r = run(make_adapter(tmp, "ok-claude", kind="claude"), tmp, "r-cl")
        ok = r.kind == "ok" and r.resolved_model == "claude-opus-4-8"
        ok = ok and len(r.raw_events) == 2
        if ok:
            m = json.load(open(os.path.join(r.detail, "manifest.json")))
            obs = m.get("models_observed", [])
            aux = [o for o in obs if o.get("model") == "claude-haiku-4-5"]
            ok = (bool(aux) and aux[0].get("host_internal_auxiliary") is True
                  and any(o.get("role") == "root-assistant-events" and
                          o.get("model") == "claude-opus-4-8" for o in obs))
        check("H8 claude-events+models-observed", ok)

        # 9. claude substitution terminalizes INVALID
        r = run(make_adapter(tmp, "substituted-claude", kind="claude"),
                tmp, "r-clsub")
        check("H9 claude-substitution-fails-closed", r.kind == "invalid")

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

        # 11. credential sentinel terminalizes INVALID, bundle QUARANTINED,
        #     value never echoed in the error
        r = run(make_adapter(tmp, "leaky"), tmp, "r-leak")
        rr = os.path.join(tmp, "custody", "r-leak")
        check("H11 credential-scan-quarantines",
              r.kind == "invalid" and "credential" in r.detail
              and "sk-ant-api03-ABCdef0123456789TOKEN" not in r.detail
              and os.path.isdir(os.path.join(rr, "quarantine-bundle"))
              and not os.path.isdir(os.path.join(rr, "bundle")))

        # 12. run-root collision refused (custody layer)
        run(make_adapter(tmp, "ok-codex"), tmp, "r-coll")
        try:
            run(make_adapter(tmp, "ok-codex"), tmp, "r-coll")
            check("H12 run-root-collision", False)
        except framework.custody.CustodyError:
            check("H12 run-root-collision", True)

        # 13. canonical-checkout write attempt terminalizes INVALID via the
        # REAL run_mission guard (product_identity stubbed for a plain dir).
        canon = os.path.join(tmp, "canonical")
        os.makedirs(canon)
        open(os.path.join(canon, "SKILL.md"), "w").write("payload" + chr(10))
        orig_pi = framework.product_identity
        framework.product_identity = (
            lambda checkout, expected_tag="v0.3.1.0": {
                "product_tag": "v0.3.1.0", "product_commit": "b" * 40,
                "product_tree": "a" * 40})
        try:
            a = make_adapter(tmp, "write-canonical", checkout=canon)
            a.stage_payload = lambda repo: None
            base_env = a._mission_env
            a._mission_env = lambda repo: {**base_env(repo),
                                           "EVAL_CANONICAL_DIR": canon}
            r = run(a, tmp, "r-canon")
            check("H13 canonical-write-aborts",
                  r.kind == "invalid" and
                  "canonical payload checkout" in r.detail)
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

        def _ver(binpath):
            b = hosts.CodexAdapter(codex_home=os.path.join(tmp, "ch3"))
            b.codex_binary = sys.executable
            orig = _sp.run

            def fake_run(argv, **kw):
                return orig([sys.executable, binpath],
                            **{k: v for k, v in kw.items()
                               if k in ("capture_output", "text")})
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
        # 18. reasoning-effort substitution terminalizes INVALID
        r = run(make_adapter(tmp, "wrong-effort"), tmp, "r-effort")
        check("H18 effort-substitution-fails-closed",
              r.kind == "invalid" and
              "reasoning-effort substitution" in r.detail)
        # 15. refusing the REAL codex home
        a = make_adapter(tmp, "ok-codex")
        a.codex_home = os.path.expanduser("~/.codex")
        r = run(a, tmp, "r-realhome")
        check("H15 real-home-refused",
              r.kind == "invalid" and "REAL codex home" in r.detail)
        # 15b. Claude symmetrically refuses the REAL ~/.claude config home
        a = make_adapter(tmp, "ok-claude", kind="claude")
        a.config_dir = os.path.expanduser("~/.claude")
        r = run(a, tmp, "r-realclaude")
        check("H15b claude-real-home-refused",
              r.kind == "invalid" and "REAL claude config home" in r.detail)
        # 29. truncated stream-json (assistant event, no result) => INVALID
        r = run(make_adapter(tmp, "truncated-claude", kind="claude"),
                tmp, "r-trunc")
        check("H29 truncated-stream-INVALID",
              r.kind == "invalid" and "truncated" in r.detail)

        # 20. crash reconciler: stale intents are adjudicated truthfully
        rec_root = os.path.join(tmp, "rec-custody")
        os.makedirs(rec_root)

        def mkrun(name, started=None, bundle=False, terminal=False):
            d = os.path.join(rec_root, name)
            os.makedirs(d)
            json.dump({"run_id": name},
                      open(os.path.join(d, "run-intent.json"), "w"))
            if started is not None:
                json.dump({"pid": started},
                          open(os.path.join(d, "process-started.json"),
                               "w"))
            if bundle:
                os.makedirs(os.path.join(d, "bundle"))
                json.dump({}, open(os.path.join(d, "bundle",
                                                "manifest.json"), "w"))
            if terminal:
                json.dump({"kind": "ok"},
                          open(os.path.join(d, "terminal.json"), "w"))
            return d

        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        mkrun("rec-nostart")
        mkrun("rec-live", started=os.getpid())
        mkrun("rec-dead", started=dead.pid)
        mkrun("rec-forensic", started=dead.pid, bundle=True)
        mkrun("rec-done", started=dead.pid, terminal=True)
        results = {r_["run_id"]: r_["disposition"]
                   for r_ in reconcilelib.reconcile_custody(rec_root)}
        t = lambda n: json.load(open(os.path.join(rec_root, n,
                                                  "terminal.json")))
        check("H20a launch-not-confirmed",
              results.get("rec-nostart") == "launch-not-confirmed"
              and t("rec-nostart")["reconciled"] is True)
        check("H20b live-process-untouched",
              results.get("rec-live") == "running"
              and not os.path.isfile(os.path.join(
                  rec_root, "rec-live", "terminal.json")))
        check("H20c terminal-state-unverified",
              results.get("rec-dead") == "terminal-state-unverified"
              and t("rec-dead")["kind"] == "error")
        check("H20d forensic-import-candidate",
              results.get("rec-forensic") == "forensic-import-candidate")
        check("H20e existing-terminal-untouched",
              "rec-done" not in results
              and t("rec-done")["kind"] == "ok")

        # 21. codex payload staging: adapter installs, hashes the STAGED
        # copy, and binds it as installed_payload_sha256
        canon2 = os.path.join(tmp, "canonical2")
        os.makedirs(os.path.join(canon2, "skills", "implementaudit"))
        open(os.path.join(canon2, "skills", "implementaudit", "SKILL.md"),
             "w").write("payload body" + chr(10))
        framework.product_identity = (
            lambda checkout, expected_tag="v0.3.1.0": {
                "product_tag": "v0.3.1.0", "product_commit": "b" * 40,
                "product_tree": "a" * 40})
        try:
            a = make_adapter(tmp, "ok-codex", checkout=canon2,
                             home=os.path.join(tmp, "codex-home-h21"))
            r = run(a, tmp, "r-stage")
            staged = os.path.join(a.codex_home, "skills", "implementaudit")
            ok = r.kind == "ok" and os.path.isfile(
                os.path.join(staged, "SKILL.md"))
            if ok:
                m = json.load(open(os.path.join(r.detail, "manifest.json")))
                ok = (m["installed_payload_sha256"] ==
                      framework.payload_hash(staged) ==
                      m.get("payload_source_sha256"))
            check("H21 codex-payload-staged+hashed", ok)
        finally:
            framework.product_identity = orig_pi

        # 22. ambiguous session identity (two matches) => INVALID
        r = run(make_adapter(tmp, "double-session",
                             home=os.path.join(tmp, "codex-home-h22")),
                tmp, "r-double")
        check("H22 session-ambiguity-INVALID",
              r.kind == "invalid" and "ambiguous" in r.detail)

        # 23. stdout agent message absent from the host session => INVALID
        r = run(make_adapter(tmp, "session-mismatch",
                             home=os.path.join(tmp, "codex-home-h23")),
                tmp, "r-mismatch")
        check("H23 event-mismatch-INVALID",
              r.kind == "invalid" and "event mismatch" in r.detail)

        # 24. credential patterns: shape positives flag, prose negatives
        # pass, and the error never echoes the matched value
        a24 = make_adapter(tmp, "ok-codex")
        neg = os.path.join(tmp, "scan-neg")
        os.makedirs(neg)
        open(os.path.join(neg, "prose.txt"), "w").write(
            "the risk-abcdefghijklmnopqrstuvwxyz01 profile and the "
            "task-ABCDEFGHIJKLMNOPQRSTUVWX12 id are ordinary prose\n")
        try:
            a24.scan_for_leaks(neg)
            check("H24a benign-prose-not-flagged", True)
        except framework.AdapterError:
            check("H24a benign-prose-not-flagged", False)
        shapes = {"ghp": "ghp_ABCDEFGHIJKLMNOPQRSTUV0123",
                  "xoxb": "xoxb-1234567890-ABCDEFGHIJK",
                  "pat": "github_pat_ABCDEFGHIJKLMNOPQRSTUV",
                  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6.eyJzdWIiOiIxMjM0."
                         "SflKxwRJSMeKKF2QT4fwpM"}
        all_ok = True
        for label, tok in shapes.items():
            d = os.path.join(tmp, f"scan-{label}")
            os.makedirs(d)
            open(os.path.join(d, "f.txt"), "w").write(f"x {tok} y\n")
            try:
                a24.scan_for_leaks(d)
                all_ok = False
            except framework.AdapterError as exc:
                if tok in str(exc):
                    all_ok = False
        check("H24b shape-positives-flagged-value-withheld", all_ok)

        # 26. missing resolved effort (codex) => INVALID, fail closed
        r = run(make_adapter(tmp, "no-effort",
                             home=os.path.join(tmp, "codex-home-h26")),
                tmp, "r-noeffort")
        check("H26 missing-effort-fails-closed",
              r.kind == "invalid" and
              "missing resolved reasoning effort" in r.detail)

        # 26b. credential leak in the RUN-ROOT raw host output (outside the
        # bundle) must also quarantine + fail closed, value withheld
        leak2 = ("model: gpt-5.6-luna\nAuthorization: Bearer "
                 "abcdefghij0123456789KLMNOPQR")

        class _RawLeak(hosts.CodexAdapter):
            def collect_raw_stream(self, repo, outcome):
                return None

            def parse_events(self, out):
                return [{"role": "assistant", "content": "clean bundle text"}]

            def resolve_model(self, out):
                self.models_observed = [{"model": "gpt-5.6-luna"}]
                return "gpt-5.6-luna"

            def check_policy(self, repo):
                self.policy_resolved = {}

            def post_checks(self, out):
                pass
        rl = _RawLeak(codex_home=os.path.join(tmp, "codex-home-26b"))
        os.makedirs(rl.codex_home, exist_ok=True)
        mock = os.path.join(tmp, "mock_host.py")
        rl.host_argv_template = [sys.executable, "-c",
                                 "import sys;sys.stdout.write(sys.argv[1])",
                                 leak2]
        rl.timeout_s = 5
        rl.preflight = lambda: None
        r = rl.run_mission("B0", os.path.join(tmp, "custody"), "r-rawleak",
                           os.path.join(tmp, "wrl"), _test_gate=lambda: None)
        rr = os.path.join(tmp, "custody", "r-rawleak")
        # the raw host output carried the leak; it must be quarantined and
        # the ordinary run root must not retain the cleartext file
        leaked_still = os.path.isfile(os.path.join(rr, "host-stdout.raw"))
        check("H26b run-root-raw-credential-quarantine",
              r.kind == "invalid" and "credential" in r.detail
              and "Bearer abcdefghij" not in r.detail
              and not leaked_still)

        # 27. same-second session binding: fractional session timestamps in
        # the SAME second as not_before must match (parsed comparison, never
        # lexicographic — the smoke-L-b0-r1 INVALID class)
        a27 = make_adapter(tmp, "ok-codex",
                           home=os.path.join(tmp, "codex-home-h27"))
        srepo = os.path.join(tmp, "h27-repo")
        os.makedirs(srepo)
        sdir = os.path.join(a27.codex_home, "sessions", "2026")
        os.makedirs(sdir)
        with open(os.path.join(sdir, "r.jsonl"), "w",
                  encoding="utf-8") as fh:
            fh.write(json.dumps({
                "timestamp": "2026-07-17T08:55:03.635Z",
                "type": "session_meta",
                "payload": {"session_id": "s27", "id": "s27",
                            "timestamp": "2026-07-17T08:55:03.635Z",
                            "cwd": srepo, "cli_version": "0.144.5"}}) + "\n")
            fh.write(json.dumps({
                "timestamp": "2026-07-17T08:55:04.000Z",
                "type": "turn_context",
                "payload": {"model": "gpt-5.6-luna", "effort": "max",
                            "approval_policy": "never",
                            "sandbox_policy": {
                                "type": "workspace-write"}}}) + "\n")
        a27._not_before = "2026-07-17T08:55:03Z"
        f27, ctx27 = a27._select_session(srepo)
        check("H27 same-second-session-binding",
              f27 is not None and ctx27.get("model") == "gpt-5.6-luna")

        # 28. E5 live host observation: the adapter RUNS the planted weak
        # rule over fixture-declared cases and records the verdicts
        r = run(make_adapter(tmp, "ok-codex",
                             home=os.path.join(tmp, "codex-home-h28")),
                tmp, "r-e5", fixture_id="E5")
        ok = r.kind == "ok"
        if ok:
            art = os.path.join(r.detail, "artifacts", "result.json")
            v = json.load(open(art, encoding="utf-8"))
            ok = (v == {"current_verdict": "accept",
                        "p1_verdict": "reject",
                        "p2_verdict": "accept"})
            status, verd = runner.score_bundle(r.detail, repo_dir=None)
            ok = ok and status in ("PASS", "FAIL")
        check("H28 e5-live-host-observation", ok)
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
