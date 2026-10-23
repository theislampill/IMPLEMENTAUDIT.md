#!/usr/bin/env python3
"""Constructed native-resume source controls; no authenticated host evidence."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = load("native_resume_projection_fixture", HERE / "protected_projection_v2_test.py")
M = F.MODULE
NATIVE_BOUNDARIES = ("host-reported-compaction", "new-session", "handoff-resume",
                     "manual-resume", "inferred-context-gap")
A = load("native_resume_archive_fixture", HERE / "archive_v2_test.py")
H = A.M


def parse(pair):
    state, roadmap, owners, artifacts = pair
    return M.parse_canonical_pair_v2(state, roadmap, owner_map=owners, artifacts=artifacts)


def migrated_preimage():
    prior = parse(F.fixture_pair(F.native_profile_bodies()))
    projected = M.derive_hot_pair_v2(prior, transition=F.successor(prior),
                                    archive_pointers=F.archive_pointers(prior), **F.LIMITS)
    bodies = {role: json.loads(projected[role.lower() + "_bytes"].split(b"```json\n")[1].split(b"\n```")[0])
              for role in ("STATE", "ROADMAP")}
    return parse(F.fixture_pair(bodies))


def native_transition(preimage, boundary="host-reported-compaction"):
    transition = F.successor(preimage)
    transition.update(schema_version="implementaudit.native-resume-transition.v1",
                      transition_kind="native-resume", boundary=boundary, invalidation_oid="6" * 40)
    return transition


def project_native(preimage, transition=None):
    return M.derive_hot_pair_v2(preimage, transition=transition or native_transition(preimage),
                                archive_pointers=F.archive_pointers(preimage, "G0003"), **F.LIMITS)


class NativeResumeAlgebra(unittest.TestCase):
    def test_native_resume_preserves_actual_boundary_payload_and_archive_genealogy(self):
        preimage = migrated_preimage()
        old_archives = preimage["protected_manifest"]["ARCHIVED_ONLY_HISTORY"]
        for boundary in NATIVE_BOUNDARIES:
            with self.subTest(boundary=boundary):
                transition = native_transition(preimage, boundary)
                result = project_native(preimage, transition)
                self.assertEqual(result["payload"], preimage["payload"])
                self.assertEqual(result["owner_map"], preimage["owner_map"])
                self.assertEqual(result["transition"]["boundary"], boundary)
                self.assertEqual(result["transition"]["continuity_epoch"], "G0003")
                self.assertEqual(result["transition"]["projection_generation_id"], "G0003")
                self.assertEqual(result["transition"]["predecessor_receipt_ref_oid"], preimage["current_receipt_ref_oid"])
                self.assertEqual(result["archive_pointers"][:len(old_archives)], old_archives)
                self.assertEqual(result["authority_ceiling"], "NO_CURRENTNESS_AUTHORITY")
                self.assertTrue(M.verify_projection_equivalence_v2(preimage, result)["equivalent"])

    def test_native_resume_rejects_reuse_substitution_relabel_and_future_bindings(self):
        preimage = migrated_preimage()
        mutations = {
            "schema": {"schema_version": "implementaudit.canonical-state-transition.v2"},
            "rotation-boundary": {"boundary": "canonical-state-rotation"},
            "unknown-boundary": {"boundary": "constructed-native"},
            "untyped-boundary": {"boundary": []},
            "rotation-kind": {"transition_kind": "rotation"},
            "recovery-kind": {"transition_kind": "recovery"},
            "old-epoch": {"continuity_epoch": "G0002"},
            "skipped-epoch": {"continuity_epoch": "G0004"},
            "old-generation": {"projection_generation_id": "G0002"},
            "skipped-generation": {"projection_generation_id": "G0004"},
            "old-invalidation": {"invalidation_oid": preimage["current_continuity"]["invalidation_oid"]},
            "wrong-predecessor": {"predecessor_receipt_ref_oid": preimage["current_receipt_ref_oid"][:-40] + "9" * 40},
            "wrong-prior-epoch": {"predecessor_epoch": "G0001"},
            "wrong-prior-generation": {"predecessor_generation_id": "G0001"},
            "reconciliation": {"reconciled": False},
            "failed-epoch": {"failed_transition_epoch": "G0003"},
            "failed-generation": {"failed_projection_generation_id": "G0003"},
            "failed-receipt": {"failed_transition_receipt_ref_oid": preimage["current_receipt_ref_oid"]},
            "future-receipt": {"successor_receipt_oid": "a" * 40},
            "future-pointer": {"pointer_oid": "b" * 40},
        }
        for name, changed in mutations.items():
            with self.subTest(mutation=name), self.assertRaises(M.ProjectionV2Error):
                project_native(preimage, dict(native_transition(preimage), **changed))
        for key in native_transition(preimage):
            transition = native_transition(preimage)
            del transition[key]
            with self.subTest(omission=key), self.assertRaises(M.ProjectionV2Error):
                project_native(preimage, transition)

    def test_native_resume_is_migrated_only_and_protected_changes_refuse(self):
        legacy = parse(F.fixture_pair())
        with self.assertRaises(M.ProjectionV2Error):
            M.derive_hot_pair_v2(legacy, transition=native_transition(legacy),
                                 archive_pointers=F.archive_pointers(legacy), **F.LIMITS)
        preimage = migrated_preimage()
        result = project_native(preimage)
        for group in preimage["payload"]["STATE"]:
            changed = copy.deepcopy(result)
            del changed["payload"]["STATE"][group]
            with self.subTest(omission=group), self.assertRaises(M.ProjectionV2Error):
                M.verify_projection_equivalence_v2(preimage, changed)


def fixture_commit_pointer(subject, pointer):
    """Construct original-wire inputs for helper tests, without currentness credit."""
    repo = subject["repo"]
    predecessor = dict(subject["predecessor"])
    pointer_oid = H._anchor_object(repo, pointer["controller"], F.canonical(pointer))
    # The constructed producer must retain its own declared invalidation;
    # otherwise the GC control would destroy its prerequisite instead of an archive.
    H._anchor_object(repo, pointer["controller"], H._blob(repo, pointer["invalidation_oid"]))
    A.git(repo, "update-ref", predecessor["pointer_ref"], pointer_oid, predecessor["pointer_oid"] or "0" * 40)
    receipt_ref = pointer["expected_receipt_ref_schema"]["ref"]
    fields = ["implementaudit.continuity-receipt.v3", pointer["controller"], pointer["claim_id"],
              pointer["run_root_identity"], pointer["continuity_epoch"], pointer["invalidation_oid"],
              predecessor["pointer_ref"], pointer_oid, pointer["state_sha256"], pointer["roadmap_sha256"],
              pointer["protected_manifest_sha256"], pointer["archive_manifest_sha256"],
              pointer["exact_next_action"], pointer["predecessor_receipt_ref_oid"]]
    receipt_oid = A.git(repo, "hash-object", "-w", "--stdin", data=("\t".join(fields) + "\n").encode()).decode().strip()
    A.git(repo, "update-ref", receipt_ref, receipt_oid, "0" * 40)
    marker_ref = "refs/implementaudit/current-generation-migrations/" + pointer["controller"]
    marker_oid = predecessor["migration_marker_oid"]
    if marker_oid is None:
        fields = ["implementaudit.current-generation-migration.v1", pointer["controller"], pointer["claim_id"],
                  pointer["run_root_identity"], pointer["continuity_epoch"], predecessor["pointer_ref"],
                  "implementaudit.current-generation.v1", receipt_ref, receipt_oid, "true"]
        marker_oid = A.git(repo, "hash-object", "-w", "--stdin", data="\t".join(fields).encode()).decode().strip()
        A.git(repo, "update-ref", marker_ref, marker_oid, "0" * 40)
    predecessor.update({key: pointer[key] for key in ("continuity_epoch", "projection_generation_id",
                                                     "invalidation_oid", "state_sha256", "roadmap_sha256")})
    predecessor.update(receipt_ref=receipt_ref, receipt_oid=receipt_oid,
                       receipt_schema="implementaudit.continuity-receipt.v3", pointer_oid=pointer_oid,
                       migration_marker_oid=marker_oid)
    for role in ("state", "roadmap"):
        predecessor[role + "_path"] = (pointer["run_root_identity"] + "/state-generations/"
                                       + pointer["projection_generation_id"] + "/" + role.upper() + ".md")
    subject["predecessor"] = predecessor
    subject["pointer"] = pointer
    return subject


def helper_native_transition(subject, boundary="host-reported-compaction"):
    predecessor = subject["predecessor"]
    epoch = "G%04X" % (int(predecessor["continuity_epoch"][1:], 16) + 1)
    generation = "G%04X" % (int(predecessor["projection_generation_id"][1:], 16) + 1)
    fields = ["implementaudit.continuity-invalidation.v1", predecessor["controller"],
              predecessor["controller_oid"], predecessor["claim_id"], boundary,
              "Constructed boundary for immutable helper regression " + epoch]
    oid = A.git(subject["repo"], "hash-object", "-w", "--stdin", data=("\t".join(fields) + "\n").encode()).decode().strip()
    return {"schema": "implementaudit.native-resume-transition.v1", "controller": predecessor["controller"],
            "claim_id": predecessor["claim_id"], "run_root_identity": predecessor["run_root_identity"],
            "projection_generation_id": generation, "continuity_epoch": epoch, "boundary": boundary,
            "invalidation_oid": oid, "predecessor_receipt_ref_oid": predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"],
            "expected_receipt_ref_schema": {"ref": "refs/implementaudit/continuity-receipts/" + predecessor["controller"] + "/" + epoch,
                                            "schema": "implementaudit.continuity-receipt.v3"},
            "transition_kind": "native-resume", "payload_source": "preimage", "failed_transition_epoch": None,
            "failed_transition_generation": None, "failed_transition_receipt_ref_oid": None,
            "head": predecessor["head"], "tree": predecessor["tree"]}


class NativeResumeArchive(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0039-native-helper-")
        self.subject = A.make_subject(Path(self.temp.name) / "repo")
        prepared = A.prepare(self.subject)
        output = H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], prepared,
                                                 A.transition(self.subject, prepared))
        fixture_commit_pointer(self.subject, output["pointer"])
        self.subject["owner_map"].unlink()

    def tearDown(self):
        self.temp.cleanup()

    def prepare_native(self):
        s = self.subject
        generation = "G%04X" % (int(s["predecessor"]["projection_generation_id"][1:], 16) + 1)
        return H.prepare_native_resume_draft(s["repo"], s["run"], s["predecessor"]["controller"],
                                             generation, s["predecessor"])

    def authority_refs(self):
        lines = A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)").decode().splitlines()
        return [line for line in lines if "/state-archives/" not in line]

    def test_native_resume_prepares_below_rotation_threshold_without_caller_map(self):
        s = self.subject
        before = H.read_canonical_generation(s["repo"], s["run"], s["pointer"])
        authority_before = self.authority_refs()
        prepared = self.prepare_native()
        self.assertEqual(prepared["schema"], "implementaudit.native-resume-prepared.v1")
        self.assertLess(prepared["measurement"]["live_bytes_before"], H.calibration_contract_v1()["byte_threshold"])
        self.assertEqual(prepared["measurement"]["model_calls"], 0)
        manifest = H.verify_canonical_archive(s["repo"], prepared["controller"], prepared["archive_ref"],
                                               prepared["archive_manifest_sha256"])
        self.assertEqual(manifest["preparation_kind"], "native-resume")
        archived = H._archive_preimage(s["repo"], manifest)
        self.assertEqual(archived["state_bytes"], before["state_bytes"])
        self.assertEqual(archived["roadmap_bytes"], before["roadmap_bytes"])
        prior_rows = before["protected_manifest"]["PRESERVED_PAYLOAD"]["owner_map"]
        for old, new in zip(prior_rows, archived["owner_map"]):
            for field in ("field", "owner", "source_kind", "source_id", "source_pointer"):
                self.assertEqual(old[field], new[field])
            if old["source_kind"] == "PAIR":
                self.assertEqual(old["value_sha256"], new["value_sha256"])
            elif old["source_id"] != "receipt":
                self.assertEqual(old, new)
        draft = json.loads((s["run"] / prepared["draft_path"] / "draft-manifest.json").read_bytes())
        self.assertIsNone(draft["transition"])
        self.assertEqual(self.authority_refs(), authority_before)
        transition = helper_native_transition(s)
        output = H.finalize_canonical_projection(s["repo"], s["run"], prepared, transition)
        resolved = H.read_canonical_generation(s["repo"], s["run"], output["pointer"])
        self.assertEqual(resolved["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"],
                         before["protected_manifest"]["PRESERVED_PAYLOAD"]["payload"])
        self.assertEqual(resolved["protected_manifest"]["MONOTONIC_TRANSITION"]["boundary"], "host-reported-compaction")
        self.assertEqual(resolved["protected_manifest"]["MONOTONIC_TRANSITION"]["invalidation_oid"], transition["invalidation_oid"])
        self.assertEqual(self.authority_refs(), authority_before)

    def test_native_predecessor_omissions_future_fields_and_identity_changes_write_nothing(self):
        original = self.subject["predecessor"]
        mutations = [{key: value for key, value in original.items() if key != missing} for missing in original]
        mutations += [dict(original, **changed) for changed in (
            {"successor_receipt_oid": "a" * 40}, {"successor_pointer_oid": "b" * 40},
            {"receipt_schema": "implementaudit.continuity-receipt.v2"}, {"continuity_epoch": "G0001"},
            {"projection_generation_id": "G0001"}, {"claim_id": "another-claim"},
            {"head": "a" * 40}, {"tree": "b" * 40}, {"exact_next_action": "Substitute action"},
            {"state_path": original["run_root_identity"] + "/STATE.md"},
            {"pointer_oid": "9" * 40}, {"receipt_oid": "9" * 40}, {"migration_marker_oid": "9" * 40},
        )]
        before = A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)")
        for index, changed in enumerate(mutations):
            self.subject["predecessor"] = changed
            with self.subTest(mutation=index), self.assertRaises(H.RotationError):
                H.prepare_native_resume_draft(self.subject["repo"], self.subject["run"], original["controller"], "G0003", changed)
            self.assertEqual(A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)"), before)
            self.assertFalse((self.subject["run"] / "state-generations/G0003").exists())
        self.subject["predecessor"] = original

    def test_native_resume_refuses_changed_referenced_artifact_before_archive(self):
        path = self.subject["run"] / "WORK_GRAPH.json"
        path.write_bytes(path.read_bytes() + b"\nChanged native owner frontier bytes.\n")
        before = A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)")
        with self.assertRaises(H.RotationError):
            self.prepare_native()
        self.assertEqual(A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)"), before)
        self.assertFalse((self.subject["run"] / "state-generations/G0003").exists())

    def test_native_resume_refuses_pointer_drift_during_source_capture(self):
        original_read = H.read_canonical_generation
        s = self.subject

        def drift(repo, run, pointer):
            resolved = original_read(repo, run, pointer)
            changed = H._store_blob(repo, b"Constructed competing pointer uncertainty")
            A.git(repo, "update-ref", s["predecessor"]["pointer_ref"], changed, s["predecessor"]["pointer_oid"])
            return resolved

        with mock.patch.object(H, "read_canonical_generation", side_effect=drift), self.assertRaises(H.RotationError):
            self.prepare_native()
        self.assertFalse((s["run"] / "state-generations/G0003").exists())
        self.assertIsNone(H._ref(s["repo"], H._identity(s["predecessor"]["controller"], "G0003"), absent=True))

    def test_native_derived_map_cannot_follow_an_aliased_generation_directory(self):
        target = Path(self.temp.name) / "unrelated"
        target.mkdir()
        os.symlink(target, self.subject["run"] / "state-generations/G0003", target_is_directory=True)
        before = self.authority_refs()
        with self.assertRaises(H.RotationError):
            self.prepare_native()
        self.assertEqual(list(target.iterdir()), [])
        self.assertEqual(self.authority_refs(), before)
        self.assertIsNone(H._ref(self.subject["repo"], H._identity(self.subject["predecessor"]["controller"], "G0003"), absent=True))

    def test_native_resume_rejects_transition_substitution_without_current_effects(self):
        prepared = self.prepare_native()
        transition = helper_native_transition(self.subject)
        fields = [{key: value for key, value in transition.items() if key != missing} for missing in transition]
        fields += [dict(transition, **changed) for changed in (
            {"schema": "implementaudit.rotation-transition.v1"}, {"boundary": "canonical-state-rotation"},
            {"boundary": []}, {"transition_kind": "rotation"}, {"transition_kind": "recovery"},
            {"payload_source": "draft"}, {"failed_transition_epoch": "G0003"},
            {"failed_transition_generation": "G0003"}, {"failed_transition_receipt_ref_oid": transition["predecessor_receipt_ref_oid"]},
            {"continuity_epoch": "G0002"}, {"projection_generation_id": "G0002"},
            {"predecessor_receipt_ref_oid": transition["predecessor_receipt_ref_oid"][:-40] + "9" * 40},
            {"future_receipt_oid": "a" * 40}, {"pointer_oid": "a" * 40}, {"head": "9" * 40},
        )]
        before = self.authority_refs()
        for index, changed in enumerate(fields):
            with self.subTest(mutation=index), self.assertRaises(H.RotationError):
                H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], prepared, changed)
        self.assertEqual(self.authority_refs(), before)
        self.assertFalse((self.subject["run"] / "state-generations/G0003/STATE.md").exists())

    def test_native_draft_interrupt_and_preparation_kind_substitution_fail_closed(self):
        prepared = self.prepare_native()
        transition = helper_native_transition(self.subject)
        before = self.authority_refs()
        altered = dict(prepared, schema="implementaudit.canonical-prepared.v2")
        with self.assertRaises(H.RotationError):
            H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], altered, transition)
        path = self.subject["run"] / prepared["draft_path"] / "STATE.md"
        path.chmod(0o644)
        path.write_bytes(b"Constructed interrupted draft write.\n")
        path.chmod(0o444)
        with self.assertRaises(H.RotationError):
            H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], prepared, transition)
        with self.assertRaises(H.RotationError):
            self.prepare_native()
        self.assertEqual(self.authority_refs(), before)
        H.verify_canonical_archive(self.subject["repo"], prepared["controller"], prepared["archive_ref"], prepared["archive_manifest_sha256"])

    def test_native_archive_kind_and_derived_map_path_are_exact(self):
        prepared = self.prepare_native()
        original = H.verify_canonical_archive(self.subject["repo"], prepared["controller"], prepared["archive_ref"],
                                               prepared["archive_manifest_sha256"])
        changes = [lambda m: m.pop("preparation_kind"), lambda m: m.update(preparation_kind="rotation"),
                   lambda m: m.update(preparation_kind="unknown")]
        for path in ("state-generations/G0002/native-resume-owner-map.json", "rotation-owner-map.json",
                     "../native-resume-owner-map.json", "state-generations/G0003/draft/owner-map.json"):
            changes.append(lambda m, path=path: next(row for row in m["entries"] if row["role"] == "OWNER_MAP").update(source_path=path))
        for index, mutate in enumerate(changes):
            manifest = copy.deepcopy(original)
            mutate(manifest)
            raw = H.canonical_bytes(manifest)
            oid = H._store_blob(self.subject["repo"], raw)
            A.git(self.subject["repo"], "update-ref", prepared["archive_ref"], oid, prepared["archive_manifest_oid"])
            with self.subTest(mutation=index), self.assertRaises(H.RotationError):
                H.verify_canonical_archive(self.subject["repo"], prepared["controller"], prepared["archive_ref"], H.sha256(raw))
            A.git(self.subject["repo"], "update-ref", prepared["archive_ref"], prepared["archive_manifest_oid"], oid)

    def test_completed_native_preparation_is_reusable_by_exact_readback_only(self):
        prepared = self.prepare_native()
        before = A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)")
        with mock.patch.object(H, "_store_blob", side_effect=AssertionError("reuse wrote a Git blob")), \
             mock.patch.object(H, "_write_verified", side_effect=AssertionError("reuse wrote a file")), \
             mock.patch.object(H, "_mkdir", side_effect=AssertionError("reuse changed directory population")):
            self.assertEqual(self.prepare_native(), prepared)
        self.assertEqual(A.git(self.subject["repo"], "for-each-ref", "--format=%(refname) %(objectname)"), before)
        transition = helper_native_transition(self.subject, "manual-resume")
        output = H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], prepared, transition)
        with self.assertRaises(H.RotationError):
            self.prepare_native()
        self.assertEqual(H.read_canonical_generation(self.subject["repo"], self.subject["run"], output["pointer"])
                          ["protected_manifest"]["MONOTONIC_TRANSITION"]["boundary"], "manual-resume")

    def test_native_generations_retain_complete_archive_guard_population_after_gc(self):
        prepared = self.prepare_native()
        output = H.finalize_canonical_projection(self.subject["repo"], self.subject["run"], prepared,
                                                 helper_native_transition(self.subject))
        fixture_commit_pointer(self.subject, output["pointer"])
        prepared = self.prepare_native()
        expected = H.archive_retention_guards(self.subject["repo"], prepared["controller"], prepared["archive_ref"],
                                              prepared["archive_manifest_sha256"])
        for epoch in ("G0002", "G0003", "G0004"):
            self.assertIn(H._identity(prepared["controller"], epoch), expected)
        for ref in [ref for ref in expected if "/objects/" not in ref]:
            manifest = H._json(H._blob(self.subject["repo"], expected[ref]), "guarded archive")
            for entry in manifest["entries"]:
                self.assertEqual(expected[H.ARCHIVE_PREFIX + "/" + prepared["controller"] + "/objects/" + entry["blob_oid"]], entry["blob_oid"])
        A.git(self.subject["repo"], "gc", "--prune=now")
        self.assertEqual(H.archive_retention_guards(self.subject["repo"], prepared["controller"], prepared["archive_ref"],
                                                    prepared["archive_manifest_sha256"]), expected)
        resolved = H.read_canonical_generation(self.subject["repo"], self.subject["run"], self.subject["pointer"])
        for pointer in resolved["protected_manifest"]["ARCHIVED_ONLY_HISTORY"]:
            self.assertEqual(H.resolve_typed_archive_pointer_v2(self.subject["repo"], pointer)["authority_ceiling"], "ARCHIVED_ONLY_HISTORY")

    def test_retention_guard_handoff_refuses_drift_after_complete_walk(self):
        prepared = self.prepare_native()
        original = H._verify_retained_archives

        def drift(repo, preimage):
            guards = original(repo, preimage)
            ref = next(ref for ref in guards if "/objects/" in ref)
            A.git(repo, "update-ref", "-d", ref, guards[ref])
            return guards

        with mock.patch.object(H, "_verify_retained_archives", side_effect=drift), self.assertRaises(H.RotationError):
            H.archive_retention_guards(self.subject["repo"], prepared["controller"], prepared["archive_ref"],
                                        prepared["archive_manifest_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
