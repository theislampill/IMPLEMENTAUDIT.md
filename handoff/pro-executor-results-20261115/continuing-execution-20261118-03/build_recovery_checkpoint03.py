"""Package completed public receiving evidence; never include private G132 bodies."""
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
OUT = BASE / 'checkpoint03-publication' / 'stage'
OUT.mkdir(parents=True, exist_ok=False)
REPO = BASE / 'g2-repair-repo'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261118-03/'
PARENT = '60d3e99853215307fdff99270a037a8cee4f9658'


def pin(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def read_public(p):
    assert p.is_file() and not p.is_symlink(), p
    data = p.read_bytes()
    assert not re.search(rb'(?:[?&]|&amp;)(?:sig|X-Amz-Signature)=', data), p
    assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', data), p
    return data


def copy(source, target):
    (OUT / target).write_bytes(read_public(BASE / source))


def archive(name, paths):
    members = {}
    for p in sorted(set(paths)):
        if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix != '.pyc':
            rel = str(p.relative_to(BASE))
            assert '..' not in Path(rel).parts
            members[rel] = read_public(p)
    manifest = {'schema': 'implementaudit.public-evidence-archive.v1', 'members': {n: pin(b) for n, b in members.items()}, 'scope': 'Previously public GitHub artifacts/source and bounded non-secret new receiving evidence; no private G132 input bodies or transcripts'}
    manifest_raw = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as tf:
        for n, data in [*members.items(), ('PUBLIC_ARCHIVE_MANIFEST.json', manifest_raw)]:
            info = tarfile.TarInfo(n)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tf.addfile(info, io.BytesIO(data))
    compressed = gzip.compress(raw.getvalue(), mtime=0)
    (OUT / name).write_bytes(compressed)
    with tarfile.open(fileobj=io.BytesIO(compressed), mode='r:gz') as tf:
        assert [m.name for m in tf.getmembers()] == [*members, 'PUBLIC_ARCHIVE_MANIFEST.json']
        for m in tf.getmembers():
            data = tf.extractfile(m).read()
            assert data == (manifest_raw if m.name == 'PUBLIC_ARCHIVE_MANIFEST.json' else members[m.name])
    return {'name': name, 'members': len(members) + 1, **pin(compressed)}


copies = {
    'build_recovery_checkpoint03.py': 'build_recovery_checkpoint03.py',
    'g2-live/terminal/ROOT_TERMINAL_DECISION.json': 'G2_ROOT_TERMINAL_DECISION.json',
    'g2-live/terminal/independent/FINAL_REPORT.md': 'G2_INDEPENDENT_TERMINAL_REPORT.md',
    'g2-live/independent/REPORT.md': 'G2_ORIGINAL_LIVE_REVIEW.md',
    'g2-live/independent/ADDENDUM-20261118-LIVE-CONTROL-TRANSPORT.md': 'G2_LIVE_REVIEW_TRANSPORT_ADDENDUM.md',
    'g2-live/diagnostic/INDEPENDENT_CONTROL_TRANSPORT_DIAGNOSIS.md': 'G2_INDEPENDENT_TRANSPORT_DIAGNOSIS.md',
    'g2-live/delivery-support/original-oracle/M2_ORACLE_REPORT.md': 'G2_ORIGINAL_M2_ORACLE.md',
    'g2-repair-review/INDEPENDENT_SOURCE_REPAIR_REVIEW.md': 'G2_REPAIR_REVIEW.md',
    'g2-smoke-cold-review/FINAL.md': 'G2_TRANSPORT_SMOKE_SOURCE_REVIEW.md',
    'g2-smoke-cold-review/hosted-receiving/FINAL.md': 'G2_TRANSPORT_SMOKE_HOSTED_RECEIVING.md',
    'g2-smoke-publication/hosted/RESULT.json': 'G2_TRANSPORT_SMOKE_ACTUAL_RESULT.json',
    'g2-smoke-publication/ROOT_HOSTED_RECEIVING.json': 'G2_ROOT_TRANSPORT_RECEIVING.json',
    'dg18-continuation/FINAL_REPORT.md': 'DG18_INDEPENDENT_CURRENT_REPORT.md',
    'dg18-continuation/CURRENT_FRONTIER.json': 'DG18_CURRENT_FRONTIER.json',
    'dg18-continuation/ROOT_RECEIVING.json': 'DG18_ROOT_RECEIVING.json',
    'g132-continuation/ALL_ELEVEN_INPUTS_RECEIVING.json': 'G132_ELEVEN_INPUTS_RECOVERY_METADATA.json',
    'checkpoint-recovery/VERIFICATION.json': 'CHECKPOINT02_LOCAL_EXACT_RECEIVING.json',
    'checkpoint03-publication/CHECKPOINT02_REMOTE_RECEIVING.json': 'CHECKPOINT02_REMOTE_RECEIVING.json',
    'checkpoint03-publication/CURRENT_STATE.md': 'CURRENT_STATE.md',
    'checkpoint03-publication/README.md': 'README.md',
}
for src, dest in copies.items():
    copy(src, dest)

g2_paths = list((BASE / 'g2-live').rglob('*'))
g2_paths += list((BASE / 'g2-repair-review').rglob('*'))
g2_paths += [BASE / 'g2-hosted-smoke-candidate' / n for n in ['AUTHORING_HANDOFF.md', 'AUTHORING_PLAN.md', 'local_tests/test_transport_smoke.py', 'qualification/dg16-r5-full-g2/transport_smoke.py', '.github/workflows/g2-production-transport-smoke.yml']]
review_manifest = json.loads((BASE / 'g2-smoke-cold-review/EVIDENCE_MANIFEST.json').read_text())
for rel, expected in review_manifest.items():
    p = BASE / 'g2-smoke-cold-review' / rel
    assert pin(read_public(p)) == expected
    g2_paths.append(p)
g2_paths.append(BASE / 'g2-smoke-cold-review/EVIDENCE_MANIFEST.json')
g2_paths += list((BASE / 'g2-smoke-cold-review/hosted-receiving').rglob('*'))
g2_paths += list((BASE / 'g2-smoke-publication/hosted').rglob('*'))
g2_paths += [BASE / 'g2-smoke-publication' / n for n in ['CANDIDATE.json', 'ROOT_INTEGRATION_CHECK.json', 'ROOT_HOSTED_RECEIVING.json']]
archives = [archive('g2-recovery-and-transport-evidence.tar.gz', g2_paths), archive('dg18-current-receiving-evidence.tar.gz', list((BASE / 'dg18-continuation').rglob('*')))]

manifest = {'schema': 'implementaudit.successor-checkpoint03.v1', 'parent': PARENT, 'prefix': PREFIX, 'archives': archives, 'files': {p.name: pin(p.read_bytes()) for p in sorted(OUT.iterdir())}, 'prior_bytes_preserved': True, 'new_original_awards': [], 'private_G132_input_bodies_published': False}
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
# Preserve reviewed Markdown hard-break bytes; every other path uses the normal check.
hardbreak_reports = {
    'G2_TRANSPORT_SMOKE_HOSTED_RECEIVING.md': '9b4cb5ccd21224d51c4822c1585c5b9e4f153f378f44364f5c7fd32eaed3ea19',
    'G2_TRANSPORT_SMOKE_SOURCE_REVIEW.md': '90490a7be7b3c9653bb2f20b450d9602146cb6b321023b4667434bc104ef72dc',
}
for name, expected_sha in hardbreak_reports.items():
    assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == expected_sha
subprocess.run(['git', 'diff', '--cached', '--check', PARENT, '--', '.', *[':(exclude)' + PREFIX + n for n in hardbreak_reports]], cwd=REPO, env=env, check=True)
delta = subprocess.check_output(['git', 'diff', '--cached', '--name-status', PARENT], cwd=REPO, env=env, text=True)
assert all(line.startswith('A\t' + PREFIX) for line in delta.splitlines())
tree = subprocess.check_output(['git', 'write-tree'], cwd=REPO, env=env, text=True).strip()
result = {'schema': 'implementaudit.exact-additive-publication.v1', 'parent': PARENT, 'base_tree': base_tree, 'tree': tree, 'files': rows, 'delta': delta}
(OUT.parent / 'PUBLICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'tree': tree, 'archives': archives}, indent=2))
