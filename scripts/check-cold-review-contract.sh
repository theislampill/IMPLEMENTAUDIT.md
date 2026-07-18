#!/usr/bin/env bash
set -euo pipefail

# Independent cold-review gate (#51, IA-ACTION-COLD-REVIEW). Every handoff
# or executor-ready phase artifact passes an independent cold review —
# fresh-context reviewer, separate child agent preferred, bounded serial
# fresh-context fallback — recording PASS / GAP-REVISE / BLOCKED /
# OWNER DECISION before preflight, dispatch, or handoff; the roadmap/index
# stays a derivative projection of the audit object.
#
# Usage: check-cold-review-contract.sh [--repo-root <dir>]

fail() {
  printf 'check-cold-review-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -ge 2 ] || fail "--repo-root requires a directory argument"
  repo_root="$2"
fi
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  [ -f "$file" ] || fail "missing file: $file"
  grep -Fqi -e "$text" "$file" || fail "missing in $file: $text"
}

# --- SKILL.md stage map carries the gate ---
skill="skills/implementaudit/SKILL.md"
for text in \
  "Stage 6.2 - Independent cold review" \
  "does not reuse the authoring context" \
  "separate child agent where the host supports subagents" \
  "bounded" \
  "serial fresh-context pass" \
  "PASS / GAP-REVISE / BLOCKED / OWNER DECISION" \
  "No handoff, preflight, or dispatch proceeds without a disposition" \
  "Self-critique is" \
  "preserved, not replaced"
do
  require "$skill" "$text"
done

# Stage 6 self-critique must remain intact (preserved, not replaced).
require "$skill" "Stage 6 - Plan review and self-critique"
require "$skill" "Stage 6.5 - Pre-flight smoke"

# --- planning-depth stage list includes the new stage ---
require "skills/implementaudit/references/planning-depth.md" \
  "Stage 6.2 - Independent cold review"

# --- plan-lifecycle owns the disposition and independence contract ---
plan_ref="skills/implementaudit/references/plan-lifecycle.md"
for text in \
  "Self-critique and independent cold review are distinct gates" \
  "does not reuse" \
  "fresh-context reviewer subagent" \
  "bounded serial fresh-context pass" \
  "GAP-REVISE" \
  "OWNER DECISION" \
  "without a recorded disposition" \
  "authoring action" \
  "does not satisfy the gate" \
  "never requires a" \
  "no arbitrary revision caps"
do
  require "$plan_ref" "$text"
done

# --- child-agents carries the reviewer lane ---
child_ref="skills/implementaudit/references/child-agents.md"
for text in \
  "## Independent cold-review lane" \
  "deliberately excludes the authoring session" \
  "cold reader and weak executor" \
  "PASS / GAP-REVISE / BLOCKED /" \
  "non-authoritative"
do
  require "$child_ref" "$text"
done

# --- templates: projection and record home ---
roadmap="skills/implementaudit/templates/ROADMAP.md"
for text in \
  "| Review | Status |" \
  "independent cold-review disposition" \
  "## Execution index (projection)" \
  "derivative, never canonical" \
  "corrected to match them"
do
  require "$roadmap" "$text"
done

require "skills/implementaudit/templates/THINKING.md" \
  "Independent cold-review disposition (PASS / GAP-REVISE / BLOCKED / OWNER DECISION)"

# --- adapted routing fixture carries the semantics ---
require "fixtures/audit-object-routing/plan-lifecycle.md" "independent cold review"
require "fixtures/audit-object-routing/plan-lifecycle.md" "derivative of the audit"

# --- positive fixtures ---
pos="fixtures/cold-review/independent-review-confirms-handoff.md"
for text in \
  "no \"review\" keyword anywhere" \
  "separate" \
  "fresh-context child agent" \
  "disposition PASS" \
  "before preflight" \
  "distinct gates"
do
  require "$pos" "$text"
done

proj="fixtures/cold-review/projection-index-derivative.md"
for text in \
  "derivative, never canonical" \
  "phase specs govern" \
  "status theater"
do
  require "$proj" "$text"
done

# --- negative fixtures declare their failing disposition ---
for negative in \
  "fixtures/cold-review/negative-self-critique-only-preflight.md" \
  "fixtures/cold-review/negative-same-context-review.md" \
  "fixtures/cold-review/negative-projection-contradicts-object.md" \
  "fixtures/cold-review/negative-review-keyword-gate.md"
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when reviewed: FAIL"
done

# --- no command-mode advertisement (including review-plan) in new surfaces ---
if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap|review-plan|review)\b' \
  fixtures/cold-review "$plan_ref" "$child_ref" \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-cold-review-command-mode-hit.txt; then
  cat /tmp/implementaudit-cold-review-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-cold-review-command-mode-hit.txt
  fail "command-mode identity advertised in cold-review surfaces"
fi
rm -f /tmp/implementaudit-cold-review-command-mode-hit.txt

printf 'check-cold-review-contract: ok\n'
