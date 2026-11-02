#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-routing.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

expect_failure() {
  local label="$1" expected="$2" diagnostic checker_status=0
  (cd "$tmp" && bash scripts/check-routing.sh) \
    >"$tmp/checker.stdout" 2>"$tmp/checker.stderr" || checker_status=$?
  diagnostic="$(<"$tmp/checker.stderr")"
  if [[ "$checker_status" -ne 1 || -s "$tmp/checker.stdout" || "$diagnostic" != "$expected" ]]; then
    printf 'routing.test: expected %s to fail only with its intended diagnostic (exit 1); got exit %s\n' \
      "$label" "$checker_status" >&2
    cat "$tmp/checker.stdout" "$tmp/checker.stderr" >&2
    exit 1
  fi
}

mkdir -p "$tmp/scripts"
mkdir -p "$tmp/fixtures/routing/greenfield-goal-synthesis"
mkdir -p "$tmp/fixtures/routing/greenfield-full-category-intake"
mkdir -p "$tmp/fixtures/routing/greenfield-batched-questions"
mkdir -p "$tmp/fixtures/routing/brownfield-audit-closure"
mkdir -p "$tmp/fixtures/routing/brownfield-zero-question-recon"
mkdir -p "$tmp/fixtures/routing/brownfield-one-question-true-gap"
mkdir -p "$tmp/fixtures/routing/brownfield-two-question-true-gap"
mkdir -p "$tmp/fixtures/routing/mixed-greenfield-in-brownfield"
mkdir -p "$tmp/skills/implementaudit/references"
cp skills/implementaudit/references/routing.md "$tmp/skills/implementaudit/references/routing.md"
cp skills/implementaudit/references/audit-category-matrix.md "$tmp/skills/implementaudit/references/audit-category-matrix.md"
cp skills/implementaudit/references/plan-lifecycle.md "$tmp/skills/implementaudit/references/plan-lifecycle.md"
cp skills/implementaudit/references/planning-depth.md "$tmp/skills/implementaudit/references/planning-depth.md"
cp skills/implementaudit/references/goal-format.md "$tmp/skills/implementaudit/references/goal-format.md"
cp skills/implementaudit/references/phase-design.md "$tmp/skills/implementaudit/references/phase-design.md"
cp skills/implementaudit/SKILL.md "$tmp/skills/implementaudit/SKILL.md"
cp README.md "$tmp/README.md"
cp AGENTS.md "$tmp/AGENTS.md"
cp fixtures/routing/greenfield-goal-synthesis/EXPECTED.md "$tmp/fixtures/routing/greenfield-goal-synthesis/EXPECTED.md"
cp fixtures/routing/greenfield-full-category-intake/EXPECTED.md "$tmp/fixtures/routing/greenfield-full-category-intake/EXPECTED.md"
cp fixtures/routing/greenfield-batched-questions/EXPECTED.md "$tmp/fixtures/routing/greenfield-batched-questions/EXPECTED.md"
cp fixtures/routing/brownfield-audit-closure/EXPECTED.md "$tmp/fixtures/routing/brownfield-audit-closure/EXPECTED.md"
cp fixtures/routing/brownfield-zero-question-recon/EXPECTED.md "$tmp/fixtures/routing/brownfield-zero-question-recon/EXPECTED.md"
cp fixtures/routing/brownfield-one-question-true-gap/EXPECTED.md "$tmp/fixtures/routing/brownfield-one-question-true-gap/EXPECTED.md"
cp fixtures/routing/brownfield-two-question-true-gap/EXPECTED.md "$tmp/fixtures/routing/brownfield-two-question-true-gap/EXPECTED.md"
cp fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md "$tmp/fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md"
cp fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md "$tmp/fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md"
cp fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md "$tmp/fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md"
cp scripts/check-routing.sh "$tmp/scripts/check-routing.sh"

# The unchanged checker derives its root from scripts/..; prove the copied
# input closure passes before interpreting any mutation as a semantic failure.
(cd "$tmp" && bash scripts/check-routing.sh >/dev/null)

cat >"$tmp/fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md" <<'BAD'
# Invalid But Too Complete

owner/source of truth
rollback/removal path
evidence plan
BAD
intake_diagnostic="$(cat <<'EXPECTED'
fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md: invalid fixture unexpectedly contains pass field: owner/source of truth
fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md: invalid fixture unexpectedly contains pass field: rollback/removal path
fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md: invalid fixture unexpectedly contains pass field: evidence plan
EXPECTED
)"
expect_failure 'invalid greenfield fixture with pass fields' "$intake_diagnostic"

cp fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md "$tmp/fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md"
(cd "$tmp" && bash scripts/check-routing.sh >/dev/null)
bad_phrase_a="generic autonomous"
bad_phrase_b="build runner"
printf 'IMPLEMENTAUDIT is a %s %s.\n' "$bad_phrase_a" "$bad_phrase_b" >>"$tmp/README.md"
bad_line_no="$(wc -l <"$tmp/README.md")"
expect_failure 'endorsed generic-runner wording' \
  "README.md:$((bad_line_no)): endorsed generic-runner wording: $bad_phrase_a $bad_phrase_b"

printf 'routing.test: ok\n'
