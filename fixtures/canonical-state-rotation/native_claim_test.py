#!/usr/bin/env python3
"""Real claim transactions with a declared fixture native owner, not host admission."""
import os
import importlib.util
from pathlib import Path
import shutil
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
        state = self.native.NativeInputState(self.binding)
        state.observe(exact(used)); state.observe(reported_window(total=used)); state.observe(terminal())
        return state

    def rotate(self):
        return self.owner.run_canonical_rotation_v1(self.context, self.owner_map,
            self.helper.full_or_calibration_contract_v1(),
            tokenizer_encoding=self.encoding_path, native_input=True)

    def refs(self):
        return self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)')

    def test_health_only_input_reaches_real_claim_cas_and_original_receipt(self):
        state = self.state()
        with mock.patch.object(self.native, '_resolve_existing_owner_v1', return_value=state):
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
        with mock.patch.object(self.native, '_resolve_existing_owner_v1', return_value=state), \
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
        with mock.patch.object(self.native, '_resolve_existing_owner_v1', return_value=state):
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
        self.assertIn(b'OWNER_UNAVAILABLE_NO_ADMITTED_NATIVE_INPUT_SOURCE', result.stderr)
        self.assertEqual(self.refs(), before)


if __name__ == '__main__':
    unittest.main()
