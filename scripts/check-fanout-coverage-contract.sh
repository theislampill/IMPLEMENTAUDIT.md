#!/usr/bin/env bash
set -euo pipefail

# Fanout coverage gate (#49, IA-ACTION-FANOUT). Materially broad audits
# trigger actual bounded specialist lanes — parallel when possible,
# serialized when the host cannot run concurrent subagents — with a binding
# per-lane prompt contract and audit-object coverage-lane records. A
# coverage table alone never satisfies a broad-coverage claim, and warranted
# lanes are never silently dropped.
#
# Usage: check-fanout-coverage-contract.sh [--repo-root <dir>]

fail() {
  printf 'check-fanout-coverage-contract: %s\n' "$*" >&2
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

# --- child-agents.md owns the binding lane contract ---
child_ref="skills/implementaudit/references/child-agents.md"
for text in \
  "Specialist fanout is a warranted" \
  "required for those" \
  "serialized as separate bounded written review passes" \
  "never silently erase a warranted lane" \
  "coverage table" \
  "never substitutes for them" \
  "## Coverage-lane records" \
  "status: executed / serialized / skipped with reason" \
  "residual risk when the lane was not executed" \
  "must not imply full coverage" \
  "arbitrary cap" \
  "audit-playbook.md path/headings" \
  "## Finding Row Contract" \
  "recon facts" \
  "risk hints" \
  "findings-only/no-dumps/read-confirmation"
do
  require "$child_ref" "$text"
done

# --- audit-category-matrix.md: fanout is required where coverage demands ---
matrix_ref="skills/implementaudit/references/audit-category-matrix.md"
for text in \
  "category fanout is required where material" \
  "serialized execution of a warranted" \
  "never a license to skip it" \
  "coverage table alone never" \
  "coverage-lane" \
  "residual risk into the final audit" \
  "Deep analysis is a default pressure"
do
  require "$matrix_ref" "$text"
done

# --- THINKING template: the record has a home ---
require "skills/implementaudit/templates/THINKING.md" "Coverage lanes"
require "skills/implementaudit/templates/THINKING.md" "status executed/serialized/skipped+reason"

# --- exemplar prompts carry the per-lane dispatch contract ---
for prompt in \
  "fixtures/child-agents/read-only-contract-auditor.md" \
  "fixtures/child-agents/adversarial-behavioral-auditor.md"
do
  for text in \
    "Per-lane dispatch contract" \
    "audit-playbook.md" \
    "## Finding Row Contract" \
    "recon facts" \
    "risk hints" \
    "findings-only" \
    "no-dumps" \
    "read-confirmation"
  do
    require "$prompt" "$text"
  done
done

# --- positive fixtures ---
broad="fixtures/child-agents/broad-scope-four-lanes.md"
for text in \
  "no activation keyword" \
  "four bounded specialist lanes" \
  "coverage-lane records" \
  "non-authoritative" \
  "zero executed" \
  "one undifferentiated written pass"
do
  require "$broad" "$text"
done

serial="fixtures/child-agents/low-concurrency-serialized-lanes.md"
for text in \
  "cannot run concurrent subagents" \
  "change scheduling, never coverage" \
  "status serialized" \
  "no warranted lane is dropped" \
  "Silently dropping a warranted lane"
do
  require "$serial" "$text"
done

# --- negative fixtures declare their failing disposition ---
for negative in \
  "fixtures/child-agents/negative-coverage-table-only.md" \
  "fixtures/child-agents/negative-silent-lane-drop.md" \
  "fixtures/child-agents/negative-generic-single-pass.md"
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when reviewed: FAIL"
done

# The mechanical child-prompt negative must exist and must NOT contain the
# fanout tokens it claims to lack (a token leak would make it silently pass
# child-prompt validation).
neg_prompt="fixtures/child-agents/negative-child-prompt-missing-fanout-contract.md"
[ -f "$neg_prompt" ] || fail "missing file: $neg_prompt"
for leak in "audit-playbook.md" "Finding Row Contract" "recon facts" \
  "risk hints" "findings-only" "no-dumps" "read-confirmation"
do
  if grep -Fqi -e "$leak" "$neg_prompt"; then
    fail "$neg_prompt leaks fanout token it must lack: $leak"
  fi
done

# --- no command-mode advertisement in the new surfaces ---
if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap)' \
  fixtures/child-agents "$child_ref" \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-fanout-command-mode-hit.txt; then
  cat /tmp/implementaudit-fanout-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-fanout-command-mode-hit.txt
  fail "command-mode identity advertised in fanout surfaces"
fi
rm -f /tmp/implementaudit-fanout-command-mode-hit.txt

printf 'check-fanout-coverage-contract: ok\n'
