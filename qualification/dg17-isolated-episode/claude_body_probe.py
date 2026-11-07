#!/usr/bin/env python3
"""One prospective canonical8ee native governor-body delivery episode.

Control source0d/currentness remains separate. The separately reviewed parent
owns actual fresh-host/capsule/loopback/resource/effect admission. No standalone
session, persistent installation, child route, upstream provider or inference.
"""
from __future__ import annotations
import argparse
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import signal
import stat
import sys
import time
import uuid
import zipfile

CONTROL_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
CONTROL_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
PACKAGE_COMMIT = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
PACKAGE_TREE = '0da374609f7fea2463a2926f3603b976620bd10e'
PACKAGE_BYTES = 584974
PACKAGE_SHA = '18bb9d7dcb876f7c6be4340bec10dbc77f091227c24504dcecdb0b7d9853f458'
MATRIX_SHA = 'ef9cbbe7c2c277c434139080d548f0cb868ee091fe79aa96633dcd46cc86a117'
SUPPORT_SHA = '6b0303d6689a260177d40a4ed495963d33e6a0f98367140d69063846192eff70'
TRANSPORT_SHA = '2f13bfef6105d89b6c1d13fed26412e0157b75089e9a3da374a178b2fec54edc'
RUN_SECONDS = 125
NATIVE_SECONDS = 45
PUBLIC_LIMIT = 32768
STARTUP_PATHS = (
    ('HOME_DOT_CLAUDE', 'home', '.claude'),
    ('HOME_DOT_CLAUDE_JSON', 'home', '.claude.json'),
    ('HOME_CONFIG_ANTHROPIC', 'home', '.config/anthropic'),
    ('HOME_CONFIG_CLAUDE', 'home', '.config/claude'),
    ('XDG_CONFIG_ANTHROPIC', 'xdg_config', 'anthropic'),
    ('XDG_CONFIG_CLAUDE', 'xdg_config', 'claude'),
    ('CONFIG_SETTINGS', 'config', 'settings.json'),
    ('CONFIG_SETTINGS_LOCAL', 'config', 'settings.local.json'),
    ('CONFIG_DOT_CREDENTIALS', 'config', '.credentials.json'),
    ('CONFIG_CREDENTIALS', 'config', 'credentials.json'),
    ('CONFIG_MANAGED_SETTINGS', 'config', 'managed-settings.json'),
    ('CONFIG_MANAGED_MCP', 'config', 'managed-mcp.json'),
    ('CONFIG_PLUGINS', 'config', 'plugins'),
    ('CONFIG_SKILLS', 'config', 'skills'),
    ('CONFIG_HOOKS', 'config', 'hooks'),
    ('CONFIG_MCP', 'config', 'mcp.json'),
    ('CONFIG_DOT_MCP', 'config', '.mcp.json'))

class Refusal(RuntimeError):
    pass

def need(ok, code):
    if not ok:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       allow_nan=False, separators=(',', ':')) + '\n').encode('ascii')

def file_identity(path, maximum, executable=False):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'NONPHYSICAL_FILE')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
         before.st_uid == os.geteuid() and not before.st_mode & 0o022 and
         before.st_size <= maximum, 'FILE_SHAPE_REFUSED')
    if executable:
        need(before.st_mode & 0o111 and not before.st_mode & 0o6000, 'BINARY_MODE_REFUSED')
        try:
            capability = os.getxattr(path, 'security.capability')
        except OSError as exc:
            need(exc.errno == errno.ENODATA, 'BINARY_CAPABILITY_UNKNOWN')
            capability = b''
        need(not capability, 'BINARY_CAPABILITY_PRESENT')
    digest = hashlib.sha256(); count = 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            count += len(block)
            need(count <= maximum, 'FILE_BYTE_BOUND_REFUSED')
            digest.update(block)
    after = path.lstat()
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink',
              'st_size', 'st_mtime_ns', 'st_ctime_ns')
    need(all(getattr(before, f) == getattr(after, f) for f in fields) and count == before.st_size,
         'FILE_CHANGED_DURING_READ')
    return {'bytes': count, 'sha256': digest.hexdigest()}

def owned_directory(path):
    path = Path(path); info = path.lstat()
    need(path.resolve(strict=True) == path and stat.S_ISDIR(info.st_mode) and
         info.st_uid == os.geteuid() and not info.st_mode & 0o077,
         'PRIVATE_DIRECTORY_REFUSED')
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': info.st_mode}

def write_private(path, raw):
    need(type(raw) is bytes, 'PRIVATE_BYTES_REQUIRED')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    need(file_identity(Path(path), max(1, len(raw))) == {'bytes': len(raw), 'sha256': sha(raw)},
         'PRIVATE_WRITE_READBACK_DIFFERS')

def diagnostic_errno(exc):
    return {errno.EACCES: 'EACCES', errno.EPERM: 'EPERM', errno.EIO: 'EIO',
            errno.ENOTDIR: 'ENOTDIR', errno.ELOOP: 'ELOOP'}.get(exc.errno, 'OTHER')


def diagnostic_kind(mode):
    if stat.S_ISDIR(mode): return 'DIRECTORY'
    if stat.S_ISREG(mode): return 'REGULAR'
    if stat.S_ISLNK(mode): return 'SYMLINK'
    return 'OTHER'


def startup_paths_diagnostic(profile):
    rows = []
    for identifier, anchor, relative in STARTUP_PATHS:
        path = profile['root']; parts = (anchor, *PurePosixPath(relative).parts)
        present = None; kind = 'UNREADABLE'; error_code = None
        # Check each intermediate entry with lstat before descending. No link
        # target or arbitrary directory population is opened by this diagnostic.
        for index in range(len(parts) + 1):
            if index: path = path / parts[index - 1]
            try:
                info = path.lstat()
            except OSError as exc:
                if exc.errno == errno.ENOENT: present, kind = False, 'ABSENT'
                else: error_code = diagnostic_errno(exc)
                break
            if index < len(parts):
                if not stat.S_ISDIR(info.st_mode):
                    kind = 'ANCESTOR_BLOCKED'; break
            else:
                present, kind = True, diagnostic_kind(info.st_mode)
        rows.append({'id': identifier, 'present': present, 'kind': kind, 'error_code': error_code})
    return {'schema': 'dg17.claude.body-startup-paths.v1', 'phase': 'NATIVE_STARTUP_AFTER',
            'path_count': 17, 'rows': rows}


