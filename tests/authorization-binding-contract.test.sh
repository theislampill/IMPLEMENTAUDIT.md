#!/usr/bin/env bash
set -euo pipefail

# Parameter-bound authorization (#12): PROTOCOL/Nemawashi binding rule +
# the drift/match fixture pair.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-authorization-binding.sh"
fx="fixtures/authorization-binding"
fail() { printf 'authorization-binding-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'Parameter-bound authorization' \
  || fail "PROTOCOL missing parameter-bound authorization rule"
printf '%s' "$flat" | grep -qi 'AUTHORITY DRIFT' \
  || fail "authority-drift classification missing"
printf '%s' "$flat" | grep -qi 'defaults are NEVER implicitly adopted' \
  || fail "no-implicit-defaults rule missing"

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

printf 'authorization-binding-contract: ok (contract + match/drift + no-binds + 3 Fable adversarial)\n'
