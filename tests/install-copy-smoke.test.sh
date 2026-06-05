#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

dest="$tmp/codex home/skills/implementaudit"
mkdir -p "$dest"
cp -R skills/. "$dest/"

for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/routing.md \
  references/repo-state-comparison.md \
  references/child-agents.md \
  scripts/detect-env.sh \
  scripts/detect-stack.sh \
  scripts/repo-state.sh \
  scripts/summarize-repo.sh \
  scripts/validate-audit-spec.sh \
  scripts/validate-phase.sh \
  templates/ROADMAP.md \
  templates/STATE.md \
  templates/phase-goal.txt \
  templates/child-agent-report.md \
  templates/PROTOCOL.md
do
  [ -f "$dest/$file" ] || {
    printf 'install-copy-smoke.test: missing copied file: %s\n' "$file" >&2
    exit 1
  }
done

bash "$dest/scripts/validate-phase.sh" "$dest/templates/phase-goal.txt"

printf 'install-copy-smoke.test: ok\n'
