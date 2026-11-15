"""Explicit Pro encryption capture using the exact maintained child custodian.

The maintained launch method is not used: it closes the carrier's pass-FDs.
This adapter has no role, command, executable, working-directory or signal
selection API. Loading is inert; capture is a separately admitted real effect.
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
    expected=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',
      'cms','-encrypt','-binary','-aes-256-gcm','-in','/proc/self/fd/'+str(plain),'-outform','DER',
      '-out','/proc/self/fd/'+str(cipher),'-recip','/proc/self/fd/'+str(certificate),
      '-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
    P.need(type(argv) is list and argv==expected,'SENDER_FIXED_ENCRYPT_COMMAND')
    return True

def close_plan(visible,kept,error_fd):
    P.need(type(visible) is list and len(visible)<=FD_LIMIT and len(visible)==len(set(visible))
      and all(type(fd) is int and 0<=fd<2**31 for fd in visible),'SENDER_DESCRIPTOR_POPULATION')
    P.need(len(kept)==3 and error_fd not in kept,'SENDER_ERROR_FD_ALIAS')
    return [fd for fd in visible if fd>2 and fd not in kept and fd!=error_fd]

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

class CaptureSession:
    def __init__(self,directory,budget,currentness):
        self.directory=Path(directory);self.currentness=currentness;self.calls=0;self.last=None;self.owner=None
        self.Owner,self.source_opening=load_owner()
        budget.reserve(OWNER_EVIDENCE_MAX,1)  # Before any possible child output.
    def _current(self):
        source_current(self.source_opening);self.currentness()
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
        evidence=None;rc=None;before_close=None;restore={};after_fds=None
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
                    for fd in close_plan(visible,fds,error_w):
                        try:os.close(fd)
                        except OSError as exc:
                            if exc.errno!=errno.EBADF:raise
                    os.execve('/usr/bin/env',argv,{'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENSSL_CONF':'/dev/null'})
                except BaseException as exc:
                    number=exc.errno if isinstance(exc,OSError) and exc.errno is not None else errno.EINVAL
                    try:os.write(error_w,(str(number)+'\n').encode('ascii'))
                    finally:os._exit(126)
            process_started=True;owner.status['primary_pid']=pid;owner.status['quiescence']='UNPROVED'
            for fd in (gate_r,error_w,out_w,err_w,null_fd):close(fd)
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