def config_plugins_identity(info):
    values = {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
        'gid': info.st_gid, 'mode': info.st_mode, 'nlink': info.st_nlink,
        'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
    need(all(type(values[key]) is int and 0 <= values[key] <= 18446744073709551615
             for key in ('device', 'inode', 'uid', 'gid', 'mode', 'nlink', 'size')) and
         all(type(values[key]) is int and -9223372036854775808 <= values[key] <= 9223372036854775807
             for key in ('mtime_ns', 'ctime_ns')), 'CONFIG_PLUGINS_METADATA_BOUND')
    return values


def config_plugins_snapshot(profile):
    """Two bounded no-follow metadata censuses; never open a file's contents."""
    base = profile['root']; config = profile['config']
    need(base.is_absolute() and config == base / 'config' and
         all(part not in ('.', '..') for part in base.parts), 'CONFIG_PLUGINS_PROFILE_PATH')
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    def once():
        result = {'schema': 'dg17.claude.config-plugins-snapshot.v1', 'path_id': 'CONFIG_PLUGINS',
            'status': 'UNREADABLE', 'root': None, 'entries': [], 'error_code': None,
            'complete': False, 'stable': False}
        held = []; anchors = []
        def opened(name, parent=None):
            fd = os.open(name, flags) if parent is None else os.open(name, flags, dir_fd=parent)
            held.append(fd); return fd
        def same(first, second):
            need(config_plugins_identity(first) == config_plugins_identity(second), 'CONFIG_PLUGINS_CHANGED')
        def owned(info):
            need(info.st_uid == os.geteuid() and info.st_gid == os.getegid(), 'CONFIG_PLUGINS_ANCESTOR_BLOCKED')
        def anchor_bookend():
            for parent, name, fd, before in anchors:
                same(before, os.fstat(fd))
                same(before, os.lstat(name, dir_fd=parent))
        def walk(fd, parts):
            before = os.fstat(fd); owned(before)
            names = []
            with os.scandir(fd) as entries:
                for entry in entries:
                    names.append(entry.name)
                    need(len(names) <= 16, 'CONFIG_PLUGINS_CENSUS_BOUND')
            need(len(names) == len(set(names)), 'CONFIG_PLUGINS_CHANGED')
            for name in sorted(names):
                relative = '/'.join((*parts, name))
                try: path_bytes = relative.encode('utf-8', 'strict')
                except UnicodeError as exc: raise Refusal('CONFIG_PLUGINS_CENSUS_BOUND') from exc
                need(type(name) is str and name not in ('', '.', '..') and '/' not in name and
                     '\x00' not in name and len(parts) + 1 <= 8 and 0 < len(path_bytes) <= 256 and
                     len(result['entries']) < 16, 'CONFIG_PLUGINS_CENSUS_BOUND')
                info = os.lstat(name, dir_fd=fd); kind = diagnostic_kind(info.st_mode)
                result['entries'].append({'relative_path': relative, 'kind': kind,
                                          'identity': config_plugins_identity(info)})
                if stat.S_ISDIR(info.st_mode):
                    owned(info)
                    child = opened(name, fd)
                    same(info, os.fstat(child)); walk(child, (*parts, name))
                    same(info, os.lstat(name, dir_fd=fd))
                else:
                    same(info, os.lstat(name, dir_fd=fd))
            same(before, os.fstat(fd))
        try:
            current = opened('/'); path = Path('/')
            for component in config.parts[1:]:
                before = os.lstat(component, dir_fd=current)
                need(stat.S_ISDIR(before.st_mode), 'CONFIG_PLUGINS_ANCESTOR_BLOCKED')
                child = opened(component, current); same(before, os.fstat(child))
                path = path / component; parent = current; current = child
                if path in (base, config):
                    owned(before)
                    need(not before.st_mode & 0o077, 'CONFIG_PLUGINS_ANCESTOR_BLOCKED')
                    anchors.append((parent, component, child, before))
            need(len(anchors) == 2, 'CONFIG_PLUGINS_ANCESTOR_BLOCKED')
            try: before = os.lstat('plugins', dir_fd=current)
            except OSError as exc:
                if exc.errno != errno.ENOENT: raise
                anchor_bookend()
                result.update(status='COMPLETE_ABSENT', complete=True)
                return result
            kind = diagnostic_kind(before.st_mode)
            result['root'] = {'kind': kind, 'identity': config_plugins_identity(before),
                              'physical_path': kind != 'SYMLINK'}
            if stat.S_ISDIR(before.st_mode):
                owned(before)
                directory = opened('plugins', current); same(before, os.fstat(directory))
                walk(directory, ()); same(before, os.fstat(directory))
            same(before, os.lstat('plugins', dir_fd=current)); anchor_bookend()
            result.update(status='COMPLETE_PRESENT', complete=True)
        except Refusal as exc:
            result['status'] = ('BOUND_EXCEEDED' if str(exc) in
                ('CONFIG_PLUGINS_CENSUS_BOUND', 'CONFIG_PLUGINS_METADATA_BOUND') else
                'ANCESTOR_BLOCKED' if str(exc) == 'CONFIG_PLUGINS_ANCESTOR_BLOCKED' else 'CHANGED')
        except OSError as exc:
            result['status'] = 'CHANGED' if exc.errno == errno.ENOENT else 'UNREADABLE'
            result['error_code'] = None if exc.errno == errno.ENOENT else diagnostic_errno(exc)
        finally:
            for fd in reversed(held):
                try: os.close(fd)
                except OSError as exc:
                    result.update(status='UNREADABLE', complete=False, stable=False)
                    if result['error_code'] is None: result['error_code'] = diagnostic_errno(exc)
            result['entries'] = sorted(result['entries'], key=lambda row: row['relative_path'])
        return result
    before = once()
    if not before['complete']: return before
    after = once()
    if not after['complete']: return after
    if canonical(before) != canonical(after):
        before.update(status='CHANGED', complete=False)
        return before
    before['stable'] = True
    need(len(canonical(before)) <= 65536, 'CONFIG_PLUGINS_SNAPSHOT_BYTE_BOUND')
    return before


def config_plugins_projection(snapshot, capture_received, provider_received, admission_quiescence):
    root = snapshot['root']; info = root['identity'] if root is not None else None
    complete = snapshot['complete'] is True; stable = snapshot['stable'] is True
    empty = None
    if complete and stable:
        if snapshot['status'] == 'COMPLETE_ABSENT' and root is None and snapshot['entries'] == []:
            empty = True
        elif root is not None and root['kind'] == 'DIRECTORY':
            empty = len(snapshot['entries']) == 0
    custody = (capture_received is True and provider_received is True and
        type(admission_quiescence) is dict and set(admission_quiescence) ==
        {'no_owned_children_listed', 'wait_echild', 'verified'} and
        all(value is True for value in admission_quiescence.values()))
    physical = (complete and stable and snapshot['error_code'] is None and
        snapshot['status'] == 'COMPLETE_ABSENT' and root is None and snapshot['entries'] == [])
    if (complete and stable and snapshot['error_code'] is None and
            snapshot['status'] == 'COMPLETE_PRESENT' and root is not None and
            root['kind'] == 'DIRECTORY' and root['physical_path'] is True and
            stat.S_ISDIR(info['mode']) and stat.S_IMODE(info['mode']) == 0o700 and
            info['uid'] == os.geteuid() and info['gid'] == os.getegid()):
        physical = len(snapshot['entries']) <= 16
        seen = {(info['device'], info['inode'])}; paths = []; total = 0
        for row in snapshot['entries']:
            identity = row['identity']; relative = row['relative_path']
            parts = relative.split('/'); raw = relative.encode('utf-8', 'strict')
            pair = (identity['device'], identity['inode'])
            eligible = (0 < len(raw) <= 256 and len(parts) <= 8 and
                all(part not in ('', '.', '..') and '\x00' not in part for part in parts) and
                pair not in seen and identity['uid'] == os.geteuid() and
                identity['gid'] == os.getegid())
            if row['kind'] == 'DIRECTORY':
                eligible = eligible and stat.S_ISDIR(identity['mode']) and stat.S_IMODE(identity['mode']) == 0o700
            elif row['kind'] == 'REGULAR':
                eligible = (eligible and stat.S_ISREG(identity['mode']) and
                    stat.S_IMODE(identity['mode']) == 0o600 and identity['nlink'] == 1 and
                    0 <= identity['size'] <= 8 * 1024 * 1024)
                total += identity['size']
            else:
                eligible = False
            physical = physical and eligible
            seen.add(pair); paths.append(relative)
        physical = (physical and paths == sorted(paths) and len(paths) == len(set(paths)) and
                    total <= 32 * 1024 * 1024)
    admitted = physical and custody
    rows = []
    for row in snapshot['entries']:
        raw = row['relative_path'].encode('utf-8', 'strict'); identity = row['identity']
        rows.append({'relative_path_bytes': len(raw), 'relative_path_sha256': sha(raw),
            'kind': row['kind'], 'mode': stat.S_IMODE(identity['mode']),
            'uid_matches_effective': identity['uid'] == os.geteuid(),
            'gid_matches_effective': identity['gid'] == os.getegid(),
            'regular_file_bytes': identity['size'] if row['kind'] == 'REGULAR' else None})
    return {'schema': 'dg17.claude.config-plugins-observation.v2', 'path_id': 'CONFIG_PLUGINS',
        'status': snapshot['status'], 'kind': root['kind'] if root is not None else None,
        'mode': stat.S_IMODE(info['mode']) if info is not None else None,
        'uid_matches_effective': info['uid'] == os.geteuid() if info is not None else None,
        'gid_matches_effective': info['gid'] == os.getegid() if info is not None else None,
        'physical_path': root['physical_path'] if root is not None else None,
        'complete': complete, 'stable': stable, 'entry_count': len(rows), 'entries': rows,
        'error_code': snapshot['error_code'], 'population_sha256': sha(canonical(snapshot)),
        'empty': empty, 'profile_admitted': admitted}


def post_native_profile_readback(meta, profile, expected_plugins, capture_received,
                                 provider_received, admission_quiescence):
    """Original profile identities/configs and 16 absences plus one closed output."""
    rows = {key: meta.owned_directory(path) for key, path in profile.items()
            if key not in ('settings', 'mcp')}
    for key, value in (('settings', meta.SETTINGS), ('mcp', meta.MCP_CONFIG)):
        raw = meta.canonical(value)
        need(meta.file_identity(profile[key], len(raw)) == {'bytes': len(raw), 'sha256': sha(raw)},
             'SELECTED_STARTUP_CONFIG_CHANGED')
    for identifier, anchor, relative in STARTUP_PATHS:
        if identifier != 'CONFIG_PLUGINS':
            need(not os.path.lexists(profile[anchor] / relative), 'UNREVIEWED_FRESH_CONTEXT_STARTUP_LAYER')
    need(expected_plugins is not None and config_plugins_projection(expected_plugins,
         capture_received, provider_received, admission_quiescence)['profile_admitted'],
         'UNREVIEWED_FRESH_CONTEXT_STARTUP_LAYER')
    observed = config_plugins_snapshot(profile)
    need(canonical(observed) == canonical(expected_plugins) and
         config_plugins_projection(observed, capture_received, provider_received,
                                   admission_quiescence)['profile_admitted'], 'CONFIG_PLUGINS_PROFILE_CHANGED')
    return rows


def directory_refusal_diagnostic(path, root):
    relative = path.relative_to(root).as_posix(); raw = relative.encode('utf-8', 'strict')
    need(0 < len(raw) <= 4096 and not PurePosixPath(relative).is_absolute() and
         all(part not in ('', '.', '..') for part in relative.split('/')), 'DIRECTORY_DIAGNOSTIC_PATH_REFUSED')
    info = None; kind = 'UNREADABLE'; error_code = None; physical = None
    try:
        info = path.lstat(); kind = diagnostic_kind(info.st_mode)
    except OSError as exc:
        if exc.errno == errno.ENOENT: kind = 'ABSENT'
        else: error_code = diagnostic_errno(exc)
    if info is not None:
        try: physical = path.resolve(strict=True) == path
        except OSError as exc: error_code = diagnostic_errno(exc)
    facts = {'status': 'PUBLIC_SAFE_FIRST_DIRECTORY_REFUSAL_ONLY', 'phase': 'PRIVATE_SEAL',
        'relative_path_bytes': len(raw), 'relative_path_sha256': sha(raw), 'kind': kind,
        'mode': stat.S_IMODE(info.st_mode) if info is not None else None,
        'uid_matches_effective': info.st_uid == os.geteuid() if info is not None else None,
        'gid_matches_effective': info.st_gid == os.getegid() if info is not None else None,
        'owner_only_mode': not bool(info.st_mode & 0o077) if info is not None else None,
        'physical_path': physical, 'error_code': error_code}
    return {'relative_path': relative, 'facts': facts}


def private_seal_rows(meta, root, directory_refused):
    # Exact inherited traversal/limits/row order, with one observer at its
    # existing directory refusal site. The observer never grants admission.
    rows = []; total = 0; pending = [root]
    while pending:
        parent = pending.pop()
        try:
            with os.scandir(parent) as entries:
                names = []
                for entry in entries:
                    names.append(entry.name)
                    meta.need(len(names) <= 513, 'PRIVATE_SEAL_POPULATION_BOUND')
            for name in sorted(names):
                path = Path(parent) / name
                if path == root / 'PRIVATE_EVIDENCE_SEAL.json':
                    continue
                relative = path.relative_to(root)
                meta.need(len(relative.parts) <= 16 and len(rows) < 512, 'PRIVATE_SEAL_POPULATION_BOUND')
                info = path.lstat()
                meta.need(not stat.S_ISLNK(info.st_mode), 'PRIVATE_SEAL_LINK_REFUSED')
                if stat.S_ISDIR(info.st_mode):
                    try:
                        meta.owned_directory(path)
                    except meta.Refusal as exc:
                        if str(exc) == 'PRIVATE_DIRECTORY_REFUSED': directory_refused(path, exc)
                        raise
                    rows.append({'path': relative.as_posix(), 'kind': 'DIRECTORY'}); pending.append(path)
                else:
                    identity = meta.file_identity(path, 8 * 1024 * 1024); total += identity['bytes']
                    meta.need(total <= 32 * 1024 * 1024, 'PRIVATE_SEAL_BYTE_BOUND')
                    rows.append({'path': relative.as_posix(), 'kind': 'REGULAR', **identity})
        except OSError as exc:
            raise meta.Refusal('PRIVATE_SEAL_ENUMERATION_REFUSED') from exc
    return sorted(rows, key=lambda row: row['path'])


def load_pinned_module(root, name, expected):
    path = root / (name + '.py')
    need(file_identity(path, 131072)['sha256'] == expected, 'DEPENDENCY_PIN_DIFFERS')
    spec = importlib.util.spec_from_file_location('dg17_claude04_' + name, path)
    need(spec is not None and spec.loader is not None, 'DEPENDENCY_LOADER_UNAVAILABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(file_identity(path, 131072)['sha256'] == expected, 'DEPENDENCY_CHANGED_DURING_LOAD')
    return module


def matrix_canonical(matrix):
    return (json.dumps(matrix, indent=2, sort_keys=True, ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def matrix_input(path, root, transport):
    path = Path(path)
    need(path == root / 'CANONICAL_PACKAGE_MATRIX.json' and
         file_identity(path, 32768)['sha256'] == MATRIX_SHA, 'PACKAGE_MATRIX_PIN_DIFFERS')
    value = transport.strict_json(path.read_bytes(), 32768)
    need(type(value) is dict and len(value) == 75 and sha(matrix_canonical(value)) == MATRIX_SHA,
         'PACKAGE_MATRIX_POPULATION_DIFFERS')
    for name, row in value.items():
        need(type(name) is str and name and '\\' not in name and not name.startswith('/') and
             all(p not in ('', '.', '..') for p in name.split('/')) and len(name) <= 512,
             'PACKAGE_MEMBER_PATH_REFUSED')
        need(type(row) is dict and set(row) == {'bytes', 'sha256', 'mode'} and
             type(row['bytes']) is int and 0 <= row['bytes'] <= 8 * 1024 * 1024 and
             type(row['sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', row['sha256']) and
             type(row['mode']) is int and row['mode'] in (0o644, 0o755),
             'PACKAGE_MATRIX_ROW_REFUSED')
    need(sum(x['bytes'] for x in value.values()) == 2092025, 'PACKAGE_EXPANDED_BYTES_DIFFERS')
    return value


def package_census(root, matrix):
    owned_directory(root)
    pending = [root]; files = {}; dirs = set(); count = 0
    while pending:
        parent = pending.pop()
        try:
            with os.scandir(parent) as iterator:
                names = [entry.name for entry in iterator]
            need(len(names) <= 128, 'PACKAGE_DIRECTORY_POPULATION_BOUND')
            for name in sorted(names):
                path = parent / name; relative = path.relative_to(root).as_posix()
                info = path.lstat(); count += 1
                need(count <= 128 and len(path.relative_to(root).parts) <= 16,
                     'PACKAGE_POPULATION_BOUND')
                if stat.S_ISDIR(info.st_mode):
                    owned_directory(path); dirs.add(relative); pending.append(path)
                else:
                    need(relative in matrix and stat.S_ISREG(info.st_mode), 'PACKAGE_UNEXPECTED_MEMBER')
                    wanted = matrix[relative]
                    need(stat.S_IMODE(info.st_mode) == wanted['mode'], 'PACKAGE_MEMBER_MODE_DIFFERS')
                    observed = file_identity(path, wanted['bytes'])
                    need(observed == {'bytes': wanted['bytes'], 'sha256': wanted['sha256']},
                         'PACKAGE_MEMBER_IDENTITY_DIFFERS')
                    files[relative] = {**observed, 'mode': stat.S_IMODE(info.st_mode)}
        except OSError:
            raise Refusal('PACKAGE_ENUMERATION_REFUSED') from None
    expected_dirs = {str(parent) for name in matrix for parent in PurePosixPath(name).parents if str(parent) != '.'}
    need(dirs == expected_dirs and files == matrix, 'PACKAGE_COMPLETE_POPULATION_DIFFERS')
    return {'member_count': len(files), 'directory_count': len(dirs),
            'expanded_bytes': sum(x['bytes'] for x in files.values()), 'matrix_sha256': sha(matrix_canonical(files))}


def extract_package(archive, destination, matrix):
    archive = Path(archive)
    before = file_identity(archive, PACKAGE_BYTES)
    need(before == {'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA}, 'CANONICAL_ARCHIVE_IDENTITY_DIFFERS')
    need(not os.path.lexists(destination), 'PACKAGE_DESTINATION_NOT_FRESH')
    destination.mkdir(mode=0o700)
    with zipfile.ZipFile(archive) as opened:
        infos = opened.infolist()
        need(len(infos) == len(matrix) and len({x.filename for x in infos}) == len(infos),
             'CANONICAL_ARCHIVE_POPULATION_DIFFERS')
        need({x.filename for x in infos} == set(matrix), 'CANONICAL_ARCHIVE_NAMES_DIFFER')
        for info in infos:
            wanted = matrix[info.filename]; mode = info.external_attr >> 16
            need(not info.is_dir() and stat.S_ISREG(mode) and stat.S_IMODE(mode) == wanted['mode'] and
                 info.file_size == wanted['bytes'] and not info.flag_bits & 1,
                 'CANONICAL_ARCHIVE_MEMBER_SHAPE_DIFFERS')
            raw = opened.read(info)
            need(len(raw) == wanted['bytes'] and sha(raw) == wanted['sha256'],
                 'CANONICAL_ARCHIVE_MEMBER_BYTES_DIFFER')
            path = destination / info.filename
            missing = []; parent = path.parent
            while parent != destination and not parent.exists():
                missing.append(parent); parent = parent.parent
            for directory in reversed(missing): directory.mkdir(mode=0o700)
            write_private(path, raw); os.chmod(path, wanted['mode'], follow_symlinks=False)
    need(file_identity(archive, PACKAGE_BYTES) == before, 'CANONICAL_ARCHIVE_CHANGED')
    return package_census(destination, matrix)


def command_argv(binary, package, profile, transport, session_id):
    prompt = ('/implementaudit:implementaudit DG17_OPERATION_ID=' + session_id +
              ' Bounded native governor content delivery observation only. No child route or effects are requested.')
    return [str(binary), '--setting-sources', 'user', '--settings', str(profile['settings']),
        '--strict-mcp-config', '--mcp-config', str(profile['mcp']), '--no-chrome',
        '--plugin-dir', str(package), '--print', '--output-format', 'stream-json', '--verbose',
        '--max-turns', '1', '--tools', 'Skill', '--disallowedTools', 'mcp__*',
        '--no-session-persistence', '--permission-prompts', 'none',
        '--session-id', session_id, '--model', transport.MODEL_SELECTOR, prompt]


def native_plugin_diagnostic_v2_empty(reason):
    return {'schema': 'dg17.claude.native-plugin-identity-diagnostic.v2',
        'status': 'UNRECEIVED', 'reason': reason, 'raw_stdout_bytes': None,
        'raw_stdout_sha256': None, 'expected_context_sha256': None, 'event_count': None,
        'pre_plugin_envelope_received': False, 'plugins_present': None, 'plugins_type': None,
        'plugins_canonical_bytes': None, 'plugins_canonical_sha256': None,
        'list_length': None, 'singleton': None, 'original_equality': None, 'array_profile': None,
        'body_acceptance_from_diagnostics': False}

def native_plugin_joint_bytes(value):
    """New commitments deliberately omit the old diagnostic codec's final LF."""
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':')).encode('ascii')

def native_plugin_joint_unavailable(reason):
    return {'schema': 'dg17.claude.plugin-joint-shape.v1', 'status': 'UNAVAILABLE',
            'reason': reason, 'rows': None}

def native_plugin_joint_valid(value):
    """Exact positional receiving; the compatible generic schema is insufficient."""
    if type(value) is not dict or set(value) != {'schema', 'status', 'reason', 'rows'}:
        return False
    if (type(value['schema']) is not str or type(value['status']) is not str or
            value['schema'] != 'dg17.claude.plugin-joint-shape.v1'):
        return False
    if value['status'] == 'UNAVAILABLE':
        return (type(value['reason']) is str and value['reason'] in
            ('ENVELOPE_UNAVAILABLE', 'NON_ARRAY', 'ROW_LIMIT', 'ENCODING_REFUSED', 'OUTPUT_BOUND')
            and value['rows'] is None)
    if value['status'] != 'COMPLETE' or value['reason'] is not None or type(value['rows']) is not list or len(value['rows']) > 4:
        return False
    types = ('NULL', 'BOOLEAN', 'INTEGER', 'FLOAT', 'STRING', 'ARRAY', 'OBJECT')
    names = ('MISSING', 'NON_STRING', 'MANIFEST_NAME_EXACT', 'MANIFEST_NAME_INLINE',
        'DOCUMENTED_1_BARE', 'DOCUMENTED_1_BUILTIN_ID', 'DOCUMENTED_2_BARE', 'DOCUMENTED_2_BUILTIN_ID',
        'DOCUMENTED_3_BARE', 'DOCUMENTED_3_BUILTIN_ID', 'DOCUMENTED_4_BARE', 'DOCUMENTED_4_BUILTIN_ID',
        'DOCUMENTED_5_BARE', 'DOCUMENTED_5_BUILTIN_ID', 'DOCUMENTED_6_BARE', 'DOCUMENTED_6_BUILTIN_ID', 'OTHER_STRING')
    paths = ('MISSING', 'NON_STRING', 'EXACT_EXPECTED', 'LEXICAL_ONLY', 'OTHER_STRING')
    fixed = {'NAME_PATH_ONLY': {'name', 'path'}, 'NAME_PATH_SOURCE': {'name', 'path', 'source'},
             'NAME_PATH_VERSION': {'name', 'path', 'version'},
             'NAME_PATH_SOURCE_VERSION': {'name', 'path', 'source', 'version'}}
    def count(v): return type(v) is int and 0 <= v <= 196609
    def hash_value(v): return type(v) is str and re.fullmatch(r'[0-9a-f]{64}', v) is not None
    for row in value['rows']:
        if type(row) is not list or len(row) != 11 or type(row[0]) is not str or row[0] not in types:
            return False
        if row[0] != 'OBJECT':
            if any(v is not None for v in row[1:]): return False
            continue
        if type(row[1]) is not str or row[1] not in names or type(row[2]) is not str or row[2] not in paths:
            return False
        if row[1] == 'OTHER_STRING':
            if not count(row[3]) or row[3] < 2 or not hash_value(row[4]): return False
        elif row[3] is not None or row[4] is not None:
            return False
        if not count(row[5]) or row[5] > 1024 or not hash_value(row[6]) or type(row[7]) is not str:
            return False
        if any(type(v) is not str or v not in ('ABSENT',) + types for v in row[8:10]) or not count(row[10]):
            return False
        keys = set()
        for present, key in ((row[1] != 'MISSING', 'name'), (row[2] != 'MISSING', 'path'),
                             (row[8] != 'ABSENT', 'source'), (row[9] != 'ABSENT', 'version')):
            if present: keys.add(key)
        if row[5] != len(keys) + row[10]: return False
        shape = next((name for name, keyset in fixed.items() if row[10] == 0 and keyset == keys), 'OTHER')
        if row[7] != shape: return False
        if row[10] == 0 and row[6] != hashlib.sha256(native_plugin_joint_bytes(sorted(keys))).hexdigest():
            return False
    return True

def native_plugin_joint_profile(plugins, expected_plugin):
    """Project at most four complete admitted elements; no lookup of reported data."""
    if type(plugins) is not list:
        return native_plugin_joint_unavailable('NON_ARRAY')
    if len(plugins) > 4:
        return native_plugin_joint_unavailable('ROW_LIMIT')
    try:
        types = {type(None): 'NULL', bool: 'BOOLEAN', int: 'INTEGER', float: 'FLOAT',
                 str: 'STRING', list: 'ARRAY', dict: 'OBJECT'}
        # Defensive finite JSON shape only; the unchanged caller owns raw admission.
        pending = [(plugins, 0)]; visited = 0
        while pending:
            current, depth = pending.pop(); visited += 1
            if type(current) not in types or depth > 32 or visited > 32768:
                raise ValueError('JOINT_JSON_SHAPE')
            if type(current) is dict:
                if len(current) > 1024 or any(type(key) is not str or len(key) > 1024 for key in current):
                    raise ValueError('JOINT_JSON_OBJECT')
                pending.extend((item, depth + 1) for item in current.values())
            elif type(current) is list:
                if len(current) > 4096: raise ValueError('JOINT_JSON_ARRAY')
                pending.extend((item, depth + 1) for item in current)
        if len(native_plugin_joint_bytes(plugins)) + 1 > 196609:
            raise ValueError('JOINT_PLUGIN_BOUND')
        names = {'implementaudit': 'MANIFEST_NAME_EXACT', 'implementaudit@inline': 'MANIFEST_NAME_INLINE',
            'cc-plugin-agents-md': 'DOCUMENTED_1_BARE', 'cc-plugin-agents-md@builtin': 'DOCUMENTED_1_BUILTIN_ID',
            'cc-plugin-diff': 'DOCUMENTED_2_BARE', 'cc-plugin-diff@builtin': 'DOCUMENTED_2_BUILTIN_ID',
            'cc-plugin-plugin-authoring': 'DOCUMENTED_3_BARE', 'cc-plugin-plugin-authoring@builtin': 'DOCUMENTED_3_BUILTIN_ID',
            'cc-plugin-sec-default': 'DOCUMENTED_4_BARE', 'cc-plugin-sec-default@builtin': 'DOCUMENTED_4_BUILTIN_ID',
            'cc-plugin-telemetry': 'DOCUMENTED_5_BARE', 'cc-plugin-telemetry@builtin': 'DOCUMENTED_5_BUILTIN_ID',
            'cc-plugin-you-should-know': 'DOCUMENTED_6_BARE', 'cc-plugin-you-should-know@builtin': 'DOCUMENTED_6_BUILTIN_ID'}
        fixed = {'NAME_PATH_ONLY': {'name', 'path'}, 'NAME_PATH_SOURCE': {'name', 'path', 'source'},
                 'NAME_PATH_VERSION': {'name', 'path', 'version'},
                 'NAME_PATH_SOURCE_VERSION': {'name', 'path', 'source', 'version'}}
        rows = []
        for item in plugins:
            kind = types[type(item)]
            if kind != 'OBJECT':
                rows.append([kind] + [None] * 10)
                continue
            name = ('MISSING' if 'name' not in item else 'NON_STRING' if type(item['name']) is not str
                    else names.get(item['name'], 'OTHER_STRING'))
            path = ('MISSING' if 'path' not in item else 'NON_STRING' if type(item['path']) is not str
                    else 'EXACT_EXPECTED' if item['path'] == expected_plugin
                    else 'LEXICAL_ONLY' if posixpath.normpath(item['path']) == posixpath.normpath(expected_plugin)
                    else 'OTHER_STRING')
            name_raw = native_plugin_joint_bytes(item['name']) if name == 'OTHER_STRING' else None
            keys = set(item)
            key_hash = hashlib.sha256(native_plugin_joint_bytes(sorted(keys))).hexdigest()
            shape = next((label for label, keyset in fixed.items() if keys == keyset), 'OTHER')
            rows.append([kind, name, path, len(name_raw) if name_raw is not None else None,
                hashlib.sha256(name_raw).hexdigest() if name_raw is not None else None,
                len(keys), key_hash, shape,
                types[type(item['source'])] if 'source' in item else 'ABSENT',
                types[type(item['version'])] if 'version' in item else 'ABSENT',
                len(keys - {'name', 'path', 'source', 'version'})])
        result = {'schema': 'dg17.claude.plugin-joint-shape.v1', 'status': 'COMPLETE', 'reason': None, 'rows': rows}
        if not native_plugin_joint_valid(result): raise ValueError('JOINT_REPRESENTATION')
        return result
    except (ValueError, TypeError, KeyError, UnicodeError, OverflowError, RecursionError):
        return native_plugin_joint_unavailable('ENCODING_REFUSED')

def native_plugin_joint_finish(base, plugins, expected_plugin):
    """Retain the exact old projection; only new complete rows may fall back."""
    if type(base) is not dict or base.get('schema') != 'dg17.claude.native-plugin-identity-diagnostic.v2':
        raise Refusal('PLUGIN_DIAGNOSTIC_BASE_SCHEMA')
    result = dict(base)
    result['schema'] = 'dg17.claude.native-plugin-identity-diagnostic.v3'
    result['joint_profile'] = (native_plugin_joint_profile(plugins, expected_plugin)
        if base.get('pre_plugin_envelope_received') is True
        else native_plugin_joint_unavailable('ENVELOPE_UNAVAILABLE'))
    if len(native_plugin_joint_bytes(result)) + 1 > 4096 and result['joint_profile']['status'] == 'COMPLETE':
        result['joint_profile'] = native_plugin_joint_unavailable('OUTPUT_BOUND')
    if not native_plugin_joint_valid(result['joint_profile']) or len(native_plugin_joint_bytes(result)) + 1 > 4096:
        raise Refusal('PLUGIN_DIAGNOSTIC_JOINT_BOUND')
    return result

def empty_native_plugin_diagnostic(reason):
    # Keep the original values and refusal reason; v3 adds only unavailable rows.
    return native_plugin_joint_finish(native_plugin_diagnostic_v2_empty(reason), None, None)


def native_plugin_array_profile(plugins, expected_plugin):
    """Count every element of a codec-admitted array using fixed literal labels.

    Name labels classify strings only; they confer no origin or admission.
    Path comparison is lexical string work and never observes a reported path.
    """
    type_labels = {type(None): 'NULL', bool: 'BOOLEAN', int: 'INTEGER', float: 'FLOAT',
                   str: 'STRING', list: 'ARRAY', dict: 'OBJECT'}
    name_labels = {
        'implementaudit': 'MANIFEST_NAME_EXACT',
        'implementaudit@inline': 'MANIFEST_NAME_INLINE',
        'cc-plugin-agents-md': 'DOCUMENTED_1_BARE',
        'cc-plugin-agents-md@builtin': 'DOCUMENTED_1_BUILTIN_ID',
        'cc-plugin-diff': 'DOCUMENTED_2_BARE',
        'cc-plugin-diff@builtin': 'DOCUMENTED_2_BUILTIN_ID',
        'cc-plugin-plugin-authoring': 'DOCUMENTED_3_BARE',
        'cc-plugin-plugin-authoring@builtin': 'DOCUMENTED_3_BUILTIN_ID',
        'cc-plugin-sec-default': 'DOCUMENTED_4_BARE',
        'cc-plugin-sec-default@builtin': 'DOCUMENTED_4_BUILTIN_ID',
        'cc-plugin-telemetry': 'DOCUMENTED_5_BARE',
        'cc-plugin-telemetry@builtin': 'DOCUMENTED_5_BUILTIN_ID',
        'cc-plugin-you-should-know': 'DOCUMENTED_6_BARE',
        'cc-plugin-you-should-know@builtin': 'DOCUMENTED_6_BUILTIN_ID'}
    profile = {'complete': True, 'element_count': len(plugins),
        'type_counts': dict.fromkeys(('NULL', 'BOOLEAN', 'INTEGER', 'FLOAT', 'STRING', 'ARRAY', 'OBJECT'), 0),
        'object_keyset_counts': dict.fromkeys(('EXACT_NAME_PATH', 'OTHER_OBJECT'), 0),
        'object_name_counts': dict.fromkeys(('MISSING', 'NON_STRING', 'MANIFEST_NAME_EXACT',
            'MANIFEST_NAME_INLINE', 'DOCUMENTED_1_BARE', 'DOCUMENTED_1_BUILTIN_ID',
            'DOCUMENTED_2_BARE', 'DOCUMENTED_2_BUILTIN_ID', 'DOCUMENTED_3_BARE',
            'DOCUMENTED_3_BUILTIN_ID', 'DOCUMENTED_4_BARE', 'DOCUMENTED_4_BUILTIN_ID',
            'DOCUMENTED_5_BARE', 'DOCUMENTED_5_BUILTIN_ID', 'DOCUMENTED_6_BARE',
            'DOCUMENTED_6_BUILTIN_ID', 'OTHER_STRING'), 0),
        'object_path_counts': dict.fromkeys(('MISSING', 'NON_STRING', 'EXACT_EXPECTED', 'LEXICAL_ONLY', 'OTHER_STRING'), 0),
        'record_counts': dict.fromkeys(('EXACT_EXPECTED_RECORD', 'INLINE_NAME_EXACT_PATH_RECORD', 'OTHER_ELEMENT'), 0)}
    expected_record = {'name': 'implementaudit', 'path': expected_plugin}
    inline_record = {'name': 'implementaudit@inline', 'path': expected_plugin}
    for item in plugins:
        profile['type_counts'][type_labels[type(item)]] += 1
        if type(item) is dict:
            keyset = 'EXACT_NAME_PATH' if set(item) == {'name', 'path'} else 'OTHER_OBJECT'
            profile['object_keyset_counts'][keyset] += 1
            if 'name' not in item:
                name = 'MISSING'
            elif type(item['name']) is not str:
                name = 'NON_STRING'
            else:
                name = name_labels.get(item['name'], 'OTHER_STRING')
            profile['object_name_counts'][name] += 1
            if 'path' not in item:
                path = 'MISSING'
            elif type(item['path']) is not str:
                path = 'NON_STRING'
            elif item['path'] == expected_plugin:
                path = 'EXACT_EXPECTED'
            elif posixpath.normpath(item['path']) == posixpath.normpath(expected_plugin):
                path = 'LEXICAL_ONLY'
            else:
                path = 'OTHER_STRING'
            profile['object_path_counts'][path] += 1
        if type(item) is dict and item == expected_record:
            record = 'EXACT_EXPECTED_RECORD'
        elif type(item) is dict and item == inline_record:
            record = 'INLINE_NAME_EXACT_PATH_RECORD'
        else:
            record = 'OTHER_ELEMENT'
        profile['record_counts'][record] += 1
    return profile


def native_plugin_identity_diagnostic(raw, context, custody_received, transport):
    """Pure bounded projection; never opens a reported path or accepts a plugin."""
    result = native_plugin_diagnostic_v2_empty('NOT_ATTEMPTED')
    def refused(reason):
        empty = empty_native_plugin_diagnostic(reason)
        for key in ('raw_stdout_bytes', 'raw_stdout_sha256', 'expected_context_sha256', 'event_count'):
            empty[key] = result[key]
        return empty
    if custody_received is not True:
        return refused('CUSTODY_OR_BOOKEND_UNRECEIVED')
    if not (type(context) is dict and set(context) == {'session_id', 'cwd', 'plugin', 'model'} and
            all(type(value) is str for value in context.values()) and
            re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',
                         context['session_id']) is not None and context['model'] == 'claude-sonnet-4-6' and
            all(posixpath.isabs(context[key]) and '\x00' not in context[key] for key in ('cwd', 'plugin'))):
        return refused('EXPECTED_CONTEXT_UNRECEIVED')
    try:
        for value in context.values(): value.encode('utf-8', errors='strict')
        result['expected_context_sha256'] = sha(canonical(context))
    except (ValueError, UnicodeError, TypeError):
        return refused('EXPECTED_CONTEXT_UNRECEIVED')
    if not (type(raw) is bytes and 0 < len(raw) <= 32768):
        return refused('INPUT_BYTE_BOUND')
    result['raw_stdout_bytes'] = len(raw); result['raw_stdout_sha256'] = sha(raw)
    lines = raw.splitlines()
    if not (0 < len(lines) <= 128 and all(lines)):
        return refused('EVENT_POPULATION_BOUND')
    result['event_count'] = len(lines)
    try:
        events = [transport.strict_json(line, 32768) for line in lines]
    except transport.Refusal as exc:
        return refused({'PROTOCOL_DUPLICATE_JSON_KEY': 'JSON_DUPLICATE_KEY',
            'PROTOCOL_JSON_ARRAY_BOUND': 'JSON_ARRAY_BOUND',
            'PROTOCOL_JSON_COMPLEXITY_BOUND': 'JSON_COMPLEXITY',
            'PROTOCOL_JSON_OBJECT_BOUND': 'JSON_OBJECT_BOUND',
            'PROTOCOL_JSON_STRING_BOUND': 'JSON_STRING_ENCODING',
            'PROTOCOL_JSON_TYPE_REFUSED': 'JSON_TYPE_UNRECEIVED',
            'PROTOCOL_JSON_UNRECEIVED': 'JSON_UNRECEIVED',
            'PROTOCOL_NONFINITE_JSON': 'JSON_NONFINITE'}.get(str(exc), 'JSON_UNRECEIVED'))
    except UnicodeError:
        return refused('JSON_STRING_ENCODING')
    except (ValueError, TypeError, RecursionError):
        return refused('JSON_UNRECEIVED')
    if not all(type(event) is dict and event.get('type') in ('system', 'user', 'assistant', 'result') for event in events):
        return refused('EVENT_TYPE_UNRECEIVED')
    if not all(event.get('session_id') == context['session_id'] for event in events):
        return refused('SESSION_DIFFERS')
    if any(event.get('parent_tool_use_id') is not None for event in events):
        return refused('CHILD_EVENT_UNRECEIVED')
    inits = [(index, event) for index, event in enumerate(events)
             if event.get('type') == 'system' and event.get('subtype') == 'init']
    terminal = [index for index, event in enumerate(events) if event.get('type') == 'result']
    if not (len(inits) == len(terminal) == 1 and inits[0][0] < terminal[0] == len(events) - 1):
        return refused('INIT_RESULT_ORDER_UNRECEIVED')
    init = inits[0][1]
    if not (init.get('cwd') == context['cwd'] and init.get('model') == context['model']):
        return refused('CONFIG_IDENTITY_DIFFERS')
    tools = init.get('tools')
    if not (type(tools) is list and all(type(value) is str for value in tools) and
            len(tools) == len(set(tools)) and 'Skill' in tools and
            all(value in ('Skill', 'EndConversation') for value in tools)):
        return refused('TOOL_SURFACE_DIFFERS')
    if not (init.get('mcp_servers') == [] and init.get('mcp_server_errors', []) == [] and
            init.get('plugin_errors', []) == []):
        return refused('MCP_OR_PLUGIN_ERROR_PRESENT')
    def kind(value):
        return {type(None): 'NULL', bool: 'BOOLEAN', int: 'INTEGER', float: 'FLOAT',
                str: 'STRING', list: 'ARRAY', dict: 'OBJECT'}[type(value)]
    def named(item, field, expected):
        present = field in item; value = item.get(field)
        row = {'present': present, 'type': kind(value) if present else 'MISSING',
               'utf8_bytes': None, 'utf8_sha256': None, 'equals_expected': None}
        if type(value) is str and present:
            raw_string = value.encode('utf-8', errors='strict')
            row.update(utf8_bytes=len(raw_string), utf8_sha256=sha(raw_string), equals_expected=value == expected)
        if field == 'name':
            row['name_relation'] = ('MISSING' if not present else 'NON_STRING' if type(value) is not str else
                'MANIFEST_NAME_EXACT' if value == 'implementaudit' else
                'MANIFEST_NAME_WITH_LITERAL_INLINE_SUFFIX' if value == 'implementaudit@inline' else 'OTHER_STRING')
        else:
            row['lexical_normalization_equals_expected'] = (
                posixpath.normpath(value) == posixpath.normpath(expected) if present and type(value) is str else None)
        return row
    present = 'plugins' in init; plugins = init.get('plugins')
    result.update(status='RECEIVED_PRE_PLUGIN_DIAGNOSTIC', reason=None,
        pre_plugin_envelope_received=True, plugins_present=present,
        plugins_type=kind(plugins) if present else 'MISSING',
        original_equality=plugins == [{'name': 'implementaudit', 'path': context['plugin']}])
    try:
        if present:
            value_raw = canonical(plugins)
            if len(value_raw) > 196609: return refused('PUBLIC_BOUND_REFUSED')
            result['plugins_canonical_bytes'] = len(value_raw); result['plugins_canonical_sha256'] = sha(value_raw)
        if type(plugins) is list:
            result['list_length'] = len(plugins)
            result['array_profile'] = native_plugin_array_profile(plugins, context['plugin'])
            if len(plugins) == 1:
                item = plugins[0]; item_raw = canonical(item)
                if len(item_raw) > 196609: return refused('PUBLIC_BOUND_REFUSED')
                one = {'type': kind(item), 'canonical_bytes': len(item_raw), 'canonical_sha256': sha(item_raw),
                       'key_count': None, 'keyset_sha256': None, 'exact_name_path_keys': None, 'name': None, 'path': None}
                if type(item) is dict:
                    one.update(key_count=len(item), keyset_sha256=sha(canonical(sorted(item))),
                        exact_name_path_keys=set(item) == {'name', 'path'},
                        name=named(item, 'name', 'implementaudit'), path=named(item, 'path', context['plugin']))
                result['singleton'] = one
        if len(canonical(result)) > 4096: return refused('PUBLIC_BOUND_REFUSED')
    except UnicodeError:
        return refused('JSON_STRING_ENCODING')
    except (ValueError, TypeError, KeyError, RecursionError):
        return refused('JSON_UNRECEIVED')
    return native_plugin_joint_finish(result, plugins, context['plugin'])


def initial_result():
    return {'schema': 'dg17.claude.canonical-body.v1', 'status': 'INCOMPLETE_OR_FAILED',
        'control_source_commit': CONTROL_COMMIT, 'control_source_tree': CONTROL_TREE,
        'package_source_commit': PACKAGE_COMMIT, 'package_source_tree': PACKAGE_TREE,
        'package_archive_bytes': PACKAGE_BYTES, 'package_archive_sha256': PACKAGE_SHA,
        'package_matrix_sha256': MATRIX_SHA, 'layout': 'CANONICAL_PLUGIN',
        'runtime_release_tag_declared': 'v2.1.318',
        'runtime_bytes': 337814032,
        'runtime_sha256': '708c77b204db30086ff6f1ed34577bda03e1be74ced80557cbf7b54249ebf0bd',
        'runtime_archive_bytes': 155477886,
        'runtime_archive_sha256': 'e6d426ca0c123f61fad58a361da0329f2a93cd206bc87040ed8d9576dd9eb583',
        'offline': None, 'provider_custody': None, 'provider_record_sha256': None,
        'currentness_receipt_sha256': None, 'currentness_before': False, 'currentness_after': False,
        'control_source_before': False, 'control_source_after': False,
        'runtime_before': False, 'runtime_after': False, 'git_admission_unchanged': False,
        'archive_before': False, 'archive_after': False, 'package_before': False, 'package_after': False,
        'startup_before': False, 'startup_after': False, 'fresh_context_count': 0,
        'startup_paths_after': None, 'private_directory_refusal': None, 'diagnostic_record_sha256': None,
        'config_plugins_profile': {'schema': 'dg17.claude.body-config-plugins.v2',
            'before_absent': False, 'before_record_sha256': None, 'after_record_sha256': None,
            'after': None, 'closing_unchanged': False, 'final_unchanged': False,
            'profile': 'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1', 'admission_quiescence': None},
        'native_sessions_started': 0, 'commands': [], 'body_delivery': None, 'native_observation': None,
        'native_plugin_identity_diagnostic': empty_native_plugin_diagnostic('NOT_ATTEMPTED'),
        'cleanup': {'after_close': None, 'after_seal': None, 'private_evidence_seal_sha256': None,
                    'private_seal_unchanged': False, 'host_teardown_observed': False,
                    'private_plaintext_policy': 'RETAIN_UNTIL_HOST_TEARDOWN'},
        'scripted_provider': True, 'upstream_forwarding': False, 'authentic_inference_proven': False,
        'native_all_five_full_bodies_received': False, 'genuine_child_route_received': False,
        'persistent_installation_proven': False, 'desktop_qualification': False,
        'parent_independent_receiving_required': True, 'independent_receiving': 'NOT_PERFORMED',
        'original_acceptance_awarded': False, 'failure': None, 'supplemental_failures': []}


def complete_result(value, records, meta):
    diagnostic = value['native_plugin_identity_diagnostic']
    if not (diagnostic['status'] == 'RECEIVED_PRE_PLUGIN_DIAGNOSTIC' and diagnostic['reason'] is None and
            diagnostic['pre_plugin_envelope_received'] is True and diagnostic['original_equality'] is True and
            diagnostic['body_acceptance_from_diagnostics'] is False):
        return False
    plugins = value['config_plugins_profile']
    quiescence = plugins['admission_quiescence']
    if not (plugins['schema'] == 'dg17.claude.body-config-plugins.v2' and
            plugins['profile'] == 'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1' and
            type(quiescence) is dict and set(quiescence) ==
            {'no_owned_children_listed', 'wait_echild', 'verified'} and
            all(item is True for item in quiescence.values()) and
            plugins['before_absent'] is True and plugins['before_record_sha256'] is not None and
            plugins['after_record_sha256'] is not None and plugins['after'] is not None and
            plugins['after']['profile_admitted'] is True and
            plugins['after_record_sha256'] == plugins['after']['population_sha256'] and
            plugins['closing_unchanged'] is True and plugins['final_unchanged'] is True):
        return False
    flags = ('currentness_before', 'currentness_after', 'control_source_before', 'control_source_after',
             'runtime_before', 'runtime_after', 'git_admission_unchanged', 'archive_before', 'archive_after',
             'package_before', 'package_after', 'startup_before', 'startup_after')
    if value['failure'] is not None or value['supplemental_failures'] or not all(value[k] is True for k in flags):
        return False
    if not (value['offline'] and value['offline']['verified'] is True and value['fresh_context_count'] == 1 and
            [r.get('name') for r in records] == ['currentness-before', 'canonical-body', 'currentness-after']):
        return False
    for row in records:
        product = row['name'] == 'canonical-body'
        if not meta.received_capture(row, enriched=product): return False
        if product and (row['recognition_status'] != 'BODY_AND_ENTRIES_RECEIVED' or row['recognition_code'] is not None or
            not all(row[k] is True for k in meta.ENRICHMENT_FIELDS - {'recognition_status', 'recognition_code'})):
            return False
    provider = value['provider_custody']
    if not (provider and provider['verified'] is True and provider['failure'] is None and
            provider['all_owned_sockets_closed'] is True and provider['thread_joined'] is True and
            provider['supplemental_failures'] == [] and provider['semantic_request_count'] == 1 and
            provider['semantic_response_complete'] is True): return False
    return (value['body_delivery'] is not None and value['native_observation'] is not None and
        value['native_observation']['canonical_advertised_entries_exact'] is True and
        value['cleanup']['private_seal_unchanged'] is True and
        all(value['cleanup'][k] is not None and value['cleanup'][k]['verified'] is True for k in ('after_close', 'after_seal')))


def run(args):
    result = initial_result(); records = []; phase = 'PRECONDITIONS'
    meta = utility = admission = transport = source = private = result_path = pins = None
    runtime_before = git_before = matrix = package = provider = profile = profile_before = managed_before = None
    gate_home = git_home = None; subreaper = False; route_safe = False
    directory_record = None; plugins_before = plugins_after = None
    out = session_id = store_after = None
    plugins_capture_received = plugins_provider_received = False
    deadline = time.monotonic() + RUN_SECONDS
    def failure(exc, where):
        kinds = tuple(x.Refusal for x in (meta, utility, admission, transport) if x is not None and hasattr(x, 'Refusal'))
        text = str(exc) if isinstance(exc, (Refusal, *kinds)) else 'UNEXPECTED_EXCEPTION'
        code = text if re.fullmatch(r'[A-Z0-9_]{1,96}', text) else 'UNEXPECTED_REFUSAL'
        row = {'phase': where, 'code': code}
        if row == result['failure'] or row in result['supplemental_failures']: return
        if result['failure'] is None: result['failure'] = row
        elif len(result['supplemental_failures']) < 16: result['supplemental_failures'].append(row)
    def observe(where, action):
        try: return action()
        except BaseException as exc: failure(exc, where); return None
    def record_directory_refusal(path, exc):
        nonlocal directory_record
        # Preserve the original guard failure before any diagnostic error.
        failure(exc, 'PRIVATE_SEAL')
        if directory_record is None:
            directory_record = observe('DIRECTORY_DIAGNOSTIC', lambda: directory_refusal_diagnostic(path, private))
            if directory_record is not None: result['private_directory_refusal'] = directory_record['facts']
    try:
        root = Path(__file__).resolve(strict=True).parent
        meta = load_pinned_module(root, 'claude_probe', SUPPORT_SHA)
        utility = load_pinned_module(root, 'host_utility', meta.HELPER_SHA256)
        admission = load_pinned_module(root, 'catalogue_probe', meta.ADMISSION_SHA256)
        transport = load_pinned_module(root, 'claude_body_transport', TRANSPORT_SHA)
        result['offline'] = admission.offline_guard(args)
        need(re.fullmatch(r'[a-z0-9][a-z0-9-]{0,95}', args.controller) is not None and
             re.fullmatch(r'refs/implementaudit/continuity-receipts/' + re.escape(args.controller) +
                          r'/G[0-9]{4}@[0-9a-f]{40}', args.receipt) is not None, 'CONTINUITY_ARGUMENTS_DIFFER')
        source = Path(args.source); episode = Path(args.episode)
        need(source.is_absolute() and source.resolve(strict=True) == source and
             episode.is_absolute() and episode.resolve(strict=True) == episode, 'NONPHYSICAL_INPUT_ROOT')
        envelope = episode / 'private'; gate_home = episode / 'home'
        owned_directory(envelope); owned_directory(gate_home)
        private = envelope / 'claude-canonical-body'
        need(not os.path.lexists(private) and not private.is_relative_to(source) and
             not source.is_relative_to(private), 'WORK_ROOT_NOT_FRESH_OR_OVERLAPPING')
        private.mkdir(mode=0o700)
        result_path = envelope / 'CLAUDE_BODY_RESULT.json'
        need(not os.path.lexists(result_path), 'RESULT_ALREADY_EXISTS')
        git_home = private / 'git-home'; git_home.mkdir(mode=0o700)
        need(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL, 'CHILD_REAP_POLICY_UNREVIEWED')
        libc = ctypes.CDLL(None, use_errno=True)
        need(libc.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_SETUP_REFUSED'); subreaper = True
        need(file_identity(root / 'SOURCE_INPUT_PINS.json', 32768)['sha256'] == meta.PINS_SHA256,
             'CONTROL_SOURCE_PINS_DIFFER')
        pins = meta.strict_json((root / 'SOURCE_INPUT_PINS.json').read_bytes())
        # The separately reviewed parent owns full commit/tree admission.
        # source_guard would issue two additional Git processes; do not call it.
        admission.source_store_guard(source)
        result['control_source_before'] = meta.source_inputs(source, pins)
        runtime_before = file_identity(Path(args.binary), meta.BINARY_BYTES, executable=True)
        need(runtime_before == {'bytes': meta.BINARY_BYTES, 'sha256': meta.BINARY_SHA256}, 'RUNTIME_IDENTITY_DIFFERS')
        result['runtime_before'] = True
        matrix = matrix_input(args.package_matrix_pins, root, transport)
        package = private / 'effective-plugin'
        extract_package(Path(args.canonical_archive), package, matrix)
        result['archive_before'] = result['package_before'] = True
        phase = 'CURRENTNESS_BEFORE'
        result['currentness_receipt_sha256'] = meta.currentness(args, source, gate_home, private,
            utility, records, deadline, 'currentness-before'); result['currentness_before'] = True
        phase = 'GIT_ADMISSION_BEFORE'
        need(meta.quiescent(utility)['verified'] is True, 'INITIAL_GIT_QUIESCENCE_REFUSED')
        git_before, _ = admission.git_startup_guard(git_home, True, source)
        write_private(private / 'GIT_ADMISSION_BEFORE.json', canonical(git_before)); route_safe = True
        phase = 'NATIVE_ADMISSION'
        profile, profile_before, managed_before = meta.fresh_profile(private, 'canonical-body', admission)
        result['fresh_context_count'] = 1; result['startup_before'] = True
        plugins_before = config_plugins_snapshot(profile)
        need(plugins_before['status'] == 'COMPLETE_ABSENT' and plugins_before['complete'] is True and
             plugins_before['stable'] is True and plugins_before['root'] is None and
             plugins_before['entries'] == [], 'UNREVIEWED_FRESH_CONTEXT_STARTUP_LAYER')
        raw = canonical(plugins_before); need(len(raw) <= 65536, 'CONFIG_PLUGINS_SNAPSHOT_BYTE_BOUND')
        write_private(private / 'CONFIG_PLUGINS_BEFORE.json', raw)
        result['config_plugins_profile']['before_absent'] = True
        result['config_plugins_profile']['before_record_sha256'] = sha(raw)
        need(admission.source_store_guard(source) == git_before['source_store'], 'SOURCE_STORE_BEFORE_COMMAND_CHANGED')
        meta.source_inputs(source, pins); package_census(package, matrix)
        need(file_identity(Path(args.binary), meta.BINARY_BYTES, executable=True) == runtime_before,
             'RUNTIME_BEFORE_COMMAND_CHANGED')
        need(meta.quiescent(utility)['verified'] is True and admission.offline_guard(args) == result['offline'],
             'NATIVE_ADMISSION_CHANGED')
        protocol_dir = private / 'provider'; protocol_dir.mkdir(mode=0o700)
        provider = transport.LocalResponder(protocol_dir, write_private, deadline)
        endpoint = provider.start()
        session_id = str(uuid.uuid4())
        argv = command_argv(Path(args.binary), package, profile, transport, session_id)
        write_private(private / 'NATIVE_INVOCATION.json', canonical({'argv': argv, 'session_id': session_id,
                      'cwd': str(profile['cwd']), 'provider_kind': 'LOCAL_SCRIPTED_NO_UPSTREAM'}))
        env = meta.command_environment(utility, profile)
        env.update(ANTHROPIC_BASE_URL=endpoint, ANTHROPIC_AUTH_TOKEN=transport.FIXTURE_TOKEN)
        phase = 'NATIVE_CAPTURE'; start = len(records); captured_error = None; out = None
        try:
            _, out, _ = meta.retain_capture(utility, 'canonical-body', argv, profile['cwd'], env,
                private, records, deadline, NATIVE_SECONDS)
        except BaseException as exc:
            captured_error = exc; failure(exc, phase)
        finally:
            result['provider_custody'] = observe('PROVIDER_CLOSE', provider.close)
            provider_record = {'schema': 'dg17.claude.local-provider-record.v1',
                'custody': result['provider_custody'], 'requests': provider.rows,
                'request_capture_scope': 'CAPTURED_HTTP_BYTES_ONLY',
                'response_capture_scope': 'PREPARED_BYTES_AND_SOCKET_SEND_RETURNED_COUNT'}
            raw = canonical(provider_record)
            def retain_provider_record():
                path = private / 'PROVIDER_RECORD.json'; write_private(path, raw)
                need(file_identity(path, len(raw)) == {'bytes': len(raw), 'sha256': sha(raw)},
                     'PROVIDER_RECORD_READBACK_DIFFERS')
                return sha(raw)
            result['provider_record_sha256'] = observe('PROVIDER_RETENTION', retain_provider_record)
            # This is a fresh data-only custody observation after the sole native
            # capture and provider close, before any output-profile admission.
            result['config_plugins_profile']['admission_quiescence'] = observe(
                'POST_NATIVE_OUTPUT_CUSTODY', lambda: meta.quiescent(utility))
            plugins_capture_received = (captured_error is None and
                [x.get('name') for x in records] == ['currentness-before', 'canonical-body'] and
                all(meta.received_capture(x) for x in records))
            custody = result['provider_custody']
            plugins_provider_received = (type(custody) is dict and custody.get('verified') is True and
                custody.get('all_owned_sockets_closed') is True and custody.get('thread_joined') is True and
                custody.get('failure') is None and custody.get('supplemental_failures') == [] and
                result['provider_record_sha256'] is not None)
            quiescence = result['config_plugins_profile']['admission_quiescence']
            if not (plugins_capture_received and plugins_provider_received and
                    type(quiescence) is dict and set(quiescence) ==
                    {'no_owned_children_listed', 'wait_echild', 'verified'} and
                    all(item is True for item in quiescence.values())):
                route_safe = False
                failure(Refusal('POST_NATIVE_OUTPUT_CUSTODY_UNVERIFIED'), 'POST_NATIVE_OUTPUT_ADMISSION')
            if len(records) == start + 1:
                row = records[-1]
                row.update(recognition_status='NOT_ATTEMPTED', recognition_code=None,
                    source_before=True, source_after=False, runtime_before=True, runtime_after=False,
                    startup_before=True, startup_after=False)
                row['source_after'] = observe('NATIVE_SOURCE_AFTER', lambda: meta.source_inputs(source, pins)) is True
                store_after = observe('NATIVE_STORE_AFTER', lambda: admission.source_store_guard(source))
                row['runtime_after'] = observe('NATIVE_RUNTIME_AFTER', lambda:
                    file_identity(Path(args.binary), meta.BINARY_BYTES, executable=True)) == runtime_before
                plugins_after = observe('CONFIG_PLUGINS_AFTER', lambda: config_plugins_snapshot(profile))
                if plugins_after is not None:
                    result['config_plugins_profile']['after'] = config_plugins_projection(plugins_after,
                        plugins_capture_received, plugins_provider_received, quiescence)
                    def retain_plugins_after():
                        raw = canonical(plugins_after)
                        need(len(raw) <= 65536, 'CONFIG_PLUGINS_SNAPSHOT_BYTE_BOUND')
                        write_private(private / 'CONFIG_PLUGINS_AFTER.json', raw)
                        return sha(raw)
                    result['config_plugins_profile']['after_record_sha256'] = observe(
                        'CONFIG_PLUGINS_RETENTION', retain_plugins_after)
                row['startup_after'] = observe('NATIVE_STARTUP_AFTER', lambda:
                    (post_native_profile_readback(meta, profile, plugins_after, plugins_capture_received,
                        plugins_provider_received, quiescence),
                     meta.managed_and_ancestor_guard(admission, profile['cwd']))) == (profile_before, managed_before)
                result['startup_after'] = row['startup_after']
                result['startup_paths_after'] = observe('NATIVE_STARTUP_DIAGNOSTIC', lambda: startup_paths_diagnostic(profile))
                need(row['source_after'] and store_after == git_before['source_store'] and row['runtime_after'] and
                     row['startup_after'], 'NATIVE_BOOKEND_REFUSED')
        if captured_error is not None: raise captured_error
        phase = 'PROVIDER_RECEIVING'
        need(result['provider_custody'] is not None and result['provider_custody']['verified'] is True and
             result['provider_custody']['failure'] is None and result['provider_custody']['supplemental_failures'] == [] and
             result['provider_custody']['semantic_request_count'] == 1 and
             result['provider_custody']['semantic_response_complete'] is True,
             'PROVIDER_CONTAINMENT_OR_PROTOCOL_REFUSED')
        need(meta.quiescent(utility)['verified'] is True, 'NATIVE_READBACK_QUIESCENCE_REFUSED')
        result['package_after'] = observe('PACKAGE_AFTER', lambda: package_census(package, matrix)) is not None
        result['archive_after'] = observe('ARCHIVE_AFTER', lambda:
            file_identity(Path(args.canonical_archive), PACKAGE_BYTES)) == {'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA}
        need(result['package_after'] and result['archive_after'], 'PACKAGE_READBACK_REFUSED')
        phase = 'NATIVE_RECOGNITION'
        try:
            governor_raw = (package / 'skills/implementaudit/SKILL.md').read_bytes()
            governor_pin = matrix['skills/implementaudit/SKILL.md']
            need(len(governor_raw) == governor_pin['bytes'] and sha(governor_raw) == governor_pin['sha256'],
                 'GOVERNOR_BODY_SOURCE_IDENTITY_DIFFERS')
            result['body_delivery'] = transport.body_witness(provider.semantic_raw, governor_raw, session_id)
            result['native_observation'] = transport.native_projection(out, session_id, profile['cwd'], package)
            need(result['native_observation']['canonical_advertised_entries_exact'] is True,
                 'CANONICAL_ADVERTISED_ENTRIES_UNRECEIVED')
            records[-1]['recognition_status'] = 'BODY_AND_ENTRIES_RECEIVED'
        except BaseException as exc:
            records[-1]['recognition_status'] = 'UNRECEIVED'
            records[-1]['recognition_code'] = str(exc) if isinstance(exc, transport.Refusal) else 'NATIVE_RECOGNITION_REFUSED'
            raise
    except BaseException as exc:
        route_safe = False; failure(exc, phase)
    finally:
        if provider is not None and result['provider_custody'] is None:
            result['provider_custody'] = observe('FINAL_PROVIDER_CLOSE', provider.close)
        if subreaper:
            result['cleanup']['after_close'] = observe('AFTER_CLOSE', lambda: meta.quiescent(utility))
        if private is not None and result['currentness_before'] and route_safe:
            def closing_admission():
                need(result['provider_custody']['verified'] is True and result['provider_custody']['failure'] is None,
                     'CLOSING_PROVIDER_CUSTODY_REFUSED')
                need(result['cleanup']['after_close'] == {'no_owned_children_listed': True, 'wait_echild': True, 'verified': True},
                     'CLOSING_CUSTODY_UNVERIFIED')
                need([x.get('name') for x in records] == ['currentness-before', 'canonical-body'] and
                     all(meta.received_capture(x, enriched=x['name'] == 'canonical-body') for x in records),
                     'CLOSING_CAPTURE_CUSTODY_UNVERIFIED')
                need(result['failure'] is None and not result['supplemental_failures'], 'CLOSING_PRIOR_FAILURE')
                need(meta.source_inputs(source, pins) is True and
                     admission.source_store_guard(source) == git_before['source_store'], 'CLOSING_SOURCE_UNVERIFIED')
                need(file_identity(Path(args.binary), meta.BINARY_BYTES, executable=True) == runtime_before,
                     'CLOSING_RUNTIME_CHANGED')
                package_census(package, matrix)
                need(file_identity(Path(args.canonical_archive), PACKAGE_BYTES) == {'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA},
                     'CLOSING_ARCHIVE_CHANGED')
                need(post_native_profile_readback(meta, profile, plugins_after, plugins_capture_received,
                     plugins_provider_received, result['config_plugins_profile']['admission_quiescence']) == profile_before and
                     meta.managed_and_ancestor_guard(admission, profile['cwd']) == managed_before and
                     admission.offline_guard(args) == result['offline'], 'CLOSING_STARTUP_OR_NAMESPACE_CHANGED')
                need(meta.quiescent(utility)['verified'] is True, 'CLOSING_GIT_QUIESCENCE_REFUSED')
                need(admission.git_startup_guard(git_home, False, source)[0] == git_before, 'CLOSING_GIT_ADMISSION_CHANGED')
                need(meta.quiescent(utility)['verified'] is True, 'CLOSING_QUIESCENCE_REFUSED')
                result['config_plugins_profile']['closing_unchanged'] = True
                return True
            if observe('CURRENTNESS_AFTER_ADMISSION', closing_admission) is True:
                after = observe('CURRENTNESS_AFTER', lambda: meta.currentness(args, source, gate_home,
                    private, utility, records, deadline, 'currentness-after'))
                result['currentness_after'] = after == result['currentness_receipt_sha256']
                if not result['currentness_after']: route_safe = False
            else: route_safe = False
        if git_before is not None and route_safe and result['currentness_after'] is True:
            def final_git():
                need(meta.quiescent(utility)['verified'] is True, 'FINAL_GIT_QUIESCENCE_REFUSED')
                after, _ = admission.git_startup_guard(git_home, False, source)
                write_private(private / 'GIT_ADMISSION_AFTER.json', canonical(after)); return after
            result['git_admission_unchanged'] = observe('FINAL_GIT', final_git) == git_before
        if source is not None and pins is not None:
            result['control_source_after'] = observe('CONTROL_SOURCE_AFTER', lambda: meta.source_inputs(source, pins)) is True
        if runtime_before is not None:
            result['runtime_after'] = observe('RUNTIME_AFTER', lambda:
                file_identity(Path(args.binary), meta.BINARY_BYTES, executable=True)) == runtime_before
        if package is not None and matrix is not None:
            result['package_after'] = observe('PACKAGE_FINAL', lambda: package_census(package, matrix)) is not None
            result['archive_after'] = observe('ARCHIVE_FINAL', lambda: file_identity(Path(args.canonical_archive), PACKAGE_BYTES)) == \
                                      {'bytes': PACKAGE_BYTES, 'sha256': PACKAGE_SHA}
        if private is not None:
            observe('COMMANDS_RETENTION', lambda: write_private(private / 'COMMANDS.json', canonical(records)))
            def seal_private():
                rows = private_seal_rows(meta, private, record_directory_refusal); path = private / 'PRIVATE_EVIDENCE_SEAL.json'
                raw = canonical({'schema': 'dg17.claude.body-private-seal.v1', 'members': rows})
                write_private(path, raw); result['cleanup']['private_evidence_seal_sha256'] = sha(raw)
                need(private_seal_rows(meta, private, record_directory_refusal) == rows and file_identity(path, len(raw)) == {'bytes': len(raw), 'sha256': sha(raw)},
                     'PRIVATE_SEAL_CHANGED')
                return True
            result['cleanup']['private_seal_unchanged'] = observe('PRIVATE_SEAL', seal_private) is True
        if subreaper:
            result['cleanup']['after_seal'] = observe('AFTER_SEAL', lambda: meta.quiescent(utility))
        if profile is not None and plugins_after is not None and result['cleanup']['after_seal'] is not None and \
                result['cleanup']['after_seal']['verified'] is True:
            def final_startup_readback():
                need(post_native_profile_readback(meta, profile, plugins_after, plugins_capture_received,
                     plugins_provider_received, result['config_plugins_profile']['admission_quiescence']) == profile_before and
                     meta.managed_and_ancestor_guard(admission, profile['cwd']) == managed_before,
                     'FINAL_STARTUP_PROFILE_CHANGED')
                return True
            result['config_plugins_profile']['final_unchanged'] = observe(
                'FINAL_STARTUP_READBACK', final_startup_readback) is True
        # This new diagnostic is passive and follows the original outcome and
        # existing final bookends. It never repairs route_safe or re-enters a gate.
        diagnostic_custody = False
        if meta is not None and transport is not None and utility is not None and subreaper:
            try:
                names = [row.get('name') for row in records]
                good_names = names in (['currentness-before', 'canonical-body'],
                    ['currentness-before', 'canonical-body', 'currentness-after'])
                body = records[1] if good_names else {}
                flags = ('currentness_before', 'control_source_before', 'control_source_after',
                    'runtime_before', 'runtime_after', 'archive_before', 'archive_after',
                    'package_before', 'package_after', 'startup_before', 'startup_after')
                custody = result['provider_custody']; plugin_profile = result['config_plugins_profile']
                def sound_quiescence(value):
                    return (type(value) is dict and set(value) ==
                        {'no_owned_children_listed', 'wait_echild', 'verified'} and
                        all(item is True for item in value.values()))
                diagnostic_custody = (plugins_capture_received and plugins_provider_received and good_names and
                    all(meta.received_capture(row, enriched=row['name'] == 'canonical-body') for row in records) and
                    all(body[key] is True for key in meta.ENRICHMENT_FIELDS - {'recognition_status', 'recognition_code'}) and
                    all(result[key] is True for key in flags) and
                    git_before is not None and store_after == git_before['source_store'] and
                    type(out) is bytes and len(out) == body['stdout_bytes'] and sha(out) == body['stdout_sha256'] and
                    type(custody) is dict and custody['verified'] is True and custody['failure'] is None and
                    custody['supplemental_failures'] == [] and custody['all_owned_sockets_closed'] is True and
                    custody['thread_joined'] is True and type(custody['semantic_request_count']) is int and
                    custody['semantic_request_count'] == 1 and
                    custody['semantic_response_complete'] is True and result['provider_record_sha256'] is not None and
                    plugin_profile['before_absent'] is True and plugin_profile['after'] is not None and
                    plugin_profile['after']['profile_admitted'] is True and plugin_profile['final_unchanged'] is True and
                    sound_quiescence(plugin_profile['admission_quiescence']) and
                    all(sound_quiescence(result['cleanup'][key]) for key in ('after_close', 'after_seal')))
                if diagnostic_custody:
                    diagnostic_custody = sound_quiescence(meta.quiescent(utility))
            except BaseException:
                diagnostic_custody = False
        try:
            expected_context = ({'session_id': session_id, 'cwd': str(profile['cwd']),
                'plugin': str(package), 'model': 'claude-sonnet-4-6'} if profile is not None and package is not None else None)
            result['native_plugin_identity_diagnostic'] = native_plugin_identity_diagnostic(
                out, expected_context, diagnostic_custody, transport)
        except BaseException:
            result['native_plugin_identity_diagnostic'] = empty_native_plugin_diagnostic('JSON_UNRECEIVED')
        if result_path is not None:
            def retain_diagnostics():
                raw = canonical({'schema': 'dg17.claude.body-diagnostics.v1',
                    'startup_paths_after': result['startup_paths_after'], 'directory_refusal': directory_record})
                need(len(raw) <= 16384, 'DIAGNOSTIC_RECORD_BYTE_BOUND')
                write_private(result_path.parent / 'CLAUDE_BODY_DIAGNOSTICS.json', raw)
                return sha(raw)
            result['diagnostic_record_sha256'] = observe('DIAGNOSTIC_RETENTION', retain_diagnostics)
        if meta is not None:
            result['commands'] = [meta.command_public(x) for x in records if x.get('name') == 'canonical-body']
        result['native_sessions_started'] = sum(x.get('process_started') is True for x in result['commands'])
        if meta is None or not complete_result(result, records, meta):
            if result['failure'] is None: failure(Refusal('REQUIRED_EVIDENCE_INCOMPLETE'), 'FINALIZATION')
        else:
            result['status'] = 'OBSERVED_CANONICAL_GOVERNOR_BODY_AND_ADVERTISED_ENTRIES'
        need(len(canonical(result['config_plugins_profile'])) <= 8192, 'CONFIG_PLUGINS_PUBLIC_BYTE_BOUND')
        raw = canonical(result); need(len(raw) <= PUBLIC_LIMIT, 'PUBLIC_RESULT_BYTE_BOUND')
        if result_path is not None:
            try: write_private(result_path, raw)
            except BaseException as exc:
                failure(exc, 'RESULT_RETENTION'); result['status'] = 'INCOMPLETE_OR_FAILED'; raw = canonical(result)
        sys.stdout.buffer.write(raw); sys.stdout.buffer.flush()
    return 0 if result['status'] == 'OBSERVED_CANONICAL_GOVERNOR_BODY_AND_ADVERTISED_ENTRIES' else 1


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    for name in ('source', 'episode', 'binary', 'controller', 'receipt', 'parent-netns',
                 'canonical-archive', 'package-matrix-pins'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--expected-uid', required=True, type=int)
    parser.add_argument('--expected-gid', required=True, type=int)
    return run(parser.parse_args())


if __name__ == '__main__':
    raise SystemExit(main())

