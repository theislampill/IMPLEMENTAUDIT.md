// New Python result -> byte-identical recovered V8 interface controls.
// All tool/capability results here are explicit inert fixtures. No API is used.
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import test from 'node:test';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const channel=readFileSync(path.join(HERE,'../channel.js'),'utf8');
const driver=readFileSync(path.join(HERE,'receiving_session.js'),'utf8');
const publisher=readFileSync(path.join(HERE,'control_publication.js'),'utf8');
const C=vm.runInNewContext(channel);
const descriptor=C.descriptor;
const PYTHON=execFileSync('python',['-c','import sys;print(sys.executable)'],{encoding:'utf8'}).trim();

function fixture(mode='receive'){
  const directory=mkdtempSync(path.join(HERE,'INERT_V8_'));
  const data=JSON.parse(execFileSync(PYTHON,['-I','-B',path.join(HERE,'test_fixture_worker.py'),directory,mode],{encoding:'utf8'}));
  assert.equal(data.fixture_scope,'SIMULATED_EXTERNAL_PROVENANCE_AND_BOUND_RECEIVER_ONLY');
  return {data,close:()=>rmSync(directory,{recursive:true,force:true})};
}
async function exercise(mode='receive',mutate=null,expireAction=null){
  const f=fixture(mode),{runtime,outcome,frame}=f.data;
  let clock=f.data.now_ms,execs=0,writes=0;
  if(mutate)mutate(outcome);
  const spec={schema:'dg16.github-public-observation-selection.v1',purpose:runtime.operator_receipt.purpose,
    operator:'PRO-EXECUTOR-01',actor:runtime.independent_receipt.actor,successor:'PRO-EXECUTOR-01, designated by owner',
    role:'live',operation_id:'INERT_INTERFACE_ONLY',source:runtime.operator_receipt.source,
    journal_root:runtime.journal_parent,expires_ms:runtime.expires_ms,context:runtime.operator_receipt.context,control:null};
  const selected={driver_source:descriptor(driver),operator_receipt:runtime.operator_receipt,
    body_outcome:runtime.body_outcome,receiver:runtime.receiver,
    semantic_source:{path:path.join(HERE,'semantic_receiver.py'),sha256:runtime.source_sha256,journal_parent:runtime.journal_parent}};
  if(mode==='receive')selected.selection=spec;
  else{
    selected.independent_receipt=runtime.independent_receipt;selected.expires_ms=runtime.expires_ms;
    selected.control={frame:JSON.parse(frame),leaves_path:runtime.control.leaves_path,leaves:runtime.control.leaves};
  }
  const supplied={...C,receive:async()=>runtime.independent_receipt};
  const tools={
    exec_command:async args=>{
      execs++;assert.match(args.cmd,/-I/);assert.match(args.cmd,/-B/);
      return{session_id:901,output:'READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME\r\n'};
    },
    write_stdin:async args=>{
      writes++;assert.equal(args.session_id,901);
      const newline=args.chars.indexOf('\n'),raw=args.chars.slice(newline+1);
      assert.equal(Number(args.chars.slice(0,newline)),descriptor(raw).bytes);
      assert.equal(raw,frame);
      return{exit_code:0,output:JSON.stringify(outcome)+'\r\n'};
    }
  };
  const D=vm.runInNewContext(driver,{tools,Date:class extends Date{static now(){return clock;}}});
  const admit=async bound=>({authorization:{ref:'INERT_TEST_ONLY',sha256:'a'.repeat(64)},
    assertCurrent:async({action})=>{if(action===expireAction)clock=outcome.expires_ms;},
    assertIndependent:async()=>{},assertControl:async()=>{}});
  try{
    const result=await (mode==='receive'?D.receive(supplied,selected,admit):D.prepareControl(supplied,selected,admit));
    return{result,outcome,execs,writes};
  }finally{f.close();}
}

test('new live outcome crosses recovered driver with the earlier REQUEST deadline',async()=>{
  const r=await exercise();
  assert.equal(r.result.status,'PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY');
  assert.equal(r.result.semantic_outcome.expires_ms,r.outcome.expires_ms);
  assert.equal(r.execs,1);assert.equal(r.writes,1);assert.equal(r.result.original_acceptance,false);
});
test('new control outcome crosses recovered driver preserving original evidence checks',async()=>{
  const r=await exercise('control');
  assert.equal(r.result.status,'LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY');
  assert.equal(r.result.semantic_outcome.original_control_checks.status,'ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_PASSED_DATA_ONLY');
  assert.equal(r.result.publication,false);
});
for(const action of ['semantic-process-completed','semantic-outcome-received']){
  test('earlier new helper deadline expiring at '+action+' refuses',async()=>{
    const r=await exercise('receive',null,action);
    assert.equal(r.result.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');
  });
}
test('noninteger new helper deadline is not accepted by the recovered driver',async()=>{
  const r=await exercise('receive',o=>{o.expires_ms=String(o.expires_ms);});
  assert.equal(r.result.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');
});

async function publicationAdmission(tamper){
  const f=fixture('control'),{runtime,outcome}=f.data;
  let admitted=false,providerCalls=0;
  if(tamper)outcome.original_control_checks.request_sha256='f'.repeat(64);
  const tools={exec_command:async()=>{providerCalls++;throw Error('NO_EFFECTS_IN_TEST');},
    mcp__codex_apps__github_fetch:async()=>{providerCalls++;throw Error('NO_EFFECTS_IN_TEST');},
    mcp__codex_apps__github_create_tree:async()=>{providerCalls++;throw Error('NO_EFFECTS_IN_TEST');},
    mcp__codex_apps__github_create_commit:async()=>{providerCalls++;throw Error('NO_EFFECTS_IN_TEST');},
    mcp__codex_apps__github_create_branch:async()=>{providerCalls++;throw Error('NO_EFFECTS_IN_TEST');}};
  const P=vm.runInNewContext(publisher,{tools});
  const selected={driver_source:descriptor(publisher),source:{...runtime.operator_receipt.source,
    semantic_path:path.join(HERE,'semantic_receiver.py'),semantic_sha256:runtime.source_sha256},
    journal_root:runtime.journal_parent,actor:'/root',context:runtime.operator_receipt.context,
    preparation:outcome,grant:'INERT_TEST_STRING_NOT_AN_EFFECT_GRANT',expires_ms:runtime.expires_ms,
    commit_message:'INERT TEST ONLY',publication_receipt:null};
  try{
    const result=await P.publish(C,selected,async bound=>{admitted=true;return null;});
    assert.equal(result.status,'REFUSED_OR_UNCERTAIN_NO_RETRY');assert.equal(providerCalls,0);
    return admitted;
  }finally{f.close();}
}
test('new original preparation satisfies recovered publisher data contract before external admission',async()=>{
  assert.equal(await publicationAdmission(false),true);
});
test('changed original review check prevents publisher admission',async()=>{
  assert.equal(await publicationAdmission(true),false);
});
