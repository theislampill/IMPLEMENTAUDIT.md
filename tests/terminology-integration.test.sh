#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v py >/dev/null 2>&1; then
  PY="py -3"
else
  echo "terminology-integration.test: SKIP (no python)" >&2
  exit 0
fi

pass=0
fail=0
errors=()

ok() { pass=$((pass + 1)); }
fail_case() { fail=$((fail + 1)); errors+=("$1"); }

expect_checker_failure() {
  local repo="$1" expected="$2" label="$3" out rc
  set +e
  out="$(bash "$repo/scripts/check-terminology-integration.sh" --repo-root "$repo" 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -Fq "$expected"; then
    ok
  else
    fail_case "FAIL: $label (expected diagnostic: $expected; rc=$rc; output=$out)"
  fi
}

make_temp() {
  local t
  t="$(mktemp -d)"
  cp -r . "$t/repo" 2>/dev/null || true
  echo "$t/repo"
}

append_text() {
  local file="$1" text="$2"
  "$PY" - "$file" "$text" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
path.write_text(path.read_text(encoding="utf-8") + "\n" + sys.argv[2] + "\n", encoding="utf-8")
PY
}

replace_text() {
  local file="$1" old="$2" new="$3"
  "$PY" - "$file" "$old" "$new" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
path.write_text(path.read_text(encoding="utf-8").replace(sys.argv[2], sys.argv[3]), encoding="utf-8")
PY
}

if bash scripts/check-terminology-integration.sh >/dev/null 2>&1; then
  ok
else
  fail_case "FAIL: check-terminology-integration.sh should pass on current repo"
fi

T=$(make_temp)
printf '# Runtime Terminology\n\n## Term Entries\n\n- Term: A3\n' > "$T/skills/references/runtime-terminology.md"
expect_checker_failure "$T" "TERMINOLOGY_GLOSSARY_FILE:" "should fail when runtime-terminology.md returns"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/templates/THINKING.md" "VOC CTQ SIPOC FMEA STRIDE SOLID GRASP Control Plan."
expect_checker_failure "$T" "TERMINOLOGY_GLOSSARY_ONLY:" "should fail on glossary-only term list"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/docs/portal/pages/terminology.html" "VOC CTQ SIPOC FMEA STRIDE SOLID GRASP Control Plan."
expect_checker_failure "$T" "TERMINOLOGY_GLOSSARY_ONLY:" "should fail on portal glossary-only term drift"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/fixtures/terminology-integration/full-stack-integration.md" "Apply SOLID everywhere, run FMEA, and use STRIDE."
expect_checker_failure "$T" "TERMINOLOGY_GENERIC_ADVICE:" "should fail on generic SOLID/FMEA/STRIDE advice"
rm -rf "$(dirname "$T")"

T=$(make_temp)
replace_text "$T/fixtures/terminology-integration/full-stack-integration.md" "Native parent:" "Native owner removed:"
expect_checker_failure "$T" "TERMINOLOGY_MISSING_NATIVE_PARENT:" "should fail when positive fixture loses Native parent"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/references/terminology-integration.md" "## Term Entries"
expect_checker_failure "$T" "TERMINOLOGY_TERM_ENTRY_DRIFT:" "should fail if thin contract becomes a term-entry glossary"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/references/routing.md" "Use C4 to map architecture."
expect_checker_failure "$T" "TERMINOLOGY_DEFERRED_C4_ACTIVE:" "should fail when deferred C4 becomes active runtime guidance"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/templates/THINKING.md" "FMEA-lite uses numeric RPN scores."
expect_checker_failure "$T" "TERMINOLOGY_RPN_THEATER:" "should fail on numeric RPN theater"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/templates/THINKING.md" "FMEA-lite improves the plan."
expect_checker_failure "$T" "TERMINOLOGY_ORPHAN_TERM:" "should fail on orphan term without runtime mapping"
rm -rf "$(dirname "$T")"

total=$((pass + fail))
if [ "$fail" -eq 0 ]; then
  printf 'terminology-integration.test: ok (%d/%d)\n' "$pass" "$total"
else
  for e in "${errors[@]}"; do printf '%s\n' "$e" >&2; done
  printf 'terminology-integration.test: FAIL (%d/%d passed)\n' "$pass" "$total" >&2
  exit 1
fi
