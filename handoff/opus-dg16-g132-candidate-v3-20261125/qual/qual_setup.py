"""Build one disposable sender placement. Usage: python3.12 -I -B qual_setup.py EPISODE PLACEMENT WORK RUN_ID [--qual]

PLACEMENT/<dg16-r5-g1-hosted-episode> is a copy of the candidate episode plus disposable private-inputs (random
bytes, 0600 files in 0700 directories). WORK (outside the placement, never visible to the sandbox) holds the
disposable recipient key, the request artifact ZIP and the workflow copy. With --qual, the qualification inner
files and config are added under the packet at qual/. Nothing private or issued is used or created.
"""
import hashlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).absolute().parent
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location('qual_common', str(HERE / 'qual_common.py'))
QC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(QC)
episode, placement, work, run_id = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
qual = '--qual' in sys.argv[5:]
placement.mkdir(mode=0o700)
os.chmod(placement, 0o700)
work.mkdir(mode=0o700, exist_ok=True)
packet = placement / 'dg16-r5-g1-hosted-episode'
shutil.copytree(episode, packet)
for p in [packet, *packet.rglob('*')]:
    os.chmod(p, 0o755 if p.is_dir() else 0o644)
pub = QC.carrier(packet)
P, C = pub.policy, pub.codec
comp = P.parse((packet / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes(), P.MAX_INDEX)
bodies = {'disposable/alpha.bin': os.urandom(200000), 'disposable/beta.json': b'{"disposable":true}\n',
          'gamma.txt': b'disposable public qualification input\n'}
index = {n: P.descriptor(b) for n, b in sorted(bodies.items())}
private = packet / 'private-inputs'
(private / 'disposable').mkdir(parents=True, mode=0o700)
os.chmod(private, 0o700)
for name, body in bodies.items():
    fd = os.open(private / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(fd, body)
    os.close(fd)
key, cert = work / (run_id + '.key'), work / (run_id + '.pem')
subprocess.run(['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:3072', '-noenc', '-sha256', '-days', '1', '-subj',
                '/CN=DG16-core-private-recipient', '-keyout', str(key), '-out', str(cert)],
               check=True, capture_output=True, env={'PATH': '/usr/bin:/bin', 'OPENSSL_CONF': '/dev/null'})
os.chmod(key, 0o600)
ctx = dict(repository=P.REPOSITORY, branch=comp['branch'], workflow_commit=hashlib.sha1(b'g132v3-disposable').hexdigest(),
           workflow_path=comp['workflow_path'], run_id=run_id, run_attempt=1, job_name=comp['job_name'])
issued = int(time.time() * 1000) - 30000
expires = issued + 590000
nonce = os.urandom(32).hex()
request = P.make_request(ctx, index, cert.read_bytes(), nonce, issued, expires)
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, body in (('REQUEST.json', request), ('RECIPIENT.pem', cert.read_bytes())):
        info = zipfile.ZipInfo(name, date_time=(2026, 11, 25, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0
        z.writestr(info, body)
archive = buf.getvalue()
(work / 'request.zip').write_bytes(archive)
(work / ('bodies-' + run_id + '.json')).write_text(json.dumps({n: b.hex() for n, b in bodies.items()}))
artifact_id = 9000000 + int(run_id) % 1000000
operation = dict(schema='dg16.pro-private-sender-operation.v1', successor='PRO-EXECUTOR-01, designated by owner', context=ctx,
                 source_commit=comp['source_commit'], source_tree=comp['source_tree'],
                 carrier_binding_sha256=P.sha((packet / 'carrier' / 'CARRIER_COMPOSITION.json').read_bytes()),
                 input_index_sha256=C.check_index(index), artifact_id=artifact_id, artifact=P.descriptor(archive), nonce=nonce,
                 issued_unix_ms=issued, expires_unix_ms=expires, sender_uid=os.getuid(), sender_gid=os.getgid(), original_awards=[])
# A listening abstract unix socket of the HOST network namespace, held by the dispatcher stand-in (outside).
abstract = 'dg16-g132v3-qual-' + run_id
github_ip = sorted({r[4][0] for r in socket.getaddrinfo('github.com', 443, socket.AF_INET)})[0]
cfg = dict(context=ctx, index=index, operation=operation, artifact_id=artifact_id, issued_unix_ms=issued,
           abstract_probe=abstract, github_ip=github_ip, request_sha256=P.sha(request))
(work / ('config-' + run_id + '.json')).write_text(json.dumps(cfg, sort_keys=True))
shutil.copy(episode.parent.parent / '.github' / 'workflows' / 'dg16-r5-g1-hosted-episode.yml', work / 'workflow.yml')
if qual:
    q = packet / 'qual'
    q.mkdir(mode=0o755)
    for name in ('qual_common.py', 'qual_inner.py', 'qual_variant.py'):
        shutil.copy(HERE / name, q / name)
        os.chmod(q / name, 0o644)
    (q / 'config.json').write_text(json.dumps(cfg, sort_keys=True))
    os.chmod(q / 'config.json', 0o644)
print(json.dumps(dict(placement=str(placement), packet=str(packet), run_id=run_id, artifact_id=artifact_id,
                      index=index, archive=P.descriptor(archive), abstract_probe=abstract, github_ip=github_ip)))
