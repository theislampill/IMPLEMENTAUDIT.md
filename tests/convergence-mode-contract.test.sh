#!/usr/bin/env bash
set -euo pipefail

# Governed state-space convergence mode (#11, #160), qualified/optional:
# the progressive reference owns the full triggered method while SKILL.md
# retains only its truthful load route. Repo-only fixtures qualify the
# structural, cheap-path, independence, and evaluator boundaries.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

ref="skills/implementaudit/references/convergence-mode.md"
skill="skills/implementaudit/SKILL.md"
fx="fixtures/convergence-mode"
r32="$fx/R0020"
fail() { printf 'convergence-mode-contract: %s\n' "$*" >&2; exit 1; }

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "Python 3 is required for R0020 deterministic fixture validation"
fi

[ -f "$ref" ] || fail "optional reference $ref missing"
flat="$(tr '\n' ' ' < "$ref" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'qualified.*optional.*progressive' \
  || fail "reference must declare the qualified optional progressive disposition"
printf '%s' "$flat" | grep -qi 'When it applies (trigger)' || fail "trigger section missing"
printf '%s' "$flat" | grep -qi 'second independently verified rejection' \
  || fail "second independently verified rejection hypothesis missing"
for branch in duplicate unrelated unresolved-family cheap-path; do
  printf '%s' "$flat" | grep -Fqi "$branch" \
    || fail "family classifier branch missing: $branch"
done
printf '%s' "$flat" | grep -qi 'Enumeration artefact' || fail "enumeration artefact step missing"
printf '%s' "$flat" | grep -qi 'exactly one outer qualification' || fail "single-outer-qualification missing"
printf '%s' "$flat" | grep -qi 'valid states' \
  || fail "explicit valid-state representation missing"
printf '%s' "$flat" | grep -qi 'state payload' \
  || fail "state-payload requirement missing"
printf '%s' "$flat" | grep -qi 'expected invariant.*discriminator outcome' \
  || fail "held-out expected-outcome binding missing"
printf '%s' "$flat" | grep -qi 'deterministic payload evaluator' \
  || fail "held-out deterministic payload evaluator missing"
printf '%s' "$flat" | grep -qi 'distractor objects' \
  || fail "resolvable distractor-object requirement missing"
printf '%s' "$flat" | grep -qi 'referential binding' \
  || fail "state-model referential-binding requirement missing"
printf '%s' "$flat" | grep -qi 'Every included failure.*family.*dimension.*class.*mutation' \
  || fail "all-included failure binding requirement missing"
printf '%s' "$flat" | grep -qi 'independently verified subset.*trigger' \
  || fail "verified-only trigger-formation boundary missing"
printf '%s' "$flat" | grep -qi 'single-fault fixture .* must NOT trigger\|must NOT trigger' \
  || fail "negative-control (must-not-trigger) missing"
printf '%s' "$flat" | grep -qi 'escalate-to-convergence-mode' \
  || fail "mechanism-replacement evidence producer missing"
printf '%s' "$flat" | grep -qi 'materially ambiguous' \
  || fail "material family ambiguity trigger missing"
printf '%s' "$flat" | grep -qi 'exploratory hypothesis discrimination' \
  || fail "R0022 informational-independence delegation missing"
printf '%s' "$flat" | grep -qi 'authoritative common facts' \
  || fail "R0022 common-facts boundary missing"
printf '%s' "$flat" | grep -qi 'conclusion-neutral' \
  || fail "R0022 conclusion-neutral first-pass boundary missing"
printf '%s' "$flat" | grep -qi 'Smoke A.*Smoke B' \
  || fail "temporal Smoke A/B axis missing"
printf '%s' "$flat" | grep -qi 'original failing witness' \
  || fail "R0023 original-witness boundary missing"
printf '%s' "$flat" | grep -qi 'evaluator identity' \
  || fail "R0023 evaluator-identity boundary missing"
