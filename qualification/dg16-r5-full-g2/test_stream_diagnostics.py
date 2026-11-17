"""Focused diagnostic regression; fixture data is never hosted acceptance evidence.

Pass the retained decoded public PROBE.json as the sole argument. No private
capture, verifier process, protected operation, or network is used.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


def module(name):
    path = Path(__file__).with_name(name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    full, adapter, reports = module('full_relation'), module('run'), module('full_output_relation')
    probe = json.loads(Path(sys.argv[1]).read_bytes())
    historical = copy.deepcopy(probe['result']['full_correspondence'])
    assert historical['relations']['whole']['difference_count'] == 4
    assert [w['kind'] for w in historical['relations']['whole']['witnesses']] == ['VALUE', 'VALUE']

    # Public fixture streams demonstrate both interior and shorter-stream EOF
    # differences; they are not reconstructions of the unavailable historical bytes.
    profile = json.loads(Path(__file__).with_name('REPORT_SLOTS.json').read_bytes())
    # Constructed report-shaped buffers only; no original tests are executed.
    headers = (b'.\n' + b'-' * 70 + b'\nRan 1 test in 1.000s\n\nOK\n') * 111
    raw_stderr = {'legacy': b'line' + headers, 'dag': b'lines' + headers}
    normalized_stderr = {}
    for mode, raw in raw_stderr.items():
        for match in reversed(list(reports.HEADER.finditer(raw))):
            raw = raw[:match.start(3)] + b'<DECLARED_UNITTEST_DIAGNOSTIC_SECONDS>' + raw[match.end(3):]
        normalized_stderr[mode] = raw
    streams = {'legacy': {'stdout': b'abcX\n', 'stderr': normalized_stderr['legacy']},
               'dag': {'stdout': b'abcY\n', 'stderr': normalized_stderr['dag']}}
    projections = {mode: {'whole': {
        'result': {name + '_sha256': hashlib.sha256(raw).hexdigest() for name, raw in pair.items()},
        **pair}} for mode, pair in streams.items()}
    original = full.compare(projections['legacy']['whole'], projections['dag']['whole'])
    assert original['difference_count'] == 4
    assert [w['kind'] for w in original['witnesses']] == ['VALUE', 'VALUE']
    proof = copy.deepcopy(historical)
    proof['schema'] = 'dg16.full-correspondence-proof.v3'
    proof['policy_sha256'] = adapter.POLICY_SHA
    proof['receiver_inputs_sha256'] = adapter.RELATION_INPUTS_SHA
    proof['source_commit'], proof['source_tree'] = adapter.SOURCE_COMMIT, adapter.SOURCE_TREE
    proof['relations']['whole'] = original
    # This known-safe closed extension is rejected by the old public validator.
    proof['normalized_streams'] = {
        name: full.compare(streams['legacy'][name], streams['dag'][name])
        for name in ('stdout', 'stderr')}
    proof['stderr_location'], _ = full.stderr_first_difference(raw_stderr, normalized_stderr,
        profile, reports, full.REPORT_PROFILE_SHA)
    bindings = dict(policy_sha=adapter.POLICY_SHA, inputs_sha=adapter.RELATION_INPUTS_SHA,
                    source_commit=adapter.SOURCE_COMMIT, source_tree=adapter.SOURCE_TREE)
    try:
        full.validate_public_proof(proof, **bindings)
    except full.Refusal as exc:
        raise AssertionError('Safe stream differences cannot reach the public proof: ' + str(exc)) from exc

    observed = full.normalized_stream_relations(projections)
    assert observed == proof['normalized_streams']
    for name, offset, left_size, right_size in [('stdout', 3, 5, 5),
            ('stderr', 4, len(normalized_stderr['legacy']), len(normalized_stderr['dag']))]:
        row = observed[name]
        assert row['equal'] is False and row['difference_count'] == 1 and row['witnesses_complete'] is True
        witness = row['witnesses'][0]
        assert witness['kind'] == 'BYTES' and witness['first_different_offset'] == offset
        assert witness['left']['bytes'] == left_size and witness['right']['bytes'] == right_size
        for side, mode in [('left', 'legacy'), ('right', 'dag')]:
            assert witness[side]['sha256'] == hashlib.sha256(streams[mode][name]).hexdigest()
    assert proof['relations']['whole'] == original
    assert proof['all_declared_relations_equal'] is False
    assert all(proof[key] is False for key in ('original_acceptance', 'full_G2', 'G1', 'G3'))
    for raw in (b'abcX', b'abcY', b'lines'):
        assert raw not in full.encode(proof)

    # Exercise the unchanged, pinned failed-summary reader and public wire codec.
    candidate = copy.deepcopy(probe['result'])
    candidate['policy_sha256'] = adapter.POLICY_SHA
    candidate['source_commit'], candidate['source_tree'] = adapter.SOURCE_COMMIT, adapter.SOURCE_TREE
    candidate['full_correspondence'] = proof
    utility = adapter.load_utility()
    with tempfile.TemporaryDirectory(prefix='g2-stream-diagnostic-') as temp:
        output = Path(temp)
        destination = output / 'private/full-pair/RECEIVED_PUBLIC.json'
        destination.parent.mkdir(parents=True)
        destination.write_bytes(adapter.canonical(candidate))
        retained = adapter.read_pair_summary(output, True, utility)
        assert retained == candidate
    probe['result'] = retained
    probe['result_disposition'] = 'VALIDATED_UNACCEPTED_NONZERO_RECEIVE'
    wire = utility.public_codec('PROBE.json', probe)
    decoded = utility.public_codec('PROBE.json', wire, True)
    assert decoded['result']['full_correspondence'] == proof
    assert decoded['result_disposition'] == 'VALIDATED_UNACCEPTED_NONZERO_RECEIVE'
    assert len(full.encode(proof)) <= 16384 and len(wire) <= 65536

    equal = copy.deepcopy(proof)
    equal['normalized_streams'] = full.normalized_stream_relations({'legacy': projections['legacy'], 'dag': projections['legacy']})
    equal['stderr_location'] = None
    full.validate_public_proof(equal, **bindings)
    assert all(row['equal'] and row['difference_count'] == 0 and row['witnesses'] == []
               for row in equal['normalized_streams'].values())

    refused = []
    for name in ('raw_export', 'unknown_stream', 'bad_offset', 'wrong_kind', 'extra_difference'):
        invalid = copy.deepcopy(proof)
        rows = invalid['normalized_streams']
        if name == 'raw_export': rows['stdout']['witnesses'][0]['raw'] = 'PRIVATE_OUTPUT'
        elif name == 'unknown_stream': rows['private_path'] = rows.pop('stdout')
        elif name == 'bad_offset': rows['stdout']['witnesses'][0]['first_different_offset'] = 5
        elif name == 'wrong_kind': rows['stdout']['witnesses'][0]['kind'] = 'VALUE'
        else: rows['stdout']['difference_count'] = 2
        try: full.validate_public_proof(invalid, **bindings)
        except full.Refusal: refused.append(name)
        else: raise AssertionError('Unsafe stream metadata accepted: ' + name)
    print(json.dumps({'scope': 'LOCAL_DIAGNOSTIC_REGRESSION_ONLY', 'result': 'PASS',
        'historical_difference_count': 4, 'fixture_difference_count': original['difference_count'],
        'stream_offsets': {'stdout': 3, 'stderr': 4}, 'refused': refused,
        'proof_bytes': len(full.encode(proof)), 'wire_bytes': len(wire),
        'protected_operations': 0, 'original_acceptance': False}, sort_keys=True))


if __name__ == '__main__':
    main()
