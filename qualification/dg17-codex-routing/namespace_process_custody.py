#!/usr/bin/env python3
"""Bound an observed /proc process to a signalable held pidfd.

The /proc mount may expose an ancestor PID namespace. NSpid is interpreted at
this caller's exact observed namespace depth; the opened pidfd's complete
kernel NSpid/Pid fields must match the candidate and its stable proc identity.
No PID arithmetic, guessed offset or bare outer-PID signal is used.
Ownership is a separate caller predicate: this module does not authenticate a
host or grant authority over arbitrary same-UID processes.
"""
from __future__ import annotations
import os, signal
from pathlib import Path

class CustodyError(RuntimeError): pass

def fields(raw):
    if len(raw)>65536: raise CustodyError('kernel record exceeds bound')
    result={}
    for line in raw.decode('ascii').splitlines():
        if ':' not in line: continue
        key,value=line.split(':',1)
        if key in result: raise CustodyError('duplicate kernel field')
        result[key]=value.split()
    return result

def parse(status,stat_text):
    f=fields(status)
    try:
        pid=int(f['Pid'][0]); tgid=int(f['Tgid'][0]); parent=int(f['PPid'][0])
        chain=[int(x) for x in f['NSpid']]; groups=[int(x) for x in f['NStgid']]
        sessions=[int(x) for x in f['NSsid']]; process_groups=[int(x) for x in f['NSpgid']]
        stat_pid=int(stat_text.split(' ',1)[0]); tail=stat_text.rsplit(') ',1)[1].split()
        started=int(tail[19]); stat_parent=int(tail[1]); stat_session=int(tail[3]); stat_group=int(tail[2])
    except (KeyError,ValueError,IndexError) as exc: raise CustodyError('incomplete kernel PID identity') from exc
    if (any(len(f[k])!=1 for k in ('Pid','Tgid','PPid')) or not chain or
        len(sessions)!=len(chain) or len(process_groups)!=len(chain) or chain!=groups or
        any(x<=0 for x in chain+sessions+process_groups) or pid!=tgid or pid!=stat_pid or
        pid!=chain[0] or parent!=stat_parent or started<=0 or stat_session!=sessions[0] or stat_group!=process_groups[0]):
        raise CustodyError('kernel PID chain/stat identity differs')
    return {'visible_pid':pid,'parent_visible_pid':parent,'namespace_pids':chain,
            'namespace_sessions':sessions,'namespace_groups':process_groups,'start_ticks':started}

def observe(path):
    path=Path(path);fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC);nsfd=None
    try:
        root=os.fstat(fd)
        def read(name):
            member=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            try:
                value=os.read(member,65537)
                if len(value)>65536 or os.read(member,1):raise CustodyError('proc member exceeds bound')
                return value
            finally:os.close(member)
        first=parse(read('status'),read('stat').decode('ascii'))
        nsfd=os.open('ns/pid',os.O_RDONLY|os.O_CLOEXEC,dir_fd=fd);ns=os.fstat(nsfd)
        executable=os.readlink('exe',dir_fd=fd)
        second=parse(read('status'),read('stat').decode('ascii'))
        current_ns=os.stat('ns/pid',dir_fd=fd)
        identities=[os.fstat(fd),os.stat(path),os.stat('/proc/'+str(first['visible_pid']))]
        if first!=second or any((x.st_dev,x.st_ino)!=(root.st_dev,root.st_ino) for x in identities) or (current_ns.st_dev,current_ns.st_ino)!=(ns.st_dev,ns.st_ino) or os.readlink('exe',dir_fd=fd)!=executable:
            raise CustodyError('proc descriptor/name/start identity changed')
        return {**first,'proc_device':root.st_dev,'proc_inode':root.st_ino,
                'namespace_device':ns.st_dev,'namespace_inode':ns.st_ino,'exe':executable}
    finally:
        if nsfd is not None:os.close(nsfd)
        os.close(fd)

class PidfdCustody:
    def __init__(self):
        if not hasattr(os,'pidfd_open') or not hasattr(signal,'pidfd_send_signal'):
            raise CustodyError('kernel pidfd interfaces unavailable')
        self.pid=os.getpid(); self.owner=observe('/proc/self'); self.depth=len(self.owner['namespace_pids'])
        if self.owner['namespace_pids'][-1]!=self.pid or os.readlink('/proc/self')!=str(self.owner['visible_pid']):
            raise CustodyError('caller PID namespace presentation differs')
        fd=os.pidfd_open(self.pid,0)
        try:self._fd_binding(fd,self.owner);signal.pidfd_send_signal(fd,0,None,0)
        finally:os.close(fd)
        self.ensure_owner()
    def ensure_owner(self):
        if os.getpid()!=self.pid or observe('/proc/self')!=self.owner:
            raise CustodyError('caller process/namespace changed')
    def _fd_binding(self,fd,snapshot):
        info=fields(Path('/proc/self/fdinfo/'+str(fd)).read_bytes())
        if info.get('Pid')!=[str(snapshot['visible_pid'])] or info.get('NSpid')!=list(map(str,snapshot['namespace_pids'])):
            raise CustodyError('opened pidfd refers to another namespace/process')
        return {'Pid':info['Pid'],'NSpid':info['NSpid']}
    def local_snapshot(self,local_pid):
        self.ensure_owner();fd=os.pidfd_open(local_pid,0)
        try:
            info=fields(Path('/proc/self/fdinfo/'+str(fd)).read_bytes())
            visible=int(info['Pid'][0]);snapshot=observe('/proc/'+str(visible));self._fd_binding(fd,snapshot)
            if len(snapshot['namespace_pids'])<self.depth or snapshot['namespace_pids'][self.depth-1]!=local_pid:
                raise CustodyError('local child depth mapping differs')
            return snapshot
        finally:os.close(fd)
    def signal_observed(self,expected,signum,ownership):
        self.ensure_owner();visible=expected['visible_pid'];path='/proc/'+str(visible)
        first=observe(path)
        if first!=expected:raise CustodyError('candidate identity changed before pidfd acquisition')
        if not ownership(first):raise CustodyError('candidate is outside explicit owned scope')
        chain=first['namespace_pids']
        if len(chain)<self.depth:raise CustodyError('candidate is not addressable at caller namespace depth')
        local_pid=chain[self.depth-1]
        if local_pid==self.pid:raise CustodyError('refuse caller process')
        fd=os.pidfd_open(local_pid,0)
        try:
            binding=self._fd_binding(fd,first)
            if observe(path)!=first or not ownership(first):raise CustodyError('candidate changed across pidfd acquisition')
            self.ensure_owner()
            signal.pidfd_send_signal(fd,signum,None,0)
            return {'status':'SENT_BY_HELD_PIDFD','signal':int(signum),'visible_pid':visible,'local_pid':local_pid,
                    'namespace_depth':self.depth,'pidfd_binding':binding,'start_ticks':first['start_ticks'],
                    'proc_inode':first['proc_inode'],'namespace_inode':first['namespace_inode'],'exe':first['exe'],
                    'namespace_sessions':first['namespace_sessions'],'ownership_predicate_verified':True}
        finally:os.close(fd)
