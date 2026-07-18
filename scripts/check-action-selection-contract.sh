#!/usr/bin/env bash
set -euo pipefail

# Action-selection contract gate (#48, IA-ACTION-DEPTH). Ordinary task-shaped
# invocations must derive the warranted ydqyq-audit-action set from the seven
# live factors — scope, uncertainty, risk, dependencies, evidence gaps,
# authorization state, intended executor — record selections AND omissions,
# and never gate depth on an activation keyword.
#
# Usage: check-action-selection-contract.sh [--repo-root <dir>]

fail() {
  printf 'check-action-selection-contract: %s\n' "$*" >&2
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

# --- runtime contract: planning-depth.md owns the contract ---
depth_ref="skills/implementaudit/references/planning-depth.md"
for text in \
  "## Action-selection contract" \
  "Depth never requires an activation keyword" \
  "- scope" \
  "- uncertainty" \
  "- risk" \
  "- dependencies" \
  "- evidence gaps" \
  "- authorization state" \
  "- intended executor" \
  "Selection is recorded, both ways" \
  "considered-but-omitted actions with the reason" \
  "why deeper planning was or was not warranted" \
  "Reference loading follows selection" \
  "request size alone never does" \
  "plan-quality defect"
do
  require "$depth_ref" "$text"
done

# --- bootloader: Stage 1 derives and records the action set ---
skill="skills/implementaudit/SKILL.md"
for text in \
  "Derive the warranted \`ydqyq-audit-action\` set from scope, uncertainty, risk," \
  "record" \
  "action-selection contract" \
  "Depth never requires an activation keyword"
do
  require "$skill" "$text"
done

# --- templates: the record has a home in the audit object ---
thinking="skills/implementaudit/templates/THINKING.md"
for text in \
  "## Action selection" \
  "Selected ydqyq-audit-actions:" \
  "Considered-but-omitted actions (with reasons):" \
  "Why deeper planning was or was not warranted:"
do
  require "$thinking" "$text"
done

roadmap="skills/implementaudit/templates/ROADMAP.md"
for text in \
  "## Action selection" \
  "Depth rationale"
do
  require "$roadmap" "$text"
done

# --- positive fixtures ---
deepens="fixtures/audit-action-selection/ordinary-task-deepens.md"
for text in \
  "no activation keyword" \
  "action-selection record" \
  "phase decomposition" \
  "considered-but-omitted actions with reasons"
do
  require "$deepens" "$text"
done

shallow="fixtures/audit-action-selection/narrow-direct-stays-shallow.md"
for text in \
  "stays direct" \
  "why deeper planning was not warranted" \
  "omitted actions with reasons" \
  "Over-planning"
do
  require "$shallow" "$text"
done

# --- adapted route fixtures carry the contract linkage ---
require "fixtures/native-integration/single-plan-native-route.md" \
  "action-selection record notes why phase decomposition beyond the single"
require "fixtures/audit-object-routing/deep-pressure-disclosure.md" \
  "factor-driven action-selection rationale"

# --- negative fixtures exist and declare their failing disposition ---
for negative in \
  "fixtures/audit-action-selection/negative-keyword-gated-depth.md" \
  "fixtures/audit-action-selection/negative-size-only-deepening.md" \
  "fixtures/audit-action-selection/negative-missing-selection-record.md"
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when reviewed: FAIL"
done

# --- no command-mode advertisement in the new surfaces ---
if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap)' \
  fixtures/audit-action-selection "$depth_ref" \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-action-selection-command-mode-hit.txt; then
  cat /tmp/implementaudit-action-selection-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-action-selection-command-mode-hit.txt
  fail "command-mode identity advertised in action-selection surfaces"
fi
rm -f /tmp/implementaudit-action-selection-command-mode-hit.txt

printf 'check-action-selection-contract: ok\n'
