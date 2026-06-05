#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'validate-phase: %s\n' "$*" >&2
  exit 1
}

phase_file="${1:-}"
[ -n "$phase_file" ] || fail "usage: validate-phase.sh <phase-file>"
[ -f "$phase_file" ] || fail "phase file not found: $phase_file"

for marker in \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE
do
  grep -q "$marker" "$phase_file" || fail "missing marker: $marker"
done

grep -qi "Smoke A" "$phase_file" || fail "missing Smoke A"
grep -qi "Smoke B" "$phase_file" || fail "missing Smoke B"
grep -qi "Owner/source" "$phase_file" || fail "missing Owner/source"
grep -qi "Acceptance" "$phase_file" || fail "missing Acceptance"

printf 'validate-phase: ok\n'
