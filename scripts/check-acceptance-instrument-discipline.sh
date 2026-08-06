#!/usr/bin/env bash
# Deterministically exercise the issue #85 acceptance/instrument control bank.
set -euo pipefail

fixture="${1:-fixtures/acceptance-instrument-discipline/cases.json}"
[ -f "$fixture" ] || {
  printf 'check-acceptance-instrument-discipline: fixture not found: %s\n' \
    "$fixture" >&2
  exit 2
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-acceptance-instrument-discipline: python is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$fixture" <<'PY'
import json
import re
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


def classify(case):
    kind = case.get("kind")
    if kind == "regex-predicate":
        matched = re.search(
            case["pattern"], case["input"], re.IGNORECASE | re.DOTALL)
        return "PASS" if matched else "FAIL"

    if kind == "prompt-independence":
        instruction = case["instruction"].casefold()
        leaked = any(
            phrase.casefold() in instruction
            for phrase in case["forbidden_instruction_phrases"])
        return "FIXTURE_DEFECT" if leaked else "PASS"

    if kind == "instrument-liveness":
        all_failed = (
            case["declared_member_count"] > 0 and
            case["pass_count"] == 0 and
            case["failure_count"] == case["declared_member_count"])
        missing_actuals = (
            not case["actuals"] or
            all(actual is None for actual in case["actuals"]))
        if all_failed and missing_actuals:
            return {
                "disposition": "ANDON",
                "class": "evidence-mismatch",
                "blocker": "instrument-suspect",
                "finding_count": 0,
            }
        return {
            "disposition": "FINDING",
            "finding_count": case["failure_count"],
        }

    if kind == "instrument-parity":
        witnessed = (
            bool(case["canned_input"]) and
            case["formal_verdict"] is not None and
            case["secondary_verdict"] is not None and
            case["formal_verdict"] == case["secondary_verdict"])
        return (
            "MAY_DRIVE_ANALYSIS_OR_REPAIR" if witnessed
            else "DIAGNOSTICS_ONLY")

    if kind == "stimulus-repair":
        complete = (
            case["repair_class"] == "STIMULUS" and
            bool(case["ambiguity_or_unsatisfiability"].strip()) and
            case["pre_repair_transcript_still_fails"] is True and
            case["held_out_negative_still_fails"] is True)
        return "PASS" if complete else "FAIL"

    raise ValueError(f"unsupported control kind: {kind!r}")


path = Path(sys.argv[1])
fixture = json.loads(
    path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
require_exact(
    fixture,
    {"schema", "controls", "phase_cases"},
    "fixture bank")
if fixture["schema"] != "implementaudit-acceptance-instrument-discipline-fixtures-v1":
    raise ValueError("fixture bank schema invalid")
if type(fixture["controls"]) is not list or not fixture["controls"]:
    raise ValueError("fixture controls must be a non-empty list")
if type(fixture["phase_cases"]) is not list or not fixture["phase_cases"]:
    raise ValueError("fixture phase_cases must be a non-empty list")

ids = []
failures = []
for index, case in enumerate(fixture["controls"]):
    if type(case) is not dict or type(case.get("id")) is not str:
        raise ValueError(f"control {index} identity invalid")
    ids.append(case["id"])
    actual = classify(case)
    if actual != case.get("expected"):
        failures.append(
            f"{case['id']}: expected {case.get('expected')!r}, got {actual!r}")

if len(ids) != len(set(ids)):
    raise ValueError("control identities duplicate")

required_ids = {
    "F1-paraphrase-must-pass",
    "F2-negation-must-fail",
    "F2n-genuine-emission",
    "F3-leaked-answer",
    "F3n-post-fix-B1",
    "F4-broken-instrument",
    "F4m-missing-actuals",
    "F4n-genuine-mismatch",
    "F5-instrument-parity",
    "F5n-parity-witness-present",
    "F6-stimulus-repair",
    "F6n-stimulus-repair-complete",
}
if set(ids) != required_ids:
    raise ValueError("fixture control identity set invalid")

required_fixtures = {
    "F1-paraphrase-must-pass": "E5c-paraphrase-control",
    "F2-negation-must-fail": "B2n-polarity-control",
    "F2n-genuine-emission": "genuine-emission",
    "F3-leaked-answer": "B1L-leak-check",
    "F3n-post-fix-B1": "post-fix-B1",
    "F4-broken-instrument": "broken-instrument",
    "F4m-missing-actuals": "broken-instrument-missing-actuals",
    "F4n-genuine-mismatch": "genuine-mismatch",
    "F5-instrument-parity": "instrument-parity",
    "F5n-parity-witness-present": "parity-witness-present",
    "F6-stimulus-repair": "stimulus-repair",
    "F6n-stimulus-repair-complete": "stimulus-repair-complete",
}
actual_fixtures = {case["id"]: case.get("fixture")
                   for case in fixture["controls"]}
if actual_fixtures != required_fixtures:
    raise ValueError("fixture family mapping invalid")

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write(
    f"check-acceptance-instrument-discipline: ok ({len(ids)} controls)\n")
PY
