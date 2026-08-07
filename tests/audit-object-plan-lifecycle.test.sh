#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-planner-stages.sh

require() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || {
    printf 'audit-object-plan-lifecycle.test: missing in %s: %s\n' "$file" "$text" >&2
    exit 1
  }
}

reference="skills/implementaudit/references/plan-lifecycle.md"
fixture="fixtures/audit-object-routing/plan-lifecycle.md"

for text in \
  "Self-Contained Plan Standard" \
  "Branch And Diff Scoping" \
  "Review-Plan Semantics" \
  "Execute / Dispatch / Review" \
  "Reconciliation Semantics" \
  "Plan Retirement" \
  "SUPERSEDED_BY: <path> — <reason>" \
  "a self-declared bound is an Andon" \
  "No Arbitrary Revision Cap" \
  "Issue Publication Deferred"
do
  require "$reference" "$text"
done

grep -Fq 'RECONCILIATION: STALE|TODO|BLOCKED' "$reference" \
  || { printf 'audit-object-plan-lifecycle.test: plan retirement reconciliation grammar missing\n' >&2; exit 1; }
grep -Fq 'does not create a bound' "$reference" \
  || { printf 'audit-object-plan-lifecycle.test: no-bound negative control missing\n' >&2; exit 1; }

for text in \
  "cold reader" \
  "weak executor" \
  "APPROVE means criteria are met with evidence" \
  "REVISE means a bounded fix is needed" \
  "BLOCK means owner/source" \
  "DONE" \
  "BLOCKED" \
  "IN PROGRESS" \
  "TODO" \
  "STALE" \
  "DRIFTED" \
  "FIXED INDEPENDENTLY"
do
  require "$fixture" "$text"
done

for text in \
  "Audit category matrix" \
  "Branch / diff / reconciliation scope" \
  "Plan lifecycle" \
  "Issue publication status: deferred"
do
  require "skills/implementaudit/templates/THINKING.md" "$text"
done

for text in \
  "Audit categories:" \
  "Branch/diff scope:" \
  "Plan lifecycle:" \
  "Reconciliation:" \
  "Authorization boundary:"
do
  require "skills/implementaudit/templates/phase-goal.txt" "$text"
done

printf 'audit-object-plan-lifecycle.test: ok\n'
