#!/usr/bin/env bash
# acceptance-instrument-discipline.test.sh — issues #85 and #164 deterministic controls
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'acceptance-instrument-discipline.test: python is required\n' >&2
  exit 2
fi

fixture="fixtures/acceptance-instrument-discipline/cases.json"
base="fixtures/phase-validation/valid-full-spec.md"
pass=0
fail=0

record_pass() {
  pass=$((pass + 1))
}

record_fail() {
  printf 'acceptance-instrument-discipline.test: %s\n' "$1" >&2
  fail=$((fail + 1))
}

if bash scripts/check-acceptance-instrument-discipline.sh "$fixture"; then
  record_pass
else
  record_fail "deterministic control checker rejected the fixture bank"
fi

# S3E-W01: one bounded state-synthesis population composes the R31/R35
# lineages.  It must stay trigger-selected; ordinary deterministic work remains
# on the existing cheap path.
s3e_contract_out="$tmp/s3e-w01-contract.out"
if "${py_cmd[@]}" - "$fixture" \
    skills/implementaudit/references/phase-design.md \
    >"$s3e_contract_out" <<'PY'
import json
import sys
from pathlib import Path

fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
cases = fixture.get("state_synthesis_cases")
expected = {
    "S3E-W01-automated-action-complete-risk-envelope",
    "S3E-W01-automated-action-incomplete-risk-envelope",
    "S3E-W01-complete-triggered-state",
    "S3E-W01-cheap-authoritative-discriminator",
    "S3E-W01-health-proxy-not-required-function",
    "S3E-W01-correlated-review-not-independent",
    "S3E-W01-incomplete-proof-boundary",
}
if not isinstance(cases, list) or {case.get("id") for case in cases} != expected:
    raise SystemExit("S3E-W01 RED: state-synthesis fixture population missing")
phase = Path(sys.argv[2]).read_text(encoding="utf-8")
if "Rule P4-17 — Triggered state-synthesis acceptance" not in phase:
    raise SystemExit("S3E-W01 RED: phase-design missing triggered state-synthesis acceptance")
if "held-outs without exposing answers/distractors" not in phase:
    raise SystemExit("P4-16 RED: distractors missing from the non-exposure boundary")
if "Easier assertions, goldens, answers," not in phase:
    raise SystemExit("P4-16 RED: answers missing from the prohibited easing set")
PY
then
  record_pass
else
  record_fail "$(cat "$s3e_contract_out")"
fi

s3e_mutant="$tmp/s3e-w01-false-green.json"
"${py_cmd[@]}" - "$fixture" "$s3e_mutant" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["state_synthesis_cases"]
            if row["id"] == "S3E-W01-complete-triggered-state")
case["required_function"] = False
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$s3e_mutant" \
    >"$tmp/s3e-w01-false-green.out" 2>&1; then
  record_fail "S3E-W01 accepted local health without required-function semantics"
elif grep -Fq 'S3E-W01-complete-triggered-state' \
    "$tmp/s3e-w01-false-green.out"; then
  record_pass
else
  record_fail "S3E-W01 negative did not identify its rejected cell"
fi

for action_axis in false_alarm_cost missed_detection_cost detection_latency \
  diagnosis_confidence reversibility action_authority; do
  automated_action_mutant="$tmp/s3e-w01-automated-action-$action_axis.json"
  "${py_cmd[@]}" - "$fixture" "$automated_action_mutant" "$action_axis" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:3])
axis = sys.argv[3]
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["state_synthesis_cases"]
            if row["id"] == "S3E-W01-automated-action-complete-risk-envelope")
case[axis] = False
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
  if bash scripts/check-acceptance-instrument-discipline.sh \
      "$automated_action_mutant" >"$tmp/s3e-w01-automated-action-$action_axis.out" 2>&1; then
    record_fail "S3E-W01 accepted automated action without $action_axis"
  elif grep -Fq 'S3E-W01-automated-action-complete-risk-envelope' \
      "$tmp/s3e-w01-automated-action-$action_axis.out"; then
    record_pass
  else
    record_fail "S3E-W01 $action_axis negative did not identify its rejected cell"
  fi
done

automated_action_schema_mutant="$tmp/s3e-w01-automated-action-schema-removed.json"
"${py_cmd[@]}" - "$fixture" "$automated_action_schema_mutant" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["state_synthesis_cases"]
            if row["id"] == "S3E-W01-automated-action-complete-risk-envelope")
