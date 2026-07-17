#!/usr/bin/env bash
set -euo pipefail

# Governed state-space convergence mode (#11), EXPERIMENTAL/optional:
# structural checks only — the reference exists, is NOT inlined into the
# bootloader path, declares trigger/mode/exit/adoption-gate, and the two
# adoption-gate fixtures are well-formed (positive 3-dim + negative
# single-fault control). The model-in-the-loop adoption gate itself is a
# #9 evaluation and is NOT run here.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

ref="skills/implementaudit/references/convergence-mode.md"
skill="skills/implementaudit/SKILL.md"
fx="fixtures/convergence-mode"
fail() { printf 'convergence-mode-contract: %s\n' "$*" >&2; exit 1; }

[ -f "$ref" ] || fail "optional reference $ref missing"
flat="$(tr '\n' ' ' < "$ref" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'EXPERIMENTAL' || fail "reference must be marked experimental"
printf '%s' "$flat" | grep -qi 'When it applies (trigger)' || fail "trigger section missing"
printf '%s' "$flat" | grep -qi 'Enumeration artifact' || fail "enumeration artifact step missing"
printf '%s' "$flat" | grep -qi 'exactly one outer qualification' || fail "single-outer-qualification missing"
printf '%s' "$flat" | grep -qi 'Adoption gate' || fail "adoption gate missing"
printf '%s' "$flat" | grep -qi 'single-fault fixture .* must NOT trigger\|must NOT trigger' \
  || fail "negative-control (must-not-trigger) missing"

# Progressive disclosure: the reference must NOT be inlined into the
# bootloader path. SKILL.md may POINT to it, but not carry its body — guard
# the budget by asserting the trigger prose is not duplicated in SKILL.md.
if grep -qi 'bounded read-only discovery' "$skill"; then
  fail "convergence-mode body leaked into the bootloader SKILL.md (must stay in references/, on-trigger)"
fi

# Fixtures well-formed.
grep -q '^expected_trigger: yes' "$fx/under-specified-3d.md" \
  || fail "positive fixture must declare expected_trigger: yes"
grep -q '^expected_enumeration_dimensions: 3' "$fx/under-specified-3d.md" \
  || fail "positive fixture must declare 3 enumeration dimensions"
grep -q '^expected_trigger: no' "$fx/single-fault-control.md" \
  || fail "negative control must declare expected_trigger: no"

printf 'convergence-mode-contract: ok (optional reference + 2 adoption-gate fixtures; gate not run)\n'
