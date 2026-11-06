"""Bounded loopback Messages test responder and data-only native receiving.

No forwarding, credentials, subprocess, model or tool implementation. Socket
creation occurs only in LocalResponder.start(), after the probe's admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import socket
import threading
import time

HEADER_LIMIT = 32768
BODY_LIMIT = 2 * 1024 * 1024
TOTAL_REQUEST_LIMIT = 4 * 1024 * 1024
REQUEST_LIMIT = 16
RESPONSE_LIMIT = 16384
CONNECTION_SECONDS = 5
ACK = 'DG17_LOCAL_CANONICAL_BODY_DELIVERY_ACK'
FIXTURE_TOKEN = 'dg17-loopback-fixture-not-an-upstream-credential'
MODEL_SELECTOR = 'claude-sonnet-4-6'
EXPECTED_NAMES = ('implementaudit:implementaudit', 'implementaudit:audit-state',
                  'implementaudit:audit-assess', 'implementaudit:audit-implement',
                  'implementaudit:audit-andon')


class Refusal(RuntimeError):
    pass


def need(condition, code):
    if not condition:
        raise Refusal(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def strict_json(raw, limit=BODY_LIMIT):
    need(type(raw) is bytes and len(raw) <= limit, 'PROTOCOL_JSON_BYTE_BOUND')
    def pairs(values):
        out = {}
        for key, value in values:
            need(key not in out, 'PROTOCOL_DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    def nonfinite(_):
        raise Refusal('PROTOCOL_NONFINITE_JSON')
    try:
        out = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                         parse_constant=nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('PROTOCOL_JSON_UNRECEIVED') from None
    pending = [(out, 0)]; count = 0
    while pending:
        value, depth = pending.pop(); count += 1
        need(count <= 32768 and depth <= 32, 'PROTOCOL_JSON_COMPLEXITY_BOUND')
        if type(value) is dict:
            need(len(value) <= 1024 and all(type(k) is str and len(k) <= 1024 for k in value),
                 'PROTOCOL_JSON_OBJECT_BOUND')
            pending.extend((v, depth + 1) for v in value.values())
        elif type(value) is list:
            need(len(value) <= 4096, 'PROTOCOL_JSON_ARRAY_BOUND')
            pending.extend((v, depth + 1) for v in value)
        elif type(value) is str:
            need(len(value.encode('utf-8')) <= limit, 'PROTOCOL_JSON_STRING_BOUND')
        elif type(value) is float:
            need(math.isfinite(value), 'PROTOCOL_NONFINITE_JSON')
        elif value is None or type(value) in (bool, int):
            pass
        else:
            raise Refusal('PROTOCOL_JSON_TYPE_REFUSED')
    return out


def parse_head(raw, port):
    need(raw.endswith(b'\r\n\r\n') and len(raw) <= HEADER_LIMIT, 'HTTP_HEADER_BOUND')
    try:
        lines = raw[:-4].decode('ascii').split('\r\n')
    except UnicodeError:
        raise Refusal('HTTP_HEADER_ENCODING') from None
    need(len(lines) <= 65 and all('\r' not in x and '\n' not in x for x in lines),
         'HTTP_HEADER_SHAPE')
    first = lines[0].split(' ')
    need(len(first) == 3 and first[2] in ('HTTP/1.0', 'HTTP/1.1') and
         first[0] in ('HEAD', 'POST') and len(first[1]) <= 512, 'HTTP_REQUEST_LINE_REFUSED')
    headers = {}
    for line in lines[1:]:
        need(':' in line and not line.startswith((' ', '\t')), 'HTTP_HEADER_SHAPE')
        name, value = line.split(':', 1); name = name.lower()
        need(re.fullmatch(r'[a-z0-9-]{1,80}', name) is not None and name not in headers,
             'HTTP_DUPLICATE_OR_INVALID_HEADER')
        headers[name] = value.strip()
    need(headers.get('host') == '127.0.0.1:' + str(port), 'HTTP_HOST_DIFFERS')
    need('transfer-encoding' not in headers and 'content-encoding' not in headers,
         'HTTP_UNREVIEWED_ENCODING')
    length = headers.get('content-length', '0')
    need(re.fullmatch(r'[0-9]{1,10}', length) is not None and int(length) <= BODY_LIMIT,
         'HTTP_BODY_BOUND')
    method, path = first[:2]
    if method == 'HEAD':
        need(path == '/api/hello' and int(length) == 0, 'HTTP_ENDPOINT_REFUSED')
        kind = 'STARTUP_HEAD'
    else:
        need(path in ('/v1/messages', '/v1/messages?beta=true', '/v1/messages/count_tokens'),
             'HTTP_ENDPOINT_REFUSED')
        need(headers.get('authorization') == 'Bearer ' + FIXTURE_TOKEN,
             'HTTP_FIXTURE_TOKEN_DIFFERS')
        need(headers.get('content-type', '').split(';', 1)[0].strip() == 'application/json',
             'HTTP_CONTENT_TYPE_REFUSED')
        need(int(length) > 0, 'HTTP_BODY_REQUIRED')
        kind = 'TOKEN_COUNT' if path.endswith('/count_tokens') else 'MESSAGES'
    return {'kind': kind, 'length': int(length)}


def message_response(model):
    need(model == MODEL_SELECTOR, 'REQUEST_MODEL_SELECTOR_DIFFERS')
    events = [
        ('message_start', {'type': 'message_start', 'message': {
            'id': 'msg_dg17_local_canonical_01', 'type': 'message', 'role': 'assistant',
            'content': [], 'model': model, 'stop_reason': None, 'stop_sequence': None,
            'usage': {'input_tokens': 1, 'output_tokens': 0}}}),
        ('content_block_start', {'type': 'content_block_start', 'index': 0,
                                'content_block': {'type': 'text', 'text': ''}}),
        ('content_block_delta', {'type': 'content_block_delta', 'index': 0,
                                'delta': {'type': 'text_delta', 'text': ACK}}),
        ('content_block_stop', {'type': 'content_block_stop', 'index': 0}),
        ('message_delta', {'type': 'message_delta',
                           'delta': {'stop_reason': 'end_turn', 'stop_sequence': None},
                           'usage': {'output_tokens': 1}}),
        ('message_stop', {'type': 'message_stop'}),
    ]
    raw = b''.join(b'event: ' + kind.encode('ascii') + b'\ndata: ' + canonical(value).rstrip(b'\n') +
                   b'\n\n' for kind, value in events)
    need(len(raw) <= RESPONSE_LIMIT, 'RESPONSE_BYTE_BOUND')
    return raw


def http_response(status, content_type, body):
    need(status in (200, 400, 501) and len(body) <= RESPONSE_LIMIT, 'RESPONSE_SHAPE_REFUSED')
    label = {200: 'OK', 400: 'Bad Request', 501: 'Not Implemented'}[status]
    return (f'HTTP/1.1 {status} {label}\r\nContent-Type: {content_type}\r\n'
            f'Content-Length: {len(body)}\r\nConnection: close\r\nx-should-retry: false\r\n\r\n').encode('ascii') + body


class LocalResponder:
    """Own exactly one listener/thread and one accepted socket at a time."""
    def __init__(self, private, write_private, deadline):
        self.private = private; self.write_private = write_private; self.deadline = deadline
        self.stop_event = threading.Event(); self.listener = None; self.active = None
        self.thread = None; self.port = None; self.rows = []; self.failure = None
        self.supplemental_failures = []; self.sent_bytes = 0
        self.total_bytes = 0; self.messages = 0; self.semantic_raw = None
        self.semantic_index = None; self.response_complete = False
        self.closed_sockets = []; self.started = False; self.joined = False

    def fail(self, code):
        if self.failure is None:
            self.failure = code
        elif code != self.failure and code not in self.supplemental_failures and len(self.supplemental_failures) < 8:
            self.supplemental_failures.append(code)
        self.stop_event.set()

    def start(self):
        need(self.listener is None and self.thread is None, 'PROVIDER_ALREADY_STARTED')
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listener.settimeout(0.2)
            self.listener.bind(('127.0.0.1', 0)); self.listener.listen(1)
            address = self.listener.getsockname()
            need(address[0] == '127.0.0.1' and 1024 <= address[1] <= 65535,
                 'PROVIDER_BIND_REFUSED')
            self.port = address[1]
            self.thread = threading.Thread(target=self._serve, name='dg17-canonical-messages', daemon=False)
            self.thread.start(); self.started = True
        except BaseException as exc:
            self.fail(str(exc) if isinstance(exc, Refusal) else 'PROVIDER_START_FAILURE')
            self._close_socket(self.listener)
            raise
        return 'http://127.0.0.1:' + str(self.port)

    def _close_socket(self, handle):
        if handle is None:
            return
        try:
            handle.close()
        except OSError:
            self.fail('PROVIDER_SOCKET_CLOSE_REFUSED')
        if not any(x is handle for x in self.closed_sockets):
            self.closed_sockets.append(handle)

    def _check(self, end):
        need(not self.stop_event.is_set(), 'PROVIDER_STOPPED')
        need(time.monotonic() < min(end, self.deadline), 'PROVIDER_IO_DEADLINE')

    def _read(self, connection, amount, end):
        while True:
            self._check(end)
            try:
                return connection.recv(amount)
            except socket.timeout:
                continue

    def _send(self, connection, raw, end):
        sent = 0; self.sent_bytes = 0
        while sent < len(raw):
            self._check(end)
            try:
                n = connection.send(raw[sent:])
            except socket.timeout:
                continue
            need(n > 0, 'PROVIDER_RESPONSE_TRUNCATED')
            sent += n
            self.sent_bytes = sent

    def _handle(self, connection, index):
        raw = bytearray(); body = b''; response = b''; complete = False; kind = 'UNKNOWN'; split = None
        self.sent_bytes = 0
        end = min(self.deadline, time.monotonic() + CONNECTION_SECONDS)
        try:
            while b'\r\n\r\n' not in raw:
                need(len(raw) < HEADER_LIMIT, 'HTTP_HEADER_BOUND')
                remaining = TOTAL_REQUEST_LIMIT - self.total_bytes - len(raw)
                need(remaining > 0, 'HTTP_TOTAL_REQUEST_BYTE_BOUND')
                part = self._read(connection, min(1024, HEADER_LIMIT - len(raw), remaining), end)
                need(part, 'HTTP_TRUNCATED_HEADER'); raw.extend(part)
            split = bytes(raw).index(b'\r\n\r\n') + 4
            head = parse_head(bytes(raw[:split]), self.port); kind = head['kind']
            need(len(raw) - split <= head['length'], 'HTTP_EXTRA_REQUEST_BYTES')
            need(self.total_bytes + split + head['length'] <= TOTAL_REQUEST_LIMIT,
                 'HTTP_TOTAL_REQUEST_BYTE_BOUND')
            while len(raw) - split < head['length']:
                part = self._read(connection, min(65536, head['length'] - len(raw) + split), end)
                need(part, 'HTTP_TRUNCATED_BODY'); raw.extend(part)
            body = bytes(raw[split:]); complete = True
            if kind == 'STARTUP_HEAD':
                response = http_response(200, 'text/plain', b'')
            elif kind == 'TOKEN_COUNT':
                strict_json(body)
                response = http_response(501, 'application/json', canonical({
                    'type': 'error', 'error': {'type': 'not_found_error',
                    'message': 'Optional token counting is unavailable in the local fixture.'}}))
            else:
                self.messages += 1
                need(self.messages == 1, 'SECOND_SEMANTIC_REQUEST_REFUSED')
                value = strict_json(body)
                need(type(value) is dict and value.get('stream') is True and
                     value.get('model') == MODEL_SELECTOR and type(value.get('messages')) is list,
                     'MESSAGES_REQUEST_SHAPE_UNRECEIVED')
                self.semantic_raw = body; self.semantic_index = index
                response = http_response(200, 'text/event-stream', message_response(value['model']))
            self._send(connection, response, end)
            if kind == 'MESSAGES':
                self.response_complete = True
        except BaseException as exc:
            self.fail(str(exc) if isinstance(exc, Refusal) else 'PROVIDER_IO_FAILURE')
            raise
        finally:
            if split is not None:
                body = bytes(raw[split:])
            self.total_bytes += len(raw)
            row = {'index': index, 'kind': kind, 'request_complete': complete,
                   'request_bytes': len(raw), 'request_sha256': digest(bytes(raw)),
                   'body_bytes': len(body), 'body_sha256': digest(body),
                   'prepared_response_bytes': len(response), 'prepared_response_sha256': digest(response),
                   'socket_send_returned_bytes': self.sent_bytes,
                   'response_send_complete': bool(response) and self.sent_bytes == len(response)}
            self.rows.append(row)
            stem = self.private / ('request-' + str(index).zfill(3))
            try:
                self.write_private(stem.with_suffix('.http'), bytes(raw))
                self.write_private(stem.with_suffix('.body'), body)
                self.write_private(stem.with_suffix('.response'), response)
            except BaseException:
                self.fail('PROVIDER_PRIVATE_RETENTION_REFUSED')
                raise

    def _serve(self):
        try:
            while not self.stop_event.is_set() and time.monotonic() < self.deadline:
                if len(self.rows) >= REQUEST_LIMIT:
                    self.stop_event.set()
                    break
                try:
                    connection, peer = self.listener.accept()
                except socket.timeout:
                    continue
                self.active = connection; connection.settimeout(0.2)
                try:
                    need(peer[0] == '127.0.0.1', 'NONLOOPBACK_PEER_REFUSED')
                    self._handle(connection, len(self.rows) + 1)
                finally:
                    self._close_socket(connection); self.active = None
            if not self.stop_event.is_set() and time.monotonic() >= self.deadline:
                self.fail('PROVIDER_IO_DEADLINE')
        except BaseException as exc:
            if not (self.stop_event.is_set() and isinstance(exc, OSError)):
                self.fail(str(exc) if isinstance(exc, Refusal) else 'PROVIDER_INTERNAL_OR_RETENTION_FAILURE')
        finally:
            if self.active is not None:
                self._close_socket(self.active); self.active = None
            if self.listener is not None:
                self._close_socket(self.listener)

    def close(self):
        self.stop_event.set()
        handles = [self.active, self.listener, *self.closed_sockets]
        for handle in handles:
            if handle is not None:
                try:
                    handle.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self._close_socket(handle)
        if self.thread is not None and self.started:
            self.thread.join(timeout=6)
        self.joined = self.started and self.thread is not None and not self.thread.is_alive()
        closed = self.listener is not None and self.listener.fileno() == -1 and self.active is None and \
                 all(handle.fileno() == -1 for handle in self.closed_sockets)
        return {'started': self.started, 'thread_joined': self.joined,
                'all_owned_sockets_closed': closed, 'verified': self.started and self.joined and closed,
                'request_count': len(self.rows), 'semantic_request_count': self.messages,
                'captured_request_bytes': self.total_bytes, 'semantic_response_complete': self.response_complete,
                'failure': self.failure, 'supplemental_failures': list(self.supplemental_failures),
                'semantic_request_index': self.semantic_index}


def body_witness(request_raw, governor_raw, operation_id):
    request = strict_json(request_raw)
    need(type(request) is dict and type(request.get('messages')) is list,
         'REQUEST_MESSAGES_UNRECEIVED')
    need(governor_raw.startswith(b'---\n') and governor_raw.count(b'\n---\n') >= 1,
         'GOVERNOR_FRONTMATTER_SHAPE_REFUSED')
    body = governor_raw.split(b'\n---\n', 1)[1].strip(b'\n')
    need(body and b'$ARGUMENTS' not in body and b'${CLAUDE_' not in body and b'!`' not in body,
         'DYNAMIC_GOVERNOR_BODY_UNREVIEWED')
    body_text = body.decode('utf-8'); matches = []; nonce_seen = False
    for i, message in enumerate(request['messages']):
        need(type(message) is dict, 'REQUEST_MESSAGE_SHAPE_UNRECEIVED')
        if message.get('role') != 'user':
            continue
        content = message.get('content')
        blocks = [{'type': 'text', 'text': content}] if type(content) is str else content
        need(type(blocks) is list, 'REQUEST_USER_CONTENT_UNRECEIVED')
        for j, block in enumerate(blocks):
            need(type(block) is dict, 'REQUEST_BLOCK_UNRECEIVED')
            if block.get('type') != 'text':
                continue
            text = block.get('text'); need(type(text) is str, 'REQUEST_TEXT_UNRECEIVED')
            nonce_seen = nonce_seen or ('DG17_OPERATION_ID=' + operation_id) in text
            need(text.count(body_text) <= 1, 'DUPLICATE_BODY_DELIVERY_UNRECEIVED')
            if body_text in text:
                at = text.index(body_text); start = len(text[:at].encode('utf-8'))
                matches.append({'message_index': i, 'content_index': j,
                    'content_was_string': type(content) is str, 'utf8_start': start,
                    'utf8_end': start + len(body), 'body_bytes': len(body), 'body_sha256': digest(body)})
    need(nonce_seen, 'REQUEST_OPERATION_ID_MISSING')
    need(len(matches) == 1, 'EXACT_NATIVE_GOVERNOR_BODY_UNRECEIVED')
    return {'status': 'EXACT_CLIENT_USER_MESSAGE_BODY_OBSERVED',
            'source_file_bytes': len(governor_raw), 'source_file_sha256': digest(governor_raw),
            'normalization': 'REMOVE_YAML_FRONTMATTER_AND_TRIM_EDGE_LF_ONLY', **matches[0]}


def native_projection(raw, session_id, cwd, plugin):
    need(type(raw) is bytes and 0 < len(raw) <= 32768, 'NATIVE_EVENT_BYTE_BOUND')
    lines = raw.splitlines(); need(0 < len(lines) <= 128 and all(lines), 'NATIVE_EVENT_POPULATION_BOUND')
    events = [strict_json(line, 32768) for line in lines]
    need(all(type(x) is dict and x.get('type') in ('system', 'user', 'assistant', 'result') for x in events),
         'NATIVE_EVENT_TYPE_UNRECEIVED')
    need(all(x.get('session_id') == session_id for x in events), 'NATIVE_SESSION_ID_DIFFERS')
    need(not any(x.get('parent_tool_use_id') is not None for x in events), 'UNPLANNED_CHILD_EVENT')
    inits = [(i, x) for i, x in enumerate(events) if x.get('type') == 'system' and x.get('subtype') == 'init']
    results = [(i, x) for i, x in enumerate(events) if x.get('type') == 'result']
    need(len(inits) == len(results) == 1 and inits[0][0] < results[0][0] == len(events) - 1,
         'NATIVE_INIT_RESULT_ORDER_UNRECEIVED')
    init = inits[0][1]; result = results[0][1]
    need(init.get('cwd') == str(cwd) and init.get('model') == MODEL_SELECTOR,
         'NATIVE_CONFIG_IDENTITY_DIFFERS')
    tools = init.get('tools')
    need(type(tools) is list and all(type(x) is str for x in tools) and
         len(tools) == len(set(tools)) and 'Skill' in tools and
         all(x in ('Skill', 'EndConversation') for x in tools), 'NATIVE_TOOL_SURFACE_DIFFERS')
    need(init.get('mcp_servers') == [] and init.get('mcp_server_errors', []) == [] and
         init.get('plugin_errors', []) == [], 'NATIVE_STARTUP_ERROR_OR_MCP_PRESENT')
    need(init.get('plugins') == [{'name': 'implementaudit', 'path': str(plugin)}],
         'NATIVE_PLUGIN_PATH_UNRECEIVED')
    skills = init.get('skills')
    need(type(skills) is list and len(skills) <= 128 and all(type(x) is str and len(x) <= 256 for x in skills)
         and len(skills) == len(set(skills)), 'NATIVE_SKILLS_SHAPE_UNRECEIVED')
    selected = sorted(x for x in skills if x.startswith('implementaudit:'))
    others = sorted(x for x in skills if not x.startswith('implementaudit:'))
    expected_present = [x for x in EXPECTED_NAMES if x in selected]
    unexpected = [x for x in selected if x not in EXPECTED_NAMES]
    assistant = []
    for event in events:
        if event.get('type') == 'system':
            need(event.get('subtype') == 'init', 'NATIVE_SYSTEM_SUBTYPE_UNRECEIVED')
        if event.get('type') not in ('user', 'assistant'):
            continue
        message = event.get('message'); need(type(message) is dict, 'NATIVE_MESSAGE_SHAPE_UNRECEIVED')
        content = message.get('content'); content = [{'type': 'text', 'text': content}] if type(content) is str else content
        need(type(content) is list and all(type(x) is dict and x.get('type') == 'text' and
             type(x.get('text')) is str for x in content), 'UNPLANNED_NATIVE_TOOL_OR_NON_TEXT_BLOCK')
        if event['type'] == 'assistant': assistant.append(''.join(x['text'] for x in content))
    need(assistant == [ACK] and result.get('subtype') == 'success' and result.get('is_error') is False
         and result.get('result') == ACK and result.get('permission_denials', []) == [],
         'NATIVE_TERMINAL_RESPONSE_UNRECEIVED')
    return {'status': 'NATIVE_INIT_AND_TERMINAL_RECEIVED', 'event_count': len(events),
        'session_id_sha256': digest(session_id.encode('ascii')), 'plugin_path_matches_effective': True,
        'canonical_advertised_entries_exact': selected == sorted(EXPECTED_NAMES),
        'expected_names_observed': expected_present, 'unexpected_package_entry_count': len(unexpected),
        'unexpected_package_names_sha256': digest(canonical(unexpected)),
        'other_skill_count': len(others), 'other_skill_names_sha256': digest(canonical(others)),
        'native_tool_calls': 0, 'child_events': 0, 'terminal_success': True,
        'runtime_version_label_matches': init.get('claude_code_version') == '2.1.318'}
