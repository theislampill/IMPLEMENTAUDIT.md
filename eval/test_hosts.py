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
elif scenario == "stdout-only":
    # NO session file at all: raw stdout is the only "transcript" — a real
    # codex lane must refuse to score it (forgeable echo).
    print("IMPLEMENTAUDIT_PHASE_START p1")
    print("IMPLEMENTAUDIT_RUN_COMPLETE")
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


TEST_POSIX_READ_ATTESTATION = {
    "id": "test-posix-read-profile-v1", "shell_dialect": "posix",
    "executables": {
        "cat": "/bin/cat", "sed": "/bin/sed", "head": "/usr/bin/head",
        "tail": "/usr/bin/tail", "rg": "/usr/bin/rg",
        "grep": "/bin/grep", "command": "builtin:command",
        "exec": "builtin:exec", "env": "/usr/bin/env",
        "sudo": "/usr/bin/sudo", "xargs": "/usr/bin/xargs",
        "true": "builtin:true", "false": "builtin:false",
        "exit": "builtin:exit", "printf": "builtin:printf",
        "echo": "builtin:echo", "find": "/usr/bin/find",
        "ls": "/bin/ls", "stat": "/usr/bin/stat",
        "git": "/usr/bin/git", "touch": "/usr/bin/touch",
        "tee": "/usr/bin/tee", "alias": "builtin:alias",
        "type": "builtin:type"}}

TEST_POWERSHELL_READ_ATTESTATION = {
    "id": "test-powershell-read-profile-v1",
    "shell_dialect": "powershell",
    "executables": {"get-content": "powershell:Get-Content"}}

TEST_CMD_READ_ATTESTATION = {
    "id": "test-cmd-read-profile-v1", "shell_dialect": "cmd",
    "executables": {"type": "cmd:type"}}


