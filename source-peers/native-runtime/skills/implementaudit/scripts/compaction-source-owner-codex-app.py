"""Existing owner generic nonprotected projection. Historical private selectors are excluded."""
import hashlib
import importlib.util
import os
from pathlib import Path
import re
HERE = Path(__file__).resolve().parent
OBSERVATION = HERE / 'compaction-result-observation.py'
READER = HERE / 'codex-recovery-native-reader.py'

def require(value, reason):
    if not value:
        raise ValueError(reason)

def observation(policy):
    require(policy['descriptor']['profile_id'] == NONPROTECTED_PROFILE, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
    key = str(Path('implementaudit/scripts/compaction-result-observation.py'))
    return _np_module({'path': str(OBSERVATION), 'bytes': OBSERVATION.stat().st_size, 'sha256': policy['code_and_skill_pins'][key]}, 'compaction-result-observation.py')

def host_binding(obs, context, policy):
    require(context['profile_id'] == NONPROTECTED_PROFILE, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
    return nonprotected_host_binding(obs, context, policy)

def sealed_prefix(obs, context, role, end):
    source = context[role]
    path, first = obs.physical(source['path'])
    require(obs.identity(first) == source['physical'] and type(end) is int and (source['metadata']['bytes'] <= end <= first.st_size) and (end <= obs.MAX_TOTAL), 'CURRENT_PUBLIC_PREFIX_BOUND')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        require(obs.identity(os.fstat(stream.fileno())) == source['physical'], 'CURRENT_PUBLIC_PREFIX_CHANGED')
        remaining = end
        while remaining:
            block = stream.read(min(65536, remaining))
            require(block, 'CURRENT_PUBLIC_PREFIX_CHANGED')
            h.update(block)
            remaining -= len(block)
    _, last = obs.physical(path)
    require(obs.identity(last) == source['physical'] and last.st_size >= end, 'CURRENT_PUBLIC_PREFIX_CHANGED')
    return {'role': role, 'physical': source['physical'], 'prefix_bytes': end, 'prefix_sha256': h.hexdigest()}

def active_public_turn(obs, context, role, pin, retained):
    """Only the declared native-turn interval; private content supplies no proof."""
    anchor = context['parent_turn_start'] if role == 'parent' else context['child_activation']
    start = anchor['locator']['offset']
    end = pin['locator']['offset'] + pin['locator']['bytes']
    require(0 <= start < end and end - start <= obs.MAX_TOTAL, 'CURRENT_PUBLIC_TURN_RANGE_BOUND')
    path, info = obs.physical(context[role]['path'])
    require(obs.identity(info) == context[role]['physical'], 'CURRENT_PUBLIC_PREFIX_CHANGED')
    active = None
    count = 0
    with path.open('rb') as stream:
        stream.seek(start)
        position = start
        while position < end:
            raw = stream.readline(min(obs.MAX_RECORD + 1, end - position))
            require(raw and raw.endswith(b'\n') and (len(raw) <= obs.MAX_RECORD), 'CURRENT_PUBLIC_TURN_FRAME')
            row = obs.json.loads(raw, object_pairs_hook=obs.unique)
            count += 1
            require(isinstance(row, dict) and isinstance(row.get('payload'), dict) and isinstance(row.get('type'), str), 'CURRENT_PUBLIC_TURN_FRAME')
            require(count <= obs.MAX_RECORDS, 'CURRENT_PUBLIC_TURN_RANGE_BOUND')
            if row.get('type') == 'event_msg' and row['payload'].get('type') == 'task_started' or row.get('type') == 'turn_context':
                active = row['payload'].get('turn_id')
            position += len(raw)
    require(active == retained['id']['turn_id'], 'CURRENT_PUBLIC_WRONG_ACTIVE_TURN')

def native_public_binding(obs, context, policy, pins):
    require(context['profile_id'] == NONPROTECTED_PROFILE, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
    return nonprotected_public_binding(obs, context, policy, pins)

def tool_calls(obs, records):
    calls = {}
    completed = set()
    inventory = []
    for record in records[1:]:
        row = record['row']
        if row['type'] != 'response_item':
            continue
        payload = row['payload']
        kind = payload.get('type')
        if kind in ('custom_tool_call', 'function_call'):
            call_id = payload.get('call_id')
            require(isinstance(call_id, str) and call_id and (call_id not in calls) and isinstance(payload.get('name'), str) and payload['name'], 'SOURCE_OWNER_EFFECT_CALL_SHAPE')
            command = payload.get('input') if kind == 'custom_tool_call' else payload.get('arguments')
            require(isinstance(command, str), 'SOURCE_OWNER_EFFECT_CALL_SHAPE')
            calls[call_id] = record
            inventory.append({'kind': kind, 'name': payload['name'], 'call_id': call_id, 'call': record['locator'], 'input_sha256': obs.digest(command.encode('utf-8'))})
        elif kind in ('custom_tool_call_output', 'function_call_output'):
            call_id = payload.get('call_id')
            require(isinstance(call_id, str) and call_id in calls and (call_id not in completed) and ((kind == 'custom_tool_call_output') == (calls[call_id]['row']['payload']['type'] == 'custom_tool_call')), 'SOURCE_OWNER_EFFECT_OUTPUT_ASSOCIATION')
            completed.add(call_id)
            item = next((value for value in inventory if value['call_id'] == call_id))
            item['output'] = record['locator']
        elif kind not in ('reasoning', 'message', 'agent_message'):
            raise ValueError('SOURCE_OWNER_UNCLASSIFIED_EFFECT_ROW')
    require(set(calls) == completed, 'SOURCE_OWNER_UNSETTLED_EFFECT_CALL')
    return obs.digest(obs.canonical(inventory))

def boundary_cutoff(obs, context, prepared):
    """Recheck the sealed parent prefix after transport, with unchanged128 MiB bound."""
    cutoff = prepared['obligation']['observation_source_cutoff']
    source = context['parent']
    require(isinstance(cutoff, dict) and cutoff.get('path') == source['path'] and (cutoff.get('physical') == source['physical']) and (type(cutoff.get('prefix_bytes')) is int) and (0 < cutoff['prefix_bytes'] <= obs.MAX_RECORDS * obs.MAX_TOTAL), 'SOURCE_OWNER_BOUNDARY_CUTOFF_CHANGED')
    path, first = obs.physical(source['path'])
    require(obs.identity(first) == source['physical'] and cutoff['prefix_bytes'] <= first.st_size <= obs.MAX_RECORDS * obs.MAX_TOTAL, 'SOURCE_OWNER_BOUNDARY_SOURCE_BOUND')
    digestor = hashlib.sha256()
    with path.open('rb') as stream:
        require(obs.identity(os.fstat(stream.fileno())) == source['physical'], 'SOURCE_OWNER_BOUNDARY_SOURCE_CHANGED')
        remaining = cutoff['prefix_bytes']
        while remaining:
            raw = stream.read(min(65536, remaining))
            require(raw, 'SOURCE_OWNER_BOUNDARY_SOURCE_TRUNCATED')
            digestor.update(raw)
            remaining -= len(raw)
        opened = os.fstat(stream.fileno())
    _, last = obs.physical(path)
    require(obs.identity(first) == obs.identity(opened) == obs.identity(last) and (first.st_size, first.st_mtime_ns) == (opened.st_size, opened.st_mtime_ns) == (last.st_size, last.st_mtime_ns) and (digestor.hexdigest() == cutoff['prefix_sha256']), 'SOURCE_OWNER_BOUNDARY_CUTOFF_CHANGED')

def release_subject(obs, context, prepared, result, accepted, candidate_pin, q_pin, child_terminal, policy=None):
    terminal_row, terminal_pin = obs.resolve_record(context, 'child', child_terminal)
    require(terminal_row['type'] == 'event_msg' and terminal_row['payload'].get('type') == 'task_complete', 'SOURCE_OWNER_CHILD_TERMINAL_ABSENT')
    obs.before(result['identity']['child_final'], terminal_pin)
    end = terminal_pin['locator']['offset'] + terminal_pin['locator']['bytes']
    general = context['profile_id'] in obs.BOUNDARY_PROFILES
    if general:
        boundary_cutoff(obs, context, prepared)
        _, current = obs.physical(context['child']['path'])
        require(end == current.st_size, 'SOURCE_OWNER_TERMINAL_NOT_FINAL')
        activation, _ = obs.resolve_record(context, 'child', context['child_activation']['locator'])
        require(terminal_row['payload'].get('turn_id') == activation['payload'].get('turn_id') and isinstance(terminal_row['payload'].get('turn_id'), str) and terminal_row['payload']['turn_id'], 'SOURCE_OWNER_TERMINAL_TURN_DIFFERS')
    records, prefix = obs.hold_records(context, cutoff=end)
    require(records[-1]['locator'] == terminal_pin['locator'], 'SOURCE_OWNER_TERMINAL_PREFIX_DIFFERS')
    if context['profile_id'] in (obs.CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE):
        require(policy is not None, 'CURRENT_PUBLIC_POLICY_REQUIRED')
        native_public_binding(obs, context, policy, [context['open'], prepared['authorization']['route_record'], prepared['authorization']['record'], result['identity']['child_final'], accepted['record']])
    return {'schema': 'implementaudit.compaction-boundary-release.v1' if general else 'implementaudit.compaction-current-release.v1', **({'covered_boundary_versions': prepared['obligation']['covered_boundary_versions']} if general else {}), 'child_id': context['actual_child_identity']['agent_path'], 'observation_id': prepared['obligation']['observation_id'], 'candidate_sha256': candidate_pin['sha256'], 'Q_sha256': q_pin['sha256'], 'result_digest': result['return_digest'], 'acceptance_digest': obs.digest(obs.canonical(accepted)), 'child_terminal': child_terminal, 'child_prefix_sha256': prefix['prefix_sha256'], 'observed_tool_calls_sha256': tool_calls(obs, records), 'effect_reconciliation': 'NO_UNRECONCILED_EFFECTS', 'explicit_release': 'GRANTED', 'authority_ceiling': 'NONE'}

def _validate_source_episode(candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, custody_root, release_evidence):
    obs = observation(policy)
    if context.get('source_association') == 'PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED':
        require(isinstance(context['child'].get('settings_envelope'), dict), 'SOURCE_OWNER_CURRENT_SETTINGS_MISSING')
    binding = host_binding(obs, context, policy)
    obs.closed(release_evidence, ('child_terminal', 'parent_release'), 'SOURCE_OWNER_RELEASE_EVIDENCE_SHAPE')
    subject = release_subject(obs, context, prepared, result, accepted, candidate_pin, q_pin, release_evidence['child_terminal'], policy=policy)
    row, release_pin = obs.resolve_record(context, 'parent', release_evidence['parent_release'])
    observed = obs.typed_message(row, tuple(subject), subject['schema'], context=context)
    require(observed == subject, 'SOURCE_OWNER_ROOT_RELEASE_DIFFERS')
    obs.before(accepted['record'], release_pin)
    terminal_pin = obs.resolve_record(context, 'child', release_evidence['child_terminal'])[1]
    obs.before(terminal_pin, release_pin)
    public_binding = None
    if context['profile_id'] in (obs.CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE):
        public_binding = native_public_binding(obs, context, policy, [context['open'], prepared['authorization']['route_record'], prepared['authorization']['record'], result['identity']['child_final'], accepted['record'], release_pin])
    return {'schema': 'implementaudit.source-owner-episode-attestation.v1', 'issuer_id': policy['descriptor']['authenticating_source_owner']['issuer_id'], 'policy_digest': policy['policy_digest'], 'candidate_sha256': candidate_pin['sha256'], 'Q_sha256': q_pin['sha256'], 'parent_identity': candidate['parent_identity'], 'actual_child_identity': candidate['actual_child_identity'], 'obligation_digest': candidate['obligation_digest'], 'result_digest': result['return_digest'], 'acceptance_digest': candidate['exact_acceptance_digest'], 'parent_source_physical': context['parent']['physical'], 'child_source_physical': context['child']['physical'], 'host_source_binding': binding, 'release_evidence': release_evidence, 'terminal_effect_release': obs.terminal_release_identity(context, prepared, candidate), 'authority_ceiling': 'NONE', **({'current_public_record_binding': public_binding} if public_binding is not None else {})}
NONPROTECTED_PROFILE = 'codex-app-bounded-public-nonprotected-v1'
NONPROTECTED_SELECTION_PIN = None
ORDINARY_SELECTION_PIN = None

class NonprotectedNativeReadRefusal(ValueError):

    def __init__(self, report):
        super().__init__('NONPROTECTED_NATIVE_READ_UNQUALIFIED')
        self.native_report = report

def _np_read_pin(pin, maximum, custody=None):
    import stat
    require(isinstance(pin, dict) and set(pin) == {'path', 'bytes', 'sha256'} and (type(pin['bytes']) is int) and (0 < pin['bytes'] <= maximum) and isinstance(pin['sha256'], str) and re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'NONPROTECTED_PIN_SHAPE')
    path = Path(pin['path'])
    require(path.is_absolute() and Path(os.path.realpath(path)) == path, 'NONPROTECTED_PIN_ALIAS')
    before = path.stat()
    parents = [(item, item.lstat()) for item in (path, *path.parents)]
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and (before.st_size == pin['bytes']) and all((not stat.S_ISLNK(info.st_mode) and (not getattr(info, 'st_file_attributes', 0) & 1024) for _, info in parents)), 'NONPROTECTED_PIN_PHYSICAL')
    opener = path.open('rb') if custody is None else custody.held_file(path, allow_append=False)
    with opener as stream:
        opened = os.fstat(stream.fileno())
        require((opened.st_dev, opened.st_ino, opened.st_size, opened.st_nlink) == (before.st_dev, before.st_ino, before.st_size, 1), 'NONPROTECTED_PIN_CHANGED')
        raw = stream.read(before.st_size)
        after = os.fstat(stream.fileno())
    require(len(raw) == before.st_size and hashlib.sha256(raw).hexdigest() == pin['sha256'] and ((after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink) == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, 1)) and all(((item.lstat().st_dev, item.lstat().st_ino) == (info.st_dev, info.st_ino) for item, info in parents)), 'NONPROTECTED_PIN_CHANGED')
    return raw

def _np_module(pin, basename, custody=None):
    import types
    require(Path(pin['path']).name == basename and Path(pin['path']).parent == HERE, 'NONPROTECTED_MODULE_OWNER_PATH')
    raw = _np_read_pin(pin, 512 * 1024, custody)
    module = types.ModuleType('_nonprotected_' + basename.replace('.', '_'))
    module.__file__ = pin['path']
    exec(compile(raw, pin['path'], 'exec', dont_inherit=True), module.__dict__)
    return module

def _np_selection():
    import json
    require(NONPROTECTED_SELECTION_PIN is not None, 'NONPROTECTED_FIXED_SELECTION_UNBOUND')
    raw = _np_read_pin(NONPROTECTED_SELECTION_PIN, 256 * 1024)

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'NONPROTECTED_SELECTION_DUPLICATE_KEY')
            result[key] = value
        return result
    selected = json.loads(raw, object_pairs_hook=unique)
    required = {'schema', 'profile_id', 'root_thread_id', 'root_agent_path', 'root_source', 'session_root', 'cwd', 'cli_version', 'native_version', 'desktop_version', 'host_process', 'desktop_process', 'native_executable', 'desktop_executable', 'desktop_asar', 'config_file', 'runtime_helpers', 'episode_owner', 'pending_owner'}
    require(isinstance(selected, dict) and set(selected) == required and (selected['schema'] == 'implementaudit.codex-nonprotected-provider-selection.v1') and (selected['profile_id'] == NONPROTECTED_PROFILE) and (set(selected['runtime_helpers']) == {'bounded_native_reader.py', 'bounded_source_owner.py', 'bounded_file_custody.py'}), 'NONPROTECTED_FIXED_SELECTION_SHAPE')
    pointer = selected['pending_owner']
    require(isinstance(pointer, dict) and set(pointer) == {'store', 'session_id', 'owner_id'} and isinstance(pointer['store'], str) and Path(pointer['store']).is_absolute() and (pointer['session_id'] == selected['root_thread_id']) and isinstance(pointer['owner_id'], str) and pointer['owner_id'], 'NONPROTECTED_FIXED_PENDING_OWNER_SHAPE')
    return selected

