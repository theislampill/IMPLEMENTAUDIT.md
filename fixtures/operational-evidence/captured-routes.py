"""Constructed portable consumer controls; no native producer/authentication proof.

Run with --consumer /absolute/path/to/consumer-or-final-companion.py. No owner
module is imported, no native host/campaign custody is accessed, and the source
formats below are intentionally constructed data, not native receipts.
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock

_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--consumer", default=str(pathlib.Path(__file__).with_name("consumer.py")))
_args, _unittest_args = _parser.parse_known_args()
_path = pathlib.Path(_args.consumer)
if _path.is_file():
    _spec = importlib.util.spec_from_file_location("r0038_route_consumer_under_test", _path)
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    DECODE = getattr(_module, "decode_route_capture", None)
else:
    DECODE = None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def sha(value):
    return "sha256:" + digest(value)


CEILING = {
    "authority": "NONE", "canonical_currentness": False, "recovery_authority": False,
    "epoch_authority": False, "effect_authority": False, "independent_children": "UNCHANGED",
    "actual_child_result_consumer": "UNQUALIFIED", "same_failed_scope_retry": "CONDITIONAL_UNQUALIFIED",
}
SESSION = "constructed-session"
CODE = {"implementaudit/scripts/compaction-audit-pending.py": digest(b"CONSTRUCTED CODE PIN")}


def source():
    return {"path": "/constructed/unopened/rollout-task.jsonl", "task_id": "constructed-task",
            "session_id": SESSION, "sessions_root": "/constructed/unopened",
            "physical": {"device": 1, "inode": 2}, "session_meta_sha256": digest(b"CONSTRUCTED META"),
            "prefix_bytes": 1000, "prefix_sha256": digest(b"CONSTRUCTED PREFIX"),
            "provenance": "HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX",
            "native_producer_runtime_equivalence": "UNVERIFIED"}


def boundary(offset=100):
    src = source()
    proof = {"source": {k: src[k] for k in ("path", "task_id", "session_id", "session_meta_sha256", "physical", "sessions_root")},
             "markers": [{"ordinal": 1 + offset // 100, "offset": offset, "bytes": 20,
                          "sha256": digest(str(offset).encode()), "kind": "compacted", "canonical": True}],
             "resume": {"ordinal": 2 + offset // 100, "offset": offset + 20, "bytes": 20,
                        "sha256": digest(str(offset + 20).encode())},
             "resume_turn": "constructed-resume-" + str(offset),
             "native_producer_runtime_equivalence": "UNVERIFIED"}
    identifier = "boundary-" + digest(proof)
    return {"id": identifier, "kind": "COMPLETED_RESUMED_BOUNDARY", "version": 1,
            "consumed_version": 0, "proof": proof}


def scope(item):
    return {k: item[k] for k in ("id", "version", "kind")}


def pending(two=False):
    items = [boundary(100)] + ([boundary(400)] if two else [])
    return {"schema": "implementaudit.compaction-audit-pending.v1", "session_id": SESSION,
            "revision": 3, "source": source(), "source_problem": None, "signals": 0,
            "unresolved_signal_version": 0, "observations": {item["id"]: item for item in items},
            "assignments": {}, "active_child": None, "native_producer_runtime_equivalence": "UNVERIFIED"}


def assignment(state):
    item = next(iter(state["observations"].values()))
    observation = {"child_id": "constructed-child", "scope": [scope(item)], "code": CODE,
                   "source_cutoff": state["source"], "source_problem": None, "revision": 2}
    oid = digest(observation)
    proposal = {"status": "VERIFIED_LOGICAL_JOIN_PENDING_PROFILE", "child_id": "constructed-child",
                "return_digest": digest(b"CONSTRUCTED RETURN"), "proposed_consumption": [scope(item)],
                "projected_pending": [scope(v) for v in list(state["observations"].values())[1:]],
                "pending_consumed": False, "host_producer_authenticated": False,
                "profile": {"authenticating_source_owner": None}, "acquisition": {}, "acceptance": {}, **CEILING}
    state["assignments"]["constructed-child"] = {
        "child_id": "constructed-child", "scope": [scope(item)], "code": CODE,
        "observations": {oid: observation}, "return": {"child_id": "constructed-child",
        "observation_id": oid, "currentness": "UNRESOLVED", "measured_epoch": "UNRESOLVED",
        "status": "SUCCEEDED", **CEILING}, "join": None, "native_lifecycle": "NOT_CLAIMED",
        "reservation_request": {"child_id": "constructed-child"}, "policy": {},
        "logical_join": proposal,
    }
    return proposal


def decision(state):
    rows = [scope(item) for item in state["observations"].values() if item["version"] > item["consumed_version"]]
    return {"schema": "implementaudit.compaction-audit-decision.v1", **CEILING,
            "decision": "AUDIT_STATE_REQUIRED" if rows else "NO_PENDING_AUDIT",
            "audit_state_required": bool(rows), "state_dependent_decisions_held": bool(rows),
            "pending": rows, "available_scope": rows, "assigned_scope": [], "active_child": None,
            "active_children": [], "source_problem": None, "signal_observations": 0,
            "native_lifecycle": "NOT_CLAIMED", "native_producer_runtime_equivalence": "UNVERIFIED"}


def binding():
    return {"schema": "implementaudit.host-session-binding.v1", "host_id": "codex",
            "host_session_id": SESSION, "controller_id": "constructed-controller", "claim_id": "1" * 32,
            "explicit_run_root": "/constructed/run", "repository_identity": "/constructed/repo",
            "git_common_directory_identity": "/constructed/repo/.git", "worktree_identity": "/constructed/repo",
            "binding_generation": "G0001", "activation_event_id": "constructed-activation",
            "activation_receipt": "constructed-activation-receipt", "applicable_continuity_generation": "G0001",
            "applicable_continuity_receipt": "refs/implementaudit/continuity-receipts/constructed-controller/G0001@" + "1" * 40,
            "status": "ACTIVE", "predecessor_generation": None, "supersession_or_tombstone_reason": None}


def wire(value, identity=None):
    raw = value if isinstance(value, bytes) else canonical(value)
    result = {"bytes": len(raw), "digest": sha(raw), "bytes_b64": base64.b64encode(raw).decode()}
    if identity is not None:
        result["identity"] = identity
    return result


EXPIRES = ["action-completion", "next-action-change", "scope-change", "read-set-change",
           "host-binding-generation-change", "continuity-receipt-change", "package-identity-change",
           "child-source-identity-change", "owner-evidence-change", "authority-evidence-change",
           "dependency-evidence-change", "effect-evidence-change", "contradiction-or-invalidation", "scope-expansion"]


def route(state="UNSATISFIED", recovery=False):
    b = binding()
    packet = {"schema": "implementaudit.route-packet.v1", "obligation_id": sha(b"CONSTRUCTED OBLIGATION"),
              "route_transaction_id": sha(b"CONSTRUCTED TRANSACTION"), "target_identity": "audit-state",
              "source_event": {"schema": "implementaudit.source-event.v1", "source_identity": "constructed-event",
              "provenance": {"schema": "implementaudit.source-event-provenance.v1", "event_id": "constructed-event",
                             "host_correlation_id": sha(b"CONSTRUCTED CORRELATION")},
              "body": "CONSTRUCTED: keep source text, including `ini` and\nnewlines.", "kind": "one-shot-action",
              "reactivation": {"reopen": False, "target_changed": False, "invalidating_evidence": False}}}
    child = wire(b"CONSTRUCTED child source; never executable", "/constructed/audit-state/SKILL.md")
    r = {"schema": "implementaudit.route-decision.v1", "predicate_version": "R0033.route-predicate.v1",
         "controller_id": b["controller_id"], "claim_id": b["claim_id"], "explicit_run_root": b["explicit_run_root"],
         "continuity_generation": "G0001", "continuity_receipt": b["applicable_continuity_receipt"],
         "host_id": b["host_id"], "host_session_id": SESSION, "host_binding_generation": "G0001",
         "host_correlation_id": sha(b"CONSTRUCTED CORRELATION"),
         "boundary": {"kind": "host-reported-compaction", "event_id": "constructed-event", "digest": sha(b"CONSTRUCTED BOUNDARY")},
         "scope": {"identity": "constructed-scope", "digest": sha(b"CONSTRUCTED SCOPE")},
         "action": {"identity": "constructed-action", "digest": sha(b"CONSTRUCTED ACTION"),
                    "class": "REQUIRED_INTERNAL_CHILD", "argv": ["route-trigger", "STALE_CONTEXT_RECONSTRUCTION"]},
         "evidence": {"owner": {}, "authority": {}, "effect": {}, "dependency": {}},
         "inputs": [{"identity": "constructed-input", "path": "source.txt", "digest": sha(b"CONSTRUCTED INPUT"), "status": "CURRENT"}],
         "package": {"head": "1" * 40, "tree": "2" * 40, "source_digests": {}, "action_executable": {}},
         "child_source": {"identity": child["identity"], "digest": child["digest"]},
         "decision": "REQUIRED", "classification": "MECHANICALLY_REQUIRED", "invalidators": [],
         "expiry_fingerprint": sha(b"CONSTRUCTED FINGERPRINT"), "expires_on": EXPIRES,
         "predecessor_record_oid": None if state == "UNSATISFIED" else "2" * 40,
         "route_transaction_id": packet["route_transaction_id"], "obligation_id": packet["obligation_id"],
         "route_state": state, "child_lifecycle_owned": state != "UNSATISFIED", "consumed_record_oid": None}
    if recovery:
        for name in ("continuity_generation", "continuity_receipt", "boundary", "evidence", "inputs",
                     "invalidators", "expiry_fingerprint", "expires_on", "consumed_record_oid"):
            del r[name]
        capsule = {"schema": "implementaudit.post-compaction-recovery.v3", "custody": {}, "native_observation": {},
                   "native_invocation_digest": sha(b"CONSTRUCTED INVOCATION"), "event_id": "constructed-recovery-event",
                   "event_digest": sha(b"CONSTRUCTED EVENT"), "scope_digest": r["scope"]["digest"],
                   "selected_child": "audit-state", "return_contract": "implementaudit.audit-state-minimum-frontier-return.v1",
                   "package": r["package"], "child_source": r["child_source"], "continuity_current": False,
                   "ordinary_effect_authority": "NONE", "subject_cause_attested": False}
        capsule["capsule_digest"] = sha(capsule)
        r.update(schema="implementaudit.route-recovery-decision.v1", predicate_version="R0033.recovery-cognition.v1",
                 continuity_current=False, ordinary_effect_authority="NONE", recovery_capsule=capsule)
    if state != "UNSATISFIED":
        packet_wire = wire(packet)
        returned = {"schema": "implementaudit.child-return.v1", "obligation_id": r["obligation_id"],
                    "route_transaction_id": r["route_transaction_id"], "packet_digest": packet_wire["digest"],
                    "status": "RETURNED", "payload": {"captured_note": "CONSTRUCTED source-only return"}}
        returned_wire = wire(returned) if state in ("RETURNED", "SATISFIED") else None
        governed = {"schema": "implementaudit.governor-route-decision.v1", "obligation_id": r["obligation_id"],
                    "route_transaction_id": r["route_transaction_id"], "return_digest": wire(returned)["digest"],
                    "outcome": "SATISFIED", "reason": "CONSTRUCTED source-only reconciliation"}
        r["lifecycle"] = {"state": state, "required_record_oid": "3" * 40,
                          "delivery": {"child": child, "packet": packet_wire}, "child_return": returned_wire,
                          "governor_decision": wire(governed) if state == "SATISFIED" else None,
                          "governor_decision_count": int(state == "SATISFIED"),
                          "source_event_status": "satisfied" if state == "SATISFIED" else "active"}
    r["record_identity"] = sha(r)
    return r


def reseal(record):
    record["record_identity"] = sha({k: v for k, v in record.items() if k != "record_identity"})


def stage(record, name, ascii_only=False):
    body = {"schema": "implementaudit.host-holon-stage-receipt.v1", "owner_id": "constructed-owner",
            "host_id": record["host_id"], "host_session_id": record["host_session_id"],
            "binding_generation": record["host_binding_generation"], "selected_child": "audit-state",
            "packet_digest": record["lifecycle"]["delivery"]["packet"]["digest"],
            "obligation_id": record["obligation_id"], "route_transaction_id": record["route_transaction_id"],
            "stage": name, "event_id": "constructed-\u00e9v\u00e9nement-" + name}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=ascii_only).encode()
    return {**body, "receipt_identity": sha(raw)}


def with_execution(record, ascii_only=False):
    stages = [stage(record, name, ascii_only) for name in ("LOAD", "USE", "DISPOSE")]
    evidence = {k: stages[0][k] for k in ("owner_id", "host_id", "host_session_id", "binding_generation",
                "selected_child", "route_transaction_id", "obligation_id", "packet_digest")}
    record["lifecycle"]["execution_evidence"] = {**evidence,
        "schema": "implementaudit.resolved-holon-execution-evidence.v1", "stages": stages}
    returned = json.loads(base64.b64decode(record["lifecycle"]["child_return"]["bytes_b64"]))
    returned["payload"]["holon_execution_evidence"] = {
        **{k: evidence[k] for k in ("selected_child", "route_transaction_id", "obligation_id", "packet_digest")},
        "schema": "implementaudit.holon-execution-evidence.v1",
        "stages": [{k: item[k] for k in ("stage", "receipt_identity")} for item in stages]}
    record["lifecycle"]["child_return"] = wire(returned)
    reseal(record)
    return record


def child_result(returned=False):
    record = route("RETURNED" if returned else "OPEN")
    result = {"schema": "implementaudit.route-transaction-result.v1",
        "status": "CHILD_RETURNED" if returned else "CHILD_OPEN", "decision": "REQUIRED",
        "route_state": "RETURNED" if returned else "OPEN", "advance_allowed": False,
        "enforcement_available": True, "record_oid": "1" * 40, "record_identity": record["record_identity"],
        "history_read_performed": False, "holon_lifecycle": {
            "required_sequence": ["OPEN", "LOAD", "USE", "RETURN", "DISPOSE", "RECONCILE"],
            "completed": ["OPEN", "RETURN"] if returned else ["OPEN"], "selected_child": "audit-state",
            "route_transaction_id": record["route_transaction_id"], "obligation_id": record["obligation_id"],
            "identity_bound": True, "unverified": ["LOAD", "USE", "DISPOSE"], "child_authority": "NONE",
            "child_can_route": False, "governor_reconciliation_required": True, "canonical_credit": False}}
    if returned:
        result["child_return"] = record["lifecycle"]["child_return"]
    else:
        result.update({k: record[k] for k in ("obligation_id", "route_transaction_id")})
        result["delivery"] = record["lifecycle"]["delivery"]
    return result


def recovery_v4(state="OPEN"):
    record = route(state, recovery=True)
    capsule = record["recovery_capsule"]
    native = {"native_thread_id": "constructed-thread", "native_session_id": SESSION,
        "native_turn_id": "constructed-turn", "epoch_identity": sha(b"CONSTRUCTED EPOCH IDENTITY"),
        "row_digest": sha(b"CONSTRUCTED ROW"), "row_ordinal": 1,
        "observation_identity": sha(b"CONSTRUCTED NATIVE OBSERVATION")}
    invocation = sha({key: native[key] for key in ("native_thread_id", "native_session_id", "native_turn_id")})
    capsule.update(schema="implementaudit.post-compaction-recovery.v4", native_observation=native,
        native_invocation_digest=invocation, custody={"subject_digest": sha(b"CONSTRUCTED SUBJECT")},
        return_contract="implementaudit.audit-state-minimum-frontier-return.v2")
    capsule["attempt_boundary"] = {"schema": "implementaudit.recovery-attempt-boundary.v1",
        **{key: native[key] for key in ("native_thread_id", "native_session_id", "native_turn_id")},
        "attempt_identity": invocation, "scope": "ENTIRE_QUALIFIED_NATIVE_TURN_THROUGH_OPEN",
        "input_occurrence_digest": native["row_digest"], "input_occurrence_ordinal": native["row_ordinal"],
        "subject_digest": capsule["custody"]["subject_digest"], "native_observation_identity": native["observation_identity"],
        "historical_misses_disposition": "PRESERVE_WITHOUT_RETROACTIVE_CREDIT"}
    capsule["capsule_digest"] = sha({k: v for k, v in capsule.items() if k != "capsule_digest"})
    record["predicate_version"] = "R0033.recovery-cognition.v2"
    if "lifecycle" in record:
        attempt = {"schema": "implementaudit.qualified-recovery-attempt-evidence.v1",
            "capsule_digest": capsule["capsule_digest"], "native_observation_identity": native["observation_identity"],
            "source_reader_digest": sha(b"CONSTRUCTED SOURCE READER"),
            "evidence": {**{key: native[key] for key in ("native_thread_id", "native_session_id", "native_turn_id", "epoch_identity")},
                "input_row_digest": native["row_digest"], "constructed_uninterpreted_payload": "NOT native acquisition"}}
        attempt["evidence_digest"] = sha(attempt)
        record["lifecycle"]["attempt_evidence"] = attempt
    reseal(record)
    return record


class RouteConsumerTests(unittest.TestCase):
    def decode(self, kind, value):
        self.assertTrue(callable(DECODE), "Missing requested decode_route_capture consumer")
        return DECODE(kind, value)

    def records(self, result, kind):
        return [row for row in result["records"] if row["record_type"] == kind]

    def test_pending_completed_boundary_survives_absent_epoch(self):
        value = pending()
        result = self.decode("pending", value)
        rows = self.records(result, "PendingCompaction")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["observation"]["pending"])
        self.assertEqual(rows[0]["observation"]["kind"], "COMPLETED_RESUMED_BOUNDARY")
        self.assertNotIn("measured_epoch", rows[0]["observation"])

    def test_second_uncovered_boundary_and_actual_pending_survive_logical_join(self):
        value = pending(two=True)
        proposal = assignment(value)
        result = self.decode("pending", value)
        self.assertEqual(sum(row["observation"]["pending"] for row in self.records(result, "PendingCompaction")), 2)
        self.assertEqual(len(proposal["projected_pending"]), 1)
        self.assertEqual(self.records(result, "LogicalJoinProposal")[0]["observation"], proposal)
        self.assertTrue(self.records(result, "ChildReturn"))
        self.assertTrue(self.records(result, "ChildReservation"))

    def test_later_version_survives_earlier_consumption(self):
        value = pending()
        item = next(iter(value["observations"].values()))
        item.update(version=2, consumed_version=1)
        result = self.decode("pending", value)
        self.assertTrue(self.records(result, "PendingCompaction")[0]["observation"]["pending"])

    def test_pending_refuses_ambiguous_map_identity_and_boolean_version(self):
        for change in (lambda v: next(iter(v["observations"].values())).update(version=True),
                       lambda v: next(iter(v["observations"].values())).update(id="other")):
            value = pending(); change(value)
            with self.assertRaises(ValueError): self.decode("pending", value)

    def test_missing_source_preserves_unresolved_signal_and_absence_census(self):
        value = pending(); value["source"] = None; value["source_problem"] = "NO_REGISTERED_TRANSCRIPT"
        sid = "unresolved-signal-" + digest(SESSION.encode())
        value["observations"] = {sid: {"id": sid, "kind": "UNRESOLVED_SIGNAL", "version": 1, "consumed_version": 0,
            "proof": {"host_session_id": SESSION, "signal": "SessionStart/source=compact",
                      "hook_source_sha256": digest(b"CONSTRUCTED HOOK"), "binding_generation": "G0001",
                      "logical_occurrence_count": None, "completion": "UNRESOLVED", "resume": "UNRESOLVED",
                      "delivery_count_is_not_occurrence_identity": True}}}
        result = self.decode("pending", value)
        self.assertTrue(self.records(result, "PendingCompaction")[0]["observation"]["pending"])
        self.assertTrue(any("source" in row["reason"].lower() for row in result["omissions"]))

    def test_pending_decision_keeps_scope_without_inventing_session(self):
        value = decision(pending(two=True)); result = self.decode("pending-decision", value)
        row = self.records(result, "PendingAuditDecision")[0]
        self.assertNotIn("session_id", row["observation"])
        self.assertEqual(row["observation"]["pending"], value["pending"])
        self.assertTrue(any("attribution" in r["reason"].lower() for r in result["omissions"]))

    def test_pending_decision_refuses_hidden_obligation(self):
        value = decision(pending()); value["audit_state_required"] = False
        with self.assertRaises(ValueError): self.decode("pending-decision", value)

    def test_logical_join_cannot_claim_native_authentication(self):
        value = pending(); proposal = assignment(value)
        positive = self.decode("pending", proposal)
        self.assertTrue(self.records(positive, "LogicalJoinProposal"))
        proposal["host_producer_authenticated"] = True
        with self.assertRaises(ValueError): self.decode("pending", proposal)

    def test_ordinary_route_retains_full_known_fields(self):
        value = route(); result = self.decode("route", value)
        row = self.records(result, "RouteObligation")[0]["observation"]
        for key in ("host_id", "host_session_id", "host_binding_generation", "boundary", "scope", "action",
                    "continuity_receipt", "child_source", "route_transaction_id", "obligation_id"):
            self.assertEqual(row[key], value[key])
        self.assertTrue(any("R0035" in r["reason"] for r in result["omissions"]))

    def test_satisfied_route_does_not_infer_execution_stages(self):
        result = self.decode("route", route("SATISFIED"))
        self.assertTrue(self.records(result, "RouteLifecycle"))
        self.assertTrue(self.records(result, "ChildReturn"))
        self.assertTrue(self.records(result, "GovernorRouteDecision"))
        self.assertFalse(self.records(result, "HostStageReceipt"))
        self.assertTrue(any("LOAD/USE/DISPOSE" in r["reason"] for r in result["omissions"]))

    def test_route_rejects_resealed_outer_with_wrong_embedded_bytes(self):
        value = route("RETURNED")
        value["lifecycle"]["child_return"]["bytes_b64"] = base64.b64encode(b"different").decode()
        reseal(value)
        with self.assertRaises(ValueError): self.decode("route", value)

    def test_route_rejects_foreign_obligation_inside_return(self):
        value = route("RETURNED")
        returned = json.loads(base64.b64decode(value["lifecycle"]["child_return"]["bytes_b64"]))
        returned["obligation_id"] = sha(b"FOREIGN CONSTRUCTED OBLIGATION")
        value["lifecycle"]["child_return"] = wire(returned); reseal(value)
        with self.assertRaises(ValueError): self.decode("route", value)

    def test_recovery_does_not_require_canonical_currentness(self):
        value = route(recovery=True); result = self.decode("route", value)
        self.assertFalse(self.records(result, "RouteObligation")[0]["observation"]["continuity_current"])
        self.assertTrue(any("recovery" in r["reason"].lower() for r in result["omissions"]))

    def test_abandoned_route_retains_unaccepted_open_lifecycle(self):
        value = route("OPEN", recovery=True)
        old_identity = value["record_identity"]
        value["route_state"] = "ABANDONED"
        value["disposition"] = {"schema": "implementaudit.recovery-abandonment.v1",
                                "old_record_oid": value["predecessor_record_oid"], "old_record_identity": old_identity,
                                "route_transaction_id": value["route_transaction_id"],
                                "capsule_digest": value["recovery_capsule"]["capsule_digest"],
                                "admission_identity": sha(b"CONSTRUCTED ADMISSION"), "evidence_digest": sha(b"CONSTRUCTED REFUSAL"),
                                "source_transition_digest": sha(b"CONSTRUCTED SOURCE TRANSITION"),
                                "successor_package": {"head": "4" * 40}, "successor_child_source": {"digest": sha(b"CONSTRUCTED SUCCESSOR")},
                                "reason": "CHILD_REFUSED", "continuity_current": False,
                                "ordinary_effect_authority": "NONE", "recovery_cognition_accepted": False}
        reseal(value); result = self.decode("route", value)
        self.assertEqual(self.records(result, "RouteObligation")[0]["observation"]["route_state"], "ABANDONED")
        self.assertEqual(self.records(result, "RouteLifecycle")[0]["observation"]["state"], "OPEN")

    def test_route_rejects_lifecycle_state_or_count_contradiction(self):
        for change in (lambda v: v["lifecycle"].update(state="OPEN"),
                       lambda v: v["lifecycle"].update(governor_decision_count=2)):
            value = route("SATISFIED"); change(value); reseal(value)
            with self.assertRaises(ValueError): self.decode("route", value)

    def test_completion_is_separate_captured_observation(self):
        value = {"schema": "implementaudit.route-transaction-result.v1", "status": "ROUTE_COMPLETE",
                 "decision": "REQUIRED", "route_state": "SATISFIED", "advance_allowed": True,
                 "enforcement_available": True, "record_oid": "1" * 40, "record_identity": sha(b"CONSTRUCTED RECORD"),
                 "governor_decision_count": 1, "post_return_currentness": "VERIFIED",
                 "holon_lifecycle": {"required_sequence": ["OPEN", "LOAD", "USE", "RETURN", "DISPOSE", "RECONCILE"],
                     "completed": ["OPEN", "RETURN", "RECONCILE"], "selected_child": "audit-state",
                     "route_transaction_id": sha(b"CONSTRUCTED TRANSACTION"), "obligation_id": sha(b"CONSTRUCTED OBLIGATION"),
                     "identity_bound": True, "unverified": ["LOAD", "USE", "DISPOSE"], "child_authority": "NONE",
                     "child_can_route": False, "governor_reconciliation_required": False, "canonical_credit": False},
                 "history_read_performed": False, "idempotent": False}
        result = self.decode("route-result", value)
        self.assertEqual(self.records(result, "RouteResult")[0]["observation"], value)
        self.assertTrue(any("currentness" in r["reason"].lower() for r in result["omissions"]))

    def test_binding_and_unbound_result_do_not_access_paths(self):
        value = binding()
        with mock.patch("builtins.open", side_effect=AssertionError("Unexpected I/O")):
            result = self.decode("host-binding", value)
        self.assertEqual(self.records(result, "HostSessionBinding")[0]["observation"], value)
        unbound = {"schema": "implementaudit.host-session-binding-result.v1", "status": "UNBOUND", "enforcement_available": False}
        self.assertTrue(self.decode("host-binding", unbound)["omissions"])

    def test_attributed_result_does_not_invent_sensor_payload(self):
        value = {"schema": "implementaudit.host-session-binding-result.v1", "status": "ATTRIBUTED",
                 "binding_generation": "G0001", "correlation_id": sha(b"CONSTRUCTED ATTRIBUTION"),
                 "host_activation_proven": False, "proof_layers": {"source_core": "PRESENT", "package": "UNVERIFIED",
                 "install": "UNVERIFIED", "host_activation": "UNVERIFIED"}}
        result = self.decode("host-binding", value)
        self.assertNotIn("event_name", result["records"][0]["observation"])
        self.assertTrue(any("sensor" in r["reason"].lower() for r in result["omissions"]))

    def test_binding_generation_chain_refuses_stale_mismatched_successor(self):
        value = binding(); value["binding_generation"] = "G0002"
        with self.assertRaises(ValueError): self.decode("host-binding", value)

    def test_input_unchanged_repeatable_with_stable_identity_and_inert_text(self):
        value = pending(); before = canonical(value)
        result = self.decode("pending", value)
        self.assertEqual(result, self.decode("pending", value))
        self.assertEqual(canonical(value), before)
        item = next(iter(value["observations"].values())); item["consumed_version"] = 1
        later = self.decode("pending", value)
        self.assertEqual(self.records(result, "PendingCompaction")[0]["key"],
                         self.records(later, "PendingCompaction")[0]["key"])

    def test_invalid_scalars_unknown_schema_and_cycle_fail(self):
        for value in (float("nan"), {"schema": "new-version"}, {"schema": "implementaudit.compaction-audit-pending.v1", "x": "\ud800"}):
            with self.assertRaises(ValueError): self.decode("pending", value)
        cycle = {}; cycle["self"] = cycle
        with self.assertRaises(ValueError): self.decode("pending", cycle)

    def test_unknown_nested_data_is_retained_with_omission(self):
        value = pending(); assignment(value)
        value["assignments"]["constructed-child"]["future_native_stage"] = {"literal": "LOAD is text, not credit"}
        result = self.decode("pending", value)
        row = self.records(result, "ChildReservation")[0]
        self.assertIn("future_native_stage", row["observation"])
        self.assertTrue(any("nested" in r["reason"].lower() for r in result["omissions"]))

    def test_constructed_nonascii_h0_hash_is_retained_and_cross_owner_gap_reported(self):
        receipt = stage(route("OPEN"), "LOAD", ascii_only=True)
        result = self.decode("host-binding", receipt)
        self.assertEqual(self.records(result, "HostStageReceipt")[0]["observation"], receipt)
        self.assertTrue(any("owner" in row["reason"].lower() and "ascii" in row["reason"].lower()
                            for row in result["omissions"]))
        receipt["receipt_identity"] = sha({k: v for k, v in receipt.items() if k != "receipt_identity"})
        with self.assertRaises(ValueError): self.decode("host-binding", receipt)

    def test_constructed_route_nonascii_stage_uses_exact_utf8_grammar(self):
        result = self.decode("route", with_execution(route("RETURNED")))
        self.assertEqual(len(self.records(result, "HostStageReceipt")), 3)
        with self.assertRaises(ValueError):
            self.decode("route", with_execution(route("RETURNED"), ascii_only=True))

    def test_unavailable_results_preserve_native_refusal_without_authority(self):
        for kind, schema in (("route-result", "implementaudit.route-transaction-result.v1"),
                             ("host-binding", "implementaudit.host-session-binding-result.v1")):
            value = {"schema": schema, "status": "UNAVAILABLE", "enforcement_available": False,
                     "error": "CONSTRUCTED refusal: source unavailable"}
            if kind == "route-result": value.update(decision="PENDING", advance_allowed=False)
            result = self.decode(kind, value)
            self.assertTrue(self.records(result, "NativeRefusal"))
            value["enforcement_available"] = True
            with self.assertRaises(ValueError): self.decode(kind, value)

    def test_child_results_validate_actual_embedded_byte_identity(self):
        for returned in (False, True):
            value = child_result(returned)
            self.assertTrue(self.decode("route-result", value)["records"])
            embedded = value["child_return"] if returned else value["delivery"]["packet"]
            embedded["bytes_b64"] = base64.b64encode(b"CONSTRUCTED wrong bytes").decode()
            with self.assertRaises(ValueError): self.decode("route-result", value)

    def test_child_result_rejects_foreign_return_and_projected_state(self):
        value = child_result(True)
        returned = json.loads(base64.b64decode(value["child_return"]["bytes_b64"]))
        returned["obligation_id"] = sha(b"CONSTRUCTED FOREIGN OBLIGATION")
        value["child_return"] = wire(returned)
        with self.assertRaises(ValueError): self.decode("route-result", value)
        value = child_result(False); value["holon_lifecycle"]["completed"].append("RETURN")
        with self.assertRaises(ValueError): self.decode("route-result", value)

    def test_current_result_retains_disagreement_and_checks_known_scalars(self):
        record = route("SATISFIED")
        value = {"schema": "implementaudit.route-transaction-result.v1", "status": "CURRENT",
            "decision": "REQUIRED", "classification": "MECHANICALLY_REQUIRED", "route_state": "SATISFIED",
            "advance_allowed": True, "admission_required": False, "enforcement_available": True,
            "record_oid": "1" * 40, "record_identity": record["record_identity"],
            "obligation_id": record["obligation_id"], "route_transaction_id": record["route_transaction_id"],
            "selected_child": "audit-state", "governor_decision_count": 1, "history_query": None,
            "history_read_performed": False, "mirror_claim": "PENDING", "mirror_status": "IGNORED_CONTRADICTION",
            "projection_status": "INVALID", "host_activation_proven": False,
            "proof_layers": {"source_core": "PRESENT", "package": "UNVERIFIED", "install": "UNVERIFIED", "host_activation": "UNVERIFIED"}}
        self.assertEqual(self.records(self.decode("route-result", value), "RouteResult")[0]["observation"], value)
        for change in ({"governor_decision_count": True}, {"advance_allowed": False},
                       {"route_transaction_id": "not-a-digest"}, {"mirror_status": "IGNORED_CORROBORATION"}):
            with self.assertRaises(ValueError): self.decode("route-result", {**value, **change})

    def test_nonrequired_route_uses_source_owned_no_child_identity(self):
        value = route()
        identity = "R0033:NOT_REQUIRED:NO_CHILD"
        value.update(decision="NOT_REQUIRED", classification="MECHANICALLY_NOT_REQUIRED",
                     route_state=None, obligation_id=None, child_source={"identity": identity, "digest": sha({"identity": identity})})
        reseal(value)
        self.assertTrue(self.decode("route", value)["records"])
        value["child_source"] = None; reseal(value)
        with self.assertRaises(ValueError): self.decode("route", value)

    def test_binding_generation_is_exactly_four_uppercase_hex_nonzero_digits(self):
        value = {"schema": "implementaudit.host-session-binding-result.v1", "status": "ATTRIBUTED",
            "binding_generation": "GFFFF", "correlation_id": sha(b"CONSTRUCTED CORRELATION"),
            "host_activation_proven": False, "proof_layers": {"source_core": "PRESENT", "package": "UNVERIFIED",
            "install": "UNVERIFIED", "host_activation": "UNVERIFIED"}}
        self.assertTrue(self.decode("host-binding", value)["records"])
        for generation in ("G0000", "G10000", "G00ff", "G001"):
            with self.assertRaises(ValueError): self.decode("host-binding", {**value, "binding_generation": generation})

    def test_pending_completed_kind_has_exactly_one_canonical_marker(self):
        value = pending()
        item = next(iter(value["observations"].values()))
        # A corroborating response item does not create another completed boundary.
        item["proof"]["markers"].append({"ordinal": 3, "offset": 120, "bytes": 10,
            "sha256": digest(b"CONSTRUCTED CORROBORATING ROW"), "kind": "response_item", "canonical": False})
        item["proof"]["resume"].update(ordinal=4, offset=130)
        item["id"] = "boundary-" + digest(item["proof"])
        value["observations"] = {item["id"]: item}
        self.assertTrue(self.decode("pending", value)["records"])
        item["kind"] = "AMBIGUOUS_MARKER_GROUP"
        with self.assertRaises(ValueError): self.decode("pending", value)
        item["proof"]["markers"][0].update(kind="response_item", canonical=False)
        item["id"] = "boundary-" + digest(item["proof"])
        value["observations"] = {item["id"]: item}
        self.assertTrue(self.decode("pending", value)["records"])
        item["kind"] = "COMPLETED_RESUMED_BOUNDARY"
        with self.assertRaises(ValueError): self.decode("pending", value)

    def test_v4_lifecycle_requires_exact_attempt_evidence_envelope(self):
        value = recovery_v4()
        self.assertTrue(self.decode("route", value)["records"])
        missing = copy.deepcopy(value); del missing["lifecycle"]["attempt_evidence"]; reseal(missing)
        with self.assertRaises(ValueError): self.decode("route", missing)
        foreign = copy.deepcopy(value)
        attempt = foreign["lifecycle"]["attempt_evidence"]
        attempt["capsule_digest"] = sha(b"CONSTRUCTED FOREIGN CAPSULE")
        attempt["evidence_digest"] = sha({k: v for k, v in attempt.items() if k != "evidence_digest"})
        reseal(foreign)
        with self.assertRaises(ValueError): self.decode("route", foreign)
        self.assertTrue(self.decode("route", recovery_v4("UNSATISFIED"))["records"])


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + _unittest_args)
