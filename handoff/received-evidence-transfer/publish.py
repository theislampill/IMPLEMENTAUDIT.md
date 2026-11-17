#!/usr/bin/env python3
"""Copy three exact existing public export ZIPs into immutable Git blobs once."""
import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from urllib.parse import urlsplit

REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-dg18-evidence-transfer-20261117'
# Populated from the already received local ZIP identities before publication.
ARTIFACTS = [{'artifact_id': 14375482043, 'attempt': 1, 'bytes': 2852920, 'git_blob': '42f17ee8dc22fe44ec07a3b2eee4706a1e93330f', 'path': 'dg17-final-44182058642-1.zip', 'run_id': 44182058642, 'sha256': '3ee01fa640bbba272f0a01ca541d8afd69627ac936debfe5c1a5d551c3b81ae5'}, {'artifact_id': 14375731614, 'attempt': 1, 'bytes': 519889, 'git_blob': 'f3b9b1789e9f72cc8b35b2c69ba0baf5b318c09b', 'path': 'dg17-reaudited-44182058642-1.zip', 'run_id': 44182058642, 'sha256': '5119d8eaa8198cbe8cc51e94cf974ab8e593bd63d01ce5196a4a7a2328474afe'}, {'artifact_id': 14369278350, 'attempt': 1, 'bytes': 1650816, 'git_blob': 'c658ea14fbfe8ad47bf9c2486902bc11792fbbd5', 'path': 'dg17-h01-final-44160676786-1.zip', 'run_id': 44160676786, 'sha256': '20970f1ed06908fd923f99fa97b080bec46b300e9351f4ac352dd13561d1953b'}]


class Refusal(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def failure(error):
    result = {'error_type': type(error).__name__}
    if isinstance(error, Refusal):
        result['error_code'] = str(error)[:160]
    return result


class Journal:
    def __init__(self, directory):
        self.directory = directory
        need(directory.is_dir() and not directory.is_symlink() and directory.stat().st_uid == os.geteuid(), 'OUTPUT_CUSTODY')
        self.stream = (directory / 'receipts.jsonl').open('x', encoding='utf-8')

    def record(self, value):
        raw = encode({'time_ns': time.time_ns(), **value}).decode()
        self.stream.write(raw); self.stream.flush(); os.fsync(self.stream.fileno())
        print(raw, end='', flush=True)

    def result(self, value):
        with (self.directory / 'result.tmp').open('wb') as f:
            f.write(encode(value)); f.flush(); os.fsync(f.fileno())
        os.replace(self.directory / 'result.tmp', self.directory / 'result.json')
        fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def request(method, path, token, body=None, limit=2 * 1024 * 1024):
    """One exact GitHub request; no automatic redirect or retry."""
    connection = http.client.HTTPSConnection('api.github.com', timeout=20)
    try:
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'received-evidence-transfer'}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read(limit + 1)
        need(len(raw) <= limit, 'GITHUB_RESPONSE_BOUND')
        return response.status, response.getheader('Location'), raw
    finally:
        connection.close()


def artifact_bytes(row, token):
    endpoint = '/repos/' + REPO + '/actions/artifacts/' + str(row['artifact_id'])
    status, _, raw = request('GET', endpoint, token)
    need(status == 200, 'ARTIFACT_METADATA_HTTP_' + str(status))
    metadata = json.loads(raw)
    need(metadata.get('id') == row['artifact_id'] and metadata.get('expired') is False and
         metadata.get('workflow_run', {}).get('id') == row['run_id'] and
         metadata.get('size_in_bytes') == row['bytes'] and
         metadata.get('digest') == 'sha256:' + row['sha256'], 'ARTIFACT_METADATA_BINDING')
    status, location, _ = request('GET', endpoint + '/zip', token)
    need(status == 302 and type(location) is str, 'ARTIFACT_REDIRECT_REQUIRED')
    url = urlsplit(location)
    need(url.scheme == 'https' and url.hostname and not url.username and not url.password and
         not url.fragment and url.port in (None, 443), 'HTTPS_ARTIFACT_REDIRECT')
    # The authenticated GitHub endpoint supplies its supported download URL.
    # The standard ephemeral GitHub token is never sent to that storage URL.
    connection = http.client.HTTPSConnection(url.hostname, timeout=30)
    try:
        target = url.path + ('?' + url.query if url.query else '')
        connection.request('GET', target, headers={'User-Agent': 'received-evidence-transfer'})
        response = connection.getresponse()
        need(response.status == 200, 'ARTIFACT_DOWNLOAD_HTTP_' + str(response.status))
        data = response.read(row['bytes'] + 1)
    finally:
        connection.close()
    need(len(data) == row['bytes'] and sha(data) == row['sha256'] and blob(data) == row['git_blob'], 'EXACT_EXISTING_ARTIFACT_BYTES')
    return data


