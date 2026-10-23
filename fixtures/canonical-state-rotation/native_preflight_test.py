#!/usr/bin/env python3
"""Constructed input controls plus real Git CAS; no native admission/benchmark.

Breaks caught: redundant direct preflight resolution; skipped custody/cancellation;
dropped source/grant CAS guards; omitted before/after/final checks or readback;
changed legacy ref_guards behavior; collapsed C02 live owner checkpoints.
Owner resolution and cancellation/C02 stimuli are constructed, not admission.
Native guard/state, retained file custody, namespace gate, read_refs and Git CAS
execute real code; the custody-failure control explicitly injects one exception.
"""
import contextlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from native_input_adapter_test import reported_window

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/implementaudit/scripts'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

owner = load('native_preflight_owner_under_test', SCRIPTS / 'claim-run-rotation.py')
native = load('native_preflight_inputs_under_test', SCRIPTS / 'canonical_rotation_inputs.py')
SUBJECT = {'controller': 'coalescing-fixture', 'claim_id': '1' * 32,
    'run_root_identity': '.IMPLEMENTAUDIT/runs/fixture-Ab12Cd',
    'receipt_token': 'refs/implementaudit/continuity-receipts/coalescing-fixture/G0001@' + '2' * 40,
    'state_sha256': '3' * 64, 'roadmap_sha256': '4' * 64}

def binding():
    return {'issuer': 'CONSTRUCTED-OWNER-NO-NATIVE-AUTHORITY',
        'grant_sha256': '5' * 64, 'producer_sha256': '6' * 64,
        'semantic_contract_sha256': '7' * 64,
        'host': {'name': 'codex', 'version': '0.153.4',
            'binary_sha256': '444a3f0008050605cae73cd9b7a2dcac61294062dfaab56dd20430fd6498518b',
            'effective_config_sha256': '8' * 64, 'model': 'gpt-6-astra'},
        'budget_policy': {'id': 'CONSTRUCTED-HEADROOM',
            'configured_usable_tokens': 258400, 'maximum_age_ms': 30000},
        'tokenizer': {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.13.0',
            'encoding_sha256': '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7'},
        'subject': SUBJECT, 'source_bytes': 100000, 'source_tokens': 30000,
        'thread_id': 'constructed-thread', 'turn_id': 'constructed-turn'}

class StickyCancellation:
    """Deterministic signal stimulus, not a Windows producer capability."""
    cancelled = False
    def check(self):
        if self.cancelled:
            raise RuntimeError('CONSTRUCTED_STICKY_CANCELLATION')

class ConstructedC02Lease:
    """Exercises real C02 operation checks, never an issuer/source grant."""
    live = True
    def verify(self):
        if not self.live:
            raise owner.RotationError('CONSTRUCTED_C02_LEASE_WITHDRAWN')
    def checkpoint(self):
        self.verify()
        return 'CONSTRUCTED-REVISION-ONE'
    def census(self):
        self.verify()
        return {}
    def grant(self):
        self.verify()
        return {}

class NativePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workspace = tempfile.TemporaryDirectory(prefix='native-preflight-')
        cls.addClassCleanup(workspace.cleanup)
        # Resolve platform temp aliases before invoking descriptor-relative custody.
        cls.repo = Path(workspace.name).resolve()
        owner.git(cls.repo, 'init', '--quiet')
        (cls.repo / '.IMPLEMENTAUDIT/.r36-locks').mkdir(parents=True)
        cls.oids = {name: owner.git(cls.repo, 'hash-object', '-w', '--stdin',
                    input_bytes=name.encode()).decode().strip()
                    for name in ('source', 'grant', 'old', 'new', 'drift')}
        cls.source_ref = 'refs/implementaudit/rotation-input-sources/coalescing-fixture'
        cls.grant_ref = 'refs/implementaudit/rotation-input-grants/coalescing-fixture'
        cls.target_ref = 'refs/implementaudit/coalescing-fixture-target'
        cls.file = cls.repo / 'retained.txt'
        cls.file.write_bytes(b'exact retained source bytes\n')

    def setUp(self):
        self.trace, self.hooks, self.reads, self.native_calls = [], {}, 0, 0
        self.c02_calls = 0
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.real_git_process, self.real_read_refs = owner.git_process, owner.read_refs
        for ref, name in ((self.source_ref, 'source'), (self.grant_ref, 'grant'), (self.target_ref, 'old')):
            owner.git(self.repo, 'update-ref', ref, self.oids[name])
        self.expected = {self.source_ref: self.oids['source'], self.grant_ref: self.oids['grant']}
        self.state = native.NativeInputState(binding())
        self.state.observe({'method': 'rawResponse/completed', 'params': {
            'threadId': 'constructed-thread', 'turnId': 'constructed-turn', 'responseId': 'resp_constructed',
            'usage': {'inputTokens': 17003, 'outputTokens': 11, 'totalTokens': 17014,
                'cachedInputTokens': 0, 'cacheWriteInputTokens': 0, 'reasoningOutputTokens': 0}}})
        self.state.observe(reported_window(thread_id='constructed-thread', turn_id='constructed-turn'))
        self.state.observe({'method': 'turn/completed', 'params': {
            'threadId': 'constructed-thread', 'turn': {'id': 'constructed-turn', 'status': 'completed'}}})
        self.state._native_revision_guards = dict(self.expected)
        self.cancel = StickyCancellation()
        self.state._native_cancellation_wait = self.cancel
        lease = native._RotationInputLease(self.state)
        self.state._active_lease = lease
        self.guard = native._PublisherGuard(lease, SUBJECT, 100000, 30000)
        self.retained = owner.RetainedInputs([self.file])
        self.stack.callback(self.retained.close)
        self.observation = owner._NativePublicationInputs(self.retained, self.guard)
        for obj, name, label in ((self.retained, 'verify', 'retained'),
                (self.guard, 'verify', 'native'), (self.guard, 'before_effect', 'before_effect'),
                (self.guard, 'after_effect', 'after_effect')):
            real = getattr(obj, name)
            def tracked(*a, _real=real, _label=label, **kw):
                self.trace.append(_label)
                if _label == 'native':
                    self.native_calls += 1
                return _real(*a, **kw)
            self.stack.enter_context(mock.patch.object(obj, name, side_effect=tracked))
        self.stack.enter_context(mock.patch.object(native, '_resolve_existing_owner_v1', side_effect=self.resolve))
        self.stack.enter_context(mock.patch.object(owner, 'read_refs', side_effect=self.read_refs))
        self.stack.enter_context(mock.patch.object(owner, 'git_process', side_effect=self.git_process))

    def hook(self, point):
        if point in self.hooks:
            self.hooks.pop(point)()

    def resolve(self, controller):
        self.trace.append('resolve')
        if controller != SUBJECT['controller'] or self.real_read_refs(self.repo, self.expected) != self.expected:
            raise native.NativeInputError('CONSTRUCTED_NATIVE_REF_DRIFT')
        return self.state

    def read_refs(self, repo, refs):
        self.reads += 1
        phase = 'preflight' if self.reads == 1 else 'readback'
        self.trace.append(phase)
        self.hook(phase + '.before')
        result = self.real_read_refs(repo, refs)
        self.hook(phase + '.after')
        return result

    def git_process(self, repo, *argv, **kwargs):
        if argv == ('update-ref', '--stdin', '-z'):
            self.trace.append('cas')
            self.hook('cas.before')
            result = self.real_git_process(repo, *argv, **kwargs)
            self.hook('cas.after')
            return result
        return self.real_git_process(repo, *argv, **kwargs)

    def current(self, ref):
        return self.real_read_refs(self.repo, [ref])[ref]

    def drift(self, role):
        ref = {'source': self.source_ref, 'grant': self.grant_ref, 'target': self.target_ref}[role]
        result = self.real_git_process(self.repo, 'update-ref', ref, self.oids['drift'])
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def publish(self, observation=None):
        with owner._CUSTODY.git_scope(self.repo, owner.fixed_git(), owner.git_environment()):
            owner.update_refs({'repo': self.repo}, {self.target_ref: (self.oids['new'], self.oids['old'])},
                {}, observation=self.observation if observation is None else observation)

    def c02(self):
        self.source, self.issuer = ConstructedC02Lease(), ConstructedC02Lease()
        operation = owner._C02OwnedOperation({}, 'CONSTRUCTED-TOKEN', {}, self.source, self.issuer)
        real = operation.verify
        def tracked():
            self.c02_calls += 1
            self.trace.append('c02')
            self.hook('c02.' + str(self.c02_calls))
            return real()
        self.stack.enter_context(mock.patch.object(operation, 'verify', side_effect=tracked))
        self.observation = owner._C02PublicationInputs(self.observation, operation)

    def test_direct_native_one_preflight_verification(self):
        self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['new'])
        self.assertEqual(self.native_calls, 5, 'direct update_refs must remove exactly one duplicate verification')
        self.assertEqual(self.trace, ['retained', 'native', 'resolve', 'preflight',
            'retained', 'native', 'resolve', 'before_effect', 'native', 'resolve',
            'cas', 'after_effect', 'native', 'resolve', 'retained', 'readback',
            'retained', 'native', 'resolve'])

    def test_legacy_ref_guards_reverify_cancellation(self):
        self.assertEqual(self.observation.ref_guards_v1(), self.expected)
        self.cancel.cancelled = True
        with self.assertRaisesRegex(native.NativeInputError, 'NATIVE_SOURCE_CANCELLED'):
            self.observation.ref_guards_v1()
        self.assertEqual(self.native_calls, 2)
        self.assertEqual(self.current(self.target_ref), self.oids['old'])

    def test_non_native_retained_checks_remain(self):
        self.publish(self.retained)
        self.assertEqual(self.trace, ['retained', 'preflight', 'cas', 'readback', 'retained'])
        self.assertEqual(self.current(self.target_ref), self.oids['new'])

    def test_retained_custody_failure_prevents_native_and_effect(self):
        with mock.patch.object(self.retained, 'verify', side_effect=owner.CustodyError('CONSTRUCTED_CUSTODY_FAILURE')):
            with self.assertRaises(owner.CustodyError):
                self.publish()
        self.assertEqual(self.native_calls, 0)
        self.assertEqual(self.current(self.target_ref), self.oids['old'])

    def test_exact_readback_refuses_post_effect_target_drift(self):
        self.hooks['readback.before'] = lambda: self.drift('target')
        with self.assertRaises(owner.CASFailure):
            self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['drift'])

    def test_c02_full_sequence_unchanged(self):
        self.c02()
        self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['new'])
        self.assertEqual(self.native_calls, 8)
        self.assertEqual(self.c02_calls, 10)
        self.assertEqual(self.trace, ['c02', 'retained', 'native', 'resolve', 'c02',
            'c02', 'native', 'resolve', 'preflight', 'c02', 'retained', 'native', 'resolve',
            'c02', 'retained', 'native', 'resolve', 'before_effect', 'native', 'resolve',
            'c02', 'cas', 'c02', 'after_effect', 'native', 'resolve', 'retained',
            'retained', 'native', 'resolve', 'c02', 'readback', 'c02', 'retained',
            'native', 'resolve', 'c02'])

