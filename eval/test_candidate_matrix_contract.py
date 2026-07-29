#!/usr/bin/env python3
"""Contract tests for the separate Luna candidate-matrix artifact envelope."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_contract.py"
DECLARATION = HERE / "candidate_matrix_contract.json"
FIXTURES = ["B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
            "E5", "E6", "E7", "E8", "E9", "E10"]


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_contract", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def reject(fn):
    try:
        fn()
    except (OSError, TypeError, ValueError):
        return
    raise AssertionError("mutation unexpectedly accepted")


def main():
    module = load_module()
    declaration = module.decode_json_bytes(
        DECLARATION.read_bytes(), "matrix contract", require_object=True)
    module.validate_declaration(declaration)
    assert declaration["campaign"] == "candidate-matrix-sol-luna-r1"
    assert declaration["execution"]["fixture_order"] == FIXTURES
    assert declaration["execution"]["configuration"] == "L"
    assert declaration["execution"]["mission_count"] == 14
    assert declaration["execution"]["final_acceptance"] is False
    assert declaration["execution"]["success_disposition"] == \
        "INCOMPLETE_PENDING_OPUS"
    assert "arm" not in declaration["execution"]
    assert "repetition" not in declaration["execution"]
    assert "Opus" not in DECLARATION.read_text(encoding="utf-8")
    assert "Terra" not in DECLARATION.read_text(encoding="utf-8")

    for mutation in (
        FIXTURES[:-1],
        FIXTURES + ["B3"],
        FIXTURES[:1] + FIXTURES[:1] + FIXTURES[2:],
        FIXTURES[:4] + [FIXTURES[5], FIXTURES[4]] + FIXTURES[6:],
    ):
        changed = copy.deepcopy(declaration)
        changed["execution"]["fixture_order"] = mutation
        reject(lambda changed=changed: module.validate_declaration(changed))
    for alias in (14.0, True):
        changed = copy.deepcopy(declaration)
        changed["execution"]["mission_count"] = alias
        reject(lambda changed=changed: module.validate_declaration(changed))
    for field, value in (("arm", "candidate"), ("rep", 1),
                         ("configuration", "O")):
        changed = copy.deepcopy(declaration)
        changed["execution"][field] = value
        reject(lambda changed=changed: module.validate_declaration(changed))

    assert module._exact_json_equal({"x": [0.0]}, {"x": [0.0]})
    assert not module._exact_json_equal(False, 0)
    assert not module._exact_json_equal(0.0, -0.0)
    for raw in (
            b'{"a":1,"a":2}',
            b'{"a":{"b":1,"b":2}}',
            b'{"a":NaN}', b'{"a":Infinity}', b'{"a":-Infinity}'):
        reject(lambda raw=raw: module.decode_json_bytes(
            raw, "strict matrix JSON", require_object=True))
    nested = 0
    for _ in range(500):
        nested = {"x": nested}
    module.decode_json_bytes(
        json.dumps(nested).encode(), "depth boundary", require_object=True)
    for _ in range(200):
        nested = {"x": nested}
    reject(lambda: module.decode_json_bytes(
        json.dumps(nested).encode(), "depth overflow", require_object=True))
    cyclic = {}
    cyclic["cycle"] = cyclic
    reject(lambda: module.canonical_json_bytes(cyclic))
    reject(lambda: module.canonical_json_bytes({"unsupported": object()}))
    assert module.canonical_json_bytes({"value": -0.0}) != \
        module.canonical_json_bytes({"value": 0.0})
    print("candidate matrix contract: PASS")


if __name__ == "__main__":
    main()
