#!/usr/bin/env python3
"""Finite held job. Receives actual independent review and root GO; creates neither."""
import argparse
import ctypes
import importlib.util
import os
from pathlib import Path
import re
import stat
import sys
import time
import urllib.request

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('h0_held_io',HERE/'host_io.py');H=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(H)
HOLD_SECONDS=1500
DRIVER_SECONDS=900
REMOTE='https://github.com/'+H.REPOSITORY+'.git'
CODE_NAMES=frozenset(('held_control.py','host_io.py','native_driver.py','live_receiver.py','mechanical_driver.py','native_transport.py','provider.py','host_utility.py','INPUT_TEMPLATE.json','PLAN.json','CONTROL_FORMAT.md','REPORT.md','PURE_CONTROLS.json'))
PREPARED_NAMES=frozenset(('host_io.py','native_driver.py','live_receiver.py','mechanical_driver.py','native_transport.py','provider.py','INPUT_MANIFEST.json','PLAN.json','HOST_CHECK.json','CONTROL_FORMAT.md'))
CONTROL_NAMES=frozenset(('CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_GO.json'))
ALLOCATIONS=['fresh-isolated-subject-and-fixture-commit','fresh-controller','owned-native-binary-copy','one-loopback-emulated-provider','one-native-app-server','one-necessary-compact-resume','existing-external-host-store','existing-canonical-OPEN','seven-actual-MCP-occurrences','existing-live-reader-receiving','bounded-cleanup']

def git(args,cwd,missing=False):
 code,out,err=H.command(['/usr/bin/git',*args],cwd,timeout=30,maximum=65536)
 if missing and code:return None
 H.need(code==0,'PUBLIC_GIT_READ_REFUSED');return out

def bundle(work):
 worker=work/'worker';H.need(HERE==worker/H.RELATIVE,'ADAPTER_LOCATION')
 raw=H.read(HERE/'BUNDLE_SEAL.json');value=H.parse(raw);names=set()
 H.need(value.get('schema')=='r5.h0-held-code-seal.v1','BUNDLE_SEAL_SCHEMA')
 for row in value['files']:
  name=row['name'];H.need(type(name) is str and name not in names and name in CODE_NAMES|{'dg18-isolated-h0-20261106-02.yml'},'BUNDLE_MEMBER_POPULATION');names.add(name)
  path=worker/H.WORKFLOW if name=='dg18-isolated-h0-20261106-02.yml' else HERE/name
  pin,_,_=H.pin(path,4*1024*1024);H.need(all(pin[k]==row[k] for k in ('bytes','sha256','mode')),'BUNDLE_MEMBER_CHANGED')
 H.need(names==CODE_NAMES|{'dg18-isolated-h0-20261106-02.yml'},'BUNDLE_MEMBER_POPULATION')
 return H.sha(raw),value

def source_checkpoint(work,workflow_commit):
 worker=work/'worker'
 H.need(git(['rev-parse','HEAD'],worker).decode().strip()==workflow_commit,'WORKFLOW_COMMIT_CHANGED')
 row=git(['rev-list','--parents','-n','1','HEAD'],worker).decode().strip().split();H.need(len(row)==2 and row[0]==workflow_commit,'ONE_SOURCE_PARENT_REQUIRED');source=row[1]
 H.need(source==H.SOURCE_COMMIT,'EXACT_PUBLISHED_SOURCE_COMMIT_REQUIRED')
 H.need(git(['rev-parse',source+'^{tree}'],worker).decode().strip()==H.SOURCE_TREE,'EXACT_SOURCE_TREE_REQUIRED')
 parents=git(['rev-list','--parents','-n','1',source],worker).decode().strip().split();H.need(parents==[source,H.SOURCE_PARENT],'SOURCE_ANCESTRY_REQUIRED')
 changed=git(['diff-tree','--no-commit-id','--name-only','-r',source,workflow_commit],worker).decode().splitlines()
 expected={H.RELATIVE+'/'+n for n in CODE_NAMES|{'BUNDLE_SEAL.json'}}|{H.WORKFLOW}
 H.need(set(changed)==expected and len(changed)==len(expected),'PUBLIC_DELTA_POPULATION')
 H.need(git(['status','--porcelain=v1','--untracked-files=no'],worker)==b'','WORKFLOW_TRACKED_SOURCE_CHANGED')
 return source

