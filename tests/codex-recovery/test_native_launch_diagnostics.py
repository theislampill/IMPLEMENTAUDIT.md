"""Focused cold controls. No native executable or external process is launched.

Production breaks caught: missing launch typing; setup escaping exact-probe
cleanup; cleanup/finalization exceptions masking refusal; unsafe error strings;
accidental changes to protocol/cleanup/deadline/interruption/retry semantics.
The only doubles replace the external process and deterministic thread boundary.
The reader, protocol parser, acquisition bracket and config helper remain real.
"""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import time
import types
import unittest
from unittest.mock import patch

CANARY = 'SYNTHETIC_PRIVATE_COMMAND_ENV_CONFIG_STDERR_TRACEBACK'
READER = None
WORK = None


class InputStream:
    def __init__(self, fixture):
        self.fixture = fixture
        self.writes = []

    def write(self, raw):
        self.writes.append(raw)

    def flush(self):
        pass

    def close(self):
        self.fixture.events.append('stdin.close')
        if self.fixture.close_error:
            raise self.fixture.close_error


class ProcessFixture:
    def __init__(self, rows, **options):
        self.pid = 81234  # Synthetic identity only; never a host PID claim.
        self.returncode = None
        self.events = []
        self.wait_calls = []
        self.close_error = options.get('close_error')
        self.wait_error = options.get('wait_error')
        self.poll_error = options.get('poll_error')
        self.wait_timeout = options.get('wait_timeout', False)
        self.unresolved = options.get('unresolved', False)
        self.exit_status = options.get('exit_status', 0)
        self.stdin = InputStream(self)
        self.stdout = io.BytesIO(b''.join(json.dumps(row).encode() + b'\n' for row in rows))
        self.stderr = io.BytesIO(b'')

    def wait(self, timeout):
        self.events.append('wait')
        self.wait_calls.append(timeout)
        if self.wait_error:
            error, self.wait_error = self.wait_error, None
            raise error
        if self.unresolved or self.wait_timeout and len(self.wait_calls) == 1:
            raise subprocess.TimeoutExpired('synthetic command ' + CANARY, timeout)
        self.returncode = self.exit_status
        return self.returncode

    def poll(self):
        self.events.append('poll')
        if self.poll_error:
            raise self.poll_error
        return self.returncode


class ThreadFixture:
    def __init__(self, target, args, daemon, *, start_error=None, join_error=None, status_error=None):
        self.target, self.args = target, args
        self.start_error, self.join_error = start_error, join_error
        self.status_error = status_error
        self.started = False

    def start(self):
        if self.start_error:
            raise self.start_error
        self.started = True
        self.target(*self.args)

    def join(self, timeout):
        if not self.started:
            raise RuntimeError('cannot join a thread before it is started')
        if self.join_error:
            raise self.join_error
        assert 0 <= timeout <= 2

    def is_alive(self):
        if self.status_error:
            raise self.status_error
        return False


class Harness:
    def __init__(self, process=None, *, launch_error=None, create_error_at=None,
                 start_error_at=None, join_error_at=None, status_error_at=None,
                 kill_error=None):
        self.process = process
        self.launch_error = launch_error
        self.create_error_at, self.start_error_at = create_error_at, start_error_at
        self.join_error_at, self.status_error_at = join_error_at, status_error_at
        self.kill_error = kill_error
        self.launches, self.threads, self.kills = [], [], []

    def popen(self, args, **kwargs):
        self.launches.append((args, kwargs))
        if self.launch_error:
            raise self.launch_error
        assert kwargs['cwd'] == str(WORK)
        assert kwargs['env'] == {'TEST_ENV': CANARY}
        assert kwargs['creationflags'] == subprocess.CREATE_NO_WINDOW
        return self.process

    def thread(self, **kwargs):
        index = len(self.threads) + 1
        if index == self.create_error_at:
            raise RuntimeError(CANARY)
        thread = ThreadFixture(**kwargs,
            start_error=RuntimeError(CANARY) if index == self.start_error_at else None,
            join_error=RuntimeError(CANARY) if index == self.join_error_at else None,
            status_error=RuntimeError(CANARY) if index == self.status_error_at else None)
        self.threads.append(thread)
        return thread

    def run(self, args, **kwargs):
        # The only permitted subprocess.run shape is the exact synthetic probe.
        assert args == ['taskkill.exe', '/PID', '81234', '/T', '/F']
        assert kwargs['timeout'] == 5 and kwargs['capture_output'] is True
        self.kills.append(args)
        if self.kill_error:
            raise self.kill_error
        return types.SimpleNamespace(returncode=0, stdout=b'', stderr=b'')

    def __enter__(self):
        self.patches = [patch.object(READER.subprocess, 'Popen', self.popen),
                        patch.object(READER.subprocess, 'run', self.run),
                        patch.object(READER.threading, 'Thread', self.thread)]
        if not hasattr(READER.subprocess, 'CREATE_NO_WINDOW'):
            self.patches.append(patch.object(READER.subprocess, 'CREATE_NO_WINDOW',
                                             0x08000000, create=True))
        for value in self.patches:
            value.start()
        return self

    def __exit__(self, *args):
        for value in reversed(self.patches):
            value.stop()


