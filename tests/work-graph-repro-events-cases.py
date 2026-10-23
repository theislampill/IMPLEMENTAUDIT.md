#!/usr/bin/env python3
"""Executable controls for the opt-in, repo-only C5 reproduction event owner."""

import json
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
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
        self.assertEqual([row["role"] for row in events], EXPECTED_ROLES)
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
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
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
            self.reseal(target, index, rewrite(read_json(target / "events" / f"{index:02d}.json")))
        closing = rewrite(read_json(target / "close.json"))
        write_json(target / "close.json", closing)
        record = read_json(target / "record.json")
        record["close_sha256"] = hashlib.sha256((target / "close.json").read_bytes()).hexdigest()
        write_json(target / "record.json", record)
        (target / "blobs" / old["sha256"]).unlink()
        with self.assertRaises(self.fixture.owner.ReproCaptureError):
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
        self.assertEqual(result.returncode, 0)
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
