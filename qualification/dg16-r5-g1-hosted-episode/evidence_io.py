"""Finite physical byte readers. No native, subprocess, network or authority API."""
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import stat


class Refusal(ValueError):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'EVIDENCE_DUPLICATE_KEY')
            result[key] = value
        return result
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('EVIDENCE_NONFINITE_JSON')))


def stamp(value):
    return [value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns, value.st_uid, value.st_gid]


def safe_name(name):
    path = PurePosixPath(name)
    need(type(name) is str and 0 < len(name) <= 4096 and not path.is_absolute()
         and str(path) == name and '..' not in path.parts and '.' not in path.parts
         and len(path.parts) <= 40, 'EVIDENCE_MEMBER_NAME')
    return name


def ancestors(path):
    result = []
    for parent in reversed(Path(path).absolute().parents):
        value = parent.lstat()
        need(stat.S_ISDIR(value.st_mode) and not parent.is_symlink(), 'EVIDENCE_PARENT_ALIAS')
        result.append([str(parent), value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid])
    return result


def file_record(path, maximum, *, body=False, require_owner=True):
    path = Path(path).absolute()
    parents = ancestors(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and (not require_owner or before.st_uid == os.geteuid()) and 0 <= before.st_size <= maximum,
         'EVIDENCE_ORDINARY_FILE_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    chunks = [] if body else None
    digest = hashlib.sha256()
    count = 0
    try:
        need(stamp(os.fstat(fd)) == stamp(before) and not os.listxattr(fd), 'EVIDENCE_OPEN_CHANGED')
        while True:
            raw = os.read(fd, min(1024 * 1024, maximum - count + 1))
            if not raw:
                break
            count += len(raw)
            need(count <= maximum, 'EVIDENCE_FILE_BOUND')
            digest.update(raw)
            if body:
                chunks.append(raw)
        need(count == before.st_size and stamp(os.fstat(fd)) == stamp(before)
             and stamp(path.lstat()) == stamp(before) and ancestors(path) == parents,
             'EVIDENCE_CLOSING_CHANGED')
    finally:
        os.close(fd)
    row = dict(bytes=count, sha256=digest.hexdigest(), mode=stat.S_IMODE(before.st_mode),
               physical=stamp(before), ancestors=parents)
    return (row, b''.join(chunks)) if body else row


def read(path, maximum=4 * 1024**2):
    return file_record(path, maximum, body=True)[1]


def read_packet(path, maximum=4 * 1024**2):
    """Pinned reviewed checkout/data input, preserving its observed owner.

    The caller must enforce its exact expected digest. Private produced/raw
    evidence uses read(), which still requires the actual process owner.
    """
    return file_record(path, maximum, body=True, require_owner=False)[1]


def write_once(path, raw, maximum=4 * 1024**2):
    need(type(raw) is bytes and len(raw) <= maximum, 'EVIDENCE_WRITE_BOUND')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            offset += os.write(fd, raw[offset:])
        os.fsync(fd)
        os.fchmod(fd, 0o400)
    finally:
        os.close(fd)
    need(read(path, maximum) == raw, 'EVIDENCE_WRITE_READBACK')
    return dict(bytes=len(raw), sha256=sha(raw))


def census(root, *, file_bytes, total_bytes, entries, depth=40):
    """Complete physical population including empty directories, no exclusions."""
    root = Path(root).absolute()
    result = {'files': {}, 'directories': {}}
    total = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        here = Path(parent)
        info = here.lstat()
        need(stat.S_ISDIR(info.st_mode) and not here.is_symlink()
             and info.st_uid == os.geteuid(), 'EVIDENCE_DIRECTORY_CUSTODY')
        name = here.relative_to(root).as_posix()
        result['directories'][name] = [info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid]
        need(len(here.relative_to(root).parts) <= depth, 'EVIDENCE_DEPTH_BOUND')
        for name in dirs:
            p = here / name
            need(not p.is_symlink() and stat.S_ISDIR(p.lstat().st_mode), 'EVIDENCE_DIRECTORY_ALIAS')
        for name in files:
            p = here / name
            key = safe_name(p.relative_to(root).as_posix())
            row = file_record(p, file_bytes)
            total += row['bytes']
            need(total <= total_bytes, 'EVIDENCE_TOTAL_BOUND')
            result['files'][key] = row
        need(len(result['files']) + len(result['directories']) <= entries, 'EVIDENCE_ENTRY_BOUND')
    result['total_bytes'] = total
    return result


def bind_bodies(root, members, *, maximum=16 * 1024**2, total=64 * 1024**2, require_owner=True):
    need(type(members) is dict and 0 < len(members) <= 4096, 'EVIDENCE_MANIFEST_POPULATION')
    result, count = {}, 0
    for name, expected in sorted(members.items()):
        safe_name(name)
        need(type(expected) is dict and set(expected) == {'bytes', 'sha256'}, 'EVIDENCE_DESCRIPTOR_SHAPE')
        need(type(expected['bytes']) is int and 0 <= expected['bytes'] <= maximum
             and type(expected['sha256']) is str and re.fullmatch('[0-9a-f]{64}', expected['sha256']),
             'EVIDENCE_DESCRIPTOR_VALUE')
        row = file_record(Path(root) / name, maximum, require_owner=require_owner)
        need({k: row[k] for k in ('bytes', 'sha256')} == expected, 'EVIDENCE_BODY_CHANGED')
        count += row['bytes']
        need(count <= total, 'EVIDENCE_TOTAL_BOUND')
        result[name] = row
    return result
