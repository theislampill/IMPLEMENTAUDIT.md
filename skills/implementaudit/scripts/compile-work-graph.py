#!/usr/bin/env python3
"""Compile a deterministic, read-only frontier projection from WORK_GRAPH.json."""

from __future__ import annotations

import hashlib
import hmac
import json
import pathlib
import re
import sys
from typing import TypeAlias


JSONValue: TypeAlias = (
    None | bool | int | str | list["JSONValue"] | dict[str, "JSONValue"]
)

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1
KNOWN_STATES = ("DONE", "ACTIVE", "READY", "BLOCKED")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
RECEIPT_RE = re.compile(
    r"^refs/implementaudit/continuity-receipts/[^/@]+/G[0-9A-F]{4}@[0-9a-f]{40}$"
)
PREPARATION_KINDS = {
    "BRIEF",
    "RECONNAISSANCE",
    "RED_DESIGN",
    "FIXTURE_DESIGN",
    "ACCEPTANCE_PLAN",
    "REVIEW_PLAN",
    "DISPOSABLE_PROTOTYPE",
}
PREPARATION_FORBIDDEN = {
    "SOURCE_MUTATION",
    "GRAPH_MUTATION",
    "LIFECYCLE_CREDIT",
    "REF_MUTATION",
    "PACKAGE_INSTALL_PUBLICATION",
    "EXTERNAL_EFFECT",
}
PRODUCT_DISPOSITIONS = {
    "CONSUMED",
    "COMPOSED",
    "INTEGRATED",
    "SUPERSEDED",
    "REJECTED",
    "EXPLICITLY_DEFERRED_TO_NAMED_JOIN",
}


class WorkGraphError(ValueError):
    """The supplied WORK_GRAPH bytes do not satisfy the v1 contract."""


def _reject_float(token: str) -> float:
    raise WorkGraphError(f"floats are forbidden: {token}")


def _reject_constant(token: str) -> None:
    raise WorkGraphError(f"non-finite numbers are forbidden: {token}")


def _decode_int(token: str) -> int:
    if token == "-0":
        raise WorkGraphError("negative zero is forbidden")
    value = int(token, 10)
    if not INT64_MIN <= value <= INT64_MAX:
        raise WorkGraphError("integer outside signed 64-bit range")
    return value


