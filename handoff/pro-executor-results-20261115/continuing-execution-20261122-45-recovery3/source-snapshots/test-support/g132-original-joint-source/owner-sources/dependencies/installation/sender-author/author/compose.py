"""Deterministic offline assembly; no issuer, remote, native or command API.

Each phase consumes exact actual root inputs and writes a fresh directory.
Requirements are requests for separately issued bodies, never admissions.
Host and later Pro sender assemblies are distinct immutable populations.
"""
import ast,hashlib,json,os,re,stat,sys,types
from pathlib import Path
import workflow as W
BASE=Path(__file__).resolve().parent.parent
SOURCE = 'c53ed7de85de22ce313233472c8d8f02ad8e9d02'
TREE = 'd60733459425a059d961b6adc2aae9811bbb761c'
CURRENT_ACQUISITION_SCHEMA = 'dg16.current-source-maintained-package-acquisition.v5'
HISTORICAL_ACQUISITION_SCHEMA = 'dg16.current-source-unchanged-package-acquisition.v4'
ROLES={'root_admission':'COMPOSITION_ROOT_ADMISSION.json','placement_receiving':'COMPOSITION_PLACEMENT_RECEIVING.json','placement_evidence_index':'COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json','native_applicability_adoption':'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'}
RETAINED = {'SOURCE_ACQUISITION.json': {'bytes': 593285, 'sha256': '265325e29418163caeb27e13f4a66b32e1e5c0e4f3ad72cbef9bfff72a3b3bbf'}, 'PACKAGE_ROOT_RECEIVING.json': {'bytes': 928, 'sha256': '0edff0f3d8bd6f5520ef72d4e91daba54a6b0033e85b94f041f448c2951d6691'}, 'PACKAGE_BODY_RECEIVING.json': {'bytes': 9744, 'sha256': '8c592c76967ae2d95101af86ca25ab3bd4d09acdad486afbb976d61e7e5a7811'}, 'PACKAGE_TERMINAL_RECEIVING.json': {'bytes': 4531, 'sha256': 'e213b8843f03741c48776277f9e1db8c78ea1d3f7609875ce32bcd94e5ed5b89'}}
PLACEMENT={'placement/ACCESS09_DIAGNOSTIC.json':{'bytes':29107,'sha256':'5a56b0705e77314c587020dda0d45522a68bf5c93d4187281971b13cea4f95ae'},'placement/ACCESS09_FINAL.json':{'bytes':5113,'sha256':'61d6afe0d5cb5bca26c435c4529788816161d484714ec3e89148d24186b945c1'},'placement/ACCESS09_ROOT_RECEIVING.json':{'bytes':1961,'sha256':'40ce62326d8e9b759a5db150bf41a99dc77c05580342989aa33e06df2b0bedd3'}}
HOST_WRAPPERS=('host_tool_observe_entry.py','host_tool_adopt_entry.py','host_request_entry.py','host_receive_entry.py','core_prepare_entry.py')
def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def parse(b):
 def pairs(rows):
  v={}
  for k,x in rows:need(k not in v,'DUPLICATE_KEY');v[k]=x
  return v
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
def read(p,limit=64*1024**2):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<=s.st_size<=limit,'INPUT_FILE_SHAPE')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_size,x.st_mtime_ns,x.st_ctime_ns,x.st_nlink)
 try:
  need(mark(os.fstat(fd))==mark(s),'INPUT_OPEN_CHANGED');b=os.pread(fd,limit+1,0)
  need(len(b)==s.st_size and mark(os.fstat(fd))==mark(s) and mark(p.lstat())==mark(s),'INPUT_CLOSING_CHANGED');return b
 finally:os.close(fd)
def population(root):
 root=Path(root);need(root.is_dir() and root.resolve()==root.absolute(),'INPUT_DIRECTORY_ALIAS');out={}
 for p in sorted(root.rglob('*')):
  need(not p.is_symlink(),'INPUT_ALIAS');s=p.lstat()
  if stat.S_ISDIR(s.st_mode):continue
  out[p.relative_to(root).as_posix()]=read(p)
 return out
def assignments(raw,values):
 text=raw.decode();tree=ast.parse(text);lines=text.splitlines(keepends=True);edits=[]
 for name,value in values.items():
  hits=[n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
  need(len(hits)==1,'UNIQUE_BINDING_'+name);n=hits[0];edits.append((n.lineno-1,n.end_lineno,name+' = '+repr(value)+'\n'))
 for start,end,repl in sorted(edits,reverse=True):lines[start:end]=[repl]
 result=''.join(lines).encode();compile(result,'<composed>','exec');return result
def literal(raw,name):
 t=ast.parse(raw);hits=[n.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets)]
 need(len(hits)==1,'BINDING_LITERAL');return ast.literal_eval(hits[0])
def tuple_assignment(raw,names,values):
 text=raw.decode();tree=ast.parse(text);lines=text.splitlines(keepends=True)
 hits=[n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Tuple)
       and all(isinstance(x,ast.Name) for x in n.targets[0].elts) and [x.id for x in n.targets[0].elts]==list(names)]
 need(len(hits)==1 and len(names)==len(values),'EXACT_G3_SOURCE_COUNT_BINDING');node=hits[0]
 lines[node.lineno-1:node.end_lineno]=[', '.join(names)+' = '+', '.join(repr(x) for x in values)+'\n']
 result=''.join(lines).encode();compile(result,'<composed-tuple>','exec');return result
