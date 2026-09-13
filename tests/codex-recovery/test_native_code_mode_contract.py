"""Synthetic protocol controls only. Never a native trace, model call or authority."""
import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import shlex
import sys
import unittest
import hashlib
import tempfile

PROFILE = PROTOCOL = VISIBILITY = SOURCE = FIXTURES = DATA = WORK = None

SCHEMA_FILES = ('ServerNotification.json','RawResponseItemCompletedNotification.json','RawResponseCompletedNotification.json')

def file_pin(path):
    raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def load_fixtures(root):
    """Required repo-only data. No host/config/history discovery or fallback."""
    manifest=json.loads((root/'PROVENANCE.json').read_bytes())
    if manifest.get('schema')!='implementaudit.native-code-mode-test-fixtures.v1':
        raise ValueError('Unknown required fixture manifest schema')
    rows=manifest.get('files',[])
    if len(rows)!=4 or {row.get('path') for row in rows}!=set(SCHEMA_FILES)|{'synthetic.json'}:
        raise ValueError('Required fixture population differs')
    for row in rows:
        actual=file_pin(root/row['path'])
        if any(actual[key]!=row.get(key) for key in ('bytes','sha256')):
            raise ValueError('Required fixture digest differs: '+row['path'])
        value=json.loads((root/row['path']).read_bytes())
        def local_refs(node):
            if isinstance(node,dict):
                if '$ref' in node and not node['$ref'].startswith('#/'):
                    raise ValueError('Fixture schema contains a nonlocal reference')
                for child in node.values():local_refs(child)
            elif isinstance(node,list):
                for child in node:local_refs(child)
        local_refs(value)
    return json.loads((root/'synthetic.json').read_bytes())

