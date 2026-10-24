#!/usr/bin/env python3
"""Original96 source controls; real namespace/original gates require allocation."""
import ast
import copy
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "CONTROLLED_TASK_CLAIM_BOUNDARY_V1"
POLICY = "ORIGINAL96_PRIVATE_DOCS_V1"
PROGRAM = "tests/claim-boundary-proof-levels.test.sh"


def load(name, relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def load_helper():
    return load("claim_boundary_finite", "scripts/qualify-work-graph-finite-leaf.py")


def bootstrap_functions():
    """Load only actual bootstrap imports/functions, never its launch body."""
    runner = (ROOT / "scripts/run-work-graph-verifier.sh").read_text()
    source = runner.split("  exec python -I -B -c '\n", 1)[1].split(
        "\n' \"$2\" \"$3\" \"$4\" \"$5\" \"$6\"", 1)[0]
    tree = ast.parse(source)
    selected = ast.Module(body=[node for node in tree.body if isinstance(node, (ast.Import, ast.FunctionDef))], type_ignores=[])
    namespace = {}
    exec(compile(selected, "captured-original96-bootstrap-functions", "exec"), namespace)
    return namespace


class CatalogCases(unittest.TestCase):
    def test_original96_has_an_explicit_finite_profile(self):
        helper = load_helper()
        missing = []
        try:
            helper.contract_for(PROFILE)
        except ValueError:
            missing.append(PROFILE)
        self.assertEqual(missing, [], "missing exact original96 profile")
        q = load("claim_catalog_owner", "scripts/qualify-work-graph-verifier.py")
        p = load("claim_catalog_prefix", "scripts/qualify-work-graph-prefix.py")
        registry = (ROOT / helper.REGISTRY).read_bytes()
        graph, scope, node = helper.select_node(q.WG, registry, p.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][96]))
        self.assertEqual((node["id"], node["source"]), ("COMMAND:" + PROGRAM + ":0", "bash " + PROGRAM + "\n"))
        self.assertEqual(scope["nodes"], [node["id"]])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(q._FINITE_MODES["claim-boundary"], PROFILE)
        with self.assertRaisesRegex(ValueError, "registry"):
            helper.select_node(q.WG, registry + b"\n", p.ENVIRONMENT, profile=PROFILE)


class SourceFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        self.h = load_helper()
        self.p = load("claim_source_prefix", "scripts/qualify-work-graph-prefix.py")
        for name in self.h.source_paths(PROFILE):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    def snapshot(self):
        objects = {}
        state, stamps = self.h.snapshot_source(self.p, self.source, objects, profile=PROFILE)
        return state, stamps, objects

    def add(self, name, data=b"ordinary selected public data\n"):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class AdmissionCases(SourceFixture):
    def test_complete_unknown_public_reads_and_excluded_typed_membership(self):
        selected = (".unknown/public.payload", "nested/.hidden/.text", "CONTRIBUTING.md", "LICENSE",
                    "docs/portal/pages/.git/future.PNG", "docs/portal/site.json")
        excluded = (".git/objects/data", "dist/payload.md", "docs/audits/archive/record.md",
                    "assets/future.PDF", "docs/research/genealogy/topic/corpus/source.md",
                    "docs/research/genealogy/method/source-prompts/source.md")
        for name in selected + excluded:
            self.add(name, name.encode() + b"\n\x00\xff\n")
        (self.source / "dist/.empty").mkdir()
        state, _, objects = self.snapshot()
        expected = {p.relative_to(self.source).as_posix() for p in self.source.rglob("*") if p.is_file()}
        self.assertEqual(set(state["files"]), expected)
        self.assertIn("dist/.empty", state["directories"])
        image = self.h.claim_boundary_image_files(state, objects)
        self.assertEqual(set(image), {"/work/" + name for name in expected})
        for name in selected:
            self.assertTrue(state["public_inputs"]["read_roles"][name], name)
            self.assertEqual(image["/work/" + name][0], (self.source / name).read_bytes())
        for name in excluded:
            self.assertEqual(state["public_inputs"]["read_roles"][name], [], name)
            self.assertEqual(image["/work/" + name], (b"", 0o444))
            self.assertEqual(objects[state["files"][name]["sha256"]], (self.source / name).read_bytes())
        self.assertEqual(state["public_inputs"]["license_presence"], "FILE")
        self.assertEqual(state["public_inputs"]["initial_probe"]["kind"], "MISSING")
        del state["public_inputs"]["read_roles"][selected[0]]
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.h.claim_boundary_image_files(state, objects)

    def test_probe_presence_and_physical_aliases_refuse_without_dispatch(self):
        probe = self.source / self.h.CLAIM_BOUNDARY_PROBE
        for kind in ("file", "directory"):
            if kind == "file": probe.write_bytes(b"must not overwrite preexisting source")
            else: probe.mkdir()
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "initially be absent"):
                self.snapshot()
            if kind == "file": probe.unlink()
            else: probe.rmdir()
        outside = self.base / "outside"
        outside.write_bytes(b"unowned outside bytes")
        member = self.source / ".new-public"
        for kind in ("symlink", "hardlink", "fifo", "mode"):
            if kind == "symlink": member.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, member)
            elif kind == "fifo": os.mkfifo(member)
            else: member.write_bytes(b"unsupported mode"); member.chmod(0)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            member.unlink()

    def test_source_currentness_binds_excluded_bytes_license_and_same_byte_replacement(self):
        path = self.add(".git/opaque-input", b"excluded bytes one")
        first, stamps, _ = self.snapshot()
        path.write_bytes(b"excluded bytes two")
        second, stamps2, _ = self.snapshot()
        self.assertNotEqual(first, second)
        self.assertNotEqual(stamps, stamps2)
        path.unlink()
        path.write_bytes(b"excluded bytes two")
        third, stamps3, _ = self.snapshot()
        self.assertEqual(second["files"], third["files"])
        self.assertNotEqual(stamps2, stamps3)
        (self.source / "LICENSE").mkdir()
        fourth, _, _ = self.snapshot()
        self.assertEqual(fourth["public_inputs"]["license_presence"], "DIRECTORY")
        self.assertNotEqual(third, fourth)
        for name in (*self.h.contract_for(PROFILE)["programs"], self.h.RUNNER):
            raw = (self.source / name).read_bytes()
            (self.source / name).write_bytes(raw + b"\n")
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "unsupported finite-leaf"):
                self.snapshot()
            (self.source / name).write_bytes(raw)

    def test_diagnostic_population_capacity_and_fixed_private_write_arithmetic(self):
        state, _, objects = self.snapshot()
        initial = state["public_inputs"]["resources"]
        self.add(".large-recursive-read", b"x" * (1024**2) + b"\xff")
        large, _, _ = self.snapshot()
        self.assertGreater(large["public_inputs"]["resources"]["largest_read_file_bytes"], initial["largest_read_file_bytes"])
        self.assertEqual(large["public_inputs"]["resources"]["diagnostic_file_bound"], initial["diagnostic_file_bound"])
        self.assertGreater(large["public_inputs"]["resources"]["original_data_memory_reservation"],
                           initial["original_data_memory_reservation"])
        # Both families count on every visible line, even when a real checker
        # would exempt or skip these bytes. U+2028 is an actual splitlines edge.
        anchor = "PRO" + "VEN"
        payload = ("Do not " + anchor + " auto-" + "update\u2028") * 9
        self.add(".new-diagnostic", payload.encode() + b"\xff\n")
        changed, _, _ = self.snapshot()
        bound = changed["public_inputs"]["resources"]
        self.assertGreaterEqual(bound["possible_diagnostic_entries"] - initial["possible_diagnostic_entries"], 18)
        self.assertGreater(bound["diagnostic_file_bound"], initial["diagnostic_file_bound"])
        reservation = self.h.temporary_requirements(changed, profile=PROFILE)
        self.assertEqual((reservation["probe_writes"], reservation["original_checker_calls"],
                          reservation["wrapper_require_calls"], reservation["checker_spools"]), (4, 5, 22, 1))
        self.assertEqual((reservation["diagnostic_files"], reservation["diagnostic_overwrites"],
                          reservation["total_checker_spool_opportunities"]), (1, 2, 5))
        self.assertEqual(reservation["required_bytes"], reservation["tmp_required_bytes"] + 1024**2)
        self.assertEqual(reservation["tmp_capacity_bytes"] + reservation["overlay_capacity_bytes"], 32 * 1024**2)
        limits = dict(scratch_bytes=32 * 1024**2, file_bytes=16 * 1024**2, stream_bytes=16 * 1024**2,
                      address_bytes=1024**3)
        self.h.require_resource_capacity(reservation, limits)
        for field, amount in (("scratch_bytes", reservation["required_bytes"] - 1),
                              ("file_bytes", reservation["largest_file_bytes"] - 1),
                              ("stream_bytes", reservation["max_stderr_bytes"] - 1),
                              ("address_bytes", reservation["original_data_memory_reservation"])):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "capacity"):
                self.h.require_resource_capacity(reservation, dict(limits, **{field: amount}))
        changed["public_inputs"]["resources"]["diagnostic_file_bound"] = 31 * 1024**2
        with self.assertRaisesRegex(ValueError, "tmp capacity"):
            self.h.temporary_requirements(changed, profile=PROFILE)
        for index in range(14):
            self.add("docs/new-entry-" + str(index))
        with self.assertRaisesRegex(ValueError, "overlay reservation"):
            self.snapshot()


