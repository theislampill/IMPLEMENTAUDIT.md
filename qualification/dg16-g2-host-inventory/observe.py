#!/usr/bin/env python3
"""Read-only public host facts; no operation, admission, or acceptance authority."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import unittest.runner

ROOT = Path(__file__).resolve().parent
UTILITY_SHA = '02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
raw = (ROOT / 'host_utility.py').read_bytes()
assert sha(raw) == UTILITY_SHA, 'EXACT_PRODUCTION_UTILITY_REQUIRED'
spec = importlib.util.spec_from_file_location('g2_inventory_utility', ROOT / 'host_utility.py')
u = importlib.util.module_from_spec(spec)
exec(compile(raw, str(ROOT / 'host_utility.py'), 'exec'), u.__dict__)
assert (ROOT / 'host_utility.py').read_bytes() == raw
release = {}
for line in u.checked_file(Path('/etc/os-release').resolve(), 16384).decode('utf-8').splitlines():
    if '=' in line:
        key, value = line.split('=', 1)
        if key in ('ID', 'VERSION_ID'):
            assert key not in release
            release[key] = u.token(value.strip('"'), 32)
uid, euid, suid = os.getresuid()
gid, egid, sgid = os.getresgid()
tools = {name: u.trusted(name)[1] for name in ('bash', 'bwrap', 'git', 'python3')}
host = dict(os=release, architecture=u.token(os.uname().machine), kernel=u.token(os.uname().release),
            uid=euid, python_version=list(sys.version_info[:3]), image_os=u.token(os.environ.get('ImageOS', '')),
            image_version=u.token(os.environ.get('ImageVersion', '')), tools=tools,
            boot_identity_sha256=sha(u.checked_file(Path('/proc/sys/kernel/random/boot_id'), 128)),
            credentials=dict(uid=uid, euid=euid, suid=suid, gid=gid, egid=egid, sgid=sgid))
runtime_path = Path(unittest.runner.__file__).resolve(strict=True)
runtime_raw = u.checked_file(runtime_path, 131072)
runtime = dict(path=str(runtime_path), version=sys.version.split()[0], bytes=len(runtime_raw), sha256=sha(runtime_raw))
child_path = Path('/proc/self/task') / str(os.getpid()) / 'children'
child_raw = u.checked_file(child_path, 4096)
result = dict(schema='dg16.prospective-host-inventory.v1', authority='NONE', scope='PUBLIC_READ_ONLY_FACTS_NO_QUALIFICATION',
              observation_phase='PRE_PROVISION_INPUTS_SAME_BOUNDARY_AS_ORIGINAL_RUN_INVENTORY',
              qualification_or_post_provision_match=False,
              workflow_commit=os.environ['GITHUB_SHA'], run_id=os.environ['GITHUB_RUN_ID'], attempt=os.environ['GITHUB_RUN_ATTEMPT'],
              host=host, unittest_runtime=runtime,
              child_census=dict(readable=True, bytes=len(child_raw), sha256=sha(child_raw)),
              exact_utility_sha256=UTILITY_SHA, observer_sha256=sha(Path(__file__).read_bytes()),
              no_test_pair_or_native_bank=True, no_decision_or_grant=True, original_acceptance=False, full_G2=False, M2=False)
body = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
assert len(body) <= 16384
out = Path(os.environ['G2_HOST_FACTS'])
out.mkdir(mode=0o700)
with (out / 'HOST_FACTS.json').open('xb') as f:
    f.write(body)
print(body.decode(), end='')
