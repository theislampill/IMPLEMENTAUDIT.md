# Exact bounded source projection; source module is never imported.
SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'

SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'

SOURCE_PARENT = '8c393aa0d415e3bb4f25d333316b3abaf498e5af'

SOURCE_FILES, SOURCE_BYTES = 1766, 167022772

SCOPE_SHA = '8c08f2aecd34f582f3662b5bc83b3d3a27cee33d2f17711ced868a1d7b11c96a'

CONTROL_BRANCH = 'pro/dg16-g1-g3-control-32-20261114'

CONTROL_PATH = 'qualification/dg16-r5-g3/ROOT_DECISION.json'

FINAL_CONTROL_PATH = 'qualification/dg16-r5-g3/ORIGINAL_DECISION.json'

ROOT, PHASE, JOIN = 'R5_ROOT', 'DG16_CURRENT', 'DG16_COMPONENT_JOIN'

PAIR, SCOPE = 'G1_ORIGINAL_PAIR', 'HOST_SCOPE_RECEIVING'

SELECTED = [PAIR, SCOPE]

OWNER_ARRANGEMENT = 'SELECTIVE_PARALLEL_EXISTING_OWNERS_DG16_SOLE_SHARED_WRITER'

NATURAL_SCOPE = 'ORIGINAL_RLGWO_PREREQUISITE_AND_NATURAL_SHAPE_NOT_RECEIVED'

SCOPE_INPUT_NAMES = ('SOURCE_ACQUISITION.json', 'PACKAGE_ROOT_RECEIVING.json', 'PACKAGE_BODY_RECEIVING.json', 'PACKAGE_TERMINAL_RECEIVING.json')

NATIVE_PREDICATES = ('fixed_receiver_identity', 'wrong_receiver_refusal', 'current_native_intake', 'later_invalidation_refusal', 'host_and_diagnosed_intake')

NATIVE_PREREQUISITE_PROFILE = 'DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1'

C5_ENTRYPOINT = 'GenuineC5Session'

C5_SOURCE_REVISION = 'R5_HOSTED_UBUNTU24_RUNTIME_DIRECTORY_MODE_SOURCE_20261110_V8'

ORIGINAL = 'DG16_ORIGINAL48_WITH_GUARDED_EXTERNAL_INTERFACES'

BEFORE = 'WAITING_FOR_G1_AND_HOST_SCOPE'

AFTER = 'SCOPED_RETURNS_RETAINED_ORIGINAL_CELL_OPEN'

FILE_LIMIT, TOTAL_LIMIT, ENTRY_LIMIT, DEPTH_LIMIT = 16*1024**2, 64*1024**2, 4096, 16

PUBLIC_LIMIT, REQUEST_LIMIT, DECISION_LIMIT = 24576, 8192, 8192

HOLD_SECONDS, POLL_SECONDS, POLL_COUNT, HTTP_SECONDS = 600, 10, 60, 8

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
             'RETIREMENT_OR_TRANSFER_UNPERFORMED', 'AUTHORITATIVE_V041_ADMISSION_PENDING',
             'NATURAL_RLGWO_PREREQUISITE_UNRECEIVED')

FINAL_PROOF_KEYS = ('g1_receiving', 'g1_preboundary_inputs', 'scope_receiving', 'initial_native', 'dispatch', 'transition', 'join',
    'root_consumption', 'recursive_records', 'final_native', 'final_transition', 'stale_return',
    'missing_return', 'negative_applicability', 'module')

M4_PINS = {
    'M4_ROOT_RECEIVING.json': {'bytes': 33448, 'sha256': '2915fe9d6723ad9c745906d763d1de5818de7f4ae79db3bba196b5d8d678d0db'},
    'M4_INDEPENDENT_REPORT.md': {'bytes': 11997, 'sha256': '8e9b1b2e565019dc72f7e64f8e59386c9b364b0dbd009941d188f9e41c6e6417'},
    'M4_INDEPENDENT_RESULT.json': {'bytes': 78141, 'sha256': '23de2fa62d080ba20e79bb8599211ffdf7f6d479d76e4d701260938e27bc4da0'},
    'M4_FINAL_CHECK.json': {'bytes': 1201, 'sha256': 'eb070f91d6c0923bd51604132dc2763ed00a08eb495aa5ddde293082a67e1689'},
}

ORIGINAL_L04_TEXT = ('Held-out positive has completed comparison inputs, genuinely blocked admission/effect, '
    'independent useful preparation with met actual prerequisites, and an ancestor future qualification/JOIN '
    'prerequisite. Show actual selected bounded work and a consumed decision-changing return while the blocked effect remains blocked.')

ORIGINAL_L04_BINDING = 'P simulated/portable test consumer can qualify its declared scope; NATIVE remains for one natural material campaign transition. [L, E]'

M4_DECISION = 'ACCEPT_ORIGINAL_M4_L04_NATIVE_NATURAL_TRANSITION_AT_DECLARED_EPISODE'

