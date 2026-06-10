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
  printf 'marker-order.test: expected legacy failure handoff plus completion to fail\n' >&2
  exit 1
fi

cat >"$tmp/andon-and-complete.md" <<'EOF'
ANDON_PROBE
ANDON_HANDOFF
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
EOF

if bash scripts/check-marker-order.sh "$tmp/andon-and-complete.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected Andon handoff plus completion to fail\n' >&2
  exit 1
fi

cat >"$tmp/andon-skip-probe.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
ANDON_HANDOFF
EOF

if bash scripts/check-marker-order.sh "$tmp/andon-skip-probe.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected Andon handoff without probe to fail\n' >&2
  exit 1
fi

cat >"$tmp/andon-wrong-order.md" <<'EOF'
ANDON_ESCALATE
ANDON_PROBE
EOF

if bash scripts/check-marker-order.sh "$tmp/andon-wrong-order.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected escalate-before-probe to fail\n' >&2
  exit 1
fi

cat >"$tmp/andon-escalation-valid.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
ANDON_PROBE
ANDON_ESCALATE
New evidence: rerun output diverges from the criterion's required evidence
ANDON_HANDOFF
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
AUDIT_START
AUDIT_VERIFY
AUDIT_HANDOFF
EOF

bash scripts/check-marker-order.sh "$tmp/andon-escalation-valid.md"

cat >"$tmp/andon-escalate-no-progress.md" <<'EOF'
ANDON_PROBE
ANDON_ESCALATE
retrying the same countermeasure with no new evidence
ANDON_HANDOFF
EOF

if bash scripts/check-marker-order.sh "$tmp/andon-escalate-no-progress.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected escalate without progress fields to fail\n' >&2
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

cat >"$tmp/pause-valid.md" <<'EOF'
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PAUSE
Phase: 1
Status: paused at boundary
EOF

bash scripts/check-marker-order.sh "$tmp/pause-valid.md"

cat >"$tmp/pause-no-start.md" <<'EOF'
IMPLEMENTAUDIT_PAUSE
Phase: 1
EOF

if bash scripts/check-marker-order.sh "$tmp/pause-no-start.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected pause without phase start to fail\n' >&2
  exit 1
fi

cat >"$tmp/gaps-after-complete.md" <<'EOF'
AUDIT_START
AUDIT_VERIFY
AUDIT_COMPLETE
AUDIT_GAPS
EOF

if bash scripts/check-marker-order.sh "$tmp/gaps-after-complete.md" >/dev/null 2>&1; then
  printf 'marker-order.test: expected AUDIT_GAPS after AUDIT_COMPLETE to fail\n' >&2
  exit 1
fi

printf 'marker-order.test: ok\n'