def _unique_object(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise WorkGraphError(f"duplicate key: {key}")
        result[key] = value
    return result


def _validate_scalar_unicode(value: str, path: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise WorkGraphError(f"{path}: string contains a non-scalar surrogate")


def validate_identity_json_v1(value: JSONValue, path: str = "$") -> None:
    if value is None or type(value) is bool:
        return
    if type(value) is str:
        _validate_scalar_unicode(value, path)
        return
    if type(value) is int:
        if not INT64_MIN <= value <= INT64_MAX:
            raise WorkGraphError(f"{path}: integer outside signed 64-bit range")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            validate_identity_json_v1(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise WorkGraphError(f"{path}: object key must be a string")
            _validate_scalar_unicode(key, f"{path}.<key>")
            validate_identity_json_v1(item, f"{path}.{key}")
        return
    raise WorkGraphError(f"{path}: floats and non-JSON values are forbidden")


def canonical_json_v1(value: JSONValue) -> bytes:
    validate_identity_json_v1(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def decode_strict_json_bytes(raw: bytes, source: str) -> JSONValue:
    if not isinstance(raw, bytes):
        raise WorkGraphError(f"{source}: input must be bytes")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise WorkGraphError(f"{source}: UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise WorkGraphError(f"{source}: invalid UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_float=_reject_float,
            parse_int=_decode_int,
            parse_constant=_reject_constant,
        )
    except WorkGraphError:
        raise
    except json.JSONDecodeError as exc:
        raise WorkGraphError(f"{source}: invalid JSON: {exc.msg}") from exc
    validate_identity_json_v1(value)
    return value


def _require_object(value: JSONValue, path: str) -> dict[str, JSONValue]:
    if type(value) is not dict:
        raise WorkGraphError(f"{path}: object required")
    return value


def _require_string(value: JSONValue, path: str) -> str:
    if type(value) is not str or not value:
        raise WorkGraphError(f"{path}: non-empty string required")
    return value


def _require_string_list(value: JSONValue, path: str) -> list[str]:
    if type(value) is not list or not value:
        raise WorkGraphError(f"{path}: non-empty array required")
    result = [_require_string(item, path) for item in value]
    if len(result) != len(set(result)):
        raise WorkGraphError(f"{path}: duplicate value")
    return result


def _require_string_array(value: JSONValue, path: str) -> list[str]:
    if type(value) is not list:
        raise WorkGraphError(f"{path}: array required")
    result = [_require_string(item, path) for item in value]
    if len(result) != len(set(result)):
        raise WorkGraphError(f"{path}: duplicate value")
    return result


def _require_digest(value: JSONValue, path: str) -> str:
    result = _require_string(value, path)
    if not DIGEST_RE.fullmatch(result):
        raise WorkGraphError(f"{path}: 64-hex digest required")
    return result


def _require_commit(value: JSONValue, path: str) -> str:
    result = _require_string(value, path)
    if not COMMIT_RE.fullmatch(result):
        raise WorkGraphError(f"{path}: 40-hex identity required")
    return result


def _validate_product_result_v1(
    value: JSONValue,
    path: str,
    by_id: dict[str, dict[str, JSONValue]],
) -> dict[str, JSONValue]:
    result = _require_object(value, path)
    if set(result) != {"product", "disposition"}:
        raise WorkGraphError(f"{path}: product and one disposition required")
    product = _require_object(result["product"], f"{path}.product")
    if set(product) != {"commit", "tree", "review_sha256"}:
        raise WorkGraphError(f"{path}.product: exact identity members required")
    _require_commit(product["commit"], f"{path}.product.commit")
    _require_commit(product["tree"], f"{path}.product.tree")
    _require_digest(product["review_sha256"], f"{path}.product.review_sha256")
    disposition = _require_object(result["disposition"], f"{path}.disposition")
    if set(disposition) != {"kind", "target"}:
        raise WorkGraphError(f"{path}.disposition: kind and target required")
    kind = _require_string(disposition["kind"], f"{path}.disposition.kind")
    target = _require_string(disposition["target"], f"{path}.disposition.target")
    if kind not in PRODUCT_DISPOSITIONS:
        raise WorkGraphError(f"{path}.disposition: unknown disposition {kind}")
    return result


def _validate_product_contract_v1(
    graph: dict[str, JSONValue],
    cells: list[dict[str, JSONValue]],
    by_id: dict[str, dict[str, JSONValue]],
    product_authority_bytes: bytes | None = None,
) -> dict[str, JSONValue] | None:
    topology_value = graph.get("integration_topology")
    topology = topology_value if type(topology_value) is dict else {}
    contract_value = topology.get("product_contract")
    product_signal = any("source_bearing" in cell for cell in cells) or any(
        key in topology for key in ("qualified_products", "composition_proposals")
    )
    if contract_value is None:
        if product_signal:
            raise WorkGraphError("qualified product contract required for governed products")
        return None
    contract = _require_object(contract_value, "$.integration_topology.product_contract")
    expected_contract = {
        "authority_sha256",
        "done_classification",
        "non_cell_owners",
        "join_owners",
        "product_bindings",
        "disposition_bindings",
        "composition_authorizations",
        "future_consumers",
    }
    if set(contract) != expected_contract:
        raise WorkGraphError("qualified product contract: exact members required")

    authority = _require_object(graph.get("authority"), "$.authority")
    source = _require_object(
        authority.get("qualified_product_contract"),
        "$.authority.qualified_product_contract",
    )
    if set(source) != {"kind", "path", "bytes", "sha256", "receipt"}:
        raise WorkGraphError("qualified product authority: exact source identity required")
    if source["kind"] != "GOVERNOR_VERIFIED_PRODUCT_BINDINGS":
        raise WorkGraphError("qualified product authority: governor-verified source required")
    _require_string(source["path"], "qualified product authority path")
    if type(source["bytes"]) is not int or source["bytes"] <= 0:
        raise WorkGraphError("qualified product authority: positive byte count required")
    _require_digest(source["sha256"], "qualified product authority sha256")
    receipt = _require_string(source["receipt"], "qualified product authority receipt")
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError("qualified product authority: current receipt required")
    authority_sha = _require_digest(
        contract["authority_sha256"], "qualified product contract authority_sha256"
    )
    expected_authority_sha = hashlib.sha256(canonical_json_v1(source)).hexdigest()
    if not hmac.compare_digest(authority_sha, expected_authority_sha):
        raise WorkGraphError("qualified product contract: authority source binding mismatch")
    if product_authority_bytes is None:
        raise WorkGraphError("qualified product contract: authoritative source bytes required")
    if len(product_authority_bytes) != source["bytes"] or not hmac.compare_digest(
        hashlib.sha256(product_authority_bytes).hexdigest(), str(source["sha256"])
    ):
        raise WorkGraphError("qualified product contract: authoritative source identity mismatch")
    authority_document = _require_object(
        decode_strict_json_bytes(product_authority_bytes, str(source["path"])),
        "qualified product authority document",
    )
    expected_document = dict(contract)
    del expected_document["authority_sha256"]
    if authority_document != expected_document:
        raise WorkGraphError("qualified product contract: authoritative source content mismatch")

    classification = _require_object(
        contract["done_classification"], "qualified product done classification"
    )
    done_ids = {str(cell["id"]) for cell in cells if cell["state"] == "DONE"}
    if set(classification) != done_ids:
        raise WorkGraphError("qualified product classification must cover every DONE cell")
    source_cells: set[str] = set()
    for cell_id in sorted(done_ids):
        category = classification[cell_id]
        if category not in {"SOURCE_PRODUCT", "NON_SOURCE"}:
            raise WorkGraphError(f"cell {cell_id}: invalid qualified product classification")
        cell = by_id[cell_id]
        if type(cell.get("source_bearing")) is not bool:
            raise WorkGraphError(f"cell {cell_id}: explicit source_bearing classification required")
        expected_source = category == "SOURCE_PRODUCT"
        if cell["source_bearing"] is not expected_source:
            raise WorkGraphError(f"cell {cell_id}: source_bearing classification mismatch")
        if expected_source:
            source_cells.add(cell_id)

    non_cell_owners = _require_string_array(
        contract["non_cell_owners"], "qualified product non-cell owners"
    )
    if non_cell_owners != sorted(non_cell_owners):
        raise WorkGraphError("qualified product non-cell owners must be sorted")
    join_owners = _require_string_array(
        contract["join_owners"], "qualified product join owners"
    )
    if join_owners != sorted(join_owners):
        raise WorkGraphError("qualified product join owners must be sorted")
    for owner in join_owners:
        if owner not in by_id or by_id[owner].get("class") != "integration":
            raise WorkGraphError(f"qualified product contract: unresolved join owner {owner}")

    bindings_value = contract["product_bindings"]
    if type(bindings_value) is not list or not bindings_value:
        raise WorkGraphError("qualified product bindings: non-empty array required")
    bindings: dict[tuple[str, str], dict[str, JSONValue]] = {}
    commits: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(bindings_value):
        binding = _require_object(value, f"qualified product binding {index}")
        if set(binding) != {
            "owner_kind", "owner", "commit", "tree", "review_sha256"
        }:
            raise WorkGraphError(f"qualified product binding {index}: exact members required")
        owner_kind = _require_string(binding["owner_kind"], "product owner kind")
        owner = _require_string(binding["owner"], "product owner")
        if owner_kind not in {"CELL", "NON_CELL"}:
            raise WorkGraphError(f"qualified product binding {index}: unknown owner kind")
        if owner_kind == "CELL" and owner not in source_cells:
            raise WorkGraphError(f"qualified product binding {index}: unknown source cell {owner}")
        if owner_kind == "NON_CELL" and owner not in non_cell_owners:
            raise WorkGraphError(f"qualified product binding {index}: unknown non-cell owner {owner}")
        key = (owner_kind, owner)
        if key in bindings:
            raise WorkGraphError(f"duplicate qualified product owner: {owner_kind}/{owner}")
        commit = _require_commit(binding["commit"], "qualified product binding commit")
        _require_commit(binding["tree"], "qualified product binding tree")
        _require_digest(binding["review_sha256"], "qualified product binding review")
        if commit in commits:
            raise WorkGraphError(f"qualified product emitted more than once: {commit}")
        bindings[key] = binding
        commits[commit] = binding
    expected_owners = {("CELL", owner) for owner in source_cells} | {
        ("NON_CELL", owner) for owner in non_cell_owners
    }
    if set(bindings) != expected_owners:
        raise WorkGraphError("qualified product bindings do not cover authoritative owners")

    dispositions_value = contract["disposition_bindings"]
    if type(dispositions_value) is not list or len(dispositions_value) != len(commits):
        raise WorkGraphError("qualified product dispositions must cover every product")
    dispositions: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(dispositions_value):
        disposition = _require_object(value, f"product disposition binding {index}")
        if set(disposition) != {"product_commit", "kind", "target"}:
            raise WorkGraphError(f"product disposition binding {index}: exact members required")
        product_commit = _require_commit(
            disposition["product_commit"], "product disposition product_commit"
        )
        if product_commit not in commits or product_commit in dispositions:
            raise WorkGraphError("product disposition: unknown or duplicate product")
        kind = _require_string(disposition["kind"], "product disposition kind")
        target = _require_string(disposition["target"], "product disposition target")
        if kind not in PRODUCT_DISPOSITIONS:
            raise WorkGraphError(f"product disposition: unknown disposition {kind}")
        if kind == "CONSUMED" and target not in by_id:
            raise WorkGraphError(f"product disposition: unknown consumer {target}")
        if kind == "COMPOSED" and (target not in commits or target == product_commit):
            raise WorkGraphError(f"product disposition: unknown composition {target}")
        if kind in {"SUPERSEDED", "REJECTED"} and target not in commits:
            raise WorkGraphError(f"product disposition: unknown product identity {target}")
        if kind == "EXPLICITLY_DEFERRED_TO_NAMED_JOIN" and target not in join_owners:
            raise WorkGraphError(f"product disposition: unresolved named join {target}")
        if kind == "INTEGRATED":
            _require_commit(target, "product disposition integration head")
        dispositions[product_commit] = disposition

    visiting_products: set[str] = set()
    visited_products: set[str] = set()

    def visit_product(commit: str) -> None:
        if commit in visiting_products:
            raise WorkGraphError(f"qualified product composition cycle includes {commit}")
        if commit in visited_products:
            return
        visiting_products.add(commit)
        disposition = dispositions[commit]
        if disposition["kind"] == "COMPOSED":
            visit_product(str(disposition["target"]))
        visiting_products.remove(commit)
        visited_products.add(commit)

    for commit in sorted(commits):
        visit_product(commit)
    for commit, disposition in dispositions.items():
        if disposition["kind"] == "COMPOSED":
            target_disposition = dispositions[str(disposition["target"])]
            if target_disposition["kind"] in {"SUPERSEDED", "REJECTED"}:
                raise WorkGraphError(
                    f"product disposition: composition target is not current {disposition['target']}"
                )

    authorizations_value = contract["composition_authorizations"]
    if type(authorizations_value) is not list:
        raise WorkGraphError("composition authorizations: array required")
    authorizations: list[dict[str, JSONValue]] = []
    reviews = {str(binding["review_sha256"]) for binding in bindings.values()}
    for index, value in enumerate(authorizations_value):
        item = _require_object(value, f"composition authorization {index}")
        if set(item) != {
            "owner", "products", "qualification_review_sha256", "integration_authority"
        }:
            raise WorkGraphError(f"composition authorization {index}: exact members required")
        owner = _require_string(item["owner"], "composition authorization owner")
        if owner not in by_id:
            raise WorkGraphError(f"composition authorization {index}: unknown cell {owner}")
        products = [
            _require_commit(product, "composition authorization product")
            for product in _require_string_list(
                item["products"], "composition authorization products"
            )
        ]
        if products != sorted(products) or any(product not in commits for product in products):
            raise WorkGraphError(f"composition authorization {index}: unknown current product")
        review = _require_digest(
            item["qualification_review_sha256"], "composition authorization review"
        )
        if review not in reviews:
            raise WorkGraphError(f"composition authorization {index}: unbound qualification review")
        if item["integration_authority"] != receipt:
            raise WorkGraphError(f"composition authorization {index}: unresolved integration authority")
        if any(canonical_json_v1(item) == canonical_json_v1(prior) for prior in authorizations):
            raise WorkGraphError("duplicate composition authorization")
        authorizations.append(item)

    consumers_value = contract["future_consumers"]
    if type(consumers_value) is not list:
        raise WorkGraphError("future consumers: array required")
    future_consumers: list[dict[str, JSONValue]] = []
    for index, value in enumerate(consumers_value):
        item = _require_object(value, f"future consumer {index}")
        if set(item) != {"product_commit", "cell_id"}:
            raise WorkGraphError(f"future consumer {index}: exact members required")
        product_commit = _require_commit(item["product_commit"], "future consumer product")
        cell_id = _require_string(item["cell_id"], "future consumer cell")
        if product_commit not in commits or cell_id not in by_id:
            raise WorkGraphError(f"future consumer {index}: unresolved binding")
        if dispositions[product_commit]["kind"] in {"SUPERSEDED", "REJECTED"}:
            raise WorkGraphError(f"future consumer {index}: product is not current")
        if any(canonical_json_v1(item) == canonical_json_v1(prior) for prior in future_consumers):
            raise WorkGraphError("duplicate future consumer")
        future_consumers.append(item)

    return {
        "authority": source,
        "source_cells": sorted(source_cells),
        "non_cell_owners": non_cell_owners,
        "join_owners": join_owners,
        "bindings": bindings,
        "commits": commits,
        "dispositions": dispositions,
        "composition_authorizations": authorizations,
        "future_consumers": future_consumers,
    }


def _validate_preparation_v1(
    cell: dict[str, JSONValue],
    by_id: dict[str, dict[str, JSONValue]],
    groups: dict[str, JSONValue],
) -> dict[str, JSONValue]:
    cell_id = str(cell["id"])
    value = _require_object(cell["preparation"], f"cell {cell_id} preparation")
    expected = {
        "kinds",
        "effect_class",
        "final_composed_only",
        "execution_unavailable",
        "rank",
        "record",
    }
    if set(value) != expected:
        raise WorkGraphError(f"cell {cell_id}: incomplete preparation declaration")
    kinds = _require_string_list(value["kinds"], f"cell {cell_id} preparation kinds")
    if kinds != sorted(kinds) or not set(kinds) <= PREPARATION_KINDS:
        raise WorkGraphError(f"cell {cell_id}: invalid preparation kinds")
    if value["effect_class"] != "READ_ONLY_EFFECT_FREE":
        raise WorkGraphError(f"cell {cell_id}: preparation must be effect-free")
    if type(value["final_composed_only"]) is not bool or value["final_composed_only"]:
        raise WorkGraphError(f"cell {cell_id}: final-composed-only preparation forbidden")

    unavailable = _require_object(
        value["execution_unavailable"], f"cell {cell_id} execution_unavailable"
    )
    states = {name: str(item["state"]) for name, item in by_id.items()}
    required_predecessors = {str(dep) for dep in cell["deps"]}  # type: ignore[union-attr]
    if cell["state"] == "BLOCKED":
        if set(unavailable) != {"kind", "dependencies"} or unavailable["kind"] != "UNMET_DEPENDENCIES":
            raise WorkGraphError(f"cell {cell_id}: blocked preparation needs dependencies")
        declared = _require_string_list(
            unavailable["dependencies"], f"cell {cell_id} preparation dependencies"
        )
        actual = sorted(str(dep) for dep in cell["deps"] if states[str(dep)] != "DONE")  # type: ignore[union-attr]
        if declared != actual:
            raise WorkGraphError(f"cell {cell_id}: preparation dependency binding mismatch")
    elif cell["state"] == "READY":
        if set(unavailable) != {"kind", "group", "holders"} or unavailable["kind"] != "LIVE_HOLD":
            raise WorkGraphError(f"cell {cell_id}: ready preparation needs live hold")
        group = _require_string(unavailable["group"], f"cell {cell_id} preparation group")
        holders = _require_string_list(
            unavailable["holders"], f"cell {cell_id} preparation holders"
        )
        members = groups.get(group)
        if type(members) is not list or cell_id not in members:
            raise WorkGraphError(f"cell {cell_id}: unresolved preparation hold")
        actual_holders = sorted(
            str(member) for member in members if states[str(member)] == "ACTIVE"
        )
        if holders != actual_holders or not holders:
            raise WorkGraphError(f"cell {cell_id}: preparation live-holder mismatch")
        required_predecessors.update(holders)
    else:
        raise WorkGraphError(f"cell {cell_id}: state is not preparation-eligible")

    rank = _require_object(value["rank"], f"cell {cell_id} preparation rank")
    rank_fields = {
        "terminal_unlock_value",
        "expected_reuse",
        "cost",
        "invalidation_risk",
    }
    if set(rank) != rank_fields or any(
        type(rank[name]) is not int or rank[name] < 0 for name in rank_fields
    ):
        raise WorkGraphError(f"cell {cell_id}: invalid preparation rank")

    record = _require_object(value["record"], f"cell {cell_id} preparation record")
    record_fields = {
        "graph_path",
        "receipt",
        "predecessors",
        "interface_assumptions",
        "inspected_paths",
        "proposed_paths",
        "allowed_work",
        "forbidden_work",
        "cost_boundary",
        "invalidators",
        "activation_revalidation",
    }
    if set(record) != record_fields:
        raise WorkGraphError(f"cell {cell_id}: incomplete preparation record")
    _require_string(record["graph_path"], f"cell {cell_id} graph_path")
    receipt = _require_string(record["receipt"], f"cell {cell_id} receipt")
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError(f"cell {cell_id}: invalid continuity receipt")
    predecessors = record["predecessors"]
    if type(predecessors) is not list or not predecessors:
        raise WorkGraphError(f"cell {cell_id}: predecessor observations required")
    seen: set[str] = set()
    for index, item in enumerate(predecessors):
        predecessor = _require_object(item, f"cell {cell_id} predecessor {index}")
        if set(predecessor) != {"cell_id", "state", "identity"}:
            raise WorkGraphError(f"cell {cell_id}: invalid predecessor observation")
        predecessor_id = _require_string(predecessor["cell_id"], f"cell {cell_id} predecessor")
        if predecessor_id in seen or predecessor_id not in by_id:
            raise WorkGraphError(f"cell {cell_id}: fabricated or duplicate predecessor")
        seen.add(predecessor_id)
        if predecessor["state"] != by_id[predecessor_id]["state"]:
            raise WorkGraphError(f"cell {cell_id}: stale predecessor state")
        identity = _require_object(
            predecessor["identity"], f"cell {cell_id} predecessor identity"
        )
        predecessor_cell = by_id[predecessor_id]
        if predecessor_cell["state"] == "DONE" and predecessor_cell.get("source_bearing") is True:
            product_result = _validate_product_result_v1(
                predecessor_cell.get("result"),
                f"cell {predecessor_id} result",
                by_id,
            )
            product = _require_object(product_result["product"], "predecessor product")
            expected_identity: dict[str, JSONValue] = {
                "kind": "QUALIFIED_PRODUCT",
                "commit": product["commit"],
                "tree": product["tree"],
                "review_sha256": product["review_sha256"],
            }
        else:
            expected_identity = {
                "kind": "UNAVAILABLE",
                "reason": (
                    "NOT_DONE"
                    if predecessor_cell["state"] != "DONE"
                    else "NON_SOURCE_PRODUCT"
                ),
            }
        if identity != expected_identity:
            raise WorkGraphError(
                f"cell {cell_id}: predecessor identity mismatch for {predecessor_id}"
            )
    if seen != required_predecessors:
        missing = sorted(required_predecessors - seen)
        extra = sorted(seen - required_predecessors)
        raise WorkGraphError(
            f"cell {cell_id}: predecessor set mismatch; missing={missing}; extra={extra}"
        )
    assumptions = _require_object(
        record["interface_assumptions"], f"cell {cell_id} interface assumptions"
    )
    if not assumptions:
        raise WorkGraphError(f"cell {cell_id}: interface assumptions required")
    for key, digest in assumptions.items():
        _require_string(key, f"cell {cell_id} assumption key")
        _require_digest(digest, f"cell {cell_id} assumption {key}")
    _require_string_list(record["inspected_paths"], f"cell {cell_id} inspected_paths")
    _require_string_list(record["proposed_paths"], f"cell {cell_id} proposed_paths")
    allowed = _require_string_list(record["allowed_work"], f"cell {cell_id} allowed_work")
    if allowed != kinds:
        raise WorkGraphError(f"cell {cell_id}: allowed work must equal declared kinds")
    forbidden = set(
        _require_string_list(record["forbidden_work"], f"cell {cell_id} forbidden_work")
    )
    if forbidden != PREPARATION_FORBIDDEN:
        raise WorkGraphError(f"cell {cell_id}: incomplete forbidden-work boundary")
    _require_string(record["cost_boundary"], f"cell {cell_id} cost_boundary")
    invalidators = set(
        _require_string_list(record["invalidators"], f"cell {cell_id} invalidators")
    )
    if not {"TARGET_STATE", "DEPENDENCY_RESULT", "INTERFACE_ASSUMPTION"} <= invalidators:
        raise WorkGraphError(f"cell {cell_id}: incomplete invalidation boundary")
    activation = set(
        _require_string_list(
            record["activation_revalidation"], f"cell {cell_id} activation_revalidation"
        )
    )
    if activation != {
        "CURRENTNESS", "DEPENDENCY_RESULTS", "INTERFACE_ASSUMPTIONS", "CAUSAL_RED"
    }:
        raise WorkGraphError(f"cell {cell_id}: incomplete activation revalidation")
    return value


def _validate_graph(
    graph: dict[str, JSONValue], product_authority_bytes: bytes | None = None
) -> list[dict[str, JSONValue]]:
    if graph.get("schema") != "implementaudit.work-graph.v1":
        raise WorkGraphError("WORK_GRAPH.json: unsupported schema")

    population = _require_object(graph.get("population"), "$.population")
    declared_total = population.get("total_cells")
    if type(declared_total) is not int or declared_total < 0:
        raise WorkGraphError("$.population.total_cells: non-negative integer required")

    cells_value = graph.get("cells")
    if type(cells_value) is not list:
        raise WorkGraphError("$.cells: array required")
    cells: list[dict[str, JSONValue]] = []
    by_id: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(cells_value):
        cell = _require_object(value, f"$.cells[{index}]")
        cell_id = _require_string(cell.get("id"), f"$.cells[{index}].id")
        if cell_id in by_id:
            raise WorkGraphError(f"duplicate cell id: {cell_id}")
        state = cell.get("state")
        if state not in KNOWN_STATES:
            raise WorkGraphError(f"unknown cell state for {cell_id}: {state}")
        deps = cell.get("deps")
        if type(deps) is not list:
            raise WorkGraphError(f"cell {cell_id}: deps array required")
        seen_deps: set[str] = set()
        for dep in deps:
            dep_id = _require_string(dep, f"cell {cell_id} dependency")
            if dep_id in seen_deps:
                raise WorkGraphError(f"cell {cell_id}: duplicate dependency {dep_id}")
            seen_deps.add(dep_id)
        cells.append(cell)
        by_id[cell_id] = cell

    counts = {
        state: sum(cell["state"] == state for cell in cells)
        for state in KNOWN_STATES
    }
    if len(cells) != declared_total or sum(counts.values()) != declared_total:
        raise WorkGraphError("frontier count does not equal population")

    for cell in cells:
        cell_id = str(cell["id"])
        for dep in cell["deps"]:  # type: ignore[union-attr]
            if dep not in by_id:
                raise WorkGraphError(f"cell {cell_id}: unknown dependency {dep}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(cell_id: str) -> None:
        if cell_id in visiting:
            raise WorkGraphError(f"dependency cycle includes {cell_id}")
        if cell_id in visited:
            return
        visiting.add(cell_id)
        for dep in by_id[cell_id]["deps"]:  # type: ignore[union-attr]
            visit(str(dep))
        visiting.remove(cell_id)
        visited.add(cell_id)

    for cell_id in sorted(by_id):
        visit(cell_id)

    groups = graph.get("serialization_groups")
    if type(groups) is not dict:
        raise WorkGraphError("$.serialization_groups: writer/resource holds required")
    for group, members in groups.items():
        _require_string(group, "serialization group name")
        if not (group.startswith("W_") or group.startswith("R_")
                or group.startswith("RESOURCE_")):
            raise WorkGraphError(f"serialization group {group}: unknown hold kind")
        if type(members) is not list or not members:
            raise WorkGraphError(f"serialization group {group}: non-empty array required")
        seen_members: set[str] = set()
        for member in members:
            member_id = _require_string(member, f"serialization group {group}")
            if member_id not in by_id:
                raise WorkGraphError(
                    f"serialization group {group}: unknown cell {member_id}"
                )
            if member_id in seen_members:
                raise WorkGraphError(
                    f"serialization group {group}: duplicate cell {member_id}"
                )
            seen_members.add(member_id)

    for cell in cells:
        cell_id = str(cell["id"])
        if "source_bearing" in cell and type(cell["source_bearing"]) is not bool:
            raise WorkGraphError(f"cell {cell_id}: source_bearing must be boolean")
        if "preparation" in cell:
            _validate_preparation_v1(cell, by_id, groups)

    product_contract = _validate_product_contract_v1(
        graph, cells, by_id, product_authority_bytes
    )
    for cell in cells:
        cell_id = str(cell["id"])
        if cell.get("source_bearing") is True:
            if cell["state"] != "DONE":
                raise WorkGraphError(f"cell {cell_id}: unqualified source result forbidden")
            result = _validate_product_result_v1(
                cell.get("result"), f"cell {cell_id} result", by_id
            )
            if product_contract is None:
                raise WorkGraphError("qualified product contract required for governed products")
            bindings = product_contract["bindings"]
            dispositions = product_contract["dispositions"]
            assert type(bindings) is dict and type(dispositions) is dict
            binding = bindings.get(("CELL", cell_id))
            if type(binding) is not dict:
                raise WorkGraphError(f"cell {cell_id}: authoritative product binding missing")
            product = _require_object(result["product"], f"cell {cell_id} result.product")
            if product != {
                "commit": binding["commit"],
                "tree": binding["tree"],
                "review_sha256": binding["review_sha256"],
            }:
                raise WorkGraphError(f"cell {cell_id}: product identity disagrees with authority")
            disposition = _require_object(
                result["disposition"], f"cell {cell_id} result.disposition"
            )
            bound_disposition = dispositions.get(str(product["commit"]))
            if type(bound_disposition) is not dict or disposition != {
                "kind": bound_disposition["kind"],
                "target": bound_disposition["target"],
            }:
                raise WorkGraphError(f"cell {cell_id}: product disposition disagrees with authority")

    frontier = graph.get("frontier")
    if frontier is not None:
        cached = _require_object(frontier, "$.frontier")
        expected_scalars = {
            "population": declared_total,
            "done": counts["DONE"],
            "active": counts["ACTIVE"],
            "ready": counts["READY"],
            "blocked": counts["BLOCKED"],
        }
        if any(cached.get(key) != value for key, value in expected_scalars.items()):
            raise WorkGraphError("stale frontier projection")
        for key, state in (("active_ids", "ACTIVE"), ("ready_ids", "READY")):
            expected_ids = sorted(
                str(cell["id"]) for cell in cells if cell["state"] == state
            )
            if cached.get(key) != expected_ids:
                raise WorkGraphError(f"stale frontier projection: {key}")

    digest = graph.get("digest")
    if digest is not None:
        if type(digest) is not str or not DIGEST_RE.fullmatch(digest):
            raise WorkGraphError("WORK_GRAPH.json: invalid digest")
        unsigned = dict(graph)
        del unsigned["digest"]
        expected_digest = hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()
        if not hmac.compare_digest(digest, expected_digest):
            raise WorkGraphError("WORK_GRAPH.json: stale digest")

    return cells


def summarize_blocked_v1(
    cells: list[dict[str, JSONValue]],
) -> dict[str, JSONValue]:
    states = {str(cell["id"]): str(cell["state"]) for cell in cells}
    summary: dict[str, JSONValue] = {}
    for cell in sorted(cells, key=lambda item: str(item["id"])):
        if cell["state"] != "BLOCKED":
            continue
        summary[str(cell["id"])] = sorted(
            str(dep)
            for dep in cell["deps"]  # type: ignore[union-attr]
            if states[str(dep)] != "DONE"
        )
    return summary


def normalize_holds_v1(
    serialization_groups: JSONValue, kind: str
) -> dict[str, JSONValue]:
    groups = _require_object(serialization_groups, "$.serialization_groups")
    if kind == "writer":
        selected = lambda name: name.startswith("W_")
    elif kind == "resource":
        selected = lambda name: name.startswith("R_") or name.startswith("RESOURCE_")
    else:
        raise WorkGraphError(f"unknown hold kind: {kind}")
    return {
        group: sorted(str(member) for member in members)  # type: ignore[union-attr]
        for group, members in sorted(groups.items())
        if selected(group)
    }


def compile_preparation_frontier_v1(
    graph: dict[str, JSONValue],
    cells: list[dict[str, JSONValue]],
    graph_bytes: bytes,
) -> list[dict[str, JSONValue]]:
    graph_id = graph.get("graph_id")
    prepared = [cell for cell in cells if "preparation" in cell]
    if not prepared:
        return []
    _require_string(graph_id, "$.graph_id")
    records: list[dict[str, JSONValue]] = []
    for cell in prepared:
        cell_id = str(cell["id"])
        declaration = _require_object(cell["preparation"], f"cell {cell_id} preparation")
        rank = _require_object(declaration["rank"], f"cell {cell_id} rank")
        source_record = _require_object(
            declaration["record"], f"cell {cell_id} preparation record"
        )
        unavailable = _require_object(
            declaration["execution_unavailable"], f"cell {cell_id} unavailable"
        )
        target_binding = {
            "cell_id": cell_id,
            "state": cell["state"],
            "deps": sorted(str(dep) for dep in cell["deps"]),  # type: ignore[union-attr]
            "unavailable": unavailable,
            "predecessors": source_record["predecessors"],
            "interface_assumptions": source_record["interface_assumptions"],
            "inspected_paths": sorted(str(path) for path in source_record["inspected_paths"]),  # type: ignore[union-attr]
            "proposed_paths": sorted(str(path) for path in source_record["proposed_paths"]),  # type: ignore[union-attr]
        }
        record: dict[str, JSONValue] = {
            "schema": "implementaudit.preparation-record.v1",
            "graph": {
                "schema": graph["schema"],
                "id": graph_id,
                "path": source_record["graph_path"],
                "bytes": len(graph_bytes),
                "sha256": hashlib.sha256(graph_bytes).hexdigest(),
            },
            "receipt": source_record["receipt"],
            "cell_id": cell_id,
            "observed_state": cell["state"],
            "execution_unavailable": unavailable,
            "predecessors": source_record["predecessors"],
            "interface_assumptions": source_record["interface_assumptions"],
            "inspected_paths": sorted(str(path) for path in source_record["inspected_paths"]),  # type: ignore[union-attr]
            "proposed_paths": sorted(str(path) for path in source_record["proposed_paths"]),  # type: ignore[union-attr]
            "allowed_work": declaration["kinds"],
            "forbidden_work": sorted(str(item) for item in source_record["forbidden_work"]),  # type: ignore[union-attr]
            "rank": rank,
            "cost_boundary": source_record["cost_boundary"],
            "invalidators": source_record["invalidators"],
            "activation_revalidation": source_record["activation_revalidation"],
            "target_binding_sha256": hashlib.sha256(
                canonical_json_v1(target_binding)
            ).hexdigest(),
            "lifecycle_credit": "NONE",
            "implementation_evidence": "NONE",
            "authority_minted": "NONE",
        }
        record["record_sha256"] = hashlib.sha256(canonical_json_v1(record)).hexdigest()
        records.append(record)
    return sorted(
        records,
        key=lambda record: (
            -int(_require_object(record["rank"], "rank")["terminal_unlock_value"]),
            -int(_require_object(record["rank"], "rank")["expected_reuse"]),
            int(_require_object(record["rank"], "rank")["cost"]),
            int(_require_object(record["rank"], "rank")["invalidation_risk"]),
            str(record["cell_id"]),
        ),
    )


def validate_preparation_activation_v1(
    record: dict[str, JSONValue],
    *,
    current_receipt: str,
    current_graph_bytes: bytes,
    causal_red_passed: bool,
    current_product_authority_bytes: bytes | None = None,
) -> bool:
    """Fail closed unless every activation-time invalidator is re-observed."""
    if record.get("schema") != "implementaudit.preparation-record.v1":
        raise WorkGraphError("preparation activation: unknown record schema")
    stored_hash = _require_digest(
        record.get("record_sha256"), "preparation activation record_sha256"
    )
    unsigned = dict(record)
    del unsigned["record_sha256"]
    if not hmac.compare_digest(
        stored_hash, hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()
    ):
        raise WorkGraphError("preparation activation: stale record digest")
    if not RECEIPT_RE.fullmatch(current_receipt) or current_receipt != record.get("receipt"):
        raise WorkGraphError("preparation activation: currentness revalidation failed")
    if type(causal_red_passed) is not bool or not causal_red_passed:
        raise WorkGraphError("preparation activation: causal RED not revalidated")
    try:
        current_projection = compile_frontier_projection(
            current_graph_bytes, current_product_authority_bytes
        )
    except WorkGraphError as exc:
        raise WorkGraphError(
            f"preparation activation: current graph revalidation failed: {exc}"
        ) from exc
    current_records = current_projection.get("preparation_frontier", [])
    if type(current_records) is not list:
        raise WorkGraphError("preparation activation: current preparation frontier missing")
    current = next(
        (
            item
            for item in current_records
            if type(item) is dict and item.get("cell_id") == record.get("cell_id")
        ),
        None,
    )
    if current is None:
        raise WorkGraphError("preparation activation: current preparation record missing")
    if current.get("target_binding_sha256") != record.get("target_binding_sha256"):
        raise WorkGraphError("preparation activation: target binding changed")
    if canonical_json_v1(current.get("predecessors")) != canonical_json_v1(
        record.get("predecessors")
    ):
        raise WorkGraphError("preparation activation: dependency results changed")
    if canonical_json_v1(current.get("interface_assumptions")) != canonical_json_v1(
        record.get("interface_assumptions")
    ):
        raise WorkGraphError("preparation activation: interface assumptions changed")
    return True


def compile_product_frontier_v1(
    graph: dict[str, JSONValue],
    cells: list[dict[str, JSONValue]],
    product_authority_bytes: bytes | None = None,
) -> dict[str, JSONValue] | None:
    by_id = {str(cell["id"]): cell for cell in cells}
    contract = _validate_product_contract_v1(
        graph, cells, by_id, product_authority_bytes
    )
    if contract is None:
        return None
    bindings = contract["bindings"]
    dispositions = contract["dispositions"]
    assert type(bindings) is dict and type(dispositions) is dict
    entries: list[dict[str, JSONValue]] = []
    for cell in cells:
        if cell.get("source_bearing") is not True or cell["state"] != "DONE":
            continue
        result = _validate_product_result_v1(
            cell["result"], f"cell {cell['id']} result", by_id
        )
        entries.append({"owner_kind": "CELL", "owner": cell["id"], **result})

    topology = graph.get("integration_topology")
    if type(topology) is dict and "qualified_products" in topology:
        noncells = topology["qualified_products"]
        if type(noncells) is not list:
            raise WorkGraphError("$.integration_topology.qualified_products: array required")
        seen_owners: set[str] = set()
        for index, item in enumerate(noncells):
            entry = _require_object(item, f"non-cell product {index}")
            if set(entry) != {"owner", "result"}:
                raise WorkGraphError("non-cell product: owner and result required")
            owner = _require_string(entry["owner"], f"non-cell product {index} owner")
            if owner in seen_owners:
                raise WorkGraphError(f"duplicate non-cell product owner: {owner}")
            seen_owners.add(owner)
            result = _validate_product_result_v1(
                entry["result"], f"non-cell product {owner} result", by_id
            )
            binding = bindings.get(("NON_CELL", owner))
            if type(binding) is not dict:
                raise WorkGraphError(f"non-cell product {owner}: unknown authoritative owner")
            product = _require_object(result["product"], f"non-cell product {owner} product")
            if product != {
                "commit": binding["commit"],
                "tree": binding["tree"],
                "review_sha256": binding["review_sha256"],
            }:
                raise WorkGraphError(f"non-cell product {owner}: identity disagrees with authority")
            disposition = _require_object(
                result["disposition"], f"non-cell product {owner} disposition"
            )
            bound_disposition = dispositions.get(str(product["commit"]))
            if type(bound_disposition) is not dict or disposition != {
                "kind": bound_disposition["kind"],
                "target": bound_disposition["target"],
            }:
                raise WorkGraphError(
                    f"non-cell product {owner}: disposition disagrees with authority"
                )
            entries.append({"owner_kind": "NON_CELL", "owner": owner, **result})
    if not entries:
        raise WorkGraphError("qualified product contract has no realised products")

    product_by_commit: dict[str, dict[str, JSONValue]] = {}
    for entry in entries:
        product = _require_object(entry["product"], "product")
        commit = str(product["commit"])
        if commit in product_by_commit:
            raise WorkGraphError(f"qualified product emitted more than once: {commit}")
        product_by_commit[commit] = entry
    if set(product_by_commit) != set(contract["commits"]):  # type: ignore[arg-type]
        raise WorkGraphError("qualified product runtime entries do not cover authority census")

    integration_heads: set[str] = set()
    if type(topology) is dict and "integration_heads" in topology:
        for head in _require_string_list(
            topology["integration_heads"], "$.integration_topology.integration_heads"
        ):
            integration_heads.add(_require_commit(head, "integration head"))
    for entry in entries:
        product = _require_object(entry["product"], "product")
        disposition = _require_object(entry["disposition"], "disposition")
        kind = str(disposition["kind"])
        target = str(disposition["target"])
        if kind == "INTEGRATED" and target not in integration_heads:
            raise WorkGraphError(f"product {product['commit']}: unknown integration head {target}")
        if kind in {"SUPERSEDED", "REJECTED"}:
            if target not in product_by_commit:
                raise WorkGraphError(f"product {product['commit']}: unknown product identity {target}")
            if kind == "SUPERSEDED" and target == product["commit"]:
                raise WorkGraphError(f"product {product['commit']}: self-supersession forbidden")

    entries.sort(
        key=lambda entry: (
            str(entry["owner_kind"]),
            str(entry["owner"]),
            str(_require_object(entry["product"], "product")["commit"]),
        )
    )
    counts = {kind: 0 for kind in sorted(PRODUCT_DISPOSITIONS)}
    target_counts: dict[str, int] = {}
    for entry in entries:
        disposition = _require_object(entry["disposition"], "disposition")
        kind = str(disposition["kind"])
        counts[kind] += 1
    future_consumers = contract["future_consumers"]
    assert type(future_consumers) is list
    for item in future_consumers:
        assert type(item) is dict
        cell_id = str(item["cell_id"])
        target_counts[cell_id] = target_counts.get(cell_id, 0) + 1

    proposals: list[dict[str, JSONValue]] = []
    if type(topology) is dict and "composition_proposals" in topology:
        raw_proposals = topology["composition_proposals"]
        if type(raw_proposals) is not list:
            raise WorkGraphError("$.integration_topology.composition_proposals: array required")
        states = {str(cell["id"]): str(cell["state"]) for cell in cells}
        groups = _require_object(graph["serialization_groups"], "$.serialization_groups")
        seen_proposals: set[str] = set()
        current_commits = {
            commit
            for commit, entry in product_by_commit.items()
            if _require_object(entry["disposition"], "disposition")["kind"]
            not in {"SUPERSEDED", "REJECTED"}
        }
        for index, value in enumerate(raw_proposals):
            proposal = _require_object(value, f"composition proposal {index}")
            if set(proposal) != {
                "owner", "products", "qualification_review_sha256", "integration_authority"
            }:
                raise WorkGraphError(f"composition proposal {index}: exact members required")
            owner = _require_string(proposal["owner"], f"composition proposal {index} owner")
            if owner in seen_proposals:
                raise WorkGraphError(f"duplicate composition proposal owner: {owner}")
            seen_proposals.add(owner)
            if owner not in by_id:
                raise WorkGraphError(f"composition proposal {index}: unknown cell {owner}")
            product_commits = [
                _require_commit(item, f"composition proposal {index} product")
                for item in _require_string_list(
                    proposal["products"], f"composition proposal {index} products"
                )
            ]
            if product_commits != sorted(product_commits):
                raise WorkGraphError(f"composition proposal {index}: products must be sorted")
            if any(commit not in current_commits for commit in product_commits):
                raise WorkGraphError(f"composition proposal {index}: unknown current product")
            _require_digest(
                proposal["qualification_review_sha256"],
                f"composition proposal {index} qualification review",
            )
            authority = _require_string(
                proposal["integration_authority"],
                f"composition proposal {index} integration authority",
            )
            if not RECEIPT_RE.fullmatch(authority):
                raise WorkGraphError(f"composition proposal {index}: unresolved integration authority")
            authorizations = contract["composition_authorizations"]
            assert type(authorizations) is list
            if not any(
                canonical_json_v1(proposal) == canonical_json_v1(item)
                for item in authorizations
            ):
                raise WorkGraphError(
                    f"composition proposal {index}: not present in authoritative bindings"
                )
            cell = by_id[owner]
            if cell["state"] != "READY" or any(
                states[str(dep)] != "DONE" for dep in cell["deps"]  # type: ignore[union-attr]
            ):
                raise WorkGraphError(f"composition proposal {index}: dependencies do not permit composition")
            active_conflicts = sorted(
                str(member)
                for members in groups.values()
                if type(members) is list and owner in members
                for member in members
                if member != owner and states[str(member)] == "ACTIVE"
            )
            if active_conflicts:
                raise WorkGraphError(f"composition proposal {index}: live hold conflict")
            proposals.append(
                {
                    "owner": owner,
                    "products": product_commits,
                    "qualification_review_sha256": proposal["qualification_review_sha256"],
                    "integration_authority": authority,
                }
            )
        proposals.sort(key=lambda item: (str(item["owner"]), item["products"]))

    ready = [str(cell["id"]) for cell in cells if cell["state"] == "READY"]
    preparation_ids = [
        str(cell["id"]) for cell in cells if "preparation" in cell
    ]
    summary = summarize_product_dispositions_v1(
        [
            str(_require_object(entry["disposition"], "disposition")["kind"])
            for entry in entries
        ]
    )
    return {
        "qualified_products": len(entries),
        "current_products": len(entries) - counts["SUPERSEDED"] - counts["REJECTED"],
        "integration_debt": (
            counts["COMPOSED"] + counts["EXPLICITLY_DEFERRED_TO_NAMED_JOIN"]
        ),
        "counts": counts,
        "potentially_stranded": summary["potentially_stranded"],
        "p0_execution_planning_escalation": summary["p0"],
        "products": entries,
        "composition_proposals": proposals,
        "ready_preference": sorted(
            ready, key=lambda cell_id: (-target_counts.get(cell_id, 0), cell_id)
        ),
        "preparation_preference": sorted(
            preparation_ids,
            key=lambda cell_id: (-target_counts.get(cell_id, 0), cell_id),
        ),
    }


def summarize_product_dispositions_v1(
    dispositions: list[str | None],
) -> dict[str, JSONValue]:
    counts = {kind: 0 for kind in PRODUCT_DISPOSITIONS}
    stranded = 0
    for index, kind in enumerate(dispositions):
        if kind is None:
            stranded += 1
        elif kind in counts:
            counts[kind] += 1
        else:
            raise WorkGraphError(
                f"product disposition {index}: unknown disposition {kind}"
            )
    return {
        "total": len(dispositions),
        "consumed": counts["CONSUMED"],
        "composed": counts["COMPOSED"],
        "integrated": counts["INTEGRATED"],
        "superseded": counts["SUPERSEDED"],
        "rejected": counts["REJECTED"],
        "deferred": counts["EXPLICITLY_DEFERRED_TO_NAMED_JOIN"],
        "potentially_stranded": stranded,
        "p0": "TRIGGERED" if stranded else "NOT_TRIGGERED",
    }


def compile_frontier_projection(
    graph_bytes: bytes, product_authority_bytes: bytes | None = None
) -> dict[str, JSONValue]:
    decoded = decode_strict_json_bytes(graph_bytes, "WORK_GRAPH.json")
    graph = _require_object(decoded, "WORK_GRAPH.json")
    cells = _validate_graph(graph, product_authority_bytes)
    declared_total = _require_object(graph["population"], "$.population")[
        "total_cells"
    ]
    counts = {
        state: sum(cell["state"] == state for cell in cells)
        for state in KNOWN_STATES
    }
    projection: dict[str, JSONValue] = {
        "population": declared_total,
        "counts": counts,
        "active": sorted(
            str(cell["id"]) for cell in cells if cell["state"] == "ACTIVE"
        ),
        "ready": sorted(
            str(cell["id"]) for cell in cells if cell["state"] == "READY"
        ),
        "blocked_summary": summarize_blocked_v1(cells),
        "writer_holds": normalize_holds_v1(graph["serialization_groups"], "writer"),
        "resource_holds": normalize_holds_v1(
            graph["serialization_groups"], "resource"
        ),
    }
    preparation = compile_preparation_frontier_v1(graph, cells, graph_bytes)
    if preparation:
        projection["preparation_frontier"] = preparation
    products = compile_product_frontier_v1(graph, cells, product_authority_bytes)
    if products is not None:
        projection["product_frontier"] = products
    projection["digest"] = hashlib.sha256(canonical_json_v1(projection)).hexdigest()
    return projection


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print(
            "usage: compile-work-graph.py WORK_GRAPH.json [PRODUCT_AUTHORITY.json]",
            file=sys.stderr,
        )
        return 2
    path = pathlib.Path(argv[1])
    try:
        raw = path.read_bytes()
        authority_bytes = pathlib.Path(argv[2]).read_bytes() if len(argv) == 3 else None
        projection = compile_frontier_projection(raw, authority_bytes)
    except OSError as exc:
        print(f"compile-work-graph: {path}: {exc}", file=sys.stderr)
        return 2
    except WorkGraphError as exc:
        print(f"compile-work-graph: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_json_v1(projection))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
