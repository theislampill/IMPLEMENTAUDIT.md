#!/usr/bin/env python3
"""Finite source controls for exact original86; live controls require root allocation."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("layout_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_SKILL_LAYOUT_V1"


class CatalogCases(unittest.TestCase):
    def test_exact_original_profile_is_explicitly_available(self):
        helper, _ = shared.load("layout_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = helper.contract_for(PROFILE)
        except ValueError:
            contract = None
        self.assertIsNotNone(contract, "missing exact original86 skill-layout profile")

    def test_exact_mapping_whole_programs_and_complete_scan_roots(self):
        helper, _ = shared.load("layout_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        graph, scope, node = helper.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][86]))
        self.assertEqual(node["source"], "bash tests/skill-layout-contract.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), ([node["id"]], 116))
        self.assertEqual(Q._FINITE_MODES["skill-layout"], PROFILE)
        contract = helper.contract_for(PROFILE)
        self.assertEqual(contract["programs"], {
            "tests/skill-layout-contract.test.sh": "1139d5406839aec5ebdfd82eb0ad63ec9f3c5404cabf3a6c377af0db4a546a7e",
            "scripts/check-skill-layout-contract.sh": "b73e014aa4727d064108515fd959f1d9efb799b2afa1d02f0e7677bd51d02988",
            "scripts/run-work-graph-verifier.sh": "6f6d2bdbcf8350d6b370d37a5e15f4ddb73d336b5bc42d941540f3269613150f"})
        checker = (ROOT / "scripts/check-skill-layout-contract.sh").read_text()
        body = checker.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        syntax = ast.parse(body)
        active = next(ast.literal_eval(n.value) for n in syntax.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "active_roots" for t in n.targets))
        self.assertEqual(set(active), {".claude-plugin", ".github", "scripts", "tests", "docs/portal", "README.md", "AGENTS.md", "CONTRIBUTING.md"})
        self.assertEqual(set(contract["recursive"]["roots"]), set(active) - {"README.md", "AGENTS.md", "CONTRIBUTING.md"} | {"skills"})
        self.assertEqual(set(contract["recursive"]["optional_files"]), {"CONTRIBUTING.md", ".git"})
        self.assertEqual(set(contract["data"]), {"README.md", "AGENTS.md", ".codex-plugin/plugin.json"})


class LayoutFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        if self.SOURCE_ADMISSION_ONLY:
            # Use the original test owner's minimal-layout factory, not a
            # reduced checkout. Every byte of this constructed subject is
            # captured; it grants no historical/current whole-source result.
            wrapper = (self.source / self.A.contract_for(PROFILE)["program"]).read_text()
            start, end = "make_minimal_repo() {\n", '\n}\n\npositive="$tmp/positive"'
            self.assertEqual((wrapper.count(start), wrapper.count(end)), (1, 1))
            factory = start + wrapper.split(start, 1)[1].split(end, 1)[0] + "\n}\n"
            built = subprocess.run(["bash", "-c", factory + '\nmake_minimal_repo "$1"\n',
                                    "constructed-original86", str(self.source)],
                                   capture_output=True, timeout=20)
            self.assertEqual(built.returncode, 0, built.stderr)
            for name in (".github/workflows/fixture.yml", "docs/portal/fixture.txt"):
                self.member(name, b"Constructed original86 source data.\n")
        else:
            # The explicitly allocated live path retains its complete actual
            # subject and all unchanged size/physical-source gates.
            for name in ("skills", ".claude-plugin", ".github", "scripts", "tests", "docs/portal"):
                if (ROOT / name).exists():
                    shutil.copytree(ROOT / name, self.source / name, dirs_exist_ok=True)
            if (ROOT / "CONTRIBUTING.md").exists():
                shutil.copyfile(ROOT / "CONTRIBUTING.md", self.source / "CONTRIBUTING.md")
        self.assertFalse((self.source / ".git").exists())
        self.restore_historical_inputs()
        if self.SOURCE_ADMISSION_ONLY:
            self.fixture_subject = {
                "scope": "CONSTRUCTED_ORIGINAL86_SOURCE",
                "files": {str(path.relative_to(self.source)): dict(
                    bytes=path.stat().st_size, mode=path.stat().st_mode & 0o777,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                    for path in sorted(self.source.rglob("*")) if path.is_file()},
            }
            (self.base / "fixture-subject.json").write_text(json.dumps(self.fixture_subject, indent=2) + "\n")

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))

    def member(self, name, raw=b"new source input\n"):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o644)
        return path

    def semantic_mutation(self):
        self.member("skills/audit-state/.unexpected-substrate.txt")
        return b"skills/audit-state must not duplicate shared substrate: skills/audit-state/.unexpected-substrate.txt"


class AdmissionCases(LayoutFixture, unittest.TestCase):
    def test_complete_actual_bytes_modes_population_and_image_subject(self):
        state, _, objects = self.snapshot()
        self.assertEqual(self.fixture_subject["scope"], "CONSTRUCTED_ORIGINAL86_SOURCE")
        self.assertEqual(set(state["files"]), set(self.fixture_subject["files"]))
        self.assertEqual(set(state["files"]), {str(p.relative_to(self.source)) for p in self.source.rglob("*") if p.is_file()})
        for name, row in state["files"].items():
            self.assertEqual(objects[row["sha256"]], (self.source / name).read_bytes())
            self.assertEqual(row["mode"], (self.source / name).stat().st_mode & 0o777)
        subject = self.A.image_subject(state, profile=PROFILE)
        self.assertEqual(subject, state["files"])
        self.assertIn(self.A.REGISTRY, subject)
        self.assertIn(self.A.RUNNER, subject)
        self.assertNotIn(self.A.REGISTRY, self.A.image_subject(state, profile=self.A.PROFILE))
        self.assertIn(self.A.REGISTRY, self.A.image_subject(state, profile=self.A.REGISTRY_PROFILE))

    def test_every_required_operand_refuses_if_missing(self):
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["data"], *contract["recursive"]["required_members"]):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_optional_absence_is_recorded_without_fabricated_members(self):
        for name in (".github", "docs/portal", "CONTRIBUTING.md"):
            path = self.source / name
            path.rename(self.base / ("absent-" + path.name))
        state, _, _ = self.snapshot()
        probes = state["recursive_inputs"]["projection"]["probes"]
        for name in (".github", "docs/portal", "CONTRIBUTING.md", ".git"):
            self.assertEqual(probes[name]["kind"], "MISSING")
            self.assertNotIn(name, state["directories"])
            self.assertNotIn(name, state["files"])
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            self.session().run()

    def test_present_git_directory_file_and_alias_refuse_before_runtime(self):
        path = self.source / ".git"
        for index, kind in enumerate(("file", "directory", "alias")):
            if kind == "file":
                path.write_bytes(b"gitdir: /outside/acquisition\n")
            elif kind == "directory":
                path.mkdir()
            else:
                path.symlink_to(self.base / "absent-git")
            session = self.session("present-git-" + str(index))
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                session.run()
            self.assertEqual((session.dispatch_count, session._issued), (0, {}))
            self.assertFalse((session.output / "objects").exists())
            path.rmdir() if kind == "directory" else path.unlink()

    def test_hidden_binary_nested_empty_directory_and_extra_skill_are_captured(self):
        members = {
            "scripts/.hidden.bin": b"\xff\x00\r\n",
            "tests/nested/new-source.txt": b"arbitrary source data\n",
            "skills/invented-child/SKILL.md": b"extra physical skill\n",
        }
        for name, raw in members.items():
            self.member(name, raw)
        (self.source / "skills/audit-state/empty").mkdir()
        state, _, objects = self.snapshot()
        for name, raw in members.items():
            self.assertEqual(objects[state["files"][name]["sha256"]], raw)
        self.assertIn("skills/audit-state/empty", state["directories"])

    def test_whole_program_registry_and_engine_runner_drift_refuse(self):
        for index, name in enumerate((*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY)):
            path = self.source / name; raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(index))
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "executable|source|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            path.write_bytes(raw)

    def test_alias_special_file_mode_and_physical_root_alias_refuse(self):
        target = self.member("tests/new-member.txt")
        outside = self.base / "outside"; outside.write_bytes(b"outside\n")
        target.unlink(); target.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); os.link(outside, target)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); os.mkfifo(target)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); target.write_bytes(b"ordinary\n"); target.chmod(0o444)
        with self.assertRaisesRegex(ValueError, "mode"): self.snapshot()
        target.chmod(0o644)
        alias = self.base / "source-alias"; alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=PROFILE)

    def test_semantic_data_change_reaches_runtime_without_preacceptance(self):
        original, _, _ = self.snapshot()
        self.semantic_mutation()
        changed, _, _ = self.snapshot()
        self.assertNotEqual(original, changed)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"): session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_nine_retained_trees_private_writes_and_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (10, 120, 137))
        self.assertEqual(reservation["private_fixture_trees"], 9)
        self.assertEqual(reservation["generated_private_files"], 109)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        self.assertLess(reservation["max_stderr_bytes"], 16 * 1024**2)
        for label, limit in (("scratch", {"scratch_bytes": reservation["required_bytes"] - 1}),
                             ("stream", {"stream_bytes": reservation["max_stderr_bytes"] - 1}),
                             ("file", {"file_bytes": reservation["largest_file_bytes"] - 1})):
            session = self.session("capacity-" + label)
            session.LIMITS = dict(session.LIMITS, **limit)
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, "capacity"): session.run()
            self.assertEqual(session.dispatch_count, 0)

    def test_decoded_line_breaks_quoted_unicode_and_dense_output_are_bounded(self):
        self.member("scripts/line-shapes.txt", "first\rsecond\u0085third\u2028fourth\n".encode())
        state, _, _ = self.snapshot()
        self.assertEqual(state["layout_resources"]["scan_line_counts"]["scripts/line-shapes.txt"], 4)
        name = "tests/" + "/".join(["n" * 180] * 3) + "/" + "d" * 180 + ".txt"
        self.member(name, b"\n" * 40000)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "capacity"): session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_literal_recursive_bounds_and_imported_receipt_refuse(self):
        path = self.source / "README.md"; raw = path.read_bytes()
        path.write_bytes(b"x" * (128 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "bound"): self.snapshot()
        path.write_bytes(raw)
        self.member("tests/too-large.bin", b"x" * (1024 * 1024 + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"): session.run()
        self.assertEqual(session.dispatch_count, 0)
        with self.assertRaises(TypeError): session.run(receipt={"exit": 0}, command="git ls-files")


@unittest.skipUnless(os.name == "posix", "complete current POSIX source acquisition")
class CurrentSourceCases(unittest.TestCase):
    def test_actual_current_recursive_population_keeps_the_original_bound(self):
        helper, _ = shared.load("current_layout_bounds", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        contract = helper.contract_for(PROFILE)["recursive"]
        paths = [path for name in contract["roots"] for path in (ROOT / name).rglob("*") if path.is_file()]
        size = sum(path.stat().st_size for path in paths)
        limit = contract["bounds"]["total_bytes"]
        self.assertEqual(limit, 8 * 1024**2)
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("unexpected current-source launch")):
            if size > limit:
                with self.assertRaisesRegex(ValueError, "combined recursive source entry/byte bound"):
                    helper.snapshot_recursive_inputs(P, ROOT, {}, contract)
                outcome = "REFUSED_OVER_BOUND"
            else:
                helper.snapshot_recursive_inputs(P, ROOT, {}, contract)
                outcome = "SOURCE_ACQUIRED_ONLY"
        print(json.dumps(dict(scope="CURRENT_RECURSIVE_SOURCE_ONLY", bytes=size, limit=limit,
                              result=outcome, runtime=False, native_authority=False), sort_keys=True))


class LiveCases(LayoutFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_SKILL_LAYOUT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_SKILL_LAYOUT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_SKILL_LAYOUT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-skill-layout-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/skill-layout-contract.test.sh:0")
        self.assertEqual((result["group"]["nodes"], len(result["group"]["omitted_nodes"])), ([receipt["node"]], 116))
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_population_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
            (0, True, b"check-skill-layout-contract: ok\npayload path hygiene: ok\n" * 2 + b"skill-layout-contract.test: ok\n", b""))
        second, stdout2, stderr2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["receipt_digest"], first["key"], first["producer"], stdout, stderr),
                         (second["receipt_digest"], second["key"], second["producer"], stdout2, stderr2))
        self.member("tests/added-source-member.txt")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"): session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertIn(diagnostic, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"): session.run()
        self.assertEqual(session.dispatch_count, 1)


GIT_ARGS = ("ls-files", "--error-unmatch", "skills/SKILL.md")
GIT_ENVIRONMENT = dict(P.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1")
GIT_OWNER = dict(context=Q._preflight_git_context_v1, capture=Q._preflight_git_capture_v1)


class GitFixture(LayoutFixture):
    def setUp(self):
        super().setUp()
        # Genuine independent repository. Every source member and Git byte is
        # acquired; an opaque input outside the original read set stays opaque.
        self.member("docs/research/opaque.bin", b"\xff\x00" * 1024**2)
        self.git("init", "--quiet", "--template=", str(self.source))
        self.git("-C", str(self.source), "add", "--all")

    def git(self, *args):
        result = subprocess.run(["/usr/bin/git", *args], cwd=self.base, env=GIT_ENVIRONMENT,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        self.assertEqual((result.returncode, result.stderr), (0, b""))
        return result.stdout

    def snapshot(self, *, owner=GIT_OWNER, environment=GIT_ENVIRONMENT):
        objects = {}
        state, stamps = self.A.snapshot_source(P, self.source, objects, profile=PROFILE,
            git_owner=owner, environment=environment)
        return state, stamps, objects

    def tracked_missing_operand(self, *, descendant=False):
        name = GIT_ARGS[-1] + ("/nested.md" if descendant else "")
        path = self.member(name, b"historical flat data\n")
        self.git("-C", str(self.source), "add", "--", name)
        path.unlink()
        if descendant:
            path.parent.rmdir()
        self.assertFalse((self.source / GIT_ARGS[-1]).exists())
        return name


class GitAdmissionCases(GitFixture, unittest.TestCase):
    def test_complete_present_source_and_actual_untracked_exit_one_are_retained(self):
        state, stamps, objects = self.snapshot()
        files = {path.relative_to(self.source).as_posix() for path in self.source.rglob("*") if path.is_file()}
        self.assertEqual(set(state["files"]), files)
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
        feature = state["skill_layout_git_inputs"]
        self.assertEqual(feature, stamps["skill_layout_git_inputs"])
        self.assertEqual((feature["branch"], feature["observed_exit"], feature["original_argv"]),
                         ("PRESENT_GIT", 1, ["git", *GIT_ARGS]))
        self.assertEqual(objects[feature["streams"]["stdout"]["sha256"]], b"")
        self.assertTrue(objects[feature["streams"]["stderr"]["sha256"]])
        self.assertEqual(state["complete_git_inputs"]["git_observation"]["exit"], 0)
        self.assertEqual(self.A.image_subject(state, profile=PROFILE), state["files"])

    def test_actual_tracked_but_absent_operand_is_not_preaccepted_or_refused(self):
        name = self.tracked_missing_operand()
        state, _, objects = self.snapshot()
        self.assertNotIn(name, state["files"])
        self.assertIn(name, state["complete_git_inputs"]["git"]["index_format"]["ordinary_paths"])
        feature = state["skill_layout_git_inputs"]
        self.assertEqual(feature["observed_exit"], 0)
        self.assertEqual(objects[feature["streams"]["stdout"]["sha256"]], name.encode() + b"\n")
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_actual_pathspec_descendant_match_is_not_replaced_with_exact_name_logic(self):
        name = self.tracked_missing_operand(descendant=True)
        state, _, objects = self.snapshot()
        self.assertNotIn(GIT_ARGS[-1], state["complete_git_inputs"]["git"]["index_format"]["ordinary_paths"])
        feature = state["skill_layout_git_inputs"]
        self.assertEqual(feature["observed_exit"], 0)
        self.assertEqual(objects[feature["streams"]["stdout"]["sha256"]], name.encode() + b"\n")

    def test_genuine_no_git_state_environment_and_read_limits_are_preserved(self):
        (self.source / ".git").rename(self.base / "held-git")
        state, _, _ = self.snapshot(environment=P.ENVIRONMENT)
        self.assertEqual(state["recursive_inputs"]["projection"]["probes"][".git"], dict(kind="MISSING", missing_at=".git"))
        self.assertNotIn("complete_git_inputs", state)
        self.assertNotIn("skill_layout_git_inputs", state)
        self.assertNotIn("docs/research/opaque.bin", state["files"])
        self.assertNotIn("original_data_memory_reservation", self.A.temporary_requirements(state, profile=PROFILE))
        session = self.session()
        self.assertEqual(session.environment, P.ENVIRONMENT)
        contract = self.A.contract_for(PROFILE)
        self.assertEqual(contract["bounds"], dict(file_bytes=128 * 1024, total_bytes=8 * 1024**2, files=7))
        self.assertEqual(contract["recursive"]["bounds"]["file_bytes"], 1024**2)
        self.assertEqual(session.LIMITS["scratch_bytes"], 32 * 1024**2)

    def test_branch_presence_change_cannot_silently_change_startup(self):
        session = self.session("present-selected")
        marker, held = self.source / ".git", self.base / "held-git"
        marker.rename(held)
        with self.assertRaisesRegex(ValueError, "branch changed"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        no_git = self.session("absent-selected")
        held.rename(marker)
        with self.assertRaisesRegex(ValueError, "startup environment"):
            no_git.run()
        self.assertEqual(no_git.dispatch_count, 0)

    def test_fixed_scope_rejects_other_commands_and_combined_selectors(self):
        context = Q._preflight_git_context_v1(root=self.source, environment=GIT_ENVIRONMENT, finite_skill_layout=True)
        self.assertEqual(context["binding"]["read_profile"], "FINITE_ORIGINAL86_SKILL_LAYOUT_TRACKED_PATH")
        with self.assertRaisesRegex(ValueError, "fixed command"):
            Q._preflight_git_capture_v1(context, ("ls-files", "-z"))
        for flags in (dict(finite_ls_files=True, finite_skill_layout=True), dict(finite_skill_layout=1)):
            with self.subTest(flags=flags), self.assertRaisesRegex(ValueError, "profile must be explicit"):
                Q._preflight_git_context_v1(root=self.source, environment=GIT_ENVIRONMENT, **flags)
        self.assertLessEqual(context["binding"]["observation_bounds"]["stdout_bytes"], 16 * 1024**2)

    def test_real_same_byte_foreign_repository_context_cannot_replace_source_custody(self):
        foreign = self.base / "foreign-source"
        shutil.copytree(self.source, foreign)
        def context(**options):
            if options.get("finite_skill_layout"):
                options = dict(options, root=foreign)
            return Q._preflight_git_context_v1(**options)
        owner = dict(context=context, capture=Q._preflight_git_capture_v1)
        with self.assertRaisesRegex(ValueError, "differs from complete source custody"):
            self.snapshot(owner=owner)

    def test_control_change_and_unadmitted_config_refuse_before_original_execution(self):
        context = Q._preflight_git_context_v1(root=self.source, environment=GIT_ENVIRONMENT, finite_skill_layout=True)
        path = self.source / ".git/config"
        path.write_bytes(path.read_bytes() + b"\n# actual control change\n")
        with self.assertRaisesRegex(ValueError, "context or fixed command"):
            Q._preflight_git_capture_v1(context, GIT_ARGS)
        path.write_bytes(path.read_bytes() + b"[include]\n path = /outside/config\n")
        with self.assertRaisesRegex(ValueError, "unsupported Git config entry"):
            self.snapshot()

    def test_new_active_member_between_complete_git_reads_cannot_escape_allocation(self):
        original = P.snapshot_tree
        whole = []
        def capture(root, *args, **options):
            result = original(root, *args, **options)
            if Path(root) == self.source:
                whole.append(1)
                if len(whole) == 2:
                    self.member("tests/new-after-complete-read.txt", b"actual new scan input\n")
            return result
        with mock.patch.object(P, "snapshot_tree", side_effect=capture):
            with self.assertRaisesRegex(ValueError, "read population changed"):
                self.snapshot()
        self.assertEqual(len(whole), 2)

    def test_opaque_complete_inputs_do_not_relax_the_original_read_set_bound(self):
        state, _, _ = self.snapshot()
        self.assertEqual(state["files"]["docs/research/opaque.bin"]["bytes"], 2 * 1024**2)
        self.assertLessEqual(state["layout_resources"]["decoder_bound"], 4 * 1024**2)
        self.assertEqual(state["complete_git_inputs"]["projection"]["bounds"]["file_bytes"], 16 * 1024**2)
        self.member("tests/too-large-read.bin", b"x" * (1024**2 + 1))
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()

    def test_original_private_effects_and_selected_memory_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (10, 120, 137))
        self.assertEqual((reservation["private_fixture_trees"], reservation["generated_private_files"]), (9, 109))
        session = self.session()
        self.assertEqual(session.environment, GIT_ENVIRONMENT)
        self.assertEqual((session.LIMITS["file_bytes"], session.LIMITS["scratch_bytes"], session.LIMITS["address_bytes"]),
                         (16 * 1024**2, 32 * 1024**2, 1024**3))
        self.A.require_resource_capacity(reservation, session.LIMITS)
        session.LIMITS = dict(session.LIMITS,
            address_bytes=reservation["original_data_memory_reservation"] * 4 // 3 - 1)
        with self.assertRaisesRegex(ValueError, "memory capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_actual_runtime_binding_carries_only_the_fixed_original86_command(self):
        state, _, _ = self.snapshot()
        name = "/usr/bin/git"
        metadata, raw = P.read_regular(Path(name), single_link=False)
        key = self.A.digest(raw)
        runtime = dict(files={name: dict(mode=0o555, bytes=len(raw), sha256=key)},
            observations={name: dict(resolved=name, mode=metadata["mode"], bytes=len(raw), sha256=key, identity=metadata["identity"])})
        binding = self.A.retention_runtime_binding(state, runtime, {key: raw}, profile=PROFILE)
        self.assertEqual(binding["original_argv"], ["git", *GIT_ARGS])
        with self.assertRaisesRegex(ValueError, "command scope"):
            self.A.retention_runtime_binding(state, runtime, {key: raw}, profile="UNKNOWN")


class GitImagePolicyCases(GitFixture, unittest.TestCase):
    """One image-policy discriminator; no runtime or original execution."""
    def test_present_git_compact_image_and_exact_no_git_projection(self):
        def source_image(state, objects):
            files = {"/work/" + name: (objects[row["sha256"]], 0o444)
                     for name, row in state["files"].items()}
            name = "/work/" + self.A.RUNNER
            files[name] = (files[name][0], 0o555)
            return files

        marker, held = self.source / ".git", self.base / "held-git"
        marker.rename(held)
        absent, _, absent_objects = self.snapshot(environment=P.ENVIRONMENT)
        original = source_image(absent, absent_objects)
        selected, policy = self.A.finite_image_permissions(original, absent, profile=PROFILE)
        self.assertIs(selected, original)
        self.assertEqual(policy, dict(source_modes="NORMALIZED_0444_READ_ONLY"))
        no_git = Q.create_finite_leaf_session(self.source, self.base / "no-git-policy", profile=PROFILE)
        before, before_key = no_git._image(original, absent["files"])
        after, after_key = no_git._image(selected, absent["files"])
        self.assertEqual((after, after_key), (before, before_key))
        self.assertNotIn("data_permissions", after)
        self.assertEqual(no_git.environment, P.ENVIRONMENT)
        self.assertEqual(no_git.LIMITS["scratch_bytes"], 32 * 1024**2)
        self.assertEqual(self.A.contract_for(PROFILE)["source_modes"], "NORMALIZED_0444_READ_ONLY")

        held.rename(marker)
        present, _, present_objects = self.snapshot()
        self.assertEqual(present["skill_layout_git_inputs"]["branch"], "PRESENT_GIT")
        original = source_image(present, present_objects)
        preserved = dict(original)
        selected, policy = self.A.finite_image_permissions(original, present, profile=PROFILE)
        self.assertEqual(original, preserved)
        self.assertEqual(policy, dict(source_modes="NORMALIZED_0600_READ_ONLY_MOUNT",
                                     data_permissions="OWNER_0600_READ_ONLY_MOUNT"))
        self.assertEqual(set(selected), set(original))
        for name, (raw, mode) in original.items():
            self.assertEqual(selected[name], (raw, 0o555 if mode == 0o555 else 0o600))
        git = Q.create_finite_leaf_session(self.source, self.base / "present-git-policy", profile=PROFILE)
        self.assertEqual(git.environment, GIT_ENVIRONMENT)
        self.assertEqual(git.LIMITS, no_git.LIMITS)
        old_image, old_key = git._image(original, present["files"])
        image, mode_key = git._image(selected, present["files"])
        self.assertNotEqual(mode_key, old_key)
        self.assertEqual(image["source_observations"], old_image["source_observations"])
        self.assertEqual([(row["path"], row["bytes"], row["sha256"]) for row in image["files"]],
                         [(row["path"], row["bytes"], row["sha256"]) for row in old_image["files"]])
        image["data_permissions"] = policy["data_permissions"]
        policy_key = git._object(git._encode(image))
        self.assertNotEqual(policy_key, mode_key)
        self.assertTrue(image["root_read_only"])
        self.assertEqual(image["directory_mode"], 0o755)
        self.assertEqual((no_git.dispatch_count, git.dispatch_count, no_git._issued, git._issued),
                         (0, 0, {}, {}))


class GitLiveCases(GitFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_SKILL_LAYOUT_GIT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_SKILL_LAYOUT_GIT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_SKILL_LAYOUT_GIT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-skill-layout-cases.py"
    actual = LiveCases.actual

    def test_actual_present_git_positive_reuse(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
            (0, True, b"check-skill-layout-contract: ok\npayload path hygiene: ok\n" * 2 + b"skill-layout-contract.test: ok\n", b""))
        second, stdout2, stderr2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["receipt_digest"], first["key"], first["producer"], stdout, stderr),
                         (second["receipt_digest"], second["key"], second["producer"], stdout2, stderr2))
        self.member("tests/changed-git-source.txt")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_tracked_missing_operand_failure_is_retained_and_not_reused(self):
        self.tracked_missing_operand()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        diagnostic = b"flat canonical source skill file must not be tracked: " + GIT_ARGS[-1].encode() + b"\n"
        self.assertEqual((result["exit"], result["complete"], stdout, stderr), (1, True, b"", diagnostic))
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
