#!/usr/bin/env python3
"""Applicable reviewed G205 source/custody helpers; no entrypoint or workload."""
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
SOURCE_COMMIT = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
SOURCE_TREE = '0da374609f7fea2463a2926f3603b976620bd10e'
MANIFEST_SHA = '466aa14af0ff6e2cde20bb2727511625b7297cfa00a3b4d529b11492f5b4486f'
NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md')
PRIVATE_CANONICAL_BYTES = 1024 * 1024
class Refusal(Exception): pass

def need(value, code):
    if not value: raise Refusal(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def canonical(value): return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')

def token(raw, pattern):
    text=raw.decode('ascii').strip(); need(re.fullmatch(pattern,text) is not None,'OWNER_TOKEN_SHAPE_REFUSED'); return text

def identities(path):
    p=Path(path); st=p.lstat();need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'DIRECTORY_CUSTODY_REFUSED')
    return [st.st_dev,st.st_ino,st.st_uid]

def read_manifest(u):
    raw=u.checked_file(Path(__file__).with_name('SOURCE_MANIFEST.json'),1024*1024)
    need(digest(raw)==MANIFEST_SHA,'SOURCE_MANIFEST_DIGEST_REFUSED'); m=u.parse_json(raw)
    need(set(m)=={'schema','repository','commit','tree','file_count','total_bytes','members'} and
         m['schema']=='dg16.linux-native-source-manifest.v2' and m['repository']==REPOSITORY and
         m['commit']==SOURCE_COMMIT and m['tree']==SOURCE_TREE and m['file_count']==1759 and
         m['total_bytes']==166402972 and len(m['members'])==1759,'SOURCE_MANIFEST_SHAPE_REFUSED')
    result={}
    for row in m['members']:
        need(set(row)=={'path','mode','git_blob','bytes','sha256'} and isinstance(row['path'],str),'SOURCE_MEMBER_REFUSED')
        p=PurePosixPath(row['path']);need(not p.is_absolute() and '..' not in p.parts and str(p)==row['path'] and
             row['path'] not in result and row['mode'] in ('100644','100755') and
             type(row['bytes']) is int and 0<=row['bytes']<=256*1024**2 and
             re.fullmatch('[0-9a-f]{40}',row['git_blob']) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'SOURCE_MEMBER_REFUSED')
        result[row['path']]=row
    need(sum(row['bytes'] for row in result.values())==m['total_bytes'],'SOURCE_SIZE_REFUSED')
    return result

def verify_source(source,manifest,u,runtime=False):
    observed=set();total=0
    allowed_dirs={str(p) for name in manifest for p in PurePosixPath(name).parents if str(p)!='.'}
    for parent,dirs,files in os.walk(source,followlinks=False):
        here=Path(parent)
        for name in list(dirs):
            p=here/name; rel=p.relative_to(source).as_posix(); st=p.lstat()
            need(stat.S_ISDIR(st.st_mode) and not p.is_symlink(),'SOURCE_DIRECTORY_SHAPE_REFUSED')
            if here==source and name=='.git':dirs.remove(name)
            elif here==source and name=='.IMPLEMENTAUDIT':
                need(runtime,'UNEXPECTED_RUNTIME_BEFORE_CLAIM');dirs.remove(name)
            else:need(rel in allowed_dirs,'UNEXPECTED_SOURCE_DIRECTORY')
        for name in files:
            p=here/name;rel=p.relative_to(source).as_posix()
            need(rel in manifest,'UNEXPECTED_SOURCE_FILE');row=manifest[rel];st=p.lstat()
            need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not st.st_mode & 0o6000 and
                 bool(st.st_mode & 0o111)==(row['mode']=='100755'),'SOURCE_FILE_MODE_REFUSED')
            raw=u.checked_file(p,256*1024**2);need(len(raw)==row['bytes'] and digest(raw)==row['sha256'] and
                 hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'SOURCE_BYTES_REFUSED')
            total+=len(raw);observed.add(rel)
    need(observed==set(manifest) and total==166402972,'SOURCE_POPULATION_REFUSED')
    return {'file_count':len(observed),'total_bytes':total,'manifest_sha256':MANIFEST_SHA,'all_members_match':True}

