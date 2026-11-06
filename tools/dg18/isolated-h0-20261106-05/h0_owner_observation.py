#!/usr/bin/env python3
"""Prospective H0 observations. Data only; never an owner/currentness authority.

Only run_observed() is integrated into the closed MCP adapter. It wraps the
already selected pending-owner argv and canonical request. Native guard files
are unmodified and execute normally under a bounded, selected Python trace.
The supervisor uses the finite05 prospective 80s completion watchdog.
LOAD, native-call, other-command and cleanup limits are separate and unchanged.
Journal counters cover previous completed emissions only; current/final emission
and counter-update tails are uncovered. Nested phase costs must never be summed.
"""
from __future__ import annotations
import ast
import dis
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import runpy
import selectors
import signal
import stat
import subprocess
import sys
import time

WATCHDOG_SECONDS = 80
CLEANUP_SECONDS = 2
MAX_INPUT = 65536
MAX_OUTPUT = 128 * 1024
MAX_STATE = 8 * 1024 * 1024
MAX_JOURNAL = 2 * 1024 * 1024
MAX_EVENTS = 4096
MAX_PUBLIC = 32768
DIRECTORY = 'h0-owner-observations-v2'
HEX = re.compile(r'[0-9a-f]{64}\Z')
SCHEMA = 'dg18.h0-owner-observation.v2'
# Filled once by the author from the immutable selected source. The source-owner
# selection constant is normalized to None, while its actual bytes are ALSO
# checked against the same assignment code pin used by the existing owner.
SOURCE_SHA256 = {'compaction-audit-pending.py': '729f7eb108b30647bf62e19d71be4cd10e41486af020a6dc69b8aa6295d8aee5', 'host-session-binding.py': '8b4f91a51e2e2d45c4bd72b58fb1e115981903f8a752f95eb71cda64b106b6ef', 'compaction-result-observation.py': 'a68145e62a0a81dfb02fc48f72cefaf3740e499bf6b85bd70f5d30cc64a038c1', 'compaction-source-owner-codex-app.py': '5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8', 'bounded_source_owner.py': 'bb6cfe1f4da62625cd6578f23102242ad35b0a6b1068a54da991ceec8a94da4e', 'bounded_native_reader.py': '1f72979eb39138d999843c127893c8dbeba97cc8c5546b19c3725758011df5a6', 'codex-recovery-native-reader.py': 'a6cb50e4926b106400864755599c096ab0b7236e7d5368184dbde9117fb35d06', 'route-transaction.py': 'b998eb7c4cd96949e9f20a4e1340b4001fe4e0751225565775fdca1569563cab'}
REQUIRED_CODE = ('implementaudit/SKILL.md','audit-state/SKILL.md',
 'implementaudit/references/child-agents.md','implementaudit/references/continuity.md') + tuple(
 'implementaudit/scripts/'+n for n in ('compaction-audit-pending.py','compaction-result-observation.py',
 'compaction-source-owner-codex-app.py','codex-recovery-native-reader.py','bounded_file_custody.py',
 'bounded_native_reader.py','bounded_source_owner.py','host-session-binding.py','route-transaction.py',
 'compaction-prior-protocol.py','compaction-prior-mcp.py'))
JOURNAL_COST_FIELDS = {'events','through_sequence','bytes','emission_ns','write_ns','fsync_ns'}
JOURNAL_TIMING_FIELDS = ('emission_ns','write_ns','fsync_ns')
COST_SCOPE = 'DISJOINT_PREVIOUS_COMPLETED_EMISSIONS_ONLY'
COST_UNCOVERED = 'CURRENT_FINAL_EMISSION_AND_COUNTER_UPDATE_TAILS'
PHASE_COST_SCOPE = 'NESTED_INCLUSIVE_DO_NOT_SUM_OR_ADD_JOURNAL_COST'
FUNCTIONS = {
 'compaction-audit-pending.py': {
  'operate':'owner.operate', 'attribution':'owner.attribution',
  'load':'state.load', '_pending_state_bytes':'io.pending_state',
  'refresh':'owner.refresh', 'nonprotected_code_identity':'validation.code',
  '_assignment_code_identity':'validation.assignment_code',
  'prior_history_context':'validation.prior_context',
  'hold_checked':'validation.hold_checked', 'save':'mutation.save'},
 'host-session-binding.py': {'writer_lock':'lock.scope','atomic_json':'mutation.atomic_json',
  'load_owner':'validation.store_owner','load_state':'state.binding','current_record':'validation.current_record'},
 'compaction-result-observation.py': {
  'authorization':'validation.authorization','completed_exchange':'validation.exchange',
  'hold_history':'validation.hold_history','_hold_history_unheld':'validation.history',
  'prior_record_occurrences':'validation.prior_occurrences',
  'classify_prior_retry':'validation.prior_retry',
  'original_bind_records':'validation.original_bind','history_with_priors':'validation.history_with_priors',
  '_nonprotected_source_owner':'custody.owner_code',
  '_nonprotected_read_records':'io.nonprotected_records','read_records':'io.records',
  'hold_records':'io.hold_records','artifact':'io.artifact'},
 'compaction-source-owner-codex-app.py': {
  '_np_runtime':'custody.runtime','_np_episode':'currentness.episode',
  '_np_module':'route.module_custody',
  '_mechanical_sources_guard_v1':'custody.source_guard_factory',
  '_mechanical_sources_guard_v1.<locals>.guard':'custody.source_guard',
  'FreshCanaryPosixCustodyV1.held_file':'custody.file'},
 'route-transaction.py': {'<module>':'route.module_exec',
  'current_controller':'route.controller_open',
  '_pure_route_semantics_v1':'route.semantics',
  'read_current_episode_binding_v1':'route.episode'},
 'bounded_source_owner.py': {'header':'io.header','read_public':'io.public','discover_public':'io.discovery'},
 'bounded_native_reader.py': {'probe':'owner.reader_probe','_probe_held':'owner.reader_work','cleanup_probe':'cleanup.reader'},
 'codex-recovery-native-reader.py': {'native_read_nonprotected':'owner.native_read'},
}
MARKERS = {
 'host-session-binding.py': [
  ('writer_lock','            fcntl.flock(descriptor, fcntl.LOCK_EX)','lock.wait'),
  ('writer_lock','            locked = True','lock.acquired'),
  ('writer_lock','                fcntl.flock(descriptor, fcntl.LOCK_UN)','cleanup.lock_release'),
  ('atomic_json','        os.replace(temporary, target)','mutation.replace_enter')],
 'compaction-result-observation.py': [
  ('prior_record_occurrences','        if identifier not in cache:','validation.prior_visit'),
  ('prior_record_occurrences',"            raw, _ = artifact(prior['obligation_pin'])",'validation.prior_revalidate')],
}
PHASES = frozenset(p for fs in FUNCTIONS.values() for p in fs.values()) | frozenset(p for ms in MARKERS.values() for _,_,p in ms) | {'worker','cleanup.supervisor','route.controller_close'}
EVENTS = frozenset({'start','enter','resume','yield','return','unwind','exception','marker','refused','finish'})
BINDING_KEYS = {'schema','invocation_nonce','selection_sha256','request_sha256','wire_request_sha256',
 'native_metadata_sha256','episode_binding_sha256','observation_source_sha256','assignment_code_sha256','session_sha256','child_sha256','observation_sha256',
 'operation','call_ordinal','preflight','authority'}

