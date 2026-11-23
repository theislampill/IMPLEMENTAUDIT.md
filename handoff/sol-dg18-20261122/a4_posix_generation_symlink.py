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
    /usr/bin/python3 -I -B "$2" --private-git-view
'''
    with tempfile.TemporaryDirectory(prefix='dg18-private-git-view-', dir=POSIX_TEMP) as temporary:
        empty = Path(temporary).resolve()
        assert empty.parent == POSIX_TEMP
        empty.chmod(0o755)
        result = subprocess.run(['unshare', '--mount',
                                 '--propagation', 'private', '/bin/bash', '-c', shell,
                                 'dg18-private-git-view', str(empty), str(Path(__file__).resolve())],
                                check=False, timeout=120)
    after = (ambient.stat().st_dev, ambient.stat().st_ino, sorted(p.name for p in ambient.iterdir()))
    unchanged = before == after
    print(json.dumps({'ambient_git_directory_unchanged': unchanged,
                      'namespace_scratch_removed': not empty.exists()}), flush=True)
    return result.returncode if unchanged and not empty.exists() else 1

if len(sys.argv) == 1:
    sys.exit(enter_private_git_view())
assert sys.argv[1:] == ['--private-git-view'] and not any(Path('/.git').iterdir())
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
    test = 'fixtures/canonical-state-rotation/claim_transaction_test.py'
    assert expected[test] == b'ce6e41cd79b57747416080a8dd3cc373249d87b2'
    print(json.dumps({'candidate': CANDIDATE, 'tree': TREE, 'verified_source_members': len(expected),
                      'fixture_blob': expected[test].decode()}), flush=True)
    spec = importlib.util.spec_from_file_location('criterion4_posix_base', source / test)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    return fixture

with tempfile.TemporaryDirectory(prefix='dg18-posix-', dir=POSIX_TEMP) as temporary:
    scratch = Path(temporary).resolve()
    assert scratch.parent == POSIX_TEMP
    filesystem = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '-T', str(scratch)],
                                capture_output=True, check=True, text=True, timeout=10).stdout.strip()
    assert filesystem == 'ext4'
    fixtures_root = scratch / 'cases'
    os.environ['R0039_CLAIM_EVIDENCE_DIR'] = str(fixtures_root)
    fixture = load_exact_fixture(scratch / 'source')

    class PosixPathRefusal(fixture.CompleteOwnerDiscriminators):
        def test_public_reader_refuses_symlink_with_pair_recoverable(self):
            roles = {'STATE': 'STATE_PREIMAGE', 'ROADMAP': 'ROADMAP_PREIMAGE'}
            initial = {role: descriptor(raw) for role, raw in self.original_pair.items()}
            self.assertEqual(set(initial), set(roles))
            original_receipt = self.fixture.receipt
            rotated = self.rotate()
            self.assertEqual(rotated['status'], 'ROTATED')
            joined = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(joined['receipt_token'], rotated['receipt_token'])
            epoch, _ = self.owner.read_epoch(self.context, 'G0002')
            prepared = epoch['prepared']
            repo = self.fixture.repo
            anchor = prepared['archive_ref']
            manifest = self.helper.verify_canonical_archive(repo, fixture.CONTROLLER, anchor,
                                                            prepared['archive_manifest_sha256'])
            preimage = self.helper._archive_preimage(repo, manifest)
            pointers = self.helper._pointers(preimage, anchor, prepared['archive_manifest_oid'],
                                             prepared['archive_manifest_sha256'], prepared['generation_id'])
            wanted = {item['role']: item for item in pointers if item['role'] in roles.values()}
            self.assertEqual(set(wanted), set(roles.values()))
            receipt_ref, _ = joined['receipt_token'].split('@')
            recorded = [self.context[name] for name in ('pointer_ref', 'marker_ref', 'invalidation_ref')]
            recorded += [original_receipt.split('@')[0], receipt_ref, anchor]
            def authority():
                rows = self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit/')
                return dict(row.split() for row in rows.splitlines())
            before = authority()
            self.assertTrue(all(ref in before for ref in recorded))
            generation = joined['state_path'].parent
            saved_generation = generation.with_name(generation.name + '-saved-fixture')
            outside = repo / 'outside-generation-fixture'
            outside.mkdir()
            sentinels = {'STATE.md': b'outside state sentinel\n', 'ROADMAP.md': b'outside roadmap sentinel\n'}
            for name, data in sentinels.items():
                (outside / name).write_bytes(data)

            generation.rename(saved_generation)
            try:
                generation.symlink_to(outside, target_is_directory=True)
                try:
                    faulted = authority()
                    self.assertEqual(faulted, before)
                    refused = self.fixture.claim('--read-current-state', fixture.CONTROLLER, 'STATE',
                                                 '--expected-pointer', rotated['pointer_token'])
                    self.assertEqual(refused.returncode, 1)
                    self.assertEqual(refused.stdout, b'')
                    self.assertEqual(authority(), faulted)
                    self.assertEqual({item.name: item.read_bytes() for item in outside.iterdir()}, sentinels)
                    recovered = {}
                    for role, archive_role in roles.items():
                        output = self.helper.resolve_typed_archive_pointer_v2(repo, wanted[archive_role])
                        self.assertEqual(output['authority_ceiling'], 'ARCHIVED_ONLY_HISTORY')
                        self.assertEqual(output['role'], archive_role)
                        self.assertEqual(output['bytes'], self.original_pair[role])
                        self.assertEqual(output['bytes'], (self.fixture.run_root / (role + '.md')).read_bytes())
                        recovered[role] = descriptor(output['bytes'])
                    self.assertTrue(generation.is_symlink())
                    self.assertEqual(generation.readlink(), outside)
                    self.assertEqual(authority(), faulted)
                finally:
                    generation.unlink()
            finally:
                saved_generation.rename(generation)
            restored = self.fixture.claim('--require-current-continuity', fixture.CONTROLLER)
            self.assertEqual(restored.returncode, 0, restored.stderr.decode())
            self.assertEqual(restored.stdout.decode().strip(), joined['receipt_token'])
            self.assertEqual(authority(), before)

            print(json.dumps({
                'fault': 'symlink_at_published_generation',
                'ordering': ['verified_G0002', 'capture_authority', 'substitute_symlink',
                             'public_path_refusal', 'typed_archive_pair_readback_while_symlink_present',
                             'restore_fixture_directory', 'verify_same_G0002_receipt'],
                'public_exit': refused.returncode,
                'public_stdout_bytes': len(refused.stdout),
                'diagnostic': refused.stderr.decode().splitlines()[-1],
                'selected_authority_refs_equal_at_all_stages': {ref: before[ref] for ref in recorded},
                'all_authority_refs_unchanged': True,
                'outside_sentinels_unchanged': True,
                'initial_preimage': initial,
                'during_fault_recovered_preimage': recovered,
                'archive_readback_authority': 'ARCHIVED_ONLY_HISTORY',
                'restored_receipt_equal': True,
            }), flush=True)

    selected = PosixPathRefusal('test_public_reader_refuses_symlink_with_pair_recoverable')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([selected]))
    entries = sorted(path.name for path in fixtures_root.iterdir())
print(json.dumps({'ok': result.wasSuccessful(), 'filesystem': filesystem, 'fixture_scratch_entries': entries,
                  'scratch_removed': not scratch.exists()}))
sys.exit(0 if result.wasSuccessful() and not entries and not scratch.exists() else 1)
