#!/usr/bin/env bash
# census-discipline.test.sh - issue #79 deterministic controls
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fixture="fixtures/census-discipline/cases.json"
public_projection_fixture="fixtures/public-projection/cases.json"
semantic_fixture="fixtures/public-projection/semantic-preservation.json"
base="fixtures/phase-validation/valid-full-spec.md"
eval_fixture="eval/fixtures/E5d-census-discipline"
r29_eval_fixture="eval/fixtures/R29-public-projection"
r29_dogfood_input="fixtures/public-projection/installed-dogfood-input.json"
checker="scripts/check-census-discipline.sh"
pass=0
fail=0

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'census-discipline.test: Python is required\n' >&2
  exit 2
fi

record_pass() {
  pass=$((pass + 1))
}

record_fail() {
  printf 'census-discipline.test: %s\n' "$1" >&2
  fail=$((fail + 1))
}

if [ -f "$checker" ] && bash "$checker" "$fixture"; then
  record_pass
else
  record_fail "deterministic checker is missing or rejected R6-F1..R6-F11"
fi

if [ -f "$public_projection_fixture" ] &&
   bash "$checker" "$public_projection_fixture"; then
  record_pass
else
  record_fail "reused census checker rejected R29-F1..R29-F18"
fi

# Package-pressure compaction once weakened the omission assertion to generic
# overclaim/omission wording. R33/R35 review rejected that evaluator mutation;
# keep the material owner-sourced omission predicate exact here.
if grep -Fq "### Public capability projection" \
     skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '| Topic | Owner/source | README disposition | Docs disposition | Current-state transition | Evidence |' \
     skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`prepublication-current`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`postpublication-current`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`stale`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq 'material owner-sourced capabilities omitted' \
     skills/implementaudit/SKILL.md &&
   grep -Fq 'Public projection challenge: overclaim / omission / not applicable with owner evidence' \
     fixtures/child-agents/read-only-contract-auditor.md &&
   grep -Fq '## Public Capability Projection (when activated)' \
     skills/implementaudit/templates/final-report.md; then
  record_pass
else
  record_fail "public-projection runtime, reviewer, or report owner is incomplete"
fi

if "${py_cmd[@]}" - "$semantic_fixture" <<'PY'
import json
import sys
from pathlib import Path

bank = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if set(bank) != {"schema", "bindings"} or bank["schema"] != \
        "implementaudit-public-projection-semantic-preservation-v1":
    raise SystemExit("semantic-preservation schema invalid")
bindings = bank["bindings"]
if not bindings or len({row["id"] for row in bindings}) != len(bindings):
    raise SystemExit("semantic-preservation bindings invalid")

def contains_all(path, tokens, override=None):
    text = override if override is not None else Path(path).read_text(encoding="utf-8")
    return all(token in text for token in tokens)

for row in bindings:
    if not contains_all(row["projection_owner"], row["projection_tokens"]):
        raise SystemExit(f"{row['id']}: projection owner lost a predicate")
    for owner in row["canonical_owners"]:
        if not contains_all(owner["path"], owner["tokens"]):
            raise SystemExit(f"{row['id']}: canonical owner lost a predicate")
        original = Path(owner["path"]).read_text(encoding="utf-8")
        held_out = original.replace(owner["tokens"][0], "")
        if contains_all(owner["path"], owner["tokens"], held_out):
            raise SystemExit(f"{row['id']}: held-out owner mutation false-passed")
    consumer = row["consumer"]
    if not contains_all(consumer["path"], consumer["tokens"]):
        raise SystemExit(f"{row['id']}: reachable consumer binding missing")
PY
then
  record_pass
else
  record_fail "package semantic-preservation owner/consumer binding failed"
fi

case_ids="$("${py_cmd[@]}" - "$fixture" <<'PY'
import json
import sys
from pathlib import Path

fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for case in fixture["phase_cases"]:
    print(case["id"])
