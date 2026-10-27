#!/usr/bin/env python3
"""Finite registry membership controls; no native or canonical reuse claim."""
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("registry_qualifier", ROOT / "scripts/qualify-work-graph-verifier.py")
Q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Q)
WG = Q.WG
REGISTRY_NODE = "COMMAND:scripts/check-validation-registry.sh:0"
REGISTRY_SHA = "c7c6b0f26111c44c4caaf5e1ffc20979e48cc15ca83600f3fea16514e9d02fee"
SCOPE = "CONTROLLED_TASK_REGISTRY_V1"


def registry_population(registry):
    """Describe the selected source; historical denominators are not defaults."""
    tests = WG.verifier_registered_tests_v1(registry)
    graph = WG.compile_verifier_graph_v1(registry, tests, {})
    return dict(registry_sha256=Q.sha(registry), nodes=len(graph["nodes"]),
                registered_tests=len(tests), test_paths=tests)


def require_registry_output(raw, population):
    expected = ("check-validation-registry: ok (%d tests; one canonical CI route)\n" %
                population["registered_tests"]).encode()
    assert raw == expected, (raw, expected)


def require_registry_members(members, population):
    expected = sorted("/work/" + path for path in population["test_paths"])
    assert sorted(member["path"] for member in members) == expected
    assert all(member["bytes"] == 0 for member in members)


class AdmissionCases(unittest.TestCase):
    def setUp(self):
        self.registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        self.graph = WG.compile_verifier_graph_v1(self.registry, WG.verifier_registered_tests_v1(self.registry), {})
        self.inputs = {"COMMAND:" + name + ":0": dict(program_sha256=contract["sha256"], image_digest="a" * 64)
                       for name, contract in WG.VERIFIER_LEAF_CONTRACTS_V1.items()}

    def request(self, scope, inputs):
        return dict(schema="implementaudit.verifier-acquisition.v1", scope=scope, binding={}, inputs=inputs)

    def test_default_scope_still_admits_only_original_two_leaves(self):
        acquired = self.request("CONTROLLED_TASK_LEAVES_V1", self.inputs)
        plan = WG.compile_verifier_reuse_v1(self.graph, self.registry, acquired, {})
        self.assertEqual(len(plan["nodes"]), 2)
        self.assertNotIn(REGISTRY_NODE, [n["node"] for n in plan["nodes"]])
        self.inputs[REGISTRY_NODE] = dict(program_sha256=REGISTRY_SHA, image_digest="b" * 64)
        with self.assertRaises(WG.WorkGraphError):
            WG.compile_verifier_reuse_v1(self.graph, self.registry, acquired, {})

    def test_explicit_scope_connects_original_registry_node_to_reuse_decision(self):
        self.inputs[REGISTRY_NODE] = dict(program_sha256=REGISTRY_SHA, image_digest="b" * 64)
        acquired = self.request(SCOPE, self.inputs)
        try:
            first = WG.compile_verifier_reuse_v1(self.graph, self.registry, acquired, {})
        except WG.WorkGraphError as exc:
            self.fail("explicit original registry consumer is unavailable: " + str(exc))
        self.assertEqual(len(first["nodes"]), 3)
        self.assertEqual(first["nodes"][-1]["node"], REGISTRY_NODE)
        self.assertEqual(first["nodes"][-1]["decision"], "EXECUTE")
        issued = {n["node"]: n["key"] for n in first["nodes"]}
        again = WG.compile_verifier_reuse_v1(self.graph, self.registry, acquired, issued)
        self.assertEqual([n["decision"] for n in again["nodes"]], ["CONSUME_PRIOR_SUCCESS"] * 3)
        self.inputs[REGISTRY_NODE]["image_digest"] = "c" * 64
        changed = WG.compile_verifier_reuse_v1(self.graph, self.registry, acquired, issued)
        self.assertEqual([n["decision"] for n in changed["nodes"]], ["CONSUME_PRIOR_SUCCESS", "CONSUME_PRIOR_SUCCESS", "EXECUTE"])
        # Original117 is a retained acceptance subject, not the size of every
        # future combined registry. Account for this source's whole population.
        self.assertEqual(first["omitted_canonical_nodes"] + 3, len(self.graph["nodes"]))
        self.assertGreater([n["id"] for n in self.graph["nodes"]].index(REGISTRY_NODE), 22)

    def test_foreign_checker_and_incomplete_population_refuse(self):
        self.inputs[REGISTRY_NODE] = dict(program_sha256="f" * 64, image_digest="b" * 64)
        with self.assertRaises(WG.WorkGraphError):
            WG.compile_verifier_reuse_v1(self.graph, self.registry, self.request(SCOPE, self.inputs), {})
        del self.inputs[REGISTRY_NODE]
        with self.assertRaises(WG.WorkGraphError):
            WG.compile_verifier_reuse_v1(self.graph, self.registry, self.request(SCOPE, self.inputs), {})

    def test_unhashable_scope_refuses_as_a_contract_error(self):
        with self.assertRaises(WG.WorkGraphError):
            WG.compile_verifier_reuse_v1(self.graph, self.registry, self.request({}, self.inputs), {})