printf '%s' "$flat" | grep -Fqi 'P4-16' \
  || fail "R0023 post-failure evaluator route missing"
printf '%s' "$flat" | grep -qi 'external.*unproved\|unproved.*external' \
  || fail "external-validity limit missing"

skill_route="$(grep -F 'references/convergence-mode.md' "$skill" || true)"
printf '%s' "$skill_route" | grep -qi 'qualified.*optional' \
  || fail "SKILL load route does not reflect qualified optional status"
printf '%s' "$skill_route" | grep -qi 'EXPERIMENTAL' && \
  fail "SKILL load route still labels the qualified reference experimental"

# Progressive disclosure: the reference must NOT be inlined into the
# bootloader path. SKILL.md may POINT to it, but not carry its body — guard
# the budget by asserting the trigger prose is not duplicated in SKILL.md.
if grep -qi 'bounded read-only discovery' "$skill"; then
  fail "convergence-mode body leaked into the bootloader SKILL.md (must stay in references/, on-trigger)"
fi

# Fixtures well-formed.
grep -q '^expected_trigger: yes' "$fx/under-specified-3d.md" \
  || fail "positive fixture must declare expected_trigger: yes"
grep -q '^expected_enumeration_dimensions: 3' "$fx/under-specified-3d.md" \
  || fail "positive fixture must declare 3 enumeration dimensions"
grep -q '^expected_trigger: no' "$fx/single-fault-control.md" \
  || fail "negative control must declare expected_trigger: no"

# R0020 independent qualification bank. The fixtures are repo-only evidence;
# the shipped reference and load route carry the final narrow activation.
incident_bank="$r32/incident-population.json"
case_bank="$r32/cases.json"
[ -f "$incident_bank" ] || fail "R0020 incident population missing: $incident_bank"
[ -f "$case_bank" ] || fail "R0020 deterministic case bank missing: $case_bank"

"${py_cmd[@]}" - "$incident_bank" "$case_bank" <<'PY'
import json
import re
import sys
import copy
from collections import Counter
from pathlib import Path


def die(message):
    raise SystemExit(f"convergence-mode-contract: {message}")


def load(path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                die(f"duplicate JSON member in {path}: {key}")
            result[key] = value
        return result
    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
        )
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot load {path}: {exc}")


incidents = load(sys.argv[1])
cases = load(sys.argv[2])

if cases.get("schema") != "implementaudit-r32-deterministic-cases-v2":
    die("R0020 case bank schema does not identify the reconstructible state model")
evidence_boundary = cases.get("evidence_boundary", "")
if "qualified optional" not in evidence_boundary or "external effectiveness unproved" not in evidence_boundary:
    die("R0020 case bank evidence boundary is stale or overclaims external validity")

# A denominator is an enumerated population, never a declared number alone.
receipts = incidents.get("receipts")
if not isinstance(receipts, list) or not receipts:
    die("incident receipts must be a nonempty list")
receipt_ids = [row.get("id") for row in receipts]
if any(not isinstance(value, str) or not value for value in receipt_ids):
    die("every incident receipt needs a nonempty id")
if len(receipt_ids) != len(set(receipt_ids)):
    die("incident receipt ids must be unique")

claims = []
for receipt in receipts:
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("head", ""))):
        die(f"{receipt['id']} lacks an exact 40-hex head")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("tree", ""))):
        die(f"{receipt['id']} lacks an exact 40-hex tree")
    locator = receipt.get("locator")
    if not isinstance(locator, str) or not locator:
        die(f"{receipt['id']} lacks a durable locator")
    rows = receipt.get("findings")
    if not isinstance(rows, list):
        die(f"{receipt['id']} findings must be a list")
    for finding in rows:
        if not isinstance(finding, dict):
            die(f"{receipt['id']} has a non-object finding")
        claims.append((receipt, finding))

