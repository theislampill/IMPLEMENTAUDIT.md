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
    require(policy['descriptor']['profile_id'] in SOURCE_PROFILES, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
    key = str(Path('implementaudit/scripts/compaction-result-observation.py'))
    return _np_module({'path': str(OBSERVATION), 'bytes': OBSERVATION.stat().st_size, 'sha256': policy['code_and_skill_pins'][key]}, 'compaction-result-observation.py')

def host_binding(obs, context, policy):
    require(context['profile_id'] in SOURCE_PROFILES, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
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
    require(context['profile_id'] in SOURCE_PROFILES, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
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
    if context['profile_id'] in (obs.CURRENT_BOUNDARY_PROFILE, *SOURCE_PROFILES):
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
    if context['profile_id'] in (obs.CURRENT_BOUNDARY_PROFILE, *SOURCE_PROFILES):
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
    pin = selected_source_pin_v1()
    require(pin is not None, 'NONPROTECTED_FIXED_SELECTION_UNBOUND')
    raw = _np_read_pin(pin, 256 * 1024)

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'NONPROTECTED_SELECTION_DUPLICATE_KEY')
            result[key] = value
        return result
    selected = json.loads(raw, object_pairs_hook=unique)
    if OWNED_STDIO_SELECTION_PIN is not None:
        return validate_owned_stdio_selection_shape_v1(selected)
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
    helpers._observation_owner = obs
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
    episode = _np_episode(runtime)
    subject = (runtime[3]._subject_from_owned_stdio_episode_v1 if runtime[0]['profile_id'] == OWNED_STDIO_PROFILE else runtime[3]._subject_from_episode_v1)(runtime, episode, _np_call)
    require(_np_episode(runtime) == episode, 'NONPROTECTED_CANONICAL_EPISODE_CHANGED_DURING_NATIVE_READ')
    return subject


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
        context = {'profile_id': selected['profile_id'], 'parent_identity': subject['parent_identity'], 'actual_child_identity': subject['actual_child_identity'], 'logical_child_id': subject['actual_child_identity']['agent_path'], 'canonical_episode_binding': subject['episode'], '_source_profile_code_pins': code_pins, 'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED', 'host_producer_authenticated': False}
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
    if selected['profile_id'] == OWNED_STDIO_PROFILE:
        return _as_fixed_policy_v1(obs, code_pins, selected)
    require(isinstance(selected['episode_owner'], dict) and selected['episode_owner'].get('module_pin') is not None, 'NONPROTECTED_CANONICAL_EPISODE_OWNER_UNBOUND')

    def code_pin(filename):
        key = str(Path('implementaudit/scripts') / filename)
        require(key in code_pins, 'NONPROTECTED_OWNER_CODE_PIN_ABSENT')
        pin = {'path': str(HERE / filename), 'bytes': (HERE / filename).stat().st_size, 'sha256': code_pins[key]}
        _np_read_pin(pin, 512 * 1024)
        return pin
    provider = {'profile_id': NONPROTECTED_PROFILE, 'selection_pin': dict(NONPROTECTED_SELECTION_PIN), 'native_version': selected['native_version'], 'native_executable': selected['native_executable'], 'desktop_version': selected['desktop_version'], 'desktop': selected['desktop_executable'], 'desktop_asar': selected['desktop_asar'], 'config_identity_only': selected['config_file']}
    descriptor = {'schema': 'implementaudit.compaction-fixed-acquisition-policy.v1', 'profile_id': NONPROTECTED_PROFILE, 'custody_namespace': 'result-observations-v1', 'qualification_key': 'qualification/Q.json', 'provider_selection': provider, 'authenticating_source_owner': {'issuer_id': 'codex-app-canonical-episode-public-source-v1', 'module_pin': code_pin('compaction-source-owner-codex-app.py'), 'native_reader_pin': code_pin('codex-recovery-native-reader.py'), 'native_binary': selected['native_executable'], 'desktop_executable': selected['desktop_executable'], 'desktop_asar': selected['desktop_asar'], 'config_file': selected['config_file']}, 'exact_host_tuple': {'source_header_cli_version': selected['cli_version'], 'provider_selection_sha256': NONPROTECTED_SELECTION_PIN['sha256'], 'native_version': selected['native_version'], 'native_executable_sha256': selected['native_executable']['sha256'], 'desktop_package_version': selected['desktop_version'], 'desktop_executable_sha256': selected['desktop_executable']['sha256'], 'desktop_asar_sha256': selected['desktop_asar']['sha256'], 'config_sha256': selected['config_file']['sha256']}}
    if capture['schema'] == 'implementaudit.owned-stdio-live-acquisition.v1':
        descriptor['provider_selection']['producer_dependencies'] = selected['producer_dependencies']
    value = {'descriptor': descriptor, 'code_and_skill_pins': code_pins}
    return {**value, 'policy_digest': obs.digest(obs.canonical(value))}

def _np_provider_guard(runtime):
    import contextlib
    selected, custody, protocol, helpers, _ = runtime
    if selected['profile_id'] == OWNED_STDIO_PROFILE:
        return _as_provider_guard_v1(runtime)

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
    if selected['profile_id'] == OWNED_STDIO_PROFILE:
        return _as_host_binding_v1(obs, context, policy, runtime)
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
    if selected['profile_id'] == OWNED_STDIO_PROFILE:
        return _as_public_binding_v1(obs, context, policy, pins, runtime)
    require(context['profile_id'] in SOURCE_PROFILES and 0 < len(pins) <= 16, 'NONPROTECTED_PUBLIC_SCOPE')
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
        require(context['profile_id'] in SOURCE_PROFILES and context['profile_id'] == selected['profile_id'] and context['parent_identity']['thread_id'] == selected['root_thread_id'], 'NONPROTECTED_SOURCE_GUARD_SCOPE')
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
    if context['profile_id'] not in SOURCE_PROFILES:
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
        'runtime_helpers', 'episode_owner', 'receiving', 'code_pins'}
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


def _ordinary_check_code_pins_v1(selected, observed):
    expected = {k: v for k, v in observed.items() if k != 'implementaudit/scripts/compaction-source-owner-codex-app.py'}
    require(selected['code_pins'] == expected, 'ORDINARY_FIXED_CODE_CHANGED')


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
    _ordinary_check_code_pins_v1(selected, pins)
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
    root, before = obs.artifact_preflight(pin, obs.MAX_TOTAL)
    allowed = Path(selected['receiving']['artifact_root']).resolve(strict=True)
    require(root.is_relative_to(allowed), 'ORDINARY_ARTIFACT_OUTSIDE_CUSTODY')
    custody = _np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    raw = _np_read_pin(pin, obs.MAX_TOTAL, custody)
    _, after = obs.physical(root)
    require(obs.identity(before) == obs.identity(after) and before.st_mtime_ns == after.st_mtime_ns,
            'ORDINARY_ARTIFACT_CHANGED')
    return raw, obs.identity(before)


def _ordinary_document_v1(obs, selected, path):
    import json
    file, info = obs.physical(path)
    require(0 < info.st_size <= 8 * 1024 * 1024 and file.is_relative_to(
        Path(selected['receiving']['artifact_root']).resolve(strict=True)), 'ORDINARY_DOCUMENT_BOUND')
    custody = _np_module(selected['runtime_helpers']['bounded_file_custody.py'], 'bounded_file_custody.py')
    with custody.held_file(file, allow_append=False) as stream:
        opened = os.fstat(stream.fileno())
        require(obs.identity(opened) == obs.identity(info) and opened.st_size == info.st_size and
                opened.st_mtime_ns == info.st_mtime_ns, 'ORDINARY_DOCUMENT_CHANGED')
        raw = stream.read(info.st_size + 1)
        after = os.fstat(stream.fileno())
        require(len(raw) == info.st_size and after.st_size == info.st_size and after.st_mtime_ns == info.st_mtime_ns,
                'ORDINARY_DOCUMENT_CHANGED')
    _, final = obs.physical(file)
    require(obs.identity(final) == obs.identity(info) and final.st_mtime_ns == info.st_mtime_ns, 'ORDINARY_DOCUMENT_CHANGED')
    pin = {'path': str(file), 'bytes': len(raw), 'sha256': obs.digest(raw)}
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
    return _ordinary_publics_v1(runtime, obs, context, [(role, locator, phase)])[0]


def _ordinary_publics_v1(runtime, obs, context, specs):
    return runtime[3]._ordinary_public_batch_v1(runtime, obs, context, specs, _np_call, _ordinary_resolve_v1)


def _ordinary_review_v1(selected, runtime, obs, pins, policy, canonical, *, _opening=None,
                        _receiving_join_locator=None):
    import contextlib
    import json
    document, document_pin = _ordinary_document_v1(obs, selected, selected['receiving']['review_evidence_path'])
    obs.closed(document, ('schema', 'records'), 'ORDINARY_REVIEW_EVIDENCE')
    require(document['schema'] == 'implementaudit.ordinary-review-evidence.v1', 'ORDINARY_REVIEW_SCHEMA')
    locators = obs.closed(document['records'], ('open', 'spawn_call', 'spawn_output', 'child_activation', 'child_final', 'acceptance'), 'ORDINARY_REVIEW_LOCATORS')
    subject = (_np_subject(runtime) if _opening is None else
               runtime[3]._subject_from_episode_v1(runtime, _opening, _np_call))
    require(subject['episode'] == canonical['opening'] and subject['episode']['selected_child_role'] == 'audit-assess', 'ORDINARY_CANONICAL_CHILD')
    context = {'profile_id': obs.NONPROTECTED_PROFILE, 'parent_identity': subject['parent_identity'],
               'actual_child_identity': subject['actual_child_identity'], '_native_subject': subject}
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
    public_specs = [('parent', locators['open'], 'commentary'),
        ('child', locators['child_final'], 'final_answer'), ('parent', locators['acceptance'], 'commentary')]
    if _receiving_join_locator is not None:
        public_specs.append(('parent', _receiving_join_locator, 'commentary'))
    public = _ordinary_publics_v1(runtime, obs, context, public_specs)
    require(public[1]['turn_id'] == activation['payload'].get('turn_id'), 'ORDINARY_FRESH_TURN')
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
    canonical = route.read_applicable_ordinary_result_v1(Path(owner['repository']), owner['controller'])
    _ordinary_h0_current_v1(selected, runtime, canonical)
    return route, canonical


def _ordinary_h0_current_v1(selected, runtime, canonical):
    if canonical['status'] != 'CANONICAL_REVIEW_ABSENT':
        h0_path = HERE / 'host-session-binding.py'
        h0 = _np_module({'path': str(h0_path), 'bytes': h0_path.stat().st_size,
                         'sha256': selected['code_pins']['implementaudit/scripts/host-session-binding.py']}, 'host-session-binding.py', runtime[1])
        store = Path(selected['receiving']['h0_store'])
        h0.load_owner(store, selected['receiving']['h0_owner_id'])
        host = canonical['opening']['host_and_scope']
        _, state = h0.load_state(store, host['host_id'], host['host_session_id'])
        binding = h0.current_record(state, require_active=True)
        expected = {'controller_id': host['controller_id'], 'claim_id': host['claim_id'], 'explicit_run_root': host['explicit_run_root'],
            'binding_generation': host['host_binding_generation'], 'applicable_continuity_generation': host['continuity_generation'],
            'applicable_continuity_receipt': host['continuity_receipt']}
        require(all(binding[k] == v for k, v in expected.items()), 'ORDINARY_H0_CURRENTNESS')


def _ordinary_sources_v1(context, all_pins):
    return {role: {'path': context[role]['path'], 'physical': context[role]['physical'], 'metadata': context[role]['metadata'],
        'thread_id': context['parent_identity']['thread_id'] if role == 'parent' else context['actual_child_identity']['thread_id'],
        'cutoff': max(pin['locator']['offset'] + pin['locator']['bytes'] for pin in all_pins if pin['role'] == role)}
        for role in ('parent', 'child')}


def _ordinary_mission_policy_v1(obs, policy, canonical):
    import json
    mission = json.loads(obs._ordinary_wire(canonical['packet'])['source_event']['body'], object_pairs_hook=obs.unique)
    obs.closed(mission, ('schema', 'policy_digest', 'scope', 'mission', 'authority_ceiling'), 'ORDINARY_MISSION')
    require(mission['schema'] == 'implementaudit.ordinary-review-mission.v1' and
            mission['policy_digest'] == obs._ordinary_hash(policy) and mission['scope'] == canonical['scope'] and
            mission['authority_ceiling'] == 'NONE', 'ORDINARY_MISSION_POLICY_CHANGED')
    obs._ordinary_text(mission['mission'])


def ordinary_receiver_check_v1():
    """Actual deterministic receiver command. It grants no JOIN or lifecycle."""
    selected = _ordinary_selection_v1()
    runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1()
    route, canonical = _ordinary_canonical_v1(selected, runtime)
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_PARENT_ACCEPTANCE_ABSENT')
    _ordinary_mission_policy_v1(obs, policy, canonical)
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
    with _ordinary_episode_observation_v1() as raw:
        value = json.loads(raw)
    return value


import contextlib as _ordinary_contextlib


@_ordinary_contextlib.contextmanager
def _ordinary_episode_observation_v1(_native=None):
    """Private composition, never a caller-facing evidence credential.

    The fixed graph owner alone supplies its active R0033 view and immutable
    graph bytes; that owner's exit performs their full fresh terminal checks.
    Public acquisition accepts no supplied view, graph, callback or authority.
    """
    import json
    if ORDINARY_SELECTION_PIN is None:
        obs_path = HERE / 'compaction-result-observation.py'
        obs = _np_module({'path': str(obs_path), 'bytes': obs_path.stat().st_size,
                          'sha256': hashlib.sha256(obs_path.read_bytes()).hexdigest()}, obs_path.name)
        yield obs.canonical(obs.ordinary_export_unavailable_v1('ORDINARY_SELECTION_UNBOUND')); return
    selected = _ordinary_selection_v1(); runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1()
    if _native is None:
        route, canonical = _ordinary_canonical_v1(selected, runtime)
    else:
        view, graph_raw, actual = _native
        runtime[3]._bind_episode_owner_v1(selected['episode_owner'], actual)
        require(type(graph_raw) is bytes, 'ORDINARY_PROVISIONAL_GRAPH_BYTES')
        canonical = json.loads(view.ordinary_result_bytes(), object_pairs_hook=obs.unique)
        _ordinary_h0_current_v1(selected, runtime, canonical)
    def canonical_read():
        return (route.read_current_ordinary_result_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller'])
                if _native is None else json.loads(view.ordinary_result_bytes(), object_pairs_hook=obs.unique))
    def execution_read():
        return (route.read_current_ordinary_execution_v1(Path(selected['episode_owner']['repository']), selected['episode_owner']['controller'])
                if _native is None else json.loads(view.ordinary_execution_bytes(), object_pairs_hook=obs.unique))
    if canonical['status'] != 'CANONICAL_REVIEW_ABSENT': _ordinary_mission_policy_v1(obs, policy, canonical)
    missing = {'CANONICAL_REVIEW_ABSENT': 'CANONICAL_REVIEW_ABSENT', 'OPEN': 'CHILD_RETURN_ABSENT', 'RETURNED': 'PARENT_ACCEPTANCE_ABSENT'}
    if canonical['status'] in missing:
        yield obs.canonical(obs.ordinary_export_unavailable_v1(missing[canonical['status']])); return
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_CANONICAL_STATE')
    execution_receipt = execution_read()
    if execution_receipt is None:
        yield obs.canonical(obs.ordinary_export_unavailable_v1('RECEIVER_EXECUTION_ABSENT')); return
    for key, reason in (('review_evidence_path', 'REVIEW_EVIDENCE_ABSENT'), ('receiving_evidence_path', 'RECEIVING_EVIDENCE_ABSENT')):
        if not os.path.lexists(selected['receiving'][key]):
            yield obs.canonical(obs.ordinary_export_unavailable_v1(reason)); return
    with _ordinary_provider_guard_v1(runtime):
        document, receiving_pin = _ordinary_document_v1(obs, selected, selected['receiving']['receiving_evidence_path'])
        obs.closed(document, ('schema', 'records', 'graph', 'dispatch', 'work_result', 'join'), 'ORDINARY_RECEIVING_EVIDENCE')
        require(document['schema'] == 'implementaudit.ordinary-receiving-evidence.v1', 'ORDINARY_RECEIVING_SCHEMA')
        locators = obs.closed(document['records'], ('join',), 'ORDINARY_RECEIVER_LOCATORS')
        # The fixed owner reads this locator from the exact receiving document.
        # O/R/A/J keep their individual raw/API checks within one bounded call;
        # neither the locator nor the unvalidated body grants receiving credit.
        owner, result, acceptance, occurrences, context, public, review_pin = _ordinary_review_v1(
            selected, runtime, obs, pins, policy, canonical,
            _opening=canonical['opening'] if _native is not None else None,
            _receiving_join_locator=locators['join'] if _native is not None else None)
        obs.validate_ordinary_execution_v1(execution_receipt, owner, result, acceptance, policy)
        values, artifact_custody = {}, {}
        for key in ('graph', 'dispatch', 'work_result', 'join'):
            raw, artifact_custody[key] = _ordinary_artifact_v1(obs, selected, document[key])
            values[key] = json.loads(raw, object_pairs_hook=obs.unique)
        graph_owner = _np_module(selected['receiving']['graph_owner'], 'compile-work-graph.py', runtime[1])
        current_graph = (graph_owner.read_native_run_v1(canonical['opening']['host_and_scope']['explicit_run_root'], selected['episode_owner']['repository'])
                         if _native is None else json.loads(graph_raw, object_pairs_hook=obs.unique))
        joined = graph_owner.reconcile_native_results_v1(values['graph'], current_graph, values['dispatch'], [values['work_result']], policy['consumer'])
        require(joined == values['join'], 'ORDINARY_RECEIVING_JOIN_CHANGED')
        if _native is None:
            # This standalone path has no later combined native API fence;
            # retain its original separate JOIN read after graph validation.
            public.append(_ordinary_public_v1(runtime, obs, context, 'parent', locators['join'], 'commentary'))
        receiving = {'process': execution_receipt, 'dispatch': values['dispatch'], 'result': values['work_result'], 'join': joined, 'record': public[-1]['pin']}
        all_pins = [item['pin'] for item in public] + [occurrences['spawn']['call'], occurrences['spawn']['output'], occurrences['activation']]
        value = {'schema': obs.ORDINARY_EXPORT_SCHEMA, 'status': 'AVAILABLE', 'reason_code': None, 'owner': owner,
            'result': result, 'acceptance': acceptance, 'receiving': receiving, 'lifecycle': dict(obs.ORDINARY_LIFECYCLE),
            'occurrences': occurrences, 'custody': {'policy': policy, 'sources': _ordinary_sources_v1(context, all_pins),
                'review_evidence': review_pin, 'receiving_evidence': receiving_pin, 'public_records': public}, 'authority_ceiling': 'NONE'}
        value['export_digest'] = obs._ordinary_hash(value)
        obs.validate_ordinary_episode_export_v1(value)
        yield obs.canonical(value)
        if _native is not None:
            runtime[3]._recheck_ordinary_native_v1(runtime, obs, context, public, occurrences, _np_call, _ordinary_resolve_v1)
        _ordinary_h0_current_v1(selected, runtime, canonical)
        require(canonical_read() == canonical and
                ordinary_policy_v1() == policy and _ordinary_document_v1(obs, selected, review_pin['path'])[1] == review_pin and
                _ordinary_document_v1(obs, selected, receiving_pin['path'])[1] == receiving_pin, 'ORDINARY_FINAL_INPUT_FENCE')
        require(execution_read() == execution_receipt,
                'ORDINARY_EXECUTION_RECEIPT_CHANGED')
        for key, physical in artifact_custody.items():
            require(_ordinary_artifact_v1(obs, selected, document[key])[1] == physical, 'ORDINARY_FINAL_RECEIVING_ARTIFACT')
        for member in result['members']:
            require(_ordinary_artifact_v1(obs, selected, member['pin'])[1] == member['physical'], 'ORDINARY_FINAL_MEMBER_FENCE')



def _ordinary_receiver_observation_v2():
    """Fixed process observation; only the serialized R0033 producer stores it."""
    selected = _ordinary_selection_v1(); runtime, obs, pins = _ordinary_modules_v1(selected)
    policy = ordinary_policy_v1(); route, canonical = _ordinary_canonical_v1(selected, runtime)
    require(canonical['status'] == 'SATISFIED', 'ORDINARY_PARENT_ACCEPTANCE_ABSENT')
    _ordinary_mission_policy_v1(obs, policy, canonical)
    repo, controller = Path(selected['episode_owner']['repository']), selected['episode_owner']['controller']
    path = Path(__file__).resolve()
    source_pin = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': pins['implementaudit/scripts/compaction-source-owner-codex-app.py']}
    with _ordinary_provider_guard_v1(runtime):
        execution = runtime[3].run_held_ordinary_receiver_v1(selected, source_pin)
        execution.update(schema='implementaudit.ordinary-receiver-execution.v1', policy_digest=obs._ordinary_hash(policy),
            opening_digest=canonical['opening']['opening_digest'], return_digest=canonical['child_return']['digest'],
            acceptance_digest=canonical['governor_decision']['digest'])
        require(execution['argv'] == policy['receiver_argv'] and ordinary_policy_v1() == policy and
                route.read_current_ordinary_result_v1(repo, controller) == canonical, 'ORDINARY_EXECUTION_INPUT_CHANGED')
        return execution


def execute_ordinary_receiver_v1():
    """Delegate the entire check/run/publication transaction to its owner."""
    selected = _ordinary_selection_v1(); runtime, obs, _ = _ordinary_modules_v1(selected)
    route, canonical = _ordinary_canonical_v1(selected, runtime)
    policy = ordinary_policy_v1(); _ordinary_mission_policy_v1(obs, policy, canonical)
    return route.execute_current_ordinary_receiver_v2(Path(selected['episode_owner']['repository']),
        selected['episode_owner']['controller'], policy)


# Distinct owned-stdio source profile. No caller field can select this issuer.
OWNED_STDIO_PROFILE = 'codex-app-server-0.153.4-owned-stdio-candidate-v1'
OWNED_STDIO_SELECTION_PIN = None
SOURCE_PROFILES = (NONPROTECTED_PROFILE, OWNED_STDIO_PROFILE)

def selected_source_pin_v1():
    selected = [pin for pin in (NONPROTECTED_SELECTION_PIN, OWNED_STDIO_SELECTION_PIN) if pin is not None]
    require(len(selected) <= 1 and not (selected and ORDINARY_SELECTION_PIN is not None), 'FIXED_SOURCE_SELECTION_AMBIGUOUS')
    return selected[0] if selected else None

def selected_source_profile_v1():
    if selected_source_pin_v1() is None:
        return None
    return _np_selection()['profile_id']

def validate_owned_stdio_selection_shape_v1(selected):
    required = {'schema', 'profile_id', 'root_thread_id', 'root_agent_path', 'root_source',
        'session_root', 'cwd', 'cli_version', 'native_version', 'native_executable', 'codex_home',
        'runtime_helpers', 'episode_owner', 'pending_owner', 'producer_capture_pin', 'capture_producer_pin', 'tool_evidence_contract'}
    require(type(selected) is dict and set(selected) - {'c02_adjudication', 'rotation_input_owner', 'producer_dependencies'} == required and
        selected['schema'] == 'implementaudit.codex-owned-stdio-provider-selection.v1' and
        selected['profile_id'] == OWNED_STDIO_PROFILE and selected['cli_version'] == '0.153.4' and
        selected['native_version'] == 'codex-cli 0.153.4' and selected['root_agent_path'] == '/root' and
        selected['tool_evidence_contract'] == 'EXACT_ORIGINAL_CUSTOM_EXEC_AND_COLLABORATION_V1' and
        set(selected['runtime_helpers']) == {'bounded_native_reader.py', 'bounded_source_owner.py', 'bounded_file_custody.py'},
        'OWNED_STDIO_FIXED_SELECTION_SHAPE')
    uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
    require(type(selected['root_thread_id']) is str and re.fullmatch(uuid, selected['root_thread_id']), 'OWNED_STDIO_ROOT_IDENTITY')
    for key in ('root_source', 'session_root', 'cwd', 'codex_home'):
        path = Path(selected[key])
        require(path.is_absolute() and path.resolve(strict=True) == path, 'OWNED_STDIO_SELECTED_PATH_ALIAS')
    require(Path(selected['session_root']) == Path(selected['codex_home']) / 'sessions' and
        Path(selected['root_source']).is_relative_to(Path(selected['session_root'])) and
        Path(selected['root_source']).name.endswith('-' + selected['root_thread_id'] + '.jsonl'), 'OWNED_STDIO_SOURCE_NAMESPACE')
    pointer = selected['pending_owner']
    require(type(pointer) is dict and set(pointer) == {'store', 'session_id', 'owner_id'} and
        type(pointer['store']) is str and Path(pointer['store']).is_absolute() and
        pointer['session_id'] == selected['root_thread_id'] and type(pointer['owner_id']) is str and pointer['owner_id'],
        'OWNED_STDIO_PENDING_OWNER_SHAPE')
    require(type(selected['episode_owner']) is dict and set(selected['episode_owner']) == {'module_pin', 'repository', 'controller'},
        'OWNED_STDIO_R0033_OWNER_SHAPE')
    c02 = selected.get('c02_adjudication')
    if c02 is not None:
        require(type(c02) is dict and set(c02) == {'issuer','census_owner','decision_path','owner_decision_locator','source_contract_locator'}
            and all(type(value) is str and value for value in c02.values())
            and Path(c02['decision_path']).is_absolute(), 'C02_CONFIGURED_OWNER_ROUTE_SHAPE')
    return selected

def transfer_owned_stdio_interval_v1(runtime, producer, *, after_c5):
    require(type(after_c5) is bool and OWNED_STDIO_SELECTION_PIN is not None and runtime[0] == _np_selection(),
            'LIVE_INTERVAL_FIXED_SELECTION_REQUIRED')
    executing = __import__('types').SimpleNamespace(**globals())
    def read_release():
        path = HERE / 'compaction-audit-pending.py'
        pin = {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        pending = _np_module(pin,'compaction-audit-pending.py',runtime[1])
        return pending.read_selected_accepted_episode_v1()
    with _as_provider_guard_v1(runtime):
        return runtime[3].transfer_live_interval_v1(runtime,producer,executing,read_release if after_c5 else None)

def own_live_stdio_process_v1(native_process, producer_pins, *, emit, native_module=None):
    # An unadmitted capture factory, not a profile/grant or subprocess launcher.
    require(type(producer_pins) is dict and set(producer_pins) == {'helper','runner','loop','claim','source_owner'},
            'LIVE_PRODUCER_PIN_POPULATION')
    require(producer_pins['source_owner']['path'] == str(Path(__file__).absolute()), 'LIVE_ACTUAL_PRODUCER_SOURCE_PATH')
    helper = _np_module(producer_pins['helper'],'bounded_source_owner.py')
    claim = helper.load_live_claim_v1(producer_pins['claim'],_np_read_pin)
    executing_owner = __import__('types').SimpleNamespace(**globals())
    return helper.OwnedStdioLiveProducerV1(native_process, executing_owner, claim,
        producer_pins, emit=emit, native_module=native_module)

def _as_capture_v1(selected, custody=None):
    import json
    raw = _np_read_pin(selected['producer_capture_pin'], 512 * 1024, custody)
    capture = json.loads(raw, object_pairs_hook=_ordinary_unique_v1)
    producer = _np_read_pin(selected['capture_producer_pin'], 128 * 1024, custody)
    schema = capture.get('schema')
    if schema == 'implementaudit.owned-stdio-live-acquisition.v1':
        helper = _np_module(selected['runtime_helpers']['bounded_source_owner.py'], 'bounded_source_owner.py', custody)
        return helper.validate_live_capture_v1(selected, capture, lambda pin, bound: _np_read_pin(pin,bound,custody))
    require('producer_dependencies' not in selected, 'CLOSED_CAPTURE_HAS_LIVE_ONLY_DEPENDENCIES')
    generic = schema == 'implementaudit.owned-stdio-source-acquisition.v1'
    require((generic and capture.get('status') == 'SOURCE_CAPTURED_UNADMITTED' or
        schema == 'r0039.native-two-boundary-capture.v1' and capture.get('status') == 'ACTUAL_TWO_BOUNDARY_CAPTURED_UNADMITTED') and
        capture.get('thread_id') == selected['root_thread_id'] and
        capture.get('native_version') == selected['native_version'] and
        capture.get('native_executable_sha256') == selected['native_executable']['sha256'] and
        capture.get('process_exit_code') == 0 and capture.get('transport') == 'dedicated-owner-started-stdio' and
        capture.get('profile_admission') == 'UNADMITTED' and capture.get('native_pending_consumption') is False and
        capture.get('capture_script_sha256') == hashlib.sha256(producer).hexdigest() and
        Path(capture.get('codex_home', '')) == Path(selected['codex_home']) and
        Path(capture.get('cwd', '')) == Path(selected['cwd']) and
        (generic and type(capture.get('source')) is dict or not generic and len(capture.get('boundaries', [])) == 2),
        'OWNED_STDIO_PRODUCER_CAPTURE_BINDING')
    # This historical acquisition record remains unadmitted. Selection never
    # rewrites its H0/currentness/epoch labels or supplies missing child evidence.
    sources = [capture['source']] if generic else [boundary['source'] for boundary in capture['boundaries']]
    for source in sources:
        require(Path(source['path']) == Path(selected['root_source']) and
            source['metadata']['id'] == source['metadata']['session_id'] == selected['root_thread_id'] and
            source['metadata']['cli_version'] == selected['cli_version'], 'OWNED_STDIO_CAPTURE_SOURCE_CHANGED')
    return capture

def _as_provider_guard_v1(runtime):
    import contextlib
    selected, custody, protocol, helpers, _ = runtime
    @contextlib.contextmanager
    def guard():
        with contextlib.ExitStack() as held:
            binary = selected['native_executable']
            held.enter_context(custody.held_file(binary['path'], allow_append=False))
            held.enter_context(custody.held_file(selected['producer_capture_pin']['path'], allow_append=False))
            before = protocol.file_pin(Path(binary['path']))
            require(before['sha256'] == binary['sha256'] and before['bytes'] == binary['bytes'], 'OWNED_STDIO_BINARY_CHANGED')
            capture = _as_capture_v1(selected, custody)
            if capture['schema'] == 'implementaudit.owned-stdio-live-acquisition.v1':
                claim_pin = selected['producer_dependencies']['claim-run-rotation.py']
                claim = _np_module(claim_pin, 'claim-run-rotation.py', custody)
                held.enter_context(helpers.held_live_capture_v1(selected,capture,claim))
            source = helpers.header({'path': selected['root_source']})
            frozen = capture['source'] if capture['schema'] in {'implementaudit.owned-stdio-source-acquisition.v1','implementaudit.owned-stdio-live-acquisition.v1'} else capture['boundaries'][-1]['source']
            require({key: source['physical'][key] for key in ('device', 'inode')} == frozen['physical'], 'OWNED_STDIO_CAPTURE_PHYSICAL_CHANGED')
            context = {'parent': {'path': selected['root_source'], 'physical': frozen['physical'],
                'metadata': {'bytes': source['header_prefix']['bytes']}}}
            # Existing prefix owner; no transcript body is copied into evidence.
            obs = helpers._observation_owner
            prefix = sealed_prefix(obs, context, 'parent', frozen['bytes'])
            require(prefix['prefix_sha256'] == frozen['sha256'], 'OWNED_STDIO_CAPTURE_PREFIX_CHANGED')
            yield {'native_executable': before, 'producer_capture_pin': selected['producer_capture_pin']}
            require(protocol.file_pin(Path(binary['path'])) == before and _as_capture_v1(selected, custody) == capture and
                sealed_prefix(obs, context, 'parent', frozen['bytes']) == prefix, 'OWNED_STDIO_PROVIDER_CHANGED_DURING_READ')
    return guard()

def _as_fixed_policy_v1(obs, code_pins, selected):
    def code_pin(name):
        path = HERE / name
        pin = {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': code_pins[str(Path('implementaudit/scripts') / name)]}
        _np_read_pin(pin, 512 * 1024)
        return pin
    capture = _as_capture_v1(selected)
    descriptor = {'schema': 'implementaudit.compaction-fixed-acquisition-policy.v1',
        'profile_id': OWNED_STDIO_PROFILE, 'custody_namespace': 'result-observations-v1', 'qualification_key': 'qualification/Q.json',
        'provider_selection': {'profile_id': OWNED_STDIO_PROFILE, 'selection_pin': dict(OWNED_STDIO_SELECTION_PIN),
            'native_version': selected['native_version'], 'native_executable': selected['native_executable'],
            'codex_home': selected['codex_home'], 'producer_capture_pin': selected['producer_capture_pin'],
            'capture_producer_pin': selected['capture_producer_pin'],
            'tool_evidence_contract': selected['tool_evidence_contract']},
        'authenticating_source_owner': {'issuer_id': 'codex-owned-stdio-canonical-episode-public-source-v1',
            'module_pin': code_pin('compaction-source-owner-codex-app.py'),
            'native_reader_pin': code_pin('codex-recovery-native-reader.py'), 'native_binary': selected['native_executable'],
            'producer_capture_pin': selected['producer_capture_pin']},
        'exact_host_tuple': {'source_header_cli_version': selected['cli_version'],
            'provider_selection_sha256': OWNED_STDIO_SELECTION_PIN['sha256'], 'native_version': selected['native_version'],
            'native_executable_sha256': selected['native_executable']['sha256'],
            'producer_capture_sha256': selected['producer_capture_pin']['sha256'], 'codex_home': selected['codex_home']}}
    if capture['schema'] == 'implementaudit.owned-stdio-live-acquisition.v1':
        descriptor['provider_selection']['producer_dependencies'] = selected['producer_dependencies']
    value = {'descriptor': descriptor, 'code_and_skill_pins': code_pins}
    return {**value, 'policy_digest': obs.digest(obs.canonical(value))}

def _as_host_binding_v1(obs, context, policy, runtime):
    selected = runtime[0]
    require(_as_fixed_policy_v1(obs, policy['code_and_skill_pins'], selected) == policy, 'OWNED_STDIO_FIXED_POLICY_CHANGED')
    with _np_provider_guard(runtime):
        subject = _np_subject(runtime)
        require(subject['parent_identity'] == context['parent_identity'] and subject['actual_child_identity'] == context['actual_child_identity'] and
            subject['episode']['opening_digest'] == context['canonical_episode_binding']['opening_digest'], 'OWNED_STDIO_CANONICAL_CONTEXT_CHANGED')
        for role in ('parent', 'child'):
            require(subject['sources'][role]['physical']['path'] == context[role]['path'] and
                {key: subject['sources'][role]['physical'][key] for key in ('device', 'inode')} == context[role]['physical'],
                'OWNED_STDIO_CONTEXT_PHYSICAL_CHANGED')
        responses = subject['metadata']['responses']
    return {'schema': 'implementaudit.codex-owned-stdio-exact-source-binding.v1',
        'native_reader_sha256': policy['descriptor']['authenticating_source_owner']['native_reader_pin']['sha256'],
        'provider_selection_sha256': OWNED_STDIO_SELECTION_PIN['sha256'], 'native_version': selected['native_version'],
        'native_executable_sha256': selected['native_executable']['sha256'],
        'producer_capture_sha256': selected['producer_capture_pin']['sha256'], 'codex_home': selected['codex_home'],
        'parent_thread_read_response_sha256': responses[0]['response_sha256'], 'child_thread_read_response_sha256': responses[1]['response_sha256'],
        'parent_source_physical': context['parent']['physical'], 'child_source_physical': context['child']['physical'], 'authority_ceiling': 'NONE'}

def _as_public_turn_v1(obs, context, role, pin):
    anchor = context['parent_turn_start'] if role == 'parent' else context['child_activation']
    start, end = anchor['locator']['offset'], pin['locator']['offset'] + pin['locator']['bytes']
    require(0 <= start < end and end - start <= obs.MAX_TOTAL, 'OWNED_STDIO_PUBLIC_TURN_BOUND')
    path, info = obs.physical(context[role]['path'])
    require(obs.identity(info) == context[role]['physical'], 'OWNED_STDIO_PUBLIC_PHYSICAL_CHANGED')
    active = None
    position, count = start, 0
    with path.open('rb') as stream:
        stream.seek(start)
        while position < end:
            raw = stream.readline(min(obs.MAX_RECORD + 1, end - position))
            require(raw and raw.endswith(b'\n') and len(raw) <= obs.MAX_RECORD, 'OWNED_STDIO_PUBLIC_TURN_FRAME')
            row = obs.json.loads(raw, object_pairs_hook=obs.unique)
            count += 1
            require(count <= obs.MAX_RECORDS and isinstance(row, dict) and isinstance(row.get('payload'), dict), 'OWNED_STDIO_PUBLIC_TURN_FRAME')
            if row.get('type') == 'turn_context' or row.get('type') == 'event_msg' and row['payload'].get('type') == 'task_started':
                active = row['payload'].get('turn_id')
            position += len(raw)
    require(isinstance(active, str) and active, 'OWNED_STDIO_ACTIVE_TURN_ABSENT')
    return active

def _as_public_binding_v1(obs, context, policy, pins, runtime):
    import contextlib
    selected, custody, _, _, _ = runtime
    require(context['profile_id'] == OWNED_STDIO_PROFILE and 0 < len(pins) <= 8, 'OWNED_STDIO_PUBLIC_SCOPE')
    with _np_provider_guard(runtime):
        episode = _np_episode(runtime)
        require(episode['opening_digest'] == context['canonical_episode_binding']['opening_digest'], 'OWNED_STDIO_PUBLIC_OPEN_CHANGED')
        requests, originals, ends = [], [], {}
        for pin in pins:
            role = pin['role']
            with custody.held_file(context[role]['path']):
                row, checked = obs.resolve_record(context, role, pin['locator'])
                require(checked == pin, 'OWNED_STDIO_PUBLIC_PIN_CHANGED')
                body = obs.public_message(row, row['payload']['phase'], context=context).encode('utf-8')
                turn = _as_public_turn_v1(obs, context, role, pin)
            expected = {'id': row['payload']['id'], 'turn_id': turn, 'phase': row['payload']['phase'],
                'body_bytes': len(body), 'body_sha256': obs.digest(body)}
            requests.append(('thread/items/list', {'threadId': context[role + '_identity']['thread_id'] if role == 'parent' else context['actual_child_identity']['thread_id'],
                'turnId': turn, 'limit': 64, 'cursor': None, 'sortDirection': 'asc'}))
            originals.append((pin, expected))
            ends[role] = max(ends.get(role, 0), pin['locator']['offset'] + pin['locator']['bytes'])
        prefixes = [sealed_prefix(obs, context, role, end) for role, end in sorted(ends.items())]
        report = _np_call(runtime, requests, context['actual_child_identity']['thread_id'])
        records = []
        for (pin, expected), response in zip(originals, report['responses']):
            require(response.get('page_complete') is True and [item for item in response['items'] if item['id'] == expected['id']] == [expected],
                'OWNED_STDIO_NATIVE_PUBLIC_DIFFERS')
            records.append({'role': pin['role'], 'pin': pin, **expected,
                'source_semantics': 'ORIGINAL_NATIVE_RECORD', 'native_response_sha256': response['response_sha256']})
        require([sealed_prefix(obs, context, role, end) for role, end in sorted(ends.items())] == prefixes and _np_episode(runtime) == episode,
            'OWNED_STDIO_PUBLIC_CUTOFF_OR_EPISODE_CHANGED')
    return {'schema': 'implementaudit.owned-stdio-native-public-record-binding.v1', 'records': records,
        'source_prefixes': prefixes, 'anchor_response_sha256s': [], 'canonical_episode_binding': episode, 'authority_ceiling': 'NONE'}


import threading
import queue


class QuiescenceRefusal(ValueError):
    pass


class OwnedStdioQuiescenceV1:
    def __init__(self, existing_queue, *, selected_thread_id=None, native_process=None):
        if type(existing_queue) is not queue.Queue:
            raise QuiescenceRefusal('EXISTING_OWNER_QUEUE_REQUIRED')
        self.queue = existing_queue
        self.native_process = native_process
        self._selected_thread_id = selected_thread_id
        self._lock = threading.RLock()
        self._pending, self._seen_ids = {}, set()
        self._turns, self._items, self._completed = set(), {}, set()
        self._mcp, self._remote_seen = {}, False
        self._lifecycle = False
        self._lifecycle_validator = None
        self._compaction_expected = 0
        self._children = set()
        self._revision = 0
        self._initialized = False
        self._notified = False
        self._thread = None
        self._announced_thread = None
        self._last_completed = None
        self._fence = None
        self._failure = None
        self._reservations = []

    def _deny(self, reason):
        self._failure = reason
        raise QuiescenceRefusal(reason)

    def _poison_all(self):
        errors = []
        for reservation in tuple(self._reservations):
            try:
                reservation.cancel_now()
            except BaseException as exc:
                errors.append(exc)
        self._fence = None
        if errors:
            self._failure = 'OWNER_CANCELLATION_FAILED'
            raise errors[0]

    def before_send(self, message):
        with self._lock:
            self._poison_all()  # ALL immediate vetoes, no durable cleanup here.
            if self._failure and not (self._lifecycle and self._failure == 'NONACCEPTING_LIFECYCLE_INTERVAL'):
                self._deny(self._failure)
            if type(message) is not dict or type(message.get('method')) is not str:
                self._deny('UNKNOWN_OWNER_REQUEST')
            method = message['method']
            if method == 'initialized' and 'id' not in message:
                if not self._initialized or self._notified:
                    self._deny('INITIALIZATION_ORDER')
                self._notified = True
                return
            identity = message.get('id')
            if type(identity) not in (str, int):
                self._deny('DUPLICATE_OR_UNKNOWN_REQUEST_ID')
            identity_key = (type(identity), identity)
            if identity_key in self._seen_ids:
                self._deny('DUPLICATE_OR_UNKNOWN_REQUEST_ID')
            if method not in {'initialize', 'thread/start', 'thread/resume', 'turn/start', 'thread/read'} | ({'thread/compact/start'} if self._lifecycle else set()):
                self._deny('REQUEST_OUTSIDE_CONSERVATIVE_PROFILE')
            if method == 'initialize':
                if self._initialized or self._pending or self._seen_ids:
                    self._deny('INITIALIZATION_ORDER')
            elif not self._notified:
                self._deny('REQUEST_BEFORE_INITIALIZATION')
            params = message.get('params', {})
            if type(params) is not dict:
                self._deny('REQUEST_PARAMS_SHAPE')
            if method in {'thread/start','thread/resume'} and (self._thread is not None
                    or any(value in {'thread/start','thread/resume'} for value in self._pending.values())):
                self._deny('SECOND_SESSION_OR_THREAD_NOT_ADMITTED')
            if method == 'thread/resume' and (not self._selected_thread_id or params.get('threadId') != self._selected_thread_id):
                self._deny('UNSELECTED_NATIVE_RESUME')
            if method == 'turn/start' and (self._turns or 'turn/start' in self._pending.values()):
                self._deny('OVERLAPPING_TURN_NOT_ADMITTED')
            if method == 'thread/compact/start':
                if self._compaction_expected or self._turns or self._items: self._deny('COMPACTION_WITH_OUTSTANDING_WORK')
                self._compaction_expected = 1
            if method in {'turn/start', 'thread/read', 'thread/compact/start'} and (self._thread is None or params.get('threadId') != self._thread):
                self._deny('FOREIGN_REQUEST_SCOPE')
            self._seen_ids.add(identity_key)
            self._pending[identity_key] = method

    def send_failed(self):
        with self._lock:
            self._poison_all()
            self._deny('OUTGOING_EFFECT_UNKNOWN')

    def after_record(self, message):
        with self._lock:
            self._poison_all()
            self._revision += 1
            if self._failure and not (self._lifecycle and self._failure == 'NONACCEPTING_LIFECYCLE_INTERVAL'):
                self._deny(self._failure)
            if type(message) is not dict:
                self._deny('UNKNOWN_NATIVE_RECORD')
            if 'id' in message:
                if set(message) != {'id', 'result'}:
                    self._deny('UNKNOWN_NATIVE_RESPONSE_ENVELOPE')
                if 'method' in message:
                    self._deny('NATIVE_SERVER_REQUEST_NOT_ADMITTED')
                identity = message['id']
                if type(identity) not in (str, int):
                    self._deny('NATIVE_RESPONSE_ID_TYPE')
                identity_key = (type(identity), identity)
                if identity_key not in self._pending or 'error' in message or 'result' not in message:
                    self._deny('UNKNOWN_DUPLICATE_OR_FAILED_RESPONSE')
                method = self._pending.pop(identity_key)
                result = message['result']
                if type(result) is not dict:
                    self._deny('RESPONSE_SHAPE')
                if method == 'initialize':
                    self._initialized = True
                elif method in {'thread/start','thread/resume'}:
                    thread = result.get('thread', {}).get('id')
                    if not isinstance(thread, str) or not thread or (self._announced_thread and thread != self._announced_thread):
                        self._deny('THREAD_CREATION_SCOPE')
                    self._thread = thread
                    if self._selected_thread_id and thread != self._selected_thread_id:
                        self._deny('SELECTED_THREAD_RESPONSE_CHANGED')
                elif method == 'turn/start':
                    turn = result.get('turn', {}).get('id')
                    if not isinstance(turn, str) or not turn:
                        self._deny('TURN_CREATION_SCOPE')
                    if turn not in self._completed:
                        self._turns.add(turn)
                elif method == 'thread/read':
                    if result.get('thread', {}).get('id') != self._thread:
                        self._deny('READ_FENCE_SCOPE')
                    if not self._pending and not self._turns and not self._items and self._last_completed and all(v == 'ready' for v in self._mcp.values()):
                        self._fence = self._revision
                return
            self._notification(message)

    def _notification(self, message):
        def need(ok, reason='UNKNOWN_NATIVE_NOTIFICATION_SHAPE'):
            if not ok: self._deny(reason)
        need(set(message) in ({'method','params'}, {'method','params','emittedAtMs'}))
        need('emittedAtMs' not in message or type(message['emittedAtMs']) is int and 0 <= message['emittedAtMs'] < 2**63)
        method, p = message['method'], message['params']
        need(type(method) is str and type(p) is dict)
        if method == 'remoteControl/status/changed':
            need(set(p) <= {'installationId','serverName','status','environmentId'} and
                 {'installationId','serverName','status'} <= set(p) and not self._remote_seen and
                 p['status'] == 'disabled' and p.get('environmentId') is None and
                 all(type(p[k]) is str and p[k] for k in ('installationId','serverName')))
            self._remote_seen = True
            return
        if method == 'account/rateLimits/updated':
            need(set(p) == {'rateLimits'} and type(p['rateLimits']) is dict and set(p['rateLimits']) <=
                 {'credits','individualLimit','limitId','limitName','planType','primary','secondary','rateLimitReachedType','spendControlReached'})
            return
        if method == 'thread/started':
            need(set(p) == {'thread'} and type(p['thread']) is dict)
            identity = p['thread'].get('id')
            need(type(identity) is str and identity and not self._announced_thread and
                 (not self._thread or identity == self._thread) and
                 (not self._selected_thread_id or identity == self._selected_thread_id), 'UNEXPECTED_NATIVE_THREAD')
            self._announced_thread = identity
            return
        need(self._thread is not None and p.get('threadId') == self._thread, 'FOREIGN_OR_UNKNOWN_NATIVE_SCOPE')
        if method == 'mcpServer/startupStatus/updated':
            need({'threadId','name','status'} <= set(p) <= {'threadId','name','status','error','failureReason'} and
                 type(p['name']) is str and p['name'] and p.get('error') is None and p.get('failureReason') is None)
            name, status = p['name'], p['status']
            need(status == 'starting' and name not in self._mcp or status == 'ready' and self._mcp.get(name) == 'starting',
                 'MCP_STARTUP_NOT_SETTLED')
            self._mcp[name] = status
        elif method == 'thread/goal/cleared':
            need(set(p) == {'threadId'} and not self._turns and not self._last_completed)
        elif method == 'thread/status/changed':
            need(set(p) == {'threadId','status'} and p['status'] in ({'type':'idle'}, {'type':'active','activeFlags':[]}))
            need(p['status']['type'] != 'active' or self._turns or 'turn/start' in self._pending.values() or self._compaction_expected)
        elif method in {'turn/started','turn/completed'}:
            need(set(p) == {'threadId','turn'} and type(p['turn']) is dict)
            turn = p['turn']; identity = turn.get('id')
            need(type(identity) is str and identity and set(turn) <=
                 {'id','status','items','itemsView','startedAt','completedAt','durationMs','error'})
            if method == 'turn/started':
                need(identity not in self._completed and (identity in self._turns or 'turn/start' in self._pending.values() or self._compaction_expected == 1),
                     'UNREQUESTED_NATIVE_TURN')
                self._turns.add(identity); self._compaction_expected = 0
            else:
                need(identity in self._turns and turn.get('status') == 'completed' and not self._items,
                     'TURN_TERMINAL_WITH_PENDING_OR_UNKNOWN_WORK')
                self._turns.remove(identity); self._completed.add(identity); self._last_completed = identity
        else:
            need(p.get('turnId') in self._turns, 'FOREIGN_OR_INACTIVE_NATIVE_TURN')
            if method in {'item/started','item/completed'}:
                clock = 'startedAtMs' if method == 'item/started' else 'completedAtMs'
                need({'threadId','turnId','item'} <= set(p) <= {'threadId','turnId','item',clock} and
                     (clock not in p or type(p[clock]) is int and p[clock] >= 0) and type(p['item']) is dict)
                item = p['item']; identity = item.get('id'); kind = item.get('type')
                need(type(kind) is str and kind in {'userMessage','agentMessage','reasoning'} | ({'commandExecution','mcpToolCall','dynamicToolCall','collabAgentToolCall','contextCompaction'} if self._lifecycle else set()) and type(identity) is str and identity,
                     'TOOLS_OR_UNKNOWN_ITEM_NOT_ADMITTED')
                if kind not in {'userMessage','agentMessage','reasoning'}:
                    need(callable(self._lifecycle_validator), 'PINNED_LIFECYCLE_VALIDATOR_REQUIRED')
                    self._lifecycle_validator(self,item,method=='item/completed')
                if method == 'item/started':
                    need(identity not in self._items, 'DUPLICATE_ITEM'); self._items[identity] = kind
                else:
                    need(self._items.get(identity) == kind, 'UNKNOWN_ITEM_COMPLETION')
                    if kind == 'collabAgentToolCall':
                        self._children.update(item['receiverThreadIds'])
                    del self._items[identity]
            elif method == 'item/agentMessage/delta':
                need(set(p) == {'threadId','turnId','itemId','delta'} and type(p['delta']) is str and
                     self._items.get(p['itemId']) == 'agentMessage', 'UNKNOWN_DELTA_ITEM')
            elif method == 'rawResponseItem/completed':
                need(set(p) == {'threadId','turnId','item'} and type(p['item']) is dict)
                item = p['item']
                if self._lifecycle and item.get('type') in {'function_call','function_call_output','custom_tool_call','custom_tool_call_output','reasoning'}:
                    need(callable(self._lifecycle_validator), 'PINNED_LIFECYCLE_VALIDATOR_REQUIRED')
                    self._lifecycle_validator(self,item,True,raw=True)
                    return
                need({'type','id','role','content'} <= set(item) <=
                     {'type','id','role','content','internal_chat_message_metadata_passthrough','phase'} and
                     item['type'] == 'message' and type(item['id']) is str and
                     item['role'] in {'system','developer','user','assistant'} and type(item['content']) is list and
                     ('phase' not in item or item['phase'] in {None,'commentary','final_answer'}), 'RAW_TOOLS_OR_UNKNOWN_ITEM')
            elif self._lifecycle and method in {'item/commandExecution/outputDelta','item/reasoning/textDelta','item/reasoning/summaryTextDelta','item/reasoning/summaryPartAdded'}:
                need(p.get('itemId') in self._items and set(p) <= {'threadId','turnId','itemId','delta','contentIndex','summaryIndex'})
            elif method == 'rawResponse/completed':
                need({'threadId','turnId','responseId','usage'} <= set(p) <=
                     {'threadId','turnId','responseId','usage','usageMetadata'} and type(p['usage']) is dict and
                     type(p['responseId']) is str and ('usageMetadata' not in p or type(p['usageMetadata']) is dict))
            elif method == 'thread/tokenUsage/updated':
                need(set(p) == {'threadId','turnId','tokenUsage'} and type(p['tokenUsage']) is dict)
            elif method == 'turn/moderationMetadata':
                need(set(p) == {'threadId','turnId','metadata'} and type(p['metadata']) is dict)
            else: self._deny('UNKNOWN_NATIVE_EVENT_REQUIRES_PROFILE_REVIEW')

    def ingest(self, message):
        with self._lock:
            self.after_record(message)
            try:
                self.queue.put_nowait(message)
            except queue.Full:
                self._deny('OWNED_QUEUE_REJECTED_INGRESS')

    def disconnect(self):
        with self._lock:
            self._poison_all()
            self._deny('NATIVE_INGRESS_CLOSED_OR_UNKNOWN')

    def acquire(self, *reservations):
        with self._lock:
            if (self._failure or not self._initialized or not self._notified or not self._thread
                    or self._pending or self._turns or self._items or not self._last_completed
                    or self._fence != self._revision or not self.queue.empty()):
                raise QuiescenceRefusal('NO_COMPLETE_CURRENT_OWNER_QUIESCENCE_FENCE')
            if any(not callable(getattr(value, 'cancel_now', None)) for value in reservations):
                raise QuiescenceRefusal('MISSING_IMMEDIATE_CANCELLATION')
            self._reservations.extend(reservations)
            return _OwnedQuiescenceReceipt(self, self._revision, self._thread, self._last_completed)


class _OwnedQuiescenceReceipt:
    def __init__(self, owner, revision, thread_id, turn_id):
        self._owner, self._revision = owner, revision
        self.thread_id, self.turn_id = thread_id, turn_id

    def verify(self):
        value = self._owner
        with value._lock:
            if (value._failure or value._revision != self._revision or value._fence != self._revision
                    or value._pending or value._turns or value._items or not value.queue.empty()):
                raise QuiescenceRefusal('OWNED_QUIESCENCE_ADVANCED_OR_WITHDRAWN')

    def checkpoint(self):
        self.verify()
        return self._revision

import contextlib as _c02_contextlib
import contextvars as _c02_contextvars
import json as _c02_json
import threading as _c02_threading

_C02_SELECTED_SESSION_V1 = _c02_contextvars.ContextVar('selected_owned_stdio_c02', default=None)
_C02_SOURCE_BINDING_SEAL_V1 = object()


class OwnedStdioC02CensusV1:
    def __init__(self, selected, claim_owner, context, ledger):
        require(selected.get('profile_id') == OWNED_STDIO_PROFILE, 'C02_SELECTED_PROFILE_REQUIRED')
        self.selected, self.owner, self.context, self.ledger = selected, claim_owner, context, ledger
        self._cancelled = _c02_threading.Event()
        self._receipt = None
        self._events = []
        self._record_oids = set()
        self._original = None
        self._fence = None
        self.expected_old = None
        self._source_check = None
        self._production_binding = None
        self._fault_inflight = False

    def cancel_now(self):
        self._cancelled.set()  # No namespace lock, file I/O or cleanup.

    def unknown_owner_event(self):
        self.cancel_now()

    def arm(self, scanned):
        require(self._receipt is None, 'C02_INTERVAL_ALREADY_ARMED')
        receipt = self.ledger.acquire(self)
        fence = scanned.get('c02_terminal_fence')
        require(type(fence) is dict and fence.get('session_id') == self.selected['root_thread_id'] == receipt.thread_id
                and fence.get('turn_id') == receipt.turn_id, 'C02_TERMINAL_AND_LIVE_RPC_FENCE_DISAGREE')
        require(not self.owner._c02_retained_decisions_v1(self.context)[0], 'C02_CONTROLLED_SUBJECT_HAS_PRIOR_ADJUDICATIONS')
        joined=self.owner.require_current_generation_join_v1(self.context)
        expected = self.owner.managed(self.context)
        require(expected['pointer']==joined['pointer_oid'] and expected['marker']==joined['marker_oid']
                and expected['invalidation']==joined['pointer']['invalidation_oid'],
                'C02_CURRENT_PREIMAGE_CHANGED_BEFORE_INTERVAL_ARM')
        receipt.verify()
        require(not self._cancelled.is_set(), 'C02_INGRESS_DURING_ARM')
        self._fence = _c02_json.loads(_c02_json.dumps(fence))
        self.expected_old = dict(expected)
        self._receipt = receipt

    def verify(self):
        require(self._receipt is not None and not self._cancelled.is_set(), 'C02_LIVE_INTERVAL_UNAVAILABLE')
        self._receipt.verify()
        if self._source_check is not None:
            self._source_check()
        require(not self._cancelled.is_set(), 'C02_LIVE_INTERVAL_ADVANCED')

    def checkpoint(self):
        self.verify()
        return self._receipt.checkpoint(), self._fence['source_sha256'], self._fence['source_bytes']

    @property
    def source_cutoff(self):
        self.verify()
        return self.selected['root_thread_id'] + ':' + str(self._fence['source_bytes']) + ':' + self._fence['source_sha256']

    def observe_engineered_invalidation(self, oid, event, expected_old):
        self.verify()
        require(self._production_binding is None or self._fault_inflight,
                'C02_CANNOT_RETROACTIVELY_LABEL_A_NATIVE_EVENT_AS_CONTROLLED')
        require(self._original is None and expected_old == self.expected_old, 'C02_FAULT_CALLBACK_SCOPE_OR_REPLAY')
        actual = self.owner.invalidation_record(self.context, oid)
        require(actual == {'event':event,'boundary':'new-session','oid':oid}, 'C02_CONTROLLED_FAULT_READBACK_MISMATCH')
        self.owner.require_anchor(self.context, oid)
        self._original = oid
        self._events.append({'sequence':1,'kind':'native-boundary','event_id':event,
                             'invalidation_oid':oid,'boundary':'new-session'})
        self.verify()

    def inject_controlled_fault(self, event):
        require(self._production_binding is _C02_SOURCE_BINDING_SEAL_V1, 'C02_SELECTED_LIVE_SOURCE_REQUIRED')
        source=self
        class Inputs(self.owner._NativePublicationInputs):
            def ref_guards_v1(self): return {}
            def verify(self): source.verify()
            def before_effect(self): return source.checkpoint()
            def after_effect(self, stamp):
                source.verify()
                require(stamp==source.checkpoint(), 'C02_CONTROLLED_FAULT_OUTCOME_UNKNOWN')
        self._fault_inflight=True
        try:
            token=self.owner.invalidate_current_generation_v1(self.context,'new-session',event,
                _expected_old=self.expected_old,_observation=Inputs())
            oid=self.owner.exact_authority_token(self.context,'invalidation',token)
            self.observe_engineered_invalidation(oid,event,self.expected_old)
            return token
        except BaseException as exc:
            self.cancel_now()
            raise ValueError('C02_CONTROLLED_FAULT_OUTCOME_UNKNOWN_READBACK_REQUIRED') from exc
        finally:
            self._fault_inflight=False

    def observe_adjudication(self, oid):
        self.verify()
        require(self._original is not None, 'C02_ADJUDICATION_BEFORE_FAULT_CALLBACK')
        record = self.owner._c02_read_correction_v1(self.context, oid)
        require(record['observation']['invalidation_oid'] == self._original, 'C02_FOREIGN_ADJUDICATION_CALLBACK')
        if oid not in self._record_oids:
            self._record_oids.add(oid)
            self._events.append({'sequence':len(self._events)+1,'kind':'adjudication','record_oid':oid})
        self.verify()

    def census(self, request):
        self.verify()
        require(self._original is not None, 'C02_EXACT_CONTROLLED_EVENT_NOT_OBSERVED')
        retained, _ = self.owner._c02_retained_decisions_v1(self.context)
        require({oid for _,oid in retained} == self._record_oids, 'C02_UNOBSERVED_OWNER_ADJUDICATION')
        result = {'schema':'implementaudit.c02-owned-interval.v1',
            'source_owner':self.selected['c02_adjudication']['census_owner'],
            'source_cutoff':self.source_cutoff,
            'subject':{key:self.context[key] for key in ('controller','claim_id','run_root_identity')},
            'interval_start':1,'interval_end':len(self._events),'complete':True,
            'covered_boundary_kinds':sorted(self.owner.BOUNDARIES),'covers_adjudications':True,
            'events':_c02_json.loads(_c02_json.dumps(self._events))}
        self.verify()
        return result


class ConfiguredC02IssuerV1:
    def __init__(self, configured, subject):
        required = {'issuer','census_owner','decision_path','owner_decision_locator','source_contract_locator'}
        require(type(configured) is dict and set(configured) == required
                and all(type(x) is str and x for x in configured.values()), 'C02_OWNER_ROUTE_NOT_SELECTED')
        self.configured, self.subject = dict(configured), dict(subject)
        self.path = Path(configured['decision_path'])
        require(self.path.is_absolute() and self.path.resolve(strict=True) == self.path, 'C02_ISSUER_LOCATOR_ALIAS')
        self._raw, self._identity, self.decision = self._read()
        self._withdrawn = _c02_threading.Event()
        self.verify()

    def _read(self):
        require(self.path.resolve(strict=True)==self.path, 'C02_ISSUER_LOCATOR_CHANGED')
        with self.path.open('rb') as handle:
            import os
            before = os.fstat(handle.fileno())
            require(0 < before.st_size <= 65536, 'C02_ISSUER_DECISION_BOUND')
            raw = handle.read(65537)
            after = os.fstat(handle.fileno())
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns) ==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns), 'C02_ISSUER_DECISION_CHANGED_DURING_READ')
        def unique(pairs):
            value = {}
            for key,item in pairs:
                require(key not in value, 'C02_DUPLICATE_ISSUER_FIELD')
                value[key]=item
            return value
        value = _c02_json.loads(raw.decode('utf-8'),object_pairs_hook=unique)
        keys={'schema','issuer','role','subject','decision_id','revoked','qualification','expected_old',
              'source_cutoff','append_grant','conditional_fresh_grant'}
        require(type(value) is dict and set(value)==keys
                and value['schema']=='implementaudit.c02-configured-owner-decision.v1'
                and value['issuer']==self.configured['issuer'] and value['role']=='CONTINUITY_ADJUDICATION_OWNER'
                and value['subject']==self.subject and value['revoked'] is False
                and value['qualification']=='CONTROLLED_NONPROTECTED_FAULT_INJECTION', 'C02_SCOPED_ISSUER_DECISION_UNAVAILABLE')
        return raw,(before.st_dev,before.st_ino),value

    def cancel_now(self):
        self._withdrawn.set()

    def verify(self):
        require(not self._withdrawn.is_set(), 'C02_ISSUER_WITHDRAWN')
        raw,identity,_ = self._read()
        require(raw==self._raw and identity==self._identity and not self._withdrawn.is_set(), 'C02_ISSUER_REVISION_CHANGED')

    def checkpoint(self):
        self.verify()
        return hashlib.sha256(self._raw).hexdigest(), self._identity

    def grant(self, request):
        self.verify()
        require(request['decision_id']==self.decision['decision_id']
                and request['source_cutoff']==self.decision['source_cutoff']
                and request['expected_old']==self.decision['expected_old'], 'C02_ISSUER_EXACT_SUBJECT_CHANGED')
        key='conditional_fresh_grant' if request['effect']=='C02_FRESH_TRANSITION' else 'append_grant'
        result=_c02_json.loads(_c02_json.dumps(self.decision[key]))
        require(type(result) is dict, 'C02_EFFECT_NOT_GRANTED')
        if key=='conditional_fresh_grant':
            require(result.get('scope',{}).get('correction_record_oid')=='$OBSERVED_EXACT_APPEND'
                    and request.get('correction_record_oid'), 'C02_CONDITIONAL_APPEND_NOT_BOUND')
            result['scope']['correction_record_oid']=request['correction_record_oid']
        self.verify()
        return result


