#!/usr/bin/env python3
"""Original58 complete genuine Git/source controls; no native authority."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("retention_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_AUDIT_RETENTION_V1"
ENVIRONMENT = dict(P.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1")
GIT_OWNER = dict(context=Q._preflight_git_context_v1, capture=Q._preflight_git_capture_v1)


class LaunchEncodingCases(unittest.TestCase):
    """Constructed transport controls; no mocked executable success."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.session = Q.VerifierTaskSession(ROOT, self.base / "evidence")

    def image(self, count=2195, compact=True):
        files = {"/work/d%03d/f%04d" % (number % 384, number):
                 (b"captured member " + str(number).encode(),
                  0o555 if number < 62 else 0o600 if compact else 0o444)
                 for number in range(count)}
        manifest, key = self.session._image(files, {})
        if compact:
            manifest["data_permissions"] = "OWNER_0600_READ_ONLY_MOUNT"
            key = self.session._object(self.session._encode(manifest))
        node = dict(id="CONSTRUCTED:closed-image", source="exit 0\n",
                    source_sha256=Q.sha(b"exit 0\n"))
        acquired = dict(images={node["id"]: (files, manifest)}, state={},
            acquired=dict(scope="CONSTRUCTED_TRANSPORT_ONLY",
                inputs={node["id"]: dict(image_digest=key)}))
        return acquired, node, files, manifest

    def test_large_closed_image_fits_without_dropping_any_sealed_member(self):
        acquired, node, files, _ = self.image()
        descriptors = []
        sealed = self.session._sealed
        def retain(raw):
            fd = sealed(raw)
            descriptors.append(fd)
            return fd
        def refuse(argv, **options):
            self.assertEqual(argv[:2], ["/usr/bin/bwrap", "--args"])
            args = os.pread(int(argv[2]), 1024 * 1024, 0).decode().split("\0")[:-1]
            self.assertLessEqual(len(args) + len(argv) - 1, 8500)
            mounted = {}
            for index, token in enumerate(args):
                if token == "--ro-bind-data":
                    fd, path = int(args[index + 1]), args[index + 2]
                    mode = int(args[index - 1], 8) if args[index - 2] == "--perms" else 0o600
                    mounted[path] = (os.pread(fd, len(files[path][0]) + 1, 0), mode)
                    self.assertEqual(Q.fcntl.fcntl(fd, Q.fcntl.F_GET_SEALS), 15)
            self.assertEqual(mounted, files)
            self.assertIn("--unshare-all", args)
            self.assertIn("--remount-ro", args)
            self.assertNotIn("--proc", args)
            self.assertNotIn("--bind", args)
            self.assertNotIn("--ro-bind", args)
            self.assertEqual(set(options["pass_fds"]), set(descriptors))
            raise OSError("constructed terminal launch refusal")
        directory = self.session.output / "constructed"
        with mock.patch.object(self.session, "_sealed", side_effect=retain), mock.patch.object(
                Q.subprocess, "Popen", side_effect=refuse):
            with self.assertRaisesRegex(OSError, "constructed terminal launch refusal"):
                self.session._execute(acquired, node, {"key": "constructed"}, directory)
        for fd in descriptors:
            with self.assertRaises(OSError):
                os.fstat(fd)
        self.assertEqual(self.session.dispatch_count, 0)
        self.assertFalse((directory / "receipt.json").exists())

    def test_compact_policy_preserves_population_bytes_and_executable_modes(self):
        helper, _ = shared.load("retention_compact_image", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        original = {"/work/hidden": (b"\x00\xff unchanged", 0o444),
                    "/usr/bin/tool": (b"captured executable", 0o555)}
        result = helper.retention_readonly_image(original)
        self.assertEqual(result, {"/work/hidden": (original["/work/hidden"][0], 0o600),
                                  "/usr/bin/tool": original["/usr/bin/tool"]})
        self.assertEqual(original["/work/hidden"][1], 0o444)
        before, key_before = self.session._image(original, {})
        after, key_after = self.session._image(result, {})
        self.assertNotEqual(key_before, key_after)
        self.assertEqual([row["sha256"] for row in before["files"]],
                         [row["sha256"] for row in after["files"]])
        with self.assertRaisesRegex(ValueError, "normalized"):
            helper.retention_readonly_image({"/work/preserved": (b"same", 0o644)})
        self.assertEqual(helper.contract_for(PROFILE)["source_modes"], "NORMALIZED_0600_READ_ONLY_MOUNT")
        self.assertEqual(helper.contract_for(helper.SKILL_LAYOUT_PROFILE)["source_modes"], "NORMALIZED_0444_READ_ONLY")

    def test_unknown_or_unowned_data_policy_refuses_before_any_launch(self):
        for label, policy, readonly in (("unowned", None, True), ("foreign", "FOREIGN", True),
                                         ("writable", "OWNER_0600_READ_ONLY_MOUNT", False)):
            acquired, node, _, manifest = self.image(count=65)
            if policy is None:
                manifest.pop("data_permissions")
            else:
                manifest["data_permissions"] = policy
            manifest["root_read_only"] = readonly
            with self.subTest(label=label), mock.patch.object(Q.subprocess, "Popen",
                    side_effect=AssertionError("unqualified launch")):
                with self.assertRaisesRegex(Q.WG.WorkGraphError, "data image permissions"):
                    self.session._execute(acquired, node, {"key": "constructed"}, self.session.output / label)
        self.assertEqual((self.session.dispatch_count, self.session._issued), (0, {}))

    def test_overbound_vector_refuses_and_closes_every_input_before_dispatch(self):
        acquired, node, _, _ = self.image(count=2700)
        descriptors = []
        sealed = self.session._sealed
        def retain(raw):
            fd = sealed(raw)
            descriptors.append(fd)
            return fd
        directory = self.session.output / "overbound"
        with mock.patch.object(self.session, "_sealed", side_effect=retain), mock.patch.object(
                Q.subprocess, "Popen", side_effect=AssertionError("unqualified launch")):
            with self.assertRaisesRegex(Q.WG.WorkGraphError, "launcher argument budget"):
                self.session._execute(acquired, node, {"key": "constructed"}, directory)
        self.assertTrue(descriptors)
        for fd in descriptors:
            with self.assertRaises(OSError):
                os.fstat(fd)
        self.assertEqual((self.session.dispatch_count, self.session._issued), (0, {}))
        self.assertFalse((directory / "receipt.json").exists())
        self.assertFalse((directory / "dispatch.json").exists())


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("retention_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")

    def test_exact_original_and_all_file_filter_are_preserved(self):
        contract = self.A.contract_for(PROFILE)
        graph, scope, node = self.A.select_node(Q.WG, H.original("scripts/verify-package.sh"), ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][58]))
        self.assertEqual(node["source"], "bash tests/audit-retention.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), (["COMMAND:tests/audit-retention.test.sh:0"], 116))
        self.assertEqual(Q._FINITE_MODES["audit-retention"], PROFILE)
        self.assertEqual(contract["programs"], {
            "tests/audit-retention.test.sh": "9c06e2ddcc380d7a6eb5f73c620a32c90f99c6805a5195227e63f98a47028a2c",
            "scripts/check-audit-retention.sh": "386d7475f7111a5e5349672b01e9c68f5fa0f15cfcf100930d8dae187370937e"})
        for name, pin in contract["programs"].items():
            self.assertEqual(hashlib.sha256(H.input_bytes(name)).hexdigest(), pin)
        wrapper, checker = ((ROOT / name).read_text() for name in contract["programs"])
        self.assertEqual(wrapper.count("bash scripts/check-audit-retention.sh"), 4)
        self.assertIn('["git", "ls-files", "-z"]', checker)
        self.assertIn('("", "AGENTS.md")', checker)
        self.assertIn('path.startswith(prefix) or path == exact', checker)
        self.assertIn('Path(".").rglob("*")', checker)
        self.assertEqual({"bash", "dirname", "mktemp", "rm", "grep", "cat", "git", "python3.12"} - set(P.TOOLS), set())

    def test_retention_runner_pin_matches_captured_source(self):
        contract = self.A.contract_for(PROFILE)
        _, runner = P.read_regular(ROOT / self.A.RUNNER)
        self.assertEqual(contract["pinned_data"][self.A.RUNNER],
                         hashlib.sha256(runner).hexdigest(),
                         "retention runner pin differs from captured source")

    def test_fixed_source_feature_has_no_executor_limit_expansion(self):
        contract = self.A.contract_for(PROFILE)
        self.assertEqual(contract["complete_git"], dict(file_bytes=16 * 1024**2,
            total_bytes=192 * 1024**2, entries=4096, depth=40, path_bytes=2048))
        self.assertNotIn("scratch_bytes", contract)
        prior_modes = ("audit-spec", "andon-class", "registry-wrapper", "marker-order", "commit-message",
            "agents-bootstrap", "andon-escalation", "internal-skill-topology", "capability-ledger",
            "issues-deferred", "no-terminal-cap", "background-chain", "plan-lifecycle", "plan-quality",
            "authorization-binding", "read-only-plans", "safeguard-restoration", "routing", "audit-object-routing")
        for mode in prior_modes:
            self.assertNotIn("complete_git", self.A.contract_for(Q._FINITE_MODES[mode]))


class RetentionFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        if not self.SOURCE_ADMISSION_ONLY:
            # The source must itself be complete, real and eligible. Copy every
            # actual byte/name, including Git; never synthesize an index or
            # replace present linked/large Git storage with absence.
            template = Path(os.environ.get("R0035_FINITE_AUDIT_RETENTION_SOURCE", str(ROOT)))
            shutil.rmtree(self.source)
            shutil.copytree(template, self.source, symlinks=True, copy_function=shutil.copy2)
            return
        for name, raw in {
            self.A.RUNNER: (ROOT / self.A.RUNNER).read_bytes(),
            "docs/research/binary-input.bin": b"\xff\x00 complete research bytes\n",
            "eval/selected.txt": b"ordinary selected input\n",
            "docs/audits/archive/history-a.md": b"historical retained archive\n",
            "docs/audits/archive/group/fixtures/example.md": b"fixture name population\n",
        }.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o644)
        (self.source / "docs/research/empty").mkdir()
        # Real, fixed Git builtins only. No checker/original/namespace execution.
        self.git("init", "--quiet", "--template=", str(self.source))
        self.git("-C", str(self.source), "add", "--all")
        (self.source / "docs/research/untracked.txt").write_bytes(b"actual fallback input\n")

    def git(self, *args):
        result = subprocess.run(["/usr/bin/git", *args], cwd=self.base, env=ENVIRONMENT,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        self.assertEqual((result.returncode, result.stderr), (0, b""))
        return result.stdout

    def snapshot(self):
        objects = {}
        state, stamps = self.A.snapshot_source(P, self.source, objects, profile=PROFILE,
            git_owner=GIT_OWNER, environment=ENVIRONMENT)
        return state, stamps, objects

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))

    def semantic_mutation(self):
        path = self.source / "docs/audits/RETENTION.md"
        raw = path.read_bytes()
        self.assertIn(b"Generated And Local Evidence Boundary", raw)
        path.write_bytes(raw.replace(b"Generated And Local Evidence Boundary", b"Removed boundary"))
        return b"docs/audits/RETENTION.md: missing retention token: Generated And Local Evidence Boundary"


