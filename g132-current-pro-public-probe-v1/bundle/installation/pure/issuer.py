# Exact bounded source projection; source module is never imported.
HOST_COMMIT = '3f6003cce29d077ad66497c30788a38af081976b'

HOST_TREE = 'bc3f8f1a10cbea041a6bf066acda113f3252360b'

def require(ok, code):
    if not ok:
        raise ValueError(code)

def publication_join(R, source, raw, ctx):
    """Join the same three Root-received GitHub bodies used at launch."""
    v = R.parse(raw, R.MAX_RESULT)
    ref, commit, run = v['ref'], v['commit'], v['run']
    require(ref['ref'] == 'refs/heads/'+ctx['branch'] and ref['object']['type'] == 'commit'
            and ref['object']['sha'] == commit['sha'] == run['head_sha'] == HOST_COMMIT,
            'PUBLICATION_HEAD_CHANGED')
    require(commit['tree']['sha'] == HOST_TREE and source.host_commit(commit) == HOST_COMMIT,
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
    common = dict(successor='PRO-EXECUTOR-01, designated by owner', source_commit=source.P.SOURCE_COMMIT, source_tree=source.P.SOURCE_TREE,
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
    admission = dict(schema='dg16.pro-private-sender-root-admission.v1', issuer='R5_ROOT_GOVERNOR', successor='PRO-EXECUTOR-01, designated by owner',
                     operation_sha256=R.sha(R.encode(op)), capture_profile=composition['capture_profile'],
                     provider_profile=source.B.PROFILE, source_commit=source.P.SOURCE_COMMIT,
                     source_tree=source.P.SOURCE_TREE, carrier_binding_sha256=common['carrier_binding_sha256'],
                     limits=source.binding['limits'], one_encryption=True, metadata_reads=18,
                     automatic_retry=False, host_or_native_effect_grant=False, original_awards=[])
    return {'ROOT_SENDER_ASSEMBLY_SELECTION.json': R.encode(selected), 'PRO_SENDER_OPERATION.json': R.encode(op),
            'PRO_SENDER_ADMISSION.json': R.encode(admission), 'ROOT_REQUEST_ARTIFACT.zip': archive,
            'HOST_PUBLICATION_ROOT_RECEIVING.json': publication}