def publication_subject(acquired,manifest_raw):
 version=acquired.get('schema');need(version in (CURRENT_ACQUISITION_SCHEMA,HISTORICAL_ACQUISITION_SCHEMA),'ACQUISITION_VERSION_REQUIRED')
 published=parse(acquired['evidence_bodies']['PRODUCT_PUBLICATION_RECEIVING.json'].encode('utf8'))
 manifest=parse(manifest_raw)
 if version==CURRENT_ACQUISITION_SCHEMA:
  need(type(published) is dict and 'subject' in published and not any(k in published for k in ('commit','tree','branch')),'V5_NESTED_PUBLICATION_SUBJECT_REQUIRED')
  subject=published['subject']
  need(type(subject) is dict and set(subject)=={'commit','tree','parent_commit','parent_tree','branch','files','bytes','manifest'},'V5_PUBLICATION_SUBJECT_FIELDS')
  need(subject['parent_commit']==manifest['parent_commit'] and subject['parent_tree']==manifest['parent_tree']
       and type(subject['files']) is int and subject['files']==manifest['file_count']
       and type(subject['bytes']) is int and subject['bytes']==manifest['total_bytes']
       and subject['manifest']==desc(manifest_raw),'V5_PUBLICATION_MANIFEST_JOIN')
 else:
  need(type(published) is dict and 'subject' not in published,'V4_FLAT_PUBLICATION_SUBJECT_REQUIRED')
  subject={k:published[k] for k in ('commit','tree','branch')}
 need(subject['commit']==SOURCE==manifest['commit'] and subject['tree']==TREE==manifest['tree']
      and type(subject.get('branch')) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9._/-]{0,120}',subject['branch'])
      and '..' not in subject['branch'] and '//' not in subject['branch'],'ACTUAL_SELECTED_PRODUCT_BRANCH_REQUIRED')
 return subject
def current_acquisition_pin(core,raw):
 """Bind fresh input bytes to the actual current scope; retained history is immutable."""
 acquired=parse(raw);need(acquired.get('schema')==CURRENT_ACQUISITION_SCHEMA,'CURRENT_V5_ACQUISITION_REQUIRED')
 scope_raw=core.get('ORIGINAL_SCOPE.json');need(type(scope_raw) is bytes,'CURRENT_ACQUISITION_SCOPE_REQUIRED')
 scope=parse(scope_raw)
 need(scope.get('schema')=='dg16.g3-retained-original-population.v3'
      and scope.get('current_subject')==dict(commit=SOURCE,tree=TREE)
      and scope.get('original_population')==dict(DG16=48,DG17=95,DG18=14,total=157)
      and type(scope.get('received_inputs')) is dict and set(scope['received_inputs'])==set(RETAINED),
      'CURRENT_ACQUISITION_SCOPE_REQUIRED')
 need(literal(core['g3_receiving.py'],'SCOPE_SHA')==sha(scope_raw),'CURRENT_ACQUISITION_SCOPE_PIN')
 expected=scope['received_inputs']['SOURCE_ACQUISITION.json']
 need(type(expected) is dict and set(expected)=={'bytes','sha256'} and desc(raw)==expected,'CURRENT_ACQUISITION_BODY_PIN')
 need(acquired.get('commit')==SOURCE and acquired.get('tree')==TREE
      and acquired.get('manifest_sha256')==scope.get('source_inventory_sha256')==sha(core['SOURCE_MANIFEST.json']),
      'CURRENT_ACQUISITION_SUBJECT_JOIN')
 return expected
def bind_g3_subject(raw,manifest,version,source_branch):
 if version==CURRENT_ACQUISITION_SCHEMA:
  names=('MAINTAINED_SOURCE_COMMIT','MAINTAINED_SOURCE_TREE','MAINTAINED_SOURCE_PARENT')
  values=(manifest['commit'],manifest['tree'],manifest['parent_commit'])
  result=assignments(raw,dict(zip(names,values),MAINTAINED_PARENT_TREE=manifest['parent_tree'],MAINTAINED_BRANCH=source_branch))
  return tuple_assignment(result,('MAINTAINED_SOURCE_FILES','MAINTAINED_SOURCE_BYTES'),(manifest['file_count'],manifest['total_bytes']))
 need(version==HISTORICAL_ACQUISITION_SCHEMA,'ACQUISITION_VERSION_REQUIRED')
 result=assignments(raw,dict(SOURCE_COMMIT=manifest['commit'],SOURCE_TREE=manifest['tree'],SOURCE_PARENT=manifest['parent_commit']))
 return tuple_assignment(result,('SOURCE_FILES','SOURCE_BYTES'),(manifest['file_count'],manifest['total_bytes']))
def bind_package_rows(raw,acquired):
 root_package=parse(acquired['evidence_bodies']['ROOT_PACKAGE_SOURCE_APPLICABILITY.json'].encode('utf8'))
 if acquired.get('schema')==CURRENT_ACQUISITION_SCHEMA:
  for field,count,pin_name in (('changes_vs_m5',16,'M5_TO_MAINTAINED_SHA256'),('changes_vs_e76',14,'E76_TO_MAINTAINED_SHA256')):
   rows=root_package.get(field)
   need(type(rows) is list and len(rows)==count and all(type(r) is dict and set(r)=={'path','before','after'} for r in rows)
        and len({r['path'] for r in rows})==count and sha(encode(rows))==literal(raw,pin_name),'EXACT_MAINTAINED_SOURCE_ROWS_REQUIRED')
  # These are v4 historical package preimages, not the v5 current delta.
  need(len(literal(raw,'PRIOR_PACKAGE_SOURCE_ROWS'))==2 and literal(raw,'PRIOR_PACKAGE_ADDED_SOURCE_PATHS')=={},'HISTORICAL_PACKAGE_PREIMAGES_REQUIRED')
  return raw
 need(acquired.get('schema')==HISTORICAL_ACQUISITION_SCHEMA,'ACQUISITION_VERSION_REQUIRED')
 cumulative=root_package['actual_source_changes_vs_observed_package']
 need(type(cumulative) is list and len({r['path'] for r in cumulative})==len(cumulative),'EXACT_CUMULATIVE_SOURCE_ROWS_REQUIRED')
 return assignments(raw,dict(PRIOR_PACKAGE_SOURCE_ROWS={r['path']:r['before'] for r in cumulative if r['before'] is not None},
                            PRIOR_PACKAGE_ADDED_SOURCE_PATHS={r['path']:r['after'] for r in cumulative if r['before'] is None}))
