#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The live repo must carry fixture-backed semantic parity.
bash scripts/check-audit-object-routing-contract.sh

# 2. A fixture-only copy with no runtime contract must fail. Fixtures are not
# proof unless the runtime also routes the behavior.
mkdir -p "$tmp/fixture-only/skills/references" "$tmp/fixture-only/skills/templates" "$tmp/fixture-only/fixtures"
cp skills/references/audit-category-matrix.md "$tmp/fixture-only/skills/references/audit-category-matrix.md"
cp skills/references/audit-playbook.md "$tmp/fixture-only/skills/references/audit-playbook.md"
cp skills/references/plan-lifecycle.md "$tmp/fixture-only/skills/references/plan-lifecycle.md"
cp skills/references/routing.md "$tmp/fixture-only/skills/references/routing.md"
cp skills/references/child-agents.md "$tmp/fixture-only/skills/references/child-agents.md"
cp skills/references/planning-depth.md "$tmp/fixture-only/skills/references/planning-depth.md"
cp skills/references/phase-design.md "$tmp/fixture-only/skills/references/phase-design.md"
cp skills/references/goal-format.md "$tmp/fixture-only/skills/references/goal-format.md"
cp skills/references/transcript-contract.md "$tmp/fixture-only/skills/references/transcript-contract.md"
cp skills/templates/THINKING.md "$tmp/fixture-only/skills/templates/THINKING.md"
cp skills/templates/phase-goal.txt "$tmp/fixture-only/skills/templates/phase-goal.txt"
cp skills/templates/PROTOCOL.md "$tmp/fixture-only/skills/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/fixture-only/fixtures/"

printf '# Audit Category Matrix\n' > "$tmp/fixture-only/skills/references/audit-category-matrix.md"

if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/fixture-only" >/tmp/fixture-only.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected fixture-only copy to fail\n' >&2
  exit 1
fi
grep -q "missing in skills/references/audit-category-matrix.md: ## Native Category Route Contract" /tmp/fixture-only.out || {
  printf 'audit-object-routing-contract.test: fixture-only failure was not the intended runtime-contract failure\n' >&2
  cat /tmp/fixture-only.out >&2
  exit 1
}

# 3. A runtime-only copy with missing fixtures must fail. Runtime prose alone is
# not enough for the imported behaviors assimilated in v0.3.0.0.
mkdir -p "$tmp/runtime-only/skills/references" "$tmp/runtime-only/skills/templates" "$tmp/runtime-only/fixtures/audit-object-routing"
cp skills/references/audit-category-matrix.md "$tmp/runtime-only/skills/references/audit-category-matrix.md"
cp skills/references/audit-playbook.md "$tmp/runtime-only/skills/references/audit-playbook.md"
cp skills/references/plan-lifecycle.md "$tmp/runtime-only/skills/references/plan-lifecycle.md"
cp skills/references/routing.md "$tmp/runtime-only/skills/references/routing.md"
cp skills/references/child-agents.md "$tmp/runtime-only/skills/references/child-agents.md"
cp skills/references/planning-depth.md "$tmp/runtime-only/skills/references/planning-depth.md"
cp skills/references/phase-design.md "$tmp/runtime-only/skills/references/phase-design.md"
cp skills/references/goal-format.md "$tmp/runtime-only/skills/references/goal-format.md"
cp skills/references/transcript-contract.md "$tmp/runtime-only/skills/references/transcript-contract.md"
cp skills/templates/THINKING.md "$tmp/runtime-only/skills/templates/THINKING.md"
cp skills/templates/phase-goal.txt "$tmp/runtime-only/skills/templates/phase-goal.txt"
cp skills/templates/PROTOCOL.md "$tmp/runtime-only/skills/templates/PROTOCOL.md"

if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/runtime-only" >/tmp/runtime-only.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected missing fixtures to fail\n' >&2
  exit 1
fi
grep -q "missing required file: fixtures/audit-object-routing/quick-bounded-audit.md" /tmp/runtime-only.out || {
  printf 'audit-object-routing-contract.test: runtime-only failure was not the intended fixture failure\n' >&2
  cat /tmp/runtime-only.out >&2
  exit 1
}

