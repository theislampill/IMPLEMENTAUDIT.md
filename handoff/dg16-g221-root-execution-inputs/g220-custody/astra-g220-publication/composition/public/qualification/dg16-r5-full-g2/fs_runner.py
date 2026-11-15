"""Gated fixed child with the exact current maintained nearest-owner class.

Effects are only in Executor.__call__, after supplied actual root currentness,
tool/code pins and finite deadline. No default selection, admission or key.
"""
import ast
import copy
import errno
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import sys
import time
import types
import fs_protocol as P
import fs_io as F
import fs_command as C

MEMBERS={'fs_protocol.py','fs_io.py','fs_command.py','fs_carrier.py','full_g2_hooks.py','fs_runner.py',
         'fs_transport.py','bound_child.py','capture_evidence.py','CAPTURE_DIAGNOSTIC_CATALOG.json'}

def pinned(path,pin,maximum):
    path=Path(path).absolute();P.need(path.resolve(strict=True)==path,'CODE_TOOL_PHYSICAL_PATH')
    before=path.lstat();P.descriptor(pin,maximum)
    P.need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size==pin['bytes']
      and not stat.S_IMODE(before.st_mode)&0o022,'CODE_TOOL_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        P.need(F.stamp(os.fstat(fd))==F.stamp(before),'CODE_TOOL_OPEN_CHANGED');h=__import__('hashlib').sha256();parts=[];size=0
        while True:
            raw=os.read(fd,min(P.CHUNK,maximum-size+1))
            if not raw:break
            size+=len(raw);P.need(size<=maximum,'CODE_TOOL_BOUND');h.update(raw)
            if maximum<=1024**2:parts.append(raw)
        P.need(size==pin['bytes'] and h.hexdigest()==pin['sha256'] and F.stamp(os.fstat(fd))==F.stamp(before)
          and F.stamp(path.lstat())==F.stamp(before),'CODE_TOOL_PIN_CHANGED')
        return b''.join(parts) if parts else None
    finally:os.close(fd)

def load_owner(path):
    P.need(path is not None,'ACTUAL_OWNER_SOURCE_REQUIRED');path=Path(path)
    before=path.stat();raw=pinned(path,{'bytes':before.st_size,'sha256':P.OWNER_SHA},1024**2)
    tree=ast.parse(raw);matches=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_CaptureChildren']
    P.need(len(matches)==1,'EXACT_OWNER_CLASS');node=matches[0]
    namespace=dict(os=os,sys=sys,signal=signal,time=time,errno=errno,re=re,Path=Path,ROOT=Path('/'),
      WG=types.SimpleNamespace(WorkGraphError=P.Refusal))
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
    return namespace['_CaptureChildren'],dict(source_sha256=P.OWNER_SHA,
      ast_sha256=P.sha(ast.dump(node,include_attributes=False).encode()),instantiated=False,
      scope='EXACT_ORDINARY_SINGLE_PROC_OWNER_CLASS; no maintained verifier or nested profile selected')

