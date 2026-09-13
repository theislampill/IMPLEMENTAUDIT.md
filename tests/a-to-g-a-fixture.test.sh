#!/usr/bin/env bash
set -euo pipefail

fixture="${1:-fixtures/a-to-g/dependency-types.json}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

"$PYTHON_BIN" - "$fixture" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)

assert data["schema"] == "implementaudit.native-a-g.fixture.v1"
assert data["slice"] == "A_DEPENDENCY_TYPING"
assert data["authority_ceiling"] == "PREPARATION_PRODUCT_EVIDENCE_ONLY"
cases = {case["id"]: case for case in data["cases"]}
expected = {
    "A01_MAY_AFFECT_IS_NOT_PREDECESSOR",
    "A02_SHARED_WRITER_SERIALIZES_ONLY_CONFLICT",
    "A03_UNKNOWN_EDGE_BLOCKS_ONLY_AFFECTED_WORK",
    "A04_MANDATORY_JOIN_REMAINS_REQUIRED",
    "A05_CAPACITY_LIMIT_IS_NOT_SEMANTIC_EDGE",
}
assert set(cases) == expected
assert cases["A01_MAY_AFFECT_IS_NOT_PREDECESSOR"]["expected"]["learning_ready"] is True
assert cases["A01_MAY_AFFECT_IS_NOT_PREDECESSOR"]["expected"]["authority_deferred_to_join"] is True
assert cases["A02_SHARED_WRITER_SERIALIZES_ONLY_CONFLICT"]["expected"]["serialize"] == ["writer_left", "writer_right"]
assert cases["A02_SHARED_WRITER_SERIALIZES_ONLY_CONFLICT"]["expected"]["unrelated_ready"] == ["reader_disjoint"]
assert cases["A03_UNKNOWN_EDGE_BLOCKS_ONLY_AFFECTED_WORK"]["expected"]["blocked"] == ["unknown_consumer"]
assert cases["A03_UNKNOWN_EDGE_BLOCKS_ONLY_AFFECTED_WORK"]["expected"]["ready"] == ["independent_reader"]
assert cases["A04_MANDATORY_JOIN_REMAINS_REQUIRED"]["expected"]["join_required"] is True
assert cases["A04_MANDATORY_JOIN_REMAINS_REQUIRED"]["expected"]["early_acceptance"] is False
assert cases["A05_CAPACITY_LIMIT_IS_NOT_SEMANTIC_EDGE"]["expected"]["resource_queue"] is True
assert cases["A05_CAPACITY_LIMIT_IS_NOT_SEMANTIC_EDGE"]["expected"]["semantic_dependency_created"] is False
assert {case["coverage"] for case in cases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-a-fixture: ok (5/5)")
PY