class ObservationRefusal(ValueError):
    pass

def need(ok, code='H0_OWNER_OBSERVATION_REFUSED'):
    if not ok:
        raise ObservationRefusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')

def unique(pairs):
    value = dict(pairs)
    need(len(value) == len(pairs))
    return value

def parse(raw, limit):
    need(type(raw) is bytes and 0 < len(raw) <= limit)
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(ObservationRefusal()))
    def bounded(v, depth=0):
        need(depth <= 48)
        if isinstance(v, dict):
            need(len(v) <= 10000 and all(type(k) is str and len(k) <= 2048 for k in v))
            for x in v.values(): bounded(x, depth+1)
        elif isinstance(v, list):
            need(len(v) <= 100000)
            for x in v: bounded(x, depth+1)
        elif isinstance(v, float): need(math.isfinite(v))
        else: need(v is None or type(v) in (str, int, bool))
    bounded(value)
    return value

def identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'bytes':info.st_size,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}

def safe_directory(path, *, private=False):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path)
    for parent in (path, *path.parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode))
    info = path.stat()
    if private: need(info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700)
    return path

def read_safe(path, maximum):
    path = Path(path)
    safe_directory(path.parent)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= maximum)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        need(identity(os.fstat(fd)) == identity(before))
        blocks = []; total = 0
        while True:
            block = os.read(fd, min(65536, maximum+1-total))
            if not block: break
            blocks.append(block); total += len(block); need(total <= maximum)
        need(identity(os.fstat(fd)) == identity(before) == identity(path.lstat()))
        raw = b''.join(blocks); need(len(raw) == before.st_size)
        return raw, identity(before)
    finally:
        os.close(fd)

def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: os.fsync(fd)
    finally: os.close(fd)

def exclusive_json(path, value, maximum=MAX_PUBLIC):
    raw = canonical(value)+b'\n'; need(len(raw) <= maximum)
    safe_directory(Path(path).parent, private=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view); need(written > 0); view = view[written:]
        os.fsync(fd)
    finally: os.close(fd)
    sync_directory(Path(path).parent)

def validate_binding(value):
    need(type(value) is dict and set(value) == BINDING_KEYS)
    need(value['schema'] == SCHEMA and value['authority'] == 'NONE')
    need(value['operation'] in ('DELIVER','BIND') and value['preflight'] == 'ACTUAL_PENDING_CALL_VALIDATED')
    need(type(value['call_ordinal']) is int and 0 <= value['call_ordinal'] <= 6)
    need(type(value['invocation_nonce']) is str and re.fullmatch('[0-9a-f]{32}', value['invocation_nonce']))
    for key in BINDING_KEYS:
        if key.endswith('_sha256'): need(type(value[key]) is str and HEX.fullmatch(value[key]))
    return value

def process_identity(pid):
    # Only Linux process facts, no argv/environ/cwd/fd data is exposed.
    try:
        raw = Path('/proc')/str(pid)/'stat'
        data = raw.read_bytes()
        need(len(data) <= 8192)
        tail = data[data.rfind(b')')+2:].split()
        return {'pid':int(pid),'ppid':int(tail[1]),'birth_ticks':int(tail[19])}
    except (OSError, ValueError, IndexError, ObservationRefusal):
        return None

def process_valid(value):
    return value is None or (type(value) is dict and set(value) == {'pid','ppid','birth_ticks'}
      and all(type(n) is int and 0 < n < 2**63 for n in value.values()))


def wait_sample(expected):
    sample = {'status':'UNAVAILABLE','run_state':'UNKNOWN','wait_class':'UNKNOWN'}
    if expected is None or process_identity(expected['pid']) != expected:
        return sample
    try:
        base = Path('/proc')/str(expected['pid'])
        raw = (base/'stat').read_bytes(); need(len(raw) <= 8192)
        state = raw[raw.rfind(b')')+2:].split()[0].decode('ascii')
        raw_wait = (base/'wchan').read_bytes(); need(len(raw_wait) <= 256)
        wait = raw_wait.strip()
        need(process_identity(expected['pid']) == expected)
        kind = ('FILE_LOCK' if b'locks_lock' in wait or b'flock' in wait else
                'PIPE' if b'pipe' in wait else 'FUTEX' if b'futex' in wait else
                'IO' if any(x in wait for x in (b'io_',b'folio',b'page_',b'fsync')) else
                'POLL' if b'poll' in wait else 'SLEEP' if b'hrtimer' in wait else
                'RUNNING_OR_UNAVAILABLE' if wait in (b'0',b'') else 'OTHER')
        sample.update(status='SAME_CHILD_AT_READ',run_state=state if state in 'RSDZTtIXP' else 'UNKNOWN',wait_class=kind)
    except (OSError,ValueError,IndexError): pass
    return sample