def _np_runtime(obs, code_pins):
    selected = _np_selection()
    custody = _np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    protocol = _np_module(selected['runtime_helpers']['bounded_native_reader.py'], 'bounded_native_reader.py', custody)
    helpers = _np_module(selected['runtime_helpers']['bounded_source_owner.py'], 'bounded_source_owner.py', custody)
    protocol.custody = helpers.custody = custody
    reader_key = str(Path('implementaudit/scripts/codex-recovery-native-reader.py'))
    require(reader_key in code_pins, 'NONPROTECTED_READER_CODE_PIN_ABSENT')
    reader_pin = {'path': str(READER), 'bytes': READER.stat().st_size, 'sha256': code_pins[reader_key]}
    reader = _np_module(reader_pin, 'codex-recovery-native-reader.py', custody)
    require(callable(getattr(reader, 'native_read_nonprotected', None)), 'NONPROTECTED_READER_ENTRY_ABSENT')
    return (selected, custody, protocol, helpers, reader)

def _np_call(runtime, methods, child_id=None):
    selected, _, protocol, helpers, reader = runtime
    report = reader.native_read_nonprotected(selected, methods, child_id=child_id, protocol_helper=protocol)
    try:
        helpers.qualified_protocol(report)
    except ValueError as error:
        raise NonprotectedNativeReadRefusal(report) from error
    return report

