"""Explicit Pro encryption capture using the exact maintained child custodian.

The maintained launch method is not used: it closes the carrier's pass-FDs.
This adapter has no role, command, executable, working-directory or signal
selection API. Loading is inert; capture is a separately admitted real effect.
The whole sender runs inside the verified sender sandbox (launch/enter_sender_sandbox below);
every capture currentness point rechecks it (require_sender_sandbox).
"""
import ast
import copy
import errno
import fcntl
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import sys
import time
import types
import carrier_policy as P
import carrier_io as F

PROFILE='MAINTAINED_OWNER_THREE_FD_ENCRYPTION_V1'
QUALIFIER=dict(bytes=268686,sha256='79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b')
COMPILER=dict(bytes=262144,sha256='0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d')
OWNER_AST_SHA256='ef5d9af63757b3fcda8d76f90567c66e9d61bba32a7251ccd8873acc1b16be1f'
STREAM_MAX=32768
OWNER_EVIDENCE_MAX=2*1024**2
CLOSE_SECONDS=3.0
FD_LIMIT=4096
# The fixed sandbox launcher. Its exact bytes are the carrier's sender_tools['bwrap'] pin, checked and
# rechecked by carrier.Commands with the other sender tools; the exec is bound to that verified file.
SANDBOX='/usr/bin/bwrap'
SANDBOX_PREFIX=[SANDBOX,'--unshare-all','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL',
  '--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',
  '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LC_ALL','C',
  '--setenv','OPENSSL_CONF','/dev/null']

class CaptureRefusal(ValueError):
    pass

def load_owner():
    base=Path(__file__).absolute().parent/'maintained';raws={};records={}
    for name,pin in (('QUALIFIER.py',QUALIFIER),('COMPILER.py',COMPILER)):
        raw,row=F.read_file(base/name,1024*1024)
        P.need(P.descriptor(raw)==pin,'SENDER_MAINTAINED_SOURCE_PIN')
        raws[name]=raw;records[name]=row
    tree=ast.parse(raws['QUALIFIER.py'])
    nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_CaptureChildren']
    P.need(len(nodes)==1 and P.sha(ast.dump(nodes[0],include_attributes=False).encode())==OWNER_AST_SHA256,
      'SENDER_MAINTAINED_CLASS_PIN')
    errors=[n for n in ast.parse(raws['COMPILER.py']).body if isinstance(n,ast.ClassDef) and n.name=='WorkGraphError']
    P.need(len(errors)==1,'SENDER_MAINTAINED_ERROR_TYPE')
    wg=types.SimpleNamespace();error_ns={}
    exec(compile(ast.Module(body=errors,type_ignores=[]),str(base/'COMPILER.py'),'exec'),error_ns)
    wg.WorkGraphError=error_ns['WorkGraphError']
    ns=dict(WG=wg,os=os,sys=sys,signal=signal,time=time,errno=errno,re=re,Path=Path,ROOT=Path('/'))
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(base/'QUALIFIER.py'),'exec'),ns)
    return ns['_CaptureChildren'],records

def source_current(opening):
    base=Path(__file__).absolute().parent/'maintained'
    for name,expected in opening.items():
        _,row=F.read_file(base/name,1024*1024);P.need(row==expected,'SENDER_MAINTAINED_SOURCE_CHANGED')

