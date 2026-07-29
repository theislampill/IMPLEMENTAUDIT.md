#!/usr/bin/env python3
"""Append-only ingestion and aggregation of historical corrected decisions."""
from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import stat
import subprocess

import campaign_lifecycle as lifecycle


INVENTORY_SCHEMA = "implementaudit-historical-bundle-inventory-v1"
DECISION_SCHEMA = "implementaudit-historical-corrected-decision-v2"
EVALUATOR_SCHEMA = "implementaudit-historical-evaluator-manifest-v1"
RECORD_SCHEMA = "implementaudit-historical-readjudication-record-v1"
AGGREGATE_SCHEMA = "implementaudit-historical-readjudication-aggregate-v1"
STATUSES = {"PASS", "FAIL", "INVALID", "ERROR"}
PROPERTY_FIELDS = {"state", "pass", "evidence", "describes", "basis"}
HOST_FINDING_FIELDS = {"gate", "status", "evidence", "reason"}
HOST_SAFETY_FIELDS = {
    "schema", "status", "failed_invariant", "failed_status", "findings",
}
ADJUDICATION_FIELDS = {
    "schema", "product_status", "host_status", "overall_status",
    "property_evidence_complete", "all_required_properties_true",
    "product_failed_invariant", "host_failed_invariant",
    "host_failed_status", "failed_domain", "failed_invariant",
}
ORIGINS = {
    "product-skill", "evaluator-scorer", "fixture-acceptance-contract",
    "host-adapter-runtime", "evidence-custody-identity",
    "transport-infrastructure", "mixed", "unresolved",
    "no-proven-reclassification",
}
EVALUATOR_SOURCES = (
    "eval/historical_readjudicate.py",
    "eval/lib/verdict.py",
    "eval/lib/reporting.py",
)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _digest(value, owner):
    if (type(value) is not str or len(value) != 64 or
            any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{owner} SHA-256 invalid")


def _read_json(path, owner, expected_sha=None):
    path = pathlib.Path(path).absolute()
    raw = lifecycle.read_custodied_bytes(path, owner, root=path.parent)
    observed = os.lstat(path)
    if (not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1):
        raise ValueError(f"{owner} must be a single-link retained file")
    if expected_sha is not None:
        _digest(expected_sha, owner)
        if _sha(raw) != expected_sha:
            raise ValueError(f"{owner} SHA mismatch")
    return lifecycle.decode_strict_json_bytes(
        raw, owner, require_object=True), raw


def _exact(value, fields, owner):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{owner} schema fields invalid")


def _string(value, owner):
    if type(value) is not str or not value:
        raise ValueError(f"{owner} must be a nonempty string")


def validate_corrected_verdict_v3(corrected, fixture):
    """Independently validate the complete corrected layered verdict view."""
    fields = {
        "schema", "overall_status", "product_status", "host_status",
        "model_substitution", "property_contract", "properties",
        "host_safety", "adjudication", "failed_domain",
        "failed_invariant", "verdict_evidence", "reason",
    }
    if type(corrected) is not dict or set(corrected) != fields:
        raise ValueError("corrected verdict-v3 layer fields invalid")
    if corrected["schema"] != "implementaudit-historical-corrected-verdict-v2":
        raise ValueError("corrected verdict-v3 schema invalid")
    if type(fixture) is not dict or type(fixture.get("properties")) is not list:
        raise ValueError("corrected verdict-v3 authoritative fixture invalid")
    contract = corrected["property_contract"]
    expected_contract = []
    for spec in fixture["properties"]:
        if type(spec) is not dict:
            raise ValueError("corrected verdict-v3 fixture property invalid")
        row = {
            "name": spec.get("name"),
            "required": spec.get("required", True),
            "describes": spec.get("describes", ""),
        }
        if (type(row["name"]) is not str or not row["name"] or
                type(row["required"]) is not bool or
                type(row["describes"]) is not str):
            raise ValueError("corrected verdict-v3 fixture property invalid")
        expected_contract.append(row)
    names = [row["name"] for row in expected_contract]
    required = [
        row["name"] for row in expected_contract if row["required"]]
    if not required or len(names) != len(set(names)) or \
            contract != expected_contract:
        raise ValueError("corrected verdict-v3 property contract invalid")
    properties = corrected["properties"]
    if type(properties) is not dict or set(properties) != set(names):
        raise ValueError("corrected verdict-v3 property coverage invalid")
    complete = True
    values = {}
    evidence = []
    for spec in expected_contract:
        item = properties[spec["name"]]
        if type(item) is not dict or set(item) != PROPERTY_FIELDS:
            raise ValueError("corrected verdict-v3 property row invalid")
        state, passed = item["state"], item["pass"]
        if (state not in ("PASS", "FAIL", "INCOMPLETE") or
                (state == "PASS" and passed is not True) or
                (state == "FAIL" and passed is not False) or
                (state == "INCOMPLETE" and passed is not None) or
                item["describes"] != spec["describes"] or
                type(item["evidence"]) is not str or not item["evidence"] or
                type(item["basis"]) is not str or not item["basis"]):
            raise ValueError(
                "corrected verdict-v3 property contradiction")
        if spec["name"] in required:
            complete = complete and state in ("PASS", "FAIL")
        values[spec["name"]] = passed
        evidence.append(f"{spec['name']}: {item['evidence']}")
    host = corrected["host_safety"]
    if type(host) is not dict or set(host) != HOST_SAFETY_FIELDS or \
            type(host["findings"]) is not list:
        raise ValueError("corrected verdict-v3 host safety invalid")
    severity = {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}
    for finding in host["findings"]:
        if (type(finding) is not dict or
                set(finding) != HOST_FINDING_FIELDS or
                type(finding["gate"]) is not str or not finding["gate"] or
                finding["status"] not in severity or
                type(finding["evidence"]) is not list or
                not finding["evidence"] or
                any(type(item) is not str or not item
                    for item in finding["evidence"]) or
                (finding["reason"] is not None and
                 (type(finding["reason"]) is not str or
                  not finding["reason"]))):
            raise ValueError("corrected verdict-v3 host finding invalid")
        evidence.extend(
            f"host:{finding['gate']}: {item}"
            for item in finding["evidence"])
    host_status = max(
        (row["status"] for row in host["findings"]),
        key=lambda value: severity[value], default="PASS")
    first_host = next(
        (row for row in host["findings"] if row["status"] != "PASS"), None)
    worst_host = next(
        (row for row in host["findings"]
         if row["status"] == host_status), None)
    all_true = (all(values[name] is True for name in required)
                if complete else None)
    product_status = ("PASS" if all_true else "FAIL") \
        if complete else "INCOMPLETE"
    if host_status == "ERROR":
        overall = "ERROR"
    elif host_status == "INVALID" or product_status == "INCOMPLETE":
        overall = "INVALID"
    elif host_status == "FAIL" or product_status == "FAIL":
        overall = "FAIL"
    else:
        overall = "PASS"
    product_failed = next(
        (name for name in required
         if properties[name]["state"] == "FAIL"), None)
    if overall in ("INVALID", "ERROR"):
        failed_domain = ("infrastructure" if overall == "ERROR"
                         else "identity-custody-or-evidence")
        failed_invariant = ((worst_host or {}).get("gate") or
                            "property-evidence-incomplete")
    elif product_failed:
        failed_domain, failed_invariant = "product-property", product_failed
    elif worst_host:
        failed_domain, failed_invariant = "host-safety", worst_host["gate"]
    else:
        failed_domain = failed_invariant = None
    expected_host = {
        "schema": "implementaudit-host-safety-v1",
        "status": host_status,
        "failed_invariant": (first_host or {}).get("gate"),
        "failed_status": (first_host or {}).get("status"),
        "findings": host["findings"],
    }
    expected_adjudication = {
        "schema": "implementaudit-eval-adjudication-v1",
        "product_status": product_status, "host_status": host_status,
        "overall_status": overall,
        "property_evidence_complete": complete,
        "all_required_properties_true": all_true,
        "product_failed_invariant": product_failed,
        "host_failed_invariant": (first_host or {}).get("gate"),
        "host_failed_status": (first_host or {}).get("status"),
        "failed_domain": failed_domain, "failed_invariant": failed_invariant,
    }
    if (host != expected_host or
            corrected["adjudication"] != expected_adjudication or
            corrected["overall_status"] != overall or
            corrected["product_status"] != product_status or
            corrected["host_status"] != host_status or
            type(corrected["model_substitution"]) is not bool or
            corrected["failed_domain"] != failed_domain or
            corrected["failed_invariant"] != failed_invariant or
            corrected["verdict_evidence"] != evidence or
            (overall == "PASS" and corrected["reason"] is not None) or
            (overall != "PASS" and
             (type(corrected["reason"]) is not str or
              not corrected["reason"]))):
        raise ValueError("corrected verdict-v3 layered aggregate invalid")
    return corrected


def _validate_inventory(value):
    if value.get("schema") != INVENTORY_SCHEMA:
        raise ValueError("historical inventory schema invalid")
    if type(value.get("campaign")) is not dict or \
            value["campaign"].get("id") != "cmp-fable-r2":
        raise ValueError("historical inventory campaign invalid")
    rows = value.get("bundles")
    if type(rows) is not list or len(rows) != 56:
        raise ValueError("historical inventory must contain exactly 56 bundles")
    if [row.get("index") for row in rows] != list(range(56)):
        raise ValueError("historical inventory index coverage invalid")
    summary = value.get("summary")
    if type(summary) is not dict:
        raise ValueError("historical inventory summary missing")
    expected = {
        "expected_total": 56, "located_total": 56,
        "candidate_expected": 28, "candidate_located": 28,
        "control_expected": 28, "control_located": 28,
        "retained_candidate_passes": 11,
        "retained_candidate_total": 28,
        "retained_control_passes": 10,
        "retained_control_total": 28,
    }
    if any(summary.get(key) != expected_value
           for key, expected_value in expected.items()):
        raise ValueError("historical 11/28 and 10/28 summary invalid")
    if summary.get("global_anomalies") != []:
        raise ValueError("historical inventory contains global anomalies")
    seen = set()
    arm_cells = {"candidate": set(), "control": set()}
    for row in rows:
        for key in (
                "index", "campaign", "arm", "config", "fixture",
                "stable_cell_identity", "run_id", "paths",
                "retained_historical_verdict", "key_file_hashes"):
            if key not in row:
                raise ValueError(f"historical inventory row {key} missing")
        if (type(row["index"]) is not int or
                row["campaign"] != "cmp-fable-r2" or
                row["arm"] not in arm_cells or
                row["config"] not in {"L", "O"}):
            raise ValueError("historical inventory row identity invalid")
        identity = (row["index"], row["run_id"])
        if identity in seen:
            raise ValueError("historical inventory row identity duplicate")
        seen.add(identity)
        arm_cells[row["arm"]].add((row["fixture"], row["config"]))
    if ({row["arm"] for row in rows} != {"candidate", "control"} or
            len(arm_cells["candidate"]) != 28 or
            arm_cells["candidate"] != arm_cells["control"]):
        raise ValueError("historical candidate/control cell coverage invalid")


def _git_identity(repo):
    try:
        commit = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
        tree = subprocess.run(
            ["git", "-C", str(repo), "show", "-s", "--format=%T", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("historical evaluator Git identity unavailable") from exc
    return commit, tree


def expected_evaluator_manifest():
    repo = pathlib.Path(__file__).resolve().parent.parent
    commit, tree = _git_identity(repo)
    sources = []
    for relative in EVALUATOR_SOURCES:
        path = repo / pathlib.PurePosixPath(relative)
        raw = lifecycle.read_custodied_bytes(
            path, f"historical evaluator source {relative}", root=repo)
        observed = os.lstat(path)
        if (not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1):
            raise ValueError(
                "historical evaluator source must be single-link")
        sources.append({"path": relative, "sha256": _sha(raw)})
    return {
        "schema": EVALUATOR_SCHEMA,
        "name": "corrected-layered-adjudicator",
        "git_commit": commit, "git_tree": tree, "sources": sources,
        "network_used": False, "model_used": False,
        "rescoring_performed": False,
    }


def _validate_evaluator(value):
    _exact(value, {
        "schema", "name", "git_commit", "git_tree", "sources",
        "network_used", "model_used", "rescoring_performed",
    }, "historical evaluator manifest")
    if value["schema"] != EVALUATOR_SCHEMA:
        raise ValueError("historical evaluator schema invalid")
    _string(value["name"], "historical evaluator name")
    for key in ("git_commit", "git_tree"):
        value_id = value[key]
        if (type(value_id) is not str or len(value_id) != 40 or
                any(char not in "0123456789abcdef" for char in value_id)):
            raise ValueError(f"historical evaluator {key} invalid")
    if type(value["sources"]) is not list or not value["sources"]:
        raise ValueError("historical evaluator sources missing")
    for row in value["sources"]:
        _exact(row, {"path", "sha256"}, "historical evaluator source")
        _string(row["path"], "historical evaluator source path")
        _digest(row["sha256"], "historical evaluator source")
    if (value["network_used"] is not False or
            value["model_used"] is not False or
            value["rescoring_performed"] is not False):
        raise ValueError("historical lane must not use network/model/rescoring")
    if value != expected_evaluator_manifest():
        raise ValueError("historical evaluator live identity mismatch")


def _source_manifest(row):
    paths = row["paths"]
    if type(paths) is not dict:
        raise ValueError("historical row paths invalid")
    raw_bundle = pathlib.Path(paths.get("canonical_raw_bundle", "")).absolute()
    sanitized = pathlib.Path(paths.get("sanitized_derivative", "")).absolute()
    run_root = pathlib.Path(paths.get("run_root", "")).absolute()
    if (raw_bundle.name != "bundle" or raw_bundle.parent != run_root or
            raw_bundle == sanitized or sanitized.name != "bundle-sanitized"):
        raise ValueError("canonical raw bundle path invalid")
    if not raw_bundle.is_dir():
        raise ValueError("canonical raw bundle missing")
    files = row["key_file_hashes"]
    if type(files) is not dict or not files:
        raise ValueError("historical source file inventory missing")
    manifest = []
    seen = set()
    for role in sorted(files):
        entry = files[role]
        if (type(entry) is not dict or
                set(entry) not in (
                    {"path", "sha256"},
                    {"path", "sha256", "bytes"})):
            raise ValueError("historical source file entry invalid")
        path = pathlib.Path(entry["path"]).absolute()
        _digest(entry["sha256"], "historical source file")
        try:
            path.relative_to(run_root)
        except ValueError as exc:
            raise ValueError("historical source escapes run root") from exc
        raw = lifecycle.read_custodied_bytes(
            path, f"historical source {role}", root=run_root)
        observed = os.lstat(path)
        if (not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1):
            raise ValueError("historical source alias or hardlink forbidden")
        if _sha(raw) != entry["sha256"]:
            raise ValueError(f"historical source drift: {role}")
        if "bytes" in entry and (
                type(entry["bytes"]) is not int or
                entry["bytes"] != len(raw)):
            raise ValueError(f"historical source length drift: {role}")
        identity = (observed.st_dev, observed.st_ino)
        if identity in seen:
            raise ValueError("historical source physical identity duplicate")
        seen.add(identity)
        manifest.append({
            "role": role, "path": str(path),
            "byte_length": len(raw), "sha256": _sha(raw),
        })
    evidence_state = row.get("evidence_state")
    if evidence_state is not None:
        if type(evidence_state) is not dict or \
                type(evidence_state.get("artifacts")) is not list:
            raise ValueError("historical artifact inventory invalid")
        for entry in sorted(
                evidence_state["artifacts"],
                key=lambda item: item.get("name", "")):
            required = {
                "name", "path", "present", "readable", "recorded_sha256",
                "actual_sha256", "match", "bytes",
            }
            if type(entry) is not dict or not required.issubset(entry):
                raise ValueError("historical artifact entry invalid")
            if (entry["present"] is not True or
                    entry["readable"] is not True or
                    entry["match"] is not True or
                    entry["recorded_sha256"] != entry["actual_sha256"]):
                raise ValueError("historical artifact inventory mismatch")
            path = pathlib.Path(entry["path"]).absolute()
            try:
                path.relative_to(raw_bundle)
            except ValueError as exc:
                raise ValueError(
                    "historical artifact escapes raw bundle") from exc
            raw = lifecycle.read_custodied_bytes(
                path, f"historical artifact {entry['name']}",
                root=raw_bundle)
            observed = os.lstat(path)
            if (not stat.S_ISREG(observed.st_mode) or
                    observed.st_nlink != 1):
                raise ValueError(
                    "historical artifact alias or hardlink forbidden")
            if (_sha(raw) != entry["recorded_sha256"] or
                    len(raw) != entry["bytes"]):
                raise ValueError(
                    f"historical artifact drift: {entry['name']}")
            identity = (observed.st_dev, observed.st_ino)
            if identity in seen:
                raise ValueError(
                    "historical source physical identity duplicate")
            seen.add(identity)
            manifest.append({
                "role": f"artifact:{entry['name']}",
                "path": str(path), "byte_length": len(raw),
                "sha256": _sha(raw),
            })
    return run_root, raw_bundle, manifest


def _validate_decision(value, row, inventory_sha256,
                       evaluator, evaluator_sha256):
    _exact(value, {
        "schema", "source", "evaluator_binding",
        "re_adjudicator_identity", "corrected_view",
        "causal_classification", "uncertainty",
    }, "historical corrected decision")
    if value["schema"] != DECISION_SCHEMA:
        raise ValueError("historical corrected decision schema invalid")
    source = value["source"]
    _exact(source, {
        "campaign", "index", "run_id", "arm", "fixture", "config",
        "stable_cell_identity", "inventory_sha256",
        "canonical_raw_bundle", "original_verdict_sha256",
    }, "historical corrected decision source")
    expected = {
        key: row[key] for key in (
            "campaign", "index", "run_id", "arm", "fixture", "config",
            "stable_cell_identity")
    }
    expected.update({
        "inventory_sha256": inventory_sha256,
        "canonical_raw_bundle": row["paths"]["canonical_raw_bundle"],
        "original_verdict_sha256":
            row["key_file_hashes"]["bundle/verdict.json"]["sha256"],
    })
    if source != expected:
        raise ValueError("historical corrected decision source mismatch")
    expected_evaluator = {
        "sha256": evaluator_sha256, "name": evaluator["name"],
        "git_commit": evaluator["git_commit"],
        "git_tree": evaluator["git_tree"],
        "sources": evaluator["sources"],
    }
    if value["evaluator_binding"] != expected_evaluator:
        raise ValueError(
            "historical corrected decision evaluator identity mismatch")
    if value["re_adjudicator_identity"] != _implementation_identity():
        raise ValueError(
            "historical corrected decision re-adjudicator identity mismatch")
    fixture_entry = row["key_file_hashes"].get("bundle/fixture.json")
    if type(fixture_entry) is not dict:
        raise ValueError(
            "historical corrected decision fixture identity missing")
    fixture, _ = _read_json(
        fixture_entry["path"], "historical authoritative fixture",
        fixture_entry["sha256"])
    corrected = validate_corrected_verdict_v3(
        value["corrected_view"], fixture)
    identity = row.get("model_host_identity")
    expected_substitution = (
        identity.get("requested_model") != identity.get("resolved_model")
        if type(identity) is dict else False)
    if corrected["model_substitution"] is not expected_substitution:
        raise ValueError(
            "historical corrected model substitution identity invalid")
    causal = value["causal_classification"]
    _exact(causal, {"primary", "evidence"}, "historical causal classification")
    if (causal["primary"] not in ORIGINS or
            type(causal["evidence"]) is not list or not causal["evidence"] or
            any(type(item) is not str or not item
                for item in causal["evidence"])):
        raise ValueError("historical causal classification invalid")
    uncertainty = value["uncertainty"]
    _exact(uncertainty, {
        "statement", "disconfirmation_conditions",
    }, "historical uncertainty")
    _string(uncertainty["statement"], "historical uncertainty statement")
    if (type(uncertainty["disconfirmation_conditions"]) is not list or
            not uncertainty["disconfirmation_conditions"] or
            any(type(item) is not str or not item
                for item in uncertainty["disconfirmation_conditions"])):
        raise ValueError("historical disconfirmation conditions invalid")


def _reject_output_inside_sources(output, inventory):
    output = pathlib.Path(output).absolute()
    for row in inventory["bundles"]:
        root = pathlib.Path(row["paths"]["run_root"]).absolute()
        try:
            output.relative_to(root)
        except ValueError:
            continue
        raise ValueError("historical output must be outside source run roots")


def _implementation_identity():
    path = pathlib.Path(__file__).resolve()
    raw = path.read_bytes()
    repo = path.parent.parent
    commit, tree = _git_identity(repo)
    return {
        "path": "eval/historical_readjudicate.py",
        "sha256": _sha(raw), "git_commit": commit, "git_tree": tree,
    }


def adjudicate_one(inventory_path, inventory_sha256, index,
                   decision_path, decision_sha256,
                   evaluator_path, evaluator_sha256, output):
    inventory, _ = _read_json(
        inventory_path, "historical inventory", inventory_sha256)
    _validate_inventory(inventory)
    if type(index) is not int or index not in range(56):
        raise ValueError("historical index invalid")
    evaluator, _ = _read_json(
        evaluator_path, "historical evaluator manifest", evaluator_sha256)
    _validate_evaluator(evaluator)
    decision, decision_raw = _read_json(
        decision_path, "historical corrected decision", decision_sha256)
    row = inventory["bundles"][index]
    _validate_decision(
        decision, row, inventory_sha256, evaluator, evaluator_sha256)
    _run_root, _bundle, source_manifest = _source_manifest(row)
    _reject_output_inside_sources(output, inventory)
    original = row["retained_historical_verdict"]
    record = {
        "schema": RECORD_SCHEMA,
        "inventory_binding": {
            "sha256": inventory_sha256, "index": index,
            "run_id": row["run_id"],
        },
        "evaluator_binding": {
            "sha256": evaluator_sha256,
            "git_commit": evaluator["git_commit"],
            "git_tree": evaluator["git_tree"],
        },
        "re_adjudicator_identity": _implementation_identity(),
        "source_binding": {
            "campaign": row["campaign"], "arm": row["arm"],
            "fixture": row["fixture"], "config": row["config"],
            "stable_cell_identity": row["stable_cell_identity"],
            "canonical_raw_bundle": row["paths"]["canonical_raw_bundle"],
            "files": source_manifest,
        },
        "original_view": {
            "status": original["status"],
            "failed_invariant": original.get("failed_invariant"),
            "verdict_sha256":
                row["key_file_hashes"]["bundle/verdict.json"]["sha256"],
            "bundle_sha256": original["verdict_bundle_sha256"],
        },
        "corrected_view": decision["corrected_view"],
        "causal_classification": decision["causal_classification"],
        "uncertainty": decision["uncertainty"],
        "decision_binding": {
            "path": str(pathlib.Path(decision_path).absolute()),
            "sha256": _sha(decision_raw),
            "byte_length": len(decision_raw),
        },
    }
    try:
        lifecycle.write_new_json(output, record)
    except FileExistsError as exc:
        raise ValueError("create-once historical record exists") from exc
    return record


def _validate_record(value, row, inventory_sha256, evaluator_sha256):
    _exact(value, {
        "schema", "inventory_binding", "evaluator_binding",
        "re_adjudicator_identity", "source_binding", "original_view",
        "corrected_view", "causal_classification", "uncertainty",
        "decision_binding",
    }, "historical record")
    if value["schema"] != RECORD_SCHEMA:
        raise ValueError("historical record schema invalid")
    binding = value["inventory_binding"]
    if binding != {
            "sha256": inventory_sha256, "index": row["index"],
            "run_id": row["run_id"]}:
        raise ValueError("historical record inventory binding invalid")
    if value["evaluator_binding"].get("sha256") != evaluator_sha256:
        raise ValueError("historical record evaluator mismatch")
    source = value["source_binding"]
    if (source.get("arm") != row["arm"] or
            source.get("fixture") != row["fixture"] or
            source.get("config") != row["config"] or
            source.get("stable_cell_identity") !=
            row["stable_cell_identity"]):
        raise ValueError("historical record source mismatch")
    corrected = value["corrected_view"]
    if (type(corrected) is not dict or
            corrected.get("overall_status") not in STATUSES):
        raise ValueError("historical record corrected status invalid")
    _exact(value["decision_binding"], {
        "path", "sha256", "byte_length",
    }, "historical record decision binding")
    _digest(value["decision_binding"]["sha256"],
            "historical record decision")
    if (type(value["decision_binding"]["path"]) is not str or
            not pathlib.Path(value["decision_binding"]["path"]).is_absolute() or
            type(value["decision_binding"]["byte_length"]) is not int or
            value["decision_binding"]["byte_length"] < 1):
        raise ValueError("historical record decision binding invalid")


def aggregate(inventory_path, inventory_sha256, records_root,
              decisions_root, evaluator_path, evaluator_sha256, output):
    inventory, _ = _read_json(
        inventory_path, "historical inventory", inventory_sha256)
    _validate_inventory(inventory)
    evaluator, _ = _read_json(
        evaluator_path, "historical evaluator manifest", evaluator_sha256)
    _validate_evaluator(evaluator)
    _reject_output_inside_sources(output, inventory)
    records_root = pathlib.Path(records_root).absolute()
    decisions_root = pathlib.Path(decisions_root).absolute()
    paths = sorted(records_root.glob("*.json"))
    if len(paths) != 56:
        raise ValueError("historical aggregate requires exactly 56 records")
    counts = {
        "candidate": {status: 0 for status in sorted(STATUSES)},
        "control": {status: 0 for status in sorted(STATUSES)},
    }
    manifest = []
    indices = []
    property_coverage = {
        "declared_rows": 0, "required_rows": 0,
        "verdict_evidence_entries": 0,
        "declared_states": {
            "PASS": 0, "FAIL": 0, "INCOMPLETE": 0},
        "required_states": {
            "PASS": 0, "FAIL": 0, "INCOMPLETE": 0},
    }
    paired = {"candidate": set(), "control": set()}
    for path in paths:
        record, raw = _read_json(path, "historical record")
        index = record.get("inventory_binding", {}).get("index")
        if type(index) is not int or index not in range(56):
            raise ValueError("historical record index invalid")
        row = inventory["bundles"][index]
        _validate_record(record, row, inventory_sha256, evaluator_sha256)
        decision_path = decisions_root / f"decision-{index:02d}.json"
        binding = record["decision_binding"]
        if pathlib.Path(binding["path"]).absolute() != decision_path:
            raise ValueError("historical record decision path mismatch")
        decision, decision_raw = _read_json(
            decision_path, "historical aggregate corrected decision",
            binding["sha256"])
        if len(decision_raw) != binding["byte_length"]:
            raise ValueError("historical aggregate decision length drift")
        _validate_decision(
            decision, row, inventory_sha256, evaluator, evaluator_sha256)
        _run_root, _bundle, source_manifest = _source_manifest(row)
        if record["source_binding"]["files"] != source_manifest:
            raise ValueError(
                "historical aggregate source manifest drift")
        if (record["corrected_view"] != decision["corrected_view"] or
                record["causal_classification"] !=
                decision["causal_classification"] or
                record["uncertainty"] != decision["uncertainty"]):
            raise ValueError(
                "historical aggregate decision/record disagreement")
        indices.append(index)
        paired[row["arm"]].add((row["fixture"], row["config"]))
        counts[row["arm"]][record["corrected_view"]["overall_status"]] += 1
        corrected = record["corrected_view"]
        contract_rows = corrected["property_contract"]
        property_coverage["declared_rows"] += len(contract_rows)
        property_coverage["required_rows"] += sum(
            item["required"] for item in contract_rows)
        property_coverage["verdict_evidence_entries"] += len(
            corrected["verdict_evidence"])
        for item in contract_rows:
            state = corrected["properties"][item["name"]]["state"]
            property_coverage["declared_states"][state] += 1
            if item["required"]:
                property_coverage["required_states"][state] += 1
        manifest.append({
            "path": str(path), "index": index, "run_id": row["run_id"],
            "sha256": _sha(raw),
            "decision_sha256": _sha(decision_raw),
            "source_manifest_sha256": _sha(
                lifecycle.canonical_json_bytes(source_manifest)),
        })
    if sorted(indices) != list(range(56)) or len(set(indices)) != 56:
        raise ValueError("historical aggregate record coverage invalid")
    if (paired["candidate"] != paired["control"] or
            len(paired["candidate"]) != 28):
        raise ValueError(
            "historical aggregate candidate/control pair coverage invalid")
    result = {
        "schema": AGGREGATE_SCHEMA,
        "inventory_sha256": inventory_sha256,
        "evaluator_sha256": evaluator_sha256,
        "historical_view": {
            "candidate": {"passes": 11, "total": 28},
            "control": {"passes": 10, "total": 28},
        },
        "corrected_view": counts,
        "coverage": {
            "record_count": 56,
            "candidate_count": 28,
            "control_count": 28,
            "cells_per_arm": 28,
            "paired_cell_count": len(paired["candidate"]),
        },
        "property_coverage": property_coverage,
        "records": sorted(manifest, key=lambda row: row["index"]),
    }
    try:
        lifecycle.write_new_json(output, result)
    except FileExistsError as exc:
        raise ValueError("create-once historical aggregate exists") from exc
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    one = subparsers.add_parser("adjudicate-one")
    one.add_argument("--inventory", required=True)
    one.add_argument("--inventory-sha256", required=True)
    one.add_argument("--index", required=True, type=int)
    one.add_argument("--decision", required=True)
    one.add_argument("--decision-sha256", required=True)
    one.add_argument("--evaluator-manifest", required=True)
    one.add_argument("--evaluator-manifest-sha256", required=True)
    one.add_argument("--output", required=True)
    all_records = subparsers.add_parser("aggregate")
    all_records.add_argument("--inventory", required=True)
    all_records.add_argument("--inventory-sha256", required=True)
    all_records.add_argument("--records-root", required=True)
    all_records.add_argument("--decisions-root", required=True)
    all_records.add_argument("--evaluator-manifest", required=True)
    all_records.add_argument("--evaluator-manifest-sha256", required=True)
    all_records.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "adjudicate-one":
            adjudicate_one(
                args.inventory, args.inventory_sha256, args.index,
                args.decision, args.decision_sha256,
                args.evaluator_manifest, args.evaluator_manifest_sha256,
                args.output)
        else:
            aggregate(
                args.inventory, args.inventory_sha256, args.records_root,
                args.decisions_root,
                args.evaluator_manifest, args.evaluator_manifest_sha256,
                args.output)
    except (OSError, TypeError, ValueError) as exc:
        print(f"HISTORICAL-READJUDICATE-INVALID: {exc}")
        return 2
    print("HISTORICAL-READJUDICATE-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
