#!/usr/bin/env python3
"""DG17-only hosted episode. No local execution route or original awards.

Maintained claim/activation/continuity owners supply all custody authority.
Command capture and child containment reuse the unchanged reviewed host utility.
"""
import argparse, ctypes, errno, hashlib, io, json, math, os, platform, re, stat, sys, tarfile, time, types, urllib.request, zipfile
from pathlib import Path

REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg17-isolated-episode-01-20261106'
SOURCE = '0d57929be5bd15682b4e9da2c0209d5dff307843'
TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'
MANIFEST_SHA = 'ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
PINS_SHA = 'a7a429a7c7728de89c2466dce8eff092689ff4adf4bc086809619eb22fbb495c'
CLAIM = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
DOCS = ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')
STEPS = ('prepare', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'runtime', 'claude', 'receive')
PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'CLAUDE_BODY.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
PURPOSE = 'Observe one separately admitted canonical8ee Claude native governor-body delivery and its advertised package entries, under the frozen0d controller, exact package/runtime pins, isolated loopback-only private filesystem view, owned provider/capture custody and independent receiving. Preserve prior component references without replay or original acceptance.'
NEXT = 'Receive the exact canonical archive and runtime as data, admit the fixed private loopback namespace, run one native session against the nonforwarding scripted Messages responder, and independently verify request-body delivery, native events, package/source/store/runtime/currentness and complete cleanup.'
ARCHIVE_URL = 'https://github.com/anthropics/claude-code/releases/download/v2.1.318/claude-linux-x64.tar.gz'
ARCHIVE_SHA = 'e6d426ca0c123f61fad58a361da0329f2a93cd206bc87040ed8d9576dd9eb583'
ARCHIVE_BYTES = 155477886
BINARY_SHA = '708c77b204db30086ff6f1ed34577bda03e1be74ced80557cbf7b54249ebf0bd'
BINARY_BYTES = 337814032
BODY_SOURCE = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
BODY_TREE = '0da374609f7fea2463a2926f3603b976620bd10e'
BODY_ARCHIVE_BYTES = 584974
BODY_ARCHIVE_SHA = '18bb9d7dcb876f7c6be4340bec10dbc77f091227c24504dcecdb0b7d9853f458'
BODY_MATRIX_SHA = 'ef9cbbe7c2c277c434139080d548f0cb868ee091fe79aa96633dcd46cc86a117'
BODY_GOVERNOR_SHA = '4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5'
BODY_RENDERED_SHA = '5304232e5361d608d3754efca1c15ab73bf300c5bd8f9f70e0785ba7431c0e47'
BODY_ACK = 'DG17_LOCAL_CANONICAL_BODY_DELIVERY_ACK'
BODY_EXPECTED_NAMES = ('implementaudit:implementaudit', 'implementaudit:audit-state', 'implementaudit:audit-assess', 'implementaudit:audit-implement', 'implementaudit:audit-andon')
PREDICATE_SCOPE = {
    'direct_source_applicability': ['T06', 'T08', 'Y04', 'BINDING_POSITIVE'],
    'component_only': ['T12'],
    'indirect_inherited_scope_only': ['NESTED/P01'],
    'narrow_receiving_input_only': ['T14'],
    'ceiling': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD',
}

