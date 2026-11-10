#!/usr/bin/env python3
"""One separately received Windows preparation canary; no original-operation entry."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import subprocess
import sys
import time
import types

OPERATION = 'c60a46d71b9f43e0941b3c2d8c460751'
BRANCH = 'pro/dg18-windows-preparation-canary-001'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
PREFIX = 'qualification/dg18-windows-preparation-canary-001'
WORKFLOW = '.github/workflows/dg18-windows-preparation-canary-001.yml'
SOURCE = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
SOURCE_TREE = '0da374609f7fea2463a2926f3603b976620bd10e'
EXCLUDED_OPERATION = '469de0eda3fd921cdfadb93a612003bf'
ACCEPTED_PREFIX = 'qualification/dg18-isolated-windows21'
HELD_SHA = 'bf04dc9b262a5b99864bfb20a47a03295ca3f6b99caebdf1e89636af1a92b7fd'
SOURCE_MANIFEST_SHA = 'c45268bda9879ad04a961565e6bb57ddf0ab197a17e4324da63d367b94ac8b64'
JOB_SHA = '0191eb110977e8aad6c615f7130052c08a38b83297c65748768608a2959ecd8b'
JOB_BLOB = '0871accd09acbba57aa8d39480a0d1a44407082c'
MAX_DOCUMENT = 65536
MAX_MEASUREMENT = 16777216
WORKER_SECONDS = 60
PEAK_BYTES = 201326592
EFFECTS = ['CANARY_WINDOWS_HOST_JOB', 'EXACT_SOURCE_AND_PACKET_READS',
           'CANARY_PRIVATE_OUTPUTS', 'CONTAINED_PREPARATION_WORKER',
           'ALLOWLISTED_GIT_CUSTODY', 'OWNED_KERNEL_FIXTURES_IF_REQUIRED',
           'INSTALLED_GIT_TWO_NONOVERWRITING_RENAMES_IF_REQUIRED',
           'RETAIN_CUSTODY_ORIGINAL_AND_PARTIAL_STATE',
           'BOUNDED_PUBLIC_ARTIFACT', 'OWNED_WORKER_PROCESS_CLEANUP']
STAGES = frozenset(('INPUT', 'CUSTODY', 'SOURCE', 'PREPARATION', 'CONTAINMENT', 'TERMINAL'))
CODES = frozenset(('HOST_REFUSED', 'ADMISSION_REFUSED', 'MANIFEST_REFUSED', 'ALLOCATION_REFUSED',
                   'CUSTODY_REFUSED', 'SOURCE_REFUSED', 'DEADLINE_EXPIRED', 'WORKER_RECORD_REFUSED',
                   'JOB_INCOMPLETE', 'WORKER_TIMEOUT', 'WORKER_LIMIT_REFUSED', 'INTERNAL_FAILURE',
                   'TERMINAL_REFUSED', 'RECEIVING_REFUSED'))


class Refusal(RuntimeError):
    def __init__(self, code, predicate_sha256=None):
        self.code = code if code in CODES else 'INTERNAL_FAILURE'
        self.predicate_sha256 = predicate_sha256
        super().__init__(self.code)


def require(ok, code):
    if not ok:
        raise Refusal(code)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def hex_value(value, length=64):
    return type(value) is str and re.fullmatch('[0-9a-f]{%d}' % length, value) is not None


def keys(value, names, code):
    require(type(value) is dict and set(value) == set(names), code)


def parse(raw, maximum=MAX_DOCUMENT):
    require(type(raw) is bytes and 0 < len(raw) <= maximum, 'MANIFEST_REFUSED')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'MANIFEST_REFUSED')
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal('MANIFEST_REFUSED')))
    except Refusal:
        raise
    except (ValueError, UnicodeError):
        raise Refusal('MANIFEST_REFUSED') from None
    require(type(value) is dict, 'MANIFEST_REFUSED')
    return value


def read_file(path, maximum=33554432):
    path = Path(path).absolute()
    require('..' not in path.parts, 'MANIFEST_REFUSED')
    for part in (path, *path.parents):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                'MANIFEST_REFUSED')
    before = path.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 <= before.st_size <= maximum,
            'MANIFEST_REFUSED')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    current = path.stat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_nlink')
    require(all(getattr(before, f) == getattr(opened, f) == getattr(after, f) == getattr(current, f)
                for f in fields) and len(data) == before.st_size, 'MANIFEST_REFUSED')
    return data


def write_new(path, value):
    raw = value if type(value) is bytes else canonical(value)
    with Path(path).open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def verify_members(root, rows):
    require(type(rows) is list and 1 <= len(rows) <= 32, 'MANIFEST_REFUSED')
    seen = set()
    for row in rows:
        keys(row, ('path', 'bytes', 'sha256', 'git_blob_oid', 'mode'), 'MANIFEST_REFUSED')
        name = row['path']
        require(type(name) is str and name and not name.startswith('/') and '\\' not in name
                and all(part not in ('', '.', '..') for part in name.split('/'))
                and name not in seen and row['mode'] == '100644', 'MANIFEST_REFUSED')
        seen.add(name)
        raw = read_file(Path(root) / name)
        require(type(row['bytes']) is int and len(raw) == row['bytes'] and sha(raw) == row['sha256']
                and blob(raw) == row['git_blob_oid'], 'MANIFEST_REFUSED')
    return seen


def pin(value):
    keys(value, ('path', 'bytes', 'sha256'), 'ADMISSION_REFUSED')
    require(type(value['path']) is str and value['path'].startswith('/')
            and 0 < len(value['path']) <= 4096 and '\0' not in value['path']
            and type(value['bytes']) is int and 0 < value['bytes'] <= 1048576
            and hex_value(value['sha256']), 'ADMISSION_REFUSED')


def validate_context(ctx):
    fixed = {'repository': REPOSITORY, 'ref': 'refs/heads/' + BRANCH, 'event': 'push',
             'actions': 'true', 'runner_os': 'Windows', 'runner_arch': 'X64',
             'runner_environment': 'github-hosted', 'platform': 'win32', 'os_name': 'nt',
             'implementation': 'cpython', 'python_version': [3, 12, 10], 'python_bits': 64, 'attempt': '1',
             'branch_creation': True}
    require(type(ctx) is dict and all(ctx.get(k) == v and type(ctx.get(k)) is type(v) for k, v in fixed.items()), 'HOST_REFUSED')
    require(type(ctx.get('run_id')) is str and re.fullmatch('[0-9]{1,20}', ctx['run_id'])
            and hex_value(ctx.get('workflow_commit'), 40), 'HOST_REFUSED')


def validate_admission(a, r, ctx, now_ns, manifest_sha):
    validate_context(ctx)
    keys(a, ('schema', 'operation_id', 'repository', 'branch', 'source_commit', 'source_tree',
             'candidate_manifest_sha256', 'root_actor', 'authority', 'issued_ns', 'expires_ns',
             'worker_seconds', 'workflow_minutes', 'max_attempts', 'maximum_peak_job_committed_bytes',
             'memory_ceiling_kind', 'effects', 'cleanup_scope', 'retained_state_policy',
             'owner_receipt_pins', 'source_review_pin', 'excluded_operation_id',
             'original_allowance_used', 'w_full_grant', 'native_GO', 'original_acceptance', 'automatic_retry'),
         'ADMISSION_REFUSED')
    fixed = {'schema': 'dg18.windows-preparation-canary-admission.v1', 'operation_id': OPERATION,
             'repository': REPOSITORY, 'branch': BRANCH, 'source_commit': SOURCE, 'source_tree': SOURCE_TREE,
             'candidate_manifest_sha256': manifest_sha, 'root_actor': '/root',
             'authority': 'SEPARATE_PREPARATION_CANARY_ONLY', 'worker_seconds': WORKER_SECONDS,
             'workflow_minutes': 10, 'max_attempts': 1, 'maximum_peak_job_committed_bytes': PEAK_BYTES,
             'memory_ceiling_kind': 'OBSERVED_WORKER_PASS_CEILING', 'effects': EFFECTS,
             'cleanup_scope': 'CONTAINED_WORKER_AND_DESCENDANTS', 'retained_state_policy': 'RETAIN_NO_ROLLBACK',
             'excluded_operation_id': EXCLUDED_OPERATION}
    require(all(a[k] == v and type(a[k]) is type(v) for k, v in fixed.items()) and hex_value(manifest_sha),
            'ADMISSION_REFUSED')
    require(all(a[k] is False for k in ('original_allowance_used', 'w_full_grant', 'native_GO',
                                       'original_acceptance', 'automatic_retry')), 'ADMISSION_REFUSED')
    require(type(now_ns) is int and type(a['issued_ns']) is int and type(a['expires_ns']) is int
            and 0 < a['issued_ns'] <= now_ns < a['expires_ns']
            and 0 < a['expires_ns'] - a['issued_ns'] <= 900000000000, 'ADMISSION_REFUSED')
    pin(a['source_review_pin'])
    require(type(a['owner_receipt_pins']) is list and 1 <= len(a['owner_receipt_pins']) <= 8,
            'ADMISSION_REFUSED')
    for p in a['owner_receipt_pins']: pin(p)
    require(len({p['path'] for p in a['owner_receipt_pins']}) == len(a['owner_receipt_pins']), 'ADMISSION_REFUSED')
    keys(r, ('schema', 'root_actor', 'decision', 'operation_id', 'admission_sha256',
             'candidate_manifest_sha256', 'owner_receipt_pins', 'source_review_pin', 'issued_ns', 'expires_ns',
             'source_review_received', 'proper_owner_resources_received', 'declared_effect_scope_received',
             'canary_execution_admitted', 'original_operation_grant', 'original_acceptance', 'automatic_retry'),
         'ADMISSION_REFUSED')
    rf = {'schema': 'dg18.windows-preparation-canary-root-receiving.v1', 'root_actor': '/root',
          'decision': 'RECEIVED_SEPARATE_CANARY_ADMISSION', 'operation_id': OPERATION,
          'admission_sha256': sha(canonical(a)), 'candidate_manifest_sha256': manifest_sha,
          'owner_receipt_pins': a['owner_receipt_pins'], 'source_review_pin': a['source_review_pin']}
    require(all(r[k] == v for k, v in rf.items()), 'ADMISSION_REFUSED')
    require(all(r[k] is True for k in ('source_review_received', 'proper_owner_resources_received',
                                      'declared_effect_scope_received', 'canary_execution_admitted'))
            and all(r[k] is False for k in ('original_operation_grant', 'original_acceptance', 'automatic_retry')),
            'ADMISSION_REFUSED')
    require(type(r['issued_ns']) is int and type(r['expires_ns']) is int
            and a['issued_ns'] <= r['issued_ns'] <= now_ns < r['expires_ns'] <= a['expires_ns'], 'ADMISSION_REFUSED')
    return {'operation_id': OPERATION, 'repository': REPOSITORY, 'branch': BRANCH,
            'run_id': ctx['run_id'], 'attempt': '1', 'workflow_commit': ctx['workflow_commit'],
            'source_commit': SOURCE, 'source_tree': SOURCE_TREE,
            'candidate_manifest_sha256': manifest_sha, 'admission_sha256': sha(canonical(a)),
            'root_receiving_sha256': sha(canonical(r)), 'issued_ns': r['issued_ns'],
            'receiving_expires_ns': r['expires_ns']}


def run_stages(stages, failure_path, *, refusal_context=None):
    require(not Path(failure_path).exists(), 'ALLOCATION_REFUSED')
    values = {}
    for stage, action in stages:
        require(stage in STAGES, 'INTERNAL_FAILURE')
        try:
            values[stage] = action()
        except BaseException as error:
            failure = {'stage': stage, 'code': error.code if isinstance(error, Refusal) else 'INTERNAL_FAILURE',
                       'predicate_sha256': getattr(error, 'predicate_sha256', None)}
            retained = failure
            if refusal_context is not None:
                keys(refusal_context, ('binding', 'pid', 'worker_entry_ns', 'start_sha256',
                                       'worker_started_sha256', 'diagnostics'), 'WORKER_RECORD_REFUSED')
                keys(refusal_context['diagnostics'], ('custody_diagnostic', 'shape_diagnostic',
                                                      'staged_copy_diagnostic'), 'WORKER_RECORD_REFUSED')
                retained = {'schema': 'dg18.windows-canary-first-refusal.v1',
                            **{k: v for k, v in refusal_context.items() if k != 'diagnostics'},
                            'first_failure': failure, **refusal_context['diagnostics']}
                require(len(canonical(retained)) <= MAX_DOCUMENT, 'WORKER_RECORD_REFUSED')
            write_new(failure_path, retained)
            return {'ok': False, 'values': values, 'first_failure': failure}
    return {'ok': True, 'values': values, 'first_failure': None}


def admit_then_run(a, r, ctx, now_ns, manifest_sha, stages, failure_path, *, refusal_context=None):
    validate_admission(a, r, ctx, now_ns, manifest_sha)
    return run_stages(stages, failure_path, refusal_context=refusal_context)


def job_completion(record, command, cwd, worker_pid):
    if type(record) is not dict or type(worker_pid) is not int or worker_pid <= 0:
        return False
    fixed = {'status': 'COMPLETE_UNADMITTED', 'started_suspended': True, 'assigned_before_resume': True,
             'root_job_membership_confirmed': True, 'completion_port_associated_before_assignment': True,
             'complete_memory_scope_valid': True, 'cleanup_complete': True, 'terminal_active_processes': 0,
             'initial_job_flags': 8192, 'terminal_job_flags': 8192, 'terminal_breakaway_allowed': False,
             'containment_status': 'ROOT_EXITED_AND_JOB_EMPTY', 'root_pid': worker_pid, 'command': command, 'cwd': cwd}
    if not all(record.get(k) == v and type(record.get(k)) is type(v) for k, v in fixed.items()): return False
    elapsed = record.get('elapsed_ms'); peak = record.get('peak_job_committed_bytes')
    return (type(record.get('exit_code')) is int and 0 <= record['exit_code'] <= 4294967295
            and type(elapsed) in (int, float) and math.isfinite(elapsed) and 0 <= elapsed <= 60000
            and type(peak) is int and 0 <= peak <= PEAK_BYTES)


def owned_job_cleanup(record, command, cwd, worker_pid):
    if type(record) is not dict or type(worker_pid) is not int or worker_pid <= 0:
        return False
    fixed = {'started_suspended': True, 'assigned_before_resume': True,
             'root_job_membership_confirmed': True, 'cleanup_complete': True,
             'terminal_active_processes': 0, 'initial_job_flags': 8192, 'terminal_job_flags': 8192,
             'terminal_breakaway_allowed': False, 'root_pid': worker_pid, 'command': command, 'cwd': cwd}
    return (all(record.get(k) == v and type(record.get(k)) is type(v) for k, v in fixed.items())
            and record.get('containment_status') in ('ROOT_EXITED_AND_JOB_EMPTY', 'TERMINATED_AND_JOB_EMPTY'))


def terminal_result(binding, worker, measurement, command, cwd, *, admission_validated_ns=None, terminal_ns=None,
                    worker_result_status=None):
    worker_valid = (type(worker) is dict and worker.get('binding') == binding
                    and type(worker.get('pid')) is int and worker['pid'] > 0)
    receiving = worker_result_status or ('RECEIVED' if worker_valid else 'UNAVAILABLE')
    require(receiving in ('RECEIVED', 'BOUND_FIRST_REFUSAL_ONLY', 'UNAVAILABLE')
            and (worker_valid or receiving == 'UNAVAILABLE'), 'WORKER_RECORD_REFUSED')
    observed_pid = worker['pid'] if worker_valid else measurement.get('root_pid') if type(measurement) is dict else None
    cleanup = owned_job_cleanup(measurement, command, cwd, observed_pid)
    complete = worker_valid and job_completion(measurement, command, cwd, worker['pid'])
    success = (complete and measurement['exit_code'] == 0 and worker.get('ok') is True
               and worker.get('first_failure') is None and worker.get('preparation') is not None)
    failure = worker.get('first_failure') if worker_valid else None
    if not success and failure is None:
        code = 'JOB_INCOMPLETE'; predicate = None
        if type(measurement) is dict:
            error = measurement.get('error')
            if type(error) is dict and error.get('type') == 'MeasurementError' and error.get('message') in (
                    'private Job exceeded diagnostic containment timeout',
                    'suspended root preparation exceeded diagnostic containment timeout'):
                code = 'WORKER_TIMEOUT'; predicate = sha(error['message'].encode())
            elif cleanup and measurement.get('status') == 'COMPLETE_UNADMITTED' and (
                    type(measurement.get('elapsed_ms')) in (int, float) and measurement['elapsed_ms'] > 60000
                    or type(measurement.get('peak_job_committed_bytes')) is int and measurement['peak_job_committed_bytes'] > PEAK_BYTES):
                code = 'WORKER_LIMIT_REFUSED'
        failure = {'stage': 'CONTAINMENT', 'code': code, 'predicate_sha256': predicate}
    result = {'schema': 'dg18.windows-preparation-canary-terminal.v1', 'binding': binding,
              'outcome': 'PREPARED' if success else 'REFUSED', 'first_failure': failure,
              'worker_result_status': receiving,
              'preparation': worker.get('preparation') if worker_valid else None,
              'custody_diagnostic': worker.get('custody_diagnostic') if worker_valid else None,
              'shape_diagnostic': worker.get('shape_diagnostic') if worker_valid else None,
              'staged_copy_diagnostic': worker.get('staged_copy_diagnostic') if worker_valid else None,
              'admission_validated_ns': admission_validated_ns,
              'worker_entry_ns': worker.get('worker_entry_ns') if worker_valid else None,
              'terminal_ns': terminal_ns,
              'owned_process_cleanup_complete': bool(cleanup),
              'complete_job_census': bool(type(measurement) is dict and measurement.get('complete_memory_scope_valid') is True),
              'worker_exit_code': measurement.get('exit_code') if type(measurement) is dict else None,
              'measurement_canonical_sha256': sha(canonical(measurement)) if type(measurement) is dict else None,
              'elapsed_ms': measurement.get('elapsed_ms') if cleanup else None,
              'peak_job_committed_bytes': measurement.get('peak_job_committed_bytes') if cleanup else None,
              'cleanup_scope': 'CONTAINED_WORKER_AND_DESCENDANTS', 'harness_included': False,
              'external_broker_scope': 'UNPROVEN', 'retained_state': 'RETAINED_NO_ROLLBACK',
              'physical_teardown': 'UNKNOWN', 'w_full_started': False, 'original_operation_consumed': False,
              'original_acceptance': False, 'automatic_retry': False, 'authority': 'CANARY_EVIDENCE_ONLY'}
    validate_terminal(result)
    return result


def validate_terminal(result):
    keys(result, ('schema', 'binding', 'outcome', 'first_failure', 'worker_result_status', 'preparation', 'custody_diagnostic',
                  'shape_diagnostic', 'staged_copy_diagnostic', 'owned_process_cleanup_complete',
                  'complete_job_census', 'worker_exit_code',
                  'admission_validated_ns', 'worker_entry_ns', 'terminal_ns',
                  'measurement_canonical_sha256', 'elapsed_ms', 'peak_job_committed_bytes',
                  'cleanup_scope', 'harness_included', 'external_broker_scope', 'retained_state',
                  'physical_teardown', 'w_full_started', 'original_operation_consumed', 'original_acceptance',
                  'automatic_retry', 'authority'), 'TERMINAL_REFUSED')
    b = result['binding']
    keys(b, ('operation_id', 'repository', 'branch', 'run_id', 'attempt', 'workflow_commit', 'source_commit',
             'source_tree', 'candidate_manifest_sha256', 'admission_sha256', 'root_receiving_sha256',
             'issued_ns', 'receiving_expires_ns'), 'TERMINAL_REFUSED')
    require(b['operation_id'] == OPERATION and b['repository'] == REPOSITORY and b['branch'] == BRANCH
            and b['source_commit'] == SOURCE and b['source_tree'] == SOURCE_TREE and b['attempt'] == '1'
            and type(b['run_id']) is str and re.fullmatch('[0-9]{1,20}', b['run_id'])
            and hex_value(b['workflow_commit'], 40)
            and all(hex_value(b[k]) for k in ('candidate_manifest_sha256', 'admission_sha256', 'root_receiving_sha256'))
            and type(b['issued_ns']) is int and type(b['receiving_expires_ns']) is int
            and 0 < b['receiving_expires_ns'] - b['issued_ns'] <= 900000000000, 'TERMINAL_REFUSED')
    fixed = {'schema': 'dg18.windows-preparation-canary-terminal.v1', 'cleanup_scope': 'CONTAINED_WORKER_AND_DESCENDANTS',
             'harness_included': False, 'external_broker_scope': 'UNPROVEN', 'retained_state': 'RETAINED_NO_ROLLBACK',
             'physical_teardown': 'UNKNOWN', 'w_full_started': False, 'original_operation_consumed': False,
             'original_acceptance': False, 'automatic_retry': False, 'authority': 'CANARY_EVIDENCE_ONLY'}
    require(all(result[k] == v and type(result[k]) is type(v) for k, v in fixed.items()), 'TERMINAL_REFUSED')
    require(type(result['owned_process_cleanup_complete']) is bool and type(result['complete_job_census']) is bool
            and (result['worker_exit_code'] is None or type(result['worker_exit_code']) is int
                 and 0 <= result['worker_exit_code'] <= 4294967295)
            and result['outcome'] in ('PREPARED', 'REFUSED'), 'TERMINAL_REFUSED')
    require(result['worker_result_status'] in ('RECEIVED', 'BOUND_FIRST_REFUSAL_ONLY', 'UNAVAILABLE'), 'TERMINAL_REFUSED')
    failure = result['first_failure']
    if failure is not None:
        keys(failure, ('stage', 'code', 'predicate_sha256'), 'TERMINAL_REFUSED')
        require(failure['stage'] in STAGES and failure['code'] in CODES
                and (failure['predicate_sha256'] is None or hex_value(failure['predicate_sha256'])), 'TERMINAL_REFUSED')
    if result['outcome'] == 'PREPARED':
        require(result['worker_result_status'] == 'RECEIVED'
                and result['owned_process_cleanup_complete'] is True and result['complete_job_census'] is True
                and result['worker_exit_code'] == 0 and failure is None
                and type(result['preparation']) is dict and hex_value(result['measurement_canonical_sha256']),
                'TERMINAL_REFUSED')
    else:
        require(failure is not None, 'TERMINAL_REFUSED')
    if result['worker_result_status'] == 'BOUND_FIRST_REFUSAL_ONLY':
        require(result['outcome'] == 'REFUSED' and result['preparation'] is None and failure is not None,
                'TERMINAL_REFUSED')
    if result['owned_process_cleanup_complete']:
        require(type(result['elapsed_ms']) in (int, float) and math.isfinite(result['elapsed_ms'])
                and 0 <= result['elapsed_ms'] and type(result['peak_job_committed_bytes']) is int
                and 0 <= result['peak_job_committed_bytes'] <= 2**64 - 1, 'TERMINAL_REFUSED')
    else:
        require(result['elapsed_ms'] is None and result['peak_job_committed_bytes'] is None, 'TERMINAL_REFUSED')
    for name in ('admission_validated_ns', 'worker_entry_ns', 'terminal_ns'):
        require(result[name] is None or type(result[name]) is int and result[name] > 0, 'TERMINAL_REFUSED')
    if result['outcome'] == 'PREPARED':
        require(all(type(result[name]) is int for name in ('admission_validated_ns', 'worker_entry_ns', 'terminal_ns'))
                and b['issued_ns'] <= result['admission_validated_ns'] <= result['worker_entry_ns']
                <= result['terminal_ns'] < b['receiving_expires_ns'] and result['elapsed_ms'] <= 60000
                and result['peak_job_committed_bytes'] <= PEAK_BYTES, 'TERMINAL_REFUSED')
    validate_native_projections(result, strict_refusal=result['worker_result_status'] == 'BOUND_FIRST_REFUSAL_ONLY')
    require(len(canonical(result)) <= MAX_DOCUMENT, 'TERMINAL_REFUSED')
    return result


def load_exact_module(path, expected_sha, name):
    raw = read_file(path)
    require(sha(raw) == expected_sha, 'MANIFEST_REFUSED')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    # Compile the exact bytes just received; do not reopen through an import loader.
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def accepted_module():
    module = load_exact_module(Path(__file__).resolve().parents[2] / ACCEPTED_PREFIX / 'held_admission.py',
                               HELD_SHA, 'canary_accepted_custody')
    module.DIAGNOSTIC_WRAPPER_SHA256 = HELD_SHA
    return module


def validate_native_projections(result, *, strict_refusal=False):
    b = result['binding']; preparation = result['preparation']
    if preparation is not None:
        keys(preparation, ('schema', 'source_commit', 'source_tree', 'source_members', 'base_tree_leaves',
                           'candidate_manifest_sha256', 'source_snapshot_sha256', 'tools_sha256',
                           'filesystems', 'git_custody'), 'TERMINAL_REFUSED')
        require(preparation['schema'] == 'dg18.windows-preparation-canary-preparation.v1'
                and preparation['source_commit'] == SOURCE and preparation['source_tree'] == SOURCE_TREE
                and type(preparation['source_members']) is int and preparation['source_members'] == 99
                and type(preparation['base_tree_leaves']) is int and preparation['base_tree_leaves'] == 1759
                and preparation['candidate_manifest_sha256'] == b['candidate_manifest_sha256']
                and hex_value(preparation['source_snapshot_sha256']) and preparation['filesystems'] == ['NTFS'],
                'TERMINAL_REFUSED')
        keys(preparation['tools_sha256'], ('python', 'git', 'bash'), 'TERMINAL_REFUSED')
        require(all(hex_value(v) for v in preparation['tools_sha256'].values()), 'TERMINAL_REFUSED')
        require(preparation['git_custody'] == result['custody_diagnostic'], 'TERMINAL_REFUSED')
    if not strict_refusal and all(result[k] is None for k in ('custody_diagnostic', 'shape_diagnostic', 'staged_copy_diagnostic')):
        require(preparation is None, 'TERMINAL_REFUSED')
        return
    try:
        held = accepted_module()
        ctx = {k: b[k] for k in ('run_id', 'attempt', 'workflow_commit')}
        custody = held.validate_custody_projection(result['custody_diagnostic'], ctx, required=preparation is not None)
        if preparation is not None:
            require(custody['status'] == 'ESTABLISHED', 'TERMINAL_REFUSED')
        failure = result['first_failure']; predicate = failure['predicate_sha256'] if failure else None
        error_class = 'PREDICATE_REFUSED' if predicate else 'UNSPECIFIED'
        held.validate_shape_diagnostic(result['shape_diagnostic'], ctx, 'PREPARE_CUSTODY', error_class, predicate)
        staged = held.validate_staged_copy_diagnostic(result['staged_copy_diagnostic'], ctx,
                                                      'PREPARE_CUSTODY', error_class, predicate)
        held.validate_staged_copy_custody(staged, custody, None)
    except BaseException:
        raise Refusal('TERMINAL_REFUSED') from None


def worker_command(ctx, source):
    validate_context(ctx)
    return [ctx['python'], '-I', '-X', 'utf8', '-B', str(Path(__file__).resolve()),
            'worker', '--source', str(source)]


def worker_environment(ctx):
    validate_context(ctx)
    python = PureWindowsPath(ctx['python']); system = os.environ.get('SystemRoot', r'C:\Windows')
    # The GitHub values below are observed in the parent, not the old wrapper's manufactured branch values.
    env = {'SystemRoot': system, 'WINDIR': system, 'ProgramFiles': r'C:\Program Files',
           'PATHEXT': '.COM;.EXE;.BAT;.CMD',
           'PATH': ';'.join((str(python.parent), r'C:\Program Files\Git\mingw64\bin',
                            r'C:\Program Files\Git\ucrt64\bin', r'C:\Program Files\Git\cmd',
                            r'C:\Program Files\Git\bin', r'C:\Program Files\Git\usr\bin', system + r'\System32')),
           'TEMP': ctx['temp'], 'TMP': ctx['temp'], 'PYTHONDONTWRITEBYTECODE': '1',
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_SYSTEM': 'NUL', 'GIT_CONFIG_GLOBAL': 'NUL',
           'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0',
           'IMPLEMENTAUDIT_PYTHON': ctx['python'], 'DG18_PHYSICAL_PYTHON': ctx['python'],
           'LC_ALL': 'C', 'LANG': 'C', 'MSYS2_ARG_CONV_EXCL': '*'}
    mapping = {'GITHUB_ACTIONS': 'actions', 'GITHUB_REPOSITORY': 'repository', 'GITHUB_EVENT_NAME': 'event',
               'GITHUB_REF': 'ref', 'GITHUB_RUN_ATTEMPT': 'attempt', 'GITHUB_RUN_ID': 'run_id',
               'GITHUB_SHA': 'workflow_commit', 'GITHUB_WORKSPACE': 'workspace', 'RUNNER_TEMP': 'temp',
               'RUNNER_OS': 'runner_os', 'RUNNER_ARCH': 'runner_arch', 'RUNNER_ENVIRONMENT': 'runner_environment'}
    env.update({key: ctx[value] for key, value in mapping.items()})
    env['GITHUB_EVENT_PATH'] = ctx['event_path']
    return env


def host_context():
    ctx = {'platform': sys.platform, 'os_name': os.name, 'implementation': sys.implementation.name,
           'python_version': list(sys.version_info[:3]), 'python_bits': 64 if sys.maxsize == 2**63 - 1 else 32}
    mapping = {'actions': 'GITHUB_ACTIONS', 'repository': 'GITHUB_REPOSITORY', 'event': 'GITHUB_EVENT_NAME',
               'ref': 'GITHUB_REF', 'attempt': 'GITHUB_RUN_ATTEMPT', 'run_id': 'GITHUB_RUN_ID',
               'workflow_commit': 'GITHUB_SHA', 'workspace': 'GITHUB_WORKSPACE', 'temp': 'RUNNER_TEMP',
               'runner_os': 'RUNNER_OS', 'runner_arch': 'RUNNER_ARCH', 'runner_environment': 'RUNNER_ENVIRONMENT',
               'python': 'DG18_PHYSICAL_PYTHON'}
    ctx.update({key: os.environ.get(value, '') for key, value in mapping.items()})
    require(os.name == 'nt' and sys.platform == 'win32', 'HOST_REFUSED')
    ctx['event_path'] = os.environ.get('GITHUB_EVENT_PATH', '')
    event_raw = read_file(ctx['event_path'], MAX_DOCUMENT); event = parse(event_raw)
    require(event.get('ref') == 'refs/heads/' + BRANCH and event.get('created') is True
            and event.get('deleted') is False and event.get('before') == '0' * 40
            and event.get('after') == ctx['workflow_commit'], 'HOST_REFUSED')
    ctx['branch_creation'] = True
    ctx['event_sha256'] = sha(event_raw)
    validate_context(ctx)
    require(Path(ctx['python']).is_absolute() and Path(ctx['python']).samefile(sys.executable), 'HOST_REFUSED')
    return ctx


def input_packet(source, *, current=True):
    ctx = host_context(); repo = Path(__file__).resolve().parents[2]; own = Path(__file__).resolve().parent
    require(repo == Path(ctx['workspace']).resolve() / 'packet'
            and source is not None and Path(source).resolve() == Path(ctx['workspace']).resolve() / 'qualified-source',
            'MANIFEST_REFUSED')
    manifest_raw = read_file(own / 'CANARY_MANIFEST.json', MAX_DOCUMENT); manifest = parse(manifest_raw)
    keys(manifest, ('schema', 'operation_id', 'branch', 'source_commit', 'source_tree', 'reused_static_tree', 'members'),
         'MANIFEST_REFUSED')
    require(manifest['schema'] == 'dg18.windows-preparation-canary-manifest.v1'
            and manifest['operation_id'] == OPERATION and manifest['branch'] == BRANCH
            and manifest['source_commit'] == SOURCE and manifest['source_tree'] == SOURCE_TREE
            and manifest['reused_static_tree'] == 'd299d4d1c6a18483131b7217bc2a9d731e39a516', 'MANIFEST_REFUSED')
    expected = {'.github/workflows/dg18-isolated-windows21.yml', WORKFLOW, PREFIX + '/canary.py'} | {
        ACCEPTED_PREFIX + '/' + name for name in ('CODE_MANIFEST.json', 'SOURCE_MANIFEST.json',
        'entitlement-reference.txt', 'held_admission.py', 'native_checks.py', 'prepare_and_execute.py')}
    require(verify_members(repo, manifest['members']) == expected, 'MANIFEST_REFUSED')
    a = parse(read_file(own / 'ADMISSION.json', MAX_DOCUMENT))
    r = parse(read_file(own / 'ROOT_RECEIVING.json', MAX_DOCUMENT))
    validated_ns = time.time_ns() if current else r['issued_ns']
    binding = validate_admission(a, r, ctx, validated_ns, sha(manifest_raw))
    return ctx, repo, own, manifest, manifest_raw, a, r, binding, validated_ns


def run_root(ctx):
    return Path(ctx['temp']) / ('dg18-preparation-canary-001-' + ctx['run_id'] + '-1')


def check_deadline(binding):
    require(time.time_ns() < binding['receiving_expires_ns'], 'DEADLINE_EXPIRED')


def source_snapshot(held, ctx, source, repo, manifest, manifest_raw, paths, binding):
    check_deadline(binding)
    record, custody = held.load_git_custody(ctx, paths)
    git = Path(record['selected']['path']); tools = {
        'python': held.fingerprint(ctx['python'], role='TOOL_PYTHON'),
        'git': held.fingerprint(git, role='TOOL_GIT'), 'bash': held.fingerprint(held.BASH, role='TOOL_BASH')}
    environment = worker_environment(ctx)
    def git_read(cwd, *args, maximum=2097152):
        check_deadline(binding)
        held.exact(held.fingerprint(git, role='TOOL_GIT'), tools['git'], 'held direct Git changed before invocation')
        command = [str(git), '-c', 'credential.helper=', '-c', 'core.hooksPath=NUL', '-c', 'gc.auto=0',
                   '-c', 'maintenance.auto=false', '-c', 'init.templateDir=', '-C', str(cwd), *args]
        response = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  env=environment, timeout=20, check=False)
        require(response.returncode == 0 and len(response.stdout) <= maximum, 'SOURCE_REFUSED')
        return response.stdout
    with held.custody_effect_lease({'context': ctx}, paths):
        require(git_read(source, 'rev-parse', 'HEAD').decode().strip() == SOURCE
                and git_read(source, 'rev-parse', 'HEAD^{tree}').decode().strip() == SOURCE_TREE, 'SOURCE_REFUSED')
        base = held.git_tree(git_read(source, 'ls-tree', '-r', '-z', 'HEAD'))
        require(len(base) == 1759, 'SOURCE_REFUSED')
        require(git_read(repo, 'rev-parse', 'HEAD').decode().strip() == ctx['workflow_commit']
                and held.parents(git_read(repo, 'cat-file', 'commit', 'HEAD')) == [SOURCE], 'SOURCE_REFUSED')
        for checkout in (source, repo):
            require(git_read(checkout, 'status', '--porcelain=v1', '--untracked-files=all', '--ignored') == b'', 'SOURCE_REFUSED')
        additions = {row['path']: {'mode': row['mode'], 'oid': row['git_blob_oid']} for row in manifest['members']}
        additions[PREFIX + '/CANARY_MANIFEST.json'] = {'mode': '100644', 'oid': blob(manifest_raw)}
        for name in ('ADMISSION.json', 'ROOT_RECEIVING.json'):
            additions[PREFIX + '/' + name] = {'mode': '100644', 'oid': blob(read_file(repo / PREFIX / name, MAX_DOCUMENT))}
        require(not set(base) & set(additions)
                and held.git_tree(git_read(repo, 'ls-tree', '-r', '-z', 'HEAD')) == {**base, **additions}, 'SOURCE_REFUSED')
        source_raw = read_file(repo / ACCEPTED_PREFIX / 'SOURCE_MANIFEST.json', MAX_DOCUMENT)
        require(sha(source_raw) == SOURCE_MANIFEST_SHA, 'SOURCE_REFUSED')
        selected = parse(source_raw)['members']; received = {}
        require(len(selected) == 99 and len({r['path'] for r in selected}) == 99, 'SOURCE_REFUSED')
        for index, row in enumerate(selected):
            keys(row, ('path', 'bytes', 'sha256', 'git_blob_oid', 'git_mode'), 'SOURCE_REFUSED')
            require(base.get(row['path']) == {'mode': row['git_mode'], 'oid': row['git_blob_oid']}, 'SOURCE_REFUSED')
            raw, identity = held.read_regular(source / row['path'], role='SELECTED_SOURCE', manifest_index=index)
            require(len(raw) == row['bytes'] and sha(raw) == row['sha256'] and blob(raw) == row['git_blob_oid'], 'SOURCE_REFUSED')
            received[row['path']] = identity
        require({p for p in base if p.startswith('skills/')} == {p for p in received if p.startswith('skills/')}, 'SOURCE_REFUSED')
        exec_path = Path(git_read(source, '--exec-path', maximum=4096).decode().strip())
        require(held.physical(exec_path) == held.physical(git.parent.parent / 'libexec/git-core'), 'SOURCE_REFUSED')
        for path in (source, repo, paths['hold']): held.ntfs(path)
        verify_members(repo, manifest['members'])
        check_deadline(binding)
    return {'schema': 'dg18.windows-preparation-canary-preparation.v1', 'source_commit': SOURCE,
            'source_tree': SOURCE_TREE, 'source_members': 99, 'base_tree_leaves': 1759,
            'candidate_manifest_sha256': binding['candidate_manifest_sha256'],
            'source_snapshot_sha256': sha(canonical(received)),
            'tools_sha256': {k: v['sha256'] for k, v in tools.items()}, 'filesystems': ['NTFS'], 'git_custody': custody}


def run_worker(source):
    worker_entry_ns = time.time_ns()
    ctx, repo, own, manifest, manifest_raw, a, r, binding, _ = input_packet(source)
    root = run_root(ctx); start_raw = read_file(root / 'START.json', MAX_DOCUMENT); start = parse(start_raw)
    keys(start, ('schema', 'binding', 'context', 'admission_validated_ns', 'command', 'cwd', 'timeout_seconds'), 'WORKER_RECORD_REFUSED')
    require(start['schema'] == 'dg18.windows-canary-start.v1' and start['binding'] == binding
            and start['context'] == ctx and start['command'] == worker_command(ctx, source)
            and start['cwd'] == str(root) and type(start['timeout_seconds']) is int
            and 1 <= start['timeout_seconds'] <= WORKER_SECONDS, 'WORKER_RECORD_REFUSED')
    started = {'schema': 'dg18.windows-canary-worker-started.v1', 'pid': os.getpid(),
               'worker_entry_ns': worker_entry_ns, 'binding': binding, 'start_sha256': sha(start_raw)}
    write_new(root / 'WORKER_STARTED.json', started)
    held = accepted_module(); source = held.physical(source)
    paths = {'source': source, 'packet_repo': repo, 'packet': repo / ACCEPTED_PREFIX,
             'hold': root / 'custody', 'out': root / 'UNALLOCATED_ORIGINAL_OUTPUT'}
    diagnostics = {'custody_diagnostic': None, 'shape_diagnostic': None, 'staged_copy_diagnostic': None}
    refusal_context = {'binding': binding, 'pid': os.getpid(), 'worker_entry_ns': worker_entry_ns,
                       'start_sha256': sha(start_raw), 'worker_started_sha256': sha(canonical(started)),
                       'diagnostics': diagnostics}
    def custody_stage():
        check_deadline(binding)
        paths['hold'].mkdir(exist_ok=False); (paths['hold'] / 'tmp').mkdir(exist_ok=False)
        try:
            return held.prepare_git_custody(ctx, paths)
        except BaseException as error:
            classification = held.classify_failure(error)
            try:
                diagnostics['custody_diagnostic'] = held.read_custody_projection(ctx, paths, required=False)
                diagnostics['shape_diagnostic'] = held.bind_shape_observation(getattr(error, 'shape_observation', None),
                    ctx, 'PREPARE_CUSTODY', classification['error_class'], classification['predicate_sha256'])
                diagnostics['staged_copy_diagnostic'] = held.bind_staged_copy_observation(getattr(error, 'staged_copy_observation', None),
                    ctx, 'PREPARE_CUSTODY', classification['error_class'], classification['predicate_sha256'])
            except BaseException:
                diagnostics.update(custody_diagnostic=None, shape_diagnostic=None, staged_copy_diagnostic=None)
            raise Refusal('CUSTODY_REFUSED', classification['predicate_sha256']) from None
    def source_stage():
        diagnostics['custody_diagnostic'] = held.read_custody_projection(ctx, paths, required=True)
        try:
            return source_snapshot(held, ctx, source, repo, manifest, manifest_raw, paths, binding)
        except Refusal:
            raise
        except BaseException:
            raise Refusal('SOURCE_REFUSED') from None
    result = admit_then_run(a, r, ctx, time.time_ns(), sha(manifest_raw),
                            [('CUSTODY', custody_stage), ('SOURCE', source_stage)], root / 'FIRST_FAILURE.json',
                            refusal_context=refusal_context)
    worker = {'schema': 'dg18.windows-canary-worker.v1', 'binding': binding, 'pid': os.getpid(),
              'worker_entry_ns': worker_entry_ns, 'ok': result['ok'],
              'preparation': result['values'].get('SOURCE'), 'first_failure': result['first_failure'], **diagnostics}
    write_new(root / 'WORKER_RESULT.json', worker)
    return 0 if worker['ok'] else 1


def receive_worker_evidence(root, binding, start, measurement, command, cwd):
    """Receive full output, or the earlier bound refusal; neither route invents missing evidence."""
    def worker_identity(value):
        require(type(measurement) is dict and measurement.get('command') == command
                and measurement.get('cwd') == cwd and type(measurement.get('root_pid')) is int
                and measurement['root_pid'] > 0 and value['binding'] == binding
                and type(value['pid']) is int and value['pid'] == measurement['root_pid']
                and type(value['worker_entry_ns']) is int
                and start['admission_validated_ns'] <= value['worker_entry_ns'] < binding['receiving_expires_ns'],
                'WORKER_RECORD_REFUSED')
    try:
        worker = parse(read_file(root / 'WORKER_RESULT.json', MAX_DOCUMENT))
        keys(worker, ('schema', 'binding', 'pid', 'worker_entry_ns', 'ok', 'preparation', 'first_failure',
                      'custody_diagnostic', 'shape_diagnostic', 'staged_copy_diagnostic'), 'WORKER_RECORD_REFUSED')
        require(worker['schema'] == 'dg18.windows-canary-worker.v1' and type(worker['ok']) is bool,
                'WORKER_RECORD_REFUSED')
        worker_identity(worker)
        return worker, 'RECEIVED'
    except BaseException:
        pass
    try:
        start_raw = read_file(root / 'START.json', MAX_DOCUMENT)
        require(start_raw == canonical(start) and start['binding'] == binding
                and start['command'] == command and start['cwd'] == cwd, 'WORKER_RECORD_REFUSED')
        started_raw = read_file(root / 'WORKER_STARTED.json', MAX_DOCUMENT); started = parse(started_raw)
        keys(started, ('schema', 'binding', 'pid', 'worker_entry_ns', 'start_sha256'), 'WORKER_RECORD_REFUSED')
        require(started['schema'] == 'dg18.windows-canary-worker-started.v1'
                and started['start_sha256'] == sha(start_raw), 'WORKER_RECORD_REFUSED')
        worker_identity(started)
        retained = parse(read_file(root / 'FIRST_FAILURE.json', MAX_DOCUMENT))
        keys(retained, ('schema', 'binding', 'pid', 'worker_entry_ns', 'start_sha256', 'worker_started_sha256',
                        'first_failure', 'custody_diagnostic', 'shape_diagnostic', 'staged_copy_diagnostic'),
             'WORKER_RECORD_REFUSED')
        require(retained['schema'] == 'dg18.windows-canary-first-refusal.v1'
                and retained['start_sha256'] == sha(start_raw)
                and retained['worker_started_sha256'] == sha(started_raw)
                and all(retained[k] == started[k] for k in ('binding', 'pid', 'worker_entry_ns')), 'WORKER_RECORD_REFUSED')
        worker_identity(retained)
        failure = retained['first_failure']
        keys(failure, ('stage', 'code', 'predicate_sha256'), 'WORKER_RECORD_REFUSED')
        require(failure['stage'] in STAGES and failure['code'] in CODES
                and (failure['predicate_sha256'] is None or hex_value(failure['predicate_sha256'])), 'WORKER_RECORD_REFUSED')
        worker = {'schema': 'dg18.windows-canary-worker.v1', 'binding': binding,
                  'pid': retained['pid'], 'worker_entry_ns': retained['worker_entry_ns'], 'ok': False,
                  'preparation': None, 'first_failure': failure,
                  **{k: retained[k] for k in ('custody_diagnostic', 'shape_diagnostic', 'staged_copy_diagnostic')}}
        # Even absent diagnostics pass through the accepted requirement predicates.
        validate_native_projections(worker, strict_refusal=True)
        return worker, 'BOUND_FIRST_REFUSAL_ONLY'
    except BaseException:
        return None, 'UNAVAILABLE'


def run_canary(source):
    ctx, repo, own, manifest, manifest_raw, a, r, binding, validated_ns = input_packet(source)
    remaining = (binding['receiving_expires_ns'] - time.time_ns()) // 1000000000 - 45
    require(remaining >= 1, 'DEADLINE_EXPIRED')
    timeout = min(WORKER_SECONDS, remaining)
    held = accepted_module()
    # This single already-selected public helper is received before any child creation.
    job_path = Path(source) / 'scripts/r0039-windows-job.py'
    raw, _ = held.read_regular(job_path)
    require(len(raw) == 25678 and sha(raw) == JOB_SHA and blob(raw) == JOB_BLOB, 'SOURCE_REFUSED')
    job = load_exact_module(job_path, JOB_SHA, 'canary_accepted_job')
    root = run_root(ctx); root.mkdir(exist_ok=False)
    command = worker_command(ctx, source)
    start = {'schema': 'dg18.windows-canary-start.v1', 'binding': binding, 'context': ctx,
             'admission_validated_ns': validated_ns, 'command': command, 'cwd': str(root), 'timeout_seconds': timeout}
    write_new(root / 'START.json', start)
    measurement = None; worker = None
    try:
        check_deadline(binding)
        measurement = job.measure(command, root, worker_environment(ctx), root / 'job', diagnostic_timeout_seconds=timeout)
    except BaseException:
        # The exact helper owns containment. Do not repeat it or start another worker.
        try: measurement = parse(read_file(root / 'job/measurement.json', MAX_MEASUREMENT), MAX_MEASUREMENT)
        except BaseException: measurement = None
    if type(measurement) is dict and measurement.get('status') == 'COMPLETE_UNADMITTED':
        try:
            census = job.reconcile_process_events(measurement['process_events'], measurement['kernel_total_processes'], measurement['root_pid'])
            require(all(measurement.get(k) == v for k, v in census.items()), 'JOB_INCOMPLETE')
            raw = read_file(root / 'job/measurement.json', MAX_MEASUREMENT)
            require(parse(raw, MAX_MEASUREMENT) == measurement, 'JOB_INCOMPLETE')
        except BaseException:
            measurement = None
    worker, worker_result_status = receive_worker_evidence(root, binding, start, measurement, command, str(root))
    result = terminal_result(binding, worker, measurement, command, str(root),
                             admission_validated_ns=validated_ns, terminal_ns=time.time_ns(),
                             worker_result_status=worker_result_status)
    public = root / 'public'; public.mkdir(exist_ok=False)
    write_new(public / 'RESULT.json', result)
    return 0 if result['outcome'] == 'PREPARED' else 1


def receive_terminal(raw, observation, now_ns=None):
    o = observation
    keys(o, ('schema', 'observer', 'repository', 'operation_id', 'run_id', 'attempt', 'workflow_commit',
             'artifact_name', 'artifact_id', 'artifact_archive_sha256', 'result_bytes', 'result_sha256',
             'candidate_manifest_sha256', 'admission_sha256', 'root_receiving_sha256'), 'RECEIVING_REFUSED')
    require(o['schema'] == 'dg18.windows-canary-artifact-observation.v1' and o['observer'] == '/root'
            and type(o['artifact_id']) is str and re.fullmatch('[0-9]{1,20}', o['artifact_id'])
            and o['artifact_id'] != '13591367765' and hex_value(o['artifact_archive_sha256'])
            and type(o['result_bytes']) is int and o['result_bytes'] == len(raw)
            and o['result_sha256'] == sha(raw), 'RECEIVING_REFUSED')
    result = validate_terminal(parse(raw)); b = result['binding']
    for key in ('repository', 'operation_id', 'run_id', 'attempt', 'workflow_commit',
                'candidate_manifest_sha256', 'admission_sha256', 'root_receiving_sha256'):
        require(o[key] == b[key], 'RECEIVING_REFUSED')
    require(o['artifact_name'] == 'dg18-preparation-canary-001-' + b['run_id'] + '-1', 'RECEIVING_REFUSED')
    now_ns = time.time_ns() if now_ns is None else now_ns
    require(type(now_ns) is int and b['issued_ns'] <= now_ns < b['receiving_expires_ns'], 'RECEIVING_REFUSED')
    return {'schema': 'dg18.windows-preparation-canary-receiving.v1', 'operation_id': OPERATION,
            'decision': 'RECEIVED_CANARY_PREPARATION_AND_OWNED_PROCESS_CLEANUP' if result['outcome'] == 'PREPARED'
                        else 'RECEIVED_CANARY_REFUSAL', 'binding': b, 'artifact_observation': o,
            'received_ns': now_ns, 'physical_teardown': 'UNKNOWN', 'original_acceptance': False,
            'original_operation_consumed': False, 'authority': 'CANARY_EVIDENCE_ONLY'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'worker', 'validate-public', 'receive'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--observation', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'receive':
            require(args.result is not None and args.observation is not None and args.output is not None, 'RECEIVING_REFUSED')
            received = receive_terminal(read_file(args.result, MAX_DOCUMENT), parse(read_file(args.observation, MAX_DOCUMENT)))
            write_new(args.output, received)
            print('DG18_CANARY_RECEIVED')
            return 0
        if args.action == 'run':
            return run_canary(args.source)
        if args.action == 'worker':
            return run_worker(args.source)
        ctx, repo, own, manifest, manifest_raw, a, r, binding, _ = input_packet(args.source, current=False)
        result = validate_terminal(parse(read_file(run_root(ctx) / 'public/RESULT.json', MAX_DOCUMENT)))
        require(result['binding'] == binding, 'TERMINAL_REFUSED')
        print('DG18_CANARY_PUBLIC_VALIDATED')
        return 0
    except BaseException as error:
        print(json.dumps({'status': 'DG18_CANARY_REFUSED', 'code': error.code if isinstance(error, Refusal)
                          else 'INTERNAL_FAILURE', 'original_operation_consumed': False,
                          'original_acceptance': False, 'automatic_retry': False}, sort_keys=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
