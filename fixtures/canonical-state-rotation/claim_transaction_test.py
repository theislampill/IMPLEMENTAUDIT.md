#!/usr/bin/env python3
"""Focused real-Git controls for the original claim-owned rotation lane.

The initial reader controls deliberately run against main until postimages exist.
Projection-helper integration is added after its owner API is available.
"""
from __future__ import annotations

import hashlib
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[2]
POST = BASE / "skills/implementaudit/scripts"
EVIDENCE = Path(os.environ.get("R0039_CLAIM_EVIDENCE_DIR") or tempfile.mkdtemp(prefix="claim-evidence-")).absolute()
EVIDENCE.mkdir(parents=True, exist_ok=True)
CONTROLLER = "transaction-test"


def run(argv, *, cwd, input_bytes=None):
    environment = dict(os.environ)
    for key in list(environment):
        if key.startswith("GIT_") or key.startswith("IMPLEMENTAUDIT_"):
            environment.pop(key)
    environment.update({"LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"})
    return subprocess.run([str(item) for item in argv], cwd=cwd, input=input_bytes,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=environment, timeout=30, check=False)


class Fixture:
    def __init__(self, *, seed_receipt=True, persistent_repo=None):
        self.directory = None if persistent_repo is not None else tempfile.TemporaryDirectory(prefix="case-", dir=EVIDENCE)
        self.repo = Path(persistent_repo) if persistent_repo is not None else Path(self.directory.name)
        if persistent_repo is not None:
            self.repo.mkdir(parents=True, exist_ok=False)
        self.scripts = self.repo / "skills/implementaudit/scripts"
        self.scripts.mkdir(parents=True)
        for name in ("claim-run.sh", "claim-run-rotation.py", "validate-run-root.sh",
                     "rotate-canonical-state.py", "canonical_hot_projection.py"):
            chosen = POST / name if (POST / name).is_file() else BASE / "skills/implementaudit/scripts" / name
            if chosen.is_file():
                shutil.copyfile(chosen, self.scripts / name)
        self.git("init", "-q")
        self.git("config", "user.name", "claim transaction fixture")
        self.git("config", "user.email", "claim-transaction@example.invalid")
        (self.repo / "product.txt").write_text("immutable fixture baseline\n")
        self.git("add", "product.txt")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "fixture baseline")
        claimed = self.claim("--controller", CONTROLLER, "reader transaction")
        if claimed.returncode:
            raise RuntimeError(claimed.stderr.decode())
        self.run_root = self.repo / claimed.stdout.decode().strip()
        for name in ("STATE.md", "ROADMAP.md", "PROTOCOL.md", "THINKING.md", "sidecars.md", "tools.md", "context.md"):
            (self.run_root / name).write_text(name + " fixture\n")
        self.head = self.git("rev-parse", "HEAD")
        self.tree = self.git("rev-parse", "HEAD^{tree}")
        if not seed_receipt:
            return
        self.write_state("G0001", "new-session")
        receipt = self.claim("--resume-controller", CONTROLLER, "--boundary", "new-session", "--epoch", "G0001")
        if receipt.returncode:
            raise RuntimeError(receipt.stderr.decode())
        self.receipt = receipt.stdout.decode().strip()

    def close(self):
        if self.directory is not None:
            self.directory.cleanup()

    def claim(self, *args):
        return run(["bash", self.scripts / "claim-run.sh", *args], cwd=self.repo)

    def git(self, *args, input_bytes=None):
        result = run(["git", *args], cwd=self.repo, input_bytes=input_bytes)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return result.stdout.decode().strip()

    def blob(self, data):
        return self.git("hash-object", "-w", "--stdin", input_bytes=data)

    def write_state(self, epoch, boundary):
        (self.run_root / "STATE.md").write_text(
            "# STATE\n\n| Next action | continue exact action |\n"
            + "Current epoch: " + epoch + "\n"
            + f"| {epoch} | {boundary} | fixture | repo at `{self.head}` / `{self.tree}` | yes | fixture |\n")

    def malformed_marker(self):
        self.git("update-ref", f"refs/implementaudit/current-generation-migrations/{CONTROLLER}",
                 self.blob(b"malformed marker\n"))


class ReaderControls(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.close)

    def test_legacy_v2_currentness_is_preserved(self):
        result = self.fixture.claim("--require-current-continuity", CONTROLLER)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout.decode().strip(), self.fixture.receipt)

    def test_a_marker_without_pointer_cannot_fall_back_to_root_v2(self):
        self.fixture.malformed_marker()
        result = self.fixture.claim("--require-current-continuity", CONTROLLER)
        self.assertNotEqual(result.returncode, 0, "retired root-v2 fallback was accepted")

    def test_verify_cannot_accept_old_v2_after_a_marker_appears(self):
        self.fixture.malformed_marker()
        result = self.fixture.claim("--verify-resume-receipt", self.fixture.receipt)
        self.assertNotEqual(result.returncode, 0, "old v2 verification bypassed migrated authority")

    def test_resume_cannot_mint_v2_around_a_broken_migrated_route(self):
        self.fixture.malformed_marker()
        self.fixture.write_state("G0002", "new-session")
        result = self.fixture.claim("--resume-controller", CONTROLLER, "--boundary", "new-session", "--epoch", "G0002")
        self.assertNotEqual(result.returncode, 0, "resume minted v2 around migrated custody")
        receipt_ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0002"
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname)", receipt_ref), "")

    def test_second_genuine_boundary_is_admitted_while_receipt_is_stale(self):
        first = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "physical-one")
        second = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "host-reported-compaction", "--event", "physical-two")
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        self.assertEqual(second.returncode, 0, second.stderr.decode())
        self.assertNotEqual(first.stdout, second.stdout)
        stale = self.fixture.claim("--require-current-continuity", CONTROLLER)
        self.assertNotEqual(stale.returncode, 0)

    def test_separate_legacy_state_read_returns_exact_bytes(self):
        expected = (self.fixture.run_root / "STATE.md").read_bytes()
        result = self.fixture.claim("--read-current-state", CONTROLLER, "STATE", "--expected-pointer", "none")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout, expected, "reader returned anything other than the verified STATE bytes")


class FixtureProjection:
    """Temporary pure-boundary substitute; never mints currentness or receipts.

    This isolates real claim-owner Git transactions while the projection owner's
    implementation is concurrent. It is not projection/equivalence evidence.
    """
    def __init__(self, fixture):
        self.fixture = fixture
        self.fail_after_pointer = False
        self.crash_after_pointer = False
        self.preempt_during_finalization = False

    @staticmethod
    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

    def prepare_canonical_draft(self, repo, run_root, controller, generation, owner_map_path, predecessor, calibration):
        if not calibration.get("trigger", True):
            return {"triggered": False}
        state = Path(predecessor["state_path"]).read_bytes()
        road = Path(predecessor["roadmap_path"]).read_bytes()
        archive = {"schema": "implementaudit.state-archive.v1", "controller": controller,
                   "state": state.hex(), "roadmap": road.hex()}
        raw = self.canonical(archive) + b"\n"
        oid = self.fixture.blob(raw)
        ref = f"refs/implementaudit/state-archives/{controller}/{generation}"
        self.fixture.git("update-ref", ref, oid, "0" * 40)
        return {"triggered": True, "archive_ref": ref,
                "archive_manifest_oid": oid, "archive_manifest_sha256": hashlib.sha256(raw).hexdigest(),
                "source_state_sha256": hashlib.sha256(state).hexdigest(),
                "source_roadmap_sha256": hashlib.sha256(road).hexdigest(),
                "exact_next_action": predecessor["exact_next_action"], "generation_id": generation,
                "predecessor": predecessor}

    def verify_canonical_archive(self, repo, controller, archive_ref, expected_sha256):
        oid = self.fixture.git("rev-parse", archive_ref)
        raw = run(["git", "cat-file", "blob", oid], cwd=repo).stdout
        if hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise RuntimeError("fixture archive corruption")
        return json.loads(raw)

    def archive_retention_guards(self, repo, controller, archive_ref, expected_sha256):
        self.verify_canonical_archive(repo, controller, archive_ref, expected_sha256)
        return {archive_ref: self.fixture.git("rev-parse", archive_ref)}

    def finalize_canonical_projection(self, repo, run_root, prepared, transition):
        archive = self.verify_canonical_archive(repo, transition["controller"], prepared["archive_ref"], prepared["archive_manifest_sha256"])
        state = bytes.fromhex(archive["state"])
        old_epoch = prepared["predecessor"]["continuity_epoch"].encode()
        state = state.replace(b"Current epoch: " + old_epoch, b"Current epoch: " + transition["continuity_epoch"].encode())
        state += (f"| {transition['continuity_epoch']} | canonical-state-rotation | fixture | "
                  f"repo at `{transition['head']}` / `{transition['tree']}` | yes | fixture successor |\n").encode()
        road = bytes.fromhex(archive["roadmap"])
        generation = Path(run_root) / "state-generations" / transition["projection_generation_id"]
        generation.mkdir(parents=True)
        (generation / "STATE.md").write_bytes(state)
        (generation / "ROADMAP.md").write_bytes(road)
        protected = {"schema": "implementaudit.protected-projection.v2",
                     "state_sha256": hashlib.sha256(state).hexdigest(),
                     "roadmap_sha256": hashlib.sha256(road).hexdigest(),
                     "payload_source": transition["payload_source"]}
        protected_raw = self.canonical(protected) + b"\n"
        (generation / "protected-state.json").write_bytes(protected_raw)
        archive_raw = self.canonical(archive) + b"\n"
        (generation / "archive-manifest.json").write_bytes(archive_raw)
        pointer = {key: transition[key] for key in ("controller", "claim_id", "run_root_identity",
                   "projection_generation_id", "continuity_epoch", "invalidation_oid",
                   "predecessor_receipt_ref_oid", "expected_receipt_ref_schema")}
        pointer.update({"schema": "implementaudit.current-generation.v1",
                        "projection_schema": "implementaudit.protected-projection.v2",
                        "state_sha256": hashlib.sha256(state).hexdigest(),
                        "roadmap_sha256": hashlib.sha256(road).hexdigest(),
                        "protected_manifest_sha256": hashlib.sha256(protected_raw).hexdigest(),
                        "archive_manifest_sha256": hashlib.sha256(archive_raw).hexdigest(),
                        "exact_next_action": prepared["exact_next_action"]})
        if self.preempt_during_finalization:
            self.preempt_during_finalization = False
            result = self.fixture.claim("--invalidate-continuity", CONTROLLER,
                                        "--boundary", "host-reported-compaction", "--event", "newer-native-boundary")
            if result.returncode:
                raise RuntimeError(result.stderr.decode())
        return {"pointer": pointer, "generation_dir": generation}

    def read_canonical_generation(self, repo, run_root, pointer):
        ref = f"refs/implementaudit/current-generations/{pointer['controller']}"
        current = self.fixture.git("for-each-ref", "--format=%(objectname)", ref)
        candidate = self.fixture.git("hash-object", "--stdin", input_bytes=self.canonical(pointer))
        if current == candidate and self.fail_after_pointer:
            self.fail_after_pointer = False
            raise RuntimeError("injected exact post-pointer readback failure")
        if current == candidate and self.crash_after_pointer:
            self.crash_after_pointer = False
            raise KeyboardInterrupt("injected process interruption after pointer CAS")
        generation = Path(run_root) / "state-generations" / pointer["projection_generation_id"]
        state = (generation / "STATE.md").read_bytes()
        road = (generation / "ROADMAP.md").read_bytes()
        protected = (generation / "protected-state.json").read_bytes()
        archive = (generation / "archive-manifest.json").read_bytes()
        for key, raw in (("state_sha256", state), ("roadmap_sha256", road),
                         ("protected_manifest_sha256", protected), ("archive_manifest_sha256", archive)):
            if hashlib.sha256(raw).hexdigest() != pointer[key]:
                raise RuntimeError("fixture generation corruption: " + key)
        return {"state_bytes": state, "roadmap_bytes": road,
                "protected_manifest": json.loads(protected), "archive_manifest": json.loads(archive),
                "state_path": generation / "STATE.md", "roadmap_path": generation / "ROADMAP.md"}


