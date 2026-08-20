#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'issue-ready-work-orders.test: %s\n' "$*" >&2
  exit 1
}

ref=skills/implementaudit/references/issue-ready-work-orders.md
cases=fixtures/issue-ready-work-orders/cases.json
model_input=fixtures/issue-ready-work-orders/model-cell-input.md
model_expectations=fixtures/issue-ready-work-orders/model-cell-expectations.json
skill=skills/implementaudit/SKILL.md

[ -f "$ref" ] || fail "missing progressive runtime reference: $ref"
[ -f "$cases" ] || fail "missing deterministic fixture set: $cases"
[ -f "$model_input" ] || fail "missing prompt-independent model-cell input: $model_input"
[ -f "$model_expectations" ] || fail "missing model-cell expectations: $model_expectations"

grep -F '`references/issue-ready-work-orders.md`' "$skill" >/dev/null \
  || fail "SKILL.md Reference Load Map does not expose the progressive reference"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$cases" <<'PY'
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("schema_version") != 2:
    raise SystemExit("fixture schema_version must be 2")

cases = payload.get("cases")
if not isinstance(cases, list):
    raise SystemExit("cases must be a list")

expected_ids = [f"R31-F{i}" for i in range(1, 27)]
ids = [case.get("id") for case in cases]
if ids != expected_ids:
    raise SystemExit(f"fixture population/order mismatch: {ids!r}")
if len(set(ids)) != len(ids):
    raise SystemExit("fixture ids must be unique")

controls = payload.get("review_controls")
if not isinstance(controls, list) or len(controls) != 46:
    raise SystemExit("review_controls must contain the 46 convergence mutations")
all_cases = cases + controls

material_fields = {
    "identity", "gap", "current_allowance", "evidence", "evidence_limits",
    "improvement", "regression", "no_bloat", "owner_source",
    "integration_plan", "tests", "dependencies", "rollback", "overlap", "done",
}
trivial_fields = {"evidence", "fix", "verification", "rollback"}
material_effects = {
    "package", "install", "migration", "security", "external-state",
    "public-doc", "publication", "release",
}
pair_actions = {
    "merge", "split", "narrow", "cross-reference", "serialise",
    "parallel", "defer", "owner-decision",
}

def is_material(finding):
    return any((
        isinstance(finding.get("files"), list)
        and len({item.strip() for item in finding["files"] if isinstance(item, str) and item.strip()}) > 1,
        len(set(finding.get("owners", []))) > 1,
        finding.get("phases", 1) > 1,
        bool(set(finding.get("effects", [])) & material_effects),
        bool(finding.get("changes_instrument")),
        bool(finding.get("issue_dependencies")),
        finding.get("rollback_risk") == "material",
        finding.get("publication_set_size", 1) > 1,
        bool(finding.get("owner_requested_work_order")),
    ))

def dependency_set(draft):
    return set(draft.get("hard_dependencies", [])) | set(draft.get("soft_dependencies", []))

def has_cycle(drafts):
    edges = {d["id"]: dependency_set(d) for d in drafts}
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(dep in edges and visit(dep) for dep in edges.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False
    return any(visit(node) for node in edges)

def pair_signature(left, right):
    left_id, right_id = left["id"], right["id"]
    return {
        "same_invariant": left.get("invariant") == right.get("invariant"),
        "shared_owner": bool(set(left.get("owners", [])) & set(right.get("owners", []))),
        "hard_dependency": (
            left_id in set(right.get("hard_dependencies", []))
            or right_id in set(left.get("hard_dependencies", []))
        ),
        "soft_dependency": (
            left_id in set(right.get("soft_dependencies", []))
            or right_id in set(left.get("soft_dependencies", []))
        ),
    }

def nonempty_unique_strings(value):
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
        and len(value) == len(set(value))
    )

def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())

