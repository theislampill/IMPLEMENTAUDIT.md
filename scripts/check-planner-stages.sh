#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-planner-stages: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require_in_file() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || fail "missing in $file: $text"
}

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_file skills/SKILL.md
require_file skills/templates/THINKING.md
require_file skills/templates/ROADMAP.md
require_file skills/templates/STATE.md
require_file skills/templates/PROTOCOL.md
require_file skills/templates/phase-goal.txt
require_file skills/references/planning-depth.md
require_file skills/references/goal-format.md
require_file skills/references/phase-design.md
require_file skills/references/transcript-contract.md

require_in_file skills/SKILL.md "## 2b. Planner stages for goal synthesis and phased audit closure"
require_in_file skills/SKILL.md "Stage 0 - Context/tool/repo-state detection"
require_in_file skills/SKILL.md "Stage 1 - Audit-governed intake and routing"
require_in_file skills/SKILL.md "Stage 2 - Recon / Gemba"
require_in_file skills/SKILL.md "Stage 3 - Deep think / risk and dependency analysis"
require_in_file skills/SKILL.md "Stage 4 - Phase decomposition"
require_in_file skills/SKILL.md 'Stage 5 - Write `.IMPLEMENTAUDIT` runtime artifacts'
require_in_file skills/SKILL.md "Stage 6 - Plan review and self-critique"
require_in_file skills/SKILL.md "Stage 6.5 - Pre-flight smoke"
require_in_file skills/SKILL.md 'Stage 7 - One ready-to-paste `/goal` handoff when not already embedded'
require_in_file skills/SKILL.md ".IMPLEMENTAUDIT/THINKING.md"
require_in_file skills/SKILL.md 'do not print a second `/goal`'
require_in_file skills/SKILL.md "Self-critique:"
require_in_file skills/SKILL.md "PREFLIGHT_GREEN"
require_in_file skills/SKILL.md "PREFLIGHT_RED"
require_in_file skills/SKILL.md "AUDIT_COMPLETE"
require_in_file skills/SKILL.md "IMPLEMENTAUDIT_RUN_COMPLETE"

require_in_file skills/templates/THINKING.md 'Runtime copy target: `.IMPLEMENTAUDIT/THINKING.md`'
require_in_file skills/templates/THINKING.md "Top objective"
require_in_file skills/templates/THINKING.md "Owner/source"
require_in_file skills/templates/THINKING.md "Top closure risks"
require_in_file skills/templates/THINKING.md "Rollback or removal path"
require_in_file skills/templates/THINKING.md "Evidence strategy"
require_in_file skills/templates/THINKING.md "Graphify status"
require_in_file skills/templates/THINKING.md "ActiveGraph status"

require_in_file skills/templates/PROTOCOL.md ".IMPLEMENTAUDIT/THINKING.md"
require_in_file skills/templates/ROADMAP.md 'Thinking file: `.IMPLEMENTAUDIT/THINKING.md`'
require_in_file skills/templates/STATE.md '| `.IMPLEMENTAUDIT/THINKING.md` |'
require_in_file skills/templates/phase-goal.txt "Thinking ref: .IMPLEMENTAUDIT/THINKING.md"
require_in_file skills/references/goal-format.md "Full phased handoff condition"
require_in_file skills/references/planning-depth.md "Native planner stage rule"
require_in_file skills/references/phase-design.md "Stage 6 self-critique"
require_in_file skills/references/transcript-contract.md "Stage handoff boundary"

require_in_file skills/SKILL.md "audit object / audit record / audit surface"
require_in_file skills/SKILL.md "auditing action / audit operation"
require_in_file skills/SKILL.md "tdqyq-audit-object"
require_in_file skills/SKILL.md "ydqyq-audit-action"
require_in_file skills/SKILL.md "Audit-governed implementation"
require_in_file skills/SKILL.md "Direct governance binds"
require_in_file skills/SKILL.md "Embedded governance inherits"
require_in_file skills/SKILL.md "Goal synthesis constructs"
require_in_file skills/SKILL.md "Double-audit pattern for high-risk runs"
require_in_file skills/SKILL.md 'Final `ydqyq-audit-action` -> terminal'
require_in_file skills/references/transcript-contract.md "audit object lifecycle"
require_in_file skills/references/transcript-contract.md "double-audit sequence"
require_in_file skills/references/goal-format.md "audit object"
require_in_file skills/references/goal-format.md "double-audit pattern"
require_in_file skills/references/planning-depth.md "audit object"
require_in_file skills/references/planning-depth.md "double-audit pattern"
require_in_file skills/references/phase-design.md "audit object"
require_in_file skills/references/phase-design.md "terminal verified closure"
require_in_file skills/templates/PROTOCOL.md "audit object"
require_in_file skills/templates/PROTOCOL.md "double-audit pattern"
require_in_file skills/templates/ROADMAP.md "Audit object"
require_in_file skills/templates/ROADMAP.md "tdqyq-audit-object"
require_in_file skills/templates/ROADMAP.md "Double-audit sequence"
require_in_file skills/templates/STATE.md "Audit object state"
require_in_file skills/templates/STATE.md "ydqyq-audit-action"
require_in_file skills/templates/STATE.md "Implementation action against object"
require_in_file skills/templates/THINKING.md "Audit object"
require_in_file skills/templates/THINKING.md "tdqyq-audit-object"
require_in_file skills/templates/THINKING.md "Double-audit sequence"
require_in_file skills/templates/phase-goal.txt "Audit object"
require_in_file skills/templates/phase-goal.txt "ydqyq-audit-action"
require_in_file skills/templates/phase-goal.txt "Terminal object state to prove"
require_in_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md "Audit object:"
require_in_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md "Auditing actions:"
require_in_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md "tdqyq-audit-object"
require_in_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md "ydqyq-audit-action"
require_in_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md "Double-audit sequence:"

if [ -n "${IMPLEMENTAUDIT_FORBIDDEN_TERMS:-}" ] || [ -n "${IMPLEMENTAUDIT_FORBIDDEN_TERMS_FILE:-}" ]; then
  bash scripts/check-forbidden-terms.sh --root .
fi

printf 'check-planner-stages: ok\n'
