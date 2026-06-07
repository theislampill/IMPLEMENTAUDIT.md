#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || {
    printf 'continuity.test: missing in %s: %s\n' "$file" "$text" >&2
    exit 1
  }
}

require skills/SKILL.md "bounded continuity"
require skills/SKILL.md "CONTINUITY_DECISION"
require skills/SKILL.md "memory/continuity"
require skills/templates/STATE.md "Continuity decision"
require skills/templates/PROTOCOL.md "CONTINUITY_DECISION"
require skills/templates/THINKING.md "Applied context"
require AGENTS.md "bounded continuity"

if grep -R "MEMORY_SAVED" -n skills README.md AGENTS.md >/dev/null; then
  printf 'continuity.test: external memory marker leaked into native surfaces\n' >&2
  exit 1
fi

printf 'continuity.test: ok\n'