class TransactionControls(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.close)
        spec = importlib.util.spec_from_file_location("claim_owner_" + self.fixture.repo.name.replace("-", "_"),
                                                     self.fixture.scripts / "claim-run-rotation.py")
        self.owner = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.owner
        spec.loader.exec_module(self.owner)
        self.addCleanup(sys.modules.pop, spec.name, None)
        self.projection = FixtureProjection(self.fixture)
        self.patch = mock.patch.object(self.owner, "projection_helper", return_value=self.projection, create=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.directory = contextlib.chdir(self.fixture.repo)
        self.directory.__enter__()
        self.addCleanup(self.directory.__exit__, None, None, None)
        self.context = self.owner.discover(CONTROLLER)
        self.owner_map = self.fixture.run_root / "owner-map.json"
        self.owner_map.write_text("{}")

    def rotate(self, calibration=None):
        self.assertTrue(callable(getattr(self.owner, "run_canonical_rotation_v1", None)),
                        "the claim owner has no canonical transaction")
        return self.owner.run_canonical_rotation_v1(self.context, self.owner_map, calibration or {"trigger": True})

    def test_first_migration_mints_real_v3_and_a_permanent_marker(self):
        result = self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(result["receipt_token"], joined["receipt_token"])
        self.assertIn(b"implementaudit.continuity-receipt.v3\t", self.owner.read_blob(self.fixture.repo, joined["receipt_token"].split("@")[1]))
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0002")
        self.assertTrue(joined["marker_oid"])

    def test_second_rotation_preserves_first_migration_marker(self):
        first = self.rotate()
        marker = self.fixture.git("rev-parse", self.context["marker_ref"])
        second = self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(marker, self.fixture.git("rev-parse", self.context["marker_ref"]))
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")
        self.assertNotEqual(first["receipt_token"], second["receipt_token"])

    def test_below_threshold_keeps_all_authority_refs_unchanged(self):
        before = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)")
        result = self.rotate({"trigger": False})
        self.assertEqual(result["status"], "NOT_TRIGGERED")
        self.assertEqual(before, self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)"))

    def test_post_pointer_failure_recovers_with_a_fresh_epoch_without_fake_intermediate_receipt(self):
        self.projection.fail_after_pointer = True
        result = self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")
        self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], self.fixture.receipt)
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname)",
                                         f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0002"), "")
        self.assertTrue(self.fixture.git("rev-parse", f"refs/implementaudit/state-archives/{CONTROLLER}/epochs/G0002"))

    def test_newer_boundary_preempts_finalization_and_is_never_compensated_over(self):
        self.projection.preempt_during_finalization = True
        with self.assertRaises(self.owner.RotationError):
            self.rotate()
        raw = self.owner.read_blob(self.fixture.repo, self.fixture.git("rev-parse", self.context["invalidation_ref"]))
        self.assertIn(b"host-reported-compaction\tnewer-native-boundary", raw)
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname)", self.context["pointer_ref"]), "")

    def test_process_interruption_recovers_from_the_retained_epoch_descriptor(self):
        self.projection.crash_after_pointer = True
        with self.assertRaises(KeyboardInterrupt):
            self.rotate()
        self.assertTrue(callable(getattr(self.owner, "recover_rotation_v1", None)))
        recovered = self.owner.recover_rotation_v1(self.context)
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(recovered["status"], "RECOVERED_PRIOR")
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")

    def test_marker_failure_uses_the_actual_failed_v3_receipt_as_predecessor(self):
        original = self.owner.update_refs
        armed = True
        def fail_marker(context, updates, guards, **kwargs):
            nonlocal armed
            if context["marker_ref"] in updates and armed:
                armed = False
                raise self.owner.CASFailure("injected marker CAS refusal")
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=fail_marker):
            result = self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        failed_ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0002"
        failed_token = failed_ref + "@" + self.fixture.git("rev-parse", failed_ref)
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], failed_token)
        self.assertTrue((self.fixture.run_root / "state-generations/G0002/STATE.md").is_file())
        record, _ = self.owner.read_epoch(self.context, "G0003")
        self.assertEqual(record["transition"]["failed_transition_receipt_ref_oid"], failed_token)

    def test_marker_that_landed_before_readback_failure_remains_permanent(self):
        original = self.owner.require_current_generation_join_v1
        armed = True
        def fail_join(context):
            nonlocal armed
            observed = self.owner.authorities(context)
            if observed["marker"] is not None and armed:
                armed = False
                raise self.owner.RotationError("injected post-marker readback refusal")
            return original(context)
        with mock.patch.object(self.owner, "require_current_generation_join_v1", side_effect=fail_join):
            result = self.rotate()
        joined = original(self.context)
        marker = self.owner.tsv(self.owner.read_blob(self.fixture.repo, joined["marker_oid"]), 10, terminal_lf=False)
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        self.assertEqual(marker[4], "G0002")
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")

    def test_pointer_cas_loses_with_exact_old_intact_then_recovers_a_fresh_epoch(self):
        original = self.owner.update_refs
        armed = True
        def fail_pointer(context, updates, guards, **kwargs):
            nonlocal armed
            if context["pointer_ref"] in updates and armed:
                armed = False
                raise self.owner.CASFailure("injected expected-old CAS failure with old intact")
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=fail_pointer):
            result = self.rotate()
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        self.assertEqual(result["continuity_epoch"], "G0003")
        failed, failed_oid = self.owner.read_epoch(self.context, "G0002")
        intent, _ = self.owner.read_publication(self.context, failed, failed_oid)
        self.owner.require_anchor(self.context, intent["pointer_oid"])

    def test_a_distinct_complete_winner_is_verified_without_competing_recovery(self):
        original = self.owner.update_refs
        armed = True
        winner = {}
        def another_owner_completes_recovery(context, updates, guards, **kwargs):
            nonlocal armed
            if context["pointer_ref"] in updates and armed:
                armed = False
                failed, failed_oid = self.owner.read_epoch(context, "G0002")
                winner.update(self.owner.recover_failed_epoch(context, failed, failed_oid))
                raise self.owner.CASFailure("injected CAS loss to a completed winner")
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=another_owner_completes_recovery):
            result = self.rotate()
        self.assertEqual(result["status"], "VERIFIED_WINNER")
        self.assertEqual(result["receipt_token"], winner["receipt_token"])
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname)",
                                         f"refs/implementaudit/state-archives/{CONTROLLER}/epochs/G0004"), "")

    def test_same_epoch_pointer_substitution_is_not_compensated_as_our_pointer(self):
        original = self.owner.update_refs
        armed = True
        substituted = []
        def substitute_pointer(context, updates, guards, **kwargs):
            nonlocal armed
            if context["pointer_ref"] in updates and armed:
                armed = False
                oid = updates[context["pointer_ref"]][0]
                pointer = self.owner.decode_json(self.owner.read_blob(self.fixture.repo, oid))
                pointer["exact_next_action"] = "substituted continuation"
                new = self.owner.write_blob(context, self.owner.canonical(pointer))
                self.fixture.git("update-ref", context["pointer_ref"], new, "0" * 40)
                substituted.append(new)
                raise self.owner.CASFailure("same epoch but distinct pointer")
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=substitute_pointer):
            with self.assertRaises(self.owner.RotationError):
                self.rotate()
        self.assertEqual(self.fixture.git("rev-parse", self.context["pointer_ref"]), substituted[0])
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname)",
                                         f"refs/implementaudit/state-archives/{CONTROLLER}/epochs/G0003"), "")

    def test_migrated_native_boundaries_can_preempt_stale_receipts_repeatedly(self):
        self.rotate()
        first = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "one")
        second = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "host-reported-compaction", "--event", "two")
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        self.assertEqual(second.returncode, 0, second.stderr.decode())
        self.assertNotEqual(first.stdout, second.stdout)
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_git_gc_preserves_first_marker_pointer_receipts_and_allocations(self):
        first = self.rotate()
        second = self.rotate()
        third = self.rotate()
        refs = self.fixture.git("for-each-ref", "--format=%(objectname)", "refs/implementaudit/").splitlines()
        self.fixture.git("reflog", "expire", "--expire=now", "--all")
        self.fixture.git("gc", "--prune=now")
        for oid in refs:
            self.owner.read_blob(self.fixture.repo, oid)
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined["receipt_token"], third["receipt_token"])
        self.assertNotEqual(first["receipt_token"], second["receipt_token"])

    def test_hardlinked_current_pointer_ref_is_refused(self):
        self.rotate()
        ref_path = self.owner.ref_path(self.fixture.repo, self.context["pointer_ref"])
        os.link(ref_path, self.fixture.repo / "hardlinked-pointer-ref")
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_publication_intent_is_required_even_when_pointer_envelope_matches(self):
        self.rotate()
        ref = self.owner.publication_ref(self.context, "G0002")
        self.fixture.git("update-ref", "-d", ref)
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_retained_source_write_restore_cannot_cross_the_f5_gate(self):
        original = self.projection.prepare_canonical_draft
        path = self.fixture.run_root / "STATE.md"
        saved = path.read_bytes()
        times = path.stat()
        def write_restore(*args):
            prepared = original(*args)
            path.write_bytes(saved + b"transient mutation\n")
            path.write_bytes(saved)
            os.utime(path, ns=(times.st_atime_ns, times.st_mtime_ns))
            return prepared
        with mock.patch.object(self.projection, "prepare_canonical_draft", side_effect=write_restore):
            with self.assertRaises(self.owner.RotationError):
                self.rotate()
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.context["invalidation_ref"]))
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, "G0002")))
        self.assertEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).stdout.decode().strip(), self.fixture.receipt)

    def test_exact_landed_readback_classifies_a_failed_git_exit_without_false_rollback(self):
        original = self.owner.git_process
        armed = True
        def report_failed_exit(repo, *args, input_bytes=None):
            nonlocal armed
            result = original(repo, *args, input_bytes=input_bytes)
            if (armed and args[:1] == ("update-ref",) and input_bytes
                    and b"update " + self.context["pointer_ref"].encode() + b"\0" in input_bytes):
                armed = False
                return subprocess.CompletedProcess(result.args, 1, result.stdout, b"injected post-effect transport exit")
            return result
        with mock.patch.object(self.owner, "git_process", side_effect=report_failed_exit):
            result = self.rotate()
        self.assertFalse(armed)
        self.assertEqual(result["status"], "ROTATED")
        self.assertEqual(result["continuity_epoch"], "G0002")

    @unittest.skipIf(os.name == "nt", "POSIX process-death evidence; native Windows execution remains separate")
    def test_process_death_releases_the_os_rotation_lease_without_deleting_evidence(self):
        code = ("import importlib.util, pathlib, sys; sys.dont_write_bytecode=True; "
                "p=pathlib.Path(sys.argv[1]); s=importlib.util.spec_from_file_location('owner',p); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "c=m.discover(sys.argv[2]); lock=m.rotation_lease(c); lock.__enter__(); "
                "print('lease-held',flush=True); sys.stdin.buffer.read(1)")
        child = subprocess.Popen([sys.executable, "-I", "-B", "-c", code,
                                  str(self.fixture.scripts / "claim-run-rotation.py"), CONTROLLER],
                                 cwd=self.fixture.repo, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def stop():
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=10)
        self.addCleanup(stop)
        self.assertEqual(child.stdout.readline(), b"lease-held\n")
        with self.assertRaises(self.owner.RotationError):
            with self.owner.rotation_lease(self.context):
                pass
        child.kill()
        child.wait(timeout=10)
        with self.owner.rotation_lease(self.context):
            pass
        lease = self.fixture.repo / ".git/implementaudit-r0039-rotation.gate"
        self.assertEqual(lease.read_bytes(), b"\0")
        self.assertEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).stdout.decode().strip(), self.fixture.receipt)

    def test_symbolic_pointer_ref_is_never_read_as_current_authority(self):
        self.rotate()
        self.fixture.git("symbolic-ref", self.context["pointer_ref"], self.context["controller_ref"])
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_parent_switch_never_reads_the_outside_file(self):
        parent = self.fixture.repo / "pinned-source"
        outside = self.fixture.repo / "outside-source"
        parent.mkdir(); outside.mkdir()
        (parent / "value").write_bytes(b"owned bytes")
        target = outside / "value"
        target.write_bytes(b"outside bytes must not be opened")
        victim = target.stat()
        original_verify = self.owner.DirectoryPin.verify
        original_read = os.read
        armed = True
        outside_reads = []
        def switch_after_pin(pin):
            nonlocal armed
            original_verify(pin)
            if armed and pin.path == parent and len(pin.nodes) == len(parent.parts):
                armed = False
                parent.rename(self.fixture.repo / "pinned-source-saved")
                parent.symlink_to(outside, target_is_directory=True)
        def observe_read(fd, size):
            current = os.fstat(fd)
            if (current.st_dev, current.st_ino) == (victim.st_dev, victim.st_ino):
                outside_reads.append(fd)
            return original_read(fd, size)
        with mock.patch.object(self.owner.DirectoryPin, "verify", new=switch_after_pin), mock.patch.object(os, "read", new=observe_read):
            with self.assertRaises((self.owner.CustodyError, OSError)):
                self.owner.read_regular(parent / "value")
        self.assertFalse(armed, "race point did not execute")
        self.assertEqual(outside_reads, [], "the read crossed into an unowned outside inode")

    def test_parent_switch_never_creates_a_gate_in_the_outside_directory(self):
        parent = self.fixture.repo / "pinned-gate"
        outside = self.fixture.repo / "outside-gate"
        parent.mkdir(); outside.mkdir()
        original_verify = self.owner.DirectoryPin.verify
        armed = True
        def switch_after_pin(pin):
            nonlocal armed
            original_verify(pin)
            if armed and pin.path == parent and len(pin.nodes) == len(parent.parts):
                armed = False
                parent.rename(self.fixture.repo / "pinned-gate-saved")
                parent.symlink_to(outside, target_is_directory=True)
        with mock.patch.object(self.owner.DirectoryPin, "verify", new=switch_after_pin):
            with self.assertRaises((self.owner.CustodyError, OSError)):
                with self.owner.native_lock(parent / "namespace.gate", blocking=False):
                    self.fail("redirected namespace gate was admitted")
        self.assertFalse(armed, "race point did not execute")
        self.assertFalse((outside / "namespace.gate").exists(), "the gate write escaped through a replaced parent")


