#!/usr/bin/env bash
set -euo pipefail

# Parameter-bound authorization (#12): PROTOCOL/Nemawashi binding rule +
# the drift/match fixture pair.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
state_template="skills/implementaudit/templates/STATE.md"
scorer="skills/implementaudit/scripts/check-authorization-binding.sh"
fx="fixtures/authorization-binding"
fail() { printf 'authorization-binding-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto" | tr -s ' ')"
state_flat="$(tr '\n' ' ' < "$state_template" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'Parameter-bound authorization' \
  || fail "PROTOCOL missing parameter-bound authorization rule"
printf '%s' "$flat" | grep -qi 'AUTHORITY DRIFT' \
  || fail "authority-drift classification missing"
printf '%s' "$flat" | grep -qi 'defaults are NEVER implicitly adopted' \
  || fail "no-implicit-defaults rule missing"
printf '%s' "$flat" | grep -qi 'materialize every owner grant at intake' \
  || fail "authorization intake materialization rule missing"
printf '%s' "$flat" | grep -qi 'inspect the durable authorization rows before requesting permission' \
  || fail "handoff must consult durable authorization rows"
printf '%s' "$state_flat" | grep -qi 'authorization-record.md' \
  || fail "STATE does not describe the durable grant record carrier"

# Authorization intake (#137): the same checker binds a source grant to
# durable STATE/auth-record carriers before evaluating runtime parameters.
state_deny="$fx/intake-state-deny.md"
state_grant="$fx/intake-state-grant.md"
auth_record="$fx/authorization-record.txt"

# 1. A genuinely ungranted run remains cheap default-deny.
bash "$scorer" --state "$state_deny" >/dev/null 2>&1 \
  || fail "default-deny STATE must pass without a claimed grant"

# 2. A source-bound grant, active STATE row, durable record, and matching
# invocation form one valid discoverable authorization chain.
bash "$scorer" --state "$state_grant" --auth "$auth_record" \
  --invocation "$fx/invocation-match.txt" \
  >/dev/null 2>&1 || fail "durable source-bound grant must pass"

# 3. After a context boundary, STATE alone names both the source reference and
# record path needed to rediscover the grant without conversation memory.
grep -Fq 'owner-message:packet-137' "$state_grant" \
  || fail "STATE does not retain the owner source reference"
grep -Fq 'fixtures/authorization-binding/authorization-record.txt' "$state_grant" \
  || fail "STATE does not retain the durable authorization-record path"

# 4. A durable record transcribed from a packet grant for push conflicts with
# STATE default-deny.
out="$(bash "$scorer" --state "$state_deny" --auth "$auth_record" \
  --invocation "$fx/invocation-match.txt" 2>&1 || true)"
printf '%s' "$out" | grep -q 'AUTHORIZATION INCONSISTENT' \
  || fail "packet grant versus STATE deny was not detected"

# 5. A claimed authorized action without a bound grant source fails closed.
out="$(bash "$scorer" --state "$state_grant" \
  --auth "$fx/authorization-record-missing-source.txt" \
  --invocation "$fx/invocation-match.txt" 2>&1 || true)"
printf '%s' "$out" | grep -qi 'missing grant source' \
  || fail "authorized action without a grant source was not rejected"

# 6. Durable intake does not weaken existing parameter drift enforcement.
out="$(bash "$scorer" --state "$state_grant" --auth "$auth_record" \
  --invocation "$fx/invocation-drift.txt" 2>&1 || true)"
printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
  || fail "source-bound out-of-range invocation did not drift"

# matching parameters -> proceed, no ceremony
bash "$scorer" --auth "$fx/auth.txt" --invocation "$fx/invocation-match.txt" \
  >/dev/null 2>&1 || fail "matching invocation must proceed"

# unbound/out-of-range parameter -> authority drift, stop
out="$(bash "$scorer" --auth "$fx/auth.txt" --invocation "$fx/invocation-drift.txt" 2>&1 || true)"
printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
  || fail "drift invocation did not classify authority drift"
printf '%s' "$out" | grep -qi 'STOP the governed action' \
  || fail "drift did not stop the governed action"
if bash "$scorer" --auth "$fx/auth.txt" --invocation "$fx/invocation-drift.txt" >/dev/null 2>&1; then
  fail "drift invocation must exit nonzero"
fi

# ADVERSARIAL (post-merge robustness): an authorization with NO `binds:`
# line at all, plus an invocation supplying a consequential parameter, must
# EVALUATE to AUTHORITY DRIFT (everything is unbound) — not die early on the
# absent `binds:` lookup under `set -euo pipefail`.
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
printf 'action: commit-only\n' > "$tmp/auth-nobinds.txt"
printf 'param.diff_scope: eval-only\n' > "$tmp/inv-x.txt"
out="$(bash "$scorer" --auth "$tmp/auth-nobinds.txt" --invocation "$tmp/inv-x.txt" 2>&1 || true)"
printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
  || fail "no-binds authorization did not reach the drift evaluation (early-death regression)"
if bash "$scorer" --auth "$tmp/auth-nobinds.txt" --invocation "$tmp/inv-x.txt" >/dev/null 2>&1; then
  fail "no-binds authorization with a consequential param must exit nonzero"
fi

# --- Fable review of PR #32: adversarial regressions -----------------------
# A bound consequential parameter the invocation never supplies is drift:
# the action would run on a default the owner never saw.
printf 'action: x\nbinds: diff_scope,timeout_s\ndiff_scope: eval-only\ntimeout_s: 1..1800\n' > "$tmp/auth-full.txt"
printf 'param.diff_scope: eval-only\n' > "$tmp/inv-missing.txt"
out="$(bash "$scorer" --auth "$tmp/auth-full.txt" --invocation "$tmp/inv-missing.txt" 2>&1 || true)"
printf '%s' "$out" | grep -q 'bound-but-unsupplied' \
  || fail "bound-but-unsupplied parameter did not drift"

# Duplicate keys in the authorization are malformed, never first-wins —
# a permissive spec first must not shadow a stricter one.
printf 'action: x\nbinds: timeout_s\ntimeout_s: 1..1000000\ntimeout_s: 1..10\n' > "$tmp/auth-dup.txt"
printf 'param.timeout_s: 500\n' > "$tmp/inv-500.txt"
out="$(bash "$scorer" --auth "$tmp/auth-dup.txt" --invocation "$tmp/inv-500.txt" 2>&1 || true)"
printf '%s' "$out" | grep -qi 'malformed authorization' \
  || fail "duplicate auth spec keys were not rejected as malformed"

# A drifting parameter on a final line WITHOUT a trailing newline is
# still evaluated, never silently dropped.
printf 'param.diff_scope: eval-only\nparam.timeout_s: 60\nparam.escape_hatch: stop-early' > "$tmp/inv-nonl.txt"
if bash "$scorer" --auth "$tmp/auth-full.txt" --invocation "$tmp/inv-nonl.txt" >/dev/null 2>&1; then
  fail "unterminated final drift line was silently dropped"
fi

# R002E P06/P17 receiving: a declared parameter without an actual owner
# value/range is not an unrestricted grant. Keep absent and empty distinct.
printf 'action: inert-read\nbinds: object\n' > "$tmp/auth-missing-spec.txt"
printf 'action: inert-read\nbinds: object\nobject:   \n' > "$tmp/auth-empty-spec.txt"
printf 'param.object: report-beta\n' > "$tmp/inv-other-object.txt"
for missing_spec in "$tmp/auth-missing-spec.txt" "$tmp/auth-empty-spec.txt"; do
  if bash "$scorer" --auth "$missing_spec" --invocation "$tmp/inv-other-object.txt" >/dev/null 2>&1; then
    fail "declared parameter without a value/range was accepted as unrestricted"
  fi
done

# The supply check must not recognize a differently cased parameter prefix
# that the value-validation loop skips. Reject ambiguous invocation grammar.
printf 'action: inert-read\nbinds: object\nobject: report-alpha\n' > "$tmp/auth-one-object.txt"
printf 'Param.object: report-beta\n' > "$tmp/inv-case-prefix.txt"
if bash "$scorer" --auth "$tmp/auth-one-object.txt" --invocation "$tmp/inv-case-prefix.txt" >/dev/null 2>&1; then
  fail "mixed-case parameter prefix bypassed value validation"
fi

# R002E P06/P17 enum receiving: a runtime scalar must equal one declared
# alternative. Joining adjacent allowed alternatives does not grant that value.
printf 'action: inert-read\nbinds: object\nobject: report-alpha|report-beta\n' > "$tmp/auth-enum.txt"
for allowed_object in report-alpha report-beta; do
  printf 'param.object: %s\n' "$allowed_object" > "$tmp/inv-enum.txt"
  bash "$scorer" --auth "$tmp/auth-enum.txt" --invocation "$tmp/inv-enum.txt" \
    >/dev/null 2>&1 || fail "declared enum member was rejected: $allowed_object"
done
for unbound_object in 'report-alpha|report-beta' report-gamma; do
  printf 'param.object: %s\n' "$unbound_object" > "$tmp/inv-enum.txt"
  if out="$(bash "$scorer" --auth "$tmp/auth-enum.txt" --invocation "$tmp/inv-enum.txt" 2>&1)"; then
    fail "value outside individual enum alternatives was accepted: $unbound_object"
  fi
  printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
    || fail "value outside enum alternatives did not classify authority drift"
done

# R002E P06/P17 range receiving: a range must contain exactly its two
# endpoints. Discarding an interior segment cannot create a broader grant.
while IFS='|' read -r range_spec range_value; do
  printf 'action: inert-parameter-check\nbinds: timeout_s\ntimeout_s: %s\n' "$range_spec" > "$tmp/auth-range.txt"
  printf 'param.timeout_s: %s\n' "$range_value" > "$tmp/inv-range.txt"
  bash "$scorer" --auth "$tmp/auth-range.txt" --invocation "$tmp/inv-range.txt" \
    >/dev/null 2>&1 || fail "valid range member was rejected: $range_value in $range_spec"
done <<'RANGE_POSITIVES'
1..10|1
1..10|7
1..10|10
-10..-1|-10
-10..-1|-7
-10..-1|-1
0..0|0
RANGE_POSITIVES

printf 'param.timeout_s: 7\n' > "$tmp/inv-range.txt"
for malformed_range in '1..not-a-bound..10' '1..5..10' '1....10'; do
  printf 'action: inert-parameter-check\nbinds: timeout_s\ntimeout_s: %s\n' "$malformed_range" > "$tmp/auth-range.txt"
  if out="$(bash "$scorer" --auth "$tmp/auth-range.txt" --invocation "$tmp/inv-range.txt" 2>&1)"; then
    fail "malformed range silently discarded an interior segment: $malformed_range"
  fi
  printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
    || fail "malformed range did not classify authority drift"
done

printf 'action: inert-parameter-check\nbinds: timeout_s\ntimeout_s: 1..10\n' > "$tmp/auth-range.txt"
for outside_value in 0 11; do
  printf 'param.timeout_s: %s\n' "$outside_value" > "$tmp/inv-range.txt"
  if out="$(bash "$scorer" --auth "$tmp/auth-range.txt" --invocation "$tmp/inv-range.txt" 2>&1)"; then
    fail "value outside the range endpoints was accepted: $outside_value"
  fi
  printf '%s' "$out" | grep -q 'AUTHORITY DRIFT' \
    || fail "value outside the range did not classify authority drift"
done

printf 'authorization-binding-contract: ok (intake 6 + match/drift + no-binds + 3 Fable adversarial + 3 R002E receiving + enum membership + exact numeric-range syntax)\n'
