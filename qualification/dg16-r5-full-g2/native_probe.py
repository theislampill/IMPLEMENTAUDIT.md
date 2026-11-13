#!/usr/bin/env python3
"""Prospective focused native qualification, never invoked by author controls.

The two maintained case bodies are unchanged. Recording wraps their actual
commands and native observations without replacing a result, graph or owner.
All raw evidence remains private. The supervising host owns process custody.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import sys
import traceback
import types
import unittest

IO_SHA256='c2f8d718c8acd3a223d494239e6bc19d4a90e3d5c66f49cdac8f701ce4807075'
PROFILE_SHA256 = 'c16c75039b938718ab4bfee9e49a6c55322bdfda22f25d0a526cf74f87944c3d'
SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
RECEIVER = 'scripts/operational-evidence.py'
CASE_SOURCE = 'tests/work-graph-original14-receiving-cases.py'
SOURCE_PINS = {
    COMPILER: (262144, '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'),
    RECEIVER: (422801, '5950164adb0e0e1d9c6ff4481ccb43cbff94a13ae1fb6578fb6a172a431e69ed'),
    CASE_SOURCE: (10298, '629dceb22be9f066e63c5fdc41e4359749e4809aca8d56102fa02456d4e32e82'),
}
TESTS = ('test_native_intake_uses_current_original14_not_retired_root',
         'test_native_intake_later_boundary_prevents_return')
BANK_TESTS = ('test_actual_later_invalidation_prevents_return', 'test_derivative_snapshot_change_after_use_prevents_return', 'test_native_intake_later_boundary_prevents_return', 'test_native_intake_rejects_opaque_fixture_work_graph', 'test_native_intake_rejects_unowned_nested_record', 'test_native_intake_uses_current_original14_not_retired_root', 'test_protected_document_change_after_use_prevents_return', 'test_real_original14_documents_reach_unchanged_graph_parser', 'test_valid_original14_owner_does_not_supply_missing_graph_document')
MAX_TOTAL = 64 * 1024**2
MAX_FILE = 4 * 1024**2
MAX_ENTRIES = 4096


class _Recorder:
    """Reserve the complete private population before any owned emission.

    Ordinary members leave the existing per-file allowance and one entry for
    RESULT.json. Directories, including the output root, count as entries.
    Reservations survive an incomplete write and stop all later emission.
    """
    def __init__(self, evidence, output):
        self.E = evidence
        self.output = output
        self.used = 0
        self.files = {}
        self.directories = {'.'}
        self.finished = False
        self.failed = False
        self.E.need(MAX_FILE <= MAX_TOTAL and MAX_ENTRIES >= 2,
                    'NATIVE_PROBE_RECORDER_BOUND')

    def save(self, name, raw):
        self._emit(name, raw, final=False)

    def finish(self, raw):
        self._emit('RESULT.json', raw, final=True)

    def _emit(self, name, raw, *, final):
        E = self.E
        E.need(not self.finished and not self.failed, 'NATIVE_PROBE_RECORDER_CLOSED')
        E.safe_name(name)
        parts = PurePosixPath(name)
        E.need(name == 'RESULT.json' if final else bool(parts.parts) and parts.parts[0] != 'RESULT.json',
               'NATIVE_PROBE_RESULT_RESERVED')
        E.need(type(raw) is bytes and len(raw) <= MAX_FILE, 'NATIVE_PROBE_RAW_BOUND')
        parents = {parent.as_posix() for parent in parts.parents}
        E.need(name not in self.files and name not in self.directories
               and not any(parent in self.files for parent in parents),
               'NATIVE_PROBE_MEMBER_COLLISION')
        reserved_bytes = 0 if final else MAX_FILE
        reserved_entries = 0 if final else 1
        E.need(self.used + len(raw) + reserved_bytes <= MAX_TOTAL, 'NATIVE_PROBE_RAW_BOUND')
        E.need(len(self.files) + 1 + len(self.directories) + len(parents - self.directories)
               + reserved_entries <= MAX_ENTRIES, 'NATIVE_PROBE_ENTRY_BOUND')
        descriptor = dict(bytes=len(raw), sha256=E.sha(raw))
        # Charge before mkdir or write. An exception conservatively leaves the
        # entire reservation held, including directories not yet created.
        self.used += len(raw)
        self.files[name] = descriptor
        self.directories.update(parents)
        self.finished = final
        self.failed = True
        path = self.output / name
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        E.write_once(path, raw, MAX_FILE)
        self.failed = False

    def check_census(self, index):
        E = self.E
        E.need(not self.failed and type(index) is dict
               and set(index) == {'files', 'directories', 'total_bytes'}
               and type(index['files']) is dict and type(index['directories']) is dict
               and type(index['total_bytes']) is int, 'NATIVE_PROBE_CENSUS_SHAPE')
        E.need(set(index['files']) == set(self.files)
               and set(index['directories']) == self.directories
               and ('RESULT.json' in index['files']) == self.finished
               and index['total_bytes'] == self.used <= MAX_TOTAL
               and len(index['files']) + len(index['directories']) <= MAX_ENTRIES,
               'NATIVE_PROBE_CENSUS_POPULATION')
        for name, expected in self.files.items():
            row = index['files'][name]
            E.need(type(row) is dict
                   and {key: row.get(key) for key in ('bytes', 'sha256')} == expected,
                   'NATIVE_PROBE_CENSUS_BODY')


def helpers():
    path = Path(__file__).with_name('evidence_io.py')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != IO_SHA256:
        raise ValueError('NATIVE_PROBE_IO_PIN')
    module = types.ModuleType('native_probe_evidence_io')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    if module.read_packet(path, MAX_FILE) != raw:
        raise ValueError('NATIVE_PROBE_IO_CHANGED')
    return module


def load_exact(path, name, raw):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def profile(evidence):
    path = Path(__file__).with_name('native_profile.py')
    raw = evidence.read_packet(path, 65536)
    evidence.need(evidence.sha(raw) == PROFILE_SHA256, 'G2_NATIVE_PROFILE_PIN')
    module = types.ModuleType('ordinary_g2_native_profile')
    module.__file__ = str(path)
    module.__dict__['_HOST_EVIDENCE_IO'] = evidence
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def run(source, output, *, current_host_bank=False):
    selected_tests = BANK_TESTS if current_host_bank else TESTS
    E = helpers()
    P = profile(E)
    process_before = P.observe_process()
    E.need(source.is_absolute() and output.is_absolute() and not output.exists()
           and not output.is_relative_to(source), 'NATIVE_PROBE_FRESH_PRIVATE_OUTPUT')
    recorder = _Recorder(E, output)
    output.mkdir(mode=0o700)
    sys.dont_write_bytecode = True
    os.chdir(source)
    def save(name, raw):
        recorder.save(name, raw)

    def source_rows():
        rows = {}
        for name, (count, digest) in SOURCE_PINS.items():
            row = E.file_record(source / name, MAX_FILE)
            E.need((row['bytes'], row['sha256']) == (count, digest), 'NATIVE_PROBE_SOURCE_PIN')
            rows[name] = row
        return rows

    save('HOST_OPEN.json', E.encode(process_before))
    before = source_rows()
    save('SOURCE_OPEN.json', E.encode(before))
    compiler_raw = E.read(source / COMPILER, MAX_FILE)
    compiler = load_exact(source / COMPILER, 'focused_current_compiler', compiler_raw)
    owner, path, receiver_raw = compiler._native_static_owner_module_v1()
    E.need(path == source / RECEIVER and E.sha(receiver_raw) == SOURCE_PINS[RECEIVER][1],
           'NATIVE_FIXED_RECEIVER_ACTUAL_PATH')
    save('FIXED_RECEIVER.json', E.encode(dict(schema='dg16.actual-fixed-receiver.v1',
        compiler=before[COMPILER], receiver=before[RECEIVER], actual_path=str(path),
        actual_body_sha256=E.sha(receiver_raw), physical_loader_returned=True,
        closing=source_rows(), source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE)))

    wrong_root = output / 'wrong-source'
    save('wrong-source/' + COMPILER, compiler_raw)
    wrong_raw = bytes([receiver_raw[0] ^ 1]) + receiver_raw[1:]
    save('wrong-source/' + RECEIVER, wrong_raw)
    wrong_compiler = load_exact(wrong_root / COMPILER, 'focused_wrong_receiver_compiler', compiler_raw)
    try:
        wrong_compiler._native_static_owner_module_v1()
    except wrong_compiler.WorkGraphError as exc:
        E.need(str(exc) == 'native static source owner is unavailable or changed'
               and isinstance(exc.__cause__, OSError), 'NATIVE_WRONG_RECEIVER_OTHER_FAILURE')
        wrong_error = dict(type=type(exc).__name__, message=str(exc), cause=type(exc.__cause__).__name__)
    else:
        raise E.Refusal('NATIVE_WRONG_RECEIVER_ACCEPTED')
    save('WRONG_RECEIVER.json', E.encode(dict(schema='dg16.actual-wrong-receiver.v1',
        compiler_sha256=E.sha(compiler_raw), expected_receiver_sha256=E.sha(receiver_raw),
        wrong_receiver_sha256=E.sha(wrong_raw), wrong_receiver_bytes=len(wrong_raw),
        fixture='wrong-source', actual_refusal=wrong_error, product_source_edited=False)))

    module = load_exact(source / CASE_SOURCE, 'focused_maintained_original14', E.read(source / CASE_SOURCE))
    if current_host_bank:
        population = [test._testMethodName for test in unittest.defaultTestLoader.loadTestsFromTestCase(module.Original14GraphReceiving)]
        E.need(population == list(BANK_TESTS), 'G2_CURRENT_HOST_BANK_POPULATION_CHANGED')
    original_command = module.READER.command
    original_read = module.NATIVE.wg.read_native_run_v1
    original_observe = module.NATIVE.wg.observe_native_run_v1
    active = {'name': None, 'commands': [], 'observations': [], 'graphs': [], 'serial': 0}

    def artifact(kind, raw):
        ordinal = active['serial']
        active['serial'] += 1
        E.need(ordinal < 2048, 'NATIVE_CASE_RECORD_BOUND')
        name = 'cases/' + active['name'] + '/' + ('%04d-' % ordinal) + kind
        save(name, raw)
        return name

    def recorded_command(argv, cwd, data=None):
        result = original_command(argv, cwd, data)
        out = artifact('stdout.raw', result.stdout)
        err = artifact('stderr.raw', result.stderr)
        row = dict(argv=[str(x) for x in argv], cwd=str(cwd), returncode=result.returncode,
                   stdout=out, stderr=err, stdout_sha256=E.sha(result.stdout), stderr_sha256=E.sha(result.stderr),
                   input_bytes=0 if data is None else len(data), input_sha256=E.sha(b'' if data is None else data))
        active['commands'].append(artifact('command.json', E.encode(row)))
        return result

    def recorded_read(*args, **kwargs):
        graph = original_read(*args, **kwargs)
        active['graphs'].append(artifact('native-graph.json', E.encode(graph)))
        return graph

    @contextlib.contextmanager
    def recorded_observe(*args, **kwargs):
        opened = None
        try:
            with original_observe(*args, **kwargs) as raw:
                E.need(type(raw) is bytes, 'NATIVE_OBSERVATION_ACTUAL_BYTES_REQUIRED')
                opened = artifact('native-observation.json', raw)
                yield raw
        except BaseException as exc:
            row = dict(opened=opened, status='REFUSED', exception_type=type(exc).__name__,
                       message=str(exc), message_sha256=E.sha(str(exc).encode()))
            active['observations'].append(artifact('native-close.json', E.encode(row)))
            raise
        else:
            active['observations'].append(artifact('native-close.json', E.encode(dict(opened=opened, status='CLOSED'))))

    module.READER.command = recorded_command
    module.NATIVE.wg.read_native_run_v1 = recorded_read
    module.NATIVE.wg.observe_native_run_v1 = recorded_observe
    rows = []
    for name in selected_tests:
        active.update(name=name, commands=[], observations=[], graphs=[], serial=0)
        test = module.Original14GraphReceiving(name)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite([test]))
        text = stream.getvalue().encode('utf-8', 'replace')
        runner = artifact('runner.txt', text)
        row = dict(test=name, outcome='PASS' if result.wasSuccessful() and result.testsRun == 1
                   and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses else 'FAIL',
                   tests_run=result.testsRun, runner=runner, commands=list(active['commands']),
                   native_graphs=list(active['graphs']), native_observations=list(active['observations']),
                   diagnostic_bytes=len(text), diagnostic_sha256=E.sha(text))
        rows.append(row)
        if row['outcome'] != 'PASS':
            break  # No extra case after a failed prerequisite.
    process_after = P.observe_process()
    E.need(process_after == process_before, 'G2_NATIVE_PROCESS_CLOSING_CHANGED')
    save('HOST_CLOSE.json', E.encode(process_after))
    after = source_rows()
    E.need(after == before, 'NATIVE_PROBE_SOURCE_CLOSING_CHANGED')
    save('SOURCE_CLOSE.json', E.encode(after))
    index = E.census(output, file_bytes=MAX_FILE, total_bytes=MAX_TOTAL, entries=MAX_ENTRIES)
    recorder.check_census(index)
    members = {name: {key: row[key] for key in ('bytes', 'sha256')}
               for name, row in index['files'].items()}
    value = dict(schema=('dg16.current-host-native-bank-actual-result.v1' if current_host_bank else 'dg16.focused-native-actual-result.v1'), authority='NONE',
                 source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, test_population=list(selected_tests),
                 tests_run=len(rows), success=len(rows) == len(selected_tests) and all(r['outcome'] == 'PASS' for r in rows),
                 rows=rows, members=members, fixed_receiver='FIXED_RECEIVER.json', wrong_receiver='WRONG_RECEIVER.json',
                 before='SOURCE_OPEN.json', after='SOURCE_CLOSE.json', source_unchanged=True,
                 recording_scope='ACTUAL_MAINTAINED_CASE_COMMAND_STREAMS_AND_NATIVE_RETURN_OR_CLOSE',
                 original_awards=[])
    raw = E.encode(value)
    recorder.finish(raw)
    closing = E.census(output, file_bytes=MAX_FILE, total_bytes=MAX_TOTAL, entries=MAX_ENTRIES)
    recorder.check_census(closing)
    # The actual body manifest stays private; even the parent capture has a
    # small closed return. Its descriptor cannot substitute for the body.
    parent = dict(schema='dg16.focused-native-parent-return.v1',
                  result_bytes=len(raw), result_sha256=E.sha(raw),
                  success=value['success'], tests_run=value['tests_run'],
                  source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE)
    sys.stdout.buffer.write(E.encode(parent))
    sys.stdout.buffer.flush()
    return 0 if value['success'] else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--current-host-bank', action='store_true')
    args = parser.parse_args()
    return run(args.source.absolute(), args.output.absolute(), current_host_bank=args.current_host_bank)


if __name__ == '__main__':
    raise SystemExit(main())
