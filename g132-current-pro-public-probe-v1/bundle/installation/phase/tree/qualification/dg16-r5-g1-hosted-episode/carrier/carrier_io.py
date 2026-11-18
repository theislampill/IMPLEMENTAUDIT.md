"""Ordinary finite files and same-identity staging; no controller or network."""
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import bundle_codec as C

need=C.need

def stamp(s):
    return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid]

def directory_id(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid]

def parents(path):
    result=[]
    for parent in reversed(Path(path).absolute().parents):
        st=parent.lstat();need(stat.S_ISDIR(st.st_mode) and not parent.is_symlink(),'PHYSICAL_PARENT_ALIAS')
        result.append([str(parent),*directory_id(st)])
    return result

def read_file(path,maximum,private=False):
    path=Path(path).absolute();ancestry=parents(path);before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'PHYSICAL_FILE_SHAPE')
    if private:need(before.st_uid==os.geteuid() and stat.S_IMODE(before.st_mode)==0o600,'PRIVATE_FILE_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'PHYSICAL_OPEN_CHANGED')
        chunks=[];count=0
        while True:
            raw=os.read(fd,min(1024*1024,maximum-count+1))
            if not raw:break
            count+=len(raw);need(count<=maximum,'PHYSICAL_FILE_BOUND');chunks.append(raw)
        raw=b''.join(chunks)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
          and stamp(path.lstat())==stamp(before) and parents(path)==ancestry,'PHYSICAL_CLOSING_CHANGED')
        return raw,dict(bytes=len(raw),sha256=C.sha(raw),identity=stamp(before),ancestors=ancestry)
    finally:os.close(fd)

def directories(index):
    result={'.'}
    for name in index:
        result.update(p.as_posix() for p in PurePosixPath(name).parents)
    return result

def acquire(root,index,private=False):
    C.check_index(index);root=Path(root).absolute();wanted_dirs=directories(index)
    observed_files=set();observed_dirs={};body={};files={}
    for parent,dirs,names in os.walk(root,followlinks=False):
        path=Path(parent);rel=path.relative_to(root).as_posix();st=path.lstat()
        need(rel in wanted_dirs and stat.S_ISDIR(st.st_mode) and not path.is_symlink(),'PHYSICAL_DIRECTORY_POPULATION')
        if private:need(st.st_uid==os.geteuid() and stat.S_IMODE(st.st_mode)==0o700,'PRIVATE_DIRECTORY_CUSTODY')
        need(not os.listxattr(path),'PHYSICAL_DIRECTORY_ATTRIBUTES')
        observed_dirs[rel]=directory_id(st)
        for name in dirs:
            child=path/name;key=child.relative_to(root).as_posix()
            need(key in wanted_dirs and not child.is_symlink(),'PHYSICAL_DIRECTORY_POPULATION')
        for name in names:
            key=(path/name).relative_to(root).as_posix()
            need(key in index and key not in observed_files,'PHYSICAL_FILE_POPULATION')
            raw,row=read_file(path/name,C.MAX_FILE_BYTES,private)
            need({k:row[k] for k in ('bytes','sha256')}==index[key],'PHYSICAL_BODY_PIN')
            body[key]=raw;files[key]=row;observed_files.add(key)
        need(len(observed_files)+len(observed_dirs)<=C.MAX_ENTRIES*6+1,'PHYSICAL_POPULATION_BOUND')
    need(observed_files==set(index) and set(observed_dirs)==wanted_dirs,'PHYSICAL_EXACT_POPULATION')
    closing={name:directory_id((root if name=='.' else root/name).lstat()) for name in wanted_dirs}
    need(closing==observed_dirs,'PHYSICAL_DIRECTORY_CHANGED')
    return body,dict(files=files,directories=observed_dirs,total_bytes=sum(row['bytes'] for row in files.values()))

def recheck(root,index,opening,private=False):
    _,closing=acquire(root,index,private)
    need(closing==opening,'PHYSICAL_CLOSING_CHANGED');return closing

