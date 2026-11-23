import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

CANDIDATE = '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7'
TREE = '9c3913ceaa95f3f36b0377fe2dba4a302afcba89'
SOURCE_PATHS = [
    'fixtures/canonical-state-rotation',
    'fixtures/controller-initialization',
    'skills/implementaudit/scripts',
    'skills/implementaudit/templates',
]
WINDOWS_GIT = '/mnt/c/Program Files/Git/cmd/git.exe'
CHECKOUT = Path.cwd().resolve()
POSIX_TEMP = Path('/var/tmp').resolve()

def source_git(*args):
    return subprocess.run([WINDOWS_GIT, *args], cwd=CHECKOUT, capture_output=True,
                          check=True, timeout=30).stdout

def descriptor(body):
    return {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}

def load_exact_fixture(source):
    assert source_git('rev-parse', f'{CANDIDATE}^{{tree}}').decode().strip() == TREE
    archive = source_git('archive', '--format=tar', CANDIDATE, '--', *SOURCE_PATHS)
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as tar:
        tar.extractall(source, filter='data')
    rows = source_git('ls-tree', '-rz', CANDIDATE, '--', *SOURCE_PATHS).split(b'\0')
    expected = {}
    for row in filter(None, rows):
        header, name = row.split(b'\t')
        mode, kind, oid = header.split()
        assert mode in {b'100644', b'100755'} and kind == b'blob'
        path = source / name.decode()
        raw = path.read_bytes()
        blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest().encode()
        assert not path.is_symlink() and blob == oid
        assert bool(path.stat().st_mode & 0o111) == (mode == b'100755')
        expected[path.relative_to(source).as_posix()] = oid
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    assert actual == set(expected)
    test = 'fixtures/canonical-state-rotation/archive_v2_test.py'
    assert expected[test] == b'3b4d52c7f998b28e5e7376a875d6ff97b1235567'
    print(json.dumps({'candidate': CANDIDATE, 'tree': TREE, 'verified_source_members': len(expected),
                      'fixture_blob': expected[test].decode()}), flush=True)
    spec = importlib.util.spec_from_file_location('criterion4_posix_base', source / test)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    return fixture

def footprint(repo):
    gitdir = repo / '.git'
    storage = {}
    for label, roots in (
        ('objects', (gitdir / 'objects',)),
        ('refs', (gitdir / 'refs', gitdir / 'packed-refs')),
        ('reflogs', (gitdir / 'logs',)),
    ):
        regular_files, directories, file_bytes, allocated_bytes = 0, 0, 0, 0
        for path in roots:
            if not path.exists():
                continue
            members = [path, *path.rglob('*')] if path.is_dir() else [path]
            for member in members:
                assert not member.is_symlink()
                stat = member.stat()
                allocated_bytes += stat.st_blocks * 512
                if member.is_file():
                    regular_files += 1
                    file_bytes += stat.st_size
                else:
                    assert member.is_dir()
                    directories += 1
        storage[label] = {'regular_files': regular_files, 'directories': directories,
                          'file_bytes': file_bytes, 'allocated_bytes': allocated_bytes}
    rows = fixture_git(repo, 'cat-file', '--batch-all-objects',
                       '--batch-check=%(objectname) %(objecttype) %(objectsize)').decode().splitlines()
    objects = {row.split()[0]: int(row.split()[-1]) for row in rows}
    assert len(rows) == len(objects)
    refs = fixture_git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').decode().splitlines()
    anchors = sorted(row.split()[0] for row in refs
                     if row.split()[0].startswith('refs/implementaudit/state-archives/')
                     and len(row.split()[0].split('/')) == 5)
    return {'storage': storage, 'object_count': len(objects), 'logical_object_bytes': sum(objects.values()),
            'ref_count': len(refs), 'ref_population_sha256': hashlib.sha256('\n'.join(refs).encode()).hexdigest(),
            'archive_anchors': anchors}

with tempfile.TemporaryDirectory(prefix='dg18-storage-', dir=POSIX_TEMP) as temporary:
    scratch = Path(temporary).resolve()
    assert scratch.parent == POSIX_TEMP
    filesystem = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(scratch)],
                                capture_output=True, check=True, text=True, timeout=10).stdout.strip()
    assert filesystem == 'ext4'
    fixture = load_exact_fixture(scratch / 'source')
    fixture_git = fixture.git
    owner_prepare = fixture.M.prepare_canonical_draft
    retained = []
    snapshots = {}

    def instrument_prepare(repo, *args, **kwargs):
        label = 'first' if not retained else 'second'
        snapshots['before_' + label] = footprint(repo)
        outcome = owner_prepare(repo, *args, **kwargs)
        snapshots['after_' + label] = footprint(repo)
        retained.append(outcome)
        return outcome

    def instrument_git(repo, *args, data=None):
        if args == ('gc', '--prune=now'):
            snapshots['before_gc'] = footprint(repo)
            output = fixture_git(repo, *args, data=data)
            snapshots['after_gc'] = footprint(repo)
            return output
        return fixture_git(repo, *args, data=data)

    class ArchiveStorage(fixture.ArchiveQualification):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix='fixture-', dir=scratch)
            self.base = Path(self.temp.name)

        def test_exact_existing_retained_chain_cost(self):
            with mock.patch.object(fixture.M, 'prepare_canonical_draft', instrument_prepare), \
                 mock.patch.object(fixture, 'git', instrument_git):
                self.test_real_retained_archive_chain_survives_gc_and_missing_ancestor_refuses()
            self.assertEqual(len(retained), 2)
            repo = self.base / 'repo'
            final = footprint(repo)
            packed = snapshots['after_gc']
            self.assertEqual(final['ref_population_sha256'], packed['ref_population_sha256'])
            self.assertEqual(final['storage']['objects'], packed['storage']['objects'])
            self.assertEqual(final['archive_anchors'], packed['archive_anchors'])
            snapshots['after_restore'] = final
            aggregates, objects_by_generation = [], []
            for record in retained:
                manifest = fixture.M.verify_canonical_archive(repo, record['controller'], record['archive_ref'],
                                                             record['archive_manifest_sha256'])
                objects = {entry['blob_oid']: entry['byte_length'] for entry in manifest['entries']}
                objects_by_generation.append(objects)
                aggregates.append({'archive_ref': record['archive_ref'], 'manifest_oid': record['archive_manifest_oid'],
                                   'entries': len(manifest['entries']), 'entry_unique_objects': len(objects),
                                   'entry_unique_logical_bytes': sum(objects.values())})
            old, new = objects_by_generation
            shared = old.keys() & new.keys()
            self.assertTrue(shared)
            self.assertTrue(all(old[oid] == new[oid] for oid in shared))
            union = old | new
            print(json.dumps({'snapshots': snapshots, 'archives': aggregates,
                              'archive_entry_union': {'objects': len(union), 'bytes':sum(union.values()),
                                                      'shared_objects':len(shared),
                                                      'shared_bytes':sum(old[oid] for oid in shared)},
                              'original_chain_refusal_and_restoration_passed': True,
                              'restored_refs_and_object_storage_match_post_gc': True}), flush=True)

    selected = ArchiveStorage('test_exact_existing_retained_chain_cost')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([selected]))
    fixture_cleanup = sorted(path.name for path in scratch.iterdir())
print(json.dumps({'ok': result.wasSuccessful(), 'filesystem': filesystem,
                  'scratch_entries_before_cleanup': fixture_cleanup,
                  'scratch_removed': not scratch.exists()}))
sys.exit(0 if result.wasSuccessful() and fixture_cleanup == ['source'] and not scratch.exists() else 1)
