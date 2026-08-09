#!/usr/bin/env bash
set -euo pipefail

# Governed state-space convergence mode (#11), EXPERIMENTAL/optional:
# structural checks only — the reference exists, is NOT inlined into the
# bootloader path, declares trigger/mode/exit/adoption-gate, and the two
# adoption-gate fixtures are well-formed (positive 3-dim + negative
# single-fault control). The model-in-the-loop adoption gate itself is a
# #9 evaluation and is NOT run here.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

ref="skills/implementaudit/references/convergence-mode.md"
skill="skills/implementaudit/SKILL.md"
fx="fixtures/convergence-mode"
r32="$fx/r32"
fail() { printf 'convergence-mode-contract: %s\n' "$*" >&2; exit 1; }

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "Python 3 is required for R32 deterministic fixture validation"
fi

[ -f "$ref" ] || fail "optional reference $ref missing"
flat="$(tr '\n' ' ' < "$ref" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'EXPERIMENTAL' || fail "reference must be marked experimental"
printf '%s' "$flat" | grep -qi 'When it applies (trigger)' || fail "trigger section missing"
printf '%s' "$flat" | grep -qi 'Enumeration artifact' || fail "enumeration artifact step missing"
printf '%s' "$flat" | grep -qi 'exactly one outer qualification' || fail "single-outer-qualification missing"
printf '%s' "$flat" | grep -qi 'Adoption gate' || fail "adoption gate missing"
printf '%s' "$flat" | grep -qi 'single-fault fixture .* must NOT trigger\|must NOT trigger' \
  || fail "negative-control (must-not-trigger) missing"
printf '%s' "$flat" | grep -qi 'escalate-to-convergence-mode' \
  || fail "mechanism-replacement evidence producer missing"
printf '%s' "$flat" | grep -qi 'real-world trigger evidence' \
  || fail "adoption-gate evidence linkage missing"

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

# R32 independent qualification bank. The fixtures are repo-only evidence;
# final activation and shared runtime wording remain integration-owned.
incident_bank="$r32/incident-population.json"
case_bank="$r32/cases.json"
[ -f "$incident_bank" ] || fail "R32 incident population missing: $incident_bank"
[ -f "$case_bank" ] || fail "R32 deterministic case bank missing: $case_bank"

"${py_cmd[@]}" - "$incident_bank" "$case_bank" <<'PY'
import json
import re
import sys
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
expected_campaign_counts = {"#144": 29, "R30": 8, "R31": 11}
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
        "malformed_states", "boundary_states", "adjacent_states", "mutation_operators",
        "red_witnesses", "held_out", "outer_qualification", "review_yield",
    ):
        value = record.get(field)
        if value in (None, "", [], {}):
            die(f"{case['id']} convergence record lacks {field}")
    if any(op not in allowed_mutations for op in record["mutation_operators"]):
        die(f"{case['id']} uses an unbounded mutation operator")
    members = record["included"]
    if any(member not in [row["id"] for row in case["failures"]] for member in members):
        die(f"{case['id']} includes an unknown failure")
    verified = [row for row in case["failures"] if row.get("independently_verified")]
    for field in ("owner", "invariant", "mechanism"):
        if len({row[field] for row in verified}) != 1:
            die(f"{case['id']} overbroad record joins distinct {field} values")
        if record[field] != verified[0][field]:
            die(f"{case['id']} record {field} differs from the failure family")
    if any(cell.get("result") != "pass" for cell in record["held_out"]):
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
    die("R32 deterministic cases must be a nonempty list")
ids = [row.get("id") for row in rows]
if len(ids) != len(set(ids)) or any(not value for value in ids):
    die("R32 deterministic case ids must be unique and nonempty")
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
    die("R32 deterministic case population is incomplete or substituted")
if any(case.get("model_call") for case in rows):
    die("deterministic R32 bank must not invoke a model")

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

print(
    "r32 deterministic bank: ok "
    f"({len(claims)} findings; {observed['included']} included; "
    f"{observed['excluded']} excluded; {observed['duplicate']} duplicate; "
    f"{observed['ambiguous']} ambiguous; {len(rows)} state cases)"
)
PY

printf 'convergence-mode-contract: ok (optional reference + original gate + R32 deterministic bank; final activation deferred)\n'
