"""Two declared canonical-output artifact roles, received in the same job.

This is a narrow capture/reader for the existing pending-fixture producers. It
does not inspect arbitrary scratch state or alter the original tests. Anonymous
fixture work is not promoted to a new internal-state equivalence requirement.
"""
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat

LIMITS = {'file_bytes': 16 * 1024**2, 'total_bytes': 64 * 1024**2,
          'entries': 4096, 'depth': 32, 'manifest_bytes': 16 * 1024**2}
ROLES = ('pending_durability', 'pending_loader')
PREFIXES = {'pending_durability': 'cognition-pending-durability-', 'pending_loader': 'pending-loader-'}
SCOPES = {'pending_durability': 'PORTABLE_ACTUAL_OWNER_CLI_PROCESS_CRASH_ONLY',
          'pending_loader': 'constructed.pending-stored-loader-qualification.v1'}
SESSION = 'portable-pending-session'
SESSION_SHA = hashlib.sha256(SESSION.encode()).hexdigest()
PENDING_NAME = 'constructed/store/compaction-audits-v1/' + SESSION_SHA + '/pending.json'


class Refusal(ValueError):
    pass


def demand(value, code):
    if not value:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value, *, indent=None, sort_keys=True, newline=True):
    return (json.dumps(value, indent=indent, sort_keys=sort_keys, allow_nan=False) + ('\n' if newline else '')).encode()


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            demand(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def documents(raw):
    """Read only complete column-zero JSON documents; preserve all other bytes."""
    text = raw.decode('utf-8', 'surrogateescape')
    decoder = json.JSONDecoder()
    for found in re.finditer(r'(?m)^\{', text):
        try:
            _, end = decoder.raw_decode(text, found.start())
            wire = text[found.start():end].encode('utf-8', 'surrogateescape')
            value = strict(wire)
        except (ValueError, UnicodeError):
            continue
        start_bytes = len(text[:found.start()].encode('utf-8', 'surrogateescape'))
        yield start_bytes, start_bytes + len(wire), value


def reports(raw, *, complete):
    selected = {}
    for start, end, value in documents(raw):
        role = ('pending_durability' if value.get('scope') == SCOPES['pending_durability'] else
                'pending_loader' if value.get('schema') == SCOPES['pending_loader'] else None)
        if role is None:
            # No unknown declared evidence directory gains an alias or an
            # unexamined authority-bearing artifact reference.
            demand(not any(key in value and isinstance(value[key], str) and value[key].startswith('/')
                           for key in ('evidence_dir', 'evidence_directory', 'artifact_path', 'report_path')),
                   'UNKNOWN_CANONICAL_ARTIFACT_REFERENCE')
            continue
        demand(role not in selected, 'DUPLICATE_PENDING_REPORT')
        demand(raw[start:end] == encode(value, newline=False), 'PENDING_STDOUT_JSON_ENCODING')
        root = value.get('evidence_dir')
        demand(type(root) is str and re.fullmatch('/tmp/' + PREFIXES[role] + '[a-z0-9_]{8}', root),
               'PENDING_ARTIFACT_ROOT_ROLE')
        if complete:
            demand(value.get('result') == 'PASS' and value.get('source_unchanged') is True and
                   value.get('authority') == 'NONE' and value.get('host_activation_proven') is False,
                   'PENDING_REPORT_NOT_COMPLETE')
        selected[role] = {'root': root, 'report': value, 'stdout_span': [start, end],
                          'stdout_report': desc(raw[start:end])}
    demand(not complete or set(selected) == set(ROLES), 'PENDING_REPORT_POPULATION')
    return selected


def census(root, owner, *, retain=False):
    """Reuse the maintained no-follow/private-directory custody primitives.

    These new roles use the existing 16 MiB/64 MiB/4096/depth32 data bounds.
    The maintained capsule's original limits are neither changed nor replaced.
    """
    root = Path(root)
    descriptor = owner._capture_directory(root)
    entries, buffers, total = {}, {}, 0

    def visit(fd, relative, depth):
        nonlocal total
        demand(depth <= LIMITS['depth'] and len(entries) < LIMITS['entries'], 'EXTERNAL_NAMESPACE_BOUND')
        before = os.fstat(fd)
        demand(before.st_uid == os.geteuid(), 'EXTERNAL_DIRECTORY_OWNER')
        names = owner._capture_names(fd, LIMITS['entries'] - len(entries))
        entries[relative] = {'kind': 'DIRECTORY', 'stamp': owner._capture_stamp(before), 'members': names}
        for name in names:
            relative_child = name if relative == '.' else relative + '/' + name
            demand(len(os.fsencode(relative_child)) <= 4096 and len(entries) < LIMITS['entries'], 'EXTERNAL_NAMESPACE_BOUND')
            before_child = os.stat(name, dir_fd=fd, follow_symlinks=False)
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            if stat.S_ISDIR(before_child.st_mode):
                child = os.open(name, flags | os.O_DIRECTORY, dir_fd=fd)
                try:
                    demand(owner._capture_stamp(before_child) == owner._capture_stamp(os.fstat(child)), 'EXTERNAL_DIRECTORY_CHANGED')
                    visit(child, relative_child, depth + 1)
                finally:
                    os.close(child)
            else:
                demand(stat.S_ISREG(before_child.st_mode) and before_child.st_nlink == 1 and
                       before_child.st_uid == os.geteuid() and not before_child.st_mode & 0o6000,
                       'EXTERNAL_FILE_KIND_OR_OWNER')
                total += before_child.st_size
                demand(0 <= before_child.st_size <= LIMITS['file_bytes'] and total <= LIMITS['total_bytes'],
                       'EXTERNAL_BYTE_BOUND')
                child = os.open(name, flags, dir_fd=fd)
                try:
                    opened = os.fstat(child)
                    demand(owner._capture_stamp(before_child) == owner._capture_stamp(opened), 'EXTERNAL_FILE_CHANGED')
                    chunks, acquired, digest = [], 0, hashlib.sha256()
                    while acquired <= opened.st_size:
                        chunk = os.read(child, min(1024 * 1024, opened.st_size + 1 - acquired))
                        if not chunk:
                            break
                        acquired += len(chunk); digest.update(chunk)
                        if retain:
                            chunks.append(chunk)
                    demand(acquired == opened.st_size and owner._capture_stamp(opened) == owner._capture_stamp(os.fstat(child)),
                           'EXTERNAL_BYTES_CHANGED')
                    entries[relative_child] = {'kind': 'FILE', 'stamp': owner._capture_stamp(opened), 'sha256': digest.hexdigest()}
                    if retain:
                        buffers[relative_child] = b''.join(chunks)
                finally:
                    os.close(child)
            demand(owner._capture_stamp(before_child) == owner._capture_stamp(os.stat(name, dir_fd=fd, follow_symlinks=False)),
                   'EXTERNAL_NAMED_MEMBER_CHANGED')
        demand(names == owner._capture_names(fd, LIMITS['entries']) and
               owner._capture_stamp(before) == owner._capture_stamp(os.fstat(fd)), 'EXTERNAL_DIRECTORY_CHANGED')

    try:
        owner._capture_private(descriptor)
        visit(descriptor, '.', 0)
        demand(owner._capture_stamp(os.fstat(descriptor)) == owner._capture_stamp(root.lstat()), 'EXTERNAL_ROOT_CHANGED')
        value = {'entries': entries, 'total_bytes': total, 'limits': LIMITS}
        demand(len(encode(value)) <= LIMITS['manifest_bytes'], 'EXTERNAL_MANIFEST_BOUND')
        return value, buffers
    finally:
        os.close(descriptor)


def store_tree(target, observed, buffers):
    demand(not target.exists(), 'NO_REPEAT_EXTERNAL_CAPTURE')
    target.mkdir(mode=0o700)
    for relative, row in sorted(observed['entries'].items(), key=lambda x: (x[0].count('/'), x[0])):
        if relative == '.':
            continue
        path = target / relative
        if row['kind'] == 'DIRECTORY':
            path.mkdir(mode=0o700)
        else:
            raw = buffers[relative]
            demand(desc(raw) == {'bytes': row['stamp']['bytes'], 'sha256': row['sha256']}, 'EXTERNAL_BUFFER_BINDING')
            with path.open('xb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        path.chmod(stat.S_IMODE(row['stamp']['mode']))


def capture_declared(raw_stdout, destination, owner, *, complete):
    demand(not destination.exists(), 'NO_REPEAT_EXTERNAL_CAPTURE')
    destination.mkdir(mode=0o700)
    selected = reports(raw_stdout, complete=complete)
    result = {'schema': 'dg16.full-declared-artifact-capture.v1', 'scope': 'SAME_JOB_PENDING_FIXTURE_OUTPUTS_ONLY',
              'stdout': desc(raw_stdout), 'roles': {}, 'complete': complete}
    total = 0
    for role in ROLES:
        if role not in selected:
            continue
        item = selected[role]; root = Path(item['root'])
        before, buffers = census(root, owner, retain=True)
        total += before['total_bytes']
        demand(total <= LIMITS['total_bytes'], 'EXTERNAL_COMBINED_BYTE_BOUND')
        demand('report.json' in buffers and buffers['report.json'] == encode(item['report'], indent=2),
               'PENDING_REPORT_FILE_BINDING')
        store_tree(destination / role, before, buffers)
        after, _ = census(root, owner)
        demand(before == after, 'EXTERNAL_ORIGINAL_CHANGED_DURING_CAPTURE')
        retained, _ = census(destination / role, owner)
        result['roles'][role] = {**item, 'original_census': before, 'retained_census': retained}
    result['total_bytes'] = total
    raw = encode(result, indent=2)
    demand(len(raw) <= LIMITS['manifest_bytes'], 'EXTERNAL_CAPTURE_MANIFEST_BOUND')
    with (destination / 'CAPTURE.json').open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return result


def container_fence(destination, owner):
    """Bind the exact outer container without adding it to a role's byte cap."""
    descriptor = owner._capture_directory(destination)
    try:
        owner._capture_private(descriptor)
        before = owner._capture_stamp(os.fstat(descriptor))
        names = owner._capture_names(descriptor, len(ROLES) + 2)
        demand(names == sorted(['CAPTURE.json', *ROLES]), 'EXTERNAL_CONTAINER_POPULATION')
        members = {}
        for name in names:
            observed = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            demand(observed.st_uid == os.geteuid() and not observed.st_mode & 0o6000 and
                   (stat.S_ISREG(observed.st_mode) and observed.st_nlink == 1 if name == 'CAPTURE.json'
                    else stat.S_ISDIR(observed.st_mode)), 'EXTERNAL_CONTAINER_MEMBER_KIND')
            members[name] = owner._capture_stamp(observed)
        demand(names == owner._capture_names(descriptor, len(ROLES) + 2) and
               before == owner._capture_stamp(os.fstat(descriptor)) == owner._capture_stamp(destination.lstat()),
               'EXTERNAL_CONTAINER_CHANGED')
        return {'root': before, 'members': members}
    finally:
        os.close(descriptor)


def receive_declared(raw_stdout, destination, owner):
    container = container_fence(destination, owner)
    raw = owner.retained_bytes(destination, 'CAPTURE.json')[0]
    value = strict(raw)
    demand(set(value) == {'schema', 'scope', 'stdout', 'roles', 'complete', 'total_bytes'} and
           value['schema'] == 'dg16.full-declared-artifact-capture.v1' and value['complete'] is True and
           value['scope'] == 'SAME_JOB_PENDING_FIXTURE_OUTPUTS_ONLY' and value['stdout'] == desc(raw_stdout),
           'EXTERNAL_CAPTURE_ENVELOPE')
    selected = reports(raw_stdout, complete=True)
    demand(set(value['roles']) == set(selected) == set(ROLES), 'EXTERNAL_CAPTURE_POPULATION')
    received = {}
    for role in ROLES:
        row = value['roles'][role]
        demand({k: row[k] for k in selected[role]} == selected[role] and
               set(row) == set(selected[role]) | {'original_census', 'retained_census'}, 'EXTERNAL_ROLE_BINDING')
        original, originals = census(Path(row['root']), owner, retain=True)
        retained, buffers = census(destination / role, owner, retain=True)
        demand(original == row['original_census'] and retained == row['retained_census'] and originals == buffers,
               'EXTERNAL_PHYSICAL_OR_BYTE_READBACK')
        demand(buffers['report.json'] == encode(row['report'], indent=2), 'EXTERNAL_REPORT_READBACK')
        received[role] = {'root': row['root'], 'report': row['report'], 'files': buffers,
                          'namespace': {name: {'kind': entry['kind'], 'mode': stat.S_IMODE(entry['stamp']['mode'])}
                                        for name, entry in original['entries'].items()},
                          'original_census': original, 'retained_census': retained}
    demand(owner.retained_bytes(destination, 'CAPTURE.json')[0] == raw, 'EXTERNAL_ENVELOPE_CHANGED')
    demand(container_fence(destination, owner) == container, 'EXTERNAL_CONTAINER_CHANGED')
    demand(sum(r['original_census']['total_bytes'] for r in received.values()) == value['total_bytes'] <= LIMITS['total_bytes'],
           'EXTERNAL_AGGREGATE_READBACK')
    return received, {'manifest': desc(raw), 'container': container, 'roles': len(received), 'bytes': value['total_bytes'],
                      'same_original_and_retained_censuses': True, 'scope': 'SAME_JOB_PHYSICAL_READBACK_NO_NATIVE_AUTHORITY'}