class OverlayCases(unittest.TestCase):
    def setUp(self):
        self.q = load("claim_overlay_owner", "scripts/qualify-work-graph-verifier.py")
        owner_type = type("FixedPolicyUnitOwner", (self.q.VerifierTaskSession,),
            dict(SCOPE=PROFILE, LIMITS=dict(scratch_bytes=32 * 1024**2, file_bytes=16 * 1024**2)))
        self.owner = object.__new__(owner_type)
        self.files = {"/work/docs/fixed.txt": (b"existing protected bytes\n", 0o444),
                      "/work/docs/child/nested.txt": (b"nested protected bytes\n", 0o444),
                      "/work/elsewhere": (b"other protected bytes\n", 0o444)}
        self.files["/usr/bin/fixed-executable"] = (b"fixed executable unit input", 0o555)
        self.before_compact = copy.deepcopy(self.files)
        self.h = load_helper()
        self.files = self.h.retention_readonly_image(self.files)
        self.directories = ["/work", "/work/docs", "/work/docs/child", "/work/docs/empty"]
        self.config, self.raw, self.policy = self.owner._claim_overlay_configuration_v1(self.files, self.directories)
        self.files[self.policy["config_path"]] = self.raw, 0o600
        self.manifest = dict(root_read_only=True, directories=self.directories, private_source_overlay=self.policy,
                             data_permissions="OWNER_0600_READ_ONLY_MOUNT")
        self.node = dict(id="COMMAND:" + PROGRAM + ":0", source="bash " + PROGRAM + "\n")

    def test_fixed_policy_derives_all_existing_mounts_and_refuses_injection(self):
        self.assertEqual(self.h.contract_for(PROFILE)["source_modes"], "NORMALIZED_0600_READ_ONLY_MOUNT")
        for path, (raw, mode) in self.before_compact.items():
            self.assertEqual(self.files[path], (raw, 0o600 if mode == 0o444 else mode))
        self.assertEqual(self.files["/usr/bin/fixed-executable"][1], 0o555)
        self.assertEqual(self.h.contract_for(self.h.SKILL_LAYOUT_PROFILE)["source_modes"], "NORMALIZED_0444_READ_ONLY")
        self.assertEqual(self.owner._claim_overlay_guard_v1(self.files, self.manifest, self.node), self.config)
        self.assertEqual(self.policy["readonly_subtrees"], ["/work/docs/child", "/work/docs/empty"])
        self.assertNotIn("/work/docs", self.config["immutable_paths"])
        self.assertIn("/work/docs/fixed.txt", self.config["immutable_paths"])
        for field, value in (("root", "/work"), ("overlay_bytes", 2 * 1024**2),
                             ("tmp_bytes", 32 * 1024**2), ("readonly_subtrees", [])):
            modified = copy.deepcopy(self.manifest)
            modified["private_source_overlay"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.owner._claim_overlay_guard_v1(self.files, modified, self.node)
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(self.files, dict(self.manifest, source_materialization="SINGLE_LINK_FILES_READ_ONLY_ROOT"), self.node)
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(self.files, dict(self.manifest, private_source_overlay=None), self.node)
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(self.files, dict(self.manifest, data_permissions=None), self.node)
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(self.files, self.manifest, dict(self.node, source="true\n"))
        bad_files = dict(self.files, **{self.policy["config_path"]: (self.raw + b"\n", 0o600)})
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(bad_files, self.manifest, self.node)
        self.owner.SCOPE = "CONTROLLED_TASK_AUDIT_SPEC_V1"
        self.assertIsNone(self.owner._claim_overlay_guard_v1(self.files, {}, self.node))
        with self.assertRaises(ValueError):
            self.owner._claim_overlay_guard_v1(self.files, self.manifest, self.node)

    def test_actual_census_observes_created_names_hashes_modes_and_cleanup(self):
        functions = bootstrap_functions()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kept").write_bytes(b"first bytes")
            (root / "empty").mkdir()
            config = dict(entry_limit=32, path_bytes=128, file_bytes=4096)
            before = functions["census"](str(root), config)
            (root / "new-descendants").mkdir()
            (root / "new-descendants/probe").write_bytes(b"private transient bytes")
            during = functions["census"](str(root), config)
            self.assertIn("new-descendants/probe", during["files"])
            self.assertIn("new-descendants", during["directories"])
            self.assertNotEqual(before, during)
            shutil.rmtree(root / "new-descendants")
            self.assertEqual(functions["census"](str(root), config), before)
            (root / "kept").write_bytes(b"other bytes")
            (root / "kept").chmod(0o600)
            after = functions["census"](str(root), config)
            self.assertNotEqual(after["files"]["kept"]["sha256"], before["files"]["kept"]["sha256"])
            self.assertEqual(after["files"]["kept"]["mode"], 0o600)
            (root / "alias").symlink_to(root / "kept")
            with self.assertRaisesRegex(ValueError, "nonordinary"):
                functions["census"](str(root), config)
            (root / "alias").unlink()
            with self.assertRaisesRegex(ValueError, "bound"):
                functions["census"](str(root), dict(config, entry_limit=2))

    def test_bounded_sealed_buffer_retains_partial_and_failure_without_success_inference(self):
        functions = bootstrap_functions()
        descriptor = self.owner._claim_census_buffer_v1()
        self.addCleanup(os.close, descriptor)
        self.assertEqual(fcntl.fcntl(descriptor, fcntl.F_GET_SEALS), fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK)
        with self.assertRaises(OSError): os.ftruncate(descriptor, 5 * 1024**2)
        raw = os.pread(descriptor, self.config["buffer_bytes"], 0)
        blank = self.owner._claim_effects_decode_v1(raw, self.config)
        self.assertEqual((blank["observation"], blank["original_started"]), ("REFUSED", "UNOBSERVED"))
        # These are explicitly constructed decoder inputs, not mount evidence,
        # original execution, an issued receipt or a reusable acceptance result.
        docs = dict(files=copy.deepcopy(self.config["baseline"]["files"]),
                    directories={name: dict(mode=mode, read_only=name != ".")
                                 for name, mode in self.config["baseline"]["directories"].items()})
        phase = dict(docs=docs, tmp=dict(files={}, directories={".": dict(mode=0o755, read_only=False)}),
                     immutable_mounts={path: True for path in self.config["immutable_paths"]})
        record = dict(policy=POLICY, phase="BEFORE", original_started=False, before=phase)
        def decode(value):
            functions["store_record"](descriptor, value, self.config["buffer_bytes"])
            return self.owner._claim_effects_decode_v1(os.pread(descriptor, self.config["buffer_bytes"], 0), self.config)
        partial = decode(record)
        self.assertEqual((partial["observation"], partial["original_exit"]), ("PARTIAL", "UNOBSERVED"))
        record.update(phase="AFTER", original_started=True, original_exit=141, after=copy.deepcopy(phase))
        failed = decode(record)
        self.assertEqual((failed["observation"], failed["original_exit"], failed["authority"]), ("COMPLETE", 141, "NONE"))
        record["original_exit"] = -13
        self.assertEqual(decode(record)["original_exit"], -13)
        record["after"]["docs"]["files"]["extra-private-name"] = dict(mode=0o644, bytes=1, sha256="0" * 64)
        self.assertFalse(decode(record)["clean_private_namespace"])
        record["after"]["docs"]["files"]["fixed.txt"]["sha256"] = "0" * 64
        self.assertFalse(decode(record)["protected_members_unchanged"])
        record["before"]["immutable_mounts"]["/work/docs/fixed.txt"] = False
        self.assertEqual(decode(record)["observation"], "REFUSED")
        record["before"]["immutable_mounts"]["/work/docs/fixed.txt"] = True
        clean_record = dict(policy=POLICY, phase="AFTER", original_started=True, original_exit=0,
                            before=copy.deepcopy(phase), after=copy.deepcopy(phase))
        clean_record["after"]["docs"]["directories"]["."]["read_only"] = True
        with self.subTest(case="changed private-parent mount flag"):
            self.assertFalse(decode(clean_record)["clean_private_namespace"])
        with self.subTest(case="malformed record type"):
            self.assertEqual(decode([])["observation"], "REFUSED")
        with self.assertRaisesRegex(ValueError, "report bound"):
            functions["store_record"](descriptor, dict(data="x" * self.config["buffer_bytes"]), self.config["buffer_bytes"])
        fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, fcntl.F_SEAL_WRITE | fcntl.F_SEAL_SEAL)
        with self.assertRaises(OSError): os.pwrite(descriptor, b"x", 8)


