#!/usr/bin/env python3
"""Evaluate R33 fixtures against inspectable repository and package evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


class FixtureError(ValueError):
    """Raised when a fixture or its cited evidence is invalid."""


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FixtureError(f"{label} must be an object")
    return value


def require_keys(mapping: dict[str, Any], keys: set[str], label: str) -> None:
    actual = set(mapping)
    if actual != keys:
        raise FixtureError(
            f"{label} keys must be {sorted(keys)}; got {sorted(actual)}"
        )


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


def normalise_repo_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{label} must be a non-empty repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise FixtureError(f"{label} must be a normalised repository-relative path")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_revision(repo: Path, path: str, revision: str) -> bytes | None:
    if revision == "WORKTREE":
        target = repo.joinpath(*PurePosixPath(path).parts)
        if not target.is_file():
            return None
        return target.read_bytes()
    completed = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout


def inspect_reference(
    value: Any, label: str, repo: Path, *, anchor_key: str = "anchor"
) -> dict[str, Any]:
    reference = require_mapping(value, label)
    require_keys(reference, {"path", "revision", "sha256", anchor_key}, label)
    path = normalise_repo_path(reference["path"], f"{label}.path")
    revision = require_string(reference, "revision", label)
    expected_hash = reference["sha256"]
    anchor = reference[anchor_key]
    if expected_hash is not None and (
        not isinstance(expected_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
    ):
        raise FixtureError(f"{label}.sha256 must be null or a lower-case SHA-256")
    if anchor is not None and (not isinstance(anchor, str) or not anchor):
        raise FixtureError(f"{label}.{anchor_key} must be null or a non-empty string")

    content = read_revision(repo, path, revision)
    if expected_hash is None:
        if content is not None:
            raise FixtureError(f"{label} declares missing evidence but {path} exists")
        if anchor is not None:
            raise FixtureError(f"{label}.{anchor_key} must be null for missing evidence")
        return {"path": path, "exists": False, "anchor_present": False}
    if content is None:
        raise FixtureError(f"{label} evidence is missing: {revision}:{path}")
    actual_hash = sha256(content)
    if actual_hash != expected_hash:
        raise FixtureError(
            f"{label} identity mismatch for {revision}:{path}: "
            f"expected {expected_hash}, got {actual_hash}"
        )
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise FixtureError(f"{label} evidence is not UTF-8: {path}") from error
    return {
        "path": path,
        "exists": True,
        "anchor_present": anchor is not None and anchor in text,
    }


def parse_builder_manifest(
    value: Any, repo: Path
) -> tuple[dict[str, str], set[str], list[str]]:
    evidence = require_mapping(value, "root.package_evidence")
    require_keys(
        evidence,
        {"builder_path", "builder_sha256", "repo_only_instrumentation"},
        "root.package_evidence",
    )
    builder_path = normalise_repo_path(
        evidence["builder_path"], "root.package_evidence.builder_path"
    )
    builder_hash = require_string(
        evidence, "builder_sha256", "root.package_evidence"
    )
    builder_bytes = read_revision(repo, builder_path, "WORKTREE")
    if builder_bytes is None or sha256(builder_bytes) != builder_hash:
        raise FixtureError("root.package_evidence builder identity mismatch")
    builder_text = builder_bytes.decode("utf-8")

    def assignment(name: str, opening: str, closing: str) -> Any:
        pattern = rf"(?ms)^{re.escape(name)}\s*=\s*({re.escape(opening)}.*?^{re.escape(closing)})"
        match = re.search(pattern, builder_text)
        if not match:
            raise FixtureError(f"builder does not expose parseable {name}")
        try:
            return ast.literal_eval(match.group(1))
        except (SyntaxError, ValueError) as error:
            raise FixtureError(f"builder {name} is not a literal collection") from error

    required_source_raw = assignment("required_source", "[", "]")
    required_archive_raw = assignment("required_archive", "[", "]")
    blocked_parts_raw = assignment("blocked_parts", "{", "}")
    if not isinstance(required_source_raw, list) or not all(
        isinstance(item, str) for item in required_source_raw
    ):
        raise FixtureError("builder required_source must be a literal string list")
    if not isinstance(blocked_parts_raw, set) or not all(
        isinstance(item, str) for item in blocked_parts_raw
    ):
        raise FixtureError("builder blocked_parts must be a literal string set")
    if not isinstance(required_archive_raw, list) or not all(
        isinstance(item, str) for item in required_archive_raw
    ):
        raise FixtureError("builder required_archive must be a literal string list")
    required_archive = set(required_archive_raw)
    required_source: dict[str, str] = {}
    for source_path in required_source_raw:
        if source_path.startswith("skills/implementaudit/"):
            archive_path = source_path.removeprefix("skills/implementaudit/")
        elif source_path.startswith(".claude-plugin/"):
            archive_path = source_path
        else:
            raise FixtureError(
                f"builder required source lacks an archive mapping: {source_path}"
            )
        if archive_path not in required_archive:
            raise FixtureError(
                f"builder archive manifest omits required source: {source_path}"
            )
        required_source[source_path] = archive_path
    blocked_parts = set(blocked_parts_raw)

    repo_only = evidence["repo_only_instrumentation"]
    if not isinstance(repo_only, list) or not repo_only:
        raise FixtureError("root.package_evidence.repo_only_instrumentation must be an array")
    checked: list[str] = []
    for index, raw_path in enumerate(repo_only):
        path = normalise_repo_path(
            raw_path, f"root.package_evidence.repo_only_instrumentation[{index}]"
        )
        if path in required_source:
            raise FixtureError(f"repo-only instrumentation is a package source: {path}")
        if not any(part in blocked_parts for part in PurePosixPath(path).parts):
            raise FixtureError(f"repo-only instrumentation is not builder-blocked: {path}")
        if read_revision(repo, path, "WORKTREE") is None:
            raise FixtureError(f"repo-only instrumentation is missing: {path}")
        checked.append(path)
    return required_source, blocked_parts, checked


def inspect_exact_literals(
    value: Any, repo: Path
) -> set[str]:
    evidence = require_mapping(value, "root.exact_literal_evidence")
    exact_ids: set[str] = set()
    for predicate_id, raw in evidence.items():
        label = f"root.exact_literal_evidence.{predicate_id}"
        row = require_mapping(raw, label)
        require_keys(row, {"value", "owner", "consumer"}, label)
        literal = require_string(row, "value", label)
        owner = inspect_reference(row["owner"], f"{label}.owner", repo)
        consumer = inspect_reference(row["consumer"], f"{label}.consumer", repo)
        if not owner["anchor_present"] or not consumer["anchor_present"]:
            raise FixtureError(f"{label} lacks an inspectable owner/consumer anchor")
        if row["owner"]["anchor"] != literal or row["consumer"]["anchor"] != literal:
            raise FixtureError(f"{label} value must be the owner and consumer anchor")
        exact_ids.add(predicate_id)
    return exact_ids


def inspect_profiles(
    value: Any, repo: Path, required_source: dict[str, str]
) -> dict[str, dict[str, Any]]:
    profiles = require_mapping(value, "root.evidence_profiles")
    resolved: dict[str, dict[str, Any]] = {}
    for evidence_id, raw in profiles.items():
        label = f"root.evidence_profiles.{evidence_id}"
        profile = require_mapping(raw, label)
        require_keys(profile, {"before", "after", "consumers"}, label)
        before = inspect_reference(profile["before"], f"{label}.before", repo)
        after = inspect_reference(profile["after"], f"{label}.after", repo)
        if not before["exists"] or not before["anchor_present"]:
            raise FixtureError(f"{label}.before must contain its governed anchor")

        archive_path = required_source.get(after["path"])
        relation_anchors = {
            anchor
            for anchor in (profile["after"]["anchor"], archive_path)
            if anchor is not None
        }
        consumers_raw = profile["consumers"]
        if not isinstance(consumers_raw, list) or not consumers_raw:
            raise FixtureError(f"{label}.consumers must be a non-empty array")
        consumers: list[dict[str, Any]] = []
        for index, raw_consumer in enumerate(consumers_raw):
            consumer_label = f"{label}.consumers[{index}]"
            consumer = require_mapping(raw_consumer, consumer_label)
            allowed = {"kind", "required", "path", "revision", "sha256", "route_anchor"}
            if "held_out" in consumer:
                allowed.add("held_out")
            require_keys(consumer, allowed, consumer_label)
            kind = require_string(consumer, "kind", consumer_label)
            required = require_bool(consumer, "required", consumer_label)
            route = inspect_reference(
                {
                    "path": consumer["path"],
                    "revision": consumer["revision"],
                    "sha256": consumer["sha256"],
                    "route_anchor": consumer["route_anchor"],
                },
                consumer_label,
                repo,
                anchor_key="route_anchor",
            )
            route_proves_owner = consumer["route_anchor"] in relation_anchors
            held_out_passes = route["exists"] and route["anchor_present"]
            held_out_present = "held_out" in consumer
            if held_out_present:
                held_out = inspect_reference(
                    consumer["held_out"], f"{consumer_label}.held_out", repo
                )
                held_out_passes = held_out["exists"] and held_out["anchor_present"]
            consumers.append(
                {
                    "kind": kind,
                    "required": required,
                    "reachable": (
                        route["exists"]
                        and route["anchor_present"]
                        and route_proves_owner
                    ),
                    "held_out_present": held_out_present,
                    "held_out_passes": held_out_passes,
                }
            )
        resolved[evidence_id] = {
            "owner_shipped": after["exists"] and archive_path is not None,
            "after_satisfied": after["exists"] and after["anchor_present"],
            "progressive_applies": before["path"] != after["path"],
            "consumers": consumers,
        }
    return resolved


def validate_case(
    case: Any,
    index: int,
    profiles: dict[str, dict[str, Any]],
    exact_ids: set[str],
) -> dict[str, Any]:
    row = require_mapping(case, f"cases[{index}]")
    require_keys(
        row,
        {
            "id",
            "package_pressure",
            "change",
            "package",
            "behaviours",
            "evaluator",
            "progressive_split",
            "expected",
        },
        f"cases[{index}]",
    )
    label = f"case {require_string(row, 'id', f'cases[{index}]')}"
    require_bool(row, "package_pressure", label)

    change = require_mapping(row["change"], f"{label}.change")
    require_keys(
        change,
        {"shipped_content", "owner_location", "consumer_route", "non_semantic_proof"},
        f"{label}.change",
    )
    for key in ("shipped_content", "owner_location", "consumer_route"):
        require_bool(change, key, f"{label}.change")
    proof = require_string(change, "non_semantic_proof", f"{label}.change")
    if proof not in {"none", "extracted-equal", "whitespace-dedup"}:
        raise FixtureError(f"{label}.change.non_semantic_proof is unsupported")

    package = require_mapping(row["package"], f"{label}.package")
    require_keys(
        package,
        {"extracted_members_equal", "fits_policy_after", "unresolved_fit_conflict"},
        f"{label}.package",
    )
    for key in ("extracted_members_equal", "fits_policy_after", "unresolved_fit_conflict"):
        require_bool(package, key, f"{label}.package")
    if package["fits_policy_after"] == package["unresolved_fit_conflict"]:
        raise FixtureError(
            f"{label}.package must distinguish fitting from unresolved conflict"
        )

    evaluator = require_mapping(row["evaluator"], f"{label}.evaluator")
    require_keys(
        evaluator,
        {"changed_after_failure", "independent_justification", "underlying_property_passes"},
        f"{label}.evaluator",
    )
    for key in ("changed_after_failure", "independent_justification", "underlying_property_passes"):
        require_bool(evaluator, key, f"{label}.evaluator")

    split = require_mapping(row["progressive_split"], f"{label}.progressive_split")
    require_keys(split, {"applies"}, f"{label}.progressive_split")
    require_bool(split, "applies", f"{label}.progressive_split")

    behaviours = row["behaviours"]
    if not isinstance(behaviours, list):
        raise FixtureError(f"{label}.behaviours must be an array")
    resolved_behaviours: list[dict[str, Any]] = []
    for behaviour_index, raw_behaviour in enumerate(behaviours):
        behaviour_label = f"{label}.behaviours[{behaviour_index}]"
        behaviour = require_mapping(raw_behaviour, behaviour_label)
        require_keys(
            behaviour, {"predicate_id", "evidence_id", "literal"}, behaviour_label
        )
        predicate_id = require_string(behaviour, "predicate_id", behaviour_label)
        evidence_id = require_string(behaviour, "evidence_id", behaviour_label)
        if evidence_id not in profiles:
            raise FixtureError(f"{behaviour_label}.evidence_id is unknown: {evidence_id}")
        literal = require_mapping(behaviour["literal"], f"{behaviour_label}.literal")
        require_keys(
            literal,
            {"claimed_class", "changed", "reauthorisation_evidence_id"},
            f"{behaviour_label}.literal",
        )
        claimed_class = require_string(
            literal, "claimed_class", f"{behaviour_label}.literal"
        )
        if claimed_class not in {"semantic", "exact"}:
            raise FixtureError(f"{behaviour_label}.literal.claimed_class is unsupported")
        if claimed_class == "exact" and predicate_id not in exact_ids:
            raise FixtureError(
                f"{behaviour_label} claims exactness without independent literal evidence"
            )
        changed = require_bool(literal, "changed", f"{behaviour_label}.literal")
        reauthorisation = literal["reauthorisation_evidence_id"]
        if reauthorisation is not None:
            raise FixtureError(
                f"{behaviour_label}.literal reauthorisation must cite a supported evidence record"
            )
        resolved_behaviours.append(
            {
                "predicate_id": predicate_id,
                "owner_shipped": profiles[evidence_id]["owner_shipped"],
                "after_satisfied": profiles[evidence_id]["after_satisfied"],
                "progressive_applies": profiles[evidence_id]["progressive_applies"],
                "literal": {
                    "class": "exact" if predicate_id in exact_ids else "semantic",
                    "changed": changed,
                    "reauthorised": False,
                },
                "consumers": profiles[evidence_id]["consumers"],
            }
        )

    expected = require_mapping(row["expected"], f"{label}.expected")
    require_keys(expected, {"triggered", "disposition", "reason_code"}, f"{label}.expected")
    require_bool(expected, "triggered", f"{label}.expected")
    require_string(expected, "disposition", f"{label}.expected")
    require_string(expected, "reason_code", f"{label}.expected")

    resolved = dict(row)
    resolved["behaviours"] = resolved_behaviours
    resolved["progressive_split"] = {
        "claimed_applies": split["applies"],
        "derived_applies": any(
            behaviour["progressive_applies"] for behaviour in resolved_behaviours
        ),
    }
    return resolved


def behaviour_failure(
    case: dict[str, Any], require_consumer_census: bool
) -> tuple[str, str] | None:
    for behaviour in case["behaviours"]:
        if not behaviour["owner_shipped"]:
            return "FAIL", "required-owner-unshipped"
        literal = behaviour["literal"]
        if literal["class"] == "exact" and literal["changed"] and not literal["reauthorised"]:
            return "FAIL", "exact-literal-owner-changed"
        if not behaviour["after_satisfied"]:
            return "FAIL", "governed-predicate-lost"
        if require_consumer_census and not any(
            consumer["required"] for consumer in behaviour["consumers"]
        ):
            return "FAIL", "required-consumer-census-missing"
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
        return {"triggered": False, "disposition": "NOT_TRIGGERED", "reason_code": "ordinary-non-package-work"}
    triggered = any(
        (change["shipped_content"], change["owner_location"], change["consumer_route"], evaluator["changed_after_failure"])
    )
    if evaluator["changed_after_failure"]:
        if not evaluator["independent_justification"]:
            return {"triggered": True, "disposition": "FAIL", "reason_code": "evaluator-change-unjustified"}
        if not evaluator["underlying_property_passes"]:
            return {"triggered": True, "disposition": "FAIL", "reason_code": "underlying-property-still-fails"}
    if triggered and not case["behaviours"]:
        return {"triggered": True, "disposition": "FAIL", "reason_code": "protected-behaviour-census-missing"}
    failure = behaviour_failure(case, require_consumer_census=triggered)
    if failure:
        disposition, reason_code = failure
        return {"triggered": True, "disposition": disposition, "reason_code": reason_code}
    if not evaluator["underlying_property_passes"]:
        return {"triggered": True, "disposition": "FAIL", "reason_code": "underlying-property-still-fails"}
    if package["unresolved_fit_conflict"]:
        return {"triggered": True, "disposition": "OWNER_DECISION", "reason_code": "irreducible-package-conflict"}
    if change["non_semantic_proof"] == "extracted-equal" and not triggered:
        if not package["extracted_members_equal"]:
            raise FixtureError(f"case {case['id']} claims extracted equality but package evidence disagrees")
        return {"triggered": False, "disposition": "PASS_MECHANICAL", "reason_code": "extracted-members-equal"}
    if not triggered:
        raise FixtureError(f"case {case['id']} has package pressure but no semantic activation or cheap-path proof")
    if split["derived_applies"]:
        # Owner movement, shipment and dispatch are derived, never asserted by the case.
        if any(
            consumer["required"] and not consumer["held_out_present"]
            for behaviour in case["behaviours"]
            for consumer in behaviour["consumers"]
        ):
            return {
                "triggered": True,
                "disposition": "FAIL",
                "reason_code": "held-out-consumer-missing",
            }
        return {"triggered": True, "disposition": "PASS_PROGRESSIVE_SPLIT", "reason_code": "progressive-consumer-chain-preserved"}
    return {"triggered": True, "disposition": "PASS_EQUIVALENT", "reason_code": "predicates-and-consumers-preserved"}


def run(cases_path: Path, check: bool) -> int:
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    root = require_mapping(payload, "root")
    require_keys(
        root,
        {"schema_version", "package_evidence", "exact_literal_evidence", "evidence_profiles", "cases"},
        "root",
    )
    if root["schema_version"] != 2:
        raise FixtureError("root.schema_version must equal 2")
    repo = Path(__file__).resolve().parents[2]
    required_source, _blocked_parts, repo_only = parse_builder_manifest(
        root["package_evidence"], repo
    )
    exact_ids = inspect_exact_literals(root["exact_literal_evidence"], repo)
    profiles = inspect_profiles(root["evidence_profiles"], repo, required_source)
    cases = root["cases"]
    if not isinstance(cases, list) or not cases:
        raise FixtureError("root.cases must be a non-empty array")
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for index, raw_case in enumerate(cases):
        case = validate_case(raw_case, index, profiles, exact_ids)
        if case["id"] in seen:
            raise FixtureError(f"duplicate case id: {case['id']}")
        seen.add(case["id"])
        actual = classify(case)
        if check and actual != case["expected"]:
            raise FixtureError(f"case {case['id']} mismatch: expected {case['expected']}, got {actual}")
        results.append({"id": case["id"], **actual})
    for result in results:
        print(
            f"{result['id']}: triggered={str(result['triggered']).lower()} "
            f"disposition={result['disposition']} reason={result['reason_code']}"
        )
    print(f"package-evidence: repo-only instrumentation absent ({len(repo_only)}/{len(repo_only)})")
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