class Executor:
    def __init__(self,owner_path,python_path,tool_pins,component_pins,current,*,witness_key_generation=False):
        self.owner_path=owner_path;self.python_path=python_path;self.tools=tool_pins;self.pins=component_pins;self.current=current
        self.last=None;self.witness_key_generation=witness_key_generation
    def check(self):
        P.need(callable(self.current),'ACTUAL_ROOT_CURRENTNESS_REQUIRED');self.current()
        P.need(type(self.tools) is dict and self.python_path is not None and len(self.tools)==2 and set(self.tools)=={'/usr/bin/openssl',str(self.python_path)},
          'ACTUAL_TOOL_PINS_REQUIRED')
        P.need(type(self.pins) is dict and set(self.pins)==MEMBERS,'ACTUAL_COMPONENT_PINS_REQUIRED')
        for path,pin in self.tools.items():pinned(path,pin,32*1024**2)
        for name,pin in self.pins.items():pinned(Path(__file__).parent/name,pin,1024**2)
    def closing(self,deadline):
        self.check();deadline.check()
    def __call__(self,operation,files,maximum,deadline):
        P.need(operation=='encrypt' and self.witness_key_generation is False,'HOST_ENCRYPT_ONLY')
        deadline.check();P.need(callable(self.current),'ACTUAL_ROOT_CURRENTNESS_REQUIRED');self.current();deadline.check()
        self.check();deadline.check()
        fds={n:f.fd for n,f in files.items()};C.cms_argv(operation,fds)
        ceiling=P.CIPHER_MAX if operation=='encrypt' else P.PLAIN_MAX if operation=='decrypt' else 8192
        P.need(P.integer(maximum,1,ceiling),'COMMAND_FILE_BOUND')
        for file in files.values():file.verify()
        Owner,source=load_owner(self.owner_path);deadline.check()
        started=time.monotonic();stop=min(deadline.stop,started+60)-3
        P.need(time.monotonic()<stop,'COMMAND_CLEANUP_RESERVE_UNAVAILABLE')
        owner=None;owned=set();selector=None;buffers=[b'',b''];error_bytes=b''
        process_started=False;pidfd_acquired=False;timeout=False;overflow=False;streams_complete=False
        failure=None;close_error=None;rc=None;before_close=None;closed=False
        mask=signal.pthread_sigmask(signal.SIG_BLOCK,set())
        handlers={n:signal.getsignal(n) for n in (signal.SIGINT,signal.SIGTERM,signal.SIGCHLD)}
        def pipe():
            pair=os.pipe2(os.O_CLOEXEC);owned.update(pair);return pair
        def close(fd):
            if fd is not None and fd in owned:owned.remove(fd);os.close(fd)
        try:
            owner=Owner();source['instantiated']=True;owner.require_quiescent()
            gate_r,gate_w=pipe();error_r,error_w=pipe();out_r,out_w=pipe();err_r,err_w=pipe()
            null=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW);owned.add(null)
            info=os.fstat(null);P.need(stat.S_ISCHR(info.st_mode) and os.major(info.st_rdev)==1 and os.minor(info.st_rdev)==3,'EMPTY_STDIN_DEVICE')
            argv=[str(self.python_path),'-I','-S','-B',str(Path(__file__).with_name('bound_child.py')),operation,str(maximum),
              *[str(fds[n]) for n in C.ROLES[operation]]]
            self.check()
            for file in files.values():file.verify()
            P.need(time.monotonic()<stop,'COMMAND_TIMEOUT_BEFORE_FORK')
            pid=os.fork()
            if pid==0:
                try:
                    for fd in (gate_w,error_r,out_r,err_r):close(fd)
                    for name in ('SIGINT','SIGTERM','SIGPIPE','SIGXFZ','SIGXFSZ'):
                        if hasattr(signal,name):signal.signal(getattr(signal,name),signal.SIG_DFL)
                    if os.read(gate_r,1)!=b'R':os._exit(125)
                    close(gate_r);os.chdir('/')
                    os.dup2(null,0);os.dup2(out_w,1);os.dup2(err_w,2)
                    keep={0,1,2,error_w,*fds.values()}
                    for fd in (0,1,2,*fds.values()):os.set_inheritable(fd,True)
                    seen=[]
                    with os.scandir('/proc/self/fd') as entries:
                        for entry in entries:
                            P.need(len(seen)<4096 and entry.name.isdigit(),'CHILD_DESCRIPTOR_BOUND');seen.append(int(entry.name))
                    for fd in seen:
                        if fd not in keep:
                            try:os.close(fd)
                            except OSError as exc:
                                if exc.errno!=errno.EBADF:raise
                    os.execve(str(self.python_path),argv,{'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENSSL_CONF':'/dev/null'})
                except BaseException as exc:
                    number=exc.errno if isinstance(exc,OSError) and exc.errno is not None else errno.EINVAL
                    try:os.write(error_w,(str(number)+'\n').encode())
                    finally:os._exit(126)
            process_started=True;owner.status['primary_pid']=pid;owner.status['quiescence']='UNPROVED'
            for fd in (gate_r,error_w,out_w,err_w,null):close(fd)
            owner.primary_fd=os.pidfd_open(pid,0);pidfd_acquired=True
            initial=os.waitid(os.P_PIDFD,owner.primary_fd,os.WEXITED|os.WNOHANG|os.WNOWAIT|owner.WALL)
            P.need(initial is None,'CHILD_ENDED_BEFORE_RELEASE');self.check()
            for file in files.values():file.verify()
            P.need(time.monotonic()<stop,'COMMAND_TIMEOUT_BEFORE_RELEASE')
            P.need(os.write(gate_w,b'R')==1,'CHILD_RELEASE');close(gate_w)
            selector=selectors.DefaultSelector()
            for fd,index in ((out_r,0),(err_r,1),(error_r,2)):
                os.set_blocking(fd,False);selector.register(fd,selectors.EVENT_READ,index)
            while selector.get_map() or owner.status['primary_exit'] is None:
                owner.quiescent();P.need(not owner.primary_wait_missing,'PRIMARY_STATUS_UNAVAILABLE')
                remaining=stop-time.monotonic()
                if remaining<=0:timeout=True;break
                for key,_ in selector.select(min(0.05,remaining)):
                    try:chunk=os.read(key.fd,4096)
                    except BlockingIOError:continue
                    if not chunk:selector.unregister(key.fd);continue
                    if key.data==2:
                        P.need(len(error_bytes)+len(chunk)<=64,'EXEC_ERROR_BOUND');error_bytes+=chunk
                    else:
                        left=C.CAPTURE_MAX-len(buffers[key.data]);buffers[key.data]+=chunk[:left]
                        if len(chunk)>left:overflow=True
                if overflow:break
            streams_complete=not selector.get_map() and not timeout and not overflow
            if error_bytes:failure='CHILD_EXEC_REFUSED'
            if timeout:failure='COMMAND_TIMEOUT'
            if overflow:failure='COMMAND_STREAM_OVERFLOW'
            if not owner.quiescent():failure=failure or 'LIVE_DESCENDANTS_REFUSED'
        except BaseException as exc:
            failure=failure or ('COMMAND_TIMEOUT' if 'TIMEOUT' in str(exc) else 'COMMAND_CAPTURE_REFUSED')
            if 'TIMEOUT' in failure:timeout=True
        finally:
            if owner is not None:
                before_close={k:v for k,v in owner.status.items() if k!='other_child_exits'}
                before_close['other_child_exit_count']=len(owner.status['other_child_exits'])
            if selector is not None:selector.close()
            for fd in tuple(owned):
                try:close(fd)
                except OSError:failure=failure or 'DESCRIPTOR_CLOSE_REFUSED'
            if owner is not None:
                try:owner.close()
                except BaseException:close_error='OWNED_CLOSE_REFUSED'
                rc=owner.status['primary_exit']
                closed=owner.status['quiescence']=='ECHILD_ALL_CHILDREN' and owner.status['flag_restored'] is True and not owner.active
            restored=(signal.pthread_sigmask(signal.SIG_BLOCK,set())==mask
              and all(signal.getsignal(n)==h for n,h in handlers.items()))
            if not closed or not restored or close_error:failure=failure or 'COMMAND_CUSTODY_RESTORATION_REFUSED'
            if not process_started or not pidfd_acquired or type(rc) is not int or not streams_complete:failure=failure or 'COMMAND_CAPTURE_INCOMPLETE'
            try:self.closing(deadline)
            except BaseException:failure=failure or 'COMMAND_CLOSING_CURRENTNESS_REFUSED'
            evidence=dict(schema='dg16.failed-stream-command-owner.v1',authority='NONE',source=source,
              operation=operation,process_started=process_started,pidfd_acquired=pidfd_acquired,
              before_close=before_close,after_close=copy.deepcopy(owner.status) if owner is not None else None,
              mask_and_handlers_restored=restored,close_error=close_error,started=started,command_stop=stop,
              ending=time.monotonic(),enclosing_deadline=deadline.stop,cleanup_seconds=3,original_acceptance=False)
            raw=P.encode(evidence);P.need(len(raw)<=262144,'OWNER_EVIDENCE_BOUND')
            output=files['cipher' if operation=='encrypt' else 'quarantine' if operation=='decrypt' else 'key']
            with F.Output(output.directory,'CAPTURE_OWNER.json',262144) as file:
                file.write(raw);owner_descriptor=file.descriptor(lambda:None)
            row=dict(name='failed-stream-'+operation,process_started=process_started,pidfd_acquired=pidfd_acquired,
              returncode=rc,timeout=timeout,output_bound_exceeded=overflow,streams_complete=streams_complete,
              internal_failure=failure,cleanup=dict(echild=closed,restoration_complete=restored),owner_evidence=owner_descriptor,
              stdout_bytes=len(buffers[0]),stderr_bytes=len(buffers[1]),stdout_sha256=P.sha(buffers[0]),stderr_sha256=P.sha(buffers[1]))
            self.last=dict(record=row,owner=evidence)
        return [row],rc,buffers[0],buffers[1]
