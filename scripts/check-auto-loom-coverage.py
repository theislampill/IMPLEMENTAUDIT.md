#!/usr/bin/env python3
"""Read-only consistency check of supplied Auto-LOOM coverage acceptance evidence.

FACTS is a separately bound governor census, not data reconstructed from the
projection. This checker neither attests omitted facts nor schedules anything.
A consistent report grants no runtime, currentness, admission or JOIN authority.
"""

import argparse
import hashlib
import json
from pathlib import Path


INVARIANTS = {
    "AUTO_LOOM_SCOPE": "FULL_RECURSIVE_CAMPAIGN_HOLARCHY",
    "LOCAL_FORWARD_ONLY": "INSUFFICIENT",
    "OUTWARD_STARVATION": "CONFORMANCE_CONCERN",
    "FUTURE_JOIN_PRECOMPUTATION_REQUIRED": "YES",
    "BLOCK_EDGE_NOT_FUTURE_GRAPH": "YES",
}
DIRECTIONS = {"INWARD", "OUTWARD", "FORWARD", "BACKWARD"}
GATES = {"identity", "authority", "independence", "writer", "resource", "prerequisites"}


def require(condition):
    if not condition:
        raise ValueError("invalid-input")


def binding(value):
    require(isinstance(value, dict) and set(value) == {"campaign", "event", "state"})
    require(all(isinstance(part, str) and part.strip() for part in value.values()))
    return value


def index(rows, key, issues, code):
    require(isinstance(rows, list))
    result = {}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get(key), str) and row[key].strip())
        if row[key] in result:
            issues.append(code)
        result[row[key]] = row
    return result


