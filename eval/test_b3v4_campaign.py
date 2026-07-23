#!/usr/bin/env python3
"""Deterministic tests for the serialized B3-v4 campaign driver."""
from __future__ import annotations

import importlib.util
import hashlib
import copy
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

from test_b3v4_freeze import valid_packet


HERE = pathlib.Path(__file__).resolve().parent
DRIVER = HERE / "b3v4_campaign.py"


def load_driver():
    spec = importlib.util.spec_from_file_location("b3v4campaign", DRIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_packet(root):
    path = pathlib.Path(root) / "intent.json"
    packet = valid_packet()
    packet["fixture"]["fixture_sha256"] = hashlib.sha256(
        (HERE / "fixtures" / "B3-v3" / "fixture.json").read_bytes()).hexdigest()
    path.write_text(json.dumps(packet, sort_keys=True), encoding="utf-8")
    return path


def append_duplicate_member(raw, name, value):
    end = raw.rfind("}")
    assert end >= 0
    return raw[:end] + f',"{name}":{json.dumps(value)}' + raw[end:]


def add_duplicate_to_file(path, name, value):
    path = pathlib.Path(path)
    path.write_text(append_duplicate_member(
        path.read_text(encoding="utf-8"), name, value), encoding="utf-8")


def make_driver(module, root, executor):
    packet = write_packet(root)
    attestations = {}
    for config, dialect, reader in (("L", "posix", "cat"),):
        path = pathlib.Path(root) / f"{config}-host-attestation.json"
        path.write_bytes((json.dumps({
            "id": f"b3v4-{config}-host", "shell_dialect": dialect,
            "executables": {reader: f"{dialect}:{reader}"},
        }, sort_keys=True, separators=(",", ":")) + "\n").encode())
        attestations[config] = path
    return module.CampaignDriver(
        packet_path=packet,
        repo_root=HERE.parent,
        campaign_root=pathlib.Path(root) / "campaign",
        candidate_checkout=pathlib.Path(root) / "candidate",
        control_checkout=pathlib.Path(root) / "control",
        runtime_root=pathlib.Path(root) / "runtime",
        attestations=attestations,
        mission_executor=executor,
        execution_mode="test",
        live_validator=lambda packet, repo: packet,
        identity_validator=lambda packet, **paths: None,
    )


FINAL_CLAIMS = {
    "final_12_of_12": False,
    "cross_model_qualified": False,
    "release_authorized": False,
    "tag_authorized": False,
    "publication_authorized": False,
}


def independent_result_for(driver, *, disagree_at=None):
    packet, _, freeze_sha = driver._load_packet()
    rows = []
    for mission in packet["missions"]:
        attempt = driver.campaign_root / driver._attempt_name(mission)
        terminal = json.loads((attempt / "attempt-terminal.json").read_text(
            encoding="utf-8"))
        rows.append({
            "index": mission["index"], "config": mission["config"],
            "arm": mission["arm"], "rep": mission["rep"],
            "overall_status": (
                "INVALID" if mission["index"] == disagree_at else "PASS"),
            "official_overall_status": terminal["official_overall_status"],
            "independent_overall_status": (
                "INVALID" if mission["index"] == disagree_at else "PASS"),
            "model_resolved": terminal["resolved_model"],
            "official_verdict_sha256": terminal["official_verdict_sha256"],
        })
    return {
        "schema": "implementaudit-b3v4-luna-independent-rederivation-v2",
        "campaign": packet["campaign"], "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "luna_stage_status": "PASS",
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True,
        "accepted": False, "mission_count": len(rows), "missions": rows,
        "claims": FINAL_CLAIMS,
    }


def write_independent_result(driver, *, disagree_at=None):
    path = driver.campaign_root / "b3v4-luna-independent-rederivation.json"
    path.write_bytes((json.dumps(
        independent_result_for(driver, disagree_at=disagree_at),
        sort_keys=True, separators=(",", ":")) + "\n").encode())
    return path


def expect_error(fragment, fn):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


def official_verdict(context, status="PASS", *, product="PASS", host="PASS",
                     resolved_model=None, substituted=False):
    fixture = json.loads((HERE / "fixtures" / "B3-v3" / "fixture.json").read_text(
        encoding="utf-8"))
    properties = {
        prop["name"]: {"state": "PASS", "pass": True,
                       "evidence": "synthetic retained evidence",
                       "describes": prop["describes"],
                       "basis": "host-observation"}
        for prop in fixture["properties"]
    }
    first_property = next(iter(properties))
    if product == "FAIL":
        properties[first_property]["state"] = "FAIL"
        properties[first_property]["pass"] = False
    elif product == "INCOMPLETE":
        properties[first_property]["state"] = "INCOMPLETE"
        properties[first_property]["pass"] = None
    host_gate = "model-substitution" if substituted else "synthetic-host-gate"
    findings = ([] if host == "PASS" else [{
        "gate": host_gate, "status": host,
        "evidence": ["synthetic retained host evidence"],
        "reason": "synthetic retained host reason"}])
    property_complete = product != "INCOMPLETE"
    all_true = True if product == "PASS" else False if product == "FAIL" else None
    product_failed = first_property if product == "FAIL" else None
    host_failed = findings[0] if findings else None
    if status in ("INVALID", "ERROR"):
        failed_domain = ("infrastructure" if status == "ERROR"
                         else "identity-custody-or-evidence")
        failed_invariant = host_gate if findings else "property-evidence-incomplete"
    elif product_failed:
        failed_domain, failed_invariant = "product-property", product_failed
    elif host_failed:
        failed_domain, failed_invariant = "host-safety", host_gate
    else:
        failed_domain = failed_invariant = None
    verdict = {
        "schema": "implementaudit-eval-verdict-v3", "status": status,
        "run_id": f"attempt-{context.mission['index']:03d}-synthetic",
        "fixture_id": "B3-v3", "fixture_sha256": "a" * 64,
        "prompt_sha256": "b" * 64, "events_sha256": "c" * 64,
        "product_tag": "v0.3.2.0", "product_commit": "d" * 40,
        "product_tree": "e" * 40, "installed_payload_sha256": "f" * 64,
        "harness_commit": "1" * 40, "adapter_name": "synthetic",
        "adapter_version": "test", "adapter_sha256": "2" * 64,
        "model_requested": resolved_model or context.expected_model,
        "model_resolved": resolved_model or context.expected_model,
        "model_substitution": substituted,
        "host": "synthetic", "started_at": "2030-01-01T00:00:00Z",
        "ended_at": "2030-01-01T00:00:01Z",
        "identity_attestation": {
            "verified_in_replay": [
                "fixture_sha256 (bytes + canonical-library authenticity)",
                "prompt_sha256 (bytes + mission consistency)",
                "events_sha256", "repo_before/after snapshot integrity",
                "artifact hashes via artifact-manifest"],
            "adapter_attested_only": [
                "product_tag/commit/tree", "installed_payload_sha256",
                "adapter_name/version/sha256", "host",
                "harness_commit (cross-checked when the scoring checkout is available)"],
        },
        "bundle_sha256": "3" * 64, "scorer_commit": "4" * 40,
        "properties": properties,
        "host_safety": {"schema": "implementaudit-host-safety-v1",
                        "status": host,
                        "failed_invariant": host_gate if findings else None,
                        "failed_status": host if findings else None,
                        "findings": findings},
        "adjudication": {
            "schema": "implementaudit-eval-adjudication-v1",
            "product_status": product, "host_status": host,
            "overall_status": status,
            "property_evidence_complete": property_complete,
            "all_required_properties_true": all_true,
            "product_failed_invariant": product_failed,
            "host_failed_invariant": host_gate if findings else None,
            "host_failed_status": host if findings else None,
            "failed_domain": failed_domain,
            "failed_invariant": failed_invariant,
        },
        "failed_domain": failed_domain, "failed_invariant": failed_invariant,
        "evidence": ["synthetic retained evidence"],
        "reason": "synthetic retained reason" if findings else None,
    }
    if substituted:
        verdict["model_substitution_note"] = "synthetic substitution"
    return verdict


def scored_outcome(context, status="PASS", *, resolved_model=None,
                   product="PASS", host="PASS", substituted=False):
    resolved = resolved_model or context.expected_model
    return {"overall_status": status, "resolved_model": resolved,
            "host_run_root": "mock-host-run",
            "official_verdict": official_verdict(
                context, status, product=product, host=host,
                resolved_model=resolved, substituted=substituted)}


def assert_runtime_executable_parent_junction_rejected(module):
    if os.name != "nt":
        print("RUNTIME_EXECUTABLE_PARENT_JUNCTION=SKIP:non-windows")
        return
    with tempfile.TemporaryDirectory(
            prefix="b3v4-runtime-executable-junction-") as tmp:
        root = pathlib.Path(tmp)
        target = root / "executable-target"
        target.mkdir()
        executable = target / "host.exe"
        executable.write_bytes(b"bounded local executable identity fixture\n")
        junction = root / "executable-junction"
        made = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
            capture_output=True, text=True)
        if made.returncode:
            print("RUNTIME_EXECUTABLE_PARENT_JUNCTION=SKIP:mklink")
            return

        packet = valid_packet()
        alias = junction / "host.exe"
        packet["configurations"]["L"]["executable"]["path"] = str(alias)
        packet["configurations"]["L"]["executable"]["sha256"] = \
            hashlib.sha256(executable.read_bytes()).hexdigest()
        candidate = root / "candidate"
        control = root / "control"
        candidate.mkdir()
        control.mkdir()
        original_git = module._git
        original_payload_hash = module.adapters.payload_hash
        original_run = module.subprocess.run

        def fake_git(checkout, *args):
            arm = pathlib.Path(checkout).name
            field = {"HEAD": "commit", "HEAD^{tree}": "tree",
                     "HEAD:skills/implementaudit": "skill_tree"}[args[-1]]
            return packet[arm][field]

        def fake_payload_hash(path):
            arm = "candidate" if "candidate" in pathlib.Path(path).parts \
                else "control"
            return packet[arm]["payload_sha256"]

        def forbid_version_execution(*args, **kwargs):
            raise AssertionError("parent-junction executable reached execution")

        module._git = fake_git
        module.adapters.payload_hash = fake_payload_hash
        module.subprocess.run = forbid_version_execution
        try:
            expect_error("link", lambda: module.validate_runtime_identities(
                packet, candidate_checkout=candidate,
                control_checkout=control))
        finally:
            module._git = original_git
            module.adapters.payload_hash = original_payload_hash
            module.subprocess.run = original_run
            os.rmdir(junction)
        print("RUNTIME_EXECUTABLE_PARENT_JUNCTION=PASS")


