#!/usr/bin/env bash
set -euo pipefail

fixture="${1:-fixtures/a-to-g/execution-owner.json}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

"$PYTHON_BIN" - "$fixture" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)

assert data["schema"] == "implementaudit.native-a-g.fixture.v1"
assert data["slice"] == "G_THIN_GOVERNOR_EXECUTION_OWNER"
cases = {case["id"]: case for case in data["cases"]}
assert set(cases) == {
    "G01_IDENTITY_HASH_CURRENTNESS_IS_GOVERNOR_MECHANICAL",
    "G02_MATERIAL_ORDINARY_INVESTIGATION_ROUTES_CHILD_TASK",
    "G03_SPECIALIST_ABNORMALITY_ROUTES_AUDIT_ANDON",
    "G04_UNKNOWN_OR_CONTRADICTORY_INPUT_BLOCKS",
    "G05_POSTHOC_REVIEWER_LAUNDERING_GETS_ZERO_CREDIT",
    "G06_DISJOINT_TASKS_MAY_RUN_CONCURRENTLY",
    "G07_CHILD_TO_CHILD_DISPATCH_STOPS",
}
assert cases["G01_IDENTITY_HASH_CURRENTNESS_IS_GOVERNOR_MECHANICAL"]["expected"]["owner"] == "GOVERNOR_MECHANICAL"
assert cases["G02_MATERIAL_ORDINARY_INVESTIGATION_ROUTES_CHILD_TASK"]["expected"]["owner"] == "CHILD_TASK"
assert cases["G03_SPECIALIST_ABNORMALITY_ROUTES_AUDIT_ANDON"]["expected"]["owner"] == "CHILD_SKILL:audit-andon"
assert cases["G04_UNKNOWN_OR_CONTRADICTORY_INPUT_BLOCKS"]["expected"]["owner"] == "BLOCK"
assert cases["G05_POSTHOC_REVIEWER_LAUNDERING_GETS_ZERO_CREDIT"]["expected"]["child_credit"] is False
assert cases["G06_DISJOINT_TASKS_MAY_RUN_CONCURRENTLY"]["expected"]["concurrent"] is True
assert cases["G07_CHILD_TO_CHILD_DISPATCH_STOPS"]["expected"]["decision"] == "STOP_CHILD_TO_CHILD_DISPATCH"
assert {case["coverage"] for case in cases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-g-fixture: ok (7/7)")
PY