def download(work):
 path=work/'codex-official.tar.gz';deadline=time.monotonic()+360
 with urllib.request.urlopen(H.ARCHIVE_URL,timeout=30) as response,path.open('xb') as output:
  H.need(response.geturl()==H.ARCHIVE_URL,'ARCHIVE_REDIRECT');size=0
  while True:
   H.need(time.monotonic()<deadline,'ARCHIVE_DOWNLOAD_WATCHDOG');block=response.read(1048576)
   if not block:break
   size+=len(block);H.need(size<=H.ARCHIVE_BYTES,'ARCHIVE_BYTE_BOUND');output.write(block)
  output.flush();os.fsync(output.fileno())
 actual,_,_=H.pin(path);H.need(actual['bytes']==H.ARCHIVE_BYTES and actual['sha256']==H.ARCHIVE_SHA,'OFFICIAL_ARCHIVE_PIN');return actual

def prepare(work,run_id,attempt,workflow_commit):
 H.need(type(run_id) is str and re.fullmatch('[0-9]{1,20}',run_id) and attempt=='1','FIRST_RUN_ATTEMPT_ONLY')
 H.need(type(workflow_commit) is str and re.fullmatch('[0-9a-f]{40}',workflow_commit),'WORKFLOW_COMMIT_FORMAT')
 seal_sha,seal=bundle(work);source=source_checkpoint(work,workflow_commit);archive=download(work);template=H.parse(H.read(HERE/'INPUT_TEMPLATE.json'))
 H.need(template['source_tree']==H.SOURCE_TREE and template['source_parent']==H.SOURCE_PARENT,'INPUT_SOURCE_BINDING')
 members=[]
 for row in template['runtime']:
  actual,_,_=H.pin(work/'worker'/row['source_relative'],4*1024*1024)
  H.need(all(actual[k]==row[k] for k in ('bytes','sha256','mode')),'SOURCE_INPUT_CHANGED')
  members.append({k:v for k,v in row.items() if k!='source_relative'}|{'path':actual['path']})
 members.append({'key':'official-binary-archive','category':'official-archive',**archive})
 for name,invocation in (('python3','/usr/bin/python3'),('git','/usr/bin/git'),('bash','/usr/bin/bash')):
  chain=H.invocation(invocation);actual,_,_=H.pin(chain['resolved']);members.append({'key':'system/'+name,'category':'system-runtime','invocation':invocation,**actual})
 for row in seal['files']:
  name=row['name'];path=work/'worker'/H.WORKFLOW if name=='dg18-isolated-h0-20261106-02.yml' else HERE/name
  actual,_,_=H.pin(path,4*1024*1024);members.append({'key':'code/'+name,'category':'reviewed-code',**actual})
 actual,_,_=H.pin(HERE/'BUNDLE_SEAL.json');members.append({'key':'code/BUNDLE_SEAL.json','category':'reviewed-code',**actual})
 H.need(len(members)==len(template['runtime'])+5+len(seal['files']) and sum(r['bytes'] for r in members)<=256*1024*1024,'INPUT_POPULATION_OR_TOTAL_BOUND')
 manifest={'schema':'r5.h0-held-input-manifest.v1','source_commit':source,'source_tree':H.SOURCE_TREE,'source_parent':H.SOURCE_PARENT,'controller':H.CONTROLLER,'subject':str(work/'private/subject'),'members':members}
 H.write(work/'INPUT_MANIFEST.json',manifest);custody=H.census(manifest)
 for name in PREPARED_NAMES-{'INPUT_MANIFEST.json','HOST_CHECK.json'}:H.write(work/name,H.read(HERE/name))
 system=[r for r in custody['members'] if r['key'].startswith('system/')]
 H.write(work/'HOST_CHECK.json',{'schema':'r5.h0-prepare-host-metadata.v1','source_commit':source,'source_tree':H.SOURCE_TREE,'runtime_input_count':len(template['runtime']),'total_input_count':len(members),'system':system,'actual_native_executed':False,'currentness_established':False,'review_or_GO_created':False,'authority':'NONE'})
 files=[]
 for name in sorted(PREPARED_NAMES):
  raw=H.read(work/name);files.append({'name':name,'bytes':len(raw),'sha256':H.sha(raw)})
 preparation={'schema':'r5.h0-sealed-host-preparation.v1','authority':'NONE','source_commit':source,'source_tree':H.SOURCE_TREE,'input_manifest_sha256':H.sha(H.read(work/'INPUT_MANIFEST.json')),'files':files}
 H.write(work/'SEALED_PREPARATION.json',preparation)
 request={'schema':'r5.h0-held-host-request.v1','repository':H.REPOSITORY,'workflow_branch':H.BRANCH,'run_id':run_id,'run_attempt':'1','workflow_commit':workflow_commit,'source_commit':source,'source_parent':H.SOURCE_PARENT,'source_tree':H.SOURCE_TREE,'bundle_seal_sha256':seal_sha,'preparation_sha256':H.sha(H.read(work/'SEALED_PREPARATION.json')),'input_manifest_sha256':preparation['input_manifest_sha256'],'input_custody_sha256':H.sha(H.encode(custody)),'input_count':len(members),'subject':str(work/'private/subject'),'controller':H.CONTROLLER,'owned_binary':str(work/'private/binary/codex'),'allocations':ALLOCATIONS,'control_branch':H.CONTROL_BRANCH,'control_path':'qualification/dg18-isolated-h0-control-20261106-02/'+run_id+'-1','hold_seconds':HOLD_SECONDS,'execution_seconds':DRIVER_SECONDS,'execution_authorized':False,'currentness_established':False,'original_acceptance':False}
 H.write(work/'HOST_REQUEST.json',request)
 identities={name:H.pin(work/name,4*1024*1024)[1] for name in PREPARED_NAMES|{'SEALED_PREPARATION.json','HOST_REQUEST.json'}}
 state={'schema':'r5.h0-held-private-state.v1','request_sha256':H.sha(H.read(work/'HOST_REQUEST.json')),'input_custody':custody,'identities':identities,'deadline_monotonic_ns':time.monotonic_ns()+HOLD_SECONDS*1000000000}
 H.write(work/'HOST_STATE.json',state,mode=0o400)
 check(work,state,request)
 code,out,err=H.command(['/usr/bin/python3','-I','-B',HERE/'native_driver.py','--work',work,'--prepare-check'],work,timeout=120,maximum=65536)
 H.write(work/'prepare-check.stdout',out);H.write(work/'prepare-check.stderr',err);H.need(code==0 and not err and H.parse(out)=={'status':'PURE_PREPARATION_CHECK_PASS','authority':'NONE'},'PURE_PREPARATION_CHECK_REFUSED')
 check(work,state,request)
 public=work/'public-preparation';public.mkdir(mode=0o700)
 for name in PREPARED_NAMES|{'SEALED_PREPARATION.json','HOST_REQUEST.json'}:H.write(public/name,H.read(work/name),mode=0o644)
 print('{"status":"PREPARED_WAITING_ACTUAL_REVIEW_AND_ROOT_GO","execution_authorized":false}',flush=True)

