"""Outer side of the G132 v3 whole-sender qualification (runs as the original sender UID, unsandboxed).

Usage: python3.12 -I -B qual_outer.py MODE PACKET WORK
  e2e        sender_capture._launch(entry=qual/qual_inner.py) with the composition's sender_tools pins
  negpin     _launch refuses before fork when the bwrap (or openssl) pin differs
  unsandboxed  the inner self-check, root_payload and Commands(root) refuse with no sandbox (NoNewPrivs 0, ...)
  variants   deliberately weakened whole-sender argvs (pinned bwrap) -> the inner self-check refuses
  verify     after e2e: decrypt the retained INPUTS.cms with the disposable key, check cleanup and effects
  contrast   what this unsandboxed account itself can reach (no sudo command is executed)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import importlib.util

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('qual_common', str(HERE / 'qual_common.py'))
QC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(QC)
mode, packet, work = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
pub = QC.carrier(packet)
SC, P, F, C, K = pub.sender_capture, pub.policy, pub.files, pub.codec, pub.carrier
comp_raw = (packet / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes()
pins = P.parse(comp_raw, P.MAX_INDEX)['sender_tools']
root = packet.parent


def refusal(fn):
    try:
        return 'NO_REFUSAL:' + repr(fn())
    except BaseException as exc:  # noqa: BLE001 - closed code only
        return f'{type(exc).__name__}:{exc}'


def cfg_for():
    return json.loads(next(work.glob('config-*.json')).read_bytes()) if mode != 'e2e' else json.loads(
        (packet / 'qual' / 'config.json').read_bytes())


MASKED = SC.group_masks(os.getgid()) if mode in ('unsandboxed', 'variants') else []


def attestation():
    """The attestation _launch would pass (for unsandboxed/variant controls)."""
    rows = {n: F.read_file(Path('/usr/bin') / n, 32 * 1024**2)[1] for n in ('openssl', 'bwrap')}
    att = dict(schema=SC.ATTESTATION_SCHEMA, uid=os.getuid(), gid=os.getgid(), overflow=SC.overflow_ids(),
               namespaces=SC.namespaces(), usr_submounts=sorted(r[0] for r in SC.mounts() if r[0].startswith('/usr/')),
               masked=MASKED,
               root=str(root), packet=str(packet), entry=SC.ENTRY,
               tools={n: dict(identity=r['identity'], ancestors=r['ancestors']) for n, r in rows.items()})
    return P.encode(att).decode('ascii')[:-1]


if mode == 'e2e':
    cfg = cfg_for()
    ctx = cfg['context']
    outer_status = SC.status_rows()
    sys.stderr.write(json.dumps(dict(outer_before_launch=dict(
        status={k: outer_status.get(k) for k in ('NoNewPrivs', 'CapBnd', 'Groups', 'Seccomp')},
        placement_before=sorted(os.listdir(root)))), sort_keys=True) + '\n')
    rc = SC._launch(packet, packet / 'qual' / 'qual_inner.py', pins,
                    [ctx['run_id'], ctx['workflow_commit'], str(cfg['artifact_id'])], work / 'request.zip')
    sys.stderr.write(json.dumps(dict(launch_rc=rc, placement_after=sorted(os.listdir(root)))) + '\n')
    sys.exit(rc)

out = {}
if mode == 'negpin':
    cfg = cfg_for()
    args = [cfg['context']['run_id'], cfg['context']['workflow_commit'], str(cfg['artifact_id'])]
    before = sorted(os.listdir(root))
    for tool in ('bwrap', 'openssl'):
        bad = json.loads(json.dumps(pins))
        bad[tool]['sha256'] = '0' * 64
        out['wrong_' + tool + '_pin'] = refusal(lambda: SC._launch(packet, packet / 'carrier' / 'sender_launch.py', bad, args,
                                                                    work / 'request.zip'))
    bad = json.loads(json.dumps(pins))
    bad['bwrap']['bytes'] += 1
    out['wrong_bwrap_size'] = refusal(lambda: SC._launch(packet, packet / 'carrier' / 'sender_launch.py', bad, args,
                                                         work / 'request.zip'))
    row = F.read_file(Path('/usr/bin/bwrap'), 32 * 1024**2)[1]
    out['launcher_fd_identity_changed'] = refusal(lambda: SC.launcher_fd(dict(row, identity=[*row['identity'][:6], 1, *row['identity'][7:]])))
    out['placement_unchanged'] = sorted(os.listdir(root)) == before
    out['placement_listing'] = before
elif mode == 'unsandboxed':
    att = attestation()
    facts, failures = SC.sandbox_facts(att)
    out['outer_view'] = {k: facts.get(k) for k in ('status', 'uid_map', 'interfaces', 'environment', 'descriptors')}
    out['outer_view']['top_level_entries'] = len(facts.get('top') or [])  # host / listing withheld (count only)
    out['policy_load_real'] = refusal(P.load)  # the issued-record seam the production entry stops at
    out['self_check_failures_in_order'] = failures
    out['enter_sender_sandbox'] = refusal(lambda: SC.enter_sender_sandbox(att))
    out['require_sender_sandbox'] = refusal(SC.require_sender_sandbox)
    reads = []
    real = F.acquire
    F.acquire = lambda *a, **k: (reads.append(str(a[0])), real(*a, **k))[1]
    out['root_payload'] = K.root_payload('424242', '0' * 40, 1, (work / 'request.zip').read_bytes())['result']['code']
    out['commands_root'] = refusal(lambda: K.Commands(dict(_sender_selection={}, sender_tools=pins, limits={}), 'root',
                                                      Path('/nonexistent'), None, time.monotonic() + 5, None))
    out['tool_custody'] = refusal(lambda: K.sender_tool_custody(Path('/usr/bin/bwrap'), F.read_file(Path('/usr/bin/bwrap'), 32 * 1024**2)[1]))
    out['private_reads'] = reads
    for label, att_arg in (('cli_inside_without_sandbox', att), ('cli_inside_junk_attestation', '{}')):
        r = subprocess.run(['/usr/bin/python3.12', '-I', '-S', '-B', str(packet / 'carrier' / 'sender_launch.py'), '--inside',
                            att_arg, '424242', '0' * 40, '1'], capture_output=True, env={'PATH': '/usr/bin:/bin'},
                           stdin=subprocess.DEVNULL)
        out[label] = dict(returncode=r.returncode, last_line=r.stderr.decode().strip().splitlines()[-1][:200])
elif mode == 'variants':
    att = attestation()
    entry = str(packet / 'qual' / 'qual_variant.py')
    base = SC.whole_sender_argv(str(root), str(packet), entry, ['--inside', att], MASKED)
    out['masked'] = MASKED

    def variant(name, argv):
        r = subprocess.run(argv + [name], capture_output=True, env={}, stdin=subprocess.DEVNULL, close_fds=True)
        try:
            return json.loads(r.stdout.decode().strip().splitlines()[-1])
        except (ValueError, IndexError):
            return dict(returncode=r.returncode, stderr=r.stderr.decode()[-400:])
    def find(argv, item):
        return next(i for i in range(len(argv)) if argv[i:i + len(item)] == list(item))
    cut = find(base, ('--remount-ro', '/'))  # extra mounts go before the final read-only remount of /

    def with_extra(extra):
        return base[:cut] + extra + base[cut:]

    def without(*items):
        argv = list(base)
        for item in items:
            i = find(argv, item)
            del argv[i:i + len(item)]
        return argv
    out['V0_exact_argv'] = variant('V0_exact_argv', base)
    out['V1_share_net'] = variant('V1_share_net', with_extra(['--share-net']))
    out['V2_extra_home_bind'] = variant('V2_extra_home_bind', with_extra(['--ro-bind', str(work), str(work)]))
    out['V3_extra_environment'] = variant('V3_extra_environment', with_extra(['--setenv', 'HOME', '/home/agent']))
    out['V4_root_left_writable'] = variant('V4_root_left_writable', without(('--remount-ro', '/')))
    out['V5_no_cap_drop'] = variant('V5_no_cap_drop', without(('--cap-drop', 'ALL')))
    out['V7_group_readable_usr_tree_unmasked'] = variant('V7_group_readable_usr_tree_unmasked',
                                                         SC.whole_sender_argv(str(root), str(packet), entry, ['--inside', att]))
    out['V6_docker_socket_bound'] = variant('V6_docker_socket_bound', with_extra(['--bind', '/run/docker.sock', '/run/docker.sock']))
elif mode == 'verify':
    cfg = json.loads((packet / 'qual' / 'config.json').read_bytes())
    run_id = cfg['context']['run_id']
    session = root / ('dg16-private-sender-' + run_id + '-a1')
    bodies = {n: bytes.fromhex(h) for n, h in json.loads((work / ('bodies-' + run_id + '.json')).read_text()).items()}
    expected_plain = C.pack(cfg['index'], bodies, cfg['request_sha256'])
    dec = subprocess.run(['/usr/bin/openssl', 'cms', '-decrypt', '-binary', '-inform', 'DER', '-in', str(session / 'INPUTS.cms'),
                          '-recip', str(work / (run_id + '.pem')), '-inkey', str(work / (run_id + '.key'))],
                         capture_output=True, env={'PATH': '/usr/bin:/bin', 'OPENSSL_CONF': '/dev/null'})
    owner = json.loads((session / 'SENDER_CAPTURE_OWNER.json').read_bytes())
    command = json.loads((session / 'COMMAND_encrypt.json').read_bytes())
    outcome = json.loads((session / 'OUTCOME.json').read_bytes())
    end = json.loads((session / 'BROKER_END.json').read_bytes())
    control = P.parse((session / 'CONTROL.json').read_bytes(), P.MAX_CONTROL)
    cipher = (session / 'INPUTS.cms').read_bytes()
    out = dict(session_members=sorted(p.name for p in session.iterdir()),
               plaintext_temporaries_absent={n: not (session / n).exists() for n in ('bundle.plain', 'recipient.pem', 'recipient.key',
                                                                                     'quarantine.plain')},
               placement_members=sorted(os.listdir(root)), decrypt_rc=dec.returncode,
               decrypts_to_exact_bundle=dec.stdout == expected_plain, bundle_bytes=len(expected_plain),
               ciphertext=P.descriptor(cipher), control_ciphertext_join=control['ciphertext'] == P.descriptor(cipher),
               control_request_join=control['request_sha256'] == cfg['request_sha256'],
               encrypt_argv_is_sandbox_prefix=command['argv'][:len(SC.SANDBOX_PREFIX)] == SC.SANDBOX_PREFIX,
               encrypt_tool_descriptors=command['tool_descriptors'], capture_restoration=owner['restoration'],
               capture_failure=owner['failure'], capture_returncode=owner['primary_returncode'],
               broker_end=dict(complete=end['complete'], prefix_entries=end['prefix_entries']),
               outcome_public=outcome['public'], outcome_owned_cleanup=outcome['owned_cleanup'])
elif mode == 'contrast':
    cfg = cfg_for()
    import socket
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind('\0' + cfg['abstract_probe'])
    listener.listen(4)
    s = SC.status_rows()
    out = dict(status={k: s.get(k) for k in ('NoNewPrivs', 'CapEff', 'CapBnd', 'Uid', 'Gid', 'Groups', 'Seccomp')},
               id=subprocess.run(['/usr/bin/id'], capture_output=True).stdout.decode().strip(),
               reachability={k: v for k, v in QC.reachability(cfg, names=False).items() if k != 'sudo_n_true'},
               sudo_note='sudo is NOT executed outside the sandbox; group membership is shown by id instead')
print(json.dumps(out, indent=1, sort_keys=True))
