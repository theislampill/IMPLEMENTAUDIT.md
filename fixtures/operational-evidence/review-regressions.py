"""Focused independent-review regressions on synthetic source inputs.

These controls do not authenticate a native source or activate a controller.
The preserved seed is the review's explicitly constructed native payload.
"""
import copy
from email.message import Message
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location("oe_review_regressions", ROOT / "scripts/operational-evidence.py")
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)
SEED = json.loads((ROOT / "fixtures/operational-evidence/review-native-before.json").read_bytes())


def digest(value):
    return hashlib.sha256(oe.canonical_json_v1(value)).hexdigest()


def material(epoch="G0009"):
    collections = copy.deepcopy(SEED["collections"])
    native = collections["native_current"]["value"]
    native["continuity"]["generation"] = epoch
    native["continuity"]["source_epoch"] = epoch
    native["continuity"]["receipt_ref"] = "refs/implementaudit/continuity-receipts/constructed-controller/" + epoch
    native["continuity"]["receipt"] = native["continuity"]["receipt_ref"] + "@" + "4" * 40
    native.pop("semantic_sha256")
    native["semantic_sha256"] = digest(native)
    collections["native_current"]["sha256"] = digest(native)
    return oe._build_snapshot_material_v1(native, collections,
        (ROOT / "docs/operational-evidence-schema.json").read_bytes(),
        (ROOT / "scripts/operational-evidence.py").read_bytes())


