#!/usr/bin/env python3
"""Receive retained public M5 bytes; no network, route, controller, or product execution."""
import datetime
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import zipfile

BASE = Path('/workspace/scratch/0269e6626329')
RETAINED = BASE / 'dg16/.IMPLEMENTAUDIT/current-source-ci/m5'
OBSERVATION = BASE / 'm5-hosted-observation-43686188100'
REVIEW = BASE / 'm5-review'
REPO = BASE / 'm5-source'
OUT = BASE / 'm5-hosted-receiving'
HEAD = 'c073689e315b4db7c26e5a95c9024a34b1e560b7'
TREE = '8d5502db6ea1f303f6345ded74cf1a0ae1dd3e94'
SOURCE = '205aeab7c93299b0666b261485ab5658d8e183de'
SOURCE_TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
SOURCE_MANIFEST = 'e912e90f2a8c3e40a93e0f1381dc7ecb387b1685106b1a1f31c0fd50d66c4743'
BRANCH = 'engineering/pro-executor-dg16-m5-source-20261115'
ARCHIVE_SHA = '897340c804241024f7be059adf0df717279d642add529c08eaa1b7851e5f3594'
NAMES = {'RESULT.json', 'HOST.json', 'SOURCE.json', 'PACKAGES.json', 'ROUTES.json',
         'PHASES.json', 'FAILURE.json', 'CLEANUP.json', 'ARTIFACT_MANIFEST.json'}
ROUTES = ['plugin-codex', 'plugin-claude', 'standalone-codex', 'standalone-claude']
PHASES = ['prepare', 'initialize', 'read-state', 'read-roadmap', 'resume', 'build', 'install',
          'qualify-plugin-codex', 'receive-plugin-codex', 'qualify-plugin-claude', 'receive-plugin-claude',
          'qualify-standalone-codex', 'receive-standalone-codex', 'qualify-standalone-claude',
          'receive-standalone-claude', 'finalize']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def parse(data):
    def refused(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=refused)


def load(path):
    return parse(path.read_bytes())


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def desc(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': sha(data), 'mode': oct(stat.S_IMODE(path.stat().st_mode))}


def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(REPO), *args],
                                   env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}).decode().strip()