def _np_episode(runtime):
    selected, custody, _, _, _ = runtime
    owner = selected['episode_owner']
    require(isinstance(owner, dict) and set(owner) == {'module_pin', 'repository', 'controller'} and isinstance(owner['repository'], str) and isinstance(owner['controller'], str) and owner['controller'], 'NONPROTECTED_CANONICAL_EPISODE_OWNER_UNBOUND')
    route = _np_module(owner['module_pin'], 'route-transaction.py', custody)
    require(callable(getattr(route, 'read_current_episode_binding_v1', None)), 'NONPROTECTED_CANONICAL_EPISODE_ENTRY_ABSENT')
    binding = route.read_current_episode_binding_v1(Path(owner['repository']), owner['controller'])
    require(binding.get('schema') == 'implementaudit.r0033-current-episode-binding.v1' and binding.get('authority_ceiling') == 'NONE' and (binding.get('canonical_route_currentness') == 'VALIDATED_AT_READ') and (binding.get('host_and_scope', {}).get('host_session_id') == selected['root_thread_id']) and isinstance(binding.get('logical_task'), str) and re.fullmatch('[a-z0-9][a-z0-9_-]{0,127}', binding['logical_task']) and isinstance(binding.get('opening_digest'), str), 'NONPROTECTED_CANONICAL_EPISODE_BINDING')
    return binding

def _np_subject(runtime):
    selected, _, _, helpers, _ = runtime
    episode = _np_episode(runtime)
    parent_id = selected['root_thread_id']
    params = {'parentThreadId': parent_id, 'sourceKinds': ['subAgent'], 'limit': 100, 'cursor': None, 'archived': False, 'useStateDbOnly': True}
    catalog = _np_call(runtime, [('thread/list', params)])
    records = catalog['responses'][0]['threads']
    expected_path = selected['root_agent_path'] + '/' + episode['logical_task']
    matches = []
    for record in records:
        require(isinstance(record.get('path'), str), 'NONPROTECTED_CATALOG_PHYSICAL_PATH_ABSENT')
        require(helpers.canonical_path(record['path']).is_relative_to(helpers.canonical_path(selected['session_root'])) and Path(record['path']).name.endswith('-' + record['id'] + '.jsonl'), 'NONPROTECTED_CATALOG_SOURCE_NAMESPACE')
        source = helpers.header(record)
        require(source['metadata'].get('id') == record['id'] and source['metadata'].get('parent_thread_id') == parent_id, 'NONPROTECTED_CATALOG_HEADER_PARENT_DIFFERS')
        if source['metadata'].get('agent_path') == expected_path:
            matches.append((record['id'], source))
    require(len(matches) == 1, 'NONPROTECTED_CANONICAL_CHILD_NOT_UNIQUE')
    child_id, discovered = matches[0]
    metadata = _np_call(runtime, [('thread/read', {'threadId': ident, 'includeTurns': False}) for ident in (parent_id, child_id)], child_id)
    parent, child = [row['thread'] for row in metadata['responses']]
    sources = {'parent': helpers.header(parent), 'child': helpers.header(child)}
    helpers.validate_relation(selected, parent, child, sources['parent']['metadata'], sources['child']['metadata'])
    require(child['id'] == child_id and all((sources['child'][key] == discovered[key] for key in ('physical', 'header_prefix', 'metadata'))) and (sources['child']['metadata']['agent_path'] == expected_path) and (helpers.canonical_path(parent['path']) == helpers.canonical_path(selected['root_source'])), 'NONPROTECTED_SELECTED_NATIVE_CHILD_CHANGED')
    require(_np_episode(runtime) == episode, 'NONPROTECTED_CANONICAL_EPISODE_CHANGED_DURING_NATIVE_READ')
    return {'episode': episode, 'metadata': metadata, 'catalog': catalog, 'sources': sources, 'parent_identity': {'thread_id': parent_id, 'agent_path': selected['root_agent_path']}, 'actual_child_identity': {'thread_id': child_id, 'parent_thread_id': parent_id, 'agent_path': expected_path}}

