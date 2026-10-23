#!/usr/bin/env python3
"""Executable controls for the opt-in, repo-only C5 reproduction event owner."""

import json
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / "scripts/repro-event-capture.py"


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def load_owner():
    spec = importlib.util.spec_from_file_location("repro_capture", OWNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_FIXTURE = r'''#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$1"
if [ "${C5_CASE_FAIL_B:-}" = 1 ] && [ "$TZ" = America/New_York ]; then
  printf 'partial generation\n' > "$1/partial.txt"
  printf 'build B failed\n' >&2
  exit 41
fi
python - "$1" <<'PY'
import os, pathlib, sys, zipfile
root = pathlib.Path(sys.argv[1])
body = b"same fixture payload\n"
if os.environ.get("C5_CASE_DIFFERENT_B") == "1" and os.environ["TZ"] == "America/New_York":
    body = b"different fixture payload\n"
for name in ("IMPLEMENTAUDIT.plugin.zip", "IMPLEMENTAUDIT.skill"):
    with zipfile.ZipFile(root / name, "w") as archive:
        stamp = (2020, 1, 1, 0, 0, 0) if os.environ.get("C5_CASE_BAD_ZIP") == "1" else (1980, 1, 1, 0, 0, 0)
        member = zipfile.ZipInfo("payload.txt", stamp)
        member.create_system = 3
        member.external_attr = (0o100644 << 16)
        member.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(member, body)
PY
bash "$(dirname "$0")/write-release-checksums.sh" --all "$1" "$1/CHECKSUMS.txt"
if [ "${C5_CASE_BAD_CHECKSUM:-}" = 1 ]; then
  printf 'invalid checksum entry\n' >> "$1/CHECKSUMS.txt"
fi
if [ "${C5_CASE_MISSING_B:-}" = 1 ] && [ "$TZ" = America/New_York ]; then
  rm "$1/IMPLEMENTAUDIT.plugin.zip"
fi
printf 'fixture build complete\n'
'''


class Fixture:
    """Real local Git clones, real ZIP producers and real cmp/checksum consumers."""
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="repro-c5-fixture-", dir="/tmp")
        self.base = Path(self.temporary.name)
        self.repo = self.base / "product"
        (self.repo / "tests").mkdir(parents=True)
        (self.repo / "scripts").mkdir()
        for relative in ("tests/reproducible-release-asset.test.sh", "scripts/repro-event-capture.py",
                         "scripts/write-release-checksums.sh"):
            shutil.copy2(ROOT / relative, self.repo / relative)
        build = self.repo / "scripts/build-release-asset.sh"
        build.write_text(BUILD_FIXTURE)
        build.chmod(0o755)
        for command in (["init", "-q"], ["config", "user.name", "C5 Local Fixture"],
                        ["config", "user.email", "c5-fixture@example.invalid"],
                        ["add", "--all"], ["commit", "-qm", "finite C5 fixture"]):
            subprocess.run(["git", "-C", str(self.repo), *command], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.commit = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"]).decode().strip()
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for key in list(self.env):
            if key.startswith(("REPRO_RETAINED_", "R0035_REPRO_EVENT_")) or key == "REPRO_SOURCE_REF":
                del self.env[key]
        self.owner = load_owner()

    def clean(self):
        self.temporary.cleanup()

    def run(self, name="capture", **overrides):
        capture = self.base / name
        env = dict(self.env, R0035_REPRO_EVENT_CAPTURE_DIR=str(capture), **overrides)
        result = subprocess.run(["bash", "tests/reproducible-release-asset.test.sh"], cwd=self.repo,
                                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return capture, result

    def cli(self, *args, env=None, **kwargs):
        return subprocess.run(["python", str(self.repo / "scripts/repro-event-capture.py"), *map(str, args)],
                              cwd=self.repo, env=env or self.env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, **kwargs)

    def prefix(self):
        work = self.base / "prefix-work"
        work.mkdir()
        capture = self.base / "prefix-capture"
        for lane in "ab":
            subprocess.run(["git", "clone", "-q", "--no-local", str(self.repo), str(work / ("checkout-" + lane))],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = self.cli("init", capture, self.repo, work, self.commit, "python")
        assert result.returncode == 0, result.stderr
        for lane, tz in (("a", "UTC"), ("b", "America/New_York")):
            result = self.cli("event", capture, "build:" + lane, "--", "bash",
                              work / ("checkout-" + lane) / "scripts/build-release-asset.sh",
                              work / ("out-" + lane), env=dict(self.env, SOURCE_DATE_EPOCH="315532800", TZ=tz, LC_ALL="C"))
            assert result.returncode == 0, result.stderr
        return capture, work

    def compare(self, capture, work, env=None):
        return self.cli("event", capture, "cmp:IMPLEMENTAUDIT.plugin.zip", "--", "cmp", "-s",
                        work / "out-a/IMPLEMENTAUDIT.plugin.zip", work / "out-b/IMPLEMENTAUDIT.plugin.zip", env=env)

    def finish_partial(self, capture, work, code=1):
        result = self.cli("close", capture, code)
        assert result.returncode == 0, result.stderr
        result = subprocess.run(["rm", "-rf", str(work)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ended = self.cli("finish", capture, result.returncode)
        assert ended.returncode == 0 if code else ended.returncode == 125, ended.stderr
        return self.owner.verify_record(capture, require_complete=False)


class QualifierCases(unittest.TestCase):
    """Actual v4 handoff through both registered-node execution routes."""
    @classmethod
    def setUpClass(cls):
        cls.fixture = Fixture()
        root = cls.fixture.repo
        for name in ("scripts/qualify-work-graph-verifier.py", "scripts/run-work-graph-verifier.sh",
                     "skills/implementaudit/scripts/compile-work-graph.py"):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        (root / "scripts/generate-readme-diagrams.sh").write_text("#!/bin/bash\nexit 0\n")
        (root / "scripts/verify-package.sh").write_text(
            "#!/bin/bash\nset -euo pipefail\n"
            "bash scripts/generate-readme-diagrams.sh --check\n"
            "bash tests/reproducible-release-asset.test.sh\n"
            "git diff --check\nprintf 'verify-package: ok\\n'\n")
        for command in (["add", "--all"], ["commit", "-qm", "finite actual qualifier C5 handoff"]):
            subprocess.run(["git", "-C", str(root), *command], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cls.outputs = {}
        for mode in ("legacy", "dag"):
            output = cls.fixture.base / ("qualifier-" + mode)
            process = cls.invoke(mode, output, "--retain-repro-events")
            if process.returncode:
                raise AssertionError((mode, process.returncode, process.stdout, process.stderr))
            cls.outputs[mode] = output

    @classmethod
    def tearDownClass(cls):
        cls.fixture.clean()

    @classmethod
    def invoke(cls, *arguments, **overrides):
        return subprocess.run([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", *map(str, arguments)],
                              cwd=cls.fixture.repo, env=dict(cls.fixture.env, **overrides),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @classmethod
    def readback(cls, directory):
        program = (
            "import importlib.util,sys; from pathlib import Path; "
            "s=importlib.util.spec_from_file_location('q','scripts/qualify-work-graph-verifier.py'); "
            "q=importlib.util.module_from_spec(s); s.loader.exec_module(q); "
            "q.verified_record(Path(sys.argv[1]))")
        return subprocess.run([sys.executable, "-B", "-c", program, str(directory)],
                              cwd=cls.fixture.repo, env=cls.fixture.env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_actual_legacy_and_dag_complete_after_original_cleanup(self):
        for mode, output in self.outputs.items():
            with self.subTest(mode=mode):
                result = read_json(output / "result.json")
                self.assertEqual(result["schema"], "implementaudit.verifier-run.v4")
                self.assertIsNone(result["portal_events"])
                self.assertEqual(result["exit"], 0)
                self.assertEqual(result["repro_events"]["coverage"], "COMPLETE_FINITE_REPRO_CHILD_EVENTS")
                self.assertEqual(len(result["repro_events"]["record"]["events"]), 19)
                session = read_json(output / "repro-events/session.json")
                self.assertFalse(Path(session["context"]["work_root"]).exists())
                actual = self.readback(output)
                self.assertEqual(actual.returncode, 0, actual.stderr.decode(errors="replace"))
                compared = self.invoke("compare", output, output, self.fixture.base / (mode + "-self-comparison.json"))
                # The comparator requires a legacy/DAG pair. A self-comparison
                # validates identical declarations but must not satisfy that
                # route obligation merely because its raw bytes are equal.
                self.assertEqual(compared.returncode, 1, (compared.stdout, compared.stderr))
                checks = json.loads(compared.stdout)["checks"]
                self.assertFalse(checks.pop("route_pair"))
                self.assertTrue(all(checks.values()), checks)

    def test_retained_source_run_context_and_shape_mutations_refuse(self):
        original = self.outputs["dag"]
        mutations = {
            "foreign-repository": lambda row: row["repro_events"]["binding"].update(repository="/foreign"),
            "foreign-output": lambda row: row["repro_events"]["binding"].update(output="/foreign"),
            "foreign-run": lambda row: row["repro_events"]["record"].update(run_id="0" * 32),
            "foreign-source": lambda row: row["repro_events"]["binding"]["source"].update(source_commit="0" * 40),
            "wrong-coverage": lambda row: row["repro_events"].update(coverage="UNQUALIFIED_PARTIAL_OR_FAILED_PROCESS"),
            "boolean-exit": lambda row: row.update(exit=False),
            "v3-downgrade": lambda row: row.update(schema="implementaudit.verifier-run.v3"),
            "missing-portal-slot": lambda row: row.pop("portal_events"),
        }
        for label, mutate in mutations.items():
            with self.subTest(control=label):
                target = self.fixture.base / ("mutation-" + label)
                shutil.copytree(original, target)
                result = read_json(target / "result.json")
                mutate(result)
                write_json(target / "result.json", result)
                self.assertNotEqual(self.readback(target).returncode, 0)
        for relative in ("session.json", "record.json"):
            with self.subTest(missing=relative):
                target = self.fixture.base / ("missing-" + relative)
                shutil.copytree(original, target)
                (target / "repro-events" / relative).unlink()
                self.assertNotEqual(self.readback(target).returncode, 0)

    def test_failed_child_keeps_actual_exit_and_partial_profile(self):
        output = self.fixture.base / "qualifier-child-failure"
        process = self.invoke("dag", output, "--retain-repro-events", C5_CASE_FAIL_B="1")
        self.assertNotEqual(process.returncode, 0)
        result = read_json(output / "result.json")
        self.assertEqual(result["exit"], int((output / "exit-code.txt").read_text()))
        self.assertEqual(result["repro_events"]["coverage"], "UNQUALIFIED_PARTIAL_OR_FAILED_PROCESS")
        self.assertFalse(result["repro_events"]["record"]["assessment"]["complete"])
        self.assertEqual(self.readback(output).returncode, 0)

    def test_ambient_capture_refuses_nominal_v3_and_explicit_v4(self):
        for ordinal, options in enumerate((("--empty-stdin",), ("--retain-repro-events",))):
            output = self.fixture.base / ("ambient-" + str(ordinal))
            actual = self.invoke("dag", output, *options, R0035_REPRO_EVENT_CAPTURE_DIR="")
            self.assertEqual(actual.returncode, 2)
            self.assertIn(b"ambiguous inherited repro event capture", actual.stderr)
            self.assertFalse((output / "exit-code.txt").exists())

    def test_new_producer_preserves_v3_six_export_contract(self):
        output = self.fixture.base / "new-producer-v3"
        actual = self.invoke("dag", output, "--retain-repro-assets")
        self.assertEqual(actual.returncode, 0, actual.stderr.decode(errors="replace"))
        result = read_json(output / "result.json")
        self.assertEqual(result["schema"], "implementaudit.verifier-run.v3")
        self.assertNotIn("repro_events", result)
        self.assertNotIn("portal_events", result)
        self.assertTrue(result["repro_artifacts"]["complete"])
        self.assertEqual(self.readback(output).returncode, 0)


EXPECTED_ROLES = [
    "build:a", "build:b", "cmp:IMPLEMENTAUDIT.plugin.zip", "cmp:IMPLEMENTAUDIT.skill", "cmp:CHECKSUMS.txt",
    "checksum:a", "checksum:b", "manifest:plugin:a", "manifest:plugin:b", "manifest-cmp:plugin",
    "manifest:skill:a", "manifest:skill:b", "manifest-cmp:skill", "hash:skill:a", "hash:skill:b",
    "hash:plugin:a", "hash:plugin:b", "hash:checksums:a", "hash:checksums:b",
]


class ProfileCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = Fixture()
        cls.capture, cls.result = cls.fixture.run()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.clean()

    def test_actual_complete_profile_and_original_cleanup(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr.decode(errors="replace"))
        owner = self.fixture.owner
        record = owner.verify_record(self.capture)
        events = [read_json(self.capture / row["path"]) for row in record["events"]]
        processes = [read_json(self.capture / row["path"]) for row in record["process_results"]]
        self.assertEqual([row["role"] for row in events], EXPECTED_ROLES)
        self.assertEqual([row["role"] for row in processes], EXPECTED_ROLES)
        self.assertTrue(all(row["dispatch"] == "CHILD_RETURNED" for row in processes))
        self.assertEqual(record["handoff_failures"], [])
        self.assertEqual(record["unhanded_blobs"], [])
        self.assertTrue(all(row["exit_code"] == 0 for row in events))
        self.assertEqual(record["cleanup"], {"exit_code": 0, "work_root_absent": True})
        self.assertFalse(Path(read_json(self.capture / "session.json")["context"]["work_root"]).exists())
        self.assertEqual(events[2]["argv"][0:2], ["cmp", "-s"])
        self.assertEqual(events[2]["inputs_before"], events[2]["inputs_after"])
        self.assertEqual(events[0]["outputs_after"][0]["members"], events[5]["inputs_before"][0]["members"])
        for index in (7, 8, 10, 11):
            self.assertEqual(events[index]["stdin"]["mode"], "INLINE_BYTES")
            self.assertEqual(events[index]["stdout"], events[index]["outputs_after"][0]["blob"])
        self.assertIn("DECLARED_CONSISTENCY_ONLY", record["semantics"])
        self.assertEqual(owner.verify_record(self.capture, expected_source=record["source"],
                                            expected_run_id=record["run_id"]), record)

    def copied(self):
        target = Path(tempfile.mkdtemp(prefix="altered-", dir=self.fixture.base))
        target.rmdir()
        shutil.copytree(self.capture, target)
        self.addCleanup(shutil.rmtree, target)
        return target

    def reseal(self, target, index, item):
        path = target / "events" / f"{index:02d}.json"
        write_json(path, item)
        record = read_json(target / "record.json")
        raw = path.read_bytes()
        record["events"][index] = dict(path="events/" + path.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        write_json(target / "record.json", record)

    def reseal_process_stdout(self, target, index, raw):
        import base64
        path = target / "processes" / f"{index:02d}.json"
        item = read_json(path)
        item["stdout_base64"] = base64.b64encode(raw).decode()
        write_json(path, item)
        data = path.read_bytes()
        record = read_json(target / "record.json")
        record["process_results"][index] = dict(path="processes/" + path.name,
                                                bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        write_json(target / "record.json", record)

    def test_missing_duplicate_reordered_and_foreign_events_refused(self):
        for change in ("missing", "duplicate", "reordered", "foreign-run", "foreign-source"):
            with self.subTest(change=change):
                target = self.copied()
                if change == "missing":
                    (target / "events/01.json").unlink()
                else:
                    item = read_json(target / "events/02.json")
                    if change == "duplicate":
                        item = read_json(target / "events/01.json")
                    elif change == "reordered":
                        item["role"] = "cmp:IMPLEMENTAUDIT.skill"
                    elif change == "foreign-run":
                        item["run_id"] = "0" * 32
                    else:
                        item["source_sha256"] = "0" * 64
                    self.reseal(target, 2, item)
                with self.assertRaises(self.fixture.owner.ReproCaptureError):
                    self.fixture.owner.verify_record(target)

    def test_raw_exit_stdin_artifact_and_generation_omissions_refused(self):
        for change in ("exit", "stdin", "input", "generation", "invocation", "output-mode"):
            with self.subTest(change=change):
                target = self.copied()
                index = 7 if change == "stdin" else 2 if change in {"exit", "input", "invocation"} else 0
                item = read_json(target / "events" / f"{index:02d}.json")
                if change == "exit":
                    item["exit_code"] = 1
                elif change == "stdin":
                    item["stdin"] = {"mode": "INHERITED_UNQUALIFIED"}
                elif change == "input":
                    item["inputs_before"] = []
                elif change == "generation":
                    item["generation_id"] = None
                elif change == "invocation":
                    item["argv"][1] = "--silent"
                else:
                    item["outputs_after"][0]["members"][0]["stat"]["mode"] ^= 0o100
                self.reseal(target, index, item)
                with self.assertRaises(self.fixture.owner.ReproCaptureError):
                    self.fixture.owner.verify_record(target)

    def test_corrupt_symlink_foreign_blob_and_stale_binding_refused(self):
        event = read_json(self.capture / "events/00.json")
        blob = event["outputs_after"][0]["members"][0]["blob"]["sha256"]
        for change in ("corrupt", "missing", "symlink", "foreign"):
            with self.subTest(change=change):
                target = self.copied()
                path = target / "blobs" / blob
                if change == "corrupt":
                    path.write_bytes(path.read_bytes() + b"corrupt")
                elif change == "missing":
                    path.unlink()
                elif change == "symlink":
                    path.unlink()
                    path.symlink_to(self.capture / "blobs" / blob)
                else:
                    (target / "blobs" / ("f" * 64)).write_bytes(b"unreferenced")
                with self.assertRaises(self.fixture.owner.ReproCaptureError):
                    self.fixture.owner.verify_record(target)
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(self.capture, expected_source={"source_commit": "0" * 40})
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(self.capture, expected_run_id="0" * 32)

    def test_resealed_inconsistent_checksum_stdout_is_not_a_success_receipt(self):
        target = self.copied()
        item = read_json(target / "events/05.json")
        raw = b"fabricated checksum success output\n"
        sha = hashlib.sha256(raw).hexdigest()
        retained = target / "blobs" / sha
        retained.write_bytes(raw)
        retained.chmod(0o600)
        item["stdout"] = {"bytes": len(raw), "sha256": sha}
        self.reseal(target, 5, item)
        self.reseal_process_stdout(target, 5, raw)
        with self.assertRaisesRegex(self.fixture.owner.ReproCaptureError, "declared completion differs"):
            self.fixture.owner.verify_record(target)

    def test_boolean_completion_type_and_retained_blob_modes_are_strict(self):
        target = self.copied()
        record = read_json(target / "record.json")
        record["assessment"]["complete"] = 1
        write_json(target / "record.json", record)
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(target)

    def test_retained_blob_mode_is_strict(self):
        target = self.copied()
        event = read_json(target / "events/02.json")
        (target / "blobs" / event["stdout"]["sha256"]).chmod(0o755)
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(target)

    def test_resealed_manifests_must_describe_the_actual_consumed_archive(self):
        target = self.copied()
        old = read_json(target / "events/07.json")["stdout"]
        raw = b"[]\n"
        new = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        path = target / "blobs" / new["sha256"]
        path.write_bytes(raw)
        path.chmod(0o600)
        def rewrite(value):
            if isinstance(value, dict):
                if value == old:
                    return dict(new)
                if value.get("kind") == "FILE" and value.get("blob") == old:
                    value["stat"]["size"] = len(raw)
                return {key: rewrite(item) for key, item in value.items()}
            if isinstance(value, list):
                return [rewrite(item) for item in value]
            return value
        for index in range(19):
            event = read_json(target / "events" / f"{index:02d}.json")
            if event["stdout"] == old:
                self.reseal_process_stdout(target, index, raw)
            self.reseal(target, index, rewrite(event))
        closing = rewrite(read_json(target / "close.json"))
        write_json(target / "close.json", closing)
        record = read_json(target / "record.json")
        record["close_sha256"] = hashlib.sha256((target / "close.json").read_bytes()).hexdigest()
        write_json(target / "record.json", record)
        (target / "blobs" / old["sha256"]).unlink()
        with self.assertRaisesRegex(self.fixture.owner.ReproCaptureError, "declared completion differs"):
            self.fixture.owner.verify_record(target)


class FailureCases(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.clean)

    def test_failed_build_keeps_actual_exit_and_never_creates_generation(self):
        capture, result = self.fixture.run(C5_CASE_FAIL_B="1")
        self.assertEqual(result.returncode, 41, result.stderr.decode(errors="replace"))
        record = self.fixture.owner.verify_record(capture, require_complete=False)
        self.assertFalse(record["assessment"]["complete"])
        self.assertEqual(len(record["events"]), 2)
        event = read_json(capture / "events/01.json")
        self.assertEqual(event["exit_code"], 41)
        self.assertIsNone(event["generation_id"])
        self.assertEqual([Path(item["path"]).name for item in event["outputs_after"][0]["members"]], ["partial.txt"])
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(capture)

    def test_actual_cmp_difference_and_missing_input_have_distinct_raw_exits(self):
        for flag, code in (("C5_CASE_DIFFERENT_B", 1), ("C5_CASE_MISSING_B", 2)):
            with self.subTest(flag=flag):
                capture, result = self.fixture.run(name=flag, **{flag: "1"})
                self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace"))
                record = self.fixture.owner.verify_record(capture, require_complete=False)
                self.assertFalse(record["assessment"]["complete"])
                self.assertEqual(len(record["events"]), 3)
                self.assertEqual(read_json(capture / "events/02.json")["exit_code"], code)

    def test_byte_and_mtime_restoration_cannot_reuse_old_generation(self):
        capture, work = self.fixture.prefix()
        operand = work / "out-b/IMPLEMENTAUDIT.plugin.zip"
        raw, before = operand.read_bytes(), operand.stat()
        operand.write_bytes(raw + b"changed then restored")
        operand.write_bytes(raw)
        os.utime(operand, ns=(before.st_atime_ns, before.st_mtime_ns))
        result = self.fixture.compare(capture, work)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        event = read_json(capture / "events/02.json")
        self.assertEqual(event["exit_code"], 0)
        record = self.fixture.finish_partial(capture, work)
        self.assertTrue(any("INPUT_GENERATION_DRIFT" in issue for issue in record["assessment"]["issues"]))
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
            self.fixture.owner.verify_record(capture)

    def test_actual_checksum_and_inline_manifest_failures_survive_cleanup(self):
        for flag, count, role in (("C5_CASE_BAD_CHECKSUM", 6, "checksum:a"),
                                  ("C5_CASE_BAD_ZIP", 8, "manifest:plugin:a")):
            with self.subTest(flag=flag):
                capture, result = self.fixture.run(name=flag, **{flag: "1"})
                self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace"))
                record = self.fixture.owner.verify_record(capture, require_complete=False)
                self.assertEqual(len(record["events"]), count)
                event = read_json(capture / record["events"][-1]["path"])
                self.assertEqual(event["role"], role)
                self.assertEqual(event["exit_code"], 1)
                self.assertGreater(event["stderr"]["bytes"], 0)
                self.assertIsNone(event["generation_id"])
                if flag == "C5_CASE_BAD_ZIP":
                    self.assertEqual(event["stdin"]["mode"], "INLINE_BYTES")
                    self.assertGreater(event["stdin"]["blob"]["bytes"], 0)

    def test_metadata_restoration_inside_consumer_window_is_detected(self):
        capture, work = self.fixture.prefix()
        commands = self.fixture.base / "commands"
        commands.mkdir()
        wrapper = commands / "cmp"
        # The real cmp executes first. A controlled effect then changes and
        # restores its operand's mode before the observed child process exits.
        wrapper.write_text('#!/usr/bin/env bash\nset -e\n/usr/bin/cmp "$@"\n'
                           'python - "$3" <<\'PY\'\nimport os,sys\np=sys.argv[1]\n'
                           'mode=os.stat(p).st_mode & 0o777\nos.chmod(p,mode ^ 0o100)\nos.chmod(p,mode)\nPY\n')
        wrapper.chmod(0o755)
        result = self.fixture.compare(capture, work, env=dict(self.fixture.env,
                                      PATH=str(commands) + os.pathsep + self.fixture.env["PATH"]))
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        record = self.fixture.finish_partial(capture, work)
        self.assertTrue(any("INPUT_WINDOW_DRIFT" in issue for issue in record["assessment"]["issues"]))

    def test_source_metadata_drift_and_symlink_input_are_not_accepted(self):
        capture, work = self.fixture.prefix()
        operand = work / "out-b/IMPLEMENTAUDIT.plugin.zip"
        operand.unlink()
        operand.symlink_to(work / "out-a/IMPLEMENTAUDIT.plugin.zip")
        producer = self.fixture.repo / "tests/reproducible-release-asset.test.sh"
        mode = producer.stat().st_mode & 0o777
        producer.chmod(mode ^ 0o100)
        producer.chmod(mode)
        result = self.fixture.compare(capture, work)
        self.assertEqual(result.returncode, 125)
        self.assertIsNone(read_json(capture / "events/02.json")["exit_code"])
        record = self.fixture.finish_partial(capture, work)
        self.assertTrue(any("SOURCE_CUSTODY_DRIFT" in issue for issue in record["assessment"]["issues"]))
        self.assertTrue(any("INPUT_GENERATION_DRIFT" in issue for issue in record["assessment"]["issues"]))

    def test_bad_order_does_not_execute_a_foreign_child(self):
        capture, work = self.fixture.prefix()
        result = self.fixture.cli("event", capture, "cmp:IMPLEMENTAUDIT.skill", "--", "cmp", "-s",
                                  work / "out-a/IMPLEMENTAUDIT.skill", work / "out-b/IMPLEMENTAUDIT.skill")
        self.assertEqual(result.returncode, 125)
        self.assertEqual(len(list((capture / "events").iterdir())), 2)
        self.fixture.finish_partial(capture, work)


class DurabilityCases(unittest.TestCase):
    """Original child outcomes survive acquisition failure; unsafe inputs never launch."""

    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.clean)

    def copied(self, source):
        target = Path(tempfile.mkdtemp(prefix="receipt-control-", dir=self.fixture.base))
        target.rmdir()
        shutil.copytree(source, target)
        self.addCleanup(shutil.rmtree, target)
        return target

    def reseal_process(self, capture, index, item):
        path = capture / "processes" / f"{index:02d}.json"
        write_json(path, item)
        raw = path.read_bytes()
        record = read_json(capture / "record.json")
        record["process_results"][index] = dict(path="processes/" + path.name,
                                                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        write_json(capture / "record.json", record)

    def test_completed_child_exit_is_durable_before_post_child_reads(self):
        import base64
        import errno
        capture, work = self.fixture.prefix()
        owner = self.fixture.owner
        left = work / "out-a/IMPLEMENTAUDIT.plugin.zip"
        right = work / "out-b/IMPLEMENTAUDIT.plugin.zip"
        right.write_bytes(right.read_bytes() + b"actual comparison difference")
        observe, execute = owner.observe, owner.capture_process
        completed = []
        def real_child(*args):
            result = execute(*args)
            completed.append(result)
            return result
        def failed_read(directory, path):
            if completed and Path(path) == left:
                raise OSError(errno.EIO, "post-child acquisition failure control")
            return observe(directory, path)
        owner.capture_process, owner.observe = real_child, failed_read
        cwd = Path.cwd()
        try:
            os.chdir(self.fixture.repo)
            try:
                result = owner.event(capture, "cmp:IMPLEMENTAUDIT.plugin.zip",
                                     ["cmp", "-s", str(left), str(right)])
            except OSError:
                result = None
        finally:
            os.chdir(cwd)
            owner.capture_process, owner.observe = execute, observe
        self.assertEqual(completed[0][0], 1)
        self.assertTrue((capture / "processes/02.json").is_file(),
                        "completed child exit was lost before post-acquisition failure")
        receipt = read_json(capture / "processes/02.json")
        self.assertEqual(receipt["exit_code"], 1)
        self.assertEqual(base64.b64decode(receipt["stdout_base64"]), completed[0][1])
        self.assertEqual(base64.b64decode(receipt["stderr_base64"]), completed[0][2])
        self.assertEqual(result, 125)
        self.assertTrue((capture / "processes/02.handoff.json").is_file())
        original_receipt = (capture / "processes/02.json").read_bytes()
        resumed = self.fixture.compare(capture, work)
        self.assertEqual(resumed.returncode, 125)
        self.assertEqual((capture / "processes/02.json").read_bytes(), original_receipt)
        record = self.fixture.finish_partial(capture, work)
        self.assertEqual(len(record["process_results"]), 3)
        self.assertEqual(len(record["events"]), 2)
        self.assertFalse(record["assessment"]["complete"])
        self.assertTrue(any("POST_ACQUISITION_HANDOFF_FAILED" in issue for issue in record["assessment"]["issues"]))
        with self.assertRaises(owner.ReproCaptureError):
            owner.verify_record(capture)
        for change in ("missing-marker", "foreign-marker", "marker-exit-bool", "unhanded-omission"):
            with self.subTest(change=change):
                target = self.copied(capture)
                marker = target / "processes/02.handoff.json"
                altered = read_json(marker)
                if change == "missing-marker":
                    marker.unlink()
                elif change == "foreign-marker":
                    altered["process_sha256"] = "0" * 64
                    write_json(marker, altered)
                elif change == "marker-exit-bool":
                    altered["errno"] = True
                    write_json(marker, altered)
                else:
                    record = read_json(target / "record.json")
                    del record["process_results"][-1]
                    write_json(target / "record.json", record)
                if marker.exists() and change != "unhanded-omission":
                    raw = marker.read_bytes()
                    record = read_json(target / "record.json")
                    record["handoff_failures"][0] = dict(path="processes/02.handoff.json",
                                                         bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                    write_json(target / "record.json", record)
                with self.assertRaises(owner.ReproCaptureError):
                    owner.verify_record(target, require_complete=False)

    def test_successful_child_raw_streams_precede_cas_read_and_failed_handoff(self):
        import base64
        import errno
        capture, work = self.fixture.prefix()
        owner = self.fixture.owner
        commands = self.fixture.base / "commands"
        commands.mkdir()
        wrapper = commands / "cmp"
        wrapper.write_text('#!/usr/bin/env bash\n/usr/bin/cmp "$@"\nresult=$?\n'
                           "printf 'actual stdout\\000tail'\nprintf 'actual stderr\\377tail' >&2\nexit \"$result\"\n")
        wrapper.chmod(0o755)
        put, execute = owner.put_blob, owner.capture_process
        completed = []
        def real_child(*args):
            result = execute(*args)
            completed.append(result)
            return result
        def failed_cas(*args):
            if completed:
                raise OSError(errno.EIO, "post-child CAS read failure control")
            return put(*args)
        owner.capture_process, owner.put_blob = real_child, failed_cas
        cwd, path = Path.cwd(), os.environ["PATH"]
        try:
            os.chdir(self.fixture.repo)
            os.environ["PATH"] = str(commands) + os.pathsep + path
            result = owner.event(capture, "cmp:IMPLEMENTAUDIT.plugin.zip",
                                 ["cmp", "-s", str(work / "out-a/IMPLEMENTAUDIT.plugin.zip"),
                                  str(work / "out-b/IMPLEMENTAUDIT.plugin.zip")])
        finally:
            os.chdir(cwd)
            os.environ["PATH"] = path
            owner.capture_process, owner.put_blob = execute, put
        self.assertEqual(completed[0][0], 0)
        self.assertEqual(result, 125)
        receipt = read_json(capture / "processes/02.json")
        self.assertEqual(receipt["exit_code"], 0)
        self.assertEqual(base64.b64decode(receipt["stdout_base64"]), b"actual stdout\0tail")
        self.assertEqual(base64.b64decode(receipt["stderr_base64"]), b"actual stderr\xfftail")
        self.assertFalse((capture / "events/02.json").exists())
        record = self.fixture.finish_partial(capture, work, code=0)
        self.assertFalse(record["assessment"]["complete"])
        self.assertTrue(record["handoff_failures"])
        # The pre-acquired wrapper executable is retained even though its event
        # could not be handed off; this inventory cannot qualify completion.
        self.assertTrue(record["unhanded_blobs"])
        target = self.copied(capture)
        altered = read_json(target / "record.json")
        altered["unhanded_blobs"] = []
        write_json(target / "record.json", altered)
        with self.assertRaises(owner.ReproCaptureError):
            owner.verify_record(target, require_complete=False)

    def test_process_receipt_identity_shape_raw_result_and_membership_are_bound(self):
        capture, result = self.fixture.run()
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.fixture.owner.verify_record(capture)
        for change in ("missing", "duplicate", "reordered", "foreign-run", "foreign-source", "bad-base64",
                       "exit-bool", "exit-null", "exit-different", "stdout-different", "not-started",
                       "index-bool", "symlink", "mode", "foreign-file", "foreign-handoff", "omitted-reference"):
            with self.subTest(change=change):
                target = self.copied(capture)
                path = target / "processes/02.json"
                item = read_json(path)
                if change == "missing":
                    path.unlink()
                elif change == "symlink":
                    path.unlink()
                    path.symlink_to(capture / "processes/02.json")
                elif change == "mode":
                    path.chmod(0o644)
                elif change == "foreign-file":
                    (target / "processes/unlisted.json").write_text("{}\n")
                elif change == "foreign-handoff":
                    (target / "processes/18.handoff.json").write_text("{}\n")
                elif change == "omitted-reference":
                    record = read_json(target / "record.json")
                    del record["process_results"][2]
                    write_json(target / "record.json", record)
                else:
                    if change == "duplicate":
                        item = read_json(target / "processes/01.json")
                    elif change == "reordered":
                        item["role"] = "cmp:IMPLEMENTAUDIT.skill"
                    elif change == "foreign-run":
                        item["run_id"] = "0" * 32
                    elif change == "foreign-source":
                        item["source_sha256"] = "0" * 64
                    elif change == "bad-base64":
                        item["stdout_base64"] = "?"
                    elif change == "exit-bool":
                        item["exit_code"] = False
                    elif change == "exit-null":
                        item["exit_code"] = None
                    elif change == "exit-different":
                        item["exit_code"] = 1
                    elif change == "stdout-different":
                        item["stdout_base64"] = "eA=="
                    elif change == "not-started":
                        item["dispatch"] = "NOT_STARTED_UNSUPPORTED_INPUT"
                        item["exit_code"] = None
                        item["capture_errors"] = ["UNSUPPORTED_INPUT_KIND:invented:SPECIAL"]
                    else:
                        item["index"] = False
                    self.reseal_process(target, 2, item)
                with self.assertRaises(self.fixture.owner.ReproCaptureError):
                    self.fixture.owner.verify_record(target, require_complete=False)

    def test_two_maximum_raw_streams_have_explicit_json_and_aggregate_bounds(self):
        import base64
        capture, work = self.fixture.prefix()
        owner = self.fixture.owner
        commands = self.fixture.base / "large-commands"
        commands.mkdir()
        wrapper = commands / "cmp"
        wrapper.write_text('#!/usr/bin/env python\nimport subprocess,sys\n'
                           'result=subprocess.run(["/usr/bin/cmp", *sys.argv[1:]])\n'
                           f'sys.stdout.buffer.write(b"x" * {owner.MAX_STREAM})\n'
                           f'sys.stderr.buffer.write(b"y" * {owner.MAX_STREAM})\n'
                           'raise SystemExit(result.returncode)\n')
        wrapper.chmod(0o755)
        result = self.fixture.compare(capture, work, env=dict(self.fixture.env,
                                      PATH=str(commands) + os.pathsep + self.fixture.env["PATH"]))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(result.stdout), owner.MAX_STREAM)
        self.assertEqual(len(result.stderr), owner.MAX_STREAM)
        path = capture / "processes/02.json"
        self.assertGreater(path.stat().st_size, owner.MAX_FILE)
        self.assertLessEqual(path.stat().st_size, owner.MAX_PROCESS_JSON)
        record = self.fixture.finish_partial(capture, work)
        self.assertFalse(record["assessment"]["complete"])
        total = sum(path.stat().st_size for folder in ("blobs", "processes") for path in (capture / folder).iterdir())
        limit = owner.MAX_TOTAL
        try:
            owner.MAX_TOTAL = total - 1
            with self.assertRaises(owner.ReproCaptureError):
                owner.verify_record(capture, require_complete=False)
        finally:
            owner.MAX_TOTAL = limit
        item = read_json(path)
        item["stdout_base64"] = base64.b64encode(b"x" * (owner.MAX_STREAM + 1)).decode()
        self.reseal_process(capture, 2, item)
        with self.assertRaises(owner.ReproCaptureError):
            owner.verify_record(capture, require_complete=False)

    def test_observed_fifo_operand_is_refused_before_child_dispatch(self):
        import signal
        capture, work = self.fixture.prefix()
        left = work / "out-a/IMPLEMENTAUDIT.plugin.zip"
        right = work / "out-b/IMPLEMENTAUDIT.plugin.zip"
        right.unlink()
        os.mkfifo(right)
        argv = ["python", str(self.fixture.repo / "scripts/repro-event-capture.py"), "event", str(capture),
                "cmp:IMPLEMENTAUDIT.plugin.zip", "--", "cmp", "-s", str(left), str(right)]
        process = subprocess.Popen(argv, cwd=self.fixture.repo, env=self.fixture.env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            _, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            _, stderr = process.communicate()
        self.assertFalse(timed_out, "observed FIFO was dispatched and needed an external watchdog")
        self.assertEqual(process.returncode, 125, stderr.decode(errors="replace"))
        receipt = read_json(capture / "processes/02.json")
        self.assertEqual(receipt["dispatch"], "NOT_STARTED_UNSUPPORTED_INPUT")
        self.assertIsNone(receipt["exit_code"])
        event = read_json(capture / "events/02.json")
        self.assertIsNone(event["exit_code"])
        self.assertTrue(any("UNSUPPORTED_INPUT_KIND" in error for error in event["capture_errors"]))
        record = self.fixture.finish_partial(capture, work)
        self.assertFalse(record["assessment"]["complete"])


class Lifecycle(unittest.TestCase):
    def test_original_consumers_and_inputs_survive_cleanup(self):
        """Deleting capture at the original producer sites loses these inputs."""
        evidence = os.environ.get("R0035_REPRO_CASE_ARTIFACTS")
        with tempfile.TemporaryDirectory(prefix="repro-c5-case-", dir="/tmp") as temporary:
            target = Path(temporary)
            capture = target / "capture"
            env = dict(os.environ, R0035_REPRO_EVENT_CAPTURE_DIR=str(capture),
                       PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(["bash", "tests/reproducible-release-asset.test.sh"],
                                    cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            (target / "stdout.bin").write_bytes(result.stdout)
            (target / "stderr.bin").write_bytes(result.stderr)
            (target / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
            if evidence:
                shutil.copytree(target, evidence, dirs_exist_ok=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertTrue((capture / "record.json").is_file(),
                            "original consumers ran, but their actual inputs/results were lost at EXIT cleanup")
            owner = load_owner()
            record = owner.verify_record(capture)
            self.assertTrue(record["assessment"]["complete"])
            self.assertEqual(len(record["events"]), 19)


if __name__ == "__main__":
    unittest.main()
