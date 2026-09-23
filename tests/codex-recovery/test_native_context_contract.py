"""Cold source-context contract witnesses. All private bodies and identities are synthetic."""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shlex
import sys
import unittest
from unittest import mock

SOURCE = FIXTURES = WORK = PROFILE = PROTOCOL = POLICY = VISIBILITY = None

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module

def pin(path):
    raw = Path(path).read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

PERMISSIONS = '<permissions instructions>CTX19_PRIVATE permission body</permissions instructions>'
AGENTS = '# AGENTS.md instructions\n<INSTRUCTIONS>CTX19_PRIVATE instructions</INSTRUCTIONS>'
ENV_LOAD = '<environment_context>CTX19_PRIVATE filesystem reads=14</environment_context>'
ENV_USE = '<environment_context>CTX19_PRIVATE filesystem reads=16</environment_context>'

def content_commitment(text):
    return {'type': 'input_text', 'bytes': len(text.encode('utf-8')), 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}

def manual_contract():
    path = WORK / 'independent_expected_input.json'
    if not path.exists():
        path.write_text('{"origin":"INDEPENDENT_SYNTHETIC_SOURCE_INPUT","not_observed":true}\n', encoding='utf-8')
    wire = {'id': 'opaque_nonempty', 'phase': 'absent_or_null',
        'turn_id': 'required_active', 'create_time': {'required': True, 'minimum': 1000, 'maximum': 1060}}
    def row(producers, role, kinds, texts):
        return {'producers': producers, 'branches': ['PRESENT'] * len(producers), 'role': role,
            'content_item_kinds': kinds, 'content': [content_commitment(text) for text in texts]}
    load_state = sha({'permissions': PERMISSIONS, 'agents': AGENTS, 'environment': ENV_LOAD})
    use_state = sha({'permissions': PERMISSIONS, 'agents': AGENTS, 'environment': ENV_USE})
    return {'schema': 'native-context-contract-v1', 'scope': 'OFFLINE_SYNTHETIC',
        'source_commit': 'b5bffd3ec4db487e7e3dec59663875b0ef7b72ca', 'source_input': pin(path),
        'basis_sha256': 'a' * 64, 'custody': [pin(path)], 'phases': {
            'LOAD': {'phase': 'LOAD', 'mode': 'INITIAL', 'previous_state_sha256': None,
                'state_sha256': load_state, 'wire': wire, 'empty_prefix_proof': None,
                'rows': [row(['permissions'], 'developer', ['permissions.instructions'], [PERMISSIONS]),
                         row(['agents', 'environment'], 'user', ['agents_md.instructions', 'environments.environment_context'], [AGENTS, ENV_LOAD])]},
            'USE': {'phase': 'USE', 'mode': 'DIFF', 'previous_state_sha256': load_state,
                'state_sha256': use_state, 'wire': copy.deepcopy(wire), 'empty_prefix_proof': None,
                'rows': [dict(row(['environment'], 'user', ['environments.environment_context'], [ENV_USE]), branches=['CHANGED'])]}}}

def selection():
    binding = {'cwd': r'C:\context19\synthetic', 'powershell': {'path': r'C:\context19\pwsh.exe'}}
    load = PROFILE.code_mode_spec(binding, "Write-Output 'LOAD synthetic'", 'CTX19 LOAD output\n', 'LOAD_READY_ONLY ' + 'b' * 64)
    use = PROFILE.code_mode_spec(binding, "Write-Output 'USE synthetic'", 'CTX19 USE output\n', 'CTX19_USE_ONLY')
    return {'command': load['arguments']['cmd'], 'cwd': binding['cwd'], 'expected_argv': load['expected_argv'],
        'expected_output': load['expected_output'], 'ready_text': load['terminal_text'],
        'code_mode': {'LOAD': load, 'USE': use}, 'context_contract': manual_contract()}

def factory_input(basis_override=None):
    base = WORK / 'factory'; base.mkdir(exist_ok=True)
    index=1
    while (base/('input-'+str(index))).exists():index+=1
    root=base/('input-'+str(index));root.mkdir()
    def put(name, value):
        path = root / name
        path.write_text(json.dumps(value, sort_keys=True) + '\n', encoding='utf-8')
        return pin(path)
    def body(name, value):
        path = root / name; path.write_bytes(value.encode('utf-8')); return pin(path)
    basis = basis_override or 'c' * 64
    source = put('synthetic-source.json', {'synthetic_source': 'Hand-derived permission/AGENTS/environment grouping and filesystem diff'})
    inputs = [put('synthetic-input.json', {'LOAD_reads': 14, 'USE_reads': 16, 'permissions_and_agents_unchanged': True})]
    definitions = [('permissions','developer','permissions.instructions','developer_aggregate',PERMISSIONS,PERMISSIONS),
        ('agents','user','agents_md.instructions','user_aggregate',AGENTS,AGENTS),
        ('environment','user','environments.environment_context','user_aggregate',ENV_LOAD,ENV_USE)]
    producers=[]
    for index,(identity,role,kind,slot,load_body,use_body) in enumerate(definitions):
        load_state={'rendering_input': load_body};use_state={'rendering_input': use_body}
        common={'schema':'native-context-producer-v1','origin':'INDEPENDENT_SOURCE_INPUT','producer_id':identity,
            'source_pin':source,'basis_sha256':basis,'input_pins':inputs}
        load_receipt=dict(common,phase='LOAD',previous_state_sha256=None,state=load_state,branch='PRESENT',
            fragment=body(identity+'-LOAD.txt',load_body))
        use_receipt=dict(common,phase='USE',previous_state_sha256=sha(load_state),state=use_state,
            branch='UNCHANGED' if load_state==use_state else 'CHANGED',
            fragment=None if load_state==use_state else body(identity+'-USE.txt',use_body))
        producers.append({'id':identity,'family':'WORLD_STATE','source_pin':source,'role':role,'content_item_kind':kind,
            'initial_slot':slot,'initial_order':index,'delta_order':index,'standalone':False,
            'receipts':{'LOAD':put(identity+'-LOAD.json',load_receipt),'USE':put(identity+'-USE.json',use_receipt)}})
    population=put('population.json',{'schema':'native-context-population-v1','origin':'INDEPENDENT_SOURCE_INPUT',
        'source_commit':'b5bffd3ec4db487e7e3dec59663875b0ef7b72ca','basis_sha256':basis,
        'source_pins':[source],'input_pins':inputs,'producer_ids':[row['id'] for row in producers],'unresolved':[]})
    document={'schema':'native-context-input-v1','origin':'INDEPENDENT_SOURCE_INPUT','scope':'OFFLINE_SYNTHETIC',
        'status':'COMPLETE','unresolved':[],'source_commit':'b5bffd3ec4db487e7e3dec59663875b0ef7b72ca',
        'basis_sha256':basis,'source_pins':[source],'input_pins':inputs,'population_proof':population,'producers':producers,
        'phases':{name:{'wire':copy.deepcopy(manual_contract()['phases'][name]['wire']),'empty_prefix_proof':None} for name in ('LOAD','USE')}}
    return {'context_input':put('context-input.json',document)},basis,document

def policy(spec):
    schema_path = FIXTURES / 'ServerNotification.json'
    union = json.loads(schema_path.read_bytes())
    methods = [branch['properties']['method']['enum'][0] for branch in union['oneOf']]
    admitted=set(json.loads((FIXTURES/'synthetic.json').read_bytes())['admitted_public_methods'])
    matrix = {'schema_pin': pin(schema_path), 'rows': [{'method': method,
        'disposition': 'THREAD_STARTED' if method == 'thread/started' else ('CANARY' if method in admitted else 'ABORT')} for method in methods]}
    schemas = {name: pin(FIXTURES / (name + '.json')) for name in ('RawResponseItemCompletedNotification', 'RawResponseCompletedNotification')}
    return POLICY.NotificationPolicy({'schemas': schemas, 'visibility': {'load_spec': spec}}, matrix, schema_path, {})

