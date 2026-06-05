#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cat >"$tmp/valid.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
AUDIT_START
AUDIT_VERIFY
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
EOF

bash scripts/check-marker-order.sh "$tmp/valid.md"

cat >"$tmp/wrong-final-order.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
AUDIT_START
IMPLEMENTAUDIT_RUN_COMPLETE
AUDIT_COMPLETE
EOF

if bash scripts/check-marker-order.sh "$tmp/wrong-final-order.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected wrong final order to fail\n' >&2
  exit 1
fi

cat >"$tmp/handoff-and-complete.md" <<'EOF'
AUDIT_START
AUDIT_VERIFY
AUDIT_HANDOFF
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
EOF

if bash scripts/check-marker-order.sh "$tmp/handoff-and-complete.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected handoff plus completion to fail\n' >&2
  exit 1
fi

cat >"$tmp/failure-and-complete.md" <<'EOF'
FAILURE_HANDOFF
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
EOF

if bash scripts/check-marker-order.sh "$tmp/failure-and-complete.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected failure handoff plus completion to fail\n' >&2
  exit 1
fi

cat >"$tmp/wrong-phase-order.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_DONE
AGENTS_UPDATE_DECISION
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
EOF

if bash scripts/check-marker-order.sh "$tmp/wrong-phase-order.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected wrong phase order to fail\n' >&2
  exit 1
fi

printf 'marker-order.test: ok\n'
