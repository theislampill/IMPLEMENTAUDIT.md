# Whole-sender restriction (G132 v3). The entire sender process -- from before its first private read
# through cleanup, including its tool-broker GitHub reads -- runs as the original nonroot UID inside the pinned
# sender bwrap: no_new_privs, every capability (bounding set included) dropped, new user/mount/pid/net/ipc/uts
# namespaces, a cleared environment, and a read-only root holding only /usr, /proc, /dev, a private /tmp and the
# exact placement (packet read-only; its parent, the one writable directory). /usr trees that a retained
# supplementary group could read beyond 'other' are masked (group_masks). The sender needs no network:
# GitHub is read only by the external root dispatcher, through tool_broker files in the session directory.
SENDER_ENTRY='sender_launch.py'
ENTRY=dict(bytes=@ENTRY_BYTES@,sha256='@ENTRY_SHA256@')
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

