"""Proposed pure Codex 0.166 mechanical grammar; not an admission or producer.

Raw native records and their physical locators remain unchanged. The existing
R/A/S owners must select and pin this module before any result can use it.
"""
import hashlib
import json
import re

PROFILE = 'codex-app-server-0.166.0-linux-prior-mechanical-v1'
NAMESPACE = 'mcp__dg18prior'
TOOL = 'observe_prior'
RESPONSE = 'implementaudit.codex0166-mechanical-tool-response.v1'
UUID = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
SHA = r'[0-9a-f]{64}'
MAX_TEXT = 256 * 1024


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'DUPLICATE_JSON_KEY')
        value[key] = item
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(text):
    require(type(text) is str and len(text.encode('utf-8')) <= MAX_TEXT,
            'MECHANICAL_JSON_BOUND')
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(
                          ValueError('NONFINITE_JSON')))


def spawn_message(episode):
    require(episode.get('schema') == 'implementaudit.r0033-current-episode-binding.v1'
            and episode.get('canonical_route_currentness') == 'VALIDATED_AT_READ'
            and episode.get('selected_child_role') == 'audit-state'
            and episode.get('authority_ceiling') == 'NONE'
            and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', episode.get('logical_task', ''))
            and re.fullmatch('sha256:' + SHA, episode.get('opening_digest', '')),
            'MECHANICAL_CANONICAL_OPEN_REQUIRED')
    return 'DG18_PRIOR_MECHANICAL_CHILD_V1\n' + canonical({
        'logical_task': episode['logical_task'],
        'opening_digest': episode['opening_digest'],
        'selected_child': 'audit-state', 'authority_ceiling': 'NONE',
        'purpose': 'Actual LOAD, authorized EXCHANGE, original BIND, exact retry; no RETURN or JOIN',
        'provider': 'DETERMINISTIC_EMULATION_NOT_INDEPENDENT_COGNITION',
    }).decode('utf-8')


def native_spawn_identity(parent, child, call, result, episode):
    """Check raw header/spawn meaning. Custody, locators and order belong to S/R."""
    root = parent.get('id')
    require(re.fullmatch(UUID, root or '') and parent.get('session_id') == root
            and parent.get('cli_version') == child.get('cli_version') == '0.166.0'
            and episode.get('host_and_scope', {}).get('host_session_id') == root,
            'MECHANICAL_NATIVE_ROOT_BINDING')
    require(call.get('type') == 'function_call'
            and call.get('namespace') == 'multi_agent_v1'
            and call.get('name') == 'spawn_agent'
            and type(call.get('call_id')) is str and call['call_id']
            and result.get('type') == 'function_call_output'
            and result.get('call_id') == call['call_id'],
            'ACTUAL_SPAWN_CALL_OUTPUT_ASSOCIATION')
    args, answer = parse(call.get('arguments')), parse(result.get('output'))
    require(args == {'fork_context': False, 'message': spawn_message(episode)},
            'MECHANICAL_CANONICAL_OPEN_SPAWN_MESSAGE_REQUIRED')
    require(type(answer) is dict and set(answer) == {'agent_id', 'nickname'}
            and re.fullmatch(UUID, answer.get('agent_id', ''))
            and type(answer['nickname']) is str and answer['nickname'],
            'MECHANICAL_NATIVE_SPAWN_RESPONSE')
    ident = answer['agent_id']
    source = child.get('source')
    require(type(source) is dict and type(source.get('subagent')) is dict,
            'MECHANICAL_ACTUAL_CHILD_HEADER_BINDING')
    relation = source['subagent'].get('thread_spawn')
    require(child.get('id') == ident and child.get('session_id') == root
            and child.get('parent_thread_id') == root
            and child.get('agent_nickname') == answer['nickname']
            and relation == {'parent_thread_id': root, 'depth': 1, 'agent_path': None,
                             'agent_nickname': answer['nickname'], 'agent_role': None}
            and all(child.get(k) is None for k in
                    ('agent_path', 'forked_from_id', 'subagent_history_start_ordinal')),
            'MECHANICAL_ACTUAL_CHILD_HEADER_BINDING')
    return {'parent_identity': {'thread_id': root},
            'actual_child_identity': {'thread_id': ident},
            'canonical_logical_task': episode['logical_task'],
            'logical_task_basis': 'CANONICAL_OPEN_AND_EXACT_NATIVE_SPAWN_MESSAGE',
            'native_agent_path': None}


