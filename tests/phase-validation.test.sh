#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash skills/scripts/validate-phase.sh skills/templates/phase-goal.txt

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bad="$tmp/placeholder-phase.md"
cat >"$bad" <<'BAD'
IMPLEMENTAUDIT_PHASE_START
Owner/source:
Acceptance criteria:
-
Smoke A:
Smoke B:
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
BAD

if bash skills/scripts/validate-phase.sh "$bad" >/dev/null 2>&1; then
  printf 'phase-validation.test: placeholder-only criteria unexpectedly passed\n' >&2
  exit 1
fi

printf 'phase-validation.test: ok\n'
