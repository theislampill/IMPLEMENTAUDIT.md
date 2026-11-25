"""Reproducible prospective G132 source change v2 on b393a905 (run from a clean worktree at b393a905).

Successor of v1 (022a10f6, make_g132_candidate.py) correcting the independent review findings:
  (a) G1 profile row for measured 20261116.133.1 with the ORIGINAL tool pins (unchanged from v1);
  (b) root provisioning step for the COMPLETE git 2.56.0 program tree (usr/bin/git + all of usr/lib/git-core)
      from one digest-bound package at a durable PPA snapshot URL, staged in a root-owned 0700 directory,
      tree-manifest verified before install and read back after; run under sudo /usr/bin/env -i like the
      other steps.  bwrap is NOT provisioned by the step (M4): the core's qualified
      --provision-hosted-launcher remains the only bwrap path.  No package is vendored (Root ruling b9f0938);
  (c) sandboxed sender exec: carrier.Commands.run('encrypt') now builds exactly SANDBOX_PREFIX+openssl (B1);
      the sender role uses a separate CARRIER_COMPOSITION.sender_tools pin set {openssl, bwrap} of the sender
      host (M6) under the carrier's tool-pin checks plus root-owned/non-writable/unprivileged file and
      /, /usr, /usr/bin chain custody, rechecked by current_tools() at every capture currentness point; the
      launcher is bound by descriptor (fexecve of the verified fd) (M2).  root_tools is kept unchanged;
      the hosted decrypt path (host role, host_tools adoption, verify_decrypt_record argv) is unchanged;
  (d) fresh 20261125-01 ref names (the 20261120-01 refs are spent).
Then fixed-point rebinding of every SHA-256 (+adjacent byte count) pin that refers to ANY prior version
of a changed file. Issued records (Root / independent) are never edited; they are reported as needing re-issue.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = 'b393a9057c249335e6cdf4ccbb898d192b0830b8'
EP = 'qualification/dg16-r5-g1-hosted-episode'
EN = 'qualification/dg16-r5-g1-hosted-entry'
WF = '.github/workflows/dg16-r5-g1-hosted-episode.yml'
ISSUED = {f'{EN}/BOOTSTRAP_ADMISSION.json', f'{EP}/carrier/CARRIER_ADMISSION.json', f'{EP}/INDEPENDENT_PROOF_PINS.json'}
# Sender host (nominated WSL Ubuntu 24.04) tools, measured: openssl 3.0.13-0ubuntu3.16, bubblewrap 0.9.0-1ubuntu0.3.
SENDER_TOOLS = {'openssl': {'bytes': 1005368, 'sha256': 'b4f547c0f16272d1cc7f870330a6f2c243710c335e7a99c734ff7a0c6fdb2503'},
                'bwrap': {'bytes': 72160, 'sha256': 'e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71'}}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout


assert git('rev-parse', 'HEAD').strip() == BASE, 'run from a worktree at b393a905'
assert git('status', '--porcelain') == '', 'worktree must be clean'


def files():
    out = [Path(WF)] + sorted(x for r in (EN, EP) for x in Path(r).rglob('*') if x.is_file())
    return [x.as_posix() for x in out]


history = {f: [Path(f).read_bytes()] for f in files()}


def edit(path, fn):
    p = Path(path)
    s = p.read_bytes().decode('utf-8')
    t = fn(s)
    assert t != s, path
    p.write_bytes(t.encode('utf-8'))


def once(s, a, b):
    assert s.count(a) == 1, a[:70]
    return s.replace(a, b)


# (a) profile row (identical to v1)
ROW = ("{'id': 'G1_UBUNTU24_20261116_133_1', 'facts': {'platform': 'linux', 'architecture': 'x86_64', "
       "'os': {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'python_version': [3, 12, 3], 'image_os': 'ubuntu24', "
       "'uid': 0, 'euid': 0, 'gid': 0, 'egid': 0, 'image_version': '20261116.133.1'}, "
       "'core_tool_sha256': {'python3.12': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f', "
       "'git': '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235', "
       "'bwrap': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}}")


def profile(s):
    lines = s.split('\n')
    i = next(k for k, line in enumerate(lines) if line.startswith('G1_HOST_PROFILES = ('))
    assert lines[i].endswith('}})')
    lines[i] = lines[i][:-1] + ', ' + ROW + ')'
    return once('\n'.join(lines),
                "len(G1_HOST_PROFILES) == 3 and (len({row['id'] for row in G1_HOST_PROFILES}) == 3)",
                "len(G1_HOST_PROFILES) == 4 and (len({row['id'] for row in G1_HOST_PROFILES}) == 4)")


edit(f'{EP}/host_utility.py', profile)

# (c) sandboxed sender: sender_capture.py
SANDBOX_DEFS = (
    "FD_LIMIT=4096\n"
    "# The fixed sandbox launcher. Its exact bytes are the carrier's sender_tools['bwrap'] pin, checked and\n"
    "# rechecked by carrier.Commands with the other sender tools; the exec is bound to that verified file.\n"
    "SANDBOX='/usr/bin/bwrap'\n"
    "SANDBOX_PREFIX=[SANDBOX,'--unshare-all','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL',\n"
    "  '--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',\n"
    "  '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LC_ALL','C',\n"
    "  '--setenv','OPENSSL_CONF','/dev/null']\n")
CLOSE_PLAN_OLD = (
    "def close_plan(visible,kept,error_fd):\n"
    "    P.need(type(visible) is list and len(visible)<=FD_LIMIT and len(visible)==len(set(visible))\n"
    "      and all(type(fd) is int and 0<=fd<2**31 for fd in visible),'SENDER_DESCRIPTOR_POPULATION')\n"
    "    P.need(len(kept)==3 and error_fd not in kept,'SENDER_ERROR_FD_ALIAS')\n"
    "    return [fd for fd in visible if fd>2 and fd not in kept and fd!=error_fd]\n")
CLOSE_PLAN_NEW = (
    "def launcher_fd(pinned):\n"
    "    \"\"\"Open the sandbox launcher once; it must be the carrier-pinned file (identity and bytes).\n\n"
    "    The child fexecve()s this descriptor, so the executed file is the verified one, not a later path lookup.\n"
    "    \"\"\"\n"
    "    P.need(type(pinned) is dict and type(pinned.get('identity')) is list,'SENDER_SANDBOX_LAUNCHER_BINDING')\n"
    "    fd=os.open(SANDBOX,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)\n"
    "    try:\n"
    "        before=os.fstat(fd)\n"
    "        P.need(F.stamp(before)==pinned['identity'] and 0<before.st_size<=32*1024**2,'SENDER_SANDBOX_LAUNCHER_BINDING')\n"
    "        chunks=[];offset=0\n"
    "        while True:\n"
    "            raw=os.pread(fd,1024*1024,offset)\n"
    "            if not raw:break\n"
    "            chunks.append(raw);offset+=len(raw);P.need(offset<=before.st_size,'SENDER_SANDBOX_LAUNCHER_BINDING')\n"
    "        P.need(P.descriptor(b''.join(chunks))==dict(bytes=pinned['bytes'],sha256=pinned['sha256'])\n"
    "          and F.stamp(os.fstat(fd))==pinned['identity'],'SENDER_SANDBOX_LAUNCHER_BINDING')\n"
    "        return fd\n"
    "    except BaseException:\n"
    "        os.close(fd);raise\n\n"
    "def close_plan(visible,kept,error_fd,exec_fd):\n"
    "    P.need(type(visible) is list and len(visible)<=FD_LIMIT and len(visible)==len(set(visible))\n"
    "      and all(type(fd) is int and 0<=fd<2**31 for fd in visible),'SENDER_DESCRIPTOR_POPULATION')\n"
    "    P.need(len(kept)==3 and error_fd not in kept and exec_fd not in kept and exec_fd!=error_fd,'SENDER_ERROR_FD_ALIAS')\n"
    "    return [fd for fd in visible if fd>2 and fd not in kept and fd!=error_fd and fd!=exec_fd]\n")


def sender(s):
    s = once(s, "FD_LIMIT=4096\n", SANDBOX_DEFS)
    s = once(s, "    expected=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',\n",
             "    expected=SANDBOX_PREFIX+['/usr/bin/openssl',\n")
    s = once(s, CLOSE_PLAN_OLD, CLOSE_PLAN_NEW)
    s = once(s, "    def __init__(self,directory,budget,currentness):\n"
                "        self.directory=Path(directory);self.currentness=currentness;",
             "    def __init__(self,directory,budget,currentness,launcher):\n"
             "        P.need(callable(currentness) and callable(launcher),'SENDER_CURRENTNESS_REQUIRED')\n"
             "        self.directory=Path(directory);self.currentness=currentness;self.launcher=launcher;")
    s = once(s, "        evidence=None;rc=None;before_close=None;restore={};after_fds=None\n",
             "        evidence=None;rc=None;before_close=None;restore={};after_fds=None;exec_fd=None\n")
    s = once(s, "              'SENDER_EMPTY_STDIN_DEVICE')\n",
             "              'SENDER_EMPTY_STDIN_DEVICE')\n"
             "            exec_fd=launcher_fd(self.launcher());owned.add(exec_fd)\n")
    s = once(s, "close_plan(visible,fds,error_w):", "close_plan(visible,fds,error_w,exec_fd):")
    s = once(s, "os.execve('/usr/bin/env',argv,{'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENSSL_CONF':'/dev/null'})",
             "os.execve(exec_fd,argv,{})")
    return once(s, "for fd in (gate_r,error_w,out_w,err_w,null_fd):close(fd)",
                "for fd in (gate_r,error_w,out_w,err_w,null_fd,exec_fd):close(fd)")


edit(f'{EP}/carrier/sender_capture.py', sender)

# (c) carrier.py: B1 argv, sender tool set, launcher seam, sender tool custody
CUSTODY_FN = (
    "def sender_tool_custody(path,observed):\n"
    "    \"\"\"Sender tools: root-owned unprivileged regular files in a root-owned non-writable /, /usr, /usr/bin.\n\n"
    "    carrier_io.read_file already refused symlinks, any extended attribute (file capabilities), extra links\n"
    "    and identity change during the read; current_tools() rechecks the whole observed row (identity, ancestry).\n"
    "    \"\"\"\n"
    "    info=path.lstat()\n"
    "    P.need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_gid==0 and not info.st_mode&0o6022\n"
    "      and F.stamp(info)==observed['identity'],'CARRIER_ACTUAL_TOOL_PIN')\n"
    "    P.need([row[0] for row in observed['ancestors']]==['/','/usr','/usr/bin']\n"
    "      and all(row[4]==0 and not row[3]&0o022 for row in observed['ancestors']),'CARRIER_ACTUAL_TOOL_PIN')\n"
    "    return True\n\n"
    "class Commands:\n")
ENV_ARGV = "argv=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',*args]\n"


def carrier(s):
    s = once(s, "class Commands:\n", CUSTODY_FN)
    s = once(s, "            SP.current(binding['_sender_selection']);self.tool_pins=binding['root_tools']\n"
                "            self.u=SC.CaptureSession(directory,budget,lambda:self.current_tools(capture_callback=True))\n",
             "            SP.current(binding['_sender_selection']);self.tool_pins=binding['sender_tools']\n"
             "            self.u=SC.CaptureSession(directory,budget,lambda:self.current_tools(capture_callback=True),\n"
             "              lambda:self.tool_rows['bwrap'])\n")
    s = once(s, "              and stat.S_IMODE(path.lstat().st_mode)&0o022==0,'CARRIER_ACTUAL_TOOL_PIN')\n"
                "            self.tool_rows[name]=observed\n",
             "              and stat.S_IMODE(path.lstat().st_mode)&0o022==0,'CARRIER_ACTUAL_TOOL_PIN')\n"
             "            if role=='root':sender_tool_custody(path,observed)\n"
             "            self.tool_rows[name]=observed\n")
    return once(s, "        # env is itself an exact body-pinned tool; credentials/configuration\n"
                   "        # selectors and inherited OpenSSL/loader variables never reach a child.\n"
                   "        " + ENV_ARGV,
                "        if name=='encrypt':\n"
                "            # Root sender: exactly the form sender_capture.validate_command accepts. The pinned\n"
                "            # sandbox launcher (fexecve of the verified file) clears the environment and drops\n"
                "            # capabilities; env is not executed on the sender path.\n"
                "            argv=SC.SANDBOX_PREFIX+['/usr/bin/openssl',*args]\n"
                "        else:\n"
                "            # Host: env is itself an exact body-pinned tool; credentials/configuration\n"
                "            # selectors and inherited OpenSSL/loader variables never reach a child.\n"
                "            " + ENV_ARGV)


edit(f'{EP}/carrier/carrier.py', carrier)


def policy(s):
    s = once(s, "'host_tools','root_tools','limits','original_awards'))",
             "'host_tools','root_tools','sender_tools','limits','original_awards'))")
    return once(s, "    for role in ('root_tools',):\n        exact(v[role],('openssl','env'))\n",
                "    for role,names in (('root_tools',('openssl','env')),('sender_tools',('openssl','bwrap'))):\n"
                "        exact(v[role],names)\n")


edit(f'{EP}/carrier/carrier_policy.py', policy)


def composition(s):
    raw = s.encode()
    v = json.loads(raw)
    assert (json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode() == raw
    assert 'sender_tools' not in v
    v['sender_tools'] = SENDER_TOOLS
    return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n'


edit(f'{EP}/carrier/CARRIER_COMPOSITION.json', composition)

# (b) provisioning step (git program tree only; no bwrap; no vendored package)
inner = (HERE / 'provision-inner.sh').read_text()
inner = re.sub(r'#DRY_RUN_BEGIN\n.*?#DRY_RUN_END\n', '', inner, flags=re.S)
assert 'DRY_RUN' not in inner and '@TREE_SHA256@' not in inner and 'bwrap' not in inner.replace('# bwrap is', '')
script = ('set -euo pipefail\n'
          'test "$GITHUB_RUN_ATTEMPT" = 1\n'
          "sudo /usr/bin/env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC /usr/bin/bash -s <<'DG16_PROVISION_GIT'\n"
          + inner + 'DG16_PROVISION_GIT\n')
w = json.loads(Path(WF).read_bytes())
steps = w['jobs']['qualify']['steps']
assert steps[1]['name'] == 'Create exclusive fixed root island and exact packet' and steps[2]['name'] == 'Observe host tools'
steps.insert(2, {'name': 'Provision original pinned git program tree', 'shell': 'bash', 'run': script})
Path(WF).write_bytes(json.dumps(w, indent=2, separators=(',', ': '), ensure_ascii=False).encode() + b'\n')

# (d) fresh ref names
REN = {f'pro/dg16-g132-{k}-20261120-01': f'pro/dg16-g132-{k}-20261125-01'
       for k in ('original', 'cipher', 'g3-control', 'tools-control')}
REN['G132 original 20261120-01'] = 'G132 original 20261125-01'
for f in files():
    if f in ISSUED:
        continue
    b = Path(f).read_bytes()
    n = b
    for a, c in REN.items():
        n = n.replace(a.encode(), c.encode())
    if n != b:
        Path(f).write_bytes(n)

# rebinding against every version seen
for f in files():
    if history[f][-1] != Path(f).read_bytes():
        history[f].append(Path(f).read_bytes())
rnd = 0
for rnd in range(1, 40):
    subs = {}
    for f, vers in history.items():
        cur = Path(f).read_bytes()
        for v in vers:
            if v != cur:
                subs[sha(v)] = (len(v), sha(cur), len(cur))
    edited = False
    for f in files():
        if f in ISSUED:
            continue
        s = Path(f).read_bytes().decode('utf-8')
        t = s
        for old, (ob, new, nb) in subs.items():
            if old not in t:
                continue
            if ob != nb:
                t = re.sub(r'(bytes["\']?\s*[:=]\s*)%d(\b[^\n]{0,80}?%s)' % (ob, old),
                           lambda m: m.group(1) + str(nb) + m.group(2), t)
            t = t.replace(old, new)
        if t != s:
            Path(f).write_bytes(t.encode('utf-8'))
            history[f].append(t.encode('utf-8'))
            edited = True
    if not edited:
        break

current = {sha(Path(f).read_bytes()) for f in files()}
allold = {sha(v) for vers in history.values() for v in vers} - current
stale = {}
for f in files():
    hits = sorted(h[:12] for h in allold if h in Path(f).read_text(encoding='utf-8'))
    if hits:
        stale[f] = hits
changed = [f for f in files() if history[f][0] != Path(f).read_bytes()]
print(json.dumps({'rounds': rnd, 'changed_files': changed, 'stale_pins_by_file': stale}, indent=1))
