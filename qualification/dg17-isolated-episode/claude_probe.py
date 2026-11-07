#!/usr/bin/env python3
"""DG17 Claude child08 exact validation target successor; prospective hosted execution only.

Exactly validate/list/details; no version/help/install/auth/session/model call.
The enclosing separately reviewed parent owns actual source/controller/capsule/
resource/effect admission. This is not recovery of lost historical child03 bytes.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import sys
import time

SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
ARCHIVE_BYTES = 155477886
ARCHIVE_SHA256 = 'e6d426ca0c123f61fad58a361da0329f2a93cd206bc87040ed8d9576dd9eb583'
BINARY_BYTES = 337814032
BINARY_SHA256 = '708c77b204db30086ff6f1ed34577bda03e1be74ced80557cbf7b54249ebf0bd'
HELPER_SHA256 = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
ADMISSION_SHA256 = 'b6e13ead54247adfe181ba9e4ea1739bbceb336d89fba0c6aee111462699b551'
PINS_SHA256 = 'd5e1e1e9abeeaa79500acc0c41f1555df4a1dc6e5a50259a94db8895500edaad'
SKILLS = ('implementaudit', 'audit-state', 'audit-assess', 'audit-implement', 'audit-andon')
COMMANDS = ('validate', 'list', 'details')
SETTINGS = {'disableAllHooks': True, 'syncClaudeAiSkills': False,
            'syncClaudeAiPlugins': False, 'disableClaudeAiConnectors': True,
            'remoteControlAtStartup': False}
MCP_CONFIG = {'mcpServers': {}}
PUBLIC_LIMIT = 32768
JSON_LIMIT = 32768
RUN_SECONDS = 125
COMMAND_SECONDS = 20
BASE_FIELDS = frozenset(('name', 'process_started', 'returncode', 'timeout',
    'output_bound_exceeded', 'pidfd_acquired', 'internal_failure', 'reason_code',
    'stream_digest_scope', 'streams_complete', 'stdout_bytes', 'stderr_bytes',
    'stdout_sha256', 'stderr_sha256', 'cleanup', 'private_streams_retained', 'retention_failure'))
CLEANUP_FIELDS = frozenset(('echild', 'pidfd_signals', 'retained_status_count',
    'retained_statuses_sha256', 'reaped_statuses', 'reaped_statuses_truncated'))
ENRICHMENT_FIELDS = frozenset(('recognition_status', 'recognition_code', 'source_before',
    'source_after', 'runtime_before', 'runtime_after', 'startup_before', 'startup_after'))
CONTINUABLE_RECOGNITION_CODES = frozenset(('JSON_BYTE_BOUND_REFUSED',
    'JSON_PARSE_UNRECEIVED', 'JSON_DUPLICATE_KEY_UNRECEIVED', 'JSON_NONFINITE_UNRECEIVED',
    'JSON_COMPLEXITY_UNRECEIVED', 'JSON_SHAPE_UNRECEIVED', 'VALIDATION_SHAPE_UNRECEIVED',
    'VALIDATION_CONTENTS_UNRECEIVED', 'VALIDATION_ADVICE_UNRECEIVED', 'LIST_SHAPE_UNRECEIVED',
    'LIST_DIAGNOSTICS_UNRECEIVED'))


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


def json_bounds(value):
    todo = [(value, 0)]
    count = 0
    while todo:
        item, depth = todo.pop()
        count += 1
        need(count <= 2048 and depth <= 12, 'JSON_COMPLEXITY_UNRECEIVED')
        if type(item) is dict:
            need(len(item) <= 128 and all(type(k) is str and len(k) <= 256 for k in item),
                 'JSON_SHAPE_UNRECEIVED')
            todo.extend((v, depth + 1) for v in item.values())
        elif type(item) is list:
            need(len(item) <= 256, 'JSON_SHAPE_UNRECEIVED')
            todo.extend((v, depth + 1) for v in item)
        elif type(item) is str:
            need(len(item) <= 8192, 'JSON_SHAPE_UNRECEIVED')
        elif item is None or type(item) is bool:
            pass
        elif type(item) is int:
            need(abs(item) <= 2**53, 'JSON_SHAPE_UNRECEIVED')
        else:
            raise Refusal('JSON_SHAPE_UNRECEIVED')
    return value


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= JSON_LIMIT, 'JSON_BYTE_BOUND_REFUSED')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE_KEY_UNRECEIVED')
            result[key] = value
        return result
    def nonfinite(_):
        raise Refusal('JSON_NONFINITE_UNRECEIVED')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                           parse_constant=nonfinite)
    except (UnicodeError, ValueError, RecursionError):
        raise Refusal('JSON_PARSE_UNRECEIVED') from None
    return json_bounds(value)


def public_json_type(value):
    if value is None:
        return 'NULL'
    kinds = {bool: 'BOOLEAN', int: 'INTEGER', str: 'STRING',
             list: 'ARRAY', dict: 'OBJECT'}
    need(type(value) in kinds, 'JSON_SHAPE_UNRECEIVED')
    return kinds[type(value)]


def validation_shape_projection(value):
    # Called only after strict_json; no arbitrary key or value is projected.
    known = ('success', 'strict', 'target', 'manifest', 'contents', 'advice',
             'gatingHooks', 'directory')
    is_object = type(value) is dict
    fields = {}
    for key in known:
        present = is_object and key in value
        item = value[key] if present else None
        fields[key] = {'present': present,
                       'type': public_json_type(item) if present else 'ABSENT',
                       'count': len(item) if present and type(item) in (dict, list) else None}
    unknown = sorted(set(value) - set(known)) if is_object else None
    return {'status': 'PUBLIC_SAFE_TOP_LEVEL_SHAPE_ONLY',
            'root_type': public_json_type(value),
            'root_count': len(value) if type(value) in (dict, list) else None,
            'unknown_key_count': len(unknown) if is_object else None,
            'unknown_key_names_sha256': sha(canonical(unknown)) if is_object else None,
            'fields': fields}


def validation_identity_projection(value, source):
    # Diagnostics precede acceptance; no returned path is resolved or exported.
    is_object = type(value) is dict
    target = value.get('target') if is_object else None
    relation = 'NON_STRING_OR_ABSENT'; raw = None
    if type(target) is str:
        try:
            raw = target.encode('utf-8')
        except UnicodeError:
            relation = 'NON_UTF8_STRING'
        else:
            if target == str(source):
                relation = 'EXACT_SOURCE_DIRECTORY'
            elif target == str(source / '.claude-plugin/marketplace.json'):
                relation = 'EXACT_SELECTED_MARKETPLACE_MANIFEST'
            elif target == str(source / '.claude-plugin/plugin.json'):
                relation = 'EXACT_PLUGIN_MANIFEST'
            else:
                relation = 'OTHER_STRING'
    return {'status': 'PUBLIC_SAFE_IDENTITY_AND_VERDICT_ONLY',
            'success_is_true': is_object and value.get('success') is True,
            'strict_is_false': is_object and value.get('strict') is False,
            'target_relation': relation,
            'target_bytes': len(raw) if raw is not None else None,
            'target_sha256': sha(raw) if raw is not None else None,
            'target_is_source_bound': relation in ('EXACT_SOURCE_DIRECTORY',
                                                  'EXACT_SELECTED_MARKETPLACE_MANIFEST')}


def validation_projection(value, source):
    required = {'success', 'strict', 'target', 'manifest', 'contents', 'advice'}
    need(type(value) is dict and required <= set(value) and
         set(value) <= required | {'gatingHooks', 'directory'} and
         type(value['success']) is bool and type(value['strict']) is bool and
         type(value['target']) is str and
         (value['manifest'] is None or type(value['manifest']) is dict) and
         type(value['contents']) is list and type(value['advice']) is list and
         ('directory' not in value or value['directory'] is None or
          type(value['directory']) is dict),
         'VALIDATION_SHAPE_UNRECEIVED')
    identity = validation_identity_projection(value, source)
    need(value['success'] is True and value['strict'] is False and
         identity['target_is_source_bound'] is True, 'VALIDATION_IDENTITY_OR_VERDICT_REFUSED')
    errors = warnings = notes = 0
    for row in value['contents']:
        need(type(row) is dict and {'file', 'errors', 'warnings', 'notes'} <= set(row) and
             set(row) <= {'file', 'errors', 'warnings', 'notes', 'gatingHooks'} and
             type(row['file']) is str and all(type(row[k]) is list and
             all(type(v) is str for v in row[k]) for k in ('errors', 'warnings', 'notes')),
             'VALIDATION_CONTENTS_UNRECEIVED')
        need(row.get('gatingHooks', []) == [], 'UNEXPECTED_GATING_HOOKS_REFUSED')
        errors += len(row['errors']); warnings += len(row['warnings']); notes += len(row['notes'])
    need(value.get('gatingHooks', []) == [], 'UNEXPECTED_GATING_HOOKS_REFUSED')
    for row in value['advice']:
        need(type(row) is dict and set(row) == {'file', 'message', 'installLine'} and
             all(type(row[k]) is str for k in row), 'VALIDATION_ADVICE_UNRECEIVED')
    need(errors == 0, 'VALIDATION_CONTENT_ERRORS_REFUSED')
    return {'status': 'DOCUMENTED_OUTER_VALIDATION_OBSERVED', 'success': True,
            'strict': False, 'target_is_source_bound': True,
            'target_relation': identity['target_relation'],
            'target_matches_source_directory': identity['target_relation'] == 'EXACT_SOURCE_DIRECTORY',
            'error_count': errors,
            'warning_count': warnings, 'note_count': notes,
            'diagnostic_count_scope': 'CONTENTS_ONLY_MANIFEST_OPAQUE',
            'contents_count': len(value['contents']), 'advice_count': len(value['advice']),
            'manifest_semantics': 'UNRECEIVED_OPAQUE_OBJECT',
            'manifest_is_null': value['manifest'] is None,
            'manifest_json_sha256': sha(canonical(value['manifest'])),
            'directory_state': ('ABSENT' if 'directory' not in value else
                                'NULL' if value['directory'] is None else 'OPAQUE_OBJECT'),
            'directory_json_sha256': sha(canonical(value['directory'])) if 'directory' in value else None,
            'directory_semantics': 'UNRECEIVED_OPAQUE_METADATA',
            'directory_validation_received': False,
            'native_five_skill_inventory_received': False}


def list_projection(value, source):
    need(type(value) is list and len(value) == 1 and type(value[0]) is dict,
         'LIST_SHAPE_UNRECEIVED')
    row = value[0]
    required = {'id', 'version', 'scope', 'enabled', 'installPath'}
    allowed = required | {'readFromFolder', 'folderVersion', 'errors', 'notes',
                          'errorDetails', 'noteDetails', 'mcpServers', 'hasUserConfig'}
    need(required <= set(row) <= allowed and all(type(row[k]) is str for k in
         ('id', 'version', 'scope', 'installPath')) and type(row['enabled']) is bool,
         'LIST_SHAPE_UNRECEIVED')
    for key in ('readFromFolder', 'folderVersion'):
        need(key not in row or type(row[key]) is str, 'LIST_SHAPE_UNRECEIVED')
    for key in ('errors', 'notes'):
        need(key not in row or (type(row[key]) is list and all(type(x) is str for x in row[key])),
             'LIST_DIAGNOSTICS_UNRECEIVED')
    for key in ('errorDetails', 'noteDetails'):
        need(key not in row or (type(row[key]) is list and all(type(x) is dict for x in row[key])),
             'LIST_DIAGNOSTICS_UNRECEIVED')
    need(row['id'] == 'implementaudit@inline' and row['version'] == '0.4.0' and
         row['scope'] == 'session' and row['enabled'] is True and
         row.get('readFromFolder', row['installPath']) == str(source) and
         row.get('folderVersion', '0.4.0') == '0.4.0', 'LIST_IDENTITY_REFUSED')
    need(row.get('errors', []) == [] and row.get('errorDetails', []) == [],
         'LIST_LOAD_ERRORS_REFUSED')
    need(row.get('mcpServers', {}) == {} and row.get('hasUserConfig', False) is False,
         'LIST_EXECUTABLE_CONFIGURATION_REFUSED')
    return {'status': 'EXACT_SESSION_CANDIDATE_OBSERVED', 'id': 'implementaudit@inline',
            'version': '0.4.0', 'scope': 'session', 'enabled': True,
            'effective_path_matches_source': True, 'plugin_count': 1, 'load_error_count': 0,
            'note_count': len(row.get('notes', [])),
            'native_five_skill_inventory_received': False}


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


def load_pinned_module(root, name, expected):
    path = root / (name + '.py')
    need(file_identity(path, 131072)['sha256'] == expected, 'DEPENDENCY_PIN_DIFFERS')
    spec = importlib.util.spec_from_file_location('dg17_claude04_' + name, path)
    need(spec is not None and spec.loader is not None, 'DEPENDENCY_LOADER_UNAVAILABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(file_identity(path, 131072)['sha256'] == expected, 'DEPENDENCY_CHANGED_DURING_LOAD')
    return module


def source_inputs(source, pins):
    need(pins['source_commit'] == SOURCE_COMMIT and pins['source_tree'] == SOURCE_TREE and
         pins['expected_skills'] == list(SKILLS), 'SOURCE_PIN_SET_DIFFERS')
    for row in pins['members']:
        need(file_identity(source / row['path'], row['bytes']) ==
             {'bytes': row['bytes'], 'sha256': row['sha256']}, 'CONSUMED_SOURCE_INPUT_DIFFERS')
    for name in ('commands', 'agents', 'hooks', '.mcp.json', '.lsp.json', 'settings.json',
                 'output-styles', 'mods'):
        need(not os.path.lexists(source / name), 'UNEXPECTED_PLUGIN_STARTUP_COMPONENT')
    with os.scandir(source / 'skills') as entries:
        names = sorted(entry.name for entry in entries)
    need(names == sorted(SKILLS), 'SOURCE_SKILL_POPULATION_DIFFERS')
    return True


def managed_and_ancestor_guard(admission, cwd):
    managed = admission.root_path_identity(Path('/etc/claude-code'), absent_ok=True)
    need(managed['present'] is False, 'MANAGED_CLAUDE_POLICY_PRESENT')
    for parent in (cwd, *cwd.parents):
        for name in ('.claude', '.mcp.json', 'CLAUDE.md', 'CLAUDE.local.md'):
            need(not os.path.lexists(parent / name), 'UNREVIEWED_ANCESTOR_STARTUP_LAYER')
    return managed


def fresh_profile(private, name, admission):
    root = private / ('context-' + name)
    need(not os.path.lexists(root), 'CONTEXT_NOT_FRESH')
    root.mkdir(mode=0o700)
    paths = {'root': root}
    for key in ('home', 'config', 'xdg_config', 'xdg_cache', 'xdg_data', 'xdg_state', 'cwd'):
        path = root / key; path.mkdir(mode=0o700); paths[key] = path
    paths['settings'] = root / 'selected-settings.json'
    paths['mcp'] = root / 'empty-mcp.json'
    write_private(paths['settings'], canonical(SETTINGS))
    write_private(paths['mcp'], canonical(MCP_CONFIG))
    snapshot = profile_readback(paths)
    return paths, snapshot, managed_and_ancestor_guard(admission, paths['cwd'])


def profile_readback(paths):
    rows = {key: owned_directory(path) for key, path in paths.items()
            if key not in ('settings', 'mcp')}
    for key, value in (('settings', SETTINGS), ('mcp', MCP_CONFIG)):
        raw = canonical(value)
        need(file_identity(paths[key], len(raw)) == {'bytes': len(raw), 'sha256': sha(raw)},
             'SELECTED_STARTUP_CONFIG_CHANGED')
    forbidden = [paths['home'] / '.claude', paths['home'] / '.claude.json',
                 paths['home'] / '.config/anthropic', paths['home'] / '.config/claude',
                 paths['xdg_config'] / 'anthropic', paths['xdg_config'] / 'claude',
                 paths['config'] / 'settings.json', paths['config'] / 'settings.local.json',
                 paths['config'] / '.credentials.json', paths['config'] / 'credentials.json',
                 paths['config'] / 'managed-settings.json', paths['config'] / 'managed-mcp.json',
                 paths['config'] / 'plugins', paths['config'] / 'skills', paths['config'] / 'hooks',
                 paths['config'] / 'mcp.json', paths['config'] / '.mcp.json']
    need(all(not os.path.lexists(p) for p in forbidden), 'UNREVIEWED_FRESH_CONTEXT_STARTUP_LAYER')
    return rows


def command_argv(binary, source, profile, name):
    prefix = [str(binary), '--setting-sources', 'user', '--settings', str(profile['settings']),
              '--strict-mcp-config', '--mcp-config', str(profile['mcp']), '--no-chrome']
    if name == 'validate':
        return prefix + ['plugin', 'validate', str(source), '--json']
    if name == 'list':
        return prefix + ['--plugin-dir', str(source), 'plugin', 'list', '--json']
    need(name == 'details', 'UNDECLARED_PRODUCT_COMMAND')
    return prefix + ['--plugin-dir', str(source), 'plugin', 'details', 'implementaudit']


def command_environment(utility, profile):
    env = utility.safe_environment()
    env.update(HOME=str(profile['home']), CLAUDE_CONFIG_DIR=str(profile['config']),
               XDG_CONFIG_HOME=str(profile['xdg_config']), XDG_CACHE_HOME=str(profile['xdg_cache']),
               XDG_DATA_HOME=str(profile['xdg_data']), XDG_STATE_HOME=str(profile['xdg_state']),
               CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC='1', DISABLE_UPDATES='1',
               DISABLE_TELEMETRY='1', DISABLE_ERROR_REPORTING='1')
    return env


def received_capture(record, enriched=False):
    if type(record) is not dict or set(record) != BASE_FIELDS | (ENRICHMENT_FIELDS if enriched else set()):
        return False
    c = record.get('cleanup')
    if type(c) is not dict or set(c) != CLEANUP_FIELDS:
        return False
    if not (record['process_started'] is True and type(record['returncode']) is int and
            record['returncode'] == 0 and record['timeout'] is False and
            record['output_bound_exceeded'] is False and record['pidfd_acquired'] is True and
            record['internal_failure'] is None and record['streams_complete'] is True and
            record['private_streams_retained'] is True and record['retention_failure'] is False and
            record['stream_digest_scope'] == 'CAPTURED_BYTES_ONLY' and
            type(record['reason_code']) is str and
            re.fullmatch(r'[A-Z0-9_]{1,96}', record['reason_code']) is not None):
        return False
    for prefix in ('stdout', 'stderr'):
        if not (type(record[prefix + '_bytes']) is int and 0 <= record[prefix + '_bytes'] <= 32768 and
                type(record[prefix + '_sha256']) is str and
                re.fullmatch('[0-9a-f]{64}', record[prefix + '_sha256'])):
            return False
    if not (c['echild'] is True and type(c['pidfd_signals']) is int and 0 <= c['pidfd_signals'] <= 4096 and
            type(c['retained_status_count']) is int and 0 <= c['retained_status_count'] <= 4096 and
            type(c['retained_statuses_sha256']) is str and re.fullmatch('[0-9a-f]{64}', c['retained_statuses_sha256']) and
            type(c['reaped_statuses']) is list and len(c['reaped_statuses']) == min(8, c['retained_status_count']) and
            c['reaped_statuses_truncated'] is (c['retained_status_count'] > 8)):
        return False
    return all(type(r) is dict and set(r) == {'pid', 'returncode'} and
               type(r['pid']) is int and r['pid'] > 0 and type(r['returncode']) is int
               for r in c['reaped_statuses'])


def retain_capture(utility, name, argv, cwd, env, private, records, deadline, seconds):
    before = len(records); out = err = None; rc = None; original = None
    saved_env = utility.safe_environment; saved_cwd = Path.cwd()
    try:
        utility.safe_environment = lambda: dict(env)
        os.chdir(cwd)
        try:
            rc, out, err = utility.capture(name, argv, records, deadline, seconds=seconds)
        except BaseException as exc:
            original = exc
            captured = getattr(exc, 'captured', None)
            if type(captured) is dict:
                rc, out, err = captured.get('returncode'), captured.get('stdout'), captured.get('stderr')
    finally:
        utility.safe_environment = saved_env
        os.chdir(saved_cwd)
    need(len(records) == before + 1 and records[-1].get('name') == name,
         'CAPTURE_RECORD_POPULATION_REFUSED')
    row = records[-1]
    row['private_streams_retained'] = False; row['retention_failure'] = False
    retention_error = None
    try:
        need(type(out) is bytes and type(err) is bytes, 'PRIVATE_CAPTURE_BYTES_UNAVAILABLE')
        for label, raw in (('stdout', out), ('stderr', err)):
            need(len(raw) == row.get(label + '_bytes') and sha(raw) == row.get(label + '_sha256'),
                 'PRIVATE_CAPTURE_IDENTITY_DIFFERS')
            write_private(private / (name + '.' + label), raw)
        row['private_streams_retained'] = True
    except BaseException as exc:
        retention_error = exc; row['retention_failure'] = True
    try:
        write_private(private / (name + '.capture.json'), canonical([row]))
    except BaseException as exc:
        row['retention_failure'] = True
        if retention_error is None: retention_error = exc
    if original is not None:
        raise original
    if retention_error is not None:
        raise retention_error
    need(received_capture(row), 'CAPTURE_OR_COMMAND_REFUSED')
    return rc, out, err


def currentness(args, source, home, private, utility, records, deadline, label):
    env = utility.safe_environment(); env.update(HOME=str(home), IMPLEMENTAUDIT_PYTHON=sys.executable)
    rc, out, err = retain_capture(utility, label,
        ['/usr/bin/bash', str(source / 'skills/implementaudit/scripts/claim-run.sh'),
         '--require-current-continuity', args.controller], source, env,
        private, records, deadline, 15)
    need(rc == 0 and out == (args.receipt + '\n').encode('ascii'), 'CURRENTNESS_GATE_REFUSED')
    return sha(out)


def quiescent(utility):
    none_listed = utility.children() == []
    try:
        os.waitpid(-1, os.WNOHANG | 0x40000000); echild = False
    except ChildProcessError:
        echild = True
    return {'no_owned_children_listed': none_listed, 'wait_echild': echild,
            'verified': none_listed and echild}


def seal_rows(root):
    rows = []; total = 0; pending = [root]
    while pending:
        parent = pending.pop()
        try:
            with os.scandir(parent) as entries:
                names = []
                for entry in entries:
                    names.append(entry.name)
                    need(len(names) <= 513, 'PRIVATE_SEAL_POPULATION_BOUND')
            for name in sorted(names):
                path = Path(parent) / name
                if path == root / 'PRIVATE_EVIDENCE_SEAL.json':
                    continue
                relative = path.relative_to(root)
                need(len(relative.parts) <= 16 and len(rows) < 512, 'PRIVATE_SEAL_POPULATION_BOUND')
                info = path.lstat()
                need(not stat.S_ISLNK(info.st_mode), 'PRIVATE_SEAL_LINK_REFUSED')
                if stat.S_ISDIR(info.st_mode):
                    owned_directory(path)
                    rows.append({'path': relative.as_posix(), 'kind': 'DIRECTORY'}); pending.append(path)
                else:
                    identity = file_identity(path, 8 * 1024 * 1024); total += identity['bytes']
                    need(total <= 32 * 1024 * 1024, 'PRIVATE_SEAL_BYTE_BOUND')
                    rows.append({'path': relative.as_posix(), 'kind': 'REGULAR', **identity})
        except OSError as exc:
            raise Refusal('PRIVATE_SEAL_ENUMERATION_REFUSED') from exc
    return sorted(rows, key=lambda row: row['path'])


def command_public(row):
    c = row.get('cleanup') or {}
    result = {'name': row['name'], 'returncode': row.get('returncode'),
              'stdout_bytes': row.get('stdout_bytes'), 'stdout_sha256': row.get('stdout_sha256'),
              'stderr_bytes': row.get('stderr_bytes'), 'stderr_sha256': row.get('stderr_sha256'),
              'recognition_status': row.get('recognition_status', 'NOT_ATTEMPTED'),
              'recognition_code': row.get('recognition_code'),
              'internal_failure': row.get('internal_failure') is not None,
              'stderr_present': row['stderr_bytes'] > 0 if type(row.get('stderr_bytes')) is int else None,
              'owned_cleanup_echild': c.get('echild') is True,
              'owned_reaped_status_count': c.get('retained_status_count'),
              'owned_statuses_sha256': c.get('retained_statuses_sha256')}
    for key in ('process_started', 'streams_complete', 'timeout', 'output_bound_exceeded',
                'pidfd_acquired', 'private_streams_retained', 'retention_failure',
                'source_before', 'source_after', 'runtime_before', 'runtime_after',
                'startup_before', 'startup_after'):
        result[key] = row.get(key) is True
    return result


def failure_value(exc, phase, utility=None, admission=None):
    types = (Refusal,) + tuple(x.Refusal for x in (utility, admission) if x is not None)
    code = str(exc) if isinstance(exc, types) else 'OPERATION_EXCEPTION'
    if re.fullmatch(r'[A-Z][A-Z0-9_]{0,95}', code) is None:
        code = 'OPERATION_EXCEPTION'
    return {'phase': phase, 'code': code,
            'exception_type': 'Refusal' if isinstance(exc, types) else 'Exception'}


def initial_result():
    return {'schema': 'dg17.claude.source-candidate.v1', 'status': 'INCOMPLETE_OR_FAILED',
        'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
        'archive_bytes': ARCHIVE_BYTES, 'archive_sha256': ARCHIVE_SHA256,
        'runtime_bytes': BINARY_BYTES, 'runtime_sha256': BINARY_SHA256,
        'runtime_release_tag_declared': 'v2.1.318', 'runtime_version_self_reported': False,
        'managed_policy_absent': False, 'currentness_before': False, 'currentness_after': False,
        'currentness_receipt_sha256': None, 'consumed_source_before': False,
        'consumed_source_after': False, 'runtime_before': False, 'runtime_after': False,
        'git_admission_unchanged': False, 'parent_full_source_admission_required': True,
        'native_five_skill_inventory_received': False, 'original_acceptance_awarded': False,
        'persistent_installation_proven': False, 'model_inference_proven': False,
        'prompt_independent_routing_proven': False, 'independent_receiving': 'NOT_PERFORMED',
        'expected_source_skills': list(SKILLS), 'fresh_context_count': 0,
        'product_commands_started': 0, 'planned_commands': list(COMMANDS),
        'unstarted_commands': list(COMMANDS), 'offline': None, 'commands': [],
        'validation_shape': None, 'validation_identity': None,
        'validation': None, 'plugin_list': None, 'details': None,
        'cleanup': {'private_evidence_seal_sha256': None, 'private_seal_unchanged': False,
                    'private_plaintext_policy': 'RETAIN_UNTIL_HOST_TEARDOWN',
                    'host_teardown_observed': False, 'after_close': None, 'after_seal': None},
        'failure': None, 'supplemental_failures': []}


def complete_result(result, records):
    if result['failure'] is not None or result['supplemental_failures']:
        return False
    if not all(result[k] is True for k in ('managed_policy_absent', 'currentness_before',
        'currentness_after', 'consumed_source_before', 'consumed_source_after',
        'runtime_before', 'runtime_after', 'git_admission_unchanged')):
        return False
    if not (result['offline'] and result['offline']['verified'] is True and
            result['fresh_context_count'] == 3 and
            [r.get('name') for r in records] == ['currentness-before', *COMMANDS, 'currentness-after']):
        return False
    for row in records:
        product = row['name'] in COMMANDS
        if not received_capture(row, enriched=product):
            return False
        if product and (not all(row[k] is True for k in ENRICHMENT_FIELDS -
            {'recognition_status', 'recognition_code'}) or row['recognition_code'] is not None or
            row['recognition_status'] != ('TEXT_UNRECEIVED' if row['name'] == 'details' else 'RECEIVED_JSON')):
            return False
    return (result['validation'] is not None and result['plugin_list'] is not None and
            result['details'] is not None and result['cleanup']['private_seal_unchanged'] is True and
            all(result['cleanup'][k] is not None and result['cleanup'][k]['verified'] is True
                for k in ('after_close', 'after_seal')))


def public_bytes(result):
    encoded = canonical(result)
    need(len(encoded) <= PUBLIC_LIMIT, 'PUBLIC_RESULT_BYTE_BOUND')
    return encoded


def run(args):
    result = initial_result(); records = []; profiles = []
    utility = admission = source = pins = private = result_path = runtime_before = git_before = None
    gate_home = git_home = None; subreaper = False; phase = 'PRECONDITIONS'
    executable_route_safe = False
    deadline = time.monotonic() + RUN_SECONDS
    def record_failure(exc, where):
        value = failure_value(exc, where, utility, admission)
        if value == result['failure'] or value in result['supplemental_failures']:
            return
        if result['failure'] is None: result['failure'] = value
        else: result['supplemental_failures'].append(value)
    def supplement(where, action):
        try: return action()
        except BaseException as exc: record_failure(exc, where); return None
    try:
        root = Path(__file__).resolve(strict=True).parent
        utility = load_pinned_module(root, 'host_utility', HELPER_SHA256)
        admission = load_pinned_module(root, 'catalogue_probe', ADMISSION_SHA256)
        result['offline'] = admission.offline_guard(args)
        need(re.fullmatch(r'[a-z0-9][a-z0-9-]{0,95}', args.controller) is not None and
             re.fullmatch(r'refs/implementaudit/continuity-receipts/' + re.escape(args.controller) +
                          r'/G[0-9]{4}@[0-9a-f]{40}', args.receipt) is not None,
             'CONTINUITY_ARGUMENTS_DIFFER')
        source = Path(args.source)
        need(source.is_absolute() and source.resolve(strict=True) == source, 'SOURCE_NOT_PHYSICAL')
        episode = Path(args.episode)
        need(episode.is_absolute() and episode.resolve(strict=True) == episode, 'EPISODE_NOT_PHYSICAL')
        envelope = episode / 'private'; gate_home = episode / 'home'
        owned_directory(envelope); owned_directory(gate_home)
        candidate = envelope / 'claude-source-candidate'
        need(not os.path.lexists(candidate) and not candidate.is_relative_to(source) and
             not source.is_relative_to(candidate), 'WORK_ROOT_NOT_FRESH_OR_OVERLAPPING')
        candidate.mkdir(mode=0o700)
        private = candidate
        result_path = envelope / 'CLAUDE_RESULT.json'
        need(not os.path.lexists(result_path), 'RESULT_ALREADY_EXISTS')
        git_home = private / 'git-home'; git_home.mkdir(mode=0o700)
        need(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL, 'CHILD_REAP_POLICY_UNREVIEWED')
        libc = ctypes.CDLL(None, use_errno=True)
        need(libc.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_SETUP_REFUSED'); subreaper = True
        need(file_identity(root / 'SOURCE_INPUT_PINS.json', 32768)['sha256'] == PINS_SHA256,
             'SOURCE_PIN_FILE_DIFFERS')
        pins = strict_json((root / 'SOURCE_INPUT_PINS.json').read_bytes())
        admission.source_store_guard(source)
        admission.source_guard(source, gate_home)
        result['consumed_source_before'] = source_inputs(source, pins)
        runtime_before = file_identity(Path(args.binary), BINARY_BYTES, executable=True)
        need(runtime_before == {'bytes': BINARY_BYTES, 'sha256': BINARY_SHA256}, 'RUNTIME_IDENTITY_DIFFERS')
        result['runtime_before'] = True
        phase = 'CURRENTNESS_BEFORE'
        result['currentness_receipt_sha256'] = currentness(args, source, gate_home, private,
            utility, records, deadline, 'currentness-before')
        result['currentness_before'] = True
        phase = 'GIT_ADMISSION_BEFORE'
        git_before, _ = admission.git_startup_guard(git_home, True, source)
        write_private(private / 'GIT_ADMISSION_BEFORE.json', canonical(git_before))
        executable_route_safe = True
        for name in COMMANDS:
            phase = name + '_ADMISSION'
            need(time.monotonic() < deadline, 'RUN_WATCHDOG')
            profile, profile_before, managed_before = fresh_profile(private, name, admission)
            profiles.append((profile, profile_before, managed_before))
            result['fresh_context_count'] = len(profiles); result['managed_policy_absent'] = True
            need(admission.source_store_guard(source) == git_before['source_store'],
                 'SOURCE_STORE_BEFORE_COMMAND_CHANGED')
            source_inputs(source, pins)
            need(file_identity(Path(args.binary), BINARY_BYTES, executable=True) == runtime_before,
                 'RUNTIME_BEFORE_COMMAND_CHANGED')
            need(quiescent(utility)['verified'] is True, 'COMMAND_ADMISSION_QUIESCENCE_REFUSED')
            phase = name + '_CAPTURE'
            start = len(records); recognition_error = None
            try:
                rc, out, err = retain_capture(utility, name, command_argv(Path(args.binary), source, profile, name),
                    profile['cwd'], command_environment(utility, profile), private, records, deadline, COMMAND_SECONDS)
                row = records[-1]
                row.update(recognition_status='NOT_ATTEMPTED', recognition_code=None,
                    source_before=True, source_after=False, runtime_before=True, runtime_after=False,
                    startup_before=True, startup_after=False)
                phase = name + '_RECOGNITION'
                try:
                    if name == 'validate':
                        parsed_validation = strict_json(out)
                        result['validation_shape'] = validation_shape_projection(parsed_validation)
                        result['validation_identity'] = validation_identity_projection(parsed_validation, source)
                        result['validation'] = validation_projection(parsed_validation, source)
                    elif name == 'list':
                        result['plugin_list'] = list_projection(strict_json(out), source)
                    else:
                        result['details'] = {'status': 'TEXT_FORMAT_UNRECEIVED', 'exit_zero_observed': True,
                                             'native_five_skill_inventory_received': False}
                    row['recognition_status'] = 'TEXT_UNRECEIVED' if name == 'details' else 'RECEIVED_JSON'
                except Refusal as exc:
                    row['recognition_status'] = 'UNRECEIVED'; row['recognition_code'] = str(exc)
                    recognition_error = exc
                    record_failure(exc, name + '_RECOGNITION')
            except BaseException as exc:
                # Preserve a capture failure before any later bookend can also refuse.
                record_failure(exc, phase)
                raise
            finally:
                if len(records) == start + 1:
                    row = records[-1]
                    for key, value in {'recognition_status':'NOT_ATTEMPTED', 'recognition_code':None,
                        'source_before':True, 'source_after':False, 'runtime_before':True,
                        'runtime_after':False, 'startup_before':True, 'startup_after':False}.items():
                        row.setdefault(key, value)
                    phase = name + '_READBACK'
                    row['source_after'] = supplement(phase + '_SOURCE', lambda: source_inputs(source, pins)) is True
                    store_after = supplement(phase + '_STORE', lambda: admission.source_store_guard(source))
                    row['runtime_after'] = supplement(phase + '_RUNTIME', lambda:
                        file_identity(Path(args.binary), BINARY_BYTES, executable=True)) == runtime_before
                    startup_after = supplement(phase + '_STARTUP', lambda:
                        (profile_readback(profile), managed_and_ancestor_guard(admission, profile['cwd'])))
                    row['startup_after'] = startup_after == (profile_before, managed_before)
                    need(row['source_after'] and store_after == git_before['source_store'] and row['runtime_after'] and
                         row['startup_after'], 'COMMAND_BOOKEND_REFUSED')
            need(quiescent(utility)['verified'] is True, 'COMMAND_READBACK_QUIESCENCE_REFUSED')
            if recognition_error is not None:
                record_failure(recognition_error, name + '_RECOGNITION')
                if str(recognition_error) not in CONTINUABLE_RECOGNITION_CODES:
                    raise recognition_error
        phase = 'COMPLETE'
    except BaseException as exc:
        executable_route_safe = False
        record_failure(exc, phase)
    finally:
        if subreaper:
            result['cleanup']['after_close'] = supplement('AFTER_CLOSE', lambda: quiescent(utility))
        if private is not None and result['currentness_before'] and executable_route_safe:
            def closing_admission():
                need(result['cleanup']['after_close'] == {'no_owned_children_listed': True,
                     'wait_echild': True, 'verified': True}, 'CLOSING_CUSTODY_UNVERIFIED')
                need([row.get('name') for row in records] == ['currentness-before', *COMMANDS] and
                     all(received_capture(row, enriched=row['name'] in COMMANDS) for row in records),
                     'CLOSING_CAPTURE_CUSTODY_UNVERIFIED')
                need(all(row['recognition_code'] is None or
                         row['recognition_code'] in CONTINUABLE_RECOGNITION_CODES
                         for row in records if row['name'] in COMMANDS),
                     'CLOSING_RECOGNITION_ROUTE_UNADMITTED')
                need(source_inputs(source, pins) is True, 'CLOSING_SOURCE_UNVERIFIED')
                need(admission.source_store_guard(source) == git_before['source_store'],
                     'CLOSING_SOURCE_STORE_CHANGED')
                need(file_identity(Path(args.binary), BINARY_BYTES, executable=True) == runtime_before,
                     'CLOSING_RUNTIME_CHANGED')
                need(len(profiles) == len(COMMANDS), 'CLOSING_STARTUP_POPULATION')
                for profile, before, managed in profiles:
                    need(profile_readback(profile) == before and
                         managed_and_ancestor_guard(admission, profile['cwd']) == managed,
                         'CLOSING_STARTUP_CHANGED')
                need(quiescent(utility)['verified'] is True, 'CLOSING_GIT_QUIESCENCE_REFUSED')
                need(admission.git_startup_guard(git_home, False, source)[0] == git_before,
                     'CLOSING_GIT_ADMISSION_CHANGED')
                need(quiescent(utility)['verified'] is True, 'CLOSING_QUIESCENCE_REFUSED')
                return True
            if supplement('CURRENTNESS_AFTER_ADMISSION', closing_admission) is True:
                after = supplement('CURRENTNESS_AFTER', lambda: currentness(args, source, gate_home,
                    private, utility, records, deadline, 'currentness-after'))
                result['currentness_after'] = after == result['currentness_receipt_sha256']
                if not result['currentness_after']:
                    executable_route_safe = False
            else:
                executable_route_safe = False
        if git_before is not None and executable_route_safe and result['currentness_after'] is True:
            def reread_git():
                need(quiescent(utility)['verified'] is True, 'FINAL_GIT_QUIESCENCE_REFUSED')
                after, _ = admission.git_startup_guard(git_home, False, source)
                write_private(private / 'GIT_ADMISSION_AFTER.json', canonical(after)); return after
            result['git_admission_unchanged'] = supplement('GIT_ADMISSION_AFTER', reread_git) == git_before
        if source is not None and pins is not None:
            result['consumed_source_after'] = supplement('SOURCE_AFTER', lambda: source_inputs(source, pins)) is True
        if runtime_before is not None:
            result['runtime_after'] = supplement('RUNTIME_AFTER', lambda:
                file_identity(Path(args.binary), BINARY_BYTES, executable=True)) == runtime_before
        for index, (profile, before, managed) in enumerate(profiles):
            def reread_profile():
                need(profile_readback(profile) == before and
                     managed_and_ancestor_guard(admission, profile['cwd']) == managed,
                     'STARTUP_FINAL_BOOKEND_CHANGED')
                return True
            supplement('STARTUP_FINAL_' + str(index), reread_profile)
        if private is not None:
            supplement('COMMANDS_RETENTION', lambda: write_private(private / 'COMMANDS.json', canonical(records)))
            def seal_private():
                rows = seal_rows(private); path = private / 'PRIVATE_EVIDENCE_SEAL.json'
                raw = canonical({'schema': 'dg17.claude.private-seal.v1', 'members': rows})
                write_private(path, raw); result['cleanup']['private_evidence_seal_sha256'] = sha(raw)
                need(seal_rows(private) == rows and file_identity(path, len(raw)) ==
                     {'bytes':len(raw), 'sha256':sha(raw)}, 'PRIVATE_SEAL_CHANGED')
                return True
            result['cleanup']['private_seal_unchanged'] = supplement('PRIVATE_SEAL', seal_private) is True
        if subreaper:
            result['cleanup']['after_seal'] = supplement('AFTER_SEAL', lambda: quiescent(utility))
        result['commands'] = [command_public(r) for r in records if r.get('name') in COMMANDS]
        started = [r['name'] for r in result['commands'] if r['process_started']]
        result['product_commands_started'] = len(started)
        result['unstarted_commands'] = [name for name in COMMANDS if name not in started]
        if not complete_result(result, records) and result['failure'] is None:
            record_failure(Refusal('REQUIRED_EVIDENCE_INCOMPLETE'), 'FINALIZATION')
        if complete_result(result, records):
            result['status'] = 'OBSERVED_SOURCE_CANDIDATE_METADATA_WITH_DETAILS_UNRECEIVED'
        encoded = public_bytes(result)
        if result_path is not None:
            try:
                write_private(result_path, encoded)
            except BaseException as exc:
                record_failure(exc, 'RESULT_RETENTION'); result['status'] = 'INCOMPLETE_OR_FAILED'
                encoded = public_bytes(result)
        sys.stdout.buffer.write(encoded); sys.stdout.buffer.flush()
    return 0 if result['status'] == 'OBSERVED_SOURCE_CANDIDATE_METADATA_WITH_DETAILS_UNRECEIVED' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'episode', 'binary', 'controller', 'receipt', 'parent-netns'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--expected-uid', type=int, required=True)
    parser.add_argument('--expected-gid', type=int, required=True)
    args = parser.parse_args()
    def interrupted(_signal, _frame):
        raise Refusal('HOST_INTERRUPTED')
    signal.signal(signal.SIGTERM, interrupted); os.umask(0o077)
    return run(args)


if __name__ == '__main__':
    raise SystemExit(main())
