from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import zipfile

BASE = Path('/workspace/scratch/2678f1e431c3')
REPO = BASE / 'recovery-repo'
OUT = BASE / 'recovery-receiving-publication08-r2'
STAGE = OUT / 'stage'
PARENT = '101a0f9a0083decfc9e6eb4d959a7693314cc3fa'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261118-08/'
CHUNK = 393216


def digest(b):
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def git(*args, env=None):
    return subprocess.check_output(['git', '-C', str(REPO), *args], env=env)


def scan(name, b):
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        return
    patterns = {
        'github_credential': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
        'actual_private_key_body': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=\r\n]{40,}-----END',
        'signed_url': r'https?://[^\s\"\x27<>]*[?&](?:X-Amz-Signature|sig|token)=[^\s\"\x27<>]+',
    }
    for kind, pattern in patterns.items():
        if re.search(pattern, s):
            raise AssertionError({'source': name, 'credential_pattern': kind})


def validate_zip(raw, expected=None):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) == len({x.casefold() for x in names})
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            assert not p.is_absolute() and '..' not in p.parts and str(p) == item.filename
            assert not item.flag_bits & 1
            mode = item.external_attr >> 16
            assert not stat.S_ISLNK(mode)
            assert not item.is_dir()
            body = z.read(item)
            scan(item.filename, body)
            if expected is not None:
                assert item.filename in expected
                assert digest(body) == expected[item.filename]
        if expected is not None:
            assert set(names) == set(expected)
        assert z.testzip() is None
        return len(names)


assert not OUT.exists(), 'Refuse overwriting publication preparation'
OUT.mkdir()
STAGE.mkdir()
assert git('rev-parse', PARENT + '^{tree}').decode().strip() == 'fe223bf1c827cce57fcce26998de7fcef2aaca8d'
archive_records = []
sources = []


def copy(name, source):
    source = Path(source)
    b = source.read_bytes()
    scan(str(source), b)
    assert not (STAGE / name).exists()
    (STAGE / name).write_bytes(b)
    sources.append({'output': name, 'source': str(source), **digest(b)})