class RealHelperIntegration(unittest.TestCase):
    """Real main receipt, claim-owned ref writes, source-pinned pure/helper APIs."""
    def setUp(self):
        self.fixture = Fixture(seed_receipt=False, persistent_repo=getattr(self, "persistent_repo", None))
        self.addCleanup(self.fixture.close)
        spec = importlib.util.spec_from_file_location("real_claim_" + self.fixture.repo.name.replace("-", "_"),
                                                     self.fixture.scripts / "claim-run-rotation.py")
        self.owner = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.owner
        spec.loader.exec_module(self.owner)
        self.addCleanup(sys.modules.pop, spec.name, None)
        self.directory = contextlib.chdir(self.fixture.repo)
        self.directory.__enter__()
        self.addCleanup(self.directory.__exit__, None, None, None)
        self.context = self.owner.discover(CONTROLLER)
        factory_path = BASE / "fixtures/canonical-state-rotation/protected_projection_v2_test.py"
        factory_spec = importlib.util.spec_from_file_location("typed_fixture_factory", factory_path)
        self.factory = importlib.util.module_from_spec(factory_spec)
        factory_spec.loader.exec_module(self.factory)
        source = json.loads((factory_path.parent / "v2/source.json").read_text())
        bodies = source["bodies"]
        identity = bodies["STATE"]["payload"]["identity"]["value"]
        identity.update({"controller_id": CONTROLLER, "claim_id": self.context["claim_id"],
                         "run_root_identity": self.context["run_root_identity"],
                         "candidate": self.fixture.head, "tree": self.fixture.tree})
        rref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0001"
        for role in ("STATE", "ROADMAP"):
            bodies[role]["continuity"].update({"boundary": "new-session", "invalidation_oid": None,
                                                "expected_receipt_ref": rref})
            for item in bodies[role]["artifact_refs"]:
                if item["role"] == "CONTINUITY_RECEIPT":
                    item["locator"] = rref
        bodies["STATE"]["history"][0]["payload"]["text"] += " Historical exact observation." * 6500
        raw = self.factory.render_pair(bodies)
        self.original_pair = raw
        for role in ("STATE", "ROADMAP"):
            (self.fixture.run_root / (role + ".md")).write_bytes(raw[role])
        minted = self.fixture.claim("--resume-controller", CONTROLLER, "--boundary", "new-session", "--epoch", "G0001")
        self.assertEqual(minted.returncode, 0, minted.stderr.decode())
        self.fixture.receipt = minted.stdout.decode().strip()
        self.assertEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).stdout, minted.stdout)
        artifacts = {key: text.encode() for key, text in source["artifact_texts"].items()}
        artifacts["receipt"] = self.owner.read_blob(self.fixture.repo, self.fixture.receipt.split("@")[1])
        for role in ("STATE", "ROADMAP"):
            for item in bodies[role]["artifact_refs"]:
                if item["role"] != "CONTINUITY_RECEIPT":
                    path = self.fixture.run_root / item["locator"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(artifacts[item["artifact_id"]])
        rows = self.factory.build_owner_map(bodies, raw, artifacts)
        self.owner_map = self.fixture.run_root / "owner-map.json"
        self.owner_map.write_bytes(self.owner.canonical({"schema": "implementaudit.rotation-owner-map.v2", "owner_map": rows}))
        self.helper = self.owner.projection_helper()

    def rotate(self):
        return self.owner.run_canonical_rotation_v1(self.context, self.owner_map, self.helper.calibration_contract_v1())

    def test_real_helper_migrates_real_main_receipt_and_separate_readers(self):
        result = self.rotate()
        self.assertEqual(result["status"], "ROTATED")
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined["receipt_token"], result["receipt_token"])
        for role in ("STATE", "ROADMAP"):
            read = self.fixture.claim("--read-canonical-state", CONTROLLER, "--role", role,
                                      "--expected-pointer", result["pointer_token"])
            self.assertEqual(read.returncode, 0, read.stderr.decode())
            self.assertEqual(read.stdout, joined[role.lower() + "_bytes"])
            self.assertEqual((self.fixture.run_root / (role + ".md")).read_bytes(), self.original_pair[role])
        resolved = self.fixture.claim("--resolve-canonical-generation", CONTROLLER)
        self.assertEqual(resolved.returncode, 0, resolved.stderr.decode())
        self.assertEqual(json.loads(resolved.stdout)["receipt_token"], result["receipt_token"])
        self.assertEqual(self.rotate()["status"], "NOT_TRIGGERED")

    def test_real_helper_recovers_a_failed_epoch_without_a_fake_receipt(self):
        original = self.helper.read_canonical_generation
        armed = True
        def fail_once(repo, run_root, pointer):
            nonlocal armed
            current = self.owner.read_ref(repo, self.context["pointer_ref"])
            oid = self.owner.write_blob(self.context, self.owner.canonical(pointer))
            if current == oid and armed:
                armed = False
                raise RuntimeError("injected real helper post-CAS readback failure")
            return original(repo, run_root, pointer)
        with mock.patch.object(self.helper, "read_canonical_generation", side_effect=fail_once):
            result = self.rotate()
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], self.fixture.receipt)
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, "G0002")))

    def test_real_helper_retains_actual_failed_receipt_and_pair_on_marker_failure(self):
        original = self.owner.update_refs
        armed = True
        def fail_once(context, updates, guards, **kwargs):
            nonlocal armed
            if context["marker_ref"] in updates and armed:
                armed = False
                raise self.owner.CASFailure("injected real marker refusal")
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=fail_once):
            result = self.rotate()
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        joined = self.owner.require_current_generation_join_v1(self.context)
        failed_ref = self.owner.receipt_ref(self.context, "G0002")
        failed_oid = self.owner.read_ref(self.fixture.repo, failed_ref)
        self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], failed_ref + "@" + failed_oid)
        self.fixture.git("reflog", "expire", "--expire=now", "--all")
        self.fixture.git("gc", "--prune=now")
        again = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(again["receipt_token"], result["receipt_token"])


