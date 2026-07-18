#!/usr/bin/env bash
set -euo pipefail

# Cold-review contract test (#51, IA-ACTION-COLD-REVIEW): runs the checker
# on the live repo, then proves it fails on mutated copies (embedded
# negative controls).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'cold-review-contract.test: %s\n' "$*" >&2
  exit 1
}

# 1. Positive: live repo passes.
bash scripts/check-cold-review-contract.sh \
  || fail "checker fails on the live repo"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

reset_sandbox() {
  rm -rf "$tmp_root"
  mkdir -p \
    "$tmp_root/skills/implementaudit/references" \
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/cold-review" \
    "$tmp_root/fixtures/audit-object-routing"
  cp skills/implementaudit/SKILL.md "$tmp_root/skills/implementaudit/"
  cp skills/implementaudit/references/planning-depth.md \
    skills/implementaudit/references/plan-lifecycle.md \
    skills/implementaudit/references/child-agents.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/templates/ROADMAP.md \
    skills/implementaudit/templates/THINKING.md \
    "$tmp_root/skills/implementaudit/templates/"
  cp fixtures/cold-review/*.md "$tmp_root/fixtures/cold-review/"
  cp fixtures/audit-object-routing/plan-lifecycle.md \
    "$tmp_root/fixtures/audit-object-routing/"
}

expect_fail() {
  local label="$1"
  if bash scripts/check-cold-review-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1; then
    fail "negative control not detected: $label"
  fi
}

# 2. Sanity: untouched sandbox passes.
reset_sandbox
bash scripts/check-cold-review-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "checker fails on the untouched sandbox copy"

# 3. Stage 6.2 removed from the stage map -> must fail.
reset_sandbox
sed 's/^### Stage 6.2 - Independent cold review$/### Stage 6.2 - Removed/' \
  "$tmp_root/skills/implementaudit/SKILL.md" >"$tmp_root/skill.tmp"
mv "$tmp_root/skill.tmp" "$tmp_root/skills/implementaudit/SKILL.md"
expect_fail "SKILL.md without Stage 6.2"

# 4. Readiness gate clause removed from plan-lifecycle -> must fail.
reset_sandbox
grep -v "without a recorded disposition" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md" \
  >"$tmp_root/plan-lifecycle.tmp"
mv "$tmp_root/plan-lifecycle.tmp" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md"
expect_fail "plan-lifecycle.md without the readiness gate"

# 5. Projection loses its derivative statement -> must fail.
reset_sandbox
sed 's/derivative, never canonical/authoritative/' \
  "$tmp_root/skills/implementaudit/templates/ROADMAP.md" \
  >"$tmp_root/roadmap.tmp"
mv "$tmp_root/roadmap.tmp" "$tmp_root/skills/implementaudit/templates/ROADMAP.md"
expect_fail "ROADMAP.md without the derivative-projection statement"

# 6. A negative fixture disappears -> must fail.
reset_sandbox
rm "$tmp_root/fixtures/cold-review/negative-same-context-review.md"
expect_fail "missing negative-same-context-review fixture"

# 7. Command-mode advertisement in a cold-review fixture -> must fail.
reset_sandbox
printf '\nAdvertised mode: /implementaudit review-plan\n' \
  >>"$tmp_root/fixtures/cold-review/independent-review-confirms-handoff.md"
expect_fail "command-mode advertisement in a cold-review fixture"

printf 'cold-review-contract.test: ok\n'
