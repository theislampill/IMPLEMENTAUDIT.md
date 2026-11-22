#!/usr/bin/env python3
"""Real disposable-file controls; never open or modify the system NSS file."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('boot_nss', ROOT / 'scripts/hosted-boot-nss.py')
N = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(N)
BEFORE = b'# disposable fixture\npasswd:         files systemd\ngroup: files\n'
AFTER = BEFORE.replace(b'passwd:         files systemd\n', b'passwd:         files\n')


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


class BootControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='g132-boot-nss-control-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'nsswitch.conf'
        self.target.write_bytes(BEFORE)
        self.target.chmod(0o644)
        self.context = dict(run_id='77', attempt='1', boot_id='disposable-fixture',
                            operation='SOURCE_ONLY_CONTROL')
        self.opening = self.target.stat()
        self.before_fds = N.descriptors()

    def owner(self):
        return N._BootNSSFiles(self.root, self.context, expected_uid=os.getuid(),
                               expected_gid=os.getgid(), before_pin=pin(BEFORE), after_pin=pin(AFTER))

    def assert_closed(self):
        self.assertEqual(N.descriptors(), self.before_fds)

    def test_configured_retention_and_fresh_readback(self):
        owner = self.owner()
        result = owner.provision()
        self.assertEqual(self.target.read_bytes(), AFTER)
        self.assertTrue(result['configured'])
        self.assertTrue(result['descriptor_restoration'])
        self.assertEqual(result['administrative_disposition'], 'RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL')
        self.assertFalse(result['deletion_attempted'])
        self.assertFalse(result['restoration_attempted'])
        self.assertFalse(result['vm_disposal_observed'])
        self.assertFalse(result['predecessor_process_custody_recovered'])
        original = owner.slot_path / 'exchange-member'
        self.assertEqual(original.read_bytes(), BEFORE)
        self.assertEqual((original.stat().st_dev, original.stat().st_ino),
                         (self.opening.st_dev, self.opening.st_ino))
        self.assertEqual((owner.slot_path / 'preimage.raw').read_bytes(), BEFORE)
        observed = self.owner().verify()
        self.assertTrue(observed['configured'])
        self.assertTrue(observed['descriptor_restoration'])
        self.assert_closed()

    def test_replay_and_already_after_without_journal_refused(self):
        self.owner().provision()
        with self.assertRaises(N.Refusal):
            self.owner().provision()
        self.assertEqual(self.target.read_bytes(), AFTER)
        self.assert_closed()
        with tempfile.TemporaryDirectory(prefix='g132-boot-orphan-') as value:
            root = Path(value)
            (root / 'nsswitch.conf').write_bytes(AFTER)
            (root / 'nsswitch.conf').chmod(0o644)
            owner = N._BootNSSFiles(root, self.context, expected_uid=os.getuid(),
                                   expected_gid=os.getgid(), before_pin=pin(BEFORE), after_pin=pin(AFTER))
            with self.assertRaises(N.Refusal):
                owner.provision()
            self.assertEqual((root / 'nsswitch.conf').read_bytes(), AFTER)

    def test_unsupported_target_alias_link_and_mode(self):
        for kind in ('symlink', 'hardlink', 'mode'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix='g132-boot-alias-') as value:
                root = Path(value)
                target = root / 'nsswitch.conf'
                target.write_bytes(BEFORE)
                target.chmod(0o644)
                if kind == 'symlink':
                    target.rename(root / 'foreign')
                    target.symlink_to('foreign')
                elif kind == 'hardlink':
                    os.link(target, root / 'foreign')
                else:
                    target.chmod(0o666)
                owner = N._BootNSSFiles(root, self.context, expected_uid=os.getuid(),
                                       expected_gid=os.getgid(), before_pin=pin(BEFORE), after_pin=pin(AFTER))
                with self.assertRaises(N.Refusal):
                    owner.provision()
                self.assertEqual(target.read_bytes(), BEFORE)
        self.assert_closed()

    def test_wrong_preimage_pin_refused_without_exchange(self):
        self.target.write_bytes(BEFORE + b'# unexpected\n')
        with patch.object(N, '_exchange', side_effect=AssertionError('must not exchange')):
            with self.assertRaises(N.Refusal) as caught:
                self.owner().provision()
        self.assertFalse(caught.exception.record['exchange_attempted'])
        self.assertEqual(self.target.read_bytes(), BEFORE + b'# unexpected\n')
        self.assert_closed()

    def test_post_exchange_exception_remains_uncertain_and_no_replay(self):
        owner = self.owner()
        real = N._exchange
        def effect_then_error(*args):
            real(*args)
            raise OSError('injected after actual exchange')
        with patch.object(N, '_exchange', side_effect=effect_then_error):
            with self.assertRaises(N.Refusal) as caught:
                owner.provision()
        self.assertEqual(self.target.read_bytes(), AFTER)
        self.assertIsNone(caught.exception.record['configured'])
        self.assertEqual(caught.exception.record['state'], 'EXCHANGE_OUTCOME_UNCERTAIN')
        self.assertTrue((owner.slot_path / '02-exchange-intent.json').exists())
        self.assertFalse((owner.slot_path / '03-configured.json').exists())
        with self.assertRaises(N.Refusal):
            self.owner().verify()
        with self.assertRaises(N.Refusal):
            self.owner().provision()
        self.assert_closed()

    def test_foreign_target_at_atomic_effect_retained_and_refused(self):
        owner = self.owner()
        real = N._exchange
        foreign = b'foreign target must survive\n'
        def substitute(left_fd, left, right_fd, right):
            os.rename(left, 'moved-owned-original', src_dir_fd=left_fd, dst_dir_fd=left_fd)
            fd = os.open(left, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, dir_fd=left_fd)
            try:
                os.write(fd, foreign)
            finally:
                os.close(fd)
            real(left_fd, left, right_fd, right)
        with patch.object(N, '_exchange', side_effect=substitute):
            with self.assertRaises(N.Refusal) as caught:
                owner.provision()
        self.assertEqual((self.root / 'moved-owned-original').read_bytes(), BEFORE)
        self.assertEqual((owner.slot_path / 'exchange-member').read_bytes(), foreign)
        self.assertEqual(self.target.read_bytes(), AFTER)
        self.assertIsNone(caught.exception.record['configured'])
        self.assertFalse(caught.exception.record['deletion_attempted'])
        with self.assertRaises(N.Refusal):
            self.owner().verify()
        self.assert_closed()

    def test_foreign_exchange_member_at_effect_retained_and_refused(self):
        owner = self.owner()
        real = N._exchange
        foreign = b'foreign replacement must survive\n'
        def substitute(left_fd, left, right_fd, right):
            os.rename(right, 'moved-owned-postimage', src_dir_fd=right_fd, dst_dir_fd=right_fd)
            fd = os.open(right, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, dir_fd=right_fd)
            try:
                os.write(fd, foreign)
            finally:
                os.close(fd)
            real(left_fd, left, right_fd, right)
        with patch.object(N, '_exchange', side_effect=substitute):
            with self.assertRaises(N.Refusal) as caught:
                owner.provision()
        self.assertEqual(self.target.read_bytes(), foreign)
        self.assertEqual((owner.slot_path / 'exchange-member').read_bytes(), BEFORE)
        self.assertEqual((owner.slot_path / 'moved-owned-postimage').read_bytes(), AFTER)
        self.assertIsNone(caught.exception.record['configured'])
        self.assertFalse(caught.exception.record['deletion_attempted'])
        self.assert_closed()

    def test_intent_write_failure_blocks_effect_and_retains_marker(self):
        owner = self.owner()
        real = N._BootNSSFiles._append
        def fail_intent(instance, name, payload):
            if name == '02-exchange-intent.json':
                raise OSError('injected journal failure before effect')
            return real(instance, name, payload)
        with patch.object(N._BootNSSFiles, '_append', fail_intent), \
             patch.object(N, '_exchange', side_effect=AssertionError('must not exchange')):
            with self.assertRaises(N.Refusal) as caught:
                owner.provision()
        self.assertFalse(caught.exception.record['exchange_attempted'])
        self.assertEqual(self.target.read_bytes(), BEFORE)
        self.assertTrue((owner.slot_path / '00-reserved.json').exists())
        self.assertTrue((owner.slot_path / 'exchange-member').exists())
        with self.assertRaises(N.Refusal):
            self.owner().provision()
        self.assert_closed()

    def test_configured_target_drift_refused_without_mutation(self):
        self.owner().provision()
        drift = AFTER + b'# drift\n'
        self.target.write_bytes(drift)
        with self.assertRaises(N.Refusal):
            self.owner().verify()
        self.assertEqual(self.target.read_bytes(), drift)
        self.assert_closed()

    def test_retained_preimage_and_journal_drift_refused(self):
        for selected in ('preimage.raw', 'exchange-member', '03-configured.json'):
            with self.subTest(selected=selected), tempfile.TemporaryDirectory(prefix='g132-boot-drift-') as value:
                root = Path(value)
                (root / 'nsswitch.conf').write_bytes(BEFORE)
                (root / 'nsswitch.conf').chmod(0o644)
                owner = N._BootNSSFiles(root, self.context, expected_uid=os.getuid(),
                                       expected_gid=os.getgid(), before_pin=pin(BEFORE), after_pin=pin(AFTER))
                owner.provision()
                (owner.slot_path / selected).write_bytes(b'changed\n')
                receiver = N._BootNSSFiles(root, self.context, expected_uid=os.getuid(),
                                          expected_gid=os.getgid(), before_pin=pin(BEFORE), after_pin=pin(AFTER))
                with self.assertRaises(N.Refusal):
                    receiver.verify()
                self.assertEqual((root / 'nsswitch.conf').read_bytes(), AFTER)
        self.assert_closed()

    def test_earlier_target_drift_during_later_private_read_refused(self):
        self.owner().provision()
        real = os.open
        drift = AFTER + b'# changed while receiver reads its private preimage\n'
        def mutate_before_private_read(name, flags, *args, **kwargs):
            if name == 'preimage.raw':
                self.target.write_bytes(drift)
            return real(name, flags, *args, **kwargs)
        with patch.object(N.os, 'open', side_effect=mutate_before_private_read):
            with self.assertRaises(N.Refusal):
                self.owner().verify()
        self.assertEqual(self.target.read_bytes(), drift)
        self.assert_closed()

    def test_partial_preimage_write_retained_without_effect_or_delete(self):
        owner = self.owner()
        real = os.pwrite
        def partial_then_error(fd, raw, offset):
            if raw == BEFORE:
                real(fd, raw[:7], offset)
                raise OSError('injected after real partial preimage write')
            return real(fd, raw, offset)
        with patch.object(N.os, 'pwrite', side_effect=partial_then_error):
            with self.assertRaises(N.Refusal) as caught:
                owner.provision()
        self.assertEqual(self.target.read_bytes(), BEFORE)
        self.assertEqual((owner.slot_path / 'preimage.raw').read_bytes(), BEFORE[:7])
        self.assertFalse(caught.exception.record['exchange_attempted'])
        self.assertFalse(caught.exception.record['deletion_attempted'])
        with self.assertRaises(N.Refusal):
            self.owner().provision()
        self.assert_closed()

    def test_context_change_cannot_adopt_configured_state(self):
        self.owner().provision()
        self.context['boot_id'] = 'different-boot'
        with self.assertRaises(N.Refusal):
            self.owner().verify()
        self.assert_closed()

    def test_close_error_retains_observation_but_refuses_descriptor_custody(self):
        real = os.close
        injected = False
        def close_then_error(fd):
            nonlocal injected
            real(fd)
            if not injected:
                injected = True
                raise OSError(5, 'injected after actual descriptor close')
        with patch.object(N.os, 'close', side_effect=close_then_error):
            with self.assertRaises(N.Refusal) as caught:
                self.owner().provision()
        self.assertTrue(caught.exception.record['configured'])
        self.assertFalse(caught.exception.record['descriptor_restoration'])
        self.assertEqual(self.target.read_bytes(), AFTER)
        self.assert_closed()

    def test_production_pins_and_nonhost_refusal(self):
        self.assertEqual(N.BEFORE, dict(bytes=526, sha256='b953df1d0016f515fc052ca6bb0ccd092b8d13c8789c51c4eaef2b0461574e57'))
        self.assertEqual(N.AFTER, dict(bytes=518, sha256='5cde76a7763cef05fea9a086f5db0025459d489ee658a8369602e415e47beff7'))
        with patch.dict(os.environ, {}, clear=True), patch.object(N, '_BootNSSFiles', side_effect=AssertionError('must not open system parent')):
            with self.assertRaises(ValueError):
                N.provision_hosted(self.context)
        self.assert_closed()


if __name__ == '__main__':
    unittest.main(verbosity=2)
