"""Existing owner generic nonprotected projection. Historical private selectors are excluded."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
from datetime import datetime
PROFILE = 'codex-desktop-0.153.4-collaboration-public-v1'
STRUCTURAL_BOUNDARY_PROFILE = 'codex-desktop-0.155.0-alpha.16-boundary-structural-v1'
BOUNDARY_PROFILE = 'codex-desktop-0.155.0-alpha.16-boundary-thread-read-v1'
CURRENT_BOUNDARY_PROFILE = 'codex-desktop-0.159.2-boundary-thread-read-v1'
BOUNDARY_PROFILES = (BOUNDARY_PROFILE, CURRENT_BOUNDARY_PROFILE)
MAX_RECORD = 256 * 1024
MAX_TOTAL = 2 * 1024 * 1024
MAX_RECORDS = 64

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

class HoldObservationRefusal(ValueError):
    """A material event witnessed in a complete stable bounded hold view."""

    def __init__(self, reason, prefix, record):
        super().__init__(reason)
        self.evidence = {'prefix': dict(prefix), 'record': dict(record['locator'])}

def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'DUPLICATE_JSON_KEY')
        value[key] = item
    return value

def physical(path):
    path = Path(path)
    require(path.is_absolute() and path.absolute() == path.resolve(strict=True), 'SOURCE_PATH_ALIAS')
    for component in (path, *path.parents):
        info = component.lstat()
        require(not component.is_symlink() and (not getattr(info, 'st_file_attributes', 0) & 1024), 'SOURCE_REPARSE')
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'SOURCE_FILE_KIND')
    return (path, info)

def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def closed(value, keys, reason):
    require(isinstance(value, dict) and set(value) == set(keys), reason)
    return value

def current_retained_locator(row, context):
    """Current native grammar carrier only; origin requires the P/Q+C owner."""
    require(context is not None and context.get('profile_id') in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE), 'CURRENT_PUBLIC_PROFILE_REQUIRED')
    p = row['payload']
    m = row.get('metadata')
    require(isinstance(m, dict) and set(m) in ({'client_authored', 'retained_source'}, {'client_authored', 'retained_source', 'user_input_order'}), 'CURRENT_PUBLIC_METADATA_SHAPE')
    if 'user_input_order' in m:
        require(type(m['user_input_order']) is int and m['user_input_order'] >= 0, 'CURRENT_PUBLIC_METADATA_SHAPE')
    r = closed(m['retained_source'], ('complete', 'id', 'revision'), 'CURRENT_PUBLIC_RETAINED_SHAPE')
    identity = closed(r['id'], ('message_id', 'role', 'turn_id'), 'CURRENT_PUBLIC_RETAINED_ID_SHAPE')
    uuid = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    require(m['client_authored'] is False and r['complete'] is True and (identity['message_id'] == p.get('id')) and (identity['role'] == p.get('role') == 'assistant') and isinstance(identity['turn_id'], str) and (re.fullmatch(uuid, identity['turn_id']) is not None) and isinstance(r['revision'], str) and (re.fullmatch('retained_' + uuid, r['revision']) is not None), 'CURRENT_PUBLIC_RETAINED_ID_OR_COMPLETENESS')
    return r

def current_record_metadata(row, context, active_turn=None):
    if 'metadata' not in row:
        return row['payload'].get('type') != 'message' or row['payload'].get('role') != 'assistant'
    if context.get('profile_id') not in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE):
        return False
    p = row['payload']
    kind = p.get('type')
    m = row['metadata']
    if kind == 'message' and p.get('role') == 'assistant':
        r = current_retained_locator(row, context)
        return active_turn is None or r['id']['turn_id'] == active_turn
    if kind in ('custom_tool_call_output', 'function_call', 'function_call_output'):
        return m == {'client_authored': False, 'fallback_token_limit_override': 12000}
    if kind == 'message' and p.get('role') == 'user' and (m == {'client_authored': False, 'mcp_attribution': {'status': 'none'}}):
        return True
    return (kind == 'agent_message' or (kind == 'message' and p.get('role') == 'user')) and isinstance(m, dict) and (set(m) == {'client_authored', 'user_input_order'}) and (m['client_authored'] is False) and (type(m['user_input_order']) is int) and (m['user_input_order'] >= 0)

def public_message(row, phase='commentary', context=None):
    payload = row['payload']
    native_current = context is not None and context.get('profile_id') in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE)
    if native_current:
        current_retained_locator(row, context)
    require(row['type'] == 'response_item' and (native_current or 'metadata' not in row) and (payload.get('type') == 'message') and (payload.get('role') == 'assistant') and (payload.get('phase') == phase) and isinstance(payload.get('id'), str) and payload['id'], 'ACTUAL_ASSISTANT_ROLE_OR_PHASE')
    content = payload.get('content')
    keys = {'type', 'text'}
    if context is not None and context.get('profile_id') == NONPROTECTED_PROFILE:
        keys |= {'annotations', 'logprobs'}
    require(isinstance(content, list) and len(content) == 1 and (set(content[0]) == keys) and (content[0]['type'] == 'output_text') and isinstance(content[0]['text'], str) and (keys == {'type', 'text'} or content[0]['annotations'] == content[0]['logprobs'] == []), 'ACTUAL_PUBLIC_TEXT_SHAPE')
    return content[0]['text']

def visible(row, expected, context=None):
    text = public_message(row, context=context)
    require(text.startswith('```ini\n') and '\n```' in text, 'VISIBLE_PRE_USE_BLOCK_ABSENT')
    block = text[len('```ini\n'):text.index('\n```')]
    pairs = []
    for line in block.splitlines():
        require('=' in line and (not line.startswith((' ', '>'))), 'VISIBLE_PRE_USE_FIELD_SHAPE')
        pairs.append(line.split('=', 1))
    fields = unique(pairs)
    require(all((fields.get(key) == value for key, value in expected.items())), 'VISIBLE_PRE_USE_MEANING')

def typed_message(row, keys, schema, action=None, phase='commentary', context=None):
    text = public_message(row, phase, context=context)
    require(text.startswith('```json\n') and text.endswith('\n```'), 'TYPED_PUBLIC_RECORD_BLOCK')
    value = json.loads(text[len('```json\n'):-len('\n```')], object_pairs_hook=unique)
    closed(value, keys, 'TYPED_PUBLIC_RECORD_FIELDS')
    require(value['schema'] == schema and value.get('authority_ceiling') == 'NONE' and (action is None or value.get('action') == action), 'TYPED_PUBLIC_RECORD_MEANING')
    return value

def before(first, second):
    require(datetime.fromisoformat(first['timestamp'].replace('Z', '+00:00')) < datetime.fromisoformat(second['timestamp'].replace('Z', '+00:00')), 'OBSERVATION_ORDER')
    if first['path'] == second['path']:
        require(first['locator']['offset'] + first['locator']['bytes'] <= second['locator']['offset'], 'SOURCE_RECORD_ORDER')

def resolve_record(context, role, locator):
    source = context[role]
    observed = _nonprotected_read_records(context, role, [source['metadata'], locator]) if context['profile_id'] == NONPROTECTED_PROFILE else read_records(source['path'], [source['metadata'], locator], source['allowed_ranges'], source['physical'])
    meta, selected = observed['records']
    require(meta['row']['type'] == 'session_meta' and digest(canonical(meta['row']['payload'])) == source['metadata_payload_digest'], 'SOURCE_METADATA_CHANGED')
    require(role != 'child' or selected['row']['ordinal'] >= source['history_start_ordinal'], 'INHERITED_CHILD_RECORD')
    row = selected['row']
    return (row, {'path': source['path'], 'physical': source['physical'], 'role': role, 'locator': dict(locator), 'timestamp': row['timestamp'], 'message_or_call_id': row['payload'].get('id', row['payload'].get('call_id'))})

def session_filename(path, task, version):
    """Accept the pinned native naming forms; a locator is never authentication."""
    name = Path(path).name
    if not isinstance(task, str) or not task or (not name.startswith('rollout-')):
        return False
    if name.endswith(task + '.jsonl'):
        return True
    uuid = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    return version == '0.155.0-alpha.16' and re.search(re.escape(task) + '_' + uuid + '\\.jsonl$', name) is not None
FRESH_CHILD_BOUNDARY_SCHEMA = 'implementaudit.current-fresh-child-source-boundary.v1'

def current_history_metadata_shape(metadata):
    """Absent remains unknown; only the independent spawn/activation closes it."""
    keys = ('forked_from_id', 'subagent_history_start_ordinal')
    present = [key in metadata for key in keys]
    if not any(present):
        return 'ABSENT_PAIR'
    require(all(present) and all((metadata[key] is None for key in keys)), 'CURRENT_CHILD_HISTORY_METADATA_UNSUPPORTED')
    return 'PRESENT_NULL_PAIR'

def fresh_child_boundary(context):
    require(context.get('profile_id') in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE), 'CURRENT_FRESH_PROFILE_REQUIRED')
    source = context['child']
    metadata = read_records(source['path'], [source['metadata']], source['allowed_ranges'], source['physical'])['records'][0]['row']
    require(metadata['type'] == 'session_meta' and metadata['ordinal'] == 0 and (digest(canonical(metadata['payload'])) == source['metadata_payload_digest']), 'SOURCE_METADATA_CHANGED')
    shape = current_history_metadata_shape(metadata['payload'])
    call, call_pin = resolve_record(context, 'parent', context['spawn_call']['locator'])
    result, result_pin = resolve_record(context, 'parent', context['spawn_output']['locator'])
    args = json.loads(call['payload']['arguments'], object_pairs_hook=unique)
    require(call['payload'].get('namespace') == 'collaboration' and call['payload'].get('name') == 'spawn_agent' and (call['payload'].get('call_id') == result['payload'].get('call_id')) and (args.get('task_name') == context['actual_child_identity']['agent_path'].removeprefix('/root/')) and (json.loads(result['payload']['output'], object_pairs_hook=unique) == {'task_name': context['actual_child_identity']['agent_path']}), 'ACTUAL_SPAWN_CHILD_IDENTITY')
    fork = args.get('fork_turns')
    require(fork == 'none', 'CURRENT_FRESH_SPAWN_REQUIRED')
    activation, pin = resolve_record(context, 'child', context['child_activation']['locator'])
    require(pin['locator']['offset'] == source['metadata']['bytes'] and activation['ordinal'] == 1 and (activation['type'] == 'event_msg') and (activation['payload'].get('type') == 'task_started') and isinstance(activation['payload'].get('turn_id'), str) and activation['payload']['turn_id'] and ('metadata' not in activation), 'CHILD_ACTIVATION_BOUNDARY')
    before(call_pin, result_pin)
    before(result_pin, pin)
    return {'schema': FRESH_CHILD_BOUNDARY_SCHEMA, 'metadata_shape': shape, 'metadata_field_presence': {key: key in metadata['payload'] for key in ('forked_from_id', 'subagent_history_start_ordinal')}, 'metadata': source['metadata'], 'actual_spawn_call': call_pin, 'actual_spawn_output': result_pin, 'observed_fork_turns': fork, 'actual_activation': pin, 'history_start_ordinal_from_activation': activation['ordinal'], 'authority_ceiling': 'NONE'}

def shell_literal(text):
    return "'" + str(text).replace("'", "''") + "'"

def tool_input(command):
    return 'const r = await tools.exec_command(' + json.dumps({'cmd': command, 'max_output_tokens': 24000}, separators=(',', ':')) + ');text(r);'

def profile_tool_input(context, command):
    """Match the exact terminal LF emitted by this current host profile only."""
    require(isinstance(command, str) and (not command.endswith('\n')), 'TOOL_INPUT_BASE_SHAPE')
    if context.get('source_association') in ('PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED', 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED'):
        return command + '\n'
    return command

def load_tool_input(skill_pin):
    command = '$p = ' + shell_literal(skill_pin['path']) + '\n$b = [IO.File]::ReadAllBytes($p)\n'
    command += '[PSCustomObject]@{path=$p;bytes=$b.Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant();utf8=[Text.Encoding]::UTF8.GetString($b)} | ConvertTo-Json -Compress'
    return tool_input(command)

def delivery_tool_input(store, session, owner, request):
    pending = Path(__file__).resolve().with_name('compaction-audit-pending.py')
    command = shell_literal(json.dumps(request, sort_keys=True)) + ' | & ' + shell_literal(sys.executable)
    command += ' -I -S -B ' + shell_literal(pending) + ' --store ' + shell_literal(store)
    command += ' --session ' + shell_literal(session) + ' --owner-id ' + shell_literal(owner) + ' observe-child'
    return tool_input(command)

def artifact_preflight(pin, maximum=1024 * 1024):
    """Validate metadata and physical identity without opening file contents."""
    closed(pin, ('path', 'bytes', 'sha256'), 'ARTIFACT_PIN_SHAPE')
    require(type(pin['bytes']) is int and 0 < pin['bytes'] <= maximum and isinstance(pin['sha256'], str) and re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'ARTIFACT_PIN_BOUND')
    path, before_stat = physical(pin['path'])
    require(before_stat.st_size == pin['bytes'], 'ARTIFACT_BYTE_COUNT')
    return (path, before_stat)

def artifact(pin, maximum=1024 * 1024, admitted=None):
    path, before_stat = artifact_preflight(pin, maximum)
    if admitted is not None:
        admitted_path, admitted_stat = admitted
        require(path == admitted_path and identity(before_stat) == identity(admitted_stat) and ((before_stat.st_size, before_stat.st_mtime_ns) == (admitted_stat.st_size, admitted_stat.st_mtime_ns)), 'ARTIFACT_ADMISSION_CHANGED')
    with open(path, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        require(identity(opened) == identity(before_stat) and opened.st_nlink == 1 and stat.S_ISREG(opened.st_mode) and ((opened.st_size, opened.st_mtime_ns) == (before_stat.st_size, before_stat.st_mtime_ns)), 'ARTIFACT_PHYSICAL_CHANGED')
        raw = stream.read(pin['bytes'])
    _, after_stat = physical(path)
    require(identity(before_stat) == identity(after_stat) and (before_stat.st_size, before_stat.st_mtime_ns) == (after_stat.st_size, after_stat.st_mtime_ns) and (len(raw) == pin['bytes']) and (digest(raw) == pin['sha256']), 'ARTIFACT_PIN_CHANGED')
    return (raw, identity(before_stat))

def command_response(context, role, call_locator, result_locator, expected_input):
    call_row, call_pin = resolve_record(context, role, call_locator)
    output_row, output_pin = resolve_record(context, role, result_locator)
    call = call_row['payload']
    output = output_row['payload']
    require(call_row['type'] == output_row['type'] == 'response_item' and call.get('type') == 'custom_tool_call' and (call.get('name') == 'exec') and (call.get('input') == expected_input) and (call.get('status') == 'completed') and isinstance(call.get('call_id'), str) and (output.get('type') == 'custom_tool_call_output') and (output.get('call_id') == call['call_id']), 'ACTUAL_HOST_CALL_RESULT_ASSOCIATION')
    content = output.get('output')
    require(isinstance(content, list) and len(content) == 2 and all((isinstance(block, dict) and set(block) == {'type', 'text'} and (block['type'] == 'input_text') and isinstance(block['text'], str) for block in content)), 'FULL_HOST_OUTPUT_SHAPE')
    nested = json.loads(content[1]['text'], object_pairs_hook=unique)
    require(isinstance(nested, dict) and set(nested) == {'chunk_id', 'wall_time_seconds', 'exit_code', 'original_token_count', 'output'} and (type(nested['exit_code']) is int) and (nested['exit_code'] == 0) and isinstance(nested['output'], str), 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED')
    before(call_pin, output_pin)
    return (nested['output'], {'call': call_pin, 'result': output_pin})

def authorization(context, prepared, evidence, skill_pin):
    closed(evidence, ('load_call', 'load_output', 'route', 'authorization'), 'AUTHORIZATION_EVIDENCE_SHAPE')
    loaded_text, load_identity = command_response(context, 'child', evidence['load_call'], evidence['load_output'], profile_tool_input(context, load_tool_input(skill_pin)))
    loaded = json.loads(loaded_text, object_pairs_hook=unique)
    closed(loaded, ('path', 'bytes', 'sha256', 'utf8'), 'FULL_LOAD_CONTENT_SHAPE')
    skill_raw, _ = artifact(skill_pin)
    require({key: loaded[key] for key in ('path', 'bytes', 'sha256')} == skill_pin and loaded['utf8'].encode('utf-8') == skill_raw, 'ACTUAL_FULL_SKILL_LOAD_DIFFERS')
    before(context['spawn_output'], load_identity['call'])
    route_row, route_pin = resolve_record(context, 'parent', evidence['route'])
    task = context['actual_child_identity']['agent_path'].removeprefix('/root/')
    visible(route_row, {'CHILD_TASK': task, 'CHILD_SKILL_ROUTE': 'audit-state', 'LOAD': 'VERIFIED'}, context=context)
    row, record_pin = resolve_record(context, 'parent', evidence['authorization'])
    value = typed_message(row, ('schema', 'action', 'parent_identity', 'actual_child_identity', 'obligation_digest', 'observation_id', 'load_observation_identity', 'selected_child', 'skill_source_pin', 'authority_ceiling'), 'implementaudit.compaction-use-authorization.v1', 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION', context=context)
    obligation = prepared['obligation']
    expected = {'schema': 'implementaudit.compaction-use-authorization.v1', 'action': 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION', 'parent_identity': obligation['parent_identity'], 'actual_child_identity': obligation['actual_child_identity'], 'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': obligation['observation_id'], 'load_observation_identity': digest(canonical(load_identity)), 'selected_child': 'audit-state', 'skill_source_pin': skill_pin, 'authority_ceiling': 'NONE'}
    require(value == expected, 'AUTHORIZATION_EXACT_OBLIGATION_OR_LOAD_IDENTITY')
    before(load_identity['result'], route_pin)
    before(route_pin, record_pin)
    return {'value': value, 'text': public_message(row, context=context), 'record': record_pin, 'load_identity': load_identity, 'route_record': route_pin, 'evidence': evidence}

def delivery_packet(prepared, validated):
    raw, _ = artifact(prepared['obligation_pin'])
    require(json.loads(raw, object_pairs_hook=unique) == prepared['obligation'], 'IMMUTABLE_OBLIGATION_CHANGED')
    return {'schema': 'implementaudit.compaction-obligation-delivery.v1', 'observation_id': prepared['obligation']['observation_id'], 'obligation_pin': prepared['obligation_pin'], 'obligation_utf8': raw.decode('utf-8'), 'authorization_record': validated['record'], 'authorization_utf8': validated['text'], 'authority_ceiling': 'NONE', 'host_producer_authenticated': False}

def completed_exchange(context, prepared, request, store, session, owner, skill_pin):
    closed(request, ('call', 'result'), 'CHILD_EXCHANGE_LOCATOR_SHAPE')
    require(prepared['authorization'] is not None and prepared.get('delivery_request') is not None, 'OBLIGATION_NOT_DELIVERED')
    validated = authorization(context, prepared, prepared['authorization']['evidence'], skill_pin)
    require(validated == prepared['authorization'], 'PUBLIC_AUTHORIZATION_CHANGED')
    text, identity = command_response(context, 'child', request['call'], request['result'], profile_tool_input(context, delivery_tool_input(store, session, owner, prepared['delivery_request'])))
    packet = json.loads(text, object_pairs_hook=unique)
    require(packet == delivery_packet(prepared, validated), 'ACTUAL_FULL_OBLIGATION_AUTHORIZATION_RESPONSE_DIFFERS')
    before(validated['record'], identity['call'])
    return {'identity': digest(canonical(identity)), 'records': identity, 'evidence': request}

def allow_current_settings_event(context, record):
    """Treat only the pinned first post-refusal host settings row as inert."""
    if context.get('source_association') != 'PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED':
        return False
    child = context['child']
    settings = child.get('settings_envelope')
    if settings is None:
        return False
    row = record['row']
    return record['locator'] == settings['locator'] and row['type'] == 'event_msg' and ('metadata' not in row) and (row['ordinal'] == child['history_start_ordinal']) and (row['payload'].get('type') == 'thread_settings_applied') and (row['payload'].get('thread_id') == context['actual_child_identity']['thread_id']) and (digest(canonical(row['payload'])) == settings['payload_digest'])

def hold_records(context, cutoff=None, prior=None, until_call=None):
    """Acquire the whole physical child prefix, not a selected list of USE rows.

    The bound source metadata supplies activation/history identity. Inherited
    rows still occupy physical bytes; no caller locator can omit those bytes.
    This is bounded physical coverage, not authentication of the host writer.
    """
    source = context['child']
    path, initial = physical(source['path'])
    require(identity(initial) == source['physical'], 'HOLD_SOURCE_PHYSICAL_CHANGED')
    discovering = until_call is not None
    require(not discovering or (cutoff is None and prior is not None), 'HOLD_COMPLETION_DISCOVERY_SHAPE')
    end = min(initial.st_size, MAX_TOTAL) if discovering else initial.st_size if cutoff is None else cutoff
    require(type(end) is int and 0 < end <= MAX_TOTAL and (end <= initial.st_size), 'HOLD_PREFIX_BYTE_BOUND')
    windows = source['allowed_ranges']
    require(isinstance(windows, list) and 0 < len(windows) <= MAX_RECORDS, 'HOLD_ALLOWED_RANGE_BOUND')
    for window in windows:
        closed(window, ('offset', 'bytes'), 'HOLD_ALLOWED_RANGE_SHAPE')
        require(type(window['offset']) is int and window['offset'] >= 0 and (type(window['bytes']) is int) and (0 < window['bytes'] <= MAX_TOTAL), 'HOLD_ALLOWED_RANGE_BOUND')
    covered = 0
    for window in sorted(windows, key=lambda value: value['offset']):
        if window['offset'] > covered:
            break
        covered = max(covered, window['offset'] + window['bytes'])
    if discovering:
        end = min(end, covered)
        require(end > 0, 'HOLD_CONTIGUOUS_RANGE_REQUIRED')
    else:
        require(covered >= end, 'HOLD_CONTIGUOUS_RANGE_REQUIRED')
    if prior is not None:
        require(prior['path'] == str(path) and prior['physical'] == source['physical'] and (type(prior['prefix_bytes']) is int) and (0 < prior['prefix_bytes'] <= end) and isinstance(prior['prefix_sha256'], str) and re.fullmatch('[0-9a-f]{64}', prior['prefix_sha256']), 'HOLD_PRIOR_PREFIX_BOUND')
    if discovering:
        closed(until_call, ('path', 'physical', 'locator', 'call_id'), 'HOLD_ORIGINAL_CALL_SHAPE')
        original = closed(until_call['locator'], ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'), 'HOLD_ORIGINAL_CALL_LOCATOR_SHAPE')
        require(until_call['path'] == str(path) and until_call['physical'] == source['physical'] and isinstance(until_call['call_id'], str) and until_call['call_id'] and (type(original['offset']) is int) and (original['offset'] >= 0) and (type(original['bytes']) is int) and (0 < original['bytes'] <= MAX_RECORD) and (original['offset'] + original['bytes'] <= prior['prefix_bytes']) and (type(original['embedded_ordinal']) is int) and (original['embedded_ordinal'] >= source['history_start_ordinal']) and isinstance(original['sha256'], str) and re.fullmatch('[0-9a-f]{64}', original['sha256']) and (original['physical_line'] is None or (type(original['physical_line']) is int and original['physical_line'] > 0)), 'HOLD_ORIGINAL_CALL_OUTSIDE_ENTRY')
    history = source.get('historical_prefix')
    if history is None:
        records = []
        position = 0
        previous_ordinal = None
        physical_count = 0
    else:
        require(end >= history['bytes'], 'HOLD_HISTORY_PREFIX_OUTSIDE_CUTOFF')
        metadata = source['metadata']
        records = read_records(path, [metadata], [{'offset': metadata['offset'], 'bytes': metadata['bytes']}], source['physical'])['records']
        require(records[0]['row']['type'] == 'session_meta' and digest(canonical(records[0]['row']['payload'])) == source['metadata_payload_digest'], 'HOLD_METADATA_CHANGED')
        position = history['bytes']
        previous_ordinal = history['last_embedded_ordinal']
        physical_count = history['physical_records']
    wires = []
    activation_seen = False
    original_seen = False
    with open(path, 'rb') as stream:
        require(identity(os.fstat(stream.fileno())) == identity(initial), 'HOLD_SOURCE_CHANGED_BEFORE_READ')
        digestor = hashlib.sha256()
        if history is not None:
            remaining = history['bytes']
            while remaining:
                chunk = stream.read(min(65536, remaining))
                require(chunk, 'HOLD_HISTORY_PREFIX_TRUNCATED')
                digestor.update(chunk)
                remaining -= len(chunk)
            require(digestor.hexdigest() == history['sha256'], 'HOLD_HISTORY_PREFIX_CHANGED')
        while position < end:
            require(len(records) < MAX_RECORDS, 'HOLD_RECORD_COUNT_BOUND')
            wire = stream.readline(min(MAX_RECORD, end - position))
            require(0 < len(wire) <= MAX_RECORD and wire.endswith(b'\n') and (wire.count(b'\n') == 1) and (b'\r' not in wire) and (b'\x00' not in wire), 'HOLD_PARTIAL_OR_OVERFLOW_FRAME')
            row = json.loads(wire.decode('utf-8'), object_pairs_hook=unique)
            require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'}, {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and (type(row.get('ordinal')) is int) and (row['ordinal'] >= 0) and isinstance(row.get('timestamp'), str) and isinstance(row.get('type'), str) and isinstance(row.get('payload'), dict), 'HOLD_RECORD_SHAPE')
            locator = {'offset': position, 'bytes': len(wire), 'sha256': digest(wire), 'embedded_ordinal': row['ordinal'], 'physical_line': physical_count + 1}
            if not records:
                meta = source['metadata']
                require(row['type'] == 'session_meta' and all((locator[k] == meta[k] for k in ('offset', 'bytes', 'sha256', 'embedded_ordinal'))) and (digest(canonical(row['payload'])) == source['metadata_payload_digest']), 'HOLD_METADATA_CHANGED')
            else:
                if previous_ordinal is not None:
                    require(row['ordinal'] == previous_ordinal + 1, 'HOLD_EVENT_GAP_OR_DUPLICATE')
                else:
                    require(row['ordinal'] <= source['history_start_ordinal'], 'HOLD_ACTIVATION_COVERAGE_MISSING')
                previous_ordinal = row['ordinal']
                if row['ordinal'] >= source['history_start_ordinal']:
                    if not activation_seen:
                        require(row['ordinal'] == source['history_start_ordinal'], 'HOLD_ACTIVATION_COVERAGE_MISSING')
                    activation_seen = True
            if discovering and position == original['offset']:
                require(all((locator[key] == original[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal'))) and (original['physical_line'] is None or locator['physical_line'] == original['physical_line']) and (row['type'] == 'response_item') and (row['payload'].get('type') == 'custom_tool_call') and (row['payload'].get('name') == 'exec') and (row['payload'].get('call_id') == until_call['call_id']), 'HOLD_ORIGINAL_CALL_DIFFERS')
                original_seen = True
            elif discovering and position > original['offset']:
                require(original_seen, 'HOLD_ORIGINAL_CALL_NOT_COVERED')
            records.append({'row': row, 'locator': locator})
            wires.append(wire)
            digestor.update(wire)
            position += len(wire)
            physical_count += 1
            if discovering and original_seen and (row['type'] == 'response_item') and (row['payload'].get('type') == 'custom_tool_call_output') and (row['payload'].get('call_id') == until_call['call_id']):
                break
        if prior is not None and history is not None:
            stream.seek(0)
            remaining = prior['prefix_bytes']
            prior_hash = hashlib.sha256()
            while remaining:
                chunk = stream.read(min(65536, remaining))
                require(chunk, 'HOLD_PRIOR_PREFIX_TRUNCATED')
                prior_hash.update(chunk)
                remaining -= len(chunk)
            require(prior_hash.hexdigest() == prior['prefix_sha256'], 'HOLD_PRIOR_PREFIX_CHANGED')
        final = os.fstat(stream.fileno())
    _, current = physical(path)
    require(identity(initial) == identity(final) == identity(current) and (initial.st_size, initial.st_mtime_ns) == (final.st_size, final.st_mtime_ns) == (current.st_size, current.st_mtime_ns), 'HOLD_SOURCE_CHANGED_DURING_READ')
    require(activation_seen, 'HOLD_ACTIVATION_COVERAGE_MISSING')
    require(not discovering or original_seen, 'HOLD_ORIGINAL_CALL_NOT_COVERED')
    raw = b''.join(wires)
    if prior is not None and history is None:
        require(digest(raw[:prior['prefix_bytes']]) == prior['prefix_sha256'], 'HOLD_PRIOR_PREFIX_CHANGED')
    return (records, {'path': str(path), 'physical': source['physical'], 'prefix_bytes': position, 'prefix_sha256': digestor.hexdigest(), 'physical_records': physical_count, 'history_start_ordinal': source['history_start_ordinal'], 'host_producer_authenticated': False})

def original_bind_records(context, prepared, bind_request, store, session, owner):
    """Recover only the pending original call sealed in the entry prefix.

    A saved reply is preparation, not completion. Later matching retry calls
    cannot supply this call's missing output or move its fixed response end.
    """
    prior = prepared.get('hold_prefix')
    require(prior is not None, 'HOLD_BIND_PREFIX_ABSENT')
    entry, _ = hold_records(context, prior['prefix_bytes'], prior)
    historical_count = context['child'].get('historical_prefix', {}).get('physical_records', 1)
    require(historical_count + len(entry) - 1 == prior['physical_records'] and prior['history_start_ordinal'] == context['child']['history_start_ordinal'], 'HOLD_ORIGINAL_ENTRY_COVERAGE')
    original = bind_entry_record(context, entry, bind_request, store, session, owner)
    call_id = original['row']['payload'].get('call_id')
    records, prefix = hold_records(context, prior=prior, until_call={'path': context['child']['path'], 'physical': context['child']['physical'], 'locator': original['locator'], 'call_id': call_id})
    last = records[-1]
    completed = None
    if last['row']['payload'].get('type') == 'custom_tool_call_output' and last['row']['payload'].get('call_id') == call_id:
        completed = {key: resolve_record(context, 'child', locator)[1] for key, locator in (('call', original['locator']), ('result', last['locator']))}
    return (records, prefix, completed)

def history_with_priors(context, prepared, exchange, bind_request, store, session, owner, prior_context, cache, occurrence_sink=None):
    """Refuse any actual exact-episode USE while the observation hold is open.

    At initial bind, cover the source tail containing the pending original call.
    Retry and RETURN/JOIN resolve that call's own response from the sealed entry.
    Later selected USE or acceptance can never repair an observed early call.
    """
    occurrences = []
    retry = prepared.get('bound_response') is not None
    completed_bind = None
    if retry:
        records, prefix, completed_bind = original_bind_records(context, prepared, bind_request, store, session, owner)
    else:
        records, prefix = hold_records(context, prior=prepared.get('hold_prefix'))
    anchors = [prepared['authorization']['load_identity'], exchange['records']]
    if completed_bind is not None:
        anchors.append(completed_bind)
    indexed = {record['locator']['offset']: record for record in records}
    current_pairs = {}
    for pair in anchors:
        for pin in pair.values():
            actual = indexed.get(pin['locator']['offset'])
            require(pin['path'] == context['child']['path'] and pin['physical'] == context['child']['physical'] and (pin['role'] == 'child') and (pin['locator']['embedded_ordinal'] >= context['child']['history_start_ordinal']) and (actual is not None) and all((actual['locator'][key] == pin['locator'][key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal'))) and (pin['locator']['physical_line'] is None or actual['locator']['physical_line'] == pin['locator']['physical_line']), 'HOLD_ANCHOR_COVERAGE_DIFFERS')
        current_pairs[pair['call']['locator']['offset']] = pair['result']['locator']['offset']
    bind_input = profile_tool_input(context, delivery_tool_input(store, session, owner, bind_request))
    marker = '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange['identity'] + '\n'

    def witnessed(condition, reason, record):
        if not condition:
            raise HoldObservationRefusal(reason, prefix, record)
    if completed_bind is not None:
        current_call = completed_bind['call']
    else:
        original = bind_entry_record(context, records, bind_request, store, session, owner)
        current_call = resolve_record(context, 'child', original['locator'])[1]
    before(exchange['records']['result'], current_call)
    current_offset = current_call['locator']['offset']
    if completed_bind is None:
        current_pairs[current_offset] = None
    prior_occurrences, prior_proofs = prior_record_occurrences(context, prepared, current_call, records, prefix, store, session, owner, prior_context, cache)
    calls = {}
    completed = set()
    previous = None
    active_turn = None
    for record in records[1:]:
        row = record['row']
        if row['ordinal'] < context['child']['history_start_ordinal']:
            continue
        try:
            stamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            raise HoldObservationRefusal('HOLD_EVENT_TIMESTAMP', prefix, record) from None
        try:
            ordered = previous is None or previous < stamp
        except TypeError:
            ordered = False
        witnessed(ordered, 'HOLD_EVENT_ORDER', record)
        previous = stamp
        if context.get('source_association') in ('PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED', 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED'):
            if row['type'] == 'event_msg':
                if row['payload'].get('type') == 'task_started':
                    active_turn = row['payload'].get('turn_id')
                if row['payload'].get('type') == 'thread_settings_applied':
                    witnessed(allow_current_settings_event(context, record), 'HOLD_UNCLASSIFIED_EVENT', record)
                    continue
                witnessed(row['payload'].get('type') in ('task_started', 'item_completed', 'token_count', 'task_complete'), 'HOLD_UNCLASSIFIED_EVENT', record)
                continue
            if row['type'] in ('world_state', 'turn_context', 'token_usage_record', 'inter_agent_communication_metadata'):
                continue
        witnessed(row['type'] == 'response_item' and (current_record_metadata(row, context, active_turn) if context['profile_id'] in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE) else 'metadata' not in row), 'HOLD_UNCLASSIFIED_EVENT', record)
        payload = row['payload']
        kind = payload.get('type')
        if kind == 'custom_tool_call':
            command = payload.get('input')
            call_id = payload.get('call_id')
            witnessed(payload.get('name') == 'exec' and isinstance(command, str) and isinstance(call_id, str) and call_id, 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            witnessed(not command.startswith(marker), 'HOLD_EARLY_SAME_EPISODE_USE', record)
            if record['locator']['offset'] in prior_occurrences:
                continue
            witnessed(call_id not in calls, 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            if classify_prior_retry(context, record, records, prefix, current_call['locator']['offset'], prior_proofs, prior_occurrences, store, session, owner, occurrence_sink=occurrences if occurrence_sink is not None else None):
                continue
            foreign = re.match('^// COMPACTION_OBSERVATION_EXCHANGE=([0-9a-f]{64})\\n\\S', command)
            witnessed(record['locator']['offset'] in current_pairs or foreign is not None, 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            calls[call_id] = record['locator']['offset']
        elif kind == 'custom_tool_call_output':
            if record['locator']['offset'] in prior_occurrences:
                continue
            call_id = payload.get('call_id')
            witnessed(isinstance(call_id, str) and call_id in calls and (call_id not in completed), 'HOLD_UNPAIRED_TOOL_OUTPUT', record)
            origin = calls[call_id]
            witnessed(origin not in current_pairs or current_pairs[origin] == record['locator']['offset'], 'HOLD_UNPAIRED_TOOL_OUTPUT', record)
            completed.add(call_id)
        elif kind in ('message', 'agent_message'):
            continue
        elif context.get('source_association') in ('PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED', 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED') and kind == 'reasoning':
            continue
        elif (context.get('source_association') == 'PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED' or context['profile_id'] in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE)) and kind == 'function_call':
            call_id = payload.get('call_id')
            witnessed(payload.get('namespace') == 'collaboration' and payload.get('name') in ('send_message', 'wait_agent') and isinstance(payload.get('arguments'), str) and isinstance(call_id, str) and call_id and (call_id not in calls), 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            calls[call_id] = record['locator']['offset']
        elif (context.get('source_association') == 'PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED' or context['profile_id'] in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE)) and kind == 'function_call_output':
            call_id = payload.get('call_id')
            witnessed(isinstance(call_id, str) and call_id in calls and (call_id not in completed), 'HOLD_UNPAIRED_TOOL_OUTPUT', record)
            completed.add(call_id)
        else:
            raise HoldObservationRefusal('HOLD_UNCLASSIFIED_EVENT', prefix, record)
    outstanding = [offset for call_id, offset in calls.items() if call_id not in completed]
    require(not outstanding or (completed_bind is None and outstanding == [current_offset]), 'HOLD_UNSETTLED_TOOL_CALL')
    if retry:
        require(completed_bind is not None, 'HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED')
        completion = indexed[completed_bind['result']['locator']['offset']]
        try:
            bound_text, validated = command_response(context, 'child', completed_bind['call']['locator'], completed_bind['result']['locator'], bind_input)
        except ValueError as exc:
            if isinstance(exc, json.JSONDecodeError) or str(exc) in {'ACTUAL_HOST_CALL_RESULT_ASSOCIATION', 'FULL_HOST_OUTPUT_SHAPE', 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED', 'DUPLICATE_JSON_KEY'}:
                raise HoldObservationRefusal(str(exc), prefix, completion) from exc
            raise
        try:
            bound_value = json.loads(bound_text, object_pairs_hook=unique)
        except ValueError as exc:
            raise HoldObservationRefusal('FULL_MECHANICAL_BIND_RESPONSE_REQUIRED', prefix, completion) from exc
        witnessed(validated == completed_bind and bound_value == prepared['bound_response'], 'FULL_MECHANICAL_BIND_RESPONSE_REQUIRED', completion)
        before(exchange['records']['result'], completed_bind['call'])
        prefix['original_bind'] = completed_bind
    else:
        require(outstanding == [current_offset], 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    if occurrence_sink is not None:
        current_id = prepared['obligation']['observation_id']
        for semantic, pair in (('LOAD', prepared['authorization']['load_identity']), ('EXCHANGE', exchange['records'])):
            occurrences.append({'population': 'CURRENT', 'attempt_class': 'ORIGINAL', 'semantic': semantic, 'observation_id': current_id, 'completion': 'COMPLETED', 'records': pair})
        occurrences.append({'population': 'CURRENT', 'attempt_class': 'ORIGINAL', 'semantic': 'BIND', 'observation_id': current_id, 'completion': 'COMPLETED' if completed_bind is not None else 'PENDING', 'records': completed_bind if completed_bind is not None else {'call': current_call, 'result': None}})
        for proof in prior_proofs:
            prior = proof['prior']
            for semantic, pair in (('LOAD', prior['authorization']['load_identity']), ('EXCHANGE', prior['exchange']['records']), ('BIND', proof['original'])):
                occurrences.append({'population': 'PRIOR', 'attempt_class': 'ORIGINAL', 'semantic': semantic, 'observation_id': prior['obligation']['observation_id'], 'completion': 'COMPLETED', 'records': pair})
        occurrences.sort(key=lambda item: item['records']['call']['locator']['offset'])
        require(len(canonical(occurrences)) <= MAX_TOTAL, 'OCCURRENCE_EXPORT_BOUND')
        occurrence_sink.extend(occurrences)
    return prefix

def bind_entry_record(context, records, bind_request, store, session, owner):
    """Select the first physical original attempt, never a later same-ID reply."""
    expected = profile_tool_input(context, delivery_tool_input(store, session, owner, bind_request))
    matches = [record for record in records[1:] if record['row']['ordinal'] >= context['child']['history_start_ordinal'] and record['row']['type'] == 'response_item' and (record['row']['payload'].get('type') == 'custom_tool_call') and (record['row']['payload'].get('name') == 'exec') and (record['row']['payload'].get('input') == expected)]
    require(len(matches) == 1, 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    original = matches[0]
    identifier = original['row']['payload'].get('call_id')
    require(isinstance(identifier, str) and identifier, 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    require(not any((record['locator']['offset'] > original['locator']['offset'] and record['row']['payload'].get('type') == 'custom_tool_call_output' and (record['row']['payload'].get('call_id') == identifier) for record in records)), 'HOLD_ORIGINAL_BIND_NOT_PENDING_AT_ENTRY')
    return original

def prior_candidate_shape(context, current, identifier, prior):
    require(isinstance(identifier, str) and re.fullmatch('[0-9a-f]{64}', identifier) and (identifier != current['obligation']['observation_id']), 'HOLD_PRIOR_OBSERVATION_ID')
    closed(prior, ('observation', 'obligation', 'obligation_pin', 'authorization', 'exchange', 'delivery_request', 'hold_prefix', 'bind_request', 'bound_response'), 'HOLD_PRIOR_PREPARED_SHAPE')
    observation = closed(prior['observation'], ('child_id', 'scope', 'code', 'source_cutoff', 'source_problem', 'revision'), 'HOLD_PRIOR_OBSERVATION_SHAPE')
    require(type(observation['revision']) is int and type(current['observation']['revision']) is int and (0 <= observation['revision'] < current['observation']['revision']), 'HOLD_PRIOR_OBSERVATION_ORDER')
    scope = observation['scope']
    require(isinstance(scope, list) and 0 < len(scope) <= MAX_RECORDS, 'HOLD_PRIOR_SCOPE_BOUND')
    for item in scope:
        closed(item, ('id', 'version', 'kind'), 'HOLD_PRIOR_SCOPE_SHAPE')
        require(isinstance(item['id'], str) and item['id'] and isinstance(item['kind'], str) and item['kind'] and (type(item['version']) is int) and (item['version'] > 0), 'HOLD_PRIOR_SCOPE_SHAPE')
    require(len({item['id'] for item in scope}) == len(scope), 'HOLD_PRIOR_SCOPE_DUPLICATE')
    obligation = closed(prior['obligation'], ('schema', 'parent_identity', 'actual_child_identity', 'selected_child', 'observation_id', 'covered_boundary_versions', 'observation_source_cutoff', 'code_and_skill_pins', 'bounded_purpose', 'authority_ceiling'), 'HOLD_PRIOR_OBLIGATION_SHAPE')
    reference = current['obligation']
    require(obligation['schema'] == 'implementaudit.compaction-obligation.v1' and obligation['observation_id'] == identifier == digest(canonical(observation)) and (observation['child_id'] == context['actual_child_identity']['thread_id']) and (observation['code'] == reference['code_and_skill_pins']) and (obligation['covered_boundary_versions'] == scope) and (obligation['observation_source_cutoff'] == observation['source_cutoff']) and all((obligation[key] == reference[key] for key in ('parent_identity', 'actual_child_identity', 'selected_child', 'code_and_skill_pins', 'bounded_purpose', 'authority_ceiling'))) and (obligation['parent_identity'] == context['parent_identity']) and (obligation['actual_child_identity'] == context['actual_child_identity']) and (obligation['selected_child'] == 'audit-state') and (obligation['authority_ceiling'] == 'NONE'), 'HOLD_PRIOR_OBLIGATION_BINDING')
    closed(prior['obligation_pin'], ('path', 'bytes', 'sha256'), 'HOLD_PRIOR_OBLIGATION_PIN')
    expected_path = Path(current['obligation_pin']['path']).parent / (digest(canonical(obligation)) + '.json')
    require(prior['obligation_pin']['path'] == str(expected_path), 'HOLD_PRIOR_OBLIGATION_NAMESPACE')
    closed(prior['authorization'], ('value', 'text', 'record', 'load_identity', 'route_record', 'evidence'), 'HOLD_PRIOR_AUTHORIZATION_SHAPE')
    closed(prior['exchange'], ('identity', 'records', 'evidence'), 'HOLD_PRIOR_EXCHANGE_SHAPE')
    closed(prior['delivery_request'], ('child_id', 'phase', 'observation_id', 'authorization_evidence'), 'HOLD_PRIOR_DELIVERY_SHAPE')
    closed(prior['bind_request'], ('child_id', 'phase', 'observation_id', 'exchange'), 'HOLD_PRIOR_BIND_SHAPE')
    require(prior['delivery_request']['child_id'] == prior['bind_request']['child_id'] == observation['child_id'] and prior['delivery_request']['phase'] == 'deliver' and (prior['bind_request']['phase'] == 'bind') and (prior['delivery_request']['observation_id'] == prior['bind_request']['observation_id'] == identifier) and (prior['delivery_request']['authorization_evidence'] == prior['authorization']['evidence']) and (prior['bind_request']['exchange'] == prior['exchange']['evidence']), 'HOLD_PRIOR_REQUEST_BINDING')
    closed(prior['hold_prefix'], ('path', 'physical', 'prefix_bytes', 'prefix_sha256', 'physical_records', 'history_start_ordinal', 'host_producer_authenticated'), 'HOLD_PRIOR_ENTRY_SHAPE')
    require(prior['hold_prefix']['history_start_ordinal'] == context['child']['history_start_ordinal'] and prior['hold_prefix']['host_producer_authenticated'] is False, 'HOLD_PRIOR_ACTIVATION_BINDING')
    expected_response = {'observation_id': identifier, 'child_observation_exchange_identity': prior['exchange']['identity'], **observation, 'authority': 'NONE', 'canonical_currentness': False, 'recovery_authority': False, 'epoch_authority': False, 'effect_authority': False, 'independent_children': 'UNCHANGED', 'actual_child_result_consumer': 'UNQUALIFIED', 'same_failed_scope_retry': 'CONDITIONAL_UNQUALIFIED'}
    require(prior['bound_response'] == expected_response, 'HOLD_PRIOR_BOUND_RESPONSE_FIELDS')

def prior_record_occurrences(context, current, current_call, records, prefix, store, session, owner, candidates, cache):
    """Return only fully revalidated physical mechanical occurrences."""
    indexed = {record['locator']['offset']: record for record in records}
    admitted = set()
    proofs = []
    boundary = current_call['locator']['offset']
    for identifier, prior in sorted(candidates.items(), key=lambda item: item[1]['observation']['revision']):
        if identifier not in cache:
            raw, _ = artifact(prior['obligation_pin'])
            require(json.loads(raw, object_pairs_hook=unique) == prior['obligation'], 'HOLD_PRIOR_IMMUTABLE_OBLIGATION_CHANGED')
            skill_pin = current['authorization']['value']['skill_source_pin']
            validated = authorization(context, prior, prior['authorization']['evidence'], skill_pin)
            require(validated == prior['authorization'], 'HOLD_PRIOR_PUBLIC_AUTHORIZATION_CHANGED')
            exchange = completed_exchange(context, prior, prior['exchange']['evidence'], store, session, owner, skill_pin)
            require(exchange == prior['exchange'], 'HOLD_PRIOR_COMPLETED_EXCHANGE_CHANGED')
            _, _, first_completion = original_bind_records(context, prior, prior['bind_request'], store, session, owner)
            require(first_completion is not None, 'HOLD_PRIOR_ORIGINAL_COMPLETION_UNPROVED')
            require(first_completion['result']['locator']['offset'] + first_completion['result']['locator']['bytes'] <= boundary, 'HOLD_PRIOR_PHYSICAL_ORDER')
            earlier = {key: value for key, value in candidates.items() if value['observation']['revision'] < prior['observation']['revision']}
            try:
                held = history_with_priors(context, prior, exchange, prior['bind_request'], store, session, owner, earlier, cache)
            except HoldObservationRefusal as exc:
                raise HoldObservationRefusal('HOLD_PRIOR_OBSERVATION_REFUSED:' + str(exc), exc.evidence['prefix'], {'locator': exc.evidence['record']}) from exc
            require(held['original_bind'] == first_completion, 'HOLD_PRIOR_ORIGINAL_COMPLETION_CHANGED')
            cache[identifier] = {'held': held, 'prior': prior}
        proof = cache[identifier]
        original = proof['held']['original_bind']
        require(original['result']['locator']['offset'] + original['result']['locator']['bytes'] <= boundary, 'HOLD_PRIOR_PHYSICAL_ORDER')
        before(original['result'], current_call)
        pairs = (prior['authorization']['load_identity'], prior['exchange']['records'], original)

        def admit(record_pin):
            locator = record_pin['locator']
            actual = indexed.get(locator['offset'])
            require(record_pin['path'] == context['child']['path'] and record_pin['physical'] == context['child']['physical'] and (record_pin['role'] == 'child') and (actual is not None) and (locator['embedded_ordinal'] >= context['child']['history_start_ordinal']) and all((actual['locator'][key] == locator[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal'))) and (locator['physical_line'] is None or actual['locator']['physical_line'] == locator['physical_line']), 'HOLD_PRIOR_OCCURRENCE_BINDING')
            admitted.add(locator['offset'])
        for pair in pairs:
            for record_pin in pair.values():
                admit(record_pin)
        proofs.append({'prior': prior, 'original': original})
    return (admitted, proofs)

def classify_prior_retry(context, record, records, prefix, boundary, proofs, admitted, store, session, owner, occurrence_sink=None):
    """Called in physical scan order, after current early-USE/type/order checks."""
    payload = record['row']['payload']
    offset = record['locator']['offset']
    indexed = {item['locator']['offset']: item for item in records}
    for proof in proofs:
        prior, original = (proof['prior'], proof['original'])
        bind_input = profile_tool_input(context, delivery_tool_input(store, session, owner, prior['bind_request']))
        end = original['result']['locator']['offset'] + original['result']['locator']['bytes']
        if not end <= offset < boundary or payload.get('input') != bind_input:
            continue
        call_id = payload.get('call_id')
        following = [item for item in records if offset < item['locator']['offset'] < boundary and item['row']['payload'].get('call_id') == call_id and (item['row']['payload'].get('type') in ('custom_tool_call', 'custom_tool_call_output'))]
        require(following and following[0]['row']['payload'].get('type') == 'custom_tool_call_output', 'HOLD_PRIOR_RETRY_COMPLETION_UNPROVED')
        response = following[0]
        try:
            text, pair = command_response(context, 'child', record['locator'], response['locator'], bind_input)
            value = json.loads(text, object_pairs_hook=unique)
        except ValueError as exc:
            if isinstance(exc, json.JSONDecodeError) or str(exc) in {'ACTUAL_HOST_CALL_RESULT_ASSOCIATION', 'FULL_HOST_OUTPUT_SHAPE', 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED', 'DUPLICATE_JSON_KEY'}:
                raise HoldObservationRefusal('HOLD_PRIOR_RETRY_REFUSED:' + str(exc), prefix, response) from exc
            raise
        if value != prior['bound_response']:
            raise HoldObservationRefusal('HOLD_PRIOR_RETRY_RESPONSE_DIFFERS', prefix, response)
        before(original['result'], pair['call'])
        for record_pin in pair.values():
            locator = record_pin['locator']
            actual = indexed.get(locator['offset'])
            require(record_pin['path'] == context['child']['path'] and record_pin['physical'] == context['child']['physical'] and (record_pin['role'] == 'child') and (actual is not None) and all((actual['locator'][key] == locator[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'))), 'HOLD_PRIOR_RETRY_OCCURRENCE_BINDING')
            admitted.add(locator['offset'])
        if occurrence_sink is not None:
            occurrence_sink.append({'population': 'PRIOR', 'attempt_class': 'RETRY', 'semantic': 'BIND', 'observation_id': prior['obligation']['observation_id'], 'completion': 'COMPLETED', 'records': pair})
        return True
    return False

def _hold_history_unheld(context, prepared, exchange, bind_request, store, session, owner, prior_context=None, occurrence_sink=None):
    """Validate bounded prior candidates, then retain the complete history scan."""
    candidates = {} if prior_context is None else prior_context
    require(type(candidates) is dict and len(candidates) <= MAX_RECORDS, 'HOLD_PRIOR_CONTEXT_BOUND')
    require(len(canonical(candidates)) <= MAX_TOTAL, 'HOLD_PRIOR_CONTEXT_BOUND')
    for identifier, prior in candidates.items():
        prior_candidate_shape(context, prepared, identifier, prior)
    revisions = [prior['observation']['revision'] for prior in candidates.values()]
    require(len(set(revisions)) == len(revisions), 'HOLD_PRIOR_OBSERVATION_ORDER')
    if candidates:
        source_request = {role: {key: context[role][key] for key in ('path', 'metadata', 'allowed_ranges')} for role in ('parent', 'child')}
        source_request.update({key: context[key]['locator'] for key in ('open', 'spawn_call', 'spawn_output')})
        if 'logical_child_id' in context:
            source_request['child_thread_id'] = context['actual_child_identity']['thread_id']
        if context['profile_id'] in BOUNDARY_PROFILES:
            source_request['child_activation'] = context['child_activation']['locator']
        if context['profile_id'] == NONPROTECTED_PROFILE:
            nominations = {key: context[key]['locator'] for key in ('open', 'spawn_call', 'spawn_output', 'child_activation', 'parent_turn_start')}
            rebound = bind_nonprotected_sources(nominations, context['_source_profile_code_pins'])
            require(rebound['canonical_episode_binding']['opening_digest'] == context['canonical_episode_binding']['opening_digest'], 'NONPROTECTED_PRIOR_CANONICAL_OPEN_CHANGED')
            rebound['canonical_episode_binding'] = context['canonical_episode_binding']
        else:
            rebound = bind_sources(source_request, context['parent_identity']['thread_id'], context.get('logical_child_id', context['actual_child_identity']['thread_id']))
        require(rebound == context, 'HOLD_PRIOR_SOURCE_CONTEXT_CHANGED')
    return history_with_priors(context, prepared, exchange, bind_request, store, session, owner, candidates, {}, occurrence_sink=occurrence_sink)

def actual_result(context, prepared, evidence, store, session, owner, skill_pin, prior_context=None):
    closed(evidence, ('bound_exchange', 'use', 'child_final', 'parent_delivery'), 'ACTUAL_RESULT_EVIDENCE_SHAPE')
    require(prepared.get('exchange') is not None and prepared.get('bound_response') is not None, 'ACTUAL_CHILD_OBSERVATION_MISSING')
    exchange = completed_exchange(context, prepared, prepared['exchange']['evidence'], store, session, owner, skill_pin)
    require(exchange == prepared['exchange'], 'OBSERVED_EXCHANGE_CHANGED')
    closed(evidence['bound_exchange'], ('call', 'result'), 'BOUND_EXCHANGE_SHAPE')
    selected_occurrences = []
    held = hold_history(context, prepared, exchange, prepared['bind_request'], store, session, owner, prior_context=prior_context, occurrence_sink=selected_occurrences if context['profile_id'] == NONPROTECTED_PROFILE else None)
    bound_identity = held['original_bind']
    for key in ('call', 'result'):
        locator = evidence['bound_exchange'][key]
        original = bound_identity[key]['locator']
        require(isinstance(locator, dict) and set(locator) == set(original) and all((locator[field] == original[field] for field in original if field != 'physical_line')) and (locator['physical_line'] in (None, original['physical_line'])), 'BOUND_EXCHANGE_NOT_ORIGINAL')
    closed(evidence['use'], ('call', 'result'), 'ACTUAL_USE_EVIDENCE_SHAPE')
    use_row, use_pin = resolve_record(context, 'child', evidence['use']['call'])
    use_input = use_row['payload'].get('input')
    prefix = '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange['identity'] + '\n'
    require(isinstance(use_input, str) and use_input.startswith(prefix) and use_input[len(prefix):].strip(), 'ACTUAL_USE_EXCHANGE_BINDING')
    _, use_identity = command_response(context, 'child', evidence['use']['call'], evidence['use']['result'], use_input)
    before(bound_identity['result'], use_pin)
    final_row, final_pin = resolve_record(context, 'child', evidence['child_final'])
    final_phase = 'final' if context['profile_id'] == NONPROTECTED_PROFILE else 'final_answer'
    returned = typed_message(final_row, ('schema', 'obligation_digest', 'observation_id', 'child_observation_exchange_identity', 'exact_observed_boundary_versions', 'result_bytes_identity', 'authority_ceiling'), 'implementaudit.compaction-result-return.v1', phase=final_phase, context=context)
    before(use_identity['result'], final_pin)
    delivered_row, delivered_pin = resolve_record(context, 'parent', evidence['parent_delivery'])
    delivery = delivered_row['payload']
    envelope = 'Message Type: FINAL_ANSWER\nTask name: /root\nSender: ' + context['actual_child_identity']['agent_path'] + '\nPayload:\n'
    require(delivered_row['type'] == 'response_item' and delivery.get('type') == 'agent_message' and (delivery.get('author') == context['actual_child_identity']['agent_path']) and (delivery.get('recipient') == '/root') and (delivery.get('content') == [{'type': 'input_text', 'text': envelope + public_message(final_row, final_phase, context=context)}]), 'ACTUAL_FINAL_RETURN_DELIVERY_ASSOCIATION')
    before(final_pin, delivered_pin)
    obligation = prepared['obligation']
    bindings = {'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': obligation['observation_id'], 'child_observation_exchange_identity': exchange['identity'], 'exact_observed_boundary_versions': obligation['covered_boundary_versions']}
    require(all((returned[key] == value for key, value in bindings.items())), 'ACTUAL_RETURN_OBLIGATION_OR_SCOPE_DIFFERS')
    raw, result_physical = artifact(returned['result_bytes_identity'])
    result = json.loads(raw, object_pairs_hook=unique)
    closed(result, ('schema', *bindings, 'code_and_skill_pins', 'status', 'currentness', 'measured_epoch', 'frontier', 'members', 'authority_ceiling'), 'ACTUAL_RESULT_ARTIFACT_FIELDS')
    require(result['schema'] == 'implementaudit.compaction-reconciliation-result.v1' and all((result[key] == value for key, value in bindings.items())) and (result['code_and_skill_pins'] == obligation['code_and_skill_pins']) and (result['authority_ceiling'] == 'NONE') and (result['status'] in ('SUCCEEDED', 'FAILED')) and (result['currentness'] in ('VERIFIED', 'UNRESOLVED')) and (result['measured_epoch'] in ('VERIFIED', 'UNRESOLVED')) and isinstance(result['frontier'], str) and (0 < len(result['frontier']) <= 1024), 'ACTUAL_RESULT_ARTIFACT_BINDING')
    members = result['members']
    require(isinstance(members, list) and 0 < len(members) <= 32, 'RESULT_MEMBER_CLOSURE')
    result_path = Path(returned['result_bytes_identity']['path'])
    directory = result_path.parent
    member_identities = []
    admitted_members = []
    seen_paths = set()
    seen_physical = set()
    total = len(raw)
    for member in members:
        admitted = artifact_preflight(member)
        path, info = admitted
        file_identity = (info.st_dev, info.st_ino)
        require(path.is_relative_to(directory) and path != result_path and (path not in seen_paths) and (file_identity not in seen_physical), 'FOREIGN_OR_DUPLICATE_RESULT_MEMBER')
        seen_paths.add(path)
        seen_physical.add(file_identity)
        total += member['bytes']
        require(total <= MAX_TOTAL, 'RESULT_CLOSURE_BYTE_BOUND')
        admitted_members.append((member, admitted))
    total = len(raw)
    for member, admitted in admitted_members:
        member_raw, member_physical = artifact(member, admitted=admitted)
        total += len(member_raw)
        require(total <= MAX_TOTAL, 'RESULT_CLOSURE_BYTE_BOUND')
        member_identities.append({'pin': member, 'physical': member_physical})
    identity = {'obligation_digest': bindings['obligation_digest'], 'observation_id': bindings['observation_id'], 'child_observation_exchange_identity': exchange['identity'], 'scope': obligation['covered_boundary_versions'], 'result_pin': returned['result_bytes_identity'], 'result_physical': result_physical, 'members': member_identities, 'child_final': final_pin, 'parent_delivery': delivered_pin, 'bound_exchange': bound_identity, 'use': use_identity, 'authorization_record': prepared['authorization']['record'], 'hold_history': held}
    if context['profile_id'] == NONPROTECTED_PROFILE:
        identity['selected_occurrences'] = selected_occurrences
    return {'identity': identity, 'return_digest': digest(canonical(identity)), 'status': result['status'], 'currentness': result['currentness'], 'measured_epoch': result['measured_epoch'], 'frontier': result['frontier'], 'observation_id': bindings['observation_id'], 'evidence': evidence}

def acceptance(context, prepared, result, locator):
    row, record_pin = resolve_record(context, 'parent', locator)
    value = typed_message(row, ('schema', 'action', 'parent_identity', 'actual_child_identity', 'obligation_digest', 'observation_id', 'child_observation_exchange_identity', 'actual_result_digest', 'accepted_boundary_versions', 'observation_source_cutoff', 'authority_ceiling'), 'implementaudit.compaction-reconciliation-acceptance.v1', 'ACCEPT_BOUNDED_RECONCILIATION', context=context)
    o = prepared['obligation']
    expected = {'schema': 'implementaudit.compaction-reconciliation-acceptance.v1', 'action': 'ACCEPT_BOUNDED_RECONCILIATION', 'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'], 'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': o['observation_id'], 'child_observation_exchange_identity': prepared['exchange']['identity'], 'actual_result_digest': result['return_digest'], 'accepted_boundary_versions': o['covered_boundary_versions'], 'observation_source_cutoff': o['observation_source_cutoff'], 'authority_ceiling': 'NONE'}
    require(value == expected, 'ROOT_ACCEPTANCE_EXACT_RESULT_OR_SCOPE_DIFFERS')
    before(result['identity']['parent_delivery'], record_pin)
    return {'record': record_pin, 'value': value}

def fixed_policy(code_pins, profile_id=None):
    require(profile_id == NONPROTECTED_PROFILE, 'NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
    return nonprotected_fixed_policy(code_pins)

def custody_record(path, root):
    """Read a deterministic external record, bounded before content I/O."""
    path = Path(path)
    require(path.is_relative_to(root), 'FOREIGN_CUSTODY_RECORD')
    path, info = physical(path)
    require(0 < info.st_size <= MAX_TOTAL, 'CUSTODY_RECORD_BYTE_BOUND')
    with open(path, 'rb') as stream:
        require(identity(os.fstat(stream.fileno())) == identity(info), 'CUSTODY_RECORD_CHANGED')
        raw = stream.read(info.st_size)
    pin = {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}
    checked, actual_physical = artifact(pin, MAX_TOTAL)
    require(checked == raw and actual_physical == identity(info), 'CUSTODY_RECORD_CHANGED')
    return (json.loads(raw, object_pairs_hook=unique), pin)

def immutable_custody(root, name, value, writer):
    path = root / name
    if path.exists():
        prior, pin = custody_record(path, root)
        require(prior == value, 'CONFLICTING_IMMUTABLE_ACQUISITION')
    else:
        writer(path, value)
        prior, pin = custody_record(path, root)
        require(prior == value, 'IMMUTABLE_ACQUISITION_WRITE_DIFFERS')
    return pin

def acquire_candidate(context, prepared, result, accepted, policy, root, writer):
    """Capture exact already validated C without claiming source authentication."""
    records = []

    def collect(value):
        if isinstance(value, dict):
            if {'path', 'physical', 'role', 'locator', 'timestamp', 'message_or_call_id'} == set(value):
                records.append(value)
            else:
                for child in value.values():
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    for value in (context['open'], context['spawn_call'], context['spawn_output'], prepared['authorization'], prepared['exchange'], result['identity'], accepted):
        collect(value)
    unique_records = {}
    for expected in records:
        _, actual = resolve_record(context, expected['role'], expected['locator'])
        require(actual == expected, 'ACQUIRED_RECORD_IDENTITY_CHANGED')
        unique_records[digest(canonical(actual))] = actual
    o = prepared['obligation']
    sources = {role: {key: item for key, item in context[role].items() if key != 'allowed_ranges'} if context.get('source_association') == 'PUBLIC_OPEN_SPAWN_ACTIVATION_STRUCTURAL_UNQUALIFIED' else context[role] for role in ('parent', 'child')}
    candidate = {'schema': 'implementaudit.compaction-unconsumed-acquisition.v1', 'policy_digest': policy['policy_digest'], 'producer_environment_identity': {'profile_id': policy['descriptor']['profile_id'], 'parent_metadata': context['parent']['metadata_payload_digest'], 'child_metadata': context['child']['metadata_payload_digest']}, 'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'], 'assignment_identity': digest(canonical({'child': o['actual_child_identity'], 'code': o['code_and_skill_pins']})), 'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': o['observation_id'], 'covered_boundary_versions': o['covered_boundary_versions'], 'O_U_exchange_USE_R_A_identities': {'O': prepared['obligation_pin'], 'U': prepared['authorization']['record'], 'exchange': prepared['exchange']['records'], 'USE': result['identity']['use'], 'R': result['identity'], 'A': accepted}, 'physical_source_and_cutoff_identities': {'parent': sources['parent'], 'child': sources['child'], 'compaction_cutoff': o['observation_source_cutoff'], 'records': list(unique_records.values())}, 'exact_result_digest': result['return_digest'], 'exact_acceptance_digest': digest(canonical(accepted)), 'source_origin_validation': 'UNESTABLISHED', 'host_producer_authenticated': False, 'authority_ceiling': 'NONE'}
    name = 'candidates/' + digest(canonical(candidate)) + '.json'
    return (candidate, immutable_custody(root, name, candidate, writer))

def production_profile(policy, root):
    """Resolve Q as data. Q bindings alone never authenticate an episode."""
    path = root / policy['descriptor']['qualification_key']
    if not path.exists():
        return {'status': 'POLICY_QUALIFICATION_ABSENT', 'policy_qualified': None, 'qualification_record_bound': False, 'policy_digest': policy['policy_digest'], 'Q': None}
    q, q_pin = custody_record(path, root)
    closed(q, ('policy_digest', 'producer_environment_identity', 'qualification_scope', 'actual_acquisition_evidence', 'independent_review', 'ROOT_qualification_selection', 'authority_ceiling'), 'POLICY_QUALIFICATION_FIELDS')
    require(q['policy_digest'] == policy['policy_digest'] and q['authority_ceiling'] == 'NONE' and (q['qualification_scope'] == {'profile_id': policy['descriptor']['profile_id'], 'candidate_consumption_required': False}), 'POLICY_QUALIFICATION_BINDING')
    evidence_pin = q['actual_acquisition_evidence']
    closed(evidence_pin, ('path', 'bytes', 'sha256'), 'QUALIFICATION_ACQUISITION_PIN')
    evidence_path = Path(evidence_pin['path'])
    require(evidence_path.parent == root / 'candidates', 'QUALIFICATION_CANDIDATE_NAMESPACE')
    evidence, checked_pin = custody_record(evidence_path, root)
    require(checked_pin == evidence_pin and evidence['schema'] == 'implementaudit.compaction-unconsumed-acquisition.v1' and (evidence['policy_digest'] == policy['policy_digest']) and (evidence['producer_environment_identity'] == q['producer_environment_identity']) and (evidence['authority_ceiling'] == 'NONE'), 'QUALIFICATION_ACTUAL_CANDIDATE_BINDING')
    subject = {key: q[key] for key in ('policy_digest', 'producer_environment_identity', 'qualification_scope', 'actual_acquisition_evidence')}
    proof_pins = []
    for field in ('independent_review', 'ROOT_qualification_selection'):
        item = q[field]
        closed(item, ('path', 'bytes', 'sha256'), 'QUALIFICATION_REVIEW_PIN')
        require(Path(item['path']).parent == root / 'qualification', 'QUALIFICATION_REVIEW_NAMESPACE')
        record, actual_pin = custody_record(Path(item['path']), root)
        require(actual_pin == item, 'QUALIFICATION_REVIEW_PIN_CHANGED')
        closed(record, ('subject', 'disposition', 'authority_ceiling'), 'QUALIFICATION_REVIEW_FIELDS')
        require(record['subject'] == subject and record['authority_ceiling'] == 'NONE' and (record['disposition'] == ('PASS' if field == 'independent_review' else 'SELECTED')), 'QUALIFICATION_REVIEW_BINDING')
        proof_pins.append(actual_pin)
    return {'status': 'QUALIFICATION_RECORD_BOUND_ORIGIN_UNRESOLVED', 'policy_qualified': None, 'qualification_record_bound': True, 'policy_digest': policy['policy_digest'], 'Q': q_pin, 'evidence': checked_pin, 'review_pins': proof_pins, 'unresolved_implementation_edge': 'No independently authenticating producer/custody validator is established'}

def episode_value(candidate, candidate_pin, q_pin):
    return {key: candidate[key] for key in ('policy_digest', 'parent_identity', 'actual_child_identity', 'assignment_identity', 'obligation_digest', 'observation_id', 'covered_boundary_versions', 'O_U_exchange_USE_R_A_identities', 'physical_source_and_cutoff_identities', 'exact_result_digest', 'exact_acceptance_digest', 'authority_ceiling')} | {'Q_digest': q_pin['sha256'], 'actual_acquisition_and_custody_validation_evidence': {'candidate': candidate_pin}}

def terminal_release_identity(context, prepared, candidate):
    if context['profile_id'] in BOUNDARY_PROFILES:
        require('historical_assignment_digest' not in prepared, 'BOUNDARY_HISTORICAL_MIGRATION_NOT_SELECTED')
        assignment = {'assignment_identity': candidate['assignment_identity']}
    else:
        assignment = {'historical_assignment_digest': prepared['historical_assignment_digest']}
    return {'child_id': candidate['actual_child_identity']['agent_path'], **assignment, 'scope': candidate['covered_boundary_versions'], 'worker_terminal': 'COMPLETED', 'effect_reconciliation': 'NO_UNRECONCILED_EFFECTS', 'explicit_release': 'GRANTED'}

def source_owner_attestation(owner, candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, custody_root, release_evidence):
    """Verify a source-owned issuer selected by fixed P, never by a caller."""
    pin = owner['module_pin']
    raw, _ = artifact(pin, maximum=65536)
    path, _ = physical(pin['path'])
    require(path.parent == Path(__file__).resolve().parent and digest(raw) == pin['sha256'], 'SOURCE_OWNER_MODULE_PIN_CHANGED')
    if context['profile_id'] == NONPROTECTED_PROFILE:
        import types
        module = types.ModuleType('_fixed_compaction_source_owner')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    else:
        spec = importlib.util.spec_from_file_location('_fixed_compaction_source_owner', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        require(digest(path.read_bytes()) == pin['sha256'], 'SOURCE_OWNER_MODULE_PIN_CHANGED')
    require(callable(getattr(module, 'validate', None)), 'SOURCE_OWNER_VALIDATOR_ABSENT')
    value = module.validate(candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, Path(custody_root), release_evidence)
    return validate_source_owner_attestation_record(value, owner, candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, release_evidence)

def validate_source_owner_attestation_record(value, owner, candidate, candidate_pin, context, prepared, result, accepted, policy, q_pin, release_evidence):
    release = terminal_release_identity(context, prepared, candidate)
    expected = {'schema': 'implementaudit.source-owner-episode-attestation.v1', 'issuer_id': owner['issuer_id'], 'policy_digest': policy['policy_digest'], 'candidate_sha256': candidate_pin['sha256'], 'Q_sha256': q_pin['sha256'], 'parent_identity': candidate['parent_identity'], 'actual_child_identity': candidate['actual_child_identity'], 'obligation_digest': candidate['obligation_digest'], 'result_digest': result['return_digest'], 'acceptance_digest': candidate['exact_acceptance_digest'], 'parent_source_physical': context['parent']['physical'], 'child_source_physical': context['child']['physical'], 'terminal_effect_release': release, 'authority_ceiling': 'NONE'}
    extra = ('current_public_record_binding',) if context['profile_id'] in (CURRENT_BOUNDARY_PROFILE, NONPROTECTED_PROFILE) else ()
    closed(value, (*expected, 'host_source_binding', 'release_evidence', *extra), 'SOURCE_OWNER_ATTESTATION_SHAPE')
    if context['profile_id'] == NONPROTECTED_PROFILE:
        _validate_nonprotected_public_proof(value['current_public_record_binding'], context)
    elif extra:
        proof = closed(value['current_public_record_binding'], ('schema', 'records', 'source_prefixes', 'anchor_response_sha256s', 'authority_ceiling'), 'CURRENT_PUBLIC_BINDING_SHAPE')
        require(proof['schema'] == 'implementaudit.current-native-public-record-binding.v1' and proof['authority_ceiling'] == 'NONE' and (len(proof['records']) == 6), 'CURRENT_PUBLIC_BINDING_SHAPE')
    require(all((value[key] == item for key, item in expected.items())) and value['release_evidence'] == release_evidence, 'SOURCE_OWNER_ATTESTATION_OR_RELEASE_DIFFERS')
    binding = closed(value['host_source_binding'], ('schema', 'native_reader_sha256', 'provider_selection_sha256', 'native_version', 'native_executable_sha256', 'desktop_executable_sha256', 'desktop_asar_sha256', 'config_sha256', 'parent_thread_read_response_sha256', 'child_thread_read_response_sha256', 'parent_source_physical', 'child_source_physical', 'authority_ceiling'), 'SOURCE_OWNER_HOST_BINDING_SHAPE')
    require(binding['schema'] == 'implementaudit.codex-app-exact-source-binding.v1' and binding['native_reader_sha256'] == owner['native_reader_pin']['sha256'] and (binding['provider_selection_sha256'] == policy['descriptor']['exact_host_tuple']['provider_selection_sha256']) and (binding['native_version'] == policy['descriptor']['exact_host_tuple']['native_version']) and (binding['native_executable_sha256'] == owner['native_binary']['sha256']) and (binding['desktop_executable_sha256'] == owner['desktop_executable']['sha256']) and (binding['desktop_asar_sha256'] == owner['desktop_asar']['sha256']) and (binding['config_sha256'] == owner['config_file']['sha256']) and (binding['parent_source_physical'] == context['parent']['physical']) and (binding['child_source_physical'] == context['child']['physical']) and (binding['authority_ceiling'] == 'NONE') and all((isinstance(binding[key], str) and re.fullmatch('[0-9a-f]{64}', binding[key]) for key in ('parent_thread_read_response_sha256', 'child_thread_read_response_sha256'))), 'SOURCE_OWNER_HOST_BINDING_CHANGED')
    return value

def acquire_episode(context, prepared, result, accepted, code_pins, custody_root, writer, policy=None, release_evidence=None):
    """Reachable existing-owner acquisition/admission seam; no new command."""
    policy = fixed_policy(code_pins, context['profile_id']) if policy is None else policy
    expected = fixed_policy(code_pins, context['profile_id']) if context['profile_id'] in (PROFILE, STRUCTURAL_BOUNDARY_PROFILE, *BOUNDARY_PROFILES) else current_fixed_policy(code_pins)
    require(policy['code_and_skill_pins'] == code_pins and policy == expected, 'ACQUISITION_FIXED_POLICY_CHANGED')
    root = Path(custody_root) / policy['descriptor']['custody_namespace'] / policy['policy_digest']
    candidate, candidate_pin = acquire_candidate(context, prepared, result, accepted, policy, root, writer)
    profile = production_profile(policy, root)
    episode_key = digest(canonical({'policy': policy['policy_digest'], 'candidate': candidate_pin['sha256'], 'result': result['return_digest'], 'acceptance': candidate['exact_acceptance_digest']}))
    path = root / 'episodes' / (episode_key + '.json')
    response = {'status': 'CANDIDATE_ACQUIRED_PENDING_QUALIFICATION', 'policy': policy, 'profile': profile, 'candidate': candidate_pin, 'lookup': {'Q': str(root / policy['descriptor']['qualification_key']), 'E': str(path)}, 'episode_record_bound': False, 'episode': None, 'origin_validated': None, 'host_producer_authenticated': False, 'terminal_effect_release_qualified': False, 'authority_ceiling': 'NONE', 'unresolved_implementation_edge': 'Fixed source owner awaits exact episode qualification and ROOT release' if policy['descriptor']['authenticating_source_owner'] is not None else 'Authenticating producer/custody acquisition validator is not implemented or qualified'}
    if profile['qualification_record_bound']:
        response['status'] = 'QUALIFICATION_BOUND_PENDING_EPISODE_ORIGIN'
        response['episode_candidate'] = episode_value(candidate, candidate_pin, profile['Q'])
    owner = policy['descriptor']['authenticating_source_owner']
    if owner is not None and profile['qualification_record_bound']:
        if context['profile_id'] in BOUNDARY_PROFILES:
            require(context.get('source_association') == 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED' and 'historical_assignment_digest' not in prepared and candidate['covered_boundary_versions'] and all((item['kind'] == 'COMPLETED_RESUMED_BOUNDARY' for item in candidate['covered_boundary_versions'])), 'SOURCE_OWNER_BOUNDARY_CONTEXT_REQUIRED')
        else:
            raise ValueError('NONPROTECTED_PROJECTION_PROFILE_REQUIRED')
        attestation = source_owner_attestation(owner, candidate, candidate_pin, context, prepared, result, accepted, policy, profile['Q'], custody_root, release_evidence)
        require(production_profile(policy, root) == profile, 'SOURCE_OWNER_QUALIFICATION_CHANGED_DURING_READ')
        artifact(candidate_pin)
        selected = fixed_policy(code_pins, context['profile_id']) if context['profile_id'] in (PROFILE, STRUCTURAL_BOUNDARY_PROFILE, *BOUNDARY_PROFILES) else current_fixed_policy(code_pins)
        require(selected == policy, 'SOURCE_OWNER_POLICY_CHANGED_DURING_READ')
        attestation_pin = immutable_custody(root, 'attestations/' + digest(canonical(attestation)) + '.json', attestation, writer)
        episode = episode_value(candidate, candidate_pin, profile['Q'])
        episode['actual_acquisition_and_custody_validation_evidence']['source_owner_attestation'] = attestation_pin
        episode_pin = immutable_custody(root, 'episodes/' + episode_key + '.json', episode, writer)
        response.update(status='ADMITTED_EXACT_SOURCE_OWNER_EPISODE', episode_candidate=episode, episode_record_bound=True, episode=episode_pin, source_owner_attestation=attestation_pin, origin_validated=True, terminal_effect_release_qualified=True, host_producer_authenticated=True)
        response['profile'] = {**profile, 'status': 'POLICY_QUALIFIED_BY_FIXED_SOURCE_OWNER', 'policy_qualified': True}
        response['profile'].pop('unresolved_implementation_edge', None)
        response.pop('unresolved_implementation_edge', None)
        return response
    if path.exists():
        require(profile['qualification_record_bound'], 'EPISODE_WITHOUT_EXACT_Q')
        episode, episode_pin = custody_record(path, root)
        require(episode == response['episode_candidate'], 'EXACT_EPISODE_BINDING_DIFFERS')
        response.update(status='EPISODE_BOUND_PENDING_ORIGIN_VALIDATOR', episode=episode_pin, episode_record_bound=True)
    require(owner is None or profile['qualification_record_bound'] is False, 'SOURCE_OWNER_QUALIFICATION_REQUIRED')
    return response

def read_records(path, selectors, allowed_ranges, expected_physical=None):
    """Read only prevalidated exact ranges; never scan a prefix then filter.

