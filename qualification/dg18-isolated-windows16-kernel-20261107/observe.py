"""One closed, fixture-only Windows sharing observation. No Campaign entry."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import threading
import time

SOURCE_COMMIT = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
WRAPPER_SHA256 = '7f433c84bf77701be37365d03ce1073111353eee08bac7a1fefb17adbff3656d'
BRANCH = 'pro/dg18-isolated-windows16-kernel-20261107'
PREFIX = 'qualification/dg18-isolated-windows16-kernel-20261107'
FIXTURE = b'DG18_WINDOWS16_OWNED_SHARING_FIXTURE\n' * 32
INVALID = (1 << 64) - 1
MASKS = {'READ': 0x80000000, 'WRITE': 0x40000000, 'DELETE': 0x10000}
SEQUENCE = (
    ('SOURCE_WRITE_HELD', 'SOURCE', 'WRITE', True),
    ('SOURCE_DELETE_HELD', 'SOURCE', 'DELETE', True),
    ('ALIAS_WRITE_HELD', 'ALIAS', 'WRITE', True),
    ('ALIAS_DELETE_HELD', 'ALIAS', 'DELETE', True),
    ('SOURCE_READ_HELD', 'SOURCE', 'READ', True),
    ('ALIAS_READ_HELD', 'ALIAS', 'READ', True),
    ('SOURCE_WRITE_UNHELD', 'SOURCE', 'WRITE', False),
    ('SOURCE_DELETE_UNHELD', 'SOURCE', 'DELETE', False),
    ('ALIAS_WRITE_UNHELD', 'ALIAS', 'WRITE', False),
    ('ALIAS_DELETE_UNHELD', 'ALIAS', 'DELETE', False),
)
ROW_FIELDS = {'label', 'role', 'access', 'desired_access', 'share_mode', 'holder_live',
              'outcome', 'handle_class', 'handle_sign', 'native_error', 'disk_handle',
              'same_file', 'fixture_links_two', 'metadata_status',
              'close_attempted', 'close_succeeded'}
OUTCOMES = {'DENIED_SHARING', 'DENIED_OTHER', 'NONCANONICAL_INVALID', 'NULL_RETURN',
            'OPENED', 'UNRECEIVED_RETURN_TYPE', 'API_CALL_RAISED'}
HANDLE_CLASSES = {'CANONICAL_INVALID', 'INVALID_BITS_NONCANONICAL', 'NULL',
                  'REAL_INTEGER_CANDIDATE', 'UNRECEIVED_TYPE', 'UNRECEIVED'}

class DiagnosticRefusal(Exception):
    pass

def need(value, reason):
    if not value: raise DiagnosticRefusal(reason)

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()

def identity(value):
    need(type(value) is dict and type(value.get('volume')) is int and value['volume'] > 0
         and type(value.get('file_id')) is str and re.fullmatch('[0-9a-f]{32}', value['file_id']),
         'IDENTITY_UNRECEIVED')
    return value['volume'], value['file_id']

def validate_row(row):
    need(type(row) is dict and set(row) == ROW_FIELDS, 'ROW_FIELDS')
    need((row['label'], row['role'], row['access'], row['holder_live']) in SEQUENCE,
         'ROW_LABEL')
    need(type(row['holder_live']) is bool and type(row['desired_access']) is int
         and row['desired_access'] == MASKS[row['access']] and type(row['share_mode']) is int
         and row['share_mode'] == 7, 'ROW_MASKS')
    need(row['outcome'] in OUTCOMES and row['handle_class'] in HANDLE_CLASSES
         and row['handle_sign'] in {'NEGATIVE', 'ZERO', 'POSITIVE', 'NONE', 'UNRECEIVED'}, 'ROW_ENUM')
    need(row['native_error'] is None or (type(row['native_error']) is int
         and 0 <= row['native_error'] <= 0xffffffff), 'ROW_ERROR')
    need(all(row[k] is None or type(row[k]) is bool
         for k in ('disk_handle', 'same_file', 'fixture_links_two')), 'ROW_TRI_STATE')
    need(row['metadata_status'] in {'NOT_REQUESTED', 'RECEIVED', 'UNAVAILABLE'}, 'ROW_METADATA')
    need(type(row['close_attempted']) is bool and type(row['close_succeeded']) is bool, 'ROW_CLOSE')
    if row['outcome'] in {'DENIED_SHARING', 'DENIED_OTHER', 'NONCANONICAL_INVALID', 'NULL_RETURN'}:
        expected_class = {'DENIED_SHARING': 'CANONICAL_INVALID', 'DENIED_OTHER': 'CANONICAL_INVALID',
                          'NONCANONICAL_INVALID': 'INVALID_BITS_NONCANONICAL', 'NULL_RETURN': 'NULL'}[row['outcome']]
        need(row['handle_class'] == expected_class and not row['close_attempted'] and row['close_succeeded']
             and row['metadata_status'] == 'NOT_REQUESTED'
             and all(row[k] is None for k in ('disk_handle', 'same_file', 'fixture_links_two')), 'ROW_NO_HANDLE')
        if row['outcome'] == 'DENIED_SHARING':
            need(row['native_error'] in (32, 33), 'ROW_SHARING_ERROR')
        if row['outcome'] == 'DENIED_OTHER':
            need(row['native_error'] not in (32, 33), 'ROW_OTHER_ERROR')
    if row['outcome'] == 'OPENED':
        need(row['handle_class'] == 'REAL_INTEGER_CANDIDATE' and row['handle_sign'] in {'POSITIVE', 'NEGATIVE'}
             and row['close_attempted'] and row['native_error'] is None
             and row['metadata_status'] in {'RECEIVED', 'UNAVAILABLE'}, 'ROW_OPENED')
        if row['metadata_status'] == 'RECEIVED':
            need(all(type(row[k]) is bool for k in ('disk_handle', 'same_file', 'fixture_links_two')), 'ROW_RECEIVED')
        else:
            need(any(row[k] is None for k in ('disk_handle', 'same_file', 'fixture_links_two')), 'ROW_UNAVAILABLE')
    if row['outcome'] == 'UNRECEIVED_RETURN_TYPE':
        need(row['handle_class'] == 'UNRECEIVED_TYPE' and not row['close_attempted']
             and not row['close_succeeded'], 'ROW_UNRECEIVED_TYPE')
    need(len(canonical(row)) <= 1024, 'ROW_BOUND')
    return row

def observe_open(api, path, label, role, access, held, expected_identity):
    need((label, role, access, held) in SEQUENCE and type(held) is bool, 'PROBE_LABEL')
    row = {'label': label, 'role': role, 'access': access, 'desired_access': MASKS[access],
           'share_mode': 7, 'holder_live': held, 'outcome': 'API_CALL_RAISED',
           'handle_class': 'UNRECEIVED', 'handle_sign': 'UNRECEIVED', 'native_error': None,
           'disk_handle': None, 'same_file': None, 'fixture_links_two': None,
           'metadata_status': 'NOT_REQUESTED', 'close_attempted': False, 'close_succeeded': False}
    h = None
    try:
        # Exact request shape of the original fixture's conflicting opens.
        h = api.create(str(path), MASKS[access], 7, None, 3, 0x00200000, None)
        error = api.C.get_last_error()  # Receive immediately; never interpret stale success error.
    except BaseException:
        if type(h) is int and h & INVALID != INVALID and h != 0:
            row['close_attempted'] = True
            try: row['close_succeeded'] = bool(api.close(h))
            except BaseException: pass
        return validate_row(row)
    if h is None:
        row.update(outcome='NULL_RETURN', handle_class='NULL', handle_sign='NONE', close_succeeded=True)
    elif type(h) is not int:
        row.update(outcome='UNRECEIVED_RETURN_TYPE', handle_class='UNRECEIVED_TYPE')
    else:
        row['handle_sign'] = 'NEGATIVE' if h < 0 else 'ZERO' if h == 0 else 'POSITIVE'
        if h & INVALID == INVALID:
            canonical_invalid = h == api.invalid
            row.update(handle_class='CANONICAL_INVALID' if canonical_invalid else 'INVALID_BITS_NONCANONICAL',
                       outcome=('DENIED_SHARING' if error in (32, 33) else 'DENIED_OTHER')
                               if canonical_invalid else 'NONCANONICAL_INVALID',
                       native_error=error if type(error) is int and 0 <= error <= 0xffffffff else None,
                       close_succeeded=True)
        elif h == 0:
            row.update(outcome='NULL_RETURN', handle_class='NULL', close_succeeded=True)
        else:
            row.update(outcome='OPENED', handle_class='REAL_INTEGER_CANDIDATE')
            try:
                row['disk_handle'] = api.filetype(h) == 1
                value = api.metadata(h)
                row['same_file'] = identity(value) == identity(expected_identity)
                row['fixture_links_two'] = type(value.get('links')) is int and value['links'] == 2
                row['metadata_status'] = 'RECEIVED'
            except BaseException:
                row['metadata_status'] = 'UNAVAILABLE'
            finally:
                row['close_attempted'] = True
                try: row['close_succeeded'] = bool(api.close(h))
                except BaseException: row['close_succeeded'] = False
    return validate_row(row)

class Window:
    def __init__(self):
        self.start_mono = time.perf_counter_ns()
        self.start_wall = time.time_ns()
        self.last_mono = self.start_mono
        self.last_wall = self.start_wall
    def check(self):
        now_mono = time.perf_counter_ns()
        now_wall = time.time_ns()
        need(now_mono >= self.last_mono and now_wall >= self.last_wall, 'CLOCK_BACKWARDS')
        mono = now_mono - self.start_mono
        wall = now_wall - self.start_wall
        need(0 <= mono < 30_000_000_000 and 0 <= wall < 30_000_000_000
             and abs(mono - wall) <= 1_000_000_000, 'CLOCK_REFUSAL')
        self.last_mono, self.last_wall = now_mono, now_wall
        return mono

def sequence(api, source, alias, window, observations, state):
    paths = {'SOURCE': source, 'ALIAS': alias}
    with api.opened(source, rename=True) as held_handle:
        state['holder_entered'] = True
        before, raw, descriptor = api.snapshot(held_handle, multiple=True)
        need(raw == FIXTURE and before['native']['links'] == 2, 'FIXTURE_ORIGIN')
        expected = before['native']
        for label, role, access, held in SEQUENCE[:6]:
            window.check()
            row = observe_open(api, paths[role], label, role, access, held, expected)
            observations.append(row)
            need(row['close_succeeded'], 'HANDLE_CLOSE_UNKNOWN')
            window.check()
        after, raw_after, descriptor_after = api.snapshot(held_handle, multiple=True)
        state['held_snapshot_unchanged'] = (after == before and raw_after == raw and descriptor_after == descriptor)
        need(state['held_snapshot_unchanged'], 'HOLDER_CHANGED')
    state['holder_context_exit_passed'] = True
    for label, role, access, held in SEQUENCE[6:]:
        window.check()
        row = observe_open(api, paths[role], label, role, access, held, expected)
        observations.append(row)
        need(row['close_succeeded'], 'HANDLE_CLOSE_UNKNOWN')
        window.check()

def read_context():
    run = os.environ.get('GITHUB_RUN_ID', '')
    commit = os.environ.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9]{1,20}', run) and re.fullmatch('[0-9a-f]{40}', commit)
         and os.environ.get('GITHUB_RUN_ATTEMPT') == '1'
         and os.environ.get('GITHUB_REPOSITORY') == 'theislampill/IMPLEMENTAUDIT.md'
         and os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH, 'HOST_CONTEXT')
    need(os.name == 'nt' and sys.platform == 'win32' and sys.implementation.name == 'cpython'
         and sys.version_info[:3] == (3, 12, 10) and sys.maxsize == (1 << 63) - 1, 'HOST_RUNTIME')
    temp = Path(os.environ['RUNNER_TEMP'])
    need(temp.is_absolute() and temp.is_dir(), 'HOST_TEMP')
    return {'run_id': run, 'attempt': '1', 'workflow_commit': commit, 'source_commit': SOURCE_COMMIT}, temp

def source_module():
    p = Path(__file__).resolve().with_name('windows15_held_admission.py')
    raw = p.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WRAPPER_SHA256, 'WRAPPER_PIN')
    spec = importlib.util.spec_from_file_location('dg18_iw16_reviewed_api', p)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def validate_result(value, context):
    fields = {'schema', 'context', 'scope', 'status', 'phase', 'error_class', 'wrapper_sha256',
              'observer_sha256', 'observations', 'state', 'sequence_elapsed_ms',
              'timing_scope', 'process_watchdog_seconds', 'kernel_sharing_guard_satisfied',
              'cleanup', 'native_W_FULL_started', 'installed_Git_image_mutated',
              'inference', 'original_acceptance', 'automatic_retry', 'process_completion_required'}
    need(type(value) is dict and set(value) == fields, 'RESULT_FIELDS')
    need(value['schema'] == 'dg18.windows16.kernel-sharing-observation.v1'
         and value['context'] == context and value['scope'] == 'OWNED_FIXTURE_ONLY', 'RESULT_CONTEXT')
    need(value['status'] in {'OBSERVATION_COMPLETE', 'REFUSED'}
         and value['phase'] in {'CODE', 'FIXTURE_ALLOCATION', 'PROBES', 'RECEIVING', 'NONE'}
         and value['error_class'] in {None, 'PREDICATE_REFUSED', 'WINDOWS_API_REFUSED', 'IO_REFUSED', 'UNEXPECTED_FAILURE'},
         'RESULT_ENUMS')
    need(value['wrapper_sha256'] == WRAPPER_SHA256 and type(value['observer_sha256']) is str
         and re.fullmatch('[0-9a-f]{64}', value['observer_sha256']), 'RESULT_PINS')
    need(type(value['observations']) is list and len(value['observations']) <= 10, 'RESULT_ROWS')
    for index, row in enumerate(value['observations']):
        validate_row(row)
        need((row['label'], row['role'], row['access'], row['holder_live']) == SEQUENCE[index], 'RESULT_ORDER')
    need(type(value['state']) is dict and set(value['state']) == {'holder_entered', 'holder_context_exit_passed',
         'held_snapshot_unchanged', 'fixture_bytes_unchanged', 'parent_context_exit_passed'}
         and all(type(v) is bool for v in value['state'].values()), 'RESULT_STATE')
    need(value['sequence_elapsed_ms'] is None or (type(value['sequence_elapsed_ms']) is int
         and 0 <= value['sequence_elapsed_ms'] < 30000), 'RESULT_TIMING')
    need(value['timing_scope'] == 'FIXTURE_SEQUENCE_THROUGH_HANDLE_CLOSURE; NOT_W_FULL_OR_WHOLE_JOB_COST'
         and type(value['process_watchdog_seconds']) is int and value['process_watchdog_seconds'] == 30,
         'RESULT_TIMING_SCOPE')
    need(type(value['kernel_sharing_guard_satisfied']) is bool
         and value['cleanup'] in {'ALL_OWNED_HANDLE_CALLS_CLOSED', 'UNKNOWN'}, 'RESULT_GUARD')
    need(all(value[k] is False for k in ('native_W_FULL_started', 'installed_Git_image_mutated',
         'inference', 'original_acceptance', 'automatic_retry'))
         and value['process_completion_required'] is True, 'RESULT_SCOPE')
    expected_guard = (value['status'] == 'OBSERVATION_COMPLETE' and len(value['observations']) == 10
         and all(value['state'].values()) and value['cleanup'] == 'ALL_OWNED_HANDLE_CALLS_CLOSED'
         and all(r['outcome'] == 'DENIED_SHARING' and r['close_succeeded'] for r in value['observations'][:4])
         and all(r['outcome'] == 'OPENED' and r['metadata_status'] == 'RECEIVED'
                 and r['disk_handle'] is True and r['same_file'] is True
                 and r['fixture_links_two'] is True and r['close_succeeded'] for r in value['observations'][4:]))
    need(value['kernel_sharing_guard_satisfied'] == expected_guard, 'RESULT_DERIVED_GUARD')
    if value['status'] == 'OBSERVATION_COMPLETE':
        need(len(value['observations']) == 10 and value['phase'] == 'NONE' and value['error_class'] is None
             and all(value['state'].values()) and value['sequence_elapsed_ms'] is not None
             and value['cleanup'] == 'ALL_OWNED_HANDLE_CALLS_CLOSED'
             and all(r['close_succeeded'] for r in value['observations']), 'RESULT_COMPLETION')
    else:
        need(value['error_class'] is not None and value['phase'] != 'NONE'
             and value['cleanup'] == 'UNKNOWN' and not value['kernel_sharing_guard_satisfied'], 'RESULT_REFUSAL')
    need(len(canonical(value)) <= 16384, 'RESULT_BOUND')
    return value

def observe(context, temp):
    window = Window()
    stop = threading.Event()
    def watchdog():
        remaining = (window.start_mono + 30_000_000_000 - time.perf_counter_ns()) / 1_000_000_000
        if remaining <= 0 or not stop.wait(remaining): os._exit(124)
    timer = threading.Thread(target=watchdog, name='iw16-fixed-deadline', daemon=True)
    timer.start()
    output = temp / ('dg18-iw16-kernel-' + context['run_id'] + '-1')
    rows = []
    state = {'holder_entered': False, 'holder_context_exit_passed': False,
             'held_snapshot_unchanged': False, 'fixture_bytes_unchanged': False,
             'parent_context_exit_passed': False}
    result = {'schema': 'dg18.windows16.kernel-sharing-observation.v1', 'context': context,
              'scope': 'OWNED_FIXTURE_ONLY', 'status': 'REFUSED', 'phase': 'CODE',
              'error_class': None, 'wrapper_sha256': WRAPPER_SHA256,
              'observer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'observations': rows, 'state': state, 'sequence_elapsed_ms': None,
              'timing_scope': 'FIXTURE_SEQUENCE_THROUGH_HANDLE_CLOSURE; NOT_W_FULL_OR_WHOLE_JOB_COST',
              'process_watchdog_seconds': 30, 'kernel_sharing_guard_satisfied': False,
              'cleanup': 'UNKNOWN', 'native_W_FULL_started': False, 'installed_Git_image_mutated': False,
              'inference': False, 'original_acceptance': False, 'automatic_retry': False,
              'process_completion_required': True}
    try:
        module = source_module()
        window.check()
        module.physical(temp)
        output.mkdir(exist_ok=False)
        api = module.WindowsCustody()
        parent = module.physical(Path(module.GIT_CANDIDATES[1]).parent)
        module.ntfs(parent)
        result['phase'] = 'FIXTURE_ALLOCATION'
        with api.directories(parent):
            work = parent / ('dg18-iw16-kernel-' + context['run_id'] + '-1')
            work.mkdir(exist_ok=False)
            module.ntfs(work)
            source, alias = work / 'origin.exe', work / 'alias.exe'
            module.save(source, FIXTURE)
            os.link(source, alias)
            window.check()
            result['phase'] = 'PROBES'
            sequence(api, source, alias, window, rows, state)
            result['phase'] = 'RECEIVING'
            state['fixture_bytes_unchanged'] = source.read_bytes() == alias.read_bytes() == FIXTURE
            need(state['fixture_bytes_unchanged'], 'FIXTURE_BYTES_CHANGED')
        state['parent_context_exit_passed'] = True
        result['sequence_elapsed_ms'] = window.check() // 1_000_000
        result.update(status='OBSERVATION_COMPLETE', phase='NONE', cleanup='ALL_OWNED_HANDLE_CALLS_CLOSED')
        result['kernel_sharing_guard_satisfied'] = (
            all(r['outcome'] == 'DENIED_SHARING' and r['close_succeeded'] for r in rows[:4])
            and all(r['outcome'] == 'OPENED' and r['metadata_status'] == 'RECEIVED'
                    and r['disk_handle'] is True and r['same_file'] is True
                    and r['fixture_links_two'] is True and r['close_succeeded'] for r in rows[4:]))
    except BaseException as exc:
        result['error_class'] = ('PREDICATE_REFUSED' if isinstance(exc, DiagnosticRefusal)
            else 'WINDOWS_API_REFUSED' if type(exc).__name__ == 'CustodyApiError'
            else 'IO_REFUSED' if isinstance(exc, OSError) else 'UNEXPECTED_FAILURE')
    try:
        window.check()
        raw = canonical(validate_result(result, context))
        with (output / 'RESULT.json').open('xb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        window.check()
        print('DG18_WINDOWS16_CLOSED_OBSERVATION_WRITTEN')
        return 0
    finally:
        stop.set(); timer.join(timeout=0.2)

def main():
    try:
        need(len(sys.argv) == 2 and sys.argv[1] in {'observe', 'validate'}, 'ACTION')
        context, temp = read_context()
        if sys.argv[1] == 'observe': return observe(context, temp)
        path = temp / ('dg18-iw16-kernel-' + context['run_id'] + '-1') / 'RESULT.json'
        raw = path.read_bytes(); need(len(raw) <= 16384, 'RESULT_BOUND')
        value = json.loads(raw)
        need(raw == canonical(validate_result(value, context)), 'RESULT_CANONICAL')
        need(value['observer_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'OBSERVER_PIN')
        print('DG18_WINDOWS16_CLOSED_OBSERVATION_VALIDATED')
        return 0
    except BaseException:
        print('DG18_WINDOWS16_REFUSED')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
