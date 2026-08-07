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
mkdir -p "$tmp/fixture-only/skills/implementaudit/references" "$tmp/fixture-only/skills/implementaudit/templates" "$tmp/fixture-only/fixtures"
cp skills/implementaudit/references/audit-category-matrix.md "$tmp/fixture-only/skills/implementaudit/references/audit-category-matrix.md"
cp skills/implementaudit/references/audit-playbook.md "$tmp/fixture-only/skills/implementaudit/references/audit-playbook.md"
cp skills/implementaudit/references/plan-lifecycle.md "$tmp/fixture-only/skills/implementaudit/references/plan-lifecycle.md"
cp skills/implementaudit/references/routing.md "$tmp/fixture-only/skills/implementaudit/references/routing.md"
cp skills/implementaudit/references/child-agents.md "$tmp/fixture-only/skills/implementaudit/references/child-agents.md"
cp skills/implementaudit/references/planning-depth.md "$tmp/fixture-only/skills/implementaudit/references/planning-depth.md"
cp skills/implementaudit/references/phase-design.md "$tmp/fixture-only/skills/implementaudit/references/phase-design.md"
cp skills/implementaudit/references/goal-format.md "$tmp/fixture-only/skills/implementaudit/references/goal-format.md"
cp skills/implementaudit/references/transcript-contract.md "$tmp/fixture-only/skills/implementaudit/references/transcript-contract.md"
cp skills/implementaudit/templates/THINKING.md "$tmp/fixture-only/skills/implementaudit/templates/THINKING.md"
cp skills/implementaudit/templates/phase-goal.txt "$tmp/fixture-only/skills/implementaudit/templates/phase-goal.txt"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/fixture-only/skills/implementaudit/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/fixture-only/fixtures/"

printf '# Audit Category Matrix\n' > "$tmp/fixture-only/skills/implementaudit/references/audit-category-matrix.md"

if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/fixture-only" >/tmp/fixture-only.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected fixture-only copy to fail\n' >&2
  exit 1
fi
grep -q "missing in skills/implementaudit/references/audit-category-matrix.md: ## Native Category Route Contract" /tmp/fixture-only.out || {
  printf 'audit-object-routing-contract.test: fixture-only failure was not the intended runtime-contract failure\n' >&2
  cat /tmp/fixture-only.out >&2
  exit 1
}

