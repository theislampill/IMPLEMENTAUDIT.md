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
f2_cases="$repo_root/fixtures/canonical-state-rotation/f2-draft-archive.json"
f3_cases="$repo_root/fixtures/canonical-state-rotation/f3-reader-matrix.json"
event_byte_cases="$repo_root/fixtures/canonical-state-rotation/event-byte-cases.json"
query_cursor_cases="$repo_root/fixtures/canonical-state-rotation/query-cursor-cases.json"
sequence_cas_cases="$repo_root/fixtures/canonical-state-rotation/sequence-cas-cases.json"

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

exec "$python_bin" - "$cases" "$f2_cases" "$f3_cases" "$event_byte_cases" "$query_cursor_cases" "$sequence_cas_cases" "$@" <<'PY'
from __future__ import annotations

import copy
import hashlib
import json
import re
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


def f2_residual_red(rows: list[dict[str, object]]) -> list[str]:
    candidate = observations(rows, "root_only")
    for row in rows:
        if str(row["id"]).startswith("A"):
            candidate[str(row["id"])]["value"] = copy.deepcopy(row["valid"])
    errors = validate(rows, candidate)
    if len(errors) != 44:
        fail(f"F2 residual RED count drifted: {len(errors)}")
    if any(error.startswith("P") or error.startswith("A") for error in errors):
        fail("F2 residual lost payload or retained a completed archive RED")
    required_anchors = {
        "M01-generation-successor:semantic-mutation",
        "M11-dependency-order:semantic-mutation",
        "D05-pointer-ref:semantic-mutation",
        "D14-acyclic-bindings:semantic-mutation",
        "D23-rehydrate-identity:semantic-mutation",
    }
    if not required_anchors.issubset(errors):
        fail("F2 residual RED lacks a later-cell semantic anchor")
    return errors


def f3_residual_red(rows: list[dict[str, object]]) -> list[str]:
    candidate = observations(rows, "root_only")
    for row in rows:
        row_id = str(row["id"])
        if row_id.startswith("A") or row_id in {
            "D15-reader-legacy-row",
            "D16-reader-invalid-legacy-row",
            "D17-reader-first-migration-row",
            "D18-reader-pointer-bad-receipt-row",
            "D19-reader-current-row",
            "D20-reader-marker-bad-receipt-row",
            "D21-reader-marker-no-pointer-row",
            "D22-reader-mismatch-row",
        }:
            candidate[row_id]["value"] = copy.deepcopy(row["valid"])
    errors = validate(rows, candidate)
    if len(errors) != 37:
        fail(f"F3 residual RED count drifted: {len(errors)}")
    if any(
        error.startswith("P")
        or error.startswith("A")
        or error.startswith(tuple(f"D{number:02d}" for number in range(15, 23)))
        for error in errors
    ):
        fail("F3 residual lost payload/archive or retained a completed reader RED")
    required_anchors = {
        "M01-generation-successor:semantic-mutation",
        "M11-dependency-order:semantic-mutation",
        "D05-pointer-ref:semantic-mutation",
        "D14-acyclic-bindings:semantic-mutation",
        "D23-rehydrate-identity:semantic-mutation",
    }
    if not required_anchors.issubset(errors):
        fail("F3 residual RED lacks a later-cell semantic anchor")
    return errors


