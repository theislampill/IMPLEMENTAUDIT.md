#!/usr/bin/env python3
"""DG17 separately admitted canonical Codex routing parent. Scripted NONVERDICT; no substantive assessment or awards."""

import argparse,ctypes,errno,hashlib,io,json,math,os,platform,re,shlex,stat,sys,tarfile,time,tomllib,types,urllib.request,zipfile
from pathlib import Path

REPO = 'theislampill/IMPLEMENTAUDIT.md'

BRANCH = 'pro/dg17-isolated-episode-01-20261106'

SOURCE = '0d57929be5bd15682b4e9da2c0209d5dff307843'

TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'

PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'

MANIFEST_SHA = 'ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4'

UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'

PINS_SHA = '6dce1cb63b1f9a06d54c09cfc0058dd1fd24dea339f51ec934d15b6e594a543f'

CLAIM = 'skills/implementaudit/scripts/claim-run.sh'

AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'

DOCS = ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')

STEPS = ('prepare', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'runtime', 'content', 'receive')

PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'ROUTING.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')

PURPOSE = 'Observe one separately admitted canonical8ee Codex native routing episode under frozen0d control. Bind one version admission, one app-server, seven RPCs, three fixed native execs, one fresh V1 audit-assess child, wait and close, eight loopback scripted Responses requests, the complete20-file historical-composition-with-stage-addendum data boundary and exact root owner selection. Preserve the first NONVERDICT and pending substantive review; no inference, original award or closure.'

NEXT = 'Admit unchanged system-only helpers and the private loopback/filesystem view; deliver governor prefix and complete native governor/resolver/selected-child returns; route one fresh actual V1 child with the selected typed Skill; receive native identity, first return and close plus exact source/store/currentness, package/cache/config, review inputs and full custody. The bwrap TOOL_OS_REFUSAL errno2 prerequisite is unresolved by this packet; no fallback/acquisition is added.'

ARCHIVE_URL = 'https://github.com/openai/codex/releases/download/rust-v0.167.0-alpha.4/codex-x86_64-unknown-linux-musl.tar.gz'

ARCHIVE_SHA = 'c4fd6fdeedf0ae78cc4d1d9dde4282c57a4a67c38319e3575b9a1e4d46c9ccc6'

ARCHIVE_BYTES = 123815356

BINARY_SHA = '57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8'

BINARY_BYTES = 324012616

PREDICATE_SCOPE = {
    'direct_source_applicability': ['T06', 'T08', 'Y04', 'BINDING_POSITIVE'],
    'component_only': ['T12'],
    'indirect_inherited_scope_only': ['NESTED/P01'],
    'narrow_receiving_input_only': ['T14'],
    'ceiling': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD',
}

PRIOR_COMPONENT = {'run_id': 42210454718, 'attempt': 1, 'artifact_id': 13497879213, 'artifact_sha256': '9a285ea3756238ac689669782b690a5aa05dfdbbe14a2c285694085ce3b70847', 'predicate_member_sha256': '9028d6711dc1e02b2babf6fc5e4e70974a99a3ed54b547d391ded3f8033af73a', 'source_commit': '0d57929be5bd15682b4e9da2c0209d5dff307843', 'source_tree': 'ee316c27250ec422d35a1ea965182ebddf7a5da0', 'test_path': 'tests/shell_companion_source_custody.py', 'test_source_sha256': '22ffd31ff45e1f439759c45bb5c67bde5e8390b69b54030833476e80aaee7f08', 'independent_receipt_sha256': '9ba49dfeb1ec8e7ac3c4fe122e5c89227340405fa729d48c0c651b8fa12bf07f', 'root_receipt_sha256': 'a63dc54e1812ddf4a57091360d09753fc3b0c9dae90d6cddd4bcc757bc550a64', 'scope': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD'}

LOOPBACK_INITIALIZER_SHA = 'e04d2c081998a08de53cf0f214cd1b9ae531fc5abc1d1bf79206b43c69570433'

CAPSULE_TARGETS = ('/opt', '/usr/local/bin', '/etc/gitconfig')

CAPSULE_SCRIPT = 'set -eu\nset -o noclobber\numask 022\n[ "$EUID" -eq 0 ]\n[ "$#" -eq 32 ]\n[ -d /opt ] && [ ! -L /opt ]\n[ -d /usr/local/bin ] && [ ! -L /usr/local/bin ]\n[ -f /etc/gitconfig ] && [ ! -L /etc/gitconfig ]\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o rw,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n: > /opt/dg17-empty-system-gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o remount,ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n/usr/bin/mount --internal-only --no-mtab -o bind,ro,nodev,nosuid,noexec /opt/dg17-empty-system-gitconfig /etc/gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /usr/local/bin\n/usr/bin/python3 -I -S -B -c \'"""Fixed root-only namespace initializer, embedded literally; never run locally."""\nimport fcntl\nimport os\nimport re\nimport socket\nimport struct\nimport sys\n\ndef need(ok):\n    if not ok:\n        raise RuntimeError(\'"\'"\'LOOPBACK_ADMISSION_REFUSED\'"\'"\')\n\ndef run():\n    need(len(sys.argv) == 2 and os.geteuid() == 0)\n    parent = sys.argv[1]\n    need(re.fullmatch(r\'"\'"\'net:\\[[0-9]+\\]\'"\'"\', parent) is not None)\n    namespace = os.readlink(\'"\'"\'/proc/self/ns/net\'"\'"\')\n    need(re.fullmatch(r\'"\'"\'net:\\[[0-9]+\\]\'"\'"\', namespace) is not None and namespace != parent)\n    with open(\'"\'"\'/proc/net/dev\'"\'"\', \'"\'"\'rb\'"\'"\') as stream:\n        raw = stream.read(8193)\n    need(len(raw) <= 8192)\n    names = [line.split(\'"\'"\':\'"\'"\', 1)[0].strip() for line in raw.decode(\'"\'"\'ascii\'"\'"\').splitlines()[2:] if \'"\'"\':\'"\'"\' in line]\n    need(names == [\'"\'"\'lo\'"\'"\'])\n    request = struct.pack(\'"\'"\'16sH22x\'"\'"\', b\'"\'"\'lo\'"\'"\', 0)\n    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC) as handle:\n        before = fcntl.ioctl(handle.fileno(), 0x8913, request)\n        flags = struct.unpack_from(\'"\'"\'H\'"\'"\', before, 16)[0]\n        need(flags & 0x8 and not flags & ~0x49)\n        # Only the IFF_UP bit of the fixed loopback interface is changed.\n        fcntl.ioctl(handle.fileno(), 0x8914, struct.pack(\'"\'"\'16sH22x\'"\'"\', b\'"\'"\'lo\'"\'"\', flags | 0x1))\n        after = fcntl.ioctl(handle.fileno(), 0x8913, request)\n        observed = struct.unpack_from(\'"\'"\'H\'"\'"\', after, 16)[0]\n        need(observed & 0x9 == 0x9 and not observed & ~0x49)\n    need(os.readlink(\'"\'"\'/proc/self/ns/net\'"\'"\') == namespace)\n    return 0\n\nif __name__ == \'"\'"\'__main__\'"\'"\':\n    try:\n        sys.exit(run())\n    except BaseException as exc:\n        if isinstance(exc, SystemExit):\n            raise\n        sys.stderr.write(\'"\'"\'DG17_LOOPBACK_ADMISSION_REFUSED\\n\'"\'"\')\n        sys.exit(1)\n\' "$7"\nexec /usr/bin/setpriv --reuid "$1" --regid "$2" --clear-groups --no-new-privs /usr/bin/python3 -I -S -B -c "$3" "$1" "$2" "$4" "$5" "$6" "$7" "$8" "${@:9}"\n'

CAPSULE_SCRIPT_SHA = 'e4f116003174fe1400960da43b32594157826760ca31c3781a6b765ade82ed0a'

CAPSULE_CODE = "import fcntl,hashlib,ipaddress,json,os,re,socket,stat,struct,subprocess,sys\nTARGETS=('/opt','/usr/local/bin','/etc/gitconfig')\nCONFIG_SOURCE='/opt/dg17-empty-system-gitconfig'\nEMPTY_SHA='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'\ndef need(ok,code):\n    if not ok: raise RuntimeError(code)\ndef encode(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\\n').encode()\ndef sha(raw):return hashlib.sha256(raw).hexdigest()\ndef parse_mounts(raw):\n    need(type(raw) is bytes and len(raw)<=1048576,'MOUNTINFO_BOUND')\n    lines=raw.decode('ascii').splitlines();need(1<=len(lines)<=4096,'MOUNTINFO_POPULATION')\n    rows={};private=True\n    for line in lines:\n        fields=line.split();need('-' in fields,'MOUNTINFO_SHAPE');split=fields.index('-')\n        need(split>=6 and len(fields)>=split+4,'MOUNTINFO_SHAPE')\n        if any(x.startswith(('shared:','master:','propagate_from:')) for x in fields[6:split]):private=False\n        if fields[4] not in TARGETS:continue\n        path=fields[4];need(path not in rows,'DUPLICATE_TARGET_MOUNT')\n        opts=fields[5].split(',');superopts=fields[split+3].split(',')\n        size=[x[5:] for x in superopts if x.startswith('size=')]\n        need(len(size)==1 and re.fullmatch(r'[0-9]+[kKmMgG]?',size[0]),'TMPFS_SIZE')\n        token=size[0];suffix=token[-1].lower();factor={'k':1024,'m':1048576,'g':1073741824}.get(suffix,1)\n        number=int(token[:-1]) if suffix in 'kmg' else int(token)\n        need(all(re.fullmatch(r'[0-9]{1,12}',fields[i]) for i in (0,1)),'MOUNT_ID')\n        rows[path]={'path':path,'mount_id':int(fields[0]),'parent_mount_id':int(fields[1]),'mount_root':fields[3],\n                    'filesystem':fields[split+1],'mount_source':fields[split+2],\n                    'readonly':'ro' in opts and 'rw' not in opts and 'ro' in superopts and 'rw' not in superopts,\n                    'nodev':'nodev' in opts,'nosuid':'nosuid' in opts,'noexec':'noexec' in opts,\n                    'size_bytes':number*factor,'mount_options_sha256':sha(fields[5].encode()),\n                    'super_options_sha256':sha(fields[split+3].encode())}\n    need(set(rows)==set(TARGETS),'TARGET_MOUNTS_MISSING')\n    return private,len(lines),[rows[path] for path in TARGETS]\ndef file_snapshot(path):\n    before=os.lstat(path)\n    need(os.path.realpath(path)==path and stat.S_ISREG(before.st_mode) and\n         before.st_uid==0 and before.st_gid==0 and stat.S_IMODE(before.st_mode)==0o644 and\n         before.st_nlink==1 and before.st_size==0,'EMPTY_CONFIG_FILE')\n    with open(path,'rb') as stream:raw=stream.read(1)\n    after=os.lstat(path)\n    identity=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)\n    need(identity(before)==identity(after) and raw==b'','EMPTY_CONFIG_FILE_CHANGED')\n    return {'file_uid':before.st_uid,'file_gid':before.st_gid,'mode':stat.S_IMODE(before.st_mode),\n            'regular':True,'symlink':False,'nlink':before.st_nlink,'bytes':len(raw),'sha256':sha(raw),\n            'device':before.st_dev,'inode':before.st_ino}\ndef network_snapshot(parent):\n    need(re.fullmatch(r'net:\\[[0-9]+\\]', parent) is not None, 'PARENT_NETWORK_NAMESPACE')\n    namespace = os.readlink('/proc/self/ns/net')\n    need(re.fullmatch(r'net:\\[[0-9]+\\]', namespace) is not None and namespace != parent,\n         'NETWORK_NAMESPACE_NOT_DISTINCT')\n    def bounded(path):\n        with open(path, 'rb') as stream:\n            raw = stream.read(8193)\n        need(len(raw) <= 8192, 'NETWORK_METADATA_BOUND')\n        return raw.decode('ascii').splitlines()\n    lines = bounded('/proc/net/dev')\n    need(2 <= len(lines) <= 4, 'NETWORK_INTERFACE_POPULATION')\n    names = [line.split(':', 1)[0].strip() for line in lines[2:] if ':' in line]\n    need(names == ['lo'], 'NONLOOPBACK_INTERFACE_PRESENT')\n    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC) as handle:\n        flags_raw = fcntl.ioctl(handle.fileno(), 0x8913, struct.pack('16sH22x', b'lo', 0))\n        flags = struct.unpack_from('H', flags_raw, 16)[0]\n        address_raw = fcntl.ioctl(handle.fileno(), 0x8915, struct.pack('16sH22x', b'lo', 0))\n    need(flags in (0x9, 0x49), 'LOOPBACK_NOT_UP_OR_FLAGS_UNREVIEWED')\n    need(struct.unpack_from('H', address_raw, 16)[0] == socket.AF_INET and\n         address_raw[20:24] == b'\\x7f\\x00\\x00\\x01', 'LOOPBACK_ADDRESS_DIFFERS')\n    route4 = []\n    lines4 = bounded('/proc/net/route')\n    need(1 <= len(lines4) <= 33, 'IPV4_ROUTE_POPULATION')\n    for line in lines4[1:]:\n        fields = line.split()\n        need(len(fields) == 11 and fields[0] == 'lo' and\n             all(re.fullmatch(r'[0-9a-fA-F]{8}', fields[i]) for i in (1, 2, 7)),\n             'IPV4_ROUTE_SHAPE')\n        need(ipaddress.IPv4Address(bytes.fromhex(fields[1])[::-1]).is_loopback and\n             int(fields[2], 16) == 0, 'EXTERNAL_IPV4_ROUTE')\n        route4.append([fields[i] for i in (0, 1, 2, 3, 7, 8, 9, 10)])\n    route6 = []\n    lines6 = bounded('/proc/net/ipv6_route')\n    need(len(lines6) <= 32, 'IPV6_ROUTE_POPULATION')\n    for line in lines6:\n        fields = line.split()\n        need(len(fields) == 10 and fields[9] == 'lo' and\n             all(re.fullmatch(r'[0-9a-fA-F]{32}', fields[i]) for i in (0, 2, 4)) and\n             all(re.fullmatch(r'[0-9a-fA-F]{2}', fields[i]) for i in (1, 3)) and\n             all(re.fullmatch(r'[0-9a-fA-F]{8}', fields[i]) for i in (5, 6, 7, 8)),\n             'IPV6_ROUTE_SHAPE')\n        rejected = bool(int(fields[8], 16) & 0x200)\n        loopback = int(fields[1], 16) == 128 and ipaddress.IPv6Address(int(fields[0], 16)).is_loopback\n        need((rejected or loopback) and int(fields[4], 16) == 0, 'EXTERNAL_IPV6_ROUTE')\n        route6.append([fields[i] for i in (0, 1, 2, 3, 4, 5, 8, 9)])\n    # Traffic counters and transient reference/use counts are deliberately not\n    # identity fields. Addresses, flags and admitted route population are.\n    routes = {'ipv4': sorted(route4), 'ipv6': sorted(route6)}\n    return {'network_namespace_sha256': sha(namespace.encode()),\n            'namespace_distinct': True, 'interfaces': ['lo'], 'loopback_up': True,\n            'loopback_flags': flags, 'loopback_address': '127.0.0.1',\n            'external_routes': 0, 'ipv4_route_count': len(route4),\n            'ipv6_route_count': len(route6), 'route_population_sha256': sha(encode(routes))}\n\ndef snapshot(uid,gid,parent,network_parent):\n    namespace=os.readlink('/proc/self/ns/mnt')\n    raw=open('/proc/self/mountinfo','rb').read(1048577)\n    private,count,rows=parse_mounts(raw)\n    fields={}\n    for line in open('/proc/self/status',encoding='ascii'):\n        if ':' in line:\n            key,value=line.split(':',1);fields[key]=value.strip()\n    uids=[int(x) for x in fields['Uid'].split()];gids=[int(x) for x in fields['Gid'].split()]\n    caps={key:int(fields[key],16) for key in ('CapEff','CapPrm','CapAmb')}\n    for row in rows[:2]:\n        path=row['path'];info=os.lstat(path);entries=sorted(os.listdir(path))\n        expected=['dg17-empty-system-gitconfig'] if path=='/opt' else []\n        need(entries==expected,'TARGET_DIRECTORY_POPULATION')\n        row.update(directory_uid=info.st_uid,directory_gid=info.st_gid,mode=stat.S_IMODE(info.st_mode),\n                   directory=stat.S_ISDIR(info.st_mode),symlink=stat.S_ISLNK(info.st_mode),\n                   entries=len(entries),device=info.st_dev,inode=info.st_ino)\n    source=file_snapshot(CONFIG_SOURCE);target=file_snapshot('/etc/gitconfig');rows[2].update(target)\n    need(source==target and source['device']==rows[0]['device'],'EMPTY_CONFIG_BIND_IDENTITY')\n    result={'mount_namespace_sha256':sha(namespace.encode()),'namespace_distinct':namespace!=parent,\n            'private_propagation':private,'mountinfo_sha256':sha(raw),'mount_count':count,\n            'uids':uids,'gids':gids,'groups':os.getgroups(),'capabilities':caps,\n            'no_new_privileges':int(fields['NoNewPrivs']),'mounts':rows,\n            'gitconfig_source':{'path':CONFIG_SOURCE,**source},'source_target_same_file':True,\n            'network':network_snapshot(network_parent)}\n    need(result['namespace_distinct'] and private and uids==[uid]*4 and gids==[gid]*4 and\n         not result['groups'] and all(v==0 for v in caps.values()) and result['no_new_privileges']==1,'PRIVILEGE_OR_NAMESPACE')\n    need(len({row['mount_id'] for row in rows})==3 and all(row['filesystem']=='tmpfs' and row['mount_source']=='tmpfs' and\n             row['mount_root']==('/dg17-empty-system-gitconfig' if row['path']=='/etc/gitconfig' else '/') and\n             row['mount_id']>0 and row['parent_mount_id']>0 and row['mount_id']!=row['parent_mount_id'] and\n             all(row[key] is True for key in ('readonly','nodev','nosuid','noexec')) and row['size_bytes']==4096 for row in rows),'TARGET_MOUNT_VIEW')\n    need(all(row['directory'] is True and row['symlink'] is False and row['directory_uid']==0 and\n             row['directory_gid']==0 and row['mode']==0o755 and row['entries']==(1 if row['path']=='/opt' else 0)\n             for row in rows[:2]),'TARGET_DIRECTORY_VIEW')\n    return result\ndef write(path,value,uid):\n    parent=os.path.dirname(path);info=os.lstat(parent)\n    need(os.path.realpath(parent)==parent and stat.S_ISDIR(info.st_mode) and info.st_uid==uid,'PROOF_PARENT')\n    raw=encode(value);need(len(raw)<=16384,'PROOF_BOUND')\n    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())\n    return sha(raw)\ndef run():\n    need(len(sys.argv)==32,'ARGUMENT_POPULATION')\n    uid=int(sys.argv[1]);gid=int(sys.argv[2]);before_path=sys.argv[3];result_path=sys.argv[4];parent=sys.argv[5];network_parent=sys.argv[6]\n    need(uid>0 and gid>0 and re.fullmatch(r'mnt:\\[[0-9]+\\]',parent),'ARGUMENT_VALUE')\n    need(os.path.basename(before_path)=='CAPSULE_ADMISSION.json' and\n         os.path.basename(result_path)=='CAPSULE_RESULT.json' and\n         os.path.dirname(before_path)==os.path.dirname(result_path),'PROOF_PATHS')\n    argv=['/usr/bin/python3','-I','-S','-B',*sys.argv[7:]]\n    argv_sha=sha(encode(argv));before=snapshot(uid,gid,parent,network_parent)\n    proof={'schema':'dg17.private-view-admission.v3','child_argv_sha256':argv_sha,'snapshot':before}\n    before_sha=write(before_path,proof,uid)\n    child_rc=None;after=None;failure=None\n    try:\n        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,close_fds=True)\n        child_rc=child.wait()\n    except BaseException:\n        failure='CHILD_START_OR_WAIT_REFUSED'\n    try:after=snapshot(uid,gid,parent,network_parent)\n    except BaseException:\n        failure=failure or 'AFTER_VIEW_REFUSED'\n    result={'schema':'dg17.private-view-result.v3','before_sha256':before_sha,'child_argv_sha256':argv_sha,\n            'before':before,'after':after,'child_returncode':child_rc,'failure':failure}\n    write(result_path,result,uid)\n    return 0 if failure is None and child_rc==0 and before==after else 1\nif __name__=='__main__':\n    try:sys.exit(run())\n    except BaseException as exc:\n        if isinstance(exc,SystemExit):raise\n        sys.stderr.write('DG17_CAPSULE_ADMISSION_REFUSED\\n');sys.exit(1)\n"

CAPSULE_CODE_SHA = 'fbc15a7cdb0ed37ceb87162b49400a18b8fd2ed2f80a124fb131c067a8d7cc93'

class Refusal(Exception): pass

def need(test, code):
    if not test: raise Refusal(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()

def read(path, limit=1048576):
    path = Path(path); before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, 'FILE_SHAPE')
    with path.open('rb') as stream: raw = stream.read(limit+1)
    after = path.lstat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and len(raw) == before.st_size, 'FILE_CHANGED')
    return raw

def save(path, value):
    path = Path(path); tmp = path.with_name(path.name+'.next')
    with tmp.open('xb') as out: out.write(encoded(value)); out.flush(); os.fsync(out.fileno())
    os.chmod(tmp, 0o600); os.replace(tmp, path)

def stream_hash(path):
    h = hashlib.sha256(); size = 0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): size += len(chunk); h.update(chunk)
    return size, h.hexdigest()

def catalogue_schema_matches(value, schema):
    # The pinned result schema uses only this small, closed keyword set.
    allowed = {'$schema', 'title', 'type', 'additionalProperties', 'required', 'properties', 'const', 'enum', 'anyOf', 'minimum', 'maximum', 'maxItems', 'items', 'pattern'}
    need(type(schema) is dict and set(schema) <= allowed, 'CATALOGUE_SCHEMA_KEYWORD')
    if 'anyOf' in schema:
        need(set(schema) == {'anyOf'}, 'CATALOGUE_SCHEMA_COMBINATION')
        return any(catalogue_schema_matches(value, part) for part in schema['anyOf'])
    expected = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        need(schema['type'] in expected, 'CATALOGUE_SCHEMA_TYPE')
        if type(value) is not expected[schema['type']]: return False
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']): return False
    if 'enum' in schema and not any(type(value) is type(item) and value == item for item in schema['enum']): return False
    if type(value) is dict:
        need(schema.get('additionalProperties') is False, 'CATALOGUE_SCHEMA_OBJECT_NOT_CLOSED')
        props = schema['properties']
        if not set(schema['required']) <= set(value) <= set(props): return False
        if not all(catalogue_schema_matches(item, props[key]) for key, item in value.items()): return False
    if type(value) is list:
        if 'maxItems' in schema and len(value) > schema['maxItems']: return False
        if 'items' in schema and not all(catalogue_schema_matches(item, schema['items']) for item in value): return False
    if 'minimum' in schema and (type(value) is not int or value < schema['minimum']): return False
    if 'maximum' in schema and (type(value) is not int or value > schema['maximum']): return False
    if 'pattern' in schema and (type(value) is not str or re.search(schema['pattern'], value) is None): return False
    return True

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'CATALOGUE_DUPLICATE_KEY'); result[key] = value
    return result

def content_fs_identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
            'uid':info.st_uid,'gid':info.st_gid,'nlink':info.st_nlink,
            'bytes':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}


def content_helper_refusal_observation(name, inherited):
    """Closed metadata from the existing refusal; no raw path, code or exception."""
    helpers = ('bash','cat','bwrap','true','python3','env')
    codes = ('TOOL_NOT_EXECUTABLE','TOOL_CUSTODY_REFUSED','PRIVILEGED_TOOL_REFUSED',
             'TOOL_CAPABILITY_UNKNOWN','FILE_SHAPE_REFUSED','FILE_CHANGED','TOOL_OS_REFUSAL')
    helper = name if type(name) is str and name in helpers else None
    received = (helper is not None and type(inherited) is dict and
                set(inherited) == {'available','requested','code','errno'} and
                inherited['available'] is False and
                type(inherited['requested']) is str and inherited['requested'] == '/usr/bin/'+helper and
                type(inherited['code']) is str and inherited['code'] in codes and
                (inherited['errno'] is None or
                 (inherited['code'] == 'TOOL_OS_REFUSAL' and type(inherited['errno']) is int and
                  0 <= inherited['errno'] <= 4096)))
    return {'schema':'dg17.codex.system-helper-refusal.v1','scope':'FIRST_HELPER_REFUSAL_ONLY',
            'helper_id':helper,'inherited_refusal_received':received,
            'inherited_code':inherited['code'] if received else None,
            'inherited_errno':inherited['errno'] if received else None}


def content_system_helpers(u, state):
    """Data-only physical system identities; never run a capability probe."""
    names = ('bash','cat','bwrap','true','python3','env')
    rows = []
    bin_alias = Path('/bin'); alias_info = bin_alias.lstat()
    need(stat.S_ISLNK(alias_info.st_mode) and alias_info.st_uid == 0 and
         os.readlink(bin_alias) in ('usr/bin','/usr/bin') and
         bin_alias.resolve(strict=True) == Path('/usr/bin'), 'CONTENT_BIN_ALIAS_PROFILE')
    for directory in (Path('/'),Path('/usr'),Path('/usr/bin')):
        info = directory.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022 and
             directory.resolve(strict=True) == directory, 'CONTENT_SYSTEM_ANCESTRY')
    for name in names:
        requested = Path('/usr/bin')/name
        canonical, inherited = u.trusted(name)
        if canonical is None:
            state.setdefault('content_helper_refusal', content_helper_refusal_observation(name, inherited))
        need(canonical is not None, 'CONTENT_SYSTEM_HELPER_REFUSED')
        path = Path(canonical); link_info = requested.lstat()
        if name == 'python3':
            need(re.fullmatch(r'/usr/bin/python3(?:\.[0-9]{1,2})?',canonical) is not None,
                 'CONTENT_PYTHON_CANONICAL_PROFILE')
            need((stat.S_ISREG(link_info.st_mode) or stat.S_ISLNK(link_info.st_mode)) and
                 link_info.st_uid == 0, 'CONTENT_PYTHON_ALIAS_PROFILE')
        else:
            need(path == requested and stat.S_ISREG(link_info.st_mode),
                 'CONTENT_SYSTEM_HELPER_ALIAS')
        info = path.lstat(); identity = content_fs_identity(info)
        need(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and
             not info.st_mode & 0o6022 and info.st_mode & 0o111 and
             64 <= info.st_size <= 67108864, 'CONTENT_SYSTEM_HELPER_SHAPE')
        fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
        try:
            need(content_fs_identity(os.fstat(fd)) == identity, 'CONTENT_SYSTEM_HELPER_OPEN_DRIFT')
            header = os.read(fd,64)
            need(len(header) == 64 and header[:7] == b'\x7fELF\x02\x01\x01' and
                 int.from_bytes(header[16:18],'little') in (2,3) and
                 int.from_bytes(header[18:20],'little') == 62, 'CONTENT_SYSTEM_HELPER_ELF')
            hashed = hashlib.sha256(); hashed.update(header); count = len(header)
            while True:
                chunk = os.read(fd,1048576)
                if not chunk: break
                count += len(chunk); need(count <= info.st_size, 'CONTENT_SYSTEM_HELPER_READ_BOUND')
                hashed.update(chunk)
            need(count == info.st_size and content_fs_identity(os.fstat(fd)) == identity and
                 content_fs_identity(path.lstat()) == identity and
                 content_fs_identity(requested.lstat()) == content_fs_identity(link_info),
                 'CONTENT_SYSTEM_HELPER_DRIFT')
        finally:
            os.close(fd)
        need(inherited['bytes'] == count and inherited['sha256'] == hashed.hexdigest() and
             (Path('/bin')/name).resolve(strict=True) == path,
             'CONTENT_SYSTEM_HELPER_IDENTITY_JOIN')
        rows.append({'name':name,'requested':str(requested),'canonical':canonical,
                     'identity':identity,'requested_identity':content_fs_identity(link_info),
                     'bytes':count,'sha256':hashed.hexdigest(),'elf':'ELF64_LSB_X86_64',
                     'bin_alias_same_file':True,'inherited_admission':inherited})
    need(content_fs_identity(bin_alias.lstat()) == content_fs_identity(alias_info) and
         bin_alias.resolve(strict=True) == Path('/usr/bin'), 'CONTENT_BIN_ALIAS_DRIFT')
    return {'profile':'PHYSICAL_SYSTEM_HELPERS_ONLY_V1','helpers':rows,
            'bin_alias':{'target':os.readlink(bin_alias),'identity':content_fs_identity(alias_info)},
            'capability_probe_executed':False}


def content_system_recheck(state,output,u,role):
    snapshot = content_system_helpers(u, state)
    need(encoded(snapshot) == encoded(state['content_helpers_private']['before']),
         'CONTENT_SYSTEM_HELPERS_CHANGED')
    raw = encoded(snapshot)
    state['content_helpers']['rechecks'][role] = {'matches_before':True,'sha256':digest(raw)}
    return snapshot


def content_runtime_owner(output,require_empty):
    """Complete separate runtime-copy owner; no binary is excluded from metadata implicitly."""
    root = output/'canonical-routing-runtime'; uid = os.getuid(); gid = os.getgid()
    root_info = root.lstat()
    need(stat.S_ISDIR(root_info.st_mode) and root_info.st_uid == uid and root_info.st_gid == gid and
         stat.S_IMODE(root_info.st_mode) == 0o700 and root.resolve(strict=True) == root,
         'CONTENT_RUNTIME_OWNER_ROOT')
    expected_dirs = {'canonical','canonical/owned-binary'}
    expected_files = {'canonical/owned-binary/codex'}
    rows = []; pending = [root]; directories = [(root,content_fs_identity(root_info))]
    try:
        while pending:
            here = pending.pop()
            with os.scandir(here) as stream:
                entries = list(stream)
            for entry in entries:
                path = here/entry.name; relative = path.relative_to(root).as_posix(); info = path.lstat()
                ident = content_fs_identity(info)
                need(info.st_uid == uid and info.st_gid == gid, 'CONTENT_RUNTIME_OWNER_IDENTITY')
                if stat.S_ISDIR(info.st_mode):
                    need(relative in expected_dirs and stat.S_IMODE(info.st_mode) == 0o700 and
                         path.resolve(strict=True) == path, 'CONTENT_RUNTIME_OWNER_DIRECTORY')
                    rows.append({'path':relative,'kind':'DIRECTORY','identity':ident})
                    directories.append((path,ident)); pending.append(path)
                else:
                    need(relative in expected_files and stat.S_ISREG(info.st_mode) and
                         info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o700,
                         'CONTENT_RUNTIME_OWNER_FILE')
                    fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
                    try:
                        need(content_fs_identity(os.fstat(fd)) == ident, 'CONTENT_RUNTIME_OWNER_OPEN_DRIFT')
                        hashed = hashlib.sha256(); size = 0
                        while True:
                            chunk = os.read(fd,1048576)
                            if not chunk: break
                            size += len(chunk); need(size <= BINARY_BYTES, 'CONTENT_RUNTIME_OWNER_BOUND')
                            hashed.update(chunk)
                        need(size == BINARY_BYTES and hashed.hexdigest() == BINARY_SHA and
                             content_fs_identity(os.fstat(fd)) == ident and
                             content_fs_identity(path.lstat()) == ident, 'CONTENT_RUNTIME_OWNER_BYTES')
                    finally:
                        os.close(fd)
                    rows.append({'path':relative,'kind':'REGULAR','identity':ident,
                                 'bytes':size,'sha256':hashed.hexdigest()})
        need(all(content_fs_identity(path.lstat()) == ident for path,ident in directories),
             'CONTENT_RUNTIME_OWNER_CHANGED')
    except OSError:
        raise Refusal('CONTENT_RUNTIME_OWNER_ENUMERATION_OR_READ_REFUSED') from None
    found_dirs = {row['path'] for row in rows if row['kind'] == 'DIRECTORY'}
    files = [row for row in rows if row['kind'] == 'REGULAR']
    need(found_dirs == expected_dirs and (not require_empty or not files),
         'CONTENT_RUNTIME_OWNER_POPULATION')
    rows.sort(key=lambda row:row['path'])
    return {'profile':'ONE_EXACT_RUNTIME_COPY_SEPARATE_OWNER_V1',
            'root_identity':content_fs_identity(root_info),'members':rows,
            'retained_files':len(files),'retained_bytes':sum(row['bytes'] for row in files),
            'empty_after_owned_closure':not files}