def tool_metadata(meta, root, child):
    """Observed MCP envelope fields; association still requires raw source pins."""
    keys = {'callId', 'itemId', 'progressToken', 'sessionId', 'threadId', 'windowId',
            'x-codex-turn-metadata'}
    require(type(meta) is dict and set(meta) == keys
            and meta['sessionId'] == root and meta['threadId'] == child
            and type(meta['callId']) is str and meta['callId']
            and type(meta['itemId']) is str and meta['itemId']
            and type(meta['progressToken']) is int and meta['progressToken'] >= 0
            and type(meta['windowId']) is str, 'MECHANICAL_NATIVE_TOOL_METADATA')
    turn = meta['x-codex-turn-metadata']
    expected = {'auto_review_enabled', 'codex_version', 'model', 'node_repl_auto_review_required',
                'node_repl_disabled', 'parent_thread_id', 'sandbox', 'sandbox_mode', 'session_id',
                'subagent_kind', 'thread_id', 'thread_source', 'turn_id', 'turn_started_at_unix_ms'}
    require(type(turn) is dict and set(turn) == expected and turn['codex_version'] == '0.166.0'
            and turn['thread_id'] == child and turn['session_id'] == turn['parent_thread_id'] == root
            and turn['thread_source'] == 'subagent' and turn['subagent_kind'] == 'thread_spawn'
            and turn['sandbox'] == 'seccomp' and turn['sandbox_mode'] == 'read-only'
            and type(turn['model']) is str
            and all(type(turn[k]) is bool for k in
                    ('auto_review_enabled', 'node_repl_auto_review_required', 'node_repl_disabled'))
            and type(turn['turn_started_at_unix_ms']) is int and turn['turn_started_at_unix_ms'] >= 0
            and re.fullmatch(UUID, turn['turn_id'] or ''), 'MECHANICAL_NATIVE_TURN_METADATA')
    return {'call_id': meta['callId'], 'item_id': meta['itemId'], 'turn_id': turn['turn_id']}


def arguments(selection_sha256, operation, request):
    require(re.fullmatch(SHA, selection_sha256 or '') and operation in ('LOAD', 'DELIVER', 'BIND')
            and type(request) is dict, 'MECHANICAL_ARGUMENT_SHAPE')
    return {'selection_sha256': selection_sha256, 'operation': operation,
            'request_json': canonical(request).decode('utf-8')}


def arguments_wire(value):
    # The retained provider.py:24 uses json.dumps on this insertion order.
    return json.dumps(value)


def parsed_arguments(text):
    value = parse(text)
    require(type(value) is dict and set(value) ==
            {'selection_sha256', 'operation', 'request_json'}, 'MECHANICAL_ARGUMENT_SHAPE')
    request = parse(value['request_json'])
    expected = arguments(value['selection_sha256'], value['operation'], request)
    require(value == expected and text == arguments_wire(expected),
            'MECHANICAL_EXACT_ARGUMENT_WIRE_REQUIRED')
    return value, request


def call_input(payload):
    require(payload.get('type') == 'function_call'
            and payload.get('namespace') == NAMESPACE and payload.get('name') == TOOL
            and type(payload.get('call_id')) is str and payload['call_id']
            and 'input' not in payload and 'status' not in payload,
            'ACTUAL_HOST_CALL_RESULT_ASSOCIATION')
    parsed_arguments(payload.get('arguments'))
    return payload['arguments']


def is_call(payload):
    return (payload.get('type') == 'function_call'
            and payload.get('namespace') == NAMESPACE and payload.get('name') == TOOL)


def is_output(payload):
    return payload.get('type') == 'function_call_output'


def framing_text(output):
    content = output.get('output')
    require(type(content) is list and len(content) == 2
            and all(type(b) is dict and set(b) == {'type', 'text'}
                    and b['type'] == 'input_text' and type(b['text']) is str for b in content)
            and re.fullmatch(r'Wall time: [0-9]+(?:\.[0-9]+)? seconds\nOutput:', content[0]['text']),
            'FULL_HOST_OUTPUT_SHAPE')
    return content[1]['text']


