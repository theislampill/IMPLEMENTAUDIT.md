"""One exact Actions checkout correction before fresh controller acquisition.

The source guard is unchanged. Only the literal checkout-created gc.auto=0
entry is removed. No other bytes or configuration keys are normalized.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys

SOURCE_COMMIT = '08e6faa9a71fc09996a32e114346dce6508ef656'
OWNER_SHA = '79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
COMPILER_SHA = '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
LIMIT = 65536
SCHEMA = 'dg16.checkout-gc-auto-preparation.v1'
PHASES = ('ACQUIRE', 'SOURCE_LOAD', 'CANDIDATE_GUARD', 'MUTATE', 'FULL_CONTEXT', 'READBACK', 'DONE')
STATUSES = ('NOT_STARTED', 'IN_PROGRESS', 'EXACT_TARGET_REMOVED_PREFLIGHT_PASS',
            'REFUSED_BEFORE_MUTATION', 'MUTATED_PREFLIGHT_REFUSED', 'MUTATION_OUTCOME_UNRESOLVED')
CODES = ('CHECKOUT_PATH', 'CHECKOUT_DIRECTORY', 'CONFIG_FILE', 'CONFIG_BOUND',
         'CONFIG_CHANGED', 'CONFIG_SYNTAX', 'TARGET_SHAPE', 'TARGET_COUNT',
         'NONFRESH_CHECKOUT', 'SOURCE_PIN', 'LOCK_CHANGED', 'POSTIMAGE_CHANGED',
         'OWNER_PREFLIGHT_REFUSED', 'PREPARATION_OPERATION_REFUSED')

class Refusal(ValueError):
    pass

def need(value, code):
    if not value:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('ascii')

def descriptor(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}

def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

def initial_record():
    return {'schema': SCHEMA, 'operation': 'REMOVE_EXACT_CHECKOUT_GC_AUTO_ZERO_BEFORE_CONTROLLER',
            'status': 'NOT_STARTED', 'phase': 'ACQUIRE', 'target_entries': 0,
            'before': None, 'after': None, 'mutation_completed': False,
            'mutation_boundary_entered': False, 'mutation_intent': None,
            'all_other_bytes_preserved': False, 'unchanged_owner_config_guard': False,
            'unchanged_complete_owner_git_context': False, 'physical_readback': False,
            'controller_acquired_before_preparation': False,
            'context': None, 'diagnostic': None}

def validate_record(value):
    need(type(value) is dict and set(value) == set(initial_record()), 'CONFIG_SYNTAX')
    initial = initial_record()
    for name in ('schema', 'operation', 'controller_acquired_before_preparation'):
        need(type(value[name]) is type(initial[name]) and value[name] == initial[name], 'CONFIG_SYNTAX')
    need(value['status'] in STATUSES and value['phase'] in PHASES, 'CONFIG_SYNTAX')
    need(type(value['target_entries']) is int and value['target_entries'] in (0, 1), 'CONFIG_SYNTAX')
    for name in ('mutation_completed', 'mutation_boundary_entered', 'all_other_bytes_preserved', 'unchanged_owner_config_guard',
                 'unchanged_complete_owner_git_context', 'physical_readback'):
        need(type(value[name]) is bool, 'CONFIG_SYNTAX')
    for name in ('before', 'after', 'context', 'mutation_intent'):
        item = value[name]
        if item is not None:
            need(type(item) is dict and set(item) == {'bytes', 'sha256'} and
                 type(item['bytes']) is int and 0 < item['bytes'] <= (1024**2 if name == 'context' else LIMIT) and
                 type(item['sha256']) is str and re.fullmatch('[0-9a-f]{64}', item['sha256']) is not None, 'CONFIG_SYNTAX')
    need(not value['mutation_completed'] or value['mutation_boundary_entered'], 'CONFIG_SYNTAX')
    need(not value['mutation_boundary_entered'] or value['mutation_intent'] is not None, 'CONFIG_SYNTAX')
    if value['status'] == 'REFUSED_BEFORE_MUTATION':
        need(not value['mutation_boundary_entered'] and not value['mutation_completed'], 'CONFIG_SYNTAX')
    if value['status'] == 'MUTATED_PREFLIGHT_REFUSED':
        need(value['mutation_completed'], 'CONFIG_SYNTAX')
    if value['status'] == 'MUTATION_OUTCOME_UNRESOLVED':
        need(value['mutation_boundary_entered'] and not value['mutation_completed'], 'CONFIG_SYNTAX')
    item = value['diagnostic']
    if item is not None:
        need(type(item) is dict and set(item) == {'code', 'exception_type', 'errno', 'message_bytes', 'message_sha256'} and
             item['code'] in CODES and item['exception_type'] in ('Refusal', 'WorkGraphError', 'OSError', 'OTHER') and
             (item['errno'] is None or type(item['errno']) is int and 0 <= item['errno'] <= 4096) and
             type(item['message_bytes']) is int and 0 <= item['message_bytes'] <= 65536 and
             type(item['message_sha256']) is str and re.fullmatch('[0-9a-f]{64}', item['message_sha256']) is not None, 'CONFIG_SYNTAX')
    if value['status'] == 'EXACT_TARGET_REMOVED_PREFLIGHT_PASS':
        need(value['phase'] == 'DONE' and value['target_entries'] == 1 and value['diagnostic'] is None and
             all(value[key] is True for key in ('mutation_completed', 'all_other_bytes_preserved',
                 'unchanged_owner_config_guard', 'unchanged_complete_owner_git_context', 'physical_readback')) and
             all(value[key] is not None for key in ('before', 'after', 'context', 'mutation_intent')), 'CONFIG_SYNTAX')
    return value

def postimage(raw):
    """Pure exact-entry transformation; all unrelated bytes are retained."""
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, 'CONFIG_BOUND')
    try:
        text = raw.decode('utf-8', 'strict')
    except UnicodeDecodeError:
        raise Refusal('CONFIG_SYNTAX') from None
    need('\x00' not in text and '\\' not in text and '\r' not in text and raw.endswith(b'\n'), 'CONFIG_SYNTAX')
    lines = raw.splitlines(keepends=True)
    section = subsection = None
    header_raw = None
    targets = []
    for index, line in enumerate(lines):
        body = line[:-1].decode('utf-8')
        header = re.fullmatch(r'[ \t]*\[([A-Za-z][A-Za-z0-9-]*)(?: "([A-Za-z0-9][A-Za-z0-9._/-]{0,127})")?\][ \t]*(?:[#;].*)?', body)
        if header:
            section, subsection = header.group(1).lower(), header.group(2)
            header_raw = line
            continue
        entry = re.match(r'[ \t]*([A-Za-z][A-Za-z0-9-]*)[ \t]*=', body)
        if section == 'gc' and subsection is None and entry and entry.group(1).lower() == 'auto':
            need(header_raw == b'[gc]\n' and line == b'\tauto = 0\n', 'TARGET_SHAPE')
            targets.append(index)
    need(len(targets) == 1, 'TARGET_COUNT')
    target = targets[0]
    result = b''.join(lines[:target] + lines[target + 1:])
    need(result != raw and len(raw) - len(result) == len(b'\tauto = 0\n'), 'TARGET_SHAPE')
    return result

def directory_fd(path, *, owned=False):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'CHECKOUT_PATH')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in path.parts[1:]:
            next_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        metadata = os.fstat(fd)
        need(stat.S_ISDIR(metadata.st_mode) and (not owned or
             metadata.st_uid == os.geteuid() and not stat.S_IMODE(metadata.st_mode) & 0o022), 'CHECKOUT_DIRECTORY')
        return fd
    except BaseException:
        os.close(fd)
        raise

def acquire_at(directory, name, *, required=True, maximum=LIMIT):
    try:
        before = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        need(not required, 'CONFIG_FILE')
        return None, None
    need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and
         before.st_nlink == 1 and not stat.S_IMODE(before.st_mode) & 0o022 and
         0 < before.st_size <= maximum, 'CONFIG_FILE')
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        need(stamp(before) == stamp(os.fstat(fd)), 'CONFIG_CHANGED')
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, maximum + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            need(total <= maximum, 'CONFIG_BOUND')
            chunks.append(chunk)
        raw = b''.join(chunks)
        need(len(raw) == before.st_size and stamp(before) == stamp(os.fstat(fd)) ==
             stamp(os.stat(name, dir_fd=directory, follow_symlinks=False)), 'CONFIG_CHANGED')
        return raw, before
    finally:
        os.close(fd)

def load_owner(source, checked_file):
    path = source / 'scripts/qualify-work-graph-verifier.py'
    raw = checked_file(path, 1024**2)
    compiler = checked_file(source / 'skills/implementaudit/scripts/compile-work-graph.py', 1024**2)
    need(sha(raw) == OWNER_SHA and sha(compiler) == COMPILER_SHA, 'SOURCE_PIN')
    spec = importlib.util.spec_from_file_location('fresh_checkout_preflight_owner', path)
    owner = importlib.util.module_from_spec(spec)
    owner._R0035_EFFECT_SOURCE_CAPTURE = {'driver': raw, 'compiler': compiler, 'expected_compiler_sha256': COMPILER_SHA}
    sys.modules[spec.name] = owner
    exec(compile(raw, str(path), 'exec'), owner.__dict__)
    return owner

def intended_environment(runtime, output):
    return {'PATH': str(runtime) + ':/usr/bin:/bin', 'HOME': str(output / 'ordinary-home'),
            'LC_ALL': 'C', 'LANG': 'C', 'TZ': 'UTC', 'CI': 'true', 'GITHUB_ACTIONS': 'true',
            'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_ATTR_NOSYSTEM': '1', 'GIT_OPTIONAL_LOCKS': '0'}

def prepare(source, output, record, checked_file, write_private):
    """Called only in fresh provision, before any owner or custody acquisition."""
    validate_record(record)
    need(record == initial_record(), 'NONFRESH_CHECKOUT')
    private = output / 'private'
    record['status'] = 'IN_PROGRESS'
    source_fd = git_fd = lock_fd = None
    lock_created = committed = False
    environment = dict(os.environ)
    try:
        source_fd = directory_fd(source, owned=True)
        git_fd = directory_fd(source / '.git', owned=True)
        for name in ('commondir', 'gitdir', 'refs/implementaudit'):
            try:
                os.stat(name, dir_fd=git_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise Refusal('NONFRESH_CHECKOUT')
        head, _ = acquire_at(git_fd, 'HEAD')
        need(head == (SOURCE_COMMIT + '\n').encode(), 'NONFRESH_CHECKOUT')
        packed, _ = acquire_at(git_fd, 'packed-refs', required=False)
        need(packed is None or b' refs/implementaudit/' not in packed, 'NONFRESH_CHECKOUT')
        before, metadata = acquire_at(git_fd, 'config')
        record['before'] = descriptor(before)
        candidate = postimage(before)
        record['target_entries'] = 1
        write_private(private / 'checkout-config.before', before)
        write_private(private / 'checkout-config.expected', candidate)
        record['phase'] = 'SOURCE_LOAD'
        owner = load_owner(source, checked_file)
        record['phase'] = 'CANDIDATE_GUARD'
        owner._preflight_git_config_v1(candidate)
        record['unchanged_owner_config_guard'] = True
        record['phase'] = 'MUTATE'
        lock_fd = os.open('config.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          stat.S_IMODE(metadata.st_mode), dir_fd=git_fd)
        lock_created = True
        os.fchmod(lock_fd, stat.S_IMODE(metadata.st_mode))
        remaining = memoryview(candidate)
        while remaining:
            written = os.write(lock_fd, remaining)
            need(written > 0, 'CONFIG_CHANGED')
            remaining = remaining[written:]
        os.fsync(lock_fd)
        lock_info = os.fstat(lock_fd)
        again, again_info = acquire_at(git_fd, 'config')
        need(again == before and stamp(again_info) == stamp(metadata), 'CONFIG_CHANGED')
        need(stamp(lock_info) == stamp(os.stat('config.lock', dir_fd=git_fd, follow_symlinks=False)), 'LOCK_CHANGED')
        intent = {'schema': 'dg16.checkout-config-replace-intent.v1',
                  'operation': 'REPLACE_EXACT_CONFIG_LOCK_TO_CONFIG_ONCE',
                  'before': descriptor(before), 'expected_after': descriptor(candidate),
                  'before_identity': list(stamp(metadata)), 'lock_identity': list(stamp(lock_info)),
                  'original_mode': stat.S_IMODE(metadata.st_mode)}
        intent_raw = encode(intent)
        write_private(private / 'checkout-mutation-intent.json', intent_raw)
        intent_directory = directory_fd(private, owned=True)
        try:
            os.fsync(intent_directory)
        finally:
            os.close(intent_directory)
        record['mutation_intent'] = descriptor(intent_raw)
        # Entering this boundary is not a receipt that the syscall ran. Any
        # interruption until its normal return is observed is explicitly unknown.
        record['mutation_boundary_entered'] = True
        os.replace('config.lock', 'config', src_dir_fd=git_fd, dst_dir_fd=git_fd)
        committed = True
        record['mutation_completed'] = True
        os.fsync(git_fd)
        actual, actual_info = acquire_at(git_fd, 'config')
        need(actual == candidate and actual_info.st_ino == lock_info.st_ino and
             actual_info.st_dev == lock_info.st_dev and stat.S_IMODE(actual_info.st_mode) == stat.S_IMODE(metadata.st_mode), 'POSTIMAGE_CHANGED')
        record['after'] = descriptor(actual)
        record['all_other_bytes_preserved'] = actual == postimage(before)
        write_private(private / 'checkout-config.after', actual)
        record['phase'] = 'FULL_CONTEXT'
        os.environ.clear()
        os.environ.update(intended_environment(private / 'ordinary-venv/bin', private / 'full-pair'))
        context = owner._preflight_git_context_v1()
        raw_context = encode(context['binding'])
        need(0 < len(raw_context) <= 1024**2, 'CONFIG_BOUND')
        write_private(private / 'checkout-complete-context.json', raw_context)
        record['context'] = descriptor(raw_context)
        record['unchanged_complete_owner_git_context'] = True
        record['phase'] = 'READBACK'
        final, final_info = acquire_at(git_fd, 'config')
        need(final == actual and stamp(final_info) == stamp(actual_info), 'POSTIMAGE_CHANGED')
        def directory_identity(info):
            return info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid
        need(directory_identity(os.fstat(source_fd)) == directory_identity(source.lstat()) and
             directory_identity(os.fstat(git_fd)) == directory_identity((source / '.git').lstat()), 'CONFIG_CHANGED')
        record['physical_readback'] = True
        record['phase'] = 'DONE'
        record['status'] = 'EXACT_TARGET_REMOVED_PREFLIGHT_PASS'
    except BaseException as exc:
        record['status'] = ('MUTATED_PREFLIGHT_REFUSED' if record['mutation_completed'] else
                            'MUTATION_OUTCOME_UNRESOLVED' if record['mutation_boundary_entered'] else
                            'REFUSED_BEFORE_MUTATION')
        message = str(exc).encode('utf-8', 'replace')
        kind = type(exc).__name__
        code = str(exc) if type(exc) is Refusal and str(exc) in CODES else (
            'OWNER_PREFLIGHT_REFUSED' if kind == 'WorkGraphError' else 'PREPARATION_OPERATION_REFUSED')
        record['diagnostic'] = {'code': code, 'exception_type': kind if kind in ('Refusal', 'WorkGraphError') else
                                'OSError' if isinstance(exc, OSError) else 'OTHER',
                                'errno': exc.errno if isinstance(exc, OSError) and type(exc.errno) is int and 0 <= exc.errno <= 4096 else None,
                                'message_bytes': len(message), 'message_sha256': sha(message)}
        raise Refusal(code) from None
    finally:
        os.environ.clear()
        os.environ.update(environment)
        if lock_created and not committed and git_fd is not None and lock_fd is not None:
            try:
                linked = os.stat('config.lock', dir_fd=git_fd, follow_symlinks=False)
                if (linked.st_dev, linked.st_ino) == (os.fstat(lock_fd).st_dev, os.fstat(lock_fd).st_ino):
                    os.unlink('config.lock', dir_fd=git_fd)
            except FileNotFoundError:
                pass
        for fd in (lock_fd, git_fd, source_fd):
            if fd is not None:
                os.close(fd)
        validate_record(record)
        write_private(private / 'checkout-preparation.json', encode(record))

def readback(output, record, checked_file):
    validate_record(record)
    if record['status'] == 'NOT_STARTED':
        return record
    private = output / 'private'
    need(checked_file(private / 'checkout-preparation.json', 16384) == encode(record), 'POSTIMAGE_CHANGED')
    if record['before'] is not None and record['target_entries'] == 1:
        before = checked_file(private / 'checkout-config.before', LIMIT)
        expected = checked_file(private / 'checkout-config.expected', LIMIT)
        need(descriptor(before) == record['before'] and expected == postimage(before), 'POSTIMAGE_CHANGED')
    if record['after'] is not None:
        actual = checked_file(private / 'checkout-config.after', LIMIT)
        need(descriptor(actual) == record['after'] and actual == expected, 'POSTIMAGE_CHANGED')
    if record['context'] is not None:
        need(descriptor(checked_file(private / 'checkout-complete-context.json', 1024**2)) == record['context'], 'POSTIMAGE_CHANGED')
    if record['mutation_intent'] is not None:
        need(descriptor(checked_file(private / 'checkout-mutation-intent.json', LIMIT)) == record['mutation_intent'], 'POSTIMAGE_CHANGED')
    return record
