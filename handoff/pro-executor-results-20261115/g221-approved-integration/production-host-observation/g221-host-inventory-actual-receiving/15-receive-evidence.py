#!/usr/bin/env python3
"""Receive one already captured public observation; no provider or host operations."""
from pathlib import Path
import base64
from datetime import datetime
import hashlib
import json
import re
import subprocess
import types

HERE = Path(__file__).absolute().parent
REPO = Path('/workspace/scratch/0269e6626329/g221-host-inventory')
BASE = '060902121a45b180853e630891caa5e6c9d2f704'
CANDIDATE = 'cd1a84fbcb39650864c4b8460309025424e2d565'
CARRIER = 'b49d09fb42f1a3e4b7bec6fed3894d5d7c13698b'
REMOTE = 'e08007f7ebefa5e27a0a264b2f7630dee4e7cba4'
TREE = '8aa5f85404c894a1ecc556ecedac8ad40986e293'
BRANCH = 'engineering/pro-executor-g221-host-inventory-20261115'
RUN = 43694426207
JOB = 132751711186
ARTIFACT = 14153163002
OWNER = 'qualification/dg16-r5-full-g2/'
EVIDENCE = 'qualification/dg16-g221-host-inventory/source-evidence/'
WORKFLOW = '.github/workflows/dg16-g221-host-inventory.yml'
OBSERVER = 'qualification/dg16-g221-host-inventory/observe.py'
REVIEW_SHA = 'a2f3398867557db71c35d6ce503f9a7768efa60b858d81615486c68e8fef89f2'
CHECKS = []
COMMANDS = []


