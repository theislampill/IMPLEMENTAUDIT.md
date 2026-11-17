#!/usr/bin/env python3
"""Strict C02 receiving in disposable Git subjects; fixture grants are not authority.

Only the existing fixture source locator is substituted. The real claim-owned
append/CAS/fresh-generation/receipt/marker, paired reader and native validator
execute unchanged. No native host, historical event or production issuer is
qualified by these constructed stimuli.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

import canonical_reader_test as reader_tests
import c02_publication_test as correction_tests

ROOT = reader_tests.ROOT
SCRIPTS = ROOT / 'skills/implementaudit/scripts'
CONTROLLER = reader_tests.CONTROLLER
BOUNDARY = 'erroneous-invalidation-correction'


class CorrectionReaders(unittest.TestCase):
    git = reader_tests.CanonicalReaderTests.git
    write_phase = reader_tests.CanonicalReaderTests.write_phase
    make_real_generation = reader_tests.CanonicalReaderTests.make_real_generation
    load_reader = reader_tests.CanonicalReaderTests.load_reader
    digest = correction_tests.CorrectionPublication.digest
    write_source = correction_tests.CorrectionPublication.write_source
    write_grant = correction_tests.CorrectionPublication.write_grant
    resolver = correction_tests.CorrectionPublication.resolver
    fixture_owner = correction_tests.CorrectionPublication.fixture_owner
    refs = correction_tests.CorrectionPublication.refs
    prepare = correction_tests.CorrectionPublication.prepare
    publish = correction_tests.CorrectionPublication.publish
    required = correction_tests.CorrectionPublication.required
    fresh_grant = correction_tests.FreshCorrection.fresh_grant
    transition = correction_tests.FreshCorrection.transition

    def setUp(self):
        self.stage_timings = []
        evidence = os.environ.get('R0039_C02_READER_EVIDENCE')
        if evidence:
            Path(evidence).mkdir(parents=True, exist_ok=True)
        if getattr(self, 'persistent_repo', None) is not None:
            self.repo = Path(self.persistent_repo).absolute()
            self.repo.mkdir(parents=True, exist_ok=False)
        else:
            self.temporary = tempfile.TemporaryDirectory(prefix='c02-reader-', dir=evidence)
            self.addCleanup(self.temporary.cleanup)
            self.repo = Path(self.temporary.name)
        self.scripts = self.repo / 'skills/implementaudit/scripts'
        source = Path(os.environ.get('R0039_C02_READER_FROZEN_SCRIPTS', SCRIPTS))
        shutil.copytree(source, self.scripts)
        # Optional frozen peers isolate a concurrent source writer. Only this
        # lane's exact reader/validator under test overlay the copied peer set.
        for name in ('read-canonical-pair.py', 'validate-run-root.sh'):
            shutil.copyfile(SCRIPTS / name, self.scripts / name)
        shutil.copytree(ROOT / 'skills/implementaudit/templates', self.scripts.parent / 'templates')
        self.git('init', '-q')
        self.git('config', 'user.name', 'constructed C02 reader')
        self.git('config', 'user.email', 'c02-reader@example.invalid')
        (self.repo / 'fixture.txt').write_text('Constructed C02 receiving subject.\n')
        self.git('add', 'fixture.txt')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'constructed C02 subject')
        claimed = self.claim('--controller', CONTROLLER, 'C02 canonical receiving')
        self.assertEqual(claimed.returncode, 0, claimed.stderr.decode())
        self.run = self.repo / claimed.stdout.decode().strip()
        for name in ('STATE.md', 'ROADMAP.md', 'PROTOCOL.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md'):
            shutil.copyfile(self.scripts.parent / 'templates' / name, self.run / name)
        (self.run / 'phases').mkdir()
        (self.run / 'phases/phase-1.md').write_text('open constructed phase\n')
        self.output = self.repo / 'read-output'
        self.output.mkdir()
        spec = importlib.util.spec_from_file_location('c02_reader_claim_' + self.repo.name.replace('-', '_'),
                                                     self.scripts / 'claim-run-rotation.py')
        self.owner = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.owner
        spec.loader.exec_module(self.owner)
        self.addCleanup(sys.modules.pop, spec.name, None)
        directory = contextlib.chdir(self.repo)
        directory.__enter__()
        self.addCleanup(directory.__exit__, None, None, None)
        self.context = self.owner.discover(CONTROLLER)
        self.fixture = types.SimpleNamespace(repo=self.repo, scripts=self.scripts, run_root=self.run,
            claim=self.claim, blob=lambda raw: self.git('hash-object', '-w', '--stdin', data=raw),
            git=self.git)
        self.helper_hashes = {name: hashlib.sha256((self.scripts / name).read_bytes()).hexdigest()
            for name in ('claim-run.sh', 'claim-run-rotation.py', 'rotate-canonical-state.py',
                         'canonical_hot_projection.py', 'read-canonical-pair.py', 'validate-run-root.sh')}

    def rotate(self):
        return self.make_real_generation(native=True)

    def record_stage(self, name, started):
        record = {'stage': name, 'elapsed_ms': (time.perf_counter() - started) * 1000,
                  'root_pid': os.getpid(), 'scope': 'functional diagnostic wall time; not whole-job memory qualification'}
        self.stage_timings.append(record)
        evidence = os.environ.get('R0039_C02_READER_EVIDENCE')
        if evidence:
            population = {role: {'bytes': (self.run / (role + '.md')).stat().st_size,
                                'sha256': hashlib.sha256((self.run / (role + '.md')).read_bytes()).hexdigest()}
                          for role in ('STATE', 'ROADMAP')}
            Path(evidence, 'STAGES_' + str(os.getpid()) + '.json').write_text(json.dumps({
                'helper_sha256': getattr(self, 'helper_hashes', {}), 'stages': self.stage_timings,
                'root_pair_population': population, 'descendant_memory_accounting': 'NOT_MEASURED',
                'scope': 'constructed native-template C02 reader controls'}, indent=2) + '\n')

    def timed(self, name, function):
        started = time.perf_counter()
        try:
            return function()
        finally:
            self.record_stage(name, started)

    def claim(self, *args):
        operation = lambda: reader_tests.CanonicalReaderTests.claim(self, *args)
        if args[0] == '--rotate-canonical-state':
            return self.timed('initial_byte_rotation_full_claim_invocation', operation)
        return operation()

    def read(self, *args):
        return reader_tests.command([sys.executable, '-B', Path(__file__).resolve(), '--observe-reader',
            self.scripts / 'read-canonical-pair.py', self.run, self.output,
            self.repo / 'reader-observations.json', *args], self.repo)

    def validate(self):
        # Bash's dirname/glob comparisons need one consistent separator spelling.
        # This is the same physical run; Python custody still verifies the path.
        return reader_tests.command(['bash', (self.scripts / 'validate-run-root.sh').as_posix(),
                                     self.run.as_posix()], self.repo)

    def correct(self):
        with mock.patch.object(correction_tests, 'CONTROLLER', CONTROLLER):
            correction_tests.CorrectionPublication.seed_correction(self)
        with self.fixture_owner():
            prepared = self.timed('c02_adjudication_preparation', self.prepare)
            appended = self.timed('c02_append_only_publication', lambda: self.publish(prepared))
        self.correction_oid = appended['record_oid']
        self.correction = self.owner.decode_json(self.owner.read_blob(self.repo, self.correction_oid))
        self.fresh_grant()
        with self.fixture_owner():
            result = self.timed('c02_fresh_transition_full_owner_call', self.transition)
        self.assertEqual(result['status'], 'CORRECTED_FRESH')
        resolved = self.timed('c02_current_generation_resolution',
                              lambda: self.claim('--resolve-canonical-generation', CONTROLLER))
        self.assertEqual(resolved.returncode, 0, resolved.stderr.decode())
        return json.loads(resolved.stdout)

    def test_fresh_c02_pair_keeps_separate_reads_and_native_validation(self):
        resolved = self.correct()
        self.assertEqual(resolved['pointer']['continuity_epoch'], 'G0003')
        self.assertEqual(resolved['marker_oid'], self.joined['marker_oid'])
        receipt = self.owner.read_blob(self.repo, resolved['receipt_token'].split('@')[1])
        self.assertEqual(len(receipt.rstrip(b'\n').split(b'\t')), 14)
        before_refs = self.refs()
        original_roots = {role: (self.run / (role + '.md')).read_bytes() for role in ('STATE', 'ROADMAP')}
        pair = {}
        for role in ('STATE', 'ROADMAP'):
            read = self.claim('--read-canonical-state', CONTROLLER, '--role', role,
                              '--expected-pointer', resolved['pointer_token'])
            self.assertEqual(read.returncode, 0, read.stderr.decode())
            self.assertEqual(hashlib.sha256(read.stdout).hexdigest(), resolved['pointer'][role.lower() + '_sha256'])
            pair[role + '.md'] = read.stdout
        # Execute both pathways before asserting, retaining both baseline REDs.
        materialized = self.timed('c02_native_guard_pair_materialization', lambda: self.read('--native-guards'))
        validated = self.timed('c02_native_run_root_validation', self.validate)
        for name, result in (('reader', materialized), ('validator', validated)):
            with self.subTest(pathway=name):
                self.assertEqual(result.returncode, 0, result.stderr.decode())
        observations = json.loads((self.repo / 'reader-observations.json').read_bytes())
        read_calls = [entry for entry in observations if entry['arguments'][0] == '--read-canonical-state']
        self.assertEqual([entry['arguments'][3] for entry in read_calls], ['STATE', 'ROADMAP'])
        self.assertTrue(all(entry['exit'] == 0 for entry in read_calls))
        self.assertTrue(all(entry['arguments'][5] == resolved['pointer_token'] for entry in read_calls))
        if materialized.returncode == 0:
            for role in ('STATE', 'ROADMAP'):
                self.assertEqual((self.output / (role + '.md')).read_bytes(), pair[role + '.md'])
                self.assertEqual((self.run / (role + '.md')).read_bytes(), original_roots[role])
            native = (self.output / 'native-STATE.md').read_text(encoding='utf-8')
            self.assertIn('| G0003 | ' + BOUNDARY + ' |', native)
            self.assertIn('| yes | native pointer JOIN |', native)
            self.assertTrue(native.endswith(self.native_source['STATE']))
            self.assertEqual((self.output / 'native-ROADMAP.md').read_text(encoding='utf-8'), self.native_source['ROADMAP'])
            reread = self.read('--native-guards', '--verify-current')
            self.assertEqual(reread.returncode, 0, reread.stderr.decode())
        self.assertEqual(self.refs(), before_refs)
        adapter = self.load_reader()
        bodies = {role: json.loads(pair[role + '.md'].splitlines()[16]) for role in ('STATE', 'ROADMAP')}
        for changes in ({'schema_version': 'implementaudit.native-resume-transition.v1'},
                        {'transition_kind': 'native-resume'}, {'boundary': 'manual-resume'},
                        {'schema_version': 'implementaudit.canonical-state-transition.v2'},
                        {'failed_transition_epoch': 'G0002'}, {'boundary': 'foreign-correction'}):
            changed_pair = {}
            for role in ('STATE', 'ROADMAP'):
                changed = copy.deepcopy(bodies[role])
                changed['transition'].update(changes)
                lines = pair[role + '.md'].split(b'\n')
                lines[16] = self.owner.canonical(changed)
                changed_pair[role + '.md'] = b'\n'.join(lines)
            with self.subTest(malformed=changes), self.assertRaises(adapter.ReaderError):
                adapter.native_guard_views(self.run, changed_pair, resolved)
        wrong_resolution = copy.deepcopy(resolved)
        wrong_resolution['pointer']['invalidation_oid'] = '9' * 40
        with self.assertRaises(adapter.ReaderError):
            adapter.native_guard_views(self.run, pair, wrong_resolution)
        for command in (('--invalidate-continuity', CONTROLLER, '--boundary', BOUNDARY, '--event', 'forged-native-c02'),
                        ('--resume-controller', CONTROLLER, '--boundary', BOUNDARY, '--epoch', 'G0004')):
            with self.subTest(private_boundary=command[0]):
                self.assertNotEqual(self.claim(*command).returncode, 0)
                self.assertEqual(self.refs(), before_refs)
        if os.environ.get('R0039_C02_READER_EVIDENCE'):
            output = Path(os.environ['R0039_C02_READER_EVIDENCE']) / 'LAST_SOURCE_READBACK.json'
            output.write_text(json.dumps({'scope': 'constructed C02 only; no production entitlement',
                'helper_sha256': self.helper_hashes, 'reader_exit': materialized.returncode,
                'validator_exit': validated.returncode, 'receipt_fields': 14,
                'state_then_roadmap': True, 'refs_unchanged': self.refs() == before_refs}, indent=2) + '\n')

    def test_legacy_private_correction_boundary_never_gains_admission(self):
        baseline = self.validate()
        self.assertEqual(baseline.returncode, 0, baseline.stderr.decode())
        path = self.run / 'STATE.md'
        original = path.read_text(encoding='utf-8')
        for epoch in ('G0001', 'G0002'):
            text = original.replace('## Context epochs and instruction applicability\n',
                '## Context epochs and instruction applicability\n\n'
                '| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n'
                '|---|---|---|---|---|---|\n'
                '| ' + epoch + ' | ' + BOUNDARY + ' | not measured | fixture | yes | native pointer JOIN |\n')
            path.write_text(text, encoding='utf-8')
            result = self.validate()
            with self.subTest(epoch=epoch):
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b'invalid boundary provenance', result.stderr)
        path.write_text(original, encoding='utf-8')


def observed_reader(arguments):
    """Fresh-process witness of actual owner calls; none are substituted."""
    path, run, output, log, *flags = arguments
    spec = importlib.util.spec_from_file_location('observed_c02_reader', path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    original, calls = reader.owner, []
    def observe(cwd, *arguments):
        result = original(cwd, *arguments)
        calls.append({'arguments': arguments, 'exit': result.returncode})
        return result
    reader.owner = observe
    sys.argv = [path, '--run-root', run, '--output', output, *flags]
    try:
        return reader.main()
    finally:
        Path(log).write_text(json.dumps(calls) + '\n')


if __name__ == '__main__':
    if len(sys.argv) >= 6 and sys.argv[1] == '--observe-reader':
        raise SystemExit(observed_reader(sys.argv[2:]))
    unittest.main()
