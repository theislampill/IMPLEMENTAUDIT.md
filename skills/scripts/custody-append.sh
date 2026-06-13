#!/usr/bin/env bash
# custody-append.sh — append one ActiveGraph custody event, absent-safe.
#
# The PROTOCOL mandates mirroring gate passages and Andon events into the
# custody store when ActiveGraph is configured and authorized. This helper
# makes that a single command so emission is never skipped for lack of API
# plumbing. When ActiveGraph is unavailable, it exits 0 with a fallback note:
# custody absence blocks nothing, and the Markdown ledger remains the
# evidence of record either way.
#
# Usage: custody-append.sh <store.db> <run-id> <event-id> <event-type> <payload-json> [caused-by-id]
# The optional caused-by id links this event to its cause (e.g., an
# andon.escalated event cites its andon.probe.recorded event), so replay and
# diff reconstruct causal chains, not just sequences.
# Exit 0: appended, or activegraph absent (note printed). Exit 2: usage error.

set -uo pipefail

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
  printf 'usage: custody-append.sh <store.db> <run-id> <event-id> <event-type> <payload-json> [caused-by-id]\n' >&2
  exit 2
fi
store="$1"; run_id="$2"; event_id="$3"; event_type="$4"; payload_json="$5"; caused_by="${6:-}"

py_cmd=()
fallback_py_cmd=()

remember_python() {
  if [ "${#fallback_py_cmd[@]}" -eq 0 ]; then
    fallback_py_cmd=("$@")
  fi
}

to_windows_path() {
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
      rest="${rest//\//\\}"
      printf '%s:\\%s' "${drive^^}" "$rest"
      ;;
    /[A-Za-z]/*)
      drive="${abs:1:1}"
      rest="${abs:3}"
      rest="${rest//\//\\}"
      printf '%s:\\%s' "${drive^^}" "$rest"
      ;;
    *)
      printf '%s' "$input"
      ;;
  esac
}

try_activegraph_python() {
  "$@" -c 'import activegraph' >/dev/null 2>&1 || return 1
  py_cmd=("$@")
  return 0
}

if command -v python >/dev/null 2>&1; then
  remember_python python
  try_activegraph_python python || true
fi
if [ "${#py_cmd[@]}" -eq 0 ] && command -v python3 >/dev/null 2>&1; then
  remember_python python3
  try_activegraph_python python3 || true
fi
if [ "${#py_cmd[@]}" -eq 0 ] && command -v py >/dev/null 2>&1; then
  remember_python py -3
  try_activegraph_python py -3 || true
fi
if [ "${#py_cmd[@]}" -eq 0 ]; then
  IFS=':' read -r -a path_entries <<< "${PATH:-}"
  for path_entry in "${path_entries[@]}"; do
    for candidate in "$path_entry/python.exe" "$path_entry/python"; do
      if [ -x "$candidate" ]; then
        remember_python "$candidate"
        if try_activegraph_python "$candidate"; then
          break 2
        fi
      fi
    done
  done
fi
if [ "${#py_cmd[@]}" -eq 0 ] && [ "${#fallback_py_cmd[@]}" -gt 0 ]; then
  py_cmd=("${fallback_py_cmd[@]}")
fi
if [ "${#py_cmd[@]}" -eq 0 ]; then
  printf 'custody-append: python unavailable; event not recorded (Markdown fallback remains evidence of record)\n'
  exit 0
fi

store_arg="$store"
case "${py_cmd[0]}" in
  *.exe|/mnt/*)
    if command -v cygpath >/dev/null 2>&1; then
      store_arg="$(cygpath -w "$store" 2>/dev/null || printf '%s' "$store")"
    else
      store_arg="$(to_windows_path "$store")"
    fi
    ;;
esac

"${py_cmd[@]}" - "$store_arg" "$run_id" "$event_id" "$event_type" "$payload_json" "$caused_by" <<'PY'
import json
import sys
import datetime

store_path, run_id, event_id, event_type, payload_json, caused_by = sys.argv[1:7]
caused_by = caused_by or None

# Payload schema poka-yoke runs BEFORE the activegraph import so the
# custody-mode labeling contract (V0260) is enforced even in environments
# where the event will not be recorded.
try:
    payload = json.loads(payload_json)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
except ValueError as exc:
    sys.stderr.write(f"custody-append: invalid payload JSON: {exc}\n")
    raise SystemExit(2)

if "custody_mode" not in payload:
    sys.stderr.write(
        "custody-append: payload must carry 'custody_mode' "
        "(live mode for this run, or historical_backfill)\n"
    )
    raise SystemExit(2)

if payload["custody_mode"] == "historical_backfill":
    required = ("source", "backfilled_at", "original_event_time", "evidence_boundary")
    missing = [k for k in required if k not in payload]
    if missing:
        sys.stderr.write(
            "custody-append: historical_backfill events must carry "
            + ", ".join(required)
            + f" (missing: {', '.join(missing)})\n"
        )
        raise SystemExit(2)

try:
    from activegraph import SQLiteEventStore, Event
except Exception:
    sys.stdout.write(
        "custody-append: activegraph absent; event not recorded "
        "(Markdown fallback remains evidence of record)\n"
    )
    raise SystemExit(0)

try:
    store = SQLiteEventStore(path=store_path, run_id=run_id)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if store.get_run() is None:
        store.upsert_run(
            label="implementaudit",
            created_at=ts,
            goal=payload.get("goal") or payload.get("purpose"),
            frame_id=None,
        )
    store.append(Event(id=event_id, type=event_type, payload=payload,
                       actor="implementaudit", frame_id=None, caused_by=caused_by,
                       timestamp=ts))
except Exception as exc:
    sys.stdout.write(
        f"custody-append: store write failed ({exc}); event not recorded "
        "(Markdown fallback remains evidence of record)\n"
    )
    raise SystemExit(0)

sys.stdout.write(f"custody-append: recorded {event_id} ({event_type})\n")
PY