def structured_r29_dispositions(value):
    required = {
        "readme", "public_docs", "current_release", "generated_owner",
        "install_route", "state_transition", "owner_source",
    }
    projection_dispositions = {"current", "historical", "delegated", "not-user-facing"}
    release_dispositions = {"prepublication", "published-current", "historical"}
    return (
        isinstance(value, dict)
        and set(value) == required
        and value["readme"] in projection_dispositions
        and value["public_docs"] in projection_dispositions
        and value["current_release"] in release_dispositions
        and all(nonempty_string(value[key]) for key in required - {"readme", "public_docs", "current_release"})
    )

def structured_r29_non_applicability(value):
    return (
        isinstance(value, dict)
        and set(value) == {"owner_source", "reason"}
        and all(nonempty_string(value[key]) for key in value)
    )

def structured_collision_control(control):
    required = {
        "left_write", "right_write", "left_acceptance", "right_acceptance",
        "reconciliation_point",
    }
    if not isinstance(control, dict) or set(control) != required:
        return False
    if not all(nonempty_unique_strings(control[key]) for key in required - {"reconciliation_point"}):
        return False
    if not isinstance(control["reconciliation_point"], str) or not control["reconciliation_point"].strip():
        return False
    return (
        set(control["left_write"]).isdisjoint(control["right_write"])
        and set(control["left_acceptance"]).isdisjoint(control["right_acceptance"])
    )

def pair_action_valid(signature, action, collision_control=None, grouped=False):
    if action not in pair_actions:
        return False
    if signature["same_invariant"] and action != "merge":
        return False
    if action == "parallel":
        if signature["hard_dependency"] or signature["soft_dependency"]:
            return False
        if signature["shared_owner"]:
            return not grouped and structured_collision_control(collision_control)
        return collision_control is None
    if collision_control is not None:
        return False
    return True

