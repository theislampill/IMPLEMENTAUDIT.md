"""Root-only fixed sender and supported-tool dispatcher file interface.

The final root wrapper pins this external body and fills the fixed packet path.
It has no CLI URL/path/mode selector. Functions return a mechanical tool plan;
only root's separately reviewed dispatcher may execute the supported MCP call.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

ENTRY_STATE='UNRESOLVED_EXACT_ROOT_SENDER_ENTRY'
FIXED_PACKET_DIRECTORY=None
LOADER_DESCRIPTOR = {'bytes': 4677, 'sha256': 'f816f336899af6e690e83d4f88ace046bc48a0ebe00eaf1402153097f884dc29'}
_CACHE=None

def need(ok,code):
    if not ok:raise ValueError(code)

def load():
    global _CACHE
    need(ENTRY_STATE=='REVIEWED_EXACT_ROOT_SENDER_ENTRY','ROOT_SENDER_ENTRY_UNRESOLVED')
    need(sys.flags.isolated==1 and sys.dont_write_bytecode is True and os.getuid()==os.geteuid()>0,
      'ROOT_SENDER_DEDICATED_ISOLATED_NONROOT_PROCESS')
    need(type(FIXED_PACKET_DIRECTORY) is str and FIXED_PACKET_DIRECTORY.startswith('/')
      and '..' not in Path(FIXED_PACKET_DIRECTORY).parts,'ROOT_SENDER_FIXED_PACKET_REQUIRED')
    if _CACHE is not None:
        loader,m=_CACHE;loader.current();return loader,m
    path=Path(FIXED_PACKET_DIRECTORY)/'carrier/carrier_loader.py';info=path.lstat()
    need(type(LOADER_DESCRIPTOR) is dict and set(LOADER_DESCRIPTOR)=={'bytes','sha256'}
      and stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_uid==os.geteuid()
      and stat.S_IMODE(info.st_mode) in (0o400,0o444) and info.st_size==LOADER_DESCRIPTOR['bytes'],
      'ROOT_SENDER_LOADER_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)
    try:
        raw=os.pread(fd,1024*1024+1,0)
        need(len(raw)==info.st_size and hashlib.sha256(raw).hexdigest()==LOADER_DESCRIPTOR['sha256']
          and stamp(os.fstat(fd))==stamp(info) and stamp(path.lstat())==stamp(info) and not os.listxattr(fd),
          'ROOT_SENDER_LOADER_CURRENT_BODY')
    finally:os.close(fd)
    loader=types.ModuleType('fixed_root_carrier_loader');loader.__file__=str(path)
    exec(compile(raw,str(path),'exec'),loader.__dict__);m=loader.load();_CACHE=(loader,m)
    return loader,m

def inputs():
    loader,m=load();binding=m.policy.load()
    raw,_=m.files.read_file(binding['_base']/'PRO_SENDER_OPERATION.json',m.policy.MAX_INDEX)
    operation=m.policy.parse(raw,m.policy.MAX_INDEX)
    # Exact pinned sender_policy.load validates these fields before use.
    archive,_=m.files.read_file(binding['_packet'].parent/'ROOT_REQUEST_ARTIFACT.zip',m.policy.MAX_ARTIFACT,private=True)
    selection=m.sender_policy.load(binding,operation['context'],operation['artifact_id'],archive)
    m.carrier.current_binding(binding);m.sender_policy.current(selection);loader.current()
    return loader,m,binding,selection,archive

def sender():
    loader,m,binding,selection,archive=inputs();op=selection['operation'];ctx=op['context']
    value=m.carrier.root_payload(ctx['run_id'],ctx['workflow_commit'],op['artifact_id'],archive)
    # Only ciphertext and its public control remain at the fixed private path.
    # This function performs no remote publication, fetch or second encryption.
    files={}
    if value['result']['status']=='PAYLOAD_READY':
        directory=m.carrier.session_path(binding,ctx,root=True)
        for name,maximum in (('CONTROL.json',m.policy.MAX_CONTROL),('INPUTS.cms',m.policy.MAX_CIPHERTEXT)):
            raw,_=m.files.read_file(directory/name,maximum,private=True)
            need(raw==value['files'][name],'ROOT_SENDER_EXACT_OUTPUT_READBACK');files[name]=m.policy.descriptor(raw)
        m.carrier.current_binding(binding);m.sender_policy.current(selection);loader.current()
    return dict(schema='dg16.root-sender-terminal-export.v1',authority='NONE',result=value['result'],
      ciphertext_members=files,publication_performed=False,original_awards=[])

def _dispatch():
    loader,m,binding,selection,archive=inputs();ctx=selection['operation']['context']
    directory=m.carrier.session_path(binding,ctx,root=True)
    raw,_=m.files.read_file(directory/'BROKER_START.json',m.tool_broker.END_MAX,private=True)
    start=m.policy.parse(raw,m.tool_broker.END_MAX)
    store=m.tool_broker.Store(directory,binding,selection['operation'],start['deadline_monotonic'])
    return loader,m,binding,selection,store

def inspect(ordinal):
    loader,m,binding,selection,store=_dispatch()
    try:
        request,row=store.inspect_request(ordinal)
        m.sender_policy.current(selection);loader.current()
        return dict(request=request,request_sha256=row['sha256'],fetch_permitted=False)
    finally:store.close_fd()

def reserve(ordinal):
    loader,m,binding,selection,store=_dispatch()
    try:
        plan=store.reserve_dispatch(ordinal);m.sender_policy.current(selection);loader.current();return plan
    finally:store.close_fd()

def publish(ordinal,intent_sha256,actual_tool_result_raw,tool_call_ref):
    loader,m,binding,selection,store=_dispatch()
    try:
        received=store.publish_response(ordinal,intent_sha256,actual_tool_result_raw,tool_call_ref)
        m.sender_policy.current(selection);loader.current();return received
    finally:store.close_fd()

def main():
    need(len(sys.argv)==1,'ROOT_SENDER_FIXED_ENTRY_NO_ARGUMENTS')
    value=sender();raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    need(len(raw)<=32768,'ROOT_SENDER_PUBLIC_TERMINAL_BOUND');sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()
    return 0 if value['result']['status']=='PAYLOAD_READY' else 1

if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"schema":"dg16.root-sender-entry-refusal.v1","authority":"NONE","status":"REFUSED","original_awards":[]}',flush=True)
        code=1
    raise SystemExit(code)
