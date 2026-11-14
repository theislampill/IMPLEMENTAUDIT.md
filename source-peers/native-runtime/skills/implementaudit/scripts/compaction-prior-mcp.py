#!/usr/bin/env python3
"""Proposed closed seven-call mechanical tool. Run only after root integration/GO.

This file creates no selection, subject, store, grant, compaction, RETURN or JOIN.
The source owner must already select the separate mechanical profile. Its fixed
pending owner and code-pinned script execute the actual operations. Provider
content remains deterministic emulation, not independent cognition.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
import types

PROFILE = 'codex-app-server-0.166.0-linux-prior-mechanical-v1'
SEQUENCE = ('LOAD', 'DELIVER', 'BIND', 'BIND', 'LOAD', 'DELIVER', 'BIND')
MAX_BYTES = 256 * 1024
# DELIVER/BIND owner worker bound, unchanged at 30s like LOAD. The worker runs in its
# own session so that its whole process group is killed on timeout and after exit.
# A watcher in that group kills it as well when this server dies for any reason.
# A fired bound leaves the owner effect UNKNOWN and closes the sequence; nothing is retried.
OWNER_SECONDS = 30
REAP_SECONDS = 2
OUTPUT_BYTES = 128 * 1024


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_bytes(pin, maximum=MAX_BYTES):
    path = Path(pin['path'])
    require(path.is_absolute() and path.resolve(strict=True) == path, 'TOOL_PIN_PATH_ALIAS')
    info = path.stat()
    require(info.st_nlink == 1 and 0 < info.st_size == pin['bytes'] <= maximum, 'TOOL_PIN_BYTE_BOUND')
    raw = path.read_bytes()
    require(len(raw) == pin['bytes'] and sha(raw) == pin['sha256'], 'TOOL_PIN_CHANGED')
    return raw


def load_module(path, raw):
    module = types.ModuleType('_mechanical_' + Path(path).stem.replace('-', '_'))
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def schema():
    return {'name': 'observe_prior',
            'description': 'Closed native mechanical LOAD or exact existing pending-owner deliver/bind; no RETURN/JOIN, no cognition claim.',
            'annotations': {'readOnlyHint': False, 'destructiveHint': False,
                            'idempotentHint': False, 'openWorldHint': False},
            'inputSchema': {'type': 'object', 'properties': {
                'selection_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
                'operation': {'type': 'string', 'enum': ['LOAD', 'DELIVER', 'BIND']},
                'request_json': {'type': 'string', 'maxLength': 131072}},
                'required': ['selection_sha256', 'operation', 'request_json'], 'additionalProperties': False}}


def owner_guard(watch, argv):
    """Become the exact owner argv after leaving a watcher in this process group.

    The watcher holds the read end of a pipe whose only write end the server holds.
    When that end closes, including by the death of the server, the watcher kills
    its own whole process group. This process then executes argv in place, so the
    worker keeps the pid, parent, session and group the server gave it.
    """
    os.set_inheritable(watch, False)
    middle = os.fork()
    if middle == 0:
        status = 1
        try:
            if os.fork() == 0:
                try:
                    null = os.open(os.devnull, os.O_RDWR)
                    for stream in (0, 1, 2):
                        os.dup2(null, stream)
                    os.close(null)
                    os.read(watch, 1)
                finally:
                    os.killpg(0, signal.SIGKILL)
            status = 0
        finally:
            os._exit(status)
    require(os.waitpid(middle, 0)[1] == 0, 'MECHANICAL_OWNER_WATCHER_REQUIRED')
    for name in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), signal.SIG_DFL)
    os.execv(argv[0], argv)


def owner_worker(argv, request, environment):
    """Run the exact owner argv in its own session under OWNER_SECONDS.

    The leader is only observed (never reaped) until its whole process group has
    been killed, so the group id cannot name another process. Only this server
    holds the write end of the watch pipe; see owner_guard.
    """
    watch, hold = os.pipe()
    try:
        child = subprocess.Popen([argv[0], '-I', '-S', '-B', str(Path(__file__).resolve()), '--owner-guard', str(watch)] + argv,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env=environment, close_fds=True, start_new_session=True, pass_fds=(watch,))
    except BaseException:
        os.close(hold)
        raise
    finally:
        os.close(watch)
    deadline = time.monotonic() + OWNER_SECONDS
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    selector = selectors.DefaultSelector()
    written = 0
    state = 'TIMEOUT'
    try:
        for stream, role in ((child.stdin, 'stdin'), (child.stdout, 'stdout'), (child.stderr, 'stderr')):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_WRITE if role == 'stdin' else selectors.EVENT_READ, role)
        while selector.get_map() and state == 'TIMEOUT':
            left = deadline - time.monotonic()
            if left <= 0:
                break
            for key, _ in selector.select(min(left, .05)):
                stream, role = key.fileobj, key.data
                if role == 'stdin':
                    try:
                        written += os.write(stream.fileno(), request[written:written + 65536])
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        written = len(request)
                    if written >= len(request):
                        selector.unregister(stream)
                        stream.close()
                    continue
                try:
                    block = os.read(stream.fileno(), 16384)
                except BlockingIOError:
                    continue
                if not block:
                    selector.unregister(stream)
                    stream.close()
                    continue
                streams[role].extend(block)
                if len(streams['stdout']) + len(streams['stderr']) > OUTPUT_BYTES:
                    state = 'OUTPUT'
                    break
        while state == 'TIMEOUT' and not selector.get_map():
            if os.waitid(os.P_PID, child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None:
                state = 'EXITED'
            elif time.monotonic() >= deadline:
                break
            else:
                time.sleep(.01)
    finally:
        selector.close()
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            child.wait(timeout=REAP_SECONDS)
        except subprocess.TimeoutExpired:
            state = 'TIMEOUT'
        for stream in (child.stdin, child.stdout, child.stderr):
            with contextlib.suppress(OSError):
                stream.close()
        os.close(hold)
    require(state != 'OUTPUT', 'MECHANICAL_CHILD_OUTPUT_BOUND')
    if state != 'EXITED':
        raise subprocess.TimeoutExpired(argv, OWNER_SECONDS)
    return subprocess.CompletedProcess(['observe-child'], child.returncode,
                                       bytes(streams['stdout']), bytes(streams['stderr']))


class ClosedSequence:
    """Finite scheduling constraint; it supplies no observation or authority."""
    def __init__(self):
        self.count = 0
        self.failed = False
        self.first_bind = None
        self.observation_p = None
        self.observation_c = None
        self.child_id = None
        self.selection_sha256 = None

    def check(self, operation, request, child):
        require(not self.failed and self.count < len(SEQUENCE)
                and operation == SEQUENCE[self.count], 'CLOSED_MECHANICAL_SEQUENCE')
        require(self.child_id in (None, child), 'CLOSED_MECHANICAL_CHILD_CHANGED')
        self.child_id = child
        if operation == 'LOAD':
            require(set(request) == {'path', 'bytes', 'sha256'}, 'CLOSED_LOAD_PIN_SHAPE')
        else:
            expected = {'child_id', 'phase', 'observation_id',
                        'authorization_evidence' if operation == 'DELIVER' else 'exchange'}
            require(set(request) == expected and request['child_id'] == child
                    and request['phase'] == operation.lower(), 'CLOSED_PENDING_OPERATION')
            if self.count == 1:
                self.observation_p = request['observation_id']
            if self.count in (2, 3):
                require(request['observation_id'] == self.observation_p, 'PRIOR_OBSERVATION_CHANGED')
            if self.count == 2:
                self.first_bind = json.dumps(request, sort_keys=True)
            if self.count == 3:
                require(json.dumps(request, sort_keys=True) == self.first_bind, 'EXACT_BIND_RETRY_REQUIRED')
            if self.count == 5:
                self.observation_c = request['observation_id']
                require(self.observation_c != self.observation_p, 'LATER_OBSERVATION_REQUIRED')
            if self.count == 6:
                require(request['observation_id'] == self.observation_c, 'CURRENT_OBSERVATION_CHANGED')

    def complete(self, exit_code):
        self.count += 1
        self.failed = exit_code != 0


def tool_call(source_path, arguments, metadata, sequence):
    # Root launches this exact admitted script through the pinned native config.
    # Selection comes from the existing owner, never from tool arguments.
    require(source_path.name == 'compaction-source-owner-codex-app.py'
            and source_path.parent == Path(__file__).resolve().parent, 'FIXED_SOURCE_OWNER_REQUIRED')
    raw = source_path.read_bytes()
    require(0 < len(raw) <= MAX_BYTES, 'SOURCE_OWNER_BOUND')
    source = load_module(source_path, raw)
    selected = source._np_selection()
    require(selected['profile_id'] == PROFILE and source.MECHANICAL_SELECTION_PIN is not None,
            'MECHANICAL_SOURCE_NOT_SELECTED')
    pins = selected['mechanical_tool']
    require(checked_bytes(pins['server_pin']) == Path(__file__).read_bytes(), 'MECHANICAL_SERVER_CODE_CHANGED')
    protocol = load_module(pins['protocol_pin']['path'], checked_bytes(pins['protocol_pin']))
    checked_bytes(pins['python_pin'], 32 * 1024 * 1024)
    require(Path(sys.executable).resolve(strict=True) == Path(pins['python_pin']['path']),
            'MECHANICAL_PYTHON_SELECTION_CHANGED')
    require(arguments['selection_sha256'] == source.MECHANICAL_SELECTION_PIN['sha256'], 'MECHANICAL_SELECTION_CHANGED')
    require(type(arguments) is dict and set(arguments) ==
            {'selection_sha256', 'operation', 'request_json'}, 'CLOSED_MCP_ARGUMENTS')
    request = protocol.parse(arguments['request_json'])
    args = protocol.arguments(arguments['selection_sha256'], arguments['operation'], request)
    require(args == arguments, 'CLOSED_MCP_ARGUMENTS')
    require(sequence.selection_sha256 in (None, args['selection_sha256']), 'CLOSED_MECHANICAL_SELECTION_CHANGED')
    sequence.selection_sha256 = args['selection_sha256']
    pending_path = source_path.with_name('compaction-audit-pending.py')
    pending = load_module(pending_path, pending_path.read_bytes())
    fixed = selected['pending_owner']
    state = pending.load(Path(fixed['store']), fixed['session_id'])
    require(type(metadata) is dict and type(metadata.get('threadId')) is str,
            'MECHANICAL_NATIVE_TOOL_METADATA')
    assignment = state['assignments'].get(metadata['threadId'])
    require(type(assignment) is dict
            and assignment.get('observation_source', {}).get('profile_id') == PROFILE
            and assignment['observation_source'].get('_mechanical_selection_sha256') == args['selection_sha256'],
            'EXACT_MECHANICAL_ASSIGNMENT_REQUIRED')
    require(assignment['code'] == pending.nonprotected_code_identity()
            and assignment['return'] is None and assignment['join'] is None,
            'MECHANICAL_CODE_OR_LIFECYCLE_CHANGED')
    actual = protocol.tool_metadata(metadata, fixed['session_id'], assignment['child_id'])
    context = assignment['observation_source']
    observation = pending.OBSERVATION
    with source.nonprotected_sources_guard(observation._nonprotected_observation_view(), context, assignment['code']):
        records, _ = observation.hold_records(context)
    calls = [r for r in records if r['row']['payload'].get('call_id') == actual['call_id']]
    require(len(calls) == 1 and protocol.call_input(calls[0]['row']['payload']) == protocol.arguments_wire(args)
            and calls[0]['row']['payload'].get('id') == actual['item_id']
            and calls[0]['row']['payload'].get('internal_chat_message_metadata_passthrough', {}).get('turn_id') == actual['turn_id'],
            'MECHANICAL_ACTUAL_PENDING_NATIVE_CALL_REQUIRED')
    operation = args['operation']
    sequence.check(operation, request, assignment['child_id'])
    if operation == 'LOAD':
        require(request == pending.selected_audit_state_pin(), 'EXACT_SELECTED_SKILL_REQUIRED')
        argv = [pins['python_pin']['path'], '-I', '-S', '-B', str(Path(__file__).resolve()), '--load-worker']
    else:
        argv = [pins['python_pin']['path'], '-I', '-S', '-B', str(pending_path),
                '--store', fixed['store'], '--session', fixed['session_id'],
                '--owner-id', fixed['owner_id'], 'observe-child']
    custody = source.selected_custody_v1(selected)
    skills_root = source_path.parent.parent.parent
    with contextlib.ExitStack() as held:
        for key in sorted(assignment['code']):
            held.enter_context(custody.held_file(skills_root / key, allow_append=False))
        held.enter_context(custody.held_file(pins['python_pin']['path'], allow_append=False))
        held.enter_context(custody.held_file(pins['config_pin']['path'], allow_append=False))
        environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}
        if operation == 'LOAD':
            child = subprocess.run(argv, input=protocol.canonical(request), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, timeout=30, check=False, env=environment)
        else:
            child = owner_worker(argv, protocol.canonical(request), environment)
        require(pending.nonprotected_code_identity() == assignment['code'], 'MECHANICAL_CODE_CHANGED_DURING_CALL')
    require(len(child.stdout) + len(child.stderr) <= 128 * 1024, 'MECHANICAL_CHILD_OUTPUT_BOUND')
    sequence.complete(child.returncode)
    stdout = child.stdout.decode('utf-8', errors='strict')
    receipt = {'schema': protocol.RESPONSE, 'selection_sha256': args['selection_sha256'],
               'operation': operation, 'request_sha256': sha(args['request_json'].encode('utf-8')),
               'exit_code': child.returncode, 'stdout': stdout, 'stdout_sha256': sha(child.stdout),
               'stderr_sha256': sha(child.stderr)}
    return {'isError': child.returncode != 0,
            'content': [{'type': 'text', 'text': protocol.canonical(receipt).decode('utf-8')}]}


def main():
    if sys.argv[1:2] == ['--owner-guard']:
        owner_guard(int(sys.argv[2]), sys.argv[3:])
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-owner', type=Path)
    parser.add_argument('--load-worker', action='store_true')
    args = parser.parse_args()
    if args.load_worker:
        require(args.source_owner is None, 'LOAD_WORKER_SCOPE')
        pin = json.loads(sys.stdin.buffer.read(MAX_BYTES + 1))
        raw = checked_bytes(pin, 128 * 1024)
        print(json.dumps({**pin, 'utf8': raw.decode('utf-8')}, sort_keys=True), flush=True)
        return
    require(args.source_owner is not None, 'FIXED_SOURCE_OWNER_REQUIRED')
    sequence = ClosedSequence()
    for wire in sys.stdin.buffer:
        require(len(wire) <= MAX_BYTES, 'MCP_REQUEST_BOUND')
        message = json.loads(wire)
        if 'id' not in message:
            continue
        method = message.get('method')
        if method == 'initialize':
            result = {'protocolVersion': message.get('params', {}).get('protocolVersion', '2024-11-05'),
                      'capabilities': {'tools': {}},
                      'serverInfo': {'name': 'dg18-prior-mechanical', 'version': 'candidate-v1'}}
        elif method == 'tools/list':
            result = {'tools': [schema()]}
        elif method == 'ping':
            result = {}
        elif method == 'tools/call':
            try:
                params = message['params']
                require(set(params) == {'name', 'arguments', '_meta'} and params['name'] == 'observe_prior', 'CLOSED_MCP_TOOL_REQUIRED')
                result = tool_call(args.source_owner.resolve(strict=True), params['arguments'], params['_meta'], sequence)
            except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
                sequence.failed = True
                result = {'isError': True, 'content': [{'type': 'text', 'text': 'MECHANICAL_REFUSED:' + type(exc).__name__ + ':' + str(exc)[:256]}]}
        else:
            result = {'isError': True, 'content': [{'type': 'text', 'text': 'CLOSED_MCP_METHOD_REQUIRED'}]}
        print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}), flush=True)


if __name__ == '__main__':
    main()
