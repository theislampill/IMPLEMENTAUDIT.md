#!/usr/bin/env python3
"""Behavior tests for the create-once Luna integration certificate."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import tempfile

import evaluated_surfaces as surfaces
import provisional_integration as integration


FALSE_CLAIMS_B3 = {
    "final_12_of_12": False, "cross_model_qualified": False,
    "release_authorized": False, "tag_authorized": False,
    "publication_authorized": False,
}
FALSE_CLAIMS_MATRIX = {
    "final_28_of_28": False, "cross_model_qualified": False,
    "release_authorized": False, "tag_authorized": False,
    "publication_authorized": False,
}


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) +
            "\n").encode()


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        if fragment is not None:
            assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected failure containing {fragment!r}")


def _row(index, campaign):
    matrix = campaign == surfaces.MATRIX_CAMPAIGN
    row = {
        "index": index, "config": "L",
        "product_status": "PASS", "host_status": "PASS",
        "overall_status": "PASS", "official_overall_status": "PASS",
        "independent_overall_status": "PASS",
        "properties": {"p": {"state": "PASS", "pass": True}},
        "reason": None, "bundle_manifest_sha256": "a" * 64,
        "raw_stdout_sha256": "b" * 64,
        "native_session_sha256": "c" * 64,
        "model_resolved": "gpt-5.6-luna",
        "official_verdict_sha256": "d" * 64,
    }
    if matrix:
        row.update({
            "fixture": integration.MATRIX_FIXTURES[index],
            "execution_mode": "production",
        })
    else:
        config, arm, rep = integration.B3_PLAN[index]
        row.update({"config": config, "arm": arm, "rep": rep})
    return row


def _stage(campaign):
    matrix = campaign == surfaces.MATRIX_CAMPAIGN
    count = 14 if matrix else 6
    rows = [_row(index, campaign) for index in range(count)]
    claims = FALSE_CLAIMS_MATRIX if matrix else FALSE_CLAIMS_B3
    independent = {
        "schema": (
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1"
            if matrix else
            "implementaudit-b3v4-luna-independent-rederivation-v2"),
        "campaign": campaign, "freeze_sha256": "e" * 64,
        "contract_sha256": "f" * 64,
        "luna_stage_status": "PASS",
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "accepted": False,
        ("cell_count" if matrix else "mission_count"): count,
        ("cells" if matrix else "missions"): rows,
        "claims": claims,
    }
    if matrix:
        independent["execution_mode"] = "production"
    official = {
        "schema": (
            "implementaudit-candidate-matrix-luna-result-v1"
            if matrix else "implementaudit-b3v4-luna-result-v2"),
        "campaign": campaign, "freeze_sha256": "e" * 64,
        "contract_sha256": "f" * 64,
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "accepted": False,
        ("cell_count" if matrix else "mission_count"): count,
        ("cells" if matrix else "missions"): copy.deepcopy(rows),
        "luna_identity": {
            "config": "L", "host": "approved-host",
            "model_resolved_required": "gpt-5.6-luna",
            "host_attestation_id": f"{campaign}-host",
            "host_attestation_sha256": "1" * 64,
        },
        "independent_rederivation": {
            "path": "independent.json",
            "sha256": hashlib.sha256(encoded(independent)).hexdigest(),
            "schema": independent["schema"], "contract_id": "rederiver-v1",
            "implementation_sha256": "2" * 64,
        },
        "claims": claims,
    }
    if matrix:
        official["execution_mode"] = "production"
    return {
        "execution_mode": "production",
        "official": official,
        "independent": independent,
    }


def _binding(root, name, path):
    raw = path.read_bytes()
    return {
        "name": name, "status": "PASS", "path": path.name,
        "byte_length": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _bind_stage(root, stage, prefix):
    official_path = root / f"{prefix}-official.json"
    independent_path = root / f"{prefix}-independent.json"
    official_path.write_bytes(encoded(stage["official"]))
    independent_path.write_bytes(encoded(stage["independent"]))
    official_sha = hashlib.sha256(official_path.read_bytes()).hexdigest()
    independent_sha = hashlib.sha256(
        independent_path.read_bytes()).hexdigest()
    official = stage["official"]
    matrix = official["campaign"] == surfaces.MATRIX_CAMPAIGN
    binding = {
        "campaign": official["campaign"], "stage": "LUNA",
        "stage_schema": (
            "implementaudit-candidate-matrix-luna-stage-v1"
            if matrix else "implementaudit-b3v4-luna-stage-v2"),
        "mission_count": 14 if matrix else 6,
        "freeze_sha256": official["freeze_sha256"],
        "contract_sha256": official["contract_sha256"],
        "official_result_sha256": official_sha,
        "independent_rederivation_sha256": independent_sha,
        "independent_rederiver_contract":
            official["independent_rederivation"]["contract_id"],
        "luna_identity": official["luna_identity"],
        "claims": official["claims"],
    }
    if matrix:
        binding.update({
            "execution_mode": "production",
            "disposition": "INCOMPLETE_PENDING_OPUS",
            "luna_stage_accepted": True,
        })
    terminal = {
        "schema": "implementaudit-staged-campaign-terminal-v1",
        "campaign": official["campaign"], "stage": "LUNA",
        "stage_schema": binding["stage_schema"],
        "mission_count": binding["mission_count"],
        "binding_sha256": hashlib.sha256(
            surfaces_manifest_bytes(binding)).hexdigest(),
        "stage_snapshot_sha256": "3" * 64,
    }
    terminal_path = root / f"{prefix}-terminal.json"
    terminal_path.write_bytes(encoded(terminal))
    stage["evidence"] = {
        "official": _binding(root, f"{prefix}-official", official_path),
        "independent": _binding(
            root, f"{prefix}-independent", independent_path),
        "stage_terminal": _binding(
            root, f"{prefix}-terminal", terminal_path),
    }
    return stage


def surfaces_manifest_bytes(value):
    import campaign_lifecycle
    return campaign_lifecycle.canonical_json_bytes(value)


def _manifest(root, campaign, prefix):
    sources = []
    for index, role in enumerate(surfaces.required_roles(campaign)):
        path = root / f"{prefix}-{index:02d}.bin"
        path.write_bytes(f"{campaign}:{role}\n".encode())
        row = {"role": role, "path": path.name}
        if role in surfaces.GIT_IDENTITY_ROLES[campaign]:
            row.update({"git_commit": "a" * 40, "git_tree": "b" * 40})
        sources.append(row)
    return surfaces.build_manifest(campaign, sources, root=root)


def _gates(root):
    gates = []
    for name in integration.REQUIRED_GATES:
        path = root / f"{name}.log"
        path.write_bytes(f"{name}=PASS\n".encode())
        raw = path.read_bytes()
        gates.append({
            "name": name, "status": "PASS", "path": path.name,
            "byte_length": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        })
    return gates


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        b3_before = _manifest(root, surfaces.B3_CAMPAIGN, "b3")
        matrix_before = _manifest(root, surfaces.MATRIX_CAMPAIGN, "matrix")
        inputs = {
            "b3_stage": _bind_stage(
                root, _stage(surfaces.B3_CAMPAIGN), "b3-stage"),
            "matrix_stage": _bind_stage(
                root, _stage(surfaces.MATRIX_CAMPAIGN), "matrix-stage"),
            "gates": _gates(root),
            "before": {
                surfaces.B3_CAMPAIGN: b3_before,
                surfaces.MATRIX_CAMPAIGN: matrix_before,
            },
            "after": {
                surfaces.B3_CAMPAIGN: copy.deepcopy(b3_before),
                surfaces.MATRIX_CAMPAIGN: copy.deepcopy(matrix_before),
            },
        }
        output = root / "integration-certificate.json"
        certificate = integration.write_certificate(
            output, inputs, evidence_root=root)
        assert certificate["disposition"] == \
            "LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN"
        assert certificate["release_authorized"] is False
        assert certificate["tag_authorized"] is False
        assert certificate["publication_authorized"] is False
        expect_error("create-once", lambda:
                     integration.write_certificate(
                         output, inputs, evidence_root=root))

        cases = []
        swapped = copy.deepcopy(inputs)
        swapped["b3_stage"], swapped["matrix_stage"] = (
            swapped["matrix_stage"], swapped["b3_stage"])
        cases.append(("campaign", swapped))
        incomplete = copy.deepcopy(inputs)
        incomplete["b3_stage"]["independent"]["missions"].pop()
        incomplete["b3_stage"]["independent"]["mission_count"] = 5
        cases.append(("six", incomplete))
        fabricated = copy.deepcopy(inputs)
        fabricated["matrix_stage"]["independent"]["cells"][0]["index"] = 7
        cases.append(("order", fabricated))
        extra = copy.deepcopy(inputs)
        extra["b3_stage"]["independent"]["final_12_of_12"] = True
        cases.append(("fields", extra))
        nonproduction = copy.deepcopy(inputs)
        nonproduction["matrix_stage"]["independent"]["execution_mode"] = "test"
        cases.append(("production", nonproduction))
        substituted = copy.deepcopy(inputs)
        substituted["b3_stage"]["independent"]["missions"][0][
            "model_resolved"] = "terra"
        cases.append(("model", substituted))
        disagreement = copy.deepcopy(inputs)
        disagreement["matrix_stage"]["official"]["cells"][0][
            "overall_status"] = "FAIL"
        cases.append(("agreement", disagreement))
        gate_extra = copy.deepcopy(inputs)
        gate_extra["gates"].append(copy.deepcopy(gate_extra["gates"][0]))
        cases.append(("gate", gate_extra))
        drift = copy.deepcopy(inputs)
        drift["after"][surfaces.B3_CAMPAIGN]["entries"][0]["sha256"] = "0" * 64
        cases.append(("byte drift", drift))
        for index, (_fragment, changed) in enumerate(cases):
            expect_error(
                None, lambda c=changed, i=index:
                integration.write_certificate(
                    root / f"rejected-{i}.json", c, evidence_root=root))

        changed_gate = copy.deepcopy(inputs)
        (root / f"{integration.REQUIRED_GATES[0]}.log").write_bytes(
            b"changed\n")
        expect_error("evidence", lambda:
                     integration.write_certificate(
                         root / "changed-evidence.json", changed_gate,
                         evidence_root=root))

    print("PROVISIONAL-INTEGRATION-PASS")


if __name__ == "__main__":
    main()