def nonprotected_bind_sources(obs, request, code_pins):
    """Bind actual source-selected child to canonical OPEN and real host events."""
    import contextlib
    import json
    require(isinstance(request, dict) and set(request) == {'open', 'spawn_call', 'spawn_output', 'child_activation', 'parent_turn_start'}, 'NONPROTECTED_PUBLIC_LOCATOR_REQUEST_SHAPE')
    runtime = _np_runtime(obs, code_pins)
    selected, custody, _, _, _ = runtime
    with _np_provider_guard(runtime):
        subject = _np_subject(runtime)
        require(subject['episode']['selected_child_role'] == 'audit-state', 'NONPROTECTED_RECONCILIATION_ROLE_REQUIRED')
        context = {'profile_id': NONPROTECTED_PROFILE, 'parent_identity': subject['parent_identity'], 'actual_child_identity': subject['actual_child_identity'], 'logical_child_id': subject['actual_child_identity']['agent_path'], 'canonical_episode_binding': subject['episode'], '_source_profile_code_pins': code_pins, 'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED', 'host_producer_authenticated': False}
        for role in ('parent', 'child'):
            source = subject['sources'][role]
            prefix = source['header_prefix']
            path = source['physical']['path']
            with custody.held_file(path) as stream:
                raw = stream.read(prefix['bytes'])
            require(hashlib.sha256(raw).hexdigest() == prefix['sha256'], 'NONPROTECTED_HEADER_CHANGED')
            header = json.loads(raw, object_pairs_hook=obs.unique)
            require(header['type'] == 'session_meta' and header['ordinal'] == 0, 'NONPROTECTED_HEADER_ORDINAL')
            metadata = {'offset': 0, 'bytes': prefix['bytes'], 'sha256': prefix['sha256'], 'embedded_ordinal': 0, 'physical_line': 1}
            context[role] = {'path': path, 'physical': {key: source['physical'][key] for key in ('device', 'inode')}, 'metadata': metadata, 'metadata_payload_digest': obs.digest(obs.canonical(header['payload'])), 'history_start_ordinal': 1 if role == 'child' else 0, 'allowed_ranges': [{'offset': index * obs.MAX_TOTAL, 'bytes': obs.MAX_TOTAL} for index in range(obs.MAX_RECORDS)], 'canonical_open_binding_digest': subject['episode']['opening_digest']}
        with contextlib.ExitStack() as held:
            for role in ('parent', 'child'):
                held.enter_context(custody.held_file(context[role]['path']))
            opened, open_pin = obs.resolve_record(context, 'parent', request['open'])
            spawn, spawn_pin = obs.resolve_record(context, 'parent', request['spawn_call'])
            output, output_pin = obs.resolve_record(context, 'parent', request['spawn_output'])
            activation, activation_pin = obs.resolve_record(context, 'child', request['child_activation'])
            turn, turn_pin = obs.resolve_record(context, 'parent', request['parent_turn_start'])
            call = spawn['payload']
            reply = output['payload']
            require(spawn['type'] == output['type'] == 'response_item' and call.get('type') == 'function_call' and (call.get('namespace') == 'collaboration') and (call.get('name') == 'spawn_agent') and (reply.get('type') == 'function_call_output') and (reply.get('call_id') == call.get('call_id')) and isinstance(call.get('call_id'), str), 'ACTUAL_SPAWN_CALL_OUTPUT_ASSOCIATION')
            args = json.loads(call['arguments'], object_pairs_hook=obs.unique)
            require(args.get('task_name') == subject['episode']['logical_task'] and args.get('fork_turns') == 'none' and (json.loads(reply['output'], object_pairs_hook=obs.unique) == {'task_name': context['actual_child_identity']['agent_path']}), 'NONPROTECTED_CANONICAL_FRESH_SPAWN_DIFFERS')
            obs.visible(opened, {'CHILD_TASK': args['task_name'], 'CHILD_SKILL_SELECTED': 'audit-state', 'STATUS': 'OPEN', 'LOAD': 'UNVERIFIED'}, context=context)
            require(activation['type'] == 'event_msg' and activation['payload'].get('type') == 'task_started' and (activation['ordinal'] == 1) and (request['child_activation']['offset'] == context['child']['metadata']['bytes']) and (turn['type'] == 'event_msg') and (turn['payload'].get('type') == 'task_started'), 'NONPROTECTED_ACTIVATION_BOUNDARY')
            obs.before(turn_pin, open_pin)
            obs.before(open_pin, spawn_pin)
            obs.before(spawn_pin, output_pin)
            obs.before(output_pin, activation_pin)
        context.update(open=open_pin, spawn_call=spawn_pin, spawn_output=output_pin, child_activation=activation_pin, parent_turn_start=turn_pin)
        with contextlib.ExitStack() as held:
            for role in ('parent', 'child'):
                held.enter_context(custody.held_file(context[role]['path']))
            context['fresh_child_boundary'] = obs.fresh_child_boundary(context)
        require(_np_episode(runtime) == subject['episode'], 'NONPROTECTED_OPEN_CHANGED_DURING_BIND')
        return context

def nonprotected_fixed_policy(obs, code_pins):
    selected, _, _, _, _ = _np_runtime(obs, code_pins)
    require(isinstance(selected['episode_owner'], dict) and selected['episode_owner'].get('module_pin') is not None, 'NONPROTECTED_CANONICAL_EPISODE_OWNER_UNBOUND')

    def code_pin(filename):
        key = str(Path('implementaudit/scripts') / filename)
        require(key in code_pins, 'NONPROTECTED_OWNER_CODE_PIN_ABSENT')
        pin = {'path': str(HERE / filename), 'bytes': (HERE / filename).stat().st_size, 'sha256': code_pins[key]}
        _np_read_pin(pin, 512 * 1024)
        return pin
    provider = {'profile_id': NONPROTECTED_PROFILE, 'selection_pin': dict(NONPROTECTED_SELECTION_PIN), 'native_version': selected['native_version'], 'native_executable': selected['native_executable'], 'desktop_version': selected['desktop_version'], 'desktop': selected['desktop_executable'], 'desktop_asar': selected['desktop_asar'], 'config_identity_only': selected['config_file']}
    descriptor = {'schema': 'implementaudit.compaction-fixed-acquisition-policy.v1', 'profile_id': NONPROTECTED_PROFILE, 'custody_namespace': 'result-observations-v1', 'qualification_key': 'qualification/Q.json', 'provider_selection': provider, 'authenticating_source_owner': {'issuer_id': 'codex-app-canonical-episode-public-source-v1', 'module_pin': code_pin('compaction-source-owner-codex-app.py'), 'native_reader_pin': code_pin('codex-recovery-native-reader.py'), 'native_binary': selected['native_executable'], 'desktop_executable': selected['desktop_executable'], 'desktop_asar': selected['desktop_asar'], 'config_file': selected['config_file']}, 'exact_host_tuple': {'source_header_cli_version': selected['cli_version'], 'provider_selection_sha256': NONPROTECTED_SELECTION_PIN['sha256'], 'native_version': selected['native_version'], 'native_executable_sha256': selected['native_executable']['sha256'], 'desktop_package_version': selected['desktop_version'], 'desktop_executable_sha256': selected['desktop_executable']['sha256'], 'desktop_asar_sha256': selected['desktop_asar']['sha256'], 'config_sha256': selected['config_file']['sha256']}}
    value = {'descriptor': descriptor, 'code_and_skill_pins': code_pins}
    return {**value, 'policy_digest': obs.digest(obs.canonical(value))}

def _np_provider_guard(runtime):
    import contextlib
    selected, custody, protocol, helpers, _ = runtime

    @contextlib.contextmanager
    def guard():
        with contextlib.ExitStack() as stack:
            pins = {}
            for key, maximum in (('native_executable', 512 * 1024 * 1024), ('desktop_executable', 512 * 1024 * 1024), ('desktop_asar', 1024 * 1024 * 1024), ('config_file', 65536)):
                pin = selected[key]
                require(type(pin.get('bytes')) is int and 0 < pin['bytes'] <= maximum, 'NONPROTECTED_PROVIDER_BOUND')
                stream = stack.enter_context(custody.held_file(pin['path'], allow_append=False))
                before = os.fstat(stream.fileno())
                require(before.st_size == pin['bytes'] and before.st_nlink == 1, 'NONPROTECTED_PROVIDER_IDENTITY')
                remaining = before.st_size
                digestor = hashlib.sha256()
                while remaining:
                    require(os.fstat(stream.fileno()).st_size == before.st_size, 'NONPROTECTED_PROVIDER_CHANGED')
                    block = stream.read(min(1024 * 1024, remaining))
                    require(block, 'NONPROTECTED_PROVIDER_TRUNCATED')
                    digestor.update(block)
                    remaining -= len(block)
                require(digestor.hexdigest() == pin['sha256'], 'NONPROTECTED_PROVIDER_DIGEST_CHANGED')
                pins[key] = (stream, before)
            host = helpers.owning_host(selected, protocol)
            yield host
            require(helpers.owning_host(selected, protocol) == host, 'NONPROTECTED_OWNING_HOST_CHANGED')
            for stream, before in pins.values():
                after = os.fstat(stream.fileno())
                require((after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink) == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, 1), 'NONPROTECTED_PROVIDER_CHANGED')
    return guard()

def nonprotected_host_binding(obs, context, policy):
    runtime = _np_runtime(obs, policy['code_and_skill_pins'])
    selected = runtime[0]
    require(nonprotected_fixed_policy(obs, policy['code_and_skill_pins']) == policy, 'NONPROTECTED_FIXED_P_CHANGED')
    with _np_provider_guard(runtime):
        subject = _np_subject(runtime)
        require(subject['parent_identity'] == context['parent_identity'] and subject['actual_child_identity'] == context['actual_child_identity'] and (subject['episode']['opening_digest'] == context['canonical_episode_binding']['opening_digest']), 'NONPROTECTED_CANONICAL_CONTEXT_CHANGED')
        for role in ('parent', 'child'):
            require(subject['sources'][role]['physical']['path'] == context[role]['path'] and {key: subject['sources'][role]['physical'][key] for key in ('device', 'inode')} == context[role]['physical'], 'NONPROTECTED_CONTEXT_PHYSICAL_CHANGED')
        responses = subject['metadata']['responses']
    owner = policy['descriptor']['authenticating_source_owner']
    return {'schema': 'implementaudit.codex-app-exact-source-binding.v1', 'native_reader_sha256': owner['native_reader_pin']['sha256'], 'provider_selection_sha256': NONPROTECTED_SELECTION_PIN['sha256'], 'native_version': selected['native_version'], 'native_executable_sha256': selected['native_executable']['sha256'], 'desktop_executable_sha256': selected['desktop_executable']['sha256'], 'desktop_asar_sha256': selected['desktop_asar']['sha256'], 'config_sha256': selected['config_file']['sha256'], 'parent_thread_read_response_sha256': responses[0]['response_sha256'], 'child_thread_read_response_sha256': responses[1]['response_sha256'], 'parent_source_physical': context['parent']['physical'], 'child_source_physical': context['child']['physical'], 'authority_ceiling': 'NONE'}

