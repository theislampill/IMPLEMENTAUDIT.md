#!/usr/bin/env python3
"""Mutation matrix for the closed B3-v4 artifact-envelope contract."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile

from test_b3v4_freeze import valid_packet


HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_MODULE = HERE / "b3v4_contract.py"
DECLARATION = HERE / "b3v4_contract.json"


def load_contract():
    spec = importlib.util.spec_from_file_location("b3v4contract", CONTRACT_MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rejected(fragment, fn):
    try:
        fn()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"mutation unexpectedly accepted; wanted {fragment!r}")


def must_reject(fn):
    try:
        fn()
    except (OSError, TypeError, ValueError):
        return
    raise AssertionError("mutation unexpectedly accepted")


def lifecycle_rows(packet):
    mission = packet["missions"][0]
    digest = "a" * 64
    rows = {
        "campaign_manifest": {
            "schema": "implementaudit-b3v4-luna-campaign-custody-v2",
            "campaign": "b3v4-sol-luna-r2", "freeze_sha256": digest,
            "contract_sha256": digest, "created_at": "2030-01-01T00:00:00Z",
            "execution_stage": "LUNA",
        },
        "attempt_status": {
            "schema": "implementaudit-b3v4-luna-attempt-status-v2",
            "campaign": "b3v4-sol-luna-r2", "freeze_sha256": digest,
            "contract_sha256": digest, "mission": mission,
            "state": "PREPARED_BEFORE_HOST_SPAWN", "execution_mode": "test",
            "created_at": "2030-01-01T00:00:00Z",
            "host_attestation_binding": {
                "path": "host-attestation.json",
                "sha256": packet["configurations"]["L"][
                    "host_attestation"]["sha256"],
                "config": "L", "host": "WSL Ubuntu Codex CLI",
                "model_resolved_required": "gpt-5.6-luna",
            },
        },
        "attempt_terminal": {
            "schema": "implementaudit-b3v4-luna-attempt-terminal-v3",
            "campaign": "b3v4-sol-luna-r2", "mission_index": 0,
            "execution_mode": "test", "overall_status": "ERROR",
            "resolved_model": None, "host_run_root": None,
            "official_overall_status": None,
            "official_verdict_sha256": None,
            "stop_reason": "mission-execution-exception",
            "error_type": "RuntimeError", "completed_at": "2030-01-01T00:00:01Z",
            "completed_attempt_seal": None,
        },
    }
    rows["official_luna_result"] = {
        "schema": "implementaudit-b3v4-luna-result-v2",
        "campaign": "b3v4-sol-luna-r2", "freeze_sha256": digest,
        "contract_sha256": digest,
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "accepted": False,
        "mission_count": 6,
        "missions": [{
            "index": mission["index"], "config": mission["config"],
            "arm": mission["arm"], "rep": mission["rep"],
            "product_status": "PASS", "host_status": "PASS",
            "overall_status": "PASS",
            "properties": {
                "required": {"state": "PASS", "pass": True}},
            "reason": None,
            "bundle_manifest_sha256": digest,
            "raw_stdout_sha256": digest,
            "native_session_sha256": digest,
            "official_overall_status": "PASS",
            "independent_overall_status": "PASS",
            "model_resolved": "gpt-5.6-luna",
            "official_verdict_sha256": digest,
        } for mission in packet["missions"]],
        "luna_identity": {
            "config": "L", "host": "WSL Ubuntu Codex CLI",
            "model_resolved_required": "gpt-5.6-luna",
            "host_attestation_id": "b3v4-L-host",
            "host_attestation_sha256": digest,
        },
        "independent_rederivation": {
            "path": "b3v4-luna-independent-rederivation.json",
            "sha256": digest,
            "schema": "implementaudit-b3v4-luna-independent-rederivation-v2",
            "contract_id": "implementaudit-b3v4-luna-independent-rederiver-v2",
            "implementation_sha256": digest,
        },
        "claims": {
            "final_12_of_12": False,
            "cross_model_qualified": False,
            "release_authorized": False,
            "tag_authorized": False,
            "publication_authorized": False,
        },
    }
    return rows


def main():
    contract = load_contract()
    assert contract.lifecycle.__name__ == "campaign_lifecycle"
    assert (contract.canonical_json_bytes({"b": 2, "a": 1}) ==
            contract.lifecycle.canonical_json_bytes({"a": 1, "b": 2}))
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    official = load("b3v4freeze_matrix", HERE / "validate_b3v4_freeze.py")
    independent = load("b3v4rederive_matrix", HERE / "b3v4_rederive.py")
    declaration_bytes = DECLARATION.read_bytes()
    declaration = contract.decode_json_bytes(
        declaration_bytes, "B3-v4 artifact contract", require_object=True)
    contract.validate_declaration(declaration)
    assert contract.contract_sha256() == hashlib.sha256(declaration_bytes).hexdigest()
    assert set(declaration["artifacts"]) == {
        "campaign_freeze", "owner_approval", "host_attestation",
        "campaign_manifest", "attempt_status", "official_verdict",
        "attempt_terminal", "host_terminal", "bundle_manifest", "fixture",
        "events", "repo_before", "repo_after", "artifact_manifest",
        "host_read_manifest", "host_read_profile", "host_read_preimages",
        "host_read_fixture", "host_read_replay_spec", "host_read_pre_spawn",
        "run_intent", "process_started", "host_stdout", "host_session",
        "host_tool_trace", "host_read_matrix", "host_read_post_probe",
        "host_read_terminal", "host_checks", "host_check_inputs",
        "official_luna_result", "luna_stage_terminal",
        "independent_rederivation",
    }
    declaration_mutations = []
    changed = copy.deepcopy(declaration)
    changed["execution"]["mutable_summary"] = "PASS"
    declaration_mutations.append(changed)
    changed = copy.deepcopy(declaration)
    changed["artifacts"]["campaign_manifest"]["producer"] = "mutable-summary"
    declaration_mutations.append(changed)
    changed = copy.deepcopy(declaration)
    changed["artifacts"]["fabricated_summary"] = copy.deepcopy(
        changed["artifacts"]["campaign_manifest"])
    declaration_mutations.append(changed)
    changed = copy.deepcopy(declaration)
    changed["lifecycle_schemas"]["campaign_manifest"].append(
        "mutable_summary")
    declaration_mutations.append(changed)
    changed = copy.deepcopy(declaration)
    changed["lifecycle_schemas"]["fabricated_summary"] = ["status"]
    declaration_mutations.append(changed)
    for mutation in declaration_mutations:
        must_reject(lambda value=mutation: contract.validate_declaration(value))
    for alias in (0, 0.0, -0.0, True):
        changed = copy.deepcopy(declaration)
        changed["execution"]["final_acceptance"] = alias
        must_reject(
            lambda changed=changed: contract.validate_declaration(changed))

    packet = valid_packet()
    packet["artifact_contract"] = {
        "schema": "implementaudit-b3v4-luna-artifact-contract-v2",
        "path": "eval/b3v4_contract.json",
        "sha256": contract.contract_sha256(),
    }
    contract.validate_freeze_envelope(packet)
    for alias in (6.0, True):
        changed = copy.deepcopy(packet)
        changed["luna_stage"]["mission_count"] = alias
        must_reject(
            lambda changed=changed: contract.validate_freeze_envelope(changed))
    rows = lifecycle_rows(packet)
    contract.validate_artifact(
        "official_luna_result", rows["official_luna_result"])
    official_mutations = []
    changed = copy.deepcopy(rows["official_luna_result"])
    changed["missions"] = [{} for _ in range(6)]
    official_mutations.append(changed)
    for path, value in (
            (("missions", 0, "index"), False),
            (("missions", 0, "index"), 0.0),
            (("missions", 0, "index"), -0.0),
            (("missions", 0, "rep"), True),
            (("missions", 0, "rep"), 1.0),
            (("luna_identity",), {}),
            (("independent_rederivation",), {}),
            (("claims", "release_authorized"), True),
            (("claims", "release_authorized"), 0),
            (("claims", "release_authorized"), 0.0),
            (("claims", "release_authorized"), -0.0)):
        changed = copy.deepcopy(rows["official_luna_result"])
        owner = changed
        for part in path[:-1]:
            owner = owner[part]
        owner[path[-1]] = value
        official_mutations.append(changed)
    changed = copy.deepcopy(rows["official_luna_result"])
    changed["missions"][0]["mutable_summary"] = "PASS"
    official_mutations.append(changed)
    changed = copy.deepcopy(rows["official_luna_result"])
    del changed["missions"][0]["official_verdict_sha256"]
    official_mutations.append(changed)
    changed = copy.deepcopy(rows["official_luna_result"])
    changed["campaign"] = "different-nonempty-campaign"
    official_mutations.append(changed)
    changed = copy.deepcopy(rows["official_luna_result"])
    changed["independent_rederivation"]["contract_id"] = \
        "different-nonempty-contract"
    official_mutations.append(changed)
    for mutation in official_mutations:
        must_reject(lambda mutation=mutation:
                    contract.validate_artifact("official_luna_result", mutation))

    # Every qualification-bearing object is closed.  Exercise both directions
    # at every nested boundary so a local subset check cannot reopen the packet.
    nested_objects = [
        ("artifact_contract",), ("foundation",), ("fixture",),
        ("artifacts",), ("artifacts", "scorer"),
        ("candidate",), ("control",), ("configurations",),
        ("configurations", "L"),
        ("configurations", "L", "executable"),
        ("configurations", "L", "host_attestation"),
        ("authorization",), ("missions", 0), ("luna_stage",),
        ("evidence_profiles",),
        ("result_composition",), ("attempt_policy",),
        ("independent_rederiver",),
        ("independent_rederiver", "implementation_identity"),
    ]

    def owner_at(value, path):
        for key in path:
            value = value[key]
        return value

    for object_path in nested_objects:
        extra_nested = copy.deepcopy(packet)
        owner_at(extra_nested, object_path)["unknown_qualification_field"] = "PASS"
        missing_nested = copy.deepcopy(packet)
        nested_owner = owner_at(missing_nested, object_path)
        nested_owner.pop(next(iter(nested_owner)))
        for mutation in (extra_nested, missing_nested):
            must_reject(lambda value=mutation:
                        contract.validate_freeze_envelope(value))
            must_reject(lambda value=mutation:
                        official.validate_structure(value))
            must_reject(lambda value=mutation:
                        independent._validate_freeze_contract(value))

    freeze_mutations = []
    missing = copy.deepcopy(packet); missing.pop("seed")
    freeze_mutations.append(("key set", missing))
    extra = copy.deepcopy(packet); extra["unknown"] = True
    freeze_mutations.append(("key set", extra))
    bool_seed = copy.deepcopy(packet); bool_seed["seed"] = True
    freeze_mutations.append(("seed", bool_seed))
    float_rep = copy.deepcopy(packet); float_rep["missions"][0]["rep"] = 1.0
    freeze_mutations.append(("rep", float_rep))
    tree_commit = copy.deepcopy(packet); tree_commit["foundation"]["commit"] = {"tree": "b" * 40}
    freeze_mutations.append(("commit", tree_commit))
    approval_type = copy.deepcopy(packet); approval_type["authorization"]["acknowledgement_path"] = 7
    freeze_mutations.append(("acknowledgement_path", approval_type))
    wrong_fixture = copy.deepcopy(packet); wrong_fixture["fixture"]["id"] = "B3-v2"
    freeze_mutations.append(("fixture", wrong_fixture))
    wrong_host = copy.deepcopy(packet); wrong_host["configurations"]["L"]["host"] = "other"
    freeze_mutations.append(("host", wrong_host))
    unknown_enum = copy.deepcopy(packet); unknown_enum["authorization"]["metered_api_spend"] = "maybe"
    freeze_mutations.append(("metered", unknown_enum))
    escaping_artifact = copy.deepcopy(packet); escaping_artifact["artifacts"]["runner"]["path"] = "../runner.py"
    freeze_mutations.append(("path", escaping_artifact))
    bad_contract = copy.deepcopy(packet); bad_contract["artifact_contract"]["sha256"] = "0" * 64
    freeze_mutations.append(("contract", bad_contract))
    for fragment, mutation in freeze_mutations:
        rejected(fragment, lambda value=mutation: contract.validate_freeze_envelope(value))
        must_reject(lambda value=mutation: official.validate_structure(value))
        must_reject(lambda value=mutation: independent._validate_freeze_contract(value))

    duplicate = b'{"schema":"x","schema":"x"}'
    rejected("duplicate", lambda: contract.decode_json_bytes(duplicate, "row"))
    for raw in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
        rejected("non-finite", lambda value=raw: contract.decode_json_bytes(value, "row"))
        must_reject(lambda value=raw: independent._decode_json(
            value, "row", "row malformed"))
    rejected("utf-8", lambda: contract.decode_json_bytes(b"\xff", "row"))

    rows = lifecycle_rows(packet)
    for schema_name, row in rows.items():
        contract.validate_artifact(schema_name, row)
        missing = copy.deepcopy(row); missing.pop(next(iter(missing)))
        rejected("key set", lambda name=schema_name, value=missing:
                 contract.validate_artifact(name, value))
        extra = copy.deepcopy(row); extra["extra"] = None
        rejected("key set", lambda name=schema_name, value=extra:
                 contract.validate_artifact(name, value))

    attestation = {"id": "frozen-host", "shell_dialect": "posix",
                   "executables": {"python": "/usr/bin/python3"}}
    contract.validate_host_attestation(attestation)
    weak_attestation = copy.deepcopy(attestation); weak_attestation["model"] = "other"
    rejected("key set", lambda: contract.validate_host_attestation(weak_attestation))

    with tempfile.TemporaryDirectory(prefix="b3v4-contract-") as tmp:
        root = pathlib.Path(tmp).resolve()
        (root / "safe").mkdir()
        target = root / "safe" / "artifact.json"
        contract.write_new_json(target, rows["campaign_manifest"])
        rejected("exists", lambda: contract.write_new_json(
            target, rows["campaign_manifest"]))
        assert contract.resolve_contained(root, "safe/artifact.json") == target
        for bad in ("../escape", "/rooted", "C:/drive", "a\\b", "a/./b"):
            rejected("path", lambda value=bad: contract.resolve_contained(root, value))
        if hasattr(target, "hardlink_to"):
            alias = root / "safe" / "alias.json"
            alias.hardlink_to(target)
            rejected("link", lambda: contract.resolve_contained(root, "safe/alias.json"))
            alias.unlink()

        file_link = root / "safe" / "artifact-link.json"
        try:
            os.symlink(target, file_link)
        except (NotImplementedError, OSError) as exc:
            print("CUSTODY_FILE_SYMLINK=SKIP:" + type(exc).__name__)
        else:
            rejected("alias", lambda: contract.read_custodied_bytes(
                file_link, "file symlink", root=root))
            must_reject(lambda: independent._read_bytes(file_link))
            file_link.unlink()
            print("CUSTODY_FILE_SYMLINK=PASS")

        directory_link = root / "safe-link"
        try:
            os.symlink(root / "safe", directory_link, target_is_directory=True)
        except (NotImplementedError, OSError) as exc:
            print("CUSTODY_DIRECTORY_SYMLINK=SKIP:" + type(exc).__name__)
        else:
            rejected("alias", lambda: contract.read_custodied_bytes(
                directory_link / "artifact.json", "directory symlink", root=root))
            must_reject(lambda: independent._read_bytes(
                directory_link / "artifact.json"))
            directory_link.unlink()
            print("CUSTODY_DIRECTORY_SYMLINK=PASS")

        if os.name == "nt":
            junction = root / "safe-junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction),
                 str(root / "safe")], capture_output=True, text=True)
            if made.returncode:
                print("CUSTODY_DIRECTORY_JUNCTION=SKIP:mklink")
            else:
                rejected("alias", lambda: contract.read_custodied_bytes(
                    junction / "artifact.json", "directory junction", root=root))
                must_reject(lambda: independent._read_bytes(
                    junction / "artifact.json"))
                rejected("alias", lambda: contract.resolve_external_file(
                    str(junction / "artifact.json"),
                    "external directory junction"))
                os.rmdir(junction)
                print("CUSTODY_DIRECTORY_JUNCTION=PASS")

    completed = [copy.deepcopy(packet["missions"][i]) for i in range(2)]
    assert contract.next_mission(packet["missions"], completed) == packet["missions"][2]
    rejected("order", lambda: contract.next_mission(
        packet["missions"], [packet["missions"][1]]))
    luna_prefix = [m for m in packet["missions"] if m["config"] == "L"]
    assert luna_prefix == packet["missions"]
    assert contract.campaign_complete(packet["missions"], luna_prefix)
    assert contract.campaign_complete(packet["missions"], packet["missions"])

    tree = ast.parse((HERE / "b3v4_rederive.py").read_text(encoding="utf-8"))
    imported = {node.module for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module}
    imported |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                 for alias in node.names}
    assert not ({"b3v4_contract", "validate_b3v4_freeze", "b3v4_campaign",
                 "hosts", "runner", "lib.scoring", "eval.lib.scoring"} & imported)

    print("test_b3v4_contract_matrix: ok")


if __name__ == "__main__":
    main()
