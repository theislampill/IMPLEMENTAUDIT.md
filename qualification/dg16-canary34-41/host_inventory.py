"""Exact maintained inventory function; profile provider is source-only. No admission."""
import os, sys, hashlib
from pathlib import Path
from types import SimpleNamespace

def need(value, code):
    if not value: raise ValueError(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def load_native(u): return SimpleNamespace(P=_PROFILE)

def inventory(u):
    need(sys.platform=='linux' and os.name=='posix' and os.geteuid()!=0 and os.uname().machine=='x86_64','HOST_IDENTITY_REFUSED')
    release={}
    for line in u.checked_file(Path('/etc/os-release').resolve(),16384).decode().splitlines():
        if '=' in line:
            k,v=line.split('=',1)
            if k in ('ID','VERSION_ID'):release[k]=u.token(v.strip('"'),32)
    need(release=={'ID':'ubuntu','VERSION_ID':'26.04'},'OS_IMAGE_REFUSED')
    paths={};facts={}
    for name in ('bwrap','bash','python3','git'):
        paths[name],facts[name]=u.trusted(name);need(paths[name] is not None,'TRUSTED_TOOL_UNAVAILABLE')
    need(Path(sys.executable).resolve()==Path(paths['python3']),'INTERPRETER_IDENTITY_REFUSED')
    host={'os':release,'architecture':'x86_64','kernel':u.token(os.uname().release),'uid':os.geteuid(),
      'python_version':list(sys.version_info[:3]),'image_os':u.token(os.environ.get('ImageOS','')),
      'image_version':u.token(os.environ.get('ImageVersion','')),'tools':facts,
      'boot_identity_sha256':digest(u.checked_file(Path('/proc/sys/kernel/random/boot_id'),128))}
    native=load_native(u)
    host['credentials']=native.P.credentials()
    native.P.validate_host(host)
    return paths,host
