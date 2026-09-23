"""Synthetic boundary integration; never invokes native processes or a watcher."""
import ast,copy,hashlib,json,pathlib,sys,tempfile,types,unittest
from unittest.mock import patch
OUT=pathlib.Path(__file__).resolve().parent
SCRIPTS=OUT.parents[1]/'skills/implementaudit/scripts'

def load(name):
 p=SCRIPTS/name;m=types.ModuleType(name);m.__file__=str(p)
 tree=ast.parse(p.read_bytes(),filename=str(p))
 # Inspected module declarations only. Native reader CLI main block is excluded.
 allowed=(ast.Import,ast.ImportFrom,ast.Assign,ast.AnnAssign,ast.FunctionDef,ast.ClassDef)
 nodes=[n for n in tree.body if isinstance(n,allowed)]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),m.__dict__);return m
r=load('codex-recovery-native-reader.py');h=load('codex-recovery-config-transition.py')
def forbidden_native(*args,**kwargs):raise AssertionError('native/process/watcher execution forbidden in synthetic tests')
r.native_read=forbidden_native;r.processes=forbidden_native
r.subprocess=types.SimpleNamespace(run=forbidden_native,Popen=forbidden_native,CREATE_NO_WINDOW=0)
r.NativeRecoveryObserver.watch_restart=forbidden_native
# Test-local import path is explicit for isolated Python invocation.
sys.path.insert(0,str(OUT))
USER='C:/synthetic/config.toml';TASK='11111111-1111-4111-8111-111111111111'
PIPES=[r'\\.\pipe\codex-computer-use-'+n*8+'-'+n*4+'-4'+n*3+'-8'+n*3+'-'+n*12 for n in ('1','2','3')]
def material(index):
 pipe=PIPES[index];cfg={'features':{h.FEATURE:True},'mcp_servers':{'node_repl':{'env':{'SKY_CUA_NATIVE_PIPE_DIRECTORY':pipe}}}}
 raw=("[features]\nretain_client_developer_messages=true\n[mcp_servers.node_repl.env]\nSKY_CUA_NATIVE_PIPE_DIRECTORY='"+pipe+"'\n").encode()
 files=[{'metadata':{'path':USER,'exists':True,'bytes':len(raw),'sha256':h._sha(raw),'mtime_ns':index+1},'content':raw}]
 rows=[{'cwd':cwd,'result':{'config':copy.deepcopy(cfg),'layers':[{'name':{'type':'user','file':USER},'config':copy.deepcopy(cfg),'version':'sha256:'+h._jsha(cfg)}],'origins':{}}} for cwd in ('C:/repo','C:/controller')]
 return rows,files

def observer():
 o=object.__new__(r.NativeRecoveryObserver);o.parameters={'task':TASK,'home':'C:/synthetic','repo':'C:/repo','controller_cwd':'C:/controller','plugin_root':'C:/plugin'};o.home=pathlib.Path('C:/synthetic');o.task=TASK;o.observation_successor_spec=None;o.observation_successor_sha256=None;o.epoch_directory=None
 return o

def observation(o,index=0,after=False):
 rows,files=material(index);configs=[h._filter_native(row,{USER:files[0]}) for row in rows]
 owner={'pid':201 if after else 101,'parent_pid':200 if after else 100,'created_utc':'2026-09-09T10:03:01Z' if after else '2026-09-09T10:00:00Z','parent':{'created_utc':'2026-09-09T10:03:00Z' if after else '2026-09-09T09:59:59Z'},'desktop_process_tree':[{'pid':200 if after else 100},{'pid':201 if after else 101}],'override_keys_and_hashes':[]}
 return {'parameters':copy.deepcopy(o.parameters),'binary':{'sha256':r.EXPECTED_BINARY},'parent_binding':{'asar':{'sha256':h.PRODUCER['asar_sha256']}},'configs':configs,'hooks':[],'recovery_hook_binding':[],'package_files':[{'fixture':'reader'}],'source_identity':{'fixture':'reader'},'owner':owner,'observed_utc':'2026-09-09T10:04:00Z' if after else '2026-09-09T10:01:00Z','frontier':{'path':'C:/synthetic/session.jsonl','session_id':TASK},'native_thread':{'id':TASK,'path':'C:/synthetic/session.jsonl','cwd':'C:/repo'}}

def stopped(before):return {'old_ids':[100,101],'matching_pids_present':[],'desktop_native_pids_now':[],'before_identity':r.digest(r.canonical(before)),'observed_utc':'2026-09-09T10:02:00Z'}

def tree_bytes(directory):
 root=pathlib.Path(directory)
 return {path.relative_to(root).as_posix():path.read_bytes() for path in root.rglob('*') if path.is_file()}

def selected_handoff(o,d,b,s,a,bb,ab):
 """Real issuer with three explicitly synthetic native/cleanup boundaries."""
 if isinstance(ab,dict) and 'native_reads' in ab and 'physical_reads' in ab:
  rows,files=ab['native_reads'][0],ab['physical_reads'][0]
 else:
  # Missing-acquisition negative: obtain the valid live selection first, then
  # pass the deliberately missing retained data to finish for provenance refusal.
  import test_affected_helper as f
  rows,files=f.multi_origin_material(PIPES[1],200)
 def protocol():
  o._acquisition_context['protocols'].append({'probe_pid':None,'process_terminated':True,'exit_code':0,'failure_present':False,'streams_complete':True,'streams':{},'bytes':{}})
 def read():protocol();return copy.deepcopy((rows,files))
 def snapshot(*args,**kwargs):protocol();return copy.deepcopy(a)
 with patch.object(o,'read_config_material',side_effect=read),patch.object(o,'snapshot',side_effect=snapshot):
  actual,acquisition,handoff=o.acquire_restarted_boundary(d,b['frontier'],watcher_deadline=r.time.monotonic()+60,before=b,stop=s,before_acquisition=bb)
 return handoff

