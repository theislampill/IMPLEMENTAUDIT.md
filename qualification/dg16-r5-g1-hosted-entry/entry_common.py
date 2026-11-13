"""External fixed entry, excluded from the packet manifest to avoid a cycle.

Final immutable workflow/tree receiving must bind this exact external file and
its three fixed wrappers. Root fills these compile-time bindings only after
whole-composition review. There are no command-line paths or authority modes.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

ENTRY_STATE = 'REVIEWED_EXACT_EXTERNAL_CARRIER_ENTRY'
CARRIER_LOADER_DESCRIPTOR = {'bytes': 4677, 'sha256': '3e9d4d947d8d98314813eee0aca09af1a501c050337c0c9132fcd915b9ba8f60'}
EXPECTED_PUBLIC_MANIFEST_SHA256 = '489db08e9bdea9fe12fce06672b3230e5e6423db89173a725d60d78e347ab7d0'
EXPECTED_BOOTSTRAP_ADMISSION_SHA256 = '24fa2ff4bb57d83cb3c48cee25120fdde6f1a0e2631ff76c057a9b197a5417ec'

def need(ok,code):
    if not ok:raise ValueError(code)

def _stamp(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid]

def _placement(modules,binding,ctx,phase):
    p=modules.policy;f=modules.files;paths=p.fixed_host_paths(ctx)
    raw,row=f.read_file(paths['packet']/'root_placement.py',1024*1024)
    need(row==binding['_opening_placement'],'EXTERNAL_PLACEMENT_BODY_CHANGED')
    module=types.ModuleType('carrier_entry_placement');module.__file__=str(paths['packet']/'root_placement.py')
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    observed=module.require_current(ctx,paths['packet'],phase=phase)
    need(type(observed) is dict and type(observed.get('receipt')) is dict,'EXTERNAL_PLACEMENT_RECEIPT_REQUIRED')
    receipt=observed['receipt']
    need(receipt.get('schema')=='dg16.fixed-root-placement-runtime.v1'
      and receipt.get('manifest_sha256')==EXPECTED_PUBLIC_MANIFEST_SHA256
      and receipt.get('bootstrap_admission_sha256')==EXPECTED_BOOTSTRAP_ADMISSION_SHA256,
      'EXTERNAL_BOOTSTRAP_RECEIPT_BINDING')
    return paths

def _open():
    need(ENTRY_STATE=='REVIEWED_EXACT_EXTERNAL_CARRIER_ENTRY','EXTERNAL_ENTRY_UNRESOLVED')
    need(sys.flags.isolated==1 and sys.dont_write_bytecode is True,'EXTERNAL_ISOLATED_INTERPRETER_REQUIRED')
    need(type(CARRIER_LOADER_DESCRIPTOR) is dict and set(CARRIER_LOADER_DESCRIPTOR)=={'bytes','sha256'}
      and type(CARRIER_LOADER_DESCRIPTOR['bytes']) is int and 0<CARRIER_LOADER_DESCRIPTOR['bytes']<=1024*1024,
      'EXTERNAL_LOADER_BINDING')
    for pin in (CARRIER_LOADER_DESCRIPTOR['sha256'],EXPECTED_PUBLIC_MANIFEST_SHA256,EXPECTED_BOOTSTRAP_ADMISSION_SHA256):
        need(type(pin) is str and re.fullmatch('[0-9a-f]{64}',pin),'EXTERNAL_BINDING_REQUIRED')
    run=os.environ.get('GITHUB_RUN_ID','');need(re.fullmatch('[1-9][0-9]{0,19}',run),'EXTERNAL_RUN_ID')
    path=Path('/dg16-g1-'+run)/'packet/carrier/carrier_loader.py'
    # The external workflow is the anchor. This first file read is fixed,
    # bounded, no-follow, and closed before any implementation is executed.
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==0
      and stat.S_IMODE(before.st_mode)==0o400 and before.st_size==CARRIER_LOADER_DESCRIPTOR['bytes'],
      'EXTERNAL_LOADER_FILE_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        need(_stamp(os.fstat(fd))==_stamp(before) and not os.listxattr(fd),'EXTERNAL_LOADER_OPEN_CHANGED')
        raw=os.pread(fd,1024*1024+1,0)
        need(len(raw)==before.st_size and hashlib.sha256(raw).hexdigest()==CARRIER_LOADER_DESCRIPTOR['sha256']
          and _stamp(os.fstat(fd))==_stamp(before) and _stamp(path.lstat())==_stamp(before),'EXTERNAL_LOADER_BODY_CHANGED')
    finally:os.close(fd)
    loader=types.ModuleType('exact_carrier_entry_loader');loader.__file__=str(path)
    exec(compile(raw,str(path),'exec'),loader.__dict__)
    modules=loader.load();binding=modules.policy.load();ctx=modules.carrier.host_context(binding)
    paths=_placement(modules,binding,ctx,'pre_prepare')
    def host_tool_anchor(current,current_context):
        need(current['_binding_raw']==binding['_binding_raw'] and current_context==ctx,'EXTERNAL_TOOL_CONTEXT_CHANGED')
        _placement(modules,current,current_context,'pre_prepare');modules.carrier.current_binding(current);loader.current()
        return dict(public_manifest_sha256=EXPECTED_PUBLIC_MANIFEST_SHA256,
          bootstrap_admission_sha256=EXPECTED_BOOTSTRAP_ADMISSION_SHA256)
    modules.host_tools._ANCHOR=host_tool_anchor
    modules.carrier.current_binding(binding);loader.current()
    return loader,modules,binding,ctx,paths

def observe_tools():
    loader,m,binding,ctx,_=_open()
    result=m.host_tools.observe(binding,ctx)
    m.carrier.current_binding(binding);_placement(m,binding,ctx,'pre_prepare');loader.current()
    return result

def adopt_tools():
    loader,m,binding,ctx,_=_open()
    result=m.host_tools.receive_adoption(binding,ctx,os.environ.get('DG16_CARRIER_READ_TOKEN'))
    m.carrier.current_binding(binding);_placement(m,binding,ctx,'pre_prepare');loader.current()
    return result

def public_tools(value):
    need(type(value) is dict and set(value)=={'files','result'},'EXTERNAL_TOOL_OBSERVATION_SHAPE')
    files=value['files'];result=value['result']
    need(type(files) is dict and set(files)=={'HOST_TOOL_OBSERVATION.json'}
      and type(files['HOST_TOOL_OBSERVATION.json']) is bytes and 0<len(files['HOST_TOOL_OBSERVATION.json'])<=65536,
      'EXTERNAL_TOOL_OBSERVATION_BOUND')
    need(result.get('status')=='OBSERVED' and result.get('command_executed') is False
      and result.get('crypto_capability_claim') is False,'EXTERNAL_READ_ONLY_TOOL_PHASE')
    return dict(schema='dg16.host-tool-observation-public-export.v1',authority='NONE',result=result,
      files_base64={'HOST_TOOL_OBSERVATION.json':base64.b64encode(files['HOST_TOOL_OBSERVATION.json']).decode('ascii')},original_awards=[])

def emit_tools(value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
    need(len(raw)<=131072,'EXTERNAL_TOOL_EXPORT_BOUND')
    sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()

def request():
    loader,m,binding,ctx,_=_open()
    result=m.carrier.host_request()
    m.carrier.current_binding(binding);_placement(m,binding,ctx,'pre_prepare');loader.current()
    return result

def receive():
    loader,m,binding,ctx,_=_open()
    result=m.carrier.host_receive(token=os.environ.get('DG16_CARRIER_READ_TOKEN'))
    m.carrier.current_binding(binding);_placement(m,binding,ctx,'pre_prepare');loader.current()
    return result

def prepare():
    loader,m,binding,ctx,paths=_open()
    available=m.carrier.require_ready()
    _placement(m,binding,ctx,'pre_prepare');m.carrier.current_binding(binding)
    raw,row=m.files.read_file(paths['packet']/'run.py',1024*1024)
    need(row==binding['_opening_core']['run.py'],'EXTERNAL_CORE_RUN_CHANGED')
    core=types.ModuleType('carrier_entry_exact_core');core.__file__=str(paths['packet']/'run.py')
    exec(compile(raw,core.__file__,'exec'),core.__dict__)
    # execute('prepare') enters the unchanged core require_complete_packet and
    # actual require_launch gates before source, output, NSS or native effects.
    code=core.execute('prepare',paths['source'],paths['output'],host_profile_binding=available['host_profile_binding'])
    loader.current()
    need(type(code) is int and code in (0,1),'EXTERNAL_CORE_RETURN')
    if code==0:_placement(m,binding,ctx,'live')
    return code

def public_request(value):
    need(type(value) is dict and set(value)=={'files','result'},'EXTERNAL_PUBLIC_REQUEST_SHAPE')
    files=value['files'];result=value['result']
    need(type(files) is dict and set(files) in (set(),{'REQUEST.json','RECIPIENT.pem'}),'EXTERNAL_PUBLIC_REQUEST_MEMBERS')
    public_result(result)
    if files:
        need(result.get('status')=='REQUEST_READY' and all(type(b) is bytes and 0<len(b)<=8192 for b in files.values()),
          'EXTERNAL_PUBLIC_REQUEST_BOUND')
    else:need(result.get('status')=='REFUSED','EXTERNAL_PUBLIC_REQUEST_REFUSAL')
    return dict(schema='dg16.core-private-recipient-public-export.v1',authority='NONE',result=result,
      files_base64={name:base64.b64encode(raw).decode('ascii') for name,raw in files.items()},original_awards=[])

def public_result(value):
    need(type(value) is dict and set(value)=={'schema','authority','status','code','request_sha256',
      'authenticated','staged','cleanup_complete','elapsed_ns','original_awards'}
      and value['schema']=='dg16.core-private-carrier-result.v1' and value['authority']=='NONE'
      and value['original_awards']==[] and value['status'] in ('REQUEST_READY','PAYLOAD_READY','INPUTS_READY','REFUSED'),
      'EXTERNAL_PUBLIC_RESULT')
    need(value['code'] in ('ACQUIRED','PRE_ENTRY_REFUSED','CMS_AUTHENTICATION_REFUSED','INPUT_RECEIVING_REFUSED',
      'CONTROL_REFUSED','CURRENTNESS_REFUSED','CLEANUP_REFUSED','INTERRUPTED','TOOL_OR_CAPTURE_REFUSED',
      'DEADLINE_EXPIRED','RESERVATION_REFUSED') and type(value['elapsed_ns']) is int and 0<=value['elapsed_ns']<=10**16
      and all(type(value[k]) is bool for k in ('authenticated','staged','cleanup_complete')),
      'EXTERNAL_PUBLIC_RESULT')
    pin=value['request_sha256']
    need((pin is None and value['status']=='REFUSED') or (type(pin) is str and re.fullmatch('[0-9a-f]{64}',pin)),
      'EXTERNAL_PUBLIC_REQUEST_DIGEST')
    return value

def emit(value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
    need(len(raw)<=32768,'EXTERNAL_PUBLIC_EXPORT_BOUND')
    sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()

def refused():
    return dict(schema='dg16.core-private-carrier-entry-refusal.v1',authority='NONE',status='REFUSED',
      code='EXTERNAL_ENTRY_OR_CURRENTNESS_REFUSED',original_awards=[])
