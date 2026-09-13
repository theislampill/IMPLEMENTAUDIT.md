#!/usr/bin/env python3
"""Bounded physical observation primitives for the compaction result consumer.

Locators and physical file identity are observations, never host authentication.
Semantic/profile selection belongs to the source-owned consumer, not the caller.
"""
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
        require(not component.is_symlink() and not (getattr(info, 'st_file_attributes', 0) & 0x400), 'SOURCE_REPARSE')
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'SOURCE_FILE_KIND')
    return path, info


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def closed(value, keys, reason):
    require(isinstance(value, dict) and set(value) == set(keys), reason)
    return value


def public_message(row, phase='commentary'):
    payload = row['payload']
    require(row['type'] == 'response_item' and 'metadata' not in row and payload.get('type') == 'message' and
            payload.get('role') == 'assistant' and payload.get('phase') == phase and
            isinstance(payload.get('id'), str) and payload['id'], 'ACTUAL_ASSISTANT_ROLE_OR_PHASE')
    content = payload.get('content')
    require(isinstance(content, list) and len(content) == 1 and
            set(content[0]) == {'type', 'text'} and content[0]['type'] == 'output_text' and
            isinstance(content[0]['text'], str), 'ACTUAL_PUBLIC_TEXT_SHAPE')
    return content[0]['text']


def visible(row, expected):
    text = public_message(row)
    require(text.startswith('```ini\n') and '\n```' in text, 'VISIBLE_PRE_USE_BLOCK_ABSENT')
    block = text[len('```ini\n'):text.index('\n```')]
    pairs = []
    for line in block.splitlines():
        require('=' in line and not line.startswith((' ', '>')), 'VISIBLE_PRE_USE_FIELD_SHAPE')
        pairs.append(line.split('=', 1))
    fields = unique(pairs)
    require(all(fields.get(key) == value for key, value in expected.items()), 'VISIBLE_PRE_USE_MEANING')


def typed_message(row, keys, schema, action=None, phase='commentary'):
    text = public_message(row, phase)
    require(text.startswith('```json\n') and text.endswith('\n```'), 'TYPED_PUBLIC_RECORD_BLOCK')
    value = json.loads(text[len('```json\n'):-len('\n```')], object_pairs_hook=unique)
    closed(value, keys, 'TYPED_PUBLIC_RECORD_FIELDS')
    require(value['schema'] == schema and value.get('authority_ceiling') == 'NONE' and
            (action is None or value.get('action') == action), 'TYPED_PUBLIC_RECORD_MEANING')
    return value


def before(first, second):
    require(datetime.fromisoformat(first['timestamp'].replace('Z', '+00:00')) <
            datetime.fromisoformat(second['timestamp'].replace('Z', '+00:00')), 'OBSERVATION_ORDER')
    if first['path'] == second['path']:
        require(first['locator']['offset'] + first['locator']['bytes'] <= second['locator']['offset'], 'SOURCE_RECORD_ORDER')


def resolve_record(context, role, locator):
    source = context[role]
    observed = read_records(source['path'], [source['metadata'], locator], source['allowed_ranges'], source['physical'])
    meta, selected = observed['records']
    require(meta['row']['type'] == 'session_meta' and digest(canonical(meta['row']['payload'])) == source['metadata_payload_digest'],
            'SOURCE_METADATA_CHANGED')
    require(role != 'child' or selected['row']['ordinal'] >= source['history_start_ordinal'], 'INHERITED_CHILD_RECORD')
    row = selected['row']
    return row, {'path': source['path'], 'physical': source['physical'], 'role': role,
        'locator': dict(locator), 'timestamp': row['timestamp'], 'message_or_call_id': row['payload'].get('id', row['payload'].get('call_id'))}


def bind_sources(request, parent_session, child_id):
    closed(request, ('parent', 'child', 'open', 'spawn_call', 'spawn_output'), 'OBSERVATION_SOURCE_CONTEXT_SHAPE')
    home = os.environ.get('CODEX_HOME')
    require(home and Path(home).is_absolute(), 'HOST_SOURCE_ROOT_ABSENT')
    sessions = (Path(home) / 'sessions').resolve(strict=True)
    result = {}; metadata = {}
    for role in ('parent', 'child'):
        source = request[role]
        closed(source, ('path', 'metadata', 'allowed_ranges'), 'HOST_SOURCE_SELECTION_SHAPE')
        path, _ = physical(source['path'])
        require(path.is_relative_to(sessions), 'HOST_SOURCE_OUTSIDE_SESSION_STORE')
        observed = read_records(path, [source['metadata']], source['allowed_ranges'])
        row = observed['records'][0]['row']; meta = row['payload']
        require(source['metadata']['offset'] == 0 and row['type'] == 'session_meta' and
                meta.get('originator') == 'Codex Desktop' and meta.get('cli_version') == '0.153.4' and
                isinstance(meta.get('id'), str) and path.name.startswith('rollout-') and
                path.name.endswith(meta['id'] + '.jsonl'), 'UNSUPPORTED_HOST_SOURCE_PROFILE')
        result[role] = {**source, 'path': str(path), 'physical': observed['physical'],
            'metadata_payload_digest': digest(canonical(meta)),
            'history_start_ordinal': meta.get('subagent_history_start_ordinal', 0)}
        metadata[role] = meta
    parent = metadata['parent']; child = metadata['child']
    relation = child.get('source', {}).get('subagent', {}).get('thread_spawn', {}) if isinstance(child.get('source'), dict) else {}
    require(parent.get('id') == parent_session and parent.get('session_id') == parent_session and
            parent.get('thread_source') == 'user' and parent.get('source') == 'vscode', 'FOREIGN_ROOT_SOURCE')
    require(child.get('id') == child_id and child_id != parent_session and child.get('session_id') == parent_session and
            child.get('thread_source') == 'subagent' and child.get('parent_thread_id') == parent_session and
            child.get('forked_from_id') == parent_session and relation.get('parent_thread_id') == parent_session and
            child.get('agent_path') == relation.get('agent_path') and
            isinstance(child.get('agent_path'), str) and child['agent_path'].startswith('/root/') and
            type(child.get('subagent_history_start_ordinal')) is int, 'FOREIGN_ACTUAL_CHILD_SOURCE')
    result['parent_identity'] = {'thread_id': parent_session, 'agent_path': '/root'}
    result['actual_child_identity'] = {'thread_id': child_id, 'parent_thread_id': parent_session, 'agent_path': child['agent_path']}
    opened, open_pin = resolve_record(result, 'parent', request['open'])
    spawn, spawn_pin = resolve_record(result, 'parent', request['spawn_call'])
    response, response_pin = resolve_record(result, 'parent', request['spawn_output'])
    call = spawn['payload']; output = response['payload']
    require(spawn['type'] == response['type'] == 'response_item' and call.get('type') == 'function_call' and
            call.get('namespace') == 'collaboration' and call.get('name') == 'spawn_agent' and
            output.get('type') == 'function_call_output' and output.get('call_id') == call.get('call_id') and
            isinstance(call.get('call_id'), str), 'ACTUAL_SPAWN_CALL_OUTPUT_ASSOCIATION')
    args = json.loads(call['arguments'], object_pairs_hook=unique)
    outcome = json.loads(output['output'], object_pairs_hook=unique)
    require(args.get('task_name') == child['agent_path'].removeprefix('/root/') and
            outcome == {'task_name': child['agent_path']}, 'ACTUAL_SPAWN_CHILD_IDENTITY')
    visible(opened, {'CHILD_TASK': args['task_name'], 'CHILD_SKILL_SELECTED': 'audit-state', 'STATUS': 'OPEN', 'LOAD': 'UNVERIFIED'})
    before(open_pin, spawn_pin); before(spawn_pin, response_pin)
    result.update(open=open_pin, spawn_call=spawn_pin, spawn_output=response_pin,
        profile_id=PROFILE, host_producer_authenticated=False)
    return result


