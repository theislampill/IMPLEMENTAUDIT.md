#!/usr/bin/env bash
# validate-phase.sh — verify a phase spec has the required structure
#
# Usage: validate-phase.sh <path-to-phase-spec.md>
#
# Exits 0 if the spec has all required markers, sections, and non-placeholder content.
# Exits 1 with specific errors otherwise. Exits 2 for usage errors.

set -uo pipefail

fail() {
  printf 'validate-phase: %s\n' "$*" >&2
  exit 1
}

phase_file="${1:-}"
[ -n "$phase_file" ] || { printf 'usage: validate-phase.sh <phase-file>\n' >&2; exit 2; }
[ -f "$phase_file" ] || fail "phase file not found: $phase_file"

errors=0

err() {
  printf 'validate-phase: ERROR: %s\n' "$*" >&2
  errors=$((errors + 1))
}

# ---------------------------------------------------------------------------
# Marker checks (required transcript anchors)
# ---------------------------------------------------------------------------
for marker in \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  CONTINUITY_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE
do
  grep -q "$marker" "$phase_file" || err "missing marker: $marker"
done

# ---------------------------------------------------------------------------
# Inline field checks (must appear in the IMPLEMENTAUDIT_PHASE_START block)
# ---------------------------------------------------------------------------
for field in \
  "Run root:" \
  "Baseline ref:" \
  "Owner/source:" \
  "Task:" \
  "Type:"
do
  grep -qi "^${field}" "$phase_file" || err "missing field: $field"
done

# Depends on phases must be present (even if value is "none")
grep -qi "^Depends on phases:" "$phase_file" || err "missing field: Depends on phases"

# ---------------------------------------------------------------------------
# Section checks (## headings)
# ---------------------------------------------------------------------------
for section in \
  "Work" \
  "Acceptance criteria" \
  "Mandatory commands" \
  "Evidence required" \
  "Rollback"
do
  grep -qi "^## .*${section}" "$phase_file" || err "missing section: ## ${section}"
done

# Rollback / defer path section
grep -qi "^## Rollback" "$phase_file" || err "missing section: ## Rollback / defer path"

# Graphify / ActiveGraph / Markdown fallback status
grep -qi "Markdown fallback:" "$phase_file" || err "missing: Markdown fallback status"

# ---------------------------------------------------------------------------
# Python checks: non-placeholder content validation
# ---------------------------------------------------------------------------
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  py_cmd=()
fi

PLACEHOLDER_TERMS='{{|tbd|todo|n/a|placeholder|criterion 1|criterion 2|work bullet|command 1|evidence 1|why one sentence|one line task'

if [ "${#py_cmd[@]}" -gt 0 ]; then
  python_errors=0

  # Check: acceptance criteria section has at least 1 non-placeholder item
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|criterion [0-9]|work bullet|"
    r"command [0-9]|evidence [0-9]|why one sentence|one.?line.?task",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_ac = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Acceptance criteria", stripped, re.IGNORECASE):
        in_ac = True
        continue
    if in_ac and re.match(r"^##\s+", stripped):
        break
    if not in_ac:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: acceptance criteria are placeholder-only or missing\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "acceptance criteria are placeholder-only or missing"
  python_errors=0

  # Check: mandatory commands section has at least 1 non-placeholder item
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|command [0-9]",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_mc = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Mandatory commands", stripped, re.IGNORECASE):
        in_mc = True
        continue
    if in_mc and re.match(r"^##\s+", stripped):
        break
    if not in_mc:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: mandatory commands are placeholder-only or missing\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "mandatory commands are placeholder-only or missing"
  python_errors=0

  # Check: evidence required section has at least 1 non-placeholder item
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|evidence [0-9]",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_ev = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Evidence required", stripped, re.IGNORECASE):
        in_ev = True
        continue
    if in_ev and re.match(r"^##\s+", stripped):
        break
    if not in_ev:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: evidence required is placeholder-only or missing\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "evidence required is placeholder-only or missing"
fi

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
if (( errors > 0 )); then
  printf 'validate-phase: %d error(s)\n' "$errors" >&2
  exit 1
fi

printf 'validate-phase: ok\n'
