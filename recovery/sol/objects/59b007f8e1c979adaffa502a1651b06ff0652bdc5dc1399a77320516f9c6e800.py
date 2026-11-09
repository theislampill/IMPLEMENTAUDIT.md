"""Deterministic offline assembly; no issuer, remote, native or command API.

Each phase consumes exact actual root inputs and writes a fresh directory.
Requirements are requests for separately issued bodies, never admissions.
Host and later Pro sender assemblies are distinct immutable populations.
"""
import ast,hashlib,json,os,re,stat,sys
from pathlib import Path
import workflow as W
BASE=Path(__file__).resolve().parent.parent
SOURCE='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
ROLES={'root_admission':'COMPOSITION_ROOT_ADMISSION.json','placement_receiving':'COMPOSITION_PLACEMENT_RECEIVING.json','placement_evidence_index':'COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json','native_applicability_adoption':'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'}
RETAINED={'SOURCE_ACQUISITION.json':{'bytes':198602,'sha256':'8c3b2ddace7802d91308121f2d3f2b8f236fd5d443dcd2237164e20665cd3319'},'PACKAGE_ROOT_RECEIVING.json':{'bytes':928,'sha256':'0edff0f3d8bd6f5520ef72d4e91daba54a6b0033e85b94f041f448c2951d6691'},'PACKAGE_BODY_RECEIVING.json':{'bytes':9744,'sha256':'8c592c76967ae2d95101af86ca25ab3bd4d09acdad486afbb976d61e7e5a7811'},'PACKAGE_TERMINAL_RECEIVING.json':{'bytes':4531,'sha256':'e213b8843f03741c48776277f9e1db8c78ea1d3f7609875ce32bcd94e5ed5b89'}}
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
 for name,row in (RETAINED|PLACEMENT).items():need(desc(private[name])==row,'EXACT_RETAINED_BODY_'+name)
 v={r:parse(private[n]) for r,n in ROLES.items()};comp=parse(core['HOST_COMPOSITION.json'])
 expected=dict(schema='dg16.current-core-host-root-admission.v1',issuer='R5_ROOT_GOVERNOR',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],run_attempt=1,automatic_retry=False,original_awards=[],prospective_operation='ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE',component_scope='CORE_G1_Q06_NATURAL_L04_SEPARATE',input_sha256={r:sha(private[n]) for r,n in ROLES.items() if r!='root_admission'})
 need(v['root_admission']==expected,'ACTUAL_CORE_ADMISSION_REQUIRED')
 a=v['native_applicability_adoption'];need(a.get('schema')=='dg16.current-native-applicability-root-adoption.v1' and a.get('source_commit')==SOURCE and a.get('source_tree')==TREE and a.get('applicability_sha256')==sha(core['NATIVE_SOURCE_APPLICABILITY.json']) and type(a.get('unchanged_members')) is int and a['unchanged_members']==87 and type(a.get('changed_members')) is int and a['changed_members']==2 and a.get('windows_qualification')=='DG18_SEPARATE' and a.get('original_awards')==[],'ACTUAL_NATIVE_ADOPTION_REQUIRED')
 scope='ACCESS09_RUN42311009492_A1_JOB128212159527_I0_ONLY'
 need(v['placement_evidence_index']==dict(schema='dg16.received-placement-evidence-index.v1',scope=scope,members=PLACEMENT),'EXACT_PLACEMENT_INDEX')
 need(v['placement_receiving']==dict(schema='dg16.actual-working-root-placement-receiving.v1',source_commit=SOURCE,source_tree=TREE,observed_source_commit='3e0f4b6d05eb086017ce721d40459fdbd68714dd',placement=comp['placement'],status='ACTUAL_ROOT_ISLAND_FD_ROUTE_RECEIVED_AT_DIAGNOSTIC_SCOPE',cause='UNPROVED',original_awards=[],evidence_scope=scope,evidence_index_sha256=sha(private[ROLES['placement_evidence_index']]),source_applicability_sha256=sha(private[ROLES['native_applicability_adoption']]),native_transfer='NONE_FRESH_NATIVE_BANK_AND_ORIGINAL_PAIR_REQUIRED'),'ACTUAL_PLACEMENT_RECEIVING_REQUIRED')
 # Booleans must not substitute for the exact integer attempt in an admission.
 need(type(v['root_admission']['run_attempt']) is int,'ADMISSION_ATTEMPT_TYPE')
 return {n:desc(b) for n,b in private.items()}

