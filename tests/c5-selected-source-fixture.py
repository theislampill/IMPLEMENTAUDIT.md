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
CURRENT_LOADER = (61142, '378844cf42ccd83009b0f1b0b42c800b2f303eb9a3ac0f4709a72788f2414943')
HISTORICAL_LOADER = (
    'test-support/r5-windows-capture-history/d2747b7-source/' + LOADER,
    39282, '042cf21f807ce52ac3522285458f1c0407415c1f0883370f1d73404abd9e97d1')
OLD_QUALIFIER = '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b'
RETAINED_V3_QUALIFIER = 'cff5376a90dbffdd18e762234c59b62285d8a26d35a916243a085bcf99c48b4c'
CURRENT_QUALIFIER = '79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
MODES = ('HISTORICAL_HOSTED_READER', 'R4_CURRENT', 'R5_RETAINED_V3', 'R5_CURRENT_V4',
    'R5_CURRENT_BUILDER_V10', 'R5_CURRENT_COMPILER_V11')
# R5_CURRENT_V4 keeps its original name: it is the frozen V4 tuple with its
# historical base. Only R5_CURRENT_BUILDER_V10 selects the actual builder.
# R5_CURRENT_BUILDER_V10 keeps its name too: it is the frozen V10 tuple with the
# 8754 compiler. Only R5_CURRENT_COMPILER_V11 selects the actual compiler.
R5_MODES = ('R5_RETAINED_V3', 'R5_CURRENT_V4', 'R5_CURRENT_BUILDER_V10', 'R5_CURRENT_COMPILER_V11')
DG17_COMPOSED_COMPILER = 'cfaea1e33fdbcdda6c883c0a1883673166f7feefedfd29d509f90288664ff7a6'
HISTORICAL_R5_BASE = '15e71318bfb65427e5f5bb49bd0a7e6f5cf4460618ef1b64d3d598b447646e97'
CURRENT_BUILDER_BASE = '5963c8779ebc1717fd120f44ab21b10386e86e3afe66c644526fe4cc9d7bbc26'
HISTORIES = ('R4_BUILD_CACHE_PHYSICAL_HISTORY', 'R4_INITIALIZATION_PHYSICAL_HISTORY',
    'R5_WINDOWS_INITIALIZATION_PHYSICAL_HISTORY', 'R5_WINDOWS_CAPTURE_PHYSICAL_HISTORY',
    'R5_HOSTED_PHYSICAL_HISTORY', 'R5_CONTINUITY_COMPILER_PHYSICAL_HISTORY',
    'R5_DG17_COMPOSED_COMPILER_PHYSICAL_HISTORY')
# HISTORIES names production-declared physical history; these mappings are shared.
# RETAINED below adds fixture-only substitutions without changing production pins.
# Neither path searches the repository for a convenient matching hash.
RETAINED = {
    (QUALIFIER, RETAINED_V3_QUALIFIER):
        'test-support/r5-c5-source-history/source5c7e/' + QUALIFIER,
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
    if (name == owner.EXECUTOR and revision is not None
            and revision in (getattr(owner, 'R5_BUDGET5_BUILDER_SOURCE_REVISION', None),
                             getattr(owner, 'R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION', None))
            and pin == owner.R5_RUNTIME_DIRECTORY_MODE_EXECUTOR_SHA256):
        # Mirrors the loader's explicit V8-V11 executor member; no search.
        physical = owner.R5_RUNTIME_DIRECTORY_MODE_EXECUTOR_MEMBER
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
        require(owner.R5_INNER_CAPTURE_PINS[owner.R5_HOSTED_BASE_SELECTION] == HISTORICAL_R5_BASE,
                'historical base distinction')
        if mode in ('R5_CURRENT_BUILDER_V10', 'R5_CURRENT_COMPILER_V11'):
            revision = owner.R5_BUDGET5_BUILDER_SOURCE_REVISION
            require(revision == 'R5_HOSTED_UBUNTU24_BUDGET5_BUILDER_SOURCE_20261113_V10',
                    'current builder revision')
            current = dict(owner.R5_BUDGET5_BUILDER_PINS)
            require(owner.R5_BUDGET5_BUILDER_BASE_SELECTION != owner.R5_HOSTED_BASE_SELECTION
                    and owner.R5_HOSTED_BASE_SELECTION not in current
                    and current.pop(owner.R5_BUDGET5_BUILDER_BASE_SELECTION) == CURRENT_BUILDER_BASE
                    and current.pop(owner.R5_BUDGET5_BUILDER_EXECUTION_SELECTION, None) is not None
                    and current == {name: pin for name, pin in owner.R5_DG17_COMPOSED_PINS.items()
                        if name not in (owner.R5_HOSTED_BASE_SELECTION,
                                        owner.R5_RUNTIME_DIRECTORY_MODE_EXECUTION_SELECTION)},
                    'current/historical builder base distinction')
            require(owner.R5_BUDGET5_BUILDER_PINS[COMPILER] == DG17_COMPOSED_COMPILER
                    and dict(owner.R5_DG17_COMPOSED_COMPILER_PHYSICAL_HISTORY)[COMPILER][1] == DG17_COMPOSED_COMPILER,
                    'frozen V9-V10 compiler distinction')
        if mode == 'R5_CURRENT_COMPILER_V11':
            revision = owner.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION
            require(revision == 'R5_HOSTED_UBUNTU24_DG17_OWNER_TEMPORARY_SOURCE_20261114_V11',
                    'current compiler revision')
            require(owner.R5_DG17_OWNER_TEMPORARY_PINS[COMPILER] != DG17_COMPOSED_COMPILER
                    and dict(owner.R5_DG17_OWNER_TEMPORARY_PINS) == dict(owner.R5_BUDGET5_BUILDER_PINS,
                        **{COMPILER: owner.R5_DG17_OWNER_TEMPORARY_COMPILER_SHA256}),
                    'current/historical compiler distinction')
        selections = [(owner.R5_HOSTED_PROFILE, revision)]
    plan = {}
    selected_base = None
    for profile, revision in selections:
        pins, base, _, _, _ = owner._selection(profile, revision)
        require(len(pins) == 12 and pins[QUALIFIER] ==
                (CURRENT_QUALIFIER if mode in ('R5_CURRENT_V4', 'R5_CURRENT_BUILDER_V10', 'R5_CURRENT_COMPILER_V11') else
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
    if mode in R5_MODES:
        selection = json.loads(buffers[base][0])
        members = set(selection['programs']) | set(selection['payload_sources'])
        require(len(members) <= 96, 'producer/payload member bound')
        for name in sorted(members):
            if name not in buffers:
                if name == COMPILER:
                    # A frozen tuple (V3, V4, V10) keeps its logical compiler
                    # in the same frozen tuple as its retained owner.
                    selected = next(row for row in plan.values() if row['logical'] == COMPILER)
                    buffers[name] = buffers[selected['physical']]
                else:
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
