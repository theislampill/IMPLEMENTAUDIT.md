"""Shared helpers for the G132 v3 whole-sender qualification. Disposable public inputs only.

Loaded by file path (python -I does not put the script directory on sys.path). Nothing here performs a
network, provider or GitHub call: the "GitHub" tool results are synthetic and are written into the tool
broker by the separate dispatcher stand-in, exactly where the real root dispatcher would write them.
"""
import datetime
import errno
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import time
from pathlib import Path


def load_file(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def carrier(packet):
    return load_file(Path(packet) / 'carrier' / 'carrier_loader.py', 'carrier_loader').load()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding_for(pub, packet, cfg):
    """The binding P.load() would return, but with the disposable input index (seam S2).

    P.load() itself cannot run: it requires the issued CARRIER_ADMISSION (stale for this candidate) and the
    INPUT_INDEX of the real private inputs. Everything else is read from the actual candidate files.
    """
    P, F = pub.policy, pub.files
    packet = Path(packet)
    base = packet / 'carrier'
    raw, brow = F.read_file(base / 'CARRIER_COMPOSITION.json', P.MAX_INDEX)
    P.need(P.sha(raw) == P.BINDING_SHA256, 'QUAL_BINDING_PIN')
    v = P.parse(raw, P.MAX_INDEX)
    records = {}
    for name, row in v['core_bodies'].items():
        body, records[name] = F.read_file(packet / name, 1024 * 1024)
        P.need(P.descriptor(body) == row, 'QUAL_CORE_BODY_PIN')
    admission, arow = F.read_file(base / 'CARRIER_ADMISSION.json', P.MAX_INDEX)
    _, irow = F.read_file(base / 'INPUT_INDEX.json', P.MAX_INDEX)
    _, prow = F.read_file(packet / 'root_placement.py', 1024 * 1024)
    v.update(_packet=packet, _base=base, _index=cfg['index'], _opening_core=records, _binding_raw=raw,
             _admission_raw=admission, _opening_contract=dict(binding=brow, index=irow, admission=arow),
             _opening_placement=prow)
    return v


def iso(ms):
    return datetime.datetime.fromtimestamp(ms // 1000, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def provider_body(kind, cfg, archive, workflow_raw):
    """Synthetic GitHub REST bodies consistent with the disposable request (no provider contact)."""
    ctx = cfg['context']
    run = int(ctx['run_id'])
    issued = cfg['issued_unix_ms']
    repo = {'full_name': ctx['repository'], 'id': 4242}
    if kind == 'workflow':
        return workflow_raw
    if kind in ('run', 'attempt'):
        value = dict(id=run, run_attempt=1, event='push', status='in_progress', head_branch=ctx['branch'],
                     head_sha=ctx['workflow_commit'], path=ctx['workflow_path'], repository=repo, head_repository=repo,
                     run_started_at=iso(issued - 120000))
    elif kind == 'jobs':
        value = dict(total_count=1, jobs=[dict(id=7777, run_id=run, run_attempt=1, head_sha=ctx['workflow_commit'],
                                               name=ctx['job_name'], status='in_progress', started_at=iso(issued - 60000))])
    else:
        artifact = dict(id=cfg['artifact_id'], name='dg16-core-private-recipient-' + ctx['run_id'] + '-a1', expired=False,
                        size_in_bytes=len(archive), digest='sha256:' + sha(archive), created_at=iso(issued + 1000),
                        workflow_run=dict(id=run, head_sha=ctx['workflow_commit'], head_branch=ctx['branch'],
                                          repository_id=4242, head_repository_id=4242))
        value = artifact if kind == 'artifact' else dict(total_count=1, artifacts=[artifact])
    return json.dumps(value, sort_keys=True).encode()


def tool_result(url, body):
    text = body.decode('utf-8')
    return json.dumps(dict(content=[dict(type='text', text=text)], isError=False,
                           structuredContent=dict(url=url, display_url=url, content=text)), sort_keys=True).encode()


def _errno_of(fn):
    try:
        value = fn()
        return dict(ok=True, value=value)
    except OSError as exc:
        return dict(ok=False, errno=errno.errorcode.get(exc.errno, exc.errno), error=type(exc).__name__)


def _connect_unix(address):
    def go():
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(3)
            s.connect(address)
            return 'CONNECTED'
        finally:
            s.close()
    return _errno_of(go)


def _tcp(host, port):
    def go():
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return 'CONNECTED'
    return _errno_of(go)


def _dns(name):
    try:
        return dict(ok=True, value=sorted({r[4][0] for r in socket.getaddrinfo(name, 443)}))
    except OSError as exc:
        return dict(ok=False, error=type(exc).__name__, detail=str(exc)[:80])


def _run(argv):
    try:
        r = subprocess.run(argv, capture_output=True, env={}, timeout=10, stdin=subprocess.DEVNULL)
        return dict(returncode=r.returncode, stdout=r.stdout[:200].decode('utf-8', 'replace'),
                    stderr=r.stderr[:300].decode('utf-8', 'replace'))
    except OSError as exc:
        return dict(spawn_error=errno.errorcode.get(exc.errno, exc.errno))


def reachability(cfg, names=True):
    """What the current process can reach. Public, harmless probes only (no request is sent anywhere)."""
    paths = {}
    for p in ('/home', '/home/agent', '/home/agent/.bashrc', '/etc/passwd', '/etc/shadow', '/etc/sudoers', '/root',
              '/var/log', '/run/docker.sock', '/var/run/docker.sock', '/run/WSL', '/mnt', '/mnt/c', '/init', '/usr/share/ollama',
              '/proc/1/root/home/agent/.bashrc'):
        if os.path.isdir(p):
            paths[p] = _errno_of(lambda p=p: sorted(os.listdir(p))[:8] if names else 'LISTABLE (%d entries; names withheld)' % len(os.listdir(p)))
        else:
            paths[p] = _errno_of(lambda p=p: (os.close(os.open(p, os.O_RDONLY)), 'OPENED')[1])
    return dict(
        sudo_n_true=_run(['/usr/bin/sudo', '-n', 'true']),
        docker_socket={p: _connect_unix(p) for p in ('/var/run/docker.sock', '/run/docker.sock')},
        host_abstract_socket={cfg['abstract_probe']: _connect_unix('\0' + cfg['abstract_probe'])},
        tcp_github_ip_443=_tcp(cfg['github_ip'], 443),
        tcp_loopback_22=_tcp('127.0.0.1', 22),
        dns_github=_dns('github.com'),
        interfaces=[line.split(':')[0].strip() for line in open('/proc/net/dev').read().splitlines()[2:]],
        paths=paths)


def probe(point, cfg, SC):
    s = SC.status_rows()
    try:
        SC.require_sender_sandbox()
        live = 'IN_FORCE'
    except ValueError as exc:
        live = 'REFUSED:' + str(exc)
    return dict(point=point, monotonic_ns=time.monotonic_ns(), require_sender_sandbox=live,
                status={k: s.get(k) for k in ('NoNewPrivs', 'Seccomp', 'CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb',
                                              'Uid', 'Gid', 'Groups')},
                uid_map=open('/proc/self/uid_map').read().split(), gid_map=open('/proc/self/gid_map').read().split(),
                setgroups=open('/proc/self/setgroups').read().strip(),
                namespaces={n: os.readlink('/proc/self/ns/' + n) for n in ('user', 'mnt', 'net', 'pid', 'ipc', 'uts')},
                mountinfo=open('/proc/self/mountinfo').read().splitlines(),
                open_descriptors=sorted(int(x) for x in os.listdir('/proc/self/fd')),
                reachability=reachability(cfg))