class EpochTests(unittest.TestCase):
 def setUp(self):
  self.o=observer();self.before=observation(self.o);self.after=observation(self.o,1,True);self.stop=stopped(self.before)
  self.prefix=patch.object(r,'verify_historical_prefix',return_value=None);self.prefix.start();self.addCleanup(self.prefix.stop)
 def require_api(self):self.assertTrue(hasattr(self.o,'capture_epoch_boundary'),'initial acquisition capability missing')
 def synthetic_protocol(self):
  # Synthetic successful cleanup at a mocked read/snapshot boundary only.
  self.o._acquisition_context['protocols'].append({'probe_pid':None,'process_terminated':True,'exit_code':0,'failure_present':False,'streams_complete':True,'streams':{},'bytes':{}})
 def acquire(self,index,obs,*,supplied_material=None):
  self.require_api();events=[]
  def synthetic_protocol():
   # Three synthetic cleanup records at mocked boundaries; no native observations.
   self.synthetic_protocol()
  def read():events.append('material');synthetic_protocol();return copy.deepcopy(material(index) if supplied_material is None else supplied_material)
  def snap(*args,**kw):events.append('snapshot');synthetic_protocol();return copy.deepcopy(obs)
  with patch.object(self.o,'read_config_material',side_effect=read),patch.object(self.o,'snapshot',side_effect=snap):
   result=self.o.capture_epoch_boundary()
  self.assertEqual(events,['material','snapshot','material']);return result
 def epoch(self,directory):
  b,bb=self.acquire(0,self.before);a,ab=self.acquire(1,self.after)
  self.o.write_epoch_record(directory,'before',b,bb);self.o.write_epoch_record(directory,'stopped',self.stop,None)
  handoff=selected_handoff(self.o,directory,b,self.stop,a,bb,ab)
  self.o.finish_initial_epoch(directory,b,self.stop,a,bb,ab,handoff=handoff)
  return bb,ab
 def read_epoch(self,directory,index=1,obs=None):
  self.o.epoch_directory=directory
  with patch.object(self.o,'read_config_material',side_effect=lambda:copy.deepcopy(material(index))),patch.object(self.o,'snapshot',return_value=copy.deepcopy(obs or self.after)):
   return self.o._current_input_context()
 def test_unchanged_v1(self):
  with tempfile.TemporaryDirectory() as d:
   a=observation(self.o,0,True)
   for stage,v in [('before',self.before),('stopped',self.stop),('restarted',a)]:self.o.write_observation(d,stage,v)
   self.assertEqual(self.o.read_epoch(d)[2],a)
 def test_exact_initial_uuid_and_independent_readback_preserve_facts(self):
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d);result=self.read_epoch(d);self.assertEqual(result[0],self.before);self.assertEqual(result[2],self.after)
   data=b''.join(p.read_bytes() for p in pathlib.Path(d).glob('*.json'))
   self.assertNotIn(b'retain_client_developer_messages=true',data);self.assertNotIn(b'current_raw_native',data)
 def test_acquisition_unstable_pairs_refused(self):
  self.require_api()
  for changed in ('native','physical'):
   first=material(1);second=copy.deepcopy(first)
   if changed=='native':second[0][0]['result']['config']['extra']='drift'
   else:second[1][0]['metadata']['mtime_ns']=9
   reads=iter((first,second))
   def read():self.synthetic_protocol();return next(reads)
   def snap(*args,**kwargs):self.synthetic_protocol();return self.after
   with patch.object(self.o,'read_config_material',side_effect=read),patch.object(self.o,'snapshot',side_effect=snap):
    with self.assertRaisesRegex(r.Refusal,'NATIVE_PAIR_CHANGED' if changed=='native' else 'PHYSICAL_PAIR_CHANGED'):self.o.capture_epoch_boundary()
 def test_missing_forged_witness_and_wrong_subject_refused(self):
  self.require_api()
  for case in ('missing','forged','producer','task','source','after_hash','witness_shape'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    self.epoch(d);p=pathlib.Path(d)/'restarted.json';record=json.loads(p.read_bytes())
    if case=='missing':record['initial_config_transition']=None
    elif case=='witness_shape':record['initial_config_transition']=[]
    elif case=='forged':record['initial_config_transition']['witness']['previous_value']=PIPES[2]
    elif case=='producer':record['observation']['parent_binding']['asar']['sha256']='0'*64
    elif case=='task':record['observation']['native_thread']['id']='other-task'
    elif case=='source':record['observation']['source_identity']={'fixture':'other-reader'}
    else:record['config_acquisition']['native_results_sha256']='0'*64
    p.write_bytes(r.canonical(record))
    with self.assertRaises(r.Refusal):self.read_epoch(d)
 def test_stale_independent_after_refused(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d)
   with self.assertRaises(r.Refusal):self.read_epoch(d,2,observation(self.o,2,True))
 def test_mtime_only_and_extra_field_refused(self):
  self.require_api()
  for case in ('mtime','field'):
   rows,files=material(0 if case=='mtime' else 1)
   if case=='mtime':files[0]['metadata']['mtime_ns']=9
   else:
    for row in rows:row['result']['config']['extra']='drift'
   a=copy.deepcopy(self.after);a['configs']=[h._filter_native(row,{USER:files[0]}) for row in rows]
   b,bb=self.acquire(0,self.before)
   a,ab=self.acquire(0,a,supplied_material=(rows,files))
   with tempfile.TemporaryDirectory() as d:
    self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',self.stop,None)
    handoff=selected_handoff(self.o,d,b,self.stop,a,bb,ab)
    with self.assertRaises(r.Refusal):self.o.finish_initial_epoch(d,b,self.stop,a,bb,ab,handoff=handoff)
    self.assertEqual(json.loads((pathlib.Path(d)/'restarted-observed.json').read_bytes())['observation'],a)
    self.assertEqual(json.loads((pathlib.Path(d)/'epoch-outcome.json').read_bytes())['outcome'],'REFUSED_NO_AUTHORITY')
 def test_failed_post_snapshot_read_retains_actual_after(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   with patch.object(self.o,'read_config_material',side_effect=[material(1),r.Refusal('fixture native cleanup failed')]),patch.object(self.o,'snapshot',return_value=self.after):
    with self.assertRaises(r.Refusal):self.o.capture_epoch_boundary(directory=d)
   self.assertEqual(json.loads((pathlib.Path(d)/'restarted-observed.json').read_bytes())['observation'],self.after)
 def test_later_pipe_transition_derives_intermediate_distinctly(self):
  self.require_api();b,bb=self.acquire(0,self.before);a,ab=self.acquire(1,self.after)
  initial=self.o.initial_transition(b,a,bb,ab)
  current=observation(self.o,2,True);c,cb=self.acquire(2,current)
  later=self.o.initial_transition(a,c,ab,cb)['witness']
  rows,files=material(2)
  evidence=r.validate_initial_config_chain(b,a,initial,[copy.deepcopy(rows),copy.deepcopy(rows)],[copy.deepcopy(files),copy.deepcopy(files)],later_witness=later)
  self.assertEqual(evidence['intermediate']['material_kind'],'derived_inverse_not_observed')
  self.assertEqual(evidence['initial']['reads_verified'],0)
  self.assertEqual(evidence['later']['reads_verified'],2)
  broken=copy.deepcopy(initial);broken['after_acquisition']['native_results_sha256']='0'*64
  with self.assertRaises(r.Refusal):r.validate_initial_config_chain(b,a,broken,[rows,copy.deepcopy(rows)],[files,copy.deepcopy(files)],later_witness=later)

 def test_source_and_pipe_successor_consumes_changed_initial_epoch(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   oldroot=str(OUT/'old-package');newroot=str(OUT/'new-package')
   names=['skills/implementaudit/scripts/codex-recovery-native-reader.py','skills/implementaudit/scripts/route-transaction.py']
   def inventory(root,token):return [{'path':str(pathlib.Path(root)/n),'exists':True,'bytes':1,'sha256':token*64,'mtime_ns':1} for n in names]
   self.o.parameters['plugin_root']=oldroot
   self.before=observation(self.o);self.after=observation(self.o,1,True)
   for obs in (self.before,self.after):
    obs['package_files']=inventory(oldroot,'1');obs['source_identity']=obs['package_files'][0]
    obs['hooks']=[{'hooks':[{'sourcePath':str(pathlib.Path(oldroot)/'hooks/hooks.json')}]}]
   self.stop=stopped(self.before);bb,ab=self.epoch(d)
   current=copy.deepcopy(self.after);current['configs']=observation(self.o,2,True)['configs']
   current['parameters']['plugin_root']=newroot;current['package_files']=inventory(newroot,'2');current['source_identity']=current['package_files'][0]
   current['hooks']=[{'hooks':[{'sourcePath':str(pathlib.Path(newroot)/'hooks/hooks.json')}]}]
   _,cb=self.acquire(2,current)
   later=self.o.initial_transition(self.after,current,ab,cb)['witness']
   receipt={'schema':'implementaudit.recovery-consumer-source-transition.v1','predecessor_root':oldroot,'successor_root':newroot,'epoch_files':r.epoch_file_pins(d),'predecessor_files':[{'path':n,'bytes':1,'sha256':'1'*64} for n in names],'successor_files':[{'path':n,'bytes':1,'sha256':'2'*64} for n in names],'review_subject_sha256':'a'*64}
   spec={'schema':'implementaudit.observation-successor-spec.v1','source_transition':receipt,'source_transition_sha256':h._jsha(receipt),'config_witness':later,'review_binding':{'subject_sha256':'a'*64,'report_sha256':'b'*64}}
   specpath=pathlib.Path(d)/'successor.json';specpath.write_bytes(r.canonical(spec))
   self.assertEqual(r.load_successor_spec(specpath,r.digest(specpath.read_bytes())),spec)
   self.o.parameters['plugin_root']=newroot
   with patch.object(self.o,'successor_spec',return_value=spec):
    result=self.read_epoch(d,2,current)
   self.assertEqual(result[2],self.after);self.assertEqual(result[3],current)
   self.assertEqual(result[4]['source']['changed_paths'],sorted(names))
   self.assertEqual(result[4]['config']['reads_verified'],2)
 def test_new_consumer_refuses_unterminated_native_read(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d);self.o.epoch_directory=d;self.o.binary=pathlib.Path('C:/synthetic/codex.exe');self.o.repo=pathlib.Path('C:/repo');self.o.controller_cwd=pathlib.Path('C:/controller');self.o.env={}
   with patch.object(r,'native_read',return_value=([],{'failure':None,'process_terminated':False})),patch.object(self.o,'snapshot',side_effect=AssertionError('snapshot must not run after failed native cleanup')):
    with self.assertRaises(r.Refusal):self.o._current_input_context()
 def test_current_read_race_on_nested_witness_is_refused(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d);self.o.epoch_directory=d
   def snap(*args,**kw):
    p=pathlib.Path(d)/'restarted.json';p.write_bytes(p.read_bytes()+b' ');return self.after
   with patch.object(self.o,'read_config_material',side_effect=lambda:copy.deepcopy(material(1))),patch.object(self.o,'snapshot',side_effect=snap):
    with self.assertRaisesRegex(r.Refusal,'epoch bytes changed'):self.o._current_input_context()
 def test_current_identity_binds_v2_witness_record_bytes(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d);one=self.read_epoch(d)
   p=pathlib.Path(d)/'restarted.json';p.write_bytes(p.read_bytes()+b' ')
   two=self.read_epoch(d)
   self.assertEqual(len(one),6,'v2 epoch identity must be returned with checked file pins')
   self.assertNotEqual(one[5],two[5])

 def test_v2_partial_record_refuses_safely(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d)
   for value in ([], {'schema':r._EPOCH_V2}):
    (pathlib.Path(d)/'before.json').write_bytes(r.canonical(value))
    with self.assertRaises(r.Refusal):self.o.read_epoch(d)
 def test_v2_direct_epoch_read_never_acquires_native_material(self):
  self.require_api()
  with tempfile.TemporaryDirectory() as d:
   self.epoch(d)
   with patch.object(self.o,'read_config_material',side_effect=AssertionError('hidden native call')):
    with self.assertRaisesRegex(r.Refusal,'explicit independently'):self.o.read_epoch(d)
 def test_rich_derived_chain_retains_origins_and_all_layer_bindings(self):
  self.require_api()
  import test_affected_helper as fixture
  first=fixture.fixture();old,after_reads,after_files,initial_w=first
  h.validate_config_transition(*first)
  middle=[h._filter_native(row,h._physical_map(after_files[0])) for row in after_reads[0]]
  third=copy.deepcopy(first);third[0]=middle
  oldpipe,newpipe=initial_w['current_value'],PIPES[2]
  # Independent synthetic third material uses the rich user/system/session layers.
  third_raw=fixture.physical(newpipe)
  for read in third[1]:
   for row in read:row['result']=fixture.native(third_raw)
  for files in third[2]:files[0]={'content':third_raw,'metadata':fixture.meta(third_raw,300)}
  third[3]['previous_value']=oldpipe;third[3]['current_value']=newpipe;fixture.repin(third)
  h.validate_config_transition(*third)
  native,files,binding=h.derive_previous_material(middle,third[1][0],third[2][0],third[3])
  restored,evidence=h.validate_derived_transition(old,native,files,initial_w,binding)
  self.assertEqual(restored,middle);self.assertEqual(evidence['reads_verified'],0)
  for key in ('material_kind','native_results_sha256','physical_metadata_sha256','filtered_configs_sha256'):
   broken=copy.deepcopy(binding);broken[key]='forged'
   with self.assertRaises(h.ConfigTransitionRefusal):h.validate_derived_transition(old,native,files,initial_w,broken)



class Epoch02Tests(unittest.TestCase):
 setUp=EpochTests.setUp

 def materials(self):
  import test_affected_helper as f
  result=[]
  for index in range(3):
   rows,files=f.multi_origin_material(PIPES[index],100*(index+1))
   configs,binding=h.observed_config_material([rows,copy.deepcopy(rows)],[files,copy.deepcopy(files)])
   obs=observation(self.o,index,index>0);obs['configs']=configs
   result.append((obs,{'binding':binding,'native_reads':[rows,copy.deepcopy(rows)],'physical_reads':[files,copy.deepcopy(files)]}))
  return result

 def initial(self):
  (b,bb),(a,ab),_=self.materials()
  return b,stopped(b),a,bb,ab

 def finish(self,d,b,s,a,bb,ab):
  self.o.write_epoch_record(d,'before',b,bb)
  self.o.write_epoch_record(d,'stopped',s,None)
  handoff=selected_handoff(self.o,d,b,s,a,bb,ab)
  return self.o.finish_initial_epoch(d,b,s,a,bb,ab,handoff=handoff)

 def diagnostic(self,d):
  self.assertTrue((pathlib.Path(d)/'initial-epoch-failure.json').is_file(),'bounded failure diagnostic missing')
  return json.loads((pathlib.Path(d)/'initial-epoch-failure.json').read_bytes())

 def assert_refused(self,d):
  value=json.loads((pathlib.Path(d)/'epoch-outcome.json').read_bytes())
  self.assertEqual(value,{'schema':'implementaudit.epoch-outcome.v1','outcome':'REFUSED_NO_AUTHORITY','currentness_restored':False})

 def test_full_before_digest_consumer_accepts_multiple_exact_origins(self):
  b,s,a,bb,ab=self.initial()
  transition=self.o.initial_transition(b,a,bb,ab)
  result=r.validate_initial_config_chain(b,a,transition,ab['native_reads'],ab['physical_reads'])
  self.assertEqual(result['before_inverse']['native_results_sha256'],bb['binding']['native_results_sha256'])
  self.assertEqual(result['before_inverse']['physical_metadata_sha256'],bb['binding']['physical_metadata_sha256'])
  self.assertEqual(result['ordinary_effect_authority'],'NONE')

 def test_two_distinct_hops_preserve_complete_ancestry(self):
  (b,bb),(a,ab),(c,cb)=self.materials()
  transition=self.o.initial_transition(b,a,bb,ab)
  later=self.o.initial_transition(a,c,ab,cb)['witness']
  result=r.validate_initial_config_chain(b,a,transition,cb['native_reads'],cb['physical_reads'],later_witness=later)
  self.assertEqual(result['intermediate']['native_results_sha256'],ab['binding']['native_results_sha256'])
  self.assertEqual(result['before_inverse']['native_results_sha256'],bb['binding']['native_results_sha256'])
  self.assertNotEqual(bb['binding']['native_results_sha256'],ab['binding']['native_results_sha256'])
  self.assertNotEqual(ab['binding']['native_results_sha256'],cb['binding']['native_results_sha256'])
  self.assertEqual(result['initial']['reads_verified'],0)
  self.assertEqual(result['intermediate']['material_kind'],'derived_inverse_not_observed')
  for target in ('before_acquisition','after_acquisition'):
   broken=copy.deepcopy(transition);broken[target]['native_results_sha256']='0'*64
   with self.assertRaises(r.Refusal):r.validate_initial_config_chain(b,a,broken,cb['native_reads'],cb['physical_reads'],later_witness=later)

 def test_origin_metadata_population_and_config_changes_remain_refused(self):
  for case in ('metadata','missing','extra','config','physical','forged_before'):
   with self.subTest(case=case):
    b,s,a,bb,ab=self.initial()
    if case=='forged_before':bb['binding']['native_results_sha256']='0'*64
    else:
     for rows in ab['native_reads']:
      for row in rows:
       origins=row['result']['origins']
       if case=='metadata':origins['model']['metadata']['rank']=8
       elif case=='missing':del origins['stable.system']
       elif case=='extra':origins['extra.system']=copy.deepcopy(origins['stable.system'])
       elif case=='config':row['result']['config']['model']='different'
     if case=='physical':
      for files in ab['physical_reads']:
       files[0]['content']+=b'# unrelated edit\n'
       files[0]['metadata'].update(bytes=len(files[0]['content']),sha256=h._sha(files[0]['content']))
     a['configs'],ab['binding']=h.observed_config_material(ab['native_reads'],ab['physical_reads'])
    transition=self.o.initial_transition(b,a,bb,ab)
    with self.assertRaises(r.Refusal):r.validate_initial_config_chain(b,a,transition,ab['native_reads'],ab['physical_reads'])

 def test_failure_retains_exact_input_pins_and_safe_available_material(self):
  b,s,a,bb,ab=self.initial();s['matching_pids_present']=[101]
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(r.Refusal):self.finish(d,b,s,a,bb,ab)
   self.assert_refused(d);record=self.diagnostic(d)
   self.assertEqual((record['stage'],record['predicate']),('STOP_ORDER','STOP_BINDING'))
   self.assertEqual(record['authority'],'NONE');self.assertFalse(record['currentness'])
   for name in ('before.json','stopped.json','restarted-observed.json'):
    self.assertEqual(record['input_files'][name]['sha256'],r.digest((pathlib.Path(d)/name).read_bytes()))
   for name in ('codex-recovery-native-reader.py','codex-recovery-config-transition.py'):
    self.assertEqual(record['sources'][name]['sha256'],r.digest((SCRIPTS/name).read_bytes()))
   for key,acq in (('before',bb),('after',ab)):
    material=record['acquisitions'][key]
    self.assertEqual(material['status'],'AVAILABLE_VALID')
    self.assertEqual(material['binding_sha256'],r.digest(r.canonical(acq['binding'])))
    self.assertEqual(material['native_results_sha256'],acq['binding']['native_results_sha256'])
   self.assertEqual(record['witness']['status'],'AVAILABLE_VALID')
   self.assertEqual(record['selected_material']['status'],'AVAILABLE_VALID')
   raw=json.dumps(record)
   for secret in ('fixture-model','C:/fixture',PIPES[0],PIPES[1],'retain_client_developer_messages=true'):
    self.assertNotIn(secret,raw)

 def test_failures_have_discriminating_bounded_stages(self):
  cases=[('witness','CONFIG_IDENTITY','INITIAL_WITNESS'),
         ('physical','INVERSE_PHYSICAL','PHYSICAL_INVERSE'),
         ('native','INVERSE_NATIVE','RESOLVED_CONFIG_INVERSE'),
         ('before_native','INITIAL_BEFORE_BINDING','BEFORE_NATIVE_DIGEST'),
         ('before_physical','INITIAL_BEFORE_BINDING','BEFORE_PHYSICAL_DIGEST'),
         ('stable','STABLE_SOURCE','EPOCH_STABLE_FIELDS'),
         ('stop','STOP_ORDER','STOP_BINDING'),('order','STOP_ORDER','STARTUP_ORDER'),
         ('prefix','HISTORICAL_PREFIX','HISTORICAL_PREFIX_REFUSED'),
         ('write','FINAL_WRITE','UNKNOWN')]
  for case,stage,predicate in cases:
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    b,s,a,bb,ab=self.initial()
    if case=='physical':
     b['configs'][0]['layers'][1]['files'][0]['sha256']='0'*64
     bb['binding']['filtered_configs_sha256']=h._jsha(b['configs']);s=stopped(b)
    elif case=='native':
     for rows in ab['native_reads']:
      for row in rows:row['result']['config']['model']='different'
     a['configs'],ab['binding']=h.observed_config_material(ab['native_reads'],ab['physical_reads'])
    elif case=='before_native':bb['binding']['native_results_sha256']='0'*64
    elif case=='before_physical':bb['binding']['physical_metadata_sha256']='0'*64
    elif case=='stable':a['hooks']=[{'different':True}]
    elif case=='stop':s['matching_pids_present']=[101]
    elif case=='order':a['observed_utc']=b['observed_utc']
    original_transition=self.o.initial_transition
    original_write=self.o.write_epoch_record
    def transition(*args):
     value=original_transition(*args)
     if case=='witness':value['witness']['producer']={}
     return value
    def write(*args,**kwargs):
     if case=='write' and args[1]=='restarted':raise OSError('SECRET_WRITE_TOKEN')
     return original_write(*args,**kwargs)
    prefix_error=r.Refusal('SECRET_PREFIX_TOKEN') if case=='prefix' else None
    with patch.object(self.o,'initial_transition',side_effect=transition),patch.object(self.o,'write_epoch_record',side_effect=write),patch.object(r,'verify_historical_prefix',side_effect=prefix_error):
     with self.assertRaises(r.Refusal):self.finish(d,b,s,a,bb,ab)
    record=self.diagnostic(d)
    self.assertEqual((record['stage'],record['predicate']),(stage,predicate))
    self.assert_refused(d)
    self.assertNotIn('SECRET_',json.dumps(record))

 def test_secret_exceptions_are_unknown_without_arbitrary_text(self):
  for error in (r.Refusal('SECRET_REFUSAL'),ValueError('SECRET_VALUE'),KeyError('SECRET_KEY'),TypeError('SECRET_TYPE'),OSError('SECRET_OS')):
   with self.subTest(error=type(error).__name__),tempfile.TemporaryDirectory() as d:
    b,s,a,bb,ab=self.initial()
    with patch.object(self.o,'validate_epoch',side_effect=error):
     with self.assertRaisesRegex(r.Refusal,'initial epoch relation refused; actual after retained'):self.finish(d,b,s,a,bb,ab)
    record=self.diagnostic(d)
    self.assertEqual((record['stage'],record['predicate']),('EPOCH_RELATION','UNKNOWN'))
    self.assertNotIn('SECRET_',json.dumps(record));self.assert_refused(d)

 def test_missing_and_malformed_material_stays_unavailable(self):
  for case in ('missing','malformed','witness','secret_path'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    b,s,a,bb,ab=self.initial()
    if case=='missing':ab={}
    elif case=='malformed':ab['binding']={'SECRET_KEY':'SECRET_VALUE'}
    elif case=='secret_path':ab['binding']['user_config_path']='SECRET_USER_CONFIG_PATH'
    real=self.o.initial_transition
    def build(*args):
     value=real(*args)
     if case=='witness':value['witness']['previous_value']='SECRET_BAD_WITNESS'
     return value
    with patch.object(self.o,'initial_transition',side_effect=build):
     with self.assertRaises(r.Refusal):self.finish(d,b,s,a,bb,ab)
    record=self.diagnostic(d)
    if case in ('missing','malformed'):self.assertEqual(record['acquisitions']['after']['status'],'UNAVAILABLE')
    self.assertEqual(record['witness']['status'],'UNAVAILABLE')
    self.assertNotIn('SECRET_',json.dumps(record));self.assert_refused(d)

 def test_diagnostic_write_failure_preserves_original_refusal_and_actual_after(self):
  self.assertTrue(hasattr(self.o,'_write_initial_failure_diagnostic'),'diagnostic persistence capability missing')
  b,s,a,bb,ab=self.initial();s['matching_pids_present']=[101]
  with tempfile.TemporaryDirectory() as d:
   with patch.object(self.o,'_write_initial_failure_diagnostic',side_effect=OSError('SECRET_DIAGNOSTIC')):
    with self.assertRaisesRegex(r.Refusal,'initial epoch relation refused; actual after retained'):self.finish(d,b,s,a,bb,ab)
   self.assert_refused(d)
   self.assertEqual(json.loads((pathlib.Path(d)/'restarted-observed.json').read_bytes())['observation'],a)
   self.assertFalse((pathlib.Path(d)/'restarted.json').exists())

 def test_refusal_outcome_write_failure_still_preserves_original_refusal(self):
  b,s,a,bb,ab=self.initial();s['matching_pids_present']=[101]
  with tempfile.TemporaryDirectory() as d:
   with patch.object(self.o,'write_epoch_outcome',side_effect=OSError('SECRET_OUTCOME')):
    with self.assertRaisesRegex(r.Refusal,'initial epoch relation refused; actual after retained'):self.finish(d,b,s,a,bb,ab)
   self.assertFalse((pathlib.Path(d)/'restarted.json').exists())
   self.assertEqual(self.diagnostic(d)['predicate'],'STOP_BINDING')

 def test_terminal_attempt_cannot_be_overwritten_or_resumed(self):
  for success in (False,True):
   with self.subTest(success=success),tempfile.TemporaryDirectory() as d:
    b,s,a,bb,ab=self.initial()
    if not success:s['matching_pids_present']=[101]
    if success:self.finish(d,b,s,a,bb,ab)
    else:
     with self.assertRaises(r.Refusal):self.finish(d,b,s,a,bb,ab)
    saved=tree_bytes(d)
    with self.assertRaises(r.Refusal):self.o.finish_initial_epoch(d,b,stopped(b),a,bb,ab)
    self.assertEqual(saved,tree_bytes(d))
    with self.assertRaises(r.Refusal):self.o.acquire_restarted_boundary(d,b['frontier'],watcher_deadline=r.time.monotonic()+60)
    self.assertEqual(saved,tree_bytes(d))

 def test_unretained_actual_after_is_not_claimed_retained(self):
  b,s,a,bb,ab=self.initial()
  with tempfile.TemporaryDirectory() as d:
   self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
   handoff=selected_handoff(self.o,d,b,s,a,bb,ab)
   with patch.object(self.o,'write_epoch_record',side_effect=OSError('SECRET_ACTUAL_AFTER_WRITE')):
    with self.assertRaises(r.Refusal) as caught:self.o.finish_initial_epoch(d,b,s,a,bb,ab,handoff=handoff)
   self.assertNotIn('actual after retained',str(caught.exception))
   self.assertEqual(self.diagnostic(d)['input_files']['restarted-observed.json']['status'],'UNAVAILABLE')

 def test_stale_helper_pin_still_refuses_before_use(self):
  with patch.object(r,'CONFIG_TRANSITION_DIGEST','0'*64):
   with self.assertRaisesRegex(r.Refusal,'helper source differs'):r._config_helper()



class TerminalProtocolTests(unittest.TestCase):
 """New terminal cases share fixture methods without replaying inherited tests."""
 setUp=Epoch02Tests.setUp
 materials=Epoch02Tests.materials
 initial=Epoch02Tests.initial
 diagnostic=Epoch02Tests.diagnostic
 assert_refused=Epoch02Tests.assert_refused

 def first_refusal_with_both_writes_failed(self,d):
  b,s,a,bb,ab=self.initial()
  self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
  handoff=selected_handoff(self.o,d,b,s,a,bb,ab)
  arguments=(b,s,a,bb,ab)
  self.used_token=handoff
  with patch.object(r,'verify_historical_prefix',side_effect=r.Refusal('synthetic historical refusal')) as prefix,patch.object(self.o,'write_epoch_outcome',side_effect=OSError('synthetic outcome failure')),patch.object(self.o,'_write_initial_failure_diagnostic',side_effect=OSError('synthetic diagnostic failure')):
   with self.assertRaises(r.Refusal):self.o.finish_initial_epoch(d,*arguments,handoff=handoff)
  self.assertEqual(prefix.call_count,1,'first attempt must reach the actual relation validator')
  self.assertFalse((pathlib.Path(d)/'restarted.json').exists())
  return arguments

 def assert_terminal_finish(self,o,d,arguments):
  saved=tree_bytes(d)
  with patch.object(o,'validate_epoch',side_effect=AssertionError('terminal reentry reached validators')):
   with self.assertRaises(r.Refusal):o.finish_initial_epoch(d,*arguments,handoff=getattr(self,'used_token',None))
  self.assertEqual(saved,tree_bytes(d))

 def test_both_failure_writes_fail_same_observer_cannot_finish_again(self):
  with tempfile.TemporaryDirectory() as d:
   arguments=self.first_refusal_with_both_writes_failed(d)
   self.assert_terminal_finish(self.o,d,arguments)

 def test_both_failure_writes_fail_fresh_observer_cannot_finish_retained_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   arguments=self.first_refusal_with_both_writes_failed(d)
   self.assert_terminal_finish(observer(),d,arguments)

 def test_separate_python_process_cannot_reconstruct_finish_from_retained_inputs(self):
  import base64,os,subprocess
  def encode(value):
   if isinstance(value,bytes):return {'fixture_bytes_base64':base64.b64encode(value).decode('ascii')}
   if isinstance(value,dict):return {key:encode(item) for key,item in value.items()}
   if isinstance(value,(list,tuple)):return [encode(item) for item in value]
   return value
  with tempfile.TemporaryDirectory() as temporary:
   scratch=pathlib.Path(temporary);d=scratch/'epoch';d.mkdir()
   b,s,a,bb,ab=self.first_refusal_with_both_writes_failed(d)
   # Retain data only, never an in-memory admission object or reconstructed token.
   saved=[b,s,a,{'binding':bb['binding']},{key:ab[key] for key in ('binding','native_reads','physical_reads')}]
   arguments=scratch/'saved-synthetic-arguments.json';arguments.write_text(json.dumps(encode(saved)),encoding='utf8')
   child=r'''
import base64,importlib.util,json,pathlib,sys
from unittest.mock import patch
fixture,arguments,directory=sys.argv[1:]
spec=importlib.util.spec_from_file_location('terminal_subprocess_fixture',fixture)
e=importlib.util.module_from_spec(spec);sys.modules[spec.name]=e;spec.loader.exec_module(e)
def decode(value):
 if isinstance(value,dict):
  if set(value)=={'fixture_bytes_base64'}:return base64.b64decode(value['fixture_bytes_base64'],validate=True)
  return {key:decode(item) for key,item in value.items()}
 if isinstance(value,list):return [decode(item) for item in value]
 return value
args=decode(json.loads(pathlib.Path(arguments).read_bytes()));o=e.observer()
with patch.object(e.r,'verify_historical_prefix',return_value=None):
 try:o.finish_initial_epoch(directory,*args)
 except e.r.Refusal:print('REFUSED_RECONSTRUCTED_ENTRY');sys.exit(0)
print('RETURNED_FROM_RECONSTRUCTED_ENTRY');sys.exit(1)
'''
   before=tree_bytes(d)
   env={**os.environ,'TMP':str(scratch),'TEMP':str(scratch),'TMPDIR':str(scratch)}
   completed=subprocess.run([sys.executable,'-I','-S','-B','-c',child,str(pathlib.Path(__file__).resolve()),str(arguments),str(d)],cwd=scratch,env=env,capture_output=True,text=True,timeout=20)
   self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
   self.assertEqual(completed.stdout.strip(),'REFUSED_RECONSTRUCTED_ENTRY')
   self.assertEqual(before,tree_bytes(d))

 def test_first_finish_with_matching_prewritten_actual_after_is_valid(self):
  b,s,a,bb,ab=self.initial()
  with tempfile.TemporaryDirectory() as d:
   self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
   handoff=selected_handoff(self.o,d,b,s,a,bb,ab)
   self.o.write_epoch_record(d,'restarted-observed',a,None)
   self.o.finish_initial_epoch(d,b,s,a,bb,ab,handoff=handoff)
   self.assertEqual(json.loads((pathlib.Path(d)/'restarted.json').read_bytes())['observation'],a)

 def ready(self,d):
  arguments=self.initial();b,s,a,bb,ab=arguments
  self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
  token=selected_handoff(self.o,d,*arguments);self.used_token=token
  return arguments,token

 def test_copied_observer_cannot_use_original_handoff(self):
  with tempfile.TemporaryDirectory() as d:
   arguments,token=self.ready(d)
   copied=copy.copy(self.o)
   with patch.object(copied,'validate_epoch',side_effect=AssertionError('foreign observer reached validators')):
    with self.assertRaises(r.Refusal):copied.finish_initial_epoch(d,*arguments,handoff=token)

 def test_handoff_is_not_copyable_or_serializable(self):
  import pickle
  with tempfile.TemporaryDirectory() as d:
   _,token=self.ready(d)
   for operation in (copy.copy,copy.deepcopy,pickle.dumps):
    with self.subTest(operation=operation.__name__),self.assertRaises(TypeError):operation(token)

 def test_expired_selection_handoff_is_consumed_without_validation(self):
  with tempfile.TemporaryDirectory() as d:
   arguments,token=self.ready(d)
   with patch.object(r.time,'monotonic',return_value=r.time.monotonic()+1000),patch.object(self.o,'validate_epoch',side_effect=AssertionError('expired selection reached validators')):
    with self.assertRaises(r.Refusal):self.o.finish_initial_epoch(d,*arguments,handoff=token)
   self.assertNotIn('_initial_finish_handoff',self.o.__dict__)

 def test_missing_foreign_consumed_and_mismatched_handoffs_never_validate(self):
  for case in ('missing','foreign','copied','epoch','task','parameters','source','helper','before','stop','frontier','after','binding','native','physical','selection'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    self.o=observer();arguments,token=self.ready(d);b,s,a,bb,ab=arguments;o=self.o;target=d
    if case=='missing':token=None
    elif case=='foreign':o=observer()
    elif case=='copied':token=object()
    elif case=='epoch':target=str(pathlib.Path(d)/'foreign');pathlib.Path(target).mkdir()
    elif case=='task':o.task='other-task'
    elif case=='parameters':o.parameters['home']='other-home'
    elif case=='source':a['source_identity']={'sha256':'0'*64}
    elif case=='before':b['hooks']=[{'changed':True}]
    elif case=='stop':s['old_ids']=[1]
    elif case=='frontier':b['frontier']['session_id']='other'
    elif case=='after':a['observed_utc']='2026-09-09T10:05:00Z'
    elif case=='binding':ab['binding']['native_results_sha256']='0'*64
    elif case=='native':ab['native_reads'][0][0]['result']['origins']['model']['metadata']['rank']=9
    elif case=='physical':ab['physical_reads'][0][0]['content']+=b'changed'
    elif case=='selection':(pathlib.Path(d)/'after-acquisition-selection.json').write_bytes(b'changed')
    with patch.object(r,'CONFIG_TRANSITION_DIGEST','0'*64 if case=='helper' else r.CONFIG_TRANSITION_DIGEST),patch.object(o,'validate_epoch',side_effect=AssertionError('invalid handoff reached validators')):
     with self.assertRaises(r.Refusal):o.finish_initial_epoch(target,*arguments,handoff=token)
    self.assertFalse((pathlib.Path(target)/'restarted.json').exists())
    if o is self.o:self.assertNotIn('_initial_finish_handoff',o.__dict__)

 def test_start_reservation_io_failures_and_partial_bytes_are_terminal(self):
  original_open=pathlib.Path.open;original_read=pathlib.Path.read_bytes;original_sync=r.os.fsync
  for case in ('create','write','short','flush','sync','close','readback','mismatch','existing'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    self.o=observer();arguments,token=self.ready(d);marker=pathlib.Path(d)/'initial-finish-start.json'
    if case=='existing':marker.write_bytes(b'foreign marker')
    class Writer:
     def __init__(self,stream):self.stream=stream
     def __enter__(self):return self
     def __exit__(self,*args):
      self.stream.close()
      if case=='close':raise OSError('SECRET_CLOSE')
     def write(self,data):
      if case=='write':self.stream.write(data[:7]);raise OSError('SECRET_WRITE')
      if case=='short':return self.stream.write(data[:7])
      return self.stream.write(data)
     def flush(self):
      self.stream.flush()
      if case=='flush':raise OSError('SECRET_FLUSH')
     def fileno(self):return self.stream.fileno()
    def opening(path,*args,**kwargs):
     if path==marker and args and args[0]=='xb':
      if case=='create':raise OSError('SECRET_CREATE')
      return Writer(original_open(path,*args,**kwargs))
     return original_open(path,*args,**kwargs)
    def reading(path):
     if path==marker:
      if case=='readback':raise OSError('SECRET_READBACK')
      if case=='mismatch':return b'wrong readback'
     return original_read(path)
    def syncing(fd):
     if case=='sync':raise OSError('SECRET_SYNC')
     return original_sync(fd)
    with patch.object(pathlib.Path,'open',opening),patch.object(pathlib.Path,'read_bytes',reading),patch.object(r.os,'fsync',side_effect=syncing),patch.object(self.o,'validate_epoch',side_effect=AssertionError('unproved reservation reached validators')),patch.object(self.o,'write_epoch_outcome',side_effect=OSError('SECRET_OUTCOME')),patch.object(self.o,'_write_initial_failure_diagnostic',side_effect=OSError('SECRET_DIAGNOSTIC')):
     with self.assertRaises(r.Refusal) as caught:self.o.finish_initial_epoch(d,*arguments,handoff=token)
    self.assertNotIn('SECRET_',str(caught.exception));self.assertNotIn('_initial_finish_handoff',self.o.__dict__)
    if case in ('write','short'):self.assertEqual(marker.read_bytes(),b'{"autho')
    if case=='existing':self.assertEqual(marker.read_bytes(),b'foreign marker')
    self.assert_terminal_finish(self.o,d,arguments);self.assert_terminal_finish(observer(),d,arguments)

 def test_only_complete_selected_acquisition_issues_handoff(self):
  original_open=pathlib.Path.open
  for case in ('retry_then_success','exhausted','cleanup','deadline','selection','selection_short','selection_readback','context'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    self.o=observer();b,s,a,bb,ab=self.initial()
    self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
    calls={'read':0,'snapshot':0};failures=[]
    def protocol():self.o._acquisition_context['protocols'].append({'synthetic':True})
    def read():
     calls['read']+=1;protocol();rows=copy.deepcopy(ab['native_reads'][0]);files=copy.deepcopy(ab['physical_reads'][0])
     if calls['read']%2==0 and (case=='exhausted' or case=='retry_then_success' and calls['read']<=4 or case=='context' and calls['read']==2):rows[0]['result']['config']['drift']='synthetic'
     return rows,files
    def snapshot(*args,**kwargs):
     calls['snapshot']+=1
     if case!='cleanup':protocol()
     value=copy.deepcopy(a)
     if case=='context' and calls['snapshot']==2:value['owner']['pid']+=100
     return value
    original_capture=self.o.capture_epoch_boundary
    def capture(*args,**kwargs):
     try:return original_capture(*args,**kwargs)
     except r.ConfigurationInstability as failure:
      self.assertNotIn('_initial_finish_handoff',self.o.__dict__);failures.append(failure.code);raise
    def opening(path,*args,**kwargs):
     if case=='selection' and path.name=='after-acquisition-selection.json':raise OSError('synthetic selection failure')
     if case in ('selection_short','selection_readback') and path.name=='after-acquisition-selection.json' and args and args[0]=='xb':
      class ShortWriter:
       def __init__(self):self.stream=original_open(path,*args,**kwargs)
       def __enter__(self):return self
       def __exit__(self,*args):self.stream.close()
       def write(self,data):
        size=self.stream.write(data[:1]);return size if case=='selection_short' else len(data)
      return ShortWriter()
     return original_open(path,*args,**kwargs)
    with patch.object(self.o,'read_config_material',side_effect=read),patch.object(self.o,'snapshot',side_effect=snapshot),patch.object(self.o,'capture_epoch_boundary',side_effect=capture),patch.object(r.time,'sleep',return_value=None),patch.object(pathlib.Path,'open',opening):
     if case=='retry_then_success':
      actual,selected,token=self.o.acquire_restarted_boundary(d,b['frontier'],watcher_deadline=r.time.monotonic()+60,before=b,stop=s,before_acquisition=bb)
      self.assertEqual(failures,['NATIVE_PAIR_CHANGED','NATIVE_PAIR_CHANGED'])
      self.assertEqual(calls,{'read':6,'snapshot':3})
      selection=json.loads((pathlib.Path(d)/'after-acquisition-selection.json').read_bytes())
      self.assertEqual((selection['selected_attempt'],selection['max_attempts'],selection['observation_window_max_seconds'],selection['cleanup_reserve_seconds_per_probe']),(3,3,120,12))
      self.o.finish_initial_epoch(d,b,s,actual,bb,selected,handoff=token)
     else:
      deadline=r.time.monotonic()+(-1 if case=='deadline' else 60)
      with self.assertRaises((r.Refusal,OSError)):self.o.acquire_restarted_boundary(d,b['frontier'],watcher_deadline=deadline,before=b,stop=s,before_acquisition=bb)
      self.assertNotIn('_initial_finish_handoff',self.o.__dict__)
      self.assertFalse((pathlib.Path(d)/'initial-finish-start.json').exists())
      if case=='exhausted':self.assertEqual(calls,{'read':6,'snapshot':3})
      if case=='deadline':self.assertEqual(calls,{'read':0,'snapshot':0})

 def test_low_level_capture_cannot_issue_finish_handoff(self):
  fixture=EpochTests();fixture.setUp()
  try:
   _,acquisition=fixture.acquire(1,fixture.after)
   self.assertNotIn('_initial_finish_handoff',fixture.o.__dict__)
   with tempfile.TemporaryDirectory() as d,patch.object(fixture.o,'validate_epoch',side_effect=AssertionError('low-level capture authorized finish')):
    with self.assertRaises(r.Refusal):fixture.o.finish_initial_epoch(d,fixture.before,fixture.stop,fixture.after,acquisition,acquisition)
  finally:fixture.doCleanups()

 def test_frontier_wire_bytes_bind_without_raw_persistence(self):
  for mutate in (False,True):
   with self.subTest(mutate=mutate),tempfile.TemporaryDirectory() as d:
    self.o=observer();b,s,a,bb,ab=self.initial()
    wire=b'{"synthetic_native_frontier":"SECRET_WIRE"}\n'
    for observation_value in (b,a):
     observation_value['frontier'].update(session_meta_wire=wire,session_meta_sha256=r.digest(wire),suffix=b'')
    s['before_identity']=r.digest(r.canonical({**b,'frontier':r.durable(b['frontier'])}))
    self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
    try:token=selected_handoff(self.o,d,b,s,a,bb,ab)
    except TypeError:self.fail('live frontier wire bytes cannot be serialized as raw JSON')
    if mutate:
     b['frontier']['suffix']=b'changed'
     with patch.object(self.o,'validate_epoch',side_effect=AssertionError('changed frontier wire reached validators')):
      with self.assertRaises(r.Refusal):self.o.finish_initial_epoch(d,b,s,a,bb,ab,handoff=token)
    else:
     self.o.finish_initial_epoch(d,b,s,a,bb,ab,handoff=token)
     marker=(pathlib.Path(d)/'initial-finish-start.json').read_bytes()
     self.assertNotIn(b'SECRET_WIRE',marker);self.assertNotIn(b'C:/',marker)

 def test_actual_process_death_never_enables_reconstructed_finish(self):
  import os,subprocess
  launcher="import importlib.util,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location('terminal_crash_fixture',p); e=importlib.util.module_from_spec(s); sys.modules[s.name]=e; s.loader.exec_module(e); e.terminal_process_fixture(sys.argv[2],sys.argv[3])"
  checkpoints=('selected_complete','before_consume','after_consume','reserve_create','reserve_flush','reserve_sync','reserve_close','reserve_readback','before_validation','during_validation','before_restarted','after_restarted','before_outcome','after_outcome')
  for checkpoint in checkpoints:
   with self.subTest(checkpoint=checkpoint),tempfile.TemporaryDirectory() as d:
    root=pathlib.Path(d);env={**os.environ,'TMP':d,'TEMP':d,'TMPDIR':d}
    command=[sys.executable,'-I','-S','-B','-c',launcher,str(pathlib.Path(__file__).resolve())]
    first=subprocess.run(command+[checkpoint,d],cwd=root,env=env,capture_output=True,text=True,timeout=20)
    self.assertEqual(first.returncode,73,first.stdout+first.stderr)
    epoch=root/'epoch';saved={p.relative_to(epoch).as_posix():p.read_bytes() for p in epoch.rglob('*') if p.is_file()}
    second=subprocess.run(command+['resume',d],cwd=root,env=env,capture_output=True,text=True,timeout=20)
    self.assertEqual(second.returncode,0,second.stdout+second.stderr)
    self.assertEqual(second.stdout.strip(),'REFUSED_NO_LIVE_HANDOFF')
    self.assertEqual(saved,{p.relative_to(epoch).as_posix():p.read_bytes() for p in epoch.rglob('*') if p.is_file()})
    print(json.dumps({'checkpoint':checkpoint,'process_exit':first.returncode,'fresh_process_refused':True,'bytes_unchanged':True}))


def terminal_process_fixture(checkpoint,directory):
 """Authorized synthetic Python process-death fixture; never native reader CLI."""
 import base64,os
 root=pathlib.Path(directory);epoch=root/'epoch'
 def encode(value):
  if isinstance(value,bytes):return {'fixture_bytes_base64':base64.b64encode(value).decode('ascii')}
  if isinstance(value,dict):return {key:encode(item) for key,item in value.items()}
  if isinstance(value,(list,tuple)):return [encode(item) for item in value]
  return value
 def decode(value):
  if isinstance(value,dict):
   if set(value)=={'fixture_bytes_base64'}:return base64.b64decode(value['fixture_bytes_base64'],validate=True)
   return {key:decode(item) for key,item in value.items()}
  if isinstance(value,list):return [decode(item) for item in value]
  return value
 def die(stage):
  if checkpoint==stage:os._exit(73)
 if checkpoint=='resume':
  arguments=decode(json.loads((root/'retained.json').read_bytes()));o=observer()
  with patch.object(o,'validate_epoch',side_effect=AssertionError('resumed process reached validators')):
   try:o.finish_initial_epoch(epoch,*arguments)
   except r.Refusal:print('REFUSED_NO_LIVE_HANDOFF');return
  raise AssertionError('resumed process returned')
 epoch.mkdir();t=TerminalProtocolTests();t.setUp()
 try:
  arguments,token=t.ready(epoch)
  b,s,a,bb,ab=arguments
  saved=[b,s,a,{'binding':bb['binding']},{key:ab[key] for key in ('binding','native_reads','physical_reads')}]
  (root/'retained.json').write_text(json.dumps(encode(saved)),encoding='utf8')
  die('selected_complete')
  consume=t.o._consume_initial_finish_handoff;validate=t.o.validate_epoch
  write_record=t.o.write_epoch_record;write_outcome=t.o.write_epoch_outcome
  opening=pathlib.Path.open;reading=pathlib.Path.read_bytes;syncing=r.os.fsync
  def consume_at(*args):die('before_consume');value=consume(*args);die('after_consume');return value
  def validate_at(*args,**kwargs):die('before_validation');return validate(*args,**kwargs)
  def prefix_at(*args,**kwargs):die('during_validation')
  def write_record_at(*args,**kwargs):
   if args[1]=='restarted':die('before_restarted')
   value=write_record(*args,**kwargs)
   if args[1]=='restarted':die('after_restarted')
   return value
  def outcome_at(*args,**kwargs):
   die('before_outcome');value=write_outcome(*args,**kwargs);die('after_outcome');return value
  class Writer:
   def __init__(self,stream):self.stream=stream;die('reserve_create')
   def __enter__(self):return self
   def __exit__(self,*args):self.stream.close();die('reserve_close')
   def write(self,data):return self.stream.write(data)
   def flush(self):self.stream.flush();die('reserve_flush')
   def fileno(self):return self.stream.fileno()
  def open_at(path,*args,**kwargs):
   value=opening(path,*args,**kwargs)
   return Writer(value) if path.name=='initial-finish-start.json' and args and args[0]=='xb' else value
  def read_at(path):
   value=reading(path)
   if path.name=='initial-finish-start.json':die('reserve_readback')
   return value
  def sync_at(fd):value=syncing(fd);die('reserve_sync');return value
  with patch.object(t.o,'_consume_initial_finish_handoff',side_effect=consume_at),patch.object(t.o,'validate_epoch',side_effect=validate_at),patch.object(r,'verify_historical_prefix',side_effect=prefix_at),patch.object(t.o,'write_epoch_record',side_effect=write_record_at),patch.object(t.o,'write_epoch_outcome',side_effect=outcome_at),patch.object(pathlib.Path,'open',open_at),patch.object(pathlib.Path,'read_bytes',read_at),patch.object(r.os,'fsync',side_effect=sync_at):
   t.o.finish_initial_epoch(epoch,*arguments,handoff=token)
  raise AssertionError('crash checkpoint not reached')
 finally:t.doCleanups()

class CustodyTypeTests(unittest.TestCase):
 """Complete structured snapshot custody, through the real selected issuer."""
 setUp=Epoch02Tests.setUp
 materials=Epoch02Tests.materials
 initial=Epoch02Tests.initial
 diagnostic=Epoch02Tests.diagnostic
 assert_refused=Epoch02Tests.assert_refused

 def ready(self,d,*,mixed=False,expected_value=None):
  self.o=observer();arguments=self.initial();b,s,a,bb,ab=arguments
  if mixed:
   # Explicit synthetic metadata exercises the JSON writer domain recursively;
   # it is bound before selection and is not a fabricated native schema claim.
   a['owner']['custody_fixture']={'nested':{'integer':7,'real':2.0,'yes':True,'no':False,
    'one':1,'zero':0,'negative_zero':-0.0,'text':'caf\u00e9 /','nothing':None},
    'list':[{'integer':3},True,False,1,0,'last']}
  if expected_value is not None:a['owner']['custody_fixture']['nested']['real']=expected_value
  self.o.write_epoch_record(d,'before',b,bb);self.o.write_epoch_record(d,'stopped',s,None)
  handoff=selected_handoff(self.o,d,*arguments)
  return arguments,handoff

 def retained(self,d,a):
  self.o.write_epoch_record(d,'restarted-observed',a,None)
  path=pathlib.Path(d)/'restarted-observed.json'
  return path,json.loads(path.read_bytes())

 def refuse_saved(self,d,arguments,handoff,path,raw,*,predicate='ACTUAL_AFTER_DIFFERS'):
  path.write_bytes(raw);after_before=r.canonical(arguments[2]);error=None
  with patch.object(self.o,'validate_epoch',wraps=self.o.validate_epoch) as validate:
   try:self.o.finish_initial_epoch(d,*arguments,handoff=handoff)
   except r.Refusal as caught:error=caught
  # On the pinned preimage, F1 returns normally and reaches the real validator.
  self.assertIsNotNone(error,'typed custody accepted; real validator calls='+str(validate.call_count)+
   '; restarted='+str((pathlib.Path(d)/'restarted.json').exists()))
  self.assertEqual(validate.call_count,0)
  self.assertFalse((pathlib.Path(d)/'restarted.json').exists())
  self.assertEqual(path.read_bytes(),raw)
  self.assertEqual(r.canonical(arguments[2]),after_before)
  self.assertNotIn('_initial_finish_handoff',self.o.__dict__)
  self.assert_refused(d);record=self.diagnostic(d)
  self.assertEqual((record['stage'],record['predicate']),('ACTUAL_AFTER_CUSTODY',predicate))
  self.assertEqual(record['input_files']['restarted-observed.json']['sha256'],r.digest(raw))
  self.assertEqual(record['authority'],'NONE');self.assertFalse(record['currentness'])

 def accept_saved(self,d,arguments,handoff,*,path=None,raw=None):
  if path is not None:path.write_bytes(raw)
  with patch.object(self.o,'validate_epoch',wraps=self.o.validate_epoch) as validate:
   self.o.finish_initial_epoch(d,*arguments,handoff=handoff)
  self.assertEqual(validate.call_count,1)
  self.assertEqual(json.loads((pathlib.Path(d)/'epoch-outcome.json').read_bytes()),
   {'schema':'implementaudit.epoch-outcome.v1','outcome':'RELATION_EVALUATED_NO_AUTHORITY','currentness_restored':False})
  if path is not None:self.assertEqual(path.read_bytes(),raw)
  self.assertNotIn('_initial_finish_handoff',self.o.__dict__)
  self.assertFalse((pathlib.Path(d)/'initial-epoch-failure.json').exists())
  # Separate observer independently reads all three records and real relations.
  b,s,a,bb,ab=arguments
  readback=observer().read_epoch(d,raw_reads=copy.deepcopy(ab['native_reads']),physical_reads=copy.deepcopy(ab['physical_reads']))
  self.assertEqual(r.canonical(readback),r.canonical((b,s,a)))

 def test_original_201_to_201_float_refuses_before_real_validator(self):
  with tempfile.TemporaryDirectory() as d:
   args,token=self.ready(d);path,saved=self.retained(d,args[2])
   self.assertIs(type(args[2]['owner']['pid']),int);self.assertEqual(args[2]['owner']['pid'],201)
   saved['observation']['owner']['pid']=201.0
   self.refuse_saved(d,args,token,path,r.canonical(saved)+b'\n')

 def test_normal_writer_and_matching_prewritten_records_accept(self):
  for prewritten in (False,True):
   with self.subTest(prewritten=prewritten),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True)
    if prewritten:
     path,_=self.retained(d,args[2]);self.accept_saved(d,args,token,path=path,raw=path.read_bytes())
    else:self.accept_saved(d,args,token)

 def test_nested_equal_numeric_values_keep_exact_types(self):
  cases=[(('nested','integer'),7.0),(('nested','real'),2),(('nested','yes'),1),
   (('nested','no'),0),(('nested','one'),True),(('nested','zero'),False),
   (('list',0,'integer'),3.0),(('list',1),1),(('list',2),0),
   (('list',3),True),(('list',4),False)]
  for keys,value in cases:
   with self.subTest(keys=keys,value=value),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True);path,saved=self.retained(d,args[2])
    target=saved['observation']['owner']['custody_fixture']
    for key in keys[:-1]:target=target[key]
    self.assertEqual(target[keys[-1]],value);self.assertIsNot(type(target[keys[-1]]),type(value))
    target[keys[-1]]=value
    self.refuse_saved(d,args,token,path,r.canonical(saved)+b'\n')

 def test_complete_envelope_keys_nested_keys_and_list_order_refuse(self):
  cases=['extra','nested_extra','nested_missing','list_order','null_to_false']
  cases+=['missing_'+key for key in ('schema','stage','observation','config_acquisition','initial_config_transition')]
  for case in cases:
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True);path,saved=self.retained(d,args[2])
    fixture=saved['observation']['owner']['custody_fixture']
    if case=='extra':saved['extra']=None
    elif case=='nested_extra':fixture['nested']['extra']=None
    elif case=='nested_missing':del fixture['nested']['nothing']
    elif case=='list_order':fixture['list'].reverse()
    elif case=='null_to_false':saved['config_acquisition']=False
    else:del saved[case.removeprefix('missing_')]
    self.refuse_saved(d,args,token,path,r.canonical(saved)+b'\n')

 def test_equivalent_format_escapes_and_float_lexemes_accept(self):
  def reversed_keys(value):
   if isinstance(value,dict):return {key:reversed_keys(item) for key,item in reversed(list(value.items()))}
   if isinstance(value,list):return [reversed_keys(item) for item in value]
   return value
  for case in ('object_order','whitespace','unicode_and_slash_escapes','float_lexeme'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True);path,saved=self.retained(d,args[2]);original=path.read_bytes()
    if case=='object_order':raw=json.dumps(reversed_keys(saved),separators=(',',':')).encode()
    elif case=='whitespace':raw=(' \n'+json.dumps(saved,indent=3)+'\r\n\t').encode()
    elif case=='unicode_and_slash_escapes':raw=json.dumps(saved,ensure_ascii=False).replace('/',r'\/').encode('utf8')
    else:
     raw=original.replace(b'"real":2.0',b'"real":2.000e+0')
     self.assertIs(type(json.loads(raw)['observation']['owner']['custody_fixture']['nested']['real']),float)
    self.assertNotEqual(raw,original)
    self.accept_saved(d,args,token,path=path,raw=raw)

 def test_signed_zero_follows_existing_canonical_identity(self):
  for lexeme,accept in ((b'-0.00e0',True),(b'0.0',False),(b'0',False)):
   with self.subTest(lexeme=lexeme),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True);path,_=self.retained(d,args[2])
    raw=path.read_bytes().replace(b'"negative_zero":-0.0',b'"negative_zero":'+lexeme)
    if accept:self.accept_saved(d,args,token,path=path,raw=raw)
    else:self.refuse_saved(d,args,token,path,raw)
  # Integer negative zero is decoded as integer zero by the existing parser.
  with tempfile.TemporaryDirectory() as d:
   args,token=self.ready(d,mixed=True);path,_=self.retained(d,args[2])
   raw=path.read_bytes().replace(b'"zero":0',b'"zero":-0')
   self.assertNotEqual(raw,path.read_bytes());self.accept_saved(d,args,token,path=path,raw=raw)

 def test_duplicates_and_nonfinite_saved_records_refuse_before_validation(self):
  for case in ('duplicate_top','duplicate_nested','NaN','Infinity','-Infinity','1e309','-1e309'):
   with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True);path,_=self.retained(d,args[2]);raw=path.read_bytes()
    if case=='duplicate_top':raw=raw.replace(b'"stage":"restarted-observed"',b'"stage":"restarted-observed","stage":"restarted-observed"')
    elif case=='duplicate_nested':raw=raw.replace(b'"integer":7',b'"integer":7,"integer":7')
    else:raw=raw.replace(b'"real":2.0',b'"real":'+case.encode())
    self.refuse_saved(d,args,token,path,raw,predicate='UNKNOWN')

 def test_overflow_on_both_sides_and_nonfinite_expected_refuse(self):
  for expected,lexeme in ((float('inf'),b'1e309'),(float('-inf'),b'-1e309'),(float('inf'),b'2.0')):
   with self.subTest(expected=expected,lexeme=lexeme),tempfile.TemporaryDirectory() as d:
    args,token=self.ready(d,mixed=True,expected_value=expected);path,_=self.retained(d,args[2])
    literal=b'-Infinity' if expected<0 else b'Infinity'
    raw=path.read_bytes().replace(b'"real":'+literal,b'"real":'+lexeme)
    self.refuse_saved(d,args,token,path,raw,predicate='UNKNOWN')

if __name__=='__main__':unittest.main(verbosity=2)