def add_archive(name, raw, members, source):
    record = {'name': name, **digest(raw), 'members': members, 'source': source, 'transport_parts': []}
    if len(raw) <= CHUNK:
        (STAGE / name).write_bytes(raw)
    else:
        for i in range(0, len(raw), CHUNK):
            piece = raw[i:i+CHUNK]
            part = name + '.part' + str(i // CHUNK + 1).zfill(3)
            (STAGE / part).write_bytes(piece)
            record['transport_parts'].append({'name': part, **digest(piece)})
    archive_records.append(record)


mr = BASE / 'recovered-dg17-receiving'
mm = json.loads((mr / 'MANIFEST.json').read_text())
names = [x['path'] for x in mm['members']] + ['MANIFEST.json', 'SEAL.json']
expected = {n: digest((mr / n).read_bytes()) for n in names}
bio = io.BytesIO()
with zipfile.ZipFile(bio, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n in sorted(names):
        p = mr / n
        b = p.read_bytes()
        assert digest(b) == expected[n]
        scan(n, b)
        info = zipfile.ZipInfo(n, (1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = (stat.S_IFREG | stat.S_IMODE(p.stat().st_mode)) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, b)
raw = bio.getvalue()
add_archive('dg17-recovered-independent-receiving.zip', raw, validate_zip(raw, expected), 'Complete sealed receiver; original source/observations are data')
for n, d in expected.items():
    assert digest((mr / n).read_bytes()) == d, n

pr = BASE / 'recovered-public-probe-receiving'
pm = json.loads((pr / 'MANIFEST.json').read_text())
pn = [x['path'] for x in pm['files']] + ['MANIFEST.json', 'SEAL.json']
pe = {n: digest((pr / n).read_bytes()) for n in pn}
raw = (pr / 'recovered-public-probe-receiving.zip').read_bytes()
assert digest(raw) == {'bytes': 1466565, 'sha256': 'c7074f699f714eabe39331b24fdbd15260dafc1ca80e3872ba5051e74aedd8f2'}
add_archive('g132-recovered-public-probe-receiving.zip', raw, validate_zip(raw, pe), 'Byte-exact independently delivered sealed receiver ZIP')
for n, d in pe.items():
    assert digest((pr / n).read_bytes()) == d, n

hp = BASE / 'dg17-exact-host-recovery-preparation'
raw = (hp / 'DG17_EXACT_A297_HOST_SOURCE_PACKET.tar.gz').read_bytes()
assert digest(raw) == {'bytes': 310326, 'sha256': 'c73b6fb499a57c5e4127d549916c19518af9d8a8a4e64faadbe5d9918e7fcb04'}
with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tf:
    names = []
    for item in tf.getmembers():
        p = PurePosixPath(item.name)
        assert not p.is_absolute() and '..' not in p.parts and str(p) == item.name
        assert item.isfile() and not item.issym() and not item.islnk()
        names.append(item.name)
        scan(item.name, tf.extractfile(item).read())
    assert len(names) == len(set(names))
add_archive('dg17-exact-a297-host-UNISSUED-source.tar.gz', raw, len(names), 'Frozen prospective source only; independent review and launch remain outstanding')

ev = BASE / 'recovery-evidence'
for n in ['ROOT_M14_RECOVERED_ADJUDICATION_G0001.json', 'ROOT_PUBLIC_PROBE_RECOVERED_RECEIVING_G0001.json', 'ROOT_RECEIVER_INTEGRITY_G0001.json', 'UNAVAILABLE_G000E_CATALOG.json', 'ACTUAL_CONTINUITY_G0001.json', 'LIVE_PROVIDER_READBACK_2202.json', 'LOCAL_RECOVERY_INITIALIZATION.json', 'DG17_CURRENT_FRONTIER_RECOVERED_G0001.json', 'DG18_CURRENT_CAPABILITY_QUERY.json', 'DG18_ROOT_CONTINUATION_G0001.json']:
    copy(n, ev / n)
root = REPO / '.IMPLEMENTAUDIT/runs/dg16-dg18-recovered-custody-20261118-Zsj2RI'
for src, dst in [('STATE.md', 'CURRENT_STATE.md'), ('ROADMAP.md', 'CURRENT_ROADMAP.md'), ('PROGRESS_G0001.jsonl', 'CURRENT_PROGRESS.jsonl'), ('authorization-record.md', 'OWNER_AUTHORITY_RECORD.md')]:
    copy(dst, root / src)
for src, dst in [('REPORT.md', 'DG17_EXACT_HOST_SOURCE_REPORT.md'), ('RESULTS.json', 'DG17_EXACT_HOST_SOURCE_RESULTS.json'), ('SEALED_PACKET.json', 'DG17_EXACT_HOST_SOURCE_SEAL.json')]:
    copy(dst, hp / src)
copy('RECOVERY_STATUS_REMOTE_RECEIVING.json', BASE / 'recovery-publication08/REMOTE_POSTUPDATE.json')
copy('reassemble_archives.py', REPO / 'handoff/pro-executor-results-20261115/continuing-execution-20261118-06/reassemble_archives.py')
copy('build_recovered_receiving08_r2.py', Path(__file__))
copy('build_recovered_receiving08_attempt001.py', BASE / 'build_recovered_receiving08.py')
copy('INITIAL_DIFF_CHECK.json', BASE / 'recovery-receiving-publication08/DIFF_CHECK.json')
exception = {'schema': 'implementaudit.exact-evidence-whitespace-exception.v1', 'path': PREFIX + 'LIVE_PROVIDER_READBACK_2202.json', 'bytes': 84003, 'sha256': 'f075bb2bf53a67b25306a0369aafb724f4a4cf8caeeafa330cf125979d9db6c1', 'condition': 'Exactly one extra final newline in Root-generated captured-response envelope', 'original_failure': 'Initial full default git diff --check exited2 for only this blank-at-EOF diagnostic', 'countermeasure': 'Preserve evidence bytes; default check every other path and apply only -blank-at-eof to this exact path/hash', 'original_requirements_or_source_changed': False, 'original_failed_attempt_preserved': True}
eb = (STAGE / 'LIVE_PROVIDER_READBACK_2202.json').read_bytes()
assert digest(eb) == {k: exception[k] for k in ('bytes', 'sha256')}
assert eb.endswith(b'\n\n') and not eb.endswith(b'\n\n\n')
assert isinstance(json.loads(eb), dict)
(STAGE / 'PACKAGING_ABNORMALITY.json').write_text(json.dumps(exception, indent=2) + '\n')

readme = '''# Continuing DG16–DG18: recovered evidence and original scope decisions

This is an additive continuation of checkpoint06 and recovery notice101a0f9a0083decfc9e6eb4d959a7693314cc3fa. It preserves every prior path. The missing checkpoint07 tree66c5fae658cdabc212ffcc88a28f39ec5db76985 is not reconstructed or silently replaced.

## Current decisions

- Original M14 finite mutation discriminator is accepted at its actual selected-source/model-policy/file-effect layer after fresh independent receiving of the genuine Cedar/Alder observations and direct reading of the original clause. This supplies no universal, installed whole-governor, native-host or whole-DG17 award. B01/H06 original literal model-policy awards remain supported. N09's specific forcing scenario remains unexercised; M09 survives. Later M03 completed-survivor history is preserved, with its original G000E bodies unavailable and no replay.
- Actual G132 public probe44352064942 and artifact14449770076 are freshly received byte-exact. Root accepts ordinary public hosted UID0 custody and public HTTP fixture transport only. OriginalG1/G3, originalM2, native model identity, issuer grants and protected execution remain unawarded. The receiving report explicitly separates recovered projections from missing complete-source provenance; a separately ongoing provenance addendum is outside this frozen packet.
- DG17 original36 cases14 mutation families17 terminal clauses and DG18 original14 criteria/amendments remain unchanged. DG18 W-FULL/C11/occurrence/cold scopes are preserved; no new authentic OR/C02 input or historicalN1 exception exists.

## New ordinary source preparation

The exact-a297 hosted-helper source packet is included as UNISSUED PREPARATION only. It has four additions, a distinct disposable fixture, and no executed helper/controller/hosted/model/native operation. Genuine independent review and Root receiving must precede an ordinary launch. The active N10 prospective design is not included or described as ready.

## Recovery and unknown effects

The prior physical workspace and local G000E receipt could not be restored. New controllerdg16-dg18-recovery-20261118 has actual localG0001 receipt007f9c33a3d9f369baab6d4e63fb4db2c82c788b. This is prospective local custody, not recreated historical evidence. CURRENT_STATE/ROADMAP preserve the exact receipt-bound recovery anchor; CURRENT_PROGRESS records later receiving without rewriting that anchor.

The two earlier first-blob requests remain UNKNOWN. The exact old blob returned404 and results branch remained checkpoint06 at reconciliation; neither is a cancellation proof. The separate one-file recovery notice was then actually published and read back at101a0f9a. OriginalG132625f310d/301aeec remain UNKNOWN_NO_REPLAY. G2's timely control remains preserved, terminal hosted consumption failed, M2 unawarded; no late control or full-pair relaunch occurred. No merge, release, tag or issue closure.

## Complete payload and verification

MANIFEST.json pins every transport file and each full archive. Run reassemble_archives.py to verify/reassemble parts without extracting. The DG17 receiver archive contains all521files (519manifested plus manifest/seal); the G132 receiver archive contains all229files (227manifested plus manifest/seal). The new exact-host source TAR is byte-exact and still unissued. Source caches are excluded; exact public objects/source copies and proof reports are retained. No private original input, credential or signed download URL is included.

The builder read every archive member, checked exact hashes/CRC or TAR type/path safety, scanned actual credential/key-body/signed-URL patterns, and reread input snapshots after packing. Public source validation header literals are data and contain no private key body. Receiving code was not substituted for original operations; original code and actors were not replayed.
'''
(STAGE / 'README_RECOVERED_EVIDENCE.md').write_text(readme)
files = []
for p in sorted(STAGE.iterdir()):
    b = p.read_bytes()
    files.append({'name': p.name, **digest(b)})
manifest = {'schema': 'implementaudit.public-recovered-receiving-checkpoint.v1', 'parent': PARENT, 'scope': 'Additive current receiving, unavailable history, unissued source preparation; no replay', 'files': files, 'archives': archive_records, 'source_copies': sources, 'original_effects_replayed': False, 'private_inputs_included': False}
(STAGE / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
env = os.environ.copy()
env['GIT_INDEX_FILE'] = str(OUT / 'publication.index')
subprocess.run(['git', '-C', str(REPO), 'read-tree', PARENT], env=env, check=True)
entries = []
for p in sorted(STAGE.iterdir()):
    b = p.read_bytes()
    blob = git('hash-object', '-w', str(p)).decode().strip()
    assert blob == hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
    path = PREFIX + p.name
    prior = subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', PARENT + ':' + path], capture_output=True)
    assert prior.returncode != 0, 'No existing path overwrite: ' + path
    subprocess.run(['git', '-C', str(REPO), 'update-index', '--add', '--cacheinfo', '100644', blob, path], env=env, check=True)
    entries.append({'path': path, 'name': p.name, 'mode': '100644', 'type': 'blob', 'sha': blob, **digest(b)})
check = subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--check', PARENT], env=env, capture_output=True, text=True)
expected_diagnostic = exception['path'] + ':155: new blank line at EOF.\n'
assert check.returncode == 2 and check.stdout == expected_diagnostic and check.stderr == ''
ordinary = subprocess.run(['git', '-C', str(REPO), 'diff', '--cached', '--check', PARENT, '--', '.', ':(exclude)' + exception['path']], env=env, capture_output=True, text=True)
allowed = subprocess.run(['git', '-C', str(REPO), '-c', 'core.whitespace=-blank-at-eof', 'diff', '--cached', '--check', PARENT, '--', exception['path']], env=env, capture_output=True, text=True)
assert ordinary.returncode == allowed.returncode == 0
assert digest((STAGE / 'LIVE_PROVIDER_READBACK_2202.json').read_bytes()) == {k: exception[k] for k in ('bytes', 'sha256')}
(OUT / 'DIFF_CHECK.json').write_text(json.dumps({'default_exit': check.returncode, 'default_stdout': check.stdout, 'default_stderr': check.stderr, 'ordinary_other_paths_exit': ordinary.returncode, 'exact_exception_path_exit': allowed.returncode, 'exception': exception, 'qualified_packaging_check': 'PASS_WITH_RECORDED_BYTE_EXACT_EOF_EXCEPTION'}, indent=2) + '\n')
delta = git('diff', '--cached', '--name-status', PARENT, env=env).decode().splitlines()
assert len(delta) == len(entries) and all(x.startswith('A\t' + PREFIX) for x in delta)
tree = git('write-tree', env=env).decode().strip()
publication = {'schema': 'implementaudit.exact-additive-evidence-publication.v1', 'parent': PARENT, 'base_tree': git('rev-parse', PARENT + '^{tree}').decode().strip(), 'tree': tree, 'branch': 'engineering/pro-executor-original-completion-20261115', 'additions': entries, 'total_bytes': sum(x['bytes'] for x in entries), 'force': False, 'root_continuity': '007f9c33a3d9f369baab6d4e63fb4db2c82c788b', 'scope': manifest['scope'], 'archives': archive_records}
(OUT / 'PUBLICATION.json').write_text(json.dumps(publication, indent=2) + '\n')
print(json.dumps({'parent': PARENT, 'tree': tree, 'additions': len(entries), 'total_bytes': publication['total_bytes'], 'archives': archive_records}, indent=2))
