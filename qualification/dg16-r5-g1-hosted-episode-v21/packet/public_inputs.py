"""Pinned public-input selector for the V21 G1/G3 hosted episode.

Owner amendment (Nov 25) replaces the encrypted carrier and private sender with
public, disposable inputs. This module is the only acquisition route: it reads
the exact index beside it and the exact bodies under public-inputs/. It has no
network, subprocess, credential, carrier, sender or native call. Any role or
contract item that only Root or an appointed receiver can supply is an explicit
HELD row; the first HELD row refuses with a distinct code before any body is
read and therefore before clone, setup, NSS change, controller creation or any
native call. A HELD row is never satisfied by this program.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

INDEX_NAME = 'PUBLIC_INPUT_INDEX.json'
INDEX_SHA256 = '6c324578a41cdbdbbce7afee412bc3f7352f42794070274f365d90d1b5a2bca6'
INPUT_DIR = 'public-inputs'
SCHEMA = 'dg16.v21-public-input-index.v1'
SOURCE_COMMIT = '6d2c0c3522ce128ea8143d7fc93e1180f46227f8'
SOURCE_TREE = 'a0c86d6a71e1f8b9ac3aed2d7c984ac79aeef26e'
SUBJECT = {'commit': SOURCE_COMMIT, 'tree': SOURCE_TREE}
ROLES = tuple(str(n) for n in range(1, 12))
PRESENT = 'PRESENT'
HELD = 'HELD_PENDING_ROOT_DECISION'
ASSEMBLED_WITH_HELD = 'ASSEMBLED_WITH_HELD_SUBRECORD'
STATES = (PRESENT, HELD, ASSEMBLED_WITH_HELD)
CONTRACT_HOLDS = ('G1_HOST_PROFILE_ADOPTION_ROUTE', 'BOOTSTRAP_ADMISSION', 'NATIVE_V21_REVISION')
MAX_INDEX = 65536
MAX_BODY = 1024 * 1024
MAX_TOTAL = 4 * 1024 * 1024
ROW_PRESENT = {'role', 'name', 'state', 'issuer', 'issuer_field', 'subject_field', 'bytes', 'sha256', 'origin'}
ROW_HELD = {'role', 'name', 'state', 'owner', 'decision_ref', 'expected_issuer'}
ROW_ASSEMBLED = ROW_PRESENT | {'held_subrecords'}
SUPPORT_ROW = {'name', 'support_of', 'bytes', 'sha256', 'origin'}
HOLD_ROW = {'name', 'state', 'owner', 'decision_ref'}


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'PUBLIC_INPUT_DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal('PUBLIC_INPUT_NONFINITE')))
    except (UnicodeError, json.JSONDecodeError):
        raise Refusal('PUBLIC_INPUT_JSON') from None


def _mark(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_uid, s.st_gid)


def read_exact(path, maximum):
    """Bounded no-follow read of one ordinary file with closing identity."""
    path = Path(path)
    for parent in reversed(path.absolute().parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode), 'PUBLIC_INPUT_PARENT_ALIAS')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= maximum,
         'PUBLIC_INPUT_ORDINARY_FILE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(_mark(os.fstat(fd)) == _mark(before), 'PUBLIC_INPUT_OPEN_CHANGED')
        raw = os.pread(fd, maximum + 1, 0)
        need(len(raw) == before.st_size and _mark(os.fstat(fd)) == _mark(before)
             and _mark(path.lstat()) == _mark(before), 'PUBLIC_INPUT_CAPTURE_CHANGED')
        return raw
    finally:
        os.close(fd)


def _name(value):
    need(type(value) is str and re.fullmatch(r'[A-Z][A-Z0-9_]{0,95}\.json', value) is not None,
         'PUBLIC_INPUT_NAME')
    return value


def _digest(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'PUBLIC_INPUT_DIGEST')
    return value


def held_code(kind, key):
    if kind == 'role':
        return 'PUBLIC_INPUT_HELD_ROLE_%02d' % int(key)
    return 'PUBLIC_INPUT_HELD_CONTRACT_' + key


def load_index(packet):
    raw = read_exact(Path(packet) / INDEX_NAME, MAX_INDEX)
    need(re.fullmatch('[0-9a-f]{64}', INDEX_SHA256) is not None and sha(raw) == INDEX_SHA256,
         'PUBLIC_INPUT_INDEX_PIN')
    value = parse(raw)
    need(type(value) is dict and set(value) == {'schema', 'authority', 'subject', 'route', 'carrier_selected',
         'private_sender_selected', 'roles', 'support', 'contract_holds', 'original_awards'},
         'PUBLIC_INPUT_INDEX_FIELDS')
    need(value['schema'] == SCHEMA and value['authority'] == 'NONE' and value['subject'] == SUBJECT
         and value['route'] == 'PINNED_PUBLIC_CHECKOUT_DIRECTORY' and value['carrier_selected'] is False
         and value['private_sender_selected'] is False and value['original_awards'] == [],
         'PUBLIC_INPUT_INDEX_SCOPE')
    roles = value['roles']
    need(type(roles) is dict and set(roles) == set(ROLES), 'PUBLIC_INPUT_ROLE_POPULATION')
    names = set()
    for key, row in roles.items():
        need(type(row) is dict and row.get('role') == int(key) and row.get('state') in STATES,
             'PUBLIC_INPUT_ROLE_ROW')
        fields = ROW_HELD if row['state'] == HELD else ROW_ASSEMBLED if row['state'] == ASSEMBLED_WITH_HELD else ROW_PRESENT
        need(set(row) == fields, 'PUBLIC_INPUT_ROLE_FIELDS')
        _name(row['name'])
        need(row['name'] not in names, 'PUBLIC_INPUT_NAME_REUSED')
        names.add(row['name'])
        if row['state'] == HELD:
            need(all(type(row[k]) is str and 0 < len(row[k]) <= 512 for k in ('owner', 'decision_ref', 'expected_issuer')),
                 'PUBLIC_INPUT_HELD_ROW')
        else:
            need(type(row['bytes']) is int and 0 < row['bytes'] <= MAX_BODY, 'PUBLIC_INPUT_BODY_BOUND')
            _digest(row['sha256'])
            need(type(row['issuer']) is str and row['issuer_field'] in (None, 'issuer', 'receiver')
                 and row['subject_field'] in (None, 'subject', 'product', 'recorded_subject', 'source'),
                 'PUBLIC_INPUT_PROVENANCE_ROW')
            if row['state'] == ASSEMBLED_WITH_HELD:
                held = row['held_subrecords']
                need(type(held) is dict and held and all(type(h) is dict and set(h) == {'state', 'owner', 'decision_ref'}
                     and h['state'] == HELD for h in held.values()), 'PUBLIC_INPUT_SUBRECORD_ROW')
    support = value['support']
    need(type(support) is list and len(support) <= 8, 'PUBLIC_INPUT_SUPPORT_POPULATION')
    for row in support:
        need(type(row) is dict and set(row) == SUPPORT_ROW and type(row['support_of']) is int
             and str(row['support_of']) in ROLES and roles[str(row['support_of'])]['state'] != HELD,
             'PUBLIC_INPUT_SUPPORT_ROW')
        _name(row['name'])
        need(row['name'] not in names and type(row['bytes']) is int and 0 < row['bytes'] <= MAX_BODY,
             'PUBLIC_INPUT_SUPPORT_ROW')
        _digest(row['sha256'])
        names.add(row['name'])
    holds = value['contract_holds']
    need(type(holds) is dict and set(holds) <= set(CONTRACT_HOLDS), 'PUBLIC_INPUT_CONTRACT_POPULATION')
    for key, row in holds.items():
        need(type(row) is dict and set(row) == HOLD_ROW and row['name'] == key and row['state'] == HELD,
             'PUBLIC_INPUT_CONTRACT_ROW')
    return raw, value


def first_held(value):
    """Deterministic order: roles 1..11, then each role's held subrecord, then contract holds."""
    for key in ROLES:
        if value['roles'][key]['state'] == HELD:
            return held_code('role', key)
    for key in ROLES:
        if value['roles'][key]['state'] == ASSEMBLED_WITH_HELD:
            return held_code('role', key)
    for key in CONTRACT_HOLDS:
        if key in value['contract_holds']:
            return held_code('contract', key)
    return None


