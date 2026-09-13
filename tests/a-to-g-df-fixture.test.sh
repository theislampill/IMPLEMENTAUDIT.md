#!/usr/bin/env bash
set -euo pipefail

lifecycle_fixture="${1:-fixtures/a-to-g/holon-lifecycle.json}"
andon_fixture="${2:-fixtures/a-to-g/andon-trigger-routing.json}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

mode="${3:-all}"
case "$mode" in
  all|--four-child-only) ;;
  *) printf '%s\n' 'unknown D/F fixture selector' >&2; exit 2 ;;
esac
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PYTHON_BIN" "$script_dir/andon-trigger-consideration.py" --root "$script_dir/.." --fixture "$andon_fixture"
if [[ "$mode" == --four-child-only ]]; then
  exit 0
fi

"$PYTHON_BIN" - "$lifecycle_fixture" "$andon_fixture" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    lifecycle = json.load(handle)
with open(sys.argv[2], encoding="utf-8") as handle:
    andon = json.load(handle)

assert lifecycle["schema"] == "implementaudit.native-a-g.fixture.v1"
assert lifecycle["slice"] == "D_VISIBLE_HOLON_LIFECYCLE"
lcases = {case["id"]: case for case in lifecycle["cases"]}
assert set(lcases) == {
    "D01_ALL_FOUR_HOLONS_REQUIRE_VISIBLE_LIFECYCLE",
    "D02_CEREMONIAL_SKILL_READ_GETS_ZERO_CREDIT",
    "D03_MISMATCHED_INSTALLED_IDENTITY_FAILS",
    "D04_NOT_REQUIRED_ROUTES_NO_CHILD",
    "D05_PRECOMPACTION_RETURN_REQUIRES_REBIND",
}
assert lcases["D01_ALL_FOUR_HOLONS_REQUIRE_VISIBLE_LIFECYCLE"]["expected"]["required_sequence"] == ["OPEN", "LOAD", "USE", "RETURN", "DISPOSE", "RECONCILE"]
assert lcases["D02_CEREMONIAL_SKILL_READ_GETS_ZERO_CREDIT"]["expected"]["child_credit"] is False
assert lcases["D03_MISMATCHED_INSTALLED_IDENTITY_FAILS"]["expected"]["accepted"] is False
assert lcases["D04_NOT_REQUIRED_ROUTES_NO_CHILD"]["expected"]["children_opened"] == 0
assert lcases["D05_PRECOMPACTION_RETURN_REQUIRES_REBIND"]["expected"]["status"] == "HISTORICAL_BUFFERED"

assert andon["schema"] == "implementaudit.native-a-g.fixture.v1"
assert andon["slice"] == "F_ANDON_COGNITION_OWNERSHIP"
fcases = {case["id"]: case for case in andon["cases"]}
assert set(fcases) == {
    "F01_SUBSTANTIVE_ABNORMALITY_ROUTES_AUDIT_ANDON",
    "F02_DETERMINISTIC_MECHANICAL_MISMATCH_STAYS_GOVERNOR_MECHANICAL",
    "F03_GOVERNOR_DIAGNOSIS_BEFORE_OPEN_REJECTED",
    "F04_CHILD_TO_CHILD_ROUTING_FORBIDDEN",
    "F05_NEW_CAUSAL_MECHANISM_REQUIRES_AUDIT_ANDON",
}
assert fcases["F01_SUBSTANTIVE_ABNORMALITY_ROUTES_AUDIT_ANDON"]["expected"]["route"] == "audit-andon"
assert fcases["F02_DETERMINISTIC_MECHANICAL_MISMATCH_STAYS_GOVERNOR_MECHANICAL"]["expected"]["route"] == "NONE"
assert fcases["F03_GOVERNOR_DIAGNOSIS_BEFORE_OPEN_REJECTED"]["expected"]["accepted"] is False
assert fcases["F04_CHILD_TO_CHILD_ROUTING_FORBIDDEN"]["expected"]["decision"] == "STOP_CHILD_TO_CHILD_DISPATCH"
assert fcases["F05_NEW_CAUSAL_MECHANISM_REQUIRES_AUDIT_ANDON"]["expected"]["route"] == "audit-andon"
assert {case["coverage"] for case in lcases.values()} == {"positive", "negative", "boundary"}
assert {case["coverage"] for case in fcases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-df-fixture: ok (D 5/5; F 5/5)")
PY
