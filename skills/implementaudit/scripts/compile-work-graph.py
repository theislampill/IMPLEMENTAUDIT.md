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


def _validate_graph(graph: dict[str, JSONValue]) -> list[dict[str, JSONValue]]:
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


def compile_frontier_projection(graph_bytes: bytes) -> dict[str, JSONValue]:
    decoded = decode_strict_json_bytes(graph_bytes, "WORK_GRAPH.json")
    graph = _require_object(decoded, "WORK_GRAPH.json")
    cells = _validate_graph(graph)
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
    projection["digest"] = hashlib.sha256(canonical_json_v1(projection)).hexdigest()
    return projection


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: compile-work-graph.py WORK_GRAPH.json", file=sys.stderr)
        return 2
    path = pathlib.Path(argv[1])
    try:
        raw = path.read_bytes()
        projection = compile_frontier_projection(raw)
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
