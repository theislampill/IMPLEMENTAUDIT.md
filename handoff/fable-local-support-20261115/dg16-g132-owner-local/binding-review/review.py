"""Independent G132 changed-binding receiving. Parent dispatch is authority.
Read-only inputs; writes only this review lane. Done when phase/source/tree/role
joins and unchanged logic reuse pass, original review predicates accept the
actual FINAL, and artifacts read back. Root retains publication/acceptance.
No native, provider, crypto, Git, phase-writer or role-issuance effects.
Rollback: retain findings and withhold source disposition; no effect to undo.
"""
from pathlib import Path
import ast, copy, datetime, hashlib, json, os, sys, types
sys.dont_write_bytecode=True
OUT=Path('/home/agent/pr255-g132-independent-binding-review-20261114-01')
PRIOR=Path('/home/agent/pr255-g131-whole-host-review-20261114-01')
PHASES=Path('/home/agent/pr255-g132-composition-20261114-01')
MIRROR=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-r3-execution-20261114-01/g132-binding-review')
ANCHOR=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-r3-execution-20261114-01/g132-root-preparation/ANCHOR_RECEIVING.json')
EXPECTED='e7b77a2e8cdf6d7409a694efcbb3b13483bac5c9'
PRODUCT='e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
BASE_TREE='ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'
BINDINGS={
 'prepare':('prepare','b5b5b42d6f2f6a37cac763064735d7e5921f1854ec222c6ad171894f6b974272',26),
 'bind':('bind-carrier','d172022b06f14aa43f444ac23e2427cb76c0fecdcd2233eb917498cf7d61b997',44),
 'finish':('finish','39fd7b7abe4f4535d31b2fad4f11a5a2074278aed7ef4c3fefd7ef5948add54e',59)}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,c):
 if not v:raise AssertionError(c)
old_driver=(PRIOR/'review.py').read_bytes()
need(sha(old_driver)=='038a1974eeaaea32834bfaf3dec5c34d7d87ce6b29245339a64f29ffa0c0e54f','G131_ORIGINAL_DRIVER')
old=types.ModuleType('reused_original_g131_review');old.__file__=str(PRIOR/'review.py')
exec(compile(old_driver,old.__file__,'exec'),old.__dict__)
old.OUT=OUT
C=old.C;W=old.W;desc=old.desc;pin=old.pin;write=old.write
CORE=old.CORE;ENTRY=old.ENTRY;CHECKS={}
main=next(n for n in ast.parse(old_driver).body if isinstance(n,ast.FunctionDef) and n.name=='main')
def assigned(n,name):
 return isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)
def check_assigned(n,name):
 return isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='CHECKS' and isinstance(t.slice,ast.Constant) and t.slice.value==name for t in n.targets)
def original_block(start,stop,ns):
 a=next(i for i,n in enumerate(main.body) if assigned(n,start))
 b=next(i for i,n in enumerate(main.body[a:],a) if check_assigned(n,stop))
 tree=ast.Module(body=main.body[a:b+1],type_ignores=[])
 exec(compile(tree,old.__file__+'#'+stop,'exec'),ns)
 return dict(start=main.body[a].lineno,end=main.body[b].end_lineno,ast_sha256=sha(ast.dump(tree,include_attributes=False).encode()))
def flat(v,p=''):
 result={}
 for k,x in v.items():
  if isinstance(x,dict):result.update(flat(x,p+k+'.'))
  else:result[p+k]=x
 return result
def reject(fn,code):
 try:fn()
 except (ValueError,AssertionError) as e:return dict(refused=True,code=str(e))
 raise AssertionError(code)