def runtime_snapshot(source,state,u):
    run=state['run_root'];need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}',run),'RUN_ROOT_SHAPE_REFUSED')
    base=source/'.IMPLEMENTAUDIT'; expected={'.r36-locks/namespace.gate'}
    prefix=run.removeprefix('.IMPLEMENTAUDIT/')+'/'
    expected.update(prefix+n for n in (*NAMES,'phases/phase-1.md','.claimed','.controller'))
    observed={};directories=set();total=0
    for parent,dirs,files in os.walk(base,followlinks=False):
        here=Path(parent);st=here.lstat();need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.geteuid() and not here.is_symlink(),'RUNTIME_DIRECTORY_REFUSED')
        directories.add(here.relative_to(base).as_posix())
        for name in dirs:need(not (here/name).is_symlink(),'RUNTIME_SYMLINK_REFUSED')
        for name in files:
            p=here/name;rel=p.relative_to(base).as_posix();st=p.lstat();need(rel in expected and st.st_uid==os.geteuid(),'RUNTIME_POPULATION_REFUSED')
            canonical_member=rel.startswith(prefix) and rel[len(prefix):] in (*NAMES,'phases/phase-1.md')
            raw=u.checked_file(p,PRIVATE_CANONICAL_BYTES if canonical_member else 65536);total+=len(raw);need(total<=512*1024,'RUNTIME_AGGREGATE_BOUND')
            observed[rel]={'bytes':len(raw),'sha256':digest(raw),'device':st.st_dev,'inode':st.st_ino}
    expected_dirs={'.','.r36-locks','runs',run.removeprefix('.IMPLEMENTAUDIT/'),run.removeprefix('.IMPLEMENTAUDIT/')+'/phases'}
    need(set(observed)==expected and directories==expected_dirs,'RUNTIME_POPULATION_REFUSED')
    need(observed['.r36-locks/namespace.gate']['bytes']==1,'RUNTIME_GATE_SHAPE_REFUSED')
    return observed

def write_private(path,raw):
    need(not path.exists(),'PRIVATE_MEMBER_ALREADY_EXISTS')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o600)

def save_state(path,state):
    tmp=path.with_suffix('.next');need(not tmp.exists(),'STATE_WRITE_INTERRUPTED')
    with tmp.open('xb') as f:f.write(canonical(state));f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o600);os.replace(tmp,path)

def setup_sudo(u):
    # Administrative provisioning intentionally uses distro sudo. Its expected
    # setuid bit is not allowed into the native transport's non-setid profile.
    pending=['usr','bin','sudo'];path=Path('/');links=0;root=path.lstat()
    need(stat.S_ISDIR(root.st_mode) and root.st_uid==0 and not root.st_mode&0o022,'SETUP_ROOT_CUSTODY_REFUSED')
    observed=[{'path':'/','device':root.st_dev,'inode':root.st_ino,'mode':root.st_mode,
               'uid':root.st_uid,'gid':root.st_gid,'links':root.st_nlink}]
    while pending:
        name=pending.pop(0)
        if name in ('','.'):continue
        if name=='..':path=path.parent;continue
        candidate=path/name;info=candidate.lstat()
        need(info.st_uid==0,'SETUP_SUDO_OWNERSHIP_REFUSED')
        observed.append({'path':str(candidate),'device':info.st_dev,'inode':info.st_ino,
                         'mode':info.st_mode,'uid':info.st_uid,'gid':info.st_gid,'links':info.st_nlink})
        if stat.S_ISLNK(info.st_mode):
            links+=1;target=os.readlink(candidate)
            need(links<=16 and len(target.encode())<=4096,'SETUP_SUDO_ALIAS_BOUND')
            observed[-1]['target_sha256']=digest(os.fsencode(target))
            target_path=Path(target)
            if target_path.is_absolute():path=Path('/');parts=target_path.parts[1:]
            else:parts=target_path.parts
            pending=list(parts)+pending
        else:
            need(not info.st_mode&0o022 and (stat.S_ISDIR(info.st_mode) if pending else stat.S_ISREG(info.st_mode)),
                 'SETUP_SUDO_ANCESTRY_REFUSED')
            path=candidate
    # Ubuntu's documented sudo-rs alternative resolves here; this is an exact
    # administrative-setup target, never a non-setid native transport admission.
    need(path in (Path('/usr/bin/sudo'),Path('/usr/bin/sudo-rs'),
                  Path('/usr/bin/sudo.ws'),Path('/usr/lib/cargo/bin/sudo')),
         'SETUP_SUDO_TARGET_REFUSED')
    info=path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and 1<=info.st_nlink<=16 and
         stat.S_IMODE(info.st_mode)==0o4755,'SETUP_SUDO_PROFILE_REFUSED')
    raw=u.checked_file(path,64*1024*1024,single_link=False)
    return {'bytes':len(raw),'sha256':digest(raw),'mode':0o4755,'uid':0,
            'canonical':str(path),'aliases_and_ancestors':observed,
            'scope':'ADMINISTRATIVE_PACKAGE_SETUP_ONLY_NOT_NATIVE_TRANSPORT'}

def enable_subreaper():
    lib=ctypes.CDLL(None,use_errno=True);actual=ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0 and lib.prctl(37,ctypes.byref(actual),0,0,0)==0 and actual.value==1,'SUBREAPER_REFUSED')

def check_source_git(command,tools,source,full=False):
    rc,out,err=command('source-identity',[tools['git'],'-C',str(source),'rev-parse','HEAD','HEAD^{tree}'])
    need(rc==0 and not err and out.decode().splitlines()==[SOURCE_COMMIT,SOURCE_TREE],'SOURCE_GIT_IDENTITY_REFUSED')
    if not full:return
    for kind,args in (('index-clean',['diff','--cached','--quiet','--exit-code']),('tracked-clean',['diff','--quiet','--exit-code'])):
        rc,out,err=command(kind,[tools['git'],'-C',str(source),*args]);need(rc==0 and not out and not err,'SOURCE_TRACKED_STATE_CHANGED')