# 3. A runtime-only copy with missing fixtures must fail. Runtime prose alone is
# not enough for the imported behaviors assimilated in v0.3.0.0.
mkdir -p "$tmp/runtime-only/skills/implementaudit/references" "$tmp/runtime-only/skills/implementaudit/templates" "$tmp/runtime-only/fixtures/audit-object-routing"
cp skills/implementaudit/references/audit-category-matrix.md "$tmp/runtime-only/skills/implementaudit/references/audit-category-matrix.md"
cp skills/implementaudit/references/audit-playbook.md "$tmp/runtime-only/skills/implementaudit/references/audit-playbook.md"
cp skills/implementaudit/references/plan-lifecycle.md "$tmp/runtime-only/skills/implementaudit/references/plan-lifecycle.md"
cp skills/implementaudit/references/routing.md "$tmp/runtime-only/skills/implementaudit/references/routing.md"
cp skills/implementaudit/references/child-agents.md "$tmp/runtime-only/skills/implementaudit/references/child-agents.md"
cp skills/implementaudit/references/planning-depth.md "$tmp/runtime-only/skills/implementaudit/references/planning-depth.md"
cp skills/implementaudit/references/phase-design.md "$tmp/runtime-only/skills/implementaudit/references/phase-design.md"
cp skills/implementaudit/references/goal-format.md "$tmp/runtime-only/skills/implementaudit/references/goal-format.md"
cp skills/implementaudit/references/transcript-contract.md "$tmp/runtime-only/skills/implementaudit/references/transcript-contract.md"
cp skills/implementaudit/templates/THINKING.md "$tmp/runtime-only/skills/implementaudit/templates/THINKING.md"
cp skills/implementaudit/templates/phase-goal.txt "$tmp/runtime-only/skills/implementaudit/templates/phase-goal.txt"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/runtime-only/skills/implementaudit/templates/PROTOCOL.md"

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
mkdir -p "$tmp/no-execute-preflight/skills/implementaudit/references" "$tmp/no-execute-preflight/skills/implementaudit/templates" "$tmp/no-execute-preflight/fixtures"
cp skills/implementaudit/references/audit-category-matrix.md "$tmp/no-execute-preflight/skills/implementaudit/references/audit-category-matrix.md"
cp skills/implementaudit/references/audit-playbook.md "$tmp/no-execute-preflight/skills/implementaudit/references/audit-playbook.md"
cp skills/implementaudit/references/plan-lifecycle.md "$tmp/no-execute-preflight/skills/implementaudit/references/plan-lifecycle.md"
cp skills/implementaudit/references/routing.md "$tmp/no-execute-preflight/skills/implementaudit/references/routing.md"
cp skills/implementaudit/references/child-agents.md "$tmp/no-execute-preflight/skills/implementaudit/references/child-agents.md"
cp skills/implementaudit/references/planning-depth.md "$tmp/no-execute-preflight/skills/implementaudit/references/planning-depth.md"
cp skills/implementaudit/references/phase-design.md "$tmp/no-execute-preflight/skills/implementaudit/references/phase-design.md"
cp skills/implementaudit/references/goal-format.md "$tmp/no-execute-preflight/skills/implementaudit/references/goal-format.md"
cp skills/implementaudit/references/transcript-contract.md "$tmp/no-execute-preflight/skills/implementaudit/references/transcript-contract.md"
cp skills/implementaudit/templates/THINKING.md "$tmp/no-execute-preflight/skills/implementaudit/templates/THINKING.md"
cp skills/implementaudit/templates/phase-goal.txt "$tmp/no-execute-preflight/skills/implementaudit/templates/phase-goal.txt"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/no-execute-preflight/skills/implementaudit/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/no-execute-preflight/fixtures/"
sed -i 's/dependency-DONE checks/dependency checks/' "$tmp/no-execute-preflight/skills/implementaudit/references/plan-lifecycle.md"
if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/no-execute-preflight" >/tmp/no-execute-preflight.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected missing execute preflight to fail\n' >&2
  exit 1
fi
grep -q "missing in skills/implementaudit/references/plan-lifecycle.md: dependency-DONE checks" /tmp/no-execute-preflight.out || {
  printf 'audit-object-routing-contract.test: execute-preflight failure was not the intended contract failure\n' >&2
  cat /tmp/no-execute-preflight.out >&2
  exit 1
}

# 5. The native category rows must stay stronger than mere listing.
mkdir -p "$tmp/no-category-strength/skills/implementaudit/references" "$tmp/no-category-strength/skills/implementaudit/templates" "$tmp/no-category-strength/fixtures"
cp skills/implementaudit/references/audit-category-matrix.md "$tmp/no-category-strength/skills/implementaudit/references/audit-category-matrix.md"
cp skills/implementaudit/references/audit-playbook.md "$tmp/no-category-strength/skills/implementaudit/references/audit-playbook.md"
cp skills/implementaudit/references/plan-lifecycle.md "$tmp/no-category-strength/skills/implementaudit/references/plan-lifecycle.md"
cp skills/implementaudit/references/routing.md "$tmp/no-category-strength/skills/implementaudit/references/routing.md"
cp skills/implementaudit/references/child-agents.md "$tmp/no-category-strength/skills/implementaudit/references/child-agents.md"
cp skills/implementaudit/references/planning-depth.md "$tmp/no-category-strength/skills/implementaudit/references/planning-depth.md"
cp skills/implementaudit/references/phase-design.md "$tmp/no-category-strength/skills/implementaudit/references/phase-design.md"
cp skills/implementaudit/references/goal-format.md "$tmp/no-category-strength/skills/implementaudit/references/goal-format.md"
cp skills/implementaudit/references/transcript-contract.md "$tmp/no-category-strength/skills/implementaudit/references/transcript-contract.md"
cp skills/implementaudit/templates/THINKING.md "$tmp/no-category-strength/skills/implementaudit/templates/THINKING.md"
cp skills/implementaudit/templates/phase-goal.txt "$tmp/no-category-strength/skills/implementaudit/templates/phase-goal.txt"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/no-category-strength/skills/implementaudit/templates/PROTOCOL.md"
cp -R fixtures/audit-object-routing "$tmp/no-category-strength/fixtures/"
sed -i '/performance \/ scale | Native route exceeds baseline through measurement-or-static-evidence distinction/d' \
  "$tmp/no-category-strength/fixtures/audit-object-routing/category-matrix.md"