def policy_inputs():
    module=load(SOURCE/'skills/implementaudit/scripts/native-capture-adapter/notification_policy.py','portable_policy')
    path=FIXTURES/'ServerNotification.json';schema=json.loads(path.read_bytes())
    methods=[row['properties']['method']['enum'][0] for row in schema['oneOf']]
    selected=set(DATA['admitted_public_methods'])
    if not selected<=set(methods):raise ValueError('Synthetic policy selects an unknown public method')
    matrix={'schema_pin':file_pin(path),'rows':[{'method':name,'disposition':'CANARY' if name in selected else 'ABORT'} for name in methods]}
    plan={'schemas':{name.removesuffix('.json'):file_pin(FIXTURES/name) for name in SCHEMA_FILES[1:]},
          'visibility':{'load_spec':CodeModeContractTests().load_spec()}}
    return module,plan,matrix,path

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def portable_context_contract(spec):
    """Independent disabled toy producer, never a statement about native context.

    Its source rule and both resolved states are authored in synthetic.json.
    Receipts and the complete omission proof precede every observed test frame.
    Missing data cannot select an empty default or a production input.
    """
    scenario=DATA['context_fixture']
    if (set(scenario)!={'scope','source_rule','producer','load_state','use_state','wire'} or
            scenario['scope']!='OFFLINE_SYNTHETIC' or scenario['source_rule']!='Emit only when enabled is true' or
            scenario['load_state']!={'enabled':False} or scenario['use_state']!={'enabled':False}):
        raise ValueError('Required independent synthetic context scenario differs')
    basis=hashlib.sha256(json.dumps({'selection':spec,'settings':DATA['settings'],'context_fixture':scenario},
        sort_keys=True,separators=(',',':')).encode()).hexdigest()
    root=WORK/('context-'+basis);root.mkdir(exist_ok=True)
    def put(name,value):
        path=root/name;raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
        if path.exists():
            if path.read_bytes()!=raw:raise ValueError('Independent synthetic input changed')
        else:path.write_bytes(raw)
        return file_pin(path)
    source=file_pin(FIXTURES/'synthetic.json')
    inputs=[put('resolved-state.json',{'LOAD':scenario['load_state'],'USE':scenario['use_state']})]
    declaration=copy.deepcopy(scenario['producer']);declaration['source_pin']=source
    receipts={}
    for phase in ('LOAD','USE'):
        receipts[phase]=put('producer-'+phase+'.json',{'schema':'native-context-producer-v1',
            'origin':'INDEPENDENT_SOURCE_INPUT','producer_id':declaration['id'],'phase':phase,'source_pin':source,
            'basis_sha256':basis,'input_pins':inputs,
            'previous_state_sha256':None if phase=='LOAD' else hashlib.sha256(json.dumps(scenario['load_state'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'state':scenario['load_state'] if phase=='LOAD' else scenario['use_state'],
            'branch':'ABSENT' if phase=='LOAD' else 'UNCHANGED','fragment':None})
    declaration['receipts']=receipts
    population=put('population.json',{'schema':'native-context-population-v1','origin':'INDEPENDENT_SOURCE_INPUT',
        'source_commit':'b5bffd3ec4db487e7e3dec59663875b0ef7b72ca','basis_sha256':basis,'source_pins':[source],
        'input_pins':inputs,'producer_ids':[declaration['id']],'unresolved':[]})
    phases={}
    for phase in ('LOAD','USE'):
        phases[phase]={'wire':copy.deepcopy(scenario['wire']),'empty_prefix_proof':put('empty-'+phase+'.json',
            {'schema':'native-context-empty-v1','origin':'INDEPENDENT_SOURCE_INPUT','phase':phase,
             'basis_sha256':basis,'producer_receipts':[receipts[phase]]})}
    document={'schema':'native-context-input-v1','origin':'INDEPENDENT_SOURCE_INPUT','scope':'OFFLINE_SYNTHETIC',
        'status':'COMPLETE','unresolved':[],'source_commit':'b5bffd3ec4db487e7e3dec59663875b0ef7b72ca',
        'basis_sha256':basis,'source_pins':[source],'input_pins':inputs,'population_proof':population,
        'producers':[declaration],'phases':phases}
    import jsonschema
    jsonschema.Draft7Validator(json.loads((SOURCE/'skills/implementaudit/templates/native-context-input.schema.json').read_bytes())).validate(document)
    binding={'context_input':put('context-input.json',document)}
    return PROFILE.context_contract_from_input(binding,basis,purpose='OFFLINE_FIXTURE')

class CodeModeContractTests(unittest.TestCase):
    def binding(self):
        return {'cwd': r'C:\bounded\cwd', 'powershell': {'path': r'C:\runtime\pwsh.exe'},
                'load_command': "& 'C:\\runtime\\python.exe' -I -S -B 'C:\\bounded\\load.py'"}

    def load_spec(self):
        binding = self.binding()
        load = PROFILE.code_mode_spec(binding, binding['load_command'], 'complete LOAD\n', 'LOAD_READY_ONLY ' + 'a'*64)
        use = PROFILE.code_mode_spec(binding, "& 'C:\\bounded\\use.py'", 'complete USE\n', 'USE_NONVERDICT')
        spec = {'command': binding['load_command'], 'cwd': binding['cwd'], 'expected_argv': load['expected_argv'],
                'expected_output': load['expected_output'], 'ready_text': load['terminal_text'],
                'code_mode': {'LOAD': load, 'USE': use}}
        spec['context_contract']=portable_context_contract(spec)
        return spec

    def staged(self):
        binding=self.binding();spec=self.load_spec();load=spec['code_mode']['LOAD']
        staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, spec)
        staged.bind_thread('synthetic-worker')
        settings = copy.deepcopy(DATA['settings'])
        settings['cwd']=binding['cwd']
        staged.active.expected_settings = settings
        request = {'id':5,'method':'turn/start','params':{'threadId':staged.thread_id,'cwd':binding['cwd'],
            'approvalPolicy':'never','permissions':'worker_load','environments':PROFILE.local_environment(binding['cwd']),
            'model':'gpt-6-astra','effort':'low','input':[{'type':'text','text':'synthetic input','text_elements':[]}]}}
        staged.register_turn(request)
        staged.response({'id':5,'result':{'turn':{'id':'synthetic-turn','status':'inProgress','items':[]}}})
        staged.observe({'method':'thread/settings/updated','params':{'threadId':staged.thread_id,'threadSettings':settings}})
        staged.observe({'method':'turn/started','params':{'threadId':staged.thread_id,'turn':{
            'id':'synthetic-turn','status':'inProgress','items':[]}}})
        return staged, request, load

    def events(self, staged, spec):
        params = {'threadId':staged.thread_id,'turnId':staged.turn_id}
        def raw(item): return {'method':'rawResponseItem/completed','params':dict(params,item=item)}
        def item(method, value):
            stamp='startedAtMs' if method=='item/started' else 'completedAtMs'
            return {'method':method,'params':dict(params,item=value,**{stamp:1000})}
        result = {'chunk_id':'synthetic','wall_time_seconds':0.1,'exit_code':0,'output':spec['expected_output']}
        body = [{'type':'input_text','text':'Script completed\nWall time 0.1 seconds\nOutput:\n'},
                {'type':'input_text','text':json.dumps(result,separators=(',',':'))}]
        command={'id':'exec-synthetic-command','type':'commandExecution','command':shlex.join(spec['expected_argv']),
                 'cwd':spec['cwd'],'status':'completed','exitCode':0,'aggregatedOutput':spec['expected_output'],
                 'commandActions':[],'processId':None,'durationMs':100}
        started=copy.deepcopy(command);started.update(status='inProgress',exitCode=None,aggregatedOutput=None,durationMs=None)
        ready={'id':'synthetic-ready','type':'agentMessage','phase':'final_answer','text':spec['terminal_text']}
        return [raw({'type':'message','id':'synthetic-user','role':'user','content':[{'type':'input_text','text':'synthetic input'}],
                     'internal_chat_message_metadata_passthrough':{'content_item_kinds':['user.text']}}),
            raw({'type':'custom_tool_call','id':'synthetic-call-item','call_id':'synthetic-call','name':'exec','input':spec['wrapper_source']}),
            item('item/started',started),item('item/completed',command),
            raw({'type':'custom_tool_call_output','call_id':'synthetic-call','output':body}),
            {'method':'rawResponse/completed','params':dict(params,responseId='synthetic-response-1',usage=None,usageMetadata=None)},
            item('item/started',dict(ready,text='')),item('item/completed',ready),
            raw({'type':'message','id':'synthetic-ready','role':'assistant','phase':'final_answer',
                 'content':[{'type':'output_text','text':spec['terminal_text']}]}),
            {'method':'rawResponse/completed','params':dict(params,responseId='synthetic-response-2',usage=None,usageMetadata=None)}]

    def with_user_lifecycle(self, events):
        """Source-shaped raw then typed request; typed ID is deliberately distinct."""
        expanded=[]
        for event in events:
            expanded.append(event)
            raw=event.get('params',{}).get('item',{})
            if event['method']=='rawResponseItem/completed' and raw.get('type')=='message' and raw.get('role')=='user':
                typed={'type':'userMessage','id':'synthetic-typed-user','clientId':None,
                       'content':[{'type':'text','text':'synthetic input','text_elements':[]}]}
                for method,stamp in [('item/started','startedAtMs'),('item/completed','completedAtMs')]:
                    expanded.append({'method':method,'params':dict(event['params'],item=copy.deepcopy(typed),**{stamp:1000})})
        return expanded

    def complete(self, edit=None, edit_expanded=None):
        staged, request, spec = self.staged();events=self.events(staged,spec)
        if edit: edit(events)
        events=self.with_user_lifecycle(events)
        if edit_expanded:edit_expanded(events)
        for event in events: staged.observe(event)
        staged.observe({'method':'turn/completed','params':{'threadId':staged.thread_id,'turn':{
            'id':staged.turn_id,'status':'completed','error':None,'itemsView':'full',
            'items':[copy.deepcopy(row['completed']) for row in staged.items.values()]}}})
        return staged, staged.qualify_load()

    def test_exact_source_and_complete_inner_and_wrapper_output(self):
        staged, proof=self.complete()
        self.assertTrue(staged.transport_complete())
        self.assertEqual(proof['code_mode']['mapping'],'SOURCE_DERIVED_LITERAL_SINGLE_CALL')
        self.assertFalse(proof['code_mode']['native_parent_link_claimed'])
        self.assertEqual(proof['code_mode']['model_visible_output'][1]['type'],'input_text')

    def test_explicit_local_selection_preserves_empty_workspace_roots(self):
        self.assertEqual(PROFILE.local_environment(self.binding()['cwd']),
            [{'environmentId':'local','cwd':self.binding()['cwd'],'runtimeWorkspaceRoots':[]}])

    def test_literal_wrapper_has_one_fixed_call_and_both_budgets(self):
        _,_,spec=self.staged()
        self.assertEqual(spec['wrapper_source'].count('tools.exec_command('),1)
        self.assertIn('"max_output_tokens":40000',spec['wrapper_source'])
        self.assertEqual(spec['arguments']['max_output_tokens'],35000)

    def test_absent_empty_default_remote_extra_and_wrong_cwd_environment_refuse(self):
        for selected in (None,[],[{'environmentId':'remote','cwd':self.binding()['cwd'],'runtimeWorkspaceRoots':[]}],
                         PROFILE.local_environment(self.binding()['cwd'])*2,
                         PROFILE.local_environment(r'C:\foreign'),[{'environmentId':'local','cwd':self.binding()['cwd']} ]):
            with self.subTest(selected=selected),self.assertRaises(ValueError):
                staged,request,_=self.staged();new=PROTOCOL.CanaryProtocol();new.bind_thread(staged.thread_id)
                new.expected_settings=copy.deepcopy(staged.expected_settings);new.bind_code_mode(staged.active.code_mode)
                request['params']['environments']=selected;new.register_turn(request)

    def test_extra_wrapper_call_or_arbitrary_function_refuses(self):
        for kind in ('custom_tool_call','function_call'):
            def edit(events,kind=kind):
                extra=copy.deepcopy(events[1]);extra['params']['item'].update(type=kind,call_id='extra-call',id='extra-item')
                events.insert(2,extra)
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.complete(edit)

    def test_wrong_source_command_cwd_and_output_refuse(self):
        edits=[lambda e:e[1]['params']['item'].__setitem__('input','text("forged");'),
               lambda e:e[2]['params']['item'].__setitem__('command','wrong'),
               lambda e:e[2]['params']['item'].__setitem__('cwd',r'C:\foreign'),
               lambda e:e[3]['params']['item'].__setitem__('aggregatedOutput','wrong'),
               lambda e:e[3]['params']['item'].__setitem__('exitCode',1),
               lambda e:e[4]['params']['item']['output'][1].__setitem__('text','{"exit_code":0,"output":"wrong"}')]
        for n,edit in enumerate(edits):
            with self.subTest(case=n),self.assertRaises(ValueError):self.complete(edit)

    def test_foreign_duplicate_unpaired_and_incomplete_prefix_refuse(self):
        edits=[lambda e:e[4]['params']['item'].__setitem__('call_id','foreign'),
               lambda e:e[1]['params'].__setitem__('turnId','foreign'),
               lambda e:e[4]['params'].__setitem__('threadId','foreign'),
               lambda e:e.insert(5,copy.deepcopy(e[4])),lambda e:e.pop(4),lambda e:e.pop(1),
               lambda e:e.pop(0),lambda e:e.pop(9),lambda e:e.pop(8)]
        for n,edit in enumerate(edits):
            with self.subTest(case=n),self.assertRaises(ValueError):self.complete(edit)

    def test_yield_truncation_hidden_extra_content_and_session_refuse(self):
        edits=[lambda e:e[4]['params']['item']['output'][0].__setitem__('text','Script running with cell ID x'),
               lambda e:e[4]['params']['item']['output'].append({'type':'input_text','text':'extra'}),
               lambda e:e[4]['params']['item']['output'][1].__setitem__('text','Warning: truncated output'),
               lambda e:e[4]['params']['item']['output'][1].__setitem__('text',json.dumps({'exit_code':0,'session_id':1,'output':'complete LOAD\n'})),
               lambda e:e[4]['params']['item']['output'][1].__setitem__('text','{"exit_code":0,"output":"wrong","output":"complete LOAD\\n"}')]
        for n,edit in enumerate(edits):
            with self.subTest(case=n),self.assertRaises(ValueError):self.complete(edit)

    def test_readiness_cannot_precede_wrapper_delivery_or_change_phase(self):
        edits=[lambda e:e.insert(4,e.pop(6)),lambda e:e[6]['params']['item'].__setitem__('phase','commentary'),
               lambda e:e[7]['params']['item'].__setitem__('text','wrong'),
               lambda e:e[8]['params']['item']['content'][0].__setitem__('text','wrong')]
        for n,edit in enumerate(edits):
            with self.subTest(case=n),self.assertRaises(ValueError):self.complete(edit)

    def test_no_raw_private_reasoning_in_projection_and_unknown_routes_refuse(self):
        def insert(events):events.insert(1,{'method':'rawResponseItem/completed','params':dict(events[0]['params'],
            item={'type':'reasoning','id':'synthetic-reasoning','summary':[],'content':[{'type':'reasoning_text','text':'PRIVATE_TEST_SENTINEL'}]})})
        staged,_=self.complete(insert)
        self.assertNotIn('PRIVATE_TEST_SENTINEL',json.dumps(staged.snapshot()))
        for kind in ('agent_message','context_compaction','additional_tools','function_call_output'):
            def change(events,kind=kind):events[1]['params']['item']['type']=kind
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.complete(change)

    def test_failure_latches_and_unreleased_use_stays_forbidden(self):
        staged,request,spec=self.staged()
        with self.assertRaises(ValueError):staged.register_turn(dict(request,id=6))
        events=self.events(staged,spec);events[1]['params']['item']['input']='wrong'
        with self.assertRaises(ValueError):
            for event in self.with_user_lifecycle(events):staged.observe(event)
        self.assertIsNotNone(staged.first_anomaly)
        with self.assertRaises(ValueError):staged.observe(self.events(staged,spec)[1])
        with self.assertRaises(ValueError):staged.qualify_load()

    def test_same_worker_use_remains_gated_and_uses_its_own_command(self):
        staged,_=self.complete();settings=copy.deepcopy(staged.expected_settings)
        settings['activePermissionProfile']={'id':'worker_use','extends':None}
        staged.release('synthetic-ready-digest',settings)
        self.assertEqual(staged.thread_id,'synthetic-worker')
        self.assertEqual(staged.active.code_mode['expected_output'],'complete USE\n')
        with self.assertRaises(ValueError):staged.release('again',settings)

    def test_complete_use_requires_fresh_turn_and_pairings_on_same_worker(self):
        staged,_=self.complete();settings=copy.deepcopy(staged.expected_settings)
        settings['activePermissionProfile']={'id':'worker_use','extends':None}
        staged.release('synthetic-ready-digest',settings)
        request={'id':6,'method':'turn/start','params':{'threadId':staged.thread_id,'cwd':settings['cwd'],
            'approvalPolicy':'never','permissions':'worker_use','environments':PROFILE.local_environment(settings['cwd']),
            'model':'gpt-6-astra','effort':'low','input':[{'type':'text','text':'synthetic input','text_elements':[]}]}}
        staged.register_turn(request)
        staged.response({'id':6,'result':{'turn':{'id':'synthetic-use-turn','status':'inProgress','items':[]}}})
        staged.observe({'method':'thread/settings/updated','params':{'threadId':staged.thread_id,'threadSettings':settings}})
        staged.observe({'method':'turn/started','params':{'threadId':staged.thread_id,'turn':{'id':staged.turn_id,'status':'inProgress','items':[]}}})
        events=self.events(staged,staged.active.code_mode)
        for event in self.with_user_lifecycle(events):
            item=event['params'].get('item',{})
            if 'call_id' in item:item['call_id']='synthetic-use-call'
            if 'responseId' in event['params']:event['params']['responseId']+='-use'
            staged.observe(event)
        staged.observe({'method':'turn/completed','params':{'threadId':staged.thread_id,'turn':{
            'id':staged.turn_id,'status':'completed','error':None,'itemsView':'full',
            'items':[copy.deepcopy(row['completed']) for row in staged.items.values()]}}})
        self.assertTrue(staged.transport_complete())

    def test_source_spec_cannot_authorize_extra_code_or_unbounded_arguments(self):
        _,_,spec=self.staged()
        edits=[lambda s:s.__setitem__('wrapper_source',s['wrapper_source']+'\ntext(await tools.other());'),
               lambda s:s['arguments'].__setitem__('login',True),lambda s:s['arguments'].__setitem__('max_output_tokens',True),
               lambda s:s['arguments'].__setitem__('extra','value')]
        for edit in edits:
            changed=copy.deepcopy(spec);edit(changed)
            with self.assertRaises(ValueError):PROTOCOL.CanaryProtocol().bind_code_mode(changed)

    def test_current_raw_schema_policy_and_private_projection(self):
        policy_module,plan,matrix,path=policy_inputs()
        staged,_,spec=self.staged()
        policy=policy_module.NotificationPolicy(plan,matrix,path,{})
        for event in self.with_user_lifecycle(self.events(staged,spec)):
            if event['method'].startswith('rawResponse'):
                self.assertEqual(policy.route(event,staged),'CANARY')
            staged.observe(event)
        self.assertTrue(all(row.get('private_body_omitted') for row in policy.frames))
        bad=copy.deepcopy(self.events(staged,spec)[1]);bad['params']['item']['unreviewed']=True
        with self.assertRaises(ValueError):policy.route(bad,staged)
        del plan['schemas']['RawResponseItemCompletedNotification']
        with self.assertRaises(ValueError):policy_module.NotificationPolicy(plan,matrix,Path(matrix['schema_pin']['path']),{})

    def test_pure_profile_factories_keep_exact_command_and_budgets(self):
        # Full host-bound prepare/readback controls remain a separate input-owner
        # qualification. Portable guard tests never fabricate native file pins.
        binding=self.binding();binding.update(python={'path':r'C:\runtime\python.exe'},loader={'path':r'C:\bounded\load.py'})
        ready='LOAD_READY_ONLY '+'a'*64
        spec=PROFILE.code_mode_spec(binding,binding['load_command'],'synthetic\n',ready)
        prompt=PROFILE.silent_load_input(binding,ready)
        self.assertIn(spec['wrapper_source'],prompt[0]['text'])
        self.assertTrue(prompt[0]['text'].endswith('\n'+ready))
        self.assertEqual(spec['arguments']['max_output_tokens'],35000)
        self.assertFalse(spec['arguments']['login'])
        binding['load_command']+=' extra'
        with self.assertRaises(ValueError):PROFILE.silent_load_input(binding,ready)

    def test_optional_typed_wrapper_must_match_raw_body_exactly(self):
        def add(events,wrong=False):
            body=copy.deepcopy(events[4]['params']['item']['output'])
            if wrong:body[0]['text']='Script completed\nWall time 0.2 seconds\nOutput:\n'
            item={'type':'functionCallOutput','id':'synthetic-call','name':'exec','namespace':None,'output':body}
            for method in ('item/completed','item/started'):
                events.insert(5,{'method':method,'params':dict(events[4]['params'],item=copy.deepcopy(item))})
        self.complete(add)
        with self.assertRaises(ValueError):self.complete(lambda events:add(events,True))

    def test_source_defined_synthetic_wrapper_output_format_is_supported(self):
        actual=copy.deepcopy(DATA['wrapper_result'])
        body=[{'type':'input_text','text':'Script completed\nWall time 0.1 seconds\nOutput:\n'},
              {'type':'input_text','text':json.dumps(actual,separators=(',',':'))}]
        spec=PROFILE.code_mode_spec(self.binding(),self.binding()['load_command'],actual['output'],'SHAPE_ONLY')
        protocol=PROTOCOL.CanaryProtocol();protocol.bind_code_mode(spec)
        self.assertEqual(protocol.wrapper_result(body),actual)

    def test_large_complete_output_and_overbound_output(self):
        binding=self.binding()
        spec=PROFILE.code_mode_spec(binding,binding['load_command'],'x'*60000,'READY')
        protocol=PROTOCOL.CanaryProtocol();protocol.bind_code_mode(spec)
        body=[{'type':'input_text','text':'Script completed\nWall time 0.1 seconds\nOutput:\n'},
              {'type':'input_text','text':json.dumps({'chunk_id':'boundary','wall_time_seconds':0.1,'exit_code':0,'output':spec['expected_output']})}]
        self.assertEqual(protocol.wrapper_result(body)['output'],spec['expected_output'])
        with self.assertRaises(ValueError):PROFILE.code_mode_spec(binding,binding['load_command'],'x'*65537,'READY')

    def test_runtime_requires_the_exact_current_profile_digest(self):
        runtime=load(SOURCE/'skills/implementaudit/scripts/native-capture-adapter/worker_runtime.py','runtime_digest_control')
        self.assertEqual(runtime.worker_profile().local_environment(self.binding()['cwd']),PROFILE.local_environment(self.binding()['cwd']))
        runtime.WORKER_PROFILE_SHA256='0'*64
        with self.assertRaises(ValueError):runtime.worker_profile()

    def test_first_completion_accepts_both_sides_of_inner_future(self):
        for position in (2,3,4,5):
            def move(events,position=position):events.insert(position,events.pop(5))
            with self.subTest(position=position):self.complete(move)

    def test_response_completion_must_follow_its_phase_body(self):
        edits=[lambda e:e.insert(0,e.pop(5)),lambda e:e.insert(8,e.pop(9)),
               lambda e:e.append(e.pop(5))]
        for edit in edits:
            with self.assertRaises(ValueError):self.complete(edit)

    def test_typed_request_content_missing_extra_and_late_refuse(self):
        def typed(events):return [e for e in events if e.get('params',{}).get('item',{}).get('type')=='userMessage']
        def mismatch(events):typed(events)[1]['params']['item']['content'][0]['text']='foreign'
        def missing(events):events[:]=[e for e in events if e not in typed(events)]
        def unfinished(events):events.remove(typed(events)[1])
        def extra(events):
            row=copy.deepcopy(typed(events)[0]);row['params']['item']['id']='extra';events.insert(3,row)
        def late(events):
            rows=typed(events);events[:]=[e for e in events if e not in rows];events.extend(rows)
        def before_raw(events):events.insert(0,events.pop(1))
        def client(events):typed(events)[0]['params']['item']['clientId']='unselected-client'
        for edit in (mismatch,missing,unfinished,extra,late,before_raw,client):
            with self.subTest(edit=edit.__name__),self.assertRaises(ValueError):self.complete(edit_expanded=edit)

    def test_raw_and_typed_request_ids_need_not_be_equal(self):
        staged,proof=self.complete()
        self.assertEqual(proof['code_mode']['typed_user_item_id'],'synthetic-typed-user')
        self.assertEqual(proof['code_mode']['raw_user_item_id'],'synthetic-user')
        self.assertNotEqual(proof['code_mode']['typed_user_item_id'],proof['code_mode']['raw_user_item_id'])

    def test_early_completion_failure_latches(self):
        staged,_,spec=self.staged();early=self.events(staged,spec)[5]
        with self.assertRaises(ValueError):staged.observe(early)
        self.assertIsNotNone(staged.first_anomaly)
        with self.assertRaises(ValueError):staged.observe(self.events(staged,spec)[0])

    def user_metadata_policy(self):
        module,plan,matrix,path=policy_inputs()
        return module.NotificationPolicy(plan,matrix,path,{})

    def assert_metadata_refused_by_both(self, edit):
        for guard in ('policy','observer'):
            staged,_,spec=self.staged();events=self.events(staged,spec);event=edit(events)
            with self.subTest(guard=guard),self.assertRaises(ValueError):
                if guard=='policy':self.user_metadata_policy().route(event,staged)
                else:staged.observe(event)

    def test_source_user_classification_passes_and_is_omitted_from_projection(self):
        staged,_,spec=self.staged();event=self.events(staged,spec)[0]
        self.assertEqual(self.user_metadata_policy().route(event,staged),'CANARY')
        staged.observe(event)
        completed,proof=self.complete()
        self.assertNotIn('content_item_kinds',json.dumps([completed.snapshot(),proof]))

    def test_user_classification_wrong_type_value_or_count_refuses_both_guards(self):
        for value in (None,False,'user.text',[],['user.image'],['user.text','user.text'],[None],[0],{'kind':'user.text'}):
            def edit(events,value=value):
                events[0]['params']['item']['internal_chat_message_metadata_passthrough']['content_item_kinds']=value
                return events[0]
            with self.subTest(value=value):self.assert_metadata_refused_by_both(edit)

    def test_source_user_classification_presence_is_required(self):
        def absent(events):events[0]['params']['item'].pop('internal_chat_message_metadata_passthrough');return events[0]
        def empty(events):events[0]['params']['item']['internal_chat_message_metadata_passthrough']={};return events[0]
        for edit in (absent,empty):self.assert_metadata_refused_by_both(edit)

    def test_classification_on_unrelated_items_or_metadata_refuses(self):
        for index in (1,4,8):
            def unrelated(events,index=index):
                events[index]['params']['item']['internal_chat_message_metadata_passthrough']={'content_item_kinds':['user.text']}
                return events[index]
            self.assert_metadata_refused_by_both(unrelated)
        for key in ('cell_id','executed_tool_calls','tool_calls_complete','unrelated'):
            def extra(events,key=key):
                events[0]['params']['item']['internal_chat_message_metadata_passthrough'][key]='unreviewed'
                return events[0]
            self.assert_metadata_refused_by_both(extra)
        def developer(events):events[0]['params']['item']['role']='developer';return events[0]
        self.assert_metadata_refused_by_both(developer)

    def test_classification_does_not_replace_selected_text_binding(self):
        def wrong(events):events[0]['params']['item']['content'][0]['text']='unselected';return events[0]
        self.assert_metadata_refused_by_both(wrong)

    def test_complete_event_sequence_conforms_to_pinned_schema_policy(self):
        staged,_,spec=self.staged();policy=self.user_metadata_policy()
        initial=[{'method':'thread/settings/updated','params':{'threadId':staged.thread_id,'threadSettings':staged.expected_settings}},
                 {'method':'turn/started','params':{'threadId':staged.thread_id,'turn':{'id':staged.turn_id,'status':'inProgress','items':[]}}}]
        for event in initial:self.assertEqual(policy.route(event,staged),'CANARY')
        for event in self.with_user_lifecycle(self.events(staged,spec)):
            self.assertEqual(policy.route(event,staged),'CANARY');staged.observe(event)
        terminal={'method':'turn/completed','params':{'threadId':staged.thread_id,'turn':{
            'id':staged.turn_id,'status':'completed','error':None,'itemsView':'full',
            'items':[copy.deepcopy(row['completed']) for row in staged.items.values()]}}}
        self.assertEqual(policy.route(terminal,staged),'CANARY');staged.observe(terminal)
        self.assertTrue(staged.qualify_load());self.assertTrue(policy.complete())

    def test_missing_or_duplicate_notification_registration_refuses(self):
        module,plan,matrix,path=policy_inputs()
        for rows in (matrix['rows'][:-1],matrix['rows']+[matrix['rows'][0]]):
            changed=copy.deepcopy(matrix);changed['rows']=rows
            with self.assertRaises(ValueError):module.NotificationPolicy(plan,changed,path,{})

    def test_unknown_and_unreviewed_notifications_fail_closed(self):
        staged,_,_=self.staged()
        with self.assertRaisesRegex(ValueError,'Unlisted notification method'):
            self.user_metadata_policy().route({'method':'unreviewed/method','params':{}},staged)
        with self.assertRaisesRegex(ValueError,'Explicit notification abort'):
            self.user_metadata_policy().route({'method':'warning','params':{'threadId':staged.thread_id,'message':'synthetic warning'}},staged)

    def test_independent_empty_context_is_explicit_and_cannot_qualify_native(self):
        contract=self.load_spec()['context_contract']
        for phase in ('LOAD','USE'):
            self.assertEqual(contract['phases'][phase]['rows'],[])
            self.assertIsNotNone(contract['phases'][phase]['empty_prefix_proof'])
        with self.assertRaisesRegex(ValueError,'Synthetic context cannot qualify native input'):
            PROFILE.context_contract_from_input({'context_input':contract['source_input']},contract['basis_sha256'],purpose='NATIVE_CAPTURE')

    def test_missing_or_changed_synthetic_context_has_no_empty_fallback(self):
        saved=DATA['context_fixture']
        try:
            del DATA['context_fixture']
            with self.assertRaises(KeyError):self.load_spec()
            DATA['context_fixture']=copy.deepcopy(saved);DATA['context_fixture']['use_state']={'enabled':True}
            with self.assertRaisesRegex(ValueError,'Required independent synthetic context scenario differs'):self.load_spec()
        finally:DATA['context_fixture']=saved

def main():
    global PROFILE,PROTOCOL,VISIBILITY,SOURCE,FIXTURES,DATA,WORK
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--log',type=Path);parser.add_argument('--work',type=Path);args=parser.parse_args()
    SOURCE=args.source.resolve();FIXTURES=SOURCE/'fixtures/codex-recovery/native-code-mode'
    try:
        import jsonschema
    except ImportError:
        parser.exit(2,"native-code-mode: required existing dependency 'jsonschema' is unavailable\n")
    try:DATA=load_fixtures(FIXTURES)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,'native-code-mode: required portable fixture failed: '+str(error)+'\n')
    p=SOURCE/'skills/implementaudit/scripts/native-capture-adapter'
    PROFILE=load(p/'worker_profile.py','code_profile');PROTOCOL=load(p/'canary_protocol.py','code_protocol')
    VISIBILITY=load(p/'load_visibility.py','code_visibility')
    def forbid(event,args):
        if event in ('subprocess.Popen','os.system','os.spawn','ctypes.dlopen','os.putenv','os.unsetenv') or event.startswith('socket.'):
            raise AssertionError('Pure controls forbid native/process/network/environment effects')
    sys.addaudithook(forbid)
    temporary=tempfile.TemporaryDirectory(prefix='native-code-mode-context-') if args.work is None else None
    WORK=(args.work or Path(temporary.name)).resolve();WORK.mkdir(parents=True,exist_ok=True)
    try:
        log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CodeModeContractTests))
    finally:
        if temporary:temporary.cleanup()
    if args.log:args.log.write_text(log.getvalue(),encoding='utf-8')
    if not result.wasSuccessful():sys.stderr.write(log.getvalue())
    print(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'portable_fixture_mode':True,'synthetic_only':True,'native_executed':False}))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
