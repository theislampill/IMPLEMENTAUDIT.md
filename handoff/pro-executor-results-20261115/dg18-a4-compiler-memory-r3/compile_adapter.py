"""Bounded same-worker compilation reuse; no module-instance or authority cache.

Only immutable code compiled from the two exact product bodies is eligible.
Every original loader and module execution still runs. A changed source body
always reaches the native compiler, so the original executing-code comparison
can refuse it. No filename rewriting, bytecode files or new process is used.
"""
import __future__
import builtins
import hashlib
import operator
import os
import sys
import threading


class ExactSourceCompiler:
    MAX_ENTRIES = 4
    # CPython 3.12.10 Include/cpython/compile.h: PyCF_MASK, excluding obsolete
    # CO_NESTED. Carry these bits from the original caller on every bypass.
    FUTURE_MASK = sum(getattr(__future__,name).compiler_flag for name in (
        'division','absolute_import','with_statement','print_function',
        'unicode_literals','barry_as_FLUFL','generator_stop','annotations'))

    def __init__(self,bodies):
        if sys.implementation.name!='cpython' or sys.version_info[:2]!=(3,12):
            raise RuntimeError('compiler adapter is qualified only for CPython 3.12')
        if not 1<=len(bodies)<=2 or any(type(name) is not str or type(raw) is not bytes
                or not raw or len(raw)>512*1024 for name,raw in bodies.items()):
            raise ValueError('one or two bounded exact byte bodies required')
        self.bodies=dict(bodies);self.entries={};self.lock=threading.RLock()
        self.original=builtins.compile
        if not isinstance(self.original,type(len)) or self.original.__module__!='builtins' or self.original.__name__!='compile':
            raise RuntimeError('native compile boundary already replaced')
        self.native_audit=sys.audit
        if (type(self.native_audit) is not type(len) or self.native_audit.__module__!='sys'
                or self.native_audit.__name__!='audit' or self.native_audit.__self__ is not sys):
            raise RuntimeError('native audit boundary already replaced')
        self.wrapper=self._compile;self.installed=False
        self.requests=0;self.hits=0;self.native_compilations=0;self.bypasses=0
        self.audit_refusals=0;self.restore_error=None

    @staticmethod
    def _integer(value):
        result=operator.index(value)
        if result < -(1<<31) or result > (1<<31)-1:
            raise OverflowError('Python int too large to convert to C int')
        return result

    def _compile(self,source,filename,mode,flags=0,dont_inherit=False,optimize=-1,*,_feature_version=-1):
        caller_flags=sys._getframe(1).f_code.co_flags & self.FUTURE_MASK
        with self.lock:
            self.requests+=1
            # Match native argument conversion order. Each user conversion is
            # called once; the native delegate receives the converted values.
            filename=os.fsdecode(filename)
            if '\0' in filename:raise ValueError('embedded null character')
            if not isinstance(mode,str):raise TypeError('compile() mode must be str')
            encoded_mode=str.encode(mode,'utf-8')
            if b'\0' in encoded_mode:raise ValueError('embedded null character')
            flags=self._integer(flags)
            dont_inherit=bool(dont_inherit)
            optimize=self._integer(optimize)
            feature=self._integer(_feature_version)
            inherited_flags=flags if dont_inherit else flags|caller_flags
            normalized_optimize=sys.flags.optimize if optimize==-1 else optimize
            name=None
            if (type(source) is bytes and type(filename) is str and type(mode) is str
                    and mode=='exec' and flags==0 and dont_inherit
                    and normalized_optimize==sys.flags.optimize and feature==-1
                    and len(filename)<=1024):
                for candidate,body in self.bodies.items():
                    if source==body:name=candidate;break
            key=(name,filename,normalized_optimize) if name is not None else None
            if key is not None and key in self.entries:
                # A cache hit must still reach real audit hooks. A refusal is
                # propagated; no code object is returned after that refusal.
                try:self.native_audit('compile',source,filename)
                except BaseException:
                    self.audit_refusals+=1
                    raise
                self.hits+=1
                return self.entries[key]
            self.native_compilations+=1
            if name is None or len(self.entries)>=self.MAX_ENTRIES:self.bypasses+=1
            result=self.original(source,filename,mode,flags=inherited_flags,
                dont_inherit=True,optimize=optimize,_feature_version=feature)
            if key is not None and len(self.entries)<self.MAX_ENTRIES:
                self.entries[key]=result
            return result

    def __enter__(self):
        if self.installed or builtins.compile is not self.original or sys.audit is not self.native_audit:
            raise RuntimeError('compiler adapter installation boundary changed')
        builtins.compile=self.wrapper;self.installed=True
        return self

    def __exit__(self,kind,value,tb):
        if not self.installed:raise RuntimeError('compiler adapter is not installed')
        if builtins.compile is not self.wrapper:
            self.restore_error='compiler boundary changed during selected worker scope'
        builtins.compile=self.original;self.installed=False
        if self.restore_error is not None and kind is None:raise RuntimeError(self.restore_error)
        return False

    def summary(self):
        return {'schema':'dg18.a4.compiler-reuse.v1','authority':'NONE',
            'same_worker_pid':os.getpid(),'requests':self.requests,'cache_hits':self.hits,
            'native_compilations':self.native_compilations,'bypasses':self.bypasses,
            'audit_refusals':self.audit_refusals,'maximum_entries':self.MAX_ENTRIES,
            'entries':[{'source_name':name,'filename_characters':len(filename),
                'filename_sha256':hashlib.sha256(filename.encode('utf-8','surrogatepass')).hexdigest(),
                'optimization':optimization} for name,filename,optimization in self.entries],
            'sources':[{'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                for name,raw in self.bodies.items()],
            'module_instances_cached':False,'filenames_rewritten':False,
            'physical_source_identity_checks_skipped':False,'installed':self.installed,
            'restore_error':self.restore_error,'original_criterion_award':None}