for key in ("automated_action", "false_alarm_cost", "missed_detection_cost",
            "detection_latency", "diagnosis_confidence", "reversibility",
            "action_authority"):
    case.pop(key)
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$automated_action_schema_mutant" \
    >"$tmp/s3e-w01-automated-action-schema-removed.out" 2>&1; then
  record_fail "S3E-W01 required automated-action case accepted after its complete risk schema was removed"
elif grep -Fq 'S3E-W01-automated-action-complete-risk-envelope' \
    "$tmp/s3e-w01-automated-action-schema-removed.out"; then
  record_pass
else
  record_fail "S3E-W01 removed automated-action schema did not identify its rejected cell"
fi

identity_proxy_fixture="$tmp/r35-nonresolving-identity-proxy.json"
"${py_cmd[@]}" - "$fixture" "$identity_proxy_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case_id = "R35-CP5-legitimate-policy-repair"
evidence = fixture["policy_evidence"][case_id]
fixture["policy_evidence_context"]["repository_evidence"][case_id] = {
    "classification": "repository-evidence",
    "identity_relationship": {
        "candidate_parent": "direct-parent",
        "authority_parent": "tree-object-at-owner-locator",
    },
    "population": {
        "source_identity": "5555555555555555555555555555555555555555",
        "total_count": 1,
        "examined_count": 1,
    },
}
identities = [
    evidence["candidate_identity"],
    evidence["parent_identity"],
    evidence["authority"]["source_identity"],
    *evidence["evidence_population"],
]
if len(identities) != len(set(identities)):
    raise SystemExit("identity-proxy witness must use distinct identities")
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
identity_proxy_out="$tmp/r35-nonresolving-identity-proxy.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$identity_proxy_fixture" --repository "$repo_root" \
    >"$identity_proxy_out" 2>&1; then
  record_fail "distinct non-resolving candidate, parent, authority and population identities were accepted"
elif grep -Fq "R35-CP5-legitimate-policy-repair" "$identity_proxy_out"; then
  record_pass
else
  record_fail "R35 identity-proxy negative failed without identifying the rejected cell"
  cat "$identity_proxy_out" >&2
fi

identity_repo="$tmp/r35-identity-repository"
wrong_identity_repo="$tmp/r35-wrong-identity-repository"
git init -q "$identity_repo"
git -C "$identity_repo" config user.name "R35 Test"
git -C "$identity_repo" config user.email "r35@example.invalid"
mkdir -p "$identity_repo/contracts"
printf 'independent evaluator authority\n' >"$identity_repo/contracts/evaluator"
git -C "$identity_repo" add contracts/evaluator
git -C "$identity_repo" commit -q -m authority
authority_identity="$(git -C "$identity_repo" rev-parse HEAD:contracts/evaluator)"
git -C "$identity_repo" commit -q --allow-empty -m parent
parent_identity="$(git -C "$identity_repo" rev-parse HEAD)"
witness_identity="$(printf 'retained witness\n' | git -C "$identity_repo" hash-object -w --stdin)"
adjacent_identity="$(printf 'adjacent witness\n' | git -C "$identity_repo" hash-object -w --stdin)"
population_source_identity="$({
  printf '%s\n' "$witness_identity"
  printf '%s\n' "$adjacent_identity"
} | git -C "$identity_repo" hash-object -w --stdin)"
git -C "$identity_repo" commit -q --allow-empty -m candidate
candidate_identity="$(git -C "$identity_repo" rev-parse HEAD)"
git init -q "$wrong_identity_repo"

