"""Fixed-point rebinding of SHA-256 (+ adjacent byte-count) pins in the G132 packet. Issued records untouched."""
import json
import hashlib, re, subprocess, sys
from pathlib import Path
BASE = 'b393a9057c249335e6cdf4ccbb898d192b0830b8'
ISSUED = {'qualification/dg16-r5-g1-hosted-entry/BOOTSTRAP_ADMISSION.json',
          'qualification/dg16-r5-g1-hosted-episode/carrier/CARRIER_ADMISSION.json',
          'qualification/dg16-r5-g1-hosted-episode/INDEPENDENT_PROOF_PINS.json'}
ROOTS = ['.github/workflows/dg16-r5-g1-hosted-episode.yml', 'qualification/dg16-r5-g1-hosted-entry', 'qualification/dg16-r5-g1-hosted-episode']
def files():
    out = []
    for r in ROOTS:
        p = Path(r)
        out += [p] if p.is_file() else sorted(x for x in p.rglob('*') if x.is_file())
    return [x.as_posix() for x in out]
def base_bytes(path):
    r = subprocess.run(['git', 'show', f'{BASE}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None
sha = lambda b: hashlib.sha256(b).hexdigest()

hist = {}   # file -> list of (bytes,len) versions seen, base first
for f in files():
    b = base_bytes(f)
    hist[f] = [b] if b is not None else []
# reconstruct intermediates is impossible now; instead treat every 64-hex pin that is NOT the current sha of any file
# and IS the sha of the base of some file as stale, and also detect pins that match no file version at all near a filename.
cur = {f: Path(f).read_bytes() for f in files()}
cursha = {sha(b): f for f, b in cur.items()}
basesha = {sha(b[0]): f for f, b in hist.items() if b}
report = {}
for f in files():
    t = cur[f].decode('utf-8', 'replace')
    for h in set(re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])', t)):
        if h in cursha: continue
        if h in basesha and basesha[h] in cur and sha(cur[basesha[h]]) != h:
            report.setdefault(f, []).append(('BASE_OF', basesha[h]))
print(json.dumps(report, indent=1))
# check every packet-file name mentioned with a sha in manifests/compositions resolves to current
for f in ['qualification/dg16-r5-g1-hosted-entry/PUBLIC_PACKET_MANIFEST.json','qualification/dg16-r5-g1-hosted-episode/carrier/CARRIER_COMPOSITION.json']:
    d = json.loads(cur[f]); bad = []
    def walk(v, path=''):
        if isinstance(v, dict):
            if 'sha256' in v and isinstance(v.get('sha256'), str):
                name = path.split('/')[-1]
                cands = [g for g in cur if g.endswith('/' + name) or g == name]
                if len(cands) == 1 and sha(cur[cands[0]]) != v['sha256']: bad.append((path, cands[0], v.get('bytes'), len(cur[cands[0]])))
                if len(cands) == 1 and 'bytes' in v and v['bytes'] != len(cur[cands[0]]): bad.append(('BYTES', path))
            for k, x in v.items(): walk(x, path + '/' + str(k))
        elif isinstance(v, list):
            for i, x in enumerate(v): walk(x, path + '/' + str(i))
    walk(d); print(f, 'mismatches:', bad)
