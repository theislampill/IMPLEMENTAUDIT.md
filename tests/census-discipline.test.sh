#!/usr/bin/env bash
# census-discipline.test.sh - issue #79 deterministic controls
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fixture="fixtures/census-discipline/cases.json"
base="fixtures/phase-validation/valid-full-spec.md"
eval_fixture="eval/fixtures/E5d-census-discipline"
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