class CompleteOwnerDiscriminators(unittest.TestCase):
    """Finite #215 F3-F7 controls, all using the real paired projection helper.

    Deliberately malformed refs are constructed stimuli in disposable repositories.
    Process exits and Git lock contention exercise real effects; these controls do
    not impersonate a native host occurrence or an entitled adjudication decision.
    """
    setUp = RealHelperIntegration.setUp
    rotate = RealHelperIntegration.rotate

    def snapshot(self):
        refs = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
        files = {}
        for path in sorted(self.fixture.run_root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                raw = path.read_bytes()
                files[path.relative_to(self.fixture.run_root).as_posix()] = {
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "mode": oct(path.stat().st_mode & 0o777)}
        return {"refs": refs.splitlines(), "files": files}

    def evidence(self, name, record):
        record["source_identity"] = {
            path.name: {"bytes": len(path.read_bytes()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(self.fixture.scripts.glob("*")) if path.is_file()}
        if os.environ.get("R0039_CLAIM_RETAIN_ARTIFACTS") == "1":
            artifact = EVIDENCE / (name + ".fixture.zip")
            paths = []
            for directory in (self.fixture.repo / ".git/objects", self.fixture.repo / ".git/refs", self.fixture.run_root):
                paths.extend(path for path in directory.rglob("*") if path.is_file() and not path.is_symlink())
            paths.extend(path for path in (self.fixture.repo / ".git/HEAD", self.fixture.repo / ".git/config",
                                          self.fixture.repo / ".git/packed-refs") if path.is_file())
            with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(set(paths)):
                    archive.write(path, path.relative_to(self.fixture.repo).as_posix())
            with zipfile.ZipFile(artifact) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))
            raw = artifact.read_bytes()
            record["retained_fixture"] = {"name": artifact.name, "bytes": len(raw),
                                           "sha256": hashlib.sha256(raw).hexdigest(),
                                           "scope": "constructed Git objects/refs and run bytes; no native producer claim"}
        target = EVIDENCE / (name + ".json")
        target.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")

    def run_crash(self, stage):
        result = run([sys.executable, "-I", "-B", Path(__file__).resolve(), "--crash-driver",
                      self.fixture.scripts / "claim-run-rotation.py", CONTROLLER,
                      self.owner_map, stage], cwd=self.fixture.repo)
        self.assertEqual(result.returncode, 86, (stage, result.stdout.decode(), result.stderr.decode()))
        return result

    def test_complete_marker_pointer_receipt_currentness_table(self):
        self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        valid_pointer = joined["pointer_oid"]
        valid_marker = joined["marker_oid"]
        valid_invalidation = joined["pointer"]["invalidation_oid"]
        v2_ref, v2_oid = self.fixture.receipt.split("@")
        v3_ref, v3_oid = joined["receipt_token"].split("@")
        bad_v2 = self.owner.tsv(self.owner.read_blob(self.fixture.repo, v2_oid), 12)
        bad_v2[-1] = "substituted exact action"
        bad_v2_oid = self.fixture.blob(("\t".join(bad_v2) + "\n").encode())
        bad_v3 = self.owner.tsv(self.owner.read_blob(self.fixture.repo, v3_oid), 14)
        bad_v3[-2] = "substituted exact action"
        bad_v3_oid = self.fixture.blob(("\t".join(bad_v3) + "\n").encode())
        bad_marker = self.owner.tsv(self.owner.read_blob(self.fixture.repo, valid_marker), 10, terminal_lf=False)
        bad_marker[1] = "wrong-controller"
        bad_marker_oid = self.fixture.blob("\t".join(bad_marker).encode())
        bad_pointer = dict(joined["pointer"], schema="implementaudit.unknown-pointer.v1")
        bad_pointer_oid = self.fixture.blob(self.owner.canonical(bad_pointer))
        malformed = self.fixture.blob(b"malformed fixture authority\n")
        stale = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "matrix-later-physical-event")
        self.assertEqual(stale.returncode, 0, stale.stderr.decode())
        stale_invalidation = stale.stdout.decode().strip().split("@")[1]
        saved = {self.context["pointer_ref"]: valid_pointer, self.context["marker_ref"]: valid_marker,
                 self.context["invalidation_ref"]: valid_invalidation, v2_ref: v2_oid, v3_ref: v3_oid}
        def assign(ref, oid):
            if oid is None:
                self.fixture.git("update-ref", "-d", ref)
            else:
                self.fixture.git("update-ref", ref, oid)
        rows = []
        marker_states = {"absent": None, "valid": valid_marker, "malformed": malformed, "wrong-controller": bad_marker_oid}
        pointer_states = {"absent": None, "valid": valid_pointer, "malformed": malformed, "wrong-schema": bad_pointer_oid}
        receipt_states = ("absent", "exact-v2", "exact-v3", "stale", "mismatched")
        try:
            for marker_name, marker_oid in marker_states.items():
                for pointer_name, pointer_oid in pointer_states.items():
                    for receipt_name in receipt_states:
                        for ref, oid in saved.items():
                            assign(ref, oid)
                        assign(self.context["marker_ref"], marker_oid)
                        assign(self.context["pointer_ref"], pointer_oid)
                        legacy = marker_name == "absent" and pointer_name == "absent"
                        assign(self.context["invalidation_ref"], None if legacy else valid_invalidation)
                        if receipt_name == "absent":
                            assign(v2_ref, None); assign(v3_ref, None)
                        elif receipt_name == "exact-v2":
                            assign(v3_ref, v2_oid)
                        elif receipt_name == "exact-v3":
                            if legacy:
                                assign(v2_ref, v3_oid)
                        elif receipt_name == "stale":
                            assign(self.context["invalidation_ref"], stale_invalidation)
                        elif receipt_name == "mismatched":
                            assign(v2_ref, bad_v2_oid); assign(v3_ref, bad_v3_oid)
                        before = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
                        result = self.fixture.claim("--require-current-continuity", CONTROLLER)
                        after = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
                        expected = (legacy and receipt_name == "exact-v2") or (
                            marker_name == pointer_name == "valid" and receipt_name == "exact-v3")
                        label = f"marker={marker_name},pointer={pointer_name},receipt={receipt_name}"
                        self.assertEqual(result.returncode == 0, expected, (label, result.stderr.decode()))
                        self.assertEqual(before, after, "reader changed authority: " + label)
                        rows.append({"marker": marker_name, "pointer": pointer_name, "receipt": receipt_name,
                                     "expected_current": expected, "exit_code": result.returncode,
                                     "stdout": result.stdout.decode(), "stderr": result.stderr.decode(),
                                     "refs_before": before.splitlines(), "refs_after": after.splitlines()})
        finally:
            for ref, oid in saved.items():
                assign(ref, oid)
            self.evidence("complete-reader-matrix", {"cases": rows, "case_count": len(rows),
                "source": "actual claim-run v2; actual helper-generated immutable pointer/v3/permanent marker"})
        self.assertEqual(len(rows), 80)
        self.assertEqual(sum(row["expected_current"] for row in rows), 2)
        self.owner.require_current_generation_join_v1(self.context)

    def test_first_migration_after_real_pointer_cas_lock_refusal(self):
        original = self.owner.git_process
        armed = True
        effects = []
        def lock_actual_git(repo, *args, input_bytes=None):
            nonlocal armed
            if (armed and args[:1] == ("update-ref",) and input_bytes
                    and b"update " + self.context["pointer_ref"].encode() + b"\0" in input_bytes):
                armed = False
                lock = self.owner.ref_path(repo, self.context["pointer_ref"]).with_name(CONTROLLER + ".lock")
                lock.parent.mkdir(parents=True, exist_ok=True)
                with lock.open("xb") as handle:
                    handle.write(b"deliberate task-owned Git lock contention\n")
                try:
                    result = original(repo, *args, input_bytes=input_bytes)
                    effects.append({"exit_code": result.returncode, "stdout": result.stdout.decode(),
                                    "stderr": result.stderr.decode(), "pointer_after": self.owner.read_ref(repo, self.context["pointer_ref"])})
                    self.assertNotEqual(result.returncode, 0)
                    return result
                finally:
                    lock.unlink()
            return original(repo, *args, input_bytes=input_bytes)
        before = self.snapshot()
        with mock.patch.object(self.owner, "git_process", side_effect=lock_actual_git):
            result = self.rotate()
        self.assertFalse(armed)
        self.assertEqual(result["status"], "RECOVERED_PRIOR")
        self.assertEqual(result["continuity_epoch"], "G0003")
        failed, _ = self.owner.read_epoch(self.context, "G0002")
        recovery, _ = self.owner.read_epoch(self.context, "G0003")
        self.assertNotEqual(failed["transition"]["invalidation_oid"], recovery["transition"]["invalidation_oid"])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, "G0002")))
        self.assertIsNotNone(self.owner.read_ref(self.fixture.repo, self.context["marker_ref"]))
        self.evidence("real-cas-lock-refusal", {"before": before, "after": self.snapshot(), "result": result, "actual_git_effects": effects})

    def test_real_process_crash_before_archive_preserves_legacy_currentness(self):
        before = self.snapshot()
        result = self.run_crash("before-archive")
        self.assertEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).stdout.decode().strip(), self.fixture.receipt)
        self.assertEqual(before, self.snapshot())
        self.evidence("crash-before-archive", {"before": before, "after": self.snapshot(), "exit_code": result.returncode})

    def _crash_and_recover(self, stage):
        before = self.snapshot()
        process = self.run_crash(stage)
        interrupted = self.snapshot()
        if stage == "after-archive":
            current = self.fixture.claim("--require-current-continuity", CONTROLLER)
            self.assertEqual(current.stdout.decode().strip(), self.fixture.receipt)
            self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.context["pointer_ref"]))
            self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.context["invalidation_ref"]))
            result = {"status": "LEGACY_CURRENT_ARCHIVE_RETAINED"}
        else:
            result = self.owner.recover_rotation_v1(self.context)
            joined = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(result["receipt_token"], joined["receipt_token"])
            self.assertIsNotNone(joined["marker_oid"])
            expected = "ALREADY_CURRENT" if stage == "after-marker" else "RECOVERED_PRIOR"
            self.assertEqual(result["status"], expected)
            self.assertEqual(joined["pointer"]["continuity_epoch"], "G0002" if stage == "after-marker" else "G0003")
            if stage != "after-marker":
                failed, _ = self.owner.read_epoch(self.context, "G0002")
                recovery, _ = self.owner.read_epoch(self.context, "G0003")
                self.assertNotEqual(failed["transition"]["invalidation_oid"], recovery["transition"]["invalidation_oid"])
        for role in ("STATE", "ROADMAP"):
            self.assertEqual((self.fixture.run_root / (role + ".md")).read_bytes(), self.original_pair[role])
        self.evidence("crash-" + stage, {"before": before, "interrupted": interrupted,
            "after": self.snapshot(), "exit_code": process.returncode, "result": result})

    def test_native_same_event_is_idempotent_and_historical_replay_refuses(self):
        self.rotate()
        first = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "physical-one")
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        original_refs = self.snapshot()["refs"]
        again = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "physical-one")
        self.assertEqual(again.returncode, 0, again.stderr.decode())
        self.assertEqual(first.stdout, again.stdout)
        self.assertEqual(original_refs, self.snapshot()["refs"])
        newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "host-reported-compaction", "--event", "physical-two")
        self.assertEqual(newer.returncode, 0, newer.stderr.decode())
        before_replay = self.snapshot()
        replay = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "physical-one")
        self.assertNotEqual(replay.returncode, 0)
        self.assertEqual(before_replay, self.snapshot())
        self.assertEqual(self.owner.read_blob(self.fixture.repo, first.stdout.decode().strip().split("@")[1]).split(b"\t")[-1], b"physical-one\n")
        self.evidence("native-event-idempotency-replay", {"after": self.snapshot(), "first": first.stdout.decode(),
            "again": again.stdout.decode(), "newer": newer.stdout.decode(), "replay_stderr": replay.stderr.decode()})

    def test_one_physical_event_cannot_gain_two_conflicting_boundary_kinds(self):
        self.rotate()
        first = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "one-physical-occurrence")
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        before = self.snapshot()
        conflict = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "host-reported-compaction", "--event", "one-physical-occurrence")
        self.evidence("native-event-kind-ambiguity", {"before": before, "after": self.snapshot(),
            "exit_code": conflict.returncode, "stderr": conflict.stderr.decode()})
        self.assertNotEqual(conflict.returncode, 0, "one physical occurrence was admitted as two conflicting native boundaries")
        self.assertEqual(before, self.snapshot())

    def test_new_native_boundary_cannot_be_repaired_by_rotation_or_legacy_resume(self):
        self.rotate()
        original_marker = self.owner.read_ref(self.fixture.repo, self.context["marker_ref"])
        native = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "host-reported-compaction", "--event", "genuine-current-boundary")
        self.assertEqual(native.returncode, 0, native.stderr.decode())
        before = self.snapshot()
        controls = []
        for args in (("--recover-canonical-state", CONTROLLER),
                     ("--resume-controller", CONTROLLER, "--boundary", "host-reported-compaction", "--epoch", "G0003"),
                     ("--require-current-continuity", CONTROLLER),
                     ("--invalidate-continuity", CONTROLLER, "--boundary", "same-recovery-repair", "--event", "invented-correction"),
                     ("--invalidate-continuity", CONTROLLER, "--boundary", "canonical-state-rotation", "--event", "invented-rotation")):
            result = self.fixture.claim(*args)
            self.assertNotEqual(result.returncode, 0, args)
            self.assertEqual(before, self.snapshot(), args)
            controls.append({"arguments": args, "exit_code": result.returncode, "stderr": result.stderr.decode()})
        successor = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "genuine-successor-boundary")
        self.assertEqual(successor.returncode, 0, successor.stderr.decode())
        self.assertNotEqual(successor.stdout, native.stdout)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["marker_ref"]), original_marker)
        self.evidence("native-boundary-authority-ceiling", {"before": before, "after": self.snapshot(), "controls": controls,
            "native_event": native.stdout.decode(), "newer_event": successor.stdout.decode()})

    def test_migrated_invalidation_ignores_hostile_git_directory_environment(self):
        self.rotate()
        other = self.fixture.repo / "hostile-environment-subject"
        other.mkdir()
        result = run(["git", "init", "-q"], cwd=other)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        environment = dict(os.environ)
        environment.update({"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(other),
                            "PYTHONDONTWRITEBYTECODE": "1"})
        result = subprocess.run(["bash", str(self.fixture.scripts / "claim-run.sh"),
            "--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "real-fixture-boundary"],
            cwd=self.fixture.repo, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        self.evidence("native-invalidation-git-environment", {"exit_code": result.returncode,
            "stderr": result.stderr.decode(), "foreign_coordination_created": (other / ".IMPLEMENTAUDIT").exists(),
            "after": self.snapshot()})
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertFalse((other / ".IMPLEMENTAUDIT").exists(), "inherited Git configuration redirected shell preflight writes")

    def test_actual_git_cas_loser_consumes_complete_winner_without_compensation(self):
        self.run_crash("before-pointer")
        failed, failed_oid = self.owner.read_epoch(self.context, "G0002")
        intent, _ = self.owner.read_publication(self.context, failed, failed_oid)
        recovered = self.fixture.claim("--recover-canonical-state", CONTROLLER)
        self.assertEqual(recovered.returncode, 0, recovered.stderr.decode())
        winner = self.owner.require_current_generation_join_v1(self.context)
        winner_pointer = winner["pointer_oid"]
        marker = winner["marker_oid"]
        # This deliberately constructed CAS stimulus is separate from writer
        # admission. Both candidate objects/receipts came from the actual owner.
        self.fixture.git("update-ref", "-d", self.context["pointer_ref"], winner_pointer)
        command = ["git", "update-ref", "--stdin"]
        loser = subprocess.Popen(command, cwd=self.fixture.repo, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.owner.git_environment())
        def stop():
            if loser.poll() is None:
                loser.kill()
            loser.communicate(timeout=10)
        self.addCleanup(stop)
        loser.stdin.write(("start\nupdate " + self.context["pointer_ref"] + " " + intent["pointer_oid"] + " " + "0" * 40 + "\n").encode())
        loser.stdin.flush()
        self.assertEqual(loser.stdout.readline(), b"start: ok\n")
        winner_effect = run(["git", "update-ref", self.context["pointer_ref"], winner_pointer, "0" * 40], cwd=self.fixture.repo)
        self.assertEqual(winner_effect.returncode, 0, winner_effect.stderr.decode())
        stdout, stderr = loser.communicate(b"prepare\ncommit\n", timeout=10)
        self.assertNotEqual(loser.returncode, 0, "a losing real Git CAS unexpectedly succeeded")
        before = self.snapshot()
        classified = self.owner.recover_failed_epoch(self.context, failed, failed_oid)
        self.assertEqual(classified["status"], "VERIFIED_WINNER")
        self.assertEqual(classified["receipt_token"], winner["receipt_token"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["marker_ref"]), marker)
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, "G0004")))
        self.evidence("actual-git-cas-winner-loser", {"before_consumer": before, "after_consumer": self.snapshot(),
            "winner_pointer": winner_pointer, "losing_pointer": intent["pointer_oid"],
            "winner_exit": winner_effect.returncode, "loser_exit": loser.returncode,
            "loser_stdout": stdout.decode(), "loser_stderr": stderr.decode(), "owner_result": classified})

    def test_distinct_incomplete_winner_is_stop_without_competing_recovery(self):
        self.run_crash("before-pointer")
        failed, failed_oid = self.owner.read_epoch(self.context, "G0002")
        self.owner.recover_rotation_v1(self.context)
        joined = self.owner.require_current_generation_join_v1(self.context)
        cases = []
        for label, ref in (("marker", self.context["marker_ref"]),
                           ("receipt", joined["receipt_token"].split("@")[0])):
            oid = self.owner.read_ref(self.fixture.repo, ref)
            self.fixture.git("update-ref", "-d", ref, oid)
            before = self.snapshot()
            try:
                with self.assertRaises(self.owner.RotationError) as refused:
                    self.owner.recover_failed_epoch(self.context, failed, failed_oid)
                self.assertEqual(self.snapshot(), before)
                self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, "G0004")))
                cases.append({"missing": label, "ref": ref, "error": str(refused.exception), "refs": before["refs"]})
            finally:
                self.fixture.git("update-ref", ref, oid, "0" * 40)
        newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session", "--event", "newer-than-winner")
        self.assertEqual(newer.returncode, 0, newer.stderr.decode())
        before = self.snapshot()
        with self.assertRaises(self.owner.RotationError):
            self.owner.recover_failed_epoch(self.context, failed, failed_oid)
        self.assertEqual(before, self.snapshot())
        self.evidence("incomplete-winner-refusal", {"cases": cases, "newer_boundary": newer.stdout.decode(), "after": self.snapshot()})

    def test_public_concurrent_rotation_loser_cannot_allocate_or_publish(self):
        code = ("import importlib.util, pathlib, sys; sys.dont_write_bytecode=True; "
                "s=importlib.util.spec_from_file_location('lease_owner',sys.argv[1]); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "c=m.discover(sys.argv[2]); lease=m.rotation_lease(c); lease.__enter__(); "
                "print('owner-lease-held',flush=True); sys.stdin.buffer.read(1); lease.__exit__(None,None,None)")
        holder = subprocess.Popen([sys.executable, "-I", "-B", "-c", code,
            str(self.fixture.scripts / "claim-run-rotation.py"), CONTROLLER], cwd=self.fixture.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def stop():
            if holder.poll() is None:
                holder.kill()
            holder.communicate(timeout=10)
        self.addCleanup(stop)
        self.assertEqual(holder.stdout.readline(), b"owner-lease-held\n")
        before = self.snapshot()
        refused = self.fixture.claim("--rotate-canonical-state", CONTROLLER, "--owner-map", self.owner_map)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(before, self.snapshot())
        holder.communicate(b"release", timeout=10)
        self.assertEqual(holder.returncode, 0)
        winner = self.fixture.claim("--rotate-canonical-state", CONTROLLER, "--owner-map", self.owner_map)
        self.assertEqual(winner.returncode, 0, winner.stderr.decode())
        result = json.loads(winner.stdout)
        self.assertEqual(result["status"], "ROTATED")
        self.assertEqual(result["continuity_epoch"], "G0002")
        self.evidence("public-sole-writer-contention", {"before": before, "after": self.snapshot(),
            "loser_exit": refused.returncode, "loser_stderr": refused.stderr.decode(),
            "winner_exit": winner.returncode, "winner_result": result})

    def test_all_retained_transition_gate_removals_refuse_currentness(self):
        self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        epoch, epoch_oid = self.owner.read_epoch(self.context, "G0002")
        receipt_ref, receipt_oid = joined["receipt_token"].split("@")
        refs = {
            "invalidation": self.context["invalidation_ref"], "pointer": self.context["pointer_ref"],
            "receipt": receipt_ref, "marker": self.context["marker_ref"],
            "allocation": self.owner.epoch_ref(self.context, "G0002"),
            "publication-intent": self.owner.publication_ref(self.context, "G0002"),
            "archive": epoch["prepared"]["archive_ref"],
            "invalidation-retention": self.owner.anchor_ref(self.context, joined["pointer"]["invalidation_oid"]),
            "pointer-retention": self.owner.anchor_ref(self.context, joined["pointer_oid"]),
            "receipt-retention": self.owner.anchor_ref(self.context, receipt_oid),
            "marker-retention": self.owner.anchor_ref(self.context, joined["marker_oid"]),
            "allocation-retention": self.owner.anchor_ref(self.context, epoch_oid)}
        rows = []
        for label, ref in refs.items():
            oid = self.owner.read_ref(self.fixture.repo, ref)
            self.assertIsNotNone(oid)
            self.fixture.git("update-ref", "-d", ref, oid)
            before = self.snapshot()
            result = self.fixture.claim("--require-current-continuity", CONTROLLER)
            try:
                self.assertNotEqual(result.returncode, 0, label)
                self.assertEqual(before, self.snapshot(), label)
                rows.append({"omitted": label, "ref": ref, "oid": oid, "exit_code": result.returncode,
                             "stderr": result.stderr.decode()})
            finally:
                self.fixture.git("update-ref", ref, oid, "0" * 40)
        self.owner.require_current_generation_join_v1(self.context)
        self.evidence("retained-transition-gate-omissions", {"case_count": len(rows), "cases": rows})

    def test_wrong_candidate_and_component_readback_refuse_without_ref_changes(self):
        result = self.rotate()
        joined = self.owner.require_current_generation_join_v1(self.context)
        rows = []
        for role, path in (("STATE", joined["state_path"]), ("ROADMAP", joined["roadmap_path"]),
                           ("protected", joined["state_path"].parent / "protected-state.json"),
                           ("archive", joined["state_path"].parent / "archive-manifest.json")):
            saved = path.read_bytes()
            saved_mode = path.stat().st_mode & 0o777
            before = self.snapshot()["refs"]
            path.chmod(0o644)
            path.write_bytes(saved + b"corruption\n")
            failed = self.fixture.claim("--require-current-continuity", CONTROLLER)
            try:
                self.assertNotEqual(failed.returncode, 0, role)
                self.assertEqual(before, self.snapshot()["refs"], role)
                rows.append({"component": role, "exit_code": failed.returncode, "stderr": failed.stderr.decode()})
            finally:
                path.write_bytes(saved)
                path.chmod(saved_mode)
        commit = self.fixture.git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                                  "commit-tree", self.fixture.tree, "-p", self.fixture.head, input_bytes=b"different candidate fixture\n")
        self.fixture.git("update-ref", "HEAD", commit, self.fixture.head)
        failed = self.fixture.claim("--require-current-continuity", CONTROLLER)
        try:
            self.assertNotEqual(failed.returncode, 0)
            rows.append({"component": "HEAD", "exit_code": failed.returncode, "stderr": failed.stderr.decode()})
        finally:
            self.fixture.git("update-ref", "HEAD", self.fixture.head, commit)
        for role in ("STATE", "ROADMAP"):
            read = self.fixture.claim("--read-current-state", CONTROLLER, role, "--expected-pointer", result["pointer_token"])
            self.assertEqual(read.returncode, 0, read.stderr.decode())
        stale_pointer = self.context["pointer_ref"] + "@" + "f" * 40
        mismatch = self.fixture.claim("--read-current-state", CONTROLLER, "ROADMAP", "--expected-pointer", stale_pointer)
        self.assertNotEqual(mismatch.returncode, 0)
        self.evidence("candidate-component-corruption", {"cases": rows, "separate_reader_mismatch": mismatch.stderr.decode()})


