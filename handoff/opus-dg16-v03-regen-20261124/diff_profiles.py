import json, sys
old_rs, new_rs, old_or, new_or = (json.load(open(p, encoding='utf8')) for p in sys.argv[1:5])
out = []
p = out.append
total = lambda d: sum(s['test_count'] for s in d['slots'])
p('slots %d -> %d; tests %d -> %d' % (old_rs['slot_count'], new_rs['slot_count'], total(old_rs), total(new_rs)))
key = lambda s: (s['wrapper'], s['invocation'])
olds = {key(s): s for s in old_rs['slots']}
news = {key(s): s for s in new_rs['slots']}
for k in news:
    if k not in olds:
        p('ADDED SLOT %d %s:%d %s (%d tests)' % (news[k]['ordinal'], k[0], news[k]['line'], news[k]['program'], news[k]['test_count']))
for k in olds:
    if k not in news:
        p('REMOVED SLOT %d %s:%d %s' % (olds[k]['ordinal'], k[0], olds[k]['line'], olds[k]['program']))
for k, n in news.items():
    o = olds.get(k)
    if not o:
        continue
    head = 'slot %d->%d %s' % (o['ordinal'], n['ordinal'], n['program'])
    notes = []
    for f in ('line', 'verbosity', 'derivation', 'registry_node'):
        if o[f] != n[f]:
            notes.append('%s %r->%r' % (f, o[f], n[f]))
    oi = [t['id'] for t in o['tests']]; ni = [t['id'] for t in n['tests']]
    added = [i for i in ni if i not in oi]; removed = [i for i in oi if i not in ni]
    if oi != ni and not added and not removed:
        notes.append('order changed')
    od = {t['id']: t for t in o['tests']}
    desc = [i for i in ni if i in od and od[i] != [t for t in n['tests'] if t['id'] == i][0]]
    if desc:
        notes.append('description changed: ' + ', '.join(desc))
    if o.get('source_class_groups') != n.get('source_class_groups'):
        notes.append('source_class_groups changed')
    if o.get('source_inline_stderr') != n.get('source_inline_stderr'):
        oinl = [(r['test_id'], r['body_base64'], r['source']['sha256']) for r in o.get('source_inline_stderr', [])]
        ninl = [(r['test_id'], r['body_base64'], r['source']['sha256']) for r in n.get('source_inline_stderr', [])]
        notes.append('source_inline_stderr changed (%s)' % ('source pin only' if [x[:2] for x in oinl] == [x[:2] for x in ninl] else 'content'))
    if added or removed or notes:
        p(head + ' tests %d->%d' % (o['test_count'], n['test_count']) + ('; ' + '; '.join(notes) if notes else ''))
        for i in added: p('    + ' + i)
        for i in removed: p('    - ' + i)
oc, nc = old_rs['source_closure'], new_rs['source_closure']
add = sorted(set(nc) - set(oc)); rem = sorted(set(oc) - set(nc))
changed = sorted(k for k in nc if k in oc and nc[k] != oc[k])
p('closure %d -> %d: +%d added, -%d removed, %d re-pinned' % (len(oc), len(nc), len(add), len(rem), len(changed)))
for k in add: p('    + ' + k)
for k in rem: p('    - ' + k)
for k in changed:
    m = ' mode %s->%s' % (oc[k]['mode'], nc[k]['mode']) if oc[k]['mode'] != nc[k]['mode'] else ''
    p('    ~ %s (%d->%d bytes%s)' % (k, oc[k]['bytes'], nc[k]['bytes'], m))
p('OUTPUT_ROLES:')
for k in sorted(set(old_or) | set(new_or)):
    if old_or.get(k) == new_or.get(k):
        continue
    if k == 'source_files':
        for f in sorted(new_or[k]):
            if new_or[k][f] != old_or[k].get(f):
                p('    source_files ~ %s (%d->%d bytes)' % (f, old_or[k][f]['bytes'], new_or[k][f]['bytes']))
    elif k == 'turn_disposition_cases':
        oc_ = [json.dumps(r, sort_keys=True) for r in old_or[k]]; nc_ = [json.dumps(r, sort_keys=True) for r in new_or[k]]
        p('    turn_disposition_cases %d -> %d' % (len(oc_), len(nc_)))
        for r in nc_:
            if r not in oc_: p('      + ' + r)
        for r in oc_:
            if r not in nc_: p('      - ' + r)
        if [r for r in oc_ if r in nc_] != [r for r in nc_ if r in oc_]: p('      (order changed)')
    else:
        p('    %s: %s -> %s' % (k, json.dumps(old_or.get(k), sort_keys=True)[:600], json.dumps(new_or.get(k), sort_keys=True)[:600]))
print('\n'.join(out))
