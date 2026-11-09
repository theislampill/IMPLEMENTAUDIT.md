"""Root data-only current04 G3 packet intake; never issues a decision.

inspect reconstructs original receiver-02 evidence and returns its requirements.
check-body validates an already-issued Root body and exact witness-file hashes.
Neither command authenticates a reviewer/Root actor from a JSON label or hash.
No provider call, live proof-consumer entry, native observation or write occurs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import types

READER = Path('/home/agent/dg16-g1-current04-operators/public-receiver-02/author/receiver.py')
READER_SHA = '378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
PHASE_SHA = '7a391c1c74329b1298349a85d3df25013707d0eb09044cf8583b3ea8bc9a038c'
PROOF_SHA = '53275d8fb0b0c78db86e697d833401348e0dd8ce503f813e13870267d0ef906c'
G3_SHA = '15f65bc76ae990a215dafc30240c7bd8485748ca38d4adc35a99e3331c7d3342'
SOURCE = '7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE = '6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(raw):
    return dict(bytes=len(raw), sha256=digest(raw))


def stamp(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_uid, s.st_gid,
            s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def ordinary(path, maximum, expected=None, source=False):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'CANONICAL_INPUT')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
         0 < before.st_size <= maximum, 'BOUNDED_REGULAR_INPUT')
    if source:
        need(before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) in (0o400, 0o444),
             'INSTALLED_SOURCE_OWNER_MODE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd)) == stamp(before) and not os.listxattr(fd), 'INPUT_OPEN_CHANGED')
        raw = os.pread(fd, before.st_size + 1, 0)
        need(len(raw) == before.st_size and stamp(os.fstat(fd)) == stamp(before) == stamp(path.lstat())
             and path.resolve(strict=True) == path, 'INPUT_CLOSING_CHANGED')
        if expected is not None:
            need(digest(raw) == expected, 'EXACT_INPUT_PIN')
        return raw
    finally:
        os.close(fd)


def receiver():
    need(sys.platform == 'linux' and sys.flags.isolated and sys.dont_write_bytecode
         and os.getuid() == os.geteuid() > 0, 'NONROOT_ISOLATED_LINUX_DATA_READER')
    raw = ordinary(READER, 1024**2, READER_SHA, source=True)
    m = types.ModuleType('exact_current04_root_packet_reader')
    m.__file__ = str(READER)
    exec(compile(raw, str(READER), 'exec'), m.__dict__)
    return m


def sources(R):
    s = R.Sources()
    need(s.sources['phase']['sha256'] == PHASE_SHA and s.P.SOURCE_COMMIT == SOURCE
         and s.P.SOURCE_TREE == TREE, 'CURRENT04_SOURCE_SCOPE')
    need(digest(s.body(R.CORE + 'proof_consumer.py')) == PROOF_SHA
         and digest(s.body(R.CORE + 'g3_receiving.py')) == G3_SHA, 'EXACT_G3_PROOF_OWNERS')
    return s


def recorded_receiving(R, s, path, initial=None, actual_first=None):
    session = R.Session(Path(path), s)
    raw = R.read(session.path / 'RECEIVING.json')
    saved = R.parse(raw)
    need(R.encode(saved) == raw, 'CANONICAL_RECORDED_RECEIVING')
    got = session.receive(saved['observed_unix_ms'], previous=initial,
                          actual_root_raw=actual_first, save=False)
    need(R.encode(got['receipt']) == raw, 'ACTUAL_RECORDED_RECEIVING_CHANGED')
    return got, descriptor(raw)


def intake(R, s, session, initial_session=None, first_root_body=None):
    previous = None
    previous_pin = None
    first = None
    if initial_session is not None:
        previous, previous_pin = recorded_receiving(R, s, initial_session)
        need(previous['phase'] == 'g3_initial', 'INITIAL_PHASE_REQUIRED')
    if first_root_body is not None:
        first = ordinary(first_root_body, 8192)
    got, pin = recorded_receiving(R, s, session, previous, first)
    need(got['phase'] in ('g3_initial', 'g3_final'), 'ONLY_ACTUAL_G3_PACKET')
    if got['phase'] == 'g3_initial':
        need(previous is None and first is None, 'NO_INITIAL_AUXILIARY_INPUTS')
    else:
        need(previous is not None and first is not None, 'EXACT_INITIAL_AND_ORIGINAL_ROOT_BODY_REQUIRED')
    return got, pin, previous_pin, first


def inspect(R, s, got, pin, previous_pin, first, now):
    req = R.requirements(s, got)
    key = 'ROOT_REQUEST.json' if got['phase'] == 'g3_initial' else 'FINAL_REQUEST.json'
    request = R.parse(got['files'][key])
    out = dict(schema='dg16.current04.actual-packet-data-intake.v1', authority='NONE',
         phase=got['phase'], context=got['context'], receiving=pin,
         actual_request=descriptor(got['files'][key]),
         source=dict(receiver_sha256=READER_SHA, phase_sha256=PHASE_SHA,
                     proof_consumer_sha256=PROOF_SHA, g3_sha256=G3_SHA),
         requirements=req, inspected_unix_ms=now,
         current_request_window_open=request['issued_unix_ms'] <= now < request['expires_unix_ms'],
         remaining_ms=request['expires_unix_ms'] - now,
         independent_review_or_root_decision_issued=False, effect_grant=False,
         live_proof_consumer_executed_by_this_helper=False,
         provider_root_reviewer_authentication='EXTERNAL_ACTUAL_PROVENANCE_REQUIRED_NOT_SUPPLIED_BY_HASHES')
    if got['phase'] == 'g3_initial':
        out['evidence_ceiling'] = 'SCOPED_COMPONENT_RETURN_CONSUMPTION_ONLY; ORIGINAL_AWARDS_ZERO'
        out['full_raw_G1_events_externally_read'] = 0
    else:
        proof = R.parse(got['files']['INDEPENDENT_PROOF_RECEIPT.json'])
        out.update(initial_receiving=previous_pin, actual_first_root_body=descriptor(first),
             validated_host_mechanical_receipt=descriptor(got['files']['INDEPENDENT_PROOF_RECEIPT.json']),
             proof_body_descriptors=len(proof['proof_bodies']),
             support_body_descriptors=len(proof['support_bodies']),
             consumer_elapsed_ns=proof['elapsed_ns'],
             recorded_final_remaining_ms=proof['final_decision_remaining_ms'],
             private_proof_bodies_exported_in_this_public_packet=False,
             evidence_ceiling='AUTHENTICATED_SOURCE_BOUND_HOST_MECHANICAL_RECEIPT_PLUS_ACTUAL_EXTERNAL_REVIEW_REQUIRED',
             forced_residuals=['CURRENT04_L04_REMAINS_UNACCEPTED_IN_THIS_COMPONENT',
                'COMPLETE_G3_GATE_CANNOT_BE_ACCEPTED_WHILE_L04_IS_UNACCEPTED',
                'NO_GLOBAL_LIVENESS_OR_RETIREMENT_OR_FULL_G2_OR_WHOLE_DG16_AWARD'])
    return out


def check_body(R, s, got, body, now, independent_review, source_review=None):
    # Root supplies the actual semantic review files. Their provenance is an
    # outside obligation; matching a hash alone never authenticates a reviewer.
    need(independent_review is not None, 'ACTUAL_EXTERNAL_REVIEW_FILE_REQUIRED')
    review = ordinary(independent_review, 1024**2)
    value = R.validate_control(s, got, body, now)
    pins = dict(independent_review=descriptor(review))
    if got['phase'] == 'g3_final':
        need(source_review is not None, 'ACTUAL_SOURCE_APPLICABILITY_FILE_REQUIRED')
        source = ordinary(source_review, 1024**2)
        need(value['independent_review_sha256'] == digest(review)
             and value['source_applicability_review_sha256'] == digest(source), 'FINAL_ACTUAL_REVIEW_BODY_JOIN')
        pins['source_applicability'] = descriptor(source)
    else:
        need(source_review is None, 'NO_UNBOUND_INITIAL_SOURCE_REVIEW')
    return dict(schema='dg16.current04.actual-root-body-data-validation.v1', authority='NONE',
                phase=got['phase'], context=got['context'], body=descriptor(body), review_files=pins,
                validated_unix_ms=now, original_schema_and_request_bindings_valid=True,
                external_review_and_root_authority_authenticated_by_helper=False,
                root_body_created=False, effect_grant=False, original_awards=[])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('inspect', 'check-body'))
    p.add_argument('--session', required=True, type=Path)
    p.add_argument('--initial-session', type=Path)
    p.add_argument('--first-root-body', type=Path)
    p.add_argument('--body', type=Path)
    p.add_argument('--independent-review', type=Path)
    p.add_argument('--source-applicability-review', type=Path)
    a = p.parse_args()
    R = receiver()
    s = sources(R)
    got, pin, prior_pin, first = intake(R, s, a.session, a.initial_session, a.first_root_body)
    now = time.time_ns() // 1000000
    if a.mode == 'inspect':
        need(a.body is None and a.independent_review is None and a.source_applicability_review is None,
             'INSPECTION_NEVER_ISSUES_REVIEW_OR_BODY')
        out = inspect(R, s, got, pin, prior_pin, first, now)
    else:
        need(a.body is not None, 'ACTUAL_ROOT_BODY_FILE_REQUIRED')
        body = ordinary(a.body, 8192 if got['phase'] == 'g3_initial' else 16384)
        out = check_body(R, s, got, body, now, a.independent_review, a.source_applicability_review)
    sys.stdout.buffer.write(R.encode(out))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        sys.stderr.write('CURRENT04_G3_ACTUAL_PACKET_DATA_INTAKE_REFUSED\n')
        raise SystemExit(1)