if [ "$(git -C "$identity_repo" rev-parse "$candidate_identity^")" = "$parent_identity" ] &&
   [ "$(git -C "$identity_repo" rev-parse \
     "$parent_identity:contracts/evaluator")" = "$authority_identity" ] &&
   [ "$(git -C "$identity_repo" cat-file -p "$population_source_identity")" = \
     "$witness_identity
$adjacent_identity" ]; then
  record_pass
else
  record_fail "independent Git controls did not establish R35 identity and population relationships"
fi

repository_fixture="$tmp/r35-repository-evidence.json"
"${py_cmd[@]}" - "$fixture" "$repository_fixture" \
    "$candidate_identity" "$parent_identity" "$authority_identity" \
    "$witness_identity" "$adjacent_identity" "$population_source_identity" <<'PY'
import json
import sys
from pathlib import Path

(source, target, candidate, parent, authority, witness, adjacent,
 population_source) = sys.argv[1:]
fixture = json.loads(Path(source).read_text(encoding="utf-8"))
case_id = "R35-CP5-legitimate-policy-repair"
evidence = fixture["policy_evidence"][case_id]
evidence["candidate_identity"] = candidate
evidence["parent_identity"] = parent
evidence["authority"]["source_identity"] = authority
evidence["witness"]["identity"] = witness
evidence["evidence_population"] = [witness, adjacent]
fixture["policy_evidence_context"]["repository_evidence"][case_id] = {
    "classification": "repository-evidence",
    "identity_relationship": {
        "candidate_parent": "direct-parent",
        "authority_parent": "tree-object-at-owner-locator",
    },
    "population": {
        "source_identity": population_source,
        "total_count": 2,
        "examined_count": 2,
    },
}
Path(target).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY

repository_fixture_out="$tmp/r35-repository-evidence.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$repository_fixture" --repository "$identity_repo" \
    >"$repository_fixture_out" 2>&1; then
  record_pass
else
  record_fail "valid repository-bound R35 evidence was rejected"
  cat "$repository_fixture_out" >&2
fi

repository_mutants="$tmp/r35-repository-mutants"
mkdir -p "$repository_mutants"
"${py_cmd[@]}" - "$repository_fixture" "$repository_mutants" <<'PY'
import copy
import json
import sys
from pathlib import Path

source, target_dir = Path(sys.argv[1]), Path(sys.argv[2])
fixture = json.loads(source.read_text(encoding="utf-8"))
case_id = "R35-CP5-legitimate-policy-repair"
for name in ("authority-candidate-equal", "authority-parent-substitution",
             "candidate-parent-equal", "missing-population",
             "partial-population"):
    payload = copy.deepcopy(fixture)
    evidence = payload["policy_evidence"][case_id]
    population = payload["policy_evidence_context"]["repository_evidence"][case_id]["population"]
    if name == "authority-candidate-equal":
        evidence["authority"]["source_identity"] = evidence["candidate_identity"]
    elif name == "authority-parent-substitution":
        evidence["authority"]["source_identity"] = evidence["parent_identity"]
    elif name == "candidate-parent-equal":
        evidence["candidate_identity"] = evidence["parent_identity"]
    elif name == "missing-population":
        evidence["evidence_population"] = []
        population["total_count"] = 0
        population["examined_count"] = 0
    elif name == "partial-population":
        evidence["evidence_population"] = evidence["evidence_population"][:1]
        population["examined_count"] = 1
    (target_dir / f"{name}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

for mutant_name in authority-candidate-equal authority-parent-substitution \
    candidate-parent-equal missing-population partial-population; do
  mutant_out="$tmp/r35-repository-$mutant_name.out"
  if bash scripts/check-acceptance-instrument-discipline.sh \
      "$repository_mutants/$mutant_name.json" --repository "$identity_repo" \
      >"$mutant_out" 2>&1; then
    record_fail "R35 repository mutant $mutant_name was accepted"
  elif grep -Fq "R35-CP5-legitimate-policy-repair" "$mutant_out"; then
    record_pass
  else
    record_fail "R35 repository mutant $mutant_name failed without identifying the rejected cell"
    cat "$mutant_out" >&2
  fi
done

wrong_repository_out="$tmp/r35-wrong-repository.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$repository_fixture" --repository "$wrong_identity_repo" \
    >"$wrong_repository_out" 2>&1; then
  record_fail "R35 repository evidence was accepted from the wrong object store"
elif grep -Fq "R35-CP5-legitimate-policy-repair" "$wrong_repository_out"; then
  record_pass
else
  record_fail "R35 wrong-repository negative failed without identifying the rejected cell"
  cat "$wrong_repository_out" >&2
fi

state_matrix_out="$tmp/r35-state-matrix.out"
if "${py_cmd[@]}" - "$fixture" >"$state_matrix_out" <<'PY'
import itertools
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    cases = json.load(stream)["mutation_cases"]

actual = set()
for case in cases:
    events = case["event_order"]
    if not case["same_claim"] or "candidate-fail" not in events:
        continue
    failed_at = events.index("candidate-fail")
    actual.add(tuple(
        event in events and events.index(event) > failed_at
        for event in ("product-change", "contract-change", "evaluator-change")
    ))
expected = set(itertools.product((False, True), repeat=3))
if actual != expected:
    raise SystemExit(f"post-failure state coverage mismatch: {sorted(actual)}")
PY
then
  record_pass
else
  record_fail "R35 bounded product/contract/evaluator state matrix is incomplete"
  cat "$state_matrix_out" >&2
fi

product_state_fixture="$tmp/r35-product-state-mismatch.json"
"${py_cmd[@]}" - "$fixture" "$product_state_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-coupled-change-isolated")
case["event_order"].remove("product-change")
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
product_state_out="$tmp/r35-product-state-mismatch.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$product_state_fixture" >"$product_state_out" 2>&1; then
  record_fail "a product-change claim passed without a post-failure product-change event"
elif grep -Fq "R35-coupled-change-isolated" "$product_state_out"; then
  record_pass
else
  record_fail "R35 product-state mismatch failed without identifying the rejected cell"
  cat "$product_state_out" >&2
fi

gaming_fixture="$tmp/r35-form-green.json"
"${py_cmd[@]}" - "$fixture" "$gaming_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-completed-form-failing-held-out")
case["expected"] = {
    "activation": "TRIGGERED",
    "classification": "EVALUATOR_DEFECT",
    "route": "EVALUATOR_REPAIR",
    "disposition": "PASS",
}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
gaming_out="$tmp/r35-form-green.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$gaming_fixture" >"$gaming_out" 2>&1; then
  record_fail "a completed mutation record purchased PASS despite a failing held-out negative"
