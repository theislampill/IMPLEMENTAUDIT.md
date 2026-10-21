"""Same-discriminator consumer and boundary tests, usable against donor or successor.

All repositories and adversarial bytes are constructed in a disposable directory.
This is a source regression suite, never native acquisition/receiving evidence.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import socket
import unittest
from unittest.mock import patch

SOURCE_ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location("oe_under_test", SOURCE_ROOT / "scripts/operational-evidence.py")
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)

def git(root, *args, **kwargs):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

def initialize(root, files):
    root.mkdir()
    for name, raw in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    git(root, "init", "-q")
    git(root, "add", "--all", "--force")
    git(root, "-c", "user.name=R0038 fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", "Constructed portable fixture")
    return root

def snapshot(collection):
    # Explicitly a frozen collector consumer fixture, not a native-current record.
    return {"schema_version": oe.SNAPSHOT_PAYLOAD_SCHEMA, "snapshot_id": "fixture",
            "aggregate": "DEGRADED", "families": list(oe.FAMILIES),
            "missing_or_omitted_state": [{"state": "UNVERIFIED", "code": "NATIVE_NOT_ACQUIRED"}],
            "collections": {"repository": {"owner": "R0038-C02", "state": "CURRENT",
                "value": collection, "sha256": hashlib.sha256(oe.canonical_json_v1(collection)).hexdigest()}}}

class PortableBoundaryTests(unittest.TestCase):
    def test_selected_reader_rechecks_real_persisted_collector_inputs(self):
        # Constructed native observer only. All repository collection, persisted
        # files, owner manifest validation and input fences execute normally.
        run = self.repo / "fixture-run"
        run.mkdir()
        (self.repo / ".git/info/exclude").write_text("fixture-run/\n")
        native = {"repository": {"root": str(self.repo), "git_common_dir": str(self.repo / ".git")},
                  "controller": {"id": "fixture-controller"},
                  "claim": {"id": "a" * 32, "run_id": "fixture-ABC123", "run_root": "fixture-run"},
                  "continuity": {"pointer_oid": "1" * 40, "source_epoch": "G0001"},
                  "hot": {"state_sha256": "2" * 64, "roadmap_sha256": "3" * 64,
                          "work_graph_sha256": "4" * 64},
                  "route": {"record_identity": "constructed-route-identity"}}
        script = SOURCE_ROOT / "scripts/operational-evidence.py"
        schema = SOURCE_ROOT / "docs/operational-evidence-schema.json"
        material = oe._build_snapshot_material_v1(native, oe._collect_snapshot_inputs_v1(native),
                                                  schema.read_bytes(), script.read_bytes())
        snapshots = run / "operational-evidence/snapshots"
        selected = snapshots / material["snapshot_id"]
        selected.mkdir(parents=True)
        for name, key in (("snapshot.json", "payload_raw"), ("input-manifest.json", "input_raw"),
                          ("manifest.json", "manifest_raw")):
            (selected / name).write_bytes(material[key])
        (snapshots / "CURRENT").write_bytes(material["current_raw"])
        source = self.repo / "local.py"
        original = source.read_bytes()
        with patch.object(oe, "collect_native_current", return_value=native):
            self.assertEqual(oe.canonical_json_v1(oe._load_selected_snapshot_v1()), material["payload_raw"])
            source.write_bytes(b"VALUE = 9\n")
            with self.assertRaises(oe.OperationalEvidenceError) as raised:
                oe._load_selected_snapshot_v1()
            self.assertEqual(raised.exception.code, "OE_SNAPSHOT_STALE")
            source.write_bytes(original)
            collect = oe._capture_snapshot_inputs_v1
            calls = []
            def drift_after_first_collection(current):
                value, reobserve = collect(current)
                calls.append(value)
                if len(calls) == 1:
                    source.write_bytes(b"VALUE = 8\n")
                def final_observation(native):
                    calls.append(None)
                    return reobserve(native)
                return value, final_observation
            with patch.object(oe, "_capture_snapshot_inputs_v1", side_effect=drift_after_first_collection):
                with self.assertRaises(oe.OperationalEvidenceError) as raised:
                    oe._load_selected_snapshot_v1()
            self.assertEqual(raised.exception.code, "OE_SNAPSHOT_INPUT_CHANGED")
            self.assertEqual(len(calls), 2)

    def test_rehashed_repository_fact_scalars_are_validated(self):
        original = oe.observe_repository_snapshot_v1(self.repo)
        for key, bad in (("bytes", -1), ("bytes", True), ("file_type", "device"),
                         ("sha256", "not-a-digest"), ("language", "foreign")):
            value = copy.deepcopy(original)
            member = value["collections"]["repository"]
            next(row for row in member["value"]["facts"] if row["kind"] == "FILE")[key] = bad
            member["sha256"] = hashlib.sha256(oe.canonical_json_v1(member["value"])).hexdigest()
            value["input_manifest"]["collection_sha256"] = member["sha256"]
            digest = hashlib.sha256(oe.canonical_json_v1(value["input_manifest"])).hexdigest()
            value["input_manifest_sha256"] = digest
            value["snapshot_id"] = "iarepo-v1-" + digest
            for consumer in (lambda: oe.query_family(value, "CODE"),
                             lambda: oe.diff_snapshots(original, value)):
                with self.subTest(key=key, value=bad):
                    with self.assertRaises(oe.OperationalEvidenceError) as raised:
                        consumer()
                    self.assertEqual(raised.exception.code, "OE_DIFF_SNAPSHOT_INVALID")

    def test_legitimate_code_cycle_remains_explainable(self):
        (self.repo / "main.py").write_bytes(b"import local\n")
        (self.repo / "local.py").write_bytes(b"import main\n")
        value = oe.observe_repository_snapshot_v1(self.repo)
        rows = oe.query_family(value, "CODE")["rows"]
        source = next(row["record"]["id"] for row in rows
                      if row["record"].get("observation", {}).get("kind") == "FILE"
                      and row["record"]["observation"]["path"] == "main.py")
        why = oe.explain_history_why_v1(value, source)
        self.assertEqual(why["status"], "FOUND")
        self.assertEqual(len(why["chain"]), 2)
        self.assertEqual(len(why["relations"]), 2)
        self.assertEqual(why["establishes"], [])
        self.assertEqual(len(why["code_cycle_relations"]), 1)

    def test_same_line_computed_imports_retain_distinct_anchors(self):
        (self.repo / "main.py").write_bytes(b'__import__("x"); __import__("y")\n')
        value = oe.observe_repository_snapshot_v1(self.repo)
        unknown = value["collections"]["repository"]["value"]["diagnostics"]["unknown"]
        self.assertEqual(len(unknown), 2)
        self.assertEqual(len(set(unknown)), 2)
        self.assertEqual(len(oe.query_family(value, "CODE")["rows"]),
                         len({row["record"]["id"] for row in oe.query_family(value, "CODE")["rows"]}))

    def test_submodule_filter_cannot_execute_during_parent_collection(self):
        child = initialize(self.root / "submodule-source", {"file.dat": b"aaaa\n"})
        git(self.repo, "-c", "protocol.file.allow=always", "submodule", "add", "--quiet", str(child), "child")
        checkout = self.repo / "child"
        marker = self.root / "FILTER_EXECUTED"
        script = self.root / "constructed-filter.py"
        script.write_text("import pathlib, sys\npathlib.Path(" + repr(str(marker)) +
                          ").write_text('constructed')\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n")
        git(checkout, "config", "filter.constructed.clean", sys.executable + " " + str(script))
        (checkout / ".gitattributes").write_bytes(b"*.dat filter=constructed\n")
        (checkout / "file.dat").write_bytes(b"bbbb\n")
        git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")
        self.assertTrue(marker.exists(), "positive control did not execute the configured submodule filter")
        marker.unlink()
        observed = oe.collect_repository(self.repo)
        self.assertFalse(marker.exists(), "untrusted child repository filter executed")
        self.assertTrue(any(row.get("path") == "child" and row["state"] != "CURRENT"
                            for row in observed["facts"]), "unqualified gitlink contents became CURRENT")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r0038-discriminator-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = initialize(self.root / "repository", {
            "main.py": b"import local\n", "local.py": b"VALUE = 1\n", "README.txt": b"ordinary data\n"})

    def test_real_collector_code_query_retains_files_and_imports(self):
        collection = oe.collect_repository(self.repo)
        rows = [r["record"] for r in oe.query_family(snapshot(collection), "CODE")["rows"]]
        actual = [r.get("observation", r) for r in rows]
        self.assertTrue(any(r.get("kind") == "FILE" and r.get("path") == "main.py" for r in actual),
                        "C02 real FILE disappeared from C07 CODE query")
        self.assertTrue(any(r.get("kind") == "PYTHON_IMPORT" and r.get("target") == "local.py" for r in actual),
                        "C02 real import disappeared from C07 CODE query")
        self.assertTrue(all(r.get("source_identity") for r in rows), "query rows lost their source anchor")

    def test_state_precedence_is_exact_for_every_pair(self):
        order = ["CURRENT", "UNSUPPORTED", "UNKNOWN", "UNVERIFIED", "STALE",
                 "PARSER_ERROR", "CONTRADICTORY", "INVALID"]
        for left in order:
            for right in order:
                with self.subTest(left=left, right=right):
                    actual = oe._compose_currentness({"state": left, "invalidators": []},
                                                       {"state": right, "invalidators": []})
                    self.assertEqual(actual["state"], max((left, right), key=order.index))

    def test_failed_external_refresh_preserves_expired_state(self):
        request = {"schema": "implementaudit-external-read-request-v1", "source": "GITHUB_API",
                   "operation": "PULL_REQUEST", "path": "/repos/fixture/project/pulls/1",
                   "auth_state": "PRESENT", "page": 1, "per_page": 100,
                   "expected_etag": "fixture-pr-etag", "captured_at": "2026-08-20T02:30:00Z",
                   "expires_at": "2026-08-20T03:30:00Z", "evaluated_at": "2026-08-20T04:00:00Z"}
        response = {"status": 503, "headers": {"etag": "fixture-pr-etag", "x-ratelimit-remaining": "99"},
                    "body": b'{"message":"constructed unavailability"}'}
        result = oe.run_external_readonly(request, lambda *_: response)
        self.assertEqual(result["currentness"]["state"], "STALE")
        self.assertIn("HTTP_STATUS_503", result["currentness"]["invalidators"])

    def test_hardlinked_repository_file_does_not_read_outside_source(self):
        external = self.root / "outside-content"
        external.write_bytes(b"constructed hardlink sentinel\n")
        os.link(external, self.repo / "aliased.txt")
        git(self.repo, "add", "aliased.txt")
        rows = oe.collect_repository(self.repo)["facts"]
        self.assertFalse(any(row.get("path") == "aliased.txt" and row.get("state") == "CURRENT" for row in rows))

    def test_parent_symlink_does_not_read_outside_root(self):
        tracked = self.repo / "nested"
        tracked.mkdir()
        (tracked / "data.txt").write_bytes(b"inside\n")
        git(self.repo, "add", "nested/data.txt")
        outside = self.root / "outside"
        outside.mkdir()
        raw = b"constructed outside sentinel, never a real secret\n"
        (outside / "data.txt").write_bytes(raw)
        shutil.rmtree(tracked)
        tracked.symlink_to(outside, target_is_directory=True)
        facts = oe.collect_repository(self.repo)["facts"]
        self.assertFalse(any(r.get("sha256") == hashlib.sha256(raw).hexdigest() for r in facts),
                         "collector read bytes through a tracked parent symlink")
        self.assertTrue(any(r.get("path") == "nested/data.txt" and r.get("state") != "CURRENT" for r in facts))

    def test_force_tracked_secret_is_excluded_before_content_read(self):
        raw = b"CONSTRUCTED_TEST_TOKEN=sentinel_only\n"
        (self.repo / ".env").write_bytes(raw)
        git(self.repo, "add", "--force", ".env")
        facts = oe.collect_repository(self.repo)["facts"]
        self.assertFalse(any(r.get("sha256") == hashlib.sha256(raw).hexdigest() for r in facts),
                         "default input policy hashed a secret-named tracked file")
        self.assertTrue(any(r.get("path") == ".env" and r.get("state") != "CURRENT" for r in facts))

    def test_force_tracked_ignored_file_is_excluded(self):
        raw = b"constructed ignored input\n"
        (self.repo / ".gitignore").write_text("ignored.txt\n")
        (self.repo / "ignored.txt").write_bytes(raw)
        git(self.repo, "add", "--force", ".gitignore", "ignored.txt")
        facts = oe.collect_repository(self.repo)["facts"]
        self.assertFalse(any(r.get("path") == "ignored.txt" and r.get("state") == "CURRENT" for r in facts),
                         "ignored tracked content was accepted")

    def test_git_environment_cannot_replace_explicit_repository(self):
        other = initialize(self.root / "other", {"foreign.txt": b"unrelated\n"})
        expected = git(self.repo, "rev-parse", "HEAD", text=True).stdout.strip()
        with patch.dict(os.environ, {"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(self.repo)}):
            observed = oe.collect_repository(self.repo)
        self.assertEqual(observed["repository"]["commit"], expected,
                         "ambient Git identity overrode the explicit root")

    def test_partial_record_is_refused_instead_of_silently_omitted(self):
        value = snapshot(oe.collect_repository(self.repo))
        value["collections"] = {"records": [{"id": "declared", "family": "CODE",
                                              "currentness": {"state": "MADE_UP", "invalidators": []}}]}
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.query_family(value, "CODE")

    def test_empty_family_cannot_keep_complete_status(self):
        value = snapshot(oe.collect_repository(self.repo))
        value["aggregate"] = "COMPLETE"
        value["missing_or_omitted_state"] = []
        value["collections"] = {}
        try:
            status = oe.evaluate_currentness(value)
        except oe.OperationalEvidenceError:
            return
        self.assertNotEqual(status["aggregate"], "COMPLETE", "empty six-family census stayed green")

    def test_saved_pointer_cannot_survive_new_native_generation(self):
        # A consumer seam with clearly constructed observations. No native owner
        # or credentials are simulated as real acquisition evidence.
        native = {"repository": {"root": str(self.repo)},
                  "claim": {"run_root": "fixture-run"},
                  "continuity": {"pointer_oid": "2" * 40}}
        current = {"snapshot_id": "iasnap-v1-" + "a" * 64, "source_pointer_oid": "1" * 40}
        payload = {"schema_version": oe.SNAPSHOT_PAYLOAD_SCHEMA, "snapshot_id": current["snapshot_id"]}
        with patch.object(oe, "collect_native_current", return_value=native), \
                patch.object(oe, "_snapshot_current_raw_v1", return_value=b"constructed"), \
                patch.object(oe, "_snapshot_validate_current_v1", return_value=current), \
                patch.object(oe, "_snapshot_read_regular_v1", return_value=oe.canonical_json_v1(payload)):
            with self.assertRaises(oe.OperationalEvidenceError) as context:
                oe._load_selected_snapshot_v1()
        self.assertEqual(context.exception.code, "OE_SNAPSHOT_STALE")

    def test_two_root_observation_and_frozen_consumers_are_offline(self):
        other = self.root / "clone"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(self.repo), str(other)], check=True)
        with patch.object(oe, "collect_native_current", side_effect=AssertionError("native acquisition invoked")), \
                patch.object(oe.urllib.request, "urlopen", side_effect=AssertionError("network invoked")), \
                patch.object(socket.socket, "connect", side_effect=AssertionError("socket invoked")), \
                patch.dict(sys.modules, {"openai": None, "anthropic": None}):
            left = oe.observe_repository_snapshot_v1(self.repo)
            right = oe.observe_repository_snapshot_v1(other)
            self.assertEqual(oe.canonical_json_v1(left), oe.canonical_json_v1(right))
            with patch.object(oe.subprocess, "run", side_effect=AssertionError("frozen process invoked")):
                status = oe.evaluate_currentness(left)
                self.assertEqual(status["aggregate"], "DEGRADED")
                for family in oe.FAMILIES:
                    result = oe.query_family(left, family)
                    if family != "CODE":
                        self.assertEqual(result["rows"], [])
                        self.assertTrue(any(row.get("family") == family and row["state"] == "UNVERIFIED"
                                            for row in result["missing_or_omitted_state"]))
                projection = json.loads(oe.render_snapshot_projection_v1(left, output_format="graph", max_rows=100, max_bytes=1000000))
                self.assertFalse(projection["truncated"])
                self.assertEqual(oe.diff_snapshots(left, right)["counts"], {"added": 0, "removed": 0, "changed": 0})
                rows = oe.query_family(left, "CODE")["rows"]
                source = next(r["record"]["id"] for r in rows if r["record"].get("observation", {}).get("path") == "main.py")
                why = oe.explain_history_why_v1(left, source)
                self.assertTrue(any(r.get("observation", {}).get("path") == "local.py" for r in why["chain"]))
        self.assertNotIn(str(self.repo), oe.canonical_json_v1(left).decode())
        self.assertFalse((self.repo / ".IMPLEMENTAUDIT").exists())

    def test_real_file_change_and_removal_survive_diff(self):
        before = oe.observe_repository_snapshot_v1(self.repo)
        (self.repo / "local.py").write_bytes(b"VALUE = 2\n")
        after = oe.observe_repository_snapshot_v1(self.repo)
        diff = oe.diff_snapshots(before, after)
        self.assertTrue(any(r["after"].get("observation", {}).get("path") == "local.py" for r in diff["changed"]))
        git(self.repo, "rm", "--force", "local.py")
        removed = oe.diff_snapshots(after, oe.observe_repository_snapshot_v1(self.repo))
        self.assertTrue(any(r["record"].get("observation", {}).get("path") == "local.py" for r in removed["removed"]))

    def test_repository_snapshot_scope_and_hash_cannot_be_promoted(self):
        value = oe.observe_repository_snapshot_v1(self.repo)
        for key, replacement in (("aggregate", "COMPLETE"), ("scope", "NATIVE"),
                                 ("schema_version", oe.SNAPSHOT_PAYLOAD_SCHEMA),
                                 ("missing_or_omitted_state", []), ("snapshot_id", "iarepo-v1-" + "0" * 64)):
            changed = copy.deepcopy(value)
            changed[key] = replacement
            with self.assertRaises(oe.OperationalEvidenceError, msg=key):
                oe.diff_snapshots(value, changed)
        changed = copy.deepcopy(value)
        changed["collections"]["repository"]["value"]["facts"][0]["state"] = "CURRENT_BUT_FAKE"
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.diff_snapshots(value, changed)

    def test_configured_git_filter_cannot_execute(self):
        marker = self.root / "FILTER_EXECUTED"
        hook = self.root / "filter.py"
        hook.write_text("from pathlib import Path\nimport sys\nPath(" + repr(str(marker)) + ").write_text('executed')\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n")
        (self.repo / ".gitattributes").write_text("*.py filter=r0038fixture\n")
        git(self.repo, "add", ".gitattributes")
        git(self.repo, "config", "filter.r0038fixture.clean", sys.executable + " " + str(hook))
        (self.repo / "main.py").write_text("import local\n# force dirty filter evaluation\n")
        git(self.repo, "status", "--porcelain=v1")
        self.assertTrue(marker.exists(), "positive sentinel did not exercise configured Git filter")
        marker.unlink()
        oe.collect_repository(self.repo)
        self.assertFalse(marker.exists(), "read-only collector executed target Git filter")

    def test_nonportable_names_and_input_limits_refuse(self):
        (self.repo / "MAIN.py").write_bytes(b"different case\n")
        git(self.repo, "add", "MAIN.py")
        with self.assertRaises(oe.OperationalEvidenceError) as context:
            oe.collect_repository(self.repo)
        self.assertEqual(context.exception.code, "OE_REPOSITORY_PATH")
        git(self.repo, "rm", "--force", "MAIN.py")
        with patch.object(oe, "REPOSITORY_MAX_FILES", 2):
            with self.assertRaises(oe.OperationalEvidenceError) as context:
                oe.collect_repository(self.repo)
            self.assertEqual(context.exception.code, "OE_REPOSITORY_LIMIT")
        with patch.object(oe, "REPOSITORY_MAX_TOTAL_BYTES", 1):
            with self.assertRaises(oe.OperationalEvidenceError):
                oe.collect_repository(self.repo)
        with patch.object(oe, "REPOSITORY_MAX_FILE_BYTES", 1):
            facts = oe.collect_repository(self.repo)["facts"]
            self.assertTrue(facts)
            self.assertTrue(all(row["state"] != "CURRENT" for row in facts))

    def test_companion_pair_missing_alias_and_wrong_bytes_refuse(self):
        scripts = SOURCE_ROOT / "scripts"
        owned = self.root / "loader"
        owned.mkdir()
        primary, companion = owned / "operational-evidence.py", owned / "operational_query_policy.py"
        primary.write_bytes((scripts / primary.name).read_bytes())
        correct = (scripts / companion.name).read_bytes()
        def invoke():
            return subprocess.run([sys.executable, "-B", str(primary), "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        missing = invoke()
        self.assertNotEqual(missing.returncode, 0)
        companion.write_bytes(correct)
        self.assertEqual(invoke().returncode, 0)
        companion.write_bytes(correct + b"\n# incompatible\n")
        self.assertNotEqual(invoke().returncode, 0)
        companion.unlink()
        companion.symlink_to(scripts / companion.name)
        self.assertNotEqual(invoke().returncode, 0)

    def test_hardlinked_companion_is_not_a_unique_source(self):
        scripts = SOURCE_ROOT / "scripts"
        owned = self.root / "hardlinked-loader"
        owned.mkdir()
        primary = owned / "operational-evidence.py"
        primary.write_bytes((scripts / primary.name).read_bytes())
        peer = owned / "peer.py"
        peer.write_bytes((scripts / "operational_query_policy.py").read_bytes())
        os.link(peer, owned / "operational_query_policy.py")
        result = subprocess.run([sys.executable, "-B", str(primary), "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(result.returncode, 0, "hardlinked policy source was accepted as unique")

    def test_cli_scan_frozen_inspect_and_typed_input_refusals(self):
        helper = SOURCE_ROOT / "scripts/operational-evidence.py"
        def invoke(*args):
            return subprocess.run([sys.executable, "-B", str(helper), *map(str, args)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        result = invoke("scan", self.repo)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        saved = self.root / "observation.json"
        saved.write_bytes(result.stdout)
        original = json.loads(result.stdout)
        for family in oe.FAMILIES:
            query = invoke("inspect", saved, "--family", family)
            self.assertEqual(query.returncode, 0, query.stderr.decode())
            parsed = json.loads(query.stdout)
            self.assertEqual(parsed["family"], family)
            self.assertEqual(parsed["acquisition_scope"], "REPOSITORY_ONLY_UNAUTHENTICATED_FILE")
        exported = invoke("inspect", saved, "--format", "json")
        self.assertEqual(exported.stdout, result.stdout)
        snapshot_before = hashlib.sha256(saved.read_bytes()).hexdigest()
        self.assertEqual(invoke("inspect", saved, "--family", "CODE", "--max-rows", 0).returncode, 2)
        self.assertEqual(invoke("status", "--repo-root", self.repo).returncode, 2)
        self.assertEqual(hashlib.sha256(saved.read_bytes()).hexdigest(), snapshot_before)
        for mutation in (None, [], 1, "bad"):
            broken = copy.deepcopy(original)
            broken["collections"]["repository"]["value"]["repository"]["commit"] = mutation
            # Even a self-consistent caller rehash cannot repair the typed schema.
            member = broken["collections"]["repository"]
            member["sha256"] = hashlib.sha256(oe.canonical_json_v1(member["value"])).hexdigest()
            manifest = broken["input_manifest"]
            manifest["collection_sha256"] = member["sha256"]
            digest = hashlib.sha256(oe.canonical_json_v1(manifest)).hexdigest()
            broken["snapshot_id"], broken["input_manifest_sha256"] = "iarepo-v1-" + digest, digest
            saved.write_bytes(oe.canonical_json_v1(broken))
            refused = invoke("inspect", saved)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(json.loads(refused.stderr)["code"], "OE_DIFF_SNAPSHOT_INVALID")

if __name__ == "__main__":
    unittest.main(verbosity=2)
