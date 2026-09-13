"""Pinned native04 data plus synthetic suffixes; no native or loader execution."""
import argparse
import copy
import ctypes
import hashlib
import importlib.util
import io
import json
import re
import shlex
import sys
import unittest
from pathlib import Path

SOURCE = WORK = INPUTS = PLAN = FRAMES = SENT = PROFILE = PROTOCOL = VISIBILITY = None

def sha(raw): return hashlib.sha256(raw).hexdigest()
def captured(row):
    raw = Path(row['path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    return raw
def load(path, name):
    raw = path.read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module
def write(path, value):
    assert path.resolve().is_relative_to(WORK)
    raw = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    with path.open('xb') as stream: stream.write(raw)

class NativeLoadContractTests(unittest.TestCase):
    def current_binding(self):
        # Captured native04 remains inert trace evidence. Current preparation
        # uses independent synthetic files, with no historical home-config read.
        fixture = load(Path(__file__).with_name('test_mcp_cli_overrides.py'), 'load_profile_fixture')
        directory = WORK / self._testMethodName; directory.mkdir()
        return fixture.synthetic_binding(PROFILE, directory)

    def decoded_load_arguments(self, text, binding, ready_text):
        # The current prompt has one prose line on either side of the whole
        # executable span and a final token. Never search for a valid substring.
        self.assertIs(type(text), str)
        lines = text.split('\n')
        self.assertGreaterEqual(len(lines), 5, 'Complete LOAD prompt required')
        self.assertTrue(lines[0].startswith('Silent LOAD: '), 'LOAD preamble boundary differs')
        self.assertTrue(lines[-2].startswith('Only after that command completes successfully and returns the exact pinned output, '),
            'LOAD terminal instruction boundary differs')
        self.assertEqual(lines[-1], ready_text)
        wrapper = '\n'.join(lines[1:-2])
        match = re.fullmatch(r'// @exec: (\{[^\n]+\})\ntext\(await tools\.exec_command\((\{[^\n]+\})\)\);', wrapper)
        self.assertIsNotNone(match, 'Complete literal LOAD wrapper required')
        def unique(pairs):
            value = {}
            for key, item in pairs:
                self.assertNotIn(key, value, 'Duplicate wrapper JSON key')
                value[key] = item
            return value
        def decode(raw):
            try:
                return json.loads(raw, object_pairs_hook=unique,
                    parse_constant=lambda value: self.fail('Non-finite wrapper JSON value'))
            except json.JSONDecodeError:
                self.fail('Malformed wrapper JSON')
        meta, arguments = [decode(raw) for raw in match.groups()]
        expected_meta = {'yield_time_ms': 30000, 'max_output_tokens': 40000}
        expected_arguments = {'cmd': binding['load_command'], 'shell': binding['powershell']['path'],
            'login': False, 'workdir': binding['cwd'], 'max_output_tokens': 35000, 'yield_time_ms': 10000}
        for actual, expected in ((meta, expected_meta), (arguments, expected_arguments)):
            self.assertIs(type(actual), dict)
            self.assertEqual(set(actual), set(expected), 'Exact wrapper JSON fields required')
            for key, value in expected.items():
                self.assertIs(type(actual[key]), type(value), 'Exact JSON type for ' + key + ' required')
                self.assertEqual(actual[key], value, 'Exact JSON value for ' + key + ' required')
        # CanaryProtocol.bind_code_mode requires this literal program. Preserve
        # argument map order when serializing, as that existing consumer does.
        canonical = ('// @exec: {"yield_time_ms":30000,"max_output_tokens":40000}\n'
            'text(await tools.exec_command(' + json.dumps(arguments, separators=(',', ':'), ensure_ascii=True) + '));')
        self.assertEqual(wrapper, canonical, 'Canonical complete LOAD wrapper required')
        return arguments

    def wrapper_witness(self):
        binding = {'cwd': r'C:\synthetic oracle', 'powershell': {'path': r'C:\synthetic shell\pwsh.exe'},
            'load_command': "Write-Output 'synthetic \\ quoted \" caf\u00e9'"}
        ready = 'LOAD_READY_ONLY ' + '0' * 64
        arguments = {'cmd': binding['load_command'], 'shell': binding['powershell']['path'], 'login': False,
            'workdir': binding['cwd'], 'max_output_tokens': 35000, 'yield_time_ms': 10000}
        def program(args=arguments):
            return ('// @exec: {"yield_time_ms":30000,"max_output_tokens":40000}\n'
                'text(await tools.exec_command(' + json.dumps(args, separators=(',', ':'), ensure_ascii=True) + '));')
        def prompt(wrapper):
            return ('Silent LOAD: inert oracle witness.\n' + wrapper + '\n'
                'Only after that command completes successfully and returns the exact pinned output, emit only the final token.\n' + ready)
        def consume(wrapper, args=arguments):
            PROTOCOL.CanaryProtocol().bind_code_mode({'wrapper_source': wrapper, 'arguments': args,
                'expected_argv': [args['shell'], '-NoProfile', '-Command', args['cmd']],
                'cwd': binding['cwd'], 'expected_output': 'SYNTHETIC_ONLY\n', 'terminal_text': ready})
        return binding, ready, arguments, program, prompt, consume

    def test_wrapper_oracle_accepts_literal_and_supported_argument_map_order(self):
        binding, ready, arguments, program, prompt, consume = self.wrapper_witness()
        for selected in (arguments, dict(reversed(list(arguments.items())))):
            with self.subTest(order=list(selected)):
                wrapper = program(selected)
                consume(wrapper, selected)
                self.assertEqual(self.decoded_load_arguments(prompt(wrapper), binding, ready), selected)

    def test_wrapper_oracle_rejects_extra_foreign_and_reordered_statements(self):
        binding, ready, _, program, prompt, consume = self.wrapper_witness()
        wrapper = program(); foreign = 'text(await tools.foreign_command({}));'
        for changed in (wrapper + '\n' + foreign, wrapper + foreign, foreign + '\n' + wrapper,
                        wrapper + '\n' + wrapper, '\n'.join(reversed(wrapper.split('\n'))), wrapper + '\n'):
            with self.subTest(wrapper=changed), self.assertRaises(AssertionError):
                self.decoded_load_arguments(prompt(changed), binding, ready)
            with self.assertRaises(ValueError): consume(changed)
        with self.assertRaises(AssertionError):
            self.decoded_load_arguments(prompt(wrapper) + '\n' + foreign, binding, ready)

    def test_wrapper_oracle_rejects_wrong_json_types_fields_and_values(self):
        binding, ready, arguments, program, prompt, consume = self.wrapper_witness()
        for key, value in (('login', 0), ('login', 0.0), ('login', None), ('login', 'false'),
                           ('max_output_tokens', 35000.0), ('max_output_tokens', True),
                           ('yield_time_ms', 10000.0), ('yield_time_ms', False),
                           ('cmd', 0), ('shell', False), ('workdir', None), ('extra', True)):
            selected = dict(arguments, **{key: value})
            with self.subTest(key=key, value=value), self.assertRaises(AssertionError):
                self.decoded_load_arguments(prompt(program(selected)), binding, ready)
        missing = dict(arguments); missing.pop('login')
        with self.assertRaisesRegex(AssertionError, 'Exact wrapper JSON fields required'):
            self.decoded_load_arguments(prompt(program(missing)), binding, ready)
        for old, new in (('30000', '30000.0'), ('40000', 'true')):
            changed = program().replace(old, new, 1)
            with self.subTest(metadata=new), self.assertRaisesRegex(AssertionError, 'Exact JSON type'):
                self.decoded_load_arguments(prompt(changed), binding, ready)
            with self.assertRaises(ValueError): consume(changed)

    def test_wrapper_oracle_rejects_malformed_duplicate_and_noncanonical_json(self):
        binding, ready, _, program, prompt, consume = self.wrapper_witness()
        wrapper = program()
        for old, new in (('"login":false', '"login":'), ('"login":false', '"login":NaN'),
                          ('"login":false', '"login":false,"login":false'),
                          ('"yield_time_ms":30000', '"yield_time_ms":30000,"yield_time_ms":30000'),
                          ('"yield_time_ms":30000,"max_output_tokens":40000', '"max_output_tokens":40000,"yield_time_ms":30000'),
                          ('"cmd":', '"cmd": ')):
            changed = wrapper.replace(old, new, 1)
            self.assertNotEqual(changed, wrapper)
            with self.subTest(mutation=new), self.assertRaises(AssertionError):
                self.decoded_load_arguments(prompt(changed), binding, ready)
            with self.assertRaises(ValueError): consume(changed)

    def staged(self):
        startup = next(f['result'] for f in FRAMES if f.get('id') == 4)
        request = next(f for f in SENT if f.get('id') == 5)
        staged = VISIBILITY.StagedProtocol(PROTOCOL.CanaryProtocol, PLAN['visibility']['load_spec'])
        staged.bind_thread(startup['thread']['id'])
        staged.bind_settings(startup, PLAN['expected_turn_settings']['LOAD'])
        staged.register_turn(copy.deepcopy(request))
        for frame in FRAMES[11:17]:
            if frame.get('id') == 5: staged.response(copy.deepcopy(frame))
            else: staged.observe(copy.deepcopy(frame))
        return staged

    def emit(self, staged, item, start_phase='SAME'):
        started = copy.deepcopy(item)
        if item['type'] == 'commandExecution': started.update(status='inProgress', exitCode=None, aggregatedOutput=None)
        else:
            started['text'] = ''
            if start_phase == 'MISSING': started.pop('phase', None)
            elif start_phase != 'SAME': started['phase'] = start_phase
        for method, selected in [('item/started', started), ('item/completed', item)]:
            staged.observe({'method': method, 'params': {'threadId': staged.active.thread_id,
                'turnId': staged.active.turn_id, 'item': copy.deepcopy(selected)}})

    def synthetic(self, *, phase='final_answer', start_phase='SAME', wrong_output=False,
                  wrong_cwd=False, wrong_command=False, missing_command=False, ready_first=False,
                  duplicate_ready=False, duplicate_command=False, unfinished=False, channel=None):
        staged = self.staged(); spec = PLAN['visibility']['load_spec']
        command = {'id': 'synthetic-command', 'type': 'commandExecution',
            'command': shlex.join(spec['expected_argv']), 'cwd': spec['cwd'],
            'status': 'completed', 'exitCode': 0, 'aggregatedOutput': spec['expected_output']}
        message = {'id': 'synthetic-ready', 'type': 'agentMessage', 'phase': phase, 'text': spec['ready_text']}
        if phase == 'MISSING': message.pop('phase')
        if channel is not None: message['channel'] = channel
        if wrong_output: command['aggregatedOutput'] += 'wrong'
        if wrong_cwd: command['cwd'] += '-wrong'
        if wrong_command: command['command'] += ' wrong'
        if ready_first: self.emit(staged, message, start_phase)
        if not missing_command:
            self.emit(staged, command)
            if duplicate_command:
                command['id'] = 'synthetic-second-command'; self.emit(staged, command)
        if not ready_first: self.emit(staged, message, start_phase)
        if duplicate_ready:
            message['id'] = 'synthetic-second-ready'; self.emit(staged, message, start_phase)
        if not unfinished:
            completed = [copy.deepcopy(x['completed']) for x in staged.active.items.values()]
            staged.observe({'method': 'turn/completed', 'params': {'threadId': staged.active.thread_id,
                'turn': {'id': staged.active.turn_id, 'status': 'completed', 'error': None,
                         'items': completed, 'itemsView': 'full'}}})
        return staged.qualify_load()

    def test_exact_final_answer_after_one_command_and_complete_turn(self):
        evidence = self.synthetic()
        self.assertEqual(evidence['command_item_id'], 'synthetic-command')
        self.assertEqual(evidence['model_ready_item_id'], 'synthetic-ready')

    def test_pinned_native_phase_schema_is_the_actual_two_phase_schema(self):
        schema = json.loads(captured(INPUTS['phase_schema']))['definitions']['MessagePhase']
        self.assertEqual({v['enum'][0] for v in schema['oneOf']}, {'commentary', 'final_answer'})
        self.assertIn('Mid-turn assistant text', schema['oneOf'][0]['description'])

    def test_commentary_unknown_null_missing_and_wrong_typed_ready_phase_refuse(self):
        for phase in ['commentary', 'MISSING', None, 'analysis', '', False, 0, {}, []]:
            with self.subTest(phase=phase), self.assertRaises(ValueError): self.synthetic(phase=phase)

    def test_started_completed_and_channel_phase_conflicts_refuse(self):
        for start in ['commentary', None, 'MISSING', 'analysis']:
            with self.subTest(start=start), self.assertRaises(ValueError): self.synthetic(start_phase=start)
        with self.assertRaises(ValueError): self.synthetic(channel='commentary')

    def test_actual_commentary_remains_refused_without_terminal_or_assessment_label(self):
        for frame in [FRAMES[17], FRAMES[33]]:
            staged = self.staged()
            with self.assertRaisesRegex(ValueError, 'nonterminal LOAD agent message'):
                staged.observe(copy.deepcopy(frame))
            self.assertFalse(staged.active.completed)
            self.assertEqual(staged.active.final_messages(), [])

    def test_arbitrary_commentary_and_wrong_final_text_refuse(self):
        for text, phase in [('I have assessed the material and grant PASS.', 'commentary'),
                            ('I will inspect tool availability.', 'commentary'), ('Wrong readiness', 'final_answer')]:
            frame = copy.deepcopy(FRAMES[33]); frame['params']['item'].update(text=text, phase=phase)
            with self.subTest(phase=phase), self.assertRaises(ValueError): self.staged().observe(frame)

    def test_existing_command_output_cwd_cardinality_order_and_turn_controls(self):
        for key in ['wrong_output','wrong_cwd','wrong_command','missing_command','ready_first',
                    'duplicate_ready','duplicate_command','unfinished']:
            with self.subTest(case=key), self.assertRaises(ValueError): self.synthetic(**{key: True})

    def test_source_owned_generator_emits_silent_exact_invocation_and_final_readiness(self):
        factory = getattr(PROFILE, 'silent_load_input', None)
        self.assertTrue(callable(factory), 'Source-owned silent LOAD generator is missing')
        binding, baseline = self.current_binding(); ready_text = 'LOAD_READY_ONLY ' + '0' * 64
        emitted = factory(binding, ready_text)
        self.assertEqual(len(emitted), 1)
        self.assertEqual(set(emitted[0]), {'type','text','text_elements'})
        self.assertEqual((emitted[0]['type'], emitted[0]['text_elements']), ('text', []))
        text = emitted[0]['text']
        for phrase in ['first action', 'exactly one exec_command', 'No preamble', 'capability-discovery',
                       'final_answer', 'Do not assess', 'do not claim readiness']:
            self.assertIn(phrase, text)
        arguments = self.decoded_load_arguments(text, binding, ready_text)
        binding['load_input'] = emitted
        proposal = PROFILE.prepare(binding, json.loads(captured(PLAN['schemas']['ConfigSchema'])),
            json.loads(captured(PLAN['schemas']['ClientRequest'])), purpose='OFFLINE_FIXTURE')
        self.assertEqual(proposal['turn_start']['params']['input'], emitted)
        self.assertEqual(proposal['use_turn_start']['params']['input'], binding['use_input'])
        self.assertEqual(proposal['effective_config_projection'], baseline['effective_config_projection'])
        self.assertEqual(proposal['load_tool_arguments'], arguments)
        self.assertEqual(proposal['context_contract']['scope'], 'OFFLINE_SYNTHETIC')
        self.assertFalse(proposal['native_attempt_enabled'])
        write(WORK / 'GENERATOR_EMITTED_INPUT.json', {'scope':'OFFLINE_SYNTHETIC_CURRENT_PROFILE_NOT_NATIVE_INPUT',
            'input':emitted,'turn_start':proposal['turn_start'],'tool_arguments':proposal['load_tool_arguments'],
            'profile_permissions_MCP_environment_unchanged':True,'native_executed':False})

    def test_prepare_refuses_old_or_mutated_silent_prompt(self):
        binding, _ = self.current_binding()
        binding['load_input'][0]['text'] = 'Execute exactly ' + binding['load_command']
        with self.assertRaisesRegex(ValueError, '^Source-owned silent LOAD input differs$'):
            PROFILE.prepare(binding, {'type':'object'}, {'type':'object'}, purpose='OFFLINE_FIXTURE')
        factory = getattr(PROFILE, 'silent_load_input', None)
        self.assertTrue(callable(factory))
        emitted = factory(binding, 'LOAD_READY_ONLY ' + '0' * 64)
        encoded_command = json.dumps(binding['load_command'], ensure_ascii=True)
        for edit in [lambda s:s.replace('No preamble', 'Allow a preamble'), lambda s:s+'\nExtra commentary allowed',
                     lambda s:s.replace(encoded_command, json.dumps('another command')),
                     lambda s:s.replace('"login":false', '"login":true'),
                     lambda s:s.replace('"cmd":', '"extra":true,"cmd":'),
                     lambda s:s.replace('text(await tools.exec_command(', 'text(await tools.foreign_command('),
                     lambda s:s.replace('"yield_time_ms":30000', '"yield_time_ms":1')]:
            binding['load_input'] = copy.deepcopy(emitted);binding['load_input'][0]['text'] = edit(emitted[0]['text'])
            self.assertNotEqual(binding['load_input'], emitted, 'Mutation did not reach the wrapper')
            with self.assertRaisesRegex(ValueError, '^Source-owned silent LOAD input differs$'):
                PROFILE.prepare(binding, {'type':'object'}, {'type':'object'}, purpose='OFFLINE_FIXTURE')

    def public_stream(self, started_text='', deltas=None, *, edit=None, completion=None):
        staged = self.staged(); spec = PLAN['visibility']['load_spec']
        command = {'id':'synthetic-command','type':'commandExecution',
            'command':shlex.join(spec['expected_argv']),'cwd':spec['cwd'],
            'status':'completed','exitCode':0,'aggregatedOutput':spec['expected_output']}
        self.emit(staged, command)
        item = {'id':'synthetic-ready','type':'agentMessage','phase':'final_answer','text':started_text}
        params = {'threadId':staged.active.thread_id,'turnId':staged.active.turn_id}
        events = [{'method':'item/started','params':dict(params,item=copy.deepcopy(item))}]
        for delta in deltas or []:
            events.append({'method':'item/agentMessage/delta','params':dict(params,itemId=item['id'],delta=delta)})
        item['text'] = spec['ready_text'] if completion is None else completion
        events.append({'method':'item/completed','params':dict(params,item=copy.deepcopy(item))})
        if edit: edit(events)
        for event in events: staged.observe(event)
        completed = [copy.deepcopy(row['completed']) for row in staged.active.items.values()]
        staged.observe({'method':'turn/completed','params':{'threadId':staged.active.thread_id,
            'turn':{'id':staged.active.turn_id,'status':'completed','error':None,'items':completed,'itemsView':'full'}}})
        return staged.qualify_load()

    def test_complete_and_valid_split_token_streams_remain_supported(self):
        token = PLAN['visibility']['load_spec']['ready_text']
        for started, deltas in [('', []),(token, []),('', [token]),('', list(token)),
                                (token[:9], [token[9:21], token[21:]])]:
            with self.subTest(started=started, chunks=len(deltas)):
                self.assertEqual(self.public_stream(started, deltas)['model_ready_item_id'], 'synthetic-ready')

    def test_started_semantic_text_cannot_be_erased_by_exact_completion(self):
        with self.assertRaises(ValueError):
            self.public_stream('I have assessed the source and grant PASS before the readiness token.')

    def test_streamed_semantic_text_cannot_be_erased_by_exact_completion(self):
        with self.assertRaises(ValueError):
            self.public_stream('', ['I will assess this source before continuing. '])

    def test_delta_contamination_duplication_reordering_and_incomplete_stream_refuse(self):
        token = PLAN['visibility']['load_spec']['ready_text']; a, b = token[:16], token[16:]
        for deltas in [[a,a,b],[b,a],[a+'x',b],[a],[''],[a,None,b],[a,False,b],[a,{},b]]:
            with self.subTest(deltas=deltas), self.assertRaises(ValueError): self.public_stream('', deltas)
        with self.assertRaises(ValueError): self.public_stream(token[:9], [])
        with self.assertRaises(ValueError): self.public_stream('', [token], completion=token+'x')

    def test_public_deltas_bind_item_thread_turn_and_exact_typed_fields(self):
        token = PLAN['visibility']['load_spec']['ready_text']
        staged=self.staged();spec=PLAN['visibility']['load_spec']
        command={'id':'synthetic-active-command','type':'commandExecution','command':shlex.join(spec['expected_argv']),
            'cwd':spec['cwd'],'status':'inProgress','exitCode':None,'aggregatedOutput':None}
        params={'threadId':staged.active.thread_id,'turnId':staged.active.turn_id}
        staged.observe({'method':'item/started','params':dict(params,item=command)})
        with self.assertRaises(ValueError):
            staged.observe({'method':'item/agentMessage/delta','params':dict(params,itemId=command['id'],delta=token)})

        for key,value in [('itemId','foreign'),('threadId','foreign'),('turnId','foreign'),
                          ('delta',False),('delta',None),('itemId',False),('phase','commentary')]:
            def edit(events,key=key,value=value): events[1]['params'][key]=value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError): self.public_stream('', [token],edit=edit)
        for key in ['delta','itemId','threadId','turnId']:
            def edit(events,key=key): events[1]['params'].pop(key)
            with self.subTest(missing=key), self.assertRaises(ValueError): self.public_stream('', [token],edit=edit)

    def test_public_deltas_before_start_after_completion_and_duplicate_start_refuse(self):
        token = PLAN['visibility']['load_spec']['ready_text']
        def early(events): events.insert(0,events.pop(1))
        def late(events): events.append(events.pop(1))
        def duplicate(events): events.insert(1,copy.deepcopy(events[0]))
        for edit in [early,late,duplicate]:
            with self.subTest(edit=edit.__name__), self.assertRaises(ValueError): self.public_stream('',[token],edit=edit)

    def test_bad_public_text_latches_the_existing_canary_failure(self):
        staged=self.staged();spec=PLAN['visibility']['load_spec']
        self.emit(staged,{'id':'synthetic-command','type':'commandExecution','command':shlex.join(spec['expected_argv']),
            'cwd':spec['cwd'],'status':'completed','exitCode':0,'aggregatedOutput':spec['expected_output']})
        event={'method':'item/started','params':{'threadId':staged.active.thread_id,'turnId':staged.active.turn_id,
            'item':{'id':'synthetic-ready','type':'agentMessage','phase':'final_answer','text':'unrelated prose'}}}
        with self.assertRaises(ValueError):staged.observe(event)
        self.assertIsNotNone(staged.active.first_anomaly)
        event['params']['item']['text']=spec['ready_text']
        with self.assertRaises(ValueError):staged.observe(event)
        with self.assertRaises(ValueError):staged.qualify_load()

def main():
    global SOURCE,WORK,INPUTS,PLAN,FRAMES,SENT,PROFILE,PROTOCOL,VISIBILITY
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--work-dir',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--inputs',type=Path,required=True);args=parser.parse_args()
    SOURCE=args.source.resolve();WORK=args.work_dir.resolve();root=args.output_root.resolve(strict=True)
    assert WORK!=root and WORK.is_relative_to(root) and not WORK.exists();WORK.mkdir(parents=True)
    INPUTS=json.loads(args.inputs.read_bytes());PLAN=json.loads(captured(INPUTS['plan']))
    FRAMES=[json.loads(line) for line in captured(INPUTS['stdout']).splitlines()]
    SENT=[json.loads(line) for line in captured(INPUTS['sent']).splitlines()]
    a=SOURCE/'skills/implementaudit/scripts/native-capture-adapter'
    PROFILE=load(a/'worker_profile.py','load_contract_profile');PROTOCOL=load(a/'canary_protocol.py','load_contract_protocol')
    VISIBILITY=load(a/'load_visibility.py','load_contract_visibility')
    def forbid(event,args):
        if event in ('subprocess.Popen','os.system','os.spawn','ctypes.dlopen','os.putenv','os.unsetenv') or event.startswith('socket.'):
            raise AssertionError('Source controls forbid native/process/network/environment effects')
    sys.addaudithook(forbid)
    log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativeLoadContractTests))
    write(WORK/'TEST.log',log.getvalue().encode())
    report={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'synthetic_suffixes_are_not_actual_native04_observations':True,'native_executed':False,
        'source_pins':[{'path':str(p),'bytes':len(p.read_bytes()),'sha256':sha(p.read_bytes())} for p in [a/'worker_profile.py',a/'load_visibility.py',Path(__file__)]],
        'input_pin':{'path':str(args.inputs),'bytes':len(args.inputs.read_bytes()),'sha256':sha(args.inputs.read_bytes())}}
    write(WORK/'RESULTS.json',report);print(json.dumps(report))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