elif grep -Fq "R35-completed-form-failing-held-out" "$gaming_out"; then
  record_pass
else
  record_fail "R35 anti-form negative failed without identifying the rejected cell"
  cat "$gaming_out" >&2
fi

matrix_fixture="$tmp/r35-nondiscriminating-matrix.json"
"${py_cmd[@]}" - "$fixture" "$matrix_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-coupled-change-isolated")
case["matrix"] = {
    "old_product_old_evaluator": "PASS",
    "old_product_new_evaluator": "PASS",
    "new_product_old_evaluator": "PASS",
    "new_product_new_evaluator": "PASS",
}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
matrix_out="$tmp/r35-nondiscriminating-matrix.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$matrix_fixture" >"$matrix_out" 2>&1; then
  record_fail "a non-discriminating old/new matrix was accepted as causal isolation"
elif grep -Fq "R35-coupled-change-isolated" "$matrix_out"; then
  record_pass
else
  record_fail "R35 matrix negative failed without identifying the rejected cell"
  cat "$matrix_out" >&2
fi

crossed_cause_fixture="$tmp/r35-crossed-cause.json"
"${py_cmd[@]}" - "$fixture" "$crossed_cause_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-legitimate-evaluator-repair")
case["matrix"] = {"old_product_old_evaluator": "FAIL", "old_product_new_evaluator": "FAIL", "new_product_old_evaluator": "PASS", "new_product_new_evaluator": "PASS"}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$crossed_cause_fixture" >"$tmp/crossed.out" 2>&1; then
  record_fail "a product-effect matrix was accepted as an evaluator repair"
elif grep -Fq "R35-legitimate-evaluator-repair" "$tmp/crossed.out"; then record_pass
else record_fail "R35 crossed-cause negative did not identify its cell"; cat "$tmp/crossed.out" >&2; fi

coupled_cause_fixture="$tmp/r35-coupled-crossed-cause.json"
"${py_cmd[@]}" - "$fixture" "$coupled_cause_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-coupled-change-isolated")
case["matrix"] = {"old_product_old_evaluator": "FAIL", "old_product_new_evaluator": "PASS", "new_product_old_evaluator": "FAIL", "new_product_new_evaluator": "PASS"}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$coupled_cause_fixture" >"$tmp/coupled-crossed.out" 2>&1; then
  record_fail "an evaluator-effect matrix was accepted as an isolated coupled repair"
elif grep -Fq "R35-coupled-change-isolated" "$tmp/coupled-crossed.out"; then record_pass
else record_fail "R35 coupled crossed-cause negative did not identify its cell"; cat "$tmp/coupled-crossed.out" >&2; fi

phantom_contract_fixture="$tmp/r35-phantom-contract-record.json"
"${py_cmd[@]}" - "$fixture" "$phantom_contract_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-legitimate-evaluator-repair")
case["contract_change"] = {"owner": "owner", "effective_boundary": "next", "migration_effect": "retained", "population_effect": "unchanged"}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$phantom_contract_fixture" >"$tmp/phantom.out" 2>&1; then
  record_fail "a contract record without a contract event was accepted"