def held_report(value):
    rows = []
    for key in ROLES:
        row = value['roles'][key]
        if row['state'] == HELD:
            rows.append(dict(code=held_code('role', key), owner=row['owner'], decision_ref=row['decision_ref']))
        elif row['state'] == ASSEMBLED_WITH_HELD:
            for name, sub in row['held_subrecords'].items():
                rows.append(dict(code=held_code('role', key), subrecord=name, owner=sub['owner'],
                                 decision_ref=sub['decision_ref']))
    for key in CONTRACT_HOLDS:
        if key in value['contract_holds']:
            row = value['contract_holds'][key]
            rows.append(dict(code=held_code('contract', key), owner=row['owner'], decision_ref=row['decision_ref']))
    return rows


def _provenance(row, body):
    parsed = parse(body)
    need(type(parsed) is dict, 'PUBLIC_INPUT_BODY_SHAPE')
    if row['issuer_field'] is not None:
        need(parsed.get(row['issuer_field']) == row['issuer'], 'PUBLIC_INPUT_ISSUER_MISMATCH')
    if row['subject_field'] is not None:
        retained_roles=(2,3,4,5,6,7,9,10,11)
        expected_subject={'commit': '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', 'tree': '53498df783ed441744ae5080982c2d5e59c34bbc'} if row['role'] in retained_roles else SUBJECT
        subject = parsed.get(row['subject_field'])
        need(type(subject) is dict and {k: subject.get(k) for k in ('commit', 'tree')} == expected_subject,
             'PUBLIC_INPUT_SUBJECT_MISMATCH')
    return parsed