if bash scripts/check-audit-object-routing-contract.sh --scan-root "$tmp/no-category-strength" >/tmp/no-category-strength.out 2>&1; then
  printf 'audit-object-routing-contract.test: expected missing category-strength row to fail\n' >&2
  exit 1
fi
grep -q "missing in fixtures/audit-object-routing/category-matrix.md: performance / scale | Native route exceeds baseline through measurement-or-static-evidence distinction" /tmp/no-category-strength.out || {
  printf 'audit-object-routing-contract.test: category-strength failure was not the intended contract failure\n' >&2
  cat /tmp/no-category-strength.out >&2
  exit 1
}

# 6. The process-history contract must validate a real enumerated corpus, not
# merely find descriptive prose in a fixture.
bash scripts/check-audit-object-routing-contract.sh \
  --validate-process-history-fixture \
  fixtures/audit-object-routing/process-history-run >/dev/null || {
  printf 'audit-object-routing-contract.test: process-history behavioral fixture expected PASS\n' >&2
  exit 1
}

process_fixture="fixtures/audit-object-routing/process-history-run"
expect_process_history_fail() {
  local label="$1"
  local copy="$2"
  if bash scripts/check-audit-object-routing-contract.sh \
    --validate-process-history-fixture "$copy" >/dev/null 2>&1; then
    printf 'audit-object-routing-contract.test: %s mutation unexpectedly passed\n' "$label" >&2
    exit 1
  fi
}

for mutation in population absent-surface replay-count citation truncated-read carrier-drift single-session compendium-order; do
  copy="$tmp/process-$mutation"
  cp -R "$process_fixture" "$copy"
  case "$mutation" in
    population) sed -i 's/"population_size": 8/"population_size": 9/' "$copy/result.json" ;;
    absent-surface) sed -i 's/"could_not_verify": \["RC-artifacts"\]/"could_not_verify": []/' "$copy/result.json" ;;
    replay-count) sed -i 's/"recurring_shape_count": 3/"recurring_shape_count": 5/' "$copy/result.json" ;;
    citation) sed -i 's/"text": "SYNTHETIC_FAILURE"/"text": "MISSING_WITNESS"/' "$copy/result.json" ;;
    truncated-read) sed -i '0,/"start": 1/s//"start": 2/' "$copy/result.json" ;;
    carrier-drift) sed -i 's/"draft": "R20"/"draft": "R21"/' "$copy/result.json" ;;
    single-session) sed -i 's/"fan_out": false/"fan_out": true/' "$copy/result.json" ;;
    compendium-order) sed -i 's/"compendium_complete_at": "2026-08-02T01:00:00Z"/"compendium_complete_at": "2026-08-02T03:00:00Z"/' "$copy/result.json" ;;
  esac
  expect_process_history_fail "$mutation" "$copy"
done

prewindow_copy="$tmp/process-prewindow-signature"
cp -R "$process_fixture" "$prewindow_copy"
sed -i 's/"message":"pre-window"/"signature":"SYNTHETIC_FAILURE"/' \
  "$prewindow_copy/corpus/old-1.jsonl"
bash scripts/check-audit-object-routing-contract.sh \
  --validate-process-history-fixture "$prewindow_copy" >/dev/null || {
  printf 'audit-object-routing-contract.test: pre-window recurrence polluted the declared window\n' >&2
  exit 1
}