# 4. A copy missing execute-preflight details must fail on that exact behavior.
mkdir -p "$tmp/no-execute-preflight/skills/references" "$tmp/no-execute-preflight/skills/templates" "$tmp/no-execute-preflight/fixtures"
cp skills/references/audit-category-matrix.md "$tmp/no-execute-preflight/skills/references/audit-category-matrix.md"
cp skills/references/audit-playbook.md "$tmp/no-execute-preflight/skills/references/audit-playbook.md"
cp skills/references/plan-lifecycle.md "$tmp/no-execute-preflight/skills/references/plan-lifecycle.md"
cp skills/references/routing.md "$tmp/no-execute-preflight/skills/references/routing.md"
cp skills/references/child-agents.md "$tmp/no-execute-preflight/skills/references/child-agents.md"
cp skills/references/planning-depth.md "$tmp/no-execute-preflight/skills/references/planning-depth.md"
cp skills/references/phase-design.md "$tmp/no-execute-preflight/skills/references/phase-design.md"
cp skills/references/goal-format.md "$tmp/no-execute-preflight/skills/references/goal-format.md"
cp skills/references/transcript-contract.md "$tmp/no-execute-preflight/skills/references/transcript-contract.md"
cp skills/templates/THINKING.md "$tmp/no-execute-preflight/skills/templates/THINKING.md"
cp skills/templates/phase-goal.txt "$tmp/no-execute-preflight/skills/templates/phase-goal.txt"
cp skills/templates/PROTOCOL.md "$tmp/no-execute-preflight/skills/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/no-execute-preflight/fixtures/"
sed -i 's/dependency-DONE checks/dependency checks/' "$tmp/no-execute-preflight/skills/references/plan-lifecycle.md"
if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/no-execute-preflight" >/tmp/no-execute-preflight.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected missing execute preflight to fail\n' >&2
  exit 1
fi
grep -q "missing in skills/references/plan-lifecycle.md: dependency-DONE checks" /tmp/no-execute-preflight.out || {
  printf 'audit-object-routing-contract.test: execute-preflight failure was not the intended contract failure\n' >&2
  cat /tmp/no-execute-preflight.out >&2
  exit 1
}

# 5. The native category rows must stay stronger than mere listing.
mkdir -p "$tmp/no-category-surpass/skills/references" "$tmp/no-category-surpass/skills/templates" "$tmp/no-category-surpass/fixtures"
cp skills/references/audit-category-matrix.md "$tmp/no-category-surpass/skills/references/audit-category-matrix.md"
cp skills/references/audit-playbook.md "$tmp/no-category-surpass/skills/references/audit-playbook.md"
cp skills/references/plan-lifecycle.md "$tmp/no-category-surpass/skills/references/plan-lifecycle.md"
cp skills/references/routing.md "$tmp/no-category-surpass/skills/references/routing.md"
cp skills/references/child-agents.md "$tmp/no-category-surpass/skills/references/child-agents.md"
cp skills/references/planning-depth.md "$tmp/no-category-surpass/skills/references/planning-depth.md"
cp skills/references/phase-design.md "$tmp/no-category-surpass/skills/references/phase-design.md"
cp skills/references/goal-format.md "$tmp/no-category-surpass/skills/references/goal-format.md"
cp skills/references/transcript-contract.md "$tmp/no-category-surpass/skills/references/transcript-contract.md"
cp skills/templates/THINKING.md "$tmp/no-category-surpass/skills/templates/THINKING.md"
cp skills/templates/phase-goal.txt "$tmp/no-category-surpass/skills/templates/phase-goal.txt"
cp skills/templates/PROTOCOL.md "$tmp/no-category-surpass/skills/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/no-category-surpass/fixtures/"
sed -i '/performance \/ scale | Native route exceeds baseline through measurement-or-static-evidence distinction/d' \
  "$tmp/no-category-surpass/fixtures/audit-object-routing/category-matrix.md"
if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/no-category-surpass" >/tmp/no-category-surpass.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected missing category-surpass row to fail\n' >&2
  exit 1
fi
grep -q "missing in fixtures/audit-object-routing/category-matrix.md: performance / scale | Native route exceeds baseline through measurement-or-static-evidence distinction" /tmp/no-category-surpass.out || {
  printf 'audit-object-routing-contract.test: category-surpass failure was not the intended contract failure\n' >&2
  cat /tmp/no-category-surpass.out >&2
  exit 1
}

printf 'audit-object-routing-contract.test: ok\n'