def make_adapter(tmp, scenario, kind="codex", counter=None, checkout=None,
                 home=None, host_read_attestation=TEST_POSIX_READ_ATTESTATION):
    mock = os.path.join(tmp, "mock_host.py")
    if not os.path.isfile(mock):
        open(mock, "w", encoding="utf-8").write(MOCK)
    argv = [sys.executable, mock, scenario] + ([counter] if counter else [])
    if kind == "codex":
        a = hosts.CodexAdapter(
            codex_home=home or os.path.join(tmp, "codex-home"),
            product_checkout=checkout, formal=False,
            host_read_attestation=host_read_attestation)
        os.makedirs(a.codex_home, exist_ok=True)
        a.preflight = lambda: None  # version/auth gates unit-tested below
    else:
        a = hosts.ClaudeAdapter(config_dir=os.path.join(tmp, "claude-cfg"),
                                product_checkout=checkout, formal=False,
                                host_read_attestation=host_read_attestation)
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
                json.dump(reconcilelib.process_identity(started),
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
        rl = _RawLeak(codex_home=os.path.join(tmp, "codex-home-26b"),
                      formal=False)
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

        # 30. process identity recorded at spawn: process-started.json must
        # carry every field the reconciler compares (lane/os/boot/pid/
        # creation time) — pid alone can be recycled.
        a30 = make_adapter(tmp, "ok-codex",
                           home=os.path.join(tmp, "codex-home-h30"))
        a30.lane_id = "test-lane-h30"
        r = run(a30, tmp, "r-h30")
        ps = json.load(open(os.path.join(tmp, "custody", "r-h30",
                                         "process-started.json"),
                            encoding="utf-8"))
        check("H30 process-identity-recorded",
              r.kind == "ok" and ps.get("lane_id") == "test-lane-h30"
              and ps.get("host_os") == reconcilelib.host_os_name()
              and ps.get("host_boot_id")
              and isinstance(ps.get("pid"), int)
              and isinstance(ps.get("process_creation_time"), float))

        # 31. recycled-pid refusal: an intent bound to a LIVE pid whose
        # recorded creation time does not match the live process must NOT
        # stay open as 'running' — it terminalizes truthfully.
        rr31 = os.path.join(tmp, "custody", "r-h31")
        os.makedirs(rr31)
        json.dump({"run_id": "r-h31"},
                  open(os.path.join(rr31, "run-intent.json"), "w"))
        json.dump({"run_id": "r-h31", "pid": os.getpid(),
                   "host_os": reconcilelib.host_os_name(),
                   "host_boot_id": reconcilelib.host_boot_id(),
                   "process_creation_time": 12345.0},
                  open(os.path.join(rr31, "process-started.json"), "w"))
        out31 = reconcilelib.reconcile_custody(os.path.join(tmp, "custody"))
        d31 = {o["run_id"]: o["disposition"] for o in out31}
        t31 = json.load(open(os.path.join(rr31, "terminal.json"),
                             encoding="utf-8"))
        check("H31 recycled-pid-not-running",
              d31.get("r-h31") == "terminal-state-unverified"
              and t31.get("reconciled") is True
              and "recycled" in t31.get("detail", ""))

        # 31b. matching identity IS running: same live pid with the TRUE
        # creation time stays open (no terminal write).
        rr31b = os.path.join(tmp, "custody", "r-h31b")
        os.makedirs(rr31b)
        json.dump({"run_id": "r-h31b"},
                  open(os.path.join(rr31b, "run-intent.json"), "w"))
        json.dump({"run_id": "r-h31b", "pid": os.getpid(),
                   "host_os": reconcilelib.host_os_name(),
                   "host_boot_id": reconcilelib.host_boot_id(),
                   "process_creation_time":
                       reconcilelib.process_creation_time(os.getpid())},
                  open(os.path.join(rr31b, "process-started.json"), "w"))
        out31b = reconcilelib.reconcile_custody(os.path.join(tmp, "custody"))
        d31b = {o["run_id"]: o["disposition"] for o in out31b}
        check("H31b matching-identity-running",
              d31b.get("r-h31b") == "running"
              and not os.path.isfile(os.path.join(rr31b, "terminal.json")))
        try:
            os.remove(os.path.join(rr31b, "run-intent.json"))
        except OSError:
            pass

        # 32. foreign-lane pid: a recorded host_os from the OTHER lane can
        # never be adjudicated as alive here (different pid namespace).
        rr32 = os.path.join(tmp, "custody", "r-h32")
        os.makedirs(rr32)
        json.dump({"run_id": "r-h32"},
                  open(os.path.join(rr32, "run-intent.json"), "w"))
        other = "posix" if reconcilelib.host_os_name() == "windows" \
            else "windows"
        json.dump({"run_id": "r-h32", "pid": os.getpid(),
                   "host_os": other, "host_boot_id": "x",
                   "process_creation_time": 1.0},
                  open(os.path.join(rr32, "process-started.json"), "w"))
        out32 = reconcilelib.reconcile_custody(os.path.join(tmp, "custody"))
        d32 = {o["run_id"]: o["disposition"] for o in out32}
        t32 = json.load(open(os.path.join(rr32, "terminal.json"),
                             encoding="utf-8"))
        check("H32 foreign-lane-pid-unverified",
              d32.get("r-h32") == "terminal-state-unverified"
              and "foreign-lane" in t32.get("detail", ""))

        # 33. orphan claim sweep: a crash between staging-dir creation and
        # the atomic rename leaves `<id>.claiming`; the reconciler must
        # terminally classify it, never silently ignore it.
        rr33 = os.path.join(tmp, "custody", "r-h33.claiming")
        os.makedirs(rr33)
        out33 = reconcilelib.reconcile_custody(os.path.join(tmp, "custody"))
        d33 = {o["run_id"]: o["disposition"] for o in out33}
        t33 = json.load(open(os.path.join(rr33, "terminal.json"),
                             encoding="utf-8"))
        check("H33 orphan-claim-swept",
              d33.get("r-h33") == "orphan-claim-swept"
              and t33.get("reconciled") is True
              and t33.get("spawned") is False)

        # 34. formal-run checkout attestation: a formal adapter without a
        # product checkout is INVALID before spawn (no process launched).
        a34 = make_adapter(tmp, "ok-codex",
                           home=os.path.join(tmp, "codex-home-h34"))
        a34.formal = True  # declared formal, but no product_checkout
        r34 = run(a34, tmp, "r-h34")
        check("H34 formal-run-requires-checkout",
              r34.kind == "invalid" and "attested product checkout"
              in str(r34.detail)
              and not os.path.isfile(os.path.join(
                  tmp, "custody", "r-h34", "process-started.json")))

        # 35. tree kill on timeout: the host spawns a GRANDCHILD sleeper
        # and then blocks past the timeout; after timeout handling neither
        # the child nor the grandchild may survive.
        killmock = os.path.join(tmp, "kill_mock.py")
        open(killmock, "w", encoding="utf-8").write(
            "import os, subprocess, sys, time\n"
            "gc = subprocess.Popen([sys.executable, '-c',\n"
            "                       'import time; time.sleep(120)'])\n"
            "open(sys.argv[1], 'w').write(str(gc.pid))\n"
            "time.sleep(120)\n")
        gcpid_file = os.path.join(tmp, "grandchild.pid")
        a35 = make_adapter(tmp, "ok-codex",
                           home=os.path.join(tmp, "codex-home-h35"))
        a35.host_argv_template = [sys.executable, killmock, gcpid_file]
        a35.timeout_s = 3
        r35 = run(a35, tmp, "r-h35")
        gcpid = int(open(gcpid_file).read().strip())
        deadline = 10.0
        import time as _t
        while deadline > 0 and reconcilelib._pid_alive(gcpid):
            _t.sleep(0.2)
            deadline -= 0.2
        gc_dead = not reconcilelib._pid_alive(gcpid)
        check("H35 timeout-kills-process-tree",
              r35.kind == "error" and "timeout" in str(r35.detail)
              and gc_dead)
        if not gc_dead:  # never leak a sleeper on failure
            try:
                subprocess.run(["taskkill", "/PID", str(gcpid), "/F"]
                               if os.name == "nt"
                               else ["kill", "-9", str(gcpid)],
                               capture_output=True, timeout=15)
            except Exception:
                pass

        # 36. custody-record integrity: a mission that rewrites its own
        # run-intent.json (possible under jail-less Config-O — canary
        # finding) must terminalize INVALID, on every exit path.
        real_spawn = hosts._spawn_once

        def _tampering_spawn(argv, env, cwd, timeout_s, **kw):
            out = real_spawn(argv, env, cwd, timeout_s, **kw)
            ip = os.path.join(tmp, "custody", "r-h36", "run-intent.json")
            body = json.load(open(ip, encoding="utf-8"))
            body["model_requested"] = "forged-model"
            json.dump(body, open(ip, "w", encoding="utf-8"))
            return out

        hosts._spawn_once = _tampering_spawn
        try:
            r36 = run(make_adapter(tmp, "ok-codex",
                                   home=os.path.join(tmp, "codex-home-h36")),
                      tmp, "r-h36")
        finally:
            hosts._spawn_once = real_spawn
        t36 = json.load(open(os.path.join(tmp, "custody", "r-h36",
                                          "terminal.json"),
                             encoding="utf-8"))
        check("H36 custody-record-tamper-INVALID",
              r36.kind == "invalid"
              and "custody record run-intent.json modified"
              in str(r36.detail) and t36.get("kind") == "invalid")

        # 37. structured-event authority: a REAL codex lane (temp
        # CODEX_HOME) whose host recorded NO session agent messages must
        # refuse to score raw stdout — echoed text can forge markers.
        r37 = run(make_adapter(tmp, "stdout-only",
                               home=os.path.join(tmp, "codex-home-h37")),
                  tmp, "r-h37")
        check("H37 real-codex-refuses-stdout-transcript",
              r37.kind == "invalid"
              and "refusing to score raw stdout" in str(r37.detail))

        # 38. forged-custody sweep: a mission that PLANTS terminal.json /
        # bundle/ in its own run root (jail-less Config-O) must be
        # quarantined and terminalize INVALID — the adapter's own terminal
        # record must win, never the forged one.
        real_spawn38 = hosts._spawn_once

        def _planting_spawn(argv, env, cwd, timeout_s, **kw):
            out = real_spawn38(argv, env, cwd, timeout_s, **kw)
            rr = os.path.join(tmp, "custody", "r-h38")
            json.dump({"kind": "ok", "reconciled": False, "forged": True},
                      open(os.path.join(rr, "terminal.json"), "w"))
            os.makedirs(os.path.join(rr, "bundle"))
            json.dump({"forged": True},
                      open(os.path.join(rr, "bundle", "manifest.json"), "w"))
            return out

        hosts._spawn_once = _planting_spawn
        try:
            r38 = run(make_adapter(tmp, "ok-codex",
                                   home=os.path.join(tmp, "codex-home-h38")),
                      tmp, "r-h38")
        finally:
            hosts._spawn_once = real_spawn38
        rr38 = os.path.join(tmp, "custody", "r-h38")
        t38 = json.load(open(os.path.join(rr38, "terminal.json"),
                             encoding="utf-8"))
        check("H38 planted-custody-quarantined-INVALID",
              r38.kind == "invalid" and "planted" in str(r38.detail)
              and t38.get("forged") is None
              and t38.get("kind") == "invalid"
              and os.path.isfile(os.path.join(
                  rr38, "quarantine-planted", "terminal.json"))
              and os.path.isdir(os.path.join(
                  rr38, "quarantine-planted", "bundle")))

        # 39. pre-spawn product attestation: a formal run pins the payload
        # hash BEFORE spawn; an unattestable checkout is INVALID with no
        # process launched.
        canon39 = os.path.join(tmp, "canon39")
        os.makedirs(os.path.join(canon39, "skills", "implementaudit"))
        open(os.path.join(canon39, "skills", "implementaudit", "SKILL.md"),
             "w").write("payload body" + chr(10))
        prev_ident39 = framework.product_identity
        framework.product_identity = (
            lambda checkout, expected_tag="v0.3.1.0": {
                "product_tag": "v0.3.1.0", "product_commit": "x",
                "product_tree": "y"})
        try:
            a39 = make_adapter(tmp, "ok-codex", checkout=canon39,
                               home=os.path.join(tmp, "codex-home-h39"))
            a39.formal = True
            r39 = run(a39, tmp, "r-h39")
        finally:
            framework.product_identity = prev_ident39
        att = json.load(open(os.path.join(tmp, "custody", "r-h39",
                                          "product-attestation.json"),
                             encoding="utf-8"))
        check("H39 formal-prespawn-attestation",
              r39.kind == "ok"
              and att.get("payload_sha256")
              == framework.payload_hash(canon39))
        a39b = make_adapter(tmp, "ok-codex",
                            checkout=os.path.join(tmp, "empty39"),
                            home=os.path.join(tmp, "codex-home-h39b"))
        os.makedirs(os.path.join(tmp, "empty39"))
        a39b.formal = True
        r39b = run(a39b, tmp, "r-h39b")
        check("H39b unattestable-checkout-INVALID",
              r39b.kind == "invalid"
              and "unattestable" in str(r39b.detail)
              and not os.path.isfile(os.path.join(
                  tmp, "custody", "r-h39b", "process-started.json")))

        # 40. a process-started.json rewritten with NON-UTF-8 garbage
        # (jail-less Config-O tamper + hard-killed wrapper) must still be
        # terminally classified — never a perpetual reconcile-error that
        # leaves the run without a terminal record on every future pass.
        rr40 = os.path.join(tmp, "custody", "r-h40")
        os.makedirs(rr40)
        json.dump({"run_id": "r-h40"},
                  open(os.path.join(rr40, "run-intent.json"), "w"))
        open(os.path.join(rr40, "process-started.json"), "wb").write(
            b"\x00\xffnot-utf8-garbage")
        out40 = reconcilelib.reconcile_custody(os.path.join(tmp, "custody"))
        d40 = {o["run_id"]: o["disposition"] for o in out40}
        t40p = os.path.join(rr40, "terminal.json")
        t40 = (json.load(open(t40p, encoding="utf-8"))
               if os.path.isfile(t40p) else {})
        check("H40 garbage-process-started-terminalized",
              d40.get("r-h40") == "terminal-state-unverified"
              and t40.get("reconciled") is True
              and t40.get("kind") == "error")

        # 40b. a forged/garbage parent terminal.json must FAIL CLOSED at
        # the scorer's parent-terminal gate: an unreadable terminal can
        # never let a planted bundle reach formal scoring (a mission that
        # writes garbage must not fare better than one that writes nothing).
        rr40b = os.path.join(tmp, "term40b")
        os.makedirs(os.path.join(rr40b, "bundle"))
        open(os.path.join(rr40b, "terminal.json"), "wb").write(
            b"\xff\xfe garbage")
        s40b, v40b = runner.score_bundle(os.path.join(rr40b, "bundle"),
                                         repo_dir=None)
        check("H40b garbage-terminal-fails-closed",
              s40b == "INVALID"
              and "terminal" in (v40b.get("reason") or ""))

        # 40c. a minimal forged dict terminal ({} — no kind) is refused too:
        # only an explicit kind=='ok', reconciled!=True terminal admits a
        # bundle to formal scoring.
        os.remove(os.path.join(rr40b, "terminal.json"))
        json.dump({}, open(os.path.join(rr40b, "terminal.json"), "w"))
        s40c, v40c = runner.score_bundle(os.path.join(rr40b, "bundle"),
                                         repo_dir=None)
        check("H40c kindless-terminal-fails-closed",
              s40c == "INVALID"
              and "terminal" in (v40c.get("reason") or ""))

        # 41. Candidate-product attestation (#35 post-change / comparison
        # phases): product_identity attests a checkout at an explicitly
        # intended non-baseline rev, still refuses a mismatched rev, and
        # the adapter's product_expected_rev is what identity_fields
        # passes down — the gate cross-checks against the campaign
        # intent's identity, never self-attestation.
        cand41 = os.path.join(tmp, "cand41")
        subprocess.run(["git", "init", "-q", cand41], check=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            subprocess.run(["git", "-C", cand41, "config", k, v],
                           check=True)
        open(os.path.join(cand41, "f.txt"), "w").write("candidate\n")
        subprocess.run(["git", "-C", cand41, "add", "."], check=True)
        subprocess.run(["git", "-C", cand41, "commit", "-q", "-m", "c1"],
                       check=True)
        head41 = subprocess.run(["git", "-C", cand41, "rev-parse", "HEAD"],
                                capture_output=True, text=True,
                                check=True).stdout.strip()
        ident41 = framework.product_identity(cand41, expected_tag=head41)
        check("H41 candidate-rev-attests",
              ident41.get("product_commit") == head41
              and ident41.get("product_tag") == head41)
        open(os.path.join(cand41, "f.txt"), "a").write("drift\n")
        subprocess.run(["git", "-C", cand41, "add", "."], check=True)
        subprocess.run(["git", "-C", cand41, "commit", "-q", "-m", "c2"],
                       check=True)
        try:
            framework.product_identity(cand41, expected_tag=head41)
            check("H41b mismatched-rev-refused", False)
        except framework.AdapterError as exc:
            check("H41b mismatched-rev-refused",
                  "refuse to attest" in str(exc))
        seen41 = {}
        prev_ident41 = framework.product_identity
        framework.product_identity = (
            lambda checkout, expected_tag="v0.3.1.0":
                (seen41.update(tag=expected_tag) or {
                    "product_tag": expected_tag, "product_commit": "x",
                    "product_tree": "y"}))
        try:
            a41 = make_adapter(tmp, "ok-codex", checkout=cand41,
                               home=os.path.join(tmp, "codex-home-h41"))
            a41.product_expected_rev = "deadbeef-intended-rev"
            a41.identity_fields("r-h41", "B0", "m", "t0", "t1")
        finally:
            framework.product_identity = prev_ident41
        check("H41c adapter-passes-expected-rev",
              seen41.get("tag") == "deadbeef-intended-rev")

        # 42. Subagent session lineage (candidate-product fanout, #49): a
        # child thread's session file in the SAME isolated home with an
        # explicit parent_thread_id chained to the bound root is the same
        # mission identity — bound to the ROOT, child ids recorded. True
        # ambiguity (two roots) and foreign parents still refuse.
        def _sess(adapter, name, sid, parent=None, repo=None):
            sdir = os.path.join(adapter.codex_home, "sessions", "2026")
            os.makedirs(sdir, exist_ok=True)
            pl = {"session_id": parent or sid, "id": sid,
                  "timestamp": "2026-07-18T08:00:01.000Z",
                  "cwd": repo, "cli_version": "0.144.5"}
            if parent:
                pl["parent_thread_id"] = parent
                pl["thread_source"] = "subagent"
            with open(os.path.join(sdir, name), "w",
                      encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "timestamp": pl["timestamp"],
                    "type": "session_meta", "payload": pl}) + "\n")
                fh.write(json.dumps({
                    "timestamp": pl["timestamp"], "type": "turn_context",
                    "payload": {"model": "gpt-5.6-luna", "effort": "max",
                                "approval_policy": "never",
                                "sandbox_policy": {
                                    "type": "workspace-write"}}}) + "\n")
        repo42 = os.path.join(tmp, "h42-repo")
        os.makedirs(repo42)
        a42 = make_adapter(tmp, "ok-codex", checkout=None,
                           home=os.path.join(tmp, "codex-home-h42"))
        a42._not_before = "2026-07-18T08:00:00Z"
        _sess(a42, "root.jsonl", "root-42", repo=repo42)
        _sess(a42, "child.jsonl", "child-42", parent="root-42",
              repo=repo42)
        f42, ctx42 = a42._select_session(repo42)
        check("H42 subagent-child-binds-to-root",
              f42 is not None and f42.endswith("root.jsonl")
              and ctx42.get("subagent_sessions") == ["child-42"])
        a42b = make_adapter(tmp, "ok-codex", checkout=None,
                            home=os.path.join(tmp, "codex-home-h42b"))
        a42b._not_before = "2026-07-18T08:00:00Z"
        _sess(a42b, "r1.jsonl", "r1-42", repo=repo42)
        _sess(a42b, "r2.jsonl", "r2-42", repo=repo42)
        try:
            a42b._select_session(repo42)
            check("H42b two-roots-still-refused", False)
        except framework.AdapterError as exc:
            check("H42b two-roots-still-refused",
                  "ambiguous" in str(exc))
        a42c = make_adapter(tmp, "ok-codex", checkout=None,
                            home=os.path.join(tmp, "codex-home-h42c"))
        a42c._not_before = "2026-07-18T08:00:00Z"
        _sess(a42c, "root.jsonl", "root-42c", repo=repo42)
        _sess(a42c, "orphan.jsonl", "orphan-42c",
              parent="not-a-matched-id", repo=repo42)
        try:
            a42c._select_session(repo42)
            check("H42c foreign-parent-refused", False)
        except framework.AdapterError as exc:
            check("H42c foreign-parent-refused",
                  "foreign-parent" in str(exc) or "ambiguous" in str(exc))

        # 43. Generic JSON-field host observation for B3-v2 continuity
        # capsules: exact expected fields pass, drifted values fail. The
        # model-authored file is measured by the host; its own claim does not
        # decide the property.
        repo43 = os.path.join(tmp, "h43-repo")
        os.makedirs(repo43)
        state43 = os.path.join(
            repo43, ".IMPLEMENTAUDIT", "runs", "run-1", "STATE.md")
        roadmap43 = os.path.join(
            repo43, ".IMPLEMENTAUDIT", "runs", "run-1", "ROADMAP.md")
        os.makedirs(os.path.dirname(state43), exist_ok=True)
        open(state43, "w", encoding="utf-8").write("epoch\n")
        open(roadmap43, "w", encoding="utf-8").write("ANDON\n")
        capsule43 = os.path.join(repo43, "continuity-capsule.json")
        json.dump({"active_item": "ANDON 251", "stale_item": "satisfied"},
                  open(capsule43, "w", encoding="utf-8"))
        fx43 = {"host_checks": {"specs": [{
            "key": "capsule_bound", "kind": "json_fields_equal",
            "path": "continuity-capsule.json",
            "equals": {"active_item": "ANDON 251",
                       "stale_item": "satisfied"}}]}}
        a43 = make_adapter(tmp, "ok-codex",
                           home=os.path.join(tmp, "codex-home-h43"))
        powershell43 = make_adapter(
            tmp, "ok-codex", home=os.path.join(tmp, "codex-home-h43-ps"),
            host_read_attestation=TEST_POWERSHELL_READ_ATTESTATION)
        cmd43 = make_adapter(
            tmp, "ok-codex", home=os.path.join(tmp, "codex-home-h43-cmd"),
            host_read_attestation=TEST_CMD_READ_ATTESTATION)
        try:
            good43 = a43._run_host_checks(fx43, repo43)
            json.dump({"active_item": "ANDON 150",
                       "stale_item": "active"},
                      open(capsule43, "w", encoding="utf-8"))
            bad43 = a43._run_host_checks(fx43, repo43)
            check("H43 json-fields-host-check",
                  good43.get("capsule_bound") is True
                  and bad43.get("capsule_bound") is False)
        except framework.AdapterError:
            check("H43 json-fields-host-check", False)
        fx43_escape = {"host_checks": {"specs": [{
            "key": "escape", "kind": "json_fields_equal",
            "path": "../outside.json", "equals": {"x": 1}}]}}
        try:
            a43._run_host_checks(fx43_escape, repo43)
            check("H43b json-fields-path-escape-refused", False)
        except framework.AdapterError as exc:
            check("H43b json-fields-path-escape-refused",
                  "unsafe" in str(exc))

        # 44. Host-owned tool sequence proves both durable-state reads
        # precede the sole authorized capsule write. Phrase order in the
        # final answer is not a substitute for the tool trace.
        fx44 = {"host_checks": {"specs": [{
            "key": "read_before_write", "kind": "path_access_order",
            "reads": [
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md",
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"],
            "write": ".IMPLEMENTAUDIT/runs/run-1/capsule.json"}]}}
        a43._tool_trace = [
            {"ordinal": 1, "action": "read",
             "path": ".IMPLEMENTAUDIT/runs/run-1/STATE.md",
             "source": "unit"},
            {"ordinal": 2, "action": "read",
             "path": ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
             "source": "unit"},
            {"ordinal": 3, "action": "write",
             "path": ".IMPLEMENTAUDIT/runs/run-1/capsule.json",
             "source": "unit"},
        ]
        try:
            good44 = a43._run_host_checks(fx44, repo43)
            a43._tool_trace[0]["ordinal"] = 4
            bad44 = a43._run_host_checks(fx44, repo43)
            check("H44 durable-reads-before-write",
                  good44.get("read_before_write") is True
                  and bad44.get("read_before_write") is False)
        except framework.AdapterError:
            check("H44 durable-reads-before-write", False)
        codex44 = "\n".join((
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "exit_code": 0,
                "command": "sed -n 1,200p .IMPLEMENTAUDIT/runs/run-1/"
                           "STATE.md && sed -n 1,200p "
                           ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"}}),
            json.dumps({"type": "item.completed", "item": {
                "type": "file_change", "changes": [{
                    "path": ".IMPLEMENTAUDIT/runs/run-1/capsule.json",
                    "kind": "add"}]}})))
        claude44 = "\n".join((
            json.dumps({"type": "assistant", "message": {"content": [{
                "type": "tool_use", "id": "read-state", "name": "Read", "input": {
                    "file_path": ".IMPLEMENTAUDIT/runs/run-1/STATE.md"}}]}}),
            json.dumps({"type": "user", "message": {"content": [{
                "type": "tool_result", "tool_use_id": "read-state",
                "content": "ok", "is_error": False}]}}),
            json.dumps({"type": "assistant", "message": {"content": [{
                "type": "tool_use", "id": "read-roadmap", "name": "Read", "input": {
                    "file_path": ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"}}]}}),
            json.dumps({"type": "user", "message": {"content": [{
                "type": "tool_result", "tool_use_id": "read-roadmap",
                "content": "ok", "is_error": False}]}}),
            json.dumps({"type": "assistant", "message": {"content": [{
                "type": "tool_use", "id": "write-capsule", "name": "Write", "input": {
                    "file_path": ".IMPLEMENTAUDIT/runs/run-1/capsule.json",
                    "content": "{}"}}]}}),
            json.dumps({"type": "user", "message": {"content": [{
                "type": "tool_result", "tool_use_id": "write-capsule",
                "content": "ok", "is_error": False}]}})))
        try:
            a43._tool_trace = a43._extract_tool_trace(codex44)
            c44 = a43._run_host_checks(fx44, repo43)
            o43 = make_adapter(
                tmp, "ok-claude", kind="claude",
                home=os.path.join(tmp, "claude-home-h44"))
            o43._tool_trace = o43._extract_tool_trace(claude44)
            o44 = o43._run_host_checks(fx44, repo43)
            check("H44c cross-host-tool-trace",
                  c44.get("read_before_write") is True
                  and o44.get("read_before_write") is True)
        except (AttributeError, framework.AdapterError):
            check("H44c cross-host-tool-trace", False)

        # 44d. A content search over the run root counts only when its
        # successful host output identifies both files. Listing-only and
        # mixed mutating commands cannot manufacture the read result.
        rg44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "rg -n 'ANDON|epoch' .IMPLEMENTAUDIT/runs/run-1",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md:1:epoch\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md:1:ANDON\n"}})
        list44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "rg --files .IMPLEMENTAUDIT/runs/run-1",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        find44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "find .IMPLEMENTAUDIT/runs/run-1 -type f -print",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        mixed_list44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "rg --files .IMPLEMENTAUDIT/runs/run-1 && find "
                       ".IMPLEMENTAUDIT/runs/run-1 -type f -print",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        spoof44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "rg -n 'STATE.md|ROADMAP.md' notes.txt",
            "aggregated_output":
                "notes.txt:1:.IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                "notes.txt:2:.IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        type44 = "\n".join((
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "exit_code": 0,
                "command": "type .IMPLEMENTAUDIT/runs/run-1/STATE.md",
                "aggregated_output": "state contents\n"}}),
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "exit_code": 0,
                "command": "type .IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
                "aggregated_output": "roadmap contents\n"}})))
        find_grep44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "find .IMPLEMENTAUDIT/runs/run-1 -type f -print | "
                       "grep -E 'STATE|ROADMAP'",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        synthetic_grep44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "printf '%s\\n' .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                       ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md | "
                       "grep -E 'STATE|ROADMAP'",
            "aggregated_output":
                ".IMPLEMENTAUDIT/runs/run-1/STATE.md\n"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md\n"}})
        cat_grep44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                       ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md | grep ANDON",
            "aggregated_output": "ANDON 251\n"}})
        overwrite44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                       ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"
                       ">.IMPLEMENTAUDIT/runs/run-1/capsule.json",
            "aggregated_output": ""}})
        append44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                       ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"
                       ">>.IMPLEMENTAUDIT/runs/run-1/capsule.json",
            "aggregated_output": ""}})
        stderr_redirect44 = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "exit_code": 0,
            "command": "cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                       ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md 2>errors.log",
            "aggregated_output": "state contents\nroadmap contents\n"}})
        quoted_arg_redirect44 = json.dumps({
            "type": "item.completed", "item": {
                "type": "command_execution", "exit_code": 0,
                "command": "cat \"label's value\" "
                           ".IMPLEMENTAUDIT/runs/run-1/STATE.md "
                           ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"
                           ">.IMPLEMENTAUDIT/runs/run-1/capsule.json",
                "aggregated_output": ""}})
        wrapped_readers44 = [
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "exit_code": 0,
                "command": command,
                "aggregated_output": "state contents\nroadmap contents\n"}})
            for command in (
                "printf '%s\\0' .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md | xargs -0 cat",
                "env CONTINUITY=1 cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
                "sudo cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
                "exec cat .IMPLEMENTAUDIT/runs/run-1/STATE.md "
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
                "Get-Content .IMPLEMENTAUDIT/runs/run-1/STATE.md,"
                ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md",
            )]
        try:
            write_event = codex44.splitlines()[-1]
            a43._tool_trace = a43._extract_tool_trace(
                rg44 + "\n" + write_event)
            good44d = a43._run_host_checks(fx44, repo43)
            a43._tool_trace = a43._extract_tool_trace(
                list44 + "\n" + write_event)
            bad44d = a43._run_host_checks(fx44, repo43)
            a43._tool_trace = a43._extract_tool_trace(
                spoof44 + "\n" + write_event)
            spoofed44d = a43._run_host_checks(fx44, repo43)
            a43._tool_trace = a43._extract_tool_trace(
                find44 + "\n" + write_event)
            find_only44d = a43._run_host_checks(fx44, repo43)
            a43._tool_trace = a43._extract_tool_trace(
                mixed_list44 + "\n" + write_event)
            mixed_list_only44d = a43._run_host_checks(fx44, repo43)
            cmd43._tool_trace = cmd43._extract_tool_trace(
                type44 + "\n" + write_event)
            type_read44d = cmd43._run_host_checks(fx44, repo43)
            check("H44d content-read-not-file-listing",
                  good44d.get("read_before_write") is True
                  and bad44d.get("read_before_write") is False
                  and spoofed44d.get("read_before_write") is False
                  and find_only44d.get("read_before_write") is False
                  and mixed_list_only44d.get("read_before_write") is False
                  and type_read44d.get("read_before_write") is True)

            # A successful filename-listing event remains non-evidence in a
            # complete trace. The property turns true only after both files
            # are subsequently read by a genuine content-reader command.
            a43._tool_trace = a43._extract_tool_trace(
                mixed_list44 + "\n" + write_event)
            listing_before_write44e = a43._run_host_checks(fx44, repo43)
            cmd43._tool_trace = cmd43._extract_tool_trace(
                mixed_list44 + "\n" + type44 + "\n" + write_event)
            content_read_before_write44e = cmd43._run_host_checks(
                fx44, repo43)
            check("H44e listing-stays-false-until-content-read",
                  listing_before_write44e.get("read_before_write") is False
                  and content_read_before_write44e.get(
                      "read_before_write") is True)

            # A search command consuming pipeline input proves only that it
            # searched the producer's output. Listing/synthetic producers do
            # not become file-content reads; an actual cat producer does.
            pipeline_results44f = []
            for event in (find_grep44, synthetic_grep44, cat_grep44):
                a43._tool_trace = a43._extract_tool_trace(
                    event + "\n" + write_event)
                pipeline_results44f.append(
                    a43._run_host_checks(fx44, repo43).get(
                        "read_before_write"))
            check("H44f pipeline-source-controls-content-read",
                  pipeline_results44f == [False, False, False])

            # Output redirection opens a write before the content command
            # executes, so the same command event cannot establish read-before-
            # write ordering. A later clean reader event may establish it.
            redirect_results44g = []
            for event in (overwrite44, append44, stderr_redirect44,
                          quoted_arg_redirect44):
                a43._tool_trace = a43._extract_tool_trace(
                    event + "\n" + write_event)
                redirect_results44g.append(
                    a43._run_host_checks(fx44, repo43).get(
                        "read_before_write"))
            a43._tool_trace = a43._extract_tool_trace(
                overwrite44 + "\n" + type44 + "\n" + write_event)
            redirect_then_clean44g = a43._run_host_checks(fx44, repo43)
            check("H44g output-redirection-disqualifies-read-event",
                  redirect_results44g == [False, False, True, False]
                  and redirect_then_clean44g.get(
                      "read_before_write") is False)

            # Common execution wrappers preserve the actual command position.
            # They must recognize cat/Get-Content without treating find's
            # unrelated `-type` option as a reader command.
            wrapped_results44h = []
            for event in wrapped_readers44:
                adapter44h = (powershell43 if "Get-Content" in event
                              else a43)
                adapter44h._tool_trace = adapter44h._extract_tool_trace(
                    event + "\n" + write_event)
                wrapped_results44h.append(
                    adapter44h._run_host_checks(fx44, repo43).get(
                        "read_before_write"))
            check("H44h wrapped-reader-command-position",
                  wrapped_results44h == [False, True, True, True, True]
                  and find_only44d.get("read_before_write") is False)
        except (AttributeError, framework.AdapterError):
            check("H44d content-read-not-file-listing", False)
            check("H44e listing-stays-false-until-content-read", False)
            check("H44f pipeline-source-controls-content-read", False)
            check("H44g output-redirection-disqualifies-read-event", False)
            check("H44h wrapped-reader-command-position", False)

        # 45. Reviewed adversarial contract for the cross-host content-read
        # boundary. These table-driven cases are deliberately expressed in
        # terms of the production tri-state API: ambiguity is distinct from a
        # proved non-read, and neither state may manufacture positive evidence.
        # See docs/audits/archive/
        # v0.3.2.0-host-read-parser-adversarial-corpus.md.
        S45 = ".IMPLEMENTAUDIT/runs/run-1/STATE.md"
        R45 = ".IMPLEMENTAUDIT/runs/run-1/ROADMAP.md"
        W45 = ".IMPLEMENTAUDIT/runs/run-1/capsule.json"

        def command_state(command, target, output="", exit_code=0):
            adapter = (powershell43 if command.lower().lstrip().startswith(
                       "get-content") else a43)
            record = {
                "action": "command", "command": command,
                "output": output, "exit_code": exit_code,
                "invoked_ordinal": 1, "completed_ordinal": 2,
                "source": "codex-command-completed"}
            record = adapter._bind_command_profile(record)
            return adapter._classify_command_target(
                record, target, repo43)

        shell_cases45 = [
            # stage/path/executable binding
            ("A01-S", "cat /dev/null && printf '%s\\n' " + S45 + " " + R45,
             S45, "not-content-read"),
            ("A02-S", "echo " + S45 + "; cat " + R45,
             S45, "not-content-read"),
            ("A02-R", "echo " + S45 + "; cat " + R45,
             R45, "content-read"),
            ("A03-S", "cat " + S45 + "; echo " + R45,
             S45, "fail-closed"),
            ("A04", "cat /dev/null # " + S45 + " " + R45,
             S45, "not-content-read"),
            ("A05-pattern", "grep -F -e '" + S45 + "' -e '" + R45 +
             "' notes.txt", S45, "not-content-read"),
            ("A07", "cat " + S45 + ".backup " + R45 + ".backup",
             S45, "not-content-read"),
            ("A10", "./tools/cat " + S45 + " " + R45,
             S45, "fail-closed"),
            # pipeline provenance and status entailment
            ("B01", "printf '%s\\n' " + S45 + " " + R45 +
             " | cat | rg 'STATE|ROADMAP'", S45, "not-content-read"),
            ("B03", "cat " + S45 + " | grep ROADMAP",
             S45, "fail-closed"),
            ("B04", "printf junk | rg -n 'epoch|ANDON' " + S45 +
             " " + R45, S45, "content-read"),
            ("B06", "printf paths | grep x || cat " + S45 + " " + R45,
             S45, "fail-closed"),
            ("B07-S", "true || cat " + S45 + "; cat " + R45,
             S45, "not-content-read"),
            ("B07-R", "true || cat " + S45 + "; cat " + R45,
             R45, "content-read"),
            ("B10", "printf '%s\\0' " + S45 + " " + R45 +
             " | xargs -0 -n 1 cat", S45, "fail-closed"),
            # descriptor-aware redirection
            ("C01-S", "cat 3<" + S45 + " 4<" + R45 + " </dev/null",
             S45, "not-content-read"),
            ("C02-S", "cat 0<" + S45 + " 3<" + R45,
             S45, "content-read"),
            ("C02-R", "cat 0<" + S45 + " 3<" + R45,
             R45, "not-content-read"),
            ("C07", "cat " + S45 + " " + R45 + " 2>&1",
             S45, "content-read"),
            ("C10", "cat " + S45 + " " + R45 + ">output.tmp",
             S45, "content-read"),
            ("C15-S", "cat " + S45 + ">" + R45,
             S45, "content-read"),
            ("C15-R", "cat " + S45 + ">" + R45,
             R45, "not-content-read"),
            # reader/wrapper argument grammar
            ("D01", "cat --help " + S45 + " " + R45,
             S45, "not-content-read"),
            ("D07", "command -p cat " + S45 + " " + R45,
             S45, "content-read"),
            ("D08", "exec -a audit cat " + S45 + " " + R45,
             S45, "content-read"),
            ("D09", "env -u NAME cat " + S45 + " " + R45,
             S45, "content-read"),
            ("D10", "sudo -u root cat " + S45 + " " + R45,
             S45, "content-read"),
            ("D14", "rg -- '--files' " + S45 + " " + R45,
             S45, "content-read"),
            ("reader-grep-e", "grep -e '" + S45 + "' notes.txt",
             S45, "not-content-read"),
            ("reader-grep-f", "grep -f " + S45 + " " + R45,
             S45, "content-read"),
            ("reader-sed-e", "sed -e '/STATE/p' notes.txt",
             S45, "not-content-read"),
            ("reader-sed-f", "sed -f " + S45 + " " + R45,
             S45, "content-read"),
            ("reader-head-zero", "head -n 0 " + S45,
             S45, "not-content-read"),
            ("reader-rg-files", "rg --files " + S45,
             S45, "not-content-read"),
            # lexical data and deliberately unsupported syntax
            ("E01", "rg -n 'apply_patch|git commit' " + S45 + " " + R45,
             S45, "content-read"),
            ("E03", "exit 0; cat " + S45 + "; cat " + R45,
             S45, "not-content-read"),
            ("E04-S", "cat " + S45 + " || true; cat " + R45,
             S45, "fail-closed"),
            ("E04-R", "cat " + S45 + " || true; cat " + R45,
             R45, "content-read"),
            ("nested-shell", "bash -c 'cat " + S45 + "'",
             S45, "fail-closed"),
            ("expansion", "cat ${ROOT}/" + S45,
             S45, "fail-closed"),
            ("substitution", "cat $(printf " + S45 + ")",
             S45, "fail-closed"),
            ("path-assignment", "PATH=./tools cat " + S45,
             S45, "fail-closed"),
            ("env-path-assignment", "env PATH=./tools cat " + S45,
             S45, "fail-closed"),
            ("alias-definition", "alias cat='printf'; cat " + S45,
             S45, "fail-closed"),
        ]
        shell_results45 = []
        for case_id, command, target, expected in shell_cases45:
            try:
                observed = command_state(command, target)
            except (AttributeError, framework.AdapterError, ValueError):
                observed = "api-error"
            shell_results45.append((case_id, observed, expected))
        check("H45a tri-state-shell-corpus",
              all(observed == expected
                  for _case, observed, expected in shell_results45))
        for case_id, observed, expected in shell_results45:
            check("H45a/" + case_id, observed == expected)

        malformed45 = [
            "cat " + S45 + " |", "| cat " + S45,
            "cat " + S45 + " &&", "&& cat " + S45,
            "cat " + S45 + " <", "cat " + S45 + " <<<",
            "cat $(printf " + S45, "cat `printf " + S45,
            "cat " + S45 + " )", "cat " + S45 + " && (",
            "cat " + S45 + "\n|", "cat " + S45 + "\x00"]
        malformed_results45 = []
        for command in malformed45:
            try:
                malformed_results45.append(command_state(command, S45))
            except (AttributeError, framework.AdapterError, ValueError):
                malformed_results45.append("api-error")
        check("H45b malformed-shell-fails-closed",
              malformed_results45 == ["fail-closed"] * len(malformed45))

        # Absolute identities are accepted only under the bound repository
        # root. Case-distinct and suffix-decoy identities do not alias it.
        absolute_s45 = state43.replace("\\", "/")
        external_s45 = "/tmp/decoy/" + S45
        identity_cases45 = [
            ("absolute", "cat '" + absolute_s45 + "'", "content-read"),
            ("external-suffix", "cat " + external_s45,
             "not-content-read"),
            ("case-distinct", "cat " + S45.replace("STATE", "state"),
             "not-content-read"),
        ]
        identity_results45 = []
        for case_id, command, expected in identity_cases45:
            try:
                observed = command_state(command, S45)
            except (AttributeError, framework.AdapterError, ValueError):
                observed = "api-error"
            identity_results45.append((case_id, observed, expected))
        check("H45c root-bound-file-identity",
              all(observed == expected
                  for _case, observed, expected in identity_results45))

        def codex_event(item, event_type="item.completed", **outer):
            return json.dumps(dict(
                {"type": event_type, "item": item}, **outer))

        codex_reader45 = codex_event({
            "id": "cmd-r", "type": "command_execution", "exit_code": 0,
            "command": "cat " + S45 + " " + R45,
            "aggregated_output": "epoch\nANDON\n"})
        codex_write45 = codex_event({
            "id": "write-w", "type": "file_change", "changes": [{
                "path": W45, "kind": "add"}]})
        codex_cases45 = [
            ("strict-green", codex_reader45 + "\n" + codex_write45, True),
            ("bool-exit", codex_event({
                "type": "command_execution", "exit_code": False,
                "command": "cat " + S45 + " " + R45}) + "\n" +
             codex_write45, False),
            ("failed-status", codex_event({
                "type": "command_execution", "status": "failed",
                "exit_code": 0, "command": "cat " + S45 + " " + R45}) +
             "\n" + codex_write45, False),
            ("scalar-contaminates", "null\n" + codex_reader45 + "\n" +
             codex_write45, False),
            ("duplicate-key", '{"type":"item.completed","item":{' +
             '"type":"command_execution","exit_code":0,' +
             '"command":"cat /dev/null","command":"cat ' + S45 +
             ' ' + R45 + '"}}\n' + codex_write45, False),
        ]
        codex_results45 = []
        for case_id, stream, expected in codex_cases45:
            try:
                a43._tool_trace = a43._extract_tool_trace(stream)
                observed = a43._run_host_checks(
                    fx44, repo43).get("read_before_write")
            except (AttributeError, framework.AdapterError, ValueError):
                observed = False
            codex_results45.append((case_id, observed, expected))
        check("H45d strict-codex-normalization",
              all(observed == expected
                  for _case, observed, expected in codex_results45))

        # A host-owned wrapper is the only recursively unwrapped interpreter.
        codex_wrapped45 = codex_event({
            "type": "command_execution", "exit_code": 0,
            "command": "/bin/bash -lc \"cat " + S45 + " " + R45 + "\"",
            "aggregated_output": "epoch\nANDON\n"})
        try:
            a43._tool_trace = a43._extract_tool_trace(
                codex_wrapped45 + "\n" + codex_write45)
            untrusted_wrapped_result45 = a43._run_host_checks(
                fx44, repo43).get("read_before_write")
            a43._tool_trace = [
                a43._bind_command_profile(record, host_owned_wrapper=True)
                if record.get("action") == "command" else record
                for record in a43._tool_trace]
            wrapped_result45 = a43._run_host_checks(
                fx44, repo43).get("read_before_write")
        except (AttributeError, framework.AdapterError, ValueError):
            untrusted_wrapped_result45 = True
            wrapped_result45 = False
        check("H45e host-owned-wrapper-green",
              untrusted_wrapped_result45 is False
              and wrapped_result45 is True)
        profile45 = a43._host_read_profile(repo43)
        check("H45e2 frozen-host-read-profile",
              profile45.get("schema") ==
              "implementaudit-host-read-profile-v1"
              and profile45.get("host") == "codex"
              and profile45.get("repo_root") == os.path.abspath(repo43)
              and profile45.get("shell_dialect") == "posix"
              and profile45.get("attestation_id") ==
              "test-posix-read-profile-v1")

        # Claude actions are intervals. Read completion must precede write
        # invocation, tool IDs are unique, result status is strict, and a
        # Claude stream cannot borrow Codex envelopes.
        claude45_adapter = make_adapter(
            tmp, "ok-claude", kind="claude",
            home=os.path.join(tmp, "claude-home-h45"))

        def cuse(tool_id, name, inputs):
            return json.dumps({"type": "assistant", "message": {"content":
                [{"type": "tool_use", "id": tool_id, "name": name,
                  "input": inputs}]}})

        def cresult(tool_id, content="ok", **fields):
            block = {"type": "tool_result", "tool_use_id": tool_id,
                     "content": content}
            block.update(fields)
            return json.dumps({"type": "user", "message": {"content":
                [block]}})

        claude_green45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            cresult("s", is_error=False),
            cuse("r", "Read", {"file_path": R45}),
            cresult("r", is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_inverted45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False), cresult("s", is_error=False),
            cuse("r", "Read", {"file_path": R45}),
            cresult("r", is_error=False)))
        claude_duplicate45 = "\n".join((
            cuse("dup", "Read", {"file_path": S45}),
            cuse("dup", "Read", {"file_path": R45}),
            cresult("dup", is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_bad_status45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            cresult("s", is_error=False, status="failed"),
            cuse("r", "Read", {"file_path": R45}),
            cresult("r", is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_mixed45 = codex_reader45 + "\n" + claude_green45
        claude_cases45 = [
            ("green", claude_green45, True),
            ("completion-inversion", claude_inverted45, False),
            ("duplicate-id", claude_duplicate45, False),
            ("failed-status", claude_bad_status45, False),
            ("mixed-host", claude_mixed45, False),
        ]
        claude_results45 = []
        for case_id, stream, expected in claude_cases45:
            try:
                claude45_adapter._tool_trace = \
                    claude45_adapter._extract_tool_trace(stream)
                observed = claude45_adapter._run_host_checks(
                    fx44, repo43).get("read_before_write")
            except (AttributeError, framework.AdapterError, ValueError):
                observed = False
            claude_results45.append((case_id, observed, expected))
        check("H45f strict-claude-intervals",
              all(observed == expected
                  for _case, observed, expected in claude_results45))

        # The remaining rows complete the mandatory mechanism inventory with
        # paired reader grammars, descriptor controls, path edge cases, strict
        # raw-event types, and realistic start/completion envelopes.
        spaced_rel45 = ".IMPLEMENTAUDIT/runs/run-1/space dir/Ünicode.md"
        spaced_abs45 = os.path.join(repo43, *spaced_rel45.split("/"))
        os.makedirs(os.path.dirname(spaced_abs45), exist_ok=True)
        open(spaced_abs45, "w", encoding="utf-8").write("evidence\n")
        command_word_rel45 = ".IMPLEMENTAUDIT/runs/run-1/git commit/EVIDENCE.md"
        command_word_abs45 = os.path.join(
            repo43, *command_word_rel45.split("/"))
        os.makedirs(os.path.dirname(command_word_abs45), exist_ok=True)
        open(command_word_abs45, "w", encoding="utf-8").write("safe\n")
        extra_shell_cases45 = [
            ("A06-delimiter", "Get-Content notes.txt -Delimiter '" + S45 +
             "|" + R45 + "'", S45, "not-content-read", 0),
            ("A08-prefix", "cat x" + S45, S45, "not-content-read", 0),
            ("A09-output-spoof", "cat notes.txt", S45,
             "not-content-read", 0),
            ("A11-local-type", "./tools/type.exe " + S45,
             S45, "fail-closed", 0),
            ("A12-local-grep", "./tools/grep pattern " + S45,
             S45, "fail-closed", 0),
            ("B02-synthetic-pipeline", "printf '%s\\n' " + S45 + " " +
             R45 + " | sed -n p | grep -E 'STATE|ROADMAP'",
             S45, "not-content-read", 0),
            ("B05-final-grep-files", "printf junk | grep -nE " +
             "'epoch|ANDON' " + S45 + " " + R45,
             S45, "content-read", 0),
            ("B09-pipe-producer", "cat " + S45 + " " + R45 +
             " |& grep x", S45, "fail-closed", 0),
            ("B11-xargs-rg", "printf '%s\\0' " + S45 + " " + R45 +
             " | xargs -0 rg -n 'epoch|ANDON'", S45, "fail-closed", 0),
            ("B12-output-spoof", "rg --no-filename '^' notes.txt",
             S45, "not-content-read", 0),
            ("C02-fd0", "cat 0<" + S45 + " 3<" + R45,
             S45, "content-read", 0),
            ("C03-heredoc", "cat <<EOF\n" + S45 + "\n" + R45 +
             "\nEOF", S45, "not-content-read", 0),
            ("C04-here-string", "cat <<< '" + S45 + " " + R45 + "'",
             S45, "not-content-read", 0),
            ("C05-process-substitution", "cat < <(printf '%s\\n' " +
             S45 + " " + R45 + ")", S45, "not-content-read", 0),
            ("C06-leading-S", "<" + S45 + " cat; <" + R45 + " cat",
             S45, "fail-closed", 0),
            ("C06-leading-R", "<" + S45 + " cat; <" + R45 + " cat",
             R45, "content-read", 0),
            ("C08-close-fd", "cat " + S45 + " " + R45 + " 2>&-",
             S45, "content-read", 0),
            ("C09-dup-fd", "cat " + S45 + " " + R45 + " 1>&2",
             S45, "content-read", 0),
            ("C11-append-other", "cat " + S45 + " " + R45 +
             ">>output.tmp", S45, "content-read", 0),
            ("C13-nested-write", "cat $(sh -c 'printf x >" + W45 +
             "; printf %s " + S45 + "')", S45, "fail-closed", 0),
            ("C16-layered", "cat " + S45 + " " + R45 +
             " && touch unrelated.tmp", S45, "content-read", 0),
            ("D02-version", "cat --version " + S45,
             S45, "not-content-read", 0),
            ("D03-rg-help", "rg --help " + S45,
             S45, "not-content-read", 0),
            ("D04-env-help", "env --help cat " + S45,
             S45, "not-content-read", 0),
            ("D05-xargs-help", "xargs --help cat " + S45,
             S45, "not-content-read", 0),
            ("D06-sudo-help", "sudo --help cat " + S45,
             S45, "not-content-read", 0),
            ("D11-xargs-n", "printf paths | xargs -n 2 cat " + S45,
             S45, "fail-closed", 0),
            ("D12-xargs-I", "printf paths | xargs -I {} cat " + S45,
             S45, "fail-closed", 0),
            ("D13-empty-xargs", "printf '' | xargs -E cat printf " +
             S45 + " " + R45, S45, "not-content-read", 0),
            ("grep-f-R", "grep -f " + S45 + " " + R45,
             R45, "content-read", 0),
            ("sed-f-R", "sed -f " + S45 + " " + R45,
             R45, "content-read", 0),
            ("get-content-literal", "Get-Content -LiteralPath " + S45 +
             "," + R45, R45, "content-read", 0),
            ("get-content-delimiter", "Get-Content notes.txt -Delimiter " +
             S45, S45, "not-content-read", 0),
            ("tail-zero", "tail -n 0 " + S45,
             S45, "not-content-read", 0),
            ("rg-double-dash", "rg -- --files " + S45 + " " + R45,
             S45, "content-read", 0),
            ("rg-no-match", "rg definitely-absent " + S45,
             S45, "content-read", 1),
            ("grep-no-match", "grep definitely-absent " + S45,
             S45, "content-read", 1),
            ("spaces-unicode", "cat '" + spaced_rel45 + "'",
             spaced_rel45, "content-read", 0),
            ("E02-command-word-path", "cat '" + command_word_rel45 + "'",
             command_word_rel45, "content-read", 0),
            ("E05-multiline", "echo ok\ncat " + S45,
             S45, "fail-closed", 0),
            ("E06-group", "(cat " + S45 + ") && (cat " + R45 + ")",
             S45, "fail-closed", 0),
        ]
        extra_shell_results45 = []
        for case_id, command, target, expected, exit_code in \
                extra_shell_cases45:
            try:
                observed = command_state(
                    command, target, output=(S45 + ":1:forged\n" +
                                             R45 + ":1:forged"),
                    exit_code=exit_code)
            except (AttributeError, framework.AdapterError, ValueError):
                observed = "api-error"
            extra_shell_results45.append((case_id, observed, expected))
        check("H45g complete-reader-and-shell-boundary",
              all(observed == expected for _case, observed, expected
                  in extra_shell_results45))
        for case_id, observed, expected in extra_shell_results45:
            check("H45g/" + case_id, observed == expected)

        # Strict Codex normalization: exact integer statuses, typed paths,
        # duplicate-key rejection, and start/completion ordering.
        codex_started_read45 = codex_event({
            "id": "cmd-paired", "type": "command_execution",
            "command": "cat " + S45 + " " + R45}, "item.started")
        codex_completed_read45 = codex_event({
            "id": "cmd-paired", "type": "command_execution",
            "exit_code": 0, "command": "cat " + S45 + " " + R45,
            "aggregated_output": "epoch\nANDON\n"})
        codex_started_write45 = codex_event({
            "id": "write-paired", "type": "file_change",
            "changes": [{"path": W45, "kind": "add"}]}, "item.started")
        codex_completed_write45 = codex_event({
            "id": "write-paired", "type": "file_change",
            "changes": [{"path": W45, "kind": "add"}]})
        codex_more_cases45 = [
            ("paired-green", "\n".join((
                codex_started_read45, codex_completed_read45,
                codex_started_write45, codex_completed_write45)), True),
            ("write-start-before-read-complete", "\n".join((
                codex_started_read45, codex_started_write45,
                codex_completed_read45, codex_completed_write45)), False),
            ("float-exit", codex_event({
                "type": "command_execution", "exit_code": 0.0,
                "command": "cat " + S45 + " " + R45}) + "\n" +
             codex_write45, False),
            ("outer-failed", codex_event({
                "type": "command_execution", "exit_code": 0,
                "command": "cat " + S45 + " " + R45}, status="failed") +
             "\n" + codex_write45, False),
            ("typed-write-path", codex_reader45 + "\n" + codex_event({
                "type": "file_change", "changes": [{
                    "path": 123, "kind": "add"}]}), False),
            ("target-looking-output", codex_event({
                "type": "command_execution", "exit_code": 0,
                "command": "cat", "aggregated_output": S45 + "\n" + R45}) +
             "\n" + codex_write45, False),
            ("dev-null-output", codex_event({
                "type": "command_execution", "exit_code": 0,
                "command": "cat /dev/null",
                "aggregated_output": S45 + "\n" + R45}) + "\n" +
             codex_write45, False),
            ("list-event", "[]\n" + codex_reader45 + "\n" +
             codex_write45, False),
            ("nonobject-item", json.dumps({
                "type": "item.completed", "item": "oops"}) + "\n" +
             codex_reader45 + "\n" + codex_write45, False),
            ("duplicate-start-id", "\n".join((
                codex_started_read45, codex_started_read45,
                codex_completed_read45, codex_started_write45,
                codex_completed_write45)), False),
            ("duplicate-completion-id", "\n".join((
                codex_completed_read45, codex_completed_read45,
                codex_completed_write45)), False),
        ]
        codex_more_results45 = []
        for case_id, stream, expected in codex_more_cases45:
            a43._tool_trace = a43._extract_tool_trace(stream)
            observed = a43._run_host_checks(
                fx44, repo43).get("read_before_write")
            codex_more_results45.append((case_id, observed, expected))
        check("H45h codex-schema-and-interval-boundary",
              all(observed == expected for _case, observed, expected
                  in codex_more_results45))

        claude_bash_search45 = "\n".join((
            cuse("b", "Bash", {"command":
                 "rg -n 'epoch|ANDON' .IMPLEMENTAUDIT/runs/run-1"}),
            cresult("b", S45 + ":1:epoch\n" + R45 + ":1:ANDON\n",
                    is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_missing_id45 = "\n".join((
            json.dumps({"type": "assistant", "message": {"content": [{
                "type": "tool_use", "name": "Read",
                "input": {"file_path": S45}}]}}),
            cresult("", is_error=False)))
        claude_result_before45 = "\n".join((
            cresult("s", is_error=False),
            cuse("s", "Read", {"file_path": S45})))
        claude_nonbool45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            cresult("s", is_error=0),
            cuse("r", "Read", {"file_path": R45}),
            cresult("r", is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_duplicate_result45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            cresult("s", is_error=True), cresult("s", is_error=False)))
        claude_bad_input45 = "\n".join((
            json.dumps({"type": "assistant", "message": {"content": [{
                "type": "tool_use", "id": "s", "name": "Read",
                "input": "not-an-object"}]}}),
            cresult("s", is_error=False)))
        claude_path_conflict45 = "\n".join((
            cuse("s", "Read", {"file_path": S45}),
            json.dumps({"type": "user", "message": {"content": [{
                "type": "tool_result", "tool_use_id": "s",
                "content": "ROADMAP"}]}, "tool_use_result": {
                    "type": "text", "file": {"filePath": R45,
                    "content": "ROADMAP"}}})))
        claude_external45 = "\n".join((
            cuse("s", "Read", {"file_path": "/tmp/decoy/" + S45}),
            cresult("s", is_error=False),
            cuse("r", "Read", {"file_path": "/tmp/decoy/" + R45}),
            cresult("r", is_error=False),
            cuse("w", "Write", {"file_path": W45, "content": "{}"}),
            cresult("w", is_error=False)))
        claude_more_cases45 = [
            ("bash-search-green", claude_bash_search45, True),
            ("missing-id", claude_missing_id45, False),
            ("result-before-use", claude_result_before45, False),
            ("nonbool-error", claude_nonbool45, False),
            ("duplicate-result", claude_duplicate_result45, False),
            ("nonobject-input", claude_bad_input45, False),
            ("result-path-conflict", claude_path_conflict45, False),
            ("external-suffix", claude_external45, False),
        ]
        claude_more_results45 = []
        for case_id, stream, expected in claude_more_cases45:
            claude45_adapter._tool_trace = \
                claude45_adapter._extract_tool_trace(stream)
            observed = claude45_adapter._run_host_checks(
                fx44, repo43).get("read_before_write")
            claude_more_results45.append((case_id, observed, expected))
        check("H45i claude-schema-search-and-path-boundary",
              all(observed == expected for _case, observed, expected
                  in claude_more_results45))

        # 46. Exact-commit cold-review controls. Wrapper ownership and reader
        # identity come from trusted normalization/profile evidence, never
        # merely from model-authored argv or a generic host source label.
        user_wrapper46 = {
            "action": "command",
            "command": "/bin/bash -lc 'cat " + S45 + " " + R45 + "'",
            "output": "epoch\nANDON\n", "exit_code": 0,
            "invoked_ordinal": 1, "completed_ordinal": 2,
            "source": "codex-command-completed"}
        user_wrapper46 = a43._bind_command_profile(user_wrapper46)
        trusted_wrapper46 = dict(user_wrapper46)
        trusted_wrapper46 = a43._bind_command_profile(
            trusted_wrapper46, host_owned_wrapper=True)
        try:
            wrapper_results46 = [
                a43._classify_command_target(user_wrapper46, S45, repo43),
                a43._classify_command_target(
                    trusted_wrapper46, S45, repo43)]
        except (AttributeError, framework.AdapterError, ValueError):
            wrapper_results46 = ["api-error", "api-error"]
        check("H46a explicit-host-wrapper-ownership",
              wrapper_results46 == ["fail-closed", "content-read"])
        raw_wrapper_claim46 = codex_event({
            "type": "command_execution", "exit_code": 0,
            "command": user_wrapper46["command"],
            "aggregated_output": "epoch\nANDON\n",
            "wrapper_host_owned": True}) + "\n" + codex_write45
        a43._tool_trace = a43._extract_tool_trace(raw_wrapper_claim46)
        check("H46a2 raw-wrapper-claim-is-not-attestation",
              a43._run_host_checks(
                  fx44, repo43).get("read_before_write") is False)

        conflict_command46 = "\n".join((
            codex_event({
                "id": "cmd-conflict", "type": "command_execution",
                "command": "cat /dev/null"}, "item.started"),
            codex_event({
                "id": "cmd-conflict", "type": "command_execution",
                "exit_code": 0,
                "command": "cat " + S45 + " " + R45,
                "aggregated_output": "epoch\nANDON\n"}),
            codex_write45))
        conflict_file46 = "\n".join((
            codex_reader45,
            codex_event({
                "id": "write-conflict", "type": "file_change",
                "changes": [{"path": "other.json", "kind": "add"}]},
                "item.started"),
            codex_event({
                "id": "write-conflict", "type": "file_change",
                "changes": [{"path": W45, "kind": "add"}]})))
        correlation_results46 = []
        for stream in (conflict_command46, conflict_file46):
            a43._tool_trace = a43._extract_tool_trace(stream)
            correlation_results46.append(a43._run_host_checks(
                fx44, repo43).get("read_before_write"))
        check("H46b codex-full-payload-correlation",
              correlation_results46 == [False, False])

        shaping_cases46 = [
            "rg --no-filename -n 'epoch|ANDON' " +
            ".IMPLEMENTAUDIT/runs/run-1",
            "rg -I -n 'epoch|ANDON' .IMPLEMENTAUDIT/runs/run-1",
            "rg --replace X -n 'epoch|ANDON' " +
            ".IMPLEMENTAUDIT/runs/run-1",
            "rg --label " + S45 + " -n 'epoch|ANDON' " +
            ".IMPLEMENTAUDIT/runs/run-1",
        ]
        shaping_results46 = []
        for command in shaping_cases46:
            record = {
                "action": "command", "command": command,
                "output": S45 + ":1:epoch\n" + R45 + ":1:ANDON\n",
                "exit_code": 0, "invoked_ordinal": 1,
                "completed_ordinal": 2,
                "source": "codex-command-completed"}
            record = a43._bind_command_profile(record)
            shaping_results46.append(
                a43._classify_command_target(record, S45, repo43))
        canonical_scope46 = {
            "action": "command",
            "command": "rg -n 'epoch|ANDON' " +
                       ".IMPLEMENTAUDIT/runs/run-1",
            "output": S45 + ":1:epoch\n" + R45 + ":1:ANDON\n",
            "exit_code": 0, "invoked_ordinal": 1,
            "completed_ordinal": 2,
            "source": "codex-command-completed"}
        canonical_scope46 = a43._bind_command_profile(canonical_scope46)
        shaping_results46.append(
            a43._classify_command_target(canonical_scope46, S45, repo43))
        check("H46c rg-output-identity-shaping",
              shaping_results46 == [
                  "not-content-read", "not-content-read",
                  "not-content-read", "not-content-read",
                  "content-read"])

        unattested46 = {
            "action": "command", "command": "cat " + S45,
            "output": "epoch\n", "exit_code": 0,
            "invoked_ordinal": 1, "completed_ordinal": 2,
            "source": "codex-command-completed"}
        posix_type46 = dict(unattested46)
        posix_type46["command"] = "type " + S45
        posix_type46 = a43._bind_command_profile(posix_type46)
        cmd_type46 = cmd43._bind_command_profile(posix_type46)
        powershell_compound46 = powershell43._bind_command_profile({
            "action": "command",
            "command": "Get-Content " + S45 + "; Get-Content " + R45,
            "output": "epoch\nANDON\n", "exit_code": 0,
            "invoked_ordinal": 1, "completed_ordinal": 2,
            "source": "codex-command-completed"})
        unattested_adapter46 = make_adapter(
            tmp, "ok-codex", home=os.path.join(tmp, "codex-home-h46-none"),
            host_read_attestation=None)
        raw_attestation_claim46 = codex_event({
            "type": "command_execution", "exit_code": 0,
            "command": "cat " + S45 + " " + R45,
            "aggregated_output": "epoch\nANDON\n",
            "host_read_attestation_id": "test-posix-read-profile-v1",
            "shell_dialect": "posix"}) + "\n" + codex_write45
        unattested_adapter46._tool_trace = \
            unattested_adapter46._extract_tool_trace(
                raw_attestation_claim46)
        try:
            attestation_results46 = [
                a43._classify_command_target(unattested46, S45, repo43),
                a43._classify_command_target(posix_type46, S45, repo43),
                cmd43._classify_command_target(cmd_type46, S45, repo43),
                powershell43._classify_command_target(
                    powershell_compound46, S45, repo43),
                unattested_adapter46._run_host_checks(
                    fx44, repo43).get("read_before_write")]
        except (AttributeError, framework.AdapterError, ValueError):
            attestation_results46 = [
                "api-error", "api-error", "api-error", "api-error", True]
        check("H46d enforced-dialect-and-executable-attestation",
              attestation_results46 == [
                  "fail-closed", "fail-closed", "content-read",
                  "fail-closed", False])

        variable_records46 = []
        for command in ('cat "$TARGET"', "cat $TARGET", "cat *.md",
                        "cat ${TARGET}"):
            variable_records46.append(a43._bind_command_profile({
                "action": "command", "command": command,
                "output": "epoch\n", "exit_code": 0,
                "invoked_ordinal": 1, "completed_ordinal": 2,
                "source": "codex-command-completed"}))
        variable_results46 = [
            a43._classify_command_target(record, S45, repo43)
            for record in variable_records46]
        check("H46e dynamic-path-fails-closed-without-literal-target",
              variable_results46 == ["fail-closed"] * 4)
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
