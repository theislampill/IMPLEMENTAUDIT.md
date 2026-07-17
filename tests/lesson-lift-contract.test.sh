#!/usr/bin/env bash
set -euo pipefail

# Lesson-lift routing record (#13): the PROTOCOL contract text and the
# scorer's five acceptance fixtures + negative control.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-lesson-lift.sh"
fx="fixtures/lesson-lift"
fail() { printf 'lesson-lift-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'Lesson-lift routing record' \
  || fail "PROTOCOL missing the Lesson-lift routing record subsection"
printf '%s' "$flat" | grep -qi 'produces exactly ONE canonical lift record' \
  || fail "unification (one canonical record) missing"
printf '%s' "$flat" | grep -qi 'closure must never claim .*recurrence' \
  || fail "closure-must-not-claim-prevention rule missing"
printf '%s' "$flat" | grep -qi 'cheap to redo by hand.*insufficient' \
  || fail "insufficient-reason rule missing"

pass_case() {
  bash "$scorer" "$fx/$1" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "$1 expected PASS"
}
fail_case() {
  if bash "$scorer" "$fx/$1" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "$1 expected FAIL"
  fi
}

fail_case qualifying-no-record-FAIL.md
fail_case checker-active-mismatch-FAIL.md
fail_case easy-redo-noreason-FAIL.md
fail_case prevented-claim-FAIL.md
pass_case reasoned-nolift-PASS.md
pass_case oneoff-typo-PASS.md
pass_case checker-active-ok-PASS.md

printf 'lesson-lift-contract: ok (contract + 4 fail + 3 pass fixtures)\n'
