#!/usr/bin/env python3
"""Mechanical encoder for the record bodies of one G2 episode. Authority NONE.

It computes bytes; it does not issue, adopt, review or seal anything. A body becomes a Root record, an independent
review or a seal only when the named actor actually performs that act and takes custody of the bytes. Every identity
label is a required argument with no default, and an unfilled <PLACEHOLDER> is refused. Every schema and fixed field
value below is the one in G220's actual document of the same kind (g220-custody/); the G220 documents are reproduced
byte-for-byte by this encoder in rehearsal/ (that is the evidence for each schema).

Encoding of every body: json.dumps(sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + newline.

subcommands (each writes exactly one fresh file, or a fresh directory for reviews/adoptions):
  runtime           PUBLIC_RUNTIME.json                       [ROOT-SUCCESSOR]
  candidate-seal    candidate SEAL.json / CANDIDATE_SEAL.json [ROOT-SUCCESSOR]
  reviews           INDEPENDENT_COLD_REVIEW.json + NATIVE_INDEPENDENT_REVIEW.json   [INDEPENDENT-REVIEWER]
  review-seal       REVIEW_SEAL.json                          [INDEPENDENT-REVIEWER issues, ROOT-SUCCESSOR receives]
  adoptions         ROOT_POLICY_ADOPTION.json + ROOT_NATIVE_APPLICABILITY_ADOPTION.json   [ROOT-SUCCESSOR]
  composition-seal  composition/SEAL.json                     [ROOT-SUCCESSOR]
  selection         FINAL_REVIEW_SELECTION.json               [ROOT-SUCCESSOR]
  receiver-seal     PUBLIC_RECEIVER_SEAL.json                 [ROOT-SUCCESSOR]
  public-index      PUBLIC_INDEX.json (the 1815 public leaves)  [MECHANICAL]
"""
import argparse, hashlib, json, sys
from pathlib import Path