def verdict(case):
    finding = case.get("finding")
    if finding is not None:
        draft = case.get("draft", {})
        fields = set(draft.get("fields", []))
        if is_material(finding):
            if not material_fields <= fields:
                return "FAIL"
        elif not trivial_fields <= fields or not draft.get("concise"):
            return "FAIL"
    if case.get("durable_evidence") is False:
        return "FAIL"
    if case.get("reused_owner"):
        if case.get("repair_class") not in {"enforcement", "tightening", "new-rule"}:
            return "FAIL"
        if not case.get("distinct_invariant"):
            return "FAIL"
    if case.get("public_effect") == "release":
        if case.get("r29") != "applied" or not structured_r29_dispositions(case.get("r29_dispositions")):
            return "FAIL"
    if case.get("public_effect") == "none":
        if case.get("r29") != "not-applicable" or not structured_r29_non_applicability(case.get("r29_evidence")):
            return "FAIL"
    if re.search(
        r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+"
        r"(?:(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+|"
        r"https://github\.com/[^/\s]+/[^/\s]+/issues/\d+)\b",
        case.get("pr_link", ""),
    ):
        return "FAIL"
    if case.get("mutation_authority") == "issue-text":
        return "FAIL"
    if case.get("new_shipped_checker") and not case.get("r30_route"):
        return "FAIL"
    if case.get("user_facing_dialect") and (case.get("user_facing_dialect") != "british" or not case.get("canonical_literals_preserved")):
        return "FAIL"
    identity_fields = {"stable_id", "signed_hash", "filed_hash", "renewed_signoff", "issue_number", "readback"}
    if identity_fields & set(case):
        if not all(nonempty_string(case.get(key)) for key in ("stable_id", "signed_hash", "filed_hash")):
            return "FAIL"
        issue_number = case.get("issue_number")
        if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number <= 0:
            return "FAIL"
        if case.get("readback") is not True:
            return "FAIL"
        if case["signed_hash"] != case["filed_hash"] and case.get("renewed_signoff") is not True:
            return "FAIL"
    if case.get("publication_intent") is True:
        audit_object_ids = case.get("audit_object_ids")
        if not nonempty_unique_strings(audit_object_ids) or len(audit_object_ids) != 1:
            return "FAIL"
        if case.get("native_spine") is not True or case.get("separate_mode") is not False:
            return "FAIL"
        if case.get("extra_audit_object") is not False:
            return "FAIL"
    if case.get("embedded") is True:
        if case.get("publication_intent") is not True:
            return "FAIL"
        if case.get("nested_goal") is not False or case.get("second_run_root") is not False:
            return "FAIL"
    if case.get("publication_intent") is False:
        if case.get("work_order_route_loaded") is not False or case.get("extra_audit_object") is not False:
            return "FAIL"
        if any(case.get(key) is True for key in ("nested_goal", "second_run_root", "separate_mode")):
            return "FAIL"

    drafts = case.get("drafts", [])
    if drafts:
        if not isinstance(drafts, list) or not all(isinstance(draft, dict) for draft in drafts):
            return "FAIL"
        for draft in drafts:
            if not isinstance(draft.get("id"), str) or not draft["id"].strip():
                return "FAIL"
            if not isinstance(draft.get("invariant"), str) or not draft["invariant"].strip():
                return "FAIL"
            if not nonempty_unique_strings(draft.get("owners")):
                return "FAIL"
            for key in ("hard_dependencies", "soft_dependencies"):
                values = draft.get(key, [])
                if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                    return "FAIL"
                if len(values) != len(set(values)) or draft["id"] in values:
                    return "FAIL"
            if set(draft.get("hard_dependencies", [])) & set(draft.get("soft_dependencies", [])):
                return "FAIL"
        by_id = {d["id"]: d for d in drafts}
        if len(by_id) != len(drafts):
            return "FAIL"
        if has_cycle(drafts):
            return "FAIL"

        for draft in drafts:
            if not dependency_set(draft) <= set(by_id):
                return "FAIL"

        order = case.get("implementation_order", list(by_id))
        if set(order) != set(by_id) or len(order) != len(by_id):
            return "FAIL"
        positions = {draft_id: index for index, draft_id in enumerate(order)}
        for draft in drafts:
            for dep in dependency_set(draft):
                if dep not in positions or draft["id"] not in positions or positions[dep] > positions[draft["id"]]:
                    return "FAIL"

        required_pairs = {tuple(sorted(pair)) for pair in itertools.combinations(by_id, 2)}
        rows = case.get("pairs", [])
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            return "FAIL"
        row_keys = []
        for row in rows:
            a, b = row.get("a"), row.get("b")
            if a not in by_id or b not in by_id or a == b:
                return "FAIL"
            row_keys.append(tuple(sorted((a, b))))
        if len(row_keys) != len(set(row_keys)):
            return "FAIL"
        actual_pairs = set(row_keys)
        equivalent = case.get("equivalent_census", {})
        grouped = False
        if equivalent:
            if rows or not isinstance(equivalent, dict):
                return "FAIL"
            members = equivalent.get("members")
            if (
                not isinstance(members, list)
                or len(members) != len(by_id)
                or len(members) != len(set(members))
                or set(members) != set(by_id)
                or not isinstance(equivalent.get("justification"), str)
                or not equivalent["justification"].strip()
            ):
                return "FAIL"
            signatures = [pair_signature(by_id[a], by_id[b]) for a, b in required_pairs]
            basis = equivalent.get("basis")
            action = equivalent.get("action")
            grouped = (
                bool(signatures)
                and all(signature == signatures[0] for signature in signatures)
                and basis == signatures[0]
                and pair_action_valid(
                    signatures[0], action, equivalent.get("collision_control"), grouped=True
                )
            )
        if actual_pairs != required_pairs and not grouped:
            return "FAIL"

        pair_rows = {tuple(sorted((row["a"], row["b"]))): row for row in rows}
        for a, b in required_pairs:
            if (a, b) not in pair_rows:
                continue
            signature, row = pair_signature(by_id[a], by_id[b]), pair_rows[(a, b)]
            if not pair_action_valid(signature, row.get("action"), row.get("collision_control")):
                return "FAIL"
    return "PASS"

