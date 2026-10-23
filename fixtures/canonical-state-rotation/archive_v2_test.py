#!/usr/bin/env python3
"""Real Git/filesystem archive controls; native currentness is tested separately."""
from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = load('rotation_archive_under_test', ROOT / 'skills/implementaudit/scripts/rotate-canonical-state.py')
F = load('rotation_archive_fixture', HERE / 'protected_projection_v2_test.py')


def git(repo, *args, data=None):
    result = subprocess.run(['git', '-C', str(repo), *args], input=data,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise AssertionError((args, result.returncode, result.stderr.decode()))
    return result.stdout


def make_subject(repo: Path, *, large=True):
    repo.mkdir()
    git(repo, 'init', '-q')
    bodies = F.fixture_bodies()
    if large:
        bodies['STATE']['history'][0]['payload']['text'] = 'Exact retained historical narrative.\n' * 5000
    state, roadmap, owners, artifacts = F.fixture_pair(bodies)
    identity = bodies['STATE']['payload']['identity']['value']
    run = repo / identity['run_root_identity']
    run.mkdir(parents=True)
    (run / 'STATE.md').write_bytes(state)
    (run / 'ROADMAP.md').write_bytes(roadmap)
    receipt_ref = bodies['STATE']['continuity']['expected_receipt_ref']
    receipt_oid = git(repo, 'hash-object', '-w', '--stdin', data=artifacts['receipt']).decode().strip()
    git(repo, 'update-ref', receipt_ref, receipt_oid, '0' * 40)
    for role in ('STATE', 'ROADMAP'):
        for declaration in bodies[role]['artifact_refs']:
            if declaration['role'] == 'CONTINUITY_RECEIPT':
                continue
            path = run / declaration['locator']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(artifacts[declaration['artifact_id']])
    owner_map = run / 'rotation-owner-map.json'
    owner_map.write_bytes(M.canonical_bytes({'schema': 'implementaudit.rotation-owner-map.v2', 'owner_map': owners}))
    predecessor = {
        'controller': identity['controller_id'], 'claim_id': identity['claim_id'],
        'run_root_identity': identity['run_root_identity'], 'controller_oid': 'e' * 40,
        'receipt_ref': receipt_ref, 'receipt_oid': receipt_oid,
        'receipt_schema': 'implementaudit.continuity-receipt.v2',
        'continuity_epoch': 'G0001', 'projection_generation_id': 'G0001',
        'invalidation_oid': bodies['STATE']['continuity']['invalidation_oid'],
        'pointer_ref': 'refs/implementaudit/current-generations/' + identity['controller_id'],
        'pointer_oid': None, 'migration_marker_oid': None,
        'head': identity['candidate'], 'tree': identity['tree'],
        'exact_next_action': bodies['STATE']['payload']['continuation']['value']['next_action'],
        'state_sha256': M.sha256(state), 'roadmap_sha256': M.sha256(roadmap),
        'state_path': identity['run_root_identity'] + '/STATE.md',
        'roadmap_path': identity['run_root_identity'] + '/ROADMAP.md',
    }
    return {'repo': repo, 'run': run, 'predecessor': predecessor, 'owner_map': owner_map,
            'source': (state, roadmap), 'artifacts': artifacts}


def prepare(subject):
    return M.prepare_canonical_draft(subject['repo'], subject['run'],
                subject['predecessor']['controller'], 'G0002', subject['owner_map'],
                subject['predecessor'], M.calibration_contract_v1())


def transition(subject, prepared, *, recovery=False):
    predecessor = subject['predecessor']
    oid = git(subject['repo'], 'hash-object', '-w', '--stdin',
              data=('Constructed exact rotation invalidation ' + str(recovery)).encode()).decode().strip()
    epoch = 'G0003' if recovery else 'G0002'
    return {'schema': 'implementaudit.rotation-transition.v1',
            'controller': predecessor['controller'], 'claim_id': predecessor['claim_id'],
            'run_root_identity': predecessor['run_root_identity'],
            'projection_generation_id': epoch, 'continuity_epoch': epoch,
            'boundary': 'canonical-state-rotation', 'invalidation_oid': oid,
            'predecessor_receipt_ref_oid': predecessor['receipt_ref'] + '@' + predecessor['receipt_oid'],
            'expected_receipt_ref_schema': {'ref': 'refs/implementaudit/continuity-receipts/' + predecessor['controller'] + '/' + epoch,
                                           'schema': 'implementaudit.continuity-receipt.v3'},
            'transition_kind': 'recovery' if recovery else 'rotation',
            'payload_source': 'preimage' if recovery else 'draft',
            'failed_transition_epoch': 'G0002' if recovery else None,
            'failed_transition_generation': 'G0002' if recovery else None,
            'failed_transition_receipt_ref_oid': None,
            'head': predecessor['head'], 'tree': predecessor['tree']}


class ArchiveQualification(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='r0039-archive-')
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def subject(self, name='repo', large=True):
        return make_subject(self.base / name, large=large)

    def test_below_threshold_keeps_legacy_cheap_path_and_creates_nothing(self):
        subject = self.subject(large=False)
        # Unsupported short ordinary prose needs no owner-map or schema migration.
        for role in ('state', 'roadmap'):
            raw = ('# Ordinary ' + role + '\n').encode()
            (subject['run'] / (role.upper() + '.md')).write_bytes(raw)
            subject['predecessor'][role + '_sha256'] = M.sha256(raw)
        subject['owner_map'].unlink()
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        result = prepare(subject)
        self.assertFalse(result['triggered'])
        self.assertEqual(result['archive_writes'], 0)
        self.assertEqual(result['model_calls'], 0)
        self.assertFalse((subject['run'] / 'state-generations').exists())
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_actual_archive_gc_retention_typed_retrieval_and_no_current_authority(self):
        subject = self.subject()
        prepared = prepare(subject)
        before = M.verify_canonical_archive(subject['repo'], prepared['controller'],
                                           prepared['archive_ref'], prepared['archive_manifest_sha256'])
        git(subject['repo'], 'gc', '--prune=now')
        after = M.verify_canonical_archive(subject['repo'], prepared['controller'],
                                          prepared['archive_ref'], prepared['archive_manifest_sha256'])
        self.assertEqual(before, after)
        preimage = M._archive_preimage(subject['repo'], after)
        pointers = M._pointers(preimage, prepared['archive_ref'], prepared['archive_manifest_oid'],
                               prepared['archive_manifest_sha256'], prepared['generation_id'])
        for pointer in pointers:
            result = M.resolve_typed_archive_pointer_v2(subject['repo'], pointer)
            self.assertEqual(result['authority_ceiling'], 'ARCHIVED_ONLY_HISTORY')
            self.assertEqual(M.sha256(result['bytes']), pointer['record_sha256'])
        refs = git(subject['repo'], 'for-each-ref', '--format=%(refname)').decode().splitlines()
        self.assertTrue(all('/state-archives/' in ref or '/continuity-receipts/' in ref for ref in refs))
        self.assertEqual((subject['run'] / 'STATE.md').read_bytes(), subject['source'][0])
        self.assertEqual((subject['run'] / 'ROADMAP.md').read_bytes(), subject['source'][1])

    def test_archive_git_effects_do_not_execute_repository_hooks(self):
        subject = self.subject()
        hook = subject['repo'] / '.git/hooks/reference-transaction'
        hook.write_text('#!/bin/sh\nexit 97\n', encoding='utf-8')
        hook.chmod(0o755)
        before = git(subject['repo'], 'config', '--local', '--list')
        prepared = prepare(subject)
        self.assertTrue(prepared['triggered'])
        self.assertEqual(before, git(subject['repo'], 'config', '--local', '--list'))
        self.assertEqual(hook.read_text(), '#!/bin/sh\nexit 97\n')

    def test_two_clean_roots_produce_byte_identical_draft_and_final_files(self):
        populations = []
        for name in ('first', 'second'):
            subject = self.subject(name)
            prepared = prepare(subject)
            result = M.finalize_canonical_projection(subject['repo'], subject['run'], prepared,
                                                      transition(subject, prepared))
            resolved = M.read_canonical_generation(subject['repo'], subject['run'], result['pointer'])
            self.assertEqual(resolved['state_path'], result['generation_dir'] / 'STATE.md')
            populations.append({p.relative_to(subject['run']).as_posix(): p.read_bytes()
                                for p in (subject['run'] / 'state-generations').rglob('*') if p.is_file()})
        self.assertEqual(populations[0], populations[1])

    def test_immutable_reader_rejects_every_changed_pointer_binding(self):
        subject = self.subject()
        prepared = prepare(subject)
        result = M.finalize_canonical_projection(subject['repo'], subject['run'], prepared,
                                                  transition(subject, prepared))
        for key in result['pointer']:
            changed = copy.deepcopy(result['pointer'])
            changed[key] = 'unknown'
            with self.subTest(field=key), self.assertRaises((M.RotationError, ValueError, KeyError)):
                M.read_canonical_generation(subject['repo'], subject['run'], changed)
        path = result['generation_dir'] / 'STATE.md'
        path.chmod(0o644)
        with self.assertRaises(M.RotationError):
            M.read_canonical_generation(subject['repo'], subject['run'], result['pointer'])

    def test_draft_corruption_and_future_receipt_are_not_finalized(self):
        subject = self.subject()
        prepared = prepare(subject)
        native = transition(subject, prepared)
        future = dict(native, future_receipt_oid='1' * 40)
        with self.assertRaises(M.RotationError):
            M.finalize_canonical_projection(subject['repo'], subject['run'], prepared, future)
        path = subject['run'] / prepared['draft_path'] / 'STATE.md'
        path.chmod(0o644)
        path.write_bytes(path.read_bytes() + b'Unparsed mutation\n')
        path.chmod(0o444)
        with self.assertRaises(M.RotationError):
            M.finalize_canonical_projection(subject['repo'], subject['run'], prepared, native)
        self.assertNotIn(b'current-generations', git(subject['repo'], 'for-each-ref', '--format=%(refname)'))
        M.verify_canonical_archive(subject['repo'], prepared['controller'],
                                   prepared['archive_ref'], prepared['archive_manifest_sha256'])

    def test_source_links_path_aliases_and_owner_omissions_refuse(self):
        subject = self.subject()
        path = subject['run'] / 'fixtures/boundary-evidence.txt'
        outside = self.base / 'outside-evidence'
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(M.RotationError):
            prepare(subject)
        for value in ('../STATE.md', '/STATE.md', 'C:/STATE.md', 'dir\\file', 'x/CON', 'x/NUL.txt', 'x/a.', 'x/a ', 'x/./a', 'x/a:b'):
            with self.subTest(path=value), self.assertRaises(M.RotationError):
                M.safe_relative(value, set())
        path.unlink()
        path.write_bytes(outside.read_bytes())
        owner = json.loads(subject['owner_map'].read_text())
        owner['owner_map'].pop()
        subject['owner_map'].write_bytes(M.canonical_bytes(owner))
        with self.assertRaises(M.RotationError):
            prepare(subject)

    def test_recovery_uses_verified_archive_and_explicit_failed_epoch(self):
        subject = self.subject()
        prepared = prepare(subject)
        native = transition(subject, prepared, recovery=True)
        bad = dict(native, failed_transition_epoch=None)
        with self.assertRaises(M.RotationError):
            M.finalize_canonical_projection(subject['repo'], subject['run'], prepared, bad)
        final = M.finalize_canonical_projection(subject['repo'], subject['run'], prepared, native)
        self.assertEqual(final['pointer']['continuity_epoch'], 'G0003')
        self.assertEqual(final['pointer']['predecessor_receipt_ref_oid'],
                         subject['predecessor']['receipt_ref'] + '@' + subject['predecessor']['receipt_oid'])
        refs = git(subject['repo'], 'for-each-ref', '--format=%(refname)').decode()
        self.assertNotIn('/continuity-receipts/r0039-fixture/G0002', refs)
        self.assertNotIn('/current-generations/', refs)

    def test_unknown_predecessor_metadata_refuses_before_archive_effects(self):
        for field in ('future_receipt_oid', 'future_pointer_oid', 'unknown_owner_grant'):
            with self.subTest(field=field):
                subject = self.subject(field)
                subject['predecessor'][field] = '1' * 40
                before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
                with self.assertRaises(M.RotationError):
                    prepare(subject)
                self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))
                self.assertFalse((subject['run'] / 'state-generations').exists())

    def test_prepared_envelope_unknown_fields_refuse_before_final_generation(self):
        for nested in (False, True):
            with self.subTest(nested=nested):
                subject = self.subject('prepared-' + str(nested))
                prepared = prepare(subject)
                changed = copy.deepcopy(prepared)
                (changed['measurement'] if nested else changed)['future_receipt_oid'] = '1' * 40
                with self.assertRaises(M.RotationError):
                    M.finalize_canonical_projection(subject['repo'], subject['run'], changed, transition(subject, prepared))
                self.assertFalse((subject['run'] / 'state-generations/G0002/STATE.md').exists())

    def test_rebound_archive_metadata_must_match_complete_source_population(self):
        subject = self.subject()
        prepared = prepare(subject)
        original = M.verify_canonical_archive(subject['repo'], prepared['controller'],
                                             prepared['archive_ref'], prepared['archive_manifest_sha256'])
        preimage = M._archive_preimage(subject['repo'], original)
        pointer = M._pointers(preimage, prepared['archive_ref'], prepared['archive_manifest_oid'],
                              prepared['archive_manifest_sha256'], prepared['generation_id'])[0]
        current_oid = prepared['archive_manifest_oid']
        mutations = [('entry', 'role', 'UNKNOWN_ROLE'), ('entry', 'owner', 'UNKNOWN_OWNER'),
                     ('entry', 'source_path', '../outside.txt'),
                     ('manifest', 'claim_id', 'another-claim'),
                     ('manifest', 'run_root_identity', '.IMPLEMENTAUDIT/runs/another-run'),
                     ('predecessor', 'future_receipt_oid', '1' * 40),
                     ('entry', 'byte_length', True), ('entry', 'mode', 'garbage')]
        for level, field, value in mutations:
            with self.subTest(level=level, field=field):
                changed = copy.deepcopy(original)
                target = (next(x for x in changed['entries'] if x['role'] == 'EVIDENCE')
                          if level == 'entry' else changed['predecessor'] if level == 'predecessor' else changed)
                target[field] = value
                raw = M.canonical_bytes(changed)
                oid = git(subject['repo'], 'hash-object', '-w', '--stdin', data=raw).decode().strip()
                git(subject['repo'], 'update-ref', prepared['archive_ref'], oid, current_oid)
                current_oid = oid
                with self.assertRaises(M.RotationError):
                    M.verify_canonical_archive(subject['repo'], prepared['controller'], prepared['archive_ref'], M.sha256(raw))
                altered = dict(pointer, archive_manifest_oid=oid, archive_manifest_sha256=M.sha256(raw))
                with self.assertRaises(M.RotationError):
                    M.resolve_typed_archive_pointer_v2(subject['repo'], altered)
        git(subject['repo'], 'update-ref', prepared['archive_ref'], prepared['archive_manifest_oid'], current_oid)
        self.assertEqual(M.resolve_typed_archive_pointer_v2(subject['repo'], pointer)['bytes'], subject['source'][0])

    def test_missing_retained_archive_refuses_before_new_archive_effects(self):
        bodies = F.fixture_bodies()
        state, roadmap, owners, artifacts = F.fixture_pair(bodies)
        prior = F.archive_pointers(M._parse(state, roadmap, owners, artifacts), 'G0001')[0]
        bodies['STATE']['archive_pointers'] = [prior]
        with mock.patch.object(F, 'fixture_bodies', return_value=bodies):
            subject = self.subject()
        before = git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
        with self.assertRaises(M.RotationError):
            prepare(subject)
        self.assertEqual(before, git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)'))

    def test_real_retained_archive_chain_survives_gc_and_missing_ancestor_refuses(self):
        subject = self.subject()
        first = prepare(subject)
        manifest = M.verify_canonical_archive(subject['repo'], first['controller'], first['archive_ref'], first['archive_manifest_sha256'])
        old = M._pointers(M._archive_preimage(subject['repo'], manifest), first['archive_ref'],
                          first['archive_manifest_oid'], first['archive_manifest_sha256'], first['generation_id'])
        # A second exact constructed legacy preimage at G0002 retains the
        # first attempted rotation's real historical archive. No campaign or
        # owner currentness is inferred from these fixture receipts.
        bodies = F.fixture_bodies()
        bodies['STATE']['history'][0]['payload']['text'] = 'Later exact retained history.\n' * 7000
        for body in bodies.values():
            body['archive_pointers'] = copy.deepcopy(old)
            body['continuity'].update(continuity_epoch='G0002', projection_generation_id='G0002',
                expected_receipt_ref='refs/implementaudit/continuity-receipts/' + first['controller'] + '/G0002',
                predecessor_receipt_ref_oid=subject['predecessor']['receipt_ref'] + '@' + subject['predecessor']['receipt_oid'])
            for declaration in body['artifact_refs']:
                if declaration['role'] == 'CONTINUITY_RECEIPT':
                    declaration['locator'] = body['continuity']['expected_receipt_ref']
        state, roadmap, owners, artifacts = F.fixture_pair(bodies)
        for role, raw in (('STATE', state), ('ROADMAP', roadmap)):
            (subject['run'] / (role + '.md')).write_bytes(raw)
            subject['predecessor'][role.lower() + '_sha256'] = M.sha256(raw)
        receipt_oid = git(subject['repo'], 'hash-object', '-w', '--stdin', data=artifacts['receipt']).decode().strip()
        receipt_ref = bodies['STATE']['continuity']['expected_receipt_ref']
        git(subject['repo'], 'update-ref', receipt_ref, receipt_oid, '0' * 40)
        subject['owner_map'].write_bytes(M.canonical_bytes({'schema': 'implementaudit.rotation-owner-map.v2', 'owner_map': owners}))
        subject['predecessor'].update(continuity_epoch='G0002', projection_generation_id='G0002',
                                      receipt_ref=receipt_ref, receipt_oid=receipt_oid)
        second = M.prepare_canonical_draft(subject['repo'], subject['run'], first['controller'],
                   'G0003', subject['owner_map'], subject['predecessor'], M.calibration_contract_v1())
        successor = transition(subject, second)
        successor.update(projection_generation_id='G0003', continuity_epoch='G0003')
        successor['expected_receipt_ref_schema']['ref'] = 'refs/implementaudit/continuity-receipts/' + first['controller'] + '/G0003'
        git(subject['repo'], 'update-ref', 'refs/r0039-test/constructed-invalidation', successor['invalidation_oid'], '0' * 40)
        final = M.finalize_canonical_projection(subject['repo'], subject['run'], second, successor)
        git(subject['repo'], 'gc', '--prune=now')
        M.read_canonical_generation(subject['repo'], subject['run'], final['pointer'])
        self.assertEqual(M.resolve_typed_archive_pointer_v2(subject['repo'], old[0])['bytes'], subject['source'][0])
        git(subject['repo'], 'update-ref', '-d', first['archive_ref'], first['archive_manifest_oid'])
        with self.assertRaises(M.RotationError):
            M.verify_canonical_archive(subject['repo'], second['controller'], second['archive_ref'], second['archive_manifest_sha256'])
        with self.assertRaises(M.RotationError):
            M.read_canonical_generation(subject['repo'], subject['run'], final['pointer'])
        git(subject['repo'], 'update-ref', first['archive_ref'], first['archive_manifest_oid'], '0' * 40)
        self.assertEqual(M.resolve_typed_archive_pointer_v2(subject['repo'], old[0])['bytes'], subject['source'][0])

    def test_admitted_predecessor_must_equal_complete_source_identity_and_action(self):
        for key, value in [('exact_next_action', 'Substituted continuation'),
                           ('claim_id', 'other-claim'), ('head', '9' * 40),
                           ('tree', '8' * 40), ('continuity_epoch', 'G0009')]:
            subject = self.subject('predecessor-' + key)
            subject['predecessor'][key] = value
            with self.subTest(field=key), self.assertRaises(M.RotationError):
                prepare(subject)

    def test_typed_pointer_cannot_substitute_preparation_generation(self):
        subject = self.subject()
        prepared = prepare(subject)
        archive = M.verify_canonical_archive(subject['repo'], prepared['controller'],
                                              prepared['archive_ref'], prepared['archive_manifest_sha256'])
        preimage = M._archive_preimage(subject['repo'], archive)
        pointer = M._pointers(preimage, prepared['archive_ref'], prepared['archive_manifest_oid'],
                               prepared['archive_manifest_sha256'], 'G0002')[0]
        pointer['preparation_generation_id'] = 'GFFFF'
        with self.assertRaises(M.RotationError):
            M.resolve_typed_archive_pointer_v2(subject['repo'], pointer)

    def test_checked_parent_replacement_cannot_read_or_create_outside_custody(self):
        for operation in ('read', 'write'):
            custody = self.base / ('custody-' + operation)
            parent = custody / 'slot'
            outside = self.base / ('outside-' + operation)
            parent.mkdir(parents=True)
            outside.mkdir()
            if operation == 'read':
                (parent / 'input').write_bytes(b'INSIDE')
                (outside / 'input').write_bytes(b'OUTSIDE')
            original = M.require_safe_directory_chain
            fired = False

            def replace_after_check(path, root):
                nonlocal fired
                original(path, root)
                if not fired and path == parent:
                    fired = True
                    parent.rename(custody / 'retained-parent')
                    parent.symlink_to(outside, target_is_directory=True)

            with mock.patch.object(M, 'require_safe_directory_chain', side_effect=replace_after_check):
                with self.subTest(operation=operation), self.assertRaises(M.RotationError):
                    if operation == 'read':
                        M.read_regular(parent / 'input', custody, 'race input', require_owner_write=False)
                    else:
                        M._write_verified(parent / 'STATE.md', b'IMMUTABLE', custody)
            self.assertTrue(fired)
            if operation == 'write':
                self.assertFalse((outside / 'STATE.md').exists())

    def test_parent_replacement_after_handle_acquisition_refuses_without_redirect(self):
        for operation in ('read', 'write'):
            custody = self.base / ('held-' + operation)
            parent, outside = custody / 'slot', self.base / ('held-outside-' + operation)
            parent.mkdir(parents=True)
            outside.mkdir()
            (parent / 'input').write_bytes(b'INSIDE')
            (outside / 'input').write_bytes(b'OUTSIDE')
            original = M._directory_handle
            calls = 0

            @contextlib.contextmanager
            def replace_after_open(path, root, **kwargs):
                nonlocal calls
                with original(path, root, **kwargs) as held:
                    if path == parent:
                        calls += 1
                        if calls == 2:
                            parent.rename(custody / 'retained-parent')
                            parent.symlink_to(outside, target_is_directory=True)
                    yield held

            with mock.patch.object(M, '_directory_handle', side_effect=replace_after_open):
                with self.subTest(operation=operation), self.assertRaises(M.RotationError):
                    if operation == 'read':
                        M.read_regular(parent / 'input', custody, 'held input', require_owner_write=False)
                    else:
                        M._write_verified(parent / 'STATE.md', b'IMMUTABLE', custody)
            self.assertEqual(calls, 2)
            self.assertFalse((outside / 'STATE.md').exists())

    def test_large_valid_source_refuses_memory_admission_before_archive_effects(self):
        # Independent process keeps this deliberately large constructed fixture
        # out of the other tests' process peak-RSS admission population.
        script = '''
import importlib.util, json, resource, sys, tempfile
from pathlib import Path
spec = importlib.util.spec_from_file_location('memory_subject', sys.argv[1])
A = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = A
spec.loader.exec_module(A)
bodies = A.F.fixture_bodies()
bodies['STATE']['history'][0]['payload']['text'] = 'x' * (12 * 1024 * 1024)
A.F.fixture_bodies = lambda: bodies
with tempfile.TemporaryDirectory(prefix='r0039-memory-') as directory:
    subject = A.make_subject(Path(directory) / 'repo', large=False)
    before = A.git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
    try:
        A.prepare(subject)
        reason = None
    except A.M.RotationError as exc:
        reason = str(exc)
    after = A.git(subject['repo'], 'for-each-ref', '--format=%(refname) %(objectname)')
    print(json.dumps({'refusal': reason, 'refs_unchanged': before == after,
                     'generation_absent': not (subject['run'] / 'state-generations').exists(),
                     'source_bytes': sum(map(len, subject['source']))}))
'''
        result = subprocess.run([sys.executable, '-B', '-c', script, str(Path(__file__).resolve())],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        observed = json.loads(result.stdout)
        self.assertIn('memory', observed['refusal'])
        self.assertGreater(observed['source_bytes'], 12 * 1024 * 1024)
        self.assertTrue(observed['refs_unchanged'])
        self.assertTrue(observed['generation_absent'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
