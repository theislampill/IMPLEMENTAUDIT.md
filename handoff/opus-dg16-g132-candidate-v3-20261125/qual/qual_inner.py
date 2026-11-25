"""Qualification inner entry: runs INSIDE the whole-sender sandbox started by sender_capture._launch.

It differs from the production inner (carrier/sender_launch.py --inside) only by the seams that need issued
or unresolved records (S2-S5 below) and by observation (probes). The sandbox self-check is the FIRST act,
exactly as in production; the probes record the restriction at the first (disposable) private read.

  S1 entry selection: this file instead of carrier/sender_launch.py (same _launch, same argv shape).
  S2 carrier_policy.load      -> the actual composition and core bodies with the disposable input index
                                 (needs the issued CARRIER_ADMISSION, stale, and the real INPUT_INDEX inputs).
  S3 carrier.current_binding  -> counted no-op (it re-runs carrier_policy.load, i.e. S2).
  S4 sender_policy.load/current -> a disposable operation (PRO_SENDER records are UNRESOLVED); current() keeps
                                 the original-UID/GID and time checks.
  S5 carrier_policy.check_inputs -> exact disposable index/body join (RETAINED/ROLES pins name the real inputs).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).absolute().parent
PACKET = HERE.parent
sys.dont_write_bytecode = True
import importlib.util  # noqa: E402


def load_file(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pub = load_file(PACKET / 'carrier' / 'carrier_loader.py', 'carrier_loader').load()
SC, K, P, F, C, SP = pub.sender_capture, pub.carrier, pub.policy, pub.files, pub.codec, pub.sender_policy
out = {'sandbox_self_check': SC.enter_sender_sandbox(sys.argv[2])}  # first act, as in production
QC = load_file(HERE / 'qual_common.py', 'qual_common')
cfg = json.loads((HERE / 'config.json').read_bytes())
probes = []
probes.append(QC.probe('P0_after_sandbox_entry_before_any_input', cfg, SC))
archive = SC.read_request_archive()
binding = QC.binding_for(pub, PACKET, cfg)
seams = dict(S2_policy_load=0, S3_current_binding=0, S4_sender_load=0, S4_sender_current=0, S5_check_inputs=0)


def s2_load():
    seams['S2_policy_load'] += 1
    return dict(binding)


def s3_current(_binding):
    seams['S3_current_binding'] += 1


def s4_load(b, ctx, artifact_id, arch):
    seams['S4_sender_load'] += 1
    op = cfg['operation']
    P.need(ctx == op['context'] and artifact_id == op['artifact_id'] and P.descriptor(arch) == op['artifact']
           and op['carrier_binding_sha256'] == P.sha(b['_binding_raw']), 'QUAL_OPERATION_BINDING')
    P.need(os.getuid() == os.geteuid() == op['sender_uid'] and os.getgid() == os.getegid() == op['sender_gid'],
           'PRO_SENDER_ACTUAL_NONROOT_IDENTITY')
    return dict(value=None, operation=op, records={}, base=PACKET / 'carrier', raw=b'')


def s4_current(selection):
    seams['S4_sender_current'] += 1
    op = selection['operation']
    P.need(op['issued_unix_ms'] <= int(time.time() * 1000) < op['expires_unix_ms']
           and os.getuid() == os.geteuid() == op['sender_uid'] and os.getgid() == os.getegid() == op['sender_gid'],
           'PRO_SENDER_CURRENT_OPERATION_CHANGED')
    return True


def s5_check(index, bodies, core):
    seams['S5_check_inputs'] += 1
    C.check_index(index)
    P.need(set(bodies) == set(index) and all(P.descriptor(bodies[n]) == r for n, r in index.items())
           and core.get('component_scope') == P.SCOPE, 'ACTUAL_INPUT_BODY_CHANGED')


real_acquire = F.acquire
reads = []


def observed_acquire(root, index, private=False):
    if not reads:
        probes.append(QC.probe('P1_first_private_read', cfg, SC))
    reads.append(str(root))
    return real_acquire(root, index, private)


P.load, K.current_binding, SP.load, SP.current, P.check_inputs, F.acquire = s2_load, s3_current, s4_load, s4_current, s5_check, observed_acquire
ctx = cfg['context']
result = K.root_payload(ctx['run_id'], ctx['workflow_commit'], cfg['artifact_id'], archive)
out['root_payload'] = dict(result=result['result'], files={k: P.descriptor(v) for k, v in result['files'].items()},
                           private_reads=reads, seam_calls=dict(seams))
probes.append(QC.probe('P2_after_root_payload_cleanup', cfg, SC))

# v2 rehearsal (through carrier.Commands) repeated INSIDE the whole-sender sandbox, in its private /tmp.
reh = Path('/tmp/reh')
reh.mkdir(mode=0o700)
env = {'PATH': '/usr/bin:/bin', 'OPENSSL_CONF': '/dev/null'}
subprocess.run(['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:3072', '-noenc', '-sha256', '-days', '1', '-subj',
                '/CN=disposable-rehearsal', '-keyout', str(reh / 'k.key'), '-out', str(reh / 'k.pem')],
               check=True, capture_output=True, env=env)
plain = os.urandom(300000)


def session(name):
    directory = reh / name
    fd, _ = F.private_directory(directory)
    os.close(fd)
    budget = K.new_budget(directory)
    h = dict(plain=F.OutputFile(directory, 'bundle.plain', C.MAX_PLAINTEXT_BYTES, budget),
             certificate=F.OutputFile(directory, 'recipient.pem', P.MAX_CERTIFICATE, budget),
             cipher=F.OutputFile(directory, 'INPUTS.cms', P.MAX_CIPHERTEXT, budget))
    h['plain'].write(plain)
    h['certificate'].write((reh / 'k.pem').read_bytes())
    return directory, budget, h


def refusal(fn):
    try:
        fn()
        return 'NO_REFUSAL'
    except BaseException as exc:  # noqa: BLE001 - closed code only
        return f'{type(exc).__name__}:{exc}'


rb = dict(sender_tools=binding['sender_tools'], limits=binding['limits'], _binding_raw=binding['_binding_raw'],
          _sender_selection=s4_load(binding, cfg['operation']['context'], cfg['artifact_id'], archive))
d, b, h = session('commands')
cmd = K.Commands(rb, 'root', d, b, time.monotonic() + 120, P.sha(b'disposable-request'))
rc = cmd.run('encrypt', h)
record = json.loads((d / 'COMMAND_encrypt.json').read_bytes())
cipher = h['cipher'].read()
K.require_auth_enveloped(cipher)
(reh / 'c.der').write_bytes(cipher)
dec = subprocess.run(['/usr/bin/openssl', 'cms', '-decrypt', '-binary', '-inform', 'DER', '-in', str(reh / 'c.der'), '-recip',
                      str(reh / 'k.pem'), '-inkey', str(reh / 'k.key')], capture_output=True, env=env)
owner = json.loads((d / 'SENDER_CAPTURE_OWNER.json').read_bytes())
closed = cmd.closed()
cleanup = [x.cleanup() for x in h.values()]
out['rehearsal_commands_encrypt'] = dict(
    returncode=rc, argv_is_sandbox_form=record['argv'][:len(SC.SANDBOX_PREFIX)] == SC.SANDBOX_PREFIX,
    env_not_executed='/usr/bin/env' not in record['argv'], tool_descriptors=record['tool_descriptors'],
    capture_cleanup=record['capture'][0]['cleanup'], restoration=owner['restoration'], cipher_bytes=len(cipher),
    decrypt_rc=dec.returncode, decrypts_to_plaintext=dec.stdout == plain, closed=closed,
    cleanup_unlinked=all(r.get('unlinked') for r in cleanup))
bad = json.loads(json.dumps(rb['sender_tools']))
bad['bwrap']['sha256'] = '0' * 64
d3, b3, h3 = session('refuse-bwrap-pin')
out['rehearsal_refusals'] = {
    '3a_wrong_bwrap_pin': refusal(lambda: K.Commands(dict(rb, sender_tools=bad), 'root', d3, b3, time.monotonic() + 60, None))}
historical_root_tools = {'env': {'bytes': 56144, 'sha256': 'eb1c64bbc9908afcdf8cb48524f17112d8dd76a249f80dee2f01da14747b3b6e'},
                         'openssl': {'bytes': 1103304, 'sha256': 'acc10176d038aeb7b2a77d9ec972ac2985857a7191f7aecb7c54ef0e2c7e9549'}}
d4, b4, h4 = session('refuse-historical-root-tools')
out['rehearsal_refusals']['3b_retired_root_tools_as_sender_pins'] = refusal(
    lambda: K.Commands(dict(rb, sender_tools=historical_root_tools), 'root', d4, b4, time.monotonic() + 60, None))
row = cmd.tool_rows['bwrap']
moved = dict(row, identity=[*row['identity'][:5], row['identity'][5] + 1, *row['identity'][6:]])
out['rehearsal_refusals']['3c_launcher_identity_changed'] = refusal(lambda: os.close(SC.launcher_fd(moved)))
out['rehearsal_refusals']['3c_launcher_identity_exact'] = refusal(lambda: os.close(SC.launcher_fd(row)))
old = ['/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LC_ALL=C', 'OPENSSL_CONF=/dev/null', '/usr/bin/openssl', 'cms', '-encrypt',
       '-binary', '-aes-256-gcm', '-in', '/proc/self/fd/3', '-outform', 'DER', '-out', '/proc/self/fd/5', '-recip',
       '/proc/self/fd/4', '-keyopt', 'rsa_padding_mode:oaep', '-keyopt', 'rsa_oaep_md:sha256', '-keyopt', 'rsa_mgf1_md:sha256']
out['rehearsal_refusals']['3d_v1_env_argv'] = refusal(lambda: SC.validate_command('carrier-encrypt', old, (3, 4, 5)))
copy = reh / 'bwrap-copy'
copy.write_bytes(Path('/usr/bin/bwrap').read_bytes())
os.chmod(copy, 0o755)
out['rehearsal_refusals']['3e_tool_outside_attested_chain'] = refusal(
    lambda: K.sender_tool_custody(copy, F.read_file(copy, 32 * 1024**2)[1]))
for hs in (h3, h4):
    for x in hs.values():
        x.cleanup()
out['probes'] = probes
out['final_require_sender_sandbox'] = refusal(SC.require_sender_sandbox)
print(json.dumps(out, sort_keys=True), flush=True)
