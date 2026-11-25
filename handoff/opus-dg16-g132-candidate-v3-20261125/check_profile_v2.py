"""Profile + run.py tool-pin check (extends v1 check_profile.py, review m7).

Usage: python check_profile_v2.py <episode dir>
Part A (v1): G1 profile selection from host_utility.py.
Part B (new): executes run.py's own inventory() body (AST-extracted, unchanged) with stub host facts, so its
hard-coded python3.12/git/bwrap pins and the selected profile are exercised together.
"""
import ast
import hashlib
import json
import sys
import types
from pathlib import Path

EP = Path(sys.argv[1])
src = (EP / 'host_utility.py').read_text(encoding='utf-8')
names = {'_g1_profile_need', 'g1_host_policy_sha256', 'select_g1_host_profile', 'validate_g1_host_profile', 'g1_profile_from_inventory'}
nodes = [n for n in ast.parse(src).body if (isinstance(n, ast.FunctionDef) and n.name in names) or
         (isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'G1_HOST_PROFILES')]
fake_sys = types.SimpleNamespace(platform='linux', version_info=(3, 12, 3, 'final', 0), executable='/usr/bin/python3.12')
ns = dict(json=json, hashlib=hashlib, sha=lambda b: hashlib.sha256(b).hexdigest(), sys=fake_sys)
exec(compile(ast.Module(body=nodes, type_ignores=[]), 'host_utility', 'exec'), ns)
facts = dict(platform='linux', architecture='x86_64', os={'ID': 'ubuntu', 'VERSION_ID': '24.04'}, python_version=[3, 12, 3],
             image_os='ubuntu24', uid=0, euid=0, gid=0, egid=0, image_version='20261116.133.1')
try:
    sel = ns['select_g1_host_profile'](facts)
    print('A 133.1 ->', sel['profile_id'], 'validates:', ns['validate_g1_host_profile'](sel) == sel)
except ValueError as e:
    print('A 133.1 refused', e)
for v in ('20261116.376.1', '20261116.133.2'):
    try:
        ns['select_g1_host_profile'](dict(facts, image_version=v)); print('A', v, 'ACCEPTED (unexpected)')
    except ValueError as e:
        print('A', v, 'refused', e)
print('A 370.1 ->', ns['select_g1_host_profile'](dict(facts, image_version='20261111.370.1'))['profile_id'])

# Part B: run.py inventory() with stub facts
run_src = (EP / 'run.py').read_text(encoding='utf-8')
inv = next(n for n in ast.parse(run_src).body if isinstance(n, ast.FunctionDef) and n.name == 'inventory')
PY, GIT, BW = ('e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f',
               '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235',
               '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712')


def attempt(label, tools, image='20261116.133.1'):
    def trusted(name):
        value = tools.get(name)
        if value is None:
            return None, {'available': False, 'requested': '/usr/bin/' + name, 'code': 'TOOL_OS_REFUSAL', 'errno': 2}
        return '/usr/bin/' + name, {'available': True, 'sha256': value}

    u = types.SimpleNamespace(trusted=trusted, g1_profile_from_inventory=ns['g1_profile_from_inventory'],
                              validate_g1_profile_binding=lambda *a: True)
    fake_os = types.SimpleNamespace(getuid=lambda: 0, geteuid=lambda: 0, getgid=lambda: 0, getegid=lambda: 0,
                                    uname=lambda: types.SimpleNamespace(machine='x86_64', release='6.11'),
                                    environ={'ImageOS': 'ubuntu24', 'ImageVersion': image})
    fake_resource = types.SimpleNamespace(RLIMIT_NOFILE=7, getrlimit=lambda k: (65536, 65536))

    class FakePath(str):
        def __new__(cls, v): return str.__new__(cls, v)
        def resolve(self, strict=False): return FakePath(self)

    def need(value, code):
        if not value: raise ValueError(code)

    env = dict(os=fake_os, sys=fake_sys, resource=fake_resource, Path=FakePath, need=need,
               read_regular=lambda p, n: b'ID=ubuntu\nVERSION_ID="24.04"\n', digest=lambda b: hashlib.sha256(b).hexdigest(),
               read_boot_identity=lambda: b'boot', SOURCE_COMMIT='0' * 40, SOURCE_TREE='0' * 40)
    exec(compile(ast.Module(body=[inv], type_ignores=[]), 'run.py', 'exec'), env)
    state = {'host_observations': [], 'host_profile_binding': None, 'context': {}}
    try:
        paths = env['inventory'](state, u)
        print('B', label, '-> accepted, bwrap path', paths['bwrap'])
    except ValueError as e:
        print('B', label, '-> refused', e)


base = {'python3.12': PY, 'git': GIT, 'bash': 'b' * 64}
attempt('original pins, bwrap absent (core provisions it)', dict(base))
attempt('original pins, original bwrap', dict(base, bwrap=BW))
attempt('image git 2.56.1 (08ca4d2e) left in place', dict(base, git='08ca4d2e' + '0' * 56))
attempt('sender-host bwrap e3189038 on core host', dict(base, bwrap='e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71'))
attempt('unmeasured image 20261116.376.1', dict(base), image='20261116.376.1')