def main():
    module = load_driver()
    assert_runtime_executable_parent_junction_rejected(module)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-verdict-contract-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        packet, _, _ = driver._load_packet()
        context = type("Context", (), {
            "mission": packet["missions"][0],
            "expected_model": packet["configurations"]["L"][
                "model_resolved_required"],
        })()
        valid = official_verdict(context)
        cases = []
        missing_root = copy.deepcopy(valid)
        del missing_root["bundle_sha256"]
        cases.append(("missing root", missing_root))
        extra_root = copy.deepcopy(valid)
        extra_root["mutable_summary"] = "PASS"
        cases.append(("extra root", extra_root))
        numeric_complete = copy.deepcopy(valid)
        numeric_complete["adjudication"]["property_evidence_complete"] = 1
        cases.append(("numeric aggregate", numeric_complete))
        contradictory_aggregate = copy.deepcopy(valid)
        contradictory_aggregate["adjudication"][
            "all_required_properties_true"] = False
        cases.append(("contradictory aggregate", contradictory_aggregate))
        empty_evidence = copy.deepcopy(valid)
        first_name = next(iter(empty_evidence["properties"]))
        empty_evidence["properties"][first_name]["evidence"] = ""
        cases.append(("empty property evidence", empty_evidence))
        extra_property_field = copy.deepcopy(valid)
        extra_property_field["properties"][first_name]["summary"] = "PASS"
        cases.append(("extra property field", extra_property_field))
        contradictory_property = copy.deepcopy(valid)
        contradictory_property["properties"][first_name]["pass"] = False
        cases.append(("contradictory property", contradictory_property))
        contradictory_host = copy.deepcopy(valid)
        contradictory_host["host_safety"]["findings"] = [{
            "gate": "model-substitution", "status": "INVALID",
            "evidence": ["substituted"], "reason": "substituted"}]
        cases.append(("contradictory host", contradictory_host))
        missing_property = copy.deepcopy(valid)
        del missing_property["properties"][first_name]
        cases.append(("missing property", missing_property))
        fabricated_property = copy.deepcopy(valid)
        fabricated_property["properties"]["fabricated"] = copy.deepcopy(
            valid["properties"][first_name])
        cases.append(("fabricated property", fabricated_property))
        missing_adjudication_field = copy.deepcopy(valid)
        del missing_adjudication_field["adjudication"]["failed_domain"]
        cases.append(("missing adjudication field", missing_adjudication_field))
        extra_host_field = copy.deepcopy(valid)
        extra_host_field["host_safety"]["summary"] = "PASS"
        cases.append(("extra host field", extra_host_field))
        contradictory_product = copy.deepcopy(valid)
        contradictory_product["adjudication"]["product_status"] = "FAIL"
        cases.append(("contradictory product", contradictory_product))
        contradictory_overall = copy.deepcopy(valid)
        contradictory_overall["status"] = "FAIL"
        cases.append(("contradictory overall", contradictory_overall))
        for label, verdict in cases:
            try:
                module._validate_official_verdict(verdict)
            except ValueError as exc:
                assert "official scorer verdict" in str(exc), (label, str(exc))
            else:
                raise AssertionError(f"official scorer verdict accepted {label}")

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-duplicate-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        packet = pathlib.Path(tmp) / "intent.json"
        add_duplicate_to_file(packet, "seed", 20260718)
        expect_error("duplicate JSON key", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-custody-") as tmp:
        def contradictory_executor(context):
            verdict = official_verdict(
                context, "INVALID", product="INCOMPLETE", host="INVALID")
            return {"overall_status": "PASS",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run",
                    "official_verdict": verdict}

        driver = make_driver(module, tmp, contradictory_executor)
        result = driver.run_next()
        attempt = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        verdict_path = attempt / "official-verdict.json"
        assert result["official_overall_status"] == "INVALID", result
        assert result["overall_status"] == "INVALID", result
        assert verdict_path.is_file(), "official verdict custody missing"
        assert result["official_verdict_sha256"] == hashlib.sha256(
            verdict_path.read_bytes()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        expect_error("cannot replace", lambda: module.CampaignDriver(
            packet_path=write_packet(tmp), repo_root=HERE.parent,
            campaign_root=pathlib.Path(tmp) / "campaign",
            candidate_checkout=pathlib.Path(tmp) / "candidate",
            control_checkout=pathlib.Path(tmp) / "control",
            runtime_root=pathlib.Path(tmp) / "runtime",
            mission_executor=lambda context: {}))

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        observed = []

        def pass_once(context):
            status = context.attempt_root / "attempt-status.json"
            assert status.is_file(), "pre-spawn attempt status missing"
            observed.append((context.mission["index"], context.mission["config"],
                             context.mission["arm"], context.mission["rep"]))
            return scored_outcome(context)

        driver = make_driver(module, tmp, pass_once)
        first = driver.run_next()
        second = driver.run_next()
        assert first["mission_index"] == 0 and second["mission_index"] == 1
        assert observed == [(0, "L", "candidate", 1),
                            (1, "L", "control", 1)]
        first_root = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        retained = first_root / "host-attestation.json"
        status = json.loads((first_root / "attempt-status.json").read_text(
            encoding="utf-8"))
        assert retained.is_file(), "create-once host attestation custody missing"
        assert status["host_attestation_binding"] == {
            "path": "host-attestation.json",
            "sha256": hashlib.sha256(retained.read_bytes()).hexdigest(),
            "config": "L", "host": "WSL Ubuntu Codex CLI",
            "model_resolved_required": "gpt-5.6-luna",
        }
        assert json.loads((first_root / "attempt-terminal.json").read_text(
            encoding="utf-8"))["overall_status"] == "PASS"

        # A prior nonterminal attempt is preserved and blocks all progression.
        (pathlib.Path(tmp) / "campaign" /
         "attempt-001-L-control-r1" / "attempt-terminal.json").unlink()
        expect_error("prior attempt is nonterminal", driver.run_next)
        assert len(observed) == 2

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-extra-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        driver.run_next()
        attempt = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        (attempt / "mutable-summary.json").write_text("{}", encoding="utf-8")
        expect_error("unexpected attempt custody", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        def invalid_once(context):
            return {"overall_status": "INVALID",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run"}

        driver = make_driver(module, tmp, invalid_once)
        result = driver.run_next()
        assert result["overall_status"] == "INVALID"
        expect_error("prior attempt stopped campaign", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-drift-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        driver.run_next()
        first = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        verdict_path = first / "official-verdict.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        verdict["reason"] = "post-terminal drift"
        verdict_path.write_text(json.dumps(verdict), encoding="utf-8")
        expect_error("official verdict custody drift", driver.run_next)

    for label, mutate in (
            ("missing", lambda attempt, status: (attempt / "host-attestation.json").unlink()),
            ("extra", lambda attempt, status: (attempt / "host-attestation.json").write_text(
                '{"executables":{"cat":"posix:cat"},"id":"b3v4-L-host",'
                '"mutable_summary":"PASS","shell_dialect":"posix"}', encoding="utf-8")),
            ("malformed", lambda attempt, status: (attempt / "host-attestation.json").write_bytes(
                b'{"id":"b3v4-L-host","id":"substituted"}')),
            ("substituted", lambda attempt, status: (attempt / "host-attestation.json").write_text(
                '{"executables":{"get-content":"powershell:get-content"},'
                '"id":"b3v4-O-host","shell_dialect":"powershell"}', encoding="utf-8")),
            ("wrong-config", lambda attempt, status: status["host_attestation_binding"].update(config="O")),
            ("wrong-host", lambda attempt, status: status["host_attestation_binding"].update(host="Windows Claude CLI")),
            ("wrong-model", lambda attempt, status: status["host_attestation_binding"].update(
                model_resolved_required="claude-opus-4-8")),
            ("wrong-path", lambda attempt, status: status["host_attestation_binding"].update(
                path="alternate-attestation.json"))):
        with tempfile.TemporaryDirectory(prefix=f"b3v4-attestation-{label}-") as tmp:
            driver = make_driver(module, tmp, scored_outcome)
            driver.run_next()
            attempt = pathlib.Path(tmp) / "campaign" / "attempt-000-L-candidate-r1"
            status_path = attempt / "attempt-status.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            mutate(attempt, status)
            retained = attempt / "host-attestation.json"
            if retained.is_file():
                status["host_attestation_binding"]["sha256"] = hashlib.sha256(
                    retained.read_bytes()).hexdigest()
            status_path.write_text(json.dumps(status), encoding="utf-8")
            expect_error("host attestation", driver.run_next)

    retained_cases = (
        ("campaign-manifest.json", "campaign", "b3v4-sol-luna-r2"),
        ("attempt-status.json", "state", "PREPARED_BEFORE_HOST_SPAWN"),
        ("attempt-terminal.json", "overall_status", "PASS"),
    )
    for relative, key, value in retained_cases:
        with tempfile.TemporaryDirectory(
                prefix="b3v4-campaign-retained-duplicate-") as tmp:
            driver = make_driver(module, tmp, scored_outcome)
            driver.run_next()
            attempt = pathlib.Path(tmp) / "campaign" / \
                "attempt-000-L-candidate-r1"
            target = (pathlib.Path(tmp) / "campaign" / relative
                      if relative == "campaign-manifest.json"
                      else attempt / relative)
            add_duplicate_to_file(target, key, value)
            expect_error("duplicate JSON key", driver.run_next)

    # Retained bytes are not authoritative when another pathname aliases the
    # same inode.  Cover campaign-root and each attempt-root reader family.
    hardlink_cases = (
        ("campaign-manifest.json", "campaign manifest"),
        ("campaign-freeze.json", "frozen packet"),
        ("attempt-status.json", "attempt status"),
        ("attempt-terminal.json", "attempt terminal"),
        ("host-attestation.json", "host attestation"),
        ("official-verdict.json", "official verdict"),
    )
    for relative, owner in hardlink_cases:
        with tempfile.TemporaryDirectory(
                prefix=f"b3v4-campaign-hardlink-{relative.split('.')[0]}-") as tmp:
            driver = make_driver(module, tmp, scored_outcome)
            driver.run_next()
            campaign = pathlib.Path(tmp) / "campaign"
            attempt = campaign / "attempt-000-L-candidate-r1"
            target = campaign / relative if relative.startswith("campaign-") \
                else attempt / relative
            alias = pathlib.Path(tmp) / (relative + ".outside-alias")
            os.link(target, alias)
            expect_error("hardlink", driver.run_next)
            assert target.stat().st_nlink == 2, owner

    with tempfile.TemporaryDirectory(
            prefix="b3v4-campaign-verdict-duplicate-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        first = driver.run_next()
        attempt = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        verdict_path = attempt / "official-verdict.json"
        raw = verdict_path.read_text(encoding="utf-8")
        raw = raw.replace(
            '"overall_status": "PASS",',
            '"overall_status": "PASS", "overall_status": "PASS",', 1)
        verdict_path.write_text(raw, encoding="utf-8")
        terminal_path = attempt / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["official_verdict_sha256"] = hashlib.sha256(
            verdict_path.read_bytes()).hexdigest()
        terminal_path.write_text(json.dumps(terminal), encoding="utf-8")
        assert first["overall_status"] == "PASS"
        expect_error("duplicate JSON key", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        order = []

        def collect_order(context):
            order.append((context.mission["config"], context.mission["arm"],
                          context.mission["rep"]))
            return scored_outcome(context)

        driver = make_driver(module, tmp, collect_order)
        for _ in range(6):
            driver.run_next()
        assert order == [tuple(row) for row in module.freeze.PLAN]
        attempts_before = sorted(driver.campaign_root.glob("attempt-*"))
        expect_error("all six Luna attempts", driver.run_next)
        assert sorted(driver.campaign_root.glob("attempt-*")) == attempts_before
        assert not (driver.campaign_root / "b3v4-luna-result.json").exists()
        assert not (driver.campaign_root / "luna-stage-terminal.json").exists()

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-finalize-early-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        for _ in range(5):
            driver.run_next()
        expect_error("exact declared prefix", driver.finalize_luna_stage)
        assert not (driver.campaign_root / "b3v4-luna-result.json").exists()

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-finalize-") as tmp:
        def pass_with_host_custody(context):
            retained = context.attempt_root / "host-custody" / "retained"
            retained.mkdir(parents=True)
            (retained / "evidence.bin").write_bytes(
                f"mission-{context.mission['index']}\n".encode())
            return scored_outcome(context)

        driver = make_driver(module, tmp, pass_with_host_custody)
        for _ in range(6):
            driver.run_next()
        independent_path = write_independent_result(driver)
        result = driver.finalize_luna_stage()
        assert result["schema"] == "implementaudit-b3v4-luna-result-v2"
        assert result["disposition"] == "INCOMPLETE_PENDING_OPUS"
        assert result["luna_stage_accepted"] is True
        assert result["accepted"] is False
        assert result["mission_count"] == 6
        assert result["claims"] == FINAL_CLAIMS
        assert independent_path.is_file()
        assert (driver.campaign_root / "b3v4-luna-result.json").is_file()
        assert (driver.campaign_root / "luna-stage-terminal.json").is_file()
        driver.validate_luna_stage()
        expect_error("already exists", driver.finalize_luna_stage)
        first = driver.campaign_root / "attempt-000-L-candidate-r1"
        (first / "host-custody" / "retained" / "evidence.bin").write_bytes(
            b"post-terminal mutation\n")
        expect_error("snapshot", driver.validate_luna_stage)

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-disagreement-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        for _ in range(6):
            driver.run_next()
        write_independent_result(driver, disagree_at=2)
        expect_error("disagree", driver.finalize_luna_stage)
        assert not (driver.campaign_root / "b3v4-luna-result.json").exists()
        assert not (driver.campaign_root / "luna-stage-terminal.json").exists()

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-claiming-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        for _ in range(6):
            driver.run_next()
        write_independent_result(driver)
        (driver.campaign_root / "attempt-005-L-candidate-r3.claiming").mkdir()
        expect_error("claim", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-gap-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        for _ in range(6):
            driver.run_next()
        write_independent_result(driver)
        shutil.rmtree(driver.campaign_root / "attempt-003-L-candidate-r2")
        expect_error("gap", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-seventh-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        for _ in range(6):
            driver.run_next()
        write_independent_result(driver)
        (driver.campaign_root / "attempt-006-L-candidate-r4").mkdir()
        expect_error("unexpected", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory(prefix="b3v4-luna-fail-stop-") as tmp:
        driver = make_driver(
            module, tmp,
            lambda context: scored_outcome(
                context, "FAIL", product="FAIL", host="PASS"))
        terminal = driver.run_next()
        assert terminal["overall_status"] == "FAIL"
        assert terminal["stop_reason"] == "failed-mission-halts-campaign"
        expect_error("stopped campaign", driver.run_next)
        expect_error("stopped prefix", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        def substitute(context):
            return scored_outcome(
                context, "INVALID", resolved_model="substituted-model",
                product="PASS", host="INVALID", substituted=True)

        driver = make_driver(module, tmp, substitute)
        result = driver.run_next()
        assert result["overall_status"] == "INVALID"
        assert result["stop_reason"] == "model-substitution"

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        driver = make_driver(module, tmp, lambda context: {
            "overall_status": "ERROR", "resolved_model": None,
            "host_run_root": "mock-host-run"})
        result = driver.run_next()
        assert result["overall_status"] == "ERROR"
        assert result["stop_reason"] == "invalid-or-error-halts-campaign"

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        driver = make_driver(
            module, tmp, scored_outcome)
        driver.run_next()
        packet = pathlib.Path(tmp) / "intent.json"
        changed = json.loads(packet.read_text(encoding="utf-8"))
        changed["acceptance_rule"] += " (drift)"
        packet.write_text(json.dumps(changed), encoding="utf-8")
        expect_error("frozen packet drift", driver.run_next)

    print("test_b3v4_campaign: ok")


if __name__ == "__main__":
    main()
