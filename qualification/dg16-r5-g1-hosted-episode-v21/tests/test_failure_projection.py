"""Constructed cross-module failure controls; no hosted occurrence."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import tempfile

PACKET = Path(__file__).resolve().parents[1] / 'packet'


def load(name):
    path = PACKET / (name + '.py')
    spec = importlib.util.spec_from_file_location('projection_test_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FailureProjection(unittest.TestCase):
    def setUp(self):
        self.core, self.operation = load('run'), load('operation')

    def test_current_diagnostic_reaches_complete_closed_failure_export(self):
        row = self.operation.namespace_neutral('NOT_APPLICABLE', 'OUT_OF_SCOPE')
        state = dict(context=dict(run_id='45681463624', workflow_commit='1' * 40),
                     failed=True, operation_result=dict(namespace_diagnostic=row),
                     failures=[dict(step='g1', code='UNCLASSIFIED_EXCEPTION',
                                    exception_type='ValueError', message_bytes=1,
                                    message_sha256='2' * 64)])
        files = self.core.public_files(state)
        self.assertEqual(set(files), set(self.core.PUBLIC_NAMES))
        self.assertTrue(json.loads(files['FAILURE.json'])['present'])
        self.assertEqual(json.loads(files['OPERATION.json'])['namespace_diagnostic']['observation'], row)
        self.assertEqual(json.loads(files['RESULT.json'])['status'], 'UNQUALIFIED')

    def test_current_diagnostic_rejects_wrong_source_pin(self):
        row = self.operation.namespace_neutral('NOT_APPLICABLE', 'OUT_OF_SCOPE')
        row['prefix_sha256'] = '0' * 64
        with self.assertRaisesRegex(self.core.Refusal, '^NAMESPACE_DIAGNOSTIC_SOURCE$'):
            self.core.public_namespace_diagnostic(row)

    def test_historical_v1_pin_and_scope_stay_accepted(self):
        row = self.operation.namespace_neutral('NOT_APPLICABLE', 'OUT_OF_SCOPE')
        row.pop('single_lock')
        row['schema'] = 'dg16.git-namespace-diagnostic.v1'
        row['prefix_sha256'] = 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab'
        self.assertEqual(self.core.public_namespace_diagnostic(row)['observation'], row)


class DiagnosticBoundary(unittest.TestCase):
    def test_diagnostic_runs_acquisition_and_selection_but_never_pair(self):
        """Constructed engine/currentness/uid readbacks; no native or root effect."""
        operation = load('operation')
        events = []
        class Session:
            def __init__(self, *args, **kwargs): events.append('construct')
            def _acquire(self):
                events.append('acquire')
                return dict(key='a' * 64, observation=dict(runtime_totals={}, provider={}))
            def run(self):
                self.assertion = 'ACTUAL_PAIR_MUST_NOT_BE_CALLED'
                raise AssertionError(self.assertion)
            def close(self): events.append('close')
        def capture(name, objects, **kwargs):
            raw = b'passwd: files\ngroup: files\n' if name.endswith('nsswitch.conf') else b'root:x:0:0::/:/bin/sh\n'
            key = operation.sha(raw); objects[key] = raw
            return dict(kind='FILE', sha256=key)
        engine = SimpleNamespace(B=SimpleNamespace(capture_selector=capture, _NSCD=[]),
            D=SimpleNamespace(_validate_nss=lambda *args: events.append('nss')),
            P=SimpleNamespace(), GenuineC5Session=Session, CHECK=lambda: events.append('check'))
        def before(observation, key, reacquire):
            events.append('select'); self.assertEqual(key, 'a' * 64)
            reacquire()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); source = base / 'source'; source.mkdir(); output = base / 'output'
            with patch.object(operation, 'load_selected', return_value=engine), \
                 patch.object(operation.os, 'getuid', return_value=0), \
                 patch.object(operation.os, 'geteuid', return_value=0), \
                 patch.object(operation.os, 'getgid', return_value=0), \
                 patch.object(operation.os, 'getegid', return_value=0):
                with self.assertRaisesRegex(ValueError, '^DIAGNOSTIC_BEFORE_PRODUCER$'):
                    operation.qualify(source, output,
                        dict(source_commit='a' * 40, source_tree=operation.SOURCE_TREE),
                        lambda: events.append('currentness'), before)
            record = json.loads((output / 'RESULT.json').read_bytes())
            self.assertFalse(record['producer_owner_invoked'])
            self.assertFalse(record['raw_receiving_complete'])
            self.assertTrue(record['child_terminal_confirmed'])
            self.assertEqual(record['status'], 'UNQUALIFIED')
        self.assertIn('select', events)
        self.assertEqual(events.count('acquire'), 3)
        self.assertEqual(events[-2:], ['check', 'currentness'])


if __name__ == '__main__':
    unittest.main()
