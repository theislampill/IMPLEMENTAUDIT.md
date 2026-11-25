"""Reproducible prospective G132 source change on b393a905 (run from a clean worktree at b393a905).

Edits:
  (a) G1 profile row for measured 20261116.133.1 with the ORIGINAL tool pins;
  (b) root provisioning step for the original git/bwrap binaries by exact package and binary hash;
  (c) sandboxed sender exec (fixed bwrap prefix, pinned launcher);
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


# (a) profile row
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

# (c) sandboxed sender
SANDBOX_DEFS = (
    "FD_LIMIT=4096\n"
    "SANDBOX='/usr/bin/bwrap'\n"
    "SANDBOX_PIN=dict(bytes=72160,sha256='e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71')\n"
    "SANDBOX_PREFIX=[SANDBOX,'--unshare-all','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL',\n"
    "  '--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin',\n"
    "  '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LC_ALL','C',\n"
    "  '--setenv','OPENSSL_CONF','/dev/null']\n")
SANDBOX_FN = (
    "def sandbox_current():\n"
    "    \"\"\"The fixed sandbox launcher: root-owned, not group/other-writable, exact pinned bytes.\"\"\"\n"
    "    info=os.stat(SANDBOX,follow_symlinks=False)\n"
    "    P.need(stat.S_ISREG(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022,'SENDER_SANDBOX_CUSTODY')\n"
    "    raw,_=F.read_file(Path(SANDBOX),1024*1024)\n"
    "    P.need(P.descriptor(raw)==SANDBOX_PIN,'SENDER_SANDBOX_PIN')\n"
    "    return True\n\n"
    "def close_plan(visible,kept,error_fd):")


def sender(s):
    s = once(s, "FD_LIMIT=4096\n", SANDBOX_DEFS)
    s = once(s, "    expected=['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',\n",
             "    expected=SANDBOX_PREFIX+['/usr/bin/openssl',\n")
    s = once(s, "def close_plan(visible,kept,error_fd):", SANDBOX_FN)
    s = once(s, "        validate_command(label,argv,fds)\n", "        validate_command(label,argv,fds);sandbox_current()\n")
    return once(s, "os.execve('/usr/bin/env',argv,{'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENSSL_CONF':'/dev/null'})",
                "os.execve(SANDBOX,argv,{})")


edit(f'{EP}/carrier/sender_capture.py', sender)

# (b) provisioning step
w = json.loads(Path(WF).read_bytes())
steps = w['jobs']['qualify']['steps']
assert steps[1]['name'] == 'Create exclusive fixed root island and exact packet' and steps[2]['name'] == 'Observe host tools'
script = (HERE / 'provision-step.sh').read_text().replace('${DRY_RUN:+exit 0}\n', '')
steps.insert(2, {'name': 'Provision original pinned git and bwrap', 'shell': 'bash', 'run': script})
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
