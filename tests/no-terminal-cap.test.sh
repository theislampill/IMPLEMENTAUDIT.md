#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. A source-backed proper noun containing "strike" is not a strike-counter
#    contract and must remain valid public documentation.
mkdir -p "$tmp/good-proper-noun/docs/portal/pages"
cat >"$tmp/good-proper-noun/docs/portal/pages/reliability.html" <<'EOF'
The CrowdStrike post-incident report documents a correlated update failure.
A lightning strike can interrupt service; recovery follows observed evidence.
A single strike damaged the unprotected sensor.
The first strike damaged the transformer; the second hit an isolated feeder.
Strike the stale observation from the record only after independent readback.
Hansei may follow any strike, regression, or evidence mismatch.
EOF
bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/good-proper-noun"

# 1b. A cap noun must not match the prefix of capability or another word.
#     This includes the native reader's real custody-refusal diagnostic.
mkdir -p "$tmp/good-capability/skills/implementaudit/scripts"
cat >"$tmp/good-capability/skills/implementaudit/scripts/reader.py" <<'EOF'
raise Refusal('attempt capability descriptor shape/custody differs')
Attempt capabilities describe available operations.
Retry capability and retry capabilities remain available.
Try capability and try capabilities as ordinary vocabulary.
attempt_capability retry-capabilities try_capabilities
The attempt capsule contains the retry capstone.
EOF
bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/good-capability"

# A byte-pinned external host schema is observation data, not our retry policy.
# The exemption must fail on any changed fixture or the same words in policy.
vendor='fixtures/codex-recovery/native-code-mode/ServerNotification.json'
mkdir -p "$tmp/vendor-good/$(dirname "$vendor")"
cp "$vendor" "$tmp/vendor-good/$vendor"
bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/vendor-good"
cp -r "$tmp/vendor-good" "$tmp/vendor-changed"
printf '\n' >> "$tmp/vendor-changed/$vendor"
if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/vendor-changed" >"$tmp/vendor-result" 2>&1; then
  printf 'no-terminal-cap.test: changed vendor identity bypassed guard\n' >&2; exit 1
fi
grep -Fq 'disallowed public-claim terminal-cap wording:' "$tmp/vendor-result"
mkdir -p "$tmp/vendor-wording/skills/implementaudit/references"
printf '%s\n' 'Reached the retry limit for responses.' > "$tmp/vendor-wording/skills/implementaudit/references/policy.md"
if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/vendor-wording" >"$tmp/vendor-result" 2>&1; then
  printf 'no-terminal-cap.test: vendor wording waived active policy\n' >&2; exit 1
fi
grep -Fq 'disallowed public-claim terminal-cap wording:' "$tmp/vendor-result"

# 2. The live repo must pass the gate.
bash scripts/check-no-terminal-cap.sh

# 3. Terminal-cap wording in a shipped runtime doc must fail.
mkdir -p "$tmp/bad-strike/skills/implementaudit/references"
cat >"$tmp/bad-strike/skills/implementaudit/references/transcript-contract.md" <<'EOF'
The three-strike sequence stops the run on Strike 3.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-strike" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected strike wording to fail\n' >&2
  exit 1
fi

# 3. Capped audit-round wording must fail.
mkdir -p "$tmp/bad-rounds/skills/implementaudit/templates"
cat >"$tmp/bad-rounds/skills/implementaudit/templates/PROTOCOL.md" <<'EOF'
The final audit may run up to 3 rounds.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-rounds" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected round-cap wording to fail\n' >&2
  exit 1
fi

# 3b. Counted/capped strike semantics must fail without banning ordinary uses.
strike_case=0
while IFS= read -r wording; do
  strike_case=$((strike_case + 1))
  dir="$tmp/bad-counted-strike-$strike_case"
  mkdir -p "$dir/skills/implementaudit/templates"
  printf '%s\n' "$wording" >"$dir/skills/implementaudit/templates/PROTOCOL.md"
  if bash scripts/check-no-terminal-cap.sh --scan-root "$dir" >/dev/null 2>&1; then
    printf 'no-terminal-cap.test: expected counted strike wording to fail: %s\n' "$wording" >&2
    exit 1
  fi
done <<'EOF'
The double-strike policy stops work.
The triple-strike rule hands off the run.
The quad-strike attack count terminates the run.
An N-strike attack count blocks closure.
A strike counter terminates at its limit.
The strike count is capped at four.
The strike limit hands off the run.
After 4 strikes, stop and hand off.
After three strikes, stop and hand off.
Strike 3 stops the run.
EOF

# 3c. Counted/capped retry semantics must fail without banning ordinary retry prose.
retry_case=0
while IFS= read -r wording; do
  retry_case=$((retry_case + 1))
  dir="$tmp/bad-counted-retry-$retry_case"
  mkdir -p "$dir/skills/implementaudit/templates"
  printf '%s\n' "$wording" >"$dir/skills/implementaudit/templates/PROTOCOL.md"
  if bash scripts/check-no-terminal-cap.sh --scan-root "$dir" >/dev/null 2>&1; then
    printf 'no-terminal-cap.test: expected counted retry wording to fail: %s\n' "$wording" >&2
    exit 1
  fi