for case in all_cases:
    observed = verdict(case)
    if observed != case.get("expected"):
        raise SystemExit(f"{case['id']}: expected {case.get('expected')}, observed {observed}")

print(f"fixture-census: ok ({len(cases)}/{len(cases)} + {len(controls)}/{len(controls)} convergence controls)")

admission_cases = payload.get("admission_cases")
admission_controls = payload.get("admission_controls")
conditional_record_locators = payload.get("conditional_record_locators")
conditional_records = payload.get("conditional_records")
conditional_evidence_records = payload.get("conditional_evidence_records")
conditional_decision_records = payload.get("conditional_decision_records")
if not isinstance(admission_cases, list) or not isinstance(admission_controls, list) or not isinstance(conditional_record_locators, dict) or not isinstance(conditional_records, dict) or not isinstance(conditional_evidence_records, dict) or not isinstance(conditional_decision_records, dict):
    raise SystemExit("admission fixtures must contain cases, controls, and resolved record locators")

expected_admission_ids = [f"R31-A{i}" for i in range(1, 7)]
if [case.get("id") for case in admission_cases] != expected_admission_ids:
    raise SystemExit("admission case population/order mismatch")

allowed_admission_actions = {
    "NO_ACTION", "SUPPORTING_ARTIFACT", "AMEND_EXISTING_OWNER",
    "AMEND_EXISTING_RXX", "DEFER", "NEW_RXX",
}
def resolve_pointer(value, pointer):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return None
    for segment in pointer[1:].split("/"):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
    return value

def canonical_digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()

def outcome(action, stage, reason):
    return {"action": action, "stage": stage, "reason": reason}

def resolve_locator(locator, record_id):
    required = {"path", "pointer", "record_id", "sha256", "current"}
    if not isinstance(locator, dict) or set(locator) != required or locator.get("record_id") != record_id:
        return None, "INVALID_LOCATOR_SCHEMA"
    if locator.get("current") is not True:
        return None, "STALE_LOCATOR"
    path_value = locator.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        return None, "INVALID_LOCATOR_PATH"
    path = Path(path_value)
    root = Path.cwd().resolve()
    if path.is_absolute():
        return None, "ABSOLUTE_LOCATOR_PATH"
    target = (root / path).resolve()
    if root not in target.parents:
        return None, "LOCATOR_ESCAPES_REPOSITORY"
    if target != Path(sys.argv[1]).resolve() or not target.is_file():
        return None, "MISSING_LOCATOR_TARGET"
    resolved = resolve_pointer(json.loads(target.read_text(encoding="utf-8")), locator.get("pointer"))
    if not isinstance(resolved, dict):
        return None, "UNRESOLVED_LOCATOR_POINTER"
    if canonical_digest(resolved) != locator.get("sha256"):
        return None, "STALE_LOCATOR_DIGEST"
    return resolved, None

def normalize_facts(value):
    required = {"gap", "runtime_consumer", "owner", "overlap", "dependency", "supersession", "distinct", "census"}
    if not isinstance(value, dict) or set(value) != required:
        return None
    if value.get("gap") not in {"absent", "supporting-only", "present", "unresolved"}:
        return None
    if not isinstance(value.get("runtime_consumer"), bool):
        return None
    owner = value.get("owner")
    if not isinstance(owner, dict) or set(owner) != {"status", "owner", "rxx"}:
        return None
    if owner.get("status") not in {"none", "existing-owner", "existing-rxx", "unresolved"}:
        return None
    if owner.get("owner") is not None and (not isinstance(owner["owner"], str) or not owner["owner"].strip()):
        return None
    if owner.get("rxx") is not None and (not isinstance(owner["rxx"], str) or not owner["rxx"].strip()):
        return None
    if value.get("overlap") not in {"none", "owned", "unresolved"}:
        return None
    if value.get("dependency") not in {"resolved", "unresolved"}:
        return None
    if value.get("supersession") not in {"none", "amend", "reopen", "unresolved"}:
        return None
    distinct = value.get("distinct")
    if not isinstance(distinct, dict) or set(distinct) != {"failure", "consumer", "owner", "acceptance"} or not all(isinstance(distinct[key], bool) for key in distinct):
        return None
    census = value.get("census")
    if not isinstance(census, dict) or set(census) != {"complete", "open_closed"} or not all(isinstance(census[key], bool) for key in census):
        return None
    return value

