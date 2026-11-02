#!/usr/bin/env python3
"""Bind R003F's retained certificate to independently received final records.

This is a narrow offline consistency consumer, not a DG21/DG22 issuer or an
authenticator of prose authority. Complete original records and their semantic
and authority receiving remain mandatory. No network or Git/issue write occurs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from verify_delivery import digest, read_json, safe_path, strict_object

CONTRACT_SHA256 = 'bdebcd505d3dd41698305496a3c5739c46aa3bc24b9ac9641984d0d7c85db396'


class BindingError(ValueError):
    pass


class PendingInput(BindingError):
    pass


def require(condition, message):
    if not condition:
        raise BindingError(message)


def canonical_hash(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode())


def named(value, message):
    require(isinstance(value, str) and bool(value.strip()), message)
    return value


def hex_id(value, length, message):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{' + str(length) + '}', value), message)
    return value


def read_contract():
    path = Path(__file__).with_name('R003F_RECEIVING_CONTRACT.json')
    require(digest(path.read_bytes()) == CONTRACT_SHA256, 'receiving contract identity changed')
    return read_json(path)


def file_identity(root, reference):
    require(isinstance(reference, dict), 'missing complete record reference')
    path = safe_path(root, reference['path'])
    require(path.is_file(), 'complete record is unavailable: ' + reference['path'])
    data = path.read_bytes()
    require(len(data) == reference['bytes'] and digest(data) == reference['sha256'],
            'complete record identity mismatch: ' + reference['path'])
    return data


def select_value(data, pointer):
    selected = data.decode('utf-8') if pointer is None else json.loads(data, object_pairs_hook=strict_object)
    if pointer:
        require(isinstance(pointer, str) and pointer.startswith('/'), 'invalid record pointer')
        try:
            for raw in pointer[1:].split('/'):
                key = raw.replace('~1', '/').replace('~0', '~')
                selected = selected[int(key)] if isinstance(selected, list) else selected[key]
        except (KeyError, ValueError, IndexError, TypeError) as error:
            raise BindingError('record pointer does not resolve') from error
    return selected


def make_reference(root, path, pointer='', origin='receipts'):
    data = safe_path(root, path).read_bytes()
    return {'origin': origin, 'path': path, 'bytes': len(data), 'sha256': digest(data),
            'json_pointer': pointer, 'selected_value_canonical_sha256': canonical_hash(select_value(data, pointer))}


def selected_record(root, reference, evidence_kind):
    data = file_identity(root, reference)
    selected = select_value(data, reference['json_pointer'])
    require(canonical_hash(selected) == reference['selected_value_canonical_sha256'],
            'record pointer identity mismatch')
    require(selected not in (None, '', [], {}), 'empty record is not receiving evidence')
    if evidence_kind == 'ACTUAL' and isinstance(selected, dict):
        require(selected.get('evidence_kind') != 'CONSTRUCTED' and selected.get('fixture') is not True,
                'constructed evidence cannot become an actual receipt')
    return selected


def disclosed_identity(selected, expected, role):
    """Do not let a normalization contradict identities exposed by its original.