def load_f2_fixture(path: Path) -> dict[str, object]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load F2 fixture {path}: {exc}")
    if not isinstance(fixture, dict) or set(fixture) != {
        "schema", "controller", "generation", "archive_ref", "protected_files",
        "forbidden_source_components", "forbidden_transition_fields", "expected",
    }:
        fail("F2 fixture fields drifted")
    if fixture.get("schema") != "implementaudit.canonical-state-rotation-f2-fixture.v1":
        fail("wrong F2 fixture schema")
    if fixture.get("controller") != "v0333-release" or fixture.get("generation") != "g0008":
        fail("F2 controller or generation identity drifted")
    if fixture.get("archive_ref") != "refs/implementaudit/state-archives/v0333-release/g0008":
        fail("F2 archive ref identity drifted")
    if fixture.get("protected_files") != [
        {"role": "STATE", "path": "STATE.md"},
        {"role": "ROADMAP", "path": "ROADMAP.md"},
        {"role": "WORK_GRAPH", "path": "WORK_GRAPH.json"},
    ]:
        fail("F2 protected-file population drifted")
    if fixture.get("forbidden_source_components") != [
        "state-generations", "state-archives", "quarantine"
    ]:
        fail("F2 recursive-population exclusions drifted")
    forbidden = fixture.get("forbidden_transition_fields")
    if forbidden != [
        "current_generation", "epoch", "invalidation_oid", "migration_marker",
        "pointer_oid", "predecessor_receipt", "receipt_oid",
    ]:
        fail("F2 transition-envelope exclusions drifted")
    if fixture.get("expected") != {
        "draft_schema": "implementaudit.canonical-state-projection-draft.v1",
        "archive_schema": "implementaudit.canonical-state-archive.v1",
        "archive_ref_update": "EXPECTED_ZERO_CAS",
        "discovery": "EXCLUDED",
        "recursive_population": "EXCLUDED",
        "retrieval": "GIT_BLOB_OID_AND_SHA256",
        "permissions": "SOURCE_MODE_EXACT_READBACK",
    }:
        fail("F2 expected results drifted")
    return fixture


def load_f3_fixture(path: Path) -> dict[str, object]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load F3 fixture {path}: {exc}")
    if not isinstance(fixture, dict) or set(fixture) != {
        "schema", "controller", "pointer_ref", "marker_ref", "cases",
    }:
        fail("F3 fixture fields drifted")
    if fixture.get("schema") != "implementaudit.canonical-state-rotation-f3-reader-matrix.v1":
        fail("wrong F3 fixture schema")
    controller = fixture.get("controller")
    if controller != "reader-controller":
        fail("F3 fixture controller drifted")
    if fixture.get("pointer_ref") != f"refs/implementaudit/current-generations/{controller}":
        fail("F3 pointer ref drifted")
    if fixture.get("marker_ref") != f"refs/implementaudit/current-generation-migrations/{controller}":
        fail("F3 marker ref drifted")
    cases = fixture.get("cases")
    if not isinstance(cases, list) or len(cases) != 24:
        fail("F3 reader matrix denominator drifted")
    ids: list[str] = []
    results: dict[str, int] = {}
    mutations: set[str] = set()
    for row in cases:
        if not isinstance(row, dict) or set(row) != {
            "id", "marker", "pointer", "receipt", "owner_mutation", "expected",
        }:
            fail("F3 reader matrix row fields drifted")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not re.fullmatch(r"[LPCM][0-9]{2}", row_id):
            fail("F3 reader matrix row identity is malformed")
        ids.append(row_id)
        if row.get("marker") not in {"absent", "valid", "malformed"}:
            fail(f"F3 marker state drifted: {row_id}")
        if row.get("pointer") not in {"absent", "valid", "malformed"}:
            fail(f"F3 pointer state drifted: {row_id}")
        if row.get("receipt") not in {
            "absent", "exact-v1", "exact-v2", "invalidated-v2", "mismatched-v2",
            "exact-v3", "stale-v3", "mismatched-v3",
        }:
            fail(f"F3 receipt state drifted: {row_id}")
        mutation = row.get("owner_mutation")
        if mutation not in {
            "none", "controller", "claim", "run", "pointer-schema",
            "marker-schema", "receipt-schema",
        }:
            fail(f"F3 owner/schema mutation drifted: {row_id}")
        mutations.add(str(mutation))
        expected = str(row.get("expected"))
        if expected not in {
            "LEGACY_COMPATIBILITY", "FIRST_MIGRATION_INCOMPLETE",
            "POINTER_CURRENT", "STOP", "STOP_NO_ROOT_FALLBACK",
        }:
            fail(f"F3 expected result drifted: {row_id}")
        results[expected] = results.get(expected, 0) + 1
    if len(set(ids)) != 24 or ids != [
        *(f"L{i:02d}" for i in range(1, 6)),
        *(f"P{i:02d}" for i in range(1, 6)),
        *(f"C{i:02d}" for i in range(1, 6)),
        *(f"M{i:02d}" for i in range(1, 10)),
    ]:
        fail("F3 reader matrix identities or ordering drifted")
    if results != {
        "LEGACY_COMPATIBILITY": 1,
        "FIRST_MIGRATION_INCOMPLETE": 1,
        "POINTER_CURRENT": 1,
        "STOP": 19,
        "STOP_NO_ROOT_FALLBACK": 2,
    }:
        fail("F3 reader matrix result population drifted")
    if mutations != {
        "none", "controller", "claim", "run", "pointer-schema",
        "marker-schema", "receipt-schema",
    }:
        fail("F3 owner/schema mutation coverage drifted")
    return fixture


