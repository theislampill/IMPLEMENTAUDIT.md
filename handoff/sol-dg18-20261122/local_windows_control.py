"""Receive historical A4 source and run a bounded ordinary Windows control."""

import ast
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[2]
BASE = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
TREE = "9c3913ceaa95f3f36b0377fe2dba4a302afcba89"
CARRIER = (
    "6431a1d1e067ab37e4f461caa4a61890d69e7c14:handoff/"
    "pro-executor-results-20261115/continuing-execution-20261122-42-qualifications/"
    "SOURCE_AND_CUSTODY_EVIDENCE.zip"
)
PREFIX = "results42-staging/evidence/dg18-source-recovery/source/"
FIXTURES = ROOT / "fixtures/canonical-state-rotation"
ORDINALS = (1, 3, 5, 7, 12, 14, 19, 20, 21)
DRAFT_GUARD = 67_108_864


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15)


def indexed_inputs():
    require(git("rev-parse", BASE + "^{tree}").decode().strip() == TREE, "base tree drift")
    carrier = git("cat-file", "blob", CARRIER)
    with zipfile.ZipFile(io.BytesIO(carrier)) as zip_file:
        names = zip_file.namelist()
        require(len(names) == len(set(names)), "duplicate carrier names")
        index_raw = zip_file.read(PREFIX + "RECOVERED_28_SOURCE_INDEX.json")
        capture_raw = zip_file.read(PREFIX + "capture06.py")
        source_manifest = json.loads(zip_file.read(PREFIX + "READ_ONLY_RECOVERY_MANIFEST.json"))
        for name, raw in (("RECOVERED_28_SOURCE_INDEX.json", index_raw), ("capture06.py", capture_raw)):
            selected, = (item for item in source_manifest["members"] if item["path"] == name)
            require((selected["bytes"], selected["sha256"], selected["git_blob"])
                    == (len(raw), sha256(raw), blob(raw)), "recovered member identity drift")
    index = json.loads(index_raw)
    statements = ast.parse(capture_raw).body
    methods, = (ast.literal_eval(statement.value) for statement in statements
                if isinstance(statement, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "ORIGINAL_METHODS"
                        for target in statement.targets))
    require([list(item) for item in methods] == index["declared_method_order"] and len(methods) == 28,
            "ordered method denominator drift")
    require((index["source"], index["tree"], index["source_member_count"]) == (BASE, TREE, 52),
            "source index identity drift")
    require(index["frozen_R01_R09_recovered"] is False, "unexpected receiving-contract claim")
    return index["source_members"], methods, {
        "carrier_git_blob": blob(carrier), "carrier_sha256": sha256(carrier),
        "capture06_sha256": sha256(capture_raw), "method_index_sha256": sha256(index_raw),
    }


def verify_source(rows):
    paths = [row["path"] for row in rows]
    require(len(paths) == len(set(paths)) == 52, "source-path denominator drift")
    raw_tree = git("ls-tree", "-z", BASE, "--", *paths).decode("utf-8")
    tree = dict(entry.split("\t", 1)[::-1] for entry in raw_tree.strip("\0").split("\0"))
    for row in rows:
        name = row["path"]
        require(name in tree and tree[name].split() == [row["mode"], "blob", row["git_blob"]],
                f"immutable tree mismatch: {name}")
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT) and path.is_file()
                and blob(path.read_bytes()) == row["git_blob"], f"worktree byte mismatch: {name}")


class OrderedResult(unittest.TestResult):
    def __init__(self, peak):
        super().__init__()
        self.peak = peak
        self.observations = []

    def startTest(self, test):
        super().startTest(test)
        self.observations.append({"test": test.id(), "pid": os.getpid(), "before_bytes": self.peak(),
                                  "started_ns": time.perf_counter_ns(), "outcome": "INCOMPLETE"})

    def stopTest(self, test):
        row = self.observations[-1]
        row["elapsed_ms"] = (time.perf_counter_ns() - row.pop("started_ns")) / 1_000_000
        row["after_bytes"] = self.peak()
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.observations[-1]["outcome"] = "PASS"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record_error("FAILURE", err)

    def addError(self, test, err):
        super().addError(test, err)
        self.record_error("ERROR", err)

    def record_error(self, outcome, err):
        line = traceback.extract_tb(err[2])[-1]
        self.observations[-1].update(
            outcome=outcome, error_type=err[0].__name__,
            error_at=f"{Path(line.filename).name}:{line.lineno}",
            guard_refusal=str(err[1]) == "process peak memory exceeds frozen bound; no publication authorised",
        )

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.observations[-1].update(outcome="SKIP", skip=reason)


def check_guard(projection):
    try:
        projection._check_memory_budget()
    except projection.RotationError as error:
        return str(error)
    return "PASS"


