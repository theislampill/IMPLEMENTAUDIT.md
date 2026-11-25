"""Local, read-only V21 derivation of the computable G1/G3 inputs.

NO EXISTING PRODUCER WAS FOUND IN REPO HISTORY for NATIVE_SOURCE_APPLICABILITY.json
or SOURCE_ACQUISITION.json / SOURCE_MANIFEST.json. This is a minimal reimplementation
derived strictly from the consumers (native_prerequisite.source_applicability,
host_composition.require_launch, g3_receiving receive_* at b393a905 and 4ef93671).
Every producer is first validated by byte-exact (or digest-exact) reproduction of a
historical committed value before being applied to V21. Nothing here grants authority.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
V21 = '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d'
V21_TREE = '53498df783ed441744ae5080982c2d5e59c34bbc'
E76 = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
RETAINED_NATIVE = '3e0f4b6d05eb086017ce721d40459fdbd68714dd'
PACKAGE = '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
M5 = '205aeab7c93299b0666b261485ab5658d8e183de'
MAINTAINED = 'c53ed7de85de22ce313233472c8d8f02ad8e9d02'
HIST = 'b393a9057c249335e6cdf4ccbb898d192b0830b8'
HIST_DIR = 'qualification/dg16-r5-g1-hosted-episode'
MAINT_CONSUMER = '4ef93671303b44f476e87b8dc759cf5efd3a6add'
BUILD_OWNERS = ['scripts/build-release-asset.sh', 'scripts/check-package-contract.sh',
                'scripts/package-contract.py', 'scripts/write-release-checksums.sh']
PRODUCER_PATHS = BUILD_OWNERS[:2] + ['scripts/package-contract.py', 'scripts/write-release-checksums.sh',
                                     'requirements-release.txt', 'package/implementaudit-package.json']
CHECKS = []


def check(label, ok, detail=''):
    CHECKS.append(dict(check=label, ok=bool(ok), detail=detail))
    print(('PASS ' if ok else 'FAIL ') + label + (' :: ' + str(detail) if detail else ''))


def git(*args):
    return subprocess.check_output(['git', '--git-dir', str(REPO), *args])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):  # g3_receiving.encode / evidence_io canonical compact
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def manifest_encode(value):  # spelling proven by g3_receiving ACTUAL_PRIOR_MANIFEST_BYTES
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def blob(spec):
    return git('cat-file', 'blob', spec)


_rows = {}


def rows(commit):
    """Every tracked entry: path, bytes, git_blob, mode, sha256 (actual bytes)."""
    if commit in _rows:
        return _rows[commit]
    listing = git('ls-tree', '-r', '-z', '--full-tree', commit).split(b'\0')
    entries = []
    for item in listing:
        if not item:
            continue
        meta, path = item.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob':
            raise SystemExit(f'non-blob entry {kind} {path!r}')
        entries.append((path.decode('utf-8'), mode, oid))
    proc = subprocess.Popen(['git', '--git-dir', str(REPO), 'cat-file', '--batch'],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    import threading

    def feed():
        proc.stdin.write(''.join(oid + '\n' for _, _, oid in entries).encode())
        proc.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    out = {}
    for path, mode, oid in entries:
        header = proc.stdout.readline().split()
        size = int(header[2])
        data = proc.stdout.read(size)
        proc.stdout.read(1)
        out[path] = dict(path=path, bytes=len(data), git_blob=oid, mode=mode, sha256=sha(data))
    proc.wait()
    _rows[commit] = out
    return out


def commit_fields(commit):
    text = git('cat-file', 'commit', commit).decode()
    head = text.split('\n\n', 1)[0].splitlines()
    tree = [l.split()[1] for l in head if l.startswith('tree ')][0]
    parents = [l.split()[1] for l in head if l.startswith('parent ')]
    return tree, parents


def manifest(commit):
    tree, parents = commit_fields(commit)
    assert len(parents) == 1, parents
    parent_tree = commit_fields(parents[0])[0]
    members = [rows(commit)[p] for p in sorted(rows(commit), key=lambda x: x.split('/'))]  # committed order
    return dict(schema='dg16.inner-owner.cumulative-source-candidate.v1', commit=commit, tree=tree,
                parent_commit=parents[0], parent_tree=parent_tree, file_count=len(members),
                total_bytes=sum(r['bytes'] for r in members), members=members)


def consts(spec, names):
    out = {}
    for node in ast.parse(blob(spec)).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    out[target.id] = ast.literal_eval(node.value)
                if isinstance(target, ast.Tuple):
                    for i, elt in enumerate(target.elts):
                        if isinstance(elt, ast.Name) and elt.id in names:
                            out[elt.id] = ast.literal_eval(node.value.elts[i])
    return out


def delta(new, old):
    a, b = rows(new), rows(old)
    return [dict(path=p, before=b.get(p), after=a.get(p)) for p in sorted(set(a) | set(b)) if a.get(p) != b.get(p)]


def canonical_paths(commit):
    """artifact_payload_entries(canonical_plugin) source paths, builder order."""
    r = rows(commit)
    skill = sorted(p for p in r if p.startswith('skills/implementaudit/'))
    children = [f'skills/{n}/SKILL.md' for n in ('audit-state', 'audit-assess', 'audit-implement', 'audit-andon')]
    return ['.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
            'package/implementaudit-package.json'] + skill + children


def strip(row):
    return {k: row[k] for k in ('bytes', 'git_blob', 'mode', 'sha256')}


# ---------------------------------------------------------------- 1. SOURCE_MANIFEST
hist_manifest_raw = blob(f'{HIST}:{HIST_DIR}/SOURCE_MANIFEST.json')
e76_raw = manifest_encode(manifest(E76))
check('manifest producer reproduces committed e76 SOURCE_MANIFEST.json byte-for-byte',
      e76_raw == hist_manifest_raw, f'{len(e76_raw)} bytes sha256 {sha(e76_raw)}')
scope = json.loads(blob(f'{HIST}:{HIST_DIR}/ORIGINAL_SCOPE.json'))
check('e76 manifest sha256 == ORIGINAL_SCOPE.source_inventory_sha256',
      sha(e76_raw) == scope['source_inventory_sha256'], scope['source_inventory_sha256'])
mc = consts(f'{MAINT_CONSUMER}:{HIST_DIR}/g3_receiving.py',
            {'MAINTAINED_MEMBERS_SHA256', 'M5_TO_MAINTAINED_SHA256', 'E76_TO_MAINTAINED_SHA256',
             'CANONICAL_PACKAGE_PATHS_SHA256', 'MAINTAINED_SOURCE_FILES', 'MAINTAINED_SOURCE_BYTES',
             'MAINTAINED_SOURCE_PARENT', 'MAINTAINED_PARENT_TREE', 'EXECUTING_SOURCE_BINDINGS',
             'PRIOR_PACKAGE_SOURCE_ROWS'})
mm = manifest(MAINTAINED)
check('maintained c53ed7de members digest == MAINTAINED_MEMBERS_SHA256',
      sha(encode(sorted(mm['members'], key=lambda r: r['path']))) == mc['MAINTAINED_MEMBERS_SHA256'], mc['MAINTAINED_MEMBERS_SHA256'])
check('maintained header (files/bytes/parent/parent_tree)',
      (mm['file_count'], mm['total_bytes'], mm['parent_commit'], mm['parent_tree']) ==
      (mc['MAINTAINED_SOURCE_FILES'], mc['MAINTAINED_SOURCE_BYTES'], mc['MAINTAINED_SOURCE_PARENT'],
       mc['MAINTAINED_PARENT_TREE']))
m5_delta = delta(MAINTAINED, M5)
check('maintained-vs-M5 delta digest == M5_TO_MAINTAINED_SHA256 (16 rows)',
      len(m5_delta) == 16 and sha(encode(m5_delta)) == mc['M5_TO_MAINTAINED_SHA256'], len(m5_delta))
e76_rows = [r for r in m5_delta if r['path'] not in mc['PRIOR_PACKAGE_SOURCE_ROWS']]
check('maintained e76-subset digest == E76_TO_MAINTAINED_SHA256 (14 rows)',
      len(e76_rows) == 14 and sha(encode(e76_rows)) == mc['E76_TO_MAINTAINED_SHA256'], len(e76_rows))
ORDERS = {'builder': lambda l: l, 'sorted': sorted, 'split': lambda l: sorted(l, key=lambda x: x.split('/'))}
cp_m = canonical_paths(MAINTAINED)
cp_order = [k for k, f in ORDERS.items() if sha(encode(f(cp_m))) == mc['CANONICAL_PACKAGE_PATHS_SHA256']]
cp_ok = len(cp_m) == 74 and bool(cp_order)
if cp_ok:
    _f = ORDERS[cp_order[0]]
    _cp = canonical_paths
    canonical_paths = lambda c: _f(_cp(c))
check('canonical package path derivation == CANONICAL_PACKAGE_PATHS_SHA256 (74)', cp_ok, (len(cp_m), cp_order))

v21 = manifest(V21)
check('V21 tree identity', v21['tree'] == V21_TREE, v21['tree'])
v21_raw = manifest_encode(v21)
(OUT / 'SOURCE_MANIFEST.V21.json').write_bytes(v21_raw)

# ---------------------------------------------------------------- 2. NATIVE_SOURCE_APPLICABILITY
hist_app_raw = blob(f'{HIST}:{HIST_DIR}/NATIVE_SOURCE_APPLICABILITY.json')
hist_app = json.loads(hist_app_raw)
paths = [m['path'] for m in hist_app['members']]


def applicability(current, carried):
    cur, ret = rows(current), rows(RETAINED_NATIVE)
    members = []
    for p in paths:
        c = strip(cur[p]) if p in cur else None
        r = strip(ret[p]) if p in ret else None
        members.append(dict(path=p, current=c, retained=r, retained_unchanged=(c == r)))
    value = dict(carried, members=members, source_commit=current, source_tree=commit_fields(current)[0],
                 retained_source_commit=RETAINED_NATIVE,
                 unchanged_count=sum(m['retained_unchanged'] for m in members),
                 changed_count=sum(not m['retained_unchanged'] for m in members))
    return value


carried = {k: v for k, v in hist_app.items() if k not in ('members',)}
re_e76 = encode(applicability(E76, carried))
check('applicability producer reproduces committed e76 NATIVE_SOURCE_APPLICABILITY.json byte-for-byte',
      re_e76 == hist_app_raw, f'{len(hist_app_raw)} bytes sha256 {sha(hist_app_raw)}')

UNDETERMINED = ('compiler_normalized_ast_sha256', 'receiver_non_windows_ast_sha256', 'semantic_report_sha256',
                'scope', 'fixture_repair')
v21_carried = {k: v for k, v in carried.items() if k not in UNDETERMINED}
v21_app = applicability(V21, v21_carried)
v21_app_raw = encode(v21_app)
(OUT / 'NATIVE_SOURCE_APPLICABILITY.V21-COMPUTABLE.json').write_bytes(v21_app_raw)
changed = [m for m in v21_app['members'] if not m['retained_unchanged']]
missing = [m['path'] for m in v21_app['members'] if m['current'] is None]

# AST hypothesis probe (reported only; never written into the artifact).
def ast_variants(raw, owner_names):
    tree = ast.parse(raw)
    out = {'plain_dump': sha(ast.dump(tree).encode())}
    t2 = ast.parse(raw)
    t2.body = [n for n in t2.body if not (isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id in owner_names for t in n.targets))]
    out['owner_pin_assigns_removed'] = sha(ast.dump(t2).encode())
    t3 = ast.parse(raw)
    for n in t3.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in owner_names for t in n.targets):
            n.value = ast.Constant(None)
    out['owner_pin_values_none'] = sha(ast.dump(t3).encode())
    return out


names = {'_NATIVE_STATIC_OWNER_SHA256', '_NATIVE_STATIC_OWNER_BYTES'}
comp = 'skills/implementaudit/scripts/compile-work-graph.py'
probe = {c: ast_variants(blob(f'{c}:{comp}'), names) for c in (E76, RETAINED_NATIVE)}
hit = [(c, k) for c, d in probe.items() for k, v in d.items() if v == hist_app['compiler_normalized_ast_sha256']]
check('compiler_normalized_ast_sha256 reproducible by a tested normalization (python ' + sys.version.split()[0] + ')',
      bool(hit), hit or 'no tested variant matched; value NOT computed for V21')

# ---------------------------------------------------------------- 3. SOURCE_ACQUISITION computable parts
cur = rows(V21)
cp_v21 = canonical_paths(V21)
deps_v21 = sorted(set(cp_v21) | set(PRODUCER_PATHS))
dep_rows = {p: cur.get(p) for p in deps_v21}


def changed_vs(old, plist):
    o = rows(old)
    return sorted(p for p in plist if o.get(p) != cur.get(p))


m5_v21 = delta(V21, M5)
e76_v21 = delta(V21, E76)
pkg_v21 = [dict(path=r['path'], current=r['after'], retained=r['before']) for r in delta(V21, PACKAGE)]
exe = mc['EXECUTING_SOURCE_BINDINGS']
exec_v21 = {p: ({'bytes': cur[p]['bytes'], 'sha256': cur[p]['sha256']} if p in cur else None) for p in exe}
acq = dict(
    note='COMPUTABLE PARTS ONLY; not a SOURCE_ACQUISITION body. Root/receiver-issued records are absent by design.',
    commit=V21, tree=v21['tree'], parent_commit=v21['parent_commit'], parent_tree=v21['parent_tree'],
    files=v21['file_count'], bytes=v21['total_bytes'],
    manifest=dict(bytes=len(v21_raw), sha256=sha(v21_raw)), manifest_sha256=sha(v21_raw),
    members_sha256=sha(encode(sorted(v21['members'], key=lambda r: r['path']))),
    canonical_inputs=dict(count=len(cp_v21), sha256=sha(encode(cp_v21)), derivation_validated=cp_ok),
    dependency_files=len(deps_v21),
    dependencies_changed_vs_package_8ee4=changed_vs(PACKAGE, deps_v21),
    dependencies_changed_vs_m5_205a=changed_vs(M5, deps_v21),
    dependencies_changed_vs_e76=changed_vs(E76, deps_v21),
    dependencies_changed_vs_maintained_c53e=changed_vs(MAINTAINED, deps_v21),
    build_owners_changed_vs_m5=changed_vs(M5, BUILD_OWNERS),
    source_delta_vs_package_8ee4=dict(rows=len(pkg_v21), sha256=sha(encode(pkg_v21)),
                                      unchanged_files=v21['file_count'] - sum(1 for r in pkg_v21 if r['current']),
                                      added=sum(1 for r in pkg_v21 if r['retained'] is None),
                                      deleted=sum(1 for r in pkg_v21 if r['current'] is None)),
    changes_vs_m5=dict(rows=len(m5_v21), sha256=sha(encode(m5_v21))),
    changes_vs_e76=dict(rows=len(e76_v21), sha256=sha(encode(e76_v21))),
    executing_source_bindings_at_v21=exec_v21,
    executing_source_bindings_changed_vs_4ef9=sorted(p for p in exe if exec_v21[p] != exe[p]),
)
(OUT / 'SOURCE_ACQUISITION.V21-COMPUTABLE-PARTS.json').write_bytes(encode(acq))
(OUT / 'SOURCE_DELTA_ROWS.V21-vs-8ee4.json').write_bytes(encode(pkg_v21))
(OUT / 'CHANGES.V21-vs-M5.json').write_bytes(encode(m5_v21))
(OUT / 'CHANGES.V21-vs-e76.json').write_bytes(encode(e76_v21))
(OUT / 'PACKAGE_DEPENDENCY_ROWS.V21.json').write_bytes(encode(dep_rows))

summary = dict(checks=CHECKS,
               v21_manifest=dict(files=v21['file_count'], bytes=v21['total_bytes'], sha256=sha(v21_raw),
                                 size=len(v21_raw), parent=v21['parent_commit'], parent_tree=v21['parent_tree']),
               v21_applicability=dict(changed=v21_app['changed_count'], unchanged=v21_app['unchanged_count'],
                                      changed_paths=[m['path'] for m in changed], missing_at_v21=missing,
                                      sha256=sha(v21_app_raw), size=len(v21_app_raw),
                                      undetermined_fields=list(UNDETERMINED)),
               ast_probe=probe,
               acquisition=acq)
(OUT / 'SUMMARY.json').write_bytes(encode(summary))
print(json.dumps({k: v for k, v in summary.items() if k != 'checks'}, indent=1))
sys.exit(0 if all(c['ok'] for c in CHECKS if 'ast' not in c['check']) else 3)
