"""Private acquisition-only projection at the exact V7 directory mode gate.

Call only in a separately selected diagnostic process after equivalent setup.
The caller supplies the module returned by the maintained load_selected.
No CLI, provisioning, file writes, namespace construction, or producer call.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import types

EXECUTOR_SHA = 'b2ca6122d61d3238c853fdbf1d1c6b23e7808b2dbd18e241d41e3b310c44145a'
SOURCE = {
    'source_commit': '64219c67e9f1dc1e54c6be9ed8e56f26ab313606',
    'source_tree': '1dacef701f3999d1f7990311c96c546446e092f7',
}
MODE_REFUSAL = 'C5 selected image directory mode differs from its fixed profile'
MODE_POLICY = {'default': 0o755, 'exceptions': {}}


def _encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def _project(topology, entry_limit, byte_limit, mode_failed):
    directories = topology['directories']
    if type(directories) is not dict or not 0 < len(directories) <= entry_limit:
        raise ValueError('C5 mode diagnostic directory population differs')
    record = dict(
        schema='dg16.c5-private-selected-directory-modes.v1',
        authority='NONE',
        source=dict(SOURCE),
        executor_sha256=EXECUTOR_SHA,
        first_topology_only=True,
        captured_directories=len(directories),
        layout_mode_gate='REFUSED' if mode_failed else 'PASSED',
        original_failure=MODE_REFUSAL if mode_failed else None,
        stop='BEFORE_SECOND_TOPOLOGY_LAUNCHER_OR_IMAGE',
        private_mismatch_rows=[],
    )
    # Bound serialization before making the complete byte buffer. No partial
    # projection is returned if any row cannot be represented under the cap.
    used = len(_encode(record))
    rows = record['private_mismatch_rows']
    for name, stamp in sorted(directories.items()):
        mode = stat.S_IMODE(stamp[2])
        if mode == MODE_POLICY['default']:
            continue
        path = PurePosixPath(name)
        if not path.is_absolute() or str(path) != name or '..' in path.parts or name.startswith('//'):
            raise ValueError('C5 mode diagnostic physical path differs')
        row = dict(path=name, mode=format(mode, '04o'), expected='0755')
        used += len(_encode(row)) + 1
        if used > byte_limit:
            raise ValueError('C5 exact mode diagnostic exceeds inherited manifest bound')
        rows.append(row)
    if bool(rows) is not mode_failed:
        raise ValueError('C5 mode diagnostic disagrees with original mode guard')
    output = _encode(record)
    if len(output) > byte_limit:
        raise ValueError('C5 exact mode diagnostic exceeds inherited manifest bound')
    return output


def observe_acquisition_to_layout(engine, source):
    """Return private report bytes with the exact original refusal text.

    Every original pre-layout operation runs. Only the boundary after the
    first layout call is intercepted in a private function namespace.
    """
    raw = engine.SOURCES[engine.EXECUTOR][0]
    if (hashlib.sha256(raw).hexdigest() != EXECUTOR_SHA
            or engine.PROFILE != engine.R5_HOSTED_PROFILE
            or engine.SPEC['directory_mode_policy'] != MODE_POLICY
            or not engine.default_acl_enabled()):
        raise ValueError('C5 mode diagnostic selected source or policy differs')
    original = engine.GenuineC5Session._acquire
    namespace = dict(original.__globals__)
    layout = namespace['runtime_layout']
    if layout is not engine.runtime_layout:
        raise ValueError('C5 mode diagnostic layout owner differs')
    entry_limit = engine.P.RUNTIME_BOUNDS['entries']
    byte_limit = engine.P.MANIFEST_BOUND

    class LayoutBoundary(Exception):
        pass

    def observe_layout(runtime, topology):
        try:
            layout(runtime, topology)
        except ValueError as error:
            if str(error) != MODE_REFUSAL:
                raise
            report = _project(topology, entry_limit, byte_limit, True)
            raise LayoutBoundary(report) from None
        raise LayoutBoundary(_project(topology, entry_limit, byte_limit, False))

    namespace['runtime_layout'] = observe_layout
    acquire = types.FunctionType(original.__code__, namespace, original.__name__)
    # Only the two fields consumed by the exact acquisition method are bound.
    # Do not construct a session, create its output, or invoke run/_image.
    subject = types.SimpleNamespace(source=Path(source), expected_source=dict(SOURCE))
    try:
        acquire(subject)
    except LayoutBoundary as stop:
        return stop.args[0]
    raise AssertionError('C5 mode diagnostic acquisition skipped the layout boundary')