claim_ids = [finding.get("id") for _, finding in claims]
if any(not isinstance(value, str) or not value for value in claim_ids):
    die("every incident finding needs a nonempty id")
if len(claim_ids) != len(set(claim_ids)):
    die("incident finding ids must be unique")
expected_claim_ids = (
    {f"R30-F{number:02d}" for number in range(1, 9)}
    | {f"G144-F{number:02d}" for number in range(1, 30)}
    | {f"R31-F{number:02d}" for number in range(1, 12)}
)
if set(claim_ids) != expected_claim_ids:
    die("incident finding population differs from the audited 48-claim denominator")

allowed_dispositions = {"included", "excluded", "duplicate", "ambiguous"}
counts = Counter()
for receipt, finding in claims:
    disposition = finding.get("disposition")
    if disposition not in allowed_dispositions:
        die(f"{finding['id']} has invalid disposition {disposition!r}")
    counts[disposition] += 1
    reason = finding.get("reason")
    if not isinstance(reason, str) or not reason:
        die(f"{finding['id']} lacks disposition reason")
    if disposition == "duplicate" and finding.get("duplicate_of") not in claim_ids:
        die(f"{finding['id']} lacks a valid duplicate_of target")
    if disposition == "ambiguous" and not finding.get("next_evidence"):
        die(f"{finding['id']} lacks a bounded next-evidence step")
    if disposition == "included":
        for field in ("owner", "invariant", "mechanism", "state_dimension"):
            if not isinstance(finding.get(field), str) or not finding[field]:
                die(f"{finding['id']} included claim lacks {field}")

declared = incidents.get("population")
observed = {
    "total": len(claims),
    "included": counts["included"],
    "excluded": counts["excluded"],
    "duplicate": counts["duplicate"],
    "ambiguous": counts["ambiguous"],
}
expected_population = {
    "total": 48, "included": 45, "excluded": 3,
    "duplicate": 0, "ambiguous": 0,
}
if observed != expected_population:
    die(f"audited incident population changed: {observed}")
if declared != observed:
    die(f"incident denominator mismatch: declared={declared} observed={observed}")

by_campaign = Counter(receipt.get("campaign") for receipt, _ in claims)
expected_campaign_counts = {"#144": 29, "R001E": 8, "R001F": 11}
if dict(sorted(by_campaign.items())) != expected_campaign_counts:
    die("enumerated campaign counts differ from the audited population")
if incidents.get("campaign_counts") != expected_campaign_counts:
    die("campaign finding counts do not match the enumerated receipts")


required_failure_fields = {
    "owner", "invariant", "mechanism", "state_dimension", "state_class",
    "mutation_relation", "independently_verified",
}
allowed_mutations = {
    "rename-label", "paraphrase-message", "move-path", "delete-required-field",
    "boundary-shift", "adjacent-class", "polarity-flip", "reorder-sequence",
}


def evaluate_expected_invariant(record, state):
    invariant = record["invariant"]
    if invariant == "packaged-helper-same-run-dispatch":
        argv = state.get("argv")
        invokes_helper = (
            isinstance(argv, list)
            and any(isinstance(value, str) and value.endswith("helper.sh") for value in argv)
            and "-n" not in argv
        )
        return "pass" if invokes_helper else "fail"
    if invariant == "scope-population-freshness":
        return "pass" if state.get("path") and state.get("ignored") is False else "fail"
    if invariant == "reject-duplicate-keys":
        raw = state.get("json", "")
        return "fail" if isinstance(raw, str) and raw.count('"key"') > 1 else "pass"
    if invariant == "route-by-kind":
        kind = state.get("kind")
        return "pass" if isinstance(kind, str) and bool(kind.strip()) else "fail"
    if invariant == "stable-path-normalisation":
        path = state.get("path")
        doubled = isinstance(path, str) and (path.endswith("//") or path.endswith("\\\\"))
        return "pass" if isinstance(path, str) and path and not doubled else "fail"
    if invariant == "preserve-owner":
        owner = state.get("owner")
        return "pass" if isinstance(owner, str) and owner.startswith("src/owner") else "fail"
    die(f"no deterministic payload evaluator for invariant {invariant}")


