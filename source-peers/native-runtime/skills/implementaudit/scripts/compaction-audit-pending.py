"""Existing owner generic nonprotected projection. Historical private selectors are excluded."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('_pending_h0_owner', HERE / 'host-session-binding.py')
CORE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CORE)
_observation_spec = importlib.util.spec_from_file_location('_compaction_result_observation', HERE / 'compaction-result-observation.py')
OBSERVATION = importlib.util.module_from_spec(_observation_spec)
_observation_spec.loader.exec_module(OBSERVATION)
SCHEMA = 'implementaudit.compaction-audit-pending.v1'
MAX_SOURCE = 8 * 1024 * 1024
MAX_ROWS = 4096
MAX_STATE = 8 * 1024 * 1024
CEILING = {'authority': 'NONE', 'canonical_currentness': False, 'recovery_authority': False, 'epoch_authority': False, 'effect_authority': False, 'independent_children': 'UNCHANGED', 'actual_child_result_consumer': 'UNQUALIFIED', 'same_failed_scope_retry': 'CONDITIONAL_UNQUALIFIED'}

class Refusal(ValueError):
    pass

def custody_refusal(reason):
    raise Refusal('HOST_CUSTODY_UNAVAILABLE: ' + reason)
CORE.fail = custody_refusal

def require(ok, reason):
    if not ok:
        raise Refusal(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(value):
    return hashlib.sha256(value).hexdigest()

def text(value):
    require(isinstance(value, str) and 0 < len(value) <= 1024 and all((ord(char) >= 32 for char in value)), 'INVALID_TEXT')
    return value

def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'DUPLICATE_JSON_KEY')
        value[key] = item
    return value

def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)

def physical(path, *, directory=False):
    path = Path(path)
    require(path.is_absolute() and path.absolute() == path.resolve(strict=True), 'SOURCE_PATH_ALIAS')
    for member in (path, *path.parents):
        info = member.lstat()
        require(not member.is_symlink() and (not getattr(info, 'st_file_attributes', 0) & 1024), 'SOURCE_REPARSE')
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'SOURCE_FILE_KIND')
    return path

def _scan_source_unheld(path, prefix=None, native_cli_version=None):
    """Check a finite source using one bounded record, not an in-memory transcript.

    The total work ceiling is the existing observation source-window budget.
    MAX_SOURCE remains the per-record limit; MAX_ROWS bounds retained boundary
    descriptors rather than unrelated transcript rows. No input is truncated.
    Embedded ordinals in the 0.155 profile are not physical line numbers.
    Nothing is published until framing, prefix and physical checks all pass.
    """
    path = physical(path)
    before = path.stat()
    require(0 < before.st_size <= OBSERVATION.MAX_TOTAL * OBSERVATION.MAX_RECORDS, 'SOURCE_TOTAL_BYTE_BOUND')
    if prefix is not None:
        require(type(prefix['prefix_bytes']) is int and 0 < prefix['prefix_bytes'] <= before.st_size, 'SOURCE_PREFIX_OR_PHYSICAL_ID_CHANGED')
    full_hash = hashlib.sha256()
    prefix_hash = hashlib.sha256()
    offset = 0
    number = 0
    summaries = []
    group = []
    retained = 0
    meta = None
    meta_sha = None
    version = None
    stamp = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    with path.open('rb') as stream:
        require(stamp(os.fstat(stream.fileno())) == stamp(before), 'SOURCE_CHANGED_DURING_READ')
        while True:
            wire = stream.readline(MAX_SOURCE + 1)
            if not wire:
                break
            require(len(wire) <= MAX_SOURCE, 'SOURCE_RECORD_BYTE_BOUND')
            require(offset + len(wire) <= before.st_size, 'SOURCE_CHANGED_DURING_READ')
            require(wire.endswith(b'\n') and b'\r' not in wire and (b'\x00' not in wire), 'SOURCE_PARTIAL_OR_UNSUPPORTED_WIRE')
            full_hash.update(wire)
            if prefix is not None and offset < prefix['prefix_bytes']:
                prefix_hash.update(wire[:min(len(wire), prefix['prefix_bytes'] - offset)])
            try:
                row = decode(wire)
            except RecursionError as exc:
                raise Refusal('SOURCE_JSON_DEPTH_BOUND') from exc
            require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'}, {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and (type(row.get('ordinal')) is int) and (row['ordinal'] >= 0) and isinstance(row.get('type'), str) and isinstance(row.get('payload'), dict), 'SOURCE_ROW_SHAPE')
            text(row['timestamp'])
            if number == 0:
                require(row['type'] == 'session_meta' and 'metadata' not in row, 'SOURCE_SESSION_META')
                meta = row['payload']
                meta_sha = digest(wire)
                version = meta.get('cli_version')
                require(version in ('0.153.4', '0.155.0-alpha.16') or (native_cli_version is not None and version == native_cli_version), 'SOURCE_SESSION_META')
            require(version != '0.153.4' or row['ordinal'] == number, 'SOURCE_ROW_SHAPE')
            descriptor = {'ordinal': row['ordinal'], 'offset': offset, 'bytes': len(wire), 'sha256': digest(wire)}
            if version == '0.155.0-alpha.16' or version == native_cli_version:
                descriptor.update(physical_line=number + 1, timestamp=row['timestamp'])
            kind = row['type']
            payload = row['payload']
            canonical_marker = kind == 'compacted' or (kind == 'event_msg' and payload.get('type') == 'context_compacted')
            corroborating = kind == 'response_item' and payload.get('type') in ('compaction', 'compaction_summary', 'context_compaction')
            if canonical_marker or corroborating:
                require('metadata' not in row, 'CLIENT_AUTHORED_COMPACT_MARKER')
                retained += 1
                require(retained <= MAX_ROWS, 'SOURCE_BOUNDARY_SUMMARY_BOUND')
                group.append({**descriptor, 'kind': kind, 'canonical': canonical_marker})
            elif group and (kind == 'turn_context' or (kind == 'event_msg' and payload.get('type') == 'task_started')):
                require('metadata' not in row and isinstance(payload.get('turn_id'), str) and payload['turn_id'], 'RESUME_IDENTITY_UNAVAILABLE')
                retained += 1
                require(retained <= MAX_ROWS, 'SOURCE_BOUNDARY_SUMMARY_BOUND')
                summaries.append({'markers': group, 'resume': descriptor, 'resume_turn': text(payload['turn_id'])})
                group = []
            offset += len(wire)
            number += 1
        opened = os.fstat(stream.fileno())
    after = physical(path).stat()
    require(stamp(before) == stamp(opened) == stamp(after) and offset == before.st_size, 'SOURCE_CHANGED_DURING_READ')
    identity = {'device': before.st_dev, 'inode': before.st_ino}
    if prefix is not None:
        require(identity == prefix['physical'] and meta_sha == prefix['session_meta_sha256'] and (prefix_hash.hexdigest() == prefix['prefix_sha256']), 'SOURCE_PREFIX_OR_PHYSICAL_ID_CHANGED')
    return {'bytes': offset, 'sha256': full_hash.hexdigest(), 'physical': identity, 'metadata': meta, 'metadata_sha256': meta_sha, 'summaries': summaries, 'unresumed_marker': bool(group)}

def source_identity(source):
    return {key: source[key] for key in ('path', 'task_id', 'session_id', 'session_meta_sha256', 'physical', 'sessions_root')}

def source_registration(request, session):
    selected = _nonprotected_registration_selection(request, session)
    require(selected is not None, 'NONPROTECTED_SELECTED_ROOT_REQUIRED')
    return _nonprotected_source_registration(request, session, selected)

def state_path(store, session):
    return store / 'compaction-audits-v1' / CORE.session_key(session) / 'pending.json'

def blank(session):
    return {'schema': SCHEMA, 'session_id': session, 'revision': 0, 'source': None, 'source_problem': None, 'signals': 0, 'unresolved_signal_version': 0, 'observations': {}, 'assignments': {}, 'active_child': None, 'native_producer_runtime_equivalence': 'UNVERIFIED'}

def load(store, session):
    path = state_path(store, session)
    if not os.path.lexists(path):
        # A missing leaf under an alias is unavailable custody, not empty state.
        ancestor = path.parent
        while not os.path.lexists(ancestor):
            ancestor = ancestor.parent
        CORE.safe_existing_directory(str(ancestor), 'compaction audit pending state ancestor')
        return blank(session)
    info = path.lstat()
    if CORE.unsafe_file(info):
        CORE.fail('compaction audit pending state is not a safe regular file')
    require(info.st_size <= MAX_STATE, 'PENDING_STATE_BYTE_BOUND')
    CORE.safe_existing_directory(str(path.parent), 'compaction audit pending state')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if CORE.unsafe_file(opened):
            CORE.fail('compaction audit pending state is not a safe regular file')
        require((opened.st_dev, opened.st_ino) == (info.st_dev, info.st_ino), 'PENDING_STATE_CHANGED_DURING_READ')
        require(opened.st_size <= MAX_STATE, 'PENDING_STATE_BYTE_BOUND')
        # One admitted descriptor supplies the bounded UTF-8 buffer to decode.
        raw = bytearray()
        while len(raw) <= MAX_STATE:
            chunk = os.read(descriptor, min(65536, MAX_STATE + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        require(len(raw) <= MAX_STATE, 'PENDING_STATE_BYTE_BOUND')
    finally:
        os.close(descriptor)
    try:
        value = decode(raw.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        CORE.fail('compaction audit pending state is unreadable or malformed: ' + str(exc))
    if not isinstance(value, dict):
        CORE.fail('compaction audit pending state is not an object')
    require(set(blank(session)) <= set(value) <= set(blank(session)) | {'current_assignment', 'successor_stage', 'successor_assignment'} and value['schema'] == SCHEMA and (value['session_id'] == session) and (type(value['revision']) is int) and isinstance(value['observations'], dict) and isinstance(value['assignments'], dict), 'PENDING_STATE_SHAPE')
    return value

def save(store, state):
    require(len(canonical(state)) < MAX_STATE, 'PENDING_STATE_BYTE_BOUND')
    state['revision'] += 1
    path = state_path(store, state['session_id'])
    CORE.atomic_json(path, state)
    if os.name != 'nt':
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

def attribution(store, session, owner=None):
    CORE.load_owner(store, owner)
    _, value = CORE.load_state(store, 'codex', session)
    binding = CORE.current_record(value, require_active=True)
    CORE.require_external_store(store, binding)
    return binding

def add_observation(state, identifier, kind, proof, version=1):
    prior = state['observations'].get(identifier)
    consumed = prior['consumed_version'] if prior else 0
    state['observations'][identifier] = {'id': identifier, 'kind': kind, 'version': version, 'consumed_version': consumed, 'proof': proof}

def refresh(state):
    source = state['source']
    if source is None:
        state['source_problem'] = 'NO_REGISTERED_TRANSCRIPT; bounded audit still required for a signal'
        return
    try:
        observed = scan_source(source['path'], source)
        meta = observed['metadata']
        require(meta.get('id') == source['task_id'] and meta.get('session_id') == state['session_id'], 'SOURCE_SESSION_CHANGED')
        staged = []
        for summary in observed['summaries']:
            proof = {'source': source_identity(source), **summary, 'native_producer_runtime_equivalence': 'UNVERIFIED'}
            identifier = 'boundary-' + digest(canonical(proof))
            completed = sum((item['canonical'] for item in summary['markers'])) == 1
            staged.append((identifier, 'COMPLETED_RESUMED_BOUNDARY' if completed else 'AMBIGUOUS_MARKER_GROUP', proof))
        for identifier, kind, proof in staged:
            add_observation(state, identifier, kind, proof)
        state['source_problem'] = 'COMPACTION_MARKER_WITHOUT_PROVED_RESUME' if observed['unresumed_marker'] else None
        source['prefix_bytes'] = observed['bytes']
        source['prefix_sha256'] = observed['sha256']
    except (Refusal, OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        state['source_problem'] = str(exc)

def outstanding(state):
    return [{'id': item['id'], 'version': item['version'], 'kind': item['kind']} for item in state['observations'].values() if item['version'] > item['consumed_version']]

def scope_owners(state, identifier):
    consumed = state['observations'][identifier]['consumed_version']
    owners = [child for child, assignment in state['assignments'].items() if any((item['id'] == identifier and item['version'] > consumed for item in assignment['scope']))]
    require(len(owners) <= 1, 'CONFLICTING_SCOPE_OWNERS')
    return owners

def available_scope(state):
    pending = outstanding(state)
    has_claim = any((scope_owners(state, item['id']) for item in pending))
    return [item for item in pending if not scope_owners(state, item['id']) and (item['kind'] == 'COMPLETED_RESUMED_BOUNDARY' or not has_claim)]

def decision(state):
    pending = outstanding(state)
    available = available_scope(state)
    assigned = [{**item, 'child_id': scope_owners(state, item['id'])[0]} for item in pending if scope_owners(state, item['id'])]
    active = sorted({item['child_id'] for item in assigned})
    return {'schema': 'implementaudit.compaction-audit-decision.v1', **CEILING, 'decision': 'AUDIT_STATE_REQUIRED' if available else 'WAIT_EXISTING_AUDIT' if pending else 'NO_PENDING_AUDIT', 'audit_state_required': bool(pending), 'state_dependent_decisions_held': bool(pending), 'pending': pending, 'available_scope': available, 'assigned_scope': assigned, 'active_child': active[0] if len(active) == 1 else None, 'active_children': active, 'source_problem': state['source_problem'], 'signal_observations': state['signals'], 'native_lifecycle': 'NOT_CLAIMED', 'native_producer_runtime_equivalence': 'UNVERIFIED'}

def record_signal(store, session, event):
    """Called by the real compact hook before any continuity prerequisite."""
    store = Path(store).absolute()
    binding = attribution(store, session)
    with CORE.writer_lock(store):
        state = load(store, session)
        refresh(state)
        state['signals'] += 1
        state['unresolved_signal_version'] += 1
        identifier = 'unresolved-signal-' + CORE.session_key(session)
        add_observation(state, identifier, 'UNRESOLVED_SIGNAL', {'host_session_id': session, 'signal': 'SessionStart/source=compact', 'hook_source_sha256': digest((HERE / 'codex-compact-interlock.py').read_bytes()), 'binding_generation': binding['binding_generation'], 'logical_occurrence_count': None, 'completion': 'UNRESOLVED', 'resume': 'UNRESOLVED', 'delivery_count_is_not_occurrence_identity': True}, state['unresolved_signal_version'])
        save(store, state)
        return decision(state)

def code_identity():
    raise Refusal('NONPROTECTED_PROJECTION_REQUIRES_SELECTED_SOURCE')

def prepare_obligation(store, state, assignment):
    scope = [item for item in outstanding(state) if scope_owners(state, item['id']) == [assignment['child_id']]]
    if 'scope' not in assignment.get('reservation_request', {}):
        scope += available_scope(state)
    require(scope, 'NO_OBSERVABLE_OWNED_SCOPE')
    claims = {item['id']: item for item in assignment['scope']}
    claims.update({item['id']: item for item in scope})
    assignment['scope'] = list(claims.values())
    observation = {'child_id': assignment['child_id'], 'scope': scope, 'code': assignment['code'], 'source_cutoff': state['source'], 'source_problem': state['source_problem'], 'revision': state['revision']}
    identifier = digest(canonical(observation))
    source = assignment['observation_source']
    obligation = {'schema': 'implementaudit.compaction-obligation.v1', 'parent_identity': source['parent_identity'], 'actual_child_identity': source['actual_child_identity'], 'selected_child': 'audit-state', 'observation_id': identifier, 'covered_boundary_versions': scope, 'observation_source_cutoff': observation['source_cutoff'], 'code_and_skill_pins': assignment['code'], 'bounded_purpose': assignment['bounded_purpose'], 'authority_ceiling': 'NONE'}
    path = state_path(store, state['session_id']).parent / 'obligations' / (digest(canonical(obligation)) + '.json')
    if path.exists():
        require(CORE.read_json(path, 'immutable compaction obligation') == obligation, 'OBLIGATION_CONFLICT')
    else:
        CORE.atomic_json(path, obligation)
    raw = path.read_bytes()
    pin = {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}
    assignment.setdefault('prepared', {})[identifier] = {'observation': observation, 'obligation': obligation, 'obligation_pin': pin, 'authorization': None, 'exchange': None}
    return {'obligation': obligation, 'obligation_pin': pin, 'obligation_digest': pin['sha256'], **CEILING}

def boundary_release_subject(store, session, owner, request):
    """Read-only release input for a fresh general assignment, never migration."""
    require(isinstance(request, dict) and set(request) == {'child_id', 'return_digest', 'acceptance', 'child_terminal'}, 'BOUNDARY_RELEASE_SUBJECT_SHAPE')
    path = state_path(store, session)
    before = path.read_bytes()
    state = load(store, session)
    child = text(request['child_id'])
    assignment = state['assignments'].get(child)
    require(assignment is not None and assignment['code'] == _assignment_code_identity(assignment) and (assignment.get('observation_source', {}).get('profile_id') in OBSERVATION.BOUNDARY_PROFILES) and ('scope' in assignment.get('reservation_request', {})) and (assignment['join'] is None), 'BOUNDARY_RELEASE_FRESH_ASSIGNMENT_REQUIRED')
    source = _rebind_selected_assignment(assignment, session, child)
    require(source == assignment['observation_source'], 'BOUNDARY_RELEASE_SOURCE_CHANGED')
    result = assignment['return']
    require(result is not None and result['status'] == 'SUCCEEDED' and (result['return_digest'] == request['return_digest']), 'BOUNDARY_RELEASE_RESULT_ABSENT')
    identifier = result['observation_id']
    require(identifier not in assignment.get('hold_failures', {}) and identifier not in assignment.get('hold_refusals', {}), 'BOUNDARY_RELEASE_HOLD_REFUSED')
    prepared = assignment['prepared'][identifier]
    actual = OBSERVATION.actual_result(source, prepared, result['evidence'], store, session, owner, selected_audit_state_pin(), prior_context=prior_history_context(assignment, identifier))
    require(result == {'child_id': child, **actual, **CEILING}, 'BOUNDARY_RELEASE_RESULT_CHANGED')
    accepted = OBSERVATION.acceptance(source, prepared, actual, request['acceptance'])
    require(assignment.get('accepted') == accepted and assignment.get('logical_join') is not None, 'BOUNDARY_RELEASE_ACCEPTANCE_CHANGED')
    policy = OBSERVATION.fixed_policy(assignment['code'], source['profile_id'])
    require(assignment['policy'] == policy, 'ASSIGNMENT_POLICY_CHANGED')
    root = path.parent / policy['descriptor']['custody_namespace'] / policy['policy_digest']

    def refuse_write(*_):
        raise Refusal('BOUNDARY_RELEASE_CANDIDATE_NOT_ACQUIRED')
    candidate, candidate_pin = OBSERVATION.acquire_candidate(source, prepared, actual, accepted, policy, root, refuse_write)
    require(candidate_pin == assignment['logical_join']['acquisition']['candidate'], 'BOUNDARY_RELEASE_CANDIDATE_CHANGED')
    profile = OBSERVATION.production_profile(policy, root)
    require(profile['qualification_record_bound'] is True, 'BOUNDARY_RELEASE_Q_ABSENT')
    issuer = policy['descriptor']['authenticating_source_owner']
    raw, _ = OBSERVATION.artifact(issuer['module_pin'], maximum=65536)
    if source['profile_id'] == OBSERVATION.NONPROTECTED_PROFILE:
        import types
        module = types.ModuleType('_boundary_release_source_owner')
        module.__file__ = issuer['module_pin']['path']
        exec(compile(raw, module.__file__, 'exec', dont_inherit=True), module.__dict__)
    else:
        spec = importlib.util.spec_from_file_location('_boundary_release_source_owner', issuer['module_pin']['path'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        require(digest(Path(issuer['module_pin']['path']).read_bytes()) == digest(raw), 'SOURCE_OWNER_MODULE_PIN_CHANGED')
    require(callable(getattr(module, 'host_binding', None)) and callable(getattr(module, 'release_subject', None)), 'BOUNDARY_RELEASE_OWNER_FUNCTIONS_ABSENT')
    binding = module.host_binding(OBSERVATION, source, policy)
    subject = module.release_subject(OBSERVATION, source, prepared, actual, accepted, candidate_pin, profile['Q'], request['child_terminal'], policy=policy)
    require(OBSERVATION.production_profile(policy, root) == profile, 'BOUNDARY_RELEASE_QUALIFICATION_CHANGED_DURING_READ')
    OBSERVATION.artifact(candidate_pin)
    require(assignment['code'] == _assignment_code_identity(assignment) and OBSERVATION.fixed_policy(assignment['code'], source['profile_id']) == policy, 'BOUNDARY_RELEASE_POLICY_CHANGED_DURING_READ')
    require(path.read_bytes() == before, 'BOUNDARY_RELEASE_STATE_CHANGED_DURING_READ')
    return {'status': 'SOURCE_BOUND_RELEASE_SUBJECT_READY', 'subject': subject, 'host_binding': binding, 'candidate': candidate_pin, 'Q': profile['Q'], 'pending_consumed': False, 'host_producer_authenticated': False, **CEILING}

def selected_audit_state_pin():
    path = HERE.parent.parent / 'audit-state' / 'SKILL.md'
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}

def hold_checked(store, state, assignment, observation_id, operation):
    """Retain proved early USE and, separately, stable material refusals."""
    require(observation_id not in assignment.get('hold_failures', {}), 'HOLD_EPISODE_PREVIOUSLY_DISQUALIFIED')
    require(observation_id not in assignment.get('hold_refusals', {}), 'HOLD_EPISODE_PREVIOUSLY_REFUSED')
    try:
        return operation()
    except ValueError as exc:
        if str(exc) == 'HOLD_EARLY_SAME_EPISODE_USE':
            bucket = 'hold_failures'
        elif isinstance(exc, OBSERVATION.HoldObservationRefusal):
            bucket = 'hold_refusals'
        else:
            raise
        refusal = {'reason': str(exc), 'observation_id': observation_id, 'authority': 'NONE'}
        if isinstance(exc, OBSERVATION.HoldObservationRefusal):
            refusal['evidence'] = exc.evidence
        assignment.setdefault(bucket, {})[observation_id] = refusal
        save(store, state)
        raise

def prior_history_context(assignment, observation_id):
    """Read-only candidates from this assignment; runtime revalidates every one."""
    observed = assignment.get('observations', {})
    require(type(observed) is dict and len(observed) <= OBSERVATION.MAX_RECORDS, 'HOLD_PRIOR_CONTEXT_BOUND')
    current = assignment['prepared'][observation_id]['observation']
    require(type(current['revision']) is int, 'HOLD_PRIOR_OBSERVATION_ORDER')
    for bucket, reason in (('hold_failures', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED'), ('hold_refusals', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED')):
        for identifier in assignment.get(bucket, {}):
            if identifier == observation_id:
                continue
            prior = assignment.get('prepared', {}).get(identifier)
            require(prior is not None and isinstance(prior.get('observation'), dict) and (type(prior['observation'].get('revision')) is int) and (digest(canonical(prior['observation'])) == identifier), 'HOLD_PRIOR_REFUSAL_SCOPE_UNKNOWN')
            require(prior['observation']['revision'] >= current['revision'], reason)
    candidates = {}
    for identifier, observation in observed.items():
        require(isinstance(observation, dict) and type(observation.get('revision')) is int, 'HOLD_PRIOR_OBSERVATION_SHAPE')
        if identifier == observation_id or observation['revision'] >= current['revision']:
            continue
        prior = assignment.get('prepared', {}).get(identifier)
        require(prior is not None and prior.get('observation') == observation, 'HOLD_PRIOR_UNBOUND_OBSERVATION')
        require(identifier not in assignment.get('hold_failures', {}), 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED')
        require(identifier not in assignment.get('hold_refusals', {}), 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED')
        candidates[identifier] = prior
    return candidates

def operate(store, session, owner, action, request):
    store = Path(store).absolute()
    attribution(store, session, text(owner))
    if action == 'status':
        require(request is None, 'STATUS_IS_NONOBSERVING')
        return decision(load(store, session))
    if action == 'release-subject':
        return boundary_release_subject(store, session, owner, request)
    if action == 'release-subject-current':
        raise Refusal('NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED')
    with CORE.writer_lock(store):
        state = load(store, session)
        if action == 'register-source':
            source = source_registration(request, session)
            require(state['source'] is None or source_identity(state['source']) == source_identity(source), 'REGISTERED_SOURCE_REPLACEMENT_REFUSED')
            if state['source'] is not None:
                old = state['source']
                scan_source(source['path'], old)
                if 'resume_observation_relations' in old:
                    source['resume_observation_relations'] = old['resume_observation_relations']
            state['source'] = source
            refresh(state)
            save(store, state)
            return {'status': 'SOURCE_REGISTERED_PHYSICAL_ONLY', 'source': source, **CEILING}
        refresh(state)
        if action == 'resume':
            require(request is None or (isinstance(request, dict) and set(request) == {'currentness', 'measured_epoch'}), 'RESUME_OBSERVATION_SHAPE')
            proved = [item for item in outstanding(state) if item['kind'] == 'COMPLETED_RESUMED_BOUNDARY']
            identifier = 'unresolved-resume-' + CORE.session_key(session)
            prior = state['observations'].get(identifier)
            version = prior['version'] + 1 if prior else 1
            add_observation(state, identifier, 'UNRESOLVED_RESUME_OBSERVATION', {'host_session_id': session, 'entry': 'EXPLICIT_GOVERNOR_POST_COMPACTION_RESUME_OBSERVATION', 'occurrence_proof': 'UNRESOLVED', 'logical_occurrence_count': None, 'delivery_count_is_not_occurrence_identity': True, 'observed_limits': request}, version)
            if proved and (not state['source_problem']):
                for item in state['observations'].values():
                    if item['kind'] == 'UNRESOLVED_RESUME_OBSERVATION':
                        state['source'].setdefault('resume_observation_relations', {})[item['id']] = {'observation_version': item['version'], 'later_proved_scope': proved, 'observed_prefix_bytes': state['source']['prefix_bytes'], 'observed_prefix_sha256': state['source']['prefix_sha256'], 'retroactive_child_credit': False}
            save(store, state)
            return decision(state)
        require(isinstance(request, dict), 'REQUEST_SHAPE')
        child = text(request.get('child_id'))
        if action == 'stage-current':
            raise Refusal('NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED')
        if action == 'activate-current':
            raise Refusal('NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED')
        if action == 'stage-successor':
            raise Refusal('NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED')
        if action == 'activate-successor':
            raise Refusal('NONPROTECTED_PROJECTION_OPERATION_UNSUPPORTED')
        if action == 'reserve':
            require(set(request) in ({'child_id'}, {'child_id', 'bounded_purpose', 'observation_source'}, {'child_id', 'bounded_purpose', 'observation_source', 'scope'}), 'RESERVATION_SHAPE')
            prior = state['assignments'].get(child)
            if prior:
                require(prior['join'] is None, 'USED_CHILD_CONTEXT_REFUSED')
                require(prior['code'] == _assignment_code_identity(prior) and prior.get('reservation_request', {'child_id': child}) == request, 'CONFLICTING_RESERVATION')
                return {'assignment': prior, **CEILING}
            scope = available_scope(state)
            if 'scope' in request:
                selected = request['scope']
                require(not state['source_problem'] and isinstance(selected, list) and (0 < len(selected) <= MAX_ROWS) and all((item in scope and item['kind'] == 'COMPLETED_RESUMED_BOUNDARY' for item in selected)) and (len({item['id'] for item in selected}) == len(selected)), 'EXACT_BOUNDARY_SCOPE_REQUIRED')
                scope = selected
            require(scope, 'NO_UNASSIGNED_INDEPENDENT_SCOPE; existing claims require reconciliation')
            assignment = {'child_id': child, 'scope': scope, 'code': nonprotected_code_identity() if _nonprotected_reservation(request) else code_identity(), 'observations': {}, 'return': None, 'join': None, 'native_lifecycle': 'NOT_CLAIMED', 'reservation_request': request}
            assignment['policy'] = OBSERVATION.fixed_policy(assignment['code'], OBSERVATION.NONPROTECTED_PROFILE if _nonprotected_reservation(request) else OBSERVATION.PROFILE)
            state['assignments'][child] = assignment
            obligation = {}
            if 'observation_source' in request:
                assignment['observation_source'] = OBSERVATION.bind_nonprotected_sources(request['observation_source'], assignment['code']) if _nonprotected_reservation(request) else OBSERVATION.bind_sources(request['observation_source'], session, child)
                if _nonprotected_reservation(request):
                    require(assignment['observation_source']['actual_child_identity']['thread_id'] == child and assignment['observation_source']['parent_identity']['thread_id'] == session, 'NONPROTECTED_RESERVED_ACTUAL_CHILD_DIFFERS')
                context = assignment['observation_source']
                if context['profile_id'] in (OBSERVATION.CURRENT_BOUNDARY_PROFILE, OBSERVATION.NONPROTECTED_PROFILE):
                    require(context['fresh_child_boundary'] == OBSERVATION.fresh_child_boundary(context), 'CURRENT_FRESH_SOURCE_BOUNDARY_CHANGED')
                if context['profile_id'] in OBSERVATION.BOUNDARY_PROFILES:
                    require('scope' in request, 'EXACT_BOUNDARY_SCOPE_REQUIRED')
                    for covered in scope:
                        proof = state['observations'][covered['id']]['proof']
                        resume = proof['resume']
                        require(resume['offset'] + resume['bytes'] <= context['open']['locator']['offset'], 'BOUNDARY_CHILD_NOT_FRESH_FOR_SCOPE')
                        OBSERVATION.before({'path': state['source']['path'], 'locator': resume, 'timestamp': resume['timestamp']}, context['open'])
                if 'scope' in request:
                    registered = state['source']
                    parent = context['parent']
                    require(registered is not None and parent['path'] == registered['path'] and (parent['physical'] == registered['physical']) and (parent['metadata']['sha256'] == registered['session_meta_sha256']), 'BOUNDARY_SOURCE_ASSOCIATION_CHANGED')
                assignment['policy'] = OBSERVATION.fixed_policy(assignment['code'], context['profile_id'])
                assignment['bounded_purpose'] = text(request['bounded_purpose'])
                obligation = prepare_obligation(store, state, assignment)
            save(store, state)
            return {'assignment': assignment, **obligation, **CEILING}
        assignment = state['assignments'].get(child)
        require(assignment is not None, 'FOREIGN_CHILD')
        successor = state.get('successor_assignment')
        successor_route = False
        current = state.get('current_assignment')
        current_route = False
        if successor_route:
            pass
        require((assignment['join'] is None or action == 'join') and (current_route or successor_route or assignment['code'] == _assignment_code_identity(assignment)), 'CHILD_OR_SOURCE_CHANGED')
        if action == 'observe-child' and 'phase' in request:
            require(assignment['return'] is None and assignment.get('observation_source') is not None, 'OBSERVATION_SOURCE_UNBOUND_OR_AFTER_RETURN')
            phase = request['phase']
            if phase == 'prepare':
                require(set(request) == {'child_id', 'phase'}, 'PREPARE_OBLIGATION_SHAPE')
                prepared = prepare_obligation(store, state, assignment)
                save(store, state)
                return prepared
            require(request.get('observation_id') in assignment.get('prepared', {}), 'UNPREPARED_OBSERVATION')
            prepared = assignment['prepared'][request['observation_id']]
            if phase == 'deliver':
                require(set(request) == {'child_id', 'phase', 'observation_id', 'authorization_evidence'}, 'DELIVERY_SHAPE')
                validated = OBSERVATION.authorization(assignment['observation_source'], prepared, request['authorization_evidence'], selected_audit_state_pin())
                require(prepared['authorization'] in (None, validated), 'CONFLICTING_PUBLIC_AUTHORIZATION')
                prepared['authorization'] = validated
                prepared['delivery_request'] = request
                packet = OBSERVATION.delivery_packet(prepared, validated)
                save(store, state)
                return packet
            require(phase == 'bind' and set(request) == {'child_id', 'phase', 'observation_id', 'exchange'}, 'OBSERVATION_BIND_SHAPE')
            exchange = OBSERVATION.completed_exchange(assignment['observation_source'], prepared, request['exchange'], store, session, owner, selected_audit_state_pin())
            require(prepared['exchange'] in (None, exchange), 'CONFLICTING_CHILD_OBSERVATION_EXCHANGE')
            require(prepared.get('bind_request') in (None, request), 'CONFLICTING_ORIGINAL_BIND_REQUEST')
            held = hold_checked(store, state, assignment, request['observation_id'], lambda: OBSERVATION.hold_history(assignment['observation_source'], prepared, exchange, request, store, session, owner, prior_context=prior_history_context(assignment, request['observation_id'])))
            if prepared.get('bound_response') is not None:
                return prepared['bound_response']
            require(prepared.get('hold_prefix') in (None, held), 'HOLD_BIND_PREFIX_ALREADY_SEALED')
            prepared['hold_prefix'] = held
            prepared['exchange'] = exchange
            assignment['observations'][request['observation_id']] = prepared['observation']
            prepared['bind_request'] = request
            prepared['bound_response'] = {'observation_id': request['observation_id'], 'child_observation_exchange_identity': exchange['identity'], **prepared['observation'], **CEILING}
            save(store, state)
            return prepared['bound_response']
        if action == 'observe-child':
            require(set(request) == {'child_id'} and assignment['return'] is None, 'OBSERVATION_AFTER_RETURN_OR_SHAPE')
            scope = [item for item in outstanding(state) if scope_owners(state, item['id']) == [child]]
            if 'scope' not in assignment.get('reservation_request', {}):
                scope += available_scope(state)
            require(scope, 'NO_OBSERVABLE_OWNED_SCOPE')
            claims = {item['id']: item for item in assignment['scope']}
            claims.update({item['id']: item for item in scope})
            assignment['scope'] = list(claims.values())
            observation = {'child_id': child, 'scope': scope, 'code': assignment['code'], 'source_cutoff': state['source'], 'source_problem': state['source_problem'], 'revision': state['revision']}
            identifier = digest(canonical(observation))
            assignment['observations'][identifier] = observation
            save(store, state)
            return {'observation_id': identifier, **observation, **CEILING}
        if action == 'return':
            require(set(request) == {'child_id', 'observation_id', 'result_evidence'}, 'RETURN_SHAPE_OR_AUTHORITY_CLAIM')
            require(request['observation_id'] in assignment['observations'], 'UNOBSERVED_RETURN_SCOPE')
            require(request['observation_id'] in assignment.get('prepared', {}), 'ACTUAL_OBLIGATION_EVIDENCE_REQUIRED')
            prepared = assignment['prepared'][request['observation_id']]
            actual = hold_checked(store, state, assignment, request['observation_id'], lambda: OBSERVATION.actual_result(assignment['observation_source'], prepared, request['result_evidence'], store, session, owner, selected_audit_state_pin(), prior_context=prior_history_context(assignment, request['observation_id'])))
            result = {'child_id': child, **actual, **CEILING}
            require(assignment['return'] in (None, result), 'CONFLICTING_RETURN')
            assignment['return'] = result
            save(store, state)
            return result
        if action == 'join':
            required_join = {'child_id', 'return_digest', 'acceptance'}
            require(set(request) == required_join or ((current_route or successor_route or assignment['observation_source']['profile_id'] in OBSERVATION.BOUNDARY_PROFILES) and set(request) == required_join | {'release_evidence'}), 'JOIN_SHAPE')
            result = assignment['return']
            require(result is not None and result['status'] == 'SUCCEEDED' and (result['return_digest'] == request['return_digest']), 'EXACT_SUCCESSFUL_RETURN_REQUIRED')
            require(result['observation_id'] in assignment.get('prepared', {}), 'ACTUAL_OBLIGATION_EVIDENCE_REQUIRED')
            prepared = assignment['prepared'][result['observation_id']]
            actual = hold_checked(store, state, assignment, result['observation_id'], lambda: OBSERVATION.actual_result(assignment['observation_source'], prepared, result['evidence'], store, session, owner, selected_audit_state_pin(), prior_context=prior_history_context(assignment, result['observation_id'])))
            require(result == {'child_id': child, **actual, **CEILING}, 'IMMUTABLE_ACTUAL_RESULT_CHANGED')
            accepted = OBSERVATION.acceptance(assignment['observation_source'], prepared, actual, request['acceptance'])
            require(assignment.get('accepted') in (None, accepted), 'CONFLICTING_ROOT_ACCEPTANCE')
            observed = assignment['observations'][result['observation_id']]
            require(observed['scope'], 'EMPTY_RETURN_COVERAGE')
            if any((item['kind'] in ('COMPLETED_RESUMED_BOUNDARY', 'AMBIGUOUS_MARKER_GROUP') for item in observed['scope'])):
                cutoff = observed['source_cutoff']
                require(cutoff is not None, 'RETURN_SOURCE_CUTOFF_ABSENT')
                try:
                    scan_source(cutoff['path'], cutoff)
                except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
                    raise Refusal('RETURN_SOURCE_CUTOFF_CHANGED: ' + str(exc)) from exc
            for covered in observed['scope']:
                item = state['observations'][covered['id']]
                exact_joined_retry = assignment['join'] is not None and assignment['join']['return_digest'] == result['return_digest'] and (assignment['join']['covered'] == observed['scope']) and (item['consumed_version'] >= covered['version'])
                require((scope_owners(state, covered['id']) == [child] or exact_joined_retry) and covered['version'] <= item['version'] and any((claim['id'] == covered['id'] and claim['version'] >= covered['version'] for claim in assignment['scope'])), 'FOREIGN_RETURN_COVERAGE')
            selected_policy = OBSERVATION.current_fixed_policy(assignment['code']) if current_route or successor_route else OBSERVATION.fixed_policy(assignment['code'], assignment['observation_source']['profile_id'])
            require(assignment.get('policy') == selected_policy, 'ASSIGNMENT_POLICY_CHANGED')
            acquisition = OBSERVATION.acquire_episode(assignment['observation_source'], prepared, actual, accepted, assignment['code'], state_path(store, session).parent, CORE.atomic_json, policy=selected_policy, release_evidence=request.get('release_evidence'))
            profile = acquisition['profile']
            if assignment['join'] is not None:
                require(acquisition['origin_validated'] is True and assignment['join']['acquisition'] == acquisition, 'ADMITTED_EPISODE_RETRY_DIFFERS')
                return assignment['join']
            if acquisition['origin_validated'] is not True:
                previous = assignment.get('admission_history', [assignment.get('logical_join')])[-1]
                if previous is not None:
                    old = previous['acquisition']
                    require(old['candidate'] == acquisition['candidate'] and (old['profile']['Q'] is None or old['profile']['Q'] == profile['Q']) and (old['episode'] is None or old['episode'] == acquisition['episode']), 'CONFLICTING_ACQUISITION_OR_ADMISSION')
                    if old == acquisition:
                        return previous
                projected = json.loads(canonical(state))
                apply_covered_versions(projected, observed['scope'])
                proposal = {'status': 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE', 'child_id': child, 'return_digest': result['return_digest'], 'proposed_consumption': observed['scope'], 'projected_pending': outstanding(projected), 'pending_consumed': False, 'host_producer_authenticated': False, 'profile': profile, 'acquisition': acquisition, 'acceptance': accepted, **CEILING}
                if assignment.get('accepted') is None:
                    assignment['accepted'] = accepted
                    assignment['logical_join'] = proposal
                assignment.setdefault('admission_history', []).append(proposal)
                save(store, state)
                return proposal
            require(acquisition['episode_record_bound'] and acquisition['episode'] is not None, 'EXACT_AUTHENTICATED_EPISODE_REQUIRED')
            if selected_policy['descriptor']['authenticating_source_owner'] is not None:
                require(acquisition.get('terminal_effect_release_qualified') is True, 'CURRENT_TERMINAL_EFFECT_RELEASE_REQUIRED')
            apply_covered_versions(state, observed['scope'])
            joined = {'status': 'JOINED_EVIDENCE_ONLY', 'child_id': child, 'return_digest': result['return_digest'], 'covered': observed['scope'], 'pending_consumed': True, 'host_producer_authenticated': True, 'profile': profile, 'acquisition': acquisition, **CEILING}
            assignment['accepted'] = accepted
            assignment['join'] = joined
            save(store, state)
            return joined
        raise Refusal('UNSUPPORTED_PENDING_OPERATION')

def apply_covered_versions(state, scope):
    """Apply the validated exact cutoff; shared by cold projection and qualified commit."""
    for covered in scope:
        item = state['observations'][covered['id']]
        item['consumed_version'] = max(item['consumed_version'], covered['version'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--owner-id', required=True)
    parser.add_argument('action', choices=('register-source', 'resume', 'status', 'reserve', 'stage-current', 'activate-current', 'stage-successor', 'activate-successor', 'observe-child', 'return', 'join', 'release-subject', 'release-subject-current'))
    args = parser.parse_args()
    try:
        raw = sys.stdin.buffer.read(65537)
        require(len(raw) <= 65536, 'REQUEST_BYTE_BOUND')
        request = decode(raw) if raw.strip() else None
        result = operate(args.store, text(args.session), args.owner_id, args.action, request)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Refusal, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'PENDING_OPERATION_REFUSED', 'reason': str(exc), **CEILING}, sort_keys=True))
        return 2

def nonprotected_code_identity():
    """Actual selected dependency closure; legacy identity stays unchanged."""
    skill = HERE.parent
    paths = [skill / 'SKILL.md', skill.parent / 'audit-state/SKILL.md', skill / 'references/child-agents.md', skill / 'references/continuity.md']
    paths += [HERE / name for name in ('compaction-audit-pending.py', 'compaction-result-observation.py', 'compaction-source-owner-codex-app.py', 'codex-recovery-native-reader.py', 'bounded_file_custody.py', 'bounded_native_reader.py', 'bounded_source_owner.py', 'host-session-binding.py', 'route-transaction.py')]
    pins = {}
    for path in paths:
        canonical_path, info = OBSERVATION.physical(path)
        require(0 < info.st_size <= 512 * 1024, 'NONPROTECTED_CODE_BOUND')
        with canonical_path.open('rb') as stream:
            require(OBSERVATION.identity(os.fstat(stream.fileno())) == OBSERVATION.identity(info), 'NONPROTECTED_CODE_CHANGED')
            raw = stream.read(info.st_size)
        pin = {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}
        require(OBSERVATION.artifact(pin, maximum=512 * 1024)[0] == raw, 'NONPROTECTED_CODE_CHANGED')
        pins[str(path.relative_to(skill.parent))] = pin['sha256']
    return pins

def _nonprotected_reservation(request):
    return isinstance(request.get('observation_source'), dict) and set(request['observation_source']) == {'open', 'spawn_call', 'spawn_output', 'child_activation', 'parent_turn_start'}

def _assignment_code_identity(assignment):
    if assignment.get('observation_source', {}).get('profile_id') == OBSERVATION.NONPROTECTED_PROFILE:
        return nonprotected_code_identity()
    return code_identity()

def _rebind_selected_assignment(assignment, session, child):
    source_request = assignment['reservation_request']['observation_source']
    previous = assignment['observation_source']
    if previous['profile_id'] != OBSERVATION.NONPROTECTED_PROFILE:
        return OBSERVATION.bind_sources(source_request, session, child)
    source = OBSERVATION.bind_nonprotected_sources(source_request, assignment['code'])
    require(source['canonical_episode_binding']['opening_digest'] == previous['canonical_episode_binding']['opening_digest'], 'NONPROTECTED_RELEASE_CANONICAL_OPEN_CHANGED')
    source['canonical_episode_binding'] = previous['canonical_episode_binding']
    return source

def _nonprotected_registration_selection(request, session):
    require(isinstance(request, dict), 'SOURCE_REGISTRATION_SHAPE')
    owner = OBSERVATION._nonprotected_source_owner(nonprotected_code_identity())
    if owner.NONPROTECTED_SELECTION_PIN is None:
        return None
    selected = owner._np_selection()
    if request.get('transcript') != selected['root_source']:
        return None
    require(session == selected['root_thread_id'], 'NONPROTECTED_REGISTRATION_PARENT_CHANGED')
    return selected

def _nonprotected_source_registration(request, session, selected):
    require(set(request) == {'task_id', 'transcript', 'expected_bytes', 'expected_sha256'} and request['task_id'] == session == selected['root_thread_id'], 'NONPROTECTED_SOURCE_REGISTRATION_SHAPE')
    observed = scan_source(selected['root_source'])
    meta = observed['metadata']
    require(observed['bytes'] == request['expected_bytes'] and observed['sha256'] == request['expected_sha256'] and (meta.get('id') == session) and (meta.get('session_id') == session) and (meta.get('cli_version') == selected['cli_version']), 'NONPROTECTED_SOURCE_REGISTRATION_PIN')
    return {'path': selected['root_source'], 'task_id': session, 'session_id': session, 'sessions_root': selected['session_root'], 'physical': observed['physical'], 'session_meta_sha256': observed['metadata_sha256'], 'prefix_bytes': observed['bytes'], 'prefix_sha256': observed['sha256'], 'provenance': 'HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX', 'native_producer_runtime_equivalence': 'UNVERIFIED'}

def scan_source(path, prefix=None):
    owner = OBSERVATION._nonprotected_source_owner(nonprotected_code_identity())
    if owner.NONPROTECTED_SELECTION_PIN is None:
        return _scan_source_unheld(path, prefix)
    selected = owner._np_selection()
    if str(path) != selected['root_source']:
        return _scan_source_unheld(path, prefix)
    custody = owner._np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    with custody.held_file(path):
        return _scan_source_unheld(path, prefix, native_cli_version=selected['cli_version'])

def _validate_registered_prefix(prefix):
    """Validate the immutable recorded prefix, never the current live EOF."""
    path = physical(prefix['path'])
    info = path.stat()
    length = prefix['prefix_bytes']
    require(type(length) is int and 0 < length <= OBSERVATION.MAX_TOTAL * OBSERVATION.MAX_RECORDS and (info.st_size >= length) and (OBSERVATION.identity(info) == prefix['physical']), 'SELECTED_EPISODE_PREFIX_PHYSICAL_CHANGED')
    with path.open('rb') as stream:
        require(OBSERVATION.identity(os.fstat(stream.fileno())) == prefix['physical'], 'SELECTED_EPISODE_PREFIX_PHYSICAL_CHANGED')
        first = stream.readline(MAX_SOURCE + 1)
        require(first.endswith(b'\n') and len(first) <= length and (digest(first) == prefix['session_meta_sha256']), 'SELECTED_EPISODE_PREFIX_HEADER_CHANGED')
        remaining = length - len(first)
        checksum = hashlib.sha256(first)
        while remaining:
            block = stream.read(min(1024 * 1024, remaining))
            require(block, 'SELECTED_EPISODE_PREFIX_TRUNCATED')
            checksum.update(block)
            remaining -= len(block)
        require(checksum.hexdigest() == prefix['prefix_sha256'] and OBSERVATION.identity(os.fstat(stream.fileno())) == prefix['physical'], 'SELECTED_EPISODE_PREFIX_CHANGED')

def _episode_export_unavailable(reason):
    value = {'schema': 'implementaudit.native-episode-export.v1', 'status': 'UNAVAILABLE', 'reason_code': reason, 'owner': None, 'episode': None, 'pending': None, 'lifecycle': None, 'occurrences': None, 'custody': None, 'authority_ceiling': 'NONE'}
    return OBSERVATION.validate_frozen_episode_export_v1({**value, 'export_digest': digest(canonical(value))})

def read_selected_accepted_episode_v1():
    """Read immutable accepted evidence through fixed R0033/H0/pending pointers.

    No native RPC, source refresh, code/profile selection argument, or writer.
    Existing canonical route validation may invoke its read-only Git owner.
    Frozen snapshots must instead call the pure observation-owner validator.
    """
    code = nonprotected_code_identity()
    owner = OBSERVATION._nonprotected_source_owner(code)
    if owner.NONPROTECTED_SELECTION_PIN is None:
        return _episode_export_unavailable('FIXED_SELECTION_UNBOUND')
    selected = owner._np_selection()
    custody = owner._np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    route = owner._np_module(selected['episode_owner']['module_pin'], 'route-transaction.py', custody)
    repo = Path(selected['episode_owner']['repository'])
    controller = selected['episode_owner']['controller']
    oid, current = route.current_ref(repo, controller)
    if current is None:
        return _episode_export_unavailable('CANONICAL_EPISODE_ABSENT')
    route.validate_pure_current_route(repo, controller)
    if current.get('route_state') not in ('OPEN', 'RETURNED', 'SATISFIED'):
        return _episode_export_unavailable('CANONICAL_EPISODE_ABSENT')
    episode_binding = owner._np_episode((selected, custody, None, None, None))
    pointer = selected['pending_owner']
    store = Path(pointer['store'])
    session = pointer['session_id']
    binding = attribution(store, session, pointer['owner_id'])
    scope = episode_binding['host_and_scope']
    require(scope['host_id'] == 'codex' and binding['binding_generation'] == scope['host_binding_generation'], 'SELECTED_EPISODE_H0_BINDING_CHANGED')
    if not state_path(store, session).exists():
        return _episode_export_unavailable('PENDING_STATE_ABSENT')
    state = load(store, session)
    matches = [item for item in state['assignments'].values() if item.get('observation_source', {}).get('profile_id') == OBSERVATION.NONPROTECTED_PROFILE and item['observation_source'].get('canonical_episode_binding', {}).get('opening_digest') == episode_binding['opening_digest']]
    require(len(matches) <= 1, 'SELECTED_EPISODE_ASSIGNMENT_AMBIGUOUS')
    if not matches:
        return _episode_export_unavailable('SELECTED_ASSIGNMENT_ABSENT')
    assignment = matches[0]
    context = assignment['observation_source']
    joined = assignment.get('join')
    require(assignment['code'] == code and context['_source_profile_code_pins'] == code and (context['actual_child_identity']['thread_id'] == assignment['child_id']) and (context['actual_child_identity']['agent_path'] == selected['root_agent_path'] + '/' + episode_binding['logical_task']) and (context['parent_identity'] == {'thread_id': session, 'agent_path': selected['root_agent_path']}), 'SELECTED_EPISODE_ASSIGNMENT_OR_CODE_CHANGED')
    if joined is None:
        return _episode_export_unavailable('ADMITTED_JOIN_ABSENT')
    result = assignment['return']
    accepted = assignment['accepted']
    acquisition = joined['acquisition']
    require(joined['status'] == 'JOINED_EVIDENCE_ONLY' and joined['pending_consumed'] is True and (joined['host_producer_authenticated'] is True) and (result['status'] == 'SUCCEEDED') and (result['return_digest'] == digest(canonical(result['identity'])) == joined['return_digest']), 'SELECTED_EPISODE_RETURN_JOIN_CHANGED')
    prepared = assignment['prepared'][result['observation_id']]
    require(prepared['observation'] == assignment['observations'][result['observation_id']] and digest(canonical(prepared['observation'])) == result['observation_id'] and (prepared['obligation']['covered_boundary_versions'] == joined['covered']) and (result['identity']['scope'] == joined['covered']), 'SELECTED_EPISODE_OBSERVATION_CHANGED')
    prior_history_context(assignment, result['observation_id'])
    policy = OBSERVATION.fixed_policy(code, OBSERVATION.NONPROTECTED_PROFILE)
    require(assignment['policy'] == acquisition['policy'] == policy, 'SELECTED_EPISODE_POLICY_CHANGED')
    root = state_path(store, session).parent / policy['descriptor']['custody_namespace'] / policy['policy_digest']
    profile = OBSERVATION.production_profile(policy, root)
    require(profile['qualification_record_bound'], 'SELECTED_EPISODE_QUALIFICATION_REMOVED')
    expected_profile = {**profile, 'status': 'POLICY_QUALIFIED_BY_FIXED_SOURCE_OWNER', 'policy_qualified': True}
    expected_profile.pop('unresolved_implementation_edge', None)
    require(joined['profile'] == acquisition['profile'] == expected_profile and acquisition['status'] == 'ADMITTED_EXACT_SOURCE_OWNER_EPISODE' and (acquisition['origin_validated'] is True) and (acquisition['episode_record_bound'] is True) and (acquisition['host_producer_authenticated'] is True) and (acquisition['terminal_effect_release_qualified'] is True), 'SELECTED_EPISODE_ADMISSION_CHANGED')

    def retained(pin, directory):
        require(Path(pin['path']).parent == root / directory, 'SELECTED_EPISODE_CUSTODY_NAMESPACE')
        value, actual = OBSERVATION.custody_record(Path(pin['path']), root)
        require(actual == pin, 'SELECTED_EPISODE_CUSTODY_CHANGED')
        return value
    candidate = retained(acquisition['candidate'], 'candidates')
    attestation = retained(acquisition['source_owner_attestation'], 'attestations')
    episode = retained(acquisition['episode'], 'episodes')
    obligation_raw, _ = OBSERVATION.artifact(prepared['obligation_pin'])
    require(decode(obligation_raw) == prepared['obligation'], 'SELECTED_EPISODE_OBLIGATION_CHANGED')
    expected = OBSERVATION.episode_value(candidate, acquisition['candidate'], profile['Q'])
    expected['actual_acquisition_and_custody_validation_evidence']['source_owner_attestation'] = acquisition['source_owner_attestation']
    require(episode == expected == acquisition['episode_candidate'] and candidate['policy_digest'] == policy['policy_digest'] and (candidate['observation_id'] == result['observation_id']) and (candidate['exact_result_digest'] == result['return_digest']) and (candidate['exact_acceptance_digest'] == digest(canonical(accepted))) and (candidate['O_U_exchange_USE_R_A_identities']['R'] == result['identity']) and (candidate['O_U_exchange_USE_R_A_identities']['A'] == accepted) and (candidate['covered_boundary_versions'] == joined['covered']) and (candidate['parent_identity'] == context['parent_identity']) and (candidate['actual_child_identity'] == context['actual_child_identity']), 'SELECTED_EPISODE_IMMUTABLE_CLOSURE_CHANGED')
    OBSERVATION.validate_source_owner_attestation_record(attestation, policy['descriptor']['authenticating_source_owner'], candidate, acquisition['candidate'], context, prepared, result, accepted, policy, profile['Q'], attestation['release_evidence'])
    for pin in [result['identity']['result_pin'], *(row['pin'] for row in result['identity']['members'])]:
        OBSERVATION.artifact(pin)
    with owner.nonprotected_sources_guard(OBSERVATION._nonprotected_observation_view(), context, code):
        OBSERVATION.hold_records(context, cutoff=result['identity']['hold_history']['prefix_bytes'], prior=result['identity']['hold_history'])
        _validate_registered_prefix(prepared['obligation']['observation_source_cutoff'])
        for pin in candidate['physical_source_and_cutoff_identities']['records']:
            source = context[pin['role']]
            _, actual = OBSERVATION.resolve_record(context, pin['role'], pin['locator'])
            require(actual == pin and source['physical'] == pin['physical'], 'SELECTED_EPISODE_RECORD_CHANGED')
    rows = []
    for item in sorted(state['observations'].values(), key=lambda item: item['id']):
        rows.append({key: item[key] for key in ('id', 'kind', 'version', 'consumed_version')} | {'assignment_children': sorted(scope_owners(state, item['id']))})
    h0 = {'status': 'NOT_RECORDED', 'stage_receipts': {}}
    execution = current.get('lifecycle', {}).get('execution_evidence')
    if execution is not None:
        evidence = route.resolved_execution_evidence_record(execution, episode_binding['selected_child_role'], scope['route_transaction_id'], scope['obligation_id'], episode_binding['packet_pin']['digest'])
        require((evidence['owner_id'], evidence['host_id'], evidence['host_session_id'], evidence['binding_generation']) == (pointer['owner_id'], scope['host_id'], session, scope['host_binding_generation']), 'SELECTED_EPISODE_H0_STAGE_CHANGED')
        h0 = {'status': 'RECORDED', 'stage_receipts': {row['stage']: row['receipt_identity'] for row in evidence['stages']}}
    identities = candidate['physical_source_and_cutoff_identities']
    occurrences = {'schema': 'implementaudit.compaction-selected-occurrences.v1', 'observation_id': result['observation_id'], 'actual_child_identity': candidate['actual_child_identity'], 'covered_boundary_versions': joined['covered'], 'source_cutoff': result['identity']['hold_history'], 'occurrences': result['identity']['selected_occurrences'], 'authority_ceiling': 'NONE'}
    value = {'schema': 'implementaudit.native-episode-export.v1', 'status': 'AVAILABLE', 'reason_code': None, 'owner': {'profile_id': OBSERVATION.NONPROTECTED_PROFILE, 'issuer_id': attestation['issuer_id'], 'policy_digest': policy['policy_digest'], 'code_pins': code, 'canonical_opening_digest': episode_binding['opening_digest'], 'canonical_route': episode_binding['route_current'], 'host_and_scope': episode_binding['host_and_scope']}, 'episode': {key: candidate[key] for key in ('parent_identity', 'actual_child_identity', 'assignment_identity', 'obligation_digest', 'observation_id', 'covered_boundary_versions')} | {'result_digest': result['return_digest'], 'acceptance_digest': candidate['exact_acceptance_digest'], 'Q_digest': profile['Q']['sha256'], 'E_digest': acquisition['episode']['sha256']}, 'pending': {'revision': state['revision'], 'observations': rows, 'assignment_scope': assignment['scope'], 'covered_scope': joined['covered'], 'pending_scope': [{key: row[key] for key in ('id', 'version', 'kind')} for row in rows if row['version'] > row['consumed_version']]}, 'lifecycle': {'result': {'status': 'SUCCEEDED', 'return_digest': result['return_digest']}, 'acceptance': {'status': 'ACCEPTED_EXACT_RESULT', 'digest': candidate['exact_acceptance_digest']}, 'join': {'status': 'JOINED_EVIDENCE_ONLY', 'covered': joined['covered'], 'pending_consumed': True}, 'h0': h0, 'source_terminal_release': {'status': 'SOURCE_OWNER_VALIDATED', 'digest': digest(canonical(attestation['terminal_effect_release']))}}, 'occurrences': occurrences, 'custody': {'candidate': acquisition['candidate'], 'qualification': profile['Q'], 'episode': acquisition['episode'], 'attestation': acquisition['source_owner_attestation'], 'source_cutoffs': {key: identities[key] for key in ('parent', 'child')} | {'compaction_cutoff': {key: identities['compaction_cutoff'][key] for key in ('path', 'task_id', 'session_id', 'sessions_root', 'physical', 'session_meta_sha256', 'prefix_bytes', 'prefix_sha256', 'provenance', 'native_producer_runtime_equivalence')}} | {'hold_history': result['identity']['hold_history']}}, 'authority_ceiling': 'NONE'}
    require(load(store, session) == state and attribution(store, session, pointer['owner_id']) == binding and (owner._np_episode((selected, custody, None, None, None)) == episode_binding) and (OBSERVATION.production_profile(policy, root) == profile) and (nonprotected_code_identity() == code), 'SELECTED_EPISODE_CHANGED_DURING_READ')
    return OBSERVATION.validate_frozen_episode_export_v1({**value, 'export_digest': digest(canonical(value))})

def acquire_selected_episode_export_v1():
    """Collector entry for explicit acquisition; never called by frozen readers.

    The compaction branch reads an already acquired immutable closure without
    a native RPC. The separately selected ordinary branch authenticates bounded
    public records through read-only local native APIs; it never executes the
    receiver or publishes its receipt. Frozen validators do neither operation.
    """
    owner = OBSERVATION._nonprotected_source_owner(nonprotected_code_identity())
    if owner.ORDINARY_SELECTION_PIN is not None:
        return owner.acquire_selected_ordinary_episode_v1()
    return read_selected_accepted_episode_v1()
if __name__ == '__main__':
    raise SystemExit(main())