def core_bind(core,s,index):
 comp=parse(core['HOST_COMPOSITION.json']);comp.update(state='REVIEWED_EXACT_COMPOSITION',workflow_branch=s['branch'])
 for role,name in ROLES.items():comp[role]=dict(path='private-inputs/'+name,**index[name])
 core['HOST_COMPOSITION.json']=encode(comp)
 core['host_composition.py']=assignments(core['host_composition.py'],{'BINDING_SHA256':sha(core['HOST_COMPOSITION.json'])})
 core['g3_receiving.py']=assignments(core['g3_receiving.py'],{'JOB_BRANCH':s['branch'],'CONTROL_BRANCH':s['g3_control_branch']})
 # Bind AFTER g3 branch rewriting and BEFORE run/manifest/bootstrap closure.
 core['INDEPENDENT_PROOF_PINS.json']=encode(dict(schema='dg16.independent-consumer-pins.v1',source_commit=SOURCE,source_tree=TREE,
  scope_sha256=sha(core['ORIGINAL_SCOPE.json']),adverse_sha256=sha(core['ADVERSE_APPLICABILITY.json']),
  compiler_sha256='0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d',
  owner_sha256='9bce5c887cd89c2d2991b84f1bf765787e7a6b75a2eba29a8433c3a6c05f73a3',
  scope_module_sha256=sha(core['g3_receiving.py']),consumer_sha256=sha(core['proof_consumer.py']),initial_control_branch=s['g3_control_branch']))
 pins=literal(core['run.py'],'MODULE_PINS');data=literal(core['run.py'],'G3_DATA_PINS')
 pins['proof_consumer']=sha(core['proof_consumer.py']);data['INDEPENDENT_PROOF_PINS.json']=sha(core['INDEPENDENT_PROOF_PINS.json'])
 core['run.py']=assignments(core['run.py'],{'BRANCH':s['branch'],'MODULE_PINS':{n:sha(core[n+'.py']) for n in pins},'G3_DATA_PINS':{n:sha(core[n]) for n in data}})
 return core

def request(stage,expected):return encode(dict(schema='dg16.offline-composition-body-requirements.v1',stage=stage,authority='NONE',actual_admission=False,expected_body=expected,original_awards=[]))
def prepare(s,private):
 s=selection(s);t=templates();core={n[5:]:b for n,b in t.items() if n.startswith('core/')};index=role_check(s,private,core);core=core_bind(core,s,index)
 flow=W.render(s);out={'tree/'+W.WORKFLOW:flow,'SELECTION.json':encode(s),'INPUT_INDEX.json':encode(index)}
 out.update({'tree/'+W.CORE+'/'+n:b for n,b in core.items()})
 expected=dict(schema='dg16.core-private-carrier-root-admission.v2',issuer='R5_ROOT_GOVERNOR',operation='ONE_FIXED_TOOL_BOOTSTRAP_ONE_FRESH_RECIPIENT_ONE_PRIVATE_TRANSFER',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],workflow_path=W.WORKFLOW,workflow_sha256=sha(flow),control_branch=s['cipher_control_branch'],control_parent=s['cipher_control_parent'],input_index_sha256=sha(encode(index)),limits=s['carrier_limits'],host_tool_bootstrap=s['host_tools'],run_attempt=1,automatic_retry=False,core_or_native_effect_grant=False,original_awards=[])
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
 # The host cannot select an operation/admission for a future recipient. This
 # immutable unresolved sender is deliberately incapable of a Pro encryption.
 sender=parse(carrier['PRO_SENDER_COMPOSITION.json']);need(sender['operation'] is None and sender['admission'] is None and sender['state']=='UNRESOLVED_PRO_SENDER_COMPONENT','HOST_SENDER_MUST_BE_UNRESOLVED')
 sender.update(source_commit=SOURCE,source_tree=TREE);carrier['PRO_SENDER_COMPOSITION.json']=encode(sender)
 carrier['sender_policy.py']=assignments(carrier['sender_policy.py'],{'BINDING_SHA256':sha(carrier['PRO_SENDER_COMPOSITION.json'])})
 loader_bind(carrier)
 out=dict(prior);out.update({'tree/'+W.CORE+'/carrier/'+n:b for n,b in carrier.items()})
 members={n:dict(**desc(b),mode=0o400) for n,b in (core|{'carrier/'+n:b for n,b in carrier.items()}).items()}
 manifest=encode(dict(schema='dg16.fixed-root-public-manifest.v1',members=members));out['PUBLIC_PACKET_MANIFEST.json']=manifest
 expected=dict(schema='dg16.fixed-root-bootstrap-admission.v1',issuer='R5_ROOT_GOVERNOR',operation='CREATE_EXCLUSIVE_ROOT_ISLAND_AND_EXACT_PUBLIC_PACKET_ONLY',source_commit=SOURCE,source_tree=TREE,workflow_branch=s['branch'],run_attempt=1,automatic_retry=False,original_awards=[],manifest_sha256=sha(manifest))
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