def check(work,state,request):
 H.need(time.monotonic_ns()<state['deadline_monotonic_ns'],'HOLD_EXPIRED')
 raw=H.read(work/'HOST_REQUEST.json');H.need(H.sha(raw)==state['request_sha256'] and H.parse(raw)==request,'HELD_REQUEST_CHANGED')
 H.need(bundle(work)[0]==request['bundle_seal_sha256'] and source_checkpoint(work,request['workflow_commit'])==request['source_commit'],'HELD_CODE_CHANGED')
 for name,identity in state['identities'].items():H.need(H.pin(work/name,4*1024*1024)[1]==identity,'HELD_PREPARATION_IDENTITY_CHANGED')
 manifest=H.parse(H.read(work/'INPUT_MANIFEST.json'));H.need(H.sha(H.read(work/'INPUT_MANIFEST.json'))==request['input_manifest_sha256'],'HELD_MANIFEST_CHANGED')
 H.need(H.sha(H.encode(state['input_custody']))==request['input_custody_sha256'] and H.census(manifest)==state['input_custody'],'HELD_INPUT_CUSTODY_CHANGED')
 public=work/'public-preparation'
 if public.exists():
  H.need(set(q.name for q in public.iterdir())==PREPARED_NAMES|{'SEALED_PREPARATION.json','HOST_REQUEST.json'},'PUBLIC_PREPARATION_POPULATION')
  for q in public.iterdir():H.need(H.read(q)==H.read(work/q.name),'PUBLIC_PREPARATION_CHANGED')
 H.need(time.monotonic_ns()<state['deadline_monotonic_ns'],'HOLD_EXPIRED')

