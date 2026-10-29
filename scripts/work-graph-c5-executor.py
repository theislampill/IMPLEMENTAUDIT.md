#!/usr/bin/env python3
"""Separate fixed genuine-C5 execution owner; live gate, no native authority.

PROPOSAL ONLY: this source has not executed. The exact loader and selection
buffers must be frozen and independently qualified before create/run is exposed.
Original commands, package programs, provider bytes and oracle values are not
replaced. The new fixed image assigns original mktemp/clone/build writes to the
existing 512 MiB private-work allocation and keeps /tmp at 32 MiB. That explicit
C5 placement policy needs execution qualification; it is not a larger scratch
allocation. Imported JSON never constructs or restores this live session.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import resource
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import zlib

PROFILE = 'FIXED_GENUINE_C5_PRODUCER_EFFECT_ORIGINAL48_V1'
BOOTSTRAP_SCHEMA = 'implementaudit.c5-execution-bootstrap.v1'
BOOTSTRAP_REPLY = 'implementaudit.c5-execution-bootstrap-release.v1'
SOURCE_MOUNT, WORK_MOUNT, SCRATCH_MOUNT = '/work', '/c5-work', '/tmp'
EXECUTOR = 'scripts/work-graph-c5-executor.py'
MAX_HEADER = 4 * 1024**2


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode() + b'\n'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_uid, info.st_gid]


def anchor(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_uid, info.st_gid]


def send(fd, raw):
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        need(written > 0, 'C5 bootstrap channel write made no progress')
        view = view[written:]


def read_fd(fd, count):
    need(type(count) is int and 0 <= count <= MAX_HEADER, 'C5 bootstrap message exceeds fixed bound')
    data = bytearray()
    while len(data) < count:
        piece = os.read(fd, min(65536, count - len(data)))
        need(bool(piece), 'C5 bootstrap channel closed before release')
        data.extend(piece)
    return bytes(data)


def bootstrap():
    """Fixed acquired-image bootstrap; preserve only the owned live channel."""
    need(sys.argv[1:] == ['--c5-bootstrap'], 'C5 bootstrap argv differs')
    raw = Path('/profile/c5-execution.json').read_bytes()
    need(0 < len(raw) <= MAX_HEADER, 'C5 bootstrap configuration exceeds bound')
    spec = json.loads(raw)
    need(encode(spec) == raw and spec['schema'] == 'implementaudit.c5-execution-image.v1',
         'C5 bootstrap image configuration differs')
    fd = spec['gate_fd']
    need(type(fd) is int and 3 <= fd < spec['limits']['descriptors']
         and stat.S_ISSOCK(os.fstat(fd).st_mode), 'C5 bootstrap inherited channel is absent')
    need(dict(os.environ) == spec['environment'], 'C5 image environment differs')
    need(os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 0,
         'C5 image identity does not match the captured NSS profile')
    need(os.getcwd() == SOURCE_MOUNT, 'C5 bootstrap cwd differs')
    for which, key in ((resource.RLIMIT_CPU,'cpu_seconds'),(resource.RLIMIT_AS,'address_bytes'),
                       (resource.RLIMIT_FSIZE,'file_bytes'),(resource.RLIMIT_NOFILE,'descriptors')):
        need(resource.getrlimit(which) == (spec['limits'][key],) * 2, 'C5 inherited process bound differs')
    os.closerange(3, fd)
    os.closerange(fd + 1, spec['limits']['descriptors'])
    os.set_inheritable(fd, True)
    os.umask(0o022)
    observations = {}
    for name, wanted in spec['startup_files'].items():
        path = Path(name)
        info = path.stat()
        need(stat.S_ISREG(info.st_mode), 'C5 startup input is not an ordinary file')
        digest, size = hashlib.sha256(), 0
        with path.open('rb') as stream:
            while piece := stream.read(65536):
                size += len(piece)
                need(size <= wanted['bytes'], 'C5 startup input exceeds captured length')
                digest.update(piece)
        value = dict(bytes=size, sha256=digest.hexdigest(), mode=stat.S_IMODE(info.st_mode),
                     resolved=str(path.resolve(strict=True)))
        need(value == wanted, 'C5 startup input bytes/mode/alias differ: ' + name)
        observations[name] = value
    for name, target in spec['runtime_links'].items():
        need(os.readlink(name) == target, 'C5 runtime link differs: ' + name)
    directory_observations={}
    for name,wanted in spec['image_directories'].items():
        info=Path(name).lstat()
        need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode)==wanted['mode'],
             'C5 image directory type or mode differs: '+name)
        names=[]
        with os.scandir(name) as entries:
            for entry in entries:
                names.append(entry.name)
                need(len(names)<=len(wanted['names']),'C5 image namespace gained an unselected entry')
        value=dict(mode=stat.S_IMODE(info.st_mode),names=sorted(names))
        need(value==wanted,'C5 complete selected image namespace differs: '+name)
        directory_observations[name]=value
    null=Path('/dev/null').stat()
    need(stat.S_ISCHR(null.st_mode) and os.major(null.st_rdev)==1 and os.minor(null.st_rdev)==3,
         'C5 isolated null device differs')
    for name in spec['required_absent']:
        need(not Path(name).exists() and not Path(name).is_symlink(), 'C5 absent startup selector appeared')
    for name in (WORK_MOUNT, SCRATCH_MOUNT):
        fs = os.statvfs(name)
        expected = spec['limits']['work_bytes' if name == WORK_MOUNT else 'scratch_bytes']
        need(fs.f_blocks * fs.f_frsize == expected, 'C5 private allocation differs: ' + name)
    need(os.statvfs(SOURCE_MOUNT).f_flag & os.ST_RDONLY, 'C5 source stage is writable')
    need(os.statvfs('/').f_flag & os.ST_RDONLY, 'C5 base image is writable')
    status = Path('/proc/self/status').read_text('ascii')
    fields = {line.split(':',1)[0]:line.split(':',1)[1].strip() for line in status.splitlines() if ':' in line}
    need(fields.get('CapEff') == '0000000000000000', 'C5 bootstrap retained capabilities')
    namespace = os.readlink('/proc/self/ns/pid')
    need(namespace != spec['host_pid_namespace'], 'C5 image shares the host PID namespace')
    message = dict(schema=BOOTSTRAP_SCHEMA, image_sha256=sha(raw), actual_pid=os.getpid(),
        actual_pid_namespace=namespace, uid=os.getuid(), gid=os.getgid(), cap_eff=fields['CapEff'],
        startup_files=observations, image_directories=directory_observations, private_work_bytes=spec['limits']['work_bytes'],
        scratch_bytes=spec['limits']['scratch_bytes'], source_readonly=True, root_readonly=True,
        retained_descriptor=fd, authority='NONE')
    data = encode(message)
    need(len(data) <= MAX_HEADER, 'C5 bootstrap observation exceeds bound')
    send(fd, len(data).to_bytes(8,'big') + data)
    size = int.from_bytes(read_fd(fd, 8), 'big')
    reply = json.loads(read_fd(fd, size))
    need(reply == dict(schema=BOOTSTRAP_REPLY, image_sha256=sha(raw), accepted=True),
         'C5 outer owner did not release the actual bootstrap')
    os.execv('/usr/bin/bash', ['bash', 'tests/reproducible-release-asset.test.sh'])


if __name__ == '__main__':
    bootstrap()
    raise SystemExit('C5 bootstrap returned without exec')

_CAPTURE = globals().pop('_R0035_C5_EXECUTOR_CAPTURE', None)
need(type(_CAPTURE) is dict and set(_CAPTURE) == {'prefix','base','provider','gate','qualifier','sources','check','root','selection'},
     'C5 executor requires its complete separate fixed captured-source owner')
P, B, D, G, Q = (_CAPTURE[name] for name in ('prefix','base','provider','gate','qualifier'))
SOURCES, CHECK, ENGINE_ROOT, SPEC = (_CAPTURE[name] for name in ('sources','check','root','selection'))
need(SPEC.get('profile') in (PROFILE, 'FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1', 'FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1'),
     'Unsupported fixed C5 execution profile')
PROFILE = SPEC['profile']
# The current prefix owner remains the one source of these production limits.
_LIMIT_OWNER = P.bind_session(Q.VerifierTaskSession, Q.WG, ENGINE_ROOT,
                             SOURCES['scripts/qualify-work-graph-prefix.py'][0])
LIMITS = dict(_LIMIT_OWNER.LIMITS)
SECCOMP = bytes(Q.VerifierTaskSession.SECCOMP)


class CapturedSourceStage:
    """Complete ordinary source, no projection, with live descriptor custody.

    This is a private pathname bind from captured bytes. It does not claim
    that bubblewrap binds only descriptors. Full bytes are checked before/after;
    file/ancestor/name identities remain checked during all live handoffs.
    """
    def __init__(self, parent, state, objects, reserve):
        self.closed, self.fds, self.members, self.ancestors = False, [], {}, []
        self.state, self.objects = state, objects
        self.root = Path(parent) / 'source-stage'
        need(not self.root.exists() and not self.root.is_symlink(), 'C5 source stage is not fresh')
        self.root.mkdir(mode=0o755)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        def hold(fd):
            self.fds.append(fd)
            need(fd < LIMITS['descriptors'], 'C5 source descriptor bound exceeded')
            return fd
        try:
            fd = hold(os.open('/', flags))
            current = Path('/')
            self.ancestors.append((None,'/',fd,anchor(os.fstat(fd))))
            for name in self.root.parts[1:]:
                previous = fd
                fd = hold(os.open(name, flags, dir_fd=previous))
                current /= name
                self.ancestors.append((previous,name,fd,anchor(os.fstat(fd))))
            self.members['.'] = (fd, None, None, 'directory')
            directories = state['directories']
            need('.' in directories and directories['.'] == 0o755, 'C5 source state lacks its supported complete root')
            os.fchmod(fd, directories['.'])
            self.ancestors[-1] = (*self.ancestors[-1][:3], anchor(os.fstat(fd)))
            for name in sorted(set(directories)-{'.'}, key=lambda value:(value.count('/'),value)):
                parent_name = str(PurePosixPath(name).parent)
                parent_fd = self.members[parent_name][0]
                leaf = PurePosixPath(name).name
                mode = directories[name]
                need(mode == 0o755, 'C5 private source directory mode is unsupported')
                os.mkdir(leaf, mode, dir_fd=parent_fd)
                child = hold(os.open(leaf, flags, dir_fd=parent_fd))
                os.fchmod(child, mode)
                self.members[name] = (child, parent_fd, leaf, 'directory')
            for name, row in sorted(state['files'].items()):
                raw = objects[row['sha256']]
                need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'C5 source object unavailable')
                reserve(len(raw), 'private source-stage file')
                parent_fd = self.members[str(PurePosixPath(name).parent)][0]
                leaf = PurePosixPath(name).name
                fd = os.open(leaf, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,
                             row['mode'], dir_fd=parent_fd)
                try:
                    send(fd, raw)
                    os.fchmod(fd, row['mode'])
                    os.fsync(fd)
                finally:
                    os.close(fd)
                child = hold(os.open(leaf, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC, dir_fd=parent_fd))
                self.members[name] = (child,parent_fd,leaf,'file')
            self.stamps = {name:stamp(os.fstat(row[0])) for name,row in self.members.items()}
            self.names = {name:sorted(PurePosixPath(member).name for member in self.members
                if member != name and str(PurePosixPath(member).parent) == name) for name in directories}
            self.check(rehash=True)
        except BaseException:
            self.close()
            raise

    def check(self, rehash=False):
        need(not self.closed, 'C5 private source custody is closed')
        for parent,name,fd,expected in self.ancestors:
            need(anchor(os.fstat(fd)) == expected == anchor(os.stat(name,dir_fd=parent,follow_symlinks=False)),
                 'C5 source stage ancestor changed')
        for name,(fd,parent,leaf,kind) in self.members.items():
            expected = self.stamps[name]
            need(stamp(os.fstat(fd)) == expected and not os.listxattr(fd), 'C5 source stage descriptor changed')
            if parent is not None:
                need(stamp(os.stat(leaf,dir_fd=parent,follow_symlinks=False)) == expected, 'C5 staged source name changed')
            if kind == 'directory':
                need(stat.S_IMODE(expected[2]) == self.state['directories'][name], 'C5 staged directory mode changed')
                need(sorted(os.listdir(fd)) == self.names[name], 'C5 staged source population changed')
            else:
                row = self.state['files'][name]
                need(expected[3] == 1 and stat.S_IMODE(expected[2]) == row['mode'], 'C5 staged file mode/links changed')
                if rehash:
                    digest, offset = hashlib.sha256(), 0
                    while piece := os.pread(fd, min(65536,row['bytes']+1-offset), offset):
                        offset += len(piece)
                        need(offset <= row['bytes'], 'C5 staged file grew')
                        digest.update(piece)
                    need(offset == row['bytes'] and digest.hexdigest() == row['sha256'], 'C5 staged bytes changed')
            need(stamp(os.fstat(fd)) == expected, 'C5 source changed during stage readback')
        return dict(files=len(self.state['files']),directories=len(self.state['directories']),
            file_bytes=sum(row['bytes'] for row in self.state['files'].values()),
            held_descriptors=len(self.fds),representation='FULL_CAPTURED_SOURCE_READ_ONLY_PRIVATE_PATHNAME_BIND',authority='NONE')

    def close(self):
        for fd in reversed(self.fds):
            os.close(fd)
        self.fds.clear()
        self.closed = True


def virtual_resolve(path, links):
    """Resolve only the finite acquired image; never follow a host link here."""
    need(type(path) is str and path.startswith('/') and '\x00' not in path, 'Invalid C5 image path')
    pending, current, followed = path.split('/')[1:], [], 0
    while pending:
        part = pending.pop(0)
        if part in ('','.'):
            continue
        if part == '..':
            need(bool(current), 'C5 runtime alias escapes root')
            current.pop()
            continue
        key = '/' + '/'.join([*current,part])
        if key in links:
            followed += 1
            need(followed <= 64, 'C5 runtime alias cycle or excessive depth')
            target = links[key]
            if target.startswith('/'):
                current = []
            pending = target.split('/') + pending
        else:
            current.append(part)
    return '/' + '/'.join(current)


def runtime_topology(runtime):
    """Observe only path hops needed to reach the already selected data files.

    The base input owner records nominal aliases and final file identities. Its
    records do not necessarily include intermediate target links (the retained
    awk record is one exact example). This separate execution owner closes those
    links with no-follow directory custody and preserves the same final bytes.
    It never selects an additional regular file through this operation.
    """
    selected = dict(runtime['files'])
    for name,row in runtime['directories'].items():
        selected[name] = dict(kind='DIRECTORY',resolved=name,identity=row['identity'])
    provider = runtime['provider']['installation']
    for name,row in provider['directories'].items():
        selected[str(D.VENV/name)] = row['observation']
    for name,row in provider['links'].items():
        selected[str(D.VENV/name)] = row
    result = dict(selected={},links={},directories={})
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    def record(group,name,value):
        need(name not in result[group] or result[group][name] == value,
             'C5 runtime path observation changed during acquisition')
        result[group][name] = value
        need(len(result['selected'])+len(result['links'])+len(result['directories']) <= P.RUNTIME_BOUNDS['entries'],
             'C5 complete path observation exceeds inherited runtime population bound')
    for name,wanted in sorted(selected.items()):
        path = PurePosixPath(name)
        need(path.is_absolute() and '..' not in path.parts and len(path.parts) <= P.RUNTIME_BOUNDS['depth']+1,
             'C5 selected runtime path exceeds its fixed bound')
        fds = []
        observations = []
        rootfd = os.open('/',flags)
        fds.append(rootfd)
        stack = [rootfd]
        current = []
        pending = list(path.parts[1:])
        followed = 0
        try:
            root_info = os.fstat(rootfd)
            record('directories','/',stamp(root_info))
            observations.append((None,'/',rootfd,stamp(root_info)))
            terminal = root_info
            while pending:
                part = pending.pop(0)
                if part in ('','.'):
                    continue
                if part == '..':
                    need(bool(current),'C5 runtime alias escapes its image root')
                    current.pop();stack.pop()
                    terminal=os.fstat(stack[-1])
                    continue
                need(len(current) < P.RUNTIME_BOUNDS['depth'],'C5 physical alias traversal exceeds inherited depth')
                parent = stack[-1]
                info = os.stat(part,dir_fd=parent,follow_symlinks=False)
                physical = '/' + '/'.join([*current,part])
                if stat.S_ISLNK(info.st_mode):
                    followed += 1
                    need(followed <= 64,'C5 runtime alias cycle or excessive depth')
                    target = os.readlink(part,dir_fd=parent)
                    need(target and '\x00' not in target and len(target.encode()) <= 4096,
                         'C5 runtime alias target exceeds fixed path bound')
                    need(stamp(os.stat(part,dir_fd=parent,follow_symlinks=False)) == stamp(info),
                         'C5 runtime link changed while reading its target')
                    record('links',physical,dict(identity=stamp(info),target=target))
                    observations.append((parent,part,None,stamp(info)))
                    if target.startswith('/'):
                        current=[];stack=[rootfd];terminal=os.fstat(rootfd)
                    pending=target.split('/')+pending
                    continue
                current.append(part)
                terminal=info
                if stat.S_ISDIR(info.st_mode):
                    child=os.open(part,flags,dir_fd=parent)
                    fds.append(child)
                    need(stamp(os.fstat(child)) == stamp(info) and not os.listxattr(child),
                         'C5 runtime directory changed or has extended metadata')
                    stack.append(child)
                    record('directories',physical,stamp(info))
                    observations.append((parent,part,child,stamp(info)))
                else:
                    need(not pending and stat.S_ISREG(info.st_mode), 'C5 runtime traversal reached an unsupported member')
                    observations.append((parent,part,None,stamp(info)))
            resolved='/'+'/'.join(current)
            need(resolved == wanted['resolved'] and P.identity(terminal) == wanted['identity'],
                 'C5 physical topology differs from its already selected target: '+name)
            need((wanted['kind']=='FILE' and stat.S_ISREG(terminal.st_mode))
                 or (wanted['kind']=='DIRECTORY' and stat.S_ISDIR(terminal.st_mode)),
                 'C5 topology target type differs from its selected input')
            for parent,part,fd,expected in observations:
                need(stamp(os.stat(part,dir_fd=parent,follow_symlinks=False)) == expected,
                     'C5 runtime path hop changed during complete traversal')
                if fd is not None:
                    need(stamp(os.fstat(fd)) == expected,'C5 runtime directory descriptor changed')
            record('selected',name,dict(kind=wanted['kind'],resolved=resolved))
        finally:
            for fd in reversed(fds):os.close(fd)
    return result


def runtime_layout(runtime,topology):
    """Preserve every selected spelling and all actual intermediate link hops."""
    logical = runtime['files']
    links = {name:row['target'] for name,row in topology['links'].items()}
    files = {}
    for name,row in logical.items():
        resolved = virtual_resolve(name,links)
        need(resolved == row['resolved'], 'C5 image link layout differs from actual selector: ' + name)
        descriptor = {key:row[key] for key in ('bytes','sha256','mode')}
        need(resolved not in files or files[resolved] == descriptor, 'C5 resolved runtime bytes disagree')
        files[resolved] = descriptor
    if PROFILE in ('FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1', 'FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1'):
        selected_paths = set(logical) | set(files) | set(links)
        need(all(not PurePosixPath(name).is_relative_to(mount)
                 for name in selected_paths for mount in (SOURCE_MOUNT, WORK_MOUNT, SCRATCH_MOUNT)),
             'C5 selected runtime input overlaps a later private mount')
    directories = {name:stat.S_IMODE(observed[2]) for name,observed in topology['directories'].items()}
    for name in ('/','/work','/c5-work','/tmp','/dev','/proc','/profile'):
        directories.setdefault(name,0o755)
    for name in set(files) | set(links):
        for parent in PurePosixPath(name).parents:directories.setdefault(str(parent),0o755)
    need(not set(files)&set(links) and not (set(files)|set(links))&set(directories),
         'C5 runtime files, aliases and directories overlap')
    # Each closed source profile preserves its actual provider ancestry. These
    # fixed policies add no paths or caller-selected directory exceptions.
    policy = SPEC['directory_mode_policy']
    expected_policy = ({'default':0o755,'exceptions':{'/home/agent':0o750}}
        if PROFILE == 'FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1' else {'default':0o755,'exceptions':{}}
        if PROFILE == 'FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1'
        else {'default':0o755,'exceptions':{'/workspace':0o777,'/workspace/scratch':0o700}})
    need(policy == expected_policy,
         'C5 selected directory mode policy differs from its fixed profile')
    need(set(policy['exceptions']) <= set(topology['directories']),
         'C5 fixed mode exception lacks its actual captured directory')
    need(all(type(mode) is int and mode == policy['exceptions'].get(name,policy['default'])
             for name,mode in directories.items()),
         'C5 selected image directory mode differs from its fixed profile')
    need(len(files)+len(links)+len(directories) <= P.RUNTIME_BOUNDS['entries'], 'C5 image population exceeds inherited runtime bound')
    return dict(files=files,links=links,directories=dict(sorted(directories.items(),key=lambda item:(item[0].count('/'),item[0]))),
        observed_logical_files=len(logical),canonical_data_files=len(files),
        semantics='ALL_SELECTED_RUNTIME_BYTES_AND_COMPLETE_ALIAS_TOPOLOGY_PRESERVED_NO_PYTHON_WRAPPER')


def image_directories(source,layout):
    """Exact selected image names, including every hidden/empty source directory.

    The fresh procfs has a kernel-owned changing population; it is checked by
    its separate readonly/new-PID-namespace bootstrap contract. Every other
    selected directory is closed before the original starts.
    """
    modes=dict(layout['directories'])
    files=set(layout['files'])|{'/profile/c5-executor.py','/profile/c5-execution.json','/dev/null'}
    links=set(layout['links'])|{'/dev/fd'}
    for name,mode in source['directories'].items():
        path=SOURCE_MOUNT if name=='.' else SOURCE_MOUNT+'/'+name
        modes[path]=mode
    files.update(SOURCE_MOUNT+'/'+name for name in source['files'])
    for name in files|links|set(modes):
        for parent in PurePosixPath(name).parents:modes.setdefault(str(parent),0o755)
    need(not files&links and not (files|links)&set(modes),'C5 complete image members overlap')
    members=files|links|set(modes)
    return {name:dict(mode=mode,names=sorted(PurePosixPath(member).name for member in members
            if member!=name and str(PurePosixPath(member).parent)==name))
            for name,mode in sorted(modes.items()) if name!='/proc'}


def captured_source_identity(source,objects,expected):
    """Bind non-authority post-commit metadata to captured actual Git bytes.

    The new clean commit must remain a loose object in this explicit profile.
    All packed/other source objects are still captured; nothing is projected
    away and no Git command or imported completion establishes this binding.
    """
    files=source['state']['files']
    raw=objects[files['.git/HEAD']['sha256']]
    need(len(raw)<=1024,'C5 HEAD input exceeds metadata bound')
    value=raw.decode('ascii','strict').strip()
    if value.startswith('ref: '):
        name=value[5:]
        need(name.startswith('refs/heads/') and '..' not in PurePosixPath(name).parts,'Unsupported C5 HEAD reference')
        member='.git/'+name
        if member in files:value=objects[files[member]['sha256']].decode('ascii','strict').strip()
        else:
            packed=objects[files['.git/packed-refs']['sha256']].decode('ascii','strict').splitlines()
            matched=[line.split(' ',1)[0] for line in packed if line.endswith(' '+name)]
            need(len(matched)==1,'C5 packed HEAD reference is ambiguous')
            value=matched[0]
    need(value==expected['source_commit'],'Captured HEAD differs from the frozen post-commit envelope')
    member='.git/objects/'+value[:2]+'/'+value[2:]
    need(member in files,'C5 reviewed fresh HEAD commit must retain its loose object')
    packed=objects[files[member]['sha256']]
    decoder=zlib.decompressobj()
    unpacked=decoder.decompress(packed,1024**2+1)
    need(len(unpacked)<=1024**2 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,
         'C5 loose HEAD commit metadata exceeds its explicit bound or has trailing data')
    header,separator,body=unpacked.partition(b'\0')
    need(separator and header==b'commit '+str(len(body)).encode('ascii') and hashlib.sha1(unpacked).hexdigest()==value,
         'C5 captured HEAD commit object bytes do not match their Git identity')
    first=body.partition(b'\n')[0]
    need(first==b'tree '+expected['source_tree'].encode('ascii'),
         'Captured HEAD tree differs from the frozen post-commit envelope')
    return dict(source_commit=value,source_tree=expected['source_tree'],loose_commit_member=member,
        loose_commit_sha256=files[member]['sha256'],metadata_bytes=len(unpacked),
        basis='ACTUAL_CAPTURED_HEAD_AND_HASH_VERIFIED_COMMIT_TREE;OUTER_METADATA_IS_NOT_AUTHORITY')


def git_inputs(objects):
    """Exact additional clone dependencies; existing base tools remain fixed."""
    result = dict(files={},directories={})
    for name,pin in SPEC['git_files'].items():
        row = B.capture_selector(name,objects,limit=P.RUNTIME_BOUNDS['file_bytes'])
        need(row['kind'] == 'FILE' and all(row[key] == pin[key] for key in ('bytes','sha256','mode','resolved','link')),
             'C5 clone input differs from its exact reviewed pin: ' + name)
        result['files'][name] = row
    for name,wanted in SPEC['git_directories'].items():
        observed = B.capture_selector(name,{})
        need(observed['kind'] == 'DIRECTORY', 'C5 clone template directory is absent')
        fd = P.open_directory(observed['resolved'])
        try:
            before = P.identity(os.fstat(fd))
            names = sorted(os.listdir(fd))
            need(names == wanted, 'C5 clone template population differs')
            B.require_same(before,P.identity(os.fstat(fd)),'clone template directory')
        finally:
            os.close(fd)
        B.require_same(observed,B.capture_selector(name,{}),'clone template selector')
        result['directories'][name] = dict(observation=observed,names=names)
    return result


class GenuineC5Session:
    """One actual C5 execution and same-live-owner reuse; no receipt importer."""
    def __init__(self, source_root, output, *, expected_source):
        CHECK()
        need(platform.system() == 'Linux' and platform.machine() == 'x86_64', 'C5 execution requires reviewed Linux x86_64')
        need(hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal'), 'C5 execution requires actual pidfd custody')
        need(type(expected_source) is dict and set(expected_source)=={'source_commit','source_tree'}
             and all(type(value) is str and len(value)==40 and all(c in '0123456789abcdef' for c in value)
                     for value in expected_source.values()),'C5 post-commit comparison metadata is malformed')
        self.expected_source=dict(expected_source)
        self.source, self.output = Path(source_root).absolute(), Path(output).absolute()
        B._ancestors(self.source)
        B._ancestors(self.output.parent)
        need(self.source == Path(ENGINE_ROOT), 'Fixed C5 source owner must execute its own full captured candidate')
        need(not self.output.exists() and not self.output.is_relative_to(self.source), 'C5 evidence must be fresh and outside source')
        self.output.mkdir(mode=0o700)
        self.output_anchor = anchor(self.output.stat())
        self.owner = os.getpid()
        self.lock = threading.Lock()
        self.owned, self.sealed, self.stage = {}, {}, None
        self.retained_directories, self.stage_directories = None, []
        self.attempted, self.closed, self.result, self.acquired = False, False, None, None
        self.reserved = 0
        self.prepaid = {'closing-custody.json':P.MANIFEST_BOUND,'result.json':P.MANIFEST_BOUND}
        self._reserve(sum(self.prepaid.values()),'bounded closing and result metadata')
        # Journal writes are owned by the unchanged CompletionContract. Reserve
        # its whole existing64MiB cap plus both actual raw outer logs before launch.
        self._reserve(64*1024**2 + 2*LIMITS['stream_bytes'],'journal and outer streams')

    def _reserve(self, count, label):
        need(type(count) is int and count >= 0, 'Invalid C5 evidence reservation')
        need(self.reserved + count <= LIMITS['evidence_bytes'], 'C5 evidence allocation exhausted: ' + label)
        self.reserved += count

    def _write(self, relative, raw):
        need(type(raw) is bytes, 'C5 evidence must be exact bytes')
        P.safe_name(relative)
        path = self.output / relative
        need(not path.exists() and not path.is_symlink(), 'C5 evidence already exists')
        if relative in self.prepaid:
            need(len(raw) <= self.prepaid[relative],'C5 prepaid metadata exceeds inherited manifest bound')
        else:
            self._reserve(len(raw),relative)
        path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        B._ancestors(path.parent)
        fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            send(fd,raw)
            os.fsync(fd)
            os.fchmod(fd,0o400)
            physical = stamp(os.fstat(fd))
        finally:
            os.close(fd)
        self.owned[relative] = dict(bytes=len(raw),sha256=sha(raw),identity=physical,mode=0o400)

    def _check_owned(self):
        need(not self.closed and os.getpid() == self.owner and anchor(self.output.stat()) == self.output_anchor,
             'C5 session owner or evidence root changed')
        CHECK()
        for name,row in self.owned.items():
            path = self.output/name
            B._ancestors(path.parent)
            metadata,raw = P.read_regular(path,max(P.SOURCE_BOUNDS['file_bytes'],G.E.MAX_PROCESS_JSON))
            need(stamp(path.lstat()) == row['identity'] and metadata['mode'] == row['mode']
                 and len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'C5 retained evidence changed')
        for fd,row in self.sealed.items():
            need(stamp(os.fstat(fd)) == row['identity'] and fcntl.fcntl(fd,fcntl.F_GET_SEALS) == 15,
                 'C5 acquired sealed input custody changed')
        if self.stage is not None:
            self.stage.check()
        if self.retained_directories is not None:
            need(self._directory_population() == self.retained_directories,
                 'C5 closed evidence directory population or metadata changed')

    def _bind_existing(self,relative,*,mode,expected=None,limit=None,seal=False):
        """Retain a file already produced by this owner; never import a result."""
        P.safe_name(relative)
        path=self.output/relative
        B._ancestors(path.parent)
        bound=max(P.SOURCE_BOUNDS['file_bytes'],G.E.MAX_PROCESS_JSON) if limit is None else limit
        metadata,raw=P.read_regular(path,bound)
        if expected is not None:
            need(len(raw)==expected['bytes'] and sha(raw)==expected['sha256'],
                 'C5 terminal owned bytes differ from their live producer record')
        if seal:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
            try:
                need(P.identity(os.fstat(fd))==metadata['identity'],'C5 outer log changed before sealing')
                os.fchmod(fd,mode)
                physical=stamp(os.fstat(fd))
            finally:os.close(fd)
            need(stamp(path.lstat())==physical,'C5 outer log changed after sealing')
            metadata,after=P.read_regular(path,bound)
            need(after==raw,'C5 outer raw log bytes changed while sealing')
        need(metadata['mode']==mode,'C5 terminal storage mode differs')
        self.owned[relative]=dict(bytes=len(raw),sha256=sha(raw),identity=stamp(path.lstat()),mode=mode)
        return {key:self.owned[relative][key] for key in ('bytes','sha256','mode')}

    def _bind_gate(self,gate):
        need(gate._closed and gate._reaped,'C5 gate evidence cannot close before actual wait custody')
        gate._check_owned()
        for relative,row in gate._owned.items():
            path=gate.output/relative
            need(G.file_identity(path.lstat())==row['identity'],'C5 live gate terminal identity differs')
            self._bind_existing('live/'+relative,mode=row['mode'],expected=row,
                                limit=max(G.E.MAX_PROCESS_JSON,G.E.MAX_FILE))
        if gate._contract is not None:
            journal=gate._contract.journal
            need(journal.closed,'C5 completion writer is still live at retention')
            lock=journal.root/'writer.lock'
            need((lock.stat().st_dev,lock.stat().st_ino)==journal.lock_identity,
                 'C5 completion lock changed after live close')
            self._bind_existing('live/journal/writer.lock',mode=0o600,
                                expected=dict(bytes=0,sha256=sha(b'')),limit=0)
            if journal.disk is not None:
                self._bind_existing('live/journal/history.json',mode=0o600,
                    expected=dict(bytes=len(journal.disk),sha256=sha(journal.disk)),limit=64*1024**2)

    def _bind_stage(self):
        if self.stage is None:return
        self.stage.check(rehash=True)
        for name,row in self.stage.state['files'].items():
            self._bind_existing('source-stage/'+name,mode=row['mode'],expected=row)
        self.stage_directories=['source-stage' if name=='.' else 'source-stage/'+name
                                for name in self.stage.state['directories']]

    def _directory_population(self):
        """Exact closed population, rooted in files produced by this live owner."""
        names={'.':set()}
        def add_directory(name):
            names.setdefault(name,set())
            if name!='.':
                parent=str(PurePosixPath(name).parent)
                add_directory(parent)
                names[parent].add(PurePosixPath(name).name)
        for name in self.stage_directories:add_directory(name)
        for name in self.owned:
            parent=str(PurePosixPath(name).parent)
            add_directory(parent)
            names[parent].add(PurePosixPath(name).name)
        result={}
        for name,expected in sorted(names.items()):
            path=self.output if name=='.' else self.output/name
            fd=P.open_directory(path)
            try:
                before=stamp(os.fstat(fd));observed=[]
                with os.scandir(fd) as entries:
                    for entry in entries:
                        observed.append(entry.name)
                        need(len(observed)<=len(expected),'C5 closed evidence gained an extra member')
                need(sorted(observed)==sorted(expected) and stamp(os.fstat(fd))==before,
                     'C5 closed evidence population changed')
                need(stamp(path.lstat())==before and not os.listxattr(fd),'C5 closed evidence directory changed')
                result[name]=dict(identity=before,names=sorted(observed))
            finally:os.close(fd)
        return result

    def _acquire(self):
        CHECK()
        captured = D.C5ProviderInputs(self.source).acquire()
        record, objects = captured['record'], dict(captured['objects'])
        extra = git_inputs(objects)
        P.validate_git_namespace(record['source']['state'],objects)
        git_identity=captured_source_identity(record['source'],objects,self.expected_source)
        runtime = dict(record['runtime'], files=dict(record['runtime']['files']))
        for name,row in extra['files'].items():
            need(name not in runtime['files'] or runtime['files'][name] == row, 'C5 clone/base runtime selector conflict')
            runtime['files'][name] = row
        runtime['directories'] = dict(runtime['directories'])
        for name,row in extra['directories'].items():
            need(name not in runtime['directories'], 'C5 clone directory duplicates an inherited runtime root')
            runtime['directories'][name] = dict(identity=row['observation']['identity'],
                ancestors=row['observation']['ancestors'],names=row['names'])
        totals = P.runtime_budget(runtime['files'],P.RUNTIME_BOUNDS)
        runtime['totals'] = totals
        topology = runtime_topology(runtime)
        layout = runtime_layout(runtime,topology)
        B.require_same(topology,runtime_topology(runtime),'complete runtime topology')
        B.require_same(extra,git_inputs({}),'complete clone runtime inputs')
        CHECK()
        metadata,launcher = P.read_regular(Path('/usr/bin/bwrap'),P.RUNTIME_BOUNDS['file_bytes'],single_link=False)
        need(dict(bytes=len(launcher),sha256=metadata['sha256'],mode=metadata['mode']) == SPEC['launcher'], 'C5 actual namespace launcher changed')
        observation = dict(provider=record,clone_inputs=extra,runtime_totals=totals,topology=topology,layout=layout,
            source_commit=git_identity['source_commit'],source_tree=git_identity['source_tree'],captured_git_identity=git_identity,launcher=metadata,
            selection_origins=SPEC['selection_origins'],executing_sources={name:dict(bytes=len(row[0]),sha256=sha(row[0])) for name,row in SOURCES.items()},
            execution_policy='READONLY_COMPLETE_SOURCE_WORK512_FOR_ORIGINAL_TEMP_CLONES_TMP32_UNCHANGED',
            authority='NONE')
        return dict(observation=observation,objects=objects,runtime=runtime,key=sha(encode(observation)))

    def _same_inputs(self):
        fresh = self._acquire()
        need(fresh['observation'] == self.acquired['observation'] and fresh['key'] == self.acquired['key'],
             'C5 source/runtime/provider/clone-input currentness changed')
        self._check_owned()

    def _seal(self, raw):
        fd = Q.VerifierTaskSession._sealed(raw)
        try:
            need(fd < LIMITS['descriptors'] and fcntl.fcntl(fd,fcntl.F_GET_SEALS) == 15,
                 'C5 sealed descriptor capacity/integrity differs')
            self.sealed[fd] = dict(identity=stamp(os.fstat(fd)),bytes=len(raw),sha256=sha(raw))
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _image(self, gate_fd):
        acquired, layout = self.acquired, self.acquired['observation']['layout']
        source = acquired['observation']['provider']['source']['state']
        environment = dict(D._ENVIRONMENT, PWD=SOURCE_MOUNT, TMPDIR=WORK_MOUNT,
            R0035_REPRO_EVENT_CAPTURE_DIR=WORK_MOUNT+'/capture',R0035_C5_LIVE_GATE_FD=str(gate_fd))
        # source and runtime are distinct existing allocations, not a new union.
        self.stage = CapturedSourceStage(self.output,source,acquired['objects'],self._reserve)
        startup = {}
        for name,row in acquired['runtime']['files'].items():
            startup[name] = {key:row[key] for key in ('bytes','sha256','mode','resolved')}
        for name,row in source['files'].items():
            path = SOURCE_MOUNT+'/'+name
            startup[path] = dict(row,resolved=path)
        startup['/profile/c5-executor.py']=dict(bytes=len(SOURCES[EXECUTOR][0]),sha256=sha(SOURCES[EXECUTOR][0]),
            mode=0o444,resolved='/profile/c5-executor.py')
        absent=set(acquired['runtime']['startup']['absent'])|set(acquired['runtime']['startup']['nscd'])
        absent.update(name for name,row in acquired['runtime']['startup']['aliases'].items() if row['kind']=='MISSING')
        configuration = dict(schema='implementaudit.c5-execution-image.v1',scope=PROFILE,
            gate_fd=gate_fd,environment=environment,limits=LIMITS,startup_files=startup,
            runtime_links=dict(layout['links'],**{'/dev/fd':'/proc/self/fd'}),required_absent=sorted(absent),
            image_directories=image_directories(source,layout),
            host_pid_namespace=os.readlink('/proc/self/ns/pid'),authority='NONE')
        configuration_raw = encode(configuration)
        need(len(configuration_raw) <= MAX_HEADER, 'C5 complete in-image readback manifest exceeds existing4MiB bound')
        support = {'/profile/c5-executor.py':(SOURCES[EXECUTOR][0],0o444),
                   '/profile/c5-execution.json':(configuration_raw,0o444)}
        execution_entries = dict(acquired['runtime']['files'])
        for name,(raw,mode) in support.items():
            execution_entries[name] = dict(bytes=len(raw),sha256=sha(raw),mode=mode)
        image_totals = P.runtime_budget(execution_entries,P.RUNTIME_BOUNDS)
        need(len(execution_entries)+len(layout['directories'])+len(layout['links']) <= P.RUNTIME_BOUNDS['entries'],
             'C5 complete runtime support population exceeds inherited bound')
        args = ['--unshare-all','--unshare-user','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL']
        for name,value in sorted(environment.items()):
            args += ['--setenv',name,value]
        for name,mode in layout['directories'].items():
            if name != '/':
                args += ['--perms',oct(mode)[2:],'--dir',name]
        for name,target in sorted(layout['links'].items(),key=lambda item:(item[0].count('/'),item[0])):
            args += ['--symlink',target,name]
        for name,row in sorted(layout['files'].items()):
            raw = acquired['objects'][row['sha256']]
            need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'C5 runtime object unavailable')
            fd = self._seal(raw)
            args += ['--perms',oct(row['mode'])[2:],'--ro-bind-data',str(fd),name]
        for name,(raw,mode) in sorted(support.items()):
            fd = self._seal(raw)
            args += ['--perms',oct(mode)[2:],'--ro-bind-data',str(fd),name]
        args += ['--ro-bind',str(self.stage.root),SOURCE_MOUNT,
            '--proc','/proc','--remount-ro','/proc','--symlink','/proc/self/fd','/dev/fd',
            '--dev-bind','/dev/null','/dev/null',
            '--perms','0755','--size',str(LIMITS['work_bytes']),'--tmpfs',WORK_MOUNT,
            '--perms','0755','--size',str(LIMITS['scratch_bytes']),'--tmpfs',SCRATCH_MOUNT,
            '--remount-ro','/','--chdir',SOURCE_MOUNT]
        seccomp = self._seal(SECCOMP)
        args += ['--seccomp',str(seccomp)]
        need(len(args) < 8500, 'C5 image argument allocation exceeded')
        argfd = self._seal(b'\0'.join(value.encode() for value in args)+b'\0')
        need(max([gate_fd,*self.sealed,*self.stage.fds]) < LIMITS['descriptors'], 'C5 complete held descriptor allocation exceeded')
        command = ['/usr/bin/bwrap','--args',str(argfd),'/usr/bin/python3.12','-I','-S','-B',
                   '/profile/c5-executor.py','--c5-bootstrap']
        dispatch = dict(argv=command,complete_bwrap_arguments=args,acquisition=acquired['key'],
            image_configuration_sha256=sha(configuration_raw),runtime_budget=image_totals,
            source_budget=dict(bytes=sum(row['bytes'] for row in source['files'].values()),
                               files=len(source['files']),directories=len(source['directories']),limit=P.SOURCE_BOUNDS),
            runtime_representation=layout,held_source_descriptors=len(self.stage.fds),
            inherited_sealed_descriptors=len(self.sealed),actual_gate_fd=gate_fd,argument_count=len(args),
            private_work_policy='TMPDIR=/c5-work within existing512MiB; /tmp remains separate32MiB',
            descendant_lifecycle='BWRAP_DIE_WITH_PARENT_FRESH_PRIVATE_PID_NAMESPACE',authority='NONE')
        self._write('dispatch.json',encode(dispatch))
        return command,environment,configuration,configuration_raw

    @staticmethod
    def _contain_unconstructed(process):
        """Fallback only before a Gate object takes exclusive wait custody."""
        waited = os.wait4(process.pid,os.WNOHANG)
        killed = False
        pidfd = None
        if not waited[0]:
            pidfd = os.pidfd_open(process.pid)
            try:
                signal.pidfd_send_signal(pidfd,signal.SIGKILL,None,0)
                killed = True
            except ProcessLookupError:
                pass
            finally:
                os.close(pidfd)
        deadline = time.monotonic()+3
        while not waited[0] and time.monotonic()<deadline:
            time.sleep(0.01)
            waited = os.wait4(process.pid,os.WNOHANG)
        need(waited[0] == process.pid, 'C5 constructor-failure direct child did not reap')
        process.returncode = os.waitstatus_to_exitcode(waited[1])
        absent = False
        while True:
            try:
                os.killpg(process.pid,0)
            except ProcessLookupError:
                absent = True
                break
            if time.monotonic()>=deadline:
                break
            time.sleep(0.01)
        return dict(actual_pid=process.pid,wait4_reaped=True,exit_code=process.returncode,
            wait_status=waited[1],max_rss_kib=waited[2].ru_maxrss,direct_child_killed=killed,
            group_absent=absent,numeric_group_signalled=False)

    def _release_bootstrap(self, gate, configuration, raw):
        gate._live_child()
        count = int.from_bytes(gate._read_exact(8),'big')
        need(0<count<=MAX_HEADER,'C5 bootstrap observation exceeds fixed bound')
        observed_raw = gate._read_exact(count)
        observed = json.loads(observed_raw)
        need(encode(observed)==observed_raw and set(observed)=={'schema','image_sha256','actual_pid',
            'actual_pid_namespace','uid','gid','cap_eff','startup_files','image_directories','private_work_bytes','scratch_bytes',
            'source_readonly','root_readonly','retained_descriptor','authority'},'C5 bootstrap observation schema differs')
        need(observed['schema']==BOOTSTRAP_SCHEMA and observed['image_sha256']==sha(raw)
            and observed['startup_files']==configuration['startup_files']
            and observed['image_directories']==configuration['image_directories'] and observed['uid']==observed['gid']==0
            and observed['cap_eff']=='0000000000000000' and observed['source_readonly'] is True
            and observed['root_readonly'] is True and type(observed['actual_pid']) is int and observed['actual_pid']>0
            and observed['actual_pid_namespace']!=configuration['host_pid_namespace']
            and observed['private_work_bytes']==LIMITS['work_bytes'] and observed['scratch_bytes']==LIMITS['scratch_bytes']
            and observed['retained_descriptor']==configuration['gate_fd'] and observed['authority']=='NONE',
            'C5 actual image readback/capacity/identity differs from reviewed acquisition')
        self._write('bootstrap-observation.json',observed_raw)
        self._same_inputs()
        gate._live_child()
        reply = encode(dict(schema=BOOTSTRAP_REPLY,image_sha256=sha(raw),accepted=True))
        gate.channel.sendall(len(reply).to_bytes(8,'big')+reply)

    def run(self):
        need(self.lock.acquire(blocking=False),'Concurrent C5 consumption is unsupported')
        try:
            self._check_owned()
            if self.result is not None:
                self._same_inputs()
                return json.loads(encode(dict(self.result,disposition='REUSED_SAME_LIVE_PRODUCER')))
            need(not self.attempted,'Failed/interrupted C5 execution cannot be replayed as a fresh result')
            return self._run_once()
        finally:
            self.lock.release()

    def _run_once(self):
        self.attempted=True
        self.acquired=self._acquire()
        record=self.acquired['observation']['provider']
        for name,value in (('provider-source.json',record['source']),('provider-runtime.json',record['runtime']),
                           ('clone-inputs.json',self.acquired['observation']['clone_inputs'])):
            raw=encode(value)
            need(len(raw)<=P.MANIFEST_BOUND,'C5 retained observation exceeds inherited per-manifest bound')
            self._write(name,raw)
        summary={key:value for key,value in record.items() if key not in ('source','runtime')}
        self._write('provider-input-observation.json',encode(dict(summary,source_file='provider-source.json',runtime_file='provider-runtime.json')))
        object_bytes=sum(len(raw) for raw in self.acquired['objects'].values())
        need(object_bytes<=LIMITS['retained_object_bytes'],'C5 object retention allocation exceeded')
        for key,raw in sorted(self.acquired['objects'].items()):
            need(key==sha(raw),'C5 object address differs')
            self._write('objects/'+key,raw)
        need(resource.getrlimit(resource.RLIMIT_NOFILE)[0]>=LIMITS['descriptors'],
             'C5 owner has insufficient declared descriptor capacity')
        endpoint,child_endpoint=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
        process=gate=watchdog=None
        stop_watchdog=threading.Event()
        timed_out=[]
        outcome=primary_error=None
        failure=None
        cleanup_errors=[]
        logs={}
        custody=dict(actual_dispatch=False,actual_exit='UNOBSERVED')
        began=time.monotonic()
        owner=self
        class BudgetedGate(G.LiveC5Gate):
            def __init__(self,*args,**kwargs):
                try:super().__init__(*args,**kwargs)
                except BaseException:
                    # Construction has not transferred wait custody to the caller.
                    # Dispose only this partially constructed object's pidfd;
                    # the executor retains actual Popen/wait4 containment below.
                    if getattr(self,'pidfd',None) is not None:
                        os.close(self.pidfd);self.pidfd=None
                    raise
            def _write(self,relative,raw):
                owner._reserve(len(raw),'live gate '+relative)
                return super()._write(relative,raw)
        try:
            command,environment,configuration,configuration_raw=self._image(child_endpoint.fileno())
            self._check_owned()
            def limits():
                for which,key in ((resource.RLIMIT_CPU,'cpu_seconds'),(resource.RLIMIT_AS,'address_bytes'),
                                  (resource.RLIMIT_FSIZE,'file_bytes'),(resource.RLIMIT_NOFILE,'descriptors')):
                    resource.setrlimit(which,(LIMITS[key],)*2)
            with (self.output/'stdout.log').open('xb') as stdout,(self.output/'stderr.log').open('xb') as stderr:
                process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                    env=environment,cwd=self.source,close_fds=True,
                    pass_fds=tuple([*self.sealed,child_endpoint.fileno()]),start_new_session=True,preexec_fn=limits)
                child_endpoint.close()
                watchdog_fd=os.pidfd_open(process.pid)
                def expire():
                    try:
                        if not stop_watchdog.wait(LIMITS['wall_seconds']):
                            try:
                                signal.pidfd_send_signal(watchdog_fd,signal.SIGKILL,None,0)
                                timed_out.append(dict(actual_pid=process.pid,signal='SIGKILL',custody='ACTUAL_PIDFD'))
                            except ProcessLookupError:
                                timed_out.append(dict(actual_pid=process.pid,signal='ALREADY_TERMINAL',custody='ACTUAL_PIDFD'))
                    finally:os.close(watchdog_fd)
                watchdog=threading.Thread(target=expire,name='owned-c5-deadline')
                try:watchdog.start()
                except BaseException:
                    os.close(watchdog_fd);watchdog=None
                    raise
                expected_source=dict(source_commit=self.acquired['observation']['source_commit'],source_tree=self.expected_source['source_tree'])
                for label,name in (('producer',G.E.PRODUCER),('capture_owner',G.E.OWNER)):
                    expected_source[label]=dict(path=name,**record['source']['state']['files'][name])
                executable_inputs={row['resolved']:row['sha256'] for row in self.acquired['runtime']['files'].values()}
                gate=BudgetedGate(self.output/'live',process,endpoint,expected_source=expected_source,
                    expected_context=dict(repository='/work',cwd='/work',python_command='python',work_parent=WORK_MOUNT),
                    executable_inputs=executable_inputs,acquisition_digest=self.acquired['key'],require_current=self._check_owned,
                    wall_seconds=LIMITS['wall_seconds'])
                self._release_bootstrap(gate,configuration,configuration_raw)
                preconsumer=False
                frames=[]
                while not gate._finished:
                    if gate._event_count==2 and gate._consumer_frontier is None and not preconsumer:
                        self._same_inputs();preconsumer=True
                    frame=gate.handle_next();frames.append(frame)
                    if frame['phase']=='INIT':
                        for role,name in (('build',G.E.BUILD),('checksum',G.E.CHECKSUM)):
                            wanted=record['source']['state']['files'][name]
                            actual=gate._session['source_scripts'][role]
                            need(actual['blob']==dict(bytes=wanted['bytes'],sha256=wanted['sha256']) and actual['mode']==wanted['mode'],
                                 'Actual Git commit scripts differ from the acquired fixed producer programs')
                    need(not timed_out,'Actual C5 producer exceeded its120-second wall deadline')
                    need(len(frames)<=40,'C5 original live frame count exceeded INIT+38event+FINISH population')
                component=gate.finalize()
                stop_watchdog.set();watchdog.join(timeout=3)
                need(not watchdog.is_alive() and not timed_out,'C5 wall watchdog did not close cleanly')
                stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
                need(preconsumer and component['output_join_preceded_first_consumer'],'Actual C5 consumer lacks required live output JOIN')
                self._same_inputs()
                source_stage=self.stage.check(rehash=True)
                outcome=dict(schema='implementaudit.genuine-c5-live-result.v1',scope=PROFILE,
                    status='SATISFIED_AT_FIXED_GENUINE_C5_EXECUTION_CONTRACT',disposition='EXECUTED',
                    acquisition=self.acquired['key'],actual_outer_process=component['actual_outer_process'],
                    original48_dispatches=1,validated_actual_events=19,retained_artifacts=6,
                    package_source_commit=self.expected_source['source_commit'],package_source_tree=self.expected_source['source_tree'],
                    complete_working_source_observation=record['observation_sha256'],
                    provider='GENUINE_CAPTURED_ZOPFLI_0.2.3.post1_NORMAL_SITE_IN_FIXED_IMAGE',
                    image_readback='COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES',
                    source_runtime_current=True,output_join_before_first_consumer=True,final_join=component['history_digest'],
                    actual_stage=source_stage,wall_timeout=False,original48_execution_qualified=True,
                    canonical_acceptance='UNQUALIFIED',native_dispatch_authorized=False,R39_criterion5='NOT_ESTABLISHED',authority='NONE')
        except BaseException as exc:
            primary_error=exc
            failure=dict(type=type(exc).__name__,message=str(exc))
        finally:
            stop_watchdog.set()
            def cleanup(label,operation):
                try:return operation()
                except BaseException as exc:
                    cleanup_errors.append(dict(operation=label,type=type(exc).__name__,message=str(exc)))
                    return None
            if gate is not None:
                cleanup('close actual live gate',gate.close)
                custody=gate._wait_result
                cleanup('retain closed actual gate and journal',lambda:self._bind_gate(gate))
            elif process is not None:
                custody=cleanup('contain actual constructor-failure child',lambda:self._contain_unconstructed(process))
            if watchdog is not None:
                cleanup('join actual watchdog',lambda:watchdog.join(timeout=3))
                if watchdog.is_alive():cleanup_errors.append(dict(operation='watchdog',type='LIVE_THREAD',message='actual watchdog failed to close'))
            cleanup('retain exact staged source',self._bind_stage)
            if self.stage is not None:
                cleanup('close staged source descriptors',self.stage.close)
                self.stage=None
            cleanup('close parent channel',endpoint.close)
            cleanup('close child channel',child_endpoint.close)
            for fd in tuple(self.sealed):cleanup('close sealed input descriptor '+str(fd),lambda fd=fd:os.close(fd))
            self.sealed.clear()
            # Reaping/containment is complete before reading logs. Both failed
            # and successful attempts keep their actual bounded stdout/stderr.
            for name in ('stdout.log','stderr.log'):
                if (self.output/name).exists():
                    value=cleanup('retain '+name,lambda name=name:self._bind_existing(name,mode=0o400,
                        limit=LIMITS['stream_bytes'],seal=True))
                    if value is not None:logs[name]=value
            closing=dict(schema='implementaudit.genuine-c5-closing-custody.v1',custody=custody,
                error=failure,cleanup_errors=cleanup_errors,watchdog=timed_out,raw_outputs=logs,
                actual_original_init_observed=gate is not None and gate._session is not None,
                original48_success_published=False,elapsed_seconds=time.monotonic()-began,authority='NONE')
            self._write('closing-custody.json',encode(closing))
        if primary_error is not None:raise primary_error
        need(not cleanup_errors and outcome is not None,'C5 actual closing custody or retained evidence failed')
        need(custody is not None and custody['wait4_reaped'] and custody['group_absent']
             and custody['exit_code']==0 and not timed_out,'C5 actual process did not close within the declared contract')
        need(set(logs)=={'stdout.log','stderr.log'},'C5 actual outer output retention is incomplete')
        self._same_inputs()
        outcome['raw_outputs']=logs
        outcome['closing_custody_sha256']=self.owned['closing-custody.json']['sha256']
        self._write('result.json',encode(outcome))
        self.retained_directories=self._directory_population()
        self._check_owned()
        # This is the first publication point, after child, channel, watchdog,
        # staged/sealed descriptors and complete retained output population close.
        self.result=outcome
        return json.loads(encode(outcome))

    def close(self):
        need(os.getpid()==self.owner,'Transferred C5 owner cannot close or resume live custody')
        need(self.lock.acquire(blocking=False),'Running C5 consumption must finish its owned cleanup before close')
        try:
            for fd in tuple(self.sealed):os.close(fd)
            self.sealed.clear()
            if self.stage is not None:
                self.stage.close();self.stage=None
            self.closed=True
        finally:self.lock.release()
