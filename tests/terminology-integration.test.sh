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

expect_checker_success() {
  local repo="$1" label="$2" out rc
  set +e
  out="$(bash "$repo/scripts/check-terminology-integration.sh" --repo-root "$repo" 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    ok
  else
    fail_case "FAIL: $label (expected rc=0; rc=$rc; output=$out)"
  fi
}

expect_missing_owner_hook() {
  local repo="$1" expected="$2" label="$3" out rc owner_lines owner_count exact_count
  set +e
  out="$(bash "$repo/scripts/check-terminology-integration.sh" --repo-root "$repo" 2>&1)"
  rc=$?
  set -e
  owner_lines="$(printf '%s\n' "$out" | grep -F 'skills/implementaudit/SKILL.md: missing owner hook:' || true)"
  owner_count="$(printf '%s\n' "$owner_lines" | grep -Fc 'skills/implementaudit/SKILL.md: missing owner hook:' || true)"
  exact_count="$(printf '%s\n' "$owner_lines" | grep -Fxc "$expected" || true)"
  if [ "$rc" -ne 0 ] && [ "$owner_count" -eq 1 ] && [ "$exact_count" -eq 1 ]; then
    ok
  else
    fail_case "FAIL: $label (expected only owner diagnostic: $expected; rc=$rc; owner diagnostics=$owner_lines; output=$out)"
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

ensure_owner_hook_sentence() {
  local file="$1/skills/implementaudit/SKILL.md"
  "$PY" - "$file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
sentence = (
    "Use FMEA-lite fields when risk is material, STRIDE/trust-boundary notes when a material "
    "security surface exists, SOLID/GRASP generic-advice guard, and a terminology integration "
    "attachment when used."
)
if sentence not in re.sub(r"\s+", " ", text):
    anchor = "- `references/terminology-integration.md`: thin terminology precedence.\n"
    if anchor not in text:
        raise SystemExit("terminology-integration test fixture missing insertion anchor")
    replacement = (
        anchor
        + "  Use FMEA-lite fields when risk is material, STRIDE/trust-boundary notes when\n"
        + "  a material security surface exists, SOLID/GRASP generic-advice guard, and a\n"
        + "  terminology integration attachment when used.\n"
    )
    text = text.replace(anchor, replacement, 1)
    path.write_text(text, encoding="utf-8")
PY
}

remove_owner_hook() {
  local file="$1/skills/implementaudit/SKILL.md" hook="$2"
  "$PY" - "$file" "$hook" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
hook = sys.argv[2]
text = path.read_text(encoding="utf-8")
pattern = re.compile(re.escape(hook).replace(r"\ ", r"\s+"))
text, count = pattern.subn("owner hook removed for isolated negative control", text, count=1)
if count != 1:
    raise SystemExit(f"terminology-integration test fixture did not remove exactly one owner hook: {hook}")
path.write_text(text, encoding="utf-8")
PY
}

if bash scripts/check-terminology-integration.sh >/dev/null 2>&1; then
  ok
else
  fail_case "FAIL: check-terminology-integration.sh should pass on current repo"
fi

T=$(make_temp)
printf '# Runtime Terminology\n\n## Term Entries\n\n- Term: A3\n' > "$T/skills/implementaudit/references/runtime-terminology.md"
expect_checker_failure "$T" "TERMINOLOGY_GLOSSARY_FILE:" "should fail when runtime-terminology.md returns"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/implementaudit/templates/THINKING.md" "VOC CTQ SIPOC FMEA STRIDE SOLID GRASP Control Plan."
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
append_text "$T/skills/implementaudit/references/terminology-integration.md" "## Term Entries"
expect_checker_failure "$T" "TERMINOLOGY_TERM_ENTRY_DRIFT:" "should fail if thin contract becomes a term-entry glossary"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/implementaudit/references/routing.md" "Use C4 to map architecture."
expect_checker_failure "$T" "TERMINOLOGY_DEFERRED_C4_ACTIVE:" "should fail when deferred C4 becomes active runtime guidance"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/implementaudit/templates/THINKING.md" "FMEA-lite uses numeric RPN scores."
expect_checker_failure "$T" "TERMINOLOGY_RPN_THEATER:" "should fail on numeric RPN theater"
rm -rf "$(dirname "$T")"

T=$(make_temp)
append_text "$T/skills/implementaudit/templates/THINKING.md" "FMEA-lite improves the plan."
expect_checker_failure "$T" "TERMINOLOGY_ORPHAN_TERM:" "should fail on orphan term without runtime mapping"
rm -rf "$(dirname "$T")"

T=$(make_temp)
ensure_owner_hook_sentence "$T"
append_text "$T/skills/implementaudit/templates/THINKING.md" "Record the filesystem access-control ACL beside the SID, UID, mode bits, and executable-handle identity."
expect_checker_success "$T" "should accept filesystem access-control ACL without terminology-owner language"
rm -rf "$(dirname "$T")"

T=$(make_temp)
ensure_owner_hook_sentence "$T"
append_text "$T/skills/implementaudit/templates/THINKING.md" "Adopt an Anti-Corruption Layer for the migration."
expect_checker_failure "$T" "TERMINOLOGY_ORPHAN_TERM:" "should reject orphan spelled-out Anti-Corruption Layer guidance"
rm -rf "$(dirname "$T")"

for hook in \
  "FMEA-lite fields when risk is material" \
  "STRIDE/trust-boundary notes when a material security surface exists" \
  "SOLID/GRASP generic-advice guard" \
  "terminology integration attachment when used"
do
  T=$(make_temp)
  ensure_owner_hook_sentence "$T"
  remove_owner_hook "$T" "$hook"
  expect_missing_owner_hook \
    "$T" \
    "skills/implementaudit/SKILL.md: missing owner hook: $hook" \
    "should report only the exact missing owner hook for $hook"
  rm -rf "$(dirname "$T")"
done

total=$((pass + fail))
if [ "$fail" -eq 0 ]; then
  printf 'terminology-integration.test: ok (%d/%d)\n' "$pass" "$total"
else
  for e in "${errors[@]}"; do printf '%s\n' "$e" >&2; done
  printf 'terminology-integration.test: FAIL (%d/%d passed)\n' "$pass" "$total" >&2
  exit 1
fi