class Budget:
    def __init__(self,byte_limit,entry_limit):
        self.byte_limit=byte_limit;self.entry_limit=entry_limit;self.bytes=0;self.entries=0
    def reserve(self,count,entries=1):
        need(type(count) is int and type(entries) is int and count>=0 and entries>=0,'RESERVATION_SHAPE')
        need(self.bytes+count<=self.byte_limit and self.entries+entries<=self.entry_limit,'CARRIER_ALLOCATION_BOUND')
        self.bytes+=count;self.entries+=entries

def private_directory(path):
    path=Path(path);path.mkdir(mode=0o700,exist_ok=False)
    st=path.lstat();need(stat.S_IMODE(st.st_mode)==0o700 and st.st_uid==os.geteuid(),'PRIVATE_DIRECTORY_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:need(directory_id(os.fstat(fd))==directory_id(st) and not os.listxattr(fd),'PRIVATE_DIRECTORY_OPEN_CHANGED')
    except BaseException:os.close(fd);raise
    return fd,directory_id(st)

def write_once(path,raw,maximum=1024*1024):
    need(type(raw) is bytes and len(raw)<=maximum,'PRIVATE_WRITE_BOUND')
    path=Path(path);ancestry=parents(path)
    fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        os.fchmod(fd,0o600);offset=0
        while offset<len(raw):
            written=os.write(fd,raw[offset:]);need(written>0,'PRIVATE_SHORT_WRITE');offset+=written
        os.fsync(fd)
        need(parents(path)==ancestry,'PRIVATE_WRITE_PARENT_CHANGED')
    finally:os.close(fd)
    body,row=read_file(path,maximum,private=True);need(body==raw,'PRIVATE_WRITE_READBACK');return row

def reserve(directory,name,raw):
    need(name in ('RECIPIENT_RESERVED.json','SEND_RESERVED.json','CONSUME_RESERVED.json'),'RESERVATION_NAME')
    row=write_once(Path(directory)/name,raw,65536)
    fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
    return row

class OutputFile:
    """Retained FD for an owned command output; /proc paths never select data."""
    def __init__(self,parent,name,maximum,budget):
        need(name in ('recipient.key','recipient.pem','bundle.plain','quarantine.plain','INPUTS.cms'),'COMMAND_FILE_NAME')
        budget.reserve(maximum)
        self.parent=Path(parent);self.name=name;self.maximum=maximum
        self.parent_fd=os.open(self.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.parent_id=directory_id(os.fstat(self.parent_fd))
        try:
            need(os.fstat(self.parent_fd).st_uid==os.geteuid() and stat.S_IMODE(os.fstat(self.parent_fd).st_mode)==0o700,'PRIVATE_DIRECTORY_CUSTODY')
            self.fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.parent_fd)
        except BaseException:
            os.close(self.parent_fd);raise
        self.identity=directory_id(os.fstat(self.fd));self.closed=False
        try:os.fchmod(self.fd,0o600);self.identity=directory_id(os.fstat(self.fd))
        except BaseException:
            self.cleanup();raise
    @property
    def proc_path(self):return '/proc/self/fd/'+str(self.fd)
    def current(self):
        info=os.fstat(self.fd)
        need(directory_id(info)==self.identity and info.st_nlink==1 and info.st_size<=self.maximum
             and not os.listxattr(self.fd),'COMMAND_OUTPUT_CUSTODY')
        need(directory_id(os.stat(self.name,dir_fd=self.parent_fd,follow_symlinks=False))==self.identity
             and directory_id(self.parent.lstat())==self.parent_id,'COMMAND_OUTPUT_PATH_CHANGED')
        return info
    def write(self,raw):
        need(type(raw) is bytes and len(raw)<=self.maximum and self.current().st_size==0,'COMMAND_INPUT_WRITE')
        count=0
        while count<len(raw):
            got=os.write(self.fd,raw[count:]);need(got>0,'COMMAND_INPUT_WRITE');count+=got
        os.fsync(self.fd);need(self.read()==raw,'COMMAND_INPUT_READBACK')
    def read(self):
        before=stamp(self.current());raw=os.pread(self.fd,self.maximum+1,0)
        need(len(raw)<=self.maximum and len(raw)==before[4] and stamp(self.current())==before,'COMMAND_OUTPUT_CHANGED')
        return raw
    def cleanup(self):
        outcome=dict(name=self.name,unlinked=False,descriptor_closed=False,identity_confirmed=False)
        try:
            current=os.stat(self.name,dir_fd=self.parent_fd,follow_symlinks=False)
            need(directory_id(current)==self.identity and current.st_nlink==1,'CLEANUP_FOREIGN_MEMBER_REFUSED')
            outcome['identity_confirmed']=True
            os.unlink(self.name,dir_fd=self.parent_fd);os.fsync(self.parent_fd);outcome['unlinked']=True
        except (OSError,ValueError):outcome['refusal']='OWNED_CLEANUP_UNCONFIRMED'
        finally:
            if not self.closed:
                os.close(self.fd);os.close(self.parent_fd);self.closed=True
            outcome['descriptor_closed']=True
        return outcome

    def retain_close(self):
        self.current();os.fsync(self.fd)
        os.close(self.fd);os.close(self.parent_fd);self.closed=True

class HeldFile(OutputFile):
    """Reacquire only a named held recipient with its full original identity."""
    def __init__(self,parent,name,expected,maximum):
        need(name in ('recipient.key','recipient.pem'),'HELD_RECIPIENT_NAME')
        self.parent=Path(parent);self.name=name;self.maximum=maximum;self.closed=False
        _,row=read_file(self.parent/name,maximum,private=True)
        need(row==expected,'HELD_RECIPIENT_CHANGED')
        self.parent_fd=os.open(self.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.parent_id=directory_id(os.fstat(self.parent_fd))
        try:self.fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.parent_fd)
        except BaseException:os.close(self.parent_fd);raise
        self.identity=directory_id(os.fstat(self.fd))
        try:
            need(stamp(os.fstat(self.fd))==expected['identity'],'HELD_RECIPIENT_CHANGED')
            need(C.sha(self.read())==expected['sha256'],'HELD_RECIPIENT_CHANGED')
        except BaseException:
            os.close(self.fd);os.close(self.parent_fd);self.closed=True;raise

def private_usage(directory,maximum):
    """Flat carrier session only. Unknown subdirectories are never ignored."""
    directory=Path(directory);info=directory.lstat()
    need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode)==0o700
      and info.st_uid==os.geteuid() and not directory.is_symlink(),'PRIVATE_DIRECTORY_CUSTODY')
    total=0;count=1
    for child in directory.iterdir():
        _,row=read_file(child,maximum,private=True);total+=row['bytes'];count+=1
        need(total<=80*1024**2 and count<=1600,'CARRIER_ALLOCATION_BOUND')
    return total,count

