"""Pure public acquisition journal/control source preparation. No tool or I/O calls.

Root's actual dispatcher must persist each transition in a private write-once
journal, authenticate native tool history, and obtain a fresh operator admission
before any SourceRoot write or tool/body call. JSON matching authenticates none.
"""
import ast,copy,datetime,hashlib,io,json,re,stat,types,urllib.parse,zipfile
from pathlib import PurePosixPath
ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
TOOL='mcp__codex_apps__github_fetch'
DOWNLOAD='mcp__codex_apps__github_download_workflow_artifact'
ORDER=('run','attempt','jobs','commit','workflow','artifacts','download','body','closing-run','closing-artifacts')
TOOL_MAX=4*1024**2
JOURNAL_MAX=32*1024**2
PINS={'root_acquire.py':'c4eca6f66708215aac994faa9fef1e253466f8898f17a4a612b4e0ec0d1d5c23',
 'root_common.py':'f4e2f07b78d4f9acd13f75882ee5faea411a904485a5fbb1c103b49c063615b8',
 'public_receiver.py':'6731aa0e20f7414326d0c93ef258dd1bd84d38cd900b01a4101ff6007bb4ecbe',
 'prepare_live_control.py':'93ae48d79b76c6775179a500107c90d24173a2fbc189182c6543a07e87a31b4f',
 'shared_broker.py':'827d4c32a2d5be3d48bdc370fdfe3df763cb7b8792421092294e3e9c65c5fbed'}
INSTALLATION_PIN='23fcaf940f2b51d321731d56fbdd217adf032a033a9cdbaca340607d468c5239'
RECEIVER_SEAL_PIN='2f86492f085eae40ab35530fe1d59773116841c120b5a9bd50421e5bdf02275d'
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return dict(bytes=len(b),sha256=sha(b))
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def parse(raw,maximum=TOOL_MAX):
 need(type(raw) is bytes and 0<len(raw)<=maximum,'PUBLIC_DATA_BOUND')
 def pairs(rows):
  d={}
  for k,v in rows:need(k not in d,'DUPLICATE_KEY');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
def integer(v,lo=0,hi=2**63-1):return type(v) is int and lo<=v<=hi
def digest(v):need(type(v) is str and re.fullmatch('[0-9a-f]{64}',v),'DIGEST');return True
def selected(raw,functions,env,constants=(),classes=False):
 nodes=[]
 for n in ast.parse(raw).body:
  if isinstance(n,ast.FunctionDef) and n.name in functions:nodes.append(n)
  elif classes and isinstance(n,ast.ClassDef):nodes.append(n)
  elif isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in constants for t in n.targets):nodes.append(n)
 m=types.ModuleType('pure_public_definitions');m.__dict__.update(env)
 exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<exact-pure-public-owner>','exec'),m.__dict__);return m

def installation_configuration(installation_raw,receiver_seal_raw,public_binding_raw,runtime_raw):
 """Join exact Root-received installation data; no physical probe or grant."""
 need(sha(installation_raw)==INSTALLATION_PIN and sha(receiver_seal_raw)==RECEIVER_SEAL_PIN,'ACTUAL_ROOT_INSTALLATION_PINS')
 installed=parse(installation_raw);seal=parse(receiver_seal_raw);b=parse(public_binding_raw);runtime=parse(runtime_raw)
 need(installed['issuer_thread']==seal['issuer_thread']==runtime['issuer_thread']==ISSUER and installed['effect_grant'] is False
  and installed['actual_verified']['native_execution'] is False and installed['private_binding'] is None,'SOURCE_ONLY_INSTALLED_PUBLIC_ROLE')
 rows={r['path']:r for r in seal['members']};need(seal['member_count']==len(rows)==7,'ACTUAL_SEVEN_PUBLIC_FILES')
 need(desc(public_binding_raw)=={k:rows['BINDING.json'][k] for k in ('bytes','sha256')}
  and desc(runtime_raw)=={k:rows['SUCCESSOR_RUNTIME_BINDING.json'][k] for k in ('bytes','sha256')},'ACTUAL_INSTALLED_BINDING_RUNTIME')
 need(b['final_tree']==seal['final_tree']==installed['actual_verified']['final_tree'] and b['session']==runtime['session']==ISSUER
  and installed['installed']['sha256']==RECEIVER_SEAL_PIN and installed['actual_verified']['receiver_seal']==RECEIVER_SEAL_PIN,'ACTUAL_INSTALLED_SOURCE_JOIN')
 root=runtime['workspace_root']+'/bound-public-receiver';need(installed['installed']['root']==root,'ACTUAL_RECEIVED_PUBLIC_DIRECTORY')
 return dict(issuer_thread=ISSUER,receiver_directory=root,receiver_seal_sha256=RECEIVER_SEAL_PIN,
  public_binding_sha256=sha(public_binding_raw),runtime_sha256=sha(runtime_raw),final_tree=b['final_tree'],
  actual_Root_installation_receipt_sha256=INSTALLATION_PIN,physical_probe_performed=False,effect_grant=False,
  actual_combined_review=installed['actual_combined_review'],actual_run=installed['actual_run'])