def run():
 prior_manifest=old.verify_manifest(PRIOR,'MANIFEST.json','89ccb836158cb27c1ddcd470ebd7f6b159904c6476dfa1291a3fc4710095cbab')
 need(desc(C.read(PRIOR/'FINAL.json'))==dict(bytes=22556,sha256='9dc92dc87f2a31990da602ac9258b5fd72003fb379f1b98bc48236da0bc020c2'),'G131_FINAL')
 previous=C.parse(C.read(PRIOR/'FINAL.json'))
 need(previous['review_completion']=='COMPLETE' and previous['blocking_source_findings']==[] and previous['original_awards']==[],'PRIOR_SCOPE')
 adoption=old.verify_source()
 need(desc(C.read(old.FACTORY))==dict(bytes=23822,sha256='9e397142d98bdef177cf5798480cbc8b96033955f7dc77ed22c272beaea2b9c5'),'ORIGINAL_CONSUMER')
 phases={}
 for name,(wanted,h,count) in BINDINGS.items():
  need(sha(C.read(PHASES/name/'PHASE.json'))==h,'PHASE_IDENTITY_'+name)
  phases[wanted]=C.read_phase(PHASES/name,wanted)
  need(len(phases[wanted])==count,'PHASE_COUNT_'+name)
 CHECKS['physical_phase_readers']={k:len(v) for k,v in phases.items()}
 prior_root=Path(previous['exact_subject']['phase_root'])
 need(sha(C.read(prior_root/'PHASE.json'))==previous['exact_subject']['finish_phase_sha256'],'PRIOR_PHASE_IDENTITY')
 old_phase=C.read_phase(prior_root,'finish')
 s=C.selection(C.parse(C.read(PHASES/'SELECTION.json')))
 old_s=C.selection(C.parse(C.read(prior_root.parent/'SELECTION.json')))
 before=flat(old_s);after=flat(s)
 delta={k:dict(before=before[k],after=after[k]) for k in before if before[k]!=after[k]}
 fresh={
  'branch':'pro/dg16-g1-original-g3-32-20261114',
  'g3_control_branch':'pro/dg16-g1-g3-control-32-20261114',
  'cipher_control_branch':'pro/dg16-g1-carrier-control-32-20261114',
  'cipher_control_parent':'e48ef76a986d1ce949661fd658cdcbe66f292788',
  'host_tools.control_branch':'pro/dg16-g1-tools-control-32-20261114',
  'host_tools.control_parent':'ec4433995f0a7b82d19d589028ece6877b8dfe98'}
 need(set(before)==set(after) and {k:v['after'] for k,v in delta.items()}==fresh,'SIX_FRESH_BINDINGS_ONLY')
 need(s['job_timeout_minutes']==75 and s['workflow_overhead_seconds']==600 and s['carrier_limits']['acquisition_seconds']==600 and s['host_tools']['adoption_seconds']==600,'ORIGINAL_LIMITS')
 names=set(C.RETAINED)|set(C.ROLES.values())|set(C.PLACEMENT)
 private={n:C.read(PHASES/'inputs'/n) for n in sorted(names)}
 old_private={n:C.read(prior_root.parent/'inputs'/n) for n in sorted(names)}
 need([n for n in private if private[n]!=old_private[n]]==['COMPOSITION_ROOT_ADMISSION.json'],'ONLY_CORE_INPUT_CHANGED')
 issuance=C.parse(C.read(PHASES/'ROOT_SOURCE_ISSUANCE.json'))
 need(issuance['actor']=='/root' and issuance['issuer_thread']=='01a1cf82-cdd6-7053-b7b7-32f5c3d93d21' and issuance['actual_turn']=='01a1dbc4-79af-7f81-a77b-a637f2b44a4f','ROOT_IDENTITY')
 need(issuance['selection']==desc(C.read(PHASES/'SELECTION.json')) and issuance['CORE']==desc(private['COMPOSITION_ROOT_ADMISSION.json']) and issuance['source_root']==str(old.SOURCE),'ROOT_ISSUANCE_JOINS')
 need(issuance['G131_material_or_grant_reused'] is False and issuance['historical_metadata_reused_at_original_scope_only'] is True and issuance['original_awards']==[],'ROOT_ISSUANCE_SCOPE')
 role_paths={'COMPOSITION_ROOT_ADMISSION.json':PHASES/'inputs/COMPOSITION_ROOT_ADMISSION.json','A03_CARRIER_ADMISSION.json':PHASES/'inputs/A03.canonical.json','A04_BOOTSTRAP_ADMISSION.json':PHASES/'inputs/A04.json'}
 roles={n:pin(p) for n,p in role_paths.items()}
 a03=C.read(role_paths['A03_CARRIER_ADMISSION.json']);a04=C.read(role_paths['A04_BOOTSTRAP_ADMISSION.json'])
 need(desc(a03)==dict(bytes=1187,sha256='b80a25aedd5524233a1338c708426f7125a84be11fdcdcc38cbf637b0fc9af73'),'ACTUAL_A03')
 need(desc(a04)==dict(bytes=470,sha256='d597a656811f44a57b02de6da7a1322da8f3d40ea8ac65a6f5cd81f4fcf2867b'),'ACTUAL_A04')
 need(a03==C.encode(C.parse(phases['prepare']['CARRIER_ADMISSION_REQUIREMENTS.json'])['expected_body']),'A03_REQUIREMENTS_EXACT')
 need(a04==C.encode(C.parse(phases['bind-carrier']['BOOTSTRAP_ADMISSION_REQUIREMENTS.json'])['expected_body']),'A04_REQUIREMENTS_EXACT')
 CHECKS['fresh_binding_roles']=dict(selection=pin(PHASES/'SELECTION.json'),exactly_six_changes=delta,unchanged_historical_inputs=10,original_limits_and_tools_unchanged=True,issuance=pin(PHASES/'ROOT_SOURCE_ISSUANCE.json'),actual_roles=roles)
 p=C.prepare(s,private);need(p==phases['prepare'],'PREPARE_IN_MEMORY_EXACT')
 b=C.bind_carrier(p,a03);need(b==phases['bind-carrier'],'BIND_IN_MEMORY_EXACT')
 f=C.finish(b,a04);need(f==phases['finish'],'FINISH_IN_MEMORY_EXACT')
 CHECKS['pure_reconstruction']=dict(prepare_members=26,bind_carrier_members=44,finish_members=59,all_bytes_exact=True,phase_writer_called=False)
 CHECKS['new_binding_controls']={
  'unselected_pretty_A03':reject(lambda:C.bind_carrier(p,C.read(PHASES/'inputs/A03.json')),'PRETTY_A03_NOT_REFUSED'),
  'old_A03':reject(lambda:C.bind_carrier(p,C.read(Path(previous['actual_root_roles']['A03_CARRIER_ADMISSION.json']['path']))),'STALE_A03_NOT_REFUSED'),
  'old_A04':reject(lambda:C.finish(b,C.read(Path(previous['actual_root_roles']['A04_BOOTSTRAP_ADMISSION.json']['path']))),'STALE_A04_NOT_REFUSED')}
 CHECKS['unselected_pretty_A03']=dict(file=pin(PHASES/'inputs/A03.json'),selected=False,original_preserved=True)
 ns=dict(old.__dict__,CHECKS=CHECKS,EXPECTED=EXPECTED,PRODUCT=PRODUCT,BASE_TREE=BASE_TREE,f=f,a03=a03,a04=a04,s=s)
 blocks={'pin_closure':original_block('core','pin_closure',ns),'publication':original_block('public','publication',ns)}
 core=ns['core'];run_body=ns['run']
 need(sha(run_body)=='5fc666e84b8788cf71df2c654522101df80d0a861bdd4a8f2af9537461d43b3c','CURRENT_RUN_IDENTITY')
 py=[n for n in f if n.startswith('tree/') and n.endswith('.py')]
 need(set(f)==set(old_phase),'UNCHANGED_PHASE_POPULATION')
 changed_functions={n:[k for k,v in old.ast_defs(f[n]).items() if old.ast_defs(old_phase[n]).get(k)!=v] for n in py}
 need(all(old.ast_defs(f[n])==old.ast_defs(old_phase[n]) for n in py),'ALL_FUNCTION_CLASS_AST_UNCHANGED')
 # Pure original recomposition above bounds every changed literal to actual new inputs.
 profiles=old.literal(core['host_utility.py'],'G1_HOST_PROFILES')
 need(profiles==old.literal(old_phase[CORE+'host_utility.py'],'G1_HOST_PROFILES') and len(profiles)==3,'EXACT_PROFILE_REUSE')
 need(all(r['facts']['os']=={'ID':'ubuntu','VERSION_ID':'24.04'} and r['facts']['python_version']==[3,12,3] and r['facts']['image_os']=='ubuntu24' for r in profiles),'UBUNTU24_PYTHON3123')
 flow=C.parse(f['tree/'+W.WORKFLOW]);need(flow['jobs']['qualify']['runs-on']=='ubuntu-24.04' and flow['jobs']['qualify']['timeout-minutes']==75,'EXACT_JOB_GUARDS')
 ht=ast.parse(core['host_utility.py']);limits=next(n.value for n in ht.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Tuple) and [x.id for x in t.elts]==['RUN_SECONDS','PROBE_SECONDS','COMMAND_SECONDS'] for t in n.targets))
 need(ast.literal_eval(limits)==(45,15,4),'ORIGINAL_45_SECOND_LIMIT')
 for name in ('NATIVE_SOURCE_APPLICABILITY.json','ORIGINAL_SCOPE.json','ADVERSE_APPLICABILITY.json'):
  need(core[name]==old_phase[CORE+name],'ORIGINAL_SCOPE_BYTES_'+name)
 CHECKS['unchanged_logic_reuse']=dict(python_members=len(py),all_function_class_AST_equal=True,changed_functions={k:v for k,v in changed_functions.items() if v},source_members=51,exact_adoption=pin(old.AUTHOR/'SOURCE_ADOPTION.json'),all_three_exact_profiles=True,profile_tools_unchanged=True,source_controls_replayed=False,original_native89_and_scope_bytes_preserved=True,limits=[75,600,45],G220_Ubuntu26_not_involved=True)
 # Existing generator was reviewed at original scope; only pin its unchanged inputs.
 gen=previous['actual_checks']['preflight_generator']
 for key in ('author','frozen_manifest','source_control_receipt'):
  row=gen[key];need(desc(C.read(Path(row['path'])))=={k:row[k] for k in ('bytes','sha256')},'REUSED_GENERATOR_'+key)
 CHECKS['preflight_generator_reuse']=dict(prior_review=pin(PRIOR/'FINAL.json'),author=gen['author'],manifest=gen['frozen_manifest'],controls=gen['source_control_receipt'],controls_replayed=False,actual_G132_interface_generated_or_qualified=False)
 anchors=C.parse(C.read(ANCHOR))
 need(anchors['issuer_thread']==issuance['issuer_thread'] and anchors['actual_turn']==issuance['actual_turn'] and anchors['original_awards']==[] and anchors['G131_unchanged_no_replay'] is True,'ANCHOR_OWNER_JOIN')
 expected_anchors={'tools':(s['host_tools']['control_branch'],s['host_tools']['control_parent']),'carrier':(s['cipher_control_branch'],s['cipher_control_parent'])}
 need(len(anchors['anchors'])==2 and {x['role'] for x in anchors['anchors']}==set(expected_anchors),'ANCHOR_POPULATION')
 for row in anchors['anchors']:
  branch,commit=expected_anchors[row['role']]
  need(row['ref']=='refs/heads/'+branch and row['commit']==commit and row['tree']=='4b825dc642cb6eb9a060e54bf8d69288fbee4904' and row['parents']==[] and row['exit']==0,'ANCHOR_EXACT_JOIN')
 need(anchors['host_and_G3_not_published'] is True and anchors['native_or_crypto_started'] is False,'ANCHOR_RECORDED_SCOPE')
 CHECKS['anchor_record_join']=dict(record=pin(ANCHOR),exact_source_bindings=True,empty_tree_parentless=True,remote_read_performed=False,publication_claim_scope='Root recorded anchor publication only; no independent current provider observation')
 old.verify_source();old.verify_manifest(PRIOR,'MANIFEST.json','89ccb836158cb27c1ddcd470ebd7f6b159904c6476dfa1291a3fc4710095cbab')
 for name,(wanted,h,count) in BINDINGS.items():
  need(sha(C.read(PHASES/name/'PHASE.json'))==h and C.read_phase(PHASES/name,wanted)==phases[wanted],'CLOSING_PHASE_'+name)
 for n,row in roles.items():need(desc(C.read(role_paths[n]))=={k:row[k] for k in ('bytes','sha256')},'CLOSING_ROLE_'+n)
 CHECKS['original_checking_blocks']=dict(driver=pin(PRIOR/'review.py'),blocks=blocks,consumer=pin(old.FACTORY))
 CHECKS['closing_readback']=dict(source51=True,prior_review_manifest=True,all_actual_phase_members=True,actual_roles=True)
 write('CHECKS.json',CHECKS)
 final=dict(schema=previous['schema'],authority='NONE',reviewer='/root/g132_binding_review',current_delta_authorship=False,independence='Fresh independently dispatched reviewer; no authorship of G132 composition, original source, Root inputs or receiver. Reuses exact G131 checking code and unchanged source controls at original scope. Writes only assigned review lane.',review_completion='COMPLETE',disposition=previous['disposition'],bounded_verdict='PASS_SOURCE_COMPOSITION_ONLY',blocking_source_findings=[],original_awards=[],effect_grant=False,actual_new_host_qualified=False,operational_readiness=False,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exact_subject=dict(branch=s['branch'],phase_root=str(PHASES/'finish'),finish_phase_bytes=len(C.read(PHASES/'finish/PHASE.json')),finish_phase_sha256=BINDINGS['finish'][1],payload_count=59,run_sha256=sha(run_body),expected_git_tree=EXPECTED,source_commit=PRODUCT,source_tree=BASE_TREE,sole_parent=PRODUCT,complete_files=1815,public_tree_additions=49,total_bytes=CHECKS['publication']['total_bytes'],selected_prospective_images=[x['facts']['image_version'] for x in profiles]),actual_root_roles=roles,root_issuance_records={'ROOT_SOURCE_ISSUANCE.json':pin(PHASES/'ROOT_SOURCE_ISSUANCE.json'),'ANCHOR_RECEIVING.json':pin(ANCHOR)},phase_bindings={n:pin(PHASES/n/'PHASE.json') for n in BINDINGS},source_binding=pin(old.AUTHOR/'SOURCE_ADOPTION.json'),prior_evidence_reused=dict(whole_host_source_review=pin(PRIOR/'FINAL.json'),whole_host_source_review_manifest=pin(PRIOR/'MANIFEST.json'),review_driver=pin(PRIOR/'review.py'),scope='Source51 and all generated Python function/class AST match G131. Original52/34 source controls and preflight30 remain reused at original scopes without replay; no host/native or operational credit transfers.'),actual_checks=CHECKS,source_acceptance_findings=['No blocking source findings in exact G132 finish.','Original phase readers accepted physical 26/44/59 populations; original prepare/bind/finish reproduced every byte in memory with phase writer forbidden.','Six fresh selection bindings, actual Root CORE/canonical A03/A04, old-byte refusal controls and recorded empty parentless anchors join. Pretty A03 remains preserved and unselected.','Original pin-closure and independent recursive-tree checks bind 1815 members/49 additions to the expected tree and sole e76 parent.','All generated functions, three Ubuntu24/Python3.12.3 exact-tool profiles, native89/original scope and 75min/600s/45s limits remain unchanged.'],execution_effects=dict(in_memory_pure_recomputation=True,phase_writer_replayed=False,source_writes=False,repository_writes=False,environment_probes=False,native=False,provider=False,crypto=False,key_access=False,privilege=False,root_island=False,root_role_issuance=False,full_product_reexecution=False,new_agents=False),reviewed_runtime_state='Frozen source and pure original assembly only; actual host, sender, callback readiness and native behavior unqualified.',maintained_receiver_contract=dict(owner=pin(old.FACTORY),check='Original final_bind.collect review and exact-subject predicates executed on this actual FINAL and finish bytes. Full collect and Root offline receiving not executed or synthesized.'),state_machine_notes=dict(stable_id='G1-FINITE-HOST-PROFILE',prior_discovery=previous['state_machine_notes']['prior_discovery'],source_transition='prepare -> actual canonical A03 -> bind -> actual A04 -> finish -> independent source receiving -> separate Root receiving/decision',dimensions='Source identity, role issuance, immutable composition, review, provider publication, live readiness and native acceptance are separate.',canonical_admission_discovery='Existing original bind_carrier requires exact canonical bytes as well as parsed body; preserved pretty A03 is unselected and refuses. Enforcement verified by original consumer. No new registry entry proposed for this already explicit adequately verified guard.',registry_disposition='Existing repository registry reference observed; no registry write authority. Root/Sol retain registry and live transition ownership.',failure_recovery='Reject stale roles, changed phase members/tree/run. Preserve G131 sender/publication UNKNOWN_NO_REPLAY; no old grant/cipher/recipient/journal reuse, no absence or cleanup inference.'),unresolved_operational_gates=['Root alone owns offline receiving, publication and acceptance; this return grants no effects.','Root records tools/carrier anchors published and host/G3 unpublished; this reviewer made no provider read and grants no fresh-ref currentness.','Actual subsequent factory71/interface151 and their physical joins await generation and receiving in this same lane; unchanged cases will not replay.','Actual callback/sender readiness, runtime-parent checks and fresh live authorization remain separate Root gates.','G131 sender/publication remains UNKNOWN_NO_REPLAY; no old grant/cipher/recipient/journal reuse and no no-effect inference.','Original G1/G3/native/L04 awards remain empty. G220 Ubuntu26 is outside this review.'])
 write('FINAL.json',final)
 owner_ast=ast.parse(C.read(old.FACTORY));collect=next(n for n in owner_ast.body if isinstance(n,ast.FunctionDef) and n.name=='collect')
 a=next(i for i,n in enumerate(collect.body) if assigned(n,'review'));z=next(i for i,n in enumerate(collect.body) if assigned(n,'root'))
 excerpt=ast.Module(body=collect.body[a:z],type_ignores=[])
 code=compile(ast.fix_missing_locations(excerpt),str(old.FACTORY)+'#collect-review-contract','exec')
 def consume(body):
  ns=dict(parse=C.parse,need=C.need,desc=C.desc,evidence={'host_review':body},PHASE_SHA=BINDINGS['finish'][1],TREE=EXPECTED,SOURCE=PRODUCT,CORE=CORE,out={'phase/'+n:v for n,v in f.items()})
  exec(code,ns)
 consume(C.read(OUT/'FINAL.json'))
 negative={}
 for field in ('finish_phase_sha256','expected_git_tree','run_sha256'):
  bad=copy.deepcopy(final);bad['exact_subject'][field]=previous['exact_subject'][field]
  negative[field]=reject(lambda:consume(C.encode(bad)),'STALE_REVIEW_NOT_REFUSED_'+field)
 write('CONTRACT_CHECK.json',dict(schema='dg16.actual-review-contract-predicate-check.v1',result='PASS',owner=pin(old.FACTORY),final=pin(OUT/'FINAL.json'),phase=pin(PHASES/'finish/PHASE.json'),run_sha256=sha(run_body),predicate_source_sha256=sha(ast.dump(excerpt,include_attributes=False).encode()),full_collect_executed=False,stale_subject_controls=negative,reason='Original review predicates only; no Root offline/export/transport evidence synthesized.'))
 manifest=dict(schema='dg16.g1-current05-whole-host-source-review-manifest.v1',authority='NONE',reviewer='/root/g132_binding_review',disposition=final['disposition'],effect_grant=False,original_awards=[],member_count=4,members={n:desc(C.read(OUT/n)) for n in ('review.py','CHECKS.json','FINAL.json','CONTRACT_CHECK.json')},self_excluded='MANIFEST.json')
 write('MANIFEST.json',manifest)
 for n,row in manifest['members'].items():need(desc(C.read(OUT/n))==row,'FINAL_READBACK_'+n)
 print(json.dumps(dict(final=pin(OUT/'FINAL.json'),manifest=pin(OUT/'MANIFEST.json'),checks=pin(OUT/'CHECKS.json'),contract=pin(OUT/'CONTRACT_CHECK.json'),blocking_source_findings=[]),sort_keys=True))
if __name__=='__main__':
 try:run()
 except Exception as e:
  write('CHECK_FAILURE.json',dict(exception_type=type(e).__name__,code=str(e),completed_checks=CHECKS))
  raise
