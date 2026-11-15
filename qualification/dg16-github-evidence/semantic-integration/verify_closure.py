"""Verify this new source packet; no provider operation or authority issuance."""
import hashlib
import json
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def descriptor(raw):
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def verify(base, rows):
    names=set()
    for row in rows:
        name=row['path']
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts and name not in names
        names.add(name)
        path=base/relative
        assert path.resolve(strict=True)==path and stat.S_ISREG(path.lstat().st_mode)
        raw=path.read_bytes()
        assert descriptor(raw)=={k:row[k] for k in ('bytes','sha256')},name
        if 'git_blob' in row:
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],name
    return names


pins=json.loads((HERE/'CANDIDATE_PINS.json').read_bytes())
closure_raw=(HERE/'SOURCE_CLOSURE.json').read_bytes()
assert descriptor(closure_raw)==pins['source_closure']
closure=json.loads(closure_raw)
assert len(closure['members'])==closure['member_count']
verify(ROOT,closure['members'])
names=verify(HERE,pins['members'])
assert len(names)==pins['member_count']
actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
assert actual==names|{'CANDIDATE_PINS.json'},sorted(actual^(names|{'CANDIDATE_PINS.json'}))
assert pins['authority']=='NONE' and pins['original_acceptance'] is False
print(json.dumps({'status':'EXACT_NEW_SOURCE_PACKET_VERIFIED','authority':'NONE',
    'candidate_members':len(names),'inherited_members':closure['member_count'],
    'original_acceptance':False,'old_candidate_manifest_recovered':False},sort_keys=True))
