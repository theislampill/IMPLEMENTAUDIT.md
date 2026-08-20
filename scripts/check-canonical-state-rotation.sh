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
import hashlib
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
        "rehydrate-evidence-burden", "zero-model-path", "expected-receipt-schema",
    ), 1)),
    *(f"A{i:02d}-{name}" for i, name in enumerate((
        "state-preimage", "roadmap-preimage", "artifact-preimages", "typed-retrieval",
        "content-addressed", "immutable-anchor", "exact-readback", "never-current",
        "not-live-discoverable", "no-recursive-archive", "retention",
        "preimage-never-deleted", "superseded-generation", "superseded-receipt",
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


def canonical_sha256(value: object) -> str:
    preimage = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()


def leaf_paths(value: object, prefix: tuple[object, ...] = ()) -> list[tuple[object, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key in sorted(value)
            for path in leaf_paths(value[key], prefix + (key,))
        ]
    if isinstance(value, list):
        return [
            path
            for index, item in enumerate(value)
            for path in leaf_paths(item, prefix + (index,))
        ]
    return [prefix]


def mutate_leaf(value: object, path: tuple[object, ...]) -> None:
    parent = value
    for part in path[:-1]:
        parent = parent[part]  # type: ignore[index]
    leaf = parent[path[-1]]  # type: ignore[index]
    if isinstance(leaf, bool):
        replacement: object = not leaf
    elif isinstance(leaf, int):
        replacement = leaf + 1
    elif isinstance(leaf, str):
        replacement = leaf + "-held-out-mutation"
    elif leaf is None:
        replacement = "held-out-mutation"
    else:
        fail(f"unsupported calibration leaf type at {path}: {type(leaf).__name__}")
    parent[path[-1]] = replacement  # type: ignore[index]


def trigger_controls(calibration: object) -> dict[str, object]:
    if not isinstance(calibration, dict):
        fail("trigger_calibration must be an object")
    if set(calibration) != {
        "schema", "population_id", "canonicalization", "population_sha256", "bound"
    }:
        fail("trigger_calibration fields drifted")
    if calibration.get("schema") != "implementaudit.canonical-state-rotation-calibration.v1":
        fail("wrong trigger calibration schema")
    if calibration.get("population_id") != "R0039-F1-CAL-v2":
        fail("calibration population identity drifted")
    if calibration.get("canonicalization") != "utf8-json-sort-keys-no-whitespace-v1":
        fail("calibration canonicalization identity drifted")
    bound = calibration.get("bound")
    if not isinstance(bound, dict):
        fail("calibration bound population must be an object")
    if set(bound) != {
        "admission_formula", "thresholds", "tokenizer", "host",
        "minimum_payoff", "maximum_runtime", "maximum_memory", "storage", "cases",
    }:
        fail("calibration bound population fields drifted")
    population_sha256 = calibration.get("population_sha256")
    if not isinstance(population_sha256, str) or len(population_sha256) != 64:
        fail("calibration population SHA-256 is malformed")
    if canonical_sha256(bound) != population_sha256:
        fail("calibration population digest does not bind its canonical content")

    thresholds = bound.get("thresholds")
    if not isinstance(thresholds, dict) or set(thresholds) != {
        "bytes", "tokens", "context_health"
    }:
        fail("calibration thresholds are incomplete")
    byte = thresholds["bytes"]
    token = thresholds["tokens"]
    context = thresholds["context_health"]
    tokenizer = bound.get("tokenizer")
    host = bound.get("host")
    payoff = bound.get("minimum_payoff")
    runtime = bound.get("maximum_runtime")
    memory = bound.get("maximum_memory")
    storage = bound.get("storage")
    cases = bound.get("cases")

    if bound.get("admission_formula") != (
        "bytes>=threshold OR tokens>=threshold OR context-health<=threshold"
    ):
        fail("trigger admission formula is not the exact any-boundary contract")
    if byte != {"value": 131072, "unit": "UTF-8-bytes"}:
        fail("byte threshold identity drifted")
    if token != {"value": 32768, "unit": "tokens"}:
        fail("token threshold identity drifted")
    if context != {
        "value": 2500,
        "unit": "remaining-context-basis-points",
        "direction": "at-or-below",
    }:
        fail("context-health threshold identity drifted")
    if tokenizer != {
        "name": "cl100k_base",
        "implementation": "tiktoken",
        "version": "0.12.0",
    }:
        fail("tokenizer name implementation or version is unbound")
    if host != {"host": "codex-desktop", "version": "2026-08-20"}:
        fail("host or version is unbound")
    if payoff != {"live_bytes_reduction": 32768, "reentry_token_reduction": 8192}:
        fail("minimum payoff identity drifted")
    if runtime != {"value": 5000, "unit": "milliseconds"}:
        fail("maximum runtime identity drifted")
    if memory != {"value": 67108864, "unit": "bytes"}:
        fail("maximum memory identity drifted")
    if storage != {
        "content_addressed": True,
        "deduplicated": True,
        "cumulative_measured": True,
        "budget_excess": "OWNER_DECISION_NO_DELETE",
    }:
        fail("storage measurement or owner-decision contract drifted")
    if not isinstance(cases, list) or len(cases) != 2:
        fail("calibration population must contain exactly two cases")
    if [case.get("id") if isinstance(case, dict) else None for case in cases] != [
        "large-root-positive", "below-threshold"
    ]:
        fail("calibration case identities or order drifted")

    case_by_id: dict[str, dict[str, object]] = {}
    expected_case_fields = {"id", "input", "result"}
    expected_input_fields = {"bytes", "tokens", "context_health_bp"}
    expected_result_fields = {
        "trigger", "payoff", "runtime", "memory", "archive_writes", "model_calls",
        "extra_ceremony", "manifest", "two_clean_roots",
    }
    for case in cases:
        if not isinstance(case, dict) or set(case) != expected_case_fields:
            fail("calibration case fields drifted")
        sample = case.get("input")
        result = case.get("result")
        if not isinstance(sample, dict) or set(sample) != expected_input_fields:
            fail(f"{case.get('id')} input fields drifted")
        if not isinstance(result, dict) or set(result) != expected_result_fields:
            fail(f"{case.get('id')} result fields drifted")
        case_by_id[str(case["id"])] = case

    large = case_by_id["large-root-positive"]
    below = case_by_id["below-threshold"]
    large_input = large["input"]
    below_input = below["input"]
    large_result = large["result"]
    below_result = below["result"]
    assert isinstance(large_input, dict) and isinstance(below_input, dict)
    assert isinstance(large_result, dict) and isinstance(below_result, dict)

    byte_limit = int(byte["value"])  # type: ignore[index]
    token_limit = int(token["value"])  # type: ignore[index]
    context_limit = int(context["value"])  # type: ignore[index]

    def admitted(sample: dict[str, object]) -> bool:
        return (
            int(sample["bytes"]) >= byte_limit
            or int(sample["tokens"]) >= token_limit
            or int(sample["context_health_bp"]) <= context_limit
        )

    if large_input != {"bytes": 131073, "tokens": 32769, "context_health_bp": 2499}:
        fail("pinned large-root input drifted")
    if not admitted(large_input) or large_result.get("trigger") != "TRIGGER":
        fail("pinned large-root positive did not trigger")
    if below_input != {"bytes": 131071, "tokens": 32767, "context_health_bp": 2501}:
        fail("pinned below-threshold input drifted")
    if admitted(below_input) or below_result.get("trigger") != "NO_TRIGGER":
        fail("pinned below-threshold case did not retain the cheap path")

    # Held-out boundary controls independently discriminate every admission leg.
    boundary_samples = (
        {"bytes": byte_limit, "tokens": token_limit - 1, "context_health_bp": context_limit + 1},
        {"bytes": byte_limit - 1, "tokens": token_limit, "context_health_bp": context_limit + 1},
        {"bytes": byte_limit - 1, "tokens": token_limit - 1, "context_health_bp": context_limit},
    )
    if not all(admitted(sample) for sample in boundary_samples):
        fail("an exact byte token or context-health boundary did not trigger")
    if admitted({
        "bytes": byte_limit - 1,
        "tokens": token_limit - 1,
        "context_health_bp": context_limit + 1,
    }):
        fail("all-below-boundary held-out negative unexpectedly triggered")

    cheap = {
        "archive": below_result.get("archive_writes"),
        "model": below_result.get("model_calls"),
        "extra_ceremony": below_result.get("extra_ceremony"),
    }
    if cheap != {"archive": 0, "model": 0, "extra_ceremony": 0}:
        fail("below-threshold cheap path acquired archive model or ceremony effects")
    if below_result.get("payoff") != {
        "live_bytes_reduction": 0, "reentry_token_reduction": 0
    }:
        fail("below-threshold cheap path acquired measured payoff")
    if below_result.get("runtime") != {"value": 0, "unit": "milliseconds"}:
        fail("below-threshold cheap path acquired runtime overhead")
    if below_result.get("memory") != {"value": 0, "unit": "bytes"}:
        fail("below-threshold cheap path acquired memory overhead")
    if below_result.get("manifest") != "NOT_TRIGGERED":
        fail("below-threshold cheap path acquired a rotation manifest")
    if below_result.get("two_clean_roots") != "BYTE_IDENTICAL_NO_TRIGGER_DECISION":
        fail("two-clean-root cheap-path equivalence is absent")
    if large_result.get("archive_writes") != 1 or large_result.get("model_calls") != 0:
        fail("large-root positive archive or zero-model result drifted")
    if large_result.get("extra_ceremony") != 1:
        fail("large-root positive rotation ceremony result drifted")
    if large_result.get("two_clean_roots") != "BYTE_IDENTICAL_TRIGGER_DECISION":
        fail("two-clean-root trigger equivalence is absent")
    if large_result.get("manifest") != "COMPLETE_ORACLE_DENOMINATOR":
        fail("large-root positive does not bind the complete denominator")

    observed_payoff = large_result.get("payoff")
    observed_runtime = large_result.get("runtime")
    observed_memory = large_result.get("memory")
    if not isinstance(observed_payoff, dict) or (
        int(observed_payoff["live_bytes_reduction"])
        < int(payoff["live_bytes_reduction"])  # type: ignore[index]
        or int(observed_payoff["reentry_token_reduction"])
        < int(payoff["reentry_token_reduction"])  # type: ignore[index]
    ):
        fail("large-root positive did not meet the minimum measured payoff")
    if not isinstance(observed_runtime, dict) or (
        observed_runtime.get("unit") != runtime["unit"]  # type: ignore[index]
        or int(observed_runtime["value"]) > int(runtime["value"])  # type: ignore[index]
    ):
        fail("large-root positive exceeded the maximum runtime")
    if not isinstance(observed_memory, dict) or (
        observed_memory.get("unit") != memory["unit"]  # type: ignore[index]
        or int(observed_memory["value"]) > int(memory["value"])  # type: ignore[index]
    ):
        fail("large-root positive exceeded the maximum memory")

    paths = leaf_paths(bound)
    changed = 0
    for path in paths:
        mutant = copy.deepcopy(bound)
        mutate_leaf(mutant, path)
        if canonical_sha256(mutant) == population_sha256:
            fail(f"bound-field digest mutation was not discriminating at {path}")
        changed += 1

    return {
        "byte": byte_limit,
        "token": token_limit,
        "context": context_limit,
        "population_sha256": population_sha256,
        "digest_mutations": changed,
        "digest_fields": len(paths),
        **cheap,
    }


def fixture_self_check(
    rows: list[dict[str, object]], calibration: object
) -> None:
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

    # Calibration is independently bounded and must not enlarge or burden the
    # four protected-state partitions consumed by projection and rehydration.
    trigger_controls(calibration)
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
payload, rows = load_fixture(fixture_path)
calibration = payload.get("trigger_calibration")

if args == ["--fixture-self-check"]:
    fixture_self_check(rows, calibration)
    raise SystemExit(0)

if args == ["--trigger-self-check"]:
    trigger = trigger_controls(calibration)
    print(
        "CANONICAL_STATE_ROTATION_TRIGGER_SELF_CHECK=PASS "
        "large-root=TRIGGER below-threshold=NO_TRIGGER "
        f"archive={trigger['archive']} model={trigger['model']} "
        f"extra-ceremony={trigger['extra_ceremony']} "
        f"thresholds=bytes:{trigger['byte']},tokens:{trigger['token']},"
        f"context-health-bp:{trigger['context']} "
        f"population-sha256={trigger['population_sha256']} "
        f"digest-mutations={trigger['digest_mutations']}/{trigger['digest_fields']}"
    )
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
    fail("usage: check-canonical-state-rotation.sh [--fixture-self-check|--trigger-self-check|--assert-root-red|--candidate PATH]")

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
