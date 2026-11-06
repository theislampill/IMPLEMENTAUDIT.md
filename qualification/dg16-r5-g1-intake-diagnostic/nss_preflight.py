"""Exact existing read-only NSS admission closure."""
import hashlib,json,math,os,stat,time,types
from pathlib import Path
MAX_PRIVATE_JSON=4*1024**2
SOURCE_TREE='ee316c27250ec422d35a1ea965182ebddf7a5da0'
LOADER_SHA256='43df4216ec94e5abac4136e31ee1a6b72289a6f7ec15452cc77d892dcfc3c76f'
PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1'
REVISION='R5_HOSTED_UBUNTU24_SINGLE_COPY_SOURCE_20261105_V1'
NSS_ENUMS=frozenset(('files','systemd','compat','db','nis','nisplus','sss','ldap','winbind',
    'resolve','dns','mdns','mdns4','mdns6','mdns_minimal','mdns4_minimal','mdns6_minimal',
    'myhostname','mymachines'))

def need(value, code):
    if not value: raise ValueError(code)

def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def sha(raw): return hashlib.sha256(raw).hexdigest()

def stamp(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
        info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)

def read_regular(path, maximum):
    path=Path(path);before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,
         'PRIVATE_INPUT_NOT_ORDINARY_BOUNDED_FILE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'PRIVATE_INPUT_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream: raw=stream.read(maximum+1)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
             and stamp(path.lstat())==stamp(before),'PRIVATE_INPUT_CHANGED')
        return raw
    finally: os.close(fd)

def write_once(path, raw, maximum=MAX_PRIVATE_JSON):
    need(type(raw) is bytes and len(raw)<=maximum,'PRIVATE_OUTPUT_BOUND')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as stream:
            stream.write(raw);stream.flush();os.fsync(fd)
        os.fchmod(fd,0o400)
    finally: os.close(fd)
    need(read_regular(path,maximum)==raw,'PRIVATE_OUTPUT_READBACK')
    return dict(bytes=len(raw),sha256=sha(raw))

def nss_token_observation(config):
    """Bounded data projection, not NSS admission and not a config rewriter."""
    need(type(config) is bytes and 0<len(config)<=65536 and b'\0' not in config,'NSS_INPUT_SHAPE')
    text=config.decode('ascii','strict')
    lines=[line.split('#',1)[0].strip() for line in text.splitlines()]
    result=dict(schema='dg16.c5-nss-token-observation.v1',raw_bytes=len(config),raw_sha256=sha(config),
        scope='ACTUAL_PARSED_DIAGNOSTIC_ONLY_NO_SERVICE_ADMISSION',categories={})
    for category in ('passwd','group'):
        selected=[line for line in lines if line.partition(':')[0].strip()==category]
        canonical=encode(selected)
        row=dict(row_count=len(selected),parsed_rows_bytes=len(canonical),parsed_rows_sha256=sha(canonical),
            tokens=[],token_count=0,classification='AMBIGUOUS_OR_MISSING',matches_files_only_syntax=False)
        if len(selected)==1:
            tokens=selected[0].partition(':')[2].split()
            row.update(token_count=len(tokens),matches_files_only_syntax=tokens==['files'])
            if len(tokens)>16 or any(len(token)>128 for token in tokens):
                row['classification']='TOKEN_BOUND_REFUSED'
            else:
                for token in tokens:
                    if token in NSS_ENUMS: row['tokens'].append(dict(kind='KNOWN_SERVICE',value=token))
                    else: row['tokens'].append(dict(kind='WITHHELD_TOKEN',bytes=len(token),sha256=sha(token.encode('ascii'))))
                row['classification']=('FILES_ONLY' if tokens==['files'] else
                    'ACTION_SYNTAX_UNQUALIFIED' if any('[' in token or ']' in token for token in tokens) else
                    'FILES_FIRST_OTHER_UNQUALIFIED' if tokens and tokens[0]=='files' else 'OTHER_UNQUALIFIED')
        result['categories'][category]=row
    need(len(encode(result))<=8192,'NSS_DIAGNOSTIC_BOUND')
    return result

def load_selected(source):
    path=source/'scripts/load-work-graph-c5-executor.py'
    raw=read_regular(path,1024**2)
    need(sha(raw)==LOADER_SHA256,'LOADER_PIN_DIFFERS')
    module=types.ModuleType('r5_hosted_c5_selected_loader');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    need(module.R5_HOSTED_PROFILE==PROFILE and module.R5_HOSTED_SOURCE_REVISION==REVISION,'PROFILE_SELECTION_DIFFERS')
    engine=module._Engine(PROFILE,source_revision=REVISION).load()
    need(read_regular(path,1024**2)==raw,'LOADER_CHANGED_DURING_LOAD')
    engine.CHECK()
    return engine
