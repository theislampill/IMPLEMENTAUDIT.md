"""Prospective independent structural predicate oracle. NOT EXECUTED.

Input authentication is separate: independently bind provider artifacts, canonical
raw records, exact Root control commit/receiving and one-use operation identity.
This code grants no authority and imports no product owner.
"""
import json
import sys

def unique(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError("duplicate member")
        out[key] = value
    return out

def evaluate(observed):
    findings = []
    def need(predicate, name):
        if not predicate:
            findings.append(name)
    negative, positive = observed["negative"], observed["positive"]
    for name, stage, code, state, advance, count in (
        ("negative", negative, 3, "RETURNED", False, 0),
        ("positive", positive, 0, "SATISFIED", True, 1),
    ):
        need(stage["exit_code"] == code, name + ":exit")
        payload = stage["payload"]
        for key, value in {"schema": "implementaudit.route-transaction-result.v1",
                           "status": "CURRENT", "decision": "REQUIRED",
                           "route_state": state, "advance_allowed": advance,
                           "governor_decision_count": count}.items():
            need(type(payload.get(key)) is type(value) and payload.get(key) == value,
                 name + ":" + key)
        need(stage["source_sha256"] == "59fd223c0a7493d94a3097c0b7d64327ff310b8af703a215a59fab2ac9ce974d",
             name + ":owner")
    for key in ("obligation_id", "route_transaction_id", "selected_child"):
        need(negative["payload"][key] == positive["payload"][key], "same:" + key)
    need(negative["payload"]["selected_child"] == "audit-assess", "selected-child")
    need(negative["before_record_oid"] == negative["after_record_oid"]
         == negative["payload"]["record_oid"] == observed["return_result_record_oid"],
         "negative-ref-unchanged")
    need(positive["payload"]["record_oid"] == observed["complete_result_record_oid"],
         "positive-exact-completion")
    need(negative["before_record_oid"] != positive["payload"]["record_oid"],
         "real-completion-transition")
    need(observed["canonical_record_joins"]["returned_packet_digest"]
         == observed["canonical_record_joins"]["satisfied_packet_digest"], "same-packet")
    need(observed["canonical_record_joins"]["returned_child_return_digest"]
         == observed["canonical_record_joins"]["satisfied_child_return_digest"], "same-return")
    need(observed["canonical_record_joins"]["satisfied_governor_return_digest"]
         == observed["canonical_record_joins"]["returned_child_return_digest"], "decision-exact-return")
    need(observed["recorded_owner_commands"] ==
         ["decide", "open", "return", "admit-current", "complete", "admit-current"],
         "sole-stage-omission-and-no-replay")
    need(negative["provider_scope"] == positive["provider_scope"] == observed["open_provider_scope"],
         "same-live-provider-job")
    return findings

if __name__ == "__main__":
    try:
        with open(sys.argv[1], encoding="utf-8") as stream:
            observed = json.load(stream, object_pairs_hook=unique)
        findings = evaluate(observed)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        findings = ["malformed-or-incomplete-observation:" + type(exc).__name__]
    print(json.dumps({"schema": "dg17.m10.fixed-oracle-result.v1",
                      "authority": "NONE", "structural_predicates_pass": not findings,
                      "findings": findings,
                      "external_evidence_authentication_required": True}, sort_keys=True))
    raise SystemExit(1 if findings else 0)
