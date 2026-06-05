#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-marker-order: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [ "$#" -eq 0 ]; then
  set -- fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
fi

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$@" <<'PY'
import sys
from pathlib import Path

phase_order = [
    "IMPLEMENTAUDIT_PHASE_START",
    "IMPLEMENTAUDIT_PHASE_VERIFY",
    "AGENTS_UPDATE_DECISION",
    "IMPLEMENTAUDIT_PHASE_DONE",
]
final_order = [
    "AUDIT_START",
    "AUDIT_VERIFY",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
]


def positions(text, marker):
    out = []
    start = 0
    while True:
        idx = text.find(marker, start)
        if idx < 0:
            return out
        out.append(idx)
        start = idx + len(marker)


def first(text, marker):
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"{path}: missing marker {marker}")
    return idx


for arg in sys.argv[1:]:
    path = Path(arg)
    text = path.read_text()

    if "AUDIT_HANDOFF" in text and "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        raise SystemExit(f"{path}: handoff transcript must not also complete")
    if "FAILURE_HANDOFF" in text and "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        raise SystemExit(f"{path}: failure handoff transcript must not also complete")
    if "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        audit_done = first(text, "AUDIT_COMPLETE")
        run_done = first(text, "IMPLEMENTAUDIT_RUN_COMPLETE")
        if not audit_done < run_done:
            raise SystemExit(f"{path}: AUDIT_COMPLETE must precede IMPLEMENTAUDIT_RUN_COMPLETE")

    for earlier, later in zip(phase_order, phase_order[1:]):
        earlier_positions = positions(text, earlier)
        later_positions = positions(text, later)
        if earlier_positions and later_positions and min(later_positions) < min(earlier_positions):
            raise SystemExit(f"{path}: {earlier} must precede {later}")

    for earlier, later in zip(final_order, final_order[1:]):
        if earlier in text and later in text and first(text, earlier) > first(text, later):
            raise SystemExit(f"{path}: {earlier} must precede {later}")

print("check-marker-order: ok")
PY