def evaluate_current_model(record, state, expected):
    mechanism = record["mechanism"]
    if mechanism == "last-write-wins" and isinstance(state.get("json"), str):
        return "pass"
    if mechanism in {
        "helper-caller-evidence-false-pass", "population-census-divergence",
        "fallthrough", "separator-only-repair", "owner-substitution",
    }:
        return expected
    die(f"no deterministic current-model evaluator for mechanism {mechanism}")


def derive_held_out_outcomes(record, cell):
    state = cell["state"]
    payload_family = state.get("family")
    if not isinstance(payload_family, dict):
        die(f"{cell.get('id')} held-out state lacks payload family binding")
    expected_family = {field: record[field] for field in ("owner", "invariant", "mechanism")}
    expected_invariant = evaluate_expected_invariant(record, state)
    observed_invariant = evaluate_current_model(record, state, expected_invariant)
    expected_discriminator = "same-family"
    observed_discriminator = "same-family" if payload_family == expected_family else "not-family"
    return {
        "expected_invariant": expected_invariant,
        "observed_invariant": observed_invariant,
        "expected_discriminator": expected_discriminator,
        "observed_discriminator": observed_discriminator,
    }


def classify(case):
    failures = case.get("failures")
    if not isinstance(failures, list):
        die(f"{case['id']} failures must be a list")
    work = case.get("work", {})
    if work.get("trivial") or (work.get("local") and work.get("reversible") and len(failures) < 2):
        return "cheap-path"
    verified = [row for row in failures if row.get("independently_verified") is True]
    if len(verified) < 2:
        return "cheap-path"
    if any(not required_failure_fields.issubset(row) for row in verified):
        return "unresolved-family"
    if case.get("family_disputed"):
        return "unresolved-family"
    signature_fields = (
        "owner", "invariant", "mechanism", "state_dimension", "state_class",
        "mutation_relation",
    )
    signatures = [tuple(row[field] for field in signature_fields) for row in verified]
    if len(signatures) != len(set(signatures)):
        return "duplicate"
    keys = ("owner", "invariant", "mechanism")
    if any(len({row[field] for row in verified}) != 1 for field in keys):
        return "unrelated"
    if any(not row[field] for row in verified for field in required_failure_fields - {"independently_verified"}):
        return "unresolved-family"
    if not any(row["mutation_relation"] in allowed_mutations for row in verified[1:]):
        return "unresolved-family"
    if case.get("local_repair_retires_shared_residual"):
        return "cheap-path"
    return "convergence"


