#!/usr/bin/env python3
"""Original79 complete whole-root copy acquisition; no native authority."""
import hashlib
import importlib.util
import copy
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location('terminology_profile_support', ROOT / 'tests/work-graph-audit-spec-cases.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = 'CONTROLLED_TASK_TERMINOLOGY_INTEGRATION_V1'


class CatalogCases(unittest.TestCase):
    def test_original79_whole_copy_is_explicitly_acquired(self):
        self.assertIn('terminology-integration', Q._FINITE_MODES)
        self.assertEqual(Q._FINITE_MODES['terminology-integration'], PROFILE)
        owner, _ = shared.load('terminology_catalog', ROOT / 'scripts/qualify-work-graph-finite-leaf.py')
        contract = owner.contract_for(PROFILE)
        graph, scope, node = owner.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph['nodes']), node), (117, graph['nodes'][79]))
        self.assertEqual(node['source'], 'bash tests/terminology-integration.test.sh\n')
        self.assertEqual((scope['nodes'], len(scope['omitted_nodes'])), (['COMMAND:tests/terminology-integration.test.sh:0'], 116))
        self.assertEqual(contract['programs'], {
            'tests/terminology-integration.test.sh': 'b35439ef0d21f8c9802a506cddf30dfbbf1258411a7606f4e94f23b89eaf4bb1',
            'scripts/check-terminology-integration.sh': 'dc5269818c3719a7a4c1fcb9ec8bc8076d4edbf37d07a5d3ce60cb73e0e7bc93'})
        for name, pin in contract['programs'].items():
            self.assertEqual(hashlib.sha256(H.input_bytes(name)).hexdigest(), pin)
        wrapper = (ROOT / 'tests/terminology-integration.test.sh').read_text()
        self.assertIn('cp -r . "$t/repo" 2>/dev/null || true', wrapper)
        self.assertEqual(wrapper.count('T=$(make_temp)'), 9)
        self.assertEqual(wrapper.count('rm -rf "$(dirname "$T")"'), 9)
        self.assertIn('whole_copy', contract)
        self.assertEqual(contract['source_modes'], 'COPY_0666_UMASK_022_READ_ONLY_ROOT')


class TerminologyFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        for name, data in {
            self.A.RUNNER: (ROOT / self.A.RUNNER).read_bytes(),
            '.git': b'gitdir: /not-an-original-git-input\n',
            '.hidden': b'captured hidden member\n',
            'docs/research/opaque.bin': b'\xff\x00\xfe\n',
            'eval/ordinary.dat': b'complete copy input\n',
        }.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(0o644)
        (self.source / 'docs/research/empty').mkdir()
        for directory in (self.source, *(p for p in self.source.rglob('*') if p.is_dir())):
            directory.chmod(0o755)

    def session(self, name='evidence', **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))


class AdmissionCases(TerminologyFixture, unittest.TestCase):
    def test_whole_root_bytes_modes_empty_directories_and_git_marker_are_copy_data(self):
        with mock.patch.object(Q.subprocess, 'check_output', side_effect=AssertionError('original79 has no Git observation')):
            state, stamps, objects = self.snapshot()
        actual = {p.relative_to(self.source).as_posix(): p for p in self.source.rglob('*') if p.is_file()}
        self.assertEqual(set(state['files']), set(actual))
        self.assertEqual(self.A.image_subject(state, profile=PROFILE), state['files'])
        for name, path in actual.items():
            self.assertEqual(objects[state['files'][name]['sha256']], path.read_bytes())
            self.assertEqual(state['files'][name]['mode'], path.stat().st_mode & 0o777)
        self.assertIn('docs/research/empty', state['directories'])
        self.assertEqual(state['whole_copy_inputs']['projection']['git'],
            'COPIED_AS_DATA_NO_ORIGINAL_GIT_COMMAND_OR_EXTERNAL_POINTER_DEREFERENCE')
        self.assertEqual(state['whole_copy_inputs'], stamps['whole_copy_inputs'])
        changed = self.source / 'docs/research/opaque.bin'
        changed.write_bytes(changed.read_bytes() + b'changed\n')
        after, after_stamps, _ = self.snapshot()
        self.assertNotEqual(state, after)
        self.assertNotEqual(stamps, after_stamps)

    def test_aliases_nonregular_members_modes_and_actual_directory_modes_refuse(self):
        path = self.source / 'eval/ordinary.dat'
        data = path.read_bytes()
        outside = self.base / 'outside'
        outside.write_bytes(data)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaisesRegex(ValueError, 'single-link'):
            self.snapshot()
        path.unlink()
        os.mkfifo(path)
        with self.assertRaises(ValueError):
            self.snapshot()
        path.unlink()
        path.write_bytes(data)
        path.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'file modes'):
            self.snapshot()
        path.chmod(0o644)
        (self.source / 'docs/research/empty').chmod(0o700)
        with self.assertRaisesRegex(ValueError, 'actual 0755 directories'):
            self.snapshot()

    def test_program_registry_and_runner_mutation_refuse_before_any_runtime(self):
        contract = self.A.contract_for(PROFILE)
        for index, name in enumerate((*contract['programs'], self.A.REGISTRY, self.A.RUNNER)):
            path = self.source / name
            original = path.read_bytes()
            session = self.session('refusal-' + str(index))
            path.write_bytes(original + b'\n')
            try:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'executable|registry|pinned'):
                    session.run()
                self.assertEqual(session.dispatch_count, 0)
                self.assertEqual(session._issued, {})
                self.assertEqual(list(session.output.rglob('dispatch.json')), [])
            finally:
                path.write_bytes(original)

    def test_semantic_failure_stays_original_input_and_is_not_preanswered(self):
        path = self.source / 'skills/implementaudit/templates/THINKING.md'
        path.write_bytes(path.read_bytes() + b'\nUse C4 to map architecture.\n')
        session = self.session()
        with self.assertRaisesRegex(AssertionError, 'runtime acquisition'):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertEqual(list(session.output.rglob('result.json')), [])

    def test_resources_charge_one_complete_peak_and_every_literal_replacement(self):
        target = self.source / 'fixtures/terminology-integration/full-stack-integration.md'
        target.write_bytes(target.read_bytes() + b'\n' + b'Native parent:\n' * 2000)
        population = self.source / 'copy-population'
        population.mkdir()
        for number in range(2100):
            (population / ('member-%04d' % number)).write_bytes(b'x')
        state, _, objects = self.snapshot()
        bounds = state['whole_copy_inputs']['resources']
        name = target.relative_to(self.source).as_posix()
        original = objects[state['files'][name]['sha256']]
        self.assertEqual(bounds['copy_file_sizes'][name], len(original) + 128 + original.count(b'Native parent:') * 7)
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation['copies'], reservation['sequential_copies']), (1, 9))
        self.assertEqual(reservation['peak_copy_files'], len(state['files']) + 1)
        self.assertGreater(reservation['required_bytes'], 256 * 1024**2)
        session = self.session()
        self.assertEqual(session.LIMITS['scratch_bytes'], 512 * 1024**2)
        self.A.require_resource_capacity(reservation, session.LIMITS)
        for ceiling in (32, 256):
            with self.subTest(ceiling=ceiling), self.assertRaisesRegex(ValueError, 'temporary'):
                self.A.require_resource_capacity(reservation, dict(session.LIMITS, scratch_bytes=ceiling * 1024**2))
        over = copy.deepcopy(reservation)
        over['required_bytes'] = session.LIMITS['scratch_bytes'] + 1
        with self.assertRaisesRegex(ValueError, 'temporary'):
            self.A.require_resource_capacity(over, session.LIMITS)