LOOPBACK_INITIALIZER_SHA = 'e04d2c081998a08de53cf0f214cd1b9ae531fc5abc1d1bf79206b43c69570433'
CAPSULE_TARGETS = ('/opt', '/usr/local/bin', '/etc/gitconfig')
CAPSULE_SCRIPT = 'set -eu\nset -o noclobber\numask 022\n[ "$EUID" -eq 0 ]\n[ "$#" -eq 28 ]\n[ -d /opt ] && [ ! -L /opt ]\n[ -d /usr/local/bin ] && [ ! -L /usr/local/bin ]\n[ -f /etc/gitconfig ] && [ ! -L /etc/gitconfig ]\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o rw,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n: > /opt/dg17-empty-system-gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o remount,ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n/usr/bin/mount --internal-only --no-mtab -o bind,ro,nodev,nosuid,noexec /opt/dg17-empty-system-gitconfig /etc/gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /usr/local/bin\n/usr/bin/python3 -I -S -B -c \'"""Fixed root-only namespace initializer, embedded literally; never run locally."""\nimport fcntl\nimport os\nimport re\nimport socket\nimport struct\nimport sys\n\ndef need(ok):\n    if not ok:\n        raise RuntimeError(\'"\'"\'LOOPBACK_ADMISSION_REFUSED\'"\'"\')\n\ndef run():\n    need(len(sys.argv) == 2 and os.geteuid() == 0)\n    parent = sys.argv[1]\n    need(re.fullmatch(r\'"\'"\'net:\\[[0-9]+\\]\'"\'"\', parent) is not None)\n    namespace = os.readlink(\'"\'"\'/proc/self/ns/net\'"\'"\')\n    need(re.fullmatch(r\'"\'"\'net:\\[[0-9]+\\]\'"\'"\', namespace) is not None and namespace != parent)\n    with open(\'"\'"\'/proc/net/dev\'"\'"\', \'"\'"\'rb\'"\'"\') as stream:\n        raw = stream.read(8193)\n    need(len(raw) <= 8192)\n    names = [line.split(\'"\'"\':\'"\'"\', 1)[0].strip() for line in raw.decode(\'"\'"\'ascii\'"\'"\').splitlines()[2:] if \'"\'"\':\'"\'"\' in line]\n    need(names == [\'"\'"\'lo\'"\'"\'])\n    request = struct.pack(\'"\'"\'16sH22x\'"\'"\', b\'"\'"\'lo\'"\'"\', 0)\n    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC) as handle:\n        before = fcntl.ioctl(handle.fileno(), 0x8913, request)\n        flags = struct.unpack_from(\'"\'"\'H\'"\'"\', before, 16)[0]\n        need(flags & 0x8 and not flags & ~0x49)\n        # Only the IFF_UP bit of the fixed loopback interface is changed.\n        fcntl.ioctl(handle.fileno(), 0x8914, struct.pack(\'"\'"\'16sH22x\'"\'"\', b\'"\'"\'lo\'"\'"\', flags | 0x1))\n        after = fcntl.ioctl(handle.fileno(), 0x8913, request)\n        observed = struct.unpack_from(\'"\'"\'H\'"\'"\', after, 16)[0]\n        need(observed & 0x9 == 0x9 and not observed & ~0x49)\n    need(os.readlink(\'"\'"\'/proc/self/ns/net\'"\'"\') == namespace)\n    return 0\n\nif __name__ == \'"\'"\'__main__\'"\'"\':\n    try:\n        sys.exit(run())\n    except BaseException as exc:\n        if isinstance(exc, SystemExit):\n            raise\n        sys.stderr.write(\'"\'"\'DG17_LOOPBACK_ADMISSION_REFUSED\\n\'"\'"\')\n        sys.exit(1)\n\' "$7"\nexec /usr/bin/setpriv --reuid "$1" --regid "$2" --clear-groups --no-new-privs /usr/bin/python3 -I -S -B -c "$3" "$1" "$2" "$4" "$5" "$6" "$7" "$8" "${@:9}"\n'
CAPSULE_SCRIPT_SHA = 'b52156331674cc4cf0f0e29bb5b4e6922098e216724defcac070aa2aad2d6f1d'
CAPSULE_CODE = "import fcntl,hashlib,ipaddress,json,os,re,socket,stat,struct,subprocess,sys\nTARGETS=('/opt','/usr/local/bin','/etc/gitconfig')\nCONFIG_SOURCE='/opt/dg17-empty-system-gitconfig'\nEMPTY_SHA='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'\ndef need(ok,code):\n    if not ok: raise RuntimeError(code)\ndef encode(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\\n').encode()\ndef sha(raw):return hashlib.sha256(raw).hexdigest()\ndef parse_mounts(raw):\n    need(type(raw) is bytes and len(raw)<=1048576,'MOUNTINFO_BOUND')\n    lines=raw.decode('ascii').splitlines();need(1<=len(lines)<=4096,'MOUNTINFO_POPULATION')\n    rows={};private=True\n    for line in lines:\n        fields=line.split();need('-' in fields,'MOUNTINFO_SHAPE');split=fields.index('-')\n        need(split>=6 and len(fields)>=split+4,'MOUNTINFO_SHAPE')\n        if any(x.startswith(('shared:','master:','propagate_from:')) for x in fields[6:split]):private=False\n        if fields[4] not in TARGETS:continue\n        path=fields[4];need(path not in rows,'DUPLICATE_TARGET_MOUNT')\n        opts=fields[5].split(',');superopts=fields[split+3].split(',')\n        size=[x[5:] for x in superopts if x.startswith('size=')]\n        need(len(size)==1 and re.fullmatch(r'[0-9]+[kKmMgG]?',size[0]),'TMPFS_SIZE')\n        token=size[0];suffix=token[-1].lower();factor={'k':1024,'m':1048576,'g':1073741824}.get(suffix,1)\n        number=int(token[:-1]) if suffix in 'kmg' else int(token)\n        need(all(re.fullmatch(r'[0-9]{1,12}',fields[i]) for i in (0,1)),'MOUNT_ID')\n        rows[path]={'path':path,'mount_id':int(fields[0]),'parent_mount_id':int(fields[1]),'mount_root':fields[3],\n                    'filesystem':fields[split+1],'mount_source':fields[split+2],\n                    'readonly':'ro' in opts and 'rw' not in opts and 'ro' in superopts and 'rw' not in superopts,\n                    'nodev':'nodev' in opts,'nosuid':'nosuid' in opts,'noexec':'noexec' in opts,\n                    'size_bytes':number*factor,'mount_options_sha256':sha(fields[5].encode()),\n                    'super_options_sha256':sha(fields[split+3].encode())}\n    need(set(rows)==set(TARGETS),'TARGET_MOUNTS_MISSING')\n    return private,len(lines),[rows[path] for path in TARGETS]\ndef file_snapshot(path):\n    before=os.lstat(path)\n    need(os.path.realpath(path)==path and stat.S_ISREG(before.st_mode) and\n         before.st_uid==0 and before.st_gid==0 and stat.S_IMODE(before.st_mode)==0o644 and\n         before.st_nlink==1 and before.st_size==0,'EMPTY_CONFIG_FILE')\n    with open(path,'rb') as stream:raw=stream.read(1)\n    after=os.lstat(path)\n    identity=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)\n    need(identity(before)==identity(after) and raw==b'','EMPTY_CONFIG_FILE_CHANGED')\n    return {'file_uid':before.st_uid,'file_gid':before.st_gid,'mode':stat.S_IMODE(before.st_mode),\n            'regular':True,'symlink':False,'nlink':before.st_nlink,'bytes':len(raw),'sha256':sha(raw),\n            'device':before.st_dev,'inode':before.st_ino}\ndef network_snapshot(parent):\n    need(re.fullmatch(r'net:\\[[0-9]+\\]', parent) is not None, 'PARENT_NETWORK_NAMESPACE')\n    namespace = os.readlink('/proc/self/ns/net')\n    need(re.fullmatch(r'net:\\[[0-9]+\\]', namespace) is not None and namespace != parent,\n         'NETWORK_NAMESPACE_NOT_DISTINCT')\n    def bounded(path):\n        with open(path, 'rb') as stream:\n            raw = stream.read(8193)\n        need(len(raw) <= 8192, 'NETWORK_METADATA_BOUND')\n        return raw.decode('ascii').splitlines()\n    lines = bounded('/proc/net/dev')\n    need(2 <= len(lines) <= 4, 'NETWORK_INTERFACE_POPULATION')\n    names = [line.split(':', 1)[0].strip() for line in lines[2:] if ':' in line]\n    need(names == ['lo'], 'NONLOOPBACK_INTERFACE_PRESENT')\n    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC) as handle:\n        flags_raw = fcntl.ioctl(handle.fileno(), 0x8913, struct.pack('16sH22x', b'lo', 0))\n        flags = struct.unpack_from('H', flags_raw, 16)[0]\n        address_raw = fcntl.ioctl(handle.fileno(), 0x8915, struct.pack('16sH22x', b'lo', 0))\n    need(flags in (0x9, 0x49), 'LOOPBACK_NOT_UP_OR_FLAGS_UNREVIEWED')\n    need(struct.unpack_from('H', address_raw, 16)[0] == socket.AF_INET and\n         address_raw[20:24] == b'\\x7f\\x00\\x00\\x01', 'LOOPBACK_ADDRESS_DIFFERS')\n    route4 = []\n    lines4 = bounded('/proc/net/route')\n    need(1 <= len(lines4) <= 33, 'IPV4_ROUTE_POPULATION')\n    for line in lines4[1:]:\n        fields = line.split()\n        need(len(fields) == 11 and fields[0] == 'lo' and\n             all(re.fullmatch(r'[0-9a-fA-F]{8}', fields[i]) for i in (1, 2, 7)),\n             'IPV4_ROUTE_SHAPE')\n        need(ipaddress.IPv4Address(bytes.fromhex(fields[1])[::-1]).is_loopback and\n             int(fields[2], 16) == 0, 'EXTERNAL_IPV4_ROUTE')\n        route4.append([fields[i] for i in (0, 1, 2, 3, 7, 8, 9, 10)])\n    route6 = []\n    lines6 = bounded('/proc/net/ipv6_route')\n    need(len(lines6) <= 32, 'IPV6_ROUTE_POPULATION')\n    for line in lines6:\n        fields = line.split()\n        need(len(fields) == 10 and fields[9] == 'lo' and\n             all(re.fullmatch(r'[0-9a-fA-F]{32}', fields[i]) for i in (0, 2, 4)) and\n             all(re.fullmatch(r'[0-9a-fA-F]{2}', fields[i]) for i in (1, 3)) and\n             all(re.fullmatch(r'[0-9a-fA-F]{8}', fields[i]) for i in (5, 6, 7, 8)),\n             'IPV6_ROUTE_SHAPE')\n        rejected = bool(int(fields[8], 16) & 0x200)\n        loopback = int(fields[1], 16) == 128 and ipaddress.IPv6Address(int(fields[0], 16)).is_loopback\n        need((rejected or loopback) and int(fields[4], 16) == 0, 'EXTERNAL_IPV6_ROUTE')\n        route6.append([fields[i] for i in (0, 1, 2, 3, 4, 5, 8, 9)])\n    # Traffic counters and transient reference/use counts are deliberately not\n    # identity fields. Addresses, flags and admitted route population are.\n    routes = {'ipv4': sorted(route4), 'ipv6': sorted(route6)}\n    return {'network_namespace_sha256': sha(namespace.encode()),\n            'namespace_distinct': True, 'interfaces': ['lo'], 'loopback_up': True,\n            'loopback_flags': flags, 'loopback_address': '127.0.0.1',\n            'external_routes': 0, 'ipv4_route_count': len(route4),\n            'ipv6_route_count': len(route6), 'route_population_sha256': sha(encode(routes))}\n\ndef snapshot(uid,gid,parent,network_parent):\n    namespace=os.readlink('/proc/self/ns/mnt')\n    raw=open('/proc/self/mountinfo','rb').read(1048577)\n    private,count,rows=parse_mounts(raw)\n    fields={}\n    for line in open('/proc/self/status',encoding='ascii'):\n        if ':' in line:\n            key,value=line.split(':',1);fields[key]=value.strip()\n    uids=[int(x) for x in fields['Uid'].split()];gids=[int(x) for x in fields['Gid'].split()]\n    caps={key:int(fields[key],16) for key in ('CapEff','CapPrm','CapAmb')}\n    for row in rows[:2]:\n        path=row['path'];info=os.lstat(path);entries=sorted(os.listdir(path))\n        expected=['dg17-empty-system-gitconfig'] if path=='/opt' else []\n        need(entries==expected,'TARGET_DIRECTORY_POPULATION')\n        row.update(directory_uid=info.st_uid,directory_gid=info.st_gid,mode=stat.S_IMODE(info.st_mode),\n                   directory=stat.S_ISDIR(info.st_mode),symlink=stat.S_ISLNK(info.st_mode),\n                   entries=len(entries),device=info.st_dev,inode=info.st_ino)\n    source=file_snapshot(CONFIG_SOURCE);target=file_snapshot('/etc/gitconfig');rows[2].update(target)\n    need(source==target and source['device']==rows[0]['device'],'EMPTY_CONFIG_BIND_IDENTITY')\n    result={'mount_namespace_sha256':sha(namespace.encode()),'namespace_distinct':namespace!=parent,\n            'private_propagation':private,'mountinfo_sha256':sha(raw),'mount_count':count,\n            'uids':uids,'gids':gids,'groups':os.getgroups(),'capabilities':caps,\n            'no_new_privileges':int(fields['NoNewPrivs']),'mounts':rows,\n            'gitconfig_source':{'path':CONFIG_SOURCE,**source},'source_target_same_file':True,\n            'network':network_snapshot(network_parent)}\n    need(result['namespace_distinct'] and private and uids==[uid]*4 and gids==[gid]*4 and\n         not result['groups'] and all(v==0 for v in caps.values()) and result['no_new_privileges']==1,'PRIVILEGE_OR_NAMESPACE')\n    need(len({row['mount_id'] for row in rows})==3 and all(row['filesystem']=='tmpfs' and row['mount_source']=='tmpfs' and\n             row['mount_root']==('/dg17-empty-system-gitconfig' if row['path']=='/etc/gitconfig' else '/') and\n             row['mount_id']>0 and row['parent_mount_id']>0 and row['mount_id']!=row['parent_mount_id'] and\n             all(row[key] is True for key in ('readonly','nodev','nosuid','noexec')) and row['size_bytes']==4096 for row in rows),'TARGET_MOUNT_VIEW')\n    need(all(row['directory'] is True and row['symlink'] is False and row['directory_uid']==0 and\n             row['directory_gid']==0 and row['mode']==0o755 and row['entries']==(1 if row['path']=='/opt' else 0)\n             for row in rows[:2]),'TARGET_DIRECTORY_VIEW')\n    return result\ndef write(path,value,uid):\n    parent=os.path.dirname(path);info=os.lstat(parent)\n    need(os.path.realpath(parent)==parent and stat.S_ISDIR(info.st_mode) and info.st_uid==uid,'PROOF_PARENT')\n    raw=encode(value);need(len(raw)<=16384,'PROOF_BOUND')\n    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())\n    return sha(raw)\ndef run():\n    need(len(sys.argv)==28,'ARGUMENT_POPULATION')\n    uid=int(sys.argv[1]);gid=int(sys.argv[2]);before_path=sys.argv[3];result_path=sys.argv[4];parent=sys.argv[5];network_parent=sys.argv[6]\n    need(uid>0 and gid>0 and re.fullmatch(r'mnt:\\[[0-9]+\\]',parent),'ARGUMENT_VALUE')\n    need(os.path.basename(before_path)=='CAPSULE_ADMISSION.json' and\n         os.path.basename(result_path)=='CAPSULE_RESULT.json' and\n         os.path.dirname(before_path)==os.path.dirname(result_path),'PROOF_PATHS')\n    argv=['/usr/bin/python3','-I','-S','-B',*sys.argv[7:]]\n    argv_sha=sha(encode(argv));before=snapshot(uid,gid,parent,network_parent)\n    proof={'schema':'dg17.private-view-admission.v3','child_argv_sha256':argv_sha,'snapshot':before}\n    before_sha=write(before_path,proof,uid)\n    child_rc=None;after=None;failure=None\n    try:\n        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,close_fds=True)\n        child_rc=child.wait()\n    except BaseException:\n        failure='CHILD_START_OR_WAIT_REFUSED'\n    try:after=snapshot(uid,gid,parent,network_parent)\n    except BaseException:\n        failure=failure or 'AFTER_VIEW_REFUSED'\n    result={'schema':'dg17.private-view-result.v3','before_sha256':before_sha,'child_argv_sha256':argv_sha,\n            'before':before,'after':after,'child_returncode':child_rc,'failure':failure}\n    write(result_path,result,uid)\n    return 0 if failure is None and child_rc==0 and before==after else 1\nif __name__=='__main__':\n    try:sys.exit(run())\n    except BaseException as exc:\n        if isinstance(exc,SystemExit):raise\n        sys.stderr.write('DG17_CAPSULE_ADMISSION_REFUSED\\n');sys.exit(1)\n"
CAPSULE_CODE_SHA = 'b1a4b6bed2bb3d1b7e85b40059a652a10eb71b9509c6054d56661523ebb3b028'
PRIOR_COMPONENT = {'run_id': 42210454718, 'attempt': 1, 'artifact_id': 13497879213, 'artifact_sha256': '9a285ea3756238ac689669782b690a5aa05dfdbbe14a2c285694085ce3b70847', 'predicate_member_sha256': '9028d6711dc1e02b2babf6fc5e4e70974a99a3ed54b547d391ded3f8033af73a', 'source_commit': '0d57929be5bd15682b4e9da2c0209d5dff307843', 'source_tree': 'ee316c27250ec422d35a1ea965182ebddf7a5da0', 'test_path': 'tests/shell_companion_source_custody.py', 'test_source_sha256': '22ffd31ff45e1f439759c45bb5c67bde5e8390b69b54030833476e80aaee7f08', 'independent_receipt_sha256': '9ba49dfeb1ec8e7ac3c4fe122e5c89227340405fa729d48c0c651b8fa12bf07f', 'root_receipt_sha256': 'a63dc54e1812ddf4a57091360d09753fc3b0c9dae90d6cddd4bcc757bc550a64', 'scope': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD'}

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
def claude_capture_base_shape(row, name):
    keys = {'name','process_started','returncode','timeout','output_bound_exceeded',
            'pidfd_acquired','internal_failure','reason_code','stream_digest_scope',
            'streams_complete','stdout_bytes','stderr_bytes','stdout_sha256','stderr_sha256',
            'cleanup','private_streams_retained','retention_failure'}
    if type(row) is not dict or set(row) != keys or row['name'] != name: return False
    if not all(type(row[k]) is bool for k in ('process_started','timeout','output_bound_exceeded','pidfd_acquired','streams_complete','private_streams_retained','retention_failure')): return False
    if type(row['returncode']) is not int or row['internal_failure'] is not None or type(row['reason_code']) is not str or not 1 <= len(row['reason_code']) <= 96 or row['stream_digest_scope'] != 'CAPTURED_BYTES_ONLY': return False
    if any(type(row[k+'_bytes']) is not int or not 0 <= row[k+'_bytes'] <= 32768 or type(row[k+'_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row[k+'_sha256']) is None for k in ('stdout','stderr')): return False
    cleanup = row['cleanup']
    if type(cleanup) is not dict or set(cleanup) != {'echild','pidfd_signals','retained_status_count','retained_statuses_sha256','reaped_statuses','reaped_statuses_truncated'}: return False
    if type(cleanup['echild']) is not bool or type(cleanup['reaped_statuses_truncated']) is not bool or any(type(cleanup[k]) is not int or cleanup[k] < 0 for k in ('pidfd_signals','retained_status_count')): return False
    if type(cleanup['retained_statuses_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',cleanup['retained_statuses_sha256']) is None: return False
    statuses = cleanup['reaped_statuses']; count = cleanup['retained_status_count']
    if type(statuses) is not list or len(statuses) != min(count,8) or cleanup['reaped_statuses_truncated'] is not (count > 8): return False
    if any(type(item) is not dict or set(item) != {'pid','returncode'} or type(item['pid']) is not int or item['pid'] <= 0 or type(item['returncode']) is not int for item in statuses): return False
    return True

def body_canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')

def body_json(raw, limit=2097152):
    need(type(raw) is bytes and len(raw) <= limit, 'BODY_JSON_BYTE_BOUND')
    def nonfinite(_):
        raise Refusal('BODY_JSON_NONFINITE')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                           parse_constant=nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('BODY_JSON_UNRECEIVED') from None
    pending = [(value, 0)]; count = 0
    while pending:
        item, depth = pending.pop(); count += 1
        need(count <= 32768 and depth <= 32, 'BODY_JSON_COMPLEXITY')
        if type(item) is dict:
            need(len(item) <= 1024 and all(type(k) is str and len(k) <= 1024 for k in item),
                 'BODY_JSON_OBJECT_BOUND')
            pending.extend((v, depth + 1) for v in item.values())
        elif type(item) is list:
            need(len(item) <= 4096, 'BODY_JSON_ARRAY_BOUND')
            pending.extend((v, depth + 1) for v in item)
        elif type(item) is str:
            need(len(item.encode('utf-8')) <= limit, 'BODY_JSON_STRING_BOUND')
        elif type(item) is float:
            need(math.isfinite(item), 'BODY_JSON_NONFINITE')
        else:
            need(item is None or type(item) in (bool, int), 'BODY_JSON_TYPE')
    return value

def body_owned_file(path, maximum):
    info = path.lstat()
    need(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and
         info.st_uid == os.getuid() and info.st_nlink == 1 and not info.st_mode & 0o022 and
         info.st_size <= maximum, 'BODY_FILE_IDENTITY')
    size, value = stream_hash(path); after = path.lstat()
    identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(info) == identity(after) and size == info.st_size, 'BODY_FILE_CHANGED')
    return {'bytes': size, 'sha256': value}

def body_owned_directory(path):
    info = path.lstat()
    need(path.resolve(strict=True) == path and stat.S_ISDIR(info.st_mode) and
         info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
         'BODY_DIRECTORY_IDENTITY')

def body_archive_input(packet):
    path = packet/'package-inputs/IMPLEMENTAUDIT.plugin.zip'
    need(stat.S_IMODE(path.lstat().st_mode) == 0o644, 'BODY_ARCHIVE_MODE')
    need(body_owned_file(path, BODY_ARCHIVE_BYTES) ==
         {'bytes':BODY_ARCHIVE_BYTES,'sha256':BODY_ARCHIVE_SHA}, 'BODY_ARCHIVE_PIN')
    return path

def body_package_receiving(packet, output):
    archive = body_archive_input(packet)
    matrix_raw = read(packet/'CANONICAL_PACKAGE_MATRIX.json', 32768)
    need(digest(matrix_raw) == BODY_MATRIX_SHA, 'BODY_MATRIX_PIN')
    matrix = body_json(matrix_raw, 32768)
    need(type(matrix) is dict and len(matrix) == 75 and encoded(matrix) == matrix_raw,
         'BODY_MATRIX_POPULATION')
    for name,row in matrix.items():
        need(type(name) is str and name and len(name) <= 512 and '\\' not in name and
             not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/')),
             'BODY_MATRIX_PATH')
        need(type(row) is dict and set(row) == {'bytes','sha256','mode'} and
             type(row['bytes']) is int and 0 <= row['bytes'] <= 8388608 and
             type(row['mode']) is int and row['mode'] in (0o644,0o755) and
             type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']),
             'BODY_MATRIX_ROW')
    need(sum(row['bytes'] for row in matrix.values()) == 2092025, 'BODY_MATRIX_TOTAL')
    raw = read(archive, BODY_ARCHIVE_BYTES)
    need(len(raw) == BODY_ARCHIVE_BYTES and digest(raw) == BODY_ARCHIVE_SHA, 'BODY_ARCHIVE_READBACK')
    with zipfile.ZipFile(io.BytesIO(raw)) as opened:
        entries = opened.infolist()
        need(len(entries) == 75 and len({entry.filename for entry in entries}) == 75 and
             {entry.filename for entry in entries} == set(matrix), 'BODY_ARCHIVE_POPULATION')
        for entry in entries:
            wanted = matrix[entry.filename]; mode = entry.external_attr >> 16
            need(not entry.is_dir() and stat.S_ISREG(mode) and stat.S_IMODE(mode) == wanted['mode'] and
                 entry.file_size == wanted['bytes'] and not entry.flag_bits & 1,
                 'BODY_ARCHIVE_MEMBER_SHAPE')
            content = opened.read(entry)
            need(len(content) == wanted['bytes'] and digest(content) == wanted['sha256'],
                 'BODY_ARCHIVE_MEMBER_BYTES')
    effective = output/'private/claude-canonical-body/effective-plugin'
    body_owned_directory(effective)
    files = {}; directories = set(); pending = [effective]; count = 0
    try:
        while pending:
            directory = pending.pop()
            with os.scandir(directory) as iterator:
                names = []
                for entry in iterator:
                    names.append(entry.name); need(len(names) <= 128, 'BODY_PACKAGE_POPULATION')
            for name in names:
                path = directory/name; relative = path.relative_to(effective).as_posix()
                info = path.lstat(); count += 1
                need(count <= 128 and len(path.relative_to(effective).parts) <= 16,
                     'BODY_PACKAGE_POPULATION')
                if stat.S_ISDIR(info.st_mode):
                    body_owned_directory(path); directories.add(relative); pending.append(path)
                else:
                    need(relative in matrix and stat.S_ISREG(info.st_mode), 'BODY_PACKAGE_UNEXPECTED_ENTRY')
                    wanted = matrix[relative]
                    need(stat.S_IMODE(info.st_mode) == wanted['mode'], 'BODY_PACKAGE_MODE')
                    files[relative] = {**body_owned_file(path,wanted['bytes']), 'mode':stat.S_IMODE(info.st_mode)}
    except OSError:
        raise Refusal('BODY_PACKAGE_ENUMERATION_REFUSED') from None
    wanted_dirs = {parent.as_posix() for name in matrix for parent in Path(name).parents
                   if parent.as_posix() != '.'}
    need(files == matrix and directories == wanted_dirs, 'BODY_PACKAGE_COMPLETE_POPULATION')
    body_archive_input(packet)
    governor = read(effective/'skills/implementaudit/SKILL.md', 32768)
    need(len(governor) == 21257 and digest(governor) == BODY_GOVERNOR_SHA,
         'BODY_GOVERNOR_SOURCE_PIN')
    return governor, {'archive_bytes':BODY_ARCHIVE_BYTES,'archive_sha256':BODY_ARCHIVE_SHA,
        'member_count':75,'directory_count':len(directories),'expanded_bytes':2092025,
        'matrix_sha256':BODY_MATRIX_SHA,'all_actual_members_verified':True}

def body_startup_receiving(output, state):
    root = output/'private/claude-canonical-body/context-canonical-body'
    paths = {name:root/name for name in ('home','config','xdg_config','xdg_cache','xdg_data','xdg_state','cwd')}
    body_owned_directory(root)
    for path in paths.values(): body_owned_directory(path)
    settings = {'disableAllHooks':True,'syncClaudeAiSkills':False,'syncClaudeAiPlugins':False,
                'disableClaudeAiConnectors':True,'remoteControlAtStartup':False}
    for name,value in (('selected-settings.json',settings),('empty-mcp.json',{'mcpServers':{}})):
        expected = body_canonical(value); path = root/name
        need(body_owned_file(path,len(expected)) == {'bytes':len(expected),'sha256':digest(expected)} and
             read(path,len(expected)) == expected, 'BODY_STARTUP_CONFIG_CHANGED')
    forbidden = [paths['home']/'.claude',paths['home']/'.claude.json',
                 paths['home']/'.config/anthropic',paths['home']/'.config/claude',
                 paths['xdg_config']/'anthropic',paths['xdg_config']/'claude']
    forbidden += [paths['config']/name for name in ('settings.json','settings.local.json','.credentials.json',
                  'credentials.json','managed-settings.json','managed-mcp.json','skills','hooks','mcp.json','.mcp.json')]
    need(all(not os.path.lexists(path) for path in forbidden), 'BODY_UNREVIEWED_STARTUP_LAYER')
    plugins = body_plugins_census(root,os.geteuid(),os.getegid())
    custody = body_plugins_receiving_success(state,'PRIVATE_SUCCESS')
    need(body_plugins_projection(plugins,os.geteuid(),os.getegid(),custody)['profile_admitted'],
         'BODY_UNREVIEWED_STARTUP_LAYER')
    etc = Path('/etc'); info = etc.lstat()
    need(etc.resolve(strict=True) == etc and stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and
         not info.st_mode & 0o022 and not os.path.lexists(etc/'claude-code'), 'BODY_MANAGED_POLICY_PRESENT')
    for directory in (paths['cwd'], *paths['cwd'].parents):
        for name in ('.claude','.mcp.json','CLAUDE.md','CLAUDE.local.md'):
            need(not os.path.lexists(directory/name), 'BODY_ANCESTOR_STARTUP_LAYER')
    return paths

def body_private_rows(root):
    body_owned_directory(root)
    identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    pending = [root]; population = []; identities = {root:identity(root.lstat())}
    try:
        while pending:
            directory = pending.pop()
            need(identity(directory.lstat()) == identities[directory], 'BODY_PRIVATE_DIRECTORY_CHANGED')
            with os.scandir(directory) as iterator:
                names = []
                for entry in iterator:
                    names.append(entry.name); need(len(names) <= 513, 'BODY_PRIVATE_POPULATION')
            for name in names:
                path = directory/name
                if path == root/'PRIVATE_EVIDENCE_SEAL.json': continue
                info = path.lstat()
                need(len(population) < 512 and len(path.relative_to(root).parts) <= 16,
                     'BODY_PRIVATE_POPULATION')
                need(not stat.S_ISLNK(info.st_mode), 'BODY_PRIVATE_SYMLINK')
                population.append(path)
                identities[path] = identity(info)
                if stat.S_ISDIR(info.st_mode):
                    body_owned_directory(path); pending.append(path)
        rows = []; total = 0
        for path in sorted(population,key=lambda p:p.relative_to(root).as_posix()):
            info = path.lstat(); relative = path.relative_to(root).as_posix()
            need(identity(info) == identities[path], 'BODY_PRIVATE_CLASSIFICATION_CHANGED')
            if stat.S_ISDIR(info.st_mode):
                body_owned_directory(path); rows.append({'path':relative,'kind':'DIRECTORY'})
            else:
                item = body_owned_file(path,8388608); total += item['bytes']
                need(total <= 33554432, 'BODY_PRIVATE_TOTAL_BOUND')
                rows.append({'path':relative,'kind':'REGULAR',**item})
        need(all(identity(path.lstat()) == stamp for path,stamp in identities.items()),
             'BODY_PRIVATE_POPULATION_CHANGED_DURING_READ')
        return rows
    except OSError:
        raise Refusal('BODY_PRIVATE_ENUMERATION_REFUSED') from None


def body_http_request(raw, expected_port):
    need(type(raw) is bytes and len(raw) <= 2129920 and b'\r\n\r\n' in raw,
         'BODY_HTTP_REQUEST_BOUND')
    split = raw.index(b'\r\n\r\n') + 4
    need(split <= 32768, 'BODY_HTTP_HEADER_BOUND')
    try: lines = raw[:split-4].decode('ascii').split('\r\n')
    except UnicodeError: raise Refusal('BODY_HTTP_HEADER_ENCODING') from None
    need(1 <= len(lines) <= 65 and all('\r' not in line and '\n' not in line for line in lines),
         'BODY_HTTP_HEADER_SHAPE')
    request = lines[0].split(' ')
    need(len(request) == 3 and request[0] in ('HEAD','POST') and
         request[2] in ('HTTP/1.0','HTTP/1.1') and len(request[1]) <= 512,
         'BODY_HTTP_REQUEST_LINE')
    headers = {}
    for line in lines[1:]:
        need(':' in line and not line.startswith((' ','\t')), 'BODY_HTTP_HEADER_SHAPE')
        name,value = line.split(':',1); name = name.lower()
        need(re.fullmatch('[a-z0-9-]{1,80}',name) and name not in headers,
             'BODY_HTTP_DUPLICATE_HEADER')
        headers[name] = value.strip()
    matched = re.fullmatch(r'127\.0\.0\.1:([0-9]{1,5})',headers.get('host',''))
    need(matched is not None, 'BODY_HTTP_HOST')
    port = int(matched.group(1))
    need(1024 <= port <= 65535 and (expected_port is None or expected_port == port),
         'BODY_HTTP_PORT_CHANGED')
    need('transfer-encoding' not in headers and 'content-encoding' not in headers,
         'BODY_HTTP_UNREVIEWED_ENCODING')
    size = headers.get('content-length','0')
    need(re.fullmatch('[0-9]{1,10}',size) and int(size) <= 2097152 and len(raw)-split == int(size),
         'BODY_HTTP_TRUNCATED_OR_EXTRA_BYTES')
    body = raw[split:]
    if request[0] == 'HEAD':
        need(request[1] == '/api/hello' and not body, 'BODY_HTTP_ENDPOINT')
        kind = 'STARTUP_HEAD'
    else:
        need(request[1] in ('/v1/messages','/v1/messages?beta=true','/v1/messages/count_tokens'),
             'BODY_HTTP_ENDPOINT')
        need(headers.get('authorization') == 'Bearer dg17-loopback-fixture-not-an-upstream-credential' and
             headers.get('content-type','').split(';',1)[0].strip() == 'application/json' and body,
             'BODY_HTTP_SELECTED_AUTH_OR_CONTENT_TYPE')
        body_json(body)
        kind = 'TOKEN_COUNT' if request[1].endswith('/count_tokens') else 'MESSAGES'
    return port, kind, body

def body_expected_response(kind):
    if kind == 'STARTUP_HEAD':
        status,label,content_type,body = 200,'OK','text/plain',b''
    elif kind == 'TOKEN_COUNT':
        status,label,content_type = 501,'Not Implemented','application/json'
        body = body_canonical({'type':'error','error':{'type':'not_found_error',
                 'message':'Optional token counting is unavailable in the local fixture.'}})
    else:
        need(kind == 'MESSAGES', 'BODY_RESPONSE_KIND')
        status,label,content_type = 200,'OK','text/event-stream'
        events = [
            ('message_start',{'type':'message_start','message':{'id':'msg_dg17_local_canonical_01',
                'type':'message','role':'assistant','content':[],'model':'claude-sonnet-4-6',
                'stop_reason':None,'stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':0}}}),
            ('content_block_start',{'type':'content_block_start','index':0,
                'content_block':{'type':'text','text':''}}),
            ('content_block_delta',{'type':'content_block_delta','index':0,
                'delta':{'type':'text_delta','text':BODY_ACK}}),
            ('content_block_stop',{'type':'content_block_stop','index':0}),
            ('message_delta',{'type':'message_delta','delta':{'stop_reason':'end_turn',
                'stop_sequence':None},'usage':{'output_tokens':1}}),
            ('message_stop',{'type':'message_stop'})]
        body = b''.join(b'event: '+kind.encode('ascii')+b'\ndata: '+body_canonical(value).rstrip(b'\n')+
                        b'\n\n' for kind,value in events)
    need(len(body) <= 16384, 'BODY_PREPARED_RESPONSE_BOUND')
    return (f'HTTP/1.1 {status} {label}\r\nContent-Type: {content_type}\r\n'
            f'Content-Length: {len(body)}\r\nConnection: close\r\nx-should-retry: false\r\n\r\n').encode('ascii')+body

def body_provider_receiving(root, public):
    raw = read(root/'PROVIDER_RECORD.json',262144)
    need(digest(raw) == public['provider_record_sha256'], 'BODY_PROVIDER_RECORD_PIN')
    value = body_json(raw,262144)
    need(type(value) is dict and set(value) == {'schema','custody','requests','request_capture_scope','response_capture_scope'} and
         value['schema'] == 'dg17.claude.local-provider-record.v1' and
         value['request_capture_scope'] == 'CAPTURED_HTTP_BYTES_ONLY' and
         value['response_capture_scope'] == 'PREPARED_BYTES_AND_SOCKET_SEND_RETURNED_COUNT',
         'BODY_PROVIDER_RECORD_SHAPE')
    custody = value['custody']
    keys = {'started','thread_joined','all_owned_sockets_closed','verified','request_count',
            'semantic_request_count','captured_request_bytes','semantic_response_complete',
            'failure','supplemental_failures','semantic_request_index'}
    need(type(custody) is dict and set(custody) == keys and custody == public['provider_custody'] and
         all(custody[k] is True for k in ('started','thread_joined','all_owned_sockets_closed','verified','semantic_response_complete')) and
         custody['failure'] is None and custody['supplemental_failures'] == [], 'BODY_PROVIDER_CUSTODY')
    rows = value['requests']
    need(type(rows) is list and 1 <= len(rows) <= 16 and type(custody['request_count']) is int and
         custody['request_count'] == len(rows) and type(custody['semantic_request_count']) is int and
         custody['semantic_request_count'] == 1, 'BODY_PROVIDER_REQUEST_POPULATION')
    row_keys = {'index','kind','request_complete','request_bytes','request_sha256','body_bytes','body_sha256',
                'prepared_response_bytes','prepared_response_sha256','socket_send_returned_bytes','response_send_complete'}
    port = None; semantic = []; total = 0; expected_files = set()
    for index,row in enumerate(rows,1):
        need(type(row) is dict and set(row) == row_keys and type(row['index']) is int and row['index'] == index and
             row['request_complete'] is True and row['response_send_complete'] is True,
             'BODY_PROVIDER_REQUEST_RECORD')
        stem = 'request-'+str(index).zfill(3)
        expected_files.update(stem+suffix for suffix in ('.http','.body','.response'))
        request = read(root/'provider'/(stem+'.http'),2129920)
        body = read(root/'provider'/(stem+'.body'),2097152)
        response = read(root/'provider'/(stem+'.response'),32768)
        for field,content in (('request',request),('body',body),('prepared_response',response)):
            need(type(row[field+'_bytes']) is int and row[field+'_bytes'] == len(content) and
                 row[field+'_sha256'] == digest(content), 'BODY_PROVIDER_PRIVATE_BYTE_BINDING')
        need(type(row['socket_send_returned_bytes']) is int and row['socket_send_returned_bytes'] == len(response) and response,
             'BODY_PROVIDER_RESPONSE_SEND_INCOMPLETE')
        port,kind,parsed_body = body_http_request(request,port)
        need(kind == row['kind'] and parsed_body == body and response == body_expected_response(kind),
             'BODY_PROVIDER_PROTOCOL_OR_PREPARED_RESPONSE_DIFFERS')
        if kind == 'MESSAGES':
            request_value = body_json(body)
            need(type(request_value) is dict and request_value.get('stream') is True and
                 request_value.get('model') == 'claude-sonnet-4-6' and
                 type(request_value.get('messages')) is list, 'BODY_SEMANTIC_REQUEST_SHAPE')
            semantic.append((index,body))
        total += len(request); need(total <= 4194304, 'BODY_PROVIDER_AGGREGATE_BOUND')
    need(len(semantic) == 1 and type(custody['semantic_request_index']) is int and
         custody['semantic_request_index'] == semantic[0][0] and
         type(custody['captured_request_bytes']) is int and custody['captured_request_bytes'] == total,
         'BODY_PROVIDER_SEMANTIC_JOIN')
    try:
        with os.scandir(root/'provider') as iterator:
            names = []
            for entry in iterator:
                names.append(entry.name); need(len(names) <= 48, 'BODY_PROVIDER_FILE_POPULATION')
        need(set(names) == expected_files, 'BODY_PROVIDER_FILE_POPULATION')
        for name in names:
            need(stat.S_ISREG((root/'provider'/name).lstat().st_mode), 'BODY_PROVIDER_NONREGULAR_FILE')
    except OSError:
        raise Refusal('BODY_PROVIDER_ENUMERATION_REFUSED') from None
    return semantic[0][1], {'request_count':len(rows),'semantic_requests':1,'captured_request_bytes':total,
        'all_private_byte_slices_verified':True,'exact_prepared_responses_verified':True,
        'recorded_send_counts_complete':True,'recorded_thread_and_socket_custody_verified':True}

def body_delivery_projection(request_raw, governor, session_id):
    value = body_json(request_raw)
    need(type(value) is dict and type(value.get('messages')) is list and
         governor.startswith(b'---\n') and b'\n---\n' in governor, 'BODY_DELIVERY_INPUT_SHAPE')
    body = governor[governor.index(b'\n---\n')+5:].strip(b'\n')
    need(len(body) == 20431 and digest(body) == BODY_RENDERED_SHA and b'$ARGUMENTS' not in body and
         b'${CLAUDE_' not in body and b'!`' not in body, 'BODY_DELIVERY_SOURCE_BOUNDARY')
    expected = body.decode('utf-8'); observations = []; marker_seen = False
    for i,message in enumerate(value['messages']):
        need(type(message) is dict, 'BODY_REQUEST_MESSAGE_SHAPE')
        if message.get('role') != 'user': continue
        content = message.get('content')
        blocks = [{'type':'text','text':content}] if type(content) is str else content
        need(type(blocks) is list, 'BODY_REQUEST_USER_CONTENT')
        for j,block in enumerate(blocks):
            need(type(block) is dict, 'BODY_REQUEST_BLOCK_SHAPE')
            if block.get('type') != 'text': continue
            text = block.get('text'); need(type(text) is str, 'BODY_REQUEST_TEXT_SHAPE')
            marker_seen = marker_seen or ('DG17_OPERATION_ID='+session_id) in text
            need(text.count(expected) <= 1, 'BODY_DUPLICATE_DELIVERY')
            if expected in text:
                position = text.index(expected); start = len(text[:position].encode('utf-8'))
                observations.append({'message_index':i,'content_index':j,'content_was_string':type(content) is str,
                    'utf8_start':start,'utf8_end':start+len(body),'body_bytes':len(body),'body_sha256':digest(body)})
    need(marker_seen and len(observations) == 1, 'BODY_EXACT_CLIENT_USER_SPAN_UNRECEIVED')
    return {'status':'EXACT_CLIENT_USER_MESSAGE_BODY_OBSERVED','source_file_bytes':len(governor),
            'source_file_sha256':digest(governor),'normalization':'REMOVE_YAML_FRONTMATTER_AND_TRIM_EDGE_LF_ONLY',
            **observations[0]}

def body_native_projection(raw, session_id, cwd, plugin):
    need(type(raw) is bytes and 0 < len(raw) <= 32768, 'BODY_NATIVE_STREAM_BOUND')
    lines = raw.splitlines(); need(1 <= len(lines) <= 128 and all(lines), 'BODY_NATIVE_EVENT_POPULATION')
    events = [body_json(line,32768) for line in lines]
    need(all(type(event) is dict and event.get('type') in ('system','user','assistant','result') and
             event.get('session_id') == session_id and event.get('parent_tool_use_id') is None for event in events),
         'BODY_NATIVE_EVENT_OR_SESSION_SHAPE')
    inits = [(i,x) for i,x in enumerate(events) if x['type'] == 'system']
    results = [(i,x) for i,x in enumerate(events) if x['type'] == 'result']
    need(len(inits) == len(results) == 1 and inits[0][1].get('subtype') == 'init' and
         inits[0][0] < results[0][0] == len(events)-1, 'BODY_NATIVE_INIT_TERMINAL_ORDER')
    init = inits[0][1]; terminal = results[0][1]
    need(init.get('cwd') == str(cwd) and init.get('model') == 'claude-sonnet-4-6', 'BODY_NATIVE_CONFIG_IDENTITY')
    tools = init.get('tools')
    need(type(tools) is list and all(type(x) is str for x in tools) and len(set(tools)) == len(tools) and
         'Skill' in tools and all(x in ('Skill','EndConversation') for x in tools), 'BODY_NATIVE_TOOL_SURFACE')
    need(init.get('mcp_servers') == [] and init.get('mcp_server_errors',[]) == [] and
         init.get('plugin_errors',[]) == [] and init.get('plugins') == [{'name':'implementaudit','path':str(plugin)}],
         'BODY_NATIVE_PLUGIN_OR_MCP_IDENTITY')
    names = init.get('skills')
    need(type(names) is list and len(names) <= 128 and all(type(x) is str and len(x) <= 256 for x in names) and
         len(names) == len(set(names)), 'BODY_NATIVE_SKILLS_SHAPE')
    selected = sorted(x for x in names if x.startswith('implementaudit:'))
    other = sorted(x for x in names if not x.startswith('implementaudit:'))
    unexpected = [x for x in selected if x not in BODY_EXPECTED_NAMES]
    assistants = []
    for event in events:
        if event['type'] not in ('user','assistant'): continue
        message = event.get('message'); need(type(message) is dict, 'BODY_NATIVE_MESSAGE_SHAPE')
        content = message.get('content')
        blocks = [{'type':'text','text':content}] if type(content) is str else content
        need(type(blocks) is list and all(type(x) is dict and x.get('type') == 'text' and
             type(x.get('text')) is str for x in blocks), 'BODY_NATIVE_TOOL_OR_CHILD_BLOCK')
        if event['type'] == 'assistant': assistants.append(''.join(x['text'] for x in blocks))
    need(assistants == [BODY_ACK] and terminal.get('subtype') == 'success' and terminal.get('is_error') is False and
         terminal.get('result') == BODY_ACK and terminal.get('permission_denials',[]) == [], 'BODY_NATIVE_TERMINAL')
    return {'status':'NATIVE_INIT_AND_TERMINAL_RECEIVED','event_count':len(events),
        'session_id_sha256':digest(session_id.encode('ascii')),'plugin_path_matches_effective':True,
        'canonical_advertised_entries_exact':selected == sorted(BODY_EXPECTED_NAMES),
        'expected_names_observed':[x for x in BODY_EXPECTED_NAMES if x in selected],
        'unexpected_package_entry_count':len(unexpected),'unexpected_package_names_sha256':digest(body_canonical(unexpected)),
        'other_skill_count':len(other),'other_skill_names_sha256':digest(body_canonical(other)),
        'native_tool_calls':0,'child_events':0,'terminal_success':True,
        'runtime_version_label_matches':init.get('claude_code_version') == '2.1.318'}


# Inert author fragment. The composed parent owns these definitions; this file
# has no entrypoint and is never imported by the hosted operation.
BODY_DIAGNOSTIC_PATHS = (
    ('HOME_DOT_CLAUDE', 'home', '.claude'),
    ('HOME_DOT_CLAUDE_JSON', 'home', '.claude.json'),
    ('HOME_CONFIG_ANTHROPIC', 'home', '.config/anthropic'),
    ('HOME_CONFIG_CLAUDE', 'home', '.config/claude'),
    ('XDG_CONFIG_ANTHROPIC', 'xdg_config', 'anthropic'),
    ('XDG_CONFIG_CLAUDE', 'xdg_config', 'claude'),
    ('CONFIG_SETTINGS', 'config', 'settings.json'),
    ('CONFIG_SETTINGS_LOCAL', 'config', 'settings.local.json'),
    ('CONFIG_DOT_CREDENTIALS', 'config', '.credentials.json'),
    ('CONFIG_CREDENTIALS', 'config', 'credentials.json'),
    ('CONFIG_MANAGED_SETTINGS', 'config', 'managed-settings.json'),
    ('CONFIG_MANAGED_MCP', 'config', 'managed-mcp.json'),
    ('CONFIG_PLUGINS', 'config', 'plugins'),
    ('CONFIG_SKILLS', 'config', 'skills'),
    ('CONFIG_HOOKS', 'config', 'hooks'),
    ('CONFIG_MCP', 'config', 'mcp.json'),
    ('CONFIG_DOT_MCP', 'config', '.mcp.json'),
)


def body_diagnostic_kind(mode):
    for predicate, label in ((stat.S_ISDIR, 'DIRECTORY'), (stat.S_ISREG, 'REGULAR'),
                             (stat.S_ISLNK, 'SYMLINK')):
        if predicate(mode): return label
    return 'OTHER'


def body_diagnostic_errno(exc):
    for number, label in ((errno.EACCES, 'EACCES'), (errno.EPERM, 'EPERM'),
                          (errno.EIO, 'EIO'), (errno.ENOTDIR, 'ENOTDIR'),
                          (errno.ELOOP, 'ELOOP')):
        if exc.errno == number: return label
    return 'OTHER'


def body_diagnostic_anchor(path):
    info = path.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and
         stat.S_IMODE(info.st_mode) == 0o700, 'BODY_DIAGNOSTIC_ANCHOR_IDENTITY')
    need(path.resolve(strict=True) == path, 'BODY_DIAGNOSTIC_ANCHOR_IDENTITY')


def body_diagnostic_file(path, maximum, mode=None):
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid() and info.st_nlink == 1 and
         not info.st_mode & 0o022 and 0 <= info.st_size <= maximum and
         (mode is None or stat.S_IMODE(info.st_mode) == mode), 'BODY_DIAGNOSTIC_CARRIER_IDENTITY')
    return body_owned_file(path, maximum)


def body_diagnostic_startup(context):
    """Only the fixed context-relative entries; no contents or directory census."""
    rows = []
    for identifier, anchor, relative in BODY_DIAGNOSTIC_PATHS:
        chain = [context]
        for part in (anchor, *relative.split('/')): chain.append(chain[-1]/part)
        row = {'id':identifier, 'present':None, 'kind':'UNREADABLE', 'error_code':None}
        for index, path in enumerate(chain):
            try:
                info = path.lstat()
            except OSError as exc:
                if exc.errno == errno.ENOENT: row.update(present=False, kind='ABSENT')
                else: row['error_code'] = body_diagnostic_errno(exc)
                break
            if index != len(chain)-1:
                if not stat.S_ISDIR(info.st_mode):
                    row['kind'] = 'ANCESTOR_BLOCKED'; break
            else:
                row.update(present=True, kind=body_diagnostic_kind(info.st_mode))
        rows.append(row)
    return {'schema':'dg17.claude.body-startup-paths.v1', 'phase':'NATIVE_STARTUP_AFTER',
            'path_count':17, 'rows':rows}


def body_diagnostic_directory(root, relative):
    """Contain the private spelling before reading metadata; never follow links."""
    need(type(relative) is str and '\x00' not in relative, 'BODY_DIAGNOSTIC_DIRECTORY_PATH')
    try: raw = relative.encode('utf-8', 'strict')
    except UnicodeError: raise Refusal('BODY_DIAGNOSTIC_DIRECTORY_PATH') from None
    parts = relative.split('/')
    need(0 < len(raw) <= 4096 and len(parts) <= 16 and
         all(part not in ('', '.', '..') for part in parts), 'BODY_DIAGNOSTIC_DIRECTORY_PATH')
    body_diagnostic_anchor(root)
    parent = root
    for part in parts[:-1]:
        parent = parent/part; info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and
             not info.st_mode & 0o022 and parent.resolve(strict=True) == parent,
             'BODY_DIAGNOSTIC_DIRECTORY_ANCESTOR')
    path = parent/parts[-1]
    info = None; error = None; physical = None; kind = 'UNREADABLE'
    try:
        info = path.lstat(); kind = body_diagnostic_kind(info.st_mode)
    except OSError as exc:
        if exc.errno == errno.ENOENT: kind = 'ABSENT'
        else: error = body_diagnostic_errno(exc)
    if info is not None:
        # The original observer is reached only after a directory lstat. A
        # later symlink cannot be resolved as diagnostic receiving authority.
        need(not stat.S_ISLNK(info.st_mode), 'BODY_DIAGNOSTIC_DIRECTORY_LINK_UNRECEIVED')
        try: physical = path.resolve(strict=True) == path
        except OSError as exc: error = body_diagnostic_errno(exc)
    return {'status':'PUBLIC_SAFE_FIRST_DIRECTORY_REFUSAL_ONLY', 'phase':'PRIVATE_SEAL',
            'relative_path_bytes':len(raw), 'relative_path_sha256':digest(raw), 'kind':kind,
            'mode':stat.S_IMODE(info.st_mode) if info is not None else None,
            'uid_matches_effective':info.st_uid == os.geteuid() if info is not None else None,
            'gid_matches_effective':info.st_gid == os.getegid() if info is not None else None,
            'owner_only_mode':not bool(info.st_mode & 0o077) if info is not None else None,
            'physical_path':physical, 'error_code':error}


