"""Fixed core input carrier. Shipped composition refuses before any effect.

These entry points create no workflow, provider publication, root grant or
original acceptance. A final reviewed host must call require_ready immediately
before the unchanged core require_launch. No private object is a public export.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import secrets
import signal
import stat
import sys
import time
import types
import bundle_codec as C
import carrier_policy as P
import carrier_io as F
import provider_reader as V
import sender_policy as SP
import sender_capture as SC
import tool_broker as B
import host_tools as HT

META_MAX = 4 * 1024**2
CAPTURE_STREAM_MAX = 32768
CAPTURE_OWNER_SHA256 = 'aa89ee1711c77d436850a0a669d3623207ba410be424097a272a604aca41fcdf'
_LOADER_CURRENT = None  # Injected only by the exact closed module loader.

def current_binding(binding):
    P.need(callable(_LOADER_CURRENT),'CARRIER_MODULE_CURRENTNESS_REQUIRED')
    _LOADER_CURRENT()
    closing=P.load()
    P.need(closing['_binding_raw']==binding['_binding_raw']
      and closing['_admission_raw']==binding['_admission_raw']
      and closing['_index']==binding['_index']
      and closing['_opening_core']==binding['_opening_core']
      and closing['_opening_contract']==binding['_opening_contract']
      and closing['_opening_placement']==binding['_opening_placement'],'CARRIER_CURRENT_INPUTS_CHANGED')

def placement_current(binding,ctx):
    paths=P.fixed_host_paths(ctx)
    P.need(binding['_packet']==paths['packet'] and binding['_base']==paths['packet']/'carrier','CARRIER_FIXED_ROOT_ISLAND_PATH')
    for path in (Path('/'),paths['island'],paths['packet']):
        info=path.lstat();mode=stat.S_IMODE(info.st_mode)
        P.need(stat.S_ISDIR(info.st_mode) and not path.is_symlink() and info.st_uid==0 and info.st_gid==0
          and (mode==0o700 if path!=Path('/') else mode&0o022==0),
          'CARRIER_ROOT_ISLAND_CUSTODY')
    raw,record=F.read_file(paths['packet']/'root_placement.py',1024*1024)
    P.need(record==binding['_opening_placement'],'CARRIER_PLACEMENT_MODULE_CHANGED')
    module=types.ModuleType('carrier_exact_root_placement');module.__file__=str(paths['packet']/'root_placement.py')
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    module.require_current(ctx,paths['packet'],phase='pre_prepare')
    current_binding(binding)
    return paths

def host_context(binding):
    e=os.environ
    P.need(os.geteuid()==0 and os.getuid()==0 and sys.platform=='linux' and os.uname().machine=='x86_64'
      and sys.version_info[:3]==(3,12,3),'CARRIER_ACTUAL_G1_HOST_PROFILE')
    os_raw,_=F.read_file(Path('/etc/os-release').resolve(strict=True),16384)
    facts=dict(line.split('=',1) for line in os_raw.decode().splitlines() if '=' in line and not line.startswith('#'))
    P.need(facts.get('ID','').strip('"')=='ubuntu' and facts.get('VERSION_ID','').strip('"')=='24.04','CARRIER_ACTUAL_G1_HOST_PROFILE')
    P.need(e.get('GITHUB_ACTIONS')=='true' and e.get('GITHUB_REPOSITORY')==P.REPOSITORY
      and e.get('GITHUB_EVENT_NAME')=='push' and e.get('GITHUB_REF')=='refs/heads/'+binding['branch']
      and e.get('GITHUB_RUN_ATTEMPT')=='1' and e.get('RUNNER_ENVIRONMENT')=='github-hosted'
      and e.get('GITHUB_JOB')==binding['job_name'],'CARRIER_FRESH_HOST_CONTEXT')
    ctx=dict(repository=P.REPOSITORY,branch=binding['branch'],workflow_commit=e.get('GITHUB_SHA'),
       workflow_path=binding['workflow_path'],run_id=e.get('GITHUB_RUN_ID'),run_attempt=1,job_name=binding['job_name'])
    P.context(ctx)
    P.need(e.get('GITHUB_WORKFLOW_SHA')==ctx['workflow_commit'] and
      e.get('GITHUB_WORKFLOW_REF')==P.REPOSITORY+'/'+ctx['workflow_path']+'@refs/heads/'+ctx['branch'],'CARRIER_WORKFLOW_ENVIRONMENT')
    placement_current(binding,ctx)
    return ctx

def host_identity():
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    P.need(len(boot)==36 and all(c in '0123456789abcdef-' for c in boot),'CARRIER_BOOT_ID')
    return dict(uid=os.getuid(),euid=os.geteuid(),gid=os.getgid(),egid=os.getegid(),boot_id=boot)

def session_path(binding,ctx,root=False):
    P.context(ctx)
    return binding['_packet'].parent / (('dg16-private-sender-' if root else 'dg16-private-recipient-')+ctx['run_id']+'-a1')

def receipt_raw(path):
    raw,_=F.read_file(path,META_MAX,private=True)
    return P.parse(raw,META_MAX)

def ensure_session(binding,ctx,directory):
    state=receipt_raw(directory/'SESSION.json')
    P.need(state.get('schema')=='dg16.actual-private-recipient-session.v1' and state.get('context')==ctx
      and state.get('host_identity')==host_identity() and state.get('binding_sha256')==P.sha(binding['_binding_raw'])
      and state.get('index_sha256')==C.check_index(binding['_index'])
      and state.get('directory_identity')==F.directory_id(directory.lstat())
      and state.get('directory_ancestry')==F.parents(directory/'marker'),'CARRIER_SAME_HOST_SESSION')
    P.need(type(state.get('deadline_monotonic')) in (int,float) and time.monotonic()<state['deadline_monotonic'],
       'CARRIER_ACQUISITION_EXPIRED')
    request,_=F.read_file(directory/'REQUEST.json',P.MAX_REQUEST,private=True)
    cert,cert_row=F.read_file(directory/'recipient.pem',P.MAX_CERTIFICATE,private=True)
    _,key_row=F.read_file(directory/'recipient.key',8192,private=True)
    P.need(cert_row==state['recipient_certificate'] and key_row==state['recipient_key'],'CARRIER_HELD_RECIPIENT_CHANGED')
    P.validate_request(request,cert,ctx,binding['_index'],int(time.time()*1000))
    P.need(P.sha(request)==state['request_sha256'],'CARRIER_REQUEST_CHANGED')
    current_binding(binding)
    return state,request,cert

def new_budget(directory,host=False):
    budget=F.Budget(P.MAX_PRIVATE_BYTES,P.MAX_PRIVATE_ENTRIES)
    if directory.exists():
        used,count=F.private_usage(directory,max(P.MAX_CIPHERTEXT,META_MAX));budget.reserve(used,count)
    else:budget.reserve(0,1)
    # Every later metadata/cleanup/ready record has an allocation reserved now.
    budget.reserve(8*1024**2,32)
    budget.metadata_bytes=0;budget.metadata_entries=0
    if host:budget.reserve(HT.MAX_PRIVATE_BYTES,HT.MAX_PRIVATE_ENTRIES)
    return budget

def metadata_reserve(budget,raw):
    P.need(type(raw) is bytes and budget.metadata_bytes+len(raw)<=8*1024**2
      and budget.metadata_entries+1<=32,'CARRIER_METADATA_ALLOCATION_BOUND')
    budget.metadata_bytes+=len(raw);budget.metadata_entries+=1

def host_usage(binding,ctx,recipient,installed=None):
    used,count=F.private_usage(recipient,max(P.MAX_CIPHERTEXT,META_MAX))
    tool_rows=HT.census(HT.directory(binding,ctx))
    used+=sum(row['bytes'] for row in tool_rows.values());count+=len(tool_rows)+1
    if installed is not None:
        used+=installed['total_bytes'];count+=len(installed['files'])+len(installed['directories'])
    P.need(used<=P.MAX_PRIVATE_BYTES and count<=P.MAX_PRIVATE_ENTRIES,'HOST_CARRIER_COMPLETE_ALLOCATION')
    return dict(bytes=used,entries=count)

def metadata(budget,path,raw,maximum=META_MAX):
    metadata_reserve(budget,raw);return F.write_once(path,raw,maximum)

def reserve(budget,directory,name,raw):
    metadata_reserve(budget,raw);return F.reserve(directory,name,raw)

def core_value(binding):
    raw,record=F.read_file(binding['_packet']/'HOST_COMPOSITION.json',P.MAX_INDEX)
    P.need(record==binding['_opening_core']['HOST_COMPOSITION.json'],'CARRIER_CORE_COMPOSITION_CHANGED')
    return P.parse(raw,P.MAX_INDEX,canonical=False)

def safe_outcome(status,code,request,authenticated,staged,cleanup,started):
    return P.public_result(status,code,P.sha(request) if request is not None else None,authenticated,staged,cleanup,
       max(0,time.monotonic_ns()-started))

def save_outcome(directory,outcome,cleanup,budget):
    value=dict(schema='dg16.private-carrier-terminal-custody.v1',authority='NONE',public=outcome,
      owned_cleanup=cleanup,original_awards=[])
    metadata(budget,directory/'OUTCOME.json',P.encode(value),META_MAX)

def private_secrets_absent(directory):
    """Unacquired or uncertain private outputs never become cleanup success."""
    if directory is None:return False
    try:
        info=directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or directory.is_symlink() or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o700:
            return False
        for name in ('recipient.key','quarantine.plain','bundle.plain'):
            try:(directory/name).lstat()
            except FileNotFoundError:continue
            return False
        return True
    except OSError:return False

class Commands:
    """Exact fixed command vectors through the retained actual capture owner.

    Constructor effects are future-only. Inert author controls never instantiate
    it. Fresh subreaper/current child custody and lowering-only resource limits
    are verified before the first command. No shell or caller-provided argv.
    """
    def __init__(self,binding,role,directory,budget,deadline,request_sha256=None):
        import ctypes
        P.need(role in ('host','root'),'CARRIER_COMMAND_ROLE')
        self.binding=binding;self.directory=directory;self.budget=budget;self.deadline=deadline;self.records=[]
        if request_sha256 is not None:P.digest(request_sha256)
        self.request_sha256=request_sha256;self.role=role
        self.tool_adoption=None;self.tool_phase=0
        if role=='host':
            self.tool_adoption=HT.ResolvedTools(binding,host_context(binding),
              'recipient' if request_sha256 is None else 'decrypt',os.environ.get('DG16_CARRIER_READ_TOKEN'))
            self.deadline=min(deadline,self.tool_adoption.deadline)
            self.tool_pins=self.tool_adoption.pins
            raw,row=F.read_file(binding['_packet']/'host_utility.py',65536)
            P.need(P.sha(raw)==CAPTURE_OWNER_SHA256 and row==binding['_opening_core']['host_utility.py'],'CARRIER_CAPTURE_OWNER_PIN')
            module=types.ModuleType('carrier_exact_capture_owner');module.__file__=str(binding['_packet']/'host_utility.py')
            exec(compile(raw,module.__file__,'exec'),module.__dict__);self.u=module
            self.capture_owner_sha256=CAPTURE_OWNER_SHA256
        else:
            P.need('_sender_selection' in binding,'EXPLICIT_PRO_SENDER_SELECTION_REQUIRED')
            SP.current(binding['_sender_selection']);self.tool_pins=binding['root_tools']
            self.u=SC.CaptureSession(directory,budget,lambda:self.current_tools(capture_callback=True))
            self.capture_owner_sha256=SC.QUALIFIER['sha256']
        self.tool_rows={}
        for name,expected in self.tool_pins.items():
            path=Path('/usr/bin')/name;body,observed=F.read_file(path,32*1024**2)
            P.need(P.descriptor(body)==expected and os.access(path,os.X_OK)
              and stat.S_IMODE(path.lstat().st_mode)&0o022==0,'CARRIER_ACTUAL_TOOL_PIN')
            self.tool_rows[name]=observed
        if role=='host':
            P.need(module.children()==[],'CARRIER_FOREIGN_CHILDREN_PRESENT')
            libc=ctypes.CDLL(None,use_errno=True)
            libc.prctl.argtypes=[ctypes.c_int,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong]
            libc.prctl.restype=ctypes.c_int
            P.need(libc.prctl(36,1,0,0,0)==0,'CARRIER_SUBREAPER_REFUSED')
            value=ctypes.c_int(0)
            P.need(libc.prctl(37,ctypes.addressof(value),0,0,0)==0 and value.value==1,'CARRIER_SUBREAPER_READBACK')
        for kind,limit in ((resource.RLIMIT_AS,P.MEMORY_BYTES),(resource.RLIMIT_FSIZE,P.MAX_CIPHERTEXT),
                           (resource.RLIMIT_CPU,binding['limits']['command_cpu_seconds'])):
            soft,hard=resource.getrlimit(kind)
            target=min(limit,hard) if hard!=resource.RLIM_INFINITY else limit
            if soft!=resource.RLIM_INFINITY:target=min(target,soft)
            P.need(target>0,'CARRIER_RESOURCE_UNAVAILABLE')
            resource.setrlimit(kind,(target,target))
            P.need(resource.getrlimit(kind)==(target,target),'CARRIER_RESOURCE_READBACK')
        self.cpu_profile=resource.getrlimit(resource.RLIMIT_CPU)
    def current_tools(self,capture_callback=False):
        for name,expected in self.tool_rows.items():
            _,row=F.read_file(Path('/usr/bin')/name,32*1024**2)
            P.need(row==expected,'CARRIER_TOOL_CURRENTNESS')
        current_binding(self.binding)
        if self.role=='root':SP.current(self.binding['_sender_selection'])
        elif not capture_callback:
            P.need(self.tool_phase<2,'HOST_TOOL_COMMAND_CURRENTNESS_ORDER')
            self.tool_adoption.recheck(('PRE','POST')[self.tool_phase]);self.tool_phase+=1
    def run(self,name,files):
        P.need(name in ('recipient','encrypt','decrypt') and name not in [r['operation'] for r in self.records],'CARRIER_COMMAND_ONCE')
        P.need((self.role=='root' and name=='encrypt') or (self.role=='host' and name in ('recipient','decrypt')),
          'CARRIER_ROLE_FIXED_COMMAND')
        self.current_tools();P.need(time.monotonic()<self.deadline,'CARRIER_COMMAND_DEADLINE')
        if name=='recipient':
            P.exact(files,('key','certificate'))
            args=['req','-x509','-newkey','rsa:3072','-noenc','-sha256','-days','1',
              '-subj','/CN=DG16-core-private-recipient','-keyout',files['key'].proc_path,'-out',files['certificate'].proc_path]
            maximum=8192
        elif name=='encrypt':
            P.exact(files,('plain','certificate','cipher'))
            args=['cms','-encrypt','-binary','-aes-256-gcm','-in',files['plain'].proc_path,'-outform','DER',
              '-out',files['cipher'].proc_path,'-recip',files['certificate'].proc_path,
              '-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
            maximum=P.MAX_CIPHERTEXT
        else:
            P.exact(files,('cipher','certificate','key','quarantine'))
            args=['cms','-decrypt','-binary','-inform','DER','-in',files['cipher'].proc_path,
              '-recip',files['certificate'].proc_path,'-inkey',files['key'].proc_path,'-out',files['quarantine'].proc_path]
            maximum=C.MAX_PLAINTEXT_BYTES
        # env is itself an exact body-pinned tool; credentials/configuration
        # selectors and inherited OpenSSL/loader variables never reach a child.
        argv=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',*args]
        self.budget.reserve(2*CAPTURE_STREAM_MAX+65536,3)
        before=[];rc=None;out=err=None;failure=None
        soft,hard=resource.getrlimit(resource.RLIMIT_FSIZE)
        P.need(hard>=maximum,'CARRIER_FILE_LIMIT_UNAVAILABLE')
        resource.setrlimit(resource.RLIMIT_FSIZE,(maximum,hard))
        try:
            rc,out,err=self.u.capture('carrier-'+name,argv,before,self.deadline,
                seconds=self.binding['limits']['command_seconds'],fds=tuple(item.fd for item in files.values()))
        except BaseException as exc:
            failure='CAPTURE_REFUSED'
            captured=getattr(exc,'captured',{})
            out=captured.get('stdout');err=captured.get('stderr');rc=captured.get('returncode')
        finally:
            resource.setrlimit(resource.RLIMIT_FSIZE,(soft,hard))
            for stream,raw in (('stdout',out),('stderr',err)):
                if type(raw) is bytes:F.write_once(self.directory/(name+'.'+stream),raw,CAPTURE_STREAM_MAX)
            record=dict(operation=name,capture=before,returncode=rc,streams_available=type(out) is bytes and type(err) is bytes,
                failure=failure,argv=argv,file_size_limit=maximum,cpu_limit=self.cpu_profile,
                binding_sha256=P.sha(self.binding['_binding_raw']),request_sha256=self.request_sha256,
                capture_owner_sha256=self.capture_owner_sha256,tool_descriptors=self.tool_pins)
            self.records.append(record);F.write_once(self.directory/('COMMAND_'+name+'.json'),P.encode(record),65536)
        P.need(failure is None and len(before)==1 and type(out) is bytes and type(err) is bytes,'CARRIER_CAPTURE_INCOMPLETE')
        capture=before[0]
        P.need(capture.get('process_started') is True and capture.get('pidfd_acquired') is True
          and capture.get('returncode')==rc and capture.get('streams_complete') is True
          and capture.get('cleanup',{}).get('echild') is True and capture.get('internal_failure') is None
          and capture.get('timeout') is False and capture.get('output_bound_exceeded') is False
          and capture.get('stdout_sha256')==P.sha(out) and capture.get('stderr_sha256')==P.sha(err)
          and capture.get('stdout_bytes')==len(out) and capture.get('stderr_bytes')==len(err),'CARRIER_ACTUAL_COMMAND_CUSTODY')
        for item in files.values():item.current()
        self.current_tools();return rc
    def closed(self):
        try:
            if self.role=='root':return self.u.closed()
            self.tool_adoption.recheck('CLOSE')
            return self.u.children()==[] and all(len(r['capture'])==1 and r['capture'][0].get('cleanup',{}).get('echild') is True for r in self.records)
        except BaseException:
            self.closing_refusal='CHILD_CENSUS_UNAVAILABLE'
            return False

def accept_authenticated(returncode,read_plaintext,index,request_sha256,core):
    # Do not call the reader, parse, log or install failed-decrypt output.
    P.need(type(returncode) is int and returncode==0,'CMS_AUTHENTICATION_REFUSED')
    raw=read_plaintext()
    bodies=C.unpack(raw,index,request_sha256)
    P.check_inputs(index,bodies,core)
    return bodies

def require_auth_enveloped(cipher):
    """Exact outer DER ContentInfo type only; OpenSSL verifies the AEAD tag.

    This is not a cryptographic verifier or a permissive CMS implementation.
    It excludes unauthenticated EnvelopedData before the decrypt command.
    """
    P.need(type(cipher) is bytes and 0<len(cipher)<=P.MAX_CIPHERTEXT,'CMS_CIPHERTEXT_BOUND')
    def tlv(pos,tag):
        P.need(pos+2<=len(cipher) and cipher[pos]==tag,'CMS_AUTH_ENVELOPED_TYPE')
        length=cipher[pos+1];start=pos+2
        if length&128:
            count=length&127
            P.need(1<=count<=4 and start+count<=len(cipher) and cipher[start]!=0,'CMS_DER_LENGTH')
            length=int.from_bytes(cipher[start:start+count],'big');start+=count
            P.need(length>=128,'CMS_DER_LENGTH')
        end=start+length;P.need(end<=len(cipher),'CMS_DER_LENGTH')
        return start,end
    start,end=tlv(0,0x30);P.need(end==len(cipher),'CMS_DER_TRAILING')
    oid_start,oid_end=tlv(start,0x06)
    P.need(cipher[oid_start:oid_end]==bytes.fromhex('2a864886f70d0109100117'),'CMS_AUTH_ENVELOPED_TYPE')
    explicit_start,explicit_end=tlv(oid_end,0xa0)
    inner_start,inner_end=tlv(explicit_start,0x30)
    P.need(explicit_end==end and inner_end==explicit_end and inner_start<inner_end,'CMS_AUTH_ENVELOPED_CONTAINER')
    return True

def verify_decrypt_record(binding,directory,request):
    """Reconsume actual capture and both stream bodies, not a READY boolean."""
    records={};bodies={}
    for name,limit in (('COMMAND_decrypt.json',65536),('decrypt.stdout',CAPTURE_STREAM_MAX),('decrypt.stderr',CAPTURE_STREAM_MAX)):
        bodies[name],records[name]=F.read_file(directory/name,limit,private=True)
    value=P.parse(bodies['COMMAND_decrypt.json'],65536)
    P.exact(value,('operation','capture','returncode','streams_available','failure','argv','file_size_limit','cpu_limit',
      'binding_sha256','request_sha256','capture_owner_sha256','tool_descriptors'))
    q=P.parse(request,P.MAX_REQUEST);ctx={k:q[k] for k in P.CONTEXT_KEYS}
    actual_host_tools=HT.read_ready(binding,ctx)['pins']
    P.need(value['operation']=='decrypt' and value['returncode']==0 and type(value['returncode']) is int
      and value['streams_available'] is True and value['failure'] is None
      and value['binding_sha256']==P.sha(binding['_binding_raw']) and value['request_sha256']==P.sha(request)
      and value['capture_owner_sha256']==CAPTURE_OWNER_SHA256 and value['tool_descriptors']==actual_host_tools
      and value['file_size_limit']==C.MAX_PLAINTEXT_BYTES,'ACTUAL_DECRYPT_RECORD_SCOPE')
    P.need(type(value['capture']) is list and len(value['capture'])==1,'ACTUAL_DECRYPT_CAPTURE_POPULATION')
    row=value['capture'][0]
    P.need(row.get('process_started') is True and row.get('pidfd_acquired') is True and row.get('returncode')==0
      and row.get('streams_complete') is True and row.get('cleanup',{}).get('echild') is True
      and row.get('internal_failure') is None and row.get('timeout') is False
      and row.get('output_bound_exceeded') is False,'ACTUAL_DECRYPT_CUSTODY')
    for name in ('stdout','stderr'):
        raw=bodies['decrypt.'+name]
        P.need(row.get(name+'_bytes')==len(raw) and row.get(name+'_sha256')==P.sha(raw),'ACTUAL_DECRYPT_STREAM_BODY')
    args=value['argv'];fixed=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null',
       '/usr/bin/openssl','cms','-decrypt','-binary','-inform','DER','-in',None,'-recip',None,'-inkey',None,'-out',None]
    P.need(type(args) is list and len(args)==len(fixed),'ACTUAL_DECRYPT_ARGV')
    fds=[]
    for observed,expected in zip(args,fixed):
        if expected is None:
            P.need(type(observed) is str and observed.startswith('/proc/self/fd/') and observed[14:].isdigit(),'ACTUAL_DECRYPT_ARGV')
            fds.append(observed)
        else:P.need(observed==expected,'ACTUAL_DECRYPT_ARGV')
    P.need(len(set(fds))==4,'ACTUAL_DECRYPT_FD_ALIAS')
    cpu=value['cpu_limit'];P.need(type(cpu) is list and len(cpu)==2 and cpu[0]==cpu[1],'ACTUAL_DECRYPT_CPU_SCOPE')
    P.integer(cpu[0],1,binding['limits']['command_cpu_seconds'])
    return records

def retained_receiving(binding,directory,request,control_commit=None):
    records=verify_decrypt_record(binding,directory,request)
    names={'CONTROL.json':P.MAX_CONTROL,'INPUTS.cms':P.MAX_CIPHERTEXT,'recipient.pem':P.MAX_CERTIFICATE,
       'REQUEST.json':P.MAX_REQUEST,'SESSION.json':META_MAX,'SELECTED_CONTROL.json':META_MAX,
       'CONTROL_PROVIDER.json':P.MAX_METADATA,'CONSUME_RESERVED.json':65536}
    bodies={}
    for name,limit in names.items():bodies[name],records[name]=F.read_file(directory/name,limit,private=True)
    P.need(bodies['REQUEST.json']==request,'RETAINED_REQUEST_CHANGED')
    q=P.parse(request,P.MAX_REQUEST);ctx={k:q[k] for k in P.CONTEXT_KEYS}
    P.validate_request(request,bodies['recipient.pem'],ctx,binding['_index'],int(time.time()*1000))
    P.validate_control(bodies['CONTROL.json'],bodies['INPUTS.cms'],request,int(time.time()*1000))
    selected=P.parse(bodies['SELECTED_CONTROL.json'],META_MAX)
    observed=P.parse(bodies['CONTROL_PROVIDER.json'],P.MAX_METADATA)
    P.exact(observed,('ref','commit','tree','closing_ref'))
    P.need(observed['ref']==observed['closing_ref'] and observed['commit']['sha']==selected['commit'],
      'RETAINED_CONTROL_PROVIDER_BINDING')
    if control_commit is not None:
        P.need(control_commit==selected['commit'],'CARRIER_READY_CONTROL_COMMIT')
    blobs={}
    import base64
    for name in ('CONTROL.json','INPUTS.cms'):
        raw=bodies[name];git=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        blobs[git]=dict(sha=git,size=len(raw),encoding='base64',content=base64.b64encode(raw).decode())
    files=V.check_control(observed['ref'],observed['commit'],observed['tree'],blobs,binding['control_branch'],binding['control_parent'])
    P.need(files=={n:bodies[n] for n in ('CONTROL.json','INPUTS.cms')}
      and selected['control_sha256']==P.sha(bodies['CONTROL.json'])
      and selected['ciphertext']==P.descriptor(bodies['INPUTS.cms']),'RETAINED_CONTROL_BODY_CHANGED')
    reserved=P.parse(bodies['CONSUME_RESERVED.json'],65536)
    P.need(reserved==dict(request_sha256=P.sha(request),nonce=q['nonce']),'RETAINED_CONSUMPTION_RESERVATION')
    return records

def host_request():
    started=time.monotonic_ns();directory=None;handles=[];commands=None;request=None;owned_directory=False;budget=None
    try:
        binding=P.load();ctx=host_context(binding);current_binding(binding)
        P.need(not (binding['_packet']/'private-inputs').exists(),'FRESH_HOST_INPUT_DESTINATION_REQUIRED')
        adopted=HT.read_ready(binding,ctx)
        directory=session_path(binding,ctx);fd,identity=F.private_directory(directory);os.close(fd);owned_directory=True
        budget=new_budget(directory,host=True);nonce=secrets.token_hex(32);issued=int(time.time()*1000)
        deadline=min(time.monotonic()+binding['limits']['acquisition_seconds'],adopted['ready']['command_deadline_monotonic'])
        reserve(budget,directory,'RECIPIENT_RESERVED.json',P.encode(dict(context=ctx,nonce=nonce,issued_unix_ms=issued)))
        key=F.OutputFile(directory,'recipient.key',8192,budget);handles.append(key)
        cert=F.OutputFile(directory,'recipient.pem',P.MAX_CERTIFICATE,budget);handles.append(cert)
        commands=Commands(binding,'host',directory,budget,deadline)
        P.need(commands.run('recipient',dict(key=key,certificate=cert))==0,'RECIPIENT_CREATION_REFUSED')
        key_raw=key.read();cert_raw=cert.read()
        P.need(key_raw.startswith(b'-----BEGIN PRIVATE KEY-----\n') and key_raw.endswith(b'-----END PRIVATE KEY-----\n')
          and cert_raw.startswith(b'-----BEGIN CERTIFICATE-----\n') and cert_raw.endswith(b'-----END CERTIFICATE-----\n'),'RECIPIENT_BODY_FORMAT')
        request=P.make_request(ctx,binding['_index'],cert_raw,nonce,issued,
          min(issued+binding['limits']['acquisition_seconds']*1000,adopted['adoption']['expires_unix_ms']))
        metadata(budget,directory/'REQUEST.json',request,P.MAX_REQUEST)
        _,key_row=F.read_file(directory/'recipient.key',8192,private=True)
        _,cert_row=F.read_file(directory/'recipient.pem',P.MAX_CERTIFICATE,private=True)
        current_binding(binding);P.need(host_context(binding)==ctx and commands.closed(),'RECIPIENT_CLOSING_CUSTODY')
        P.need(time.monotonic()<deadline,'CARRIER_ACQUISITION_EXPIRED')
        session=dict(schema='dg16.actual-private-recipient-session.v1',context=ctx,host_identity=host_identity(),
          directory_identity=identity,directory_ancestry=F.parents(directory/'marker'),binding_sha256=P.sha(binding['_binding_raw']),
          index_sha256=C.check_index(binding['_index']),request_sha256=P.sha(request),recipient_key=key_row,
          recipient_certificate=cert_row,deadline_monotonic=deadline,started_monotonic_ns=started,original_awards=[])
        metadata(budget,directory/'SESSION.json',P.encode(session),META_MAX)
        host_usage(binding,ctx,directory)
        for handle in handles:handle.retain_close()
        return dict(files={'REQUEST.json':request,'RECIPIENT.pem':cert_raw},
          result=safe_outcome('REQUEST_READY','ACQUIRED',request,False,False,False,started))
    except BaseException:
        cleanup=[handle.cleanup() for handle in handles if not handle.closed]
        complete=owned_directory and private_secrets_absent(directory) and all(row['unlinked'] and row['descriptor_closed'] for row in cleanup) and (commands is None or commands.closed())
        result=safe_outcome('REFUSED','PRE_ENTRY_REFUSED' if directory is None else 'TOOL_OR_CAPTURE_REFUSED',request,False,False,complete,started)
        if owned_directory and budget is not None:save_outcome(directory,result,cleanup,budget)
        return dict(files={},result=result)

def root_payload(run_id,workflow_commit,artifact_id,archive,token=None):
    """Root-only local preparation; returns no private body and publishes none."""
    started=time.monotonic_ns();directory=None;handles=[];commands=None;request=None;files={};error=None;owned_directory=False;budget=None;broker=None
    try:
        P.need(token is None,'PRO_SENDER_SUPPORTED_TOOL_ONLY_NO_HTTP_CREDENTIAL')
        binding=P.load();deadline=time.monotonic()+binding['limits']['acquisition_seconds']
        ctx=dict(repository=P.REPOSITORY,branch=binding['branch'],workflow_commit=workflow_commit,
          workflow_path=binding['workflow_path'],run_id=run_id,run_attempt=1,job_name=binding['job_name'])
        P.context(ctx);selection=SP.load(binding,ctx,artifact_id,archive);binding['_sender_selection']=selection
        deadline=min(deadline,time.monotonic()+(selection['operation']['expires_unix_ms']-int(time.time()*1000))/1000)
        # This first parse supplies a reservation digest only, never provenance.
        request=V.artifact_files(archive)['REQUEST.json'];directory=session_path(binding,ctx,root=True)
        fd,_=F.private_directory(directory);os.close(fd);owned_directory=True;budget=new_budget(directory)
        reserve(budget,directory,'SEND_RESERVED.json',P.encode(dict(request_sha256=P.sha(request),context=ctx)))
        metadata(budget,directory/'REQUEST_ARTIFACT.zip',archive,P.MAX_ARTIFACT)
        broker=B.Store(directory,binding,selection['operation'],deadline,budget=budget,create=True)
        received=B.receive_request(binding,ctx,artifact_id,archive,broker)
        P.need(received.request_raw==request,'PRO_SENDER_RECEIVED_REQUEST_CHANGED')
        bodies,opening=F.acquire(binding['_packet']/'private-inputs',binding['_index'])
        P.check_inputs(binding['_index'],bodies,core_value(binding))
        encoded=C.pack(binding['_index'],bodies,P.sha(request))
        plain=F.OutputFile(directory,'bundle.plain',C.MAX_PLAINTEXT_BYTES,budget);handles.append(plain);plain.write(encoded)
        cert=F.OutputFile(directory,'recipient.pem',P.MAX_CERTIFICATE,budget);handles.append(cert);cert.write(received.certificate)
        cipher=F.OutputFile(directory,'INPUTS.cms',P.MAX_CIPHERTEXT,budget);handles.append(cipher)
        receipt=received.recheck();metadata(budget,directory/'REQUEST_RECEIVING_BEFORE.json',P.encode(receipt),META_MAX)
        metadata(budget,directory/'REQUEST_PROVIDER_BEFORE.json',P.encode(received.observed),P.MAX_METADATA)
        commands=Commands(binding,'root',directory,budget,deadline,P.sha(request))
        P.need(commands.run('encrypt',dict(plain=plain,certificate=cert,cipher=cipher))==0,'CMS_ENCRYPTION_REFUSED')
        encrypted=cipher.read()
        require_auth_enveloped(encrypted)
        P.need(encrypted and plain.read()==encoded and cert.read()==received.certificate,'SENDER_INPUT_CLOSING_CHANGED')
        F.recheck(binding['_packet']/'private-inputs',binding['_index'],opening)
        current_binding(binding);receipt=received.recheck()
        receipt_raw=P.encode(receipt);metadata(budget,directory/'REQUEST_RECEIVING_AFTER.json',receipt_raw,META_MAX)
        metadata(budget,directory/'REQUEST_PROVIDER_AFTER.json',P.encode(received.observed),P.MAX_METADATA)
        control=P.make_control(request,encrypted,P.sha(receipt_raw),int(time.time()*1000))
        metadata(budget,directory/'CONTROL.json',control,P.MAX_CONTROL)
        files={'CONTROL.json':control,'INPUTS.cms':encrypted}
    except BaseException:error='INPUT_RECEIVING_REFUSED';files={}
    cleanup=[]
    for handle in handles:
        if handle.closed:continue
        if files and handle.name=='INPUTS.cms':
            try:
                handle.retain_close();cleanup.append(dict(name=handle.name,retained_ciphertext=True,descriptor_closed=True));continue
            except BaseException:error='CURRENTNESS_REFUSED';files={}
        cleanup.append(handle.cleanup())
    broker_complete=False
    if broker is not None:
        try:
            closing=broker.finish(bool(files));broker_complete=closing['complete']
            metadata(budget,directory/'TOOL_BROKER_CLOSING.json',P.encode(closing),META_MAX)
        except BaseException:
            error='CURRENTNESS_REFUSED';files={}
        finally:broker.close_fd()
    complete=owned_directory and private_secrets_absent(directory) and all((row.get('unlinked') or row.get('retained_ciphertext'))
      and row['descriptor_closed'] for row in cleanup) and (commands is None or commands.closed())
    if files and not broker_complete:error='CURRENTNESS_REFUSED';files={}
    if not complete:error='CLEANUP_REFUSED';files={}
    result=safe_outcome('PAYLOAD_READY' if files else 'REFUSED','ACQUIRED' if files else (error or 'PRE_ENTRY_REFUSED'),request,False,False,complete,started)
    if owned_directory and budget is not None:
        save_outcome(directory,result,cleanup,budget)
        F.private_usage(directory,max(P.MAX_CIPHERTEXT,META_MAX))
    return dict(files=files,result=result)

def host_receive(token=None):
    started=time.monotonic_ns();directory=None;handles=[];commands=None;request=None
    authenticated=False;installed=None;selected=None;binding=None;ctx=None;error=None
    reserved=False;stage_cleanup=None
    try:
        binding=P.load();ctx=host_context(binding);directory=session_path(binding,ctx)
        session,request,certificate=ensure_session(binding,ctx,directory)
        budget=new_budget(directory,host=True)
        reserve(budget,directory,'CONSUME_RESERVED.json',P.encode(dict(request_sha256=P.sha(request),nonce=P.parse(request,P.MAX_REQUEST)['nonce'])))
        reserved=True
        key=F.HeldFile(directory,'recipient.key',session['recipient_key'],8192);handles.append(key)
        cert=F.HeldFile(directory,'recipient.pem',session['recipient_certificate'],P.MAX_CERTIFICATE);handles.append(cert)
        api=V.GitHubReads(binding,token,session['deadline_monotonic'])
        while selected is None:
            ensure_session(binding,ctx,directory)
            selected=V.control(api)
            if selected is None:
                remaining=session['deadline_monotonic']-time.monotonic()
                P.need(remaining>0,'CARRIER_ACQUISITION_EXPIRED')
                time.sleep(min(binding['limits']['poll_seconds'],remaining))
        fields=selected['files'];P.validate_control(fields['CONTROL.json'],fields['INPUTS.cms'],request,int(time.time()*1000))
        require_auth_enveloped(fields['INPUTS.cms'])
        metadata(budget,directory/'CONTROL.json',fields['CONTROL.json'],P.MAX_CONTROL)
        metadata(budget,directory/'CONTROL_PROVIDER.json',P.encode(selected['provider']),P.MAX_METADATA)
        metadata(budget,directory/'SELECTED_CONTROL.json',P.encode(dict(commit=selected['commit'],
          control_sha256=P.sha(fields['CONTROL.json']),ciphertext=P.descriptor(fields['INPUTS.cms']),reads=selected['reads'])),META_MAX)
        cipher=F.OutputFile(directory,'INPUTS.cms',P.MAX_CIPHERTEXT,budget);handles.append(cipher);cipher.write(fields['INPUTS.cms'])
        quarantine=F.OutputFile(directory,'quarantine.plain',C.MAX_PLAINTEXT_BYTES,budget);handles.append(quarantine)
        commands=Commands(binding,'host',directory,budget,session['deadline_monotonic'],P.sha(request))
        rc=commands.run('decrypt',dict(cipher=cipher,certificate=cert,key=key,quarantine=quarantine))
        bodies=accept_authenticated(rc,quarantine.read,binding['_index'],P.sha(request),core_value(binding))
        authenticated=True
        P.need(cipher.read()==fields['INPUTS.cms'] and cert.read()==certificate,'RECIPIENT_CLOSING_BODY_CHANGED')
        ensure_session(binding,ctx,directory)
        ref=api.get('ref',binding['control_branch'])
        P.need(ref.get('object',{}).get('sha')==selected['commit'],'CONTROL_CHANGED_BEFORE_INSTALL')
        budget.reserve(sum(row['bytes'] for row in binding['_index'].values()),len(binding['_index'])+len(F.directories(binding['_index'])))
        installed=F.stage(binding['_packet'],binding['_index'],bodies,P.parse(request,P.MAX_REQUEST)['nonce'])
        current_binding(binding);P.need(host_context(binding)==ctx,'CARRIER_HOST_CHANGED')
        F.recheck(binding['_packet']/'private-inputs',binding['_index'],installed,private=True)
        ref=api.get('ref',binding['control_branch'])
        P.need(ref.get('object',{}).get('sha')==selected['commit'],'CONTROL_CHANGED_AFTER_INSTALL')
    except BaseException as exc:
        stage_cleanup=getattr(exc,'stage_cleanup',None)
        error='CMS_AUTHENTICATION_REFUSED' if str(exc)=='CMS_AUTHENTICATION_REFUSED' else 'INPUT_RECEIVING_REFUSED'
    cleanup=[]
    for handle in handles:
        if handle.closed:continue
        if error is None and installed is not None and handle.name in ('recipient.pem','INPUTS.cms'):
            try:
                handle.retain_close();cleanup.append(dict(name=handle.name,retained_public_body=True,descriptor_closed=True))
                continue
            except BaseException:error='CURRENTNESS_REFUSED'
        cleanup.append(handle.cleanup())
    if error is not None and installed is not None:
        stage_cleanup=F.discard_stage(binding['_packet']/'private-inputs',binding['_index'],installed)
    complete=reserved and private_secrets_absent(directory) and all((row.get('unlinked') or row.get('retained_public_body')) and row['descriptor_closed'] for row in cleanup) and (commands is None or commands.closed())
    if stage_cleanup is not None:
        cleanup.append(dict(stage_cleanup=stage_cleanup));complete=complete and stage_cleanup['complete']
    if not complete:error='CLEANUP_REFUSED'
    if error is None and installed is not None:
        try:
            P.need(time.monotonic()<session['deadline_monotonic'],'CARRIER_ACQUISITION_EXPIRED')
            current_binding(binding);P.need(host_context(binding)==ctx and host_identity()==session['host_identity'],'CARRIER_HOST_CHANGED')
            F.recheck(binding['_packet']/'private-inputs',binding['_index'],installed,private=True)
            retained=retained_receiving(binding,directory,request)
            ready=dict(schema='dg16.actual-core-private-inputs-ready.v1',authority='NONE',context=ctx,
               host_identity=session['host_identity'],directory_identity=session['directory_identity'],
               binding_sha256=P.sha(binding['_binding_raw']),request_sha256=P.sha(request),control_commit=selected['commit'],
               input_index_sha256=C.check_index(binding['_index']),installed=installed,authenticated=True,
               cleanup_complete=True,carrier_elapsed_ns=time.monotonic_ns()-session['started_monotonic_ns'],
               retained_bodies=retained,deadline_monotonic=session['deadline_monotonic'],core_or_native_effect_grant=False,original_awards=[])
            metadata(budget,directory/'READY.json',P.encode(ready),META_MAX)
            host_usage(binding,ctx,directory,installed)
        except BaseException:error='CURRENTNESS_REFUSED'
    result=safe_outcome('INPUTS_READY' if error is None and installed is not None else 'REFUSED',
       'ACQUIRED' if error is None and installed is not None else (error or 'PRE_ENTRY_REFUSED'),request,
       authenticated,installed is not None,complete,started)
    if reserved:save_outcome(directory,result,cleanup,budget)
    return result

def successful_terminal(outcome,request_sha256):
    """A successful label cannot override contradictory closing evidence."""
    P.exact(outcome,('schema','authority','public','owned_cleanup','original_awards'))
    P.need(outcome['schema']=='dg16.private-carrier-terminal-custody.v1' and outcome['authority']=='NONE'
      and outcome['original_awards']==[],'CARRIER_TERMINAL_SCOPE')
    public=outcome['public']
    P.exact(public,('schema','authority','status','code','request_sha256','authenticated','staged',
      'cleanup_complete','elapsed_ns','original_awards'))
    expected=P.public_result('INPUTS_READY','ACQUIRED',request_sha256,True,True,True,public['elapsed_ns'])
    P.need(P.encode(public)==P.encode(expected),'CARRIER_TERMINAL_SUCCESS_CONJUNCTION')
    expected_cleanup=[
      dict(name='recipient.key',unlinked=True,descriptor_closed=True,identity_confirmed=True),
      dict(name='recipient.pem',retained_public_body=True,descriptor_closed=True),
      dict(name='INPUTS.cms',retained_public_body=True,descriptor_closed=True),
      dict(name='quarantine.plain',unlinked=True,descriptor_closed=True,identity_confirmed=True)]
    P.need(P.encode(outcome['owned_cleanup'])==P.encode(expected_cleanup),'CARRIER_TERMINAL_OWNED_CLEANUP')
    return True

def require_ready():
    """Call in the same host immediately before unchanged core require_launch."""
    binding=P.load();ctx=host_context(binding);directory=session_path(binding,ctx)
    actual_tools=HT.ResolvedTools(binding,ctx,'prepare',os.environ.get('DG16_CARRIER_READ_TOKEN'))
    ready=receipt_raw(directory/'READY.json');outcome=receipt_raw(directory/'OUTCOME.json')
    P.exact(ready,('schema','authority','context','host_identity','directory_identity','binding_sha256','request_sha256',
       'control_commit','input_index_sha256','installed','authenticated','cleanup_complete','carrier_elapsed_ns',
       'retained_bodies','deadline_monotonic','core_or_native_effect_grant','original_awards'))
    P.need(type(ready['control_commit']) is str and P.re.fullmatch('[0-9a-f]{40}',ready['control_commit']),
      'CARRIER_READY_CONTROL_COMMIT')
    P.need(ready.get('schema')=='dg16.actual-core-private-inputs-ready.v1' and ready.get('authority')=='NONE' and ready.get('context')==ctx
      and ready.get('host_identity')==host_identity() and ready.get('binding_sha256')==P.sha(binding['_binding_raw'])
      and ready.get('directory_identity')==F.directory_id(directory.lstat())
      and ready.get('input_index_sha256')==C.check_index(binding['_index']) and ready.get('authenticated') is True
      and ready.get('cleanup_complete') is True and ready.get('core_or_native_effect_grant') is False
      and ready.get('original_awards')==[],'CARRIER_READY_SCOPE')
    P.need((directory/'CONSUME_RESERVED.json').is_file() and not (directory/'recipient.key').exists()
      and not (directory/'quarantine.plain').exists(),'CARRIER_SECRET_DISPOSAL')
    request,_=F.read_file(directory/'REQUEST.json',P.MAX_REQUEST,private=True)
    P.need(P.sha(request)==ready['request_sha256'],'CARRIER_READY_REQUEST')
    successful_terminal(outcome,P.sha(request))
    q=P.parse(request,P.MAX_REQUEST)
    P.need(int(time.time()*1000)<=q['expires_unix_ms'] and time.monotonic()<ready['deadline_monotonic'],'CARRIER_READY_EXPIRED')
    P.need(retained_receiving(binding,directory,request,ready['control_commit'])==ready['retained_bodies'],
      'CARRIER_RETAINED_PHYSICAL_CHANGED')
    bodies,observed=F.acquire(binding['_packet']/'private-inputs',binding['_index'],private=True)
    P.need(observed==ready['installed'],'CARRIER_READY_PHYSICAL_CHANGED')
    P.check_inputs(binding['_index'],bodies,core_value(binding));current_binding(binding)
    actual_tools.recheck('CLOSE')
    host_usage(binding,ctx,directory,observed)
    return dict(status='RECEIVED_EXACT_PRIVATE_INPUT_AVAILABILITY',authority='NONE',input_index_sha256=ready['input_index_sha256'],
        request_sha256=ready['request_sha256'],control_commit=ready['control_commit'],original_awards=[],core_or_native_effect_grant=False)
