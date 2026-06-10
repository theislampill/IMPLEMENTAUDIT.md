#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-marker-order: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [ "$#" -eq 0 ]; then
  set -- \
    fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md \
    fixtures/simple-audit/EXPECTED-ANDON-RECOVERY-SKELETON.md \
    fixtures/simple-audit/EXPECTED-ANDON-HANDOFF-SKELETON.md
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
    "AUDIT_GAPS",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
]
andon_order = [
    "ANDON_PROBE",
    "ANDON_ESCALATE",
    "ANDON_HANDOFF",
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
    if "ANDON_HANDOFF" in text and "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        raise SystemExit(f"{path}: Andon handoff transcript must not also complete")
    # Legacy marker spelling from pre-v0.2.9.0 transcripts: same exclusivity rule.
    if "FAILURE_HANDOFF" in text and "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        raise SystemExit(f"{path}: failure handoff transcript must not also complete")
    for marker in ("ANDON_ESCALATE", "ANDON_HANDOFF"):
        if marker in text and "ANDON_PROBE" not in text:
            raise SystemExit(f"{path}: {marker} requires a preceding ANDON_PROBE")

    if "IMPLEMENTAUDIT_PAUSE" in text:
        starts = positions(text, "IMPLEMENTAUDIT_PHASE_START")
        pause = first(text, "IMPLEMENTAUDIT_PAUSE")
        if not starts or min(starts) > pause:
            raise SystemExit(
                f"{path}: IMPLEMENTAUDIT_PAUSE requires a preceding IMPLEMENTAUDIT_PHASE_START"
            )
    if "IMPLEMENTAUDIT_RUN_COMPLETE" in text:
        audit_done = first(text, "AUDIT_COMPLETE")
        run_done = first(text, "IMPLEMENTAUDIT_RUN_COMPLETE")
        if not audit_done < run_done:
            raise SystemExit(f"{path}: AUDIT_COMPLETE must precede IMPLEMENTAUDIT_RUN_COMPLETE")

    for order in (phase_order, andon_order):
        for earlier, later in zip(order, order[1:]):
            earlier_positions = positions(text, earlier)
            later_positions = positions(text, later)
            if earlier_positions and later_positions and min(later_positions) < min(earlier_positions):
                raise SystemExit(f"{path}: {earlier} must precede {later}")

    # Fixture-scoped escalation-progress rule: each ANDON_ESCALATE block must
    # show progress via "New evidence:" or "Changed approach:". If neither can
    # be truthfully filled, the protocol routes to ANDON_HANDOFF condition
    # evaluation instead of escalating. Block = text from the marker to the
    # next marker (lightweight segmentation, not a transcript parser).
    block_boundaries = (
        "ANDON_PROBE",
        "ANDON_ESCALATE",
        "ANDON_HANDOFF",
        "IMPLEMENTAUDIT_PHASE",
        "AUDIT_",
    )
    for start in positions(text, "ANDON_ESCALATE"):
        search_from = start + len("ANDON_ESCALATE")
        end = len(text)
        for marker in block_boundaries:
            idx = text.find(marker, search_from)
            if 0 <= idx < end:
                end = idx
        block = text[start:end]
        if "New evidence:" not in block and "Changed approach:" not in block:
            raise SystemExit(
                f"{path}: ANDON_ESCALATE block lacks 'New evidence:' or "
                f"'Changed approach:' (route to ANDON_HANDOFF conditions instead)"
            )

    for earlier, later in zip(final_order, final_order[1:]):
        if earlier in text and later in text and first(text, earlier) > first(text, later):
            raise SystemExit(f"{path}: {earlier} must precede {later}")

print("check-marker-order: ok")
PY
