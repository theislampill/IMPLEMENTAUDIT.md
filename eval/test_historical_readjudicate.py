#!/usr/bin/env python3
"""Deterministic append-only historical re-adjudication tests."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import tempfile

import historical_readjudicate as history


CELLS = [
    f"{fixture}-{config}"
    for fixture in (
        "B0", "B1", "B2", "E1", "E10", "E2a", "E2b",
        "E3", "E4", "E5", "E6", "E7", "E8", "E9")
    for config in ("L", "O")
]


def encoded(value):
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def build_inventory(base):
    rows = []
    for index in range(56):
        arm = "candidate" if index % 2 == 0 else "control"
        cell = CELLS[index // 2]
        fixture, config = cell.rsplit("-", 1)
        run_id = f"cmp-fable-r2-{index:03d}-{cell}-{arm}"
        run_root = base / "historical" / run_id
        bundle = run_root / "bundle"
        source = bundle / "verdict.json"
        fixture_path = bundle / "fixture.json"
        fixture_doc = {
            "id": fixture,
            "properties": [{
                "name": "governing_property", "required": True,
                "describes": "the governing historical property",
            }, {
                "name": "diagnostic_property", "required": False,
                "describes": "non-governing diagnostic evidence",
            }],
        }
        write(fixture_path, fixture_doc)
        write(source, {"status": "PASS" if index < 21 else "FAIL"})
        rows.append({
            "index": index,
            "campaign": "cmp-fable-r2",
            "arm": arm,
            "config": config,
            "fixture": fixture,
            "stable_cell_identity": f"{cell}-{arm}",
            "run_id": run_id,
            "paths": {
                "run_root": str(run_root),
                "canonical_raw_bundle": str(bundle),
                "sanitized_derivative": str(run_root / "bundle-sanitized"),
            },
            "retained_historical_verdict": {
                "status": "PASS" if index < 21 else "FAIL",
                "failed_invariant": None if index < 21 else "historical",
                "verdict_bundle_sha256": "a" * 64,
            },
            "key_file_hashes": {
                "bundle/fixture.json": {
                    "path": str(fixture_path), "sha256": sha(fixture_path),
                },
                "bundle/verdict.json": {
                    "path": str(source), "sha256": sha(source),
                },
            },
            "inventory_complete": True,
            "anomalies": [],
        })
    inventory = {
        "schema": "implementaudit-historical-bundle-inventory-v1",
        "campaign": {"id": "cmp-fable-r2", "mission_count": 56},
        "summary": {
            "expected_total": 56, "located_total": 56,
            "candidate_expected": 28, "candidate_located": 28,
            "control_expected": 28, "control_located": 28,
            "retained_candidate_passes": 11,
            "retained_candidate_total": 28,
            "retained_control_passes": 10,
            "retained_control_total": 28,
            "global_anomalies": [],
        },
        "preservation_boundary": {
            "historical_candidate_record": "11/28",
            "historical_control_record": "10/28",
            "canonical_bundle_rule": "raw bundle only",
        },
        "bundles": rows,
    }
    path = base / "inventory.json"
    write(path, inventory)
    return path, inventory


def decision(row, inventory_hash, evaluator_value, evaluator_hash,
             status="PASS"):
    original_hash = row["key_file_hashes"]["bundle/verdict.json"]["sha256"]
    return {
        "schema": "implementaudit-historical-corrected-decision-v2",
        "source": {
            "campaign": row["campaign"], "index": row["index"],
            "run_id": row["run_id"], "arm": row["arm"],
            "fixture": row["fixture"], "config": row["config"],
            "stable_cell_identity": row["stable_cell_identity"],
            "inventory_sha256": inventory_hash,
            "canonical_raw_bundle": row["paths"]["canonical_raw_bundle"],
            "original_verdict_sha256": original_hash,
        },
        "evaluator_binding": {
            "sha256": evaluator_hash,
            "name": evaluator_value["name"],
            "git_commit": evaluator_value["git_commit"],
            "git_tree": evaluator_value["git_tree"],
            "sources": evaluator_value["sources"],
        },
        "re_adjudicator_identity": history._implementation_identity(),
        "corrected_view": corrected_view(status),
        "causal_classification": {
            "primary": "no-proven-reclassification",
            "evidence": ["retained corrected decision"],
        },
        "uncertainty": {
            "statement": "historical evidence only",
            "disconfirmation_conditions": ["new source drift"],
        },
    }


def corrected_view(status):
    passed = status == "PASS"
    property_state = "PASS" if passed else "FAIL"
    findings = []
    failed_domain = None if passed else "product-property"
    failed_invariant = None if passed else "governing_property"
    properties = {
        "governing_property": {
            "state": property_state, "pass": passed,
            "evidence": "retained governing evidence",
            "describes": "the governing historical property",
            "basis": "append-only retained evidence",
        },
        "diagnostic_property": {
            "state": "PASS", "pass": True,
            "evidence": "retained diagnostic evidence",
            "describes": "non-governing diagnostic evidence",
            "basis": "append-only retained evidence",
        },
    }
    return {
        "schema": "implementaudit-historical-corrected-verdict-v2",
        "overall_status": status,
        "product_status": status,
        "host_status": "PASS",
        "model_substitution": False,
        "property_contract": [{
            "name": "governing_property", "required": True,
            "describes": "the governing historical property",
        }, {
            "name": "diagnostic_property", "required": False,
            "describes": "non-governing diagnostic evidence",
        }],
        "properties": properties,
        "host_safety": {
            "schema": "implementaudit-host-safety-v1",
            "status": "PASS", "failed_invariant": None,
            "failed_status": None, "findings": findings,
        },
        "adjudication": {
            "schema": "implementaudit-eval-adjudication-v1",
            "product_status": status, "host_status": "PASS",
            "overall_status": status,
            "property_evidence_complete": True,
            "all_required_properties_true": passed,
            "product_failed_invariant": failed_invariant,
            "host_failed_invariant": None,
            "host_failed_status": None,
            "failed_domain": failed_domain,
            "failed_invariant": failed_invariant,
        },
        "failed_domain": failed_domain,
        "failed_invariant": failed_invariant,
        "verdict_evidence": [
            "governing_property: retained governing evidence",
            "diagnostic_property: retained diagnostic evidence",
        ],
        "reason": None if passed else "required property failed",
    }


def evaluator():
    return history.expected_evaluator_manifest()


def main():
    # Governing round-2 RED: corrected decisions retain the full existing
    # verdict-v3 property/evidence layer; a four-status shortcut is invalid.
    expect_error(
        "verdict-v3",
        lambda: history.validate_corrected_verdict_v3({}, {}))

    with tempfile.TemporaryDirectory(prefix="historical-readjudicate-") as tmp:
        base = pathlib.Path(tmp)
        inventory_path, inventory = build_inventory(base)
        inventory_hash = sha(inventory_path)
        evaluator_path = base / "evaluator.json"
        evaluator_value = evaluator()
        write(evaluator_path, evaluator_value)
        evaluator_hash = sha(evaluator_path)
        records = base / "records"
        records.mkdir()
        for row in inventory["bundles"]:
            dpath = base / f"decision-{row['index']:02d}.json"
            write(dpath, decision(
                row, inventory_hash, evaluator_value, evaluator_hash))
            history.adjudicate_one(
                inventory_path, inventory_hash, row["index"],
                dpath, sha(dpath), evaluator_path, evaluator_hash,
                records / f"{row['index']:02d}.json")
        aggregate_path = base / "aggregate.json"
        aggregate = history.aggregate(
            inventory_path, inventory_hash, records, base,
            evaluator_path, evaluator_hash, aggregate_path)
        assert aggregate["historical_view"] == {
            "candidate": {"passes": 11, "total": 28},
            "control": {"passes": 10, "total": 28},
        }
        assert aggregate["corrected_view"]["candidate"]["PASS"] == 28
        assert aggregate["corrected_view"]["control"]["PASS"] == 28
        assert aggregate["coverage"]["record_count"] == 56
        assert aggregate["coverage"]["paired_cell_count"] == 28
        assert aggregate["property_coverage"] == {
            "declared_rows": 112,
            "required_rows": 56,
            "verdict_evidence_entries": 112,
            "declared_states": {
                "PASS": 112, "FAIL": 0, "INCOMPLETE": 0},
            "required_states": {
                "PASS": 56, "FAIL": 0, "INCOMPLETE": 0},
        }
        expect_error(
            "create-once",
            lambda: history.aggregate(
                inventory_path, inventory_hash, records, base,
                evaluator_path, evaluator_hash, aggregate_path))

        changed = copy.deepcopy(inventory)
        changed["bundles"][0]["paths"]["canonical_raw_bundle"] = \
            changed["bundles"][0]["paths"]["sanitized_derivative"]
        changed_path = base / "sanitized-inventory.json"
        write(changed_path, changed)
        changed_decision = decision(
            changed["bundles"][0], sha(changed_path),
            evaluator_value, evaluator_hash)
        changed_decision_path = base / "sanitized-decision.json"
        write(changed_decision_path, changed_decision)
        expect_error(
            "canonical raw bundle",
            lambda: history.adjudicate_one(
                changed_path, sha(changed_path), 0,
                changed_decision_path, sha(changed_decision_path),
                evaluator_path, evaluator_hash, base / "bad.json"))
        expect_error(
            "inventory SHA",
            lambda: history.adjudicate_one(
                inventory_path, "0" * 64, 0,
                base / "decision-00.json", sha(base / "decision-00.json"),
                evaluator_path, evaluator_hash, base / "bad2.json"))
        decision_zero = base / "decision-00.json"
        decision_zero_raw = decision_zero.read_bytes()
        changed_zero = json.loads(decision_zero_raw)
        changed_zero["uncertainty"]["statement"] = "post-record mutation"
        write(decision_zero, changed_zero)
        expect_error(
            "SHA mismatch",
            lambda: history.aggregate(
                inventory_path, inventory_hash, records, base,
                evaluator_path, evaluator_hash,
                base / "mutated-decision-aggregate.json"))
        decision_zero.write_bytes(decision_zero_raw)
        fixture_zero = pathlib.Path(
            inventory["bundles"][0]["key_file_hashes"][
                "bundle/fixture.json"]["path"])
        fixture_zero_raw = fixture_zero.read_bytes()
        fixture_zero.write_bytes(fixture_zero_raw + b" ")
        expect_error(
            "SHA mismatch",
            lambda: history.aggregate(
                inventory_path, inventory_hash, records, base,
                evaluator_path, evaluator_hash,
                base / "mutated-source-aggregate.json"))
        fixture_zero.write_bytes(fixture_zero_raw)
        (records / "55.json").unlink()
        expect_error(
            "56",
            lambda: history.aggregate(
                inventory_path, inventory_hash, records, base,
                evaluator_path, evaluator_hash, base / "incomplete.json"))
    print("HISTORICAL-READJUDICATE-PASS")


if __name__ == "__main__":
    main()