def admit(packet):
    """Return exact bodies by role, or refuse. Never reads a body while any row is HELD."""
    packet = Path(packet)
    raw, value = load_index(packet)
    held = first_held(value)
    if held is not None:
        raise Refusal(held)
    source_bridge(packet)  # explicit issued relation before any retained-subject use
    need(not (packet / 'carrier').exists() and not (packet / 'private-inputs').exists(),
         'PUBLIC_INPUT_CARRIER_OR_PRIVATE_ROUTE_PRESENT')
    directory = packet / INPUT_DIR
    info = directory.lstat()
    need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode), 'PUBLIC_INPUT_DIRECTORY')
    expected = {row['name'] for row in value['roles'].values()} | {row['name'] for row in value['support']}
    present = set()
    for child in directory.iterdir():
        need(child.name in expected, 'PUBLIC_INPUT_EXTRA_BODY')
        present.add(child.name)
    need(present == expected, 'PUBLIC_INPUT_MISSING_BODY')
    bodies, support, total = {}, {}, 0
    for key in ROLES:
        row = value['roles'][key]
        body = read_exact(directory / row['name'], MAX_BODY)
        need(len(body) == row['bytes'], 'PUBLIC_INPUT_BYTE_MISMATCH')
        need(sha(body) == row['sha256'], 'PUBLIC_INPUT_DIGEST_MISMATCH')
        _provenance(row, body)
        total += len(body)
        bodies[int(key)] = body
    for row in value['support']:
        body = read_exact(directory / row['name'], MAX_BODY)
        need(len(body) == row['bytes'], 'PUBLIC_INPUT_BYTE_MISMATCH')
        need(sha(body) == row['sha256'], 'PUBLIC_INPUT_DIGEST_MISMATCH')
        parse(body)
        total += len(body)
        support[row['name']] = body
    need(total <= MAX_TOTAL, 'PUBLIC_INPUT_TOTAL_BOUND')
    need(read_exact(packet / INDEX_NAME, MAX_INDEX) == raw, 'PUBLIC_INPUT_INDEX_CLOSING_CHANGED')
    return dict(index_sha256=sha(raw), index=value, bodies=bodies,
                names={int(k): r['name'] for k, r in value['roles'].items()}, support=support)



SOURCE_ADMISSION_OWNER_SHA256 = 'c3bf9d26cf1e25131c90432f525efa93bee2f3fc5cb57591ee728224bfce5f7d'

def source_bridge(packet=None, *, source=None):
    import types
    owner=Path(__file__).with_name('source_admission.py')
    raw=read_exact(owner,1024*1024)
    need(sha(raw)==SOURCE_ADMISSION_OWNER_SHA256,'SOURCE_ADMISSION_OWNER_PIN')
    module=types.ModuleType('exact_successor_source_admission');module.__file__=str(owner)
    exec(compile(raw,str(owner),'exec'),module.__dict__)
    need(read_exact(owner,1024*1024)==raw,'SOURCE_ADMISSION_OWNER_CHANGED')
    return module.receive(Path(__file__).parent if packet is None else Path(packet),source=source)
