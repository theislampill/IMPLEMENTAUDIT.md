// External API calls are controlled doubles; the durable journal is the real
// Python implementation. This is offline source qualification, never native evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const WORK=path.join(HERE,'.test-work');fs.mkdirSync(WORK,{recursive:true,mode:0o700});
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const clone=v=>JSON.parse(JSON.stringify(v));
const canon=v=>JSON.stringify(v,(k,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const DESC=x=>({bytes:Buffer.byteLength(x),sha256:hash(x)});
const REPO='theislampill/IMPLEMENTAUDIT.md',BASE='https://api.github.com/repos/'+REPO;
const COMMIT='ce144b1d06f81bda3225b48d3bab32374515cff5',TREE='bbc3669b2167548a5a8b9ec0986b1e8b18e720eb';
const SOURCE='205aeab7c93299b0666b261485ab5658d8e183de',STREE='9ffbaf95080092bf4a45b8772a97ed16068544a7';
const BRANCH='pro/dg16-r5-full-g2-direct-host-20-20261114',RUN='43640583300';
const ACTOR={id:266501826,login:'theislampill'},RID=1243475954;
const WF='name: offline test only\n';
const URLS={run:BASE+'/actions/runs/'+RUN,attempt:BASE+'/actions/runs/'+RUN+'/attempts/1',jobs:BASE+'/actions/runs/'+RUN+'/attempts/1/jobs?per_page=100&page=1',commit:BASE+'/git/commits/'+COMMIT,source:BASE+'/git/commits/'+SOURCE,workflow:BASE+'/contents/.github/workflows/dg16-r5-full-g2.yml?ref='+COMMIT,artifacts:BASE+'/actions/runs/'+RUN+'/artifacts?per_page=100',ref:BASE+'/git/ref/heads/'+BRANCH};
function wrap(url,body,text=false){const content=text?body:JSON.stringify(body);return {content:[{type:'text',text:'Action completed.'}],structuredContent:{content,title:'test',modified_date:null,url,display_url:url,display_title:'test',structuredContent:{title:'test',content,display_url:url}},isError:false};}
function fixtures(){
 const run={id:Number(RUN),run_attempt:1,head_sha:COMMIT,head_branch:BRANCH,path:'.github/workflows/dg16-r5-full-g2.yml',event:'push',status:'completed',conclusion:'failure',repository:{id:RID,full_name:REPO},head_repository:{id:RID,full_name:REPO},actor:ACTOR,triggering_actor:ACTOR,run_started_at:'2026-11-14T20:00:00Z'};
 const artifact={id:14136761564,name:'dg16-full-registry-'+RUN+'-1',expired:false,size_in_bytes:15700,digest:'sha256:4a18656e3431b579e7a459cb9f811bd85e1e226787c28933239946e4637ede98',workflow_run:{id:Number(RUN),repository_id:RID,head_repository_id:RID,head_sha:COMMIT,head_branch:BRANCH},created_at:'2026-11-14T23:14:48Z'};
 return {[URLS.run]:wrap(URLS.run,run),[URLS.attempt]:wrap(URLS.attempt,run),[URLS.jobs]:wrap(URLS.jobs,{total_count:1,jobs:[{id:132587057176,run_id:Number(RUN),run_attempt:1,head_sha:COMMIT,name:'full-registry-raw-pair',status:'completed',conclusion:'failure',started_at:'2026-11-14T20:00:01Z'}]}),[URLS.commit]:wrap(URLS.commit,{sha:COMMIT,tree:{sha:TREE},parents:[{sha:SOURCE}]}),[URLS.source]:wrap(URLS.source,{sha:SOURCE,tree:{sha:STREE},parents:[]}),[URLS.workflow]:wrap(URLS.workflow,WF,true),[URLS.artifacts]:wrap(URLS.artifacts,{total_count:1,artifacts:[artifact]}),[URLS.ref]:wrap(URLS.ref,{ref:'refs/heads/'+BRANCH,object:{type:'commit',sha:COMMIT}})};
}
function scenario(options={}){
 const dir=fs.mkdtempSync(path.join(WORK,'case-'));fs.chmodSync(dir,0o700);
 const sourcePath=path.join(HERE,'channel.js'),journalPath=path.join(HERE,'journal.py');
 const source=fs.existsSync(sourcePath)?fs.readFileSync(sourcePath,'utf8'):'({})';
 const spec={schema:'dg16.github-public-observation-selection.v1',purpose:'SOURCE_QUALIFICATION',operator:'PRO-EXECUTOR-01',actor:'/root',successor:'PRO-EXECUTOR-01, designated by owner',role:'terminal',operation_id:'offline-'+path.basename(dir),source:{channel_sha256:hash(source),journal_sha256:fs.existsSync(journalPath)?hash(fs.readFileSync(journalPath)):'0'.repeat(64),journal_path:journalPath,python_path:process.env.CODEX_PRIMARY_RUNTIME_PYTHON||'/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python'},journal_root:dir,expires_ms:Date.now()+240000,context:{repository:REPO,repository_id:RID,branch:BRANCH,run_id:RUN,run_attempt:1,workflow_commit:COMMIT,workflow_tree:TREE,source_commit:SOURCE,source_tree:STREE,workflow_path:'.github/workflows/dg16-r5-full-g2.yml',workflow_sha256:hash(WF),job_name:'full-registry-raw-pair',github_actor:ACTOR},control:null};
 const calls=[],data=fixtures(),shell=[];let admissionCalls=0;
 const host={admit:async request=>{
  assert.equal(request.source.channel_sha256,hash(source));
  admissionCalls++;
  return {authorization:{ref:'owner/offline-source-engineering',sha256:'a'.repeat(64)},assertCurrent:async scope=>{assert.equal(scope.operator,'PRO-EXECUTOR-01');if(options.revoke&&calls.length>=options.revoke)throw Error('revoked');if(options.current)await options.current(scope);},assertIndependent:async()=>{if(options.notIndependent)throw Error('not independent');}};
 }};
 const tools={mcp__codex_apps__github_fetch:async args=>{
  assert.deepEqual(Object.keys(args),['url']);
  // A provider call without a durable intent is the key mutation this catches.
  const slots=fs.readdirSync(dir);assert.equal(slots.length,1);
  const names=fs.readdirSync(path.join(dir,slots[0]));assert.ok(names.includes(String(calls.length).padStart(3,'0')+'.intent.json'));
  calls.push(args.url);
  if(options.throwAt===calls.length)throw Error('private token should never be logged');
  let reply=clone(data[args.url]);assert.ok(reply,'unplanned endpoint '+args.url);
  if(options.mutate)reply=options.mutate(reply,args.url,calls.length)||reply;
  return reply;
 },exec_command:async args=>{
  assert.equal(args.login,false);assert.equal(args.shell,'/bin/bash');shell.push(args.cmd);
  const r=spawnSync('/bin/bash',['-c',args.cmd],{encoding:'utf8',maxBuffer:2**20});if(options.persisted&&r.status===0)await options.persisted(JSON.parse(r.stdout),args.cmd);return {exit_code:r.status,output:r.stdout+r.stderr,wall_time_seconds:0};
 }};
 // No process/require/fs/Buffer/TextEncoder/crypto/fetch is exposed in this VM.
 const api=vm.runInNewContext(source,{tools,Date:options.clock||Date},{filename:'channel.js',timeout:2000});
 return {api,spec,host,data,calls,shell,dir,admissionCalls:()=>admissionCalls};
}
function mutateBody(reply,fn){const s=reply.structuredContent;const v=JSON.parse(s.content);fn(v);s.content=JSON.stringify(v);if(s.structuredContent)s.structuredContent.content=s.content;return reply;}
function withControl(s){const branch=BRANCH.replace('-host-','-control-'),commit='4'.repeat(40),tree='5'.repeat(40),prefix='qualification/dg16-full-g2-control/'+RUN+'-1';const files={};for(const name of ['CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_CONSUMPTION.json']){const body=JSON.stringify({fixture:'NO_ACTUAL_REVIEW_OR_AUTHORITY',name})+'\n';files[name]=DESC(body);const url=BASE+'/contents/'+prefix+'/'+name+'?ref='+commit;s.data[url]=wrap(url,body,true);}s.spec.control={branch,commit,tree,path:prefix,files};const ref=BASE+'/git/ref/heads/'+branch,git=BASE+'/git/commits/'+commit;s.data[ref]=wrap(ref,{ref:'refs/heads/'+branch,object:{type:'commit',sha:commit}});s.data[git]=wrap(git,{sha:commit,tree:{sha:tree},parents:[{sha:COMMIT}]});return {ref,git};}
async function collect(options={},change=()=>{}){const s=scenario(options);change(s);s.result=await s.api.collect(s.spec,s.host);return s;}

test('V8 channel exposes acquisition and independent receiving without Node globals',()=>{const s=scenario();assert.equal(typeof s.api.collect,'function');assert.equal(typeof s.api.receive,'function');});
test('UTF8 SHA-256 descriptors match independent standard vectors',()=>{const s=scenario();for(const v of ['', 'abc','snowman ☃ / emoji 😀','\ud800'])assert.deepEqual(clone(s.api.descriptor(v)),DESC(v));});
test('real journal precedes every read; failed run remains failure and no acceptance',async()=>{
 const s=await collect();assert.equal(s.result.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(s.result.public_metadata.run.conclusion,'failure');assert.equal(s.result.original_acceptance,false);assert.equal(s.calls.length,11);assert.equal(s.result.operator,'PRO-EXECUTOR-01');assert.equal(s.result.private_or_cipher,false);
 const dir=path.join(s.dir,fs.readdirSync(s.dir)[0]);assert.ok(fs.existsSync(path.join(dir,'FINAL.json')));assert.ok(!fs.readFileSync(path.join(dir,'FINAL.json'),'utf8').includes('private token'));
 for(const [i,url] of s.calls.entries()){const record=JSON.parse(fs.readFileSync(path.join(dir,String(i).padStart(3,'0')+'.result.json'),'utf8'));assert.deepEqual(record.whole_actual_wrapper,DESC(JSON.stringify(s.data[url])));}
});
test('serialized authority labels cannot replace the external admission capability',async()=>{const s=scenario();const r=await s.api.collect(s.spec,{admit:async()=>({authorization:{ref:'x',sha256:'a'.repeat(64)},authorized:true})});assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('expired authorization fails before reserving or reading',async()=>{const s=await collect({},s=>{s.spec.expires_ms=Date.now()-1;});assert.equal(s.result.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('replay with changed nonce is refused without another provider invocation',async()=>{const s=await collect();assert.equal(s.result.original_acceptance,false);const before=s.calls.length;s.spec.operation_id+='-changed';const second=await s.api.collect(s.spec,s.host);assert.equal(second.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,before);});
test('lost provider response is UNKNOWN; no automatic retry and no exception disclosure',async()=>{const s=await collect({throwAt:2});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');assert.equal(s.calls.length,2);assert.ok(!JSON.stringify(s.result).includes('private token'));const second=await s.api.collect(s.spec,s.host);assert.equal(second.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,2);});
test('revoked live capability stops before the next provider call',async()=>{const s=await collect({revoke:2});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');assert.equal(s.calls.length,2);});
for(const [label,kind,fn] of [
 ['misattributed GitHub actor','run',v=>{v.actor.id=7;}],
 ['wrong workflow parent','commit',v=>{v.parents.push({sha:'1'.repeat(40)});} ],
 ['wrong source tree','source',v=>{v.tree.sha='2'.repeat(40);} ],
 ['missing artifact','artifacts',v=>{v.total_count=0;v.artifacts=[];} ],
 ['duplicate artifacts','artifacts',v=>{v.artifacts.push(v.artifacts[0]);v.total_count=2;} ],
 ['wrong attempt','attempt',v=>{v.run_attempt=2;} ],
 ['changed host ref','ref',v=>{v.object.sha='3'.repeat(40);} ],
 ['unknown extra job','jobs',v=>{v.total_count=2;v.jobs.push(v.jobs[0]);} ]
])test(label+' is refused by the actual acquisition consumer',async()=>{const s=await collect({mutate:(r,url)=>url===URLS[kind]?mutateBody(r,fn):r});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');assert.ok(s.calls.length<=11);});
test('a stale closing run prevents completion',async()=>{let n=0;const s=await collect({mutate:(r,url)=>url===URLS.run&&++n===2?mutateBody(r,v=>{v.status='in_progress';}):r});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');});
test('wrong endpoint and incomplete connector wrappers are refused',async()=>{for(const mode of ['endpoint','partial','duplicate']){const s=await collect({mutate:r=>{if(mode==='endpoint')r.structuredContent.url+='x';if(mode==='partial')r._meta={partial:true};if(mode==='duplicate'){r.structuredContent.content='{"id":1,"id":2}';r.structuredContent.structuredContent.content=r.structuredContent.content;}return r;}});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');assert.equal(s.calls.length,1);}});
test('tampered journal source cannot run before a connector call',async()=>{const s=await collect({},s=>{s.spec.source.journal_sha256='f'.repeat(64);});assert.equal(s.result.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('symlink journal directory fails closed before provider access',async()=>{const s=scenario();const link=s.dir+'-link';fs.symlinkSync(s.dir,link);s.spec.journal_root=link;const r=await s.api.collect(s.spec,s.host);assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('independent receiving performs its own reads and preserves failed outcome',async()=>{const first=await collect();const s=scenario();s.spec.actor='/root/independent_receiver';const result=await s.api.receive(first.result,s.spec,s.host);assert.equal(result.status,'INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY');assert.equal(s.calls.length,11);assert.equal(result.original_acceptance,false);});
test('same actor or absent actual independence cannot receive its own result',async()=>{const first=await collect();for(const mode of ['same','unattested']){const s=scenario({notIndependent:mode==='unattested'});if(mode==='unattested')s.spec.actor='/root/independent_receiver';const r=await s.api.receive(first.result,s.spec,s.host);assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);}});
test('forged supplied provider metadata disagrees with independently reacquired facts',async()=>{const first=await collect();const fake=clone(first.result);fake.public_metadata.artifact.id+=1;const s=scenario();s.spec.actor='/root/independent_receiver';const r=await s.api.receive(fake,s.spec,s.host);assert.notEqual(r.status,'INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY');});
test('self-rehashed false metadata still loses to the independent fresh provider reads',async()=>{const first=await collect();const fake=clone(first.result);fake.public_metadata.artifact.id+=1;fake.facts.public_metadata.artifact.id+=1;fake.facts.artifact_population[0].id+=1;delete fake.receipt_sha256;fake.receipt_sha256=hash(canon(fake));const s=scenario();s.spec.actor='/root/independent_receiver';const r=await s.api.receive(fake,s.spec,s.host);assert.equal(r.status,'UNKNOWN_NO_RETRY');assert.equal(s.calls.length,11);});
test('internally inconsistent public metadata cannot be repaired by rehashing its envelope',async()=>{const first=await collect();const fake=clone(first.result);fake.public_metadata.artifact.id+=1;delete fake.receipt_sha256;fake.receipt_sha256=hash(canon(fake));const s=scenario();s.spec.actor='/root/independent_receiver';const r=await s.api.receive(fake,s.spec,s.host);assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('the external gate receives the actual journal custody and operation window',async()=>{const s=scenario();let seen;const admit=s.host.admit;s.host.admit=async req=>{seen=clone(req);return admit(req);};const r=await s.api.collect(s.spec,s.host);assert.equal(r.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(seen.journal_root,s.spec.journal_root);assert.equal(seen.expires_ms,s.spec.expires_ms);assert.equal(seen.operation_id,s.spec.operation_id);});
test('independent receiving refuses an expired but internally consistent operator receipt',async()=>{const first=await collect();const old=clone(first.result);old.expires_ms=Date.now()-1;delete old.receipt_sha256;old.receipt_sha256=hash(canon(old));const s=scenario();s.spec.actor='/root/independent_receiver';const r=await s.api.receive(old,s.spec,s.host);assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
for(const [phase,expectedCalls] of [['provider-return',2],['authority-callback',0],['last-result-write',11],['finish-callback',11],['final-durable-write',11]])test('parent expiry at '+phase+' stops receiving without extending its deadline',async()=>{
 let now=Date.now();const began=now,deadline=now+1000,clock={now:()=>now,parse:Date.parse};
 const first=await collect({clock},s=>{s.spec.expires_ms=deadline;});assert.equal(first.result.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');
 let resultWrites=0;
 const s=scenario({clock,mutate:(r,u,n)=>{if(phase==='provider-return'&&n===2)now=deadline;return r;},current:async scope=>{
  if(phase==='authority-callback'&&scope.action?.index===0&&scope.action.intent)now=deadline;
  if(phase==='finish-callback'&&scope.action==='finish')now=deadline;
 },persisted:async r=>{
  if(r.action==='result')resultWrites++;
  if(phase==='last-result-write'&&r.action==='result'&&resultWrites===11)now=deadline;
  if(phase==='final-durable-write'&&r.action==='finish')now=deadline;
 }});
 s.spec.actor='/root/independent_receiver';s.spec.expires_ms=began+240000;
 const r=await s.api.receive(first.result,s.spec,s.host);
 assert.equal(r.status,'UNKNOWN_NO_RETRY');assert.equal(s.calls.length,expectedCalls);assert.equal(r.automatic_retry,false);assert.equal(r.original_acceptance,false);
 const slot=path.join(s.dir,fs.readdirSync(s.dir)[0]);
 if(phase==='final-durable-write'){
  assert.equal(r.journal_completion,'UNKNOWN');assert.ok(fs.existsSync(path.join(slot,'FINAL.json')));
 }else{
  assert.ok(fs.existsSync(path.join(slot,'UNKNOWN.json')));assert.ok(!fs.existsSync(path.join(slot,'FINAL.json')));
 }
});
test('operator expiry during final durable write cannot return a received observation',async()=>{
 let now=Date.now();const deadline=now+1000,clock={now:()=>now,parse:Date.parse};
 const s=await collect({clock,persisted:async r=>{if(r.action==='finish')now=deadline;}},s=>{s.spec.expires_ms=deadline;});
 assert.equal(s.result.status,'UNKNOWN_NO_RETRY');assert.equal(s.result.journal_completion,'UNKNOWN');assert.equal(s.calls.length,11);assert.equal(s.result.automatic_retry,false);
});
test('optional action validator covers every actual callback including selected control reads',async()=>{
 const gated=s=>({admit:async scope=>{
  const admission=await s.host.admit(scope),validate=s.api.createActionValidator(s.spec);
  return {...admission,assertCurrent:async next=>{const received={...next};delete received.action;assert.equal(canon(received),canon(scope));validate(next.action);await admission.assertCurrent(next);}};
 }});
 for(const control of [false,true]){
  const first=scenario();if(control)withControl(first);const r=await first.api.collect(first.spec,gated(first));
  assert.equal(r.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(first.calls.length,control?17:11);
  const receiver=scenario();if(control)withControl(receiver);receiver.spec.actor='/root/independent_receiver';
  const q=await receiver.api.receive(r,receiver.spec,gated(receiver));assert.equal(q.status,'INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY');assert.equal(receiver.calls.length,control?17:11);assert.equal(q.original_acceptance,false);
 }
});
test('optional action validator refuses malformed redirected skipped and reordered callbacks',()=>{
 const s=scenario(),first={index:0,tool:'mcp__codex_apps__github_fetch',request:{url:URLS.ref}};
 for(const mutation of [()=>({...first,index:1}),()=>({...first,tool:'wrong'}),()=>({...first,request:{url:URLS.run}}),()=>({...first,request:{...first.request,method:'POST'}}),()=>({...first,intent:{bytes:3,sha256:'a'.repeat(64)}}),()=>({index:0,result_returned:true}),()=>('before:ref')]){
  const validate=s.api.createActionValidator(s.spec);validate('begin');assert.throws(()=>validate(mutation()));
 }
 const invalidIntent=s.api.createActionValidator(s.spec);invalidIntent('begin');invalidIntent(first);assert.throws(()=>invalidIntent({...first,intent:{bytes:0,sha256:'bad'}}));
 const earlyFinish=s.api.createActionValidator(s.spec);earlyFinish('begin');assert.throws(()=>earlyFinish('finish'));
 const duplicateFinish=s.api.createActionValidator(s.spec);duplicateFinish('begin');
 for(const [index,url] of [URLS.ref,URLS.run,URLS.attempt,URLS.jobs,URLS.commit,URLS.source,URLS.workflow,URLS.artifacts,URLS.run,URLS.artifacts,URLS.ref].entries()){
  const request={index,tool:first.tool,request:{url}};duplicateFinish(request);duplicateFinish({...request,intent:{bytes:1,sha256:'a'.repeat(64)}});duplicateFinish({index,result_returned:true});
 }
 duplicateFinish('finish');assert.throws(()=>duplicateFinish('finish'));
});
test('source qualification cannot be relabeled as the original acceptance route',async()=>{const first=await collect();const s=scenario();s.spec.actor='/root/independent_receiver';s.spec.purpose='OWNER_APPROVED_ORIGINAL_ROUTE';const r=await s.api.receive(first.result,s.spec,s.host);assert.equal(r.status,'REFUSED_BEFORE_PROVIDER_CALL');assert.equal(s.calls.length,0);});
test('known cipher metadata does not prevent receiving the public artifact; no cipher is fetched',async()=>{const s=await collect({mutate:(r,url)=>url===URLS.artifacts?mutateBody(r,v=>{v.artifacts.push({...v.artifacts[0],id:14136761565,name:'dg16-g2-failed-streams-'+RUN+'-a1',size_in_bytes:2000000});v.total_count=2;}):r});assert.equal(s.result.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(s.result.public_metadata.artifact.id,14136761564);assert.ok(s.calls.every(u=>!u.includes('/artifacts/')));});
test('arbitrary provider conclusion text cannot cross into the journal',async()=>{const s=await collect({mutate:(r,url)=>url===URLS.jobs?mutateBody(r,v=>{v.jobs[0].conclusion='untrusted arbitrary provider text';}):r});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');const files=fs.readdirSync(path.join(s.dir,fs.readdirSync(s.dir)[0]));for(const file of files)assert.ok(!fs.readFileSync(path.join(s.dir,fs.readdirSync(s.dir)[0],file),'utf8').includes('untrusted arbitrary provider text'));});
test('declared control ref, sole workflow parent and all three exact file bodies are observed',async()=>{const s=await collect({},withControl);assert.equal(s.result.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(s.calls.length,17);assert.equal(s.result.control_observation,'EXACT_SELECTED_PUBLIC_CONTROL_BYTES_ONLY');assert.equal(s.result.original_acceptance,false);});
test('a control commit with a second parent cannot be received',async()=>{let url;const s=await collect({mutate:(r,u)=>u===url?mutateBody(r,v=>v.parents.push({sha:SOURCE})):r},s=>{url=withControl(s).git;});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');});
test('altered control payload body cannot retain its selected digest',async()=>{const s=await collect({mutate:(r,u)=>u.includes('/CONTROL.json?')?{...r,structuredContent:{...r.structuredContent,content:'altered',structuredContent:{...r.structuredContent.structuredContent,content:'altered'}}}:r},withControl);assert.equal(s.result.status,'UNKNOWN_NO_RETRY');});
test('control ref drift at closing is refused',async()=>{let url,seen=0;const s=await collect({mutate:(r,u)=>u===url&&++seen===2?mutateBody(r,v=>{v.object.sha='6'.repeat(40);}):r},s=>{url=withControl(s).ref;});assert.equal(s.result.status,'UNKNOWN_NO_RETRY');});
test('actual current connector wrappers retain original parser-compatible shape',{skip:!process.env.DG16_ACTUAL_PROVIDER},async()=>{
 const input=process.env.DG16_ACTUAL_PROVIDER;
 const s=scenario();for(const name of ['run','attempt','jobs','commit','workflow','artifacts'])s.data[URLS[name]]=JSON.parse(fs.readFileSync(path.join(input,name+'.json'),'utf8'));
 s.spec.context.workflow_sha256=hash(s.data[URLS.workflow].structuredContent.content);
 const r=await s.api.collect(s.spec,s.host);assert.equal(r.status,'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING');assert.equal(r.public_metadata.artifact.id,14136761564);assert.equal(r.public_metadata.run.conclusion,'failure');
 // Exercise the unchanged original semantic metadata receiver function. Full
 // archive/PROOF/native/closing-log receiving remains root's separate gate.
 const original=path.resolve(HERE,'../../handoff/dg16-g221-root-execution-inputs/g220-custody/candidate-e76-source-01/receiver/public_receiver.py');
 const code="import ast,hashlib,json,re,sys\nfrom pathlib import Path\np=Path(sys.argv[1]); raw=p.read_bytes(); assert hashlib.sha256(raw).hexdigest()=='5bb8d71aa40e2a4d842ddd178b31257eef496ca3c0073461e8328d2e64560f5e'\nt=ast.parse(raw); chosen=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in {'need','sha','encode','metadata_bindings'}]; scope={'hashlib':hashlib,'json':json,'re':re}; exec(compile(ast.Module(body=chosen,type_ignores=[]),str(p),'exec'),scope)\nm=json.loads(sys.argv[2]); a=m['artifact']; b={'branch':m['run']['head_branch'],'repository':'theislampill/IMPLEMENTAUDIT.md','final_tree':m['commit']['tree']['sha'],'source_commit':m['commit']['parents'][0]['sha']}\nr=scope['metadata_bindings'](m,'terminal',str(m['run']['id']),m['run']['head_sha'],{'bytes':a['size_in_bytes'],'sha256':a['digest'][7:]},b); assert r['scope']=='PROVIDED_METADATA_BINDINGS; acquisition authenticity is independently received'; print('ORIGINAL_METADATA_RECEIVER_ACCEPTED_AT_DATA_SCOPE')\n";
 const check=spawnSync(s.spec.source.python_path,['-I','-B','-c',code,original,JSON.stringify(r.public_metadata)],{encoding:'utf8'});assert.equal(check.status,0,check.stdout+check.stderr);assert.equal(check.stdout.trim(),'ORIGINAL_METADATA_RECEIVER_ACCEPTED_AT_DATA_SCOPE');
 fs.writeFileSync(path.join(s.dir,'actual-wrapper-result.json'),JSON.stringify(r,null,2)+'\n',{mode:0o600});
});
