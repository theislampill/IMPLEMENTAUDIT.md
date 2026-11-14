"""Finite owned held-file IO; no process, provider, crypto or source repair."""
import hashlib
import os
from pathlib import Path
import stat
import fs_protocol as P

OUTPUT_NAMES={'FRAME.bin','FAILED_STREAMS.cms','FAILURE_ENVELOPE.json','QUARANTINE.bin','stdout.bin','stderr.bin',
 'recipient.pem','recipient.key','wrong.pem','wrong.key','COMMAND.json','COMMAND.stdout','COMMAND.stderr','STATE.json',
 'INTENT.json','RETENTION.json','ACQUISITION.json','RECEIVING.json','CAPTURE_OWNER.json','ARTIFACT.zip'}
def identity(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
def stamp(s):return (*identity(s),s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def name_ok(name):return type(name) is str and name not in ('','.','..') and '/' not in name and '\\' not in name and '\x00' not in name and len(name)<=128

class Directory:
    def __init__(self,path,private=True):
        self.path=Path(path).absolute();P.need(self.path.parts[0]=='/' and '..' not in self.path.parts,'DIRECTORY_PATH')
        self.chain=[];self.fd=None
        try:
            parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            self.chain.append((parent,None,None,identity(os.fstat(parent))))
            for part in self.path.parts[1:]:
                before=os.stat(part,dir_fd=parent,follow_symlinks=False)
                P.need(stat.S_ISDIR(before.st_mode),'DIRECTORY_ALIAS')
                fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
                self.chain.append((fd,parent,part,identity(before)));P.need(identity(os.fstat(fd))==identity(before),'DIRECTORY_OPEN_CHANGED')
                parent=fd
            self.fd=parent;info=os.fstat(parent)
            if private:P.need(info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,'PRIVATE_DIRECTORY_CUSTODY')
            self.current()
        except BaseException:self.close();raise
    def current(self):
        for fd,parent,name,expected in self.chain:
            P.need(identity(os.fstat(fd))==expected,'DIRECTORY_HELD_CHANGED')
            if parent is not None:P.need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==expected,'DIRECTORY_NAME_CHANGED')
        return os.fstat(self.fd)
    def close(self):
        for fd,_,_,_ in reversed(self.chain):os.close(fd)
        self.chain=[];self.fd=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

def create_directory(path):
    path=Path(path).absolute()
    with Directory(path.parent,private=False) as parent:
        P.need(name_ok(path.name),'DIRECTORY_NAME');os.mkdir(path.name,0o700,dir_fd=parent.fd)
        parent.current();os.fsync(parent.fd)
    return Directory(path)

class Input:
    def __init__(self,directory,name,maximum,expected=None,private=False):
        self.directory=directory;self.name=name;self.maximum=maximum;self.fd=None;self.position=0;self.expected=expected
        P.need(name_ok(name) and P.integer(maximum,0,P.TOTAL_MAX),'INPUT_NAME_BOUND');directory.current()
        before=os.stat(name,dir_fd=directory.fd,follow_symlinks=False)
        P.need(stat.S_ISREG(before.st_mode) and before.st_uid==os.geteuid() and before.st_nlink==1
          and 0<=before.st_size<=maximum,'INPUT_CUSTODY')
        if private:P.need(stat.S_IMODE(before.st_mode) in (0o600,0o400),'PRIVATE_INPUT_MODE')
        try:
            self.fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=directory.fd)
            self.opening=stamp(before);P.need(stamp(os.fstat(self.fd))==self.opening and not os.listxattr(self.fd),'INPUT_OPEN_CHANGED')
            self.verify()
        except BaseException:self.close();raise
    def verify(self):
        self.directory.current();P.need(stamp(os.fstat(self.fd))==self.opening
          and stamp(os.stat(self.name,dir_fd=self.directory.fd,follow_symlinks=False))==self.opening,'INPUT_CHANGED')
    def read(self,count):
        P.need(P.integer(count,1,P.CHUNK),'READ_CHUNK_BOUND');self.verify()
        raw=os.pread(self.fd,count,self.position);self.position+=len(raw);self.verify();return raw
    def rewind(self):self.verify();self.position=0
    def descriptor(self,check):
        self.verify();h=hashlib.sha256();offset=0
        while offset<self.opening[6]:
            check();raw=os.pread(self.fd,min(P.CHUNK,self.opening[6]-offset),offset);check()
            P.need(raw,'HASH_SHORT_READ');h.update(raw);offset+=len(raw)
        check();self.verify();row=dict(bytes=offset,sha256=h.hexdigest())
        if self.expected is not None:P.need(row==self.expected,'HELD_INPUT_DESCRIPTOR')
        return row
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