def nonprotected_public_binding(obs, context, policy, pins):
    runtime = _np_runtime(obs, policy['code_and_skill_pins'])
    selected, custody, _, _, _ = runtime
    require(context['profile_id'] == NONPROTECTED_PROFILE and 0 < len(pins) <= 16, 'NONPROTECTED_PUBLIC_SCOPE')
    with _np_provider_guard(runtime):
        episode = _np_episode(runtime)
        require(episode['opening_digest'] == context['canonical_episode_binding']['opening_digest'], 'NONPROTECTED_OPEN_BINDING_CHANGED')
        requests = []
        selected_records = []
        ends = {}
        for pin in pins:
            role = pin['role']
            source = context[role]
            with custody.held_file(source['path']):
                row, checked = obs.resolve_record(context, role, pin['locator'])
                require(checked == pin, 'NONPROTECTED_PUBLIC_PIN_CHANGED')
                retained = obs.current_retained_locator(row, context)
                body = obs.public_message(row, row['payload']['phase'], context=context)
                active_public_turn(obs, context, role, pin, retained)
            ident = retained['id']
            selected_records.append((pin, retained, body, row['payload']['phase']))
            requests.append(('thread/items/read', {'threadId': context['parent_identity']['thread_id'] if role == 'parent' else context['actual_child_identity']['thread_id'], 'turnId': ident['turn_id'], 'itemIds': [ident['message_id']]}))
            ends[role] = max(ends.get(role, 0), pin['locator']['offset'] + pin['locator']['bytes'])
        prefixes = []
        for role, end in sorted(ends.items()):
            with custody.held_file(context[role]['path']):
                prefixes.append(sealed_prefix(obs, context, role, end))
        require(len(requests) <= 8, 'NONPROTECTED_PUBLIC_REQUEST_BOUND')
        report = _np_call(runtime, requests, context['actual_child_identity']['thread_id'])
        records = []
        for (pin, retained, body, phase), response in zip(selected_records, report['responses']):
            ident = retained['id']
            native = response['items'][0]
            require(native == {'id': ident['message_id'], 'turn_id': ident['turn_id'], 'phase': phase, 'body_bytes': len(body.encode('utf-8')), 'body_sha256': obs.digest(body.encode('utf-8'))}, 'NONPROTECTED_PUBLIC_NATIVE_DIFFERS')
            records.append({'role': pin['role'], 'pin': pin, 'id': ident['message_id'], 'turn_id': ident['turn_id'], 'revision': retained['revision'], 'phase': phase, 'full_body_sha256': native['body_sha256'], 'native_response_sha256': response['response_sha256']})
        after = []
        for role, end in sorted(ends.items()):
            with custody.held_file(context[role]['path']):
                after.append(sealed_prefix(obs, context, role, end))
        require(after == prefixes and _np_episode(runtime) == episode, 'NONPROTECTED_PUBLIC_CUTOFF_OR_EPISODE_CHANGED')
    return {'schema': 'implementaudit.nonprotected-native-public-record-binding.v1', 'records': records, 'source_prefixes': prefixes, 'anchor_response_sha256s': [], 'canonical_episode_binding': episode, 'authority_ceiling': 'NONE'}

def nonprotected_sources_guard(obs, context, code_pins):
    import contextlib
    runtime = _np_runtime(obs, code_pins)
    selected, custody, _, helpers, _ = runtime

    @contextlib.contextmanager
    def guard():
        require(context['profile_id'] == NONPROTECTED_PROFILE and context['parent_identity']['thread_id'] == selected['root_thread_id'], 'NONPROTECTED_SOURCE_GUARD_SCOPE')
        expected = selected['root_agent_path'] + '/' + context['canonical_episode_binding']['logical_task']
        with contextlib.ExitStack() as stack:
            for role in ('parent', 'child'):
                source = context[role]
                path = custody.lexical_path(source['path'])
                if role == 'parent':
                    require(path == custody.lexical_path(selected['root_source']), 'NONPROTECTED_ROOT_SOURCE_CHANGED')
                else:
                    require(path.is_relative_to(custody.lexical_path(selected['session_root'])) and path.name.endswith('-' + context['actual_child_identity']['thread_id'] + '.jsonl'), 'NONPROTECTED_CHILD_SOURCE_NAMESPACE')
                stack.enter_context(custody.held_file(path))
                observed = helpers.header({'path': str(path)})
                require({key: observed['physical'][key] for key in ('device', 'inode')} == source['physical'] and observed['header_prefix']['sha256'] == source['metadata']['sha256'] and (observed['metadata']['cli_version'] == selected['cli_version']), 'NONPROTECTED_SOURCE_GUARD_CHANGED')
                if role == 'child':
                    require(observed['metadata'].get('id') == context['actual_child_identity']['thread_id'] and observed['metadata'].get('parent_thread_id') == selected['root_thread_id'] and (observed['metadata'].get('agent_path') == expected), 'NONPROTECTED_CHILD_HEADER_BINDING')
            yield
    return guard()

def validate(candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, custody_root, release_evidence):
    """The original final validator runs under the new source custody guard."""
    if context['profile_id'] != NONPROTECTED_PROFILE:
        return _validate_source_episode(candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, custody_root, release_evidence)
    obs = observation(policy)
    with nonprotected_sources_guard(obs, context, policy['code_and_skill_pins']):
        return _validate_source_episode(candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, custody_root, release_evidence)


def _ordinary_selection_v1():
    import json
    require(ORDINARY_SELECTION_PIN is not None, 'ORDINARY_SELECTION_UNBOUND')
    selected = json.loads(_np_read_pin(ORDINARY_SELECTION_PIN, 256 * 1024), object_pairs_hook=_ordinary_unique_v1)
    fields = {'schema', 'profile_id', 'instance_selection', 'root_thread_id', 'root_agent_path',
        'root_source', 'session_root', 'cwd', 'cli_version', 'native_version', 'desktop_version',
        'native_executable', 'desktop_executable', 'desktop_asar', 'config_file', 'python_executable',
        'runtime_helpers', 'episode_owner', 'receiving'}
    require(type(selected) is dict and set(selected) == fields and
            selected['schema'] == 'implementaudit.codex-ordinary-selection.v1' and
            selected['profile_id'] == 'codex-app-ordinary-review-v1' and
            selected['instance_selection'] == 'EXACT_ROOT_EXECUTION_ANCESTRY' and selected['root_agent_path'] == '/root',
            'ORDINARY_SELECTION_SHAPE')
    require(set(selected['runtime_helpers']) == {'bounded_native_reader.py', 'bounded_source_owner.py', 'bounded_file_custody.py'},
            'ORDINARY_HELPER_POPULATION')
    receiving = selected['receiving']
    require(type(receiving) is dict and set(receiving) == {'artifact_root', 'review_evidence_path', 'receiving_evidence_path',
        'graph_owner', 'receiver_node', 'consumer', 'h0_store', 'h0_owner_id'}, 'ORDINARY_RECEIVING_SELECTION')
    for key in ('artifact_root', 'review_evidence_path', 'receiving_evidence_path', 'h0_store'):
        require(type(receiving[key]) is str and Path(receiving[key]).is_absolute(), 'ORDINARY_SELECTED_PATH')
    require(receiving['review_evidence_path'] != receiving['receiving_evidence_path'], 'ORDINARY_EVIDENCE_SLOT_ALIAS')
    return selected


