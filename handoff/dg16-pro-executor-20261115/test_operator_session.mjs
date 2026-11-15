// Actual channel and Python journal; body/connector boundaries are controlled
// doubles. Retained genuine wrappers are source-test data, never a new event.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const HERE=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.resolve(HERE,'../..');
const CHANNEL=path.join(ROOT,'qualification/dg16-github-evidence/channel.js');
const JOURNAL=path.join(ROOT,'qualification/dg16-github-evidence/journal.py');
const INPUT=process.env.DG16_ACTUAL_PROVIDER;
const digest=x=>crypto.createHash('sha256').update(x).digest('hex');
const copy=x=>JSON.parse(JSON.stringify(x));
const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
const fixture=(url,content)=>({content:[{type:'text',text:'Action completed.'}],isError:false,
  structuredContent:{url,display_url:url,content:JSON.stringify(content)}});

function scenario(options={}){
  assert.ok(INPUT,'DG16_ACTUAL_PROVIDER is required for this source-shape suite');
  const wrappers=Object.fromEntries(['run','attempt','jobs','commit','workflow','artifacts'].map(k=>
    [k,JSON.parse(fs.readFileSync(path.join(INPUT,k+'.json'),'utf8'))]));
  const read=k=>JSON.parse(wrappers[k].structuredContent.content);
  const run=read('run'),commit=read('commit'),artifact=read('artifacts').artifacts[0];
  const branch=run.head_branch,repo=run.repository.full_name,base='https://api.github.com/repos/'+repo;
  const source=fs.readFileSync(CHANNEL,'utf8'),journal=fs.readFileSync(JOURNAL);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'dg16-operator-source-test-'));fs.chmodSync(dir,0o700);
  const selection={schema:'dg16.github-public-observation-selection.v1',purpose:'SOURCE_QUALIFICATION',
    operator:'PRO-EXECUTOR-01',actor:'/root',successor:'PRO-EXECUTOR-01, designated by owner',role:'terminal',
    operation_id:path.basename(dir),journal_root:dir,expires_ms:Date.now()+240000,control:null,
    source:{channel_sha256:digest(source),journal_sha256:digest(journal),journal_path:JOURNAL,
      python_path:process.env.CODEX_PRIMARY_RUNTIME_PYTHON||'/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3'},
    context:{repository:repo,repository_id:run.repository.id,branch,run_id:String(run.id),run_attempt:1,
      workflow_commit:commit.sha,workflow_tree:commit.tree.sha,source_commit:commit.parents[0].sha,
      source_tree:'9ffbaf95080092bf4a45b8772a97ed16068544a7',workflow_path:run.path,
      workflow_sha256:digest(wrappers.workflow.structuredContent.content),job_name:'full-registry-raw-pair',
      github_actor:{id:run.actor.id,login:run.actor.login}}};
  const data=Object.fromEntries(Object.values(wrappers).map(w=>[w.structuredContent.url,w]));
  const ref=base+'/git/ref/heads/'+branch,sourceURL=base+'/git/commits/'+commit.parents[0].sha;
  data[ref]=fixture(ref,{ref:'refs/heads/'+branch,object:{type:'commit',sha:commit.sha}});
  data[sourceURL]=fixture(sourceURL,{sha:commit.parents[0].sha,tree:{sha:selection.context.source_tree},parents:[]});
  const bodySource={path:path.join(HERE,'platform_artifact.py'),sha256:digest(fs.readFileSync(path.join(HERE,'platform_artifact.py'))),journal_parent:'/unused-offline-body-root'};
  const counts={metadata:0,body_process:0,download:0,frames:0,polls:0};let previous=null;
  const tools={
    exec_command:async args=>{
      if(!args.tty){const r=spawnSync('/bin/bash',['-c',args.cmd],{encoding:'utf8'});return{exit_code:r.status,output:r.stdout+r.stderr};}
      counts.body_process++;assert.ok(args.cmd.includes(quote(bodySource.sha256)));
      assert.ok(args.cmd.includes(quote(bodySource.path)));assert.equal(args.login,false);
      return {session_id:17,output:options.badReady?'unqualified readiness\r\n':'READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME\r\n'};
    },
    mcp__codex_apps__github_fetch:async request=>{
      counts.metadata++;assert.deepEqual(Object.keys(request),['url']);assert.ok(data[request.url]);return copy(data[request.url]);
    },
    mcp__codex_apps__github_download_workflow_artifact:async request=>{
      counts.download++;assert.equal(counts.body_process,1);assert.equal(counts.download,1);
      assert.deepEqual(JSON.parse(JSON.stringify(request)),{repo_full_name:repo,artifact_id:artifact.id,file_name:artifact.name+'.zip'});
      if(options.lostDownload)throw Error('SENSITIVE_FIXTURE_MUST_NOT_ESCAPE');
      return {content:[],isError:false,structuredContent:{fixture:'INERT_DOWNLOAD_NO_REAL_REFERENCE'}};
    },
    write_stdin:async request=>{
      assert.equal(request.session_id,17);
      if(request.chars){counts.frames++;assert.equal(counts.frames,1);const i=request.chars.indexOf('\n');
        assert.equal(Number(request.chars.slice(0,i)),Buffer.byteLength(request.chars.slice(i+1)));
        JSON.parse(request.chars.slice(i+1));
        if(options.poll)return{session_id:17,output:''};
      }else counts.polls++;
      const outcome={status:'EXACT_PUBLIC_BODY_RECEIVED',original_acceptance:false,body_get_attempts:1,
        signed_url_retained:false,provider_receipt_sha256:previous.receipt_sha256,
        archive:{bytes:artifact.size_in_bytes,sha256:options.wrongBody?'a'.repeat(64):artifact.digest.slice(7)}};
      return{exit_code:0,output:JSON.stringify(outcome)+'\r\n'};
    }};
  const C=vm.runInNewContext(source,{tools,Date},{filename:CHANNEL});
  const originalCollect=C.collect;
  const channel={...C,collect:async(...args)=>{previous=await originalCollect(...args);return previous;}};
  const invoke=vm.runInNewContext(fs.readFileSync(path.join(HERE,'operator_session.js'),'utf8'),{tools,Date},{filename:'operator_session.js'});
  const admit=async bound=>{
    assert.equal(bound.operation,'READ_ONLY_PUBLIC_METADATA_AND_ONE_PUBLIC_ARCHIVE');
    assert.equal(C.canonical(bound.selection),C.canonical(selection));
    assert.equal(C.canonical(bound.body_source),C.canonical(bodySource));
    return{authorization:{ref:'OFFLINE_SOURCE_TEST_ONLY_NO_AUTHORITY',sha256:'e'.repeat(64)},
      assertCurrent:async value=>{
        assert.equal(C.canonical(value.bound),C.canonical(bound));
        if(options.revokeAtBody&&value.action==='body-process-start')throw Error('revoked');
      }};
  };
  return{run:()=>invoke(channel,selection,bodySource,options.serializedAdmission?{}:admit),counts,dir};
}