class PopulationCases(unittest.TestCase):
    def test_current_population_accepts_actual_checker_and_exact_members(self):
        population = registry_population((ROOT / "scripts/verify-package.sh").read_bytes())
        result = subprocess.run(["bash", str(ROOT / "scripts/check-validation-registry.sh")],
                                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        require_registry_output(result.stdout, population)
        members = [{"path": "/work/tests/" + p.name, "bytes": 0}
                   for p in (ROOT / "tests").glob("*.test.sh")]
        require_registry_members(members, population)
        self.assertEqual(population["registered_tests"], len(members))

    def test_original117_population_retains_its_89_test_contract(self):
        raw = (ROOT / "test-support/work-graph-registry/original117/verify-package.sh").read_bytes()
        population = registry_population(raw)
        self.assertEqual((population["nodes"], population["registered_tests"]), (117, 89))
        require_registry_output(b"check-validation-registry: ok (89 tests; one canonical CI route)\n", population)

    def test_changed_population_is_derived_instead_of_assuming_91(self):
        raw = (ROOT / "scripts/verify-package.sh").read_bytes()
        current = registry_population(raw)
        changed = registry_population(raw.replace(b"\ngit diff --check\n",
            b"\nbash tests/selected-extra.test.sh\ngit diff --check\n"))
        self.assertEqual(changed["registered_tests"], current["registered_tests"] + 1)
        self.assertEqual(changed["nodes"], current["nodes"] + 1)
        self.assertNotEqual(changed["registry_sha256"], current["registry_sha256"])
        with self.assertRaises(AssertionError):
            require_registry_output(
                ("check-validation-registry: ok (%d tests; one canonical CI route)\n" %
                 current["registered_tests"]).encode(), changed)

    def test_same_count_foreign_member_and_stale_output_refuse(self):
        population = registry_population((ROOT / "scripts/verify-package.sh").read_bytes())
        members = [{"path": "/work/" + p, "bytes": 0} for p in population["test_paths"]]
        members[0]["path"] = "/work/tests/foreign.test.sh"
        with self.assertRaises(AssertionError):
            require_registry_members(members, population)
        with self.assertRaises(AssertionError):
            require_registry_output(
                ("check-validation-registry: ok (%d tests; one canonical CI route)\n" %
                 (population["registered_tests"] + 1)).encode(), population)


class MembershipCases(unittest.TestCase):
    def setUp(self):
        try:
            Q.require_source_descriptor_api()
        except WG.WorkGraphError as exc:
            self.skipTest(str(exc))
        self.temp = tempfile.TemporaryDirectory(prefix="r0035-registry-unit-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.tests = self.root / "tests"
        self.tests.mkdir()

    def acquire(self):
        method = getattr(Q, "registry_membership_v1", None)
        self.assertTrue(callable(method), "closed actual registry membership acquirer is missing")
        return method(self.root)

    def test_matching_untracked_and_hidden_names_are_acquired_without_contents(self):
        for name in ("z.test.sh", ".hidden.test.sh", "a.test.sh", "not-a-test.py"):
            (self.tests / name).write_text("not executable test content\n")
        result = self.acquire()
        self.assertEqual(result["entries"], {".hidden.test.sh": "FILE", "a.test.sh": "FILE", "z.test.sh": "FILE"})
        self.assertEqual(result["observation"], "IMMEDIATE_GLOB_NAMES_ONLY_NO_CONTENT_READS")
        (self.tests / "z.test.sh").write_text("different contents\n")
        self.assertEqual(self.acquire(), result)
        (self.tests / "later.test.sh").write_text("")
        self.assertNotEqual(self.acquire(), result)
        (self.tests / "later.test.sh").unlink()
        self.assertEqual(self.acquire(), result)

    def test_empty_glob_is_acquired_as_empty_not_absent(self):
        self.assertEqual(self.acquire()["entries"], {})
        self.tests.rmdir()
        with self.assertRaises((OSError, WG.WorkGraphError)):
            self.acquire()

    def test_matching_directory_is_refused_instead_of_silently_omitted(self):
        (self.tests / "directory.test.sh").mkdir()
        with self.assertRaisesRegex(WG.WorkGraphError, "ordinary file"):
            self.acquire()

    def test_matching_symlink_and_fifo_refuse_without_target_reads(self):
        outside = Path(self.temp.name) / "outside"
        outside.write_text("private target content")
        link = self.tests / "linked.test.sh"
        link.symlink_to(outside)
        with self.assertRaisesRegex(WG.WorkGraphError, "ordinary file"):
            self.acquire()
        link.unlink()
        os.mkfifo(link)
        with self.assertRaisesRegex(WG.WorkGraphError, "ordinary file"):
            self.acquire()

    def test_nonmatching_special_entry_is_not_a_glob_input(self):
        os.mkfifo(self.tests / "irrelevant.pipe")
        self.assertEqual(self.acquire()["entries"], {})

    def test_source_or_tests_symlink_ancestor_refuses(self):
        actual = self.root / "actual-tests"
        self.tests.rename(actual)
        self.tests.symlink_to(actual, target_is_directory=True)
        with self.assertRaises((OSError, WG.WorkGraphError)):
            self.acquire()
        self.tests.unlink()
        actual.rename(self.tests)
        linked = Path(self.temp.name) / "linked-source"
        linked.symlink_to(self.root, target_is_directory=True)
        method = getattr(Q, "registry_membership_v1", None)
        self.assertTrue(callable(method))
        with self.assertRaises((OSError, WG.WorkGraphError)):
            method(linked)

    def test_parent_traversal_alias_refuses_before_normalization_or_open(self):
        left, right = Path(self.temp.name) / "left", Path(self.temp.name) / "right"
        for root, name in ((left, "lexical.test.sh"), (right, "resolved.test.sh")):
            (root / "target/tests").mkdir(parents=True)
            (root / "target/tests" / name).touch()
        (right / "child").mkdir()
        (left / "link").symlink_to(right / "child", target_is_directory=True)
        supplied = left / "link/../target"
        self.assertEqual(Path(os.path.abspath(supplied)), left / "target")
        self.assertEqual(supplied.resolve(), right / "target")
        self.assertEqual([p.name for p in (supplied / "tests").glob("*.test.sh")], ["resolved.test.sh"])
        with self.assertRaisesRegex(WG.WorkGraphError, "parent traversal"):
            Q.registry_membership_v1(supplied)
        for operation in (lambda: Q.registry_membership_v1(supplied),
                          lambda: Q.RegistryVerifierTaskSession(supplied, Path(self.temp.name) / "evidence")):
            with mock.patch.object(Q.os, "open", wraps=os.open) as opened, \
                    mock.patch.object(Q.os.path, "abspath", wraps=os.path.abspath) as normalized:
                with self.assertRaisesRegex(WG.WorkGraphError, "parent traversal"):
                    operation()
                opened.assert_not_called()
                normalized.assert_not_called()

    def test_population_limit_refuses_before_unbounded_projection(self):
        for i in range(4097):
            (self.tests / ("%04d.test.sh" % i)).touch()
        with self.assertRaisesRegex(WG.WorkGraphError, "bound"):
            self.acquire()

    def test_source_depth_bound_admits_128_and_refuses_129_before_open(self):
        root = self.root
        while len(root.parts) - 1 < 128:
            root = root / "d"
            root.mkdir()
        (root / "tests").mkdir()
        self.assertEqual(Q.registry_membership_v1(root)["entries"], {})
        beyond = root / "d"
        beyond.mkdir()
        (beyond / "tests").mkdir()
        with self.assertRaisesRegex(WG.WorkGraphError, "source path bound"):
            Q.registry_membership_v1(beyond)
        with mock.patch.object(Q.os, "open", wraps=os.open) as opened:
            with self.assertRaisesRegex(WG.WorkGraphError, "source path bound"):
                Q.registry_membership_v1(beyond)
            opened.assert_not_called()

    def test_source_byte_bound_admits_4096_and_refuses_4097_before_open(self):
        def actual_root(byte_length):
            # Descriptor-relative creation permits a real long directory chain
            # without substituting the host's single-syscall PATH_MAX refusal.
            remaining = byte_length - len(str(self.root).encode("utf-8"))
            components = []
            fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                while remaining:
                    size = min(200, remaining - 1)
                    if remaining - size - 1 == 1:
                        size -= 1
                    name = "b" * size
                    try:
                        os.mkdir(name, dir_fd=fd)
                    except FileExistsError:
                        pass
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)
                    os.close(fd)
                    fd = child
                    components.append(name)
                    remaining -= size + 1
                os.mkdir("tests", dir_fd=fd)
            finally:
                os.close(fd)
            result = self.root.joinpath(*components)
            self.assertEqual(len(str(result).encode("utf-8")), byte_length)
            return result
        root, beyond = actual_root(4096), actual_root(4097)
        self.assertEqual(Q.registry_membership_v1(root)["entries"], {})
        with self.assertRaisesRegex(WG.WorkGraphError, "source path bound"):
            Q.registry_membership_v1(beyond)
        with mock.patch.object(Q.os, "open", wraps=os.open) as opened:
            with self.assertRaisesRegex(WG.WorkGraphError, "source path bound"):
                Q.registry_membership_v1(beyond)
            opened.assert_not_called()

    def test_population_mutation_during_enumeration_refuses(self):
        (self.tests / "one.test.sh").touch()
        original = os.scandir
        fired = False
        @contextmanager
        def change(fd):
            nonlocal fired
            with original(fd) as entries:
                yield entries
            if not fired:
                fired = True
                (self.tests / "late.test.sh").touch()
        with mock.patch.object(Q.os, "scandir", change):
            with self.assertRaisesRegex(WG.WorkGraphError, "changed"):
                self.acquire()

    def test_tests_directory_replacement_during_enumeration_refuses(self):
        (self.tests / "one.test.sh").touch()
        original = os.scandir
        fired = False
        @contextmanager
        def change(fd):
            nonlocal fired
            with original(fd) as entries:
                yield entries
            if not fired:
                fired = True
                self.tests.rename(self.root / "old-tests")
                self.tests.mkdir()
                (self.tests / "one.test.sh").touch()
        with mock.patch.object(Q.os, "scandir", change):
            with self.assertRaisesRegex(WG.WorkGraphError, "changed"):
                self.acquire()

    def test_source_ancestor_replacement_during_enumeration_refuses(self):
        original = os.scandir
        fired = False
        @contextmanager
        def change(fd):
            nonlocal fired
            with original(fd) as entries:
                yield entries
            if not fired:
                fired = True
                self.root.rename(Path(self.temp.name) / "old-source")
                self.root.mkdir()
                self.tests.mkdir()
        with mock.patch.object(Q.os, "scandir", change):
            with self.assertRaisesRegex(WG.WorkGraphError, "changed"):
                self.acquire()

    def test_member_replacement_between_censuses_refuses(self):
        member = self.tests / "one.test.sh"
        member.touch()
        original = os.scandir
        count = 0
        @contextmanager
        def change(fd):
            nonlocal count
            with original(fd) as entries:
                yield entries
            count += 1
            if count == 2:
                member.unlink()
                member.symlink_to("/no-target")
        with mock.patch.object(Q.os, "scandir", change):
            with self.assertRaisesRegex(WG.WorkGraphError, "changed"):
                self.acquire()

    def test_exact_entry_bound_is_admitted(self):
        for i in range(4096):
            (self.tests / ("%04d.test.sh" % i)).touch()
        self.assertEqual(len(self.acquire()["entries"]), 4096)


class ImageCases(unittest.TestCase):
    acquire = MembershipCases.acquire

    def setUp(self):
        MembershipCases.setUp(self)
        if Q.platform.system() != "Linux" or Q.platform.machine() != "x86_64" or Q.fcntl is None or not all(
                hasattr(Q.fcntl, name) for name in ("F_ADD_SEALS", "F_SEAL_WRITE", "F_SEAL_GROW", "F_SEAL_SHRINK", "F_SEAL_SEAL")):
            self.skipTest("finite image requires supported Linux memfd sealing runtime")

    def test_empty_glob_materializes_real_declared_directory(self):
        session = Q.RegistryVerifierTaskSession(self.root, Path(self.temp.name) / "evidence")
        membership = self.acquire()
        manifest, key = session._image({"/work/checker": (b"", 0o444)}, {}, membership)
        self.assertIn("/work/tests", manifest["directories"])
        self.assertEqual(manifest["directory_membership"]["entries"], {})
        self.assertFalse(any(row["path"].startswith("/work/tests/") for row in manifest["files"]))
        self.assertEqual(Q.sha((session.output / "objects" / key).read_bytes()), key)


def live_controls(destination):
    """Explicit real no-proc qualification; never invoked by the canonical bank."""
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    rows = []
    def retain(name, value):
        data = value if isinstance(value, bytes) else WG.canonical_json_v1(value) + b"\n"
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    def command(argv, cwd):
        index = len(list((destination / "setup").glob("*"))) if (destination / "setup").exists() else 0
        path = "setup/%02d" % index
        result = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retain(path + "/command.json", dict(argv=argv, cwd=str(cwd), exit=result.returncode))
        retain(path + "/stdout", result.stdout)
        retain(path + "/stderr", result.stderr)
        if result.returncode:
            raise AssertionError((argv, result.returncode, result.stderr))
        return result.stdout
    source = destination / "source"
    command(["git", "clone", "--no-hardlinks", "--no-checkout", str(ROOT), str(source)], ROOT)
    head = command(["git", "rev-parse", "HEAD"], ROOT).decode().strip()
    command(["git", "checkout", "--detach", head], source)
    changed = command(["git", "diff", "--name-only", "--diff-filter=ACMRT", "HEAD"], ROOT).decode().splitlines()
    changed += command(["git", "ls-files", "--others", "--exclude-standard"], ROOT).decode().splitlines()
    for name in changed:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    initial_diff = command(["git", "diff", "--binary", "HEAD"], source)
    retain("candidate.patch", initial_diff)
    population = registry_population((source / "scripts/verify-package.sh").read_bytes())
    retain("selected-registry.json", population)
    retain("invocation.json", dict(argv=[sys.executable, "-B", str(Path(__file__).resolve()), "--live", str(destination)],
        source=str(source), head=head, registry_sha256=population["registry_sha256"],
        engine=Q.sha(Q.LOADED_DRIVER), compiler=Q.sha(Q.LOADED_COMPILER), harness=Q.sha(Path(__file__).read_bytes()),
        scope=SCOPE, authority="NONE", original_node=REGISTRY_NODE, canonical_acceptance="UNQUALIFIED"))
    session = Q.RegistryVerifierTaskSession(source, destination / "consumer")
    def record(label, **extra):
        row = dict(control=label, **extra)
        rows.append(row)
        with (destination / "controls.jsonl").open("ab") as stream:
            stream.write(WG.canonical_json_v1(row) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        print("registry control %02d: %s" % (len(rows), label), flush=True)
    def run(label, expected, code=0, current=session):
        prior = current.dispatch_count
        result = current.run()
        assert result["scope"] == current.SCOPE
        assert result["exit"] == code, (label, result)
        assert [n["disposition"] for n in result["nodes"]] == expected, (label, result)
        assert current.dispatch_count - prior == expected.count("EXECUTED")
        generation = current.output / ("generation-%06d" % result["generation"])
        assert json.loads((generation / "result.json").read_bytes()) == result
        for stream in ("stdout", "stderr"):
            assert (generation / (stream + ".log")).read_bytes() == b"".join(
                (Path(n["evidence_directory"]) / (stream + ".log")).read_bytes() for n in result["nodes"])
        for node in result["nodes"]:
            assert int((Path(node["evidence_directory"]) / "exit-code.txt").read_text()) == node["exit"]
        record(label, result=result, dispatch_delta=current.dispatch_count - prior)
        return result
    def refuse(label, action, contains):
        prior = session.dispatch_count
        try:
            action()
        except (OSError, WG.WorkGraphError) as exc:
            assert contains in str(exc), (label, str(exc))
            assert session.dispatch_count == prior
            record(label, refusal=str(exc), dispatch_delta=0)
        else:
            raise AssertionError("expected refusal: " + label)
    def registry_stderr(result):
        return (Path(result["nodes"][-1]["evidence_directory"]) / "stderr.log").read_bytes()
    baseline = run("selected registry three leaves execute", ["EXECUTED"] * 3)
    raw = (Path(baseline["nodes"][-1]["evidence_directory"]) / "stdout.log").read_bytes()
    require_registry_output(raw, population)
    unchanged = run("unchanged live receipts reused", ["REUSED"] * 3)
    assert [n["receipt_digest"] for n in baseline["nodes"]] == [n["receipt_digest"] for n in unchanged["nodes"]]
    old_receipts = [n["receipt_digest"] for n in baseline["nodes"][:2]]
    mutation = source / "tests/.r0035-untracked.test.sh"
    mutation.write_text("name only; this body is never executed\n")
    failed = run("untracked hidden matching name invalidates only registry", ["REUSED", "REUSED", "EXECUTED"], 1)
    assert registry_stderr(failed) == b"tests/.r0035-untracked.test.sh is not invoked by scripts/verify-package.sh\n"
    assert [n["receipt_digest"] for n in failed["nodes"][:2]] == old_receipts
    run("failed registry result cannot be reused", ["REUSED", "REUSED", "EXECUTED"], 1)
    mutation.unlink()
    run("membership restoration executes fresh successful registry", ["REUSED", "REUSED", "EXECUTED"])
    ci = source / ".github/workflows/validate.yml"
    ci_before = ci.read_bytes()
    retain("preimages/validate.yml", ci_before)
    ci.write_bytes(ci_before + b"\n        run: bash tests/agents-bootstrap-budget.test.sh\n")
    failed = run("CI text mutation invalidates only registry", ["REUSED", "REUSED", "EXECUTED"], 1)
    assert b"directly invoked" in registry_stderr(failed)
    assert [n["receipt_digest"] for n in failed["nodes"][:2]] == old_receipts
    ci.write_bytes(ci_before)
    restored = run("CI restoration requires successful fresh registry", ["REUSED", "REUSED", "EXECUTED"])
    mutation.mkdir()
    refuse("matching directory refuses before launch", session.run, "ordinary file")
    mutation.rmdir()
    restored = run("restored unsupported member preserves valid receipt", ["REUSED"] * 3)
    image_path = Path(restored["nodes"][-1]["evidence_directory"]) / "image.json"
    image_raw = image_path.read_bytes()
    image_key = Q.sha(image_raw)
    manifest = json.loads(image_raw)
    assert manifest["namespace"] == "UNSHARE_ALL_NO_PROC_NO_GENERAL_DEV_NO_HOST_ROOT"
    assert manifest["directory_membership"]["observation"] == "IMMEDIATE_GLOB_NAMES_ONLY_NO_CONTENT_READS"
    assert "/work/tests" in manifest["directories"]
    test_members = [m for m in manifest["files"] if m["path"].startswith("/work/tests/")]
    require_registry_members(test_members, population)
    assert image_key in session._issued[REGISTRY_NODE]["required_objects"]
    (session.output / "objects" / image_key).unlink()
    replay = run("missing membership image object rejects prior receipt", ["REUSED", "REUSED", "EXECUTED"])
    assert REGISTRY_NODE in replay["refused_cached_outputs"]
    receipt_path = Path(replay["nodes"][-1]["evidence_directory"]) / "receipt.json"
    receipt_before = receipt_path.read_bytes()
    retain("preimages/receipt.json", receipt_before)
    receipt_path.write_bytes(receipt_before + b"changed\n")
    replay = run("tampered registry receipt rejected before reuse", ["REUSED", "REUSED", "EXECUTED"])
    assert REGISTRY_NODE in replay["refused_cached_outputs"]
    # Default profile remains its independent historical two-command API.
    default = Q.VerifierTaskSession(source, destination / "default-consumer")
    run("default API executes exactly two original leaves", ["EXECUTED"] * 2, current=default)
    # A separate acquired zero-name image reaches the unchanged checker's own failure.
    empty_source = destination / "empty-source"
    command(["git", "clone", "--no-hardlinks", str(source), str(empty_source)], destination)
    for name in changed:
        target = empty_source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    for path in (empty_source / "tests").glob("*.test.sh"):
        path.unlink()
    empty = Q.RegistryVerifierTaskSession(empty_source, destination / "empty-consumer")
    result = run("empty acquired glob executes original negative", ["EXECUTED"] * 3, 1, current=empty)
    assert registry_stderr(result) == b"no tests/*.test.sh found\n"
    assert REGISTRY_NODE not in empty._issued
    assert command(["git", "diff", "--binary", "HEAD"], source) == initial_diff
    assert not mutation.exists()
    assert registry_population((source / "scripts/verify-package.sh").read_bytes()) == population
    record("candidate restored after all mutations", source_patch_sha256=Q.sha(initial_diff))
    retain("summary.json", dict(scope=SCOPE, controls=len(rows), passed=True, source_head=head,
        actual_selected_registry_execution=True, canonical_acceptance="UNQUALIFIED", authority="NONE",
        selected_registry=population, admitted_scope_nodes=3,
        historical_original_contract=dict(nodes=117, registered_tests=89,
            qualification="NOT_ESTABLISHED_BY_SELECTED_CURRENT_RUN"),
        actual_native_execution=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--live":
        raise SystemExit(live_controls(Path(sys.argv[2]).absolute()))
    unittest.main(verbosity=2)
