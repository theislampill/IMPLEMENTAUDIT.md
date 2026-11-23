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
    'fixtures/run-root-example/phases/phase-1.md',
    'skills/implementaudit/scripts',
    'skills/implementaudit/templates',
]
WINDOWS_GIT = '/mnt/c/Program Files/Git/cmd/git.exe'
CHECKOUT = Path.cwd().resolve()
POSIX_TEMP = Path('/var/tmp').resolve()

def enter_private_git_view():
    assert os.geteuid() == 0
    ambient = Path('/.git')
    before = (ambient.stat().st_dev, ambient.stat().st_ino, sorted(p.name for p in ambient.iterdir()))
    assert before[2]
    shell = '''set -eu
mount --bind "$1" /.git
mount -o remount,bind,ro /.git
test -z "$(ls -A /.git)"
exec /usr/bin/setpriv --reuid 1000 --regid 1000 --init-groups --reset-env \
    /usr/bin/python3 -I -B "$2" --private-git-view "$3" "$4"
'''
    with tempfile.TemporaryDirectory(prefix='dg18-private-git-view-', dir=POSIX_TEMP) as temporary:
        empty = Path(temporary).resolve()
        assert empty.parent == POSIX_TEMP
        empty.chmod(0o755)
        result = subprocess.run(['unshare', '--mount',
                                 '--propagation', 'private', '/bin/bash', '-c', shell,
                                 'dg18-private-git-view', str(empty), str(Path(__file__).resolve()), *sys.argv[1:]],
                                check=False, timeout=120)
    after = (ambient.stat().st_dev, ambient.stat().st_ino, sorted(p.name for p in ambient.iterdir()))
    unchanged = before == after
    print(json.dumps({'ambient_git_directory_unchanged': unchanged,
                      'namespace_scratch_removed': not empty.exists()}), flush=True)
    return result.returncode if unchanged and not empty.exists() else 1

if len(sys.argv) == 3:
    sys.exit(enter_private_git_view())
assert len(sys.argv) == 4 and sys.argv[1] == '--private-git-view' and not any(Path('/.git').iterdir())
DOCUMENT_CUSTODY, FRONTIER_CUSTODY = map(Path, sys.argv[2:])
assert os.geteuid() == 1000 and Path(sys.executable).resolve().stat().st_uid == 0

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
    test = 'fixtures/canonical-state-rotation/canonical_reader_test.py'
    assert expected[test] == b'38edca905b5c8dea5134cb8ec48e60f1ac100577'
    print(json.dumps({'candidate': CANDIDATE, 'tree': TREE, 'verified_source_members': len(expected),
                      'fixture_blob': expected[test].decode()}), flush=True)
    spec = importlib.util.spec_from_file_location('criterion4_posix_base', source / test)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    return fixture

def payload(pair_bytes):
    return json.loads(pair_bytes.split(b'\x60\x60\x60json\n')[1].split(b'\n\x60\x60\x60')[0])['payload']

