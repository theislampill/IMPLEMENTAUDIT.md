#!/usr/bin/env bash
# Deterministically exercise the issue #79 census-discipline control bank.
set -euo pipefail

fixture="${1:-fixtures/census-discipline/cases.json}"
[ -f "$fixture" ] || {
  printf 'check-census-discipline: fixture not found: %s\n' "$fixture" >&2
  exit 2
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-census-discipline: Python is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$fixture" <<'PY'
import collections
import json
import sys
from pathlib import Path


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def require_exact(value, keys, owner):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(f"{owner} keys invalid")
    return value


def nonempty_string(value):
    return type(value) is str and bool(value.strip())


def classify_enumeration(case):
    members = case["enumerated_members"]
    valid_members = (
        type(members) is list and bool(members) and
        all(nonempty_string(member) for member in members) and
        len(members) == len(set(members)))
    complete = (
        case["claim_mode"] == "census" and
        type(case["population_size"]) is int and
        type(case["examined_count"]) is int and valid_members and
        case["population_size"] == len(members) and
        case["examined_count"] == len(members))
    return "PASS" if complete else "FAIL"


def classify_distinct_hashes(case):
    rows = case["rows"]
    if type(rows) is not list or len(rows) < 2:
        return "FAIL"
    ids = []
    row_hashes = {}
    by_hash = collections.defaultdict(list)
    for row in rows:
        if type(row) is not dict or set(row) != {"id", "sha256"}:
            return "FAIL"
        if not nonempty_string(row["id"]) or not nonempty_string(row["sha256"]):
            return "FAIL"
        ids.append(row["id"])
        row_hashes[row["id"]] = row["sha256"]
        by_hash[row["sha256"]].append(row["id"])
    if len(ids) != len(set(ids)):
        return "FAIL"

    witness = case["discrimination_witness"]
    witnessed = False
    if type(witness) is dict and set(witness) == {
            "known_distinct_items", "observed_hashes"}:
        items = witness["known_distinct_items"]
        hashes = witness["observed_hashes"]
        witnessed = (
            type(items) is list and len(items) == 2 and
            len(set(items)) == 2 and all(item in row_hashes for item in items) and
            type(hashes) is list and len(hashes) == 2 and
            len(set(hashes)) == 2 and
            hashes == [row_hashes[item] for item in items])

    receipts = case["collision_receipts"]
    if type(receipts) is not list:
        return "FAIL"
    receipt_by_hash = {}
    for receipt in receipts:
        if type(receipt) is not dict or set(receipt) != {
                "sha256", "members", "reason"}:
            return "FAIL"
        if not nonempty_string(receipt["sha256"]) or \
                not nonempty_string(receipt["reason"]):
            return "FAIL"
        if type(receipt["members"]) is not list or len(receipt["members"]) < 2:
            return "FAIL"
        receipt_by_hash[receipt["sha256"]] = set(receipt["members"])

    uncovered = []
    for digest, members in by_hash.items():
        if len(members) > 1 and receipt_by_hash.get(digest) != set(members):
            uncovered.append(digest)
    if case["claims_distinct"] is not True:
        return "PASS"
    return "PASS" if witnessed and not uncovered else "FAIL"


def classify_dead_file(case):
    literal = case["literal_basename"]
    composed = case["stem_dirname"]
    move_run = case["red_first_move_run"]
    for method, owner in ((literal, "literal_basename"),
                          (composed, "stem_dirname")):
        require_exact(method, {"ran", "hits"}, owner)
        if type(method["ran"]) is not bool or type(method["hits"]) is not list:
            return "FAIL"
    require_exact(move_run, {"ran", "consumer_failed"}, "red_first_move_run")
    if type(move_run["ran"]) is not bool or \
            type(move_run["consumer_failed"]) is not bool:
        return "FAIL"

    proof_complete = (
        literal["ran"] is True and composed["ran"] is True and
        (case["suite_exists"] is False or move_run["ran"] is True))
    live_signal = bool(literal["hits"] or composed["hits"] or
                       move_run["consumer_failed"])
    warranted = "RETAIN" if live_signal else "ARCHIVE"
    return "PASS" if proof_complete and \
        case["proposed_disposition"] == warranted else "FAIL"


def classify_dismissed(case):
    anomaly = case["in_rubric_anomaly"]
    if not nonempty_string(anomaly) or case["global_verdict"] != "PASS":
        return "PASS"
    row = case["dismissed_observation"]
    complete = (
        type(row) is dict and set(row) == {"what", "why", "falsifier"} and
        all(nonempty_string(row[key]) for key in ("what", "why", "falsifier")) and
        row["what"].strip().casefold() == anomaly.strip().casefold())
    return "PASS" if complete else "FAIL"


def classify(case):
    kind = case.get("kind")
    if kind == "enumeration-authority":
        return classify_enumeration(case)
    if kind == "distinct-hash-census":
        return classify_distinct_hashes(case)
    if kind == "dead-file-proof":
        return classify_dead_file(case)
    if kind == "dismissed-observation":
        return classify_dismissed(case)
    raise ValueError(f"unsupported control kind: {kind!r}")


path = Path(sys.argv[1])
bank = json.loads(
    path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
require_exact(bank, {"schema", "controls", "phase_cases"}, "fixture bank")
if bank["schema"] != "implementaudit-census-discipline-fixtures-v1":
    raise ValueError("fixture bank schema invalid")
if type(bank["controls"]) is not list or not bank["controls"]:
    raise ValueError("controls must be a non-empty list")
if type(bank["phase_cases"]) is not list or not bank["phase_cases"]:
    raise ValueError("phase_cases must be a non-empty list")

required_ids = {
    "R6-F1", "R6-F1n", "R6-F5", "R6-F5c", "R6-F6",
    "R6-F9", "R6-F10", "R6-F11", "R6-F11n",
}
ids = [case.get("id") for case in bank["controls"]]
if set(ids) != required_ids or len(ids) != len(set(ids)):
    raise ValueError("fixture control identity set invalid")

failures = []
for case in bank["controls"]:
    actual = classify(case)
    if actual != case.get("expected"):
        failures.append(
            f"{case['id']}: expected {case.get('expected')!r}, got {actual!r}")
if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write(f"check-census-discipline: ok ({len(ids)} controls)\n")
PY
