#!/usr/bin/env python3
"""DRAFT (adviser, not reviewed, not shipped): deterministic audit-andon return check.

Encodes skills/audit-andon/SKILL.md at 51416b2f:
  GOVERNED_ROUTE=L4_TO_AUDIT_ANDON_TO_L4_OR_GOVERNOR, DIRECT_RETURN=ACTUAL_CALLER,
  AUTHORITY/CURRENTNESS/LIFECYCLE/STATE_MUTATION/RELEASE/CLOSURE/RXX ownership NONE,
  CAN_ESTABLISH_AUDIT_COMPLETE=NO, CHILD_ROUTING=FORBIDDEN.
Input: the route envelope plus the child's returned record (JSON on stdin).
Output: one JSON verdict; exit 0 accept, 1 refuse. Never repairs or mutates.
Targets DG17 N04, N05, H07, M11 and terminal clause 4.
"""
import json
import sys

RETURN_FIELDS = {"route", "returns_to", "classification", "causal_account",
                 "disposition", "countermeasure_options", "escalation_recommendation",
                 "follow_up_evidence_obligation"}
FORBIDDEN_KEYS = {"pass", "audit_complete", "closure", "release", "merge", "publish",
                  "currentness", "epoch", "receipt", "mutation", "patch", "lifecycle",
                  "state_transition", "rxx", "dispatch", "route_child", "next_child"}
FORBIDDEN_MARKERS = ("AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE")
VALID = {"GOVERNED": {"L4", "GOVERNOR"}, "DIRECT": {"ACTUAL_CALLER"}}


def refuse(reason):
    print(json.dumps({"schema": "draft.audit-andon-return-verdict.v1", "decision": "REFUSE", "reason": reason}))
    return 1


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def check(envelope, record):
    route = envelope.get("route")
    if route not in VALID:
        return "unknown route envelope"
    if route == "GOVERNED" and not envelope.get("governor_envelope_digest"):
        return "governed route requires the exact governor envelope"
    if route == "DIRECT" and not envelope.get("caller"):
        return "direct route requires the actual caller identity"
    if not isinstance(record, dict) or set(record) != RETURN_FIELDS:
        return "return record does not have the exact bounded field set"
    if record["route"] != route:
        return "return route differs from the entry envelope"
    if record["returns_to"] not in VALID[route]:
        return "return owner is wrong for this route"
    if route == "DIRECT" and envelope.get("caller") != envelope.get("returns_to_caller", envelope.get("caller")):
        return "direct return must go to the actual caller"
    if any(str(key).lower() in FORBIDDEN_KEYS for key in walk_keys(record)):
        return "return carries an authority, currentness, lifecycle, mutation or closure field"
    if any(marker in text for text in walk_strings(record) for marker in FORBIDDEN_MARKERS):
        return "return asserts a terminal marker"
    return None


def main():
    try:
        payload = json.loads(sys.stdin.read())
        reason = check(payload["envelope"], payload["record"])
    except (ValueError, KeyError, TypeError) as error:
        return refuse("malformed input: " + type(error).__name__)
    if reason:
        return refuse(reason)
    print(json.dumps({"schema": "draft.audit-andon-return-verdict.v1", "decision": "ACCEPT",
                      "returns_to": payload["record"]["returns_to"], "authority_granted": False}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