def cancellation_case(point, landed):
    def test(self):
        if point == 'initial':
            self.cancel.cancelled = True
        else:
            self.hooks[point] = lambda: setattr(self.cancel, 'cancelled', True)
        error = native.NativeInputOutcomeUnknown if landed else native.NativeInputError
        with self.assertRaises(error):
            self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['new' if landed else 'old'])
        if landed:
            with self.assertRaises(native.NativeInputOutcomeUnknown):
                self.guard.verify()  # UNKNOWN remains sticky even if callers try again.
    return test

for point, landed in [('initial', False), ('preflight.after', False),
                       ('cas.before', True), ('cas.after', True), ('readback.after', True)]:
    setattr(NativePreflight, 'test_cancellation_' + point.replace('.', '_'), cancellation_case(point, landed))

def ref_drift_case(role, point, error, landed):
    def test(self):
        if point == 'initial':
            self.drift(role)
        else:
            self.hooks[point] = lambda: self.drift(role)
        with self.assertRaises(error):
            self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['new' if landed else 'old'])
        self.assertEqual(self.current(self.source_ref if role == 'source' else self.grant_ref), self.oids['drift'])
    return test

for role in ('source', 'grant'):
    for point, error, landed in [('initial', native.NativeInputError, False),
            ('preflight.before', owner.CASFailure, False),
            ('cas.before', native.NativeInputOutcomeUnknown, False),
            ('cas.after', native.NativeInputOutcomeUnknown, True)]:
        setattr(NativePreflight, 'test_' + role + '_drift_' + point.replace('.', '_'),
                ref_drift_case(role, point, error, landed))

def c02_drift_case(role, point):
    def test(self):
        self.c02()
        self.hooks[point] = lambda: setattr(getattr(self, role), 'live', False)
        with self.assertRaisesRegex(owner.RotationError, 'CONSTRUCTED_C02_LEASE_WITHDRAWN'):
            self.publish()
        self.assertEqual(self.current(self.target_ref), self.oids['old'])
    return test

for role, point in [('source', 'c02.2'), ('issuer', 'c02.3'),
                    ('source', 'preflight.after'), ('issuer', 'preflight.after')]:
    setattr(NativePreflight, 'test_c02_' + role + '_drift_' + point.replace('.', '_'), c02_drift_case(role, point))

if __name__ == '__main__':
    unittest.main()
