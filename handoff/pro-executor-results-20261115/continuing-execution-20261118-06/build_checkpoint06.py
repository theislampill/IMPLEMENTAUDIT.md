"""Build an exact additive checkpoint from an explicit terminal evidence inventory."""
from pathlib import Path
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import zipfile

BASE = Path('/workspace/scratch/2678f1e431c3')
WORK = BASE / 'checkpoint06-publication'
REPO = BASE / 'g2-repair-repo'
PARENT = '4194fc656e9c3cc46bcd0043c21900277ca12f60'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261118-06/'
LITERAL_MARKER_SOURCE_PATHS = {
    'g132-root-path/outer-binding-v1/review-packet-outer-binding-v1/source-inputs/baseline/qualification/dg16-r5-g1-hosted-episode/carrier/carrier.py',
    'g132-root-path/outer-binding-v1/review-packet-outer-binding-v1/prepared-outer/tree/qualification/dg16-r5-g1-hosted-episode/carrier/carrier.py',
    'g132-outer-review/evidence-run2/rebuild-a/tree/qualification/dg16-r5-g1-hosted-episode/carrier/carrier.py',
    'g132-outer-review/evidence-run2/rebuild-b/tree/qualification/dg16-r5-g1-hosted-episode/carrier/carrier.py',
}


