#!/usr/bin/env bash
set -euo pipefail

# Action-selection contract test (#48, IA-ACTION-DEPTH): runs the checker on
# the live repo, then proves the checker actually fails on mutated copies
# (embedded negative controls, not whole-file grep optimism).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'action-selection-contract.test: %s\n' "$*" >&2
  exit 1
}

# 1. Positive: live repo passes.
bash scripts/check-action-selection-contract.sh \
  || fail "checker fails on the live repo"

# Sandbox for negative controls.
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

reset_sandbox() {
  rm -rf "$tmp_root"
  mkdir -p \
    "$tmp_root/skills/implementaudit/references" \
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/audit-action-selection" \
    "$tmp_root/fixtures/native-integration" \
    "$tmp_root/fixtures/audit-object-routing"
  cp skills/implementaudit/SKILL.md "$tmp_root/skills/implementaudit/"
  cp skills/implementaudit/references/planning-depth.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/templates/THINKING.md \
    skills/implementaudit/templates/ROADMAP.md \
    "$tmp_root/skills/implementaudit/templates/"
  cp fixtures/audit-action-selection/*.md \
    "$tmp_root/fixtures/audit-action-selection/"
  cp fixtures/native-integration/single-plan-native-route.md \
    "$tmp_root/fixtures/native-integration/"
  cp fixtures/audit-object-routing/deep-pressure-disclosure.md \
    "$tmp_root/fixtures/audit-object-routing/"
}

expect_fail() {
  local label="$1"
  if bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1; then
    fail "negative control not detected: $label"
  fi
}

# 2. Sanity: untouched sandbox passes.
reset_sandbox
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "checker fails on the untouched sandbox copy"

# 3. Keyword-freedom clause removed from the contract -> must fail.
reset_sandbox
grep -v "Depth never requires an activation keyword" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md" \
  >"$tmp_root/planning-depth.tmp"
mv "$tmp_root/planning-depth.tmp" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md"
expect_fail "planning-depth.md without the keyword-freedom clause"

# 4. Action-selection record loses its template home -> must fail.
reset_sandbox
sed 's/^## Action selection$/## Renamed section/' \
  "$tmp_root/skills/implementaudit/templates/THINKING.md" \
  >"$tmp_root/thinking.tmp"
mv "$tmp_root/thinking.tmp" \
  "$tmp_root/skills/implementaudit/templates/THINKING.md"
expect_fail "THINKING.md without the Action selection section"

# 5. A negative fixture disappears -> must fail.
reset_sandbox
rm "$tmp_root/fixtures/audit-action-selection/negative-keyword-gated-depth.md"
expect_fail "missing negative-keyword-gated-depth fixture"

# 6. Command-mode advertisement in the new surfaces -> must fail.
reset_sandbox
printf '\nAdvertised mode: /implementaudit deep\n' \
  >>"$tmp_root/fixtures/audit-action-selection/ordinary-task-deepens.md"
expect_fail "command-mode advertisement in an action-selection fixture"

printf 'action-selection-contract.test: ok\n'