def valid_hash(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    metadata = load(OBSERVATION / 'METADATA_REPORT.json')
    assert metadata['run']['id'] == 43686188100 and metadata['run']['attempt'] == 1
    assert metadata['run']['event'] == 'push' and metadata['run']['head_sha'] == HEAD
    assert metadata['run']['tree'] == TREE and metadata['run']['head_branch'] == BRANCH
    assert metadata['run']['conclusion'] == metadata['job']['conclusion'] == 'success'
    assert metadata['job']['id'] == 132727043728 and len(metadata['job']['steps']) == 24
    assert all(row['conclusion'] == 'success' and row['status'] == 'completed' for row in metadata['job']['steps'])
    catalog = load(RETAINED.parent / 'm5-artifacts.json')
    assert catalog['total_count'] == len(catalog['artifacts']) == 1
    artifact = catalog['artifacts'][0]
    for key in ('id', 'name', 'size_in_bytes', 'digest', 'expired', 'created_at', 'expires_at'):
        assert artifact[key] == metadata['artifact'][key]
    assert artifact['id'] == 14151065080 and artifact['workflow_run']['head_sha'] == HEAD
    assert artifact['workflow_run']['id'] == 43686188100 and artifact['expired'] is False
    intent = load(RETAINED / 'ACQUISITION_INTENT.json')
    receipt = load(RETAINED / 'ACQUISITION_RECEIPT.json')
    body_intent = load(RETAINED / 'BODY_READ_INTENT.json')
    reference = load(RETAINED / 'DOWNLOAD_REFERENCE_DESCRIPTOR.json')
    assert intent['artifact'] == artifact and intent['body_get_limit'] == 1 and intent['automatic_retry'] is False
    assert receipt['body_gets'] == body_intent['body_gets'] == 1
    assert receipt['automatic_retry'] is body_intent['automatic_retry'] is False
    assert receipt['artifact_id'] == reference['artifact_id'] == artifact['id']
    assert receipt['run_id'] == 43686188100 and receipt['head_sha'] == HEAD
    assert reference['signed_url_retained'] is receipt['signed_url_retained'] is False
    archive = (RETAINED / 'artifact.zip').read_bytes()
    assert len(archive) == artifact['size_in_bytes'] == receipt['archive']['bytes'] == 6847
    assert sha(archive) == receipt['archive']['sha256'] == ARCHIVE_SHA
    assert artifact['digest'] == 'sha256:' + ARCHIVE_SHA
    members = {}
    documents = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        infos = zipped.infolist()
        assert len(infos) == 9 and {info.filename for info in infos} == NAMES
        assert len({info.filename for info in infos}) == len(infos)
        for info in infos:
            name = PurePosixPath(info.filename)
            assert len(name.parts) == 1 and not name.is_absolute() and not info.is_dir()
            assert not info.flag_bits & 1 and not stat.S_ISLNK(info.external_attr >> 16)
            assert 0 <= info.file_size <= 65536
            data = zipped.read(info)
            assert data == (RETAINED / 'members' / info.filename).read_bytes()
            members[info.filename] = data
            documents[info.filename] = parse(data)
            assert canonical(documents[info.filename]) == data
    assert sum(map(len, members.values())) == 17149 <= 262144
    actual_members = [{'path': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in members.items()]
    assert {r['path']: r for r in actual_members} == {r['path']: r for r in receipt['members']}
    public_manifest = documents['ARTIFACT_MANIFEST.json']
    assert public_manifest['schema'] == 'dg16.installed-runtime-artifact-manifest.v1'
    assert public_manifest['authority'] == 'NONE' and public_manifest['private_outputs_included'] is False
    expected = [{'name': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in sorted(members.items())
                if name != 'ARTIFACT_MANIFEST.json']
    assert public_manifest['files'] == expected

    # Bind the exact published tree to local integration and all 65 reviewed
    # candidate files; only review/root-integration records may be additive.
    assert git('rev-parse', 'HEAD') == '689e39feb0665e0be8222e91117b1434654b50e7'
    assert git('show', '-s', '--format=%T', 'HEAD') == TREE
    assert git('status', '--porcelain', '--untracked-files=all') == ''
    source_packet_file = REPO / 'handoff/dg16-m5-source-20261115/SOURCE_PACKET_MANIFEST.json'
    assert sha(source_packet_file.read_bytes()) == '1068764f35a15d9610e8cf01dda9ea85861546e33da844d17839aac39a40a75c'
    for row in load(source_packet_file)['members']:
        data = (REPO / row['path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    delta = [line.split('\t') for line in git('diff', '--name-status', '21c53ac61f6db57f0bb8ddfdabeb254420e109c2', 'HEAD').splitlines()]
    assert len(delta) == 27 and all(row[0] == 'A' for row in delta)

    result, host, source = (documents[n] for n in ('RESULT.json', 'HOST.json', 'SOURCE.json'))
    packages, routes, phases = (documents[n] for n in ('PACKAGES.json', 'ROUTES.json', 'PHASES.json'))
    failures, cleanup = (documents[n] for n in ('FAILURE.json', 'CLEANUP.json'))
    for name, schema in [('RESULT.json','result'),('HOST.json','host'),('SOURCE.json','source'),
                         ('PACKAGES.json','packages'),('ROUTES.json','routes'),('PHASES.json','phases'),
                         ('FAILURE.json','failure'),('CLEANUP.json','cleanup')]:
        assert documents[name]['schema'] == 'dg16.installed-runtime-' + schema + '.v1'
    assert result['status'] == 'PASS' and result['authority'] == 'NONE'
    assert result['repository'] == 'theislampill/IMPLEMENTAUDIT.md' and result['branch'] == BRANCH
    assert result['run_id'] == '43686188100' and result['attempt'] == 1 and result['workflow_commit'] == HEAD
    assert result['source_commit'] == source['commit'] == packages['source']['commit'] == SOURCE
    assert result['source_tree'] == source['tree'] == packages['source']['tree'] == SOURCE_TREE
    assert result['source_manifest_sha256'] == source['manifest_sha256'] == SOURCE_MANIFEST
    assert source['file_count'] == 1766 and source['total_bytes'] == 167023692
    for key in ('before_complete','after_complete','source_unchanged','parent_runtime_unchanged'):
        assert source[key] is True
    assert source['tracked_product_mutations_authorized'] is False
    assert result['runtime_version'] == '0.4.0' and result['release_family'] == 'v0.4.0.0' and result['budget_revision'] == 4
    assert result['scope'] == 'FOUR_LINUX_ISOLATED_INSTALLED_INITIALIZATION_AND_FIRST_NORMAL_CONTINUITY_CHAINS'
    assert result['mechanical_independence'] == 'DISTINCT_SAME_SUBJECT_PROCESS_ONLY'
    for key in ('original_acceptance','native_application_discovery','windows','whole_cell_claim','public_release',
                'audit_closure','governed_phase_completion_claimed','automatic_retry','performance_threshold_claimed',
                'canonical_registry_claim'):
        assert result[key] is False
    assert result['parent_final_currentness'] is True and result['installed_routes_received'] == 4
    assert result['watchdog_seconds'] == 2400 and result['finalization_reserve_seconds'] == 180
    assert type(result['elapsed_seconds']) in (int,float) and math.isfinite(result['elapsed_seconds'])
    assert 0 <= result['elapsed_seconds'] <= 2400 and result['elapsed_subtraction'] == 0
    assert result['checkout_and_artifact_transport_outside_interval'] is True
    assert result['command_count'] == 225 and result['captured_bytes'] == 121739 <= 16*1024*1024
    assert valid_hash(result['private_command_ledger_sha256'])

    observation = host['observation']
    assert observation['os'] == {'ID':'ubuntu','VERSION_ID':'26.04'}
    assert observation['architecture'] == 'x86_64' and observation['python_version'] == [3,14,4]
    assert type(observation['uid']) is int and observation['uid'] == 1001
    assert observation['image_os'] == 'ubuntu26' and observation['image_version'] == '20261111.196.1'
    assert valid_hash(observation['boot_identity_sha256'])
    assert set(observation['tools']) == {'bash','python3','git','env'}
    for row in observation['tools'].values():
        assert row['root_owned_nonwritable_chain'] is True and row['setid_or_file_capabilities'] is False
        assert valid_hash(row['sha256']) and row['bytes'] > 0 and row['canonical'].startswith('/usr/')
    assert observation['tools']['python3']['canonical'] == '/usr/bin/python3.14'
    assert host['toolchain_bookends_equal'] is True and host['venv']['closing_manifest_equal'] is True
    assert host['setup']['status'] == 'COMPLETED' and host['setup']['zopfli_version'] == '0.2.3.post1'
    assert host['setup']['uid'] == 0 and host['setup']['mode'] == 0o4755
    assert host['setup']['watchdog_seconds'] == 600 and 0 <= host['setup']['elapsed_seconds'] <= 600

    assert packages['build_command_reservations'] == 1 and packages['build_started_observed'] is True
    assert packages['build_completion_unknown'] is False and packages['packages_unchanged'] is True
    assert packages['all_installed_populations_unchanged'] is True and packages['native_discovery_claimed'] is False
    package_map = {row['role']: row for row in packages['artifacts']}
    assert len(packages['artifacts']) == 2 and set(package_map) == {'canonical_plugin','standalone_compatibility'}
    fixture_dir = REPO / 'handoff/dg16-m5-source-20261115/validation/new-package-fixture-build/artifacts'
    parity = []
    for role, row in package_map.items():
        data = (fixture_dir / row['name']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert row['cap_bytes'] == 589824 and row['reserve_bytes'] == 2000 and row['bytes'] <= 587824
        assert row['complete_inventory_and_source_parity'] is True
        payload = {}
        with zipfile.ZipFile(io.BytesIO(data)) as zipped:
            for info in zipped.infolist():
                raw = zipped.read(info)
                payload[info.filename] = {'bytes':len(raw),'sha256':sha(raw),'mode':stat.S_IMODE(info.external_attr >> 16)}
            inventory = parse(zipped.read('IMPLEMENTAUDIT_INVENTORY.json'))
            assert inventory['source'] == {'commit':SOURCE,'tree':SOURCE_TREE,'worktree_state':'clean'}
            assert inventory['artifact_role'] == role
        assert sha(canonical(payload)) == row['member_bytes_modes_sha256']
        assert len(payload) == row['members'] == (75 if role == 'canonical_plugin' else 72)
        assert sum(x['bytes'] for x in payload.values()) == row['expanded_bytes']
        assert len(inventory['members']) == row['inventory_members'] == len(payload)-1
        parity.append({'role':role,'name':row['name'],'bytes':len(data),'sha256':sha(data),
                       'member_manifest_sha256':sha(canonical(payload)),
                       'remaining_after_reserve_bytes':587824-len(data),
                       'relation':'Actual hosted public package identity equals independently read new local fixture bytes; no hosted private package body acquired.'})

    assert routes['authority'] == 'NONE' and [r['route'] for r in routes['routes']] == ROUTES
    true_keys = ('first_normal_resume_verified','distinct_receiver_process','refs_objects_receipt_documents_received',
                 'receiver_final_currentness','closing_currentness','closing_refs_and_documents_unchanged')
    for row in routes['routes']:
        role = 'canonical_plugin' if row['route'].startswith('plugin-') else 'standalone_compatibility'
        assert row['status'] == 'RECEIVED' and all(row[key] is True for key in true_keys)
        assert row['installed_manifest_sha256'] == package_map[role]['member_bytes_modes_sha256']
        assert row['installed_members'] == package_map[role]['members']
        assert row['authority_ref_count'] == 4 and row['document_count'] == 10
        assert row['governed_phase_completion_claimed'] is False
        assert all(valid_hash(row[key]) for key in ('receipt_body_sha256','readback_request_sha256',
                   'authority_objects_manifest_sha256','document_population_sha256'))
    assert len({r['receipt_body_sha256'] for r in routes['routes']}) == 4
    assert [r['stage'] for r in phases['phases']] == PHASES
    assert all(r['status']=='COMPLETED' and r['own_children_reaped'] is True for r in phases['phases'])
    assert sum(r['command_count'] for r in phases['phases']) == result['command_count']
    assert all(type(r['elapsed_seconds']) in (int,float) and math.isfinite(r['elapsed_seconds'])
               and r['elapsed_seconds'] >= 0 for r in phases['phases'])
    phase_sum = sum(r['elapsed_seconds'] for r in phases['phases'])
    assert phase_sum <= result['elapsed_seconds']
    assert phases['memory_acceptance_threshold_claimed'] is False
    assert failures['present'] is False and failures['failed_commands'] == failures['failures'] == []
    assert failures['raw_diagnostics_private'] is True
    for key in ('all_recorded_step_children_reaped','final_bookends_complete','parent_final_currentness'):
        assert cleanup[key] is True
    for key in ('unknown_pending_command','unknown_pending_step','private_outputs_uploaded','original_acceptance'):
        assert cleanup[key] is False

    # Retain byte-identical evidence copies after all checks; no network request.
    for name in ('evidence','metadata','custody'):
        (OUT/name).mkdir(exist_ok=False)
    (OUT/'evidence/artifact.zip').write_bytes(archive)
    for name, data in members.items():
        (OUT/'evidence'/name).write_bytes(data)
    for path in OBSERVATION.glob('*.json'):
        shutil.copyfile(path, OUT/'metadata'/path.name)
    for name in ('ACQUISITION_INTENT.json','ACQUISITION_RECEIPT.json','BODY_READ_INTENT.json','DOWNLOAD_REFERENCE_DESCRIPTOR.json'):
        shutil.copyfile(RETAINED/name, OUT/'custody'/name)
    shutil.copyfile(RETAINED.parent/'m5-artifacts.json', OUT/'custody/ARTIFACT_CATALOG.json')
    received = {'schema':'dg16.m5-distinct-actual-hosted-receiving.v1','receiver':'/root/dg18_engineering',
        'disposition':'RECEIVED_CURRENT_SOURCE_FOUR_ROUTE_HOSTED_QUALIFICATION','authority':'NONE',
        'started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'run':metadata['run'],'job_id':132727043728,'all_recorded_job_steps_successful':24,
        'artifact':artifact,'archive':{'bytes':6847,'sha256':ARCHIVE_SHA},'public_members':actual_members,
        'public_member_count':9,'public_uncompressed_bytes':17149,'public_manifest_verified':True,
        'reviewed_source_commit':'21c53ac61f6db57f0bb8ddfdabeb254420e109c2',
        'published_tree_binding':{'remote_commit':HEAD,'local_integration_commit':'689e39feb0665e0be8222e91117b1434654b50e7',
                                  'equal_tree':TREE,'reviewed_65_files_unchanged':True,'added_review_and_integration_files':27},
        'result':result,'host':host,'source':source,'packages':packages,'fixture_identity_join':parity,
        'routes':routes,'phases':phases,'failure':failures,'cleanup':cleanup,
        'timing':{'actual_interval_seconds':result['elapsed_seconds'],'sum_of_recorded_phase_seconds':phase_sum,
                  'checkout_and_artifact_transport_outside_interval':True,'elapsed_subtraction':0,
                  'performance_threshold_claimed':False},
        'acquisition':{'root_body_gets':1,'receiver_body_gets':0,'receiver_job_log_acquisitions':0,
                       'artifact_reacquired':False,'signed_url_retained':False},
        'mechanical_independence':'DISTINCT_SAME_SUBJECT_PROCESS_ONLY; distinct external source reviewer now receives public result',
        'first_failed_predicate':None,'source_controller_or_remote_mutation_by_receiver':False,
        'historical_raw_packet_recovered':False,'old_27_controls_rerun':False,
        'original_M5_remaining':['Exact canonical G221 package/source identity join','Applicable M6/original receiving'],
        'original_M5_Q04_Q05_G221_M6_native_Windows_release_closure_acceptance':False}
    (OUT/'RECEIVING.json').write_bytes(canonical(received))
    assert (RETAINED/'artifact.zip').read_bytes() == archive
    assert git('status','--porcelain','--untracked-files=all') == ''
    print(json.dumps({'disposition':received['disposition'],'public_files':9,'uncompressed_bytes':17149,
        'elapsed_seconds':result['elapsed_seconds'],'phase_sum_seconds':phase_sum,'routes':4,
        'root_body_gets':1,'receiver_body_gets':0,'receiving_json_sha256':sha((OUT/'RECEIVING.json').read_bytes())},indent=2))


if __name__ == '__main__':
    main()