@_c02_contextlib.contextmanager
def selected_c02_materializer_session_v1(runtime, context, source):
    selected=runtime[0]
    require(OWNED_STDIO_SELECTION_PIN is not None and selected==_np_selection()
            and selected.get('profile_id')==OWNED_STDIO_PROFILE
            and type(source) is OwnedStdioC02CensusV1 and source.selected is selected
            and source._production_binding is _C02_SOURCE_BINDING_SEAL_V1
            and source.context is context and _C02_SELECTED_SESSION_V1.get() is None,
            'C02_SELECTED_SOURCE_SESSION_UNAVAILABLE')
    source.verify()
    subject={key:context[key] for key in ('controller','claim_id','run_root_identity')}
    issuer=ConfiguredC02IssuerV1(selected.get('c02_adjudication'),subject)
    require(issuer.decision['source_cutoff']==source.source_cutoff
            and issuer.decision['expected_old']==source.expected_old, 'C02_ISSUER_SOURCE_CUTOFF_CHANGED')
    value=(context,source,issuer)
    token=_C02_SELECTED_SESSION_V1.set(value)
    try:
        yield value
        source.verify(); issuer.verify()
    except BaseException:
        source.cancel_now(); raise
    finally:
        issuer.cancel_now()  # The enclosing interval owns successful source disposal.
        _C02_SELECTED_SESSION_V1.reset(token)