def rename_noreplace(parent,staging,target):
    """Future Linux ordinary-file primitive, never called by author controls."""
    import ctypes
    libc=ctypes.CDLL(None,use_errno=True)
    call=libc.renameat2
    call.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    call.restype=ctypes.c_int
    fd=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        need('/' not in staging and target=='private-inputs','ATOMIC_TARGET_SCOPE')
        rc=call(fd,os.fsencode(staging),fd,os.fsencode(target),1) # RENAME_NOREPLACE
        if rc:raise ValueError('ATOMIC_NOREPLACE_REFUSED')
        os.fsync(fd)
    finally:os.close(fd)

def discard_stage(root,index,opening):
    """Delete only the exact acquired owned tree; foreign replacement refuses."""
    root=Path(root);outcomes=[]
    try:
        recheck(root,index,opening,private=True)
        for name,row in sorted(opening['files'].items(),reverse=True):
            path=root/name;parent_fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            fd=None
            try:
                fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent_fd)
                need(stamp(os.fstat(fd))==row['identity'] and stamp(os.stat(path.name,dir_fd=parent_fd,follow_symlinks=False))==row['identity'],
                     'STAGE_CLEANUP_FOREIGN_MEMBER')
                os.unlink(path.name,dir_fd=parent_fd);os.fsync(parent_fd)
                outcomes.append(dict(name=name,unlinked=True))
            finally:
                if fd is not None:os.close(fd)
                os.close(parent_fd)
        for name in sorted(opening['directories'],key=lambda n:(len(PurePosixPath(n).parts),n),reverse=True):
            path=root if name=='.' else root/name
            need(directory_id(path.lstat())==opening['directories'][name] and not list(path.iterdir()),'STAGE_CLEANUP_DIRECTORY_CHANGED')
            path.rmdir();outcomes.append(dict(name=name,directory_removed=True))
        return dict(complete=True,outcomes=outcomes,retained_private_stage=False)
    except (OSError,ValueError):
        return dict(complete=False,outcomes=outcomes,retained_private_stage=True,refusal='STAGE_CLEANUP_UNCONFIRMED')

