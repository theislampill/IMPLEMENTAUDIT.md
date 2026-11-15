#!/usr/bin/env python3
"""FABLE G221: mechanical pin-chain regeneration for ONE changed file (pending_relation.py).

argv: <universe-in> <universe-out> <relative-path-of-changed-file> <replacement-file> <report.json>

Fixpoint over the digest-reference DAG: every sha256 hex literal that names a changed file is replaced by that
file's new digest; in JSON documents a sibling "bytes" of a {bytes, sha256} descriptor is updated too. JSON files
are re-encoded only in the exact style their original bytes round-trip through (refuses otherwise); all other
files are edited textually. Nothing else is touched: no branch, host, decision, review, seal-identity or timing
field. Files that are Root / independent-review issued are NOT in this universe and are only listed by the report.
"""
import hashlib, json, shutil, sys
from collections import OrderedDict
from pathlib import Path

src, dst, changed_rel, replacement, report_path = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]), Path(sys.argv[5])
sha = lambda raw: hashlib.sha256(raw).hexdigest()
blob = lambda raw: hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()
original = {p.relative_to(src).as_posix(): p.read_bytes() for p in sorted(src.rglob('*')) if p.is_file()}
assert changed_rel in original
STYLES = [dict(indent=2, sort_keys=True), dict(indent=2, sort_keys=False), dict(sort_keys=True), dict(sort_keys=False),
          dict(indent=2, sort_keys=True, ensure_ascii=False), dict(sort_keys=True, separators=(',', ':'))]


def json_style(raw):
    try: value = json.loads(raw, object_pairs_hook=OrderedDict)
    except ValueError: return None
    for style in STYLES:
        for tail in ('\n', ''):
            if (json.dumps(value, **style) + tail).encode() == raw: return value, style, tail
    return None


def rewrite(name, raw, mapping):
    """mapping: old_sha -> (new_sha, old_bytes, new_bytes)."""
    if not any(old.encode() in raw for old in mapping): return raw
    styled = json_style(raw) if name.endswith('.json') else None
    if styled is None:
        assert not name.endswith('.json'), 'non-canonical JSON carries a changed pin: ' + name
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


current = dict(original); current[changed_rel] = replacement.read_bytes()
for round_number in range(1, 32):
    mapping = {sha(original[name]): (sha(current[name]), len(original[name]), len(current[name]))
               for name in original if current[name] != original[name]}
    updated = {name: (current[name] if name == changed_rel else rewrite(name, original[name], mapping)) for name in original}
    if updated == current: break
    current = updated
else: raise SystemExit('no fixpoint')
old_blobs = {blob(original[name]): name for name in original if current[name] != original[name]}
for name, raw in current.items():  # a git-blob pin of a changed file inside the author universe would need its own handling
    assert not any(b.encode() in raw for b in old_blobs), 'git blob pin of a changed file in ' + name
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src, dst)
rows = []
for name in sorted(original):
    if current[name] == original[name]: continue
    (dst / name).chmod(0o644); (dst / name).write_bytes(current[name])
    pins = sorted({other for other in original if other != name and sha(original[name]).encode() in original[other]})
    rows.append({'path': name, 'before': {'bytes': len(original[name]), 'sha256': sha(original[name]), 'git_blob': blob(original[name])},
                 'after': {'bytes': len(current[name]), 'sha256': sha(current[name]), 'git_blob': blob(current[name])},
                 'pinned_by': pins})
report = {'rounds': round_number, 'changed_files': len(rows), 'unchanged_files': len(original) - len(rows), 'changes': rows}
report_path.write_text(json.dumps(report, indent=1) + '\n')
for row in rows:
    print('%s\n   before %s %6d\n   after  %s %6d' % (row['path'], row['before']['sha256'], row['before']['bytes'], row['after']['sha256'], row['after']['bytes']))
print('rounds', round_number, 'changed', len(rows), 'unchanged', len(original) - len(rows))
