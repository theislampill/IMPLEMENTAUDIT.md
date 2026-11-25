"""Independent cross-check of the provisioning step pins (no install, no execution of package code).

Usage: python3.12 -I -B check_provision_v2.py <git .deb> <workflow json>
Recomputes the git tree manifest digest straight from the package's tar members (a second implementation of
the step's bash manifest()), and checks the step embedded in the workflow carries the same pins.
"""
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile

deb, wf = sys.argv[1], sys.argv[2]
raw = open(deb, 'rb').read()
print('package', len(raw), hashlib.sha256(raw).hexdigest())
tar = subprocess.run(['/usr/bin/dpkg-deb', '--fsys-tarfile', deb], capture_output=True, check=True).stdout
lines, git_row = [], None
with tarfile.open(fileobj=io.BytesIO(tar)) as t:
    for m in t.getmembers():
        p = m.name[2:] if m.name.startswith('./') else m.name
        p = p.rstrip('/')
        if not (p == 'usr/bin/git' or p == 'usr/lib/git-core' or p.startswith('usr/lib/git-core/')):
            continue
        if m.issym():
            h, mode = hashlib.sha256(m.linkname.encode()).hexdigest(), 0o120777
        elif m.isfile():
            body = t.extractfile(m).read()
            h, mode = hashlib.sha256(body).hexdigest(), 0o100000 | m.mode
            if p == 'usr/bin/git':
                git_row = (len(body), h)
        elif m.isdir():
            h, mode = hashlib.sha256(b'').hexdigest(), 0o040000 | m.mode
        else:
            raise SystemExit('unexpected member type ' + p)
        lines.append((p, h, mode))
lines.sort(key=lambda r: r[0].encode())
digest = hashlib.sha256(''.join(f'{p} {h} {mode:o}\n' for p, h, mode in lines).encode()).hexdigest()
print('usr/bin/git', git_row)
print('tree entries', len(lines), 'digest', digest)
step = next(s for s in json.load(open(wf))['jobs']['qualify']['steps'] if s['name'] == 'Provision original pinned git program tree')
run = step['run']
pins = dict(re.findall(r'^(PKG_BYTES|PKG_SHA256|GIT_BYTES|GIT_SHA256|TREE_SHA256|URL)=\'?([^\'\n]+)\'?$', run, re.M))
print('step pins', json.dumps(pins, indent=1))
ok = (pins['PKG_BYTES'] == str(len(raw)) and pins['PKG_SHA256'] == hashlib.sha256(raw).hexdigest()
      and git_row == (int(pins['GIT_BYTES']), pins['GIT_SHA256'])
      and pins['GIT_SHA256'] == '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'
      and pins['TREE_SHA256'] == digest)
print('step uses sudo env -i form:', run.splitlines()[2].startswith('sudo /usr/bin/env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC '))
print('step mentions bwrap install:', bool(re.search(r'install[^\n]*bwrap|bwrap\.deb', run)))
print('ALL_PINS_AGREE', ok)
sys.exit(0 if ok else 1)