def publish_blob(row, data, token, journal, sequence):
    payload = encode({'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
    endpoint = '/repos/' + REPO + '/git/blobs'
    journal.record({'type': 'intent', 'sequence': sequence, 'method': 'POST', 'endpoint': endpoint,
                    'artifact_id': row['artifact_id'], 'path': row['path'], 'body_bytes': len(payload),
                    'body_sha256': sha(payload), 'expected_git_blob': row['git_blob']})
    receipt = {'type': 'result', 'sequence': sequence, 'status': 'UNKNOWN', 'artifact_id': row['artifact_id']}
    raw = None
    try:
        status, _, raw = request('POST', endpoint, token, payload)
        receipt.update(http_status=status, response_bytes=len(raw), response_sha256=sha(raw))
        need(status == 201, 'GIT_BLOB_HTTP_' + str(status))
        response = json.loads(raw)
        need(response.get('sha') == row['git_blob'], 'GIT_BLOB_IDENTITY')
        receipt.update(status='CONFIRMED', git_blob=response['sha'])
    except BaseException as error:
        receipt.update(failure(error))
        if raw is not None and token.encode() not in raw:
            name = 'response-' + str(sequence) + '.body'
            with (journal.directory / name).open('xb') as f:
                f.write(raw); f.flush(); os.fsync(f.fileno())
            receipt['response_body'] = name
        journal.record(receipt)
        raise Refusal('UNCONFIRMED_BLOB_STOP_NO_RETRY') from None
    journal.record(receipt)
    return {k: row[k] for k in ('artifact_id', 'run_id', 'path', 'bytes', 'sha256', 'git_blob')}


def event_binding():
    env = os.environ
    need(env.get('GITHUB_REPOSITORY') == REPO and env.get('GITHUB_REF') == 'refs/heads/' + BRANCH and
         env.get('GITHUB_EVENT_NAME') == 'push' and env.get('GITHUB_RUN_ATTEMPT') == '1', 'FIRST_OWNED_BRANCH_PUSH')
    need(env.get('GITHUB_API_URL') == 'https://api.github.com' and env.get('GITHUB_SERVER_URL') == 'https://github.com', 'PROVIDER')
    event = json.loads(Path(env['GITHUB_EVENT_PATH']).read_bytes())
    commit = env.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9a-f]{40}', commit) and env.get('GITHUB_WORKFLOW_SHA') == commit and
         event.get('after') == commit and event.get('before') == '0' * 40 and
         event.get('created') is True and event.get('deleted') is False and event.get('forced') is False and
         event.get('ref') == env['GITHUB_REF'] and event.get('repository', {}).get('full_name') == REPO, 'EXACT_NEW_NONFORCED_EVENT')
    root = Path(__file__).resolve().parents[2]
    actual = subprocess.run(['/usr/bin/git', '-c', 'safe.directory=' + str(root), '-C', str(root), 'rev-parse', 'HEAD'],
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
                            env={'PATH': '/usr/bin:/bin', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_TERMINAL_PROMPT': '0'}).stdout
    need(actual.decode().strip() == commit, 'EXACT_PUBLISHER_CHECKOUT')
    return commit


def main():
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[0-9]+', run_id), 'RUN_ID')
    output = Path(os.environ['RUNNER_TEMP']) / ('received-evidence-transfer-' + run_id + '-1')
    journal = Journal(output)
    result = {'schema': 'received-evidence-immutable-blob-transfer.v1', 'status': 'PREFLIGHT_PENDING', 'run_id': run_id,
              'confirmed': [], 'automatic_retry': False, 'commit_ref_or_runtime_effects': False}
    def expired(_s, _f):
        raise Refusal('BOUNDED_TRANSPORT_EXPIRED')
    signal.signal(signal.SIGALRM, expired); signal.signal(signal.SIGTERM, expired); signal.alarm(360)
    try:
        result['bootstrap_commit'] = event_binding()
        need(len(ARTIFACTS) == 3 and len({r['artifact_id'] for r in ARTIFACTS}) == 3, 'EXACT_THREE_ARTIFACTS')
        token = os.environ.pop('GITHUB_TOKEN', '')
        need(token and token.strip() == token, 'STANDARD_EPHEMERAL_TOKEN')
        data = [artifact_bytes(row, token) for row in ARTIFACTS]
        journal.record({'type': 'preflight_verified', 'artifact_ids': [r['artifact_id'] for r in ARTIFACTS],
                        'exact_public_zip_bytes': sum(len(x) for x in data), 'planned_immutable_blob_writes': 3})
        result['status'] = 'PREFLIGHT_VERIFIED'; journal.result(result)
        for n, (row, raw) in enumerate(zip(ARTIFACTS, data), 1):
            result['confirmed'].append(publish_blob(row, raw, token, journal, n))
            journal.result(result)
        result['status'] = 'THREE_IMMUTABLE_BLOBS_CONFIRMED'; journal.result(result)
        return 0
    except BaseException as error:
        result.update(status='STOPPED_NO_RETRY', **failure(error)); journal.result(result)
        return 1
    finally:
        signal.alarm(0); journal.stream.close()


if __name__ == '__main__':
    raise SystemExit(main())
