#!/usr/bin/env python3
"""Serialized, create-once driver for the frozen B3-v4 campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone

import adapters
import hosts
import runner
import validate_b3v4_freeze as freeze
import b3v4_contract as contract
import campaign_freeze_preflight as launch_preflight
import evaluated_surfaces as surfaces


STOP_STATES = frozenset({"FAIL", "INVALID", "ERROR"})
CONTINUE_STATES = frozenset({"PASS"})
OFFICIAL_STATES = CONTINUE_STATES | STOP_STATES
SCORED_STATES = frozenset({"PASS", "FAIL"})
FINAL_CLAIMS = {
    "final_12_of_12": False,
    "cross_model_qualified": False,
    "release_authorized": False,
    "tag_authorized": False,
    "publication_authorized": False,
}
INDEPENDENT_PASS_ROW_FIELDS = {
    "index", "config", "arm", "rep", "product_status", "host_status",
    "overall_status", "properties", "reason", "bundle_manifest_sha256",
    "raw_stdout_sha256", "native_session_sha256",
    "official_overall_status", "independent_overall_status",
    "model_resolved", "official_verdict_sha256",
}
REQUIRED_ATTEMPT_ARTIFACTS = {
    "attempt-status.json", "attempt-terminal.json", "host-attestation.json",
    "launch-readiness.json", "official-verdict.json", "host-custody",
}
COMPLETED_ATTEMPT_SEAL_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "mission",
    "execution_mode", "overall_status", "resolved_model", "host_run_root",
    "official_overall_status", "official_verdict_sha256", "stop_reason",
    "error_type", "completed_at", "attempt_name", "attempt_status_sha256",
    "host_attestation_sha256", "launch_readiness_sha256",
    "host_custody_manifest_sha256",
}
MAX_JSON_DEPTH = 512


def _exact_json_equal(left, right):
    """Compare strict JSON models without Python numeric coercion."""
    active_left = set()
    active_right = set()
    stack = [("compare", left, right, 0)]
    while stack:
        action, current_left, current_right, depth = stack.pop()
        if action == "leave":
            active_left.remove(id(current_left))
            active_right.remove(id(current_right))
            continue
        if type(current_left) is not type(current_right):
            return False
        if type(current_left) is dict:
            if depth >= MAX_JSON_DEPTH or set(current_left) != set(current_right):
                return False
            left_id = id(current_left)
            right_id = id(current_right)
            if left_id in active_left or right_id in active_right:
                return False
            active_left.add(left_id)
            active_right.add(right_id)
            stack.append(("leave", current_left, current_right, depth))
            stack.extend(
                ("compare", current_left[key], current_right[key], depth + 1)
                for key in reversed(list(current_left)))
            continue
        if type(current_left) is list:
            if depth >= MAX_JSON_DEPTH or len(current_left) != len(current_right):
                return False
            left_id = id(current_left)
            right_id = id(current_right)
            if left_id in active_left or right_id in active_right:
                return False
            active_left.add(left_id)
            active_right.add(right_id)
            stack.append(("leave", current_left, current_right, depth))
            stack.extend(
                ("compare", left_item, right_item, depth + 1)
                for left_item, right_item in reversed(
                    list(zip(current_left, current_right))))
            continue
        if type(current_left) is float:
            if (not math.isfinite(current_left) or
                    not math.isfinite(current_right) or
                    current_left != current_right or
                    (current_left == 0.0 and
                     math.copysign(1.0, current_left) !=
                     math.copysign(1.0, current_right))):
                return False
            continue
        if type(current_left) in (str, bool, int) or current_left is None:
            if current_left != current_right:
                return False
            continue
        return False
    return True
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERIFIED_IDENTITIES = [
    "fixture_sha256 (bytes + canonical-library authenticity)",
    "prompt_sha256 (bytes + mission consistency)",
    "events_sha256", "repo_before/after snapshot integrity",
    "artifact hashes via artifact-manifest",
]
ATTESTED_IDENTITIES = [
    "product_tag/commit/tree", "installed_payload_sha256",
    "adapter_name/version/sha256", "host",
    "harness_commit (cross-checked when the scoring checkout is available)",
]
VERDICT_FIELDS = {
    "schema", "status", "run_id", "fixture_id", "fixture_sha256",
    "prompt_sha256", "events_sha256", "product_tag", "product_commit",
    "product_tree", "installed_payload_sha256", "harness_commit",
    "adapter_name", "adapter_version", "adapter_sha256", "model_requested",
    "model_resolved", "host", "started_at", "ended_at",
    "model_substitution", "identity_attestation", "bundle_sha256",
    "scorer_commit", "properties", "host_safety", "adjudication",
    "failed_domain", "failed_invariant", "evidence", "reason",
}
PROPERTY_FIELDS = {"state", "pass", "evidence", "describes", "basis"}
HOST_SAFETY_FIELDS = {
    "schema", "status", "failed_invariant", "failed_status", "findings"}
HOST_FINDING_FIELDS = {"gate", "status", "evidence", "reason"}
ADJUDICATION_FIELDS = {
    "schema", "product_status", "host_status", "overall_status",
    "property_evidence_complete", "all_required_properties_true",
    "product_failed_invariant", "host_failed_invariant",
    "host_failed_status", "failed_domain", "failed_invariant",
}


def _strict_json_loads(value):
    return contract.decode_json_bytes(value.encode("utf-8"), "retained JSON")


def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path, *, root=None, owner=None):
    raw = contract.read_custodied_bytes(
        path, owner or f"retained file {pathlib.Path(path).name}", root=root)
    return hashlib.sha256(raw).hexdigest()


def _write_new_json(path, value):
    contract.write_new_json(path, value)


def _read_object(path, owner, *, root=None):
    return contract.load_json_file(path, owner, root=root)


def _expected_host_run_root(attempt_root):
    attempt_root = pathlib.Path(attempt_root).absolute()
    return attempt_root / "host-custody" / attempt_root.name


def _completed_attempt_seal(attempt_root, status, terminal, packet,
                            packet_sha256):
    attempt_root = pathlib.Path(attempt_root).absolute()
    host_root = _expected_host_run_root(attempt_root)
    if terminal["host_run_root"] != str(host_root):
        raise ValueError("attempt host run root identity mismatch")
    host_manifest = contract.read_custodied_directory_manifest(
        attempt_root / "host-custody", "completed host custody",
        root=attempt_root)
    return {
        "schema": "implementaudit-b3v4-completed-attempt-seal-v1",
        "campaign": packet["campaign"],
        "freeze_sha256": packet_sha256,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "mission": status["mission"],
        "execution_mode": terminal["execution_mode"],
        "overall_status": terminal["overall_status"],
        "resolved_model": terminal["resolved_model"],
        "host_run_root": terminal["host_run_root"],
        "official_overall_status": terminal["official_overall_status"],
        "official_verdict_sha256": terminal["official_verdict_sha256"],
        "stop_reason": terminal["stop_reason"],
        "error_type": terminal["error_type"],
        "completed_at": terminal["completed_at"],
        "attempt_name": attempt_root.name,
        "attempt_status_sha256": _sha256_file(
            attempt_root / "attempt-status.json", root=attempt_root,
            owner="attempt status"),
        "host_attestation_sha256": _sha256_file(
            attempt_root / "host-attestation.json", root=attempt_root,
            owner="host attestation"),
        "launch_readiness_sha256": _sha256_file(
            attempt_root / "launch-readiness.json", root=attempt_root,
            owner="launch readiness"),
        "host_custody_manifest_sha256": _sha256_bytes(host_manifest),
    }


def _verify_completed_attempt_seal(attempt_root, status, terminal, packet,
                                   packet_sha256):
    seal = terminal.get("completed_attempt_seal")
    if type(seal) is not dict or set(seal) != COMPLETED_ATTEMPT_SEAL_FIELDS:
        raise ValueError("completed attempt seal identity shape invalid")
    expected = _completed_attempt_seal(
        attempt_root, status, terminal, packet, packet_sha256)
    if not _exact_json_equal(seal, expected):
        raise ValueError("completed attempt seal drift")
    return seal


def _official_error(message):
    raise ValueError("official scorer verdict " + message)


def _nonempty(value):
    return type(value) is str and bool(value)


def _validate_official_verdict(verdict, fixture=None, *, packet=None,
                               mission=None, production=False):
    """Validate the complete scorer-owned verdict, not a mutable summary."""
    if not isinstance(verdict, dict):
        _official_error("must be a JSON object")
    expected_fields = set(VERDICT_FIELDS)
    if verdict.get("model_substitution") is True:
        expected_fields.add("model_substitution_note")
    if set(verdict) != expected_fields:
        _official_error("has missing or extra root fields")
    if fixture is None:
        fixture = _read_object(
            pathlib.Path(__file__).resolve().parent / "fixtures" / "B3-v3" /
            "fixture.json", "B3-v3 fixture")
    if not isinstance(fixture, dict):
        _official_error("has no authoritative fixture")
    adjudication = verdict.get("adjudication")
    host_safety = verdict.get("host_safety")
    properties = verdict.get("properties")
    status = verdict.get("status")
    if (verdict["schema"] != "implementaudit-eval-verdict-v3" or
            status not in OFFICIAL_STATES or
            type(verdict["model_substitution"]) is not bool or
            not isinstance(adjudication, dict) or
            set(adjudication) != ADJUDICATION_FIELDS or
            not isinstance(host_safety, dict) or
            set(host_safety) != HOST_SAFETY_FIELDS or
            not isinstance(properties, dict)):
        _official_error("is incomplete or inconsistent")
    if verdict["model_substitution"] and not _nonempty(
            verdict["model_substitution_note"]):
        _official_error("has malformed substitution custody")
    attestation = verdict["identity_attestation"]
    if (not isinstance(attestation, dict) or
            set(attestation) != {"verified_in_replay", "adapter_attested_only"} or
            not _exact_json_equal(
                attestation["verified_in_replay"], VERIFIED_IDENTITIES) or
            not _exact_json_equal(
                attestation["adapter_attested_only"], ATTESTED_IDENTITIES)):
        _official_error("identity attestation is malformed")
    required_names = [item.get("name") for item in fixture.get("properties", [])]
    if (not required_names or any(not _nonempty(name) for name in required_names) or
            len(required_names) != len(set(required_names)) or
            set(properties) != set(required_names)):
        _official_error("property key set differs from the frozen fixture")
    property_complete = True
    property_values = {}
    for spec in fixture["properties"]:
        name = spec["name"]
        item = properties[name]
        if not isinstance(item, dict) or set(item) != PROPERTY_FIELDS:
            _official_error("property row has missing or extra fields")
        state = item["state"]
        value = item["pass"]
        if (state not in ("PASS", "FAIL", "INCOMPLETE") or
                (state == "PASS" and value is not True) or
                (state == "FAIL" and value is not False) or
                (state == "INCOMPLETE" and value is not None) or
                not _nonempty(item["evidence"]) or
                item["describes"] != spec.get("describes", "") or
                not _nonempty(item["basis"])):
            _official_error("property row is malformed or contradictory")
        property_complete = property_complete and state in ("PASS", "FAIL")
        property_values[name] = value
    findings = host_safety["findings"]
    if not isinstance(findings, list):
        _official_error("host finding list is malformed")
    for finding in findings:
        if (not isinstance(finding, dict) or set(finding) != HOST_FINDING_FIELDS or
                not _nonempty(finding["gate"]) or
                finding["status"] not in OFFICIAL_STATES or
                not isinstance(finding["evidence"], list) or
                not finding["evidence"] or
                any(not _nonempty(item) for item in finding["evidence"]) or
                (finding["reason"] is not None and
                 not _nonempty(finding["reason"]))):
            _official_error("host finding is malformed")
    severity = {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}
    host_status = max((item["status"] for item in findings),
                      key=lambda item: severity[item], default="PASS")
    first_host_failed = next(
        (item for item in findings if item["status"] != "PASS"), None)
    host_failed = next(
        (item for item in findings if item["status"] == host_status), None)
    all_true = (all(property_values[name] is True for name in required_names)
                if property_complete else None)
    product_status = ("PASS" if all_true else "FAIL") \
        if property_complete else "INCOMPLETE"
    if host_status == "ERROR":
        overall = "ERROR"
    elif host_status == "INVALID" or product_status == "INCOMPLETE":
        overall = "INVALID"
    elif host_status == "FAIL" or product_status == "FAIL":
        overall = "FAIL"
    else:
        overall = "PASS"
    product_failed = next(
        (name for name in required_names
         if properties[name]["state"] == "FAIL"), None)
    if overall in ("INVALID", "ERROR"):
        failed_domain = ("infrastructure" if overall == "ERROR"
                         else "identity-custody-or-evidence")
        failed_invariant = ((host_failed or {}).get("gate") or
                            "property-evidence-incomplete")
    elif product_failed:
        failed_domain, failed_invariant = "product-property", product_failed
    elif host_failed:
        failed_domain, failed_invariant = "host-safety", host_failed["gate"]
    else:
        failed_domain = failed_invariant = None
    expected_adjudication = {
        "schema": "implementaudit-eval-adjudication-v1",
        "product_status": product_status, "host_status": host_status,
        "overall_status": overall,
        "property_evidence_complete": property_complete,
        "all_required_properties_true": all_true,
        "product_failed_invariant": product_failed,
        "host_failed_invariant": (first_host_failed or {}).get("gate"),
        "host_failed_status": (first_host_failed or {}).get("status"),
        "failed_domain": failed_domain, "failed_invariant": failed_invariant,
    }
    expected_host = {
        "schema": "implementaudit-host-safety-v1", "status": host_status,
        "failed_invariant": (first_host_failed or {}).get("gate"),
        "failed_status": (first_host_failed or {}).get("status"),
        "findings": findings,
    }
    if (type(adjudication["property_evidence_complete"]) is not bool or
            (adjudication["all_required_properties_true"] is not None and
             type(adjudication["all_required_properties_true"]) is not bool) or
            adjudication["product_status"] not in
            ("PASS", "FAIL", "INCOMPLETE") or
            adjudication["host_status"] not in OFFICIAL_STATES or
            adjudication["overall_status"] not in OFFICIAL_STATES or
            any(value is not None and not _nonempty(value) for value in (
                adjudication["product_failed_invariant"],
                adjudication["host_failed_invariant"],
                adjudication["host_failed_status"],
                adjudication["failed_domain"],
                adjudication["failed_invariant"])) or
            not _exact_json_equal(adjudication, expected_adjudication) or
            not _exact_json_equal(host_safety, expected_host) or
            status != overall or verdict["failed_domain"] != failed_domain or
            verdict["failed_invariant"] != failed_invariant):
        _official_error("layered aggregates are contradictory")
    if (not isinstance(verdict["evidence"], list) or not verdict["evidence"] or
            any(not _nonempty(item) for item in verdict["evidence"]) or
            (verdict["reason"] is not None and not _nonempty(verdict["reason"]))):
        _official_error("evidence custody is incomplete")
    hash_fields = ("fixture_sha256", "prompt_sha256", "events_sha256",
                   "installed_payload_sha256", "adapter_sha256")
    commit_fields = ("product_commit", "product_tree", "harness_commit",
                     "scorer_commit")
    if status in SCORED_STATES:
        if (any(not _nonempty(verdict[field]) for field in (
                "run_id", "fixture_id", "product_tag", "adapter_name",
                "adapter_version", "model_requested", "model_resolved", "host",
                "started_at", "ended_at")) or
                any(not HEX64.fullmatch(str(verdict[field]))
                    for field in hash_fields + ("bundle_sha256",)) or
                any(not HEX40.fullmatch(str(verdict[field]))
                    for field in commit_fields)):
            _official_error("qualification identity is incomplete")
    else:
        for field in hash_fields + ("bundle_sha256",):
            if verdict[field] is not None and not HEX64.fullmatch(str(verdict[field])):
                _official_error("has malformed digest identity")
        for field in commit_fields:
            if verdict[field] is not None and not HEX40.fullmatch(str(verdict[field])):
                _official_error("has malformed commit identity")
    if production and packet is not None and mission is not None:
        config = packet["configurations"][mission["config"]]
        arm = packet[mission["arm"]]
        adapter = "codex-cli" if mission["config"] == "L" else "claude-cli"
        expected_requested = (config["model_requested"]
                              if mission["config"] == "L" else
                              config["model_resolved_required"])
        expected = {
            "run_id": (f"attempt-{mission['index']:03d}-{mission['config']}-"
                       f"{mission['arm']}-r{mission['rep']}"),
            "fixture_id": packet["fixture"]["id"],
            "fixture_sha256": packet["fixture"]["fixture_sha256"],
            "product_commit": arm["commit"], "product_tree": arm["tree"],
            "installed_payload_sha256": arm["payload_sha256"],
            "harness_commit": packet["foundation"]["commit"],
            "scorer_commit": packet["foundation"]["commit"],
            "adapter_name": adapter, "host": adapter,
            "model_requested": expected_requested,
        }
        if any(verdict.get(key) != value for key, value in expected.items()):
            _official_error("identity disagrees with the frozen mission")
        if (not verdict["model_substitution"] and
                verdict["model_resolved"] != config["model_resolved_required"]):
            _official_error("resolved model disagrees with the frozen mission")
    return status


def _write_official_verdict(attempt_root, verdict, fixture, *, packet, mission,
                            production):
    status = _validate_official_verdict(
        verdict, fixture, packet=packet, mission=mission,
        production=production)
    path = attempt_root / "official-verdict.json"
    _write_new_json(path, verdict)
    return status, _sha256_file(
        path, root=attempt_root, owner="official verdict")


def _fixture_for_packet(repo_root, packet):
    path = pathlib.Path(repo_root) / "eval" / "fixtures" / packet["fixture"][
        "id"] / "fixture.json"
    raw = contract.read_custodied_bytes(
        path, "frozen fixture", root=pathlib.Path(repo_root))
    if _sha256_bytes(raw) != packet["fixture"]["fixture_sha256"]:
        raise ValueError("frozen fixture custody drift")
    return contract.decode_json_bytes(raw, "frozen fixture")


def _verify_official_verdict(attempt_root, terminal, fixture, *, packet,
                             mission, production):
    path = attempt_root / "official-verdict.json"
    digest = terminal.get("official_verdict_sha256")
    official = terminal.get("official_overall_status")
    if not path.is_file() or not isinstance(digest, str):
        raise ValueError("prior official verdict custody is incomplete")
    if _sha256_file(
            path, root=attempt_root, owner="official verdict") != digest:
        raise ValueError("prior official verdict custody drift")
    verdict = _read_object(path, "official verdict", root=attempt_root)
    observed = _validate_official_verdict(
        verdict, fixture, packet=packet, mission=mission,
        production=production)
    if observed != official:
        raise ValueError("prior official verdict status drift")
    return official


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode:
        raise ValueError(f"Git identity check failed for {repo}")
    return proc.stdout.strip()


def validate_runtime_identities(packet, *, candidate_checkout,
                                control_checkout):
    """Re-derive product, executable, and approval identities."""
    for arm, checkout in (("candidate", candidate_checkout),
                          ("control", control_checkout)):
        checkout = pathlib.Path(checkout).resolve()
        expected = packet[arm]
        if _git(checkout, "rev-parse", "HEAD") != expected["commit"]:
            raise ValueError(f"{arm} commit identity drift")
        if _git(checkout, "rev-parse", "HEAD^{tree}") != expected["tree"]:
            raise ValueError(f"{arm} tree identity drift")
        if _git(checkout, "rev-parse", "HEAD:skills/implementaudit") != \
                expected["skill_tree"]:
            raise ValueError(f"{arm} skill tree identity drift")
        payload = checkout / "skills" / "implementaudit"
        if adapters.payload_hash(str(payload)) != expected["payload_sha256"]:
            raise ValueError(f"{arm} payload identity drift")
    for name in ("L",):
        executable = packet["configurations"][name]["executable"]
        path = contract.resolve_external_file(
            executable["path"], f"configuration {name} executable")
        if _sha256_file(path) != executable["sha256"]:
            raise ValueError(f"configuration {name} executable identity drift")
        proc = subprocess.run([str(path), "--version"], capture_output=True,
                              text=True, timeout=60)
        observed = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode or executable["version"] not in observed:
            raise ValueError(f"configuration {name} executable version drift")
    approval = packet["authorization"]
    approved_path = os.environ.get("IMPLEMENTAUDIT_BASELINE_APPROVAL")
    if (not approved_path or os.path.realpath(approved_path) !=
            os.path.realpath(approval["acknowledgement_path"])):
        raise ValueError("owner approval acknowledgement identity drift")
    if _sha256_file(approved_path) != approval["acknowledgement_sha256"]:
        raise ValueError("owner approval acknowledgement hash drift")


class MissionContext:
    def __init__(self, **values):
        self.__dict__.update(values)
        self.expected_model = self.packet["configurations"][
            self.mission["config"]]["model_resolved_required"]


class CampaignDriver:
    """Advance exactly one preregistered mission per call without retry."""

    def __init__(self, *, packet_path, repo_root, campaign_root,
                 candidate_checkout, control_checkout, runtime_root,
                 attestations=None, mission_executor=None,
                 execution_mode="production", live_validator=None,
                 identity_validator=None, codex_auth_source=None,
                 launch_readiness=None, launch_context=None):
        if execution_mode not in ("production", "test"):
            raise ValueError("unsupported execution mode")
        if execution_mode == "production" and any(
                item is not None for item in (
                    mission_executor, live_validator, identity_validator)):
            raise ValueError(
                "production execution cannot replace validators or host adapters")
        if execution_mode == "test" and mission_executor is None:
            raise ValueError("test execution requires an explicit mock executor")
        self.packet_path = pathlib.Path(packet_path).absolute()
        self.repo_root = pathlib.Path(repo_root).resolve()
        self.campaign_root = pathlib.Path(campaign_root).absolute()
        self.candidate_checkout = pathlib.Path(candidate_checkout).resolve()
        self.control_checkout = pathlib.Path(control_checkout).resolve()
        self.runtime_root = pathlib.Path(runtime_root).resolve()
        self.attestations = attestations or {}
        self.execution_mode = execution_mode
        self.mission_executor = mission_executor or self._execute_formal_host
        self.live_validator = live_validator or freeze.validate_live
        self.identity_validator = identity_validator or validate_runtime_identities
        self.codex_auth_source = (pathlib.Path(codex_auth_source).resolve()
                                  if codex_auth_source else None)
        self.launch_readiness = (
            pathlib.Path(launch_readiness).absolute()
            if launch_readiness else None)
        self.launch_context = (
            pathlib.Path(launch_context).absolute()
            if launch_context else None)
        self._campaign_root_identity = None

    def _load_launch_context(self):
        if self.execution_mode != "production":
            return None
        if self.launch_context is None:
            raise ValueError("production live launch context is required")
        raw = contract.read_custodied_bytes(
            self.launch_context, "production live launch context",
            root=self.launch_context.parent)
        context = _strict_json_loads(raw.decode("utf-8"))
        if type(context) is not dict:
            raise ValueError("production live launch context must be object")
        auth = context.get("codex_auth_source_path")
        attestation = context.get("host_attestation_path")
        observed = self.attestations.get("L")
        if (self.codex_auth_source is None or type(auth) is not str or
                self.codex_auth_source != pathlib.Path(auth).resolve()):
            raise ValueError(
                "production authentication source/context mismatch")
        if (observed is None or type(attestation) is not str or
                pathlib.Path(observed).resolve() !=
                pathlib.Path(attestation).resolve()):
            raise ValueError(
                "production host attestation/context mismatch")
        return context

    def _load_launch_readiness(self, packet, *, campaign_initialized=False):
        if self.launch_readiness is None:
            raise ValueError("live launch readiness is required")
        return launch_preflight.validate_live_ready(
            "b3v4", packet, self.launch_readiness,
            execution_mode=self.execution_mode,
            live_context=self._load_launch_context(),
            campaign_initialized=campaign_initialized,
            campaign_root_identity=(
                self._campaign_root_identity
                if campaign_initialized else None))

    def _verify_launch_readiness(self, attempt_root, status, packet):
        binding = status["launch_readiness_binding"]
        path = attempt_root / binding["path"]
        report, raw = launch_preflight.validate_live_ready(
            "b3v4", packet, path, execution_mode=self.execution_mode,
            live_context=(self._load_launch_context()
                          if self.launch_context else None),
            retained_only=self.launch_context is None,
            campaign_initialized=True,
            campaign_root_identity=self._campaign_root_identity)
        if (_sha256_bytes(raw) != binding["sha256"] or
                report["schema"] != binding["schema"] or
                report["execution_mode"] != binding["execution_mode"] or
                report["disposition"] != binding["disposition"]):
            raise ValueError("retained launch readiness binding drift")
        return report, raw

    def _load_packet(self):
        raw = contract.read_custodied_bytes(
            self.packet_path, "B3-v4 freeze input", root=self.packet_path.parent)
        packet = _strict_json_loads(raw.decode("utf-8"))
        freeze.validate_structure(packet)
        self.live_validator(packet, self.repo_root)
        return packet, raw, _sha256_bytes(raw)

    def _ensure_campaign(self, raw, packet_sha256, packet):
        frozen = self.campaign_root / "campaign-freeze.json"
        manifest = self.campaign_root / "campaign-manifest.json"
        if not self.campaign_root.exists():
            self._load_launch_readiness(
                packet, campaign_initialized=False)
            try:
                self.campaign_root.mkdir(exist_ok=False)
            except FileExistsError as exc:
                raise ValueError(
                    "campaign root create-once collision") from exc
            root_identity = self._validate_campaign_root_identity()
            with open(frozen, "xb") as stream:
                stream.write(raw)
            _write_new_json(manifest, {
                "schema": "implementaudit-b3v4-luna-campaign-custody-v3",
                "campaign": "b3v4-sol-luna-r2", "freeze_sha256": packet_sha256,
                "contract_sha256": contract.contract_sha256(),
                "created_at": _utc_now(),
                "execution_stage": "LUNA",
                "campaign_root_identity": root_identity,
            })
            self._load_launch_readiness(
                packet, campaign_initialized=True)
        self._validate_campaign_root_identity()
        if not frozen.is_file() or not manifest.is_file():
            raise ValueError("campaign custody is incomplete")
        recorded = _read_object(
            manifest, "campaign manifest", root=self.campaign_root)
        contract.validate_artifact("campaign_manifest", recorded)
        self._validate_campaign_root_identity(
            recorded["campaign_root_identity"])
        if (recorded.get("campaign") != packet["campaign"] or
                recorded.get("freeze_sha256") != packet_sha256 or
                recorded.get("contract_sha256") != contract.contract_sha256() or
                _sha256_file(frozen, root=self.campaign_root,
                             owner="frozen packet") != packet_sha256 or
                contract.read_custodied_bytes(
                    frozen, "frozen packet", root=self.campaign_root) != raw):
            raise ValueError("frozen packet or campaign manifest drift")

    def _campaign_custody_initialized(self):
        return (
            (self.campaign_root / "campaign-freeze.json").is_file() and
            (self.campaign_root / "campaign-manifest.json").is_file())

    def _validate_campaign_root_identity(self, expected=None):
        try:
            resolved = self.campaign_root.resolve(strict=True)
            observed = os.lstat(self.campaign_root)
        except OSError as exc:
            raise ValueError("campaign root custody unavailable") from exc
        if (resolved != self.campaign_root or
                not stat.S_ISDIR(observed.st_mode) or
                stat.S_ISLNK(observed.st_mode) or
                bool(getattr(observed, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
            raise ValueError("campaign root link or reparse alias forbidden")
        identity = {
            "device": observed.st_dev,
            "inode": observed.st_ino,
            "mode": observed.st_mode,
        }
        if expected is not None:
            if (type(expected) is not dict or
                    set(expected) != {"device", "inode", "mode"} or
                    any(type(expected[key]) is not int or expected[key] < 0
                        for key in ("device", "inode", "mode")) or
                    not stat.S_ISDIR(expected["mode"])):
                raise ValueError(
                    "campaign root physical identity invalid")
            if expected != identity:
                raise ValueError(
                    "campaign root physical identity drift")
        if getattr(self, "_campaign_root_identity", None) is None:
            self._campaign_root_identity = identity
        elif self._campaign_root_identity != identity:
            raise ValueError("campaign root identity changed before host spawn")
        return identity

    @staticmethod
    def _attempt_name(mission):
        return (f"attempt-{mission['index']:03d}-{mission['config']}-"
                f"{mission['arm']}-r{mission['rep']}")

    def _next_mission(self, packet):
        allowed_root = {
            "campaign-freeze.json", "campaign-manifest.json",
            "b3v4-luna-independent-rederivation.json",
            "b3v4-luna-result.json", "luna-stage-terminal.json"}
        allowed_root.update(self._attempt_name(m) for m in packet["missions"])
        allowed_root.update(self._attempt_name(m) + ".claiming"
                            for m in packet["missions"])
        unexpected = {p.name for p in self.campaign_root.iterdir()} - allowed_root
        if unexpected:
            raise ValueError("unexpected campaign custody entry")
        expected = {self._attempt_name(m) for m in packet["missions"]}
        actual = {p.name for p in self.campaign_root.glob("attempt-*")
                  if not p.name.endswith(".claiming")}
        if actual - expected:
            raise ValueError("unexpected attempt custody entry")
        stage_artifacts = {
            "b3v4-luna-independent-rederivation.json",
            "b3v4-luna-result.json", "luna-stage-terminal.json"}
        if (stage_artifacts & {p.name for p in self.campaign_root.iterdir()} and
                len(actual) != len(packet["missions"])):
            raise ValueError("Luna stage artifact exists before six terminals")
        if list(self.campaign_root.glob("attempt-*.claiming")):
            raise ValueError("prior attempt is nonterminal")
        for mission in packet["missions"]:
            root = self.campaign_root / self._attempt_name(mission)
            if not root.exists():
                if any((self.campaign_root / self._attempt_name(m)).exists()
                       for m in packet["missions"]
                       if m["index"] > mission["index"]):
                    raise ValueError("campaign attempt order has a gap")
                return mission
            if not root.is_dir():
                raise ValueError("attempt custody entry is not a directory")
            allowed_attempt = {"attempt-status.json", "attempt-terminal.json",
                               "host-attestation.json", "launch-readiness.json",
                               "official-verdict.json",
                               "host-custody"}
            if {path.name for path in root.iterdir()} - allowed_attempt:
                raise ValueError("unexpected attempt custody entry")
            status_path = root / "attempt-status.json"
            terminal_path = root / "attempt-terminal.json"
            if not status_path.is_file() or not terminal_path.is_file():
                raise ValueError("prior attempt is nonterminal")
            status = _read_object(status_path, "attempt status",
                                  root=self.campaign_root)
            terminal = _read_object(terminal_path, "attempt terminal",
                                    root=self.campaign_root)
            contract.validate_artifact("attempt_status", status)
            contract.validate_artifact("attempt_terminal", terminal)
            if (status.get("execution_mode") != self.execution_mode or
                    terminal.get("execution_mode") != self.execution_mode):
                raise ValueError("prior attempt execution mode drift")
            if (not _exact_json_equal(status.get("mission"), mission) or
                    status.get("campaign") != packet["campaign"] or
                    status.get("freeze_sha256") !=
                    _sha256_file(
                        self.campaign_root / "campaign-freeze.json",
                        root=self.campaign_root, owner="frozen packet") or
                    status.get("contract_sha256") !=
                    packet["artifact_contract"]["sha256"] or
                    terminal.get("campaign") != packet["campaign"] or
                    terminal.get("mission_index") != mission["index"]):
                raise ValueError("prior attempt identity drift")
            self._verify_host_attestation(root, status, mission, packet)
            self._verify_launch_readiness(root, status, packet)
            overall = terminal.get("overall_status")
            if terminal.get("official_verdict_sha256") is not None:
                _verify_official_verdict(
                    root, terminal, _fixture_for_packet(self.repo_root, packet),
                    packet=packet, mission=mission,
                    production=self.execution_mode == "production")
            elif overall in CONTINUE_STATES:
                raise ValueError("prior official verdict custody is incomplete")
            if overall in STOP_STATES or terminal.get("stop_reason"):
                raise ValueError("prior attempt stopped campaign")
            if overall not in CONTINUE_STATES:
                raise ValueError("prior attempt has unsupported terminal state")
            if {path.name for path in root.iterdir()} != \
                    REQUIRED_ATTEMPT_ARTIFACTS:
                raise ValueError(
                    "required qualification attempt artifact missing or extra")
            config = packet["configurations"][mission["config"]]
            if (terminal.get("resolved_model") !=
                    config["model_resolved_required"] or
                    terminal.get("official_overall_status") != "PASS" or
                    terminal.get("official_verdict_sha256") is None or
                    terminal.get("error_type") is not None or
                    type(terminal.get("host_run_root")) is not str or
                    not terminal["host_run_root"]):
                raise ValueError("prior attempt terminal binding drift")
            contract.read_custodied_directory_manifest(
                root / "host-custody", "prior host custody",
                root=self.campaign_root)
            _verify_completed_attempt_seal(
                root, status, terminal, packet,
                status["freeze_sha256"])
        raise ValueError(
            "campaign already contains all six Luna attempts; "
            "finalize-luna-stage is required")

    def _load_host_attestation(self, mission, packet):
        config_name = mission["config"]
        source = self.attestations.get(config_name)
        if not source:
            raise ValueError("formal host attestation is required")
        source = pathlib.Path(source)
        raw = contract.read_custodied_bytes(
            source, "host attestation source", root=source.parent)
        attestation = contract.decode_json_bytes(raw, "host attestation")
        contract.validate_host_attestation(attestation)
        expected = packet["configurations"][config_name]["host_attestation"]
        if (attestation["id"] != expected["id"] or
                _sha256_bytes(raw) != expected["sha256"]):
            raise ValueError("host attestation frozen identity mismatch")
        return raw, attestation

    @staticmethod
    def _verify_host_attestation(root, status, mission, packet):
        binding = status["host_attestation_binding"]
        config = packet["configurations"][mission["config"]]
        if not _exact_json_equal(binding, {
                "path": "host-attestation.json",
                "sha256": config["host_attestation"]["sha256"],
                "config": mission["config"], "host": config["host"],
                "model_resolved_required": config["model_resolved_required"]}):
            raise ValueError("host attestation mission identity mismatch")
        path = root / binding["path"]
        if not path.is_file() or _sha256_file(
                path, root=root, owner="host attestation") != binding["sha256"]:
            raise ValueError("host attestation custody hash mismatch")
        retained = _read_object(path, "host attestation", root=root)
        contract.validate_host_attestation(retained)
        if retained["id"] != config["host_attestation"]["id"]:
            raise ValueError("host attestation retained identity mismatch")
        return retained

    def _claim_attempt(self, mission, packet_sha256, packet,
                       readiness_raw, readiness):
        name = self._attempt_name(mission)
        claiming = self.campaign_root / (name + ".claiming")
        final = self.campaign_root / name
        attestation_raw, _ = self._load_host_attestation(mission, packet)
        launch_preflight.validate_live_ready(
            "b3v4", packet, self.launch_readiness,
            execution_mode=self.execution_mode,
            live_context=self._load_launch_context(),
            campaign_initialized=True,
            campaign_root_identity=self._campaign_root_identity)
        claiming.mkdir(exist_ok=False)
        with open(claiming / "host-attestation.json", "xb") as stream:
            stream.write(attestation_raw)
        with open(claiming / "launch-readiness.json", "xb") as stream:
            stream.write(readiness_raw)
        config = packet["configurations"][mission["config"]]
        _write_new_json(claiming / "attempt-status.json", {
            "schema": "implementaudit-b3v4-luna-attempt-status-v2",
            "campaign": "b3v4-sol-luna-r2", "freeze_sha256": packet_sha256,
            "contract_sha256": contract.contract_sha256(),
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": self.execution_mode, "created_at": _utc_now(),
            "host_attestation_binding": {
                "path": "host-attestation.json",
                "sha256": config["host_attestation"]["sha256"],
                "config": mission["config"], "host": config["host"],
                "model_resolved_required": config["model_resolved_required"],
            },
            "launch_readiness_binding": {
                "path": "launch-readiness.json",
                "sha256": _sha256_bytes(readiness_raw),
                "schema": readiness["schema"],
                "execution_mode": readiness["execution_mode"],
                "disposition": readiness["disposition"],
            },
        })
        os.rename(claiming, final)
        return final

    def _validate_identities(self, packet):
        self.identity_validator(
            packet, candidate_checkout=self.candidate_checkout,
            control_checkout=self.control_checkout)

    def _validate_surfaces(self, packet):
        if self.execution_mode == "production":
            surfaces.validate_packet_surfaces(
                packet, surfaces.B3_CAMPAIGN, root=self.repo_root)

    def _verify_frozen_binding(self, expected_sha):
        packet, raw, observed_sha = self._load_packet()
        if observed_sha != expected_sha:
            raise ValueError("frozen packet drift")
        self._ensure_campaign(raw, observed_sha, packet)
        self._validate_identities(packet)
        self._validate_surfaces(packet)

    def run_next(self):
        packet, raw, packet_sha256 = self._load_packet()
        campaign_initialized = self._campaign_custody_initialized()
        readiness = readiness_raw = None
        if not campaign_initialized:
            readiness, readiness_raw = self._load_launch_readiness(
                packet, campaign_initialized=False)
        fixture = _fixture_for_packet(self.repo_root, packet)
        self._ensure_campaign(raw, packet_sha256, packet)
        if campaign_initialized:
            readiness, readiness_raw = self._load_launch_readiness(
                packet, campaign_initialized=True)
        self._validate_identities(packet)
        mission = self._next_mission(packet)
        self._validate_surfaces(packet)
        reread, reread_raw = self._load_launch_readiness(
            packet, campaign_initialized=True)
        if reread_raw != readiness_raw:
            raise ValueError("live launch readiness changed before claim")
        attempt_root = self._claim_attempt(
            mission, packet_sha256, packet, reread_raw, reread)
        status = None
        terminal = {
            "schema": "implementaudit-b3v4-luna-attempt-terminal-v3",
            "campaign": "b3v4-sol-luna-r2", "mission_index": mission["index"],
            "execution_mode": self.execution_mode,
            "overall_status": None, "resolved_model": None,
            "host_run_root": None, "official_overall_status": None,
            "official_verdict_sha256": None, "stop_reason": None,
            "error_type": None, "completed_at": None,
            "completed_attempt_seal": None,
        }
        try:
            self._validate_campaign_root_identity()
            status = _read_object(
                attempt_root / "attempt-status.json",
                "attempt status", root=self.campaign_root)
            retained_attestation = self._verify_host_attestation(
                attempt_root, status, mission, packet)
            self._verify_launch_readiness(
                attempt_root, status, packet)
            context = MissionContext(
                packet=packet, packet_sha256=packet_sha256, mission=mission,
                attempt_root=attempt_root,
                candidate_checkout=self.candidate_checkout,
                control_checkout=self.control_checkout,
                runtime_root=self.runtime_root,
                attestations=self.attestations,
                host_attestation=retained_attestation)
            self._validate_surfaces(packet)
            live_again, live_again_raw = self._load_launch_readiness(
                packet, campaign_initialized=True)
            retained_again, retained_again_raw = \
                self._verify_launch_readiness(
                    attempt_root, status, packet)
            if (live_again_raw != readiness_raw or
                    retained_again_raw != readiness_raw or
                    live_again != retained_again):
                raise ValueError(
                    "launch readiness changed before host spawn")
            self._validate_campaign_root_identity()
            outcome = self.mission_executor(context)
            if not isinstance(outcome, dict):
                raise TypeError("mission executor returned a non-object")
            claimed_status = outcome.get("overall_status")
            official_verdict = outcome.get("official_verdict")
            terminal.update({
                "overall_status": claimed_status,
                "resolved_model": outcome.get("resolved_model"),
                "host_run_root": outcome.get("host_run_root"),
            })
            if official_verdict is not None:
                official_status, official_sha = _write_official_verdict(
                    attempt_root, official_verdict, fixture, packet=packet,
                    mission=mission,
                    production=self.execution_mode == "production")
                terminal.update({
                    "official_overall_status": official_status,
                    "official_verdict_sha256": official_sha,
                    "overall_status": official_status,
                })
                if claimed_status != official_status:
                    terminal["stop_reason"] = "executor-status-disagrees-with-official-verdict"
                if (official_status in SCORED_STATES and
                        official_verdict.get("model_resolved") !=
                        terminal["resolved_model"]):
                    terminal["overall_status"] = "INVALID"
                    terminal["stop_reason"] = "official-model-identity-disagrees"
            elif claimed_status in SCORED_STATES:
                terminal["overall_status"] = "ERROR"
                terminal["stop_reason"] = "official-verdict-missing"
            try:
                self._verify_frozen_binding(packet_sha256)
            except (OSError, ValueError, json.JSONDecodeError):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "frozen-input-drift"
            resolved = terminal.get("resolved_model")
            if (terminal.get("overall_status") in SCORED_STATES and
                    resolved != context.expected_model):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "model-substitution"
            expected_host_root = str(_expected_host_run_root(attempt_root))
            if (terminal.get("overall_status") in SCORED_STATES and
                    terminal.get("host_run_root") != expected_host_root):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "host-run-root-identity-mismatch"
            elif (terminal.get("overall_status") == "INVALID" and
                  resolved is not None and resolved != context.expected_model):
                terminal["stop_reason"] = "model-substitution"
            if terminal.get("overall_status") not in CONTINUE_STATES | STOP_STATES:
                terminal["overall_status"] = "ERROR"
                terminal["stop_reason"] = "unsupported-executor-result"
            elif terminal["overall_status"] in STOP_STATES:
                if not terminal.get("stop_reason"):
                    terminal["stop_reason"] = (
                        "failed-mission-halts-campaign"
                        if terminal["overall_status"] == "FAIL" else
                        "invalid-or-error-halts-campaign")
        except Exception as exc:
            terminal.update({
                "overall_status": "ERROR", "resolved_model": None,
                "host_run_root": None, "stop_reason": "mission-execution-exception",
                "error_type": type(exc).__name__,
            })
            try:
                self._verify_frozen_binding(packet_sha256)
            except (OSError, ValueError, json.JSONDecodeError):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "frozen-input-drift"
        terminal["completed_at"] = _utc_now()
        if terminal["overall_status"] in SCORED_STATES:
            terminal["completed_attempt_seal"] = _completed_attempt_seal(
                attempt_root, status, terminal, packet, packet_sha256)
        contract.validate_artifact("attempt_terminal", terminal)
        _write_new_json(attempt_root / "attempt-terminal.json", terminal)
        return terminal

    @staticmethod
    def _stage_root_policy(packet_raw, packet_sha256, manifest_identity,
                           independent_raw, official_raw=None):
        allowed = {
            "campaign-freeze.json": {
                "kind": "exact_bytes", "byte_length": len(packet_raw),
                "sha256": packet_sha256},
            "campaign-manifest.json": {
                "kind": "json_identity", "identity": manifest_identity},
        }
        if independent_raw is not None:
            allowed["b3v4-luna-independent-rederivation.json"] = {
                "kind": "exact_bytes", "byte_length": len(independent_raw),
                "sha256": _sha256_bytes(independent_raw)}
        if official_raw is not None:
            allowed["b3v4-luna-result.json"] = {
                "kind": "exact_bytes", "byte_length": len(official_raw),
                "sha256": _sha256_bytes(official_raw)}
        return allowed

    def _stage_descriptor(self, packet, packet_raw, packet_sha256,
                          independent_raw=None, official_raw=None):
        missions = []
        for mission in packet["missions"]:
            status_identity = {
                "schema": "implementaudit-b3v4-luna-attempt-status-v2",
                "campaign": packet["campaign"],
                "freeze_sha256": packet_sha256,
                "contract_sha256": packet["artifact_contract"]["sha256"],
                "mission": mission,
            }
            terminal_identity = {
                "schema": "implementaudit-b3v4-luna-attempt-terminal-v3",
                "campaign": packet["campaign"],
                "mission_index": mission["index"],
            }
            missions.append({
                "attempt": self._attempt_name(mission),
                "status_identity": status_identity,
                "terminal_identity": terminal_identity,
                "terminal_state_field": "overall_status",
                "terminal_stop_reason_field": "stop_reason",
                "allowed_attempt": {
                    "attempt-status.json": {
                        "kind": "json_identity", "identity": status_identity},
                    "attempt-terminal.json": {
                        "kind": "json_identity", "identity": terminal_identity},
                    "host-attestation.json": {"kind": "custodied_file"},
                    "launch-readiness.json": {"kind": "custodied_file"},
                    "official-verdict.json": {"kind": "custodied_file"},
                    "host-custody": {"kind": "custodied_directory"},
                },
            })
        manifest_identity = {
            "schema": "implementaudit-b3v4-luna-campaign-custody-v3",
            "campaign": packet["campaign"],
            "freeze_sha256": packet_sha256,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "execution_stage": "LUNA",
            "campaign_root_identity": self._campaign_root_identity,
        }
        return {
            "name": packet["luna_stage"]["name"],
            "campaign": packet["campaign"],
            "schema": packet["luna_stage"]["schema"],
            "terminal_name": packet["luna_stage"]["terminal_name"],
            "missions": missions,
            "stop_states": sorted(STOP_STATES),
            "allowed_root": self._stage_root_policy(
                packet_raw, packet_sha256, manifest_identity,
                independent_raw, official_raw),
        }

    @staticmethod
    def _result_claims(value, owner):
        if not _exact_json_equal(value, FINAL_CLAIMS):
            raise ValueError(f"{owner} contains a forbidden final claim")

    def _validate_independent_luna_result(self, value, packet, packet_sha256,
                                          summaries):
        fields = {
            "schema", "campaign", "freeze_sha256", "contract_sha256",
            "luna_stage_status", "disposition", "luna_stage_accepted",
            "accepted", "mission_count", "missions", "claims"}
        if type(value) is not dict or set(value) != fields:
            raise ValueError("independent Luna result key set invalid")
        if (value["schema"] !=
                "implementaudit-b3v4-luna-independent-rederivation-v2" or
                value["campaign"] != packet["campaign"] or
                value["freeze_sha256"] != packet_sha256 or
                value["contract_sha256"] !=
                packet["artifact_contract"]["sha256"] or
                value["luna_stage_status"] != "PASS" or
                value["disposition"] != "INCOMPLETE_PENDING_OPUS" or
                value["luna_stage_accepted"] is not True or
                value["accepted"] is not False or
                type(value["mission_count"]) is not int or
                value["mission_count"] != 6 or
                type(value["missions"]) is not list or
                len(value["missions"]) != 6):
            raise ValueError("independent Luna result is not accepted 6/6")
        self._result_claims(value["claims"], "independent Luna result")
        for expected, observed in zip(summaries, value["missions"]):
            if type(observed) is not dict or set(observed) != \
                    INDEPENDENT_PASS_ROW_FIELDS:
                raise ValueError("independent Luna mission row schema invalid")
            if (set(expected) != INDEPENDENT_PASS_ROW_FIELDS or
                    not _exact_json_equal(observed, expected)):
                raise ValueError("official and independent Luna results disagree")
        return value

    def _luna_summaries(self, packet, packet_sha256, rows):
        if len(rows) != len(packet["missions"]):
            if rows and (rows[-1]["terminal"]["overall_status"] in STOP_STATES or
                         rows[-1]["terminal"]["stop_reason"] is not None):
                raise ValueError("stopped prefix cannot create a Luna stage result")
            raise ValueError("Luna stage terminal requires the exact declared prefix")
        fixture = _fixture_for_packet(self.repo_root, packet)
        summaries = []
        for mission, row in zip(packet["missions"], rows):
            attempt = self.campaign_root / self._attempt_name(mission)
            terminal = row["terminal"]
            status = row["status"]
            if {path.name for path in attempt.iterdir()} != \
                    REQUIRED_ATTEMPT_ARTIFACTS:
                raise ValueError(
                    "required qualification attempt artifact missing or extra")
            contract.validate_artifact("attempt_status", status)
            contract.validate_artifact("attempt_terminal", terminal)
            if (not _exact_json_equal(status["mission"], mission) or
                    status["campaign"] != packet["campaign"] or
                    status["freeze_sha256"] != packet_sha256 or
                    status["contract_sha256"] !=
                    packet["artifact_contract"]["sha256"] or
                    status["execution_mode"] != self.execution_mode or
                    terminal["campaign"] != packet["campaign"] or
                    terminal["mission_index"] != mission["index"] or
                    terminal["execution_mode"] != self.execution_mode):
                raise ValueError("retained attempt identity drift")
            self._verify_host_attestation(attempt, status, mission, packet)
            if (terminal["overall_status"] != "PASS" or
                    terminal["official_overall_status"] != "PASS" or
                    terminal["resolved_model"] != packet["configurations"][
                        "L"]["model_resolved_required"] or
                    terminal["stop_reason"] is not None):
                raise ValueError("stopped prefix cannot create a Luna stage result")
            _verify_official_verdict(
                attempt, terminal, fixture, packet=packet, mission=mission,
                production=self.execution_mode == "production")
            _verify_completed_attempt_seal(
                attempt, status, terminal, packet, packet_sha256)
            verdict = _read_object(
                attempt / "official-verdict.json", "official verdict",
                root=attempt)
            name = self._attempt_name(mission)
            bundle = attempt / "host-custody" / name / "bundle"
            properties = {
                property_name: {
                    "state": property_row["state"],
                    "pass": property_row["pass"],
                }
                for property_name, property_row in
                verdict["properties"].items()
            }
            summaries.append({
                "index": mission["index"], "config": mission["config"],
                "arm": mission["arm"], "rep": mission["rep"],
                "product_status":
                    verdict["adjudication"]["product_status"],
                "host_status": verdict["adjudication"]["host_status"],
                "overall_status": terminal["overall_status"],
                "properties": properties, "reason": None,
                "bundle_manifest_sha256": _sha256_file(
                    bundle / "manifest.json", root=attempt,
                    owner="bundle manifest"),
                "raw_stdout_sha256": _sha256_file(
                    bundle / "artifacts" / "host-stdout.raw", root=attempt,
                    owner="host stdout"),
                "native_session_sha256": _sha256_file(
                    bundle / "artifacts" / "host-session.raw", root=attempt,
                    owner="host session"),
                "official_overall_status": terminal["official_overall_status"],
                "independent_overall_status": "PASS",
                "model_resolved": terminal["resolved_model"],
                "official_verdict_sha256":
                    terminal["official_verdict_sha256"],
            })
        return summaries

    @staticmethod
    def _luna_identity(packet):
        config = packet["configurations"]["L"]
        return {
            "config": "L", "host": config["host"],
            "model_resolved_required": config["model_resolved_required"],
            "host_attestation_id": config["host_attestation"]["id"],
            "host_attestation_sha256": config["host_attestation"]["sha256"],
        }

    def _official_luna_result(self, packet, packet_sha256, summaries,
                              independent_raw):
        independent_path = packet["luna_stage"]["independent_result_name"]
        return {
            "schema": "implementaudit-b3v4-luna-result-v2",
            "campaign": packet["campaign"], "freeze_sha256": packet_sha256,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "disposition": "INCOMPLETE_PENDING_OPUS",
            "luna_stage_accepted": True, "accepted": False,
            "mission_count": 6, "missions": summaries,
            "luna_identity": self._luna_identity(packet),
            "independent_rederivation": {
                "path": independent_path,
                "sha256": _sha256_bytes(independent_raw),
                "schema":
                    "implementaudit-b3v4-luna-independent-rederivation-v2",
                "contract_id": packet["independent_rederiver"]["contract_id"],
                "implementation_sha256": packet["independent_rederiver"][
                    "implementation_identity"]["sha256"],
            },
            "claims": dict(FINAL_CLAIMS),
        }

    def _stage_binding(self, packet, packet_sha256, official_raw,
                       independent_raw):
        return {
            "campaign": packet["campaign"], "stage": "LUNA",
            "stage_schema": packet["luna_stage"]["schema"],
            "mission_count": 6, "freeze_sha256": packet_sha256,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "official_result_sha256": _sha256_bytes(official_raw),
            "independent_rederivation_sha256":
                _sha256_bytes(independent_raw),
            "independent_rederiver_contract":
                packet["independent_rederiver"]["contract_id"],
            "luna_identity": self._luna_identity(packet),
            "claims": dict(FINAL_CLAIMS),
        }

    def finalize_luna_stage(self):
        result_path = self.campaign_root / "b3v4-luna-result.json"
        terminal_path = self.campaign_root / "luna-stage-terminal.json"
        if result_path.exists() or terminal_path.exists():
            raise ValueError("create-once Luna stage artifact already exists")
        packet, packet_raw, packet_sha256 = self._load_packet()
        self._ensure_campaign(packet_raw, packet_sha256, packet)
        self._validate_identities(packet)
        self._validate_surfaces(packet)
        independent_path = self.campaign_root / packet["luna_stage"][
            "independent_result_name"]
        independent_raw = None
        if independent_path.exists():
            independent_raw = contract.read_custodied_bytes(
                independent_path, "independent Luna result",
                root=self.campaign_root)
        pre_descriptor = self._stage_descriptor(
            packet, packet_raw, packet_sha256, independent_raw)
        pre_rows = contract.lifecycle.validate_terminal_prefix(
            self.campaign_root, pre_descriptor["missions"],
            stop_states=pre_descriptor["stop_states"],
            allowed_root=pre_descriptor["allowed_root"])
        summaries = self._luna_summaries(packet, packet_sha256, pre_rows)
        if independent_raw is None:
            independent_raw = contract.read_custodied_bytes(
                independent_path, "independent Luna result",
                root=self.campaign_root)
        independent = contract.decode_json_bytes(
            independent_raw, "independent Luna result", require_object=True)
        self._validate_independent_luna_result(
            independent, packet, packet_sha256, summaries)
        result = self._official_luna_result(
            packet, packet_sha256, summaries, independent_raw)
        contract.validate_artifact("official_luna_result", result)
        _write_new_json(result_path, result)
        official_raw = contract.read_custodied_bytes(
            result_path, "official Luna result", root=self.campaign_root)
        descriptor = self._stage_descriptor(
            packet, packet_raw, packet_sha256, independent_raw, official_raw)
        binding = self._stage_binding(
            packet, packet_sha256, official_raw, independent_raw)
        contract.lifecycle.write_stage_terminal(
            self.campaign_root, descriptor, binding)
        return result

    def _validate_luna_stage(self, *, validate_runtime_identities=True):
        packet, packet_raw, packet_sha256 = self._load_packet()
        self._ensure_campaign(packet_raw, packet_sha256, packet)
        if validate_runtime_identities:
            self._validate_identities(packet)
        self._validate_surfaces(packet)
        independent_path = self.campaign_root / packet["luna_stage"][
            "independent_result_name"]
        result_path = self.campaign_root / packet["luna_stage"][
            "official_result_name"]
        independent_raw = contract.read_custodied_bytes(
            independent_path, "independent Luna result", root=self.campaign_root)
        official_raw = contract.read_custodied_bytes(
            result_path, "official Luna result", root=self.campaign_root)
        descriptor = self._stage_descriptor(
            packet, packet_raw, packet_sha256, independent_raw, official_raw)
        binding = self._stage_binding(
            packet, packet_sha256, official_raw, independent_raw)
        contract.lifecycle.validate_stage_resume(
            self.campaign_root, descriptor, binding)
        independent = contract.decode_json_bytes(
            independent_raw, "independent Luna result", require_object=True)
        official = contract.decode_json_bytes(
            official_raw, "official Luna result", require_object=True)
        rows = contract.lifecycle.validate_terminal_prefix(
            self.campaign_root, descriptor["missions"],
            stop_states=descriptor["stop_states"],
            allowed_root={**descriptor["allowed_root"],
                          "luna-stage-terminal.json": {
                              "kind": "exact_bytes",
                              "byte_length": len(contract.read_custodied_bytes(
                                  self.campaign_root /
                                  "luna-stage-terminal.json",
                                  "stage terminal", root=self.campaign_root)),
                              "sha256": _sha256_file(
                                  self.campaign_root /
                                  "luna-stage-terminal.json",
                                  root=self.campaign_root,
                                  owner="stage terminal")}})
        summaries = self._luna_summaries(packet, packet_sha256, rows)
        self._validate_independent_luna_result(
            independent, packet, packet_sha256, summaries)
        expected = self._official_luna_result(
            packet, packet_sha256, summaries, independent_raw)
        if contract.canonical_json_bytes(official) != \
                contract.canonical_json_bytes(expected):
            raise ValueError("official Luna result drift")
        return official

    def validate_luna_stage(self):
        return self._validate_luna_stage()

    def _execute_formal_host(self, context):
        mission = context.mission
        config_name = mission["config"]
        config = context.packet["configurations"][config_name]
        product = (context.candidate_checkout if mission["arm"] == "candidate"
                   else context.control_checkout)
        runtime = context.runtime_root / self._attempt_name(mission)
        runtime.mkdir(parents=True, exist_ok=False)
        attestation = context.host_attestation
        executable = config["executable"]["path"]
        common = {
            "product_checkout": str(product),
            "product_expected_rev": context.packet[mission["arm"]]["commit"],
            "formal": True, "lane_id": config_name,
            "host_read_attestation": attestation,
        }
        if config_name != "L":
            raise ValueError("only the frozen Luna configuration is authorized")
        home = runtime / "codex-home"
        home.mkdir()
        if self.codex_auth_source:
            shutil.copy2(self.codex_auth_source, home / "auth.json")
        adapter = hosts.CodexAdapter(
            requested_model=config["model_requested"],
            reasoning_effort=config["reasoning_effort"],
            codex_binary=executable, codex_home=str(home), **common)
        custody = context.attempt_root / "host-custody"
        custody.mkdir()
        work = runtime / "fixture-work"
        work.mkdir()
        run_id = self._attempt_name(mission)
        result = adapter.run_mission(
            context.packet["fixture"]["id"], str(custody), run_id,
            str(work), call_ordinal=mission["index"] + 1)
        host_root = custody / run_id
        if result.kind != "ok":
            return {"overall_status":
                    "INVALID" if result.kind == "invalid" else "ERROR",
                    "resolved_model": result.resolved_model,
                    "host_run_root": str(host_root)}
        status, verdict = runner.score_bundle(result.detail, repo_dir=None)
        return {"overall_status": status,
                "resolved_model": result.resolved_model,
                "host_run_root": str(host_root),
                "official_verdict": verdict}


def validate_retained_luna_stage(packet_path, campaign_root, surface_root):
    """Validate a completed retained stage without launching or Git mutation."""
    driver = object.__new__(CampaignDriver)
    driver.packet_path = pathlib.Path(packet_path).absolute()
    driver.repo_root = pathlib.Path(surface_root).resolve()
    driver.campaign_root = pathlib.Path(campaign_root).absolute()
    driver.execution_mode = "production"
    driver.live_validator = lambda packet, root: \
        surfaces.validate_packet_surfaces(
            packet, surfaces.B3_CAMPAIGN, root=root)
    return driver._validate_luna_stage(validate_runtime_identities=False)


def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="operation", required=True)

    def add_common(name):
        command = subparsers.add_parser(name)
        command.add_argument("intent")
        command.add_argument("--repo-root", required=True)
        command.add_argument("--campaign-root", required=True)
        command.add_argument("--candidate-checkout", required=True)
        command.add_argument("--control-checkout", required=True)
        command.add_argument("--runtime-root", required=True)
        command.add_argument("--l-attestation", required=True)
        command.add_argument("--codex-auth-source")
        return command

    run_next = add_common("run-next")
    run_next.add_argument("--launch-readiness", required=True)
    run_next.add_argument("--launch-context", required=True)
    add_common("finalize-luna-stage")
    add_common("validate-luna-stage")
    args = parser.parse_args(argv)
    driver = CampaignDriver(
        packet_path=args.intent, repo_root=args.repo_root,
        campaign_root=args.campaign_root,
        candidate_checkout=args.candidate_checkout,
        control_checkout=args.control_checkout, runtime_root=args.runtime_root,
        attestations={"L": args.l_attestation},
        codex_auth_source=args.codex_auth_source,
        launch_readiness=getattr(args, "launch_readiness", None),
        launch_context=getattr(args, "launch_context", None))
    if args.operation == "run-next":
        terminal = driver.run_next()
        print(json.dumps({"mission_index": terminal["mission_index"],
                          "overall_status": terminal["overall_status"],
                          "stop_reason": terminal.get("stop_reason")},
                         sort_keys=True))
        return 0 if terminal["overall_status"] in CONTINUE_STATES else 2
    result = (driver.finalize_luna_stage()
              if args.operation == "finalize-luna-stage" else
              driver.validate_luna_stage())
    print(json.dumps({
        "disposition": result["disposition"],
        "luna_stage_accepted": result["luna_stage_accepted"],
        "accepted": result["accepted"],
        "mission_count": result["mission_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"B3V4-CAMPAIGN-REFUSED: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(2)