def get_selected_c02_materializer_v1(context, request):
    value=_C02_SELECTED_SESSION_V1.get()
    require(OWNED_STDIO_SELECTION_PIN is not None and value is not None and value[0] is context,
            'C02_SOURCE_AND_ACTUAL_ISSUER_NOT_SELECTED')
    _,source,issuer=value
    source.verify(); issuer.verify()
    selected={key:context[key] for key in ('controller','claim_id','run_root_identity')}
    selected.update(repo=str(context['repo']),**{key:issuer.configured[key] for key in
        ('census_owner','issuer','source_contract_locator','owner_decision_locator')})
    return selected,source,issuer


@_c02_contextlib.contextmanager
def acquire_selected_c02_interval_v1(runtime, claim_owner, context, ledger, native_process, code_pins):
    import subprocess
    import os
    selected=runtime[0]
    require(OWNED_STDIO_SELECTION_PIN is not None and selected==_np_selection()
            and type(ledger) is OwnedStdioQuiescenceV1 and ledger.native_process is native_process
            and type(native_process) is subprocess.Popen and native_process.poll() is None
            and native_process.stdin is not None and native_process.stdout is not None
            and native_process.args==[selected['native_executable']['path'],'app-server','--listen','stdio://'],
            'C02_ACTUAL_SELECTED_OWNED_STDIO_REQUIRED')
    key=str(Path('implementaudit/scripts/compaction-audit-pending.py'))
    require(key in code_pins, 'C02_EXISTING_SCANNER_CODE_PIN_REQUIRED')
    path=HERE/'compaction-audit-pending.py'
    pending=_np_module({'path':str(path),'bytes':path.stat().st_size,'sha256':code_pins[key]},
                       'compaction-audit-pending.py',runtime[1])
    with _as_provider_guard_v1(runtime):
        episode=_np_episode(runtime)
        require(episode['host_and_scope']['host_session_id']==selected['root_thread_id'], 'C02_R0033_EPISODE_SCOPE')
        source=OwnedStdioC02CensusV1(selected,claim_owner,context,ledger)
        def physical_revision():
            value=os.stat(selected['root_source'])
            return value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns,value.st_ctime_ns
        before=physical_revision()
        scanned=pending.scan_source(Path(selected['root_source']),require_c02_terminal=True)
        require(physical_revision()==before, 'C02_SOURCE_CHANGED_DURING_FULL_SCAN')
        source.arm(scanned)
        def check_source():
            require(native_process.poll() is None, 'C02_NATIVE_OWNER_EXITED')
            require(physical_revision()==before, 'C02_ORIGINAL_SOURCE_ADVANCED')
        source._source_check=check_source
        source._production_binding=_C02_SOURCE_BINDING_SEAL_V1
        try:
            source.verify()
            yield source
            source.verify()
        finally:
            source.cancel_now()