class PublicOperator:
 @classmethod
 def from_received_installation(cls,sources,binding,installation_raw,receiver_seal_raw,public_binding_raw,runtime_raw):
  configuration=installation_configuration(installation_raw,receiver_seal_raw,public_binding_raw,runtime_raw)
  need(binding['public_binding']==parse(public_binding_raw),'CONFIGURED_PUBLIC_BINDING_CHANGED')
  result=cls(sources,binding,parse(runtime_raw));result.actual_installation=configuration;return result
 def __init__(self,sources,binding,runtime):
  need(type(sources) is dict and set(sources)==set(PINS),'PUBLIC_SOURCE_POPULATION')
  for n,h in PINS.items():need(type(sources[n]) is bytes and sha(sources[n])==h,'FROZEN_PUBLIC_SOURCE_'+n)
  self.sources=dict(sources);self.binding=copy.deepcopy(binding);self.runtime=copy.deepcopy(runtime)
  binding=self.binding;runtime=self.runtime;self.b=self.binding['public_binding']
  need(binding['issuer_thread']==runtime['issuer_thread']==runtime['session']==self.b['session']==ISSUER
   and self.b['authority']=='NONE' and self.b['effect_authority'] is False and self.b['original_acceptance'] is False
   and runtime['private_custody_ready'] is False and runtime['effect_grant'] is False,'PUBLIC_ONLY_NATIVE_ROOT_CONTEXT')
  need(binding['provider_actor']=='theislampill' and binding['provider_actor_id']=='266501826','FIXED_PROVIDER_ACTOR')
  self.K=types.SimpleNamespace(need=need,parse=parse,encode=encode,desc=desc,sha=sha,integer=integer,digest=digest,
   SOURCE_COMMIT=self.b['source_commit'],ROLE_CAPS={'live':400000,'terminal':400000,'cipher':269574168},METADATA_MAX=TOOL_MAX,
   AUTH='ACTUAL_NATIVE_ROOT_TOOL_HISTORY_AND_INDEPENDENT_RECEIVING_REQUIRED')
  def context(c):
   need(type(c) is dict and set(c)==set('repository branch run_id run_attempt workflow_commit source_commit source_tree workflow_path job_name'.split()),'PUBLIC_CONTEXT_FIELDS')
   for k in ('repository','branch','source_commit','source_tree'):need(c[k]==self.b[k],'PUBLIC_CONTEXT_'+k)
   need(type(c['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',c['run_id']) and type(c['run_attempt']) is int and c['run_attempt']==1
    and type(c['workflow_commit']) is str and re.fullmatch('[0-9a-f]{40}',c['workflow_commit']) and c['workflow_commit']!='0'*40
    and c['workflow_path']=='.github/workflows/dg16-r5-full-g2.yml' and c['job_name']=='full-registry-raw-pair','PUBLIC_CONTEXT_SCOPE')
  self.K.context=context
  common=selected(sources['root_common.py'],{'artifact_name'},self.K.__dict__)
  self.K.artifact_name=common.artifact_name
  self.A=selected(sources['root_acquire.py'],{'endpoint','unwrap','artifacts','download_reference','unix_ms','verify_snapshot'},
   {'K':self.K,'need':need,'parse':parse,'encode':encode,'desc':desc,'datetime':datetime,'hashlib':hashlib,'re':re,'urllib':urllib,'ORDER':tuple(x for x in ORDER if x!='body')})
  # Exact shared wrapper function, with G2-only endpoints/kinds. No G1 Store,
  # Client, dispatcher, public receiver surface or private profile is imported.
  P=types.SimpleNamespace(need=need,digest=digest,MAX_METADATA=TOOL_MAX)
  V=types.SimpleNamespace(json_body=parse,workflow_endpoint=lambda c:self.A.endpoint(c,'workflow'),
   supported_workflow=lambda body,raw,c,h:self.A.unwrap(raw,self.A.endpoint(c,'workflow'),'workflow',{'workflow_sha256':h}))
  self.U=selected(sources['shared_broker.py'],{'unwrap_tool_result'},{'P':P,'V':V,'TOOL_MAX':TOOL_MAX,
   'KINDS':('run','attempt','jobs','commit','workflow','artifacts')})
  self.R=selected(sources['public_receiver.py'],{'need','sha','encode','strict','expected_names','decode_zip'},
   {'hashlib':hashlib,'json':json,'io':io,'zipfile':zipfile,'stat':stat},constants={'NAMES'})
 def plan(self,context,role,now_ms,operator_admission_reference):
  self.K.context(context);need(role in ('live','terminal'),'PUBLIC_ROLE_ONLY')
  need(integer(now_ms) and type(operator_admission_reference) is str and 0<len(operator_admission_reference)<=256,'ROOT_OPERATOR_ADMISSION_REFERENCE_REQUIRED')
  return dict(schema='dg16.public-only-acquisition-source-plan.v1',authority='NONE',issuer_thread=ISSUER,
   binding=desc(encode(self.binding)),context=copy.deepcopy(context),role=role,opened_ms=now_ms,expires_ms=now_ms+300000,
   operator_admission_reference=operator_admission_reference,session_directory=self.runtime['receiver_output_root']+'/'+role,
   entries=[],pending=None,status='SOURCE_PLAN_REQUIRES_NATIVE_ROOT_ADMISSION',automatic_retry=False)
 def _check(self,state,now,require_window=True):
  need(integer(now) and state['opened_ms']<=now and (not require_window or now<state['expires_ms']) and state['expires_ms']==state['opened_ms']+300000,'PUBLIC_300S_WINDOW_EXPIRED')
  need(state['binding']==desc(encode(self.binding)) and state['issuer_thread']==ISSUER and state['role'] in ('live','terminal')
   and state['automatic_retry'] is False and state['status']!='REFUSED_NO_RETRY','PUBLIC_PLAN_CHANGED_OR_REFUSED')
  self.K.context(state['context'])
  for i,e in enumerate(state['entries']):
   need(i<len(ORDER) and e['kind']==ORDER[i] and e['reservation']['ordinal']==e['intent']['ordinal']==e['receiving']['ordinal']==i
    and e['receiving']['reservation']==desc(encode(e['reservation'])) and e['receiving']['intent']==desc(encode(e['intent']))
    and e['receiving']['actual_tool_result']==desc(e['tool_result']) and e['receiving']['complete_native_history']==desc(e['history'])
    and e['parsed']==self._decode(state,e['kind'],e['intent'],e['tool_result']),'PUBLIC_JOURNAL_CHAIN_CHANGED')
 def _selected(self,state):
  rows={e['kind']:e['parsed'] for e in state['entries'] if e['kind'] in ORDER[:6]}
  item,joins=self.A.verify_snapshot(rows,state['context'],state['role'],self.b,state['last_result_ms'])
  self._actors(rows);return item,joins
 def _actors(self,rows):
  for kind in ('run','attempt'):
   actor=rows[kind].get('actor',{});need(actor.get('login')==self.binding['provider_actor'] and str(actor.get('id'))==self.binding['provider_actor_id'],'ACTUAL_PROVIDER_ACTOR')
 def _decode(self,state,kind,intent,raw):
  if kind=='body':
   item,_=self._selected(state);need(desc(raw)=={'bytes':item['size_in_bytes'],'sha256':item['digest'][7:]},'ACTUAL_PUBLIC_ZIP_DIGEST');self.R.decode_zip(raw,state['role']);return {'archive':desc(raw)}
  if kind=='download':
   safe,_ephemeral=self.A.download_reference(raw,intent['arguments']['artifact_id'],intent['arguments']['file_name']);return safe
  value=parse(raw);meta=value.get('_meta',{});need(type(meta) is dict and set(meta)<={'truncated','isTruncated','partial','hasMore'} and all(type(v) is bool and not v for v in meta.values()),'COMPLETE_TOOL_META')
  key='run' if kind=='closing-run' else 'artifacts' if kind=='closing-artifacts' else kind
  _,parsed=self.U.unwrap_tool_result(raw,intent['arguments']['url'],kind=key,context=state['context'],workflow_sha256=self.binding['workflow_sha256']);return parsed
 def reserve(self,state,now):
  self._check(state,now);need(state['pending'] is None,'UNCERTAIN_ORDINAL_NO_RETRY');i=len(state['entries']);need(i<len(ORDER),'PUBLIC_SESSION_COMPLETE')
  retained=sum(len(e['tool_result'])+len(e['history']) for e in state['entries']);need(retained+2*TOOL_MAX+65536<=JOURNAL_MAX,'PUBLIC_JOURNAL_RESERVATION_BOUND')
  kind=ORDER[i];c=state['context']
  if kind in ('download','body'):
   item,_=self._selected(state);args={'repo_full_name':c['repository'],'artifact_id':item['id'],'file_name':self.K.artifact_name(state['role'],c)+'.zip'}
   tool=DOWNLOAD if kind=='download' else None
  else:tool=TOOL;args={'url':self.A.endpoint(c,kind)}
  receipt=dict(schema='dg16.public-only-call-reservation.v1',authority='NONE',ordinal=i,kind=kind,tool=tool,arguments=args,
   reserved_ms=now,expires_ms=state['expires_ms'],automatic_retry=False,actual_native_history_required=True)
  new=copy.deepcopy(state);new['pending']={'phase':'RESERVED','reservation':receipt};return new,receipt
 def intent(self,state,now,persistence):
  self._check(state,now);p=state['pending'];need(p is not None and p['phase']=='RESERVED','RESERVATION_BEFORE_INTENT')
  need(type(persistence) is dict and persistence.get('issuer_thread')==ISSUER and persistence.get('reservation')==desc(encode(p['reservation']))
   and persistence.get('native_root_persisted') is True,'ACTUAL_ROOT_DURABILITY_RECEIPT_REQUIRED')
  intent=dict(p['reservation'],intent_ms=now,reservation_sha256=sha(encode(p['reservation'])),persistence_receipt=desc(encode(persistence)))
  new=copy.deepcopy(state);new['pending'].update(phase='INTENT',intent=intent);return new,intent
 def result(self,state,tool_result,history,history_join,now):
  self._check(state,now,require_window=False);p=state['pending'];need(p is not None and p['phase']=='INTENT','INTENT_BEFORE_ACTUAL_RESULT')
  need(type(tool_result) is bytes and 0<len(tool_result)<=TOOL_MAX and type(history) is bytes and 0<len(history)<=TOOL_MAX,'COMPLETE_TOOL_AND_HISTORY_BOUND')
  new=copy.deepcopy(state);q=new['pending'];q.update(tool_result=tool_result,history=history,history_join=copy.deepcopy(history_join),phase='RESULT');intent=p['intent'];kind=intent['kind']
  try:
   need(now<state['expires_ms'],'PUBLIC_300S_WINDOW_EXPIRED')
   need(history_join.get('tool')==intent['tool'] and history_join.get('arguments')==intent['arguments']
    and history_join.get('tool_result_sha256')==sha(tool_result) and history_join.get('history_sha256')==sha(history)
    and type(history_join.get('tool_call_ref')) is str and re.fullmatch('[A-Za-z0-9_-]{1,160}',history_join['tool_call_ref']),'NATIVE_TOOL_HISTORY_JOIN')
   q['parsed']=self._decode(state,kind,intent,tool_result)
  except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
   new['status']='REFUSED_NO_RETRY';q['refusal']='PUBLIC_TOOL_HISTORY_WRAPPER_OR_BODY_REFUSED'
  new['last_result_ms']=now;return new
 def receive_result(self,state,now):
  self._check(state,now);p=state['pending'];need(p is not None and p['phase']=='RESULT' and 'parsed' in p,'RESULT_BEFORE_RECEIVING')
  need(p['parsed']==self._decode(state,p['intent']['kind'],p['intent'],p['tool_result']),'PENDING_RESULT_BODY_CHANGED')
  receipt=dict(schema='dg16.public-only-ordinal-receiving.v1',authority='NONE',ordinal=p['intent']['ordinal'],kind=p['intent']['kind'],
   reservation=desc(encode(p['reservation'])),intent=desc(encode(p['intent'])),actual_tool_result=desc(p['tool_result']),
   complete_native_history=desc(p['history']),tool_call_ref=p['history_join']['tool_call_ref'],received_ms=now,
   external_history_authentication_required=True,automatic_retry=False)
  new=copy.deepcopy(state);entry=dict(p,kind=p['intent']['kind'],receiving=receipt);new['entries'].append(entry);new['pending']=None;return new,receipt
 def receive_public(self,state,now):
  self._check(state,now);need(state['pending'] is None and len(state['entries'])==len(ORDER),'ALL_PUBLIC_ORDINALS_REQUIRED')
  item,joins=self._selected(state);rows={e['kind']:e for e in state['entries']}
  opening=rows['run']['parsed'];closing=rows['closing-run']['parsed']
  for k in ('id','run_attempt','head_sha','head_branch','event','path','status','conclusion','actor'):need(closing.get(k)==opening.get(k),'CLOSING_PUBLIC_RUN_CHANGED')
  need(rows['closing-artifacts']['parsed']==rows['artifacts']['parsed'],'CLOSING_PUBLIC_ARTIFACT_LIST_CHANGED')
  archive=rows['body']['tool_result'];need(desc(archive)=={'bytes':item['size_in_bytes'],'sha256':item['digest'][7:]},'PUBLIC_BODY_CHANGED')
  metadata=dict(run=opening,commit=rows['commit']['parsed'],artifact=item)
  receipt=dict(schema='dg16.public-only-provider-data-receiving.v1',authority='NONE',context=state['context'],role=state['role'],
   archive=desc(archive),joins=joins,ordinal_receipts=[e['receiving'] for e in state['entries']],
   authentication_boundary='ACTUAL_NATIVE_ROOT_TOOL_HISTORY_AND_INDEPENDENT_RECEIVING_REQUIRED',private_or_cipher_received=False,automatic_retry=False,original_awards=[])
  return {'ARTIFACT.zip':archive,'PUBLIC_METADATA.json':encode(metadata),'PROVIDER_RECEIVING.json':encode(receipt)}
 def journal_records(self,state):
  """Private write-once byte records for Root's existing native writer only.

  This does not write or authenticate them. Preserve full wrapper/history bytes
  separately; signed download references must never be echoed or published.
  """
  plan={k:v for k,v in state.items() if k not in ('entries','pending','last_result_ms','status')}
  plan['status']='SOURCE_PLAN_REQUIRES_NATIVE_ROOT_ADMISSION'
  records={'PLAN.json':encode(plan)}
  entries=list(state['entries'])+([state['pending']] if state['pending'] is not None else [])
  for i,e in enumerate(entries):
   prefix='%02d.'%i;records[prefix+'RESERVATION.json']=encode(e['reservation'])
   if 'intent' in e:records[prefix+'INTENT.json']=encode(e['intent'])
   if 'tool_result' in e:records[prefix+'TOOL_RESULT']=e['tool_result']
   if 'history' in e:records[prefix+'NATIVE_HISTORY']=e['history']
   if 'receiving' in e:records[prefix+'RECEIVING.json']=encode(e['receiving'])
  if state['status']=='REFUSED_NO_RETRY':records['REFUSED.json']=encode(dict(authority='NONE',status='REFUSED_NO_RETRY',automatic_retry=False))
  need(len(records)<=64 and sum(map(len,records.values()))<=JOURNAL_MAX,'PUBLIC_PRIVATE_JOURNAL_EXPORT_BOUND')
  return records
 def control_source(self,receiver_directory,public_binding_raw):
  if hasattr(self,'actual_installation'):
   need(receiver_directory==self.actual_installation['receiver_directory'] and sha(public_binding_raw)==self.actual_installation['public_binding_sha256'],'RECEIVED_INSTALLATION_CONTROL_PIN')
  root=PurePosixPath(self.runtime['workspace_root']);receiver=PurePosixPath(receiver_directory)
  need(receiver.is_absolute() and '..' not in receiver.parts and receiver!=root and receiver.is_relative_to(root)
   and not any(receiver.is_relative_to(root/n) for n in ('candidate','source','composition','public-receiving')),'FRESH_ACTUAL_BOUND_RECEIVER_DIRECTORY_REQUIRED')
  need(parse(public_binding_raw)==self.b and self.b.get('composition_path')==str(root/'composition'),'ACTUAL_PUBLIC_BINDING_AND_COMPOSITION_REQUIRED')
  raw=self.sources['prepare_live_control.py'];lines=raw.decode().splitlines(keepends=True);edits=[]
  values={'ROOT':'Path('+repr(str(root))+')','HERE':'ROOT','RECEIVER':'Path('+repr(str(receiver))+')','COMPOSITION':'ROOT/\'composition\'',
   'LIVE':'Path('+repr(self.runtime['receiver_output_root']+'/live')+')','OUT':'ROOT/\'public-control-preparation\''}
  for n in ast.parse(raw).body:
   if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in values:
    name=n.targets[0].id;edits.append((n.lineno-1,n.end_lineno,name+' = '+values[name]+'\n'))
  need(len(edits)==len(values),'EXACT_PUBLIC_CONTROL_RUNTIME_ASSIGNMENTS')
  for start,end,text in sorted(edits,reverse=True):lines[start:end]=[text]
  raw=''.join(lines)
  def once(before,after):
   nonlocal raw
   need(raw.count(before)==1,'EXACT_PUBLIC_CONTROL_SOURCE_ANCHOR');raw=raw.replace(before,after)
  once("    raise ValueError('FINAL_RECEIVER_BINDING_REQUIRED')\n",'')
  once("'current_control_branch_absence_received','automatic_replay'}","'current_control_branch_absence_received','automatic_replay','issuer_thread','session','independent_reviewer'}")
  once("'dg16.current-g2.actual-root-live-decision-input.v1'","'dg16.current-g2.public-root-live-decision-input.v2'")
  once("    verify_seal(RECEIVER, selected['receiver_seal_sha256'])", "    assert selected['issuer_thread'] == selected['session'] == "+repr(ISSUER)+"\n    assert selected['independent_reviewer'] != "+repr(self.binding['source_author'])+"\n    verify_seal(RECEIVER, selected['receiver_seal_sha256'])")
  once("    binding, composition, _gate, modules, _catalog, _manifest = R.verified()", "    assert R.BINDING_SHA == "+repr(sha(public_binding_raw))+"\n    binding, composition, _gate, modules, _catalog, _manifest = R.verified()")
  once("review['reviewer'] == '/root/g2_cold_review'", "review['reviewer'] == selected['independent_reviewer']")
  result=raw.encode();ast.parse(result);return result
