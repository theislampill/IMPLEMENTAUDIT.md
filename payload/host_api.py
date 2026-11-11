import errno,hashlib,json,os,re,signal,stat,sys
from pathlib import Path
from types import SimpleNamespace
def utility_api():
    def sha(raw):
        return hashlib.sha256(raw).hexdigest()
    class Refusal(Exception):
        pass
    def require(condition, code):
        if not condition:
            raise Refusal(code)
    def checked_file(path, maximum=64*1024*1024, single_link=True):
        path = Path(path)
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and (not single_link or before.st_nlink == 1)
                and before.st_size <= maximum, 'FILE_SHAPE_REFUSED')
        with path.open('rb') as stream:
            raw = stream.read(maximum+1)
        after = path.lstat()
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and len(raw)<=maximum, 'FILE_CHANGED')
        return raw
    def trusted(name):
        requested = Path('/usr/bin')/name
        try:
            path = requested.resolve(strict=True)
            require(path.is_file() and os.access(path,os.X_OK), 'TOOL_NOT_EXECUTABLE')
            for item in (path,*path.parents):
                info = item.lstat()
                require(info.st_uid==0 and not info.st_mode & 0o022, 'TOOL_CUSTODY_REFUSED')
            info = path.stat()
            require(not info.st_mode & 0o6000, 'PRIVILEGED_TOOL_REFUSED')
            try: cap = os.getxattr(path,'security.capability')
            except OSError as exc:
                require(exc.errno in (errno.ENODATA,errno.ENOTSUP), 'TOOL_CAPABILITY_UNKNOWN')
                cap = b''
            require(not cap, 'PRIVILEGED_TOOL_REFUSED')
            raw = checked_file(path, single_link=False)
            return str(path), {'available':True,'requested':'/usr/bin/'+name,'canonical':str(path),
                               'bytes':len(raw),'sha256':sha(raw),'root_owned_nonwritable_chain':True,
                               'setid_or_file_capabilities':False}
        except (OSError,Refusal) as exc:
            code=str(exc) if isinstance(exc,Refusal) else 'TOOL_OS_REFUSAL'
            return None, {'available':False,'requested':'/usr/bin/'+name,'code':code,
                          'errno':getattr(exc,'errno',None)}
    def token(value, maximum=80):
        require(type(value) is str and re.fullmatch(r'[A-Za-z0-9_.:+~/=-]{1,'+str(maximum)+'}', value), 'UNSAFE_IDENTITY_TOKEN')
        return value
    return SimpleNamespace(checked_file=checked_file, trusted=trusted, token=token)

def evidence_api():
    class Refusal(ValueError):
        pass
    def need(value, code):
        if not value:
            raise Refusal(code)
    return SimpleNamespace(need=need)