class OwnedStdioC02HooksV1:
    def __init__(self, runtime, claim_owner, context, invalidation_token, decision, *, source_owner_module):
        require(OWNED_STDIO_SELECTION_PIN is not None
                and runtime[0]['profile_id'] == OWNED_STDIO_PROFILE,
                'C02_OWNED_STDIO_PROFILE_NOT_ADMITTED')
        self.runtime, self.owner, self.context = runtime, claim_owner, context
        self.invalidation_token, self.decision = invalidation_token, decision
        self.source_owner_module = source_owner_module
        self._held = None
        self._operation = None

    def __enter__(self):
        import contextlib
        require(self._held is None, 'C02_OWNED_OPERATION_REPLAY')
        held = contextlib.ExitStack()
        try:
            held.enter_context(_as_provider_guard_v1(self.runtime))
            operation = held.enter_context(self.owner.c02_owned_operation_v1(
                self.context, self.invalidation_token, self.decision,
                _selected_source_owner=self.source_owner_module))
        except BaseException:
            held.close()
            raise
        self._held, self._operation = held, operation
        return self

    def __exit__(self, kind, value, traceback):
        held, self._held = self._held, None
        if held is None:return False
        try:
            return held.__exit__(kind, value, traceback)
        finally:
            self._operation = None

    def _active(self):
        require(self._operation is not None, 'C02_OWNED_OPERATION_NOT_ACTIVE')
        return self._operation

    def before_context_request(self, method):
        self._active().before_context_request(method)

    def cancel_now(self):
        self._active().cancel_now()

    def after_native_record(self):
        self._active().after_native_record()

    def disconnect(self):
        self._active().disconnect()

    def issuer_withdrawn(self):
        self._active().issuer_withdrawn()

    def append(self):
        self._active().verify()
        self.owner.materialize_c02_owner_revisions_v1(
            self.context, self.invalidation_token, self.decision)
        prepared = self.owner.prepare_c02_correction_v1(
            self.context, self.invalidation_token, self.decision)
        result = self.owner.publish_c02_correction_v1(self.context, prepared)
        self._active().source.observe_adjudication(result['record_oid'])
        self._active().verify()
        return result

    def apply_conditional_successor(self, correction_record_oid):
        self._active().verify()
        self.owner.materialize_c02_owner_revisions_v1(self.context, self.invalidation_token,
            self.decision, correction_record_oid=correction_record_oid)
        result = self.owner.run_c02_correction_v1(self.context, correction_record_oid)
        self._active().verify()
        return result