done <<'EOF'
After 3 retries, stop the run.
After three retries, hand off the run.
EOF

# Ordinary retry guidance remains valid when it does not impose a finite
# terminal stop or handoff policy.
mkdir -p "$tmp/good-retry/skills/implementaudit/templates"
cat >"$tmp/good-retry/skills/implementaudit/templates/PROTOCOL.md" <<'EOF'
Retry after a transient evidence mismatch and continue until the evidence resolves.
Repeated retries remain available while the currentness check is inconclusive.
EOF
bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/good-retry"

# 4. Run-stopping wording and legacy marker spellings must fail.
mkdir -p "$tmp/bad-legacy/skills/implementaudit/references"
cat >"$tmp/bad-legacy/skills/implementaudit/references/transcript-contract.md" <<'EOF'
FAILURE_HANDOFF: run stops. No subsequent phases execute.
EOF

if bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/bad-legacy" >/dev/null 2>&1; then
  printf 'no-terminal-cap.test: expected legacy marker wording to fail\n' >&2
  exit 1
fi

# 5. Cap synonyms must fail when they teach runtime behavior.
for term in "max retries" "retry limit" "revision limit" "round limit" "capped rounds" "attempt cap" "max-2 revision" "max-3 audit"; do
  dir="$tmp/bad-synonym-${term// /-}"
  mkdir -p "$dir/skills/implementaudit/references"
  printf 'Escalate after the %s is reached.\n' "$term" >"$dir/skills/implementaudit/references/transcript-contract.md"
  if bash scripts/check-no-terminal-cap.sh --scan-root "$dir" >/dev/null 2>&1; then
    printf 'no-terminal-cap.test: expected synonym wording to fail: %s\n' "$term" >&2
    exit 1
  fi
done

# 5b. Cap nouns stay forbidden in singular/plural and delimited forms.
#     A checker crash is not evidence that forbidden wording was detected.
cap_case=0
while IFS= read -r wording; do
  cap_case=$((cap_case + 1))
  dir="$tmp/bad-cap-boundary-$cap_case"
  mkdir -p "$dir/skills/implementaudit/references"
  printf '%s\n' "$wording" >"$dir/skills/implementaudit/references/policy.md"
  cap_status=0
  bash scripts/check-no-terminal-cap.sh --scan-root "$dir" >"$tmp/cap-output" 2>&1 || cap_status=$?
  if [ "$cap_status" -ne 1 ] || ! grep -Fq 'disallowed public-claim terminal-cap wording:' "$tmp/cap-output"; then
    printf 'no-terminal-cap.test: expected cap wording refusal: %s\n' "$wording" >&2
    cat "$tmp/cap-output" >&2
    exit 1
  fi
done <<'EOF'
attempt cap
attempt caps
retry cap
retry caps
try cap
try caps
Stop at the ATTEMPT CAPS.
Enforce the `attempt cap`.
Stop at the attempt cap.
Stop at the attempt caps.
Stop at the retry cap.
Stop at the retry caps.
Stop at the try cap.
Stop at the try caps.
Enforce policy_attempt cap_limit.
Enforce policy_attempt caps_limit.
Enforce policy_retry cap_limit.
Enforce policy_retry caps_limit.
Enforce policy_try cap_limit.
Enforce policy_try caps_limit.
Enforce (attempt cap), then hand off.
EOF

# 6. Explicit denials of caps must remain valid runtime wording.
mkdir -p "$tmp/good-denial/skills/implementaudit/templates"
cat >"$tmp/good-denial/skills/implementaudit/templates/PROTOCOL.md" <<'EOF'
There is no arbitrary retry cap, revision limit, round limit, or attempt cap.
Do not use a first/second/third failure ladder.
EOF
bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/good-denial"

# 7. Legacy history surfaces are exempt: the same wording outside the scanned
#    runtime surfaces must pass.
mkdir -p "$tmp/exempt/docs/audits" "$tmp/exempt/skills/implementaudit"
cat >"$tmp/exempt/docs/audits/old-ledger.md" <<'EOF'
v0.2.6.0 added exact 3-strike failure recovery (FAILURE_PROBE).
EOF
cat >"$tmp/exempt/CHANGELOG.md" <<'EOF'
- Added exact 3-strike failure recovery with FAILURE_HANDOFF.
EOF
cat >"$tmp/exempt/skills/implementaudit/SKILL.md" <<'EOF'
Andon escalation uses ANDON_PROBE, ANDON_ESCALATE, ANDON_HANDOFF.
EOF

bash scripts/check-no-terminal-cap.sh --scan-root "$tmp/exempt"

printf 'no-terminal-cap.test: ok\n'
