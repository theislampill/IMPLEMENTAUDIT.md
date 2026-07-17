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

# --- Fable review of PR #29: adversarial regressions -----------------------
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
adv_fail() {  # label, record-content
  printf '%s\n' "$2" > "$tmp/adv.md"
  if bash "$scorer" "$tmp/adv.md" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "$1 expected FAIL"
  fi
}
adv_pass() {
  printf '%s\n' "$2" > "$tmp/adv.md"
  bash "$scorer" "$tmp/adv.md" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "$1 expected PASS"
}

lift_rec='IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: governing-rule evidence (qualifying trigger).
Lesson-lift: lesson observed = x; decision: lift; reason = y; destination: checker or deterministic test; target: tests/andon-class-contract.test.sh; authority: repo; encoding written: yes; mechanically active: yes; installed current: n/a; recurrence class: regression.
AUDIT_COMPLETE'

# Hidden wordings of the forbidden prevention claim still fail.
adv_fail "hidden prevented-variant (worded)" \
  "$lift_rec
The recurrence has been prevented by this encoding."
adv_fail "hidden prevented-variant (prevents recurrence)" \
  "$lift_rec
This encoding prevents recurrence of the class."

# Two Lesson-lift records in one closure are competing records.
adv_fail "duplicate competing records" \
'IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: qualifying trigger: recurrence.
Lesson-lift: lesson observed = a; decision: lift; reason = z; destination: project docs; authority: repo.
Lesson-lift: lesson observed = a; decision: no-lift; reason = w; destination: no lift; authority: n/a.
AUDIT_COMPLETE'

# A no-lift decision with an EMPTY reason is a bare no.
adv_fail "empty no-lift reason" \
'IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: qualifying trigger: recurrence.
Lesson-lift: lesson observed = a; decision: no-lift; reason = ; destination: no lift; authority: n/a.
AUDIT_COMPLETE'

# A one-off disposition mentioning "recurrence" in its own line must NOT
# be forced into lift ceremony (bounded trigger).
adv_pass "one-off disposition mentioning recurrence" \
'IMPLEMENTAUDIT_PHASE_VERIFY
No-lift: one-off typo; no recurrence expected.
AUDIT_COMPLETE'

printf 'lesson-lift-contract: ok (contract + 4 fail + 3 pass fixtures + 5 adversarial)\n'