def control_head(work):
 raw=git(['ls-remote','--exit-code','--refs',REMOTE,'refs/heads/'+H.CONTROL_BRANCH],work,missing=True)
 if raw is None:return None
 lines=raw.decode().splitlines();H.need(len(lines)==1,'CONTROL_REF_POPULATION');parts=lines[0].split('\t');H.need(len(parts)==2 and re.fullmatch('[0-9a-f]{40}',parts[0]) and parts[1]=='refs/heads/'+H.CONTROL_BRANCH,'CONTROL_REF_SHAPE');return parts[0]

def controls(work,commit,request):
 cache=work/'control.git';git(['--git-dir',str(cache),'fetch','--quiet','--no-tags','--depth=1',REMOTE,commit],work)
 prefix=request['control_path'];raw=git(['--git-dir',str(cache),'ls-tree',commit+':'+prefix],work,missing=True)
 if raw is None:return None
 names=[]
 for line in raw.decode().splitlines():
  fields=line.split('\t');H.need(len(fields)==2 and re.fullmatch('100644 blob [0-9a-f]{40}',fields[0]),'CONTROL_BLOB_REQUIRED');names.append(fields[1])
 H.need(len(names)==len(set(names)) and set(names) in ({'CONTROL.json'},CONTROL_NAMES),'CONTROL_FILE_POPULATION');payload={}
 for name in names:
  ref=commit+':'+prefix+'/'+name;size=int(git(['--git-dir',str(cache),'cat-file','-s',ref],work));H.need(0<size<=65536,'CONTROL_FILE_BOUND');raw=git(['--git-dir',str(cache),'show',ref],work);H.need(len(raw)==size,'CONTROL_FILE_CHANGED');payload[name]=raw
 return payload

def validate(payload,request_raw):
 request=H.parse(request_raw);value=H.parse(payload['CONTROL.json'])
 expected={'schema':'r5.h0-held-control.v1','publisher':'/root','repository':H.REPOSITORY,'run_id':request['run_id'],'run_attempt':'1','workflow_commit':request['workflow_commit'],'host_request_sha256':H.sha(request_raw),'preparation_sha256':request['preparation_sha256'],'input_custody_sha256':request['input_custody_sha256']}
 H.need(type(value) is dict and set(value)==set(expected)|{'decision','files'} and H.matches(value,expected),'CONTROL_BINDING')
 H.need(value['decision'] in ('GO','STOP'),'CONTROL_DECISION')
 if value['decision']=='STOP':H.need(set(payload)=={'CONTROL.json'} and value['files']=={},'STOP_POPULATION');return 'STOP',None
 H.need(set(payload)==CONTROL_NAMES and set(value['files'])==CONTROL_NAMES-{'CONTROL.json'},'GO_POPULATION')
 for name in CONTROL_NAMES-{'CONTROL.json'}:H.need(value['files'][name]=={'bytes':len(payload[name]),'sha256':H.sha(payload[name])},'CONTROL_AUTHORIZATION_PIN')
 review=H.parse(payload['INDEPENDENT_REVIEW.json']);go=H.parse(payload['ROOT_GO.json'])
 fixed={'schema':'r5.h0-independent-host-review.v1','decision':'PASS','blocking_findings':[],'host_request_sha256':H.sha(request_raw),'preparation_sha256':request['preparation_sha256']}
 H.need(H.matches(review,fixed) and H.independent_reviewer(review.get('reviewer')),'INDEPENDENT_REVIEW_SCOPE')
 fixed={'schema':'r5.h0-root-go.v1','author':'/root','decision':'GO','one_shot':True,'host_request_sha256':H.sha(request_raw),'preparation_sha256':request['preparation_sha256'],'input_custody_sha256':request['input_custody_sha256'],'subject':request['subject'],'controller':H.CONTROLLER,'source_commit':request['source_commit'],'source_tree':H.SOURCE_TREE,'review_sha256':H.sha(payload['INDEPENDENT_REVIEW.json']),'allocations':ALLOCATIONS}
 H.need(H.matches(go,fixed),'ROOT_GO_SCOPE');return 'GO',H.sha(payload['ROOT_GO.json'])

