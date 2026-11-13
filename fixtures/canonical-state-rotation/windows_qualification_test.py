#!/usr/bin/env python3
"""Constructed evidence-gate controls; no Windows or native acceptance claim."""
import copy
import contextlib
import hashlib
import importlib.util
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / 'scripts/check-r0039-windows-resume.py'


def load():
    spec = importlib.util.spec_from_file_location('r0039_windows_qualification', PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TOOLS = {name: {'path': 'C:/' + name + '/' + name + '.exe', 'sha256': digit * 64}
         for name, digit in [('bash', 'a'), ('python', 'b'), ('git', 'c')]}
COMMAND = [TOOLS['bash']['path'], '--noprofile', '--norc',
           'C:/subject/skills/implementaudit/scripts/claim-run.sh',
           '--resume-controller', 'dg30-test', '--boundary', 'manual-resume', '--epoch', 'G0003',
           '--expected-pointer', 'refs/implementaudit/current-generations/dg30-test@' + '1' * 40,
           '--expected-invalidation', 'refs/implementaudit/continuity-invalidations/dg30-test@' + '2' * 40]


def measurement():
    return {'schema': 'implementaudit.windows-job-measurement.v1', 'platform': 'win32',
            'command': COMMAND[:], 'exit_code': 0, 'elapsed_ms': 60000.0,
            'root_exit_observed_ms': 59999.0, 'peak_job_committed_bytes': 201326592,
            'peak_single_process_committed_bytes': 64000000, 'kernel_total_processes': 3,
            'terminal_active_processes': 0, 'root_pid': 10, 'started_suspended': True,
            'root_job_membership_confirmed': True, 'assigned_before_resume': True,
            'initial_job_flags': 8192, 'terminal_job_flags': 8192,
            'terminal_breakaway_allowed': False, 'baseline_subtracted_bytes': 0,
            'harness_included': False, 'sampled_pid_census_complete': False,
            'complete_memory_scope_valid': True, 'metric_admission': 'UNADMITTED_DIAGNOSTIC',
            'completion_port_associated_before_assignment': True, 'cleanup_complete': True,
            'status': 'COMPLETE_UNADMITTED',
            'creation_event_count': 3, 'exit_event_count': 3,
            'process_events': [{'event': 'NEW_PROCESS', 'pid': p} for p in (10, 11, 12)] +
                              [{'event': 'EXIT_PROCESS', 'pid': p} for p in (12, 11, 10)] +
                              [{'event': 'ACTIVE_PROCESS_ZERO', 'pid': 0}],
            'observed_processes': [dict(pid=p, image=TOOLS[name]['path'],
                                       image_sha256=TOOLS[name]['sha256'], in_job=True)
                                   for p, name in [(10, 'bash'), (11, 'python'), (12, 'git')]]}


def transition_fixture():
    pointer = {'schema': 'implementaudit.current-generation.v1', 'controller': 'dg30-test',
               'claim_id': 'claim-test', 'run_root_identity': '.IMPLEMENTAUDIT/runs/dg30-test',
               'continuity_epoch': 'G0002', 'projection_generation_id': 'G0002',
               'exact_next_action': 'Retain pending obligations',
               'state_sha256': '3' * 64, 'roadmap_sha256': '4' * 64,
               'protected_manifest_sha256': '5' * 64, 'archive_manifest_sha256': '6' * 64}
    before = dict(schema='implementaudit.native-resume-source.v1', status='PRE_RESUME_EVIDENCE',
                  controller='dg30-test', claim_id='claim-test', run_root_identity=pointer['run_root_identity'],
                  boundary='manual-resume', next_continuity_epoch='G0003', next_projection_generation_id='G0003',
                  pointer_token=COMMAND[-3], invalidation_token=COMMAND[-1], marker_oid='7' * 40,
                  receipt_token='refs/implementaudit/continuity-receipts/dg30-test/G0002@' + '8' * 40,
                  pointer=pointer)
    new = dict(pointer, continuity_epoch='G0003', projection_generation_id='G0003')
    blob = json.dumps(new, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    oid = hashlib.sha1(b'blob ' + str(len(blob)).encode() + b'\0' + blob).hexdigest()
    after = dict(before, schema='implementaudit.canonical-generation-resolution.v1', pointer=new,
                 pointer_token='refs/implementaudit/current-generations/dg30-test@' + oid)
    fields = ['implementaudit.continuity-receipt.v3', 'dg30-test', 'claim-test', pointer['run_root_identity'],
              'G0003', '2' * 40, *after['pointer_token'].split('@'), new['state_sha256'], new['roadmap_sha256'],
              new['protected_manifest_sha256'], new['archive_manifest_sha256'], new['exact_next_action'], before['receipt_token']]
    raw = ('\t'.join(fields) + '\n').encode()
    oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    after['receipt_token'] = 'refs/implementaudit/continuity-receipts/dg30-test/G0003@' + oid
    payloads = {'STATE': {'pending': ['uncovered'], 'unknown': ['retained']}, 'ROADMAP': {'next': 'Retain pending obligations'}}
    retained = {'files': {name: {'bytes': 1, 'sha256': 'a' * 64} for name in
                ('STATE', 'ROADMAP', 'protected', 'archive', 'retired_STATE', 'retired_ROADMAP')},
                'refs': {before['receipt_token'].split('@')[0]: '8' * 40,
                         'refs/implementaudit/current-generation-migrations/dg30-test': '7' * 40,
                         'refs/implementaudit/state-archives/dg30-test/G0002': '9' * 40}}
    return before, after, raw, payloads, retained


class QualificationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()

    def accept(self, raw):
        return self.mod.validate_measurement(raw, COMMAND, TOOLS)

    def refuse(self, raw):
        with self.assertRaises(self.mod.QualificationError):
            self.accept(raw)

    def test_exact_inclusive_envelope_is_record_consistency_only(self):
        result = self.accept(measurement())
        self.assertEqual(result['status'], 'WITHIN_WINDOWS_ENVELOPE_AT_RECORDED_SCOPE')
        self.assertEqual(result['authority_ceiling'], 'NO_NATIVE_OR_ISSUE_ACCEPTANCE')

    def test_explicit_incomplete_scope_refuses_even_when_numbers_pass(self):
        raw = measurement()
        raw.update(elapsed_ms=562.758, root_exit_observed_ms=561.5788,
                   peak_job_committed_bytes=17137664, peak_single_process_committed_bytes=7073792,
                   complete_memory_scope_valid=False)
        self.refuse(raw)

    def test_zero_population_and_unrelated_command_refuse(self):
        for changes in ({'kernel_total_processes': 0}, {'command': ['C:/cmd.exe', '/c', 'exit', '0']}):
            with self.subTest(changes=changes):
                self.refuse(dict(measurement(), **changes))

    def test_missing_fields_and_wrong_exact_types_refuse(self):
        original = measurement()
        for name in original:
            raw = copy.deepcopy(original)
            del raw[name]
            with self.subTest(missing=name):
                self.refuse(raw)
        for name in ('exit_code', 'kernel_total_processes', 'root_pid', 'creation_event_count',
                     'exit_event_count', 'terminal_active_processes', 'baseline_subtracted_bytes',
                     'peak_job_committed_bytes', 'peak_single_process_committed_bytes',
                     'initial_job_flags', 'terminal_job_flags', 'elapsed_ms', 'root_exit_observed_ms'):
            with self.subTest(boolean_numeric=name):
                self.refuse(dict(original, **{name: True}))

    def test_nonfinite_negative_zero_and_over_bound_measurements_refuse(self):
        for value in (math.nan, math.inf, -1, 0, 60000.001, '100'):
            with self.subTest(elapsed=value):
                self.refuse(dict(measurement(), elapsed_ms=value))
        for value in (-1, 0, 201326593, 1.5, '100'):
            with self.subTest(memory=value):
                self.refuse(dict(measurement(), peak_job_committed_bytes=value))

    def test_nonterminal_changed_flags_and_subtraction_refuse(self):
        for name, value in [('exit_code', 1), ('terminal_active_processes', 1),
                            ('initial_job_flags', 0), ('terminal_job_flags', 0x3800),
                            ('terminal_breakaway_allowed', True), ('baseline_subtracted_bytes', 1),
                            ('started_suspended', False), ('root_job_membership_confirmed', False),
                            ('assigned_before_resume', False), ('harness_included', True),
                            ('sampled_pid_census_complete', True), ('platform', 'linux'),
                            ('root_exit_observed_ms', 60001), ('peak_single_process_committed_bytes', 201326593)]:
            with self.subTest(name=name):
                self.refuse(dict(measurement(), **{name: value}))

    def test_completeness_boolean_cannot_replace_kernel_event_reconciliation(self):
        for mutate in (lambda r: r['process_events'].pop(0),
                       lambda r: r['process_events'].append({'event': 'NEW_PROCESS', 'pid': 99}),
                       lambda r: r.update(kernel_total_processes=4),
                       lambda r: r.update(creation_event_count=4),
                       lambda r: r.update(exit_event_count=4),
                       lambda r: r['process_events'].append({'event': 'UNRECOGNIZED', 'pid': 0})):
            raw = measurement()
            mutate(raw)
            self.refuse(raw)

    def test_required_executables_need_actual_in_job_identity(self):
        for mutate in (lambda r: r['observed_processes'].pop(),
                       lambda r: r['observed_processes'][1].update(in_job=False),
                       lambda r: r['observed_processes'][1].update(image='C:/WindowsApps/python.exe'),
                       lambda r: r['observed_processes'][2].update(image_sha256='f' * 64),
                       lambda r: r['observed_processes'][2].update(pid=999)):
            raw = measurement()
            mutate(raw)
            self.refuse(raw)

    def test_optimized_python_cannot_remove_rejection(self):
        code = ("import importlib.util; s=importlib.util.spec_from_file_location('q', " + repr(str(PATH)) +
                "); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "m.validate_measurement({}, [], {})")
        result = subprocess.run([sys.executable, '-O', '-c', code], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'QualificationError', result.stderr)


class TransitionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()

    def test_fresh_preparation_requires_every_successor_slot_absent(self):
        before, *_ = transition_fixture()
        fresh = {'generation_path_exists': False, 'archive_ref_oid': None,
                 'epoch_ref_oid': None, 'publication_ref_oid': None, 'receipt_ref_oid': None}
        self.mod.validate_fresh_preflight(before, fresh)
        for key in fresh:
            for mutation in ('missing', 'present'):
                changed = dict(fresh)
                if mutation == 'missing':
                    del changed[key]
                else:
                    changed[key] = True if key == 'generation_path_exists' else 'f' * 40
                with self.subTest(key=key, mutation=mutation), self.assertRaises(self.mod.QualificationError):
                    self.mod.validate_fresh_preflight(before, changed)

    def test_exact_fresh_original14_transition_preserves_pending_and_unknown(self):
        before, after, raw, payload, retained = transition_fixture()
        stdout = (after['receipt_token'] + '\n').encode()
        result = self.mod.validate_transition(before, after, raw, payload, payload, retained, retained,
                                             stdout, stdout, stdout)
        self.assertEqual(result['authority_ceiling'], 'NO_NATIVE_OR_ISSUE_ACCEPTANCE')

    def test_same_generation_marker_payload_receipt_and_retention_mutations_refuse(self):
        for mutation in ('old_generation', 'marker', 'pending', 'missing_retained', 'receipt_bytes', 'receipt_oid', 'pointer_oid'):
            before, after, raw, payload, retained = transition_fixture()
            new_payload, new_retained = copy.deepcopy(payload), copy.deepcopy(retained)
            if mutation == 'old_generation': after['pointer']['continuity_epoch'] = 'G0002'
            if mutation == 'marker': after['marker_oid'] = 'f' * 40
            if mutation == 'pending': new_payload['STATE']['pending'] = []
            if mutation == 'missing_retained': del new_retained['files']['archive']
            if mutation == 'receipt_bytes': raw = raw.replace(b'G0003', b'G0004')
            if mutation == 'receipt_oid': after['receipt_token'] = after['receipt_token'].split('@')[0] + '@' + '0' * 40
            if mutation == 'pointer_oid': after['pointer_token'] = after['pointer_token'].split('@')[0] + '@' + '0' * 40
            stdout = (after['receipt_token'] + '\n').encode()
            with self.subTest(mutation=mutation), self.assertRaises(self.mod.QualificationError):
                self.mod.validate_transition(before, after, raw, payload, new_payload, retained, new_retained,
                                             stdout, stdout, stdout)

    def test_duplicate_json_members_and_nonfinite_values_refuse(self):
        for raw in (b'{"a":1,"a":1}', b'{"elapsed_ms":NaN}', b'{"a":1,"\\u0061":2}'):
            with self.assertRaises(self.mod.QualificationError):
                self.mod.strict_json(raw)

    def test_equal_valued_json_type_changes_do_not_preserve_payload(self):
        for original, replacement in ((1, True), (0, False), (1, 1.0)):
            before, after, raw, payload, retained = transition_fixture()
            payload['STATE']['typed_pending'] = {'covered': [original]}
            changed = copy.deepcopy(payload)
            changed['STATE']['typed_pending']['covered'][0] = replacement
            stdout = (after['receipt_token'] + '\n').encode()
            with self.subTest(original=original, replacement=replacement), self.assertRaises(self.mod.QualificationError):
                self.mod.validate_transition(before, after, raw, payload, changed, retained, retained,
                                             stdout, stdout, stdout)

    def test_equal_valued_json_type_changes_do_not_preserve_retained_evidence(self):
        before, after, raw, payload, retained = transition_fixture()
        changed = copy.deepcopy(retained)
        changed['files']['archive']['bytes'] = True
        stdout = (after['receipt_token'] + '\n').encode()
        with self.assertRaises(self.mod.QualificationError):
            self.mod.validate_transition(before, after, raw, payload, payload, retained, changed,
                                         stdout, stdout, stdout)


class WindowsGitLayoutControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()

    def test_direct_git_legacy_and_ucrt_layouts_are_explicit(self):
        self.assertTrue(callable(getattr(self.mod, 'direct_git_layout', None)), 'supported direct Git layout gate is absent')
        self.assertEqual(self.mod.direct_git_layout(r'C:\Program Files\Git\mingw64\bin\git.exe'), 'mingw64')
        self.assertEqual(self.mod.direct_git_layout(r'C:\Program Files\Git\ucrt64\bin\git.exe'), 'ucrt64')

    def test_direct_git_wrappers_foreign_and_aliased_paths_refuse(self):
        self.assertTrue(callable(getattr(self.mod, 'direct_git_layout', None)), 'supported direct Git layout gate is absent')
        for value in (r'C:\Program Files\Git\cmd\git.exe', r'C:\Program Files\Git\bin\git.exe',
                      r'C:\other\ucrt64\bin\git.exe', r'C:\Program Files\Git\ucrt64\bin\..\bin\git.exe',
                      r'C:\Program Files\Git\ucrt64\bin\.\git.exe', 'git.exe', None):
            with self.subTest(value=value), self.assertRaises(self.mod.QualificationError):
                self.mod.direct_git_layout(value)

    def test_selected_layout_drives_exact_owner_search_path(self):
        from unittest import mock
        spec = importlib.util.spec_from_file_location('r0039_driver_layout', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        for variant in ('mingw64', 'ucrt64'):
            selected = rf'C:\Program Files\Git\{variant}\bin\git.exe'
            tools = {'git': {'path': selected}, 'python': {'path': r'C:\Python312\python.exe'}}
            with self.subTest(variant=variant), mock.patch.object(driver, 'Path', pathlib.PureWindowsPath), mock.patch.object(driver.os, 'pathsep', ';'):
                env = driver.environment(tools)
                self.assertEqual(env['PATH'].split(';')[:5], [r'C:\Python312',
                    rf'C:\Program Files\Git\{variant}\bin', r'C:\Program Files\Git\cmd',
                    r'C:\Program Files\Git\bin', r'C:\Program Files\Git\usr\bin'])

    def test_native_git_selection_refuses_raw_dot_alias_before_measurement(self):
        from unittest import mock
        spec = importlib.util.spec_from_file_location('r0039_native_git_selection', ROOT / 'fixtures/canonical-state-rotation/windows_job_test.py')
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        class ExistingWindowsFile(pathlib.PureWindowsPath):
            def is_file(self):
                return True
        def path(value):
            return ExistingWindowsFile(value) if str(value).lower().startswith('c:') else pathlib.Path(value)
        raw = r'C:\Program Files\Git\ucrt64\bin\.\git.exe'
        with mock.patch.dict(fixture.os.environ, {'IMPLEMENTAUDIT_WINDOWS_JOB_GIT': raw}), mock.patch.object(fixture, 'Path', side_effect=path), mock.patch.object(fixture.M, 'measure', side_effect=AssertionError('aliased selection reached measurement')):
            control = fixture.WindowsKernelIntegration('test_actual_git_root_identity_is_observed_before_resume')
            with self.assertRaises(ValueError):
                control.test_actual_git_root_identity_is_observed_before_resume()

    def test_prepare_refuses_raw_dot_alias_before_physical_reads(self):
        from unittest import mock
        spec = importlib.util.spec_from_file_location('r0039_driver_raw_selection', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        argv = ['driver', 'prepare']
        for key in ('source', 'repo', 'controller', 'source-head', 'source-tree', 'bash', 'python', 'out'):
            argv += ['--' + key, 'unused']
        argv += ['--git', r'C:\Program Files\Git\ucrt64\bin\.\git.exe']
        with mock.patch.object(driver.sys, 'argv', argv), mock.patch.object(driver.sys, 'platform', 'win32'), mock.patch.object(driver.os, 'name', 'nt'), mock.patch.object(driver, 'physical', side_effect=AssertionError('aliased selection reached physical reads')):
            with self.assertRaisesRegex(driver.Q.QualificationError, 'aliased direct Git'):
                driver.main()


class DriverControls(unittest.TestCase):
    def test_non_windows_driver_refuses_before_touching_requested_paths(self):
        if sys.platform == 'win32':
            self.skipTest('portable non-Windows refusal control')
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / 'must-not-exist'
            argv = [sys.executable, '-B', str(ROOT / 'scripts/run-r0039-windows-resume.py'), 'prepare']
            for key in ('source', 'repo', 'controller', 'source-head', 'source-tree', 'bash', 'python', 'git'):
                argv += ['--' + key, 'unavailable']
            argv += ['--out', str(out)]
            result = subprocess.run(argv, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'authentic Windows execution unavailable', result.stderr)
            self.assertFalse(out.exists())

    def test_changed_plan_digest_cannot_create_an_attempt(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        with tempfile.TemporaryDirectory() as tmp:
            plan = pathlib.Path(tmp) / 'OPERATION.json'
            plan.write_text('{"schema":"implementaudit.dg30-windows-operation.v1"}\n')
            with self.assertRaises(driver.Q.QualificationError):
                driver.execute(plan, '0' * 64, 'constructed test: no native entitlement')
            self.assertFalse((plan.parent / 'execution').exists())

    def test_existing_attempt_directory_cannot_be_replayed(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            for name in ('source', 'subject', 'evidence'):
                (base / name).mkdir()
            plan = base / 'evidence/OPERATION.json'
            raw = json.dumps({'schema': 'implementaudit.dg30-windows-operation.v1',
                              'request': {'source_root': str(base / 'source'), 'subject_root': str(base / 'subject')}}).encode()
            plan.write_bytes(raw)
            (plan.parent / 'execution').mkdir()
            with self.assertRaises(FileExistsError):
                driver.execute(plan, hashlib.sha256(raw).hexdigest(), 'constructed test: no native entitlement')

    def test_moved_plan_cannot_write_inside_source_or_governed_subject(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        for location in ('source', 'subject'):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as tmp:
                base = pathlib.Path(tmp)
                (base / 'source').mkdir()
                (base / 'subject').mkdir()
                plan = base / location / 'OPERATION.json'
                raw = json.dumps({'schema': 'implementaudit.dg30-windows-operation.v1', 'request': {
                    'source_root': str(base / 'source'), 'subject_root': str(base / 'subject')}}).encode()
                plan.write_bytes(raw)
                with self.assertRaises(Exception):
                    driver.execute(plan, hashlib.sha256(raw).hexdigest(), 'constructed test: no native entitlement')
                self.assertFalse((plan.parent / 'execution').exists())

    def test_parent_aliased_plan_cannot_write_inside_either_protected_root(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        for location in ('source', 'subject'):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as tmp:
                base = pathlib.Path(tmp)
                for name in ('source', 'subject', 'outside'):
                    (base / name).mkdir()
                plan = base / location / 'OPERATION.json'
                raw = json.dumps({'schema': 'implementaudit.dg30-windows-operation.v1', 'request': {
                    'source_root': str(base / 'source'), 'subject_root': str(base / 'subject')}}).encode()
                plan.write_bytes(raw)
                alias = base / 'outside' / '..' / location / 'OPERATION.json'
                with self.assertRaises(Exception):
                    driver.execute(alias, hashlib.sha256(raw).hexdigest(), 'constructed: no native entitlement')
                self.assertFalse((plan.parent / 'execution').exists())
                self.assertEqual(list(plan.parent.iterdir()), [plan])

    def test_physical_path_check_rejects_parent_alias_and_symlink(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            (base / 'outside').mkdir()
            (base / 'subject').mkdir()
            self.assertEqual(driver.physical(base / 'subject'), (base / 'subject').resolve())
            with self.assertRaises(driver.Q.QualificationError):
                driver.physical(base / 'outside' / '..' / 'subject')
            if sys.platform != 'win32':
                (base / 'alias').symlink_to(base / 'subject', target_is_directory=True)
                with self.assertRaises(driver.Q.QualificationError):
                    driver.physical(base / 'alias')

    def test_prepare_and_execute_share_the_physical_output_boundary(self):
        spec = importlib.util.spec_from_file_location('r0039_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            source, subject, outside = [base / name for name in ('source', 'subject', 'outside')]
            for path in (source, subject, outside):
                path.mkdir()
            self.assertEqual(driver.separated_output(outside / 'new', source, subject), outside.resolve() / 'new')
            for protected in (source, subject):
                for out in (protected / 'new', outside / '..' / protected.name / 'new'):
                    with self.subTest(out=out), self.assertRaises(driver.Q.QualificationError):
                        driver.separated_output(out, source, subject)
                self.assertEqual(list(protected.iterdir()), [])
            self.assertEqual(list(outside.iterdir()), [])


class UnqualifiedOperationReadbackControls(unittest.TestCase):
    """Exercise the real one-shot driver with an inert measurement boundary.

    The fixture operation changes one disposable Git ref. The readback shell
    accepts only the three existing read-only queries and records each query.
    No Windows launch, governor authority or native episode is constructed.
    """
    def setUp(self):
        if sys.platform == 'win32':
            self.skipTest('portable inert subprocess controls')
        spec = importlib.util.spec_from_file_location(
            'r0039_failed_driver', ROOT / 'scripts/run-r0039-windows-resume.py')
        self.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.driver)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = pathlib.Path(self.tmp.name)
        self.source, self.subject, self.evidence = [self.base / n for n in ('source', 'subject', 'evidence')]
        for path in (self.source, self.subject, self.evidence):
            path.mkdir()
        subprocess.run(['/usr/bin/git', 'init', '-q', str(self.subject)], check=True)
        self.controller = 'dg30-disposable-readback'
        self.pointer_ref = 'refs/implementaudit/current-generations/' + self.controller
        self.old_oid = subprocess.check_output(
            ['/usr/bin/git', '-C', str(self.subject), 'hash-object', '-w', '--stdin'], input=b'old fixture pointer').decode().strip()
        self.new_oid = subprocess.check_output(
            ['/usr/bin/git', '-C', str(self.subject), 'hash-object', '-w', '--stdin'], input=b'new fixture pointer').decode().strip()
        subprocess.run(['/usr/bin/git', '-C', str(self.subject), 'update-ref', self.pointer_ref, self.old_oid], check=True)
        self.claim_path = self.subject / 'skills/implementaudit/scripts/claim-run.sh'
        self.claim_path.parent.mkdir(parents=True)
        self.claim_path.write_text('#!/usr/bin/bash\ncase "$1" in\n  --resolve-canonical-generation|--resolve-resume-generation|--require-current-continuity)\n    printf \'%s\\n\' "$1" >> query.log\n    printf \'fixture refuses currentness after incomplete owner effect\\n\' >&2\n    exit 19 ;;\n  *) printf \'unexpected non-read-only query\\n\' >&2; exit 93 ;;\nesac\n')
        self.claim_path.chmod(0o755)
        self.tools = {name: {'path': path, 'sha256': self.driver.ident(path)['sha256']}
                      for name, path in [('bash', '/usr/bin/bash'), ('python', str(pathlib.Path(sys.executable).resolve())), ('git', '/usr/bin/git')]}
        self.request = {'source_root': str(self.source), 'subject_root': str(self.subject),
                        'controller': self.controller, 'tools': self.tools}
        runtime = {'skills/implementaudit/scripts/claim-run.sh': self.driver.ident(self.claim_path)}
        recorders = {name: self.driver.ident(ROOT / 'scripts' / name) for name in
                     ('run-r0039-windows-resume.py', 'check-r0039-windows-resume.py', 'r0039-windows-job.py')}
        run = self.subject / '.IMPLEMENTAUDIT/runs/disposable'
        generation = run / 'generation'
        generation.mkdir(parents=True)
        before = {'controller': self.controller, 'run_root_identity': '.IMPLEMENTAUDIT/runs/disposable'}
        for key, name in (('state_path', 'STATE.md'), ('roadmap_path', 'ROADMAP.md'),
                          ('protected_manifest_path', 'protected.json'), ('archive_manifest_path', 'archive.json')):
            path = generation / name
            path.write_bytes(b'unchanged retained fixture')
            before[key] = str(path)
        for name in ('STATE.md', 'ROADMAP.md'):
            (run / name).write_bytes(b'unchanged retired fixture')
        self.current = {'snapshot': {'runtime': runtime, 'tools': self.tools, 'recorders': recorders},
                        'before': before, 'command': ['inert-disposable-owner-operation'],
                        'retained': {'files': {}, 'refs': {self.pointer_ref: self.old_oid}}}
        self.plan = self.evidence / 'OPERATION.json'
        raw = self.driver.canonical({'schema': 'implementaudit.dg30-windows-operation.v1',
                                    'request': self.request, 'prepared': self.current})
        self.plan.write_bytes(raw)
        self.plan_sha = hashlib.sha256(raw).hexdigest()
        self.operation_calls = 0

    def invoke(self, *, exit_code=23, stdout=b'', raise_measurement=False, after_effect=None, fail_one_query=False):
        def measure(argv, cwd, environment, out):
            self.operation_calls += 1
            out.mkdir()
            (out / 'stdout.bin').write_bytes(stdout)
            (out / 'stderr.bin').write_bytes(b'original inert measurement failure\n')
            subprocess.run(['/usr/bin/git', '-C', str(self.subject), 'update-ref',
                            self.pointer_ref, self.new_oid, self.old_oid], check=True)
            if after_effect:
                after_effect()
            if raise_measurement:
                raise RuntimeError('original measurement unavailable after fixture effect')
            return {'exit_code': exit_code}
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(self.driver, 'preflight', return_value=self.current))
            stack.enter_context(mock.patch.object(self.driver, 'native_control', return_value={'constructed': True}))
            stack.enter_context(mock.patch.object(self.driver, 'environment', return_value={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}))
            stack.enter_context(mock.patch.object(self.driver, 'load', return_value=type('InertMeter', (), {'measure': staticmethod(measure)})()))
            if fail_one_query:
                original_command = self.driver.command
                def command(*args, **kwargs):
                    if args[4] == 'resolve-canonical':
                        raise RuntimeError('secondary read-only query unavailable')
                    return original_command(*args, **kwargs)
                stack.enter_context(mock.patch.object(self.driver, 'command', side_effect=command))
            with self.assertRaisesRegex(Exception, 'owner failed|original measurement unavailable'):
                self.driver.execute(self.plan, self.plan_sha, 'inert fixture only; no native grant')
        self.assertEqual(self.operation_calls, 1)
        self.assertEqual(subprocess.check_output(['/usr/bin/git', '-C', str(self.subject),
                          'rev-parse', self.pointer_ref]).decode().strip(), self.new_oid)
        self.assertFalse((self.evidence / 'execution/RESULT.json').exists())
        return self.evidence / 'execution'

    def test_nonzero_owner_retains_actual_after_effect_refs_without_retry(self):
        out = self.invoke()
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertEqual(observation['refs_before_queries'][self.pointer_ref], self.new_oid)
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)
        self.assertEqual(observation['status'], 'UNQUALIFIED_POST_ATTEMPT_OBSERVATION')
        self.assertEqual((self.subject / 'query.log').read_text().splitlines(),
                         ['--resolve-canonical-generation', '--resolve-resume-generation', '--require-current-continuity'])
        failure = json.loads((out / 'FAILURE.json').read_text())
        self.assertEqual(failure['status'], 'OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED')
        self.assertFalse(failure['automatic_retry'])
        with self.assertRaises(FileExistsError):
            self.driver.execute(self.plan, self.plan_sha, 'inert fixture only; no native grant')
        self.assertEqual(self.operation_calls, 1)


    def test_zero_exit_without_receipt_still_observes_actual_effect(self):
        out = self.invoke(exit_code=0, stdout=b'no authenticated receipt\n')
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)
        self.assertEqual(observation['queries']['require-current']['exit_code'], 19)
        self.assertEqual(len(observation['retained_files']), 6)
        self.assertFalse(observation['errors'])
        self.assertEqual(observation['authority_ceiling'], 'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE')

    def test_measurement_exception_preserves_original_failure_and_after_effect_refs(self):
        out = self.invoke(raise_measurement=True)
        failure = json.loads((out / 'FAILURE.json').read_text())
        self.assertEqual(failure['detail'], 'original measurement unavailable after fixture effect')
        self.assertEqual((out / 'operation/stderr.bin').read_bytes(), b'original inert measurement failure\n')
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)

    def test_failed_primary_marker_write_preserves_error_and_continues_readback(self):
        original_save = self.driver.save
        def save(path, value):
            if path.name == 'FAILURE.json':
                raise OSError('injected primary diagnostic write failure')
            return original_save(path, value)
        with mock.patch.object(self.driver, 'save', side_effect=save):
            out = self.invoke(raise_measurement=True)
        self.assertFalse((out / 'FAILURE.json').exists())
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)
        self.assertEqual((self.subject / 'query.log').read_text().splitlines(),
                         ['--resolve-canonical-generation', '--resolve-resume-generation', '--require-current-continuity'])
        with self.assertRaises(FileExistsError):
            self.driver.execute(self.plan, self.plan_sha, 'inert fixture only; no native grant')
        self.assertEqual(self.operation_calls, 1)

    def test_failed_prelaunch_marker_write_preserves_error_without_queries(self):
        original_save = self.driver.save
        def save(path, value):
            if path.name == 'FAILURE.json':
                raise OSError('injected prelaunch diagnostic write failure')
            return original_save(path, value)
        with mock.patch.object(self.driver, 'save', side_effect=save), \
                mock.patch.object(self.driver, 'preflight', side_effect=RuntimeError('preflight refused')):
            with self.assertRaisesRegex(RuntimeError, '^preflight refused$'):
                self.driver.execute(self.plan, self.plan_sha, 'inert fixture only; no native grant')
        self.assertFalse((self.evidence / 'execution/unqualified-readback').exists())
        self.assertFalse((self.subject / 'query.log').exists())
        self.assertEqual(self.operation_calls, 0)

    def test_secondary_readback_error_cannot_replace_operation_failure(self):
        out = self.invoke(fail_one_query=True)
        failure = json.loads((out / 'FAILURE.json').read_text())
        self.assertIn('owner failed or returned no receipt', failure['detail'])
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertIn('secondary read-only query unavailable', observation['errors']['resolve-canonical']['detail'])
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)
        self.assertEqual(observation['queries']['resolve-resume']['exit_code'], 19)
        self.assertEqual(observation['queries']['require-current']['exit_code'], 19)

    def test_changed_runtime_blocks_owner_queries_but_retains_actual_refs(self):
        out = self.invoke(after_effect=lambda: self.claim_path.write_text('#!/usr/bin/bash\nexit 0\n'))
        observation = json.loads((out / 'unqualified-readback/OBSERVATION.json').read_text())
        self.assertFalse((self.subject / 'query.log').exists())
        self.assertEqual(observation['refs_after_queries'][self.pointer_ref], self.new_oid)
        for label in ('resolve-canonical', 'resolve-resume', 'require-current'):
            self.assertIn('runtime identity changed', observation['errors'][label]['detail'])
            self.assertIsNone(observation['queries'][label])

    def test_prelaunch_failure_does_not_start_after_effect_queries(self):
        with mock.patch.object(self.driver, 'preflight', side_effect=RuntimeError('preflight refused')):
            with self.assertRaisesRegex(RuntimeError, 'preflight refused'):
                self.driver.execute(self.plan, self.plan_sha, 'inert fixture only; no native grant')
        out = self.evidence / 'execution'
        failure = json.loads((out / 'FAILURE.json').read_text())
        self.assertEqual(failure['status'], 'NO_OWNER_LAUNCH')
        self.assertFalse((out / 'unqualified-readback').exists())
        self.assertFalse((self.subject / 'query.log').exists())
        self.assertEqual(self.operation_calls, 0)



if __name__ == '__main__':
    unittest.main(verbosity=2)
