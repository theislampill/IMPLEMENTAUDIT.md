"""Disposable sender rehearsal THROUGH carrier.Commands (not CaptureSession directly).

Usage (non-root sender host, fresh isolated interpreter):
  python3.12 -I -B sender_rehearsal_v2.py <copied qualification/dg16-r5-g1-hosted-episode> <scratch dir>

Part 1 drives the real entry (carrier_policy.load / carrier.root_payload) and reports its first refusal.
Part 2 substitutes ONLY the two seams that need issued/private records (carrier.current_binding, which
re-runs carrier_policy.load against the issued CARRIER_ADMISSION, and sender_policy.current, which needs the
unresolved PRO_SENDER records) with disposable stand-ins, and runs the unchanged Commands.__init__/run/
current_tools/closed and CaptureSession code on a throwaway RSA recipient and random plaintext (0600 files).
Part 3 shows refusals; part 4 shows the host decrypt argv still satisfies verify_decrypt_record's template.
"""
import ast
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

EP = Path(sys.argv[1]).absolute()
TMP = Path(sys.argv[2]).absolute()
spec = importlib.util.spec_from_file_location('carrier_loader', EP / 'carrier' / 'carrier_loader.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
pub = loader.load()
K, P, F, C, SC, SP = pub.carrier, pub.policy, pub.files, pub.codec, pub.sender_capture, pub.sender_policy
out = {}


def refusal(fn):
    try:
        fn()
        return 'NO_REFUSAL'
    except BaseException as exc:  # noqa: BLE001 - report the closed code only
        return f'{type(exc).__name__}:{exc}'


# 1. Real entry
out['1_real_policy_load'] = refusal(P.load)
out['1_real_root_payload'] = K.root_payload('1', '0' * 40, 1, b'not-an-artifact')['result']['code']

# 2. Through carrier.Commands with disposable seams
raw = (EP / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes()
comp = json.loads(raw)
calls = {'current_binding': 0, 'sender_current': 0}


def stand_in_binding(_binding):
    calls['current_binding'] += 1


def stand_in_sender(_selection):
    calls['sender_current'] += 1
    return True


K.current_binding = stand_in_binding
SP.current = stand_in_sender
binding = dict(sender_tools=comp['sender_tools'], root_tools=comp['root_tools'], limits=comp['limits'],
               _binding_raw=raw, _sender_selection={'disposable': True})
TMP.mkdir(mode=0o700)
key, cert = TMP / 'recipient.key', TMP / 'recipient.pem'
subprocess.run(['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:3072', '-noenc', '-sha256', '-days', '1',
                '-subj', '/CN=disposable-rehearsal', '-keyout', str(key), '-out', str(cert)],
               check=True, capture_output=True, env={'PATH': '/usr/bin:/bin', 'OPENSSL_CONF': '/dev/null'})
os.chmod(key, 0o600)
plain = os.urandom(300000)


def session(name):
    directory = TMP / name
    fd, _ = F.private_directory(directory)
    os.close(fd)
    budget = K.new_budget(directory)
    handles = dict(plain=F.OutputFile(directory, 'bundle.plain', C.MAX_PLAINTEXT_BYTES, budget),
                   certificate=F.OutputFile(directory, 'recipient.pem', P.MAX_CERTIFICATE, budget),
                   cipher=F.OutputFile(directory, 'INPUTS.cms', P.MAX_CIPHERTEXT, budget))
    handles['plain'].write(plain)
    handles['certificate'].write(cert.read_bytes())
    return directory, budget, handles


directory, budget, h = session('dg16-private-sender-rehearsal')
cmd = K.Commands(binding, 'root', directory, budget, time.monotonic() + 120, P.sha(b'disposable-request'))
rc = cmd.run('encrypt', h)
record = json.loads((directory / 'COMMAND_encrypt.json').read_bytes())
cipher = h['cipher'].read()
K.require_auth_enveloped(cipher)
(TMP / 'cipher.der').write_bytes(cipher)
dec = subprocess.run(['/usr/bin/openssl', 'cms', '-decrypt', '-binary', '-inform', 'DER', '-in', str(TMP / 'cipher.der'),
                      '-recip', str(cert), '-inkey', str(key)], capture_output=True,
                     env={'PATH': '/usr/bin:/bin', 'OPENSSL_CONF': '/dev/null'})
closed = cmd.closed()
cleanup = [x.cleanup() for x in h.values()]
out['2_commands_encrypt'] = dict(
    returncode=rc, argv_head=record['argv'][:2], argv_is_sandbox_form=record['argv'][:len(SC.SANDBOX_PREFIX)] == SC.SANDBOX_PREFIX,
    env_not_executed='/usr/bin/env' not in record['argv'], tool_descriptors=record['tool_descriptors'],
    capture_row={k: record['capture'][0][k] for k in ('process_started', 'pidfd_acquired', 'returncode', 'internal_failure',
                                                       'streams_complete', 'cleanup')},
    file_size_limit=record['file_size_limit'], cpu_limit=record['cpu_limit'],
    rlimit_as=resource.getrlimit(resource.RLIMIT_AS), rlimit_cpu=resource.getrlimit(resource.RLIMIT_CPU),
    tool_rows=sorted(cmd.tool_rows), seam_calls=dict(calls), cipher_bytes=len(cipher), auth_enveloped=True,
    decrypt_rc=dec.returncode, decrypts_to_plaintext=dec.stdout == plain, closed=closed,
    owner_evidence=(directory / 'SENDER_CAPTURE_OWNER.json').is_file(),
    cleanup_unlinked=all(r.get('unlinked') for r in cleanup))

# 3. Refusals through the same code
bad = json.loads(json.dumps(binding['sender_tools']))
bad['bwrap']['sha256'] = '0' * 64
d3, b3, h3 = session('refuse-bwrap-pin')
out['3a_wrong_bwrap_pin'] = refusal(lambda: K.Commands(dict(binding, sender_tools=bad), 'root', d3, b3, time.monotonic() + 60, None))
d4, b4, h4 = session('refuse-hosted-root-tools')
out['3b_hosted_root_tools_as_sender_pins'] = refusal(
    lambda: K.Commands(dict(binding, sender_tools=binding['root_tools']), 'root', d4, b4, time.monotonic() + 60, None))
row = F.read_file(Path('/usr/bin/bwrap'), 32 * 1024**2)[1]
moved = dict(row, identity=[*row['identity'][:5], row['identity'][5] + 1, *row['identity'][6:]])
out['3c_launcher_identity_changed'] = refusal(lambda: os.close(SC.launcher_fd(moved)))
out['3c_launcher_identity_exact'] = refusal(lambda: os.close(SC.launcher_fd(row)))
old = ['/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LC_ALL=C', 'OPENSSL_CONF=/dev/null', '/usr/bin/openssl', 'cms', '-encrypt',
       '-binary', '-aes-256-gcm', '-in', '/proc/self/fd/3', '-outform', 'DER', '-out', '/proc/self/fd/5', '-recip',
       '/proc/self/fd/4', '-keyopt', 'rsa_padding_mode:oaep', '-keyopt', 'rsa_oaep_md:sha256', '-keyopt', 'rsa_mgf1_md:sha256']
out['3d_v1_env_argv_refused'] = refusal(lambda: SC.validate_command('carrier-encrypt', old, (3, 4, 5)))
copy = TMP / 'bwrap-copy'
copy.write_bytes(Path('/usr/bin/bwrap').read_bytes())
os.chmod(copy, 0o755)
out['3e_non_root_chain_custody'] = refusal(lambda: K.sender_tool_custody(copy, F.read_file(copy, 32 * 1024**2)[1]))
for hs in (h3, h4):
    for x in hs.values():
        x.cleanup()

# 4. Host decrypt argv (unchanged) against verify_decrypt_record's fixed template
src = (EP / 'carrier' / 'carrier.py').read_text()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == 'verify_decrypt_record')
fixed = next(ast.literal_eval(t.value) for t in ast.walk(fn)
             if isinstance(t, ast.Assign) and getattr(t.targets[0], 'id', '') == 'fixed')


class StubOwner:
    def capture(self, label, argv, records, deadline, seconds=60, fds=()):
        self.seen = (label, argv, fds)
        raise RuntimeError('STUB_NO_EFFECT')


host_dir = TMP / 'host-argv'
fd, _ = F.private_directory(host_dir)
os.close(fd)
hc = K.Commands.__new__(K.Commands)
hc.role, hc.records, hc.deadline, hc.binding = 'host', [], time.monotonic() + 60, binding
hc.budget, hc.directory, hc.u, hc.cpu_profile = F.Budget(10**9, 100), host_dir, StubOwner(), (60, 60)
hc.request_sha256, hc.capture_owner_sha256, hc.tool_pins = None, '0' * 64, {}
hc.current_tools = lambda capture_callback=False: None


class Item:
    def __init__(self, n):
        self.fd = n
        self.proc_path = '/proc/self/fd/' + str(n)

    def current(self):
        return True


out['4_host_run'] = refusal(lambda: hc.run('decrypt', dict(cipher=Item(3), certificate=Item(4), key=Item(5), quarantine=Item(6))))
argv = hc.u.seen[1]
ok = len(argv) == len(fixed) and all((e is None and a.startswith('/proc/self/fd/') and a[14:].isdigit()) or a == e
                                     for a, e in zip(argv, fixed))
out['4_host_decrypt_argv'] = dict(argv=argv, matches_verify_decrypt_record_template=ok,
                                  distinct_fds=len({a for a, e in zip(argv, fixed) if e is None}) == 4)
print(json.dumps(out, indent=1))