def execute_once(work,state,request,payload,commit,go_sha):
 check(work,state,request)
 H.write(work/'DISPATCH_RESERVED.json',{'one_shot':True,'automatic_retry':False,'control_commit':commit,'go_sha256':go_sha},mode=0o400)
 for name in CONTROL_NAMES-{'CONTROL.json'}:H.write(work/name,payload[name],mode=0o400)
 utility=H.load(HERE/'host_utility.py','h0_outer_owned_child_utility')
 H.need(H.sha(H.read(HERE/'host_utility.py'))=='429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c','EXACT_CLEANUP_UTILITY')
 libc=ctypes.CDLL(None,use_errno=True);libc.prctl.argtypes=[ctypes.c_int,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong];libc.prctl.restype=ctypes.c_int
 H.need(libc.prctl(36,1,0,0,0)==0 and utility.children()==[],'EXCLUSIVE_SUBREAPER_REQUIRED')
 records=[];code=None
 try:
  code,out,err=utility.capture('h0-native-episode',['/usr/bin/python3','-I','-B',str(HERE/'native_driver.py'),'--work',str(work),'--execute','--go-sha256',go_sha],records,time.monotonic()+DRIVER_SECONDS+10,seconds=DRIVER_SECONDS)
  H.write(work/'native-driver.stdout',out);H.write(work/'native-driver.stderr',err)
 except BaseException as exc:
  captured=getattr(exc,'captured',None)
  if captured is not None:H.write(work/'native-driver.stdout',captured['stdout']);H.write(work/'native-driver.stderr',captured['stderr'])
  raise
 finally:H.write(work/'OUTER_CAPTURE.json',{'returncode':code,'records':records,'automatic_retry':False})
 H.need(code==0,'NATIVE_DRIVER_FAILED_NO_RETRY')
 H.write(work/'DISPATCH_FINISHED.json',{'returncode':code,'cleanup_echild':records[-1]['cleanup']['echild'],'control_commit':commit,'automatic_retry':False},mode=0o400)

def hold(work):
 request_raw=H.read(work/'HOST_REQUEST.json');request=H.parse(request_raw);state=H.parse(H.read(work/'HOST_STATE.json'));check(work,state,request)
 git(['init','--bare','--quiet',str(work/'control.git')],work);seen=set();notice=0
 while time.monotonic_ns()<state['deadline_monotonic_ns']:
  commit=control_head(work)
  if commit and commit not in seen:
   seen.add(commit);payload=controls(work,commit,request)
   if payload is not None:
    decision,go_sha=validate(payload,request_raw);H.need(decision=='GO','ROOT_STOP')
    check(work,state,request);code,out,err=H.command(['/usr/bin/python3','-I','-B',HERE/'native_driver.py','--work',work,'--prepare-check'],work,timeout=120,maximum=65536)
    H.write(work/'predispatch-check.stdout',out);H.write(work/'predispatch-check.stderr',err);H.need(code==0 and not err and H.parse(out)=={'status':'PURE_PREPARATION_CHECK_PASS','authority':'NONE'},'PREDISPATCH_CHECK_REFUSED')
    check(work,state,request);H.need(control_head(work)==commit,'CONTROL_HEAD_CHANGED');execute_once(work,state,request,payload,commit,go_sha);return
  if time.monotonic()>notice:print('{"status":"WAITING_ACTUAL_REVIEW_AND_ROOT_GO","execution_authorized":false}',flush=True);notice=time.monotonic()+120
  remaining=(state['deadline_monotonic_ns']-time.monotonic_ns())/1e9
  if remaining>0:time.sleep(min(30,remaining))
 raise H.Refusal('HOLD_EXPIRED')

