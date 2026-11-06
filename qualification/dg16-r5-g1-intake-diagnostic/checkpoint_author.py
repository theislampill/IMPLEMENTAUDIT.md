"""Exact hosted03r1 preactivation author closure only.

The native graph and AUTHORED record remain comparable. No receiving,
consumption, control fetch, provider, or original-award operation is reachable.
"""
import hashlib,json,math,os,re,stat,sys,time
from pathlib import Path
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
SCOPE_SHA = 'ec8a371d9b13686883d9f15034bdd25202893b855b63d53f39eb03cda41cd668'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
JOB_BRANCH = 'pro/dg16-r5-g1-intake-diagnostic-05-20261106'
ROOT, PHASE, JOIN = 'R5_ROOT', 'DG16_CURRENT', 'DG16_COMPONENT_JOIN'
PAIR, SCOPE = 'G1_ORIGINAL_PAIR', 'HOST_SCOPE_RECEIVING'
SELECTED = [PAIR, SCOPE]
ORIGINAL = 'DG16_48_DG17_95_DG18_14_ORIGINAL157'
CONDITION = 'ACTUAL_ROOT_CONSUMPTION_OF_BOTH_COMPONENT_RETURNS'
DOCS = ('STATE.md', 'ROADMAP.md', 'phases/phase-1.md')
FENCE = re.compile(rb'(?m)^```implementaudit-work-graph\n.*?\n```[ \t]*$', re.S)
FILE_LIMIT, TOTAL_LIMIT, ENTRY_LIMIT, DEPTH_LIMIT = 16*1024**2, 64*1024**2, 4096, 16
CANONICAL_LIMIT, CANONICAL_TOTAL = 96*1024, 256*1024
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
DISPOSITIONS = ('ACCEPTED_AT_DECLARED_SCOPE', 'PARTIAL_SCOPE_ONLY', 'NOT_RECEIVED')
REFUSAL_CODES = frozenset(('ACTUAL_COMPLETE_INPUT_CONSUMER_REQUIRED', 'ACTUAL_G1_RECEIVING_CONJUNCTION', 'ACTUAL_G1_RESULT_CONJUNCTION', 'ACTUAL_JOIN_REFUSED', 'ACTUAL_NATIVE_BINDING', 'ACTUAL_NATIVE_SCOPE', 'ACTUAL_OWNED_ROOT_REQUIRED', 'ACTUAL_PRODUCER_SCOPE_OR_SELECTED_INPUTS', 'ACTUAL_RAW_RECEIVER_CALLBACK_REQUIRED', 'ACTUAL_RAW_RECEIVER_RETURN_BINDING', 'ACTUAL_ROOT_CUSTODY_REQUIRED', 'ACTUAL_SCOPE_RETURN_IDENTITY', 'ACTUAL_STALE_RETURN_NOT_REFUSED', 'ADVERSE_APPLICABILITY_PIN', 'ADVERSE_APPLICABILITY_SCOPE', 'ANCESTOR_CREDIT_REFUSED', 'CANONICAL_FENCE_POPULATION', 'CANONICAL_FILE_BOUND', 'CANONICAL_OPEN_CHANGED', 'CANONICAL_PREIMAGE_CHANGED', 'CANONICAL_READBACK', 'CANONICAL_TOTAL_BOUND', 'CLOSED_SCHEMA_REFUSED', 'COMPILER_LOAD_CHANGED', 'COMPILER_PIN', 'COMPLETE_ACQUISITION_KEY', 'COMPLETE_ACQUISITION_SUBJECT', 'COMPLETE_INPUTS_CHANGED', 'CONTROL_COMMIT_SHAPE', 'CONTROL_HTTP_BOUND', 'CONTROL_HTTP_REFUSED', 'CONTROL_HTTP_RESPONSE', 'CONTROL_REDIRECT_REFUSED', 'CONTROL_REF_SHAPE', 'CONTROL_TRANSPORT_REFUSED', 'DECLARED_INPUT_AGGREGATE', 'DIAGNOSTIC_BOOLEAN', 'DIAGNOSTIC_BOUND', 'DIAGNOSTIC_CANONICAL_BYTES', 'DIAGNOSTIC_CATEGORY', 'DIAGNOSTIC_CODE', 'DIAGNOSTIC_EFFECT', 'DIAGNOSTIC_EFFECT_CONTRADICTION', 'DIAGNOSTIC_FLAG_CONTRADICTION', 'DIAGNOSTIC_MILESTONE', 'DIAGNOSTIC_ORIGINAL_SCOPE', 'DIAGNOSTIC_PHASE', 'DIAGNOSTIC_SCHEMA', 'DIAGNOSTIC_UNEARNED_ROOT_DECISION', 'DIGEST_SHAPE', 'DUPLICATE_JSON_KEY', 'EFFECT_ALREADY_STARTED', 'ENCLOSING_DEADLINE', 'FILE_OPEN_CHANGED', 'FILE_READ_CHANGED', 'FINAL_G1_FACT_FIXED_BOUND', 'FINAL_G1_FACT_IDENTITY', 'FINAL_G1_FACT_SCOPE', 'FINAL_GATE_DECISION_SCOPE', 'FINAL_HELD_IDENTITY_OR_BINDING', 'FINAL_HELD_SUMMARY_BOUND', 'FINAL_INPUT_SCOPE_SEPARATION', 'FINAL_NATIVE_BANK_RECEIVING', 'FINAL_ORIGINAL_CURRENTNESS_OR_DEADLINE', 'FINAL_ORIGINAL_RAW_RECEIVING_CHANGED', 'FINAL_ORIGINAL_ROW_POPULATION', 'FINAL_ORIGINAL_ROW_SCOPE', 'FINAL_PROOF_POPULATION', 'FINAL_PUBLIC_AUTHORITY_SCOPE', 'FINAL_PUBLIC_CONTEXT', 'FINAL_PUBLIC_NATIVE_SCOPE', 'FINAL_PUBLIC_SHARED_DEADLINE', 'FINAL_PUBLIC_SOURCE_AND_ROUTE', 'FINAL_ROOT_DECISION_ACTION', 'FINAL_ROOT_DECISION_BINDING', 'FINAL_ROOT_DECISION_EXPIRED_OR_FUTURE', 'FINAL_ROOT_RESERVED_CONJUNCTION', 'FINAL_UNRECEIVED_RESIDUAL', 'FIXED_SCOPE_READER_ENTRY_ONLY', 'FRESH_CONTROLLER_REQUIRED', 'FRESH_JOB_CONTEXT_REQUIRED', 'FRESH_RUN_ROOT_REQUIRED', 'G1_ACTUAL_ELAPSED_SHAPE', 'G1_ACTUAL_TERMINAL_CONJUNCTION', 'G1_RETURN_CHANGED_DURING_HOLD', 'G3_CURRENT_RECEIPT_DIFFERS', 'G3_INITIAL_GENERATION', 'G3_INVALIDATION_TOKEN', 'G3_MAINTAINED_OWNER_REFUSED', 'G3_NEW_RECEIPT_SHAPE', 'G3_NEW_RECEIPT_VERIFY', 'HELD_ANCESTRY_NOT_ORDINARY', 'HELD_IDENTITY_OR_BYTES_CHANGED', 'HELD_SUMMARY_AGGREGATE_BOUND', 'HOST_TASK_CAPACITY_UNAVAILABLE', 'INITIAL_NATIVE_GENERATION_REQUIRED', 'INSUFFICIENT_CUSTODY_FOR_ROOT_HOLD', 'INSUFFICIENT_SHARED_WINDOW_FOR_ORIGINAL_RECEIVING', 'INTEGER_BOUND', 'JOIN_DEPENDENCE_DECLARATION', 'JSON_BYTE_BOUND', 'L07_STRONGER_CLAIM_MUST_REMAIN_SEPARATE', 'MAINTAINED_COMPLETE_INPUTS_CHANGED', 'MAINTAINED_COMPLETE_INPUT_REACQUISITION_REQUIRED', 'MAINTAINED_COMPLETE_OBSERVATION_DIFFERS', 'MISSING_RETURN_NOT_PENDING', 'NONFINITE_JSON', 'ORDINARY_FILE_BOUND', 'ORIGINAL_DECISION_ALREADY_RESERVED', 'ORIGINAL_ID_POPULATION', 'ORIGINAL_POPULATION', 'ORIGINAL_RECEIPT_IDENTITY', 'ORIGINAL_RECEIPT_SCOPE', 'ORIGINAL_SCOPE_PIN', 'PARTIAL_ROWS_CANNOT_GRANT_COMPLETE_G3_SCOPE', 'POST_JOIN_ANCESTOR_OR_SIBLING_CREDIT', 'POST_JOIN_FRONTIER_REFUSED', 'PREACTIVATION_ONLY', 'PRIVATE_HOLD_BINDING', 'PRIVATE_OUTPUT_BOUND', 'PRIVATE_OUTPUT_READBACK', 'PRIVATE_SOURCE_SEPARATION', 'PROSPECTIVE_SELECTION_DIFFERS', 'PUBLIC_CANONICAL_BYTES', 'PUBLIC_OBLIGATION_BINDING', 'PUBLIC_OBLIGATION_POPULATION', 'PUBLIC_REQUEST_HOLD', 'PUBLIC_REQUEST_IDENTITY', 'PUBLIC_REQUEST_ROUTE', 'PUBLIC_REQUEST_SCOPE', 'PUBLIC_REQUEST_SOURCE', 'PUBLIC_SCOPE_CREDIT', 'PUBLIC_SCOPE_IDENTITY', 'PUBLIC_SCOPE_POLICY', 'PUBLIC_SCOPE_POPULATION', 'PUBLIC_SCOPE_RUN', 'RECURSIVE_RECORD_CONSUMPTION_REFUSED', 'RECURSIVE_SELECTION_DIFFERS', 'ROOT_CONSUMPTION_ALREADY_RESERVED', 'ROOT_DECISION_ACTION_OR_REQUEST', 'ROOT_DECISION_BINDING', 'ROOT_DECISION_CANONICAL_BYTES', 'ROOT_DECISION_EXPIRED_OR_FUTURE', 'ROOT_DECISION_SCOPE', 'ROOT_HOLD_EXPIRED', 'ROOT_HOLD_POLL_BOUND', 'ROOT_JOIN_CHANGED_DURING_HOLD', 'RUN_ID_SHAPE', 'SCHEDULE_OR_RESERVED_AUTHORITY_DROPPED', 'SCOPE_PROCESS_BINDING', 'SCOPE_PROCESS_REFUSED', 'SELECTED_C5_CANONICAL_POPULATION', 'SELECTION_CHANGED_BEFORE_PAIR', 'SHARED_DECISION_WINDOW', 'SHARED_WRITER_NOT_ADMITTED', 'WHOLE_ROOT_POPULATION', 'WORKER_ACTUAL_SOURCE_BINDING', 'WORKER_ACTUAL_SOURCE_CENSUS', 'WORKER_ADVERSE_INPUT_CHANGED', 'WORKER_COMPLETED_COMPARISON_PREREQUISITE', 'WORKER_COMPLETE_POPULATION', 'WORKER_INPUT_BINDING', 'WORKER_MAINTAINED_REDERIVATION', 'WORKER_ORIGINAL_CONSUMER_COVERAGE', 'WORKER_ORIGINAL_SCOPE_PIN'))  # @REFUSAL_CODES@

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