def pin(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def owned(path):
    path.relative_to(BASE)
    assert not any(x in path.parts for x in ('g132-private-preservation', 'recovered_inputs'))
    return path


def public_data(path):
    owned(path)
    assert path.is_file() and not path.is_symlink(), path
    raw = path.read_bytes()
    assert not re.search(rb'(?:[?&]|&amp;)(?:sig|X-Amz-Signature)=', raw), path
    sensitive = list(re.finditer(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', raw))
    if sensitive:
        # Exact published source validation literal; never arbitrary key material.
        assert path.relative_to(BASE).as_posix() in LITERAL_MARKER_SOURCE_PATHS, path
        assert pin(raw) == {'bytes': 42896, 'sha256': 'dedbde52ce2912cb063e0fb35ece1ab4930e294856b1dd457695393c65765c91'}, path
        assert len(sensitive) == 1 and sensitive[0].group() == b'-----BEGIN ' + b'PRIVATE KEY-----', path
        assert raw[sensitive[0].end():sensitive[0].end() + 2] == b'\\n', path
    assert not re.search(rb'libfile_[0-9a-f]{16,}', raw), path
    return raw


def collect(relative_paths):
    files, directories = {}, set()
    for rel in relative_paths:
        start = owned(BASE / rel)
        assert start.exists() or start.is_symlink(), start
        population = [start]
        if start.is_dir() and not start.is_symlink():
            population = []
            for directory, children, leaves in os.walk(start, followlinks=False):
                here = Path(directory)
                directories.add(here.relative_to(BASE).as_posix())
                for child in list(children):
                    path = here / child
                    if path.is_symlink():
                        children.remove(child)
                        population.append(path)
                population.extend(here / leaf for leaf in leaves)
        for path in population:
            key = path.relative_to(BASE).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                target = os.readlink(path)
                raw = os.fsencode(target)
                item = {'kind': 'symlink', 'target': target, 'mode': stat.S_IMODE(mode), **pin(raw)}
            else:
                assert stat.S_ISREG(mode), path
                raw = public_data(path)
                item = {'kind': 'file', 'mode': stat.S_IMODE(mode), **pin(raw)}
            if key in files:
                assert files[key] == (raw, item), key
            files[key] = (raw, item)
    return dict(sorted(files.items())), sorted(directories)


def archive(name, sources, out):
    members, directories = collect(sources)
    descriptor = {
        'schema': 'implementaudit.exact-public-evidence-archive.v2',
        'scope': 'Public source and controlled fixture evidence only; no original private G132 input bodies',
        'symlink_representation': 'ZIP Unix symlink entry contains exact link-target bytes; verification reads entries without following or extracting links',
        'directories': directories,
        'members': {key: info for key, (_, info) in members.items()},
    }
    manifest = (json.dumps(descriptor, indent=2, sort_keys=True) + '\n').encode()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive_file:
        for key, (raw, entry) in members.items():
            info = zipfile.ZipInfo(key, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            kind = stat.S_IFLNK if entry['kind'] == 'symlink' else stat.S_IFREG
            info.external_attr = (kind | entry['mode']) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive_file.writestr(info, raw)
        info = zipfile.ZipInfo('PUBLIC_ARCHIVE_MANIFEST.json', (1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive_file.writestr(info, manifest)
    packed = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(packed)) as archive_file:
        assert archive_file.namelist() == [*members, 'PUBLIC_ARCHIVE_MANIFEST.json']
        assert archive_file.testzip() is None
        for key, (raw, entry) in members.items():
            assert archive_file.read(key) == raw, key
            mode = archive_file.getinfo(key).external_attr >> 16
            assert stat.S_ISLNK(mode) == (entry['kind'] == 'symlink'), key
        assert archive_file.read('PUBLIC_ARCHIVE_MANIFEST.json') == manifest
    after_members, after_directories = collect(sources)
    assert after_members == members and after_directories == directories, 'source changed during packaging'
    part_size = 393216  # Encodes to at most 512 KiB per bounded blob request.
    parts = []
    if len(packed) > part_size:
        for number, offset in enumerate(range(0, len(packed), part_size), 1):
            part_name = name + '.part%03d' % number
            piece = packed[offset:offset + part_size]
            (out / part_name).write_bytes(piece)
            parts.append({'name': part_name, **pin(piece)})
        assert b''.join((out / part['name']).read_bytes() for part in parts) == packed
    else:
        (out / name).write_bytes(packed)
    return {'name': name, 'members': len(members) + 1,
            'regular_files': sum(v[1]['kind'] == 'file' for v in members.values()),
            'symlinks': sum(v[1]['kind'] == 'symlink' for v in members.values()),
            'directories': len(directories), 'transport_parts': parts, **pin(packed)}


def main():
    config = json.loads((WORK / 'CONFIG.json').read_text())
    assert config['parent'] == PARENT and config['prefix'] == PREFIX
    assert config['actors_terminal_and_received'] is True
    assert config['frozen_sources_and_final_reviews_only'] is True
    out = WORK / 'stage'
    assert not out.exists(), 'retain any existing stage; do not overwrite a prior attempt'
    for source in config['copies']:
        assert owned(BASE / source).is_file(), source
    out.mkdir()
    for source, name in config['copies'].items():
        assert Path(name).name == name
        (out / name).write_bytes(public_data(BASE / source))
    archives = [archive(name, sources, out) for name, sources in config['archives'].items()]
    manifest = {'schema': 'implementaudit.successor-checkpoint06.v1', 'parent': PARENT,
                'prefix': PREFIX, 'archives': archives,
                'files': {p.name: pin(p.read_bytes()) for p in sorted(out.iterdir())},
                'prior_bytes_preserved': True, 'original_private_inputs_published': False,
                'whole_programme_or_cell_awards': False}
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = str(WORK / 'publication.index')
    subprocess.run(['git', 'read-tree', PARENT], cwd=REPO, env=env, check=True)
    base_tree = subprocess.check_output(['git', 'rev-parse', PARENT + '^{tree}'], cwd=REPO, text=True).strip()
    rows = []
    for path in sorted(out.iterdir()):
        raw = path.read_bytes()
        blob = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'], cwd=REPO, input=raw).decode().strip()
        target = PREFIX + path.name
        subprocess.run(['git', 'update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + target], cwd=REPO, env=env, check=True)
        rows.append({'path': target, 'local_path': str(path), 'git_blob': blob, 'mode': '100644', **pin(raw)})
    subprocess.run(['git', 'diff', '--cached', '--check', PARENT], cwd=REPO, env=env, check=True)
    delta = subprocess.check_output(['git', 'diff', '--cached', '--name-status', PARENT], cwd=REPO, env=env, text=True)
    assert all(line.startswith('A\t' + PREFIX) for line in delta.splitlines())
    assert len(delta.splitlines()) == len(rows)
    tree = subprocess.check_output(['git', 'write-tree'], cwd=REPO, env=env, text=True).strip()
    result = {'schema': 'implementaudit.exact-additive-publication.v1', 'parent': PARENT,
              'base_tree': base_tree, 'tree': tree, 'files': rows, 'delta': delta}
    (WORK / 'PUBLICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'tree': tree, 'archives': archives}, indent=2))


if __name__ == '__main__':
    main()