def _ordinary_unique_v1(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'ORDINARY_DUPLICATE_KEY')
        value[key] = item
    return value


def _ordinary_modules_v1(selected):
    custody = _np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    protocol = _np_module(selected['runtime_helpers']['bounded_native_reader.py'], 'bounded_native_reader.py', custody)
    helpers = _np_module(selected['runtime_helpers']['bounded_source_owner.py'], 'bounded_source_owner.py', custody)
    protocol.custody = helpers.custody = custody
    pins = {}
    names = ('route-transaction.py', 'compaction-audit-pending.py', 'compaction-result-observation.py',
        'compaction-source-owner-codex-app.py', 'bounded_source_owner.py', 'bounded_native_reader.py',
        'bounded_file_custody.py', 'codex-recovery-native-reader.py', 'host-session-binding.py',
        'compile-work-graph.py', 'claim-run.sh', 'validate-run-root.sh', 'route_request_policy.py')
    paths = [HERE / name for name in names] + [HERE.parent / 'SKILL.md', HERE.parent.parent / 'audit-assess/SKILL.md',
        HERE.parent / 'references/child-agents.md', HERE.parent / 'references/continuity.md']
    for path in paths:
        with custody.held_file(path, allow_append=False) as stream:
            info = os.fstat(stream.fileno())
            require(0 < info.st_size <= 512 * 1024 and info.st_nlink == 1, 'ORDINARY_CODE_BOUND')
            raw = stream.read(info.st_size)
            require(len(raw) == info.st_size, 'ORDINARY_CODE_TRUNCATED')
        pins[path.relative_to(HERE.parent.parent).as_posix()] = hashlib.sha256(raw).hexdigest()
    def module(name):
        path = HERE / name
        return _np_module({'path': str(path), 'bytes': path.stat().st_size,
                          'sha256': pins['implementaudit/scripts/' + name]}, name, custody)
    return (selected, custody, protocol, helpers, module('codex-recovery-native-reader.py')), module('compaction-result-observation.py'), pins


def _ordinary_receiver_input_v1(selected, obs):
    command = '& ' + obs.shell_literal(selected['python_executable']['path'])
    command += ' -I -S -B ' + obs.shell_literal(str(Path(__file__).resolve())) + ' --ordinary-execute'
    return obs.tool_input(command) + '\n'


def ordinary_policy_v1():
    """Prospective P. Put its digest in the immutable R0033 mission before OPEN."""
    selected = _ordinary_selection_v1()
    _, obs, pins = _ordinary_modules_v1(selected)
    receiving = selected['receiving']
    return {'schema': 'implementaudit.ordinary-native-policy.v1', 'profile_id': obs.ORDINARY_PROFILE,
        'selection_pin': dict(ORDINARY_SELECTION_PIN), 'instance_selection': selected['instance_selection'],
        'provider': {k: selected[k] for k in ('native_executable', 'desktop_executable', 'desktop_asar', 'config_file', 'python_executable')},
        'code_pins': pins, 'receiver_argv': [selected['python_executable']['path'], '-I', '-S', '-B', str(Path(__file__).resolve()), '--ordinary-receiver'],
        'receiver_node': receiving['receiver_node'], 'consumer': receiving['consumer'],
        'artifact_root': receiving['artifact_root'], 'root_thread_id': selected['root_thread_id'], 'root_agent_path': selected['root_agent_path']}


def ordinary_receiver_tool_input_v1():
    selected = _ordinary_selection_v1()
    _, obs, _ = _ordinary_modules_v1(selected)
    return _ordinary_receiver_input_v1(selected, obs)


def _ordinary_provider_guard_v1(runtime):
    import contextlib
    selected, custody, protocol, helpers, _ = runtime
    @contextlib.contextmanager
    def guard():
        with contextlib.ExitStack() as stack:
            held = []
            # All immutable pins are checked BEFORE any native app-server read.
            for key, maximum in (('native_executable', 512 * 1024 * 1024), ('desktop_executable', 512 * 1024 * 1024),
                ('desktop_asar', 1024 * 1024 * 1024), ('config_file', 65536), ('python_executable', 128 * 1024 * 1024)):
                pin = selected[key]
                require(set(pin) == {'path', 'bytes', 'sha256'} and type(pin['bytes']) is int and 0 < pin['bytes'] <= maximum,
                        'ORDINARY_PROVIDER_PIN')
                stream = stack.enter_context(custody.held_file(pin['path'], allow_append=False))
                info = os.fstat(stream.fileno())
                require(info.st_size == pin['bytes'] and info.st_nlink == 1, 'ORDINARY_PROVIDER_IDENTITY')
                checksum = hashlib.sha256(); remaining = pin['bytes']
                while remaining:
                    raw = stream.read(min(65536, remaining))
                    require(raw, 'ORDINARY_PROVIDER_TRUNCATED'); checksum.update(raw); remaining -= len(raw)
                require(checksum.hexdigest() == pin['sha256'], 'ORDINARY_PROVIDER_DIGEST_CHANGED')
                held.append((stream, info))
            host = helpers.owning_ordinary_host(selected, protocol)
            yield
            require(helpers.owning_ordinary_host(selected, protocol) == host, 'ORDINARY_PROCESS_INSTANCE_CHANGED')
            for stream, before in held:
                after = os.fstat(stream.fileno())
                require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_nlink) ==
                        (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink), 'ORDINARY_PROVIDER_CHANGED')
    return guard()


def _ordinary_artifact_v1(obs, selected, pin):
    root, _ = obs.physical(pin['path'])
    allowed = Path(selected['receiving']['artifact_root']).resolve(strict=True)
    require(root.is_relative_to(allowed), 'ORDINARY_ARTIFACT_OUTSIDE_CUSTODY')
    return obs.artifact(pin, maximum=obs.MAX_TOTAL)


def _ordinary_document_v1(obs, selected, path):
    import json
    file, info = obs.physical(path)
    require(0 < info.st_size <= 8 * 1024 * 1024 and file.is_relative_to(
        Path(selected['receiving']['artifact_root']).resolve(strict=True)), 'ORDINARY_DOCUMENT_BOUND')
    raw = file.read_bytes()
    pin = {'path': str(file), 'bytes': len(raw), 'sha256': obs.digest(raw)}
    require(obs.artifact(pin, maximum=8 * 1024 * 1024)[0] == raw, 'ORDINARY_DOCUMENT_CHANGED')
    return json.loads(raw, object_pairs_hook=obs.unique), pin


def _ordinary_resolve_v1(obs, context, role, locator):
    source = context[role]
    selected = obs.read_records(source['path'], [source['metadata'], locator],
        [{'offset': source['metadata']['offset'], 'bytes': source['metadata']['bytes']},
         {'offset': locator['offset'], 'bytes': locator['bytes']}], source['physical'])['records']
    meta, row = selected[0]['row'], selected[1]['row']
    require(meta['type'] == 'session_meta' and obs.digest(obs.canonical(meta['payload'])) == source['metadata_payload_digest'],
            'ORDINARY_SOURCE_HEADER_CHANGED')
    p = row['payload']
    pin = {'path': source['path'], 'physical': source['physical'], 'role': role, 'locator': dict(locator),
           'timestamp': row['timestamp'], 'message_or_call_id': p.get('id', p.get('call_id', p.get('turn_id')))}
    return row, pin


