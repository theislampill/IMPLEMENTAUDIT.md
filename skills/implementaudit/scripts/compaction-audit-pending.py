#!/usr/bin/env python3
"""Non-authorizing compaction audit obligations in existing host-session custody.

This owner never invokes a model, Git, native runtime, installer or watchdog.
It uses the existing H0 owner lock and atomic writer without changing that owner.
Physical transcript registration is an explicit host-store-owner action, never
a hook payload capability or proof of runtime producer equivalence.
"""
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
CEILING = {'authority': 'NONE', 'canonical_currentness': False, 'recovery_authority': False,
           'epoch_authority': False, 'effect_authority': False, 'independent_children': 'UNCHANGED',
           'actual_child_result_consumer': 'UNQUALIFIED',
           'same_failed_scope_retry': 'CONDITIONAL_UNQUALIFIED'}


class Refusal(ValueError):
    pass


def custody_refusal(reason):
    # Reuse safe H0 helpers without leaking a second JSON protocol or SystemExit.
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
    require(isinstance(value, str) and 0 < len(value) <= 1024 and
            all(ord(char) >= 32 for char in value), 'INVALID_TEXT')
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
        require(not member.is_symlink() and not (getattr(info, 'st_file_attributes', 0) & 0x400), 'SOURCE_REPARSE')
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
            'SOURCE_FILE_KIND')
    return path


def source_bytes(path):
    path = physical(path)
    before = path.stat()
    require(0 < before.st_size <= MAX_SOURCE, 'SOURCE_BYTE_BOUND')
    with path.open('rb') as stream:
        raw = stream.read(MAX_SOURCE + 1)
    after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'SOURCE_CHANGED_DURING_READ')
    require(len(raw) <= MAX_SOURCE and raw.endswith(b'\n') and b'\r' not in raw and b'\x00' not in raw,
            'SOURCE_PARTIAL_OR_UNSUPPORTED_WIRE')
    wires = raw.splitlines(keepends=True)
    require(len(wires) <= MAX_ROWS, 'SOURCE_ROW_BOUND')
    return raw, wires, {'device': before.st_dev, 'inode': before.st_ino}


def rows(wires):
    result = []
    offset = 0
    for number, wire in enumerate(wires):
        row = decode(wire)
        require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'},
            {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and
            type(row.get('ordinal')) is int and row['ordinal'] == number and
            isinstance(row.get('type'), str) and isinstance(row.get('payload'), dict), 'SOURCE_ROW_SHAPE')
        text(row['timestamp'])
        result.append((row, {'ordinal': number, 'offset': offset, 'bytes': len(wire), 'sha256': digest(wire)}))
        offset += len(wire)
    return result


def source_identity(source):
    return {key: source[key] for key in ('path', 'task_id', 'session_id', 'session_meta_sha256', 'physical', 'sessions_root')}


def source_registration(request, session):
    require(isinstance(request, dict) and set(request) == {'task_id', 'transcript', 'expected_bytes', 'expected_sha256'},
            'SOURCE_REGISTRATION_SHAPE')
    task = text(request['task_id'])
    home = os.environ.get('CODEX_HOME')
    require(home and Path(home).is_absolute(), 'HOST_CODEX_HOME_UNAVAILABLE')
    root = physical(Path(home) / 'sessions', directory=True)
    path = physical(request['transcript'])
    require(path.is_relative_to(root) and path.name.startswith('rollout-') and path.name.endswith(task + '.jsonl'),
            'SOURCE_OUTSIDE_NATIVE_SESSION_STORE')
    raw, wires, identity = source_bytes(path)
    require(type(request['expected_bytes']) is int and len(raw) == request['expected_bytes'] and
            digest(raw) == request['expected_sha256'], 'SOURCE_REGISTRATION_PIN')
    parsed = rows(wires); meta = parsed[0][0]
    require(meta['type'] == 'session_meta' and 'metadata' not in meta and
            meta['payload'].get('id') == task and meta['payload'].get('session_id') == session and
            meta['payload'].get('cli_version') == '0.153.4', 'SOURCE_SESSION_META')
    return {'path': str(path), 'task_id': task, 'session_id': session,
            'sessions_root': str(root), 'physical': identity, 'session_meta_sha256': digest(wires[0]),
            'prefix_bytes': len(raw), 'prefix_sha256': digest(raw),
            'provenance': 'HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX',
            'native_producer_runtime_equivalence': 'UNVERIFIED'}