SOURCE = '205aeab7c93299b0666b261485ab5658d8e183de'
TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
Q = 'candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/'
REVIEWS = ('INDEPENDENT_COLD_REVIEW.json', 'NATIVE_INDEPENDENT_REVIEW.json')
ADOPTIONS = ('ROOT_POLICY_ADOPTION.json', 'ROOT_NATIVE_APPLICABILITY_ADOPTION.json')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
desc = lambda raw: dict(bytes=len(raw), sha256=sha(raw))
fsha = lambda path: sha(Path(path).read_bytes())
encode = lambda value: (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')
load = lambda path: json.loads(Path(path).read_bytes())


def label(value, name):
    if not value or '<' in value or '>' in value: raise SystemExit('UNFILLED_IDENTITY_LABEL --' + name + ': ' + repr(value))
    return value


def emit(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle: handle.write(raw)
    print('%s  %6d  %s' % (sha(raw), len(raw), path))


def members(root, mode, modes=None, exclude=('SEAL.json',), order='string'):
    """order='string': rows sorted by path text (G220 candidate seal). order='parts': by path components, so
    dg16-r5-full-g2/ precedes dg16-r5-full-g2-decisions/ (G220 composition seal). Both are reproduced in rehearsal."""
    rows = []
    for q in sorted(Path(root).rglob('*')):
        rel = q.relative_to(root).as_posix()
        if q.is_file() and rel not in exclude:
            raw = q.read_bytes(); rows.append(dict(bytes=len(raw), mode=(modes or {}).get(rel, mode), path=rel, sha256=sha(raw)))
    key = (lambda row: row['path']) if order == 'string' else (lambda row: tuple(row['path'].split('/')))
    return sorted(rows, key=key)


def digest_map(previous, universe):
    out = {}
    for q in sorted(Path(previous).rglob('*')):
        rel = q.relative_to(previous)
        if q.is_file() and (Path(universe) / rel).is_file(): out[fsha(q)] = fsha(Path(universe) / rel)
    return out


def remap(value, mapping):
    if isinstance(value, dict): return {k: remap(v, mapping) for k, v in value.items()}
    if isinstance(value, list): return [remap(v, mapping) for v in value]
    return mapping.get(value, value) if isinstance(value, str) else value


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
s = p.add_subparsers(dest='cmd', required=True)
c = s.add_parser('runtime'); c.add_argument('--universe', required=True)
for n in ('actor', 'issuer-thread', 'workspace-root', 'receiver-output-root', 'maintained-source-root', 'out'): c.add_argument('--' + n, required=True)
c = s.add_parser('candidate-seal'); c.add_argument('--candidate', required=True); c.add_argument('--modes-from', required=True)
for n in ('actor', 'issuer-thread', 'out'): c.add_argument('--' + n, required=True)
c = s.add_parser('reviews')
for n in ('previous-universe', 'universe', 'previous-decisions', 'candidate-seal', 'reviewer', 'out-dir'): c.add_argument('--' + n, required=True)
c = s.add_parser('review-seal')
for n in ('reviews', 'candidate-seal', 'reviewer', 'out'): c.add_argument('--' + n, required=True)
c.add_argument('--report'); c.add_argument('--report-descriptor', help='BYTES:SHA256 when REPORT.md itself is held elsewhere')
c = s.add_parser('adoptions')
for n in ('previous-universe', 'universe', 'previous-decisions', 'reviews', 'review-seal', 'candidate-seal', 'author', 'out-dir'): c.add_argument('--' + n, required=True)
c = s.add_parser('composition-seal')
for n in ('composition', 'actor', 'issuer-thread', 'out'): c.add_argument('--' + n, required=True)
c = s.add_parser('selection')
for n in ('composition', 'composition-seal', 'candidate-seal', 'actor', 'issuer-thread', 'author', 'reviewer', 'out'): c.add_argument('--' + n, required=True)
c = s.add_parser('receiver-seal')
for n in ('receiver', 'composition', 'actor', 'issuer-thread', 'out'): c.add_argument('--' + n, required=True)
c = s.add_parser('public-index')
for n in ('composition', 'out'): c.add_argument('--' + n, required=True)
a = p.parse_args()

if a.cmd == 'runtime':
    issuer = label(a.issuer_thread, 'issuer-thread')
    emit(a.out, encode(dict(schema='dg16.direct-host-public-runtime-binding.v1', actor=label(a.actor, 'actor'), issuer_thread=issuer, session=issuer,
        status='ACTUAL_PUBLIC_PATHS_RECEIVED_FOR_CODE_BINDING', workspace_root=a.workspace_root, receiver_output_root=a.receiver_output_root,
        maintained_source_root=a.maintained_source_root, source_commit=SOURCE, source_tree=TREE,
        host_adoption=desc((Path(a.universe) / Q / 'PROTECTED_RECIPIENT.json').read_bytes()), workspace_current=True, output_fresh=True,
        source_current=True, private_custody_ready=False, effect_grant=False, native_currentness=False, original_awards=[])))
elif a.cmd == 'candidate-seal':
    modes = {row['path']: row['mode'] for row in load(a.modes_from)['members']}
    rows = members(a.candidate, None, modes)
    missing = [row['path'] for row in rows if row['mode'] is None]
    if missing or len(rows) != len(modes): raise SystemExit('CANDIDATE_POPULATION_DIFFERS_FROM_PREVIOUS_SEAL ' + json.dumps(missing))
    emit(a.out, encode(dict(schema='dg16.actual-public-host-candidate-seal.v1', actor=label(a.actor, 'actor'), issuer_thread=label(a.issuer_thread, 'issuer-thread'),
        effect_grant=False, member_count=len(rows), members=rows, original_awards=[], source_commit=SOURCE, source_tree=TREE)))
elif a.cmd == 'reviews':
    mapping = digest_map(a.previous_universe, a.universe)
    for name in REVIEWS:
        body = remap(load(Path(a.previous_decisions) / name), mapping)
        body.update(candidate_seal_sha256=fsha(a.candidate_seal), reviewer=label(a.reviewer, 'reviewer'))
        emit(Path(a.out_dir) / name, encode(body))
elif a.cmd == 'review-seal':
    if a.report: report = desc(Path(a.report).read_bytes())
    else: size, digest = a.report_descriptor.split(':'); report = dict(bytes=int(size), sha256=digest)
    rows = [dict(mode='0444', path=name, **desc((Path(a.reviews) / name).read_bytes())) for name in REVIEWS] + [dict(mode='0444', path='REPORT.md', **report)]
    for name in REVIEWS:
        if load(Path(a.reviews) / name)['reviewer'] != a.reviewer: raise SystemExit('REVIEW_BODY_REVIEWER_DIFFERS ' + name)
    emit(a.out, encode(dict(schema='dg16.independent-code-native-source-review-seal.v1', authority='NONE', decision='PASS_SOURCE_REVIEW_ONLY',
        candidate_seal_sha256=fsha(a.candidate_seal), effect_grant=False, members=rows, original_awards=[], reviewer=label(a.reviewer, 'reviewer'),
        self_excluded=True, source_commit=SOURCE, source_tree=TREE)))
elif a.cmd == 'adoptions':
    mapping = digest_map(a.previous_universe, a.universe)
    for review_name, name in zip(REVIEWS, ADOPTIONS):
        review_raw = (Path(a.reviews) / review_name).read_bytes(); review = json.loads(review_raw)
        body = remap(load(Path(a.previous_decisions) / name), mapping)
        body.update(author=label(a.author, 'author'), candidate_seal_sha256=fsha(a.candidate_seal), independent_review_sha256=sha(review_raw),
                    independent_reviewer=review['reviewer'], independent_review_seal_sha256=fsha(a.review_seal))
        emit(Path(a.out_dir) / name, encode(body))
elif a.cmd == 'composition-seal':
    tree = load(Path(a.composition) / 'PROSPECTIVE_TREE.json')['tree']; rows = members(a.composition, '0400', order='parts')
    emit(a.out, encode(dict(schema='dg16.actual-root-composition-seal.v1', actor=label(a.actor, 'actor'), issuer_thread=label(a.issuer_thread, 'issuer-thread'),
        effect_grant=False, final_tree=tree, member_count=len(rows), members=rows, original_awards=[], source_commit=SOURCE, source_tree=TREE)))
elif a.cmd == 'selection':
    comp = load(Path(a.composition) / 'COMPOSITION.json'); issuer = label(a.issuer_thread, 'issuer-thread')
    if label(a.author, 'author') == label(a.reviewer, 'reviewer'): raise SystemExit('REVIEWER_MUST_DIFFER_FROM_AUTHOR')
    emit(a.out, encode(dict(schema='dg16.direct-host-public-combined-review-selection.v1', actor=label(a.actor, 'actor'), issuer_thread=issuer, session=issuer,
        status='ACTUAL_DISTINCT_REVIEWER_SELECTED_FOR_FINAL_BINDING', author=a.author, reviewer=a.reviewer, source_commit=SOURCE, source_tree=TREE,
        branch=comp['branch'], control_branch=comp['control_branch'], candidate_seal_sha256=fsha(a.candidate_seal),
        composition_seal_sha256=fsha(a.composition_seal), final_tree=comp['final_tree'], effect_grant=False, native_currentness=False, original_awards=[])))
elif a.cmd == 'receiver-seal':
    rows = members(a.receiver, '0400', exclude=('SEAL.json', 'PUBLIC_RECEIVER_SEAL.json'))
    if len(rows) != 7: raise SystemExit('SEVEN_FILE_RECEIVER_REQUIRED, found %d' % len(rows))
    emit(a.out, encode(dict(schema='dg16.root.actual-public-receiver-source-seal.v1', actor=label(a.actor, 'actor'), authority='NONE',
        issuer_thread=label(a.issuer_thread, 'issuer-thread'), effect_grant=False, final_tree=load(Path(a.composition) / 'COMPOSITION.json')['final_tree'],
        member_count=7, members=rows, original_awards=[], self_excluded=True, source_commit=SOURCE, source_tree=TREE)))
elif a.cmd == 'public-index':
    public = Path(a.composition) / 'public'
    base = load(public / 'qualification/dg16-r5-full-g2/SOURCE_MANIFEST.json')
    leaves = {row['path']: dict(git_blob=row['git_blob'], mode=row['mode'], path=row['path']) for row in base['members']}
    for q in sorted(public.rglob('*')):
        if q.is_file():
            raw = q.read_bytes(); rel = q.relative_to(public).as_posix()
            if rel in leaves: raise SystemExit('OVERLAY_REPLACES_MAINTAINED_BASE_MEMBER ' + rel)
            leaves[rel] = dict(git_blob=hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest(), mode='100644', path=rel)
    rows = [leaves[name] for name in sorted(leaves)]
    emit(a.out, encode(dict(members=rows)))
    print('leaves', len(rows), 'base', len(base['members']), 'overlay', len(rows) - len(base['members']), file=sys.stderr)
