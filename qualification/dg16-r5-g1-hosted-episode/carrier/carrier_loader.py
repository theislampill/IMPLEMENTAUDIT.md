"""Load exactly the reviewed carrier bodies in a fresh isolated interpreter.

The enclosing immutable workflow and external entry bind this loader. The
loader binds the implementation bodies; no implementation imports this file.
"""
import hashlib
import os
from pathlib import Path
import stat
import sys
import types

MODULE_PINS = {'bundle_codec': {'bytes': 4404, 'sha256': '81b4494e8940f9f4a70d7359f689c099caa1a152aa6afd71008183fb2b5fd2aa'}, 'carrier_policy': {'bytes': 13481, 'sha256': '79bd118acc54a60a3b35d155a981ff7a501964b7f6b51bfd94b61f6e9253b03b'}, 'carrier_io': {'bytes': 15576, 'sha256': '779461deb44bf0192a4253c9a257926e23b6ab73cf5da602d0dc86a31e90d274'}, 'provider_reader': {'bytes': 19139, 'sha256': '9d1a2624796f98127214d990acbfe72e0d6f2b7a603d739ace39678e44d66726'}, 'sender_policy': {'bytes': 4707, 'sha256': '83081bd900d2c0dc5b9e2ec8d1a1ff52f95f36d69dfae69a1a1943043c27863f'}, 'sender_capture': {'bytes': 16748, 'sha256': '232bfdfc2ad7edbbce125110518ac2ce60fc5044b00614d6b4c472c2054e783e'}, 'tool_broker': {'bytes': 19693, 'sha256': '1157d3466630218093ace25ea1704c15653092b5f0aa62ff5c3254ad25afebd9'}, 'host_tools': {'bytes': 26922, 'sha256': '876aeb6af4c5c40bc234409c60ee3d6d73421c28fbd73ef07ab212a11b501e5c'}, 'carrier': {'bytes': 42835, 'sha256': 'a2ffc6d5dc0828ab1dec7a478b8d3e624f35f85a494e7a7fc5086fb3e8552ab1'}}
ORDER = ('bundle_codec', 'carrier_policy', 'carrier_io', 'provider_reader', 'sender_policy', 'sender_capture', 'tool_broker', 'host_tools', 'carrier')
_CACHE=None

def need(ok,code):
    if not ok:raise ValueError(code)

def stamp(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid]

def parents(path):
    result=[]
    for p in reversed(path.parents):
        s=p.lstat();need(stat.S_ISDIR(s.st_mode) and not p.is_symlink(),'LOADER_PARENT_ALIAS')
        result.append([str(p),s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid])
    return result

def read(path):
    path=path.absolute();ancestry=parents(path);before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=1024*1024
      and stat.S_IMODE(before.st_mode) in (0o400,0o444,0o644),'LOADER_SOURCE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'LOADER_OPEN_CHANGED')
        raw=os.pread(fd,1024*1024+1,0)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
          and stamp(path.lstat())==stamp(before) and parents(path)==ancestry,'LOADER_CLOSING_CHANGED')
        return raw,dict(identity=stamp(before),ancestors=ancestry)
    finally:os.close(fd)

def read_all():
    need(set(MODULE_PINS)==set(ORDER),'LOADER_MODULE_POPULATION')
    base=Path(__file__).absolute().parent;bodies={};records={}
    for name in ORDER:
        raw,record=read(base/(name+'.py'))
        need(MODULE_PINS[name]==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'LOADER_BODY_PIN')
        bodies[name]=raw;records[name]=record
    return bodies,records

def current():
    need(_CACHE is not None,'LOADER_NOT_LOADED')
    bodies,records=read_all()
    need(bodies==_CACHE['bodies'] and records==_CACHE['records'],'LOADER_CURRENTNESS')
    need(all(sys.modules.get(n) is m for n,m in _CACHE['modules'].items()),'LOADER_MODULE_REPLACED')
    return True

def load():
    global _CACHE
    need(sys.flags.isolated==1 and sys.dont_write_bytecode is True,'LOADER_FRESH_ISOLATED_INTERPRETER_REQUIRED')
    if _CACHE is not None:current();return _CACHE['public']
    bodies,records=read_all()
    need(not any(name in sys.modules for name in ORDER),'LOADER_PREEXISTING_MODULE_REFUSED')
    made={};base=Path(__file__).absolute().parent
    try:
        for name in ORDER:
            module=types.ModuleType(name);module.__file__=str(base/(name+'.py'))
            sys.modules[name]=module;made[name]=module
            exec(compile(bodies[name],module.__file__,'exec'),module.__dict__)
        public=types.SimpleNamespace(codec=made['bundle_codec'],policy=made['carrier_policy'],
          files=made['carrier_io'],provider=made['provider_reader'],carrier=made['carrier'],
          sender_policy=made['sender_policy'],sender_capture=made['sender_capture'],tool_broker=made['tool_broker'],host_tools=made['host_tools'])
        _CACHE=dict(bodies=bodies,records=records,modules=made,public=public)
        made['carrier']._LOADER_CURRENT=current
        current();return public
    except BaseException:
        _CACHE=None
        for name,module in made.items():
            if sys.modules.get(name) is module:del sys.modules[name]
        raise