elif grep -Fq "R35-legitimate-evaluator-repair" "$tmp/phantom.out"; then record_pass
else record_fail "R35 phantom-contract negative did not identify its cell"; cat "$tmp/phantom.out" >&2; fi

missing_contract_fixture="$tmp/r35-missing-contract-record.json"
"${py_cmd[@]}" - "$fixture" "$missing_contract_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-authorised-contract-recalibration")
case["contract_change"] = None
case["expected"] = {"activation": "TRIGGERED", "classification": "EVALUATOR_DEFECT", "route": "EVALUATOR_REPAIR", "disposition": "PASS"}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$missing_contract_fixture" >"$tmp/missing-contract.out" 2>&1; then
  record_fail "a contract event without its structured record was accepted"
elif grep -Fq "R35-authorised-contract-recalibration" "$tmp/missing-contract.out"; then record_pass
else record_fail "R35 missing-contract negative did not identify its cell"; cat "$tmp/missing-contract.out" >&2; fi

parity_fixture="$tmp/r35-live-instrument-without-parity.json"
"${py_cmd[@]}" - "$fixture" "$parity_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-legitimate-prompt-repair")
case["proof"]["parity"] = False
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$parity_fixture" >"$tmp/parity.out" 2>&1; then
  record_fail "a live independent instrument was accepted without parity"
elif grep -Fq "R35-legitimate-prompt-repair" "$tmp/parity.out"; then record_pass
else record_fail "R35 parity negative did not identify its cell"; cat "$tmp/parity.out" >&2; fi

mock_parity_fixture="$tmp/r35-mock-only-green.json"
"${py_cmd[@]}" - "$fixture" "$mock_parity_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-mock-promotion")
case["proof"]["parity"] = True
case["expected"] = {"activation": "TRIGGERED", "classification": "EVALUATOR_DEFECT", "route": "EVALUATOR_REPAIR", "disposition": "PASS"}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$mock_parity_fixture" >"$tmp/mock-parity.out" 2>&1; then
  record_fail "mock-only green passed without an equal structured parity witness"
elif grep -Fq "R35-mock-promotion" "$tmp/mock-parity.out"; then record_pass
else record_fail "R35 mock-parity negative did not identify its cell"; cat "$tmp/mock-parity.out" >&2; fi

parity_witness_fixture="$tmp/r35-missing-parity-witness.json"
"${py_cmd[@]}" - "$fixture" "$parity_witness_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
del fixture["instrument_parity"]["R35-legitimate-prompt-repair"]
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$parity_witness_fixture" >"$tmp/parity-witness.out" 2>&1; then
  record_fail "an independent instrument passed without a structured parity witness"
elif grep -Fq "R35-legitimate-prompt-repair" "$tmp/parity-witness.out"; then record_pass
else record_fail "R35 structured-parity negative did not identify its cell"; cat "$tmp/parity-witness.out" >&2; fi

representation_matrix_fixture="$tmp/r35-representation-nondiscriminating-matrix.json"
"${py_cmd[@]}" - "$fixture" "$representation_matrix_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-representation-preserving-refactor")
case["matrix"] = {
    "old_product_old_evaluator": "PASS",
    "old_product_new_evaluator": "PASS",
    "new_product_old_evaluator": "PASS",
    "new_product_new_evaluator": "PASS",
}
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
representation_matrix_out="$tmp/r35-representation-nondiscriminating-matrix.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$representation_matrix_fixture" >"$representation_matrix_out" 2>&1; then
  record_fail "a non-discriminating matrix was accepted as representation-preserving evidence"
elif grep -Fq "R35-representation-preserving-refactor" "$representation_matrix_out"; then
  record_pass
else
  record_fail "R35 representation matrix negative failed without identifying the rejected cell"
  cat "$representation_matrix_out" >&2
fi

prompt_fixture="$tmp/r35-prompt-answer-leak.json"
"${py_cmd[@]}" - "$fixture" "$prompt_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-legitimate-prompt-repair")
case["prompt_contract"]["after_prompt"] = (
    "The correct owner is R29. State R29 and cite it.")
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
prompt_out="$tmp/r35-prompt-answer-leak.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$prompt_fixture" >"$prompt_out" 2>&1; then
  record_fail "a post-failure prompt that revealed the expected answer was accepted"
