// @exec: {"yield_time_ms": 1000, "max_output_tokens": 2000}
// Root executes only the exact late-bound reviewed file in functions.exec.
// This file never starts the sender or issues an admission. Its logical call
// references join the journal to actual root tool history, not native tool IDs.
const HELPER_PATH = null;
const HELPER_SHA256 = null;
const PYTHON = "/usr/local/bin/python3";
function need(v,c){if(!v)throw Error(c);}
const TRANSPORT_CHUNK_BYTES = 8192;
const OP_EXPIRES_UNIX_MS = null;
function psLiteral(s){
 need(typeof s==='string' && !/[\u0000\r\n]/.test(s),'NON_LITERAL_HELPER_ARGUMENT');
 return "'"+s.replaceAll("'","''")+"'";
}
function wslCommand(python,loader,path,pin,action,...args){
 need(python==='/usr/bin/python3' && path.startsWith('/') && /^[0-9a-f]{64}$/.test(pin),'WSL_SENDER_BINDING');
 const tokens=['C:\\Windows\\System32\\wsl.exe','--distribution','Ubuntu','--user','agent','--cd','/','--exec',
  python,'-I','-B','-c',loader,path,pin,action,...args];
 const cmd="$PSNativeCommandArgumentPassing='Standard'; & "+tokens.map(psLiteral).join(' ')+"; exit $LASTEXITCODE";
 need(cmd.length<=18000,'WINDOWS_COMMAND_BOUND');
 return cmd;
}

function utf8(s){
 const out=[];
 for(const ch of s){let n=ch.codePointAt(0);
  if(n<128)out.push(n);
  else if(n<2048)out.push(192|(n>>6),128|(n&63));
  else if(n<65536)out.push(224|(n>>12),128|((n>>6)&63),128|(n&63));
  else out.push(240|(n>>18),128|((n>>12)&63),128|((n>>6)&63),128|(n&63));
 }
 return out;
}
function base64(bytes){
 const chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';let out='';
 for(let i=0;i<bytes.length;i+=3){const a=bytes[i],b=bytes[i+1],c=bytes[i+2];out+=chars[a>>2]+chars[((a&3)<<4)|((b??0)>>4)]+(b===undefined?'=':chars[((b&15)<<2)|((c??0)>>6)])+(c===undefined?'=':chars[c&63]);}
 return out;
}
function jsonValue(value,depth=0){
 need(depth<=100,'ACTUAL_TOOL_RESULT_DEPTH');
 if(value===null||typeof value==='string'||typeof value==='boolean')return;
 if(typeof value==='number'){need(Number.isFinite(value),'ACTUAL_TOOL_NONFINITE');return;}
 need(typeof value==='object','ACTUAL_TOOL_NON_JSON');
 if(Array.isArray(value)){for(const x of value)jsonValue(x,depth+1);return;}
 need(Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null,'ACTUAL_TOOL_NONPLAIN_OBJECT');
 for(const key of Object.keys(value))jsonValue(value[key],depth+1);
}
async function helper(action,...args){
 need(typeof HELPER_PATH==='string'&&HELPER_PATH.startsWith('/')&&/^[0-9a-f]{64}$/.test(HELPER_SHA256),'UNRESOLVED_EXACT_DISPATCHER');
 const loader="import hashlib,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); pin=sys.argv[2]; s=p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode) in (0o400,0o444) and 0<s.st_size<=1048576; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC); raw=os.pread(fd,1048577,0); mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns); assert len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==pin and mark(os.fstat(fd))==mark(s) and mark(p.lstat())==mark(s) and not os.listxattr(fd); os.close(fd); sys.argv=[str(p),*sys.argv[3:]]; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})";
 const cmd=wslCommand(PYTHON,loader,HELPER_PATH,HELPER_SHA256,action,...args.map(String));
 let response=await tools.exec_command({cmd,login:false,yield_time_ms:1000,max_output_tokens:5000});
 let output=response.output;
 while(response.exit_code==null && response.session_id!=null){
  need(Number.isSafeInteger(OP_EXPIRES_UNIX_MS) && Date.now()<OP_EXPIRES_UNIX_MS,
       'EXPIRED_HELPER_COMPLETION_UNKNOWN_SESSION_'+response.session_id);
  response=await tools.write_stdin({session_id:response.session_id,chars:'',yield_time_ms:1000,max_output_tokens:5000});
  output+=response.output;
  need(output.length<=32768,'HELPER_RESPONSE_BOUND');
 }
 // An unknown helper completion never causes automatic invocation replay.
 need(response.exit_code===0&&response.session_id===undefined,'HELPER_REFUSED_OR_COMPLETION_UNKNOWN');
 const value=JSON.parse(output.trim());need(value&&typeof value==='object','HELPER_RESPONSE');return value;
}
async function dispatch(){
 const opening=await helper('initialize');need(opening.status==='INITIALIZED','JOURNAL_OPEN');
 for(let ordinal=0;ordinal<18;ordinal++){
  for(;;){
   const ready=await helper('ready',ordinal);
   if(ready.status==='READY')break;
   need(ready.status==='PENDING'&&ready.fetch_permitted===false,'READINESS_REFUSED');
   await new Promise(resolve=>setTimeout(resolve,50));
  }
  const reserved=await helper('reserve',ordinal);const plan=reserved.plan;
  need(reserved.status==='RESERVED_ONCE'&&reserved.remaining_ms>0&&plan.ordinal===ordinal&&plan.tool==='mcp__codex_apps__github_fetch'&&Object.keys(plan.arguments).length===1&&typeof plan.arguments.url==='string','EXACT_RESERVED_FIXED_READ');
  // Exactly one supported GET occurs after both O_EXCL intents. There is no
  // retry, alternate fetch, timeout Promise.race or synthetic result envelope.
  const actual=await tools.mcp__codex_apps__github_fetch({url:plan.arguments.url});
  jsonValue(actual);need(actual!==null&&!Array.isArray(actual)&&typeof actual==='object','FULL_CALL_TOOL_RESULT_REQUIRED');
  const raw=JSON.stringify(actual)+'\n';const bytes=utf8(raw);need(bytes.length>0&&bytes.length<=4194304,'ACTUAL_RESULT_BOUND');
  let final;
  for(let offset=0;offset<bytes.length;offset+=TRANSPORT_CHUNK_BYTES){
   const chunk=bytes.slice(offset,offset+TRANSPORT_CHUNK_BYTES);final=await helper('chunk',ordinal,offset,base64(chunk));
   need(final.status==='CHUNK_RETAINED'&&final.bytes===offset+chunk.length,'ACTUAL_RESULT_CHUNK_READBACK');
  }
  const retained=await helper('complete',ordinal,bytes.length,final.sha256,plan.intent_sha256);
  need(retained.status==='ACTUAL_FULL_RESULT_RETAINED'&&retained.receipt.logical_tool_call_ref===reserved.logical_tool_call_ref,'ACTUAL_RESULT_JOURNAL_JOIN');
  const published=await helper('publish',ordinal);
  need(published.status==='PUBLISHED'&&published.ordinal===ordinal&&published.broker_status==='RECEIVED'&&published.fetch_permitted===false,'BROKER_REFUSED_OR_LATE_RESULT');
  notify({dispatcher:'EXACT_FIXED_READ_RETAINED_AND_PUBLISHED',ordinal,logical_tool_call_ref:reserved.logical_tool_call_ref,actual_tool_result:retained.receipt.tool_result});
 }
 const terminal=await helper('finish');need(terminal.status==='DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE','DISPATCHER_CLOSURE');text(terminal);
}
await dispatch();
