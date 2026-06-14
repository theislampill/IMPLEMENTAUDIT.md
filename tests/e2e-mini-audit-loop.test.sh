#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

phase_fixture="fixtures/e2e-mini-audit-loop/phase-1.md"
[ -f "$phase_fixture" ] || {
  printf 'e2e-mini-audit-loop.test: missing fixture %s\n' "$phase_fixture" >&2
  exit 1
}

bash skills/implementaudit/scripts/validate-phase.sh "$phase_fixture"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/repo/.IMPLEMENTAUDIT/runs/mini/phases"
cp skills/implementaudit/scripts/repo-state.sh "$tmp/repo/.IMPLEMENTAUDIT/runs/mini/repo-state.sh"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/repo/.IMPLEMENTAUDIT/runs/mini/PROTOCOL.md"
cp "$phase_fixture" "$tmp/repo/.IMPLEMENTAUDIT/runs/mini/phases/phase-1.md"

(
  cd "$tmp/repo"
  git init -q
  git config user.email test@example.invalid
  git config user.name 'ImplementAudit E2E'
  printf 'baseline\n' > README.md
  git add README.md
  git commit -qm baseline
  baseline="$(git rev-parse HEAD)"
  printf 'mini proof\n' > src-mini-proof.txt
  bash .IMPLEMENTAUDIT/runs/mini/repo-state.sh deliverable "$baseline" src-mini-proof.txt |
    grep -E 'present - (untracked new file|changed vs baseline)' >/dev/null
)

grep -F "AUDIT_COMPLETE" fixtures/e2e-mini-audit-loop/EXPECTED-TRANSCRIPT.md >/dev/null
grep -F "IMPLEMENTAUDIT_RUN_COMPLETE" fixtures/e2e-mini-audit-loop/EXPECTED-TRANSCRIPT.md >/dev/null

printf 'e2e-mini-audit-loop.test: ok\n'
