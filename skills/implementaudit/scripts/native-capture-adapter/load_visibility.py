"""Prospective capture adapter. No process creation, route or stage authority.

The existing pinned capture owns send/response, closed notification grammar,
raw streams, deadlines, process identity and containment. This adapter supplies
the missing pause/relay/ACK/second-turn edge. All errors escape to that owner's
existing containment finally. Never resume a disposed process or recreate a turn.
"""
import copy
import shlex
import hashlib
import re
import json
import os
import time
from pathlib import Path, PureWindowsPath


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def publish_once(path, raw):
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


class StagedProtocol:
    """Two monitors of the retained CanaryProtocol; one native thread binding.

    The capture's closed NotificationPolicy still runs BEFORE observe. Request
    IDs 5 and 6 are real distinct native IDs; normalization only feeds the old
    one-turn monitor's fixed local request guard. Prior snapshots stay intact.
    """
    def __init__(self, protocol_type, load_spec):
        self.protocol_type = protocol_type
        self.active = protocol_type()
        self.load_spec = copy.deepcopy(load_spec)
        self.phase = 'LOAD'
        self.load_snapshot = None
        self.release_digest = None
        self.code_mode = self.load_spec.get('code_mode')
        if self.code_mode is not None:
            require(type(self.code_mode) is dict and set(self.code_mode)=={'LOAD','USE'}, 'Exact two-phase code-mode selection required')
            self.active.bind_code_mode(self.code_mode['LOAD'])
            self.active.bind_context_contract(self.load_spec.get('context_contract'),'LOAD')

    def __getattr__(self, name):
        return getattr(self.active, name)

    def register_turn(self, request):
        expected = 5 if self.phase == 'LOAD' else 6
        require(request.get('id') == expected, 'Unreleased, duplicate or foreign turn request')
        normalized = copy.deepcopy(request)
        normalized['id'] = 5
        self.active.register_turn(normalized)

    def response(self, message):
        self.active.response(message)
        if self.phase=='USE' and self.active.turn_id==self.load_snapshot['turn_id']:
            self.active.fail('USE reused the consumed LOAD turn identity')

    @staticmethod
    def require_final_answer_phase(item):
        # Native MessagePhase: commentary is an item inside a turn, not a
        # terminal answer. This selected provider contract requires known phase.
        phase = item.get('phase')
        require(type(phase) is str and phase in ('commentary', 'final_answer'),
                'LOAD agent message phase is missing or unknown')
        require('channel' not in item, 'Unsupported or conflicting native LOAD phase label')
        require(phase == 'final_answer',
                'Unexpected nonterminal LOAD agent message; silent LOAD required')

    def validate_load_agent_text(self, identity):
        """Bind public start/deltas/completion using the retained item history.

        Complete-only delivery starts empty or with the full token. Streaming
        may start with a token prefix, then nonempty ordered deltas reconstruct
        the complete token. No later completed field erases observed prose.
        """
        row = self.active.items.get(identity)
        if row is None or row['started'].get('type') != 'agentMessage':
            self.active.fail('LOAD public text delta targets a non-agent item')
        expected = self.active.code_mode['terminal_text'] if self.active.code_mode else self.load_spec['ready_text']
        text = row['started'].get('text')
        if type(text) is not str or not expected.startswith(text):
            self.active.fail('LOAD started public text differs from readiness token')
        streamed = False
        for frame in self.active._protocol_frames:
            if frame.get('method') != 'item/agentMessage/delta':
                continue
            params = frame['params']
            if params['itemId'] != identity:
                continue
            part = params['delta']
            if type(part) is not str or not part or len(part) > len(expected) - len(text):
                self.active.fail('LOAD public text delta is empty, malformed or exceeds readiness')
            text += part
            if not expected.startswith(text):
                self.active.fail('LOAD ordered public text differs from readiness token')
            streamed = True
        if row['completed'] is not None:
            if row['completed'].get('text') != expected:
                self.active.fail('LOAD completed public text differs from readiness token')
            if (streamed and text != expected) or (not streamed and text not in ('', expected)):
                self.active.fail('LOAD observed public text does not reconstruct complete readiness')

    def observe(self, message):
        self.active._current_diagnostic=None
        try:
            require(type(message) is dict, 'Malformed notification envelope')
            self._observe(message)
        except ValueError as exc:
            if self.active._current_diagnostic is None and len(self.active.frames)<512:
                try:self.active._record_diagnostic(message)
                except (TypeError,ValueError):pass
            self.active.fail(str(exc))
        self.active.publish_diagnostic(message)

    def _observe(self, message):
        if self.phase=='USE' and self.code_mode:
            params=message.get('params',{})
            if type(params) is not dict or ('item' in params and type(params['item']) is not dict) or ('turn' in params and type(params['turn']) is not dict):
                self.active.fail('Malformed USE item/turn envelope')
            item=params.get('item',{})
            old=self.load_snapshot['code_mode_custody']
            if (params.get('turn',{}).get('id')==self.load_snapshot['turn_id'] or
                    (message.get('method')=='rawResponse/completed' and params.get('responseId') in old['responses']) or
                    (item.get('type') in ('custom_tool_call','custom_tool_call_output') and item.get('call_id')==old['call']['call_id']) or
                    (item.get('id') is not None and any(row['raw_item_id']==item['id']
                        for row in self.load_snapshot.get('context',{}).get('observed',[])))):
                self.active.fail('USE reused consumed LOAD turn/call/response custody')
        guarded_phase = self.phase == 'LOAD' or self.active.code_mode is not None
        current_spec = self.active.code_mode or self.load_spec
        terminal_text = current_spec.get('terminal_text', self.load_spec['ready_text'])
        public_delta = guarded_phase and message.get('method') == 'item/agentMessage/delta'
        if public_delta:
            params = message.get('params')
            if (type(params) is not dict or set(params) != {'threadId', 'turnId', 'itemId', 'delta'} or
                    any(type(params[key]) is not str for key in params) or
                    not all(params[key] for key in ('threadId', 'turnId', 'itemId'))):
                self.active.fail('Malformed native LOAD public text delta identity or fields')
        if guarded_phase and message.get('method') in ('item/started', 'item/completed'):
            item = message.get('params', {}).get('item', {})
            kind = item.get('type')
            allowed = ('userMessage', 'agentMessage', 'reasoning', 'commandExecution')
            if self.active.code_mode: allowed += ('functionCallOutput',)
            require(kind in allowed,
                    'Early USE or unreviewed LOAD item route')
            if kind == 'agentMessage':
                self.require_final_answer_phase(item)
            if kind == 'commandExecution':
                try:
                    observed_argv = shlex.split(item.get('command', ''), posix=True)
                except ValueError:
                    observed_argv = None
                expected_argv = current_spec['expected_argv']
                exact_command = (isinstance(observed_argv, list) and len(observed_argv) == len(expected_argv) and
                    '..' not in PureWindowsPath(observed_argv[0]).parts and
                    PureWindowsPath(observed_argv[0]) == PureWindowsPath(expected_argv[0]) and
                    observed_argv[1:] == expected_argv[1:])
                require(exact_command and
                        item.get('cwd') == current_spec['cwd'], 'Early USE: non-LOAD executable/argv/cwd')
            if kind == 'agentMessage' and message['method'] == 'item/completed':
                require(item.get('text') == terminal_text,
                        'Unexpected final LOAD readiness text')
        self.active.observe(message,publish=False)
        if public_delta:
            self.validate_load_agent_text(message['params']['itemId'])
        elif (guarded_phase and message.get('method') in ('item/started', 'item/completed') and
                message['params']['item']['type'] == 'agentMessage'):
            self.validate_load_agent_text(message['params']['item']['id'])

    def qualify_load(self):
        if self.phase != 'LOAD' or not self.active.transport_complete():
            self.active.fail(self.active.first_anomaly or 'Incomplete LOAD turn')
        items = [r['completed'] for r in self.active.items.values()]
        commands = [i for i in items if i['type'] == 'commandExecution']
        messages = [i for i in items if i['type'] == 'agentMessage']
        require(len(commands) == 1 and len(messages) == 1, 'Missing/duplicate actual LOAD command or readiness')
        command = commands[0]
        require(command.get('status') == 'completed' and command.get('exitCode') == 0,
                'Actual LOAD command failed')
        require(command.get('aggregatedOutput') == self.load_spec['expected_output'],
                'Actual LOAD output differs from adopted source/OPEN bytes')
        self.require_final_answer_phase(messages[0])
        require(messages[0].get('text') == self.load_spec['ready_text'], 'Missing matching final-answer readiness')
        self.validate_load_agent_text(messages[0]['id'])
        ordered = list(self.active.items)
        require(ordered.index(command['id']) < ordered.index(messages[0]['id']), 'Readiness before actual LOAD')
        completed_at = [n for n, frame in enumerate(self.active._protocol_frames)
                        if frame.get('method') == 'item/completed' and
                        frame.get('params', {}).get('item', {}).get('id') == command['id']]
        ready_started_at = [n for n, frame in enumerate(self.active._protocol_frames)
                            if frame.get('method') == 'item/started' and
                            frame.get('params', {}).get('item', {}).get('id') == messages[0]['id']]
        require(len(completed_at) == len(ready_started_at) == 1 and completed_at[0] < ready_started_at[0],
                'Readiness did not follow completed actual LOAD command')
        self.load_snapshot = copy.deepcopy(self.active.snapshot())
        evidence = {'command_item_id': command['id'], 'model_ready_item_id': messages[0]['id'],
                    'turn_id': self.active.turn_id, 'snapshot_sha256': digest(encode(self.load_snapshot))}
        if self.active.code_mode: evidence['code_mode'] = self.active.code_mode_evidence()
        return evidence

    def release(self, ready_digest, use_settings):
        if self.phase != 'LOAD' or self.load_snapshot is None or self.release_digest is not None:
            self.active.fail(self.active.first_anomaly or 'Duplicate or premature USE release')
        old = self.active
        if not old.transport_complete() or old.first_anomaly is not None:
            old.fail(old.first_anomaly or 'Failed or incomplete LOAD cannot release USE')
        old.require_context_complete()
        if not isinstance(use_settings, dict) or use_settings.get('activePermissionProfile') != {'id':'worker_use','extends':None}:
            old.fail('Exact USE settings binding unavailable')
        selected = self.protocol_type()
        selected.bind_thread(old.thread_id)
        selected.expected_settings = copy.deepcopy(use_settings)
        try:
            if self.code_mode is not None:
                selected.bind_code_mode(self.code_mode['USE'])
                selected.bind_context_contract(self.load_spec['context_contract'],'USE')
                require(selected.context_contract_sha256==old.context_contract_sha256,'Context contract changed after LOAD')
        except Exception:
            old.fail('USE code/context selection differs from verified LOAD')
        self.active = selected
        self.release_digest = ready_digest
        self.phase = 'USE'

    def snapshot(self):
        return {'phase': self.phase, 'load': self.load_snapshot,
                'release_digest': self.release_digest, 'active': self.active.snapshot()}


