#!/usr/bin/env python3
"""Rehydrate digest-addressed public sources inside a fresh reference directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('destination',type=Path)
    out=args.parse_args().destination.absolute()
    here=Path(__file__).resolve().parent
    if os.path.lexists(out) or not out.parent.is_dir():
        raise SystemExit('Choose a fresh reference directory with an existing parent')
    deps=json.loads((here/'DEPENDENCIES.json').read_bytes())
    targets={}
    for row in deps['layout']:
        rel=PurePosixPath(row['destination'])
        if rel.is_absolute() or '..' in rel.parts or '\\' in str(rel) or ':' in str(rel):
            raise ValueError('unsafe destination')
        if str(rel).casefold() in targets:raise ValueError('duplicate destination')
        member=PurePosixPath(row['member'])
        if member.is_absolute() or '..' in member.parts:raise ValueError('unsafe source')
        raw=here.joinpath(*member.parts).read_bytes()
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
            raise ValueError('source mismatch: '+str(rel))
        targets[str(rel).casefold()]=(rel,raw,row['sha256'])
    out.mkdir(mode=0o700)
    for rel,raw,sha in targets.values():
        path=out.joinpath(*rel.parts)
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:f.write(raw)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('copy changed')
    print(json.dumps({'verified_named_source_paths':len(targets),'path':str(out),'installed':False,'effect_grants':0}))
if __name__=='__main__':main()