class AdmissionCases(RetentionFixture, unittest.TestCase):
    def test_complete_actual_git_source_fallback_names_and_registry_are_captured(self):
        state, stamps, objects = self.snapshot()
        actual = {path.relative_to(self.source).as_posix() for path in self.source.rglob("*") if path.is_file()}
        self.assertEqual(set(state["files"]), actual)
        for name in actual:
            self.assertEqual(objects[state["files"][name]["sha256"]], (self.source / name).read_bytes())
        self.assertIn("docs/research/empty", state["directories"])
        self.assertIn(".git/objects/info", state["directories"])
        details = state["complete_git_inputs"]
        self.assertEqual(details, stamps["complete_git_inputs"])
        self.assertEqual(details["git"]["ownership"]["source"]["uid"], os.geteuid())
        tracked = details["git"]["index_format"]["ordinary_paths"]
        self.assertNotIn("docs/research/untracked.txt", tracked)
        observed = objects[details["git_observation"]["sha256"]]
        self.assertEqual(observed, b"\0".join(name.encode() for name in tracked) + b"\0")
        self.assertEqual(self.A.image_subject(state, profile=PROFILE), state["files"])

    def test_missing_linked_and_external_git_storage_refuse_without_forcing_fallback(self):
        marker, held = self.source / ".git", self.base / "held-git"
        marker.rename(held)
        try:
            with self.assertRaisesRegex(ValueError, "standalone"):
                self.snapshot()
            marker.write_text("gitdir: " + str(held) + "\n")
            with self.assertRaisesRegex(ValueError, "standalone"):
                self.snapshot()
            marker.unlink()
        finally:
            held.rename(marker)
        for name in ("commondir", "objects/info/alternates", "objects/info/http-alternates", "shallow"):
            path = marker / name
            path.write_text("unsupported external selection\n")
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "external, partial"):
                    self.snapshot()
            finally:
                path.unlink()

    def test_unknown_configuration_refuses_before_actual_git_observer(self):
        path = self.source / ".git/config"
        path.write_bytes(path.read_bytes() + b"\n[include]\n path = /outside/config\n")
        with mock.patch.object(Q.subprocess, "check_output", side_effect=AssertionError("unadmitted Git executed")):
            with self.assertRaisesRegex(ValueError, "config entry"):
                self.snapshot()

    def test_index_subset_is_explicit_and_existing_c2_default_is_unchanged(self):
        raw = (self.source / ".git/index").read_bytes()
        legacy = Q._preflight_git_index_v1(raw)
        self.assertEqual(legacy["profile"], "INLINE_SHA1_V2_V3_V4_TREE_REUC")
        self.assertNotIn("ordinary_paths", legacy)
        supported = Q._preflight_git_index_v1(raw, ordinary_only=True)
        self.assertEqual(supported["entries"], len(supported["ordinary_paths"]))
        for label, offset, value, width in (("version", 4, 3, 4), ("stage", 72, 0x1000, 2),
                                          ("symlink", 36, 0o120000, 4)):
            changed = bytearray(raw)
            struct.pack_into(">I" if width == 4 else ">H", changed, offset, value)
            changed[-20:] = hashlib.sha1(changed[:-20]).digest()
            with self.subTest(label=label), self.assertRaises(ValueError):
                Q._preflight_git_index_v1(bytes(changed), ordinary_only=True)
        with self.assertRaisesRegex(ValueError, "structure"):
            Q._preflight_git_index_v1(raw[:-1] + bytes([raw[-1] ^ 1]), ordinary_only=True)
        with self.assertRaisesRegex(ValueError, "overrides"):
            Q._preflight_git_context_v1(root=self.source)

    def test_closed_startup_command_and_currentness_are_owned_by_existing_c2(self):
        for changed in ({"SUDO_UID": "1"}, {"GIT_CONFIG_COUNT": "1"}, {"LD_PRELOAD": "/outside.so"}, {"HOME": "/tmp"}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                Q._preflight_git_context_v1(root=self.source, environment=dict(ENVIRONMENT, **changed), finite_ls_files=True)
        context = Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT, finite_ls_files=True)
        with self.assertRaisesRegex(ValueError, "fixed command"):
            Q._preflight_git_capture_v1(context, ("status", "--porcelain=v1", "-z", "--untracked-files=all"))
        path = self.source / ".git/config"
        path.write_bytes(path.read_bytes() + b"\n# actual context change\n")
        with self.assertRaisesRegex(ValueError, "context or fixed command"):
            Q._preflight_git_capture_v1(context, ("ls-files", "-z"))

    def test_complete_source_closing_scan_detects_data_outside_git_controls(self):
        original = P.snapshot_tree
        calls = []
        def capture(*args, **kwargs):
            value = original(*args, **kwargs)
            calls.append(1)
            if len(calls) == 1:
                (self.source / "docs/research/untracked.txt").write_bytes(b"changed during complete acquisition\n")
            return value
        with mock.patch.object(P, "snapshot_tree", side_effect=capture):
            with self.assertRaisesRegex(ValueError, "changed during acquisition"):
                self.snapshot()
        self.assertEqual(len(calls), 2)

    def test_source_aliases_and_unknown_modes_refuse(self):
        path = self.source / "eval/selected.txt"
        raw = path.read_bytes()
        outside = self.base / "outside"
        outside.write_bytes(raw)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaisesRegex(ValueError, "single-link"):
            self.snapshot()
        path.unlink()
        path.write_bytes(raw)
        path.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "modes"):
            self.snapshot()

    def test_program_registry_and_readable_runner_must_remain_exact(self):
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["programs"], self.A.REGISTRY, self.A.RUNNER):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "source|pinned"):
                    self.snapshot()
            finally:
                path.write_bytes(raw)

    def test_semantic_failure_bytes_reach_runtime_without_an_answer_substitute(self):
        before, _, _ = self.snapshot()
        self.semantic_mutation()
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        name = "docs/audits/RETENTION.md"
        self.assertEqual(objects[after["files"][name]["sha256"]], (self.source / name).read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_all_diagnostics_spools_names_and_original_data_memory_are_reserved(self):
        before, _, _ = self.snapshot()
        path = self.source / "eval/selected.txt"
        path.write_bytes(b"docs/audits/" + b"arbitrary-name\n")
        state, _, _ = self.snapshot()
        bound = state["complete_git_inputs"]["resources"]
        self.assertGreater(bound["active_diagnostic_bound"], before["complete_git_inputs"]["resources"]["active_diagnostic_bound"])
        self.assertEqual(bound["archive_stale_names"], ["docs/audits/history-a.md"])
        git_only = self.source / ".git/objects/info" / ("observed-" + "x" * 128)
        git_only.write_bytes(b"")
        whole, _, _ = self.snapshot()
        whole_bound = whole["complete_git_inputs"]["resources"]
        self.assertEqual(whole_bound["selected_name_bytes"], bound["selected_name_bytes"])
        self.assertGreater(whole_bound["original_data_memory_reservation"], bound["original_data_memory_reservation"])
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (0, 9, 1))
        self.assertEqual((reservation["diagnostic_files"], reservation["checker_spools"], reservation["wrapper_spools"]), (3, 4, 1))
        session = self.session()
        self.assertEqual(session.environment, ENVIRONMENT)
        self.assertEqual((session.LIMITS["scratch_bytes"], session.LIMITS["file_bytes"], session.LIMITS["address_bytes"],
                          session.LIMITS["descriptors"]), (32 * 1024**2, 16 * 1024**2, 1024**3, 4096))
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for override in ({"scratch_bytes": reservation["required_bytes"] - 1},
                         {"file_bytes": reservation["largest_file_bytes"] - 1},
                         {"stream_bytes": reservation["max_stderr_bytes"] - 1},
                         {"address_bytes": reservation["original_data_memory_reservation"] * 4 // 3 - 1}):
            with self.subTest(override=override), self.assertRaisesRegex(ValueError, "capacity"):
                self.A.require_resource_capacity(reservation, dict(session.LIMITS, **override))

    def test_unchanged_file_limit_also_bounds_source_and_every_materialized_member(self):
        limit = 16 * 1024**2
        path = self.source / "too-large.bin"
        path.write_bytes(b"x" * (limit + 1))
        with self.assertRaisesRegex(ValueError, "byte/entry bound"):
            self.snapshot()
        limits = dict(file_bytes=limit, address_bytes=1024**3, descriptors=4096)
        with self.assertRaisesRegex(ValueError, "image member"):
            self.A.retention_image_reservation({"/work/large": (path.read_bytes(), 0o444)}, limits)
        block = b"x" * limit
        with self.assertRaisesRegex(ValueError, "descriptor/memory"):
            self.A.retention_image_reservation({"/work/" + str(i): (block, 0o444) for i in range(17)}, limits)
        with self.assertRaisesRegex(ValueError, "descriptor/memory"):
            self.A.retention_image_reservation({"/work/" + str(i): (b"x", 0o444) for i in range(4031)}, limits)
        self.assertEqual(self.A.retention_image_reservation({"/work/exact": (block, 0o444)}, limits)["image_member_limit"], limit)

    def test_actual_physical_git_capture_must_equal_the_runtime_member(self):
        state, _, _ = self.snapshot()
        name = "/usr/bin/git"
        metadata, raw = P.read_regular(Path(name), single_link=False)
        key = hashlib.sha256(raw).hexdigest()
        runtime = dict(files={name: dict(mode=0o555, bytes=len(raw), sha256=key)},
            observations={name: dict(resolved=name, mode=metadata["mode"], bytes=len(raw), sha256=key, identity=metadata["identity"])})
        binding = self.A.retention_runtime_binding(state, runtime, {key: raw})
        self.assertEqual(binding["original_argv"], ["git", "ls-files", "-z"])
        bad = copy.deepcopy(runtime)
        bad["observations"][name]["resolved"] = "/outside/git"
        with self.assertRaisesRegex(ValueError, "differs from captured"):
            self.A.retention_runtime_binding(state, bad, {key: raw})
        with self.assertRaisesRegex(ValueError, "differs from captured"):
            self.A.retention_runtime_binding(state, runtime, {key: raw + b"x"})


class LiveCases(RetentionFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_AUDIT_RETENTION_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_AUDIT_RETENTION_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_AUDIT_RETENTION_OBJECTS"
    TEST_SOURCE = "tests/work-graph-audit-retention-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/audit-retention.test.sh:0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_input_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
                         (0, True, b"check-audit-retention: ok\naudit-retention.test: ok\n", b""))
        second, out2, err2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["key"], first["receipt_digest"], stdout, stderr), (second["key"], second["receipt_digest"], out2, err2))
        self.semantic_mutation()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertEqual(stderr, diagnostic + b"\n")
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