# 7. Retrospective governance reuses the real run-root, closure, and cold-review
# validators. These cases distinguish affordable micro custody from review work
# that must use a full root.
retro="fixtures/audit-object-routing/retrospective"
for case_name in unadjudicated-deferral retired-with-reason uncited-could-not-verify meta-tier-claim; do
  [ -d "$retro/$case_name/root" ] || {
    printf 'audit-object-routing-contract.test: missing retrospective fixture: %s\n' "$case_name" >&2
    exit 1
  }
done
[ -f "$retro/no-run-root/deliverable.md" ] || {
  printf 'audit-object-routing-contract.test: missing no-run-root retrospective fixture\n' >&2
  exit 1
}
if bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$retro/no-run-root/root" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: retrospective without run root unexpectedly passed\n' >&2
  exit 1
fi

bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$retro/unadjudicated-deferral/root" >/dev/null
if bash skills/implementaudit/scripts/check-closure-surface.sh \
  "$retro/unadjudicated-deferral/root/STATE.md" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: unadjudicated retrospective deferral unexpectedly passed\n' >&2
  exit 1
fi

bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$retro/retired-with-reason/root" >/dev/null
bash skills/implementaudit/scripts/check-closure-surface.sh \
  "$retro/retired-with-reason/root/STATE.md" >/dev/null

if bash skills/implementaudit/scripts/check-closure-surface.sh \
  "$retro/uncited-could-not-verify/root/STATE.md" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: unadjudicated could-not-verify unexpectedly passed\n' >&2
  exit 1
fi

if bash scripts/check-cold-review-contract.sh --fixture \
  "$retro/self-reviewed-deliverable.md" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: same-context retrospective review unexpectedly passed\n' >&2
  exit 1
fi

bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  fixtures/run-root/micro-conformant/root >/dev/null
micro_extra="$tmp/micro-extra/root"
mkdir -p "$micro_extra/plans"
cp fixtures/run-root/micro-conformant/root/.claimed \
  fixtures/run-root/micro-conformant/root/STATE.md "$micro_extra/"
printf '# undeclared extra payload\n' > "$micro_extra/plans/retrospective.md"
if bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$micro_extra" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: micro root accepted undeclared extra payload\n' >&2
  exit 1
fi
for allowed_name in .claimed STATE.md deferrals.jsonl; do
  nested_micro="$tmp/micro-nested-$allowed_name/root"
  mkdir -p "$nested_micro/extra"
  cp fixtures/run-root/micro-conformant/root/.claimed \
    fixtures/run-root/micro-conformant/root/STATE.md "$nested_micro/"
  printf 'nested basename must not inherit root allowance\n' \
    > "$nested_micro/extra/$allowed_name"
  if bash skills/implementaudit/scripts/validate-run-root.sh --micro \
    "$nested_micro" >/dev/null 2>&1; then
    printf 'audit-object-routing-contract.test: nested %s bypassed micro payload boundary\n' \
      "$allowed_name" >&2
    exit 1
  fi
done
if bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  fixtures/run-root/micro-with-stage62-disposition/root >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: micro retrospective carried Stage 6.2 review\n' >&2
  exit 1
fi
bash skills/implementaudit/scripts/validate-run-root.sh \
  fixtures/run-root/no-sentinel-legacy/root >/dev/null
bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$retro/read-only-plans-lane/runs/retrospective/root" >/dev/null
[ -f "$retro/read-only-plans-lane/plans/retrospective.md" ] || {
  printf 'audit-object-routing-contract.test: read-only retrospective plan is missing\n' >&2
  exit 1
}

if bash skills/implementaudit/scripts/validate-run-root.sh --micro \
  "$retro/meta-tier-claim/root" >/dev/null 2>&1; then
  printf 'audit-object-routing-contract.test: reduced-obligation meta-tier claim unexpectedly passed\n' >&2
  exit 1
fi
printf 'audit-object-routing-contract.test: ok\n'
