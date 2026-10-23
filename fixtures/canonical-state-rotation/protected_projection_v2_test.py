#!/usr/bin/env python3
"""R0039 typed-source qualification controls; not native history/currentness proof."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "skills/implementaudit/scripts/canonical_hot_projection.py"
FIXTURE = pathlib.Path(__file__).with_name("v2") / "source.json"
SPEC = importlib.util.spec_from_file_location("protected_projection_under_test", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUTHORITY = "NO_CURRENTNESS_AUTHORITY"
LIMITS = {"max_state_bytes": 100000, "max_roadmap_bytes": 100000}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw, algorithm="sha1"):
    return hashlib.new(algorithm, b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def escape(value):
    return value.replace("~", "~0").replace("/", "~1")


def leaves(value, pointer=""):
    if isinstance(value, dict) and value:
        for key in sorted(value):
            yield from leaves(value[key], pointer + "/" + escape(key))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from leaves(child, pointer + "/" + str(index))
    else:
        yield pointer, value


def render_pair(bodies):
    result = {}
    action = bodies["STATE"]["payload"]["continuation"]["value"]["next_action"]
    identity = bodies["STATE"]["payload"]["identity"]["value"]
    for role in ("STATE", "ROADMAP"):
        body = bodies[role]
        current = body["transition"] or body["continuity"]
        text = ("# IMPLEMENTAUDIT " + role.title() + "\n\n"
                + "Current epoch: " + current["continuity_epoch"] + "\n"
                + "Canonical projection generation: " + current["projection_generation_id"] + "\n\n"
                + "| Field | Value |\n|---|---|\n| Next action | " + action + " |\n\n"
                + "## Context epochs and instruction applicability\n\n"
                + "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n"
                + "|---|---|---|---|---|---|\n"
                + "| " + current["continuity_epoch"] + " | " + current["boundary"] + " | not measured | `"
                + identity["candidate"] + "` / `" + identity["tree"] + "` | yes | exact source facts |\n\n```json\n")
        result[role] = text.encode() + canonical(body) + b"\n```\n"
    return result


def build_owner_map(bodies, raw, artifacts):
    rows = []
    for role in ("STATE", "ROADMAP"):
        for name, group in bodies[role]["payload"].items():
            for pointer, value in leaves(group, "/payload/" + escape(name)):
                rows.append({"field": "/" + role + pointer, "owner": group["owner"],
                             "source_kind": "PAIR", "source_id": role,
                             "source_pointer": pointer, "source_sha256": sha(raw[role]),
                             "value_sha256": sha(canonical(value))})
        for ref in bodies[role]["artifact_refs"]:
            digest = sha(artifacts[ref["artifact_id"]])
            rows.append({"field": "/artifacts/" + ref["artifact_id"], "owner": ref["owner"],
                         "source_kind": "ARTIFACT", "source_id": ref["artifact_id"],
                         "source_pointer": "", "source_sha256": digest, "value_sha256": digest})
    return sorted(rows, key=lambda row: row["field"])


def fixture_pair(bodies=None, artifact_texts=None):
    fixture = json.loads(FIXTURE.read_text())
    bodies = copy.deepcopy(bodies or fixture["bodies"])
    texts = artifact_texts or fixture["artifact_texts"]
    artifacts = {key: value.encode() for key, value in texts.items()}
    raw = render_pair(bodies)
    identity = bodies["STATE"]["payload"]["identity"]["value"]
    current = bodies["STATE"]["transition"] or bodies["STATE"]["continuity"]
    action = bodies["STATE"]["payload"]["continuation"]["value"]["next_action"]
    if current["expected_receipt_schema"].endswith(".v2"):
        fields = ["implementaudit.continuity-receipt.v2", identity["controller_id"], "e" * 40,
                  identity["claim_id"], identity["candidate"], identity["tree"],
                  sha(raw["STATE"]), sha(raw["ROADMAP"]), current["invalidation_oid"] or "none",
                  current["boundary"], current["continuity_epoch"], action]
    else:
        fields = ["implementaudit.continuity-receipt.v3", identity["controller_id"],
                  identity["claim_id"], identity["run_root_identity"], current["continuity_epoch"],
                  current["invalidation_oid"], "refs/implementaudit/current-generations/" + identity["controller_id"],
                  "f" * 40, sha(raw["STATE"]), sha(raw["ROADMAP"]), "9" * 64, "8" * 64,
                  action, current["predecessor_receipt_ref_oid"]]
    artifacts["receipt"] = ("\t".join(fields) + "\n").encode()
    return raw["STATE"], raw["ROADMAP"], build_owner_map(bodies, raw, artifacts), artifacts


def fixture_bodies():
    return json.loads(FIXTURE.read_text())["bodies"]


def native_profile_bodies(status="IN_PHASE"):
    bodies = fixture_bodies()
    continuation = bodies["STATE"]["payload"]["continuation"]["value"]
    continuation["status"] = status
    for role in ("STATE", "ROADMAP"):
        lines = ["# " + role, "", "Exact owner-bound native guard text.", "Status: pending"]
        if role == "STATE":
            lines += ["| Status | " + status + " |",
                      "| Next action | " + continuation["next_action"] + " |"]
        bodies[role]["payload"]["native_guards"] = {
            "owner": role + ".md",
            "value": {"schema_version": "implementaudit.native-guard-profile.v1", "lines": lines}}
    return bodies


def archive_pointers(preimage, preparation_generation_id="G0002"):
    controller = preimage["payload"]["STATE"]["identity"]["value"]["controller_id"]
    return [{**copy.deepcopy(row), "schema_version": "implementaudit.typed-archive-pointer.v2",
             "archive_ref": "refs/implementaudit/state-archives/" + controller + "/" + preparation_generation_id,
             "preparation_generation_id": preparation_generation_id,
             "archive_manifest_oid": "7" * 40, "archive_manifest_sha256": "6" * 64,
             "authority": "ARCHIVED_ONLY_HISTORY"} for row in preimage["archive_population"]]


def successor(preimage, recovery=False):
    current = preimage["current_continuity"]
    controller = preimage["payload"]["STATE"]["identity"]["value"]["controller_id"]
    def plus(value, increment):
        return "G%04X" % (int(value[1:], 16) + increment)
    epoch = plus(current["continuity_epoch"], 2 if recovery else 1)
    return {"schema_version": "implementaudit.canonical-state-transition.v2",
            "boundary": "canonical-state-rotation", "reconciled": True, "transition_kind": "recovery" if recovery else "rotation",
            "predecessor_generation_id": current["projection_generation_id"],
            "projection_generation_id": plus(current["projection_generation_id"], 2 if recovery else 1),
            "predecessor_epoch": current["continuity_epoch"], "continuity_epoch": epoch,
            "failed_transition_receipt_ref_oid": None,
            "failed_transition_epoch": plus(current["continuity_epoch"], 1) if recovery else None,
            "failed_projection_generation_id": plus(current["projection_generation_id"], 1) if recovery else None,
            "invalidation_oid": "5" * 40,
            "predecessor_receipt_ref_oid": preimage["current_receipt_ref_oid"],
            "expected_receipt_ref": "refs/implementaudit/continuity-receipts/" + controller + "/" + epoch,
            "expected_receipt_schema": "implementaudit.continuity-receipt.v3"}


class ProjectionV2Qualification(unittest.TestCase):
    def setUp(self):
        if not hasattr(MODULE, "parse_canonical_pair_v2"):
            self.fail("R0039_PROJECTION_V2_MISSING: complete source-bound protected pair preservation is unavailable")
        self.state, self.roadmap, self.owner_map, self.artifacts = fixture_pair()

    def parse(self, pair=None):
        state, roadmap, owners, artifacts = pair or (self.state, self.roadmap, self.owner_map, self.artifacts)
        return MODULE.parse_canonical_pair_v2(state, roadmap, owner_map=owners, artifacts=artifacts)

    def project(self, preimage=None, transition=None, pointers=None, limits=None):
        preimage = preimage or self.parse()
        return MODULE.derive_hot_pair_v2(preimage, transition=transition,
                   archive_pointers=pointers if pointers is not None else archive_pointers(preimage),
                   **(limits or LIMITS))

    def rejects(self, function, *args, **kwargs):
        with self.assertRaises(MODULE.ProjectionV2Error):
            function(*args, **kwargs)

    def test_paired_native_guard_lines_preserve_exact_native_status_and_action(self):
        for status in ("open", "READY_TO_DISPATCH", "IN_PHASE", "PAUSED", "BLOCKED", "INTERRUPTED", "DONE"):
            with self.subTest(status=status):
                preimage = self.parse(fixture_pair(native_profile_bodies(status)))
                result = self.project(preimage)
                self.assertEqual(result["payload"], preimage["payload"])
                for role in ("STATE", "ROADMAP"):
                    self.assertEqual(len(result[role.lower() + "_bytes"].decode().split("\n")), 19)
                    self.assertEqual(result["payload"][role]["native_guards"], preimage["payload"][role]["native_guards"])
                self.assertEqual(result["authority_ceiling"], AUTHORITY)

    def test_native_guard_profile_schema_and_mirrors_refuse_ambiguity(self):
        mutations = [
            lambda b: b["ROADMAP"]["payload"].pop("native_guards"),
            lambda b: b["STATE"]["payload"]["native_guards"].update(owner="ROADMAP.md"),
            lambda b: b["STATE"]["payload"]["native_guards"]["value"].update(schema_version="unknown"),
            lambda b: b["STATE"]["payload"]["native_guards"]["value"].update(future_grant=True),
            lambda b: b["STATE"]["payload"]["native_guards"]["value"].update(lines=[]),
            lambda b: b["ROADMAP"]["payload"]["native_guards"]["value"].update(lines="untyped"),
            lambda b: b["STATE"]["payload"]["continuation"]["value"].update(status="ACTIVE"),
            lambda b: b["STATE"]["payload"]["continuation"]["value"].update(next_action="Substituted action"),
        ]
        for extra in ("| Status | IN_PHASE |", "| Status | DONE |", "| Next action | other |",
                      " |  Status  | IN_PHASE |", "Current epoch: G0002", " current EPOCH : G0002",
                      "embedded\rreturn", "embedded\nline", "embedded\0nul", 7):
            mutations.append(lambda b, extra=extra: b["STATE"]["payload"]["native_guards"]["value"]["lines"].append(extra))
        mutations.append(lambda b: b["ROADMAP"]["payload"]["native_guards"]["value"]["lines"].append("Current epoch: G0002"))
        for index, mutate in enumerate(mutations):
            bodies = native_profile_bodies()
            mutate(bodies)
            with self.subTest(mutation=index):
                self.rejects(self.parse, fixture_pair(bodies))

    def test_every_native_guard_leaf_is_in_complete_owner_and_equivalence_population(self):
        pair = fixture_pair(native_profile_bodies())
        preimage = self.parse(pair)
        result = self.project(preimage)
        native_rows = [(index, row) for index, row in enumerate(pair[2]) if "/native_guards/" in row["field"]]
        self.assertGreater(len(native_rows), 10)
        for index, row in native_rows:
            with self.subTest(field=row["field"], omission=True):
                self.rejects(self.parse, (pair[0], pair[1], pair[2][:index] + pair[2][index+1:], pair[3]))
            changed = copy.deepcopy(result)
            role = row["source_id"]
            target = changed["payload"][role]
            parts = row["source_pointer"].split("/")[2:]
            for part in parts[:-1]:
                target = target[int(part)] if isinstance(target, list) else target[part]
            key = int(parts[-1]) if isinstance(target, list) else parts[-1]
            target[key] = str(target[key]) + " changed"
            with self.subTest(field=row["field"], mutation=True):
                self.rejects(MODULE.verify_projection_equivalence_v2, preimage, changed)

    def test_complete_pair_preservation_and_draft_without_successor(self):
        preimage = self.parse()
        candidate = self.project(preimage)
        self.assertEqual(candidate["payload"], preimage["payload"])
        self.assertEqual(candidate["transition"], None)
        self.assertEqual(candidate["authority_ceiling"], AUTHORITY)
        self.assertEqual(preimage["authority_ceiling"], AUTHORITY)
        self.assertEqual(len(preimage["archive_population"]), 4)
        self.assertEqual(len(preimage["owner_map"]), 222)
        for raw in (candidate["state_bytes"], candidate["roadmap_bytes"]):
            self.assertIn(b"Current epoch: G0001\n", raw)
            self.assertNotIn(b'"pointer_oid"', raw)
            self.assertNotIn(b'"receipt_oid"', raw)
        checked = MODULE.verify_projection_equivalence_v2(preimage, candidate)
        self.assertTrue(checked["equivalent"])
        self.assertEqual(checked["authority_ceiling"], AUTHORITY)
        self.assertEqual(candidate, self.project(preimage))

    def test_each_protected_leaf_requires_exact_owner_and_value_evidence(self):
        preimage = self.parse()
        pair_rows = [row for row in self.owner_map if row["source_kind"] == "PAIR"]
        self.assertTrue(MODULE.validate_protected_payload_v2(preimage["payload"], pair_rows))
        for index, original in enumerate(pair_rows):
            with self.subTest(field=original["field"], mutation="missing"):
                self.rejects(MODULE.validate_protected_payload_v2, preimage["payload"], pair_rows[:index] + pair_rows[index+1:])
            for name, bad in (("owner", "ROADMAP.md" if original["owner"] != "ROADMAP.md" else "STATE.md"),
                              ("value_sha256", "0" * 64), ("source_pointer", "/wrong")):
                rows = copy.deepcopy(pair_rows)
                rows[index][name] = bad
                with self.subTest(field=original["field"], mutation=name):
                    self.rejects(MODULE.validate_protected_payload_v2, preimage["payload"], rows)

    def test_source_pair_and_owner_map_denominator_are_not_caller_assertions(self):
        for field in ("source_sha256", "source_id", "field"):
            owners = copy.deepcopy(self.owner_map)
            owners[0][field] = "0" * 64 if field == "source_sha256" else "wrong"
            self.rejects(self.parse, (self.state, self.roadmap, owners, self.artifacts))
        for owners in (self.owner_map + [self.owner_map[0]], self.owner_map[:-1],
                       self.owner_map + [{"fully_mapped": True}]):
            self.rejects(self.parse, (self.state, self.roadmap, owners, self.artifacts))
        artifacts = dict(self.artifacts); del artifacts["evidence"]
        owners = [row for row in self.owner_map if row["source_id"] != "evidence"]
        self.rejects(self.parse, (self.state, self.roadmap, owners, artifacts))
        artifacts = dict(self.artifacts, extra=b"unmapped")
        self.rejects(self.parse, (self.state, self.roadmap, self.owner_map, artifacts))

    def test_legacy_extra_unknown_noncanonical_and_duplicate_json_fail_closed(self):
        for state in (b"# STATE\nHistorical narrative and unknown live obligation\n", self.state+b"unparsed\n",
                      b"\xef\xbb\xbf"+self.state, self.state.replace(b"\n", b"\r\n"),
                      self.state.replace(b'"pair_id":', b'"pair_id":"duplicate","pair_id":', 1)):
            self.rejects(self.parse, (state, self.roadmap, self.owner_map, self.artifacts))
        for role in ("STATE", "ROADMAP"):
            bodies = fixture_bodies(); bodies[role]["unknown"] = "Must not silently become historical"
            self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); del bodies["STATE"]["payload"]["steers"]
        self.rejects(self.parse, fixture_pair(bodies))
        self.rejects(self.parse, (self.roadmap, self.state, self.owner_map, self.artifacts))

    def test_closed_state_vocabularies_and_frontier_population(self):
        paths = [("STATE", "continuation", "status"), ("STATE", "rollback", "status")]
        for role, group, key in paths:
            bodies = fixture_bodies(); bodies[role]["payload"][group]["value"][key] = "SUCCESS_ISH"
            self.rejects(self.parse, fixture_pair(bodies))
        for group in ("instructions", "authorisations", "andons", "original_reds", "non_verdicts", "evidence_ceilings", "steers"):
            bodies = fixture_bodies(); bodies["STATE"]["payload"][group]["value"][0]["status"] = "UNKNOWN_NEW_STATE"
            self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); bodies["ROADMAP"]["payload"]["frontier"]["value"]["QUEUED"] = []
        self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); bodies["ROADMAP"]["payload"]["frontier"]["value"]["READY"] = ["phase-1"]
        self.rejects(self.parse, fixture_pair(bodies))

    def test_every_protected_leaf_change_is_detected_against_immutable_preimage(self):
        preimage = self.parse(); candidate = self.project(preimage)
        for role in ("STATE", "ROADMAP"):
            for pointer, value in leaves(candidate["payload"][role]):
                changed = copy.deepcopy(candidate)
                target = changed["payload"][role]
                segments = [segment.replace("~1", "/").replace("~0", "~") for segment in pointer.split("/")[1:]]
                for segment in segments[:-1]:
                    target = target[int(segment)] if isinstance(target, list) else target[segment]
                key = int(segments[-1]) if isinstance(target, list) else segments[-1]
                target[key] = not value if type(value) is bool else "SEMANTIC_CHANGE"
                with self.subTest(role=role, leaf=pointer):
                    self.rejects(MODULE.verify_projection_equivalence_v2, preimage, changed)
        changed = copy.deepcopy(candidate); del changed["payload"]["STATE"]["pending_boundaries"]
        self.rejects(MODULE.verify_projection_equivalence_v2, preimage, changed)

    def test_changed_whole_pair_with_self_consistent_metadata_is_not_equivalent(self):
        preimage = self.parse()
        bodies = fixture_bodies(); bodies["STATE"]["payload"]["instructions"]["value"][0]["scope"] = "Widened scope"
        altered = self.parse(fixture_pair(bodies)); forged = self.project(altered)
        self.rejects(MODULE.verify_projection_equivalence_v2, preimage, forged)
        changed = copy.deepcopy(preimage); changed["payload"]["STATE"]["steers"]["value"] = []
        self.rejects(self.project, changed)

    def test_typed_history_has_complete_exact_retrieval_pointers(self):
        preimage = self.parse(); candidate = self.project(preimage)
        pointers = archive_pointers(preimage)
        for row in pointers:
            raw = self.state if row["source_role"] == "STATE" else self.roadmap
            self.assertEqual(row["source_sha256"], sha(raw)); self.assertEqual(row["blob_oid"], blob(raw))
            self.assertEqual(row["source_bytes"], len(raw))
        self.assertEqual(candidate["archive_pointers"], pointers)
        self.rejects(self.project, preimage, pointers=pointers[:-1])
        self.rejects(self.project, preimage, pointers=pointers+[pointers[-1]])
        for field, value in (("record_sha256", "0"*64), ("source_pointer", "/history/999"),
                             ("blob_oid", "0"*40), ("authority", "CURRENT"),
                             ("archive_ref", pointers[0]["archive_ref"]+"/objects")):
            bad = copy.deepcopy(pointers); bad[0][field] = value
            self.rejects(self.project, preimage, pointers=bad)
        text = candidate["state_bytes"].decode()
        self.assertNotIn('"history":[{', text)
        self.assertIn("TC11-admission-history", text)
        self.assertEqual(preimage["bodies"]["STATE"]["history"][0]["payload"]["current_applicability"], "INVALIDATED_CURRENT_USE")

    def test_tc06_existing_archive_remains_when_followup_rotation_is_unavailable(self):
        first = self.parse(); old = archive_pointers(first)
        bodies = fixture_bodies(); bodies["STATE"]["archive_pointers"] = old
        second = self.parse(fixture_pair(bodies)); candidate = self.project(second)
        for pointer in old:
            self.assertIn(pointer, candidate["archive_pointers"])
        self.assertTrue(MODULE.verify_projection_equivalence_v2(second, candidate)["equivalent"])

    def test_rotation_transition_and_recovery_skip_only_exact_failed_allocation(self):
        preimage = self.parse(); transition = successor(preimage)
        candidate = self.project(preimage, transition)
        self.assertIn(b"Current epoch: G0002\n", candidate["state_bytes"])
        self.assertEqual(candidate["predecessor_continuity"], preimage["current_continuity"])
        self.assertEqual(candidate["transition"]["predecessor_receipt_ref_oid"], preimage["current_continuity"]["expected_receipt_ref"]+"@"+blob(self.artifacts["receipt"]))
        recovery = successor(preimage, recovery=True); recovered = self.project(preimage, recovery)
        self.assertIn(b"Current epoch: G0003\n", recovered["state_bytes"])
        self.assertEqual(recovered["transition"]["failed_transition_epoch"], "G0002")
        self.assertEqual(recovered["transition"]["predecessor_receipt_ref_oid"], preimage["current_continuity"]["expected_receipt_ref"]+"@"+blob(self.artifacts["receipt"]))
        for field, value in (("continuity_epoch", "G0004"), ("projection_generation_id", "G0003"),
                             ("predecessor_receipt_ref_oid", "1"*40), ("invalidation_oid", "a"*40),
                             ("expected_receipt_ref", transition["expected_receipt_ref"]+"/extra"),
                             ("future_receipt_oid", "2"*40)):
            bad = dict(transition); bad[field] = value
            self.rejects(self.project, preimage, bad)
        bad = dict(recovery); bad["failed_transition_epoch"] = None
        self.rejects(self.project, preimage, bad)
        bad = dict(transition); bad["failed_projection_generation_id"] = "G0002"
        self.rejects(self.project, preimage, bad)

    def test_native_epoch_bridge_and_recovery_with_actual_failed_receipt_token(self):
        preimage = self.parse()
        self.assertIn(b"| G0001 | handoff-resume | not measured |", self.state)
        self.assertTrue(preimage["current_continuity"]["reconciled"])
        recovery = successor(preimage, recovery=True)
        failed = "refs/implementaudit/continuity-receipts/r0039-fixture/G0002@" + "2"*40
        recovery["failed_transition_receipt_ref_oid"] = failed
        recovery["predecessor_receipt_ref_oid"] = failed
        candidate = self.project(preimage, recovery)
        self.assertEqual(candidate["payload"], preimage["payload"])
        self.assertEqual(candidate["transition"]["predecessor_receipt_ref_oid"], failed)
        self.assertIn(b"| G0003 | canonical-state-rotation | not measured |", candidate["state_bytes"])
        for changed in (failed.replace("G0002", "G0004"), failed.replace("r0039-fixture", "other-controller"), "2"*40):
            bad = dict(recovery); bad["failed_transition_receipt_ref_oid"] = changed; bad["predecessor_receipt_ref_oid"] = changed
            self.rejects(self.project, preimage, bad)
        bad = dict(recovery); bad["predecessor_receipt_ref_oid"] = preimage["current_receipt_ref_oid"]
        self.rejects(self.project, preimage, bad)
        bad = dict(successor(preimage)); bad["failed_transition_receipt_ref_oid"] = failed
        self.rejects(self.project, preimage, bad)

    def test_receipt_is_external_exact_byte_bound_and_preserves_identity(self):
        preimage = self.parse()
        self.assertNotIn(blob(self.artifacts["receipt"]).encode(), self.state)
        self.assertEqual(preimage["current_receipt_ref_oid"], preimage["current_continuity"]["expected_receipt_ref"]+"@"+blob(self.artifacts["receipt"]))
        artifacts = dict(self.artifacts); fields = artifacts["receipt"].decode().rstrip("\n").split("\t")
        for index in (1, 3, 6, 7, 8, 10, 11):
            bad = fields[:]; bad[index] = "wrong"
            artifacts["receipt"] = ("\t".join(bad)+"\n").encode()
            owners = build_owner_map(fixture_bodies(), {"STATE":self.state,"ROADMAP":self.roadmap}, artifacts)
            self.rejects(self.parse, (self.state,self.roadmap,owners,artifacts))
        bodies = fixture_bodies()
        for body in bodies.values():
            body["continuity"].update(expected_receipt_schema="implementaudit.continuity-receipt.v3",
                continuity_epoch="G0002", projection_generation_id="G0002",
                predecessor_receipt_ref_oid="refs/implementaudit/continuity-receipts/r0039-fixture/G0001@"+"b"*40,
                expected_receipt_ref="refs/implementaudit/continuity-receipts/r0039-fixture/G0002")
            for ref in body["artifact_refs"]:
                if ref["role"] == "CONTINUITY_RECEIPT": ref["locator"] = body["continuity"]["expected_receipt_ref"]
        v3 = self.parse(fixture_pair(bodies))
        self.assertEqual(v3["authority_ceiling"], AUTHORITY)

    def test_safe_artifact_dependencies_are_derived_from_complete_pair(self):
        for locator in ("../evidence", "/absolute", "C:/drive", "safe/../escape", "safe\\escape", "safe//file", "./file"):
            bodies = fixture_bodies(); bodies["STATE"]["artifact_refs"][1]["locator"] = locator
            self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); bodies["STATE"]["payload"]["runtime_artifacts"]["value"] = ["receipt", "work_graph", "missing"]
        self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); bodies["STATE"]["payload"]["instructions"]["value"][0]["evidence_refs"] = ["missing"]
        self.rejects(self.parse, fixture_pair(bodies))

    def test_pending_boundaries_keep_unresolved_epoch_and_required_rehydration(self):
        preimage = self.parse(); candidate = self.project(preimage)
        rows = candidate["payload"]["STATE"]["pending_boundaries"]["value"]
        self.assertEqual(rows, preimage["payload"]["STATE"]["pending_boundaries"]["value"])
        self.assertEqual(rows[0]["observation"], rows[1]["observation"])
        self.assertNotEqual(rows[0]["physical_source"], rows[1]["physical_source"])
        for row in rows:
            self.assertEqual(row["currentness"], {"state":"UNRESOLVED", "epoch":None})
            self.assertTrue(row["audit_state_required"])
            self.assertEqual(row["consumption"]["state"], "PENDING")
        bodies = fixture_bodies(); bodies["STATE"]["payload"]["pending_boundaries"]["value"][0]["audit_state_required"] = False
        self.rejects(self.parse, fixture_pair(bodies))

    def test_reservation_failed_result_and_later_correct_response_do_not_consume(self):
        for condition in ("reservation", "failed-result", "missing-witness"):
            bodies = fixture_bodies(); row = bodies["STATE"]["payload"]["pending_boundaries"]["value"][0]
            row["consumption"] = {"state":"ACCEPTED", "witness":None, "covered_boundary_ids":["boundary-1"]}
            if condition == "missing-witness": row["result"]["state"] = "SUCCEEDED"
            self.rejects(self.parse, fixture_pair(bodies))
        bodies = fixture_bodies(); row = bodies["STATE"]["payload"]["pending_boundaries"]["value"][0]
        row["result"] = {"state":"SUCCEEDED", "original_response_sha256":sha(b"wrong"), "returned_response_sha256":sha(b"later correct")}
        preimage = self.parse(fixture_pair(bodies)); candidate = self.project(preimage)
        retained = candidate["payload"]["STATE"]["pending_boundaries"]["value"][0]
        self.assertNotEqual(retained["result"]["original_response_sha256"], retained["result"]["returned_response_sha256"])
        self.assertEqual(retained["consumption"]["state"], "PENDING")

    def test_accepted_witness_covers_only_exact_observation_and_occurrence_scope(self):
        bodies = fixture_bodies(); row = bodies["STATE"]["payload"]["pending_boundaries"]["value"][0]
        row["result"] = {"state":"SUCCEEDED", "original_response_sha256":sha(b"bad"), "returned_response_sha256":sha(b"correct")}
        row["consumption"] = {"state":"ACCEPTED", "covered_boundary_ids":["boundary-1"],
            "witness":{"evidence_ref":"evidence", "sha256":sha(self.artifacts["evidence"]),
                       "observation_scope":"H0 bounded observation", "cutoff":4, "boundary_ids":["boundary-1"]}}
        preimage = self.parse(fixture_pair(bodies)); candidate = self.project(preimage)
        rows = candidate["payload"]["STATE"]["pending_boundaries"]["value"]
        self.assertEqual(rows[0]["consumption"]["covered_boundary_ids"], ["boundary-1"])
        self.assertEqual(rows[1]["consumption"]["state"], "PENDING")
        for key, value in (("cutoff",5), ("observation_scope","broader scope"), ("boundary_ids",["boundary-1","unobserved"])):
            changed = copy.deepcopy(bodies); changed["STATE"]["payload"]["pending_boundaries"]["value"][0]["consumption"]["witness"][key] = value
            self.rejects(self.parse, fixture_pair(changed))

    def test_physical_source_selected_occurrence_prior_retry_and_refusal_are_protected(self):
        bodies = fixture_bodies(); row = bodies["STATE"]["payload"]["pending_boundaries"]["value"][1]
        row["retry"] = {"state":"SUPPORTED_RETRY", "original_occurrence_id":"boundary-1", "supported_evidence_ref":"evidence"}
        preimage = self.parse(fixture_pair(bodies)); candidate = self.project(preimage)
        self.assertEqual(candidate["payload"], preimage["payload"])
        for key, value in (("offset",0), ("ordinal",True), ("source_binding","0"*64), ("sha256","0"*64)):
            changed = copy.deepcopy(bodies); changed["STATE"]["payload"]["pending_boundaries"]["value"][1]["physical_source"][key] = value
            self.rejects(self.parse, fixture_pair(changed))

    def test_explicit_bounds_and_pure_inputs(self):
        preimage = self.parse(); original = copy.deepcopy(preimage); pointers = archive_pointers(preimage)
        saved_pointers = copy.deepcopy(pointers); transition = successor(preimage); saved_transition = dict(transition)
        candidate = self.project(preimage, transition, pointers)
        self.assertEqual(preimage, original); self.assertEqual(pointers,saved_pointers); self.assertEqual(transition,saved_transition)
        for limits in ({"max_state_bytes":1,"max_roadmap_bytes":100000},
                       {"max_state_bytes":True,"max_roadmap_bytes":100000},
                       {"max_state_bytes":100000,"max_roadmap_bytes":0}):
            self.rejects(self.project, preimage, limits=limits)
        exact = {"max_state_bytes":len(candidate["state_bytes"]),"max_roadmap_bytes":len(candidate["roadmap_bytes"])}
        self.assertEqual(self.project(preimage,transition,pointers,exact)["state_bytes"],candidate["state_bytes"])

    def test_large_typed_history_reduces_with_complete_source_retrieval(self):
        bodies = fixture_bodies()
        bodies["STATE"]["history"][0]["payload"]["text"] = "Exact historical scope and original refusal. " * 3000
        preimage = self.parse(fixture_pair(bodies))
        candidate = self.project(preimage, limits={"max_state_bytes":20000,"max_roadmap_bytes":12000})
        self.assertLess(len(candidate["state_bytes"]),len(preimage["state_bytes"]))
        self.assertEqual(candidate["payload"],preimage["payload"])
        record = preimage["bodies"]["STATE"]["history"][0]
        pointer = next(row for row in candidate["archive_pointers"] if row["record_id"] == record["record_id"])
        self.assertEqual(pointer["record_sha256"],sha(canonical(record)))
        self.assertEqual(pointer["source_pointer"],"/history/0")
        self.assertEqual(pointer["source_sha256"],sha(preimage["state_bytes"]))
        self.assertTrue(MODULE.verify_projection_equivalence_v2(preimage,candidate)["equivalent"])

    def test_all_pending_state_vocabulary_is_closed(self):
        for group in ("reservation","result","consumption","historical_refusal","currentness","retry"):
            bodies = fixture_bodies()
            bodies["STATE"]["payload"]["pending_boundaries"]["value"][0][group]["state"] = "UNRECOGNIZED_STATE"
            with self.subTest(group=group): self.rejects(self.parse,fixture_pair(bodies))
        bodies = fixture_bodies()
        bodies["STATE"]["payload"]["pending_boundaries"]["value"][0]["currentness"] = {"state":"CURRENT","epoch":None}
        self.rejects(self.parse,fixture_pair(bodies))

    def test_epoch_table_mirror_mismatch_refuses_even_with_refreshed_receipt_and_owner_hashes(self):
        state = self.state.replace(b"| yes | exact source facts |",b"| no | exact source facts |",1)
        artifacts = dict(self.artifacts)
        fields = artifacts["receipt"].decode().rstrip("\n").split("\t"); fields[6] = sha(state)
        artifacts["receipt"] = ("\t".join(fields)+"\n").encode()
        owners = build_owner_map(fixture_bodies(),{"STATE":state,"ROADMAP":self.roadmap},artifacts)
        self.rejects(self.parse,(state,self.roadmap,owners,artifacts))

    def test_api_invocations_do_not_read_write_or_spawn(self):
        import os
        import subprocess
        from unittest import mock
        preimage = self.parse(); pointers = archive_pointers(preimage); transition = successor(preimage)
        fail = AssertionError("pure projection attempted filesystem or subprocess access")
        with mock.patch("builtins.open",side_effect=fail), mock.patch.object(os,"open",side_effect=fail), \
             mock.patch.object(subprocess,"Popen",side_effect=fail):
            reparsed = self.parse()
            candidate = self.project(reparsed,transition,pointers)
            self.assertTrue(MODULE.verify_projection_equivalence_v2(reparsed,candidate)["equivalent"])

    def test_review_v3_pointer_ref_binds_exact_role_and_source_controller(self):
        bodies = fixture_bodies()
        for body in bodies.values():
            body["continuity"].update(expected_receipt_schema="implementaudit.continuity-receipt.v3",
                continuity_epoch="G0002",projection_generation_id="G0002",
                predecessor_receipt_ref_oid="refs/implementaudit/continuity-receipts/r0039-fixture/G0001@"+"b"*40,
                expected_receipt_ref="refs/implementaudit/continuity-receipts/r0039-fixture/G0002")
            for ref in body["artifact_refs"]:
                if ref["role"] == "CONTINUITY_RECEIPT": ref["locator"] = body["continuity"]["expected_receipt_ref"]
        state,roadmap,owners,artifacts = fixture_pair(bodies)
        self.assertEqual(self.parse((state,roadmap,owners,artifacts))["current_continuity"]["continuity_epoch"],"G0002")
        for pointer_ref in ("refs/implementaudit/current-generations/other-controller",
                            "refs/implementaudit/continuity-receipts/r0039-fixture/G0002",
                            "refs/implementaudit/state-archives/r0039-fixture/G0002",
                            "refs/implementaudit/current-generations/r0039-fixture/extra"):
            changed = dict(artifacts)
            fields = changed["receipt"].decode()[:-1].split("\t"); fields[6] = pointer_ref
            changed["receipt"] = ("\t".join(fields)+"\n").encode()
            mapped = build_owner_map(bodies,{"STATE":state,"ROADMAP":roadmap},changed)
            with self.subTest(pointer_ref=pointer_ref): self.rejects(self.parse,(state,roadmap,mapped,changed))

    def test_review_supersession_targets_are_present_and_not_self(self):
        for group in ("instructions","authorisations"):
            for target in ("self","absent-record","oneshot-1"):
                bodies = fixture_bodies(); row = bodies["STATE"]["payload"][group]["value"][0]
                row["supersedes"] = [row["record_id"] if target == "self" else target]
                with self.subTest(group=group,target=target): self.rejects(self.parse,fixture_pair(bodies))

    def test_review_supersession_cycles_refuse_after_valid_closed_targets(self):
        bodies = fixture_bodies(); rows = bodies["STATE"]["payload"]["instructions"]["value"]
        rows[0]["supersedes"] = [rows[1]["record_id"]]
        rows[1]["supersedes"] = [rows[0]["record_id"]]
        self.rejects(self.parse,fixture_pair(bodies))
        bodies = fixture_bodies(); rows = bodies["STATE"]["payload"]["instructions"]["value"]
        authorisation = bodies["STATE"]["payload"]["authorisations"]["value"][0]
        rows[0]["supersedes"] = [rows[1]["record_id"]]
        rows[1]["supersedes"] = [authorisation["record_id"]]
        authorisation["supersedes"] = [rows[0]["record_id"]]
        self.rejects(self.parse,fixture_pair(bodies))

    def test_review_planning_actions_cannot_be_selected_and_omitted(self):
        bodies = fixture_bodies(); action = bodies["ROADMAP"]["payload"]["planning"]["value"]["action_selection"]
        action["omitted"].append(action["selected"][0])
        self.rejects(self.parse,fixture_pair(bodies))

    def test_review_compensation_subject_requires_one_existing_protected_record(self):
        for subject in ("absent-record","TC11-admission-history","phase-0","compensation-1"):
            bodies = fixture_bodies()
            bodies["ROADMAP"]["payload"]["compensations"]["value"][0]["for_record"] = subject
            with self.subTest(subject=subject): self.rejects(self.parse,fixture_pair(bodies))
        bodies = fixture_bodies()
        bodies["STATE"]["payload"]["andons"]["value"][0]["record_id"] = "oneshot-1"
        self.rejects(self.parse,fixture_pair(bodies))

    def test_review_compensation_cycles_refuse_with_existing_targets(self):
        bodies = fixture_bodies(); rows = bodies["ROADMAP"]["payload"]["compensations"]["value"]
        rows.append({**copy.deepcopy(rows[0]),"record_id":"compensation-2","for_record":"compensation-1"})
        rows[0]["for_record"] = "compensation-2"
        self.rejects(self.parse,fixture_pair(bodies))

    def test_valid_closed_relation_chains_preserve_exact_source_bound_values(self):
        bodies = fixture_bodies(); instructions = bodies["STATE"]["payload"]["instructions"]["value"]
        instructions[0]["supersedes"] = [instructions[1]["record_id"]]
        authorisations = bodies["STATE"]["payload"]["authorisations"]["value"]
        authorisations.append({**copy.deepcopy(authorisations[0]),"record_id":"authorisation-old","status":"SUPERSEDED"})
        authorisations[0]["supersedes"] = [authorisations[1]["record_id"]]
        compensations = bodies["ROADMAP"]["payload"]["compensations"]["value"]
        compensations.append({**copy.deepcopy(compensations[0]),"record_id":"compensation-2","for_record":"compensation-1"})
        preimage = self.parse(fixture_pair(bodies)); candidate = self.project(preimage)
        self.assertEqual(candidate["payload"],preimage["payload"])
        self.assertTrue(MODULE.verify_projection_equivalence_v2(preimage,candidate)["equivalent"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
