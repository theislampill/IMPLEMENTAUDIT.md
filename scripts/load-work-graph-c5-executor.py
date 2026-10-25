#!/usr/bin/env python3
"""Separate fixed genuine-C5 executor source owner; no default whitelist change.

The outer caller must bind the exact loader buffer it executes. A read of this
file is physical currentness only. Post-commit comparison metadata has no live
custody or completion authority and cannot select commands or source members.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import types

ROOT=Path(__file__).absolute().parents[1]
LOADER='scripts/load-work-graph-c5-executor.py'
MAX_SOURCE_BYTES=1024**2
PREFIX = 'scripts/qualify-work-graph-prefix.py'
BASE = 'scripts/work-graph-c5-inputs.py'
PROVIDER = 'scripts/work-graph-c5-provider-inputs.py'
EVENT = 'scripts/repro-event-capture.py'
COMPLETION = 'scripts/work-graph-completion.py'
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
QUALIFIER = 'scripts/qualify-work-graph-verifier.py'
GATE = 'scripts/work-graph-c5-live-gate.py'
EXECUTOR = 'scripts/work-graph-c5-executor.py'
BASE_SELECTION = 'fixtures/work-graph-c5-inputs/execution-system-python312.json'
PROVIDER_SELECTION = 'fixtures/work-graph-c5-inputs/package-venv-python312.json'
EXECUTION_SELECTION = 'fixtures/work-graph-c5-inputs/genuine-execution-profile.json'
PROFILE='FIXED_GENUINE_C5_PRODUCER_EFFECT_ORIGINAL48_V1'
PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': '86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016', 'scripts/work-graph-c5-inputs.py': 'c9dc12fb3d9c12c8161426956944730ba543f66ffec0c36abd8a1193f3c5cd4f', 'scripts/work-graph-c5-provider-inputs.py': '9b29c100a2b89fe6f53072f726f990ecd115cdb6f7bff574e2e62b48099baff4', 'scripts/repro-event-capture.py': 'f8238acbb6aea7bb1c246774ee780149abad56c9221fe31640d522e53f8da443', 'scripts/work-graph-completion.py': '1a73009c7085c66797d9310258b2b1d723f304a0034cbc6a7ce16e1c97283b92', 'skills/implementaudit/scripts/compile-work-graph.py': '1824b1f9d38c53d45016ed249926784c958cfd24b59920df2252ef366f6ec46b', 'scripts/qualify-work-graph-verifier.py': 'b06561d44f48d49aef97f9a29364e4016cdff44782381d1cca258a86420171a0', 'scripts/work-graph-c5-live-gate.py': '5221b3039263ba42ededa080591cd9e23608e44ee601ad8b72b7eba590a7be60', 'scripts/work-graph-c5-executor.py': '3be657bce635eafccf0b000dedb85e2ae62cb95c874b03c953c192738b9524ce', 'fixtures/work-graph-c5-inputs/execution-system-python312.json': 'c22e25897db88cb86a345a79ff5da39ef7b335571aff8786617ea6c82a4ac1fa', 'fixtures/work-graph-c5-inputs/package-venv-python312.json': 'c6ba97cd3be936284eab790b3b35cec92c4f84252086c817eabbd372c2c68014', 'fixtures/work-graph-c5-inputs/genuine-execution-profile.json': '5dbcaddb4d33ee046592030c49108e859fd104c75e138d3be614b4cc82c194b1'})
ORIGINS=types.MappingProxyType({'base_logical_key': 'fixtures/work-graph-c5-inputs/system-python312.json', 'base_actual_member': 'fixtures/work-graph-c5-inputs/execution-system-python312.json', 'provider_actual_member': 'fixtures/work-graph-c5-inputs/package-venv-python312.json'})


def _identity(info):
    return (str(info.st_dev),str(info.st_ino),info.st_mode,info.st_nlink,
            info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def _anchor(info):
    return (str(info.st_dev),str(info.st_ino),info.st_mode,info.st_uid,info.st_gid)


def _read(name):
    if name not in PINS and name!=LOADER:raise ValueError('Unknown fixed C5 execution member')
    path=ROOT/name
    if not path.is_absolute() or '..' in path.parts:raise ValueError('C5 execution source alias is unsupported')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    current=Path('/')
    ancestors={str(current):_anchor(os.fstat(directory))}
    fd=None
    try:
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
            os.close(directory);directory=child;current/=part
            ancestors[str(current)]=_anchor(os.fstat(directory))
        before=os.stat(path.name,dir_fd=directory,follow_symlinks=False)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink!=1
                or stat.S_IMODE(before.st_mode) not in (0o644,0o755) or not 0<before.st_size<=MAX_SOURCE_BYTES):
            raise ValueError('C5 execution source must be a bounded ordinary single-link file')
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
        if _identity(os.fstat(fd))!=_identity(before) or os.listxattr(fd):
            raise ValueError('C5 executing source changed or has unsupported extended metadata')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(MAX_SOURCE_BYTES+1)
        if (len(raw)!=before.st_size or _identity(os.fstat(fd))!=_identity(before)
                or _identity(os.stat(path.name,dir_fd=directory,follow_symlinks=False))!=_identity(before)):
            raise ValueError('C5 execution source changed during capture')
        return raw,_identity(before),ancestors
    finally:
        if fd is not None:os.close(fd)
        os.close(directory)


class _Engine:
    def __init__(self):
        sources={};ancestors={}
        for name in (LOADER,*PINS):
            raw,identity,observed=_read(name)
            if name in PINS and hashlib.sha256(raw).hexdigest()!=PINS[name]:
                raise ValueError('Unsupported fixed C5 execution member: '+name)
            for directory,value in observed.items():
                if directory in ancestors and ancestors[directory]!=value:
                    raise ValueError('C5 execution source ancestor changed during capture')
                ancestors[directory]=value
            sources[name]=(raw,identity)
        self.sources=types.MappingProxyType(sources)
        self.ancestors=types.MappingProxyType(ancestors)
        self.check()

    def check(self):
        for name,expected in self.sources.items():
            raw,identity,ancestors=_read(name)
            if (raw,identity)!=expected or any(self.ancestors[name]!=value for name,value in ancestors.items()):
                raise ValueError('Captured C5 execution source or ancestor is no longer current')

    def load(self):
        selection=json.loads(self.sources[EXECUTION_SELECTION][0])
        if (selection.get('schema')!='implementaudit.c5-execution-selection.v1'
                or selection.get('profile')!=PROFILE or selection.get('selection_origins')!=dict(ORIGINS)
                or selection.get('original_argv')!=['bash','tests/reproducible-release-asset.test.sh']):
            raise ValueError('Unsupported fixed C5 execution selection')
        # The unchanged data reader names its historical logical fixture key.
        # This explicit map binds that key to the separately captured execution
        # selection. The old physical selection/default loader remain untouched.
        base_sources=dict(self.sources)
        base_sources[ORIGINS['base_logical_key']]=self.sources[BASE_SELECTION]
        base_sources=types.MappingProxyType(base_sources)
        modules={}
        for name in (PREFIX,BASE,PROVIDER,QUALIFIER,EVENT,COMPLETION,GATE,EXECUTOR):
            self.check()
            module=types.ModuleType('_fixed_genuine_c5_'+Path(name).stem.replace('-','_'))
            module.__file__=str(ROOT/name);module.__package__=''
            if name==BASE:
                module._R0035_C5_INPUT_CAPTURE=dict(prefix=modules[PREFIX],sources=base_sources,check=self.check)
            elif name==PROVIDER:
                module._R0035_C5_PROVIDER_CAPTURE=dict(prefix=modules[PREFIX],base=modules[BASE],sources=self.sources,check=self.check)
            elif name==QUALIFIER:
                module._R0035_EFFECT_SOURCE_CAPTURE=dict(driver=self.sources[QUALIFIER][0],compiler=self.sources[COMPILER][0],
                    expected_compiler_sha256=PINS[COMPILER])
            elif name==GATE:
                module._R0035_C5_LIVE_GATE_CAPTURE=dict(capture=modules[EVENT],completion=modules[COMPLETION],
                    compiler_sha256=PINS[COMPILER],check=self.check)
            elif name==EXECUTOR:
                module._R0035_C5_EXECUTOR_CAPTURE=dict(prefix=modules[PREFIX],base=modules[BASE],provider=modules[PROVIDER],
                    gate=modules[GATE],qualifier=modules[QUALIFIER],sources=self.sources,check=self.check,
                    root=str(ROOT),selection=selection)
            try:exec(compile(self.sources[name][0],module.__file__,'exec'),module.__dict__)
            finally:self.check()
            modules[name]=module
        return modules[EXECUTOR]


def create_genuine_c5_session(source_root,output,*,expected_source):
    """Create one fixed local execution owner, never import a prior result.

    expected_source is exact post-commit comparison data from the separately
    reviewed outer envelope. The executor binds it to captured Git bytes and
    actual INIT/clone observations; it cannot grant execution or native authority.
    """
    return _Engine().load().GenuineC5Session(source_root,output,expected_source=expected_source)
