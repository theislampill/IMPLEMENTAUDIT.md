"""Rebind a dg16.g2-failed-capture-closed-catalog.v1 to a successor source (read-only git).
Literal/prefix references survive only on exactly unchanged lines (git diff -U0 hunks);
no new literal pattern is added. Tests are re-derived from the successor REPORT_SLOTS."""
import hashlib, json, re, subprocess, sys, types
repo, pred_path, target, slots_path, out = sys.argv[1:6]
def git(*a, text=False):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, check=True, text=text).stdout
sha = lambda raw: hashlib.sha256(raw).hexdigest()
enc = lambda v: (json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')
pred_raw = open(pred_path, 'rb').read(); pred = json.loads(pred_raw)
pc = pred['source_commit']
tc = git('rev-parse', target + '^{commit}', text=True).strip(); tt = git('rev-parse', tc + '^{tree}', text=True).strip()
def tree(c):
    rows = {}
    for line in git('ls-tree', '-r', '-z', c, text=True).split('\0'):
        if line:
            meta, path = line.split('\t', 1); rows[path] = meta.split()[2]
    return rows
ptree, ttree = tree(pc), tree(tc)
pfiles = {f['id']: f for f in pred['files']}
ppaths = {f['path'] for f in pred['files']}
excluded = {p for p in ptree if p.endswith(('.py', '.sh'))} - ppaths       # derived from predecessor
current = {p for p in ttree if p.endswith(('.py', '.sh')) and p not in excluded}
# Predecessor files keep their order/ids; new files are appended in path order.
paths = [f['path'] for f in pred['files'] if f['path'] in current] + sorted(current - ppaths)
files, newid, blobs = [], {}, {}
pid = {f['path']: f['id'] for f in pred['files']}
added = [p for p in paths if p not in pid]
for p in paths:
    raw = git('cat-file', 'blob', ttree[p]); blobs[p] = raw
    newid[p] = pid.get(p) or 'F%06d' % (len(pred['files']) + added.index(p))
    files.append({'bytes': len(raw), 'id': newid[p], 'lines': raw.count(b'\n'), 'path': p, 'sha256': sha(raw)})
import difflib
maps = {}
def line_map(path):
    if path in maps: return maps[path]
    if path not in ttree: maps[path] = None; return None
    if ptree.get(path) == ttree[path]: maps[path] = 'IDENTITY'; return 'IDENTITY'
    old = git('cat-file', 'blob', ptree[path]).splitlines(); new = git('cat-file', 'blob', ttree[path]).splitlines()
    table = {}
    for a, b, n in difflib.SequenceMatcher(None, old, new, autojunk=False).get_matching_blocks():
        for k in range(n): table[a + k + 1] = b + k + 1
    maps[path] = table; return table
def mapped(path, line):
    h = line_map(path)
    if h is None: return None
    if h == 'IDENTITY': return line
    return h.get(line)
dropped = 0
literals = []
for lit in pred['literals']:
    refs = []
    for fid, line, kind in lit['references']:
        path = pfiles[fid]['path']; new = mapped(path, line)
        if new is None or path not in newid: dropped += 1; continue
        refs.append([newid[path], new, kind])
    if refs: literals.append({**lit, 'references': refs})
prefixes = []
for row in pred['prefixes']:
    new = mapped(row['path'], row['line'])
    if new is None or row['path'] not in newid: dropped += 1; continue
    prefixes.append({**row, 'line': new})
slots_raw = open(slots_path, 'rb').read(); slots = json.loads(slots_raw)
tests = {}
for s in slots['slots']:
    for i, t in enumerate(s['tests']):
        raw = t['printed_identity'].encode(); tests.setdefault(sha(raw), [len(raw), []])[1].append([s['ordinal'], i])
prior = [t['sha256'] for t in pred['tests'] if t['sha256'] in tests]   # predecessor order kept; new appended
removed_tests = len(pred['tests']) - len(prior)
ids = {t['sha256']: t['id'] for t in pred['tests'] if t['sha256'] in tests}   # surviving ids kept (gaps stay)
for k, h in enumerate(sorted(set(tests) - set(ids))): ids[h] = 'T%06d' % (len(pred['tests']) + k)
order = prior + sorted(set(tests) - set(prior))
tests = [{'bytes': tests[h][0], 'id': ids[h], 'references': tests[h][1], 'sha256': h} for h in order]
owner_raw = blobs[pred['owner_path']]
module = compile(owner_raw, pred['owner_path'], 'exec', dont_inherit=True, optimize=0)
def walk(code):
    yield code
    for v in code.co_consts:
        if type(v) is types.CodeType: yield from walk(v)
codes = list(walk(module))
def site(row):
    found = [c for c in codes if c.co_qualname == row['name']]
    if len(found) != 1: raise SystemExit('OWNER_SITE_AMBIGUOUS ' + row['name'])
    lines = [l for _, _, l in found[0].co_lines() if l is not None]
    return {**row, 'first': found[0].co_firstlineno, 'last': max(lines)}
value = dict(pred)
value.update(files=files, literals=literals, prefixes=prefixes, tests=tests,
             owner_frames=[site(r) for r in pred['owner_frames']], observation_calls=[site(r) for r in pred['observation_calls']],
             owner_sha256=sha(owner_raw), source_commit=tc, source_tree=tt, report_slots_sha256=sha(slots_raw))
value['literal_scope'] = 'RETAINED_DECLARED_SOURCE_LITERALS_ONLY_ON_EXACT_UNCHANGED_LINES_IN_CURRENT_SOURCE; NEW_OR_CHANGED_MESSAGES_REMAIN_UNCLASSIFIED'
value['current_source_catalog_rebinding'] = {'changed_line_references_not_reused': dropped, 'complete_raw_stream_custody_unchanged': True,
    'new_literal_patterns_added': 0, 'unknowns_still_hashed_and_raw_private_streams_retained': True}
raw = enc(value); open(out, 'wb').write(raw)
print(sha(raw), len(raw), 'files', len(files), 'literals', len(literals), 'prefixes', len(prefixes), 'tests', len(tests), 'dropped', dropped, 'removed_tests', removed_tests,
      'frames', [(r['name'], r['first'], r['last']) for r in value['owner_frames'] + value['observation_calls']])
