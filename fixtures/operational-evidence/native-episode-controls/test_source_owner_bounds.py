"""Constructed source-reader controls; no native episode or acceptance credit."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from native_test_support import SCRATCH, functions, load


class SourceOwnerBoundsControls(unittest.TestCase):
    READERS = ('policy', 'attestation', 'release-subject')

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='issuer-bound-', dir=SCRATCH)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / 'compaction-source-owner-codex-app.py'
        self.marker = self.root / 'module-evaluated'
        self.obs = load('compaction-result-observation.py')
        self.result = {'fixture': 'source-code-read'}

    def issuer(self, size):
        # Evaluation touches only this test's marker. Oversized/changed sources
        # must be refused before this deliberately observable effect.
        body = (
            'from pathlib import Path\n'
            f'Path({str(self.marker)!r}).write_text("evaluated", encoding="utf-8")\n'
            f'VALUE = {self.result!r}\n'
            'def validate(*args): return VALUE\n'
            'def host_binding(*args): return VALUE\n'
            'def release_subject(*args, **kwargs): return VALUE\n'
        ).encode()
        self.assertGreaterEqual(size, len(body) + 2)
        raw = body + b'#' + b'x' * (size - len(body) - 2) + b'\n'
        self.path.write_bytes(raw)
        return {'path': str(self.path), 'bytes': size,
                'sha256': hashlib.sha256(raw).hexdigest()}

    def release_subject(self, pin):
        """Real pending function and artifact reader; native gates are fixtures.

        The complete assignment/result/P/C/Q shapes used by this function are
        explicit. Native authentication is outside these source-reader controls.
        The real pending before/after file guard and code-artifact I/O execute.
        """
        obs = self.obs
        child = 'constructed-child'
        source = {'profile_id': obs.NONPROTECTED_PROFILE}
        code = {'fixture': 'unchanged-code'}
        accepted = {'fixture': 'separate-acceptance'}
        actual = {'status': 'SUCCEEDED', 'return_digest': '1' * 64,
                  'observation_id': 'constructed-observation', 'evidence': {}}
        ceiling = {'authority': 'NONE'}
        candidate = self.root / 'candidate.json'
        candidate.write_bytes(b'{"fixture":"unconsumed-candidate"}\n')
        candidate_pin = {'path': str(candidate), 'bytes': candidate.stat().st_size,
                         'sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}
        policy = {'policy_digest': '2' * 64, 'descriptor': {
            'custody_namespace': 'constructed-custody',
            'authenticating_source_owner': {'module_pin': pin}}}
        profile = {'qualification_record_bound': True, 'Q': {'fixture': 'Q'}}
        assignment = {'code': code, 'observation_source': source,
                      'reservation_request': {'scope': []}, 'join': None,
                      'return': {'child_id': child, **actual, **ceiling},
                      'prepared': {actual['observation_id']: {}},
                      'accepted': accepted, 'policy': policy,
                      'logical_join': {'acquisition': {'candidate': candidate_pin}}}
        state = {'assignments': {child: assignment}}
        state_path = self.root / 'pending.json'
        state_path.write_text(json.dumps(state), encoding='utf-8')
        view = types.SimpleNamespace(**vars(obs))
        view.actual_result = lambda *args, **kwargs: copy.deepcopy(actual)
        view.acceptance = lambda *args: copy.deepcopy(accepted)
        view.fixed_policy = lambda *args: copy.deepcopy(policy)
        view.acquire_candidate = lambda *args: ({'fixture': 'C'}, candidate_pin)
        view.production_profile = lambda *args: copy.deepcopy(profile)
        env = {'OBSERVATION': view, 'Path': Path, 'CEILING': ceiling,
               'Refusal': ValueError, 'require': obs.require, 'text': str,
               'state_path': lambda *args: state_path,
               'load': lambda *args: json.loads(state_path.read_text()),
               '_assignment_code_identity': lambda assignment: code,
               '_rebind_selected_assignment': lambda *args: source,
               'selected_audit_state_pin': lambda: {'fixture': 'skill'},
               'prior_history_context': lambda *args: None}
        functions('compaction-audit-pending.py', ['boundary_release_subject'], env)
        before = state_path.read_bytes()
        response = env['boundary_release_subject'](
            self.root, 'constructed-session', 'constructed-owner', {
                'child_id': child, 'return_digest': actual['return_digest'],
                'acceptance': accepted, 'child_terminal': {'fixture': 'terminal'}})
        self.assertEqual(state_path.read_bytes(), before)
        self.assertEqual(response['status'], 'SOURCE_BOUND_RELEASE_SUBJECT_READY')
        self.assertFalse(response['pending_consumed'])
        self.assertFalse(response['host_producer_authenticated'])
        return response['subject']

    def read(self, reader, pin):
        # Relocate only the inert public module's sibling lookup into the owned
        # fixture. No production source or configured native owner is modified.
        with mock.patch.object(self.obs, '__file__',
                               str(self.root / 'compaction-result-observation.py')):
            if reader == 'policy':
                key = str(Path('implementaudit/scripts/compaction-source-owner-codex-app.py'))
                return self.obs._nonprotected_source_owner({key: pin['sha256']}).VALUE
            if reader == 'attestation':
                # Post-read native attestation receiving is a separate gate.
                with mock.patch.object(self.obs, 'validate_source_owner_attestation_record',
                                       side_effect=lambda value, *args: value):
                    return self.obs.source_owner_attestation(
                        {'module_pin': pin}, {}, {},
                        {'profile_id': self.obs.NONPROTECTED_PROFILE},
                        {}, {}, {}, {}, {}, self.root, {})
            return self.release_subject(pin)

    def test_all_issuer_readers_accept_delivered_module_length(self):
        pin = self.issuer(131651)
        for reader in self.READERS:
            with self.subTest(reader=reader):
                try:
                    result = self.read(reader, pin)
                except ValueError as error:
                    self.fail(f'{reader} refused the admitted issuer length: {error}')
                self.assertEqual(result, self.result)
                self.assertEqual(self.marker.read_text(), 'evaluated')

    def test_all_issuer_readers_accept_exact_code_ceiling(self):
        pin = self.issuer(262144)
        for reader in self.READERS:
            with self.subTest(reader=reader):
                try:
                    result = self.read(reader, pin)
                except ValueError as error:
                    self.fail(f'{reader} refused the exact code-artifact ceiling: {error}')
                self.assertEqual(result, self.result)

    def test_all_issuer_readers_refuse_above_ceiling_before_evaluation(self):
        pin = self.issuer(262145)
        for reader in self.READERS:
            with self.subTest(reader=reader):
                with self.assertRaisesRegex(ValueError, '^ARTIFACT_PIN_BOUND$'):
                    self.read(reader, pin)
                self.assertFalse(self.marker.exists())

    def test_all_issuer_readers_refuse_wrong_digest(self):
        pin = self.issuer(128000)
        pin['sha256'] = '0' * 64
        for reader in self.READERS:
            with self.subTest(reader=reader):
                with self.assertRaisesRegex(ValueError, '^ARTIFACT_PIN_CHANGED$'):
                    self.read(reader, pin)
                self.assertFalse(self.marker.exists())

    def test_supplied_declared_length_must_match_the_real_file(self):
        pin = self.issuer(128000)
        pin['bytes'] -= 1
        # Policy loading derives its length from the real sibling file; the
        # other two entrypoints receive declared module pins.
        for reader in ('attestation', 'release-subject'):
            with self.subTest(reader=reader):
                with self.assertRaisesRegex(ValueError, '^ARTIFACT_BYTE_COUNT$'):
                    self.read(reader, pin)
                self.assertFalse(self.marker.exists())

    def test_all_issuer_readers_refuse_replacement_before_open(self):
        original_open = open
        for reader in self.READERS:
            with self.subTest(reader=reader):
                pin = self.issuer(128000)
                held = self.root / ('held-' + reader)
                swapped = False

                def replace_then_open(path, *args, **kwargs):
                    nonlocal swapped
                    if Path(path) == self.path and not swapped:
                        swapped = True
                        self.path.rename(held)
                        self.path.write_bytes(held.read_bytes())
                    return original_open(path, *args, **kwargs)

                with mock.patch('builtins.open', side_effect=replace_then_open):
                    with self.assertRaisesRegex(ValueError, '^ARTIFACT_PHYSICAL_CHANGED$'):
                        self.read(reader, pin)
                self.assertTrue(swapped)
                self.assertFalse(self.marker.exists())

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_is_refused_before_any_content_read(self):
        os.mkfifo(self.path)
        pin = {'path': str(self.path), 'bytes': 128000, 'sha256': '0' * 64}
        for reader in ('attestation', 'release-subject'):
            with self.subTest(reader=reader):
                with self.assertRaisesRegex(ValueError, '^SOURCE_FILE_KIND$'):
                    self.read(reader, pin)
                self.assertFalse(self.marker.exists())