def ordinary_rows(result=None):
    return [{'id': 1, 'result': {}}, {'id': 2, 'result': result or {'accepted': True}},
            {'id': 3, 'result': result or {'accepted': True}}]


class LaunchDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.directory = WORK / self.id().rsplit('.', 1)[-1]
        self.directory.mkdir()
        self.observer = object.__new__(READER.NativeRecoveryObserver)
        self.observer.binary = WORK / 'unchanged-synthetic-locator.exe'
        self.observer.repo = str(WORK)
        self.observer.controller_cwd = str(WORK / 'controller')
        self.observer.env = {'TEST_ENV': CANARY}

    def capture_failure(self, harness, expected='UNKNOWN_FAILURE'):
        caught = None
        with harness:
            try:
                self.observer.capture_epoch_boundary(diagnostic_directory=self.directory)
            except BaseException as error:
                caught = error
        self.assertIsInstance(caught, READER.AcquisitionFailure)
        self.assertEqual(caught.code, expected)
        self.assertEqual(str(caught), 'epoch acquisition ' + expected)
        diagnostic = json.loads((self.directory / 'acquisition-diagnostic.json').read_text())
        self.assertEqual(diagnostic['category'], expected)
        self.assertFalse(diagnostic['snapshot_returned'])
        self.assertFalse(diagnostic['currentness'])
        self.assertNotIn(CANARY, json.dumps(diagnostic))
        return diagnostic

    def protocol(self, diagnostic):
        self.assertEqual(len(diagnostic['protocols']), 1, 'failure must retain one safe probe record')
        return diagnostic['protocols'][0]

    def event(self, protocol, operation, category=None):
        self.assertTrue(protocol['failure_present'], 'unexpected operation cannot report failure absent')
        matches = [row for row in protocol.get('diagnostics', []) if row.get('operation') == operation]
        self.assertTrue(matches, 'missing typed operation ' + operation)
        result = matches[0]
        self.assertEqual(set(result), {'operation', 'predicate', 'category', 'errno', 'winerror'})
        if category:
            self.assertEqual(result['category'], category)
        return result

    def test_vanished_locator_is_typed_without_spawn_or_cleanup_proof(self):
        error = FileNotFoundError(2, CANARY, 'synthetic-absent-path')
        error.winerror = 2
        harness = Harness(launch_error=error)
        diagnostic = self.capture_failure(harness)
        protocol = self.protocol(diagnostic)
        event = self.event(protocol, 'LAUNCH', 'FILE_NOT_FOUND')
        self.assertEqual(event, {'operation': 'LAUNCH', 'predicate': 'PROBE_CREATE_FAILED',
            'category': 'FILE_NOT_FOUND', 'errno': 2, 'winerror': 2})
        self.assertIsNone(protocol['probe_pid'])
        self.assertFalse(protocol['process_terminated'])
        self.assertFalse(protocol['streams_complete'])
        self.assertIsNone(protocol['exit_code'])
        self.assertEqual(len(harness.launches), 1)
        self.assertFalse(harness.kills)

    def test_permission_error_retains_only_numeric_os_fields(self):
        error = PermissionError(13, CANARY)
        error.winerror = 5
        protocol = self.protocol(self.capture_failure(Harness(launch_error=error)))
        event = self.event(protocol, 'LAUNCH', 'PERMISSION_DENIED')
        self.assertEqual((event['errno'], event['winerror']), (13, 5))

    def test_unknown_exception_name_and_noninteger_os_fields_are_not_serialized(self):
        error_type = type(CANARY, (Exception,), {})
        error = error_type(CANARY)
        error.errno, error.winerror = True, CANARY
        protocol = self.protocol(self.capture_failure(Harness(launch_error=error)))
        event = self.event(protocol, 'LAUNCH', 'OTHER_EXCEPTION')
        self.assertIsNone(event['errno'])
        self.assertIsNone(event['winerror'])

    def test_stream_preparation_failure_cannot_strand_a_created_probe(self):
        process = ProcessFixture(ordinary_rows())
        harness = Harness(process)
        with patch.object(READER.queue, 'Queue', side_effect=RuntimeError(CANARY)):
            diagnostic = self.capture_failure(harness)
        protocol = self.protocol(diagnostic)
        self.event(protocol, 'PREPARE', 'RUNTIME_ERROR')
        if harness.launches:
            self.assertIn('wait', process.events)
            self.assertEqual(protocol['probe_pid'], 81234)
        else:
            self.assertIsNone(protocol['probe_pid'])

    def test_first_thread_constructor_failure_cleans_the_created_probe(self):
        process = ProcessFixture(ordinary_rows())
        protocol = self.protocol(self.capture_failure(Harness(process, create_error_at=1)))
        self.event(protocol, 'THREAD_CREATE', 'RUNTIME_ERROR')
        self.assertEqual(protocol['probe_pid'], 81234)
        self.assertTrue(protocol['process_terminated'])
        self.assertFalse(protocol['streams_complete'])
        self.assertEqual(process.wait_calls, [3])

    def test_second_thread_start_failure_preserves_partial_stream_truth(self):
        process = ProcessFixture(ordinary_rows())
        protocol = self.protocol(self.capture_failure(Harness(process, start_error_at=2)))
        self.event(protocol, 'THREAD_START', 'RUNTIME_ERROR')
        self.assertTrue(protocol['process_terminated'])
        self.assertTrue(protocol['streams']['stdout']['done'])
        self.assertFalse(protocol['streams']['stderr']['done'])
        self.assertFalse(protocol['streams_complete'])
        self.assertEqual(process.wait_calls, [3])

    def test_unexpected_stdin_close_error_still_waits_and_refuses(self):
        process = ProcessFixture(ordinary_rows(), close_error=RuntimeError(CANARY))
        protocol = self.protocol(self.capture_failure(Harness(process)))
        self.event(protocol, 'STDIN_CLOSE', 'RUNTIME_ERROR')
        self.assertTrue(protocol['process_terminated'])
        self.assertEqual(process.wait_calls, [3])

    def test_unexpected_wait_error_attempts_exact_bounded_cleanup_and_refuses(self):
        process = ProcessFixture(ordinary_rows(), wait_error=OSError(5, CANARY))
        harness = Harness(process)
        protocol = self.protocol(self.capture_failure(harness))
        self.event(protocol, 'WAIT', 'OS_ERROR')
        self.assertEqual(process.wait_calls, [3, 2])
        self.assertEqual(len(harness.kills), 1)
        self.assertTrue(protocol['process_terminated'])

    def test_cleanup_command_error_is_observable_and_not_success(self):
        process = ProcessFixture(ordinary_rows(), wait_timeout=True)
        harness = Harness(process, kill_error=OSError(5, CANARY))
        diagnostic = self.capture_failure(harness, 'NATIVE_PROTOCOL_FAILURE')
        self.event(self.protocol(diagnostic), 'TERMINATE', 'OS_ERROR')
        self.assertEqual(process.wait_calls, [3, 2])

    def test_cleanup_unproved_stays_refusing(self):
        process = ProcessFixture(ordinary_rows(), unresolved=True)
        protocol = self.protocol(self.capture_failure(Harness(process), 'NATIVE_CLEANUP_UNPROVED'))
        self.assertFalse(protocol['process_terminated'])
        self.assertEqual(process.wait_calls, [3, 2])

    def test_thread_join_exception_does_not_mask_setup_failure(self):
        process = ProcessFixture(ordinary_rows())
        harness = Harness(process, start_error_at=2, join_error_at=1)
        protocol = self.protocol(self.capture_failure(harness))
        self.event(protocol, 'THREAD_START', 'RUNTIME_ERROR')
        self.event(protocol, 'DRAIN_JOIN', 'RUNTIME_ERROR')
        self.assertFalse(protocol['streams_complete'])
        self.assertTrue(protocol['process_terminated'])

    def test_thread_status_exception_is_sanitized_and_refusing(self):
        process = ProcessFixture(ordinary_rows())
        protocol = self.protocol(self.capture_failure(Harness(process, status_error_at=1)))
        self.event(protocol, 'DRAIN_STATUS', 'RUNTIME_ERROR')
        self.assertFalse(protocol['streams_complete'])

    def test_final_process_poll_exception_does_not_fabricate_termination(self):
        process = ProcessFixture(ordinary_rows(), poll_error=RuntimeError(CANARY))
        protocol = self.protocol(self.capture_failure(Harness(process)))
        self.event(protocol, 'FINALIZE', 'RUNTIME_ERROR')
        self.assertIsNone(protocol['exit_code'])
        self.assertFalse(protocol['process_terminated'])

    def test_final_digest_exception_remains_visible_after_proved_cleanup(self):
        actual_sha256 = READER.hashlib.sha256
        class FinalDigestFailure:
            def update(self, raw):
                pass
            def hexdigest(self):
                raise RuntimeError(CANARY)
        def sha256(*args, **kwargs):
            return actual_sha256(*args, **kwargs) if args else FinalDigestFailure()
        process = ProcessFixture(ordinary_rows())
        with patch.object(READER.hashlib, 'sha256', sha256):
            protocol = self.protocol(self.capture_failure(Harness(process)))
        self.event(protocol, 'FINALIZE', 'RUNTIME_ERROR')
        self.assertTrue(protocol['process_terminated'])
        self.assertTrue(protocol['streams_complete'])

    def test_protocol_error_retains_existing_classification(self):
        process = ProcessFixture([{'id': 1, 'error': {'message': CANARY}}])
        self.capture_failure(Harness(process), 'NATIVE_PROTOCOL_FAILURE')

    def test_response_error_retains_existing_classification(self):
        process = ProcessFixture([{'id': 1, 'result': {}},
            {'id': 2, 'error': {'message': CANARY}}, {'id': 3, 'result': {}}])
        self.capture_failure(Harness(process), 'NATIVE_RESPONSE_ERROR')

    def test_deadline_before_launch_has_no_spawn_or_protocol(self):
        harness = Harness(launch_error=AssertionError('must not launch'))
        with harness:
            with self.assertRaises(READER.AcquisitionFailure) as caught:
                self.observer.capture_epoch_boundary(diagnostic_directory=self.directory,
                    deadline=time.monotonic() - 1)
        self.assertEqual(caught.exception.code, 'DEADLINE_EXHAUSTED')
        diagnostic = json.loads((self.directory / 'acquisition-diagnostic.json').read_text())
        self.assertEqual(diagnostic['protocols'], [])
        self.assertFalse(harness.launches)

    def test_launch_keyboard_interrupt_keeps_interrupted_classification(self):
        protocol = self.protocol(self.capture_failure(Harness(launch_error=KeyboardInterrupt(CANARY)), 'INTERRUPTED'))
        self.event(protocol, 'LAUNCH', 'INTERRUPTED')
        self.assertIsNone(protocol['probe_pid'])

    def test_existing_acquisition_failure_object_and_code_survive(self):
        failure = READER.AcquisitionFailure('DEADLINE_EXHAUSTED')
        with Harness(launch_error=failure):
            caught = None
            try:
                READER.native_read('synthetic', str(WORK), [], {'TEST_ENV': CANARY})
            except BaseException as error:
                caught = error
        self.assertIs(caught, failure)
        self.assertEqual(caught.code, 'DEADLINE_EXHAUSTED')

    def test_only_existing_configuration_instability_codes_are_retryable(self):
        for code in ('NATIVE_PAIR_CHANGED', 'PHYSICAL_PAIR_CHANGED', 'SNAPSHOT_BRACKET_CHANGED'):
            failure = READER.ConfigurationInstability(code)
            self.assertIsInstance(failure, READER.AcquisitionFailure)
            self.assertEqual(failure.code, code)
        for code in ('UNKNOWN_FAILURE', 'NATIVE_PROTOCOL_FAILURE', 'NATIVE_CLEANUP_UNPROVED',
                     'INTERRUPTED', 'DEADLINE_EXHAUSTED', 'PROBE_CREATE_FAILED'):
            with self.assertRaises(READER.AcquisitionFailure) as caught:
                READER.ConfigurationInstability(code)
            self.assertNotIsInstance(caught.exception, READER.ConfigurationInstability)
            self.assertEqual(caught.exception.code, 'UNKNOWN_FAILURE')

    def test_unchanged_locator_real_acquisition_bracket_completes(self):
        self._successful_bracket()

    def test_tolerated_broken_pipe_close_still_requires_and_preserves_complete_cleanup(self):
        self._successful_bracket(close_error=BrokenPipeError(32, CANARY))

    def _successful_bracket(self, close_error=None):
        config_file = self.directory / 'fixture.toml'
        config_file.write_text('[features]\nretain_client_developer_messages = true\n')
        config = {'features': {'retain_client_developer_messages': True}}
        result = {'config': config, 'layers': [{'name': {'type': 'project', 'file': str(config_file)},
                  'version': 'fixture-v1', 'config': config}], 'origins': {}}
        processes = []
        launches = []
        def popen(args, **kwargs):
            assert kwargs['creationflags'] == subprocess.CREATE_NO_WINDOW
            launches.append(args)
            process = ProcessFixture([{'id': 1, 'result': {}},
                {'id': 2, 'result': copy.deepcopy(result)}, {'id': 3, 'result': copy.deepcopy(result)}],
                close_error=close_error)
            processes.append(process)
            return process
        def snapshot(previous=None, *, before_restart=False):
            methods = [('config/read', {'cwd': str(cwd), 'includeLayers': True}, 'ConfigRead')
                for cwd in (self.observer.repo, self.observer.controller_cwd)]
            rows, protocol = self.observer._read_native(methods)
            return {'configs': [{'cwd': row['params']['cwd'], **READER.filter_config(row['result'])}
                    for row in rows], 'protocol': protocol}
        self.observer.snapshot = snapshot
        harness = Harness()
        with harness, patch.object(READER.subprocess, 'Popen', popen):
            observation, acquisition = self.observer.capture_epoch_boundary(diagnostic_directory=self.directory)
        diagnostic = json.loads((self.directory / 'acquisition-diagnostic.json').read_text())
        self.assertEqual(diagnostic['category'], 'COMPLETE')
        self.assertEqual(len(diagnostic['protocols']), 3)
        self.assertEqual(len(processes), 3)
        self.assertTrue(all(p.returncode == 0 for p in processes))
        self.assertTrue(all(args[0] == str(self.observer.binary) for args in launches))
        self.assertTrue(all(row['feature'] is True for row in observation['configs']))
        self.assertEqual(acquisition['binding']['schema'], 'implementaudit.config-acquisition-binding.v1')
        self.assertEqual(len(acquisition['native_reads']), 2)
        self.assertTrue(all(row['process_terminated'] and row['streams_complete'] and not row['failure_present']
                            for row in diagnostic['protocols']))
        self.assertFalse(diagnostic['currentness'])
        self.assertNotIn(CANARY, json.dumps(diagnostic))


def main():
    global READER, WORK
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=pathlib.Path, required=True)
    parser.add_argument('--work-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    WORK = args.work_dir.resolve()
    WORK.mkdir(parents=True, exist_ok=False)
    source = args.source.resolve()
    spec = importlib.util.spec_from_file_location('cold_native_reader', source)
    READER = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(READER)
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LaunchDiagnosticsTests)
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    log = output.getvalue()
    (WORK / 'TEST.log').write_text(log, encoding='utf8')
    record = {'source': str(source), 'source_bytes': source.stat().st_size,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'test_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'successful': result.wasSuccessful(), 'native_executed': False,
        'fixture_process_identity': 'SYNTHETIC_ONLY', 'runtime_qualification': False}
    (WORK / 'TEST.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    print(log)
    print(json.dumps(record))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