class Output:
    def __init__(self,directory,name,maximum):
        P.need(name in OUTPUT_NAMES and P.integer(maximum,0,P.TOTAL_MAX),'OUTPUT_NAME_BOUND')
        self.directory=directory;self.name=name;self.maximum=maximum;self.fd=None;self.position=0;directory.current()
        self.fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory.fd)
        try:
            os.fchmod(self.fd,0o600);self.opening=identity(os.fstat(self.fd));self.current();os.fsync(directory.fd)
        except BaseException:self.close();raise
    def current(self):
        self.directory.current();info=os.fstat(self.fd)
        P.need(identity(info)==self.opening and info.st_uid==os.geteuid() and info.st_nlink==1
          and stat.S_IMODE(info.st_mode)==0o600 and 0<=info.st_size<=self.maximum and not os.listxattr(self.fd)
          and identity(os.stat(self.name,dir_fd=self.directory.fd,follow_symlinks=False))==self.opening,'OUTPUT_CUSTODY')
        return info
    def verify(self):return self.current()
    def write(self,raw):
        P.need(type(raw) is bytes and len(raw)<=P.CHUNK,'WRITE_CHUNK_BOUND');self.current()
        P.need(self.position+len(raw)<=self.maximum,'OUTPUT_SIZE_BOUND');offset=0
        while offset<len(raw):
            n=os.pwrite(self.fd,raw[offset:],self.position+offset);P.need(n>0,'OUTPUT_SHORT_WRITE');offset+=n
        self.position+=offset;self.current();return offset
    def read(self,count):
        P.need(P.integer(count,1,P.CHUNK),'READ_CHUNK_BOUND');self.current()
        raw=os.pread(self.fd,count,self.position);self.position+=len(raw);self.current();return raw
    def rewind(self):self.current();self.position=0
    def descriptor(self,check):
        os.fsync(self.fd);before=stamp(self.current());h=hashlib.sha256();offset=0
        while offset<before[6]:
            check();raw=os.pread(self.fd,min(P.CHUNK,before[6]-offset),offset);check()
            P.need(raw,'HASH_SHORT_READ');h.update(raw);offset+=len(raw)
        check();P.need(stamp(self.current())==before,'OUTPUT_HASH_CHANGED')
        return dict(bytes=offset,sha256=h.hexdigest())
    def unlink_owned(self):
        self.current();os.unlink(self.name,dir_fd=self.directory.fd);os.fsync(self.directory.fd);self.close()
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()

def usage(root,check):
    total=0;count=0
    with Directory(root) as base:
        def walk(fd,depth):
            nonlocal total,count
            check();P.need(depth<=64,'USAGE_DEPTH');before=stamp(os.fstat(fd));count+=1
            with os.scandir(fd) as entries:
                for entry in entries:
                    check();P.need(count<P.ENTRY_MAX,'USAGE_ENTRIES');info=entry.stat(follow_symlinks=False)
                    P.need(info.st_uid==os.geteuid(),'USAGE_OWNER')
                    if stat.S_ISDIR(info.st_mode):
                        child=os.open(entry.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
                        try:P.need(stamp(os.fstat(child))==stamp(info),'USAGE_DIRECTORY_CHANGED');walk(child,depth+1)
                        finally:os.close(child)
                    else:
                        P.need(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'USAGE_ALIAS');count+=1;total+=info.st_size
                        P.need(total<=P.TOTAL_MAX,'USAGE_BYTES')
            check();P.need(stamp(os.fstat(fd))==before,'USAGE_NAMESPACE_CHANGED')
        walk(base.fd,0);base.current()
    return dict(bytes=total,entries=count)