def state_path(store, session):
    return store / 'compaction-audits-v1' / CORE.session_key(session) / 'pending.json'


def blank(session):
    return {'schema': SCHEMA, 'session_id': session, 'revision': 0, 'source': None, 'source_problem': None,
            'signals': 0, 'unresolved_signal_version': 0, 'observations': {}, 'assignments': {},
            'active_child': None, 'native_producer_runtime_equivalence': 'UNVERIFIED'}


def load(store, session):
    path = state_path(store, session)
    if not path.exists():
        return blank(session)
    require(path.stat().st_size <= MAX_STATE, 'PENDING_STATE_BYTE_BOUND')
    value = CORE.read_json(path, 'compaction audit pending state')
    require(set(value) == set(blank(session)) and value['schema'] == SCHEMA and value['session_id'] == session and
            type(value['revision']) is int and isinstance(value['observations'], dict) and
            isinstance(value['assignments'], dict), 'PENDING_STATE_SHAPE')
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
    # H0 attribution does not ask for canonical currentness or a measured epoch.
    CORE.load_owner(store, owner)
    _, value = CORE.load_state(store, 'codex', session)
    binding = CORE.current_record(value, require_active=True)
    CORE.require_external_store(store, binding)
    return binding


def add_observation(state, identifier, kind, proof, version=1):
    prior = state['observations'].get(identifier)
    consumed = prior['consumed_version'] if prior else 0
    state['observations'][identifier] = {'id': identifier, 'kind': kind, 'version': version,
        'consumed_version': consumed, 'proof': proof}


def refresh(state):
    source = state['source']
    if source is None:
        state['source_problem'] = 'NO_REGISTERED_TRANSCRIPT; bounded audit still required for a signal'
        return
    try:
        raw, wires, physical_id = source_bytes(source['path'])
        require(physical_id == source['physical'] and digest(wires[0]) == source['session_meta_sha256'] and
                len(raw) >= source['prefix_bytes'] and digest(raw[:source['prefix_bytes']]) == source['prefix_sha256'],
                'SOURCE_PREFIX_OR_PHYSICAL_ID_CHANGED')
        parsed = rows(wires)
        meta = parsed[0][0]['payload']
        require(meta.get('id') == source['task_id'] and meta.get('session_id') == state['session_id'], 'SOURCE_SESSION_CHANGED')
        group = []
        for row, descriptor in parsed[1:]:
            kind = row['type']; payload = row['payload']
            canonical_marker = kind == 'compacted' or kind == 'event_msg' and payload.get('type') == 'context_compacted'
            corroborating = kind == 'response_item' and payload.get('type') in ('compaction', 'compaction_summary', 'context_compaction')
            if canonical_marker or corroborating:
                require('metadata' not in row, 'CLIENT_AUTHORED_COMPACT_MARKER')
                group.append({**descriptor, 'kind': kind, 'canonical': canonical_marker})
            elif group and (kind == 'turn_context' or kind == 'event_msg' and payload.get('type') == 'task_started'):
                require('metadata' not in row and isinstance(payload.get('turn_id'), str) and payload['turn_id'],
                        'RESUME_IDENTITY_UNAVAILABLE')
                canonical_markers = [item for item in group if item['canonical']]
                proof = {'source': source_identity(source), 'markers': group, 'resume': descriptor,
                         'resume_turn': payload['turn_id'], 'native_producer_runtime_equivalence': 'UNVERIFIED'}
                identifier = 'boundary-' + digest(canonical(proof))
                completed = len(canonical_markers) == 1
                add_observation(state, identifier, 'COMPLETED_RESUMED_BOUNDARY' if completed else 'AMBIGUOUS_MARKER_GROUP', proof)
                group = []
        # A committed marker without a resume is recorded as unresolved, never completed.
        # Its exact bytes remain in the frozen source; it is surfaced in source_problem.
        state['source_problem'] = 'COMPACTION_MARKER_WITHOUT_PROVED_RESUME' if group else None
        state['source']['prefix_bytes'] = len(raw)
        state['source']['prefix_sha256'] = digest(raw)
    except (Refusal, OSError, ValueError, KeyError, TypeError) as exc:
        state['source_problem'] = str(exc)


