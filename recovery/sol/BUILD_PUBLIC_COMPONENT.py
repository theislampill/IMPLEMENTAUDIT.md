"""Explicit public allowlist packaging only. No engineering, provider or test call."""
from pathlib import Path
import ast, copy, hashlib, json

WORK=Path('C:/workspace/ai/improveimplementaudit')
OUT=WORK/'plans/dg16-pro-handoff-20261109/staging/sol'
BASE=WORK/'plans/sol-dg16-staged-execution-20261108'
G1=BASE/'g1-current03-recovered'
G2=BASE/'g2-production-qualification'
ROOT=WORK/'plans/astra-successor-reconciliation-20261108'
PREFIX='recovery/sol/'
index=[];objects={}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,ensure_ascii=True)+'\n').encode()
def read(path):
    before=path.stat();raw=path.read_bytes();after=path.stat()
    assert (before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert len(raw)==before.st_size and not path.is_symlink()
    return raw

def object_bytes(logical,raw,category,origin,extension):
    digest=sha(raw);suffix=extension if extension in {'.py','.js','.sh','.json','.md','.yml','.txt'} else '.bin'
    target=Path('objects')/(digest+suffix)
    if digest in objects:target=Path(objects[digest])
    else:
        (OUT/target).parent.mkdir(exist_ok=True)
        with (OUT/target).open('xb') as f:f.write(raw)
        assert read(OUT/target)==raw
        objects[digest]=target.as_posix()
    index.append(dict(logical_path=logical,archive_path=PREFIX+target.as_posix(),bytes=len(raw),sha256=digest,
                      category=category,origin=origin,authority='REFERENCE_BYTES_ONLY_NO_EFFECT_GRANT'))

def add(logical,path,category='PUBLIC_SOURCE'):
    raw=read(path);object_bytes(logical,raw,category,str(path.relative_to(WORK)),path.suffix)

def add_json(logical,value,category='DERIVED_PUBLIC_PROJECTION'):
    object_bytes(logical,encoded(value),category,'Allowlisted projection of retained public structured receipt', '.json')

# Complete public generator code/static templates. Actual role bodies are NOT here.
for path in sorted((G1/'received/source').rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:continue
    relative=path.relative_to(G1/'received/source')
    assert relative.parts[0] in {'author','templates','inputs'}
    if relative.parts[0]=='inputs':assert relative.as_posix()=='inputs/TEMPLATE_INDEX.json'
    add('g1/generator/source/'+relative.as_posix(),path)
for name in ['prepare_current04.py','phase_current04.py','check_current05_fetch.py','CURRENT05_FETCH_RED.json']:
    add('g1/current05-wip/'+name,G1/name,'HISTORICAL_PRODUCER_OR_PARTIAL_SOURCE_CONTROL')
add('g1/current05-wip/base-run-b4c9013c.py',ROOT/'g1-current04-issuer/original-host-01/root-lock-and-currentness/run.py')
add('g1/current05-wip/operation-v2.py',G1/'original-host-failure-01/candidate-v2/operation.py')
add('g1/current05-wip/SELECTION.json',ROOT/'g1-current05-issuer/SELECTION.json','PUBLIC_SELECTION_METADATA')
add('g1/current05-wip/ROOT_CORE_ROLES_INDEX.json',ROOT/'g1-current05-issuer/ROOT_CORE_ROLES.json','PUBLIC_INDEX_NOT_ROLE_BODIES')
add('g1/current05-wip/PRE_CANDIDATE_INTERFACES.json',G1/'current05-review/PRE_CANDIDATE_INTERFACES.json','PUBLIC_REVIEW_RECEIPT')

late=G1/'current04-late-sender'
selected={
 'g1/operator/windows_role_io.js':late/'windows_role_io.js',
 'g1/operator/provider_slots.js':late/'provider_slots.js',
 'g1/operator/role_process_v4.py':late/'framed-operator/role_process_v4.py',
 'g1/operator/control_process_v3.py':late/'control-driver/control_process_v3.py',
 'g1/operator/control_process_v5.py':late/'root-readback/control/control_process_v5.py',
 'g1/operator/control_readback.py':late/'root-readback/control/control_readback.py',
 'g1/operator/control_callback_v6.js':late/'root-readback/control/control_callback_v6.js',
 'g1/operator/file_readback.py':late/'root-readback/file_readback.py',
 'g1/operator/binary_publish_v3.py':late/'root-readback/binary/binary_publish_v3.py',
 'g1/operator/binary_driver_v3.js':late/'root-readback/binary/binary_driver_v3.js',
 'g1/operator/root_sha256_utf8.js':late/'binary-publication/root_sha256_utf8.js',
 'g1/operator/root_pipeline_inputs_v2.py':late/'root-orchestration/root_pipeline_inputs_v2.py',
 'g1/late-assembly/assemble_actual.py':late/'assemble_actual.py',
 'g1/late-assembly/late_sender_current04_v2.py':late/'late_sender_current04_v2.py',
 'g1/late-assembly/AUTHOR_SOURCE_INDEX.json':late/'source-stage-01/AUTHOR_SOURCE_INDEX.json',
 'g2/operator/newcandidate-v2.py':G2/'public-operator-source/newcandidate-v2.py',
 'g2/operator/root_operator.py':G2/'public-operator-source/operational/root_operator.py',
 'g2/operator/concrete_root_bridge.py':G2/'public-operator-source/operational/concrete_root_bridge.py',
 'g2/discriminator/pair_driver_noio_v2.py':G2/'original-host-diagnostic-01/candidate-status-discriminator/pair_driver_noio_v2.py',
}
for logical,path in selected.items():add(logical,path,'FROZEN_PUBLIC_OPERATOR_SOURCE_HISTORICAL_BINDINGS_REQUIRE_FRESH_CUSTODY')

# Complete indexed public late-assembly support, excluding every private packet.
stage=late/'source-stage-01';author_index=json.loads(read(stage/'AUTHOR_SOURCE_INDEX.json'))['members']
for name,pin in author_index.items():
    path=stage/'source-support'/name;raw=read(path)
    assert dict(bytes=len(raw),sha256=sha(raw))==pin
    add('g1/late-assembly/stage/source-support/'+name,path)
add('g1/late-assembly/stage/source-support/root_tool_broker.py',stage/'source-support/root_tool_broker.py')

# Public receiver algorithms and unresolved static templates; actual Root role
# bodies, installation receipts/configuration/admissions are deliberately omitted.
for path in sorted((G2/'actual-host-source-01/receiver').iterdir()):
    if path.is_file() and (path.suffix=='.py' or path.name.endswith('_TEMPLATE.json')):
        add('g2/receiver-source/'+path.name,path)
for path in sorted((G2/'final-public-binding-01').glob('*.py')):
    add('g2/bound-public-receiver-source/'+path.name,path)

reviews={
 'g1/reviews/control-author-successor.json':late/'root-readback/control/SUCCESSOR_FINAL.json',
 'g1/reviews/control-independent.json':late/'root-readback/control/PARENT_SUCCESSOR_RECEIVING.json',
 'g1/reviews/control-retained-revise.json':late/'root-readback/control/REVISE_RECEIVING.json',
 'g1/reviews/decoder-independent.json':late/'root-readback/PARENT_DECODER_RECEIVING.json',
 'g1/reviews/binary-independent.json':late/'root-readback/binary/independent-review/FINAL.json',
 'g1/reviews/binary-final-delta-independent.json':late/'root-readback/binary/independent-review-v3/FINAL.json',
 'g1/reviews/original04-public-terminal-independent.json':G1/'original-host-failure-01/independent-receiving/RECEIVING.json',
 'g1/reviews/lock-owner-analysis.json':G1/'original-host-failure-01/lock-owner-analysis/FINAL.json',
 'g1/reviews/diagnostic-independent-successor.json':G1/'original-host-failure-01/independent-source-review/SUCCESSOR_RECEIVING.json',
 'g1/reviews/diagnostic-initial-revise.json':G1/'original-host-failure-01/independent-source-review/FINAL.json',
 'g2/reviews/operator-independent.json':G2/'public-operator-source/v2-independent-review/FINAL.json',
 'g2/reviews/concrete-bridge-independent.json':G2/'public-operator-source/operational/concrete-independent-review/FINAL.json',
 'g2/reviews/first-terminal-independent.json':G2/'original-host-diagnostic-01/independent-terminal-receiving/RECEIPT.json',
 'g2/evidence/FIRST_OUTCOME_DISPOSITION.json':G2/'original-host-diagnostic-01/FIRST_OUTCOME_DISPOSITION.json',
 'g2/evidence/LEGACY_SUCCESSOR_SOURCE_SCOPE.json':G2/'original-host-diagnostic-01/LEGACY_SUCCESSOR_SOURCE_SCOPE.json',
}
for logical,path in reviews.items():add(logical,path,'PUBLIC_SCOPED_RECEIPT_NOT_RAW_LOG_OR_TOOL_HISTORY')
fixture=G1/'git256-package-probe-01'
for name in ['package_probe.py','tiny_git_probe.py','tiny_git_probe_v2.py','public_repo_probe.py','public_repo_probe_v2.py']:
    add('git-fixture/source/'+name,fixture/name)
for logical,name in [
 ('tiny-source-revise','independent-review/FINAL.json'),
 ('tiny-source-successor','independent-review/SUCCESSOR_RECEIVING.json'),
 ('tiny-actual-independent','independent-actual-receiving/RECEIVING.json'),
 ('public-source-revise','independent-public-source-review/FINAL.json'),
 ('public-source-successor','independent-public-source-review/SUCCESSOR_RECEIVING.json'),
 ('public-actual-independent','independent-public-actual-receiving/RECEIVING.json')]:
    add('git-fixture/reviews/'+logical+'.json',fixture/name,'PUBLIC_SCOPED_RECEIPT_NOT_RAW_LOG_OR_TOOL_HISTORY')

# Remove raw command stdout/stderr; retain actual returned-code, arguments,
# stream descriptors, namespace and owned-child facts as a labelled projection.
for name in ['TINY_PROBE_RECEIVING.json','PUBLIC_PROBE_RECEIVING.json']:
    raw=read(fixture/name);data=json.loads(raw);projection=copy.deepcopy(data)
    for row in projection.get('commands',[]):
        for field in ('stdout','stderr'):
            text=row.pop(field,None)
            if text is not None:row[field+'_omitted_descriptor']=dict(bytes=len(text.encode()),sha256=sha(text.encode()))
    projection['handoff_projection']=dict(original_receipt_sha256=sha(raw),original_receipt_bytes=len(raw),
        raw_stdout_stderr_omitted=True,no_tool_history_included=True,original_receipt_retained_by_Root=True)
    add_json('git-fixture/evidence/'+name,projection)
package=json.loads(read(fixture/'PACKAGE_RECEIVING.json'))
add_json('git-fixture/evidence/PACKAGE_PUBLIC_PROVENANCE.json',dict(
    ppa=package['ppa'],published_signing_fingerprint=package['published_signing_fingerprint'],
    signature_verified=package['signature_verified'],inrelease_sha256=package['inrelease_sha256'],
    packages_sha256=package['packages_sha256'],package={k:package['package'][k] for k in ['Package','Version','Architecture','Filename','Size','SHA256']},
    executable=package['executable'],version=package['version'],distro_git=package['distro_git'],
    installed=False,original_receipt_sha256=sha(read(fixture/'PACKAGE_RECEIVING.json'))))
add('git-fixture/evidence/FIXTURE_TERMINAL_CUSTODY.json',fixture/'FIXTURE_TERMINAL_CUSTODY.json','PUBLIC_OWNED_RESOURCE_RECEIPT')
add('git-fixture/evidence/PACKAGE_ROUTE_HISTORY.json',fixture/'PACKAGE_ROUTE_HISTORY.json','PUBLIC_SCOPED_HISTORY_SUMMARY_NOT_RAW_LOG')

# Exact private dependency identities are metadata only. No corresponding body
# may be present in this public component's content-addressed objects.
compose=ast.parse(read(G1/'received/source/author/compose.py'))
values={t.id:ast.literal_eval(n.value) for n in compose.body if isinstance(n,ast.Assign)
        for t in n.targets if isinstance(t,ast.Name) and t.id in {'RETAINED','PLACEMENT','ROLES'}}
roles=json.loads(read(ROOT/'g1-current05-issuer/ROOT_CORE_ROLES.json'))
private=[]
for name,pin in (values['RETAINED']|values['PLACEMENT']|roles['roles']).items():
    private.append(dict(logical_role='g1.current05.private-inputs/'+name,**pin,status='BODY_OMITTED',
                        fresh_custody='Root must deliver/receive this exact source role under an explicit successor lease; never synthesize a PASS or reuse a historical effect grant.'))
for name in ['BINDING.json','SUCCESSOR_RUNTIME_BINDING.json','FINAL_REVIEW_SELECTION.json']:
    raw=read(G2/'final-public-binding-01'/name)
    private.append(dict(logical_role='g2.root-received-source-binding/'+name,bytes=len(raw),sha256=sha(raw),status='BODY_OMITTED',
                        fresh_custody='Root-controlled source/configuration receipt; code is public but this packet conveys no historical or fresh Root authority.'))
forbidden={r['sha256'] for r in private}
assert not (forbidden & set(objects)), 'PRIVATE_ROLE_BODY_IN_PUBLIC_COMPONENT'

external=[
 ('g1.root.receiver','378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'),
 ('g1.root.resolve_artifact','b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530'),
 ('g1.root.recipient_issuer','b21469b2ee92a7dd3cf59f09d5e006c6fe143b0b38f1581a588411e748a43053'),
 ('g1.root.bind_dispatcher','d83c761dbc666d78856cf2d52ced4db2b6b8d373742deef4938b2d4b6434938f'),
 ('g1.root.dispatcher_entry','0bde14158b8505b89f6492ee96f8b5e9f42c9c09341da3cc49201efd0dec80b7'),
 ('g1.root.dispatch_js','ed48969832fc789dcc8ed3a238f355c43b3908c82b61ba9f835684c56e1a7c68'),
 ('g2.root.native_history_SOURCE_ONLY','71b4538d41501c017d2282f799dfbd3ad8e3435c9409c40633ed156d18529bd1'),
 ('g2.root.public_receiver_installation_receipt','23fcaf940f2b51d321731d56fbdd217adf032a033a9cdbaca340607d468c5239'),
 ('g2.root.public_receiver_source_seal','2f86492f085eae40ab35530fe1d59773116841c120b5a9bd50421e5bdf02275d'),
 ('root.fetch_countermeasure_receiving','0957ab3a5f31fecf923a64b03570d479d676f5255a5c29ed7bf2c65599fa85d9'),
 ('episodes.g1.original04.public_archive','28ef2877d8d5c42ff5300568cc601074b48378e609275aeea3455ac12fa3dec6'),
 ('episodes.g2.original01.public_archive','6b869e5e7543703e7f70def6119d4f7a7ce1aa0a9868ee7f0d11ba41542d1f31')]
external=[dict(logical_role=role,sha256=digest,status='EXPECTED_ROOT_COMPONENT_SOURCE_OR_PUBLIC_EPISODE',
               archive_component='recovery/episodes' if role.startswith('episodes.') else 'recovery/root-runtime',
               archive_path='Resolve through Root DEPENDENCIES.json by exact SHA; no duplicate bytes supplied here.') for role,digest in external]

documents={
 'SOURCE_INDEX.json':dict(schema='dg16.sol-public-source-index.v1',archive_prefix=PREFIX,members=index,external_public_dependencies=external),
 'PRIVATE_DEPENDENCIES.json':dict(schema='dg16.sol-private-dependency-metadata-only.v1',bodies_included=False,dependencies=private,
    further_fresh_inputs=['Actual current05 carrier and bootstrap SourceRoot decisions','Per-run current tools/recipient/request/source/operation/admission','Actual G3 independent producer and Root initial/final decisions within their original windows','Actual private inputs/key custody and native tool history source/cursor; no raw data or credentials are supplied'],
    rule='Exact metadata identifies a missing dependency, not a grant or independent receiving.'),
 'PUBLIC_GIT_ANCHORS.json':dict(schema='dg16.sol-public-immutable-source-anchors.v1',repository='https://github.com/theislampill/IMPLEMENTAUDIT.md',
    product=dict(commit='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f',tree='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e',
                 url='https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'),
    historical_g1_04=dict(commit='f9ba187e8f5520956f0f16cf13c0a706e8360b96',tree='8390375505282e602759c7976b6bca82a44d5737'),
    historical_g2_01=dict(commit='7f618adc702912f760d87f68fe9c94cc419e844c',tree='27bb6432546c2d0b3fb7df09f0845c3d1303bccd'),
    scope='Previously Root-received public immutable references; no network/provider verification performed for packaging. Public product dependencies resolve at exact commit/path; never substitute default branch.'),
 'CURRENT_CHECKPOINT.json':dict(schema='dg16.sol-owner-stop-checkpoint.v1',state='SOURCE_ENGINEERING_STOPPED_BY_OWNER; PUBLIC_HANDOFF_ONLY',
    actual_current05_point=dict(functional_fetch_patch_written=False,current05_inputs_written=False,prepare_executed=False,bind_carrier_executed=False,finish_executed=False,
        produced_current05_commit=None,reviewed_current05_candidate=None,
        partial_public_files=['check_current05_fetch.py','CURRENT05_FETCH_RED.json','PRE_CANDIDATE_INTERFACES.json'],
        verified_source_bases=dict(run_sha256='b4c9013c0c665df6c2e66c609f93d5a08c2e12905a7663d3d144419b64b69865',operation_sha256='0c67470c1138f7e200a5d7e9c8e4cedfe3c56d6dc8ae86f123fdeeadd32cdc43'),
        selection_sha256='aac7a08587e5fb5151345730d0a001228676c09652adb2ade27eddc866636e65',core_role_index_sha256='816b7bfe544cff1edb83540919e91b7409df8792fdc28a50a186896c8fa379af',
        intended_unperformed_change='Command-local -c maintenance.autoDetach=false only on hosted source-preparation fetch; retain ordinary detach and Root finalizer cwd fix. No mutation, generator run or further check occurred after owner stop.'),
    actual_g1_04=dict(run=42596136449,job=129089113853,attempt=1,status='UNQUALIFIED_BEFORE_PRODUCER',
        namespace='Exact52B namespace refusal; ATTRIBUTED PROVIDER,2272 names,one lock,others0,flags0',
        historical_lock_name_owner='UNPROVEN',original_pair='NOT_STARTED',G3='SKIPPED',final_currentness='REFUSED; Root separately repaired prospective finalizer cwd source'),
    actual_g2_01=dict(run=42579780645,job=129035519895,attempt=1,status='FAILED',legacy_nodes=119,legacy_tests=91,legacy_node_status='UNSETTLED',
        causal_scope='Legacy verifier returned1; stale artifact-capture phase did not prove collector bug; inner cause UNKNOWN.',
        diagnostic='No-I/O LEGACY_EXIT_STATUS successor88afb accepted at diagnostic source scope only; no complete native repair claimed.'),
    scope_ceiling='Current core/L04-separate G3 contract cannot accept R35-L04 inside this episode or whole G3 from its own rows. Separate applicable Root receiving/composition remains Root-owned; this is not a retraction of an external accepted receipt.',
    root_authority='Astra retains source integration, sole PR255/publication and DAG acceptance. The human will launch one Pro successor; no Pro delivery/receipt, new source lease, native custody or effect authority is asserted.',
    whole_cell_or_issue_awards=[]),
 'RESOURCE_CUSTODY.json':dict(schema='dg16.sol-resource-stop-custody.v1',Sol_native_chat='01a1953f-c449-72b0-9514-333b090b6dce',Root_native_chat='01a1953f-a15b-7811-aa72-3538ebb03562',
    actors=[dict(name='/root/dg16_g1_design_review_20261108',actual_turn_state='COMPLETED; HOLD instructed; no process/effect'),
            dict(name='/root/dg16_g2_diagnostic_review_20261108',actual_turn_state='COMPLETED; HOLD instructed; no process/effect'),
            dict(name='/root/dg16_post_compaction_recovery',actual_turn_state='COMPLETED LOAD-only; USE/JOIN held; HOLD instructed; no process/effect')],
    owned_live_processes=0,owned_live_protected_effects=0,
    retained_fixtures=[dict(path='/home/agent/sol-git256-package-probe-20261109-01',state='Public package/tiny repositories retained; process terminal,ECHILD; private public-key-only GPG agent shut down/no-agent readback'),
        dict(path='/home/agent/sol-git256-public-clone-20261109-01',state='Public dataset/baseline/foreground retained; terminal ECHILD. Default maintenance.lock deliberately retained as evidence; not an admissible clean input; do not remove it.')],
    leases=dict(source_engineering='STOPPED/FROZEN by owner',packaging='Only staging/sol; ends after contribution',
        tiny_fixture='CONSUMED:13 ordinary commands; no lock; signal attempt/reaped0 correction retained; no foreground control',
        dataset_fixture='CONSUMED:one network clone,six commands including conditional foreground fetch/detach; no repeated full campaign',
        current05_source='PREEMPTED before functional patch or generator execution',current05_hosted_native_publication='NOT_GRANTED_OR_CONSUMED_BY_SOL',
        future='Human start and fresh exact Root custody/leases/approvals required; this component transfers no live authority'),
    formal_recovery='No qualified audit-state USE/RETURN/JOIN or pending consumption is asserted. Native currentness/epoch/owner observation remain fresh receiving obligations, not reconstructed from this packet.')
}
for name,value in documents.items():
    with (OUT/name).open('xb') as f:f.write(encoded(value))
print(json.dumps(dict(logical_members=len(index),unique_objects=len(objects),object_bytes=sum((OUT/p).stat().st_size for p in objects.values()),private_dependency_bodies=0,external_public_roles=len(external))))