class LiveCases(unittest.TestCase):
    """Two actual gates only; source tests above supply no execution credit."""
    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_CLAIM_BOUNDARY_LIVE") != "1":
            raise unittest.SkipTest("requires a separately allocated original96 receiving namespace")
        if not os.environ.get("R0035_CLAIM_BOUNDARY_EVIDENCE"):
            raise RuntimeError("a fresh explicit original96 evidence destination is required")

    def setUp(self):
        self.base = Path(os.environ["R0035_CLAIM_BOUNDARY_EVIDENCE"]) / self._testMethodName
        self.base.mkdir(parents=True)
        self.source = self.base / "source"
        shutil.copytree(ROOT, self.source)
        self.q = load("claim_live_owner", "scripts/qualify-work-graph-verifier.py")
        self.h = load_helper()
        self.p = load("claim_live_prefix", "scripts/qualify-work-graph-prefix.py")

    def actual(self, session):
        result = session.run()
        directory = Path(result["evidence_directory"])
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        effects = json.loads((directory / "source-effects.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + PROGRAM + ":0")
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        self.assertEqual((effects["observation"], effects["original_started"], effects["original_exit"]),
                         ("COMPLETE", True, result["exit"]))
        self.assertTrue(effects["protected_members_unchanged"])
        self.assertTrue(effects["clean_private_namespace"])
        return result, (directory / "stdout.log").read_bytes(), (directory / "stderr.log").read_bytes()

    def test_actual_original_success_reuses_one_receipt_and_restores_private_names(self):
        before, stamps = self.h.snapshot_source(self.p, self.source, {}, profile=PROFILE)
        session = self.q.create_finite_leaf_session(self.source, self.base / "evidence", profile=PROFILE)
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
                         (0, True, b"claim-boundary-proof-levels.test: ok\n", b""))
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        for field in ("key", "producer", "receipt_digest"):
            self.assertEqual(first[field], second[field])
        self.assertEqual(self.h.snapshot_source(self.p, self.source, {}, profile=PROFILE), (before, stamps))

    def test_actual_unknown_public_claim_failure_is_retained_and_not_reused(self):
        (self.source / "unknown-public-claim.txt").write_text("Capability parity is " + "PRO" + "VEN.\n")
        session = self.q.create_finite_leaf_session(self.source, self.base / "evidence", profile=PROFILE)
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertIn(b"checker fails on the live tree", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
