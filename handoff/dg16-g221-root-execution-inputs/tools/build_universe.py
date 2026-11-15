#!/usr/bin/env python3
"""Assemble an author universe (candidate-e76-source-01/ + author/) from a checkout of this repository.

Mechanical byte copying only. Nothing is issued, sealed, adopted or published.

  g220  the HISTORICAL G220 universe exactly as held in g220-custody/ (proves the checker: 17/17).
  g221  the G221 correction on the G220 (host-20) base:
          g220-custody/candidate-e76-source-01        (historical base)
        + every candidate/public/<path> replaced by <repo>/<path>   (the committed correction, 82f4c3d1)
        + prospective-custody SEAL.json, receiver templates and author tools (proposals, not Root issued)

usage: build_universe.py {g220|g221} --repo <checkout-root> --out <fresh-dir>
       [--custody DIR] [--prospective DIR]     (defaults are the handoff folders inside --repo)
"""
import argparse, hashlib, json, shutil
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('base', choices=['g220', 'g221']); p.add_argument('--repo', type=Path, required=True)
p.add_argument('--out', type=Path, required=True); p.add_argument('--custody', type=Path); p.add_argument('--prospective', type=Path)
a = p.parse_args()
custody = a.custody or a.repo / 'handoff/dg16-g221-root-execution-inputs/g220-custody'
prospective = a.prospective or a.repo / 'handoff/dg16-g221-receiver-fix-20261114/prospective-custody'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
if a.out.exists(): raise SystemExit('FRESH_OUTPUT_REQUIRED: ' + str(a.out))
a.out.mkdir(parents=True)
C = a.out / 'candidate-e76-source-01'
shutil.copytree(custody / 'candidate-e76-source-01', C)
shutil.copytree(custody / 'author', a.out / 'author')
changed = []


def put(target, source, label):
    new = source.read_bytes()
    if not target.exists() or target.read_bytes() != new:
        changed.append(dict(path=target.relative_to(a.out).as_posix(), source=label, sha256=sha(new), bytes=len(new)))
        target.write_bytes(new)


if a.base == 'g221':
    public = C / 'candidate/public'
    for target in sorted(q for q in public.rglob('*') if q.is_file()):
        rel = target.relative_to(public)
        source = a.repo / rel
        if not source.is_file(): raise SystemExit('REPOSITORY_MEMBER_MISSING: ' + rel.as_posix())
        put(target, source, 'repo:' + rel.as_posix())
    for rel in ('SEAL.json', 'receiver/BINDING_TEMPLATE.json', 'receiver/ROOT_BINDING_TEMPLATE.json'):
        put(C / rel, prospective / 'candidate-e76-source-01' / rel, 'prospective-custody:' + rel)
    for name in ('bind_public_successor.py', 'compose-candidate-bound.py', 'compose-final-bound.py'):
        put(a.out / 'author' / name, prospective / 'author' / name, 'prospective-custody:author/' + name)
files = sorted(q for q in a.out.rglob('*') if q.is_file())
print(json.dumps(dict(base=a.base, out=str(a.out), files=len(files), changed_from_g220=changed), indent=1))
