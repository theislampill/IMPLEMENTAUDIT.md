"""v3 static checks on the sender host (python3.12 -I -B), outside any sandbox. No private input, no effect.

Usage: python3.12 -I -B check_v3_static.py <tree root> <extra .py files...>
  1. syntax: every .py in the entry/episode packets and the given extra files compiles under Python 3.12;
  2. host decrypt argv (v2 rehearsal part 4, unchanged): Commands.run('decrypt') still builds exactly the argv
     that verify_decrypt_record's fixed template accepts (host role; capture owner stubbed, no effect);
  3. the carrier loads in a fresh isolated interpreter and the shipped carrier_policy.load() still refuses
     (issued CARRIER_ADMISSION stale), with root_tools absent from the composition.
"""
import ast
import importlib.util
import json
import sys
import time
from pathlib import Path

tree = Path(sys.argv[1])
EP = tree / 'qualification' / 'dg16-r5-g1-hosted-episode'
out = {}
sources = sorted(p for r in ('qualification/dg16-r5-g1-hosted-entry', 'qualification/dg16-r5-g1-hosted-episode')
                 for p in (tree / r).rglob('*.py')) + [Path(p) for p in sys.argv[2:]]
bad = []
for p in sources:
    try:
        compile(p.read_bytes(), str(p), 'exec', dont_inherit=True)
    except SyntaxError as exc:
        bad.append(f'{p}: {exc}')
out['1_syntax'] = dict(files=len(sources), errors=bad)
spec = importlib.util.spec_from_file_location('carrier_loader', EP / 'carrier' / 'carrier_loader.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
pub = loader.load()
K, P, F = pub.carrier, pub.policy, pub.files
src = (EP / 'carrier' / 'carrier.py').read_text()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == 'verify_decrypt_record')
fixed = next(ast.literal_eval(t.value) for t in ast.walk(fn)
             if isinstance(t, ast.Assign) and getattr(t.targets[0], 'id', '') == 'fixed')


class StubOwner:
    def capture(self, label, argv, records, deadline, seconds=60, fds=()):
        self.seen = (label, argv, fds)
        raise RuntimeError('STUB_NO_EFFECT')


class Item:
    def __init__(self, n):
        self.fd = n
        self.proc_path = '/proc/self/fd/' + str(n)

    def current(self):
        return True


import tempfile  # noqa: E402
import os  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    host_dir = Path(tmp) / 'host-argv'
    fd, _ = F.private_directory(host_dir)
    os.close(fd)
    hc = K.Commands.__new__(K.Commands)
    hc.role, hc.records, hc.deadline = 'host', [], time.monotonic() + 60
    hc.binding = dict(limits={'command_seconds': 60}, _binding_raw=b'x')
    hc.budget, hc.directory, hc.u, hc.cpu_profile = F.Budget(10**9, 100), host_dir, StubOwner(), (60, 60)
    hc.request_sha256, hc.capture_owner_sha256, hc.tool_pins = None, '0' * 64, {}
    hc.current_tools = lambda capture_callback=False: None
    import resource
    # As Commands.__init__ does before any command (an unlimited hard RLIMIT_FSIZE reads as -1 there).
    resource.setrlimit(resource.RLIMIT_FSIZE, (P.MAX_CIPHERTEXT, P.MAX_CIPHERTEXT))
    try:
        hc.run('decrypt', dict(cipher=Item(3), certificate=Item(4), key=Item(5), quarantine=Item(6)))
    except BaseException as exc:  # noqa: BLE001
        stub = f'{type(exc).__name__}:{exc}'
    argv = getattr(hc.u, 'seen', (None, []))[1]
    if not argv:
        print('STUB_NOT_REACHED', stub)
ok = len(argv) == len(fixed) and all((e is None and a.startswith('/proc/self/fd/') and a[14:].isdigit()) or a == e
                                     for a, e in zip(argv, fixed))
out['2_host_decrypt_argv'] = dict(argv=argv, matches_verify_decrypt_record_template=ok, stub_refusal=stub)
try:
    P.load()
    load = 'NO_REFUSAL'
except ValueError as exc:
    load = str(exc)
comp = json.loads((EP / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes())
out['3_policy'] = dict(policy_load=load, root_tools_in_composition='root_tools' in comp,
                       sender_tools=comp['sender_tools'], binding_sha_matches=P.sha((EP / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes()) == P.BINDING_SHA256)
print(json.dumps(out, indent=1))
sys.exit(0 if not bad and ok else 1)
