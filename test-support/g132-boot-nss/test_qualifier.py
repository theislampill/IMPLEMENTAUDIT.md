#!/usr/bin/env python3
"""Focused receipt/identity controls for the distinct ordinary boot NSS adapter."""
import copy
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


Q = module('boot_qualifier', Path(__file__).with_name('ordinary_qualifier.py'))
N = module('boot_nss_controls', ROOT / 'scripts/hosted-boot-nss.py')
COMMIT, TREE = 'a' * 40, 'b' * 40


class QualifierControls(unittest.TestCase):
    def test_actual_configuration_receipt_join_and_negative_controls(self):
        before = b'passwd:         files systemd\ngroup: files\n'
        after = before.replace(N.OLD_ROW, N.NEW_ROW)
        context = dict(run_id='88', boot_id='fixture-boot')
        binding = Q.boot_binding(context, COMMIT, TREE)
        with tempfile.TemporaryDirectory(prefix='g132-boot-join-') as value:
            root = Path(value)
            target = root / 'nsswitch.conf'
            target.write_bytes(before)
            target.chmod(0o644)
            def owner():
                return N._BootNSSFiles(root, binding, expected_uid=os.getuid(), expected_gid=os.getgid(),
                                       before_pin=N.pin(before), after_pin=N.pin(after))
            configured = owner().provision()
            row = dict(schema='g132.boot-nss-prepare.v1', authority='NONE', operation=Q.OPERATION,
                       context=context, source_commit=COMMIT, source_tree=TREE, nss_pin=Q.NSS_PIN,
                       setup_pin=Q.SETUP_PIN, descriptor_restoration=True,
                       selected_gate_observation='OBSERVED_SELECTED_GATE_PASS', configuration=configured)
            self.assertTrue(Q.boot_join(row, context, COMMIT, TREE))
            current = owner().verify()
            self.assertTrue(Q.configured_join(configured, current))
            for key, replacement in [('configured', None), ('descriptor_restoration', False),
                                     ('exchange_attempted', False), ('original_execution', True),
                                     ('administrative_disposition', 'RESTORED'), ('children_spawned', True)]:
                bad = copy.deepcopy(row)
                bad['configuration'][key] = replacement
                with self.subTest(key=key), self.assertRaises(ValueError):
                    Q.boot_join(bad, context, COMMIT, TREE)
            bad = copy.deepcopy(current)
            bad['configured_target']['ino'] += 1
            with self.assertRaises(ValueError):
                Q.configured_join(configured, bad)
            with Q.legacy() as previous:
                self.assertFalse(previous.nss_cleanup_complete(configured))

    def test_selected_inputs_do_not_create_full_startup_admission(self):
        host = dict(pins=[dict(match=True)] * 12, system_aliases=[dict(match=True)] * 4,
                    nss=dict(result=dict(match=True)), selected_bookends_equal=True,
                    full_startup=dict(match=False, reason='copied runtime absent'))
        self.assertTrue(Q.selected_inputs_match(host))
        for key, value in [('pins', []), ('system_aliases', []), ('selected_bookends_equal', False)]:
            bad = copy.deepcopy(host)
            bad[key] = value
            self.assertFalse(Q.selected_inputs_match(bad))
        self.assertFalse(host['full_startup']['match'])

    def test_exact_source_pins_limits_and_nonhost_refusal(self):
        raw = (ROOT / 'scripts/hosted-boot-nss.py').read_bytes()
        self.assertEqual(Q.NSS_PIN, dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
        with Q.legacy() as previous:
            self.assertEqual(Q.LIMITS, previous.LIMITS)
            self.assertEqual(Q.SETUP_PIN, previous.SETUP_PIN)
            self.assertNotEqual(Q.OPERATION, previous.OPERATION)
            self.assertNotEqual(Q.REF, previous.REF)
        with patch.dict(os.environ, {}, clear=True), patch.object(Q, 'limits', side_effect=AssertionError('must not set host limits')):
            with self.assertRaises(ValueError):
                Q.main(['--step', 'boot-nss', '--source-commit', COMMIT, '--source-tree', TREE])


if __name__ == '__main__':
    unittest.main(verbosity=2)