def body_diagnostic_quiescence():
    # Read-only waitid does not consume an unreceived child status. Positive
    # ECHILD is required; a live, zombie, unknown, or unsupported case refuses.
    try:
        os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT | 0x40000000)
    except ChildProcessError:
        return True
    raise Refusal('BODY_DIAGNOSTIC_PARENT_QUIESCENCE')


def body_diagnostic_capture_shape(row):
    # This is host_utility's 15-field outer capture. The child-only private
    # retention fields are deliberately not synthesized as observed evidence.
    keys = {'name', 'process_started', 'returncode', 'timeout', 'output_bound_exceeded',
            'pidfd_acquired', 'internal_failure', 'reason_code', 'stream_digest_scope',
            'streams_complete', 'stdout_bytes', 'stderr_bytes', 'stdout_sha256',
            'stderr_sha256', 'cleanup'}
    if type(row) is not dict or set(row) != keys or row['name'] != 'loopback-claude-canonical-body': return False
    if not all(type(row[key]) is bool for key in ('process_started', 'timeout',
               'output_bound_exceeded', 'pidfd_acquired', 'streams_complete')): return False
    if type(row['returncode']) is not int or row['internal_failure'] is not None: return False
    if type(row['reason_code']) is not str or not 1 <= len(row['reason_code']) <= 96 or row['stream_digest_scope'] != 'CAPTURED_BYTES_ONLY': return False
    for stream in ('stdout', 'stderr'):
        if type(row[stream+'_bytes']) is not int or not 0 <= row[stream+'_bytes'] <= 32768: return False
        if type(row[stream+'_sha256']) is not str or re.fullmatch('[0-9a-f]{64}', row[stream+'_sha256']) is None: return False
    cleanup = row['cleanup']
    if type(cleanup) is not dict or set(cleanup) != {'echild', 'pidfd_signals', 'retained_status_count',
            'retained_statuses_sha256', 'reaped_statuses', 'reaped_statuses_truncated'}: return False
    if type(cleanup['echild']) is not bool or type(cleanup['reaped_statuses_truncated']) is not bool: return False
    if any(type(cleanup[key]) is not int or cleanup[key] < 0 for key in ('pidfd_signals', 'retained_status_count')): return False
    if type(cleanup['retained_statuses_sha256']) is not str or re.fullmatch('[0-9a-f]{64}', cleanup['retained_statuses_sha256']) is None: return False
    statuses = cleanup['reaped_statuses']; count = cleanup['retained_status_count']
    if type(statuses) is not list or len(statuses) != min(count, 8) or cleanup['reaped_statuses_truncated'] is not (count > 8): return False
    if any(type(item) is not dict or set(item) != {'pid', 'returncode'} or type(item['pid']) is not int or
           item['pid'] <= 0 or type(item['returncode']) is not int for item in statuses): return False
    return True


def receive_body_diagnostics(state, output, phase):
    """Separate data-only receiving; no body success or late executable gate."""
    need(phase in ('AFTER_COMMAND', 'PRIVATE_SUCCESS', 'FINAL'), 'BODY_DIAGNOSTIC_PHASE')
    validation = state.setdefault('claude_validation', {})
    previous = validation.get('diagnostic_receiving', {})
    phases = {key:previous.get('verified_phases', {}).get(key) is True
              for key in ('AFTER_COMMAND', 'PRIVATE_SUCCESS', 'FINAL')}
    result = {'schema':'dg17.claude.body-parent-diagnostics.v1', 'status':'UNRECEIVED',
              'reason':None, 'latest_phase':phase, 'verified_phases':phases,
              'carrier_sha256':None, 'carrier_bytes':None, 'carrier_identity_verified':False,
              'public_projection_bound':False, 'fresh_parent_echild':False,
              'startup_paths_available':False, 'startup_paths_received':False, 'startup_path_count':0,
              'directory_facts_available':False, 'directory_facts_received':False,
              'metadata_recomputed':False, 'matches_initial_readback':False,
              'metadata_snapshot_sha256':None, 'body_acceptance_from_diagnostics':False}
    validation['diagnostic_receiving'] = result
    try:
        need(validation.get('valid') is True and validation.get('captured_result_matches') is True and
             state.get('active_command') is None, 'BODY_DIAGNOSTIC_PUBLIC_UNBOUND')
        public = state.get('claude')
        need(type(public) is dict, 'BODY_DIAGNOSTIC_PUBLIC_UNBOUND')
        expected = public.get('diagnostic_record_sha256')
        if expected is None:
            result['reason'] = 'CARRIER_DIGEST_UNAVAILABLE'; return result
        need(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected),
             'BODY_DIAGNOSTIC_PUBLIC_UNBOUND')
        result['carrier_sha256'] = expected
        captures = [(i+1,row) for i,row in enumerate(state.get('commands', []))
                    if type(row) is dict and row.get('name') == 'loopback-claude-canonical-body']
        need(len(captures) == 1, 'BODY_DIAGNOSTIC_PARENT_CAPTURE')
        ordinal, capture = captures[0]
        need(body_diagnostic_capture_shape(capture) and
             capture['process_started'] is True and capture['streams_complete'] is True and
             capture['pidfd_acquired'] is True and capture['timeout'] is False and
             capture['output_bound_exceeded'] is False and capture['internal_failure'] is None and
             capture['cleanup']['echild'] is True, 'BODY_DIAGNOSTIC_PARENT_CAPTURE')
        body_diagnostic_quiescence(); result['fresh_parent_echild'] = True
        body_diagnostic_anchor(output); body_diagnostic_anchor(output/'private')
        public_path = output/'private/CLAUDE_BODY_RESULT.json'
        captured_path = output/'private'/f'{ordinal:03d}-loopback-claude-canonical-body.stdout'
        public_pin = body_diagnostic_file(public_path, 32768, 0o600)
        captured_pin = body_diagnostic_file(captured_path, 32768)
        public_raw = read(public_path, 32768); captured = read(captured_path, 32768)
        need(public_raw == captured and digest(public_raw) == validation['result_sha256'] and
             public_pin == captured_pin == {'bytes':len(public_raw), 'sha256':digest(public_raw)} and
             digest(captured) == capture['stdout_sha256'] and len(captured) == capture['stdout_bytes'] and
             body_canonical(body_json(public_raw, 32768)) == body_canonical(public),
             'BODY_DIAGNOSTIC_PUBLIC_UNBOUND')
        carrier = output/'private/CLAUDE_BODY_DIAGNOSTICS.json'
        def identity(info):
            return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                    info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        first_identity = identity(carrier.lstat())
        pin = body_diagnostic_file(carrier, 16384, 0o600); raw = read(carrier, 16384)
        need(pin == {'bytes':len(raw), 'sha256':digest(raw)} and digest(raw) == expected,
             'BODY_DIAGNOSTIC_CARRIER_PIN')
        record = body_json(raw, 16384)
        need(type(record) is dict and set(record) == {'schema', 'startup_paths_after', 'directory_refusal'} and
             record['schema'] == 'dg17.claude.body-diagnostics.v1' and body_canonical(record) == raw,
             'BODY_DIAGNOSTIC_CARRIER_SHAPE')
        result.update(carrier_bytes=len(raw), carrier_identity_verified=True)
        startup = record['startup_paths_after']; rejected = record['directory_refusal']
        need(body_canonical(startup) == body_canonical(public['startup_paths_after']),
             'BODY_DIAGNOSTIC_PROJECTION_DIFFERS')
        if rejected is None:
            need(public['private_directory_refusal'] is None, 'BODY_DIAGNOSTIC_PROJECTION_DIFFERS')
        else:
            need(type(rejected) is dict and set(rejected) == {'relative_path', 'facts'} and
                 body_canonical(rejected['facts']) == body_canonical(public['private_directory_refusal']),
                 'BODY_DIAGNOSTIC_PROJECTION_DIFFERS')
            failures = [public['failure'], *public['supplemental_failures']]
            need({'phase':'PRIVATE_SEAL', 'code':'PRIVATE_DIRECTORY_REFUSED'} in failures,
                 'BODY_DIAGNOSTIC_DIRECTORY_FAILURE_BINDING')
        result['public_projection_bound'] = True
        root = output/'private/claude-canonical-body'
        observed_startup = None; observed_directory = None
        if startup is not None or rejected is not None: body_diagnostic_anchor(root)
        if startup is not None:
            result['startup_paths_available'] = True
            observed_startup = body_diagnostic_startup(root/'context-canonical-body')
            need(body_canonical(observed_startup) == body_canonical(startup),
                 'BODY_DIAGNOSTIC_STARTUP_METADATA_DIFFERS')
            result.update(startup_paths_received=True, startup_path_count=17)
        if rejected is not None:
            result['directory_facts_available'] = True
            observed_directory = body_diagnostic_directory(root, rejected['relative_path'])
            need(body_canonical(observed_directory) == body_canonical(rejected['facts']),
                 'BODY_DIAGNOSTIC_DIRECTORY_METADATA_DIFFERS')
            result['directory_facts_received'] = True
        # Repeat the whole finite metadata observation, not just the child
        # carrier, before claiming a stable parent readback.
        if startup is not None:
            need(body_diagnostic_startup(root/'context-canonical-body') == observed_startup,
                 'BODY_DIAGNOSTIC_STARTUP_METADATA_DIFFERS')
        if rejected is not None:
            need(body_diagnostic_directory(root, rejected['relative_path']) == observed_directory,
                 'BODY_DIAGNOSTIC_DIRECTORY_METADATA_DIFFERS')
        need(identity(carrier.lstat()) == first_identity and body_diagnostic_file(carrier, 16384, 0o600) == pin and
             read(carrier, 16384) == raw, 'BODY_DIAGNOSTIC_CARRIER_CHANGED')
        need(body_diagnostic_file(public_path, 32768, 0o600) == public_pin and
             body_diagnostic_file(captured_path, 32768) == captured_pin,
             'BODY_DIAGNOSTIC_PUBLIC_UNBOUND')
        body_diagnostic_quiescence()
        snapshot = {'carrier_identity':first_identity, 'carrier_sha256':expected,
                    'startup':observed_startup, 'directory':observed_directory}
        snapshot_sha = digest(body_canonical(snapshot))
        if 'body_diagnostic_baseline_sha256' not in state:
            state['body_diagnostic_baseline_sha256'] = snapshot_sha
        need(state['body_diagnostic_baseline_sha256'] == snapshot_sha,
             'BODY_DIAGNOSTIC_CHANGED_SINCE_FIRST_READBACK')
        result.update(status='RECEIVED_AVAILABLE_METADATA' if startup is not None or rejected is not None
                      else 'RECEIVED_CARRIER_WITHOUT_OBSERVATIONS', metadata_recomputed=True,
                      matches_initial_readback=True, metadata_snapshot_sha256=snapshot_sha)
        phases[phase] = True
    except BaseException as exc:
        # Only fixed labels are public. Unknown exception text may contain a
        # private path and is neither copied nor used as an acceptance result.
        fixed = {'BODY_DIAGNOSTIC_PUBLIC_UNBOUND', 'BODY_DIAGNOSTIC_PARENT_CAPTURE',
                 'BODY_DIAGNOSTIC_PARENT_QUIESCENCE', 'BODY_DIAGNOSTIC_CARRIER_IDENTITY',
                 'BODY_DIAGNOSTIC_ANCHOR_IDENTITY',
                 'BODY_DIAGNOSTIC_CARRIER_PIN', 'BODY_DIAGNOSTIC_CARRIER_SHAPE',
                 'BODY_DIAGNOSTIC_PROJECTION_DIFFERS', 'BODY_DIAGNOSTIC_DIRECTORY_FAILURE_BINDING',
                 'BODY_DIAGNOSTIC_STARTUP_METADATA_DIFFERS', 'BODY_DIAGNOSTIC_DIRECTORY_METADATA_DIFFERS',
                 'BODY_DIAGNOSTIC_DIRECTORY_PATH', 'BODY_DIAGNOSTIC_DIRECTORY_ANCESTOR',
                 'BODY_DIAGNOSTIC_DIRECTORY_LINK_UNRECEIVED', 'BODY_DIAGNOSTIC_CARRIER_CHANGED',
                 'BODY_DIAGNOSTIC_CHANGED_SINCE_FIRST_READBACK'}
        result['reason'] = str(exc) if isinstance(exc, Refusal) and str(exc) in fixed else 'METADATA_UNAVAILABLE'
    return result


