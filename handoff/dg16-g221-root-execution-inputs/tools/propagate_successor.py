#!/usr/bin/env python3
"""Propagate a successor episode's identities through an author universe, then close the pin chain.

Mechanical text and digest propagation only. It issues nothing: the regenerated SEAL.json, PROTECTED_RECIPIENT.json and
CURRENT_HOST_QUALIFICATION_REQUEST.json are PROPOSED BYTES that become Root records only when Root (or the designated
successor) adopts them. Writes only into a fresh output directory.

Seeds (the only non-digest edits):
  1. every occurrence of the previous host branch / control branch name -> the successor names (same file set that
     hardcodes them: workflow filter, run.py, protected_bridge.py, live_control.py, PROTECTED_RECIPIENT.json, the
     request, receiver/root_common.py, both binding templates, HOST_PROFILE_BINDING_REQUIREMENTS.json);
  2. PROTECTED_RECIPIENT.pem replaced by the supplied PUBLIC certificate (refused if it carries anything but exactly
     one CERTIFICATE block);
  3. optional, OFF by default, owner-designation gated: --old-issuer-thread/--new-issuer-thread (see RUNBOOK section 0).

Then the same fixpoint as regen_chain.py (same JSON-style rule, same refusals), generalised to several seed files and
to Python-literal {'bytes': N, 'sha256': S} descriptors (protected_bridge.py), which regen_chain.py never had to touch.

usage: propagate_successor.py <universe-in> <universe-out> <report.json>
         --old-host-branch B --new-host-branch B --old-control-branch B --new-control-branch B --recipient-cert PEM
         [--old-issuer-thread UUID --new-issuer-thread UUID_OR_PRO-EXECUTOR-01]
"""
import argparse, ast, hashlib, json, re, shutil
from collections import OrderedDict
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('src', type=Path); p.add_argument('dst', type=Path); p.add_argument('report', type=Path)
for name in ('old-host-branch', 'new-host-branch', 'old-control-branch', 'new-control-branch'): p.add_argument('--' + name, required=True)
p.add_argument('--recipient-cert', type=Path, required=True)
p.add_argument('--old-issuer-thread'); p.add_argument('--new-issuer-thread')
a = p.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
blob = lambda raw: hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
BRANCH = r'pro/dg16-r5-full-g2-direct-%s-[0-9]+-[0-9]{8}'
assert re.fullmatch(BRANCH % 'host', a.new_host_branch) and re.fullmatch(BRANCH % 'control', a.new_control_branch), 'BRANCH_NAME_SHAPE'
assert a.new_control_branch == a.new_host_branch.replace('-host-', '-control-'), 'CONTROL_MUST_BE_HOST_WITH_control (current_host.validate_request)'
assert a.new_host_branch != a.old_host_branch and a.new_control_branch != a.old_control_branch, 'SUCCESSOR_BRANCH_MUST_DIFFER'
assert bool(a.old_issuer_thread) == bool(a.new_issuer_thread), 'ISSUER_PAIR'
cert = a.recipient_cert.read_bytes()
assert cert.count(b'-----BEGIN CERTIFICATE-----') == 1 and cert.count(b'-----END CERTIFICATE-----') == 1 and cert.count(b'-----BEGIN') == 1 \
    and b'PRIVATE' not in cert and 0 < len(cert) <= 8192, 'RECIPIENT_MUST_BE_EXACTLY_ONE_PUBLIC_CERTIFICATE'
original = {q.relative_to(a.src).as_posix(): q.read_bytes() for q in sorted(a.src.rglob('*')) if q.is_file()}
PEM = 'candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/PROTECTED_RECIPIENT.pem'
assert PEM in original
swaps = [(a.old_host_branch.encode(), a.new_host_branch.encode()), (a.old_control_branch.encode(), a.new_control_branch.encode())]
if a.new_issuer_thread:
    assert a.new_issuer_thread == 'PRO-EXECUTOR-01' or re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', a.new_issuer_thread), 'ISSUER_THREAD_SHAPE'
    swaps.append((a.old_issuer_thread.encode(), a.new_issuer_thread.encode()))
seeded, seeds = {}, {}
for name, raw in original.items():
    out = cert if name == PEM else raw
    counts = {}
    for old, new in swaps:
        if old in out: counts[old.decode()] = out.count(old); out = out.replace(old, new)
    seeded[name] = out
    if out != raw: seeds[name] = counts or 'recipient certificate replaced'
for name in seeds:
    assert not name.endswith(('SOURCE_MANIFEST.json', 'REPORT_SLOTS.json', 'CAPTURE_DIAGNOSTIC_CATALOG.json')), 'SEED_IN_FROZEN_BASE_DATA ' + name
STYLES = [dict(indent=2, sort_keys=True), dict(indent=2, sort_keys=False), dict(sort_keys=True), dict(sort_keys=False),
          dict(indent=2, sort_keys=True, ensure_ascii=False), dict(sort_keys=True, separators=(',', ':'))]
PYDESC = re.compile(rb"\{'bytes': (\d+), 'sha256': '([0-9a-f]{64})'\}")


def json_style(raw):
    try: value = json.loads(raw, object_pairs_hook=OrderedDict)
    except ValueError: return None
    for style in STYLES:
        for tail in ('\n', ''):
            if (json.dumps(value, **style) + tail).encode() == raw: return value, style, tail
    return None


