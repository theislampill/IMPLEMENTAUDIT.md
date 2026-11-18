// Bounded regression for the actual Root driver's host receipt receiver.
// Only deterministic host-protocol fixtures are used; no tool or GitHub call.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';

const file=process.argv[2];
const source=fs.readFileSync(file,'utf8');
const match=source.match(/  async function runPython\(source,args\)\{([\s\S]*?)\n  \}\n  async function save/);
assert(match,'actual runPython owner function not found');
const owner='async function runPython(source,args){'+match[1]+'\n  }';
const rows=[];
async function check(name,sequence,{accept=false,wantedError=null,advance=0}={}){
  let executions=0,polls=0,now=100000;
  const hostReceipts=[];
  const actual=[];
  const next=()=>{const item=sequence.shift();assert(item,'unexpected host invocation');actual.push(item);now+=advance;return item;};
  const tools={
    exec_command:async a=>{executions++;assert.equal(executions,1,'command replay');assert.equal(a.yield_time_ms,1000);return next();},
    write_stdin:async a=>{polls++;assert.equal(a.session_id,42,'different process polled');assert.equal(a.chars,'','poll supplied input');return next();},
  };
  const codec={strict:JSON.parse,descriptor:s=>({bytes:Buffer.byteLength(s),sha256:crypto.createHash('sha256').update(s).digest('hex')})};
  const context={tools,codec,hostReceipts,cfg:{spec:{expires_ms:120000}},policy:{repo:'/test-only'},
    quote:s=>"'"+s.replace(/'/g,"'\\''")+"'",need:(v,c)=>{if(!v)throw Error(c);},
    Date:{now:()=>now}};
  const run=vm.runInNewContext('('+owner+')',context);
  let value,error;
  try{value=await run('print(0)',[]);}catch(e){error=e;}
  if(accept){assert.equal(error,undefined,'valid yielded command was not received: '+error);assert.deepEqual(value,{ok:true});assert.equal(sequence.length,0);}
  else {assert(error,'invalid host outcome accepted');if(wantedError)assert.match(String(error),wantedError);}
  assert.equal(executions,1,'command must never be reinvoked');
  return {name,executions,polls,accepted:!error,error:error?String(error):null,host_receipts:hostReceipts.length};
}
const cases=[
  ['immediate terminal JSON',[{output:'{"ok":true}\n',exit_code:0}],{accept:true}],
  ['yield then receive same command',[{output:'{"ok":',session_id:42},{output:'true}\n',exit_code:0}],{accept:true}],
  ['multiple yields preserve chunks and identity',[{output:'',session_id:42},{output:'{"ok":',session_id:42},{output:'true}\n',exit_code:0}],{accept:true}],
  ['terminal failure stays refusal',[{output:'failure',exit_code:1}],{}],
  ['missing terminal and session stays refusal',[{output:''}],{}],
  ['changed session stays refusal',[{output:'',session_id:42},{output:'',session_id:43}],{}],
  ['expired wait stays refusal without reinvocation',[{output:'',session_id:42}],{advance:20001}],
  ['invalid completed JSON stays refusal',[{output:'not JSON',exit_code:0}],{}],
];
for(const [name,sequence,options] of cases){
  try{rows.push({...await check(name,sequence,options),status:'PASS'});}
  catch(error){rows.push({name,status:'FAIL',error:String(error)});}
}
console.log(JSON.stringify({schema:'dg16.root-host-receiving-regression.v1',driver:file,driver_sha256:crypto.createHash('sha256').update(source).digest('hex'),fixture_only:true,actual_tools_called:0,rows},null,2));
if(rows.some(x=>x.status==='FAIL'))process.exitCode=1;