class LiveCases(unittest.TestCase):
    """Two actual original controls, allocated explicitly by the receiver."""
    @classmethod
    def setUpClass(cls):
        if os.environ.get('R0035_TERMINOLOGY_LIVE') != '1':
            raise unittest.SkipTest('set R0035_TERMINOLOGY_LIVE=1 only under a receiving namespace allocation')
        if not os.environ.get('R0035_TERMINOLOGY_EVIDENCE'):
            raise RuntimeError('actual original79 controls require a fresh evidence destination')

    def setUp(self):
        self.base = Path(os.environ['R0035_TERMINOLOGY_EVIDENCE']) / self._testMethodName
        self.base.mkdir(parents=True, exist_ok=False)
        self.source = self.base / 'source'
        shutil.copytree(ROOT, self.source, symlinks=True)
        self.A, _ = shared.load('terminology_live_helper', ROOT / 'scripts/qualify-work-graph-finite-leaf.py')

    def actual(self, session):
        result = session.run()
        directory = Path(result['evidence_directory'])
        receipt = json.loads((directory / 'receipt.json').read_bytes())
        self.assertEqual((directory / 'exit-code.txt').read_bytes(), (str(result['exit']) + '\n').encode())
        self.assertEqual(receipt['node'], 'COMMAND:tests/terminology-integration.test.sh:0')
        self.assertEqual((result['group']['nodes'], len(result['group']['omitted_nodes'])),
                         ([receipt['node']], 116))
        self.assertEqual((result['canonical_acceptance'], result['authority']), ('UNQUALIFIED', 'NONE'))
        return result, (directory / 'stdout.log').read_bytes(), (directory / 'stderr.log').read_bytes()

    def test_actual_original_positive_reuse_and_added_copy_member_refusal(self):
        before = self.A.snapshot_source(P, self.source, {}, profile=PROFILE)
        session = Q.create_finite_leaf_session(self.source, self.base / 'evidence', profile=PROFILE)
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first['exit'], first['complete'], stdout, stderr),
                         (0, True, b'terminology-integration.test: ok (10/10)\n', b''))
        second, out2, err2 = self.actual(session)
        self.assertEqual((first['disposition'], second['disposition'], session.dispatch_count),
                         ('EXECUTED', 'REUSED', 1))
        for name in ('key', 'producer', 'receipt_digest'):
            self.assertEqual(first[name], second[name])
        self.assertEqual((stdout, stderr), (out2, err2))
        self.assertEqual(self.A.snapshot_source(P, self.source, {}, profile=PROFILE), before)
        extra = self.source / '.r0035-added-copy-input'
        self.assertFalse(extra.exists())
        extra.write_bytes(b'\xff\x00new copied bytes\n')
        extra.chmod(0o644)
        with self.assertRaisesRegex(ValueError, 'prior receipt refused'):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_is_retained_without_reuse(self):
        path = self.source / 'skills/implementaudit/templates/THINKING.md'
        path.write_bytes(path.read_bytes() + b'\nUse C4 to map architecture.\n')
        session = Q.create_finite_leaf_session(self.source, self.base / 'evidence', profile=PROFILE)
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result['exit'], result['complete'], stdout), (1, True, b''))
        self.assertEqual(stderr,
            b'FAIL: check-terminology-integration.sh should pass on current repo\n'
            b'terminology-integration.test: FAIL (9/10 passed)\n')
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, 'failed or interrupted'):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == '__main__':
    unittest.main()