def descriptor(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def receive_exact_m4(bodies):
    """Receive an immutable accepted historical fact. No new acceptance follows."""
    need(type(bodies) is dict and set(bodies) == set(M4_PINS), 'M4_EXACT_BODY_POPULATION')
    for name, pin in M4_PINS.items():
        raw = bodies[name]
        need(type(raw) is bytes, 'M4_BODY_TYPE')
        need(descriptor(raw) == pin, 'M4_BODY_PIN')
    root = parse(bodies['M4_ROOT_RECEIVING.json'])
    need(root['schema'] == 'implementaudit.Root-original-scope-receiving.v1'
         and root['decision'] == M4_DECISION and root['receiver'] == '/root'
         and root['operation'] == 'M4' and root['criterion'] == 'R35-L04'
         and type(root['actual_run']) is int and root['actual_run'] == 44076469956
         and root['launch_commit'] == '5d8bd6aa60b7490788b1905e2dec14701fdcef35'
         and root['root_consumption_commit'] == '1fa59671a71f3c3f22c70aa2918d02125ab98bd7',
         'M4_ORIGINAL_ACCEPTED_SUBJECT')
    need(root['original_text'] == ORIGINAL_L04_TEXT and root['original_scope_and_binding'] == ORIGINAL_L04_BINDING
         and root['missing_original_M4_predicates_at_episode'] == [] and root['required_M4_rerun'] is False,
         'M4_ORIGINAL_REQUIREMENT_CHANGED')
    need(root['G132'] == 'UNKNOWN_NO_REPLAY' and root['ancestor_JOIN'] == 'BLOCKED'
         and root['Q06_whole_award'] is False and root['audit_complete'] is False
         and root['native_Stop_acceptance'] is False and root['other_operation_awards'] == [],
         'M4_RESERVED_SCOPE_CHANGED')
    for key, name in (('review', 'M4_INDEPENDENT_REPORT.md'), ('result', 'M4_INDEPENDENT_RESULT.json'),
                      ('final_check', 'M4_FINAL_CHECK.json')):
        need({k: root[key][k] for k in ('bytes', 'sha256')} == M4_PINS[name], 'M4_ROOT_SUPPORT_JOIN')
    return {
        'schema': 'g132.prospective-retained-m4-input-receiving.v1', 'authority': 'NONE',
        'criterion': 'R35-L04', 'original_scope': ORIGINAL_SCOPES[4], 'prior_accepted_run': '44076469956',
        'prior_root_decision': M4_DECISION, 'bodies': {k: dict(v) for k, v in M4_PINS.items()},
        'missing_predicates_at_prior_episode': [], 'required_m4_rerun': False,
        'currentness_transfer': False, 'new_acceptance': False, 'g132': 'UNKNOWN_NO_REPLAY',
        'source_applicability_and_live_root_decision_required_for_new_consumer': True,
    }

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

def scope_basis():
    raw = current_original_scope_body()
    need(sha(raw) == SCOPE_SHA, 'ORIGINAL_SCOPE_PIN')
    value = parse(raw)
    need(value.get('schema') == 'dg16.g3-retained-original-population.v3'
         and value['original_population'] == dict(DG16=48, DG17=95, DG18=14, total=157)
         and type(value['new_original_awards']) is int and value['new_original_awards'] == 0
         and value['scheduling_authority'] == OWNER_ARRANGEMENT
         and value['native_original_scope'] == ORIGINAL and value['natural_transition'] == NATURAL_SCOPE
         and value['current_subject'] == dict(commit=SOURCE_COMMIT, tree=SOURCE_TREE), 'ORIGINAL_POPULATION')
    for cell, size in (('DG16', 48), ('DG17', 95), ('DG18', 14)):
        ids = value['original_ids'][cell]
        need(type(ids) is list and len(ids) == size and len(set(ids)) == size
             and all(type(x) is str and 3 <= len(x) <= 64 and re.fullmatch(r'[A-Z0-9][A-Z0-9_-]*(?:/[A-Z0-9][A-Z0-9_-]*)*', x) for x in ids), 'ORIGINAL_ID_POPULATION')
    exact(value['received_inputs'], SCOPE_INPUT_NAMES, 'CURRENT_SCOPE_INPUT_POPULATION')
    for row in value['received_inputs'].values():
        exact(row, ('bytes', 'sha256'))
        integer(row['bytes'], 1, FILE_LIMIT); digest(row['sha256'])
    return raw, value

def policy(run):
    return dict(schema='dg16.g3-prospective-policy.v2',source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,
        source_parent=SOURCE_PARENT,run_id=run,attempt=1,original_scope_sha256=SCOPE_SHA,
        capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS',host_capacity=2,
        operator_ceiling=2,reserve=0,active_owned_task_slots=0,
        execution_order=['HOST_SCOPE_RECEIVING_BEFORE_TIMED_C5','G1_ORIGINAL_PAIR'],
        independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',
        input_limits=dict(file_bytes=FILE_LIMIT,total_bytes=TOTAL_LIMIT,entries=ENTRY_LIMIT,depth=DEPTH_LIMIT),
        full_source_reader='MAINTAINED_GENUINE_C5_SESSION_ACQUIRE_WITH_UNCHANGED_BOUNDS',
        selected_tracked_source_files=SOURCE_FILES,selected_tracked_source_bytes=SOURCE_BYTES,
        original_awards=0,full_g2=False,owner_arrangement=OWNER_ARRANGEMENT,
        natural_transition=NATURAL_SCOPE,c5_entrypoint=C5_ENTRYPOINT,c5_source_revision=C5_SOURCE_REVISION,
        timing_scope='PRODUCER_WATCHDOG120_CPU90_ENCLOSING_INTERVAL_MEASURED_SEPARATELY_NO_SUBTRACTION')

def validate_public_scope(raw):
    value = parse(raw,PUBLIC_LIMIT)
    exact(value,('schema','authority','source_commit','source_tree','run_id','attempt',
        'graph_sha256','dispatch_sha256','original_scope_sha256','complete_input_key',
        'selected_tracked_source_files','selected_tracked_source_bytes','scope_obligations','ancestors',
        'actual_complete_source_files','actual_complete_source_bytes','selected','required_join','root','node_count',
        'original_total','observed_affinity_count','capacity_units','host_capacity','operator_ceiling','reserve',
        'active_owned_task_slots','independence','owner_arrangement','received_input_bodies','natural_transition',
        'full_g2','original_awards','future_adoption','result','root_decision_before'))
    need(value['schema'] == 'dg16.g3-host-scope-receiving.v2' and value['authority'] == 'NONE'
         and value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE, 'PUBLIC_SCOPE_IDENTITY')
    need(type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}',value['run_id'])
         and type(value['attempt']) is int and value['attempt'] == 1, 'PUBLIC_SCOPE_RUN')
    for key in ('graph_sha256','dispatch_sha256','complete_input_key'): digest(value[key])
    need(value['original_scope_sha256'] == SCOPE_SHA and value['selected_tracked_source_files'] == SOURCE_FILES
         and value['selected_tracked_source_bytes'] == SOURCE_BYTES and value['original_total'] == 157
         and value['node_count'] == 14, 'PUBLIC_SCOPE_POPULATION')
    integer(value['observed_affinity_count'],2,4096)
    integer(value['actual_complete_source_files'],SOURCE_FILES,4096)
    integer(value['actual_complete_source_bytes'],SOURCE_BYTES,256*1024**2)
    expected = policy(value['run_id'])
    for key in ('capacity_units','host_capacity','operator_ceiling','reserve','active_owned_task_slots','independence','owner_arrangement'):
        need(type(value[key]) is type(expected[key]) and value[key] == expected[key], 'PUBLIC_SCOPE_POLICY')
    basis = scope_basis()[1]
    need(value['received_input_bodies'] == {name:row['sha256'] for name,row in basis['received_inputs'].items()}
         and value['natural_transition'] == NATURAL_SCOPE, 'PUBLIC_CURRENT_INPUT_SCOPE')
    need(value['selected'] == SELECTED and value['ancestors'] == [PAIR,PHASE,ROOT] and value['required_join'] == JOIN
         and value['root'] == ROOT and type(value['original_awards']) is int and value['original_awards'] == 0
         and value['full_g2'] == 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
         and value['future_adoption'] == 'SEPARATE_GUARDED_RECEIVING_AND_OWNER_DECISION'
         and value['root_decision_before'] == BEFORE and value['result'] == 'HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED', 'PUBLIC_SCOPE_CREDIT')
    required = (('DG16','DG16_ORIGINAL_RECEIVING','ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS'),
                ('DG17','DG17_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE057_INTERFACE_ONLY'),
                ('DG18','DG18_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE051_CHANGED_INPUT_ONLY'))
    need(type(value['scope_obligations']) is list and len(value['scope_obligations']) == 3, 'PUBLIC_OBLIGATION_POPULATION')
    for row,(cell,consumer,condition) in zip(value['scope_obligations'],required):
        exact(row,('cell','count','original_ids_sha256','consumer','condition','state'))
        need(row == dict(cell=cell,count=basis['original_population'][cell],original_ids_sha256=sha(encode(basis['original_ids'][cell])),
                         consumer=consumer,condition=condition,state='RETAINED_SCOPE_NOT_EXECUTED_BY_THIS_HOST'), 'PUBLIC_OBLIGATION_BINDING')
    need(encode(value) == raw, 'PUBLIC_CANONICAL_BYTES')
    return value