def rewrite(name, raw, mapping):
    """mapping: old_sha -> (new_sha, old_bytes, new_bytes); raw is the SEEDED body, which still names old digests."""
    if not any(old.encode() in raw for old in mapping): return raw
    styled = json_style(raw) if name.endswith('.json') else None
    if styled is None:
        assert not name.endswith('.json'), 'non-canonical JSON carries a changed pin: ' + name

        def descriptor(match):
            size, digest = int(match.group(1)), match.group(2).decode()
            if digest not in mapping: return match.group(0)
            new, old_bytes, new_bytes = mapping[digest]
            assert size == old_bytes, (name, digest, size, old_bytes)
            return b"{'bytes': %d, 'sha256': '%s'}" % (new_bytes, new.encode())
        raw = PYDESC.sub(descriptor, raw)
        for old, (new, old_bytes, new_bytes) in mapping.items(): raw = raw.replace(old.encode(), new.encode())
        return raw
    value, style, tail = styled

    def walk(node):
        if isinstance(node, dict):
            for key, item in list(node.items()):
                if isinstance(item, str) and item in mapping:
                    new, old_bytes, new_bytes = mapping[item]; node[key] = new
                    if key == 'sha256' and 'bytes' in node:
                        assert node['bytes'] == old_bytes, (name, key, node['bytes'], old_bytes)
                        node['bytes'] = new_bytes
                else: walk(item)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                if isinstance(item, str) and item in mapping: node[index] = mapping[item][0]
                else: walk(item)
    walk(value)
    out = (json.dumps(value, **style) + tail).encode()
    assert not any(old.encode() in out for old in mapping), 'unreplaced digest (key or embedded text) in ' + name
    return out


for name in seeds:
    if name.endswith('.json'): assert json_style(seeded[name]) is not None, 'seed broke canonical JSON: ' + name
current = dict(seeded)
for round_number in range(1, 48):
    mapping = {sha(original[name]): (sha(current[name]), len(original[name]), len(current[name]))
               for name in original if current[name] != original[name]}
    updated = {name: rewrite(name, seeded[name], mapping) for name in original}
    if updated == current: break
    current = updated
else: raise SystemExit('no fixpoint')
changed = [name for name in original if current[name] != original[name]]
old_shas = {sha(original[name]): name for name in changed}; old_blobs = {blob(original[name]): name for name in changed}
by_sha = {sha(raw): len(raw) for raw in current.values()}
for name, raw in current.items():
    for digest, owner in old_shas.items(): assert digest.encode() not in raw, 'stale sha256 of %s in %s' % (owner, name)
    for digest, owner in old_blobs.items(): assert digest.encode() not in raw, 'git blob pin of changed %s in %s' % (owner, name)
    for old, new in swaps: assert old not in raw, 'previous identity survives in ' + name
    for match in PYDESC.finditer(raw):  # every Python-literal descriptor of a universe file states its real size
        digest = match.group(2).decode()
        if digest in by_sha: assert int(match.group(1)) == by_sha[digest], 'stale bytes in Python descriptor: ' + name
Q = 'candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/'
adoption = json.loads(current[Q + 'PROTECTED_RECIPIENT.json'])
literal = {n.targets[0].id: n.value for n in ast.parse(current[Q + 'protected_bridge.py']).body
           if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
joins = {
    'adoption.recipient == descriptor(new certificate)': adoption['recipient'] == dict(bytes=len(cert), sha256=sha(cert)),
    'adoption.branch / control_branch == successor names': (adoption['branch'], adoption['control_branch']) == (a.new_host_branch, a.new_control_branch),
    'protected_bridge.HOST_SELECTION_EXPECTED == adoption body': ast.literal_eval(literal['HOST_SELECTION_EXPECTED']) == adoption,
    'protected_bridge.SELECTION_SHA == sha256(PROTECTED_RECIPIENT.json)': ast.literal_eval(literal['SELECTION_SHA']) == sha(current[Q + 'PROTECTED_RECIPIENT.json']),
    'protected_bridge BRANCH / CONTROL_BRANCH': (ast.literal_eval(literal['BRANCH']), ast.literal_eval(literal['CONTROL_BRANCH'])) == (a.new_host_branch, a.new_control_branch),
    'workflow filter names the successor host branch only': current['candidate-e76-source-01/candidate/public/.github/workflows/dg16-r5-full-g2.yml'].count(a.new_host_branch.encode()) >= 1,
}
assert all(joins.values()), joins
if a.dst.exists(): raise SystemExit('FRESH_OUTPUT_REQUIRED: ' + str(a.dst))
shutil.copytree(a.src, a.dst)
rows = []
for name in sorted(changed):
    (a.dst / name).chmod(0o644); (a.dst / name).write_bytes(current[name])
    rows.append({'path': name, 'seed': seeds.get(name), 'before': {'bytes': len(original[name]), 'sha256': sha(original[name])},
                 'after': {'bytes': len(current[name]), 'sha256': sha(current[name]), 'git_blob': blob(current[name])}})
report = {'authority': 'NONE', 'rounds': round_number, 'changed_files': len(rows), 'unchanged_files': len(original) - len(rows),
          'host_branch': a.new_host_branch, 'control_branch': a.new_control_branch, 'recipient': dict(bytes=len(cert), sha256=sha(cert)),
          'issuer_thread_rebound': bool(a.new_issuer_thread), 'joins': joins, 'changes': rows}
a.report.write_text(json.dumps(report, indent=1) + '\n')
for row in rows: print('%-112s %s -> %s%s' % (row['path'][-112:], row['before']['sha256'][:8], row['after']['sha256'][:8], '  SEED' if row['seed'] else ''))
print('rounds', round_number, 'changed', len(rows), 'unchanged', len(original) - len(rows), 'joins', sum(joins.values()), '/', len(joins))