def run(complete):
    require(os.name == "nt" and not sys.flags.optimize, "requires unoptimized ordinary Windows Python")
    require(Path.cwd() == ROOT, "invoke from the owned worktree")
    rows, methods, historical = indexed_inputs()
    verify_source(rows)
    sys.path.insert(0, str(FIXTURES))
    custody_tests = importlib.import_module("windows_custody_test")
    projection = custody_tests.load("rotate-canonical-state")
    custody = projection._WINDOWS
    require(custody is not None and projection.calibration_contract_v1()["maximum_memory_bytes"] == DRAFT_GUARD,
            "actual Windows guard is unavailable")
    before = {"peak_bytes": custody.peak_process_memory(), "guard": check_guard(projection)}
    ordinals = tuple(range(1, len(methods) + 1)) if complete else ORDINALS
    scratch_clear = False
    result = OrderedResult(custody.peak_process_memory)
    git_exe = custody_tests.load("claim-run-rotation").fixed_git()
    git_root = Path(git_exe).parents[2]
    os.environ["PATH"] = os.pathsep.join(map(str, (
        Path(sys.executable).parent, Path(git_exe).parent,
        git_root / "cmd", git_root / "bin", git_root / "usr/bin",
        Path(os.environ["SystemRoot"]) / "System32",
    )))
    fixture_evidence = {}
    with tempfile.TemporaryDirectory(prefix=".d18-", dir=ROOT) as scratch:
        cleanup_root = Path(scratch)
        old_tempdir, tempfile.tempdir = tempfile.tempdir, scratch
        try:
            os.environ["R0039_CLAIM_EVIDENCE_DIR"] = str(cleanup_root / "claim")
            os.environ.pop("R0039_CLAIM_RETAIN_ARTIFACTS", None)
            cases = []
            for ordinal in ordinals:
                file, cls, method = methods[ordinal - 1]
                module = importlib.import_module(Path(file).stem)
                cases.append(getattr(module, cls)(method))
            unittest.TestSuite(cases).run(result)
            names = {path.name for path in cleanup_root.iterdir()}
            receiver = cleanup_root / "claim"
            if receiver.is_dir():
                records = {path.name for path in receiver.iterdir()}
                want = {"candidate-component-corruption.json"}
                scratch_clear = records <= want and (result.observations[-1]["outcome"] != "PASS" or records == want)
                if records == want:
                    raw = (receiver / next(iter(want))).read_bytes()
                    fixture_evidence = {"bytes": len(raw), "sha256": sha256(raw)}
                names.remove("claim")
            else:
                scratch_clear = not complete
            scratch_clear = scratch_clear and not names
        finally:
            tempfile.tempdir = old_tempdir
    after = {"peak_bytes": custody.peak_process_memory(), "guard": check_guard(projection)}
    peaks = [before["peak_bytes"]]
    for ordinal, row in zip(ordinals, result.observations, strict=True):
        row["historical_ordinal"] = ordinal
        peaks.extend((row["before_bytes"], row["after_bytes"]))
    peaks.append(after["peak_bytes"])
    require(peaks == sorted(peaks) and all(type(p) is int and p > 0 for p in peaks),
            "invalid or nonmonotonic native lifetime observations")

    modeled = {}
    for observation in (DRAFT_GUARD, DRAFT_GUARD + 1):
        with patch.object(custody, "peak_process_memory", return_value=observation):
            modeled[str(observation)] = check_guard(projection)
    require(modeled == {
        str(DRAFT_GUARD): "PASS",
        str(DRAFT_GUARD + 1): "process peak memory exceeds frozen bound; no publication authorised",
    }, "modeled unchanged source guard did not discriminate the exact boundary")
    require(check_guard(projection) == after["guard"], "native guard restoration disagrees")
    verify_source(rows)
    clean = not cleanup_root.exists() and scratch_clear
    skips_accepted = all(test.id() == "windows_custody_test.WindowsCustody.test_actual_short_directory_alias_is_refused"
                         and reason == "this volume did not provide a distinct 8.3 alias"
                         for test, reason in result.skipped)
    passed = result.wasSuccessful() and skips_accepted and clean and before["guard"] == after["guard"] == "PASS"
    return {
        "schema": "dg18.ordinary-windows-a4-control.v1",
        "status": "PASS_BOUNDED" if passed else "FAILED_BOUNDED",
        "base": BASE, "tree": TREE, **historical, "source_members_before_after": len(rows),
        "platform": platform.platform(), "python": platform.python_version(),
        "python_executable_sha256": sha256(Path(sys.executable).read_bytes()),
        "owner_git_sha256": sha256(Path(git_exe).read_bytes()),
        "owner_git_version": subprocess.check_output([git_exe, "--version"], timeout=15).decode().strip(),
        "historical_methods": len(methods), "worker_pid": os.getpid(), "observations": result.observations,
        "scope": "LOCAL_ALL_28" if complete else "LOCAL_NINE_METHOD_SUBSET",
        "last_method_fixture_evidence": fixture_evidence or None,
        "metric": "raw lifetime peak working-set bytes from the existing Windows custody owner",
        "before": before, "after": after, "modeled_guard_control": modeled,
        "scratch_clean": clean, "original_host_equivalence_established": False,
        "full_operation_job_memory_or_population_measured": False, "full_A4_accepted": False,
    }


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--complete"]):
        raise SystemExit("usage: local_windows_control.py [--complete]")
    evidence = run(complete=sys.argv[1:] == ["--complete"])
    print(json.dumps(evidence, indent=2, ensure_ascii=True))
    raise SystemExit(evidence["status"] != "PASS_BOUNDED")
