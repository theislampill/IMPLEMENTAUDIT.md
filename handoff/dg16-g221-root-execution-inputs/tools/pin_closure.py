#!/usr/bin/env python3
"""FABLE G221: digest-reference closure. Which files pin (by sha256 hex, or by git blob id) a file whose bytes change?

argv: <universe-root> <seed-relative-path>... ; prints the transitive closure of "G contains sha256(F)" edges
starting at the seeds, with the referencing line(s). Read-only.
"""
import hashlib, subprocess, sys
from pathlib import Path

root = Path(sys.argv[1]); seeds = sys.argv[2:]
files = {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}
sha = {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()}
blob = {name: hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest() for name, raw in files.items()}
by_digest = {}
for name in files: by_digest.setdefault(sha[name], []).append(name)
seen, queue, edges = set(), list(seeds), []
while queue:
    name = queue.pop(0)
    if name in seen: continue
    seen.add(name)
    for kind, digest in (('sha256', sha[name]), ('gitblob', blob[name])):
        needle = digest.encode()
        for other, raw in files.items():
            if other == name or needle not in raw: continue
            lines = [(i + 1, line.strip()[:150].decode('utf-8', 'replace')) for i, line in enumerate(raw.split(b'\n')) if needle in line]
            edges.append((name, other, kind, digest, lines))
            if other not in seen: queue.append(other)
for name, other, kind, digest, lines in edges:
    print(f'{name} [{kind} {digest[:12]}] <- {other}')
    for number, line in lines[:4]: print(f'      {number}: {line}')
print('\nCLOSURE (%d files change):' % len(seen))
for name in sorted(seen): print('  ', sha[name], len(files[name]), name, '(identical copies: %d)' % len(by_digest[sha[name]]))
