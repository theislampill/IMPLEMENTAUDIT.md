#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$ROOT/scripts/check-v0410-reabsorption-preparation.py"
PREP_REL="docs/research/implementaudit/v0410-reabsorption-preparation"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() { printf 'v0410-reabsorption-preparation.test: %s\n' "$*" >&2; exit 1; }

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

expect_failure() {
  local expected="$1"; shift
  local output
  if output="$("$@" 2>&1)"; then
    fail "expected failure containing: $expected"
  fi
  printf '%s' "$output" | grep -Fq "$expected" ||
    fail "failure did not contain '$expected': $output"
}
fresh_fixture() {
  rm -rf "$TMP/repo"
  mkdir -p "$TMP/repo/docs/research/implementaudit" "$TMP/repo/scripts"
  cp -R "$ROOT/$PREP_REL" "$TMP/repo/docs/research/implementaudit/"
  cp "$CHECKER" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py"
}

"${py_cmd[@]}" "$CHECKER" --root "$ROOT"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_PROVISIONAL_RXX_CANDIDATE.md" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace("RXX_ID=UNALLOCATED", "RXX_ID=R56"), encoding="utf-8")
PY
expect_failure "provisional RXX ID must remain UNALLOCATED" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_PROVISIONAL_RXX_CANDIDATE.md" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace(
    "CANDIDATE_PENDING_RELEASED_V0400_EVIDENCE",
    "NEW_RXX_REQUIRED",
), encoding="utf-8")
PY
expect_failure "provisional RXX disposition is predecided" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_CURRENT_DISPOSITION_SCHEMA.json" <<'PY'
from pathlib import Path
import json, sys
p = Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["properties"]["ROWS"]["minItems"] = 657
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "current disposition schema must require exactly 658 rows" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_CHILD_SKILL_ADMISSION_SCHEMA.json" <<'PY'
from pathlib import Path
import json, sys
p = Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["required"].remove("NOT_REFERENCE_ONLY")
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "child-skill schema lost required admission field: NOT_REFERENCE_ONLY" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_REABSORPTION_EXECUTOR_WORK_ORDER.md" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace(
    "HYPOTHESIS_TO_TEST",
    "ACCEPTED",
), encoding="utf-8")
PY
expect_failure "state-derived terminal orchestration must remain a hypothesis" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

fresh_fixture
"${py_cmd[@]}" - "$TMP/repo/$PREP_REL/V0410_CURRENT_DISPOSITION_SCHEMA.json" <<'PY'
from pathlib import Path
import json, sys
p = Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["$defs"]["deferredFact"]["oneOf"] = [{"type": "string"}]
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "released-v0.4-dependent fields lost explicit deferral" "${py_cmd[@]}" "$TMP/repo/scripts/check-v0410-reabsorption-preparation.py" --root "$TMP/repo"

printf 'v0410-reabsorption-preparation.test: PASS\n'