def outstanding(state):
    return [{'id': item['id'], 'version': item['version'], 'kind': item['kind']}
            for item in state['observations'].values() if item['version'] > item['consumed_version']]


def scope_owners(state, identifier):
    consumed = state['observations'][identifier]['consumed_version']
    owners = [child for child, assignment in state['assignments'].items()
              if any(item['id'] == identifier and item['version'] > consumed
                     for item in assignment['scope'])]
    require(len(owners) <= 1, 'CONFLICTING_SCOPE_OWNERS')
    return owners


def available_scope(state):
    pending = outstanding(state)
    has_claim = any(scope_owners(state, item['id']) for item in pending)
    # Ambiguous observations cannot be called distinct events to evade a claim.
    return [item for item in pending if not scope_owners(state, item['id']) and
            (item['kind'] == 'COMPLETED_RESUMED_BOUNDARY' or not has_claim)]


def decision(state):
    pending = outstanding(state)
    available = available_scope(state)
    assigned = [{**item, 'child_id': scope_owners(state, item['id'])[0]}
                for item in pending if scope_owners(state, item['id'])]
    active = sorted({item['child_id'] for item in assigned})
    return {'schema': 'implementaudit.compaction-audit-decision.v1', **CEILING,
        'decision': 'AUDIT_STATE_REQUIRED' if available else 'WAIT_EXISTING_AUDIT' if pending else 'NO_PENDING_AUDIT',
        'audit_state_required': bool(pending), 'state_dependent_decisions_held': bool(pending),
        'pending': pending, 'available_scope': available, 'assigned_scope': assigned,
        'active_child': active[0] if len(active) == 1 else None, 'active_children': active,
        'source_problem': state['source_problem'],
        'signal_observations': state['signals'], 'native_lifecycle': 'NOT_CLAIMED',
        'native_producer_runtime_equivalence': 'UNVERIFIED'}


def record_signal(store, session, event):
    """Called by the real compact hook before any continuity prerequisite."""
    store = Path(store).absolute()
    binding = attribution(store, session)
    with CORE.writer_lock(store):
        state = load(store, session)
        refresh(state)
        state['signals'] += 1
        # The current callback carries no qualified per-delivery correlation.
        # Descriptor dedup in refresh cannot correlate this delivery to old proof.
        state['unresolved_signal_version'] += 1
        identifier = 'unresolved-signal-' + CORE.session_key(session)
        add_observation(state, identifier, 'UNRESOLVED_SIGNAL', {
            'host_session_id': session, 'signal': 'SessionStart/source=compact',
            'hook_source_sha256': digest((HERE / 'codex-compact-interlock.py').read_bytes()),
            'binding_generation': binding['binding_generation'],
            'logical_occurrence_count': None, 'completion': 'UNRESOLVED', 'resume': 'UNRESOLVED',
            'delivery_count_is_not_occurrence_identity': True}, state['unresolved_signal_version'])
        save(store, state)
        return decision(state)


def code_identity():
    skill = HERE.parent
    paths = [skill / 'SKILL.md', skill.parent / 'audit-state/SKILL.md',
             skill / 'references/child-agents.md', skill / 'references/continuity.md',
             HERE / 'compaction-audit-pending.py', HERE / 'codex-compact-interlock.py']
    paths.append(HERE / 'compaction-result-observation.py')
    paths.append(HERE / 'compaction-result-profile.py')
    return {str(path.relative_to(skill.parent)): digest(path.read_bytes()) for path in paths}