class NativeResumeDiscriminators(unittest.TestCase):
    """Original native boundary identity, exact prior payload and sole-owner v3.

    Occurrences below are declared fixture stimuli, not host authentication or
    erroneous-event adjudication. All receipts come from the real claim owner.
    """
    setUp = RealHelperIntegration.setUp
    rotate = RealHelperIntegration.rotate
    snapshot = CompleteOwnerDiscriminators.snapshot
    evidence = CompleteOwnerDiscriminators.evidence

    def native_pending(self, boundary="host-reported-compaction", event="native-pre-resume-occurrence"):
        rotated = self.rotate()
        prior = self.owner.require_current_generation_join_v1(self.context)
        invalidated = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", boundary, "--event", event)
        self.assertEqual(invalidated.returncode, 0, invalidated.stderr.decode())
        resolved = self.fixture.claim("--resolve-resume-generation", CONTROLLER)
        self.assertEqual(resolved.returncode, 0, resolved.stderr.decode())
        source = json.loads(resolved.stdout)
        self.assertEqual(source["schema"], "implementaudit.native-resume-source.v1")
        self.assertEqual(source["status"], "PRE_RESUME_EVIDENCE")
        self.assertEqual(source["pointer_token"], rotated["pointer_token"])
        self.assertEqual(source["invalidation_token"], invalidated.stdout.decode().strip())
        return source, prior

    def native_resume(self, source, *, epoch=None, boundary=None):
        return self.fixture.claim("--resume-controller", CONTROLLER, "--boundary", boundary or source["boundary"],
            "--epoch", epoch or source["next_continuity_epoch"], "--expected-pointer", source["pointer_token"],
            "--expected-invalidation", source["invalidation_token"])

    def test_public_native_resume_accepts_exact_native_successor_tokens(self):
        rotated = self.rotate()
        prior = self.owner.require_current_generation_join_v1(self.context)
        event = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "new-session",
                                   "--event", "native-resume-original-event")
        self.assertEqual(event.returncode, 0, event.stderr.decode())
        before = self.snapshot()
        resumed = self.fixture.claim("--resume-controller", CONTROLLER, "--boundary", "new-session",
                                     "--epoch", "G0003", "--expected-pointer", rotated["pointer_token"],
                                     "--expected-invalidation", event.stdout.decode().strip())
        self.evidence("native-resume-exact-successor", {"before": before, "after": self.snapshot(),
            "exit_code": resumed.returncode, "stderr": resumed.stderr.decode(), "stdout": resumed.stdout.decode(),
            "prior_pointer": rotated["pointer_token"], "native_invalidation": event.stdout.decode().strip()})
        self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(resumed.stdout.decode().strip(), joined["receipt_token"])
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")
        self.assertEqual(joined["pointer"]["invalidation_oid"], event.stdout.decode().strip().split("@")[1])
        self.assertEqual(joined["marker_oid"], prior["marker_oid"])
        self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], prior["receipt_token"])
        self.assertEqual(joined["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"],
                         prior["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"])
        record, _ = self.owner.read_epoch(self.context, "G0003")
        self.assertEqual(record["transition"]["transition_kind"], "native-resume")
        self.assertEqual(record["transition"]["boundary"], "new-session")
        self.assertEqual(record["transition"]["payload_source"], "preimage")
        for role in ("STATE", "ROADMAP"):
            self.assertEqual((self.fixture.run_root / (role + ".md")).read_bytes(), self.original_pair[role])

    def test_separate_native_evidence_reads_never_supply_currentness(self):
        source, prior = self.native_pending()
        before = self.snapshot()
        for role in ("STATE", "ROADMAP"):
            ordinary = self.fixture.claim("--read-canonical-state", CONTROLLER, "--role", role,
                                          "--expected-pointer", source["pointer_token"])
            self.assertNotEqual(ordinary.returncode, 0)
            evidence = self.fixture.claim("--read-resume-state", CONTROLLER, "--role", role,
                "--expected-pointer", source["pointer_token"], "--expected-invalidation", source["invalidation_token"])
            self.assertEqual(evidence.returncode, 0, evidence.stderr.decode())
            self.assertEqual(evidence.stdout, prior[role.lower() + "_bytes"])
        self.assertNotEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).returncode, 0)
        self.assertNotEqual(self.fixture.claim("--verify-resume-receipt", source["receipt_token"]).returncode, 0)
        self.assertEqual(self.snapshot(), before)
        resumed = self.native_resume(source)
        self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
        self.assertEqual(self.fixture.claim("--verify-resume-receipt", resumed.stdout.decode().strip()).stdout, resumed.stdout)
        self.assertEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).stdout, resumed.stdout)
        self.assertNotEqual(self.fixture.claim("--resolve-resume-generation", CONTROLLER).returncode, 0)
        self.evidence("native-separate-evidence-currentness", {"source": source, "before": before,
                      "after": self.snapshot(), "receipt": resumed.stdout.decode().strip()})

    def test_native_tokens_epoch_boundary_and_completed_retry_are_exact(self):
        source, _ = self.native_pending()
        before = self.snapshot()
        controls = []
        base = ["--resume-controller", CONTROLLER, "--boundary", source["boundary"], "--epoch", "G0003"]
        pairs = [(None, source["invalidation_token"]), (source["pointer_token"], None),
                 (source["pointer_token"].split("@")[0], source["invalidation_token"]),
                 (source["pointer_token"].split("@")[0] + "@" + "a" * 40, source["invalidation_token"]),
                 (source["pointer_token"], source["invalidation_token"].split("@")[0] + "@" + "b" * 40)]
        for pointer, invalidation in pairs:
            args = base + (["--expected-pointer", pointer] if pointer else [])
            args += ["--expected-invalidation", invalidation] if invalidation else []
            refused = self.fixture.claim(*args)
            controls.append({"arguments": args, "exit_code": refused.returncode, "stderr": refused.stderr.decode()})
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(self.snapshot(), before)
        for epoch, boundary in (("G0002", source["boundary"]), ("G0004", source["boundary"]),
                                ("G0000", source["boundary"]), ("G0003", "new-session"),
                                ("G0003", "canonical-state-rotation"), ("G0003", "same-recovery-repair")):
            refused = self.native_resume(source, epoch=epoch, boundary=boundary)
            controls.append({"epoch": epoch, "boundary": boundary, "exit_code": refused.returncode,
                             "stderr": refused.stderr.decode()})
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(self.snapshot(), before)
        resumed = self.native_resume(source, epoch="e3")
        self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
        completed = self.snapshot()
        retry = self.native_resume(source)
        self.assertEqual(retry.returncode, 0, retry.stderr.decode())
        self.assertEqual(retry.stdout, resumed.stdout)
        self.assertEqual(self.snapshot(), completed)
        self.evidence("native-exact-tokens-and-retry", {"controls": controls, "before": before,
                      "after": completed, "receipt": resumed.stdout.decode().strip()})

    def test_newer_native_event_between_separate_reads_refuses_old_evidence(self):
        source, prior = self.native_pending()
        first = self.fixture.claim("--read-resume-state", CONTROLLER, "--role", "STATE",
            "--expected-pointer", source["pointer_token"], "--expected-invalidation", source["invalidation_token"])
        self.assertEqual(first.stdout, prior["state_bytes"])
        newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "handoff-resume", "--event", "newer-between-reads")
        self.assertEqual(newer.returncode, 0, newer.stderr.decode())
        before = self.snapshot()
        second = self.fixture.claim("--read-resume-state", CONTROLLER, "--role", "ROADMAP",
            "--expected-pointer", source["pointer_token"], "--expected-invalidation", source["invalidation_token"])
        self.assertNotEqual(second.returncode, 0)
        self.assertNotEqual(self.native_resume(source).returncode, 0)
        self.assertEqual(self.snapshot(), before)
        latest = json.loads(self.fixture.claim("--resolve-resume-generation", CONTROLLER).stdout)
        resumed = self.native_resume(latest)
        self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
        self.evidence("native-between-separate-reads", {"old_source": source, "new_source": latest,
                      "after": self.snapshot(), "receipt": resumed.stdout.decode().strip()})

    def test_all_five_native_boundaries_preserve_the_permanent_marker(self):
        result = self.rotate()
        prior = self.owner.require_current_generation_join_v1(self.context)
        rows = []
        for ordinal, boundary in enumerate(sorted(self.owner.BOUNDARIES), 3):
            invalidated = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", boundary,
                                             "--event", "distinct-native-occurrence-" + boundary)
            self.assertEqual(invalidated.returncode, 0, invalidated.stderr.decode())
            source = json.loads(self.fixture.claim("--resolve-resume-generation", CONTROLLER).stdout)
            resumed = self.native_resume(source)
            self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
            joined = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(joined["marker_oid"], result["marker_oid"])
            self.assertEqual(joined["pointer"]["continuity_epoch"], f"G{ordinal:04X}")
            self.assertEqual(joined["pointer"]["predecessor_receipt_ref_oid"], prior["receipt_token"])
            self.assertEqual(joined["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"],
                             prior["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"])
            rows.append({"boundary": boundary, "source_pointer": source["pointer_token"],
                         "invalidation": source["invalidation_token"], "receipt": joined["receipt_token"]})
            prior = joined
        self.evidence("native-all-five-boundaries", {"rows": rows, "after": self.snapshot()})

    def test_native_preparation_preemption_preserves_actual_event_and_allocation_absence(self):
        source, _ = self.native_pending()
        original = self.helper.prepare_native_resume_draft
        def preempt(*args, **kwargs):
            prepared = original(*args, **kwargs)
            newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "manual-resume",
                                       "--event", "actual-newer-event-during-prepare")
            self.assertEqual(newer.returncode, 0, newer.stderr.decode())
            return prepared
        with mock.patch.object(self.helper, "prepare_native_resume_draft", side_effect=preempt):
            with self.assertRaises(self.owner.RotationError):
                self.owner.resume_native_generation_v1(self.context, source["boundary"], "G0003",
                                                       source["pointer_token"], source["invalidation_token"])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.epoch_ref(self.context, "G0003")))
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, "G0003")))
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["pointer_ref"]), source["pointer_token"].split("@")[1])
        latest = json.loads(self.fixture.claim("--resolve-resume-generation", CONTROLLER).stdout)
        self.assertEqual(latest["boundary"], "manual-resume")
        resumed = self.native_resume(latest)
        self.evidence("native-prepare-preemption", {"source": source, "latest": latest, "after": self.snapshot(),
                      "retry_exit_code": resumed.returncode, "retry_stderr": resumed.stderr.decode()})
        self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())

    def test_native_ancestor_archive_ref_drift_is_fenced_by_real_pointer_cas(self):
        source, _ = self.native_pending()
        original = self.owner.update_refs
        ancestor = f"refs/implementaudit/state-archives/{CONTROLLER}/G0002"
        old = self.owner.read_ref(self.fixture.repo, ancestor)
        observed = {}
        def drift(context, updates, guards, **kwargs):
            if context["pointer_ref"] in updates:
                self.assertEqual(guards.get(ancestor), old)
                observed["guards"] = dict(guards)
                self.fixture.git("update-ref", "-d", ancestor, old)
            return original(context, updates, guards, **kwargs)
        with mock.patch.object(self.owner, "update_refs", side_effect=drift):
            with self.assertRaises(self.owner.RotationError):
                self.owner.resume_native_generation_v1(self.context, source["boundary"], "G0003",
                                                       source["pointer_token"], source["invalidation_token"])
        self.assertTrue(observed)
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, ancestor))
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["pointer_ref"]), source["pointer_token"].split("@")[1])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["invalidation_ref"]), source["invalidation_token"].split("@")[1])
        self.assertIsNone(self.owner.read_ref(self.fixture.repo, self.owner.receipt_ref(self.context, "G0003")))
        self.evidence("native-ancestor-archive-cas-drift", {"source": source, "deleted_ancestor": ancestor,
                      "old_oid": old, "publication_guards": observed["guards"], "after": self.snapshot()})

    def test_newer_native_event_after_allocation_is_never_relabeled_or_compensated(self):
        source, prior = self.native_pending()
        original = self.helper.finalize_canonical_projection
        events = []
        def preempt(*args, **kwargs):
            final = original(*args, **kwargs)
            newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "handoff-resume",
                                       "--event", "actual-newer-native-event-during-finalization")
            self.assertEqual(newer.returncode, 0, newer.stderr.decode())
            events.append(newer.stdout.decode().strip())
            return final
        with mock.patch.object(self.helper, "finalize_canonical_projection", side_effect=preempt):
            with self.assertRaises(self.owner.RotationError):
                self.owner.resume_native_generation_v1(self.context, source["boundary"], "G0003",
                                                       source["pointer_token"], source["invalidation_token"])
        self.assertEqual(len(events), 1)
        stopped = self.snapshot()
        record, _ = self.owner.read_epoch(self.context, "G0003")
        self.assertEqual(record["transition"]["boundary"], source["boundary"])
        self.assertEqual(record["transition"]["invalidation_oid"], source["invalidation_token"].split("@")[1])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["invalidation_ref"]), events[0].split("@")[1])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["pointer_ref"]), prior["pointer_oid"])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["marker_ref"]), prior["marker_oid"])
        self.assertNotEqual(self.fixture.claim("--recover-canonical-state", CONTROLLER).returncode, 0)
        latest = json.loads(self.fixture.claim("--resolve-resume-generation", CONTROLLER).stdout)
        self.assertNotEqual(self.native_resume(latest).returncode, 0)
        self.assertEqual(self.snapshot(), stopped)
        self.evidence("native-post-allocation-preemption", {"source": source, "newer_event": events[0],
                      "retained_transition": record["transition"], "after": stopped})

    def test_pending_native_evidence_requires_complete_prior_custody(self):
        source, prior = self.native_pending()
        baseline = self.snapshot()
        controls = []
        for ref in (self.context["pointer_ref"], self.context["marker_ref"], source["receipt_token"].split("@")[0],
                    self.owner.anchor_ref(self.context, prior["pointer"]["invalidation_oid"]),
                    self.owner.anchor_ref(self.context, source["invalidation_token"].split("@")[1])):
            old = self.owner.read_ref(self.fixture.repo, ref)
            self.fixture.git("update-ref", "-d", ref, old)
            before = self.snapshot()
            refused = self.fixture.claim("--resolve-resume-generation", CONTROLLER)
            self.assertNotEqual(refused.returncode, 0, ref)
            self.assertEqual(self.snapshot(), before)
            controls.append({"ref": ref, "exit_code": refused.returncode, "stderr": refused.stderr.decode()})
            self.fixture.git("update-ref", ref, old, "0" * 40)
        for path in (Path(source["state_path"]), Path(source["protected_manifest_path"])):
            old = path.read_bytes()
            mode = path.stat().st_mode & 0o777
            path.chmod(0o644)
            path.write_bytes(old + b"unbound change\n")
            path.chmod(mode)
            before = self.snapshot()
            refused = self.fixture.claim("--resolve-resume-generation", CONTROLLER)
            self.assertNotEqual(refused.returncode, 0, str(path))
            self.assertEqual(self.snapshot(), before)
            controls.append({"component": path.name, "exit_code": refused.returncode, "stderr": refused.stderr.decode()})
            path.chmod(0o644)
            path.write_bytes(old)
            path.chmod(mode)
        self.fixture.git("-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "unbound candidate fixture")
        before = self.snapshot()
        refused = self.fixture.claim("--resolve-resume-generation", CONTROLLER)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(self.snapshot(), before)
        controls.append({"head_change": True, "exit_code": refused.returncode, "stderr": refused.stderr.decode()})
        self.fixture.git("update-ref", "HEAD", self.fixture.head)
        self.assertEqual(self.snapshot(), baseline)
        self.assertEqual(self.fixture.claim("--resolve-resume-generation", CONTROLLER).returncode, 0)
        self.evidence("native-prior-custody-matrix", {"controls": controls, "after": self.snapshot()})

    def _native_crash_and_check(self, stage):
        source, prior = self.native_pending()
        crashed = run([sys.executable, "-I", "-B", Path(__file__).resolve(), "--native-crash-driver",
            self.fixture.scripts / "claim-run-rotation.py", CONTROLLER, source["boundary"],
            source["next_continuity_epoch"], source["pointer_token"], source["invalidation_token"], stage], cwd=self.fixture.repo)
        self.assertEqual(crashed.returncode, 86, (stage, crashed.stderr.decode()))
        stopped = self.snapshot()
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["marker_ref"]), prior["marker_oid"])
        self.assertEqual(self.owner.read_ref(self.fixture.repo, self.context["invalidation_ref"]), source["invalidation_token"].split("@")[1])
        if stage == "after-receipt":
            current = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(current["pointer"]["continuity_epoch"], "G0003")
            resumed = self.native_resume(source)
            self.assertEqual(resumed.returncode, 0, resumed.stderr.decode())
            self.assertEqual(resumed.stdout.decode().strip(), current["receipt_token"])
            self.assertEqual(self.snapshot(), stopped)
        else:
            self.assertNotEqual(self.native_resume(source).returncode, 0)
            self.assertNotEqual(self.fixture.claim("--recover-canonical-state", CONTROLLER).returncode, 0)
            self.assertNotEqual(self.fixture.claim("--require-current-continuity", CONTROLLER).returncode, 0)
            self.assertEqual(self.snapshot(), stopped)
            newer = self.fixture.claim("--invalidate-continuity", CONTROLLER, "--boundary", "inferred-context-gap",
                                       "--event", "genuinely-new-after-native-crash-" + stage)
            self.assertEqual(newer.returncode, 0, newer.stderr.decode())
        self.evidence("native-process-crash-" + stage, {"source": source, "exit_code": crashed.returncode,
                      "stopped": stopped, "after": self.snapshot()})


