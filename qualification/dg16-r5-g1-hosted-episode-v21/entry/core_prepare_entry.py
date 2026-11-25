"""Fixed external V21 prepare entry; no carrier, no private sender, no network.

The exact run.py in the fixed root island is executed only after the pinned
public-input selector admits every body. The G1 host-profile adoption binding
that run.py requires was historically produced by the carrier's same-host tool
adoption; that route is a HELD contract item for V21, so this entry refuses with
its distinct code instead of inventing a binding. No effect precedes it.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

BRANCH = 'engineering/opus-dg16-g1-v21-trigger-20261126'
CORE_RUN_SHA256 = 'ce63294c505a41408165a54b1eb80e8e2222ccaa15a00f3cf2691c8e5fde2f82'
SELECTOR_SHA256 = '89bb56e8c980aa1e067e00f09b076a2fa24d22be1293a5e20a5321e8225470b4'
HOST_PROFILE_BINDING = None  # HELD: G1_HOST_PROFILE_ADOPTION_ROUTE (Root decision); never synthesized here


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
    need(HOST_PROFILE_BINDING is not None, 'PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE')
    raw = read(packet / 'run.py', 1024 * 1024, CORE_RUN_SHA256)
    core = types.ModuleType('v21_exact_core')
    core.__file__ = str(packet / 'run.py')
    exec(compile(raw, core.__file__, 'exec'), core.__dict__)
    code = core.execute('prepare', packet.parent / 'source', packet.parent / 'output',
                        host_profile_binding=HOST_PROFILE_BINDING)
    need(type(code) is int and code in (0, 1), 'PREPARE_CORE_RETURN')
    return code


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
