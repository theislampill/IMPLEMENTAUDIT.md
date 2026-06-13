#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d -p "$repo_root" .custody-append-test.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT

helper="skills/scripts/custody-append.sh"

to_windows_url_path() {
  local input="$1"
  local abs="$input"
  local drive rest
  if [ "${abs#/}" = "$abs" ]; then
    abs="$PWD/$abs"
  fi
  case "$abs" in
    /mnt/[A-Za-z]/*)
      drive="${abs:5:1}"
      rest="${abs:7}"
      printf '%s:/%s' "${drive^^}" "$rest"
      ;;
    /[A-Za-z]/*)
      drive="${abs:1:1}"
      rest="${abs:3}"
      printf '%s:/%s' "${drive^^}" "$rest"
      ;;
    *)
      printf '%s' "$input"
      ;;
  esac
}

activegraph_cmd=()
if command -v activegraph >/dev/null 2>&1; then
  activegraph_cmd=(activegraph)
else
  IFS=':' read -r -a path_entries <<< "${PATH:-}"
  for path_entry in "${path_entries[@]}"; do
    for candidate in "$path_entry/activegraph.exe" "$path_entry/Scripts/activegraph.exe"; do
      if [ -x "$candidate" ]; then
        activegraph_cmd=("$candidate")
        break 2
      fi
    done
  done
fi

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
    if [ "${#activegraph_cmd[@]}" -gt 0 ]; then
      store_url_path="$tmp/store.db"
      case "${activegraph_cmd[0]}" in
        *.exe|/mnt/*)
          store_url_path="$(to_windows_url_path "$store_url_path")"
          ;;
      esac
      inspect_out="$("${activegraph_cmd[@]}" inspect "sqlite:///$store_url_path" --run-id test-run --tail 1 2>&1)" || {
        printf 'custody-append.test: activegraph inspect could not read appended run: %s\n' "$inspect_out" >&2
        exit 1
      }
      printf '%s' "$inspect_out" | grep -Fq "run_id:           test-run" || {
        printf 'custody-append.test: inspect output missing run id: %s\n' "$inspect_out" >&2
        exit 1
      }
      printf '%s' "$inspect_out" | grep -Fq "ev-001" || {
        printf 'custody-append.test: inspect output missing event id: %s\n' "$inspect_out" >&2
        exit 1
      }
      trace_out="$tmp/trace.jsonl"
      trace_arg="$trace_out"
      case "${activegraph_cmd[0]}" in
        *.exe|/mnt/*)
          trace_arg="$(to_windows_url_path "$trace_arg")"
          ;;
      esac
      "${activegraph_cmd[@]}" export-trace "sqlite:///$store_url_path" --run-id test-run --format jsonl -o "$trace_arg" >/dev/null
      grep -Fq 'ev-001' "$trace_out" || {
        printf 'custody-append.test: export-trace output missing event id\n' >&2
        exit 1
      }
    fi
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