def content_package_spec(family):
    specs = {
        'canonical':{'archive':'IMPLEMENTAUDIT.plugin.zip','bytes':584974,
                     'sha256':'18bb9d7dcb876f7c6be4340bec10dbc77f091227c24504dcecdb0b7d9853f458',
                     'git_blob':'e303febc90f4264ccff06853584c7242c6ef8b4a',
                     'matrix':'CANONICAL_PACKAGE_MATRIX.json',
                     'matrix_sha256':'ef9cbbe7c2c277c434139080d548f0cb868ee091fe79aa96633dcd46cc86a117',
                     'files':75,'expanded_bytes':2092025,'governor':'skills/implementaudit/SKILL.md'},
        'standalone':{'archive':'IMPLEMENTAUDIT.skill','bytes':580372,
                      'sha256':'b6fd05b9f1c0b26fe6a193b47e8f6487f3a161e51824670ca0a520772b307413',
                      'git_blob':'50c244b02520d440a4194c7b24a105c8bc8ca506',
                      'matrix':'STANDALONE_PACKAGE_MATRIX.json',
                      'matrix_sha256':'687367382cf92717c87a5b838aaebf2a39e15e6b98ddf34baa40c0e2ff8d9b6f',
                      'files':72,'expanded_bytes':2087351,'governor':'SKILL.md'}}
    need(type(family) is str and family in specs, 'CONTENT_PACKAGE_FAMILY')
    return specs[family]


def content_archive_input(packet,family):
    spec = content_package_spec(family); directory = packet/'package-inputs'
    need(packet.resolve(strict=True) == packet and directory.resolve(strict=True) == directory,
         'CONTENT_PACKAGE_INPUT_ALIAS')
    info = directory.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
         not info.st_mode & 0o022, 'CONTENT_PACKAGE_INPUT_DIRECTORY')
    path = directory/spec['archive']; info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid() and
         stat.S_IMODE(info.st_mode) == 0o644 and info.st_size == spec['bytes'],
         'CONTENT_PACKAGE_INPUT_SHAPE')
    identity = content_fs_identity(info); raw = read(path,spec['bytes'])
    need(content_fs_identity(path.lstat()) == identity and digest(raw) == spec['sha256'] and
         hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest() == spec['git_blob'],
         'CONTENT_PACKAGE_INPUT_PIN')
    return path


def content_archive_population(packet,family):
    spec = content_package_spec(family); path = content_archive_input(packet,family)
    matrix_raw = read(packet/spec['matrix'],65536)
    need(digest(matrix_raw) == spec['matrix_sha256'], 'CONTENT_PACKAGE_MATRIX_PIN')
    matrix = json.loads(matrix_raw,object_pairs_hook=unique_object)
    need(type(matrix) is dict and len(matrix) == spec['files'], 'CONTENT_PACKAGE_MATRIX_POPULATION')
    files = {}; total = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        need(len(infos) == spec['files'] and len({row.filename for row in infos}) == len(infos),
             'CONTENT_PACKAGE_ARCHIVE_POPULATION')
        for row in infos:
            name = row.filename; relative = Path(name)
            need(type(name) is str and re.fullmatch(r'[A-Za-z0-9_./-]{1,512}',name) is not None and
                 not relative.is_absolute() and all(part not in ('','.','..') for part in name.split('/')) and
                 relative.as_posix() == name and not row.is_dir() and name in matrix,
                 'CONTENT_PACKAGE_ARCHIVE_PATH')
            expected = matrix[name]
            need(type(expected) is dict and set(expected) == {'bytes','mode','sha256'} and
                 type(expected['bytes']) is int and 0 <= expected['bytes'] <= 4194304 and
                 type(expected['mode']) is int and expected['mode'] in (0o644,0o755) and
                 type(expected['sha256']) is str and re.fullmatch('[0-9a-f]{64}',expected['sha256']) is not None,
                 'CONTENT_PACKAGE_MATRIX_ROW')
            mode = row.external_attr >> 16
            need(not row.flag_bits & 1 and row.create_system == 3 and stat.S_ISREG(mode) and
                 stat.S_IMODE(mode) == expected['mode'] and row.file_size == expected['bytes'],
                 'CONTENT_PACKAGE_ARCHIVE_ENTRY')
            raw = archive.read(row)
            need(len(raw) == expected['bytes'] and digest(raw) == expected['sha256'],
                 'CONTENT_PACKAGE_ARCHIVE_BYTES')
            total += len(raw); need(total <= spec['expanded_bytes'], 'CONTENT_PACKAGE_ARCHIVE_TOTAL_BOUND')
            files[name] = raw
    need(total == spec['expanded_bytes'] and set(files) == set(matrix), 'CONTENT_PACKAGE_ARCHIVE_TOTAL')
    content_governor_bytes(files[spec['governor']])
    content_archive_input(packet,family)
    return {'spec':spec,'matrix':matrix,'files':files}


def content_package_snapshot(root,population):
    """Complete physical package tree, including directory identities and every file byte."""
    matrix = population['matrix']; spec = population['spec']; uid = os.getuid(); gid = os.getgid()
    expected_dirs = set()
    for name in matrix:
        parts = Path(name).parts
        expected_dirs.update('/'.join(parts[:index]) for index in range(1,len(parts)))
    info = root.lstat(); root_identity = content_fs_identity(info)
    need(root.resolve(strict=True) == root and stat.S_ISDIR(info.st_mode) and
         info.st_uid == uid and info.st_gid == gid and stat.S_IMODE(info.st_mode) in (0o700,0o755),
         'CONTENT_PACKAGE_ROOT')
    rows = []; pending = [root]; directories = [(root,root_identity)]; found_files = set(); found_dirs = set(); total = 0
    try:
        while pending:
            here = pending.pop()
            with os.scandir(here) as stream:
                entries = list(stream)
            for entry in entries:
                path = here/entry.name; relative = path.relative_to(root).as_posix(); info = path.lstat()
                identity = content_fs_identity(info)
                need(info.st_uid == uid and info.st_gid == gid, 'CONTENT_PACKAGE_OWNER')
                if stat.S_ISDIR(info.st_mode):
                    need(relative in expected_dirs and stat.S_IMODE(info.st_mode) in (0o700,0o755) and
                         path.resolve(strict=True) == path, 'CONTENT_PACKAGE_DIRECTORY')
                    found_dirs.add(relative); pending.append(path); directories.append((path,identity))
                    rows.append({'path':relative,'kind':'DIRECTORY','identity':identity})
                    continue
                need(relative in matrix and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                     stat.S_IMODE(info.st_mode) == matrix[relative]['mode'], 'CONTENT_PACKAGE_FILE')
                expected = matrix[relative]; fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
                try:
                    need(content_fs_identity(os.fstat(fd)) == identity, 'CONTENT_PACKAGE_OPEN_DRIFT')
                    h = hashlib.sha256(); count = 0
                    while True:
                        chunk = os.read(fd,1048576)
                        if not chunk: break
                        count += len(chunk); need(count <= expected['bytes'], 'CONTENT_PACKAGE_FILE_BOUND')
                        h.update(chunk)
                    need(count == expected['bytes'] and h.hexdigest() == expected['sha256'] and
                         content_fs_identity(os.fstat(fd)) == identity and
                         content_fs_identity(path.lstat()) == identity, 'CONTENT_PACKAGE_FILE_BYTES_OR_DRIFT')
                finally:
                    os.close(fd)
                found_files.add(relative); total += count
                rows.append({'path':relative,'kind':'REGULAR','identity':identity,
                             'bytes':count,'sha256':h.hexdigest()})
        need(all(content_fs_identity(path.lstat()) == identity for path,identity in directories),
             'CONTENT_PACKAGE_DIRECTORY_DRIFT')
    except OSError:
        raise Refusal('CONTENT_PACKAGE_ENUMERATION_OR_READ_REFUSED') from None
    need(found_files == set(matrix) and found_dirs == expected_dirs and total == spec['expanded_bytes'],
         'CONTENT_PACKAGE_POPULATION')
    rows.sort(key=lambda row:row['path'])
    return {'root_identity':root_identity,'members':rows,'regular_files':len(found_files),
            'directories':len(found_dirs),'bytes':total,'matrix_sha256':spec['matrix_sha256']}

def content_governor_bytes(raw):
    need(type(raw) is bytes and len(raw) == 21257 and
         digest(raw) == '4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5',
         'CONTENT_GOVERNOR_INPUT_PIN')
    try:
        text = raw.decode('utf-8','strict')
        prefix = raw[:8000].decode('utf-8','strict')
    except UnicodeError:
        raise Refusal('CONTENT_GOVERNOR_UTF8') from None
    need(digest(prefix.encode()) == '3c89161abdc251c3973122ed1d0e0e52b582e144b8d9f50148246972e2f1d791',
         'CONTENT_GOVERNOR_PREFIX_PIN')
    return text,prefix


def content_fixed_path(value):
    need(type(value) is str and 1 <= len(value.encode('utf-8')) <= 512 and
         re.fullmatch(r'/[A-Za-z0-9_./-]+',value) is not None and
         all(part not in ('','.','..') for part in value.split('/')[1:]) and
         str(Path(value)) == value, 'CONTENT_FIXED_PATH')
    return value


def content_fixed_exec_args(path,cwd):
    path = content_fixed_path(path); cwd = content_fixed_path(cwd)
    return {'cmd':"/usr/bin/cat -- '"+path+"'",'workdir':cwd,'shell':'/usr/bin/bash',
            'login':False,'tty':False,'yield_time_ms':30000,'max_output_tokens':8192,
            'sandbox_permissions':'use_default'}


def content_skill_fragment(family,path,raw):
    need(family in ('canonical','standalone'), 'CONTENT_FAMILY')
    name = 'implementaudit:implementaudit' if family == 'canonical' else 'implementaudit'
    path = content_fixed_path(path); full,prefix = content_governor_bytes(raw)
    fragment = '<skill>\n<name>'+name+'</name>\n<path>'+path+'</path>\n'+prefix+'\n</skill>'
    need(fragment.count(prefix) == 1 and full not in fragment, 'CONTENT_FRAGMENT_CEILING')
    return fragment


def content_prefix_projection(request,family,path,raw):
    """Receive the selected fragment only from an actual native request's user text."""
    full,prefix = content_governor_bytes(raw); fragment = content_skill_fragment(family,path,raw)
    need(type(request) is dict, 'CONTENT_REQUEST_OBJECT')
    inputs = request.get('input')
    need(type(inputs) is list and 1 <= len(inputs) <= 1024, 'CONTENT_REQUEST_INPUTS')
    matches = []; total_fragment_occurrences = 0; full_occurrences = 0
    pending = [request]; walked = 0
    while pending:
        node = pending.pop(); walked += 1
        need(walked <= 65536, 'CONTENT_REQUEST_VALUE_BOUND')
        if type(node) is str:
            total_fragment_occurrences += node.count(fragment)
            full_occurrences += node.count(full)
        elif type(node) is list:
            pending.extend(node)
        elif type(node) is dict:
            pending.extend(node.values())
        else:
            need(node is None or type(node) in (bool,int,float), 'CONTENT_REQUEST_JSON_VALUE')
    for input_index,item in enumerate(inputs):
        if type(item) is not dict or item.get('role') != 'user': continue
        if item.get('type','message') != 'message': continue
        blocks = item.get('content')
        if type(blocks) is not list: continue
        for content_index,block in enumerate(blocks):
            if type(block) is not dict or block.get('type') != 'input_text' or type(block.get('text')) is not str: continue
            text = block['text']; offset = text.find(fragment)
            if offset < 0: continue
            need(text.count(fragment) == 1, 'CONTENT_PREFIX_DUPLICATED')
            start = len(text[:offset].encode('utf-8')); fragment_raw = fragment.encode('utf-8')
            prefix_offset = len(fragment[:fragment.index(prefix)].encode('utf-8'))
            matches.append({'input_index':input_index,'content_index':content_index,
                            'fragment_start_bytes':start,'fragment_end_bytes':start+len(fragment_raw),
                            'fragment_bytes':len(fragment_raw),'fragment_sha256':digest(fragment_raw),
                            'prefix_start_bytes':start+prefix_offset,'prefix_bytes':8000,
                            'prefix_sha256':digest(prefix.encode()),'raw_frontmatter_preserved':True,
                            'edge_whitespace_trimmed':False,'full_governor_received_in_first_request':False})
    need(len(matches) == 1 and total_fragment_occurrences == 1 and full_occurrences == 0,
         'CONTENT_TYPED_PREFIX_ORIGIN_OR_POPULATION')
    return matches[0]


def content_full_output_projection(text,raw):
    """Pinned ordinary interactive ExecCommandToolOutput text, never code-mode JSON."""
    content_governor_bytes(raw)
    need(type(text) is str and len(text.encode('utf-8')) <= 32768, 'CONTENT_TOOL_OUTPUT_BOUND')
    pattern = (r'(?:Chunk ID: [A-Za-z0-9_-]{1,64}\n)?'
               r'Wall time: ((?:0|[1-9][0-9]{0,2})\.[0-9]{4}) seconds\n'
               r'Process exited with code 0\n'
               r'(?:Original token count: (0|[1-9][0-9]{0,8})\n)?'
               r'Output:\n')
    match = re.match(pattern,text)
    need(match is not None and 0 <= float(match.group(1)) <= 90,
         'CONTENT_TOOL_OUTPUT_ENVELOPE')
    start = len(text[:match.end()].encode('utf-8')); output = text[match.end():].encode('utf-8')
    need(output == raw, 'CONTENT_TOOL_OUTPUT_FULL_BYTES')
    return {'header_bytes':start,'output_start_bytes':start,'output_end_bytes':start+len(raw),
            'output_bytes':len(raw),'output_sha256':digest(raw),'exit_code':0,
            'live_session':False,'truncation_observed':False,
            'full_governor_in_matched_native_tool_output':True}

