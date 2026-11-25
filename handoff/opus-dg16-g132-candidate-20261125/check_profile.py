import ast, json, hashlib, sys
src = open(sys.argv[1], encoding='utf-8').read()
names = {'_g1_profile_need', 'g1_host_policy_sha256', 'select_g1_host_profile', 'validate_g1_host_profile', 'g1_profile_from_inventory'}
nodes = [n for n in ast.parse(src).body if (isinstance(n, ast.FunctionDef) and n.name in names) or
         (isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'G1_HOST_PROFILES')]
ns = dict(json=json, hashlib=hashlib, sha=lambda b: hashlib.sha256(b).hexdigest(), sys=sys)
exec(compile(ast.Module(body=nodes, type_ignores=[]), 'p', 'exec'), ns)
facts = dict(platform='linux', architecture='x86_64', os={'ID': 'ubuntu', 'VERSION_ID': '24.04'}, python_version=[3, 12, 3],
             image_os='ubuntu24', uid=0, euid=0, gid=0, egid=0, image_version='20261116.133.1')
sel = ns['select_g1_host_profile'](facts); print('133.1 ->', sel['profile_id'], 'validates:', ns['validate_g1_host_profile'](sel) == sel)
for v in ('20261116.376.1', '20261116.133.2'):
    try: ns['select_g1_host_profile'](dict(facts, image_version=v)); print(v, 'ACCEPTED (unexpected)')
    except ValueError as e: print(v, 'refused', e)
print('370.1 ->', ns['select_g1_host_profile'](dict(facts, image_version='20261111.370.1'))['profile_id'])
