#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'agents-bootstrap-budget.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

bash scripts/check-agents-bootstrap-budget.sh

"${py_cmd[@]}" - "$tmp/too-long.md" <<'PY'
from pathlib import Path
import sys
Path(sys.argv[1]).write_text("\n".join(["# AGENTS.md"] * 451) + "\n", encoding="utf-8")
PY

if bash scripts/check-agents-bootstrap-budget.sh \
  --agents-file "$tmp/too-long.md" \
  >/tmp/agents-budget-too-long.out 2>&1; then
  printf 'agents-bootstrap-budget.test: over-budget fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "line budget exceeded" /tmp/agents-budget-too-long.out >/dev/null || {
  printf 'agents-bootstrap-budget.test: expected line-budget diagnostic\n' >&2
  cat /tmp/agents-budget-too-long.out >&2
  exit 1
}

cat >"$tmp/missing-dogfood-proof.md" <<'BAD'
# AGENTS.md

Concise maintainer bootloader.

## Project Identity
## Canonical Paths
## Authorization Gates
## Source And Package Layout
## Validation Map
## Release And Dogfood Boundaries
## Active Anti-Repeat Rules
## History And Retention

No commit. No push. No tag. No release. No publication. No provenance.
skills/implementaudit/SKILL.md
docs/maintenance/AGENTS-HISTORY.md
docs/audits/RETENTION.md
scripts/check-agents-bootstrap-budget.sh
tests/agents-bootstrap-budget.test.sh
scripts/check-dogfood-bootstrap-contract.sh
scripts/check-validation-registry.sh
scripts/verify-package.sh
LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN
tests/release-asset-install-claude.test.sh
Graphify output is orientation evidence, not proof
ActiveGraph custody is not correctness proof
temporary `CODEX_HOME`
BAD

if bash scripts/check-agents-bootstrap-budget.sh \
  --agents-file "$tmp/missing-dogfood-proof.md" \
  >/tmp/agents-budget-missing.out 2>&1; then
  printf 'agents-bootstrap-budget.test: missing dogfood proof fields unexpectedly passed\n' >&2
  exit 1
fi

grep -F "installed skill path under that temp home" /tmp/agents-budget-missing.out >/dev/null || {
  printf 'agents-bootstrap-budget.test: expected missing dogfood field diagnostic\n' >&2
  cat /tmp/agents-budget-missing.out >&2
  exit 1
}

cat >"$tmp/history-inline.md" <<'BAD'
# AGENTS.md

Concise maintainer bootloader.

## Project Identity
## Canonical Paths
## Authorization Gates
## Source And Package Layout
## Validation Map
## Release And Dogfood Boundaries
## Active Anti-Repeat Rules
## History And Retention

skills/implementaudit/SKILL.md
docs/maintenance/AGENTS-HISTORY.md
docs/audits/RETENTION.md
No commit. No push. No tag. No release. No publication. No provenance.
temporary `CODEX_HOME`
installed skill path under that temp home
installed `SKILL.md` line/byte count
exact command proving Codex used that temp home
Real-home installed skill readback
NON-EVIDENCE
stale-installed-skill /
real-home-contamination
scripts/check-agents-bootstrap-budget.sh
tests/agents-bootstrap-budget.test.sh
scripts/check-dogfood-bootstrap-contract.sh
scripts/check-validation-registry.sh
scripts/verify-package.sh
LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN
tests/release-asset-install-claude.test.sh
Graphify output is orientation evidence, not proof
ActiveGraph custody is not correctness proof

## Release asset gate
BAD

if bash scripts/check-agents-bootstrap-budget.sh \
  --agents-file "$tmp/history-inline.md" \
  >/tmp/agents-budget-history.out 2>&1; then
  printf 'agents-bootstrap-budget.test: inline history fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "historical section belongs" /tmp/agents-budget-history.out >/dev/null || {
  printf 'agents-bootstrap-budget.test: expected historical-section diagnostic\n' >&2
  cat /tmp/agents-budget-history.out >&2
  exit 1
}

printf 'agents-bootstrap-budget.test: ok\n'
