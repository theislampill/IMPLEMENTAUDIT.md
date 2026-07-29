#!/usr/bin/env python3
"""Deterministic tests for the independent Luna matrix rederiver."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import pathlib
import tempfile

from test_candidate_matrix_freeze import valid_packet


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_rederive.py"
FORBIDDEN = {
    "candidate_matrix_campaign", "campaign_lifecycle", "b3v4_campaign",
    "b3v4_rederive", "b3v4_contract", "hosts", "runner", "adapters",
    "lib.scoring", "eval.lib.scoring",
}


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_rederive", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert not (imports & FORBIDDEN), imports & FORBIDDEN
    module = load_module()
    assert module.FIXTURE_ORDER == (
        "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
        "E5", "E6", "E7", "E8", "E9", "E10")
    assert module._exact_json_equal({"x": [0.0]}, {"x": [0.0]})
    assert not module._exact_json_equal(False, 0)
    assert not module._exact_json_equal(0.0, -0.0)
    claims = module.FINAL_CLAIMS
    assert claims == {
        "final_28_of_28": False,
        "cross_model_qualified": False,
        "release_authorized": False,
        "tag_authorized": False,
        "publication_authorized": False,
    }
    packet = valid_packet()
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        hashlib.sha256(MODULE.read_bytes()).hexdigest()
    module._validate_freeze_contract(packet)
    for alias in (14.0, True):
        changed = json.loads(json.dumps(packet))
        changed["attempt_policy"]["maximum_attempts"] = alias
        try:
            module._validate_freeze_contract(changed)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError("numeric alias accepted by independent contract")

    for raw in (
            b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}',
            b'{"a":NaN}', b'{"a":Infinity}'):
        try:
            module._decode_json(
                raw, "strict retained JSON", "malformed retained JSON", True)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError("malformed retained JSON accepted")

    for fixture_id in module.FIXTURE_ORDER:
        fixture_path = HERE / "fixtures" / fixture_id / "fixture.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        module._validate_fixture_schema(fixture, fixture_id)
        transcript = (HERE / "fixtures" / fixture_id /
                      "transcript_pass.txt").read_text(encoding="utf-8")
        summary_path = (HERE / "fixtures" / fixture_id /
                        "transcript_pass.summary.json")
        summary = (
            json.loads(summary_path.read_text(encoding="utf-8"))
            if summary_path.exists() else {"changed_files": []})
        states = [
            module._eval_rule(
                prop["rule"], {"assistant": transcript}, summary)
            for prop in fixture["properties"] if prop["required"]]
        assert states and all(state is True for state in states), (
            fixture_id, states)

    fixtures = {
        fixture_id: json.loads(
            (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
                encoding="utf-8"))
        for fixture_id in ("B0", "E5", "E6")
    }
    assert "result.json" in module._required_capture_files(fixtures["E5"])
    preimages = {
        "repo": {"lexical_root": "/candidate", "case_sensitive": True},
        "targets": {},
    }
    module._validate_write_boundary(
        [{"effect": "write", "path": "/candidate/task.txt"}],
        fixtures["B0"], preimages)
    module._validate_write_boundary(
        [{"effect": "write",
          "path": "/candidate/.IMPLEMENTAUDIT/run.json"}],
        fixtures["B0"], preimages)
    module._validate_write_boundary(
        [{"effect": "write", "path": "/candidate/docs/analysis.md"}],
        fixtures["E6"], preimages)
    for fixture_id, path in (
            ("B0", "/candidate/src/escape.py"),
            ("E5", "/candidate/result.json"),
            ("E6", "/candidate/src/escape.py")):
        try:
            module._validate_write_boundary(
                [{"effect": "write", "path": path}],
                fixtures[fixture_id], preimages)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"{fixture_id} accepted out-of-bound write {path}")

    result = {
        "schema":
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "freeze_sha256": "a" * 64,
        "contract_sha256": module.CONTRACT_SHA256,
        "luna_stage_status": "INVALID", "disposition": "ANDON_STOPPED",
        "luna_stage_accepted": False, "accepted": False,
        "cell_count": 0, "cells": [], "claims": dict(module.FINAL_CLAIMS),
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        path = root / "candidate-matrix-luna-independent-rederivation.json"
        module.write_rederivation(path, result, root=root)
        assert path.is_file()
        try:
            module.write_rederivation(path, result, root=root)
        except module.EvidenceInvalid as exc:
            assert "create-once" in str(exc)
        else:
            raise AssertionError("independent result overwrite accepted")
    print("candidate matrix rederive: PASS")


if __name__ == "__main__":
    main()
