#!/usr/bin/env python3
"""Repo-only DG30 record checks. JSON consistency never authenticates a host.

The Windows runner records actual observations separately. This portable gate
does not issue a grant, currentness, native-event or whole-issue acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import ntpath
from pathlib import Path
import re

MAXIMUM_MS = 60000
MAXIMUM_JOB_BYTES = 201326592
BOUNDARIES = {'host-reported-compaction', 'new-session', 'handoff-resume',
              'manual-resume', 'inferred-context-gap'}


def require(condition, message):
    if not condition:
        raise QualificationError(message)


class QualificationError(ValueError):
    pass


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON member')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: require(False, 'nonfinite JSON'))
    except (ValueError, UnicodeError, TypeError) as exc:
        raise QualificationError('invalid qualification JSON') from exc


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def same_json(left, right):
    # Strictly parsed JSON still needs typed comparison: Python considers
    # True == 1 == 1.0, including nested values in otherwise equal dicts.
    try:
        encode = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True,
                                          separators=(',', ':'), allow_nan=False)
        return encode(left) == encode(right)
    except (TypeError, ValueError):
        return False


def blob_oid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def windows_path(value):
    require(type(value) is str and ntpath.isabs(value) and '\x00' not in value,
            'absolute physical Windows executable path required')
    return ntpath.normcase(ntpath.normpath(value))


def load_job():
    spec = importlib.util.spec_from_file_location('r0039_job_gate',
                Path(__file__).with_name('r0039-windows-job.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_measurement(op, expected_command, expected_tools):
    require(type(op) is dict, 'measurement must be an object')
    fixed = {'schema': 'implementaudit.windows-job-measurement.v1', 'platform': 'win32',
             'status': 'COMPLETE_UNADMITTED', 'cleanup_complete': True,
             'completion_port_associated_before_assignment': True,
             'exit_code': 0, 'terminal_active_processes': 0, 'started_suspended': True,
             'root_job_membership_confirmed': True, 'assigned_before_resume': True,
             'initial_job_flags': 8192, 'terminal_job_flags': 8192,
             'terminal_breakaway_allowed': False, 'baseline_subtracted_bytes': 0,
             'harness_included': False, 'sampled_pid_census_complete': False,
             'complete_memory_scope_valid': True, 'metric_admission': 'UNADMITTED_DIAGNOSTIC'}
    for key, value in fixed.items():
        require(type(op.get(key)) is type(value) and op[key] == value,
                'missing, incomplete or mismatched measurement: ' + key)
    require(type(expected_command) is list and len(expected_command) > 1
            and all(type(arg) is str and arg and '\x00' not in arg for arg in expected_command)
            and op.get('command') == expected_command, 'measured command is not the exact requested operation')
    for name in ('elapsed_ms', 'root_exit_observed_ms'):
        value = op.get(name)
        require(type(value) in (int, float) and math.isfinite(value) and 0 < value <= MAXIMUM_MS,
                'invalid or over-envelope time: ' + name)
    require(op['root_exit_observed_ms'] <= op['elapsed_ms'], 'whole interval ends before root exit')
    for name in ('peak_job_committed_bytes', 'peak_single_process_committed_bytes',
                 'kernel_total_processes', 'root_pid', 'creation_event_count', 'exit_event_count'):
        require(type(op.get(name)) is int and op[name] > 0, 'missing or impossible measurement: ' + name)
    require(op['peak_single_process_committed_bytes'] <= op['peak_job_committed_bytes'] <= MAXIMUM_JOB_BYTES,
            'invalid or over-envelope aggregate Job committed memory')
    job = load_job()
    try:
        census = job.reconcile_process_events(op.get('process_events'), op['kernel_total_processes'], op['root_pid'])
    except (job.MeasurementError, TypeError, ValueError, KeyError) as exc:
        raise QualificationError('incomplete kernel/process-event reconciliation') from exc
    require(census['complete_memory_scope_valid'] is True
            and census['creation_event_count'] == op['creation_event_count']
            and census['exit_event_count'] == op['exit_event_count'], 'reported process counts do not reconcile')
    require(type(expected_tools) is dict and set(expected_tools) == {'bash', 'python', 'git'},
            'exact Bash, Python and Git identities required')
    observed = op.get('observed_processes')
    require(type(observed) is list and observed, 'actual executable/membership observations are absent')
    pids = {item['pid'] for item in op['process_events'] if item['event'] == 'NEW_PROCESS'}
    for item in observed:
        require(type(item) is dict and type(item.get('pid')) is int and item['pid'] in pids
                and item.get('in_job') is True, 'out-of-job, unknown or unrelated required process')
    for name, expected in expected_tools.items():
        require(type(expected) is dict and set(expected) == {'path', 'sha256'}
                and type(expected['sha256']) is str and re.fullmatch('[0-9a-f]{64}', expected['sha256']),
                'invalid pinned executable identity')
        target = windows_path(expected['path'])
        require(any(windows_path(item.get('image')) == target
                    and item.get('image_sha256') == expected['sha256']
                    and (name != 'bash' or item['pid'] == op['root_pid']) for item in observed),
                'required executable was not observed in the Job: ' + name)
    require(windows_path(expected_command[0]) == windows_path(expected_tools['bash']['path']),
            'root command is not the pinned Bash executable')
    return {'status': 'WITHIN_WINDOWS_ENVELOPE_AT_RECORDED_SCOPE',
            'authority_ceiling': 'NO_NATIVE_OR_ISSUE_ACCEPTANCE',
            'elapsed_ms': op['elapsed_ms'], 'peak_job_committed_bytes': op['peak_job_committed_bytes'],
            'kernel_total_processes': op['kernel_total_processes']}


def validate_fresh_preflight(before, slots):
    require(type(before) is dict and before.get('schema') == 'implementaudit.native-resume-source.v1'
            and before.get('status') == 'PRE_RESUME_EVIDENCE', 'exact native-resume source readback required')
    controller = before.get('controller')
    require(type(controller) is str and re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9._-]*', controller),
            'invalid controller identity')
    require(before.get('boundary') in BOUNDARIES, 'unrecognized original boundary')
    for field, family in [('pointer_token', 'current-generations'),
                          ('invalidation_token', 'continuity-invalidations')]:
        require(type(before.get(field)) is str and re.fullmatch(
            re.escape('refs/implementaudit/' + family + '/' + controller + '@') + '[0-9a-f]{40}', before[field]),
            'missing exact authority token: ' + field)
    pointer = before.get('pointer')
    require(type(pointer) is dict and pointer.get('schema') == 'implementaudit.current-generation.v1',
            'original generation-v1 pointer required')
    for field in ('continuity_epoch', 'projection_generation_id'):
        prior = pointer.get(field)
        require(type(prior) is str and re.fullmatch('G[0-9A-F]{4}', prior), 'noncanonical prior generation')
        require(int(prior[1:], 16) < 65535 and before.get('next_' + field) == 'G%04X' % (int(prior[1:], 16) + 1),
                'native operation must be the next unreused generation')
    require(type(before.get('marker_oid')) is str and re.fullmatch('[0-9a-f]{40}', before['marker_oid']),
            'permanent migration marker required')
    require(slots == {'generation_path_exists': False, 'archive_ref_oid': None,
                      'epoch_ref_oid': None, 'publication_ref_oid': None, 'receipt_ref_oid': None}
            and type(slots.get('generation_path_exists')) is bool,
            'next generation already exists or is unknown; no replay or reuse qualifies a full operation')


def validate_transition(before, after, receipt_raw, pre_payloads, post_payloads,
                        retained_before, retained_after, owner_stdout, verify_stdout, require_stdout):
    require(type(after) is dict and after.get('schema') == 'implementaudit.canonical-generation-resolution.v1',
            'current generation readback missing')
    pointer = after.get('pointer')
    require(type(pointer) is dict and pointer.get('schema') == 'implementaudit.current-generation.v1',
            'current original generation-v1 pointer missing')
    for key in ('controller', 'claim_id', 'run_root_identity'):
        require(after.get(key) == before.get(key) == pointer.get(key), 'subject identity changed: ' + key)
    for key in ('continuity_epoch', 'projection_generation_id'):
        require(pointer.get(key) == before['next_' + key], 'new generation does not match the measured operation')
    require(after.get('marker_oid') == before['marker_oid'], 'permanent marker changed')
    require(after.get('pointer_token') != before['pointer_token']
            and after.get('receipt_token') != before['receipt_token'], 'operation was already satisfied')
    token = after.get('receipt_token')
    require(type(token) is str and all(raw.strip() == token.encode() for raw in
                (owner_stdout, verify_stdout, require_stdout)), 'receipt verify/currentness/owner outputs disagree')
    expected_ref = 'refs/implementaudit/continuity-receipts/' + before['controller'] + '/' + before['next_continuity_epoch']
    require(type(receipt_raw) is bytes and receipt_raw.endswith(b'\n') and not receipt_raw.endswith(b'\n\n')
            and token == expected_ref + '@' + blob_oid(receipt_raw), 'receipt bytes do not bind their Git object identity')
    pointer_raw = json.dumps(pointer, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    require(after.get('pointer_token') == 'refs/implementaudit/current-generations/' + before['controller'] + '@' + blob_oid(pointer_raw),
            'pointer bytes do not bind their Git object identity')
    fields = receipt_raw.rstrip(b'\n').split(b'\t')
    require(len(fields) == 14 and fields[0] == b'implementaudit.continuity-receipt.v3',
            'exact original14 receipt-v3 required')
    expected = ['implementaudit.continuity-receipt.v3', before['controller'], before['claim_id'],
                before['run_root_identity'], before['next_continuity_epoch'],
                before['invalidation_token'].split('@')[1], *after['pointer_token'].split('@'),
                pointer['state_sha256'], pointer['roadmap_sha256'], pointer['protected_manifest_sha256'],
                pointer['archive_manifest_sha256'], pointer['exact_next_action'], before['receipt_token']]
    require(fields == [x.encode() for x in expected], 'receipt is not the exact measured successor')
    require(type(pre_payloads) is dict and set(pre_payloads) == {'STATE', 'ROADMAP'}
            and same_json(pre_payloads, post_payloads), 'protected payload changed or is incomplete')
    require(type(retained_before) is dict and set(retained_before) == {'files', 'refs'}
            and type(retained_before['files']) is dict and set(retained_before['files']) ==
                {'STATE', 'ROADMAP', 'protected', 'archive', 'retired_STATE', 'retired_ROADMAP'}
            and type(retained_before['refs']) is dict and retained_before['refs']
            and same_json(retained_before, retained_after),
            'predecessor pair/archive/retired-root bytes were not preserved')
    refs = retained_before['refs']
    require(refs.get(before['receipt_token'].split('@')[0]) == before['receipt_token'].split('@')[1]
            and refs.get('refs/implementaudit/current-generation-migrations/' + before['controller']) == before['marker_oid']
            and any(key.startswith('refs/implementaudit/state-archives/' + before['controller'] + '/') for key in refs),
            'retained receipt, marker and archive ref population is incomplete')
    require(pointer['exact_next_action'] == before['pointer']['exact_next_action'], 'next action changed')
    return {'status': 'RECORDED_FRESH_ORIGINAL14_TRANSITION_CONSISTENT',
            'authority_ceiling': 'NO_NATIVE_OR_ISSUE_ACCEPTANCE'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('measurement', type=Path)
    parser.add_argument('--request', required=True, type=Path)
    args = parser.parse_args()
    request = strict_json(args.request.read_bytes())
    print(json.dumps(validate_measurement(strict_json(args.measurement.read_bytes()),
                                         request['command'], request['tools']), indent=2))


if __name__ == '__main__':
    main()
