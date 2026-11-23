"""Check route and destination binding in a supplied Andon return fixture."""
import hashlib
import json
import re
import sys

RETURN_FIELDS = {"route", "returns_to", "classification", "causal_account",
                 "disposition", "countermeasure_options", "escalation_recommendation",
                 "follow_up_evidence_obligation"}
FORBIDDEN_KEYS = {"pass", "audit_complete", "closure", "release", "merge", "publish",
                  "currentness", "epoch", "receipt", "mutation", "patch", "lifecycle",
                  "state_transition", "rxx", "dispatch", "route_child", "next_child"}
FORBIDDEN_MARKERS = ("AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE")
VALID = {"GOVERNED": ("L4", "GOVERNOR"), "DIRECT": ("ACTUAL_CALLER",)}
DIGEST = re.compile(r"[0-9a-f]{64}")


def check(envelope, record):
    if not isinstance(envelope, dict) or not isinstance(record, dict):
        return "envelope and return must be objects"
    route = envelope.get("route")
    if not isinstance(route, str) or route not in VALID:
        return "unknown route envelope"
    binding_field = "recipient_id" if route == "DIRECT" else "governor_envelope_digest"
    if set(record) != RETURN_FIELDS | {binding_field}:
        return "return record lacks exact bounded fields or route binding"
    if record["route"] != route:
        return "return route differs from the entry envelope"
    if record["returns_to"] not in VALID[route]:
        return "return owner is wrong for this route"
    if route == "DIRECT":
        caller = envelope.get("caller")
        if (set(envelope) != {"route", "caller"} or not isinstance(caller, str) or not caller
                or caller != caller.strip() or record[binding_field] != caller):
            return "direct return recipient differs from the caller"
    else:
        frozen = envelope.get("governor_envelope")
        digest = envelope.get("governor_envelope_digest")
        if (set(envelope) != {"route", "governor_envelope", "governor_envelope_digest"}
                or not isinstance(frozen, dict) or not frozen
                or not isinstance(digest, str) or not DIGEST.fullmatch(digest)):
            return "governed route requires the exact governor envelope"
        raw = json.dumps(frozen, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
        if hashlib.sha256(raw).hexdigest() != digest or record[binding_field] != digest:
            return "governed return differs from the frozen envelope digest"

    pending = [record]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if any(key.casefold() in FORBIDDEN_KEYS for key in item):
                return "return carries an authority, currentness, lifecycle, mutation or closure field"
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, str) and any(marker in item for marker in FORBIDDEN_MARKERS):
            return "return asserts a terminal marker"
    return None


def unique_object(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def main():
    try:
        payload = json.load(sys.stdin, object_pairs_hook=unique_object)
        if not isinstance(payload, dict) or set(payload) != {"envelope", "record"}:
            raise ValueError("invalid fixture")
        reason = check(payload["envelope"], payload["record"])
    except (ValueError, RecursionError):
        reason = "malformed input"
    verdict = {"schema": "sol-dg17.andon-return-fixture-verdict.v1",
               "decision": "REFUSE" if reason else "ACCEPT", "authority_granted": False}
    if reason:
        verdict["reason"] = reason
    else:
        verdict["returns_to"] = payload["record"]["returns_to"]
    print(json.dumps(verdict))
    return 1 if reason else 0


if __name__ == "__main__":
    sys.exit(main())