def normalize_complete_record(record):
    scalar_fields = {"semantic_centre", "trigger", "non_trigger_cheap_path", "cheapest_discriminator"}
    if not all(isinstance(record.get(key), str) and record[key].strip() for key in scalar_fields):
        return None
    live_gap = record.get("live_gap")
    consumer = record.get("named_consumer")
    owner = record.get("owner_analysis")
    overlap = record.get("overlap_analysis")
    dependency = record.get("dependency_analysis")
    supersession = record.get("supersession_analysis")
    if not isinstance(live_gap, dict) or set(live_gap) != {"summary", "status"} or not isinstance(live_gap.get("summary"), str) or not live_gap["summary"].strip():
        return None
    if not isinstance(consumer, dict) or set(consumer) != {"name", "runtime"} or not isinstance(consumer.get("name"), str) or not consumer["name"].strip():
        return None
    if not isinstance(owner, dict) or set(owner) != {"summary", "status", "owner", "rxx"} or not isinstance(owner.get("summary"), str) or not owner["summary"].strip():
        return None
    for analysis in (overlap, dependency, supersession):
        if not isinstance(analysis, dict) or set(analysis) != {"summary", "status"} or not isinstance(analysis.get("summary"), str) or not analysis["summary"].strip():
            return None
    distinct = {}
    for name in ("failure", "consumer", "owner", "acceptance"):
        field = record.get(f"distinct_{name}")
        if not isinstance(field, dict) or set(field) != {"summary", "distinct"} or not isinstance(field.get("summary"), str) or not field["summary"].strip() or not isinstance(field.get("distinct"), bool):
            return None
        distinct[name] = field["distinct"]
    return normalize_facts({
        "gap": live_gap.get("status"),
        "runtime_consumer": consumer.get("runtime"),
        "owner": {"status": owner.get("status"), "owner": owner.get("owner"), "rxx": owner.get("rxx")},
        "overlap": overlap.get("status"),
        "dependency": dependency.get("status"),
        "supersession": supersession.get("status"),
        "distinct": distinct,
        "census": record.get("census"),
    })

def projection_route(facts):
    owner_status = facts["owner"]["status"]
    if facts["gap"] == "absent" and owner_status == "none":
        return "no-gap"
    if facts["gap"] == "supporting-only" and owner_status == "none":
        return "supporting-artifact"
    if facts["gap"] == "present" and owner_status == "existing-owner":
        return "existing-owner"
    if facts["gap"] == "present" and owner_status == "existing-rxx":
        return "existing-rxx"
    if facts["gap"] == "present" and owner_status == "none":
        return "unowned"
    return "unresolved"

def checked_projection(record_id, record, facts):
    owner = facts["owner"]
    expected = {
        "id": record_id,
        "current": record["current"],
        "selected_outcome": record["selected_outcome"],
        "decision": {
            "route": projection_route(facts),
            "runtime_consumer": facts["runtime_consumer"],
            "owner": owner["owner"],
            "rxx": owner["rxx"],
            "distinct": facts["distinct"],
            "census": facts["census"],
        },
        "authority_confirmed": record["authority_confirmed"],
    }
    return conditional_decision_records.get(record_id) == expected

