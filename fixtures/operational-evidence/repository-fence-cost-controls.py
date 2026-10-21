"""Constructed repository cost/fence controls; no native or performance-budget credit.

Only disposable repositories are published. The native observer is an explicit
constructed fixture; repository handles, Git reads, collectors and fences run.
"""
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch


parser = argparse.ArgumentParser()
parser.add_argument("source_root", type=Path)
parser.add_argument("--report", type=Path)
parser.add_argument("--reference-source", type=Path)
parser.add_argument("--test", action="append")
args = parser.parse_args()
ROOT = args.source_root.resolve()
METRICS = {}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oe = load(ROOT / "scripts/operational-evidence.py", "repository_cost_subject")
reference = load(args.reference_source, "repository_cost_reference") if args.reference_source else None


@contextlib.contextmanager
def constructed_native_observation():
    """Preserve mocked before/after drift checks without invoking a native owner."""
    before = copy.deepcopy(oe.collect_native_current())
    before_raw = oe.canonical_json_v1(before)
    yield before
    if oe.canonical_json_v1(oe.collect_native_current()) != before_raw:
        raise oe.OperationalEvidenceError(
            "OE_NATIVE_CURRENT_CHANGED", "$native.fixture", "constructed native observation drifted")


def git(root, *argv):
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_DATE="2026-10-20T12:00:00Z", GIT_COMMITTER_DATE="2026-10-20T12:00:00Z")
    return subprocess.run(["git", "-C", str(root), *argv], env=environment,
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class RepositoryFenceCostTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="oe-repository-cost-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repository"
        shutil.copytree(ROOT / "fixtures/operational-evidence/release/positive", self.root)
        (self.root / "local.py").write_bytes(b"VALUE = 1\n")
        git(self.root, "init", "-q")
        git(self.root, "add", "--all", "--force")
        git(self.root, "-c", "user.name=Constructed repository control",
            "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
            "commit", "-qm", "Constructed repository fence control")
        (self.root / ".git/info/exclude").write_text(
            "fixture-run/\nscripts/\ndocs/\nast-copy.py\n", encoding="ascii")
        for relative in ("scripts/operational-evidence.py", "docs/operational-evidence-schema.json"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.native = {
            "repository": {"root": str(self.root), "git_common_dir": str(self.root / ".git")},
            "controller": {"id": "fixture-controller"},
            "claim": {"id": "a" * 32, "run_id": "fixture-ABC123", "run_root": "fixture-run"},
            "continuity": {"pointer_oid": "1" * 40, "source_epoch": "G0001"},
            "hot": {"state_sha256": "2" * 64, "roadmap_sha256": "3" * 64,
                    "work_graph_sha256": "4" * 64},
            "route": {"record_identity": "constructed-route-identity"}}
        (self.root / "fixture-run").mkdir()
        self.current = self.root / "fixture-run/operational-evidence/snapshots/CURRENT"

    def publish(self, stage=None):
        with patch.object(oe, "__file__", str(self.root / "scripts/operational-evidence.py")), \
                patch.object(oe, "collect_native_current", side_effect=lambda: copy.deepcopy(self.native)), \
                patch.object(oe, "_snapshot_stage_v1", side_effect=stage or (lambda name: None)):
            return oe.publish_current_snapshot()

    def measured(self, name, action):
        counts = {"python_parses": 0, "secure_reads": 0, "stability_fences": 0, "git_reads": 0}
        secure_reader = ("_windows_read_held_leaf_v1"
                         if os.name == "nt" and hasattr(oe, "_windows_read_held_leaf_v1")
                         else "_read_repository_path")
        originals = {key: getattr(oe, value) for key, value in {
            "secure_reads": secure_reader, "stability_fences": "_require_repository_snapshot_stable",
            "git_reads": "_run_git"}.items()}
        original_parse = oe.ast.parse

        def parse(source, filename="<unknown>", *a, **kw):
            if filename == "local.py":
                counts["python_parses"] += 1
            return original_parse(source, filename, *a, **kw)

        def counted(key):
            def invoke(*a, **kw):
                counts[key] += 1
                return originals[key](*a, **kw)
            return invoke

        started = time.perf_counter()
        with patch.object(oe.ast, "parse", side_effect=parse), \
                patch.object(oe, secure_reader, side_effect=counted("secure_reads")), \
                patch.object(oe, "_require_repository_snapshot_stable", side_effect=counted("stability_fences")), \
                patch.object(oe, "_run_git", side_effect=counted("git_reads")):
            result = action()
        METRICS[name] = {**counts, "seconds": time.perf_counter() - started}
        return result, counts

    def test_release_derives_repository_once_with_exact_output(self):
        # A second AST reconstruction is the redundant work this guard rejects.
        expected = (reference or oe)._collect_release_from_repository_v1(
            self.root, (reference or oe).collect_repository(self.root))
        result, counts = self.measured("release", lambda: oe.collect_release(self.root))
        self.assertEqual(oe.canonical_json_v1(result), oe.canonical_json_v1(expected))
        self.assertEqual(counts["python_parses"], 1)

    def test_secure_read_counter_includes_scoped_and_standalone_acquisitions(self):
        path = self.root / "local.py"
        def both_read_paths():
            first = oe._read_repository_path(path, root=self.root)
            if hasattr(oe, "_repository_read_scope_v1"):
                with oe._repository_read_scope_v1(self.root) as read:
                    second = read(path)
            else:
                second = oe._read_repository_path(path, root=self.root)
            return first, second
        values, counts = self.measured("secure_reader_counter", both_read_paths)
        self.assertEqual(values, ((b"VALUE = 1\n", "file"), (b"VALUE = 1\n", "file")))
        self.assertEqual(counts["secure_reads"], 2)

    def test_snapshot_publication_derives_repository_once(self):
        result, counts = self.measured("constructed_publication", self.publish)
        self.assertEqual(result["selection_state"], "ADVANCED")
        self.assertTrue(self.current.is_file())
        self.assertEqual(counts["python_parses"], 1)
        payload = json.loads((self.current.parent / result["snapshot_id"] / "snapshot.json").read_bytes())
        expected = (reference or oe)._collect_snapshot_inputs_v1(self.native)
        self.assertEqual(oe.canonical_json_v1(payload["collections"]), oe.canonical_json_v1(expected))

    def test_collector_retains_three_terminal_fences_and_exact_output(self):
        expected = (reference or oe).collect_repository(self.root)
        result, counts = self.measured("repository", lambda: oe.collect_repository(self.root))
        self.assertEqual(oe.canonical_json_v1(result), oe.canonical_json_v1(expected))
        self.assertEqual(counts["stability_fences"], 3)

    def test_no_sensitive_callback_follows_terminal_collector_fence(self):
        original_fence = oe._require_repository_snapshot_stable
        state = {"fences": 0, "after": []}
        def fence(*a, **kw):
            result = original_fence(*a, **kw)
            state["fences"] += 1
            return result
        def monitor(name, action):
            def invoke(*a, **kw):
                if state["fences"] == 3:
                    state["after"].append(name)
                return action(*a, **kw)
            return invoke
        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(oe, "_require_repository_snapshot_stable", side_effect=fence))
            for name in ("_run_git", "_read_repository_path", "canonical_json_v1", "decode_strict_json_bytes"):
                stack.enter_context(patch.object(oe, name, side_effect=monitor(name, getattr(oe, name))))
            result = oe.collect_repository(self.root)
        self.assertEqual(result["repository"]["worktree_state"], "CLEAN")
        self.assertEqual(state, {"fences": 3, "after": []})

    def test_partial_parser_and_exclusion_outputs_match_frozen_preimage(self):
        for name, raw in {"local.py": b"import helper\n__import__('dynamic')\n", "helper.py": b"VALUE = 1\n",
                          "broken.py": b"def broken(:\n", ".env": b"constructed private bytes\n"}.items():
            (self.root / name).write_bytes(raw)
        git(self.root, "add", "--force", "local.py", "helper.py", "broken.py", ".env")
        expected = (reference or oe).collect_repository(self.root)
        result = oe.collect_repository(self.root)
        self.assertEqual(oe.canonical_json_v1(result), oe.canonical_json_v1(expected))
        self.assertIn("PARSER_ERROR_OBSERVATION", {row["kind"] for row in result["facts"]})
        self.assertIn("FILE_EXCLUDED_OBSERVATION", {row["kind"] for row in result["facts"]})

    def test_supplied_repository_facts_do_not_create_live_authority(self):
        supplied = oe.collect_repository(self.root)
        supplied["facts"].append({"kind": "PYTHON_IMPORT", "source": "local.py", "target": "fabricated.py"})
        with self.assertRaises(oe.OperationalEvidenceError) as caught:
            oe._collect_release_from_repository_v1(self.root, supplied)
        self.assertEqual(caught.exception.code, "OE_RELEASE_CHANGED_DURING_SCAN")

    def test_fresh_fences_reject_bytes_paths_exclusions_git_and_hardlinks(self):
        mutations = {
            "bytes": lambda: (self.root / "local.py").write_bytes(b"VALUE = 2\n"),
            "index": lambda: git(self.root, "update-index", "--force-remove", "local.py"),
            "exclusions": lambda: (self.root / ".git/info/exclude").write_text("local.py\nfixture-run/\nscripts/\ndocs/\n"),
            "head": lambda: git(self.root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                                "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Changed identity"),
            "hardlink": lambda: os.link(self.root / "local.py", Path(self.temporary.name) / "alias.py"),
        }
        # Restore the constructed repository between independent mutations.
        for name, mutation in mutations.items():
            with self.subTest(mutation=name):
                fired = []
                def stage(boundary):
                    if boundary == "after-first-observation" and not fired:
                        fired.append(True)
                        mutation()
                with self.assertRaises(oe.OperationalEvidenceError):
                    self.publish(stage)
                self.assertTrue(fired)
                self.assertFalse(self.current.exists())
                if name != "hardlink":
                    git(self.root, "reset", "--hard", "HEAD~1" if name == "head" else "HEAD")
                    (self.root / ".git/info/exclude").write_text("fixture-run/\nscripts/\ndocs/\nast-copy.py\n")

    def test_late_byte_drift_cannot_select_current(self):
        def stage(boundary):
            if boundary == "before-current-replace":
                (self.root / "local.py").write_bytes(b"VALUE = 3\n")
        with self.assertRaises(oe.OperationalEvidenceError):
            self.publish(stage)
        self.assertFalse(self.current.exists())

    def test_ast_provenance_drift_is_not_reused(self):
        ast_copy = self.root / "ast-copy.py"
        ast_copy.write_bytes(Path(oe.ast.__file__).read_bytes())
        def stage(boundary):
            if boundary == "after-first-observation":
                ast_copy.write_bytes(ast_copy.read_bytes() + b"\n# changed collector source\n")
        with patch.object(oe.ast, "__file__", str(ast_copy)), self.assertRaises(oe.OperationalEvidenceError):
            self.publish(stage)
        self.assertFalse(self.current.exists())

    def test_runtime_and_optional_owner_drift_are_not_reused(self):
        for mode in ("runtime", "optional-owner", "compiler"):
            with self.subTest(mode=mode):
                original_version = oe.platform.python_version
                def stage(boundary):
                    if boundary != "after-first-observation":
                        return
                    if mode == "runtime":
                        oe.platform.python_version = lambda: "constructed-runtime-drift"
                    elif mode == "compiler":
                        source = self.root / "scripts/operational-evidence.py"
                        source.write_bytes(source.read_bytes() + b"\n# changed source\n")
                    else:
                        shutil.copytree(ROOT / "fixtures/operational-evidence/run-artifacts/positive",
                                        self.root / "fixture-run", dirs_exist_ok=True)
                try:
                    with self.assertRaises(oe.OperationalEvidenceError):
                        self.publish(stage)
                    self.assertFalse(self.current.exists())
                finally:
                    oe.platform.python_version = original_version
                if mode == "optional-owner":
                    # Remove only the exact fixture files just copied in this test.
                    for source in (ROOT / "fixtures/operational-evidence/run-artifacts/positive").iterdir():
                        if source.is_file():
                            (self.root / "fixture-run" / source.name).unlink()

    def test_returned_collection_mutation_does_not_change_retained_baseline(self):
        if not hasattr(oe, "_capture_snapshot_inputs_v1"):
            self.skipTest("private transaction factory absent in preimage")
        collections, reobserve = oe._capture_snapshot_inputs_v1(self.native)
        expected = oe.canonical_json_v1(collections)
        collections["repository"]["value"]["facts"].append({"kind": "FORGED"})
        self.assertEqual(oe.canonical_json_v1(reobserve(self.native)), expected)

    def test_selected_reader_rechecks_drift_after_live_capture(self):
        self.publish()
        original_capture = oe._capture_snapshot_inputs_v1
        captured = []
        def capture(native):
            result = original_capture(native)
            captured.append(True)
            (self.root / "local.py").write_bytes(b"VALUE = 99\n")
            return result
        with patch.object(oe, "__file__", str(self.root / "scripts/operational-evidence.py")), \
                patch.object(oe, "collect_native_current", side_effect=lambda: copy.deepcopy(self.native)), \
                patch.object(oe, "_observe_native_current_v1", side_effect=constructed_native_observation):
            selected = oe._load_selected_snapshot_v1()
            self.assertEqual(selected["snapshot_id"], json.loads(self.current.read_bytes())["snapshot_id"])
            with patch.object(oe, "_capture_snapshot_inputs_v1", side_effect=capture), \
                    self.assertRaises(oe.OperationalEvidenceError) as caught:
                oe._load_selected_snapshot_v1()
        self.assertEqual(captured, [True])
        self.assertEqual(caught.exception.code, "OE_SNAPSHOT_INPUT_CHANGED")

    def test_native_drift_is_still_observed(self):
        def stage(boundary):
            if boundary == "after-first-observation":
                self.native["continuity"]["pointer_oid"] = "f" * 40
        with self.assertRaises(oe.OperationalEvidenceError) as caught:
            self.publish(stage)
        self.assertEqual(caught.exception.code, "OE_SNAPSHOT_INPUT_CHANGED")

    def test_each_transaction_collects_fresh_semantics(self):
        first = oe.collect_release(self.root)
        (self.root / "local.py").write_bytes(b"VALUE = 4\n")
        second, counts = self.measured("next_transaction", lambda: oe.collect_release(self.root))
        self.assertEqual(first["repository"]["worktree_state"], "CLEAN")
        self.assertEqual(second["repository"]["worktree_state"], "DIRTY")
        self.assertEqual(counts["python_parses"], 1)


if __name__ == "__main__":
    suite = (unittest.TestSuite(RepositoryFenceCostTests(name) for name in args.test)
             if args.test else unittest.defaultTestLoader.loadTestsFromTestCase(RepositoryFenceCostTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"scope": "CONSTRUCTED_REPOSITORY_CONTROLS_NOT_NATIVE_ACCEPTANCE_OR_BUDGET",
              "source_sha256": hashlib.sha256((ROOT / "scripts/operational-evidence.py").read_bytes()).hexdigest(),
              "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "metrics": METRICS}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
