#!/usr/bin/env bash
set -euo pipefail

fail() { printf 'check-respec-impact-set: %s\n' "$*" >&2; exit 1; }
file="${1:-}"
[ -f "$file" ] || fail "impact set not found: ${file:-<none>}"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail 'python, python3, or py -3 is required'
fi

"${py_cmd[@]}" - "$file" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()


def fail(message):
    print(f"check-respec-impact-set: {message}", file=sys.stderr)
    raise SystemExit(1)


if not lines or lines[0].strip() != "IMPLEMENTAUDIT_RESPEC_IMPACT_SET":
    fail("missing IMPLEMENTAUDIT_RESPEC_IMPACT_SET marker")


def field(name):
    prefix = f"{name}:"
    values = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
    if len(values) != 1 or not values[0]:
        fail(f"{name} must occur exactly once with a value")
    return values[0]


field("Change")
field("Declared by")
try:
    population = int(field("Population size"))
    literal_count = int(field("Literal count"))
    stem_count = int(field("Stem/dirname additional count"))
except ValueError:
    fail("population and enumeration counts must be integers")
if population < 1 or literal_count < 0 or stem_count < 0:
    fail("population must be positive and method counts nonnegative")
if field("Enumeration method") != "literal + stem/dirname":
    fail("Enumeration method must be literal + stem/dirname")
literal_output = field("Literal carriers")
stem_output = field("Stem/dirname additional carriers")
if literal_count and literal_output == "none":
    fail("Literal carriers output contradicts Literal count")
if not literal_count and literal_output != "none":
    fail("Literal carriers must be none when Literal count is zero")
if stem_count and stem_output == "none":
    fail("Stem/dirname output contradicts additional count")
if not stem_count and stem_output != "none":
    fail("Stem/dirname additional carriers must be none when count is zero")
if literal_count + stem_count != population:
    fail("two-method counts do not reconcile to Population size")
replacement = field("Replacement")
replacement_path = field("Replacement path")
if replacement not in {"yes", "no"}:
    fail("Replacement must be yes or no")
if replacement == "no" and replacement_path != "none":
    fail("Replacement path must be none when Replacement is no")
if replacement == "yes" and replacement_path == "none":
    fail("Replacement yes requires a concrete Replacement path")


def table_rows(header, end_heading=None):
    try:
        start = lines.index(header) + 1
    except ValueError:
        fail(f"missing table header: {header}")
    rows = []
    for line in lines[start:]:
        if end_heading and line.startswith(end_heading):
            break
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r"-+", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


carriers = table_rows(
    "| # | Carrier | Kind | Status | Evidence |", "## Invariants carried forward"
)
if len(carriers) != population:
    fail(f"carrier row count {len(carriers)} does not match Population size {population}")
seen = set()
terminal_deferred = re.compile(
    r"^deferred\((deferred|transferred|owner-assigned|risk-accepted|validated-resolved):\s*[^)]+\)$"
)
for index, row in enumerate(carriers, 1):
    if len(row) != 5:
        fail(f"carrier row {index} must have five cells")
    number, carrier, kind, status, evidence = row
    if number != str(index) or not carrier or not kind:
        fail(f"carrier row {index} has invalid identity, carrier, or kind")
    if carrier in seen:
        fail(f"duplicate carrier: {carrier}")
    seen.add(carrier)
    valid = status in {"applied", "owner-assigned"}
    valid = valid or bool(re.fullmatch(r"out-of-scope\([^)]+\)", status))
    valid = valid or bool(terminal_deferred.fullmatch(status))
    if not valid:
        fail(f"carrier {carrier}: invalid or empty Status '{status}'")
    if not evidence or evidence in {"-", "none"}:
        fail(f"carrier {carrier}: terminal Status requires Evidence")


def parse_output(value):
    if value == "none":
        return []
    items = [item.strip() for item in value.split(",")]
    if any(not item for item in items) or len(items) != len(set(items)):
        fail("enumeration outputs must be nonempty, unique comma-separated carriers")
    return items


literal_carriers = parse_output(literal_output)
stem_carriers = parse_output(stem_output)
if len(literal_carriers) != literal_count or len(stem_carriers) != stem_count:
    fail("enumeration output lengths do not match their method counts")
if set(literal_carriers) & set(stem_carriers):
    fail("stem/dirname additional carriers must be additions, not literal duplicates")
if set(literal_carriers) | set(stem_carriers) != seen:
    fail("two-method carrier union does not equal the carrier table")

invariants = table_rows(
    "| # | Invariant | Enforced by | Present in replacement? | Evidence |"
)
if replacement == "yes" and not invariants:
    fail("replacement requires at least one invariant carried forward")
replacement_file = None
if replacement == "yes":
    replacement_file = Path(replacement_path)
    if not replacement_file.is_absolute():
        replacement_file = path.parent / replacement_file
    if not replacement_file.is_file():
        fail(f"replacement file is not inspectable: {replacement_path}")
    replacement_text = replacement_file.read_text(encoding="utf-8")
for index, row in enumerate(invariants, 1):
    if len(row) != 5:
        fail(f"invariant row {index} must have five cells")
    number, invariant, enforced_by, present, evidence = row
    if number != str(index) or not invariant or not enforced_by:
        fail(f"invariant row {index} is incomplete")
    if present != "yes" or not evidence.startswith("contains:"):
        fail(f"invariant {invariant}: replacement presence and Evidence are required")
    marker = evidence[len("contains:"):]
    if not marker or marker not in replacement_text:
        fail(f"invariant {invariant}: declared marker is absent from replacement")

print(f"check-respec-impact-set: ok ({len(carriers)} carrier row(s), {len(invariants)} invariant row(s))")
PY
