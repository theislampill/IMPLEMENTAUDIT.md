#!/usr/bin/env python3
"""Real claim transactions with a declared fixture native owner, not host admission."""
import os
import contextlib
import hashlib
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import claim_transaction_test as claim
from native_input_adapter_test import binding, exact, reported_window, terminal, NOW


class PhysicalOwnerIsolation(unittest.TestCase):
    def test_identical_installations_keep_their_physical_sibling_and_input_owner(self):
        with tempfile.TemporaryDirectory(prefix='native-owner-isolation-') as temp:
            helpers = []
            for name in ('first', 'second'):
                folder = Path(temp) / name
                folder.mkdir()
                for script in ('claim-run-rotation.py', 'rotate-canonical-state.py',
                               'canonical_hot_projection.py', 'canonical_custody.py',
                               'canonical_rotation_inputs.py'):
                    shutil.copyfile(claim.POST / script, folder / script)
                spec = importlib.util.spec_from_file_location('isolated_claim_' + name,
                                                              folder / 'claim-run-rotation.py')
                owner = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(owner)
                helper = owner.projection_helper()
                self.assertEqual(Path(helper.__file__), folder / 'rotate-canonical-state.py')
                helpers.append(helper)
            self.assertIsNot(helpers[0], helpers[1])
            self.assertIsNot(helpers[0].native_inputs_module_v1(), helpers[1].native_inputs_module_v1())


