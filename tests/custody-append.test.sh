#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper="skills/scripts/custody-append.sh"

# 1. Usage errors exit 2.
if bash "$helper" only two args >/dev/null 2>&1; then
  printf 'custody-append.test: expected usage error for wrong arity\n' >&2
  exit 1
fi

# 2. Invalid payload JSON exits 2 (when python is available).
if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  if bash "$helper" "$tmp/s.db" run-x ev-1 some.event 'not json' >/dev/null 2>&1; then
    printf 'custody-append.test: expected invalid JSON to fail\n' >&2
    exit 1
  fi
fi

# 2b. Custody-mode labeling is enforced at write time (V0260), regardless of
#     whether activegraph is installed.
if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  if bash "$helper" "$tmp/s.db" run-x ev-2 some.event '{"no_mode":true}' >/dev/null 2>&1; then
    printf 'custody-append.test: expected missing custody_mode to fail\n' >&2
    exit 1
  fi
  if bash "$helper" "$tmp/s.db" run-x ev-3 some.event '{"custody_mode":"historical_backfill","source":"x"}' >/dev/null 2>&1; then
    printf 'custody-append.test: expected under-labeled backfill to fail\n' >&2
    exit 1
  fi
fi

# 3. Behavior depends on whether activegraph is importable — both paths are
#    contract-correct, and both must exit 0.
out="$(bash "$helper" "$tmp/store.db" test-run ev-001 smoke.baseline.recorded '{"checks":"demo","custody_mode":"live_test"}')"
case "$out" in
  *"recorded ev-001"*)
    [ -f "$tmp/store.db" ] || {
      printf 'custody-append.test: append reported but store file missing\n' >&2
      exit 1
    }
    # Idempotency guard: duplicate ids must not crash the helper (absent-safe note or error note, exit 0).
    bash "$helper" "$tmp/store.db" test-run ev-001 smoke.baseline.recorded '{"dup":true,"custody_mode":"live_test"}' >/dev/null
    ;;
  *"activegraph absent"*|*"python unavailable"*)
    : # absent-safe fallback path: correct when the sidecar is not installed
    ;;
  *)
    printf 'custody-append.test: unexpected output: %s\n' "$out" >&2
    exit 1
    ;;
esac

printf 'custody-append.test: ok\n'
