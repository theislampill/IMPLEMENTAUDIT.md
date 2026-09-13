"""Bounded observation of one native turn. No execution or qualification authority."""
import json
import copy
import hashlib
import math
import re
import shlex
from pathlib import PureWindowsPath


class CanaryProtocol:
    def __init__(self):
        self.thread_id = None
        self.turn_id = None
        self.requested = False
        self.started = False
        self.completed = False
        self.response_seen = False
        self.items = {}
        self.frames = []
        self._protocol_frames = []
        self._public_shape_checks = {}
        self._current_diagnostic = None
        self.first_anomaly = None
        self.turn_payloads = []
        self.function_routes = []
        self.expected_settings = None
        self.settings_observed = False
        self.phase_activity_observed = False
        self.startup_effort_evidence = None
        self.unadmitted_raw_tail = []
        self.unadmitted_raw_tail_truncated = False
        self.code_mode = None
        self.raw_custody = {'call': None, 'output': None, 'user': None, 'typed_user': None, 'final': None, 'responses': []}
        self.request_input = None
        self.request_content = None
        self.context_contract_sha256 = None
        self.context_phase = None
        self.context_expected = None
        self.context_observations = []
        self.context_closed = False

    def bind_context_contract(self, contract, phase):
        if self.requested or self.context_expected is not None or phase not in ('LOAD','USE'):
            self.fail('Unbound or repeated context expectation selection')
        def valid_pin(value):
            return (type(value) is dict and set(value)=={'path','bytes','sha256'} and
                type(value['path']) is str and bool(value['path']) and type(value['bytes']) is int and value['bytes']>=0 and
                type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['sha256']) is not None)
        digest=lambda value:type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
        if (type(contract) is not dict or set(contract)!={'schema','scope','source_commit','source_input','basis_sha256','custody','phases'} or
                contract['schema']!='native-context-contract-v1' or contract['scope'] not in ('OFFLINE_SYNTHETIC','SOURCE_INPUT') or
                contract['source_commit']!='b5bffd3ec4db487e7e3dec59663875b0ef7b72ca' or
                not valid_pin(contract['source_input']) or contract['source_input']['bytes']==0 or not digest(contract['basis_sha256']) or
                type(contract['custody']) is not list or not contract['custody'] or
                any(not valid_pin(row) for row in contract['custody']) or
                type(contract['phases']) is not dict or set(contract['phases'])!={'LOAD','USE'}):
            self.fail('Missing or malformed independent context contract')
        if any(type(value) is not dict for value in contract['phases'].values()):
            self.fail('Malformed context phase declaration')
        if contract['source_input'] not in contract['custody'] or len({row['path'] for row in contract['custody']})!=len(contract['custody']):
            self.fail('Context source-input custody is incomplete or duplicated')
        for name, expected in contract['phases'].items():
            if (type(expected) is not dict or set(expected)!={'phase','mode','previous_state_sha256','state_sha256','wire','empty_prefix_proof','rows'} or
                    expected['phase']!=name or expected['mode']!=('INITIAL' if name=='LOAD' else 'DIFF') or
                    not digest(expected['state_sha256']) or
                    (name=='LOAD' and expected['previous_state_sha256'] is not None) or
                    (name=='USE' and expected['previous_state_sha256']!=contract['phases']['LOAD'].get('state_sha256')) or
                    type(expected['rows']) is not list or len(expected['rows'])>128):
                self.fail('Context phase or LOAD-to-USE state binding differs')
            wire=expected['wire']
            if (type(wire) is not dict or set(wire)!={'id','phase','turn_id','create_time'} or
                    wire['id'] not in ('opaque_nonempty','absent_or_null','absent','null') or wire['phase']!='absent_or_null' or
                    wire['turn_id'] not in ('required_active','optional_active')):
                self.fail('Context wire-shape proof selection differs')
            clock=wire['create_time']
            if (type(clock) is not dict or set(clock)!={'required','minimum','maximum'} or type(clock['required']) is not bool or
                    any(type(clock[key]) not in (int,float) or not math.isfinite(clock[key]) for key in ('minimum','maximum')) or
                    not 0<=clock['minimum']<=clock['maximum']<=clock['minimum']+60):
                self.fail('Context timestamp source interval is unbound')
            if ((not expected['rows'] and (not valid_pin(expected['empty_prefix_proof']) or expected['empty_prefix_proof']['bytes']==0)) or
                    (expected['rows'] and expected['empty_prefix_proof'] is not None)):
                self.fail('Empty context requires an independent empty-branch proof')
            seen=set()
            for row in expected['rows']:
                if (type(row) is not dict or set(row)!={'producers','branches','role','content_item_kinds','content'} or
                        row['role'] not in ('user','developer') or
                        any(type(row[key]) is not list for key in ('producers','branches','content_item_kinds','content')) or
                        not 0<len(row['content'])<=128 or
                        any(len(row[key])!=len(row['content']) for key in ('producers','branches','content_item_kinds')) or
                        any(type(value) is not str or not value or len(value)>256 for key in ('producers','branches','content_item_kinds') for value in row[key]) or
                        'user.text' in row['content_item_kinds'] or len(set(row['producers']))!=len(row['producers']) or seen.intersection(row['producers'])):
                    self.fail('Context producer/grouping/cardinality contract differs')
                seen.update(row['producers'])
                for item in row['content']:
                    if (type(item) is not dict or set(item)!={'type','bytes','sha256'} or item['type']!='input_text' or
                            type(item['bytes']) is not int or not 0<=item['bytes']<=65536 or not digest(item['sha256'])):
                        self.fail('Independent private context commitment is malformed')
        self.context_contract_sha256=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.context_phase=phase
        self.context_expected=copy.deepcopy(contract['phases'][phase])

    def require_context_complete(self, close=False):
        if self.code_mode and (self.context_expected is None or
                len(self.context_observations)!=len(self.context_expected['rows'])):
            self.fail('Missing expected source context before submitted input or phase completion')
        if close:self.context_closed=True

    def observe_context(self, message):
        if self.context_expected is None or self.context_closed or len(self.context_observations)>=len(self.context_expected['rows']):
            self.fail('Unexpected, extra or late source-context row')
        expected=self.context_expected['rows'][len(self.context_observations)]
        item=message['params']['item'];wire=self.context_expected['wire']
        if (set(message) not in ({'method','params'},{'method','params','emittedAtMs'}) or
                ('emittedAtMs' in message and (type(message['emittedAtMs']) is not int or not 0<=message['emittedAtMs']<2**63)) or
                not {'type','role','content','internal_chat_message_metadata_passthrough'}<=set(item)<=
                    {'type','id','role','phase','content','internal_chat_message_metadata_passthrough'} or
                item.get('type')!='message' or item.get('role')!=expected['role'] or item.get('phase') is not None):
            self.fail('Source-context envelope/role/phase differs')
        identity=item.get('id')
        if ((wire['id']=='opaque_nonempty' and (type(identity) is not str or not 0<len(identity)<=128)) or
                (wire['id']=='absent_or_null' and identity is not None) or
                (wire['id']=='absent' and 'id' in item) or (wire['id']=='null' and ('id' not in item or identity is not None)) or
                (identity is not None and any(row['raw_item_id']==identity for row in self.context_observations))):
            self.fail('Source-context identifier behavior or uniqueness differs')
        metadata=item.get('internal_chat_message_metadata_passthrough')
        if (type(metadata) is not dict or set(metadata)-{'turn_id','create_time','content_item_kinds'} or
                not self.exact_shape(metadata.get('content_item_kinds'),expected['content_item_kinds']) or
                metadata.get('turn_id') not in (None,self.turn_id) or
                (wire['turn_id']=='required_active' and metadata.get('turn_id')!=self.turn_id)):
            self.fail('Source-context classification/order or metadata differs')
        stamp=metadata.get('create_time');clock=wire['create_time']
        if ((clock['required'] and stamp is None) or (stamp is not None and
                (type(stamp) not in (int,float) or not math.isfinite(stamp) or not clock['minimum']<=stamp<=clock['maximum']))):
            self.fail('Source-context timestamp differs from bound interval')
        content=item.get('content')
        if type(content) is not list or len(content)!=len(expected['content']):
            self.fail('Source-context split/merge or content cardinality differs')
        for value,wanted in zip(content,expected['content']):
            if type(value) is not dict or set(value)!={'type','text'} or value.get('type')!='input_text' or type(value.get('text')) is not str:
                self.fail('Source-context content shape differs')
            raw=value['text'].encode('utf-8')
            if len(raw)!=wanted['bytes'] or hashlib.sha256(raw).hexdigest()!=wanted['sha256']:
                self.fail('Private source-context bytes differ from independent commitment')
        self.context_observations.append(self.public_raw_descriptor(message))

    def bind_code_mode(self, spec):
        required = {'wrapper_source','arguments','expected_argv','cwd','expected_output','terminal_text'}
        if self.requested or self.code_mode is not None or type(spec) is not dict or set(spec) != required:
            self.fail('Unbound or duplicate literal code-mode selection')
        if any(type(spec[key]) is not str or not spec[key] for key in ('wrapper_source','cwd','expected_output','terminal_text')):
            self.fail('Incomplete literal code-mode selection')
        if len(spec['expected_output'].encode('utf-8')) > 65536:
            self.fail('Code-mode output exceeds existing byte bound')
        arguments=spec['arguments']
        if (type(arguments) is not dict or set(arguments)!={'cmd','shell','login','workdir','max_output_tokens','yield_time_ms'} or
                arguments.get('login') is not False or type(arguments.get('max_output_tokens')) is not int or arguments['max_output_tokens']!=35000 or
                type(arguments.get('yield_time_ms')) is not int or arguments['yield_time_ms']!=10000 or
                arguments.get('workdir')!=spec['cwd'] or type(arguments.get('cmd')) is not str or not arguments['cmd'] or
                type(arguments.get('shell')) is not str or not PureWindowsPath(arguments['shell']).is_absolute() or
                spec['expected_argv']!=[arguments['shell'],'-NoProfile','-Command',arguments['cmd']]):
            self.fail('Code-mode arguments are not the exact bounded shell call')
        literal=('// @exec: {"yield_time_ms":30000,"max_output_tokens":40000}\n'
                 'text(await tools.exec_command('+json.dumps(arguments,separators=(',',':'),ensure_ascii=True)+'));')
        if spec['wrapper_source']!=literal:
            self.fail('Code-mode source is not the literal single-call program')
        self.code_mode = copy.deepcopy(spec)

    @staticmethod
    def public_raw_descriptor(message):
        raw = json.dumps(message,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
        params=message.get('params',{})
        if type(params) is not dict:params={}
        item=params.get('item',{})
        if type(item) is not dict:item={}
        return {'method':message.get('method'),'params':{'threadId':params.get('threadId'),
            'turnId':params.get('turnId')},'raw_item_type':item.get('type'),
            'raw_item_id':item.get('id'),'call_id':item.get('call_id'),
            'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'private_body_omitted':True}

    def diagnostic_descriptor(self, message):
        if type(message) is not dict:
            raw=json.dumps(message,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
            return {'method':None,'params':{},'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'private_body_omitted':True}
        result=self.public_raw_descriptor(message)
        # Unclassified identity fields can themselves contain private bodies.
        # The complete frame commitment preserves identity without trusting them.
        for key in ('raw_item_type','raw_item_id','call_id'):
            result[key]=None
        if message.get('method') not in ('rawResponseItem/completed','rawResponse/completed'):
            result['method']=None
            result['method_sha256']=hashlib.sha256(json.dumps(message.get('method'),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        for key,expected in (('threadId',self.thread_id),('turnId',self.turn_id)):
            if result['params'].get(key)!=expected:result['params'][key]=None
        return result

    def note_validated_public_shape(self, message, accepted_callback):
        """Internal diagnostic classification after the existing closed public schema.

        This is not a wire field, admission token or context authorization.
        The public body stays omitted until semantic acceptance calls back.
        """
        identity=self.diagnostic_descriptor(message)['sha256']
        self._public_shape_checks[identity]=accepted_callback

    def publish_diagnostic(self, message):
        if self._current_diagnostic is not None:
            index,descriptor,callback=self._current_diagnostic
            if callback is not None and message.get('method') not in ('rawResponseItem/completed','rawResponse/completed'):
                self.frames[index]=copy.deepcopy(message)
                callback()
        self._current_diagnostic=None

    def _record_diagnostic(self, message):
        descriptor=self.diagnostic_descriptor(message)
        index=len(self.frames)
        callback=self._public_shape_checks.pop(descriptor['sha256'],None)
        self.frames.append(descriptor)
        self._current_diagnostic=(index,descriptor,callback)

    def _diagnostic_item(self, item):
        if item is None:return None
        for frame in self.frames:
            params=frame.get('params',{})
            if frame.get('method') in ('item/started','item/completed') and params.get('item')==item:
                return copy.deepcopy(item)
        descriptor=self.diagnostic_descriptor({'method':'unclassified/item','params':{'item':item}})
        return {'id':descriptor.get('raw_item_id'),'type':descriptor.get('raw_item_type'),
            'bytes':descriptor['bytes'],'sha256':descriptor['sha256'],'private_body_omitted':True}

    def public_final_messages(self):
        return [self._diagnostic_item(item) for item in self.final_messages()]

    def wrapper_result(self, body):
        if (type(body) is not list or len(body)!=2 or any(type(x) is not dict or
                set(x)!={'type','text'} or x['type']!='input_text' or type(x['text']) is not str for x in body)):
            self.fail('Wrapper output is not the complete two-text native result')
        if (re.fullmatch(r'Script completed\nWall time [0-9]+\.[0-9] seconds\nOutput:\n',body[0]['text']) is None or
                len(json.dumps(body,ensure_ascii=False).encode('utf-8'))>65536):
            self.fail('Wrapper failed, yielded, truncated or exceeded the output bound')
        def unique(pairs):
            result={}
            for key,value in pairs:
                if key in result: raise ValueError('duplicate output key')
                result[key]=value
            return result
        try:
            result=json.loads(body[1]['text'],object_pairs_hook=unique,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite output')))
        except (ValueError,TypeError):
            self.fail('Malformed or duplicate wrapper result fields')
        required={'chunk_id','wall_time_seconds','exit_code','output'}
        if (type(result) is not dict or not required<=set(result)<=required|{'original_token_count'} or
                type(result['exit_code']) is not int or result['exit_code']!=0 or
                type(result['chunk_id']) is not str or not 0<len(result['chunk_id'])<=128 or
                type(result['wall_time_seconds']) not in (int,float) or
                not math.isfinite(result['wall_time_seconds']) or not 0<=result['wall_time_seconds']<=60 or
                result['output']!=self.code_mode['expected_output']):
            self.fail('Wrapper result differs from complete successful inner output')
        if 'original_token_count' in result and (type(result['original_token_count']) is not int or result['original_token_count']<0):
            self.fail('Invalid native result token count')
        return result

    def observe_raw(self, message):
        if self.code_mode is None or self.first_anomaly or len(self.frames)>=512:
            self.fail(self.first_anomaly or 'Raw events require the reviewed literal code-mode route')
        params=message.get('params')
        if (type(params) is not dict or params.get('threadId')!=self.thread_id or
                params.get('turnId')!=self.turn_id or not self.requested or not self.started or self.completed):
            self.fail('Raw event outside exact active worker/turn prefix')
        try:self._record_diagnostic(message)
        except (TypeError,ValueError):self.fail('Raw notification is not valid JSON/UTF-8')
        if message['method']=='rawResponse/completed':
            identity=params.get('responseId')
            if type(identity) is not str or not identity or identity in self.raw_custody['responses'] or len(self.raw_custody['responses'])>=2:
                self.fail('Foreign, duplicate or extra raw response completion')
            # A response completes its emitted items, not an arbitrary count.
            # Its inner tool future may overlap this boundary; do not order the
            # first completion against the command or wrapper output.
            if not self.raw_custody['responses']:
                if self.raw_custody['call'] is None:
                    self.fail('First raw response completed before its wrapper invocation')
            elif self.raw_custody['final'] is None:
                self.fail('Final raw response completed before its final raw/typed pair')
            self.raw_custody['responses'].append(identity)
            return
        if set(params)!={'threadId','turnId','item'} or type(params['item']) is not dict:
            self.fail('Malformed raw item envelope')
        item=params['item'];kind=item.get('type')
        metadata=item.get('internal_chat_message_metadata_passthrough')
        if kind=='message' and item.get('role') in ('user','developer') and (
                item.get('role')=='developer' or type(metadata) is not dict or metadata.get('content_item_kinds')!=['user.text']):
            self.observe_context(message)
            return
        literal_user=kind=='message' and item.get('role')=='user'
        allowed_metadata={'turn_id','create_time'}|({'content_item_kinds'} if literal_user else set())
        if metadata is not None and (type(metadata) is not dict or set(metadata)-allowed_metadata or
                metadata.get('turn_id') not in (None,self.turn_id)):
            self.fail('Unreviewed or foreign raw metadata')
        # The pinned producer/annotation/serde path preserves this exact
        # classification for the selected single text user. It is not a token
        # of provenance or permission, and is not admitted on other rows.
        if literal_user and (type(metadata) is not dict or
                not self.exact_shape(metadata.get('content_item_kinds'),['user.text'])):
            self.fail('Missing or invalid selected text-user classification')
        if kind=='reasoning':
            return  # Private body remains solely in the existing private raw capture.
        if kind=='message':
            role=item.get('role');content=item.get('content')
            if role=='developer': return
            if type(content) is not list or len(content)!=1 or type(content[0]) is not dict:
                self.fail('Unexpected raw public message shape')
            if role=='user':
                self.require_context_complete(close=True)
                if self.raw_custody['user'] is not None or content[0]!={'type':'input_text','text':self.request_input} or self.raw_custody['call']:
                    self.fail('Raw input differs from the exact selected request')
                self.raw_custody['user']=self.public_raw_descriptor(message)
            elif role=='assistant':
                if (self.raw_custody['final'] is not None or self.raw_custody['output'] is None or
                        len(self.raw_custody['responses'])!=1 or
                        item.get('phase')!='final_answer' or content[0]!={'type':'output_text','text':self.code_mode['terminal_text']}):
                    self.fail('Unreviewed raw assistant conduct or readiness before wrapper delivery')
                messages=self.final_messages()
                if len(messages)!=1 or item.get('id')!=messages[0]['id']:
                    self.fail('Raw final message does not pair with completed typed readiness')
                self.raw_custody['final']=self.public_raw_descriptor(message)
            else:self.fail('Unreviewed raw message role')
            return
        self.require_activity_settings()
        if kind=='custom_tool_call':
            typed_user=self.raw_custody['typed_user']
            if (self.raw_custody['call'] is not None or self.raw_custody['user'] is None or
                    typed_user is None or not typed_user['completed'] or self.items_have_command() or
                    item.get('name')!='exec' or item.get('namespace') is not None or
                    item.get('input')!=self.code_mode['wrapper_source'] or
                    type(item.get('call_id')) is not str or not item['call_id'] or item.get('status') not in (None,'completed')):
                self.fail('Extra, late, nonliteral or unreviewed wrapper invocation')
            self.raw_custody['call']={'call_id':item['call_id'],'input':item['input'],
                                      'source_sha256':hashlib.sha256(item['input'].encode()).hexdigest()}
            return
        if kind=='custom_tool_call_output':
            call=self.raw_custody['call'];commands=self.items_have_command(completed=True)
            if (call is None or self.raw_custody['output'] is not None or item.get('call_id')!=call['call_id'] or
                    item.get('name') not in (None,'exec') or len(commands)!=1):
                self.fail('Foreign, duplicate, unpaired or premature wrapper output')
            result=self.wrapper_result(item.get('output'))
            if result['output']!=commands[0]['aggregatedOutput']:
                self.fail('Wrapper delivery differs from actual inner command output')
            self.raw_custody['output']={'call_id':item['call_id'],'body':copy.deepcopy(item['output']),
                'sha256':hashlib.sha256(json.dumps(item['output'],separators=(',',':')).encode()).hexdigest()}
            return
        self.fail('Unreviewed raw response route; frame SHA256: '+self.diagnostic_descriptor(message)['sha256'])

    def items_have_command(self, completed=False):
        return [row['completed' if completed else 'started'] for row in self.items.values()
                if row['started'].get('type')=='commandExecution' and (not completed or row['completed'] is not None)]

    def code_mode_evidence(self):
        if self.code_mode is None:return None
        self.require_context_complete()
        if (any(self.raw_custody[key] is None for key in ('call','output','user','typed_user','final')) or
                not self.raw_custody['typed_user']['completed'] or
                len([row for row in self.items.values() if row['started'].get('type')=='userMessage'])!=1 or
                len(self.raw_custody['responses'])!=2 or len(self.items_have_command(completed=True))!=1):
            self.fail('Incomplete raw/typed prefix or wrapper/inner/output custody')
        wrappers=[row['completed'] for row in self.items.values() if row['started'].get('type')=='functionCallOutput']
        if len(wrappers)>1 or any(row is None or row.get('id')!=self.raw_custody['call']['call_id'] or
                not self.exact_shape(row.get('output'),self.raw_custody['output']['body']) for row in wrappers):
            self.fail('Typed wrapper projection does not exactly match raw delivery')
        return {'mapping':'SOURCE_DERIVED_LITERAL_SINGLE_CALL','native_parent_link_claimed':False,
            'typed_user_item_id':self.raw_custody['typed_user']['id'],
            'raw_user_item_id':self.raw_custody['user']['raw_item_id'],
            'user_pairing':'SELECTED_CONTENT_AND_ORDERED_LIFECYCLE_NOT_ID_EQUALITY',
            'wrapper_call_id':self.raw_custody['call']['call_id'],'inner_command_id':self.items_have_command(True)[0]['id'],
            'wrapper_source_sha256':self.raw_custody['call']['source_sha256'],
            'model_visible_output':self.raw_custody['output']['body'],
            'wrapper_output_sha256':self.raw_custody['output']['sha256'],'raw_response_ids':list(self.raw_custody['responses']),
            'native_metadata_census_claimed':False,
            'context_contract_sha256':self.context_contract_sha256,'context_rows_consumed':len(self.context_observations)}

    def fail(self, reason):
        if self._current_diagnostic is not None:
            index,descriptor,callback=self._current_diagnostic
            self.frames[index]=descriptor
        self._public_shape_checks.clear()
        if self.first_anomaly is None:
            self.first_anomaly = reason
        raise ValueError(reason)

    def bind_thread(self, identity):
        if self.thread_id is not None or not isinstance(identity, str) or not identity:
            self.fail('Invalid or repeated canary thread binding')
        self.thread_id = identity

    def register_turn(self, request):
        if self.requested or self.thread_id is None or request.get('id') != 5 or request.get('method') != 'turn/start':
            self.fail('Only one bound canary turn request is permitted')
        params = request.get('params', {})
        if self.expected_settings is None or params.get('threadId') != self.thread_id or params.get('permissions') != self.expected_settings['activePermissionProfile']['id']:
            self.fail('Turn thread/profile binding differs')
        environments = ([{'environmentId':'local','cwd':self.code_mode['cwd'],'runtimeWorkspaceRoots':[]}]
                        if self.code_mode else [])
        if params.get('approvalPolicy') != 'never' or not self.exact_shape(params.get('environments'),environments) or 'sandboxPolicy' in params:
            self.fail('Turn approval/environment/profile constraints differ')
        if self.code_mode:
            if self.context_expected is None:
                self.fail('Code-mode turn lacks independent context expectations')
            inputs=params.get('input')
            if (type(inputs) is not list or len(inputs)!=1 or type(inputs[0]) is not dict or
                    set(inputs[0])!={'type','text','text_elements'} or inputs[0].get('type')!='text' or
                    type(inputs[0].get('text')) is not str or inputs[0]['text_elements']!=[] or params.get('clientId') is not None):
                self.fail('Exact literal turn input missing')
            self.request_input=inputs[0]['text']
            self.request_content=copy.deepcopy(inputs)
        if self.expected_settings is not None:
            expected = self.expected_settings
            if params.get('model') != expected['model'] or params.get('effort') != expected['effort']:
                self.fail('Actual turn model/effort differs from effective settings binding')
            collaboration = expected['collaborationMode']
            if collaboration != {'mode': 'default', 'settings': {'model': params['model'],
                    'reasoning_effort': params['effort'], 'developer_instructions': None}}:
                self.fail('Actual turn collaboration settings differ')
        if params.get('cwd') != self.expected_settings['cwd']:
            self.fail('Turn cwd binding differs')
        self.requested = True

    @staticmethod
    def exact_shape(value, expected):
        # Type-aware equality rejects bool/int aliases, missing/null members,
        # extra fields and every unreviewed value, recursively. This fixed
        # projection is narrower than the pinned native settings schema.
        if type(value) is not type(expected):
            return False
        if isinstance(expected, dict):
            return set(value) == set(expected) and all(
                CanaryProtocol.exact_shape(value[key], expected[key]) for key in expected)
        if isinstance(expected, list):
            return len(value) == len(expected) and all(
                CanaryProtocol.exact_shape(a, b) for a, b in zip(value, expected))
        return value == expected

    def bind_settings(self, startup, expected):
        if self.thread_id is None or self.requested or self.expected_settings is not None:
            self.fail('Settings binding outside accepted startup')
        if not isinstance(startup, dict) or not isinstance(expected, dict):
            self.fail('Malformed settings binding')
        # Startup effort is intentionally not the turn effort. The latter is
        # checked against the actual request at registration below.
        for key in ('cwd', 'approvalPolicy', 'approvalsReviewer', 'activePermissionProfile',
                    'model', 'modelProvider', 'serviceTier', 'multiAgentMode'):
            if key not in startup or key not in expected or not self.exact_shape(startup[key], expected[key]):
                self.fail('Startup/effective settings differ: ' + key)
        if 'sandbox' not in startup or not self.exact_shape(startup['sandbox'], expected.get('sandboxPolicy')):
            self.fail('Startup/effective sandbox differs')
        # This caller relies on a natural startup-to-LOAD effort change.
        # Both native response.reasoningEffort and settings.effort map
        # to the same config snapshot field. Equal effort supplies no
        # guaranteed change-only notification and no full witness here.
        effort = startup.get('reasoningEffort')
        if ('reasoningEffort' not in startup or
                (effort is not None and (type(effort) is not str or not effort))):
            self.fail('Actual startup effort evidence missing or malformed')
        self.startup_effort_evidence = {'observed': effort, 'requested': expected.get('effort'),
            'effective_change': not self.exact_shape(effort, expected.get('effort')),
            'complete_settings_witness': False}
        if not self.startup_effort_evidence['effective_change']:
            self.fail('Same-effort startup has no guaranteed full settings witness in this caller')
        self.expected_settings = copy.deepcopy(expected)

    def require_activity_settings(self):
        # Observation may arrive after real execution. This gate refuses
        # evidence admission; it does not prove prevention of that effect.
        self.phase_activity_observed = True
        if not self.settings_observed:
            self.fail('Phase activity observed before exact settings evidence; effects not disproved')

    def observe_settings(self, message):
        if (not self.requested or self.completed or self.settings_observed or self.expected_settings is None
                or self.phase_activity_observed or any(row['terminal'] for row in self.turn_payloads)):
            self.fail('Unrequested, late, duplicate or unbound settings notification')
        if set(message) not in ({'method', 'params'}, {'method', 'params', 'emittedAtMs'}):
            self.fail('Malformed settings notification envelope')
        if 'emittedAtMs' in message and (type(message['emittedAtMs']) is not int or message['emittedAtMs'] < 0):
            self.fail('Malformed settings notification timestamp')
        expected = {'threadId': self.thread_id, 'threadSettings': self.expected_settings}
        if not self.exact_shape(message['params'], expected):
            self.fail('Effective settings shape or invariant differs')
        self.settings_observed = True

    def record_unadmitted(self, message):
        # Diagnostic identities only. Never invoke observe/response or repair
        # accepted-ledger absence from bytes retained after semantic abort.
        if len(self.unadmitted_raw_tail) >= 512:
            self.unadmitted_raw_tail_truncated = True
            return
        try:descriptor=self.diagnostic_descriptor(message)
        except (TypeError,ValueError):descriptor={'private_body_omitted':True,'invalid_json_utf8':True}
        row = dict(descriptor, classification='UNADMITTED_RAW_TAIL', semantic_credit=False)
        if isinstance(message, dict):
            if type(message.get('id')) is int:
                row['response_id'] = message['id']
        self.unadmitted_raw_tail.append(row)

    def turn_identity(self, identity):
        if not self.requested or not isinstance(identity, str) or not identity:
            self.fail('Unrequested or malformed turn identity')
        if self.turn_id is not None and identity != self.turn_id:
            self.fail('Mismatched turn identity')
        self.turn_id = identity

    def validate_item_route(self, item):
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id']:
            self.fail('Malformed item identity')
        kind = item.get('type')
        allowed = ('userMessage', 'agentMessage', 'reasoning', 'plan', 'commandExecution', 'functionCallOutput', 'imageView')
        if kind not in allowed:
            self.fail('Unreviewed or prohibited item route; item SHA256: ' + self._diagnostic_item(item)['sha256'])
        if self.code_mode and kind=='userMessage':
            if not self.context_closed:self.fail('Typed submitted user before complete source-context prefix')
            # Native source constructs this item from UserInput separately after
            # recording the raw user. Bind content and its own lifecycle ID;
            # never equate the independently constructed raw and typed IDs.
            typed_user=self.raw_custody['typed_user']
            if (not {'type','id','content'}<=set(item)<={'type','id','content','clientId'} or
                    not self.exact_shape(item['content'],self.request_content) or item.get('clientId') is not None or
                    (typed_user is not None and item['id']!=typed_user['id'])):
                self.fail('Typed user differs from exact selected request/lifecycle')
        if kind != 'userMessage':
            self.require_activity_settings()
        if self.code_mode and kind=='commandExecution':
            try: argv=shlex.split(item.get('command',''),posix=True)
            except ValueError:argv=None
            if (self.raw_custody['call'] is None or item['id']==self.raw_custody['call']['call_id'] or
                    argv!=self.code_mode['expected_argv'] or item.get('cwd')!=self.code_mode['cwd'] or
                    (self.items_have_command() and item['id']!=self.items_have_command()[0]['id'])):
                self.fail('Inner command outside exact literal wrapper/command/cwd binding')
            if item.get('status')=='completed' and (type(item.get('exitCode')) is not int or item['exitCode']!=0 or
                    item.get('aggregatedOutput')!=self.code_mode['expected_output']):
                self.fail('Inner command failed or output differs')
        if self.code_mode and kind=='agentMessage' and self.raw_custody['output'] is None:
            self.fail('Public readiness before complete wrapper delivery')
        if kind == 'functionCallOutput':
            name, namespace = item.get('name'), item.get('namespace')
            # These exact interface labels admit observation only. No function
            # output proves its invocation, locality, read-only effect or denial.
            direct = {('functions', 'exec_command'), ('functions', 'write_stdin'),
                      ('functions', 'view_image'), (None, 'exec_command'),
                      (None, 'write_stdin'), (None, 'view_image')}
            wrapper = {('functions', 'exec')}
            if self.code_mode:
                call=self.raw_custody['call']
                if call is None or item['id']!=call['call_id'] or name!='exec' or namespace not in (None,'functions'):
                    self.fail('Unpaired typed wrapper output')
                if item.get('output') is not None:self.wrapper_result(item['output'])
                wrapper.add((None,'exec'))
            if not isinstance(name, str) or (namespace is not None and not isinstance(namespace, str)):
                self.fail('Malformed function output route identity')
            route = (namespace, name)
            classification = ('DIRECT_LOCAL_INTERFACE_OUTPUT_ONLY' if route in direct else
                              'CODE_MODE_WRAPPER_NESTED_UNPROVED' if route in wrapper else
                              'UNREVIEWED_OR_PROHIBITED_FUNCTION_OUTPUT')
            self.function_routes.append({'item_id': item['id'], 'namespace': namespace, 'name': name,
                'classification': classification, 'invocation_or_prevention_proven': False})
            if route not in direct and route not in wrapper:
                self.fail('Unreviewed or prohibited function output; item SHA256: ' + self._diagnostic_item(item)['sha256'])

    def validate_turn_payload(self, turn, terminal=False):
        items = turn.get('items')
        view = turn.get('itemsView', 'full')
        if not isinstance(items, list) or len(items) > 128 or view not in ('full', 'summary', 'notLoaded'):
            self.fail('Malformed or unbounded turn items payload')
        # Preserve every supplied item, including unexpected/prohibited members,
        # while treating summary/notLoaded as incomplete views, not a census.
        self.turn_payloads.append({'terminal': terminal, 'itemsView': view, 'items': items})
        if terminal and not self.settings_observed:
            self.fail('Phase completion observed without exact settings evidence; effects not disproved')
        identities = set()
        for item in items:
            self.validate_item_route(item)
            identity = item['id']
            if identity in identities:
                self.fail('Duplicate item identity in turn payload')
            identities.add(identity)
            row = self.items.get(identity)
            if terminal:
                if row is None or row['completed'] is None or row['completed']['type'] != item['type']:
                    self.fail('Terminal item is not corroborated by completed item stream')
                if view == 'full' and row['completed'] != item:
                    self.fail('Full terminal item contradicts completed item stream')
        if terminal and view == 'full' and identities != set(self.items):
            self.fail('Full terminal item census differs from observed item stream')

    def response(self, message):
        self._current_diagnostic=None
        if self.first_anomaly:
            self.fail(self.first_anomaly)
        if self.response_seen or 'error' in message or not isinstance(message.get('result'), dict):
            self.fail('Duplicate or failed canary turn response')
        turn = message['result'].get('turn')
        if not isinstance(turn, dict) or turn.get('status') not in ('inProgress', 'completed'):
            self.fail('Malformed canary start response')
        self.turn_identity(turn.get('id'))
        self.validate_turn_payload(turn, terminal=turn.get('status') == 'completed')
        self.response_seen = True

    def observe(self, message, *, publish=True):
        self._current_diagnostic=None
        result=self._observe(message)
        if self._current_diagnostic is not None:
            index,descriptor,callback=self._current_diagnostic
            is_raw=message.get('method') in ('rawResponseItem/completed','rawResponse/completed')
            self._protocol_frames.append(copy.deepcopy(descriptor if is_raw else message))
            if publish:self.publish_diagnostic(message)
        return result

    def _observe(self, message):
        """Outer capture performs independent marker recognition before this call."""
        if self.first_anomaly:
            self.fail(self.first_anomaly)
        if type(message) is not dict:
            try:self._record_diagnostic(message)
            except (TypeError,ValueError):self.fail('Notification is not valid JSON/UTF-8')
            self.fail('Malformed notification envelope')
        if message.get('method') in ('rawResponseItem/completed','rawResponse/completed'):
            self.observe_raw(message)
            return
        if len(self.frames) >= 512:
            self.fail('Canary notification bound reached')
        try:self._record_diagnostic(message)
        except (TypeError,ValueError):self.fail('Notification is not valid JSON/UTF-8')
        method, params = message.get('method'), message.get('params')
        if type(method) is not str:self.fail('Malformed notification method')
        if not isinstance(params, dict) or params.get('threadId') != self.thread_id:
            self.fail('Missing or mismatched notification thread identity')
        if method == 'thread/settings/updated':
            self.observe_settings(message)
            return
        if method == 'thread/status/changed':
            if not isinstance(params.get('status'), dict):
                self.fail('Malformed thread status')
            return
        if method == 'thread/tokenUsage/updated':
            self.turn_identity(params.get('turnId'))
            return
        if method in ('turn/started', 'turn/completed'):
            turn = params.get('turn')
            if not isinstance(turn, dict) or not isinstance(turn.get('items'), list):
                self.fail('Malformed turn notification')
            self.turn_identity(turn.get('id'))
            self.validate_turn_payload(turn, terminal=method == 'turn/completed')
            if method == 'turn/started':
                if self.started or self.completed or turn.get('status') != 'inProgress':
                    self.fail('Duplicate or invalid turn start notification')
                self.started = True
            else:
                if not self.started or self.completed:
                    self.fail('Unstarted or duplicate turn completion')
                if turn.get('status') != 'completed' or turn.get('error') is not None:
                    self.fail('Canary turn failed or interrupted')
                if any(row['completed'] is None for row in self.items.values()):
                    self.fail('Turn completed with unfinished captured items')
                if self.code_mode:self.code_mode_evidence()
                self.completed = True
            return
        self.turn_identity(params.get('turnId'))
        if not self.started or self.completed:
            self.fail('Item or turn update outside active canary turn')
        if method in ('turn/plan/updated', 'turn/moderationMetadata'):
            self.require_activity_settings()
            return
        if method in ('item/started', 'item/completed'):
            item = params.get('item')
            self.validate_item_route(item)
            identity, kind = item['id'], item.get('type')
            if self.code_mode and kind=='agentMessage' and len(self.raw_custody['responses'])!=1:
                self.fail('Typed final answer outside the second raw response phase')
            if self.code_mode and kind=='userMessage':
                typed_user=self.raw_custody['typed_user']
                if (self.raw_custody['user'] is None or self.raw_custody['call'] is not None or self.raw_custody['responses'] or
                        (method=='item/started' and typed_user is not None) or
                        (method=='item/completed' and (typed_user is None or typed_user['completed']))):
                    self.fail('Missing, extra or late typed request lifecycle')
            if method == 'item/started':
                if identity in self.items or len(self.items) >= 128:
                    self.fail('Duplicate item or item bound reached')
                self.items[identity] = {'started': item, 'completed': None}
            else:
                row = self.items.get(identity)
                if row is None or row['completed'] is not None or row['started']['type'] != kind:
                    self.fail('Unstarted, duplicate or mismatched completed item')
                row['completed'] = item
            if self.code_mode and kind=='userMessage':
                self.raw_custody['typed_user']={'id':identity,'completed':method=='item/completed'}
            return
        allowed_deltas = ('item/agentMessage/delta', 'item/plan/delta', 'item/commandExecution/outputDelta',
            'item/commandExecution/terminalInteraction', 'item/reasoning/summaryTextDelta',
            'item/reasoning/summaryPartAdded', 'item/reasoning/textDelta')
        if method not in allowed_deltas:
            self.fail('Unexpected canary notification method SHA256: ' + hashlib.sha256(method.encode('utf-8')).hexdigest())
        self.require_activity_settings()
        row = self.items.get(params.get('itemId'))
        if row is None or row['completed'] is not None:
            self.fail('Delta for unknown or completed item')

    def snapshot(self):
        public_items={}
        for key,row in self.items.items():
            projected={phase:self._diagnostic_item(value) for phase,value in row.items()}
            public_key=key if any(value and not value.get('private_body_omitted') for value in projected.values()) else (
                'sha256:'+hashlib.sha256(json.dumps(key,ensure_ascii=True).encode()).hexdigest())
            public_items[public_key]=projected
        public_turns=[{'terminal':row['terminal'],'itemsView':row['itemsView'],
            'items':[self._diagnostic_item(item) for item in row['items']]} for row in self.turn_payloads]
        public_routes=[]
        for route in self.function_routes:
            item=next((row.get('completed') or row.get('started') for key,row in public_items.items() if key==route.get('item_id')),None)
            if item and not item.get('private_body_omitted'):
                public_routes.append(copy.deepcopy(route))
            else:
                public_routes.append(self.diagnostic_descriptor({'method':'unclassified/function-route','params':{'item':route}}))
        return {'thread_id': self.thread_id, 'turn_id': self.turn_id, 'requested': self.requested,
            'start_response_observed': self.response_seen, 'started': self.started, 'completed': self.completed,
            'items': public_items, 'frames': copy.deepcopy(self.frames), 'first_anomaly': self.first_anomaly,
            'turn_payloads': public_turns, 'function_routes': public_routes,
            'settings_observed': self.settings_observed, 'expected_turn_settings': self.expected_settings,
            'phase_activity_observed': self.phase_activity_observed,
            'startup_effort_evidence': self.startup_effort_evidence,
            'unadmitted_raw_tail': self.unadmitted_raw_tail,
            'unadmitted_raw_tail_truncated': self.unadmitted_raw_tail_truncated,
            'code_mode_custody': self.raw_custody if self.code_mode else None,
            'context': {'phase':self.context_phase,'contract_sha256':self.context_contract_sha256,
                'expected_rows':len(self.context_expected['rows']) if self.context_expected else None,
                'observed':self.context_observations,'closed_before_submitted_user':self.context_closed},
            'complete_tool_inventory_observed': False, 'all_routes_read_exclusion_proven': False}

    def final_messages(self):
        return [row['completed'] for row in self.items.values() if row['completed'] is not None
            and row['completed'].get('type') == 'agentMessage']

    def transport_complete(self):
        return self.requested and self.response_seen and self.started and self.completed and self.settings_observed and not self.first_anomaly