def bind_native_sources(core,manifest,retained,changed):
 """Support exactly the historical template or its already-derived owner form."""
 native=core['native_prerequisite.py'];old=b"closure.get('file_count') == 1759 and closure.get('total_bytes') == 166407881"
 bound=b"closure.get('file_count') == SOURCE_FILES and closure.get('total_bytes') == SOURCE_BYTES"
 if native.count(old)==1 and native.count(bound)==0:
  need(not any(isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('SOURCE_FILES','SOURCE_BYTES') for x in n.targets) for n in ast.parse(native).body),'NATIVE_COUNT_BINDING_ALREADY_PRESENT')
  native=b'SOURCE_FILES = '+repr(manifest['file_count']).encode()+b'\nSOURCE_BYTES = '+repr(manifest['total_bytes']).encode()+b'\n'+native.replace(old,bound)
 else:
  need(native.count(old)==0 and native.count(bound)==1,'EXACT_NATIVE_CLOSURE_BINDING')
  native=assignments(native,dict(SOURCE_FILES=manifest['file_count'],SOURCE_BYTES=manifest['total_bytes']))
 run=core['run.py'];old=b'retained_native_members=87,changed_native_members=2';bound=b'retained_native_members=NATIVE_RETAINED_MEMBERS,changed_native_members=NATIVE_CHANGED_MEMBERS'
 if run.count(old)==1 and run.count(bound)==0:
  need(not any(isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('NATIVE_RETAINED_MEMBERS','NATIVE_CHANGED_MEMBERS') for x in n.targets) for n in ast.parse(run).body),'NATIVE_PROJECTION_BINDING_ALREADY_PRESENT')
  run=b'NATIVE_RETAINED_MEMBERS = '+repr(retained).encode()+b'\nNATIVE_CHANGED_MEMBERS = '+repr(changed).encode()+b'\n'+run.replace(old,bound)
 else:
  need(run.count(old)==0 and run.count(bound)==1,'EXACT_NATIVE_PROJECTION_BINDING')
  run=assignments(run,dict(NATIVE_RETAINED_MEMBERS=retained,NATIVE_CHANGED_MEMBERS=changed))
 core['native_prerequisite.py']=native;core['run.py']=run
 return core
def tuple_literal(raw,names):
 hits=[n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Tuple)
       and all(isinstance(x,ast.Name) for x in n.targets[0].elts) and [x.id for x in n.targets[0].elts]==list(names)]
 need(len(hits)==1,'UNIQUE_TUPLE_LITERAL');values=ast.literal_eval(hits[0])
 need(type(values) is tuple and len(values)==len(names),'EXACT_TUPLE_LITERAL');return values
def source_only_peer_bindings(core):
 """Derive byte/source constants only. Actual scope/admission bodies stay unchanged.

 This is not prepare, core admission, currentness or a ready hosted composition.
 The outer source-generation owner must retain the unresolved operational joins.
 """
 core=dict(core);g3=core['g3_receiving.py']
 source=literal(g3,'MAINTAINED_SOURCE_COMMIT');tree=literal(g3,'MAINTAINED_SOURCE_TREE')
 need((source,tree)==(SOURCE,TREE),'SOURCE_ONLY_SELECTED_OWNER_JOIN')
 files,total=tuple_literal(g3,('MAINTAINED_SOURCE_FILES','MAINTAINED_SOURCE_BYTES'))
 need(type(files) is int and type(total) is int and files>0 and total>0,'SOURCE_ONLY_SELECTED_COUNTS')
 facts=dict(file_count=files,total_bytes=total)
 core=bind_native_sources(core,facts,literal(core['run.py'],'NATIVE_RETAINED_MEMBERS'),literal(core['run.py'],'NATIVE_CHANGED_MEMBERS'))
 core['root_placement.py']=assignments(core['root_placement.py'],dict(SOURCE=source,TREE=tree))
 for module in ('host_utility.py','host_composition.py','natural_inputs.py','native_probe.py','native_prerequisite.py'):
  core[module]=assignments(core[module],dict(SOURCE_COMMIT=source,SOURCE_TREE=tree))
 core['native_probe.py']=assignments(core['native_probe.py'],dict(IO_SHA256=sha(core['evidence_io.py'])))
 core['native_prerequisite.py']=assignments(core['native_prerequisite.py'],dict(PROBE_SHA256=sha(core['native_probe.py'])))
 core['input_setup.py']=assignments(core['input_setup.py'],dict(UTILITY_SHA256=sha(core['host_utility.py'])))
 for module in ('g3_receiving.py','proof_consumer.py'):
  core[module]=assignments(core[module],dict(SCOPE_SHA=sha(core['ORIGINAL_SCOPE.json']),ADVERSE_SHA=sha(core['ADVERSE_APPLICABILITY.json'])))
 # This data file is generated by core_bind, not an extra author template.
 pins=parse(core['INDEPENDENT_PROOF_PINS.json']) if 'INDEPENDENT_PROOF_PINS.json' in core else dict(
      schema='dg16.independent-consumer-pins.v1',compiler_sha256=literal(core['g3_receiving.py'],'COMPILER_SHA'),
      owner_sha256=literal(core['proof_consumer.py'],'OWNER_SHA'))
 need(pins.get('schema')=='dg16.independent-consumer-pins.v1','SOURCE_ONLY_PROOF_PIN_SCHEMA')
 pins.update(source_commit=source,source_tree=tree,scope_sha256=sha(core['ORIGINAL_SCOPE.json']),
             adverse_sha256=sha(core['ADVERSE_APPLICABILITY.json']),scope_module_sha256=sha(core['g3_receiving.py']),
             consumer_sha256=sha(core['proof_consumer.py']),initial_control_branch=literal(core['g3_receiving.py'],'CONTROL_BRANCH'))
 core['INDEPENDENT_PROOF_PINS.json']=encode(pins)
 modules=literal(core['run.py'],'MODULE_PINS');data=literal(core['run.py'],'G3_DATA_PINS')
 need(all(n+'.py' in core for n in modules) and all(n in core for n in data),'SOURCE_ONLY_COMPLETE_PEER_BODIES')
 core['run.py']=assignments(core['run.py'],dict(MODULE_PINS={n:sha(core[n+'.py']) for n in modules},
                 G3_DATA_PINS={n:sha(core[n]) for n in data},MANIFEST_SHA=sha(core['SOURCE_MANIFEST.json']),
                 PROVIDER_SETUP_SHA=sha(core['PROVIDER_SETUP.json'])))
 return core