PY
)" || {
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
             if line.startswith("## Evidence required"))
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith("## "))
body = [lines[start], ""] + case["evidence"] + [""]
Path(output_path).write_text(
    "\n".join(lines[:start] + body + lines[end:]) + "\n",
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
  if [ "$expected" = "PASS" ] && [ "$status" -eq 0 ]; then
    record_pass
  elif [ "$expected" = "FAIL" ] && [ "$status" -ne 0 ] &&
       grep -Fq "$diagnostic" "$out"; then
    record_pass
  else
    record_fail "$case_id expected $expected with diagnostic '$diagnostic'"
    cat "$out" >&2
  fi
done <<< "$case_ids"

if "${py_cmd[@]}" - "$eval_fixture" <<'PY'
import json
import sys
from pathlib import Path

fixture_dir = Path(sys.argv[1])
sys.path.insert(0, str(Path("eval/lib").resolve()))
import scoring

fixture = json.loads((fixture_dir / "fixture.json").read_text(encoding="utf-8"))
mission = fixture["mission"].casefold()
for phrase in ("population", "denominator", "census", "true count"):
    if phrase in mission:
        raise SystemExit(f"mission leaks forbidden phrase: {phrase}")
contract_phrases = {
    phrase.casefold()
    for field in fixture["matrix_instruction_contract"]["fields"]
    for phrase in field["forbidden_mission_phrases"]
}
if not {"population", "denominator", "census", "true count"} <= contract_phrases:
    raise SystemExit("P4-13 forbidden phrase set is incomplete")

def patterns(rule):
    if rule["kind"] in {"all_of", "any_of"}:
        for child in rule["rules"]:
            yield from patterns(child)
    elif "pattern" in rule:
        yield rule["pattern"]

for prop in fixture["properties"]:
    for pattern in patterns(prop["rule"]):
        if "|" in pattern:
            raise SystemExit("scoring uses a synonym/alternative list")

controls = json.loads((fixture_dir / "controls.json").read_text(encoding="utf-8"))
if [row["id"] for row in controls] != [
        "paraphrase-must-pass", "polarity-inversion-must-fail"]:
    raise SystemExit("paired controls are incomplete")
for row in controls:
    actual = scoring.overall(scoring.score(fixture, row["transcript"], {}), fixture)
    if actual is not row["expected_pass"]:
        raise SystemExit(f"{row['id']} scored {actual}")
PY
then
  record_pass
else
  record_fail "supplementary E5 metamorphic fixture contract failed"
fi

if "${py_cmd[@]}" - "$r29_eval_fixture" "$r29_dogfood_input" <<'PY'
import copy
import json
import sys
from pathlib import Path

fixture_dir, dogfood_path = map(Path, sys.argv[1:])
sys.path.insert(0, str(Path("eval/lib").resolve()))
import scoring

fixture = json.loads((fixture_dir / "fixture.json").read_text(encoding="utf-8"))
controls = json.loads((fixture_dir / "controls.json").read_text(encoding="utf-8"))
dogfood = json.loads(dogfood_path.read_text(encoding="utf-8"))
required_tuples = [
    ("ITEMS", "owner_topic_derivation", True, "contains",
     "^ITEMS=recovery-replay,offline-archive-install$",
     "recovery-replay,offline-archive-install",
     frozenset({"audit-sequencing", "none"}),
     frozenset({"projection", "population", "denominator",
                "recovery replay", "offline archive install"})),
    ("HISTORY", "historical_preservation", True, "contains",
     "^HISTORY=PRESERVE$", "PRESERVE", frozenset({"REWRITE", "DELETE"}),
     frozenset({"preserve the historical statement", "historical-intentional"})),
    ("GAPS", "omission_detection", True, "contains",
     "^GAPS=recovery-replay,offline-archive-install$",
     "recovery-replay,offline-archive-install",
     frozenset({"none", "cache-compaction"}),
     frozenset({"missing capability", "missing installation route",
                "recovery replay", "offline archive install"})),
    ("EDIT", "owner_source_correction", True, "contains",
     "^EDIT=OWNER_SOURCE$", "OWNER_SOURCE",
     frozenset({"GENERATED_OUTPUT", "NONE"}),
     frozenset({"owner source", "generated output"})),
    ("STATE", "postpublication_refusal", True, "contains",
     "^STATE=REFUSE$", "REFUSE", frozenset({"CLOSE"}),
     frozenset({"postpublication readback", "refuse closure"})),
    ("DETAIL", "concise_delegation", True, "contains",
     "^DETAIL=LEGAL$", "LEGAL", frozenset({"DUPLICATE"}),
     frozenset({"concise delegation", "discoverably delegated"})),
]
property_ids = {row[1] for row in required_tuples}


def validate_model_contract(candidate):
    if candidate.get("id") != "R29-public-projection":
        raise SystemExit("R29 model-cell identity invalid")
    mission = candidate.get("mission", "").casefold()
    fields = candidate.get("matrix_instruction_contract", {}).get("fields", [])
    properties = candidate.get("properties", [])
    if [row.get("field") for row in fields] != [row[0] for row in required_tuples]:
        raise SystemExit("R29 model-cell field identity set invalid")
    if [row.get("name") for row in properties] != [row[1] for row in required_tuples]:
        raise SystemExit("R29 model-cell scorer property set invalid")
    for field, prop, required in zip(fields, properties, required_tuples):
        label = required[0]
        distractors, forbidden = required[6:]
        actual = (
            field.get("field"), field.get("property"), prop.get("required"),
            prop.get("rule", {}).get("kind"), prop.get("rule", {}).get("pattern"),
            field.get("expected"), frozenset(field.get("distractors", [])),
            frozenset(field.get("forbidden_mission_phrases", [])))
        if (actual != required or prop.get("required") is not True or
                set(prop.get("rule", {})) != {"kind", "pattern"} or
                len(field.get("distractors", [])) != len(distractors) or
                len(field.get("forbidden_mission_phrases", [])) != len(forbidden)):
            raise SystemExit(f"{label}: exact acceptance tuple invalid")
        for phrase in forbidden:
            if phrase.casefold() in mission:
                raise SystemExit(f"R29 model-cell mission leaks forbidden phrase: {phrase}")
    for prop in properties:
        rule = prop.get("rule", {})
        patterns = [rule.get("pattern", "")]
        patterns += [child.get("pattern", "") for child in rule.get("rules", [])]
        if any("|" in pattern for pattern in patterns):
            raise SystemExit("R29 model-cell scorer uses a synonym list")


validate_model_contract(fixture)


def require_rejection(candidate, mutation):
    try:
        validate_model_contract(candidate)
    except SystemExit:
        return
    raise SystemExit(f"R29 model-cell accepted {mutation}")


for index, required in enumerate(required_tuples):
    label = required[0]
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["field"] += "_RENAMED"
    require_rejection(mutated, f"renamed field {label}")
    mutated = copy.deepcopy(fixture)
    del mutated["properties"][index]
    require_rejection(mutated, f"removal of {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["required"] = False
    require_rejection(mutated, f"optional {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["required"] = 1
    require_rejection(mutated, f"integer-true {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["rule"] = {"kind": "contains", "pattern": ".*"}
    require_rejection(mutated, f"permissive {label} rule")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["expected"] += "-renamed"
    require_rejection(mutated, f"replaced {label} expected value")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["distractors"].pop()
    require_rejection(mutated, f"removed {label} distractor")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["distractors"][0] += "-renamed"
    require_rejection(mutated, f"replaced {label} distractor")
    for phrase in required[7]:
        mutated = copy.deepcopy(fixture)
        forbidden = mutated["matrix_instruction_contract"]["fields"][index][
            "forbidden_mission_phrases"]
        forbidden.remove(phrase)
        require_rejection(mutated, f"removal of {label} phrase {phrase}")
        forbidden.append(f"{phrase} renamed")
        require_rejection(mutated, f"replacement of {label} phrase {phrase}")

properties = fixture["properties"]

base_seed = {
    "runtime/public-method.md": "Supported user-facing behaviours: audit sequencing; recovery replay.",
    "install/routes.json": "{\"supported\":[\"package manager\",\"offline archive install\"]}",
    "release/state.json": "{\"phase\":\"prepublication\",\"required_next\":\"published-route readback\"}",
    "README.md": "The tool sequences an audit. Details: docs/public-guide.md.",
    "docs/public-guide.md": "The public guide explains audit sequencing. Historical: release-1 retains alias old-runner for host 6.2.",
    "docs/generated.txt": "The public guide explains audit sequencing. Historical: release-1 retains alias old-runner for host 6.2.",
    "docs/generated-owner.json": "{\"source\":\"docs/public-guide.md\",\"output\":\"docs/generated.txt\"}",
    "internal/cache.md": "Internal-only cache compaction is not user-facing.",
}
if fixture.get("seed_repository") != base_seed:
    raise SystemExit("R29 model-cell base seed binding invalid")

control_contracts = {
    "positive-paraphrase": {
        "repository_identity": "R29-positive-paraphrase-seed",
        "polarity": "positive", "expected_pass": True,
        "semantic_role": "owner-derived-omission-pass",
        "seed_repository": {
            "engine/contract.md": "Supported user-facing behaviours: guided rollback; session rebuild.",
            "delivery/routes.json": "{\"supported\":[\"registry\",\"portable zip route\"]}",
            "README.md": "The engine supports guided rollback. Details: guide/start.md.",
            "guide/start.md": "Guided rollback is documented.",
            "guide/rendered.txt": "Guided rollback is documented.",
        },
        "transcript": "ITEMS=session-rebuild,portable-zip-route\nHISTORY=PRESERVE\nGAPS=session-rebuild,portable-zip-route\nEDIT=OWNER_SOURCE\nSTATE=REFUSE\nDETAIL=LEGAL\n",
        "patterns": [
            "^ITEMS=session-rebuild,portable-zip-route$", "^HISTORY=PRESERVE$",
            "^GAPS=session-rebuild,portable-zip-route$", "^EDIT=OWNER_SOURCE$",
            "^STATE=REFUSE$", "^DETAIL=LEGAL$"],
    },
    "negative-internal-only": {
        "repository_identity": "R29-negative-internal-only-seed",
        "polarity": "negative", "expected_pass": True,
        "semantic_role": "internal-only-cheap-path-pass",
        "seed_repository": {
            "internal/cache.md": "Internal-only cache compaction is not user-facing.",
            "release/state.json": "{\"phase\":\"postpublication-current\",\"readback\":true}",
            "README.md": "The supported public behaviours are complete. Details: docs/public.md.",
            "docs/public.md": "The supported public behaviours are complete.",
            "docs/generated.txt": "The supported public behaviours are complete.",
        },
        "transcript": "ITEMS=none\nHISTORY=PRESERVE\nGAPS=none\nEDIT=NONE\nSTATE=CLOSE\nDETAIL=LEGAL\n",
        "patterns": ["^ITEMS=none$", "^HISTORY=PRESERVE$", "^GAPS=none$",
                     "^EDIT=NONE$", "^STATE=CLOSE$", "^DETAIL=LEGAL$"],
    },
    "polarity-denial": {
        "repository_identity": "R29-public-projection-seed",
        "polarity": "polarity-denial", "expected_pass": False,
        "semantic_role": "unstructured-denial-fail",
        "seed_repository": {"fixture_reference": "seed_repository"},
        "transcript": "I did not verify public topic coverage. The phrases recovery-replay and offline-archive-install appear in this denial, but no structured evidence rows were produced.",
        "patterns": [row[4] for row in required_tuples],
    },
}


def validate_control(row):
    control_id = row.get("id")
    if control_id not in control_contracts:
        raise SystemExit("R29 model-cell control identity invalid")
    contract = control_contracts[control_id]
    if set(row) != {
            "id", "repository_identity", "polarity", "expected_pass",
            "semantic_role", "seed_repository", "transcript", "properties"}:
        raise SystemExit(f"{control_id}: control keys invalid")
    for field in ("repository_identity", "polarity", "expected_pass", "semantic_role",
                  "seed_repository", "transcript"):
        if row[field] != contract[field]:
            raise SystemExit(f"{control_id}: {field} binding invalid")
    property_rows = (
        properties if row["properties"] == {"fixture_reference": "properties"}
        else row["properties"])
    actual = [
        (prop.get("name"), prop.get("required"), prop.get("rule"))
        for prop in property_rows]
    expected = [
        (required[1], True, {"kind": "contains", "pattern": pattern})
        for required, pattern in zip(required_tuples, contract["patterns"])]
    if (actual != expected or
            any(prop.get("required") is not True for prop in property_rows)):
        raise SystemExit(f"{control_id}: property tuple binding invalid")


def require_control_rejection(candidate, mutation):
    try:
        validate_control(candidate)
    except SystemExit:
        return
    raise SystemExit(f"R29 model-cell accepted {mutation}")


if set(controls) != {"schema", "cases"} or controls.get("schema") != "implementaudit-r29-model-controls-v2":
    raise SystemExit("R29 model-cell controls schema invalid")
cases = controls.get("cases", [])
if [row.get("id") for row in cases] != [
        "positive-paraphrase", "negative-internal-only", "polarity-denial"]:
    raise SystemExit("R29 model-cell controls must be positive/negative/polarity paired")
for row in cases:
    validate_control(row)
    local_fixture = dict(fixture)
    local_fixture["properties"] = (
        properties if row["properties"] == {"fixture_reference": "properties"}
        else row["properties"])
    actual = scoring.overall(
        scoring.score(local_fixture, row["transcript"], {}),
        local_fixture)
    if actual is not row["expected_pass"]:
        raise SystemExit(f"{row['id']}: synthetic control scored {actual}")

for index, row in enumerate(cases):
    control_id = row["id"]
    next_row = cases[(index + 1) % len(cases)]
    for property_index, required in enumerate(required_tuples):
        mutated = copy.deepcopy(row)
        if mutated["properties"] == {"fixture_reference": "properties"}:
            mutated["properties"] = copy.deepcopy(properties)
        mutated["properties"][property_index]["required"] = 1
        require_control_rejection(
            mutated, f"{control_id} integer-true {required[0]} scoring property")
    for field in ("repository_identity", "polarity", "semantic_role"):
        mutated = copy.deepcopy(row)
        mutated[field] += "-renamed"
        require_control_rejection(mutated, f"{control_id} replacement of {field}")
    mutated = copy.deepcopy(row)
    mutated["expected_pass"] = not mutated["expected_pass"]
    require_control_rejection(mutated, f"{control_id} expected-verdict inversion")
    mutated = copy.deepcopy(row)
    mutated["seed_repository"] = next_row["seed_repository"]
    require_control_rejection(mutated, f"{control_id} seed substitution")
    mutated = copy.deepcopy(row)
    del mutated["seed_repository"]
    require_control_rejection(mutated, f"{control_id} seed removal")
    mutated = copy.deepcopy(row)
    mutated["transcript"] = next_row["transcript"]
    require_control_rejection(mutated, f"{control_id} transcript substitution")

if dogfood.get("schema") != "implementaudit-r29-installed-dogfood-input-v1":
    raise SystemExit("R29 installed-dogfood input schema invalid")
if dogfood.get("execution_state") != "NOT_RUN":
    raise SystemExit("R29 installed dogfood must remain unexecuted in this repair")
if dogfood.get("model_fixture") != "eval/fixtures/R29-public-projection/fixture.json":
    raise SystemExit("R29 dogfood input does not bind the distinct model fixture")
if set(dogfood.get("expected_properties", [])) != property_ids:
    raise SystemExit("R29 dogfood input lost a live scored property")
boundary = dogfood.get("execution_boundary", {})
if boundary != {
        "disposable_codex_home_required": True,
        "exact_package_digest_required_at_execution": True,
        "model_execution_authorised": False,
        "installed_dogfood_authorised": False,
        "publication_authorised": False,
}:
    raise SystemExit("R29 dogfood execution boundary invalid")
PY
then
  record_pass
else
  record_fail "R29 prompt-independent model/install-dogfood input contract failed"
fi

selftest_out="$tmp/eval-selftest.out"
if "${py_cmd[@]}" eval/selftest.py >"$selftest_out" 2>&1 &&
   grep -Fq "no model calls" "$selftest_out"; then
  record_pass
else
  record_fail "eval selftest did not finish with the no-model-call marker"
  cat "$selftest_out" >&2
fi

total=$((pass + fail))
if [ "$fail" -ne 0 ]; then
  printf 'census-discipline.test: FAIL - %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'census-discipline.test: ok (%d/%d)\n' "$pass" "$total"
