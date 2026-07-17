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
[ -n "$phase_file" ] || { printf 'usage: validate-phase.sh <phase-file> | --explain\n' >&2; exit 2; }

if [ "$phase_file" = "--explain" ]; then
  cat <<'EXPLAIN'
validate-phase: a filled phase spec requires —
  markers: IMPLEMENTAUDIT_PHASE_START, IMPLEMENTAUDIT_PHASE_VERIFY,
           AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, IMPLEMENTAUDIT_PHASE_DONE
  header fields: Task, Type, Run root, Baseline ref, Owner/source,
                 Audit object, Depends on phases
  sections: ## Current state excerpts; ## Work;
            ## Acceptance criteria (>=1 non-placeholder `- [ ]` item);
            ## Mandatory commands (>=1 non-placeholder `- <command>` list item
            with expected success shape);
            ## Evidence required (>=1 non-placeholder `- <evidence>` item);
            ## Rollback / defer path; ## Maintenance notes
  sidecar status: literal `Markdown fallback:` field (any value)
Canonical filled examples (source repo only): fixtures/run-root-example/phases/phase-1.md (brownfield)
and (source repo only) fixtures/phase-design/dmadv-greenfield-phase.md (greenfield);
the blank skeleton ships as templates/phase-goal.txt.
EXPLAIN
  exit 0
fi

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
  "Current state excerpts" \
  "Acceptance criteria" \
  "Mandatory commands" \
  "Evidence required" \
  "Rollback" \
  "Maintenance notes"
do
  grep -qi "^## .*${section}" "$phase_file" || err "missing section: ## ${section}"
done

# Rollback / defer path section
grep -qi "^## Rollback" "$phase_file" || err "missing section: ## Rollback / defer path"

# Graphify / ActiveGraph / Markdown fallback status
grep -qi "Markdown fallback:" "$phase_file" || err "missing literal field \`Markdown fallback:\` (any value) - see the sidecar status block in templates/phase-goal.txt"

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
    sys.stderr.write("validate-phase: ## Acceptance criteria needs at least one non-placeholder `- [ ] criterion` list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Acceptance criteria needs at least one non-placeholder list item (- [ ] ...)"
  python_errors=0

  # Check: mandatory commands section has at least 1 non-placeholder item and
  # each command item states an expected success shape.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|command [0-9]",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
missing_expected = []
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
            if not re.search(r"\b(expected|expects|exit 0|passes|pass|no errors|outputs?|last ~?10 lines)\b", item, re.IGNORECASE):
                missing_expected.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Mandatory commands needs at least one non-placeholder `- <command>` list item (bare lines are not counted)\n")
    raise SystemExit(1)
if missing_expected:
    sys.stderr.write(
        "validate-phase: ## Mandatory commands items must include expected success shape; missing: "
        + "; ".join(missing_expected[:3])
        + "\n"
    )
    raise SystemExit(1)

# Evidence property tags (#3): every command declares which property class
# it exercises (structural / behavioral / provenance). Newly authored specs
# (any tagged item present) REQUIRE tags on every item; a fully untagged
# spec is treated as legacy and warned, not failed. Authorization is not an
# evidence property and is not accepted as one.
TAG = re.compile(r"property:\s*(structural|behavioral|provenance)\b",
                 re.IGNORECASE)
# \b-anchored: a PREFIX of a valid class ("structurally", "behavioralish")
# is an invalid tag, not an untagged/legacy item (Fable review of PR #25).
BAD_TAG = re.compile(r"property:\s*(?!(?:structural|behavioral|provenance)\b)\w+",
                     re.IGNORECASE)
tagged = [i for i in items if TAG.search(i)]
badly = [i for i in items if BAD_TAG.search(i)]
if badly:
    sys.stderr.write(
        "validate-phase: invalid evidence property tag (allowed: "
        "structural / behavioral / provenance; authorization is a separate "
        "gate, not a property): " + "; ".join(badly[:3]) + "\n")
    raise SystemExit(1)
if tagged and len(tagged) != len(items):
    untagged = [i for i in items if not TAG.search(i)]
    sys.stderr.write(
        "validate-phase: ## Mandatory commands mixes tagged and untagged "
        "items — every command in a newly authored spec declares "
        "`property: structural|behavioral|provenance`; untagged: "
        + "; ".join(untagged[:3]) + "\n")
    raise SystemExit(1)
# A property tag without a scope is the mis-scoped-validator hazard the
# tag exists to prevent: the class says WHAT KIND of evidence, the scope
# says what the check actually tests (and implicitly what it does not).
noscope = [i for i in tagged
           if not re.search(r"scope:\s*\S", i, re.IGNORECASE)]
if noscope:
    sys.stderr.write(
        "validate-phase: property-tagged command lacks `scope:` (the "
        "plain-language statement of what this check actually tests): "
        + "; ".join(noscope[:3]) + "\n")
    raise SystemExit(1)
if not tagged:
    sys.stderr.write(
        "validate-phase: WARNING legacy spec — mandatory commands carry no "
        "`property:` evidence tags (structural / behavioral / provenance); "
        "newly authored specs must tag every command\n")
PY
  [ "$python_errors" -eq 0 ] || err "## Mandatory commands needs non-placeholder list items with expected success shape"
  python_errors=0

  # Check: current-state excerpts section has at least one non-placeholder item.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|current state",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_section = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Current state excerpts", stripped, re.IGNORECASE):
        in_section = True
        continue
    if in_section and re.match(r"^##\s+", stripped):
        break
    if not in_section:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Current state excerpts needs at least one non-placeholder list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Current state excerpts needs at least one non-placeholder list item"
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
    sys.stderr.write("validate-phase: ## Evidence required needs at least one non-placeholder `- <evidence>` list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Evidence required needs at least one non-placeholder list item (- <evidence>)"
  python_errors=0

  # Check: maintenance notes section has at least one non-placeholder item.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|maintenance note",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_section = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Maintenance notes", stripped, re.IGNORECASE):
        in_section = True
        continue
    if in_section and re.match(r"^---\s*$|^##\s+", stripped):
        break
    if not in_section:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Maintenance notes needs at least one non-placeholder list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Maintenance notes needs at least one non-placeholder list item"
fi

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
if (( errors > 0 )); then
  printf 'validate-phase: %d error(s); see templates/phase-goal.txt in the skill directory for the canonical filled shape\n' "$errors" >&2
  exit 1
fi

printf 'validate-phase: ok\n'