def _ordinary_public_v1(runtime, obs, context, role, locator, phase):
    row, pin = _ordinary_resolve_v1(obs, context, role, locator)
    body = obs.public_message(row, phase, context=context)
    retained = obs.current_retained_locator(row, context)
    ident = retained['id']
    thread = context['actual_child_identity']['thread_id'] if role == 'child' else context['parent_identity']['thread_id']
    report = _np_call(runtime, [('thread/items/read', {'threadId': thread, 'turnId': ident['turn_id'], 'itemIds': [ident['message_id']]})],
                      context['actual_child_identity']['thread_id'])
    expected = {'id': ident['message_id'], 'turn_id': ident['turn_id'], 'phase': phase,
                'body_bytes': len(body.encode('utf-8')), 'body_sha256': obs.digest(body.encode('utf-8'))}
    require(report['responses'][0]['items'] == [expected], 'ORDINARY_NATIVE_PUBLIC_BODY_DIFFERS')
    require(_ordinary_resolve_v1(obs, context, role, locator) == (row, pin), 'ORDINARY_PUBLIC_CHANGED_DURING_READ')
    # No response timestamp/updatedAt/protocol run identifier enters semantics.
    return {'pin': pin, 'message_id': ident['message_id'], 'turn_id': ident['turn_id'], 'revision': retained['revision'],
            'phase': phase, 'body': body, 'body_sha256': expected['body_sha256']}


def _ordinary_review_v1(selected, runtime, obs, pins, policy, canonical):
    import contextlib
    import json
    document, document_pin = _ordinary_document_v1(obs, selected, selected['receiving']['review_evidence_path'])
    obs.closed(document, ('schema', 'records'), 'ORDINARY_REVIEW_EVIDENCE')
    require(document['schema'] == 'implementaudit.ordinary-review-evidence.v1', 'ORDINARY_REVIEW_SCHEMA')
    locators = obs.closed(document['records'], ('open', 'spawn_call', 'spawn_output', 'child_activation', 'child_final', 'acceptance'), 'ORDINARY_REVIEW_LOCATORS')
    subject = _np_subject(runtime)
    require(subject['episode'] == canonical['opening'] and subject['episode']['selected_child_role'] == 'audit-assess', 'ORDINARY_CANONICAL_CHILD')
    context = {'profile_id': obs.NONPROTECTED_PROFILE, 'parent_identity': subject['parent_identity'],
               'actual_child_identity': subject['actual_child_identity']}
    for role in ('parent', 'child'):
        source = subject['sources'][role]
        prefix = source['header_prefix']
        path = source['physical']['path']
        with runtime[1].held_file(path) as stream:
            raw = stream.read(prefix['bytes'])
        require(obs.digest(raw) == prefix['sha256'], 'ORDINARY_METADATA_CHANGED')
        header = json.loads(raw, object_pairs_hook=obs.unique)
        require(header['type'] == 'session_meta' and header['ordinal'] == 0, 'ORDINARY_METADATA_ORDINAL')
        context[role] = {'path': path, 'physical': {k: source['physical'][k] for k in ('device', 'inode')},
            'metadata': {'offset': 0, 'bytes': prefix['bytes'], 'sha256': prefix['sha256'], 'embedded_ordinal': 0, 'physical_line': 1},
            'metadata_payload_digest': obs.digest(obs.canonical(header['payload']))}
    public = [_ordinary_public_v1(runtime, obs, context, 'parent', locators['open'], 'commentary')]
    call, call_pin = _ordinary_resolve_v1(obs, context, 'parent', locators['spawn_call'])
    output, output_pin = _ordinary_resolve_v1(obs, context, 'parent', locators['spawn_output'])
    activation, activation_pin = _ordinary_resolve_v1(obs, context, 'child', locators['child_activation'])
    args = json.loads(call['payload']['arguments'], object_pairs_hook=obs.unique)
    require(call['type'] == output['type'] == 'response_item' and call['payload'].get('type') == 'function_call' and
        call['payload'].get('namespace') == 'collaboration' and call['payload'].get('name') == 'spawn_agent' and
        output['payload'].get('type') == 'function_call_output' and output['payload'].get('call_id') == call['payload'].get('call_id') and
        args.get('task_name') == canonical['opening']['logical_task'] and args.get('fork_turns') == 'none' and
        json.loads(output['payload']['output'], object_pairs_hook=obs.unique) == {'task_name': subject['actual_child_identity']['agent_path']},
        'ORDINARY_ACTUAL_SPAWN_PAIR')
    require(activation['type'] == 'event_msg' and activation['payload'].get('type') == 'task_started' and
        activation['ordinal'] == 1 and locators['child_activation']['offset'] == context['child']['metadata']['bytes'], 'ORDINARY_ACTUAL_ACTIVATION')
    public.append(_ordinary_public_v1(runtime, obs, context, 'child', locators['child_final'], 'final_answer'))
    require(public[-1]['turn_id'] == activation['payload'].get('turn_id'), 'ORDINARY_FRESH_TURN')
    public.append(_ordinary_public_v1(runtime, obs, context, 'parent', locators['acceptance'], 'commentary'))
    owner = {'profile_id': obs.ORDINARY_PROFILE, 'issuer_id': 'codex-app-canonical-ordinary-public-v1',
        'policy_digest': obs._ordinary_hash(policy), 'code_pins': pins, 'canonical_route': canonical['canonical_route'],
        'host_and_scope': canonical['opening']['host_and_scope'], 'opening': canonical['opening'], 'scope': canonical['scope']}
    returned = obs._ordinary_wire(canonical['child_return'])
    payload = obs.closed(returned['payload'], ('schema', 'verdict', 'scope', 'summary', 'members', 'authority_ceiling'), 'ORDINARY_PAYLOAD')
    require(type(payload['members']) is list and 1 <= len(payload['members']) <= 32, 'ORDINARY_MEMBER_POPULATION')
    members = [{'pin': pin, 'physical': _ordinary_artifact_v1(obs, selected, pin)[1]} for pin in payload['members']]
    result = {'packet': canonical['packet'], 'return': canonical['child_return'], 'actual_child_identity': subject['actual_child_identity'],
              'members': members, 'final': public[1]['pin']}
    acceptance = {'decision': canonical['governor_decision'], 'record': public[2]['pin']}
    occurrences = {'scope': 'SELECTED_FRESH_CHILD_ONLY', 'history': 'UNEXAMINED_OUTSIDE_SELECTED_RECORDS', 'open': public[0]['pin'],
        'spawn': {'call': call_pin, 'output': output_pin, 'task_name': args['task_name'], 'fork_turns': args['fork_turns']}, 'activation': activation_pin}
    return owner, result, acceptance, occurrences, context, public, document_pin


def _ordinary_canonical_v1(selected, runtime):
    owner = selected['episode_owner']
    route = _np_module(owner['module_pin'], 'route-transaction.py', runtime[1])
    canonical = route.read_current_ordinary_result_v1(Path(owner['repository']), owner['controller'])
    if canonical['status'] != 'CANONICAL_REVIEW_ABSENT':
        h0_path = HERE / 'host-session-binding.py'
        h0 = _np_module({'path': str(h0_path), 'bytes': h0_path.stat().st_size,
                         'sha256': hashlib.sha256(h0_path.read_bytes()).hexdigest()}, 'host-session-binding.py', runtime[1])
        store = Path(selected['receiving']['h0_store'])
        h0.load_owner(store, selected['receiving']['h0_owner_id'])
        host = canonical['opening']['host_and_scope']
        _, state = h0.load_state(store, host['host_id'], host['host_session_id'])
        binding = h0.current_record(state, require_active=True)
        expected = {'controller_id': host['controller_id'], 'claim_id': host['claim_id'], 'explicit_run_root': host['explicit_run_root'],
            'binding_generation': host['host_binding_generation'], 'applicable_continuity_generation': host['continuity_generation'],
            'applicable_continuity_receipt': host['continuity_receipt']}
        require(all(binding[k] == v for k, v in expected.items()), 'ORDINARY_H0_CURRENTNESS')
    return route, canonical


def _ordinary_sources_v1(context, all_pins):
    return {role: {'path': context[role]['path'], 'physical': context[role]['physical'], 'metadata': context[role]['metadata'],
        'thread_id': context['parent_identity']['thread_id'] if role == 'parent' else context['actual_child_identity']['thread_id'],
        'cutoff': max(pin['locator']['offset'] + pin['locator']['bytes'] for pin in all_pins if pin['role'] == role)}
        for role in ('parent', 'child')}