class NativeClaim(unittest.TestCase):
    history_text = 'q ' * 22000

    def setUp(self):
        self.encoding_path = os.environ.get('R0039_TOKENIZER_ENCODING')
        if not self.encoding_path:
            self.skipTest('exact offline encoding absent; native OR remains unqualified')
        claim.RealHelperIntegration.setUp(self)
        shutil.copyfile(claim.POST / 'canonical_rotation_inputs.py',
                        self.fixture.scripts / 'canonical_rotation_inputs.py')
        self.native = self.helper.native_inputs_module_v1()
        self.clock = mock.patch.object(self.native.time, 'time_ns', return_value=NOW * 1000000).start()
        self.monotonic = mock.patch.object(self.native.time, 'monotonic_ns', return_value=5000000000).start()
        self.addCleanup(mock.patch.stopall)
        predecessor = self.owner.resolve_predecessor(self.context)
        self.binding = binding()
        self.binding.update(subject=self.helper._native_subject(predecessor),
            source_bytes=sum(map(len, self.original_pair.values())),
            source_tokens=sum(self.helper.count_rotation_tokens_v1(
                Path(self.encoding_path).read_bytes(), tuple(self.original_pair.values()))))
        self.binding['budget_policy']['id'] = 'R0039-CONFIGURED-HEADROOM-v1'

    def state(self, used=193800):
        # The sole injected boundary remains the declared in-process native
        # owner below. Supply its COMPLETE immediate-READY wire/profile here so
        # the real public entry and preparation frontend still run unchanged.
        # This is not a live stdio producer, issuer decision or native admission.
        selected = self.select_fixture_owner()
        grant = {'schema': 'implementaudit.native-rotation-owner-grant.v1', 'status': 'ACTIVE',
            **{key: selected[key] for key in ('issuer', 'source_owner', 'source_contract_sha256',
                'provider_selection_sha256', 'producer_sha256', 'owner_decision_locator')},
            'episode_binding_sha256': hashlib.sha256(b'EXPLICIT_UNIT_EPISODE_NOT_NATIVE').hexdigest(),
            'consumer_sha256': hashlib.sha256(Path(self.owner.__file__).read_bytes()).hexdigest(),
            **{key: self.binding[key] for key in ('subject', 'host', 'budget_policy', 'tokenizer')},
            'not_before_unix_ms': NOW, 'expires_at_unix_ms': NOW + 30000}
        self.binding.update(issuer=selected['issuer'], producer_sha256=selected['producer_sha256'],
            semantic_contract_sha256=selected['source_contract_sha256'],
            grant_sha256=hashlib.sha256(self.owner.canonical(grant)).hexdigest())
        state = self.native.NativeInputState(self.binding)
        state.observe(exact(used)); state.observe(reported_window(total=used)); state.observe(terminal())
        # Opaque transport metadata at the existing unit-adapter boundary. No
        # kernel handle/process or authentic host is asserted by this fixture.
        process = {'pid': os.getpid(), 'creation_filetime': 1, 'image': str(Path(sys.executable).resolve())}
        reservation = 'f' * 32
        source = {'schema': 'implementaudit.native-rotation-source.v3', 'phase': 'READY',
            'binding': state._binding, 'exact_usage': state._snapshot, 'reported_window': state._reported_window,
            'cutoff_revision': state._revision, 'observed_monotonic_ns': state._received_monotonic_ns,
            'reservation_id': reservation, 'producer_process': process, 'host_process': dict(process),
            'cancellation': {'schema': 'implementaudit.native-cancellation.v1',
                'producer_process': process, 'event_handle': 1, 'reservation_id': reservation},
            'episode_binding_sha256': grant['episode_binding_sha256'],
            **{key: selected[key] for key in ('source_owner', 'source_contract_sha256', 'provider_selection_sha256')}}
        refs = self.owner.native_input_revision_refs_v1(self.context)
        with self.owner._CUSTODY.git_scope(self.fixture.repo, self.owner.fixed_git(), self.owner.git_environment()):
            predecessor = self.owner.resolve_predecessor(self.context)
            plan = self.owner.prepare_native_source_update_v1(self.context, source, grant,
                expected_source_oid=None, expected_grant_oid=None)
            self.fixture_heads = {refs['source']: self.owner.write_blob(self.context, plan['source_bytes']),
                                  refs['grant']: self.owner.write_blob(self.context, plan['grant_bytes'])}
            self.owner.update_refs(self.context, plan['updates'], self.owner.predecessor_guards(self.context, predecessor))
            self.assertEqual(self.owner.read_refs(self.fixture.repo, refs.values()), self.fixture_heads)
        self.fixture_source, self.fixture_grant = source, grant
        state._native_revision_guards = dict(self.fixture_heads)
        return state

    def select_fixture_owner(self):
        root = self.fixture.run_root / 'declared-native-unit-owner'
        session = root / 'sessions'
        session.mkdir(parents=True)
        thread = '00000000-0000-4000-8000-000000000001'
        stream = session / ('fixture-' + thread + '.jsonl')
        stream.write_bytes(b'{"fixture":"NO_AUTHENTIC_NATIVE_CAPTURE"}\n')
        evidence = root / 'unit-owner.json'
        evidence.write_bytes(b'{"authority_ceiling":"NONE","owner":"IN_PROCESS_TEST_ADAPTER"}\n')
        def pin(path):
            raw = path.read_bytes()
            return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        peers = claim.BASE / 'source-peers/native-runtime/skills/implementaudit/scripts'
        provider = {'schema': 'implementaudit.codex-owned-stdio-provider-selection.v1',
            'profile_id': 'codex-app-server-0.153.4-owned-stdio-candidate-v1',
            'root_thread_id': thread, 'root_agent_path': '/root', 'root_source': str(stream),
            'session_root': str(session), 'cwd': str(root), 'codex_home': str(root),
            'cli_version': '0.153.4', 'native_version': 'codex-cli 0.153.4',
            'native_executable': pin(Path(sys.executable).resolve()),
            'runtime_helpers': {name: pin(peers / name) for name in
                ('bounded_native_reader.py', 'bounded_source_owner.py', 'bounded_file_custody.py')},
            'episode_owner': {'module_pin': pin(evidence), 'repository': str(self.fixture.repo),
                              'controller': claim.CONTROLLER},
            'pending_owner': {'store': str(root / 'UNUSED_UNIT_STORE'), 'session_id': thread,
                              'owner_id': 'IN_PROCESS_TEST_ADAPTER'},
            'producer_capture_pin': pin(evidence), 'capture_producer_pin': pin(evidence),
            'tool_evidence_contract': 'EXACT_ORIGINAL_CUSTOM_EXEC_AND_COLLABORATION_V1',
            'rotation_input_owner': {'repo': str(self.fixture.repo), 'controller': claim.CONTROLLER,
                'claim_id': self.context['claim_id'], 'run_root_identity': self.context['run_root_identity'],
                'issuer': self.binding['issuer'], 'source_contract_sha256': self.binding['semantic_contract_sha256'],
                'owner_decision_locator': 'EXPLICIT_UNIT_ADAPTER_NO_PRODUCTION_OWNER_DECISION'}}
        profile = root / 'provider.json'
        profile.write_bytes(self.owner.canonical(provider))
        template = (peers / 'compaction-source-owner-codex-app.py').read_bytes()
        self.assertEqual(hashlib.sha256(template).hexdigest(), self.owner._NATIVE_SOURCE_OWNER_TEMPLATE_SHA256)
        marker = b'OWNED_STDIO_SELECTION_PIN = None'
        self.assertEqual(template.count(marker), 1)
        materialized = template.replace(marker, b'OWNED_STDIO_SELECTION_PIN = ' + repr(pin(profile)).encode())
        self.assertLessEqual(len(materialized), 131072)
        (self.fixture.scripts / 'compaction-source-owner-codex-app.py').write_bytes(materialized)
        selected = self.owner._native_selection_v1(self.context)
        def close_selection():
            held = self.owner._NATIVE_PRIVATE_PROFILE_V1
            if held is not None:
                for item in reversed(held[2]):
                    item.close()
                self.owner._NATIVE_PRIVATE_PROFILE_V1 = None
        self.addCleanup(close_selection)
        return selected

    @contextlib.contextmanager
    def fixture_owner(self, state):
        """Existing unit seam, with real profile/ref/wire closure on every read.

        Source transport authentication is intentionally outside this in-process
        adapter test. No preparation, CAS, custody or freshness gate is mocked.
        """
        def resolve(controller):
            self.assertEqual(controller, claim.CONTROLLER)
            selected = self.owner._native_selection_v1(self.context)
            self.assertEqual(self.owner.read_refs(self.fixture.repo, self.fixture_heads), self.fixture_heads)
            refs = self.owner.native_input_revision_refs_v1(self.context)
            source = self.owner.decode_json(self.owner.read_blob(self.fixture.repo, self.fixture_heads[refs['source']]))
            grant = self.owner.decode_json(self.owner.read_blob(self.fixture.repo, self.fixture_heads[refs['grant']]))
            self.assertEqual(source, self.fixture_source)
            self.assertEqual(grant, self.fixture_grant)
            self.assertEqual(source['binding'], state._binding)
            self.assertEqual(source['exact_usage'], state._snapshot)
            self.assertEqual(source['reported_window'], state._reported_window)
            self.assertEqual(source['observed_monotonic_ns'], state._received_monotonic_ns)
            self.assertEqual(state._binding['grant_sha256'], hashlib.sha256(self.owner.canonical(grant)).hexdigest())
            for key in ('issuer', 'source_owner', 'source_contract_sha256', 'provider_selection_sha256',
                        'producer_sha256', 'owner_decision_locator'):
                self.assertEqual(grant[key], selected[key])
            self.native._validate_binding(state._binding)
            self.native.validate_reported_window_v1(source['reported_window'], state._binding,
                source['exact_usage'], source['cutoff_revision'])
            return state
        with mock.patch.object(self.native, '_resolve_existing_owner_v1', side_effect=resolve):
            yield

    def rotate(self):
        return self.owner.run_canonical_rotation_v1(self.context, self.owner_map,
            self.helper.full_or_calibration_contract_v1(),
            tokenizer_encoding=self.encoding_path, native_input=True)

    def refs(self):
        return self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)')

    def test_health_only_input_reaches_real_claim_cas_and_original_receipt(self):
        state = self.state()
        with self.fixture_owner(state):
            result = self.rotate()
        self.assertEqual(result['status'], 'ROTATED')
        self.assertTrue(state._consumed)
        record, _ = self.owner.read_epoch(self.context, 'G0002')
        self.assertEqual(record['prepared']['measurement']['triggered_by'], ['CONTEXT_HEALTH'])
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.assertEqual(joined['receipt_token'], result['receipt_token'])
        receipt = self.owner.read_blob(self.fixture.repo, result['receipt_token'].split('@')[1])
        self.assertEqual(len(receipt.decode().strip().split('\t')), 14)
        for role, original in self.original_pair.items():
            self.assertEqual((self.fixture.run_root / (role + '.md')).read_bytes(), original)
            self.assertEqual(self.owner.read_component(self.context, role), joined[role.lower() + '_bytes'])

    def test_source_withdrawal_during_actual_cas_is_unknown_without_automatic_recovery(self):
        state = self.state()
        original = self.owner.git_process
        commits = []
        def race(repo, *args, **kwargs):
            result = original(repo, *args, **kwargs)
            if args[:1] == ('update-ref',):
                commits.append(result.returncode)
                state.withdraw_admission()
            return result
        with self.fixture_owner(state), \
             mock.patch.object(self.owner, 'git_process', side_effect=race):
            with self.assertRaises(self.native.NativeInputOutcomeUnknown):
                self.rotate()
        self.assertEqual(commits, [0])
        with self.assertRaises((self.owner.RotationError, self.owner.LegacyRoute)):
            self.owner.require_current_generation_join_v1(self.context)

    def test_below_all_thresholds_is_no_effect(self):
        state = self.state(17014)
        before = self.refs()
        self.owner_map.unlink()
        with self.fixture_owner(state):
            result = self.rotate()
        self.assertEqual(result['status'], 'NOT_TRIGGERED')
        self.assertEqual(result['input_scope'], 'BYTES_TOKENS_AND_CONFIGURED_HEADROOM')
        self.assertEqual(self.refs(), before)
        self.assertFalse(state._consumed)

    def test_public_native_mode_refuses_unadmitted_source_before_archive(self):
        before = self.refs()
        result = self.fixture.claim('--rotate-canonical-state', claim.CONTROLLER,
            '--owner-map', str(self.owner_map), '--tokenizer-encoding', self.encoding_path, '--native-input')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'NATIVE_INPUT_EXISTING_OWNER_SELECTION_ABSENT', result.stderr)
        self.assertEqual(self.refs(), before)


if __name__ == '__main__':
    unittest.main()
