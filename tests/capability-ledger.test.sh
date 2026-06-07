#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || {
    printf 'capability-ledger.test: missing in %s: %s\n' "$file" "$text" >&2
    exit 1
  }
}

require skills/SKILL.md "Capability Ledger"
require skills/SKILL.md "derived from recorded gate passages"
require skills/SKILL.md "Do not claim general competence from one run."
require skills/templates/PROTOCOL.md "Capability Ledger entries"
require skills/templates/STATE.md "Capability Ledger"
require README.md "Capability Ledger"
require docs/audits/v0.2.4.5-graphify-activegraph-honesty.md "Capability Ledger"

if grep -R "broad competence" -n skills README.md AGENTS.md | grep -iv "do not\|no \|not " >/dev/null; then
  printf 'capability-ledger.test: broad competence claim appears endorsed\n' >&2
  exit 1
fi

printf 'capability-ledger.test: ok\n'