def prepare_obligation(store, state, assignment):
    scope = [item for item in outstanding(state) if scope_owners(state, item['id']) == [assignment['child_id']]]
    scope += available_scope(state)
    require(scope, 'NO_OBSERVABLE_OWNED_SCOPE')
    claims = {item['id']: item for item in assignment['scope']}
    claims.update({item['id']: item for item in scope})
    assignment['scope'] = list(claims.values())
    observation = {'child_id': assignment['child_id'], 'scope': scope, 'code': assignment['code'],
        'source_cutoff': state['source'], 'source_problem': state['source_problem'], 'revision': state['revision']}
    identifier = digest(canonical(observation))
    source = assignment['observation_source']
    obligation = {'schema': 'implementaudit.compaction-obligation.v1',
        'parent_identity': source['parent_identity'], 'actual_child_identity': source['actual_child_identity'],
        'selected_child': 'audit-state', 'observation_id': identifier, 'covered_boundary_versions': scope,
        'observation_source_cutoff': observation['source_cutoff'], 'code_and_skill_pins': assignment['code'],
        'bounded_purpose': assignment['bounded_purpose'], 'authority_ceiling': 'NONE'}
    path = state_path(store, state['session_id']).parent / 'obligations' / (digest(canonical(obligation)) + '.json')
    if path.exists():
        require(CORE.read_json(path, 'immutable compaction obligation') == obligation, 'OBLIGATION_CONFLICT')
    else:
        CORE.atomic_json(path, obligation)
    raw = path.read_bytes()
    pin = {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}
    assignment.setdefault('prepared', {})[identifier] = {'observation': observation,
        'obligation': obligation, 'obligation_pin': pin, 'authorization': None, 'exchange': None}
    return {'obligation': obligation, 'obligation_pin': pin, 'obligation_digest': pin['sha256'], **CEILING}


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
            raise  # Missing, raced or out-of-bound acquisition is not a witness.
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
    # A failed initial bind may never have entered observations. Its saved
    # material refusal still belongs to this assignment and cannot be erased
    # merely by preparing a later observation. Future scopes stay separate.
    for bucket, reason in (('hold_failures', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_DISQUALIFIED'),
                           ('hold_refusals', 'HOLD_PRIOR_EPISODE_PREVIOUSLY_REFUSED')):
        for identifier in assignment.get(bucket, {}):
            if identifier == observation_id:
                continue  # hold_checked owns the current observation's veto.
            prior = assignment.get('prepared', {}).get(identifier)
            require(prior is not None and isinstance(prior.get('observation'), dict)
                    and type(prior['observation'].get('revision')) is int
                    and digest(canonical(prior['observation'])) == identifier, 'HOLD_PRIOR_REFUSAL_SCOPE_UNKNOWN')
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
        # Atomic state reads only: no writer lock creation, source scan or save.
        return decision(load(store, session))
    with CORE.writer_lock(store):
        state = load(store, session)
        if action == 'register-source':
            source = source_registration(request, session)
            require(state['source'] is None or source_identity(state['source']) == source_identity(source),
                    'REGISTERED_SOURCE_REPLACEMENT_REFUSED')
            if state['source'] is not None:
                raw = Path(source['path']).read_bytes()
                old = state['source']
                require(len(raw) >= old['prefix_bytes'] and digest(raw[:old['prefix_bytes']]) == old['prefix_sha256'],
                        'REGISTERED_PREFIX_REWRITE_REFUSED')
                if 'resume_observation_relations' in old:
                    source['resume_observation_relations'] = old['resume_observation_relations']
            state['source'] = source
            refresh(state); save(store, state)
            return {'status': 'SOURCE_REGISTERED_PHYSICAL_ONLY', 'source': source, **CEILING}
        refresh(state)
        if action == 'resume':
            require(request is None or isinstance(request, dict) and set(request) == {'currentness', 'measured_epoch'},
                    'RESUME_OBSERVATION_SHAPE')
            proved = [item for item in outstanding(state) if item['kind'] == 'COMPLETED_RESUMED_BOUNDARY']
            # Invoking resume does not correlate this delivery to any descriptor.
            identifier = 'unresolved-resume-' + CORE.session_key(session)
            prior = state['observations'].get(identifier)
            version = prior['version'] + 1 if prior else 1
            add_observation(state, identifier, 'UNRESOLVED_RESUME_OBSERVATION', {
                'host_session_id': session, 'entry': 'EXPLICIT_GOVERNOR_POST_COMPACTION_RESUME_OBSERVATION',
                'occurrence_proof': 'UNRESOLVED', 'logical_occurrence_count': None,
                'delivery_count_is_not_occurrence_identity': True,
                'observed_limits': request}, version)
            if proved and not state['source_problem']:
                # Relate earlier uncertainty to the observed source cutoff without
                # consuming it or crediting a child that never observed this proof.
                for item in state['observations'].values():
                    if item['kind'] == 'UNRESOLVED_RESUME_OBSERVATION':
                        state['source'].setdefault('resume_observation_relations', {})[item['id']] = {
                            'observation_version': item['version'], 'later_proved_scope': proved,
                            'observed_prefix_bytes': state['source']['prefix_bytes'],
                            'observed_prefix_sha256': state['source']['prefix_sha256'],
                            'retroactive_child_credit': False}
            save(store, state)
            return decision(state)
        require(isinstance(request, dict), 'REQUEST_SHAPE')
        child = text(request.get('child_id'))
        if action == 'reserve':
            require(set(request) in ({'child_id'}, {'child_id', 'bounded_purpose', 'observation_source'}), 'RESERVATION_SHAPE')
            prior = state['assignments'].get(child)
            if prior:
                require(prior['join'] is None, 'USED_CHILD_CONTEXT_REFUSED')
                require(prior['code'] == code_identity() and
                        prior.get('reservation_request', {'child_id': child}) == request, 'CONFLICTING_RESERVATION')
                return {'assignment': prior, **CEILING}
            scope = available_scope(state)
            require(scope, 'NO_UNASSIGNED_INDEPENDENT_SCOPE; existing claims require reconciliation')
            assignment = {'child_id': child, 'scope': scope, 'code': code_identity(),
                'observations': {}, 'return': None, 'join': None, 'native_lifecycle': 'NOT_CLAIMED',
                'reservation_request': request}
            assignment['policy'] = OBSERVATION.fixed_policy(assignment['code'])
            state['assignments'][child] = assignment
            obligation = {}
            if 'observation_source' in request:
                assignment['observation_source'] = OBSERVATION.bind_sources(request['observation_source'], session, child)
                assignment['bounded_purpose'] = text(request['bounded_purpose'])
                obligation = prepare_obligation(store, state, assignment)
            save(store, state)
            return {'assignment': assignment, **obligation, **CEILING}
        assignment = state['assignments'].get(child)
        require(assignment is not None, 'FOREIGN_CHILD')
        require((assignment['join'] is None or action == 'join') and assignment['code'] == code_identity(), 'CHILD_OR_SOURCE_CHANGED')
        if action == 'observe-child' and 'phase' in request:
            require(assignment['return'] is None and assignment.get('observation_source') is not None,
                    'OBSERVATION_SOURCE_UNBOUND_OR_AFTER_RETURN')
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
                validated = OBSERVATION.authorization(assignment['observation_source'], prepared,
                    request['authorization_evidence'], selected_audit_state_pin())
                require(prepared['authorization'] in (None, validated), 'CONFLICTING_PUBLIC_AUTHORIZATION')
                prepared['authorization'] = validated; prepared['delivery_request'] = request
                packet = OBSERVATION.delivery_packet(prepared, validated)
                save(store, state)
                return packet  # The host has not yet produced this tool response; no observation credit here.
            require(phase == 'bind' and set(request) == {'child_id', 'phase', 'observation_id', 'exchange'}, 'OBSERVATION_BIND_SHAPE')
            exchange = OBSERVATION.completed_exchange(assignment['observation_source'], prepared, request['exchange'],
                store, session, owner, selected_audit_state_pin())
            require(prepared['exchange'] in (None, exchange), 'CONFLICTING_CHILD_OBSERVATION_EXCHANGE')
            require(prepared.get('bind_request') in (None, request), 'CONFLICTING_ORIGINAL_BIND_REQUEST')
            held = hold_checked(store, state, assignment, request['observation_id'], lambda:
                OBSERVATION.hold_history(assignment['observation_source'], prepared, exchange, request, store, session, owner,
                    prior_context=prior_history_context(assignment, request['observation_id'])))
            if prepared.get('bound_response') is not None:
                # The same original physical completion was revalidated above.
                # An exact retry must not replace the immutable entry prefix.
                return prepared['bound_response']
            require(prepared.get('hold_prefix') in (None, held), 'HOLD_BIND_PREFIX_ALREADY_SEALED')
            prepared['hold_prefix'] = held
            prepared['exchange'] = exchange
            assignment['observations'][request['observation_id']] = prepared['observation']
            prepared['bind_request'] = request
            prepared['bound_response'] = {'observation_id': request['observation_id'],
                'child_observation_exchange_identity': exchange['identity'], **prepared['observation'], **CEILING}
            save(store, state)
            return prepared['bound_response']
        if action == 'observe-child':
            require(set(request) == {'child_id'} and assignment['return'] is None, 'OBSERVATION_AFTER_RETURN_OR_SHAPE')
            scope = [item for item in outstanding(state) if scope_owners(state, item['id']) == [child]]
            scope += available_scope(state)
            require(scope, 'NO_OBSERVABLE_OWNED_SCOPE')
            claims = {item['id']: item for item in assignment['scope']}
            claims.update({item['id']: item for item in scope})
            assignment['scope'] = list(claims.values())
            observation = {'child_id': child, 'scope': scope, 'code': assignment['code'],
                'source_cutoff': state['source'], 'source_problem': state['source_problem'], 'revision': state['revision']}
            identifier = digest(canonical(observation))
            assignment['observations'][identifier] = observation
            save(store, state)
            return {'observation_id': identifier, **observation, **CEILING}
        if action == 'return':
            require(set(request) == {'child_id', 'observation_id', 'result_evidence'},
                    'RETURN_SHAPE_OR_AUTHORITY_CLAIM')
            require(request['observation_id'] in assignment['observations'], 'UNOBSERVED_RETURN_SCOPE')
            require(request['observation_id'] in assignment.get('prepared', {}), 'ACTUAL_OBLIGATION_EVIDENCE_REQUIRED')
            prepared = assignment['prepared'][request['observation_id']]
            actual = hold_checked(store, state, assignment, request['observation_id'], lambda:
                OBSERVATION.actual_result(assignment['observation_source'], prepared, request['result_evidence'],
                    store, session, owner, selected_audit_state_pin(),
                    prior_context=prior_history_context(assignment, request['observation_id'])))
            result = {'child_id': child, **actual, **CEILING}
            require(assignment['return'] in (None, result), 'CONFLICTING_RETURN')
            assignment['return'] = result; save(store, state)
            return result
        if action == 'join':
            require(set(request) == {'child_id', 'return_digest', 'acceptance'}, 'JOIN_SHAPE')
            result = assignment['return']
            require(result is not None and result['status'] == 'SUCCEEDED' and
                    result['return_digest'] == request['return_digest'], 'EXACT_SUCCESSFUL_RETURN_REQUIRED')
            require(result['observation_id'] in assignment.get('prepared', {}), 'ACTUAL_OBLIGATION_EVIDENCE_REQUIRED')
            prepared = assignment['prepared'][result['observation_id']]
            actual = hold_checked(store, state, assignment, result['observation_id'], lambda:
                OBSERVATION.actual_result(assignment['observation_source'], prepared, result['evidence'],
                    store, session, owner, selected_audit_state_pin(),
                    prior_context=prior_history_context(assignment, result['observation_id'])))
            require(result == {'child_id': child, **actual, **CEILING}, 'IMMUTABLE_ACTUAL_RESULT_CHANGED')
            accepted = OBSERVATION.acceptance(assignment['observation_source'], prepared, actual, request['acceptance'])
            require(assignment.get('accepted') in (None, accepted), 'CONFLICTING_ROOT_ACCEPTANCE')
            observed = assignment['observations'][result['observation_id']]
            require(observed['scope'], 'EMPTY_RETURN_COVERAGE')
            if any(item['kind'] in ('COMPLETED_RESUMED_BOUNDARY', 'AMBIGUOUS_MARKER_GROUP') for item in observed['scope']):
                cutoff = observed['source_cutoff']
                require(cutoff is not None, 'RETURN_SOURCE_CUTOFF_ABSENT')
                raw, wires, identity = source_bytes(cutoff['path'])
                require(identity == cutoff['physical'] and digest(wires[0]) == cutoff['session_meta_sha256'] and
                        len(raw) >= cutoff['prefix_bytes'] and digest(raw[:cutoff['prefix_bytes']]) == cutoff['prefix_sha256'],
                        'RETURN_SOURCE_CUTOFF_CHANGED')
            for covered in observed['scope']:
                item = state['observations'][covered['id']]
                require(scope_owners(state, covered['id']) == [child] and
                        covered['version'] <= item['version'] and any(
                            claim['id'] == covered['id'] and claim['version'] >= covered['version']
                            for claim in assignment['scope']), 'FOREIGN_RETURN_COVERAGE')
            require(assignment.get('policy') == OBSERVATION.fixed_policy(assignment['code']), 'ASSIGNMENT_POLICY_CHANGED')
            acquisition = OBSERVATION.acquire_episode(assignment['observation_source'], prepared, actual, accepted,
                assignment['code'], state_path(store, session).parent, CORE.atomic_json)
            profile = acquisition['profile']
            if assignment['join'] is not None:
                require(acquisition['origin_validated'] is True and
                    assignment['join']['acquisition'] == acquisition, 'ADMITTED_EPISODE_RETRY_DIFFERS')
                return assignment['join']
            if acquisition['origin_validated'] is not True:
                previous = assignment.get('admission_history', [assignment.get('logical_join')])[-1]
                if previous is not None:
                    old = previous['acquisition']
                    require(old['candidate'] == acquisition['candidate'] and
                        (old['profile']['Q'] is None or old['profile']['Q'] == profile['Q']) and
                        (old['episode'] is None or old['episode'] == acquisition['episode']),
                        'CONFLICTING_ACQUISITION_OR_ADMISSION')
                    if old == acquisition:
                        return previous
                projected = json.loads(canonical(state))
                apply_covered_versions(projected, observed['scope'])
                proposal = {'status': 'VERIFIED_LOGICAL_JOIN_PENDING_PROFILE', 'child_id': child,
                    'return_digest': result['return_digest'], 'proposed_consumption': observed['scope'],
                    'projected_pending': outstanding(projected),
                    'pending_consumed': False, 'host_producer_authenticated': False, 'profile': profile,
                    'acquisition': acquisition, 'acceptance': accepted, **CEILING}
                if assignment.get('accepted') is None:
                    assignment['accepted'] = accepted; assignment['logical_join'] = proposal
                assignment.setdefault('admission_history', []).append(proposal)
                save(store, state)
                return proposal
            require(acquisition['episode_record_bound'] and acquisition['episode'] is not None,
                'EXACT_AUTHENTICATED_EPISODE_REQUIRED')
            apply_covered_versions(state, observed['scope'])
            joined = {'status': 'JOINED_EVIDENCE_ONLY', 'child_id': child,
                'return_digest': result['return_digest'], 'covered': observed['scope'],
                'pending_consumed': True, 'host_producer_authenticated': True, 'profile': profile,
                'acquisition': acquisition, **CEILING}
            assignment['accepted'] = accepted; assignment['join'] = joined
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
    parser.add_argument('action', choices=('register-source', 'resume', 'status', 'reserve', 'observe-child', 'return', 'join'))
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


if __name__ == '__main__':
    raise SystemExit(main())
