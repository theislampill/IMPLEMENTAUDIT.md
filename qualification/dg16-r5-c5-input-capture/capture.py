#!/usr/bin/env python3
"""One prospective C5 host-input capture; no original executor or acceptance.

Only main allocates a provider or reads host/source inputs. Importing this file
for isolated format tests performs neither operation. Outputs are metadata;
all source, wheel, account databases and subprocess streams remain job-local.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import time
import types
import urllib.request
import zipfile
import zlib

SOURCE_COMMIT = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
BRANCH = 'pro/dg16-r5-c5-input-capture-02-20261105'
UTILITY_SHA256 = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
_UTILITY = None
_COMMAND_DEADLINE = None
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
RUNTIME_NAMES = ('RUNTIME_A.json','RUNTIME_B.json','RUNTIME_C.json','RUNTIME_D.json')
PUBLIC_NAMES = frozenset(('RESULT.json','HOST.json','SOURCE.json',*RUNTIME_NAMES,
    'PROVIDER.json','SETUP.json','DIFFERENCES.json','ARTIFACT_MANIFEST.json'))
ENV = {'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','TZ':'UTC',
       'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null',
       'GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0'}


def need(value, code):
    if not value: raise ValueError(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def selected_wheel(raw, spec):
    need(len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],'WHEEL_BYTES_DIFFER')
    expected={row['name']:row for row in spec['members']}
    need(len(expected)==len(spec['members'])==12,'WHEEL_SELECTION_POPULATION')
    for name in expected:
        path=PurePosixPath(name)
        need(not path.is_absolute() and '..' not in path.parts and '\\' not in name
             and str(path)==name and len(path.parts)==2,'WHEEL_MEMBER_PATH')
    files={}; names=set()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for info in archive.infolist():
            need(info.filename not in names,'WHEEL_DUPLICATE_MEMBER');names.add(info.filename)
            mode=info.external_attr>>16
            if info.is_dir():
                need(info.filename in {'zopfli/','zopfli-0.2.3.post1.dist-info/'}
                     and stat.S_ISDIR(mode),'WHEEL_DIRECTORY_SHAPE')
                continue
            need(info.filename in expected and stat.S_ISREG(mode),'WHEEL_FILE_POPULATION')
            row=expected[info.filename]
            need(info.file_size==row['bytes'] and stat.S_IMODE(mode)==row['mode']
                 and info.file_size<=4*1024**2 and not info.flag_bits&1,'WHEEL_MEMBER_METADATA')
            with archive.open(info) as stream: data=stream.read(row['bytes']+1)
            need(len(data)==row['bytes'] and sha(data)==row['sha256'],'WHEEL_MEMBER_BYTES')
            files[info.filename]=data
    need(set(files)==set(expected),'WHEEL_MEMBER_POPULATION')
    record='zopfli-0.2.3.post1.dist-info/RECORD';seen=set()
    for row in csv.reader(io.StringIO(files[record].decode('utf-8','strict'))):
        need(len(row)==3,'WHEEL_RECORD_SYNTAX');name,digest,size=row
        need(name in files and name not in seen,'WHEEL_RECORD_POPULATION');seen.add(name)
        if name==record: need(digest==size=='','WHEEL_RECORD_SELF')
        else:
            expected_digest='sha256='+base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode().rstrip('=')
            need(digest==expected_digest and size==str(len(files[name])),'WHEEL_RECORD_DIGEST')
    need(seen==set(files),'WHEEL_RECORD_OMISSION')
    return files


def public_envelopes(documents, limits):
    need(set(documents)<=PUBLIC_NAMES,'PUBLIC_NAME_REFUSED')
    rows=[];total=log=0
    for name,body in sorted(documents.items()):
        raw=encoded(body);total+=len(raw)
        need(len(raw)<=limits['file_bytes'] and total<=limits['total_bytes'],'PUBLIC_BYTE_LIMIT')
        row={'name':name,'bytes':len(raw),'sha256':sha(raw),'utf8_json':raw.decode()}
        line=encoded(row);log+=len(line)+len('DG16_C5_INPUT_JSON ')
        need(len(line)<=limits['encoded_line_bytes'] and log<=limits['encoded_log_bytes'],'PUBLIC_ENCODED_LIMIT')
        rows.append(row)
    return rows


def compressed_catalog(value):
    raw=encoded(value);need(len(raw)<=1024**2,'CATALOG_DECODED_LIMIT')
    return {'encoding':'zlib-base64','decoded_bytes':len(raw),'decoded_sha256':sha(raw),
            'zlib_base64':base64.b64encode(zlib.compress(raw,9)).decode()}


class BoundedObjects(dict):
    def __init__(self): super().__init__();self.total=0
    def setdefault(self,key,value):
        need(len(value)<=32*1024**2,'OBJECT_FILE_LIMIT')
        if key not in self:
            need(self.total+len(value)<=128*1024**2,'OBJECT_AGGREGATE_LIMIT')
            self.total+=len(value)
        return super().setdefault(key,value)


def identity(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
            info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def read_regular(path,maximum):
    before=os.lstat(path)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
         and before.st_size<=maximum,'ORDINARY_BOUNDED_FILE_REQUIRED')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd))==identity(before),'FILE_OPEN_CHANGED')
        raw=b''
        while len(raw)<=maximum:
            part=os.read(fd,min(1024**2,maximum+1-len(raw)))
            if not part: break
            raw+=part
        need(len(raw)==before.st_size and identity(os.fstat(fd))==identity(before)
             and identity(os.lstat(path))==identity(before),'FILE_CAPTURE_CHANGED')
        return raw
    finally: os.close(fd)


def root_ancestry(path):
    path=Path(path);need(path.is_absolute(),'ABSOLUTE_PATH_REQUIRED')
    for part in reversed((path,*path.parents)):
        info=part.lstat()
        need(info.st_uid==info.st_gid==0 and not info.st_mode&0o022
             and not stat.S_ISLNK(info.st_mode),'TRUSTED_ROOT_ANCESTRY_REQUIRED')


def load_utility():
    global _UTILITY
    if _UTILITY is None:
        path=Path(__file__).with_name('host_utility.py')
        raw=read_regular(path,65536);need(sha(raw)==UTILITY_SHA256,'UTILITY_PIN_DIFFERS')
        module=types.ModuleType('selected_owned_child_utility');module.__file__=str(path)
        exec(compile(raw,str(path),'exec'),module.__dict__)
        _UTILITY=module
    return _UTILITY


def enable_subreaper():
    u=load_utility();lib=u.ctypes.CDLL(None,use_errno=True);actual=u.ctypes.c_int()
    need(lib.prctl(36,1,0,0,0)==0
         and lib.prctl(37,u.ctypes.byref(actual),0,0,0)==0
         and actual.value==1,'SUBREAPER_REFUSED')


def command(argv, *, cwd='/', seconds=60, maximum=32768):
    # This is the sole child-owning adapter. Reuse the exact bank03 capture and
    # terminal-first pidfd/ECHILD cleanup; never call its context or probe bank.
    need(cwd=='/' and type(maximum) is int and maximum>0,'COMMAND_SELECTION')
    u=load_utility();records=[];began=time.monotonic();error=None;stdout=stderr=b'';rc=None
    previous=os.getcwd();deadline=_COMMAND_DEADLINE or began+seconds+1
    try:
        os.chdir(cwd)
        try: rc,stdout,stderr=u.capture('input-capture',argv,records,deadline,seconds=seconds)
        except BaseException as exc:
            error=type(exc).__name__
            captured=getattr(exc,'captured',{})
            stdout=captured.get('stdout',b'');stderr=captured.get('stderr',b'')
            rc=captured.get('returncode')
    finally: os.chdir(previous)
    record=records[-1] if records else {}
    rc=record.get('returncode',rc)
    overflow=record.get('output_bound_exceeded',False) or len(stdout)>maximum or len(stderr)>maximum
    cleanup=record.get('cleanup',{})
    row={'exit_code':rc,'elapsed_seconds':time.monotonic()-began,
         'timed_out':record.get('timeout',False),'overflow':overflow,
         'primary_reaped':record.get('process_started',False) and rc is not None,
         'all_owned_children_reaped':cleanup.get('echild',False),
         'stream_bytes':{'stdout':record.get('stdout_bytes',len(stdout)),
                         'stderr':record.get('stderr_bytes',len(stderr))},
         'stream_sha256':{'stdout':record.get('stdout_sha256',sha(stdout)),
                          'stderr':record.get('stderr_sha256',sha(stderr))},
         'exception_type':error,'capture':record,'utility_sha256':UTILITY_SHA256}
    row['complete']=(error is None and not overflow and not row['timed_out']
        and row['primary_reaped'] and row['all_owned_children_reaped']
        and record.get('streams_complete',False) and record.get('internal_failure') is None)
    return row,stdout[:maximum],stderr[:maximum]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('WHEEL_REDIRECT_REFUSED')


def fetch_wheel(spec):
    opener=urllib.request.build_opener(NoRedirect())
    with opener.open(spec['url'],timeout=30) as response:
        need(response.status==200 and response.geturl()==spec['url'],'WHEEL_HTTP_REFUSED')
        raw=response.read(spec['bytes']+1)
    return selected_wheel(raw,spec)


def allocate_provider(spec,commands):
    root=Path(spec['new_provider_root']);root_ancestry(root.parent)
    need(not root.exists() and not root.is_symlink(),'PROVIDER_ALREADY_EXISTS')
    root.mkdir(mode=0o755,exist_ok=False)
    row,_,_=command(['/usr/bin/python3.12','-I','-S','-B','-m','venv','--without-pip','--copies',str(root)],seconds=60)
    commands.append(dict(operation='VENV_WITHOUT_PIP',**row));need(row['complete'] and row['exit_code']==0,'VENV_CREATION_REFUSED')
    files=fetch_wheel(spec['wheel']);site=root/'lib/python3.12/site-packages'
    root_ancestry(site)
    need(list(site.iterdir())==[],'FRESH_SITE_NOT_EMPTY')
    for name in ('zopfli','zopfli-0.2.3.post1.dist-info'): (site/name).mkdir(mode=0o755,exist_ok=False)
    record='zopfli-0.2.3.post1.dist-info/RECORD'
    files['zopfli-0.2.3.post1.dist-info/INSTALLER']=b'implementaudit-r5-hosted-fixed-wheel-v1\n'
    files['zopfli-0.2.3.post1.dist-info/REQUESTED']=b''
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    for name in sorted(files):
        raw=files[name]
        writer.writerow((name,'','') if name==record else
            (name,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('='),str(len(raw))))
    files[record]=stream.getvalue().encode()
    selected_modes={row['name']:row['mode'] for row in spec['wheel']['members']}
    for name,raw in sorted(files.items()):
        # The downloaded wheel's RECORD has group-write permissions. New
        # installed data uses the explicit ordinary 0644 policy instead.
        mode=0o755 if selected_modes.get(name)==0o755 else 0o644
        fd=os.open(site/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
        with os.fdopen(fd,'wb') as out: out.write(raw)
        need(read_regular(site/name,len(raw))==raw,'PROVIDER_WRITE_READBACK')
    return root


def compact(row):
    # Complete maintained selector. Deduplication is lossless and performed only
    # when building the compressed public catalogs below.
    return dict(row)


def pack_catalog(value):
    tables={'aliases':[],'ancestors':[]};indexes={key:{} for key in tables}
    def walk(item):
        if isinstance(item,list): return [walk(x) for x in item]
        if not isinstance(item,dict): return item
        result={}
        for key,val in item.items():
            if key in tables and isinstance(item.get('kind'),str) and item['kind'] in ('FILE','DIRECTORY','MISSING'):
                need(isinstance(val,dict),'CUSTODY_TABLE_SHAPE')
                references=[]
                for path,observation in sorted(val.items()):
                    atom={'path':path,'observation':observation};digest=sha(encoded(atom))
                    index=indexes[key].get(digest)
                    if index is None:
                        index=len(tables[key]);indexes[key][digest]=index;tables[key].append(atom)
                    else: need(tables[key][index]==atom,'CUSTODY_DIGEST_COLLISION')
                    references.append(index)
                result[key+'_refs']=references
            else: result[key]=walk(val)
        return result
    packed=walk(value)
    return {'schema':'dg16.c5-lossless-catalog.v1','value':packed,'custody_tables':tables}


def close_catalog(B,runtime_files,provider_files,runtime_dirs,provider_dirs,namespaces):
    for name,opening in {**runtime_files,**provider_files}.items():
        need(B.capture_selector(name,{})==opening,'SELECTOR_CHANGED')
    for name,opening in {**runtime_dirs,**provider_dirs}.items():
        need(list(identity(os.lstat(name)))==opening['identity']
             and sorted(os.listdir(name))==opening['names'],'NAMESPACE_CHANGED')
    for name,opening in namespaces.items():
        need(B._namespace(name,{})==opening,'STARTUP_OR_TEMPLATE_NAMESPACE_CHANGED')


def runtime_catalogs(files,directories,namespaces):
    # Four fixed transport files retain the prior aggregate 2MiB decoded bound
    # and every unchanged public byte limit. No path or custody field is dropped.
    buckets=[{'files':{},'directories':{},'namespaces':{}} for _ in RUNTIME_NAMES]
    weights=[0]*len(buckets)
    entries=[(kind,path,row) for kind,rows in (('files',files),('directories',directories),
        ('namespaces',namespaces)) for path,row in sorted(rows.items())]
    for kind,path,row in sorted(entries,key=lambda e:(-len(encoded(e[2])),e[0],e[1])):
        index=min(range(len(weights)),key=lambda i:(weights[i],i))
        buckets[index][kind][path]=row;weights[index]+=len(encoded(row))+len(path.encode())
    result=[compressed_catalog(pack_catalog(value)) for value in buckets]
    need(sum(row['decoded_bytes'] for row in result)<=2*1024**2,'CATALOG_AGGREGATE_DECODED_LIMIT')
    return dict(zip(RUNTIME_NAMES,result))


def catalog_tree(root,B,objects,bounds):
    pending=[(Path(root),0)];files={};directories={};count=0
    while pending:
        path,depth=pending.pop();need(depth<=bounds['depth'],'CATALOG_DEPTH')
        before=path.lstat();need(stat.S_ISDIR(before.st_mode),'CATALOG_DIRECTORY')
        B._ancestors(path);names=sorted(os.listdir(path));count+=len(names)
        need(count<=bounds['entries'],'CATALOG_ENTRIES')
        directories[str(path)]={'identity':list(identity(before)),'names':names}
        for name in names:
            B.P.safe_name(name);child=path/name;info=child.lstat()
            if stat.S_ISDIR(info.st_mode): pending.append((child,depth+1))
            elif stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
                files[str(child)]=B.capture_selector(child,objects,limit=bounds['file_bytes'])
            else: raise ValueError('CATALOG_MEMBER_TYPE')
        need(identity(path.lstat())==identity(before),'CATALOG_DIRECTORY_CHANGED')
    return files,directories


def main(args):
    global _COMMAND_DEADLINE
    started=time.monotonic();out=Path(args.output);need(not out.exists(),'OUTPUT_ALREADY_EXISTS')
    _COMMAND_DEADLINE=started+530
    out.mkdir(mode=0o700,parents=False,exist_ok=False);private=out/'private';private.mkdir(mode=0o700)
    documents={name:{'status':'NOT_CAPTURED','authority':'NONE'} for name in PUBLIC_NAMES if name!='ARTIFACT_MANIFEST.json'}
    spec=json.loads(read_regular(Path(__file__).with_name('INPUT_SPEC.json'),65536))
    need(spec['prospective_branch']==BRANCH and spec['source_commit']==SOURCE_COMMIT
         and spec['source_tree']==SOURCE_TREE and spec['host_utility_sha256']==UTILITY_SHA256
         and set(spec['public_allowlist'])==PUBLIC_NAMES,'INPUT_SELECTION_DIFFERS')
    phase='HOST_BINDING';commands=[];complete=False;error=None;objects=BoundedObjects()
    try:
        need(sys.platform=='linux' and sys.version_info[:2]==(3,12) and sys.implementation.name=='cpython','RUNTIME_PROFILE')
        need((os.getuid(),os.geteuid(),os.getgid(),os.getegid())==(0,0,0,0),'ACTUAL_ROOT_REQUIRED')
        def terminated(_signum,_frame): raise ValueError('TERMINATION_REQUESTED')
        signal.signal(signal.SIGTERM,terminated)
        enable_subreaper()
        need(args.repository==REPOSITORY and args.branch==BRANCH and args.attempt=='1'
             and re.fullmatch('[0-9]{1,20}',args.run_id) and re.fullmatch('[0-9a-f]{40}',args.workflow_commit),'WORKFLOW_BINDING')
        need(re.fullmatch('[A-Za-z0-9._-]{1,64}',args.image_os) and re.fullmatch('[A-Za-z0-9._-]{1,64}',args.image_version),'IMAGE_METADATA_SHAPE')
        root_ancestry(Path('/usr/bin/python3.12'));root_ancestry(Path('/usr/bin/git'))
        python_before=read_regular('/usr/bin/python3.12',32*1024**2)
        source=Path(args.source);need(source.is_absolute() and source.resolve()==source,'SOURCE_PHYSICAL_PATH')
        for query,expected in (('HEAD',SOURCE_COMMIT),('HEAD^{tree}',SOURCE_TREE)):
            row,raw,_=command(['/usr/bin/git','-c','safe.directory='+str(source),'-C',str(source),'rev-parse',query])
            commands.append(dict(operation='SOURCE_COMMIT' if query=='HEAD' else 'SOURCE_TREE',**row))
            need(row['complete'] and row['exit_code']==0 and raw.decode().strip()==expected,'SOURCE_GIT_IDENTITY')
        source_bytes={}
        for row in spec['source_members']:
            raw=read_regular(source/row['member'],row['bytes']);need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'SOURCE_MEMBER_DIFFER')
            source_bytes[row['member']]=raw
        documents['SOURCE.json']={'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'members':spec['source_members'],
            'input_spec_sha256':sha(read_regular(Path(__file__).with_name('INPUT_SPEC.json'),65536)),'authority':'NONE'}
        # This kernel pseudo-file intentionally has st_size zero. It is an
        # observed boot marker, not a physical regular-file custody witness.
        with open('/proc/sys/kernel/random/boot_id','rb') as stream: boot=stream.read(129).strip()
        need(re.fullmatch(b'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',boot),'KERNEL_BOOT_MARKER')
        documents['HOST.json']={'uid':os.getuid(),'euid':os.geteuid(),'gid':os.getgid(),'egid':os.getegid(),
            'python_version':list(sys.version_info[:3]),'python_sha256':sha(python_before),'python_bytes':len(python_before),
            'uname':list(os.uname()),'boot_id_sha256':sha(boot),'image_os':args.image_os,'image_version':args.image_version,
            'workflow_commit':args.workflow_commit,'run_id':args.run_id,'attempt':args.attempt,'authority':'NONE'}
        setup=types.ModuleType('selected_fixed_setup_owner');setup.__file__=str(source/'scripts/qualify-work-graph-c5-setup.py')
        exec(compile(source_bytes['scripts/qualify-work-graph-c5-setup.py'],setup.__file__,'exec'),setup.__dict__)
        owner=setup.hosted_current_owner(source);B=owner.B
        phase='PROVIDER_ALLOCATION';provider=allocate_provider(spec,commands)
        need(read_regular('/usr/bin/python3.12',32*1024**2)==python_before,'PYTHON_CHANGED_DURING_PREPARATION')
        phase='ABSENT_LAUNCHER_PREPARATION'
        launcher=B.capture_selector('/usr/bin/bwrap',objects)
        if launcher['kind']=='MISSING':
            row,_,_=command(['/usr/bin/python3.12','-I','-S','-B',setup.__file__,'--provision-hosted-launcher'],seconds=60)
            commands.append(dict(operation='ABSENT_LAUNCHER_PROVISION',**row))
            need(row['complete'] and row['exit_code']==0,'LAUNCHER_PROVISION_REFUSED')
            # The later acquisition and closing readback include the new path.
            need(B.capture_selector('/usr/bin/bwrap',objects)['kind']=='FILE','LAUNCHER_PROVISION_NO_FILE')
        phase='RUNTIME_CAPTURE'
        runtime_files,runtime_dirs=catalog_tree('/usr/lib/python3.12',B,objects,spec['runtime_bounds'])
        names={'/usr/bin/'+name for name in spec['selected_system_tools']}
        names.update('/lib/x86_64-linux-gnu/'+name for name in spec['selected_libraries'])
        names.update(('/lib64/ld-linux-x86-64.so.2','/bin/bash','/bin/sh','/usr/bin/bwrap'))
        for key in ('unchanged_old_runtime_pins','unchanged_old_provider_startup_pins','unchanged_old_provider_native_pins','unchanged_old_git_files'):
            names.update(spec[key])
        names.update(B._ABSENT);names.update(B._NSCD);names.update(B._PYTHON_ALIASES)
        names.update(('/etc/ld.so.preload','/etc/passwd','/etc/group','/etc/nsswitch.conf'))
        for name in sorted(names): runtime_files[name]=B.capture_selector(name,objects,limit=spec['runtime_bounds']['file_bytes'])
        provider_files,provider_dirs=catalog_tree(provider,B,objects,spec['runtime_bounds'])
        need(len(runtime_files)+len(runtime_dirs)+len(provider_files)+len(provider_dirs)<=spec['runtime_bounds']['entries'],'TOTAL_ENTRY_LIMIT')
        mounted=sum(row.get('bytes',0) for row in runtime_files.values())+sum(row.get('bytes',0) for row in provider_files.values())
        need(mounted<=spec['runtime_bounds']['mounted_bytes'],'MOUNTED_BYTE_LIMIT')
        namespace_names=sorted(set(B._SITE_ROOTS)|set(spec['unchanged_old_git_directories']))
        namespaces={name:B._namespace(name,objects) for name in namespace_names}
        phase='CLOSING_READBACK'
        close_catalog(B,runtime_files,provider_files,runtime_dirs,provider_dirs,namespaces)
        for name,raw in source_bytes.items(): need(read_regular(source/name,len(raw))==raw,'SOURCE_CHANGED')
        owner.CHECK()
        projected={name:compact(row) for name,row in sorted(runtime_files.items())}
        nss={}
        for name in ('/etc/passwd','/etc/group'):
            row=runtime_files[name];data=objects[row['sha256']]
            roots=[line.split(':') for line in data.decode('utf-8','strict').splitlines() if line.startswith('root:')]
            nss[name]={'sha256':row['sha256'],'bytes':row['bytes'],'root_entry_count':len(roots),
                'root_id_zero':len(roots)==1 and len(roots[0])>=4 and roots[0][2]=='0',
                'root_group_zero':name=='/etc/group' or (len(roots)==1 and roots[0][3]=='0')}
        nssraw=objects[runtime_files['/etc/nsswitch.conf']['sha256']].decode('utf-8','strict')
        for category in ('passwd','group'):
            rows=[line.split(':',1)[1].split('#',1)[0].strip().split() for line in nssraw.splitlines() if line.startswith(category+':')]
            nss[category+'_files_only']=rows==[['files']]
        for name,catalog in runtime_catalogs(projected,runtime_dirs,namespaces).items():
            documents[name]={'catalog':catalog,'authority':'NONE','scope':'ACTUAL_METADATA_NOT_EXECUTION_PROFILE'}
        documents['RUNTIME_A.json'].update(nss_predicates=nss,unique_bytes=objects.total,mounted_bytes=mounted)
        documents['PROVIDER.json']={'root':str(provider),'catalog':compressed_catalog(pack_catalog({
            'files':{name:compact(row) for name,row in sorted(provider_files.items())},'directories':provider_dirs})),
            'wheel_sha256':spec['wheel']['sha256'],'provider_imported':False,'authority':'NONE'}
        differences=[]
        for group in ('unchanged_old_runtime_pins','unchanged_old_provider_startup_pins','unchanged_old_provider_native_pins','unchanged_old_git_files'):
            for name,pin in spec[group].items():
                row=runtime_files[name];keys=[key for key,val in pin.items() if row.get(key)!=val]
                if keys: differences.append({'group':group,'path':name,'different_fields':keys})
        for name,expected in spec['unchanged_old_git_directories'].items():
            row=namespaces[name]
            if row['observation']['kind']!='DIRECTORY' or sorted(row['names'])!=expected:
                differences.append({'group':'unchanged_old_git_directories','path':name,'different_fields':['population']})
        documents['DIFFERENCES.json']={'old_profile_unchanged':True,'differences':differences,
            'profile_qualified':False,'authority':'NONE','next':'DERIVE_AND_INDEPENDENTLY_QUALIFY_EXACT_NEW_PROFILE'}
        phase='C5_SETUP_ONLY';launcher=runtime_files['/usr/bin/bwrap'];old=spec['unchanged_old_launcher']
        if all(launcher.get(key)==value for key,value in old.items()):
            row,stdout,stderr=command(['/usr/bin/python3.12','-I','-S','-B',setup.__file__],seconds=15,maximum=65536)
            commands.append(dict(operation='EXISTING_C5_SETUP_ONLY',**row))
            need(row['complete'],'SETUP_CAPTURE_INCOMPLETE')
            result=json.loads(stdout)
            fields=('classification','complete_custody','exit_code','elapsed_seconds','wait4_reaped','rusage',
                    'owned_group_absent','descriptor_restoration','timed_out','overflow','pidfd_kill','eof','stream_bytes')
            documents['SETUP.json']={'status':'OBSERVED','operation':row,'result':{key:result[key] for key in fields},
                'actual_launcher':compact(launcher),'source_stdout_sha256':sha(stdout),'source_stderr_sha256':sha(stderr),'authority':'NONE'}
        else:
            documents['SETUP.json']={'status':'NOT_RUN_LAUNCHER_PIN_DIFFERS','actual_launcher':compact(launcher),
                'expected_launcher':old,'authority':'NONE'}
        phase='FINAL_CLOSING_READBACK'
        close_catalog(B,runtime_files,provider_files,runtime_dirs,provider_dirs,namespaces)
        for name,raw in source_bytes.items(): need(read_regular(source/name,len(raw))==raw,'SOURCE_CHANGED')
        owner.CHECK()
        complete=True;phase='CAPTURE_COMPLETE'
    except BaseException as exc:
        error={'type':type(exc).__name__,'code':str(exc) if isinstance(exc,ValueError) and re.fullmatch('[A-Z0-9_]{1,80}',str(exc)) else 'CAPTURE_REFUSED',
               'phase':phase,'errno':getattr(exc,'errno',None)}
    documents['RESULT.json']={'schema':'dg16.c5-input-capture.v1','status':'CAPTURED_NOT_QUALIFIED' if complete else 'FAILED_RETAINED',
        'phase':phase,'failure':error,'elapsed_seconds':time.monotonic()-started,'commands':commands,
        'source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,'run_id':args.run_id,'workflow_commit':args.workflow_commit,
        'automatic_retry':False,'original_c5_started':False,'original_acceptance':False,'authority':'NONE'}
    documents['ARTIFACT_MANIFEST.json']={'schema':'dg16.c5-input-capture-manifest.v1','files':[
        {'name':name,'bytes':len(encoded(body)),'sha256':sha(encoded(body))} for name,body in sorted(documents.items())]}
    rows=public_envelopes(documents,spec['public_limits'])
    public=out/'public';public.mkdir(mode=0o755)
    for row in rows:
        target=public/row['name'];target.write_bytes(row['utf8_json'].encode());target.chmod(0o644)
    out.chmod(0o755)
    # Validation completes before the first public log line or upload eligibility.
    for row in rows: print('DG16_C5_INPUT_JSON '+encoded(row).decode().strip(),flush=True)
    (out/'PUBLIC_ELIGIBLE').write_text('true\n')
    (out/'PUBLIC_ELIGIBLE').chmod(0o644)
    return 0 if complete else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('source','output','repository','branch','attempt','run-id','workflow-commit','image-os','image-version'):
        parser.add_argument('--'+name,required=True)
    try: result=main(parser.parse_args())
    except BaseException:
        print('DG16_C5_INPUT_REFUSAL {"code":"PUBLICATION_UNAVAILABLE","authority":"NONE","automatic_retry":false}',flush=True)
        raise SystemExit(1)
    raise SystemExit(result)
