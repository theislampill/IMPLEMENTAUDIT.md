"""Original14 owner-to-graph document receiving; constructed scope, no native JOIN."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


NATIVE = load("original14_graph_documents", ROOT / "tests/native-work-graph-cases.py")
READER = load("original14_graph_reader", ROOT / "fixtures/canonical-state-rotation/canonical_reader_test.py")


def snapshot(root):
    return {str(path.relative_to(root)): (path.stat().st_mode & 0o777,
            hashlib.sha256(path.read_bytes()).hexdigest())
            for path in root.rglob("*") if path.is_file()}


@unittest.skipUnless(sys.platform == "linux", "actual POSIX owner/document receiving")
class Original14GraphReceiving(unittest.TestCase):
    def setUp(self):
        self.subject = READER.CanonicalReaderTests()
        self.addCleanup(self.subject.doCleanups)
        self.subject.setUp()

    def construct(self, *, omit_root=False):
        subject = self.subject
        with tempfile.TemporaryDirectory(prefix="original14-graph-documents-") as directory:
            documents = Path(directory)
            state, nodes = NATIVE.fixture()
            NATIVE.write_run(documents, state, nodes)
            extra = {str(path.relative_to(documents)): path.read_bytes()
                     for path in documents.rglob("*") if path.is_file()
                     and path.name not in {"STATE.md", "ROADMAP.md", "PH.md"}}
            # Preserve the real phase guard fixture and give its one physical
            # file the unchanged PH graph record; do not create a duplicate PH.
            extra["phases/phase-1.md"] = (subject.write_phase().read_bytes() + b"\n"
                                             + (documents / "phases/PH.md").read_bytes())
            if omit_root:
                extra.pop("plans/ROOT.md")
            self.resolution = subject.make_real_generation(native=True,
                state_edit=lambda text: text + "\n" + (documents / "STATE.md").read_text(),
                roadmap_edit=lambda text: text + "\n" + (documents / "ROADMAP.md").read_text(),
                extra_artifacts=extra)
        receipt = READER.command(["git", "cat-file", "blob",
                     self.resolution["receipt_token"].split("@", 1)[1]], subject.repo)
        self.assertEqual(receipt.returncode, 0, receipt.stderr)
        self.assertEqual(len(receipt.stdout.rstrip(b"\n").split(b"\t")), 14)

    def observe(self, after_use=None):
        subject = self.subject
        materialized = subject.read("--native-guards")
        self.assertEqual(materialized.returncode, 0, materialized.stderr)
        graph = NATIVE.wg.read_native_run_v1(subject.output / "native-records")
        if after_use is not None:
            after_use()
        closed = subject.read("--native-guards", "--verify-current")
        if closed.returncode:
            raise RuntimeError(closed.stderr.decode("utf-8", "replace"))
        # No result is returned before the existing owner closes consumption.
        return graph

    def test_real_original14_documents_reach_unchanged_graph_parser(self):
        self.construct()
        before = snapshot(self.subject.run)
        graph = self.observe()
        self.assertEqual(graph["binding"]["acquisition"], "CONSTRUCTED_FILESYSTEM")
        self.assertEqual(len(graph["nodes"]), 9)
        frontier = NATIVE.wg.select_native_frontier_v1(graph)
        self.assertEqual(frontier["selected"], ["PREP", "SIB"])
        self.assertIn("AUTHORIZATION", frontier["blocked"]["ADMIT"])
        self.assertIn("DEPENDENCY", frontier["blocked"]["QUALIFY"])
        self.assertEqual(frontier["authority"], "NONE")
        self.assertEqual(snapshot(self.subject.run), before)
        # The separately preserved WORK_GRAPH artifact is not silently replaced
        # by this new constructed projection or claimed as a native graph JOIN.
        stored = (self.subject.output / "native-records/WORK_GRAPH.json").read_bytes()
        self.assertNotEqual(json.loads(stored), graph)

    def test_protected_document_change_after_use_prevents_return(self):
        self.construct()
        path = self.subject.run / "plans/ROOT.md"
        raw = path.read_bytes()
        try:
            with self.assertRaisesRegex(RuntimeError, "JOIN refused|preserved owner bytes|changed"):
                self.observe(lambda: path.write_bytes(raw + b"\nchanged after graph use\n"))
        finally:
            path.write_bytes(raw)

    def test_derivative_snapshot_change_after_use_prevents_return(self):
        self.construct()
        def change():
            path = self.subject.output / "native-records/tasks/C1.md"
            path.write_bytes(path.read_bytes() + b"\nchanged derivative\n")
        with self.assertRaisesRegex(RuntimeError, "validation snapshot or current native authority changed"):
            self.observe(change)

    def test_actual_later_invalidation_prevents_return(self):
        self.construct()
        def invalidate():
            result = self.subject.claim("--invalidate-continuity", READER.CONTROLLER,
                "--boundary", "new-session", "--event", "constructed-later-original14-boundary")
            self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaisesRegex(RuntimeError, "JOIN refused|changed"):
            self.observe(invalidate)

    def test_valid_original14_owner_does_not_supply_missing_graph_document(self):
        self.construct(omit_root=True)
        materialized = self.subject.read("--native-guards")
        self.assertEqual(materialized.returncode, 0, materialized.stderr)
        with self.assertRaises(NATIVE.wg.WorkGraphError):
            NATIVE.wg.read_native_run_v1(self.subject.output / "native-records")
        closed = self.subject.read("--native-guards", "--verify-current")
        self.assertEqual(closed.returncode, 0, closed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
