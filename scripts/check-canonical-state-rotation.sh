#!/usr/bin/env bash
# R0039 F1 canonical-state rotation oracle.
#
# This checkpoint intentionally contains no rotator, pointer, marker, archive,
# receipt-v3, migration, or continuity mutation.  The fixture self-check proves
# the complete #215 four-part denominator plus independent omission/mutation
# negatives.  The default evaluates today's root-only semantics and exits RED.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cases="$repo_root/fixtures/canonical-state-rotation/cases.json"

if [ -n "${PYTHON:-}" ]; then
  python_bin="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  python_bin=python
elif command -v python3 >/dev/null 2>&1; then
  python_bin=python3
else
  printf 'check-canonical-state-rotation: Python is required\n' >&2
  exit 2
fi

exec "$python_bin" - "$cases" "$@" <<'PY'
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


EXPECTED_IDS = [
    *(f"P{i:02d}-{name}" for i, name in enumerate((
        "controller", "claim", "run-root", "audit-object", "phase-status",
        "candidate", "tree", "package", "pull-request", "release",
        "frontier-done", "frontier-active", "frontier-ready", "frontier-blocked",
        "next-action", "instruction-active", "instruction-satisfied",
        "instruction-superseded", "instruction-revoked", "instruction-expired",
        "instruction-ambiguous", "authorisation-active", "authorisation-satisfied",
        "authorisation-superseded", "authorisation-revoked", "authorisation-expired",
        "authorisation-ambiguous", "terminal-one-shots", "terminal-markers",
        "handoffs", "external-effects", "andons", "original-reds", "obligations",
        "deferrals", "nonverdicts", "evidence-ceilings", "dependencies",
        "compensations", "steers", "rollback", "runtime-artifacts", "unknown-policy",
        "unknown-frontier-policy", "unknown-instruction-policy",
        "unknown-authorisation-policy", "unknown-continuity-policy",
        "unknown-terminal-policy", "unknown-steer-policy",
    ), 1)),
    *(f"M{i:02d}-{name}" for i, name in enumerate((
        "generation-successor", "epoch-successor", "invalidation",
        "predecessor-receipt", "no-generation-reuse", "no-epoch-reuse",
        "no-invalidation-reuse", "no-predecessor-substitution",
        "no-skipped-transition", "no-reordered-transition", "dependency-order",
        "archive-before-pointer", "invalidation-after-draft", "pointer-before-receipt",
        "marker-after-receipt", "compensating-cas", "terminal-states",
        "uncertainty-stop",
    ), 1)),
    *(f"D{i:02d}-{name}" for i, name in enumerate((
        "state-hash", "roadmap-hash", "protected-manifest-hash",
        "archive-manifest-hash", "pointer-ref", "pointer-oid", "receipt-ref",
        "receipt-oid-location", "marker-ref", "marker-oid", "owner-binding",
        "next-action-binding", "future-receipt-excluded", "acyclic-bindings",
        "reader-legacy-row", "reader-invalid-legacy-row",
        "reader-first-migration-row", "reader-pointer-bad-receipt-row",
        "reader-current-row", "reader-marker-bad-receipt-row",
        "reader-marker-no-pointer-row", "reader-mismatch-row", "rehydrate-identity",
        "rehydrate-frontier", "rehydrate-obligations", "rehydrate-next-action",
        "rehydrate-evidence-burden", "zero-model-path",
    ), 1)),
    *(f"A{i:02d}-{name}" for i, name in enumerate((
        "state-preimage", "roadmap-preimage", "artifact-preimages", "typed-retrieval",
        "content-addressed", "immutable-anchor", "exact-readback", "never-current",
        "not-live-discoverable", "no-recursive-archive", "retention",
        "preimage-never-deleted",
    ), 1)),
]

CLASS_FOR_PREFIX = {
    "P": "PRESERVED_PAYLOAD",
    "M": "MONOTONIC_TRANSITION",
    "D": "DERIVED_BINDINGS",
    "A": "ARCHIVED_ONLY_HISTORY",
}


def fail(message: str, code: int = 2) -> None:
    print(f"check-canonical-state-rotation: {message}", file=sys.stderr)
    raise SystemExit(code)


