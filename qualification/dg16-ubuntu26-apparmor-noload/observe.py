"""Observe the reviewed policy compiler output on the exact failed host image."""
import ast
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import time

PARSER = Path('/usr/sbin/apparmor_parser')
OWNER = Path('scripts/qualify-work-graph-c5-setup.py')
EXPECTED_OWNER = '5caa2b1771c41b9c13328b44c72b45ff73d65832b6892cc6bc61cfb54bd6cbf1'
EXPECTED_POLICY = 'b3f303f76b8f2c097f92ca5e41b6e0126cd34a10df1d5d0e67b9e86e92e322af'
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}
FLAGS = ['--config-file=/dev/null','--skip-cache','--skip-read-cache','--jobs=0','--skip-kernel-load','--stdout']
sha = lambda body: hashlib.sha256(body).hexdigest()

def parser_identity():
    assert PARSER.resolve(strict=True) == PARSER
    fd = os.open(PARSER, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        assert stat.S_ISREG(before.st_mode) and before.st_uid == 0 and not before.st_mode & 0o022
        assert 0 < before.st_size <= 32 * 1024**2
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        mark = lambda st:(st.st_dev, st.st_ino, st.st_size, st.st_mode, st.st_uid, st.st_mtime_ns, st.st_ctime_ns)
        assert mark(before) == mark(os.fstat(stream.fileno())) == mark(PARSER.lstat())
        return dict(path=str(PARSER), bytes=before.st_size, sha256=digest, mode=oct(stat.S_IMODE(before.st_mode)), uid=before.st_uid)

def call(args, body, limits):
    start = time.monotonic()
    proc = subprocess.Popen([str(PARSER), *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=ENV, cwd='/', start_new_session=True, close_fds=True)
    data = [bytearray(), bytearray()]
    try:
        proc.stdin.write(body)
        proc.stdin.close()
        with selectors.DefaultSelector() as sel:
            for i, stream in enumerate((proc.stdout, proc.stderr)):
                sel.register(stream, selectors.EVENT_READ, i)
            while sel.get_map():
                remaining = start + 20 - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('compiler deadline')
                for key, _ in sel.select(remaining):
                    i = key.data
                    chunk = os.read(key.fd, min(8192, limits[i] + 1 - len(data[i])))
                    if not chunk:
                        sel.unregister(key.fileobj)
                    else:
                        data[i].extend(chunk)
                        if len(data[i]) > limits[i]:
                            raise ValueError('stream exceeds original bound')
        code = proc.wait(timeout=max(0, start + 20 - time.monotonic()))
        # One original no-parallel compiler. A nonempty child population is a
        # refusal and must go through the same owned-session cleanup as a timeout.
        try:
            os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            pass
        else:
            raise RuntimeError('child custody not quiescent')
    except BaseException:
        # This process is the only subreaper in the observation. Limit a stop
        # to our own session and reap any child adopted from that session.
        if proc.poll() is None or Path(f'/proc/self/task/{os.getpid()}/children').read_text().strip():
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.wait(timeout=3)
        end=time.monotonic()+3
        while True:
            try:
                waited,_=os.waitpid(-1,os.WNOHANG)
            except ChildProcessError:
                break
            if time.monotonic() >= end:
                raise RuntimeError('cleanup not established')
            if waited==0:time.sleep(0.02)
        raise
    finally:
        proc.stdout.close()
        proc.stderr.close()
    return code, bytes(data[0]), bytes(data[1]), round(time.monotonic()-start, 4)

def receive():
    assert 0 < os.geteuid() == os.getuid() and os.environ['GITHUB_RUN_ATTEMPT'] == '1'
    assert os.environ['ImageOS'] == 'ubuntu26' and os.environ['ImageVersion'] == '20261101.186.1'
    libc = ctypes.CDLL(None, use_errno=True)
    assert libc.prctl(36,1,0,0,0) == 0
    flag = ctypes.c_int()
    assert libc.prctl(37,ctypes.byref(flag),0,0,0) == 0 and flag.value == 1
    raw = OWNER.read_bytes()
    assert sha(raw) == EXPECTED_OWNER
    tree = ast.parse(raw)
    policy = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='HOSTED_BWRAP_POLICY')
    assert len(policy) == 841 and sha(policy) == EXPECTED_POLICY
    identity = parser_identity()
    vr, vo, ve, vt = call(['--version'], b'', (2048, 2048))
    assert vr == 0 and len(vo) + len(ve) <= 2048 and parser_identity() == identity
    version = re.search(rb'(?<![0-9])\d+\.\d+(?:\.\d+){0,3}',vo+b' '+ve)
    assert version is not None
    rc, compiled, err, elapsed = call(FLAGS, policy, (65536,8192))
    assert parser_identity() == identity
    result = dict(scope='userspace compiler observation only', image_os=os.environ['ImageOS'],image_version=os.environ['ImageVersion'],
                  run=os.environ['GITHUB_RUN_ID'],attempt=1,head=os.environ['GITHUB_SHA'],uid=os.getuid(),kernel=os.uname().release,
                  parser=identity, version=version.group().decode('ascii'),version_sha256=sha(vo+b'\0'+ve),
                  owner_sha256=sha(raw),policy_sha256=sha(policy),argv=FLAGS,elapsed_seconds=elapsed,
                  exit=rc,bytes=len(compiled),compiled_sha256=sha(compiled),stderr_bytes=len(err),stderr_sha256=sha(err),
                  child_cleanup='ECHILD',policy_loads=0,kernel_policy_export_reads=0,original_awards=[])
    if rc == 0 and compiled:
        # The received bytes are exclusively this public source policy's userspace stdout.
        # Keep bytes out of the job log. Only the small fixed header is public in the receipt.
        nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_bwrap_need','_bwrap_v5_profiles')]
        assert len(nodes)==2
        ns={'HOSTED_BWRAP_EXPORT_LIMIT':65536,'hashlib':hashlib}
        exec(compile(ast.Module(body=nodes,type_ignores=[]), str(OWNER), 'exec'),ns)
        try:
            profiles=ns['_bwrap_v5_profiles'](compiled)
        except ValueError as exc:
            msg=exc.args[0]
            assert isinstance(msg,str) and len(msg)<128 and re.fullmatch(r'[A-Za-z0-9 _-]+',msg)
            result['original_receiver']={'accepted':False,'refusal':msg}
        else:
            result['original_receiver']={'accepted':True,'names':sorted(profiles)}
        result['header_hex']=compiled[:64].hex()
        prefix=b'\x04\x08\x00version\x00\x02'
        if compiled.startswith(prefix) and len(compiled)>=len(prefix)+4:
            result['version_word_le']=int.from_bytes(compiled[len(prefix):len(prefix)+4],'little')
        with Path('observation/approved-policy.userspace.bin').open('xb') as f:
            f.write(compiled)
    return result

if __name__ == '__main__':
    os.umask(0o077)
    Path('observation').mkdir(mode=0o700)
    try:
        result=receive()
    except Exception as exc:
        result=dict(scope='userspace compiler observation only',status='REFUSED',exception=type(exc).__name__,
                    image_os=os.environ.get('ImageOS'),image_version=os.environ.get('ImageVersion'),original_awards=[])
        with Path('observation/RESULT.json').open('x') as f:json.dump(result,f,indent=2)
        raise SystemExit(1)
    with Path('observation/RESULT.json').open('x') as f:json.dump(result,f,indent=2)
    raise SystemExit(0 if result['exit']==0 and result['bytes']>0 else 1)
