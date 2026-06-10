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

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
else
  printf 'custody-append: python unavailable; event not recorded (Markdown fallback remains evidence of record)\n'
  exit 0
fi

"${py_cmd[@]}" - "$store" "$run_id" "$event_id" "$event_type" "$payload_json" "$caused_by" <<'PY'
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
