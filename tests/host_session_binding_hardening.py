#!/usr/bin/env python3
"""Source/storage qualification of the existing R003A core, not native authority."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
CORE = Path(os.environ.get(
    "R003A_BINDING_CORE", str(REPO / "skills/implementaudit/scripts/host-session-binding.py")
)).resolve()
spec = importlib.util.spec_from_file_location("binding_core_under_test", CORE)
core = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(core)

FAULT_RUNNER = r'''
import importlib.util,os,sys
from pathlib import Path
source,fault=sys.argv[1:3]
spec=importlib.util.spec_from_file_location("binding_core",source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if fault == "bind-before-state-write":
 original=module.atomic_json
 def interrupted(path,payload):
  if path.name == "binding.json":
   raise OSError("diagnostic interruption before state write")
  return original(path,payload)
 module.atomic_json=interrupted
elif fault == "after-replace":
 original=os.replace
 def interrupted(source,target):
  original(source,target)
  raise OSError("diagnostic interruption after replace")
 os.replace=interrupted
elif fault == "owner-partial-create":
 def interrupt_owner(original):
  def interrupted(path,payload):
   if path.name == "owner.json":
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    os.write(descriptor,b"{")
    os.close(descriptor)
    raise OSError("diagnostic uncertain owner creation")
   return original(path,payload)
  return interrupted
 module.atomic_json=interrupt_owner(module.atomic_json)
 module.atomic_create_json=interrupt_owner(module.atomic_create_json)
elif fault in {"attempt-partial-create", "after-attempt-create"}:
 original=module.atomic_create_json
 def interrupted(path,payload):
  if path.parent.parent.name == "activation-attempts":
   if fault == "attempt-partial-create":
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    os.write(descriptor,b"{")
    os.close(descriptor)
   else:
    original(path,payload)
   raise OSError("diagnostic uncertain activation attempt creation")
  return original(path,payload)
 module.atomic_create_json=interrupted
sys.argv=[source]+sys.argv[3:]
raise SystemExit(module.main())
'''


class BindingHardening(unittest.TestCase):
    def setUp(self):
        temporary_root = os.environ.get("R003A_TEST_TMPDIR")
        self.temporary = tempfile.TemporaryDirectory(prefix="r003a-core-", dir=temporary_root)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.store = self.root / "store"
        self.repository = self.root / "repository"
        self.common = self.root / "git-common"
        self.worktree = self.root / "worktree"
        self.run = self.worktree / ".IMPLEMENTAUDIT/runs/current"
        for path in (self.repository, self.common, self.run):
            path.mkdir(parents=True)
        self.options = {
            "owner_id": "fixture-owner", "host_id": "codex", "host_session_id": "session-a",
            "controller_id": "controller-a", "claim_id": "claim-a", "explicit_run_root": str(self.run),
            "repository_identity": str(self.repository), "git_common_directory_identity": str(self.common),
            "worktree_identity": str(self.worktree), "activation_event_id": "activation-1",
            "activation_receipt": "activation-receipt-1", "continuity_generation": "G0001",
            "continuity_receipt": "continuity-receipt-1",
        }

    def arguments(self, options):
        return [item for key, value in options.items()
                for item in ("--" + key.replace("_", "-"), str(value))]

    def run_core(self, command, *, options=None, extra=(), raw_input=None, fault=None):
        arguments = ["--store", str(self.store), command, *self.arguments(options or {}), *extra]
        invocation = [sys.executable, "-B", str(CORE)]
        if fault is not None:
            invocation = [sys.executable, "-B", "-c", FAULT_RUNNER, str(CORE), fault]
        process = subprocess.run(invocation + arguments, input=raw_input,
                                 capture_output=True, text=True, timeout=15)
        try:
            payload = json.loads(process.stdout)
        except json.JSONDecodeError:
            payload = None
        return process, payload

    def expect(self, command, status, **kwargs):
        process, payload = self.run_core(command, **kwargs)
        self.assertEqual(process.stderr, "", process.stderr)
        self.assertIsInstance(payload, dict, process.stdout or "no structured result")
        self.assertEqual(payload.get("status"), status, payload)
        self.assertEqual(process.returncode, 2 if status == "UNAVAILABLE" else 0, payload)
        if status == "UNAVAILABLE":
            self.assertIs(payload.get("enforcement_available"), False)
        return payload

    def init(self):
        return self.expect("init", "READY", options={"owner_id": "fixture-owner"})

    def bind(self, options=None):
        self.init()
        return self.expect("bind", "BOUND", options=options or self.options)

    def lookup_options(self, session="session-a"):
        return {"host_id": "codex", "host_session_id": session}

    def state_path(self, session="session-a"):
        return core.state_path(self.store, "codex", session)

    def attempt_path(self, session="session-a"):
        index = core.session_index_path(self.store, session)
        return self.store / "activation-attempts" / index.parent.name / index.name

    def event_options(self, generation="G0001"):
        keys = ("host_id", "host_session_id", "controller_id", "claim_id", "explicit_run_root",
                "repository_identity", "git_common_directory_identity", "worktree_identity",
                "continuity_generation", "continuity_receipt")
        return {**{key: self.options[key] for key in keys},
                "binding_generation": generation, "event_id": "event-1"}

    def test_legacy_opaque_owner_inputs_remain_supported(self):
        self.assertFalse((self.repository / ".git").exists())
        result = self.bind()
        self.assertFalse(result["host_activation_proven"])
        self.assertEqual(result["binding"]["controller_id"], "controller-a")
        self.expect("validate-event", "ATTRIBUTED", options=self.event_options())

    def test_two_actual_git_worktrees_and_sessions_remain_isolated(self):
        repository = self.root / "actual-repository"
        subprocess.run(["git", "init", "--quiet", str(repository)], check=True, capture_output=True)
        worktrees = [self.root / "actual-worktree-a", self.root / "actual-worktree-b"]
        common = []
        for ordinal, worktree in enumerate(worktrees):
            # Unborn worktrees exercise real Git common-directory custody without creating commits.
            result = subprocess.run(["git", "-C", str(repository), "worktree", "add", "--quiet",
                                     "--orphan", "-b", f"fixture-{ordinal}", str(worktree)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            common.append(subprocess.check_output(
                ["git", "-C", str(worktree), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                text=True).strip())
        self.assertEqual(common[0], common[1])
        self.init()
        for ordinal, worktree in enumerate(worktrees):
            run = worktree / ".IMPLEMENTAUDIT/runs/current"
            run.mkdir(parents=True)
            options = dict(self.options, host_session_id=f"session-{ordinal}", claim_id=f"claim-{ordinal}",
                           repository_identity=str(repository), git_common_directory_identity=common[ordinal],
                           worktree_identity=str(worktree), explicit_run_root=str(run))
            self.expect("bind", "BOUND", options=options)
            looked_up = self.expect("lookup", "BOUND", options=self.lookup_options(f"session-{ordinal}"))
            self.assertEqual(looked_up["binding"]["worktree_identity"], str(worktree))
            event = {key: value for key, value in options.items()
                     if key not in {"owner_id", "activation_event_id", "activation_receipt"}}
            event.update(binding_generation="G0001", event_id="worktree-event",
                         worktree_identity=str(worktrees[1 - ordinal]))
            self.expect("validate-event", "UNAVAILABLE", options=event)

    def test_concurrent_rebind_has_one_generation_winner(self):
        self.bind()
        processes = []
        for suffix in ("one", "two"):
            options = dict(self.options, expected_generation="G0001", reason="concurrent-rebind",
                           controller_id="controller-" + suffix)
            processes.append(subprocess.Popen(
                [sys.executable, "-B", str(CORE), "--store", str(self.store), "rebind", *self.arguments(options)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        results = [process.communicate(timeout=15) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2])
        self.assertTrue(all(not errors for _, errors in results))
        self.assertEqual(sorted(json.loads(output)["status"] for output, _ in results), ["BOUND", "UNAVAILABLE"])
        state = json.loads(self.state_path().read_text())
        self.assertEqual([record["binding_generation"] for record in state["records"]], ["G0001", "G0002"])

    @unittest.skipUnless(os.name == "posix", "POSIX interleaving control; Windows is unqualified")
    def test_concurrent_initialisers_cannot_both_establish_different_owners(self):
        import fcntl
        self.store.mkdir(mode=0o700)
        ready, release = threading.Event(), threading.Event()
        second_progress = queue.Queue()
        outputs, returncodes = io.StringIO(), {}
        original_atomic, original_create, original_flock = core.atomic_json, core.atomic_create_json, fcntl.flock

        def delay(function):
            def delayed(path, payload):
                if path == self.store / "owner.json" and threading.current_thread().name == "owner-one":
                    ready.set()
                    if not release.wait(10):
                        raise RuntimeError("test owner write was never released")
                return function(path, payload)
            return delayed

        def observed_flock(descriptor, operation):
            if operation == fcntl.LOCK_EX and threading.current_thread().name == "owner-two":
                second_progress.put("waiting-for-owner-lock")
            return original_flock(descriptor, operation)

        def initialise(owner):
            try:
                core.command_init(argparse.Namespace(store=str(self.store), owner_id=owner))
                returncodes[owner] = 0
            except SystemExit as error:
                returncodes[owner] = error.code
            finally:
                if owner == "owner-two":
                    second_progress.put("finished")

        with contextlib.redirect_stdout(outputs), mock.patch.object(core, "atomic_json", delay(original_atomic)), \
                mock.patch.object(core, "atomic_create_json", delay(original_create)), \
                mock.patch.object(fcntl, "flock", observed_flock):
            first = threading.Thread(target=initialise, args=("owner-one",), name="owner-one")
            second = threading.Thread(target=initialise, args=("owner-two",), name="owner-two")
            first.start()
            self.assertTrue(ready.wait(10), "first owner never reached its storage write")
            second.start()
            second_progress.get(timeout=10)
            release.set()
            first.join(10)
            second.join(10)
            self.assertFalse(first.is_alive() or second.is_alive())
        self.assertEqual(sorted(returncodes.values()), [0, 2], outputs.getvalue())
        self.assertEqual(json.loads((self.store / "owner.json").read_text())["owner_id"], "owner-one")

    @unittest.skipUnless(os.name == "posix", "POSIX flock proof; Windows is unqualified")
    def test_waiting_writer_refuses_replaced_lock_identity(self):
        import fcntl
        self.init()
        path = self.store / ".writer.lock"
        if not path.exists():
            path.write_bytes(b"\0")
            path.chmod(0o600)
        first_descriptor = os.open(path, os.O_RDWR)
        original_flock = fcntl.flock
        original_flock(first_descriptor, fcntl.LOCK_EX)
        waiting = threading.Event()
        entered, errors, output = [], [], io.StringIO()

        def observed_flock(descriptor, operation):
            if operation == fcntl.LOCK_EX and threading.current_thread().name == "waiting-writer":
                waiting.set()
            return original_flock(descriptor, operation)

        def wait_for_lock():
            try:
                with core.writer_lock(self.store):
                    entered.append(True)
            except SystemExit as error:
                errors.append(error.code)

        try:
            with contextlib.redirect_stdout(output), mock.patch.object(fcntl, "flock", observed_flock):
                thread = threading.Thread(target=wait_for_lock, name="waiting-writer")
                thread.start()
                self.assertTrue(waiting.wait(10), "writer never reached the real blocking lock")
                path.rename(self.store / "old-lock")
                path.write_bytes(b"\0")
                path.chmod(0o600)
                second_descriptor = os.open(path, os.O_RDWR)
                try:
                    original_flock(second_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    original_flock(first_descriptor, fcntl.LOCK_UN)
                    thread.join(10)
                    self.assertFalse(thread.is_alive())
                finally:
                    os.close(second_descriptor)
        finally:
            os.close(first_descriptor)
        self.assertEqual(entered, [], "waiting writer entered under a retired lock inode")
        self.assertEqual(errors, [2], output.getvalue())
        self.assertEqual(json.loads(output.getvalue())["status"], "UNAVAILABLE")

    @unittest.skipUnless(os.name == "posix", "POSIX waiting-owner proof; Windows is unqualified")
    def test_waiting_writer_rechecks_disabled_owner(self):
        import fcntl
        self.bind()
        original_state = self.state_path().read_bytes()
        descriptor = os.open(self.store / ".writer.lock", os.O_RDWR)
        original_flock = fcntl.flock
        original_flock(descriptor, fcntl.LOCK_EX)
        waiting, output, codes = threading.Event(), io.StringIO(), []

        def observed_flock(opened, operation):
            if operation == fcntl.LOCK_EX and threading.current_thread().name == "owner-waiter":
                waiting.set()
            return original_flock(opened, operation)

        def rebind():
            try:
                core.command_rebind(argparse.Namespace(
                    store=str(self.store), **dict(self.options, expected_generation="G0001", reason="owner-wait")))
                codes.append(0)
            except SystemExit as error:
                codes.append(error.code)

        try:
            with contextlib.redirect_stdout(output), mock.patch.object(fcntl, "flock", observed_flock):
                thread = threading.Thread(target=rebind, name="owner-waiter")
                thread.start()
                self.assertTrue(waiting.wait(10), "writer never reached the real blocking lock")
                owner_path = self.store / "owner.json"
                owner = json.loads(owner_path.read_bytes())
                owner["enabled"] = False
                owner_path.write_text(json.dumps(owner))
                original_flock(descriptor, fcntl.LOCK_UN)
                thread.join(10)
                self.assertFalse(thread.is_alive())
        finally:
            os.close(descriptor)
        self.assertEqual(codes, [2], output.getvalue())
        self.assertEqual(json.loads(output.getvalue())["status"], "UNAVAILABLE")
        self.assertEqual(self.state_path().read_bytes(), original_state)

    def checked_read_swap(self, *, symlink):
        self.bind()
        target = self.state_path()
        expected_inode = target.stat().st_ino
        original_bytes = target.read_bytes()
        substituted = original_bytes.replace(b'"controller-a"', b'"controller-b"')
        self.assertEqual(len(original_bytes), len(substituted), "same-size drift control")
        foreign = self.root / "foreign-state.json"
        foreign.write_bytes(substituted)
        real_open = io.open
        substituted_once = []

        def intercepted_open(file, mode="r", *args, **kwargs):
            selected = ((isinstance(file, int) and os.fstat(file).st_ino == expected_inode)
                        or (not isinstance(file, int) and Path(file) == target))
            if selected and "r" in mode and not substituted_once:
                substituted_once.append(True)
                if symlink:
                    target.unlink()
                    target.symlink_to(foreign)
                else:
                    with real_open(target, "wb") as stream:
                        stream.write(substituted)
            return real_open(file, mode, *args, **kwargs)

        output = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(output), mock.patch.object(io, "open", intercepted_open):
            try:
                core.command_lookup(argparse.Namespace(store=str(self.store), **self.lookup_options()))
            except SystemExit as error:
                code = error.code
        self.assertTrue(substituted_once, "test did not reach actual byte consumption")
        payload = json.loads(output.getvalue())
        self.assertEqual((code, payload.get("status")), (2, "UNAVAILABLE"), payload)

    @unittest.skipUnless(os.name == "posix", "Symlink race proof; Windows is unqualified")
    def test_checked_json_read_refuses_alias_replacement(self):
        self.checked_read_swap(symlink=True)

    def test_checked_json_read_refuses_same_size_in_place_drift(self):
        self.checked_read_swap(symlink=False)

    def test_duplicate_owner_policy_members_are_unavailable(self):
        self.bind()
        path = self.store / "owner.json"
        path.write_text('{"schema":"' + core.STORE_SCHEMA + '","owner_id":"fixture-owner",'
                        '"trusted":false,"trusted":true,"enabled":true}')
        self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())

    def test_malformed_typed_binding_fields_are_structured_unavailable(self):
        self.bind()
        path = self.state_path()
        original = json.loads(path.read_text())
        for field, value in (("binding_generation", None), ("binding_generation", 1),
                             ("binding_generation", []), ("applicable_continuity_generation", {}),
                             ("status", []), ("status", {})):
            with self.subTest(field=field, value=value):
                state = json.loads(json.dumps(original))
                state["records"][-1][field] = value
                path.write_text(json.dumps(state))
                self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())

    def test_empty_owner_identity_is_unavailable(self):
        self.bind()
        path = self.store / "owner.json"
        owner = json.loads(path.read_text())
        owner["owner_id"] = ""
        path.write_text(json.dumps(owner))
        self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())

    @unittest.skipUnless(os.name == "posix", "POSIX mode custody proof; Windows ACLs are unqualified")
    def test_store_and_file_write_permissions_are_checked(self):
        self.bind()
        for path in (self.store, self.store / "owner.json", self.store / "bindings",
                     self.store / "sessions", self.state_path().parent, self.state_path()):
            previous = path.stat().st_mode & 0o777
            with self.subTest(path=path.name):
                try:
                    path.chmod(previous | 0o022)
                    self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())
                finally:
                    path.chmod(previous)
        self.expect("lookup", "BOUND", options=self.lookup_options())

        # Refusal must precede creating a new session prefix beneath an already
        # unsafe custody directory, not merely precede the marker file write.
        attempts = self.store / "activation-attempts"
        new_marker = self.attempt_path("new-permission-session")
        self.assertFalse(new_marker.parent.exists())
        previous = attempts.stat().st_mode & 0o777
        try:
            attempts.chmod(previous | 0o022)
            self.expect("bind", "UNAVAILABLE", options=dict(self.options, host_session_id="new-permission-session"))
            self.assertFalse(new_marker.parent.exists(), "refused custody admission still created a session prefix")
        finally:
            attempts.chmod(previous)

    def test_interrupted_binding_attempt_keeps_unavailable_partial_pair(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=self.options, fault="bind-before-state-write")
        self.assertTrue(core.session_index_path(self.store, "session-a").exists())
        self.assertFalse(self.state_path().exists())
        before = core.session_index_path(self.store, "session-a").read_bytes()
        self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())
        self.expect("bind", "UNAVAILABLE", options=self.options)
        self.assertEqual(core.session_index_path(self.store, "session-a").read_bytes(), before)

    def test_uncertain_rebind_keeps_consumed_generation(self):
        self.bind()
        options = dict(self.options, expected_generation="G0001", reason="uncertain-acknowledgement")
        self.expect("rebind", "UNAVAILABLE", options=options, fault="after-replace")
        current = self.expect("lookup", "BOUND", options=self.lookup_options())
        self.assertEqual(current["binding"]["binding_generation"], "G0002")
        self.expect("rebind", "UNAVAILABLE", options=options)

    def test_uncertain_owner_creation_is_not_replaced(self):
        self.expect("init", "UNAVAILABLE", options={"owner_id": "fixture-owner"}, fault="owner-partial-create")
        owner = self.store / "owner.json"
        self.assertEqual(owner.read_bytes(), b"{")
        self.expect("init", "UNAVAILABLE", options={"owner_id": "fixture-owner"})
        self.assertEqual(owner.read_bytes(), b"{")

    def test_failed_first_bind_remains_unavailable_until_valid_owner_retry(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=dict(self.options, controller_id=""))
        marker = self.attempt_path()
        self.assertTrue(marker.exists(), "an admitted failed activation lost its session attribution")
        self.assertEqual(json.loads(marker.read_bytes()), {
            "schema": "implementaudit.host-session-binding-attempt.v1",
            "owner_id": "fixture-owner", "host_id": "codex", "host_session_id": "session-a"})
        self.assertFalse(core.session_index_path(self.store, "session-a").exists())
        self.assertFalse(self.state_path().exists())
        output = io.StringIO()
        with mock.patch.object(os, "scandir", side_effect=AssertionError("attempt lookup scan")), \
                contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as failure:
            core.command_lookup(argparse.Namespace(store=str(self.store), **self.lookup_options()))
        self.assertEqual(failure.exception.code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "UNAVAILABLE")
        before = marker.read_bytes()
        result = self.expect("bind", "BOUND", options=self.options)
        self.assertEqual(result["binding"]["binding_generation"], "G0001")
        self.assertIs(result["host_activation_proven"], False)
        self.assertEqual(marker.read_bytes(), before)
        self.expect("lookup", "BOUND", options=self.lookup_options())

    def test_failed_attempt_refuses_foreign_host_without_poisoning_owner_retry(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=dict(self.options, continuity_receipt=""))
        self.assertTrue(self.attempt_path().exists(), "missing admitted attempt marker")
        before = self.attempt_path().read_bytes()
        self.expect("lookup", "UNAVAILABLE", options=dict(self.lookup_options(), host_id="claude-code"))
        self.expect("bind", "UNAVAILABLE", options=dict(self.options, host_id="claude-code"))
        self.assertEqual(self.attempt_path().read_bytes(), before)
        self.expect("bind", "BOUND", options=self.options)

    def test_failed_bind_before_safe_admission_does_not_write_attempt(self):
        self.init()
        for invalid in ({"owner_id": "foreign-owner"}, {"host_id": ""},
                        {"repository_identity": str(self.root / "absent-repository")},
                        {"repository_identity": str(self.root)}):
            with self.subTest(invalid=tuple(invalid)):
                self.expect("bind", "UNAVAILABLE", options=dict(self.options, **invalid))
                self.assertFalse(self.attempt_path().exists())
                self.assertFalse(self.state_path().exists())
                self.assertFalse((self.store / "sessions").exists())

    def test_failed_rebind_and_cas_do_not_poison_complete_pair(self):
        self.bind()
        paths = (self.state_path(), core.session_index_path(self.store, "session-a"), self.attempt_path())
        before = {path: path.read_bytes() if path.exists() else None for path in paths}
        for invalid in ({"controller_id": "", "expected_generation": "G0001"},
                        {"expected_generation": "G0002"}):
            self.expect("rebind", "UNAVAILABLE", options=dict(self.options, reason="failed-rebind", **invalid))
        self.expect("validate-event", "UNAVAILABLE", options=self.event_options("G0002"))
        self.assertEqual({path: path.read_bytes() if path.exists() else None for path in paths}, before)
        self.assertEqual(self.expect("lookup", "BOUND", options=self.lookup_options())["binding"]["binding_generation"],
                         "G0001")

    def test_legacy_complete_pair_without_attempt_marker_remains_valid(self):
        self.bind()
        if self.attempt_path().exists():
            self.attempt_path().unlink()
        self.expect("lookup", "BOUND", options=self.lookup_options())
        self.expect("rebind", "BOUND", options=dict(self.options, expected_generation="G0001", reason="legacy-pair"))
        self.assertFalse(self.attempt_path().exists())

    def test_malformed_or_foreign_attempt_is_not_recreated(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=dict(self.options, activation_receipt=""))
        path = self.attempt_path()
        self.assertTrue(path.exists(), "missing admitted attempt marker")
        original = json.loads(path.read_bytes())
        for field, value in (("owner_id", "foreign-owner"), ("host_id", "claude-code"),
                             ("host_session_id", "foreign-session"), ("host_id", []), ("schema", None)):
            with self.subTest(field=field, value=value):
                payload = dict(original, **{field: value})
                path.write_text(json.dumps(payload))
                before = path.read_bytes()
                self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())
                self.expect("bind", "UNAVAILABLE", options=self.options)
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse(self.state_path().exists())

    def test_interrupted_attempt_completion_remains_unavailable_and_allows_exact_retry(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=self.options, fault="after-attempt-create")
        self.assertTrue(self.attempt_path().exists())
        self.assertFalse(self.state_path().exists())
        self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())
        self.expect("bind", "BOUND", options=self.options)

    def test_partial_attempt_creation_is_not_replaced(self):
        self.init()
        self.expect("bind", "UNAVAILABLE", options=self.options, fault="attempt-partial-create")
        self.assertEqual(self.attempt_path().read_bytes(), b"{")
        self.expect("lookup", "UNAVAILABLE", options=self.lookup_options())
        self.expect("bind", "UNAVAILABLE", options=self.options)
        self.assertEqual(self.attempt_path().read_bytes(), b"{")
        self.assertFalse(self.state_path().exists())

    def test_malformed_proximal_typed_fields_are_structured_unavailable(self):
        self.bind()
        authority = {key: "NONE" for key in (
            "closure", "done", "lifecycle_credit", "merge", "package", "publication", "release")}
        for malformed in ("authority", "qualification", "mode-list", "mode-object"):
            with self.subTest(field=malformed):
                selection = {
                    "schema": "implementaudit.proximal-action-selection.v1", "decision_sha256": "0" * 64,
                    "applicable": True, "decision": "PROXIMAL_CLASSIFICATION_SATISFIED",
                    "applicability_reason": "source-fixture", "advance_allowed": True,
                    "currentness": {"receipt": "continuity-receipt-1", "current": True},
                    "qualification": {"authority": dict(authority)}, "authority": dict(authority),
                    "request_sha256": "1" * 64, "projection_digest": "2" * 64,
                    "mode": "NEXT_ACTION", "reason": "bounded fixture", "lanes": ["fixture"],
                }
                if malformed == "authority":
                    selection["authority"]["closure"] = []
                elif malformed == "qualification":
                    selection["qualification"]["authority"]["done"] = {}
                else:
                    selection["mode"] = [] if malformed == "mode-list" else {}
                canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                selection["digest"] = hashlib.sha256(canonical(selection).encode("utf-8")).hexdigest()
                self.expect("consume-proximal-action", "UNAVAILABLE",
                            options=dict(self.event_options(), turn_id="turn-1"), raw_input=canonical(selection))

    def test_lineage_checks_and_sparse_gc_history(self):
        self.bind()
        for number in (2, 3):
            options = dict(self.options, expected_generation=f"G{number - 1:04X}", reason="continuity-owner-update",
                           continuity_generation=f"G{number:04X}", continuity_receipt=f"continuity-receipt-{number}")
            self.expect("rebind", "BOUND", options=options)
        event = dict(self.event_options("G0003"), continuity_generation="G0003", continuity_receipt="continuity-receipt-3")
        valid = [item for number in (1, 2, 3) for item in
                 ("--expected-lineage-link", f"G{number:04X}", f"G{number:04X}", f"continuity-receipt-{number}")]
        self.expect("validate-event", "ATTRIBUTED", options=event, extra=valid)
        wrong_receipt = valid.copy()
        wrong_receipt[3] = "foreign-receipt"
        for links in (wrong_receipt, valid[:4] + valid[8:], valid[:8]):
            self.expect("validate-event", "UNAVAILABLE", options=event, extra=links)
        gc = {"owner_id": "fixture-owner", "host_id": "codex", "host_session_id": "session-a",
              "expected_generation": "G0003", "retain_generations": 1,
              "resolved_generation": "G0002", "resolution_receipt": "opaque-closure-owner-receipt"}
        self.expect("gc", "GC_COMPLETE", options=gc)
        self.assertEqual([record["binding_generation"] for record in json.loads(self.state_path().read_text())["records"]],
                         ["G0001", "G0003"])
        self.expect("lookup", "BOUND", options=self.lookup_options())
        self.expect("validate-event", "UNAVAILABLE", options=event, extra=valid)
        self.expect("gc", "GC_COMPLETE", options=gc)

    def test_tombstone_and_gc_preserve_governed_evidence(self):
        self.bind()
        sentinel = self.run / "evidence-preserve.txt"
        sentinel.write_bytes(b"unresolved governed evidence\n")
        digest = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        result = self.expect("tombstone", "TOMBSTONED", options={
            "owner_id": "fixture-owner", "host_id": "codex", "host_session_id": "session-a",
            "expected_generation": "G0001", "reason": "session-end"})
        self.assertFalse(result["object_closed"])
        self.expect("gc", "UNAVAILABLE", options={
            "owner_id": "fixture-owner", "host_id": "codex", "host_session_id": "session-a",
            "expected_generation": "G0002", "retain_generations": 1})
        self.assertEqual(hashlib.sha256(sentinel.read_bytes()).hexdigest(), digest)

    def test_ordinary_unbound_path_does_not_scan_or_create(self):
        output = io.StringIO()
        with mock.patch.object(os, "scandir", side_effect=AssertionError("ordinary unbound scan")), \
                contextlib.redirect_stdout(output):
            core.command_lookup(argparse.Namespace(store=str(self.store), **self.lookup_options()))
        self.assertEqual(json.loads(output.getvalue())["status"], "UNBOUND")
        self.assertFalse(self.store.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
