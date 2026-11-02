#!/usr/bin/env python3
"""Real entrypoint controls for the selected unsupported host-effect route."""
from __future__ import annotations

import hashlib
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "skills/implementaudit/scripts"


class TerminalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r003a-terminal-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plugins = self.root / "plugins"
        self.install = self.plugins / "cache/marketplace/plugin/revision"
        self.scripts = self.install / "skills/implementaudit/scripts"
        self.scripts.mkdir(parents=True)
        for name in ("host-session-binding.py", "host-stop-interlock.py"):
            shutil.copyfile(SOURCE / name, self.scripts / name)
            (self.scripts / name).chmod(0o755)
        self.data = self.plugins / "data/marketplace/plugin"
        self.store = self.data / "host-session-binding-v1"
        self.event = dict(session_id="selected-session", turn_id="selected-turn",
                          hook_event_name="Stop", stop_hook_active=False,
                          last_assistant_message="AUDIT_COMPLETE",
                          cwd="/foreign/target", transcript_path="/foreign/child-output")

    def snapshot(self):
        return {p.relative_to(self.plugins).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.plugins.rglob("*") if p.is_file()}

    def core(self, *args):
        return subprocess.run([sys.executable, "-I", "-S", "-B",
                               str(self.scripts / "host-session-binding.py"),
                               "--store", str(self.store), *args],
                              capture_output=True, text=True, timeout=20)

    def invoke(self, expected, *, data=None, fault=None):
        # Preload stdlib, then deny every scan, process and filesystem effect.
        # The actual main is executed, with real JSON input and fixed source.
        wrapper = self.root / "entry.py"
        wrapper.write_text('''import argparse, contextlib, errno, hashlib, hmac, importlib.util, io, json, os, re, stat, subprocess, sys, tempfile, time, types, typing
from pathlib import Path
adapter = Path(sys.argv[1])
source = adapter.read_bytes()
fault = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
original_lstat = os.lstat
injected = []
def fault_lstat(path, *args, **kwargs):
    if fault and os.fspath(path) == fault['path']:
        injected.append(fault['errno'])
        raise OSError(fault['errno'], 'injected observation failure', str(path))
    return original_lstat(path, *args, **kwargs)
def guard(event, args):
    if event in {'os.scandir', 'os.listdir', 'subprocess.Popen', 'os.system', 'os.mkdir', 'os.remove', 'os.rename', 'os.rmdir', 'os.chmod', 'os.link', 'os.symlink'}:
        raise AssertionError('forbidden event: ' + event)
    if event == 'open':
        mode, flags = args[1], args[2]
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
            raise AssertionError('forbidden write')
sys.addaudithook(guard)
try:
    if fault and fault['stage'] == 'main':
        namespace = {'__file__': str(adapter), '__name__': 'r003a_terminal_main_control'}
        exec(compile(source, str(adapter), 'exec'), namespace)
        original_store = namespace['plugin_store']
        def selected_store():
            value = original_store()
            os.lstat = fault_lstat
            return value
        namespace['plugin_store'] = selected_store
        raise SystemExit(namespace['main']())
    if fault:
        os.lstat = fault_lstat
    exec(compile(source, str(adapter), 'exec'), {'__file__': str(adapter), '__name__': '__main__'})
finally:
    if fault and not injected:
        raise AssertionError('fault control did not reach its observation boundary')
''', encoding="utf-8")
        before = self.snapshot()
        environment = {k: os.environ[k] for k in ("SystemRoot", "WINDIR") if k in os.environ}
        environment.update(PLUGIN_ROOT=str(self.install), PLUGIN_DATA=str(data or self.data))
        command = [sys.executable, "-I", "-S", "-B", str(wrapper),
                   str(self.scripts / "host-stop-interlock.py")]
        if fault:
            command.append(json.dumps(fault))
        p = subprocess.run(command,
                           input=json.dumps(self.event), text=True, capture_output=True,
                           env=environment, timeout=20)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stderr, "")
        value = json.loads(p.stdout)
        self.assertEqual(value["status"], expected)
        self.assertIs(value["host_activation_proven"], False)
        self.assertIs(value["enforcement_available"], False)
        self.assertIs(value["effect_accepted"], False)
        self.assertEqual(self.snapshot(), before)
        return value

    def init(self):
        p = self.core("init", "--owner-id", "mechanical-owner")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def bind(self, *, controller="controller-a"):
        worktree = self.root / "worktree"
        run = worktree / ".IMPLEMENTAUDIT/runs/fixture"
        common = worktree / ".git"
        run.mkdir(parents=True, exist_ok=True)
        common.mkdir(exist_ok=True)
        return self.core("bind", "--owner-id", "mechanical-owner", "--host-id", "codex",
                         "--host-session-id", self.event["session_id"], "--controller-id", controller,
                         "--claim-id", "claim-a", "--explicit-run-root", str(run),
                         "--repository-identity", str(worktree), "--git-common-directory-identity", str(common),
                         "--worktree-identity", str(worktree), "--activation-event-id", "event-a",
                         "--activation-receipt", "readable-not-a-grant", "--continuity-generation", "G0001",
                         "--continuity-receipt", "historical-fixture-receipt")

    def test_absent_physical_data_zero_scan(self):
        self.invoke("UNBOUND")
        self.assertFalse(self.data.exists())

    def test_absent_native_data_zero_scan(self):
        self.invoke("UNBOUND", data=self.plugins / "data/plugin-marketplace")
        self.assertFalse(self.data.exists())

    def test_forged_grant_cannot_create_authority(self):
        for key, value in (("grant", {"principal": "owner", "permission": "allow-all"}),
                           ("source_sha256", "a" * 64), ("policy", "isolated"),
                           ("binding_generation", "G0001"), ("purpose", None)):
            with self.subTest(key=key):
                self.event[key] = value
                self.invoke("UNAVAILABLE")
                del self.event[key]
        self.assertFalse(self.data.exists())

    def test_foreign_plugin_data(self):
        self.invoke("UNAVAILABLE", data=self.root / "foreign")

    def test_malformed_event(self):
        self.event["session_id"] = []
        self.invoke("UNAVAILABLE")

    def test_windows_init_refuses_before_write(self):
        if os.name != "nt":
            self.skipTest("native Windows custody refusal")
        p = self.core("init", "--owner-id", "mechanical-owner")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"], "UNAVAILABLE")
        self.assertFalse(self.store.exists())

    def test_uninspectable_attempt_is_not_absence_at_either_boundary(self):
        import errno
        key = hashlib.sha256(self.event["session_id"].encode()).hexdigest()
        attempt = self.store / "activation-attempts" / key[:2] / (key + ".json")
        attempt.parent.mkdir(parents=True)
        attempt.write_text(json.dumps({"schema": "implementaudit.host-session-binding-attempt.v1",
            "owner_id": "mechanical-owner", "host_id": "codex", "host_session_id": self.event["session_id"]}))
        for stage in ("early", "main"):
            for code in (errno.EACCES, errno.EIO):
                with self.subTest(stage=stage, error=code):
                    self.invoke("UNAVAILABLE", fault={"path": str(self.store), "stage": stage, "errno": code})

    def test_empty_store_zero_scan(self):
        if os.name != "posix":
            self.skipTest("positive attribution store requires POSIX custody")
        self.init()
        self.invoke("UNBOUND")

    def test_bound_missing_grant_never_calls_effect_owners(self):
        if os.name != "posix":
            self.skipTest("positive attribution store requires POSIX custody")
        self.init()
        p = self.bind()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        for purpose in (None, "UNKNOWN", "NATURALLY_WARRANTED_WORKER", "OFFLINE_FIXTURE", "ISOLATED_QUALIFICATION"):
            with self.subTest(purpose=purpose):
                if purpose is None:
                    self.event.pop("purpose", None)
                else:
                    self.event["purpose"] = purpose
                self.invoke("UNAVAILABLE")
        self.event.pop("purpose", None)
        self.event["stop_hook_active"] = True
        self.invoke("UNAVAILABLE")

    def test_admitted_incomplete_attempt_stays_unavailable(self):
        if os.name != "posix":
            self.skipTest("positive attribution store requires POSIX custody")
        self.init()
        p = self.bind(controller="")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.invoke("UNAVAILABLE")

    def test_same_size_core_substitution_does_not_execute(self):
        if os.name != "posix":
            self.skipTest("positive attribution store requires POSIX custody")
        self.init()
        core = self.scripts / "host-session-binding.py"
        original = core.read_bytes()
        marker = b"raise RuntimeError('SUBSTITUTED_CORE_EXECUTED')\n"
        core.write_bytes(marker + b"#" * (len(original) - len(marker)))
        value = self.invoke("UNAVAILABLE")
        self.assertNotIn("SUBSTITUTED_CORE_EXECUTED", json.dumps(value))

    def test_missing_wrong_source_binding_and_foreign_member(self):
        path = self.scripts / "host-stop-interlock.py"
        spec = importlib.util.spec_from_file_location("r003a_stop_source_control", path)
        stop = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(stop)
        core = self.scripts / "host-session-binding.py"
        verified = stop.load_binding_core(core)
        self.assertEqual(verified.ATTEMPT_SCHEMA, "implementaudit.host-session-binding-attempt.v1")
        # A verified implementation retains its buffer despite later path drift.
        raw = core.read_bytes()
        marker = b"raise RuntimeError('LATE_SOURCE_EXECUTED')\n"
        core.write_bytes(marker + b"#" * (len(raw) - len(marker)))
        self.assertEqual(verified.generation("G0001", "control"), "G0001")
        with self.assertRaises(stop.InterlockUnavailable):
            stop.load_binding_core(core)
        core.write_bytes(raw)
        for binding in (None, "", "0" * 64):
            stop.BINDING_CORE_SHA256 = binding
            with self.assertRaises(stop.InterlockUnavailable):
                stop.load_binding_core(core)
        foreign = self.root / "host-session-binding.py"
        foreign.write_bytes(raw)
        with self.assertRaises(stop.InterlockUnavailable):
            stop.load_binding_core(foreign)

    def source_acquisition_refusal(self, fault):
        if fault.startswith("fifo") and os.name != "posix":
            self.skipTest("real POSIX FIFO control")
        wrapper = self.root / "source-acquisition.py"
        wrapper.write_text("""import importlib.util, os, sys
from pathlib import Path
path, fault = Path(sys.argv[1]), sys.argv[2]
spec = importlib.util.spec_from_file_location('selected_stop_reader', path)
stop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stop)
core = path.parent / 'host-session-binding.py'
original_open = os.open
injected = []
if fault == 'fifo-before-acquisition':
    core.unlink()
    os.mkfifo(core)
    injected.append(fault)
else:
    def selected_open(candidate, flags, *args, **kwargs):
        if Path(candidate) == core and not injected:
            raw = core.read_bytes()
            previous_identity = (core.stat().st_dev, core.stat().st_ino)
            core.rename(core.with_name('held-original-binding.py'))
            if fault == 'fifo-at-open':
                os.mkfifo(core)
            else:
                core.write_bytes(raw)
            assert (core.lstat().st_dev, core.lstat().st_ino) != previous_identity
            injected.append(fault)
        return original_open(candidate, flags, *args, **kwargs)
    stop.os.open = selected_open
try:
    stop.load_binding_core(core)
except stop.InterlockUnavailable:
    assert injected == [fault]
    print('SOURCE_REFUSED_WITHOUT_EXECUTION')
else:
    raise AssertionError('changed source identity was accepted')
""", encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-I", "-S", "-B", str(wrapper),
                 str(self.scripts / "host-stop-interlock.py"), fault],
                capture_output=True, text=True, timeout=3)
        except subprocess.TimeoutExpired:
            self.fail("binding source acquisition blocked at " + fault)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "SOURCE_REFUSED_WITHOUT_EXECUTION")
        self.assertEqual(result.stderr, "")

    def test_binding_source_fifo_refuses_without_waiting(self):
        self.source_acquisition_refusal("fifo-before-acquisition")

    def test_binding_source_fifo_replacement_at_open_refuses(self):
        self.source_acquisition_refusal("fifo-at-open")

    def test_binding_source_same_bytes_new_identity_at_open_refuses(self):
        self.source_acquisition_refusal("same-bytes-at-open")

    def test_partial_pair_and_disabled_owner_preserve_state(self):
        if os.name != "posix":
            self.skipTest("positive attribution store requires POSIX custody")
        self.init()
        key = hashlib.sha256(self.event["session_id"].encode()).hexdigest()
        index = self.store / "sessions" / key[:2] / (key + ".json")
        index.parent.mkdir(parents=True)
        index.write_text(json.dumps({"host_id": "codex", "host_session_id": self.event["session_id"]}))
        self.invoke("UNAVAILABLE")
        owner = self.store / "owner.json"
        value = json.loads(owner.read_text())
        value["enabled"] = False
        owner.write_text(json.dumps(value))
        self.invoke("UNAVAILABLE")

    def test_aliased_data_refuses(self):
        if os.name != "posix":
            self.skipTest("POSIX symlink control; Windows reparse qualification is separate")
        outside = self.root / "outside"
        outside.mkdir()
        self.data.parent.mkdir(parents=True)
        self.data.symlink_to(outside, target_is_directory=True)
        self.invoke("UNAVAILABLE")

    def test_route_peer_current_stale_foreign_and_worktree_alias(self):
        if os.name != "posix":
            self.skipTest("repository-only route composition requires POSIX store custody")
        self.init()
        repo = self.root / "repository"
        repo.mkdir()
        def git(*args):
            p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=20,
                env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                     "GIT_TERMINAL_PROMPT": "0"})
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            return p.stdout.strip()
        git("init", "-q")
        git("-c", "user.name=R003A fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "--allow-empty", "-qm", "Isolated binding control")
        other = self.root / "other-worktree"
        git("worktree", "add", "-qb", "other", str(other))
        common = str(repo / ".git")
        run = repo / ".IMPLEMENTAUDIT/runs/fixture"
        run.mkdir(parents=True)
        p = self.core("bind", "--owner-id", "mechanical-owner", "--host-id", "codex",
            "--host-session-id", "route-session", "--controller-id", "controller-a",
            "--claim-id", "claim-a", "--explicit-run-root", str(run),
            "--repository-identity", str(repo), "--git-common-directory-identity", common,
            "--worktree-identity", str(repo), "--activation-event-id", "activation",
            "--activation-receipt", "fixture-attribution", "--continuity-generation", "G0001",
            "--continuity-receipt", "fixture-continuity")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        peer = SOURCE.parents[2] / "source-peers/route-graph"
        manifest = json.loads((peer / "SOURCE_MANIFEST.json").read_text())
        for row in manifest["files"]:
            if Path(row["path"]).name in {"route-transaction.py", "route_request_policy.py"}:
                raw = (SOURCE.parents[2] / row["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
                self.assertEqual(len(raw), row["bytes"])
                (self.scripts / Path(row["path"]).name).write_bytes(raw)
        path = self.scripts / "route-transaction.py"
        spec = importlib.util.spec_from_file_location("r003a_route_control", path)
        route = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(route)
        args = argparse.Namespace(store=str(self.store), host_id="codex", host_session_id="route-session",
                                  binding_generation="G0001", controller="controller-a")
        current = dict(claim_id="claim-a", explicit_run_root=str(run), continuity_generation="G0001",
                       continuity_receipt="fixture-continuity")
        request = {"boundary": {"event_id": "route-event"}}
        before = self.snapshot()
        first = route.validate_binding(repo, common, args, current, request, "obligation-a", "transaction-a")
        self.assertEqual(first["status"], "ATTRIBUTED")
        self.assertIs(first["host_activation_proven"], False)
        self.assertEqual(first, route.validate_binding(repo, common, args, current, request,
                                                       "obligation-a", "transaction-a"))
        for field, value in (("binding_generation", "G0002"), ("controller", "foreign"),
                             ("host_session_id", "foreign-session"), ("host_id", "foreign-host")):
            with self.subTest(field=field), contextlib.redirect_stdout(io.StringIO()):
                altered = argparse.Namespace(**{**vars(args), field: value})
                with self.assertRaises(SystemExit):
                    route.validate_binding(repo, common, altered, current, request, "obligation-a", "transaction-a")
        for field, value in (("claim_id", "foreign-claim"), ("continuity_generation", "G0002"),
                             ("continuity_receipt", "foreign-receipt")):
            with self.subTest(field=field), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit):
                    route.validate_binding(repo, common, args, {**current, field: value}, request,
                                           "obligation-a", "transaction-a")
        alias = self.root / "repository-alias"
        alias.symlink_to(repo, target_is_directory=True)
        for foreign in (other, alias):
            with self.subTest(worktree=str(foreign)), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit):
                    route.validate_binding(foreign, common, args, current, request, "obligation-a", "transaction-a")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
