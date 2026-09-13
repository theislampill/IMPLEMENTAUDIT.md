#!/usr/bin/env bash
set -euo pipefail

fixture="${1:-fixtures/a-to-g/semantic-invalidation-radius.json}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

"$PYTHON_BIN" - "$fixture" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)

assert data["schema"] == "implementaudit.native-a-g.fixture.v1"
assert data["slice"] == "B_SEMANTIC_INVALIDATION_RADIUS"
cases = {case["id"]: case for case in data["cases"]}
assert set(cases) == {
    "B01_LOCAL_CHANGE_PRESERVES_DISJOINT_EVIDENCE",
    "B02_PACKAGE_INVENTORY_CHANGE_EXPANDS_TO_INSTALL",
    "B03_UNKNOWN_IMPACT_BLOCKS_ONLY_AFFECTED_EVIDENCE",
    "B04_HARNESS_ONLY_CHANGE_INVALIDATES_PROOF_NOT_RUNTIME",
    "B05_LATER_DISJOINT_CHANGE_PRESERVES_PRIOR_CREDIT",
}
assert cases["B01_LOCAL_CHANGE_PRESERVES_DISJOINT_EVIDENCE"]["expected"]["invalidated"] == ["owner_test", "direct_consumer"]
assert cases["B01_LOCAL_CHANGE_PRESERVES_DISJOINT_EVIDENCE"]["expected"]["preserved"] == ["disjoint_review", "disjoint_runtime_test"]
assert cases["B02_PACKAGE_INVENTORY_CHANGE_EXPANDS_TO_INSTALL"]["expected"]["invalidated"] == ["package_inventory", "package_boundary", "install_projection"]
assert cases["B03_UNKNOWN_IMPACT_BLOCKS_ONLY_AFFECTED_EVIDENCE"]["expected"]["global_replay"] is False
assert cases["B04_HARNESS_ONLY_CHANGE_INVALIDATES_PROOF_NOT_RUNTIME"]["expected"]["invalidated"] == ["harness_result", "review_of_harness_result"]
assert cases["B04_HARNESS_ONLY_CHANGE_INVALIDATES_PROOF_NOT_RUNTIME"]["expected"]["preserved"] == ["runtime_semantics", "source_review"]
assert cases["B05_LATER_DISJOINT_CHANGE_PRESERVES_PRIOR_CREDIT"]["expected"]["prior_credit_preserved"] is True
assert {case["coverage"] for case in cases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-b-fixture: ok (5/5)")
PY