def ordinary_receiver_check_v1():
    """Actual deterministic receiver command. It grants no JOIN or lifecycle."""
    selected = _ordinary_selection_v1()
    runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1()
    route, canonical = _ordinary_canonical_v1(selected, runtime)
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_PARENT_ACCEPTANCE_ABSENT')
    with _ordinary_provider_guard_v1(runtime):
        owner, result, acceptance, occurrences, context, public, document_pin = _ordinary_review_v1(selected, runtime, obs, pins, policy, canonical)
        # Reuse the strict review-only semantic validator before any success.
        obs.validate_ordinary_review_v1(owner, result, acceptance, occurrences, context, public, policy)
        require(route.read_current_ordinary_result_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller']) == canonical and
                ordinary_policy_v1() == policy and _ordinary_document_v1(obs, selected, document_pin['path'])[1] == document_pin,
                'ORDINARY_RECEIVER_INPUT_CHANGED')
        return obs.ordinary_receiver_value_v1(owner, result, acceptance)


def acquire_selected_ordinary_episode_v1():
    """Explicit live read-only acquisition; frozen consumers never call this."""
    import json
    if ORDINARY_SELECTION_PIN is None:
        obs_path = HERE / 'compaction-result-observation.py'
        obs = _np_module({'path': str(obs_path), 'bytes': obs_path.stat().st_size,
                          'sha256': hashlib.sha256(obs_path.read_bytes()).hexdigest()}, obs_path.name)
        return obs.ordinary_export_unavailable_v1('ORDINARY_SELECTION_UNBOUND')
    selected = _ordinary_selection_v1(); runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1(); route, canonical = _ordinary_canonical_v1(selected, runtime)
    missing = {'CANONICAL_REVIEW_ABSENT': 'CANONICAL_REVIEW_ABSENT', 'OPEN': 'CHILD_RETURN_ABSENT', 'RETURNED': 'PARENT_ACCEPTANCE_ABSENT'}
    if canonical['status'] in missing: return obs.ordinary_export_unavailable_v1(missing[canonical['status']])
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_CANONICAL_STATE')
    execution_receipt = route.read_current_ordinary_execution_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller'])
    if execution_receipt is None: return obs.ordinary_export_unavailable_v1('RECEIVER_EXECUTION_ABSENT')
    for key, reason in (('review_evidence_path', 'REVIEW_EVIDENCE_ABSENT'), ('receiving_evidence_path', 'RECEIVING_EVIDENCE_ABSENT')):
        if not os.path.lexists(selected['receiving'][key]): return obs.ordinary_export_unavailable_v1(reason)
    with _ordinary_provider_guard_v1(runtime):
        owner, result, acceptance, occurrences, context, public, review_pin = _ordinary_review_v1(selected, runtime, obs, pins, policy, canonical)
        document, receiving_pin = _ordinary_document_v1(obs, selected, selected['receiving']['receiving_evidence_path'])
        obs.closed(document, ('schema', 'records', 'graph', 'dispatch', 'work_result', 'join'), 'ORDINARY_RECEIVING_EVIDENCE')
        require(document['schema'] == 'implementaudit.ordinary-receiving-evidence.v1', 'ORDINARY_RECEIVING_SCHEMA')
        locators = obs.closed(document['records'], ('join',), 'ORDINARY_RECEIVER_LOCATORS')
        obs.validate_ordinary_execution_v1(execution_receipt, owner, result, acceptance, policy)
        values = {}
        for key in ('graph', 'dispatch', 'work_result', 'join'):
            raw, _ = _ordinary_artifact_v1(obs, selected, document[key])
            values[key] = json.loads(raw, object_pairs_hook=obs.unique)
        graph_owner = _np_module(selected['receiving']['graph_owner'], 'compile-work-graph.py', runtime[1])
        current_graph = graph_owner.read_native_run_v1(canonical['opening']['host_and_scope']['explicit_run_root'], selected['episode_owner']['repository'])
        joined = graph_owner.reconcile_native_results_v1(values['graph'], current_graph, values['dispatch'], [values['work_result']], policy['consumer'])
        require(joined == values['join'], 'ORDINARY_RECEIVING_JOIN_CHANGED')
        public.append(_ordinary_public_v1(runtime, obs, context, 'parent', locators['join'], 'commentary'))
        receiving = {'process': execution_receipt, 'dispatch': values['dispatch'], 'result': values['work_result'], 'join': joined, 'record': public[-1]['pin']}
        all_pins = [item['pin'] for item in public] + [occurrences['spawn']['call'], occurrences['spawn']['output'], occurrences['activation']]
        value = {'schema': obs.ORDINARY_EXPORT_SCHEMA, 'status': 'AVAILABLE', 'reason_code': None, 'owner': owner,
            'result': result, 'acceptance': acceptance, 'receiving': receiving, 'lifecycle': dict(obs.ORDINARY_LIFECYCLE),
            'occurrences': occurrences, 'custody': {'policy': policy, 'sources': _ordinary_sources_v1(context, all_pins),
                'review_evidence': review_pin, 'receiving_evidence': receiving_pin, 'public_records': public}, 'authority_ceiling': 'NONE'}
        value['export_digest'] = obs._ordinary_hash(value)
        obs.validate_ordinary_episode_export_v1(value)
        require(route.read_current_ordinary_result_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller']) == canonical and
                ordinary_policy_v1() == policy and _ordinary_document_v1(obs, selected, review_pin['path'])[1] == review_pin and
                _ordinary_document_v1(obs, selected, receiving_pin['path'])[1] == receiving_pin, 'ORDINARY_FINAL_INPUT_FENCE')
        require(route.read_current_ordinary_execution_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller']) == execution_receipt,
                'ORDINARY_EXECUTION_RECEIPT_CHANGED')
        for member in result['members']:
            require(_ordinary_artifact_v1(obs, selected, member['pin'])[1] == member['physical'], 'ORDINARY_FINAL_MEMBER_FENCE')
        return value


def execute_ordinary_receiver_v1():
    """Explicit effect entry. Hold exact bytes, run once, retain owner receipt."""
    selected = _ordinary_selection_v1(); runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1(); route, canonical = _ordinary_canonical_v1(selected, runtime)
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_PARENT_ACCEPTANCE_ABSENT')
    repo, controller = Path(selected['episode_owner']['repository']), selected['episode_owner']['controller']
    existing = route.read_current_ordinary_execution_v1(repo, controller)
    if existing is not None:
        return {'status': 'EXISTING_EXECUTION_PRESERVED', 'receipt': existing, 'executed': False}
    path = Path(__file__).resolve()
    source_pin = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': pins['implementaudit/scripts/compaction-source-owner-codex-app.py']}
    with _ordinary_provider_guard_v1(runtime):
        execution = runtime[3].run_held_ordinary_receiver_v1(selected, source_pin)
        execution.update(schema='implementaudit.ordinary-receiver-execution.v1', policy_digest=obs._ordinary_hash(policy),
            opening_digest=canonical['opening']['opening_digest'], return_digest=canonical['child_return']['digest'],
            acceptance_digest=canonical['governor_decision']['digest'])
        require(execution['argv'] == policy['receiver_argv'] and ordinary_policy_v1() == policy and
                route.read_current_ordinary_result_v1(repo, controller) == canonical, 'ORDINARY_EXECUTION_INPUT_CHANGED')
        receipt = route.record_current_ordinary_execution_v1(repo, controller, execution)
        return {'status': 'EXECUTION_RECORDED', 'receipt': receipt, 'executed': True}


if __name__ == '__main__':
    import json
    import sys
    try:
        require(sys.argv[1:] in (['--ordinary-receiver'], ['--ordinary-execute']), 'ORDINARY_RECEIVER_ARGUMENTS')
        value = ordinary_receiver_check_v1() if sys.argv[1] == '--ordinary-receiver' else execute_ordinary_receiver_v1()
        sys.stdout.write(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n')
    except (Exception, SystemExit) as error:
        sys.stderr.write(json.dumps({'schema': 'implementaudit.ordinary-receiver-refusal.v1', 'reason': str(error)}) + '\n')
        raise SystemExit(2)