def matrix_errors(rows: object) -> list[str]:
    if not isinstance(rows, list):
        return ["cases-not-list"]
    errors: list[str] = []
    ids = [row.get("id") if isinstance(row, dict) else None for row in rows]
    if ids != EXPECTED_IDS:
        missing = [item for item in EXPECTED_IDS if item not in ids]
        extra = [item for item in ids if item not in EXPECTED_IDS]
        duplicates = sorted({item for item in ids if item is not None and ids.count(item) > 1})
        errors.append(f"denominator-mismatch:missing={missing}:extra={extra}:duplicates={duplicates}")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row-{index}-not-object")
            continue
        row_id = row.get("id", f"row-{index}")
        for key in ("id", "class", "owner", "rule", "valid", "mutation", "root_only"):
            if key not in row:
                errors.append(f"{row_id}:missing-{key}")
        expected_class = CLASS_FOR_PREFIX.get(str(row_id)[:1])
        if row.get("class") != expected_class:
            errors.append(f"{row_id}:class={row.get('class')!r}:expected={expected_class!r}")
        if not isinstance(row.get("owner"), str) or not row.get("owner", "").strip():
            errors.append(f"{row_id}:owner-missing")
        if not isinstance(row.get("rule"), str) or not row.get("rule", "").strip():
            errors.append(f"{row_id}:rule-missing")
        if "valid" in row and "mutation" in row and row["valid"] == row["mutation"]:
            errors.append(f"{row_id}:mutation-not-discriminating")
    return errors


def observations(rows: list[dict[str, object]], field: str) -> dict[str, object]:
    return {
        str(row["id"]): {
            "owner": row["owner"],
            "value": copy.deepcopy(row[field]),
        }
        for row in rows
    }


def validate(rows: list[dict[str, object]], candidate: object) -> list[str]:
    if not isinstance(candidate, dict):
        return ["candidate:not-object"]
    result: list[str] = []
    expected = {str(row["id"]): row for row in rows}
    for row_id in EXPECTED_IDS:
        if row_id not in candidate:
            result.append(f"{row_id}:omission")
            continue
        observation = candidate[row_id]
        if not isinstance(observation, dict):
            result.append(f"{row_id}:malformed-observation")
            continue
        if observation.get("owner") != expected[row_id]["owner"]:
            result.append(f"{row_id}:owner-mutation")
        if observation.get("value") != expected[row_id]["valid"]:
            result.append(f"{row_id}:semantic-mutation")
        extras_for_row = sorted(set(observation) - {"owner", "value"})
        if extras_for_row:
            result.append(f"{row_id}:unknown-fields:{extras_for_row}")
    extras = sorted(set(candidate) - set(EXPECTED_IDS))
    if extras:
        result.append(f"unknown-observations:{extras}")
    return result