def response_text(call, output, expected_input):
    require(call_input(call) == expected_input and is_output(output)
            and output.get('call_id') == call['call_id'],
            'ACTUAL_HOST_CALL_RESULT_ASSOCIATION')
    args, _ = parsed_arguments(expected_input)
    receipt = parse(framing_text(output))
    keys = {'schema', 'selection_sha256', 'operation', 'request_sha256', 'exit_code',
            'stdout', 'stdout_sha256', 'stderr_sha256'}
    require(type(receipt) is dict and set(receipt) == keys and receipt['schema'] == RESPONSE
            and receipt['selection_sha256'] == args['selection_sha256']
            and receipt['operation'] == args['operation']
            and receipt['request_sha256'] == digest(args['request_json'].encode('utf-8'))
            and type(receipt['exit_code']) is int and receipt['exit_code'] == 0
            and type(receipt['stdout']) is str
            and receipt['stdout_sha256'] == digest(receipt['stdout'].encode('utf-8'))
            and re.fullmatch(SHA, receipt['stderr_sha256'] or ''),
            'FULL_SUCCESSFUL_HOST_RESPONSE_REQUIRED')
    return receipt['stdout']


def retained_metadata(row, role, active_turn=None):
    p, m = row['payload'], row.get('metadata')
    if type(m) is not dict or m.get('client_authored') is not False:
        return False
    allowed = {'client_authored', 'retained_source', 'user_input_order'}
    if role == 'user':
        allowed.add('mcp_attribution')
    if not set(m) <= allowed or 'retained_source' not in m:
        return False
    r = m['retained_source']; ident = r.get('id', {}) if type(r) is dict else {}
    return (type(r) is dict and set(r) == {'complete', 'id', 'revision'} and r['complete'] is True
            and type(ident) is dict and set(ident) == {'message_id', 'role', 'turn_id'}
            and ident['message_id'] == p.get('id') and ident['role'] == role
            and type(ident['turn_id']) is str and re.fullmatch(UUID, ident['turn_id']) is not None
            and type(r['revision']) is str and re.fullmatch('retained_' + UUID, r['revision']) is not None
            and (active_turn is None or ident['turn_id'] == active_turn)
            and ('user_input_order' not in m or
                 type(m['user_input_order']) is int and m['user_input_order'] >= 0)
            and ('mcp_attribution' not in m or m['mcp_attribution'] == {'status': 'none'}))


def metadata_ok(row, active_turn=None):
    p = row['payload']; kind = p.get('type'); m = row.get('metadata')
    if 'metadata' not in row:
        return kind == 'message' and p.get('role') == 'user'
    if kind == 'message' and p.get('role') in ('assistant', 'user'):
        return retained_metadata(row, p['role'], active_turn)
    if kind == 'message' and p.get('role') == 'developer':
        return m == {'client_authored': False, 'mcp_attribution': {'status': 'none'}}
    if kind == 'function_call':
        return (type(m) is dict and set(m) == {'client_authored', 'user_input_order'}
                and m['client_authored'] is False and type(m['user_input_order']) is int
                and m['user_input_order'] >= 0)
    if kind == 'function_call_output':
        if type(m) is not dict or set(m) not in (
                {'client_authored', 'fallback_token_limit_override'},
                {'client_authored', 'fallback_token_limit_override', 'mcp_attribution'}):
            return False
        attribution = m.get('mcp_attribution')
        valid = attribution is None or (
            type(attribution) is dict and set(attribution) == {'sources', 'status'}
            and attribution['status'] == 'complete' and type(attribution['sources']) is list
            and len(attribution['sources']) == 1
            and attribution['sources'][0] == {'server_name': 'dg18prior', 'tool_name': TOOL,
                                             'first_turn_id': active_turn})
        return m['client_authored'] is False and m['fallback_token_limit_override'] == 3000 and valid
    return False


def public_text(row, phase='commentary'):
    p = row['payload']; content = p.get('content')
    require(phase == 'commentary' and row.get('type') == 'response_item'
            and p.get('type') == 'message' and p.get('role') == 'assistant'
            and p.get('status') == 'completed' and 'phase' not in p
            and retained_metadata(row, 'assistant') and type(content) is list and len(content) == 1
            and set(content[0]) == {'type', 'text', 'annotations'}
            and content[0]['type'] == 'output_text' and content[0]['annotations'] == []
            and type(content[0]['text']) is str,
            'ACTUAL_ASSISTANT_ROLE_OR_PHASE')
    return content[0]['text']