def resolve_conditional_record(case):
    record_id = case.get("conditional_record_id")
    if not isinstance(record_id, str) or not record_id.strip():
        return None, "RECORD_RESOLUTION", "MISSING_RECORD_ID"
    locator = conditional_record_locators.get(record_id)
    record, reason = resolve_locator(locator, record_id)
    if record is None:
        return None, "RECORD_RESOLUTION", reason
    if record is not conditional_records.get(record_id) and record != conditional_records.get(record_id):
        return None, "RECORD_RESOLUTION", "RECORD_IDENTITY_MISMATCH"
    if canonical_digest(record) != case.get("expected_digest", locator["sha256"]):
        return None, "RECORD_RESOLUTION", "STALE_EXPECTED_DIGEST"
    if record.get("id") != record_id:
        return None, "COMPLETE_RECORD", "INCOMPLETE_COMPLETE_RECORD"
    if not isinstance(record.get("current"), bool) or not isinstance(record.get("authority_confirmed"), bool):
        return None, "COMPLETE_RECORD", "MISSING_CURRENT_OR_AUTHORITY"
    if record.get("selected_outcome") not in allowed_admission_actions:
        return None, "COMPLETE_RECORD", "INVALID_SELECTED_OUTCOME"
    facts = normalize_complete_record(record)
    locators = record.get("locators")
    if facts is None or not isinstance(locators, dict) or set(locators) != {"admission_evidence"}:
        return None, "EVIDENCE_RESOLUTION", "MISSING_TYPED_FACTS_OR_EVIDENCE_LOCATOR"
    resolved_evidence, reason = resolve_locator(locators["admission_evidence"], record_id)
    if resolved_evidence is None:
        return None, "EVIDENCE_RESOLUTION", reason
    expected_evidence = {"record_id": record_id, **facts}
    if resolved_evidence != expected_evidence or conditional_evidence_records.get(record_id) != expected_evidence:
        return None, "EVIDENCE_RECONCILIATION", "CONTRADICTORY_COMPLETE_EVIDENCE"
    if not checked_projection(record_id, record, facts):
        return None, "DERIVATIVE_CHECK", "COMPACT_PROJECTION_MISMATCH"
    return {"record": record, "facts": facts}, None, None

def decision_action(normalized):
    record, facts = normalized["record"], normalized["facts"]
    if record["current"] is not True:
        return outcome("DEFER", "CURRENTNESS_AUTHORITY", "EVIDENCE_NOT_CURRENT")
    if record["authority_confirmed"] is not True:
        return outcome("DEFER", "CURRENTNESS_AUTHORITY", "AUTHORITY_NOT_CONFIRMED")
    owner = facts["owner"]
    distinct = facts["distinct"]
    if facts["gap"] == "absent" and facts["runtime_consumer"] is False and owner == {"status": "none", "owner": None, "rxx": None} and facts["overlap"] == "none" and facts["supersession"] == "none":
        return outcome("NO_ACTION", "ROUTE_SELECTED", "NO_DISTINCT_GAP")
    if facts["gap"] == "supporting-only":
        if facts["runtime_consumer"] is not False:
            return outcome("REJECT", "ROUTE_PREDICATE", "SUPPORTING_ARTIFACT_HAS_RUNTIME_CONSUMER")
        if owner == {"status": "none", "owner": None, "rxx": None} and facts["overlap"] == "none" and facts["supersession"] == "none":
            return outcome("SUPPORTING_ARTIFACT", "ROUTE_SELECTED", "SUPPORTING_ONLY_NO_RUNTIME_CONSUMER")
    if facts["gap"] == "present" and facts["runtime_consumer"] is True and owner["status"] == "existing-owner" and isinstance(owner["owner"], str) and owner["rxx"] is None and facts["overlap"] == "owned" and facts["supersession"] == "amend" and distinct["owner"] is False:
        return outcome("AMEND_EXISTING_OWNER", "ROUTE_SELECTED", "EXISTING_OWNER_OWNS_INVARIANT")
    if facts["gap"] == "present" and facts["runtime_consumer"] is True and owner["status"] == "existing-rxx" and isinstance(owner["owner"], str) and isinstance(owner["rxx"], str) and facts["overlap"] == "owned" and facts["supersession"] == "reopen" and distinct["owner"] is False:
        return outcome("AMEND_EXISTING_RXX", "ROUTE_SELECTED", "EXISTING_RXX_OWNS_INVARIANT")
    if facts["gap"] == "present" and facts["runtime_consumer"] is True and owner == {"status": "none", "owner": None, "rxx": None} and facts["overlap"] == "none" and facts["supersession"] == "none" and all(distinct[key] is True for key in ("failure", "consumer", "owner", "acceptance")):
        return outcome("NEW_RXX", "ROUTE_SELECTED", "DISTINCT_UNOWNED_INVARIANT")
    return outcome("REJECT", "ROUTE_PREDICATE", "CONTRADICTORY_ADMISSION_SEMANTICS")