with tempfile.TemporaryDirectory(prefix='dg18-dual-reader-', dir=POSIX_TEMP) as temporary:
    scratch = Path(temporary).resolve()
    assert scratch.parent == POSIX_TEMP
    filesystem = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(scratch)],
                                capture_output=True, check=True, text=True, timeout=10).stdout.strip()
    assert filesystem == 'ext4'
    source = scratch / 'source'
    fixture = load_exact_fixture(source)
    occurrence_path = source / 'fixtures/canonical-state-rotation/occurrence_preservation_test.py'
    occurrence_spec = importlib.util.spec_from_file_location('document_pins', occurrence_path)
    occurrence = importlib.util.module_from_spec(occurrence_spec)
    occurrence_spec.loader.exec_module(occurrence)
    documents = occurrence.pinned_documents(DOCUMENT_CUSTODY)
    selected_frontier = occurrence.pinned_frontier_selection(FRONTIER_CUSTODY)
    facts = occurrence.historical_facts(documents, selected_frontier)
    artifacts = {'documentary/' + name + '.json': body for name, body in documents.items()}
    artifacts['documentary/selected_frontier.json'] = occurrence.F.canonical(selected_frontier)
    records = {
        'STATE': ('evidence_ceilings', occurrence.row('documentary-occurrence-scope', 'UNVERIFIED',
                  occurrence.F.canonical(facts).decode())),
        'ROADMAP': ('obligations', occurrence.row('original-14114-native-consumption', 'BLOCKED',
                     'Recorded native consumption remains unproved and uncovered by boundary 13520.')),
    }

    class DocumentaryReader(fixture.CanonicalReaderTests):
        def test_public_pair_and_typed_archive_preserve_documentary_records(self):
            original_loads = json.loads
            template = (occurrence_path.parent / 'v2/source.json').read_text()
            edited = []
            def include_documentary_rows(raw, *args, **kwargs):
                data = original_loads(raw, *args, **kwargs)
                if raw == template:
                    for role, (field, record) in records.items():
                        data['bodies'][role]['payload'][field]['value'].append(record)
                    edited.append(True)
                return data

            with mock.patch.object(fixture.json, 'loads', side_effect=include_documentary_rows):
                resolved = self.make_real_generation(native=True, extra_artifacts=artifacts)
            self.assertEqual(edited, [True])
            ref_args = ('for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit/')
            before = self.git(*ref_args)
            reader = self.load_reader()
            dispatched = []
            actual_owner = reader.owner
            def observe(repo, *args):
                dispatched.append(args)
                return actual_owner(repo, *args)
            with mock.patch.object(reader, 'owner', side_effect=observe):
                self.assertEqual(reader.materialize_pair(self.run, self.output, native_guards=True), 0)
            self.assertEqual([args[0] for args in dispatched], ['--current-controller', '--resolve-canonical-generation',
                '--read-canonical-state', '--read-canonical-state', '--resolve-canonical-generation'])
            self.assertEqual([args[3] for args in dispatched[2:4]], ['STATE', 'ROADMAP'])
            self.assertEqual([args[5] for args in dispatched[2:4]], [resolved['pointer_token']] * 2)
            self.assertTrue(json.loads((self.output / 'resolution.json').read_bytes()) == resolved)

            helper = occurrence.load('documentary_archive_owner', self.scripts / 'rotate-canonical-state.py')
            pointer = resolved['pointer']
            epoch = pointer['projection_generation_id']
            anchor = f'refs/implementaudit/state-archives/{fixture.CONTROLLER}/{epoch}'
            archive_sha = pointer['archive_manifest_sha256']
            manifest = helper.verify_canonical_archive(self.repo, fixture.CONTROLLER, anchor, archive_sha)
            oid = self.git('rev-parse', anchor)
            preimage = helper._archive_preimage(self.repo, manifest)
            pointers = helper._pointers(preimage, anchor, oid, archive_sha, epoch)
            archived_documents = {}
            for entry in manifest['entries']:
                loc = entry['source_path']
                if loc in artifacts:
                    body = helper._blob(self.repo, entry['blob_oid'])
                    self.assertTrue(body == artifacts[loc], 'archived documentary body differs')
                    archived_documents[loc] = descriptor(body)
            self.assertTrue(set(archived_documents) == set(artifacts), 'document population differs')

            pair = {}
            for role, (field, record) in records.items():
                current = (self.output / (role + '.md')).read_bytes()
                self.assertEqual(descriptor(current)['sha256'], pointer[role.lower() + '_sha256'])
                item, = [p for p in pointers if p['role'] == role + '_PREIMAGE']
                old = helper.resolve_typed_archive_pointer_v2(self.repo, item)
                self.assertEqual(old['authority_ceiling'], 'ARCHIVED_ONLY_HISTORY')
                self.assertTrue(old['bytes'] == (self.run / (role + '.md')).read_bytes(), 'archived preimage differs')
                for candidate in (current, old['bytes']):
                    selected, = [row for row in payload(candidate)[field]['value']
                                 if row['record_id'] == record['record_id']]
                    self.assertTrue(selected == record, 'documentary status or description differs')
                pair[role] = {'projected': descriptor(current), 'archived_preimage': descriptor(old['bytes']),
                              'record_status': record['status']}

            self.assertEqual(self.git(*ref_args), before)
            self.assertEqual(occurrence.pinned_documents(DOCUMENT_CUSTODY), documents)
            self.assertEqual(occurrence.pinned_frontier_selection(FRONTIER_CUSTODY), selected_frontier)
            print(json.dumps({'documentary_boundary_scope': {
                                  '13520': {'cutoff_line': facts['boundary13520']['cutoff_line'],
                                            'covers_14114': facts['boundary13520']['covers_14114'],
                                            'native_consumption': facts['boundary13520']['native_consumption']},
                                  '14114': {'cutoff_line': facts['boundary14114']['cutoff_line'],
                                            'native_consumption': facts['boundary14114']['native_consumption'],
                                            'native_consumption_obligation': facts['boundary14114']['native_consumption_obligation']}},
                              'h0_identity': facts['h0_identity'], 'archived_documents': archived_documents,
                              'receipt_token': resolved['receipt_token'], 'pointer_token': resolved['pointer_token'],
                              'marker_oid': resolved['marker_oid'], 'archive_oid': oid,
                              'public_read_order':['STATE', 'ROADMAP'], 'both_bound_to_same_pointer': True,
                              'exact_typed_preimage_comparisons': pair, 'authority_refs_unchanged_while_reading': True,
                              'original_documents_unchanged': True, 'native_pending_consumption': False}), flush=True)

    selected = DocumentaryReader('test_public_pair_and_typed_archive_preserve_documentary_records')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([selected]))
print(json.dumps({'ok': result.wasSuccessful(), 'filesystem': filesystem, 'scratch_removed': not scratch.exists()}))
sys.exit(0 if result.wasSuccessful() and not scratch.exists() else 1)