def body_diagnostics_success(state):
    value = state.get('claude_validation', {}).get('diagnostic_receiving', {})
    return (value.get('status') == 'RECEIVED_AVAILABLE_METADATA' and value.get('reason') is None and
            all(value.get(key) is True for key in ('carrier_identity_verified', 'public_projection_bound',
                'fresh_parent_echild', 'startup_paths_available', 'startup_paths_received',
                'metadata_recomputed', 'matches_initial_readback')) and
            value.get('startup_path_count') == 17 and value.get('directory_facts_available') is False and
            value.get('directory_facts_received') is False and
            value.get('verified_phases', {}).get('AFTER_COMMAND') is True)


# Root-owned independent derivation from immutable body04 input contract.
# This file is authored as data. Its filesystem owners are not executed locally.

def body_plugins_identity(info):
    return {key:getattr(info, attr) for key,attr in (
        ('device','st_dev'),('inode','st_ino'),('uid','st_uid'),('gid','st_gid'),
        ('mode','st_mode'),('nlink','st_nlink'),('size','st_size'),
        ('mtime_ns','st_mtime_ns'),('ctime_ns','st_ctime_ns'))}


def body_plugins_kind(mode):
    if stat.S_ISDIR(mode): return 'DIRECTORY'
    if stat.S_ISREG(mode): return 'REGULAR'
    if stat.S_ISLNK(mode): return 'SYMLINK'
    return 'OTHER'


def body_plugins_relative(value):
    need(type(value) is str and value != '' and not value.startswith('/'), 'BODY_PLUGINS_PATH')
    parts = value.split('/')
    need(len(parts) <= 8 and all(part not in ('','.','..') for part in parts), 'BODY_PLUGINS_PATH')
    try: encoded_path = value.encode('utf-8', errors='strict')
    except UnicodeError: raise Refusal('BODY_PLUGINS_PATH') from None
    need(1 <= len(encoded_path) <= 256 and '\x00' not in value, 'BODY_PLUGINS_PATH')
    return encoded_path


def body_plugins_record_shape(value):
    need(type(value) is dict and set(value) == {'schema','path_id','status','root',
        'entries','error_code','complete','stable'}, 'BODY_PLUGINS_RECORD')
    need(value['schema'] == 'dg17.claude.config-plugins-snapshot.v1' and
        value['path_id'] == 'CONFIG_PLUGINS', 'BODY_PLUGINS_RECORD')
    need(value['status'] in ('COMPLETE_ABSENT','COMPLETE_PRESENT','UNREADABLE',
        'ANCESTOR_BLOCKED','BOUND_EXCEEDED','CHANGED') and
        value['error_code'] in (None,'EACCES','EPERM','EIO','ENOTDIR','ELOOP','OTHER') and
        type(value['complete']) is bool and type(value['stable']) is bool,
        'BODY_PLUGINS_RECORD')
    def identity(row):
        fields = {'device','inode','uid','gid','mode','nlink','size','mtime_ns','ctime_ns'}
        need(type(row) is dict and set(row) == fields, 'BODY_PLUGINS_RECORD')
        for key, number in row.items():
            low, high = (-9223372036854775808,9223372036854775807) if key.endswith('_ns') else (0,18446744073709551615)
            need(type(number) is int and low <= number <= high, 'BODY_PLUGINS_RECORD')
    root = value['root']
    if root is not None:
        need(type(root) is dict and set(root) == {'kind','identity','physical_path'} and
            type(root['physical_path']) is bool, 'BODY_PLUGINS_RECORD')
        identity(root['identity'])
        need(root['kind'] == body_plugins_kind(root['identity']['mode']) and
            not (root['kind'] == 'SYMLINK' and root['physical_path']), 'BODY_PLUGINS_RECORD')
    rows = value['entries']
    need(type(rows) is list and len(rows) <= 16, 'BODY_PLUGINS_RECORD')
    paths = []
    for row in rows:
        need(type(row) is dict and set(row) == {'relative_path','kind','identity'}, 'BODY_PLUGINS_RECORD')
        body_plugins_relative(row['relative_path']); paths.append(row['relative_path'])
        identity(row['identity'])
        need(row['kind'] == body_plugins_kind(row['identity']['mode']), 'BODY_PLUGINS_RECORD')
    need(paths == sorted(paths) and len(paths) == len(set(paths)), 'BODY_PLUGINS_RECORD')
    if value['complete']:
        need(value['status'] in ('COMPLETE_ABSENT','COMPLETE_PRESENT') and value['error_code'] is None,
            'BODY_PLUGINS_RECORD')
        if value['status'] == 'COMPLETE_ABSENT':
            need(root is None and rows == [], 'BODY_PLUGINS_RECORD')
        else:
            need(root is not None and (root['kind'] == 'DIRECTORY' or rows == []), 'BODY_PLUGINS_RECORD')
    else:
        need(value['status'] not in ('COMPLETE_ABSENT','COMPLETE_PRESENT') and value['stable'] is False,
            'BODY_PLUGINS_RECORD')
    need(not value['stable'] or value['complete'], 'BODY_PLUGINS_RECORD')
    need(len(body_canonical(value)) <= 65536, 'BODY_PLUGINS_RECORD_BOUND')
    return value


def body_plugins_admission_facts(records, captures, streams, provider, public, receipt):
    """Pure join; caller separately owns exact file hashes, identities and quiescence."""
    prefix = ['currentness-before','canonical-body']
    need(type(records) is list and all(type(row) is dict for row in records) and
        [row.get('name') for row in records] in (prefix,prefix+['currentness-after']),
        'BODY_PLUGINS_OUTPUT_COMMANDS')
    need(type(captures) is dict and set(captures) == set(prefix) and type(streams) is dict and
        set(streams) == {name+'.'+kind for name in prefix for kind in ('stdout','stderr')},
        'BODY_PLUGINS_OUTPUT_CAPTURE')
    flags = ('source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')
    native_ok = True; product = None
    for name,row in zip(prefix,records[:2]):
        values = captures[name]
        need(type(values) is list and len(values) == 1 and claude_capture_base_shape(values[0],name),
            'BODY_PLUGINS_OUTPUT_CAPTURE')
        base = values[0]
        extra = {'recognition_status','recognition_code',*flags} if name == 'canonical-body' else set()
        need(set(row) == set(base)|extra and claude_capture_base_shape({key:row[key] for key in base},name) and
            all(type(row[key]) is type(value) and row[key] == value
            for key,value in base.items()), 'BODY_PLUGINS_OUTPUT_CAPTURE')
        for kind in ('stdout','stderr'):
            raw = streams[name+'.'+kind]
            need(type(raw) is bytes and len(raw) <= 32768 and len(raw) == base[kind+'_bytes'] and
                digest(raw) == base[kind+'_sha256'], 'BODY_PLUGINS_OUTPUT_STREAM')
        if name == 'currentness-before':
            need(streams[name+'.stdout'] == (receipt+'\n').encode() and streams[name+'.stderr'] == b'',
                'BODY_PLUGINS_OUTPUT_RECEIPT')
        native_ok = native_ok and (base['process_started'] is True and base['returncode'] == 0 and
            base['streams_complete'] is True and base['pidfd_acquired'] is True and
            base['timeout'] is False and base['output_bound_exceeded'] is False and
            base['internal_failure'] is None and base['private_streams_retained'] is True and
            base['retention_failure'] is False and base['cleanup']['echild'] is True)
        if extra:
            need(all(type(row[key]) is bool for key in flags) and type(row['recognition_status']) is str and
                (row['recognition_code'] is None or type(row['recognition_code']) is str),
                'BODY_PLUGINS_OUTPUT_CAPTURE')
            product = {key:row[key] for key in ('name','returncode','stdout_bytes','stdout_sha256',
                'stderr_bytes','stderr_sha256','recognition_status','recognition_code')}
            for key in ('process_started','streams_complete','timeout','output_bound_exceeded','pidfd_acquired',
                'private_streams_retained','retention_failure',*flags): product[key] = row[key] is True
            product.update(internal_failure=row['internal_failure'] is not None,
                stderr_present=row['stderr_bytes'] > 0,owned_cleanup_echild=row['cleanup']['echild'] is True,
                owned_reaped_status_count=row['cleanup']['retained_status_count'],
                owned_statuses_sha256=row['cleanup']['retained_statuses_sha256'])
    need(public.get('commands') == [product], 'BODY_PLUGINS_OUTPUT_PUBLIC_CAPTURE')
    need(type(provider) is dict and set(provider) == {'schema','custody','requests',
        'request_capture_scope','response_capture_scope'} and
        provider['schema'] == 'dg17.claude.local-provider-record.v1' and
        provider['request_capture_scope'] == 'CAPTURED_HTTP_BYTES_ONLY' and
        provider['response_capture_scope'] == 'PREPARED_BYTES_AND_SOCKET_SEND_RETURNED_COUNT' and
        type(provider['requests']) is list and len(provider['requests']) <= 16,
        'BODY_PLUGINS_OUTPUT_PROVIDER')
    provider_keys = {'started','thread_joined','all_owned_sockets_closed','verified','request_count',
        'semantic_request_count','captured_request_bytes','semantic_response_complete',
        'failure','supplemental_failures','semantic_request_index'}
    custody = provider['custody']
    need(type(custody) is dict and set(custody) == provider_keys and
        body_canonical(custody) == body_canonical(public.get('provider_custody')),
        'BODY_PLUGINS_OUTPUT_PROVIDER')
    provider_ok = (all(custody[key] is True for key in ('verified','all_owned_sockets_closed','thread_joined')) and
        custody['failure'] is None and custody['supplemental_failures'] == [])
    quiescence = public['config_plugins_profile'].get('admission_quiescence')
    q_received = (type(quiescence) is dict and set(quiescence) ==
        {'no_owned_children_listed','wait_echild','verified'} and all(type(v) is bool for v in quiescence.values()))
    return {'native_capture_bound':True,'provider_custody_bound':True,
        'producer_quiescence_received':q_received,
        'verified':bool(native_ok and provider_ok and body_plugins_quiescence_valid(quiescence))}

def body_plugins_admission_receiving(root, public, receipt):
    """Read fixed evidence only; opaque output members are not interpreted here."""
    result = {'status':'UNRECEIVED','reason':None,'native_capture_bound':False,
        'provider_custody_bound':False,'producer_quiescence_received':False,
        'verified':False,'evidence_sha256':None}
    try:
        body_diagnostic_anchor(root)
        population = {}
        def receive_file(name, maximum):
            path = root/name; before = body_plugins_identity(path.lstat())
            need(before['gid'] == os.getegid(), 'BODY_PLUGINS_OUTPUT_FILE')
            pin = body_diagnostic_file(path,maximum,0o600); raw = read(path,maximum)
            need(pin == {'bytes':len(raw),'sha256':digest(raw)} and
                before == body_plugins_identity(path.lstat()), 'BODY_PLUGINS_OUTPUT_FILE')
            population[name] = {'identity':before,'bytes':len(raw),'sha256':digest(raw)}
            return raw
        records = body_json(receive_file('COMMANDS.json',262144),262144)
        captures = {}; streams = {}
        for name in ('currentness-before','canonical-body'):
            captures[name] = body_json(receive_file(name+'.capture.json',65536),65536)
            for kind in ('stdout','stderr'):
                streams[name+'.'+kind] = receive_file(name+'.'+kind,32768)
        raw = receive_file('PROVIDER_RECORD.json',262144)
        need(type(public.get('provider_record_sha256')) is str and
            digest(raw) == public['provider_record_sha256'], 'BODY_PLUGINS_OUTPUT_PROVIDER_PIN')
        provider = body_json(raw,262144)
        facts = body_plugins_admission_facts(records,captures,streams,provider,public,receipt)
        for name,row in population.items():
            path = root/name
            need(body_plugins_identity(path.lstat()) == row['identity'] and
                body_diagnostic_file(path,row['bytes'],0o600) == {'bytes':row['bytes'],'sha256':row['sha256']} and
                digest(read(path,row['bytes'])) == row['sha256'], 'BODY_PLUGINS_OUTPUT_FILE_CHANGED')
        result.update(facts)
        result.update(status='RECEIVED',evidence_sha256=digest(body_canonical(population)))
    except BaseException as exc:
        fixed = {'BODY_PLUGINS_OUTPUT_COMMANDS','BODY_PLUGINS_OUTPUT_CAPTURE','BODY_PLUGINS_OUTPUT_STREAM',
            'BODY_PLUGINS_OUTPUT_RECEIPT','BODY_PLUGINS_OUTPUT_PUBLIC_CAPTURE','BODY_PLUGINS_OUTPUT_PROVIDER',
            'BODY_PLUGINS_OUTPUT_FILE','BODY_PLUGINS_OUTPUT_PROVIDER_PIN','BODY_PLUGINS_OUTPUT_FILE_CHANGED'}
        result['reason'] = str(exc) if isinstance(exc,Refusal) and str(exc) in fixed else 'OUTPUT_EVIDENCE_UNAVAILABLE'
    return result

def body_plugins_quiescence_valid(value):
    return (type(value) is dict and set(value) == {'no_owned_children_listed','wait_echild','verified'} and
        all(value[key] is True for key in ('no_owned_children_listed','wait_echild','verified')))


def body_plugins_projection(snapshot, uid, gid, custody):
    body_plugins_record_shape(snapshot)
    root = snapshot['root']; ident = None if root is None else root['identity']
    complete = snapshot['complete']; stable = snapshot['stable']
    absent = complete and stable and snapshot['status'] == 'COMPLETE_ABSENT'
    directory = complete and stable and root is not None and root['kind'] == 'DIRECTORY'
    empty = (len(snapshot['entries']) == 0) if absent or directory else None
    physical = absent
    if directory and root['physical_path'] is True:
        physical = (stat.S_IMODE(ident['mode']) == 0o700 and ident['uid'] == uid and ident['gid'] == gid)
        seen = {(ident['device'],ident['inode'])}; total = 0
        for member in snapshot['entries']:
            data = member['identity']; pair = (data['device'],data['inode'])
            eligible = (data['uid'] == uid and data['gid'] == gid and pair not in seen)
            seen.add(pair)
            if member['kind'] == 'DIRECTORY':
                eligible = eligible and stat.S_IMODE(data['mode']) == 0o700
            elif member['kind'] == 'REGULAR':
                eligible = (eligible and stat.S_IMODE(data['mode']) == 0o600 and
                    data['nlink'] == 1 and data['size'] <= 8388608)
                total += data['size']
            else:
                eligible = False
            physical = physical and eligible
        physical = physical and total <= 33554432
    rows = []
    for row in snapshot['entries']:
        raw = body_plugins_relative(row['relative_path']); data = row['identity']
        rows.append({'relative_path_bytes':len(raw),'relative_path_sha256':digest(raw),
            'kind':row['kind'],'mode':stat.S_IMODE(data['mode']),
            'uid_matches_effective':data['uid'] == uid,'gid_matches_effective':data['gid'] == gid,
            'regular_file_bytes':data['size'] if row['kind'] == 'REGULAR' else None})
    return {'schema':'dg17.claude.config-plugins-observation.v2','path_id':'CONFIG_PLUGINS',
        'status':snapshot['status'],'kind':None if root is None else root['kind'],
        'mode':None if ident is None else stat.S_IMODE(ident['mode']),
        'uid_matches_effective':None if ident is None else ident['uid'] == uid,
        'gid_matches_effective':None if ident is None else ident['gid'] == gid,
        'physical_path':None if root is None else root['physical_path'],
        'complete':complete,'stable':stable,'entry_count':len(rows),'entries':rows,
        'error_code':snapshot['error_code'],'population_sha256':digest(body_canonical(snapshot)),
        'empty':empty,'profile_admitted':bool(physical and custody is True)}


def body_plugins_census(context, uid, gid):
    """Fixed-path metadata only; held directory descriptors, no contents/links."""
    class Halt(Exception):
        def __init__(self, status, error=None): self.status,self.error = status,error
    def once():
        record = {'schema':'dg17.claude.config-plugins-snapshot.v1','path_id':'CONFIG_PLUGINS',
            'status':'UNREADABLE','root':None,'entries':[],'error_code':None,
            'complete':False,'stable':False}
        handles = []; fixed_anchors = []; context_fd = None; config_fd = None
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        def opened(path, parent=None):
            fd = os.open(path, flags, **({} if parent is None else {'dir_fd':parent}))
            handles.append(fd); return fd
        def directory(fd, expected=False):
            data = body_plugins_identity(os.fstat(fd))
            if not stat.S_ISDIR(data['mode']): raise Halt('ANCESTOR_BLOCKED')
            if expected and (data['uid'] != uid or data['gid'] != gid or stat.S_IMODE(data['mode']) != 0o700):
                raise Halt('ANCESTOR_BLOCKED')
            return data
        def scan(fd, prefix):
            before = directory(fd)
            if before['uid'] != uid or before['gid'] != gid: raise Halt('ANCESTOR_BLOCKED')
            names = []
            with os.scandir(fd) as iterator:
                for entry in iterator:
                    name = entry.name
                    if type(name) is not str or name in ('','.','..') or '/' in name: raise Halt('BOUND_EXCEEDED')
                    relative = name if not prefix else prefix+'/'+name
                    try: body_plugins_relative(relative)
                    except Refusal: raise Halt('BOUND_EXCEEDED') from None
                    names.append(name)
                    if len(names) + len(record['entries']) > 16: raise Halt('BOUND_EXCEEDED')
            if len(names) != len(set(names)): raise Halt('CHANGED')
            for name in sorted(names):
                relative = name if not prefix else prefix+'/'+name
                if len(record['entries']) >= 16: raise Halt('BOUND_EXCEEDED')
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                meta = body_plugins_identity(info); kind = body_plugins_kind(meta['mode'])
                record['entries'].append({'relative_path':relative,'kind':kind,'identity':meta})
                if kind == 'DIRECTORY':
                    if meta['uid'] != uid or meta['gid'] != gid: raise Halt('ANCESTOR_BLOCKED')
                    nested = opened(name, fd)
                    if body_plugins_identity(os.fstat(nested)) != meta: raise Halt('CHANGED')
                    scan(nested, relative)
                    if body_plugins_identity(os.stat(name, dir_fd=fd, follow_symlinks=False)) != meta:
                        raise Halt('CHANGED')
                elif body_plugins_identity(os.stat(name, dir_fd=fd, follow_symlinks=False)) != meta:
                    raise Halt('CHANGED')
            if directory(fd) != before: raise Halt('CHANGED')
        try:
            # Walk the absolute ancestry through no-follow descriptors; earlier
            # system ancestors may have their normal root ownership/modes.
            need(context.is_absolute() and all(p not in ('.','..') for p in context.parts), 'BODY_PLUGINS_CONTEXT')
            current = opened(context.anchor)
            for index,component in enumerate(context.parts[1:]):
                parent = current
                named = body_plugins_identity(os.stat(component,dir_fd=parent,follow_symlinks=False))
                current = opened(component,parent)
                if body_plugins_identity(os.fstat(current)) != named: raise Halt('CHANGED')
                if index == len(context.parts)-2: fixed_anchors.append((parent,component,named))
            context_fd = current; context_before = directory(context_fd, True)
            config_named = body_plugins_identity(os.stat('config',dir_fd=context_fd,follow_symlinks=False))
            config_fd = opened('config', context_fd); config_before = directory(config_fd, True)
            if config_named != config_before: raise Halt('CHANGED')
            fixed_anchors.append((context_fd,'config',config_named))
            try: info = os.stat('plugins', dir_fd=config_fd, follow_symlinks=False)
            except FileNotFoundError:
                record['status'] = 'COMPLETE_ABSENT'; record['complete'] = True
            else:
                meta = body_plugins_identity(info); kind = body_plugins_kind(meta['mode'])
                record['root'] = {'kind':kind,'identity':meta,'physical_path':kind != 'SYMLINK'}
                if kind == 'DIRECTORY':
                    if meta['uid'] != uid or meta['gid'] != gid: raise Halt('ANCESTOR_BLOCKED')
                    root_fd = opened('plugins', config_fd)
                    if body_plugins_identity(os.fstat(root_fd)) != meta: raise Halt('CHANGED')
                    scan(root_fd, '')
                if body_plugins_identity(os.stat('plugins', dir_fd=config_fd, follow_symlinks=False)) != meta:
                    raise Halt('CHANGED')
                record['status'] = 'COMPLETE_PRESENT'; record['complete'] = True
            if directory(context_fd,True) != context_before or directory(config_fd,True) != config_before:
                raise Halt('CHANGED')
            for parent,name,expected in fixed_anchors:
                if body_plugins_identity(os.stat(name,dir_fd=parent,follow_symlinks=False)) != expected:
                    raise Halt('CHANGED')
        except Halt as exc:
            record.update(status=exc.status,error_code=exc.error,complete=False,stable=False)
        except OSError as exc:
            code = body_diagnostic_errno(exc)
            record.update(status='UNREADABLE',error_code=code,complete=False,stable=False)
        except BaseException:
            record.update(status='UNREADABLE',error_code='OTHER',complete=False,stable=False)
        finally:
            close_failed = False
            for fd in reversed(handles):
                try: os.close(fd)
                except OSError: close_failed = True
            if close_failed: record.update(status='UNREADABLE',error_code='OTHER',complete=False,stable=False)
        record['entries'].sort(key=lambda row:row['relative_path'])
        return body_plugins_record_shape(record)
    first = once()
    if not first['complete']: return first
    second = once()
    if first != second:
        first.update(status='CHANGED',complete=False,stable=False)
    else:
        first['stable'] = True
    return body_plugins_record_shape(first)


