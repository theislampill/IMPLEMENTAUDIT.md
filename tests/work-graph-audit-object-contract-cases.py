#!/usr/bin/env python3
"""Finite original73 source controls; original execution requires allocation."""
import hashlib
import errno
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
PROFILE = "CONTROLLED_TASK_AUDIT_OBJECT_CONTRACT_V1"
spec = importlib.util.spec_from_file_location("audit_object_contract_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
ENVIRONMENT = dict(P.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1")
GIT_OWNER = dict(context=Q._preflight_git_context_v1, capture=Q._preflight_git_capture_v1)
ROUTING = "fixtures/audit-object-routing"
PROCESS = ROUTING + "/process-history-run"
POPULATION = ("for-each-ref", "--format=%(refname)%09%(symref)%09%(objecttype)",
    "refs/implementaudit/controllers/", "refs/implementaudit/current-generations/",
    "refs/implementaudit/current-generation-migrations/")


def load_helper():
    path = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
    spec = importlib.util.spec_from_file_location("audit_object_contract_finite", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CopyImageCases(unittest.TestCase):
    """Constructed transport controls never simulate successful execution."""

    def test_fixed_copy_directory_defaults_preserve_transport_and_other_profiles(self):
        helper = load_helper()
        original = {
            '/work/aa-executable': (b'executable source bytes', 0o755),
            '/work/nested/data': (b'data\x00\xff', 0o644),
            '/work/nested/readonly': (b'readonly source', 0o444),
            '/usr/bin/runtime': (b'constructed runtime', 0o555),
            '/usr/lib/runtime-data': (b'runtime data', 0o444),
        }
        observations = []
        for copy_policy in (True, False):
            files = helper.copy_readonly_image(original) if copy_policy else dict(original)
            self.assertEqual(set(files), set(original))
            with self.subTest(copy_policy=copy_policy), tempfile.TemporaryDirectory() as temporary:
                session = Q.VerifierTaskSession(ROOT, Path(temporary) / 'evidence')
                manifest, _ = session._image(files, {})
                manifest['directories'] += ['/work/empty', '/work/empty/deeper', '/work/empty-peer']
                if copy_policy:
                    manifest.update(source_materialization='SINGLE_LINK_FILES_READ_ONLY_ROOT',
                        data_permissions='OWNER_0600_READ_ONLY_MOUNT',
                        source_permissions='COPY_0666_UMASK_022_READ_ONLY_ROOT', copy_umask=0o022)
                image_key = session._object(session._encode(manifest))
                node = dict(id='CONSTRUCTED:directory-defaults', source='false\n', source_sha256=Q.sha(b'false\n'))
                acquired = dict(images={node['id']: (files, manifest)},
                    acquired=dict(inputs={node['id']: dict(image_digest=image_key)}))
                held = []
                def deny(argv, **options):
                    self.assertEqual(argv[:2], ['/usr/bin/bwrap', '--args'])
                    raw = os.pread(int(argv[2]), 1024 * 1024, 0)
                    self.assertTrue(raw.endswith(b'\0'))
                    args = raw[:-1].decode().split('\0')
                    directory_ops = [(i, args[i+1]) for i, arg in enumerate(args[:-1]) if arg == '--dir']
                    expected = set(manifest['directories']) | {'/dev', '/tmp'}
                    self.assertEqual({name for _, name in directory_ops}, expected)
                    self.assertEqual(len(directory_ops), len(expected))
                    for index, name in directory_ops:
                        if copy_policy:
                            self.assertNotEqual(args[index-2:index], ['--perms', '0755'])
                        else:
                            self.assertEqual(args[index-2:index], ['--perms', '0755'])
                    self.assertIn('--remount-ro', args)
                    for name, (data, mode) in files.items():
                        at = args.index(name)
                        kind = '--file' if copy_policy and name.startswith('/work/') else '--ro-bind-data'
                        self.assertEqual(args[at-2], kind)
                        self.assertEqual(data, original[name][0])
                        self.assertEqual(os.pread(int(args[at-1]), len(data)+1, 0), data)
                        default_mode = (kind, mode) in (('--file', 0o666), ('--ro-bind-data', 0o600))
                        if default_mode:
                            self.assertNotEqual(args[at-4:at-2], ['--perms', oct(mode)[2:]])
                        else:
                            self.assertEqual(args[at-4:at-2], ['--perms', oct(mode)[2:]])
                    held.extend(options['pass_fds'])
                    for fd in held:
                        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GET_SEALS), 15)
                    observations.append(dict(copy_policy=copy_policy, directories=len(expected),
                        files=len(files), expanded_arguments=len(args)+len(argv)-1,
                        namespace_dispatched=False, successful_execution_mocked=False))
                    raise OSError(errno.EPERM, 'constructed directory transport denial; no child launched')
                with mock.patch.object(Q.subprocess, 'Popen', side_effect=deny):
                    with self.assertRaisesRegex(OSError, 'constructed directory transport denial'):
                        session._execute(acquired, node, {'key': 'constructed'}, session.output / 'execution')
                self.assertTrue(held)
                for fd in held:
                    with self.assertRaises(OSError) as error:
                        os.fstat(fd)
                    self.assertEqual(error.exception.errno, errno.EBADF)
                self.assertEqual(session.dispatch_count, 0)
                self.assertFalse((session.output / 'execution/receipt.json').exists())
                self.assertFalse((session.output / 'execution/exit-code.txt').exists())
        print(json.dumps(dict(scope='CONSTRUCTED_LAUNCH_VECTOR_ONLY', observations=observations), sort_keys=True))

    def test_complete_linked_copy_image_preserves_bytes_and_bounds_arguments(self):
        helper = load_helper()
        original = {
            "/work/aa-executable": (b"original executable bytes", 0o755),
            "/work/ab-data": (b"original data\x00\xff", 0o644),
            "/work/ac-readonly": (b"readonly copy remains0444", 0o444),
            "/usr/bin/engine": (b"constructed runtime executable", 0o555),
            "/usr/lib/runtime-data": (b"captured runtime data", 0o444),
            **{"/work/population/member-%04d" % i: (str(i).encode(), 0o644) for i in range(2190)},
        }
        files = helper.copy_readonly_image(original)
        self.assertEqual(set(files), set(original))
        for name, (data, mode) in original.items():
            self.assertEqual(files[name][0], data)
            self.assertEqual(files[name][1], (0o666 if mode == 0o644 else mode) if name.startswith('/work/')
                else (0o600 if mode == 0o444 else mode))
        with self.assertRaisesRegex(ValueError, 'copy image'):
            helper.copy_readonly_image({'/work/foreign-mode': (b'x', 0o600)})
        with tempfile.TemporaryDirectory() as temporary:
            session = Q.VerifierTaskSession(ROOT, Path(temporary) / 'evidence')
            manifest, _ = session._image(files, {})
            manifest.update(source_materialization='SINGLE_LINK_FILES_READ_ONLY_ROOT',
                data_permissions='OWNER_0600_READ_ONLY_MOUNT',
                source_permissions='COPY_0666_UMASK_022_READ_ONLY_ROOT', copy_umask=0o022)
            manifest['directories'] += ['/work/empty-%03d' % i for i in range(325)]
            key = session._object(session._encode(manifest))
            node = dict(id='CONSTRUCTED:copy-transport', source='false\n', source_sha256=Q.sha(b'false\n'))
            acquired = dict(images={node['id']: (files, manifest)}, acquired=dict(inputs={node['id']: dict(image_digest=key)}))
            held = []
            def deny(argv, **options):
                self.assertEqual(argv[:2], ['/usr/bin/bwrap', '--args'])
                args = os.pread(int(argv[2]), 1024 * 1024, 0)[:-1].decode().split('\0')
                self.assertLessEqual(len(args) + len(argv) - 1, 8500)
                self.assertIn('--remount-ro', args)
                for name, (raw, mode) in files.items():
                    at = args.index(name)
                    expected = '--file' if name.startswith('/work/') else '--ro-bind-data'
                    self.assertEqual(args[at - 2], expected)
                    self.assertEqual(os.pread(int(args[at - 1]), len(raw) + 1, 0), raw)
                    if (expected, mode) in (('--file', 0o666), ('--ro-bind-data', 0o600)):
                        self.assertNotEqual(args[at - 4:at - 2], ['--perms', oct(mode)[2:]])
                    else:
                        self.assertEqual(args[at - 4:at - 2], ['--perms', oct(mode)[2:]])
                held.extend(options['pass_fds'])
                for fd in held:
                    self.assertEqual(fcntl.fcntl(fd, fcntl.F_GET_SEALS), 15)
                raise OSError(errno.EPERM, 'constructed transport denial; no child launched')
            with mock.patch.object(Q.subprocess, 'Popen', side_effect=deny):
                with self.assertRaisesRegex(OSError, 'constructed transport denial'):
                    session._execute(acquired, node, {'key': 'constructed'}, session.output / 'execution')
            self.assertTrue(held)
            for fd in held:
                with self.assertRaises(OSError) as error:
                    os.fstat(fd)
                self.assertEqual(error.exception.errno, errno.EBADF)
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / 'execution/exit-code.txt').exists())

    def test_copy_policy_requires_readonly_linked_materialization_and_closed_umask(self):
        files = {'/work/data': (b'fixed copy source', 0o666)}
        valid = dict(source_materialization='SINGLE_LINK_FILES_READ_ONLY_ROOT',
            data_permissions='OWNER_0600_READ_ONLY_MOUNT',
            source_permissions='COPY_0666_UMASK_022_READ_ONLY_ROOT', copy_umask=0o022)
        cases = [dict(source_permissions=None), dict(source_permissions='foreign'),
            dict(source_materialization=None), dict(root_read_only=False),
            dict(data_permissions=None), dict(copy_umask=0), dict(copy_umask=None)]
        with tempfile.TemporaryDirectory() as temporary:
            session = Q.VerifierTaskSession(ROOT, Path(temporary) / 'evidence')
            node = dict(id='constructed', source='false\n', source_sha256=Q.sha(b'false\n'))
            for number, changes in enumerate(cases):
                manifest, _ = session._image(files, {})
                manifest.update(valid, **changes)
                acquired = dict(images={'constructed': (files, manifest)},
                    acquired=dict(inputs={'constructed': dict(image_digest='constructed')}))
                with self.subTest(changes=changes), mock.patch.object(Q.subprocess, 'Popen',
                        side_effect=AssertionError('unowned source permission policy reached dispatch')):
                    with self.assertRaisesRegex(ValueError, 'materialization|permissions'):
                        session._execute(acquired, node, {'key': 'constructed'}, session.output / ('denied-' + str(number)))
            manifest, _ = session._image({'/usr/lib/foreign': (b'x', 0o666)}, {})
            manifest.update(valid)
            with mock.patch.object(Q.subprocess, 'Popen', side_effect=AssertionError('foreign runtime mode reached dispatch')):
                with self.assertRaisesRegex(ValueError, 'permissions'):
                    session._execute(dict(images={'constructed': ({'/usr/lib/foreign': (b'x', 0o666)}, manifest)},
                        acquired=dict(inputs={'constructed': dict(image_digest='constructed')})),
                        node, {'key': 'constructed'}, session.output / 'foreign-runtime')
            self.assertEqual(session.dispatch_count, 0)