def notify_owned_c02_and_rotation_v1(reservations, method, *arguments):
    if method not in {'before_context_request', 'after_native_record', 'disconnect'}:
        raise ValueError('unsupported existing owned-stdio hook')
    errors = []
    for reservation in reservations:
        try:
            reservation.cancel_now()
        except BaseException as exc:
            errors.append(exc)
    for reservation in reservations:
        try:
            getattr(reservation, method)(*arguments)
        except BaseException as exc:
            errors.append(exc)
    if errors:
        raise errors[0]


def owned_stdio_ingest_v1(ledger, reservations, message):
    errors=[]
    for reservation in reservations:
        try: reservation.cancel_now()
        except BaseException as exc: errors.append(exc)
    try: ledger.ingest(message)
    except BaseException as exc: errors.append(exc)
    for reservation in reservations:
        try: reservation.after_native_record()
        except BaseException as exc: errors.append(exc)
    if errors: raise errors[0]


def owned_stdio_before_send_v1(ledger, reservations, message):
    errors=[]
    for reservation in reservations:
        try: reservation.cancel_now()
        except BaseException as exc: errors.append(exc)
    try: ledger.before_send(message)
    except BaseException as exc: errors.append(exc)
    for reservation in reservations:
        try: reservation.before_context_request(message.get('method'))
        except BaseException as exc: errors.append(exc)
    if errors: raise errors[0]


