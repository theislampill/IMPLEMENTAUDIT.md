"""Exact disposable source fixtures for the selected composite C5 tests.

These copies exercise declared historical or current source tuples. They never
change the product source, replace a loader guard, or confer host/native evidence.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import types

LOADER = 'scripts/load-work-graph-c5-executor.py'
QUALIFIER = 'scripts/qualify-work-graph-verifier.py'
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
OLD_COMPILER = '3649a8dc856e29ce11b6daa5861351cc1c21bf9c7a9b4f5a2ddde12108d8581f'
CURRENT_COMPILER = '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
CURRENT_LOADER = (49927, '2989ba6cb8da6f52f9a2f94f27d141a931a0bffb8ebd03172091b170646d8017')
HISTORICAL_LOADER = (
    'test-support/r5-windows-capture-history/d2747b7-source/' + LOADER,
    39282, '042cf21f807ce52ac3522285458f1c0407415c1f0883370f1d73404abd9e97d1')
OLD_QUALIFIER = '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b'
RETAINED_V3_QUALIFIER = 'cff5376a90dbffdd18e762234c59b62285d8a26d35a916243a085bcf99c48b4c'
CURRENT_QUALIFIER = '79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
MODES = ('HISTORICAL_HOSTED_READER', 'R4_CURRENT', 'R5_RETAINED_V3', 'R5_CURRENT_V4')
HISTORIES = ('R4_BUILD_CACHE_PHYSICAL_HISTORY', 'R4_INITIALIZATION_PHYSICAL_HISTORY',
    'R5_WINDOWS_INITIALIZATION_PHYSICAL_HISTORY', 'R5_WINDOWS_CAPTURE_PHYSICAL_HISTORY',
    'R5_HOSTED_PHYSICAL_HISTORY')
# Each historical substitution is explicit and belongs to this fixture only.
# The production loader's historical pin table and refusal on current bytes stay
# unchanged; no fallback searches the repository for a convenient matching hash.
RETAINED = {
    (COMPILER, OLD_COMPILER):
        'test-support/r5-c5-source-history/source0d579/' + COMPILER,
    (QUALIFIER, OLD_QUALIFIER):
        'test-support/r5-c5-source-history/source0d579/' + QUALIFIER,
    ('scripts/work-graph-c5-inputs.py', 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e'):
        'test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-inputs.py',
    ('scripts/work-graph-c5-provider-inputs.py', '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776'):
        'test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-provider-inputs.py',
    ('scripts/work-graph-c5-executor.py', 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d'):
        'test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-executor.py',
    ('skills/implementaudit/scripts/compile-work-graph.py', '62c3b0fb95bbf006ef81e981a16325395e6165ae65c901f667de0e60bf74de3c'):
        'test-support/r5-windows-capture-history/d2747b7-source/skills/implementaudit/scripts/compile-work-graph.py',
}


def require(value, message):
    if not value:
        raise ValueError('C5 selected-source fixture: ' + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def relative(value):
    require(type(value) is str, 'member name type')
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and value
            and not any(part in ('', '.', '..') for part in path.parts), 'member path')
    return value


def read_member(source, name, expected=None):
    path = source / relative(name)
    first = path.lstat()
    require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
            and 0 < first.st_size <= 1024**2 and stat.S_IMODE(first.st_mode) in (0o644, 0o755),
            'ordinary source member')
    identity = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        require(identity(os.fstat(fd)) == identity(first), 'member changed at open')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(1024**2 + 1)
        require(identity(first) == identity(os.fstat(fd)) == identity(path.lstat())
                and len(raw) == first.st_size, 'member changed')
    finally:
        os.close(fd)
    require(expected is None or sha(raw) == expected, 'selected member digest')
    return raw, stat.S_IMODE(first.st_mode)


def owner_buffer(source, mode):
    require(mode in MODES, 'unknown selection mode')
    if mode == 'HISTORICAL_HOSTED_READER':
        name, size, digest = HISTORICAL_LOADER
    else:
        name, (size, digest) = LOADER, CURRENT_LOADER
    raw, permissions = read_member(source, name, digest)
    require(len(raw) == size, 'loader size')
    return raw, permissions


def physical_member(owner, name, pin, profile, revision):
    physical = name
    if name == owner.GATE and revision == owner.R4_COMPOSED_SOURCE_REVISION:
        physical = owner.R4_COPY_GATE_MEMBER
    for attribute in HISTORIES:
        history = getattr(owner, attribute, {})
        retained = history.get(name)
        if retained is not None and retained[1] == pin:
            physical = retained[0]
    return relative(physical)


def selected_plan(owner, mode):
    require(mode in MODES and owner.LOADER == LOADER and owner.QUALIFIER == QUALIFIER,
            'loader roles')
    if mode == 'HISTORICAL_HOSTED_READER':
        selections = [(owner.R4_BUILD_CACHE_PROFILE, owner.R5_WINDOWS_INITIALIZATION_SOURCE_REVISION),
            (owner.R4_BUILD_CACHE_PROFILE, owner.R4_INITIALIZATION_SOURCE_REVISION),
            (owner.R4_BUILD_CACHE_PROFILE, owner.R4_BUILD_CACHE_SOURCE_REVISION)]
    elif mode == 'R4_CURRENT':
        selections = [(owner.CURRENT_PROFILE, owner.R4_COMPOSED_SOURCE_REVISION)]
    else:
        require(owner.R5_QUALIFIER_REPAIR_SOURCE_REVISION ==
                'R5_HOSTED_UBUNTU24_QUALIFIER_REPAIR_SOURCE_20261106_V2', 'current revision')
        require(dict(owner.R5_QUALIFIER_REPAIR_PINS) == dict(owner.R5_HOSTED_PINS, **{QUALIFIER: RETAINED_V3_QUALIFIER})
                and owner.R5_HOSTED_PINS[QUALIFIER] == OLD_QUALIFIER, 'current/historical qualifier distinction')
        require(owner.R5_CONTINUITY_RECEIVER_SOURCE_REVISION ==
                'R5_HOSTED_UBUNTU24_CONTINUITY_RECEIVER_SOURCE_20261106_V3', 'current receiver revision')
        require(dict(owner.R5_CONTINUITY_RECEIVER_PINS) ==
                dict(owner.R5_QUALIFIER_REPAIR_PINS, **{COMPILER: CURRENT_COMPILER})
                and owner.R5_QUALIFIER_REPAIR_PINS[COMPILER] == OLD_COMPILER,
                'current/historical compiler distinction')
        require(owner.R5_INNER_CAPTURE_SOURCE_REVISION ==
                'R5_HOSTED_UBUNTU24_INNER_CAPTURE_SOURCE_20261107_V4', 'current inner-capture revision')
        require(dict(owner.R5_INNER_CAPTURE_PINS) ==
                dict(owner.R5_CONTINUITY_RECEIVER_PINS, **{QUALIFIER: CURRENT_QUALIFIER}),
                'current/retained V3 owner distinction')
        revision = (owner.R5_INNER_CAPTURE_SOURCE_REVISION if mode == 'R5_CURRENT_V4'
                    else owner.R5_CONTINUITY_RECEIVER_SOURCE_REVISION)
        selections = [(owner.R5_HOSTED_PROFILE, revision)]
    plan = {}
    selected_base = None
    for profile, revision in selections:
        pins, base, _, _, _ = owner._selection(profile, revision)
        require(len(pins) == 12 and pins[QUALIFIER] ==
                (CURRENT_QUALIFIER if mode == 'R5_CURRENT_V4' else
                 RETAINED_V3_QUALIFIER if mode == 'R5_RETAINED_V3' else OLD_QUALIFIER), 'selected tuple')
        selected_base = base
        for name, pin in pins.items():
            physical = physical_member(owner, name, pin, profile, revision)
            source_name = RETAINED.get((name, pin), physical)
            row = dict(logical=name, physical=physical, source=relative(source_name), sha256=pin)
            require(physical not in plan or plan[physical] == row, 'conflicting selected physical member')
            plan[physical] = row
    return plan, selected_base


def write_plan(source, destination, mode, owner, loader_raw, loader_permissions):
    """Copy only the exact finite plan; also used by source-only inert controls."""
    size, digest = HISTORICAL_LOADER[1:] if mode == 'HISTORICAL_HOSTED_READER' else CURRENT_LOADER
    require(type(loader_raw) is bytes and len(loader_raw) == size and sha(loader_raw) == digest
            and loader_permissions in (0o644, 0o755), 'selected loader buffer')
    plan, base = selected_plan(owner, mode)
    buffers = {LOADER: (loader_raw, loader_permissions)}
    for name, row in plan.items():
        buffers[name] = read_member(source, row['source'], row['sha256'])
    if mode in ('R5_RETAINED_V3', 'R5_CURRENT_V4'):
        selection = json.loads(buffers[base][0])
        members = set(selection['programs']) | set(selection['payload_sources'])
        require(len(members) <= 96, 'producer/payload member bound')
        for name in sorted(members):
            if name not in buffers:
                buffers[relative(name)] = read_member(source, name)
    require(0 < len(buffers) <= 128 and sum(len(raw) for raw, _ in buffers.values()) <= 8 * 1024**2,
            'fixture population/byte bound')
    require(not destination.exists(), 'destination already exists')
    destination.mkdir(mode=0o700, parents=True)
    rows = []
    for name, (raw, permissions) in sorted(buffers.items()):
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        path.chmod(permissions)
        require(read_member(destination, name) == (raw, permissions), 'copy readback')
        rows.append(dict(path=name, bytes=len(raw), sha256=sha(raw), mode=permissions))
    return dict(mode=mode, members=rows, source_changed=False, authority='NONE')


def materialize(source, destination, mode):
    source, destination = Path(source), Path(destination)
    raw, permissions = owner_buffer(source, mode)
    owner = types.ModuleType('c5_selected_fixture_declarations')
    owner.__file__ = str(source / LOADER)
    # This is test fixture execution of the exact selected loader buffer, never
    # a product fallback. Its later _Engine still enforces the unmodified pins.
    exec(compile(raw, owner.__file__, 'exec'), owner.__dict__)
    return write_plan(source, destination, mode, owner, raw, permissions)
