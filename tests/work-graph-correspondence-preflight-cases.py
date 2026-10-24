#!/usr/bin/env python3
"""Read-only paired-plan controls; never execute a qualified verifier route."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
RETAIN = None


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@unittest.skipUnless(
    all(hasattr(os, name) for name in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")) and
    all(call in os.supports_dir_fd for call in (os.open, os.stat, os.readlink)) and
    os.stat in os.supports_follow_symlinks,
    "paired preflight requires the existing no-follow descriptor source observer")
class PairPreflightTests(unittest.TestCase):
    def setUp(self):
        if RETAIN is None:
            self.temp = tempfile.TemporaryDirectory(prefix="r0035-pair-preflight-")
            self.addCleanup(self.temp.cleanup)
            self.directory = Path(self.temp.name)
        else:
            self.directory = RETAIN / self._testMethodName
            self.directory.mkdir()
        self.repo = self.directory / "source"
        self.repo.mkdir()
        self.marker = self.directory / "SUBJECT-LAUNCHED"
        self.env = dict(os.environ)
        # This is the declared planned environment of each tiny fixture, not
        # an observer-only alteration of an unsafe inherited Git context.
        for key in tuple(self.env):
            if key.startswith(("GIT_", "LD_", "DYLD_")) or key in {"PAGER", "GCONV_PATH"}:
                del self.env[key]
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
                        GIT_ATTR_NOSYSTEM="1")
        for name in ("scripts/qualify-work-graph-verifier.py",
                     "skills/implementaudit/scripts/compile-work-graph.py"):
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        sentinel = "#!/bin/bash\nprintf 'launched\\n' >> " + shlex.quote(str(self.marker)) + "\nexit 99\n"
        for name in ("verify-package.sh", "run-work-graph-verifier.sh"):
            (self.repo / "scripts" / name).write_text(sentinel)
        (self.repo / "subject.txt").write_text("bound input\n")
        for arguments in (("init", "-q"), ("config", "user.name", "Preflight Test"),
                          ("config", "user.email", "preflight@example.invalid"),
                          ("config", "core.hooksPath", "/dev/null"),
                          ("config", "commit.gpgsign", "false"), ("add", "."),
                          ("commit", "-qm", "preflight fixture")):
            subprocess.run(["git", *arguments], cwd=self.repo, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        spec = importlib.util.spec_from_file_location("preflight_fixture_owner", self.repo / "scripts/qualify-work-graph-verifier.py")
        self.owner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.owner)
        self.calls = 0

    def currentness(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            return self.owner.verifier_preflight_currentness_v1()

    def plan(self, extended=False):
        binding = self.currentness()
        capture = dict(retain_repro_assets=extended, stdin_file=None, empty_stdin=extended,
                       capture_dist=extended, capture_portal_events=extended, retain_repro_events=extended)
        return dict(schema="implementaudit.verifier-pair-plan.v1", expected_currentness=binding,
                    runs=[dict(mode=mode, output=str(self.directory / mode),
                               base_environment_sha256=binding["base_environment_sha256"],
                               capture=copy.deepcopy(capture)) for mode in ("legacy", "dag")])

    def invoke(self, plan=None, *, raw=None, env=None):
        self.calls += 1
        directory = self.directory / ("call-%02d" % self.calls)
        directory.mkdir()
        path = directory / "plan.json"
        path.write_bytes(raw if raw is not None else json.dumps(plan, sort_keys=True).encode())
        argv = [sys.executable, "-B", str(self.repo / "scripts/qualify-work-graph-verifier.py"), "preflight", str(path)]
        result = subprocess.run(argv, cwd=self.repo, env=self.env if env is None else env,
                                capture_output=True, timeout=15)
        (directory / "stdout.log").write_bytes(result.stdout)
        (directory / "stderr.log").write_bytes(result.stderr)
        (directory / "exit-code.txt").write_text(str(result.returncode) + "\n")
        (directory / "command.json").write_text(json.dumps(dict(argv=argv, cwd=str(self.repo)), sort_keys=True) + "\n")
        self.assertFalse(self.marker.exists(), "preflight launched a qualified subject route")
        self.assertFalse((self.directory / "legacy").exists(), "preflight created an evidence output")
        self.assertFalse((self.directory / "dag").exists(), "preflight created an evidence output")
        return result

    def report(self, result, code):
        self.assertEqual(result.returncode, code, result.stderr.decode(errors="replace"))
        value = json.loads(result.stdout)
        self.assertEqual(value["subject_launches"], 0)
        self.assertEqual(value["authority"], "NONE")
        self.assertEqual(value["normalization"], "NONE_RAW_BYTES")
        self.assertIsNone(value["raw_observables_equal"])
        return value

    def test_distinct_capture_roots_block_the_selected_raw_oracle(self):
        # Break caught: dropping output-bound overrides/declarations would let a
        # known incompatible historical configuration look conflict-free.
        value = self.report(self.invoke(self.plan(extended=True)), 1)
        self.assertEqual(value["status"], "BLOCKED")
        self.assertEqual(set(value["guaranteed_false_predicates"]), {
            "same_environment", "same_child_environment",
            "same_declared_repro_artifacts", "same_dist_namespace"})
        self.assertTrue(value["currentness"]["matches"])

    def test_different_planned_base_environment_is_not_current_or_equal(self):
        # Break caught: accepting a declared second environment without actual
        # acquisition, or failing to compare its base-environment namespace.
        plan = self.plan()
        plan["runs"][1]["base_environment_sha256"] = "0" * 64
        value = self.report(self.invoke(plan), 1)
        self.assertIn("PLANNED_ENVIRONMENT_NOT_CURRENT", value["blocking_reasons"])
        self.assertIn("same_environment", value["guaranteed_false_predicates"])

    def test_missing_currentness_binding_refuses_before_subject_launch(self):
        # Break caught: treating an unbound caller plan as a current launch plan.
        plan = self.plan()
        del plan["expected_currentness"]
        result = self.invoke(plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"preflight plan", result.stderr)
        self.assertEqual(result.stdout, b"")

    def test_no_detected_conflict_is_only_necessary_preconditions(self):
        # Break caught: promoting absent static conflicts to raw equivalence or
        # claiming a future launch is current/authorized.
        value = self.report(self.invoke(self.plan()), 0)
        self.assertEqual(value["status"], "NECESSARY_PRECONDITIONS_ONLY")
        self.assertEqual(value["guaranteed_false_predicates"], [])
        self.assertEqual(value["blocking_reasons"], [])
        self.assertTrue(value["currentness"]["matches"])
        self.assertIn("same_stdout", value["unqualified_predicates"])
        self.assertIn("same_stderr", value["unqualified_predicates"])
        self.assertEqual(value["currentness"]["scope"], "PRE_POST_OBSERVATIONS_NOT_A_LAUNCH_LEASE")

    def test_stale_source_binding_blocks(self):
        plan = self.plan()
        (self.repo / "subject.txt").write_text("changed after plan binding\n")
        value = self.report(self.invoke(plan), 1)
        self.assertFalse(value["currentness"]["matches"])
        self.assertIn("EXPECTED_CURRENTNESS_MISMATCH", value["blocking_reasons"])
        self.assertIn("source_sha256", value["currentness"]["mismatches"])

    def test_wrong_engine_binding_blocks(self):
        plan = self.plan()
        plan["expected_currentness"]["engine_binding"]["driver_sha256"] = "0" * 64
        value = self.report(self.invoke(plan), 1)
        self.assertFalse(value["currentness"]["matches"])
        self.assertIn("engine_binding", value["currentness"]["mismatches"])

    def test_observation_does_not_refresh_the_git_index(self):
        # Break caught: git status without disabled optional locks refreshes the
        # index when filesystem stat data changes even if source bytes do not.
        self.env["GIT_OPTIONAL_LOCKS"] = "1"
        plan = self.plan()
        source = self.repo / "subject.txt"
        st = source.stat()
        os.utime(source, ns=(st.st_atime_ns, st.st_mtime_ns + 10_000_000_000))
        index = self.repo / ".git/index"
        before = index.read_bytes()
        value = self.report(self.invoke(plan), 0)
        self.assertEqual(value["status"], "NECESSARY_PRECONDITIONS_ONLY")
        self.assertEqual(index.read_bytes(), before, "read-only preflight rewrote the Git index")

    def index_snapshot(self, paths):
        result = {}
        for path in paths:
            metadata = path.stat()
            result[path.name] = dict(bytes=metadata.st_size, sha256=digest(path.read_bytes()),
                                     mtime_ns=metadata.st_mtime_ns, ctime_ns=metadata.st_ctime_ns)
        return result

    def test_split_index_refuses_before_any_git_and_preserves_shared_metadata(self):
        plan = self.plan()
        subprocess.run(["git", "update-index", "--split-index"], cwd=self.repo, env=self.env,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotIn(b"splitindex", (self.repo / ".git/config").read_bytes().lower())
        shared = sorted((self.repo / ".git").glob("sharedindex.*"))
        self.assertEqual(len(shared), 1)
        os.utime(shared[0], ns=(1_000_000_000, 1_000_000_000))
        paths = [self.repo / ".git/index", *shared]
        before = self.index_snapshot(paths)
        result = self.invoke(plan)
        after = self.index_snapshot(paths)
        (self.directory / "split-index-observations.json").write_text(json.dumps(
            dict(before=before, after=after, preflight_exit=result.returncode), indent=2, sort_keys=True) + "\n")
        self.assertEqual(after, before, "preflight changed split-index bytes or mtime/ctime")
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"refuses split-index indirection", result.stderr)
        self.assert_no_git_starts()
        self.assertEqual(self.index_snapshot(paths), before)

    def test_plain_v2_index_allows_link_filename_and_untouched_unreferenced_shared_file(self):
        (self.repo / "link").write_text("ordinary filename, not an index extension\n")
        subprocess.run(["git", "add", "--", "link"], cwd=self.repo, env=self.env, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "update-index", "--index-version=2"], cwd=self.repo, env=self.env,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        index = self.repo / ".git/index"
        raw = index.read_bytes()
        self.assertEqual(int.from_bytes(raw[4:8], "big"), 2)
        self.assertIn(b"link\0", raw)
        shared = self.repo / ".git" / ("sharedindex." + raw[-20:].hex())
        shared.write_bytes(raw)
        os.utime(shared, ns=(1_000_000_000, 1_000_000_000))
        plan = self.plan()
        before = self.index_snapshot([index, shared])
        value = self.report(self.invoke(plan), 0)
        self.assertTrue(value["currentness"]["matches"])
        self.assertEqual(self.index_snapshot([index, shared]), before)

    def test_plain_v3_index_with_extended_flags_remains_read_only(self):
        subprocess.run(["git", "update-index", "--skip-worktree", "subject.txt"], cwd=self.repo,
                       env=self.env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        index = self.repo / ".git/index"
        self.assertEqual(int.from_bytes(index.read_bytes()[4:8], "big"), 3)
        plan = self.plan()
        before = self.index_snapshot([index])
        value = self.report(self.invoke(plan), 0)
        self.assertTrue(value["currentness"]["matches"])
        self.assertEqual(self.index_snapshot([index]), before)

    def test_plain_v4_index_with_long_prefix_compression_remains_read_only(self):
        name = "a" * 160
        (self.repo / name).write_text("long prefix predecessor\n")
        subprocess.run(["git", "add", "--", name], cwd=self.repo, env=self.env, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "update-index", "--index-version=4"], cwd=self.repo, env=self.env,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        index = self.repo / ".git/index"
        self.assertEqual(int.from_bytes(index.read_bytes()[4:8], "big"), 4)
        plan = self.plan()
        before = self.index_snapshot([index])
        value = self.report(self.invoke(plan), 0)
        self.assertTrue(value["currentness"]["matches"])
        self.assertEqual(self.index_snapshot([index]), before)

    def test_unknown_index_extension_and_malformed_index_refuse_before_any_git(self):
        index = self.repo / ".git/index"
        original = index.read_bytes()

        def checksummed(body):
            return body + hashlib.sha1(body).digest()

        variants = [original[:-20] + b"\0" * 20,
                    checksummed(original[:4] + (5).to_bytes(4, "big") + original[8:-20]),
                    checksummed(original[:-20] + b"NEXT" + (0).to_bytes(4, "big")),
                    checksummed(original[:-20] + b"TREE" + (100).to_bytes(4, "big") + b"x")]
        for number, raw in enumerate(variants):
            with self.subTest(case=number):
                index.write_bytes(raw)
                self.assert_no_git_starts()
        index.write_bytes(original)

    def append_git_config(self, text):
        with (self.repo / ".git/config").open("a") as stream:
            stream.write(text)

    def callback(self, name, output):
        marker = self.directory / (name + "-EXECUTED")
        callback = self.repo / ".git" / name
        callback.write_text("#!/bin/sh\nprintf 'callback\\n' >> " + shlex.quote(str(marker)) + "\n" + output)
        callback.chmod(0o700)
        return callback, marker

    def assert_observation_refused(self, result, marker):
        self.assertFalse(marker.exists(), "read-only Git observation caused an external write")
        self.assertEqual(result.returncode, 2, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"preflight Git observation", result.stderr)

    def assert_no_git_starts(self):
        with mock.patch.dict(os.environ, self.env, clear=True), \
                mock.patch.object(self.owner.subprocess, "Popen", side_effect=AssertionError(
                    "preflight attempted to start a process before refusing unsupported input")) as launch:
            with self.assertRaisesRegex(self.owner.WG.WorkGraphError, "preflight Git observation") as refusal:
                self.owner.verifier_preflight_currentness_v1()
        launch.assert_not_called()
        with (self.directory / "refusal-process-checks.jsonl").open("a") as stream:
            stream.write(json.dumps(dict(process_launches=launch.call_count,
                                         refusal=str(refusal.exception)), sort_keys=True) + "\n")

    def test_fsmonitor_callback_is_refused_before_git_observation(self):
        plan = self.plan()
        callback, marker = self.callback("fsmonitor-probe", "printf '\\0'\n")
        self.append_git_config('\n[core]\n\tfsmonitor = "' + str(callback) + '"\n')
        self.assert_observation_refused(self.invoke(plan), marker)
        self.assert_no_git_starts()

    def test_clean_filter_is_refused_before_git_observation(self):
        (self.repo / ".gitattributes").write_text("subject.txt filter=preflight-probe\n")
        plan = self.plan()
        callback, marker = self.callback("clean-filter-probe", "cat\n")
        self.append_git_config('\n[filter "preflight-probe"]\n\tclean = "' + str(callback) + '"\n\trequired = true\n')
        member = self.repo / "subject.txt"
        before = member.stat()
        os.utime(member, ns=(before.st_atime_ns, before.st_mtime_ns + 10_000_000_000))
        self.assert_observation_refused(self.invoke(plan), marker)
        self.assert_no_git_starts()

    def test_inherited_git_trace_is_refused_before_git_observation(self):
        plan = self.plan()
        marker = self.directory / "GIT-TRACE-WRITTEN"
        self.env["GIT_TRACE"] = str(marker)
        binding = self.owner.environment_digest(self.env)
        plan["expected_currentness"]["base_environment_sha256"] = binding
        for route in plan["runs"]:
            route["base_environment_sha256"] = binding
        self.assert_observation_refused(self.invoke(plan), marker)
        self.assert_no_git_starts()

    def test_unsupported_environment_selection_refuses_before_any_git(self):
        original = dict(self.env)
        cases = {"GIT_CONFIG_NOSYSTEM": "0", "GIT_CONFIG_GLOBAL": str(self.directory / "global"),
                 "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_CONFIG_COUNT": "0",
                 "GIT_CONFIG_PARAMETERS": "'core.fsmonitor=false'", "GIT_DIR": str(self.repo / ".git"),
                 "GIT_COMMON_DIR": str(self.repo / ".git"), "GIT_WORK_TREE": str(self.repo),
                 "GIT_INDEX_FILE": str(self.repo / ".git/index"), "GIT_NAMESPACE": "probe",
                 "GIT_OBJECT_DIRECTORY": str(self.repo / ".git/objects"), "GIT_EXEC_PATH": "/usr/bin",
                 "GIT_TRACE2_EVENT": str(self.directory / "TRACE2"), "GIT_EXTERNAL_DIFF": "probe",
                 "GIT_PAGER": "probe", "PAGER": "probe", "GIT_FUTURE_UNKNOWN": "1",
                 "LD_PRELOAD": str(self.directory / "not-loaded"), "GCONV_PATH": str(self.directory)}
        for key, value in cases.items():
            with self.subTest(variable=key):
                self.env = dict(original, **{key: value})
                self.assert_no_git_starts()
        self.env = original
        for key in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_ATTR_NOSYSTEM"):
            with self.subTest(missing=key):
                self.env = dict(original)
                del self.env[key]
                self.assert_no_git_starts()
        self.env = original

    def test_unsupported_configuration_refuses_before_any_git(self):
        config = self.repo / ".git/config"
        original = config.read_bytes()
        cases = ['[filter "probe"]\nprocess = probe\n', '[core]\npager = probe\n',
                 '[core]\nhooksPath = /tmp/probe\n', '[diff]\nexternal = probe\n',
                 '[diff "probe"]\ntextconv = probe\n', '[trace2]\neventTarget = /tmp/probe\n',
                 '[include]\npath = /tmp/probe\n', '[includeIf "onbranch:main"]\npath = /tmp/probe\n',
                 '[core]\nworktree = /tmp/probe\n', '[extensions]\npartialClone = origin\n',
                 '[core]\nfutureUnknown = true\n', '[core]\nfilemode = true\\\nfalse\n']
        for number, suffix in enumerate(cases):
            with self.subTest(case=number):
                config.write_bytes(original + b"\n" + suffix.encode())
                self.assert_no_git_starts()
        config.write_bytes(original)

    def test_path_selected_git_wrapper_is_refused_without_execution(self):
        plan = self.plan()
        marker = self.directory / "WRAPPER-EXECUTED"
        directory = self.directory / "bin"
        directory.mkdir()
        wrapper = directory / "git"
        wrapper.write_text("#!/bin/sh\nprintf 'callback\\n' >> " + shlex.quote(str(marker)) + "\nexit 99\n")
        wrapper.chmod(0o700)
        self.env["PATH"] = str(directory) + os.pathsep + self.env.get("PATH", os.defpath)
        self.assert_observation_refused(self.invoke(plan), marker)
        self.assert_no_git_starts()

    def test_admitted_config_change_has_its_own_currentness_binding(self):
        plan = self.plan()
        self.assertIn("git_observation_sha256", plan["expected_currentness"])
        self.append_git_config('\n[user]\nname = Changed Binding\n')
        value = self.report(self.invoke(plan), 1)
        self.assertIn("git_observation_sha256", value["currentness"]["mismatches"])
        self.assertNotIn("source_sha256", value["currentness"]["mismatches"])

    def test_supported_observation_preserves_actual_source_identity(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            actual = self.owner.source_identity()
            binding = self.owner.verifier_preflight_currentness_v1()
        self.assertEqual(binding["source_sha256"], digest(self.owner.WG.canonical_json_v1(actual)))
        self.assertEqual(binding["base_environment_sha256"], self.owner.environment_digest(self.env))
        self.assertIn("git_observation_sha256", binding)
        value = self.report(self.invoke(self.plan()), 0)
        self.assertTrue(value["currentness"]["matches"])
        self.assertEqual(value["currentness"]["git_observation_policy"], "DECLARED_ISOLATED_GIT_CONFIG_V1")

    def test_missing_git_observation_binding_refuses(self):
        plan = self.plan()
        plan["expected_currentness"].pop("git_observation_sha256", None)
        result = self.invoke(plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"preflight currentness", result.stderr)

    def test_linked_worktree_configuration_selection_is_bound_and_checked(self):
        linked = self.directory / "linked-source"
        for arguments in (("config", "extensions.worktreeConfig", "true"),
                          ("worktree", "add", "--detach", str(linked))):
            subprocess.run(["git", *arguments], cwd=self.repo, env=self.env, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        common = self.repo / ".git"
        self.repo = linked
        spec = importlib.util.spec_from_file_location("linked_preflight_owner", linked / "scripts/qualify-work-graph-verifier.py")
        self.owner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.owner)
        gitdir = Path((linked / ".git").read_text().strip()[8:])
        config = gitdir / "config.worktree"
        config.write_text("[user]\nname = Worktree Binding\n")
        plan = self.plan()
        value = self.report(self.invoke(plan), 0)
        self.assertTrue(value["currentness"]["matches"])
        with mock.patch.dict(os.environ, self.env, clear=True):
            observation = self.owner._preflight_git_context_v1()["binding"]
        self.assertEqual(observation["common_directory"], str(common))
        self.assertEqual(observation["git_directory"], str(gitdir))
        selected = {item["path"] for item in observation["controls"]}
        for path in (common / "config", config, gitdir / "HEAD", linked / ".git", gitdir / "commondir"):
            self.assertIn(str(path), selected)
        config.write_text("[includeIf \"onbranch:main\"]\npath = /tmp/unadmitted-include\n")
        self.assert_no_git_starts()

    def test_aliased_config_is_refused_before_any_git(self):
        config = self.repo / ".git/config"
        target = self.directory / "aliased-config"
        target.write_bytes(config.read_bytes())
        config.unlink()
        config.symlink_to(target)
        self.assert_no_git_starts()

    def test_gitlink_stops_before_status_can_observe_another_repository(self):
        plan = self.plan()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, env=self.env).decode().strip()
        subprocess.run(["git", "update-index", "--add", "--cacheinfo", "160000", commit, "nested"],
                       cwd=self.repo, env=self.env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = self.invoke(plan)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"refuses gitlinks", result.stderr)
        original = self.owner.subprocess.check_output
        with mock.patch.dict(os.environ, self.env, clear=True), \
                mock.patch.object(self.owner.subprocess, "check_output", wraps=original) as launch:
            with self.assertRaisesRegex(self.owner.WG.WorkGraphError, "refuses gitlinks"):
                self.owner.verifier_preflight_currentness_v1()
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(launch.call_args.args[0][-3:], ["ls-files", "--stage", "-z"])

    def test_environment_changed_after_binding_blocks_without_revealing_value(self):
        plan = self.plan()
        changed = dict(self.env, R0035_PREFLIGHT_TEST_NAMESPACE="test-private-namespace")
        result = self.invoke(plan, env=changed)
        value = self.report(result, 1)
        self.assertFalse(value["currentness"]["matches"])
        self.assertIn("base_environment_sha256", value["currentness"]["mismatches"])
        self.assertNotIn(b"test-private-namespace", result.stdout + result.stderr)

    def test_schema_and_stdin_conflicts_are_diagnosed_without_capture(self):
        plan = self.plan()
        plan["runs"][1]["capture"]["empty_stdin"] = True
        value = self.report(self.invoke(plan), 1)
        self.assertIn("same_record_schema", value["guaranteed_false_predicates"])
        plan = self.plan()
        for run in plan["runs"]:
            run["capture"]["capture_dist"] = True
        plan["runs"][1]["capture"]["empty_stdin"] = True
        value = self.report(self.invoke(plan), 1)
        self.assertIn("same_stdin", value["guaranteed_false_predicates"])

    def test_missing_digest_duplicate_route_unknown_option_and_relative_path_refuse(self):
        mutations = [(lambda p: p["expected_currentness"].pop("source_sha256"), b"preflight currentness"),
                     (lambda p: p["runs"][1].update(mode="legacy"), b"preflight route pair"),
                     (lambda p: p["runs"][0]["capture"].update(ignored_capture=True), b"preflight capture"),
                     (lambda p: p["runs"][0].update(output="relative-output"), b"preflight output")]
        for mutate, reason in mutations:
            with self.subTest(reason=reason):
                plan = self.plan()
                mutate(plan)
                result = self.invoke(plan)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(reason, result.stderr)

    def test_same_output_root_cannot_be_a_conflict_free_launch_plan(self):
        plan = self.plan()
        plan["runs"][1]["output"] = plan["runs"][0]["output"]
        value = self.report(self.invoke(plan), 1)
        self.assertIn("OUTPUT_NAMESPACE_COLLISION", value["blocking_reasons"])

    def test_duplicate_keys_and_oversized_plan_refuse(self):
        valid = json.dumps(self.plan()).encode()
        duplicate = valid[:-1] + b',"schema":"implementaudit.verifier-pair-plan.v1"}'
        for raw, reason in ((duplicate, b"duplicate key"), (b" " * 65537, b"preflight plan exceeds byte limit")):
            with self.subTest(bytes=len(raw)):
                result = self.invoke(raw=raw)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(reason, result.stderr)

    def test_currentness_change_during_preflight_blocks(self):
        plan = self.plan()
        self.assertTrue(hasattr(self.owner, "preflight_verifier_pair_v1"), "paired preflight API is absent")
        original = self.owner.source_identity
        reads = 0

        def observe_then_change(**kwargs):
            nonlocal reads
            value = original(**kwargs)
            reads += 1
            if reads == 1:
                (self.repo / "subject.txt").write_text("changed within read-only preflight\n")
            return value

        # Only the observation timing boundary is instrumented. Both returned
        # source observations are obtained from the real filesystem owner.
        with mock.patch.dict(os.environ, self.env, clear=True), \
                mock.patch.object(self.owner, "source_identity", side_effect=observe_then_change):
            value = self.owner.preflight_verifier_pair_v1(plan)
        self.assertEqual(value["status"], "BLOCKED")
        self.assertFalse(value["currentness"]["matches"])
        self.assertIn("CURRENTNESS_CHANGED_DURING_PREFLIGHT", value["blocking_reasons"])
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--retain-fixtures", type=Path)
    options, remaining = parser.parse_known_args()
    if options.retain_fixtures is not None:
        RETAIN = options.retain_fixtures.resolve()
        RETAIN.mkdir(parents=True, exist_ok=False)
    unittest.main(argv=[sys.argv[0], *remaining])
