"""Issue the five late G1 sender inputs after Root receives a real current04 recipient.

This command is invoked by the Root operator only after independent publication
and recipient receiving. It neither launches the sender nor contacts GitHub.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import time
import types

BASE = Path('/home/agent/dg16-g1-current04-operators')
RECEIVER = BASE / 'public-receiver-02'
READER = RECEIVER / 'author/receiver.py'
READER_SHA = '378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
HOST_COMMIT = 'f9ba187e8f5520956f0f16cf13c0a706e8360b96'
HOST_TREE = '8390375505282e602759c7976b6bca82a44d5737'

def require(ok, code):
    if not ok:
        raise ValueError(code)

def private_directory(path):
    require(path.is_absolute() and path.resolve(strict=True) == path and path.is_relative_to(BASE),
            'PRIVATE_CANONICAL_ROOT')
    st = path.stat()
    require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid() and stat.S_IMODE(st.st_mode) == 0o700,
            'PRIVATE_DIRECTORY_OWNER')

def load_reader():
    def identity(st):
        return (st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_uid, st.st_gid,
                st.st_size, st.st_mtime_ns, st.st_ctime_ns)

    require(READER.resolve(strict=True) == READER, 'INSTALLED_READER_ALIAS')
    before = READER.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
            and before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) in (0o400, 0o444)
            and 0 < before.st_size <= 1024**2, 'INSTALLED_READER_CUSTODY')
    fd = os.open(READER, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        require(identity(os.fstat(fd)) == identity(before) and not os.listxattr(fd), 'INSTALLED_READER_OPEN')
        raw = os.pread(fd, before.st_size+1, 0)
        require(len(raw) == before.st_size and hashlib.sha256(raw).hexdigest() == READER_SHA
                and identity(os.fstat(fd)) == identity(before) == identity(READER.lstat())
                and READER.resolve(strict=True) == READER, 'INSTALLED_RECEIVER_CHANGED')
    finally:
        os.close(fd)
    m = types.ModuleType('root_recipient_receiver')
    m.__file__ = str(READER)
    exec(compile(raw, str(READER), 'exec'), m.__dict__)
    return m

def publication_join(R, source, raw, ctx):
    """Join the same three Root-received GitHub bodies used at launch."""
    v = R.parse(raw, R.MAX_RESULT)
    ref, commit, run = v['ref'], v['commit'], v['run']
    require(ref['ref'] == 'refs/heads/'+ctx['branch'] and ref['object']['type'] == 'commit'
            and ref['object']['sha'] == commit['sha'] == run['head_sha'] == HOST_COMMIT,
            'PUBLICATION_HEAD_CHANGED')
    require(commit['tree']['sha'] == HOST_TREE
            and [row['sha'] for row in commit['parents']] == [source.P.SOURCE_COMMIT],
            'PUBLICATION_TREE_OR_ANCESTRY_CHANGED')
    require(run['repository']['full_name'] == run['head_repository']['full_name'] == ctx['repository']
            and run['head_branch'] == ctx['branch'] and run['path'] == ctx['workflow_path']
            and run['event'] == 'push' and type(run['id']) is int and str(run['id']) == ctx['run_id']
            and type(run['run_attempt']) is int and run['run_attempt'] == ctx['run_attempt'] == 1,
            'PUBLICATION_RUN_CHANGED')

def derive(R, source, received, archive, publication, packet, issued, nonce, uid, gid):
    require(received['phase'] == 'recipient' and received['context']['workflow_commit'] == HOST_COMMIT,
            'CURRENT04_RECIPIENT_REQUIRED')
    ctx = received['context']
    publication_join(R, source, publication, ctx)
    q = R.parse(received['files']['REQUEST.json'])
    receipt = received['receipt']
    require(receipt['archive'] == R.desc(archive), 'RECIPIENT_ARCHIVE_CHANGED')
    limit = min(q['expires_unix_ms'], issued + source.binding['limits']['acquisition_seconds'] * 1000)
    require(q['issued_unix_ms'] <= issued < limit, 'RECIPIENT_WINDOW_CLOSED')
    require(q['nonce'] != nonce and len(nonce) == 64, 'DISTINCT_OPERATION_NONCE_REQUIRED')
    common = dict(source_commit=source.P.SOURCE_COMMIT, source_tree=source.P.SOURCE_TREE,
                  carrier_binding_sha256=R.sha(source.binding_raw),
                  input_index_sha256=source.binding['input_index']['sha256'],
                  artifact_id=receipt['provider']['artifact_id'], artifact=R.desc(archive), original_awards=[])
    selected = dict(common, schema='dg16.late-root-sender-assembly-selection.v1', issuer='R5_ROOT_GOVERNOR',
                    fixed_packet_directory=str(packet), workflow_commit=ctx['workflow_commit'],
                    workflow_branch=ctx['branch'], workflow_path=ctx['workflow_path'],
                    workflow_sha256=source.binding['workflow_sha256'], **source.anchor,
                    request_sha256=R.sha(received['files']['REQUEST.json']),
                    actual_host_receiving_sha256=R.sha(publication))
    op = dict(common, schema='dg16.pro-private-sender-operation.v1', context=ctx, nonce=nonce,
              issued_unix_ms=issued, expires_unix_ms=limit, sender_uid=uid, sender_gid=gid)
    composition = R.parse(source.body(R.CORE+'carrier/PRO_SENDER_COMPOSITION.json'))
    admission = dict(schema='dg16.pro-private-sender-root-admission.v1', issuer='R5_ROOT_GOVERNOR',
                     operation_sha256=R.sha(R.encode(op)), capture_profile=composition['capture_profile'],
                     provider_profile=source.B.PROFILE, source_commit=source.P.SOURCE_COMMIT,
                     source_tree=source.P.SOURCE_TREE, carrier_binding_sha256=common['carrier_binding_sha256'],
                     limits=source.binding['limits'], one_encryption=True, metadata_reads=18,
                     automatic_retry=False, host_or_native_effect_grant=False, original_awards=[])
    return {'ROOT_SENDER_ASSEMBLY_SELECTION.json': R.encode(selected), 'PRO_SENDER_OPERATION.json': R.encode(op),
            'PRO_SENDER_ADMISSION.json': R.encode(admission), 'ROOT_REQUEST_ARTIFACT.zip': archive,
            'HOST_PUBLICATION_ROOT_RECEIVING.json': publication}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('session', type=Path)
    p.add_argument('recipient_receipt_sha256')
    p.add_argument('publication_receipt', type=Path)
    p.add_argument('publication_receipt_sha256')
    p.add_argument('episode_directory', type=Path)
    a = p.parse_args()
    require(sys.platform == 'linux' and sys.flags.isolated and sys.dont_write_bytecode
            and os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid(), 'FIXED_RUNTIME')
    private_directory(a.session)
    require(a.session.parent == RECEIVER/'sessions', 'EXACT_SESSION_PARENT')
    private_directory(a.episode_directory)
    private_directory(a.publication_receipt.parent)
    R = load_reader()
    source = R.Sources()
    session = R.Session(a.session, source)
    raw = R.read(a.session/'RECEIVING.json')
    require(R.sha(raw) == a.recipient_receipt_sha256, 'ACTUAL_RECEIVING_DIGEST')
    saved = R.parse(raw)
    got = session.receive(saved['observed_unix_ms'], save=False)
    require(raw == R.encode(got['receipt']), 'RECEIVING_READBACK_CHANGED')
    publication = R.read(a.publication_receipt, R.MAX_RESULT)
    require(R.sha(publication) == a.publication_receipt_sha256, 'ROOT_PUBLICATION_RECEIVING_DIGEST')
    archive = R.read(a.session/'ARTIFACT.zip', R.PHASES['recipient'][2])
    output = a.episode_directory/'late-inputs'
    target = a.episode_directory/'assembled'
    require(not os.path.lexists(target), 'FRESH_ASSEMBLER_DESTINATION')
    bodies = derive(R, source, got, archive, publication, target/'packet',
                    time.time_ns()//1000000, secrets.token_hex(32), os.geteuid(), os.getegid())
    output.mkdir(mode=0o700)
    for name, body in bodies.items():
        fd = os.open(output/name, os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as writer:
            writer.write(body)
            writer.flush()
            os.fsync(writer.fileno())
        require(R.read(output/name, max(1,len(body))) == body, 'NEW_BODY_READBACK')
    session.sync(output)
    session.sync(a.episode_directory)
    require(time.time_ns()//1000000 < R.parse(bodies['PRO_SENDER_OPERATION.json'])['expires_unix_ms'],
            'NEW_BODY_WINDOW_CLOSED')
    print(json.dumps({'directory':str(output),'assembly_destination':str(target),
                      'files':{name:R.desc(body) for name,body in bodies.items()},'sender_started':False}))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError):
        sys.stderr.write('ROOT_RECIPIENT_INPUT_ISSUANCE_REFUSED\n')
        raise SystemExit(1)