def validate_command(label,argv,fds):
    P.need(label=='carrier-encrypt' and type(fds) is tuple and len(fds)==3
      and all(type(fd) is int and 3<=fd<2**31 for fd in fds) and len(set(fds))==3,'SENDER_THREE_HELD_FDS')
    plain,certificate,cipher=fds
    expected=SANDBOX_PREFIX+['/usr/bin/openssl',
      'cms','-encrypt','-binary','-aes-256-gcm','-in','/proc/self/fd/'+str(plain),'-outform','DER',
      '-out','/proc/self/fd/'+str(cipher),'-recip','/proc/self/fd/'+str(certificate),
      '-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
    P.need(type(argv) is list and argv==expected,'SENDER_FIXED_ENCRYPT_COMMAND')
    return True

def launcher_fd(pinned):
    """Open the sandbox launcher once; it must be the carrier-pinned file (identity and bytes).

    The child fexecve()s this descriptor, so the executed file is the verified one, not a later path lookup.
    """
    P.need(type(pinned) is dict and type(pinned.get('identity')) is list,'SENDER_SANDBOX_LAUNCHER_BINDING')
    fd=os.open(SANDBOX,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        P.need(F.stamp(before)==pinned['identity'] and 0<before.st_size<=32*1024**2,'SENDER_SANDBOX_LAUNCHER_BINDING')
        chunks=[];offset=0
        while True:
            raw=os.pread(fd,1024*1024,offset)
            if not raw:break
            chunks.append(raw);offset+=len(raw);P.need(offset<=before.st_size,'SENDER_SANDBOX_LAUNCHER_BINDING')
        P.need(P.descriptor(b''.join(chunks))==dict(bytes=pinned['bytes'],sha256=pinned['sha256'])
          and F.stamp(os.fstat(fd))==pinned['identity'],'SENDER_SANDBOX_LAUNCHER_BINDING')
        return fd
    except BaseException:
        os.close(fd);raise

def close_plan(visible,kept,error_fd,exec_fd):
    P.need(type(visible) is list and len(visible)<=FD_LIMIT and len(visible)==len(set(visible))
      and all(type(fd) is int and 0<=fd<2**31 for fd in visible),'SENDER_DESCRIPTOR_POPULATION')
    P.need(len(kept)==3 and error_fd not in kept and exec_fd not in kept and exec_fd!=error_fd,'SENDER_ERROR_FD_ALIAS')
    return [fd for fd in visible if fd>2 and fd not in kept and fd!=error_fd and fd!=exec_fd]

def append_stream(prefix,chunk):
    P.need(type(prefix) is bytes and type(chunk) is bytes and len(prefix)<=STREAM_MAX,'SENDER_STREAM_SHAPE')
    remaining=STREAM_MAX-len(prefix)
    return prefix+chunk[:remaining],len(chunk)>remaining

def descriptor_snapshot():
    rows=[]
    with os.scandir('/proc/self/fd') as entries:
        names=[]
        for entry in entries:
            P.need(entry.name.isdigit() and len(names)<FD_LIMIT,'SENDER_DESCRIPTOR_POPULATION')
            names.append(int(entry.name))
    for fd in sorted(names):
        try:s=os.fstat(fd)
        except OSError as exc:
            if exc.errno==errno.EBADF:continue  # The closed directory iterator only.
            raise
        flags=fcntl.fcntl(fd,fcntl.F_GETFD);status=fcntl.fcntl(fd,fcntl.F_GETFL)
        values=[fd,s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,flags,status]
        P.need(all(type(n) is int and 0<=n<2**64 for n in values),'SENDER_DESCRIPTOR_VALUE')
        rows.append(values)
    return rows

def kernel_echild():
    try:os.waitid(os.P_ALL,0,os.WEXITED|os.WNOHANG|os.WNOWAIT|0x40000000)
    except ChildProcessError:return True
    return False

def restoration_ok(facts):
    return all(facts.get(k) is True for k in ('echild','mask_restored','handlers_restored','subreaper_restored',
      'descriptors_restored','owned_descriptors_closed'))

# Whole-sender restriction (G132 v3). The entire sender process -- from before its first private read
# through cleanup, including its tool-broker GitHub reads -- runs as the original nonroot UID inside the pinned
# sender bwrap: no_new_privs, every capability (bounding set included) dropped, new user/mount/pid/net/ipc/uts
# namespaces, a cleared environment, and a read-only root holding only /usr, /proc, /dev, a private /tmp and the
# exact placement (packet read-only; its parent, the one writable directory). /usr trees that a retained
# supplementary group could read beyond 'other' are masked (group_masks). The sender needs no network:
# GitHub is read only by the external root dispatcher, through tool_broker files in the session directory.
SENDER_ENTRY='sender_launch.py'
ENTRY=dict(bytes=2086,sha256='1845fbfadb63133063211e67eb1771f4b19174eef9fd2ea9c30dae7087e0f073')
SENDER_ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','PWD':'/'}
SANDBOX_DEVICES=('/dev/null','/dev/zero','/dev/full','/dev/random','/dev/urandom','/dev/tty','/dev/pts')
SANDBOX_TOP=('bin','dev','lib','lib64','proc','tmp','usr')
SANDBOX_ABSENT=('/etc','/var','/run','/root','/run/docker.sock','/var/run/docker.sock','/etc/sudoers','/etc/shadow')
NAMESPACES=('user','mnt','net','pid','ipc','uts')
CAPABILITY_SETS=('CapInh','CapPrm','CapEff','CapBnd','CapAmb')
ZERO_CAPS='0000000000000000'
PLACEMENT_PATTERN=r'(/[A-Za-z0-9][A-Za-z0-9._-]{0,127}){2,16}'
ATTESTATION_SCHEMA='dg16.pro-sender-whole-sandbox-attestation.v1'
_SANDBOX=None

def whole_sender_argv(root,packet,entry,args,masked=()):
    masks=[a for d in masked for a in ('--tmpfs',d,'--remount-ro',d)]
    return [SANDBOX,'--unshare-all','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL',
      '--ro-bind','/usr','/usr',*masks,'--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',
      '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--bind',root,root,'--ro-bind',packet,packet,'--remount-ro','/',
      '--setenv','PATH','/usr/bin:/bin','--setenv','LC_ALL','C','--chdir','/',
      '/usr/bin/python3.12','-I','-S','-B',entry,*args]

def group_masks(gid):
    """Outer: directories under /usr that a SUPPLEMENTARY group of the sender may read beyond 'other'.

    An unprivileged user namespace cannot drop supplementary groups (setgroups is denied), so they still apply
    to the read-only /usr view. Each such directory is masked by an empty read-only tmpfs; such a regular file
    refuses the launch. Inside, unmapped groups show as the overflow gid, so only the outer can compute this.
    """
    groups=set(os.getgroups())-{gid};masks=[]
    if not groups:return masks
    def extra(st):return st.st_gid in groups and (st.st_mode>>3)&7&~st.st_mode&7
    for top,dirs,names in os.walk('/usr',followlinks=False):
        keep=[]
        for name in sorted(dirs):
            path=os.path.join(top,name)
            if extra(os.lstat(path)):masks.append(path)
            else:keep.append(name)
        dirs[:]=keep
        for name in names:
            P.need(not extra(os.lstat(os.path.join(top,name))),'SENDER_GROUP_ACCESSIBLE_FILE')
    P.need(all(re.fullmatch(PLACEMENT_PATTERN,m) for m in masks) and len(masks)<=64,'SENDER_GROUP_ACCESSIBLE_PATH')
    return sorted(masks)

def _proc(path,maximum=1024*1024):
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        chunks=[];count=0
        while True:
            raw=os.read(fd,65536)
            if not raw:break
            count+=len(raw);P.need(count<=maximum,'SENDER_SANDBOX_PROC_BOUND');chunks.append(raw)
    finally:os.close(fd)
    return b''.join(chunks).decode('ascii')

def status_rows():
    rows={}
    for line in _proc('/proc/self/status').splitlines():
        key,_,value=line.partition(':');rows[key]=value.strip()
    return rows

def namespaces():return {n:os.readlink('/proc/self/ns/'+n) for n in NAMESPACES}

def mounts():
    rows=[]
    for line in _proc('/proc/self/mountinfo').splitlines():
        f=line.split(' ');sep=f.index('-');rows.append([f[4],f[5].split(','),f[sep+1]])
    return rows

def overflow_ids():
    return [int(_proc('/proc/sys/kernel/overflowuid')),int(_proc('/proc/sys/kernel/overflowgid'))]

def host_tool_custody(path,observed):
    """Outer, host view: root-owned unprivileged regular file in a root-owned non-writable /, /usr, /usr/bin.

    carrier_io.read_file already refused symlinks, any extended attribute (file capabilities), extra links
    and identity change during the read.
    """
    info=path.lstat()
    P.need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_gid==0 and not info.st_mode&0o6022
      and F.stamp(info)==observed['identity'],'CARRIER_ACTUAL_TOOL_PIN')
    P.need([row[0] for row in observed['ancestors']]==['/','/usr','/usr/bin']
      and all(row[4]==0 and row[5]==0 and not row[3]&0o022 for row in observed['ancestors']),'CARRIER_ACTUAL_TOOL_PIN')
    return True

def _tool_view(att,root_row,path,observed):
    """Inside view of an attested tool: same file and chain, owner unmapped (host uid/gid 0 is not mapped)."""
    path=Path(path);host=att['tools'].get(path.name);ovf=att['overflow']
    info=path.lstat();anc=observed['ancestors']
    return (path==Path('/usr/bin')/path.name and type(host) is dict and len(host['ancestors'])==3
      and stat.S_ISREG(info.st_mode) and not info.st_mode&0o6022 and F.stamp(info)==observed['identity']
      and observed['identity']==host['identity'][:7]+ovf and [r[0] for r in anc]==['/','/usr','/usr/bin']
      and anc[0]==root_row and all(a==h[:4]+ovf for a,h in zip(anc[1:],host['ancestors'][1:])))

def sandbox_facts(attestation_raw):
    """Observe the in-sandbox view (no private read). Returns (facts, failure codes in check order)."""
    failures=[]
    def check(ok,code):
        if not ok and code not in failures:failures.append(code)
    try:
        att=P.parse(attestation_raw.encode('ascii')+b'\n',65536)
        P.exact(att,('schema','uid','gid','overflow','namespaces','usr_submounts','masked','root','packet','entry','tools'))
        P.need(att['schema']==ATTESTATION_SCHEMA and att['entry']==ENTRY and type(att['uid']) is int and type(att['gid']) is int
          and set(att['tools'])=={'openssl','bwrap'} and set(att['namespaces'])==set(NAMESPACES)
          and type(att['usr_submounts']) is list and type(att['masked']) is list
          and all(type(m) is str and m.startswith('/usr/') for m in att['masked'])
          and re.fullmatch(PLACEMENT_PATTERN,att['packet'])
          and str(Path(att['packet']).parent)==att['root'],'SENDER_SANDBOX_ATTESTATION')
    except (ValueError,UnicodeError,AttributeError,KeyError,TypeError):
        return dict(attestation=None),['SENDER_SANDBOX_ATTESTATION']
    uid,gid,root,packet=att['uid'],att['gid'],att['root'],att['packet']
    s=status_rows()
    facts=dict(status={k:s.get(k) for k in ('NoNewPrivs','Seccomp',*CAPABILITY_SETS,'Uid','Gid','Groups')})
    check(s.get('NoNewPrivs')=='1','SENDER_SANDBOX_NO_NEW_PRIVS')
    check(all(s.get(k)==ZERO_CAPS for k in CAPABILITY_SETS),'SENDER_SANDBOX_CAPABILITIES')
    check(s.get('Uid','').split()==[str(uid)]*4 and s.get('Gid','').split()==[str(gid)]*4 and uid>0
      and os.getuid()==os.geteuid()==uid and os.getgid()==os.getegid()==gid,'SENDER_SANDBOX_IDENTITY')
    maps=dict(uid_map=_proc('/proc/self/uid_map').split(),gid_map=_proc('/proc/self/gid_map').split(),
      setgroups=_proc('/proc/self/setgroups').strip());facts.update(maps)
    check(len(maps['uid_map'])==3 and maps['uid_map'][0]==str(uid) and maps['uid_map'][2]=='1'
      and len(maps['gid_map'])==3 and maps['gid_map'][0]==str(gid) and maps['gid_map'][2]=='1'
      and maps['setgroups']=='deny','SENDER_SANDBOX_USER_NAMESPACE')
    ns=namespaces();facts['namespaces']=ns;facts['outer_namespaces']=att['namespaces']
    check(all(ns[n]!=att['namespaces'][n] for n in NAMESPACES),'SENDER_SANDBOX_NAMESPACES')
    interfaces=[line.split(':')[0].strip() for line in _proc('/proc/net/dev').splitlines()[2:]]
    facts['interfaces']=interfaces;check(interfaces==['lo'],'SENDER_SANDBOX_NETWORK')
    rows=mounts();facts['mounts']=rows
    expected={'/':'ro','/usr':'ro','/proc':'rw','/dev':'rw','/tmp':'rw',root:'rw',packet:'ro'}
    expected.update({d:'rw' for d in SANDBOX_DEVICES});expected.update({d:'ro' for d in att['usr_submounts']})
    expected.update({d:'ro' for d in att['masked']})
    points=[r[0] for r in rows];facts['masked']=att['masked']
    check(len(points)==len(set(points)) and set(points)==set(expected)
      and all(r[1][0]==expected.get(r[0]) and 'nosuid' in r[1] for r in rows)
      and [r[2] for r in rows if r[0]=='/']==['tmpfs']
      and all(r[2]=='tmpfs' for r in rows if r[0] in att['masked']),'SENDER_SANDBOX_FILESYSTEM_VIEW')
    try:check(all(os.listdir(m)==[] for m in att['masked']),'SENDER_SANDBOX_FILESYSTEM_VIEW')
    except OSError:check(False,'SENDER_SANDBOX_FILESYSTEM_VIEW')
    try:
        parts=Path(root).parts;top=sorted(os.listdir('/'));facts['top']=top
        facts['placement_chain']=[[str(Path(*parts[:i])),sorted(os.listdir(Path(*parts[:i])))] for i in range(2,len(parts))]
        check(parts[1] not in SANDBOX_TOP and top==sorted(SANDBOX_TOP+(parts[1],))
          and all(listing==[parts[i]] for i,(_,listing) in enumerate(facts['placement_chain'],2))
          and os.listdir(root)==[Path(packet).name],'SENDER_SANDBOX_FILESYSTEM_VIEW')
    except OSError:check(False,'SENDER_SANDBOX_FILESYSTEM_VIEW')
    facts['absent']={p:not os.path.lexists(p) for p in SANDBOX_ABSENT}
    check(all(facts['absent'].values()),'SENDER_SANDBOX_UNREACHABLE')
    facts['environment']=sorted(os.environ);check(dict(os.environ)==SENDER_ENV,'SENDER_SANDBOX_ENVIRONMENT')
    facts['descriptors']=[row[0] for row in descriptor_snapshot()]
    check(facts['descriptors']==[0,1,2],'SENDER_SANDBOX_DESCRIPTORS')
    try:
        raw,_=F.read_file(Path(packet)/'carrier'/SENDER_ENTRY,1024*1024)
        check(P.descriptor(raw)==ENTRY,'SENDER_SANDBOX_ENTRY')
    except (OSError,ValueError):check(False,'SENDER_SANDBOX_ENTRY')
    try:
        check(att['overflow']==overflow_ids(),'SENDER_SANDBOX_TOOL_VIEW')
        root_row=['/',*F.directory_id(Path('/').lstat())];facts['root_row']=root_row
        for name in sorted(att['tools']):
            _,row=F.read_file(Path('/usr/bin')/name,32*1024**2)
            check(_tool_view(att,root_row,Path('/usr/bin')/name,row),'SENDER_SANDBOX_TOOL_VIEW')
    except (OSError,ValueError,TypeError):check(False,'SENDER_SANDBOX_TOOL_VIEW')
    facts['max_user_namespaces']=_proc('/proc/sys/user/max_user_namespaces').strip()
    facts['pids']=sorted(int(p) for p in os.listdir('/proc') if p.isdigit())
    return facts,failures

def enter_sender_sandbox(attestation_raw):
    """Inner, first act after loading: refuse unless the whole-sender sandbox is exactly in force."""
    global _SANDBOX
    P.need(_SANDBOX is None,'SENDER_SANDBOX_ALREADY_ENTERED')
    facts,failures=sandbox_facts(attestation_raw)
    if failures:raise ValueError(failures[0])
    _SANDBOX=dict(attestation=P.parse(attestation_raw.encode('ascii')+b'\n',65536),facts=facts,
      mounts=facts['mounts'],namespaces=facts['namespaces'],root_row=facts['root_row'])
    return facts

def require_sender_sandbox():
    """Live recheck at every sender effect point; refuses outside the verified whole-sender sandbox."""
    P.need(_SANDBOX is not None,'SENDER_WHOLE_SANDBOX_REQUIRED')
    s=status_rows();att=_SANDBOX['attestation']
    P.need(s.get('NoNewPrivs')=='1' and all(s.get(k)==ZERO_CAPS for k in CAPABILITY_SETS)
      and os.getuid()==os.geteuid()==att['uid'] and os.getgid()==os.getegid()==att['gid']
      and namespaces()==_SANDBOX['namespaces'] and mounts()==_SANDBOX['mounts'],'SENDER_WHOLE_SANDBOX_CHANGED')
    return _SANDBOX

def attested_tool_custody(path,observed):
    s=require_sender_sandbox()
    P.need(_tool_view(s['attestation'],s['root_row'],path,observed),'CARRIER_ACTUAL_TOOL_PIN')
    return True

def read_request_archive():
    """Inner: the public request artifact the outer passed as the read-only stdin regular file."""
    require_sender_sandbox()
    info=os.fstat(0)
    P.need(stat.S_ISREG(info.st_mode) and 0<info.st_size<=P.MAX_ARTIFACT
      and fcntl.fcntl(0,fcntl.F_GETFL)&os.O_ACCMODE==os.O_RDONLY,'SENDER_REQUEST_ARTIFACT_SHAPE')
    raw=os.pread(0,P.MAX_ARTIFACT+1,0)
    P.need(len(raw)==info.st_size and F.stamp(os.fstat(0))==F.stamp(info),'SENDER_REQUEST_ARTIFACT_SHAPE')
    null=os.open('/dev/null',os.O_RDONLY|os.O_NOFOLLOW)
    try:os.dup2(null,0)
    finally:os.close(null)
    return raw

def launch(run_id,workflow_commit,artifact_id,archive_path):
    """Outer entry (sender_launch.py), as the original sender UID before any private read."""
    carrier=Path(__file__).absolute().parent;entry=carrier/SENDER_ENTRY
    raw,_=F.read_file(entry,1024*1024);P.need(P.descriptor(raw)==ENTRY,'SENDER_ENTRY_PIN')
    braw,_=F.read_file(carrier/'CARRIER_COMPOSITION.json',P.MAX_INDEX)
    P.need(P.sha(braw)==P.BINDING_SHA256,'CARRIER_BINDING_PIN')
    P.need(all(type(v) is str for v in (run_id,workflow_commit,artifact_id)) and re.fullmatch('[1-9][0-9]{0,19}',run_id)
      and re.fullmatch('[0-9a-f]{40}',workflow_commit) and re.fullmatch('[1-9][0-9]{0,19}',artifact_id),'SENDER_LAUNCH_ARGUMENTS')
    return _launch(carrier.parent,entry,P.parse(braw,P.MAX_INDEX)['sender_tools'],[run_id,workflow_commit,artifact_id],archive_path)

def _launch(packet,entry,pins,args,archive_path):
    import ctypes
    uid,gid=os.getuid(),os.getgid()
    P.need(uid>0 and gid>0 and uid==os.geteuid() and gid==os.getegid(),'SENDER_LAUNCH_IDENTITY')
    P.need(_SANDBOX is None,'SENDER_LAUNCH_NESTED')
    packet=Path(packet).absolute();root=packet.parent;entry=Path(entry).absolute()
    P.need(re.fullmatch(PLACEMENT_PATTERN,str(packet)) is not None and root.parts[1] not in SANDBOX_TOP
      and packet in entry.parents and len(args)==3,'SENDER_PLACEMENT_PATH')
    info=root.lstat()
    P.need(stat.S_ISDIR(info.st_mode) and not root.is_symlink() and info.st_uid==uid and stat.S_IMODE(info.st_mode)==0o700
      and not os.listxattr(root) and os.listdir(root)==[packet.name],'SENDER_PLACEMENT_CUSTODY')
    pinfo=packet.lstat();P.need(stat.S_ISDIR(pinfo.st_mode) and not packet.is_symlink(),'SENDER_PLACEMENT_CUSTODY')
    P.exact(pins,('openssl','bwrap'))
    rows={}
    for name in ('openssl','bwrap'):
        path=Path('/usr/bin')/name;body,row=F.read_file(path,32*1024**2)
        P.need(P.descriptor(body)==pins[name],'CARRIER_ACTUAL_TOOL_PIN');host_tool_custody(path,row);rows[name]=row
    usr=sorted(r[0] for r in mounts() if r[0].startswith('/usr/'));masked=group_masks(gid)
    archive=exec_fd=None
    try:
        archive=os.open(archive_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
        a=os.fstat(archive)
        P.need(stat.S_ISREG(a.st_mode) and 0<a.st_size<=P.MAX_ARTIFACT,'SENDER_REQUEST_ARTIFACT_SHAPE')
        exec_fd=launcher_fd(rows['bwrap'])
        att=dict(schema=ATTESTATION_SCHEMA,uid=uid,gid=gid,overflow=overflow_ids(),namespaces=namespaces(),
          usr_submounts=usr,masked=masked,root=str(root),packet=str(packet),entry=ENTRY,
          tools={n:dict(identity=r['identity'],ancestors=r['ancestors']) for n,r in rows.items()})
        argv=whole_sender_argv(str(root),str(packet),str(entry),['--inside',P.encode(att).decode('ascii')[:-1],*args],masked)
        libc=ctypes.CDLL(None,use_errno=True)
        libc.prctl.argtypes=[ctypes.c_int,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong]
        libc.prctl.restype=ctypes.c_int
        pid=os.fork()
        if pid==0:
            try:
                os.dup2(archive,0);os.closerange(3,exec_fd);os.closerange(exec_fd+1,FD_LIMIT)
                # PR_SET_NO_NEW_PRIVS, read back with PR_GET_NO_NEW_PRIVS: set before the launcher runs.
                if libc.prctl(38,1,0,0,0)==0 and libc.prctl(39,0,0,0,0)==1:os.execve(exec_fd,argv,{})
            finally:os._exit(126)
    finally:
        for fd in (archive,exec_fd):
            if fd is not None:os.close(fd)
    _,status=os.waitpid(pid,0);rc=os.waitstatus_to_exitcode(status)
    after=os.listdir(root)
    P.need(F.directory_id(root.lstat())==F.directory_id(info) and F.directory_id(packet.lstat())==F.directory_id(pinfo)
      and set(after)<={packet.name,'dg16-private-sender-'+args[0]+'-a1'},'SENDER_PLACEMENT_EFFECTS')
    return rc

class CaptureSession:
    def __init__(self,directory,budget,currentness,launcher):
        P.need(callable(currentness) and callable(launcher),'SENDER_CURRENTNESS_REQUIRED')
        self.directory=Path(directory);self.currentness=currentness;self.launcher=launcher;self.calls=0;self.last=None;self.owner=None
        self.Owner,self.source_opening=load_owner()
        budget.reserve(OWNER_EVIDENCE_MAX,1)  # Before any possible child output.
    def _current(self):
        require_sender_sandbox();source_current(self.source_opening);self.currentness()
    def capture(self,label,argv,records,deadline,seconds=60,fds=()):
        validate_command(label,argv,fds)
        P.need(self.calls==0,'SENDER_CAPTURE_ALREADY_RESERVED');self.calls=1
        P.need(type(seconds) is int and 1<=seconds<=60,'SENDER_COMMAND_BOUND')
        started=time.monotonic();stop=min(started+seconds,deadline)-CLOSE_SECONDS
        P.need(started<stop,'SENDER_CLOSING_RESERVATION_UNAVAILABLE')
        self._current()
        before_fds=descriptor_snapshot();before_mask=signal.pthread_sigmask(signal.SIG_BLOCK,set())
        handler_names=(signal.SIGCHLD,signal.SIGINT,signal.SIGTERM)
        before_handlers={n:signal.getsignal(n) for n in handler_names}
        held={fd:F.stamp(os.fstat(fd)) for fd in fds}
        P.need(all(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink==1
          and os.fstat(fd).st_uid==os.geteuid() and stat.S_IMODE(os.fstat(fd).st_mode)==0o600 for fd in fds),
          'SENDER_HELD_INPUT_CUSTODY')
        owner=None;owned=set();selector=None;buffers=[b'',b''];stream_fds={};pipe_observed=False
        process_started=False;pidfd_acquired=False;timed_out=False;overflow=False;streams_complete=False
        failure=None;exec_bytes=b'';exec_errno=None;natural_quiet=False;close_error=None;fd_close_ok=True
        evidence=None;rc=None;before_close=None;restore={};after_fds=None;exec_fd=None
        def pipe():
            pair=os.pipe2(os.O_CLOEXEC);owned.update(pair);return pair
        def close(fd):
            nonlocal fd_close_ok
            if fd is not None and fd in owned:
                owned.remove(fd)
                try:os.close(fd)
                except OSError:fd_close_ok=False
        try:
            owner=self.Owner();self.owner=owner;owner.require_quiescent()
            gate_r,gate_w=pipe();error_r,error_w=pipe();out_r,out_w=pipe();err_r,err_w=pipe()
            null_fd=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW);owned.add(null_fd)
            null_info=os.fstat(null_fd)
            P.need(stat.S_ISCHR(null_info.st_mode) and os.major(null_info.st_rdev)==1 and os.minor(null_info.st_rdev)==3,
              'SENDER_EMPTY_STDIN_DEVICE')
            exec_fd=launcher_fd(self.launcher());owned.add(exec_fd)
            pipe_observed=True;self._current()
            P.need({fd:F.stamp(os.fstat(fd)) for fd in fds}==held,'SENDER_HELD_INPUT_CHANGED')
            if not time.monotonic()<stop:
                timed_out=True;failure='COMMAND_TIMEOUT_BEFORE_FORK'
                raise CaptureRefusal(failure)
            pid=os.fork()
            if pid==0:
                try:
                    for fd in (gate_w,error_r,out_r,err_r):close(fd)
                    for name in ('SIGINT','SIGTERM','SIGPIPE','SIGXFZ','SIGXFSZ'):
                        if hasattr(signal,name):signal.signal(getattr(signal,name),signal.SIG_DFL)
                    if os.read(gate_r,1)!=b'R':os._exit(125)
                    close(gate_r);os.chdir('/')
                    os.dup2(null_fd,0);os.dup2(out_w,1);os.dup2(err_w,2)
                    for fd in (0,1,2,*fds):os.set_inheritable(fd,True)
                    visible=[]
                    with os.scandir('/proc/self/fd') as entries:
                        for entry in entries:
                            if len(visible)>=FD_LIMIT or not entry.name.isdigit():raise ValueError('SENDER_DESCRIPTOR_POPULATION')
                            visible.append(int(entry.name))
                    for fd in close_plan(visible,fds,error_w,exec_fd):
                        try:os.close(fd)
                        except OSError as exc:
                            if exc.errno!=errno.EBADF:raise
                    os.execve(exec_fd,argv,{})
                except BaseException as exc:
                    number=exc.errno if isinstance(exc,OSError) and exc.errno is not None else errno.EINVAL
                    try:os.write(error_w,(str(number)+'\n').encode('ascii'))
                    finally:os._exit(126)
            process_started=True;owner.status['primary_pid']=pid;owner.status['quiescence']='UNPROVED'
            for fd in (gate_r,error_w,out_w,err_w,null_fd,exec_fd):close(fd)
            owner.primary_fd=os.pidfd_open(pid,0);pidfd_acquired=True
            initial=os.waitid(os.P_PIDFD,owner.primary_fd,os.WEXITED|os.WNOHANG|os.WNOWAIT|owner.WALL)
            P.need(initial is None,'SENDER_PRIMARY_ENDED_BEFORE_RELEASE')
            self._current();P.need({fd:F.stamp(os.fstat(fd)) for fd in fds}==held,'SENDER_HELD_INPUT_CHANGED')
            if not time.monotonic()<stop:
                timed_out=True;failure='COMMAND_TIMEOUT_BEFORE_RELEASE'
                raise CaptureRefusal(failure)
            P.need(os.write(gate_w,b'R')==1,'SENDER_RELEASE_GATE');close(gate_w)
            selector=selectors.DefaultSelector()
            for fd,index in ((out_r,0),(err_r,1),(error_r,2)):
                os.set_blocking(fd,False);selector.register(fd,selectors.EVENT_READ,index);stream_fds[fd]=index
            while selector.get_map() or owner.status['primary_exit'] is None:
                owner.quiescent()
                P.need(not owner.primary_wait_missing,'SENDER_PRIMARY_STATUS_MISSING')
                remaining=stop-time.monotonic()
                if remaining<=0:timed_out=True;break
                if not selector.get_map():
                    time.sleep(min(0.01,remaining));continue
                for key,_ in selector.select(min(0.05,remaining)):
                    try:chunk=os.read(key.fd,4096)
                    except BlockingIOError:continue
                    if not chunk:selector.unregister(key.fd);continue
                    if key.data==2:
                        P.need(len(exec_bytes)+len(chunk)<=64,'SENDER_EXEC_ERROR_BOUND');exec_bytes+=chunk
                    else:
                        buffers[key.data],over=append_stream(buffers[key.data],chunk);overflow=overflow or over
                if overflow:break
            streams_complete=not selector.get_map() and not timed_out and not overflow
            if exec_bytes:
                P.need(re.fullmatch(rb'[0-9]{1,5}\n',exec_bytes),'SENDER_EXEC_ERROR_SHAPE')
                exec_errno=int(exec_bytes);failure='EXEC_REFUSED'
            if timed_out:failure='COMMAND_TIMEOUT'
            if overflow:failure='STREAM_OVERFLOW'
            natural_quiet=owner.quiescent()
            if not natural_quiet:failure=failure or 'LIVE_DESCENDANTS_REFUSED'
            P.need(not owner.primary_wait_missing and type(owner.status['primary_exit']) is int,'SENDER_PRIMARY_STATUS_MISSING')
        except BaseException as exc:
            failure=failure or ('INTERRUPTED' if isinstance(exc,(KeyboardInterrupt,SystemExit)) else 'CAPTURE_REFUSED')
        finally:
            if owner is not None:before_close=copy.deepcopy(owner.status)
            if selector is not None:
                try:selector.close()
                except BaseException:fd_close_ok=False
            for fd in tuple(owned):close(fd)
            if owner is not None:
                try:owner.close()
                except BaseException:close_error='MAINTAINED_OWNED_CLOSE_REFUSED'
                rc=owner.status['primary_exit']
            try:signal.pthread_sigmask(signal.SIG_SETMASK,before_mask)
            except BaseException:failure=failure or 'MASK_RESTORATION_REFUSED'
            try:
                after_fds=descriptor_snapshot()
                restore=dict(echild=kernel_echild(),mask_restored=signal.pthread_sigmask(signal.SIG_BLOCK,set())==before_mask,
                  handlers_restored=all(signal.getsignal(n) is before_handlers[n] or signal.getsignal(n)==before_handlers[n] for n in handler_names),
                  subreaper_restored=owner is not None and owner.status.get('flag_restored') is True and owner._get_flag()==owner.previous_flag,
                  descriptors_restored=after_fds==before_fds,owned_descriptors_closed=fd_close_ok and not owned
                    and (owner is None or owner.primary_fd is None))
            except BaseException:restore=dict(echild=False,restoration_observation_refused=True)
            if not restoration_ok(restore):failure=failure or 'CUSTODY_RESTORATION_REFUSED'
            if close_error:failure=failure or 'CLEANUP_REFUSED'
            if not process_started or not pidfd_acquired or type(rc) is not int or not streams_complete:
                failure=failure or 'CAPTURE_INCOMPLETE'
            data=dict(schema='dg16.pro-sender-actual-capture-owner.v1',authority='NONE',profile=PROFILE,
              qualifier=QUALIFIER,compiler=COMPILER,owner_ast_sha256=OWNER_AST_SHA256,
              source_opening=self.source_opening,process_started=process_started,pidfd_acquired=pidfd_acquired,
              primary_returncode=rc,exec_errno=exec_errno,failure=failure,close_error=close_error,
              before_close=before_close,after_close=copy.deepcopy(owner.status) if owner is not None else None,
              original_mask=sorted(int(n) for n in before_mask),before_descriptors=before_fds,after_descriptors=after_fds,
              restoration=restore,natural_quiescence=natural_quiet,elapsed_ns=int((time.monotonic()-started)*10**9),
              command_deadline=stop,enclosing_deadline=deadline,maintained_close_seconds=CLOSE_SECONDS,
              stdout=P.descriptor(buffers[0]),stderr=P.descriptor(buffers[1]),original_awards=[])
            try:
                evidence=F.write_once(self.directory/'SENDER_CAPTURE_OWNER.json',P.encode(data),OWNER_EVIDENCE_MAX)
                self._current()
            except BaseException:failure=failure or 'OWNER_EVIDENCE_UNRECEIVED'
            row=dict(name=label,process_started=process_started,returncode=rc,timeout=timed_out,
              output_bound_exceeded=overflow,pidfd_acquired=pidfd_acquired,internal_failure=failure,
              streams_complete=streams_complete,stdout_bytes=len(buffers[0]),stderr_bytes=len(buffers[1]),
              stdout_sha256=P.sha(buffers[0]),stderr_sha256=P.sha(buffers[1]),
              cleanup=dict(echild=restore.get('echild') is True,restoration_complete=restoration_ok(restore)),
              sender_profile=PROFILE,owner_evidence=({k:evidence[k] for k in ('bytes','sha256')} if evidence else None))
            records.append(row);self.last=dict(row=row,owner_evidence=evidence,restoration=restore,
              original_mask=before_mask,original_handlers=before_handlers)
        if failure is not None:
            error=CaptureRefusal(failure);error.captured=dict(returncode=rc,
              stdout=buffers[0] if pipe_observed else None,stderr=buffers[1] if pipe_observed else None,
              streams_complete=streams_complete);raise error
        return rc,buffers[0],buffers[1]
    def closed(self):
        try:
            if self.last is None or self.owner is None or not restoration_ok(self.last['restoration']):return False
            raw,row=F.read_file(self.directory/'SENDER_CAPTURE_OWNER.json',OWNER_EVIDENCE_MAX,private=True)
            if row!=self.last['owner_evidence']:return False
            self.owner._scope();self._current()
            return (kernel_echild() and self.owner._get_flag()==self.owner.previous_flag
              and signal.pthread_sigmask(signal.SIG_BLOCK,set())==self.last['original_mask']
              and all(signal.getsignal(n) is old or signal.getsignal(n)==old for n,old in self.last['original_handlers'].items()))
        except BaseException:return False