def validate_record(case, route):
    record = case.get("record")
    if route != "convergence":
        if record is not None or case.get("model_call"):
            die(f"{case['id']} imposes convergence work on route {route}")
        return
    if not isinstance(record, dict):
        die(f"{case['id']} convergence route lacks a record")
    for field in (
        "owner", "invariant", "mechanism", "included", "excluded", "dimensions", "classes",
        "valid_states", "distractors", "held_out_ids",
        "malformed_states", "boundary_states", "adjacent_states", "mutation_operators",
        "red_witnesses", "held_out", "outer_qualification", "review_yield",
    ):
        value = record.get(field)
        if value in (None, "", [], {}):
            die(f"{case['id']} convergence record lacks {field}")
    dimensions = record["dimensions"]
    if (not all(isinstance(value, str) and value for value in dimensions)
            or len(dimensions) != len(set(dimensions))):
        die(f"{case['id']} dimensions must be unique nonempty ids")
    classes = record["classes"]
    if not all(isinstance(value, dict) for value in classes):
        die(f"{case['id']} classes must bind ids to dimensions")
    class_ids = [value.get("id") for value in classes]
    if (any(not isinstance(value, str) or not value for value in class_ids)
            or len(class_ids) != len(set(class_ids))):
        die(f"{case['id']} class ids must be unique and nonempty")
    class_dimensions = {value["id"]: value.get("dimension") for value in classes}
    for class_id, dimension in class_dimensions.items():
        if dimension not in dimensions:
            die(f"{case['id']} class {class_id} references unknown dimension")

    mutations = record["mutation_operators"]
    if not all(isinstance(value, dict) for value in mutations):
        die(f"{case['id']} mutation operators must be bound objects")
    mutation_ids = [value.get("id") for value in mutations]
    mutation_keys = [(value.get("id"), value.get("dimension")) for value in mutations]
    if (any(value not in allowed_mutations for value in mutation_ids)
            or len(mutation_keys) != len(set(mutation_keys))):
        die(f"{case['id']} uses an unbounded or duplicate mutation binding")
    for mutation in mutations:
        dimension = mutation.get("dimension")
        if dimension not in dimensions:
            die(f"{case['id']} mutation {mutation.get('id')} references unknown dimension")
        for endpoint in ("from_class", "to_class"):
            class_id = mutation.get(endpoint)
            if class_id not in class_dimensions:
                die(f"{case['id']} mutation {mutation.get('id')} references unknown class")
            if class_dimensions[class_id] != dimension:
                die(f"{case['id']} mutation {mutation.get('id')} crosses an unbound dimension")

    members = record["included"]
    failure_ids = [row["id"] for row in case["failures"]]
    if set(members) != set(failure_ids) or len(members) != len(set(members)):
        die(f"{case['id']} included ids do not resolve to the failure population")
    if set(record["red_witnesses"]) != set(members):
        die(f"{case['id']} RED witnesses do not resolve to the included population")
    if set(record["included"]) & set(record["excluded"]):
        die(f"{case['id']} included and excluded populations overlap")
    failure_by_id = {row["id"]: row for row in case["failures"]}
    included_failures = [failure_by_id[member] for member in members]
    for failure in included_failures:
        if any(field not in failure for field in required_failure_fields):
            die(f"{case['id']} included failure {failure['id']} lacks family or state binding")
        if any(not failure[field] for field in required_failure_fields - {"independently_verified"}):
            die(f"{case['id']} included failure {failure['id']} has an empty family or state binding")
        if not isinstance(failure["independently_verified"], bool):
            die(f"{case['id']} included failure {failure['id']} lacks a boolean verification disposition")
    family_fields = ("owner", "invariant", "mechanism")
    record_family = tuple(record[field] for field in family_fields)
    included_families = {tuple(row[field] for field in family_fields) for row in included_failures}
    if len(included_families) != 1:
        unbound = next(row for row in included_failures
                       if tuple(row[field] for field in family_fields) != record_family)
        die(f"{case['id']} included failure {unbound['id']} differs from the record family")
    for field in ("owner", "invariant", "mechanism"):
        if record[field] != included_failures[0][field]:
            die(f"{case['id']} record {field} differs from the failure family")
    for failure in included_failures:
        dimension = failure["state_dimension"]
        class_id = failure["state_class"]
        if dimension not in dimensions:
            die(f"{case['id']} failure {failure['id']} references unknown dimension")
        if class_id not in class_dimensions or class_dimensions[class_id] != dimension:
            die(f"{case['id']} failure {failure['id']} references unknown class")
        mutation_key = (failure["mutation_relation"], dimension)
        if mutation_key not in mutation_keys:
            die(f"{case['id']} failure {failure['id']} references unknown mutation")
        bound_mutation = next(value for value in mutations
                              if (value["id"], value["dimension"]) == mutation_key)
        if class_id not in {bound_mutation["from_class"], bound_mutation["to_class"]}:
            die(f"{case['id']} failure {failure['id']} class is not bound to its mutation")

    state_ids = set()
    for state_kind in ("valid_states", "malformed_states", "boundary_states", "adjacent_states"):
        states = record[state_kind]
        if not isinstance(states, list) or not states:
            die(f"{case['id']} lacks {state_kind}")
        for state in states:
            if not isinstance(state, dict):
                die(f"{case['id']} {state_kind} must contain state objects")
            state_id = state.get("id")
            if not isinstance(state_id, str) or not state_id or state_id in state_ids:
                die(f"{case['id']} has a duplicate or empty state id")
            state_ids.add(state_id)
            dimension = state.get("dimension")
            class_id = state.get("class")
            if dimension not in dimensions:
                die(f"{case['id']} state {state_id} references unknown dimension")
            if class_id not in class_dimensions or class_dimensions[class_id] != dimension:
                die(f"{case['id']} state {state_id} references unknown class")
            if not isinstance(state.get("payload"), dict) or not state["payload"]:
                die(f"{case['id']} state {state_id} lacks payload")
            if state.get("expected_invariant") not in {"pass", "fail"}:
                die(f"{case['id']} state {state_id} lacks expected invariant outcome")
            if state_kind == "valid_states" and state["expected_invariant"] != "pass":
                die(f"{case['id']} valid state {state_id} does not satisfy the invariant")
            if state_kind == "malformed_states" and state["expected_invariant"] != "fail":
                die(f"{case['id']} malformed state {state_id} does not violate the invariant")

    distractors = record["distractors"]
    if not isinstance(distractors, list) or not distractors:
        die(f"{case['id']} lacks distractor objects")
    distractor_ids = [row.get("id") for row in distractors]
    if set(record["excluded"]) != set(distractor_ids) or len(distractor_ids) != len(set(distractor_ids)):
        die(f"{case['id']} excluded ids do not resolve to distractor objects")
    if set(distractor_ids) & set(failure_ids):
        die(f"{case['id']} distractor ids overlap the included failure population")
    for distractor in distractors:
        for field in ("id", "owner", "invariant", "mechanism", "state_dimension", "state_class", "mutation_relation", "exclusion_reason"):
            if not isinstance(distractor.get(field), str) or not distractor[field]:
                die(f"{case['id']} distractor lacks {field}")
        if not isinstance(distractor.get("payload"), dict) or not distractor["payload"]:
            die(f"{case['id']} distractor {distractor['id']} lacks payload")
        if all(distractor[field] == record[field] for field in ("owner", "invariant", "mechanism")):
            die(f"{case['id']} distractor belongs to the included failure family")

    held_out = record["held_out"]
    held_out_ids = [cell.get("id") for cell in held_out]
    if set(record["held_out_ids"]) != set(held_out_ids) or len(held_out_ids) != len(set(held_out_ids)):
        die(f"{case['id']} held_out_ids do not resolve to held-out states")
    if set(held_out_ids) & (set(failure_ids) | set(distractor_ids) | state_ids):
        die(f"{case['id']} held-out ids overlap another state population")
    for cell in held_out:
        if not isinstance(cell.get("state"), dict) or not cell["state"]:
            die(f"{case['id']} held-out state lacks payload")
        dimension = cell.get("dimension")
        class_id = cell.get("class")
        mutation = cell.get("mutation")
        if dimension not in dimensions:
            die(f"{case['id']} held-out {cell.get('id')} references unknown dimension")
        if class_id not in class_dimensions or class_dimensions[class_id] != dimension:
            die(f"{case['id']} held-out {cell.get('id')} references unknown class")
        mutation_key = (mutation, dimension)
        if mutation_key not in mutation_keys:
            die(f"{case['id']} held-out {cell.get('id')} references unknown mutation")
        bound_mutation = next(value for value in mutations
                              if (value["id"], value["dimension"]) == mutation_key)
        if class_id != bound_mutation["to_class"]:
            die(f"{case['id']} held-out {cell.get('id')} is not the mutation target class")
        if cell.get("expected_invariant") not in {"pass", "fail"} or cell.get("observed_invariant") not in {"pass", "fail"}:
            die(f"{case['id']} held-out {cell.get('id')} lacks invariant outcomes")
        if cell.get("expected_discriminator") not in {"same-family", "not-family"} or cell.get("observed_discriminator") not in {"same-family", "not-family"}:
            die(f"{case['id']} held-out {cell.get('id')} lacks discriminator outcomes")
        derived_outcomes = derive_held_out_outcomes(record, cell)
        declared_outcomes = {field: cell[field] for field in derived_outcomes}
        if declared_outcomes != derived_outcomes:
            die(f"{case['id']} held-out {cell.get('id')} declarations differ from deterministic payload evaluation")
        derived_result = "pass" if (
            derived_outcomes["expected_invariant"] == derived_outcomes["observed_invariant"]
            and derived_outcomes["expected_discriminator"] == derived_outcomes["observed_discriminator"]
        ) else "fail"
        if cell.get("result") != derived_result:
            die(f"{case['id']} held-out {cell.get('id')} result is not derived from outcomes")
        if derived_result != "pass":
            die(f"{case['id']} held-out mutation still fails")
    if record["outer_qualification"] != "pass":
        die(f"{case['id']} outer qualification is not pass")
    for item in record["review_yield"]:
        expected = item.get("expected_yield")
        residual = item.get("residual_risk")
        decision = item.get("decision")
        if decision == "run" and (expected not in {"new-class", "known-class"} or not residual):
            die(f"{case['id']} prices an extra review without a material residual")
        if decision == "stop" and expected not in {"duplicate", "style", "none"}:
            die(f"{case['id']} stops despite material expected yield")