class CatalogCases(unittest.TestCase):
    def test_original73_profile_is_explicitly_available(self):
        helper = load_helper()
        missing = []
        try:
            helper.contract_for(PROFILE)
        except ValueError:
            missing.append(PROFILE)
        self.assertEqual(missing, [], "missing exact original73 profile")

    def test_original_mapping_full_import_closure_and_private_copy_modes(self):
        helper = load_helper()
        contract = helper.contract_for(PROFILE)
        graph, scope, node = helper.select_node(Q.WG, H.original("scripts/verify-package.sh"), ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][73]))
        self.assertEqual(node["source"], "bash tests/audit-object-routing-contract.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])),
            (["COMMAND:tests/audit-object-routing-contract.test.sh:0"], 116))
        self.assertEqual(Q._FINITE_MODES["audit-object-contract"], PROFILE)
        self.assertEqual(set(contract["programs"]), {
            "tests/audit-object-routing-contract.test.sh", "scripts/check-audit-object-routing-contract.sh",
            "scripts/check-cold-review-contract.sh", "skills/implementaudit/scripts/validate-run-root.sh",
            "skills/implementaudit/scripts/check-closure-surface.sh", "skills/implementaudit/scripts/read-canonical-pair.py",
            "skills/implementaudit/scripts/canonical_custody.py"})
        for name, pin in contract["programs"].items():
            self.assertEqual(hashlib.sha256(H.input_bytes(name)).hexdigest(), pin)
        self.assertEqual(contract["source_modes"], "COPY_0666_UMASK_022_READ_ONLY_ROOT")
        self.assertEqual(len(helper.source_paths(PROFILE)), 23)
        self.assertEqual(set(contract["pinned_data"]), {helper.RUNNER, PROCESS + "/mission.json", PROCESS + "/result.json"})
        self.assertEqual(set(contract["pinned_trees"]), {
            ROUTING + "/retrospective", "fixtures/run-root/micro-conformant",
            "fixtures/run-root/micro-with-stage62-disposition", "fixtures/run-root/no-sentinel-legacy"})
        self.assertEqual({"bash", "dirname", "git", "grep", "cat", "rm", "mktemp", "head", "sed", "tr",
                          "wc", "find", "mkdir", "cp", "awk", "basename", "python3.12"} - set(P.TOOLS), set())


class ContractFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        if not self.SOURCE_ADMISSION_ONLY:
            template = Path(os.environ.get("R0035_FINITE_AUDIT_OBJECT_CONTRACT_SOURCE", str(ROOT)))
            shutil.rmtree(self.source)
            shutil.copytree(template, self.source, symlinks=True, copy_function=shutil.copy2)
            return
        # Constructed source controls use a genuine owned repository. They never
        # execute an original checker, substitute Git output, or issue a receipt.
        for name in ("skills", ROUTING, "fixtures/run-root/micro-conformant",
                     "fixtures/run-root/micro-with-stage62-disposition", "fixtures/run-root/no-sentinel-legacy"):
            shutil.copytree(ROOT / name, self.source / name, dirs_exist_ok=True)
        self.git("init", "--quiet", "--template=", str(self.source))
        self.git("-C", str(self.source), "add", "--all")
        self.restore_historical_inputs()

    def git(self, *args, data=None):
        options = dict(input=data) if data is not None else dict(stdin=subprocess.DEVNULL)
        result = subprocess.run(["/usr/bin/git", *args], cwd=self.base, env=ENVIRONMENT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, **options)
        self.assertEqual((result.returncode, result.stderr), (0, b""))
        return result.stdout

    def snapshot(self, *, git_owner=GIT_OWNER):
        objects = {}
        state, stamps = self.A.snapshot_source(P, self.source, objects, profile=PROFILE,
            git_owner=git_owner, environment=ENVIRONMENT)
        return state, stamps, objects

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))

    def semantic_mutation(self):
        path = self.source / "skills/implementaudit/references/audit-category-matrix.md"
        raw = path.read_bytes()
        self.assertIn(b"## Native Category Route Contract", raw)
        path.write_bytes(raw.replace(b"## Native Category Route Contract", b"## Removed Category Route Contract"))
        return (b"check-audit-object-routing-contract: missing in "
                b"skills/implementaudit/references/audit-category-matrix.md: ## Native Category Route Contract")


