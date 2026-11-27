"""Proposed external V21 prepare entry; no carrier, private sender or network.

The exact run.py in the fixed root island is executed only after the pinned
public-input selector admits every body. The profile route is conditional on
Root selecting prospective adoption and issuing the exact policy.
ROOT_POLICY_PIN=None retains the current refusal. Adjacent helper and policy
files use the maintained bounded checkout reader and exact literal pins. The
root-island core reader still requires root custody. No policy or grant is
supplied by this candidate.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

BRANCH = 'engineering/pro-dg16-image23-main-20261127-02'
CORE_RUN_SHA256 = '50810d86b470fcbfb7a3a305ad71281e9f1881c95aea63a52e45ecaf3f335b39'
SELECTOR_SHA256 = '7ee65173fbbb52bd13709d70d33a890fbcf9034c4c6ae197dc37d20ed6d99ab5'
ROOT_POLICY_PIN = {'bytes': 868, 'sha256': '7e9bb7e165e62a7f5c25293eafe35d111845d429c6691c96997e077a3fb14e9c'}
D4_BINDER_SHA256 = '7388c05b14ff7b4050bf5ddb1898164e5f2c198e0eb221ab8a6066be7ae19ce3'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def read(path, limit, digest):
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == 0 and 0 < info.st_size <= limit,
         'PREPARE_FILE_CUSTODY')
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        raw = os.pread(fd, limit + 1, 0)
    finally:
        os.close(fd)
    need(len(raw) == info.st_size and hashlib.sha256(raw).hexdigest() == digest, 'PREPARE_BODY_PIN')
    return raw


def read_external(core, name, limit, digest):
    """Authenticate fixed checkout bytes without claiming root file ownership."""
    need(name in ('host_profile_binding.py', 'G1_HOST_PROFILE_POLICY.json'), 'PREPARE_EXTERNAL_MEMBER')
    here = Path(__file__).absolute().parent
    workspace = Path(os.environ.get('GITHUB_WORKSPACE', ''))
    expected = workspace / 'packet/qualification/dg16-r5-g1-hosted-episode-v21/entry'
    need(workspace.is_absolute() and here == expected and here.resolve(strict=True) == here,
         'PREPARE_FIXED_CHECKOUT')
    reader = core.load_module('public_inputs')
    raw = reader.read_exact(here / name, limit)
    need(hashlib.sha256(raw).hexdigest() == digest, 'PREPARE_EXTERNAL_BODY_PIN')
    return raw


def prepare_core(packet):
    need(ROOT_POLICY_PIN is not None, 'PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE')
    raw = read(packet / 'run.py', 1024 * 1024, CORE_RUN_SHA256)
    core = types.ModuleType('v21_exact_core')
    core.__file__ = str(packet / 'run.py')
    exec(compile(raw, core.__file__, 'exec'), core.__dict__)
    try:
        here = Path(__file__).absolute().parent
        helper_raw = read_external(core, 'host_profile_binding.py', 65536, D4_BINDER_SHA256)
        helper = types.ModuleType('v21_d4_profile_binding')
        helper.__file__ = str(here / 'host_profile_binding.py')
        exec(compile(helper_raw, helper.__file__, 'exec'), helper.__dict__)
        produced = helper.prepare(core, packet.parent / 'source', packet.parent / 'output',
            root_policy_pin=ROOT_POLICY_PIN,
            read_policy=lambda: read_external(core, 'G1_HOST_PROFILE_POLICY.json', 65536, ROOT_POLICY_PIN['sha256']))
        code = core.execute('prepare', packet.parent / 'source', packet.parent / 'output',
                            host_profile_binding=produced['binding'], host_profile_evidence=produced['evidence'])
    except core.Refusal as exc:
        # Only the exact pinned core class and its closed enum may cross the
        # entry boundary. Unknown payloads/subclasses keep the generic refusal.
        if type(exc) is core.Refusal and len(exc.args) == 1 and type(exc.args[0]) is str \
                and exc.args[0] in core.KNOWN_FAILURE_CODES:
            raise ValueError(exc.args[0]) from None
        raise
    need(type(code) is int and code in (0, 1), 'PREPARE_CORE_RETURN')
    return code


def main():
    e = os.environ
    need(len(sys.argv) == 1 and sys.flags.isolated == 1 and sys.dont_write_bytecode is True, 'FIXED_ISOLATED_ENTRY_ONLY')
    need(e.get('GITHUB_ACTIONS') == 'true' and e.get('GITHUB_REF') == 'refs/heads/' + BRANCH
         and e.get('GITHUB_RUN_ATTEMPT') == '1' and re.fullmatch('[1-9][0-9]{5,19}', e.get('GITHUB_RUN_ID', ''))
         and os.getuid() == os.geteuid() == 0, 'PREPARE_CONTEXT')
    packet = Path('/dg16-g1-' + e['GITHUB_RUN_ID']) / 'packet'
    selector_raw = read(packet / 'public_inputs.py', 1024 * 1024, SELECTOR_SHA256)
    selector = types.ModuleType('v21_prepare_selector')
    selector.__file__ = str(packet / 'public_inputs.py')
    exec(compile(selector_raw, selector.__file__, 'exec'), selector.__dict__)
    selector.admit(packet)  # first HELD role or contract item refuses here
    return prepare_core(packet)


if __name__ == '__main__':
    try:
        rc = main()
        out = dict(schema='dg16.v21-core-prepare-return.v1', authority='NONE', returncode=rc, original_awards=[])
    except BaseException as exc:
        literal = exc.args[0] if isinstance(exc, ValueError) and exc.args and type(exc.args[0]) is str \
            and re.fullmatch('[A-Z0-9_]{1,96}', exc.args[0]) else 'PREPARE_INTERNAL_REFUSAL'
        out = dict(schema='dg16.v21-core-prepare-return.v1', authority='NONE', returncode=1, code=literal,
                   original_awards=[])
        rc = 1
    sys.stdout.write(json.dumps(out, sort_keys=True, separators=(',', ':')) + '\n')
    raise SystemExit(rc)
