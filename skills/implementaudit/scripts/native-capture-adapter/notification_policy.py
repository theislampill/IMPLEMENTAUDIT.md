"""Closed disposition of the pinned 81-method one-turn fixture protocol.

This observer does not run hooks, authenticate their output, or authorize their
effects. An offline effect contract is an input to tests, never native readiness.
"""
import copy
import hashlib
import importlib.metadata
import json
import math
import re
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:
    raise RuntimeError('Pinned existing jsonschema runtime unavailable; no dependency acquisition permitted') from exc


def file_pin(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def runtime_identity():
    return {'version': importlib.metadata.version('jsonschema'), 'module': file_pin(jsonschema.__file__)}


def closed_schema(node):
    """Narrow native object shapes, retaining explicitly declared map schemas."""
    if isinstance(node, dict):
        if node.get('type') == 'object' and 'properties' in node:
            node.setdefault('additionalProperties', False)
        for value in node.values():
            closed_schema(value)
    elif isinstance(node, list):
        for value in node:
            closed_schema(value)


class NotificationPolicy:
    def __init__(self, plan, matrix, schema_path, effect_contract):
        self.plan = copy.deepcopy(plan)
        self.contract = copy.deepcopy(effect_contract)
        self.context_contract = None
        self.context_states = {}
        self.matrix = {row['method']: row['disposition'] for row in matrix['rows']}
        if (len(matrix['rows']) != 81 or len(self.matrix) != 81
                or any(value not in ('ABORT', 'HOOK', 'TELEMETRY', 'CANARY', 'THREAD_STARTED') for value in self.matrix.values())
                or file_pin(schema_path) != matrix['schema_pin']):
            raise ValueError('Pinned 81-method schema or disposition population differs')
        schema = json.loads(Path(schema_path).read_bytes())
        members = {branch['properties']['method']['enum'][0] for branch in schema['oneOf']}
        if set(self.matrix) != members:
            raise ValueError('Notification disposition matrix does not exactly cover native methods')
        closed_schema(schema)
        self.validator = jsonschema.Draft7Validator(schema)
        # Internal raw methods have separate generated schemas; they are absent
        # from the 81-method public union. Never infer them from a typed output.
        self.raw_validators = {}
        if plan.get('visibility', {}).get('load_spec', {}).get('code_mode') is not None:
            self.context_contract = copy.deepcopy(plan['visibility']['load_spec'].get('context_contract'))
            self.validate_context_expectations()
            self.context_contract_sha256 = hashlib.sha256(json.dumps(self.context_contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            kinds = {'user.text'}
            for phase in self.context_contract['phases'].values():
                for row in phase['rows']: kinds.update(row['content_item_kinds'])
            for method, name in [('rawResponseItem/completed','RawResponseItemCompletedNotification'),
                                 ('rawResponse/completed','RawResponseCompletedNotification')]:
                selected = plan.get('schemas', {}).get(name)
                if type(selected) is not dict or set(selected) != {'path','bytes','sha256'} or file_pin(selected['path']) != selected:
                    raise ValueError('Exact current raw-response schema pin required')
                raw_schema = json.loads(Path(selected['path']).read_bytes())
                metadata = raw_schema.get('definitions', {}).get('InternalChatMessageMetadataPassthrough')
                if metadata is not None:
                    # Current source serializes this host timestamp but hides it
                    # from JSON Schema. No warehouse cell/census fields admitted.
                    metadata['properties']['create_time'] = {'type':['number','null']}
                    # The source serializes this positional classification but
                    # omits it from schemas. Context/presence is checked below.
                    metadata['properties']['content_item_kinds'] = {
                        'type':'array','minItems':1,'maxItems':128,
                        'items':{'type':'string','enum':sorted(kinds)}}
                closed_schema(raw_schema)
                self.raw_validators[method] = jsonschema.Draft7Validator(raw_schema)
        self.frames = []
        self._current_diagnostic = None
        self.hooks = {}
        self.first_anomaly = None
        self.telemetry_counts = {}

    def validate_context_expectations(self):
        contract = self.context_contract
        def digest(value): return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
        def pin(value):
            return (type(value) is dict and set(value)=={'path','bytes','sha256'} and
                type(value['path']) is str and bool(value['path']) and type(value['bytes']) is int and value['bytes']>=0 and digest(value['sha256']))
        if (type(contract) is not dict or set(contract)!={'schema','scope','source_commit','source_input','basis_sha256','custody','phases'} or
                contract['schema']!='native-context-contract-v1' or contract['scope'] not in ('OFFLINE_SYNTHETIC','SOURCE_INPUT') or
                contract['source_commit']!='b5bffd3ec4db487e7e3dec59663875b0ef7b72ca' or not pin(contract['source_input']) or contract['source_input']['bytes']==0 or
                not digest(contract['basis_sha256']) or type(contract['custody']) is not list or not contract['custody'] or
                any(not pin(row) for row in contract['custody']) or type(contract['phases']) is not dict or set(contract['phases'])!={'LOAD','USE'}):
            raise ValueError('Policy requires independent phase context expectations')
        if any(type(value) is not dict for value in contract['phases'].values()):
            raise ValueError('Policy context phase declaration is malformed')
        if contract['source_input'] not in contract['custody'] or len({row['path'] for row in contract['custody']})!=len(contract['custody']):
            raise ValueError('Policy source-input custody is incomplete or duplicated')
        for name, phase in contract['phases'].items():
            if (type(phase) is not dict or set(phase)!={'phase','mode','previous_state_sha256','state_sha256','wire','empty_prefix_proof','rows'} or
                    phase['phase']!=name or phase['mode']!=('INITIAL' if name=='LOAD' else 'DIFF') or not digest(phase['state_sha256']) or
                    (name=='LOAD' and phase['previous_state_sha256'] is not None) or
                    (name=='USE' and phase['previous_state_sha256']!=contract['phases']['LOAD'].get('state_sha256')) or
                    type(phase['rows']) is not list or len(phase['rows'])>128):
                raise ValueError('Policy context phase/history binding differs')
            wire=phase['wire']
            if (type(wire) is not dict or set(wire)!={'id','phase','turn_id','create_time'} or
                    wire['id'] not in ('opaque_nonempty','absent_or_null','absent','null') or wire['phase']!='absent_or_null' or
                    wire['turn_id'] not in ('required_active','optional_active')):
                raise ValueError('Policy context wire behavior is unbound')
            clock=wire['create_time']
            if (type(clock) is not dict or set(clock)!={'required','minimum','maximum'} or type(clock['required']) is not bool or
                    any(type(clock[key]) not in (int,float) or not math.isfinite(clock[key]) for key in ('minimum','maximum')) or
                    not 0<=clock['minimum']<=clock['maximum']<=clock['minimum']+60):
                raise ValueError('Policy context time interval is unbound')
            if ((not phase['rows'] and (not pin(phase['empty_prefix_proof']) or phase['empty_prefix_proof']['bytes']==0)) or
                    (phase['rows'] and phase['empty_prefix_proof'] is not None)):
                raise ValueError('Policy empty context lacks independent branch proof')
            seen=set()
            for row in phase['rows']:
                if (type(row) is not dict or set(row)!={'producers','branches','role','content_item_kinds','content'} or row['role'] not in ('user','developer') or
                        any(type(row[key]) is not list for key in ('producers','branches','content_item_kinds','content')) or not 0<len(row['content'])<=128 or
                        any(len(row[key])!=len(row['content']) for key in ('producers','branches','content_item_kinds')) or
                        any(type(value) is not str or not value or len(value)>256 for key in ('producers','branches','content_item_kinds') for value in row[key]) or
                        'user.text' in row['content_item_kinds'] or len(set(row['producers']))!=len(row['producers']) or seen.intersection(row['producers'])):
                    raise ValueError('Policy context producer/grouping contract differs')
                seen.update(row['producers'])
                for content in row['content']:
                    if (type(content) is not dict or set(content)!={'type','bytes','sha256'} or content['type']!='input_text' or
                            type(content['bytes']) is not int or not 0<=content['bytes']<=65536 or not digest(content['sha256'])):
                        raise ValueError('Policy private context commitment is malformed')

    def context_state(self, canary):
        if self.context_contract is None:return None
        phase=getattr(canary,'context_phase',None)
        if phase not in ('LOAD','USE') or getattr(canary,'context_contract_sha256',None)!=self.context_contract_sha256:
            self.fail('Policy and observer context expectations/phase differ')
        if canary.first_anomaly:self.fail('Context phase already failed in the observer')
        if phase=='USE' and not self.context_states.get('LOAD',{}).get('complete'):
            self.fail('USE context before complete LOAD and phase release')
        state=self.context_states.setdefault(phase,{'thread_id':canary.thread_id,'turn_id':canary.turn_id,
            'observed':[],'closed':False,'complete':False})
        if state['thread_id']!=canary.thread_id or state['turn_id']!=canary.turn_id:
            self.fail('Context phase moved to a different worker/turn')
        return state

    def context_complete(self, canary, close=False, terminal=False):
        state=self.context_state(canary)
        if state is None:return
        if len(state['observed'])!=len(self.context_contract['phases'][canary.context_phase]['rows']):
            self.fail('Policy source-context prefix is incomplete')
        if close:state['closed']=True
        if terminal:
            if not state['closed']:self.fail('Phase completed before selected submitted input')
            state['complete']=True

    def observe_context(self, message, canary):
        state=self.context_state(canary)
        phase=self.context_contract['phases'][canary.context_phase]
        if state['closed'] or len(state['observed'])>=len(phase['rows']):
            self.fail('Policy rejected extra, duplicate or late context')
        expected=phase['rows'][len(state['observed'])]
        item=message['params']['item'];wire=phase['wire']
        if (not {'type','role','content','internal_chat_message_metadata_passthrough'}<=set(item)<=
                {'type','id','role','phase','content','internal_chat_message_metadata_passthrough'} or
                item.get('type')!='message' or item.get('role')!=expected['role'] or item.get('phase') is not None):
            self.fail('Policy source-context envelope/role/phase differs')
        identity=item.get('id')
        if ((wire['id']=='opaque_nonempty' and (type(identity) is not str or not 0<len(identity)<=128)) or
                (wire['id']=='absent_or_null' and identity is not None) or (wire['id']=='absent' and 'id' in item) or
                (wire['id']=='null' and ('id' not in item or identity is not None)) or
                (identity is not None and any(row['raw_item_id']==identity for old in self.context_states.values() for row in old['observed']))):
            self.fail('Policy context identifier behavior or reuse differs')
        metadata=item.get('internal_chat_message_metadata_passthrough')
        if (type(metadata) is not dict or set(metadata)-{'turn_id','create_time','content_item_kinds'} or
                metadata.get('content_item_kinds')!=expected['content_item_kinds'] or
                metadata.get('turn_id') not in (None,canary.turn_id) or
                (wire['turn_id']=='required_active' and metadata.get('turn_id')!=canary.turn_id)):
            self.fail('Policy context ordered classification or metadata differs')
        clock=wire['create_time'];stamp=metadata.get('create_time')
        if ((clock['required'] and stamp is None) or (stamp is not None and
                (type(stamp) not in (int,float) or not math.isfinite(stamp) or not clock['minimum']<=stamp<=clock['maximum']))):
            self.fail('Policy context timestamp differs')
        content=item.get('content')
        if type(content) is not list or len(content)!=len(expected['content']):self.fail('Policy context split/merge/cardinality differs')
        for actual,wanted in zip(content,expected['content']):
            if type(actual) is not dict or set(actual)!={'type','text'} or actual.get('type')!='input_text' or type(actual.get('text')) is not str:
                self.fail('Policy private context content shape differs')
            raw=actual['text'].encode('utf-8')
            if len(raw)!=wanted['bytes'] or hashlib.sha256(raw).hexdigest()!=wanted['sha256']:
                self.fail('Policy private context differs from independent bytes/commitment')
        state['observed'].append(canary.public_raw_descriptor(message))

    def fail(self, reason):
        if self._current_diagnostic is not None:
            index,descriptor=self._current_diagnostic
            self.frames[index]=descriptor
        if self.first_anomaly is None:
            self.first_anomaly = reason
        raise ValueError(reason)

    def bounded(self, value, depth=0):
        if depth > 32:
            self.fail('Notification nesting bound exceeded')
        if isinstance(value, dict):
            if len(value) > 128:
                self.fail('Notification object bound exceeded')
            for key, child in value.items():
                if len(key) > 256:
                    self.fail('Notification key bound exceeded')
                self.bounded(child, depth + 1)
        elif isinstance(value, list):
            if len(value) > 128:
                self.fail('Notification array bound exceeded')
            for child in value:
                self.bounded(child, depth + 1)
        elif isinstance(value, str):
            try:encoded=value.encode('utf-8')
            except UnicodeEncodeError:self.fail('Notification text is not valid UTF-8')
            if len(encoded)>65536:self.fail('Notification text bound exceeded')
        elif type(value) is int and not -(2**63) <= value < 2**63:
            self.fail('Notification integer bound exceeded')
        elif isinstance(value, float) and not math.isfinite(value):
            self.fail('Non-finite notification JSON number')

    def route(self, message, canary, positive_thread_id=None):
        self._current_diagnostic=None
        disposition=self._route(message,canary,positive_thread_id)
        if self._current_diagnostic is not None and message.get('method') not in self.raw_validators:
            index,descriptor=self._current_diagnostic
            if disposition=='CANARY':
                public=copy.deepcopy(message)
                canary.note_validated_public_shape(message,lambda index=index,public=public:self.frames.__setitem__(index,public))
            elif disposition=='HANDLED':
                self.frames[index]=copy.deepcopy(message)
        return disposition

    def accept_thread_started_diagnostic(self, message, canary):
        # The existing capture owns thread-start identity and request ordering.
        # Schema validation alone cannot publish a later-rejected thread body.
        if self.first_anomaly or self._current_diagnostic is None:
            self.fail(self.first_anomaly or 'Missing thread-start diagnostic candidate')
        index,descriptor=self._current_diagnostic
        if (message.get('method')!='thread/started' or
                canary.diagnostic_descriptor(message)['sha256']!=descriptor['sha256']):
            self.fail('Thread-start diagnostic identity differs')
        self.frames[index]=copy.deepcopy(message)
        self._current_diagnostic=None

    def _route(self, message, canary, positive_thread_id=None):
        if self.first_anomaly:
            self.fail(self.first_anomaly)
        if len(self.frames) >= 512:
            self.fail('All-notification bound reached')
        # Complete input remains in private raw custody. Public diagnostics
        # start body-omitted and are promoted only after closed validation.
        try:
            descriptor=canary.diagnostic_descriptor(message)
            self._current_diagnostic=(len(self.frames),descriptor)
            self.frames.append(descriptor)
        except (TypeError,ValueError):self.fail('Notification is not valid JSON/UTF-8')
        if not isinstance(message, dict) or set(message) not in (
                {'method', 'params'}, {'method', 'params', 'emittedAtMs'}):
            self.fail('Notification envelope differs')
        if 'emittedAtMs' in message and (type(message['emittedAtMs']) is not int
                or not 0 <= message['emittedAtMs'] < 2**63):
            self.fail('Notification timestamp malformed')
        self.bounded(message)
        method = message.get('method')
        if type(method) is not str:self.fail('Malformed notification method')
        if method in self.raw_validators:
            try:self.raw_validators[method].validate(message['params'])
            except jsonschema.ValidationError as exc:
                self.fail('Native raw-response schema rejected '+method+': '+str(exc.validator))
            self.active_turn(message['params'],canary)
            if method=='rawResponseItem/completed':
                item=message['params']['item']
                metadata=item.get('internal_chat_message_metadata_passthrough')
                if item.get('type')=='message' and item.get('role') in ('user','developer') and (
                        item.get('role')=='developer' or type(metadata) is not dict or metadata.get('content_item_kinds')!=['user.text']):
                    self.observe_context(message,canary)
                    return 'CANARY'
                if item.get('type')=='message' and item.get('role')=='user':
                    if (type(metadata) is not dict or
                            not canary.exact_shape(metadata.get('content_item_kinds'),['user.text']) or
                            not canary.exact_shape(item.get('content'),[{'type':'input_text','text':canary.request_input}])):
                        self.fail('Raw user classification does not bind the selected single text request')
                    self.context_complete(canary,close=True)
                elif type(metadata) is dict and 'content_item_kinds' in metadata:
                    self.fail('Classification metadata on an unrelated raw item')
            return 'CANARY'
        if method not in self.matrix:
            self.fail('Unlisted notification method SHA256: ' + hashlib.sha256(method.encode('utf-8')).hexdigest())
        # emittedAtMs is native transport metadata not declared by the enum.
        envelope = {key: message[key] for key in ('method', 'params')}
        try:
            self.validator.validate(envelope)
        except jsonschema.ValidationError as exc:
            self.fail('Native notification schema rejected ' + str(method) + ': ' + str(exc.validator))
        disposition = self.matrix[method]
        if self.context_contract is not None and method=='turn/completed':
            self.context_complete(canary,terminal=True)
        if self.context_contract is not None and method in ('item/started','item/completed') and message['params']['item'].get('type')=='userMessage':
            state=self.context_state(canary)
            if not state['closed']:self.fail('Policy typed user before exact context/submitted prefix')
        if disposition == 'ABORT':
            self.fail('Explicit notification abort: ' + method)
        if disposition == 'HOOK':
            self.observe_hook(message, canary)
            return 'HANDLED'
        if disposition == 'TELEMETRY':
            self.observe_telemetry(message, canary, positive_thread_id)
            return 'HANDLED'
        if method == 'turn/completed' and any(row['completed'] is None for row in self.hooks.values()):
            self.fail('Turn terminal cannot hide an unfinished hook')
        if method.startswith('item/') and any(row['completed'] is None for row in self.hooks.values()):
            self.fail('Model item while synchronous hook is unfinished')
        if method == 'thread/status/changed':
            status = message['params']['status']
            if status['type'] not in ('idle', 'active'):
                self.fail('Unexpected thread status state')
        if method == 'thread/tokenUsage/updated' and (not canary.started or canary.completed):
            self.fail('Token telemetry outside active turn')
        return disposition

    def active_turn(self, params, canary):
        if (not canary.requested or not canary.started or canary.completed
                or params.get('threadId') != canary.thread_id
                or params.get('turnId') != canary.turn_id):
            self.fail('Notification outside exact active thread/turn')

    def observe_telemetry(self, message, canary, positive_thread_id=None):
        method, params = message['method'], message['params']
        count = self.telemetry_counts.get(method, 0) + 1
        if count > 32:
            self.fail('Per-method telemetry bound exceeded')
        self.telemetry_counts[method] = count
        if method == 'remoteControl/status/changed':
            if not canary.exact_shape(params, self.plan['expected_remote_control']):
                self.fail('Remote control state or identity drift')
        elif method == 'warning':
            if params != {'threadId': canary.thread_id or positive_thread_id, 'message': self.plan['expected_warning']}:
                self.fail('Unreviewed warning semantics or identity')
        elif method == 'account/rateLimits/updated':
            if not canary.started or canary.completed:
                self.fail('Account telemetry outside active canary interval')
        elif method in ('model/verification', 'model/safetyBuffering/updated'):
            self.active_turn(params, canary)
            if method == 'model/safetyBuffering/updated' and (
                    params['model'] != self.plan['expected_metadata']['model']
                    or params.get('fasterModel') not in (None, self.plan['expected_metadata']['model'])):
                self.fail('Model telemetry reports an unapproved model alternative')
        else:
            self.fail('No telemetry discriminator: ' + method)

    def observe_hook(self, message, canary):
        params = message['params']
        self.active_turn(params, canary)
        if self.contract.get('scope') != 'OFFLINE_UNBOUND_EFFECT_CONTRACT_FIXTURE':
            self.fail('No admitted hook effect predicate; notifications do not authorize hooks')
        run = params['run']
        required = {'id', 'eventName', 'handlerType', 'executionMode', 'scope', 'sourcePath', 'source',
                    'displayOrder', 'status', 'statusMessage', 'startedAt', 'completedAt', 'durationMs', 'entries'}
        if set(params) != {'threadId', 'turnId', 'run'} or set(run) != required:
            self.fail('Incomplete or extra hook run fields')
        approved = next((row for row in self.contract['hooks'] if row['identity']['id'] == run['id']), None)
        if approved is None:
            self.fail('Unapproved hook run identity')
        identity = {key: run[key] for key in approved['identity']}
        if not canary.exact_shape(identity, approved['identity']):
            self.fail('Hook identity or source provenance differs')
        if file_pin(run['sourcePath']) != approved['source_pin']:
            self.fail('Hook configured source hash differs')
        if approved['disposition'] != 'ADMIT_OFFLINE_OBSERVATION_ONLY':
            self.fail('Current installed hook effect/compatibility contract blocks admission: ' + run['eventName'])
        # Only the source-traced no-context fixture output is permitted here.
        # Empty public entries are not proof that the hook followed UNBOUND.
        expected_entries = [] if message['method'] == 'hook/started' else approved['completion_entries']
        if run['entries'] != expected_entries:
            self.fail('Hook context/error/stop/output outside reviewed fixture contract')
        started = run['startedAt']
        if type(started) is not int or not 0 <= started < 2**63:
            self.fail('Malformed hook start timestamp')
        if message['method'] == 'hook/started':
            if run['id'] in self.hooks or len(self.hooks) >= 2:
                self.fail('Duplicate hook run or hook bound exceeded')
            if run['status'] != 'running' or run['completedAt'] is not None or run['durationMs'] is not None:
                self.fail('Malformed running hook state')
            if run['eventName'] == 'userPromptSubmit' and canary.items:
                self.fail('UserPromptSubmit preview after model items')
            if run['eventName'] == 'stop' and any(row['completed'] is None for row in self.hooks.values()):
                self.fail('Stop preview while another hook is unfinished')
            self.hooks[run['id']] = {'started': copy.deepcopy(run), 'completed': None}
        else:
            row = self.hooks.get(run['id'])
            if row is None or row['completed'] is not None:
                self.fail('Unstarted or duplicate hook completion')
            completed, duration = run['completedAt'], run['durationMs']
            if (run['status'] != 'completed' or type(completed) is not int or type(duration) is not int
                    or not row['started']['startedAt'] <= started <= completed
                    or not 0 <= duration <= 60000 or completed - row['started']['startedAt'] > 60
                    or abs((completed - started) * 1000 - duration) > 1000):
                self.fail('Failed hook or malformed/out-of-bound completion timing')
            row['completed'] = copy.deepcopy(run)

    def complete(self):
        return (not self.first_anomaly and all(row['completed'] is not None for row in self.hooks.values()) and
            (self.context_contract is None or (bool(self.context_states) and all(row['complete'] for row in self.context_states.values()))))

    def snapshot(self):
        return {'frames': self.frames, 'hooks': self.hooks, 'telemetry_counts': self.telemetry_counts,
                'context':self.context_states,'context_contract_sha256':getattr(self,'context_contract_sha256',None),
                'first_anomaly': self.first_anomaly, 'effect_authority': 'NONE',
                'hook_unbound_execution_proven': False, 'native_ready': False}
