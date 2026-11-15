"""G132 source interface receiving: new physical joins and original consumers.
No build/generator replay, native/provider/crypto/Git operation, role or live
preflight. Prior G131 cases reused only after exact bounded source rebinding.
Root alone owns acceptance/selection. Writes confined to this review lane.
"""
from pathlib import Path
import ast,copy,datetime,hashlib,json,os,re,stat,sys,types
OUT=Path('/home/agent/pr255-g132-independent-binding-review-20261114-01/interface')
PRIOR=Path('/home/agent/pr255-g131-interface-review-20261114-01')
S=Path('/home/agent/pr255-g132-source-preparation-20261114-01/bound-interface-01')
A=Path('/home/agent/pr255-g132-root-20261114-01/public-tools-source-01')
G=A.parent/'receiver-generation-01/source/candidate'
OLD=Path('/home/agent/pr255-g131-root-20261114-01/public-tools-source-01')
OLDS=Path('/home/agent/pr255-g131-source-preparation-20261114-01/interface-preparation')
D1=Path('/home/agent/pr255-g1-image127-adopted-source-20261114-01/source')
WHOLE=OUT.parent
ROOT='01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
PHASE='39fd7b7abe4f4535d31b2fad4f11a5a2074278aed7ef4c3fefd7ef5948add54e'
TREE='e7b77a2e8cdf6d7409a694efcbb3b13483bac5c9'
COMMIT='a33b8d1cdb967124b1b0d4fe877cf9b283304798'
CHECKS={};BLOCKED=[]
def need(v,c):
 if not v:raise AssertionError(c)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def read(p):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not p.is_symlink(),'READ_PHYSICAL_FILE')
 mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns,x.st_nlink)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  need(mark(os.fstat(fd))==mark(s),'OPEN_CHANGED');b=os.pread(fd,s.st_size+1,0)
  need(len(b)==s.st_size and mark(os.fstat(fd))==mark(s)==mark(p.lstat()),'CLOSING_CHANGED');return b
 finally:os.close(fd)
def pin(p):return dict(path=str(p),**desc(read(p)))
def write(name,v):
 b=(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
 with (OUT/name).open('xb') as f:f.write(b)
 need(read(OUT/name)==b,'OUTPUT_READBACK');return pin(OUT/name)
def fence(event,args):
 if event.startswith(('subprocess.','socket.','ctypes.')) or event in ('os.fork','os.exec','os.posix_spawn','os.system','os.kill','os.killpg'):
  BLOCKED.append(event);raise PermissionError('SOURCE_REVIEW_EFFECT_REFUSED')
 if event=='open':
  p,mode,flags=args
  writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  if writing:need(isinstance(p,(str,bytes,os.PathLike)) and Path(os.fsdecode(p)).resolve().is_relative_to(OUT),'WRITE_OUTSIDE_REVIEW')
 if event in ('os.mkdir','os.remove','os.rename','os.rmdir','os.chmod','os.chown','os.symlink','os.link','os.truncate','os.utime'):
  BLOCKED.append(event);raise PermissionError('SOURCE_REVIEW_MUTATION_REFUSED')
sys.addaudithook(fence)
def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(read(p),str(p),'exec'),m.__dict__);return m
def constants(raw):
 out={}
 for n in ast.parse(raw).body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
   try:out[n.targets[0].id]=ast.literal_eval(n.value)
   except (ValueError,TypeError):pass
 return out
def owners(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))}
def semantic(raw,exclude=()):
 t=ast.parse(raw)
 for n in t.body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in exclude:n.value=ast.Constant(n.targets[0].id)
 return ast.dump(t,include_attributes=False)
def verify_manifest(root,h):
 p=root/'MANIFEST.json';need(sha(read(p))==h,'MANIFEST_PIN_'+str(root));v=json.loads(read(p))
 need(len(v['members'])==v['member_count'],'MANIFEST_COUNT')
 for n,row in v['members'].items():
  need(not Path(n).is_absolute() and '..' not in Path(n).parts,'MANIFEST_PATH')
  need(desc(read(root/n))=={k:row[k] for k in ('bytes','sha256')},'MANIFEST_MEMBER_'+n)
  if 'mode' in row:need(stat.S_IMODE((root/n).lstat().st_mode)==row['mode'],'MANIFEST_MODE_'+n)
 return v