def body_plugins_read_record(path, expected_sha):
    need(type(expected_sha) is str and re.fullmatch('[0-9a-f]{64}',expected_sha), 'BODY_PLUGINS_PIN')
    first = body_plugins_identity(path.lstat())
    need(first['gid'] == os.getegid(), 'BODY_PLUGINS_CARRIER')
    pin = body_diagnostic_file(path,65536,0o600); raw = read(path,65536)
    record = body_json(raw,65536); body_plugins_record_shape(record)
    need(body_canonical(record) == raw and pin == {'bytes':len(raw),'sha256':digest(raw)} and
        digest(raw) == expected_sha and first == body_plugins_identity(path.lstat()), 'BODY_PLUGINS_PIN')
    return record,first,raw


def receive_body_plugins(state, output, phase):
    """Independent available-metadata receipt; cannot turn child failure into success."""
    need(phase in ('AFTER_COMMAND','PRIVATE_SUCCESS','FINAL'), 'BODY_PLUGINS_PHASE')
    validation = state.setdefault('claude_validation',{})
    old = validation.get('config_plugins_receiving',{})
    phases = {key:old.get('verified_phases',{}).get(key) is True
        for key in ('AFTER_COMMAND','PRIVATE_SUCCESS','FINAL')}
    result = {'schema':'dg17.claude.body-parent-config-plugins.v2','status':'UNRECEIVED',
        'reason':None,'latest_phase':phase,'verified_phases':phases,
        'fresh_parent_echild':False,'before_record_received':False,'before_absence_bound':False,
        'after_record_received':False,'metadata_recomputed':False,'public_projection_bound':False,
        'same_as_initial':False,'profile_admitted':False,'before_record_sha256':None,
        'after_record_sha256':None,'metadata_snapshot_sha256':None,
        'before_evidence_scope':'PRODUCER_PRE_NATIVE_RECORD_NOT_PARENT_HISTORICAL_OBSERVATION',
        'body_acceptance_from_diagnostics':False,
        'profile':'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1',
        'producer_admission_evidence_received':False,'producer_admission_custody_verified':False,
        'admission_evidence':None,
        'producer_custody_scope':'SOURCE_BOUND_RETAINED_PRODUCER_CUT_NOT_PARENT_HISTORICAL_OBSERVATION',
        'opaque_content_semantics':'UNRECEIVED'}
    validation['config_plugins_receiving'] = result
    try:
        # The existing independent legacy receiver establishes complete capture,
        # exact public/captured-result equality and its owned filesystem anchors.
        legacy = validation.get('diagnostic_receiving',{})
        need(validation.get('valid') is True and validation.get('captured_result_matches') is True and
            state.get('active_command') is None and legacy.get('verified_phases',{}).get(phase) is True and
            legacy.get('public_projection_bound') is True and legacy.get('fresh_parent_echild') is True,
            'BODY_PLUGINS_PUBLIC_UNBOUND')
        body_diagnostic_quiescence(); result['fresh_parent_echild'] = True
        public = state['claude']['config_plugins_profile']
        need(type(public) is dict and public.get('schema') == 'dg17.claude.body-config-plugins.v2' and
            public.get('profile') == 'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1',
            'BODY_PLUGINS_PUBLIC_UNBOUND')
        root = output/'private/claude-canonical-body'; body_diagnostic_anchor(root)
        before_path = root/'CONFIG_PLUGINS_BEFORE.json'; after_path = root/'CONFIG_PLUGINS_AFTER.json'
        before,before_id,before_raw = body_plugins_read_record(before_path,public.get('before_record_sha256'))
        absent = {'schema':'dg17.claude.config-plugins-snapshot.v1','path_id':'CONFIG_PLUGINS',
            'status':'COMPLETE_ABSENT','root':None,'entries':[],'error_code':None,'complete':True,'stable':True}
        need(before == absent and public.get('before_absent') is True,'BODY_PLUGINS_BEFORE')
        result.update(before_record_received=True,before_absence_bound=True,before_record_sha256=digest(before_raw))
        after,after_id,after_raw = body_plugins_read_record(after_path,public.get('after_record_sha256'))
        result.update(after_record_received=True,after_record_sha256=digest(after_raw))
        observed = body_plugins_census(root/'context-canonical-body',os.geteuid(),os.getegid())
        need(observed == after,'BODY_PLUGINS_AFTER_DIFFERS')
        admission = body_plugins_admission_receiving(root,state['claude'],state['receipt'])
        result.update(admission_evidence=admission,
            producer_admission_evidence_received=admission['status'] == 'RECEIVED',
            producer_admission_custody_verified=admission['verified'] is True)
        projected = body_plugins_projection(observed,os.geteuid(),os.getegid(),admission['verified'])
        need(projected == public.get('after') and projected['population_sha256'] == digest(after_raw),
            'BODY_PLUGINS_PROJECTION_DIFFERS')
        result.update(metadata_recomputed=True,public_projection_bound=True,
            profile_admitted=projected['profile_admitted'])
        need(body_plugins_census(root/'context-canonical-body',os.geteuid(),os.getegid()) == observed,
            'BODY_PLUGINS_AFTER_DIFFERS')
        need(body_plugins_read_record(before_path,public['before_record_sha256']) == (before,before_id,before_raw) and
            body_plugins_read_record(after_path,public['after_record_sha256']) == (after,after_id,after_raw),
            'BODY_PLUGINS_CARRIER_CHANGED')
        need(body_plugins_admission_receiving(root,state['claude'],state['receipt']) == admission,
            'BODY_PLUGINS_OUTPUT_CHANGED')
        body_diagnostic_quiescence()
        snapshot_sha = digest(body_canonical({'before_identity':before_id,'after_identity':after_id,
            'before_sha256':digest(before_raw),'after_sha256':digest(after_raw),'observed':observed,'admission_evidence':admission}))
        if 'body_plugins_baseline_sha256' not in state: state['body_plugins_baseline_sha256'] = snapshot_sha
        need(state['body_plugins_baseline_sha256'] == snapshot_sha,'BODY_PLUGINS_CHANGED_SINCE_FIRST')
        phases[phase] = True
        result.update(status='RECEIVED_AVAILABLE_METADATA',same_as_initial=True,metadata_snapshot_sha256=snapshot_sha)
    except BaseException as exc:
        permitted = {'BODY_PLUGINS_PUBLIC_UNBOUND','BODY_PLUGINS_PIN','BODY_PLUGINS_CARRIER',
            'BODY_PLUGINS_RECORD','BODY_PLUGINS_RECORD_BOUND','BODY_PLUGINS_PATH','BODY_PLUGINS_BEFORE',
            'BODY_PLUGINS_AFTER_DIFFERS','BODY_PLUGINS_PROJECTION_DIFFERS','BODY_PLUGINS_CARRIER_CHANGED',
            'BODY_PLUGINS_CHANGED_SINCE_FIRST','BODY_PLUGINS_OUTPUT_CHANGED'}
        result['reason'] = str(exc) if isinstance(exc,Refusal) and str(exc) in permitted else 'METADATA_UNAVAILABLE'
    return result


def body_plugins_receiving_success(state, phase):
    value = state.get('claude_validation',{}).get('config_plugins_receiving',{})
    return (value.get('schema') == 'dg17.claude.body-parent-config-plugins.v2' and
        value.get('profile') == 'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1' and
        value.get('status') == 'RECEIVED_AVAILABLE_METADATA' and value.get('reason') is None and all(
        value.get(key) is True for key in ('fresh_parent_echild','before_record_received','before_absence_bound',
            'after_record_received','metadata_recomputed','public_projection_bound','same_as_initial','profile_admitted',
            'producer_admission_evidence_received','producer_admission_custody_verified')) and
        value.get('verified_phases',{}).get(phase) is True)


def body_plugins_child_success(value):
    profile = value.get('config_plugins_profile')
    if type(profile) is not dict or profile.get('schema') != 'dg17.claude.body-config-plugins.v2': return False
    if profile.get('profile') != 'OPAQUE_POST_NATIVE_PLUGIN_OUTPUT_V1': return False
    if not body_plugins_quiescence_valid(profile.get('admission_quiescence')): return False
    if not all(profile.get(key) is True for key in ('before_absent','closing_unchanged','final_unchanged')): return False
    for key in ('before_record_sha256','after_record_sha256'):
        if type(profile.get(key)) is not str or re.fullmatch('[0-9a-f]{64}',profile[key]) is None: return False
    after = profile.get('after')
    return (type(after) is dict and after.get('schema') == 'dg17.claude.config-plugins-observation.v2' and
        after.get('profile_admitted') is True and after.get('complete') is True and after.get('stable') is True and
        after.get('population_sha256') == profile['after_record_sha256'])


"""Prospective parent diagnostic owners, derived before changed child code.

Composed later into the exact reviewed parent namespace. This file has no
entrypoint, imports no child projector, starts no process and writes no private
or public file. Existing parent parsers, file readers, invocation and complete
capture/provider owners are explicit immutable dependencies.
"""
import posixpath

# Body08 parent helpers derived before producer authorship; pure data only.
PLUGIN_JOINT_SCHEMA = 'dg17.claude.plugin-joint-shape.v1'
PLUGIN_JOINT_V2_SCHEMA = 'dg17.claude.native-plugin-identity-diagnostic.v2'
PLUGIN_JOINT_V3_SCHEMA = 'dg17.claude.native-plugin-identity-diagnostic.v3'
PLUGIN_JOINT_ROW_CAP = 4
PLUGIN_JOINT_COUNT_BOUND = 196609
PLUGIN_JOINT_DIAGNOSTIC_BOUND = 4096
PLUGIN_JOINT_TYPE_LABELS = ('NULL', 'BOOLEAN', 'INTEGER', 'FLOAT', 'STRING', 'ARRAY', 'OBJECT')
PLUGIN_JOINT_FIELD_TYPES = ('ABSENT',) + PLUGIN_JOINT_TYPE_LABELS
PLUGIN_JOINT_NAME_LITERALS = {'implementaudit': 'MANIFEST_NAME_EXACT', 'implementaudit@inline': 'MANIFEST_NAME_INLINE', 'cc-plugin-agents-md': 'DOCUMENTED_1_BARE', 'cc-plugin-agents-md@builtin': 'DOCUMENTED_1_BUILTIN_ID', 'cc-plugin-diff': 'DOCUMENTED_2_BARE', 'cc-plugin-diff@builtin': 'DOCUMENTED_2_BUILTIN_ID', 'cc-plugin-plugin-authoring': 'DOCUMENTED_3_BARE', 'cc-plugin-plugin-authoring@builtin': 'DOCUMENTED_3_BUILTIN_ID', 'cc-plugin-sec-default': 'DOCUMENTED_4_BARE', 'cc-plugin-sec-default@builtin': 'DOCUMENTED_4_BUILTIN_ID', 'cc-plugin-telemetry': 'DOCUMENTED_5_BARE', 'cc-plugin-telemetry@builtin': 'DOCUMENTED_5_BUILTIN_ID', 'cc-plugin-you-should-know': 'DOCUMENTED_6_BARE', 'cc-plugin-you-should-know@builtin': 'DOCUMENTED_6_BUILTIN_ID'}
PLUGIN_JOINT_NAME_LABELS = ('MISSING', 'NON_STRING', *PLUGIN_JOINT_NAME_LITERALS.values(), 'OTHER_STRING')
PLUGIN_JOINT_PATH_LABELS = ('MISSING', 'NON_STRING', 'EXACT_EXPECTED', 'LEXICAL_ONLY', 'OTHER_STRING')
PLUGIN_JOINT_KEYSETS = {'NAME_PATH_ONLY': frozenset(('name', 'path')), 'NAME_PATH_SOURCE': frozenset(('name', 'path', 'source')), 'NAME_PATH_VERSION': frozenset(('name', 'path', 'version')), 'NAME_PATH_SOURCE_VERSION': frozenset(('name', 'path', 'source', 'version'))}
PLUGIN_JOINT_KEY_SHAPES = (*PLUGIN_JOINT_KEYSETS, 'OTHER')
PLUGIN_JOINT_KNOWN_KEYS = frozenset(('name', 'path', 'source', 'version'))
PLUGIN_JOINT_REASONS = ('ENVELOPE_UNAVAILABLE', 'NON_ARRAY', 'ROW_LIMIT', 'ENCODING_REFUSED', 'OUTPUT_BOUND')
PLUGIN_JOINT_BASE_FIELDS = frozenset(('schema', 'status', 'reason', 'raw_stdout_bytes', 'raw_stdout_sha256', 'expected_context_sha256', 'event_count', 'pre_plugin_envelope_received', 'plugins_present', 'plugins_type', 'plugins_canonical_bytes', 'plugins_canonical_sha256', 'list_length', 'singleton', 'array_profile', 'original_equality', 'body_acceptance_from_diagnostics'))

class PluginJointRefusal(ValueError):
    """No valid bounded result can be supplied without changing legacy fields."""

def plugin_joint_json_bytes(value):
    """Selected commitment codec: compact ASCII JSON, NO terminal LF."""
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('ascii')

def plugin_joint_wire_bytes(value):
    """Existing diagnostic/whole-child codec: compact ASCII JSON plus LF."""
    return plugin_joint_json_bytes(value) + b'\n'

def plugin_joint_sha(raw):
    return hashlib.sha256(raw).hexdigest()

def plugin_joint_type(value):
    types = {type(None): 'NULL', bool: 'BOOLEAN', int: 'INTEGER', float: 'FLOAT', str: 'STRING', list: 'ARRAY', dict: 'OBJECT'}
    if type(value) not in types:
        raise PluginJointRefusal('NON_JSON_TYPE')
    if type(value) is float and (not math.isfinite(value)):
        raise PluginJointRefusal('NONFINITE_JSON')
    return types[type(value)]

def plugin_joint_json_shape(value):
    """Check exact JSON types and finite work, without new Unicode normalization.

This does not replace the unchanged raw codec. In particular the caller owns
its existing string-value UTF8 check, duplicate-key refusal and envelope proof.
Canonical commitments preserve admitted escaped keys, including surrogate keys.
"""
    pending = [(value, 0)]
    count = 0
    while pending:
        current, depth = pending.pop()
        count += 1
        if count > 32768 or depth > 32:
            raise PluginJointRefusal('JSON_COMPLEXITY')
        kind = plugin_joint_type(current)
        if kind == 'OBJECT':
            if len(current) > 1024 or any((type(k) is not str or len(k) > 1024 for k in current)):
                raise PluginJointRefusal('OBJECT_SHAPE')
            pending.extend(((v, depth + 1) for v in current.values()))
        elif kind == 'ARRAY':
            if len(current) > 4096:
                raise PluginJointRefusal('ARRAY_SHAPE')
            pending.extend(((v, depth + 1) for v in current))

def plugin_joint_unavailable(reason):
    if reason not in PLUGIN_JOINT_REASONS:
        raise PluginJointRefusal('UNKNOWN_REASON')
    return {'schema': PLUGIN_JOINT_SCHEMA, 'status': 'UNAVAILABLE', 'reason': reason, 'rows': None}

def plugin_joint_derive(plugins, expected_plugin, *, envelope_available):
    """Derive every selected row from already admitted parent-owned values.

Unavailable precedence is contractual. The availability boolean is a local
parent precondition, never a producer-supplied custody or acceptance assertion.
"""
    if envelope_available is not True or type(expected_plugin) is not str or (not expected_plugin.startswith('/')) or ('\x00' in expected_plugin):
        return plugin_joint_unavailable('ENVELOPE_UNAVAILABLE')
    if type(plugins) is not list:
        return plugin_joint_unavailable('NON_ARRAY')
    if len(plugins) > PLUGIN_JOINT_ROW_CAP:
        return plugin_joint_unavailable('ROW_LIMIT')
    try:
        plugin_joint_json_shape(plugins)
        if len(plugin_joint_wire_bytes(plugins)) > PLUGIN_JOINT_COUNT_BOUND:
            raise PluginJointRefusal('CANONICAL_PLUGIN_BOUND')
        rows = []
        for element in plugins:
            kind = plugin_joint_type(element)
            if kind != 'OBJECT':
                rows.append([kind] + [None] * 10)
                continue
            keys = set(element)
            if 'name' not in element:
                name = 'MISSING'
            elif type(element['name']) is not str:
                name = 'NON_STRING'
            else:
                name = PLUGIN_JOINT_NAME_LITERALS.get(element['name'], 'OTHER_STRING')
            if 'path' not in element:
                path = 'MISSING'
            elif type(element['path']) is not str:
                path = 'NON_STRING'
            elif element['path'] == expected_plugin:
                path = 'EXACT_EXPECTED'
            elif posixpath.normpath(element['path']) == posixpath.normpath(expected_plugin):
                path = 'LEXICAL_ONLY'
            else:
                path = 'OTHER_STRING'
            if name == 'OTHER_STRING':
                encoded_name = plugin_joint_json_bytes(element['name'])
                name_bytes, name_sha = (len(encoded_name), plugin_joint_sha(encoded_name))
            else:
                name_bytes = name_sha = None
            key_sha = plugin_joint_sha(plugin_joint_json_bytes(sorted(element)))
            shape = next((label for label, fixed in PLUGIN_JOINT_KEYSETS.items() if keys == fixed), 'OTHER')
            source_type = 'ABSENT' if 'source' not in element else plugin_joint_type(element['source'])
            version_type = 'ABSENT' if 'version' not in element else plugin_joint_type(element['version'])
            rows.append([kind, name, path, name_bytes, name_sha, len(element), key_sha, shape, source_type, version_type, len(keys - PLUGIN_JOINT_KNOWN_KEYS)])
        result = {'schema': PLUGIN_JOINT_SCHEMA, 'status': 'COMPLETE', 'reason': None, 'rows': rows}
        if not plugin_joint_valid(result):
            raise PluginJointRefusal('DERIVED_WIRE_UNREPRESENTABLE')
        return result
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError):
        return plugin_joint_unavailable('ENCODING_REFUSED')

def plugin_joint_count_shape(value):
    return type(value) is int and 0 <= value <= PLUGIN_JOINT_COUNT_BOUND

def plugin_joint_hash_shape(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None

def plugin_joint_valid(value):
    """Mandatory exact tuple owner; generic schema validation is insufficient."""
    if type(value) is not dict or set(value) != {'schema', 'status', 'reason', 'rows'}:
        return False
    if type(value['schema']) is not str or value['schema'] != PLUGIN_JOINT_SCHEMA or type(value['status']) is not str:
        return False
    if value['status'] == 'UNAVAILABLE':
        return type(value['reason']) is str and value['reason'] in PLUGIN_JOINT_REASONS and (value['rows'] is None)
    if value['status'] != 'COMPLETE' or value['reason'] is not None or type(value['rows']) is not list or (len(value['rows']) > PLUGIN_JOINT_ROW_CAP):
        return False
    for row in value['rows']:
        if type(row) is not list or len(row) != 11 or type(row[0]) is not str or (row[0] not in PLUGIN_JOINT_TYPE_LABELS):
            return False
        if row[0] != 'OBJECT':
            if any((x is not None for x in row[1:])):
                return False
            continue
        if type(row[1]) is not str or row[1] not in PLUGIN_JOINT_NAME_LABELS or type(row[2]) is not str or (row[2] not in PLUGIN_JOINT_PATH_LABELS):
            return False
        if row[1] == 'OTHER_STRING':
            if not plugin_joint_count_shape(row[3]) or row[3] < 2 or (not plugin_joint_hash_shape(row[4])):
                return False
        elif row[3] is not None or row[4] is not None:
            return False
        if not plugin_joint_count_shape(row[5]) or row[5] > 1024 or (not plugin_joint_hash_shape(row[6])) or (type(row[7]) is not str) or (row[7] not in PLUGIN_JOINT_KEY_SHAPES):
            return False
        if any((type(x) is not str or x not in PLUGIN_JOINT_FIELD_TYPES for x in row[8:10])) or not plugin_joint_count_shape(row[10]):
            return False
        known_present = (row[1] != 'MISSING') + (row[2] != 'MISSING') + (row[8] != 'ABSENT') + (row[9] != 'ABSENT')
        if row[5] != known_present + row[10]:
            return False
        keys = set()
        if row[1] != 'MISSING':
            keys.add('name')
        if row[2] != 'MISSING':
            keys.add('path')
        if row[8] != 'ABSENT':
            keys.add('source')
        if row[9] != 'ABSENT':
            keys.add('version')
        expected_shape = next((label for label, fixed in PLUGIN_JOINT_KEYSETS.items() if row[10] == 0 and keys == fixed), 'OTHER')
        if row[7] != expected_shape:
            return False
        if row[10] == 0 and row[6] != plugin_joint_sha(plugin_joint_json_bytes(sorted(keys))):
            return False
    return True

def plugin_joint_add(base_v2, plugins, expected_plugin, *, envelope_available):
    """Preserve every legacy value, add selected wire, and apply total size guard.

The caller retains the original base schema/envelope and private receiving.
This model is not an alternative way to admit an arbitrary base record.
"""
    if type(base_v2) is not dict or set(base_v2) != PLUGIN_JOINT_BASE_FIELDS or base_v2.get('schema') != PLUGIN_JOINT_V2_SCHEMA:
        raise PluginJointRefusal('BASE_DIAGNOSTIC_SHAPE')
    plugin_joint_json_shape(base_v2)
    base_raw = plugin_joint_wire_bytes(base_v2)
    if len(base_raw) > PLUGIN_JOINT_DIAGNOSTIC_BOUND:
        raise PluginJointRefusal('UNCHANGED_BASE_DIAGNOSTIC_UNREPRESENTABLE')
    result = json.loads(base_raw)
    result['schema'] = PLUGIN_JOINT_V3_SCHEMA
    available = envelope_available is True and base_v2.get('pre_plugin_envelope_received') is True
    result['joint_profile'] = plugin_joint_derive(plugins, expected_plugin, envelope_available=available)
    if len(plugin_joint_wire_bytes(result)) > PLUGIN_JOINT_DIAGNOSTIC_BOUND:
        if result['joint_profile']['status'] == 'COMPLETE':
            result['joint_profile'] = plugin_joint_unavailable('OUTPUT_BOUND')
        if len(plugin_joint_wire_bytes(result)) > PLUGIN_JOINT_DIAGNOSTIC_BOUND:
            raise PluginJointRefusal('UNCHANGED_BASE_DIAGNOSTIC_UNREPRESENTABLE')
    return result

def plugin_joint_projection_shape(value):
    """Exact joint/total bound; full old schema and raw receiving remain separate."""
    if (type(value) is not dict or set(value) != PLUGIN_JOINT_BASE_FIELDS | {'joint_profile'} or
            value.get('schema') != PLUGIN_JOINT_V3_SCHEMA or
            not plugin_joint_valid(value.get('joint_profile'))):
        return False
    try:
        return len(body_canonical(value)) <= 4096
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError):
        return False