def owned_stdio_disconnect_v1(ledger, reservations):
    errors=[]
    for reservation in reservations:
        try: reservation.cancel_now()
        except BaseException as exc: errors.append(exc)
    try: ledger.disconnect()
    except BaseException as exc: errors.append(exc)
    for reservation in reservations:
        try: reservation.disconnect()
        except BaseException as exc: errors.append(exc)
    if errors: raise errors[0]


def rotation_input_owner_selection_v1():
    if OWNED_STDIO_SELECTION_PIN is None:
        return None
    selected = _np_selection()
    owner = selected.get('rotation_input_owner')
    if owner is None:
        return None
    fields = {'repo', 'controller', 'claim_id', 'run_root_identity', 'issuer',
              'source_contract_sha256', 'owner_decision_locator'}
    require(type(owner) is dict and set(owner) == fields
            and all(type(value) is str and value for value in owner.values()),
            'ROTATION_INPUT_PRIVATE_OWNER_SHAPE')
    return dict(owner, source_owner='codex-owned-stdio-canonical-episode-public-source-v1',
                provider_selection_sha256=OWNED_STDIO_SELECTION_PIN['sha256'],
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


class OwnedStdioRotationReservationV1:
    def __init__(self, runtime, native_state, native_process, claim_owner, claim_context, grant):
        import os
        import secrets
        import subprocess
        import threading
        selected = runtime[0]
        require(OWNED_STDIO_SELECTION_PIN is not None and selected['profile_id'] == OWNED_STDIO_PROFILE,
                'ROTATION_SOURCE_PROFILE_NOT_ADMITTED')
        require(type(native_process) is subprocess.Popen and native_process.poll() is None
                and native_process.stdin is not None and native_process.stdout is not None,
                'ROTATION_REQUIRES_EXISTING_OWNER_STDIO_HANDLES')
        require(native_process.args == [selected['native_executable']['path'], 'app-server', '--listen', 'stdio://'],
                'ROTATION_REQUIRES_EXACT_OWNED_STDIO_LAUNCH_WITHOUT_SECOND_TRANSPORT')
        episode = _np_episode(runtime)
        require(episode['host_and_scope']['host_session_id'] == native_state._binding['thread_id'],
                'ROTATION_NATIVE_EPISODE_DOES_NOT_MATCH_H0')
        policy = claim_owner._native_selection_v1(claim_context)
        require(policy['provider_selection_sha256'] == OWNED_STDIO_SELECTION_PIN['sha256']
                and grant.get('episode_binding_sha256') == episode['binding_digest']
                and policy['producer_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'ROTATION_SOURCE_CODE_PROFILE_OR_ISSUER_EPISODE_DIFFERS')
        native = claim_owner.projection_helper().native_inputs_module_v1()
        require(type(native_state) is native.NativeInputState, 'ROTATION_NATIVE_STATE_SOURCE_DIFFERS')
        reservation_id = secrets.token_hex(16)
        signal = claim_owner.NativeCancellationSignalV1(reservation_id)
        try:
            with native_state._signal_lock:
                native_state._verify(native_state._binding['subject'], native_state._binding['source_bytes'],
                                     native_state._binding['source_tokens'])
                snapshot = {'schema': 'implementaudit.native-rotation-source.v3', 'phase': 'READY',
                    'binding': native_state._binding, 'exact_usage': native_state._snapshot,
                    'reported_window': native_state._reported_window,
                    'cutoff_revision': native_state._revision,
                    'observed_monotonic_ns': native_state._received_monotonic_ns,
                    'reservation_id': reservation_id,
                    'producer_process': claim_owner.native_process_identity_v1(os.getpid()),
                    'host_process': claim_owner.native_process_identity_v1(native_process.pid),
                    'cancellation': signal.descriptor, 'episode_binding_sha256': episode['binding_digest'],
                    **{key: policy[key] for key in ('source_owner', 'source_contract_sha256', 'provider_selection_sha256')}}
            claim_owner._validate_native_revision_v1(claim_context, snapshot, grant, native)
        except BaseException:
            signal.signal()
            signal.close()  # No READY publication was attempted by this constructor.
            raise
        self.owner, self.context, self.native = claim_owner, claim_context, native
        self.host_process, self.native_state, self.signal = native_process, native_state, signal
        self.runtime, self.episode_binding = runtime, episode['binding_digest']
        self.snapshot = claim_owner.decode_json(claim_owner.canonical(snapshot))
        self.grant = claim_owner.decode_json(claim_owner.canonical(grant))
        self.refs = claim_owner.native_input_revision_refs_v1(claim_context)
        self._lock = threading.RLock()  # Materialization/cleanup only, NEVER ingress cancellation.
        self._published = self._ready_attempted = self._closed = False
        self._terminal_error = None
        self.ready_outcome = 'NOT_ATTEMPTED'

    def _cancel_first(self):
        try:
            self.signal.signal()
        except BaseException as exc:
            self._terminal_error = self._terminal_error or exc
            self.host_process.terminate()
            raise

    def _raise_poisoned(self):
        if self._terminal_error is not None:
            raise self._terminal_error

    def cancel_now(self):
        self._cancel_first()

    def _poison(self, error):
        self._cancel_first()
        self._terminal_error = self._terminal_error or error
        if self._ready_attempted or self._published:
            self.host_process.terminate()

    def _check_source(self):
        self.signal.check()
        require(_np_episode(self.runtime)['binding_digest'] == self.episode_binding,
                'ROTATION_CANONICAL_EPISODE_CHANGED')
        self.owner._validate_native_revision_v1(self.context, self.snapshot, self.grant, self.native)
        with self.native_state._signal_lock:
            self.native_state._verify(self.snapshot['binding']['subject'],
                self.snapshot['binding']['source_bytes'], self.snapshot['binding']['source_tokens'])
            require(self.native_state._revision == self.snapshot['cutoff_revision'], 'ROTATION_NATIVE_STREAM_ADVANCED')
        self.signal.check()

    def publish_ready(self):
        owner = self.owner
        with owner._CUSTODY.git_scope(self.context['repo'], owner.fixed_git(), owner.git_environment()):
            return self._publish_ready_with_custody()

    def _publish_ready_with_custody(self):
        with self._lock:
            self._raise_poisoned()
            require(not self._published and not self._closed and not self._ready_attempted, 'ROTATION_RESERVATION_REPLAY')
            owner, context = self.owner, self.context
            try:
                self._check_source()
                previous = owner.read_refs(context['repo'], self.refs.values())
                if previous[self.refs['source']] is not None:
                    old = owner.decode_json(owner.read_blob(context['repo'], previous[self.refs['source']]))
                    prior_resolved = (old.get('phase') == 'CLOSED'
                        and old.get('resolution', {}).get('status') == 'EXACT_CANONICAL_JOIN_VERIFIED')
                    require(old.get('phase') in {'REVOKED', 'CLOSED'}
                            and ('transaction_id' not in old or prior_resolved)
                            and old.get('exact_usage', {}).get('response_id') != self.snapshot['exact_usage']['response_id'],
                            'ROTATION_PRIOR_CONSUMPTION_REQUIRES_RECONCILIATION')
                predecessor = owner.resolve_predecessor(context)
                require(owner.projection_helper()._native_subject(predecessor) == self.snapshot['binding']['subject'],
                        'ROTATION_SOURCE_PREDECESSOR_CHANGED')
                plan = owner.prepare_native_source_update_v1(context, self.snapshot, self.grant,
                    expected_source_oid=previous[self.refs['source']], expected_grant_oid=previous[self.refs['grant']])
                source_oid = owner.write_blob(context, plan['source_bytes'])
                grant_oid = owner.write_blob(context, plan['grant_bytes'])
                updates = owner.retention_updates(context, [source_oid, grant_oid, *previous.values()])
                updates.update(plan['updates'])
                self.signal.check()
                self._ready_attempted = True
                self.ready_outcome = 'MAY_HAVE_PUBLISHED'  # BEFORE any READY CAS.
                owner.update_refs(context, updates, owner.predecessor_guards(context, predecessor))
                self._published = True
                self.ready_outcome = 'EXACT_READY_READBACK'
                self._check_source()
            except BaseException as exc:
                self._poison(exc)
                try:
                    self._revoke('READY attempt refused or outcome uncertain')
                except BaseException:
                    pass  # Original failure plus sticky cancellation/containment survive.
                raise

    def _revoke(self, reason):
        owner = self.owner
        with owner._CUSTODY.git_scope(self.context['repo'], owner.fixed_git(), owner.git_environment()):
            return self._revoke_with_custody(reason)

    def _revoke_with_custody(self, reason):
        with self._lock:
            if self._closed:
                return
            if not (self._ready_attempted or self._published):
                self._closed = True
                return
            owner, context = self.owner, self.context
            source_oid = owner.read_ref(context['repo'], self.refs['source'])
            if source_oid is None:
                self._closed = True  # Exact absence, not a successful READY claim.
                return
            current = owner.decode_json(owner.read_blob(context['repo'], source_oid))
            require(current.get('reservation_id') == self.snapshot['reservation_id'], 'ROTATION_RESERVATION_REPLACED')
            if current.get('phase') in {'REVOKED', 'CLOSED'}:
                self._closed = True
                return
            require(current.get('phase') in {'READY', 'CLAIMED'}, 'ROTATION_SOURCE_PHASE_UNKNOWN')
            ended = dict(current, phase='REVOKED', terminal_reason=str(reason)[:256])
            oid = owner.write_blob(context, owner.canonical(ended))
            updates = owner.retention_updates(context, [oid, source_oid])
            updates[self.refs['source']] = (oid, source_oid)
            owner.update_refs(context, updates, {})
            self._closed = True

    def _cleanup_after_signal(self, reason):
        try:
            self._revoke(reason)
        except BaseException as exc:
            self._poison(exc)
            raise
        self._raise_poisoned()  # A later successful cleanup never clears UNKNOWN.

    def before_context_request(self, method):
        self._cancel_first()
        self._cleanup_after_signal('before context request: ' + str(method))

    def after_native_record(self):
        self._cancel_first()
        self._cleanup_after_signal('native stream advanced after cutoff')

    def disconnect(self):
        self._cancel_first()
        self._cleanup_after_signal('native connection closed or uncertain')

    def before_grant_withdrawal(self):
        self._cancel_first()
        self._cleanup_after_signal('before independent issuer withdrawal')

    def finish(self):
        self._cancel_first()
        self._cleanup_after_signal('owner finished; explicit effect reconciliation required')


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