elif grep -Fq "R35-legitimate-prompt-repair" "$prompt_out"; then
  record_pass
else
  record_fail "R35 prompt-independence negative failed without identifying the rejected cell"
  cat "$prompt_out" >&2
fi

punctuation_prompt_fixture="$tmp/r35-punctuation-answer-leak.json"
"${py_cmd[@]}" - "$fixture" "$punctuation_prompt_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-legitimate-prompt-repair")
case["prompt_contract"]["after_prompt"] = "The correct owner is R-29; cite it."
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$punctuation_prompt_fixture" >"$tmp/punctuation.out" 2>&1; then
  record_fail "a punctuation-separated expected answer leaked into the prompt"
elif grep -Fq "R35-legitimate-prompt-repair" "$tmp/punctuation.out"; then record_pass
else record_fail "R35 punctuation-leak negative did not identify its cell"; cat "$tmp/punctuation.out" >&2; fi

distinct_identifier_fixture="$tmp/r35-distinct-identifier.json"
"${py_cmd[@]}" - "$fixture" "$distinct_identifier_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"] if row["id"] == "R35-legitimate-prompt-repair")
case["prompt_contract"]["after_prompt"] = "Compare the public projection owner with R290 and cite repository evidence."
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$distinct_identifier_fixture" >"$tmp/distinct-identifier.out" 2>&1; then
  record_pass
else
  record_fail "a distinct identifier such as R290 was treated as leaked R29"
  cat "$tmp/distinct-identifier.out" >&2
fi

before_prompt_fixture="$tmp/r35-before-prompt-answer-leak.json"
"${py_cmd[@]}" - "$fixture" "$before_prompt_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-legitimate-prompt-repair")
case["prompt_contract"]["before_prompt"] = (
    "The correct owner is R29. State R29 and cite it.")
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
before_prompt_out="$tmp/r35-before-prompt-answer-leak.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$before_prompt_fixture" >"$before_prompt_out" 2>&1; then
  record_fail "a pre-repair prompt that revealed the expected answer was accepted as evidence"
elif grep -Fq "R35-legitimate-prompt-repair" "$before_prompt_out"; then
  record_pass
else
  record_fail "R35 before-prompt negative failed without identifying the rejected cell"
  cat "$before_prompt_out" >&2
fi

record_fixture="$tmp/r35-incomplete-record.json"
"${py_cmd[@]}" - "$fixture" "$record_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-legitimate-evaluator-repair")
case["record_complete"] = False
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
record_out="$tmp/r35-incomplete-record.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$record_fixture" >"$record_out" 2>&1; then
  record_fail "an incomplete triggered mutation record was accepted as sufficient evidence"
elif grep -Fq "R35-legitimate-evaluator-repair" "$record_out"; then
  record_pass
else
  record_fail "R35 incomplete-record negative failed without identifying the rejected cell"
  cat "$record_out" >&2
fi

structural_record_fixture="$tmp/r35-structurally-incomplete-record.json"
"${py_cmd[@]}" - "$fixture" "$structural_record_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
del fixture["mutation_records"]["R35-legitimate-evaluator-repair"]["property_owner"]
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
structural_record_out="$tmp/r35-structurally-incomplete-record.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$structural_record_fixture" >"$structural_record_out" 2>&1; then
  record_fail "a mutation record missing its property owner was accepted"
elif grep -Fq "R35-legitimate-evaluator-repair" "$structural_record_out"; then
  record_pass
else
  record_fail "R35 structural-record negative failed without identifying the rejected cell"
  cat "$structural_record_out" >&2
fi

policy_mutants="$tmp/r35-policy-mutants"
mkdir -p "$policy_mutants"
"${py_cmd[@]}" - "$fixture" "$policy_mutants" <<'PY'
import copy
import json
import sys
from pathlib import Path

