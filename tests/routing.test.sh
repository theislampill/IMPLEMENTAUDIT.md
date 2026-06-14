#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-routing.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

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

cat >"$tmp/fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md" <<'BAD'
# Invalid But Too Complete

owner/source of truth
rollback/removal path
evidence plan
BAD
cp fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md "$tmp/fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md"

cp scripts/check-routing.sh "$tmp/check-routing.sh"
if (cd "$tmp" && bash check-routing.sh >/dev/null 2>&1); then
  printf 'routing.test: expected invalid greenfield fixture with pass fields to fail\n' >&2
  exit 1
fi

cp fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md "$tmp/fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md"
cat >>"$tmp/README.md" <<'BAD'
BAD
bad_phrase_a="generic autonomous"
bad_phrase_b="build runner"
printf 'IMPLEMENTAUDIT is a %s %s.\n' "$bad_phrase_a" "$bad_phrase_b" >>"$tmp/README.md"
if (cd "$tmp" && bash check-routing.sh >/dev/null 2>&1); then
  printf 'routing.test: expected endorsed generic-runner wording to fail\n' >&2
  exit 1
fi

printf 'routing.test: ok\n'
