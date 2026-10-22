"""Constructed R0033/R0035 executor-binding controls; no native acceptance."""
import argparse,base64,contextlib,copy,hashlib,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]
def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha(x):return hashlib.sha256(x if type(x) is bytes else canonical(x)).hexdigest()
def fence(x):return b'```implementaudit-work-graph\n'+canonical(x)+b'\n```\n'

class ReceiverDispatchControls(unittest.TestCase):
    def setUp(self):
        self.cost=load(ROOT/'fixtures/operational-evidence/native-route-cost-controls.py','receiver_cost_support')
        self.temp=tempfile.TemporaryDirectory(prefix='receiver-dispatch-');self.addCleanup(self.temp.cleanup)
        self.h=self.cost.Harness(Path(self.temp.name));self.scope=self.h.patched();self.scope.__enter__();self.addCleanup(self.scope.__exit__,None,None,None)
        self.wg=self.h.wg;self.route=self.h.expected_scope()
        self.binding=dict(acquisition='NATIVE_CONTINUITY_VERIFIED',controller=self.h.controller,claim=self.h.current['claim_id'],
            receipt=self.h.current['continuity_receipt'],epoch='G0001',candidate_head='a'*40,candidate_tree='b'*40,
            worktree_digest='c'*64,continuity_helper_digest='d'*64,read_set={},input_root_identity='e'*64)
        def node(name,kind='TASK',requires=(),scopes=()):
            return dict(id=name,parent=None if name=='root' else 'root',kind=kind,state='OPEN',requires=list(requires),optional=[],
                reads=[],writes=[],acceptance=['semantic:acceptance:'+name],resources=[],authority=[],effect='READ_ONLY',
                authorization='PERMITTED',independence='KNOWN',resource_demand=1,rank=0,route_scopes=list(scopes),logical_delivery=None,
                future_consumer=None,invalidators=[],independent_results=True,context=dict(locality='GOVERNOR',governor_cost=1,child_cost=2,return_cost=1,useful_value=3),done_evidence=None)
        self.nodes=[node('root','PLAN'),node('review',scopes=[self.route['scope']['identity']]),node('receiver',requires=['review']),node('join','JOIN',requires=['receiver']),node('unrelated')]
        self.nodes[0]['state']='ACTIVE';self.nodes[1].update(state='DONE',done_evidence='f'*64)
        self.nodes[2].update(effect='MUTATION',writes=['semantic:r0033-ordinary-receiver-receipt'],resources=['semantic:writer:r0033-ordinary-receiver-receipt'],rank=10)
        self.nodes[-1].update(effect='EXTERNAL')
        self.scripts=self.h.root/'skills/implementaudit/scripts';self.scripts.mkdir(parents=True)
        custody=(ROOT/'source-peers/native-runtime/skills/implementaudit/scripts/bounded_file_custody.py').read_bytes()
        (self.scripts/'bounded_file_custody.py').write_bytes(custody)
        self.policy=dict(schema='implementaudit.ordinary-native-policy.v1',profile_id='CONSTRUCTED',selection_pin={},instance_selection={},provider={'python_executable':{'path':sys.executable}},
            receiver_node='receiver',consumer='join',code_pins={'implementaudit/scripts/route-transaction.py':self.h.source_digest[7:],
            'implementaudit/scripts/bounded_file_custody.py':sha(custody)},receiver_argv=[sys.executable,'-I','-S','-B',str(self.scripts/'compaction-source-owner-codex-app.py'),'--ordinary-receiver'],
            artifact_root=str(self.h.root),root_thread_id='fixture-root',root_agent_path='/root')
        owner_code=('import hashlib,json\nfrom pathlib import Path\ndef ordinary_policy_v1():\n    p=json.loads('+repr(json.dumps(self.policy))+')\n'
            "    p['code_pins']['implementaudit/scripts/compaction-source-owner-codex-app.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()\n    return p\n").encode()
        (self.scripts/'compaction-source-owner-codex-app.py').write_bytes(owner_code)
        self.policy['code_pins']['implementaudit/scripts/compaction-source-owner-codex-app.py']=sha(owner_code)
        self.pins={k:v for k,v in self.policy['code_pins'].items() if not k.endswith('/route-transaction.py')}
        self.h.request['inputs'] += [dict(identity='skills/'+k,path='skills/'+k,digest='sha256:'+v) for k,v in self.pins.items()]
        self.h.request['inputs'].sort(key=lambda x:x['identity']);self.h.create_records()
        mission=dict(schema='implementaudit.ordinary-review-mission.v1',policy_digest=sha(self.policy),scope=self.route['scope'],mission='Constructed receiver binding',authority_ceiling='NONE')
        packet=json.loads(base64.b64decode(self.h.record['lifecycle']['delivery']['packet']['bytes_b64']));packet['source_event']['body']=canonical(mission).decode()
        self.packet=self.cost.wire(packet)
        for record in [*self.h.objects.values(),self.h.record]:
            life=record['lifecycle'];life['delivery']['packet']=self.packet
            if life['child_return']:
                returned=json.loads(base64.b64decode(life['child_return']['bytes_b64']));returned['packet_digest']=self.packet['digest'];life['child_return']=self.cost.wire(returned)
            if life['governor_decision']:
                decision=json.loads(base64.b64decode(life['governor_decision']['bytes_b64']));decision['return_digest']=life['child_return']['digest'];life['governor_decision']=self.cost.wire(decision)
            record['record_identity']=self.cost.digest({k:v for k,v in record.items() if k!='record_identity'})
        record_raw=json.dumps(self.h.record,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()+b'\n'
        self.h.oid=hashlib.sha1(b'blob '+str(len(record_raw)).encode()+b'\0'+record_raw).hexdigest();self.route=self.h.expected_scope()
        self.cap=dict(schema='implementaudit.ordinary-receiver-binding.v1',producer='R0033',executor='execute_current_ordinary_receiver_v2',
            route_record_oid=self.route['route']['record_oid'],route_scope_digest=self.route['digest'],policy=self.policy,
            record=self.cost.wire(record_raw),source_pins=self.pins,authority_ceiling='NONE',establishes=[])
        self.wg._NATIVE_ROUTE_PRODUCER_SHA256=self.h.source_digest[7:]
    def compile(self,cap=None):
        state=dict(schema='implementaudit.native-state.v1',campaign='fixture',root='root',original_scope='fixture',nodes=sorted(x['id'] for x in self.nodes),
            event=dict(id='fixture-review-return',kind='RETURN',subject='review'),context=dict(host_capacity=2,operator_ceiling=2,reserve=0,route_facts=[],outstanding_deliveries=[]))
        snapshot={'STATE.md':fence(state),'ROADMAP.md':fence(dict(schema='implementaudit.native-roadmap.v1',phases=[])),
            'tasks/fixture.md':fence(dict(schema='implementaudit.native-spec.v1',nodes=self.nodes))}
        self.snapshot=snapshot
        observed=self.wg._RouteScopeObservation(self.route,self.wg._NATIVE_ROUTE_OBSERVATION_KEY)
        if cap is not None:
            # Explicit fixture injection, never an acquisition/authentication claim.
            observed=self.wg._RouteScopeObservation(self.route,self.wg._NATIVE_ROUTE_OBSERVATION_KEY,receiver_binding=cap)
        return self.wg._compile_native_documents_v1(snapshot,self.binding,_route_observation=observed)
    def test_fixed_receiver_is_selected_only_with_owner_binding(self):
        absent=self.compile();self.assertIn('EFFECT_EXECUTOR_UNAVAILABLE',next(n for n in absent['nodes'] if n['id']=='receiver')['blocked_reasons'])
        graph=self.compile(self.cap);dispatch=self.wg.select_native_frontier_v1(graph)
        self.assertEqual(dispatch['selected'],['receiver']);self.assertIn('EFFECT_EXECUTOR_UNAVAILABLE',dispatch['blocked']['unrelated'])
        self.assertEqual(graph['receiver_binding'],self.cap)

    @unittest.skipIf(os.name=='nt','Unsupported-platform refusal is specific to non-Windows hosts')
    def test_unsupported_bootstrap_refuses_before_io(self):
        with mock.patch.object(self.h.rt,'git',side_effect=AssertionError('GIT_REACHED')):
            with self.assertRaisesRegex(self.cost.Refusal,'requires Windows held-file custody'):
                with self.h.rt._ordinary_fixed_source_owner_v2(self.h.root,self.pins):
                    self.fail('unsupported source owner yielded')

    @contextlib.contextmanager
    def actual_bootstrap(self):
        """Real owned Git blobs/files; only canonical eligibility is injected."""
        env={k:v for k,v in os.environ.items() if not k.upper().startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='NUL' if os.name=='nt' else '/dev/null',GIT_TERMINAL_PROMPT='0')
        def git(*args):
            return subprocess.check_output(['git','-C',str(self.h.root),'-c','core.hooksPath='+('NUL' if os.name=='nt' else '/dev/null'),
                '-c','core.autocrlf=false',*args],env=env,stderr=subprocess.PIPE)
        git('init');git('add','skills');git('-c','user.name=Constructed control','-c','user.email=control@example.invalid','commit','-m','Owned fixed bootstrap fixture')
        def routed(repo,*args,**kwargs):
            return self.h.git(repo,*args,**kwargs) if args[:1]==('for-each-ref',) else git(*args).decode().strip()
        def blob(repo,oid,*args,**kwargs):
            return canonical(self.h.objects[oid]) if oid in self.h.objects else git('cat-file','blob',oid)
        with mock.patch.object(self.h.rt,'git',side_effect=routed),mock.patch.object(self.h.rt,'git_blob_bytes',side_effect=blob), \
             mock.patch.object(self.h.rt,'_ordinary_publish_v2',side_effect=AssertionError('PUBLICATION_FORBIDDEN')), \
             mock.patch.object(self.h.rt,'execute_current_ordinary_receiver_v2',side_effect=AssertionError('EXECUTION_FORBIDDEN')):
            yield

    @unittest.skipUnless(os.name=='nt','Selected fixed source uses Windows held-file custody')
    def test_real_fixed_bootstrap_exports_binding_without_effect(self):
        with self.actual_bootstrap(),self.h.rt.current_route_observation_v1(self.h.root,self.h.controller) as observed:
            actual=json.loads(observed.ordinary_receiver_binding_bytes())
        self.assertEqual(actual,self.cap)
        self.assertEqual(self.h.validation.call_count,2)
        with self.assertRaisesRegex(self.cost.Refusal,'closed'):observed.ordinary_receiver_binding_bytes()

    def test_binding_requires_accepted_ordinary_route_and_source_inputs(self):
        for change in (lambda r:r.update(route_state='OPEN'),lambda r:r.update(decision='NOT_REQUIRED'),
                lambda r:r.update(inputs=[x for x in r['inputs'] if x['path']=='input.txt'])):
            rec=copy.deepcopy(self.h.record);change(rec)
            with mock.patch.object(self.h.rt,'_ordinary_fixed_source_owner_v2',side_effect=AssertionError('BOOTSTRAP_REACHED')):
                self.assertIsNone(self.h.rt._ordinary_receiver_binding_from_read_v1(self.h.root,rec,self.h.summary()))

    @unittest.skipUnless(os.name=='nt','Selected fixed source uses Windows held-file custody')
    def test_unaccepted_policy_change_is_refused(self):
        rec=copy.deepcopy(self.h.record);packet=json.loads(base64.b64decode(self.packet['bytes_b64']))
        mission=json.loads(packet['source_event']['body']);mission['policy_digest']='0'*64
        packet['source_event']['body']=canonical(mission).decode();rec['lifecycle']['delivery']['packet']=self.cost.wire(packet)
        with self.actual_bootstrap(),self.assertRaisesRegex(self.cost.Refusal,'accepted fixed policy'):
            self.h.rt._ordinary_receiver_binding_from_read_v1(self.h.root,rec,self.h.summary())

    @unittest.skipUnless(os.name=='nt','Selected fixed source uses Windows held-file custody')
    def test_changed_active_source_is_rejected_before_execution(self):
        with self.actual_bootstrap():
            (self.scripts/'compaction-source-owner-codex-app.py').write_bytes(b'raise AssertionError("UNTRUSTED_EXECUTION")\n')
            with self.assertRaisesRegex(self.cost.Refusal,'active source differs'):
                self.h.rt._ordinary_receiver_binding_from_read_v1(self.h.root,self.h.record,self.h.summary())

    @unittest.skipUnless(os.name=='nt','Selected fixed source uses Windows held-file custody')
    def test_input_drift_cannot_commit_provisional_binding(self):
        with self.actual_bootstrap(),self.assertRaisesRegex(self.cost.Refusal,'live predicate'):
            with self.h.rt.current_route_observation_v1(self.h.root,self.h.controller) as observed:
                observed.ordinary_receiver_binding_bytes();self.h.input.write_bytes(b'changed with refs fixed\n')

    def test_foreign_and_resealed_binding_fields_refuse(self):
        changes=[lambda c:c.update(route_record_oid='0'*40),lambda c:c.update(route_scope_digest='0'*64),
            lambda c:c.update(authority_ceiling='PERMITTED'),lambda c:c['policy'].update(receiver_node='unrelated'),
            lambda c:c['source_pins'].update({'implementaudit/scripts/bounded_file_custody.py':'0'*64}),
            lambda c:c.update(record=self.cost.wire(canonical({'forged':True}))),lambda c:c.update(executor='arbitrary_command')]
        for change in changes:
            c=copy.deepcopy(self.cap);change(c)
            with self.subTest(change=change),self.assertRaises(self.wg.WorkGraphError):self.compile(c)

    def test_no_blanket_mutation_or_wrong_node_clearance(self):
        original=copy.deepcopy(self.nodes)
        changes=[lambda n:n[2].update(writes=['path:outside.txt']),lambda n:n[2].update(effect='EXTERNAL'),
            lambda n:n[2].update(authority=['semantic:new-grant']),lambda n:n[2].update(requires=[]),
            lambda n:n[3].update(requires=['unrelated']),lambda n:n[2]['context'].update(locality='CHILD')]
        for change in changes:
            self.nodes=copy.deepcopy(original);change(self.nodes)
            with self.subTest(change=change):
                graph=self.compile(self.cap)
                self.assertIn('EFFECT_EXECUTOR_UNAVAILABLE',next(n for n in graph['nodes'] if n['id']=='receiver')['blocked_reasons'])
                self.assertNotIn('receiver',self.wg.select_native_frontier_v1(graph)['selected'])

    def test_authorization_and_other_unchanged_gates_still_hold(self):
        original=copy.deepcopy(self.nodes)
        for field,value,reason in [('authorization','MISSING','AUTHORIZATION'),('independence','UNKNOWN','INDEPENDENCE_UNKNOWN')]:
            self.nodes=copy.deepcopy(original);self.nodes[2][field]=value
            graph=self.compile(self.cap);node=next(n for n in graph['nodes'] if n['id']=='receiver')
            self.assertIn(reason,node['blocked_reasons']);self.assertNotIn('receiver',self.wg.select_native_frontier_v1(graph)['selected'])

    def test_frozen_semantic_replay_cannot_add_executor_clearance(self):
        graph=self.compile();forged=copy.deepcopy(graph)
        node=next(n for n in forged['nodes'] if n['id']=='receiver');node['state']='READY';node['blocked_reasons']=[]
        forged['digest']=sha({k:v for k,v in forged.items() if k!='digest'})
        with self.assertRaises(self.wg.WorkGraphError):self.wg.select_native_frontier_v1(forged)
        with mock.patch.object(self.wg,'_native_route_scope_module_v1',side_effect=AssertionError('LIVE_ACQUISITION')):
            self.assertEqual(self.wg.select_native_frontier_v1(self.compile(self.cap))['selected'],['receiver'])

    @unittest.skipUnless(os.name=='nt','Selected fixed source uses Windows held-file custody')
    def test_actual_read_native_run_connects_owner_binding_to_full_compiler(self):
        self.compile();raw=Path(self.h.rt.__file__).read_bytes()
        with self.actual_bootstrap(),mock.patch.object(self.wg,'_native_continuity',return_value=self.binding), \
             mock.patch.object(self.wg,'_native_source_snapshot',return_value=self.snapshot),mock.patch.object(self.wg,'_acquire_native_read_set',return_value={}), \
             mock.patch.object(self.wg,'_native_route_scope_module_v1',return_value=(self.h.rt,Path(self.h.rt.__file__),raw)):
            graph=self.wg.read_native_run_v1(self.h.root,self.h.root)
        self.assertEqual(graph['receiver_binding'],self.cap)
        self.assertEqual(self.wg.select_native_frontier_v1(graph)['selected'],['receiver'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=ROOT);args,rest=p.parse_known_args();ROOT=args.repo_root.resolve()
    unittest.main(argv=[__file__,*rest])