PLUGIN_DIAGNOSTIC_SCHEMA = 'dg17.claude.native-plugin-identity-diagnostic.v3'
PLUGIN_DIAGNOSTIC_NAME = 'implementaudit'
PLUGIN_DIAGNOSTIC_INLINE_NAME = 'implementaudit@inline'
# Prospective literal discriminators only. A matching name neither establishes
# actual origin nor changes admission or body acceptance.
PLUGIN_DIAGNOSTIC_NAME_LITERALS = {
    'MANIFEST_NAME_EXACT': 'implementaudit',
    'MANIFEST_NAME_INLINE': 'implementaudit@inline',
    'DOCUMENTED_1_BARE': 'cc-plugin-agents-md',
    'DOCUMENTED_1_BUILTIN_ID': 'cc-plugin-agents-md@builtin',
    'DOCUMENTED_2_BARE': 'cc-plugin-diff',
    'DOCUMENTED_2_BUILTIN_ID': 'cc-plugin-diff@builtin',
    'DOCUMENTED_3_BARE': 'cc-plugin-plugin-authoring',
    'DOCUMENTED_3_BUILTIN_ID': 'cc-plugin-plugin-authoring@builtin',
    'DOCUMENTED_4_BARE': 'cc-plugin-sec-default',
    'DOCUMENTED_4_BUILTIN_ID': 'cc-plugin-sec-default@builtin',
    'DOCUMENTED_5_BARE': 'cc-plugin-telemetry',
    'DOCUMENTED_5_BUILTIN_ID': 'cc-plugin-telemetry@builtin',
    'DOCUMENTED_6_BARE': 'cc-plugin-you-should-know',
    'DOCUMENTED_6_BUILTIN_ID': 'cc-plugin-you-should-know@builtin',
}
PLUGIN_DIAGNOSTIC_MODEL = 'claude-sonnet-4-6'
PLUGIN_DIAGNOSTIC_CANONICAL_BOUND = 196609
PLUGIN_DIAGNOSTIC_REASONS = frozenset((
    'NOT_ATTEMPTED', 'CUSTODY_OR_BOOKEND_UNRECEIVED', 'EXPECTED_CONTEXT_UNRECEIVED',
    'INPUT_BYTE_BOUND', 'EVENT_POPULATION_BOUND', 'JSON_UNRECEIVED',
    'JSON_DUPLICATE_KEY', 'JSON_NONFINITE', 'JSON_COMPLEXITY', 'JSON_OBJECT_BOUND',
    'JSON_ARRAY_BOUND', 'JSON_STRING_ENCODING', 'JSON_TYPE_UNRECEIVED',
    'EVENT_TYPE_UNRECEIVED', 'SESSION_DIFFERS', 'CHILD_EVENT_UNRECEIVED',
    'INIT_RESULT_ORDER_UNRECEIVED', 'CONFIG_IDENTITY_DIFFERS', 'TOOL_SURFACE_DIFFERS',
    'MCP_OR_PLUGIN_ERROR_PRESENT', 'PUBLIC_BOUND_REFUSED'))


def plugin_diagnostic_empty(reason='NOT_ATTEMPTED'):
    need(reason in PLUGIN_DIAGNOSTIC_REASONS, 'PLUGIN_DIAGNOSTIC_REASON')
    return {'schema': PLUGIN_DIAGNOSTIC_SCHEMA, 'status': 'UNRECEIVED', 'reason': reason,
        'raw_stdout_bytes': None, 'raw_stdout_sha256': None, 'expected_context_sha256': None,
        'event_count': None, 'pre_plugin_envelope_received': False,
        'plugins_present': None, 'plugins_type': None, 'plugins_canonical_bytes': None,
        'plugins_canonical_sha256': None, 'list_length': None, 'singleton': None,
        'array_profile': None,
        'joint_profile': plugin_joint_unavailable('ENVELOPE_UNAVAILABLE'),
        'original_equality': None, 'body_acceptance_from_diagnostics': False}


def plugin_diagnostic_type(value):
    types = {type(None): 'NULL', bool: 'BOOLEAN', int: 'INTEGER', float: 'FLOAT',
             str: 'STRING', list: 'ARRAY', dict: 'OBJECT'}
    need(type(value) in types, 'PLUGIN_DIAGNOSTIC_TYPE')
    return types[type(value)]


def plugin_diagnostic_named_field(item, key, expected, name_field=False):
    present = key in item
    result = {'present': present, 'type': plugin_diagnostic_type(item[key]) if present else 'MISSING',
        'utf8_bytes': None, 'utf8_sha256': None, 'equals_expected': None}
    if name_field:
        result['name_relation'] = 'MISSING' if not present else 'NON_STRING'
    else:
        result['lexical_normalization_equals_expected'] = None
    if present and type(item[key]) is str:
        raw = item[key].encode('utf-8', errors='strict')
        need(len(raw) <= 32768, 'PLUGIN_DIAGNOSTIC_STRING_BOUND')
        result.update(utf8_bytes=len(raw), utf8_sha256=digest(raw), equals_expected=item[key] == expected)
        if name_field:
            result['name_relation'] = ('MANIFEST_NAME_EXACT' if item[key] == PLUGIN_DIAGNOSTIC_NAME else
                'MANIFEST_NAME_WITH_LITERAL_INLINE_SUFFIX' if item[key] == PLUGIN_DIAGNOSTIC_INLINE_NAME else 'OTHER_STRING')
        else:
            # Pure POSIX lexical data operation: no filesystem lookup, cwd join,
            # expanduser, symlink resolution, path fallback or acceptance change.
            result['lexical_normalization_equals_expected'] = (
                posixpath.normpath(item[key]) == posixpath.normpath(expected))
    return result


def plugin_diagnostic_array_profile(value, expected_plugin):
    """Count every codec-admitted element; literals disclose no actual origin.

    Completeness describes this array value only. No counter admits a plugin,
    identifies an installed/built-in source, or confers native/body acceptance.
    """
    need(type(value) is list and len(value) <= 4096, 'PLUGIN_DIAGNOSTIC_VALUE_BOUND')
    result = {'complete': True, 'element_count': len(value),
        'type_counts': dict.fromkeys(('NULL','BOOLEAN','INTEGER','FLOAT','STRING','ARRAY','OBJECT'), 0),
        'object_keyset_counts': dict.fromkeys(('EXACT_NAME_PATH','OTHER_OBJECT'), 0),
        'object_name_counts': dict.fromkeys(
            ('MISSING','NON_STRING',*PLUGIN_DIAGNOSTIC_NAME_LITERALS,'OTHER_STRING'), 0),
        'object_path_counts': dict.fromkeys(
            ('MISSING','NON_STRING','EXACT_EXPECTED','LEXICAL_ONLY','OTHER_STRING'), 0),
        'record_counts': dict.fromkeys(
            ('EXACT_EXPECTED_RECORD','INLINE_NAME_EXACT_PATH_RECORD','OTHER_ELEMENT'), 0)}
    for item in value:
        result['type_counts'][plugin_diagnostic_type(item)] += 1
        record = 'OTHER_ELEMENT'
        if type(item) is dict:
            keys = 'EXACT_NAME_PATH' if set(item) == {'name','path'} else 'OTHER_OBJECT'
            result['object_keyset_counts'][keys] += 1
            if 'name' not in item:
                name = 'MISSING'
            elif type(item['name']) is not str:
                name = 'NON_STRING'
            else:
                name = next((label for label, literal in PLUGIN_DIAGNOSTIC_NAME_LITERALS.items()
                             if item['name'] == literal), 'OTHER_STRING')
            result['object_name_counts'][name] += 1
            if 'path' not in item:
                path = 'MISSING'
            elif type(item['path']) is not str:
                path = 'NON_STRING'
            elif item['path'] == expected_plugin:
                path = 'EXACT_EXPECTED'
            elif posixpath.normpath(item['path']) == posixpath.normpath(expected_plugin):
                # Lexical POSIX data only: no filesystem lookup or path following.
                path = 'LEXICAL_ONLY'
            else:
                path = 'OTHER_STRING'
            result['object_path_counts'][path] += 1
            if item == {'name': PLUGIN_DIAGNOSTIC_NAME, 'path': expected_plugin}:
                record = 'EXACT_EXPECTED_RECORD'
            elif item == {'name': PLUGIN_DIAGNOSTIC_INLINE_NAME, 'path': expected_plugin}:
                record = 'INLINE_NAME_EXACT_PATH_RECORD'
        result['record_counts'][record] += 1
    return result