def make_run(store, binding, code_pins):
    validate_binding(binding)
    need(type(code_pins) is dict and sha(canonical(code_pins)) == binding['assignment_code_sha256'])
    root = safe_directory(store) / DIRECTORY
    try: root.mkdir(mode=0o700)
    except FileExistsError: pass
    safe_directory(root, private=True)
    run = root / sha(canonical(binding)); run.mkdir(mode=0o700)  # no retry/reuse
    sync_directory(root)
    exclusive_json(run/'binding.json', binding)
    exclusive_json(run/'code-pins.json', code_pins)
    return run

class Journal:
    def __init__(self, run, binding):
        self.binding_sha = sha(canonical(validate_binding(binding)))
        need(Path(run).name == self.binding_sha)
        safe_directory(run, private=True)
        self.fd = os.open(Path(run)/'owner.jsonl', os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
        self.start_ns = time.monotonic_ns(); self.seq = 0; self.bytes = 0
        self.previous = self.binding_sha; self.closed = False
        self.cost = {k:0 for k in JOURNAL_TIMING_FIELDS}
        self.emit('start','worker',0, {'process':process_identity(os.getpid()),'monotonic_ns':self.start_ns})
    def emit(self, event, phase, frame, data=None):
        t0 = time.monotonic_ns()
        need(not self.closed and event in EVENTS and phase in PHASES)
        need(self.seq < MAX_EVENTS)
        # Snapshot only earlier fully completed emissions. The event containing
        # this snapshot cannot measure its own eventual write or fsync.
        cost = dict(self.cost, events=self.seq, through_sequence=self.seq-1, bytes=self.bytes)
        row = {'schema':SCHEMA,'binding_sha256':self.binding_sha,'sequence':self.seq,
               'elapsed_ns':t0-self.start_ns,'event':event,'phase':phase,
               'frame':frame,'data':data or {},'previous_sha256':self.previous,'journal_cost':cost}
        validate_event(row)
        raw = canonical(row)+b'\n'; need(self.bytes+len(raw) <= MAX_JOURNAL)
        view = memoryview(raw); t1 = time.monotonic_ns()
        while view:
            written = os.write(self.fd, view); need(written > 0); view = view[written:]
        t2 = time.monotonic_ns()
        os.fsync(self.fd)
        t3 = time.monotonic_ns()
        self.seq += 1; self.bytes += len(raw); self.previous = sha(raw)
        t4 = time.monotonic_ns()
        # These measured intervals are disjoint. This counter-update tail,
        # Journal construction/close and other tracing overhead are unmeasured.
        self.cost['emission_ns'] += (t1-t0)+(t4-t3)
        self.cost['write_ns'] += t2-t1
        self.cost['fsync_ns'] += t3-t2
    def close(self):
        if not self.closed: os.close(self.fd); self.closed = True

def validate_cost(cost, sequence, elapsed_ns):
    need(type(cost) is dict and set(cost) == JOURNAL_COST_FIELDS)
    need(all(type(v) is int for v in cost.values()))
    need(cost['events'] == sequence and cost['through_sequence'] == sequence-1)
    need(0 <= cost['bytes'] <= MAX_JOURNAL)
    need(all(0 <= cost[k] <= elapsed_ns for k in JOURNAL_TIMING_FIELDS))
    need(sum(cost[k] for k in JOURNAL_TIMING_FIELDS) <= elapsed_ns)
    if sequence == 0: need(cost['bytes'] == 0 and all(cost[k] == 0 for k in JOURNAL_TIMING_FIELDS))

def validate_event(row):
    need(type(row) is dict and set(row) == {'schema','binding_sha256','sequence','elapsed_ns','event','phase','frame','data','previous_sha256','journal_cost'})
    need(row['schema'] == SCHEMA and all(type(row[k]) is str and HEX.fullmatch(row[k]) for k in ('binding_sha256','previous_sha256')))
    need(type(row['sequence']) is int and 0 <= row['sequence'] < MAX_EVENTS)
    need(type(row['elapsed_ns']) is int and 0 <= row['elapsed_ns'] < 3600*10**9)
    validate_cost(row['journal_cost'],row['sequence'],row['elapsed_ns'])
    need(type(row['frame']) is int and 0 <= row['frame'] <= MAX_EVENTS)
    need(row['event'] in EVENTS and row['phase'] in PHASES)
    data = row['data']; need(type(data) is dict)
    if row['event'] == 'start':
        need(row['phase'] == 'worker' and row['frame'] == 0 and set(data) == {'process','monotonic_ns'} and process_valid(data['process']))
        need(type(data['monotonic_ns']) is int and 0 < data['monotonic_ns'] < 2**63)
    elif row['event'] == 'return' and row['phase'] == 'currentness.episode':
        need(set(data) == {'value_sha256'} and type(data['value_sha256']) is str and HEX.fullmatch(data['value_sha256']))
    else: need(data == {})

def source_contract(directory, code_pins):
    directory = safe_directory(directory)
    need(type(code_pins) is dict and set(code_pins) == set(REQUIRED_CODE)
      and all(type(v) is str and HEX.fullmatch(v) for v in code_pins.values()))
    functions = {}; markers = {}
    for filename, names in FUNCTIONS.items():
        path = directory/filename; raw, _ = read_safe(path, 512*1024)
        need(code_pins.get('implementaudit/scripts/'+filename) == sha(raw))
        normalized = raw
        if filename == 'compaction-source-owner-codex-app.py':
            lines = raw.splitlines(keepends=True)
            slots = [i for i,line in enumerate(lines) if line.startswith(b'MECHANICAL_SELECTION_PIN = ')]
            need(len(slots) == 1)
            lines[slots[0]] = b'MECHANICAL_SELECTION_PIN = None\n'; normalized = b''.join(lines)
        need(sha(normalized) == SOURCE_SHA256[filename])
        tree = ast.parse(raw)
        defined = {n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        need(all(name == '<module>' or name.split('.')[-1] in defined for name in names))
        functions[str(path)] = names
        lines = raw.decode('utf-8').splitlines()
        for function, literal, phase in MARKERS.get(filename, []):
            matches = [i+1 for i,line in enumerate(lines) if line == literal]
            need(len(matches) == 1)
            markers[(str(path), function, matches[0])] = phase
    return functions, markers

class Trace:
    def __init__(self, journal, source_dir, code_pins):
        self.journal = journal
        self.functions, self.markers = source_contract(source_dir,code_pins)
        self.frames = {}; self.next_frame = 0
        self.source_owner_path = str(Path(source_dir)/'compaction-source-owner-codex-app.py')
        self.route_path = str(Path(source_dir)/'route-transaction.py')
    def __call__(self, frame, event, arg):
        filename = frame.f_code.co_filename
        names = self.functions.get(filename)
        if names is None: return None
        qualname = getattr(frame.f_code,'co_qualname', frame.f_code.co_name)
        phase = names.get(qualname)
        if phase is None: return None
        # Select only exact pinned code metadata. Never inspect f_locals,
        # arguments, exception payloads, return values or private paths here.
        caller = frame.f_back
        caller_file = caller.f_code.co_filename if caller is not None else None
        caller_name = getattr(caller.f_code,'co_qualname',caller.f_code.co_name) if caller is not None else None
        if phase == 'route.module_custody':
            if caller_file != self.source_owner_path or caller_name != '_np_episode': return None
        elif phase == 'route.module_exec':
            if caller_file != self.source_owner_path or caller_name != '_np_module': return None
        elif phase == 'route.controller_open':
            if caller_file != self.route_path: return None
            if caller_name == 'current_route_observation_v1.<locals>.closing': phase = 'route.controller_close'
            elif caller_name != '_open_pure_route_read_v1': return None
        if phase.startswith('route.'):
            frame.f_trace_lines = False  # No line markers in these new phases.
        key = id(frame)
        if event == 'call':
            if key in self.frames:
                self.journal.emit('resume',phase,self.frames[key])
            else:
                self.next_frame += 1; self.frames[key] = self.next_frame
                self.journal.emit('enter',phase,self.next_frame)
        elif event == 'line':
            marker = self.markers.get((filename,frame.f_code.co_name,frame.f_lineno))
            if marker: self.journal.emit('marker',marker,self.frames[key])
        elif event == 'exception':
            # No exception object, message, locals or frame arguments are read.
            self.journal.emit('exception',phase,self.frames[key])
        elif event == 'return':
            opcode = dis.opname[frame.f_code.co_code[frame.f_lasti]]
            kind = 'yield' if opcode in ('YIELD_VALUE','YIELD_FROM') else ('return' if opcode in ('RETURN_VALUE','RETURN_CONST') else 'unwind')
            data = {'value_sha256':sha(canonical(arg))} if kind == 'return' and phase == 'currentness.episode' else None
            self.journal.emit(kind,phase,self.frames[key],data)
            if kind != 'yield': self.frames.pop(key)
        return self

def state_snapshot(path, binding):
    """Passive bounded file view; never canonical currentness or sole-writer proof."""
    result = {'status':'UNAVAILABLE','sha256':None,'physical':None,'revision':None,
              'assignment_sha256':None,'prepared_present':False,'bound_response_sha256':None,
              'authority':'NONE','currentness':'NOT_EVALUATED'}
    try:
        raw, physical = read_safe(path,MAX_STATE)
        state = parse(raw,MAX_STATE)
        need(type(state) is dict and state.get('schema') == 'implementaudit.compaction-audit-pending.v1')
        need(type(state.get('session_id')) is str and sha(state['session_id'].encode()) == binding['session_sha256'])
        need(type(state.get('revision')) is int and 0 <= state['revision'] < 2**63)
        assignments = state.get('assignments'); need(type(assignments) is dict)
        found = [value for key,value in assignments.items() if sha(key.encode()) == binding['child_sha256']]
        need(len(found) <= 1)
        result.update(status='PASSIVE_SNAPSHOT',sha256=sha(raw),physical=physical,revision=state['revision'])
        if found:
            assignment = found[0]; need(type(assignment) is dict and type(assignment.get('prepared')) is dict)
            result['assignment_sha256'] = sha(canonical(assignment))
            observed = [value for key,value in assignment['prepared'].items() if sha(key.encode()) == binding['observation_sha256']]
            need(len(observed) <= 1)
            if observed:
                need(type(observed[0]) is dict)
                result['prepared_present'] = True
                if observed[0].get('bound_response') is not None:
                    result['bound_response_sha256'] = sha(canonical(observed[0]['bound_response']))
        return result
    except FileNotFoundError:
        result['status'] = 'ABSENT'
    except (OSError,ValueError,TypeError,KeyError,RecursionError):
        # A malformed/unstable view never becomes a partially valid snapshot.
        result = {**result,'status':'UNAVAILABLE','sha256':None,'physical':None,'revision':None,
                  'assignment_sha256':None,'prepared_present':False,'bound_response_sha256':None}
    return result

def journal_summary(run, expected_binding, expected_child):
    binding_sha = sha(canonical(validate_binding(expected_binding)))
    raw, _ = read_safe(Path(run)/'owner.jsonl',MAX_JOURNAL)
    end = len(raw) if raw.endswith(b'\n') else raw.rfind(b'\n')+1
    tail_bytes = len(raw)-end; need(tail_bytes <= 2048)
    lines = raw[:end].splitlines(keepends=True); need(1 <= len(lines) <= MAX_EVENTS)
    previous = binding_sha; prior_time = -1; counts = {}; currentness = []; active = {}
    inclusive = {}; wait_started = {}; lock_wait_ns = 0; worker_start = None
    prior_bytes = 0; prior_cost = {k:0 for k in JOURNAL_TIMING_FIELDS}
    mutation = {'save_entered':0,'replace_entered':0,'atomic_write_returned':0,'save_returned':0}
    for seq,line in enumerate(lines):
        row = parse(line,2048); validate_event(row)
        need(row['sequence'] == seq and row['previous_sha256'] == previous and row['binding_sha256'] == binding_sha)
        need(row['elapsed_ns'] >= prior_time)
        need(row['journal_cost']['bytes'] == prior_bytes)
        need(all(row['journal_cost'][k] >= prior_cost[k] for k in JOURNAL_TIMING_FIELDS))
        prior_cost = row['journal_cost']; prior_bytes += len(line)
        need((seq == 0) == (row['event'] == 'start'))
        if seq == 0:
            need(row['data']['process'] is not None and row['data']['process'] == expected_child)
            worker_start = row['data']['monotonic_ns']
        if row['event'] == 'finish': need(seq == len(lines)-1 and row['phase'] == 'worker' and row['frame'] == 0)
        phase = row['phase']; event = row['event']; frame = row['frame']
        if event == 'enter':
            need(frame > 0 and frame not in active); active[frame] = (phase,row['elapsed_ns'])
            counts[phase] = counts.get(phase,0)+1
        elif event in ('return','unwind','yield','resume','exception'):
            need(frame in active and active[frame][0] == phase)
            if event in ('return','unwind'):
                inclusive[phase] = inclusive.get(phase,0)+row['elapsed_ns']-active[frame][1]
                active.pop(frame)
                wait_started.pop(frame,None)
        elif event == 'marker':
            need(frame in active)
            counts[phase] = counts.get(phase,0)+1
            if phase == 'lock.wait': wait_started[frame] = row['elapsed_ns']
            if phase == 'lock.acquired':
                need(frame in wait_started)
                lock_wait_ns += row['elapsed_ns']-wait_started.pop(frame)
        if phase == 'mutation.save' and event == 'enter': mutation['save_entered'] += 1
        if phase == 'mutation.replace_enter' and event == 'marker': mutation['replace_entered'] += 1
        if phase == 'mutation.atomic_json' and event == 'return': mutation['atomic_write_returned'] += 1
        if phase == 'mutation.save' and event == 'return': mutation['save_returned'] += 1
        if phase == 'currentness.episode' and event == 'return': currentness.append(row['data']['value_sha256'])
        previous = sha(line); prior_time = row['elapsed_ns']
    last = parse(lines[-1],2048)
    return {'journal_sha256':sha(raw),'journal_bytes':len(raw),'journal_tail_bytes':tail_bytes,'events':len(lines),
            'last_event':last['event'],'last_phase':last['phase'],'last_elapsed_ns':last['elapsed_ns'],
            'counts':counts,'active_phases':sorted(set(phase for phase,_ in active.values())),
            'journal_cost':last['journal_cost'],'journal_cost_scope':COST_SCOPE,
            'journal_cost_uncovered':COST_UNCOVERED,'journal_cost_uncovered_sequence':last['sequence'],
            'phase_cost_scope':PHASE_COST_SCOPE,
            'phase_inclusive_ns':inclusive,'active_since_ns':{phase:min(t for p,t in active.values() if p == phase) for phase,_ in active.values()},
            'lock_wait_completed_ns':lock_wait_ns,'lock_wait_since_ns':min(wait_started.values()) if wait_started else None,
            'worker_start_monotonic_ns':worker_start,
            'mutation':mutation,'episode_reads':len(currentness),
            'episode_first_sha256':currentness[0] if currentness else None,
            'episode_last_sha256':currentness[-1] if currentness else None,
            'episode_reads_agree':len(set(currentness)) <= 1 if currentness else None,
            'currentness':'VALIDATED_AT_RECORDED_READ_ONLY' if currentness else 'UNKNOWN'}

def _supervise(argv, request, run, binding, state_path, *, timeout=WATCHDOG_SECONDS):
    """Private engine; run_observed fixes argv, request, and production timeout."""
    need(type(request) is bytes and 0 < len(request) <= MAX_INPUT)
    validate_binding(binding)
    start = time.monotonic(); child = None; pidfd = None; child_identity = None
    selector = selectors.DefaultSelector(); out = bytearray(); err = bytearray(); reason = 'SUPERVISOR_FAILURE'
    pre = state_snapshot(state_path,binding); eof = False; killed = False; reaped = False
    watchdog_started = None; sampled_wait = wait_sample(None); watchdog_elapsed = 0; watchdog_start_ns = None
    try:
        child = subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
          env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'},close_fds=True)
        watchdog_start_ns = time.monotonic_ns(); watchdog_started = watchdog_start_ns/10**9; deadline = watchdog_started+timeout
        child_identity = process_identity(child.pid)
        need(child_identity is not None and child_identity['ppid'] == os.getpid())
        if hasattr(os,'pidfd_open'): pidfd = os.pidfd_open(child.pid)
        exclusive_json(Path(run)/'supervisor-start.json',{'schema':SCHEMA,'binding_sha256':sha(canonical(binding)),
          'supervisor':process_identity(os.getpid()),'child':child_identity,'pre':pre,'watchdog_seconds':timeout,
          'watchdog_start_monotonic_ns':watchdog_start_ns})
        for stream,role in ((child.stdin,'stdin'),(child.stdout,'stdout'),(child.stderr,'stderr')):
            os.set_blocking(stream.fileno(),False)
            selector.register(stream,selectors.EVENT_WRITE if role == 'stdin' else selectors.EVENT_READ,role)
        written = 0
        while selector.get_map():
            left = deadline-time.monotonic()
            if left <= 0: reason = 'SUBPROCESS_TIMEOUT'; break
            for key,_ in selector.select(min(left,.05)):
                stream = key.fileobj; role = key.data
                if role == 'stdin':
                    try: count = os.write(stream.fileno(),request[written:]); written += count
                    except BrokenPipeError: written = len(request)
                    if written == len(request): selector.unregister(stream); stream.close()
                else:
                    block = os.read(stream.fileno(), min(16384,MAX_OUTPUT+1-len(out)-len(err)))
                    if not block: selector.unregister(stream); stream.close(); continue
                    (out if role == 'stdout' else err).extend(block)
                    if len(out)+len(err) > MAX_OUTPUT: reason = 'OUTPUT_BOUND'; break
            if reason == 'OUTPUT_BOUND': break
        else:
            eof = True
            left = deadline-time.monotonic()
            try: child.wait(timeout=max(0,left)); reaped = True; reason = 'EXITED'
            except subprocess.TimeoutExpired: reason = 'SUBPROCESS_TIMEOUT'
    except (OSError,ValueError,TypeError):
        reason = 'SUPERVISOR_FAILURE'
    finally:
        watchdog_elapsed = int((time.monotonic()-watchdog_started)*10**9) if watchdog_started is not None else 0
        sampled_wait = wait_sample(child_identity)
        if child is not None:
            if child.poll() is None:
                try:
                    if pidfd is not None and hasattr(signal,'pidfd_send_signal'):
                        signal.pidfd_send_signal(pidfd,signal.SIGKILL); killed = True
                    elif child_identity is not None and process_identity(child.pid) == child_identity:
                        child.kill(); killed = True
                except (OSError,ValueError): pass
            try: child.wait(timeout=CLEANUP_SECONDS); reaped = True
            except subprocess.TimeoutExpired: pass
            for stream in (child.stdin,child.stdout,child.stderr):
                if stream is not None:
                    try: stream.close()
                    except OSError: pass
        selector.close()
        if pidfd is not None: os.close(pidfd)
        post = state_snapshot(state_path,binding) if reaped else {**pre,'status':'NOT_READ_CHILD_UNREAPED','sha256':None,'physical':None,'revision':None,'assignment_sha256':None,'prepared_present':False,'bound_response_sha256':None}
        owner = None; journal_status = 'UNAVAILABLE'
        if reaped and child_identity is not None:
            try: owner = journal_summary(run,binding,child_identity); journal_status = 'VALIDATED'
            except (OSError,ValueError,TypeError,KeyError): journal_status = 'UNAVAILABLE_OR_INVALID'
        result = {'schema':SCHEMA,'binding':binding,'binding_sha256':sha(canonical(binding)),
          'reason':reason,'watchdog_seconds':timeout,'elapsed_ns':int((time.monotonic()-start)*10**9),
          'watchdog_elapsed_ns':watchdog_elapsed,'watchdog_start_monotonic_ns':watchdog_start_ns,'wait_sample':sampled_wait,
          'supervisor':process_identity(os.getpid()),'child':child_identity,
          'child_exit_code':child.returncode if child is not None and reaped else None,
          'direct_child_reaped':reaped,'kill_sent':killed,'output_eof':eof,
          'stdout_bytes':len(out),'stderr_bytes':len(err),'stdout_sha256':sha(out),'stderr_sha256':sha(err),
          'journal_status':journal_status,'owner':owner,'pre':pre,'post':post,
          'effect':'UNKNOWN','canonical_currentness':'UNKNOWN','descendant_provider_closure':'NOT_ESTABLISHED',
          'authority':'NONE'}
        # A visible file difference is observation, never assignment of cause or
        # retrospective acceptance; actual owner mutation milestones stay separate.
        if pre['sha256'] is not None and post['sha256'] is not None:
            result['effect'] = 'PASSIVE_STATE_CHANGED' if pre['sha256'] != post['sha256'] else 'PASSIVE_STATE_SAME'
        try:
            validate_result(result,expected_binding=binding,production=False)
            exclusive_json(Path(run)/'result.json',result)
        except (OSError,ValueError,TypeError):
            if reason == 'SUBPROCESS_TIMEOUT':
                raise subprocess.TimeoutExpired(['observe-child'],timeout) from None
            raise ObservationRefusal() from None
    return subprocess.CompletedProcess(['observe-child'],result['child_exit_code'],bytes(out),bytes(err)), result

def validate_snapshot(value):
    need(type(value) is dict and set(value) == {'status','sha256','physical','revision','assignment_sha256','prepared_present','bound_response_sha256','authority','currentness'})
    need(value['status'] in ('PASSIVE_SNAPSHOT','UNAVAILABLE','ABSENT','NOT_READ_CHILD_UNREAPED'))
    need(value['authority'] == 'NONE' and value['currentness'] == 'NOT_EVALUATED' and type(value['prepared_present']) is bool)
    for k in ('sha256','assignment_sha256','bound_response_sha256'):
        need(value[k] is None or (type(value[k]) is str and HEX.fullmatch(value[k])))
    if value['status'] == 'PASSIVE_SNAPSHOT':
        need(value['sha256'] is not None and type(value['revision']) is int and 0 <= value['revision'] < 2**63)
        p = value['physical']; need(type(p) is dict and set(p) == {'device','inode','bytes','mtime_ns','ctime_ns'})
        need(all(type(v) is int and v >= 0 for v in p.values()) and 0 < p['bytes'] <= MAX_STATE)
    else:
        need(all(value[k] is None for k in ('sha256','physical','revision','assignment_sha256','bound_response_sha256')) and not value['prepared_present'])

def validate_result(value, *, expected_binding, production=True):
    expected = {'schema','binding','binding_sha256','reason','watchdog_seconds','elapsed_ns','watchdog_elapsed_ns','watchdog_start_monotonic_ns','wait_sample','supervisor','child',
      'child_exit_code','direct_child_reaped','kill_sent','output_eof','stdout_bytes','stderr_bytes','stdout_sha256','stderr_sha256',
      'journal_status','owner','pre','post','effect','canonical_currentness','descendant_provider_closure','authority'}
    need(type(value) is dict and set(value) == expected and len(canonical(value)) <= MAX_PUBLIC)
    validate_binding(expected_binding)
    need(value['schema'] == SCHEMA and value['binding'] == expected_binding and value['binding_sha256'] == sha(canonical(expected_binding)))
    need(value['reason'] in ('EXITED','SUBPROCESS_TIMEOUT','OUTPUT_BOUND','SUPERVISOR_FAILURE'))
    need(type(value['watchdog_seconds']) in (int,float) and math.isfinite(value['watchdog_seconds']) and 0 < value['watchdog_seconds'] <= WATCHDOG_SECONDS)
    if production: need(value['watchdog_seconds'] == WATCHDOG_SECONDS)
    need(type(value['elapsed_ns']) is int and 0 <= value['elapsed_ns'] < 3600*10**9)
    need(type(value['watchdog_elapsed_ns']) is int and 0 <= value['watchdog_elapsed_ns'] <= value['elapsed_ns'])
    need(value['watchdog_start_monotonic_ns'] is None or (type(value['watchdog_start_monotonic_ns']) is int and 0 < value['watchdog_start_monotonic_ns'] < 2**63))
    sample = value['wait_sample']
    need(type(sample) is dict and set(sample) == {'status','run_state','wait_class'})
    need(sample['status'] in ('UNAVAILABLE','SAME_CHILD_AT_READ') and sample['run_state'] in ('UNKNOWN','R','S','D','Z','T','t','I','X','P'))
    need(sample['wait_class'] in ('UNKNOWN','FILE_LOCK','PIPE','FUTEX','IO','POLL','SLEEP','RUNNING_OR_UNAVAILABLE','OTHER'))
    if sample['status'] == 'UNAVAILABLE': need(sample['run_state'] == sample['wait_class'] == 'UNKNOWN')
    need(process_valid(value['supervisor']) and process_valid(value['child']))
    need(value['supervisor'] is not None)
    if value['child'] is not None: need(value['child']['ppid'] == value['supervisor']['pid'])
    for k in ('direct_child_reaped','kill_sent','output_eof'): need(type(value[k]) is bool)
    need((value['child_exit_code'] is None) == (not value['direct_child_reaped']))
    need(value['child_exit_code'] is None or (type(value['child_exit_code']) is int and -128 <= value['child_exit_code'] <= 255))
    for k in ('stdout_bytes','stderr_bytes'): need(type(value[k]) is int and 0 <= value[k] <= MAX_OUTPUT+1)
    need(value['stdout_bytes']+value['stderr_bytes'] <= MAX_OUTPUT+1)
    for k in ('stdout_sha256','stderr_sha256'): need(type(value[k]) is str and HEX.fullmatch(value[k]))
    need(value['journal_status'] in ('VALIDATED','UNAVAILABLE','UNAVAILABLE_OR_INVALID'))
    need((value['owner'] is not None) == (value['journal_status'] == 'VALIDATED'))
    if value['owner'] is not None:
        summary = value['owner']; need(type(summary) is dict and set(summary) == {'journal_sha256','journal_bytes','journal_tail_bytes','events','last_event','last_phase','last_elapsed_ns','counts','active_phases','phase_inclusive_ns','active_since_ns','lock_wait_completed_ns','lock_wait_since_ns','worker_start_monotonic_ns','mutation','episode_reads','episode_first_sha256','episode_last_sha256','episode_reads_agree','currentness','journal_cost','journal_cost_scope','journal_cost_uncovered','journal_cost_uncovered_sequence','phase_cost_scope'})
        need(type(summary['journal_sha256']) is str and HEX.fullmatch(summary['journal_sha256']))
        need(type(summary['journal_bytes']) is int and 0 < summary['journal_bytes'] <= MAX_JOURNAL)
        need(type(summary['journal_tail_bytes']) is int and 0 <= summary['journal_tail_bytes'] <= 2048)
        need(type(summary['events']) is int and 1 <= summary['events'] <= MAX_EVENTS)
        need(summary['last_event'] in EVENTS and summary['last_phase'] in PHASES)
        need(type(summary['last_elapsed_ns']) is int and 0 <= summary['last_elapsed_ns'] <= value['elapsed_ns'])
        validate_cost(summary['journal_cost'],summary['events']-1,summary['last_elapsed_ns'])
        need(summary['journal_cost']['bytes'] < summary['journal_bytes']-summary['journal_tail_bytes'])
        need(summary['journal_cost_scope'] == COST_SCOPE and summary['journal_cost_uncovered'] == COST_UNCOVERED
          and summary['phase_cost_scope'] == PHASE_COST_SCOPE
          and type(summary['journal_cost_uncovered_sequence']) is int and summary['journal_cost_uncovered_sequence'] == summary['events']-1)
        need(type(summary['counts']) is dict and set(summary['counts']) <= PHASES and all(type(v) is int and 0 < v <= MAX_EVENTS for v in summary['counts'].values()))
        need(type(summary['active_phases']) is list and all(p in PHASES for p in summary['active_phases']))
        for field in ('phase_inclusive_ns','active_since_ns'):
            need(type(summary[field]) is dict and set(summary[field]) <= PHASES and all(type(v) is int and 0 <= v <= MAX_EVENTS*summary['last_elapsed_ns'] for v in summary[field].values()))
        need(set(summary['active_since_ns']) == set(summary['active_phases']))
        need(type(summary['lock_wait_completed_ns']) is int and 0 <= summary['lock_wait_completed_ns'] <= MAX_EVENTS*summary['last_elapsed_ns'])
        need(summary['lock_wait_since_ns'] is None or (type(summary['lock_wait_since_ns']) is int and 0 <= summary['lock_wait_since_ns'] <= summary['last_elapsed_ns']))
        need(type(summary['worker_start_monotonic_ns']) is int and 0 < summary['worker_start_monotonic_ns'] < 2**63)
        need(type(summary['mutation']) is dict and set(summary['mutation']) == {'save_entered','replace_entered','atomic_write_returned','save_returned'} and all(type(v) is int and 0 <= v <= MAX_EVENTS for v in summary['mutation'].values()))
        need(type(summary['episode_reads']) is int and 0 <= summary['episode_reads'] <= MAX_EVENTS)
        for k in ('episode_first_sha256','episode_last_sha256'): need(summary[k] is None or (type(summary[k]) is str and HEX.fullmatch(summary[k])))
        if summary['episode_reads']:
            need(type(summary['episode_reads_agree']) is bool and summary['episode_first_sha256'] is not None and summary['episode_last_sha256'] is not None and summary['currentness'] == 'VALIDATED_AT_RECORDED_READ_ONLY')
        else: need(summary['episode_reads_agree'] is None and summary['episode_first_sha256'] is None and summary['episode_last_sha256'] is None and summary['currentness'] == 'UNKNOWN')
    validate_snapshot(value['pre']); validate_snapshot(value['post'])
    wanted = 'UNKNOWN'
    if value['pre']['sha256'] is not None and value['post']['sha256'] is not None:
        wanted = 'PASSIVE_STATE_SAME' if value['pre']['sha256'] == value['post']['sha256'] else 'PASSIVE_STATE_CHANGED'
    need(value['effect'] == wanted and value['canonical_currentness'] == 'UNKNOWN'
      and value['descendant_provider_closure'] == 'NOT_ESTABLISHED' and value['authority'] == 'NONE')
    if value['reason'] == 'EXITED': need(value['direct_child_reaped'] and value['output_eof'])
    return value

def read_result(run, expected_binding, *, production=True):
    run = safe_directory(run,private=True)
    need(run.name == sha(canonical(validate_binding(expected_binding))))
    binding = parse(read_safe(run/'binding.json',MAX_PUBLIC)[0],MAX_PUBLIC)
    need(binding == expected_binding)
    result = parse(read_safe(run/'result.json',MAX_PUBLIC)[0],MAX_PUBLIC)
    validate_result(result,expected_binding=expected_binding,production=production)
    if result['journal_status'] == 'VALIDATED':
        need(journal_summary(run,expected_binding,result['child']) == result['owner'])
    return result

def run_observed(argv, request, *, binding_fields, code_pins):
    need(os.name == 'posix' and sys.platform == 'linux')
    need(type(argv) is list and len(argv) == 12 and argv[1:4] == ['-I','-S','-B'] and argv[5] == '--store'
      and argv[7] == '--session' and argv[9] == '--owner-id' and argv[11] == 'observe-child')
    pending = Path(argv[4]); need(pending.name == 'compaction-audit-pending.py' and pending.parent == Path(__file__).resolve().parent)
    value = parse(request,MAX_INPUT)
    need(type(value) is dict and value.get('phase') in ('deliver','bind') and type(value.get('child_id')) is str and type(value.get('observation_id')) is str)
    fields = dict(binding_fields)
    fields.update(schema=SCHEMA,invocation_nonce=os.urandom(16).hex(),authority='NONE',preflight='ACTUAL_PENDING_CALL_VALIDATED',
      request_sha256=sha(request),session_sha256=sha(argv[8].encode()),child_sha256=sha(value['child_id'].encode()),
      observation_sha256=sha(value['observation_id'].encode()),assignment_code_sha256=sha(canonical(code_pins)))
    validate_binding(fields); need(fields['operation'] == value['phase'].upper())
    source_contract(pending.parent,code_pins)
    store = safe_directory(argv[6]); run = make_run(store,fields,code_pins)
    worker_argv = argv[:4]+[str(Path(__file__).resolve()),'--pending-worker',str(run)]+argv[4:]
    state_file = store/'compaction-audits-v1'/sha(argv[8].encode())/'pending.json'
    completed, result = _supervise(worker_argv,request,run,fields,state_file,timeout=WATCHDOG_SECONDS)
    if result['reason'] == 'SUBPROCESS_TIMEOUT':
        raise subprocess.TimeoutExpired(['observe-child'],WATCHDOG_SECONDS)
    need(result['reason'] == 'EXITED' and result['journal_status'] == 'VALIDATED')
    need(result['owner']['last_event'] == 'finish' and result['owner']['journal_tail_bytes'] == 0)
    return completed

def main():
    # Original owner argv is passed without logging or storing its values.
    args = sys.argv[1:]
    need(len(args) == 10 and args[0] == '--pending-worker')
    run = safe_directory(args[1],private=True); pending = Path(args[2])
    need(pending.name == 'compaction-audit-pending.py' and pending.parent == Path(__file__).resolve().parent
      and args[3] == '--store' and args[5] == '--session' and args[7] == '--owner-id' and args[9] == 'observe-child')
    binding = parse(read_safe(run/'binding.json',MAX_PUBLIC)[0],MAX_PUBLIC); validate_binding(binding)
    need(sha(args[6].encode()) == binding['session_sha256'])
    need(run.parent == safe_directory(args[4])/DIRECTORY)
    code_pins = parse(read_safe(run/'code-pins.json',MAX_PUBLIC)[0],MAX_PUBLIC)
    need(sha(canonical(code_pins)) == binding['assignment_code_sha256'])
    journal = Journal(run,binding)
    try:
        trace = Trace(journal,pending.parent,code_pins)
        request = sys.stdin.buffer.read(MAX_INPUT+1)
        need(sha(request) == binding['request_sha256'])
        value = parse(request,MAX_INPUT)
        need(sha(value['child_id'].encode()) == binding['child_sha256']
          and sha(value['observation_id'].encode()) == binding['observation_sha256']
          and value['phase'].upper() == binding['operation'])
        sys.stdin = io.TextIOWrapper(io.BytesIO(request),encoding='utf-8')
        sys.argv = args[2:]
        sys.settrace(trace)
        try:
            runpy.run_path(str(pending),run_name='__main__')
        except SystemExit:
            sys.settrace(None); journal.emit('finish','worker',0); raise
        finally: sys.settrace(None)
    except ObservationRefusal:
        sys.settrace(None)
        # Do not replace a consumed native mutation with success; the supervisor
        # retains the bounded prefix and refuses this operation.
        raise SystemExit(74) from None
    finally: journal.close()

if __name__ == '__main__':
    try: main()
    except (OSError,ValueError,TypeError,KeyError): raise SystemExit(74) from None