Prose/other producer formats still need the distinct independent semantic and
authority receiving. This check does not manufacture an absent actor statement.
"""
    if isinstance(selected, dict):
        for key, value in expected.items():
            if key in selected:
                actual = selected[key]
                same = actual == value or (key == 'issue' and actual == 225 and value == 'R003F')
                require(same, role + ' original record contradicts ' + key)


def git_read(repo, args):
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *args],
                            capture_output=True, timeout=30)
    require(result.returncode == 0, 'read-only Git lookup failed: ' + result.stderr.decode(errors='replace'))
    return result.stdout


def git_source_readback(repo, source, expected_paths):
    commit = hex_id(source.get('commit'), 40, 'invalid source commit')
    tree = hex_id(source.get('tree'), 40, 'invalid source tree')
    require(git_read(repo, ['rev-parse', '--verify', commit + '^{tree}']).decode().strip() == tree,
            'Git commit/tree mismatch')
    parents = git_read(repo, ['show', '-s', '--format=%P', commit]).decode().strip().split()
    names = [row['path'] for row in expected_paths]
    raw = git_read(repo, ['ls-tree', '-rz', '--long', commit, '--', *names])
    observed = {}
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, kind, blob, size = meta.decode().split()
        observed[path.decode()] = {'mode': mode, 'kind': kind, 'blob': blob, 'bytes': int(size)}
    require(set(observed) == set(names), 'consumed path missing or extra in final source')
    for row in expected_paths:
        require(observed[row['path']] == {k: row[k] for k in ('mode', 'kind', 'blob', 'bytes')},
                'changed consumed path needs affected qualification: ' + row['path'])
    return {'commit': commit, 'tree': tree, 'ordered_parents': parents,
            'consumed_paths': [{'path': path, **observed[path]} for path in sorted(observed)],
            'proof_scope': 'exact Git identity of the retained documentary dependency closure'}


def bind(data, receipts_root, retained, continuation, repo, expected_main, acceptance=None, sol_authority=None):
    contract = read_contract()
    require(data.get('schema') == 'dg31.r003f.final-binding-input.v1', 'unsupported receiving input')
    kind = data.get('evidence_kind')
    require(kind in ('ACTUAL', 'CONSTRUCTED'), 'evidence kind must be explicit')
    require(data.get('repository') == contract['repository'] and data.get('issue') == 'R003F', 'wrong repository or issue')
    named(data.get('prepared_by'), 'missing actual preparer identity')
    pending = [edge for edge, state in [('ce085', 'PASS'), ('ce086', 'ACTUAL_ADOPTION_READBACK')]
               if not isinstance(data.get(edge), dict) or data[edge].get('state') != state]
    if pending or not data.get('source'):
        raise PendingInput('Authentic final-source receiving/adoption inputs pending: ' + ', '.join(pending or ['source']))
    source = data['source']
    require(source.get('commit') == hex_id(expected_main, 40, 'fresh main commit is required'),
            'selected source does not match the separately observed fresh main')
    require(set(source) == {'commit', 'tree'}, 'source must name exactly commit and tree')
    for ref in contract['retained_files']:
        file_identity(retained, ref)
    file_identity(continuation, contract['historical_dg21_records'])
    certificate = read_json(retained / 'checkpoint/CERTIFICATE.json')
    cert_sha = contract['retained_files'][0]['sha256']
    require({r['id']: r['accepted_disposition'] for r in certificate['original_predicates']} == contract['original_predicates'],
            'original predicate population or disposition changed')
    g = git_source_readback(repo, source, contract['consumed_paths'])
    refs_checked = []

    def receive(ref):
        require(isinstance(ref, dict), 'missing complete record reference')
        origin = ref.get('origin', 'receipts')
        require(origin in ('receipts', 'continuation'), 'unsupported record origin')
        if origin == 'continuation':
            require(all(ref.get(k) == contract['historical_dg21_records'][k]
                        for k in ('path', 'bytes', 'sha256')), 'only pinned historical receiving uses continuation origin')
        selected = selected_record(continuation if origin == 'continuation' else receipts_root, ref, kind)
        refs_checked.append(ref)
        return selected

    ce85, ce86 = data['ce085'], data['ce086']
    for edge in (ce85, ce86):
        require(edge.get('issue') == 'R003F', 'borrowed sibling issue receipt')
        require(edge.get('source') == source, 'receipt source identity differs from final source')
    require(ce85.get('scope') == contract['selected_scope'], 'unsupported stronger R003F claim scope')
    require(ce85.get('certificate_sha256') == cert_sha, 'wrong retained certificate identity')
    require(ce85.get('residual_receipt_hashes') == contract['residual_receipt_hashes'], 'incomplete or altered residual receiving')
    for key in ('producer', 'receiver', 'environment'):
        named(ce85.get(key), 'missing CE085 ' + key)
    original = receive(ce85.get('original_receipt'))
    disclosed_identity(original, {'issue': 'R003F', 'rlgwo': 'R003F'}, 'CE085 issue')
    current = receive(ce85.get('current_receiving'))
    disclosed_identity(current, {key: ce85[key] for key in
                       ('state', 'issue', 'source', 'producer', 'receiver', 'environment', 'scope',
                        'certificate_sha256', 'residual_receipt_hashes')}, 'CE085 current source receiving')
    receive(ce85.get('receiver_authority'))
    claims = ce85.get('conditional_claims', {})
    require(set(claims) == set(contract['conditional_claims']), 'conditional claim population changed')
    for name, claim in claims.items():
        claim_record = receive(claim.get('record'))
        disclosed_identity(claim_record, {'state': claim.get('state'), 'issue': 'R003F', 'qualified_source': source}, name + ' qualification')
        if claim.get('state') == 'NOT_TRIGGERED_WITH_JUSTIFICATION':
            named(claim.get('reason'), name + ' lacks an entitled issue-specific nontrigger justification')
        else:
            require(claim.get('state') == 'PASS', name + ' remains unqualified')
            require(claim.get('qualified_source') == source, name + ' qualification source mismatch')
            named(claim.get('consumer'), name + ' consumer missing')
            named(claim.get('environment'), name + ' environment missing')
            if name in ('package', 'installed'):
                artifact_source = hex_id(claim.get('artifact_source_commit'), 40, name + ' artifact source missing')
                hex_id(claim.get('artifact_sha256'), 64, name + ' artifact identity missing')
                if artifact_source != source['commit']:
                    bridge = claim.get('bridge')
                    require(isinstance(bridge, dict) and bridge.get('result') == 'PASS' and
                            bridge.get('from_commit') == artifact_source and bridge.get('to_source') == source,
                            'different artifact source requires an exact qualified consumer bridge')
                    named(bridge.get('consumer'), 'bridge consumer missing')
                    bridge_record = receive(bridge.get('record'))
                    disclosed_identity(bridge_record, {key: bridge[key] for key in
                                       ('result', 'from_commit', 'to_source', 'consumer')}, 'qualified consumer bridge')

    approval = ce86.get('owner_approval')
    require(isinstance(approval, dict), 'actual owner approval missing')
    old = hex_id(ce86.get('expected_old_main'), 40, 'expected-old main identity missing')
    parents = ce86.get('ordered_parents')
    require(isinstance(parents, list) and parents and g['ordered_parents'] == parents,
            'adoption ordered parents disagree')
    git_read(repo, ['merge-base', '--is-ancestor', old, source['commit']])
    require(ce86.get('target_ref') == 'refs/heads/main', 'wrong adoption target ref')
    require(approval.get('operation') == 'ADOPT_MAIN' and approval.get('source') == source and
            approval.get('expected_old_main') == old and approval.get('ordered_parents') == parents,
            'owner approval is for a different adoption subject')
    approval_record = receive(approval.get('record'))
    disclosed_identity(approval_record, {key: approval[key] for key in
                       ('operation', 'source', 'expected_old_main', 'ordered_parents')}, 'owner approval')
    adoption_record = receive(ce86.get('adoption_result'))
    disclosed_identity(adoption_record, {key: ce86[key] for key in
                       ('source', 'expected_old_main', 'ordered_parents', 'target_ref')}, 'adoption result')
    main = receive(ce86.get('main_readback'))
    require(isinstance(main, dict) and main.get('ref') == 'refs/heads/main' and
            main.get('object', {}).get('type') == 'commit' and main['object'].get('sha') == source['commit'] and
            main.get('url') == 'https://api.github.com/repos/' + contract['repository'] + '/git/refs/heads/main',
            'actual main readback does not bind the approved repository/ref/commit')
    commit = receive(ce86.get('commit_readback'))
    require(isinstance(commit, dict) and commit.get('sha') == source['commit'] and
            commit.get('tree', {}).get('sha') == source['tree'] and
            [p.get('sha') for p in commit.get('parents', [])] == parents,
            'actual commit readback does not bind tree/ordered parents')
    issue_read = ce86.get('issue_slice_readback', {})
    require(issue_read.get('issue') == 'R003F' and issue_read.get('source') == source and
            issue_read.get('certificate_sha256') == cert_sha and
            issue_read.get('residual_receipt_hashes') == contract['residual_receipt_hashes'],
            'incomplete issue-slice certificate/residual readback')
    named(issue_read.get('receiver'), 'independent issue-slice receiver missing')
    require(issue_read.get('independent_of_adoption_writer') is True, 'issue-slice independence not received')
    issue_record = receive(issue_read.get('record'))
    disclosed_identity(issue_record, {key: issue_read[key] for key in
                       ('issue', 'source', 'certificate_sha256', 'residual_receipt_hashes')}, 'issue-slice readback')

    core = {'schema': 'dg31.r003f.final-certificate-core.v1', 'evidence_kind': kind,
            'repository': contract['repository'], 'issue': 'R003F', 'source': source,
            'prepared_by': data['prepared_by'], 'input_canonical_sha256': canonical_hash(data),
            'retained_files': contract['retained_files'], 'historical_dg21_records': contract['historical_dg21_records'],
            'original_predicates': contract['original_predicates'], 'population': certificate['population'],
            'protected_limits': certificate['protected_limits'], 'source_readback': g,
            'ce085_receiving': ce85, 'ce086_receiving': ce86,
            'residual_receipt_hashes': contract['residual_receipt_hashes'],
            'claim_limit': 'Exact retained documentary scope and explicitly qualified conditional claims only; no issue effect.'}
    core_hash = canonical_hash(core)
    accepted = False
    authorized = False
    if acceptance is not None:
        require(acceptance.get('state') == 'ACCEPTED' and acceptance.get('core_sha256') == core_hash and
                acceptance.get('independent_of_preparer') is True and
                named(acceptance.get('reviewer'), 'acceptance reviewer missing') != data['prepared_by'],
                'independent acceptance does not bind this exact final core')
        acceptance_record = receive(acceptance.get('record'))
        disclosed_identity(acceptance_record, {key: acceptance[key] for key in
                           ('state', 'core_sha256', 'reviewer', 'independent_of_preparer')}, 'independent acceptance')
        receive(acceptance.get('authority'))
        accepted = True
    if sol_authority is not None:
        require(sol_authority.get('core_sha256') == core_hash and sol_authority.get('issue') == 225 and
                sol_authority.get('writer') == 'Sol' and sol_authority.get('exclusive') is True and
                sol_authority.get('operation') == 'post_final_evidence_comment',
                'comment authority must bind this core and Sol-exclusive issue225 custody')
        sol_record = receive(sol_authority.get('record'))
        disclosed_identity(sol_record, {key: sol_authority[key] for key in
                           ('core_sha256', 'issue', 'writer', 'exclusive', 'operation')}, 'Sol authority')
        authorized = True
    return {'schema': 'dg31.r003f.final-binding-result.v1',
            'result': 'PASS_CONSTRUCTED_FORM_ONLY' if kind == 'CONSTRUCTED' else 'CONSISTENT_FOR_INDEPENDENT_RECEIVING',
            'core': core, 'core_sha256': core_hash,
            'independent_acceptance_supplied': accepted, 'sol_comment_authority_supplied': authorized,
            'comment_ready': kind == 'ACTUAL' and accepted and authorized,
            'closure_ready': False, 'issue_comment_posted': False, 'issue_closed': False,
            'verification_limit': 'Offline identities and consistency only. Referenced producer/authority acts must be authentically received; fixture labels never establish them.',
            'complete_record_references_checked': len(refs_checked)}


def evidence_draft(result):
    core = result['core']
    constructed = core['evidence_kind'] == 'CONSTRUCTED'
    heading = 'CONSTRUCTED CONTROL — NEVER POST' if constructed else 'R003F / issue225 — final evidence receiving'
    lines = ['# ' + heading, '', 'Final certificate core SHA-256: `' + result['core_sha256'] + '`.', '',
             'Adopted source: `' + core['source']['commit'] + '`; tree: `' + core['source']['tree'] + '`.', '',
             'Retained original certificate: `149e7f9eb12af23ccb55a833ba566d9914f24ace`, '
             '`docs/integration/pro-dg31-r003f-certification-20261101/CERTIFICATE.json`.', '',
             'The original73 EBPM properties and separate234-member/41-group/608-membership BWP component '
             'retain their accepted documentary/source, bounded semantic-decision and residual-receiving scopes.', '',
             '| Original controls | Retained disposition |', '| --- | --- |']
    for key, state in core['original_predicates'].items():
        lines.append('| ' + key + ' | ' + state + ' |')
    lines += ['', 'CE085 binds the original independent issue receipt and current final-source receiving. '
              'CE086 binds actual owner approval, adoption and independent main/commit/issue-slice readbacks. '
              'Their complete identities and source/environment/consumer bindings are in the exact final core.', '',
              'The29 consumed documentary paths retain their exact qualified Git identities. '
              'Package, installed and native claim dispositions are separately recorded; none is inferred from source equality.', '']
    for key, claim in core['ce085_receiving']['conditional_claims'].items():
        lines.append('- ' + key + ': `' + claim['state'] + '`.')
    lines += ['', 'E6/B8 retain the original full residual records, horizons and lawful next actions. '
              'EBPM-053 remains unresolved/research-only. TC10 comparison/configuration, non-equivalence, '
              'common-source and original negative/UNKNOWN limits survive. No native effectiveness, '
              'general autonomy or business-benefit promotion follows.', '',
              'The historical33 unavailable byte subjects remain explicit historical limitations; '
              'the accepted current primary/group/context/receiving records are retained.', '',
              'This evidence comment does not itself close the issue. Exclusive Sol custody, independent '
              'final certificate acceptance, actual independent published-body readback, separate manual '
              'closure authority and final GitHub issue-state readback remain distinct.', '']
    return '\n'.join(lines)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'reference':
        parser = argparse.ArgumentParser(description='Make an identity descriptor from complete actual bytes; this does not issue a receipt.')
        parser.add_argument('root', type=Path)
        parser.add_argument('path')
        parser.add_argument('--pointer', default='')
        parser.add_argument('--text', action='store_true')
        parser.add_argument('--origin', choices=['receipts', 'continuation'], default='receipts')
        args = parser.parse_args(sys.argv[2:])
        print(json.dumps(make_reference(args.root, args.path, None if args.text else args.pointer, args.origin), indent=2))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--retained', required=True, type=Path)
    parser.add_argument('--continuation', required=True, type=Path)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--expected-main', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--acceptance', type=Path)
    parser.add_argument('--sol-authority', type=Path)
    args = parser.parse_args()
    roots = [args.inputs.parent, args.retained, args.continuation, args.repo]
    output = args.output.resolve()
    require(not args.output.is_symlink(), 'output cannot be a symlink')
    for root in roots:
        require(not root.is_symlink(), 'input root cannot be a symlink')
        resolved = root.resolve()
        require(output != resolved and resolved not in output.parents, 'outputs must be outside inputs and source')
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())), 'output directory must be empty')
    try:
        result = bind(read_json(args.inputs), args.inputs.parent, args.retained, args.continuation, args.repo,
                      args.expected_main, read_json(args.acceptance) if args.acceptance else None,
                      read_json(args.sol_authority) if args.sol_authority else None)
        exit_code = 0
    except PendingInput as error:
        result = {'result': 'BLOCKED_PENDING_AUTHENTIC_INPUTS', 'reason': str(error), 'comment_ready': False, 'closure_ready': False}
        exit_code = 2
    output.mkdir(parents=True, exist_ok=True)
    (output / 'FINAL_BINDING.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    if 'core' in result:
        (output / 'FINAL_CERTIFICATE_CORE.json').write_text(json.dumps(result['core'], indent=2, ensure_ascii=False) + '\n')
        (output / 'SOL_FINAL_EVIDENCE_DRAFT.md').write_text(evidence_draft(result), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'core'}, indent=2))
    return exit_code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (BindingError, KeyError, ValueError, TypeError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'result': 'REFUSED', 'reason': str(error), 'comment_ready': False, 'closure_ready': False}), file=sys.stderr)
        raise SystemExit(1)