def plugin_diagnostic_projection(raw, session, cwd, plugin, model=PLUGIN_DIAGNOSTIC_MODEL):
    """Complete pre-plugin envelope and plugin data only; never native acceptance."""
    result = plugin_diagnostic_empty()
    reason = 'EXPECTED_CONTEXT_UNRECEIVED'
    try:
        need(type(session) is str and re.fullmatch(
            r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', session) is not None and
            type(cwd) is str and cwd.startswith('/') and '\x00' not in cwd and
            type(plugin) is str and plugin.startswith('/') and '\x00' not in plugin and
            type(model) is str and model == PLUGIN_DIAGNOSTIC_MODEL, 'PLUGIN_DIAGNOSTIC_CONTEXT')
        cwd.encode('utf-8', errors='strict'); plugin.encode('utf-8', errors='strict')
        result['expected_context_sha256'] = digest(body_canonical({
            'session_id': session, 'cwd': cwd, 'plugin': plugin, 'model': model}))
        reason = 'INPUT_BYTE_BOUND'
        need(type(raw) is bytes and 0 < len(raw) <= 32768, 'PLUGIN_DIAGNOSTIC_INPUT')
        result.update(raw_stdout_bytes=len(raw), raw_stdout_sha256=digest(raw))
        lines = raw.splitlines(); reason = 'EVENT_POPULATION_BOUND'
        need(1 <= len(lines) <= 128 and all(lines), 'PLUGIN_DIAGNOSTIC_EVENTS')
        result['event_count'] = len(lines)
        events = []
        for line in lines:
            reason = 'JSON_UNRECEIVED'
            try:
                events.append(body_json(line, 32768))
            except BaseException as exc:
                mapped = {'CATALOGUE_DUPLICATE_KEY': 'JSON_DUPLICATE_KEY',
                    'BODY_JSON_NONFINITE': 'JSON_NONFINITE', 'BODY_JSON_COMPLEXITY': 'JSON_COMPLEXITY',
                    'BODY_JSON_OBJECT_BOUND': 'JSON_OBJECT_BOUND', 'BODY_JSON_ARRAY_BOUND': 'JSON_ARRAY_BOUND',
                    'BODY_JSON_STRING_BOUND': 'JSON_STRING_ENCODING', 'BODY_JSON_TYPE': 'JSON_TYPE_UNRECEIVED'}
                if isinstance(exc, Refusal): reason = mapped.get(str(exc), 'JSON_UNRECEIVED')
                elif isinstance(exc, UnicodeError): reason = 'JSON_STRING_ENCODING'
                raise
        reason = 'EVENT_TYPE_UNRECEIVED'
        need(all(type(event) is dict and event.get('type') in ('system','user','assistant','result')
                 for event in events), 'PLUGIN_DIAGNOSTIC_EVENT_TYPE')
        reason = 'SESSION_DIFFERS'
        need(all(event.get('session_id') == session for event in events), 'PLUGIN_DIAGNOSTIC_SESSION')
        reason = 'CHILD_EVENT_UNRECEIVED'
        need(all(event.get('parent_tool_use_id') is None for event in events), 'PLUGIN_DIAGNOSTIC_CHILD')
        inits = [(index,event) for index,event in enumerate(events)
                 if event.get('type') == 'system' and event.get('subtype') == 'init']
        results = [(index,event) for index,event in enumerate(events) if event.get('type') == 'result']
        reason = 'INIT_RESULT_ORDER_UNRECEIVED'
        need(len(inits) == 1 and len(results) == 1 and
             inits[0][0] < results[0][0] == len(events)-1, 'PLUGIN_DIAGNOSTIC_ORDER')
        init = inits[0][1]; reason = 'CONFIG_IDENTITY_DIFFERS'
        need(init.get('cwd') == cwd and init.get('model') == model, 'PLUGIN_DIAGNOSTIC_CONFIG')
        tools = init.get('tools'); reason = 'TOOL_SURFACE_DIFFERS'
        need(type(tools) is list and all(type(item) is str for item in tools) and
             len(tools) == len(set(tools)) and 'Skill' in tools and
             all(item in ('Skill','EndConversation') for item in tools), 'PLUGIN_DIAGNOSTIC_TOOLS')
        reason = 'MCP_OR_PLUGIN_ERROR_PRESENT'
        need(init.get('mcp_servers') == [] and init.get('mcp_server_errors',[]) == [] and
             init.get('plugin_errors',[]) == [], 'PLUGIN_DIAGNOSTIC_STARTUP')

        # Exactly the pre-plugin predicates of frozen native_projection above.
        # Skills, system subtype handling, user/assistant blocks and terminal ACK
        # remain later native predicates; this owner neither runs nor bypasses them.
        result['pre_plugin_envelope_received'] = True
        present = 'plugins' in init
        result['plugins_present'] = present
        result['plugins_type'] = plugin_diagnostic_type(init['plugins']) if present else 'MISSING'
        if present:
            value = init['plugins']; canonical = body_canonical(value)
            reason = 'PUBLIC_BOUND_REFUSED'
            need(len(canonical) <= PLUGIN_DIAGNOSTIC_CANONICAL_BOUND, 'PLUGIN_DIAGNOSTIC_VALUE_BOUND')
            result.update(plugins_canonical_bytes=len(canonical), plugins_canonical_sha256=digest(canonical))
            if type(value) is list:
                result['list_length'] = len(value)
                result['array_profile'] = plugin_diagnostic_array_profile(value, plugin)
                if len(value) == 1:
                    item = value[0]; encoded_item = body_canonical(item)
                    need(len(encoded_item) <= PLUGIN_DIAGNOSTIC_CANONICAL_BOUND, 'PLUGIN_DIAGNOSTIC_VALUE_BOUND')
                    observed = {'type': plugin_diagnostic_type(item), 'canonical_bytes': len(encoded_item),
                        'canonical_sha256': digest(encoded_item), 'key_count': None, 'keyset_sha256': None,
                        'exact_name_path_keys': None, 'name': None, 'path': None}
                    if type(item) is dict:
                        observed.update(key_count=len(item), keyset_sha256=digest(body_canonical(sorted(item))),
                            exact_name_path_keys=set(item) == {'name','path'},
                            name=plugin_diagnostic_named_field(item, 'name', PLUGIN_DIAGNOSTIC_NAME, True),
                            path=plugin_diagnostic_named_field(item, 'path', plugin))
                    result['singleton'] = observed
        result['original_equality'] = init.get('plugins') == [{'name':'implementaudit','path':plugin}]
        result.update(status='RECEIVED_PRE_PLUGIN_DIAGNOSTIC', reason=None)
        reason = 'PUBLIC_BOUND_REFUSED'
        # Preserve the exact old v2 bound before adding any joint fields.
        base_v2 = {key: result[key] for key in PLUGIN_JOINT_BASE_FIELDS}
        base_v2['schema'] = PLUGIN_JOINT_V2_SCHEMA
        need(len(body_canonical(base_v2)) <= 4096, 'PLUGIN_DIAGNOSTIC_PUBLIC_BOUND')
    except BaseException:
        # Partial observations never masquerade as a complete field projection.
        refused = plugin_diagnostic_empty(reason if reason in PLUGIN_DIAGNOSTIC_REASONS else 'JSON_UNRECEIVED')
        for key in ('raw_stdout_bytes','raw_stdout_sha256','expected_context_sha256','event_count'):
            refused[key] = result[key]
        return refused
    # Extension-only refusal must not reset or hide the old received fields.
    # This call is deliberately outside the old raw/envelope refusal boundary.
    return plugin_joint_add(base_v2, init.get('plugins'), plugin, envelope_available=True)


def plugin_diagnostic_bookends(public):
    """Require existing source-bound facts; do not manufacture historical cuts."""
    need(type(public) is dict and all(public.get(key) is True for key in (
        'control_source_before','control_source_after','runtime_before','runtime_after',
        'archive_before','archive_after','package_before','package_after','startup_before','startup_after')),
        'PLUGIN_DIAGNOSTIC_BOOKENDS')
    commands = public.get('commands')
    need(type(commands) is list and len(commands) == 1 and type(commands[0]) is dict,
        'PLUGIN_DIAGNOSTIC_BOOKENDS')
    need(all(commands[0].get(key) is True for key in (
        'source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')),
        'PLUGIN_DIAGNOSTIC_BOOKENDS')
    custody = public.get('provider_custody')
    need(type(custody) is dict and all(custody.get(key) is True for key in (
        'started','thread_joined','all_owned_sockets_closed','verified','semantic_response_complete')) and
        custody.get('failure') is None and custody.get('supplemental_failures') == [] and
        type(custody.get('request_count')) is int and 1 <= custody['request_count'] <= 16 and
        type(custody.get('semantic_request_count')) is int and custody['semantic_request_count'] == 1 and
        type(custody.get('semantic_request_index')) is int and 1 <= custody['semantic_request_index'] <= custody['request_count'] and
        type(custody.get('captured_request_bytes')) is int and 1 <= custody['captured_request_bytes'] <= 4194304,
        'PLUGIN_DIAGNOSTIC_PROVIDER_COMPLETENESS')


def plugin_diagnostic_failure_snapshot(state):
    public = state.get('claude')
    public = public if type(public) is dict else {}
    return body_canonical({'failed':state.get('failed'), 'failure':state.get('failure'),
        'failures':state.get('failures'), 'claude_failure':public.get('failure'),
        'claude_supplemental':public.get('supplemental_failures')})


def plugin_diagnostic_public_binding(state, output):
    """Reopen complete fixed outer streams; rc1 is valid failure-time evidence."""
    rows = [(index+1,row) for index,row in enumerate(state.get('commands',[]))
            if type(row) is dict and row.get('name') == 'loopback-claude-canonical-body']
    need(len(rows) == 1, 'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE')
    ordinal,capture = rows[0]
    need(body_diagnostic_capture_shape(capture) and all(capture[key] is True for key in
        ('process_started','streams_complete','pidfd_acquired')) and
        capture['timeout'] is False and capture['output_bound_exceeded'] is False and
        capture['internal_failure'] is None and capture['cleanup']['echild'] is True,
        'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE')
    body_diagnostic_anchor(output); body_diagnostic_anchor(output/'private')
    population = {}; streams = {}
    for suffix in ('stdout','stderr'):
        path=output/'private'/f'{ordinal:03d}-loopback-claude-canonical-body.{suffix}'
        before=body_plugins_identity(path.lstat()); pin=body_diagnostic_file(path,32768)
        raw=read(path,32768)
        need(pin == {'bytes':len(raw),'sha256':digest(raw)} and
             capture[suffix+'_bytes'] == len(raw) and capture[suffix+'_sha256'] == digest(raw) and
             body_plugins_identity(path.lstat()) == before, 'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE')
        population[suffix]={'identity':before,**pin}; streams[suffix]=raw
    path=output/'private/CLAUDE_BODY_RESULT.json'
    before=body_plugins_identity(path.lstat()); pin=body_diagnostic_file(path,32768,0o600); raw=read(path,32768)
    need(raw == streams['stdout'] and pin == {'bytes':len(raw),'sha256':digest(raw)} and
         digest(raw) == state['claude_validation']['result_sha256'] and
         body_canonical(body_json(raw,32768)) == body_canonical(state['claude']) and
         body_plugins_identity(path.lstat()) == before, 'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE')
    population['public_result']={'identity':before,**pin}
    return population


def receive_native_plugin_diagnostic(state, output, phase, utility):
    """Same-job failure-time receiving; changes only its diagnostic validation row."""
    need(phase in ('AFTER_COMMAND','FINAL'), 'PLUGIN_DIAGNOSTIC_PARENT_PHASE')
    validation = state.setdefault('claude_validation', {})
    previous = validation.get('native_plugin_diagnostic_receiving', {})
    phases = {key:previous.get('verified_phases', {}).get(key) is True for key in ('AFTER_COMMAND','FINAL')}
    result = {'schema':'dg17.claude.body-parent-native-plugin-diagnostic.v1', 'status':'UNRECEIVED',
        'reason':None, 'latest_phase':phase, 'verified_phases':phases,
        'fresh_parent_no_children':False, 'fresh_parent_echild':False,
        'outer_capture_bound':False, 'complete_native_capture_bound':False, 'provider_custody_bound':False,
        'source_runtime_startup_package_bookends_received':False, 'invocation_context_bound':False,
        'raw_stdout_received':False, 'projection_recomputed':False, 'public_projection_bound':False,
        'matches_initial_readback':False, 'raw_stdout_bytes':None, 'raw_stdout_sha256':None,
        'expected_context_sha256':None, 'projection_sha256':None, 'snapshot_sha256':None,
        'projection_status':None, 'projection_reason':None,
        'producer_custody_scope':'SOURCE_BOUND_RETAINED_PRODUCER_CUT_NOT_PARENT_HISTORICAL_OBSERVATION',
        'body_acceptance_from_diagnostics':False}
    validation['native_plugin_diagnostic_receiving'] = result
    first_failure = plugin_diagnostic_failure_snapshot(state)
    try:
        need(validation.get('valid') is True and validation.get('captured_result_matches') is True and
             state.get('active_command') is None and body_plugins_receiving_success(state,phase),
             'PLUGIN_DIAGNOSTIC_PARENT_PREMISES')
        need(utility.children() == [], 'PLUGIN_DIAGNOSTIC_PARENT_QUIESCENCE')
        body_diagnostic_quiescence()
        result.update(fresh_parent_no_children=True, fresh_parent_echild=True)
        outer_population = plugin_diagnostic_public_binding(state,output)
        result['outer_capture_bound'] = True
        public = state['claude']; plugin_diagnostic_bookends(public)
        root = output/'private/claude-canonical-body'; body_diagnostic_anchor(root)
        admission = body_plugins_admission_receiving(root,public,state['receipt'])
        need(admission.get('status') == 'RECEIVED' and all(admission.get(key) is True for key in (
            'native_capture_bound','provider_custody_bound','producer_quiescence_received','verified')),
            'PLUGIN_DIAGNOSTIC_ADMISSION_EVIDENCE')
        result.update(complete_native_capture_bound=True,provider_custody_bound=True,
            source_runtime_startup_package_bookends_received=True)
        population = {}
        def stable_private(name, maximum):
            path = root/name; identity = body_plugins_identity(path.lstat())
            need(identity['gid'] == os.getegid(), 'PLUGIN_DIAGNOSTIC_PRIVATE_IDENTITY')
            pin = body_diagnostic_file(path,maximum,0o600); raw = read(path,maximum)
            need(pin == {'bytes':len(raw),'sha256':digest(raw)} and identity == body_plugins_identity(path.lstat()),
                'PLUGIN_DIAGNOSTIC_PRIVATE_IDENTITY')
            population[name] = {'identity':identity,'bytes':len(raw),'sha256':digest(raw)}
            return raw
        invocation_raw = stable_private('NATIVE_INVOCATION.json',65536)
        invocation = body_json(invocation_raw,65536)
        session,cwd,plugin = body_invocation_receiving(root,output)
        need(invocation_raw == read(root/'NATIVE_INVOCATION.json',65536) and
             type(invocation) is dict and invocation.get('session_id') == session,
             'PLUGIN_DIAGNOSTIC_INVOCATION_CHANGED')
        result['invocation_context_bound'] = True
        stdout = stable_private('canonical-body.stdout',32768)
        command = public['commands'][0]
        need(type(command.get('stdout_bytes')) is int and len(stdout) == command['stdout_bytes'] and
             digest(stdout) == command.get('stdout_sha256'), 'PLUGIN_DIAGNOSTIC_STDOUT_CAPTURE_DIFFERS')
        projected = plugin_diagnostic_projection(stdout,session,str(cwd),str(plugin),PLUGIN_DIAGNOSTIC_MODEL)
        expected = public.get('native_plugin_identity_diagnostic')
        need(type(expected) is dict and len(body_canonical(expected)) <= 4096 and
             plugin_joint_projection_shape(expected) and plugin_joint_projection_shape(projected) and
             body_canonical(projected) == body_canonical(expected), 'PLUGIN_DIAGNOSTIC_PROJECTION_DIFFERS')
        result.update(raw_stdout_received=True,projection_recomputed=True,public_projection_bound=True,
            raw_stdout_bytes=len(stdout),raw_stdout_sha256=digest(stdout),
            expected_context_sha256=projected['expected_context_sha256'],
            projection_sha256=digest(body_canonical(projected)),projection_status=projected['status'],
            projection_reason=projected['reason'])
        # Fresh reopen/readback at each receiving phase, plus within-phase bookends.
        for name,row in population.items():
            path=root/name
            need(body_plugins_identity(path.lstat()) == row['identity'] and
                 body_diagnostic_file(path,row['bytes'],0o600) == {'bytes':row['bytes'],'sha256':row['sha256']} and
                 digest(read(path,row['bytes'])) == row['sha256'], 'PLUGIN_DIAGNOSTIC_PRIVATE_CHANGED')
        need(body_invocation_receiving(root,output) == (session,cwd,plugin), 'PLUGIN_DIAGNOSTIC_INVOCATION_CHANGED')
        need(body_plugins_admission_receiving(root,public,state['receipt']) == admission,
             'PLUGIN_DIAGNOSTIC_ADMISSION_CHANGED')
        need(plugin_diagnostic_public_binding(state,output) == outer_population,
             'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE')
        plugin_diagnostic_bookends(public)
        need(utility.children() == [], 'PLUGIN_DIAGNOSTIC_PARENT_QUIESCENCE')
        body_diagnostic_quiescence()
        snapshot = digest(body_canonical({'population':population,'outer_population':outer_population,'admission':admission,
            'projection':projected,'context_sha256':projected['expected_context_sha256']}))
        baseline = state.get('native_plugin_diagnostic_baseline_sha256')
        if baseline is None:
            need(phase == 'AFTER_COMMAND', 'PLUGIN_DIAGNOSTIC_FIRST_PHASE_MISSING')
            state['native_plugin_diagnostic_baseline_sha256'] = snapshot
        else:
            need(baseline == snapshot, 'PLUGIN_DIAGNOSTIC_CHANGED_SINCE_FIRST')
        phases[phase] = True
        result.update(status=('RECEIVED_DIAGNOSTIC' if projected['status'] == 'RECEIVED_PRE_PLUGIN_DIAGNOSTIC'
            else 'RECEIVED_UPSTREAM_REFUSAL'), matches_initial_readback=True,snapshot_sha256=snapshot)
    except BaseException as exc:
        allowed = {'PLUGIN_DIAGNOSTIC_PARENT_PREMISES','PLUGIN_DIAGNOSTIC_PARENT_QUIESCENCE',
            'PLUGIN_DIAGNOSTIC_OUTER_CAPTURE',
            'PLUGIN_DIAGNOSTIC_BOOKENDS','PLUGIN_DIAGNOSTIC_PROVIDER_COMPLETENESS',
            'PLUGIN_DIAGNOSTIC_ADMISSION_EVIDENCE','PLUGIN_DIAGNOSTIC_PRIVATE_IDENTITY',
            'PLUGIN_DIAGNOSTIC_INVOCATION_CHANGED','PLUGIN_DIAGNOSTIC_STDOUT_CAPTURE_DIFFERS',
            'PLUGIN_DIAGNOSTIC_PROJECTION_DIFFERS','PLUGIN_DIAGNOSTIC_PRIVATE_CHANGED',
            'PLUGIN_DIAGNOSTIC_ADMISSION_CHANGED','PLUGIN_DIAGNOSTIC_FIRST_PHASE_MISSING',
            'PLUGIN_DIAGNOSTIC_CHANGED_SINCE_FIRST'}
        result['reason'] = str(exc) if isinstance(exc,Refusal) and str(exc) in allowed else 'PRIVATE_EVIDENCE_UNAVAILABLE'
    # The function neither changes recognition/failure nor calls a late executable
    # gate. This assertion detects accidental future mutation of those owner fields.
    need(plugin_diagnostic_failure_snapshot(state) == first_failure,
        'PLUGIN_DIAGNOSTIC_FAILURE_PRECEDENCE_CHANGED')
    return result


PLUGIN_DIAGNOSTIC_PARENT_SCHEMA = json.loads('{"$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"body_acceptance_from_diagnostics":{"const":false},"complete_native_capture_bound":{"type":"boolean"},"expected_context_sha256":{"anyOf":[{"pattern":"\\\\A[0-9a-f]{64}\\\\Z","type":"string"},{"type":"null"}]},"fresh_parent_echild":{"type":"boolean"},"fresh_parent_no_children":{"type":"boolean"},"invocation_context_bound":{"type":"boolean"},"latest_phase":{"enum":["AFTER_COMMAND","FINAL"]},"matches_initial_readback":{"type":"boolean"},"outer_capture_bound":{"type":"boolean"},"producer_custody_scope":{"const":"SOURCE_BOUND_RETAINED_PRODUCER_CUT_NOT_PARENT_HISTORICAL_OBSERVATION"},"projection_reason":{"anyOf":[{"enum":["CHILD_EVENT_UNRECEIVED","CONFIG_IDENTITY_DIFFERS","CUSTODY_OR_BOOKEND_UNRECEIVED","EVENT_POPULATION_BOUND","EVENT_TYPE_UNRECEIVED","EXPECTED_CONTEXT_UNRECEIVED","INIT_RESULT_ORDER_UNRECEIVED","INPUT_BYTE_BOUND","JSON_ARRAY_BOUND","JSON_COMPLEXITY","JSON_DUPLICATE_KEY","JSON_NONFINITE","JSON_OBJECT_BOUND","JSON_STRING_ENCODING","JSON_TYPE_UNRECEIVED","JSON_UNRECEIVED","MCP_OR_PLUGIN_ERROR_PRESENT","NOT_ATTEMPTED","PUBLIC_BOUND_REFUSED","SESSION_DIFFERS","TOOL_SURFACE_DIFFERS"]},{"type":"null"}]},"projection_recomputed":{"type":"boolean"},"projection_sha256":{"anyOf":[{"pattern":"\\\\A[0-9a-f]{64}\\\\Z","type":"string"},{"type":"null"}]},"projection_status":{"anyOf":[{"enum":["UNRECEIVED","RECEIVED_PRE_PLUGIN_DIAGNOSTIC"]},{"type":"null"}]},"provider_custody_bound":{"type":"boolean"},"public_projection_bound":{"type":"boolean"},"raw_stdout_bytes":{"anyOf":[{"maximum":32768,"minimum":0,"type":"integer"},{"type":"null"}]},"raw_stdout_received":{"type":"boolean"},"raw_stdout_sha256":{"anyOf":[{"pattern":"\\\\A[0-9a-f]{64}\\\\Z","type":"string"},{"type":"null"}]},"reason":{"anyOf":[{"enum":["PLUGIN_DIAGNOSTIC_PARENT_PREMISES","PLUGIN_DIAGNOSTIC_PARENT_QUIESCENCE","PLUGIN_DIAGNOSTIC_OUTER_CAPTURE","PLUGIN_DIAGNOSTIC_BOOKENDS","PLUGIN_DIAGNOSTIC_PROVIDER_COMPLETENESS","PLUGIN_DIAGNOSTIC_ADMISSION_EVIDENCE","PLUGIN_DIAGNOSTIC_PRIVATE_IDENTITY","PLUGIN_DIAGNOSTIC_INVOCATION_CHANGED","PLUGIN_DIAGNOSTIC_STDOUT_CAPTURE_DIFFERS","PLUGIN_DIAGNOSTIC_PROJECTION_DIFFERS","PLUGIN_DIAGNOSTIC_PRIVATE_CHANGED","PLUGIN_DIAGNOSTIC_ADMISSION_CHANGED","PLUGIN_DIAGNOSTIC_FIRST_PHASE_MISSING","PLUGIN_DIAGNOSTIC_CHANGED_SINCE_FIRST","PRIVATE_EVIDENCE_UNAVAILABLE"]},{"type":"null"}]},"schema":{"const":"dg17.claude.body-parent-native-plugin-diagnostic.v1"},"snapshot_sha256":{"anyOf":[{"pattern":"\\\\A[0-9a-f]{64}\\\\Z","type":"string"},{"type":"null"}]},"source_runtime_startup_package_bookends_received":{"type":"boolean"},"status":{"enum":["UNRECEIVED","RECEIVED_DIAGNOSTIC","RECEIVED_UPSTREAM_REFUSAL"]},"verified_phases":{"additionalProperties":false,"properties":{"AFTER_COMMAND":{"type":"boolean"},"FINAL":{"type":"boolean"}},"required":["AFTER_COMMAND","FINAL"],"type":"object"}},"required":["schema","status","reason","latest_phase","verified_phases","fresh_parent_no_children","fresh_parent_echild","outer_capture_bound","complete_native_capture_bound","provider_custody_bound","source_runtime_startup_package_bookends_received","invocation_context_bound","raw_stdout_received","projection_recomputed","public_projection_bound","matches_initial_readback","raw_stdout_bytes","raw_stdout_sha256","expected_context_sha256","projection_sha256","snapshot_sha256","projection_status","projection_reason","producer_custody_scope","body_acceptance_from_diagnostics"],"title":"Same-job parent receiving of native plugin diagnostics only","type":"object"}')


def native_plugin_parent_success(state, phase):
    value = state.get('claude_validation',{}).get('native_plugin_diagnostic_receiving')
    if not catalogue_schema_matches(value,PLUGIN_DIAGNOSTIC_PARENT_SCHEMA): return False
    return (value.get('status') == 'RECEIVED_DIAGNOSTIC' and value.get('reason') is None and
        value.get('latest_phase') == phase and value.get('verified_phases',{}).get(phase) is True and
        value.get('projection_status') == 'RECEIVED_PRE_PLUGIN_DIAGNOSTIC' and value.get('projection_reason') is None and
        all(value.get(key) is True for key in ('fresh_parent_no_children','fresh_parent_echild',
            'outer_capture_bound','complete_native_capture_bound','provider_custody_bound',
            'source_runtime_startup_package_bookends_received','invocation_context_bound',
            'raw_stdout_received','projection_recomputed','public_projection_bound','matches_initial_readback')))


def native_plugin_child_success(value):
    diag = value.get('native_plugin_identity_diagnostic')
    return (type(diag) is dict and diag.get('schema') == PLUGIN_DIAGNOSTIC_SCHEMA and
        diag.get('status') == 'RECEIVED_PRE_PLUGIN_DIAGNOSTIC' and diag.get('reason') is None and
        diag.get('pre_plugin_envelope_received') is True and diag.get('original_equality') is True and
        diag.get('body_acceptance_from_diagnostics') is False)

def receive_claude(state, packet, raw):
    schema_raw = read(packet/'PUBLIC_RESULT_SCHEMA.json')
    state['claude_validation'] = {'valid':False,'schema_sha256':digest(schema_raw),
                                  'result_sha256':digest(raw),'result_bytes':len(raw)}
    value = body_json(raw,32768)
    need(catalogue_schema_matches(value,body_json(schema_raw,131072)), 'CLAUDE_BODY_RESULT_SCHEMA')
    need(plugin_joint_projection_shape(value.get('native_plugin_identity_diagnostic')), 'CLAUDE_BODY_RESULT_SCHEMA')
    state['claude'] = value
    state['claude_validation']['valid'] = True

def claude_success(value, uid, gid, receipt):
    if type(value) is not dict: return False
    exact = {'schema':'dg17.claude.canonical-body.v1',
             'status':'OBSERVED_CANONICAL_GOVERNOR_BODY_AND_ADVERTISED_ENTRIES',
             'control_source_commit':SOURCE,'control_source_tree':TREE,
             'package_source_commit':BODY_SOURCE,'package_source_tree':BODY_TREE,
             'package_archive_bytes':BODY_ARCHIVE_BYTES,'package_archive_sha256':BODY_ARCHIVE_SHA,
             'package_matrix_sha256':BODY_MATRIX_SHA,'layout':'CANONICAL_PLUGIN',
             'runtime_release_tag_declared':'v2.1.318','runtime_bytes':BINARY_BYTES,'runtime_sha256':BINARY_SHA,
             'runtime_archive_bytes':ARCHIVE_BYTES,'runtime_archive_sha256':ARCHIVE_SHA,
             'currentness_receipt_sha256':digest((receipt+'\n').encode()),
             'fresh_context_count':1,'native_sessions_started':1,'independent_receiving':'NOT_PERFORMED'}
    if any(type(value.get(k)) is not type(v) or value[k] != v for k,v in exact.items()): return False
    flags = ('currentness_before','currentness_after','control_source_before','control_source_after',
             'runtime_before','runtime_after','git_admission_unchanged','archive_before','archive_after',
             'package_before','package_after','startup_before','startup_after','scripted_provider',
             'parent_independent_receiving_required')
    if not all(value.get(k) is True for k in flags): return False
    false_flags = ('upstream_forwarding','authentic_inference_proven','native_all_five_full_bodies_received',
                   'genuine_child_route_received','persistent_installation_proven','desktop_qualification',
                   'original_acceptance_awarded')
    if not all(value.get(k) is False for k in false_flags) or value.get('failure') is not None or value.get('supplemental_failures') != []: return False
    offline = value.get('offline')
    if type(offline) is not dict or offline.get('uid') != uid or offline.get('gid') != gid or offline.get('external_routes') != 0: return False
    if not all(offline.get(k) is True for k in ('verified','namespace_differs_from_parent','only_loopback',
               'effective_permitted_ambient_capabilities_zero','no_new_privileges')): return False
    commands = value.get('commands')
    if type(commands) is not list or len(commands) != 1 or type(commands[0]) is not dict: return False
    row = commands[0]
    if row.get('name') != 'canonical-body' or type(row.get('returncode')) is not int or row['returncode'] != 0: return False
    if not all(row.get(k) is True for k in ('process_started','streams_complete','pidfd_acquired','private_streams_retained',
        'owned_cleanup_echild','source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')): return False
    if not all(row.get(k) is False for k in ('timeout','output_bound_exceeded','internal_failure','retention_failure')): return False
    if row.get('recognition_status') != 'BODY_AND_ENTRIES_RECEIVED' or row.get('recognition_code') is not None: return False
    if any(type(row.get(k+'_bytes')) is not int or not 0 <= row[k+'_bytes'] <= 32768 or
           type(row.get(k+'_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',row[k+'_sha256']) is None
           for k in ('stdout','stderr')): return False
    if row.get('stderr_present') is not (row['stderr_bytes'] > 0) or type(row.get('owned_reaped_status_count')) is not int or row['owned_reaped_status_count'] < 0: return False
    provider = value.get('provider_custody')
    if type(provider) is not dict or not all(provider.get(k) is True for k in ('started','thread_joined','all_owned_sockets_closed','verified','semantic_response_complete')): return False
    if provider.get('failure') is not None or provider.get('supplemental_failures') != [] or type(provider.get('semantic_request_count')) is not int or provider['semantic_request_count'] != 1: return False
    native = value.get('native_observation'); body = value.get('body_delivery')
    if (type(native) is not dict or native.get('status') != 'NATIVE_INIT_AND_TERMINAL_RECEIVED' or
        native.get('canonical_advertised_entries_exact') is not True): return False
    if native.get('expected_names_observed') != list(BODY_EXPECTED_NAMES) or native.get('unexpected_package_entry_count') != 0 or native.get('native_tool_calls') != 0 or native.get('child_events') != 0 or native.get('terminal_success') is not True: return False
    if (type(body) is not dict or body.get('status') != 'EXACT_CLIENT_USER_MESSAGE_BODY_OBSERVED' or
        body.get('source_file_bytes') != 21257 or body.get('source_file_sha256') != BODY_GOVERNOR_SHA or
        body.get('body_bytes') != 20431 or body.get('body_sha256') != BODY_RENDERED_SHA): return False
    if not body_plugins_child_success(value): return False
    if not native_plugin_child_success(value): return False
    cleanup = value.get('cleanup')
    if type(cleanup) is not dict or cleanup.get('private_seal_unchanged') is not True or cleanup.get('host_teardown_observed') is not False or cleanup.get('private_plaintext_policy') != 'RETAIN_UNTIL_HOST_TEARDOWN': return False
    if type(cleanup.get('private_evidence_seal_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',cleanup['private_evidence_seal_sha256']) is None: return False
    return all(cleanup.get(k) == {'no_owned_children_listed':True,'wait_echild':True,'verified':True}
               for k in ('after_close','after_seal'))

def body_invocation_receiving(root, output):
    value = body_json(read(root/'NATIVE_INVOCATION.json',65536),65536)
    need(type(value) is dict and set(value) == {'argv','session_id','cwd','provider_kind'} and
         value['provider_kind'] == 'LOCAL_SCRIPTED_NO_UPSTREAM' and type(value['session_id']) is str and
         re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',value['session_id']),
         'BODY_NATIVE_INVOCATION_SHAPE')
    session = value['session_id']; context = root/'context-canonical-body'
    cwd = context/'cwd'; plugin = root/'effective-plugin'
    prompt = '/implementaudit:implementaudit DG17_OPERATION_ID='+session+' Bounded native governor content delivery observation only. No child route or effects are requested.'
    argv = [str(output/'private/claude-input'),'--setting-sources','user','--settings',str(context/'selected-settings.json'),
            '--strict-mcp-config','--mcp-config',str(context/'empty-mcp.json'),'--no-chrome','--plugin-dir',str(plugin),
            '--print','--output-format','stream-json','--verbose','--max-turns','1','--tools','Skill',
            '--disallowedTools','mcp__*','--no-session-persistence','--permission-prompts','none',
            '--session-id',session,'--model','claude-sonnet-4-6',prompt]
    need(value['argv'] == argv and value['cwd'] == str(cwd), 'BODY_NATIVE_INVOCATION_DIFFERS')
    return session,cwd,plugin

def receive_claude_private(state, output, source):
    receive_body_diagnostics(state, output, 'PRIVATE_SUCCESS')
    need(body_diagnostics_success(state), 'BODY_DIAGNOSTIC_SUCCESS_PREMISES')
    receive_body_plugins(state,output,'PRIVATE_SUCCESS')
    need(body_plugins_receiving_success(state,'PRIVATE_SUCCESS'),'BODY_PLUGINS_SUCCESS_PREMISES')
    need(claude_success(state.get('claude'),os.getuid(),os.getgid(),state['receipt']),
         'BODY_PRIVATE_SUCCESS_PREMISES')
    packet = Path(__file__).absolute().parent
    root = output/'private/claude-canonical-body'
    body_owned_directory(root)
    seal_path = root/'PRIVATE_EVIDENCE_SEAL.json'
    need(stat.S_IMODE(seal_path.lstat().st_mode) == 0o600, 'BODY_PRIVATE_SEAL_MODE')
    seal_pin = body_owned_file(seal_path,262144); raw = read(seal_path,262144)
    need(seal_pin == {'bytes':len(raw),'sha256':digest(raw)} and
         digest(raw) == state['claude']['cleanup']['private_evidence_seal_sha256'], 'BODY_PRIVATE_SEAL_PIN')
    declared = body_json(raw,262144)
    need(type(declared) is dict and set(declared) == {'schema','members'} and
         declared['schema'] == 'dg17.claude.body-private-seal.v1' and type(declared['members']) is list and
         len(declared['members']) <= 512, 'BODY_PRIVATE_SEAL_SHAPE')
    observed = body_private_rows(root)
    need(body_canonical(observed) == body_canonical(declared['members']), 'BODY_PRIVATE_SEAL_POPULATION')
    governor, package_projection = body_package_receiving(packet,output)
    body_startup_receiving(output,state)
    session,cwd,plugin = body_invocation_receiving(root,output)
    for name in ('currentness-before','currentness-after'):
        need(read(root/(name+'.stdout'),32768) == (state['receipt']+'\n').encode() and
             read(root/(name+'.stderr'),32768) == b'', 'BODY_EXACT_RECEIPT_BINDING')
    before = body_json(read(root/'GIT_ADMISSION_BEFORE.json',262144),262144)
    after = body_json(read(root/'GIT_ADMISSION_AFTER.json',262144),262144)
    need(type(before) is dict and set(before) == {'resolver','git','libexec','helpers','system_config','home','source_store'} and
         body_canonical(before) == body_canonical(after) and
         body_canonical(before['source_store']) == body_canonical(state['currentness_store_before']['guard']),
         'BODY_GIT_STORE_BOOKENDS')
    selected = before['git']; admitted = state['host']['tools']['git']; system = before['system_config']
    need(type(selected) is dict and selected.get('resolved') == '/usr/bin/git' and
         selected.get('bytes') == admitted['bytes'] and selected.get('sha256') == admitted['sha256'], 'BODY_GIT_HOST_BINDING')
    need(type(system) is dict and system.get('present') is True and system.get('bytes') == 0 and
         system.get('sha256') == digest(b''), 'BODY_EMPTY_SYSTEM_CONFIG_BINDING')
    names = ['currentness-before','canonical-body','currentness-after']
    records = body_json(read(root/'COMMANDS.json',262144),262144)
    need(type(records) is list and len(records) == 3 and all(type(row) is dict for row in records) and
         [row.get('name') for row in records] == names, 'BODY_PRIVATE_COMMAND_POPULATION')
    products = []; flags = ('source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')
    for name,row in zip(names,records):
        captures = body_json(read(root/(name+'.capture.json'),65536),65536)
        need(type(captures) is list and len(captures) == 1 and claude_capture_base_shape(captures[0],name),
             'BODY_PRIVATE_CAPTURE_REQUIRED_FIELDS')
        base = captures[0]; extra = {'recognition_status','recognition_code',*flags} if name == 'canonical-body' else set()
        need(set(row) == set(base)|extra and claude_capture_base_shape({k:row[k] for k in base},name) and
             all(row[k] == v for k,v in base.items()), 'BODY_PRIVATE_CAPTURE_BINDING')
        for stream in ('stdout','stderr'):
            data = read(root/(name+'.'+stream),32768)
            need(row[stream+'_bytes'] == len(data) and row[stream+'_sha256'] == digest(data), 'BODY_PRIVATE_STREAM_BINDING')
        need(row['process_started'] is True and row['returncode'] == 0 and row['streams_complete'] is True and
             row['timeout'] is False and row['output_bound_exceeded'] is False and row['pidfd_acquired'] is True and
             row['internal_failure'] is None and row['private_streams_retained'] is True and
             row['retention_failure'] is False and row['cleanup']['echild'] is True, 'BODY_PRIVATE_CAPTURE_CUSTODY')
        if extra:
            need(row['recognition_status'] == 'BODY_AND_ENTRIES_RECEIVED' and row['recognition_code'] is None and
                 all(row[k] is True for k in flags), 'BODY_PRIVATE_ENRICHMENTS')
            public = {k:row[k] for k in ('name','returncode','stdout_bytes','stdout_sha256','stderr_bytes','stderr_sha256','recognition_status','recognition_code')}
            for key in ('process_started','streams_complete','timeout','output_bound_exceeded','pidfd_acquired',
                        'private_streams_retained','retention_failure',*flags): public[key] = row[key] is True
            public.update(internal_failure=row['internal_failure'] is not None,stderr_present=row['stderr_bytes'] > 0,
                owned_cleanup_echild=row['cleanup']['echild'] is True,owned_reaped_status_count=row['cleanup']['retained_status_count'],
                owned_statuses_sha256=row['cleanup']['retained_statuses_sha256'])
            products.append(public)
    need(products == state['claude']['commands'], 'BODY_PRIVATE_PUBLIC_CAPTURE_BINDING')
    semantic, protocol_projection = body_provider_receiving(root,state['claude'])
    body_projection = body_delivery_projection(semantic,governor,session)
    native_projection = body_native_projection(read(root/'canonical-body.stdout',32768),session,cwd,plugin)
    need(body_projection == state['claude']['body_delivery'] and native_projection == state['claude']['native_observation'],
         'BODY_PUBLIC_CONTENT_OR_NATIVE_PROJECTION_DIFFERS')
    need(body_private_rows(root) == observed and read(seal_path,262144) == raw,
         'BODY_PRIVATE_AFTER_RECEIVING_CHANGED')
    receive_body_plugins(state,output,'PRIVATE_SUCCESS')
    need(body_plugins_receiving_success(state,'PRIVATE_SUCCESS'),'BODY_PLUGINS_SUCCESS_PREMISES')
    state['claude_validation'].update(private_seal_verified_after_child_reaping=True,
        private_member_count=len(observed),same_receipt_private_readbacks_verified=True,
        git_private_bookends_verified=True,git_admission_identity_sha256=digest(json.dumps(before,sort_keys=True,separators=(',',':')).encode()),
        private_public_stream_and_command_bindings_verified=True,complete_package=package_projection,
        startup_policy_and_invocation_contract_verified=True,provider_receiving=protocol_projection,
        native_advertised_entries_independently_received=True,full_governor_user_body_independently_received=True)


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
def packet_check(packet):
    raw = read(packet/'INPUT_PINS.json'); need(digest(raw) == PINS_SHA, 'PACKET_UNSEALED_OR_CHANGED')
    pins = json.loads(raw)
    for name, row in pins.items():
        need(re.fullmatch(r'[A-Za-z0-9_.-]+', name) is not None, 'INPUT_PATH')
        content = read(packet/name)
        need(len(content) == row['bytes'] and digest(content) == row['sha256'], 'INPUT_PIN')
    body_archive_input(packet)
    return pins
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

def currentness_admission(state, source, output, u, label):
    """Data-only re-entry gate. Failure containment is distinct from cleanup."""
    expected_steps = {'initial-currentness':'require','before-runtime-acquisition':'runtime',
                      'after-runtime-acquisition':'runtime','before-claude':'claude',
                      'after-claude':'claude','before-receiving':'receive',
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
    late = label in ('after-claude','before-receiving','after-receiving','final-currentness')
    if label == 'final-currentness':
        need(state.get('completed') == list(STEPS) and state.get('bounded_receiving_complete') is True,
             'FINAL_CURRENTNESS_INCOMPLETE_RECEIVING')
    packet = Path(__file__).absolute().parent
    body_archive_input(packet)
    if late:
        need(any(row.get('name') == 'loopback-claude-canonical-body' for row in state['commands']),
             'CURRENTNESS_NATIVE_CAPTURE_MISSING')
        need(state.get('claude_validation',{}).get('valid') is True and
             state['claude_validation'].get('captured_result_matches') is True and
             claude_success(state.get('claude',{}),os.getuid(),os.getgid(),state['receipt']),
             'CURRENTNESS_CHILD_ROUTE_UNSOUND')
        raw = read(output/'private/CLAUDE_BODY_RESULT.json',32768)
        need(digest(raw) == state['claude_validation']['result_sha256'] and
             json.loads(raw,object_pairs_hook=unique_object) == state['claude'], 'CURRENTNESS_CHILD_RESULT_CHANGED')
        receive_claude_private(state,output,source)
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
        received_git = json.loads(read(output/'private/claude-canonical-body/GIT_ADMISSION_BEFORE.json',262144),
                                  object_pairs_hook=unique_object)
        need(store['guard'] == received_git.get('source_store'), 'CURRENTNESS_RECEIVED_STORE_DRIFT')
    for name in ('bash','env','git','python3'):
        path,observed_tool = u.trusted(name)
        need(path is not None and observed_tool == state['host']['tools'][name], 'CURRENTNESS_TOOL_CHANGED')
    if 'runtime' in state:
        binary = output/'private/claude-input'; info = binary.lstat()
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

def current(state, source, output, u, label):
    need(state.get('receipt') is not None, 'CURRENTNESS_NOT_ESTABLISHED')
    admission = currentness_admission(state,source,output,u,label)
    raw = owner(state, source, output, u, label, '--require-current-continuity', state['controller'])
    need(raw == (state['receipt']+'\n').encode(), 'CURRENTNESS_RECEIPT_DIFFERS')
    state['currentness'].append({'role': label, 'receipt_sha256': digest(raw), 'same_source_cwd': True, 'verified': True, 'pre_execution_admission':admission})
    save(output/'private/episode.json', state)
def acquire_runtime(output):
    archive = output/'private/claude.tar.gz'; started = time.monotonic(); count = 0; h = hashlib.sha256()
    with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as stream:
        while True:
            chunk = response.read(1048576)
            if not chunk: break
            count += len(chunk); need(count <= ARCHIVE_BYTES and time.monotonic()-started < 180, 'ARCHIVE_BOUND')
            h.update(chunk); stream.write(chunk)
    need(count == ARCHIVE_BYTES and h.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    binary = output/'private/claude-input'
    with tarfile.open(archive,'r:gz') as tar:
        members = tar.getmembers()
        need(len(members) == 1, 'ARCHIVE_MEMBERS')
        member = members[0]
        need(member.isreg() and member.name == 'claude' and member.size == BINARY_BYTES and member.mode == 0o755 and member.linkname == '' and member.pax_headers == {}, 'ARCHIVE_MEMBER_IDENTITY')
        count = 0
        with tar.extractfile(member) as inp, binary.open('xb') as out:
            while True:
                chunk = inp.read(1048576)
                if not chunk: break
                count += len(chunk); need(count <= BINARY_BYTES, 'ARCHIVE_BINARY_BOUND')
                out.write(chunk)
    need(stream_hash(binary) == (BINARY_BYTES,BINARY_SHA), 'BINARY_PIN')
    os.chmod(binary,0o700)
    info = binary.lstat()
    need(binary.resolve(strict=True) == binary and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid() and info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700, 'BINARY_OWNED_PHYSICAL_FILE')
    with binary.open('rb') as stream: header = stream.read(64)
    need(len(header) == 64 and header[:6] == b'\x7fELF\x02\x01' and int.from_bytes(header[18:20],'little') == 62, 'BINARY_ELF_X64')
    return {'archive_sha256':ARCHIVE_SHA,'archive_bytes':ARCHIVE_BYTES,'archive_member':'claude',
            'binary_sha256':BINARY_SHA,'binary_bytes':BINARY_BYTES,'release_tag_declared':'v2.1.318',
            'runtime_version_self_reported':False,'elf64_little_endian_x86_64':True,
            'input_retained_until_host_teardown':True,
            'parent_runtime_identity_horizon':'ACQUISITION_RECEIVE_AND_CURRENTNESS_ADMISSION'}

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
def capsule_recheck(state, u, phase):
    before = state['capsule_private']['host_before']; after = capsule_host_snapshot(state, u)
    equal = after == before
    state['capsule']['outside_rechecks'][phase] = {'unchanged': equal, 'identity_sha256': digest(encoded(after))}
    need(equal, 'CAPSULE_OUTSIDE_OR_UTILITY_CHANGED')
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
def launch_claude(state, source, output, packet, u):
    need(digest(CAPSULE_SCRIPT.encode()) == CAPSULE_SCRIPT_SHA and digest(CAPSULE_CODE.encode()) == CAPSULE_CODE_SHA, 'CAPSULE_LITERAL_PIN')
    host = capsule_host_snapshot(state, u)
    netns = host['parent_net_namespace']
    probe_args = ['--source',str(source),'--episode',str(output),'--binary',str(output/'private/claude-input'),
                  '--controller',state['controller'],'--receipt',state['receipt'],'--expected-uid',str(os.getuid()),
                  '--expected-gid',str(os.getgid()),'--parent-netns',netns,
                  '--canonical-archive',str(body_archive_input(packet)),'--package-matrix-pins',str(packet/'CANONICAL_PACKAGE_MATRIX.json')]
    child_argv = ['/usr/bin/python3','-I','-S','-B',str(packet/'claude_body_probe.py'),*probe_args]
    state['capsule_private'] = {'host_before':host,'child_argv_sha256':digest(encoded(child_argv))}
    state['capsule'] = {'profile':'PRIVATE_READONLY_VIEW_AND_LOOPBACK_ONLY_V3','status':'PREPARED_NOT_OBSERVED',
                        'qualification_scope':'CONSTRUCTED_PRIVATE_VIEW_NOT_STOCK_INSTALLATION_PATH_QUALIFICATION',
                        'targets':list(CAPSULE_TARGETS),'root_watchdog_seconds':165,'root_kill_after_seconds':5,
                        'root_script_sha256':CAPSULE_SCRIPT_SHA,'inline_code_sha256':CAPSULE_CODE_SHA,
                        'loopback_initializer_sha256':LOOPBACK_INITIALIZER_SHA,
                        'outside_before_sha256':digest(encoded(host)),'outside_rechecks':{},
                        'outside_system_gitconfig':host['outside']['/etc/gitconfig'],
                        'admitted_before':False,'before_after_equal':False,'admission_sha256':None,
                        'result_sha256':None,'before':None,'after':None,'child_returncode':None}
    save(output/'private/episode.json', state)
    argv = ['/usr/bin/sudo','-n','/usr/bin/timeout','--signal=TERM','--kill-after=5s','165s',
            '/usr/bin/unshare','--mount','--net','--propagation','private','--',
            '/usr/bin/bash','--noprofile','--norc','-c',CAPSULE_SCRIPT,'dg17-private-view',
            str(os.getuid()),str(os.getgid()),CAPSULE_CODE,
            str(output/'private/CAPSULE_ADMISSION.json'),str(output/'private/CAPSULE_RESULT.json'),
            host['parent_mount_namespace'],netns,str(packet/'claude_body_probe.py'),*probe_args]
    failure = None
    try: command(state, output, u, 'loopback-claude-canonical-body', argv, seconds=180)
    except BaseException as exc: failure = exc
    for label, action in (('capsule-outside-after',lambda:capsule_recheck(state,u,'after-command')),
                          ('capsule-proof-after',lambda:receive_capsule(state,output))):
        try: action()
        except BaseException as exc:
            observe_capsule_failure(state,label,exc)
            if failure is None: failure = exc
    try:
        if (output/'private/CLAUDE_BODY_RESULT.json').exists():
            receive_claude(state, packet, read(output/'private/CLAUDE_BODY_RESULT.json', 32768))
            record = state['commands'][-1]
            state['claude_validation']['captured_result_matches'] = False
            if record.get('name') == 'loopback-claude-canonical-body' and record.get('streams_complete') is True:
                captured_raw = read(output/'private'/f'{len(state["commands"]):03d}-loopback-claude-canonical-body.stdout',32768)
                need(captured_raw == read(output/'private/CLAUDE_BODY_RESULT.json',32768), 'CLAUDE_CAPTURE_DIFFERS')
                captured = json.loads(captured_raw, object_pairs_hook=unique_object)
                need(catalogue_schema_matches(captured, json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'), object_pairs_hook=unique_object)) and captured == state['claude'], 'CLAUDE_CAPTURE_DIFFERS')
                need(plugin_joint_projection_shape(captured.get('native_plugin_identity_diagnostic')), 'CLAUDE_CAPTURE_DIFFERS')
                state['claude_validation']['captured_result_matches'] = True
                state['claude_validation']['child_success_claimed'] = claude_success(state['claude'],os.getuid(),os.getgid(),state['receipt'])
                receive_body_diagnostics(state, output, 'AFTER_COMMAND')
                receive_body_plugins(state, output, 'AFTER_COMMAND')
                receive_native_plugin_diagnostic(state, output, 'AFTER_COMMAND', u)
    except BaseException as exc:
        observe_capsule_failure(state,'claude-receiving',exc)
        if failure is None: failure = exc
    if failure is not None: raise failure
    need(body_plugins_receiving_success(state,'AFTER_COMMAND'),'BODY_PLUGINS_SUCCESS_PREMISES')
    need(native_plugin_parent_success(state,'AFTER_COMMAND'),'NATIVE_PLUGIN_DIAGNOSTIC_SUCCESS_PREMISES')

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
        tools['sudo'] = {'canonical': str(sudo), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True, 'mode': '04755', 'admitted_effect': 'ROOT_WATCHDOG_PRIVATE_MOUNT_AND_NETWORK_NAMESPACES_FIXED_READONLY_VIEW_AND_LOOPBACK_ONLY_UP_THEN_DROP_UID_GID_NO_NEW_PRIVILEGES'}
        state['host'] = {'platform': platform.system(), 'kernel': platform.release(), 'python': list(sys.version_info[:3]), 'uid': os.getuid(), 'gid': os.getgid(), 'tools': tools, 'upstream_provider_calls':0,'selected_local_scripted_provider_sessions':1}
        state['source_before'] = source_check(source, packet)
        prior_component(state, source, 'prepare')
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
        current(state, source, output, u, 'after-runtime-acquisition')
    elif step == 'claude':
        current(state, source, output, u, 'before-claude')
        launch_claude(state, source, output, packet, u)
        current(state, source, output, u, 'after-claude')
    elif step == 'receive':
        current(state, source, output, u, 'before-receiving')
        prior_component(state, source, 'receive')
        receive_capsule(state, output)
        capsule_recheck(state, u, 'receive')
        need(state.get('claude_validation', {}).get('valid') is True and state['claude_validation'].get('captured_result_matches') is True and claude_success(state.get('claude', {}),os.getuid(),os.getgid(),state['receipt']), 'CLAUDE_NOT_RECEIVED')
        need(stream_hash(output/'private/claude-input') == (BINARY_BYTES,BINARY_SHA), 'RECEIVED_RUNTIME_CHANGED')
        receive_claude_private(state,output,source)
        state['claude_validation']['semantic_receiving_passed'] = True
        state['source_after'] = source_check(source, packet)
        need(state['source_after'] == state['source_before'] and canonical_hashes(source, state) == state['canonical_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
        current(state, source, output, u, 'after-receiving')
        state['bounded_receiving_complete'] = True
    else: raise Refusal('UNKNOWN_STEP')

def export(state, output, packet):
    diagnostic_receipt = state.get('claude_validation',{}).get('native_plugin_diagnostic_receiving')
    if diagnostic_receipt is not None:
        need(catalogue_schema_matches(diagnostic_receipt,PLUGIN_DIAGNOSTIC_PARENT_SCHEMA),
             'NATIVE_PLUGIN_DIAGNOSTIC_PUBLIC_SCHEMA')
    if 'claude' in state:
        try:
            need(catalogue_schema_matches(state['claude'], json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))), 'CLAUDE_EXPORT_SCHEMA')
            need(plugin_joint_projection_shape(state['claude'].get('native_plugin_identity_diagnostic')), 'CLAUDE_EXPORT_SCHEMA')
        except BaseException as exc:
            state.pop('claude', None); state.setdefault('claude_validation',{})['valid'] = False; state['failed'] = True; state['bounded_receiving_complete'] = False
            state['failures'].append({'step': 'export', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
    docs = {
        'RESULT.json': {'schema': 'dg17.isolated-claude-body-hosted-result.v1', 'context': state['context'], 'completed': state['completed'], 'failed': state['failed'], 'bounded_receiving_complete': state.get('bounded_receiving_complete', False), 'claude_validation': state.get('claude_validation'), 'local_currentness_transfer': False, 'original_acceptance': False, 'whole_T12': False, 'whole_T14': False, 'new_original_awards': []},
        'SOURCE.json': {'before': state.get('source_before'), 'after': state.get('source_after'), 'canonical_unchanged': state.get('canonical_unchanged')},
        'HOST.json': {'host': state.get('host'), 'runtime': state.get('runtime'), 'capsule': state.get('capsule')},
        'CURRENTNESS.json': {'checks': state['currentness'], 'reads': state['reads'], 'local_or_future_transfer': False},
        'PREDICATES.json': state.get('predicates', {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],'source_closure':{'prepare':False,'receive':False,'final':False}}),
        'CLAUDE_BODY.json': state.get('claude', {'status': 'INVALID_RESULT_SCHEMA' if state.get('claude_validation',{}).get('valid') is False else 'NOT_COMPLETED'}),
        'CLEANUP.json': {'commands': state['commands'], 'active_step': state.get('active_step'), 'active_command': state.get('active_command'), 'all_recorded_commands_reaped': all(x.get('cleanup', {}).get('echild') is True for x in state['commands']), 'private_roots_retained_until_disposable_host_teardown': True},
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
                capsule_recheck(state, u, 'final')
                receive_capsule(state, output)
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False
                observe_capsule_failure(state, 'capsule-final', exc)
        if state.get('claude_validation', {}).get('valid') is True and state['claude_validation'].get('captured_result_matches') is True:
            receive_body_diagnostics(state, output, 'FINAL')
            receive_body_plugins(state, output, 'FINAL')
            receive_native_plugin_diagnostic(state, output, 'FINAL', u)
            if state.get('failed') is False and not body_plugins_receiving_success(state,'FINAL'):
                state['failed'] = True; state['bounded_receiving_complete'] = False
                code = 'BODY_PLUGINS_FINAL_UNRECEIVED'
                state['failures'].append({'step':'plugins-final','exception_type':'Refusal',
                    'message_sha256':digest(code.encode()),'message_bytes':len(code)})
            if state.get('failed') is False and not body_diagnostics_success(state):
                state['failed'] = True; state['bounded_receiving_complete'] = False
                code = 'BODY_DIAGNOSTIC_FINAL_UNRECEIVED'
                state['failures'].append({'step':'diagnostic-final', 'exception_type':'Refusal',
                                          'message_sha256':digest(code.encode()), 'message_bytes':len(code)})
            if state.get('failed') is False and not native_plugin_parent_success(state,'FINAL'):
                state['failed'] = True; state['bounded_receiving_complete'] = False
                code = 'NATIVE_PLUGIN_DIAGNOSTIC_FINAL_UNRECEIVED'
                state['failures'].append({'step':'native-plugin-diagnostic-final','exception_type':'Refusal',
                    'message_sha256':digest(code.encode()),'message_bytes':len(code)})
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
                    need(digest(read(output/'private/CLAUDE_BODY_RESULT.json',32768)) == state['claude_validation']['result_sha256'] and claude_success(state['claude'],os.getuid(),os.getgid(),state['receipt']), 'FINAL_CLAUDE_RESULT_DRIFT')
                    receive_claude_private(state,output,source)
                    state['claude_validation']['final_private_seal_verified'] = True
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
    try: sys.exit(main())
    except BaseException as exc:
        if isinstance(exc, SystemExit): raise
        print(json.dumps({'status': 'BOOTSTRAP_REFUSED', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode())})); sys.exit(1)