def admission_action(case):
    normalized, stage, reason = resolve_conditional_record(case)
    if normalized is None:
        return outcome("REJECT", stage, reason)
    result = decision_action(normalized)
    action = result["action"]
    record, facts = normalized["record"], normalized["facts"]
    if action == "REJECT":
        return result
    if record["selected_outcome"] != action:
        return outcome("REJECT", "DERIVATIVE_CHECK", "SELECTED_OUTCOME_MISMATCH")
    allocated_rxx = case.get("allocated_rxx")
    has_number = isinstance(allocated_rxx, str) and bool(allocated_rxx.strip())
    if action in {"AMEND_EXISTING_OWNER", "AMEND_EXISTING_RXX"}:
        existing_owner = case.get("existing_owner")
        if existing_owner != facts["owner"]["owner"] or case.get("new_owner"):
            return outcome("REJECT", "OWNER_BINDING", "OWNER_IDENTITY_MISMATCH")
    if action == "AMEND_EXISTING_RXX":
        existing_rxx = case.get("existing_rxx")
        if existing_rxx != facts["owner"]["rxx"]:
            return outcome("REJECT", "OWNER_BINDING", "RXX_IDENTITY_MISMATCH")
    if action == "NEW_RXX":
        census = facts["census"]
        if census["complete"] is not True or census["open_closed"] is not True:
            return outcome("REJECT", "CENSUS_GATE", "INCOMPLETE_OPEN_CLOSED_CENSUS")
        if not has_number:
            return outcome("REJECT", "NUMBER_GATE", "NEW_RXX_NUMBER_MISSING")
        return result
    if has_number:
        return outcome("REJECT", "NUMBER_GATE", "NON_NEW_RXX_NUMBER_FORBIDDEN")
    return result

def assert_admission_result(case, result):
    if result["action"] != case.get("expected"):
        raise SystemExit(f"{case.get('id')}: expected {case.get('expected')}, observed {result['action']} at {result['stage']} ({result['reason']})")
    if "expected_stage" in case and result["stage"] != case["expected_stage"]:
        raise SystemExit(f"{case.get('id')}: expected stage {case['expected_stage']}, observed {result['stage']} ({result['reason']})")
    if "expected_reason" in case and result["reason"] != case["expected_reason"]:
        raise SystemExit(f"{case.get('id')}: expected reason {case['expected_reason']}, observed {result['reason']} at {result['stage']}")

for case in admission_cases:
    observed = admission_action(case)
    if observed["action"] not in allowed_admission_actions:
        raise SystemExit(f"{case['id']}: admission did not produce an allowed action: {observed['action']}")
    assert_admission_result(case, observed)

for control in admission_controls:
    assert_admission_result(control, admission_action(control))

print("admission-census: ok (six exclusive actions; normalized resolved evidence before route and allocation)")
PY

"${py_cmd[@]}" - "$model_input" "$model_expectations" <<'PY'
import json
import sys
from pathlib import Path

mission = Path(sys.argv[1]).read_text(encoding="utf-8")
expected = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if expected.get("schema_version") != 1:
    raise SystemExit("model-cell expectations schema_version must be 1")