source, target_dir = Path(sys.argv[1]), Path(sys.argv[2])
fixture = json.loads(source.read_text(encoding="utf-8"))
mutations = {
    "path-only-trigger": ("R35-CP7-support-file-path-only", {"expected": {"activation": "CANDIDATE_CONTROLLED_VALIDATION_POLICY", "classification": "CANDIDATE_CONTROLLED_POLICY_WEAKENING", "route": "REJECT_SELF_AUTHENTICATED_GREEN", "disposition": "FAIL"}}),
    "strengthening-replaces-baseline": ("R35-CP4-policy-strengthening", {"baseline_equivalent": False}),
    "repair-drops-adjacent": ("R35-CP5-legitimate-policy-repair", {"held_out_passed": ["positive", "negative", "boundary"]}),
    "new-policy-self-authorised": ("R35-CP6-new-policy-no-baseline", {"external_owner_authority": False}),
    "migration-loses-property": ("R35-CP8-authoritative-migration", {"property_equivalent_or_stronger": False}),
    "self-attested-authority": ("R35-CP5-legitimate-policy-repair", {"external_owner_authority": True, "authoritative_contract": True}),
    "missing-authority-identity": ("R35-CP5-legitimate-policy-repair", {}),
    "missing-effective-boundary": ("R35-CP5-legitimate-policy-repair", {}),
    "missing-owner-delta": ("R35-CP5-legitimate-policy-repair", {}),
    "missing-witness": ("R35-CP5-legitimate-policy-repair", {"original_witness_retained": True}),
    "fake-equivalence": ("R35-CP2-candidate-skip-guidance", {"property_equivalent_or_stronger": True, "expected": {"activation": "CANDIDATE_CONTROLLED_VALIDATION_POLICY", "classification": "AUTHORISED_POLICY_CHANGE", "route": "INDEPENDENT_PROPERTY_ADJUDICATION", "disposition": "PASS"}}),
}
for name, (case_id, updates) in mutations.items():
    payload = copy.deepcopy(fixture)
    case = next(row for row in payload["policy_cases"] if row["id"] == case_id)
    case.update(updates)
    evidence = payload["policy_evidence"][case_id]
    if name == "strengthening-replaces-baseline":
        evidence["behaviour"]["baseline"] = None
    elif name == "repair-drops-adjacent":
        evidence["behaviour"]["candidate"]["adjacent"] = "PASS"
    elif name == "new-policy-self-authorised":
        evidence["authority"]["source_identity"] = evidence["candidate_identity"]
    elif name == "migration-loses-property":
        evidence["behaviour"]["candidate"]["boundary"] = "PASS"
    elif name == "self-attested-authority":
        evidence["authority"] = None
    elif name == "missing-authority-identity":
        evidence["authority"]["source_identity"] = ""
    elif name == "missing-effective-boundary":
        evidence["authority"]["effective_boundary"] = ""
    elif name == "missing-owner-delta":
        evidence["owner_delta"]["changed_owners"] = []
    elif name == "missing-witness":
        evidence["witness"] = None
    (target_dir / f"{name}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

while IFS='|' read -r mutant_name case_id; do
  mutant_name="${mutant_name%$'\r'}"
  case_id="${case_id%$'\r'}"
  mutant_out="$tmp/r35-policy-$mutant_name.out"
  if bash scripts/check-acceptance-instrument-discipline.sh \
      "$policy_mutants/$mutant_name.json" >"$mutant_out" 2>&1; then
    record_fail "R35 policy mutant $mutant_name was accepted"
  elif grep -Fq "$case_id" "$mutant_out"; then
    record_pass
  else
    record_fail "R35 policy mutant $mutant_name failed without identifying $case_id"
    cat "$mutant_out" >&2
  fi
done < <("${py_cmd[@]}" - "$fixture" <<'PY'
print("path-only-trigger|R35-CP7-support-file-path-only")
print("strengthening-replaces-baseline|R35-CP4-policy-strengthening")
print("repair-drops-adjacent|R35-CP5-legitimate-policy-repair")
print("new-policy-self-authorised|R35-CP6-new-policy-no-baseline")
print("migration-loses-property|R35-CP8-authoritative-migration")
print("self-attested-authority|R35-CP5-legitimate-policy-repair")
print("missing-authority-identity|R35-CP5-legitimate-policy-repair")
print("missing-effective-boundary|R35-CP5-legitimate-policy-repair")
print("missing-owner-delta|R35-CP5-legitimate-policy-repair")
print("missing-witness|R35-CP5-legitimate-policy-repair")
print("fake-equivalence|R35-CP2-candidate-skip-guidance")
PY
)

cp8_unchanged_fixture="$tmp/r35-cp8-unchanged-bypass.json"
"${py_cmd[@]}" - "$fixture" "$cp8_unchanged_fixture" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["policy_cases"] if row["id"] == "R35-CP8-undiscoverable-owner")
case["policy_delta"] = "unchanged"
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
if bash scripts/check-acceptance-instrument-discipline.sh "$cp8_unchanged_fixture" >"$tmp/cp8-unchanged.out" 2>&1; then
  record_pass
