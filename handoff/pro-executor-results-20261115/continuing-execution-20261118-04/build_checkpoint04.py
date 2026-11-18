"""Preserve completed original-scope model receiving and public source candidates."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile

BASE = Path('/workspace/scratch/2678f1e431c3')
OUT = BASE / 'checkpoint04-publication' / 'stage'
REPO = BASE / 'g2-repair-repo'
PARENT = '1586c5f1ebcf7ed5ce9d8bf7cc0fc416815ce50d'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261118-04/'


def pin(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def public_bytes(path):
    assert path.is_file() and not path.is_symlink(), path
    raw = path.read_bytes()
    assert not re.search(rb'(?:[?&]|&amp;)(?:sig|X-Amz-Signature)=', raw), path
    assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', raw), path
    assert not re.search(rb'libfile_[0-9a-f]{16,}', raw), path
    return raw


def archive(name, paths):
    members = {}
    for path in sorted(set(paths)):
        if not path.is_file() or path.is_symlink():
            continue
        assert '__pycache__' not in path.parts and path.suffix != '.pyc', path
        rel = path.relative_to(BASE).as_posix()
        assert not any(part in {'g132-private-preservation', 'recovered_inputs'} for part in path.parts)
        members[rel] = public_bytes(path)
    manifest = {'schema': 'implementaudit.public-evidence-archive.v1',
                'scope': 'Completed controlled model observations and already-public source/retained M4 bodies; no private original G132 bodies',
                'members': {name: pin(raw) for name, raw in members.items()}}
    manifest_raw = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.PAX_FORMAT) as tf:
        for rel, raw in [*members.items(), ('PUBLIC_ARCHIVE_MANIFEST.json', manifest_raw)]:
            info = tarfile.TarInfo(rel)
            info.size = len(raw)
            info.mode = 0o644
            info.mtime = 0
            tf.addfile(info, io.BytesIO(raw))
    packed = gzip.compress(stream.getvalue(), mtime=0)
    (OUT / name).write_bytes(packed)
    with tarfile.open(fileobj=io.BytesIO(packed), mode='r:gz') as tf:
        assert [m.name for m in tf.getmembers()] == [*members, 'PUBLIC_ARCHIVE_MANIFEST.json']
        for member in tf.getmembers():
            expected = manifest_raw if member.name == 'PUBLIC_ARCHIVE_MANIFEST.json' else members[member.name]
            assert tf.extractfile(member).read() == expected
    return {'name': name, 'members': len(members) + 1, **pin(packed)}


# Missing an outcome means packaging refuses; no partially received actor is published as terminal.
copies = {
    'build_checkpoint04.py': 'build_checkpoint04.py',
    'dg16-current-receiving/DG16_ORIGINAL48_G0008.json': 'DG16_ORIGINAL48_CURRENT.json',
    'g2-live/next-operation-preparation/ROOT_PREPARATION.json': 'G2_NEXT_OPERATION_PREPARATION.json',
    'dg17-continuation/CURRENT_FRONTIER_ROOT_G0008.json': 'DG17_CURRENT_FRONTIER.json',
    'dg17-continuation/causal-observation-20261118/ROOT_ORIGINAL_RECEIVING.json': 'DG17_P09_N08_M07_ROOT_RECEIVING.json',
    'dg17-model-receiving/CAUSAL_COBALT_BASELINE_RECEIVING.json': 'DG17_CAUSAL_BASELINE_RECEIVING.json',
    'dg17-model-receiving/CAUSAL_AMBER_COMPARISON_RECEIVING.json': 'DG17_CAUSAL_COMPARISON_RECEIVING.json',
    'dg17-model-receiving/M08_INITIAL_PACKET_RECEIVING.json': 'DG17_M08_INITIAL_GAP.json',
    'dg17-model-receiving/M08_R2_PACKET_RECEIVING.json': 'DG17_M08_REPAIRED_PACKET_RECEIVING.json',
    'dg17-model-receiving/M08_WILLOW_BASELINE_RECEIVING.json': 'DG17_M08_BASELINE_RECEIVING.json',
    'dg17-model-receiving/M08_MAPLE_COMPARISON_RECEIVING.json': 'DG17_M08_COMPARISON_RECEIVING.json',
    'dg17-continuation/maintenance-observation-20261118-r2/ROOT_ORIGINAL_RECEIVING.json': 'DG17_M08_ROOT_RECEIVING.json',
    'g132-m4-join-review/REPORT.md': 'G132_M4_JOIN_V1_GAP_REPORT.md',
    'g132-m4-join-review/v2/REPORT.md': 'G132_M4_JOIN_V2_REVIEW.md',
    'g132-continuation/ROOT_M4_JOIN_V2_RECEIVING.json': 'G132_M4_JOIN_ROOT_RECEIVING.json',
    'g132-root-path/review-packet-hosted-validation-v1/HOSTED_VALIDATOR_INTERFACE.md': 'G132_READONLY_VALIDATOR_INTERFACE.md',
    'checkpoint03-publication/REMOTE_PUBLICATION_RECEIVING.json': 'CHECKPOINT03_REMOTE_RECEIVING.json',
    'checkpoint04-publication/CURRENT_STATE.md': 'CURRENT_STATE.md',
    'checkpoint04-publication/README.md': 'README.md',
}
for rel in copies:
    assert (BASE / rel).is_file(), rel
OUT.mkdir(parents=True, exist_ok=False)
for source, name in copies.items():
    (OUT / name).write_bytes(public_bytes(BASE / source))

dg17 = BASE / 'dg17-continuation'
model_paths = []
for rel in ['causal-observation-20261118', 'maintenance-observation-20261118',
            'maintenance-observation-20261118-r2', 'maintenance-alias-red',
            'maintenance-alias-v2-red', 'maintenance-alias-v2-red-corrected',
            'maintenance-alias-v2-green', 'maintenance-r2-repair', 'receiving',
            'retained-root-scopes']:
    model_paths.extend((dg17 / rel).rglob('*'))
model_paths.extend((BASE / 'dg17-model-receiving').rglob('*'))
model_paths += [dg17 / name for name in ['REPORT.md', 'CURRENT_FRONTIER.json',
                'CURRENT_FRONTIER_ROOT_G0007.json', 'CURRENT_FRONTIER_ROOT_G0008.json',
                'prepare_maintenance_packet.py', 'prepare_maintenance_packet_r2.py',
                'test_workbench_immutable_aliases.py', 'test_workbench_immutable_aliases_v2.py',
                'check_maintenance_workbench.py', 'M08_DESIGN.md',
                'receive_causal_packet.py', 'receive_n07.py', 'receive_retained.py',
                'FINAL_VERIFICATION.json', 'inputs/issue-211-current.md',
                'inputs/issue-211-comments-current.json']]
g132_paths = []
for rel in ['review-packet-m4-join-v1', 'review-packet-m4-join-v2', 'review-packet-hosted-validation-v1']:
    g132_paths.extend((BASE / 'g132-root-path' / rel).rglob('*'))
g132_paths.extend((BASE / 'g132-m4-join-review').rglob('*'))
g132_paths += [BASE / 'g132-continuation/ROOT_M4_JOIN_V2_RECEIVING.json']
archives = [archive('dg17-model-observations-and-receiving.tar.gz', model_paths),
            archive('g132-public-source-candidates-and-review.tar.gz', g132_paths)]

manifest = {'schema': 'implementaudit.successor-checkpoint04.v1', 'parent': PARENT,
            'prefix': PREFIX, 'archives': archives,
            'files': {p.name: pin(p.read_bytes()) for p in sorted(OUT.iterdir())},
            'prior_bytes_preserved': True, 'private_original_G132_bodies_published': False,
            'whole_programme_or_cell_awards': False}
(OUT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
env = os.environ.copy()
env['GIT_INDEX_FILE'] = str(OUT.parent / 'publication.index')
subprocess.run(['git', 'read-tree', PARENT], cwd=REPO, env=env, check=True)
base_tree = subprocess.check_output(['git', 'rev-parse', PARENT + '^{tree}'], cwd=REPO, text=True).strip()
rows = []
for p in sorted(OUT.iterdir()):
    data = p.read_bytes()
    sha = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'], cwd=REPO, input=data).decode().strip()
    path = PREFIX + p.name
    subprocess.run(['git', 'update-index', '--add', '--cacheinfo', '100644,' + sha + ',' + path], cwd=REPO, env=env, check=True)
    rows.append({'path': path, 'local_path': str(p), 'git_blob': sha, 'mode': '100644', **pin(data)})
subprocess.run(['git', 'diff', '--cached', '--check', PARENT], cwd=REPO, env=env, check=True)
delta = subprocess.check_output(['git', 'diff', '--cached', '--name-status', PARENT], cwd=REPO, env=env, text=True)
assert all(line.startswith('A\t' + PREFIX) for line in delta.splitlines())
assert len(delta.splitlines()) == len(rows)
tree = subprocess.check_output(['git', 'write-tree'], cwd=REPO, env=env, text=True).strip()
result = {'schema': 'implementaudit.exact-additive-publication.v1', 'parent': PARENT,
          'base_tree': base_tree, 'tree': tree, 'files': rows, 'delta': delta}
(OUT.parent / 'PUBLICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'tree': tree, 'archives': archives}, indent=2))