rows = cases.get("cases")
if not isinstance(rows, list) or not rows:
    die("R0020 deterministic cases must be a nonempty list")
ids = [row.get("id") for row in rows]
if len(ids) != len(set(ids)) or any(not value for value in ids):
    die("R0020 deterministic case ids must be unique and nonempty")
required_case_ids = {
    "R32-C01-second-same-family",
    "R32-C02-renamed-rephrased-same-family",
    "R32-C03-unrelated-owners-and-mechanisms",
    "R32-C04-unresolved-missing-mechanism",
    "R32-C05-overbroad-family-rejected",
    "R32-C06-single-fault-cheap-path",
    "R32-C07-tiny-reversible-work-cheap-path",
    "R32-C08-local-repair-retires-shared-residual",
    "R32-C09-filled-record-failing-held-out",
    "R32-C10-record-without-held-out-discriminator",
    "R32-C11-unpriced-repeat-after-pass",
    "R32-C12-priced-review-and-evidence-stop",
    "R32-C13-duplicate-report-does-not-trigger",
    "R32-C14-record-owner-substitution-rejected",
}
if set(ids) != required_case_ids:
    die("R0020 deterministic case population is incomplete or substituted")
if any(case.get("model_call") for case in rows):
    die("deterministic R0020 bank must not invoke a model")

