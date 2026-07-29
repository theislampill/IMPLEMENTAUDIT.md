#!/usr/bin/env python3
"""Contract tests for the separate Luna candidate-matrix artifact envelope."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import shutil
import tempfile


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_contract.py"
DECLARATION = HERE / "candidate_matrix_contract.json"
FREEZE_TEST = HERE / "test_candidate_matrix_freeze.py"
FIXTURES = ["B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
            "E5", "E6", "E7", "E8", "E9", "E10"]
LUNA_MODEL = "gpt-5.6-luna"


def fixture_properties(fixture_id):
    fixture = json.loads(
        (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
            encoding="utf-8"))
    return {
        prop["name"]: prop["required"]
        for prop in fixture["properties"]
    }


def valid_official_luna_result(packet, packet_sha256):
    cells = []
    for index, fixture_id in enumerate(FIXTURES):
        declaration = fixture_properties(fixture_id)
        properties = {
            name: {"state": "PASS", "pass": True}
            for name in declaration
        }
        for name, required in declaration.items():
            if not required and fixture_id in ("B0", "E5"):
                properties[name] = {"state": "FAIL", "pass": False}
        cells.append({
            "index": index, "config": "L", "fixture": fixture_id,
            "execution_mode": "production",
            "product_status": "PASS", "host_status": "PASS",
            "overall_status": "PASS", "properties": properties,
            "reason": None, "bundle_manifest_sha256": "1" * 64,
            "raw_stdout_sha256": "2" * 64,
            "native_session_sha256": "3" * 64,
            "official_overall_status": "PASS",
            "independent_overall_status": "PASS",
            "model_resolved": LUNA_MODEL,
            "official_verdict_sha256": "4" * 64,
        })
    return {
        "schema": "implementaudit-candidate-matrix-luna-result-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "execution_mode": "production",
        "freeze_sha256": packet_sha256,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "accepted": False,
        "cell_count": 14, "cells": cells,
        "luna_identity": {
            "config": packet["configuration"]["id"],
            "host": packet["configuration"]["host"],
            "model_resolved_required":
                packet["configuration"]["model_resolved_required"],
            "host_attestation_id":
                packet["configuration"]["host_attestation"]["id"],
            "host_attestation_sha256":
                packet["configuration"]["host_attestation"]["sha256"],
        },
        "independent_rederivation": {
            "path": "candidate-matrix-luna-independent-rederivation.json",
            "sha256": "8" * 64,
            "schema":
                "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
            "contract_id":
                "implementaudit-candidate-matrix-luna-rederiver-v1",
            "implementation_sha256": "9" * 64,
        },
        "claims": {
            "final_28_of_28": False, "cross_model_qualified": False,
            "release_authorized": False, "tag_authorized": False,
            "publication_authorized": False,
        },
    }


def valid_freeze_packet():
    spec = importlib.util.spec_from_file_location(
        "candidate_matrix_freeze_test_helper", FREEZE_TEST)
    helper = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(helper)
    packet = helper.valid_packet()
    for fixture in packet["fixtures"]:
        fixture["sha256"] = hashlib.sha256(
            (HERE / "fixtures" / fixture["id"] /
             "fixture.json").read_bytes()).hexdigest()
    return packet


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

    packet = valid_freeze_packet()
    packet_raw = module.canonical_json_bytes(packet)
    packet_sha256 = hashlib.sha256(packet_raw).hexdigest()
    accepted_result = valid_official_luna_result(packet, packet_sha256)
    packet_tmp = tempfile.TemporaryDirectory(prefix="matrix-packet-root-")
    packet_root = pathlib.Path(packet_tmp.name) / "accepted"
    packet_root.mkdir()
    packet_path = packet_root / "campaign-freeze.json"
    packet_path.write_bytes(packet_raw)
    packet_root_false_accepts = []
    partial_packet = {"campaign": packet["campaign"]}
    for label, result_value, context_value, asserted_sha in (
            ("partial-packet", accepted_result, partial_packet,
             packet_sha256),
            ("arbitrary-packet-sha",
             {**accepted_result, "freeze_sha256": "b" * 64},
             partial_packet, "b" * 64),
            ("non-current-contract",
             {**accepted_result, "contract_sha256": "b" * 64},
             {**partial_packet,
              "artifact_contract": {"sha256": "b" * 64}},
             packet_sha256)):
        try:
            module.validate_artifact(
                "official_luna_result", result_value,
                packet=context_value, packet_sha256=asserted_sha)
        except (OSError, TypeError, ValueError):
            pass
        else:
            packet_root_false_accepts.append(label)
    assert not packet_root_false_accepts, (
        "official result accepted caller-forged packet root: " +
        ", ".join(packet_root_false_accepts))
    validate_result = lambda value: module.validate_artifact(
        "official_luna_result", value, packet_path=packet_path,
        packet_root=packet_root)
    validate_result(accepted_result)
    test_only_result = copy.deepcopy(accepted_result)
    test_only_result["execution_mode"] = "test"
    for row in test_only_result["cells"]:
        row["execution_mode"] = "test"
    reject(lambda: validate_result(test_only_result))
    mixed_mode_result = copy.deepcopy(accepted_result)
    mixed_mode_result["cells"][7]["execution_mode"] = "test"
    reject(lambda: validate_result(mixed_mode_result))
    reject(lambda: module.validate_artifact(
        "official_luna_result", accepted_result,
        packet_path=packet_root / "not-the-freeze.json",
        packet_root=packet_root))

    def reject_packet_raw(label, raw, result=accepted_result):
        root = pathlib.Path(packet_tmp.name) / label
        root.mkdir()
        path = root / "campaign-freeze.json"
        path.write_bytes(raw)
        reject(lambda: module.validate_artifact(
            "official_luna_result", result,
            packet_path=path, packet_root=root))

    reject_packet_raw(
        "partial-json",
        module.canonical_json_bytes({"campaign": packet["campaign"]}))
    duplicate_packet_raw = (
        packet_raw[:-2] +
        b',"campaign":"candidate-matrix-sol-luna-r1"}\n')
    reject_packet_raw("duplicate-json-key", duplicate_packet_raw)
    coerced_packet = copy.deepcopy(packet)
    coerced_packet["seed"] = 20260718.0
    reject_packet_raw(
        "type-coercion", module.canonical_json_bytes(coerced_packet))
    for label, field, value in (
            ("wrong-contract-path", "path", "eval/other-contract.json"),
            ("wrong-contract-schema", "schema", "other-contract-v1"),
            ("wrong-contract-hash", "sha256", "b" * 64)):
        changed_packet = copy.deepcopy(packet)
        changed_packet["artifact_contract"][field] = value
        reject_packet_raw(
            label, module.canonical_json_bytes(changed_packet))
    arbitrary_sha_result = copy.deepcopy(accepted_result)
    arbitrary_sha_result["freeze_sha256"] = "b" * 64
    reject(lambda: validate_result(arbitrary_sha_result))
    for field, value in (
            ("path", "eval/fixtures/E1/fixture.json"),
            ("sha256", "b" * 64),
            ("id", "E1")):
        changed_packet = copy.deepcopy(packet)
        changed_packet["fixtures"][0][field] = value
        reject_packet_raw(
            f"fixture-{field}", module.canonical_json_bytes(changed_packet))
    for field, value in (("index", 1), ("config", "O"), ("fixture", "E1")):
        changed_packet = copy.deepcopy(packet)
        changed_packet["cells"][0][field] = value
        reject_packet_raw(
            f"cell-{field}", module.canonical_json_bytes(changed_packet))
    replacement_root = pathlib.Path(packet_tmp.name) / "packet-replacement"
    replacement_root.mkdir()
    replacement_path = replacement_root / "campaign-freeze.json"
    replacement_path.write_bytes(packet_raw)
    module.validate_artifact(
        "official_luna_result", accepted_result,
        packet_path=replacement_path, packet_root=replacement_root)
    replacement_packet = copy.deepcopy(packet)
    replacement_packet["candidate"]["commit"] = "d" * 40
    replacement_path.write_bytes(
        module.canonical_json_bytes(replacement_packet))
    reject(lambda: module.validate_artifact(
        "official_luna_result", accepted_result,
        packet_path=replacement_path, packet_root=replacement_root))
    changed_contract = copy.deepcopy(accepted_result)
    changed_contract["contract_sha256"] = "b" * 64
    reject(lambda: validate_result(changed_contract))
    for field, value in (("index", 1), ("config", "O"), ("fixture", "E1")):
        changed_row = copy.deepcopy(accepted_result)
        changed_row["cells"][0][field] = value
        reject(lambda changed_row=changed_row: validate_result(changed_row))
    b0_properties = accepted_result["cells"][0]["properties"]
    assert b0_properties["agents_update_decision"] == {
        "state": "FAIL", "pass": False}
    e5_properties = accepted_result["cells"][8]["properties"]
    assert e5_properties["current_answer_correctness"] == {
        "state": "FAIL", "pass": False}
    required_fail = copy.deepcopy(accepted_result)
    required_fail["cells"][0]["properties"]["phase_start"] = {
        "state": "FAIL", "pass": False}
    reject(lambda: validate_result(required_fail))
    missing = copy.deepcopy(accepted_result)
    del missing["cells"][0]["properties"]["phase_start"]
    reject(lambda: validate_result(missing))
    extra = copy.deepcopy(accepted_result)
    extra["cells"][0]["properties"]["invented_property"] = {
        "state": "PASS", "pass": True}
    reject(lambda: validate_result(extra))
    false_accepts = []
    with tempfile.TemporaryDirectory(
            prefix="matrix-fixture-replacement-") as tmp:
        replacement_root = pathlib.Path(tmp)
        replacement_eval = replacement_root / "eval"
        shutil.copytree(HERE / "fixtures", replacement_eval / "fixtures")
        b0_path = replacement_eval / "fixtures" / "B0" / "fixture.json"
        replacement = json.loads(b0_path.read_text(encoding="utf-8"))
        next(
            prop for prop in replacement["properties"]
            if prop["name"] == "phase_start")["required"] = False
        b0_path.write_text(
            json.dumps(replacement, indent=1) + "\n", encoding="utf-8")
        replacement_result = copy.deepcopy(accepted_result)
        replacement_result["cells"][0]["properties"]["phase_start"] = {
            "state": "FAIL", "pass": False}
        original_here = module.HERE
        module.HERE = replacement_eval
        try:
            try:
                module.validate_artifact(
                    "official_luna_result", replacement_result,
                    packet_path=packet_path, packet_root=packet_root)
            except (OSError, TypeError, ValueError):
                pass
            else:
                false_accepts.append("ambient-fixture-requiredness-drift")
        finally:
            module.HERE = original_here
    for label, model in (
            ("Sol", "gpt-5.6-sol"),
            ("Terra", "gpt-5.6-terra"),
            ("arbitrary", "not-luna")):
        changed = copy.deepcopy(accepted_result)
        for cell in changed["cells"]:
            cell["model_resolved"] = model
        changed["luna_identity"]["model_resolved_required"] = model
        try:
            validate_result(changed)
        except (OSError, TypeError, ValueError):
            pass
        else:
            false_accepts.append(label)
    single_row = copy.deepcopy(accepted_result)
    single_row["cells"][6]["model_resolved"] = "gpt-5.6-sol"
    try:
        validate_result(single_row)
    except (OSError, TypeError, ValueError):
        pass
    else:
        false_accepts.append("single-row-model-mismatch")
    stage_mismatch = copy.deepcopy(accepted_result)
    stage_mismatch["luna_identity"][
        "model_resolved_required"] = "gpt-5.6-sol"
    try:
        validate_result(stage_mismatch)
    except (OSError, TypeError, ValueError):
        pass
    else:
        false_accepts.append("stage-row-model-mismatch")
    assert not false_accepts, (
        "official accepted-result identity false accepts: " +
        ", ".join(false_accepts))
    packet_tmp.cleanup()

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