def population(root,inventory,modes=False):
 wanted=set(inventory);need(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in wanted),'INVENTORY_PATHS')
 paths=list(root.rglob('*'));found=set();dirs={''}
 for p in paths:
  st=p.lstat();need(not p.is_symlink() and (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)),'PHYSICAL_TYPE')
  if stat.S_ISREG(st.st_mode):found.add(p.relative_to(root).as_posix())
  else:dirs.add(p.relative_to(root).as_posix())
 need(found==wanted,'EXACT_SOURCE_POPULATION')
 # Only after exact population holds, read listed source/metadata; never unexpected key/cipher/session data.
 out={n:read(root/n) for n in sorted(wanted)}
 need({n:desc(b) for n,b in out.items()}==inventory,'EXACT_SOURCE_INVENTORY')
 for n in wanted:
  st=(root/n).lstat();need(st.st_uid==os.geteuid() and not os.listxattr(root/n),'SOURCE_OWNER_XATTR')
  if modes:need(stat.S_IMODE(st.st_mode)==(0o600 if n.startswith('retained-final5f-private-inputs/') else 0o400),'SOURCE_MODE')
 if modes:
  expected={''}
  for n in wanted:expected.update(p.as_posix() for p in Path(n).parents if str(p)!='.')
  need(dirs==expected,'NO_EXTRA_DIRECTORIES')
  for n in dirs:
   st=(root/n).lstat();need(st.st_uid==os.geteuid() and stat.S_IMODE(st.st_mode)==0o700 and not os.listxattr(root/n),'DIRECTORY_CUSTODY')
 return out,dirs
def reject(fn,code):
 try:fn()
 except (AssertionError,ValueError) as e:return str(e)
 raise AssertionError(code)