const control=(name,options,verify)=>test(name,{skip:!INPUT},async()=>{
  const s=scenario(options);try{const result=await s.run();verify(result,s.counts);}finally{fs.rmSync(s.dir,{recursive:true,force:true});}
});
control('real channel and journal compose with one pinned body process and one ephemeral frame',{},(r,n)=>{
  assert.equal(r.status,'PUBLIC_ACQUISITION_REQUIRES_DISTINCT_AND_SEMANTIC_RECEIVING');
  assert.equal(r.original_acceptance,false);assert.deepEqual(n,{metadata:11,body_process:1,download:1,frames:1,polls:0});
});
control('polling observes the same body process without repeating download or frame',{poll:true},(r,n)=>{
  assert.equal(r.status,'PUBLIC_ACQUISITION_REQUIRES_DISTINCT_AND_SEMANTIC_RECEIVING');assert.equal(n.download,1);assert.equal(n.frames,1);assert.equal(n.polls,1);
});
control('unreceived durable readiness prevents a download',{badReady:true},(r,n)=>{
  assert.equal(r.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(n.download,0);assert.equal(n.frames,0);
});
control('lost download result is not repeated or exposed',{lostDownload:true},(r,n)=>{
  assert.equal(r.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(n.download,1);assert.equal(n.frames,0);
  assert.ok(!JSON.stringify(r).includes('SENSITIVE_FIXTURE'));assert.equal(r.automatic_retry,false);
});
control('altered returned archive descriptor cannot complete acquisition',{wrongBody:true},(r,n)=>{
  assert.equal(r.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(n.download,1);assert.equal(n.frames,1);
});
control('revocation after metadata prevents starting the body process',{revokeAtBody:true},(r,n)=>{
  assert.equal(r.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(n.metadata,11);assert.equal(n.body_process,0);assert.equal(n.download,0);
});
control('serialized admission cannot replace actual authority callback',{serializedAdmission:true},(r,n)=>{
  assert.equal(r.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(n.metadata,0);assert.equal(n.body_process,0);
});