def require(ok, predicate):
    CHECKS.append({'predicate': predicate, 'passed': bool(ok)})
    if not ok:
        raise ValueError(predicate)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_object(kind, raw):
    return hashlib.sha1(kind.encode('ascii') + b' ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw), 'git_blob': git_object('blob', raw)}


def git(*args):
    proc = subprocess.run(['git', '--no-optional-locks', *args], cwd=REPO, capture_output=True, check=False)
    COMMANDS.append({'argv': proc.args, 'returncode': proc.returncode,
                     'stdout_bytes': len(proc.stdout), 'stdout_sha256': sha(proc.stdout),
                     'stderr_bytes': len(proc.stderr), 'stderr_sha256': sha(proc.stderr)})
    if proc.returncode:
        raise ValueError('LOCAL_GIT_READ_FAILED')
    return proc.stdout


def read_json(name):
    return json.loads((HERE / name).read_bytes())


def write_once(name, raw):
    with (HERE / name).open('xb') as stream:
        stream.write(raw)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def main():
    run = read_json('03-run.raw.json')
    remote_commit = read_json('04-git-commit.raw.json')
    ref = read_json('05-ref.raw.json')
    jobs = read_json('09-jobs-full.raw.json')
    remote_tree = read_json('10-tree.raw.json')
    raw_artifacts = read_json('14-artifacts-full-tool-result.json')['result']['structuredContent']['content'].encode('utf-8')
    write_once('14-artifacts-full.raw.json', raw_artifacts)
    artifacts = json.loads(raw_artifacts)
    log_raw = (HERE / '06-job-log.decoded-utf8.txt').read_bytes()
    log = log_raw.decode('utf-8')
    raw = (HERE / '13-artifact-OBSERVATION.json').read_bytes()
    observation = json.loads(raw)
    transfer = read_json('12-archive-transfer.json')
    require(run['id'] == RUN and run['run_attempt'] == 1 and run['event'] == 'push'
            and run['status'] == 'completed' and run['conclusion'] == 'success'
            and run['path'] == WORKFLOW and run['head_sha'] == REMOTE and run['head_branch'] == BRANCH
            and run['repository']['full_name'] == run['head_repository']['full_name'] == 'theislampill/IMPLEMENTAUDIT.md',
            'EXACT_TERMINAL_PROVIDER_RUN')
    require(ref['ref'] == 'refs/heads/' + BRANCH and ref['object'] == {
        'sha': REMOTE, 'type': 'commit',
        'url': 'https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/git/commits/' + REMOTE},
        'EXACT_PUBLISHED_REF')
    require(remote_commit['sha'] == REMOTE and remote_commit['tree']['sha'] == TREE
            and [p['sha'] for p in remote_commit['parents']] == [BASE], 'EXACT_REMOTE_PARENT_AND_TREE')
    require(jobs['total_count'] == len(jobs['jobs']) == 1, 'ONE_ACTUAL_JOB')
    job = jobs['jobs'][0]
    require(job['id'] == JOB and job['run_id'] == RUN and job['run_attempt'] == 1
            and job['head_sha'] == REMOTE and job['head_branch'] == BRANCH and job['name'] == 'observe'
            and job['status'] == 'completed' and job['conclusion'] == 'success'
            and job['labels'] == ['ubuntu-26.04'], 'EXACT_TERMINAL_PROVIDER_JOB')
    require([s['name'] for s in job['steps']] == [
        'Set up job', 'Check out the exact observation source', 'Observe the unchanged selected host contract',
        'Retain the actual observation or refusal', 'Post Check out the exact observation source', 'Complete job']
        and all(s['status'] == 'completed' and s['conclusion'] == 'success' for s in job['steps']),
        'ONLY_EXPECTED_JOB_STEPS_SUCCEEDED')
    require(artifacts['total_count'] == len(artifacts['artifacts']) == 1, 'ONE_NEW_PROVIDER_ARTIFACT')
    artifact = artifacts['artifacts'][0]
    require(artifact['id'] == ARTIFACT and artifact['name'] == f'dg16-g221-prelaunch-host-inventory-{RUN}-1'
            and artifact['expired'] is False and artifact['size_in_bytes'] == 2443
            and artifact['workflow_run'] == {'id': RUN, 'repository_id': run['repository']['id'],
                'head_repository_id': run['head_repository']['id'], 'head_branch': BRANCH, 'head_sha': REMOTE},
            'ARTIFACT_JOINS_EXACT_RUN_REPOSITORY_AND_SOURCE')
    archive_raw = (HERE / '12-observation-artifact.zip').read_bytes()
    require(len(archive_raw) == artifact['size_in_bytes'] and 'sha256:' + sha(archive_raw) == artifact['digest']
            and transfer['http_status'] == 200 and transfer['provider_artifact_download_calls'] == 1
            and transfer['returned_file_reference_gets'] == 1, 'EXACT_ARCHIVE_PROVIDER_SIZE_AND_DIGEST')
    require(sorted(m['name'] for m in transfer['members']) == ['OBSERVATION.json', 'OBSERVATION.sha256'],
            'EXACT_ARCHIVE_MEMBER_POPULATION')
    pattern = r'^(\d{4}-\d\d-\d\dT[0-9:.]+Z) DG16_G221_HOST_INVENTORY sha256=([0-9a-f]{64}) base64=([A-Za-z0-9+/]+={0,2})$'
    markers = [m for line in log.splitlines() if (m := re.fullmatch(pattern, line))]
    require(len(markers) == 1, 'UNIQUE_ACTUAL_MARKER_EXCLUDING_PRINTED_WORKFLOW_SOURCE')
    marker = markers[0]
    decoded = base64.b64decode(marker[3], validate=True)
    require(raw == decoded == (HERE / '11-log-OBSERVATION.json').read_bytes() == canonical(observation)
            and marker[2] == sha(raw), 'CANONICAL_LF_LOG_ARTIFACT_BYTES_AND_SHA_EQUAL')
    require((HERE / '13-artifact-OBSERVATION.sha256').read_bytes() ==
            (sha(raw) + '  OBSERVATION.json\n').encode('ascii'), 'EXACT_OBSERVATION_SIDECAR')
    stamp = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
    require(stamp(job['started_at']) <= stamp(marker[1]) <= stamp(job['completed_at'])
            and stamp(job['started_at']) <= stamp(artifact['created_at']) <= stamp(job['completed_at']),
            'OBSERVATION_AND_ARTIFACT_WITHIN_ACTUAL_JOB_INTERVAL')
    require('G221_PUSH_CREATED: true' in log and 'G221_PUSH_DELETED: false' in log
            and re.search(r'^\d{4}-[^\n]+Z ' + REMOTE + r'$', log, re.MULTILINE) is not None
            and 'SHA256 digest of uploaded artifact zip is ' + sha(archive_raw) in log
            and 'Artifact ID is ' + str(ARTIFACT) in log, 'LOG_CHECKOUT_CREATED_BRANCH_AND_UPLOAD_JOIN')
    require(observation['provider'] == {'repository': 'theislampill/IMPLEMENTAUDIT.md', 'ref': 'refs/heads/' + BRANCH,
            'sha': REMOTE, 'run_id': str(RUN), 'attempt': '1', 'event': 'push'}, 'OBSERVATION_PROVIDER_JOIN')
    require(observation['schema'] == 'dg16.g221-prelaunch-host-inventory.v1'
            and observation['authority'] == 'NONE' and observation['scope'] == 'PRELAUNCH_OBSERVATION_ONLY'
            and observation['context'] == 'GITHUB_HOSTED' and observation['status'] == 'SELECTED_TUPLE_MATCH_OBSERVED'
            and observation['first_refusal'] is None and observation['closing_refusal'] is None
            and observation['selected_match'] is True and observation['source_closing_verified'] is True,
            'ACTUAL_MATCH_WITH_NO_REFUSAL_AND_COMPLETE_SOURCE_CLOSING')
    require(all(observation[k] is False for k in ('same_job_earned_qualification', 'currentness',
            'future_g221_acceptance', 'effect_grant')), 'NO_QUALIFICATION_CURRENTNESS_ACCEPTANCE_OR_GRANT_TRANSFER')

    require(remote_tree['sha'] == TREE and remote_tree['truncated'] is False, 'COMPLETE_REMOTE_ROOT_TREE')
    entries = remote_tree['tree']
    require(len({e['path'] for e in entries}) == len(entries), 'UNIQUE_REMOTE_ROOT_TREE_NAMES')
    ordered = sorted(entries, key=lambda e: (e['path'] + ('/' if e['type'] == 'tree' else '')).encode('utf-8'))
    tree_raw = b''.join(format(int(e['mode'], 8), 'o').encode('ascii') + b' ' + e['path'].encode('utf-8')
                        + b'\0' + bytes.fromhex(e['sha']) for e in ordered)
    require(git_object('tree', tree_raw) == TREE and tree_raw == git('cat-file', 'tree', CARRIER + '^{tree}'),
            'REMOTE_TREE_RECONSTRUCTS_AND_EQUALS_LOCAL_CARRIER_TREE')
    require(git('rev-parse', CARRIER + '^{tree}').decode().strip() == TREE, 'LOCAL_CARRIER_TREE_IDENTITY')
    candidate_paths = git('diff', '--name-only', BASE, CANDIDATE).decode().splitlines()
    require(len(candidate_paths) == 21, 'EXACT_REVIEWED_CANDIDATE_21_FILES')
    unchanged = []
    for name in candidate_paths:
        a = git('show', CANDIDATE + ':' + name)
        b = git('show', CARRIER + ':' + name)
        require(a == b and git('ls-tree', CANDIDATE, '--', name) == git('ls-tree', CARRIER, '--', name),
                'UNCHANGED_REVIEWED_MEMBER:' + name)
        unchanged.append(dict(path=name, **desc(a)))
    additions = git('diff', '--name-status', CANDIDATE, CARRIER).decode().splitlines()
    expected_additions = ['A\t' + EVIDENCE + n for n in
                         ('INDEPENDENT_SOURCE_REVIEW.md', 'LOCAL_REVIEW_COMMIT_OBJECT.txt', 'REVIEWED_PUBLICATION_JOIN.json')]
    require(additions == expected_additions, 'ONLY_THREE_PUBLICATION_JOIN_ADDITIONS')
    review_raw = git('show', CARRIER + ':' + EVIDENCE + 'INDEPENDENT_SOURCE_REVIEW.md')
    frozen_report = HERE.parent / 'g221-host-inventory-independent-review.md'
    require(sha(review_raw) == REVIEW_SHA and review_raw == frozen_report.read_bytes(), 'FROZEN_SOURCE_REVIEW_UNCHANGED')
    candidate_raw = git('show', CARRIER + ':' + EVIDENCE + 'LOCAL_REVIEW_COMMIT_OBJECT.txt')
    require(git_object('commit', candidate_raw) == CANDIDATE and candidate_raw == git('cat-file', 'commit', CANDIDATE),
            'RAW_REVIEWED_CANDIDATE_COMMIT_JOINS')
    join_raw = git('show', CARRIER + ':' + EVIDENCE + 'REVIEWED_PUBLICATION_JOIN.json')
    join = json.loads(join_raw)
    require(join['review_candidate'] == CANDIDATE and join['review_tree'] == '3531df3b34d5008f78030b0e40308d3da48ad8bf'
            and join['base'] == BASE and join['review']['sha256'] == REVIEW_SHA
            and join['candidate_files_unchanged'] == unchanged, 'PUBLICATION_JOIN_EXACT_MEMBER_DESCRIPTORS')
    write_once('16-reviewed-publication-join.raw.json', join_raw)
    packet = json.loads(git('show', CANDIDATE + ':' + EVIDENCE + 'REVIEW_PACKET.json'))
    expected_sources = {OBSERVER, WORKFLOW, *packet['unchanged_owner_source']}
    require(set(observation['sources']) == expected_sources, 'EXACT_TEN_EXECUTED_SOURCE_DESCRIPTORS')
    owner_bytes = {}
    for name in sorted(expected_sources):
        source = git('show', CARRIER + ':' + name)
        want = desc(source)
        if name in packet['unchanged_owner_source']:
            owner_bytes[name.rsplit('/', 1)[1]] = source
            require(source == git('show', BASE + ':' + name), 'UNCHANGED_OWNER_BYTES:' + name)
            want['expected_sha256'] = packet['unchanged_owner_source'][name]['sha256']
            require(want['expected_sha256'] == want['sha256'], 'EXPECTED_OWNER_PIN:' + name)
        require(observation['sources'][name] == want, 'ACTUAL_EXECUTED_SOURCE_DESCRIPTOR:' + name)
    require(observation['source_base_commit'] == BASE and observation['source_base_tree'] ==
            git('rev-parse', BASE + '^{tree}').decode().strip(), 'SOURCE_BASE_IDENTITY')

    # Pure receiving of actual emitted data through the unchanged target/encoder.
    # No inventory, credentials(), validate_request(), native loader, or host operation is called.
    modules = {}
    for filename in ('evidence_io.py', 'native_profile.py', 'current_host.py'):
        module = types.ModuleType('actual_observation_receiving_' + filename[:-3])
        module.__file__ = str(REPO / OWNER / filename)
        if modules:
            module.__dict__['_HOST_EVIDENCE_IO'] = modules['evidence_io.py']
        if 'native_profile.py' in modules:
            module.__dict__['_G2_NATIVE_PROFILE'] = modules['native_profile.py']
        exec(compile(owner_bytes[filename], module.__file__, 'exec'), module.__dict__)
        modules[filename] = module
    E = modules['evidence_io.py']
    C = modules['current_host.py']
    selected = C.target_host(observation['host'])
    selected_raw = E.encode(selected)
    matches = [i for i, candidate in enumerate(C.SELECTED_HOSTS) if E.encode(candidate) == selected_raw]
    require(E.encode(observation['selected_tuple']) == selected_raw
            and sha(selected_raw) == observation['selected_tuple_sha256'], 'ORIGINAL_TARGET_AND_ENCODER_REPRODUCE_ACTUAL_TUPLE')
    require(len(matches) == 1 and matches == [1]
            and sha(E.encode(list(C.SELECTED_HOSTS))) == observation['selected_candidates_sha256'],
            'GENUINE_EXACT_MATCH_TO_ORIGINAL_SECOND_SELECTED_HOST')
    require(set(selected['credentials']) == {'uid', 'euid', 'suid', 'gid', 'egid', 'sgid'}
            and all(type(v) is int and v == 1001 for v in selected['credentials'].values())
            and set(selected['tools']['bwrap']) == {'available', 'requested', 'canonical', 'bytes', 'sha256',
                'root_owned_nonwritable_chain', 'setid_or_file_capabilities'}, 'COMPLETE_ACTUAL_CREDENTIALS_AND_BWRAP_DESCRIPTOR')
    require(observation['tool_paths'] == {k: v['canonical'] for k, v in selected['tools'].items()},
            'TOOL_PATHS_MATCH_ACTUAL_DESCRIPTORS')
    require('Version: ' + selected['image_version'] in log and 'Image: ubuntu-26.04' in log,
            'RUNNER_IMAGE_LOG_MATCHES_ACTUAL_HOST')
    result = {
        'schema': 'dg16.g221-prelaunch-host-inventory-independent-receiving.v1',
        'receiver': '/root/g221_host_inventory_review', 'authority': 'NONE',
        'status': 'RECEIVED_ACTUAL_SELECTED_TUPLE_MATCH_OBSERVATION_ONLY',
        'first_failing_predicate': None, 'repository': 'theislampill/IMPLEMENTAUDIT.md',
        'ref': ref['ref'], 'remote_commit': REMOTE, 'remote_parent': BASE, 'published_tree': TREE,
        'local_carrier': CARRIER, 'reviewed_candidate': CANDIDATE, 'frozen_review_sha256': REVIEW_SHA,
        'run_id': RUN, 'attempt': 1, 'event': 'push', 'workflow': WORKFLOW, 'job_id': JOB,
        'job_started_at': job['started_at'], 'job_completed_at': job['completed_at'],
        'observation_log_time': marker[1], 'run_conclusion': run['conclusion'], 'job_conclusion': job['conclusion'],
        'runner': {k: job[k] for k in ('runner_id', 'runner_name', 'runner_group_id', 'runner_group_name', 'labels')},
        'artifact_id': ARTIFACT, 'artifact_name': artifact['name'], 'archive_bytes': len(archive_raw),
        'archive_sha256': sha(archive_raw), 'observation_bytes': len(raw), 'observation_sha256': sha(raw),
        'decoded_log_utf8_bytes': len(log_raw), 'decoded_log_utf8_sha256': sha(log_raw),
        'actual_marker_count': len(markers), 'selected_candidate_index_zero_based': matches[0],
        'selected_tuple_sha256': sha(selected_raw), 'selected_candidates_sha256': observation['selected_candidates_sha256'],
        'selected_tuple': selected, 'boot_identity_sha256': observation['host']['boot_identity_sha256'],
        'log_artifact_equality': True, 'source_closing_verified': True,
        'same_job_earned_qualification': False, 'currentness': False, 'future_g221_acceptance': False, 'effect_grant': False,
        'scope': 'This observed runner/image during this job interval only. No protected or future-job authority.',
        'checks': CHECKS, 'local_read_commands': COMMANDS,
        'no_source_test_reruns': True, 'no_inventory_rerun': True, 'no_protected_native_or_model_operation': True,
        'transport_retention': 'Provider JSON content strings and decoded UTF-8 log text retained losslessly as delivered; original ZIP and member bytes retained exactly. Temporary download URL and opaque file reference omitted.'}
    write_once('17-RECEIVING_RESULT.json', (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii'))
    print(json.dumps({k: result[k] for k in ('status', 'first_failing_predicate', 'run_id', 'job_id', 'artifact_id',
        'archive_bytes', 'archive_sha256', 'observation_bytes', 'observation_sha256', 'selected_tuple_sha256')}))
    print(json.dumps({'checks': len(CHECKS), 'all_checks_passed': all(c['passed'] for c in CHECKS)}))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        failure = {'status': 'RECEIVING_FAILED', 'exception_type': type(exc).__name__, 'checks': CHECKS,
                   'first_failing_predicate': next((x['predicate'] for x in CHECKS if not x['passed']), None),
                   'local_read_commands': COMMANDS}
        write_once('17-RECEIVING_FAILURE.json', (json.dumps(failure, sort_keys=True, indent=2) + '\n').encode('ascii'))
        print(json.dumps({'status': failure['status'], 'exception_type': failure['exception_type'],
                          'first_failing_predicate': failure['first_failing_predicate']}))
        raise SystemExit(1)
