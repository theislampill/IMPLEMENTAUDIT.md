#!/usr/bin/env bash
set -euo pipefail

fixture="${1:-fixtures/a-to-g/transaction-concurrency.json}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

"$PYTHON_BIN" - "$fixture" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)

assert data["schema"] == "implementaudit.native-a-g.fixture.v1"
assert data["slice"] == "C_TRANSACTION_SCOPED_CONCURRENCY"
cases = {case["id"]: case for case in data["cases"]}
assert set(cases) == {
    "C01_DISJOINT_TRANSACTIONS_MAY_RUN_CONCURRENTLY",
    "C02_SECOND_CHILD_IN_SAME_TRANSACTION_REJECTED",
    "C03_SHARED_WRITER_SERIALIZES_ONLY_PAIR",
    "C04_HOST_CAPACITY_QUEUES_WITHOUT_GRAPH_EDGE",
    "C05_STALE_UNRELATED_CHILD_CANNOT_BLOCK_P0_RECOVERY",
    "C06_RETURN_BUFFERED_UNTIL_GOVERNOR_RECONCILIATION",
}
assert cases["C01_DISJOINT_TRANSACTIONS_MAY_RUN_CONCURRENTLY"]["expected"]["active_transactions"] == ["tx-a", "tx-b"]
assert cases["C02_SECOND_CHILD_IN_SAME_TRANSACTION_REJECTED"]["expected"]["rejected_child"] == "child-2"
assert cases["C03_SHARED_WRITER_SERIALIZES_ONLY_PAIR"]["expected"]["unrelated_transaction_ready"] is True
assert cases["C04_HOST_CAPACITY_QUEUES_WITHOUT_GRAPH_EDGE"]["expected"]["semantic_dependency_created"] is False
assert cases["C05_STALE_UNRELATED_CHILD_CANNOT_BLOCK_P0_RECOVERY"]["expected"]["p0_audit_state_ready"] is True
assert cases["C06_RETURN_BUFFERED_UNTIL_GOVERNOR_RECONCILIATION"]["expected"]["authority_before_reconcile"] == "NONE"
assert cases["C06_RETURN_BUFFERED_UNTIL_GOVERNOR_RECONCILIATION"]["expected"]["canonical_credit_before_reconcile"] is False
assert {case["coverage"] for case in cases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-c-fixture: ok (6/6)")
PY
