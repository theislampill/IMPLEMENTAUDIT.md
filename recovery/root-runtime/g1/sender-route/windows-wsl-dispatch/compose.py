"""Adapt only transport of the reviewed root dispatch template to Windows and WSL."""
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parent/'recovered-g1-g3-root-binding-r2/author/dispatch.js'
ORIGINAL_BINDER=ORIGINAL.with_name('bind_dispatcher.py')

def once(s,old,new):
    if s.count(old)!=1: raise ValueError(old)
    return s.replace(old,new)

def compose():
    raw=ORIGINAL.read_bytes()
    s=raw.decode('utf8')
    start=s.index('function shell(s){')
    end=s.index('function utf8(s){',start)
    s=s[:start]+(HERE/'windows_transport.js.in').read_text('utf8')+'\n'+s[end:]
    old="const cmd=[PYTHON,'-I','-B','-c',loader,HELPER_PATH,HELPER_SHA256,action,...args.map(String)].map(shell).join(' ');"
    new="const cmd=wslCommand(PYTHON,loader,HELPER_PATH,HELPER_SHA256,action,...args.map(String));"
    s=once(s,old,new)
    s=once(s,'offset+=49152','offset+=TRANSPORT_CHUNK_BYTES')
    s=once(s,'offset+49152','offset+TRANSPORT_CHUNK_BYTES')
    # Unknown completion does not reissue an action or a GET. Set no new
    # budget on the actual helper. Continue a yielded command via its own ID.
    s=once(s,"const response=await tools.exec_command({cmd,yield_time_ms:1000,max_output_tokens:5000});",
    """let response=await tools.exec_command({cmd,login:false,yield_time_ms:1000,max_output_tokens:5000});
 let output=response.output;
 while(response.exit_code==null && response.session_id!=null){
  need(Number.isSafeInteger(OP_EXPIRES_UNIX_MS) && Date.now()<OP_EXPIRES_UNIX_MS,
       'EXPIRED_HELPER_COMPLETION_UNKNOWN_SESSION_'+response.session_id);
  response=await tools.write_stdin({session_id:response.session_id,chars:'',yield_time_ms:1000,max_output_tokens:5000});
  output+=response.output;
  need(output.length<=32768,'HELPER_RESPONSE_BOUND');
 }""")
    s=once(s,"JSON.parse(response.output.trim())","JSON.parse(output.trim())")
    return raw,s.encode()

def binder():
    source=ORIGINAL_BINDER.read_text('utf8')
    anchor=" helper=read(BASE/'dispatcher_entry.py');"
    source=once(source,anchor," need(selection['python_path']=='/usr/bin/python3','WSL_SELECTED_INTERPRETER')\n"+anchor)
    anchor=" out={'dispatcher_entry.py':helper"
    inject=""" need(js.count('const OP_EXPIRES_UNIX_MS = null;')==1,'DISPATCH_EXPIRY_PLACEHOLDER')
 opraw=read(Path(b['operation_path']));need(desc(opraw)==b['operation'],'WSL_OPERATION_CHANGED')
 js=js.replace('const OP_EXPIRES_UNIX_MS = null;', 'const OP_EXPIRES_UNIX_MS = '+str(json.loads(opraw)['expires_unix_ms'])+';')
"""
    return once(source,anchor,inject+anchor).encode()

if __name__=='__main__':
    baseline,output=compose()
    (HERE/'dispatch.js').write_bytes(output)
    (HERE/'bind_dispatcher.py').write_bytes(binder())
    print(hashlib.sha256(baseline).hexdigest(),hashlib.sha256(output).hexdigest())