def content_capture_base_shape(row,name):
    keys = {'name','process_started','returncode','timeout','output_bound_exceeded',
            'pidfd_acquired','internal_failure','reason_code','stream_digest_scope',
            'streams_complete','stdout_bytes','stderr_bytes','stdout_sha256','stderr_sha256',
            'cleanup','private_streams_retained','retention_failure'}
    if type(row) is not dict or set(row) != keys or row['name'] != name: return False
    if not all(type(row[k]) is bool for k in ('process_started','timeout','output_bound_exceeded','pidfd_acquired','streams_complete','private_streams_retained','retention_failure')): return False
    if type(row['returncode']) is not int or (row['internal_failure'] is not False if name == 'native-content' else row['internal_failure'] is not None) or type(row['reason_code']) is not str or not 1 <= len(row['reason_code']) <= 96 or row['stream_digest_scope'] != 'CAPTURED_BYTES_ONLY': return False
    limits = {'stdout':2097152,'stderr':131072} if name == 'native-content' else {'stdout':32768,'stderr':32768}
    if any(type(row[k+'_bytes']) is not int or not 0 <= row[k+'_bytes'] <= limits[k] or type(row[k+'_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row[k+'_sha256']) is None for k in ('stdout','stderr')): return False
    cleanup = row['cleanup']
    if type(cleanup) is not dict or set(cleanup) != {'echild','pidfd_signals','retained_status_count','retained_statuses_sha256','reaped_statuses','reaped_statuses_truncated'}: return False
    if type(cleanup['echild']) is not bool or type(cleanup['reaped_statuses_truncated']) is not bool or any(type(cleanup[k]) is not int or cleanup[k] < 0 for k in ('pidfd_signals','retained_status_count')): return False
    if type(cleanup['retained_statuses_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',cleanup['retained_statuses_sha256']) is None: return False
    statuses = cleanup['reaped_statuses']; count = cleanup['retained_status_count']
    if type(statuses) is not list or len(statuses) != min(count,8) or cleanup['reaped_statuses_truncated'] is not (count > 8): return False
    if any(type(item) is not dict or set(item) != {'pid','returncode'} or type(item['pid']) is not int or item['pid'] <= 0 or type(item['returncode']) is not int for item in statuses): return False
    return True


def receive_content(state,packet,raw):
    need(type(raw) is bytes and len(raw) <= 32768, 'CONTENT_RESULT_BOUND')
    value = json.loads(raw,object_pairs_hook=unique_object)
    schema = json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'),object_pairs_hook=unique_object)
    need(catalogue_schema_matches(value,schema), 'CONTENT_RESULT_SCHEMA')
    state['content'] = value
    state['content_validation'] = {'valid':True,'result_sha256':digest(raw),
                                   'captured_result_matches':False,'semantic_receiving_passed':False}


class RouteRefusal(Exception):
    pass


def r_need(ok, code):
    if not ok:
        raise RouteRefusal(code)


def r_hash(raw):
    return hashlib.sha256(raw).hexdigest()


def r_compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')


def r_pretty(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)+'\n').encode('utf-8')


def r_json(raw, limit=2097152):
    r_need(type(raw) is bytes and len(raw) <= limit, 'ROUTE_JSON_BOUND')
    def pairs(rows):
        out = {}
        for key, value in rows:
            r_need(key not in out, 'ROUTE_DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    def constant(value):
        raise RouteRefusal('ROUTE_NONFINITE_JSON')
    try:
        value = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs, parse_constant=constant)
        pending = [(value, 0)]; count = 0
        while pending:
            node, depth = pending.pop(); count += 1
            r_need(depth <= 32 and count <= 65536, 'ROUTE_JSON_STRUCTURE_BOUND')
            if type(node) is dict:
                r_need(all(type(k) is str and len(k.encode()) <= 1024 for k in node), 'ROUTE_JSON_KEY_BOUND')
                pending.extend((v, depth+1) for v in node.values())
            elif type(node) is list:
                pending.extend((v, depth+1) for v in node)
            elif type(node) is str:
                r_need(len(node.encode('utf-8', 'strict')) <= 2097152, 'ROUTE_JSON_STRING_BOUND')
            else:
                r_need(node is None or type(node) in (int, bool) or type(node) is float and math.isfinite(node), 'ROUTE_JSON_SCALAR')
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise RouteRefusal('ROUTE_JSON_DECODE') from None


R_INDEX_SHA = '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347'


R_GOV_SHA = '4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5'


R_PREFIX_SHA = '3c89161abdc251c3973122ed1d0e0e52b582e144b8d9f50148246972e2f1d791'


R_CHILD_SHA = '6f5d5738b9efd5fa5d4c35868400220458a2f81179d4081fce508ef65c3f72e4'


R_RESOLVER_SHA = '97ce587a295cfa0f13276a8dfccf63ca9f679352fdcf0d769a095eab5284b67d'


R_NONVERDICT_SHA = '3e0f9e74b5663b5cb63e2ff3d80e10f17c899ea46d34e1d88710ae16fb91fee3'


R_MODEL = 'dg17-canonical-routing-fixture'


R_CLAIMS = ['NINE_OPERATION_SCOPE_RECONCILIATION', 'ORIGINAL95_IDENTITY_HISTORY_AND_COUNT_PRESERVATION', 'HOST_FAMILY_SCOPE_AND_PENDING_CONJUNCTIONS', 'NO_PROMOTION_AND_UNKNOWN_BOUNDARY_PRESERVATION']


R_ANNOUNCEMENT = 'Loaded the exact audit-assess procedure after the governor and resolver gates. Starting one fresh native child for the bound composition object; the scripted NONVERDICT will leave substantive review pending.'


R_METHODS = ['initialize', 'plugin/install', 'plugin/read', 'skills/list', 'hooks/list', 'thread/start', 'turn/start']


R_EXEC_IDS = ['dg17_route_governor', 'dg17_route_resolver', 'dg17_route_document']


R_COLLAB_IDS = ['dg17_route_spawn', 'dg17_route_wait', 'dg17_route_close']


R_PHASES = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']


R_ALLOWED_METHODS = ['skills/changed', 'remoteControl/status/changed', 'warning', 'thread/started', 'thread/status/changed', 'thread/tokenUsage/updated', 'turn/started', 'turn/completed', 'item/started', 'item/completed', 'item/commandExecution/outputDelta', 'item/agentMessage/delta']


def r_strings(value):
    pending = [value]; count = 0
    while pending:
        node = pending.pop(); count += 1
        r_need(count <= 65536, 'ROUTE_STRING_WALK_BOUND')
        if type(node) is str:
            yield node
        elif type(node) is dict:
            pending.extend(node.values())
        elif type(node) is list:
            pending.extend(node)


def r_identity(value):
    r_need(type(value) is str and re.fullmatch('[A-Za-z0-9_-]{1,128}', value) is not None, 'ROUTE_NATIVE_IDENTITY')
    return value


def r_fixed_path(value):
    r_need(type(value) is str and 1 <= len(value.encode()) <= 4096 and value.startswith('/') and
           not any(part in ('', '.', '..') for part in value[1:].split('/')) and
           '\x00' not in value and '\n' not in value and '\r' not in value and "'" not in value, 'ROUTE_FIXED_PHYSICAL_PATH')
    return value



AUDIT_OBJECT = 'HISTORICAL_COMPOSITION_DRAFT03_WITH_WINDOWS_STAGE_ADDENDUM_01'
SELECTION_PINS = {'REVIEW_PACKET_INDEX.json': {'path': 'REVIEW_PACKET_INDEX.json', 'bytes': 6499, 'sha256': '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347', 'file_type': 'regular', 'mode_octal': '0644'}, 'SOURCE_BINDING.json': {'path': 'SOURCE_BINDING.json', 'bytes': 34822, 'sha256': '73e8e26cc7411cb84e460cfdbad704087004279d59dd4c168c704027dea48342', 'file_type': 'regular', 'mode_octal': '0644'}, 'PROSPECTIVE_SELECTION.json': {'path': 'PROSPECTIVE_SELECTION.json', 'bytes': 7216, 'sha256': '2c9956d3425884a3eb9e8ae78ee6933c0d16342d44baf39e23aa82ac0b1c792f', 'file_type': 'regular', 'mode_octal': '0644'}, 'OWNER_BINDING.json': {'path': 'OWNER_BINDING.json', 'bytes': 5373, 'sha256': 'dd06fa8a644b61a0f11323beb53a50e988dabddebe89e5a7e9ab17f9e6e45e90', 'file_type': 'regular', 'mode_octal': '0644'}}
DRIVER_APPLICABILITY = {'admission_limit': 'This clarification grants no native route, fresh context or operation admission and establishes no satisfaction, waiver or retirement of the original review obligation; all other owner-binding limits remain applicable.', 'fields_scoped': ['scripted_nonverdict_only', 'substantive_assessment_performed', 'review_obligation_satisfied'], 'interpretation': 'The historical deterministic driver is limited to scripted NONVERDICT and cannot perform substantive assessment or satisfy the substantive review obligation.', 'separately_commissioned_substantive_reviewer': 'This historical driver ceiling does not restrict the separately commissioned substantive reviewer from returning any disposition in allowed_dispositions: PASS, NEEDS_REVISION or NONVERDICT.', 'subject': 'HISTORICAL_DETERMINISTIC_NATIVE_ROUTING_DRIVER_FOR_ORIGINAL14_CURRENT_COMPOSITION_DRAFT03', 'temporal_scope': 'Retained historical driver capability ceiling only; these three fields do not describe or admit any present or future reviewer execution.'}
PACKET02_LINEAGE = {'selection_metadata': {'REVIEW_PACKET_INDEX.json': {'path': 'REVIEW_PACKET_INDEX.json', 'bytes': 6499, 'sha256': '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347', 'file_type': 'regular', 'mode_octal': '0644'}, 'SOURCE_BINDING.json': {'path': 'SOURCE_BINDING.json', 'bytes': 34822, 'sha256': '73e8e26cc7411cb84e460cfdbad704087004279d59dd4c168c704027dea48342', 'file_type': 'regular', 'mode_octal': '0644'}, 'PROSPECTIVE_SELECTION.json': {'path': 'PROSPECTIVE_SELECTION.json', 'bytes': 7216, 'sha256': '2c9956d3425884a3eb9e8ae78ee6933c0d16342d44baf39e23aa82ac0b1c792f', 'file_type': 'regular', 'mode_octal': '0644'}, 'OWNER_BINDING.json': {'path': 'OWNER_BINDING.json', 'bytes': 5373, 'sha256': 'dd06fa8a644b61a0f11323beb53a50e988dabddebe89e5a7e9ab17f9e6e45e90', 'file_type': 'regular', 'mode_octal': '0644'}}, 'source_data_selection_only': True, 'native_launch_authority': False}

def r_selection_metadata(raws, index):
    r_need(type(raws) is dict and set(raws) == set(SELECTION_PINS), "SELECTION_METADATA_POPULATION")
    docs = {}
    for name, pin in SELECTION_PINS.items():
        raw = raws[name]
        r_need(type(raw) is bytes and len(raw) == pin["bytes"] and r_hash(raw) == pin["sha256"], "SELECTION_METADATA_PIN")
        docs[name] = r_json(raw)
    received_index = r_index_document(raws["REVIEW_PACKET_INDEX.json"])
    r_need(r_exact(received_index, index), "SELECTION_INDEX_JOIN")
    owner, source, selection = (docs[name] for name in ("OWNER_BINDING.json", "SOURCE_BINDING.json", "PROSPECTIVE_SELECTION.json"))
    r_need(all(doc.get("audit_object") == AUDIT_OBJECT and doc.get("global_current_acceptance_count") is None
             and doc.get("native_execution") is False and doc.get("new_original_awards") == [] for doc in docs.values()), "SELECTION_SUBJECT_CEILING")
    r_need(owner["review_packet_member_count"] == source["member_count"] == 20
         and owner["review_packet_total_bytes"] == 1356110
         and owner["read_boundary"] == [row["path"] for row in index["members"]]
         and owner["selection_metadata_boundary"] == ["REVIEW_PACKET_INDEX.json", "SOURCE_BINDING.json", "PROSPECTIVE_SELECTION.json", "OWNER_BINDING.json"], "SELECTION_OWNER_POPULATION")
    for doc in (owner, source, selection):
        r_need(r_exact(doc["review_packet_index"], SELECTION_PINS["REVIEW_PACKET_INDEX.json"]), "SELECTION_INDEX_BINDING")
    r_need(r_exact(owner["source_binding"], SELECTION_PINS["SOURCE_BINDING.json"])
         and r_exact(selection["source_binding"], SELECTION_PINS["SOURCE_BINDING.json"])
         and r_exact(owner["prospective_selection"], SELECTION_PINS["PROSPECTIVE_SELECTION.json"]), "SELECTION_METADATA_JOIN")
    rows = source["members"]
    r_need(type(rows) is list and len(rows) == 20 and len({r["packet_member"] for r in rows}) == 20, "SELECTION_SOURCE_POPULATION")
    by_path = {r["path"]:r for r in index["members"]}
    roles = {}
    for row in rows:
        r_need(row["packet_member"] in by_path, "SELECTION_SOURCE_MEMBER")
        expected = by_path[row["packet_member"]]
        r_need(all(r_exact(row["exact_source"][key], expected[key]) for key in ("bytes", "sha256", "file_type", "mode_octal")), "SELECTION_SOURCE_BODY_JOIN")
        roles[row["source_role"]] = roles.get(row["source_role"],0)+1
    r_need(roles == {"original14":14,"reviewed_sidecar":1,"draft02_preservation_predecessor":2,"G03_source_evidence":3}, "SELECTION_SOURCE_ROLES")
    precedence = selection["consumption_precedence"]
    r_need([r["order"] for r in precedence] == [1,2,3,4]
         and [r["role"] for r in precedence] == ["historical_base","bounded_stage_projection","draft02_preservation_predecessors","G03_source_evidence"], "SELECTION_PRECEDENCE")
    targets = precedence[1]["targets"]
    r_need([(r["packet_member"],r["json_pointer"],r["selected_projection_member"],r["selected_projection_pointer"]) for r in targets] == [
        ("composition/HOST_MAP.json","/windows_shared_finding","addenda/WINDOWS_STAGE_ADDENDUM.json","/current_stage_projection"),
        ("composition/ORIGINAL95_SOURCE_MAP.json","/check_registry/DG18_WINDOWS_ARTIFACT_RECEIVING","addenda/WINDOWS_STAGE_ADDENDUM.json","/current_stage_projection")], "SELECTION_STAGE_TARGETS")
    r_need(all(all(r_exact(row[key],by_path[row["packet_member"]][key]) for key in ("bytes","sha256")) for row in targets)
         and r_exact(selection["selected_stage_projection"],by_path["addenda/WINDOWS_STAGE_ADDENDUM.json"]), "SELECTION_STAGE_BODY_JOIN")
    r_need(r_exact(owner["driver_ceiling"]["applicability"], DRIVER_APPLICABILITY)
         and owner["driver_ceiling"]["scripted_nonverdict_only"] is True
         and owner["driver_ceiling"]["substantive_assessment_performed"] is False
         and owner["driver_ceiling"]["review_obligation_satisfied"] is False, "SELECTION_DRIVER_APPLICABILITY")
    return {"selection_metadata":SELECTION_PINS,"selection_metadata_member_count":4,
            "consumption_precedence":precedence,"driver_applicability":DRIVER_APPLICABILITY,
            "transport_modes":{"origin_modes":"EXACT_RECEIVED_DESCRIPTORS","public_body_and_metadata":"0644","private_body_and_metadata":"0600"},
            "instructions_inside_data":selection["instructions_inside_data"],
            "common_temporal_stage_interpretation":selection["common_temporal_stage_interpretation"],
            "historical_label_preservation":selection["historical_label_preservation"]}

def r_exact(left,right):return r_compact(left)==r_compact(right)

def r_index_document(raw):
    r_need(type(raw) is bytes and len(raw)==6499 and r_hash(raw)==R_INDEX_SHA,"ROUTE_INDEX_PIN")
    index=r_json(raw,8192)
    r_need(index["audit_object"]==AUDIT_OBJECT and index["member_count"]==20 and index["total_bytes"]==1356110
           and len(index["members"])==20 and len({r["path"] for r in index["members"]})==20
           and sum(r["bytes"] for r in index["members"])==1356110,"ROUTE_INDEX_POPULATION")
    return index


def r_nonverdict():
    value = {'schema':'dg17.codex.routing.nonverdict.v1', 'audit_object':AUDIT_OBJECT,
             'claims':[{'claim':claim,'disposition':'NONVERDICT'} for claim in R_CLAIMS],
             'authority':'NONE', 'reason':'DETERMINISTIC_DRIVER_NO_SUBSTANTIVE_ASSESSMENT',
             'review_obligation_satisfied':False, 'substantive_assessment_performed':False,
             'review_packet_index_sha256':R_INDEX_SHA}
    raw = r_compact(value)
    r_need(len(raw) == 718 and r_hash(raw) == R_NONVERDICT_SHA, 'ROUTE_NONVERDICT_LITERAL_BINDING')
    return raw.decode('ascii')


def r_owner(raw, expected_sha, index):
    r_index_document(r_pretty(index))
    r_need(type(expected_sha) is str and re.fullmatch('[0-9a-f]{64}', expected_sha) is not None and r_hash(raw) == expected_sha, 'ROUTE_OWNER_BYTES_BINDING')
    owner = r_json(raw, 4096)
    keys = {'schema','operation','root_binding_id','route_owner','selected_child','review_required','claims','read_boundary','allowed_dispositions','independence','authority_ceiling','driver_ceiling','review_packet_index_sha256','review_packet_member_count','review_packet_total_bytes','audit_object','packet02_lineage'}
    r_need(type(owner) is dict and set(owner) == keys, 'ROUTE_OWNER_CLOSED_FIELDS')
    r_need(owner['schema'] == 'dg17.codex.routing.owner-binding.v3' and owner['operation'] == 'ONE_CANONICAL_AUDIT_ASSESS_NATIVE_ROUTE_NONVERDICT'
           and type(owner['root_binding_id']) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,95}',owner['root_binding_id']) is not None
           and owner['route_owner'] == 'implementaudit' and owner['selected_child'] == 'audit-assess'
           and owner['review_required'] is True and owner['claims'] == R_CLAIMS and owner['read_boundary'] == [row['path'] for row in index['members']]
           and owner['allowed_dispositions'] == ['PASS','NEEDS_REVISION','NONVERDICT'], 'ROUTE_OWNER_SELECTION')
    r_need(r_compact(owner['authority_ceiling']) == r_compact({k:'NONE' for k in ('mutation','release','closure','lifecycle','currentness','authority')})
           and r_compact(owner['driver_ceiling']) == r_compact({'scripted_nonverdict_only':True,'substantive_assessment_performed':False,'review_obligation_satisfied':False,'applicability':DRIVER_APPLICABILITY})
           and r_compact(owner['independence']) == r_compact({'fresh_native_context_required':True,'fork_context':False,'authoring_notes_allowed':False,'other_composition_review_outputs_allowed':False,'prior_component_evidence_as_target_data':True}), 'ROUTE_OWNER_AUTHORITY_CEILING')
    r_need(owner['review_packet_index_sha256'] == R_INDEX_SHA and type(owner['review_packet_member_count']) is int and owner['review_packet_member_count'] == 20
           and type(owner['review_packet_total_bytes']) is int and owner['review_packet_total_bytes'] == 1356110
           and owner['audit_object'] == AUDIT_OBJECT and r_exact(owner['packet02_lineage'],PACKET02_LINEAGE), 'ROUTE_OWNER_REVIEW_OBJECT')
    return owner


def r_context(episode, review_root, owner_raw, owner_sha, index_raw, docs, metadata_raws, metadata_root):
    episode = r_fixed_path(episode); review_root = r_fixed_path(review_root)
    r_need(r_hash(index_raw) == R_INDEX_SHA and len(index_raw) == 6499, 'ROUTE_REVIEW_INDEX_BYTES')
    index = r_index_document(index_raw); owner = r_owner(owner_raw, owner_sha, index)
    selection=r_selection_metadata(metadata_raws,index);metadata_root=r_fixed_path(metadata_root)
    r_need(type(docs) is dict and set(docs) == {'governor','resolver','child'}, 'ROUTE_DOCUMENT_POPULATION')
    for name, size, sha in (('governor',21257,R_GOV_SHA),('resolver',5178,R_RESOLVER_SHA),('child',2039,R_CHILD_SHA)):
        r_need(type(docs[name]) is bytes and len(docs[name]) == size and r_hash(docs[name]) == sha, 'ROUTE_DOCUMENT_BYTES')
        docs[name].decode('utf-8','strict')
    r_need(r_hash(docs['governor'][:8000]) == R_PREFIX_SHA, 'ROUTE_PREFIX_BYTES')
    root = episode+'/canonical-routing-payloads/canonical'; home = root+'/home'
    effective = home+'/plugins/cache/implementaudit/implementaudit/0.4.0'
    ctx = {'episode':episode,'root':root,'home':home,'cwd':root+'/neutral','tmp':root+'/tmp','image':root+'/source-package',
           'effective':effective,'governor':effective+'/skills/implementaudit/SKILL.md',
           'resolver':effective+'/skills/implementaudit/scripts/resolve-internal-skill.py',
           'child':effective+'/skills/audit-assess/SKILL.md','governor_name':'implementaudit:implementaudit',
           'child_name':'implementaudit:audit-assess','owner':owner,'owner_sha':owner_sha,'index':index,'review_root':review_root}
    envelope = {'schema':'dg17.codex.routing.native-input.v2','operation':'ONE_CANONICAL_AUDIT_ASSESS_NATIVE_ROUTE_NONVERDICT',
                'owner_selection':owner,'owner_selection_sha256':owner_sha,'review_packet_index':index,
                'review_packet_root':review_root,'selection_metadata_root':metadata_root,'selection_contract':selection,'authority_gain':'NONE','substantive_review':'NOT_PERFORMED_BY_SCRIPTED_DRIVER'}
    ctx['envelope'] = envelope; ctx['text'] = 'DG17_CANONICAL_ROUTING_INPUT\n'+r_compact(envelope).decode('ascii')
    ctx['nonverdict'] = r_nonverdict()
    r_need(all(docs[key].decode() not in text for text in r_strings(envelope) for key in ('governor','child')), 'ROUTE_ENVELOPE_DOCUMENT_INJECTION')
    return ctx


def r_exec_args(ctx, ordinal):
    r_need(type(ordinal) is int and ordinal in (0,1,2), 'ROUTE_EXEC_ORDINAL')
    cmd = ("/usr/bin/cat -- '"+ctx['governor']+"'" if ordinal == 0 else
           "/usr/bin/python3 -I -B '"+ctx['resolver']+"' --governor '"+ctx['governor']+"' --child audit-assess" if ordinal == 1 else
           "/usr/bin/cat -- '"+ctx['child']+"'")
    return {'cmd':cmd,'workdir':ctx['cwd'],'shell':'/usr/bin/bash','login':False,'tty':False,
            'yield_time_ms':30000,'max_output_tokens':8192,'sandbox_permissions':'use_default'}


def r_spawn_args(ctx):
    return {'fork_context':False,'items':[{'type':'text','text':ctx['text']}, {'type':'skill','name':ctx['child_name'],'path':ctx['child']}]}


def r_skill_fragment(name, path, body, prefix):
    raw = body[:8000] if prefix else body
    return '<skill>\n<name>'+name+'</name>\n<path>'+path+'</path>\n'+raw.decode('utf-8','strict')+'\n</skill>'


def r_user_span(request, literal):
    items = request.get('input'); matches = []
    r_need(type(items) is list and 1 <= len(items) <= 256, 'ROUTE_INPUT_POPULATION')
    for i,item in enumerate(items):
        if type(item) is not dict or item.get('role') != 'user' or item.get('type','message') != 'message':
            continue
        blocks = item.get('content')
        if type(blocks) is not list:
            continue
        for j,block in enumerate(blocks):
            if type(block) is dict and block.get('type') == 'input_text' and type(block.get('text')) is str:
                text = block['text']; start = text.find(literal)
                if start >= 0:
                    r_need(text.count(literal) == 1, 'ROUTE_USER_SPAN_DUPLICATED')
                    start = len(text[:start].encode())
                    matches.append({'input_index':i,'content_index':j,'start_bytes':start,'end_bytes':start+len(literal.encode()),'bytes':len(literal.encode()),'sha256':r_hash(literal.encode())})
    r_need(len(matches) == 1 and sum(s.count(literal) for s in r_strings(request)) == 1, 'ROUTE_USER_SPAN_ORIGIN')
    return matches[0]


def r_output(text, expected):
    r_need(type(text) is str and len(text.encode()) <= 32768, 'ROUTE_NATIVE_OUTPUT_BOUND')
    pattern = (r'(?:Chunk ID: [A-Za-z0-9_-]{1,64}\n)?Wall time: ((?:0|[1-9][0-9]{0,2})\.[0-9]{4}) seconds\n'
               r'Process exited with code 0\n(?:Original token count: (0|[1-9][0-9]{0,8})\n)?Output:\n')
    match = re.match(pattern,text)
    r_need(match is not None and 0 <= float(match.group(1)) <= 90, 'ROUTE_NATIVE_OUTPUT_ENVELOPE')
    r_need(text[match.end():].encode() == expected, 'ROUTE_NATIVE_OUTPUT_EXACT_BYTES')
    offset = len(text[:match.end()].encode())
    return {'header_bytes':offset,'output_start_bytes':offset,'output_end_bytes':offset+len(expected),'output_bytes':len(expected),
            'output_sha256':r_hash(expected),'exit_code':0,'live_session':False,'truncation_observed':False}


def r_header(header, body, port):
    r_need(type(header) is bytes and len(header) <= 32768 and header.endswith(b'\r\n\r\n'), 'ROUTE_HTTP_HEADER_BOUND')
    try:
        lines = header[:-4].decode('ascii','strict').split('\r\n')
    except UnicodeError:
        raise RouteRefusal('ROUTE_HTTP_HEADER_ASCII') from None
    r_need(lines[0] == 'POST /v1/responses HTTP/1.1', 'ROUTE_HTTP_ENDPOINT')
    fields = {}
    for line in lines[1:]:
        r_need(line and not line[0].isspace() and ':' in line, 'ROUTE_HTTP_HEADER_SYNTAX')
        name,value = line.split(':',1); name = name.lower(); value = value.strip()
        r_need(re.fullmatch('[a-z0-9-]+',name) is not None and name not in fields and len(value) <= 8192, 'ROUTE_HTTP_HEADER_KEY')
        fields[name] = value
    r_need(fields.get('host') == '127.0.0.1:'+str(port) and fields.get('content-type') == 'application/json'
           and not set(fields)&{'authorization','proxy-authorization','cookie','transfer-encoding','content-encoding','expect'}, 'ROUTE_HTTP_AUTH_OR_TRANSPORT')
    size = fields.get('content-length','')
    r_need(re.fullmatch('[0-9]{1,8}',size) is not None and int(size) == len(body) and 0 < len(body) <= 2097152, 'ROUTE_HTTP_BODY_SIZE')
    r_identity(fields.get('thread-id')); r_need(fields.get('x-client-request-id') == fields['thread-id'], 'ROUTE_HTTP_THREAD_HEADER_JOIN')
    return fields


def r_advertisement(tools):
    """Receive the selected V1 surface; other advertised tools gain no authority."""
    r_need(type(tools) is list and 1 <= len(tools) <= 128, 'ROUTE_TOOL_ADVERTISEMENT_POPULATION')
    r_need(not any(type(t) is dict and t.get('name') in ('spawn_agent','send_input','resume_agent','wait_agent','close_agent','multi_agent_v2','list_agents','followup_task','interrupt_agent') for t in tools), 'ROUTE_V2_OR_UNNAMESPACED_COLLAB')
    exec_rows = [t for t in tools if type(t) is dict and t.get('name') == 'exec_command']
    groups = [t for t in tools if type(t) is dict and t.get('name') == 'multi_agent_v1']
    r_need(len(exec_rows) == len(groups) == 1, 'ROUTE_SELECTED_TOOL_NAMESPACE')
    group = groups[0]
    r_need(set(group) == {'type','name','description','tools'} and group['type'] == 'namespace'
           and type(group['description']) is str and len(group['description'].encode()) <= 8192
           and type(group['tools']) is list and len(group['tools']) == 5 and {row.get('name') for row in group['tools'] if type(row) is dict} == {'spawn_agent','send_input','resume_agent','wait_agent','close_agent'}, 'ROUTE_V1_NAMESPACE_PROFILE')
    wanted = {'spawn_agent':{'items':'array','fork_context':'boolean'}, 'wait_agent':{'targets':'array','timeout_ms':'number'}, 'close_agent':{'target':'string'}}
    selected = {}
    for name, kinds in wanted.items():
        rows = [t for t in group['tools'] if type(t) is dict and t.get('name') == name]
        r_need(len(rows) == 1, 'ROUTE_V1_FUNCTION_POPULATION'); row = rows[0]
        r_need(row.get('type') == 'function' and row.get('strict') is False and type(row.get('description')) is str
               and len(row['description'].encode()) <= 32768 and type(row.get('parameters')) is dict, 'ROUTE_V1_FUNCTION_PROFILE')
        p = row['parameters']; props = p.get('properties')
        r_need(p.get('type') == 'object' and p.get('additionalProperties') is False and type(props) is dict
               and all(type(props.get(k)) is dict and props[k].get('type') == v for k,v in kinds.items()), 'ROUTE_V1_PARAMETER_PROFILE')
        if name == 'spawn_agent':
            r_need(set(props) <= {'message','items','agent_type','fork_context','model','reasoning_effort'} and p.get('required',[]) == [], 'ROUTE_V1_SPAWN_PROFILE')
        elif name == 'wait_agent':
            r_need(set(props) == set(kinds) and p.get('required') == ['targets'] and props['targets'].get('items') == {'type':'string'}, 'ROUTE_V1_WAIT_PROFILE')
        else:
            r_need(set(props) == set(kinds) and p.get('required') == ['target'], 'ROUTE_V1_CLOSE_PROFILE')
        selected[name] = r_hash(r_pretty(row))
    exe = exec_rows[0]; props = exe.get('parameters',{}).get('properties')
    r_need(exe.get('type') == 'function' and exe.get('strict') is False and type(props) is dict
           and set(props) == {'cmd','workdir','shell','login','tty','yield_time_ms','max_output_tokens','sandbox_permissions','justification','prefix_rule'}
           and exe['parameters'].get('required') == ['cmd'] and exe['parameters'].get('additionalProperties') is False, 'ROUTE_EXEC_ADVERTISEMENT_PROFILE')
    return {'v1_namespace_received':True,'exec_command_received':True,'advertised_tool_count':len(tools),
            'advertised_tools_sha256':r_hash(r_pretty(tools)),'selected_v1_functions_sha256':selected}


def r_response_items(ctx, phase, child):
    def call(name, call_id, args, namespace=None):
        row = {'type':'function_call','id':'fc_'+phase,'call_id':call_id,'name':name,'arguments':r_compact(args).decode(),'status':'completed'}
        if namespace is not None:
            row['namespace'] = namespace
        return row
    def message(identifier, text, channel):
        return {'type':'message','id':identifier,'status':'completed','role':'assistant','phase':channel,
                'content':[{'type':'output_text','text':text,'annotations':[]}]}
    if phase in ('P1','P2','P3'):
        i = int(phase[1])-1
        return [call('exec_command',R_EXEC_IDS[i],r_exec_args(ctx,i))]
    if phase == 'P4':
        return [message('msg_dg17_announcement',R_ANNOUNCEMENT,'commentary'),call('spawn_agent',R_COLLAB_IDS[0],r_spawn_args(ctx),'multi_agent_v1')]
    if phase == 'P5':
        return [call('wait_agent',R_COLLAB_IDS[1],{'targets':[r_identity(child)],'timeout_ms':10000},'multi_agent_v1')]
    if phase == 'P6':
        return [call('close_agent',R_COLLAB_IDS[2],{'target':r_identity(child)},'multi_agent_v1')]
    r_need(phase in ('P7','C1'), 'ROUTE_RESPONSE_PHASE')
    return [message('msg_dg17_'+phase,ctx['nonverdict'],'final_answer')]


def r_response_bytes(ctx, phase, child, docs):
    items = r_response_items(ctx,phase,child)
    for text in r_strings(items):
        r_need(all(docs[k].decode() not in text for k in ('governor','child')), 'ROUTE_RESPONSE_DOCUMENT_INJECTION')
    response_id = 'resp_dg17_route_'+phase
    events = [('response.created',{'type':'response.created','response':{'id':response_id}})]
    events += [('response.output_item.done',{'type':'response.output_item.done','output_index':i,'item':item}) for i,item in enumerate(items)]
    events += [('response.completed',{'type':'response.completed','response':{'id':response_id,'status':'completed','output':items,'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}})]
    sse = b''.join(b'event: '+event.encode()+b'\ndata: '+r_compact(value)+b'\n\n' for event,value in events)
    r_need(len(sse) <= 65536, 'ROUTE_SSE_PAYLOAD_BOUND')
    return b'HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nConnection: close\r\nContent-Length: '+str(len(sse)).encode()+b'\r\n\r\n'+sse


def r_history(request, ctx, phase, child, docs):
    items = request['input']; n = int(phase[1]) if phase != 'C1' else 1
    r_need(all(type(row) is dict and row.get('type') in (None,'message','function_call','function_call_output') and (row.get('type') is not None or row.get('role') in ('system','developer','user','assistant')) for row in items), 'ROUTE_RESPONSES_ITEM_PROFILE')
    calls = [row for row in items if type(row) is dict and row.get('type') == 'function_call']
    outputs = [row for row in items if type(row) is dict and row.get('type') == 'function_call_output']
    if phase == 'C1':
        r_need(not calls and not outputs and not any(row.get('role') == 'assistant' for row in items), 'ROUTE_CHILD_PARENT_HISTORY')
        r_need(all(docs['governor'].decode() not in s and R_ANNOUNCEMENT not in s for s in r_strings(request)), 'ROUTE_CHILD_FORKED_HISTORY')
        fragment = r_skill_fragment(ctx['child_name'],ctx['child'],docs['child'],False)
        span = r_user_span(request,fragment); r_user_span(request,ctx['text'])
        r_need(sum(s.count(docs['child'].decode()) for s in r_strings(request)) == 1, 'ROUTE_CHILD_TYPED_BODY_ORIGIN')
        return {'phase':phase,'typed_child':span}
    expected = []
    for prior in R_PHASES[:n-1]:
        expected.extend(item for item in r_response_items(ctx,prior,child) if item['type'] == 'function_call')
    r_need(len(calls) == len(outputs) == len(expected), 'ROUTE_HISTORY_CALL_POPULATION')
    received = {}
    for position,(actual,wanted) in enumerate(zip(calls,expected)):
        r_need(items.index(actual) < items.index(outputs[position]) and (position == 0 or items.index(outputs[position-1]) < items.index(actual)), 'ROUTE_NATIVE_HISTORY_ORDER')
        r_need(actual.get('call_id') == wanted['call_id'] and actual.get('name') == wanted['name']
               and actual.get('namespace') == wanted.get('namespace') and type(actual.get('arguments')) is str
               and r_compact(r_json(actual['arguments'].encode(),32768)) == r_compact(r_json(wanted['arguments'].encode(),32768)), 'ROUTE_HISTORY_FIXED_CALL')
    for output,wanted in zip(outputs,expected):
        r_need(output.get('call_id') == wanted['call_id'] and type(output.get('output')) is str and output['call_id'] not in received, 'ROUTE_HISTORY_OUTPUT_IDENTITY')
        received[output['call_id']] = output['output']
    projected = {'phase':phase}
    r_user_span(request,r_skill_fragment(ctx['governor_name'],ctx['governor'],docs['governor'],True))
    announcements = [block.get('text') for row in items if row.get('role') == 'assistant' for block in row.get('content',[]) if type(block) is dict and block.get('text') == R_ANNOUNCEMENT]
    r_need(len(announcements) == (1 if n >= 5 else 0), 'ROUTE_ANNOUNCEMENT_HISTORY')
    if n == 1:
        projected['typed_governor'] = r_user_span(request,r_skill_fragment(ctx['governor_name'],ctx['governor'],docs['governor'],True))
        r_need(all(docs['governor'].decode() not in s and docs['child'].decode() not in s for s in r_strings(request)), 'ROUTE_INITIAL_FULL_DOCUMENT_INJECTION')
    r_user_span(request,ctx['text'])
    for i,raw in enumerate((docs['governor'],(ctx['child']+'\n').encode(),docs['child'])):
        if n > i+1:
            projected[['governor_return','resolver_return','child_return'][i]] = r_output(received[R_EXEC_IDS[i]],raw)
    if n >= 5:
        spawn = r_json(received[R_COLLAB_IDS[0]].encode(),32768)
        r_need(type(spawn) is dict and set(spawn) == {'agent_id','nickname'} and spawn['agent_id'] == child
               and (spawn['nickname'] is None or type(spawn['nickname']) is str and len(spawn['nickname'].encode()) <= 1024), 'ROUTE_SPAWN_RESULT')
        projected['spawn_result'] = {'child_id_sha256':r_hash(child.encode()),'nickname_present':spawn['nickname'] is not None}
    if n >= 6:
        wait = r_json(received[R_COLLAB_IDS[1]].encode(),32768)
        r_need(r_compact(wait) == r_compact({'status':{child:{'completed':ctx['nonverdict']}},'timed_out':False}), 'ROUTE_WAIT_FIRST_RETURN')
        projected['wait_result'] = {'first_return_sha256':R_NONVERDICT_SHA,'timed_out':False}
    if n >= 7:
        close = r_json(received[R_COLLAB_IDS[2]].encode(),32768)
        r_need(r_compact(close) == r_compact({'previous_status':{'completed':ctx['nonverdict']}}), 'ROUTE_CLOSE_PREVIOUS_STATUS')
        projected['close_result'] = {'first_return_sha256':R_NONVERDICT_SHA,'completed_before_close':True}
    # The only complete bodies in a parent request must be the matched native outputs.
    for key, threshold in (('governor',2),('child',4)):
        r_need(sum(s.count(docs[key].decode()) for s in r_strings(request)) == (1 if n >= threshold else 0), 'ROUTE_NATIVE_BODY_PROVENANCE')
    return projected


def r_http_receive(retained, ctx, docs, parent, port):
    """Data-only raw HTTP join. Native identity/events are independently joined later."""
    r_identity(parent); r_need(type(port) is int and 1024 <= port <= 65535, 'ROUTE_PROVIDER_PORT')
    r_need(type(retained) is list and len(retained) == 8, 'ROUTE_PROVIDER_REQUEST_POPULATION')
    parent_count = 0; child = None; order = []; projections = []; total = 0; advertisement = None
    # Learn the child's actual spawn result from P5, rather than assuming a provider assertion.
    for entry in retained:
        r_need(type(entry) is dict and set(entry) == {'header','body','response'}, 'ROUTE_HTTP_RETAINED_SHAPE')
        fields = r_header(entry['header'],entry['body'],port)
        if fields['thread-id'] == parent:
            req = r_json(entry['body']); inp = req.get('input',[])
            if type(inp) is list:
                outputs = [r for r in inp if type(r) is dict and r.get('type') == 'function_call_output' and r.get('call_id') == R_COLLAB_IDS[0]]
                if outputs:
                    r_need(len(outputs) == 1 and type(outputs[0].get('output')) is str, 'ROUTE_SPAWN_OUTPUT_POPULATION')
                    result = r_json(outputs[0]['output'].encode(),32768)
                    r_need(type(result) is dict and set(result) == {'agent_id','nickname'}, 'ROUTE_SPAWN_OUTPUT_FIELDS')
                    actual = r_identity(result['agent_id']); r_need(actual != parent and (child is None or child == actual), 'ROUTE_CHILD_IDENTITY_COLLISION'); child = actual
    r_need(child is not None, 'ROUTE_NATIVE_CHILD_IDENTITY_UNRECEIVED')
    for ordinal,entry in enumerate(retained,1):
        fields = r_header(entry['header'],entry['body'],port); total += len(entry['header'])+len(entry['body'])
        r_need(total <= 17039360, 'ROUTE_HTTP_AGGREGATE_BOUND')
        if fields['thread-id'] == parent:
            parent_count += 1; r_need(parent_count <= 7 and fields.get('x-openai-subagent') is None, 'ROUTE_PARENT_HTTP_IDENTITY')
            phase = 'P'+str(parent_count)
        else:
            r_need(fields['thread-id'] == child and fields.get('x-openai-subagent') == 'collab_spawn'
                   and 'C1' not in order and ordinal in (5,6) and parent_count in (4,5), 'ROUTE_FRESH_CHILD_HTTP_IDENTITY')
            phase = 'C1'
        req = r_json(entry['body']); r_need(type(req) is dict and req.get('model') == R_MODEL and req.get('stream') is True, 'ROUTE_REQUEST_MODEL_STREAM')
        if phase == 'P1':
            advertisement = r_advertisement(req.get('tools'))
        projection = r_history(req,ctx,phase,child,docs)
        r_need(entry['response'] == r_response_bytes(ctx,phase,child,docs), 'ROUTE_FIXED_SENT_RESPONSE')
        order.append(phase); projections.append(projection)
    r_need(order in (['P1','P2','P3','P4','C1','P5','P6','P7'],['P1','P2','P3','P4','P5','C1','P6','P7']), 'ROUTE_PROVIDER_PHASE_ORDER')
    return {'parent_id':parent,'child_id':child,'request_order':order,'phase_projections':projections,
            'parent_requests':7,'child_requests':1,'request_headers_match_thread':True,'advertisement':advertisement}


def r_expected_sends(ctx, parent):
    r_identity(parent)
    return [
        {'id':1,'method':'initialize','params':{'clientInfo':{'name':'dg17_package_content','version':'1.0.0'},'capabilities':{'experimentalApi':True}}},
        {'method':'initialized'},
        {'id':2,'method':'plugin/install','params':{'pluginName':'implementaudit','marketplacePath':ctx['image']+'/.claude-plugin/marketplace.json'}},
        {'id':3,'method':'plugin/read','params':{'pluginName':'implementaudit','marketplacePath':ctx['image']+'/.claude-plugin/marketplace.json'}},
        {'id':4,'method':'skills/list','params':{'cwds':[ctx['cwd']],'forceReload':True}},
        {'id':5,'method':'hooks/list','params':{'cwds':[ctx['cwd']]}},
        {'id':6,'method':'thread/start','params':{'cwd':ctx['cwd'],'approvalPolicy':'never','approvalsReviewer':'user','sandbox':'read-only','ephemeral':True,'model':R_MODEL,'modelProvider':'dg17_loopback'}},
        {'id':7,'method':'turn/start','params':{'threadId':parent,'input':[{'type':'text','text':ctx['text'],'text_elements':[]},{'type':'skill','name':ctx['governor_name'],'path':ctx['governor']}]}}
    ]


def r_command(item, ctx, docs, complete):
    r_need(type(item) is dict and item.get('type') == 'commandExecution' and item.get('id') in R_EXEC_IDS, 'ROUTE_NATIVE_COMMAND_ID')
    ordinal = R_EXEC_IDS.index(item['id'])
    try:
        actual = shlex.split(item.get('command',''),posix=True)
    except ValueError:
        raise RouteRefusal('ROUTE_NATIVE_COMMAND_DISPLAY') from None
    r_need(item.get('cwd') == ctx['cwd'] and actual == ['/usr/bin/bash','-c',r_exec_args(ctx,ordinal)['cmd']], 'ROUTE_NATIVE_FIXED_COMMAND')
    raw = (docs['governor'],(ctx['child']+'\n').encode(),docs['child'])[ordinal]
    if complete:
        r_need(item.get('status') == 'completed' and type(item.get('exitCode')) is int and item['exitCode'] == 0, 'ROUTE_NATIVE_COMMAND_COMPLETION')
        aggregate = item.get('aggregatedOutput')
        r_need(aggregate is None or type(aggregate) is str and aggregate.encode() == raw, 'ROUTE_NATIVE_COMMAND_AGGREGATE')
    return ordinal


def r_collab(item, ctx, parent, child, complete):
    fields = {'type','id','tool','status','senderThreadId','receiverThreadIds','prompt','model','reasoningEffort','agentsStates'}
    r_need(type(item) is dict and set(item) == fields and item['type'] == 'collabAgentToolCall'
           and item['id'] in R_COLLAB_IDS and item['senderThreadId'] == parent, 'ROUTE_COLLAB_CLOSED_IDENTITY')
    ordinal = R_COLLAB_IDS.index(item['id']); tool = ('spawnAgent','wait','closeAgent')[ordinal]
    r_need(item['tool'] == tool and item['status'] == ('completed' if complete else 'inProgress'), 'ROUTE_COLLAB_TOOL_STATUS')
    if ordinal == 0:
        preview = ctx['text']+'\n[skill:$'+ctx['child_name']+']('+ctx['child']+')'
        r_need(item['prompt'] == preview and item['receiverThreadIds'] == ([child] if complete else []), 'ROUTE_COLLAB_SPAWN_PREVIEW')
        r_need(item['model'] == (R_MODEL if complete else '') and item['reasoningEffort'] in ('none','minimal','low','medium','high','xhigh','max'), 'ROUTE_COLLAB_INHERITED_MODEL')
        states = item['agentsStates']
        if complete:
            r_need(type(states) is dict and set(states) == {child} and type(states[child]) is dict and set(states[child]) == {'status','message'}
                   and states[child]['status'] in ('pendingInit','running','completed') and
                   (states[child]['message'] is None if states[child]['status'] != 'completed' else states[child]['message'] == ctx['nonverdict']), 'ROUTE_COLLAB_SPAWN_STATE')
        else:
            r_need(states == {}, 'ROUTE_COLLAB_SPAWN_STARTED_STATE')
    else:
        r_need(item['receiverThreadIds'] == [child] and all(item[k] is None for k in ('prompt','model','reasoningEffort')), 'ROUTE_COLLAB_TARGET_SCOPE')
        r_need(item['agentsStates'] == ({child:{'status':'completed','message':ctx['nonverdict']}} if complete else {}), 'ROUTE_COLLAB_RETURN_STATE')
    return ordinal


def r_wire_receive(raw, events, actual_sends, send_status, ctx, docs, http):
    r_need(type(raw) is bytes and len(raw) <= 2097152, 'ROUTE_NATIVE_STDOUT_BOUND')
    lines = raw.splitlines(); r_need(all(0 < len(line) <= 262144 for line in lines), 'ROUTE_NATIVE_LINE_BOUND')
    frames = [r_json(line,262144) for line in lines]
    r_need(type(events) is list and len(events) <= 1024, 'ROUTE_NATIVE_EVENT_BOUND')
    parent,child = http['parent_id'],http['child_id']; sends = r_expected_sends(ctx,parent)
    responses = {row['id']:row['result'] for row in frames if type(row) is dict and set(row) == {'id','result'} and type(row['id']) is int}
    r_need(6 in responses and 7 in responses, 'ROUTE_NATIVE_THREAD_TURN_RESPONSE')
    r_need(type(responses[6]) is dict and type(responses[6].get('thread')) is dict and responses[6]['thread'].get('id') == parent, 'ROUTE_NATIVE_PARENT_ID_JOIN')
    turn = r_identity(responses[7].get('turn',{}).get('id'))
    received = []; sent = []; seen = {}; notifications = []; warnings = []
    starts = []; completions = []; collab_starts = []; collab_completions = []; positions = {}; deltas = {k:[] for k in R_EXEC_IDS}
    parent_messages = []; child_messages = []; parent_completed = []; child_completed = []; child_turn = None
    for sequence,event in enumerate(events,1):
        r_need(type(event) is dict and set(event) == {'sequence','direction','value'} and type(event['sequence']) is int and event['sequence'] == sequence, 'ROUTE_NATIVE_EVENT_SEQUENCE')
        value = event['value']
        if event['direction'] == 'send':
            r_need(len(sent) < len(sends) and r_compact(value) == r_compact(sends[len(sent)]), 'ROUTE_NATIVE_SEND_SEQUENCE'); sent.append(value); continue
        r_need(event['direction'] == 'receive' and type(value) is dict, 'ROUTE_NATIVE_EVENT_DIRECTION'); received.append(value)
        if 'id' in value:
            r_need(set(value) == {'id','result'} and type(value['id']) is int and value['id'] not in seen and value['id'] in {v['id'] for v in sent if 'id' in v}, 'ROUTE_NATIVE_RESPONSE_ID')
            seen[value['id']] = value['result']; continue
        r_need(set(value) == {'method','params','emittedAtMs'} and type(value['emittedAtMs']) is int and 0 <= value['emittedAtMs'] <= 9223372036854775807
               and value['method'] in R_ALLOWED_METHODS and type(value['params']) is dict, 'ROUTE_NATIVE_NOTIFICATION_CLOSED')
        method,p = value['method'],value['params']; notifications.append(method)
        if method == 'skills/changed':
            r_need(p == {}, 'ROUTE_SKILLS_NOTIFICATION'); continue
        if method == 'remoteControl/status/changed':
            r_need(set(p) in ({'status','installationId','serverName'},{'status','installationId','serverName','environmentId'}) and p['status'] == 'disabled'
                   and p.get('environmentId') is None and all(type(p[k]) is str and len(p[k].encode()) <= 1024 for k in ('installationId','serverName')), 'ROUTE_REMOTE_CONTROL_NOTIFICATION'); continue
        if method == 'warning':
            message = 'Skill `'+ctx['governor_name']+'` exceeded the main prompt context limit and was truncated.'
            r_need(p == {'threadId':parent,'message':message}, 'ROUTE_NATIVE_WARNING_PROFILE'); warnings.append(r_hash(message.encode())); continue
        thread_id = p.get('threadId') if method != 'thread/started' else p.get('thread',{}).get('id')
        r_need(thread_id in (parent,child), 'ROUTE_NATIVE_THREAD_SCOPE')
        if method.startswith('item/') or method in ('turn/started','turn/completed'):
            actual_turn = p.get('turnId') if method.startswith('item/') else p.get('turn',{}).get('id')
            r_identity(actual_turn)
            if thread_id == parent:
                r_need(actual_turn == turn, 'ROUTE_NATIVE_PARENT_TURN_SCOPE')
            else:
                r_need(child_turn is None or child_turn == actual_turn, 'ROUTE_NATIVE_CHILD_TURN_COUNT'); child_turn = actual_turn
        if method in ('item/started','item/completed'):
            done = method == 'item/completed'; item = p.get('item')
            r_need(type(item) is dict and item.get('type') in ('userMessage','agentMessage','commandExecution','collabAgentToolCall'), 'ROUTE_NATIVE_ITEM_PROFILE')
            if done:
                r_need(type(p.get('completedAtMs')) is int and 0 <= p['completedAtMs'] <= 9223372036854775807, 'ROUTE_NATIVE_ITEM_TIMESTAMP')
            if item['type'] == 'commandExecution':
                r_need(thread_id == parent, 'ROUTE_CHILD_TOOL_FORBIDDEN'); ordinal = r_command(item,ctx,docs,done)
                (completions if done else starts).append(ordinal); positions[('exec_done' if done else 'exec_start',ordinal)] = sequence
            elif item['type'] == 'collabAgentToolCall':
                r_need(thread_id == parent, 'ROUTE_CHILD_COLLAB_FORBIDDEN'); ordinal = r_collab(item,ctx,parent,child,done)
                (collab_completions if done else collab_starts).append(ordinal); positions[('collab_done' if done else 'collab_start',ordinal)] = sequence
            elif item['type'] == 'agentMessage' and done:
                r_need(type(item.get('text')) is str, 'ROUTE_NATIVE_AGENT_TEXT')
                if thread_id == parent:
                    parent_messages.append(item['text'])
                    if item['text'] == R_ANNOUNCEMENT:
                        r_need(item.get('phase') == 'commentary', 'ROUTE_NATIVE_ANNOUNCEMENT_CHANNEL'); positions['announcement'] = sequence
                    elif item['text'] == ctx['nonverdict']:
                        r_need(item.get('phase') == 'final_answer', 'ROUTE_NATIVE_FINAL_CHANNEL'); positions['final'] = sequence
                else:
                    r_need(item['text'] == ctx['nonverdict'] and item.get('phase') == 'final_answer', 'ROUTE_NATIVE_CHILD_FIRST_TEXT'); child_messages.append(item['text'])
        elif method.endswith('/outputDelta'):
            r_need(thread_id == parent and p.get('itemId') in R_EXEC_IDS and type(p.get('delta')) is str, 'ROUTE_NATIVE_OUTPUT_DELTA_SCOPE'); deltas[p['itemId']].append(p['delta'])
        elif method == 'item/agentMessage/delta':
            r_need(type(p.get('delta')) is str, 'ROUTE_NATIVE_AGENT_DELTA_TYPE')
        elif method == 'turn/completed':
            t = p['turn']; r_need(t.get('status') == 'completed' and t.get('error') is None, 'ROUTE_NATIVE_TURN_COMPLETION')
            (parent_completed if thread_id == parent else child_completed).append(t)
            if thread_id == parent:
                positions['parent_completed'] = sequence
        elif method == 'thread/status/changed':
            r_need(set(p) == {'threadId','status'} and r_compact(p['status']) in (r_compact({'type':'notLoaded'}),r_compact({'type':'idle'}),r_compact({'type':'active','activeFlags':[]})), 'ROUTE_NATIVE_THREAD_STATUS')
    r_need(r_compact(received) == r_compact(frames) and r_compact(sent) == r_compact(sends) and set(seen) == set(range(1,8)), 'ROUTE_NATIVE_RAW_EVENT_JOIN')
    r_need(starts == completions == collab_starts == collab_completions == [0,1,2] and len(warnings) == 1 and len(parent_completed) == 1
           and parent_messages == [R_ANNOUNCEMENT,ctx['nonverdict']] and len(child_messages) <= 1 and len(child_completed) <= 1, 'ROUTE_NATIVE_COMPLETE_POPULATION')
    chain = [positions[('exec_start',0)],positions[('exec_done',0)],positions[('exec_start',1)],positions[('exec_done',1)],positions[('exec_start',2)],positions[('exec_done',2)],positions['announcement'],positions[('collab_start',0)],positions[('collab_done',0)],positions[('collab_start',1)],positions[('collab_done',1)],positions[('collab_start',2)],positions[('collab_done',2)],positions['final'],positions['parent_completed']]
    r_need(chain == sorted(set(chain)), 'ROUTE_LOAD_ANNOUNCE_DISPATCH_RETURN_ORDER')
    for i,key in enumerate(R_EXEC_IDS):
        if deltas[key]:
            r_need(''.join(deltas[key]).encode() == (docs['governor'],(ctx['child']+'\n').encode(),docs['child'])[i], 'ROUTE_NATIVE_DELTA_EXACT_BYTES')
    prepared = [r_compact(v)+b'\n' for v in sends]
    r_need(all(len(v) <= 32768 for v in prepared) and len(actual_sends) <= 131072 and actual_sends == b''.join(prepared), 'ROUTE_NATIVE_ACTUAL_SEND_BYTES')
    statuses = [{'method':v['method'],'id':v.get('id'),'prepared_bytes':len(raw),'prepared_sha256':r_hash(raw),'written_bytes':len(raw),'complete':True} for v,raw in zip(sends,prepared)]
    r_need(r_compact(send_status) == r_compact(statuses), 'ROUTE_NATIVE_SEND_COMPLETE')
    return {'schema':'dg17.routing.independent-protocol-projection.v1','parent_id_sha256':r_hash(parent.encode()),'child_id_sha256':r_hash(child.encode()),
            'parent_turn_id_sha256':r_hash(turn.encode()),'response_count':7,'notification_count':len(notifications),'notification_methods':sorted(set(notifications)),
            'warning_count':1,'warning_messages_sha256':r_hash(r_pretty(warnings)),
            'native_exec_started_count':3,'native_exec_completed_count':3,'native_collab_started_count':3,'native_collab_completed_count':3,
            'parent_completed_turn_count':1,'child_completed_turn_notifications':len(child_completed),'load_announce_dispatch_return_order_received':True,
            'server_requests':0,'unknown_frames':0,'first_return_sha256':R_NONVERDICT_SHA,
            'typed_governor_prefix_bytes':8000,'full_governor_bytes':21257,'selected_child_bytes':2039,
            'model_inference_proven':False,'substantive_independent_review_performed':False,'independent_review_obligation_satisfied':False,
            'substantive_composition_review_pending':True}




ROUTE_OWNER_SHA = '4a698fa6dfed29f6e3b3acc5d12415401e0865ac9a4646c7a61d74023843e814'


def route_index(packet):
    raw=read(packet/'REVIEW_PACKET02_INDEX.json',8192)
    return raw,r_index_document(raw)


def route_review_census(root,index,private):
    expected={row['path']:row for row in index['members']}
    need(digest(r_pretty(index))==R_INDEX_SHA,'ROUTE_REVIEW_INDEX_PIN')
    need(len(expected)==20 and sum(row['bytes'] for row in expected.values())==1356110,'ROUTE_REVIEW_INDEX_POPULATION')
    wanted_dirs={part.as_posix() for name in expected for part in Path(name).parents if part!=Path('.')}
    root_identity=content_directory(root,private);files={};dirs={};pending=[root];identities=[]
    try:
        while pending:
            directory=pending.pop();before=content_directory(directory,private);identities.append((directory,before))
            with os.scandir(directory) as entries:rows=list(entries)
            need(len(files)+len(dirs)+len(rows)<=len(expected)+len(wanted_dirs),'ROUTE_REVIEW_POPULATION_BOUND')
            for row in rows:
                path=directory/row.name;relative=path.relative_to(root).as_posix();info=path.lstat()
                need(path.resolve(strict=True)==path,'ROUTE_REVIEW_ALIAS')
                if stat.S_ISDIR(info.st_mode):
                    need(relative in wanted_dirs,'ROUTE_REVIEW_EXTRA_DIRECTORY')
                    dirs[relative]=content_directory(path,private);pending.append(path)
                else:
                    need(relative in expected and stat.S_ISREG(info.st_mode) and
                         stat.S_IMODE(info.st_mode)==(0o600 if private else 0o644),'ROUTE_REVIEW_MEMBER_SHAPE')
                    unused,found=content_file(path,8388608)
                    need(found['bytes']==expected[relative]['bytes'] and found['sha256']==expected[relative]['sha256'],'ROUTE_REVIEW_MEMBER_BYTES')
                    files[relative]=found
            need(content_directory(directory,private)==before,'ROUTE_REVIEW_DIRECTORY_CHANGED')
        need(set(files)==set(expected) and set(dirs)==wanted_dirs and
             all(content_directory(path,private)==identity for path,identity in identities),'ROUTE_REVIEW_COMPLETE_POPULATION')
    except OSError:
        raise Refusal('ROUTE_REVIEW_ENUMERATION_OR_READ_REFUSED') from None
    return {'root':str(root),'root_identity':root_identity,'files':files,'directories':dirs,
            'member_count':len(files),'bytes':sum(row['bytes'] for row in files.values())}


def route_owner_snapshot(path,index):
    raw,row=content_file(path,4096,True)
    need(path.is_absolute() and path.resolve(strict=True)==path and row['identity']['mode']==0o600
         and row['bytes']==3912 and row['sha256']==ROUTE_OWNER_SHA,'ROUTE_ROOT_OWNER_FILE')
    document=r_owner(raw,ROUTE_OWNER_SHA,index)
    return raw,{'path':str(path),'file':row,'document':document}


def route_selection_metadata(root,index,private=True):
    before=content_directory(root,private)
    with os.scandir(root) as entries:names={entry.name for entry in entries}
    need(names==set(SELECTION_PINS),"SELECTION_METADATA_POPULATION")
    raws={};files={}
    for name,pin in SELECTION_PINS.items():
        path=root/name
        need(path.resolve(strict=True)==path,"SELECTION_METADATA_ALIAS")
        raw,row=content_file(path,65536,True)
        need(row["identity"]["mode"]==(0o600 if private else 0o644),"SELECTION_METADATA_OWNER_MODE")
        raws[name]=raw;files[name]=row
    selection=r_selection_metadata(raws,index)
    need(content_directory(root,private)==before,"SELECTION_METADATA_DIRECTORY_CHANGED")
    return raws,{"root":str(root),"root_identity":before,"files":files,"selection_contract":selection}


def route_stage_inputs(state,output,packet):
    index_raw,index=route_index(packet);public=packet/'routing-review-inputs'
    before=route_review_census(public,index,False)
    metadata_public=packet/'routing-selection-metadata'
    metadata_raws,metadata_before=route_selection_metadata(metadata_public,index,False)
    metadata_target=output/'routing-selection-metadata'
    need(not os.path.lexists(metadata_target),'ROUTE_SELECTION_INPUT_NOT_FRESH')
    metadata_target.mkdir(mode=0o700)
    for name,raw in metadata_raws.items():
        mode=0o600
        fd=os.open(metadata_target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
        with os.fdopen(fd,'wb') as stream:stream.write(raw);os.fchmod(stream.fileno(),mode)
    need(route_selection_metadata(metadata_public,index,False)[1]==metadata_before,'SELECTION_METADATA_CHANGED')
    target=output/'routing-review-inputs';owner=output/'private/routing-owner-binding.json'
    need(not os.path.lexists(target) and not os.path.lexists(owner),'ROUTE_SELECTION_INPUT_NOT_FRESH')
    target.mkdir(mode=0o700)
    wanted_dirs=sorted(before['directories'],key=lambda text:(len(Path(text).parts),text))
    for name in wanted_dirs:(target/name).mkdir(mode=0o700)
    for name in sorted(before['files']):
        raw,row=content_file(public/name,8388608,True)
        need(row==before['files'][name],'ROUTE_PUBLIC_REVIEW_MEMBER_CHANGED')
        mode=0o600
        fd=os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
        with os.fdopen(fd,'wb') as stream:stream.write(raw);os.fchmod(stream.fileno(),mode)
    need(route_review_census(public,index,False)==before,'ROUTE_PUBLIC_REVIEW_TREE_CHANGED')
    raw=read(packet/'ROUTING_OWNER_BINDING.json',4096)
    need(len(raw)==3912 and digest(raw)==ROUTE_OWNER_SHA,'ROUTE_ROOT_OWNER_INPUT_PIN');r_owner(raw,ROUTE_OWNER_SHA,index)
    fd=os.open(owner,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw)
    state['routing_selection_private']={'metadata':route_selection_metadata(metadata_target,index)[1],'review':route_review_census(target,index,True),'owner':route_owner_snapshot(owner,index)[1]}
    state['routing_selection']={'audit_object':AUDIT_OBJECT,'review_index_sha256':R_INDEX_SHA,
          'review_member_count':20,'review_total_bytes':1356110,'owner_sha256':ROUTE_OWNER_SHA,
          'substantive_review_pending':True,'authority':'NONE','rechecks':[]}


def route_inputs_recheck(state,output,packet,label):
    unused,index=route_index(packet)
    need(type(state.get('routing_selection_private')) is dict,'ROUTE_SELECTION_NOT_STAGED')
    before=state['routing_selection_private']
    observed={'metadata':route_selection_metadata(output/'routing-selection-metadata',index)[1],'review':route_review_census(output/'routing-review-inputs',index,True),
              'owner':route_owner_snapshot(output/'private/routing-owner-binding.json',index)[1]}
    need(encoded(observed)==encoded(before),'ROUTE_SELECTION_INPUT_DRIFT')
    if label not in state['routing_selection']['rechecks']:state['routing_selection']['rechecks'].append(label)
    need(len(state['routing_selection']['rechecks'])<=16,'ROUTE_SELECTION_RECHECK_BOUND')
    return observed


def route_context(output,packet):
    population=content_archive_population(packet,'canonical')
    docs={'governor':population['files']['skills/implementaudit/SKILL.md'],
          'resolver':population['files']['skills/implementaudit/scripts/resolve-internal-skill.py'],
          'child':population['files']['skills/audit-assess/SKILL.md']}
    index_raw,index=route_index(packet)
    owner_raw,unused=route_owner_snapshot(output/'private/routing-owner-binding.json',index)
    metadata_raws,unused=route_selection_metadata(output/'routing-selection-metadata',index)
    return r_context(str(output),str(output/'routing-review-inputs'),owner_raw,ROUTE_OWNER_SHA,index_raw,docs,metadata_raws,str(output/'routing-selection-metadata')),docs


def route_collaboration_advertisement(tools):
    r_advertisement(tools)
    ns=next(row for row in tools if type(row) is dict and row.get('name')=='multi_agent_v1')
    for row in ns['tools']:
        need(set(row)=={'type','name','description','strict','parameters'} and row['type']=='function' and row['strict'] is False,
             'ROUTE_V1_FUNCTION_CLOSED')
        params=row['parameters'];need(params.get('type')=='object' and params.get('additionalProperties') is False and type(params.get('properties')) is dict,'ROUTE_V1_FUNCTION_PARAMETERS')
    selected={row['name']:row['parameters'] for row in ns['tools']}
    def simple(value,kind):
        need(type(value) is dict and set(value)=={'type','description'} and value['type']==kind
             and type(value['description']) is str and len(value['description'].encode())<=8192,'ROUTE_V1_PROPERTY_DESCRIPTION')
    spawn=selected['spawn_agent'];base={'message','items','fork_context','model','reasoning_effort'}
    need(set(spawn)=={'type','properties','additionalProperties'} and set(spawn['properties']) in (base,base|{'agent_type'}),'ROUTE_V1_SPAWN_PROPERTY_POPULATION')
    for key,value in spawn['properties'].items():
        if key!='items':simple(value,'boolean' if key=='fork_context' else 'string')
    items=spawn['properties']['items']
    need(type(items) is dict and set(items)=={'type','description','items'} and items['type']=='array'
         and type(items['description']) is str and len(items['description'].encode())<=8192,'ROUTE_V1_ITEMS_SCHEMA')
    entry=items['items']
    need(type(entry) is dict and set(entry)=={'type','properties','additionalProperties'} and entry['type']=='object'
         and entry['additionalProperties'] is False and set(entry['properties'])=={'type','text','image_url','audio_url','path','name'},'ROUTE_V1_TYPED_ITEM_SCHEMA')
    for value in entry['properties'].values():simple(value,'string')
    wait=selected['wait_agent'];close=selected['close_agent']
    need(set(wait)==set(close)=={'type','properties','required','additionalProperties'},'ROUTE_V1_WAIT_CLOSE_SCHEMA')
    target=wait['properties']['targets']
    need(set(target)=={'type','description','items'} and target['type']=='array' and target['items']=={'type':'string'}
         and type(target['description']) is str and len(target['description'].encode())<=8192,'ROUTE_V1_WAIT_TARGET_SCHEMA')
    simple(wait['properties']['timeout_ms'],'number');simple(close['properties']['target'],'string')
    return {'v1_namespace_exact':True,'advertised_v1_tools':['spawn_agent','send_input','resume_agent','wait_agent','close_agent'],
            'namespace_sha256':digest(encoded(ns))}


def route_phase_projection(raw,phase,ordinal,ctx,child,docs):
    request=r_json(raw);history=r_history(request,ctx,phase,child,docs)
    row={'ordinal':ordinal,'request_bytes':len(raw),'request_sha256':digest(raw),
         'thread_id_sha256':digest((child if phase=='C1' else ctx['parent']).encode()),
         'request_header_thread_join':True,'native_history_count':0,'native_outputs':[]}
    if phase=='C1':
        row.update(role='child',phase='C1',full_child_document_bytes=2039,full_child_document_sha256=R_CHILD_SHA,fresh_no_parent_history=True)
        return row
    count=int(phase[1])-1;row.update(role='parent',phase=phase,native_history_count=count)
    if not count:
        row['advertisement']={**content_exec_advertisement(request.get('tools')),**route_collaboration_advertisement(request.get('tools'))}
    outputs=[item for item in request['input'] if item.get('type')=='function_call_output']
    for i,item in enumerate(outputs):
        raw_output=item['output'].encode()
        if i<3:
            expected=(docs['governor'],(ctx['child']+'\n').encode(),docs['child'])[i];bound=r_output(item['output'],expected)
            record={'terminal_exit_zero':True,'live_session_returned':False,'output_bytes':len(expected),'output_sha256':digest(expected),
                    'tool_output_bytes':len(raw_output),'tool_output_sha256':digest(raw_output),'body_offset_utf8':bound['header_bytes']}
        else:record={'json_return_exact':True,'return_bytes':len(raw_output),'return_sha256':digest(raw_output)}
        row['native_outputs'].append({'call_id':item['call_id'],**record})
    return row


def route_provider_receiving(output,evidence,case,packet,parent,turn):
    record=content_private_json(evidence/'PROVIDER.json')
    keys={'schema','accepted_socket_count','semantic_request_count','listener_closed','thread_joined','non_daemon','thread_alive','port','request_rows','failure_type'}
    need(type(record) is dict and set(record)==keys and record['schema']=='dg17.codex.routing.provider-private.v1'
         and type(record['accepted_socket_count']) is int and record['accepted_socket_count']==8
         and type(record['semantic_request_count']) is int and record['semantic_request_count']==8
         and record['listener_closed'] is True and record['thread_joined'] is True and record['non_daemon'] is True
         and record['thread_alive'] is False and record['failure_type'] is None,'ROUTE_PROVIDER_CUSTODY')
    port=record['port'];need(type(port) is int and 1024<=port<=65535,'ROUTE_PROVIDER_PORT')
    need(type(record['request_rows']) is list and len(record['request_rows'])==8,'ROUTE_PROVIDER_ROWS')
    retained=[]
    for ordinal,row in enumerate(record['request_rows'],1):
        need(type(row) is dict and set(row)=={'ordinal','loopback_peer','header_complete','header_bytes','header_sha256','body_bytes','body_sha256','projection','response_prepared_bytes','response_prepared_sha256','response_sent_bytes','complete'}
             and type(row['ordinal']) is int and row['ordinal']==ordinal and row['loopback_peer'] is True
             and row['header_complete'] is True and row['complete'] is True,'ROUTE_PROVIDER_ROW_CLOSED')
        header,_=content_file(evidence/'http'/(str(ordinal)+'.header'),32768,True)
        body,_=content_file(evidence/'http'/(str(ordinal)+'.body'),2097152,True)
        response,_=content_file(evidence/'http'/(str(ordinal)+'.response.prepared'),66048,True)
        for prefix,raw in (('header',header),('body',body),('response_prepared',response)):
            need(type(row[prefix+'_bytes']) is int and row[prefix+'_bytes']==len(raw) and row[prefix+'_sha256']==digest(raw),'ROUTE_PROVIDER_RAW_BINDING')
        need(type(row['response_sent_bytes']) is int and row['response_sent_bytes']==len(response),'ROUTE_PROVIDER_RESPONSE_COMPLETE')
        retained.append({'header':header,'body':body,'response':response})
    ctx,docs=route_context(output,packet);ctx['parent']=parent
    http=r_http_receive(retained,ctx,docs,parent,port);child=http['child_id']
    phases=[route_phase_projection(entry['body'],phase,i,ctx,child,docs) for i,(entry,phase) in enumerate(zip(retained,http['request_order']),1)]
    need(encoded(phases)==encoded([row['projection'] for row in record['request_rows']]),'ROUTE_PROVIDER_PHASE_PROJECTION')
    expected={'accepted_sockets':8,'semantic_requests':8,'parent_requests':7,'child_requests':1,'request_order':http['request_order'],
              'complete_response_phases':http['request_order'],'listener_closed':True,'thread_joined':True,'responses_fully_sent':True}
    need(encoded(case['provider'])==encoded(expected),'ROUTE_PROVIDER_PUBLIC_CUSTODY')
    route=content_private_json(evidence/'ROUTE_CONTEXT.json')
    expected_route={'parent_thread_id':parent,'parent_turn_id':turn,'child_thread_id':child,'parent_requests':7,'child_requests':1,'received_requests':8,
                    'request_order':http['request_order'],'responses_complete':http['request_order'],'child_first_return':r_nonverdict(),
                    'phase_projections':phases,'provider_advertisement':phases[0]['advertisement']}
    need(encoded(route)==encoded(expected_route),'ROUTE_CONTEXT_INDEPENDENT_PROJECTION')
    need(encoded(content_private_json(output/'private/canonical-routing/EXECUTION_ROUTE_ENVELOPE.json'))==encoded(ctx['envelope']),'ROUTE_NATIVE_ENVELOPE_JOIN')
    return port,ctx,docs,http


def route_wire_receiving(ctx,evidence,case,docs,http):
    native=evidence/'native';events=content_private_json(native/'NATIVE_EVENTS.json')
    raw,_=content_file(native/'native.stdout',2097152,True)
    sends,_=content_file(native/'native.sends.jsonl',131072,True)
    status=content_private_json(native/'NATIVE_SEND_STATUS.json')
    observed=r_wire_receive(raw,events,sends,status,ctx,docs,http)
    commands=[];collaboration=[]
    for event in events:
        value=event['value']
        if event['direction']!='receive' or value.get('method') not in ('item/started','item/completed'):continue
        item=value['params']['item'];done=value['method']=='item/completed'
        if item['type']=='commandExecution' and done:
            i=R_EXEC_IDS.index(item['id']);body=(docs['governor'],(ctx['child']+'\n').encode(),docs['child'])[i]
            commands.append({'call_id':item['id'],'exit_code':0,'argv_exact':True,'cwd_exact':True,'output_bytes':len(body),
                             'output_sha256':digest(body),'aggregate_present':item.get('aggregatedOutput') is not None})
        elif item['type']=='collabAgentToolCall':
            i=R_COLLAB_IDS.index(item['id'])
            collaboration.append({'call_id':item['id'],'tool':('spawnAgent','wait','closeAgent')[i],'completed':done,
                                  'child_id_joined':done or i!=0,'first_return_exact':done and i in (1,2)})
    keys=('response_count','notification_count','notification_methods','warning_count','warning_messages_sha256',
          'native_exec_started_count','native_exec_completed_count','native_collab_started_count','native_collab_completed_count',
          'parent_completed_turn_count','child_completed_turn_notifications','load_announce_dispatch_return_order_received','unknown_frames','server_requests')
    projection={key:observed[key] for key in keys};projection.update(commands=commands,collaboration=collaboration)
    need(encoded(projection)==encoded(case['native_protocol']),'ROUTE_NATIVE_PUBLIC_PROJECTION')
    need(case['parent_thread_id_sha256']==observed['parent_id_sha256'] and case['child_thread_id_sha256']==observed['child_id_sha256']
         and case['scripted_nonverdict_sha256']==R_NONVERDICT_SHA,'ROUTE_PUBLIC_IDENTITY_PROJECTION')
    previous=0
    for phase in http['request_order']:
        admission=content_private_json(evidence/('PHASE_'+phase+'_ADMISSION.json'))
        need(type(admission) is dict and set(admission)=={'phase','source_store_runtime','package_config_helpers','review_packet_owner_selection','live_arg0_aliases','native_events_received','global_echild_required_while_native_live'}
             and admission['phase']==phase and all(admission[k] is True for k in ('source_store_runtime','package_config_helpers','review_packet_owner_selection','live_arg0_aliases'))
             and admission['global_echild_required_while_native_live'] is False
             and type(admission['native_events_received']) is int and previous<=admission['native_events_received']<=len(events),'ROUTE_IMMEDIATE_PHASE_ADMISSION')
        previous=admission['native_events_received']
        # Every claimed prefix consists only of the already independently received closed wire.
        prefix=events[:previous]
        need(any(row['direction']=='send' and row['value'].get('method')=='turn/start' for row in prefix),'ROUTE_PHASE_TURN_NOT_STARTED')
        exec_limit={'P1':0,'P2':1,'P3':2}.get(phase,3)
        collab_limit={'P1':0,'P2':0,'P3':0,'P4':0,'P5':1,'P6':2,'P7':3,
                      'C1':1 if http['request_order'].index('C1')<http['request_order'].index('P5') else 2}[phase]
        for row in prefix:
            value=row['value']
            if row['direction']!='receive':continue
            if value.get('method') not in ('item/started','item/completed'):continue
            item=value['params']['item']
            if item['type']=='commandExecution':need(R_EXEC_IDS.index(item['id'])<exec_limit,'ROUTE_PHASE_FUTURE_EXEC')
            elif item['type']=='collabAgentToolCall':
                index=R_COLLAB_IDS.index(item['id'])
                need(index<collab_limit and not(phase=='C1' and index==1 and value['method']=='item/completed'),'ROUTE_PHASE_FUTURE_COLLAB')
            elif item['type']=='agentMessage' and value['method']=='item/completed':
                if value['params']['threadId']==http['parent_id']:
                    need(item['text']==R_ANNOUNCEMENT and phase in ('C1','P5','P6','P7'),'ROUTE_PHASE_FUTURE_PARENT_MESSAGE')
                else:need(phase in ('P6','P7'),'ROUTE_PHASE_FUTURE_CHILD_RETURN')
    frames=[r_json(line,262144) for line in raw.splitlines()]
    return {row['id']:row['result'] for row in frames if 'id' in row},observed


def route_selected_documents(evidence,ctx,case,population):
    selected=[row for row in case['skills']['selected_entries'] if row['logical_name']=='audit-assess']
    need(len(selected)==1 and selected[0]['name']=='implementaudit:audit-assess','ROUTE_SELECTED_CATALOGUED_CHILD')
    unused,child=content_file(ctx['effective']/'skills/audit-assess/SKILL.md',2039)
    unused,resolver=content_file(ctx['effective']/'skills/implementaudit/scripts/resolve-internal-skill.py',5178)
    need(child['bytes']==2039 and child['sha256']==R_CHILD_SHA and resolver['bytes']==5178 and resolver['sha256']==R_RESOLVER_SHA,'ROUTE_SELECTED_DOCUMENT_BYTES')
    expected={'selected_child':selected[0],'child':child,'resolver':resolver}
    need(encoded(content_private_json(evidence/'SELECTED_DOCUMENTS.json'))==encoded(expected),'ROUTE_SELECTED_DOCUMENTS_JOIN')


def content_success(value,uid,gid,receipt):
    """Full routing public conjunction, supplemented by independent raw/private joins."""
    try:
        if type(value) is not dict or value['schema']!='dg17.codex.canonical-routing.v1' or value['status']!='OBSERVED_CANONICAL_NATIVE_ROUTE_NONVERDICT':return False
        if (value['control_source_commit'],value['control_source_tree'])!=(SOURCE,TREE):return False
        if (value['package_source_commit'],value['package_source_tree'])!=('8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b','0da374609f7fea2463a2926f3603b976620bd10e'):return False
        if value['runtime_release_declared']!='0.167.0-alpha.4' or type(value['runtime_bytes']) is not int or value['runtime_bytes']!=BINARY_BYTES or value['runtime_sha256']!=BINARY_SHA:return False
        if any(value[k] is not True for k in ('parent_full_source_admission_required','source_before','source_after','runtime_before','runtime_after','currentness_before','currentness_after','git_unchanged','post_return_readmission','selection_metadata_received','review_packet_files_available','review_packet_unchanged','substantive_composition_review_pending')):return False
        if value['currentness_receipt_sha256']!=digest((receipt+'\n').encode()) or value['owner_envelope_sha256']!=ROUTE_OWNER_SHA or value['review_packet_index_sha256']!=R_INDEX_SHA:return False
        if any(type(value[k]) is not int or value[k]!=n for k,n in (('review_packet_member_count',20),('review_packet_total_bytes',1356110),('requested_rpc_count',7),('requested_exec_count',3),('requested_collaboration_count',3),('additional_failure_count',0))):return False
        if value['planned_families']!=['canonical'] or value['unstarted_families']!=[] or value['failure'] is not None or value['supplemental_failures']!=[]:return False
        if value['native_internal_helper_count']!='UNESTABLISHED' or value['independent_receiving']!='NOT_PERFORMED':return False
        if any(value[k] is not False for k in ('model_inference_proven','substantive_independent_review_performed','independent_review_obligation_satisfied','persistent_real_home_installation_proven','original_acceptance_awarded','readiness_or_effect_authority')):return False
        offline=value['offline']
        if type(offline) is not dict or any(offline[k] is not True for k in ('verified','namespace_differs_from_parent','only_loopback','effective_permitted_ambient_capabilities_zero','no_new_privileges')):return False
        if any(type(offline[k]) is not int or offline[k]!=n for k,n in (('uid',uid),('gid',gid),('external_routes',0))):return False
        cleanup=value['cleanup']
        if any(cleanup[k] is not True for k in ('all_native_closed','all_provider_closed','global_echild_after_close','global_echild_after_seal','private_seal_unchanged')):return False
        if type(cleanup['runtime_copy_files_retained']) is not int or cleanup['runtime_copy_files_retained']!=0:return False
        if any(type(cleanup[k]) is not str or re.fullmatch('[0-9a-f]{64}',cleanup[k]) is None for k in ('runtime_owner_sha256','private_seal_sha256')):return False
        if cleanup['private_plaintext_policy']!='RETAIN_UNTIL_HOST_TEARDOWN' or cleanup['host_teardown_observed'] is not False:return False
        if type(value['cases']) is not list or len(value['cases'])!=1:return False
        case=value['cases'][0];spec=content_package_spec('canonical')
        if case['family']!='canonical' or case['status']!='CANONICAL_NATIVE_ROUTE_NONVERDICT_OBSERVED' or case['failure'] is not None:return False
        if type(case['archive_bytes']) is not int or case['archive_bytes']!=spec['bytes'] or case['archive_sha256']!=spec['sha256'] or case['matrix_sha256']!=spec['matrix_sha256']:return False
        if case['rpc_methods']!=R_METHODS or any(type(case[k]) is not int or case[k]!=7 for k in ('rpc_frames_attempted','rpc_frames_complete')):return False
        if any(type(case[k]) is not int or case[k]!=3 for k in ('requested_exec_count','requested_collaboration_count','exec_responses_complete','collaboration_responses_complete','native_exec_started_count','native_exec_completed_count','native_collab_started_count','native_collab_completed_count')):return False
        if any(case[k] is not True for k in ('native_started','runtime_reported_version_matches','package_unchanged','helper_bookends_unchanged','arg0_aliases_exact','arg0_aliases_closed','config_unchanged','native_governor_body_received','resolver_exact','native_child_body_received_by_governor','native_child_body_received_by_child','fresh_native_child_observed','first_return_received','native_close_return_received','announcement_after_load','first_return_propagated','native_child_closed')):return False
        for key in ('package_before','package_after'):
            row=case[key]
            if row!={'family':'canonical','files':75,'bytes':2092025,'matrix_sha256':spec['matrix_sha256'],'complete_matrix_matches':True}:return False
        catalog=case['catalog']
        if catalog['status']!='SOURCE_CANDIDATE_INSTALLED_ENABLED' or catalog['id']!='implementaudit@implementaudit' or any(catalog[k] is not True for k in ('installed','enabled','source_image_path_bound','five_exact_skill_paths')):return False
        if len(catalog['skills'])!=5 or any(type(catalog[k]) is not int or catalog[k]!=0 for k in ('other_skill_count','declared_hook_count','declared_app_count','declared_mcp_count')):return False
        if case['skills']['selected_count']!=5 or case['skills']['selected_enabled'] is not True or len(case['skills']['selected_entries'])!=5:return False
        if case['hooks']!={'status':'EMPTY_CONFIGURED_HOOK_METADATA','hook_count':0,'error_count':0,'warning_count':0,'loaded_thread_hooks_observed':False,'hook_delivery_exercised':False}:return False
        capture=case['capture']
        if not content_capture_base_shape(capture,'native-content') or capture['process_started'] is not True or type(capture['returncode']) is not int or capture['returncode']!=0:return False
        if any(capture[k] is not True for k in ('pidfd_acquired','streams_complete','private_streams_retained')) or any(capture[k] is not False for k in ('timeout','output_bound_exceeded','internal_failure','retention_failure')) or capture['reason_code']!='NATIVE_COMPLETE' or capture['cleanup']['echild'] is not True:return False
        scope=case['runtime_scope']
        if scope['full_session_scope_available'] is not True or scope['launch_directory_empty'] is not True or any(type(scope[k]) is not int or scope[k]!=0 for k in ('living_owned_processes','owned_zombies','uncertain_owned_candidates')):return False
        provider=case['provider'];order=provider['request_order']
        if order not in (['P1','P2','P3','P4','C1','P5','P6','P7'],['P1','P2','P3','P4','P5','C1','P6','P7']) or provider['complete_response_phases']!=order:return False
        if any(type(provider[k]) is not int or provider[k]!=n for k,n in (('accepted_sockets',8),('semantic_requests',8),('parent_requests',7),('child_requests',1))) or any(provider[k] is not True for k in ('listener_closed','thread_joined','responses_fully_sent')):return False
        if case['scripted_nonverdict_sha256']!=R_NONVERDICT_SHA or case['parent_thread_id_sha256']==case['child_thread_id_sha256']:return False
        protocol=case['native_protocol']
        if protocol['load_announce_dispatch_return_order_received'] is not True or any(type(protocol[k]) is not int or protocol[k]!=n for k,n in (('response_count',7),('warning_count',1),('native_exec_started_count',3),('native_exec_completed_count',3),('native_collab_started_count',3),('native_collab_completed_count',3),('parent_completed_turn_count',1),('unknown_frames',0),('server_requests',0))):return False
        if type(protocol['commands']) is not list or len(protocol['commands'])!=3 or type(protocol['collaboration']) is not list or len(protocol['collaboration'])!=6:return False
        return True
    except (KeyError,TypeError,ValueError):return False

def content_compact(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()


def content_json(raw,limit=8388608):
    need(type(raw) is bytes and len(raw) <= limit,'CONTENT_JSON_BOUND')
    def nonfinite(unused): raise Refusal('CONTENT_NONFINITE_JSON')
    try:
        value=json.loads(raw.decode('utf-8','strict'),object_pairs_hook=unique_object,parse_constant=nonfinite)
        todo=[(value,0)];count=0
        while todo:
            item,depth=todo.pop();count+=1
            need(depth <= 32 and count <= 65536,'CONTENT_JSON_STRUCTURE')
            if type(item) is dict:
                need(all(type(k) is str and len(k.encode('utf-8')) <= 1024 for k in item),'CONTENT_JSON_KEYS')
                todo.extend((v,depth+1) for v in item.values())
            elif type(item) is list: todo.extend((v,depth+1) for v in item)
            elif type(item) is str: need(len(item.encode('utf-8','strict')) <= 2097152,'CONTENT_JSON_STRING')
            else: need(item is None or type(item) in (bool,int) or type(item) is float and math.isfinite(item),'CONTENT_JSON_SCALAR')
        return value
    except (UnicodeError,ValueError,RecursionError):
        raise Refusal('CONTENT_JSON_DECODE') from None


def content_context(family,output):
    spec=content_package_spec(family);root=output/'canonical-routing-payloads'/family
    home=root/'home';image=root/'source-package' if family=='canonical' else home/'skills/implementaudit'
    effective=home/'plugins/cache/implementaudit/implementaudit/0.4.0' if family=='canonical' else image
    target=effective/spec['governor'];cwd=root/'neutral'
    for path in (home,image,effective,target,cwd,root/'tmp'):content_fixed_path(str(path))
    return {'family':family,'root':root,'home':home,'image':image,'effective':effective,'target':target,'cwd':cwd,'tmp':root/'tmp',
            'name':'implementaudit:implementaudit' if family=='canonical' else 'implementaudit',
            'marker':'DG17_FIXED_GOVERNOR_CONTENT_'+family.upper(),'ack':'DG17_CONTENT_ACK_'+family.upper(),
            'call_id':'dg17_governor_read_'+family,'args':content_fixed_exec_args(str(target),str(cwd))}


def content_expected_config(ctx,port,installed):
    need(type(port) is int and 1024 <= port <= 65535,'CONTENT_PROVIDER_PORT')
    value={'model':'dg17-canonical-routing-fixture','model_provider':'dg17_loopback','approval_policy':'never',
           'sandbox_mode':'read-only','allow_login_shell':False,'tool_output_token_limit':16384,
           'cli_auth_credentials_store':'ephemeral','mcp_oauth_credentials_store':'file',
           'features':{'plugins':True,'plugin_discovery_prefetch':False,'remote_plugin':False,'shell_tool':True,
                       'unified_exec':True,'exec_permission_approvals':False,'shell_snapshot':False,
                       'shell_snapshot_v2':False,'code_mode':False,'code_mode_only':False},
           'analytics':{'enabled':False},'feedback':{'enabled':False},
           'shell_environment_policy':{'inherit':'none','experimental_use_profile':False,'set':{'HOME':str(ctx['home']),
                 'PATH':'/usr/bin:/bin','TMPDIR':str(ctx['tmp']),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8'}},
           'model_providers':{'dg17_loopback':{'name':'DG17 fixed canonical routing fixture',
                 'base_url':'http://127.0.0.1:'+str(port)+'/v1','wire_api':'responses','requires_openai_auth':False,
                 'supports_websockets':False,'request_max_retries':0,'stream_max_retries':0,'stream_idle_timeout_ms':15000}}}
    value['agents']={'enabled':True,'max_concurrent_threads_per_session':1,'max_depth':1}
    value['features'].update({'multi_agent':True,'multi_agent_v2':False})
    if installed:value['plugins']={'implementaudit@implementaudit':{'enabled':True}}
    return value


def content_initial_config_bytes(ctx,port):
    """Bind the declared initial TOML bytes even though canonical install later rewrites it."""
    lines=[]
    def table(value,path):
        if path:lines.append('['+'.'.join(path)+']')
        for key,item in value.items():
            if type(item) is not dict:lines.append(key+' = '+json.dumps(item,ensure_ascii=True))
        lines.append('')
        for key,item in value.items():
            if type(item) is dict:table(item,path+(key,))
    table(content_expected_config(ctx,port,False),())
    return ('\n'.join(lines)+'\n').encode()


def content_expected_sends(ctx,thread_id):
    canonical=ctx['family']=='canonical';cwd=str(ctx['cwd']);image=str(ctx['image'])
    rows=[{'id':1,'method':'initialize','params':{'clientInfo':{'name':'dg17_package_content','version':'1.0.0'},'capabilities':{'experimentalApi':True}}},
          {'method':'initialized'}]
    if canonical: rows.extend([
        {'id':2,'method':'plugin/install','params':{'pluginName':'implementaudit','marketplacePath':image+'/.claude-plugin/marketplace.json'}},
        {'id':3,'method':'plugin/read','params':{'pluginName':'implementaudit','marketplacePath':image+'/.claude-plugin/marketplace.json'}}])
    first=4 if canonical else 2
    rows.extend([{'id':first,'method':'skills/list','params':{'cwds':[cwd],'forceReload':True}},
                 {'id':first+1,'method':'hooks/list','params':{'cwds':[cwd]}},
                 {'id':first+2,'method':'thread/start','params':{'cwd':cwd,'approvalPolicy':'never','approvalsReviewer':'user',
                     'sandbox':'read-only','ephemeral':True,'model':'dg17-package-body-fixture','modelProvider':'dg17_loopback'}},
                 {'id':first+3,'method':'turn/start','params':{'threadId':thread_id,'input':[
                     {'type':'text','text':ctx['marker'],'text_elements':[]},
                     {'type':'skill','name':ctx['name'],'path':str(ctx['target'])}]}}])
    return rows


def content_exec_advertisement(tools):
    need(type(tools) is list and 1 <= len(tools) <= 128,'CONTENT_ADVERTISEMENT_POPULATION')
    selected=[row for row in tools if type(row) is dict and row.get('name')=='exec_command']
    need(len(selected)==1,'CONTENT_ADVERTISEMENT_SELECTION');row=selected[0]
    need(set(row)=={'type','name','description','strict','parameters'} and row['type']=='function' and row['strict'] is False
         and type(row['description']) is str and len(row['description'].encode())<=4096,'CONTENT_ADVERTISEMENT_PROFILE')
    p=row['parameters'];need(type(p) is dict and set(p)=={'type','properties','required','additionalProperties'}
         and p['type']=='object' and p['required']==['cmd'] and p['additionalProperties'] is False,'CONTENT_EXEC_SCHEMA')
    kinds={'cmd':'string','workdir':'string','shell':'string','login':'boolean','tty':'boolean','yield_time_ms':'number',
           'max_output_tokens':'number','sandbox_permissions':'string','justification':'string','prefix_rule':'array'}
    need(type(p['properties']) is dict and set(p['properties'])==set(kinds),'CONTENT_EXEC_PROPERTY_POPULATION')
    for key,kind in kinds.items():
        item=p['properties'][key];extra={'enum'} if key=='sandbox_permissions' else {'items'} if key=='prefix_rule' else set()
        need(type(item) is dict and set(item)=={'type','description'}|extra and item['type']==kind
             and type(item['description']) is str and len(item['description'].encode())<=8192,'CONTENT_EXEC_PROPERTY_SHAPE')
        if key=='sandbox_permissions':need(item['enum']==['use_default','require_escalated'],'CONTENT_EXEC_SANDBOX_ENUM')
        if key=='prefix_rule':need(item['items']=={'type':'string'},'CONTENT_EXEC_PREFIX_SCHEMA')
    return {'exec_command_advertised':True,'exec_profile_exact':True,'advertised_tool_count':len(tools),
            'advertised_tools_sha256':digest(encoded(tools)),'exec_advertisement_sha256':digest(encoded(row))}


def content_provider_projection(raw,ctx,ordinal,governor):
    value=content_json(raw,2097152)
    need(type(value) is dict and value.get('model')=='dg17-package-body-fixture' and value.get('stream') is True
         and type(value.get('input')) is list and len(value['input'])<=256,'CONTENT_RESPONSES_REQUEST')
    items=value['input'];base={'ordinal':ordinal,'request_bytes':len(raw),'request_sha256':digest(raw)}
    if ordinal==1:
        prefix=content_prefix_projection(value,ctx['family'],str(ctx['target']),governor)
        texts=[]
        for item in items:
            if type(item) is not dict or item.get('role')!='user':continue
            parts=item.get('content')
            if type(parts) is str:texts.append(parts)
            elif type(parts) is list:
                texts.extend(p['text'] for p in parts if type(p) is dict and p.get('type') in ('input_text','output_text') and type(p.get('text')) is str)
        need(sum(t.count(ctx['marker']) for t in texts)==1 and not any(type(i) is dict and i.get('type') in ('function_call','function_call_output') for i in items),'CONTENT_FIRST_REQUEST_HISTORY')
        ad=content_exec_advertisement(value.get('tools'))
        return {**base,**ad,'typed_fragment_exact':True,'typed_fragment_bytes':prefix['fragment_bytes'],
                'typed_fragment_sha256':prefix['fragment_sha256'],'raw_prefix_bytes':8000,
                'raw_prefix_sha256':digest(governor[:8000]),'full_body_present_initially':False}
    need(ordinal==2,'CONTENT_PROVIDER_REQUEST_QUOTA')
    calls=[i for i in items if type(i) is dict and i.get('type')=='function_call'];outputs=[i for i in items if type(i) is dict and i.get('type')=='function_call_output']
    need(len(calls)==len(outputs)==1,'CONTENT_NATIVE_TOOL_RETURN_POPULATION');call=calls[0];out=outputs[0]
    need(call.get('call_id')==ctx['call_id'] and call.get('name')=='exec_command' and type(call.get('arguments')) is str
         and content_compact(content_json(call['arguments'].encode(),32768))==content_compact(ctx['args'])
         and out.get('call_id')==ctx['call_id'] and type(out.get('output')) is str,'CONTENT_NATIVE_TOOL_RETURN_JOIN')
    body=content_full_output_projection(out['output'],governor);raw_output=out['output'].encode()
    return {**base,'matching_call_id':True,'exact_fixed_arguments':True,'terminal_exit_zero':True,
            'live_session_returned':False,'full_governor_received':True,'full_governor_bytes':21257,
            'full_governor_sha256':digest(governor),'tool_output_bytes':len(raw_output),
            'tool_output_sha256':digest(raw_output),'body_offset_utf8':body['output_start_bytes'],
            'body_end_utf8':body['output_end_bytes'],'requested_output_tokens':8192,'configured_output_tokens':16384}


def content_response_bytes(ctx,ordinal):
    rid='resp_dg17_'+ctx['family']+'_'+str(ordinal)
    if ordinal==1:
        item={'type':'function_call','id':'fc_'+ctx['family'],'call_id':ctx['call_id'],'name':'exec_command',
              'arguments':content_compact(ctx['args']).decode(),'status':'completed'}
    else:
        need(ordinal==2,'CONTENT_RESPONSE_QUOTA')
        item={'type':'message','id':'msg_'+ctx['family'],'role':'assistant','status':'completed',
              'content':[{'type':'output_text','text':ctx['ack'],'annotations':[]}]}
    events=[{'type':'response.created','response':{'id':rid}},
            {'type':'response.output_item.done','output_index':0,'item':item},
            {'type':'response.completed','response':{'id':rid,'status':'completed','output':[item],
                'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}}]
    payload=b''.join(b'event: '+e['type'].encode()+b'\ndata: '+content_compact(e)+b'\n\n' for e in events)
    need(len(payload)<=8192,'CONTENT_SSE_BOUND')
    return b'HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nConnection: close\r\nContent-Length: '+str(len(payload)).encode()+b'\r\n\r\n'+payload


def content_http_request(header,body,port):
    need(type(header) is bytes and len(header)<=32768 and header.endswith(b'\r\n\r\n'),'CONTENT_HTTP_HEADER_BOUND')
    lines=header[:-4].decode('ascii','strict').split('\r\n')
    need(lines[0]=='POST /v1/responses HTTP/1.1','CONTENT_HTTP_ENDPOINT');fields={}
    for line in lines[1:]:
        need(line and not line[0].isspace() and ':' in line,'CONTENT_HTTP_HEADER_SYNTAX')
        name,value=line.split(':',1);name=name.lower();value=value.strip()
        need(re.fullmatch('[a-z0-9-]+',name) is not None and name not in fields and len(value)<=8192,'CONTENT_HTTP_HEADER_KEY')
        fields[name]=value
    need(fields.get('host')=='127.0.0.1:'+str(port) and fields.get('content-type')=='application/json'
         and not set(fields)&{'authorization','proxy-authorization','cookie','transfer-encoding','content-encoding','expect'},'CONTENT_HTTP_AUTH_OR_TRANSPORT')
    length=fields.get('content-length','')
    need(re.fullmatch('[0-9]{1,8}',length) is not None and int(length)==len(body) and 0<len(body)<=2097152,'CONTENT_HTTP_BODY_SIZE')


def content_provider_receiving(ctx,evidence,case,governor):
    record=content_private_json(evidence/'PROVIDER.json');keys={'schema','accepted_socket_count','semantic_request_count','listener_closed','thread_joined','non_daemon','thread_alive','port','request_rows','failure_type'}
    need(type(record) is dict and set(record)==keys and record['schema']=='dg17.codex.content.provider-private.v1'
         and type(record['accepted_socket_count']) is int and record['accepted_socket_count']==2
         and type(record['semantic_request_count']) is int and record['semantic_request_count']==2
         and record['listener_closed'] is True and record['thread_joined'] is True and record['non_daemon'] is True
         and record['thread_alive'] is False and record['failure_type'] is None,'CONTENT_PROVIDER_CUSTODY')
    port=record['port'];need(type(port) is int and 1024<=port<=65535,'CONTENT_PROVIDER_PORT')
    need(type(record['request_rows']) is list and len(record['request_rows'])==2,'CONTENT_PROVIDER_ROWS')
    projected=[];total=0
    for ordinal,row in enumerate(record['request_rows'],1):
        keys={'ordinal','loopback_peer','header_complete','header_bytes','header_sha256','body_bytes','body_sha256','projection','response_prepared_bytes','response_prepared_sha256','response_sent_bytes','complete'}
        need(type(row) is dict and set(row)==keys and type(row['ordinal']) is int and row['ordinal']==ordinal
             and row['loopback_peer'] is True and row['header_complete'] is True and row['complete'] is True,'CONTENT_PROVIDER_ROW')
        header,_=content_file(evidence/'http'/(str(ordinal)+'.header'),32768,True)
        body,_=content_file(evidence/'http'/(str(ordinal)+'.body'),2097152,True)
        sent,_=content_file(evidence/'http'/(str(ordinal)+'.response.prepared'),16384,True)
        content_http_request(header,body,port);total+=len(header)+len(body)
        need(total<=2*(2097152+32768),'CONTENT_PROVIDER_TOTAL')
        for name,raw in (('header',header),('body',body),('response_prepared',sent)):
            need(type(row[name+'_bytes']) is int and row[name+'_bytes']==len(raw) and row[name+'_sha256']==digest(raw),'CONTENT_PROVIDER_RAW_BINDING')
        need(type(row['response_sent_bytes']) is int and row['response_sent_bytes']==len(sent)
             and sent==content_response_bytes(ctx,ordinal),'CONTENT_PROVIDER_FIXED_SENT_RESPONSE')
        projection=content_provider_projection(body,ctx,ordinal,governor)
        need(encoded(projection)==encoded(row['projection'])==encoded(case['typed_request' if ordinal==1 else 'full_body_request']),'CONTENT_PROVIDER_PUBLIC_PROJECTION')
        projected.append(projection)
    need(case['provider']=={'accepted_sockets':2,'semantic_requests':2,'listener_closed':True,'thread_joined':True,'responses_fully_sent':True},'CONTENT_PROVIDER_PUBLIC_CUSTODY')
    return port


def content_terminal_command(item,ctx,governor,complete):
    need(type(item) is dict and item.get('type')=='commandExecution' and item.get('id')==ctx['call_id']
         and item.get('cwd')==str(ctx['cwd']) and type(item.get('command')) is str,'CONTENT_COMMAND_IDENTITY')
    try:args=shlex.split(item['command'],posix=True)
    except ValueError:raise Refusal('CONTENT_COMMAND_DISPLAY') from None
    need(args==['/usr/bin/bash','-c',ctx['args']['cmd']],'CONTENT_COMMAND_FIXED_ARGV')
    if not complete:return None
    need(item.get('status')=='completed' and type(item.get('exitCode')) is int and item['exitCode']==0,'CONTENT_COMMAND_TERMINAL_EXIT')
    aggregate=item.get('aggregatedOutput');need(aggregate is None or type(aggregate) is str and aggregate.encode()==governor,'CONTENT_COMMAND_AGGREGATE')
    return {'command_id_matches':True,'command_argv_matches':True,'cwd_matches':True,'completed':True,'exit_code':0,
            'aggregate_present':aggregate is not None,'aggregate_full_body_matches':aggregate is not None}


def content_wire_receiving(ctx,evidence,case,governor):
    native=evidence/'native';events=content_private_json(native/'NATIVE_EVENTS.json')
    raw,_=content_file(native/'native.stdout',2097152,True)
    need(type(events) is list and len(events)<=1024,'CONTENT_NATIVE_EVENT_POPULATION')
    lines=raw.splitlines();need(all(0<len(line)<=262144 for line in lines),'CONTENT_NATIVE_LINE_BOUND')
    received=[content_json(line,262144) for line in lines]
    need(all(type(v) is dict for v in received),'CONTENT_NATIVE_FRAME_OBJECT')
    thread_key=6 if ctx['family']=='canonical' else 4;turn_key=thread_key+1
    response_rows=[v for v in received if 'id' in v]
    need(all(set(v)=={'id','result'} and type(v['id']) is int for v in response_rows),'CONTENT_RESPONSE_ENVELOPE')
    responses={v['id']:v['result'] for v in response_rows};need(len(responses)==len(response_rows),'CONTENT_RESPONSE_DUPLICATE')
    thread=responses.get(thread_key);turn=responses.get(turn_key)
    need(type(thread) is dict and type(thread.get('thread')) is dict and type(turn) is dict and type(turn.get('turn')) is dict,'CONTENT_THREAD_TURN_RESPONSES')
    thread_id=thread['thread'].get('id');turn_id=turn['turn'].get('id')
    need(type(thread_id) is str and re.fullmatch('[A-Za-z0-9_-]{1,128}',thread_id) is not None
         and type(turn_id) is str and re.fullmatch('[A-Za-z0-9_-]{1,128}',turn_id) is not None,'CONTENT_THREAD_TURN_IDS')
    sends=content_expected_sends(ctx,thread_id);sent=[];seen={};recv=[];notifications=[];warnings=[];commands=[];agents=[];completed=[];starts=0;deltas=[]
    allowed={'skills/changed','remoteControl/status/changed','warning','thread/started','thread/status/changed','thread/tokenUsage/updated','turn/started','turn/completed','item/started','item/completed','item/commandExecution/outputDelta','item/agentMessage/delta'}
    for index,event in enumerate(events,1):
        need(type(event) is dict and set(event)=={'sequence','direction','value'} and type(event['sequence']) is int and event['sequence']==index,'CONTENT_EVENT_SEQUENCE')
        value=event['value']
        if event['direction']=='send':
            need(len(sent)<len(sends) and content_compact(value)==content_compact(sends[len(sent)]),'CONTENT_SEND_SEQUENCE');sent.append(value);continue
        need(event['direction']=='receive' and type(value) is dict,'CONTENT_EVENT_DIRECTION');recv.append(value)
        if 'id' in value:
            need(set(value)=={'id','result'} and type(value['id']) is int and value['id'] in {v['id'] for v in sent if 'id' in v}
                 and value['id'] not in seen,'CONTENT_SERVER_REQUEST_ERROR_OR_UNBOUND_ID');seen[value['id']]=value['result'];continue
        need(set(value)=={'method','params','emittedAtMs'} and type(value['emittedAtMs']) is int
             and 0<=value['emittedAtMs']<=9223372036854775807 and value['method'] in allowed
             and type(value['params']) is dict,'CONTENT_UNADMITTED_NOTIFICATION')
        method=value['method'];p=value['params'];notifications.append(method)
        if method=='skills/changed':need(p=={},'CONTENT_SKILLS_NOTIFICATION')
        elif method=='remoteControl/status/changed':
            need(set(p) in ({'status','installationId','serverName'},{'status','installationId','serverName','environmentId'})
                 and p['status']=='disabled' and p.get('environmentId') is None
                 and all(type(p[k]) is str and len(p[k].encode())<=1024 for k in ('installationId','serverName')),'CONTENT_REMOTE_CONTROL_NOTIFICATION')
        elif method=='warning':
            message='Skill `'+ctx['name']+'` exceeded the main prompt context limit and was truncated.'
            need(set(p)=={'threadId','message'} and p['threadId']==thread_id and p['message']==message,'CONTENT_TYPED_WARNING')
            warnings.append(digest(message.encode()))
        elif method.startswith('item/'):
            need(p.get('threadId')==thread_id and p.get('turnId')==turn_id,'CONTENT_ITEM_SCOPE')
            if method in ('item/started','item/completed'):
                item=p.get('item');need(type(item) is dict and item.get('type') in ('userMessage','agentMessage','commandExecution'),'CONTENT_ITEM_TYPE')
                done=method=='item/completed'
                if done:need(type(p.get('completedAtMs')) is int and 0<=p['completedAtMs']<=9223372036854775807,'CONTENT_ITEM_TIMESTAMP')
                if item['type']=='commandExecution':
                    projected=content_terminal_command(item,ctx,governor,done)
                    if done:commands.append(projected)
                    else:starts+=1
                elif item['type']=='agentMessage' and done:
                    need(type(item.get('text')) is str,'CONTENT_AGENT_TEXT_TYPE');agents.append(item['text'])
            else:
                need(type(p.get('delta')) is str,'CONTENT_DELTA_TYPE')
                if method=='item/commandExecution/outputDelta':need(p.get('itemId')==ctx['call_id'],'CONTENT_OUTPUT_DELTA_ID');deltas.append(p['delta'])
        elif method in ('turn/started','turn/completed'):
            need(p.get('threadId')==thread_id and type(p.get('turn')) is dict and p['turn'].get('id')==turn_id,'CONTENT_TURN_SCOPE')
            if method=='turn/completed':
                need(p['turn'].get('status')=='completed' and p['turn'].get('error') is None,'CONTENT_TURN_COMPLETION');completed.append(p['turn'])
        elif method=='thread/started':need(type(p.get('thread')) is dict and p['thread'].get('id')==thread_id,'CONTENT_THREAD_STARTED')
        elif method=='thread/status/changed':
            need(set(p)=={'threadId','status'} and p['threadId']==thread_id and type(p['status']) is dict
                 and content_compact(p['status']) in (content_compact({'type':'notLoaded'}),content_compact({'type':'idle'}),
                      content_compact({'type':'active','activeFlags':[]})),'CONTENT_THREAD_STATUS_UNRECEIVED')
        else:need(p.get('threadId')==thread_id,'CONTENT_THREAD_NOTIFICATION_SCOPE')
    need(encoded(recv)==encoded(received) and encoded(sent)==encoded(sends) and set(seen)=={v['id'] for v in sends if 'id' in v},'CONTENT_NATIVE_WIRE_MEMORY_JOIN')
    need(starts==len(commands)==len(completed)==len(warnings)==1 and agents==[ctx['ack']],'CONTENT_NATIVE_TERMINAL_POPULATION')
    if deltas:need(''.join(deltas).encode()==governor,'CONTENT_NATIVE_OUTPUT_DELTA_BODY')
    actual_sends,_=content_file(native/'native.sends.jsonl',131072,True);prepared=[content_compact(v)+b'\n' for v in sends]
    need(actual_sends==b''.join(prepared),'CONTENT_ACTUAL_NATIVE_SEND_BYTES')
    statuses=content_private_json(native/'NATIVE_SEND_STATUS.json')
    expected_status=[{'method':v['method'],'id':v.get('id'),'prepared_bytes':len(raw),'prepared_sha256':digest(raw),'written_bytes':len(raw),'complete':True} for v,raw in zip(sends,prepared)]
    need(encoded(statuses)==encoded(expected_status),'CONTENT_NATIVE_SEND_COMPLETENESS')
    projection={'response_count':len(responses),'notification_count':len(notifications),'notification_methods':sorted(set(notifications)),
                'warning_count':len(warnings),'warning_messages_sha256':digest(encoded(warnings)),'terminal_command_count':1,
                'turn_completed_count':1,'fixed_ack_observed':True,'unknown_frames':0,'server_requests':0,'command':commands[0]}
    need(encoded(projection)==encoded(case['native_protocol']),'CONTENT_PROTOCOL_PUBLIC_PROJECTION')
    return responses


def content_rpc_receiving(ctx,case,responses,population):
    home=str(ctx['home']);cwd=str(ctx['cwd']);matrix=population['matrix'];canonical=ctx['family']=='canonical'
    init=responses[1]
    need(type(init) is dict and set(init)=={'userAgent','codexHome','platformFamily','platformOs'} and init['codexHome']==home
         and init['platformFamily']=='unix' and init['platformOs']=='linux' and type(init['userAgent']) is str
         and len(init['userAgent'])<=1024 and '0.167.0-alpha.4' in init['userAgent'],'CONTENT_INITIALIZE_IDENTITY')
    names=('implementaudit','audit-state','audit-assess','audit-implement','audit-andon')
    if canonical:
        need(encoded(responses[2])==encoded({'authPolicy':'ON_INSTALL','appsNeedingAuth':[]}),'CONTENT_INSTALL_RESPONSE')
        detail=responses[3];need(type(detail) is dict and set(detail)=={'plugin'} and type(detail['plugin']) is dict,'CONTENT_PLUGIN_DETAIL')
        detail=detail['plugin'];summary=detail.get('summary')
        need(type(summary) is dict and summary.get('id')=='implementaudit@implementaudit' and summary.get('name')=='implementaudit'
             and summary.get('installed') is True and summary.get('enabled') is True and summary.get('authPolicy')=='ON_INSTALL'
             and summary.get('source')=={'type':'local','path':str(ctx['image'])}
             and detail.get('marketplacePath')==str(ctx['image']/'.claude-plugin/marketplace.json') and detail.get('marketplaceName')=='implementaudit','CONTENT_PLUGIN_SOURCE')
        need(all(type(detail.get(k)) is list and detail[k]==[] for k in ('apps','appTemplates','mcpServers','hooks')),'CONTENT_PLUGIN_ACTIVE_COMPONENTS')
        need(type(detail.get('skills')) is list and len(detail['skills'])==5,'CONTENT_PLUGIN_SKILL_COUNT')
        selected=[]
        for row in detail['skills']:
            logical=row.get('name','').removeprefix('implementaudit:') if type(row) is dict else None
            need(logical in names and row.get('name')=='implementaudit:'+logical and type(row.get('enabled')) is bool and row['enabled'] is True,'CONTENT_CANDIDATE_SKILL_NAME')
            relative='skills/'+logical+'/SKILL.md';need(row.get('path')==str(ctx['image']/relative),'CONTENT_CANDIDATE_SKILL_PATH')
            selected.append({'name':logical,'path':relative,'sha256':matrix[relative]['sha256'],'enabled':True,'exact_selected_root':True,'plugin_attribution_matches':False})
        need({r['name'] for r in selected}==set(names),'CONTENT_CANDIDATE_SKILL_DUPLICATE')
        expected={'status':'SOURCE_CANDIDATE_INSTALLED_ENABLED','id':'implementaudit@implementaudit','installed':True,'enabled':True,
                  'source_image_path_bound':True,'five_exact_skill_paths':True,'skills':sorted(selected,key=lambda r:r['name']),
                  'other_skill_count':0,'declared_hook_count':0,'declared_app_count':0,'declared_mcp_count':0}
        need(encoded(case['catalog'])==encoded(expected),'CONTENT_CANDIDATE_PUBLIC_PROJECTION')
    else:need(case['catalog'] is None,'CONTENT_STANDALONE_CATALOG_CEILING')
    first=4 if canonical else 2;skills=responses[first]
    need(type(skills) is dict and set(skills)=={'data'} and type(skills['data']) is list and len(skills['data'])==1,'CONTENT_SKILLS_ENVELOPE')
    row=skills['data'][0];need(type(row) is dict and set(row)=={'cwd','skills','errors'} and row['cwd']==cwd and row['errors']==[]
         and type(row['skills']) is list and len(row['skills'])<=128,'CONTENT_SKILLS_SCOPE')
    selected=[];other=[]
    for skill in row['skills']:
        need(type(skill) is dict and type(skill.get('name')) is str and type(skill.get('path')) is str,'CONTENT_SKILL_ROW')
        logical=skill['name'][len('implementaudit:'):] if canonical and skill['name'].startswith('implementaudit:') else 'implementaudit' if not canonical and skill['name']=='implementaudit' else None
        if (canonical and logical not in names) or (not canonical and logical!='implementaudit'):
            need(skill.get('pluginId')!='implementaudit@implementaudit' and not Path(skill['path']).is_relative_to(ctx['effective']),'CONTENT_UNATTRIBUTED_CANDIDATE_SKILL');other.append(skill);continue
        rel='skills/'+logical+'/SKILL.md' if canonical else 'SKILL.md'
        need(skill['path']==str(ctx['effective']/rel) and skill.get('enabled') is True and skill.get('pluginId')==('implementaudit@implementaudit' if canonical else None),'CONTENT_EFFECTIVE_SKILL_BINDING')
        selected.append({'name':skill['name'],'logical_name':logical,'relative_path':rel,'sha256':matrix[rel]['sha256'],'enabled':True})
    wanted=set(names) if canonical else {'implementaudit'}
    need(len(selected)==len(wanted) and {r['logical_name'] for r in selected}==wanted,'CONTENT_EFFECTIVE_SKILL_POPULATION')
    expected={'selected_entries':sorted(selected,key=lambda r:r['name']),'selected_count':len(selected),'other_entry_count':len(other),
              'other_entries_sha256':digest(encoded(other)),'selected_enabled':True}
    need(encoded(case['skills'])==encoded(expected),'CONTENT_SKILLS_PUBLIC_PROJECTION')
    need(encoded(responses[first+1])==encoded({'data':[{'cwd':cwd,'hooks':[],'errors':[],'warnings':[]}]}),'CONTENT_HOOKS_EXACT_SCOPE')
    thread=responses[first+2];sandbox=thread.get('sandbox')
    need(thread.get('model')=='dg17-canonical-routing-fixture' and thread.get('modelProvider')=='dg17_loopback' and thread.get('cwd')==cwd
         and thread.get('approvalPolicy')=='never' and thread.get('approvalsReviewer')=='user'
         and content_compact(sandbox) in (content_compact({'type':'readOnly','networkAccess':False}),content_compact({'type':'readOnly'}))
         and thread.get('instructionSources',[])==[] and thread.get('disabledPluginIds',[])==[],'CONTENT_THREAD_POLICY')
    t=thread['thread'];need(t.get('ephemeral') is True and t.get('cwd')==cwd and t.get('modelProvider')=='dg17_loopback'
         and t.get('turns')==[] and t.get('parentThreadId') is None,'CONTENT_THREAD_FRESH_EPHEMERAL')

def content_identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'mode':stat.S_IMODE(info.st_mode),
            'uid':info.st_uid,'gid':info.st_gid,'links':info.st_nlink,'bytes':info.st_size,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}


def content_directory(path,private=False):
    info=path.lstat()
    need(stat.S_ISDIR(info.st_mode) and path.is_absolute() and path.resolve(strict=True)==path
         and info.st_uid==os.getuid() and info.st_gid==os.getgid() and not info.st_mode&0o022
         and (not private or stat.S_IMODE(info.st_mode)==0o700),'CONTENT_DIRECTORY_SHAPE')
    return content_identity(info)


def content_file(path,limit,collect=False):
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid() and
         before.st_gid==os.getgid() and not before.st_mode&0o022 and 0<=before.st_size<=limit,'CONTENT_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW);size=0;h=hashlib.sha256();parts=[]
    try:
        need(content_identity(os.fstat(fd))==content_identity(before),'CONTENT_FILE_OPEN_CHANGED')
        while True:
            chunk=os.read(fd,1048576)
            if not chunk:break
            size+=len(chunk);need(size<=before.st_size,'CONTENT_FILE_READ_BOUND');h.update(chunk)
            if collect:parts.append(chunk)
        need(size==before.st_size and content_identity(os.fstat(fd))==content_identity(before)
             and content_identity(path.lstat())==content_identity(before),'CONTENT_FILE_CHANGED')
    finally:os.close(fd)
    return b''.join(parts),{'bytes':size,'sha256':h.hexdigest(),'identity':content_identity(before)}


def content_private_json(path,limit=8388608):
    raw,_=content_file(path,limit,True)
    return content_json(raw,limit)


def content_convert_identity(row):
    need(type(row) is dict and set(row)=={'device','inode','mode','uid','gid','nlink','bytes','mtime_ns','ctime_ns'},'CONTENT_IDENTITY_CONVERSION')
    return {('links' if key=='nlink' else key):(stat.S_IMODE(value) if key=='mode' else value) for key,value in row.items()}


def content_package_child_snapshot(snapshot):
    files={};dirs={}
    for row in snapshot['members']:
        identity=content_convert_identity(row['identity'])
        if row['kind']=='DIRECTORY':dirs[row['path']]=identity
        else:files[row['path']]={'bytes':row['bytes'],'sha256':row['sha256'],'identity':identity}
    return {'root_identity':content_convert_identity(snapshot['root_identity']),'files':files,'directories':dirs,
            'member_count':len(files),'bytes':sum(row['bytes'] for row in files.values())}


def content_metadata_census(output):
    private=output/'private/canonical-routing';owners=[('evidence',private,())]
    for family in ('canonical',):
        ctx=content_context(family,output)
        owners.extend([(family+'-home',ctx['home'],(ctx['effective'],)),(family+'-tmp',ctx['tmp'],())])
    rows=[];total=0;directories=[]
    try:
        for owner,root,exclusions in owners:
            content_directory(root,True);pending=[root]
            while pending:
                here=pending.pop();before=here.lstat();directories.append((here,content_identity(before)))
                with os.scandir(here) as stream:entries=list(stream)
                for entry in entries:
                    path=here/entry.name;info=path.lstat()
                    if path in exclusions:
                        need(stat.S_ISDIR(info.st_mode) and path.resolve(strict=True)==path,'CONTENT_PAYLOAD_EXCLUSION_TYPE');continue
                    if path==private/'PRIVATE_EVIDENCE_SEAL.json':
                        need(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'CONTENT_SEAL_EXCLUSION_TYPE');continue
                    need(info.st_uid==os.getuid() and info.st_gid==os.getgid() and not info.st_mode&0o022,'CONTENT_METADATA_OWNER')
                    name=owner+'/'+path.relative_to(root).as_posix()
                    if stat.S_ISDIR(info.st_mode):
                        need(path.resolve(strict=True)==path,'CONTENT_METADATA_DIRECTORY_ALIAS');pending.append(path)
                        rows.append({'path':name,'kind':'DIRECTORY'})
                    else:
                        need(stat.S_ISREG(info.st_mode),'CONTENT_METADATA_NONREGULAR')
                        _,observed=content_file(path,8388608);total+=observed['bytes']
                        need(total<=33554432,'CONTENT_METADATA_TOTAL')
                        rows.append({'path':name,'kind':'REGULAR','bytes':observed['bytes'],'sha256':observed['sha256']})
                    need(len(rows)<=2048,'CONTENT_METADATA_POPULATION')
        need(all(content_identity(path.lstat())==identity for path,identity in directories),'CONTENT_METADATA_DIRECTORY_DRIFT')
    except OSError:raise Refusal('CONTENT_METADATA_ENUMERATION_OR_READ_REFUSED') from None
    return sorted(rows,key=lambda row:row['path'])


def content_expected_private_files():
    root={'SELECTION_METADATA_BEFORE.json','SELECTION_METADATA_AFTER.json','REVIEW_PACKET_BEFORE.json','OWNER_SELECTION.json','SOURCE_BEFORE.json','RUNTIME_BEFORE.json','GIT_BEFORE.json','EXECUTION_ROUTE_ENVELOPE.json',
          'GIT_AFTER.json','SOURCE_AFTER.json','RUNTIME_AFTER.json','REVIEW_PACKET_AFTER.json','CURRENTNESS_COMMANDS.json','PAYLOAD_OWNERS.json','RUNTIME_OWNER.json'}
    for gate in ('gate-before','gate-after'):root.update(gate+suffix for suffix in ('.stdout','.stderr','.capture.json'))
    case={'PACKAGE_BEFORE.json','HELPERS_BEFORE_NATIVE.json','CONFIG_BEFORE_NATIVE.json','ALIASES_AFTER_INITIALIZE.json','HELPERS_AFTER_INITIALIZE.json',
          'CONFIG_AFTER_INSTALL.json','EFFECTIVE_BEFORE_TURN.json','SELECTED_DOCUMENTS.json','ALIASES_BEFORE_TURN.json','HELPERS_BEFORE_TURN.json',
          'PROVIDER.json','ROUTE_CONTEXT.json','ALIASES_AFTER_CLOSE.json','HELPERS_AFTER_CLOSE.json','PACKAGE_AFTER_CLOSE.json','CONFIG_AFTER_CLOSE.json','CASE_RESULT.json'}
    case.update('PHASE_'+phase+'_ADMISSION.json' for phase in ('P1','P2','P3','P4','C1','P5','P6','P7'))
    case.update('native/'+name for name in ('native.stdout','native.stderr','native.sends.jsonl','NATIVE_SEND_STATUS.json','NATIVE_EVENTS.json','native.capture.json','NATIVE_OWNERSHIP.json'))
    case.update('http/'+str(i)+suffix for i in range(1,9) for suffix in ('.header','.body','.response.prepared'))
    return {'evidence/'+name for name in root}|{'evidence/canonical/'+name for name in case}


def content_startup_readback(ctx,source):
    for root in (source,ctx['image'],ctx['cwd']):
        for ancestor in (root,*root.parents):
            for name in ('config.toml','hooks.json','managed_config.toml','requirements.toml'):
                need(not os.path.lexists(ancestor/'.codex'/name),'CONTENT_PROJECT_STARTUP_LAYER')
    for ancestor in (ctx['cwd'],*ctx['cwd'].parents):
        for name in ('AGENTS.md','AGENTS.override.md','.agents/skills'):
            need(not os.path.lexists(ancestor/name),'CONTENT_NEUTRAL_INSTRUCTION_LAYER')
    for name in ('config.toml','managed_config.toml','requirements.toml','hooks.json'):
        need(not os.path.lexists(Path('/etc/codex')/name),'CONTENT_SYSTEM_STARTUP_LAYER')
    for name in ('auth.json','auth.json.tmp','managed_config.toml','requirements.toml','hooks.json','.env','AGENTS.md','AGENTS.override.md','.gitconfig','.config/git/config'):
        need(not os.path.lexists(ctx['home']/name),'CONTENT_NATIVE_HOME_STARTUP_LAYER')
    for name in ('plugin.json','.mcp.json','.app.json','hooks/hooks.json','commands','.codex-plugin/migrated-command-skills'):
        need(not os.path.lexists(ctx['image']/name),'CONTENT_PACKAGE_ACTIVE_EXTRAS')
    content_directory(ctx['cwd'],True)
    with os.scandir(ctx['cwd']) as stream:need(list(stream)==[],'CONTENT_NEUTRAL_CHANGED')


def content_config_receiving(ctx,evidence,port):
    before=content_private_json(evidence/'CONFIG_BEFORE_NATIVE.json')
    after=content_private_json(evidence/'CONFIG_AFTER_CLOSE.json')
    for row in (before,after):
        need(type(row) is dict and set(row)=={'bytes','sha256','identity','document'} and type(row['bytes']) is int
             and 0<row['bytes']<=32768 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,
             'CONTENT_CONFIG_SNAPSHOT')
        identity=row['identity'];need(type(identity) is dict and identity.get('uid')==os.getuid() and identity.get('gid')==os.getgid()
             and identity.get('mode') in (0o600,0o644) and identity.get('links')==1 and identity.get('bytes')==row['bytes'],'CONTENT_CONFIG_IDENTITY')
    initial_raw=content_initial_config_bytes(ctx,port)
    need(content_compact(before['document'])==content_compact(content_expected_config(ctx,port,False))
         and before['bytes']==len(initial_raw) and before['sha256']==digest(initial_raw),'CONTENT_INITIAL_CONFIG_PROFILE')
    canonical=ctx['family']=='canonical'
    if canonical:need(encoded(content_private_json(evidence/'CONFIG_AFTER_INSTALL.json'))==encoded(after),'CONTENT_INSTALLED_CONFIG_BOOKEND')
    else:need(encoded(before)==encoded(after),'CONTENT_STANDALONE_CONFIG_BOOKEND')
    raw,file=content_file(ctx['home']/'config.toml',32768,True);document=tomllib.loads(raw.decode('utf-8','strict'))
    actual={'bytes':file['bytes'],'sha256':file['sha256'],'identity':file['identity'],'document':document}
    need(content_compact(document)==content_compact(content_expected_config(ctx,port,canonical)) and encoded(actual)==encoded(after),'CONTENT_CONFIG_ACTUAL_READBACK')


def content_helper_row_receiving(row,requested,system):
    need(type(row) is dict and set(row)=={'present','path','resolved','ancestry','bytes','sha256','mtime_ns','ctime_ns'}
         and row['present'] is True and row['path']==str(requested) and row['resolved']==system['canonical']
         and type(row['bytes']) is int and row['bytes']==system['bytes'] and row['sha256']==system['sha256']
         and row['mtime_ns']==system['identity']['mtime_ns'] and row['ctime_ns']==system['identity']['ctime_ns'],'CONTENT_HELPER_TOOL_BINDING')
    expected_paths=set(map(str,(requested,*requested.parents,Path(system['canonical']),*Path(system['canonical']).parents)))
    # /bin's protected symlink also brings /usr/bin's physical ancestry into the source-derived snapshot.
    if str(requested).startswith('/bin/'):expected_paths.update(('/usr','/usr/bin'))
    need(type(row['ancestry']) is dict and set(row['ancestry'])==expected_paths,'CONTENT_HELPER_ANCESTRY_POPULATION')
    for text,item in row['ancestry'].items():
        path=Path(text);info=path.lstat();actual={'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,'gid':info.st_gid,'mode':info.st_mode}
        if stat.S_ISLNK(info.st_mode):actual['link_sha256']=digest(os.fsencode(os.readlink(path)))
        need(encoded(actual)==encoded(item),'CONTENT_HELPER_ANCESTRY_CHANGED')


def content_helpers_receiving(ctx,evidence,output,system):
    launch=output/'canonical-routing-runtime'/ctx['family']/'owned-binary'
    expected_absent=[str(launch/'codex-resources'),str(launch.parent/'codex-resources'),str(launch/'bwrap'),str(launch/'codex-path')]
    need(all(not os.path.lexists(path) for path in expected_absent),'CONTENT_BUNDLED_FALLBACK_PRESENT')
    rows=[content_private_json(evidence/name) for name in ('HELPERS_BEFORE_NATIVE.json','HELPERS_AFTER_INITIALIZE.json','HELPERS_BEFORE_TURN.json','HELPERS_AFTER_CLOSE.json')]
    need(all(encoded(row)==encoded(rows[0]) for row in rows),'CONTENT_HELPER_BOOKENDS')
    row=rows[0];need(type(row) is dict and set(row)=={'tools','bin_aliases','absent_candidates','install_context','managed_bazel_environment_absent','native_initial_path','system_capability_fallback'}
         and row['absent_candidates']==expected_absent and row['install_context']=='OTHER_FIXED_OWNED_BINARY_LEAF'
         and row['managed_bazel_environment_absent'] is True and row['native_initial_path']=='/usr/bin:/bin'
         and row['system_capability_fallback']=='UNAVAILABLE_WHEN_SYSTEM_REJECTED','CONTENT_HELPER_CLOSED_PROFILE')
    tools={r['name']:r for r in system['helpers']}
    need(type(row['tools']) is dict and set(row['tools'])==set(tools) and type(row['bin_aliases']) is dict
         and set(row['bin_aliases'])=={'bash','cat','bwrap','true'},'CONTENT_HELPER_POPULATION')
    for name,value in row['tools'].items():content_helper_row_receiving(value,Path('/usr/bin')/name,tools[name])
    for name,value in row['bin_aliases'].items():content_helper_row_receiving(value,Path('/bin')/name,tools[name])
    live=content_private_json(evidence/'ALIASES_AFTER_INITIALIZE.json')
    need(encoded(live)==encoded(content_private_json(evidence/'ALIASES_BEFORE_TURN.json')),'CONTENT_ARG0_ALIAS_BOOKENDS')
    need(type(live) is dict and set(live)=={'live','roots','present_unrequested_aliases'} and live['live'] is True
         and live['present_unrequested_aliases']==['apply_patch','applypatch'] and type(live['roots']) is list and len(live['roots'])==1,'CONTENT_ARG0_ROOT_POPULATION')
    root=live['roots'][0];need(type(root) is dict and set(root)=={'path','identity','members'} and type(root['path']) is str,'CONTENT_ARG0_ROOT_SHAPE')
    alias_root=Path(root['path']);need(alias_root.parent==ctx['home']/'tmp/arg0-linux' and re.fullmatch('codex-arg0[A-Za-z0-9_-]+',alias_root.name) is not None
         and root['identity']['uid']==os.getuid() and root['identity']['gid']==os.getgid() and root['identity']['mode']==0o700,'CONTENT_ARG0_FIXED_PARENT')
    members=root['members'];need(type(members) is list and [x.get('name') for x in members]==['.lock','apply_patch','applypatch','codex-linux-sandbox'],'CONTENT_ARG0_MEMBER_POPULATION')
    for member in members:
        identity=member.get('identity');need(type(identity) is dict and identity.get('uid')==os.getuid() and identity.get('gid')==os.getgid(),'CONTENT_ARG0_OWNER')
        if member['name']=='.lock':need(set(member)=={'name','kind','identity'} and member['kind']=='REGULAR' and identity.get('links')==1 and identity.get('bytes')==0 and type(identity.get('mode')) is int and not identity['mode']&0o022,'CONTENT_ARG0_LOCK')
        else:need(set(member)=={'name','kind','identity','target'} and member['kind']=='SAME_RUNTIME_SYMLINK' and member['target']==str(launch/'codex'),'CONTENT_ARG0_LINK_TARGET')
    closed=content_private_json(evidence/'ALIASES_AFTER_CLOSE.json')
    need(encoded(closed)==encoded({'live':False,'roots':[],'present_unrequested_aliases':[]}),'CONTENT_ARG0_CLOSED_RECORD')
    path=ctx['home']/'tmp/arg0-linux'
    if os.path.lexists(path):
        content_directory(path,True)
        with os.scandir(path) as stream:need(list(stream)==[],'CONTENT_ARG0_AFTER_CLOSE_NOT_EMPTY')


def content_process_receiving(ctx,evidence,case,output,packet,u):
    root=evidence/'native';record=content_private_json(root/'native.capture.json',65536)
    need(type(record) is list and len(record)==1 and content_capture_base_shape(record[0],'native-content')
         and encoded(record[0])==encoded(case['capture']),'CONTENT_NATIVE_CAPTURE_REQUIRED_FIELDS')
    for key,limit in (('stdout',2097152),('stderr',131072)):
        raw,_=content_file(root/('native.'+key),limit,True)
        need(record[0][key+'_bytes']==len(raw) and record[0][key+'_sha256']==digest(raw),'CONTENT_NATIVE_CAPTURE_BYTES')
    owner=content_private_json(root/'NATIVE_OWNERSHIP.json');launch=output/'canonical-routing-runtime'/ctx['family']/'owned-binary'
    environment={**u.safe_environment(),'HOME':str(ctx['home']),'CODEX_HOME':str(ctx['home']),'TMPDIR':str(ctx['tmp']),
                 'LANG':'C.UTF-8','LC_ALL':'C.UTF-8',**{'XDG_'+name+'_HOME':str(ctx['home']/('xdg-'+name.lower())) for name in ('CONFIG','CACHE','DATA','STATE')}}
    need(type(owner) is dict and set(owner)=={'argv','environment','process_identity','copy_identity','copy_removed','full_scope_readback'}
         and owner['argv']==[str(launch/'codex'),'app-server','--listen','stdio://','--strict-config']
         and encoded(owner['environment'])==encoded(environment) and owner['copy_removed'] is True
         and encoded(owner['full_scope_readback'])==encoded(case['runtime_scope']),'CONTENT_NATIVE_EFFECT_RECORD')
    copy=owner['copy_identity'];need(type(copy) is dict and set(copy)=={'bytes','sha256','identity'} and copy['bytes']==BINARY_BYTES and copy['sha256']==BINARY_SHA,'CONTENT_RUNTIME_COPY_PIN')
    ident=copy['identity'];need(type(ident) is dict and ident.get('uid')==os.getuid() and ident.get('gid')==os.getgid()
         and ident.get('mode')==0o700 and ident.get('links')==1 and ident.get('bytes')==BINARY_BYTES,'CONTENT_RUNTIME_COPY_IDENTITY')
    process=owner['process_identity'];keys={'visible_pid','parent_visible_pid','namespace_pids','namespace_sessions','namespace_groups','start_ticks','proc_device','proc_inode','namespace_device','namespace_inode','exe'}
    need(type(process) is dict and set(process)==keys and process['exe']==str(launch/'codex')
         and all(type(process[k]) is int and process[k]>0 for k in keys-{'exe','namespace_pids','namespace_sessions','namespace_groups'}),'CONTENT_NATIVE_PROCESS_IDENTITY')
    chains=[process[k] for k in ('namespace_pids','namespace_sessions','namespace_groups')]
    need(all(type(chain) is list and 1<=len(chain)<=32 and all(type(v) is int and v>0 for v in chain) for chain in chains)
         and len({len(c) for c in chains})==1 and chains[0][0]==process['visible_pid'],'CONTENT_NATIVE_PID_NAMESPACE_CHAIN')
    modules={}
    for name,pin in (('namespace_process_custody','6d2e049a8ddbc89e6213c4968d44e6e1483254d852d45480b90f01f960453630'),
                     ('owned_resources','0b7d871aca378dc807bc33211d4b84a1b0baa45939c9c24ca54374c23468e33a'),
                     ('catalogue_probe','b6e13ead54247adfe181ba9e4ea1739bbceb336d89fba0c6aee111462699b551')):
        raw=read(packet/(name+'.py'));need(digest(raw)==pin,'CONTENT_CUSTODY_HELPER_PIN')
        mod=types.ModuleType('dg17_content_parent_'+name);mod.__file__=str(packet/(name+'.py'));exec(compile(raw,mod.__file__,'exec'),mod.__dict__);modules[name]=mod
    self_identity=modules['namespace_process_custody'].observe('/proc/self');depth=len(self_identity['namespace_pids'])
    need(len(chains[0])==depth and process['namespace_inode']==self_identity['namespace_inode'] and process['namespace_device']==self_identity['namespace_device']
         and chains[0][-1]==chains[1][-1]==chains[2][-1],'CONTENT_NATIVE_SESSION_LEADER')
    subject=types.SimpleNamespace(launch_dir=launch,process_identity=process,custody=types.SimpleNamespace(depth=depth))
    observed=modules['catalogue_probe'].independent_readback(subject,modules)
    need(encoded(observed)==encoded(case['runtime_scope']) and observed['full_session_scope_available'] is True and observed['launch_directory_empty'] is True
         and all(type(observed[k]) is int and observed[k]==0 for k in ('living_owned_processes','owned_zombies','uncertain_owned_candidates')),'CONTENT_PARENT_SESSION_READBACK')


def receive_content_private(state,output,source):
    packet=Path(__file__).absolute().parent;private=output/'private/canonical-routing';value=state['content'];flags=state['content_validation'];u=utility(packet)
    need(content_success(value,os.getuid(),os.getgid(),state['receipt']),'CONTENT_PRIVATE_RECEIVING_UNSOUND_ROUTE')
    content_directory(private,True);content_directory(output/'canonical-routing-payloads',True)
    with os.scandir(output/'canonical-routing-payloads') as stream:need({e.name for e in stream}=={'canonical'},'CONTENT_PAYLOAD_FAMILY_POPULATION')
    selection=route_inputs_recheck(state,output,packet,'private-receiving')
    need(encoded(content_private_json(private/'REVIEW_PACKET_BEFORE.json'))==encoded(selection['review'])==encoded(content_private_json(private/'REVIEW_PACKET_AFTER.json')) and encoded(content_private_json(private/'OWNER_SELECTION.json'))==encoded(selection['owner']),'ROUTE_REVIEW_OWNER_PRIVATE_BOOKENDS')
    need(encoded(content_private_json(private/'SELECTION_METADATA_BEFORE.json'))==encoded(selection['metadata'])==encoded(content_private_json(private/'SELECTION_METADATA_AFTER.json')),'SELECTION_METADATA_PRIVATE_BOOKENDS')
    system=content_system_recheck(state,output,u,'private-receiving')
    source_now=source_check(source,packet);need(source_now==state['source_before'],'CONTENT_FULL_SOURCE_CHANGED')
    store=currentness_store_snapshot(source,packet);need(store==state['currentness_store_before'],'CONTENT_SOURCE_STORE_CHANGED')
    pins=content_json(read(packet/'SOURCE_INPUT_PINS.json',32768),32768);inputs={}
    need(digest(read(packet/'SOURCE_INPUT_PINS.json'))=='d5e1e1e9abeeaa79500acc0c41f1555df4a1dc6e5a50259a94db8895500edaad','CONTENT_SOURCE_INPUT_PINS')
    for member in pins['members']:
        _,row=content_file(source/member['path'],8388608)
        need(row['bytes']==member['bytes'] and row['sha256']==member['sha256'],'CONTENT_SUPPLEMENTAL_SOURCE_BYTES');inputs[member['path']]=row
    need(encoded({'inputs':inputs,'store':store['guard']})==encoded(content_private_json(private/'SOURCE_BEFORE.json'))==encoded(content_private_json(private/'SOURCE_AFTER.json')),'CONTENT_SOURCE_PRIVATE_BOOKENDS')
    _,runtime=content_file(output/'private/codex-input',BINARY_BYTES)
    need(runtime['bytes']==BINARY_BYTES and runtime['sha256']==BINARY_SHA and runtime['identity']['mode']==0o700
         and encoded(runtime)==encoded(content_private_json(private/'RUNTIME_BEFORE.json'))==encoded(content_private_json(private/'RUNTIME_AFTER.json')),'CONTENT_RUNTIME_INPUT_BOOKENDS')
    before=content_private_json(private/'GIT_BEFORE.json');after=content_private_json(private/'GIT_AFTER.json')
    need(type(before) is dict and set(before)=={'resolver','git','libexec','helpers','system_config','home','source_store'}
         and encoded(before)==encoded(after) and before['source_store']==store['guard'],'CONTENT_GIT_BOOKENDS')
    selected=before['git'];admitted=state['host']['tools']['git'];config=before['system_config']
    need(selected.get('resolved')=='/usr/bin/git' and selected.get('sha256')==admitted['sha256'] and selected.get('bytes')==admitted['bytes']
         and config.get('present') is True and config.get('bytes')==0 and config.get('sha256')==digest(b''),'CONTENT_GIT_CAPSULE_JOIN')
    gate_home=output/'home';home_identity=gate_home.lstat();content_directory(gate_home,True)
    need(before['home']=={'device':home_identity.st_dev,'inode':home_identity.st_ino,'uid':home_identity.st_uid,
                         'gid':home_identity.st_gid,'mode':home_identity.st_mode,'global_paths_absent':True},'CONTENT_GIT_HOME_IDENTITY')
    for ancestor in (gate_home,*gate_home.parents):need(not os.path.lexists(ancestor/'.git'),'CONTENT_GIT_METADATA_CWD_REPOSITORY')
    for relative in ('.gitconfig','.config/git/config'):need(not os.path.lexists(gate_home/relative),'CONTENT_GIT_GLOBAL_CONFIG_PRESENT')
    for relative in ('.config','.config/git'):
        if os.path.lexists(gate_home/relative):content_directory(gate_home/relative)
    # This is the retained helper's exact identity codec: compact sorted JSON, no LF.
    flags['git_snapshot_identity_sha256']=digest(json.dumps(before,sort_keys=True,separators=(',',':')).encode())
    gates=content_private_json(private/'CURRENTNESS_COMMANDS.json')
    need(type(gates) is list and len(gates)==2,'CONTENT_CURRENTNESS_CAPTURE_POPULATION')
    for name,row in zip(('gate-before','gate-after'),gates):
        need(content_capture_base_shape(row,name) and content_private_json(private/(name+'.capture.json'),65536)==[row]
             and row['process_started'] is True and row['returncode']==0 and row['streams_complete'] is True and row['pidfd_acquired'] is True
             and row['timeout'] is False and row['output_bound_exceeded'] is False and row['private_streams_retained'] is True
             and row['retention_failure'] is False and row['cleanup']['echild'] is True,'CONTENT_CURRENTNESS_CAPTURE_CUSTODY')
        stdout,_=content_file(private/(name+'.stdout'),32768,True);stderr,_=content_file(private/(name+'.stderr'),32768,True)
        need(stdout==(state['receipt']+'\n').encode() and stderr==b'' and row['stdout_bytes']==len(stdout) and row['stdout_sha256']==digest(stdout)
             and row['stderr_bytes']==0 and row['stderr_sha256']==digest(b'') and value['currentness_receipt_sha256']==digest(stdout),'CONTENT_CURRENTNESS_RECEIPT')
    owners=[];package_rows=[]
    for family,case in zip(('canonical',),value['cases']):
        ctx=content_context(family,output);evidence=private/family;population=content_archive_population(packet,family)
        content_directory(evidence,True);identity=content_directory(ctx['root'],True)
        wanted={'home','neutral','tmp'}|({'source-package'} if family=='canonical' else set())
        with os.scandir(ctx['root']) as stream:need({e.name for e in stream}==wanted,'CONTENT_PAYLOAD_CASE_POPULATION')
        owners.append({'family':family,'identity':{k:identity[k] for k in ('device','inode','mode','uid','gid')},'children':sorted(wanted)})
        for path in (ctx['home'],ctx['tmp']):content_directory(path,True)
        content_startup_readback(ctx,source)
        image=content_package_child_snapshot(content_package_snapshot(ctx['image'],population))
        effective=content_package_child_snapshot(content_package_snapshot(ctx['effective'],population))
        _,archive=content_file(content_archive_input(packet,family),population['spec']['bytes'])
        need(encoded({'archive':archive,'image':image})==encoded(content_private_json(evidence/'PACKAGE_BEFORE.json'))
             and encoded({'archive':archive,'image':image,'effective':effective})==encoded(content_private_json(evidence/'PACKAGE_AFTER_CLOSE.json'))
             and encoded(effective)==encoded(content_private_json(evidence/'EFFECTIVE_BEFORE_TURN.json')),'CONTENT_COMPLETE_PACKAGE_BOOKENDS')
        need(encoded(case)==encoded(content_private_json(evidence/'CASE_RESULT.json')),'CONTENT_CASE_PRIVATE_PUBLIC_BINDING')
        content_helpers_receiving(ctx,evidence,output,system)
        content_process_receiving(ctx,evidence,case,output,packet,u)
        native_raw,_=content_file(evidence/'native/native.stdout',2097152,True)
        native_responses={row['id']:row['result'] for row in (r_json(line,262144) for line in native_raw.splitlines()) if type(row) is dict and set(row)=={'id','result'} and type(row['id']) is int}
        need(type(native_responses.get(6)) is dict and type(native_responses.get(7)) is dict,'ROUTE_THREAD_TURN_RESULTS')
        parent=r_identity(native_responses[6].get('thread',{}).get('id'));turn=r_identity(native_responses[7].get('turn',{}).get('id'))
        port,route_ctx,docs,http=route_provider_receiving(output,evidence,case,packet,parent,turn)
        content_config_receiving(ctx,evidence,port)
        responses,observed=route_wire_receiving(route_ctx,evidence,case,docs,http)
        content_rpc_receiving(ctx,case,responses,population)
        route_selected_documents(evidence,ctx,case,population)
        flags['routing_protocol_observations']=observed
        package_rows.append({'family':family,'source_files':len(image['files']),'effective_files':len(effective['files']),
                             'source_bytes':image['bytes'],'effective_bytes':effective['bytes'],'source_equals_effective_bytes':True})
    need(encoded(owners)==encoded(content_private_json(private/'PAYLOAD_OWNERS.json')),'CONTENT_PAYLOAD_OWNERS_JOIN')
    runtime_owner=content_runtime_owner(output,True)
    converted=[{**row,'identity':content_convert_identity(row['identity'])} for row in runtime_owner['members']]
    runtime_raw,_=content_file(private/'RUNTIME_OWNER.json',8388608,True)
    need(encoded(converted)==encoded(content_json(runtime_raw)) and digest(runtime_raw)==value['cleanup']['runtime_owner_sha256'],'CONTENT_RUNTIME_OWNER_JOIN')
    seal_raw,_=content_file(private/'PRIVATE_EVIDENCE_SEAL.json',8388608,True);seal=content_json(seal_raw)
    need(type(seal) is dict and set(seal)=={'schema','members'} and seal['schema']=='dg17.codex.routing.private-seal.v1'
         and digest(seal_raw)==value['cleanup']['private_seal_sha256'],'CONTENT_PRIVATE_SEAL_IDENTITY')
    rows=content_metadata_census(output)
    need(encoded(rows)==encoded(seal['members']) and {r['path'] for r in rows if r['kind']=='REGULAR' and r['path'].startswith('evidence/')}==content_expected_private_files(),'CONTENT_PRIVATE_COMPLETE_POPULATION')
    need(content_file(private/'PRIVATE_EVIDENCE_SEAL.json',8388608,True)[0]==seal_raw,'CONTENT_PRIVATE_SEAL_READBACK')
    flags.update(full_source_store_independently_received=True,complete_packages_and_effective_paths_received=True,
                 exact_runtime_and_helper_routes_received=True,private_native_protocol_and_provider_received=True,
                 same_receipt_private_readbacks_verified=True,private_seal_verified_after_child_reaping=True,
                 private_member_count=len(rows),payload_populations=package_rows,runtime_copies_remaining=0,
                 raw_prefix_and_full_body_distinct=True,system_only_sandbox_route_received=True,
                 exact_review_owner_and_complete_data_received=True,native_selected_child_and_first_return_joined=True,
                 scripted_nonverdict_only=True,substantive_composition_review_pending=True)

def body_network_snapshot_valid(value, parent_namespace):
    keys = {'network_namespace_sha256','namespace_distinct','interfaces','loopback_up','loopback_flags',
            'loopback_address','external_routes','ipv4_route_count','ipv6_route_count','route_population_sha256'}
    if type(value) is not dict or set(value) != keys: return False
    if type(parent_namespace) is not str or re.fullmatch(r'net:\[[0-9]+\]',parent_namespace) is None: return False
    if not all(type(value[k]) is str and re.fullmatch('[0-9a-f]{64}',value[k]) for k in
               ('network_namespace_sha256','route_population_sha256')): return False
    if value['network_namespace_sha256'] == digest(parent_namespace.encode()) or value['namespace_distinct'] is not True: return False
    if value['interfaces'] != ['lo'] or value['loopback_up'] is not True or value['loopback_address'] != '127.0.0.1': return False
    if type(value['loopback_flags']) is not int or value['loopback_flags'] not in (9,73): return False
    if type(value['external_routes']) is not int or value['external_routes'] != 0: return False
    if any(type(value[k]) is not int or not 0 <= value[k] <= 32 for k in ('ipv4_route_count','ipv6_route_count')): return False
    return True

def utility(packet):
    raw = read(packet/'host_utility.py'); need(digest(raw) == UTILITY_SHA, 'UTILITY_PIN')
    module = types.ModuleType('dg17_retained_host_utility'); module.__file__ = str(packet/'host_utility.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module

def source_check(source, packet):
    raw = read(packet/'SOURCE_MANIFEST.json'); need(digest(raw) == MANIFEST_SHA, 'MANIFEST_PIN')
    manifest = json.loads(raw); need(manifest['expected_tree'] == TREE and manifest['file_count'] == 1755 and manifest['total_bytes'] == 165855954, 'MANIFEST_SUBJECT')
    members = manifest['members']; seen = set(); total = 0
    for row in members:
        path = source/row['path']; info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == (0o755 if row['mode'] == '100755' else 0o644), 'SOURCE_FILE_SHAPE')
        size, sha = stream_hash(path)
        need(size == row['bytes'] and sha == row['sha256'], 'SOURCE_BYTES')
        seen.add(row['path']); total += size
    need(len(seen) == 1755 and total == 165855954, 'SOURCE_POPULATION')
    observed = set(); pending = [source]
    try:
        while pending:
            here = pending.pop()
            with os.scandir(here) as stream:
                entries = list(stream)
            for entry in entries:
                path = here/entry.name; mode = path.lstat().st_mode
                need(not stat.S_ISLNK(mode), 'SOURCE_DIRECTORY_ALIAS')
                if stat.S_ISDIR(mode):
                    if here == source and entry.name in ('.git', '.IMPLEMENTAUDIT'): continue
                    pending.append(path)
                else: observed.add(path.relative_to(source).as_posix())
    except OSError:
        raise Refusal('SOURCE_ENUMERATION_REFUSED') from None
    need(observed == seen, 'SOURCE_EXTRA_OR_MISSING_MEMBER')
    return {'commit': SOURCE, 'tree': TREE, 'parent': PARENT, 'files': len(seen), 'bytes': total, 'all_manifest_members_match': True}

def canonical_hashes(source, state):
    return {name: digest(read(source/state['run_root']/name)) for name in DOCS}

def command(state, output, u, label, argv, seconds=60):
    env_args = ['/usr/bin/env', 'HOME='+str(output/'home'), 'CODEX_HOME='+str(output/'home/codex'), 'TMPDIR='+str(output/'tmp')]
    state['active_command'] = label; save(output/'private/episode.json', state)
    try:
        try:
            rc, stdout, stderr = u.capture(label, env_args+argv, state['commands'], time.monotonic()+seconds+5, seconds=seconds)
        except BaseException as exc:
            captured = getattr(exc, 'captured', None)
            if captured is not None:
                for suffix in ('stdout', 'stderr'):
                    raw = captured[suffix]; need(type(raw) is bytes and len(raw) <= 32768, 'FAILURE_CAPTURE_SHAPE')
                    with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
            raise
        for suffix, raw in (('stdout', stdout), ('stderr', stderr)):
            with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
        state['active_command'] = None
        need(rc == 0, 'COMMAND_NONZERO_'+label)
        return stdout
    finally:
        save(output/'private/episode.json', state)

def owner(state, source, output, u, label, *args):
    need(Path.cwd() == source, 'OWNER_CWD')
    return command(state, output, u, label, ['/usr/bin/bash', str(source/CLAIM), *args])

def currentness_store_snapshot(source, packet):
    """Data-only post-resume Git-store admission; no Git or custody subprocess."""
    helper_raw = read(packet/'catalogue_probe.py')
    need(digest(helper_raw) == 'b6e13ead54247adfe181ba9e4ea1739bbceb336d89fba0c6aee111462699b551',
         'CURRENTNESS_STORE_HELPER_PIN')
    helper = types.ModuleType('dg17_parent_source_store_admission')
    helper.__file__ = str(packet/'catalogue_probe.py')
    exec(compile(helper_raw,helper.__file__,'exec'),helper.__dict__)
    guard = helper.source_store_guard(source)
    root = source/'.git'; rows = []; pending = [root]; directories = []; total = 0; files = 0
    def identity(info):
        return {'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
                'uid':info.st_uid,'gid':info.st_gid,'nlink':info.st_nlink,
                'bytes':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
    root_identity = identity(root.lstat())
    try:
        while pending:
            directory = pending.pop(); before = directory.lstat()
            need(stat.S_ISDIR(before.st_mode) and before.st_uid == os.getuid() and
                 not before.st_mode & 0o022 and directory.resolve(strict=True) == directory,
                 'CURRENTNESS_STORE_DIRECTORY')
            directories.append((directory,identity(before)))
            with os.scandir(directory) as stream:
                entries = list(stream)
            need(identity(directory.lstat()) == identity(before), 'CURRENTNESS_STORE_CHANGED')
            for entry in entries:
                path = directory/entry.name; info = path.lstat(); relative = path.relative_to(root)
                need(len(rows) < 65536 and len(relative.parts) <= 32 and len(relative.as_posix()) <= 4096 and
                     info.st_uid == os.getuid() and not info.st_mode & 0o022 and
                     (stat.S_ISDIR(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink == 1)),
                     'CURRENTNESS_STORE_MEMBER')
                row = {'path':relative.as_posix(),'identity':identity(info)}
                if stat.S_ISDIR(info.st_mode):
                    row['kind'] = 'DIRECTORY'; pending.append(path)
                else:
                    need(0 <= info.st_size <= 536870912 and total+info.st_size <= 536870912,
                         'CURRENTNESS_STORE_BYTE_BOUND')
                    fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
                    try:
                        need(identity(os.fstat(fd)) == identity(info), 'CURRENTNESS_STORE_OPEN_CHANGED')
                        hashed = hashlib.sha256(); size = 0
                        while True:
                            chunk = os.read(fd,1048576)
                            if not chunk: break
                            size += len(chunk); need(size <= info.st_size, 'CURRENTNESS_STORE_READ_BOUND')
                            hashed.update(chunk)
                        need(size == info.st_size and identity(os.fstat(fd)) == identity(info) and
                             identity(path.lstat()) == identity(info), 'CURRENTNESS_STORE_CHANGED')
                    finally: os.close(fd)
                    row.update(kind='REGULAR',sha256=hashed.hexdigest()); total += size; files += 1
                rows.append(row)
        need(all(identity(path.lstat()) == observed for path,observed in directories) and
             identity(root.lstat()) == root_identity, 'CURRENTNESS_STORE_CHANGED')
    except OSError:
        raise Refusal('CURRENTNESS_STORE_ENUMERATION_OR_READ_REFUSED') from None
    need(len(rows) == guard['entries_checked'] and
         any(row['path'] == 'config' and row.get('sha256') == guard['config_sha256'] for row in rows) and
         helper.source_store_guard(source) == guard, 'CURRENTNESS_STORE_GUARD_JOIN')
    population = encoded({'root':root_identity,'members':sorted(rows,key=lambda row:row['path'])})
    need(len(population) <= 33554432, 'CURRENTNESS_STORE_CENSUS_BOUND')
    return {'profile':'POST_RESUME_PHYSICAL_GIT_STORE_V1','guard':guard,'entries':len(rows),
            'regular_files':files,'bytes':total,'population_sha256':digest(population)}

def current(state, source, output, u, label):
    need(state.get('receipt') is not None, 'CURRENTNESS_NOT_ESTABLISHED')
    admission = currentness_admission(state,source,output,u,label)
    raw = owner(state, source, output, u, label, '--require-current-continuity', state['controller'])
    need(raw == (state['receipt']+'\n').encode(), 'CURRENTNESS_RECEIPT_DIFFERS')
    state['currentness'].append({'role': label, 'receipt_sha256': digest(raw), 'same_source_cwd': True, 'verified': True, 'pre_execution_admission':admission})
    save(output/'private/episode.json', state)

def acquire_runtime(output):
    archive = output/'private/codex.tar.gz'; started = time.monotonic(); count = 0; h = hashlib.sha256()
    with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as f:
        while True:
            chunk = response.read(1048576)
            if not chunk: break
            count += len(chunk); need(count <= ARCHIVE_BYTES and time.monotonic()-started < 180, 'ARCHIVE_BOUND')
            h.update(chunk); f.write(chunk)
    need(count == ARCHIVE_BYTES and h.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    binary = output/'private/codex-input'
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        need(len(members) == 1 and members[0].isreg() and members[0].name == 'codex-x86_64-unknown-linux-musl' and members[0].size == BINARY_BYTES, 'ARCHIVE_MEMBERS')
        with tar.extractfile(members[0]) as inp, binary.open('xb') as out:
            while True:
                chunk = inp.read(1048576)
                if not chunk: break
                out.write(chunk)
    need(stream_hash(binary) == (BINARY_BYTES, BINARY_SHA), 'BINARY_PIN')
    os.chmod(binary, 0o700)
    return {'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_BYTES, 'binary_sha256': BINARY_SHA, 'binary_bytes': BINARY_BYTES, 'version_subject': 'codex-cli 0.167.0-alpha.4', 'input_retained_until_host_teardown': True}

def mount_role():
    path = Path('/usr/bin/mount').resolve(strict=True); info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and os.access(path, os.X_OK) and stat.S_IMODE(info.st_mode) in (0o755, 0o4755), 'MOUNT_ROLE_MODE')
    for node in (path, *path.parents):
        value = node.lstat(); need(value.st_uid == 0 and not value.st_mode & 0o022, 'MOUNT_ROLE_ANCESTRY')
    try: cap = os.getxattr(path, 'security.capability')
    except OSError as exc:
        need(exc.errno in (errno.ENODATA, errno.ENOTSUP), 'MOUNT_ROLE_CAPABILITY_UNKNOWN'); cap = b''
    need(not cap, 'MOUNT_ROLE_FILE_CAPABILITY')
    with path.open('rb') as stream: header = stream.read(64)
    need(len(header) == 64 and header[:6] == b'\x7fELF\x02\x01' and int.from_bytes(header[18:20], 'little') == 62, 'MOUNT_ROLE_ELF_X64')
    size, sha = stream_hash(path); after = path.lstat()
    identity = lambda x: (x.st_dev,x.st_ino,x.st_uid,x.st_gid,x.st_mode,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(info) == identity(after), 'MOUNT_ROLE_CHANGED')
    return {'canonical': str(path), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True,
            'mode': oct(stat.S_IMODE(info.st_mode)), 'file_capabilities': False, 'elf64_little_endian_x86_64': True,
            'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,'gid':info.st_gid,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns,
            'admitted_effect': 'ROOT_ONLY_FIXED_TMPFS_AND_CONFIG_BIND_IN_PRIVATE_NAMESPACE'}

def capsule_outside():
    rows = {}
    for name in ('/', '/usr', '/usr/local', '/etc', '/opt', '/usr/local/bin'):
        path = Path(name); info = path.lstat(); mode = stat.S_IMODE(info.st_mode)
        need(path.resolve(strict=True) == path and stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and info.st_gid == 0, 'CAPSULE_OUTSIDE_PHYSICAL_ROOT')
        need(mode in (0o755, 0o777) if name in CAPSULE_TARGETS else not mode & 0o022, 'CAPSULE_OUTSIDE_MODE')
        rows[name] = {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid, 'gid': info.st_gid,
                      'mode': mode, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
    path = Path('/etc/gitconfig'); info = path.lstat()
    need(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
         info.st_uid == 0 and info.st_gid == 0 and not info.st_mode & 0o022 and info.st_size <= 65536, 'CAPSULE_OUTSIDE_CONFIG_SHAPE')
    size, sha = stream_hash(path); after = path.lstat()
    identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(info) == identity(after) and size == info.st_size, 'CAPSULE_OUTSIDE_CONFIG_CHANGED')
    rows['/etc/gitconfig'] = {'kind':'REGULAR','device':info.st_dev,'inode':info.st_ino,
                            'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),
                            'nlink':info.st_nlink,'bytes':size,'sha256':sha,
                            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
    return rows

def capsule_recheck(state, u, phase):
    before = state['capsule_private']['host_before']; after = capsule_host_snapshot(state, u)
    equal = after == before
    state['capsule']['outside_rechecks'][phase] = {'unchanged': equal, 'identity_sha256': digest(encoded(after))}
    need(equal, 'CAPSULE_OUTSIDE_OR_UTILITY_CHANGED')

def prior_component(state, source, phase):
    expected = {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,
                'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],
                'source_closure':{'prepare':False,'receive':False,'final':False}}
    if 'predicates' not in state: state['predicates'] = expected
    row = state['predicates']; closure = row.get('source_closure')
    need(type(row) is dict and set(row) == set(expected) and type(closure) is dict and set(closure) == {'prepare','receive','final'} and
         all(type(x) is bool for x in closure.values()) and {k:v for k,v in row.items() if k!='source_closure'} == {k:v for k,v in expected.items() if k!='source_closure'}, 'PRIOR_COMPONENT_REFERENCE')
    closure[phase] = False
    need(SOURCE == PRIOR_COMPONENT['source_commit'] and TREE == PRIOR_COMPONENT['source_tree'] and
         state.get('source_before', {}).get('commit') == SOURCE and state['source_before'].get('tree') == TREE and
         state['source_before'].get('all_manifest_members_match') is True and
         digest(read(source/PRIOR_COMPONENT['test_path'])) == PRIOR_COMPONENT['test_source_sha256'], 'PRIOR_COMPONENT_SOURCE_CLOSURE')
    closure[phase] = True

def observe_capsule_failure(state, label, exc):
    state['failures'].append({'step':label,'exception_type':type(exc).__name__,
                              'message_sha256':digest(str(exc).encode()),'message_bytes':len(str(exc).encode())})

def packet_check(packet):
    raw = read(packet/'INPUT_PINS.json'); need(digest(raw) == PINS_SHA, 'PACKET_UNSEALED_OR_CHANGED')
    pins = json.loads(raw)
    for name, row in pins.items():
        need(re.fullmatch(r'[A-Za-z0-9_.-]+', name) is not None, 'INPUT_PATH')
        content = read(packet/name)
        need(len(content) == row['bytes'] and digest(content) == row['sha256'], 'INPUT_PIN')
    for family in ('canonical',):content_archive_input(packet,family)
    return pins

def capsule_host_snapshot(state, u):
    tools = {}
    for name in ('bash', 'unshare', 'setpriv', 'python3', 'env', 'timeout'):
        path, observed = u.trusted(name)
        need(path is not None and observed == state['host']['tools'][name], 'CAPSULE_ROOT_UTILITY_DRIFT')
        info = Path(path).lstat()
        tools[name] = {'admission': observed, 'device': info.st_dev, 'inode': info.st_ino,
                       'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
                       'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
    observed = mount_role(); need(observed == state['host']['tools']['mount'], 'CAPSULE_MOUNT_TOOL_DRIFT')
    tools['mount'] = observed
    sudo = Path('/usr/bin/sudo').resolve(strict=True); info = sudo.lstat()
    for node in (sudo, *sudo.parents):
        item = node.lstat(); need(item.st_uid == 0 and not item.st_mode & 0o022, 'CAPSULE_SUDO_ANCESTRY')
    need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o4755 and
         stream_hash(sudo) == (state['host']['tools']['sudo']['bytes'], state['host']['tools']['sudo']['sha256']), 'CAPSULE_SUDO_DRIFT')
    try: cap = os.getxattr(sudo, 'security.capability')
    except OSError as exc:
        need(exc.errno in (errno.ENODATA,errno.ENOTSUP), 'CAPSULE_SUDO_CAPABILITY_UNKNOWN'); cap = b''
    need(not cap, 'CAPSULE_SUDO_FILE_CAPABILITY')
    tools['sudo'] = {'device': info.st_dev, 'inode': info.st_ino, 'mode': stat.S_IMODE(info.st_mode),
                     'uid': info.st_uid, 'gid': info.st_gid, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns,
                     'sha256': state['host']['tools']['sudo']['sha256']}
    namespace = os.readlink('/proc/self/ns/mnt'); need(re.fullmatch(r'mnt:\[[0-9]+\]', namespace), 'PARENT_MOUNT_NAMESPACE')
    network_namespace = os.readlink('/proc/self/ns/net')
    need(re.fullmatch(r'net:\[[0-9]+\]',network_namespace), 'PARENT_NETWORK_NAMESPACE')
    return {'outside': capsule_outside(), 'root_tools': tools, 'parent_mount_namespace': namespace, 'parent_net_namespace':network_namespace}

def capsule_snapshot_valid(value, uid, gid, parent_namespace, parent_net_namespace):
    keys = {'mount_namespace_sha256','namespace_distinct','private_propagation','mountinfo_sha256','mount_count',
            'uids','gids','groups','capabilities','no_new_privileges','mounts','gitconfig_source','source_target_same_file','network'}
    if type(value) is not dict or set(value) != keys: return False
    hexsha = lambda x:type(x) is str and re.fullmatch('[0-9a-f]{64}',x) is not None
    if not all(hexsha(value[k]) for k in ('mount_namespace_sha256','mountinfo_sha256')): return False
    if value['mount_namespace_sha256'] == digest(parent_namespace.encode()) or value['namespace_distinct'] is not True or value['private_propagation'] is not True: return False
    if type(value['mount_count']) is not int or not 4 <= value['mount_count'] <= 4096: return False
    for key,expected in (('uids',uid),('gids',gid)):
        if type(value[key]) is not list or len(value[key]) != 4 or not all(type(x) is int and x == expected for x in value[key]): return False
    if type(value['groups']) is not list or value['groups'] != []: return False
    caps = value['capabilities']
    if type(caps) is not dict or set(caps) != {'CapEff','CapPrm','CapAmb'} or not all(type(x) is int and x == 0 for x in caps.values()): return False
    if type(value['no_new_privileges']) is not int or value['no_new_privileges'] != 1: return False
    common = {'path','mount_id','parent_mount_id','mount_root','filesystem','mount_source','readonly','nodev','nosuid','noexec','size_bytes','mount_options_sha256','super_options_sha256'}
    directory = {'directory_uid','directory_gid','mode','directory','symlink','entries','device','inode'}
    filekeys = {'file_uid','file_gid','mode','regular','symlink','nlink','bytes','sha256','device','inode'}
    def file_ok(row):
        if row['regular'] is not True or row['symlink'] is not False or row['sha256'] != 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': return False
        if not all(type(row[k]) is int and row[k] == n for k,n in (('file_uid',0),('file_gid',0),('mode',0o644),('nlink',1),('bytes',0))): return False
        return all(type(row[k]) is int and row[k] > 0 for k in ('device','inode'))
    rows = value['mounts']
    if type(rows) is not list or len(rows) != 3: return False
    for path,row in zip(CAPSULE_TARGETS,rows):
        expected_keys = common | (filekeys if path == '/etc/gitconfig' else directory)
        if type(row) is not dict or set(row) != expected_keys or row['path'] != path: return False
        root = '/dg17-empty-system-gitconfig' if path == '/etc/gitconfig' else '/'
        if row['filesystem'] != 'tmpfs' or row['mount_source'] != 'tmpfs' or row['mount_root'] != root: return False
        if not all(type(row[k]) is int and row[k] > 0 for k in ('mount_id','parent_mount_id')) or row['mount_id'] == row['parent_mount_id']: return False
        if not all(row[k] is True for k in ('readonly','nodev','nosuid','noexec')) or type(row['size_bytes']) is not int or row['size_bytes'] != 4096: return False
        if not all(hexsha(row[k]) for k in ('mount_options_sha256','super_options_sha256')): return False
        if path == '/etc/gitconfig':
            if not file_ok(row): return False
        else:
            if row['directory'] is not True or row['symlink'] is not False: return False
            for key,expected in (('directory_uid',0),('directory_gid',0),('mode',0o755),('entries',1 if path == '/opt' else 0)):
                if type(row[key]) is not int or row[key] != expected: return False
            if not all(type(row[k]) is int and row[k] > 0 for k in ('device','inode')): return False
    if len({row['mount_id'] for row in rows}) != 3: return False
    source = value['gitconfig_source']
    if type(source) is not dict or set(source) != filekeys | {'path'} or source['path'] != '/opt/dg17-empty-system-gitconfig' or not file_ok(source): return False
    if value['source_target_same_file'] is not True or source['device'] != rows[0]['device'] or any(source[k] != rows[2][k] for k in filekeys): return False
    if rows[0]['super_options_sha256'] != rows[2]['super_options_sha256']: return False
    return body_network_snapshot_valid(value['network'],parent_net_namespace)

def receive_capsule(state, output):
    before_raw = read(output/'private/CAPSULE_ADMISSION.json', 16384)
    before = json.loads(before_raw, object_pairs_hook=unique_object)
    expected = state['capsule_private']['child_argv_sha256']; parent = state['capsule_private']['host_before']['parent_mount_namespace']; network_parent = state['capsule_private']['host_before']['parent_net_namespace']
    need(type(before) is dict and set(before) == {'schema','child_argv_sha256','snapshot'} and
         before['schema'] == 'dg17.private-view-admission.v3' and before['child_argv_sha256'] == expected and
         capsule_snapshot_valid(before['snapshot'], os.getuid(), os.getgid(), parent, network_parent), 'CAPSULE_BEFORE_PROOF')
    first_sha = digest(before_raw); previous = state['capsule'].get('admission_sha256')
    need(previous is None or previous == first_sha, 'CAPSULE_BEFORE_PROOF_CHANGED')
    state['capsule'].update(admission_sha256=first_sha, before=before['snapshot'], admitted_before=True)
    raw = read(output/'private/CAPSULE_RESULT.json', 16384); value = json.loads(raw, object_pairs_hook=unique_object)
    keys = {'schema','before_sha256','child_argv_sha256','before','after','child_returncode','failure'}
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg17.private-view-result.v3' and
         value['before_sha256'] == first_sha and value['child_argv_sha256'] == expected and value['before'] == before['snapshot'],
         'CAPSULE_RESULT_BINDING')
    after_ok = capsule_snapshot_valid(value['after'], os.getuid(), os.getgid(), parent, network_parent)
    rc = value['child_returncode']
    need(type(rc) is int and -128 <= rc <= 255 and value['failure'] in (None,'CHILD_START_OR_WAIT_REFUSED','AFTER_VIEW_REFUSED'), 'CAPSULE_RESULT_VALUE')
    result_sha = digest(raw); previous = state['capsule'].get('result_sha256')
    need(previous is None or previous == result_sha, 'CAPSULE_RESULT_CHANGED')
    state['capsule'].update(result_sha256=result_sha, child_returncode=rc,
                            after=value['after'] if after_ok else None,
                            before_after_equal=after_ok and value['before'] == value['after'])
    need(after_ok and value['before'] == value['after'] and rc == 0 and value['failure'] is None, 'CAPSULE_AFTER_OR_CHILD_REFUSED')
    state['capsule']['status'] = 'OBSERVED_PRIVATE_VIEW_BEFORE_AFTER'

def currentness_admission(state, source, output, u, label):
    """Data-only re-entry gate. Failure containment is distinct from cleanup."""
    expected_steps = {'initial-currentness':'require','before-runtime-acquisition':'runtime',
                      'after-runtime-acquisition':'runtime','before-content':'content',
                      'after-content':'content','before-receiving':'receive',
                      'after-receiving':'receive','final-currentness':None}
    need(label in expected_steps and state.get('failed') is False and state.get('failures') == [] and
         state.get('active_command') is None and state.get('active_step') == expected_steps[label],
         'CURRENTNESS_UNSOUND_PRIOR_STATE')
    need(type(state.get('commands')) is list and len(state['commands']) > 0 and all(type(row) is dict and
         row.get('process_started') is True and type(row.get('returncode')) is int and row['returncode'] == 0 and
         row.get('timeout') is False and row.get('output_bound_exceeded') is False and
         row.get('pidfd_acquired') is True and row.get('internal_failure') is None and
         row.get('streams_complete') is True and row.get('cleanup',{}).get('echild') is True
         for row in state['commands']), 'CURRENTNESS_PRIOR_CAPTURE_UNSOUND')
    late = label in ('after-content','before-receiving','after-receiving','final-currentness')
    if label == 'final-currentness':
        need(state.get('completed') == list(STEPS) and state.get('bounded_receiving_complete') is True,
             'FINAL_CURRENTNESS_INCOMPLETE_RECEIVING')
    packet = Path(__file__).absolute().parent
    if late:
        need(any(row.get('name') == 'loopback-codex-canonical-routing' for row in state['commands']),
             'CURRENTNESS_NATIVE_CAPTURE_MISSING')
        need(state.get('content_validation',{}).get('valid') is True and
             state['content_validation'].get('captured_result_matches') is True and
             content_success(state.get('content',{}),os.getuid(),os.getgid(),state['receipt']),
             'CURRENTNESS_CHILD_ROUTE_UNSOUND')
        raw = read(output/'private/ROUTING_RESULT.json',32768)
        need(digest(raw) == state['content_validation']['result_sha256'] and
             json.loads(raw,object_pairs_hook=unique_object) == state['content'], 'CURRENTNESS_CHILD_RESULT_CHANGED')
        receive_content_private(state,output,source)
    route_inputs_recheck(state,output,packet,'currentness-'+label)
    content_system_recheck(state,output,u,'currentness-'+label)
    for family in ('canonical',):content_archive_input(packet,family)
    observed = source_check(source,packet)
    need(observed == state.get('source_before') and
         canonical_hashes(source,state) == state.get('canonical_before'), 'CURRENTNESS_SOURCE_OR_STATE_DRIFT')
    store = currentness_store_snapshot(source,packet)
    if label == 'initial-currentness':
        need('currentness_store_before' not in state and state.get('currentness') == [] and
             state.get('completed') == list(STEPS[:STEPS.index('require')]), 'CURRENTNESS_STORE_BASELINE_SEQUENCE')
        state['currentness_store_before'] = store
    else:
        need(store == state.get('currentness_store_before'), 'CURRENTNESS_STORE_DRIFT')
    if late:
        received_git = json.loads(read(output/'private/canonical-routing/GIT_BEFORE.json',262144),
                                  object_pairs_hook=unique_object)
        need(store['guard'] == received_git.get('source_store'), 'CURRENTNESS_RECEIVED_STORE_DRIFT')
    for name in ('bash','env','git','python3'):
        path,observed_tool = u.trusted(name)
        need(path is not None and observed_tool == state['host']['tools'][name], 'CURRENTNESS_TOOL_CHANGED')
    if 'runtime' in state:
        binary = output/'private/codex-input'; info = binary.lstat()
        need(binary.resolve(strict=True) == binary and stat.S_ISREG(info.st_mode) and
             info.st_uid == os.getuid() and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o700 and
             stream_hash(binary) == (BINARY_BYTES,BINARY_SHA), 'CURRENTNESS_RUNTIME_CHANGED')
    need(u.children() == [], 'CURRENTNESS_OWNED_CHILDREN_REMAIN')
    try:
        os.waitpid(-1,os.WNOHANG|0x40000000)
    except ChildProcessError:
        return {'source_before_execution':True,'canonical_before_execution':True,
                'tools_before_execution':True,'runtime_before_execution':'runtime' in state,
                'child_private_binding_before_execution':late,'global_echild_before_execution':True,
                'git_store_before_execution':True,'git_store_baseline_matches':True,
                'git_store_entries':store['entries'],'git_store_bytes':store['bytes'],
                'git_store_population_sha256':store['population_sha256']}
    raise Refusal('CURRENTNESS_GLOBAL_ECHILD_UNCONFIRMED')

def launch_content(state, source, output, packet, u):
    need(digest(CAPSULE_SCRIPT.encode()) == CAPSULE_SCRIPT_SHA and digest(CAPSULE_CODE.encode()) == CAPSULE_CODE_SHA, 'CAPSULE_LITERAL_PIN')
    route_inputs_recheck(state,output,packet,'before-native')
    content_system_recheck(state,output,u,'before-content')
    host = capsule_host_snapshot(state, u)
    netns = host['parent_net_namespace']
    probe_args = ['--source',str(source),'--episode',str(output),'--binary',str(output/'private/codex-input'),
                  '--controller',state['controller'],'--receipt',state['receipt'],'--expected-uid',str(os.getuid()),
                  '--expected-gid',str(os.getgid()),'--parent-netns',netns,
                  '--canonical-archive',str(content_archive_input(packet,'canonical')),
                  '--review-packet-root',str(output/'routing-review-inputs'),'--owner-envelope',str(output/'private/routing-owner-binding.json'),
                  '--owner-envelope-sha256',ROUTE_OWNER_SHA]
    child_argv = ['/usr/bin/python3','-I','-S','-B',str(packet/'routing_probe.py'),*probe_args]
    state['capsule_private'] = {'host_before':host,'child_argv_sha256':digest(encoded(child_argv))}
    state['capsule'] = {'profile':'PRIVATE_READONLY_VIEW_AND_LOOPBACK_ONLY_V3','status':'PREPARED_NOT_OBSERVED',
                        'qualification_scope':'CONSTRUCTED_PRIVATE_VIEW_NOT_STOCK_INSTALLATION_PATH_QUALIFICATION',
                        'targets':list(CAPSULE_TARGETS),'root_watchdog_seconds':285,'root_kill_after_seconds':5,
                        'root_script_sha256':CAPSULE_SCRIPT_SHA,'inline_code_sha256':CAPSULE_CODE_SHA,
                        'loopback_initializer_sha256':LOOPBACK_INITIALIZER_SHA,
                        'outside_before_sha256':digest(encoded(host)),'outside_rechecks':{},
                        'outside_system_gitconfig':host['outside']['/etc/gitconfig'],
                        'admitted_before':False,'before_after_equal':False,'admission_sha256':None,
                        'result_sha256':None,'before':None,'after':None,'child_returncode':None}
    save(output/'private/episode.json', state)
    argv = ['/usr/bin/sudo','-n','/usr/bin/timeout','--signal=TERM','--kill-after=5s','285s',
            '/usr/bin/unshare','--mount','--net','--propagation','private','--',
            '/usr/bin/bash','--noprofile','--norc','-c',CAPSULE_SCRIPT,'dg17-private-view',
            str(os.getuid()),str(os.getgid()),CAPSULE_CODE,
            str(output/'private/CAPSULE_ADMISSION.json'),str(output/'private/CAPSULE_RESULT.json'),
            host['parent_mount_namespace'],netns,str(packet/'routing_probe.py'),*probe_args]
    failure = None
    try: command(state, output, u, 'loopback-codex-canonical-routing', argv, seconds=300)
    except BaseException as exc: failure = exc
    for label, action in (('system-helpers-after',lambda:content_system_recheck(state,output,u,'after-content')),
                          ('capsule-outside-after',lambda:capsule_recheck(state,u,'after-command')),
                          ('capsule-proof-after',lambda:receive_capsule(state,output))):
        try: action()
        except BaseException as exc:
            observe_capsule_failure(state,label,exc)
            if failure is None: failure = exc
    try:
        if (output/'private/ROUTING_RESULT.json').exists():
            receive_content(state, packet, read(output/'private/ROUTING_RESULT.json', 32768))
            record = state['commands'][-1]
            state['content_validation']['captured_result_matches'] = False
            if record.get('name') == 'loopback-codex-canonical-routing' and record.get('streams_complete') is True:
                captured_raw = read(output/'private'/f'{len(state["commands"]):03d}-loopback-codex-canonical-routing.stdout',32768)
                need(captured_raw == read(output/'private/ROUTING_RESULT.json',32768), 'CONTENT_CAPTURE_DIFFERS')
                captured = json.loads(captured_raw, object_pairs_hook=unique_object)
                need(catalogue_schema_matches(captured, json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'), object_pairs_hook=unique_object)) and captured == state['content'], 'CONTENT_CAPTURE_DIFFERS')
                state['content_validation']['captured_result_matches'] = True
                state['content_validation']['child_success_claimed'] = content_success(state['content'],os.getuid(),os.getgid(),state['receipt'])
    except BaseException as exc:
        observe_capsule_failure(state,'content-receiving',exc)
        if failure is None: failure = exc
    if failure is not None: raise failure

def observe_owned_leaf(path, expected_parent=None):
    """None means exact leaf ENOENT; a stat record means present; errors refuse.

    Bind every physical ancestor and the owned, non-group/world-writable parent
    before and after a no-follow lookup relative to that parent's descriptor.
    The selected workspace/Git parent need not have private-home mode. These
    observations do not make a later path-based subprocess race-free.
    """
    path = Path(path)
    need(path.is_absolute() and ".." not in path.parts and path.name not in {"", ".", ".."},
         "OWNED_LEAF_PATH_UNADMITTED")
    parent = path.parent

    def identity(info):
        return {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
                "gid": info.st_gid, "mode": info.st_mode}

    def ancestry():
        rows = {}
        for item in (*reversed(parent.parents), parent):
            info = os.stat(item, follow_symlinks=False)
            need(stat.S_ISDIR(info.st_mode), "OWNED_LEAF_ANCESTOR_NOT_PHYSICAL")
            rows[str(item)] = identity(info)
        current = rows[str(parent)]
        need(current["uid"] == os.geteuid() and current["gid"] == os.getegid() and
             not current["mode"] & 0o022, "OWNED_LEAF_PARENT_UNADMITTED")
        return rows

    fd = None
    try:
        before = ancestry()
        parent_row = before[str(parent)]
        if expected_parent is not None:
            need(parent_row == expected_parent, "OWNED_LEAF_ADMITTED_PARENT_CHANGED")
        fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        need(identity(os.fstat(fd)) == parent_row and ancestry() == before,
             "OWNED_LEAF_PARENT_CHANGED_BEFORE_LOOKUP")
        try:
            observed = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
            observed = None
        need(identity(os.fstat(fd)) == parent_row and ancestry() == before,
             "OWNED_LEAF_PARENT_CHANGED_AFTER_LOOKUP")
        return observed
    except OSError as exc:
        raise Refusal("OWNED_LEAF_OBSERVATION_UNREADABLE") from exc
    finally:
        if fd is not None:
            os.close(fd)


def source_freshness_guard(source):
    need(observe_owned_leaf(source) is None, 'SOURCE_NOT_FRESH')


def execute(step, state, source, output, packet, u):
    if step == 'prepare':
        need(os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid() > 0, 'ORDINARY_RUNNER_IDENTITY')
        source_freshness_guard(source)
        for label, args in [('git-init', ['init', '--quiet', '--initial-branch=dg17-bootstrap', str(source)]), ('git-remote', ['-C', str(source), 'remote', 'add', 'origin', 'https://github.com/'+REPO+'.git']), ('git-fetch', ['-c', 'protocol.https.allow=always', '-C', str(source), 'fetch', '--quiet', '--depth=2', '--no-tags', 'origin', SOURCE]), ('git-checkout', ['-C', str(source), 'checkout', '--quiet', '--detach', SOURCE])]:
            command(state, output, u, label, ['/usr/bin/git', *args], seconds=180)
        os.chdir(source)
        head = command(state, output, u, 'head-identity', ['/usr/bin/git', 'rev-parse', 'HEAD', 'HEAD^{tree}'])
        need(head.decode().splitlines() == [SOURCE, TREE], 'HEAD_TREE')
        body = command(state, output, u, 'head-parent', ['/usr/bin/git', 'cat-file', '-p', 'HEAD'])
        need(body.split(b'\n\n', 1)[0].splitlines()[:2] == [('tree '+TREE).encode(), ('parent '+PARENT).encode()], 'PARENT')
        need(command(state, output, u, 'fresh-controller-refs', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)', 'refs/implementaudit']) == b'', 'IMPORTED_CONTROLLER_REFS')
        need(not command(state, output, u, 'fresh-source-clean', ['/usr/bin/git', 'status', '--porcelain=v1', '--untracked-files=all']), 'SOURCE_DIRTY')
        tools = {}
        for name in ('python3', 'git', 'bash', 'env', 'unshare', 'setpriv', 'timeout'):
            path, observed = u.trusted(name); need(path is not None, 'HOST_TOOL_'+name); tools[name] = observed
        tools['mount'] = mount_role()
        sudo = Path('/usr/bin/sudo').resolve(strict=True)
        for path in (sudo, *sudo.parents):
            info = path.lstat(); need(info.st_uid == 0 and not info.st_mode & 0o022, 'SUDO_ANCESTRY')
        need(stat.S_IMODE(sudo.stat().st_mode) == 0o4755, 'SUDO_EXPECTED_SETUID_MODE')
        size, sha = stream_hash(sudo)
        tools['sudo'] = {'canonical': str(sudo), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True, 'mode': '04755', 'admitted_effect': 'ROOT_WATCHDOG_PRIVATE_MOUNT_AND_NETWORK_NAMESPACES_FIXED_TMPFS_AND_EMPTY_READONLY_GITCONFIG_BIND_THEN_DROP_UID_GID_NO_NEW_PRIVILEGES'}
        state['host'] = {'platform': platform.system(), 'kernel': platform.release(), 'python': list(sys.version_info[:3]), 'uid': os.getuid(), 'gid': os.getgid(), 'tools': tools, 'upstream_provider_calls':0,'planned_loopback_requests':8,'planned_appserver_processes':1,'planned_native_version_commands':1,'planned_requested_exec_commands':3,'planned_collaboration_commands':3,'planned_rpc_count':7,'native_internal_helper_count':'UNESTABLISHED'}
        helper_snapshot=content_system_helpers(u, state)
        state['content_helpers_private']={'before':helper_snapshot}
        state['content_helpers']={'profile':'PHYSICAL_SYSTEM_HELPERS_ONLY_V1','before_sha256':digest(encoded(helper_snapshot)),
                                  'helper_count':6,'capability_probe_executed':False,'rechecks':{}}
        for family in ('canonical',):content_archive_population(packet,family)
        state['source_before'] = source_check(source, packet)
        prior_component(state, source, 'prepare')
        route_stage_inputs(state,output,packet)
    elif step == 'initialize':
        raw = owner(state, source, output, u, 'fresh-claim', '--controller', state['controller'], 'dg17-isolated-native')
        run = raw.decode('ascii').strip(); need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/dg17-isolated-native-[A-Za-z0-9]{6}', run), 'RUN_ROOT')
        state['run_root'] = run; save(output/'private/episode.json', state)
        authored = json.loads(command(state, output, u, 'author-task', ['/usr/bin/python3', '-I', '-S', '-B', str(source/AUTHOR), '--repo', str(source), '--run-root', run, '--source', str(source), '--purpose', PURPOSE, '--next-action', NEXT]))
        need(set(authored) == set(DOCS) and authored == canonical_hashes(source, state), 'AUTHOR_READBACK')
        inspected = json.loads(owner(state, source, output, u, 'inspect-initialization', '--inspect-controller-initialization', state['controller'], '--run-root', run))
        init = inspected['initialization_token']; need(re.fullmatch('refs/implementaudit/controller-initializations/'+state['controller']+r'/[0-9a-f]{32}@[0-9a-f]{40}', init), 'PREPARATION_TOKEN')
        activated = json.loads(owner(state, source, output, u, 'activate-initialization', '--activate-controller', state['controller'], '--run-root', run, '--expected-initialization', init))
        need(activated.get('status') == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and activated.get('authority_ceiling') == 'ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY', 'ACTIVATION')
        state['canonical_before'] = canonical_hashes(source, state)
    elif step == 'discover':
        parts = owner(state, source, output, u, 'discover', '--current-controller', state['controller']).decode().strip().split('\t')
        need(len(parts) == 4 and parts[0] == state['controller'] and Path(parts[1]) == source and Path(parts[2]) == source/state['run_root'], 'DISCOVERY')
    elif step == 'invalidate':
        owner(state, source, output, u, 'invalidate', '--invalidate-continuity', state['controller'], '--boundary', 'new-session', '--event', 'dg17-hosted-'+state['context']['run_id']+'-attempt-1')
    elif step in ('read-state', 'read-roadmap'):
        name = 'STATE.md' if step == 'read-state' else 'ROADMAP.md'; raw = read(source/state['run_root']/name)
        with (output/'private'/(step+'.read')).open('xb') as f: f.write(raw)
        state['reads'][name] = {'sha256': digest(raw), 'completed_host_action_ordinal': len(state['completed'])+1}
    elif step == 'resume':
        need(set(state['reads']) == {'STATE.md', 'ROADMAP.md'} and state['reads']['STATE.md']['completed_host_action_ordinal'] < state['reads']['ROADMAP.md']['completed_host_action_ordinal'], 'SEPARATE_READS')
        for name, row in state['reads'].items(): need(digest(read(source/state['run_root']/name)) == row['sha256'], 'READ_CHANGED')
        raw = owner(state, source, output, u, 'resume', '--resume-controller', state['controller'], '--boundary', 'new-session', '--epoch', 'G0001')
        receipt = raw.decode().strip(); need(re.fullmatch('refs/implementaudit/continuity-receipts/'+state['controller']+r'/G0001@[0-9a-f]{40}', receipt), 'RECEIPT')
        state['receipt'] = receipt
    elif step == 'verify':
        need(owner(state, source, output, u, 'verify', '--verify-resume-receipt', state['receipt']) == (state['receipt']+'\n').encode(), 'VERIFY')
    elif step == 'require': current(state, source, output, u, 'initial-currentness')
    elif step == 'runtime':
        current(state, source, output, u, 'before-runtime-acquisition'); state['runtime'] = acquire_runtime(output)
        version = command(state, output, u, 'codex-version', [str(output/'private/codex-input'), '--version']).decode().strip()
        need(version == 'codex-cli 0.167.0-alpha.4', 'CODEX_VERSION'); state['runtime']['observed_version'] = version
        current(state, source, output, u, 'after-runtime-acquisition')
    elif step == 'content':
        current(state, source, output, u, 'before-content')
        launch_content(state, source, output, packet, u)
        current(state, source, output, u, 'after-content')
    elif step == 'receive':
        current(state, source, output, u, 'before-receiving')
        prior_component(state, source, 'receive')
        receive_capsule(state, output)
        capsule_recheck(state, u, 'receive')
        need(state.get('content_validation', {}).get('valid') is True and state['content_validation'].get('captured_result_matches') is True and content_success(state.get('content', {}),os.getuid(),os.getgid(),state['receipt']), 'CONTENT_NOT_RECEIVED')
        need(stream_hash(output/'private/codex-input') == (BINARY_BYTES,BINARY_SHA), 'RECEIVED_RUNTIME_CHANGED')
        receive_content_private(state,output,source)
        state['content_validation']['semantic_receiving_passed'] = True
        state['source_after'] = source_check(source, packet)
        need(state['source_after'] == state['source_before'] and canonical_hashes(source, state) == state['canonical_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
        current(state, source, output, u, 'after-receiving')
        state['bounded_receiving_complete'] = True
    else: raise Refusal('UNKNOWN_STEP')

def export(state, output, packet):
    if 'content' in state:
        try:
            need(catalogue_schema_matches(state['content'], json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))), 'CONTENT_EXPORT_SCHEMA')
        except BaseException as exc:
            state.pop('content', None); state.setdefault('content_validation',{})['valid'] = False; state['failed'] = True; state['bounded_receiving_complete'] = False
            state['failures'].append({'step': 'export', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
    docs = {
        'RESULT.json': {'schema': 'dg17.isolated-codex-canonical-routing-hosted-result.v1', 'context': state['context'], 'completed': state['completed'], 'failed': state['failed'], 'bounded_receiving_complete': state.get('bounded_receiving_complete', False), 'routing_validation': state.get('content_validation'), 'routing_selection': state.get('routing_selection'), 'local_currentness_transfer': False, 'original_acceptance': False, 'whole_T12': False, 'whole_T14': False, 'new_original_awards': []},
        'SOURCE.json': {'before': state.get('source_before'), 'after': state.get('source_after'), 'canonical_unchanged': state.get('canonical_unchanged')},
        'HOST.json': {'host': state.get('host'), 'runtime': state.get('runtime'), 'capsule':state.get('capsule'),'system_helpers':state.get('content_helpers'),'system_helper_refusal':state.get('content_helper_refusal')},
        'CURRENTNESS.json': {'checks': state['currentness'], 'reads': state['reads'], 'local_or_future_transfer': False},
        'PREDICATES.json': state.get('predicates', {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],'source_closure':{'prepare':False,'receive':False,'final':False}}),
        'ROUTING.json': state.get('content', {'status': 'INVALID_RESULT_SCHEMA' if state.get('content_validation',{}).get('valid') is False else 'NOT_COMPLETED'}),
        'CLEANUP.json': {'commands': state['commands'], 'active_step': state.get('active_step'), 'active_command': state.get('active_command'), 'all_recorded_commands_reaped': all(x.get('cleanup', {}).get('echild') is True for x in state['commands']), 'private_roots_retained_until_disposable_host_teardown': True, 'declared_large_payload_owners_retained_until_disposable_host_teardown': True},
        'FAILURE.json': {'failures': state['failures']}}
    files = {name: encoded(value) for name, value in docs.items()}; need(all(len(raw) <= 65536 for raw in files.values()) and sum(map(len, files.values())) <= 262144, 'PUBLIC_BOUND')
    files['ARTIFACT_MANIFEST.json'] = encoded({'schema': 'dg17.public-artifact-manifest.v1', 'members': [{'name': name, 'bytes': len(raw), 'sha256': digest(raw)} for name, raw in sorted(files.items())]})
    public = output/'public'; public.mkdir(exist_ok=True)
    for name, raw in files.items():
        with (public/name).open('xb') as f: f.write(raw)
    print(json.dumps({'status': 'FAILED_RETAINED' if state['failed'] else 'BOUNDED_OBSERVATIONS_RETAINED', 'completed_steps': len(state['completed']), 'original_acceptance': False}))

def main():
    p = argparse.ArgumentParser(); p.add_argument('--step', choices=(*STEPS, 'finalize'), required=True); p.add_argument('--output', required=True); p.add_argument('--source', required=True); a = p.parse_args()
    packet = Path(__file__).absolute().parent; output = Path(a.output).absolute(); source = Path(a.source).absolute(); env = os.environ
    need(env.get('GITHUB_ACTIONS') == 'true' and env.get('RUNNER_ENVIRONMENT') == 'github-hosted' and env.get('GITHUB_REPOSITORY') == REPO and env.get('GITHUB_REF') == 'refs/heads/'+BRANCH and env.get('GITHUB_EVENT_NAME') == 'push' and env.get('GITHUB_RUN_ATTEMPT') == '1', 'ACTUAL_HOSTED_EVENT_REQUIRED')
    run_id = env['GITHUB_RUN_ID']; need(re.fullmatch(r'[0-9]{1,20}', run_id), 'RUN_ID')
    need(re.fullmatch(r'[0-9a-f]{40}', env.get('GITHUB_SHA', '')), 'WORKFLOW_COMMIT')
    need(output == Path(env['RUNNER_TEMP'])/('dg17-episode-'+run_id+'-1') and source == Path(env['GITHUB_WORKSPACE'])/'dg17-qualified-source', 'OWNED_PATHS')
    packet_check(packet); u = utility(packet)
    lib = ctypes.CDLL(None, use_errno=True); need(lib.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER')
    if a.step == 'prepare':
        output.mkdir(mode=0o700)
        for name in ('private', 'home', 'tmp'): (output/name).mkdir(mode=0o700)
        state = {'context': {'repository': REPO, 'branch': BRANCH, 'run_id': run_id, 'attempt': 1, 'workflow_commit': env['GITHUB_SHA']}, 'controller': 'dg17-hosted-'+run_id+'-a1', 'run_root': None, 'receipt': None, 'completed': [], 'commands': [], 'currentness': [], 'reads': {}, 'failed': False, 'failures': [], 'active_step': None, 'active_command': None}
    else:
        state = json.loads(read(output/'private/episode.json'))
        need(state['context']['run_id'] == run_id and state['context']['workflow_commit'] == env['GITHUB_SHA'], 'EPISODE_IDENTITY')
    # Preparation admits absence immediately before Git init; this cwd branch
    # supplies no freshness proof. Later steps retain an explicit optional cwd.
    if a.step != 'prepare':
        source_info = observe_owned_leaf(source)
        if source_info is not None:
            need(stat.S_ISDIR(source_info.st_mode) and source_info.st_uid == os.geteuid() and
                 not source_info.st_mode & 0o022, 'SOURCE_CWD_UNADMITTED')
            os.chdir(source)
    if a.step == 'finalize':
        if 'capsule_private' in state:
            try:
                content_system_recheck(state,output,u,'final')
                capsule_recheck(state, u, 'final')
                receive_capsule(state, output)
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False
                observe_capsule_failure(state, 'capsule-final', exc)
        if state.get('active_step') is not None or state.get('active_command') is not None or state['completed'] != list(STEPS) or not state.get('receipt') or not all(row.get('cleanup', {}).get('echild') is True for row in state['commands']) or state.get('bounded_receiving_complete') is not True:
            state['failed'] = True
            state['bounded_receiving_complete'] = False
            code = 'UNCERTAIN_PREDECESSOR' if state.get('active_step') is not None or state.get('active_command') is not None else 'INCOMPLETE_EPISODE'
            state['failures'].append({'step': 'finalize', 'exception_type': 'Refusal', 'message_sha256': digest(code.encode()), 'message_bytes': len(code)})
        if state.get('failed') is False and state.get('failures') == [] and state.get('bounded_receiving_complete') is True and state.get('completed') == list(STEPS) and state.get('receipt') and state.get('active_step') is None and state.get('active_command') is None and all(x.get('cleanup', {}).get('echild') is True for x in state['commands']):
            try:
                state['canonical_unchanged'] = canonical_hashes(source, state) == state['canonical_before']
                state['source_after'] = source_check(source, packet)
                need(state['canonical_unchanged'] and state['source_after'] == state['source_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
                prior_component(state, source, 'final')
                if state.get('bounded_receiving_complete') is True:
                    need(digest(read(output/'private/ROUTING_RESULT.json',32768)) == state['content_validation']['result_sha256'] and content_success(state['content'],os.getuid(),os.getgid(),state['receipt']), 'FINAL_CONTENT_RESULT_DRIFT')
                    receive_content_private(state,output,source)
                    state['content_validation']['final_private_seal_verified'] = True
                current(state, source, output, u, 'final-currentness')
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False; state['failures'].append({'step': 'finalize', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        export(state, output, packet); save(output/'private/episode.json', state); return 1 if state['failed'] else 0
    need(not state['failed'] and state['active_step'] is None and state['active_command'] is None and state['completed'] == list(STEPS[:STEPS.index(a.step)]), 'STEP_SEQUENCE_OR_UNCERTAIN_PREDECESSOR')
    state['active_step'] = a.step; save(output/'private/episode.json', state)
    try:
        execute(a.step, state, source, output, packet, u)
        state['completed'].append(a.step); state['active_step'] = None
    except BaseException as exc:
        state['failed'] = True
        state['failures'].append({'step': a.step, 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        if state['active_command'] is None: state['active_step'] = None
    finally: save(output/'private/episode.json', state)
    print(json.dumps({'step': a.step, 'complete': a.step in state['completed'], 'failed': state['failed']}))
    return 1 if state['failed'] else 0

if __name__ == '__main__':
    sys.exit(main())