def profile_api(E):
    OS = {'ID': 'ubuntu', 'VERSION_ID': '26.04'}
    VERSION = [3, 14, 4]
    TOOLS = ('bash', 'bwrap', 'git', 'python3')
    PYTHON = '/usr/bin/python3.14'
    HOST_FIELDS = ('os', 'architecture', 'kernel', 'python_version', 'tools')
    MATCH_FIELDS = ('os', 'architecture', 'kernel', 'python_version',
                    'tools.bash', 'tools.bwrap', 'tools.git', 'tools.python3')
    need = E.need
    def credentials():
        uid, euid, suid = os.getresuid()
        gid, egid, sgid = os.getresgid()
        return dict(uid=uid, euid=euid, suid=suid, gid=gid, egid=egid, sgid=sgid)
    def validate_credentials(value):
        need(type(value) is dict and set(value) == {'uid', 'euid', 'suid', 'gid', 'egid', 'sgid'}
             and all(type(v) is int and 0 <= v < 2**32 for v in value.values())
             and value['uid'] == value['euid'] == value['suid'] != 0
             and value['gid'] == value['egid'] == value['sgid'], 'G2_NATIVE_NONROOT_CREDENTIALS_REQUIRED')
        return value
    def validate_host(host):
        keys = {'os', 'architecture', 'kernel', 'uid', 'python_version', 'image_os',
                'image_version', 'tools', 'boot_identity_sha256', 'credentials'}
        need(type(host) is dict and set(host) == keys and host['os'] == OS
             and host['architecture'] == 'x86_64' and host['python_version'] == VERSION,
             'G2_NATIVE_ORDINARY_HOST_PROFILE')
        creds = validate_credentials(host['credentials'])
        need(type(host['uid']) is int and host['uid'] == creds['euid'], 'G2_NATIVE_CALLER_IDENTITY')
        for name in ('kernel', 'image_os', 'image_version'):
            need(type(host[name]) is str and re.fullmatch(r'[A-Za-z0-9_.:+~/=-]{1,80}', host[name]),
                 'G2_NATIVE_HOST_FACT_SHAPE')
        need(type(host['boot_identity_sha256']) is str and re.fullmatch('[0-9a-f]{64}', host['boot_identity_sha256']),
             'G2_NATIVE_BOOT_IDENTITY')
        need(type(host['tools']) is dict and set(host['tools']) == set(TOOLS), 'G2_NATIVE_TOOL_POPULATION')
        for name in TOOLS:
            row = host['tools'][name]
            need(type(row) is dict and set(row) == {'available', 'requested', 'canonical', 'bytes', 'sha256',
                 'root_owned_nonwritable_chain', 'setid_or_file_capabilities'} and row['available'] is True
                 and row['requested'] == '/usr/bin/' + name and type(row['canonical']) is str
                 and row['canonical'].startswith('/usr/') and Path(row['canonical']).is_absolute()
                 and '..' not in Path(row['canonical']).parts
                 and type(row['bytes']) is int and 0 < row['bytes'] <= 64 * 1024**2
                 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256'])
                 and row['root_owned_nonwritable_chain'] is True and row['setid_or_file_capabilities'] is False,
                 'G2_NATIVE_TRUSTED_TOOL_FACT_REQUIRED')
        need(host['tools']['python3']['canonical'] == PYTHON, 'G2_NATIVE_SYSTEM_INTERPRETER_REQUIRED')
        return {key: host[key] for key in HOST_FIELDS}
    def compare_historical(host, historical):
        observed = validate_host(host)
        need(type(historical) is dict and set(historical) == set(HOST_FIELDS), 'G2_NATIVE_HISTORICAL_PROFILE_SHAPE')
        matches = {key: observed[key] == historical[key] for key in HOST_FIELDS if key != 'tools'}
        matches.update({'tools.' + name: observed['tools'][name] == historical['tools'][name] for name in TOOLS})
        need(set(matches) == set(MATCH_FIELDS), 'G2_NATIVE_HOST_MATCH_POPULATION')
        return matches
    return SimpleNamespace(credentials=credentials, validate_host=validate_host, compare_historical=compare_historical)

def inventory_api(profile):
    def load_native(_utility):
        return SimpleNamespace(P=profile)
    class Refusal(Exception): pass
    class Deadline(Exception): pass
    def need(value, code):
        if not value: raise Refusal(code)
    def digest(raw): return hashlib.sha256(raw).hexdigest()
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
    return SimpleNamespace(inventory=inventory, Deadline=Deadline)

HISTORICAL_PROFILE = {'architecture': 'x86_64', 'kernel': '7.0.0-1019-azure', 'os': {'ID': 'ubuntu', 'VERSION_ID': '26.04'}, 'python_version': [3, 14, 4], 'tools': {'bash': {'available': True, 'bytes': 1540520, 'canonical': '/usr/bin/bash', 'requested': '/usr/bin/bash', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': '450c68376d14e5040d36cce58605c35b2211d244f3079297440dc9d602ee4994'}, 'bwrap': {'available': True, 'bytes': 80424, 'canonical': '/usr/bin/bwrap', 'requested': '/usr/bin/bwrap', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': 'a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361'}, 'git': {'available': True, 'bytes': 4771424, 'canonical': '/usr/bin/git', 'requested': '/usr/bin/git', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': '63acee09d55a44c7f4480f3a2c3fb79e7063deaf61df3f920b113ed38c0541e6'}, 'python3': {'available': True, 'bytes': 7468968, 'canonical': '/usr/bin/python3.14', 'requested': '/usr/bin/python3', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': 'be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd'}}}