routes = Counter()
record_verdicts = Counter()
for case in rows:
    route = classify(case)
    routes[route] += 1
    if route != case.get("expected_route"):
        die(f"{case['id']} expected {case.get('expected_route')} but derived {route}")
    expected_record_verdict = case.get("expected_record_verdict", "accept")
    if expected_record_verdict not in {"accept", "reject"}:
        die(f"{case['id']} has invalid expected_record_verdict")
    try:
        validate_record(case, route)
    except SystemExit as exc:
        if expected_record_verdict != "reject":
            raise
        expected_error = case.get("expected_record_error")
        if not expected_error or expected_error not in str(exc):
            die(f"{case['id']} rejected for the wrong reason: {exc}")
        record_verdicts["reject"] += 1
    else:
        if expected_record_verdict == "reject":
            die(f"{case['id']} invalid record was accepted")
        record_verdicts["accept"] += 1

required_routes = {"convergence", "unrelated", "unresolved-family", "duplicate", "cheap-path"}
if not required_routes.issubset(routes):
    die(f"case bank lacks routes: {sorted(required_routes - set(routes))}")
if not {"accept", "reject"}.issubset(record_verdicts):
    die("case bank must contain accepted and rejected record controls")

negative_rows = cases.get("state_model_negatives")
required_negative_ids = {
    "R32-N01-missing-valid-states",
    "R32-N02-self-declared-held-out-pass",
    "R32-N03-unknown-dimension",
    "R32-N04-unknown-class",
    "R32-N05-unknown-mutation",
    "R32-N06-dangling-held-out",
    "R32-N07-dangling-excluded-distractor",
    "R32-N08-incoherent-family-distractor",
    "R32-N09-mutated-declarations-unchanged-payload",
    "R32-N10-unverified-included-member-unbound",
}
if not isinstance(negative_rows, list) or {row.get("id") for row in negative_rows} != required_negative_ids:
    die("R0020 adversarial state-model population is incomplete or substituted")
