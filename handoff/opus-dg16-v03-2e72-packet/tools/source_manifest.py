"""Regenerate dg16.linux-native-source-manifest.v2 from a commit (read-only git)."""
import hashlib, json, subprocess, sys
repo, commit, out = sys.argv[1:4]
def git(*a, text=True):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, check=True, text=text).stdout
commit = git('rev-parse', commit + '^{commit}').strip()
tree = git('rev-parse', commit + '^{tree}').strip()
members = []
for line in git('ls-tree', '-r', '-z', '--full-tree', commit).split('\0'):
    if not line: continue
    meta, path = line.split('\t', 1)
    mode, kind, blob = meta.split()
    if kind != 'blob' or mode not in ('100644', '100755'):
        raise SystemExit('UNSUPPORTED_TREE_ENTRY ' + mode + ' ' + kind + ' ' + path)
    raw = git('cat-file', 'blob', blob, text=False)
    members.append({'bytes': len(raw), 'git_blob': blob, 'mode': mode, 'path': path,
                    'sha256': hashlib.sha256(raw).hexdigest()})
members.sort(key=lambda m: m['path'])
value = {'commit': commit, 'file_count': len(members), 'members': members,
         'repository': 'theislampill/IMPLEMENTAUDIT.md', 'schema': 'dg16.linux-native-source-manifest.v2',
         'total_bytes': sum(m['bytes'] for m in members), 'tree': tree}
raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
open(out, 'wb').write(raw)
print(hashlib.sha256(raw).hexdigest(), len(raw), len(members))
