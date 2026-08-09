#!/usr/bin/env python3
"""Evaluate the deterministic R33 semantic-preservation fixture bank."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class FixtureError(ValueError):
    """Raised when a fixture does not satisfy the R33 test schema."""


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FixtureError(f"{label} must be an object")
    return value


def require_bool(mapping: dict[str, Any], key: str, label: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise FixtureError(f"{label}.{key} must be boolean")
    return value


def require_string(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{label}.{key} must be a non-empty string")
    return value


def validate_case(case: Any, index: int) -> dict[str, Any]:
    row = require_mapping(case, f"cases[{index}]")
    label = f"case {require_string(row, 'id', f'cases[{index}]')}"
    require_bool(row, "package_pressure", label)

    change = require_mapping(row.get("change"), f"{label}.change")
    for key in ("shipped_content", "owner_location", "consumer_route"):
        require_bool(change, key, f"{label}.change")
    proof = require_string(change, "non_semantic_proof", f"{label}.change")
    if proof not in {"none", "extracted-equal", "whitespace-dedup"}:
        raise FixtureError(f"{label}.change.non_semantic_proof is unsupported")

    package = require_mapping(row.get("package"), f"{label}.package")
    for key in ("extracted_members_equal", "unresolved_fit_conflict"):
        require_bool(package, key, f"{label}.package")

    evaluator = require_mapping(row.get("evaluator"), f"{label}.evaluator")
    for key in (
        "changed_after_failure",
        "independent_justification",
        "underlying_property_passes",
    ):
        require_bool(evaluator, key, f"{label}.evaluator")

    split = require_mapping(row.get("progressive_split"), f"{label}.progressive_split")
    for key in (
        "applies",
        "owner_shipped",
        "same_run_dispatch",
        "public_projection_required",
        "public_projection_preserved",
    ):
        require_bool(split, key, f"{label}.progressive_split")

    behaviours = row.get("behaviours")
    if not isinstance(behaviours, list):
        raise FixtureError(f"{label}.behaviours must be an array")
    for behaviour_index, behaviour_value in enumerate(behaviours):
        behaviour_label = f"{label}.behaviours[{behaviour_index}]"
        behaviour = require_mapping(behaviour_value, behaviour_label)
        require_string(behaviour, "predicate_id", behaviour_label)
        require_string(behaviour, "owner", behaviour_label)
        require_bool(behaviour, "owner_shipped", behaviour_label)
        require_bool(behaviour, "after_satisfied", behaviour_label)

        literal = require_mapping(behaviour.get("literal"), f"{behaviour_label}.literal")
        literal_class = require_string(literal, "class", f"{behaviour_label}.literal")
        if literal_class not in {"semantic", "exact"}:
            raise FixtureError(f"{behaviour_label}.literal.class is unsupported")
        require_bool(literal, "changed", f"{behaviour_label}.literal")
        require_bool(literal, "reauthorised", f"{behaviour_label}.literal")

        consumers = behaviour.get("consumers")
        if not isinstance(consumers, list) or not consumers:
            raise FixtureError(f"{behaviour_label}.consumers must be a non-empty array")
        for consumer_index, consumer_value in enumerate(consumers):
            consumer_label = f"{behaviour_label}.consumers[{consumer_index}]"
            consumer = require_mapping(consumer_value, consumer_label)
            require_string(consumer, "kind", consumer_label)
            for key in ("required", "reachable", "held_out_passes"):
                require_bool(consumer, key, consumer_label)

    expected = require_mapping(row.get("expected"), f"{label}.expected")
    require_bool(expected, "triggered", f"{label}.expected")
    require_string(expected, "disposition", f"{label}.expected")
    require_string(expected, "reason_code", f"{label}.expected")
    return row


def behaviour_failure(case: dict[str, Any]) -> tuple[str, str] | None:
    for behaviour in case["behaviours"]:
        if not behaviour["owner_shipped"]:
            return "FAIL", "required-owner-unshipped"

        literal = behaviour["literal"]
        if literal["class"] == "exact" and literal["changed"] and not literal["reauthorised"]:
            return "FAIL", "exact-literal-owner-changed"

        if not behaviour["after_satisfied"]:
            return "FAIL", "governed-predicate-lost"

        for consumer in behaviour["consumers"]:
            if not consumer["required"]:
                continue
            if not consumer["reachable"]:
                return "FAIL", "required-consumer-unreachable"
            if not consumer["held_out_passes"]:
                return "FAIL", "held-out-consumer-fails"
    return None


def classify(case: dict[str, Any]) -> dict[str, Any]:
    evaluator = case["evaluator"]
    change = case["change"]
    package = case["package"]
    split = case["progressive_split"]

    if not case["package_pressure"]:
        return {
            "triggered": False,
            "disposition": "NOT_TRIGGERED",
            "reason_code": "ordinary-non-package-work",
        }

    if evaluator["changed_after_failure"]:
        if not evaluator["independent_justification"]:
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "evaluator-change-unjustified",
            }
        if not evaluator["underlying_property_passes"]:
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "underlying-property-still-fails",
            }

    failure = behaviour_failure(case)
    if failure:
        disposition, reason_code = failure
        return {"triggered": True, "disposition": disposition, "reason_code": reason_code}

    if not evaluator["underlying_property_passes"]:
        return {
            "triggered": True,
            "disposition": "FAIL",
            "reason_code": "underlying-property-still-fails",
        }

    if (
        change["non_semantic_proof"] == "extracted-equal"
        and not evaluator["changed_after_failure"]
    ):
        if not package["extracted_members_equal"]:
            raise FixtureError(
                f"case {case['id']} claims extracted equality but package evidence disagrees"
            )
        return {
            "triggered": False,
            "disposition": "PASS_MECHANICAL",
            "reason_code": "extracted-members-equal",
        }

    if (
        change["non_semantic_proof"] == "whitespace-dedup"
        and not evaluator["changed_after_failure"]
    ):
        if change["owner_location"] or change["consumer_route"]:
            raise FixtureError(
                f"case {case['id']} cannot use the whitespace cheap path after an owner or consumer move"
            )
        return {
            "triggered": False,
            "disposition": "PASS_MECHANICAL",
            "reason_code": "proved-non-semantic-change",
        }

    triggered = any(
        (
            change["shipped_content"],
            change["owner_location"],
            change["consumer_route"],
            evaluator["changed_after_failure"],
        )
    )
    if not triggered:
        raise FixtureError(
            f"case {case['id']} has package pressure but no semantic activation or cheap-path proof"
        )

    if split["applies"]:
        if not split["owner_shipped"]:
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "required-owner-unshipped",
            }
        if not split["same_run_dispatch"]:
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "required-consumer-unreachable",
            }
        if split["public_projection_required"] and not split["public_projection_preserved"]:
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "public-projection-missing",
            }
        return {
            "triggered": True,
            "disposition": "PASS_PROGRESSIVE_SPLIT",
            "reason_code": "progressive-consumer-chain-preserved",
        }

    if package["unresolved_fit_conflict"]:
        return {
            "triggered": True,
            "disposition": "OWNER_DECISION",
            "reason_code": "irreducible-package-conflict",
        }

    return {
        "triggered": True,
        "disposition": "PASS_EQUIVALENT",
        "reason_code": "predicates-and-consumers-preserved",
    }


def run(cases_path: Path, check: bool) -> int:
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    root = require_mapping(payload, "root")
    if root.get("schema_version") != 1:
        raise FixtureError("root.schema_version must equal 1")
    cases = root.get("cases")
    if not isinstance(cases, list) or not cases:
        raise FixtureError("root.cases must be a non-empty array")

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for index, raw_case in enumerate(cases):
        case = validate_case(raw_case, index)
        if case["id"] in seen:
            raise FixtureError(f"duplicate case id: {case['id']}")
        seen.add(case["id"])
        actual = classify(case)
        if check and actual != case["expected"]:
            raise FixtureError(
                f"case {case['id']} mismatch: expected {case['expected']}, got {actual}"
            )
        results.append({"id": case["id"], **actual})

    for result in results:
        print(
            f"{result['id']}: triggered={str(result['triggered']).lower()} "
            f"disposition={result['disposition']} reason={result['reason_code']}"
        )
    print(f"semantic-preservation-cases: ok ({len(results)}/{len(results)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return run(args.cases, args.check)
    except (FixtureError, json.JSONDecodeError, OSError) as error:
        print(f"semantic-preservation-cases: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