ISOLATED_QUALIFICATION = 'ISOLATED_QUALIFICATION'


def isolated_identity(identity):
    require(isinstance(identity, dict) and 'selected_child' in identity and identity['selected_child'] is None,
            'Isolated qualification cannot select a governed child')
    logical = identity.get('logical_task')
    require(isinstance(logical, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', logical),
            'Isolated qualification requires a stable logical task')
    for key in ('parent_thread_id', 'transaction_ref'):
        value = identity.get(key)
        require(isinstance(value, str) and 0 < len(value) <= 240 and value == value.strip() and
                not any(ord(char) < 32 or ord(char) == 127 for char in value),
                'Isolated qualification custody identity missing or malformed')
    source = identity.get('source_sha256')
    require(isinstance(source, str) and re.fullmatch(r'[0-9a-f]{64}', source),
            'Isolated qualification source digest missing')
    reason = identity.get('reason')
    require(isinstance(reason, str) and 0 < len(reason) <= 240 and reason == reason.strip() and
            not any(ord(char) < 32 or ord(char) == 127 for char in reason) and not reason.endswith('.') and
            'CHILD_SKILL_ROUTE' not in reason and "I'm using" not in reason,
            'Isolated qualification requires one truthful bounded reason')
    return logical, reason


def validate_isolated_qualification_plan(plan):
    require(isinstance(plan, dict) and plan.get('purpose') == ISOLATED_QUALIFICATION,
            'Exact isolated qualification purpose required')
    require('governor_dispatch' not in plan, 'Isolated qualification cannot carry governed dispatch')
    cfg = plan.get('visibility')
    require(isinstance(cfg, dict), 'Isolated qualification visibility binding missing')
    isolated_identity(cfg.get('identity'))
    source = plan.get('binding', {}).get('load_pins', {}).get('child_source', {})
    require(cfg['identity']['source_sha256'] == source.get('sha256'),
            'Isolated qualification source differs from exact LOAD input')
    return cfg


def isolated_qualification_marker(ready, ready_sha):
    require(ready.get('purpose') == ISOLATED_QUALIFICATION,
            'Unknown qualification presentation purpose')
    logical, reason = isolated_identity(ready.get('identity'))
    worker = ready.get('worker_thread_id')
    require(isinstance(worker, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', worker),
            'Isolated qualification worker identity missing')
    process = ready.get('process_identity')
    require(isinstance(process, dict) and type(process.get('pid')) is int and process['pid'] > 0 and
            type(process.get('creation_filetime_100ns')) is int and process['creation_filetime_100ns'] > 0,
            'Isolated qualification PID and birth identity missing')
    prefixes = ready.get('raw_prefix')
    require(isinstance(prefixes, list) and len(prefixes) == 3 and
            all(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'} and
                isinstance(row['path'], str) and type(row['bytes']) is int and row['bytes'] >= 0 and
                isinstance(row['sha256'], str) and re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
                for row in prefixes) and
            {Path(row['path']).name for row in prefixes} == {'stdout.bin', 'stderr.bin', 'sent.jsonl'},
            'Isolated qualification raw prefix binding missing')
    require('semantic_verdict' in ready and ready['semantic_verdict'] is None and
            'owner_stage_receipt' in ready and ready['owner_stage_receipt'] is None,
            'Isolated qualification READY cannot carry authority')
    require(digest(encode(ready)) == ready_sha, 'LOAD_READY digest does not bind the exact delivery tuple')
    return ('```ini\nISOLATED_QUALIFICATION=LOAD_READY\nLOGICAL_TASK=' + logical +
            '\nWORKER_TASK=' + worker + '\nSOURCE_SHA256=' + ready['identity']['source_sha256'] +
            '\nPROCESS_PID=' + str(process['pid']) +
            '\nPROCESS_BIRTH_FILETIME_100NS=' + str(process['creation_filetime_100ns']) +
            '\nLOAD_READY_SHA256=' + ready_sha + '\n```\n' +
            'The isolated qualification task ' + logical + ' has loaded the bound source to ' + reason + '.')


def is_parent_commentary_message(payload):
    """Current phase and legacy channel must agree when both are supplied."""
    if (not isinstance(payload, dict) or payload.get('type') != 'message' or
            payload.get('role') != 'assistant'):
        return False
    labels = [payload[key] for key in ('phase', 'channel') if key in payload]
    return bool(labels) and all(value == 'commentary' for value in labels)


def normal_logical_task(identity, worker=None):
    logical = identity.get('logical_task') if isinstance(identity, dict) else None
    require(isinstance(logical, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', logical),
            'Governed visibility requires the bound stable logical task')
    require(logical not in ('audit-state', 'audit-assess', 'audit-andon', 'audit-implement') and
            not re.fullmatch(r'[0-9a-f]{32,64}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', logical),
            'Logical task cannot be a reserved skill, digest or physical UUID')
    require(logical not in (identity.get('selected_child'), identity.get('parent_thread_id'),
                            identity.get('transaction_ref'), worker),
            'Logical task cannot substitute a skill, transaction or physical identity')
    return logical


def marker_for(ready, ready_sha):
    """Canonical product announcement plus exact existing delivery custody.

    The normal event names its canonical logical task separately from physical
    worker custody. The READY digest retains source/process/transaction/LOAD
    evidence; formatting does not replace the caller's actual LOAD verification.
    """
    if 'purpose' in ready:
        return isolated_qualification_marker(ready, ready_sha)
    identity = ready['identity']
    child, reason = identity['selected_child'], identity['reason']
    require(child in ('audit-state', 'audit-assess', 'audit-andon', 'audit-implement'),
            'Announcement selected child is not a governed skill')
    logical = normal_logical_task(identity, ready['worker_thread_id'])
    require(isinstance(reason, str) and 0 < len(reason) <= 240 and reason == reason.strip() and
            not any(ord(char) < 32 or ord(char) == 127 for char in reason) and
            not reason.endswith('.'), 'Announcement requires one bounded reason without a terminal period')
    for value in (identity['parent_thread_id'], identity['transaction_ref'], ready['worker_thread_id']):
        require(isinstance(value, str) and value and not any(char in value for char in '\r\n'),
                'Announcement task/transaction custody identity missing or malformed')
    require(digest(encode(ready)) == ready_sha, 'LOAD_READY digest does not bind the exact delivery tuple')
    return ('```ini\nCHILD_TASK=' + logical + '\nCHILD_SKILL_ROUTE=' + child +
            '\nLOAD=VERIFIED\nWORKER_TASK=' + ready['worker_thread_id'] +
            '\nLOAD_READY_SHA256=' + ready_sha + '\n```\n' +
            "I'm using the `" + logical + '` holon with the `' + child + '` skill to ' + reason + '.')


def verify_parent_ack(ack, ready, ready_sha, parent_rollout, launch_offset, ready_offset):
    """Read actual native parent assistant bytes, not an ACK-supplied message.

    parent_rollout and launch_offset are governor-owned launch inputs, never
    selected by the child or ACK. Scan only the bounded run suffix for exactly
    one marker. A late retrospective marker cannot release an already used turn.
    """
    require(set(ack) == {'ready_sha256', 'parent_row_offset', 'parent_row_bytes', 'parent_row_sha256'},
            'ACK shape differs')
    require(ack['ready_sha256'] == ready_sha, 'Foreign readiness ACK')
    path = Path(parent_rollout)
    with path.open('rb') as stream:
        first = stream.readline(65537)
        require(len(first) <= 65536, 'Parent session metadata bound')
        meta = json.loads(first)
        require(meta.get('type') == 'session_meta' and meta.get('payload', {}).get('id') ==
                ready['identity']['parent_thread_id'], 'Wrong native parent session')
        stream.seek(launch_offset)
        raw = stream.read(4 * 1024 * 1024 + 1)
    require(len(raw) <= 4 * 1024 * 1024 and (not raw or raw.endswith(b'\n')), 'Parent suffix incomplete/over bound')
    marker = marker_for(ready, ready_sha)
    matches = []
    offset = launch_offset
    for line in raw.splitlines(keepends=True):
        row = json.loads(line)
        payload = row.get('payload', {})
        if (row.get('type') == 'response_item' and is_parent_commentary_message(payload) and
                payload.get('content') == [{'type': 'output_text', 'text': marker}]):
            matches.append((offset, line))
        offset += len(line)
    require(len(matches) == 1, 'Missing or duplicate truthful parent marker')
    offset, row = matches[0]
    require(offset >= ready_offset and offset == ack['parent_row_offset'] and
            len(row) == ack['parent_row_bytes'] and digest(row) == ack['parent_row_sha256'],
            'Parent marker is retroactive, foreign or byte-unbound')
    return {'path': str(path), 'offset': offset, 'bytes': len(row), 'sha256': digest(row)}


def staged_turns(*, plan, canary, response, check_deadline, wait_event, process_identity,
                  flush_raw, run, clock=time.monotonic, pause=time.sleep, relay=print):
    try:
        return _staged_turns(plan=plan,canary=canary,response=response,check_deadline=check_deadline,
            wait_event=wait_event,process_identity=process_identity,flush_raw=flush_raw,run=run,
            clock=clock,pause=pause,relay=relay)
    except Exception as exc:
        canary.fail(canary.first_anomaly or 'Staged LOAD/USE failed: '+type(exc).__name__)


def _staged_turns(*, plan, canary, response, check_deadline, wait_event, process_identity,
                  flush_raw, run, clock=time.monotonic, pause=time.sleep, relay=print):
    """Invoked inside the retained capture's try/finally after startup binding.

    ACK file is an ordinary governor-to-capture input, not native model stdin.
    Native continuation uses documented turn/start over still-open app-server
    stdin. A failure never retries either turn or republishes a marker.
    """
    # These two fields are authenticated provenance only. The consuming
    # governor reconciles actual qualification/adoption; non-null or matching
    # pins do not admit an effect. Isolated qualification has its separate owner.
    cfg = plan['visibility']
    isolated = plan.get('purpose') == ISOLATED_QUALIFICATION
    if isolated:
        validate_isolated_qualification_plan(plan)
    else:
        require(cfg['identity']['selected_child'] in ('audit-state', 'audit-assess', 'audit-andon', 'audit-implement'),
                'Ordinary/nochild paths must bypass audit adapter')
    require(cfg['phase_capable_source_adoption'] is not None, 'Source composition provenance input missing')
    require(cfg['runtime_selection_acceptance'] is not None, 'Runtime/profile selection provenance input missing')
    require(type(cfg['ack_timeout_seconds']) in (int, float) and 0 < cfg['ack_timeout_seconds'] <= 600,
            'ACK deadline bound')
    thread_id = canary.thread_id
    load = copy.deepcopy(plan['turn_start'])
    require(load['id'] == 5, 'LOAD request identity')
    load['params']['threadId'] = thread_id
    require(load['params']['input'] == cfg['load_input'], 'LOAD prompt substitution')
    response(load)
    while not canary.completed:
        check_deadline()
        wait_event()
    evidence = canary.qualify_load()
    prefix = flush_raw()  # existing owner flushes + hashes exact captured prefix
    ready = {'schema': 'child-load-ready-v1', 'identity': cfg['identity'],
             'worker_thread_id': thread_id, 'process_identity': process_identity,
             'load_evidence': evidence, 'raw_prefix': prefix,
             'phase_capable_source_adoption': cfg['phase_capable_source_adoption'],
             'runtime_selection_acceptance': cfg['runtime_selection_acceptance'],
             'semantic_verdict': None, 'owner_stage_receipt': None}
    if isolated:
        ready['purpose'] = ISOLATED_QUALIFICATION
    raw = encode(ready)
    ready_sha = digest(raw)
    ready_offset = Path(cfg['parent_rollout']).stat().st_size
    publish_once(Path(run) / 'LOAD_READY.json', raw)
    relay('LOAD_READY ' + str(Path(run) / 'LOAD_READY.json') + ' ' + ready_sha, flush=True)
    deadline = clock() + cfg['ack_timeout_seconds']
    ack_path = Path(run) / 'PARENT_VISIBILITY_ACK.json'
    while not ack_path.exists():
        check_deadline()
        require(clock() < deadline, 'Parent visibility ACK timeout; preserve LOAD and contain owned process')
        pause(.05)
    check_deadline()
    require(clock() < deadline and canary.phase == 'LOAD' and canary.completed, 'Late or post-USE ACK')
    ack_raw = ack_path.read_bytes()
    require(len(ack_raw) <= 4096, 'ACK byte bound')
    ack = json.loads(ack_raw)
    proof = verify_parent_ack(ack, ready, ready_sha, cfg['parent_rollout'], cfg['parent_launch_offset'], ready_offset)
    check_deadline()
    # Exact replay is reconciled by retained RELEASE.json, never sent again.
    release = {'ready_sha256': ready_sha, 'ack_sha256': digest(ack_raw), 'parent_message': proof,
               'worker_thread_id': thread_id, 'use_request_id': 6, 'delivery_status': 'PENDING'}
    publish_once(Path(run) / 'RELEASE.json', encode(release))
    canary.release(ready_sha, plan['expected_turn_settings']['USE'])
    use = copy.deepcopy(plan['use_turn_start'])
    use['id'] = 6
    use['params']['threadId'] = thread_id
    use['params']['input'] = cfg['use_input']
    # Failure here may include a partial native write. Existing sent/raw custody
    # resolves that effect; RELEASE is deliberately not delivery/completion proof.
    response(use)
    while not canary.completed:
        check_deadline()
        wait_event()
    require(canary.transport_complete(), 'USE transport incomplete')
    return {'status': 'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT', 'ready': ready,
            'ready_sha256': ready_sha, 'release': release, 'snapshot': canary.snapshot()}
