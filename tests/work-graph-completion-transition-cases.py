"""Completion-aware ancestry over live portable records; no native acceptance."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("completion_case_support", REPO / "tests/work-graph-completion-cases.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


class TransitionCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.CompletionCases.setUpClass()

    def setUp(self):
        self.case = support.CompletionCases()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.c = self.case.consumer
        self.run = self.case.run

    def accept(self, name, consumer="JOIN", status="PASS", output=None):
        view = self.c.transition()
        self.assertIn(name, view["selected"])
        result = self.case.result(view, name, status=status, output=output)
        event = self.c.accept(view, [result], consumer, expected_old=self.c.history_digest)
        return view, result, event

    def complete_join(self):
        self.accept("A")
        self.accept("B")
        return self.c.join("JOIN", expected_old=self.c.history_digest)

    def complete_all(self):
        self.complete_join()
        self.accept("NEXT", "FINAL")
        self.c.join("FINAL", expected_old=self.c.history_digest)

    def nested(self, *, active=False, conflict=False):
        nodes = self.case.nodes
        nodes.append(support.node("INNER", kind="PLAN", requires=["JOIN"]))
        for row in nodes:
            if row["id"] in {"A", "B", "JOIN"}:
                row["parent"] = "INNER"
            if row["id"] == "NEXT":
                row["effect"] = "PREPARATION"
            if row["id"] == "FINAL":
                row["requires"].append("SIB")
        nodes.append(support.node("SIB", reads=["path:inputs/sib"],
                                  future_consumer=dict(node="FINAL", condition="retained sibling output")))
        nodes.append(support.node("ADMIT", parent="INNER", requires=["JOIN"],
                                  effect="MUTATION", authorization="MISSING",
                                  authority=["scope:admission"]))
        if active:
            nodes.append(support.node("ACTIVE", state="ACTIVE", resource_demand=1,
                                      writes=["path:inputs/next"] if conflict else []))
        self.case.state["nodes"] = [n["id"] for n in nodes]
        self.case.state["context"]["host_capacity"] = 3 if active else 2
        self.case.write_source()
        (self.run / "inputs/sib").write_text("independent sibling\n")

    def test_actual_join_selects_successor_and_preserves_native_entry(self):
        joined = self.complete_join()
        view = self.c.transition()
        frontier = self.c.frontier()
        self.assertEqual(view["selected"], ["NEXT"])
        for key in ("dispatch_id", "graph_digest", "source_graph_digest", "inputs", "states"):
            self.assertEqual(view[key], frontier[key])
        with self.c._graph() as graph:
            native = self.c.wg.compile_recursive_transition_v1(graph, [])
        self.assertEqual(native["selected"], ["A"])
        self.assertEqual([e["kind"] for e in view["completion_events"]], ["BATCH", "BATCH", "JOIN"])
        self.assertEqual(view["retained_ancestry"]["JOIN"], ["JOIN", "ROOT"])
        record = view["completion_events"][-1]["records"][0]
        self.assertEqual(record["node"], "JOIN")
        self.assertEqual(record["digest"], joined["completion_digest"])
        self.assertEqual(record["scope"], ["JOIN"])
        self.assertEqual(view["consumers"]["NEXT"]["node"], "FINAL")
        self.assertNotEqual(view["states"]["ROOT"], "DONE")
        self.assertEqual(view["authority"], "NONE")
        self.assertFalse(view["native_dispatch_authorized"])
        self.assertFalse(view["native_campaign_proven"])

    def test_nested_join_exposes_real_prep_and_sibling_while_effect_stays_held(self):
        self.nested()
        self.complete_join()
        view = self.c.transition()
        self.assertEqual(set(view["selected"]), {"NEXT", "SIB"})
        self.assertEqual(view["retained_ancestry"]["JOIN"], ["JOIN", "INNER", "ROOT"])
        self.assertEqual(view["retained_ancestry"]["A"], ["A", "INNER", "ROOT"])
        self.assertIn("SIB", view["directions"]["OUTWARD"])
        self.assertIn("NEXT", view["directions"]["FORWARD"])
        self.assertIn("JOIN", view["directions"]["BACKWARD"])
        self.assertEqual(view["states"]["ADMIT"], "BLOCKED")
        self.assertIn("EFFECT_EXECUTOR_UNAVAILABLE", view["blocked"]["ADMIT"])
        before = view["history_digest"]
        # Actual preparation and an independent actual child return. The fixed
        # portable consumer checks the prepared bytes before accepting them;
        # this is source-contract evidence, not a native child selection.
        input_bytes = (self.run / "inputs/a").read_bytes() + (self.run / "inputs/b").read_bytes()
        prepared = subprocess.run([sys.executable, "-I", "-S", "-B", "-c",
                                   "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read().upper())"],
                                  input=input_bytes, capture_output=True, check=True).stdout
        self.assertEqual(prepared, input_bytes.upper())
        result = self.case.result(view, "NEXT", output=prepared)
        self.c.accept(view, [result], "FINAL", expected_old=self.c.history_digest)
        self.accept("SIB", "FINAL")
        final = self.c.join("FINAL", expected_old=self.c.history_digest)
        self.assertEqual(final["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        after = self.c.transition()
        self.assertNotEqual(before, after["history_digest"])
        self.assertEqual(after["selected"], [])
        self.assertEqual(after["states"]["ADMIT"], "BLOCKED")
        self.assertNotEqual(after["states"]["ROOT"], "DONE")
        self.assertNotEqual(after["states"]["INNER"], "DONE")

    def test_each_material_scope_gets_its_own_recursive_directions(self):
        self.nested()
        self.case.nodes.append(support.node("OTHER", kind="PLAN"))
        next(n for n in self.case.nodes if n["id"] == "B")["parent"] = "OTHER"
        self.case.nodes.append(support.node("B_CHILD", parent="B", authorization="MISSING"))
        self.case.state["nodes"] = [n["id"] for n in self.case.nodes]
        self.case.write_source()
        self.complete_join()
        view = self.c.transition()
        self.assertEqual(view["ancestors"], ["A", "INNER", "ROOT"])
        self.assertEqual(view["retained_ancestry"]["B"], ["B", "OTHER", "ROOT"])
        self.assertEqual(view["retained_directions"]["B"]["INWARD"], ["B_CHILD"])
        self.assertEqual(view["directions"]["INWARD"], [])
        self.assertEqual(view["states"]["B_CHILD"], "BLOCKED")
        self.assertNotEqual(view["states"]["OTHER"], "DONE")

    def test_changed_input_invalidates_only_affected_live_scopes(self):
        self.nested()
        self.complete_join()
        self.accept("SIB", "FINAL")
        before = self.c.transition()
        history = before["history_digest"]
        (self.run / "inputs/a").write_text("material change\n")
        view = self.c.transition()
        self.assertEqual(view["history_digest"], history)
        self.assertEqual(view["selected"], ["A"])
        self.assertTrue({"A", "JOIN"}.issubset(view["invalidated"]))
        self.assertEqual(view["states"]["B"], "DONE")
        self.assertEqual(view["states"]["SIB"], "DONE")
        self.assertEqual(set(view["retained_ancestry"]), {"B", "SIB"})
        self.assertEqual({r["node"] for e in view["completion_events"] for r in e["records"]}, {"B", "SIB"})
        self.assertEqual(view["states"]["NEXT"], "BLOCKED")

    def test_partial_batch_invalidation_retains_original_and_current_scopes(self):
        self.case.state["context"]["host_capacity"] = 2
        self.case.write_source()
        view = self.c.transition()
        self.assertEqual(view["selected"], ["A", "B"])
        results = [self.case.result(view, name) for name in ("A", "B")]
        self.c.accept(view, results, "JOIN", expected_old=self.c.history_digest)
        (self.run / "inputs/a").write_text("changed first contributor only\n")
        view = self.c.transition()
        self.assertEqual(len(view["completion_events"]), 1)
        event = view["completion_events"][0]
        self.assertEqual(event["original_scope"], ["A", "B"])
        self.assertEqual(event["retained_scope"], ["B"])
        self.assertEqual([r["node"] for r in event["records"]], ["B"])
        self.assertEqual(view["states"]["A"], "READY")
        self.assertEqual(view["states"]["B"], "DONE")
        self.assertEqual(view["states"]["JOIN"], "BLOCKED")

    def test_changed_acceptance_premise_preserves_disjoint_result(self):
        self.complete_join()
        self.case.nodes[1]["authorization"] = "MISSING"
        self.case.write_source()
        view = self.c.transition()
        self.assertEqual(view["states"]["A"], "BLOCKED")
        self.assertEqual(view["states"]["B"], "DONE")
        self.assertEqual(view["states"]["JOIN"], "BLOCKED")
        self.assertEqual(set(view["retained_ancestry"]), {"B"})
        self.assertIn("AUTHORIZATION", view["blocked"]["A"])

    def test_active_occupancy_and_shared_writer_hold_preserve_independent_work(self):
        self.nested(active=True, conflict=True)
        self.complete_join()
        view = self.c.transition()
        self.assertEqual(view["states"]["ACTIVE"], "ACTIVE")
        self.assertEqual(view["active_occupancy"], 1)
        self.assertEqual(view["free_capacity"], 2)
        self.assertEqual(view["selected"], ["SIB"])
        self.assertEqual(view["deferred"]["NEXT"], "CONFLICT")
        self.assertEqual(view["states"]["ADMIT"], "BLOCKED")

    def test_capacity_and_context_cost_are_not_overridden(self):
        self.nested(active=True)
        self.complete_join()
        self.case.state["context"]["host_capacity"] = 1
        self.case.write_source()
        view = self.c.transition()
        self.assertEqual(view["selected"], [])
        self.assertEqual(view["active_occupancy"], 1)
        self.assertEqual(view["free_capacity"], 0)
        self.assertEqual(view["deferred"]["NEXT"], "CAPACITY")
        self.case.state["context"]["host_capacity"] = 3
        next(n for n in self.case.nodes if n["id"] == "NEXT")["context"]["useful_value"] = 0
        self.case.write_source()
        view = self.c.transition()
        self.assertEqual(view["deferred"]["NEXT"], "CONTEXT_COST")
        self.assertIn("SIB", view["selected"])

    def test_exact_transition_object_is_accepted_and_copy_or_reseal_refuses(self):
        view = self.c.transition()
        result = self.case.result(view, "A")
        with self.assertRaisesRegex(self.case.owner.CompletionError, "issued"):
            self.c.accept(copy.deepcopy(view), [result], "JOIN", expected_old=self.c.history_digest)
        view["ancestors"] = ["A"]
        body = {k: v for k, v in view.items() if k != "digest"}
        view["digest"] = self.c.wg._graph_hash(body)
        with self.assertRaisesRegex(self.case.owner.CompletionError, "modified"):
            self.c.accept(view, [result], "JOIN", expected_old=self.c.history_digest)
        self.accept("A")
        self.assertEqual(self.c.transition()["states"]["A"], "DONE")

    def test_source_change_after_transition_refuses_old_result(self):
        view = self.c.transition()
        result = self.case.result(view, "A")
        (self.run / "inputs/a").write_text("changed after dispatch\n")
        with self.assertRaisesRegex(self.case.owner.CompletionError, "stale"):
            self.c.accept(view, [result], "JOIN", expected_old=self.c.history_digest)
        self.assertEqual(self.c.transition()["completion_events"], [])

    def test_projection_only_does_not_record_execution_or_consumption(self):
        old = self.c.history_digest
        first, second = self.c.transition(), self.c.transition()
        self.assertEqual(first["selected"], ["A"])
        self.assertEqual(first, second)
        self.assertEqual(second["completion_events"], [])
        self.assertEqual(second["retained_ancestry"], {})
        self.assertEqual(self.c.history_digest, old)
        self.assertEqual(second["states"]["A"], "READY")

    def test_no_supplied_event_history_completion_or_projection(self):
        for args, kwargs in [(([{}],), {}), ((), {"history": []}), ((), {"event": {}}),
                             ((), {"outcomes": {"ROOT": "PASS"}})]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(TypeError):
                    self.c.transition(*args, **kwargs)

    def test_reopened_journal_gives_no_live_event_or_ancestor_credit(self):
        self.accept("A")
        self.c.close()
        self.c = self.case.owner.CompletionContract(self.run, self.case.root / "journal")
        self.addCleanup(self.c.close)
        view = self.c.transition()
        self.assertEqual(view["completion_events"], [])
        self.assertEqual(view["retained_ancestry"], {})
        self.assertEqual(view["states"]["A"], "BLOCKED")
        self.assertIn("COMPLETION_RECOVERY_CUSTODY_UNVERIFIED", view["blocked"]["A"])
        self.assertEqual(view["selected"], ["B"])
        self.assertNotEqual(view["states"]["ROOT"], "DONE")

    def test_reminder_reuses_scopes_without_event_or_dispatch_credit(self):
        self.complete_all()
        before = self.c.transition()
        self.case.state["event"] = dict(id="reminder-2", kind="REMINDER", subject="JOIN")
        self.case.write_source()
        view = self.c.transition()
        self.assertEqual(view["selected"], [])
        self.assertEqual(view["history_digest"], before["history_digest"])
        self.assertEqual(view["completion_events"], before["completion_events"])
        self.assertEqual(view["ancestors"], ["JOIN", "ROOT"])
        self.assertEqual(view["event"]["kind"], "REMINDER")
        self.assertEqual(view["states"]["FINAL"], "DONE")
        self.assertNotEqual(view["states"]["ROOT"], "DONE")

    def test_changed_original_scope_discards_all_prior_completion_use(self):
        self.complete_join()
        view = self.c.transition()
        result = self.case.result(view, "NEXT")
        self.case.state["original_scope"] = "different original scope"
        self.case.write_source()
        with self.assertRaisesRegex(self.case.owner.CompletionError, "campaign scope"):
            self.c.accept(view, [result], "FINAL", expected_old=self.c.history_digest)
        current = self.c.transition()
        self.assertEqual(current["completion_events"], [])
        self.assertEqual(current["retained_ancestry"], {})
        self.assertEqual(current["selected"], ["A"])

    def test_missing_campaign_root_refuses_fresh_transition(self):
        self.complete_join()
        self.case.state["root"] = "FOREIGN"
        self.case.write_source()
        with self.assertRaisesRegex(self.case.owner.CompletionError, "root"):
            self.c.transition()

    def test_failure_return_is_retained_without_join_or_whole_scope_credit(self):
        self.accept("A", status="FAIL", output=b"declared failure-contract evidence")
        self.accept("B")
        verdict = self.c.join("JOIN", expected_old=self.c.history_digest)
        view = self.c.transition()
        self.assertEqual(verdict["status"], "FAIL")
        self.assertEqual(view["states"]["JOIN"], "BLOCKED")
        self.assertEqual(view["states"]["NEXT"], "BLOCKED")
        record = view["completion_events"][0]["records"][0]
        self.assertEqual(record["status"], "FAIL")
        self.assertEqual(record["scope"], ["A"])
        self.assertNotIn("JOIN", view["retained_ancestry"])

    def test_source_closing_guard_prevents_transition_issuance(self):
        original = self.c.wg._recursive_context_v1
        source = self.run / "inputs/a"
        def change_after_context(*args, **kwargs):
            context = original(*args, **kwargs)
            source.write_text("changed while deriving recursive projection\n")
            return context
        count = len(self.c._issued)
        self.c.wg._recursive_context_v1 = change_after_context
        try:
            with self.assertRaisesRegex(self.case.owner.CompletionError, "changed"):
                self.c.transition()
        finally:
            self.c.wg._recursive_context_v1 = original
        self.assertEqual(len(self.c._issued), count)

    def test_oversized_projection_refuses_without_issuing_credit(self):
        limit = self.case.owner.MAX_JOURNAL_BYTES
        self.case.owner.MAX_JOURNAL_BYTES = 128
        try:
            with self.assertRaisesRegex(self.case.owner.CompletionError, "projection byte bound"):
                self.c.transition()
        finally:
            self.case.owner.MAX_JOURNAL_BYTES = limit
        self.assertEqual(self.c._issued, {})
        self.assertEqual(self.c.transition()["completion_events"], [])

    def test_current_compiler_identity_closing_guard_is_required(self):
        original = self.c.owner.raw
        self.c.owner.raw = original + b"\n"
        count = len(self.c._issued)
        try:
            with self.assertRaisesRegex(self.case.owner.CompletionError, "compiler source changed"):
                self.c.transition()
        finally:
            self.c.owner.raw = original
        self.assertEqual(len(self.c._issued), count)


if __name__ == "__main__":
    unittest.main()
