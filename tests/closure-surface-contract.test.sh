#!/usr/bin/env bash
set -euo pipefail

# Final-audit success-surface indexing (#14): the PROTOCOL clause + scorer
# fixtures. A closure claim closes only with evidence from the surface that
# establishes it; lower-layer evidence is never promoted.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-closure-surface.sh"
fx="fixtures/closure-surface"
fail() { printf 'closure-surface-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto" | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'Closure-claims table' \
  || fail "PROTOCOL missing closure-claims table"
printf '%s' "$flat" | grep -qi 'never promoted into a higher-surface claim' \
  || fail "layer-promotion prohibition missing"
printf '%s' "$flat" | grep -qi 'NEVER trigger an unauthorized network or deployment check' \
  || fail "unauthorized-inspection prohibition missing"
printf '%s' "$flat" | grep -qi 'closure gate .*not defect prevention' \
  || fail "honest-framing (closure gate not prevention) missing"

pass_case() { bash "$scorer" "$fx/$1" >/dev/null 2>&1 || fail "$1 expected PASS"; }
fail_case() { if bash "$scorer" "$fx/$1" >/dev/null 2>&1; then fail "$1 expected FAIL"; fi; }

fail_case layer-promotion-FAIL.md
fail_case verified-no-evidence-FAIL.md
pass_case uninspectable-unverified-PASS.md
pass_case source-only-PASS.md
pass_case installed-verified-PASS.md

# --- Fable review of PR #31: adversarial regressions -----------------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# Duplicate Claim-ID with conflicting surfaces is ambiguous, never valid.
printf '%s\n%s\n' \
  'claim: X | surface: source | property: structural | status: verified | evidence-surface: source' \
  'claim: X | surface: deployed-service | property: behavioral | status: unverified | residual: r1' \
  > "$tmp/dup.md"
if bash "$scorer" "$tmp/dup.md" >/dev/null 2>&1; then
  fail "duplicate Claim-ID accepted"
fi

# A near-miss row (capitalized key) must fail loudly, never be silently
# skipped — otherwise a layer-promotion row hides by casing its key.
printf '%s\n%s\n' \
  'claim: ok | surface: source | property: structural | status: verified | evidence-surface: source' \
  'Claim: bad | surface: deployed-service | property: behavioral | status: verified | evidence-surface: source' \
  > "$tmp/caps.md"
if bash "$scorer" "$tmp/caps.md" >/dev/null 2>&1; then
  fail "capitalized near-miss claim row silently skipped"
fi

# Control: two DISTINCT claims at different surfaces remain valid.
printf '%s\n%s\n' \
  'claim: a | surface: source | property: structural | status: verified | evidence-surface: source' \
  'claim: b | surface: deployed-service | property: behavioral | status: unverified | residual: r2' \
  > "$tmp/two.md"
bash "$scorer" "$tmp/two.md" >/dev/null 2>&1 \
  || fail "two distinct claims at different surfaces must pass"

printf 'closure-surface-contract: ok (contract + 2 fail + 3 pass fixtures + 3 adversarial)\n'
