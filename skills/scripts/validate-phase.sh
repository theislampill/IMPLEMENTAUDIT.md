#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'validate-phase: %s\n' "$*" >&2
  exit 1
}

phase_file="${1:-}"
[ -n "$phase_file" ] || fail "usage: validate-phase.sh <phase-file>"
[ -f "$phase_file" ] || fail "phase file not found: $phase_file"

for marker in \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE
do
  grep -q "$marker" "$phase_file" || fail "missing marker: $marker"
done

grep -qi "Smoke A" "$phase_file" || fail "missing Smoke A"
grep -qi "Smoke B" "$phase_file" || fail "missing Smoke B"
grep -qi "Owner/source" "$phase_file" || fail "missing Owner/source"
grep -qi "Acceptance" "$phase_file" || fail "missing Acceptance"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  py_cmd=()
fi

if [ "${#py_cmd[@]}" -gt 0 ]; then
  "${py_cmd[@]}" - "$phase_file" <<'PY' || fail "acceptance criteria are placeholder-only"
import re
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_section = False
for line in lines:
    if re.match(r"(?i)^Acceptance criteria:\s*$", line.strip()):
        in_section = True
        continue
    if in_section and re.match(r"(?i)^(Smoke A|Smoke B|Implementation notes|IMPLEMENTAUDIT_PHASE_VERIFY)\s*:", line.strip()):
        break
    if not in_section:
        continue
    stripped = line.strip()
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and item not in {".", "tbd", "todo", "n/a"}:
            items.append(item)
if not items:
    raise SystemExit(1)
PY
fi

printf 'validate-phase: ok\n'