def load_fixture(path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load fixture {path}: {exc}")
    if not isinstance(payload, dict):
        fail("fixture root must be an object")
    if payload.get("schema") != "implementaudit.canonical-state-rotation-fixtures.v1":
        fail("wrong fixture schema")
    if payload.get("issue") != "#215":
        fail("fixture is not bound to live owner #215")
    if payload.get("semantic_owner") != "CANONICAL_CURRENT_STATE_GENERATION_TRANSACTION":
        fail("wrong semantic owner")
    rows = payload.get("cases")
    errors = matrix_errors(rows)
    if errors:
        fail("invalid matrix: " + "; ".join(errors))
    return payload, rows  # type: ignore[return-value]


def root_red(rows: list[dict[str, object]]) -> list[str]:
    root = observations(rows, "root_only")
    errors = validate(rows, root)
    if any(error.startswith("P") for error in errors):
        fail("root-only profile lost preserved payload: " + ",".join(errors))
    required_anchors = {
        "M01-generation-successor:semantic-mutation",
        "M11-dependency-order:semantic-mutation",
        "D05-pointer-ref:semantic-mutation",
        "D14-acyclic-bindings:semantic-mutation",
        "D23-rehydrate-identity:semantic-mutation",
        "A01-state-preimage:semantic-mutation",
        "A08-never-current:semantic-mutation",
        "A12-preimage-never-deleted:semantic-mutation",
    }
    if not required_anchors.issubset(errors):
        fail("root-only RED lacks required semantic anchors")
    if not any(error.startswith("M") for error in errors):
        fail("root-only profile unexpectedly satisfies transition algebra")
    if not any(error.startswith("D") for error in errors):
        fail("root-only profile unexpectedly satisfies derived bindings")
    if not any(error.startswith("A") for error in errors):
        fail("root-only profile unexpectedly satisfies archive semantics")
    return errors


def fixture_self_check(rows: list[dict[str, object]]) -> None:
    complete = observations(rows, "valid")
    complete_errors = validate(rows, complete)
    if complete_errors:
        fail("positive control failed: " + ",".join(complete_errors))

    for row in rows:
        row_id = str(row["id"])
        omitted = copy.deepcopy(complete)
        del omitted[row_id]
        got = validate(rows, omitted)
        if got != [f"{row_id}:omission"]:
            fail(f"omission control {row_id} was not independently discriminating: {got}")

        mutated = copy.deepcopy(complete)
        mutated[row_id]["value"] = copy.deepcopy(row["mutation"])
        got = validate(rows, mutated)
        if got != [f"{row_id}:semantic-mutation"]:
            fail(f"mutation control {row_id} was not independently discriminating: {got}")

        owner_mutated = copy.deepcopy(complete)
        owner_mutated[row_id]["owner"] = "substituted.owner"
        got = validate(rows, owner_mutated)
        if got != [f"{row_id}:owner-mutation"]:
            fail(f"owner mutation control {row_id} was not independently discriminating: {got}")

    # Matrix controls prove the denominator and field ownership fail closed.
    truncated = copy.deepcopy(rows[:-1])
    if not matrix_errors(truncated):
        fail("N-1 matrix negative unexpectedly passed")
    duplicate = copy.deepcopy(rows)
    duplicate[-1]["id"] = duplicate[-2]["id"]
    if not matrix_errors(duplicate):
        fail("duplicate matrix id negative unexpectedly passed")
    unknown_class = copy.deepcopy(rows)
    unknown_class[0]["class"] = "UNKNOWN"
    if not matrix_errors(unknown_class):
        fail("unknown partition negative unexpectedly passed")
    missing_owner = copy.deepcopy(rows)
    missing_owner[0]["owner"] = ""
    if not matrix_errors(missing_owner):
        fail("missing owner negative unexpectedly passed")
    multiple_owners = copy.deepcopy(rows)
    multiple_owners[0]["owner"] = ["STATE.controller", "ROADMAP.controller"]
    if not matrix_errors(multiple_owners):
        fail("multiple owners negative unexpectedly passed")
    nondiscriminating = copy.deepcopy(rows)
    nondiscriminating[0]["mutation"] = copy.deepcopy(nondiscriminating[0]["valid"])
    if not matrix_errors(nondiscriminating):
        fail("non-discriminating mutation negative unexpectedly passed")
    unknown_observation = copy.deepcopy(complete)
    unknown_observation["X01-unknown"] = {"owner": "unknown", "value": "unknown"}
    if validate(rows, unknown_observation) != ["unknown-observations:['X01-unknown']"]:
        fail("N+1 unknown observation negative unexpectedly passed")

    errors = root_red(rows)
    class_counts = {
        cls: sum(1 for row in rows if row["class"] == cls)
        for cls in CLASS_FOR_PREFIX.values()
    }
    print(
        "CANONICAL_STATE_ROTATION_FIXTURE_SELF_CHECK=PASS "
        f"denominator={len(rows)} omission={len(rows)} mutation={len(rows)} "
        f"owner-mutation={len(rows)} "
        f"root-semantic-red={len(errors)} partitions={json.dumps(class_counts, sort_keys=True, separators=(',', ':'))}"
    )


def candidate_from_file(path: Path) -> object:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load candidate {path}: {exc}")
    if not isinstance(payload, dict) or payload.get("schema") != "implementaudit.canonical-state-rotation-candidate.v1":
        fail("candidate must use implementaudit.canonical-state-rotation-candidate.v1")
    return payload.get("observations")


fixture_path = Path(sys.argv[1])
args = sys.argv[2:]
_, rows = load_fixture(fixture_path)

if args == ["--fixture-self-check"]:
    fixture_self_check(rows)
    raise SystemExit(0)

if args == ["--assert-root-red"]:
    errors = root_red(rows)
    print(
        "CANONICAL_STATE_ROTATION_ROOT_RED_SELF_CHECK=PASS "
        f"semantic-failures={len(errors)} preserved-payload=49/49"
    )
    raise SystemExit(0)

if len(args) == 2 and args[0] == "--candidate":
    errors = validate(rows, candidate_from_file(Path(args[1])))
    if errors:
        print("CANONICAL_STATE_ROTATION_CANDIDATE=FAIL " + ",".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"CANONICAL_STATE_ROTATION_CANDIDATE=PASS denominator={len(rows)}")
    raise SystemExit(0)

if args:
    fail("usage: check-canonical-state-rotation.sh [--fixture-self-check|--assert-root-red|--candidate PATH]")

errors = root_red(rows)
print(
    "CANONICAL_STATE_ROTATION_RED=ROOT_ONLY_NOT_EQUIVALENT "
    f"semantic-failures={len(errors)} preserved-payload=49/49 "
    "missing-equivalence=transition,pointer+marker+v3,archive,rehydration",
    file=sys.stderr,
)
print("CANONICAL_STATE_ROTATION_RED_IDS=" + ",".join(errors), file=sys.stderr)
raise SystemExit(1)
PY
