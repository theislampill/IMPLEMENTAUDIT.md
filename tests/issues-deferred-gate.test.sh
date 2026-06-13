#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || {
    printf 'issues-deferred-gate.test: missing in %s: %s\n' "$file" "$text" >&2
    exit 1
  }
}

for file in \
  "skills/references/plan-lifecycle.md" \
  "skills/templates/PROTOCOL.md" \
  "skills/templates/phase-goal.txt" \
  "fixtures/audit-object-routing/issues-deferred.md"
do
  require "$file" "deferred"
done

require "skills/references/plan-lifecycle.md" "must not create GitHub issues"
require "skills/references/plan-lifecycle.md" "future publication gate"
require "fixtures/audit-object-routing/issues-deferred.md" "Forbidden: create GitHub issues"
require "fixtures/audit-object-routing/issues-deferred.md" "explicit authorization"
require "fixtures/audit-object-routing/issues-deferred.md" "readback evidence"

if grep -R -n -i -E 'gh issue create|github issue create|create GitHub issues' \
  skills README.md docs/portal fixtures/audit-object-routing \
  | grep -vi "must not" \
  | grep -vi "forbidden" \
  | grep -vi "future gate" \
  >/tmp/implementaudit-issue-publication-hit.txt; then
  cat /tmp/implementaudit-issue-publication-hit.txt >&2
  rm -f /tmp/implementaudit-issue-publication-hit.txt
  printf 'issues-deferred-gate.test: issue publication appears enabled\n' >&2
  exit 1
fi
rm -f /tmp/implementaudit-issue-publication-hit.txt

printf 'issues-deferred-gate.test: ok\n'
