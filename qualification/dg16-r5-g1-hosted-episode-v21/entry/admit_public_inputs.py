"""Pre-effect public-input gate for the V21 hosted episode (unprivileged).

Runs from the exact checkout before the root island, clone, setup, NSS change,
controller creation or any native call. It loads the pinned selector body,
refuses with the first HELD role or contract item, and otherwise verifies every
exact public body. It never writes, never uses the network and never elevates.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

SELECTOR_SHA256 = 'c2bbc0aba28032bc580ca9e2ae0052f4688132701fda2965a362b22012301c91'
BRANCH = 'engineering/dg16-image23-main-20261128-06'
EPISODE = 'qualification/dg16-r5-g1-hosted-episode-v21'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def load_selector(packet):
    path = packet / 'public_inputs.py'
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and 0 < info.st_size <= 1024 * 1024, 'GATE_SELECTOR_SHAPE')
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        raw = os.pread(fd, 1024 * 1024 + 1, 0)
    finally:
        os.close(fd)
    need(len(raw) == info.st_size and hashlib.sha256(raw).hexdigest() == SELECTOR_SHA256, 'GATE_SELECTOR_PIN')
    module = types.ModuleType('v21_public_input_gate_selector')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def context():
    e = os.environ
    need(sys.flags.isolated == 1 and sys.dont_write_bytecode and len(sys.argv) == 1, 'GATE_FIXED_ENTRY')
    need(e.get('GITHUB_ACTIONS') == 'true' and e.get('GITHUB_REPOSITORY') == 'theislampill/IMPLEMENTAUDIT.md'
         and e.get('GITHUB_EVENT_NAME') == 'create' and e.get('GITHUB_REF') == 'refs/heads/' + BRANCH
         and e.get('GITHUB_RUN_ATTEMPT') == '1' and re.fullmatch('[1-9][0-9]{5,19}', e.get('GITHUB_RUN_ID', '')),
         'GATE_CONTEXT')
    return Path(e['GITHUB_WORKSPACE']) / 'packet' / EPISODE / 'packet'


def gate(packet):
    selector = load_selector(packet)
    try:
        raw, index = selector.load_index(packet)
        held = selector.held_report(index)
        selected = selector.admit(packet)
    except selector.Refusal as exc:
        code = exc.args[0] if exc.args and type(exc.args[0]) is str else 'PUBLIC_INPUT_REFUSED'
        held_rows = None
        try:
            held_rows = selector.held_report(selector.load_index(packet)[1])
        except Exception:
            held_rows = None
        return 1, dict(schema='dg16.v21-public-input-gate.v1', authority='NONE', status='REFUSED', code=code,
                       held=held_rows, effects_before_refusal=[], original_awards=[])
    return 0, dict(schema='dg16.v21-public-input-gate.v1', authority='NONE', status='ADMITTED', code='ADMITTED',
                   index_sha256=selected['index_sha256'], held=held, effects_before_refusal=[], original_awards=[])


def main():
    code, value = gate(context())
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')
    sys.stdout.flush()
    return code


if __name__ == '__main__':
    try:
        rc = main()
    except BaseException as exc:
        literal = exc.args[0] if isinstance(exc, ValueError) and exc.args and type(exc.args[0]) is str \
            and re.fullmatch('[A-Z0-9_]{1,96}', exc.args[0]) else 'GATE_INTERNAL_REFUSAL'
        sys.stdout.write(json.dumps(dict(schema='dg16.v21-public-input-gate.v1', authority='NONE', status='REFUSED',
                                         code=literal, held=None, effects_before_refusal=[], original_awards=[]),
                                    sort_keys=True, separators=(',', ':')) + '\n')
        rc = 1
    raise SystemExit(rc)
