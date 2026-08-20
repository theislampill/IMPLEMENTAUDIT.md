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
if not isinstance(admission_cases, list) or not isinstance(admission_controls, list):
    raise SystemExit("admission fixtures must contain cases and controls")

expected_admission_ids = [f"R31-A{i}" for i in range(1, 7)]
if [case.get("id") for case in admission_cases] != expected_admission_ids:
    raise SystemExit("admission case population/order mismatch")

allowed_admission_actions = {
    "NO_ACTION", "SUPPORTING_ARTIFACT", "AMEND_EXISTING_OWNER",
    "AMEND_EXISTING_RXX", "DEFER", "NEW_RXX",
}

def admission_action(case):
    state = case.get("state")
    allocated_rxx = case.get("allocated_rxx")
    has_number = isinstance(allocated_rxx, str) and bool(allocated_rxx.strip())
    if not case.get("evidence_current") or not case.get("authority_confirmed"):
        action = "DEFER"
    elif state == "no-gap":
        action = "NO_ACTION"
    elif state == "cross-cutting-note-no-runtime-consumer" and case.get("runtime_consumer") is False:
        action = "SUPPORTING_ARTIFACT"
    elif state == "existing-owner-needs-amendment":
        action = "AMEND_EXISTING_OWNER"
    elif state == "existing-rxx-needs-amendment":
        action = "AMEND_EXISTING_RXX"
    elif state == "distinct-unowned-invariant":
        action = "NEW_RXX"
    else:
        return "REJECT"
    if action in {"AMEND_EXISTING_OWNER", "AMEND_EXISTING_RXX"}:
        existing_owner = case.get("existing_owner")
        if not isinstance(existing_owner, str) or not existing_owner.strip() or case.get("new_owner"):
            return "REJECT"
    if action == "AMEND_EXISTING_RXX":
        existing_rxx = case.get("existing_rxx")
        if not isinstance(existing_rxx, str) or not existing_rxx.strip():
            return "REJECT"
    if action == "NEW_RXX":
        return action if (
            has_number
            and case.get("complete_admission_census") is True
            and case.get("current_open_and_closed_census") is True
        ) else "REJECT"
    return action if not has_number else "REJECT"

for case in admission_cases:
    observed = admission_action(case)
    if observed not in allowed_admission_actions:
        raise SystemExit(f"{case['id']}: admission did not produce an allowed action: {observed}")
    if observed != case.get("expected"):
        raise SystemExit(f"{case['id']}: expected {case.get('expected')}, observed {observed}")

for control in admission_controls:
    observed = admission_action(control)
    if observed != control.get("expected"):
        raise SystemExit(f"{control.get('id')}: expected {control.get('expected')}, observed {observed}")

print("admission-census: ok (six exclusive actions; census before NEW_RXX allocation)")
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
