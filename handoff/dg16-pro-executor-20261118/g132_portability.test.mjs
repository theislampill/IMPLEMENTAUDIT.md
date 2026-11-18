/* Synthetic qualification only. GitHub, Root authority and original G1/G3 are
 * fixtures; local process/file/TTY boundaries run on the actual Linux host. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import crypto from 'node:crypto';

const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../..');
const reportArg=process.argv.indexOf('--report');
const reportPath=reportArg>=0?path.resolve(process.argv[reportArg+1]):null;
const parent=reportPath?path.dirname(reportPath):os.tmpdir();fs.mkdirSync(parent,{recursive:true});
const root=fs.mkdtempSync(path.join(parent,'g132-fixture-'));fs.chmodSync(root,0o700);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const desc=b=>({bytes:Buffer.byteLength(b),sha256:sha(b)});
const codecPath=path.join(repo,'qualification/dg16-github-evidence/channel.js');
const bridgePath=path.join(here,'g132_operator_bridge.js');
const hostPath=path.join(here,'g132_linux_host.py');
const received={codec:fs.readFileSync(codecPath),bridge:fs.readFileSync(bridgePath),host:fs.readFileSync(hostPath),test:fs.readFileSync(fileURLToPath(import.meta.url))};
const codec=eval(received.codec.toString('utf8'));
const factory=eval(received.bridge.toString('utf8'));
let nextId=1,processCalls=0;const processes=new Map(),testRows=[];
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function drain(row){const output=row.output;row.output='';return row.exit===undefined?
  {output,session_id:row.id}:{output,exit_code:row.exit};}
async function observed(row){await wait(20);return drain(row);}
const processTools={
  async exec_command(a){processCalls++;let child;
    if(a.tty)child=spawn('/usr/bin/script',['-qec',a.cmd,'/dev/null'],{stdio:['pipe','pipe','pipe']});
    else child=spawn('/bin/bash',['-c',a.cmd],{stdio:['pipe','pipe','pipe']});
    const row={id:nextId++,child,output:'',exit:undefined};processes.set(row.id,row);
    child.stdout.on('data',b=>row.output+=b.toString('utf8'));
    child.stderr.on('data',b=>row.output+=b.toString('utf8'));
    child.on('close',code=>row.exit=code??1);
    return observed(row);
  },
  async write_stdin(a){const row=processes.get(a.session_id);assert.ok(row,'only actual owned test process');
    if(a.chars)row.child.stdin.write(a.chars);return observed(row);},
};
const allCalls=[];
function toolkit(provider=async(name,args)=>({content:[],structuredContent:{sha:(name.includes('create_tree')?'3':name.includes('create_commit')?'4':'1').repeat(40)},isError:false})){
  const tools={...processTools};for(const name of ['fetch','fetch_file','create_blob','create_tree','create_commit','update_ref']){
    const full='mcp__codex_apps__github_'+name;tools[full]=async args=>{allCalls.push({name:full,args});return provider(full,args);};
  }return tools;
}
let run=7000;
function spec(role,extra={}){const now=Date.now();return {schema:'dg16.pro-functions-operator.v1',role,
  context:{repository:'theislampill/IMPLEMENTAUDIT.md',run_id:String(++run),run_attempt:1,
    workflow_commit:'a'.repeat(40),source_commit:'b'.repeat(40),source_tree:'c'.repeat(40),
    workflow_path:'.github/workflows/dg16-r5-g1-hosted-episode.yml'},
  actor:{surface:'ChatGPT-functions',controller:'fixture-current-root',continuity_receipt:'fixture-receipt-only',assignment_ref:'FIXTURE_ONLY'},
  operator_source:{commit:'d76c1e9c22fd816fbc6ddcac0080625b8f087d23',index_sha256:'17efb4b30df56a5a97bc3a9a72579478a3b4850a15e544c0e76a1374116056cf'},
  issued_ms:now-10,expires_ms:now+590000,...extra};}
function permit(check=()=>true,noReplay=()=>true){return async scope=>({authorization:{ref:'FIXTURE_ONLY_NOT_A_GRANT',sha256:'d'.repeat(64)},
  assertCurrent:check,assertNoReplay:noReplay});}
function bridge(tools=toolkit(),suffix='journal'){
  const journal=fs.mkdtempSync(path.join(root,suffix+'-'));fs.chmodSync(journal,0o700);
  return {api:factory({tools,codec,linux:{python_path:'/usr/bin/python3',helper_path:hostPath,
    helper_sha256:sha(received.host),journal_root:journal}}),journal};
}
async function test(name,fn){const began=Date.now();try{await fn();testRows.push({name,status:'PASS',elapsed_ms:Date.now()-began});}
  catch(error){testRows.push({name,status:'FAIL',elapsed_ms:Date.now()-began,message:String(error)});throw error;}}
const dispatcherSource=String.raw`import base64,hashlib,json,pathlib,sys
p=pathlib.Path(__file__).with_suffix('.state.json')
def out(v): print(json.dumps(v,separators=(',',':')))
def save(v):p.write_text(json.dumps(v))
def d(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
cfg=json.loads(pathlib.Path(__file__).with_suffix('.config.json').read_text());a=sys.argv[1:];op=a[0]
if op=='initialize':
 assert not p.exists();save({'ordinal':0,'body':''});out({'status':'INITIALIZED'})
else:
 s=json.loads(p.read_text());i=int(a[1]) if len(a)>1 else 18
 if op=='ready':assert i==s['ordinal'];out({'status':'READY'})
 elif op=='reserve':
  assert i==s['ordinal'] and not s.get('reserved');s['reserved']=True;save(s)
  tails=['/actions/runs/'+cfg['run_id'],'/actions/runs/'+cfg['run_id']+'/attempts/1','/actions/runs/'+cfg['run_id']+'/attempts/1/jobs?per_page=100&page=1','/actions/runs/'+cfg['run_id']+'/artifacts?per_page=100','/actions/runs/'+cfg['run_id']+'/artifacts?per_page=100','/contents/'+cfg['workflow_path']+'?ref='+cfg['workflow_commit']]
  url='https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md'+tails[i%6]
  if cfg.get('bad_url'):url+='-foreign'
  out({'status':'RESERVED_ONCE','remaining_ms':500000,'logical_tool_call_ref':'fixture-'+str(i),'plan':{'ordinal':i,'tool':'mcp__codex_apps__github_fetch','arguments':{'url':url},'intent_sha256':'e'*64}})
 elif op=='chunk':
  old=base64.b64decode(s['body']);assert int(a[2])==len(old);b=old+base64.b64decode(a[3]);s['body']=base64.b64encode(b).decode();save(s);out({'status':'CHUNK_RETAINED',**d(b)})
 elif op=='complete':
  b=base64.b64decode(s['body']);assert len(b)==int(a[2]) and d(b)['sha256']==a[3] and a[4]=='e'*64 and b.endswith(b'\n');assert type(json.loads(b)['isError']) is bool
  out({'status':'ACTUAL_FULL_RESULT_RETAINED','receipt':{'logical_tool_call_ref':'fixture-'+str(i)}})
 elif op=='publish':
  s={'ordinal':i+1,'body':''};save(s);out({'status':'PUBLISHED','ordinal':i,'broker_status':'RECEIVED','fetch_permitted':False})
 elif op=='finish':assert s['ordinal']==18;out({'status':'DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE','fixture_only':True})
 else:raise AssertionError('unknown fixture operation')
`;
function dispatcher(s,bad=false){const dir=fs.mkdtempSync(path.join(root,'dispatcher-'));const file=path.join(dir,'entry.py');
 fs.writeFileSync(file,dispatcherSource,{mode:0o400});fs.writeFileSync(path.join(dir,'entry.config.json'),JSON.stringify({...s.context,bad_url:bad}),{mode:0o600});
 return {path:file,descriptor:desc(dispatcherSource)};}
const senderCaps=d=>({dispatcher:d,startSender:async()=>({status:'FIXTURE_STARTED',automatic_retry:false}),
  receiveSenderTerminal:async()=>({status:'FIXTURE_TERMINAL',fixture_only:true,original_awards:[]})});

const publicationSource=String.raw`import hashlib,json,os,pathlib,select,sys,termios,time
root=pathlib.Path(sys.argv[1]);cfg=json.loads((root/'config.json').read_text());repo='theislampill/IMPLEMENTAUDIT.md'
def enc(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def d(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def emit(v):print(enc(v).decode(),end='',flush=True)
def frame():
 attr=termios.tcgetattr(0);attr[3]&=~(termios.ECHO|termios.ICANON);attr[6][termios.VMIN]=1;attr[6][termios.VTIME]=0;termios.tcsetattr(0,termios.TCSANOW,attr)
 print('READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME',flush=True)
 end=time.monotonic()+5;header=b''
 while not header.endswith(b'\n'):
  assert time.monotonic()<end
  if select.select([0],[],[],.1)[0]:header+=os.read(0,1)
 n=int(header);assert 0<n<=4194304;b=b''
 while len(b)<n:
  assert time.monotonic()<end
  if select.select([0],[],[],.1)[0]:b+=os.read(0,n-len(b))
 return b
calls=[('create_blob',{'repository_full_name':repo,'content':'SYNTHETIC_CONTROL','encoding':'utf-8'}),('create_blob',{'repository_full_name':repo,'content':'U1lOVEhFVElDX05PX0NSWVBUTw==','encoding':'base64'}),('create_tree',{'repository_full_name':repo,'tree_elements':[{'path':'CONTROL.json','mode':'100644','type':'blob','sha':'1'*40},{'path':'INPUTS.cms','mode':'100644','type':'blob','sha':'1'*40}]}),('create_commit',{'repository_full_name':repo,'tree_sha':'3'*40,'parent_sha':'5'*40,'message':'FIXTURE_ONLY'}),('update_ref',{'repository_full_name':repo,'branch_name':cfg['branch'],'sha':'4'*40,'expected_sha':('6' if cfg.get('bad_parent') else '5')*40,'force':False})]
api='https://api.github.com/repos/'+repo
if cfg.get('control'):
 calls=calls[2:];calls[0][1]['tree_elements']=[{'path':name,'mode':'100644','type':'blob','content':'FIXTURE_ONLY'} for name in ['CONTROL.json','INPUTS.cms']]
calls.extend([('fetch',{'url':api+'/git/ref/heads/'+cfg['branch']}),('fetch',{'url':api+'/git/commits/'+'4'*40}),('fetch',{'url':api+'/git/trees/'+'3'*40+('?recursive=1' if cfg.get('control') else '')}),('fetch_file',{'repository_full_name':repo,'path':'CONTROL.json','ref':'4'*40,'encoding':'base64'}),('fetch_file',{'repository_full_name':repo,'path':'INPUTS.cms','ref':'4'*40,'encoding':'base64'}),('fetch',{'url':api+'/git/ref/heads/'+cfg['branch']})])
if cfg.get('extra_read'):calls.append(calls[-1])
for n,(tool,args) in enumerate(calls):
 kind='CALL'+str(n);body=enc(args);ap=root/(('OTHER' if cfg.get('relocated_argument') else kind)+'.ARGUMENTS.json');ap.write_bytes(body);ap.chmod(cfg.get('argument_mode',0o600));now=int(time.time()*1000)
 intent={'schema':'dg16.binary-publication-exclusive-intent.v1','authority':'NONE','kind':kind,'tool':'mcp__codex_apps__github_'+tool,'arguments':d(body),'arguments_path':str(ap),'expires_unix_ms':cfg['deadline'],'frame_started_unix_ms':now,'frame_deadline_unix_ms':min(now+45000,cfg['deadline']),'automatic_retry':False}
 if cfg.get('expired_origin'):intent['frame_started_unix_ms']=now-50000;intent['frame_deadline_unix_ms']=now+20000
 if cfg.get('control'):intent={'schema':'dg16.root-control-exclusive-'+('call' if n<3 else 'read')+'-intent.v1','authority':'NONE','kind':kind,'ordinal':n,'call':{'tool':'mcp__codex_apps__github_'+tool,'arguments':args},'deadline_unix_ms':cfg['deadline'],'frame_deadline_unix_ms':min(now+45000,cfg['deadline']),'automatic_retry':False,'actual_native_history_required':True}
 iraw=enc(intent);ip=root/(kind+'.INTENT.json');ip.write_bytes(iraw);ip.chmod(0o600)
 emit({'event':'intent','intent':intent,'intent_sha256':d(iraw)['sha256'],'intent_path':str(ip)})
 raw=frame();assert isinstance(json.loads(raw)['isError'],bool);emit({'event':'retained','kind':kind,'actual_result':d(raw)})
emit({'event':'complete','receipt':{'authority':'NONE','fixture_only':True,'original_awards':[],'root_tool_history_authentication_required':True}})
`;
function pubSource(s,api,bad=false,extra={}){const dir=fs.mkdtempSync(path.join(root,'publication-'));fs.chmodSync(dir,0o700);
 const file=path.join(dir,'producer.py');fs.writeFileSync(file,publicationSource,{mode:0o400});
 fs.writeFileSync(path.join(dir,'config.json'),JSON.stringify({branch:s.publication.branch,deadline:s.expires_ms,bad_parent:bad,control:s.publication.writes===3,...extra}),{mode:0o600});
 return api.framedProcess({path:file,sha256:sha(publicationSource),args:[dir],exchange_root:dir,deadline_ms:s.expires_ms});}
function pubSpec(){return spec('publication',{publication:{kind:'CONTROL_DATA_ONLY',branch:'engineering/g132-fixture-only',parent_sha:'5'.repeat(40),writes:5,reads:6,paths:['CONTROL.json','INPUTS.cms']}});}

try{
 await test('factory is inert and Linux identity is actual',async()=>{const before=processCalls;const {api}=bridge();assert.equal(processCalls,before);
  const observed=await api.observeHost();assert.equal(observed.stable.platform,'linux');assert.equal(observed.stable.uid,process.getuid());
  assert.equal(observed.native_model_identity,'NOT_OBSERVED');});
 await test('public observation has one exact provider read and no sender/G3 callback',async()=>{const {api}=bridge();const s=spec('public-observation'),before=allCalls.length;
  const result=await api.observePublic(s,permit());assert.equal(result.status,'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING');
  assert.equal(allCalls.length-before,1);assert.equal(result.result.qualification,'PUBLIC_READ_TRANSPORT_SMOKE_ONLY');
  assert.equal(result.result.sender_invoked,false);assert.equal(result.result.g3_invoked,false);});
 await test('300000 ms floor refuses before sender/tool call',async()=>{const {api}=bridge();const s=spec('sender',{expires_ms:Date.now()+299999});let starts=0;
  const count=allCalls.length;const result=await api.sender(s,permit(),{...senderCaps(dispatcher(s)),startSender:async()=>{starts++;}});
  assert.equal(result.status,'REFUSED_BEFORE_OPERATION');assert.equal(starts,0);assert.equal(allCalls.length,count);});
 await test('JSON labels cannot replace current admission or no-replay capabilities',async()=>{const {api}=bridge();let starts=0;const s=spec('sender');const caps={...senderCaps(dispatcher(s)),startSender:async()=>{starts++;}};
  for(const admit of [null,async()=>({authorization:{ref:'label',sha256:'d'.repeat(64)},assertCurrent:true}),permit(()=>true,()=>false)]){
   const result=await api.sender(s,admit,caps);assert.equal(result.status,'REFUSED_BEFORE_OPERATION');}
  assert.equal(starts,0);});
 await test('18 original sender reads through actual Linux helper protocol',async()=>{const {api}=bridge();const s=spec('sender');const before=allCalls.length;
  const result=await api.sender(s,permit(),senderCaps(dispatcher(s)));assert.equal(result.status,'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING');
  assert.equal(result.result.sender_reads,18);assert.equal(result.original_acceptance,false);assert.equal(allCalls.length-before,18);
  for(let i=0;i<18;i++)assert.equal(allCalls[before+i].args.url,api.endpoint(s.context,i));
  const replay=await api.sender({...s,actor:{...s.actor,controller:'another-label'}},permit(),senderCaps(dispatcher(s)));
  assert.equal(replay.status,'REFUSED_BEFORE_OPERATION');assert.equal(allCalls.length-before,18);});
 await test('foreign sender endpoint refuses with no provider call',async()=>{const {api}=bridge();const s=spec('sender'),before=allCalls.length;
  const result=await api.sender(s,permit(),senderCaps(dispatcher(s,true)));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length,before);});
 await test('revocation preserves returned-result descriptor and stops',async()=>{const {api,journal}=bridge();const s=spec('sender'),before=allCalls.length;
  const result=await api.sender(s,permit(({action})=>!(action.kind==='sender-read'&&action.phase==='after-return')),senderCaps(dispatcher(s)));
  assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length-before,1);
  assert.ok(fs.existsSync(path.join(journal,result.subject_key,'001.RESULT.json')));assert.ok(fs.existsSync(path.join(journal,result.subject_key,'UNKNOWN.json')));});
 await test('truncated actual tool wrapper cannot reach the sender consumer',async()=>{const {api}=bridge(toolkit(async()=>({content:[],structuredContent:{},isError:false,_meta:{truncated:true}})));
  const s=spec('sender'),before=allCalls.length;const result=await api.sender(s,permit(),senderCaps(dispatcher(s)));
  assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length-before,1);});
 await test('dispatcher symlink refuses before provider invocation',async()=>{const {api}=bridge();const s=spec('sender'),d=dispatcher(s),alias=d.path+'.alias';fs.symlinkSync(d.path,alias);
  const before=allCalls.length;const result=await api.sender(s,permit(),senderCaps({...d,path:alias}));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length,before);});
 await test('five writes and six readbacks through actual local TTY frames',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api));assert.equal(result.status,'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING');
  assert.equal(allCalls.length-before,11);assert.equal(result.result.calls,11);assert.equal(result.native_history_authenticated,false);
  const update=allCalls[before+4];assert.equal(update.args.expected_sha,'5'.repeat(40));assert.equal(update.args.force,false);});
 await test('publication expected-old mismatch stops before ref call',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api,true));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length-before,4);
  assert.ok(!allCalls.slice(before).some(x=>x.name.endsWith('update_ref')));});
 await test('three-write control source uses exact recursive tree readback',async()=>{const {api}=bridge();const s=pubSpec();s.publication.writes=3;const before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api));assert.equal(result.status,'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING');
  assert.equal(allCalls.length-before,9);assert.equal(allCalls[before+5].args.url,'https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/git/trees/'+'3'.repeat(40)+'?recursive=1');});
 await test('extra read from source cannot exceed admitted call population',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api,false,{extra_read:true}));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length-before,11);});
 await test('original frame start prevents refreshing an expired frame',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api,false,{expired_origin:true}));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length,before);});
 await test('publicly readable argument file refuses before provider call',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api,false,{argument_mode:0o644}));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length,before);});
 await test('renamed argument file cannot replace exact intent sibling',async()=>{const {api}=bridge();const s=pubSpec(),before=allCalls.length;
  const result=await api.publish(s,permit(),pubSource(s,api,false,{relocated_argument:true}));assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(allCalls.length,before);});
 await test('protected host launch ref is outside the adapter publication profile',async()=>{const {api}=bridge();const s=pubSpec();s.publication.branch='pro/dg16-g1-original-g3-32-20261114';let started=0;
  const result=await api.publish(s,permit(),{start:async()=>{started++;},next:async()=>{},respond:async()=>{},selection:{deadline_ms:s.expires_ms}});
  assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(started,0);});
 await test('live Root decision and separate G3 consumption use exact actual bytes',async()=>{const {api}=bridge();const s=spec('g3',{stage:'components'}),order=[];
  const request={raw:JSON.stringify({schema:'FIXTURE_ONLY_REQUEST',run:s.context.run_id})};const decision={raw:JSON.stringify({schema:'FIXTURE_ONLY_DECISION',request_sha256:sha(request.raw)})};
  const result=await api.consumeG3(s,permit(),{readRequest:async()=>{order.push('read');return request;},validateRequest:async()=>{order.push('validate-request');return {request_sha256:sha(request.raw)};},decide:async()=>{order.push('decide');return decision;},validateDecision:async()=>{order.push('validate-decision');return {request_sha256:sha(request.raw),decision_sha256:sha(decision.raw)};},consume:async value=>{order.push('consume');assert.deepEqual(value.decision,decision);return {fixture_only:true,original_awards:[]};}});
  assert.equal(result.status,'TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING');assert.deepEqual(order,['read','validate-request','decide','validate-decision','consume']);assert.equal(result.original_acceptance,false);});
 await test('wrong G3 body binding cannot invoke the consumption callback',async()=>{const {api}=bridge();const s=spec('g3',{stage:'original-final'});let consumed=0;
  const result=await api.consumeG3(s,permit(),{readRequest:async()=>({raw:'{}'}),validateRequest:async()=>({request_sha256:sha('{}')}),decide:async()=>({raw:'{}'}),validateDecision:async()=>({request_sha256:sha('{}'),decision_sha256:'f'.repeat(64)}),consume:async()=>{consumed++;return {};}});
  assert.equal(result.status,'UNKNOWN_NO_REPLAY');assert.equal(consumed,0);});
 await test('rejected provider promise is never replayed',async()=>{const {api}=bridge(toolkit(async()=>{throw Error('fixture disconnected');}));const s=spec('sender'),before=allCalls.length;
  const result=await api.sender(s,permit(),senderCaps(dispatcher(s)));assert.equal(result.status,'UNKNOWN_NO_REPLAY');
  const replay=await api.sender(s,permit(),senderCaps(dispatcher(s)));assert.equal(replay.status,'REFUSED_BEFORE_OPERATION');assert.equal(allCalls.length-before,1);});
}finally{
 for(const row of processes.values())if(row.exit===undefined){row.child.kill('SIGKILL');}
 const result={schema:'g132.pro-portability-fixture-results.v1',scope:'SYNTHETIC_GITHUB_AUTHORITY_SENDER_AND_G3; ACTUAL_LINUX_PROCESS_FILE_TTY_ONLY',
  tests:testRows,passed:testRows.filter(x=>x.status==='PASS').length,failed:testRows.filter(x=>x.status==='FAIL').length,
  local_process_calls:processCalls,synthetic_provider_calls:allCalls.length,real_github_calls:0,protected_effects:0,
  original_encryption_decryption:0,original_acceptance:false,fixture_directory:root,
  source:Object.fromEntries(Object.entries(received).map(([name,body])=>[name,desc(body)])),
  closing_source_matches:received.bridge.equals(fs.readFileSync(bridgePath))&&received.host.equals(fs.readFileSync(hostPath))
    &&received.codec.equals(fs.readFileSync(codecPath))&&received.test.equals(fs.readFileSync(fileURLToPath(import.meta.url)))};
 if(!result.closing_source_matches)process.exitCode=1;
 if(reportPath)fs.writeFileSync(reportPath,JSON.stringify(result,null,2)+'\n');
 process.stdout.write(JSON.stringify(result,null,2)+'\n');
}