def validate_public_request(raw):
    value = parse(raw, REQUEST_LIMIT)
    exact(value, ('schema', 'authority', 'source_commit', 'source_tree', 'source_parent', 'run_id', 'attempt',
        'nonce', 'control_branch', 'control_path', 'root', 'join', 'original_scope_sha256', 'graph_sha256',
        'dispatch_sha256', 'transition_sha256', 'join_sha256', 'scope_return_sha256', 'g1_return_sha256',
        'complete_input_key', 'returned_nodes', 'issued_unix_ms', 'expires_unix_ms', 'hold_seconds',
        'shared_expires_unix_ms', 'shared_window_seconds',
        'decision_before', 'decision_after', 'original_total', 'original_awards', 'full_g2', 'status'))
    need(value['schema'] == 'dg16.g3-root-consumption-request.v2' and value['authority'] == 'NONE'
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

def validate_decision(raw, request, request_sha, now_unix_ms):
    value = parse(raw, DECISION_LIMIT)
    exact(value, ('schema', 'issuer', 'successor', 'action', 'request_sha256', 'run_id', 'attempt', 'nonce',
        'source_commit', 'source_tree', 'graph_sha256', 'dispatch_sha256', 'join_sha256', 'outputs',
        'consumed_nodes', 'decision_before', 'decision_after', 'owner_arrangement', 'full_g2',
        'original_awards', 'issued_unix_ms', 'expires_unix_ms'))
    need(value['schema'] == 'dg16.g3-root-consumption-decision.v2' and value['issuer'] == 'R5_ROOT_GOVERNOR' and value['successor'] == 'PRO-EXECUTOR-01, designated by owner'
         and value['action'] == 'CONSUME_COMPONENT_RETURNS_ONLY' and value['request_sha256'] == digest(request_sha),
         'ROOT_DECISION_ACTION_OR_REQUEST')
    for key in ('run_id', 'attempt', 'nonce', 'source_commit', 'source_tree', 'graph_sha256',
                'dispatch_sha256', 'join_sha256', 'decision_before', 'decision_after', 'full_g2', 'expires_unix_ms'):
        need(type(value[key]) is type(request[key]) and value[key] == request[key], 'ROOT_DECISION_BINDING')
    need(value['outputs'] == {PAIR:request['g1_return_sha256'], SCOPE:request['scope_return_sha256']}
         and value['consumed_nodes'] == SELECTED and value['owner_arrangement'] == OWNER_ARRANGEMENT
         and type(value['original_awards']) is int and value['original_awards'] == 0, 'ROOT_DECISION_SCOPE')
    issued = integer(value['issued_unix_ms'], request['issued_unix_ms'], request['expires_unix_ms'])
    need(issued <= now_unix_ms < request['expires_unix_ms'], 'ROOT_DECISION_EXPIRED_OR_FUTURE')
    need(encode(value) == raw, 'ROOT_DECISION_CANONICAL_BYTES')
    return value

def validate_g1_facts(value):
    exact(value, ('schema','source_commit','source_tree','native_prerequisite_profile','native_prerequisite_receiving_sha256',
        'native_predicates','native_prerequisite_scope',
        'raw_receiving_sha256','actual_dispatches','validated_actual_events','retained_artifacts','original_children_exit_codes',
        'producer_closing_sha256','maintained_elapsed_ns','enclosing_elapsed_ns','zero_subtracted_ns','producer_watchdog_seconds',
        'per_process_cpu_seconds','watchdog_events','cleanup_errors','wait4_reaped','process_group_absent',
        'measured_outer_wait4_max_rss_kib','max_rss_scope','runtime_mounted_bytes','runtime_unique_bytes','runtime_logical_bytes',
        'actual_source_files','actual_source_bytes','runtime_physical_limit_bytes','source_acquisition_limit_bytes',
        'image_readback','operation_scope','producer_original48_qualification','whole_DG16_awarded'))
    need(value['schema'] == 'dg16.g3-g1-actual-facts.v2' and value['source_commit'] == SOURCE_COMMIT
         and value['source_tree'] == SOURCE_TREE and value['original_children_exit_codes'] == [0,0]
         and all(type(x) is int for x in value['original_children_exit_codes']), 'FINAL_G1_FACT_IDENTITY')
    for key in ('native_prerequisite_receiving_sha256','raw_receiving_sha256','producer_closing_sha256'):
        digest(value[key])
    for key,expected in dict(actual_dispatches=2,validated_actual_events=38,retained_artifacts=12,
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
    need(value['native_prerequisite_profile'] == NATIVE_PREREQUISITE_PROFILE
         and value['native_predicates'] == list(NATIVE_PREDICATES)
         and value['native_prerequisite_scope'] == 'ACTUALLY_CONSUMED_G0001_PREDICATES'
         and value['wait4_reaped'] is True and value['process_group_absent'] is True
         and value['max_rss_scope'] == 'ACTUAL_OUTER_WAIT4_OBSERVATION_NOT_WINDOWS_WHOLE_JOB'
         and value['image_readback'] == 'COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES'
         and value['operation_scope'] == 'PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR'
         and value['producer_original48_qualification'] is False and value['whole_DG16_awarded'] is False,
         'FINAL_G1_FACT_SCOPE')
    return value

def validate_public_final_request(raw, *, retained_bodies=None):
    value = parse(raw,16384)
    exact(value,('schema','authority','source_commit','source_tree','source_parent','run_id','attempt','nonce',
        'control_branch','control_path','original_scope_sha256','initial_request_sha256','proofs','initial_graph_sha256',
        'final_graph_sha256','continuity_generation','current_receipt_sha256','component_return_nodes','consumed_join','root',
        'actual_stale_result','final_selected','original_ids','original_scopes','g1_facts','retained_original_total',
        'g1_input_scope','g1_complete_input_key','g3_current_scope','input_change_reason',
        'actual_original_awards','original_scope','v041_admission','global_liveness','retirement_or_transfer',
        'full_g2','whole_DG16_awarded','shared_window_started_unix_ms','issued_unix_ms','expires_unix_ms',
        'shared_window_seconds','status','retained_m4'))
    need(value['schema']=='dg16.g3-original-receiving-request.v3' and value['authority']=='NONE'
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
    need(encode(value['retained_m4']) == encode(receive_exact_m4(retained_bodies)), 'FINAL_RETAINED_M4_BINDING')
    need(encode(value)==raw,'PUBLIC_CANONICAL_BYTES')
    return value

def validate_row_decisions(rows, gates, *, retained_bodies=None):
    """Prospective source rule only; caller still needs the actual final consumer.

    All original scopes and the full-G3 conjunction remain exact. A retained M4
    input qualifies only the L04 evidence branch, never Q06 or current G1/G3.
    """
    retained = receive_exact_m4(retained_bodies) if retained_bodies is not None else None
    need(type(rows) is list and len(rows) == len(ORIGINAL_IDS), 'FINAL_ORIGINAL_ROW_POPULATION')
    for row, name, scope in zip(rows, ORIGINAL_IDS, ORIGINAL_SCOPES):
        exact(row, ('id', 'scope', 'disposition', 'evidence', 'residuals'))
        permitted_proofs = FINAL_PROOF_KEYS + (('retained_m4_receiving',) if name == 'R35-L04' else ())
        need(row['id'] == name and row['scope'] == scope and row['disposition'] in DISPOSITIONS
             and type(row['evidence']) is list and 1 <= len(row['evidence']) <= len(permitted_proofs)
             and len(row['evidence']) == len(set(row['evidence']))
             and all(k in permitted_proofs for k in row['evidence'])
             and type(row['residuals']) is list and 1 <= len(row['residuals']) <= len(RESIDUALS)
             and len(row['residuals']) == len(set(row['residuals']))
             and all(k in RESIDUALS for k in row['residuals']), 'FINAL_ORIGINAL_ROW_SCOPE')
        need(row['disposition'] != 'NOT_RECEIVED' or 'NONE_AT_DECLARED_SCOPE' not in row['residuals'],
             'FINAL_UNRECEIVED_RESIDUAL')
        if name == 'R35-L04':
            if 'retained_m4_receiving' in row['evidence']:
                need(retained is not None, 'EXACT_RETAINED_M4_REQUIRED')
            if row['disposition'] == 'ACCEPTED_AT_DECLARED_SCOPE':
                need(retained is not None, 'EXACT_RETAINED_M4_REQUIRED')
                need('retained_m4_receiving' in row['evidence'], 'M4_EXPLICIT_EVIDENCE_REQUIRED')
                need(row['residuals'] == ['NONE_AT_DECLARED_SCOPE'], 'M4_ACCEPTED_EPISODE_RESIDUAL_CONTRADICTION')
            else:
                need('NATURAL_RLGWO_PREREQUISITE_UNRECEIVED' in row['residuals'], 'NATURAL_RLGWO_SCOPE_NOT_ESTABLISHED')
        if name == 'R35-L07':
            need('GLOBAL_LIVENESS_UNPROVED' in row['residuals'] and 'RETIREMENT_OR_TRANSFER_UNPERFORMED' in row['residuals'],
                 'L07_STRONGER_CLAIM_MUST_REMAIN_SEPARATE')
    exact(gates, ('G1', 'G3'))
    for name, scope in (('G1', 'PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR'),
                        ('G3', 'EXACT_Q06_AND_L01_TO_L07_DECLARED_SCOPES')):
        row = gates[name]
        exact(row, ('scope', 'disposition', 'evidence'))
        need(row['scope'] == scope and row['disposition'] in DISPOSITIONS and type(row['evidence']) is list
             and 1 <= len(row['evidence']) <= len(FINAL_PROOF_KEYS)
             and len(set(row['evidence'])) == len(row['evidence'])
             and all(k in FINAL_PROOF_KEYS for k in row['evidence']), 'FINAL_GATE_DECISION_SCOPE')
    if gates['G3']['disposition'] == 'ACCEPTED_AT_DECLARED_SCOPE':
        need(all(row['disposition'] == 'ACCEPTED_AT_DECLARED_SCOPE' for row in rows),
             'PARTIAL_ROWS_CANNOT_GRANT_COMPLETE_G3_SCOPE')
    return {'schema': 'g132.prospective-final-row-validation.v1', 'authority': 'NONE',
            'status': 'PROSPECTIVE_ROW_FORMAT_AND_RETAINED_JOIN_VALIDATED',
            'retained_m4': retained, 'original_consumer_executed': False, 'live_g1_or_g3_proven': False,
            'new_awards': [], 'hosted_integration_review_and_fresh_binding_required': True}

def validate_final_decision(raw,request,request_sha,now_unix_ms, *, retained_bodies=None):
    value=parse(raw,16384)
    exact(value,('schema','issuer','successor','action','request_sha256','run_id','attempt','nonce','source_commit','source_tree',
        'final_graph_sha256','current_receipt_sha256','proofs','independent_review_sha256','source_applicability_review_sha256',
        'original_rows','gate_decisions','whole_DG16_awarded','full_g2','v041_admission','global_liveness',
        'retirement_or_transfer','issued_unix_ms','expires_unix_ms','retained_m4'))
    need(value['schema']=='dg16.g3-root-original-decision.v3' and value['issuer']=='R5_ROOT_GOVERNOR' and value['successor']=='PRO-EXECUTOR-01, designated by owner'
         and value['action']=='RECEIVE_EXACT_ORIGINAL_IDS_AND_GATES' and value['request_sha256']==digest(request_sha),
         'FINAL_ROOT_DECISION_ACTION')
    for key in ('run_id','attempt','nonce','source_commit','source_tree','final_graph_sha256','current_receipt_sha256',
                'proofs','expires_unix_ms'):
        need(type(value[key]) is type(request[key]) and value[key]==request[key],'FINAL_ROOT_DECISION_BINDING')
    digest(value['independent_review_sha256']);digest(value['source_applicability_review_sha256'])
    need(encode(value['retained_m4']) == encode(request['retained_m4']) == encode(receive_exact_m4(retained_bodies)), 'FINAL_RETAINED_M4_BINDING')
    validate_row_decisions(value['original_rows'],value['gate_decisions'], retained_bodies=retained_bodies)
    need(value['whole_DG16_awarded'] is False and value['full_g2']=='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
         and value['v041_admission']=='PENDING_NOT_GRANTED_BY_THIS_EPISODE' and value['global_liveness']=='NOT_ESTABLISHED'
         and value['retirement_or_transfer']=='NOT_PERFORMED','FINAL_ROOT_RESERVED_CONJUNCTION')
    issued=integer(value['issued_unix_ms'],request['issued_unix_ms'],request['expires_unix_ms'])
    need(issued<=now_unix_ms<request['expires_unix_ms'],'FINAL_ROOT_DECISION_EXPIRED_OR_FUTURE')
    need(encode(value)==raw,'ROOT_DECISION_CANONICAL_BYTES')
    return value

def validate_original_receipt(raw, *, retained_bodies=None):
    value=parse(raw,16384)
    exact(value,('schema','authority','source_commit','source_tree','run_id','attempt','request_sha256',
        'decision_sha256','control_commit','current_graph_sha256','current_receipt_sha256',
        'independent_review_sha256','source_applicability_review_sha256','original_rows','gate_decisions',
        'whole_DG16_awarded','full_g2','status','automatic_awards','retained_m4'))
    need(value['schema']=='dg16.g3-root-original-decision-retained.v3'
         and value['authority']=='ROOT_GOVERNOR_RECORDED_DECISION'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
         and type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}',value['run_id'])
         and type(value['attempt']) is int and value['attempt']==1
         and type(value['control_commit']) is str and re.fullmatch('[0-9a-f]{40}',value['control_commit']),
         'ORIGINAL_RECEIPT_IDENTITY')
    for key in ('request_sha256','decision_sha256','current_graph_sha256','current_receipt_sha256',
                'independent_review_sha256','source_applicability_review_sha256'):
        digest(value[key])
    need(encode(value['retained_m4']) == encode(receive_exact_m4(retained_bodies)), 'FINAL_RETAINED_M4_BINDING')
    validate_row_decisions(value['original_rows'],value['gate_decisions'], retained_bodies=retained_bodies)
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

REFUSAL_CODES = frozenset(('ACTUAL_COMPLETE_INPUT_CONSUMER_REQUIRED', 'ACTUAL_G1_RECEIVING_CONJUNCTION', 'ACTUAL_G1_RESULT_CONJUNCTION', 'ACTUAL_JOIN_REFUSED', 'ACTUAL_NATIVE_BINDING', 'ACTUAL_NATIVE_PREREQUISITE_RECEIVER_BINDING', 'ACTUAL_NATIVE_PREREQUISITE_RECEIVER_REQUIRED', 'ACTUAL_NATIVE_SCOPE', 'ACTUAL_OWNED_ROOT_REQUIRED', 'ACTUAL_PRODUCER_SCOPE_OR_SELECTED_INPUTS', 'ACTUAL_RAW_RECEIVER_CALLBACK_REQUIRED', 'ACTUAL_RAW_RECEIVER_RETURN_BINDING', 'ACTUAL_ROOT_CUSTODY_REQUIRED', 'ACTUAL_SCOPE_RETURN_IDENTITY', 'ACTUAL_STALE_RETURN_NOT_REFUSED', 'ADVERSE_APPLICABILITY_PIN', 'ADVERSE_APPLICABILITY_SCOPE', 'ANCESTOR_CREDIT_REFUSED', 'CANONICAL_FENCE_POPULATION', 'CANONICAL_FILE_BOUND', 'CANONICAL_OPEN_CHANGED', 'CANONICAL_PREIMAGE_CHANGED', 'CANONICAL_READBACK', 'CANONICAL_TOTAL_BOUND', 'COMPILER_LOAD_CHANGED', 'COMPILER_PIN', 'COMPLETE_ACQUISITION_KEY', 'COMPLETE_ACQUISITION_SUBJECT', 'COMPLETE_INPUTS_CHANGED', 'CONSUMED_NATIVE_PREREQUISITE_CHANGED', 'CONTROL_COMMIT_SHAPE', 'CONTROL_HTTP_BOUND', 'CONTROL_HTTP_REFUSED', 'CONTROL_HTTP_RESPONSE', 'CONTROL_REDIRECT_REFUSED', 'CONTROL_REF_SHAPE', 'CONTROL_TRANSPORT_REFUSED', 'CURRENT_ACQUISITION_FIELDS', 'CURRENT_C5_EXECUTION_SOURCE_BINDINGS', 'CURRENT_CUMULATIVE_DELTA_SCOPE', 'CURRENT_MANIFEST_BODY_BINDING', 'CURRENT_MANIFEST_POPULATION', 'CURRENT_MANIFEST_SOURCE_SCOPE', 'CURRENT_NATIVE_PREREQUISITE_BINDING', 'CURRENT_NATIVE_PREREQUISITE_POPULATION', 'CURRENT_NATIVE_PREREQUISITE_UNRECEIVED', 'CURRENT_PACKAGE_IDENTITY_RELATION', 'CURRENT_PACKAGE_INPUT_RECEIVING', 'CURRENT_ROOT_SOURCE_EVIDENCE', 'CURRENT_SCOPE_INPUT_BODY_CHANGED', 'CURRENT_SCOPE_INPUT_POPULATION', 'CURRENT_SOURCE_INPUT_RECEIVING', 'DECLARED_INPUT_AGGREGATE', 'DIAGNOSTIC_BOOLEAN', 'DIAGNOSTIC_BOUND', 'DIAGNOSTIC_CANONICAL_BYTES', 'DIAGNOSTIC_CATEGORY', 'DIAGNOSTIC_CODE', 'DIAGNOSTIC_EFFECT', 'DIAGNOSTIC_EFFECT_CONTRADICTION', 'DIAGNOSTIC_FLAG_CONTRADICTION', 'DIAGNOSTIC_MILESTONE', 'DIAGNOSTIC_ORIGINAL_SCOPE', 'DIAGNOSTIC_PHASE', 'DIAGNOSTIC_SCHEMA', 'DIAGNOSTIC_UNEARNED_ROOT_DECISION', 'DIGEST_SHAPE', 'DUPLICATE_JSON_KEY', 'EFFECT_ALREADY_STARTED', 'ENCLOSING_DEADLINE', 'EXACT_RETAINED_M4_REQUIRED', 'EXTERNAL_OWNER_SCOPE_CHANGED', 'FILE_OPEN_CHANGED', 'FILE_READ_CHANGED', 'FINAL_G1_FACT_FIXED_BOUND', 'FINAL_G1_FACT_IDENTITY', 'FINAL_G1_FACT_SCOPE', 'FINAL_GATE_DECISION_SCOPE', 'FINAL_HELD_IDENTITY_OR_BINDING', 'FINAL_HELD_SUMMARY_BOUND', 'FINAL_INPUT_SCOPE_SEPARATION', 'FINAL_ORIGINAL_CURRENTNESS_OR_DEADLINE', 'FINAL_ORIGINAL_RAW_RECEIVING_CHANGED', 'FINAL_ORIGINAL_ROW_POPULATION', 'FINAL_ORIGINAL_ROW_SCOPE', 'FINAL_PROOF_POPULATION', 'FINAL_PUBLIC_AUTHORITY_SCOPE', 'FINAL_PUBLIC_CONTEXT', 'FINAL_PUBLIC_NATIVE_SCOPE', 'FINAL_PUBLIC_SHARED_DEADLINE', 'FINAL_PUBLIC_SOURCE_AND_ROUTE', 'FINAL_RETAINED_M4_BINDING', 'FINAL_ROOT_DECISION_ACTION', 'FINAL_ROOT_DECISION_BINDING', 'FINAL_ROOT_DECISION_EXPIRED_OR_FUTURE', 'FINAL_ROOT_RESERVED_CONJUNCTION', 'FINAL_UNRECEIVED_RESIDUAL', 'FIXED_SCOPE_READER_ENTRY_ONLY', 'FRESH_CONTROLLER_REQUIRED', 'FRESH_JOB_CONTEXT_REQUIRED', 'FRESH_RUN_ROOT_REQUIRED', 'G1_ACTUAL_ELAPSED_SHAPE', 'G1_ACTUAL_TERMINAL_CONJUNCTION', 'G1_RETURN_CHANGED_DURING_HOLD', 'G3_CURRENT_RECEIPT_DIFFERS', 'G3_INITIAL_GENERATION', 'G3_INVALIDATION_TOKEN', 'G3_MAINTAINED_OWNER_REFUSED', 'G3_NEW_RECEIPT_SHAPE', 'G3_NEW_RECEIPT_VERIFY', 'HELD_ANCESTRY_NOT_ORDINARY', 'HELD_IDENTITY_OR_BYTES_CHANGED', 'HELD_SUMMARY_AGGREGATE_BOUND', 'HOST_TASK_CAPACITY_UNAVAILABLE', 'INITIAL_NATIVE_GENERATION_REQUIRED', 'INSUFFICIENT_CUSTODY_FOR_ROOT_HOLD', 'INSUFFICIENT_SHARED_WINDOW_FOR_ORIGINAL_RECEIVING', 'INTEGER_BOUND', 'JOIN_DEPENDENCE_DECLARATION', 'JSON_BYTE_BOUND', 'L07_STRONGER_CLAIM_MUST_REMAIN_SEPARATE', 'LOCAL_SCOPE_OR_RESERVED_AUTHORITY_DROPPED', 'M4_ACCEPTED_EPISODE_RESIDUAL_CONTRADICTION', 'M4_BODY_PIN', 'M4_BODY_TYPE', 'M4_CANONICAL_DIRECTORY', 'M4_CLOSING_CHANGED', 'M4_DIRECTORY_CHANGED', 'M4_EXACT_BODY_POPULATION', 'M4_EXPLICIT_EVIDENCE_REQUIRED', 'M4_OPEN_CHANGED', 'M4_ORDINARY_OWNED_FILE', 'M4_ORIGINAL_ACCEPTED_SUBJECT', 'M4_ORIGINAL_REQUIREMENT_CHANGED', 'M4_OWNED_DIRECTORY', 'M4_RESERVED_SCOPE_CHANGED', 'M4_ROOT_SUPPORT_JOIN', 'MAINTAINED_COMPLETE_INPUTS_CHANGED', 'MAINTAINED_COMPLETE_INPUT_REACQUISITION_REQUIRED', 'MAINTAINED_COMPLETE_OBSERVATION_DIFFERS', 'MISSING_RETURN_NOT_PENDING', 'NATURAL_RLGWO_SCOPE_NOT_ESTABLISHED', 'NONFINITE_JSON', 'ORDINARY_FILE_BOUND', 'ORIGINAL_DECISION_ALREADY_RESERVED', 'ORIGINAL_ID_POPULATION', 'ORIGINAL_POPULATION', 'ORIGINAL_RECEIPT_IDENTITY', 'ORIGINAL_RECEIPT_SCOPE', 'ORIGINAL_SCOPE_PIN', 'PACKAGE_DEPENDENCY_POPULATION_CHANGED', 'PACKAGE_DEPENDENCY_SCOPE', 'PACKAGE_EVIDENCE_ACTUAL_BODY_CHANGED', 'PACKAGE_EVIDENCE_BODY_TYPE', 'PACKAGE_EVIDENCE_POPULATION', 'PACKAGE_PRODUCER_POPULATION', 'PARTIAL_ROWS_CANNOT_GRANT_COMPLETE_G3_SCOPE', 'POST_JOIN_ANCESTOR_OR_SIBLING_CREDIT', 'POST_JOIN_FRONTIER_REFUSED', 'PREACTIVATION_ONLY', 'PRIVATE_HOLD_BINDING', 'PRIVATE_OUTPUT_BOUND', 'PRIVATE_OUTPUT_READBACK', 'PRIVATE_SOURCE_SEPARATION', 'PROSPECTIVE_SELECTION_DIFFERS', 'PUBLIC_CANONICAL_BYTES', 'PUBLIC_CURRENT_INPUT_SCOPE', 'PUBLIC_OBLIGATION_BINDING', 'PUBLIC_OBLIGATION_POPULATION', 'PUBLIC_REQUEST_HOLD', 'PUBLIC_REQUEST_IDENTITY', 'PUBLIC_REQUEST_ROUTE', 'PUBLIC_REQUEST_SCOPE', 'PUBLIC_REQUEST_SOURCE', 'PUBLIC_SCOPE_CREDIT', 'PUBLIC_SCOPE_IDENTITY', 'PUBLIC_SCOPE_POLICY', 'PUBLIC_SCOPE_POPULATION', 'PUBLIC_SCOPE_RUN', 'RECURSIVE_RECORD_CONSUMPTION_REFUSED', 'RECURSIVE_SELECTION_DIFFERS', 'RETAINED_ARCHIVE_ACTUAL_COMPARISON', 'RETAINED_ARCHIVE_ENTRY_SCOPE', 'RETAINED_ARCHIVE_POPULATION', 'RETAINED_PACKAGE_BODY_BINDING', 'RETAINED_PACKAGE_RELATION_FIELDS', 'RETAINED_PACKAGE_RELATION_SCOPE', 'ROOT_CONSUMPTION_ALREADY_RESERVED', 'ROOT_DECISION_ACTION_OR_REQUEST', 'ROOT_DECISION_BINDING', 'ROOT_DECISION_CANONICAL_BYTES', 'ROOT_DECISION_EXPIRED_OR_FUTURE', 'ROOT_DECISION_SCOPE', 'ROOT_HOLD_EXPIRED', 'ROOT_HOLD_POLL_BOUND', 'ROOT_JOIN_CHANGED_DURING_HOLD', 'RUN_ID_SHAPE', 'SCOPE_PROCESS_BINDING', 'SCOPE_PROCESS_REFUSED', 'SELECTED_C5_CANONICAL_POPULATION', 'SELECTION_CHANGED_BEFORE_PAIR', 'SHARED_DECISION_WINDOW', 'SHARED_WRITER_NOT_ADMITTED', 'WHOLE_ROOT_POPULATION', 'WHOLE_SIBLING_BARRIER_FORBIDDEN', 'WORKER_ACTUAL_SOURCE_BINDING', 'WORKER_ACTUAL_SOURCE_CENSUS', 'WORKER_ADVERSE_INPUT_CHANGED', 'WORKER_COMPLETE_POPULATION', 'WORKER_CURRENT_RECEIVED_INPUT_PREREQUISITE', 'WORKER_INPUT_BINDING', 'WORKER_MAINTAINED_REDERIVATION', 'WORKER_ORIGINAL_CONSUMER_COVERAGE', 'WORKER_ORIGINAL_SCOPE_PIN'))
