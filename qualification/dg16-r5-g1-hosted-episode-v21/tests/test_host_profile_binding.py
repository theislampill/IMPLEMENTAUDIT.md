"""Offline behavior controls; every policy below is synthetic and long expired.

No Root policy is issued by this file. The positive fixture supplies a test-only
pin and a fake 1970 clock. The real policy is independently pinned; fixtures never issue it. Actual hosted
facts are replaced only at the environment/observation boundary; the maintained
selector, binding validator, raw reader and file writer are real C code.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
OP = ROOT
SOURCE = '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d'
TREE = '53498df783ed441744ae5080982c2d5e59c34bbc'
BRANCH = 'engineering/pro-dg16-g1-v21-diagnostic-20261125-02'
BOOT = b'11111111-2222-3333-4444-555555555555\n'
OTHER_BOOT = b'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n'
PROFILE = 'G1_UBUNTU24_20261111_127_1'
HOST_PIN = '75b1aaf71995b95201529a9fc62cc2d59398674fb3733f1b9066f6a18a53f781'


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def pin(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProfileBinding(unittest.TestCase):
    def setUp(self):
        candidate = OP / 'entry/host_profile_binding.py'
        self.assertTrue(candidate.is_file(), 'D4 producer is not implemented yet')
        self.subject = load(candidate, 'd4_candidate')
        raw = (OP / 'packet/host_utility.py').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), HOST_PIN)
        self.owner = load(OP / 'packet/host_utility.py', 'd4_exact_c_host_utility')
        self.core = load(OP / 'packet/run.py', 'd4_exact_c_run')
        self.temp = tempfile.TemporaryDirectory(prefix='d4-offline-', dir=ROOT / 'tests')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = self.root / 'packet'
        (self.packet / 'public-inputs').mkdir(parents=True)
        self.entry = self.root / 'entry'; self.entry.mkdir()
        self.policy_path = self.entry / 'G1_HOST_PROFILE_POLICY.json'
        self.source = self.root / 'source'
        self.output = self.root / 'output'
        self.workspace = self.root / 'workspace'; self.workspace.mkdir()
        self.runner_temp = self.root / 'runner-temp'; self.runner_temp.mkdir()
        self.context = dict(repository='theislampill/IMPLEMENTAUDIT.md', branch=BRANCH,
            run_id='123456789', run_attempt=1, workflow_commit='1' * 40,
            workspace=str(self.workspace), runner_temp=str(self.runner_temp))
        self.operation = dict(repository=self.context['repository'], branch=BRANCH,
            workflow_path='.github/workflows/dg16-g1-v21-offline-fixture.yml', job_name='g1', run_attempt=1)
        self.env = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
            GITHUB_REPOSITORY=self.context['repository'], GITHUB_REF='refs/heads/' + BRANCH,
            GITHUB_RUN_ID=self.context['run_id'], GITHUB_RUN_ATTEMPT='1', GITHUB_SHA='1' * 40,
            GITHUB_JOB='g1', GITHUB_WORKFLOW_SHA='1' * 40,
            GITHUB_WORKFLOW_REF=self.context['repository'] + '/' + self.operation['workflow_path'] + '@refs/heads/' + BRANCH,
            GITHUB_WORKSPACE=str(self.workspace), RUNNER_TEMP=str(self.runner_temp))
        facts = dict(platform='linux', architecture='x86_64', os={'ID': 'ubuntu', 'VERSION_ID': '24.04'},
            python_version=[3, 12, 3], image_os='ubuntu24', image_version='20261111.127.1', uid=0, euid=0, gid=0, egid=0)
        self.profile = self.owner.select_g1_host_profile(facts)
        self.policy = dict(schema='dg16.g1-prospective-host-profile-policy.v2', issuer='R5_ROOT_GOVERNOR',
            successor='CHATGPT-PRO-DG16, owner-appointed successor 2026-11-25',
            decision='ADOPT_FINITE_EXACT_PROFILES_CONDITIONALLY', semantics='PROSPECTIVE_PROFILE_MATCH_BEFORE_PREPARE',
            source_commit=SOURCE, source_tree=TREE, operation=self.operation,
            finite_host_policy_sha256=self.owner.g1_host_policy_sha256(), profile_ids=[PROFILE],
            issued_unix_ms=1000, expires_unix_ms=2000, core_or_native_effect_grant=False, original_awards=[])
        self.raw = wire(self.policy)
        self.write_policy(self.raw)
        self.env_patch = mock.patch.dict(os.environ, self.env, clear=True)
        self.env_patch.start(); self.addCleanup(self.env_patch.stop)
        self.patches = [
            mock.patch.object(self.core, 'host_context', side_effect=lambda output, source: copy.deepcopy(self.context)),
            mock.patch.object(self.core, 'read_boot_identity', return_value=BOOT),
            mock.patch.object(self.core, 'load_module', side_effect=lambda name: self.owner if name == 'host_utility' else self.fail('unexpected module load')),
            mock.patch.object(self.owner, 'observe_g1_host_profile', side_effect=lambda: copy.deepcopy(self.profile)),
            mock.patch.object(self.subject.time, 'time', return_value=1.5),
        ]
        for patch in self.patches:
            patch.start(); self.addCleanup(patch.stop)

    def write_policy(self, raw):
        self.policy_path.write_bytes(raw)

    def prepare(self, trusted_pin='fixture'):
        selected = pin(self.raw) if trusted_pin == 'fixture' else trusted_pin
        try:
            return self.subject.prepare(self.core, self.source, self.output, root_policy_pin=selected,
                read_policy=lambda: self.core.read_regular(self.policy_path, 65536))
        except TypeError as exc:
            self.fail('External pinned entry policy interface is not implemented: ' + str(exc))

    def refuse(self, code, trusted_pin='fixture'):
        with self.assertRaisesRegex(ValueError, '^' + code + '$'):
            self.prepare(trusted_pin)
        self.assertFalse(self.output.exists())

    def replace_policy(self, change):
        change(self.policy); self.raw = wire(self.policy); self.write_policy(self.raw)

    def test_unissued_policy_cannot_be_enabled_by_self_describing_body(self):
        # Removing the independently trusted pin guard would admit this file.
        self.refuse('PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE', None)

    def test_unissued_policy_refuses_before_any_host_observation(self):
        # Late checking could inspect/use a host before the required authority.
        with mock.patch.object(self.core, 'load_module', side_effect=AssertionError('host use before policy')):
            self.refuse('PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE', None)

    def test_missing_policy_body_refuses(self):
        self.policy_path.unlink()
        self.refuse('D4_POLICY_BODY_UNAVAILABLE')

    def test_tampered_body_is_rejected_under_the_real_pinned_descriptor(self):
        self.write_policy(self.raw + b' ')
        self.refuse('D4_POLICY_PIN')

    def test_duplicate_keys_cannot_hide_a_second_issuer(self):
        self.raw = self.raw.replace(b'{', b'{"issuer":"FORGED",', 1)
        self.write_policy(self.raw)
        self.refuse('D4_POLICY_JSON')

    def test_repinned_wrong_authority_and_scope_refuse(self):
        # Even a transport-authenticated body cannot widen its semantic scope.
        cases = [('issuer', 'AUTHOR', 'D4_POLICY_SCOPE'),
                 ('decision', 'ADOPT_FIXED_SAME_HOST_TOOL_BODIES', 'D4_POLICY_SCOPE'),
                 ('source_commit', 'e' * 40, 'D4_POLICY_SOURCE'),
                 ('source_tree', 'f' * 40, 'D4_POLICY_SOURCE'),
                 ('core_or_native_effect_grant', True, 'D4_POLICY_SCOPE'),
                 ('original_awards', ['G1'], 'D4_POLICY_SCOPE'),
                 ('finite_host_policy_sha256', '0' * 64, 'D4_POLICY_PROFILE')]
        original = copy.deepcopy(self.policy)
        for key, value, code in cases:
            with self.subTest(key=key):
                self.policy = copy.deepcopy(original)
                self.replace_policy(lambda p: p.update({key: value}))
                self.refuse(code)

    def test_expired_and_future_policy_refuse_at_prepare(self):
        for issued, expires in ((1000, 1500), (1501, 2000)):
            with self.subTest(issued=issued, expires=expires):
                self.replace_policy(lambda p: p.update(issued_unix_ms=issued, expires_unix_ms=expires))
                self.refuse('D4_POLICY_TIME')

    def test_wrong_workflow_job_or_branch_refuses(self):
        original = copy.deepcopy(self.policy)
        for field, value in (('branch', 'engineering/other'), ('job_name', 'other'),
                             ('workflow_path', '.github/workflows/other.yml'), ('run_attempt', 2)):
            with self.subTest(field=field):
                self.policy = copy.deepcopy(original)
                self.replace_policy(lambda p: p['operation'].update({field: value}))
                self.refuse('D4_POLICY_OPERATION')

    def test_other_valid_finite_row_is_not_the_root_selected_profile(self):
        other = copy.deepcopy(self.profile['facts']); other['image_version'] = '20261111.370.1'
        self.profile = self.owner.select_g1_host_profile(other)
        self.refuse('D4_PROFILE_NOT_ADOPTED')

    def test_finite_policy_allows_either_exact_named_profile(self):
        ids=['G1_UBUNTU24_20261116_133_1','G1_UBUNTU24_20261116_376_1','G1_UBUNTU24_20261122_23_1']
        self.replace_policy(lambda p:p.update(profile_ids=ids))
        for image in ('20261116.133.1','20261116.376.1','20261122.23.1'):
            with self.subTest(image=image):
                facts=copy.deepcopy(self.profile['facts']);facts['image_version']=image
                self.profile=self.owner.select_g1_host_profile(facts)
                received=self.prepare()
                self.assertEqual(received['binding']['host_profile'],self.profile)
                self.assertFalse(self.output.exists())

    def test_finite_policy_refuses_empty_duplicate_unknown_and_wrong_type(self):
        for ids in ([],[PROFILE,PROFILE],['NO_SUCH_PROFILE'],PROFILE,[False]):
            with self.subTest(ids=ids):
                self.replace_policy(lambda p:p.update(profile_ids=ids))
                self.refuse('D4_POLICY_PROFILE')

    def test_positive_returns_actual_bodies_and_passes_unchanged_c_validator(self):
        result = self.prepare()
        binding = result['binding']; evidence = result['evidence']
        self.assertEqual(set(evidence), {'observation', 'adoption'})
        observation = json.loads(evidence['observation'])
        self.assertEqual(observation['schema'], 'dg16.g1-prospective-host-profile-observation.v1')
        self.assertEqual(observation['semantics'], 'LIVE_MATCH_TO_PREISSUED_ROOT_POLICY')
        self.assertEqual(observation['authority'], 'NONE')
        self.assertEqual(observation['context']['run_id'], '123456789')
        self.assertEqual(observation['host_identity']['boot_id'], BOOT.decode().strip())
        self.assertEqual(observation['host_profile']['profile_id'], PROFILE)
        self.assertEqual(evidence['adoption'], self.raw)
        self.assertEqual(binding['observation'], pin(evidence['observation']))
        self.assertEqual(binding['adoption'], pin(self.raw))
        self.assertEqual(binding['host_profile']['native_qualification'], False)
        self.assertEqual(binding['host_profile']['original_awards'], [])
        self.owner.validate_g1_profile_binding(binding, self.context, SOURCE, TREE,
            self.profile, hashlib.sha256(BOOT).hexdigest())
        self.assertFalse(self.output.exists())

    def test_binding_cannot_be_replayed_as_another_run_or_boot(self):
        binding = self.prepare()['binding']
        wrong = dict(self.context, run_id='987654321')
        with self.assertRaisesRegex(ValueError, 'HOST_PROFILE_CHANGED'):
            self.owner.validate_g1_profile_binding(binding, wrong, SOURCE, TREE,
                self.profile, hashlib.sha256(BOOT).hexdigest())
        with self.assertRaisesRegex(ValueError, 'HOST_PROFILE_CHANGED'):
            self.owner.validate_g1_profile_binding(binding, self.context, SOURCE, TREE,
                self.profile, hashlib.sha256(OTHER_BOOT).hexdigest())

    def test_boot_changes_during_observation_refuse(self):
        with mock.patch.object(self.core, 'read_boot_identity', side_effect=[BOOT, OTHER_BOOT]):
            self.refuse('D4_LIVE_OBSERVATION_CHANGED')

    def test_context_changes_during_observation_refuse(self):
        with mock.patch.object(self.core, 'host_context', side_effect=[self.context, dict(self.context, run_id='222222222')]):
            self.refuse('D4_LIVE_OBSERVATION_CHANGED')

    def test_profile_changes_during_observation_refuse(self):
        other = copy.deepcopy(self.profile['facts']); other['image_version'] = '20261111.370.1'
        with mock.patch.object(self.owner, 'observe_g1_host_profile', side_effect=[self.profile, self.owner.select_g1_host_profile(other)]):
            self.refuse('D4_LIVE_OBSERVATION_CHANGED')

    def test_policy_expiry_during_observation_refuses(self):
        with mock.patch.object(self.subject.time, 'time', side_effect=[1.5, 2.0]):
            self.refuse('D4_POLICY_TIME')

    def test_policy_body_changed_between_observations_refuses(self):
        real = self.core.read_regular
        calls = 0
        def changing(path, limit):
            nonlocal calls
            calls += 1
            return real(path, limit) if calls == 1 else real(path, limit) + b' '
        with mock.patch.object(self.core, 'read_regular', side_effect=changing):
            self.refuse('D4_POLICY_BODY_CHANGED')

    def test_external_entry_policy_needs_no_new_packet_member(self):
        result = self.prepare()
        self.assertEqual(result['evidence']['adoption'], self.raw)
        self.assertEqual(list((self.packet / 'public-inputs').iterdir()), [])

    def proposed_core(self):
        path = OP / 'packet/run.py'
        self.assertTrue(path.is_file(), 'Prepare evidence integration is not implemented yet')
        return load(path, 'd4_candidate_core')

    def core_boundary(self, new, on_stage):
        # External composition/admission is outside this local fixture. Execution
        # stops at the existing staging boundary, before subreaper/setup/clone.
        selector = types.SimpleNamespace(admit=lambda _: None)
        composition = types.SimpleNamespace(require_launch=lambda *a, **k: {})
        modules = {'host_utility': self.owner, 'public_inputs': selector, 'host_composition': composition,
                   'g3_receiving': types.SimpleNamespace()}
        return [mock.patch.object(new, 'require_complete_packet', return_value=None),
                mock.patch.object(new, 'load_module', side_effect=lambda name: modules[name]),
                mock.patch.object(new, 'host_context', return_value=copy.deepcopy(self.context)),
                mock.patch.object(new, 'read_boot_identity', return_value=BOOT),
                mock.patch.object(new, 'stage_received_inputs', side_effect=on_stage)]

    def test_raw_evidence_retained_in_existing_state_before_staging(self):
        result = self.prepare(); new = self.proposed_core()
        class ReachedStaging(Exception):
            pass
        def stage(output, approved):
            state = json.loads((output / 'private/episode.json').read_bytes())
            for name, body in result['evidence'].items():
                self.assertEqual(state['host_profile_evidence'][name].encode('ascii'), body)
                self.assertEqual(state['host_profile_binding'][name], pin(body))
            self.assertEqual(sorted(p.name for p in (output / 'private').iterdir()), ['episode.json'])
            self.assertFalse(self.source.exists())
            raise ReachedStaging
        patches = self.core_boundary(new, stage)
        for p in patches: p.start(); self.addCleanup(p.stop)
        with self.assertRaises(ReachedStaging):
            new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'],
                        host_profile_evidence=result['evidence'])

    def test_mismatched_raw_evidence_refuses_before_output_creation(self):
        result = self.prepare(); new = self.proposed_core()
        result['evidence']['observation'] += b' '
        for p in self.core_boundary(new, AssertionError('staging must not run')):
            p.start(); self.addCleanup(p.stop)
        with self.assertRaisesRegex(ValueError, 'D4_EVIDENCE_BINDING'):
            new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'],
                        host_profile_evidence=result['evidence'])
        self.assertFalse(self.output.exists())

    def test_missing_raw_evidence_refuses_before_output_creation(self):
        result = self.prepare(); new = self.proposed_core()
        for p in self.core_boundary(new, AssertionError('staging must not run')):
            p.start(); self.addCleanup(p.stop)
        with self.assertRaisesRegex(ValueError, 'D4_EVIDENCE_REQUIRED'):
            new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'])
        self.assertFalse(self.output.exists())

    def test_policy_expiry_between_producer_and_core_effect_refuses(self):
        result = self.prepare(); new = self.proposed_core()
        for p in self.core_boundary(new, AssertionError('expired policy must not stage')):
            p.start(); self.addCleanup(p.stop)
        with mock.patch.object(new.time, 'time', return_value=2.0):
            with self.assertRaisesRegex(ValueError, '^D4_EVIDENCE_TIME$'):
                new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'],
                            host_profile_evidence=result['evidence'])
        self.assertFalse(self.output.exists())

    def test_observation_cannot_be_from_after_the_core_effect_boundary(self):
        result = self.prepare(); new = self.proposed_core()
        for p in self.core_boundary(new, AssertionError('clock reversal must not stage')):
            p.start(); self.addCleanup(p.stop)
        with mock.patch.object(new.time, 'time', return_value=1.49):
            with self.assertRaisesRegex(ValueError, '^D4_EVIDENCE_TIME$'):
                new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'],
                            host_profile_evidence=result['evidence'])
        self.assertFalse(self.output.exists())

    def test_raw_legacy_adoption_cannot_be_relabelled_as_prospective_evidence(self):
        result = self.prepare(); new = self.proposed_core()
        policy = json.loads(result['evidence']['adoption'])
        policy['schema'] = 'dg16.g1-same-host-tool-adoption.v1'
        result['evidence']['adoption'] = wire(policy)
        result['binding']['adoption'] = pin(result['evidence']['adoption'])
        observation = json.loads(result['evidence']['observation'])
        observation['root_policy'] = result['binding']['adoption']
        result['evidence']['observation'] = wire(observation)
        result['binding']['observation'] = pin(result['evidence']['observation'])
        for p in self.core_boundary(new, AssertionError('legacy semantics must not stage')):
            p.start(); self.addCleanup(p.stop)
        with self.assertRaisesRegex(ValueError, '^D4_EVIDENCE_SCOPE$'):
            new.execute('prepare', self.source, self.output, host_profile_binding=result['binding'],
                        host_profile_evidence=result['evidence'])
        self.assertFalse(self.output.exists())

    def test_external_entry_rejects_non_root_custody(self):
        entry = load(OP / 'entry/core_prepare_entry.py', 'd4_candidate_entry_custody')
        info = self.policy_path.lstat()
        # The runner is not root. If run elsewhere, alter only the recorded
        # owner for this negative control; the inherited entry reader is real.
        nonroot = types.SimpleNamespace(st_mode=info.st_mode, st_nlink=info.st_nlink,
                                       st_size=info.st_size, st_uid=1000)
        with mock.patch.object(Path, 'lstat', return_value=nonroot):
            with self.assertRaisesRegex(ValueError, '^PREPARE_FILE_CUSTODY$'):
                entry.read(self.policy_path, 65536, pin(self.raw)['sha256'])

    def test_existing_entry_stays_refused_without_issued_policy_even_if_files_exist(self):
        path = OP / 'entry/core_prepare_entry.py'
        self.assertTrue(path.is_file(), 'Conditional entry integration is not implemented yet')
        entry = load(path, 'd4_candidate_entry')
        with mock.patch.object(entry, 'ROOT_POLICY_PIN', None), mock.patch.object(entry, 'read', side_effect=AssertionError('unissued policy cannot read or execute code')):
            with self.assertRaisesRegex(ValueError, '^PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE$'):
                entry.prepare_core(self.packet)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
