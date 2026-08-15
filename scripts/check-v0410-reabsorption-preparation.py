#!/usr/bin/env python3
"""Validate the pre-v0.4.1 reabsorption executor preparation contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PREP_REL = Path("docs/research/implementaudit/v0410-reabsorption-preparation")
REQUIRED_FILES = (
    "V0410_REABSORPTION_EXECUTOR_WORK_ORDER.md",
    "V0410_REABSORPTION_DAG.md",
    "V0410_CURRENT_DISPOSITION_SCHEMA.json",
    "V0410_RXX_ADMISSION_SCHEMA.json",
    "V0410_CHILD_SKILL_ADMISSION_SCHEMA.json",
    "V0410_HELD_OUT_ACCEPTANCE_PLAN.md",
    "V0410_PROVISIONAL_RXX_CANDIDATE.md",
    "V0410_WORK_ORDER_COLD_REVIEW.md",
)

DESTINATIONS = {
    "NO_CHANGE_ALREADY_COMPLETE",
    "DETERMINISTIC_SUBSTRATE",
    "GOVERNOR_OR_L1_L5",
    "AUDIT_STATE",
    "AUDIT_ASSESS",
    "AUDIT_IMPLEMENT",
    "AUDIT_ANDON",
    "EXISTING_CHILD_REFERENCE_OR_TRIGGER_REFINEMENT",
    "CANDIDATE_NEW_CHILD_SKILL",
    "DAG_CHILD_AGENT_ORCHESTRATION",
    "REFERENCE",
    "TEMPLATE_OR_SCHEMA",
    "CHECKER_OR_FIXTURE",
    "PACKAGE_OR_REACHABILITY",
    "BEHAVIOURAL_PROOF_ONLY",
    "EXISTING_RXX_AMENDMENT",
    "GENUINE_UNOWNED_RESIDUAL",
    "STILL_REJECTED",
    "STILL_ASSUMPTION_BOUND",
    "STILL_DOMAIN_BOUND",
    "UNRESOLVED",
}

RXX_REQUIRED = {
    "GENEALOGY_EXISTING_RXXS",
    "OVERLAPPING_EXISTING_RXXS",
    "DEPENDENCY_RXXS",
    "AUTHORITY_NEIGHBOURS",
    "SUPERSEDED_ASSUMPTIONS",
    "CONFLICTS",
    "REQUIRED_AMENDMENTS_TO_OLDER_RXXS",
    "WHY_THIS_IS_NOT_MERELY_DUPLICATE_OF_EXISTING_RXXS",
    "ROOT_PROBLEM",
    "OBSERVED_FAILURE_OR_CURRENT_GAP",
    "GENUINE_UNOWNED_RESIDUAL",
    "CONSUMER",
    "ENGINEERING_PAYOFF",
    "TRIGGER",
    "NON_TRIGGER_CHEAP_PATH",
    "AUTHORITY",
    "STATE",
    "NATIVE_OWNER",
    "ORDERED_WORK",
    "CONTROLS",
    "ANTI_GAMING",
    "NO_REGRESSION",
    "NO_BLOAT",
    "ROLLBACK_RETIREMENT",
    "PACKAGE_REACHABILITY",
    "BEHAVIOURAL_ACCEPTANCE",
    "TERMINAL_ACCEPTANCE",
    "ACCEPTANCE_INHERITANCE",
}

CHILD_REQUIRED = {
    "TRIGGER",
    "NON_TRIGGER",
    "CONSUMER",
    "BOUNDED_INPUT",
    "OWNED_COGNITIVE_PROCEDURE",
    "IRREDUCIBLE_MODEL_JUDGEMENT",
    "BOUNDED_OUTPUT_POSTCONDITION",
    "GOVERNOR_AUTHORITY_FENCE",
    "CONTEXT_REASONING_PAYOFF",
    "REPEATED_VALUE_EVIDENCE",
    "NOT_REFERENCE_ONLY",
    "NOT_DETERMINISTIC_SUBSTRATE",
    "NOT_ALREADY_OWNED_BY_EXISTING_CHILD",
    "NOT_DISCIPLINE_LABEL",
    "CHEAP_PATH_EFFECT",
    "PACKAGE_INSTALL_HOST_COST",
    "MAINTENANCE_COST",
    "RETIREMENT_CONDITION",
}


class ContractError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing required preparation file: {path.name}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.name}: {exc}") from exc
    require(isinstance(value, dict), f"{path.name} must contain one JSON object")
    return value


def has_deferred_const(definition: dict) -> bool:
    one_of = definition.get("oneOf")
    return isinstance(one_of, list) and any(
        isinstance(item, dict) and item.get("const") == "DEFER_TO_V0410_BASELINE"
        for item in one_of
    )


def check(root: Path) -> None:
    prep = root / PREP_REL
    require(prep.is_dir(), f"missing preparation directory: {PREP_REL.as_posix()}")
    texts: dict[str, str] = {}
    for name in REQUIRED_FILES:
        path = prep / name
        texts[name] = read_text(path)

    work = texts["V0410_REABSORPTION_EXECUTOR_WORK_ORDER.md"]
    dag = texts["V0410_REABSORPTION_DAG.md"]
    held = texts["V0410_HELD_OUT_ACCEPTANCE_PLAN.md"]
    candidate = texts["V0410_PROVISIONAL_RXX_CANDIDATE.md"]
    review = texts["V0410_WORK_ORDER_COLD_REVIEW.md"]

    require(
        "STATE_DERIVED_TERMINAL_ORCHESTRATION=`HYPOTHESIS_TO_TEST`" in work,
        "state-derived terminal orchestration must remain a hypothesis",
    )
    require(
        "RXX_ID=UNALLOCATED" in candidate,
        "provisional RXX ID must remain UNALLOCATED",
    )
    require(
        not re.search(r"^RXX_ID=R\d+", candidate, re.MULTILINE),
        "provisional RXX ID must remain UNALLOCATED",
    )
    require(
        "DISPOSITION=CANDIDATE_PENDING_RELEASED_V0400_EVIDENCE" in candidate,
        "provisional RXX disposition is predecided",
    )
    require(
        not re.search(
            r"^DISPOSITION=(?:NEW_RXX_REQUIRED|EXISTING_RXX_AMENDMENT|NO_RXX_REQUIRED)",
            candidate,
            re.MULTILINE,
        ),
        "provisional RXX disposition is predecided",
    )
    require(
        "BASELINE_PUBLIC_READBACK=`DEFER_TO_V0410_BASELINE`" in work,
        "work order lost public-v0.4 baseline deferral",
    )
    for field in (
        "CURRENT_PROPERTY_DISPOSITIONS",
        "RELEASED_V0400_COMMIT",
        "RELEASED_V0400_TREE",
        "RELEASED_V0400_TAG_OBJECT",
        "RELEASED_V0400_RELEASE_OBJECT",
        "RELEASED_V0400_ASSET_SHA256",
        "RELEASED_V0400_CHECKSUMS_SHA256",
        "RELEASED_V0400_PACKAGE_MEMBERS",
        "RELEASED_V0400_INSTALLED_RUNTIME",
        "RELEASED_V0400_PUBLIC_READBACK",
        "RELEASED_V0400_RXX_HIGH_WATER",
        "RELEASED_V0400_RXX_STATES",
    ):
        require(
            re.search(
                rf"^{field}=(?:`)?DEFER_TO_V0410_BASELINE(?:`)?$",
                work,
                re.MULTILINE,
            )
            is not None,
            f"work order does not defer released-v0.4 field: {field}",
        )
    for field in (
        "SOURCE_DELTA_REQUIRED",
        "CURRENT_IMPLEMENTATION_ALREADY_SATISFIES",
        "RELEASED_V0400_COMMIT",
        "RELEASED_V0400_TREE",
        "RELEASED_V0400_PACKAGE",
        "RELEASED_V0400_INSTALLED_RUNTIME",
        "RELEASED_V0400_PUBLIC_EVIDENCE",
        "CURRENT_RXX_GENEALOGY",
        "ROOT_PROBLEM",
        "OBSERVED_FAILURE_OR_CURRENT_GAP",
        "GENUINE_UNOWNED_RESIDUAL",
        "NATIVE_OWNER",
    ):
        require(
            re.search(
                rf"^{field}=(?:`)?DEFER_TO_V0410_BASELINE(?:`)?$",
                candidate,
                re.MULTILINE,
            )
            is not None,
            f"provisional candidate does not defer released-v0.4 field: {field}",
        )
    for rxx in ("R31", "R34", "R42", "R51", "R53", "R54", "R55"):
        require(rxx in work and rxx in candidate, f"missing required RXX pressure owner: {rxx}")
    for token in (
        "automatic DAG derivation/recomputation",
        "State-plan divergence",
        "Unresolved-obligation derivation",
        "DONE/ACTIVE/READY/BLOCKED",
        "JOIN/writer/authority/resource edges",
        "Progressive child routing",
        "Currentness invalidation",
        "Recovery/re-entry reconstruction",
    ):
        require(token.lower() in work.lower(), f"work order missing hypothesis cell: {token}")
    for destination in DESTINATIONS:
        require(destination in work, f"work order missing current destination: {destination}")
    require("A00 PUBLIC_V0400_READBACK_GATE" in dag, "DAG lost public baseline gate")
    require("BLOCKED=DEFER_TO_V0410_BASELINE" in dag, "DAG lost pre-baseline blocked frontier")
    for number in range(1, 21):
        require(f"H{number:02d}" in held, f"held-out plan missing H{number:02d}")

    current_schema = read_json(prep / "V0410_CURRENT_DISPOSITION_SCHEMA.json")
    rows = current_schema.get("properties", {}).get("ROWS")
    require(
        isinstance(rows, dict) and rows.get("minItems") == 658 and rows.get("maxItems") == 658,
        "current disposition schema must require exactly 658 rows",
    )
    destination_values = set(
        current_schema.get("$defs", {}).get("destination", {}).get("enum", [])
    )
    require(destination_values == DESTINATIONS, "current destination taxonomy drift")
    deferred_fact = current_schema.get("$defs", {}).get("deferredFact", {})
    require(
        has_deferred_const(deferred_fact),
        "released-v0.4-dependent fields lost explicit deferral",
    )
    property_required = set(
        current_schema.get("$defs", {}).get("propertyDisposition", {}).get("required", [])
    )
    for field in (
        "HISTORICAL_DISPOSITION",
        "HISTORICAL_OWNER",
        "HISTORICAL_NONADOPTION_OR_PARTIAL_BASIS",
        "RELEASED_V0400_EXACT_OWNER",
        "SOURCE_IMPLEMENTATION",
        "PACKAGE_STATE",
        "PROGRESSIVE_DISCLOSURE_REACHABILITY",
        "BEHAVIOURAL_ACTIVATION",
        "CURRENTNESS_AUTHORITY",
        "DETERMINISTIC_DISCRIMINATOR",
        "COGNITIVE_OWNER",
        "DAG_WORK_TOPOLOGY_RELATION",
        "CURRENT_COST_CEREMONY",
        "CURRENT_EVIDENCE_LIMIT",
        "CURRENT_DESTINATION",
    ):
        require(field in property_required, f"current disposition schema lost field: {field}")

    rxx_schema = read_json(prep / "V0410_RXX_ADMISSION_SCHEMA.json")
    rxx_required = set(rxx_schema.get("required", []))
    missing_rxx = sorted(RXX_REQUIRED - rxx_required)
    require(not missing_rxx, f"RXX schema lost required admission fields: {missing_rxx}")
    rxx_id = rxx_schema.get("properties", {}).get("RXX_ID", {})
    require(
        any(item.get("const") == "UNALLOCATED" for item in rxx_id.get("oneOf", [])),
        "RXX schema lost unallocated candidate state",
    )

    child_schema = read_json(prep / "V0410_CHILD_SKILL_ADMISSION_SCHEMA.json")
    child_required = set(child_schema.get("required", []))
    missing_child = sorted(CHILD_REQUIRED - child_required)
    if missing_child:
        if len(missing_child) == 1:
            raise ContractError(
                f"child-skill schema lost required admission field: {missing_child[0]}"
            )
        raise ContractError(f"child-skill schema lost required admission fields: {missing_child}")

    require("PREPARATION_COLD_REVIEW=PASS" in review, "cold review has no PASS receipt")
    for challenge in (
        "DUPLICATE_OWNERSHIP",
        "PREDECIDED_CONCLUSIONS",
        "FEATURE_OR_RXX_QUOTAS",
        "TAXONOMY_DRIVEN_CHILD_PROLIFERATION",
        "MONOLITH_SPLIT_REWARD_HACKING",
        "STALE_PLAN_BIAS",
        "RESEARCH_TO_RUNTIME_OVERTRANSFER",
    ):
        require(challenge in review, f"cold review missing challenge: {challenge}")

    combined = "\n".join(texts.values())
    require(
        not re.search(r"(?:[A-Za-z]:\\Users\\|file:///C:/Users/|/home/[^/]+/)", combined),
        "preparation artifacts leak an absolute user path",
    )
    require(
        not re.search(r"(?:next|expected|reserved)\s+RXX\s*(?:is|=|:)\s*R\d+", combined, re.I),
        "preparation artifacts predict or reserve an RXX number",
    )

    sys.stdout.write(
        "V0410_REABSORPTION_PREPARATION=PASS "
        "FILES=8 SCHEMAS=3 PROPERTY_DENOMINATOR=658 "
        "RXX_ID=UNALLOCATED DISPOSITION=CANDIDATE_PENDING_RELEASED_V0400_EVIDENCE\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        check(args.root.resolve())
    except ContractError as exc:
        sys.stderr.write(f"check-v0410-reabsorption-preparation: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