def summary(work):
 output=work/'public-result';output.mkdir(mode=0o700)
 result={'schema':'r5.h0-held-public-result.v1','authority':'OBSERVATION_ONLY','status':'NO_RECEIVED_RESULT','original_acceptance':False,'authentic_OR':False,'independent_cognition':False,'formal_governor_decision':False,'public_RETURN':False,'public_JOIN':False,'old_pending_consumed':False,'automatic_retry':False,'raw_evidence_published':False}
 try:
  request_raw=H.read(work/'HOST_REQUEST.json');request=H.parse(request_raw);state=H.parse(H.read(work/'HOST_STATE.json'))
  H.need(type(request) is dict and type(request.get('preparation_sha256')) is str and re.fullmatch('[0-9a-f]{64}',request['preparation_sha256']) and state['request_sha256']==H.sha(request_raw) and H.pin(work/'HOST_REQUEST.json')[1]==state['identities']['HOST_REQUEST.json'],'SUMMARY_REQUEST_BINDING')
  result.update(preparation_sha256=request['preparation_sha256'],request_sha256=H.sha(request_raw))
  result['dispatch_reserved']=(work/'DISPATCH_RESERVED.json').is_file()
  # Progress contains only closed phase names and completed milestone flags.
  # It is atomically replaced, preserving the last complete observation if the
  # driver is terminated during its next checkpoint write.
  try:
   progress=H.parse(H.read(work/'PROGRESS.json',16384));go_raw=H.read(work/'ROOT_GO.json',65536)
   fixed={'schema':'r5.h0-closed-progress.v1','host_request_sha256':H.sha(request_raw),'go_sha256':H.sha(go_raw),'source_tree':H.SOURCE_TREE,'authority':'NONE'}
   H.need(H.matches(progress,fixed) and set(progress)==set(fixed)|{'phase','phase_completed','completed','failure_phase','failure_code','mcp_failure'},'SUMMARY_PROGRESS_BINDING')
   H.need(type(progress['phase']) is str and progress['phase'] in H.PROGRESS_PHASES and type(progress['phase_completed']) is bool,'SUMMARY_PROGRESS_PHASE')
   H.need(type(progress['completed']) is dict and set(progress['completed'])<=H.PROGRESS_PHASES and all(type(v) is bool and v is True for v in progress['completed'].values()),'SUMMARY_PROGRESS_COMPLETED')
   H.need(progress['failure_phase'] is None or type(progress['failure_phase']) is str and progress['failure_phase'] in H.PROGRESS_PHASES,'SUMMARY_FAILURE_PHASE')
   H.need(progress['failure_code'] is None or type(progress['failure_code']) is str and progress['failure_code'] in H.FAILURE_CODES,'SUMMARY_FAILURE_CODE')
   H.need((progress['failure_phase'] is None)==(progress['failure_code'] is None),'SUMMARY_FAILURE_PAIR')
   result.update(native_driver_started=True,phase=progress['phase'],phase_completed=progress['phase_completed'],completed_milestones=progress['completed'],failure_phase=progress['failure_phase'],failure_code=progress['failure_code'])
   # The diagnostic is validated separately so malformed new data cannot erase
   # an otherwise valid primary phase/failure or publish partial receipt facts.
   try:
    if progress['mcp_failure'] is not None:
     diagnostic=H.validate_mcp_failure(progress['mcp_failure'])
     H.need(progress['failure_phase'] is not None and diagnostic['phase']==progress['failure_phase'],'SUMMARY_DIAGNOSTIC_PHASE')
     result['mcp_failure']=diagnostic
   except (OSError,ValueError,TypeError,KeyError,H.Refusal):pass
  except (OSError,ValueError,TypeError,KeyError,H.Refusal):pass
  try:
   capture=H.parse(H.read(work/'OUTER_CAPTURE.json',65536));rows=capture['records'];H.need(type(rows) is list and len(rows)==1,'SUMMARY_OUTER_POPULATION');row=rows[0]
   H.need(type(row) is dict and row.get('name')=='h0-native-episode' and type(row.get('process_started')) is bool,'SUMMARY_OUTER_SCOPE')
   result['native_driver_started']=row['process_started']
   if type(row.get('returncode')) is int and -65536<=row['returncode']<=65536:result['native_driver_returncode']=row['returncode']
   if row['process_started']:
    H.need(type(row['cleanup']['echild']) is bool,'SUMMARY_OUTER_CLEANUP');result['outer_cleanup_echild']=row['cleanup']['echild']
  except (OSError,ValueError,TypeError,KeyError,H.Refusal):pass
  # Closed private command metadata can explain the last completed helper
  # without exposing command arguments, source records or diagnostic text.
  try:
   commands=H.parse(H.read(work/'private/evidence/COMMANDS.json',1024*1024))
   H.need(type(commands) is list and 0<len(commands)<=128,'SUMMARY_COMMAND_COUNT')
   last=commands[-1];H.need(type(last) is dict and type(last.get('returncode')) is int and -65536<=last['returncode']<=65536,'SUMMARY_COMMAND_STATUS')
   row={'completed_commands':len(commands),'last_returncode':last['returncode']}
   for key in ('stdout_sha256','stderr_sha256'):
    H.need(type(last.get(key)) is str and re.fullmatch('[0-9a-f]{64}',last[key]),'SUMMARY_COMMAND_DIGEST');row['last_'+key]=last[key]
   result.update(row)
  except (OSError,ValueError,TypeError,KeyError,H.Refusal):pass
  receiving=H.parse(H.read(work/'private/evidence/MECHANICAL_RECEIVING.json',65536))
  fixed={'schema':'r5.h0-existing-reader-receiving.v1','status':'EXISTING_READER_SEVEN_OCCURRENCES_RECEIVED','authority':'NONE','source_commit':request['source_commit'],'source_tree':H.SOURCE_TREE,'public_return':None,'public_join':None,'formal_governor_decision':False,'independent_cognition':False,'authentic_OR':False,'original_acceptance':False,'old_archive_or_pending_used':False}
  H.need(H.matches(receiving,fixed),'SUMMARY_RECEIVING_SCOPE')
  projection={}
  for key in ('selected_occurrence_count','strict_prior_revision','original_and_retry_distinct','reader_agrees_with_producer','canonical_open_reread_unchanged','pending_unconsumed'):
   expected=7 if key=='selected_occurrence_count' else True;H.need(type(receiving.get(key)) is type(expected) and receiving[key]==expected,'SUMMARY_RECEIVING_PREDICATE');projection[key]=expected
  for key in ('mechanical_result_sha256','received_export_sha256','go_sha256'):
   H.need(type(receiving.get(key)) is str and re.fullmatch('[0-9a-f]{64}',receiving[key]),'SUMMARY_RECEIVING_DIGEST');projection[key]=receiving[key]
  go_raw=H.read(work/'ROOT_GO.json',65536);go=H.parse(go_raw)
  H.need(H.sha(go_raw)==receiving['go_sha256'] and H.matches(go,{'schema':'r5.h0-root-go.v1','author':'/root','decision':'GO','one_shot':True,'host_request_sha256':H.sha(request_raw),'preparation_sha256':request['preparation_sha256']}),'SUMMARY_EXACT_GO')
  projection['status']='MECHANICAL_RECEIVED_CLEANUP_UNCONFIRMED';result.update(projection)
  final=H.parse(H.read(work/'DISPATCH_FINISHED.json',65536));H.need(type(final) is dict and type(final.get('returncode')) is int and final['returncode']==0 and final.get('cleanup_echild') is True,'SUMMARY_CLEANUP')
  result['status']='MECHANICAL_RECEIVED_PENDING_ROOT_RECONCILIATION';result['cleanup_echild']=True
 except (OSError,ValueError,TypeError,KeyError,H.Refusal):pass
 raw=H.encode(result);H.need(len(raw)<=4096,'PUBLIC_SUMMARY_BYTE_BOUND');H.write(output/'PUBLIC_RESULT.json',raw,mode=0o644)
 print('{"status":"PUBLIC_ALLOWLIST_WRITTEN","raw_evidence_published":false}',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('prepare','hold','public-summary'));p.add_argument('--work',required=True,type=Path);p.add_argument('--run-id');p.add_argument('--run-attempt');p.add_argument('--workflow-commit');a=p.parse_args();work=a.work
 H.need(work.is_absolute() and work.resolve(strict=True)==work and work.is_dir() and work.stat().st_uid==os.getuid() and stat.S_IMODE(work.stat().st_mode)==0o700,'PRIVATE_WORK_REQUIRED')
 if a.mode=='prepare':prepare(work,a.run_id,a.run_attempt,a.workflow_commit)
 elif a.mode=='hold':hold(work)
 else:summary(work)
if __name__=='__main__':
 try:main()
 except BaseException:print('{"status":"H0_HELD_ADAPTER_REFUSED","automatic_retry":false,"authority":"NONE"}',flush=True);raise SystemExit(1)