def _install_crash_test(stage):
    def case(self):
        self._crash_and_recover(stage)
    case.__name__ = "test_real_process_crash_" + stage.replace("-", "_")
    setattr(CompleteOwnerDiscriminators, case.__name__, case)


for _stage in ("after-archive", "after-invalidation", "before-generation", "after-generation",
               "before-pointer", "after-pointer", "before-receipt", "after-receipt", "before-marker", "after-marker"):
    _install_crash_test(_stage)


def _install_native_crash_test(stage):
    def case(self):
        self._native_crash_and_check(stage)
    case.__name__ = "test_native_process_crash_" + stage.replace("-", "_")
    setattr(NativeResumeDiscriminators, case.__name__, case)


for _native_stage in ("after-epoch", "after-pointer", "after-receipt"):
    _install_native_crash_test(_native_stage)


def crash_driver(arguments):
    owner_path, controller, owner_map, stage = arguments
    spec = importlib.util.spec_from_file_location("actual_claim_crash_owner", owner_path)
    owner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = owner
    spec.loader.exec_module(owner)
    context = owner.discover(controller)
    helper = owner.projection_helper()
    original_prepare = helper.prepare_canonical_draft
    original_finalize = helper.finalize_canonical_projection
    original_git = owner.git_process
    def stop():
        os._exit(86)
    def prepare(*args, **kwargs):
        if stage == "before-archive": stop()
        result = original_prepare(*args, **kwargs)
        if stage == "after-archive": stop()
        return result
    def finalize(*args, **kwargs):
        if stage == "before-generation": stop()
        result = original_finalize(*args, **kwargs)
        if stage == "after-generation": stop()
        return result
    def git_operation(repo, *args, input_bytes=None):
        point = None
        if args[:1] == ("update-ref",) and input_bytes:
            for label, ref in (("invalidation", context["invalidation_ref"]), ("pointer", context["pointer_ref"]),
                               ("receipt", owner.receipt_ref(context, "G0002")), ("marker", context["marker_ref"])):
                if b"update " + ref.encode() + b"\0" in input_bytes:
                    point = label
                    break
        if stage == "before-" + str(point): stop()
        result = original_git(repo, *args, input_bytes=input_bytes)
        if stage == "after-" + str(point) and result.returncode == 0: stop()
        return result
    helper.prepare_canonical_draft = prepare
    helper.finalize_canonical_projection = finalize
    owner.git_process = git_operation
    owner.run_canonical_rotation_v1(context, Path(owner_map), helper.calibration_contract_v1())
    raise RuntimeError("the requested crash point was not reached")


