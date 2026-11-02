#!/usr/bin/env python3
"""Inert DG22 source/package/receipt checker. No fetch, ref write, push or live mode.

Receipt hashes establish byte custody, not issuer authenticity or authority.
An entitled receiver must authenticate the original CE021, CE059 and approval.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import zipfile

METHOD = 'single-parent-exact-tree/non-force-push-with-advertised-old-guard'
FINAL_RECEIPTS = ('CE021', 'DG21_COMMON_ADOPTION', 'Sol_selected_final_source',
                  'final_independent_candidate_review', 'human_exact_approval')
ROLES = {'canonical_plugin', 'standalone_compatibility'}
REMOTES = {'https://github.com/theislampill/IMPLEMENTAUDIT.md.git',
           'git@github.com:theislampill/IMPLEMENTAUDIT.md.git'}
CLOSING = re.compile(
    r'\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?:[\w.-]+/[\w.-]+)?#\d+'
    r'|\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+https://github\.com/[^\s]+/issues/\d+', re.I)


class Refusal(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def hexid(value, size=40):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{' + str(size) + '}', value), 'INVALID_HEX_ID')
    return value


def file_bytes(path):
    p = Path(path)
    require(p.is_absolute() and p.exists() and not p.is_symlink() and stat.S_ISREG(p.stat().st_mode), 'REGULAR_ABSOLUTE_FILE_REQUIRED')
    return p.read_bytes()


def receipt(ref):
    require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'}, 'RECEIPT_REFERENCE_REQUIRED')
    data = file_bytes(ref['path'])
    require(sha(data) == hexid(ref['sha256'], 64), 'RECEIPT_DIGEST_MISMATCH')
    return {'sha256': sha(data), 'bytes': len(data), 'issuer_authenticity_inferred': False}


def environment():
    e = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    e.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
             GIT_CONFIG_SYSTEM=os.devnull, GIT_NO_REPLACE_OBJECTS='1',
             GIT_TERMINAL_PROMPT='0', GIT_ALLOW_PROTOCOL='file',
             PYTHONDONTWRITEBYTECODE='1')
    return e


def git(repo, *args):
    require(args[0] in {'status', 'rev-parse', 'show', 'ls-tree'}, 'READ_ONLY_GIT_COMMAND_REQUIRED')
    p = subprocess.run(['git', '-c', 'credential.helper=', '-c', 'core.hooksPath=' + os.devnull,
                        '-C', str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment())
    require(p.returncode == 0, 'GIT_READ_FAILED:' + p.stderr.decode(errors='replace'))
    return p.stdout


def construct_future_command(subject, *, remote, checkout, hook_directory):
    """Return reviewable data only; this function never executes or writes it."""
    for k in ('expected_old', 'adoption_commit', 'source_tree', 'source_commit'):
        hexid(subject[k])
    require(remote in REMOTES, 'EXACT_REPOSITORY_REMOTE_REQUIRED')
    require(Path(checkout).is_absolute() and Path(hook_directory).is_absolute(), 'ABSOLUTE_OPERATION_PATHS_REQUIRED')
    values = {'remote': remote, 'candidate': subject['adoption_commit'],
              'target': 'refs/heads/main', 'old': subject['expected_old']}
    # Exact non-racing predicate from the accepted METHOD_ONLY pre-push guard.
    guard = ("#!/usr/bin/env python3\nimport json,sys\nV=" + repr(values) + "\n"
             "rows=[x.split() for x in sys.stdin.read().splitlines()]\n"
             "ok=(len(rows)==1 and len(rows[0])==4 and rows[0][1:]==[V['candidate'],V['target'],V['old']] and len(sys.argv)==3 and sys.argv[2]==V['remote'])\n"
             "print(json.dumps({'argv':sys.argv[1:],'advertised':rows,'guard_pass':ok}),file=sys.stderr)\n"
             "if not ok: print('DG22_EXPECTED_ADVERTISED_HEAD_REFUSED',file=sys.stderr); sys.exit(9)\n")
    return {'authorized_to_execute': False, 'method': METHOD, 'guard_values': values,
            'guard_python': guard, 'guard_sha256': sha(guard.encode()),
            'commit_tree_argv': ['git', '-C', checkout, 'commit-tree', subject['source_tree'], '-p', subject['expected_old']],
            'commit_tree_stdin': 'EXACT_APPROVED_UTF8_MESSAGE_BYTES; freeze author/committer identity and dates before deriving the candidate',
            'push_argv': ['git', '-c', 'credential.helper=', '-c', 'core.hooksPath=' + hook_directory,
                          '-C', checkout, 'push', '--porcelain', '--atomic', '--no-follow-tags',
                          '--no-force', '--recurse-submodules=no', remote,
                          subject['adoption_commit'] + ':refs/heads/main'],
            'transport_limit': 'Native Git remote transport and actual mainline permissions require Astra effect-time qualification; the connected API diagnostic is not a substitute.'}


def check(packet, *, final_gate=False):
    require(packet.get('schema') == 'dg22.inert-preflight-inputs.v1', 'INPUT_SCHEMA')
    require(packet.get('effects') == [] and packet.get('method') == METHOD, 'NO_LIVE_MUTATION_MODE')
    require(packet.get('scope') in {'PROVISIONAL_NOT_FINAL_SOURCE', 'EXACT_SELECTED_SUBJECT'}, 'SCOPE')
    authorities = packet.get('authority_inputs', {})
    require(set(authorities) == set(FINAL_RECEIPTS), 'AUTHORITY_INPUT_POPULATION')
    missing = [k for k in FINAL_RECEIPTS if authorities[k] is None]
    if final_gate:
        require(not missing, 'MISSING_AUTHENTIC_FINAL_INPUTS:' + ','.join(missing))
        require(packet['scope'] == 'EXACT_SELECTED_SUBJECT', 'PROVISIONAL_SUBJECT_CANNOT_BE_FINAL')
    custody = {k: receipt(v) for k, v in authorities.items() if v is not None}
    if packet['scope'] == 'PROVISIONAL_NOT_FINAL_SOURCE':
        custody['provisional_authorization'] = receipt(packet['provisional_authorization'])
    evidence = packet.get('evidence', {})
    require(set(evidence) == {'accepted_method', 'package_qualification', 'source_cutoff'}, 'EVIDENCE_POPULATION')
    custody.update({k: receipt(v) for k, v in evidence.items()})
    s = packet['subject']
    for k in ('source_commit', 'source_tree', 'adoption_commit', 'expected_old'):
        hexid(s[k])
    repo = Path(s['checkout'])
    require(repo.is_absolute() and repo.is_dir(), 'CHECKOUT_REQUIRED')
    require(git(repo, 'rev-parse', '--verify', 'HEAD').decode().strip() == s['adoption_commit'], 'CHECKOUT_COMMIT_MISMATCH')
    require(not git(repo, 'status', '--porcelain', '--untracked-files=all'), 'DIRTY_SOURCE')
    require(git(repo, 'rev-parse', s['source_commit'] + '^{tree}').decode().strip() == s['source_tree'], 'SOURCE_TREE_MISMATCH')
    require(git(repo, 'rev-parse', s['adoption_commit'] + '^{tree}').decode().strip() == s['source_tree'], 'ADOPTION_TREE_MISMATCH')
    require(git(repo, 'show', '-s', '--format=%P', s['adoption_commit']).decode().split() == [s['expected_old']], 'ORDERED_PARENT_MISMATCH')
    message = git(repo, 'show', '-s', '--format=%B', s['adoption_commit'])
    require(sha(message) == hexid(s['commit_message_sha256'], 64), 'COMMIT_MESSAGE_MISMATCH')
    require(not CLOSING.search(message.decode()), 'CLOSING_DIRECTIVE_REFUSED')
    source_members = git(repo, 'ls-tree', '--full-tree', '-rz', s['source_commit'])
    adoption_members = git(repo, 'ls-tree', '--full-tree', '-rz', s['adoption_commit'])
    require(source_members == adoption_members, 'SOURCE_BLOB_MODE_POPULATION_MISMATCH')
    artifacts = packet['artifacts']
    require(len(artifacts) == 2 and {a['role'] for a in artifacts} == ROLES, 'EXACT_TWO_PACKAGE_ROLES_REQUIRED')
    for a in artifacts:
        require(sha(file_bytes(a['path'])) == hexid(a['sha256'], 64), 'ARTIFACT_DIGEST_MISMATCH')
    verified = []
    for a in artifacts:
        argv = [sys.executable, str(repo / 'scripts/package-contract.py'), '--verify-artifact',
                a['role'], a['path'], '--require-clean-source']
        p = subprocess.run(argv, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment())
        require(p.returncode == 0, 'STRICT_ARTIFACT_REFUSAL:' + p.stderr.decode(errors='replace'))
        with zipfile.ZipFile(a['path']) as z:
            inv = json.loads(z.read('IMPLEMENTAUDIT_INVENTORY.json'))
            require(inv['source'] == {'commit': s['adoption_commit'], 'tree': s['source_tree'], 'worktree_state': 'clean'}, 'EXACT_INVENTORY_SOURCE_MISMATCH')
        verified.append({'role': a['role'], 'sha256': a['sha256'], 'verifier_exit': p.returncode,
                         'argv': argv, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()})
    require(not git(repo, 'status', '--porcelain', '--untracked-files=all'), 'POSTCHECK_DIRTY_SOURCE')
    return {'schema': 'dg22.inert-preflight-result.v1',
            'status': 'MECHANICAL_INPUTS_VERIFIED_EXTERNAL_AUTHENTICATION_REQUIRED' if final_gate else 'PROVISIONAL_INPUTS_VERIFIED',
            'scope': packet['scope'], 'adoption_ready': False, 'live_mutation_mode': False,
            'missing_final_inputs': missing, 'receipt_custody': custody,
            'source_inventory_sha256': sha(source_members), 'subject': s,
            'strict_artifacts': verified, 'authority_authentication': 'NOT_PERFORMED_BY_THIS_TOOL',
            'external_gate': 'Entitled receiving must authenticate original receipts, selected finite claims and exact owner approval; byte hashes cannot confer authority.'}


def unique_object(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, 'DUPLICATE_JSON_KEY:' + k)
        out[k] = v
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', required=True)
    parser.add_argument('--require-final-inputs', action='store_true')
    args = parser.parse_args()
    try:
        packet = json.loads(Path(args.packet).read_text(), object_pairs_hook=unique_object)
        report = check(packet, final_gate=args.require_final_inputs)
    except (Refusal, KeyError, OSError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(json.dumps({'status': 'REFUSED', 'reason': str(error), 'adoption_ready': False,
                          'live_mutation_mode': False}, indent=2))
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