def load_clarification_fixture(
    path: Path,
    schema: str,
    expected_cases: list[tuple[str, str]],
) -> dict[str, object]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load clarification fixture {path}: {exc}")
    if not isinstance(fixture, dict) or set(fixture) != {"schema", "cases"}:
        fail(f"clarification fixture fields drifted: {path.name}")
    if fixture.get("schema") != schema:
        fail(f"clarification fixture schema drifted: {path.name}")
    cases = fixture.get("cases")
    if not isinstance(cases, list):
        fail(f"clarification fixture cases are not a list: {path.name}")
    observed_cases: list[tuple[str, str]] = []
    for row in cases:
        if not isinstance(row, dict) or set(row) != {"id", "expect"}:
            fail(f"clarification fixture row fields drifted: {path.name}")
        row_id, expectation = row.get("id"), row.get("expect")
        if not isinstance(row_id, str) or not isinstance(expectation, str):
            fail(f"clarification fixture row types drifted: {path.name}")
        observed_cases.append((row_id, expectation))
    if observed_cases != expected_cases:
        fail(f"clarification fixture population drifted: {path.name}")
    return fixture


def clarification_fixture_self_check(
    event_byte_path: Path,
    query_cursor_path: Path,
    sequence_cas_path: Path,
) -> None:
    event_bytes = load_clarification_fixture(
        event_byte_path,
        "implementaudit.canonical-state-rotation-event-byte-cases.v1",
        [
            ("EB01-key-order", "ACCEPT"),
            ("EB02-no-terminal-lf", "ACCEPT"),
            ("EB03-utf8-no-bom", "ACCEPT"),
            ("EB04-unicode-preserved", "ACCEPT"),
            ("EB05-float-rejected", "REJECT"),
            ("EB06-int64-boundary", "ACCEPT"),
            ("EB07-windows-posix-path-converges", "ACCEPT"),
            ("EB08-case-remains-semantic", "ACCEPT"),
            ("EB09-host-bound-requires-host-identity", "REJECT"),
            ("EB10-posix-literal-backslash-distinct", "ACCEPT"),
            ("EB11-caller-source-fields-rejected", "REJECT"),
            ("EB12-posix-trailing-backslash-is-data", "ACCEPT"),
            ("EB13-owner-manifest-context-mismatch", "REJECT"),
            ("EB14-event-extra-key-rejected", "REJECT"),
            ("EB15-event-missing-key-rejected", "REJECT"),
            ("EB16-self-hashed-source-absent-owner-manifest", "REJECT"),
            ("EB17-wrong-owner-manifest-ref", "REJECT"),
            ("EB18-wrong-owner-run-controller", "REJECT"),
            ("EB19-unknown-source-evidence-id", "REJECT"),
            ("EB20-stored-source-evidence-revalidated", "ACCEPT"),
        ],
    )
    cursor = load_clarification_fixture(
        query_cursor_path,
        "implementaudit.canonical-state-rotation-query-cursor-cases.v1",
        [
            ("QC01-valid", "ACCEPT"),
            ("QC02-wrong-version", "REJECT"),
            ("QC03-wrong-generation", "REJECT"),
            ("QC04-wrong-manifest", "REJECT"),
            ("QC05-wrong-filters", "REJECT"),
            ("QC06-stale-position", "REJECT"),
            ("QC07-malformed-digest", "REJECT"),
            ("QC08-recomputed-skip-is-nondecision", "NONDECISION"),
        ],
    )
    sequence_cas = load_clarification_fixture(
        sequence_cas_path,
        "implementaudit.canonical-state-rotation-sequence-cas-cases.v1",
        [
            ("SC01-single-winner", "WINNER"),
            ("SC02-loser-not-queryable", "NOT_QUERYABLE"),
            ("SC03-loser-not-current", "NOT_CURRENT"),
            ("SC04-retry-reallocates", "RETRY_REALLOCATED"),
            ("SC05-winner-data-preserved", "PRESERVED"),
            ("SC06-reused-predecessor-sequence", "REJECT"),
            ("SC07-noncontiguous-gap", "REJECT"),
            ("SC08-wrong-predecessor-high-water", "REJECT"),
            ("SC09-other-predecessor-manifest", "REJECT"),
            ("SC10-pointer-manifest-type-confusion", "REJECT"),
        ],
    )
    print(
        "CANONICAL_STATE_ROTATION_CLARIFICATIONS_FIXTURE_SELF_CHECK=PASS "
        f"event-bytes={len(event_bytes['cases'])} cursor={len(cursor['cases'])} "
        f"sequence-cas={len(sequence_cas['cases'])}"
    )


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
f2_fixture_path = Path(sys.argv[2])
f3_fixture_path = Path(sys.argv[3])
event_byte_fixture_path = Path(sys.argv[4])
query_cursor_fixture_path = Path(sys.argv[5])
sequence_cas_fixture_path = Path(sys.argv[6])
args = sys.argv[7:]
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

