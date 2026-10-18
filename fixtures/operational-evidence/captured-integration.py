"""Constructed established owner formats through the actual R0038 public consumer.

These controls do not run a producer, authenticate a host event, or satisfy a
native obligation. The independent decoder banks retain their original oracles.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
HERE = Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts/operational-evidence.py"
POLICY = SCRIPT.with_name("operational_query_policy.py")


def load(path, name, arguments=()):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    with patch.object(sys, "argv", [str(path), *arguments]):
        spec.loader.exec_module(module)
    return module


oe = load(SCRIPT, "captured_integration_oe")
routes = load(HERE / "captured-routes.py", "route_data", ["--consumer", str(POLICY)])
occurrences = load(HERE / "captured-occurrences.py", "occurrence_data", ["--target", str(POLICY)])


def sources():
    facts, projection = occurrences.fixtures.coverage_case()
    return {
        "pending": routes.pending(two=True),
        "pending-decision": routes.decision(routes.pending(two=True)),
        "route": routes.route("RETURNED"),
        "route-result": routes.child_result(returned=True),
        "host-binding": routes.binding(),
        "result-occurrence": occurrences.candidate(),
        "member-coverage": {"facts": facts, "projection": projection},
        "child-visibility": occurrences.stage_evidence(),
    }


class CapturedIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def capture(self, kind, source):
        path = self.directory / (kind + ".json")
        raw = json.dumps(source, indent=2, ensure_ascii=False).encode("utf-8")
        path.write_bytes(raw)
        captured = oe.observe_captured_snapshot_v1(kind, path)
        self.assertEqual(captured["collections"]["captured_owner"]["input_text"].encode("utf-8"), raw)
        self.assertEqual(captured["input_manifest"]["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(captured["input_manifest"]["compiler_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
        return captured

    def rows(self, captured, record_type=None):
        rows = [r["record"] for family in oe.FAMILIES for r in oe.query_family(captured, family)["rows"]]
        return rows if record_type is None else [r for r in rows if r["record_type"] == record_type]

    def test_every_established_kind_uses_primary_projection_and_authority_floor(self):
        for kind, source in sources().items():
            with self.subTest(kind=kind):
                captured = self.capture(kind, source)
                rows = self.rows(captured)
                self.assertTrue(rows)
                self.assertEqual(captured["families"], list(oe.FAMILIES))
                self.assertEqual(captured["aggregate"], "DEGRADED")
                self.assertEqual({r["currentness"]["state"] for r in rows}, {"UNVERIFIED"})
                self.assertTrue(all(r["establishes"] == [] and r["source_identity"]["format_sources"] for r in rows))
                self.assertEqual({r["family"] for r in captured["missing_or_omitted_state"] if r["kind"] == "CAPTURE_SCOPE"}, set(oe.FAMILIES))
                for family in oe.FAMILIES:
                    self.assertEqual(oe.query_family(captured, family, True)["rows"], [])

    def test_no_epoch_two_boundaries_and_logical_join_remain_visible(self):
        pending = routes.pending(two=True)
        proposal = routes.assignment(pending)
        captured = self.capture("pending", pending)
        rows = self.rows(captured, "PendingCompaction")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["observation"]["pending"] for r in rows))
        self.assertEqual(self.rows(captured, "LogicalJoinProposal")[0]["observation"], proposal)
        self.assertFalse(proposal["pending_consumed"])
        first = next(iter(pending["observations"].values()))
        first["consumed_version"] = first["version"]
        after = self.capture("pending", pending)
        observed = self.rows(after, "PendingCompaction")
        self.assertEqual(sum(r["observation"]["pending"] for r in observed), 1)
        self.assertEqual({r["id"] for r in rows}, {r["id"] for r in observed})
        self.assertGreater(oe.diff_snapshots(captured, after)["counts"]["changed"], 0)
        self.assertTrue(oe.explain_history_why_v1(captured, rows[0]["id"]))

    def test_physical_identity_coverage_and_group_populations_survive_queries(self):
        candidate = occurrences.candidate()
        captured = self.capture("result-occurrence", candidate)
        rows = self.rows(captured)
        self.assertTrue(any(r["observation"] == candidate for r in rows))
        self.assertTrue(self.rows(captured, "SourceOccurrence"))
        self.assertTrue(self.rows(captured, "Artifact"))
        graph = {"schema": "implementaudit.work-graph.v1", "population": {"total_cells": 3},
                 "cells": [{"id": "source", "state": "DONE", "deps": []},
                           {"id": "test", "state": "READY", "deps": ["source"]},
                           {"id": "future", "state": "BLOCKED", "deps": ["test"]}],
                 "serialization_groups": {"W_owner": ["source", "test"], "R_resource": ["future"]}}
        graph_snapshot = self.capture("member-coverage", graph)
        self.assertEqual(len(self.rows(graph_snapshot, "Group")), 2)
        self.assertEqual(sum(r.get("relation_type") == "DEPENDS_ON" for r in self.rows(graph_snapshot)), 2)
        facts, projection = occurrences.fixtures.coverage_case()
        coverage = self.capture("member-coverage", {"facts": facts, "projection": projection})
        edges = self.rows(coverage, "CoverageEdge")
        self.assertEqual({r["observation"]["id"] for r in edges}, {r["id"] for r in facts["edges"]})
        blocked = next(r["observation"] for r in edges if r["observation"]["id"] == "native-recovery")
        self.assertEqual(blocked["gates"]["native_currentness"], "MISSING")

    def test_full_route_return_and_stages_are_not_receiving_or_join(self):
        route = routes.with_execution(routes.route("RETURNED"))
        captured = self.capture("route", route)
        self.assertEqual(self.rows(captured, "RouteObligation")[0]["observation"],
                         {k: v for k, v in route.items() if k != "lifecycle"})
        self.assertEqual(self.rows(captured, "RouteLifecycle")[0]["observation"], route["lifecycle"])
        self.assertEqual(len(self.rows(captured, "HostStageReceipt")), 3)
        self.assertEqual(len(self.rows(captured, "ChildReturn")), 1)
        self.assertEqual(self.rows(captured, "GovernorRouteDecision"), [])
        self.assertTrue(all(r["establishes"] == [] for r in self.rows(captured)))
        stages = self.capture("child-visibility", occurrences.stage_evidence())
        self.assertEqual({r["observation"]["stage"] for r in self.rows(stages, "LifecycleEvent")}, {"LOAD", "USE", "DISPOSE"})
        self.assertIn("ACCEPTANCE_JOIN_PARENT_COMPLETION_NOT_ESTABLISHED", {r["code"] for r in stages["missing_or_omitted_state"]})

    def test_known_structural_mismatches_are_typed_at_primary_boundary(self):
        route = routes.route("RETURNED")
        route["lifecycle"]["child_return"]["bytes_b64"] = "bm90IHRoZSByZXR1cm4="
        routes.reseal(route)
        candidate = occurrences.candidate()
        candidate["O_U_exchange_USE_R_A_identities"]["R"]["bound_exchange"] = copy.deepcopy(candidate["O_U_exchange_USE_R_A_identities"]["USE"])
        facts, projection = occurrences.fixtures.coverage_case()
        projection["ancestors"] = [facts["subject"]]
        for kind, value in (("route", route), ("result-occurrence", candidate),
                            ("member-coverage", {"facts": facts, "projection": projection})):
            with self.subTest(kind=kind):
                with self.assertRaises(oe.OperationalEvidenceError) as caught:
                    self.capture(kind, value)
                self.assertEqual(caught.exception.code, "OE_CAPTURE_INVALID")

    def test_frozen_queries_diff_why_and_render_have_zero_input_or_native_io(self):
        snapshots = [self.capture(kind, value) for kind, value in sources().items()]
        with patch.object(oe, "_read_repository_path", side_effect=AssertionError("input read")), \
                patch.object(oe, "collect_native_current", side_effect=AssertionError("native")), \
                patch.object(os, "open", side_effect=AssertionError("filesystem")), \
                patch("builtins.open", side_effect=AssertionError("filesystem")), \
                patch.object(subprocess, "run", side_effect=AssertionError("subprocess")), \
                patch.object(socket, "socket", side_effect=AssertionError("network")):
            for captured in snapshots:
                rows = self.rows(captured)
                self.assertEqual(oe.diff_snapshots(captured, captured)["counts"], {"added": 0, "removed": 0, "changed": 0})
                self.assertTrue(oe.explain_history_why_v1(captured, rows[0]["id"]))
                for mode in ("table", "graph"):
                    self.assertTrue(oe.render_snapshot_projection_v1(captured, output_format=mode, max_rows=100, max_bytes=262144))

    def test_explicit_cli_pending_and_physical_capture_inspect_roundtrip(self):
        for kind in ("pending", "result-occurrence"):
            with self.subTest(kind=kind):
                value = sources()[kind]
                source = self.directory / (kind + "-cli-input.json")
                source.write_text(json.dumps(value), encoding="utf-8")
                completed = subprocess.run([sys.executable, "-B", str(SCRIPT), "capture", kind, str(source)], capture_output=True)
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                output = self.directory / (kind + "-cli-snapshot.json")
                output.write_bytes(completed.stdout)
                inspected = subprocess.run([sys.executable, "-B", str(SCRIPT), "inspect", str(output), "--family", "EXECUTION",
                                            "--max-rows", "100", "--max-bytes", "262144"], capture_output=True)
                self.assertEqual(inspected.returncode, 0, inspected.stderr.decode())
                result = json.loads(inspected.stdout)
                self.assertEqual(result["acquisition_scope"], "CAPTURED_OWNER_UNAUTHENTICATED_FILE")
                self.assertTrue(all(r["record"]["currentness"]["state"] == "UNVERIFIED" for r in result["rows"]))


if __name__ == "__main__":
    unittest.main()