else
  record_fail "CP8 undiscoverable owner bypassed Surface B through an unchanged label"
  cat "$tmp/cp8-unchanged.out" >&2
fi

answer_authority_fixture="$tmp/r35-answer-correction-without-authority.json"
"${py_cmd[@]}" - "$fixture" "$answer_authority_fixture" <<'PY'
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
fixture = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in fixture["mutation_cases"]
            if row["id"] == "R35-legitimate-expected-answer-correction")
case["authoritative_instrument"] = ""
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
PY
answer_authority_out="$tmp/r35-answer-correction-without-authority.out"
if bash scripts/check-acceptance-instrument-discipline.sh \
    "$answer_authority_fixture" >"$answer_authority_out" 2>&1; then
  record_fail "an expected-answer mutation passed without independent authority"
elif grep -Fq "R35-legitimate-expected-answer-correction" "$answer_authority_out"; then
  record_pass
else
  record_fail "R35 expected-answer authority negative failed without identifying the rejected cell"
  cat "$answer_authority_out" >&2
fi

review_fixture="fixtures/acceptance-instrument-discipline/F7-vacuous-invariant.md"
if grep -Fq 'Disposition: REVIEW_FLAG' "$review_fixture" &&
   grep -Fq 'Mechanical gate: forbidden' "$review_fixture"; then
  record_pass
else
  record_fail "F7 must remain a cold-review fixture without a mechanical gate"
fi

case_ids="$({ "${py_cmd[@]}" - "$fixture" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    fixture = json.load(stream)
for case in fixture["phase_cases"]:
    print(case["id"])
PY
} 2>/dev/null)" || {
  record_fail "could not enumerate phase cases"
  case_ids=""
}

while IFS= read -r case_id; do
  case_id="${case_id//$'\r'/}"
  [ -n "$case_id" ] || continue
  spec="$tmp/$case_id.md"
  meta="$tmp/$case_id.meta"
  "${py_cmd[@]}" - "$fixture" "$base" "$case_id" "$spec" "$meta" <<'PY'
import json
import sys
from pathlib import Path

fixture_path, base_path, case_id, output_path, meta_path = sys.argv[1:]
fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
case = next(row for row in fixture["phase_cases"] if row["id"] == case_id)
lines = Path(base_path).read_text(encoding="utf-8").splitlines()
start = next(i for i, line in enumerate(lines)
             if line.startswith("## Mandatory commands"))
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith("## "))
prefix = lines[start:start + 1]
body = [""] + case["commands"] + [""]
Path(output_path).write_text(
    "\n".join(lines[:start] + prefix + body + lines[end:]) + "\n",
    encoding="utf-8", newline="\n")
Path(meta_path).write_text(
    case["expected"] + "\n" + case.get("diagnostic", "") + "\n",
    encoding="utf-8", newline="\n")
PY
  expected="$(sed -n '1p' "$meta")"
  diagnostic="$(sed -n '2p' "$meta")"
  out="$tmp/$case_id.out"
  bash skills/implementaudit/scripts/validate-phase.sh "$spec" >"$out" 2>&1
  status=$?
  case "$expected" in
    PASS)
      if [ "$status" -eq 0 ]; then
        record_pass
      else
        record_fail "$case_id should pass validate-phase.sh"
        cat "$out" >&2
      fi
      ;;
    FAIL)
      if [ "$status" -ne 0 ] && grep -Fq "$diagnostic" "$out"; then
        record_pass
      else
        record_fail "$case_id should fail with diagnostic: $diagnostic"
        cat "$out" >&2
      fi
      ;;
    WARN)
      if [ "$status" -eq 0 ] && grep -Fq "$diagnostic" "$out"; then
        record_pass
      else
        record_fail "$case_id should pass with warning: $diagnostic"
        cat "$out" >&2
      fi
      ;;
    *)
      record_fail "$case_id carries unsupported expected result: $expected"
      ;;
  esac
done <<< "$case_ids"

total=$((pass + fail))
if [ "$fail" -ne 0 ]; then
  printf 'acceptance-instrument-discipline.test: FAIL — %d/%d checks failed\n' \
    "$fail" "$total" >&2
  exit 1
fi

printf 'acceptance-instrument-discipline.test: ok (%d/%d)\n' "$pass" "$total"