def violations(facts, projection):
    require(isinstance(facts, dict) and isinstance(projection, dict))
    issues = []
    current = binding(facts["binding"])
    require(facts["currentness"] is None or type(facts["currentness"]) is bool)
    require(isinstance(facts["evidence_scope"], str) and facts["evidence_scope"].strip())
    if binding(projection["binding"]) != current:
        issues.append("projection-freshness")
    if projection.get("authority") != "NONE":
        issues.append("authority-widening")
    if projection.get("evidence_scope") != facts["evidence_scope"]:
        issues.append("evidence-scope")
    if projection.get("invariants") != INVARIANTS:
        issues.append("invariant-contract")
    if not isinstance(projection.get("directions"), list) or (
        len(projection["directions"]) != 4 or set(projection["directions"]) != DIRECTIONS
    ):
        issues.append("direction-population")

    parents, subject, root = facts["parents"], facts["subject"], facts["root"]
    require(isinstance(parents, dict))
    require(isinstance(subject, str) and subject.strip())
    require(isinstance(root, str) and root.strip())
    ancestors = []
    cursor = subject
    while cursor is not None:
        if not isinstance(cursor, str) or not cursor.strip() or (
            cursor in ancestors or cursor not in parents
        ):
            issues.append("ancestry-unresolved")
            break
        ancestors.append(cursor)
        if cursor == root:
            if parents[cursor] is not None:
                issues.append("ancestry-unresolved")
            break
        cursor = parents[cursor]
    if not ancestors or ancestors[-1] != root:
        issues.append("ancestry-unresolved")
    if projection.get("ancestors") != ancestors:
        issues.append("ancestor-coverage")

    known_edges = index(facts["edges"], "id", issues, "edge-population")
    observed_edges = index(projection["edges"], "id", issues, "edge-population")
    if set(known_edges) != set(observed_edges):
        issues.append("edge-population")
    eligible, joined = set(), set()
    for identity, edge in known_edges.items():
        if edge.get("at") not in ancestors:
            issues.append("edge-ancestor")
        state, gates = edge["state"], edge["gates"]
        require(state in {"PENDING", "ACTIVE", "DONE", "RETURNED", "JOINED"})
        require(edge.get("direction") in DIRECTIONS)
        require(isinstance(edge.get("evidence_scope"), str) and edge["evidence_scope"].strip())
        require(isinstance(gates, dict) and GATES <= set(gates))
        require(all(isinstance(key, str) and key.strip() and value in
                    {"SATISFIED", "MISSING", "UNKNOWN"} for key, value in gates.items()))
        if gates.get("native_currentness") == "SATISFIED" and facts["currentness"] is not True:
            issues.append("native-currentness")
        require(type(edge["accepted"]) is bool)
        require(edge["joined_into"] is None or isinstance(edge["joined_into"], str))
        pending = {key: value for key, value in gates.items() if value != "SATISFIED"}
        if state in {"RETURNED", "JOINED"} and edge["direction"] != "BACKWARD":
            issues.append("edge-direction")
        if state == "JOINED":
            if edge["accepted"] is not True or edge["joined_into"] not in ancestors:
                issues.append("join-acceptance")
            else:
                joined.add(identity)
        elif edge["joined_into"] is not None:
            issues.append("join-acceptance")
        disposition = {
            "ACTIVE": "ACTIVE", "DONE": "RETAINED",
            "RETURNED": "PENDING_JOIN", "JOINED": "RETAINED",
        }.get(state, "BLOCKED" if pending else "ELIGIBLE")
        if disposition == "ELIGIBLE":
            eligible.add(identity)

        row = observed_edges.get(identity)
        if row is None:
            continue
        if binding(row["binding"]) != current:
            issues.append("edge-freshness")
        if row.get("direction") != edge["direction"]:
            issues.append("edge-direction")
        if row.get("eligibility") != disposition:
            issues.append("edge-disposition")
        if row.get("pending") != pending:
            issues.append("pending-inputs")
        for field in ("owner", "consumer", "reconsider", "next_action"):
            if row.get(field) != edge.get(field):
                issues.append("pending-custody")
            if state != "DONE" and not (
                isinstance(edge.get(field), str) and edge[field].strip()
            ):
                issues.append("pending-custody")
        if row.get("evidence_scope") != edge.get("evidence_scope"):
            issues.append("evidence-scope")
        if row.get("authority") != "NONE":
            issues.append("authority-widening")

    for field in ("new_actions", "backward_joins"):
        require(isinstance(projection.get(field), list))
        require(all(isinstance(item, str) and item for item in projection[field]))
        if len(set(projection[field])) != len(projection[field]):
            issues.append("duplicate-action")
    if not set(projection["new_actions"]) <= eligible:
        issues.append("ineligible-new-action")
    if set(projection["backward_joins"]) != joined:
        issues.append("accepted-backward-joins")
    prior = facts.get("prior")
    if prior is not None:
        require(isinstance(prior, dict))
        previous = binding(prior["binding"])
        if previous["campaign"] != current["campaign"]:
            issues.append("prior-campaign")
        if previous == current and projection["new_actions"]:
            issues.append("unchanged-event-redispatch")

    names = facts["views"]
    require(isinstance(names, list) and names)
    require(all(isinstance(name, str) and name.strip() for name in names))
    require(len(set(names)) == len(names))
    views = index(projection["views"], "name", issues, "projection-population")
    if set(views) != set(names):
        issues.append("projection-population")
    history = facts["history"]
    require(isinstance(history, list))
    for entry in history:
        require(isinstance(entry, dict))
        binding(entry["binding"])
        require(isinstance(entry.get("evidence_scope"), str) and entry["evidence_scope"].strip())
        require(entry.get("authority") == "NONE")
    current_views = 0
    for view in views.values():
        observed = binding(view["binding"])
        if view.get("authority") != "NONE":
            issues.append("authority-widening")
        if view.get("status") == "CURRENT":
            current_views += 1
            if observed != current:
                issues.append("projection-freshness")
            if view.get("evidence_scope") != facts["evidence_scope"]:
                issues.append("evidence-scope")
        elif view.get("status") == "HISTORICAL":
            retained = {"binding": observed, "evidence_scope": view.get("evidence_scope"),
                        "authority": view.get("authority")}
            if retained not in history:
                issues.append("historical-scope")
        else:
            issues.append("projection-status")
    if not current_views:
        issues.append("current-projection-missing")
    return sorted(set(issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facts", required=True, type=Path)
    parser.add_argument("--projection", required=True, type=Path)
    args = parser.parse_args()
    identities = {}
    try:
        inputs = []
        for label, path in (("facts", args.facts), ("projection", args.projection)):
            raw = path.read_bytes()
            identities[label + "_sha256"] = hashlib.sha256(raw).hexdigest()
            inputs.append(json.loads(raw))
        issues = violations(*inputs)
        code = 1 if issues else 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        issues, code = ["invalid-input"], 2
    print(json.dumps({
        "status": "REJECT" if issues else "CONSISTENT_SOURCE_COVERAGE_ONLY",
        "authority": "NONE", "issues": issues, **identities,
    }, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