def run():
 need(sys.platform=='linux' and sys.flags.isolated and sys.dont_write_bytecode and os.getuid()==os.geteuid()>0,'ISOLATED_NONROOT')
 verify_manifest(PRIOR,'d0ca990724416ad2b93de0455328cc384c1dd823995669eaebe8f40a42db53ed')
 old_final=json.loads(read(PRIOR/'FINAL.json'))
 need(desc(read(PRIOR/'FINAL.json'))==dict(bytes=10467,sha256='ab5e2a8d7005e3a1ae17cefedbf9d5fe986fde39bc1fbe9c01a04adbbb6f43c8'),'PRIOR_FINAL')
 need(old_final['disposition']=='PASS_SOURCE_INTERFACE_ONLY' and old_final['blocking_source_findings']==[] and old_final['original_awards']==[],'PRIOR_SCOPE')
 verify_manifest(S,'1020e0265031c8fff6adbac3e15e317863d5221273446eb67000c2f9fece1dc2')
 verify_manifest(S/'actual','3bcf02ebb18faab8c988e4030b7cdf7733497f9db9d77fd16c6647e4ddb317f0')
 inv=json.loads(read(S/'actual/PUBLIC_TOOLS_SOURCE_INVENTORY.json'))
 need(sha(read(S/'actual/PUBLIC_TOOLS_SOURCE_INVENTORY.json'))=='aa63fc9b5ad0dcd0f5b098996498c47c71a6746103fd602816a801192fcf7a63','INVENTORY')
 before,dirs=population(A,inv['members'],True);need(len(before)==151 and len(dirs)==34,'SOURCE151')
 receipt=json.loads(read(S/'actual/ACTUAL_RECEIVER_FACTORY_RECEIVING.json'))
 factory,fdirs=population(G,receipt['inventory']['files']);need(len(factory)==71,'FACTORY71')
 CHECKS['physical_inventory']=dict(interface_files=151,factory_files=71,source0400=140,metadata0600=11,owned0700_directories=len(dirs),no_extra_files_or_directories=True,single_link_regular_no_xattrs=True,runtime_parents_present=False)
 for n,row in receipt['factory_source_closure'].items():
  need(desc(read(S/'factory'/n))==row and read(S/'factory'/n)==read(G.parent/n),'FACTORY_CLOSURE_'+n)
 for n,b in factory.items():
  if n.startswith(('phase/','evidence/')) or n=='SOURCES.json':need(b==before['public-receiver-02/'+n],'ACTUAL71_151_JOIN_'+n)
 priorinv=json.loads(read(OLDS/'actual/PUBLIC_TOOLS_SOURCE_INVENTORY.json'))['members']
 need(set(priorinv)==set(before),'UNCHANGED151_POPULATION')
 prior={n:read(OLD/n) for n in sorted(priorinv)}
 need({n:desc(b) for n,b in prior.items()}==priorinv,'PRIOR151_BYTES')
 oldfr=json.loads(read(OLDS/'actual/ACTUAL_RECEIVER_FACTORY_RECEIVING.json'))
 oldg=OLD.parent/'receiver-generation-01/source/candidate'
 priorfactory={n:read(oldg/n) for n in oldfr['inventory']['files']}
 need({n:desc(b) for n,b in priorfactory.items()}==oldfr['inventory']['files'],'PRIOR71_BYTES')
 mapping={}
 for previous,current in ((prior,before),(priorfactory,factory)):
  for n,b in previous.items():
   if n in current and b!=current[n]:
    h=sha(b);v=sha(current[n]);need(h not in mapping or mapping[h]==v,'AMBIGUOUS_PIN_REBIND');mapping[h]=v
 for n,row in receipt['factory_source_closure'].items():
  oldbody=read(OLDS/'factory'/n);newbody=read(S/'factory'/n)
  if oldbody!=newbody:mapping[sha(oldbody)]=sha(newbody)
 def rebound(raw):
  raw=raw.replace(str(OLD.parent).encode(),str(A.parent).encode())
  raw=raw.replace(b'03c94f06624e87179ad23ac3c4e3081eace726d8',TREE.encode())
  raw=raw.replace(b'pro/dg16-g1-original-g3-31-20261114',b'pro/dg16-g1-original-g3-32-20261114')
  raw=raw.replace(b'pro/dg16-g1-g3-control-31-20261114',b'pro/dg16-g1-g3-control-32-20261114')
  return re.sub(rb'[0-9a-f]{64}',lambda m:mapping.get(m.group().decode(),m.group().decode()).encode(),raw)
 code_names=[n for n in before if n.endswith(('.py','.js'))]
 changed=[]
 for n in code_names:
  got=rebound(prior[n])
  if got!=before[n]:changed.append(n)
 need(not changed,'UNEXPLAINED_SOURCE_BYTES:'+json.dumps(changed))
 oldfact=read(OLDS/'factory/final_bind.py');newfact=read(S/'factory/final_bind.py')
 need(semantic(oldfact,('PHASE_SHA','TREE'))==semantic(newfact,('PHASE_SHA','TREE')) and len(owners(newfact))==12,'FACTORY12_SOURCE_SEMANTICS')
 need(sha(read(S/'assemble_public_tools_source_g131.py'))=='c7bec750418a3313c66f08e79a86184ada9574fd59f72e702267b7a07118ec1b','UNCHANGED_GENERATOR')
 CHECKS['source_case_applicability']=dict(code_members=len(code_names),exact_complete_bytes_after_only_current_BASE_tree_branch_and_member_pin_rebinding=True,changed_functions_after_rebinding=[],factory12_semantics_except_PHASE_SHA_TREE_equal=True,generator_c7bec_unchanged=True,prior_review=pin(PRIOR/'FINAL.json'),prior57_checks_replayed=False,prior52_34_30_39_9_66_cases_replayed=False,scope='Original source scopes only; no runtime/native applicability inferred')
 pins=json.loads(before['OPERATOR_PINS.json']);need(pins=={n:desc(b) for n,b in before.items() if n.endswith(('.py','.js')) or n=='SOURCE_SELECTION.json'} and len(pins)==98,'OPERATOR98_CLOSURE')
 late='late-assembler-01/source-stage-01/source-support/';late_index=json.loads(before['late-assembler-01/source-stage-01/AUTHOR_SOURCE_INDEX.json'])['members']
 need(len(late_index)==46,'LATE46')
 for n,row in late_index.items():need(desc(before[late+n])==row and before[late+n]==read(D1/n),'LATE46_SOURCE_'+n)
 meta=json.loads(read(S/'actual/SOURCE_METADATA_11_INPUTS.json'))['members'];idx=json.loads(before['public-receiver-02/phase/INPUT_INDEX.json'])
 need(set(meta)==set(idx) and len(meta)==11,'METADATA11')
 for n,row in meta.items():need(desc(before['retained-final5f-private-inputs/'+n])==idx[n]=={k:row[k] for k in ('bytes','sha256')} and before['retained-final5f-private-inputs/'+n]==read(row['source']),'METADATA_JOIN_'+n)
 rb=json.loads(read(S/'ROOT_BINDINGS.json'))
 need(rb==dict(B=str(A.parent),D1=str(D1),H=str(S/'actual'),HOST_TREE=TREE,INPUTS='/home/agent/pr255-g132-composition-20261114-01/inputs',NEW=str(A),PACKET=str(G),PHASE_SHA=PHASE,issuer_thread=ROOT),'ROOT_BINDING_EXACT')
 inputs=json.loads(read(S/'actual/ROOT_INSTALLATION_SELECTION_INPUTS.json'))
 need(inputs['phase_sha256']==PHASE and inputs['host_tree']==TREE and inputs['actual_151_source_root']==str(A) and inputs['expected_unpublished_local_commit']==COMMIT and inputs['actual_Root_selection_issued'] is False,'SELECTION_INPUTS')
 for n,row in inputs['actual_source_descriptors'].items():need(sha(read(row['path']))==row['sha256'],'SOURCE_DESCRIPTOR_'+n)
 need(inputs['runtime_paths']['BASE']==str(A) and Path(inputs['runtime_paths']['journal_fresh_leaf']).parent==A/'public-receiver-02/control-sessions','PLANNED_JOURNAL_LEXICAL_JOIN')
 rootraw=read(A.parent/'ROOT_OFFLINE_HOST_RECEIVING.json');hostraw=read(WHOLE/'FINAL.json')
 need(desc(rootraw)==dict(bytes=1356,sha256='51cd1068466d1a77edb92e5eab4baf0172c44cb408f9172580da0f34061555a4'),'ACTUAL_ROOT_OFFLINE')
 need(before['public-receiver-02/evidence/root_offline_receiving.json']==rootraw and before['public-receiver-02/evidence/host_review.json']==hostraw,'ROOT_WHOLE_COPIES')
 root=json.loads(rootraw);whole=json.loads(hostraw)
 need(root['actor']=='/root' and root['issuer_thread']==ROOT and root['actual_root_turn']=='01a1dbc4-79af-7f81-a77b-a637f2b44a4f' and root['effect_grant'] is False and root['original_awards']==[],'ACTUAL_ROOT_IDENTITY')
 CHECKS['binding_pin_joins']=dict(operator_pins=98,late_source=46,metadata=11,root_bindings=pin(S/'ROOT_BINDINGS.json'),selection_inputs=pin(S/'actual/ROOT_INSTALLATION_SELECTION_INPUTS.json'),root_offline=pin(A.parent/'ROOT_OFFLINE_HOST_RECEIVING.json'),whole_host_review=pin(WHOLE/'FINAL.json'),host_commit_basis='Root record only; no provider publication observation')
 # Original factory collection revalidates actual phase and Root/independent/export evidence; build is never called.
 load(G.parent/'physical_io.py','physical_io');F=load(G.parent/'final_bind.py','g132_actual_factory_source')
 bind=json.loads(read(S/'BINDING_INPUTS.json'));collected=F.collect(bind)
 need(all(factory[n]==b for n,b in collected.items()),'ORIGINAL_COLLECT_ACTUAL71')
 R=load(A/'public-receiver-02/author/receiver.py','g132_actual_receiver');rs=R.Sources();rs.R.require_complete_packet()
 D=load(A/'g3-intake/actual_packet.py','g132_actual_D2');ds=D.sources(D.receiver());need(ds.sources['phase']['sha256']==PHASE,'D2_PHASE_JOIN')
 M=load(A/'root-event-helpers-02/root_live_sender_call_received.py','g132_actual_helper');P=M.pipeline()
 for n,(p,h) in M.PINS.items():need(sha(read(p))==h,'HELPER_PEER_'+n)
 need(P.BASE==A and P.BINARY_SHA==sha(before['root-final-operators-01/binary_publish_v3.py']),'PIPELINE_BINARY_JOIN')
 E=load(A/'root-event-helpers-02/g1_event_config_corrected.py','g132_actual_event');role=load(A/'framed-role-02/role_process_v4.py','g132_actual_role');control=load(A/'public-receiver-02/root-control-v5/control_process_v5.py','g132_actual_control')
 receiver=before['public-receiver-02/author/receiver.py'];resolver=before['public-receiver-02/author/resolve_artifact.py']
 need(E.ISSUER==role.ISSUER==control.ISSUER==M.ROOT==P.ISSUER==ROOT,'SIX_CURRENT_ROOT')
 need(E.ROLE_SHA==sha(before['framed-role-02/role_process_v4.py']) and E.CONTROL_SHA==sha(before['public-receiver-02/root-control-v5/control_process_v5.py']) and E.RECEIVER_SHA==role.RECEIVER_SHA==control.RECEIVER_SHA==sha(receiver) and E.RESOLVER_SHA==role.RESOLVER_SHA==control.RESOLVER_SHA==sha(resolver),'ROLE_CONTROL_PINS')
 need(constants(before['root-final-operators-01/control_process_v3.py'])['ISSUER']=='01a1953f-a15b-7811-aa72-3538ebb03562','HISTORICAL_DRIVER_ISSUER')
 selector=load(A/'source_selected_event.py','g132_actual_selector');v,sr,ss,se=selector.selected(before['SOURCE_SELECTION.json'])
 need(v['purpose']=='DONOR_PREFLIGHT_ONLY' and ss.sources['phase']['sha256']==PHASE and v['host_tree']==TREE,'ACTUAL_SOURCE_SELECTED_JOIN')
 bad=copy.deepcopy(v);bad['phase_sha256']=old_final['exact_subject']['phase_sha256']
 stale=reject(lambda:selector.selected(json.dumps(bad).encode()),'STALE_PHASE_ACCEPTED')
 need(stale=='SOURCE_HOST_PHASE_MISMATCH','STALE_PHASE_REASON')
 CHECKS['actual_original_consumers']=dict(factory_collect_members=len(collected),factory_build_called=False,Sources_and_complete_packet=True,D2=True,helper_pipeline=True,role_control_event=True,selected_donor_preflight=True,stale_selected_phase_refusal=stale,live_path_preflight_invoked=False,case_suite_replayed=False)
 qual=json.loads(read(S/'actual/PUBLIC_TOOLS_SOURCE_QUALIFICATION.json'));author=json.loads(read(S/'actual/RETURN.json'))
 need(sha(read(S/'actual/PUBLIC_TOOLS_SOURCE_QUALIFICATION.json'))=='d1abe9b3ee7c7fb96fec24b8fc14f4e5b1007574bc00f8d352c469045bc93ce6','QUALIFICATION_PIN')
 need(qual['source_inventory']==desc(read(S/'actual/PUBLIC_TOOLS_SOURCE_INVENTORY.json')) and qual['actual_receiver']==desc(receiver) and qual['actual_e76_helper']==desc(before['root-event-helpers-02/root_live_sender_call_received.py']) and qual['pin_rounds']==author['actual_pin_rounds']==3,'QUALIFICATION_PHYSICAL_JOIN')
 need(author['generator_main_invocations']==author['factory_invocations']==1 and author['runtime_parent_or_preflight_operations'] is False and author['provider_native_crypto_job_or_publication_operations'] is False and author['G131_UNKNOWN_NO_REPLAY_preserved'] is True,'AUTHOR_BOUNDARIES')
 after,_=population(A,inv['members'],True);afterfactory,_=population(G,receipt['inventory']['files'])
 need(after==before and afterfactory==factory and not BLOCKED,'CLOSING_NO_CHANGE_OR_EFFECT')
 verify_manifest(S/'actual','3bcf02ebb18faab8c988e4030b7cdf7733497f9db9d77fd16c6647e4ddb317f0')
 CHECKS['closing']=dict(source151_unchanged=True,factory71_unchanged=True,author_manifest_unchanged=True,guarded_effect_attempts=BLOCKED)
 write('CHECKS.json',dict(schema='source.G132.exact-interface-review-checks.v1',status='PASS_SOURCE_INTERFACE_ONLY',authority='NONE',original_awards=[],checks=CHECKS))
 final=dict(schema='source.G132.independent-exact-interface-review.v1',authority='NONE',reviewer='/root/g132_binding_review',source_author='/root/g2_source_review',review_completion='COMPLETE',review_scope=old_final['review_scope'],disposition='PASS_SOURCE_INTERFACE_ONLY',blocking_source_findings=[],effect_grant=False,native_qualification=False,operational_readiness=False,original_awards=[],completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),independence='Same independently dispatched G132 whole-host reviewer; no source/factory/Root-record authorship. New physical/source joins and original maintained consumers checked; exact prior source cases reused after bounded full-code rebinding equality.',effects=dict(generation_replays=0,native_or_crypto_calls=0,private_key_access=0,protected_unknown_replays=0,provider_calls=0,roles=0,source_mutations=0),exact_subject=dict(currentRoot=ROOT,expected_host_tree=TREE,factory_root=str(G),interface_root=str(A),phase_sha256=PHASE,prospective_profile_rows=3,source_selection='DONOR_PREFLIGHT_ONLY',actual_author_manifest=pin(S/'actual/MANIFEST.json'),actual_factory_receiving=pin(S/'actual/ACTUAL_RECEIVER_FACTORY_RECEIVING.json'),actual_qualification=pin(S/'actual/PUBLIC_TOOLS_SOURCE_QUALIFICATION.json'),interface_inventory=pin(S/'actual/PUBLIC_TOOLS_SOURCE_INVENTORY.json'),prepared_author_manifest=pin(S/'MANIFEST.json'),source_adoption=pin(D1.parent/'SOURCE_ADOPTION.json'),receiver=pin(A/'public-receiver-02/author/receiver.py'),D2=pin(A/'g3-intake/actual_packet.py'),generator=pin(S/'assemble_public_tools_source_g131.py'),generator_root_bindings=pin(S/'ROOT_BINDINGS.json'),actual_helper=pin(A/'root-event-helpers-02/root_live_sender_call_received.py'),actual_pipeline=pin(A/'root-final-operators-01/root_pipeline_inputs_v2.py'),actual_pin_rounds=3,expected_local_host_commit=COMMIT,commit_basis='Root record; not provider publication observation',installation_selection_inputs=pin(S/'actual/ROOT_INSTALLATION_SELECTION_INPUTS.json')),reused_evidence=[pin(PRIOR/'FINAL.json'),pin(PRIOR/'MANIFEST.json'),pin(WHOLE/'FINAL.json')],verification=dict(check_count=len(CHECKS),checks=pin(OUT/'CHECKS.json'),script=pin(OUT/'interface_checks.py'),runtime='WSL Linux nonroot Python -I -B',poststate='Exact151/71 unchanged; no extra source directories or runtime parents; actual live preflights not invoked.',prior_harness_reuse='Prior57,52/34,30,39,9 and66 case sets not replayed. All97 code members match prior complete bytes after only actual BASE/tree/branch/member digest rebinding; original scope retained.',original_consumers=CHECKS['actual_original_consumers']),verified_scope=['Exact factory71/interface151 inventories and current physical custody, 140 source0400/11 metadata0600 and34 owned0700 directories.','Factory12 semantics unchanged except phase/tree; reviewed c7bec generator unchanged; actual71 immutable phase/evidence copies and151 current Root receiving join.','All97 code files preserve full bytes after exact new BASE/tree/branch and member pin rebinding; caller-path guards and all original cases retained at source scope.','Operator98/late46/metadata11 and six Root identities/pins close. Original collect, Sources, complete-packet, D2, helper/pipeline, role/control/event and selected-source consumers pass. Stale selected phase refuses.','G131 UNKNOWN_NO_REPLAY preserved; source selection remains DONOR_PREFLIGHT_ONLY, current live path or native acceptance not established.'],remaining_gates=['Root receives this FINAL and issues actual installation/source-selection records; reviewer grants no effect.','Root creates/receives actual runtime parents and executes both original pure publication-inputs journal validation and read-only check-runtime-parents before live role/window issuance; recheck on drift.','Keep recipient leaf r<run_id>-recipient and original exact Ubuntu24/Python3.12.3/tool/image and75min/600s/45s guards.','Preserve G131 sender/publication UNKNOWN_NO_REPLAY and earlier fences; no old grant/cipher/recipient/journal reuse, absence or no-effect inference.','Host publication, currentness, callback/sender readiness, native/G1/G3/L04 acceptance remain separate Root gates. G220 Ubuntu26 untouched.'],state_machine=dict(stable_id='G1-CALLER-BOUNDARY-PREFLIGHT',related_machine='ROOT_BINARY_PUBLICATION',runtime_baseline=CHECKS['physical_inventory'],registry_disposition='No registry write authority. Existing source/path enforcement retained. Actual source151, Root selection, runtime parents, live roles and acceptance remain separate dimensions.'))
 need(set(old_final)<=set(final),'ORIGINAL_FINAL_FIELDS')
 need(final['exact_subject']['phase_sha256']==whole['exact_subject']['finish_phase_sha256'] and final['exact_subject']['expected_host_tree']==whole['exact_subject']['expected_git_tree'],'FINAL_WHOLE_JOIN')
 write('FINAL.json',final)
 write('CONTRACT_CHECK.json',dict(schema='source.G132.interface-review-contract-check.v1',authority='NONE',actual_current_phase_join=True,actual_final=pin(OUT/'FINAL.json'),all_prior_top_level_fields_present=True,prior_contract=pin(PRIOR/'FINAL.json'),actual_original_consumers=CHECKS['actual_original_consumers'],source_only=True))
 members={n:desc(read(OUT/n)) for n in ('interface_checks.py','CHECKS.json','FINAL.json','CONTRACT_CHECK.json')}
 write('MANIFEST.json',dict(schema='source.G132.independent-interface-review-manifest.v1',authority='NONE',reviewer='/root/g132_binding_review',effect_grant=False,original_awards=[],member_count=len(members),members=members,self_excluded='MANIFEST.json'))
 for n,row in members.items():need(desc(read(OUT/n))==row,'DELIVERY_READBACK')
 print(json.dumps(dict(final=pin(OUT/'FINAL.json'),manifest=pin(OUT/'MANIFEST.json'),checks=pin(OUT/'CHECKS.json'),disposition=final['disposition']),sort_keys=True))
if __name__=='__main__':
 try:run()
 except BaseException as e:
  write('CHECK_FAILURE.json',dict(exception_type=type(e).__name__,message=str(e),checks=CHECKS,guarded_effect_attempts=BLOCKED));raise
