#!/usr/bin/env python3
"""Serialized, create-once driver for the frozen B3-v4 campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

import adapters
import hosts
import runner
import validate_b3v4_freeze as freeze
import b3v4_contract as contract


STOP_STATES = frozenset({"INVALID", "ERROR"})
CONTINUE_STATES = frozenset({"PASS", "FAIL"})
OFFICIAL_STATES = CONTINUE_STATES | STOP_STATES
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


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_new_json(path, value):
    contract.write_new_json(path, value)


def _read_object(path, owner):
    return contract.load_json_file(path, owner)


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
            attestation["verified_in_replay"] != VERIFIED_IDENTITIES or
            attestation["adapter_attested_only"] != ATTESTED_IDENTITIES):
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
    if overall in STOP_STATES:
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
            adjudication != expected_adjudication or host_safety != expected_host or
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
    if status in CONTINUE_STATES:
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
    return status, _sha256_file(path)


def _fixture_for_packet(repo_root, packet):
    path = pathlib.Path(repo_root) / "eval" / "fixtures" / packet["fixture"][
        "id"] / "fixture.json"
    raw = path.read_bytes()
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
    if _sha256_file(path) != digest:
        raise ValueError("prior official verdict custody drift")
    verdict = _read_object(path, "official verdict")
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
    for name in ("L", "O"):
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
                 identity_validator=None, codex_auth_source=None):
        if execution_mode not in ("production", "test"):
            raise ValueError("unsupported execution mode")
        if execution_mode == "production" and any(
                item is not None for item in (
                    mission_executor, live_validator, identity_validator)):
            raise ValueError(
                "production execution cannot replace validators or host adapters")
        if execution_mode == "test" and mission_executor is None:
            raise ValueError("test execution requires an explicit mock executor")
        self.packet_path = pathlib.Path(packet_path).resolve()
        self.repo_root = pathlib.Path(repo_root).resolve()
        self.campaign_root = pathlib.Path(campaign_root).resolve()
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

    def _load_packet(self):
        raw = self.packet_path.read_bytes()
        packet = _strict_json_loads(raw.decode("utf-8"))
        freeze.validate_structure(packet)
        self.live_validator(packet, self.repo_root)
        return packet, raw, _sha256_bytes(raw)

    def _ensure_campaign(self, raw, packet_sha256):
        frozen = self.campaign_root / "campaign-freeze.json"
        manifest = self.campaign_root / "campaign-manifest.json"
        if not self.campaign_root.exists():
            self.campaign_root.mkdir(parents=True, exist_ok=False)
            with open(frozen, "xb") as stream:
                stream.write(raw)
            _write_new_json(manifest, {
                "schema": "implementaudit-b3v4-campaign-custody-v1",
                "campaign": "b3v4-sol-r1", "freeze_sha256": packet_sha256,
                "contract_sha256": contract.contract_sha256(),
                "created_at": _utc_now(),
                "execution_stage": "LUNA_THEN_OPUS_UNCHANGED_PACKET",
            })
        if not frozen.is_file() or not manifest.is_file():
            raise ValueError("campaign custody is incomplete")
        recorded = _read_object(manifest, "campaign manifest")
        contract.validate_artifact("campaign_manifest", recorded)
        if (recorded.get("freeze_sha256") != packet_sha256 or
                recorded.get("contract_sha256") != contract.contract_sha256() or
                _sha256_file(frozen) != packet_sha256 or
                frozen.read_bytes() != raw):
            raise ValueError("frozen packet drift")

    @staticmethod
    def _attempt_name(mission):
        return (f"attempt-{mission['index']:03d}-{mission['config']}-"
                f"{mission['arm']}-r{mission['rep']}")

    def _next_mission(self, packet):
        allowed_root = {"campaign-freeze.json", "campaign-manifest.json"}
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
                               "host-attestation.json", "official-verdict.json",
                               "host-custody"}
            if {path.name for path in root.iterdir()} - allowed_attempt:
                raise ValueError("unexpected attempt custody entry")
            status_path = root / "attempt-status.json"
            terminal_path = root / "attempt-terminal.json"
            if not status_path.is_file() or not terminal_path.is_file():
                raise ValueError("prior attempt is nonterminal")
            status = _read_object(status_path, "attempt status")
            terminal = _read_object(terminal_path, "attempt terminal")
            contract.validate_artifact("attempt_status", status)
            contract.validate_artifact("attempt_terminal", terminal)
            if (status.get("mission") != mission or
                    terminal.get("mission_index") != mission["index"]):
                raise ValueError("prior attempt identity drift")
            self._verify_host_attestation(root, status, mission, packet)
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
        raise ValueError("campaign already contains all 12 attempts")

    def _load_host_attestation(self, mission, packet):
        config_name = mission["config"]
        source = self.attestations.get(config_name)
        if not source:
            raise ValueError("formal host attestation is required")
        raw = pathlib.Path(source).read_bytes()
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
        if binding != {
                "path": "host-attestation.json",
                "sha256": config["host_attestation"]["sha256"],
                "config": mission["config"], "host": config["host"],
                "model_resolved_required": config["model_resolved_required"]}:
            raise ValueError("host attestation mission identity mismatch")
        path = root / binding["path"]
        if not path.is_file() or _sha256_file(path) != binding["sha256"]:
            raise ValueError("host attestation custody hash mismatch")
        retained = _read_object(path, "host attestation")
        contract.validate_host_attestation(retained)
        if retained["id"] != config["host_attestation"]["id"]:
            raise ValueError("host attestation retained identity mismatch")
        return retained

    def _claim_attempt(self, mission, packet_sha256, packet):
        name = self._attempt_name(mission)
        claiming = self.campaign_root / (name + ".claiming")
        final = self.campaign_root / name
        claiming.mkdir(exist_ok=False)
        attestation_raw, _ = self._load_host_attestation(mission, packet)
        with open(claiming / "host-attestation.json", "xb") as stream:
            stream.write(attestation_raw)
        config = packet["configurations"][mission["config"]]
        _write_new_json(claiming / "attempt-status.json", {
            "schema": "implementaudit-b3v4-attempt-status-v1",
            "campaign": "b3v4-sol-r1", "freeze_sha256": packet_sha256,
            "contract_sha256": contract.contract_sha256(),
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": self.execution_mode, "created_at": _utc_now(),
            "host_attestation_binding": {
                "path": "host-attestation.json",
                "sha256": config["host_attestation"]["sha256"],
                "config": mission["config"], "host": config["host"],
                "model_resolved_required": config["model_resolved_required"],
            },
        })
        os.rename(claiming, final)
        return final

    def _validate_identities(self, packet):
        self.identity_validator(
            packet, candidate_checkout=self.candidate_checkout,
            control_checkout=self.control_checkout)

    def _verify_frozen_binding(self, expected_sha):
        packet, raw, observed_sha = self._load_packet()
        if observed_sha != expected_sha:
            raise ValueError("frozen packet drift")
        self._ensure_campaign(raw, observed_sha)
        self._validate_identities(packet)

    def run_next(self):
        packet, raw, packet_sha256 = self._load_packet()
        fixture = _fixture_for_packet(self.repo_root, packet)
        self._ensure_campaign(raw, packet_sha256)
        self._validate_identities(packet)
        mission = self._next_mission(packet)
        attempt_root = self._claim_attempt(mission, packet_sha256, packet)
        status = _read_object(attempt_root / "attempt-status.json",
                              "attempt status")
        retained_attestation = self._verify_host_attestation(
            attempt_root, status, mission, packet)
        context = MissionContext(
            packet=packet, packet_sha256=packet_sha256, mission=mission,
            attempt_root=attempt_root,
            candidate_checkout=self.candidate_checkout,
            control_checkout=self.control_checkout,
            runtime_root=self.runtime_root, attestations=self.attestations,
            host_attestation=retained_attestation)
        terminal = {
            "schema": "implementaudit-b3v4-attempt-terminal-v1",
            "campaign": "b3v4-sol-r1", "mission_index": mission["index"],
            "execution_mode": self.execution_mode,
            "overall_status": None, "resolved_model": None,
            "host_run_root": None, "official_overall_status": None,
            "official_verdict_sha256": None, "stop_reason": None,
            "error_type": None, "completed_at": None,
        }
        try:
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
                if (official_status in CONTINUE_STATES and
                        official_verdict.get("model_resolved") !=
                        terminal["resolved_model"]):
                    terminal["overall_status"] = "INVALID"
                    terminal["stop_reason"] = "official-model-identity-disagrees"
            elif claimed_status in CONTINUE_STATES:
                terminal["overall_status"] = "ERROR"
                terminal["stop_reason"] = "official-verdict-missing"
            try:
                self._verify_frozen_binding(packet_sha256)
            except (OSError, ValueError, json.JSONDecodeError):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "frozen-input-drift"
            resolved = terminal.get("resolved_model")
            if (terminal.get("overall_status") in CONTINUE_STATES and
                    resolved != context.expected_model):
                terminal["overall_status"] = "INVALID"
                terminal["stop_reason"] = "model-substitution"
            elif (terminal.get("overall_status") == "INVALID" and
                  resolved is not None and resolved != context.expected_model):
                terminal["stop_reason"] = "model-substitution"
            if terminal.get("overall_status") not in CONTINUE_STATES | STOP_STATES:
                terminal["overall_status"] = "ERROR"
                terminal["stop_reason"] = "unsupported-executor-result"
            elif terminal["overall_status"] in STOP_STATES:
                if not terminal.get("stop_reason"):
                    terminal["stop_reason"] = "invalid-or-error-halts-campaign"
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
        contract.validate_artifact("attempt_terminal", terminal)
        _write_new_json(attempt_root / "attempt-terminal.json", terminal)
        return terminal

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
        if config_name == "L":
            home = runtime / "codex-home"
            home.mkdir()
            if self.codex_auth_source:
                shutil.copy2(self.codex_auth_source, home / "auth.json")
            adapter = hosts.CodexAdapter(
                requested_model=config["model_requested"],
                reasoning_effort=config["reasoning_effort"],
                codex_binary=executable, codex_home=str(home), **common)
        else:
            home = runtime / "claude-config"
            home.mkdir()
            adapter = hosts.ClaudeAdapter(
                requested_model=config["model_requested"],
                effort=config["reasoning_effort"], config_dir=str(home),
                resolved_expect=config["model_resolved_required"], **common)
            adapter.host_argv_template[0] = executable
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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("intent")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--campaign-root", required=True)
    parser.add_argument("--candidate-checkout", required=True)
    parser.add_argument("--control-checkout", required=True)
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--l-attestation", required=True)
    parser.add_argument("--o-attestation", required=True)
    parser.add_argument("--codex-auth-source")
    args = parser.parse_args(argv)
    driver = CampaignDriver(
        packet_path=args.intent, repo_root=args.repo_root,
        campaign_root=args.campaign_root,
        candidate_checkout=args.candidate_checkout,
        control_checkout=args.control_checkout, runtime_root=args.runtime_root,
        attestations={"L": args.l_attestation, "O": args.o_attestation},
        codex_auth_source=args.codex_auth_source)
    terminal = driver.run_next()
    print(json.dumps({"mission_index": terminal["mission_index"],
                      "overall_status": terminal["overall_status"],
                      "stop_reason": terminal.get("stop_reason")},
                     sort_keys=True))
    return 0 if terminal["overall_status"] in CONTINUE_STATES else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"B3V4-CAMPAIGN-REFUSED: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(2)
