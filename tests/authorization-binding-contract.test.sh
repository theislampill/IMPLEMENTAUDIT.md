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

printf 'authorization-binding-contract: ok (contract + match/drift fixtures)\n'