def native_crash_driver(arguments):
    owner_path, controller, boundary, epoch, pointer_token, invalidation_token, stage = arguments
    spec = importlib.util.spec_from_file_location("actual_native_crash_owner", owner_path)
    owner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = owner
    spec.loader.exec_module(owner)
    context = owner.discover(controller)
    original_git = owner.git_process
    refs = {"epoch": owner.epoch_ref(context, epoch), "pointer": context["pointer_ref"],
            "receipt": owner.receipt_ref(context, epoch)}
    def git_operation(repo, *args, input_bytes=None):
        point = None
        if args[:1] == ("update-ref",) and input_bytes:
            for label, ref in refs.items():
                if b"update " + ref.encode() + b"\0" in input_bytes:
                    point = label
                    break
        result = original_git(repo, *args, input_bytes=input_bytes)
        if stage == "after-" + str(point) and result.returncode == 0:
            os._exit(86)
        return result
    owner.git_process = git_operation
    owner.resume_native_generation_v1(context, boundary, epoch, pointer_token, invalidation_token)
    raise RuntimeError("the requested native crash point was not reached")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--crash-driver"]:
        crash_driver(sys.argv[2:])
    elif sys.argv[1:2] == ["--native-crash-driver"]:
        native_crash_driver(sys.argv[2:])
    else:
        unittest.main(verbosity=2)