def stage(packet,index,bodies,nonce):
    C.check_index(index);C.check_request(nonce)
    need(type(bodies) is dict and set(bodies)==set(index),'STAGE_POPULATION')
    packet=Path(packet);target=packet/'private-inputs';staging=packet/('.private-inputs-'+nonce)
    need(not target.exists() and not target.is_symlink() and not staging.exists(),'STAGE_ALREADY_EXISTS')
    info=packet.lstat()
    need(stat.S_ISDIR(info.st_mode) and not packet.is_symlink() and info.st_uid==os.geteuid()
      and stat.S_IMODE(info.st_mode)==0o700 and not os.listxattr(packet),'PRIVATE_DIRECTORY_CUSTODY')
    packet_before=directory_id(info);ancestry=parents(packet/'marker')
    budget=Budget(C.MAX_TOTAL_BYTES,C.MAX_ENTRIES*6+1)
    needed=directories(index);budget.reserve(0,len(needed))
    for name,row in index.items():
        need(type(bodies[name]) is bytes and dict(bytes=len(bodies[name]),sha256=C.sha(bodies[name]))==row,'STAGE_BODY_PIN')
        budget.reserve(len(bodies[name]))
    staging.mkdir(mode=0o700,exist_ok=False);opening=None;published=False
    try:
        for name in sorted(needed-{'.'},key=lambda n:(len(PurePosixPath(n).parts),n)):(staging/name).mkdir(mode=0o700)
        for name,raw in sorted(bodies.items()):write_once(staging/name,raw,C.MAX_FILE_BYTES)
        _,opening=acquire(staging,index,private=True)
        for name in needed:
            fd=os.open(staging if name=='.' else staging/name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:os.fsync(fd)
            finally:os.close(fd)
        need(directory_id(packet.lstat())==packet_before and parents(packet/'marker')==ancestry,'STAGE_PARENT_CHANGED')
        rename_noreplace(packet,staging.name,target.name);published=True
        _,closing=acquire(target,index,private=True)
        # Rename changes absolute ancestry/root ctime, not member inode/body.
        need(closing['directories']==opening['directories'],'STAGE_DIRECTORY_IDENTITY_CHANGED')
        for name,row in opening['files'].items():
            need({k:row[k] for k in ('bytes','sha256','identity')}==
                 {k:closing['files'][name][k] for k in ('bytes','sha256','identity')},'STAGE_MEMBER_CHANGED')
        need(directory_id(packet.lstat())==packet_before,'STAGE_PARENT_CHANGED')
        return closing
    except BaseException as cause:
        # A partial write or uncertain rename is quarantined when its entire
        # actual owned population cannot be received. Never sweep by pathname.
        cleanup=(discard_stage(staging,index,opening) if opening is not None and not published and staging.exists() else
                 dict(complete=False,outcomes=[],retained_private_stage=True,refusal='PARTIAL_OR_PUBLICATION_CUSTODY_UNRECEIVED'))
        error=ValueError('PRIVATE_STAGE_REFUSED');error.stage_cleanup=cleanup
        raise error from cause
