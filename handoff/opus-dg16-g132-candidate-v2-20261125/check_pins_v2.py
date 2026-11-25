"""Pin check for the v2 tree (run from the worktree root).

For every 64-hex value in the in-scope files (workflow, entry, episode): classify it as the current sha256 of
an in-scope file, the baseline sha256 of a CHANGED in-scope file (stale), or other. For current-file hits,
compare the nearest preceding byte count (if any, within the same record) with the file size. Also check the
PUBLIC_PACKET_MANIFEST members exactly, and that verify_decrypt_record is byte-identical to the baseline.
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = 'b393a9057c249335e6cdf4ccbb898d192b0830b8'
EP = 'qualification/dg16-r5-g1-hosted-episode'
EN = 'qualification/dg16-r5-g1-hosted-entry'
WF = '.github/workflows/dg16-r5-g1-hosted-episode.yml'
ISSUED = {f'{EN}/BOOTSTRAP_ADMISSION.json', f'{EP}/carrier/CARRIER_ADMISSION.json', f'{EP}/INDEPENDENT_PROOF_PINS.json'}
files = [WF] + sorted(x.as_posix() for r in (EN, EP) for x in Path(r).rglob('*') if x.is_file())
cur = {f: Path(f).read_bytes() for f in files}
base = {f: subprocess.run(['git', 'show', f'{BASE}:{f}'], capture_output=True).stdout for f in files}
by_sha = {hashlib.sha256(b).hexdigest(): f for f, b in cur.items()}
stale_sha = {hashlib.sha256(base[f]).hexdigest(): f for f in files if base[f] != cur[f]}
report = {'checked_current_pins': 0, 'byte_mismatch': [], 'stale_non_issued': [], 'stale_issued': {}}
for f, b in cur.items():
    text = b.decode('utf-8', 'replace')
    for m in re.finditer(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])', text):
        h = m.group(0)
        if h in stale_sha:
            (report['stale_issued'].setdefault(f, []) if f in ISSUED else report['stale_non_issued']).append(
                f'{h[:12]} (baseline {stale_sha[h]})' if f in ISSUED else f'{f}: {h[:12]} (baseline {stale_sha[h]})')
        elif h in by_sha and f not in ISSUED:
            report['checked_current_pins'] += 1
            window = text[max(0, m.start() - 120):m.start()]
            counts = re.findall(r'bytes["\']?\s*[:=]\s*(\d+)', window)
            if counts and '}' not in window[window.rfind('bytes'):] and int(counts[-1]) != len(cur[by_sha[h]]):
                report['byte_mismatch'].append(f'{f}: {h[:12]} says {counts[-1]} actual {len(cur[by_sha[h]])}')
# Manifest members
man = json.loads(cur[f'{EN}/PUBLIC_PACKET_MANIFEST.json'])
bad = []
for name, row in man['members'].items():
    p = Path(EP) / name
    body = p.read_bytes() if p.is_file() else None
    if body is None or row['bytes'] != len(body) or row['sha256'] != hashlib.sha256(body).hexdigest():
        bad.append(name)
episode_files = {x.relative_to(EP).as_posix() for x in Path(EP).rglob('*') if x.is_file()}
report['manifest'] = dict(members=len(man['members']), mismatched=bad,
                          episode_files_not_listed=sorted(episode_files - set(man['members']))[:10],
                          listed_not_present=sorted(set(man['members']) - episode_files))


def fn_src(src, name):
    tree = ast.parse(src)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(src, node)


c_now = cur[f'{EP}/carrier/carrier.py'].decode()
c_base = base[f'{EP}/carrier/carrier.py'].decode()
report['verify_decrypt_record_unchanged'] = fn_src(c_now, 'verify_decrypt_record') == fn_src(c_base, 'verify_decrypt_record')
comp_now, comp_base = (json.loads(x[f'{EP}/carrier/CARRIER_COMPOSITION.json']) for x in (cur, base))
report['root_tools_unchanged'] = comp_now['root_tools'] == comp_base['root_tools']
report['host_tools_paths_unchanged'] = comp_now['host_tools']['paths'] == comp_base['host_tools']['paths']
report['sender_tools'] = comp_now['sender_tools']
print(json.dumps(report, indent=1))
sys.exit(1 if report['byte_mismatch'] or report['stale_non_issued'] or bad else 0)