The calling owner must establish allowed_ranges independently. This primitive
does not promote a supplied range, digest, path or physical ID into provenance.
Physical line labels are preserved as labels; embedded ordinals are separately
checked against actual wire bytes, with no assumption that the two are equal.
"""
    require(isinstance(selectors, list) and 0 < len(selectors) <= MAX_RECORDS, 'RECORD_COUNT_BOUND')
    require(isinstance(allowed_ranges, list) and 0 < len(allowed_ranges) <= MAX_RECORDS, 'ALLOWED_RANGE_SHAPE')
    for window in allowed_ranges:
        require(isinstance(window, dict) and set(window) == {'offset', 'bytes'} and (type(window['offset']) is int) and (window['offset'] >= 0) and (type(window['bytes']) is int) and (0 < window['bytes'] <= MAX_TOTAL), 'ALLOWED_RANGE_BOUND')
    total = 0
    intervals = []
    for item in selectors:
        require(isinstance(item, dict) and set(item) == {'offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'}, 'RECORD_LOCATOR_SHAPE')
        require(type(item['offset']) is int and item['offset'] >= 0 and (type(item['bytes']) is int) and (0 < item['bytes'] <= MAX_RECORD), 'RECORD_BYTE_BOUND')
        require(isinstance(item['sha256'], str) and re.fullmatch('[0-9a-f]{64}', item['sha256']) and (type(item['embedded_ordinal']) is int) and (item['embedded_ordinal'] >= 0) and (item['physical_line'] is None or (type(item['physical_line']) is int and item['physical_line'] > 0)), 'RECORD_IDENTITY_SHAPE')
        end = item['offset'] + item['bytes']
        require(any((window['offset'] <= item['offset'] and end <= window['offset'] + window['bytes'] for window in allowed_ranges)), 'OUTSIDE_ALLOWED_READ_RANGE')
        intervals.append((item['offset'], end))
        total += item['bytes']
    require(total <= MAX_TOTAL, 'TOTAL_RECORD_BYTE_BOUND')
    intervals.sort()
    require(all((left[1] <= right[0] for left, right in zip(intervals, intervals[1:]))), 'OVERLAPPING_RECORD_LOCATORS')
    path, before = physical(path)
    require(expected_physical is None or expected_physical == identity(before), 'SOURCE_PHYSICAL_ID_CHANGED')
    require(all((end <= before.st_size for _, end in intervals)), 'RECORD_RANGE_PAST_END')
    records = []
    with open(path, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        require(identity(opened) == identity(before) and opened.st_nlink == 1, 'SOURCE_CHANGED_BEFORE_READ')
        for selector in selectors:
            stream.seek(selector['offset'])
            raw = stream.read(selector['bytes'])
            require(len(raw) == selector['bytes'] and hashlib.sha256(raw).hexdigest() == selector['sha256'], 'RECORD_PIN_CHANGED')
            require(raw.endswith(b'\n') and raw.count(b'\n') == 1 and (b'\r' not in raw) and (b'\x00' not in raw), 'RECORD_PARTIAL_OR_MULTIPLE_WIRE')
            row = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
            require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'}, {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and (type(row.get('ordinal')) is int) and (row['ordinal'] == selector['embedded_ordinal']) and isinstance(row.get('timestamp'), str) and isinstance(row.get('type'), str) and isinstance(row.get('payload'), dict), 'OBSERVED_RECORD_SHAPE_OR_ORDINAL')
            records.append({'locator': dict(selector), 'row': row})
        after_open = os.fstat(stream.fileno())
    _, after_path = physical(path)
    require(identity(after_path) == identity(after_open) == identity(before) and (before.st_size, before.st_mtime_ns) == (after_open.st_size, after_open.st_mtime_ns) == (after_path.st_size, after_path.st_mtime_ns), 'SOURCE_CHANGED_DURING_READ')
    return {'path': str(path), 'physical': identity(before), 'records': records, 'host_producer_authenticated': False}
NONPROTECTED_PROFILE = 'codex-app-bounded-public-nonprotected-v1'
BOUNDARY_PROFILES = (*BOUNDARY_PROFILES, NONPROTECTED_PROFILE)

def _nonprotected_source_owner(code_pins):
    """Load the existing owner by exact verified bytes; never execute a reread."""
    import types
    path = Path(__file__).resolve().with_name('compaction-source-owner-codex-app.py')
    key = str(Path('implementaudit/scripts/compaction-source-owner-codex-app.py'))
    require(key in code_pins, 'NONPROTECTED_OWNER_CODE_PIN_ABSENT')
    pin = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': code_pins[key]}
    raw, _ = artifact(pin, maximum=128 * 1024)
    module = types.ModuleType('_nonprotected_source_owner')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module

def _nonprotected_observation_view():
    import types
    return types.SimpleNamespace(**globals())

def nonprotected_fixed_policy(code_pins):
    return _nonprotected_source_owner(code_pins).nonprotected_fixed_policy(_nonprotected_observation_view(), code_pins)

def bind_nonprotected_sources(request, code_pins):
    """No caller child UUID, profile or path participates in source selection."""
    return _nonprotected_source_owner(code_pins).nonprotected_bind_sources(_nonprotected_observation_view(), request, code_pins)

def _nonprotected_read_records(context, role, selectors):
    code_pins = context['_source_profile_code_pins']
    owner = _nonprotected_source_owner(code_pins)
    with owner.nonprotected_sources_guard(_nonprotected_observation_view(), context, code_pins):
        source = context[role]
        return read_records(source['path'], selectors, source['allowed_ranges'], source['physical'])

def hold_history(context, prepared, exchange, bind_request, store, session, owner, prior_context=None, occurrence_sink=None):
    if context['profile_id'] != NONPROTECTED_PROFILE:
        return _hold_history_unheld(context, prepared, exchange, bind_request, store, session, owner, prior_context=prior_context, occurrence_sink=occurrence_sink)
    code_pins = context['_source_profile_code_pins']
    source_owner = _nonprotected_source_owner(code_pins)
    with source_owner.nonprotected_sources_guard(_nonprotected_observation_view(), context, code_pins):
        return _hold_history_unheld(context, prepared, exchange, bind_request, store, session, owner, prior_context=prior_context, occurrence_sink=occurrence_sink)

def _validate_nonprotected_public_proof(proof, context):
    closed(proof, ('schema', 'records', 'source_prefixes', 'anchor_response_sha256s', 'canonical_episode_binding', 'authority_ceiling'), 'NONPROTECTED_PUBLIC_BINDING_SHAPE')
    require(proof['schema'] == 'implementaudit.nonprotected-native-public-record-binding.v1' and proof['authority_ceiling'] == 'NONE' and (len(proof['records']) == 6) and (proof['canonical_episode_binding']['schema'] == 'implementaudit.r0033-current-episode-binding.v1') and (proof['canonical_episode_binding']['opening_digest'] == context['canonical_episode_binding']['opening_digest']) and (proof['canonical_episode_binding']['host_and_scope']['host_session_id'] == context['parent_identity']['thread_id']), 'NONPROTECTED_PUBLIC_CANONICAL_BINDING')

def export_selected_occurrences(context, prepared, exchange, bind_request, store, session, owner, prior_context=None):
    """Expose classifications only from successful existing owner branches.

    The exporter shares the original hold/history validator, so copied calls,
    missing original completion and failed priors retain the same vetoes.
    No caller-provided class or later successful output supplies a missing fact.
    """
    output = []
    prefix = hold_history(context, prepared, exchange, bind_request, store, session, owner, prior_context=prior_context, occurrence_sink=output)
    return {'schema': 'implementaudit.compaction-selected-occurrences.v1', 'observation_id': prepared['obligation']['observation_id'], 'actual_child_identity': context['actual_child_identity'], 'covered_boundary_versions': prepared['obligation']['covered_boundary_versions'], 'source_cutoff': prefix, 'occurrences': output, 'authority_ceiling': 'NONE'}

def _episode_export_pin(value):
    closed(value, ('path', 'bytes', 'sha256'), 'EPISODE_EXPORT_PIN_SHAPE')
    require(isinstance(value['path'], str) and 0 < len(value['path']) <= 4096 and (type(value['bytes']) is int) and (0 < value['bytes'] <= MAX_TOTAL) and isinstance(value['sha256'], str) and re.fullmatch('[0-9a-f]{64}', value['sha256']), 'EPISODE_EXPORT_PIN_BINDING')

def _episode_export_scope(value):
    require(isinstance(value, list) and len(value) <= 4096, 'EPISODE_EXPORT_SCOPE_BOUND')
    seen = set()
    for row in value:
        closed(row, ('id', 'version', 'kind'), 'EPISODE_EXPORT_SCOPE_SHAPE')
        require(isinstance(row['id'], str) and 0 < len(row['id']) <= 256 and (row['id'] not in seen) and (type(row['version']) is int) and (row['version'] > 0) and (row['kind'] in ('COMPLETED_RESUMED_BOUNDARY', 'AMBIGUOUS_MARKER_GROUP', 'UNRESOLVED_RESUME_OBSERVATION', 'UNRESOLVED_SIGNAL')), 'EPISODE_EXPORT_SCOPE_BINDING')
        seen.add(row['id'])

def _episode_export_path(value):
    require(isinstance(value, str) and 0 < len(value) <= 4096 and ('\x00' not in value) and (re.match('^(?:[A-Za-z]:[\\\\/]|/[^/])', value) is not None) and all((part not in ('.', '..') and '~' not in part for part in re.split('[\\\\/]', value))), 'EPISODE_EXPORT_SOURCE_PATH')

def _episode_export_physical(value):
    closed(value, ('device', 'inode'), 'EPISODE_EXPORT_SOURCE_PHYSICAL_SHAPE')
    require(all((type(item) is int and item > 0 for item in value.values())), 'EPISODE_EXPORT_SOURCE_PHYSICAL_BINDING')

def _episode_export_locator(value):
    closed(value, ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'), 'EPISODE_EXPORT_SOURCE_LOCATOR_SHAPE')
    require(type(value['offset']) is int and value['offset'] >= 0 and (type(value['bytes']) is int) and (0 < value['bytes'] <= 256 * 1024) and isinstance(value['sha256'], str) and re.fullmatch('[0-9a-f]{64}', value['sha256']) and (type(value['embedded_ordinal']) is int) and (value['embedded_ordinal'] >= 0) and (value['physical_line'] is None or (type(value['physical_line']) is int and value['physical_line'] > 0)), 'EPISODE_EXPORT_SOURCE_LOCATOR_BINDING')

def _episode_export_source(value, role, episode, opening_digest):
    closed(value, ('path', 'physical', 'metadata', 'metadata_payload_digest', 'history_start_ordinal', 'allowed_ranges', 'canonical_open_binding_digest'), 'EPISODE_EXPORT_SOURCE_SHAPE')
    _episode_export_path(value['path'])
    _episode_export_physical(value['physical'])
    _episode_export_locator(value['metadata'])
    identity = episode['parent_identity'] if role == 'parent' else episode['actual_child_identity']
    require(value['path'].endswith('-' + identity['thread_id'] + '.jsonl') and value['metadata']['offset'] == value['metadata']['embedded_ordinal'] == 0 and (value['metadata']['physical_line'] == 1) and (value['history_start_ordinal'] == (0 if role == 'parent' else 1)) and (value['canonical_open_binding_digest'] == opening_digest) and isinstance(value['metadata_payload_digest'], str) and re.fullmatch('[0-9a-f]{64}', value['metadata_payload_digest']), 'EPISODE_EXPORT_SOURCE_IDENTITY_BINDING')
    ranges = value['allowed_ranges']
    require(isinstance(ranges, list) and 0 < len(ranges) <= 64, 'EPISODE_EXPORT_SOURCE_RANGE_BOUND')
    end = 0
    for window in ranges:
        closed(window, ('offset', 'bytes'), 'EPISODE_EXPORT_SOURCE_RANGE_SHAPE')
        require(type(window['offset']) is int and window['offset'] == end and (type(window['bytes']) is int) and (0 < window['bytes'] <= MAX_TOTAL), 'EPISODE_EXPORT_SOURCE_RANGE_BINDING')
        end += window['bytes']
    require(value['metadata']['bytes'] <= end <= 64 * MAX_TOTAL, 'EPISODE_EXPORT_SOURCE_RANGE_BOUND')
    return end

def _episode_export_route_binding(owner, episode):
    route = closed(owner['canonical_route'], ('controller_id', 'controller_record_oid', 'ref', 'record_oid',
        'record_identity', 'decision', 'classification', 'route_transaction_id', 'obligation_id', 'route_state'),
        'EPISODE_EXPORT_CANONICAL_ROUTE_SHAPE')
    scope = closed(owner['host_and_scope'], ('host_id', 'host_session_id', 'host_binding_generation', 'host_correlation_id',
        'continuity_generation', 'continuity_receipt', 'obligation_id', 'route_transaction_id', 'controller_id',
        'claim_id', 'explicit_run_root'), 'EPISODE_EXPORT_HOST_SCOPE_SHAPE')
    require(isinstance(route['controller_id'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', route['controller_id']) and
        route['ref'] == 'refs/implementaudit/route-decisions/' + route['controller_id'] and
        all(isinstance(route[key], str) and re.fullmatch('[0-9a-f]{40}(?:[0-9a-f]{24})?', route[key])
            for key in ('controller_record_oid', 'record_oid')) and route['decision'] == 'REQUIRED' and
        route['classification'] in ('MECHANICALLY_REQUIRED', 'JUDGEMENT_REQUIRED') and
        route['route_state'] in ('OPEN', 'RETURNED', 'SATISFIED'), 'EPISODE_EXPORT_CANONICAL_ROUTE_BINDING')
    for item in (route['record_identity'], route['route_transaction_id'], route['obligation_id'], scope['host_correlation_id']):
        require(isinstance(item, str) and re.fullmatch('sha256:[0-9a-f]{64}', item), 'EPISODE_EXPORT_ROUTE_DIGEST_SHAPE')
    require(all(scope[key] == route[key] for key in ('controller_id', 'route_transaction_id', 'obligation_id')) and
        scope['host_id'] == 'codex' and scope['host_session_id'] == episode['parent_identity']['thread_id'] and
        all(isinstance(scope[key], str) and re.fullmatch('G[0-9A-F]{4}', scope[key])
            for key in ('host_binding_generation', 'continuity_generation')) and
        isinstance(scope['claim_id'], str) and re.fullmatch('[0-9a-f]{32}', scope['claim_id']),
        'EPISODE_EXPORT_ROUTE_SCOPE_BINDING')
    receipt_prefix = 'refs/implementaudit/continuity-receipts/' + scope['controller_id'] + '/' + scope['continuity_generation'] + '@'
    require(isinstance(scope['continuity_receipt'], str) and
        re.fullmatch(re.escape(receipt_prefix) + '[0-9a-f]{40}(?:[0-9a-f]{24})?', scope['continuity_receipt']),
        'EPISODE_EXPORT_CONTINUITY_RECEIPT_BINDING')
    _episode_export_path(scope['explicit_run_root'])


def _episode_export_code_pins(pins):
    required = {'implementaudit/SKILL.md', 'audit-state/SKILL.md',
        'implementaudit/references/child-agents.md', 'implementaudit/references/continuity.md'}
    required.update('implementaudit/scripts/' + name for name in (
        'compaction-audit-pending.py', 'compaction-result-observation.py',
        'compaction-source-owner-codex-app.py', 'codex-recovery-native-reader.py',
        'bounded_file_custody.py', 'bounded_native_reader.py', 'bounded_source_owner.py',
        'host-session-binding.py', 'route-transaction.py'))
    require(type(pins) is dict and len(pins) == len(required) and
        all(type(key) is str and 0 < len(key) <= 256 and type(item) is str and
            re.fullmatch('[0-9a-f]{64}', item) for key, item in pins.items()),
        'EPISODE_EXPORT_CODE_PIN_SHAPE')
    normalized = {key.replace('\\', '/') for key in pins}
    require(normalized == required and len(normalized) == len(pins), 'EPISODE_EXPORT_CODE_PIN_POPULATION')


def validate_frozen_episode_export_v1(value):
    """Validate a captured projection only. No filesystem, native RPC or refresh.

    This function does not authenticate caller-authored facts. The collector
    must separately pin this owner and the fixed producer acquisition path.
    """
    closed(value, ('schema', 'status', 'reason_code', 'owner', 'episode', 'pending', 'lifecycle', 'occurrences', 'custody', 'export_digest', 'authority_ceiling'), 'EPISODE_EXPORT_SHAPE')
    require(len(canonical(value)) <= MAX_TOTAL and value['schema'] == 'implementaudit.native-episode-export.v1' and (value['authority_ceiling'] == 'NONE') and (value['status'] in ('AVAILABLE', 'UNAVAILABLE')), 'EPISODE_EXPORT_BOUND')
    require(value['export_digest'] == digest(canonical({key: item for key, item in value.items() if key != 'export_digest'})), 'EPISODE_EXPORT_DIGEST')
    if value['status'] == 'UNAVAILABLE':
        require(value['reason_code'] in ('FIXED_SELECTION_UNBOUND', 'CANONICAL_EPISODE_ABSENT', 'PENDING_STATE_ABSENT', 'SELECTED_ASSIGNMENT_ABSENT', 'ADMITTED_JOIN_ABSENT') and all((value[key] is None for key in ('owner', 'episode', 'pending', 'lifecycle', 'occurrences', 'custody'))), 'EPISODE_EXPORT_ABSENCE_SHAPE')
        return value
    require(value['reason_code'] is None, 'EPISODE_EXPORT_PRESENT_REASON')
    owner = closed(value['owner'], ('profile_id', 'issuer_id', 'policy_digest', 'code_pins', 'canonical_opening_digest', 'canonical_route', 'host_and_scope'), 'EPISODE_EXPORT_OWNER_SHAPE')
    require(owner['profile_id'] == NONPROTECTED_PROFILE and owner['issuer_id'] == 'codex-app-canonical-episode-public-source-v1', 'EPISODE_EXPORT_OWNER_BINDING')
    _episode_export_code_pins(owner['code_pins'])
    episode = closed(value['episode'], ('parent_identity', 'actual_child_identity', 'assignment_identity', 'obligation_digest', 'observation_id', 'covered_boundary_versions', 'result_digest', 'acceptance_digest', 'Q_digest', 'E_digest'), 'EPISODE_EXPORT_EPISODE_SHAPE')
    parent = closed(episode['parent_identity'], ('thread_id', 'agent_path'), 'EPISODE_EXPORT_PARENT_SHAPE')
    child = closed(episode['actual_child_identity'], ('thread_id', 'parent_thread_id', 'agent_path'), 'EPISODE_EXPORT_CHILD_SHAPE')
    require(all((isinstance(item, str) and 0 < len(item) <= 256 for item in (*parent.values(), *child.values()))) and child['parent_thread_id'] == parent['thread_id'] and (child['thread_id'] != parent['thread_id']) and child['agent_path'].startswith(parent['agent_path'] + '/'), 'EPISODE_EXPORT_PARENT_CHILD_BINDING')
    _episode_export_route_binding(owner, episode)
    require(isinstance(owner['canonical_opening_digest'], str) and re.fullmatch('sha256:[0-9a-f]{64}', owner['canonical_opening_digest']), 'EPISODE_EXPORT_CANONICAL_OPENING_DIGEST')
    for item in (owner['policy_digest'], *(episode[key] for key in ('assignment_identity', 'obligation_digest', 'observation_id', 'result_digest', 'acceptance_digest', 'Q_digest', 'E_digest'))):
        require(isinstance(item, str) and re.fullmatch('[0-9a-f]{64}', item), 'EPISODE_EXPORT_DIGEST_SHAPE')
    _episode_export_scope(episode['covered_boundary_versions'])
    require(episode['covered_boundary_versions'] and all((row['kind'] == 'COMPLETED_RESUMED_BOUNDARY' for row in episode['covered_boundary_versions'])), 'EPISODE_EXPORT_REAL_BOUNDARY_REQUIRED')
    pending = closed(value['pending'], ('revision', 'observations', 'assignment_scope', 'covered_scope', 'pending_scope'), 'EPISODE_EXPORT_PENDING_SHAPE')
    require(type(pending['revision']) is int and pending['revision'] >= 0 and isinstance(pending['observations'], list) and (len(pending['observations']) <= 4096), 'EPISODE_EXPORT_PENDING_BOUND')
    for field in ('assignment_scope', 'covered_scope', 'pending_scope'):
        _episode_export_scope(pending[field])
    require(pending['covered_scope'] == episode['covered_boundary_versions'] and all((row in pending['assignment_scope'] for row in pending['covered_scope'])), 'EPISODE_EXPORT_COVERAGE_BINDING')
    observations = {}
    for row in pending['observations']:
        closed(row, ('id', 'kind', 'version', 'consumed_version', 'assignment_children'), 'EPISODE_EXPORT_PENDING_ROW_SHAPE')
        _episode_export_scope([{key: row[key] for key in ('id', 'kind', 'version')}])
        require(row['id'] not in observations and type(row['consumed_version']) is int and (0 <= row['consumed_version'] <= row['version']) and isinstance(row['assignment_children'], list) and (len(row['assignment_children']) <= 64) and (len(set(row['assignment_children'])) == len(row['assignment_children'])) and all((isinstance(item, str) and item for item in row['assignment_children'])), 'EPISODE_EXPORT_PENDING_ROW_BINDING')
        observations[row['id']] = row
    require(all(row['id'] in observations and observations[row['id']]['kind'] == row['kind'] and
        observations[row['id']]['version'] >= row['version'] for row in pending['assignment_scope']),
        'EPISODE_EXPORT_ASSIGNED_OBSERVATION_BINDING')
    require(pending['pending_scope'] == [{key: row[key] for key in ('id', 'version', 'kind')} for row in pending['observations'] if row['version'] > row['consumed_version']] and all((row['id'] in observations and observations[row['id']]['consumed_version'] >= row['version'] for row in pending['covered_scope'])), 'EPISODE_EXPORT_CONSUMPTION_BINDING')
    lifecycle = closed(value['lifecycle'], ('result', 'acceptance', 'join', 'h0', 'source_terminal_release'), 'EPISODE_EXPORT_LIFECYCLE_SHAPE')
    require(lifecycle['result'] == {'status': 'SUCCEEDED', 'return_digest': episode['result_digest']} and lifecycle['acceptance'] == {'status': 'ACCEPTED_EXACT_RESULT', 'digest': episode['acceptance_digest']} and (lifecycle['join'] == {'status': 'JOINED_EVIDENCE_ONLY', 'covered': episode['covered_boundary_versions'], 'pending_consumed': True}), 'EPISODE_EXPORT_RESULT_ACCEPTANCE_JOIN_BINDING')
    h0 = closed(lifecycle['h0'], ('status', 'stage_receipts'), 'EPISODE_EXPORT_H0_SHAPE')
    require(h0['status'] in ('NOT_RECORDED', 'RECORDED') and isinstance(h0['stage_receipts'], dict) and (set(h0['stage_receipts']) == (set() if h0['status'] == 'NOT_RECORDED' else {'LOAD', 'USE', 'DISPOSE'})) and all((isinstance(item, str) and re.fullmatch('sha256:[0-9a-f]{64}', item) for item in h0['stage_receipts'].values())) and (len(set(h0['stage_receipts'].values())) == len(h0['stage_receipts'])), 'EPISODE_EXPORT_H0_BINDING')
    release = closed(lifecycle['source_terminal_release'], ('status', 'digest'), 'EPISODE_EXPORT_RELEASE_SHAPE')
    require(release['status'] == 'SOURCE_OWNER_VALIDATED' and isinstance(release['digest'], str) and re.fullmatch('[0-9a-f]{64}', release['digest']), 'EPISODE_EXPORT_RELEASE_BINDING')
    occurrences = closed(value['occurrences'], ('schema', 'observation_id', 'actual_child_identity', 'covered_boundary_versions', 'source_cutoff', 'occurrences', 'authority_ceiling'), 'EPISODE_EXPORT_OCCURRENCES_SHAPE')
    require(occurrences['schema'] == 'implementaudit.compaction-selected-occurrences.v1' and occurrences['observation_id'] == episode['observation_id'] and (occurrences['actual_child_identity'] == child) and (occurrences['covered_boundary_versions'] == episode['covered_boundary_versions']) and (occurrences['authority_ceiling'] == 'NONE') and isinstance(occurrences['occurrences'], list) and (3 <= len(occurrences['occurrences']) <= 256), 'EPISODE_EXPORT_OCCURRENCES_BINDING')
    for row in occurrences['occurrences']:
        closed(row, ('population', 'attempt_class', 'semantic', 'observation_id', 'completion', 'records'), 'EPISODE_EXPORT_OCCURRENCE_SHAPE')
        require((row['population'], row['attempt_class'], row['semantic']) in {('CURRENT', 'ORIGINAL', semantic) for semantic in ('LOAD', 'EXCHANGE', 'BIND')} | {('PRIOR', 'ORIGINAL', semantic) for semantic in ('LOAD', 'EXCHANGE', 'BIND')} | {('PRIOR', 'RETRY', 'BIND')} and row['completion'] == 'COMPLETED' and isinstance(row['observation_id'], str) and re.fullmatch('[0-9a-f]{64}', row['observation_id']), 'EPISODE_EXPORT_OCCURRENCE_CLASSIFICATION')
        closed(row['records'], ('call', 'result'), 'EPISODE_EXPORT_OCCURRENCE_PAIR')
        require(all((isinstance(row['records'][part], dict) and row['records'][part] for part in ('call', 'result'))), 'EPISODE_EXPORT_OCCURRENCE_COMPLETION')
        for pin in row['records'].values():
            closed(pin, ('path', 'physical', 'role', 'locator', 'timestamp', 'message_or_call_id'), 'EPISODE_EXPORT_RECORD_PIN_SHAPE')
            locator = closed(pin['locator'], ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'), 'EPISODE_EXPORT_RECORD_LOCATOR_SHAPE')
            physical = closed(pin['physical'], ('device', 'inode'), 'EPISODE_EXPORT_RECORD_PHYSICAL_SHAPE')
            require(pin['role'] == 'child' and isinstance(pin['path'], str) and (0 < len(pin['path']) <= 4096) and all((type(item) is int and item >= 0 for item in physical.values())) and (type(locator['offset']) is int) and (locator['offset'] >= 0) and (type(locator['bytes']) is int) and (0 < locator['bytes'] <= 256 * 1024) and (type(locator['embedded_ordinal']) is int) and (locator['embedded_ordinal'] >= 1) and (locator['physical_line'] is None or (type(locator['physical_line']) is int and locator['physical_line'] >= 1)) and isinstance(locator['sha256'], str) and re.fullmatch('[0-9a-f]{64}', locator['sha256']) and all((isinstance(pin[key], str) and pin[key] for key in ('timestamp', 'message_or_call_id'))), 'EPISODE_EXPORT_RECORD_PIN_BINDING')
        before(row['records']['call'], row['records']['result'])
    require({row['semantic'] for row in occurrences['occurrences'] if row['population'] == 'CURRENT'} == {'LOAD', 'EXCHANGE', 'BIND'} and all((row['observation_id'] == episode['observation_id'] for row in occurrences['occurrences'] if row['population'] == 'CURRENT')), 'EPISODE_EXPORT_CURRENT_OCCURRENCES')
    custody = closed(value['custody'], ('candidate', 'qualification', 'episode', 'attestation', 'source_cutoffs'), 'EPISODE_EXPORT_CUSTODY_SHAPE')
    for key in ('candidate', 'qualification', 'episode', 'attestation'):
        _episode_export_pin(custody[key])
    require(custody['qualification']['sha256'] == episode['Q_digest'] and custody['episode']['sha256'] == episode['E_digest'], 'EPISODE_EXPORT_CUSTODY_BINDING')
    cuts = closed(custody['source_cutoffs'], ('parent', 'child', 'compaction_cutoff', 'hold_history'), 'EPISODE_EXPORT_CUTOFF_SHAPE')
    parent_limit = _episode_export_source(cuts['parent'], 'parent', episode, owner['canonical_opening_digest'])
    child_limit = _episode_export_source(cuts['child'], 'child', episode, owner['canonical_opening_digest'])
    require(cuts['parent']['path'] != cuts['child']['path'] and cuts['parent']['physical'] != cuts['child']['physical'], 'EPISODE_EXPORT_SOURCE_PHYSICAL_ALIAS')
    compact = closed(cuts['compaction_cutoff'], ('path', 'task_id', 'session_id', 'sessions_root', 'physical', 'session_meta_sha256', 'prefix_bytes', 'prefix_sha256', 'provenance', 'native_producer_runtime_equivalence'), 'EPISODE_EXPORT_COMPACTION_CUTOFF_SHAPE')
    _episode_export_path(compact['sessions_root'])
    _episode_export_physical(compact['physical'])
    root = compact['sessions_root'].replace('\\', '/').rstrip('/') + '/'
    require(compact['path'] == cuts['parent']['path'] and compact['physical'] == cuts['parent']['physical'] and (compact['task_id'] == compact['session_id'] == parent['thread_id']) and all((cuts[role]['path'].replace('\\', '/').startswith(root) for role in ('parent', 'child'))) and (compact['session_meta_sha256'] == cuts['parent']['metadata']['sha256']) and (type(compact['prefix_bytes']) is int) and (cuts['parent']['metadata']['bytes'] <= compact['prefix_bytes'] <= parent_limit) and isinstance(compact['prefix_sha256'], str) and re.fullmatch('[0-9a-f]{64}', compact['prefix_sha256']) and (compact['provenance'] == 'HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX') and (compact['native_producer_runtime_equivalence'] == 'UNVERIFIED'), 'EPISODE_EXPORT_COMPACTION_CUTOFF_BINDING')
    held = closed(cuts['hold_history'], ('path', 'physical', 'prefix_bytes', 'prefix_sha256', 'physical_records', 'history_start_ordinal', 'host_producer_authenticated', 'original_bind'), 'EPISODE_EXPORT_HOLD_CUTOFF_SHAPE')
    _episode_export_physical(held['physical'])
    require(held == occurrences['source_cutoff'] and held['path'] == cuts['child']['path'] and (held['physical'] == cuts['child']['physical']) and (type(held['prefix_bytes']) is int) and (cuts['child']['metadata']['bytes'] < held['prefix_bytes'] <= min(MAX_TOTAL, child_limit)) and isinstance(held['prefix_sha256'], str) and re.fullmatch('[0-9a-f]{64}', held['prefix_sha256']) and (type(held['physical_records']) is int) and (held['physical_records'] >= 2) and (held['history_start_ordinal'] == 1) and (held['host_producer_authenticated'] is False), 'EPISODE_EXPORT_FIXED_CUTOFF_BINDING')
    current_rows = [row for row in occurrences['occurrences'] if row['population'] == 'CURRENT']
    require(len(current_rows) == 3 and held['original_bind'] == next((row['records'] for row in current_rows if row['semantic'] == 'BIND')), 'EPISODE_EXPORT_ORIGINAL_BIND_CUTOFF')
    offsets = set()
    ordered_records = []
    for row in occurrences['occurrences']:
        for pin in row['records'].values():
            locator = pin['locator']
            require(pin['path'] == held['path'] and pin['physical'] == held['physical'] and (cuts['child']['metadata']['bytes'] <= locator['offset']) and (locator['offset'] + locator['bytes'] <= held['prefix_bytes']) and (locator['embedded_ordinal'] < held['physical_records']) and (locator['physical_line'] in (None, locator['embedded_ordinal'] + 1)) and (locator['offset'] not in offsets), 'EPISODE_EXPORT_OCCURRENCE_SOURCE_RANGE_OR_IDENTITY')
            offsets.add(locator['offset'])
            ordered_records.append(pin)
    ordered_records.sort(key=lambda pin: pin['locator']['offset'])
    for prior, current in zip(ordered_records, ordered_records[1:]):
        before(prior, current)
        require(prior['locator']['embedded_ordinal'] < current['locator']['embedded_ordinal'],
            'EPISODE_EXPORT_RECORD_ORDINAL_ORDER')
    return value
