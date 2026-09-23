"""Bind the proposed/public research tree; run after corpus generation and review edits."""
import argparse
import hashlib
import json
from pathlib import Path

LOCK = Path('docs/research/PUBLIC_CUSTODY_LOCK.json')

def build(root):
    rows = []
    for folder in ('docs/research/genealogy', 'docs/research/implementaudit/triad-integration', 'docs/research/implementaudit/historical-absorption-baseline', 'scripts'):
        for p in sorted((root / folder).rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:
                continue
            if folder == 'scripts' and p.name not in {'genealogy_corpus.py','genealogy_triad.py','build-genealogy-corpus.py','check-genealogy-corpus.py','build-public-custody-lock.py','resolve-genealogy.py','historical_absorption.py','build-historical-absorption-baseline.py','check-historical-absorption-baseline.py'}:
                continue
            b = p.read_bytes()
            rows.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    value = {'schema':'research-public-custody-lock-v1','authority_boundary':'Content identity only. This lock does not assert publication, target adoption, implementation or release.',
             'files':sorted(rows,key=lambda r:r['path']), 'publication_binding':'After authorized publication, bind this exact lock digest to the verified full immutable commit and origin. No commit is invented in this content lock.'}
    data = (json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    (root / LOCK).write_bytes(data)
    return hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args()
    print('PUBLIC_CUSTODY_LOCK_SHA256='+build(a.root.resolve()))
