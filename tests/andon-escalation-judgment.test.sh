#!/usr/bin/env bash
set -euo pipefail

# ANDON_ESCALATE governing-rule (second-order recurrence) judgment (#7):
# the escalation contract must carry the judgment step, and the five
# scored fixtures must each contain the judgment token that the contract
# requires for their situation.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
fail() { printf 'andon-escalation-judgment: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'Governing-rule review (second-order recurrence)' \
  || fail "governing-rule review step missing from ANDON_ESCALATE"
printf '%s' "$flat" | grep -qi 'Governing-rule judgment:' \
  || fail "Governing-rule judgment field missing"
printf '%s' "$flat" | grep -qi 'correct-by-luck' \
  || fail "correct-by-luck pathway missing"
printf '%s' "$flat" | grep -qi 'neighboring-perturbation' \
  || fail "neighboring-perturbation probe admissibility missing"
printf '%s' "$flat" | grep -qi 'separate judgments' \
  || fail "answer-correctness vs pathway-adequacy separation missing"
printf '%s' "$flat" | grep -qi 'Rejecting governing-rule suspicion REQUIRES a recorded reason' \
  || fail "reasoned-rejection rule missing"
printf '%s' "$flat" | grep -qi 'governing-rule suspicion' \
  || fail "Hansei governing-rule-suspicion field missing"

# --- five scored transcript fixtures (the judgment token per situation) ----
dir="fixtures/andon-escalation"
[ -d "$dir" ] || fail "fixture dir $dir missing"

score() {  # file, required-token
  grep -Fq "$2" "$1" || fail "fixture $1 missing required token: $2"
}

score "$dir/same-class-recurrence.md" "Governing-rule judgment:"
score "$dir/first-occurrence-misscoped-validator.md" \
  "governing-rule-defect (validator)"
score "$dir/cross-class-shared-invariant.md" \
  "governing-rule-defect (standard)"
score "$dir/correct-by-luck-perturbation.md" \
  "correct current placement, defective pathway"
score "$dir/reasoned-rejection.md" "case-defect"
# the reasoned-rejection fixture must record a REASON, not a bare no
grep -Fq "Rejection reason:" "$dir/reasoned-rejection.md" \
  || fail "reasoned-rejection fixture must record an explicit reason"

printf 'andon-escalation-judgment: ok (contract + 5 scored fixtures)\n'