def begin(staged, phase='LOAD', activate=True):
    settings=copy.deepcopy(json.loads((FIXTURES/'synthetic.json').read_bytes())['settings'])
    settings['cwd']=staged.load_spec['cwd']
    settings['activePermissionProfile']={'id':'worker_load' if phase=='LOAD' else 'worker_use','extends':None}
    if phase == 'LOAD':
        staged.bind_thread('context19-worker')
        staged.active.expected_settings = settings
    else:
        staged.release('synthetic-reviewed-release', settings)
    request = {'id': 5 if phase == 'LOAD' else 6, 'method': 'turn/start', 'params': {
        'threadId': staged.thread_id, 'cwd': settings['cwd'], 'approvalPolicy': 'never',
        'permissions': settings['activePermissionProfile']['id'], 'model': settings['model'], 'effort': settings['effort'],
        'environments': PROFILE.local_environment(settings['cwd']),
        'input': [{'type': 'text', 'text': 'submitted ' + phase + ' literal', 'text_elements': []}]}}
    if not activate:return request
    activate_request(staged,request)
    return request

def activate_request(staged,request,selected_policy=None):
    settings=staged.active.expected_settings
    phase='LOAD' if request['id']==5 else 'USE'
    staged.register_turn(request)
    turn_id = 'context19-turn-' + phase
    reply={'id':request['id'],'result':{'turn':{'id':turn_id,'status':'inProgress','items':[]}}}
    staged.response(reply)
    notifications=[{'method':'thread/settings/updated','params':{'threadId':staged.thread_id,'threadSettings':settings}},
        {'method':'turn/started','params':{'threadId':staged.thread_id,'turn':{'id':turn_id,'status':'inProgress','items':[]}}}]
    for message in notifications:
        if selected_policy:selected_policy.route(message,staged)
        staged.observe(message)
    return [reply]+notifications

def events(staged, phase):
    params = {'threadId': staged.thread_id, 'turnId': staged.turn_id}
    spec = staged.active.code_mode
    def raw(item): return {'method': 'rawResponseItem/completed', 'params': dict(params, item=item)}
    def typed(method, item):
        return {'method': method, 'params': dict(params, item=item,
            **{('startedAtMs' if method == 'item/started' else 'completedAtMs'): 1000000})}
    def context(identity, role, kinds, texts):
        return raw({'type': 'message', 'id': identity + '-' + phase, 'role': role,
            'content': [{'type': 'input_text', 'text': text} for text in texts],
            'internal_chat_message_metadata_passthrough': {'turn_id': staged.turn_id, 'create_time': 1001.25,
                'content_item_kinds': kinds}})
    prefix = ([context('ctx-permissions', 'developer', ['permissions.instructions'], [PERMISSIONS]),
               context('ctx-user', 'user', ['agents_md.instructions', 'environments.environment_context'], [AGENTS, ENV_LOAD])]
              if phase == 'LOAD' else [context('ctx-user', 'user', ['environments.environment_context'], [ENV_USE])])
    user = {'type': 'userMessage', 'id': 'typed-user-' + phase, 'clientId': None, 'content': copy.deepcopy(staged.request_content)}
    command = {'type': 'commandExecution', 'id': 'inner-' + phase, 'command': shlex.join(spec['expected_argv']),
        'cwd': spec['cwd'], 'commandActions': [], 'status': 'completed', 'exitCode': 0, 'aggregatedOutput': spec['expected_output']}
    ready = {'type': 'agentMessage', 'id': 'ready-' + phase, 'phase': 'final_answer', 'text': spec['terminal_text']}
    body = [{'type': 'input_text', 'text': 'Script completed\nWall time 0.1 seconds\nOutput:\n'},
        {'type': 'input_text', 'text': json.dumps({'chunk_id': 'cold-' + phase, 'wall_time_seconds': 0.1,
            'exit_code': 0, 'output': spec['expected_output']}, separators=(',', ':'))}]
    return prefix + [raw({'type': 'message', 'id': 'raw-user-' + phase, 'role': 'user',
        'content': [{'type': 'input_text', 'text': staged.request_input}],
        'internal_chat_message_metadata_passthrough': {'content_item_kinds': ['user.text']}}),
        typed('item/started', copy.deepcopy(user)), typed('item/completed', user),
        raw({'type': 'custom_tool_call', 'id': 'wrapper-' + phase, 'call_id': 'call-' + phase, 'name': 'exec', 'input': spec['wrapper_source']}),
        typed('item/started', dict(command, status='inProgress', exitCode=None, aggregatedOutput=None)), typed('item/completed', command),
        raw({'type': 'custom_tool_call_output', 'call_id': 'call-' + phase, 'output': body}),
        {'method': 'rawResponse/completed', 'params': dict(params, responseId='first-' + phase, usage=None, usageMetadata=None)},
        typed('item/started', dict(ready, text='')), typed('item/completed', ready),
        raw({'type': 'message', 'id': ready['id'], 'role': 'assistant', 'phase': 'final_answer', 'content': [{'type': 'output_text', 'text': ready['text']}]}),
        {'method': 'rawResponse/completed', 'params': dict(params, responseId='final-' + phase, usage=None, usageMetadata=None)}]

def consume(staged, selected_policy, rows):
    for row in rows:
        if selected_policy: selected_policy.route(row, staged)
        staged.observe(row)
    terminal = {'method': 'turn/completed', 'params': {'threadId': staged.thread_id, 'turn': {
        'id': staged.turn_id, 'status': 'completed', 'error': None, 'itemsView': 'full',
        'items': [copy.deepcopy(row['completed']) for row in staged.items.values()]}}}
    if selected_policy: selected_policy.route(terminal, staged)
    staged.observe(terminal)

