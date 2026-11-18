/* Synthetic provider/Root only. Exact public owner modules and real current
 * Linux processes perform publication receiving and the genuine G3 refusal. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../..');
const where=process.argv.indexOf('--report');
const report=where>=0?path.resolve(process.argv[where+1]):null;
const base=report?path.dirname(report):os.tmpdir();fs.mkdirSync(base,{recursive:true});
const container=fs.mkdtempSync(path.join(base,'g132-owner-fixture-'));fs.chmodSync(container,0o700);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const desc=b=>({bytes:Buffer.byteLength(b),sha256:sha(b)});
const git=(kind,b)=>crypto.createHash('sha1').update(Buffer.concat([Buffer.from(kind+' '+b.length+'\0'),b])).digest('hex');
const paths={bridge:path.join(here,'g132_operator_bridge.js'),host:path.join(here,'g132_linux_host.py'),
  runtime:path.join(here,'g132_owner_runtime.py'),prepare:path.join(here,'g132_prepare_smoke.py'),
  senderFixture:path.join(here,'g132_sender_fixture.py'),
  harness:path.join(here,'g132_functions_smoke.js'),codec:path.join(repo,'qualification/dg16-github-evidence/channel.js'),test:fileURLToPath(import.meta.url)};
const source=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(p)]));
const codec=eval(source.codec.toString()),makeBridge=eval(source.bridge.toString()),smoke=eval(source.harness.toString());
let sequence=0,processCalls=0;const live=new Map(),results=[];
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function drain(row){const output=row.output;row.output='';return row.exit===undefined?{output,session_id:row.id}:{output,exit_code:row.exit};}
const local={
  async exec_command(args){processCalls++;
    const child=args.tty?spawn('/usr/bin/script',['-qec',args.cmd,'/dev/null'],{stdio:['pipe','pipe','pipe']}):spawn('/bin/bash',['-c',args.cmd],{stdio:['pipe','pipe','pipe']});
    const row={id:++sequence,child,output:'',exit:undefined};live.set(row.id,row);
    child.stdout.on('data',b=>row.output+=b);child.stderr.on('data',b=>row.output+=b);
    child.on('close',code=>row.exit=code??1);await wait(20);return drain(row);
  },
  async write_stdin(args){const row=live.get(args.session_id);assert.ok(row);if(args.chars)row.child.stdin.write(args.chars);await wait(20);return drain(row);},
};
function prepare(name){const directory=path.join(container,name);
  const call=spawnSync('/usr/bin/python3',['-I','-B',paths.prepare,'--repo',repo,'--root',directory,
    '--branch','engineering/g132-portability-smoke-fixture-'+name,'--parent','d8813ea46a06ce0e9f6260d6adccb4ab30cf4445',
    '--controller','fixture-current-root','--continuity-receipt','FIXTURE_ONLY','--assignment-ref','FIXTURE_ONLY'],{encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
  assert.equal(call.status,0,call.stderr);return JSON.parse(call.stdout);
}
function fakeProvider(corruptFile=false){const blobs=new Map(),trees=new Map(),commits=new Map(),branches=new Map(),calls=[];
  const object=body=>({content:[],structuredContent:body,isError:false});
  const tools={...local};
  const api='https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md';
  for(const name of ['create_blob','create_tree','create_commit','create_branch','update_ref','fetch','fetch_file']){
    tools['mcp__codex_apps__github_'+name]=async args=>{
      calls.push({tool:name,args});
      if(name==='create_blob'){
        const b=Buffer.from(args.content,args.encoding==='base64'?'base64':'utf8'),id=git('blob',b);blobs.set(id,b);return object({sha:id});
      }
      if(name==='create_tree'){
        const rows=args.tree_elements.map(row=>{
          let id=row.sha;if(row.content!==undefined){const b=Buffer.from(row.content);id=git('blob',b);blobs.set(id,b);}
          assert.ok(blobs.has(id));return {path:row.path,mode:'100644',type:'blob',sha:id,size:blobs.get(id).length};
        }).sort((a,b)=>a.path.localeCompare(b.path));
        const bytes=Buffer.concat(rows.map(row=>Buffer.concat([Buffer.from(row.mode+' '+row.path+'\0'),Buffer.from(row.sha,'hex')])));
        const id=git('tree',bytes);trees.set(id,rows);return object({sha:id});
      }
      if(name==='create_commit'){
        assert.ok(trees.has(args.tree_sha));const raw=Buffer.from('tree '+args.tree_sha+'\nparent '+args.parent_sha+'\n\n'+args.message+'\n');
        const id=git('commit',raw);commits.set(id,{sha:id,tree:{sha:args.tree_sha},parents:[{sha:args.parent_sha}]});return object({sha:id});
      }
      if(name==='create_branch'){assert.ok(!branches.has(args.branch_name));assert.ok(commits.has(args.sha));branches.set(args.branch_name,args.sha);return object({ref:'refs/heads/'+args.branch_name,object:{sha:args.sha,type:'commit'}});}
      if(name==='update_ref'){assert.equal(branches.get(args.branch_name),args.expected_sha);assert.equal(args.force,false);branches.set(args.branch_name,args.sha);return object({ref:'refs/heads/'+args.branch_name,object:{sha:args.sha,type:'commit'}});}
      if(name==='fetch_file'){
        const commit=commits.get(args.ref),entry=trees.get(commit.tree.sha).find(row=>row.path===args.path),b=blobs.get(entry.sha);
        return object({content:b.toString('base64'),encoding:'base64',sha:corruptFile?'f'.repeat(40):entry.sha,
          display_url:'https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/'+args.ref+'/'+args.path,
          display_title:args.path.split('/').at(-1)});
      }
      let body;
      if(args.url.includes('/actions/runs/'))body={id:43853354399,run_attempt:1,status:'completed',conclusion:'failure',head_sha:'625f310d04cb5b5a1f02901cfdcf3c3815730a5e'};
      else if(args.url.includes('/contents/'))body={type:'file',encoding:'base64',content:Buffer.from('SYNTHETIC WORKFLOW METADATA ONLY').toString('base64')};
      else if(args.url.startsWith(api+'/git/ref/heads/')){const branch=args.url.slice((api+'/git/ref/heads/').length);body={ref:'refs/heads/'+branch,object:{sha:branches.get(branch),type:'commit'}};}
      else if(args.url.startsWith(api+'/git/commits/'))body=commits.get(args.url.split('/').at(-1));
      else if(args.url.startsWith(api+'/git/trees/')){const id=args.url.split('/').at(-1);body={sha:id,truncated:false,tree:trees.get(id)};}
      else throw Error('unexpected synthetic endpoint');
      assert.ok(body);return object({url:args.url,display_url:args.url,content:JSON.stringify(body)});
    };
  }return {tools,calls};
}
const admit=async scope=>({authorization:{ref:'FIXTURE_ONLY_NOT_A_GRANT',sha256:'d'.repeat(64)},
  assertCurrent:async()=>Date.now()<scope.spec.expires_ms,assertNoReplay:async()=>true});
let decisions=0;
const rootCaps={admit,decide:async({request,fixture_scope,original_effect_grant})=>{
  assert.equal(fixture_scope,'SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS');assert.equal(original_effect_grant,false);
  decisions++;return {raw:codec.canonical(request.decision_proposal)+'\n',fixture_only:true};
}};
async function test(name,fn){const start=Date.now();try{await fn();results.push({name,status:'PASS',elapsed_ms:Date.now()-start});}
  catch(error){results.push({name,status:'FAIL',elapsed_ms:Date.now()-start,message:String(error)});throw error;}}
try{
  await test('exact owner publication and strict G3 decision validate; actual consumer refuses nonroot',async()=>{
    const setup=prepare('positive'),provider=fakeProvider();
    const outcome=await smoke({tools:provider.tools,codec,makeBridge,setup,root:rootCaps});
    fs.writeFileSync(path.join(container,'POSITIVE_OWNER_RECEIPT.json'),JSON.stringify(outcome,null,2)+'\n');
    assert.equal(outcome.status,'PUBLIC_SMOKE_COMPLETE_ORIGINAL_G3_REFUSED');
    assert.equal(provider.calls.length,34);assert.equal(decisions,1);
    assert.equal(outcome.sender_mechanics.result.sender_reads,18);
    assert.equal(outcome.sender_mechanics.result.terminal.original_binding_gate_passed,false);
    assert.equal(outcome.sender_mechanics.result.terminal.original_sender_invoked,false);
    assert.equal(Object.keys(outcome.sender_mechanics.result.terminal.actual_tool_result_descriptors).length,18);
    assert.equal(outcome.publication.result.source_receipt.exact_owner_receipt.readback_profile,'FIRST_PARTY_BASE64_FILE_AT_PUBLISHED_COMMIT');
    assert.equal(outcome.g3.result.decisionBinding.strict_original_validator_returned,true);
    assert.equal(outcome.g3.result.consumer_return.refusal,'ACTUAL_ROOT_CUSTODY_REQUIRED');
    assert.equal(outcome.g3.result.consumer_return.uid,process.getuid());
    assert.equal(outcome.original_acceptance,false);
  });
  await test('exact original file receiver rejects a wrong provider blob identity before G3',async()=>{
    const setup=prepare('bad-file'),provider=fakeProvider(true),before=decisions;
    const outcome=await smoke({tools:provider.tools,codec,makeBridge,setup,root:rootCaps});
    fs.writeFileSync(path.join(container,'NEGATIVE_OWNER_RECEIPT.json'),JSON.stringify(outcome,null,2)+'\n');
    assert.equal(outcome.status,'STOPPED_PUBLICATION_NO_REPLAY');
    assert.equal(outcome.publication.status,'UNKNOWN_NO_REPLAY');assert.equal(decisions,before);
    const again=await smoke({tools:provider.tools,codec,makeBridge,setup,root:rootCaps});
    assert.equal(again.status,'STOPPED_PUBLIC_READ_NO_REPLAY');assert.equal(provider.calls.length,34);
  });
}finally{
  for(const row of live.values())if(row.exit===undefined)row.child.kill('SIGKILL');
  const outcome={schema:'g132.actual-owner-fixture-receipt.v1',scope:'FAKE_GITHUB_AND_ROOT; EXACT_PUBLIC_OWNER_FUNCTIONS_ON_ACTUAL_LINUX',
    tests:results,passed:results.filter(x=>x.status==='PASS').length,failed:results.filter(x=>x.status==='FAIL').length,
    local_process_calls:processCalls,fixture_root:container,source:Object.fromEntries(Object.entries(source).map(([k,b])=>[k,desc(b)])),
    closing_source_matches:Object.entries(paths).every(([k,p])=>source[k].equals(fs.readFileSync(p))),
    real_github_calls:0,protected_effects:0,original_private_body_operations:0,original_acceptance:false};
  if(!outcome.closing_source_matches)process.exitCode=1;
  if(report)fs.writeFileSync(report,JSON.stringify(outcome,null,2)+'\n');process.stdout.write(JSON.stringify(outcome,null,2)+'\n');
}
