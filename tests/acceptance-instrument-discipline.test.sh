#!/usr/bin/env bash
# acceptance-instrument-discipline.test.sh — issue #85 deterministic controls
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

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

review_fixture="fixtures/acceptance-instrument-discipline/F7-vacuous-invariant.md"
if grep -Fq 'Disposition: REVIEW_FLAG' "$review_fixture" &&
   grep -Fq 'Mechanical gate: forbidden' "$review_fixture"; then
  record_pass
else
  record_fail "F7 must remain a cold-review fixture without a mechanical gate"
fi

case_ids="$({ python - "$fixture" <<'PY'
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
  python - "$fixture" "$base" "$case_id" "$spec" "$meta" <<'PY'
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