class AdmissionCases(ContractFixture, unittest.TestCase):
    def test_complete_read_copy_glob_and_git_namespaces_use_actual_bytes(self):
        hidden = self.source / ROUTING / ".complete-population/.binary"
        hidden.parent.mkdir()
        hidden.write_bytes(b"\xff\x00 retained by cp and recursive grep\n")
        (hidden.parent / ".empty").mkdir()
        (self.source / PROCESS / "RC-artifacts").mkdir()
        state, stamps, objects = self.snapshot()
        expected = {path.relative_to(self.source).as_posix() for path in self.source.rglob("*") if path.is_file()}
        self.assertEqual(set(state["files"]), expected)
        self.assertEqual(self.A.image_subject(state, profile=PROFILE), state["files"])
        for name, entry in state["files"].items():
            self.assertEqual(objects[entry["sha256"]], (self.source / name).read_bytes())
            self.assertEqual(entry["mode"], (self.source / name).stat().st_mode & 0o777)
        for name in (ROUTING + "/.complete-population/.empty", PROCESS + "/RC-artifacts", ".git/objects/info"):
            self.assertIn(name, state["directories"])
        details = state["complete_git_inputs"]
        self.assertEqual(stamps["complete_git_inputs"], details)
        population = details["controller_population"]
        self.assertEqual([row["argv"][2:] for row in population["observations"]],
            [["rev-parse", "--show-toplevel"], list(POPULATION)])
        top, refs = population["observations"]
        self.assertEqual(objects[top["stdout_sha256"]], os.fsencode(str(self.source)) + b"\n")
        self.assertEqual(objects[refs["stdout_sha256"]], b"")
        self.assertEqual((refs["exit"], refs["stderr_bytes"]), (0, 0))

    def test_program_dynamic_selectors_and_native_branch_changes_refuse(self):
        examples = (
            ("skills/implementaudit/scripts/canonical_custody.py", b"\n", "executable"),
            (PROCESS + "/mission.json", b"\n", "pinned branch"),
            (ROUTING + "/retrospective/retired-with-reason/root/STATE.md", b"\ncold-review: changed selector\n", "legacy branch tree"),
        )
        for name, change, diagnostic in examples:
            path = self.source / name
            before = path.read_bytes()
            path.write_bytes(before + change)
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, diagnostic):
                    self.snapshot()
            finally:
                path.write_bytes(before)
        root = self.source / "fixtures/run-root/micro-conformant/root"
        for name, raw in ((".controller", b"controller_id=not-authority\n"),
                          ("respec-impact-set.md", b"new reader selector\n")):
            path = root / name
            path.write_bytes(raw)
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "legacy branch tree"):
                    self.snapshot()
            finally:
                path.unlink()
        (root / "phases").mkdir()
        with self.assertRaisesRegex(ValueError, "legacy branch tree"):
            self.snapshot()

    def test_actual_loose_and_packed_controller_refs_are_never_invented_absent(self):
        oid = self.git("-C", str(self.source), "hash-object", "-w", "--stdin", data=b"ordinary blob, no native authority\n").strip().decode()
        self.git("-C", str(self.source), "update-ref", "refs/source-control/unrelated", oid)
        self.snapshot()  # Non-controller refs are a genuinely observed population.
        ref = "refs/implementaudit/controllers/observed-control"
        self.git("-C", str(self.source), "update-ref", ref, oid)
        with self.assertRaisesRegex(ValueError, "actually observed empty controller-ref population"):
            self.snapshot()
        self.git("-C", str(self.source), "pack-refs", "--all")
        self.assertFalse((self.source / ".git" / ref).exists())
        self.assertIn(ref.encode(), (self.source / ".git/packed-refs").read_bytes())
        with self.assertRaisesRegex(ValueError, "actually observed empty controller-ref population"):
            self.snapshot()

    def test_new_c2_scope_is_fixed_disjoint_and_does_not_expand58(self):
        context = Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT, finite_controller_population=True)
        self.assertEqual(Q._preflight_git_capture_v1(context, ("rev-parse", "--show-toplevel")),
                         os.fsencode(str(self.source)) + b"\n")
        self.assertEqual(Q._preflight_git_capture_v1(context, POPULATION), b"")
        for args in (("ls-files", "-z"), ("cat-file", "blob", "refs/implementaudit/controllers/unused"),
                     ("for-each-ref", "--format=%(refname)", "refs/")):
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, "fixed command"):
                Q._preflight_git_capture_v1(context, args)
        old = Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT, finite_ls_files=True)
        with self.assertRaisesRegex(ValueError, "fixed command"):
            Q._preflight_git_capture_v1(old, POPULATION)
        with self.assertRaisesRegex(ValueError, "one fixed finite profile"):
            Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT,
                                       finite_ls_files=True, finite_controller_population=True)
        layout = Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT,
                                             finite_skill_layout=True)
        observed = Q._preflight_git_capture_v1(layout, ("ls-files", "--error-unmatch", "skills/SKILL.md"))
        self.assertEqual((observed["exit"], observed["stdout"]), (1, b""))
        self.assertIn(b"did not match", observed["stderr"])
        with self.assertRaisesRegex(ValueError, "fixed command"):
            Q._preflight_git_capture_v1(layout, POPULATION)
        selectors = ("finite_ls_files", "finite_skill_layout", "finite_controller_population")
        with mock.patch.object(Q, "require_source_descriptor_api", side_effect=AssertionError("source accessed")):
            for left, right in ((0, 1), (0, 2), (1, 2)):
                with self.subTest(selectors=(left, right)), self.assertRaisesRegex(ValueError, "one fixed finite profile"):
                    Q._preflight_git_context_v1(**{selectors[left]: True, selectors[right]: True})
            for name in selectors:
                with self.subTest(non_boolean=name), self.assertRaisesRegex(ValueError, "one fixed finite profile"):
                    Q._preflight_git_context_v1(**{name: 1})

    def test_real_git_warning_cannot_be_treated_as_an_empty_clean_population(self):
        path = self.source / ".git/refs/implementaudit/controllers/broken"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not an object id\n")
        context = Q._preflight_git_context_v1(root=self.source, environment=ENVIRONMENT, finite_controller_population=True)
        actual_run, observations = Q.subprocess.run, []
        def retain_actual(*args, **options):
            result = actual_run(*args, **options)
            observations.append(result)
            return result
        with mock.patch.object(Q.subprocess, "run", side_effect=retain_actual):
            with self.assertRaisesRegex(ValueError, "actual exit or stderr"):
                Q._preflight_git_capture_v1(context, POPULATION)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].returncode, 0)
        self.assertTrue(observations[0].stderr)
        self.assertEqual(observations[0].stdout, b"")

    def test_ref_added_after_actual_observation_fails_complete_currentness(self):
        oid = self.git("-C", str(self.source), "hash-object", "-w", "--stdin", data=b"late actual ref\n").strip().decode()
        observed = []
        def observe_then_change(context, args):
            raw = Q._preflight_git_capture_v1(context, args)
            if args == POPULATION:
                observed.append(raw)
                self.git("-C", str(self.source), "update-ref", "refs/implementaudit/controllers/late", oid)
            return raw
        with self.assertRaisesRegex(ValueError, "changed during controller observation"):
            self.snapshot(git_owner=dict(GIT_OWNER, capture=observe_then_change))
        self.assertEqual(observed, [b""])

    def test_full_private_allocation_refuses32_and_later_population_above64(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["private_file_entries"], reservation["private_directories"]), (363, 125))
        self.assertEqual((reservation["files"], reservation["directories"], reservation["reader_snapshot_directories"]), (394, 147, 22))
        self.assertEqual((reservation["sed_temporaries"], reservation["possible_heredoc_spools"], reservation["original_checker_calls"]), (11, 14, 36))
        self.assertEqual(reservation["required_bytes"], 62390272)
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 64 * 1024**2)
        with self.assertRaisesRegex(ValueError, "temporary write set exceeds scratch capacity") as old_refusal:
            self.A.require_resource_capacity(reservation, dict(session.LIMITS, scratch_bytes=32 * 1024**2))
        print(json.dumps(dict(control="ORIGINAL73_32MIB_REFUSAL", required_bytes=reservation["required_bytes"],
            available_bytes=32 * 1024**2, actual_exception=str(old_refusal.exception), original_executions=0), sort_keys=True))
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for number in range(32):
            (self.source / ROUTING / (".owned-capacity-%02d" % number)).write_bytes(b"")
        changed, _, _ = self.snapshot()
        larger = self.A.temporary_requirements(changed, profile=PROFILE)
        self.assertGreater(larger["required_bytes"], 64 * 1024**2)
        with self.assertRaisesRegex(ValueError, "temporary write set exceeds scratch capacity"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertFalse((session.output / "objects").exists())

    def test_invalid_utf8_and_hidden_match_lines_still_receive_report_capacity(self):
        baseline, _, _ = self.snapshot()
        name = ROUTING + "/.raw-grep-input"
        raw = b"\xff undecodable first line\n" + b"/implementaudit deep source-data\n" * 5000
        (self.source / name).write_bytes(raw)
        state, _, objects = self.snapshot()
        bound = state["complete_git_inputs"]["resources"]
        prior = baseline["complete_git_inputs"]["resources"]
        visible = sum(len(name.encode()) + len(str(number)) + 2 + len(line) + 1
                      for number, line in enumerate(raw.split(b"\n"), 1) if b"/implementaudit " in line)
        self.assertGreaterEqual(bound["report_file_bound"] - prior["report_file_bound"], visible)
        self.assertEqual(objects[state["files"][name]["sha256"]], raw)
        self.assertGreater(bound["diagnostic_file_bound"], prior["diagnostic_file_bound"])
        self.assertEqual(bound["private_file_entries"] - prior["private_file_entries"], 3)

    def test_semantic_mutation_remains_original_input_without_a_mock_receipt(self):
        before, _, _ = self.snapshot()
        self.semantic_mutation()
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        name = "skills/implementaudit/references/audit-category-matrix.md"
        self.assertEqual(objects[after["files"][name]["sha256"]], (self.source / name).read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("result.json")), [])


class LiveCases(ContractFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_AUDIT_OBJECT_CONTRACT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_AUDIT_OBJECT_CONTRACT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_AUDIT_OBJECT_CONTRACT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-audit-object-contract-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/audit-object-routing-contract.test.sh:0")
        self.assertEqual((result["group"]["nodes"], len(result["group"]["omitted_nodes"])), ([receipt["node"]], 116))
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_input_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
            (0, True, b"check-audit-object-routing-contract: ok\naudit-object-routing-contract.test: ok\n", b""))
        second, out2, err2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["key"], first["receipt_digest"], stdout, stderr),
            (second["key"], second["receipt_digest"], out2, err2))
        self.semantic_mutation()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout, stderr), (1, True, b"", diagnostic + b"\n"))
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