class ReviewRegressions(unittest.TestCase):
    def test_native_response_selects_only_consumed_headers(self):
        class Response:
            status = 200
            def __init__(self, headers): self.headers = headers
            def read(self, maximum): return b"{}"
            def close(self): pass
        headers = Message()
        headers.add_header("X-OAuth-Client-Id", "synthetic-public-client")
        headers.add_header("X-OAuth-Client-Id", "synthetic-public-client")
        headers.add_header("ETag", "exact-etag")
        headers.add_header("X-RateLimit-Remaining", "1")
        headers.add_header("X-RateLimit-Reset", "978307200")
        with patch.object(oe.urllib.request, "build_opener") as opener:
            opener.return_value.open.return_value = Response(headers)
            result = oe._native_external_get("https://api.github.com/repos/fixture/project/pulls/1", {})
        self.assertEqual(result["headers"], {"ETag": "exact-etag", "X-RateLimit-Remaining": "1",
                                           "X-RateLimit-Reset": "978307200"})
        for name in ("etag", "x-ratelimit-remaining", "x-ratelimit-reset", "link"):
            duplicate = Message()
            duplicate.add_header(name, "first")
            duplicate.add_header(name.upper(), "second")
            with self.subTest(header=name), patch.object(oe.urllib.request, "build_opener") as opener:
                opener.return_value.open.return_value = Response(duplicate)
                with self.assertRaises(oe.OperationalEvidenceError):
                    oe._native_external_get("https://api.github.com/repos/fixture/project/pulls/1", {})

    def test_external_capture_retains_exact_rate_reset_without_invention(self):
        request = {"schema": "implementaudit-external-read-request-v1", "source": "GITHUB_API",
            "operation": "PULL_REQUEST", "path": "/repos/fixture/project/pulls/1", "auth_state": "PRESENT",
            "page": 1, "per_page": 100, "expected_etag": None, "captured_at": "2001-01-01T00:00:00Z",
            "expires_at": "2099-01-01T01:00:00Z", "evaluated_at": "2001-01-01T00:00:00Z"}
        response = {"status": 200, "headers": {"ETag": "fixture", "X-RateLimit-Remaining": "1",
                    "X-RateLimit-Reset": "978307200"}, "body": oe.canonical_json_v1({"id": 1, "number": 1,
                    "url": "https://api.github.com/repos/fixture/project/pulls/1",
                    "base": {"repo": {"full_name": "fixture/project"}}})}
        with patch.object(oe, "_native_external_get", return_value=response):
            value = oe.run_external_readonly(request, authorization_token="synthetic-token")
        self.assertEqual(value["response"]["rate_reset_at"], "2001-01-01T00:00:00Z")
        self.assertNotIn("synthetic-token", str(value))
        for bad in ("-1", "not-an-epoch", "1,2", "253402300800", "９７８３０７２００"):
            with self.subTest(reset=bad), patch.object(oe, "_native_external_get", return_value={
                    **response, "headers": {**response["headers"], "X-RateLimit-Reset": bad}}):
                with self.assertRaises(oe.OperationalEvidenceError):
                    oe.run_external_readonly(request)
        response["headers"].pop("X-RateLimit-Reset")
        with patch.object(oe, "_native_external_get", return_value=response):
            missing = oe.run_external_readonly(request)
        self.assertIsNone(missing["response"]["rate_reset_at"])

    def test_snapshot_release_reuses_acquired_repository_and_keeps_final_fence(self):
        root = ROOT / "fixtures/operational-evidence/release/positive"
        repository = {"repository": {"commit": "3"*40, "tree": "4"*40, "worktree_state": "CLEAN"},
            "facts": [{"kind": "FILE", "path": p.relative_to(root).as_posix(),
                       "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in root.rglob("*") if p.is_file()]}
        native = copy.deepcopy(SEED["collections"]["native_current"]["value"])
        native["repository"]["root"] = str(root)
        native["claim"]["run_root"] = "."
        with patch.object(oe, "collect_repository", return_value=repository) as scan:
            reference = oe.collect_release(root)
            self.assertEqual(scan.call_count, 2)
        with patch.object(oe, "collect_repository", return_value=repository) as scan:
            composed = oe._collect_snapshot_inputs_v1(native)
            self.assertEqual(scan.call_count, 2)  # Opening C02 plus unchanged C05 final fence.
            self.assertEqual(composed["release"]["value"], reference)
        changed = copy.deepcopy(repository)
        changed["repository"]["commit"] = "5"*40
        with patch.object(oe, "collect_repository", side_effect=[repository, changed]), \
                self.assertRaises(oe.OperationalEvidenceError) as refused:
            oe._collect_snapshot_inputs_v1(native)
        self.assertEqual(refused.exception.code, "OE_RELEASE_CHANGED_DURING_SCAN")

    @unittest.skipUnless(os.name == "nt", "Windows Git long-path behavior")
    def test_git_long_path_deletion_is_not_clean(self):
        with tempfile.TemporaryDirectory(prefix="oe-long-git-") as directory:
            root = Path(directory)
            environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
            def git(*args):
                return subprocess.run(["git", "-c", "core.longpaths=true", "-c", "core.hooksPath=" + os.devnull,
                    "-c", "commit.gpgsign=false", "-C", str(root), *args], env=environment,
                    capture_output=True, check=True)
            git("init", "-q")
            relative = "/".join(["directory_" + "a" * 40] * 5 + ["input.txt"])
            target = root / relative
            target.parent.mkdir(parents=True)
            target.write_bytes(b"tracked bytes\n")
            self.assertGreater(len(str(target)), 260)
            git("add", ".")
            git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
            self.assertEqual(oe._run_git(root, "status", "--porcelain=v1").stdout, "")
            target.unlink()
            expected = git("status", "--porcelain=v1").stdout.decode()
            self.assertIn(" D ", expected)
            self.assertEqual(oe._run_git(root, "status", "--porcelain=v1").stdout, expected)

    def test_all_external_operations_bind_the_exact_object(self):
        api = "https://api.github.com/repos/fixture/project"
        cases = [
            ("PULL_REQUEST", "/pulls/1", {"id": 1, "number": 1, "url": api + "/pulls/1",
                "base": {"repo": {"full_name": "fixture/project"}}}, "number", 2),
            ("CHECK_RUNS", "/commits/" + "a" * 40 + "/check-runs", {"total_count": 1,
                "check_runs": [{"id": 1, "url": api + "/check-runs/1", "head_sha": "a" * 40}]},
                "check_runs", [{"id": 1, "url": api + "/check-runs/1", "head_sha": "b" * 40}]),
            ("TAG", "/git/ref/tags/v1", {"ref": "refs/tags/v1", "url": api + "/git/refs/tags/v1",
                "object": {"type": "commit", "sha": "a" * 40}}, "ref", "refs/tags/v2"),
            ("RELEASE", "/releases/tags/v1", {"id": 1, "tag_name": "v1", "url": api + "/releases/1"}, "tag_name", "v2"),
            ("ASSET", "/releases/assets/1", {"id": 1, "url": api + "/releases/assets/1"}, "id", 2),
            ("PUBLIC_READBACK", "/contents/README.md", {"type": "file", "path": "README.md",
                "url": api + "/contents/README.md", "sha": "a" * 40}, "path", "other.md"),
        ]
        for operation, suffix, payload, key, wrong in cases:
            with self.subTest(operation=operation):
                request = {"schema": "implementaudit-external-read-request-v1", "source": "GITHUB_API",
                    "operation": operation, "path": "/repos/fixture/project" + suffix, "auth_state": "ABSENT",
                    "page": 1, "per_page": 100, "expected_etag": "fixture", "captured_at": "2001-01-01T00:00:00Z",
                    "expires_at": "2099-01-01T01:00:00Z", "evaluated_at": "2001-01-01T00:01:00Z"}
                response = {"status": 200, "headers": {"ETag": "fixture", "X-RateLimit-Remaining": "1"},
                            "body": oe.canonical_json_v1(payload)}
                with patch.object(oe, "_native_external_get", return_value=response) as native:
                    positive = oe.run_external_readonly(request, authorization_token="synthetic-token")
                self.assertEqual(positive["currentness"]["state"], "CURRENT")
                self.assertEqual(native.call_args.args[1]["Authorization"], "Bearer synthetic-token")
                self.assertNotIn("synthetic-token", str(positive))
                response["body"] = oe.canonical_json_v1({**payload, key: wrong})
                with patch.object(oe, "_native_external_get", return_value=response):
                    negative = oe.run_external_readonly(request, authorization_token="synthetic-token")
                self.assertIn("RESPONSE_OBJECT_MISMATCH", negative["currentness"]["invalidators"])
                response["body"] = oe.canonical_json_v1(payload)
                injected = oe.run_external_readonly({**request, "auth_state": "PRESENT"},
                                                    lambda _url, _headers: response)
                self.assertNotEqual(injected["currentness"]["state"], "CURRENT")
                with self.assertRaises(oe.OperationalEvidenceError):
                    oe.run_external_readonly(request, lambda *_: response, authorization_token="synthetic-token")

    def test_expired_release_rows_are_not_current_now(self):
        source = ROOT / "fixtures/operational-evidence/release/positive"
        repository = {"commit": "3" * 40, "tree": "4" * 40, "worktree_state": "CLEAN"}
        files = [{"kind": "FILE", "path": path.relative_to(source).as_posix(),
                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                 for path in source.rglob("*") if path.is_file()]
        with patch.object(oe, "collect_repository", return_value={"repository": repository, "facts": files}):
            release = oe.collect_release(source)
        collections = copy.deepcopy(SEED["collections"])
        collections["release"] = {"owner": "R0038-C05", "state": "CURRENT",
                                  "value": release, "sha256": digest(release)}
        built = oe._build_snapshot_material_v1(collections["native_current"]["value"], collections,
            (ROOT / "docs/operational-evidence-schema.json").read_bytes(), b"synthetic compiler")
        value = json.loads(built["payload_raw"])
        original = oe.canonical_json_v1(value)
        current = oe.query_family(value, "RELEASE", current_only=True)
        self.assertFalse([row for row in current["rows"] if row["record"].get("layer") == "EXTERNAL"])
        all_rows = oe.query_family(value, "RELEASE")["rows"]
        external = [row["record"] for row in all_rows if row["record"].get("layer") == "EXTERNAL"]
        self.assertEqual(len(external), 7)
        self.assertTrue(all("CAPTURE_EXPIRED" in row["currentness"]["invalidators"] for row in external))
        self.assertEqual(oe.canonical_json_v1(value), original)
        self.assertEqual(oe.diff_snapshots(value, value)["counts"]["changed"], 0)

    def test_native_http_cannot_inherit_caller_authentication(self):
        request = {"schema": "implementaudit-external-read-request-v1", "source": "GITHUB_API",
            "operation": "PULL_REQUEST", "path": "/repos/constructed/project/pulls/1", "auth_state": "PRESENT",
            "page": 1, "per_page": 100, "expected_etag": "fixture", "captured_at": "2001-01-01T00:00:00Z",
            "expires_at": "2099-01-01T01:00:00Z", "evaluated_at": "2001-01-01T00:01:00Z"}
        response = {"status": 200, "headers": {"ETag": "fixture", "X-RateLimit-Remaining": "1"},
            "body": b'{"id":999,"number":999,"url":"https://api.github.com/repos/foreign/project/pulls/999"}'}
        with patch.object(oe, "_native_external_get", return_value=response):
            result = oe.run_external_readonly(request)
        self.assertNotEqual(result["currentness"]["state"], "CURRENT")
        self.assertIn("AUTH_ABSENT", result["currentness"]["invalidators"])
        self.assertIn("RESPONSE_OBJECT_MISMATCH", result["currentness"]["invalidators"])

    def test_content_mutation_cannot_retain_snapshot_identity(self):
        built = material()
        before = json.loads(built["payload_raw"])
        self.assertEqual(oe.diff_snapshots(before, before)["counts"]["changed"], 0)
        changed = copy.deepcopy(before)
        native = changed["collections"]["native_current"]["value"]
        native["next_action"] = "changed synthetic action"
        native.pop("semantic_sha256")
        native["semantic_sha256"] = digest(native)
        changed["collections"]["native_current"]["sha256"] = digest(native)
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.diff_snapshots(before, changed)

    def test_original_structured_snapshot_identity(self):
        built = material()
        value = json.loads(built["payload_raw"])
        self.assertIn("input_manifest", value)
        self.assertIn("identity_record", value)
        semantic = {k: value[k] for k in ("schema_version", "aggregate", "families",
                                         "missing_or_omitted_state", "collections")}
        identity = value["identity_record"]
        self.assertEqual(set(identity), {"domain", "encoding", "canonicalisation",
            "semantic_payload_sha256", "canonical_input_manifest_sha256", "schema_sha256",
            "compiler_contract_sha256", "compiler_blob_sha256"})
        self.assertEqual(identity["domain"], "IA-OPERATIONAL-SNAPSHOT-v1")
        self.assertEqual(identity["semantic_payload_sha256"], digest(semantic))
        self.assertEqual(identity["canonical_input_manifest_sha256"], digest(value["input_manifest"]))
        self.assertEqual(value["snapshot_id"], "iasnap-v1-" + digest(identity))

    @unittest.skipIf(os.name == "nt", "real filter fixture uses a POSIX Git shell")
    def test_git_configuration_change_cannot_execute_a_filter(self):
        with tempfile.TemporaryDirectory(prefix="oe-review-git-") as directory:
            root = Path(directory)
            environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
            real_run = subprocess.run

            def git(*args):
                return real_run(["git", "-C", str(root), "-c", "core.hooksPath=" + os.devnull,
                    "-c", "commit.gpgsign=false", *args], env=environment, check=True, capture_output=True)

            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (root / "item.dat").write_bytes(b"before\n")
            (root / ".gitattributes").write_bytes(b"item.dat filter=latefixture\n")
            git("add", "item.dat", ".gitattributes")
            git("commit", "-qm", "fixture")
            (root / "item.dat").write_bytes(b"after!\n")
            marker = root / "marker"
            helper = root / "filter.py"
            helper.write_text("from pathlib import Path\nimport sys\nPath(" + repr(str(marker)) +
                ").write_text('fixture')\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n")
            command = shlex.quote(sys.executable) + " " + shlex.quote(str(helper))
            git("config", "filter.latefixture.clean", command)
            git("status", "--porcelain=v1")
            self.assertTrue(marker.exists(), "ordinary Git must exercise the positive sentinel")
            marker.unlink()
            oe._run_git(root, "status", "--porcelain=v1")
            self.assertFalse(marker.exists(), "a preexisting filter must be disabled")
            git("config", "--unset", "filter.latefixture.clean")
            injected = []

            def at_invocation(args, *positional, **kwargs):
                if "status" in args and not injected:
                    with (root / ".git/config").open("a") as stream:
                        stream.write('\n[filter "latefixture"]\n\tclean = ' + command + "\n")
                    injected.append(True)
                return real_run(args, *positional, **kwargs)

            with patch.object(oe.subprocess, "run", side_effect=at_invocation):
                oe._run_git(root, "status", "--porcelain=v1")
            self.assertEqual(injected, [True])
            self.assertFalse(marker.exists(), "configuration changed before invocation executed target code")

    def test_hexadecimal_epoch_acceptance(self):
        for epoch in ("G0009", "G000A", "GFFFF"):
            with self.subTest(epoch=epoch):
                built = material(epoch)
                parsed = oe._snapshot_validate_manifest_v1(built["manifest_raw"], built["snapshot_id"])
                self.assertEqual(parsed["source_epoch"], epoch)

    def test_malformed_epoch_refusal(self):
        built = material()
        for epoch in ("g000A", "G000a", "G000", "G10000", "G00X1", 10):
            row = json.loads(built["manifest_raw"])
            row["source_epoch"] = epoch
            with self.subTest(epoch=epoch), self.assertRaises(oe.OperationalEvidenceError):
                oe._snapshot_validate_manifest_v1(oe.canonical_json_v1(row), built["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