if args == ["--f2-fixture-self-check"]:
    f2_fixture = load_f2_fixture(f2_fixture_path)
    print(
        "CANONICAL_STATE_ROTATION_F2_FIXTURE_SELF_CHECK=PASS "
        f"files={len(f2_fixture['protected_files'])} "
        f"transition-fields={len(f2_fixture['forbidden_transition_fields'])} "
        "traversal=REJECTED recursive=EXCLUDED"
    )
    raise SystemExit(0)

if args == ["--assert-f2-residual-red"]:
    errors = f2_residual_red(rows)
    print(
        "CANONICAL_STATE_ROTATION_RED=F2_DRAFT_ARCHIVE_ONLY_NOT_EQUIVALENT "
        f"semantic-failures={len(errors)} preserved-payload=49/49 "
        "missing-equivalence=transition,pointer+marker+v3,rehydration",
        file=sys.stderr,
    )
    print("CANONICAL_STATE_ROTATION_RED_IDS=" + ",".join(errors), file=sys.stderr)
    raise SystemExit(1)

if args == ["--f3-fixture-self-check"]:
    f3_fixture = load_f3_fixture(f3_fixture_path)
    print(
        "CANONICAL_STATE_ROTATION_F3_FIXTURE_SELF_CHECK=PASS "
        f"cases={len(f3_fixture['cases'])} legacy=1 first-migration=1 "
        "pointer-current=1 stop=19 stop-no-root-fallback=2 "
        "owner-schema-mutations=6"
    )
    raise SystemExit(0)

if args == ["--clarification-fixtures-self-check"]:
    clarification_fixture_self_check(
        event_byte_fixture_path,
        query_cursor_fixture_path,
        sequence_cas_fixture_path,
    )
    raise SystemExit(0)

if args == ["--assert-f3-residual-red"]:
    errors = f3_residual_red(rows)
    print(
        "CANONICAL_STATE_ROTATION_RED=F3_READERS_ONLY_NOT_EQUIVALENT "
        f"semantic-failures={len(errors)} preserved-payload=49/49 "
        "missing-equivalence=transition,pointer+marker+v3-publication,rehydration",
        file=sys.stderr,
    )
    print("CANONICAL_STATE_ROTATION_RED_IDS=" + ",".join(errors), file=sys.stderr)
    raise SystemExit(1)

if len(args) == 2 and args[0] == "--candidate":
    errors = validate(rows, candidate_from_file(Path(args[1])))
    if errors:
        print("CANONICAL_STATE_ROTATION_CANDIDATE=FAIL " + ",".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"CANONICAL_STATE_ROTATION_CANDIDATE=PASS denominator={len(rows)}")
    raise SystemExit(0)

if args:
    fail("usage: check-canonical-state-rotation.sh [--fixture-self-check|--trigger-self-check|--assert-root-red|--f2-fixture-self-check|--assert-f2-residual-red|--f3-fixture-self-check|--assert-f3-residual-red|--clarification-fixtures-self-check|--candidate PATH]")

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
