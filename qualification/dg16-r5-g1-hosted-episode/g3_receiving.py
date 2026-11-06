#!/usr/bin/env python3
"""Prospective DG16 G3 receiving in the selected G1 job's actual custody.

No saved graph, JSON result, or root decision grants native authority. Native
observations come from the unchanged maintained compiler and fresh owner in the
same checkout. The root decision consumes only the two declared component
returns. The separate final root decision can receive exact original scopes;
whole-DG16, full-G2 transfer, and parked sibling awards are never automatic.
The only standalone entry point is the bounded, read-only scope receiver.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import signal
import stat
import sys
import time
import types
import urllib.error
import urllib.request

SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
SOURCE_PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'
SOURCE_FILES, SOURCE_BYTES = 1755, 165855954
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
COMPILER_SHA = '3649a8dc856e29ce11b6daa5861351cc1c21bf9c7a9b4f5a2ddde12108d8581f'
COMPILER_BYTES = 262144
OWNER = 'skills/implementaudit/scripts/claim-run.sh'
SCOPE_SHA = 'ec8a371d9b13686883d9f15034bdd25202893b855b63d53f39eb03cda41cd668'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
JOB_BRANCH = 'pro/dg16-r5-g1-hosted-episode-01-20261105'
CONTROL_BRANCH = 'pro/dg16-r5-g3-control-01-20261105'
CONTROL_PATH = 'qualification/dg16-r5-g3/ROOT_DECISION.json'
FINAL_CONTROL_PATH = 'qualification/dg16-r5-g3/ORIGINAL_DECISION.json'
ADVERSE_SHA = 'a9ba4151c65beb39185f22240be4e7ba6594016a60e1173f862e71fc1db97f71'
ROOT, PHASE, JOIN = 'R5_ROOT', 'DG16_CURRENT', 'DG16_COMPONENT_JOIN'
PAIR, SCOPE = 'G1_ORIGINAL_PAIR', 'HOST_SCOPE_RECEIVING'
SELECTED = [PAIR, SCOPE]
ORIGINAL = 'DG16_48_DG17_95_DG18_14_ORIGINAL157'
CONDITION = 'ACTUAL_ROOT_CONSUMPTION_OF_BOTH_COMPONENT_RETURNS'
BEFORE = 'WAITING_FOR_G1_AND_HOST_SCOPE'
AFTER = 'SCOPED_RETURNS_RETAINED_ORIGINAL_CELL_OPEN'
DOCS = ('STATE.md', 'ROADMAP.md', 'phases/phase-1.md')
FENCE = re.compile(rb'(?m)^```implementaudit-work-graph\n.*?\n```[ \t]*$', re.S)
FILE_LIMIT, TOTAL_LIMIT, ENTRY_LIMIT, DEPTH_LIMIT = 16*1024**2, 64*1024**2, 4096, 16
CANONICAL_LIMIT, CANONICAL_TOTAL = 96*1024, 256*1024
PUBLIC_LIMIT, REQUEST_LIMIT, DECISION_LIMIT = 24576, 8192, 8192
HOLD_SECONDS, POLL_SECONDS, POLL_COUNT, HTTP_SECONDS = 600, 10, 60, 8
RESUME_RESERVE_SECONDS = 180
PHASES = ('AUTHOR', 'INPUTS', 'SELECT', 'SCOPE_PROCESS', 'INPUTS_RECHECK',
          'UPSTREAM_RECEIVE', 'JOIN', 'HOLD_READY', 'CONTROL_READ', 'RESERVE',
          'ROOT_CONSUME', 'INVALIDATE', 'CANONICAL_UPDATE', 'RESUME',
          'REDERIVE', 'STALE_RETURN', 'FINAL_REQUEST', 'FINAL_CONTROL_READ', 'FINAL_DECISION', 'COMPLETE')
MILESTONES = ('AUTHORED', 'SELECTED', 'SCOPE_RETURNED', 'INPUTS_RECHECKED',
              'G1_RECEIVED', 'JOIN_READY', 'REQUEST_RETAINED', 'ROOT_DECISION_READ',
              'CONSUMPTION_RESERVED', 'ROOT_CONSUMED', 'INVALIDATED',
              'CANONICAL_UPDATED', 'NEW_CURRENTNESS', 'FRONTIER_RECOMPUTED',
              'STALE_RETURN_REFUSED', 'FINAL_REQUEST_RETAINED', 'ORIGINAL_DECISION_RETAINED')
ORIGINAL_IDS = ('R35-Q06', 'R35-L01', 'R35-L02', 'R35-L03', 'R35-L04', 'R35-L05', 'R35-L06', 'R35-L07')
ORIGINAL_SCOPES = (
    'NATIVE_BOUNDED_FRESH_GOVERNED_EPISODE', 'MATERIAL_RETURN_ANCESTRY_CURRENT_NATIVE_CAMPAIGN',
    'PREPARATION_SELECTION_WITH_BLOCKED_ADMISSION_EFFECT', 'FOUR_DIRECTIONS_PARTIAL_JOIN_RECONSIDERATION',
    'ACTUAL_NATURAL_TRANSITION_AND_CONSUMED_USEFUL_PREPARATION',
    'HELD_OUT_INERT_NEGATIVES_WITH_EXACT_SOURCE_APPLICABILITY',
    'NATIVE_CURRENTNESS_AND_BOUNDED_SELECTION_BLOCKS', 'SCOPED_TRIAD_GUARDS_WITH_STRONGER_CLAIMS_SEPARATE')
DISPOSITIONS = ('ACCEPTED_AT_DECLARED_SCOPE', 'PARTIAL_SCOPE_ONLY', 'NOT_RECEIVED')
RESIDUALS = ('NONE_AT_DECLARED_SCOPE', 'ORIGINAL_CONJUNCTION_NOT_ESTABLISHED',
             'INDEPENDENT_REVIEW_APPLICABILITY_NOT_ESTABLISHED', 'GLOBAL_LIVENESS_UNPROVED',
             'RETIREMENT_OR_TRANSFER_UNPERFORMED', 'AUTHORITATIVE_V041_ADMISSION_PENDING')
FINAL_PROOF_KEYS = ('g1_receiving', 'g1_preboundary_inputs', 'scope_receiving', 'initial_native', 'dispatch', 'transition', 'join',
    'root_consumption', 'recursive_records', 'final_native', 'final_transition', 'stale_return',
    'missing_return', 'negative_applicability', 'module')


class Refusal(Exception):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def acquisition_encode(value):
    # Exact selected C5 owner spelling; the public projection uses ASCII above.
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')+b'\n'


def parse(raw, maximum=FILE_LIMIT):
    need(type(raw) is bytes and len(raw) <= maximum, 'JSON_BYTE_BOUND')
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def exact(value, fields, code='CLOSED_SCHEMA_REFUSED'):
    need(type(value) is dict and set(value) == set(fields), code)


def digest(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'DIGEST_SHAPE')
    return value


def integer(value, low, high):
    need(type(value) is int and low <= value <= high, 'INTEGER_BOUND')
    return value


def identity(s):
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns, s.st_uid, s.st_gid]


def read_file(path, maximum=FILE_LIMIT):
    path = Path(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and 0 <= before.st_size <= maximum, 'ORDINARY_FILE_BOUND')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd)) == identity(before) and not os.listxattr(fd), 'FILE_OPEN_CHANGED')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(maximum+1)
        need(len(raw) == before.st_size and identity(os.fstat(fd)) == identity(before)
             and identity(path.lstat()) == identity(before), 'FILE_READ_CHANGED')
        return raw
    finally:
        os.close(fd)


def write_once(path, raw, maximum=FILE_LIMIT):
    need(type(raw) is bytes and len(raw) <= maximum, 'PRIVATE_OUTPUT_BOUND')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(fd)
        os.fchmod(fd, 0o400)
    finally:
        os.close(fd)
    need(read_file(path, maximum) == raw, 'PRIVATE_OUTPUT_READBACK')
    return sha(raw)


def atomic_checkpoint(path, value):
    raw = encode(value)
    need(len(raw) <= 4096, 'DIAGNOSTIC_BOUND')
    tmp = Path(str(path)+'.next')
    write_once(tmp, raw, 4096)
    os.replace(tmp, path)


class Diagnostics:
    def __init__(self, private):
        self.path = Path(private)/'G3_EFFECT_STATE.json'
        self.value = dict(schema='dg16.g3-diagnostic.v1', authority='NONE', phase='AUTHOR',
                          completed=[], failed=False, failure_code=None, exception_category=None,
                          original_awards=0, consumption_reserved=False, root_consumed=False,
                          continuity_updated=False, native_frontier_recomputed=False,
                          root_original_disposition=None, root_original_ids=[],
                          effects={key:'NOT_STARTED' for key in ('reservation', 'root_consumption',
                            'invalidation', 'canonical_update', 'resume_currentness', 'frontier_recomputation',
                            'original_receiving')})
        if self.path.exists():
            self.value = validate_effect_state(read_file(self.path, 4096))
        atomic_checkpoint(self.path, self.value)

    def phase(self, name):
        need(name in PHASES, 'DIAGNOSTIC_PHASE')
        self.value['phase'] = name
        atomic_checkpoint(self.path, self.value)

    def done(self, name):
        need(name in MILESTONES and name not in self.value['completed'], 'DIAGNOSTIC_MILESTONE')
        self.value['completed'].append(name)
        for key, mark in (('consumption_reserved', 'CONSUMPTION_RESERVED'),
                          ('root_consumed', 'ROOT_CONSUMED'),
                          ('continuity_updated', 'NEW_CURRENTNESS'),
                          ('native_frontier_recomputed', 'FRONTIER_RECOMPUTED')):
            if name == mark:
                self.value[key] = True
        related = {'CONSUMPTION_RESERVED':'reservation', 'ROOT_CONSUMED':'root_consumption',
                   'INVALIDATED':'invalidation', 'CANONICAL_UPDATED':'canonical_update',
                   'NEW_CURRENTNESS':'resume_currentness', 'FRONTIER_RECOMPUTED':'frontier_recomputation',
                   'ORIGINAL_DECISION_RETAINED':'original_receiving'}
        if name in related:
            self.value['effects'][related[name]] = 'COMPLETED'
        atomic_checkpoint(self.path, self.value)

    def start(self, name):
        need(name in self.value['effects'] and self.value['effects'][name] == 'NOT_STARTED', 'EFFECT_ALREADY_STARTED')
        self.value['effects'][name] = 'STARTED_OUTCOME_UNKNOWN'
        atomic_checkpoint(self.path, self.value)

    def fail(self, exc):
        # No raw exception string, path, controller ID, traceback or provider
        # payload crosses this diagnostic projection.
        self.value.update(failed=True, failure_code=(str(exc) if isinstance(exc, Refusal)
                          and str(exc) in REFUSAL_CODES else 'UNCLASSIFIED_EXCEPTION'),
                          exception_category=(type(exc).__name__ if type(exc).__name__ in
                            ('Refusal', 'OSError', 'FileNotFoundError', 'PermissionError', 'ValueError',
                             'TypeError', 'KeyError', 'WorkGraphError', 'KeyboardInterrupt', 'SystemExit') else 'OTHER'))
        atomic_checkpoint(self.path, self.value)


def guarded(function):
    def call(api):
        d = Diagnostics(api['private'])
        try:
            return function(api, d)
        except BaseException as exc:
            d.fail(exc)
            raise
    return call


def context(api):
    need(os.getuid() == os.geteuid() == 0 and os.getgid() == os.getegid() == 0, 'ACTUAL_ROOT_CUSTODY_REQUIRED')
    run = os.environ.get('GITHUB_RUN_ID')
    need(type(run) is str and re.fullmatch('[1-9][0-9]{5,19}', run), 'RUN_ID_SHAPE')
    need(os.environ.get('GITHUB_RUN_ATTEMPT') == '1'
         and os.environ.get('GITHUB_REPOSITORY') == REPOSITORY
         and os.environ.get('GITHUB_REF') == 'refs/heads/'+JOB_BRANCH, 'FRESH_JOB_CONTEXT_REQUIRED')
    need(type(api.get('deadline_monotonic')) in (int, float)
         and 0 < api['deadline_monotonic']-time.monotonic() <= 1800, 'ENCLOSING_DEADLINE')
    source, private = Path(api['source']).absolute(), Path(api['private']).absolute()
    need(not private.is_relative_to(source) and not source.is_symlink() and not private.is_symlink(), 'PRIVATE_SOURCE_SEPARATION')
    for root in (source, private):
        info = root.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == info.st_gid == 0
             and not info.st_mode & 0o022, 'ACTUAL_OWNED_ROOT_REQUIRED')
    run_root = api['run_root']
    need(type(run_root) is str and re.fullmatch(r'\.IMPLEMENTAUDIT/runs/r5-g1-hosted-[A-Za-z0-9]{6}', run_root), 'FRESH_RUN_ROOT_REQUIRED')
    need(api['controller'] == 'r5-g1-hosted-'+run+'-a1', 'FRESH_CONTROLLER_REQUIRED')
    return source, private, source/run_root, run


def scope_basis():
    raw = read_file(Path(__file__).with_name('ORIGINAL_SCOPE.json'), 8192)
    need(sha(raw) == SCOPE_SHA, 'ORIGINAL_SCOPE_PIN')
    value = parse(raw)
    need(value['original_population'] == dict(DG16=48, DG17=95, DG18=14, total=157)
         and value['new_original_awards'] == 0, 'ORIGINAL_POPULATION')
    for cell, size in (('DG16', 48), ('DG17', 95), ('DG18', 14)):
        ids = value['original_ids'][cell]
        need(type(ids) is list and len(ids) == size and len(set(ids)) == size
             and all(type(x) is str and 3 <= len(x) <= 64 and re.fullmatch(r'[A-Z0-9][A-Z0-9_-]*(?:/[A-Z0-9][A-Z0-9_-]*)*', x) for x in ids), 'ORIGINAL_ID_POPULATION')
    return raw, value


def node(name, parent, kind='TASK', *, requires=(), effect='READ_ONLY', permitted=True,
         reads=(), writes=(), future=None, state='OPEN', evidence=None, rank=0):
    return dict(id=name, parent=parent, kind=kind, state=state, requires=list(requires), optional=[],
        reads=list(reads), writes=list(writes), resources=[], acceptance=[], authority=[],
        effect=effect, authorization='PERMITTED' if permitted else 'MISSING', independence='KNOWN',
        resource_demand=1, rank=rank, logical_delivery=None, done_evidence=evidence,
        future_consumer=None if future is None else dict(node=future, condition=CONDITION if future == JOIN else
            'OWNER_REACTIVATION_AND_APPLICABLE_ORIGINAL_QUALIFICATION'),
        independent_results=False, route_scopes=[], invalidators=[],
        context=dict(locality='GOVERNOR' if kind in ('PLAN', 'PHASE', 'JOIN') else 'CHILD',
            governor_cost=3, child_cost=1, return_cost=1, useful_value=10))


def declarations(run, completion=None):
    completion = {} if completion is None else completion
    historical = scope_basis()[1]['finite_g2_input']['determination_sha256']
    nodes = [
        node(ROOT, None, 'PLAN'), node(PHASE, ROOT, 'PHASE'),
        node('DG17_PARKED', ROOT, 'PHASE', permitted=False, future='TRIAD_RECEIVING'),
        node('DG18_PARKED', ROOT, 'PHASE', permitted=False, future='TRIAD_RECEIVING'),
        node('FINITE_G2_HISTORY', PHASE, state='DONE', evidence=historical),
        node(PAIR, PHASE, effect='PREPARATION', reads=('path:G1_INPUTS.json', 'path:POLICY.json'),
             writes=('semantic:g1-private-owned-operation',), future=JOIN, rank=20),
        node(SCOPE, PHASE, requires=('FINITE_G2_HISTORY',), effect='PREPARATION', reads=('path:ORIGINAL_SCOPE.json', 'path:G1_INPUTS.json',
             'path:POLICY.json', 'path:SCOPE_READER.py', 'path:COMPILER_READER.py', 'path:ADVERSE_APPLICABILITY.json'), writes=('semantic:host-scope-receiving-output',),
             future=JOIN, rank=10),
        node(JOIN, PHASE, 'JOIN', requires=SELECTED),
        node('FULL_G2_UNPERFORMED', PHASE, effect='PREPARATION', permitted=False,
             future='DG16_ORIGINAL_RECEIVING'),
        node('DG16_ORIGINAL_RECEIVING', PHASE, 'JOIN', requires=(JOIN, 'FULL_G2_UNPERFORMED'), permitted=False),
        node('DG17_ORIGINAL_RECEIVING', 'DG17_PARKED', permitted=False,
             effect='PREPARATION', future='TRIAD_RECEIVING'),
        node('DG18_ORIGINAL_RECEIVING', 'DG18_PARKED', permitted=False,
             effect='PREPARATION', future='TRIAD_RECEIVING'),
        node('TRIAD_RECEIVING', ROOT, 'JOIN', requires=('DG16_ORIGINAL_RECEIVING',
             'DG17_ORIGINAL_RECEIVING', 'DG18_ORIGINAL_RECEIVING'), permitted=False),
        node('RESERVED_ORIGINAL_ADOPTION', ROOT, effect='EXTERNAL', requires=('TRIAD_RECEIVING',), permitted=False),
    ]
    need(set(completion) <= {PAIR, SCOPE, JOIN}, 'ANCESTOR_CREDIT_REFUSED')
    for item in nodes:
        if item['id'] == 'FULL_G2_UNPERFORMED':
            item['authority'] = ['scope:this-host-episode-has-no-full-g2-dispatch-grant']
            item['reads'] = ['semantic:parallel-full-g2-obligation-remains-active']
            item['future_consumer']['condition'] = 'RECEIVE_ACTUAL_PARALLEL_FULL_G2_AT_APPLICABLE_SOURCE'
        if item['id'] in completion:
            item.update(state='DONE', done_evidence=digest(completion[item['id']]))
    event = dict(id='g3-hosted-'+run+('-root-join' if completion else '-prospective-selection'),
                 kind='JOIN' if completion else 'REDERIVE', subject=JOIN if completion else PAIR)
    state = dict(schema='implementaudit.native-state.v1', campaign='R5_G3_FRESH_HOST_'+run,
        root=ROOT, original_scope=ORIGINAL, nodes=[n['id'] for n in nodes], event=event,
        context=dict(host_capacity=2, operator_ceiling=2, reserve=0, route_facts=[], outstanding_deliveries=[]))
    roadmap = dict(schema='implementaudit.native-roadmap.v1', phases=[PHASE, 'DG17_PARKED', 'DG18_PARKED'])
    return dict(zip(DOCS, (state, roadmap, dict(schema='implementaudit.native-spec.v1', nodes=nodes))))


def render_fences(run_root, values, initial):
    result = {}
    for name in DOCS:
        raw = read_file(run_root/name, CANONICAL_LIMIT)
        count = len(FENCE.findall(raw))
        need(count == (0 if initial else 1) and raw.count(b'```implementaudit-work-graph') == count,
             'CANONICAL_FENCE_POPULATION')
        fenced = b'```implementaudit-work-graph\n'+encode(values[name]).rstrip(b'\n')+b'\n```'
        result[name] = raw.rstrip(b'\n')+b'\n\n'+fenced+b'\n' if initial else FENCE.sub(lambda _: fenced, raw)
        need(len(result[name]) <= CANONICAL_LIMIT, 'CANONICAL_FILE_BOUND')
    need(sum(map(len, result.values())) <= CANONICAL_TOTAL, 'CANONICAL_TOTAL_BOUND')
    return result


def update_existing(path, before, after):
    # Keep each owner-created file and mode; never introduce a symlink, hardlink
    # or new canonical population. Currentness is deliberately invalidated first
    # for post-activation writes. Initialization has not activated yet.
    need(read_file(path, CANONICAL_LIMIT) == before, 'CANONICAL_PREIMAGE_CHANGED')
    old = path.lstat()
    fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd)) == identity(old), 'CANONICAL_OPEN_CHANGED')
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(after)
            stream.truncate()
            stream.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    need(read_file(path, CANONICAL_LIMIT) == after and path.lstat().st_ino == old.st_ino
         and path.lstat().st_mode == old.st_mode, 'CANONICAL_READBACK')


@guarded
def author_checkpoint(api, diagnostic):
    source, private, run_root, run = context(api)
    diagnostic.phase('AUTHOR')
    need(api['receipt'] is None, 'PREACTIVATION_ONLY')
    docs = render_fences(run_root, declarations(run), True)
    before = {name: read_file(run_root/name, CANONICAL_LIMIT) for name in DOCS}
    write_once(private/'G3_INITIAL_CANONICAL.json', encode({name:sha(raw) for name,raw in before.items()}))
    for name in DOCS:
        update_existing(run_root/name, before[name], docs[name])
    diagnostic.done('AUTHORED')
    return dict(status='PREACTIVATION_NATIVE_DECLARATIONS_AUTHORED', source_commit=SOURCE_COMMIT,
                source_tree=SOURCE_TREE, original_awards=0)


def compiler_file(path):
    raw = read_file(path, COMPILER_BYTES)
    need(len(raw) == COMPILER_BYTES and sha(raw) == COMPILER_SHA, 'COMPILER_PIN')
    module = types.ModuleType('g3_exact_maintained_compiler')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    need(read_file(path, COMPILER_BYTES) == raw, 'COMPILER_LOAD_CHANGED')
    return module


def compiler(source):
    return compiler_file(source/COMPILER)


def observe(api, owner_module, inputs):
    source, _, run_root, _ = context(api)
    api['require_current']('g3-before-native-observation')
    # Nothing is retained/consumed until all maintained closing guards finish.
    with owner_module.observe_native_run_sources_v2(run_root, source, input_root=inputs) as raw:
        value = parse(raw)
        graph = value['projection']
        need(value['schema'] == 'implementaudit.native-run-source-observation.v2'
             and graph['binding']['acquisition'] == 'NATIVE_CONTINUITY_VERIFIED'
             and graph['binding']['candidate_head'] == SOURCE_COMMIT
             and graph['binding']['candidate_tree'] == SOURCE_TREE
             and graph['binding']['controller'] == api['controller']
             and graph['binding']['receipt'] == api['receipt'], 'ACTUAL_NATIVE_BINDING')
        need(graph['root'] == ROOT and graph['original_scope'] == ORIGINAL, 'ACTUAL_NATIVE_SCOPE')
    api['require_current']('g3-after-native-observation')
    return raw, graph


def check_selection(graph, dispatch, transition):
    need(dispatch['selected'] == SELECTED and dispatch['capacity'] == 2
         and dispatch['active_occupancy'] == 0 and dispatch['free_capacity'] == 2
         and dispatch['graph_required'] is True and dispatch['authority'] == 'NONE', 'PROSPECTIVE_SELECTION_DIFFERS')
    need(transition['selected'] == SELECTED and transition['ancestors'] == [PAIR, PHASE, ROOT]
         and transition['original_scope'] == ORIGINAL, 'RECURSIVE_SELECTION_DIFFERS')
    actual = {row['id']: row for row in graph['nodes']}
    need(set(actual) == set(declarations('0')['STATE.md']['nodes']), 'WHOLE_ROOT_POPULATION')
    for name in ('DG17_PARKED', 'DG18_PARKED', 'FULL_G2_UNPERFORMED',
                 'DG16_ORIGINAL_RECEIVING', 'RESERVED_ORIGINAL_ADOPTION'):
        need(actual[name]['state'] == 'BLOCKED' and 'AUTHORIZATION' in actual[name]['blocked_reasons'],
             'SCHEDULE_OR_RESERVED_AUTHORITY_DROPPED')
    need(actual[JOIN]['requires'] == SELECTED and not actual[JOIN]['independent_results'], 'JOIN_DEPENDENCE_DECLARATION')
    need(not (set(actual[PAIR]['writes']) & set(actual[SCOPE]['writes'])), 'SHARED_WRITER_NOT_ADMITTED')


def policy(run):
    return dict(schema='dg16.g3-prospective-policy.v1', source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE,
        source_parent=SOURCE_PARENT, run_id=run, attempt=1, original_scope_sha256=SCOPE_SHA,
        capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS', host_capacity=2,
        operator_ceiling=2, reserve=0, active_owned_task_slots=0,
        execution_order=['HOST_SCOPE_RECEIVING_BEFORE_TIMED_C5', 'G1_ORIGINAL_PAIR'],
        independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',
        input_limits=dict(file_bytes=FILE_LIMIT, total_bytes=TOTAL_LIMIT, entries=ENTRY_LIMIT, depth=DEPTH_LIMIT),
        full_source_reader='MAINTAINED_GENUINE_C5_SESSION_ACQUIRE_WITH_UNCHANGED_BOUNDS',
        selected_tracked_source_files=SOURCE_FILES, selected_tracked_source_bytes=SOURCE_BYTES,
        original_awards=0, full_g2=False, owner_schedule=['DG16', 'DG17', 'DG18'])


def adverse_basis():
    raw = read_file(Path(__file__).with_name('ADVERSE_APPLICABILITY.json'), 16384)
    need(sha(raw) == ADVERSE_SHA, 'ADVERSE_APPLICABILITY_PIN')
    value = parse(raw)
    need(value.get('schema') == 'dg16.g3-adverse-source-applicability.v1'
         and value.get('compiler_sha256') == COMPILER_SHA
         and value.get('source_commit') == SOURCE_COMMIT and value.get('source_tree') == SOURCE_TREE
         and value.get('status') == 'INERT_CONTROLS_PASSED_NATIVE_EXECUTION_UNPERFORMED'
         and value.get('native_operations') == 0 and value.get('original_awards') == 0,
         'ADVERSE_APPLICABILITY_SCOPE')
    return raw, value


@guarded
def prepare(api, diagnostic):
    source, private, run_root, run = context(api)
    diagnostic.phase('INPUTS')
    need(len(os.sched_getaffinity(0)) >= 2, 'HOST_TASK_CAPACITY_UNAVAILABLE')
    need(callable(api.get('reacquire_inputs')), 'ACTUAL_COMPLETE_INPUT_CONSUMER_REQUIRED')
    observation, key = api['acquisition_observation'], digest(api['acquisition_key'])
    need(sha(acquisition_encode(observation)) == key, 'COMPLETE_ACQUISITION_KEY')
    need(observation.get('source_commit') == SOURCE_COMMIT and observation.get('source_tree') == SOURCE_TREE
         and observation.get('provider', {}).get('source', {}).get('projection') == 'ALL_ACTUAL_BYTES_NO_GIT_OR_HIDDEN_OMISSIONS',
         'COMPLETE_ACQUISITION_SUBJECT')
    canonical_inputs = {}
    for name in ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md','phases/phase-1.md'):
        relative = api['run_root']+'/'+name
        captured = observation['provider']['source']['state']['files'].get(relative)
        current = read_file(run_root/name, CANONICAL_LIMIT)
        need(type(captured) is dict and captured['sha256'] == sha(current) and captured['bytes'] == len(current),
             'SELECTED_C5_CANONICAL_POPULATION')
        canonical_inputs[name] = dict(bytes=len(current),sha256=sha(current))
    base = private/'g3'
    base.mkdir(mode=0o700)
    inputs = base/'inputs'
    inputs.mkdir(mode=0o700)
    write_once(base/'SELECTED_CANONICAL_INPUTS.json', encode(canonical_inputs))
    initial = {'G1_INPUTS.json': encode(dict(key=key, observation=observation)),
               'POLICY.json': encode(policy(run)), 'ORIGINAL_SCOPE.json': scope_basis()[0],
               'SCOPE_READER.py': read_file(Path(__file__), 1024*1024),
               'COMPILER_READER.py': read_file(source/COMPILER, COMPILER_BYTES),
               'ADVERSE_APPLICABILITY.json': adverse_basis()[0]}
    need(sum(map(len, initial.values())) <= TOTAL_LIMIT and len(initial) <= ENTRY_LIMIT, 'DECLARED_INPUT_AGGREGATE')
    for name, raw in initial.items():
        write_once(inputs/name, raw)
    diagnostic.phase('SELECT')
    engine = compiler(source)
    native_raw, graph = observe(api, engine, inputs)
    dispatch = engine.select_native_frontier_v1(graph)
    transition = engine.compile_recursive_transition_v1(graph, [])
    need(graph['binding']['epoch'] == 'G0001', 'INITIAL_NATIVE_GENERATION_REQUIRED')
    check_selection(graph, dispatch, transition)
    for name, data in (('SELECTED_NATIVE.json', native_raw), ('DISPATCH.json', encode(dispatch)),
                       ('TRANSITION.json', encode(transition))):
        write_once(base/name, data)
    diagnostic.done('SELECTED')
    diagnostic.phase('SCOPE_PROCESS')
    # This one real subprocess has its own finite output and joins before the
    # timed pair. It cannot modify canonical/source state or dispatch product.
    began = time.monotonic_ns()
    rc, out, err = api['command']('g3-host-scope-receiver', ['/usr/bin/python3.12', '-I', '-S', '-B',
        str(inputs/'SCOPE_READER.py'), '--scope-receive', str(base)], seconds=30)
    ended = time.monotonic_ns()
    need(rc == 0 and not err and len(out) <= PUBLIC_LIMIT, 'SCOPE_PROCESS_REFUSED')
    scope = validate_public_scope(out)
    need(scope['run_id'] == run and scope['graph_sha256'] == graph['digest']
         and scope['dispatch_sha256'] == dispatch['dispatch_id']
         and scope['complete_input_key'] == key, 'SCOPE_PROCESS_BINDING')
    write_once(base/'SCOPE_RETURN.json', out, PUBLIC_LIMIT)
    write_once(base/'SCOPE_EXECUTION.json', encode(dict(node=SCOPE, actual_exit_code=rc,
        began_monotonic_ns=began, ended_monotonic_ns=ended, stdout_sha256=sha(out), stderr_bytes=0,
        process_kind='ACTUAL_BOUNDED_DISTINCT_HOST_PROCESS', joined_before_timed_pair=True)))
    diagnostic.done('SCOPE_RETURNED')
    diagnostic.phase('INPUTS_RECHECK')
    again = api['reacquire_inputs']()
    need(type(again) is dict and set(again) == {'key', 'observation'}
         and again['key'] == key and again['observation'] == observation, 'COMPLETE_INPUTS_CHANGED')
    second_raw, second_graph = observe(api, engine, inputs)
    need(second_graph == graph, 'SELECTION_CHANGED_BEFORE_PAIR')
    write_once(base/'BEFORE_PAIR_NATIVE.json', second_raw)
    diagnostic.done('INPUTS_RECHECKED')
    return dict(status='PROSPECTIVE_TWO_CELL_SELECTION_COMPLETE', selected=SELECTED,
                graph_sha256=graph['digest'], dispatch_sha256=dispatch['dispatch_id'],
                acquisition_key=key, scope_output_sha256=sha(out), original_awards=0)


def scope_receive(base):
    """Actual independent work: reconcile this host's native selection with the
    complete original scope and current scheduling/consumer obligations.
    Output is useful to the root's component-only consumption decision; it is
    not another review of the historical 48-row contract map.
    """
    base = Path(base)
    raw = read_file(base/'SELECTED_NATIVE.json')
    graph = parse(raw)['projection']
    dispatch = parse(read_file(base/'DISPATCH.json'))
    transition = parse(read_file(base/'TRANSITION.json'))
    inputs = base/'inputs'
    basis_raw = read_file(inputs/'ORIGINAL_SCOPE.json', 8192)
    need(sha(basis_raw) == SCOPE_SHA, 'WORKER_ORIGINAL_SCOPE_PIN')
    basis = parse(basis_raw)
    p = parse(read_file(inputs/'POLICY.json', 8192))
    acquired = parse(read_file(inputs/'G1_INPUTS.json'))
    need(p == policy(p['run_id']) and sha(acquisition_encode(acquired['observation'])) == acquired['key'], 'WORKER_INPUT_BINDING')
    maintained = compiler_file(inputs/'COMPILER_READER.py')
    need(maintained.select_native_frontier_v1(graph) == dispatch
         and maintained.compile_recursive_transition_v1(graph, []) == transition, 'WORKER_MAINTAINED_REDERIVATION')
    check_selection(graph, dispatch, transition)
    need(graph['binding']['acquisition'] == 'NATIVE_CONTINUITY_VERIFIED'
         and graph['binding']['candidate_head'] == SOURCE_COMMIT
         and graph['binding']['candidate_tree'] == SOURCE_TREE, 'WORKER_ACTUAL_SOURCE_BINDING')
    actual = {x['id']: x for x in graph['nodes']}
    provider = acquired['observation']['provider']
    source_files = provider['source']['state']['files']
    need(type(source_files) is dict and provider['actual_source_files'] == len(source_files)
         and provider['actual_source_bytes'] == sum(row['bytes'] for row in source_files.values())
         and provider['source']['projection'] == 'ALL_ACTUAL_BYTES_NO_GIT_OR_HIDDEN_OMISSIONS',
         'WORKER_ACTUAL_SOURCE_CENSUS')
    need(actual[SCOPE]['requires'] == ['FINITE_G2_HISTORY']
         and actual['FINITE_G2_HISTORY']['state'] == 'DONE'
         and actual['FINITE_G2_HISTORY']['done_evidence'] == basis['finite_g2_input']['determination_sha256'],
         'WORKER_COMPLETED_COMPARISON_PREREQUISITE')
    adverse_raw, _ = adverse_basis()
    need(read_file(inputs/'ADVERSE_APPLICABILITY.json', 16384) == adverse_raw, 'WORKER_ADVERSE_INPUT_CHANGED')
    required_coverage = {
        'DG16': ('DG16_ORIGINAL_RECEIVING', 'ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS'),
        'DG17': ('DG17_ORIGINAL_RECEIVING', 'OWNER_REACTIVATES_DG17_AFTER_DG16_DISPOSITION'),
        'DG18': ('DG18_ORIGINAL_RECEIVING', 'OWNER_REACTIVATES_DG18_AFTER_DG17_DISPOSITION')}
    obligations = []
    for cell, (consumer, condition) in required_coverage.items():
        ids = basis['original_ids'][cell]
        need(len(ids) == basis['original_population'][cell] and len(ids) == len(set(ids))
             and actual[consumer]['state'] == 'BLOCKED', 'WORKER_ORIGINAL_CONSUMER_COVERAGE')
        obligations.append(dict(cell=cell, count=len(ids), original_ids_sha256=sha(encode(ids)),
             consumer=consumer, condition=condition, state='RETAINED_UNCONSUMED_IN_THIS_EPISODE'))
    need(sum(x['count'] for x in obligations) == 157 and len(graph['nodes']) == 14, 'WORKER_COMPLETE_POPULATION')
    value = dict(schema='dg16.g3-host-scope-receiving.v1', authority='NONE', source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE, run_id=p['run_id'], attempt=1, graph_sha256=graph['digest'],
        dispatch_sha256=dispatch['dispatch_id'], original_scope_sha256=SCOPE_SHA,
        complete_input_key=acquired['key'], selected_tracked_source_files=SOURCE_FILES,
        selected_tracked_source_bytes=SOURCE_BYTES, scope_obligations=obligations,
        actual_complete_source_files=provider['actual_source_files'],
        actual_complete_source_bytes=provider['actual_source_bytes'],
        ancestors=transition['ancestors'], selected=SELECTED, required_join=JOIN,
        root=ROOT, node_count=len(graph['nodes']), original_total=157,
        observed_affinity_count=len(os.sched_getaffinity(0)),
        capacity_units=p['capacity_units'], host_capacity=2, operator_ceiling=2, reserve=0,
        active_owned_task_slots=0, independence=p['independence'],
        owner_schedule=p['owner_schedule'], full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST',
        original_awards=0, future_adoption='RESERVED_BLOCKED',
        result='HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED', root_decision_before=BEFORE)
    return validate_public_scope(encode(value))


def validate_public_scope(raw):
    value = parse(raw, PUBLIC_LIMIT)
    exact(value, ('schema', 'authority', 'source_commit', 'source_tree', 'run_id', 'attempt',
        'graph_sha256', 'dispatch_sha256', 'original_scope_sha256', 'complete_input_key',
        'selected_tracked_source_files', 'selected_tracked_source_bytes', 'scope_obligations', 'ancestors',
        'actual_complete_source_files', 'actual_complete_source_bytes',
        'selected', 'required_join', 'root', 'node_count', 'original_total', 'observed_affinity_count',
        'capacity_units', 'host_capacity', 'operator_ceiling', 'reserve', 'active_owned_task_slots',
        'independence', 'owner_schedule', 'full_g2', 'original_awards', 'future_adoption',
        'result', 'root_decision_before'))
    need(value['schema'] == 'dg16.g3-host-scope-receiving.v1' and value['authority'] == 'NONE'
         and value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE, 'PUBLIC_SCOPE_IDENTITY')
    need(type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}', value['run_id'])
         and type(value['attempt']) is int and value['attempt'] == 1, 'PUBLIC_SCOPE_RUN')
    for key in ('graph_sha256', 'dispatch_sha256', 'complete_input_key'):
        digest(value[key])
    need(value['original_scope_sha256'] == SCOPE_SHA and value['selected_tracked_source_files'] == SOURCE_FILES
         and value['selected_tracked_source_bytes'] == SOURCE_BYTES and value['original_total'] == 157
         and value['node_count'] == 14, 'PUBLIC_SCOPE_POPULATION')
    integer(value['observed_affinity_count'], 2, 4096)
    integer(value['actual_complete_source_files'], SOURCE_FILES, 4096)
    integer(value['actual_complete_source_bytes'], SOURCE_BYTES, 256*1024**2)
    expected = policy(value['run_id'])
    for key in ('capacity_units', 'host_capacity', 'operator_ceiling', 'reserve',
                'active_owned_task_slots', 'independence', 'owner_schedule'):
        need(type(value[key]) is type(expected[key]) and value[key] == expected[key], 'PUBLIC_SCOPE_POLICY')
    need(value['selected'] == SELECTED and value['ancestors'] == [PAIR, PHASE, ROOT]
         and value['required_join'] == JOIN and value['root'] == ROOT
         and type(value['original_awards']) is int and value['original_awards'] == 0
         and value['full_g2'] == 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST' and value['future_adoption'] == 'RESERVED_BLOCKED'
         and value['root_decision_before'] == BEFORE
         and value['result'] == 'HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED', 'PUBLIC_SCOPE_CREDIT')
    basis = scope_basis()[1]
    need(type(value['scope_obligations']) is list and len(value['scope_obligations']) == 3, 'PUBLIC_OBLIGATION_POPULATION')
    for row, cell, condition in zip(value['scope_obligations'], ('DG16', 'DG17', 'DG18'),
        ('ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS', 'OWNER_REACTIVATES_DG17_AFTER_DG16_DISPOSITION',
         'OWNER_REACTIVATES_DG18_AFTER_DG17_DISPOSITION')):
        exact(row, ('cell', 'count', 'original_ids_sha256', 'consumer', 'condition', 'state'))
        need(row == dict(cell=cell, count=basis['original_population'][cell],
             original_ids_sha256=sha(encode(basis['original_ids'][cell])), consumer=cell+'_ORIGINAL_RECEIVING',
             condition=condition, state='RETAINED_UNCONSUMED_IN_THIS_EPISODE'), 'PUBLIC_OBLIGATION_BINDING')
    need(encode(value) == raw, 'PUBLIC_CANONICAL_BYTES')
    return value


def ancestors(path):
    rows = []
    for parent in reversed(Path(path).absolute().parents):
        s = parent.lstat()
        # GitHub workspace ancestors may be genuinely runner-owned. Bind their
        # actual identity instead of manufacturing UID0 or changing ownership.
        need(stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode), 'HELD_ANCESTRY_NOT_ORDINARY')
        rows.append([str(parent), s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid])
    return rows


def held_files(api):
    source, private, run_root, _ = context(api)
    g = private/'g3'
    names = [run_root/name for name in ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md',
                                      'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')]
    names += [source/COMPILER, source/OWNER]
    names += [g/'inputs'/name for name in ('G1_INPUTS.json', 'POLICY.json', 'ORIGINAL_SCOPE.json',
                                         'SCOPE_READER.py', 'COMPILER_READER.py', 'ADVERSE_APPLICABILITY.json')]
    names += [g/name for name in ('SELECTED_NATIVE.json', 'DISPATCH.json', 'TRANSITION.json', 'SCOPE_RETURN.json',
                                 'SCOPE_EXECUTION.json', 'BEFORE_PAIR_NATIVE.json', 'RETURN_NATIVE.json',
                                 'RESULTS.json', 'JOIN.json', 'EXECUTIONS.json', 'SELECTED_CANONICAL_INPUTS.json')]
    names += [private/name for name in ('G3_ROOT_REQUEST.json', 'G3_SCOPE_RECEIVING.json', 'RECEIVING.json')]
    names += [private/'operation'/name for name in ('RESULT.json', 'PRODUCER_RETURN.json',
                                                    'RECEIVED_RAW_COMPARISON.json', 'OWNED_EVIDENCE_INDEX.json')]
    rows, total = [], 0
    for path in names:
        raw = read_file(path)
        total += len(raw)
        need(total <= TOTAL_LIMIT and len(rows) < ENTRY_LIMIT, 'HELD_SUMMARY_AGGREGATE_BOUND')
        rows.append(dict(path=str(path), physical=identity(path.lstat()), bytes=len(raw),
                         sha256=sha(raw), ancestors=ancestors(path)))
    # This census is explicitly the held native/result summary population.
    # The actual complete G1 captures are reacquired by the unchanged original
    # reader callback; this list is not a substitute for that consumer.
    return rows


def result_envelope(node_id, graph, dispatch, output):
    selected = next(n for n in graph['nodes'] if n['id'] == node_id)
    return dict(schema='implementaudit.work-result.v1', node=node_id,
        dispatch_id=dispatch['dispatch_id'], graph_digest=graph['digest'], input_digest=selected['input_digest'],
        status='PASS', terminal=True, exit_code=0, evidence_digest=digest(output),
        independence_key='ACTUAL_G1_OWNER' if node_id == PAIR else 'ACTUAL_DISTINCT_SCOPE_RECEIVER', scope=[node_id])


def execution_records(graph, dispatch, outputs):
    records = []
    for name in SELECTED:
        node_value = next(n for n in graph['nodes'] if n['id'] == name)
        reads = {p:graph['binding']['read_set'][p] for p in node_value['reads']+node_value['invalidators'] if p.startswith('path:')}
        records.append(dict(node=name, dispatch_id=dispatch['dispatch_id'], graph_digest=graph['digest'],
            input_digest=node_value['input_digest'], input_root_identity=graph['binding']['input_root_identity'],
            read_set=reads, output_digest=outputs[name], exit_code=0))
    return records


def selected_inputs_current(api, expected_key):
    need(callable(api.get('verify_g1_selected_inputs')), 'MAINTAINED_COMPLETE_INPUT_REACQUISITION_REQUIRED')
    value = api['verify_g1_selected_inputs']()
    need(type(value) is dict and set(value) == {'key','observation'} and value['key'] == expected_key
         and len(acquisition_encode(value['observation'])) <= FILE_LIMIT
         and sha(acquisition_encode(value['observation'])) == expected_key,
         'MAINTAINED_COMPLETE_INPUTS_CHANGED')
    selected = parse(read_file(Path(api['private'])/'g3/inputs/G1_INPUTS.json'))
    need(value == selected, 'MAINTAINED_COMPLETE_OBSERVATION_DIFFERS')
    return dict(scope='ACTUAL_MAINTAINED_ACQUIRE_ALL_SOURCE_GIT_HIDDEN_AND_RUNTIME',
                complete_input_key=expected_key, current_generation='G0001', observed_equal=True)


def actual_upstream(api, expected_key, complete_current=True):
    _, private, _, _ = context(api)
    if complete_current:
        selected_inputs_current(api, expected_key)
    need(callable(api.get('verify_g1_retained')), 'ACTUAL_RAW_RECEIVER_CALLBACK_REQUIRED')
    received_sha = digest(api['verify_g1_retained']())
    received_raw = read_file(private/'RECEIVING.json', 8192)
    need(sha(received_raw) == received_sha, 'ACTUAL_RAW_RECEIVER_RETURN_BINDING')
    received = parse(received_raw)
    result_raw = read_file(private/'operation/RESULT.json', 4*1024**2)
    result = parse(result_raw)
    producer = parse(read_file(private/'operation/PRODUCER_RETURN.json', 4*1024**2))
    comparison_sha = sha(read_file(private/'operation/RECEIVED_RAW_COMPARISON.json', 4*1024**2))
    need(received.get('schema') == 'dg16.g1-live-receiving.v1'
         and received.get('source_commit') == SOURCE_COMMIT and received.get('source_tree') == SOURCE_TREE
         and received.get('status') == 'RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE'
         and received.get('authority') == 'NONE' and received.get('original_G1_award') is False
         and received.get('original_acceptance') is False and received.get('same_checkout_current') is True
         and received.get('original_operation_complete') is True and received.get('private_raw_publication') is False
         and received.get('operation_result_sha256') == sha(result_raw)
         and received.get('actual_raw_comparison_sha256') == comparison_sha, 'ACTUAL_G1_RECEIVING_CONJUNCTION')
    need(result.get('source') == dict(source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE)
         and result.get('status') == received['status'] and result.get('raw_receiving_complete') is True
         and result.get('child_terminal_confirmed') is True and result.get('failure') is None
         and result.get('closing_failure') is None and result.get('original_G1_award') is False
         and result.get('selected_acquisition_key') == expected_key, 'ACTUAL_G1_RESULT_CONJUNCTION')
    need(producer.get('schema') == 'implementaudit.genuine-c5-shared-image-pair-result.v1'
         and producer.get('status') == 'SATISFIED_AT_PROSPECTIVE_SHARED_IMAGE_C5_PAIR_CONTRACT'
         and producer.get('acquisition') == expected_key and producer.get('original48_dispatches') == 2
         and producer.get('validated_actual_events') == 38 and producer.get('retained_artifacts') == 12
         and producer.get('source_runtime_current') is True and producer.get('original48_execution_qualified') is False
         and producer.get('canonical_acceptance') == 'UNQUALIFIED', 'ACTUAL_PRODUCER_SCOPE_OR_SELECTED_INPUTS')
    if complete_current:
        selected_inputs_current(api, expected_key)
    return received_sha


def validate_public_request(raw):
    value = parse(raw, REQUEST_LIMIT)
    exact(value, ('schema', 'authority', 'source_commit', 'source_tree', 'source_parent', 'run_id', 'attempt',
        'nonce', 'control_branch', 'control_path', 'root', 'join', 'original_scope_sha256', 'graph_sha256',
        'dispatch_sha256', 'transition_sha256', 'join_sha256', 'scope_return_sha256', 'g1_return_sha256',
        'complete_input_key', 'returned_nodes', 'issued_unix_ms', 'expires_unix_ms', 'hold_seconds',
        'shared_expires_unix_ms', 'shared_window_seconds',
        'decision_before', 'decision_after', 'original_total', 'original_awards', 'full_g2', 'status'))
    need(value['schema'] == 'dg16.g3-root-consumption-request.v1' and value['authority'] == 'NONE'
         and value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE
         and value['source_parent'] == SOURCE_PARENT, 'PUBLIC_REQUEST_SOURCE')
    need(type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}', value['run_id'])
         and type(value['attempt']) is int and value['attempt'] == 1
         and type(value['nonce']) is str and re.fullmatch('[0-9a-f]{32}', value['nonce']), 'PUBLIC_REQUEST_IDENTITY')
    need(value['control_branch'] == CONTROL_BRANCH and value['control_path'] == CONTROL_PATH
         and value['root'] == ROOT and value['join'] == JOIN
         and value['original_scope_sha256'] == SCOPE_SHA, 'PUBLIC_REQUEST_ROUTE')
    for key in ('graph_sha256', 'dispatch_sha256', 'transition_sha256', 'join_sha256',
                'scope_return_sha256', 'g1_return_sha256', 'complete_input_key'):
        digest(value[key])
    hold = integer(value['hold_seconds'], 60, 300)
    start = integer(value['issued_unix_ms'], 1, 10**16)
    need(integer(value['expires_unix_ms'], 1, 10**16) == start+1000*hold, 'PUBLIC_REQUEST_HOLD')
    shared = integer(value['shared_window_seconds'], 180, HOLD_SECONDS)
    need(value['shared_expires_unix_ms'] == start+1000*shared and hold <= shared-120, 'SHARED_DECISION_WINDOW')
    need(value['returned_nodes'] == SELECTED and value['decision_before'] == BEFORE and value['decision_after'] == AFTER
         and type(value['original_total']) is int and value['original_total'] == 157
         and type(value['original_awards']) is int and value['original_awards'] == 0
         and value['full_g2'] == 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST' and value['status'] == 'ROOT_REQUEST_READY', 'PUBLIC_REQUEST_SCOPE')
    need(encode(value) == raw, 'PUBLIC_CANONICAL_BYTES')
    return value


@guarded
def receive(api, diagnostic):
    source, private, _, run = context(api)
    g = private/'g3'
    inputs = g/'inputs'
    diagnostic.phase('UPSTREAM_RECEIVE')
    selected = parse(read_file(g/'SELECTED_NATIVE.json'))['projection']
    dispatch = parse(read_file(g/'DISPATCH.json'))
    transition = parse(read_file(g/'TRANSITION.json'))
    check_selection(selected, dispatch, transition)
    key = parse(read_file(inputs/'G1_INPUTS.json'))['key']
    received_sha = actual_upstream(api, key)
    scope_raw = read_file(g/'SCOPE_RETURN.json', PUBLIC_LIMIT)
    scope = validate_public_scope(scope_raw)
    need(scope['run_id'] == run and scope['graph_sha256'] == selected['digest'], 'ACTUAL_SCOPE_RETURN_IDENTITY')
    diagnostic.done('G1_RECEIVED')
    diagnostic.phase('JOIN')
    engine = compiler(source)
    returned_raw, current = observe(api, engine, inputs)
    outputs = {PAIR:received_sha, SCOPE:sha(scope_raw)}
    results = [result_envelope(name, selected, dispatch, outputs[name]) for name in SELECTED]
    joined = engine.reconcile_native_results_v1(selected, current, dispatch, results, JOIN)
    need(joined['status'] == 'SATISFIED_AT_DECLARED_RESULT_CONTRACT'
         and joined['required'] == SELECTED and joined['all_required_settled'] is True
         and joined['authority'] == 'NONE' and joined['lifecycle_credit'] == 'NONE', 'ACTUAL_JOIN_REFUSED')
    for name, raw in (('RETURN_NATIVE.json', returned_raw), ('RESULTS.json', encode(results)),
                      ('JOIN.json', encode(joined)), ('EXECUTIONS.json', encode(execution_records(selected, dispatch, outputs)))):
        write_once(g/name, raw)
    diagnostic.done('JOIN_READY')
    diagnostic.phase('HOLD_READY')
    now = time.monotonic()
    shared_seconds = min(HOLD_SECONDS, int(api['deadline_monotonic']-now-RESUME_RESERVE_SECONDS))
    need(180 <= shared_seconds <= HOLD_SECONDS, 'INSUFFICIENT_CUSTODY_FOR_ROOT_HOLD')
    hold_seconds = min(300, shared_seconds-120)
    issued = int(time.time()*1000)
    request = dict(schema='dg16.g3-root-consumption-request.v1', authority='NONE', source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE, source_parent=SOURCE_PARENT, run_id=run, attempt=1, nonce=secrets.token_hex(16),
        control_branch=CONTROL_BRANCH, control_path=CONTROL_PATH, root=ROOT, join=JOIN, original_scope_sha256=SCOPE_SHA,
        graph_sha256=selected['digest'], dispatch_sha256=dispatch['dispatch_id'], transition_sha256=transition['digest'],
        join_sha256=sha(encode(joined)), scope_return_sha256=outputs[SCOPE], g1_return_sha256=outputs[PAIR],
        complete_input_key=key, returned_nodes=SELECTED, issued_unix_ms=issued,
        expires_unix_ms=issued+hold_seconds*1000, hold_seconds=hold_seconds,
        shared_expires_unix_ms=issued+shared_seconds*1000, shared_window_seconds=shared_seconds,
        decision_before=BEFORE, decision_after=AFTER, original_total=157, original_awards=0,
        full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST', status='ROOT_REQUEST_READY')
    request_raw = encode(request)
    validate_public_request(request_raw)
    write_once(private/'G3_ROOT_REQUEST.json', request_raw, REQUEST_LIMIT)
    write_once(private/'G3_SCOPE_RECEIVING.json', scope_raw, PUBLIC_LIMIT)
    held = held_files(api)
    hold = dict(schema='dg16.g3-private-hold.v1', request_sha256=sha(request_raw),
                expires_monotonic=now+hold_seconds, enclosing_deadline=api['deadline_monotonic'], held_files=held,
                shared_expires_monotonic=now+shared_seconds,
                held_input_names=sorted(p.name for p in inputs.iterdir()))
    write_once(g/'HOLD.json', encode(hold))
    diagnostic.done('REQUEST_RETAINED')
    return dict(status='ROOT_REQUEST_READY', request_sha256=sha(request_raw), scope_return_sha256=sha(scope_raw),
                hold_seconds=hold_seconds, original_awards=0)


def validate_decision(raw, request, request_sha, now_unix_ms):
    value = parse(raw, DECISION_LIMIT)
    exact(value, ('schema', 'issuer', 'action', 'request_sha256', 'run_id', 'attempt', 'nonce',
        'source_commit', 'source_tree', 'graph_sha256', 'dispatch_sha256', 'join_sha256', 'outputs',
        'consumed_nodes', 'decision_before', 'decision_after', 'owner_schedule', 'full_g2',
        'original_awards', 'issued_unix_ms', 'expires_unix_ms'))
    need(value['schema'] == 'dg16.g3-root-consumption-decision.v1' and value['issuer'] == 'R5_ROOT_GOVERNOR'
         and value['action'] == 'CONSUME_COMPONENT_RETURNS_ONLY' and value['request_sha256'] == digest(request_sha),
         'ROOT_DECISION_ACTION_OR_REQUEST')
    for key in ('run_id', 'attempt', 'nonce', 'source_commit', 'source_tree', 'graph_sha256',
                'dispatch_sha256', 'join_sha256', 'decision_before', 'decision_after', 'full_g2', 'expires_unix_ms'):
        need(type(value[key]) is type(request[key]) and value[key] == request[key], 'ROOT_DECISION_BINDING')
    need(value['outputs'] == {PAIR:request['g1_return_sha256'], SCOPE:request['scope_return_sha256']}
         and value['consumed_nodes'] == SELECTED and value['owner_schedule'] == ['DG16', 'DG17', 'DG18']
         and type(value['original_awards']) is int and value['original_awards'] == 0, 'ROOT_DECISION_SCOPE')
    issued = integer(value['issued_unix_ms'], request['issued_unix_ms'], request['expires_unix_ms'])
    need(issued <= now_unix_ms < request['expires_unix_ms'], 'ROOT_DECISION_EXPIRED_OR_FUTURE')
    need(encode(value) == raw, 'ROOT_DECISION_CANONICAL_BYTES')
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refusal('CONTROL_REDIRECT_REFUSED')


def http_bytes(url, maximum, deadline):
    left = deadline-time.monotonic()
    need(left > 0, 'ROOT_HOLD_EXPIRED')
    request = urllib.request.Request(url, headers={'Accept':'application/json',
        'Cache-Control':'no-cache', 'User-Agent':'implementaudit-reviewed-g3-receiver/1'})
    opener = urllib.request.build_opener(NoRedirect())
    # urllib's socket timeout alone is not a whole-request deadline (including
    # DNS and a slow response). Temporarily shorten the existing main-thread
    # timer, preserving its remaining budget and handler on exit. No producer
    # owner or subprocess is live during this root-decision read.
    began = time.monotonic()
    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)
    own_deadline = old_timer[0] == 0 or left < old_timer[0]
    if own_deadline:
        def expired(_signum, _frame):
            raise Refusal('ROOT_HOLD_EXPIRED')
        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, left)
    try:
        with opener.open(request, timeout=min(HTTP_SECONDS, left)) as response:
            need(response.status == 200 and response.geturl() == url, 'CONTROL_HTTP_RESPONSE')
            size = response.headers.get('Content-Length')
            if size is not None:
                need(re.fullmatch('[0-9]{1,8}', size) and int(size) <= maximum, 'CONTROL_HTTP_BOUND')
            pieces = []
            total = 0
            while total <= maximum:
                need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
                part = response.read1(min(4096, maximum+1-total))
                if not part:
                    break
                pieces.append(part)
                total += len(part)
            raw = b''.join(pieces)
            need(len(raw) <= maximum and time.monotonic() < deadline, 'CONTROL_HTTP_BOUND')
            return raw
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise Refusal('CONTROL_HTTP_REFUSED') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Refusal('CONTROL_TRANSPORT_REFUSED') from None
    finally:
        if own_deadline:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)
            if old_timer[0]:
                signal.setitimer(signal.ITIMER_REAL, max(0.000001, old_timer[0]-(time.monotonic()-began)), old_timer[1])


def read_root_decision(request, request_sha, deadline, final=False):
    ref_url = 'https://api.github.com/repos/'+REPOSITORY+'/git/ref/heads/'+CONTROL_BRANCH
    for _ in range(POLL_COUNT):
        need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
        raw = http_bytes(ref_url, 8192, deadline)
        if raw is not None:
            ref = parse(raw, 8192)
            need(type(ref) is dict and ref.get('ref') == 'refs/heads/'+CONTROL_BRANCH
                 and type(ref.get('object')) is dict and ref['object'].get('type') == 'commit', 'CONTROL_REF_SHAPE')
            commit = ref['object'].get('sha')
            need(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'CONTROL_COMMIT_SHAPE')
            path = FINAL_CONTROL_PATH if final else CONTROL_PATH
            decision_raw = http_bytes('https://raw.githubusercontent.com/'+REPOSITORY+'/'+commit+'/'+path,
                                      16384 if final else DECISION_LIMIT, deadline)
            if decision_raw is not None:
                validate = validate_final_decision if final else validate_decision
                decision = validate(decision_raw, request, request_sha, int(time.time()*1000))
                need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
                return decision_raw, decision, commit
        left = deadline-time.monotonic()
        need(left > 0, 'ROOT_HOLD_EXPIRED')
        time.sleep(min(POLL_SECONDS, left))
    raise Refusal('ROOT_HOLD_POLL_BOUND')


def owner_command(api, label, args, seconds=45):
    source = Path(api['source'])
    rc, out, err = api['command'](label, ['/usr/bin/bash', str(source/OWNER), *args], seconds=seconds)
    need(rc == 0 and not err, 'G3_MAINTAINED_OWNER_REFUSED')
    return out


def require_receipt(api, receipt, label):
    out = owner_command(api, label, ['--require-current-continuity', api['controller']])
    need(out.decode('ascii', 'strict').strip() == receipt, 'G3_CURRENT_RECEIPT_DIFFERS')
    return sha(out)


@guarded
def consume(api, diagnostic):
    source, private, run_root, run = context(api)
    g, inputs = private/'g3', private/'g3/inputs'
    need(not (g/'CONSUMPTION_RESERVED.json').exists(), 'ROOT_CONSUMPTION_ALREADY_RESERVED')
    request_raw = read_file(private/'G3_ROOT_REQUEST.json', REQUEST_LIMIT)
    request = validate_public_request(request_raw)
    scope_raw = read_file(private/'G3_SCOPE_RECEIVING.json', PUBLIC_LIMIT)
    validate_public_scope(scope_raw)
    held = parse(read_file(g/'HOLD.json'))
    need(held.get('schema') == 'dg16.g3-private-hold.v1' and held['request_sha256'] == sha(request_raw)
         and held['enclosing_deadline'] == api['deadline_monotonic'] and request['run_id'] == run
         and held['expires_monotonic'] <= api['deadline_monotonic']-RESUME_RESERVE_SECONDS,
         'PRIVATE_HOLD_BINDING')
    need(held_files(api) == held['held_files'] and sorted(p.name for p in inputs.iterdir()) == held['held_input_names'],
         'HELD_IDENTITY_OR_BYTES_CHANGED')
    diagnostic.phase('CONTROL_READ')
    decision_raw, decision, control_commit = read_root_decision(request, sha(request_raw), held['expires_monotonic'])
    diagnostic.done('ROOT_DECISION_READ')
    # Actual maintained readback and physical identity comparison occur after
    # the hold. A public decision or equal-byte replacement cannot skip either.
    need(actual_upstream(api, request['complete_input_key']) == request['g1_return_sha256'], 'G1_RETURN_CHANGED_DURING_HOLD')
    engine = compiler(source)
    native_raw, current = observe(api, engine, inputs)
    selected = parse(read_file(g/'SELECTED_NATIVE.json'))['projection']
    dispatch = parse(read_file(g/'DISPATCH.json'))
    results = parse(read_file(g/'RESULTS.json'))
    joined = engine.reconcile_native_results_v1(selected, current, dispatch, results, JOIN)
    need(sha(encode(joined)) == request['join_sha256'] and joined['status'] == 'SATISFIED_AT_DECLARED_RESULT_CONTRACT',
         'ROOT_JOIN_CHANGED_DURING_HOLD')
    need(held_files(api) == held['held_files'] and sorted(p.name for p in inputs.iterdir()) == held['held_input_names'],
         'HELD_IDENTITY_OR_BYTES_CHANGED')
    need(time.monotonic() < held['expires_monotonic'] and int(time.time()*1000) < request['expires_unix_ms'],
         'ROOT_HOLD_EXPIRED')
    diagnostic.phase('RESERVE')
    diagnostic.start('reservation')
    write_once(g/'CONSUMPTION_RESERVED.json', encode(dict(schema='dg16.g3-one-shot-reservation.v1',
        request_sha256=sha(request_raw), root_decision_sha256=sha(decision_raw), control_commit=control_commit,
        nonce=request['nonce'], attempt=1)))
    diagnostic.done('CONSUMPTION_RESERVED')
    diagnostic.phase('ROOT_CONSUME')
    diagnostic.start('root_consumption')
    write_once(g/'ROOT_DECISION.json', decision_raw, DECISION_LIMIT)
    write_once(g/'G1_PREBOUNDARY_INPUTS.json', encode(dict(
        scope='ACTUAL_MAINTAINED_ACQUIRE_ALL_SOURCE_GIT_HIDDEN_AND_RUNTIME',
        complete_input_key=request['complete_input_key'], current_generation='G0001',
        root_consumption_decision_sha256=sha(decision_raw),
        actual_canonical_population_sha256=sha(read_file(g/'SELECTED_CANONICAL_INPUTS.json')),
        g1_receiving_sha256=request['g1_return_sha256'], complete_readback_before_and_after_raw_receiver=True)))
    write_once(g/'CONSUMING_NATIVE.json', native_raw)
    executions = parse(read_file(g/'EXECUTIONS.json'))
    transition = parse(read_file(g/'TRANSITION.json'))
    consumptions = [dict(node=row['node'], consumer=JOIN, condition=CONDITION,
        input_digest=row['input_digest'], input_root_identity=row['input_root_identity'],
        read_set_digest=sha(engine.canonical_json_v1(row['read_set'])),
        output_digest=row['output_digest'], decision_before=decision['decision_before'], decision_after=decision['decision_after'])
        for row in executions]
    checked = engine.check_recursive_execution_v1(selected, [], transition, executions, consumptions)
    need(checked['status'] == 'PORTABLE_RECORDS_CONSUMED' and checked['native_campaign_proven'] is False
         and checked['consumed'] == SELECTED, 'RECURSIVE_RECORD_CONSUMPTION_REFUSED')
    # Leave the pure checker's authority and evidence level unchanged. Actual
    # process custody, native observations and root control are separate records.
    write_once(g/'CONSUMPTIONS.json', encode(consumptions))
    write_once(g/'RECURSIVE_RECORD_CHECK.json', encode(checked))
    diagnostic.done('ROOT_CONSUMED')
    completion = {PAIR:request['g1_return_sha256'], SCOPE:request['scope_return_sha256'], JOIN:request['join_sha256']}
    before = {name:read_file(run_root/name, CANONICAL_LIMIT) for name in DOCS}
    updated = render_fences(run_root, declarations(run, completion), False)
    diagnostic.phase('INVALIDATE')
    diagnostic.start('invalidation')
    invalid = owner_command(api, 'g3-invalidate-for-root-join', ['--invalidate-continuity', api['controller'],
        '--boundary', 'manual-resume', '--event', 'g3-root-consumed-'+run+'-'+request['nonce']])
    need(re.fullmatch('refs/implementaudit/continuity-invalidations/'+re.escape(api['controller'])+r'@[0-9a-f]{40}',
                      invalid.decode('ascii','strict').strip()), 'G3_INVALIDATION_TOKEN')
    write_once(g/'INVALIDATION.read', invalid, 4096)
    diagnostic.done('INVALIDATED')
    diagnostic.phase('CANONICAL_UPDATE')
    diagnostic.start('canonical_update')
    for name in DOCS:
        update_existing(run_root/name, before[name], updated[name])
    diagnostic.done('CANONICAL_UPDATED')
    # Separate, exact current canonical reads precede ordinary supported resume.
    write_once(g/'RESUME_STATE.read', read_file(run_root/'STATE.md', CANONICAL_LIMIT), CANONICAL_LIMIT)
    write_once(g/'RESUME_ROADMAP.read', read_file(run_root/'ROADMAP.md', CANONICAL_LIMIT), CANONICAL_LIMIT)
    diagnostic.phase('RESUME')
    diagnostic.start('resume_currentness')
    need(type(api['receipt']) is str and re.fullmatch('refs/implementaudit/continuity-receipts/'
         +re.escape(api['controller'])+r'/G0001@[0-9a-f]{40}', api['receipt']), 'G3_INITIAL_GENERATION')
    resumed = owner_command(api, 'g3-resume-after-root-join', ['--resume-controller', api['controller'],
        '--boundary', 'manual-resume', '--epoch', 'G0002'])
    receipt = resumed.decode('ascii', 'strict').strip()
    need(re.fullmatch('refs/implementaudit/continuity-receipts/'+re.escape(api['controller'])+r'/G0002@[0-9a-f]{40}', receipt),
         'G3_NEW_RECEIPT_SHAPE')
    verified = owner_command(api, 'g3-verify-new-receipt', ['--verify-resume-receipt', receipt])
    need(verified.decode('ascii', 'strict').strip() == receipt, 'G3_NEW_RECEIPT_VERIFY')
    require_receipt(api, receipt, 'g3-require-new-currentness')
    write_once(g/'NEW_RECEIPT.read', resumed, 4096)
    diagnostic.done('NEW_CURRENTNESS')
    diagnostic.phase('REDERIVE')
    diagnostic.start('frontier_recomputation')
    next_api = dict(api, receipt=receipt, require_current=lambda label:require_receipt(api, receipt, label))
    final_raw, final_graph = observe(next_api, engine, inputs)
    final_transition = engine.compile_recursive_transition_v1(final_graph, [checked['event_receipt']])
    need(final_transition['selected'] == [] and final_transition['ancestors'] == [JOIN, PHASE, ROOT]
         and final_graph['binding']['epoch'] == 'G0002', 'POST_JOIN_FRONTIER_REFUSED')
    nodes = {row['id']:row for row in final_graph['nodes']}
    need(all(nodes[name]['state'] == 'DONE' for name in (PAIR, SCOPE, JOIN))
         and all(nodes[name]['state'] != 'DONE' for name in (ROOT, PHASE, 'DG17_PARKED', 'DG18_PARKED',
                  'FULL_G2_UNPERFORMED', 'DG16_ORIGINAL_RECEIVING', 'TRIAD_RECEIVING', 'RESERVED_ORIGINAL_ADOPTION')),
         'POST_JOIN_ANCESTOR_OR_SIBLING_CREDIT')
    write_once(g/'FINAL_NATIVE.json', final_raw)
    write_once(g/'FINAL_TRANSITION.json', encode(final_transition))
    diagnostic.done('FRONTIER_RECOMPUTED')
    diagnostic.phase('STALE_RETURN')
    stale = engine.reconcile_native_results_v1(selected, final_graph, dispatch, results, JOIN)
    need(stale['status'] == 'RECOMPUTE_REQUIRED' and all(name in stale['invalidated'] for name in SELECTED),
         'ACTUAL_STALE_RETURN_NOT_REFUSED')
    write_once(g/'STALE_RETURN.json', encode(stale))
    # Matched negative uses the same real before/after snapshots without another
    # dispatch or root effect. Its result is read-only comparator discrimination.
    missing = engine.reconcile_native_results_v1(selected, selected, dispatch, results[:1], JOIN)
    need(missing['status'] == 'PENDING' and missing['missing'] == [SCOPE], 'MISSING_RETURN_NOT_PENDING')
    write_once(g/'MISSING_RETURN_CONTROL.json', encode(missing))
    diagnostic.done('STALE_RETURN_REFUSED')
    diagnostic.phase('FINAL_REQUEST')
    prepare_final_request(next_api, request, held, selected, final_graph, diagnostic)
    return dict(status='ROOT_CONSUMED_SCOPED_RETURNS', receipt=receipt, root_decision_sha256=sha(decision_raw),
        request_sha256=sha(request_raw), native_final_graph_sha256=final_graph['digest'],
        native_final_transition_sha256=final_transition['digest'], pure_record_status=checked['status'],
        stale_return_status=stale['status'], original_awards=0, full_g2=False, whole_cell_ready=False)


def g1_public_facts(private):
    result = parse(read_file(private/'operation/RESULT.json', 4*1024**2))
    producer = parse(read_file(private/'operation/PRODUCER_RETURN.json', 4*1024**2))
    closing_raw = read_file(private/'operation/producer/closing-custody.json', 4*1024**2)
    closing = parse(closing_raw)
    bank_raw = read_file(private/'NATIVE_BANK_RECEIVING.json', 8192)
    bank = parse(bank_raw)
    bank_output = read_file(private/'native-bank.stdout', 32768)
    bank_result = parse(bank_output, 32768)
    need(bank['source_commit'] == SOURCE_COMMIT and bank['source_tree'] == SOURCE_TREE
         and bank['tests'] == 9 and bank['same_checkout_current'] is True
         and bank['actual_result_sha256'] == sha(bank_output) and bank_result['success'] is True
         and len(bank_result['rows']) == 9 and all(r['outcome'] == 'PASS' for r in bank_result['rows']),
         'FINAL_NATIVE_BANK_RECEIVING')
    elapsed = closing['elapsed_seconds']
    need(type(elapsed) in (int, float) and math.isfinite(elapsed) and 0 <= elapsed <= 1800,
         'G1_ACTUAL_ELAPSED_SHAPE')
    custody = closing['custody']
    runtime = result['selected_runtime_totals']
    original = result['selected_complete_source_totals']
    timing = result['timing']
    outcomes = producer['pair_child_outcomes']
    need(len(outcomes) == 2 and all(row['exit_code'] == 0 for row in outcomes)
         and custody['wait4_reaped'] is True and custody['group_absent'] is True
         and custody['exit_code'] == 0 and not closing['watchdog'] and not closing['cleanup_errors'],
         'G1_ACTUAL_TERMINAL_CONJUNCTION')
    fields = dict(schema='dg16.g3-g1-actual-facts.v1', source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE,
        native_bank_tests=9, native_bank_receiving_sha256=sha(bank_raw), raw_receiving_sha256=sha(read_file(private/'RECEIVING.json',8192)),
        actual_dispatches=2, validated_actual_events=38, retained_artifacts=12,
        original_children_exit_codes=[integer(row['exit_code'],0,0) for row in outcomes],
        producer_closing_sha256=sha(closing_raw), maintained_elapsed_ns=int(elapsed*10**9),
        enclosing_elapsed_ns=integer(timing['enclosing_elapsed_ns'],0,1800*10**9),
        zero_subtracted_ns=integer(timing['subtracted_ns'],0,0), producer_watchdog_seconds=120,
        per_process_cpu_seconds=90, watchdog_events=0, cleanup_errors=0,
        wait4_reaped=True, process_group_absent=True, measured_outer_wait4_max_rss_kib=integer(custody['max_rss_kib'],0,2**63-1),
        max_rss_scope='ACTUAL_OUTER_WAIT4_OBSERVATION_NOT_WINDOWS_WHOLE_JOB',
        runtime_mounted_bytes=integer(runtime['mounted_bytes'],1,128*1024**2),
        runtime_unique_bytes=integer(runtime['unique_bytes'],1,128*1024**2),
        runtime_logical_bytes=integer(runtime['logical_bytes'],1,2**63-1),
        actual_source_files=integer(original['actual_source_files'],SOURCE_FILES,4096),
        actual_source_bytes=integer(original['actual_source_bytes'],SOURCE_BYTES,256*1024**2),
        runtime_physical_limit_bytes=128*1024**2, source_acquisition_limit_bytes=256*1024**2,
        image_readback='COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES',
        operation_scope='PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR',
        producer_original48_qualification=False, whole_DG16_awarded=False)
    return validate_g1_facts(fields)


def validate_g1_facts(value):
    exact(value, ('schema','source_commit','source_tree','native_bank_tests','native_bank_receiving_sha256',
        'raw_receiving_sha256','actual_dispatches','validated_actual_events','retained_artifacts','original_children_exit_codes',
        'producer_closing_sha256','maintained_elapsed_ns','enclosing_elapsed_ns','zero_subtracted_ns','producer_watchdog_seconds',
        'per_process_cpu_seconds','watchdog_events','cleanup_errors','wait4_reaped','process_group_absent',
        'measured_outer_wait4_max_rss_kib','max_rss_scope','runtime_mounted_bytes','runtime_unique_bytes','runtime_logical_bytes',
        'actual_source_files','actual_source_bytes','runtime_physical_limit_bytes','source_acquisition_limit_bytes',
        'image_readback','operation_scope','producer_original48_qualification','whole_DG16_awarded'))
    need(value['schema'] == 'dg16.g3-g1-actual-facts.v1' and value['source_commit'] == SOURCE_COMMIT
         and value['source_tree'] == SOURCE_TREE and value['original_children_exit_codes'] == [0,0]
         and all(type(x) is int for x in value['original_children_exit_codes']), 'FINAL_G1_FACT_IDENTITY')
    for key in ('native_bank_receiving_sha256','raw_receiving_sha256','producer_closing_sha256'):
        digest(value[key])
    for key,expected in dict(native_bank_tests=9,actual_dispatches=2,validated_actual_events=38,retained_artifacts=12,
        zero_subtracted_ns=0,producer_watchdog_seconds=120,per_process_cpu_seconds=90,watchdog_events=0,cleanup_errors=0,
        runtime_physical_limit_bytes=128*1024**2,source_acquisition_limit_bytes=256*1024**2).items():
        need(type(value[key]) is int and value[key] == expected, 'FINAL_G1_FACT_FIXED_BOUND')
    for key in ('maintained_elapsed_ns','enclosing_elapsed_ns'):
        integer(value[key],0,1800*10**9)
    integer(value['measured_outer_wait4_max_rss_kib'],0,2**63-1)
    for key in ('runtime_mounted_bytes','runtime_unique_bytes'):
        integer(value[key],1,128*1024**2)
    integer(value['runtime_logical_bytes'],1,2**63-1)
    integer(value['actual_source_files'],SOURCE_FILES,4096)
    integer(value['actual_source_bytes'],SOURCE_BYTES,256*1024**2)
    need(value['wait4_reaped'] is True and value['process_group_absent'] is True
         and value['max_rss_scope'] == 'ACTUAL_OUTER_WAIT4_OBSERVATION_NOT_WINDOWS_WHOLE_JOB'
         and value['image_readback'] == 'COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES'
         and value['operation_scope'] == 'PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR'
         and value['producer_original48_qualification'] is False and value['whole_DG16_awarded'] is False,
         'FINAL_G1_FACT_SCOPE')
    return value


def final_census(api):
    _, private, _, _ = context(api)
    rows = held_files(api)
    for name in ('FINAL_NATIVE.json','FINAL_TRANSITION.json','STALE_RETURN.json','MISSING_RETURN_CONTROL.json',
                 'ROOT_DECISION.json','CONSUMPTIONS.json','RECURSIVE_RECORD_CHECK.json','NEW_RECEIPT.read',
                 'G1_PREBOUNDARY_INPUTS.json','SELECTED_CANONICAL_INPUTS.json'):
        path = private/'g3'/name
        raw = read_file(path)
        rows.append(dict(path=str(path),physical=identity(path.lstat()),bytes=len(raw),sha256=sha(raw),ancestors=ancestors(path)))
    raw = read_file(private/'G3_FINAL_REQUEST.json', 16384)
    path = private/'G3_FINAL_REQUEST.json'
    rows.append(dict(path=str(path),physical=identity(path.lstat()),bytes=len(raw),sha256=sha(raw),ancestors=ancestors(path)))
    need(sum(r['bytes'] for r in rows) <= TOTAL_LIMIT and len(rows) <= ENTRY_LIMIT, 'FINAL_HELD_SUMMARY_BOUND')
    return rows


def prepare_final_request(api, initial, hold, selected, final_graph, diagnostic):
    _, private, _, run = context(api)
    g = private/'g3'
    left = hold['shared_expires_monotonic']-time.monotonic()
    need(left >= 60 and hold['shared_expires_monotonic'] <= api['deadline_monotonic']-RESUME_RESERVE_SECONDS,
         'INSUFFICIENT_SHARED_WINDOW_FOR_ORIGINAL_RECEIVING')
    paths = dict(g1_receiving=private/'RECEIVING.json', g1_preboundary_inputs=g/'G1_PREBOUNDARY_INPUTS.json',
        scope_receiving=g/'SCOPE_RETURN.json',
        initial_native=g/'SELECTED_NATIVE.json', dispatch=g/'DISPATCH.json', transition=g/'TRANSITION.json',
        join=g/'JOIN.json', root_consumption=g/'ROOT_DECISION.json', recursive_records=g/'RECURSIVE_RECORD_CHECK.json',
        final_native=g/'FINAL_NATIVE.json', final_transition=g/'FINAL_TRANSITION.json', stale_return=g/'STALE_RETURN.json',
        missing_return=g/'MISSING_RETURN_CONTROL.json', negative_applicability=g/'inputs/ADVERSE_APPLICABILITY.json',
        module=g/'inputs/SCOPE_READER.py')
    proofs = {name:sha(read_file(path)) for name,path in paths.items()}
    need(tuple(proofs) == FINAL_PROOF_KEYS, 'FINAL_PROOF_POPULATION')
    final = dict(schema='dg16.g3-original-receiving-request.v1', authority='NONE', source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE, source_parent=SOURCE_PARENT, run_id=run, attempt=1, nonce=initial['nonce'],
        control_branch=CONTROL_BRANCH, control_path=FINAL_CONTROL_PATH, original_scope_sha256=SCOPE_SHA,
        initial_request_sha256=sha(read_file(private/'G3_ROOT_REQUEST.json',REQUEST_LIMIT)), proofs=proofs,
        initial_graph_sha256=selected['digest'], final_graph_sha256=final_graph['digest'],
        continuity_generation='G0002', current_receipt_sha256=sha(api['receipt'].encode()),
        component_return_nodes=SELECTED, consumed_join=JOIN, root=ROOT,
        actual_stale_result='RECOMPUTE_REQUIRED', final_selected=[], original_ids=list(ORIGINAL_IDS),
        original_scopes=dict(zip(ORIGINAL_IDS,ORIGINAL_SCOPES)), g1_facts=g1_public_facts(private),
        g1_input_scope='ACTUALLY_CONSUMED_G0001_COMPLETE_SOURCE_GIT_HIDDEN_AND_RUNTIME',
        g1_complete_input_key=initial['complete_input_key'],
        g3_current_scope='CURRENT_G0002_AFTER_SUPPORTED_ROOT_CONSUMPTION_AND_REDERIVATION',
        input_change_reason='ACTUAL_CAPTURE_INCLUDES_CANONICAL_FILES_CHANGED_BY_ROOT_JOIN_AND_OWNER_GENERATION',
        retained_original_total=157, actual_original_awards='ROOT_DECISION_PENDING',
        original_scope='EXACT_ORIGINAL_ID_AND_GATE_DECISIONS_REQUIRE_ROOT_AND_INDEPENDENT_APPLICABILITY',
        v041_admission='PENDING_NOT_GRANTED_BY_THIS_EPISODE', global_liveness='NOT_ESTABLISHED',
        retirement_or_transfer='NOT_PERFORMED', full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST', whole_DG16_awarded=False,
        shared_window_started_unix_ms=initial['issued_unix_ms'], issued_unix_ms=int(time.time()*1000),
        expires_unix_ms=initial['shared_expires_unix_ms'], shared_window_seconds=initial['shared_window_seconds'],
        status='FINAL_ROOT_DECISION_REQUIRED_WHILE_CURRENT')
    raw = encode(final)
    validate_public_final_request(raw)
    write_once(private/'G3_FINAL_REQUEST.json',raw,16384)
    write_once(g/'FINAL_HOLD.json',encode(dict(schema='dg16.g3-final-private-hold.v1', request_sha256=sha(raw),
        expires_monotonic=hold['shared_expires_monotonic'], enclosing_deadline=api['deadline_monotonic'],
        held_files=final_census(api))))
    diagnostic.done('FINAL_REQUEST_RETAINED')


def validate_public_final_request(raw):
    value = parse(raw,16384)
    exact(value,('schema','authority','source_commit','source_tree','source_parent','run_id','attempt','nonce',
        'control_branch','control_path','original_scope_sha256','initial_request_sha256','proofs','initial_graph_sha256',
        'final_graph_sha256','continuity_generation','current_receipt_sha256','component_return_nodes','consumed_join','root',
        'actual_stale_result','final_selected','original_ids','original_scopes','g1_facts','retained_original_total',
        'g1_input_scope','g1_complete_input_key','g3_current_scope','input_change_reason',
        'actual_original_awards','original_scope','v041_admission','global_liveness','retirement_or_transfer',
        'full_g2','whole_DG16_awarded','shared_window_started_unix_ms','issued_unix_ms','expires_unix_ms',
        'shared_window_seconds','status'))
    need(value['schema']=='dg16.g3-original-receiving-request.v1' and value['authority']=='NONE'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
         and value['source_parent']==SOURCE_PARENT and value['control_branch']==CONTROL_BRANCH
         and value['control_path']==FINAL_CONTROL_PATH and value['original_scope_sha256']==SCOPE_SHA,
         'FINAL_PUBLIC_SOURCE_AND_ROUTE')
    need(type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}',value['run_id'])
         and type(value['attempt']) is int and value['attempt']==1 and type(value['nonce']) is str
         and re.fullmatch('[0-9a-f]{32}',value['nonce']), 'FINAL_PUBLIC_CONTEXT')
    for key in ('initial_request_sha256','initial_graph_sha256','final_graph_sha256','current_receipt_sha256'):
        digest(value[key])
    exact(value['proofs'],FINAL_PROOF_KEYS)
    for item in value['proofs'].values():digest(item)
    need(value['continuity_generation']=='G0002' and value['component_return_nodes']==SELECTED
         and value['consumed_join']==JOIN and value['root']==ROOT and value['actual_stale_result']=='RECOMPUTE_REQUIRED'
         and value['final_selected']==[] and value['original_ids']==list(ORIGINAL_IDS)
         and value['original_scopes']==dict(zip(ORIGINAL_IDS,ORIGINAL_SCOPES)), 'FINAL_PUBLIC_NATIVE_SCOPE')
    validate_g1_facts(value['g1_facts'])
    digest(value['g1_complete_input_key'])
    need(value['g1_input_scope']=='ACTUALLY_CONSUMED_G0001_COMPLETE_SOURCE_GIT_HIDDEN_AND_RUNTIME'
         and value['g3_current_scope']=='CURRENT_G0002_AFTER_SUPPORTED_ROOT_CONSUMPTION_AND_REDERIVATION'
         and value['input_change_reason']=='ACTUAL_CAPTURE_INCLUDES_CANONICAL_FILES_CHANGED_BY_ROOT_JOIN_AND_OWNER_GENERATION',
         'FINAL_INPUT_SCOPE_SEPARATION')
    need(type(value['retained_original_total']) is int and value['retained_original_total']==157
         and value['actual_original_awards']=='ROOT_DECISION_PENDING'
         and value['original_scope']=='EXACT_ORIGINAL_ID_AND_GATE_DECISIONS_REQUIRE_ROOT_AND_INDEPENDENT_APPLICABILITY'
         and value['v041_admission']=='PENDING_NOT_GRANTED_BY_THIS_EPISODE' and value['global_liveness']=='NOT_ESTABLISHED'
         and value['retirement_or_transfer']=='NOT_PERFORMED' and value['full_g2']=='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
         and value['whole_DG16_awarded'] is False and value['status']=='FINAL_ROOT_DECISION_REQUIRED_WHILE_CURRENT',
         'FINAL_PUBLIC_AUTHORITY_SCOPE')
    began=integer(value['shared_window_started_unix_ms'],1,10**16)
    window=integer(value['shared_window_seconds'],180,HOLD_SECONDS)
    issued=integer(value['issued_unix_ms'],began,began+window*1000)
    need(value['expires_unix_ms']==began+window*1000 and issued<value['expires_unix_ms'], 'FINAL_PUBLIC_SHARED_DEADLINE')
    need(encode(value)==raw,'PUBLIC_CANONICAL_BYTES')
    return value


def validate_row_decisions(rows,gates):
    need(type(rows) is list and len(rows)==len(ORIGINAL_IDS), 'FINAL_ORIGINAL_ROW_POPULATION')
    for row,name,scope in zip(rows,ORIGINAL_IDS,ORIGINAL_SCOPES):
        exact(row,('id','scope','disposition','evidence','residuals'))
        need(row['id']==name and row['scope']==scope and row['disposition'] in DISPOSITIONS
             and type(row['evidence']) is list and 1<=len(row['evidence'])<=len(FINAL_PROOF_KEYS)
             and len(row['evidence'])==len(set(row['evidence'])) and all(k in FINAL_PROOF_KEYS for k in row['evidence'])
             and type(row['residuals']) is list and 1<=len(row['residuals'])<=len(RESIDUALS)
             and len(row['residuals'])==len(set(row['residuals'])) and all(k in RESIDUALS for k in row['residuals']),
             'FINAL_ORIGINAL_ROW_SCOPE')
        need(row['disposition']!='NOT_RECEIVED' or 'NONE_AT_DECLARED_SCOPE' not in row['residuals'], 'FINAL_UNRECEIVED_RESIDUAL')
        if name=='R35-L07':
            need('GLOBAL_LIVENESS_UNPROVED' in row['residuals'] and 'RETIREMENT_OR_TRANSFER_UNPERFORMED' in row['residuals'],
                 'L07_STRONGER_CLAIM_MUST_REMAIN_SEPARATE')
    exact(gates,('G1','G3'))
    for name,scope in (('G1','PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR'),('G3','EXACT_Q06_AND_L01_TO_L07_DECLARED_SCOPES')):
        row=gates[name]
        exact(row,('scope','disposition','evidence'))
        need(row['scope']==scope and row['disposition'] in DISPOSITIONS and type(row['evidence']) is list
             and 1<=len(row['evidence'])<=len(FINAL_PROOF_KEYS) and len(set(row['evidence']))==len(row['evidence'])
             and all(k in FINAL_PROOF_KEYS for k in row['evidence']), 'FINAL_GATE_DECISION_SCOPE')
    if gates['G3']['disposition']=='ACCEPTED_AT_DECLARED_SCOPE':
        need(all(row['disposition']=='ACCEPTED_AT_DECLARED_SCOPE' for row in rows),
             'PARTIAL_ROWS_CANNOT_GRANT_COMPLETE_G3_SCOPE')


def validate_final_decision(raw,request,request_sha,now_unix_ms):
    value=parse(raw,16384)
    exact(value,('schema','issuer','action','request_sha256','run_id','attempt','nonce','source_commit','source_tree',
        'final_graph_sha256','current_receipt_sha256','proofs','independent_review_sha256','source_applicability_review_sha256',
        'original_rows','gate_decisions','whole_DG16_awarded','full_g2','v041_admission','global_liveness',
        'retirement_or_transfer','issued_unix_ms','expires_unix_ms'))
    need(value['schema']=='dg16.g3-root-original-decision.v1' and value['issuer']=='R5_ROOT_GOVERNOR'
         and value['action']=='RECEIVE_EXACT_ORIGINAL_IDS_AND_GATES' and value['request_sha256']==digest(request_sha),
         'FINAL_ROOT_DECISION_ACTION')
    for key in ('run_id','attempt','nonce','source_commit','source_tree','final_graph_sha256','current_receipt_sha256',
                'proofs','expires_unix_ms'):
        need(type(value[key]) is type(request[key]) and value[key]==request[key],'FINAL_ROOT_DECISION_BINDING')
    digest(value['independent_review_sha256']);digest(value['source_applicability_review_sha256'])
    validate_row_decisions(value['original_rows'],value['gate_decisions'])
    need(value['whole_DG16_awarded'] is False and value['full_g2']=='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
         and value['v041_admission']=='PENDING_NOT_GRANTED_BY_THIS_EPISODE' and value['global_liveness']=='NOT_ESTABLISHED'
         and value['retirement_or_transfer']=='NOT_PERFORMED','FINAL_ROOT_RESERVED_CONJUNCTION')
    issued=integer(value['issued_unix_ms'],request['issued_unix_ms'],request['expires_unix_ms'])
    need(issued<=now_unix_ms<request['expires_unix_ms'],'FINAL_ROOT_DECISION_EXPIRED_OR_FUTURE')
    need(encode(value)==raw,'ROOT_DECISION_CANONICAL_BYTES')
    return value


@guarded
def decide(api,diagnostic):
    source,private,_,run=context(api)
    g=private/'g3'
    need(not (g/'ORIGINAL_DECISION_RESERVED.json').exists(),'ORIGINAL_DECISION_ALREADY_RESERVED')
    raw=read_file(private/'G3_FINAL_REQUEST.json',16384)
    request=validate_public_final_request(raw)
    held=parse(read_file(g/'FINAL_HOLD.json'))
    need(held['schema']=='dg16.g3-final-private-hold.v1' and held['request_sha256']==sha(raw)
         and held['enclosing_deadline']==api['deadline_monotonic'] and request['run_id']==run
         and request['current_receipt_sha256']==sha(api['receipt'].encode())
         and final_census(api)==held['held_files'], 'FINAL_HELD_IDENTITY_OR_BINDING')
    diagnostic.phase('FINAL_CONTROL_READ')
    decision_raw,decision,commit=read_root_decision(request,sha(raw),held['expires_monotonic'],True)
    # G1 was actually consumed before the supported canonical/generation change.
    # Its old full input key is retained history, not called current G0002 input.
    need(actual_upstream(api,parse(read_file(g/'inputs/G1_INPUTS.json'))['key'],False)==request['proofs']['g1_receiving'],
         'FINAL_ORIGINAL_RAW_RECEIVING_CHANGED')
    engine=compiler(source)
    final_raw,graph=observe(api,engine,g/'inputs')
    need(graph['digest']==request['final_graph_sha256'] and final_census(api)==held['held_files']
         and time.monotonic()<held['expires_monotonic'] and int(time.time()*1000)<request['expires_unix_ms'],
         'FINAL_ORIGINAL_CURRENTNESS_OR_DEADLINE')
    diagnostic.phase('FINAL_DECISION')
    diagnostic.start('original_receiving')
    write_once(g/'ORIGINAL_DECISION_RESERVED.json',encode(dict(request_sha256=sha(raw),
        decision_sha256=sha(decision_raw),control_commit=commit,nonce=request['nonce'])))
    write_once(g/'ORIGINAL_DECISION.json',decision_raw,16384)
    write_once(g/'ORIGINAL_DECISION_CURRENT_NATIVE.json',final_raw)
    require_receipt(api,api['receipt'],'g3-original-decision-currentness')
    projection=dict(schema='dg16.g3-root-original-decision-retained.v1',authority='ROOT_GOVERNOR_RECORDED_DECISION',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,run_id=run,attempt=1,
        request_sha256=sha(raw),decision_sha256=sha(decision_raw),control_commit=commit,
        current_graph_sha256=graph['digest'],current_receipt_sha256=request['current_receipt_sha256'],
        independent_review_sha256=decision['independent_review_sha256'],
        source_applicability_review_sha256=decision['source_applicability_review_sha256'],
        original_rows=decision['original_rows'],gate_decisions=decision['gate_decisions'],
        whole_DG16_awarded=False,full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST',
        status='ROOT_G3_DECISION_RETAINED',automatic_awards=False)
    validate_original_receipt(encode(projection))
    write_once(private/'G3_ORIGINAL_DECISION_RECEIPT.json',encode(projection),16384)
    diagnostic.value['root_original_disposition']=decision['gate_decisions']['G3']['disposition']
    diagnostic.value['root_original_ids']=[row['id'] for row in decision['original_rows'] if row['disposition']=='ACCEPTED_AT_DECLARED_SCOPE']
    diagnostic.done('ORIGINAL_DECISION_RETAINED')
    diagnostic.phase('COMPLETE')
    return dict(status='ROOT_G3_DECISION_RETAINED',receipt=api['receipt'],
        root_decision_sha256=sha(decision_raw),root_receiving=projection,whole_DG16_awarded=False,automatic_awards=False)


def validate_original_receipt(raw):
    value=parse(raw,16384)
    exact(value,('schema','authority','source_commit','source_tree','run_id','attempt','request_sha256',
        'decision_sha256','control_commit','current_graph_sha256','current_receipt_sha256',
        'independent_review_sha256','source_applicability_review_sha256','original_rows','gate_decisions',
        'whole_DG16_awarded','full_g2','status','automatic_awards'))
    need(value['schema']=='dg16.g3-root-original-decision-retained.v1'
         and value['authority']=='ROOT_GOVERNOR_RECORDED_DECISION'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
         and type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}',value['run_id'])
         and type(value['attempt']) is int and value['attempt']==1
         and type(value['control_commit']) is str and re.fullmatch('[0-9a-f]{40}',value['control_commit']),
         'ORIGINAL_RECEIPT_IDENTITY')
    for key in ('request_sha256','decision_sha256','current_graph_sha256','current_receipt_sha256',
                'independent_review_sha256','source_applicability_review_sha256'):
        digest(value[key])
    validate_row_decisions(value['original_rows'],value['gate_decisions'])
    need(value['whole_DG16_awarded'] is False and value['full_g2']=='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
         and value['status']=='ROOT_G3_DECISION_RETAINED' and value['automatic_awards'] is False,
         'ORIGINAL_RECEIPT_SCOPE')
    need(encode(value)==raw,'PUBLIC_CANONICAL_BYTES')
    return value


def validate_effect_state(raw):
    value = parse(raw, 4096)
    exact(value, ('schema', 'authority', 'phase', 'completed', 'failed', 'failure_code', 'exception_category',
                 'original_awards', 'consumption_reserved', 'root_consumed', 'continuity_updated',
                 'native_frontier_recomputed', 'root_original_disposition', 'root_original_ids', 'effects'))
    need(value['schema'] == 'dg16.g3-diagnostic.v1' and value['authority'] == 'NONE'
         and value['phase'] in PHASES and type(value['original_awards']) is int and value['original_awards'] == 0,
         'DIAGNOSTIC_SCHEMA')
    need(type(value['completed']) is list and value['completed'] == list(MILESTONES[:len(value['completed'])]), 'DIAGNOSTIC_MILESTONE')
    for key in ('failed', 'consumption_reserved', 'root_consumed', 'continuity_updated', 'native_frontier_recomputed'):
        need(type(value[key]) is bool, 'DIAGNOSTIC_BOOLEAN')
    need(value['failure_code'] is None or value['failure_code'] in REFUSAL_CODES | {'UNCLASSIFIED_EXCEPTION'}, 'DIAGNOSTIC_CODE')
    need(value['exception_category'] in (None, 'Refusal', 'OSError', 'FileNotFoundError', 'PermissionError', 'ValueError',
                'TypeError', 'KeyError', 'WorkGraphError', 'KeyboardInterrupt', 'SystemExit', 'OTHER'), 'DIAGNOSTIC_CATEGORY')
    exact(value['effects'], ('reservation', 'root_consumption', 'invalidation', 'canonical_update',
                             'resume_currentness', 'frontier_recomputation', 'original_receiving'))
    need(all(x in ('NOT_STARTED', 'STARTED_OUTCOME_UNKNOWN', 'COMPLETED') for x in value['effects'].values()),
         'DIAGNOSTIC_EFFECT')
    for key,mark in (('consumption_reserved','CONSUMPTION_RESERVED'),('root_consumed','ROOT_CONSUMED'),
                     ('continuity_updated','NEW_CURRENTNESS'),('native_frontier_recomputed','FRONTIER_RECOMPUTED')):
        need(value[key] == (mark in value['completed']), 'DIAGNOSTIC_FLAG_CONTRADICTION')
    for key,mark in dict(reservation='CONSUMPTION_RESERVED',root_consumption='ROOT_CONSUMED',invalidation='INVALIDATED',
        canonical_update='CANONICAL_UPDATED',resume_currentness='NEW_CURRENTNESS',frontier_recomputation='FRONTIER_RECOMPUTED',
        original_receiving='ORIGINAL_DECISION_RETAINED').items():
        need((value['effects'][key]=='COMPLETED') == (mark in value['completed']), 'DIAGNOSTIC_EFFECT_CONTRADICTION')
    need(value['root_original_disposition'] in (None,*DISPOSITIONS)
         and type(value['root_original_ids']) is list and len(value['root_original_ids'])<=8
         and len(set(value['root_original_ids']))==len(value['root_original_ids'])
         and all(x in ORIGINAL_IDS for x in value['root_original_ids']), 'DIAGNOSTIC_ORIGINAL_SCOPE')
    if 'ORIGINAL_DECISION_RETAINED' not in value['completed']:
        need(value['root_original_disposition'] is None and not value['root_original_ids'], 'DIAGNOSTIC_UNEARNED_ROOT_DECISION')
    need(encode(value) == raw, 'DIAGNOSTIC_CANONICAL_BYTES')
    return value


# Fixed literal refusal vocabulary is generated from this module's own literal
# need()/Refusal() sites by the authoring control, then independently sealed.
REFUSAL_CODES = frozenset(('ACTUAL_COMPLETE_INPUT_CONSUMER_REQUIRED', 'ACTUAL_G1_RECEIVING_CONJUNCTION', 'ACTUAL_G1_RESULT_CONJUNCTION', 'ACTUAL_JOIN_REFUSED', 'ACTUAL_NATIVE_BINDING', 'ACTUAL_NATIVE_SCOPE', 'ACTUAL_OWNED_ROOT_REQUIRED', 'ACTUAL_PRODUCER_SCOPE_OR_SELECTED_INPUTS', 'ACTUAL_RAW_RECEIVER_CALLBACK_REQUIRED', 'ACTUAL_RAW_RECEIVER_RETURN_BINDING', 'ACTUAL_ROOT_CUSTODY_REQUIRED', 'ACTUAL_SCOPE_RETURN_IDENTITY', 'ACTUAL_STALE_RETURN_NOT_REFUSED', 'ADVERSE_APPLICABILITY_PIN', 'ADVERSE_APPLICABILITY_SCOPE', 'ANCESTOR_CREDIT_REFUSED', 'CANONICAL_FENCE_POPULATION', 'CANONICAL_FILE_BOUND', 'CANONICAL_OPEN_CHANGED', 'CANONICAL_PREIMAGE_CHANGED', 'CANONICAL_READBACK', 'CANONICAL_TOTAL_BOUND', 'CLOSED_SCHEMA_REFUSED', 'COMPILER_LOAD_CHANGED', 'COMPILER_PIN', 'COMPLETE_ACQUISITION_KEY', 'COMPLETE_ACQUISITION_SUBJECT', 'COMPLETE_INPUTS_CHANGED', 'CONTROL_COMMIT_SHAPE', 'CONTROL_HTTP_BOUND', 'CONTROL_HTTP_REFUSED', 'CONTROL_HTTP_RESPONSE', 'CONTROL_REDIRECT_REFUSED', 'CONTROL_REF_SHAPE', 'CONTROL_TRANSPORT_REFUSED', 'DECLARED_INPUT_AGGREGATE', 'DIAGNOSTIC_BOOLEAN', 'DIAGNOSTIC_BOUND', 'DIAGNOSTIC_CANONICAL_BYTES', 'DIAGNOSTIC_CATEGORY', 'DIAGNOSTIC_CODE', 'DIAGNOSTIC_EFFECT', 'DIAGNOSTIC_EFFECT_CONTRADICTION', 'DIAGNOSTIC_FLAG_CONTRADICTION', 'DIAGNOSTIC_MILESTONE', 'DIAGNOSTIC_ORIGINAL_SCOPE', 'DIAGNOSTIC_PHASE', 'DIAGNOSTIC_SCHEMA', 'DIAGNOSTIC_UNEARNED_ROOT_DECISION', 'DIGEST_SHAPE', 'DUPLICATE_JSON_KEY', 'EFFECT_ALREADY_STARTED', 'ENCLOSING_DEADLINE', 'FILE_OPEN_CHANGED', 'FILE_READ_CHANGED', 'FINAL_G1_FACT_FIXED_BOUND', 'FINAL_G1_FACT_IDENTITY', 'FINAL_G1_FACT_SCOPE', 'FINAL_GATE_DECISION_SCOPE', 'FINAL_HELD_IDENTITY_OR_BINDING', 'FINAL_HELD_SUMMARY_BOUND', 'FINAL_INPUT_SCOPE_SEPARATION', 'FINAL_NATIVE_BANK_RECEIVING', 'FINAL_ORIGINAL_CURRENTNESS_OR_DEADLINE', 'FINAL_ORIGINAL_RAW_RECEIVING_CHANGED', 'FINAL_ORIGINAL_ROW_POPULATION', 'FINAL_ORIGINAL_ROW_SCOPE', 'FINAL_PROOF_POPULATION', 'FINAL_PUBLIC_AUTHORITY_SCOPE', 'FINAL_PUBLIC_CONTEXT', 'FINAL_PUBLIC_NATIVE_SCOPE', 'FINAL_PUBLIC_SHARED_DEADLINE', 'FINAL_PUBLIC_SOURCE_AND_ROUTE', 'FINAL_ROOT_DECISION_ACTION', 'FINAL_ROOT_DECISION_BINDING', 'FINAL_ROOT_DECISION_EXPIRED_OR_FUTURE', 'FINAL_ROOT_RESERVED_CONJUNCTION', 'FINAL_UNRECEIVED_RESIDUAL', 'FIXED_SCOPE_READER_ENTRY_ONLY', 'FRESH_CONTROLLER_REQUIRED', 'FRESH_JOB_CONTEXT_REQUIRED', 'FRESH_RUN_ROOT_REQUIRED', 'G1_ACTUAL_ELAPSED_SHAPE', 'G1_ACTUAL_TERMINAL_CONJUNCTION', 'G1_RETURN_CHANGED_DURING_HOLD', 'G3_CURRENT_RECEIPT_DIFFERS', 'G3_INITIAL_GENERATION', 'G3_INVALIDATION_TOKEN', 'G3_MAINTAINED_OWNER_REFUSED', 'G3_NEW_RECEIPT_SHAPE', 'G3_NEW_RECEIPT_VERIFY', 'HELD_ANCESTRY_NOT_ORDINARY', 'HELD_IDENTITY_OR_BYTES_CHANGED', 'HELD_SUMMARY_AGGREGATE_BOUND', 'HOST_TASK_CAPACITY_UNAVAILABLE', 'INITIAL_NATIVE_GENERATION_REQUIRED', 'INSUFFICIENT_CUSTODY_FOR_ROOT_HOLD', 'INSUFFICIENT_SHARED_WINDOW_FOR_ORIGINAL_RECEIVING', 'INTEGER_BOUND', 'JOIN_DEPENDENCE_DECLARATION', 'JSON_BYTE_BOUND', 'L07_STRONGER_CLAIM_MUST_REMAIN_SEPARATE', 'MAINTAINED_COMPLETE_INPUTS_CHANGED', 'MAINTAINED_COMPLETE_INPUT_REACQUISITION_REQUIRED', 'MAINTAINED_COMPLETE_OBSERVATION_DIFFERS', 'MISSING_RETURN_NOT_PENDING', 'NONFINITE_JSON', 'ORDINARY_FILE_BOUND', 'ORIGINAL_DECISION_ALREADY_RESERVED', 'ORIGINAL_ID_POPULATION', 'ORIGINAL_POPULATION', 'ORIGINAL_RECEIPT_IDENTITY', 'ORIGINAL_RECEIPT_SCOPE', 'ORIGINAL_SCOPE_PIN', 'PARTIAL_ROWS_CANNOT_GRANT_COMPLETE_G3_SCOPE', 'POST_JOIN_ANCESTOR_OR_SIBLING_CREDIT', 'POST_JOIN_FRONTIER_REFUSED', 'PREACTIVATION_ONLY', 'PRIVATE_HOLD_BINDING', 'PRIVATE_OUTPUT_BOUND', 'PRIVATE_OUTPUT_READBACK', 'PRIVATE_SOURCE_SEPARATION', 'PROSPECTIVE_SELECTION_DIFFERS', 'PUBLIC_CANONICAL_BYTES', 'PUBLIC_OBLIGATION_BINDING', 'PUBLIC_OBLIGATION_POPULATION', 'PUBLIC_REQUEST_HOLD', 'PUBLIC_REQUEST_IDENTITY', 'PUBLIC_REQUEST_ROUTE', 'PUBLIC_REQUEST_SCOPE', 'PUBLIC_REQUEST_SOURCE', 'PUBLIC_SCOPE_CREDIT', 'PUBLIC_SCOPE_IDENTITY', 'PUBLIC_SCOPE_POLICY', 'PUBLIC_SCOPE_POPULATION', 'PUBLIC_SCOPE_RUN', 'RECURSIVE_RECORD_CONSUMPTION_REFUSED', 'RECURSIVE_SELECTION_DIFFERS', 'ROOT_CONSUMPTION_ALREADY_RESERVED', 'ROOT_DECISION_ACTION_OR_REQUEST', 'ROOT_DECISION_BINDING', 'ROOT_DECISION_CANONICAL_BYTES', 'ROOT_DECISION_EXPIRED_OR_FUTURE', 'ROOT_DECISION_SCOPE', 'ROOT_HOLD_EXPIRED', 'ROOT_HOLD_POLL_BOUND', 'ROOT_JOIN_CHANGED_DURING_HOLD', 'RUN_ID_SHAPE', 'SCHEDULE_OR_RESERVED_AUTHORITY_DROPPED', 'SCOPE_PROCESS_BINDING', 'SCOPE_PROCESS_REFUSED', 'SELECTED_C5_CANONICAL_POPULATION', 'SELECTION_CHANGED_BEFORE_PAIR', 'SHARED_DECISION_WINDOW', 'SHARED_WRITER_NOT_ADMITTED', 'WHOLE_ROOT_POPULATION', 'WORKER_ACTUAL_SOURCE_BINDING', 'WORKER_ACTUAL_SOURCE_CENSUS', 'WORKER_ADVERSE_INPUT_CHANGED', 'WORKER_COMPLETED_COMPARISON_PREREQUISITE', 'WORKER_COMPLETE_POPULATION', 'WORKER_INPUT_BINDING', 'WORKER_MAINTAINED_REDERIVATION', 'WORKER_ORIGINAL_CONSUMER_COVERAGE', 'WORKER_ORIGINAL_SCOPE_PIN'))  # @REFUSAL_CODES@


if __name__ == '__main__':
    need(len(sys.argv) == 3 and sys.argv[1] == '--scope-receive', 'FIXED_SCOPE_READER_ENTRY_ONLY')
    sys.stdout.buffer.write(encode(scope_receive(Path(sys.argv[2]))))