for phrase in expected.get("forbidden_mission_phrases", []):
    if phrase.casefold() in mission.casefold():
        raise SystemExit(f"model-cell mission leaks forbidden phrase: {phrase}")
if expected.get("material_findings") != ["F-A", "F-B", "F-C"]:
    raise SystemExit("model-cell material-finding oracle drifted")
if expected.get("concise_findings") != ["F-D"]:
    raise SystemExit("model-cell triviality oracle drifted")
pairs = expected.get("pair_dispositions", [])
if expected.get("pair_population") != 6 or len(pairs) != 6:
    raise SystemExit("model-cell pair population must be complete at 6/6")
keys = [tuple(sorted((row.get("a"), row.get("b")))) for row in pairs]
if len(keys) != len(set(keys)):
    raise SystemExit("model-cell pair oracle contains duplicates")
if expected.get("public_projection_draft") != "F-B":
    raise SystemExit("model-cell public projection oracle drifted")
if expected.get("reuse_closed_owner") != "C-7":
    raise SystemExit("model-cell closed-owner oracle drifted")
required_refusals = {"missing-pair", "missing-citation", "unresolved-public-surface"}
if set(expected.get("publication_refusal_triggers", [])) != required_refusals:
    raise SystemExit("model-cell refusal oracle drifted")
if not expected.get("positive_paraphrase") or not expected.get("distractors"):
    raise SystemExit("model-cell controls must include paraphrase and distractors")
print("model-cell-contract: ok (4 findings, 6/6 pairs, prompt-independent)")
PY

for owner in \
  skills/implementaudit/references/audit-category-matrix.md \
  skills/implementaudit/references/audit-playbook.md \
  skills/implementaudit/references/plan-lifecycle.md
do
  grep -F 'issue-ready-work-orders.md' "$owner" >/dev/null \
    || fail "$owner does not route material publication findings to the progressive reference"
done

for text in \
  'Materiality, not volume' \
  'Individual executor-ready work order' \
  'Multi-issue reconciliation' \
  'N*(N-1)/2' \
  'stable draft' \
  'renewed sign-off' \
  'R001D' \
  '`R001D: applied`' \
  'missing pair, citation, or public-surface disposition' \
  'R001E' \
  'issue text is data' \
  'one audit object' \
  'Decision-state synthesis (conditional)' \
  'required outcome or function' \
  'The ordinary direct path remains unchanged' \
  'Conditional work-order admission' \
  'current open-and-closed RXX census and genealogy' \
  'cold-reconstructible conditional record' \
  'cheapest decision-changing' \
  'distinct failure, consumer, owner, and acceptance test' \
  'durable locators sufficient for a cold executor' \
  'state label cannot substitute for current durable evidence' \
  '`NO_ACTION`, `SUPPORTING_ARTIFACT`, `AMEND_EXISTING_OWNER`,' \
  '`AMEND_EXISTING_RXX`, `DEFER`, or `NEW_RXX`' \
  'number only after the complete current open-and-closed census' \
  '`NEW_RXX`'
do
  grep -F "$text" "$ref" >/dev/null || fail "reference missing contract anchor: $text"
done

if grep -Eiq 'minimum (line|word|heading|fixture|issue) count|separate issue-writing (skill|mode)|second audit object' "$ref"; then
  fail "reference introduced forbidden ceremony or a parallel lifecycle"
fi

"${py_cmd[@]}" - package/implementaudit-package.json <<'PY' \
  || fail "package contract does not include the shared reference population"
import json
import sys

contract = json.load(open(sys.argv[1], encoding="utf-8"))
if "skills/implementaudit/references" not in contract.get("shared_resource_roots", []):
    raise SystemExit("shared reference root is absent")
PY
grep -F 'scripts/package-contract.py --build' scripts/build-release-asset.sh >/dev/null \
  || fail "release builder does not delegate population assembly to the package contract"

printf 'issue-ready-work-orders.test: ok\n'