base_case = next(row for row in rows if row["id"] == "R32-C01-second-same-family")
for negative in negative_rows:
    probe = copy.deepcopy(base_case)
    probe["id"] = negative["id"]
    record = probe["record"]
    operation = negative.get("operation")
    if operation == "drop-valid-states":
        record.pop("valid_states", None)
    elif operation == "drop-held-out-payload":
        record["held_out"][0].pop("state", None)
    elif operation == "unknown-dimension":
        record["valid_states"][0]["dimension"] = "unknown-dimension"
    elif operation == "unknown-class":
        record["valid_states"][0]["class"] = "unknown-class"
    elif operation == "unknown-mutation":
        record["held_out"][0]["mutation"] = "unknown-mutation"
    elif operation == "dangling-held-out":
        record["held_out_ids"].append("missing-held-out")
    elif operation == "dangling-excluded":
        record["excluded"].append("missing-distractor")
    elif operation == "family-distractor":
        for field in ("owner", "invariant", "mechanism"):
            record["distractors"][0][field] = record[field]
    elif operation == "flip-held-out-declarations":
        held_out = record["held_out"][0]
        held_out["expected_invariant"] = "fail"
        held_out["observed_invariant"] = "fail"
        held_out["expected_discriminator"] = "not-family"
        held_out["observed_discriminator"] = "not-family"
    elif operation == "add-unverified-unbound-member":
        probe["failures"].append({
            "id": "F-UNBOUND",
            "owner": "src/unrelated.py",
            "invariant": "unrelated-invariant",
            "mechanism": "unrelated-mechanism",
            "state_dimension": "unknown-dimension",
            "state_class": "unknown-class",
            "mutation_relation": "unknown-mutation",
            "independently_verified": False,
        })
        record["included"].append("F-UNBOUND")
        record["red_witnesses"].append("F-UNBOUND")
    else:
        die(f"{negative['id']} has unknown mutation operation")
    try:
        validate_record(probe, "convergence")
    except SystemExit as exc:
        expected_error = negative.get("expected_error")
        if not expected_error or expected_error not in str(exc):
            die(f"{negative['id']} rejected for the wrong reason: {exc}")
    else:
        die(f"{negative['id']} adversarial state model was accepted")

print(
    "r32 deterministic bank: ok "
    f"({len(claims)} findings; {observed['included']} included; "
    f"{observed['excluded']} excluded; {observed['duplicate']} duplicate; "
    f"{observed['ambiguous']} ambiguous; {len(rows)} state cases; "
    f"{len(negative_rows)} adversarial state-model cases)"
)
PY

printf 'convergence-mode-contract: ok (qualified optional reference + R0020 deterministic bank)\n'
