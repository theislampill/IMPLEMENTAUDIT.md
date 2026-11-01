#!/usr/bin/env python3
"""Constructed evidence-gate controls; no Windows or native acceptance claim."""
import copy
import hashlib
import importlib.util
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