class ContextContractTests(unittest.TestCase):
    def test_c91_36a_selected_context_policy_and_complete_LOAD(self):
        schema_path = FIXTURES / 'ServerNotification.json'
        schema_pin = pin(schema_path)
        self.assertEqual((schema_pin['bytes'], schema_pin['sha256']), (203001,
            'eb4317b57ce7cad32d6ab8a5b7d39eb765c8fb8f67acbc808dd6e55959411c93'))
        self.assertEqual(Path(schema_pin['path']).resolve(), schema_path.resolve())
        methods = [row['properties']['method']['enum'][0] for row in json.loads(schema_path.read_bytes())['oneOf']]
        canary = {'thread/settings/updated', 'turn/started', 'turn/completed',
                  'item/started', 'item/completed', 'item/agentMessage/delta'}
        # This reviewed literal oracle is independent of candidate matrix rows
        # and of the mutable fixture admitted_public_methods list.
        expected = {name: 'THREAD_STARTED' if name == 'thread/started' else
                    'CANARY' if name in canary else 'ABORT' for name in methods}
        spec = selection(); selected = policy(spec)
        self.assertEqual(selected.matrix, expected)
        self.assertEqual(len(selected.matrix), 81)
        self.assertEqual({kind: list(selected.matrix.values()).count(kind)
                          for kind in ('THREAD_STARTED', 'CANARY', 'ABORT')},
                         {'THREAD_STARTED': 1, 'CANARY': 6, 'ABORT': 74})
        self.assertEqual(selected.matrix['item/commandExecution/outputDelta'], 'ABORT')
        staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
        begin(staged); consume(staged, selected, events(staged, 'LOAD'))
        evidence = staged.qualify_load()
        self.assertTrue(staged.transport_complete()); self.assertTrue(selected.complete())
        self.assertEqual(evidence['command_item_id'], 'inner-LOAD')
        (WORK / 'C91-36A.json').write_text(json.dumps({'control': 'C91-36A', 'rows': 81,
            'semantic_oracle_matched': True, 'complete_synthetic_LOAD_reached': True,
            'candidate_schema_pin': schema_pin, 'native_credit': False}) + '\n', encoding='utf-8')

    def test_c91_36b_matrix_pin_drift_is_distinct_from_semantics(self):
        schema_path = FIXTURES / 'ServerNotification.json'
        selected = policy(selection())
        matrix = {'schema_pin': pin(schema_path), 'rows': [
            {'method': name, 'disposition': disposition} for name, disposition in selected.matrix.items()]}
        path = WORK / 'C91-36B-matrix.json'
        raw = (json.dumps(matrix, sort_keys=True) + '\n').encode('utf-8')
        path.write_bytes(raw)
        expected_pin = pin(path)  # Frozen before corruption; custody only.
        self.assertEqual(pin(path), expected_pin)
        path.write_bytes(raw + b' ')
        self.assertEqual(json.loads(path.read_bytes()), matrix)
        with self.assertRaises(AssertionError):
            self.assertEqual(pin(path), expected_pin)
        (WORK / 'C91-36B.json').write_text(json.dumps({'control': 'C91-36B',
            'frozen_expected_pin': expected_pin, 'observed_corrupt_pin': pin(path),
            'semantic_rows_unchanged': True, 'pin_drift_rejected': True,
            'owner': 'immutable input custody comparison; not NotificationPolicy matrix-file enforcement'}) + '\n', encoding='utf-8')

    def test_c91_36c_population_failures_reach_constructor_guard(self):
        schema_path = FIXTURES / 'ServerNotification.json'
        selected = policy(selection())
        matrix = {'schema_pin': pin(schema_path), 'rows': [
            {'method': name, 'disposition': disposition} for name, disposition in selected.matrix.items()]}
        observations = []
        constructor = POLICY.jsonschema.Draft7Validator
        with mock.patch.object(POLICY.jsonschema, 'Draft7Validator', wraps=constructor) as validators:
            positive = POLICY.NotificationPolicy(selected.plan, matrix, schema_path, {})
            self.assertEqual(positive.matrix, selected.matrix)
            self.assertEqual(validators.call_count, 3)
            positive_calls = validators.call_count
            for name in ('missing', 'duplicate'):
                with self.subTest(population=name):
                    candidate = copy.deepcopy(matrix)
                    if name == 'missing': candidate['rows'].pop()
                    else: candidate['rows'][-1] = copy.deepcopy(candidate['rows'][0])
                    self.assertEqual(candidate['schema_pin'], pin(schema_path))
                    validators.reset_mock()
                    with self.assertRaisesRegex(ValueError, 'Pinned 81-method schema or disposition population differs'):
                        POLICY.NotificationPolicy(selected.plan, candidate, schema_path, {})
                    validators.assert_not_called()
                    observations.append({'mutation': name, 'schema_pin_valid': True,
                                         'constructor_schema_validation_calls': validators.call_count})
        (WORK / 'C91-36C.json').write_text(json.dumps({'control': 'C91-36C',
            'positive_schema_validator_constructions': positive_calls, 'negative_guard_reach': observations,
            'refusal': 'Pinned 81-method schema or disposition population differs', 'native_credit': False}) + '\n', encoding='utf-8')

    def test_c91_36d_own_pin_cannot_authorize_semantic_substitution(self):
        schema_path = FIXTURES / 'ServerNotification.json'
        methods = [row['properties']['method']['enum'][0] for row in json.loads(schema_path.read_bytes())['oneOf']]
        canary = {'thread/settings/updated', 'turn/started', 'turn/completed',
                  'item/started', 'item/completed', 'item/agentMessage/delta'}
        expected = {name: 'THREAD_STARTED' if name == 'thread/started' else
                    'CANARY' if name in canary else 'ABORT' for name in methods}
        selected = policy(selection()); self.assertEqual(selected.matrix, expected)
        matrix = {'schema_pin': pin(schema_path), 'rows': [
            {'method': name, 'disposition': expected[name]} for name in methods]}
        next(row for row in matrix['rows'] if row['method'] == 'item/commandExecution/outputDelta')['disposition'] = 'TELEMETRY'
        path = WORK / 'C91-36D-substituted-matrix.json'
        path.write_text(json.dumps(matrix, sort_keys=True) + '\n', encoding='utf-8')
        own_pin = pin(path); self.assertEqual(pin(path), own_pin)
        constructor = POLICY.jsonschema.Draft7Validator
        with mock.patch.object(POLICY.jsonschema, 'Draft7Validator', wraps=constructor) as validators:
            accepted_structure = POLICY.NotificationPolicy(selected.plan, matrix, schema_path, {})
            self.assertEqual(validators.call_count, 3)
        self.assertEqual(len(accepted_structure.matrix), 81)
        self.assertIsNone(accepted_structure.first_anomaly)
        self.assertEqual(accepted_structure.matrix['item/commandExecution/outputDelta'], 'TELEMETRY')
        with self.assertRaises(AssertionError):
            self.assertEqual(accepted_structure.matrix, expected)
        (WORK / 'C91-36D.json').write_text(json.dumps({'control': 'C91-36D',
            'candidate_own_pin': own_pin, 'own_pin_matches': True, 'structural_constructor_accepted': True,
            'schema_validator_constructions': 3, 'independent_semantic_oracle_rejected': True,
            'runtime_semantic_enforcement_claimed': False}) + '\n', encoding='utf-8')

    def test_c91_36e_contrary_code_mode_policy_is_not_selected_context_policy(self):
        schema_path = FIXTURES / 'ServerNotification.json'
        methods = [row['properties']['method']['enum'][0] for row in json.loads(schema_path.read_bytes())['oneOf']]
        canary = {'thread/settings/updated', 'turn/started', 'turn/completed',
                  'item/started', 'item/completed', 'item/agentMessage/delta'}
        expected = {name: 'THREAD_STARTED' if name == 'thread/started' else
                    'CANARY' if name in canary else 'ABORT' for name in methods}
        selected = policy(selection()); self.assertEqual(selected.matrix, expected)
        # Exact contrasting policy_inputs rule: no thread/started override.
        contrary = {'schema_pin': pin(schema_path), 'rows': [
            {'method': name, 'disposition': 'CANARY' if name in canary else 'ABORT'} for name in methods]}
        constructed = POLICY.NotificationPolicy(selected.plan, contrary, schema_path, {})
        self.assertIsNone(constructed.first_anomaly)
        self.assertEqual([name for name in methods if constructed.matrix[name] != expected[name]], ['thread/started'])
        with self.assertRaises(AssertionError):
            self.assertEqual(constructed.matrix, expected)
        (WORK / 'C91-36E.json').write_text(json.dumps({'control': 'C91-36E', 'structural_constructor_accepted': True,
            'semantic_difference': {'thread/started': {'selected': 'THREAD_STARTED', 'contrary': 'ABORT'}},
            'scope': 'rejected for selected context fixture only; no global defect claim'}) + '\n', encoding='utf-8')

    def test_c91_36f_command_output_delta_reaches_selected_abort(self):
        spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
        selected = policy(spec)
        self.assertEqual(selected.matrix['item/commandExecution/outputDelta'], 'ABORT')
        request = begin(staged, activate=False); activate_request(staged, request, selected)
        for row in events(staged, 'LOAD'):
            selected.route(row, staged); staged.observe(row)
            if row['method'] == 'item/started' and row['params']['item']['type'] == 'commandExecution':
                break
        self.assertIn('inner-LOAD', staged.items)
        self.assertIsNone(staged.items['inner-LOAD']['completed'])
        before = copy.deepcopy(staged.items)
        selected.validator = mock.Mock(wraps=selected.validator)
        delta = {'method': 'item/commandExecution/outputDelta', 'params': {
            'threadId': staged.thread_id, 'turnId': staged.turn_id, 'itemId': 'inner-LOAD', 'delta': 'synthetic delta'}}
        with self.assertRaisesRegex(ValueError, 'Explicit notification abort: item/commandExecution/outputDelta'):
            selected.route(delta, staged)
        selected.validator.validate.assert_called_once()
        self.assertEqual(staged.items, before)
        self.assertEqual(selected.first_anomaly, 'Explicit notification abort: item/commandExecution/outputDelta')
        (WORK / 'C91-36F.json').write_text(json.dumps({'control': 'C91-36F',
            'active_bound_command_reached': True, 'public_schema_validation_calls': 1,
            'refusal': selected.first_anomaly, 'staged_items_unchanged': True, 'native_credit': False}) + '\n', encoding='utf-8')

    def test_c91_32_numeric_signed64_and_finite_boundaries(self):
        selected = policy(selection())
        positive = [-(2**63), 2**63 - 1, 0.5]
        for value in positive:
            selected.bounded(value)
        self.assertIsNone(selected.first_anomaly)
        observations = []
        for label, value, message in (
            ('below_signed64', -(2**63) - 1, 'Notification integer bound exceeded'),
            ('above_signed64', 2**63, 'Notification integer bound exceeded'),
            ('NaN', float('nan'), 'Non-finite notification JSON number'),
            ('positive_infinity', float('inf'), 'Non-finite notification JSON number'),
            ('negative_infinity', float('-inf'), 'Non-finite notification JSON number')):
            with self.subTest(boundary=label):
                bounded_policy = policy(selection())
                with self.assertRaisesRegex(ValueError, message): bounded_policy.bounded(value)
                self.assertEqual(bounded_policy.first_anomaly, message)
                observations.append({'case': label, 'refusal': message})
        (WORK / 'C91-32-NUMERIC.json').write_text(json.dumps({'control': 'C91-32-NUMERIC',
            'positive_values': positive, 'negatives': observations,
            'scope': 'existing numeric primitive guard; not full trace/native qualification'}, allow_nan=False) + '\n', encoding='utf-8')

    def test_existing_prepare_binds_context_to_requests_and_never_defaults_empty(self):
        base={'synthetic_source_selection':'independent-fixed-input'}
        core={'server_argv':['synthetic-only'],'server_cwd':'synthetic-cwd','thread_start':{'method':'thread/start'},
            'turn_start':{'params':{'permissions':'worker_load'}},'use_turn_start':{'params':{'permissions':'worker_use'}},
            'effective_config_projection':{'synthetic_only':True}}
        expected_basis=sha({'binding':base,'proposal':core})
        binding,_,_=factory_input(expected_basis);binding.update(base)
        with mock.patch.object(PROFILE,'_prepare_profile',side_effect=lambda *args,**kwargs:copy.deepcopy(core)):
            prepared=PROFILE.prepare(binding,{}, {},purpose='OFFLINE_FIXTURE')
            self.assertEqual(prepared['context_contract']['basis_sha256'],expected_basis)
            with self.assertRaises(ValueError):PROFILE.prepare(base,{}, {},purpose='OFFLINE_FIXTURE')
            first_pass=PROFILE.prepare_context_basis(base,{}, {},purpose='OFFLINE_FIXTURE')
            self.assertEqual(first_pass['status'],'CONTEXT_INPUT_REQUIRED');self.assertFalse(first_pass['native_attempt_enabled'])
            self.assertNotIn('context_contract',first_pass['profile_proposal_without_context'])
        changed=copy.deepcopy(core);changed['use_turn_start']['params']['permissions']='foreign-profile'
        with mock.patch.object(PROFILE,'_prepare_profile',return_value=changed),self.assertRaises(ValueError):
            PROFILE.prepare(binding,{}, {},purpose='OFFLINE_FIXTURE')

    def test_zero_byte_input_custody_is_distinct_from_empty_context(self):
        path=WORK/'zero-byte-independent-input';path.write_bytes(b'')
        spec=selection();spec['context_contract']['custody'].append(pin(path))
        error=None
        try:
            staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
            begin(staged);consume(staged,selected_policy,events(staged,'LOAD'))
        except ValueError as exc:error=str(exc)
        self.assertIsNone(error,'A pinned empty input file cannot erase or invalidate the nonempty expected context prefix')

    def test_source_initial_standalone_does_not_force_USE_standalone(self):
        binding,basis,document=factory_input();root=Path(binding['context_input']['path']).parent
        def write(path,value):path.write_text(json.dumps(value)+'\n',encoding='utf-8');return pin(path)
        # A caller-created standalone initial slot is distinct from the
        # requires_separate_message flag used by merge_contextual_fragments.
        producer=document['producers'][0];producer['initial_slot']='developer_standalone';producer['standalone']=False
        binding['context_input']=write(Path(binding['context_input']['path']),document)
        contract=None
        try:contract=PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        except ValueError:pass
        self.assertIsNotNone(contract,'Initial grouping must not invent a different USE requires_separate_message value')
        self.assertEqual(contract['phases']['LOAD']['rows'][0]['role'],'developer')

    def test_synthetic_context_cannot_enter_actual_capture(self):
        capture=load(SOURCE/'skills/implementaudit/scripts/native-capture-adapter/capture.py','ctx19_capture_scope')
        plan={'visibility':{'load_spec':selection()}}
        with mock.patch.object(capture,'preflight',return_value=(plan,None,None)),mock.patch.object(capture,'worker_runtime',return_value=None):
            with self.assertRaisesRegex(ValueError,'Synthetic context'):
                capture.capture('synthetic-plan','no-native-attempt',bundle_root=WORK,pins_sha256='f'*64)

    def full_staged_witness(self, mode):
        binding,basis,_=factory_input()
        spec=selection();spec['context_contract']=PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
        load_request=begin(staged,activate=False)
        use_request=copy.deepcopy(load_request);use_request['id']=6;use_request['params']['permissions']='worker_use'
        use_request['params']['input']=[{'type':'text','text':'submitted USE literal','text_elements':[]}]
        use_settings=copy.deepcopy(staged.expected_settings);use_settings['activePermissionProfile']={'id':'worker_use','extends':None}
        run=WORK/('synthetic-staged-'+mode);run.mkdir(exist_ok=True)
        # Each invocation receives a new attempt directory; never overwrite a previous witness.
        if (run/'LOAD_READY.json').exists():
            suffix=1
            while (WORK/(run.name+'-'+str(suffix))).exists():suffix+=1
            run=WORK/(run.name+'-'+str(suffix));run.mkdir()
        parent=run/'synthetic-parent.jsonl'
        parent_meta=(json.dumps({'type':'session_meta','payload':{'id':'context19-synthetic-parent'}})+'\n').encode()
        parent.write_bytes(parent_meta+(b'{"synthetic_padding":true}\n' if mode=='retroactive' else b''))
        identity={'selected_child':None,'logical_task':'context19_synthetic','parent_thread_id':'context19-synthetic-parent',
            'transaction_ref':'synthetic-non-authorizing','source_sha256':'d'*64,'reason':'exercise a synthetic context contract'}
        cfg={'identity':identity,'phase_capable_source_adoption':{'synthetic_only':True},'runtime_selection_acceptance':{'synthetic_only':True},
            'ack_timeout_seconds':1,'load_input':copy.deepcopy(load_request['params']['input']),
            'use_input':copy.deepcopy(use_request['params']['input']),'parent_rollout':str(parent),'parent_launch_offset':len(parent_meta)}
        plan={'purpose':'ISOLATED_QUALIFICATION','binding':{'load_pins':{'child_source':{'sha256':'d'*64}}},
            'visibility':cfg,'turn_start':load_request,'use_turn_start':use_request,'expected_turn_settings':{'USE':use_settings}}
        pending=[];recorded=[];sent=[];inspected=[];clock=[0.0]
        def response(request):
            sent.append(copy.deepcopy(request));recorded.extend(activate_request(staged,request,selected_policy))
            pending.extend(events(staged,'LOAD' if request['id']==5 else 'USE'));pending.append(None)
        def wait_event():
            self.assertTrue(pending,'Synthetic event source exhausted before completion')
            row=pending.pop(0)
            if row is None:
                row={'method':'turn/completed','params':{'threadId':staged.thread_id,'turn':{'id':staged.turn_id,
                    'status':'completed','error':None,'itemsView':'full','items':[copy.deepcopy(item['completed']) for item in staged.items.values()]}}}
            selected_policy.route(row,staged);staged.observe(row);recorded.append(copy.deepcopy(row));clock[0]+=.001
        def flush_raw():
            self.assertEqual(staged.phase,'LOAD');self.assertTrue(staged.transport_complete())
            payloads={'stdout.bin':b''.join((json.dumps(row)+'\n').encode() for row in recorded),
                'stderr.bin':b'', 'sent.jsonl':b''.join((json.dumps(row)+'\n').encode() for row in sent)}
            result=[]
            for name,raw in payloads.items():
                path=run/name;path.write_bytes(raw);result.append(pin(path))
            return result
        def relay(*args,**kwargs):
            ready_raw=(run/'LOAD_READY.json').read_bytes();ready=json.loads(ready_raw);ready_sha=hashlib.sha256(ready_raw).hexdigest()
            self.assertEqual([row['id'] for row in sent],[5]);self.assertEqual(staged.phase,'LOAD')
            self.assertEqual(ready['load_evidence']['code_mode']['context_rows_consumed'],2)
            self.assertEqual(ready['load_evidence']['code_mode']['context_contract_sha256'],staged.context_contract_sha256)
            inspected.append(ready_sha)
            if mode=='ack_timeout':return
            marker=('```ini\nISOLATED_QUALIFICATION=LOAD_READY\nLOGICAL_TASK=context19_synthetic\nWORKER_TASK=context19-worker\n'
                'SOURCE_SHA256='+('d'*64)+'\nPROCESS_PID=17001\nPROCESS_BIRTH_FILETIME_100NS=1700001\nLOAD_READY_SHA256='+ready_sha+'\n```\n'
                'The isolated qualification task context19_synthetic has loaded the bound source to exercise a synthetic context contract.')
            line=(json.dumps({'type':'response_item','synthetic_only':True,'payload':{'type':'message','role':'assistant','phase':'commentary',
                'content':[{'type':'output_text','text':marker}]}},separators=(',',':'))+'\n').encode()
            if mode=='retroactive':parent.write_bytes(parent_meta+line);offset=len(parent_meta)
            else:
                offset=parent.stat().st_size
                with parent.open('ab') as stream:stream.write(line)
            ack={'ready_sha256':ready_sha,'parent_row_offset':offset,'parent_row_bytes':len(line),'parent_row_sha256':hashlib.sha256(line).hexdigest()}
            (run/'PARENT_VISIBILITY_ACK.json').write_text(json.dumps(ack)+'\n',encoding='utf-8')
        outcome=None
        try:
            outcome=VISIBILITY.staged_turns(plan=plan,canary=staged,response=response,check_deadline=lambda:None,
                wait_event=wait_event,process_identity={'pid':17001,'creation_filetime_100ns':1700001},
                flush_raw=flush_raw,run=run,clock=lambda:clock[0],pause=lambda _:clock.__setitem__(0,clock[0]+2),relay=relay)
        except ValueError:
            if mode=='success':raise
        self.assertEqual(len(inspected),1)
        self.assertNotIn('CTX19_PRIVATE',json.dumps([staged.snapshot(),selected_policy.snapshot(),outcome]))
        if mode=='success':
            self.assertEqual([row['id'] for row in sent],[5,6]);self.assertTrue(selected_policy.complete())
            self.assertEqual(outcome['status'],'TWO_TURN_TRANSPORT_COMPLETE_NONVERDICT')
        else:
            self.assertIsNone(outcome);self.assertEqual([row['id'] for row in sent],[5])
            self.assertIsNotNone(staged.first_anomaly);self.assertFalse((run/'RELEASE.json').exists())
            with self.assertRaises(ValueError):staged.release('late-repair',use_settings)
        (run/'SYNTHETIC_WITNESS.json').write_text(json.dumps({'mode':mode,'native_execution':False,
            'actual_ROOT_or_parent_ACK':False,'fake_transport_request_ids':[row['id'] for row in sent],
            'independent_input':binding['context_input'],'source_context_contract_sha256':sha(spec['context_contract']),
            'private_real_bodies_used':False,'first_anomaly':staged.first_anomaly},indent=2)+'\n',encoding='utf-8')

    def test_full_factory_context_inspection_ACK_and_USE_with_fake_transport(self):
        self.full_staged_witness('success')

    def test_retroactive_or_timed_out_ACK_cannot_release_USE(self):
        self.full_staged_witness('retroactive');self.full_staged_witness('ack_timeout')

    def test_empty_context_requires_complete_independent_omission_proof(self):
        binding,basis,document=factory_input();root=Path(binding['context_input']['path']).parent
        def write(path,value):path.write_text(json.dumps(value)+'\n',encoding='utf-8');return pin(path)
        inputs=[write(root/'synthetic-input.json',{'synthetic_absent_branch':True})];document['input_pins']=inputs
        for producer in document['producers']:
            for phase in ('LOAD','USE'):
                path=Path(producer['receipts'][phase]['path']);receipt=json.loads(path.read_bytes())
                receipt.update(input_pins=inputs,state={'enabled':False},branch='ABSENT' if phase=='LOAD' else 'UNCHANGED',fragment=None,
                    previous_state_sha256=None if phase=='LOAD' else sha({'enabled':False}))
                producer['receipts'][phase]=write(path,receipt)
        population=json.loads(Path(document['population_proof']['path']).read_bytes());population['input_pins']=inputs
        document['population_proof']=write(Path(document['population_proof']['path']),population)
        for phase in ('LOAD','USE'):
            document['phases'][phase]['empty_prefix_proof']=write(root/('empty-'+phase+'.json'),
                {'schema':'native-context-empty-v1','origin':'INDEPENDENT_SOURCE_INPUT','phase':phase,'basis_sha256':basis,
                 'producer_receipts':[row['receipts'][phase] for row in document['producers']]})
        binding['context_input']=write(Path(binding['context_input']['path']),document)
        contract=PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        self.assertEqual(contract['phases']['LOAD']['rows'],[]);self.assertEqual(contract['phases']['USE']['rows'],[])
        spec=selection();spec['context_contract']=contract;staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
        begin(staged);consume(staged,selected_policy,events(staged,'LOAD')[2:]);staged.qualify_load()
        begin(staged,'USE');consume(staged,selected_policy,events(staged,'USE')[1:]);self.assertTrue(staged.transport_complete())
        document['phases']['USE']['empty_prefix_proof']=None;binding['context_input']=write(Path(binding['context_input']['path']),document)
        with self.assertRaises(ValueError):PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')

    def guard_refuses(self, edit, spec_edit=None, before_start=False):
        for guard in ('policy','observer'):
            spec=selection()
            if spec_edit:spec_edit(spec)
            staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
            request=begin(staged,activate=not before_start)
            if before_start:
                staged.register_turn(request)
                staged.response({'id':5,'result':{'turn':{'id':'context19-turn-LOAD','status':'inProgress','items':[]}}})
            rows=events(staged,'LOAD');edit(rows)
            rejected=False
            try:
                for event in rows:
                    if guard=='policy':selected_policy.route(event,staged)
                    else:staged.observe(event)
            except ValueError:
                rejected=True
            with self.subTest(guard=guard):
                self.assertTrue(rejected)
                monitor=selected_policy if guard=='policy' else staged
                self.assertIsNotNone(monitor.first_anomaly)
                first=monitor.first_anomaly
                with self.assertRaises(ValueError):
                    if guard=='policy':selected_policy.route(events(staged,'LOAD')[0],staged)
                    else:staged.observe(events(staged,'LOAD')[0])
                self.assertEqual(first,monitor.first_anomaly)
                self.assertNotIn('CTX19_PRIVATE',json.dumps([staged.snapshot(),selected_policy.snapshot()]))

    def test_known_kind_wrong_body_length_or_commitment_refuses(self):
        edits={
            'same_length_body':lambda rows:rows[0]['params']['item']['content'][0].__setitem__('text',PERMISSIONS.replace('CTX19','CTX18')),
            'added_byte':lambda rows:rows[0]['params']['item']['content'][0].__setitem__('text',PERMISSIONS+' '),
            'invalid_utf8_string':lambda rows:rows[0]['params']['item']['content'][0].__setitem__('text',chr(0xd800)),
            'wrong_type':lambda rows:rows[0]['params']['item']['content'][0].__setitem__('text',None)}
        for name,edit in edits.items():
            with self.subTest(case=name):self.guard_refuses(edit)
        for key,value in [('sha256','f'*64),('bytes',len(PERMISSIONS.encode())+1)]:
            with self.subTest(expected=key):self.guard_refuses(lambda rows:None,
                lambda spec,key=key,value=value:spec['context_contract']['phases']['LOAD']['rows'][0]['content'][0].__setitem__(key,value))

    def test_role_order_cardinality_and_split_merge_refuse(self):
        def split(rows):
            original=rows.pop(1)
            for index in (1,0):
                part=copy.deepcopy(original);item=part['params']['item'];item['id']+='-'+str(index)
                item['content']=[item['content'][index]]
                item['internal_chat_message_metadata_passthrough']['content_item_kinds']=[item['internal_chat_message_metadata_passthrough']['content_item_kinds'][index]]
                rows.insert(1,part)
        def merge(rows):
            second=rows.pop(1)['params']['item'];first=rows[0]['params']['item']
            first['content']+=second['content']
            first['internal_chat_message_metadata_passthrough']['content_item_kinds']+=second['internal_chat_message_metadata_passthrough']['content_item_kinds']
        edits={
            'role':lambda rows:rows[0]['params']['item'].__setitem__('role','user'),
            'rows':lambda rows:rows.insert(0,rows.pop(1)),
            'ordered_kinds':lambda rows:rows[1]['params']['item']['internal_chat_message_metadata_passthrough']['content_item_kinds'].reverse(),
            'ordered_bodies':lambda rows:rows[1]['params']['item']['content'].reverse(),
            'missing_content':lambda rows:rows[1]['params']['item']['content'].pop(),
            'split':split,'merge':merge}
        for name,edit in edits.items():
            with self.subTest(case=name):self.guard_refuses(edit)

    def test_missing_extra_duplicate_unknown_and_self_claimed_context_refuse(self):
        edits={
            'missing_first':lambda rows:rows.pop(0),
            'missing_last':lambda rows:rows.pop(1),
            'duplicate':lambda rows:rows.insert(1,copy.deepcopy(rows[0])),
            'unknown_extension':lambda rows:rows[0]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('content_item_kinds',['unknown_extension.instructions']),
            'metadata_capability':lambda rows:rows[0]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('cell_id','claimed-authority'),
            'metadata_oracle':lambda rows:rows[0]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('expected_sha256',content_commitment(PERMISSIONS)['sha256']),
            'extra_item_field':lambda rows:rows[0]['params']['item'].__setitem__('context_verified',True),
            'context_as_submitted':lambda rows:rows[1]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('content_item_kinds',['user.text'])}
        for name,edit in edits.items():
            with self.subTest(case=name):self.guard_refuses(edit)

    def test_worker_turn_phase_timestamp_and_prefix_boundaries_refuse(self):
        edits={
            'worker':lambda rows:rows[0]['params'].__setitem__('threadId','foreign-worker'),
            'turn':lambda rows:rows[0]['params'].__setitem__('turnId','foreign-turn'),
            'phase':lambda rows:rows[0]['params']['item'].__setitem__('phase','final_answer'),
            'wrong_USE_body':lambda rows:rows[1]['params']['item']['content'][1].__setitem__('text',ENV_USE),
            'time_outside':lambda rows:rows[0]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('create_time',1061),
            'boolean_time':lambda rows:rows[0]['params']['item']['internal_chat_message_metadata_passthrough'].__setitem__('create_time',True),
            'late_context':lambda rows:rows.insert(3,copy.deepcopy(rows[0])),
            'reused_context_id':lambda rows:rows[1]['params']['item'].__setitem__('id',rows[0]['params']['item']['id'])}
        for name,edit in edits.items():
            with self.subTest(case=name):self.guard_refuses(edit)
        self.guard_refuses(lambda rows:None,before_start=True)

    def test_explicit_absent_and_nullable_ID_contracts(self):
        for mode in ('absent','null','absent_or_null'):
            spec=selection();spec['context_contract']['phases']['LOAD']['wire']['id']=mode
            staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec);begin(staged)
            rows=events(staged,'LOAD')
            for event in rows[:2]:
                if mode=='absent':event['params']['item'].pop('id')
                else:event['params']['item']['id']=None
            with self.subTest(mode=mode):
                consume(staged,selected_policy,rows);staged.qualify_load();self.assertTrue(staged.transport_complete())
        self.guard_refuses(lambda rows:rows[0]['params']['item'].pop('id'))

    def test_contract_is_frozen_and_policy_observer_disagreement_refuses(self):
        spec=selection();staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
        spec['context_contract']['phases']['LOAD']['rows'][0]['content'][0]['sha256']='f'*64
        begin(staged);consume(staged,selected_policy,events(staged,'LOAD'));self.assertTrue(staged.transport_complete())
        spec=selection();staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec)
        spec['context_contract']['basis_sha256']='f'*64;selected_policy=policy(spec);begin(staged)
        with self.assertRaises(ValueError):selected_policy.route(events(staged,'LOAD')[0],staged)

    def test_missing_malformed_or_inconsistent_expectations_refuse_before_input(self):
        edits=[lambda spec:spec.pop('context_contract'),
            lambda spec:spec['context_contract'].__setitem__('scope','OBSERVED_FRAME'),
            lambda spec:spec['context_contract']['phases']['USE'].__setitem__('previous_state_sha256','f'*64),
            lambda spec:spec['context_contract']['phases']['LOAD'].__setitem__('rows',[]),
            lambda spec:spec['context_contract']['phases'].__setitem__('LOAD',None)]
        for edit in edits:
            for guard in ('policy','observer'):
                spec=selection();edit(spec)
                with self.subTest(guard=guard,edit=edits.index(edit)),self.assertRaises(ValueError):
                    if guard=='policy':policy(spec)
                    else:VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec)

    def test_malformed_rejected_frame_cannot_escape_failure_latch(self):
        self.guard_refuses(lambda rows:rows[0]['params'].__setitem__('item',None))

    def test_failure_timeout_or_incomplete_prefix_prevents_READY_and_USE(self):
        for failure in ('timeout','source_error'):
            spec=selection();staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec)
            request=begin(staged,activate=False);run=WORK/('failed-'+failure)
            visible=[]
            plan={'turn_start':request,'visibility':{'identity':{'selected_child':'audit-state'},
                'phase_capable_source_adoption':{'synthetic_only':True},'runtime_selection_acceptance':{'synthetic_only':True},
                'ack_timeout_seconds':1,'load_input':copy.deepcopy(request['params']['input'])}}
            def response(value):
                if failure=='source_error':raise ValueError('synthetic source error')
                activate_request(staged,value)
            def timeout():raise TimeoutError('synthetic held prefix timeout')
            with self.subTest(failure=failure),self.assertRaises(ValueError):
                VISIBILITY.staged_turns(plan=plan,canary=staged,response=response,check_deadline=timeout,
                    wait_event=lambda:None,process_identity={'synthetic_only':True},
                    flush_raw=lambda:self.fail('Incomplete prefix must not flush READY'),run=run,
                    relay=lambda *args,**kwargs:visible.append(args))
            self.assertIsNotNone(staged.first_anomaly);self.assertFalse(visible)
            self.assertFalse((run/'LOAD_READY.json').exists())
            with self.assertRaises(ValueError):staged.release('early-ACK',{'activePermissionProfile':{'id':'worker_use','extends':None}})
        staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,selection());begin(staged)
        with self.assertRaises(ValueError):staged.qualify_load()
        self.assertIsNotNone(staged.first_anomaly,'Rejected incomplete qualification must latch')

    def test_existing_F1_F2_and_complete_output_boundaries_remain(self):
        edits={
            'first_response_before_call':lambda rows:rows.insert(5,rows.pop(9)),
            'final_response_before_final_item':lambda rows:rows.insert(12,rows.pop(13)),
            'typed_user_contradiction':lambda rows:rows[4]['params']['item']['content'][0].__setitem__('text','different user'),
            'inner_output_truncated':lambda rows:rows[7]['params']['item'].__setitem__('aggregatedOutput','partial')}
        for name,edit in edits.items():
            spec=selection();staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec);begin(staged)
            rows=events(staged,'LOAD');edit(rows)
            with self.subTest(case=name),self.assertRaises(ValueError):consume(staged,selected_policy,rows)
        spec=selection();staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec);begin(staged)
        rows=events(staged,'LOAD');rows.insert(6,rows.pop(9));consume(staged,selected_policy,rows)
        self.assertTrue(staged.transport_complete(),'Allowed first-response overlap with inner future must survive')

    def test_factory_rejects_changed_missing_unresolved_or_circular_inputs(self):
        def save(binding,document):
            path=Path(binding['context_input']['path']);path.write_text(json.dumps(document)+'\n',encoding='utf-8');binding['context_input']=pin(path)
        mutations={
            'unresolved':lambda document:document.__setitem__('unresolved',['dynamic environment body']),
            'observed_oracle':lambda document:document.__setitem__('origin','OBSERVED_FRAME'),
            'wrong_basis':lambda document:document.__setitem__('basis_sha256','f'*64),
            'wrong_source':lambda document:document.__setitem__('source_commit','f'*40),
            'missing_producer':lambda document:document['producers'].pop(),
            'duplicate_order':lambda document:document['producers'][1].__setitem__('initial_order',0)}
        for name,edit in mutations.items():
            binding,basis,document=factory_input();edit(document);save(binding,document)
            with self.subTest(case=name),self.assertRaises(ValueError):PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        binding,basis,document=factory_input()
        with self.assertRaises(ValueError):PROFILE.context_contract_from_input({},basis,purpose='OFFLINE_FIXTURE')
        with self.assertRaises(ValueError):PROFILE.context_contract_from_input(binding,basis,purpose='ISOLATED_QUALIFICATION')
        path=Path(document['input_pins'][0]['path']);path.write_text('{}\n',encoding='utf-8')
        with self.assertRaises(ValueError):PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        for name in ('wrong_previous','blind_LOAD_replay','circular_body'):
            binding,basis,document=factory_input();producer=document['producers'][0]
            receipt=json.loads(Path(producer['receipts']['USE']['path']).read_bytes())
            if name=='wrong_previous':receipt['previous_state_sha256']='f'*64
            elif name=='blind_LOAD_replay':
                receipt['branch']='CHANGED';receipt['fragment']=json.loads(Path(producer['receipts']['LOAD']['path']).read_bytes())['fragment']
            else:
                producer=document['producers'][2];receipt=json.loads(Path(producer['receipts']['USE']['path']).read_bytes())
                receipt['fragment']=binding['context_input']
            path=Path(producer['receipts']['USE']['path']);path.write_text(json.dumps(receipt)+'\n',encoding='utf-8');producer['receipts']['USE']=pin(path)
            save(binding,document)
            with self.subTest(case=name),self.assertRaises(ValueError):PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')

    def test_factory_derives_source_grouping_and_changed_USE(self):
        binding,basis,_=factory_input()
        try:
            contract=PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')
        except AttributeError:
            contract=None
        self.assertIsNotNone(contract,'Factory must derive expectations from independent source/input receipts')
        self.assertEqual([row['content_item_kinds'] for row in contract['phases']['LOAD']['rows']],
            [['permissions.instructions'],['agents_md.instructions','environments.environment_context']])
        self.assertEqual([row['content_item_kinds'] for row in contract['phases']['USE']['rows']],
            [['environments.environment_context']])
        spec=selection();spec['context_contract']=contract
        staged=VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol,spec);selected_policy=policy(spec)
        begin(staged);consume(staged,selected_policy,events(staged,'LOAD'));staged.qualify_load()
        begin(staged,'USE');consume(staged,selected_policy,events(staged,'USE'))
        self.assertTrue(staged.transport_complete())

    def test_complete_independently_bound_LOAD_and_USE_prefixes(self):
        spec = selection()
        staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
        selected_policy = policy(spec)
        error = None
        try:
            begin(staged)
            consume(staged, selected_policy, events(staged, 'LOAD'))
            load_proof = staged.qualify_load()
            begin(staged, 'USE')
            consume(staged, selected_policy, events(staged, 'USE'))
        except ValueError as exc:
            error = str(exc)
        self.assertIsNone(error, 'Matching independent source contexts must pass: ' + str(error))
        self.assertTrue(staged.transport_complete())
        self.assertTrue(selected_policy.complete())
        public = json.dumps([staged.snapshot(), selected_policy.snapshot(), load_proof])
        self.assertNotIn('CTX19_PRIVATE', public)
        self.assertEqual(len(staged.items), 3, 'Context cannot enter the submitted-user/command/readiness census')

    def test_rejected_unknown_methods_omit_private_bodies_in_both_guards(self):
        private = 'PRIVACY_TEST_SENTINEL diagnostic label'
        for pipeline in (False, True):
            # The exact REVIEW30-F1 discriminator changes only method. The same
            # independent context bytes pass and remain private when recognized.
            spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
            selected_policy = policy(spec) if pipeline else None; begin(staged)
            recognized = events(staged, 'LOAD')[0]
            if selected_policy: self.assertEqual(selected_policy.route(recognized, staged), 'CANARY')
            staged.observe(recognized)
            self.assertNotIn('CTX19_PRIVATE', json.dumps([staged.snapshot(), selected_policy.snapshot() if selected_policy else None]))
            for variant in ('unknown_method', 'method_body'):
                with self.subTest(pipeline=pipeline, variant=variant):
                    spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
                    selected_policy = policy(spec) if pipeline else None
                    begin(staged)
                    message = events(staged, 'LOAD')[0]
                    if variant == 'unknown_method': message['method'] = 'rawResponseItem/review30Unknown'
                    else: message['method'] = private
                    original = copy.deepcopy(message)
                    raw = json.dumps(message, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
                    with self.assertRaises(ValueError):
                        if selected_policy: selected_policy.route(message, staged)
                        staged.observe(message)
                    self.assertEqual(message, original)
                    public = json.dumps([staged.snapshot(), selected_policy.snapshot() if selected_policy else None])
                    self.assertNotIn('CTX19_PRIVATE', public)
                    self.assertNotIn(private, public)
                    monitor = selected_policy if selected_policy else staged
                    self.assertTrue(any(row.get('sha256') == hashlib.sha256(raw).hexdigest()
                        and row.get('bytes') == len(raw) and row.get('private_body_omitted') is True
                        for row in monitor.frames))
                    first = monitor.first_anomaly
                    self.assertTrue(first)
                    with self.assertRaises(ValueError):
                        valid = events(staged, 'LOAD')[0]
                        if selected_policy: selected_policy.route(valid, staged)
                        staged.observe(valid)
                    self.assertEqual(monitor.first_anomaly, first)

    def test_policy_schema_acceptance_does_not_publish_failed_readiness(self):
        private = 'PRIVACY_TEST_SENTINEL invalid readiness'
        for variant in ('started', 'completed', 'delta'):
            with self.subTest(variant=variant):
                spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
                selected_policy = policy(spec); begin(staged)
                rows = events(staged, 'LOAD')
                start = next(i for i, row in enumerate(rows) if row['method'] == 'item/started'
                    and row['params']['item']['type'] == 'agentMessage')
                for row in rows[:start]:
                    selected_policy.route(row, staged)
                    staged.observe(row)
                if variant == 'started':
                    bad = copy.deepcopy(rows[start]); bad['params']['item']['text'] = private
                else:
                    selected_policy.route(rows[start], staged)
                    staged.observe(rows[start])
                    if variant == 'completed':
                        bad = copy.deepcopy(rows[start + 1]); bad['params']['item']['text'] = private
                    else:
                        bad = {'method': 'item/agentMessage/delta', 'params': {'threadId': staged.thread_id,
                            'turnId': staged.turn_id, 'itemId': rows[start]['params']['item']['id'], 'delta': private}}
                original = copy.deepcopy(bad)
                self.assertEqual(selected_policy.route(bad, staged), 'CANARY')
                policy_before_observe = json.dumps(selected_policy.snapshot())
                with self.assertRaises(ValueError): staged.observe(bad)
                self.assertEqual(bad, original)
                if variant in ('started', 'delta'):
                    # Semantic validation still receives full working bytes;
                    # they are not made public to preserve readiness checks.
                    history = getattr(staged.active, '_protocol_frames', staged.active.frames)
                    self.assertIn(bad, history)
                self.assertNotIn(private, policy_before_observe)
                self.assertNotIn(private, json.dumps([staged.snapshot(), selected_policy.snapshot()]))
                first = staged.first_anomaly; self.assertTrue(first)
                self.assertFalse(staged.transport_complete())
                self.assertIsNone(staged.release_digest)
                later = copy.deepcopy(rows[start])
                self.assertEqual(selected_policy.route(later, staged), 'CANARY')
                with self.assertRaises(ValueError): staged.observe(later)
                self.assertEqual(staged.first_anomaly, first)
                self.assertTrue(selected_policy.frames[-1].get('private_body_omitted'))

    def test_accepted_public_diagnostics_preserve_LOAD_and_USE_outputs(self):
        spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
        selected_policy = policy(spec); begin(staged)
        load_rows = events(staged, 'LOAD')
        for row in load_rows:
            self.assertEqual(selected_policy.route(row, staged), 'CANARY')
            if row['method'] in ('item/started', 'item/completed'):
                self.assertNotIn(row, selected_policy.frames)
            staged.observe(row)
        consume(staged, selected_policy, [])  # Only the terminal; no prefix replay.
        public_rows = [row for row in load_rows if row['method'] in ('item/started', 'item/completed')]
        self.assertTrue(all(row in staged.frames and row in selected_policy.frames for row in public_rows))
        self.assertEqual(staged.public_final_messages(), staged.final_messages())
        load_frames = copy.deepcopy(staged.frames)
        staged.qualify_load(); begin(staged, 'USE')
        consume(staged, selected_policy, events(staged, 'USE'))
        self.assertTrue(staged.transport_complete()); self.assertTrue(selected_policy.complete())
        self.assertEqual(staged.load_snapshot['frames'], load_frames)
        self.assertEqual(staged.public_final_messages(), staged.final_messages())
        self.assertNotIn('CTX19_PRIVATE', json.dumps([staged.snapshot(), selected_policy.snapshot(), staged.public_final_messages()]))

    def test_unadmitted_tail_omits_untrusted_labels_and_invalid_UTF8(self):
        private = 'PRIVACY_TEST_SENTINEL unadmitted identity'
        spec = selection(); staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec); begin(staged)
        with self.assertRaises(ValueError): staged.observe({'method': 'unknown/privacy-abort', 'params': {}})
        first = staged.first_anomaly; self.assertTrue(first)
        accepted_items = copy.deepcopy(staged.items)
        bad = events(staged, 'LOAD')[0]
        bad['method'] = private; bad['params']['threadId'] = private; bad['params']['item']['id'] = private
        original = copy.deepcopy(bad)
        staged.record_unadmitted(bad)
        self.assertEqual(bad, original)
        self.assertNotIn(private, json.dumps(staged.snapshot()))
        self.assertNotIn('CTX19_PRIVATE', json.dumps(staged.snapshot()))
        staged.record_unadmitted({'method': '\ud800'})
        self.assertTrue(all(row.get('semantic_credit') is False and row.get('private_body_omitted') is True
                            for row in staged.unadmitted_raw_tail))
        self.assertTrue(staged.unadmitted_raw_tail[-1].get('invalid_json_utf8'))
        self.assertEqual(staged.first_anomaly, first); self.assertEqual(staged.items, accepted_items)
        with self.assertRaises(ValueError): staged.observe(events(staged, 'LOAD')[0])
        self.assertEqual(staged.first_anomaly, first); self.assertFalse(staged.transport_complete())

