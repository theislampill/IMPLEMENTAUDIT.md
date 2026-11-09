"""Root-invoked source assembly only. No sender, tools, control or crypto run.

Run on the independently received nonroot POSIX installation only, after real
recipient receiving and actual Root issuance. The qualification fixture runner
is not this CLI. Output is fresh, private, and refuses automatic replay.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import types

READER_SHA='378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
ASSEMBLER_SHA='97408df8058e6c8c8bab754ed8f9df8edf3f930ac4f47dd466c16eda9732f3cb'
PHASE_SHA='7a391c1c74329b1298349a85d3df25013707d0eb09044cf8583b3ea8bc9a038c'
DISPATCHER_SHA='d83c761dbc666d78856cf2d52ced4db2b6b8d373742deef4938b2d4b6434938f'

def need(ok,code):
    if not ok:raise ValueError(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def private_read(read,path,maximum):
    p=Path(path);before=p.lstat()
    mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid()
      and stat.S_IMODE(before.st_mode) in (0o400,0o600),'PRIVATE_SOURCE_INPUT_CUSTODY')
    raw=read(p,maximum)
    need(type(raw) is bytes and mark(p.lstat())==mark(before),'PRIVATE_SOURCE_READ_CONTRACT_OR_CHANGE')
    return raw

def physical_reader(reader_path):
    # Bootstrap one already Root-qualified, literal-pinned reader source.
    path=Path(reader_path);need(path.is_absolute() and path.resolve(strict=True)==path,'ROOT_READER_PATH')
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid()
      and stat.S_IMODE(before.st_mode) in (0o400,0o444),'ROOT_READER_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        need(mark(os.fstat(fd))==mark(before) and not os.listxattr(fd),'ROOT_READER_OPEN')
        raw=os.pread(fd,1024**2,0)
        need(len(raw)==before.st_size and sha(raw)==READER_SHA and mark(os.fstat(fd))==mark(before)==mark(path.lstat()),'ROOT_READER_BODY')
    finally:os.close(fd)
    # Reuse only the exact physical-I/O module embedded in Root's receiver.
    # Its public receiving/transport surface is neither copied nor modified.
    nodes=[]
    for n in ast.parse(raw).body:
        if (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)
          and n.value.func.id=='exec' and n.value.args and isinstance(n.value.args[0],ast.Call)
          and isinstance(n.value.args[0].func,ast.Name) and n.value.args[0].func.id=='compile'):
            first=n.value.args[0].args[0]
            if isinstance(first,ast.Constant) and isinstance(first.value,bytes):nodes.append(first.value)
    need(len(nodes)==1,'ONE_ROOT_PHYSICAL_READER')
    module=types.ModuleType('actual_root_physical_io');exec(compile(nodes[0],'<pinned-root-physical-io>','exec'),module.__dict__)
    return module.read_file

def main():
    need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0
      and sys.flags.isolated and sys.dont_write_bytecode,'ACTUAL_ROOT_NONROOT_POSIX_SOURCE_PROCESS_REQUIRED')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('stage','host-phase','root-reader','dispatcher-source'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--late-inputs',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--private-inputs',type=Path)
    p.add_argument('--preflight',action='store_true')
    p.add_argument('--dispatcher-selection',type=Path)
    p.add_argument('--late-receiving',type=Path)
    a=p.parse_args();read=physical_reader(a.root_reader)
    local=Path(__file__).resolve().parent
    raw=read(local/'late_sender_current04_v2.py',1024**2);need(sha(raw)==ASSEMBLER_SHA,'ASSEMBLER_SOURCE_PIN')
    L=types.ModuleType('actual_current04_late_assembly');L.__file__=str(local/'late_sender_current04_v2.py')
    exec(compile(raw,L.__file__,'exec'),L.__dict__)
    phase_raw=read(a.host_phase/'PHASE.json',1024**2);need(sha(phase_raw)==PHASE_SHA,'ACTUAL_CURRENT04_HOST_PHASE')
    phase=json.loads(phase_raw);host={}
    for name,pin in phase['members'].items():
        need(not name.startswith('/') and '..' not in Path(name).parts,'FIXED_PHASE_MEMBER')
        body=read(a.host_phase/name,32*1024**2);need(L.desc(body)==pin,'HOST_PHASE_MEMBER_CHANGED');host[name]=body
    source_index=json.loads(read(a.stage/'AUTHOR_SOURCE_INDEX.json',1024**2))['members']
    template_raw=read(a.stage/'source-support/inputs/TEMPLATE_INDEX.json',1024**2)
    need(sha(template_raw)==L.AUTHOR_PINS['inputs/TEMPLATE_INDEX.json'],'PINNED_TEMPLATE_INDEX_BEFORE_MEMBER_READS')
    template_index=json.loads(template_raw)
    expected_names=set(L.AUTHOR_PINS)|{'templates/'+n for n in template_index}
    need(len(expected_names)==46 and set(source_index)==expected_names,'EXACT_AUTHOR_NAMES_BEFORE_PAYLOAD_IO')
    for name in expected_names:
        need(not name.startswith('/') and '..' not in Path(name).parts and '\\' not in name
          and ':' not in name and '\0' not in name,'FIXED_AUTHOR_NAME')
        expected_sha=L.AUTHOR_PINS[name] if name in L.AUTHOR_PINS else template_index[name[len('templates/'):]]['sha256']
        need(source_index[name]['sha256']==expected_sha,'AUTHOR_DESCRIPTOR_BEFORE_PAYLOAD_IO')
    author_bodies={n:read(a.stage/'source-support'/n,32*1024**2) for n in source_index}
    author=L.Author(author_bodies,source_index)
    broker=read(a.stage/'source-support/root_tool_broker.py',1024**2)
    private_index=author.C.parse(host[L.CORE+'carrier/INPUT_INDEX.json'])
    private_root=a.private_inputs if a.private_inputs is not None else a.stage/'stage/packet/private-inputs'
    root_stat=private_root.lstat()
    need(private_root.is_absolute() and private_root.resolve(strict=True)==private_root and stat.S_ISDIR(root_stat.st_mode)
      and root_stat.st_uid==os.geteuid() and stat.S_IMODE(root_stat.st_mode)==0o700,'ACTUAL_PRIVATE_SOURCE_DIRECTORY')
    inputs={'private-inputs/'+n:private_read(read,private_root/n,32*1024**2) for n in private_index}
    need({n[len('private-inputs/'):]:L.desc(body) for n,body in inputs.items()}==private_index,'ACTUAL_PRIVATE_SOURCE_INDEX')
    deriver=read(a.dispatcher_source,1024**2);need(sha(deriver)==DISPATCHER_SHA,'CORRECTED_DISPATCHER_SOURCE')
    if a.preflight:
        need(a.late_inputs is None and a.output is None and a.dispatcher_selection is None and a.late_receiving is None,
          'PREFLIGHT_HAS_NO_LATE_OR_OUTPUT_EFFECT')
        staged=L.stage(author,host,broker,{n[len('private-inputs/'):]:body for n,body in inputs.items()})
        print(json.dumps(dict(authority='NONE',status='STATIC_SOURCE_PRIVATE_INPUTS_AND_DISPATCHER_RECEIVED',
          staged_members=len(staged),private_source_members=len(private_index),late_inputs='FIVE_ACTUAL_ROOT_BODIES_REQUIRED',
          sender_started=False,actual_crypto_or_provider_or_control=False,original_awards=[])))
        return
    need(a.late_inputs is not None and a.output is not None,'ACTUAL_LATE_INPUTS_AND_OUTPUT_REQUIRED')
    late_names={'ROOT_SENDER_ASSEMBLY_SELECTION.json','PRO_SENDER_OPERATION.json','PRO_SENDER_ADMISSION.json',
      'ROOT_REQUEST_ARTIFACT.zip','HOST_PUBLICATION_ROOT_RECEIVING.json'}
    need({x.name for x in a.late_inputs.iterdir()}==late_names,'EXACT_FIVE_ACTUAL_ROOT_LATE_BODIES')
    inputs.update({n:private_read(read,a.late_inputs/n,4*1024**2) for n in late_names})
    operation=author.C.parse(inputs['PRO_SENDER_OPERATION.json'])
    need(operation['sender_uid']==os.getuid()==os.geteuid() and operation['sender_gid']==os.getgid()==os.getegid(),
      'ACTUAL_SENDER_IDENTITY')
    def current():
        need(operation['issued_unix_ms']<=time.time_ns()//1000000<operation['expires_unix_ms'],'ACTUAL_OPERATION_EXPIRED')
    current();files=L.assemble(author,host,broker,inputs)
    selection=author.C.parse(inputs['ROOT_SENDER_ASSEMBLY_SELECTION.json'])
    need(a.output.is_absolute() and a.output.parent.resolve(strict=True)==a.output.parent and not os.path.lexists(a.output)
      and str(a.output/'packet')==selection['fixed_packet_directory'],'FRESH_ROOT_SELECTED_OUTPUT')
    if a.dispatcher_selection is not None:
        need(a.late_receiving is not None,'ACTUAL_LATE_RECEIVING_REQUIRED')
        files['DISPATCHER_ADMISSION_REQUIREMENTS.json']=L.dispatcher_requirements(deriver,files,
          author.C.parse(read(a.dispatcher_selection,65536)),read(a.late_receiving,4*1024**2))
    current();a.output.mkdir(mode=0o700)
    for name,body in files.items():
        current();target=a.output/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        mode=0o600 if name.startswith('packet/private-inputs/') or name=='ROOT_REQUEST_ARTIFACT.zip' else 0o400
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
        try:
            view=memoryview(body)
            while view:
                count=os.write(fd,view);need(count>0,'SHORT_SOURCE_WRITE');view=view[count:]
            os.fsync(fd)
        finally:os.close(fd)
        need(read(target,32*1024**2)==body,'LATE_SOURCE_READBACK')
    current()
    print(json.dumps(dict(authority='NONE',source_files=len(files),sender_started=False,
      dispatcher_admission_issued=False,provider_or_control_effects=False,actual_currentness_or_root_authentication='ROOT_SEPARATE_RECEIVING_REQUIRED',original_awards=[])))

if __name__=='__main__':main()
