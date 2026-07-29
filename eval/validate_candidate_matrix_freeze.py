#!/usr/bin/env python3
"""Validate the separate frozen Luna candidate-matrix packet."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import subprocess
import sys

import candidate_matrix_contract as contract


FIXTURE_ORDER = contract.FIXTURE_ORDER
ACCEPTANCE_RULE = (
    "all fourteen canonical Luna candidate fixture cells terminal and PASS; "
    "independent rederivation agrees; zero INVALID, ERROR, or substitution; "
    "successful Luna stage is INCOMPLETE_PENDING_OPUS with "
    "luna_stage_accepted true and accepted false"
)
INVALID_ERROR_RULE = (
    "FAIL, INVALID, unexplained ERROR, substitution, disagreement, and "
    "custody or identity failure halt the Luna stage"
)
STOP_CONDITIONS = [
    "authentication or quota failure", "model substitution",
    "identity or custody mismatch", "any FAIL, INVALID, or unexplained ERROR",
    "official and independent disagreement", "frozen input drift",
]
FORBIDDEN_IMPORTS = {
    "candidate_matrix_campaign", "campaign_lifecycle", "b3v4_campaign",
    "b3v4_rederive", "b3v4_contract", "hosts", "runner", "adapters",
    "lib.scoring", "eval.lib.scoring",
}
EXPECTED_MUST_NOT_IMPORT = [
    "eval.candidate_matrix_campaign", "eval.hosts", "eval.runner",
    "eval.lib.scoring", "eval.adapters", "eval.campaign_lifecycle",
    "eval.b3v4_campaign", "eval.b3v4_rederive", "eval.b3v4_contract",
]


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _tree_manifest(path):
    path = pathlib.Path(path)
    rows = []
    for child in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
        if child.is_symlink():
            raise ValueError("fixture tree link alias forbidden")
        relative = child.relative_to(path).as_posix()
        if child.is_dir():
            rows.append({"path": relative, "kind": "directory"})
        elif child.is_file():
            rows.append({
                "path": relative, "kind": "file",
                "byte_length": child.stat().st_size,
                "sha256": _sha256(child),
            })
        else:
            raise ValueError("fixture tree special entry forbidden")
    return hashlib.sha256(contract.canonical_json_bytes({
        "schema": "implementaudit-candidate-matrix-fixture-tree-v1",
        "entries": rows,
    })).hexdigest()


def _git(repo_root, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True, text=True, timeout=60)
    if proc.returncode:
        raise ValueError("repository Git identity unavailable")
    return proc.stdout.strip()


def _imports(path):
    source = contract.read_custodied_bytes(
        path, "independent rederiver", root=path.parent)
    tree = ast.parse(source, filename=str(path))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def validate_structure(packet):
    contract.validate_freeze_envelope(packet)
    if not contract.exact_json_equal(packet["attempt_policy"], {
            "silent_retry": "FORBIDDEN", "preserve_every_attempt": True,
            "maximum_attempts": 14}):
        raise ValueError("attempt policy must preserve exactly fourteen cells")
    if not contract.exact_json_equal(packet["evidence_profiles"], {
            "formal_host_read": "implementaudit-host-read-profile-v2",
            "raw_stdout": "required", "native_session": "required",
            "pre_spawn": "required", "post_cell_manifest": "required"}):
        raise ValueError("evidence profile drift")
    if not contract.exact_json_equal(packet["result_composition"], {
            "product_property_states": ["PASS", "FAIL", "INCOMPLETE"],
            "host_states": ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
            "overall_states": ["PASS", "FAIL", "INVALID", "ERROR"],
            "luna_stage_dispositions": ["INCOMPLETE_PENDING_OPUS"]}):
        raise ValueError("result composition drift")
    if packet["acceptance_rule"] != ACCEPTANCE_RULE:
        raise ValueError("acceptance rule drift")
    if packet["invalid_error_rule"] != INVALID_ERROR_RULE:
        raise ValueError("invalid/error rule drift")
    if not contract.exact_json_equal(
            packet["stop_conditions"], STOP_CONDITIONS):
        raise ValueError("stop conditions drift")
    rederiver = packet["independent_rederiver"]
    if not contract.exact_json_equal(
            rederiver["must_not_import"], EXPECTED_MUST_NOT_IMPORT):
        raise ValueError("independent rederiver import boundary drift")
    if [row["fixture"] for row in packet["cells"]] != list(FIXTURE_ORDER):
        raise ValueError("canonical fourteen-cell order drift")
    return packet


def validate_live(packet, repo_root):
    validate_structure(packet)
    repo_root = pathlib.Path(repo_root).resolve(strict=True)
    if _git(repo_root, "rev-parse", "HEAD") != packet["foundation"]["commit"]:
        raise ValueError("foundation commit drift")
    if _git(repo_root, "rev-parse", "HEAD^{tree}") != \
            packet["foundation"]["tree"]:
        raise ValueError("foundation tree drift")
    if contract.contract_sha256() != packet["artifact_contract"]["sha256"]:
        raise ValueError("artifact contract drift")
    for fixture in packet["fixtures"]:
        path = contract.resolve_contained(repo_root, fixture["path"])
        if _sha256(path) != fixture["sha256"]:
            raise ValueError(f"fixture {fixture['id']} byte drift")
        if _tree_manifest(path.parent) != fixture["complete_manifest_sha256"]:
            raise ValueError(f"fixture {fixture['id']} tree drift")
    for name, identity in packet["artifacts"].items():
        path = contract.resolve_contained(repo_root, identity["path"])
        if _sha256(path) != identity["sha256"]:
            raise ValueError(f"artifact {name} byte drift")
    rederiver = packet["independent_rederiver"]["implementation_identity"]
    rederiver_path = contract.resolve_contained(repo_root, rederiver["path"])
    if _sha256(rederiver_path) != rederiver["sha256"]:
        raise ValueError("independent rederiver byte drift")
    forbidden = _imports(rederiver_path) & FORBIDDEN_IMPORTS
    if forbidden:
        raise ValueError(
            "independent rederiver forbidden import: " +
            ", ".join(sorted(forbidden)))
    return packet


def _read_packet(path):
    path = pathlib.Path(path).absolute()
    return contract.decode_json_bytes(
        contract.read_custodied_bytes(
            path, "candidate matrix freeze packet", root=path.parent),
        "candidate matrix freeze packet", require_object=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    parser.add_argument("--repo-root")
    args = parser.parse_args(argv)
    try:
        packet = _read_packet(args.packet)
        if args.repo_root:
            validate_live(packet, args.repo_root)
        else:
            validate_structure(packet)
    except (OSError, TypeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "PASS", "campaign": packet["campaign"],
        "cell_count": len(packet["cells"]),
        "disposition": "FROZEN_BEFORE_FIRST_CELL",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