def main():
    global SOURCE, FIXTURES, WORK, PROFILE, PROTOCOL, POLICY, VISIBILITY
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--fixtures', type=Path)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    SOURCE = args.source.resolve()
    FIXTURES = (args.fixtures or SOURCE / 'fixtures/codex-recovery/native-code-mode').resolve()
    provenance=json.loads((FIXTURES/'PROVENANCE.json').read_bytes())
    assert {row['path'] for row in provenance['files']}=={'ServerNotification.json','RawResponseItemCompletedNotification.json','RawResponseCompletedNotification.json','synthetic.json'}
    for row in provenance['files']:
        actual=pin(FIXTURES/row['path'])
        assert (actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256'])
    WORK = args.work.resolve(); WORK.mkdir(parents=True, exist_ok=True)
    module_dir = SOURCE / 'skills/implementaudit/scripts/native-capture-adapter'
    PROFILE, PROTOCOL, POLICY, VISIBILITY = [load(module_dir / (name + '.py'), 'ctx19_' + name)
        for name in ('worker_profile', 'canary_protocol', 'notification_policy', 'load_visibility')]
    def forbid(event, arguments):
        if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'ctypes.dlopen', 'os.putenv', 'os.unsetenv') or event.startswith('socket.'):
            raise AssertionError('Cold controls forbid process/network/environment effects')
    sys.addaudithook(forbid)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContextContractTests))
    args.log.write_text(log.getvalue(), encoding='utf-8')
    print(json.dumps({'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors), 'synthetic_only': True}))
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__': raise SystemExit(main())
