#!/usr/bin/env bash
set -euo pipefail

# Fanout coverage test (#49, IA-ACTION-FANOUT): runs the checker on the live
# repo, proves the extended child-prompt validation rejects a fanout-free
# prompt, and proves the checker fails on mutated copies (embedded negative
# controls).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'fanout-coverage-contract.test: %s\n' "$*" >&2
  exit 1
}

# 1. Positive: live repo passes.
bash scripts/check-fanout-coverage-contract.sh \
  || fail "checker fails on the live repo"

# 2. Extended child-prompt validation: both exemplar prompts pass with the
#    fanout tokens; the fanout-free negative prompt fails.
bash scripts/check-plan-quality-contract.sh \
  --child-prompt-file fixtures/child-agents/read-only-contract-auditor.md \
  --child-prompt-file fixtures/child-agents/adversarial-behavioral-auditor.md \
  >/dev/null 2>&1 || fail "exemplar child prompts fail extended validation"

out="/tmp/implementaudit-fanout-neg-prompt.out"
if bash scripts/check-plan-quality-contract.sh \
  --child-prompt-file fixtures/child-agents/negative-child-prompt-missing-fanout-contract.md \
  >"$out" 2>&1; then
  fail "fanout-free child prompt unexpectedly passed validation"
fi
grep -Fq "missing required token" "$out" \
  || { cat "$out" >&2; fail "expected missing-token diagnostic"; }
rm -f "$out"

# Sandbox for checker negative controls.
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

reset_sandbox() {
  rm -rf "$tmp_root"
  mkdir -p \
    "$tmp_root/skills/implementaudit/references" \
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/child-agents"
  cp skills/implementaudit/references/child-agents.md \
    skills/implementaudit/references/audit-category-matrix.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/templates/THINKING.md \
    "$tmp_root/skills/implementaudit/templates/"
  cp fixtures/child-agents/*.md "$tmp_root/fixtures/child-agents/"
}

expect_fail() {
  local label="$1"
  if bash scripts/check-fanout-coverage-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1; then
    fail "negative control not detected: $label"
  fi
}

# 3. Sanity: untouched sandbox passes.
reset_sandbox
bash scripts/check-fanout-coverage-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "checker fails on the untouched sandbox copy"

# 4. Binding clause removed from child-agents.md -> must fail.
reset_sandbox
grep -v "never silently erase a warranted lane" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "child-agents.md without the silent-erase prohibition"

# 5. Coverage lanes lose their template home -> must fail.
reset_sandbox
sed 's/^Coverage lanes .*$/Removed field./' \
  "$tmp_root/skills/implementaudit/templates/THINKING.md" \
  >"$tmp_root/thinking.tmp"
mv "$tmp_root/thinking.tmp" \
  "$tmp_root/skills/implementaudit/templates/THINKING.md"
expect_fail "THINKING.md without the Coverage lanes field"

# 6. A negative fixture disappears -> must fail.
reset_sandbox
rm "$tmp_root/fixtures/child-agents/negative-silent-lane-drop.md"
expect_fail "missing negative-silent-lane-drop fixture"

# 7. Fanout token leaks into the fanout-free negative prompt -> must fail.
reset_sandbox
printf '\nAlso include recon facts here.\n' \
  >>"$tmp_root/fixtures/child-agents/negative-child-prompt-missing-fanout-contract.md"
expect_fail "token leak into the fanout-free negative prompt"

# 8. Command-mode advertisement in a fanout fixture -> must fail.
reset_sandbox
printf '\nAdvertised mode: /implementaudit deep\n' \
  >>"$tmp_root/fixtures/child-agents/broad-scope-four-lanes.md"
expect_fail "command-mode advertisement in a fanout fixture"

printf 'fanout-coverage-contract.test: ok\n'