def templates():
 data=population(BASE/'templates');index=parse(read(BASE/'inputs/TEMPLATE_INDEX.json'))
 need({n:desc(b) for n,b in data.items()}==index,'TEMPLATE_POPULATION_CHANGED');return data
def branch(v):need(type(v) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',v) and '..' not in v and '//' not in v,'BRANCH')
def selection(v):
 need(type(v) is dict and set(v)=={'branch','g3_control_branch','cipher_control_branch','cipher_control_parent','host_tools','root_tools','carrier_limits','job_timeout_minutes','workflow_overhead_seconds'},'SELECTION_FIELDS')
 W.validate(v)
 for k in ('branch','g3_control_branch','cipher_control_branch'):branch(v[k])
 h=v['host_tools'];need(type(h) is dict and set(h)=={'profile','paths','control_branch','control_parent','observation_seconds','adoption_seconds'},'HOST_DECLARATION')
 need(h['profile']=='DEFERRED_SAME_HOST_FIXED_TOOLS_V1' and h['paths']=={'env':'/usr/bin/env','openssl':'/usr/bin/openssl'},'HOST_PATHS');branch(h['control_branch'])
 need(len({v['branch'],v['g3_control_branch'],v['cipher_control_branch'],h['control_branch']})==4,'DISTINCT_CONTROL_REFS')
 for x in (v['cipher_control_parent'],h['control_parent']):need(type(x) is str and re.fullmatch('[0-9a-f]{40}',x),'CONTROL_PARENT')
 need(v['cipher_control_parent']!=h['control_parent'],'SEPARATE_TOOL_CONTROL_PARENT')
 need(set(v['carrier_limits'])=={'acquisition_seconds','command_seconds','command_cpu_seconds','poll_seconds'} and 4<=v['carrier_limits']['command_seconds']<=v['carrier_limits']['acquisition_seconds'],'CARRIER_TIME_RELATION')
 need(type(v['root_tools']) is dict and set(v['root_tools'])=={'env','openssl'},'ROOT_TOOLS_REQUIRED')
 for row in v['root_tools'].values():need(type(row) is dict and set(row)=={'bytes','sha256'} and type(row['bytes']) is int and 0<row['bytes']<=32*1024**2 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']),'ROOT_TOOL_DESCRIPTOR')
 return v

def role_check(s,private,core):
 need(set(private)==set(RETAINED)|set(ROLES.values())|set(PLACEMENT),'EXACT_EIGHT_ROLES_THREE_PLACEMENT_MEMBERS')
 acquired=parse(private['SOURCE_ACQUISITION.json']);expected=dict(RETAINED)
 if acquired.get('schema')==CURRENT_ACQUISITION_SCHEMA:
  expected['SOURCE_ACQUISITION.json']=current_acquisition_pin(core,private['SOURCE_ACQUISITION.json'])
 else:need(acquired.get('schema')==HISTORICAL_ACQUISITION_SCHEMA,'ACQUISITION_VERSION_REQUIRED')
 for name,row in (expected|PLACEMENT).items():need(desc(private[name])==row,'EXACT_RETAINED_BODY_'+name)
 v={r:parse(private[n]) for r,n in ROLES.items()};comp=parse(core['HOST_COMPOSITION.json'])
 expected=dict(schema='dg16.current-core-host-root-admission.v1',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],run_attempt=1,automatic_retry=False,original_awards=[],prospective_operation='ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE',component_scope='CORE_G1_Q06_NATURAL_L04_SEPARATE',input_sha256={r:sha(private[n]) for r,n in ROLES.items() if r!='root_admission'})
 need(v['root_admission']==expected,'ACTUAL_CORE_ADMISSION_REQUIRED')
 a=v['native_applicability_adoption'];need(a.get('schema')=='dg16.current-native-applicability-root-adoption.v1' and a.get('successor')=='PRO-EXECUTOR-01, designated by owner' and a.get('source_commit')==SOURCE and a.get('source_tree')==TREE and a.get('applicability_sha256')==sha(core['NATIVE_SOURCE_APPLICABILITY.json']) and type(a.get('unchanged_members')) is int and a['unchanged_members']==86 and type(a.get('changed_members')) is int and a['changed_members']==3 and a.get('windows_qualification')=='DG18_SEPARATE' and a.get('original_awards')==[],'ACTUAL_NATIVE_ADOPTION_REQUIRED')
 scope='ACCESS09_RUN42311009492_A1_JOB128212159527_I0_ONLY'
 need(v['placement_evidence_index']==dict(schema='dg16.received-placement-evidence-index.v1',scope=scope,members=PLACEMENT),'EXACT_PLACEMENT_INDEX')
 need(v['placement_receiving']==dict(schema='dg16.actual-working-root-placement-receiving.v1',successor='PRO-EXECUTOR-01, designated by owner',source_commit=SOURCE,source_tree=TREE,observed_source_commit='3e0f4b6d05eb086017ce721d40459fdbd68714dd',placement=comp['placement'],status='ACTUAL_ROOT_ISLAND_FD_ROUTE_RECEIVED_AT_DIAGNOSTIC_SCOPE',cause='UNPROVED',original_awards=[],evidence_scope=scope,evidence_index_sha256=sha(private[ROLES['placement_evidence_index']]),source_applicability_sha256=sha(private[ROLES['native_applicability_adoption']]),native_transfer='NONE_FRESH_NATIVE_BANK_AND_ORIGINAL_PAIR_REQUIRED'),'ACTUAL_PLACEMENT_RECEIVING_REQUIRED')
 # Booleans must not substitute for the exact integer attempt in an admission.
 need(type(v['root_admission']['run_attempt']) is int,'ADMISSION_ATTEMPT_TYPE')
 return {n:desc(b) for n,b in private.items()}

def core_bind(core,s,index,*,acquisition_schema=None):
 manifest=parse(core['SOURCE_MANIFEST.json'])
 applicability=parse(core['NATIVE_SOURCE_APPLICABILITY.json'])
 need(applicability['source_commit']==SOURCE and applicability['source_tree']==TREE,'CORE_NATIVE_APPLICABILITY_SELECTED_SUBJECT')
 native_rows=applicability['members']
 need(len(native_rows)==89 and len({r['path'] for r in native_rows})==89,'CORE_NATIVE_APPLICABILITY_POPULATION')
 retained=sum(r['retained_unchanged'] is True for r in native_rows)
 changed=sum(r['retained_unchanged'] is False for r in native_rows)
 need(retained==applicability['unchanged_count'] and changed==applicability['changed_count'] and retained+changed==89,'CORE_NATIVE_APPLICABILITY_COUNTS')
 core=bind_native_sources(core,manifest,retained,changed)
 need(manifest['commit']==SOURCE and manifest['tree']==TREE,'CORE_MANIFEST_SELECTED_SUBJECT')
 # Bind semantic peer guards before module/workflow/packet hashes. Source and
 # historical evidence identity are distinct; only actual selected bodies bind.
 subject=dict(SOURCE_COMMIT=manifest['commit'],SOURCE_TREE=manifest['tree'],SOURCE_PARENT=manifest['parent_commit'],SOURCE_FILES=manifest['file_count'],SOURCE_BYTES=manifest['total_bytes'])
 # All four are current consumers, not retained evidence identities. Bind
 # before utility, composition, module, carrier and external-entry peer pins.
 core['root_placement.py']=assignments(core['root_placement.py'],dict(SOURCE=manifest['commit'],TREE=manifest['tree']))
 for module in ('host_utility.py','host_composition.py','natural_inputs.py'):
  core[module]=assignments(core[module],dict(SOURCE_COMMIT=manifest['commit'],SOURCE_TREE=manifest['tree']))
 core['g3_receiving.py']=bind_g3_subject(core['g3_receiving.py'],manifest,acquisition_schema,literal(core['run.py'],'SOURCE_BRANCH'))
 core['native_probe.py']=assignments(core['native_probe.py'],{'SOURCE_COMMIT':manifest['commit'],'SOURCE_TREE':manifest['tree'],'IO_SHA256':sha(core['evidence_io.py'])})
 core['native_prerequisite.py']=assignments(core['native_prerequisite.py'],{'SOURCE_COMMIT':manifest['commit'],'SOURCE_TREE':manifest['tree'],'PROBE_SHA256':sha(core['native_probe.py'])})
 core['input_setup.py']=assignments(core['input_setup.py'],{'UTILITY_SHA256':sha(core['host_utility.py'])})
 rows={r['path']:r for r in manifest['members']}
 setup=literal(core['run.py'],'SETUP')
 core['run.py']=assignments(core['run.py'],dict(subject,MANIFEST_SHA=sha(core['SOURCE_MANIFEST.json']),SETUP_SHA=rows[setup]['sha256'],PROVIDER_SETUP_SHA=sha(core['PROVIDER_SETUP.json'])))
 comp=parse(core['HOST_COMPOSITION.json']);comp.update(state='REVIEWED_EXACT_COMPOSITION',workflow_branch=s['branch'],source_commit=manifest['commit'],source_tree=manifest['tree'])
 for role,name in ROLES.items():comp[role]=dict(path='private-inputs/'+name,**index[name])
 core['HOST_COMPOSITION.json']=encode(comp)
 core['host_composition.py']=assignments(core['host_composition.py'],{'BINDING_SHA256':sha(core['HOST_COMPOSITION.json'])})
 core['g3_receiving.py']=assignments(core['g3_receiving.py'],{'JOB_BRANCH':s['branch'],'CONTROL_BRANCH':s['g3_control_branch']})
 # Consume the actual operation-owned selected-loader bindings before peer pins.
 selected_operation=core['operation.py']
 executing=literal(selected_operation,'EXECUTING_SOURCE_BINDINGS')
 entry=literal(selected_operation,'C5_ENTRYPOINT')
 revision=literal(selected_operation,'C5_SOURCE_REVISION')
 need(type(executing) is dict and len(executing)==13 and entry=='GenuineC5Session'
      and revision==literal(selected_operation,'REVISION'),'ACTUAL_OPERATION_EXECUTION_BINDINGS_REQUIRED')
 need(literal(selected_operation,'SOURCE_TREE')==manifest['tree'] and
      literal(selected_operation,'LOADER_SHA256')==rows['scripts/load-work-graph-c5-executor.py']['sha256'],
      'ACTUAL_OPERATION_SELECTED_SOURCE_REQUIRED')
 core['g3_receiving.py']=assignments(core['g3_receiving.py'],dict(C5_ENTRYPOINT=entry,C5_SOURCE_REVISION=revision,EXECUTING_SOURCE_BINDINGS=executing))
 core['proof_consumer.py']=assignments(core['proof_consumer.py'],dict(C5_ENTRYPOINT=entry,C5_SOURCE_REVISION=revision,EXECUTING_SOURCE_PINS=executing,
   SOURCE=manifest['commit'],TREE=manifest['tree'],SOURCE_PARENT=manifest['parent_commit'],
   SOURCE_FILES=manifest['file_count'],SOURCE_BYTES=manifest['total_bytes']))
 # Bind AFTER g3 branch rewriting and BEFORE run/manifest/bootstrap closure.
 core['g3_receiving.py']=assignments(core['g3_receiving.py'],{'SCOPE_SHA':sha(core['ORIGINAL_SCOPE.json']),'ADVERSE_SHA':sha(core['ADVERSE_APPLICABILITY.json'])})
 core['proof_consumer.py']=assignments(core['proof_consumer.py'],{'SCOPE_SHA':sha(core['ORIGINAL_SCOPE.json']),'ADVERSE_SHA':sha(core['ADVERSE_APPLICABILITY.json'])})
 core['INDEPENDENT_PROOF_PINS.json']=encode(dict(schema='dg16.independent-consumer-pins.v1',source_commit=SOURCE,source_tree=TREE,
  scope_sha256=sha(core['ORIGINAL_SCOPE.json']),adverse_sha256=sha(core['ADVERSE_APPLICABILITY.json']),
  compiler_sha256='0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d',
  owner_sha256='9bce5c887cd89c2d2991b84f1bf765787e7a6b75a2eba29a8433c3a6c05f73a3',
  scope_module_sha256=sha(core['g3_receiving.py']),consumer_sha256=sha(core['proof_consumer.py']),initial_control_branch=s['g3_control_branch']))
 pins=literal(core['run.py'],'MODULE_PINS');data=literal(core['run.py'],'G3_DATA_PINS')
 pins['proof_consumer']=sha(core['proof_consumer.py']);data['INDEPENDENT_PROOF_PINS.json']=sha(core['INDEPENDENT_PROOF_PINS.json'])
 core['run.py']=assignments(core['run.py'],{'BRANCH':s['branch'],'MODULE_PINS':{n:sha(core[n+'.py']) for n in pins},'G3_DATA_PINS':{n:sha(core[n]) for n in data}})
 # Fixed current-consumer joins are checked after final peer pin closure.
 g3_keys=('MAINTAINED_SOURCE_COMMIT','MAINTAINED_SOURCE_TREE') if acquisition_schema==CURRENT_ACQUISITION_SCHEMA else ('SOURCE_COMMIT','SOURCE_TREE')
 for module,commit_key,tree_key in (('root_placement.py','SOURCE','TREE'),('host_utility.py','SOURCE_COMMIT','SOURCE_TREE'),('host_composition.py','SOURCE_COMMIT','SOURCE_TREE'),('natural_inputs.py','SOURCE_COMMIT','SOURCE_TREE'),('run.py','SOURCE_COMMIT','SOURCE_TREE'),('g3_receiving.py',*g3_keys),('proof_consumer.py','SOURCE','TREE'),('native_probe.py','SOURCE_COMMIT','SOURCE_TREE'),('native_prerequisite.py','SOURCE_COMMIT','SOURCE_TREE')):
  need((literal(core[module],commit_key),literal(core[module],tree_key))==(manifest['commit'],manifest['tree']),'CORE_CURRENT_SOURCE_SUBJECT_JOIN')
 need((parse(core['HOST_COMPOSITION.json'])['source_commit'],parse(core['HOST_COMPOSITION.json'])['source_tree'])==(manifest['commit'],manifest['tree']),'CORE_CURRENT_COMPOSITION_SUBJECT_JOIN')
 return core

def request(stage,expected):return encode(dict(schema='dg16.offline-composition-body-requirements.v1',stage=stage,authority='NONE',actual_admission=False,expected_body=expected,original_awards=[]))
def prepare(s,private):
 s=selection(s);t=templates();core={n[5:]:b for n,b in t.items() if n.startswith('core/')}
 acquired=parse(private['SOURCE_ACQUISITION.json'])
 need(acquired.get('schema')==CURRENT_ACQUISITION_SCHEMA,'CURRENT_V5_ACQUISITION_REQUIRED')
 index=role_check(s,private,core)
 published=publication_subject(acquired,core['SOURCE_MANIFEST.json'])
 core['run.py']=assignments(core['run.py'],dict(SOURCE_BRANCH=published['branch']))
 core['g3_receiving.py']=bind_package_rows(core['g3_receiving.py'],acquired)
 core=core_bind(core,s,index,acquisition_schema=acquired['schema'])
 # Exercise the actual source/package consumer before any hosted composition.
 # It reads only already received bodies and the exact selected manifest.
 package_gate=types.ModuleType('actual_offline_g3_package_gate')
 package_gate.__file__=str(BASE/'templates/core/g3_receiving.py')
 exec(compile(core['g3_receiving.py'],package_gate.__file__,'exec'),package_gate.__dict__)
 basis=parse(core['ORIGINAL_SCOPE.json'])
 need(acquired['schema']==CURRENT_ACQUISITION_SCHEMA and basis['current_subject']==dict(commit=SOURCE,tree=TREE),'CURRENT_V5_ASSEMBLED_SCOPE_REQUIRED')
 need(package_gate.receive_retained_package_relation(acquired,basis,
      {n:private[n] for n in package_gate.SCOPE_INPUT_NAMES})==acquired['package_relation'],'ACTUAL_ASSEMBLED_SOURCE_PACKAGE_CONSUMER_REQUIRED')
 flow=W.render(s);out={'tree/'+W.WORKFLOW:flow,'SELECTION.json':encode(s),'INPUT_INDEX.json':encode(index)}
 out.update({'tree/'+W.CORE+'/'+n:b for n,b in core.items()})
 expected=dict(schema='dg16.core-private-carrier-root-admission.v2',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',operation='ONE_FIXED_TOOL_BOOTSTRAP_ONE_FRESH_RECIPIENT_ONE_PRIVATE_TRANSFER',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],workflow_path=W.WORKFLOW,workflow_sha256=sha(flow),control_branch=s['cipher_control_branch'],control_parent=s['cipher_control_parent'],input_index_sha256=sha(encode(index)),limits=s['carrier_limits'],host_tool_bootstrap=s['host_tools'],run_attempt=1,automatic_retry=False,core_or_native_effect_grant=False,original_awards=[])
 out['CARRIER_ADMISSION_REQUIREMENTS.json']=request('ACTUAL_ROOT_CARRIER_ADMISSION',expected)
 return out

def loader_bind(carrier):
 pins=literal(carrier['carrier_loader.py'],'MODULE_PINS');carrier['carrier_loader.py']=assignments(carrier['carrier_loader.py'],{'MODULE_PINS':{n:desc(carrier[n+'.py']) for n in pins}})
 return carrier

def bind_carrier(prior,admission_raw):
 expected=parse(prior['CARRIER_ADMISSION_REQUIREMENTS.json'])['expected_body'];need(parse(admission_raw)==expected and encode(expected)==admission_raw,'ACTUAL_CARRIER_ADMISSION_MISMATCH')
 s=selection(parse(prior['SELECTION.json']));t=templates();carrier={n[len('adapter/src/'):]:b for n,b in t.items() if n.startswith('adapter/src/')}
 core={n[len('tree/'+W.CORE+'/'):]:b for n,b in prior.items() if n.startswith('tree/'+W.CORE+'/')}
 binding=parse(carrier['CARRIER_COMPOSITION.json']);binding.update(state='REVIEWED_EXACT_CARRIER_COMPOSITION',source_commit=SOURCE,source_tree=TREE,branch=s['branch'],workflow_path=W.WORKFLOW,workflow_sha256=sha(prior['tree/'+W.WORKFLOW]),job_name='qualify',control_branch=s['cipher_control_branch'],control_parent=s['cipher_control_parent'],core_bodies={n:desc(core[n]) for n in ('HOST_COMPOSITION.json','NATIVE_SOURCE_APPLICABILITY.json','host_composition.py','host_utility.py','run.py')},input_index=desc(prior['INPUT_INDEX.json']),carrier_admission=desc(admission_raw),placement_body=dict(path='root_placement.py',**desc(core['root_placement.py'])),host_tools=s['host_tools'],root_tools=s['root_tools'],limits=s['carrier_limits'])
 carrier['CARRIER_COMPOSITION.json']=encode(binding);carrier['INPUT_INDEX.json']=prior['INPUT_INDEX.json'];carrier['CARRIER_ADMISSION.json']=admission_raw
 carrier['carrier_policy.py']=assignments(carrier['carrier_policy.py'],{'SOURCE_COMMIT':SOURCE,'SOURCE_TREE':TREE,'BINDING_SHA256':sha(carrier['CARRIER_COMPOSITION.json']),'RETAINED':RETAINED})
 carrier['carrier.py']=assignments(carrier['carrier.py'],{'CAPTURE_OWNER_SHA256':sha(core['host_utility.py'])})
 # The host cannot select an operation/admission for a future recipient. This
 # immutable unresolved sender is deliberately incapable of a Pro encryption.
 sender=parse(carrier['PRO_SENDER_COMPOSITION.json']);need(sender['operation'] is None and sender['admission'] is None and sender['state']=='UNRESOLVED_PRO_SENDER_COMPONENT','HOST_SENDER_MUST_BE_UNRESOLVED')
 sender.update(source_commit=SOURCE,source_tree=TREE);carrier['PRO_SENDER_COMPOSITION.json']=encode(sender)
 carrier['sender_policy.py']=assignments(carrier['sender_policy.py'],{'BINDING_SHA256':sha(carrier['PRO_SENDER_COMPOSITION.json'])})
 loader_bind(carrier)
 out=dict(prior);out.update({'tree/'+W.CORE+'/carrier/'+n:b for n,b in carrier.items()})
 members={n:dict(**desc(b),mode=0o400) for n,b in (core|{'carrier/'+n:b for n,b in carrier.items()}).items()}
 manifest=encode(dict(schema='dg16.fixed-root-public-manifest.v1',members=members));out['PUBLIC_PACKET_MANIFEST.json']=manifest
 expected=dict(schema='dg16.fixed-root-bootstrap-admission.v1',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',operation='CREATE_EXCLUSIVE_ROOT_ISLAND_AND_EXACT_PUBLIC_PACKET_ONLY',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],run_attempt=1,automatic_retry=False,original_awards=[],manifest_sha256=sha(manifest))
 out['BOOTSTRAP_ADMISSION_REQUIREMENTS.json']=request('ACTUAL_ROOT_BOOTSTRAP_ADMISSION',expected)
 return out

def finish(prior,admission_raw):
 expected=parse(prior['BOOTSTRAP_ADMISSION_REQUIREMENTS.json'])['expected_body'];need(parse(admission_raw)==expected and encode(expected)==admission_raw,'ACTUAL_BOOTSTRAP_ADMISSION_MISMATCH')
 t=templates();s=selection(parse(prior['SELECTION.json']));out=dict(prior);core_prefix='tree/'+W.CORE+'/'
 common=assignments(t['adapter/integration/entry_common.py'],{'ENTRY_STATE':'REVIEWED_EXACT_EXTERNAL_CARRIER_ENTRY','CARRIER_LOADER_DESCRIPTOR':desc(prior[core_prefix+'carrier/carrier_loader.py']),'EXPECTED_PUBLIC_MANIFEST_SHA256':sha(prior['PUBLIC_PACKET_MANIFEST.json']),'EXPECTED_BOOTSTRAP_ADMISSION_SHA256':sha(admission_raw)})
 entries={'entry_common.py':common,'PUBLIC_PACKET_MANIFEST.json':prior['PUBLIC_PACKET_MANIFEST.json'],'BOOTSTRAP_ADMISSION.json':admission_raw}
 for name in HOST_WRAPPERS:entries[name]=assignments(t['adapter/integration/'+name],{'COMMON_SHA256':sha(common)})
 entries['public_export.py']=assignments(read(BASE/'author/public_export.py'),{'BRANCH':s['branch'],'CORE_RUN_SHA256':sha(prior[core_prefix+'run.py'])})
 entries['bootstrap_entry.py']=assignments(read(BASE/'author/bootstrap_entry.py'),{'BRANCH':s['branch'],'PLACEMENT_DESCRIPTOR':desc(prior[core_prefix+'root_placement.py']),'MANIFEST_SHA256':sha(prior['PUBLIC_PACKET_MANIFEST.json']),'ADMISSION_SHA256':sha(admission_raw)})
 from refusal_render import render
 for name in (*HOST_WRAPPERS,'bootstrap_entry.py','public_export.py'):entries[name]=render(name,entries[name])
 out.update({'tree/'+W.ENTRY+'/'+n:b for n,b in entries.items()})
 out['COMPOSITION_RESULT.json']=encode(dict(schema='dg16.offline-composition-result.v1',authority='NONE',status='EXACT_ASSEMBLY_REQUIRES_ROOT_WHOLE_TREE_RECEIVING_AND_FRESH_GRANT',source_commit=SOURCE,source_tree=TREE,workflow_sha256=sha(prior['tree/'+W.WORKFLOW]),public_manifest_sha256=sha(prior['PUBLIC_PACKET_MANIFEST.json']),bootstrap_admission_sha256=sha(admission_raw),root_sender='LATE_SEPARATE_IMMUTABLE_ASSEMBLY_REQUIRED',physical_currentness='ACTUAL_HOST_REQUIRED',original_awards=[]))
 from publication import build
 out.update({'publication/'+n:b for n,b in build(out).items()})
 return out

def write_phase(directory,data,phase):
 directory=Path(directory);need(not directory.exists(),'FRESH_OUTPUT_REQUIRED');directory.mkdir(mode=0o700)
 index={}
 for n,b in sorted(data.items()):
  need(not n.startswith('/') and '..' not in Path(n).parts,'OUTPUT_PATH');p=directory/n;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(b)
  p.chmod(0o600);need(read(p)==b,'OUTPUT_READBACK');index[n]=desc(b)
 summary=encode(dict(schema='dg16.offline-composition-phase.v1',phase=phase,authority='NONE',members=index,original_awards=[]));(directory/'PHASE.json').write_bytes(summary)
 return desc(summary)
def read_phase(path,wanted):
 data=population(Path(path));record=parse(data.pop('PHASE.json'));need(record['schema']=='dg16.offline-composition-phase.v1' and record['phase']==wanted and record['authority']=='NONE' and record['original_awards']==[] and record['members']=={n:desc(b) for n,b in data.items()},'PHASE_CHANGED');return data

def main():
 args=sys.argv[1:];need(len(args)==4,'USAGE_PHASE_INPUT_ACTUAL_BODY_OUTPUT')
 phase,a,b,out=args
 if phase=='prepare':data=prepare(parse(read(a)),population(Path(b)))
 elif phase=='bind-carrier':data=bind_carrier(read_phase(a,'prepare'),read(b))
 elif phase=='finish':data=finish(read_phase(a,'bind-carrier'),read(b))
 elif phase=='sender':
  from sender_assembly import assemble
  data=assemble(read_phase(a,'finish'),population(Path(b)))
 else:need(False,'UNKNOWN_PHASE')
 print(json.dumps(write_phase(out,data,phase),sort_keys=True))
if __name__=='__main__':main()
