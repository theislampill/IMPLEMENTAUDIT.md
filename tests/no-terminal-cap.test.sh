#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The live repo must pass the gate.
bash scripts/check-no-terminal-cap.sh

# 2. Terminal-cap wording in a shipped runtime doc must fail.
mkdir -p "$tmp/bad-strike/skills/references"
cat >"$tmp/bad-strike/skills/references/transcript-contract.md" <<'EOF'
The three-strike sequence stops the run on Strike 3.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-strike" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected strike wording to fail\n' >&2
  exit 1
fi

# 3. Capped audit-round wording must fail.
mkdir -p "$tmp/bad-rounds/skills/templates"
cat >"$tmp/bad-rounds/skills/templates/PROTOCOL.md" <<'EOF'
The final audit may run up to 3 rounds.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-rounds" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected round-cap wording to fail\n' >&2
  exit 1
fi

# 3b. Bare strike-counter wording (no number attached) must fail.
mkdir -p "$tmp/bad-bare-strike/skills/templates"
cat >"$tmp/bad-bare-strike/skills/templates/PROTOCOL.md" <<'EOF'
Hansei is required after any strike or substitution.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-bare-strike" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected bare strike wording to fail\n' >&2
  exit 1
fi

# 4. Run-stopping wording and legacy marker spellings must fail.
mkdir -p "$tmp/bad-legacy/skills/references"
cat >"$tmp/bad-legacy/skills/references/transcript-contract.md" <<'EOF'
FAILURE_HANDOFF: run stops. No subsequent phases execute.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-legacy" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected legacy marker wording to fail\n' >&2
  exit 1
fi

# 5. Legacy history surfaces are exempt: the same wording outside the scanned
#    runtime surfaces must pass.
mkdir -p "$tmp/exempt/docs/audits" "$tmp/exempt/skills"
cat >"$tmp/exempt/docs/audits/old-ledger.md" <<'EOF'
v0.2.6.0 added exact 3-strike failure recovery (FAILURE_PROBE).
EOF
cat >"$tmp/exempt/CHANGELOG.md" <<'EOF'
- Added exact 3-strike failure recovery with FAILURE_HANDOFF.
EOF
cat >"$tmp/exempt/skills/SKILL.md" <<'EOF'
Andon escalation uses ANDON_PROBE, ANDON_ESCALATE, ANDON_HANDOFF.
EOF

bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/exempt"

printf 'no-terminal-cap.test: ok\n'