def shell_literal(text):
    return "'" + str(text).replace("'", "''") + "'"


def tool_input(command):
    return 'const r = await tools.exec_command(' + json.dumps({'cmd': command, 'max_output_tokens': 24000}, separators=(',', ':')) + ');text(r);'


def load_tool_input(skill_pin):
    command = "$p = " + shell_literal(skill_pin['path']) + "\n$b = [IO.File]::ReadAllBytes($p)\n"
    command += "[PSCustomObject]@{path=$p;bytes=$b.Length;sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant();utf8=[Text.Encoding]::UTF8.GetString($b)} | ConvertTo-Json -Compress"
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
    require(type(pin['bytes']) is int and 0 < pin['bytes'] <= maximum and
            isinstance(pin['sha256'], str) and re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'ARTIFACT_PIN_BOUND')
    path, before_stat = physical(pin['path'])
    require(before_stat.st_size == pin['bytes'], 'ARTIFACT_BYTE_COUNT')
    return path, before_stat


def artifact(pin, maximum=1024 * 1024, admitted=None):
    path, before_stat = artifact_preflight(pin, maximum)
    if admitted is not None:
        admitted_path, admitted_stat = admitted
        require(path == admitted_path and identity(before_stat) == identity(admitted_stat) and
                (before_stat.st_size, before_stat.st_mtime_ns) ==
                (admitted_stat.st_size, admitted_stat.st_mtime_ns), 'ARTIFACT_ADMISSION_CHANGED')
    with open(path, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        require(identity(opened) == identity(before_stat) and opened.st_nlink == 1 and
                stat.S_ISREG(opened.st_mode) and
                (opened.st_size, opened.st_mtime_ns) == (before_stat.st_size, before_stat.st_mtime_ns),
                'ARTIFACT_PHYSICAL_CHANGED')
        raw = stream.read(pin['bytes'])
    _, after_stat = physical(path)
    require(identity(before_stat) == identity(after_stat) and
            (before_stat.st_size, before_stat.st_mtime_ns) == (after_stat.st_size, after_stat.st_mtime_ns) and
            len(raw) == pin['bytes'] and digest(raw) == pin['sha256'], 'ARTIFACT_PIN_CHANGED')
    return raw, identity(before_stat)


def command_response(context, role, call_locator, result_locator, expected_input):
    call_row, call_pin = resolve_record(context, role, call_locator)
    output_row, output_pin = resolve_record(context, role, result_locator)
    call = call_row['payload']; output = output_row['payload']
    require(call_row['type'] == output_row['type'] == 'response_item' and
            call.get('type') == 'custom_tool_call' and call.get('name') == 'exec' and
            call.get('input') == expected_input and call.get('status') == 'completed' and
            isinstance(call.get('call_id'), str) and output.get('type') == 'custom_tool_call_output' and
            output.get('call_id') == call['call_id'], 'ACTUAL_HOST_CALL_RESULT_ASSOCIATION')
    content = output.get('output')
    require(isinstance(content, list) and len(content) == 2 and
            all(isinstance(block, dict) and set(block) == {'type', 'text'} and block['type'] == 'input_text'
                and isinstance(block['text'], str) for block in content), 'FULL_HOST_OUTPUT_SHAPE')
    nested = json.loads(content[1]['text'], object_pairs_hook=unique)
    require(isinstance(nested, dict) and set(nested) == {'chunk_id', 'wall_time_seconds', 'exit_code', 'original_token_count', 'output'} and
            type(nested['exit_code']) is int and nested['exit_code'] == 0 and
            isinstance(nested['output'], str), 'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED')
    before(call_pin, output_pin)
    return nested['output'], {'call': call_pin, 'result': output_pin}


def authorization(context, prepared, evidence, skill_pin):
    closed(evidence, ('load_call', 'load_output', 'route', 'authorization'), 'AUTHORIZATION_EVIDENCE_SHAPE')
    loaded_text, load_identity = command_response(context, 'child', evidence['load_call'], evidence['load_output'], load_tool_input(skill_pin))
    loaded = json.loads(loaded_text, object_pairs_hook=unique)
    closed(loaded, ('path', 'bytes', 'sha256', 'utf8'), 'FULL_LOAD_CONTENT_SHAPE')
    skill_raw, _ = artifact(skill_pin)
    require({key: loaded[key] for key in ('path', 'bytes', 'sha256')} == skill_pin and
            loaded['utf8'].encode('utf-8') == skill_raw, 'ACTUAL_FULL_SKILL_LOAD_DIFFERS')
    before(context['spawn_output'], load_identity['call'])
    route_row, route_pin = resolve_record(context, 'parent', evidence['route'])
    task = context['actual_child_identity']['agent_path'].removeprefix('/root/')
    visible(route_row, {'CHILD_TASK': task, 'CHILD_SKILL_ROUTE': 'audit-state', 'LOAD': 'VERIFIED'})
    row, record_pin = resolve_record(context, 'parent', evidence['authorization'])
    value = typed_message(row, ('schema', 'action', 'parent_identity', 'actual_child_identity', 'obligation_digest',
        'observation_id', 'load_observation_identity', 'selected_child', 'skill_source_pin', 'authority_ceiling'),
        'implementaudit.compaction-use-authorization.v1', 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION')
    obligation = prepared['obligation']
    expected = {'schema': 'implementaudit.compaction-use-authorization.v1',
        'action': 'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION', 'parent_identity': obligation['parent_identity'],
        'actual_child_identity': obligation['actual_child_identity'], 'obligation_digest': prepared['obligation_pin']['sha256'],
        'observation_id': obligation['observation_id'], 'load_observation_identity': digest(canonical(load_identity)),
        'selected_child': 'audit-state', 'skill_source_pin': skill_pin, 'authority_ceiling': 'NONE'}
    require(value == expected, 'AUTHORIZATION_EXACT_OBLIGATION_OR_LOAD_IDENTITY')
    before(load_identity['result'], route_pin); before(route_pin, record_pin)
    return {'value': value, 'text': public_message(row), 'record': record_pin,
            'load_identity': load_identity, 'route_record': route_pin, 'evidence': evidence}


def delivery_packet(prepared, validated):
    raw, _ = artifact(prepared['obligation_pin'])
    require(json.loads(raw, object_pairs_hook=unique) == prepared['obligation'], 'IMMUTABLE_OBLIGATION_CHANGED')
    return {'schema': 'implementaudit.compaction-obligation-delivery.v1',
        'observation_id': prepared['obligation']['observation_id'], 'obligation_pin': prepared['obligation_pin'],
        'obligation_utf8': raw.decode('utf-8'), 'authorization_record': validated['record'],
        'authorization_utf8': validated['text'], 'authority_ceiling': 'NONE', 'host_producer_authenticated': False}


def completed_exchange(context, prepared, request, store, session, owner, skill_pin):
    closed(request, ('call', 'result'), 'CHILD_EXCHANGE_LOCATOR_SHAPE')
    require(prepared['authorization'] is not None and prepared.get('delivery_request') is not None, 'OBLIGATION_NOT_DELIVERED')
    validated = authorization(context, prepared, prepared['authorization']['evidence'], skill_pin)
    require(validated == prepared['authorization'], 'PUBLIC_AUTHORIZATION_CHANGED')
    text, identity = command_response(context, 'child', request['call'], request['result'],
        delivery_tool_input(store, session, owner, prepared['delivery_request']))
    packet = json.loads(text, object_pairs_hook=unique)
    require(packet == delivery_packet(prepared, validated), 'ACTUAL_FULL_OBLIGATION_AUTHORIZATION_RESPONSE_DIFFERS')
    before(validated['record'], identity['call'])
    return {'identity': digest(canonical(identity)), 'records': identity, 'evidence': request}


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
    require(not discovering or cutoff is None and prior is not None, 'HOLD_COMPLETION_DISCOVERY_SHAPE')
    end = min(initial.st_size, MAX_TOTAL) if discovering else initial.st_size if cutoff is None else cutoff
    require(type(end) is int and 0 < end <= MAX_TOTAL and end <= initial.st_size, 'HOLD_PREFIX_BYTE_BOUND')
    windows = source['allowed_ranges']
    require(isinstance(windows, list) and 0 < len(windows) <= MAX_RECORDS, 'HOLD_ALLOWED_RANGE_BOUND')
    for window in windows:
        closed(window, ('offset', 'bytes'), 'HOLD_ALLOWED_RANGE_SHAPE')
        require(type(window['offset']) is int and window['offset'] >= 0 and
                type(window['bytes']) is int and 0 < window['bytes'] <= MAX_TOTAL, 'HOLD_ALLOWED_RANGE_BOUND')
    covered = 0
    for window in sorted(windows, key=lambda value: value['offset']):
        if window['offset'] > covered:
            break
        covered = max(covered, window['offset'] + window['bytes'])
    if discovering:
        # The original response, not settled later traffic, determines the end.
        # Discovery can only read within the already allowed contiguous budget.
        end = min(end, covered)
        require(end > 0, 'HOLD_CONTIGUOUS_RANGE_REQUIRED')
    else:
        require(covered >= end, 'HOLD_CONTIGUOUS_RANGE_REQUIRED')
    if prior is not None:
        require(prior['path'] == str(path) and prior['physical'] == source['physical'] and
                type(prior['prefix_bytes']) is int and 0 < prior['prefix_bytes'] <= end and
                isinstance(prior['prefix_sha256'], str) and re.fullmatch('[0-9a-f]{64}', prior['prefix_sha256']),
                'HOLD_PRIOR_PREFIX_BOUND')
    if discovering:
        closed(until_call, ('path', 'physical', 'locator', 'call_id'), 'HOLD_ORIGINAL_CALL_SHAPE')
        original = closed(until_call['locator'], ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'),
                          'HOLD_ORIGINAL_CALL_LOCATOR_SHAPE')
        require(until_call['path'] == str(path) and until_call['physical'] == source['physical'] and
                isinstance(until_call['call_id'], str) and until_call['call_id'] and
                type(original['offset']) is int and original['offset'] >= 0 and
                type(original['bytes']) is int and 0 < original['bytes'] <= MAX_RECORD and
                original['offset'] + original['bytes'] <= prior['prefix_bytes'] and
                type(original['embedded_ordinal']) is int and original['embedded_ordinal'] >= source['history_start_ordinal'] and
                isinstance(original['sha256'], str) and re.fullmatch('[0-9a-f]{64}', original['sha256']) and
                (original['physical_line'] is None or type(original['physical_line']) is int and original['physical_line'] > 0),
                'HOLD_ORIGINAL_CALL_OUTSIDE_ENTRY')
    # Complete range/identity/byte ceilings are established before content I/O.
    wires = []; records = []; position = 0; previous_ordinal = None
    activation_seen = False; original_seen = False
    with open(path, 'rb') as stream:
        require(identity(os.fstat(stream.fileno())) == identity(initial), 'HOLD_SOURCE_CHANGED_BEFORE_READ')
        while position < end:
            require(len(records) < MAX_RECORDS, 'HOLD_RECORD_COUNT_BOUND')
            # Never read beyond the predeclared prefix or an unbounded record.
            wire = stream.readline(min(MAX_RECORD, end - position))
            require(0 < len(wire) <= MAX_RECORD and wire.endswith(b'\n') and
                    wire.count(b'\n') == 1 and b'\r' not in wire and b'\x00' not in wire,
                    'HOLD_PARTIAL_OR_OVERFLOW_FRAME')
            row = json.loads(wire.decode('utf-8'), object_pairs_hook=unique)
            require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'},
                    {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and
                    type(row.get('ordinal')) is int and row['ordinal'] >= 0 and
                    isinstance(row.get('timestamp'), str) and isinstance(row.get('type'), str) and
                    isinstance(row.get('payload'), dict), 'HOLD_RECORD_SHAPE')
            locator = {'offset': position, 'bytes': len(wire), 'sha256': digest(wire),
                'embedded_ordinal': row['ordinal'], 'physical_line': len(records) + 1}
            if not records:
                meta = source['metadata']
                require(row['type'] == 'session_meta' and all(locator[k] == meta[k] for k in
                        ('offset', 'bytes', 'sha256', 'embedded_ordinal')) and
                        digest(canonical(row['payload'])) == source['metadata_payload_digest'], 'HOLD_METADATA_CHANGED')
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
                require(all(locator[key] == original[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal')) and
                        (original['physical_line'] is None or locator['physical_line'] == original['physical_line']) and
                        row['type'] == 'response_item' and row['payload'].get('type') == 'custom_tool_call' and
                        row['payload'].get('name') == 'exec' and row['payload'].get('call_id') == until_call['call_id'],
                        'HOLD_ORIGINAL_CALL_DIFFERS')
                original_seen = True
            elif discovering and position > original['offset']:
                require(original_seen, 'HOLD_ORIGINAL_CALL_NOT_COVERED')
            records.append({'row': row, 'locator': locator})
            wires.append(wire); position += len(wire)
            # Inherited same-ID outputs are physical coverage, not this active
            # call's completion. Only its exact preceding occurrence enables it.
            if discovering and original_seen and row['type'] == 'response_item' and row['payload'].get('type') == 'custom_tool_call_output' and row['payload'].get('call_id') == until_call['call_id']:
                break
        final = os.fstat(stream.fileno())
    _, current = physical(path)
    require(identity(initial) == identity(final) == identity(current) and
            (initial.st_size, initial.st_mtime_ns) == (final.st_size, final.st_mtime_ns) ==
            (current.st_size, current.st_mtime_ns), 'HOLD_SOURCE_CHANGED_DURING_READ')
    require(activation_seen, 'HOLD_ACTIVATION_COVERAGE_MISSING')
    require(not discovering or original_seen, 'HOLD_ORIGINAL_CALL_NOT_COVERED')
    raw = b''.join(wires)
    if prior is not None:
        require(digest(raw[:prior['prefix_bytes']]) == prior['prefix_sha256'], 'HOLD_PRIOR_PREFIX_CHANGED')
    return records, {'path': str(path), 'physical': source['physical'], 'prefix_bytes': position,
        'prefix_sha256': digest(raw), 'physical_records': len(records),
        'history_start_ordinal': source['history_start_ordinal'], 'host_producer_authenticated': False}


def original_bind_records(context, prepared, bind_request, store, session, owner):
    """Recover only the pending original call sealed in the entry prefix.

    A saved reply is preparation, not completion. Later matching retry calls
    cannot supply this call's missing output or move its fixed response end.
    """
    prior = prepared.get('hold_prefix')
    require(prior is not None, 'HOLD_BIND_PREFIX_ABSENT')
    entry, _ = hold_records(context, prior['prefix_bytes'], prior)
    require(len(entry) == prior['physical_records'] and
            prior['history_start_ordinal'] == context['child']['history_start_ordinal'], 'HOLD_ORIGINAL_ENTRY_COVERAGE')
    original = bind_entry_record(context, entry, bind_request, store, session, owner)
    call_id = original['row']['payload'].get('call_id')
    records, prefix = hold_records(context, prior=prior, until_call={
        'path': context['child']['path'], 'physical': context['child']['physical'],
        'locator': original['locator'], 'call_id': call_id})
    last = records[-1]
    completed = None
    if last['row']['payload'].get('type') == 'custom_tool_call_output' and last['row']['payload'].get('call_id') == call_id:
        completed = {key: resolve_record(context, 'child', locator)[1] for key, locator in
                     (('call', original['locator']), ('result', last['locator']))}
    return records, prefix, completed


def history_with_priors(context, prepared, exchange, bind_request, store, session, owner, prior_context, cache):
    """Refuse any actual exact-episode USE while the observation hold is open.

    At initial bind, cover the source tail containing the pending original call.
    Retry and RETURN/JOIN resolve that call's own response from the sealed entry.
    Later selected USE or acceptance can never repair an observed early call.
    """
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
            require(pin['path'] == context['child']['path'] and pin['physical'] == context['child']['physical'] and
                    pin['role'] == 'child' and pin['locator']['embedded_ordinal'] >= context['child']['history_start_ordinal'] and
                    actual is not None and all(actual['locator'][key] == pin['locator'][key] for key in
                        ('offset', 'bytes', 'sha256', 'embedded_ordinal')) and
                    (pin['locator']['physical_line'] is None or actual['locator']['physical_line'] == pin['locator']['physical_line']),
                    'HOLD_ANCHOR_COVERAGE_DIFFERS')
        current_pairs[pair['call']['locator']['offset']] = pair['result']['locator']['offset']
    bind_input = delivery_tool_input(store, session, owner, bind_request)
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
        current_pairs[current_offset] = None  # Only this exact original may still be pending.
    prior_occurrences, prior_proofs = prior_record_occurrences(context, prepared, current_call, records, prefix,
        store, session, owner, prior_context, cache)
    calls = {}; completed = set(); previous = None
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
        witnessed(row['type'] == 'response_item' and 'metadata' not in row, 'HOLD_UNCLASSIFIED_EVENT', record)
        payload = row['payload']; kind = payload.get('type')
        if kind == 'custom_tool_call':
            command = payload.get('input'); call_id = payload.get('call_id')
            witnessed(payload.get('name') == 'exec' and isinstance(command, str) and
                      isinstance(call_id, str) and call_id, 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            # A call alone proves an attempt. It need not have completed output.
            # Pairing ambiguity cannot erase this independently witnessed fact.
            witnessed(not command.startswith(marker), 'HOLD_EARLY_SAME_EPISODE_USE', record)
            if record['locator']['offset'] in prior_occurrences:
                continue  # Exact validated pair; current early-USE detection ran first.
            witnessed(call_id not in calls, 'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            if classify_prior_retry(context, record, records, prefix, current_call['locator']['offset'],
                    prior_proofs, prior_occurrences, store, session, owner):
                continue
            foreign = re.match(r'^// COMPACTION_OBSERVATION_EXCHANGE=([0-9a-f]{64})\n\S', command)
            # Selected full LOAD/delivery proofs and the original bind cover
            # only their own physical calls, never another same-text pair.
            witnessed(record['locator']['offset'] in current_pairs or foreign is not None,
                      'HOLD_UNCLASSIFIED_TOOL_CALL', record)
            calls[call_id] = record['locator']['offset']
        elif kind == 'custom_tool_call_output':
            if record['locator']['offset'] in prior_occurrences:
                continue  # Exact physical output association was revalidated.
            call_id = payload.get('call_id')
            witnessed(isinstance(call_id, str) and call_id in calls and call_id not in completed,
                      'HOLD_UNPAIRED_TOOL_OUTPUT', record)
            origin = calls[call_id]
            witnessed(origin not in current_pairs or current_pairs[origin] == record['locator']['offset'],
                      'HOLD_UNPAIRED_TOOL_OUTPUT', record)
            completed.add(call_id)  # Association cannot substitute a different selected output.
        elif kind in ('message', 'agent_message'):
            # Quoted/public/output marker text is not an executed tool input.
            continue
        else:
            raise HoldObservationRefusal('HOLD_UNCLASSIFIED_EVENT', prefix, record)
    outstanding = [offset for call_id, offset in calls.items() if call_id not in completed]
    require(not outstanding or completed_bind is None and outstanding == [current_offset], 'HOLD_UNSETTLED_TOOL_CALL')
    if retry:
        require(completed_bind is not None, 'HOLD_ORIGINAL_BIND_COMPLETION_UNPROVED')
        completion = indexed[completed_bind['result']['locator']['offset']]
        try:
            bound_text, validated = command_response(context, 'child', completed_bind['call']['locator'],
                completed_bind['result']['locator'], bind_input)
        except ValueError as exc:
            # Only semantics of the exact covered response qualify here. A
            # second-read pin/range/race refusal is not a stable material event.
            if isinstance(exc, json.JSONDecodeError) or str(exc) in {
                    'ACTUAL_HOST_CALL_RESULT_ASSOCIATION', 'FULL_HOST_OUTPUT_SHAPE',
                    'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED', 'DUPLICATE_JSON_KEY'}:
                raise HoldObservationRefusal(str(exc), prefix, completion) from exc
            raise
        try:
            bound_value = json.loads(bound_text, object_pairs_hook=unique)
        except ValueError as exc:
            raise HoldObservationRefusal('FULL_MECHANICAL_BIND_RESPONSE_REQUIRED', prefix, completion) from exc
        witnessed(validated == completed_bind and bound_value == prepared['bound_response'],
                  'FULL_MECHANICAL_BIND_RESPONSE_REQUIRED', completion)
        before(exchange['records']['result'], completed_bind['call'])
        prefix['original_bind'] = completed_bind
    else:
        require(outstanding == [current_offset], 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    return prefix


def bind_entry_record(context, records, bind_request, store, session, owner):
    """Select the first physical original attempt, never a later same-ID reply."""
    expected = delivery_tool_input(store, session, owner, bind_request)
    matches = [record for record in records[1:]
               if record['row']['ordinal'] >= context['child']['history_start_ordinal']
               and record['row']['type'] == 'response_item'
               and record['row']['payload'].get('type') == 'custom_tool_call'
               and record['row']['payload'].get('name') == 'exec'
               and record['row']['payload'].get('input') == expected]
    require(len(matches) == 1, 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    original = matches[0]
    identifier = original['row']['payload'].get('call_id')
    require(isinstance(identifier, str) and identifier, 'HOLD_ORIGINAL_BIND_CALL_UNPROVED')
    # Earlier completed observations may legitimately have reused a call ID.
    # An output before this exact occurrence is not this occurrence's output.
    require(not any(record['locator']['offset'] > original['locator']['offset']
                    and record['row']['payload'].get('type') == 'custom_tool_call_output'
                    and record['row']['payload'].get('call_id') == identifier for record in records),
            'HOLD_ORIGINAL_BIND_NOT_PENDING_AT_ENTRY')
    return original


def prior_candidate_shape(context, current, identifier, prior):
    require(isinstance(identifier, str) and re.fullmatch('[0-9a-f]{64}', identifier)
            and identifier != current['obligation']['observation_id'], 'HOLD_PRIOR_OBSERVATION_ID')
    closed(prior, ('observation', 'obligation', 'obligation_pin', 'authorization', 'exchange',
                   'delivery_request', 'hold_prefix', 'bind_request', 'bound_response'), 'HOLD_PRIOR_PREPARED_SHAPE')
    observation = closed(prior['observation'], ('child_id', 'scope', 'code', 'source_cutoff', 'source_problem', 'revision'),
                         'HOLD_PRIOR_OBSERVATION_SHAPE')
    require(type(observation['revision']) is int and type(current['observation']['revision']) is int
            and 0 <= observation['revision'] < current['observation']['revision'], 'HOLD_PRIOR_OBSERVATION_ORDER')
    scope = observation['scope']
    require(isinstance(scope, list) and 0 < len(scope) <= MAX_RECORDS, 'HOLD_PRIOR_SCOPE_BOUND')
    for item in scope:
        closed(item, ('id', 'version', 'kind'), 'HOLD_PRIOR_SCOPE_SHAPE')
        require(isinstance(item['id'], str) and item['id'] and isinstance(item['kind'], str) and item['kind']
                and type(item['version']) is int and item['version'] > 0, 'HOLD_PRIOR_SCOPE_SHAPE')
    require(len({item['id'] for item in scope}) == len(scope), 'HOLD_PRIOR_SCOPE_DUPLICATE')
    obligation = closed(prior['obligation'], ('schema', 'parent_identity', 'actual_child_identity', 'selected_child',
        'observation_id', 'covered_boundary_versions', 'observation_source_cutoff', 'code_and_skill_pins',
        'bounded_purpose', 'authority_ceiling'), 'HOLD_PRIOR_OBLIGATION_SHAPE')
    reference = current['obligation']
    require(obligation['schema'] == 'implementaudit.compaction-obligation.v1'
            and obligation['observation_id'] == identifier == digest(canonical(observation))
            and observation['child_id'] == context['actual_child_identity']['thread_id']
            and observation['code'] == reference['code_and_skill_pins']
            and obligation['covered_boundary_versions'] == scope
            and obligation['observation_source_cutoff'] == observation['source_cutoff']
            and all(obligation[key] == reference[key] for key in (
                'parent_identity', 'actual_child_identity', 'selected_child', 'code_and_skill_pins', 'bounded_purpose', 'authority_ceiling'))
            and obligation['parent_identity'] == context['parent_identity']
            and obligation['actual_child_identity'] == context['actual_child_identity']
            and obligation['selected_child'] == 'audit-state' and obligation['authority_ceiling'] == 'NONE',
            'HOLD_PRIOR_OBLIGATION_BINDING')
    closed(prior['obligation_pin'], ('path', 'bytes', 'sha256'), 'HOLD_PRIOR_OBLIGATION_PIN')
    expected_path = Path(current['obligation_pin']['path']).parent / (digest(canonical(obligation)) + '.json')
    require(prior['obligation_pin']['path'] == str(expected_path), 'HOLD_PRIOR_OBLIGATION_NAMESPACE')
    closed(prior['authorization'], ('value', 'text', 'record', 'load_identity', 'route_record', 'evidence'),
           'HOLD_PRIOR_AUTHORIZATION_SHAPE')
    closed(prior['exchange'], ('identity', 'records', 'evidence'), 'HOLD_PRIOR_EXCHANGE_SHAPE')
    closed(prior['delivery_request'], ('child_id', 'phase', 'observation_id', 'authorization_evidence'), 'HOLD_PRIOR_DELIVERY_SHAPE')
    closed(prior['bind_request'], ('child_id', 'phase', 'observation_id', 'exchange'), 'HOLD_PRIOR_BIND_SHAPE')
    require(prior['delivery_request']['child_id'] == prior['bind_request']['child_id'] == observation['child_id']
            and prior['delivery_request']['phase'] == 'deliver' and prior['bind_request']['phase'] == 'bind'
            and prior['delivery_request']['observation_id'] == prior['bind_request']['observation_id'] == identifier
            and prior['delivery_request']['authorization_evidence'] == prior['authorization']['evidence']
            and prior['bind_request']['exchange'] == prior['exchange']['evidence'], 'HOLD_PRIOR_REQUEST_BINDING')
    closed(prior['hold_prefix'], ('path', 'physical', 'prefix_bytes', 'prefix_sha256', 'physical_records',
                                 'history_start_ordinal', 'host_producer_authenticated'), 'HOLD_PRIOR_ENTRY_SHAPE')
    require(prior['hold_prefix']['history_start_ordinal'] == context['child']['history_start_ordinal']
            and prior['hold_prefix']['host_producer_authenticated'] is False, 'HOLD_PRIOR_ACTIVATION_BINDING')
    # The closed original wire response is compared to this exact fixed ceiling;
    # no saved completed flag or later RETURN/JOIN supplies mechanical evidence.
    expected_response = {'observation_id': identifier,
        'child_observation_exchange_identity': prior['exchange']['identity'], **observation,
        'authority': 'NONE', 'canonical_currentness': False, 'recovery_authority': False,
        'epoch_authority': False, 'effect_authority': False, 'independent_children': 'UNCHANGED',
        'actual_child_result_consumer': 'UNQUALIFIED', 'same_failed_scope_retry': 'CONDITIONAL_UNQUALIFIED'}
    require(prior['bound_response'] == expected_response, 'HOLD_PRIOR_BOUND_RESPONSE_FIELDS')


def prior_record_occurrences(context, current, current_call, records, prefix, store, session, owner, candidates, cache):
    """Return only fully revalidated physical mechanical occurrences."""
    indexed = {record['locator']['offset']: record for record in records}
    admitted = set(); proofs = []
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
            require(first_completion['result']['locator']['offset'] + first_completion['result']['locator']['bytes'] <= boundary,
                    'HOLD_PRIOR_PHYSICAL_ORDER')
            earlier = {key: value for key, value in candidates.items()
                       if value['observation']['revision'] < prior['observation']['revision']}
            try:
                held = history_with_priors(context, prior, exchange, prior['bind_request'], store, session, owner, earlier, cache)
            except HoldObservationRefusal as exc:
                # A bad prior event disqualifies this dependent history without
                # falsely labeling it as a current-episode early USE attempt.
                raise HoldObservationRefusal('HOLD_PRIOR_OBSERVATION_REFUSED:' + str(exc),
                    exc.evidence['prefix'], {'locator': exc.evidence['record']}) from exc
            require(held['original_bind'] == first_completion, 'HOLD_PRIOR_ORIGINAL_COMPLETION_CHANGED')
            cache[identifier] = {'held': held, 'prior': prior}
        proof = cache[identifier]
        original = proof['held']['original_bind']
        require(original['result']['locator']['offset'] + original['result']['locator']['bytes'] <= boundary,
                'HOLD_PRIOR_PHYSICAL_ORDER')
        before(original['result'], current_call)
        pairs = (prior['authorization']['load_identity'], prior['exchange']['records'], original)
        def admit(record_pin):
            locator = record_pin['locator']; actual = indexed.get(locator['offset'])
            require(record_pin['path'] == context['child']['path'] and record_pin['physical'] == context['child']['physical']
                    and record_pin['role'] == 'child' and actual is not None
                    and locator['embedded_ordinal'] >= context['child']['history_start_ordinal']
                    and all(actual['locator'][key] == locator[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal'))
                    and (locator['physical_line'] is None or actual['locator']['physical_line'] == locator['physical_line']),
                    'HOLD_PRIOR_OCCURRENCE_BINDING')
            admitted.add(locator['offset'])
        for pair in pairs:
            for record_pin in pair.values():
                admit(record_pin)
        proofs.append({'prior': prior, 'original': original})
    return admitted, proofs


def classify_prior_retry(context, record, records, prefix, boundary, proofs, admitted, store, session, owner):
    """Called in physical scan order, after current early-USE/type/order checks."""
    payload = record['row']['payload']; offset = record['locator']['offset']
    indexed = {item['locator']['offset']: item for item in records}
    for proof in proofs:
        prior, original = proof['prior'], proof['original']
        bind_input = delivery_tool_input(store, session, owner, prior['bind_request'])
        end = original['result']['locator']['offset'] + original['result']['locator']['bytes']
        if not end <= offset < boundary or payload.get('input') != bind_input:
            continue
        call_id = payload.get('call_id')
        following = [item for item in records if offset < item['locator']['offset'] < boundary
                     and item['row']['payload'].get('call_id') == call_id
                     and item['row']['payload'].get('type') in ('custom_tool_call', 'custom_tool_call_output')]
        require(following and following[0]['row']['payload'].get('type') == 'custom_tool_call_output',
                'HOLD_PRIOR_RETRY_COMPLETION_UNPROVED')
        response = following[0]
        try:
            text, pair = command_response(context, 'child', record['locator'], response['locator'], bind_input)
            value = json.loads(text, object_pairs_hook=unique)
        except ValueError as exc:
            if isinstance(exc, json.JSONDecodeError) or str(exc) in {
                    'ACTUAL_HOST_CALL_RESULT_ASSOCIATION', 'FULL_HOST_OUTPUT_SHAPE',
                    'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED', 'DUPLICATE_JSON_KEY'}:
                raise HoldObservationRefusal('HOLD_PRIOR_RETRY_REFUSED:' + str(exc), prefix, response) from exc
            raise
        if value != prior['bound_response']:
            raise HoldObservationRefusal('HOLD_PRIOR_RETRY_RESPONSE_DIFFERS', prefix, response)
        before(original['result'], pair['call'])
        for record_pin in pair.values():
            locator = record_pin['locator']; actual = indexed.get(locator['offset'])
            require(record_pin['path'] == context['child']['path'] and record_pin['physical'] == context['child']['physical']
                    and record_pin['role'] == 'child' and actual is not None
                    and all(actual['locator'][key] == locator[key] for key in ('offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line')),
                    'HOLD_PRIOR_RETRY_OCCURRENCE_BINDING')
            admitted.add(locator['offset'])
        return True
    return False



def hold_history(context, prepared, exchange, bind_request, store, session, owner, prior_context=None):
    """Validate bounded prior candidates, then retain the complete history scan."""
    candidates = {} if prior_context is None else prior_context
    require(type(candidates) is dict and len(candidates) <= MAX_RECORDS, 'HOLD_PRIOR_CONTEXT_BOUND')
    require(len(canonical(candidates)) <= MAX_TOTAL, 'HOLD_PRIOR_CONTEXT_BOUND')
    for identifier, prior in candidates.items():
        prior_candidate_shape(context, prepared, identifier, prior)
    revisions = [prior['observation']['revision'] for prior in candidates.values()]
    require(len(set(revisions)) == len(revisions), 'HOLD_PRIOR_OBSERVATION_ORDER')
    if candidates:
        source_request = {role: {key: context[role][key] for key in ('path', 'metadata', 'allowed_ranges')}
                          for role in ('parent', 'child')}
        source_request.update({key: context[key]['locator'] for key in ('open', 'spawn_call', 'spawn_output')})
        rebound = bind_sources(source_request, context['parent_identity']['thread_id'], context['actual_child_identity']['thread_id'])
        require(rebound == context, 'HOLD_PRIOR_SOURCE_CONTEXT_CHANGED')
    return history_with_priors(context, prepared, exchange, bind_request, store, session, owner, candidates, {})


def actual_result(context, prepared, evidence, store, session, owner, skill_pin, prior_context=None):
    closed(evidence, ('bound_exchange', 'use', 'child_final', 'parent_delivery'), 'ACTUAL_RESULT_EVIDENCE_SHAPE')
    require(prepared.get('exchange') is not None and prepared.get('bound_response') is not None, 'ACTUAL_CHILD_OBSERVATION_MISSING')
    exchange = completed_exchange(context, prepared, prepared['exchange']['evidence'], store, session, owner, skill_pin)
    require(exchange == prepared['exchange'], 'OBSERVED_EXCHANGE_CHANGED')
    closed(evidence['bound_exchange'], ('call', 'result'), 'BOUND_EXCHANGE_SHAPE')
    held = hold_history(context, prepared, exchange, prepared['bind_request'], store, session, owner, prior_context=prior_context)
    bound_identity = held['original_bind']
    for key in ('call', 'result'):
        locator = evidence['bound_exchange'][key]
        original = bound_identity[key]['locator']
        require(isinstance(locator, dict) and set(locator) == set(original) and
                all(locator[field] == original[field] for field in original if field != 'physical_line') and
                locator['physical_line'] in (None, original['physical_line']), 'BOUND_EXCHANGE_NOT_ORIGINAL')
    closed(evidence['use'], ('call', 'result'), 'ACTUAL_USE_EVIDENCE_SHAPE')
    use_row, use_pin = resolve_record(context, 'child', evidence['use']['call'])
    use_input = use_row['payload'].get('input')
    prefix = '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange['identity'] + '\n'
    require(isinstance(use_input, str) and use_input.startswith(prefix) and use_input[len(prefix):].strip(), 'ACTUAL_USE_EXCHANGE_BINDING')
    _, use_identity = command_response(context, 'child', evidence['use']['call'], evidence['use']['result'], use_input)
    before(bound_identity['result'], use_pin)
    final_row, final_pin = resolve_record(context, 'child', evidence['child_final'])
    returned = typed_message(final_row, ('schema', 'obligation_digest', 'observation_id', 'child_observation_exchange_identity',
        'exact_observed_boundary_versions', 'result_bytes_identity', 'authority_ceiling'),
        'implementaudit.compaction-result-return.v1', phase='final_answer')
    before(use_identity['result'], final_pin)
    delivered_row, delivered_pin = resolve_record(context, 'parent', evidence['parent_delivery'])
    delivery = delivered_row['payload']
    envelope = 'Message Type: FINAL_ANSWER\nTask name: /root\nSender: ' + context['actual_child_identity']['agent_path'] + '\nPayload:\n'
    require(delivered_row['type'] == 'response_item' and delivery.get('type') == 'agent_message' and
            delivery.get('author') == context['actual_child_identity']['agent_path'] and delivery.get('recipient') == '/root' and
            delivery.get('content') == [{'type': 'input_text', 'text': envelope + public_message(final_row, 'final_answer')}],
            'ACTUAL_FINAL_RETURN_DELIVERY_ASSOCIATION')
    before(final_pin, delivered_pin)
    obligation = prepared['obligation']
    bindings = {'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': obligation['observation_id'],
        'child_observation_exchange_identity': exchange['identity'], 'exact_observed_boundary_versions': obligation['covered_boundary_versions']}
    require(all(returned[key] == value for key, value in bindings.items()), 'ACTUAL_RETURN_OBLIGATION_OR_SCOPE_DIFFERS')
    raw, result_physical = artifact(returned['result_bytes_identity'])
    result = json.loads(raw, object_pairs_hook=unique)
    closed(result, ('schema', *bindings, 'code_and_skill_pins', 'status', 'currentness', 'measured_epoch', 'frontier', 'members', 'authority_ceiling'),
           'ACTUAL_RESULT_ARTIFACT_FIELDS')
    require(result['schema'] == 'implementaudit.compaction-reconciliation-result.v1' and
            all(result[key] == value for key, value in bindings.items()) and
            result['code_and_skill_pins'] == obligation['code_and_skill_pins'] and result['authority_ceiling'] == 'NONE' and
            result['status'] in ('SUCCEEDED', 'FAILED') and result['currentness'] in ('VERIFIED', 'UNRESOLVED') and
            result['measured_epoch'] in ('VERIFIED', 'UNRESOLVED') and isinstance(result['frontier'], str) and 0 < len(result['frontier']) <= 1024,
            'ACTUAL_RESULT_ARTIFACT_BINDING')
    members = result['members']
    require(isinstance(members, list) and 0 < len(members) <= 32, 'RESULT_MEMBER_CLOSURE')
    result_path = Path(returned['result_bytes_identity']['path'])
    directory = result_path.parent
    member_identities = []; admitted_members = []; seen_paths = set(); seen_physical = set(); total = len(raw)
    for member in members:
        admitted = artifact_preflight(member)
        path, info = admitted
        file_identity = (info.st_dev, info.st_ino)
        require(path.is_relative_to(directory) and path != result_path and
                path not in seen_paths and file_identity not in seen_physical,
                'FOREIGN_OR_DUPLICATE_RESULT_MEMBER')
        seen_paths.add(path); seen_physical.add(file_identity)
        total += member['bytes']
        require(total <= MAX_TOTAL, 'RESULT_CLOSURE_BYTE_BOUND')
        admitted_members.append((member, admitted))
    # Admit the complete closure before any member content read. Recheck each
    # admitted file immediately before opening and retain all after-read checks.
    total = len(raw)
    for member, admitted in admitted_members:
        member_raw, member_physical = artifact(member, admitted=admitted)
        total += len(member_raw)
        require(total <= MAX_TOTAL, 'RESULT_CLOSURE_BYTE_BOUND')
        member_identities.append({'pin': member, 'physical': member_physical})
    identity = {'obligation_digest': bindings['obligation_digest'], 'observation_id': bindings['observation_id'],
        'child_observation_exchange_identity': exchange['identity'], 'scope': obligation['covered_boundary_versions'],
        'result_pin': returned['result_bytes_identity'], 'result_physical': result_physical, 'members': member_identities,
        'child_final': final_pin, 'parent_delivery': delivered_pin, 'bound_exchange': bound_identity, 'use': use_identity,
        'authorization_record': prepared['authorization']['record'], 'hold_history': held}
    return {'identity': identity, 'return_digest': digest(canonical(identity)),
        'status': result['status'], 'currentness': result['currentness'], 'measured_epoch': result['measured_epoch'],
        'frontier': result['frontier'], 'observation_id': bindings['observation_id'], 'evidence': evidence}


def acceptance(context, prepared, result, locator):
    row, record_pin = resolve_record(context, 'parent', locator)
    value = typed_message(row, ('schema', 'action', 'parent_identity', 'actual_child_identity', 'obligation_digest',
        'observation_id', 'child_observation_exchange_identity', 'actual_result_digest', 'accepted_boundary_versions',
        'observation_source_cutoff', 'authority_ceiling'), 'implementaudit.compaction-reconciliation-acceptance.v1',
        'ACCEPT_BOUNDED_RECONCILIATION')
    o = prepared['obligation']
    expected = {'schema': 'implementaudit.compaction-reconciliation-acceptance.v1', 'action': 'ACCEPT_BOUNDED_RECONCILIATION',
        'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'],
        'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': o['observation_id'],
        'child_observation_exchange_identity': prepared['exchange']['identity'], 'actual_result_digest': result['return_digest'],
        'accepted_boundary_versions': o['covered_boundary_versions'], 'observation_source_cutoff': o['observation_source_cutoff'],
        'authority_ceiling': 'NONE'}
    require(value == expected, 'ROOT_ACCEPTANCE_EXACT_RESULT_OR_SCOPE_DIFFERS')
    before(result['identity']['parent_delivery'], record_pin)
    return {'record': record_pin, 'value': value}


def fixed_policy(code_pins):
    path = Path(__file__).resolve().with_name('compaction-result-profile.py')
    path, _ = physical(path)
    spec = importlib.util.spec_from_file_location('_fixed_compaction_policy', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    descriptor = module.POLICY
    closed(descriptor, ('schema', 'profile_id', 'custody_namespace', 'qualification_key',
        'authenticating_source_owner'), 'FIXED_POLICY_SHAPE')
    require(descriptor['schema'] == 'implementaudit.compaction-fixed-acquisition-policy.v1' and
            descriptor['profile_id'] == PROFILE and descriptor['custody_namespace'] == 'result-observations-v1' and
            descriptor['qualification_key'] == 'qualification/Q.json', 'FIXED_POLICY_UNSUPPORTED')
    value = {'descriptor': descriptor, 'code_and_skill_pins': code_pins}
    return {**value, 'policy_digest': digest(canonical(value))}


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
    return json.loads(raw, object_pairs_hook=unique), pin


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
                for child in value.values(): collect(child)
        elif isinstance(value, list):
            for child in value: collect(child)
    for value in (context['open'], context['spawn_call'], context['spawn_output'],
                  prepared['authorization'], prepared['exchange'], result['identity'], accepted):
        collect(value)
    unique_records = {}
    for expected in records:
        _, actual = resolve_record(context, expected['role'], expected['locator'])
        require(actual == expected, 'ACQUIRED_RECORD_IDENTITY_CHANGED')
        unique_records[digest(canonical(actual))] = actual
    o = prepared['obligation']
    candidate = {
        'schema': 'implementaudit.compaction-unconsumed-acquisition.v1',
        'policy_digest': policy['policy_digest'],
        'producer_environment_identity': {'profile_id': PROFILE,
            'parent_metadata': context['parent']['metadata_payload_digest'],
            'child_metadata': context['child']['metadata_payload_digest']},
        'parent_identity': o['parent_identity'], 'actual_child_identity': o['actual_child_identity'],
        'assignment_identity': digest(canonical({'child': o['actual_child_identity'], 'code': o['code_and_skill_pins']})),
        'obligation_digest': prepared['obligation_pin']['sha256'], 'observation_id': o['observation_id'],
        'covered_boundary_versions': o['covered_boundary_versions'],
        'O_U_exchange_USE_R_A_identities': {'O': prepared['obligation_pin'], 'U': prepared['authorization']['record'],
            'exchange': prepared['exchange']['records'], 'USE': result['identity']['use'],
            'R': result['identity'], 'A': accepted},
        'physical_source_and_cutoff_identities': {'parent': context['parent'], 'child': context['child'],
            'compaction_cutoff': o['observation_source_cutoff'], 'records': list(unique_records.values())},
        'exact_result_digest': result['return_digest'], 'exact_acceptance_digest': digest(canonical(accepted)),
        'source_origin_validation': 'UNESTABLISHED', 'host_producer_authenticated': False,
        'authority_ceiling': 'NONE'}
    name = 'candidates/' + digest(canonical(candidate)) + '.json'
    return candidate, immutable_custody(root, name, candidate, writer)


def production_profile(policy, root):
    """Resolve Q as data. Q bindings alone never authenticate an episode."""
    path = root / policy['descriptor']['qualification_key']
    if not path.exists():
        return {'status': 'POLICY_QUALIFICATION_ABSENT', 'policy_qualified': None,
            'qualification_record_bound': False, 'policy_digest': policy['policy_digest'], 'Q': None}
    q, q_pin = custody_record(path, root)
    closed(q, ('policy_digest', 'producer_environment_identity', 'qualification_scope',
        'actual_acquisition_evidence', 'independent_review', 'ROOT_qualification_selection',
        'authority_ceiling'), 'POLICY_QUALIFICATION_FIELDS')
    require(q['policy_digest'] == policy['policy_digest'] and q['authority_ceiling'] == 'NONE' and
        q['qualification_scope'] == {'profile_id': PROFILE, 'candidate_consumption_required': False},
        'POLICY_QUALIFICATION_BINDING')
    evidence_pin = q['actual_acquisition_evidence']
    closed(evidence_pin, ('path', 'bytes', 'sha256'), 'QUALIFICATION_ACQUISITION_PIN')
    evidence_path = Path(evidence_pin['path'])
    require(evidence_path.parent == root / 'candidates', 'QUALIFICATION_CANDIDATE_NAMESPACE')
    evidence, checked_pin = custody_record(evidence_path, root)
    require(checked_pin == evidence_pin and evidence['schema'] == 'implementaudit.compaction-unconsumed-acquisition.v1' and
        evidence['policy_digest'] == policy['policy_digest'] and
        evidence['producer_environment_identity'] == q['producer_environment_identity'] and
        evidence['authority_ceiling'] == 'NONE', 'QUALIFICATION_ACTUAL_CANDIDATE_BINDING')
    subject = {key: q[key] for key in ('policy_digest', 'producer_environment_identity',
                                     'qualification_scope', 'actual_acquisition_evidence')}
    proof_pins = []
    for field in ('independent_review', 'ROOT_qualification_selection'):
        item = q[field]; closed(item, ('path', 'bytes', 'sha256'), 'QUALIFICATION_REVIEW_PIN')
        require(Path(item['path']).parent == root / 'qualification', 'QUALIFICATION_REVIEW_NAMESPACE')
        record, actual_pin = custody_record(Path(item['path']), root)
        require(actual_pin == item, 'QUALIFICATION_REVIEW_PIN_CHANGED')
        closed(record, ('subject', 'disposition', 'authority_ceiling'), 'QUALIFICATION_REVIEW_FIELDS')
        require(record['subject'] == subject and record['authority_ceiling'] == 'NONE' and
            record['disposition'] == ('PASS' if field == 'independent_review' else 'SELECTED'),
            'QUALIFICATION_REVIEW_BINDING')
        proof_pins.append(actual_pin)
    return {'status': 'QUALIFICATION_RECORD_BOUND_ORIGIN_UNRESOLVED', 'policy_qualified': None,
        'qualification_record_bound': True, 'policy_digest': policy['policy_digest'], 'Q': q_pin,
        'evidence': checked_pin, 'review_pins': proof_pins,
        'unresolved_implementation_edge': 'No independently authenticating producer/custody validator is established'}


def episode_value(candidate, candidate_pin, q_pin):
    return {key: candidate[key] for key in ('policy_digest', 'parent_identity', 'actual_child_identity',
        'assignment_identity', 'obligation_digest', 'observation_id', 'covered_boundary_versions',
        'O_U_exchange_USE_R_A_identities', 'physical_source_and_cutoff_identities',
        'exact_result_digest', 'exact_acceptance_digest', 'authority_ceiling')} | {
        'Q_digest': q_pin['sha256'],
        'actual_acquisition_and_custody_validation_evidence': {'candidate': candidate_pin}}


def acquire_episode(context, prepared, result, accepted, code_pins, custody_root, writer):
    """Reachable existing-owner acquisition/admission seam; no new command."""
    policy = fixed_policy(code_pins)
    root = Path(custody_root) / policy['descriptor']['custody_namespace'] / policy['policy_digest']
    candidate, candidate_pin = acquire_candidate(context, prepared, result, accepted, policy, root, writer)
    profile = production_profile(policy, root)
    episode_key = digest(canonical({'policy': policy['policy_digest'], 'candidate': candidate_pin['sha256'],
        'result': result['return_digest'], 'acceptance': candidate['exact_acceptance_digest']}))
    path = root / 'episodes' / (episode_key + '.json')
    response = {'status': 'CANDIDATE_ACQUIRED_PENDING_QUALIFICATION', 'policy': policy, 'profile': profile,
        'candidate': candidate_pin, 'lookup': {'Q': str(root / policy['descriptor']['qualification_key']), 'E': str(path)},
        'episode_record_bound': False, 'episode': None, 'origin_validated': None,
        'host_producer_authenticated': False, 'authority_ceiling': 'NONE',
        'unresolved_implementation_edge': 'Authenticating producer/custody acquisition validator is not implemented or qualified'}
    if profile['qualification_record_bound']:
        response['status'] = 'QUALIFICATION_BOUND_PENDING_EPISODE_ORIGIN'
        response['episode_candidate'] = episode_value(candidate, candidate_pin, profile['Q'])
    if path.exists():
        require(profile['qualification_record_bound'], 'EPISODE_WITHOUT_EXACT_Q')
        episode, episode_pin = custody_record(path, root)
        require(episode == response['episode_candidate'], 'EXACT_EPISODE_BINDING_DIFFERS')
        response.update(status='EPISODE_BOUND_PENDING_ORIGIN_VALIDATOR', episode=episode_pin, episode_record_bound=True)
    # This is the explicit incomplete foundational edge. No API or validating
    # owner is invented here. A future implemented/qualified fixed P must derive
    # actual origin from its supported owner before first-creating admitted E.
    # Record binding, global Q or an owner-writable E cannot replace that work.
    require(policy['descriptor']['authenticating_source_owner'] is None, 'UNSUPPORTED_AUTHENTICATING_OWNER')
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
        require(isinstance(window, dict) and set(window) == {'offset', 'bytes'} and
                type(window['offset']) is int and window['offset'] >= 0 and
                type(window['bytes']) is int and 0 < window['bytes'] <= MAX_TOTAL, 'ALLOWED_RANGE_BOUND')
    total = 0; intervals = []
    for item in selectors:
        require(isinstance(item, dict) and set(item) == {'offset', 'bytes', 'sha256', 'embedded_ordinal', 'physical_line'},
                'RECORD_LOCATOR_SHAPE')
        require(type(item['offset']) is int and item['offset'] >= 0 and
                type(item['bytes']) is int and 0 < item['bytes'] <= MAX_RECORD, 'RECORD_BYTE_BOUND')
        require(isinstance(item['sha256'], str) and re.fullmatch('[0-9a-f]{64}', item['sha256']) and
                type(item['embedded_ordinal']) is int and item['embedded_ordinal'] >= 0 and
                (item['physical_line'] is None or type(item['physical_line']) is int and item['physical_line'] > 0),
                'RECORD_IDENTITY_SHAPE')
        end = item['offset'] + item['bytes']
        require(any(window['offset'] <= item['offset'] and end <= window['offset'] + window['bytes']
                    for window in allowed_ranges), 'OUTSIDE_ALLOWED_READ_RANGE')
        intervals.append((item['offset'], end)); total += item['bytes']
    require(total <= MAX_TOTAL, 'TOTAL_RECORD_BYTE_BOUND')
    intervals.sort()
    require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])), 'OVERLAPPING_RECORD_LOCATORS')
    # All range checks precede any file opening or content read.
    path, before = physical(path)
    require(expected_physical is None or expected_physical == identity(before), 'SOURCE_PHYSICAL_ID_CHANGED')
    require(all(end <= before.st_size for _, end in intervals), 'RECORD_RANGE_PAST_END')
    records = []
    with open(path, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        require(identity(opened) == identity(before) and opened.st_nlink == 1, 'SOURCE_CHANGED_BEFORE_READ')
        for selector in selectors:
            stream.seek(selector['offset'])
            raw = stream.read(selector['bytes'])
            require(len(raw) == selector['bytes'] and hashlib.sha256(raw).hexdigest() == selector['sha256'], 'RECORD_PIN_CHANGED')
            require(raw.endswith(b'\n') and raw.count(b'\n') == 1 and b'\r' not in raw and b'\x00' not in raw,
                    'RECORD_PARTIAL_OR_MULTIPLE_WIRE')
            row = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
            require(isinstance(row, dict) and set(row) in ({'timestamp', 'ordinal', 'type', 'payload'},
                    {'timestamp', 'ordinal', 'type', 'payload', 'metadata'}) and
                    type(row.get('ordinal')) is int and row['ordinal'] == selector['embedded_ordinal'] and
                    isinstance(row.get('timestamp'), str) and isinstance(row.get('type'), str) and
                    isinstance(row.get('payload'), dict), 'OBSERVED_RECORD_SHAPE_OR_ORDINAL')
            records.append({'locator': dict(selector), 'row': row})
        after_open = os.fstat(stream.fileno())
    _, after_path = physical(path)
    require(identity(after_path) == identity(after_open) == identity(before) and
            (before.st_size, before.st_mtime_ns) == (after_open.st_size, after_open.st_mtime_ns) ==
            (after_path.st_size, after_path.st_mtime_ns), 'SOURCE_CHANGED_DURING_READ')
    return {'path': str(path), 'physical': identity(before), 'records': records,
            'host_producer_authenticated': False}
