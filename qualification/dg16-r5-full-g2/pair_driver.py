#!/usr/bin/env python3
"""Prepare or execute the full current registry through its maintained owners.

No finite registry substitution, producer edit, normalization adoption or original
acceptance occurs. --execute runs the complete legacy and DAG population serially.
Without that flag only complete-population mapping and necessary preflight run.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


"""Additional hosted custody and closed projections for the retained pair driver.

This file is concatenated before the retained driver's main by build_packet.py.
It is not a replacement verifier or a normalization contract.
"""
import fcntl
import re
import stat

PLAN_SCHEMA = 'implementaudit.verifier-pair-plan.v2'
PROC_PROFILE = 'MAINTAINED_SINGLE_PROC_PIDFD_V2_EXPLICIT_SELECTION'
OWNER_SHA256 = '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b'
SOURCE_COMMIT = '35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE = 'abe08aabc83de3b27c43e6acf28646fb089f0f34'
CHECKS = ('same_source', 'same_registry', 'same_environment', 'same_record_schema',
          'same_exit', 'same_stdout', 'same_stderr', 'route_pair', 'same_engine',
          'same_execution_cwd', 'same_compiled_stream', 'same_child_environment',
          'same_declared_repro_artifacts', 'same_stdin', 'same_dist_namespace',
          'same_portal_events', 'same_repro_events')
NODE_STATES = ('PASS', 'FAIL', 'INTERRUPTED', 'UNSETTLED')


def require(value, code):
    if not value:
        raise ValueError(code)


def stable_stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_uid,
            info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def bounded_json(path, limit=128 * 1024 * 1024):
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
            info.st_uid == os.geteuid() and info.st_size <= limit, 'PRIVATE_JSON_SHAPE')
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    raw = path.read_bytes()
    require(stable_stamp(info) == stable_stamp(path.lstat()), 'PRIVATE_JSON_CHANGED')
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('JSON_CONSTANT')))


def blob_binding(path):
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
            info.st_size <= 128 * 1024 * 1024, 'PRIVATE_FILE_SHAPE')
    raw = path.read_bytes()
    require(stable_stamp(info) == stable_stamp(path.lstat()), 'PRIVATE_FILE_CHANGED')
    return {'bytes': len(raw), 'sha256': sha(raw)}


def proc_observation():
    raw = Path('/proc/self/status').read_bytes()
    fields = {line.split(':', 1)[0]: line.split(':', 1)[1].split()
              for line in raw.decode('ascii').splitlines() if ':' in line}
    pid = os.getpid()
    require(fields.get('NSpid') == [str(pid)] and fields.get('NStgid') == [str(pid)] and
            fields.get('Threads') == ['1'] and os.listdir('/proc/self/task') == [str(pid)] and
            Path('/proc/self/stat').read_text().split(' ', 1)[0] == str(pid),
            'EXPLICIT_SINGLE_PROC_PROFILE_MISMATCH')
    return {'schema': PLAN_SCHEMA, 'profile': PROC_PROFILE, 'namespace_depth': 1,
            'threads': 1, 'actual_pid': pid, 'status_sha256': sha(raw)}


def set_environment(runtime, out):
    # Both operation and receiver acquire this exact ordinary environment.
    # No inherited event file, token, provider credential, or controller token.
    env = {
        'PATH': str(runtime) + ':/usr/bin:/bin', 'HOME': str(out / 'ordinary-home'),
        'LC_ALL': 'C', 'LANG': 'C', 'TZ': 'UTC', 'CI': 'true', 'GITHUB_ACTIONS': 'true',
        'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
        'GIT_CONFIG_SYSTEM': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1',
        'GIT_ATTR_NOSYSTEM': '1', 'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0',
        'GIT_NO_LAZY_FETCH': '1', 'GIT_NO_REPLACE_OBJECTS': '1',
    }
    os.environ.clear()
    os.environ.update(env)
    os.umask(0o077)
    return env


def load_owner(source):
    path = source / 'scripts/qualify-work-graph-verifier.py'
    raw = path.read_bytes()
    require(sha(raw) == OWNER_SHA256, 'MAINTAINED_OWNER_CHANGED')
    spec = importlib.util.spec_from_file_location('hosted_full_pair_owner', path)
    owner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = owner
    spec.loader.exec_module(owner)
    return owner


def ordinary_inventory(owner, runtime):
    tools = {name: owner.executable_identity(shutil.which(name))
             for name in ('bash', 'git', 'node', 'npx', 'python', 'python3', 'rg')}
    require(all(tools[name]['available'] for name in ('bash', 'git', 'node', 'python', 'python3', 'rg')),
            'ORDINARY_TOOL_MISSING')
    require(Path(shutil.which('python')).parent == runtime and
            Path(shutil.which('python3')).parent == runtime, 'ORDINARY_INTERPRETER_SELECTION')
    # The complete bounded venv census is an ordinary-provider bookend, not C5.
    entries = {}; total = 0; root = runtime.parent
    root_info = root.lstat()
    require(root.resolve(strict=True) == root and stat.S_ISDIR(root_info.st_mode) and
            root_info.st_uid == os.geteuid() and not root_info.st_mode & 0o022, 'ORDINARY_PROVIDER_ROOT')
    root_identity = {'device': root_info.st_dev, 'inode': root_info.st_ino, 'mode': root_info.st_mode,
                     'uid': root_info.st_uid, 'gid': root_info.st_gid}
    for parent, directories, files in os.walk(root, followlinks=False):
        here = Path(parent)
        for name in sorted(directories + files):
            path = here / name; info = path.lstat(); rel = path.relative_to(root).as_posix()
            require(info.st_uid == os.geteuid() and
                    (stat.S_ISLNK(info.st_mode) or not info.st_mode & 0o022), 'ORDINARY_PROVIDER_OWNERSHIP')
            row = {'mode': info.st_mode, 'device': info.st_dev, 'inode': info.st_ino,
                   'uid': info.st_uid, 'gid': info.st_gid, 'links': info.st_nlink}
            if stat.S_ISLNK(info.st_mode):
                row.update(kind='SYMLINK', target_sha256=sha(os.fsencode(os.readlink(path))))
                if name in directories:
                    directories.remove(name)
            elif stat.S_ISREG(info.st_mode):
                require(info.st_nlink == 1 and info.st_size <= 64 * 1024 * 1024, 'ORDINARY_PROVIDER_FILE_BOUND')
                raw = path.read_bytes(); total += len(raw)
                row.update(kind='FILE', bytes=len(raw), sha256=sha(raw))
            else:
                require(stat.S_ISDIR(info.st_mode), 'ORDINARY_PROVIDER_KIND')
                row.update(kind='DIRECTORY')
            require(stable_stamp(info) == stable_stamp(path.lstat()), 'ORDINARY_PROVIDER_CHANGED')
            entries[rel] = row
            require(len(entries) <= 8192 and total <= 128 * 1024 * 1024, 'ORDINARY_PROVIDER_AGGREGATE')
    closing = root.lstat()
    require(root_identity == {'device': closing.st_dev, 'inode': closing.st_ino, 'mode': closing.st_mode,
                             'uid': closing.st_uid, 'gid': closing.st_gid}, 'ORDINARY_PROVIDER_ROOT_CHANGED')
    return {'tools': tools, 'venv_root': root_identity, 'venv': entries, 'venv_bytes': total,
            'scope': 'ACTUAL_ORDINARY_EXECUTABLES_AND_VENV_BOOKENDS_NOT_TOOLCHAIN_CLOSURE_OR_C5'}


def raw_projection(value):
    # All public text is literal; no free-form coverage strings are forwarded.
    require(type(value) is dict and value.get('schema') == 'implementaudit.verifier-correspondence.v1' and
            value.get('normalization') == 'NONE_RAW_BYTES' and value.get('authority') == 'NONE', 'RAW_RELATION_SCHEMA')
    checks = value.get('checks')
    require(type(checks) is dict and set(checks) == set(CHECKS) and
            all(type(v) is bool for v in checks.values()), 'RAW_RELATION_PREDICATES')
    require(type(value.get('raw_observables_equal')) is bool and
            value['raw_observables_equal'] == all(checks.values()), 'RAW_RELATION_EQUALITY')
    return {'checks': {key: checks[key] for key in CHECKS},
            'raw_observables_equal': value['raw_observables_equal'],
            'normalization': 'NONE_RAW_BYTES', 'authority': 'NONE',
            'full_population_normalization_adopted': False,
            'finite_normalization_unchanged': True}


def record_projection(record, mapping):
    require(record.get('schema') == 'implementaudit.verifier-run.v4' and
            record.get('mode') in ('legacy', 'dag') and type(record.get('exit')) is int and
            type(record.get('elapsed_ms')) is int and record['elapsed_ms'] >= 0 and
            record.get('mapped_nodes') == len(mapping['nodes']) and
            type(record.get('registration_complete')) is bool, 'CAPTURE_RESULT_SCHEMA')
    names = [n['id'] for n in mapping['nodes']]
    nodes = record.get('nodes')
    require(type(nodes) is list and len(nodes) == len(names), 'CAPTURE_NODE_POPULATION')
    projected = []
    for ordinal, (name, row) in enumerate(zip(names, nodes)):
        require(type(row) is dict and set(row) == {'node', 'status', 'terminal'} and
                row['node'] == name and row['status'] in NODE_STATES and
                type(row['terminal']) is bool and row['terminal'] == (row['status'] != 'UNSETTLED'),
                'CAPTURE_NODE_STATUS')
        projected.append({'ordinal': ordinal, 'status': row['status'], 'terminal': row['terminal']})
    for key in ('stdout_sha256', 'stderr_sha256', 'registry_sha256', 'graph_digest'):
        require(type(record.get(key)) is str and re.fullmatch('[0-9a-f]{64}', record[key]), 'CAPTURE_DIGEST')
    return {'mode': record['mode'], 'exit': record['exit'], 'elapsed_ms': record['elapsed_ms'],
            'mapped_nodes': len(names), 'registration_complete': record['registration_complete'],
            'stdout_sha256': record['stdout_sha256'], 'stderr_sha256': record['stderr_sha256'],
            'registry_sha256': record['registry_sha256'], 'graph_digest': record['graph_digest'],
            'nodes': projected,
            'legacy_node_trace': 'UNAVAILABLE_WHOLE_PROCESS_ONLY' if record['mode'] == 'legacy' else 'NOT_APPLICABLE',
            'test_level_skip_semantics': 'RETAINED_IN_PRIVATE_RAW_STREAMS_NO_SYNTHETIC_PASS'}


def write_public_summary(out, result, receive=None):
    evidence = out / 'evidence'
    summary = {'schema': 'dg16.full-registry-operation.v1', 'authority': 'NONE',
        'source_commit': SOURCE_COMMIT, 'source_tree': SOURCE_TREE,
        'capture_plan_schema': PLAN_SCHEMA, 'capture_process_profile': PROC_PROFILE,
        'source_checkout': 'SAME_CHECKOUT_AS_FRESH_CONTROLLER', 'source_cloned': False,
        'normalization': 'NONE_RAW_BYTES', 'finite_normalization_unchanged': True,
        'full_population_normalization_adopted': False, 'original_acceptance': False,
        'full_G2': False, 'C5': False, 'G1': False, 'G3': False, 'full_T14': False,
        'status': 'COMPLETE_PAIR_RAW_RELATION_RECORDED' if result.get('status') ==
            'COMPLETE_CURRENT_PAIR_EXECUTED_RAW_RELATION_RECORDED' else 'INCOMPLETE_OR_FAILED_OPERATION',
        'subject_verifier_attempts': result.get('subject_verifier_attempts', 0),
        'failed_or_unsealed_attempts_are_not_received_as_complete': True,
        'receiving_status': 'NOT_RECEIVED', 'records': [], 'raw_relation': None,
        'private_raw_captures': 'LIVE_JOB_ONLY_RECEIVE_BEFORE_TEARDOWN_NO_CUSTODY_TRANSFER',
        'ordinary_toolchain_scope': 'ACTUAL_EXECUTABLE_AND_VENV_BOOKENDS_PARTIAL_NOT_C5',
        'ci_applicability': 'CANONICAL_PACKAGE_LEG_ONLY_OTHER_VALIDATE_WORKFLOW_STEPS_UNQUALIFIED'}
    require(type(summary['subject_verifier_attempts']) is int and
            0 <= summary['subject_verifier_attempts'] <= 2, 'ATTEMPT_COUNT')
    if (evidence / 'FULL_MAPPING.json').exists():
        mapping = bounded_json(evidence / 'FULL_MAPPING.json')
        tests = bounded_json(evidence / 'PHYSICAL_REGISTERED_TESTS.json')
        summary['mapping'] = {'mapped_nodes': len(mapping['nodes']), 'registered_tests': len(tests),
            'mapping': blob_binding(evidence / 'FULL_MAPPING.json'),
            'physical_tests': blob_binding(evidence / 'PHYSICAL_REGISTERED_TESTS.json'),
            'command_stream': blob_binding(evidence / 'commands.bin'),
            'exact_registry_reassembly': result.get('exact_registry_reassembly') is True}
        for mode in ('legacy', 'dag'):
            captured = out / 'captures' / mode / 'capture/result.json'
            if captured.exists():
                summary['records'].append(record_projection(bounded_json(captured), mapping))
    if (evidence / 'RAW_COMPARISON.json').exists():
        summary['raw_relation'] = raw_projection(bounded_json(evidence / 'RAW_COMPARISON.json', 65536))
    if receive is not None:
        require(receive['status'] in ('RECEIVED_COMPLETE_RAW_PAIR', 'RECEIVED_PARTIAL_FAILED_OPERATION',
                                     'NO_SEALED_CAPTURE_RECEIVED'), 'RECEIVER_STATUS')
        summary.update(receiving_status=receive['status'], records=receive['records'],
                       raw_relation=receive['raw_relation'],
                       receive_record=blob_binding(evidence / 'RECEIVING.json'),
                       same_live_source_current=receive['same_live_source_current'],
                       ordinary_toolchain_unchanged=receive['ordinary_toolchain_unchanged'])
    raw = json.dumps(summary, sort_keys=True, separators=(',', ':'), allow_nan=False).encode() + b'\n'
    require(len(raw) <= 49152, 'PUBLIC_OPERATION_BOUND')
    target = out / ('RECEIVED_PUBLIC.json' if receive is not None else 'OPERATION_PUBLIC.json')
    require(not target.exists(), 'NO_REPEAT_PUBLIC_SUMMARY')
    target.write_bytes(raw)


def receive_main(args):
    source = args.source.resolve(strict=True); out = args.out.absolute(); runtime = args.runtime_bin.absolute()
    require(out.resolve(strict=True) == out and out.parent.resolve() == out.parent, 'RECEIVE_PATH')
    evidence = out / 'evidence'; captures = out / 'captures'
    require(not (evidence / 'RECEIVING.json').exists(), 'NO_REPEAT_RECEIVING')
    set_environment(runtime, out); proc = proc_observation(); owner = load_owner(source)
    result = bounded_json(out / 'RESULT.json', 1024 * 1024)
    mapping = bounded_json(evidence / 'FULL_MAPPING.json')
    registry = (source / 'scripts/verify-package.sh').read_bytes()
    registered = owner.WG.verifier_registered_tests_v1(registry)
    physical = sorted(p.relative_to(source).as_posix() for p in (source / 'tests').glob('*.test.sh'))
    actual_mapping = owner.WG.compile_verifier_graph_v1(registry, physical, owner.environment_identity(child_resolution=True))
    require(registered == physical == bounded_json(evidence / 'PHYSICAL_REGISTERED_TESTS.json') and
            mapping == actual_mapping and b''.join(n['source'].encode() for n in mapping['nodes']) == registry and
            (evidence / 'commands.bin').read_bytes() == owner.WG.verifier_command_stream_v1(mapping, registry),
            'RECEIVER_COMPLETE_MAPPING_READBACK')
    ordinary = bounded_json(evidence / 'ORDINARY_BEFORE.json', 8 * 1024 * 1024)
    require(ordinary_inventory(owner, runtime) == ordinary, 'ORDINARY_TOOLCHAIN_CHANGED_BEFORE_RECEIVE')
    plan_path = evidence / 'PLAN.json'
    plan, file_digest, plan_digest = owner._read_verifier_pair_plan_file(plan_path)
    require(plan['schema'] == PLAN_SCHEMA, 'RECEIVE_PLAN_PROFILE')
    require(owner.verifier_preflight_currentness_v1() == plan['expected_currentness'], 'RECEIVE_CURRENTNESS')
    records = []; censuses = {}
    # Independent process calls the maintained original reader on every actual
    # sealed envelope. It never treats a result hash or author verdict as custody.
    parent = owner._capture_directory(captures)
    try:
        owner._capture_private(parent); fcntl.flock(parent, fcntl.LOCK_EX | fcntl.LOCK_NB)
        workspace, sinks = owner._capture_plan_paths(plan)
        owner._capture_parent_population(parent, workspace, sinks)
        require(not os.path.lexists(workspace), 'UNSEALED_WORKSPACE_REMAINS')
        for mode, sink in zip(('legacy', 'dag'), sinks):
            if not os.path.lexists(sink):
                continue
            capture, census = owner._read_sealed_capture(sink, plan, file_digest, plan_digest)
            record = owner.verified_record(capture)
            require(record['mode'] == mode, 'RECEIVE_MODE')
            records.append(record_projection(record, mapping)); censuses[str(capture)] = census
        for path, census in censuses.items():
            require(owner._capture_census(Path(path)) == census, 'RECEIVE_CAPTURE_CHANGED')
        require(owner.verifier_preflight_currentness_v1() == plan['expected_currentness'], 'RECEIVE_CLOSING_CURRENTNESS')
    finally:
        os.close(parent)
    raw_relation = None
    if len(records) == 2:
        with (evidence / 'receive-compare.stdout').open('w') as stdout, (evidence / 'receive-compare.stderr').open('w') as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = owner._compare_sealed_captures(captures / 'legacy', captures / 'dag',
                                                     evidence / 'RECEIVED_RAW_COMPARISON.json', plan_path)
        require(code in (0, 1), 'RAW_COMPARISON_EXIT')
        received = bounded_json(evidence / 'RECEIVED_RAW_COMPARISON.json', 65536)
        original = bounded_json(evidence / 'RAW_COMPARISON.json', 65536)
        require(received == original, 'RAW_COMPARISON_READBACK_CHANGED')
        raw_relation = raw_projection(received)
        require(code == int(not raw_relation['raw_observables_equal']), 'RAW_COMPARISON_EXIT_MISMATCH')
    require(ordinary_inventory(owner, runtime) == ordinary, 'ORDINARY_TOOLCHAIN_CHANGED_AFTER_RECEIVE')
    require(owner.verifier_preflight_currentness_v1() == plan['expected_currentness'], 'FINAL_RECEIVING_CURRENTNESS')
    complete = len(records) == 2 and all(row['exit'] == 0 for row in records) and raw_relation is not None
    receipt = {'schema': 'dg16.full-registry-live-raw-receiving.v1', 'authority': 'NONE',
        'status': 'RECEIVED_COMPLETE_RAW_PAIR' if complete else
                  'RECEIVED_PARTIAL_FAILED_OPERATION' if records else 'NO_SEALED_CAPTURE_RECEIVED',
        'records': records, 'raw_relation': raw_relation, 'proc_observation': proc,
        'same_live_source_current': True, 'ordinary_toolchain_unchanged': True,
        'captured_census_sha256': sha(json.dumps(censuses, sort_keys=True).encode()),
        'normalization': 'NONE_RAW_BYTES', 'original_acceptance': False, 'full_G2': False}
    write_json(evidence / 'RECEIVING.json', receipt)
    write_public_summary(out, result, receipt)
    print(json.dumps({'role': 'receive', 'status': receipt['status'], 'authority': 'NONE'}), flush=True)
    return 0 if complete else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--runtime-bin", required=True, type=Path)
    parser.add_argument("--node-bin", type=Path,
                        help="Explicit ordinary Node binary directory; unrelated to the fixed C5 provider")
    parser.add_argument("--expected-node-sha256",
                        help="Required exact binary digest when --node-bin is supplied")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--receive", action="store_true")
    parser.add_argument("--capture-plan-profile", required=True, choices=["single-proc-v2"])
    args = parser.parse_args()
    require(bool(args.execute) != bool(args.receive), "EXACTLY_ONE_OPERATION_ROLE")
    require(args.node_bin is None and args.expected_node_sha256 is None, "DISTRO_NODE_ONLY")
    if args.receive:
        try:
            return receive_main(args)
        except Exception:
            failure_path = args.out.absolute() / "evidence/receiver-failure.txt"
            if failure_path.parent.resolve(strict=True) == failure_path.parent and not failure_path.exists():
                with failure_path.open("x") as retained:
                    retained.write(traceback.format_exc())
            raise
    source = args.source.resolve(strict=True)
    runtime = args.runtime_bin.absolute()
    out = args.out.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError("a new output path is required")
    if out.parent.resolve() != out.parent:
        raise ValueError("output parent must be canonical")
    out.mkdir(mode=0o700)
    evidence = out / "evidence"
    evidence.mkdir(mode=0o700)
    captures = out / "captures"
    captures.mkdir(mode=0o700)
    repo = source
    (out / "ordinary-home").mkdir(mode=0o700)
    env = set_environment(runtime, out)
    proc = proc_observation()
    result = {"schema": "r4.full-current-verifier-pair.v1", "original_acceptance_delta": 0,
              "source_mutations": [], "producer_mutations": [], "normalization_adopted": False,
              "authority": "NONE", "execute_requested": args.execute}
    commands = []

    def command(label, argv, cwd):
        started = time.monotonic_ns()
        p = subprocess.run([str(x) for x in argv], cwd=cwd, env=env, capture_output=True)
        (evidence / (label + ".stdout")).write_bytes(p.stdout)
        (evidence / (label + ".stderr")).write_bytes(p.stderr)
        commands.append({"label": label, "argv": [str(x) for x in argv],
                         "returncode": p.returncode, "elapsed_ns": time.monotonic_ns() - started,
                         "stdout_sha256": sha(p.stdout), "stderr_sha256": sha(p.stderr)})
        write_json(evidence / "COMMANDS.json", commands)
        if p.returncode:
            raise RuntimeError(label + " refused: " + p.stderr.decode(errors="replace"))
        return p.stdout

    try:
        selected_node = shutil.which("node", path=env["PATH"])
        if selected_node is None:
            raise ValueError("complete verifier needs Node; supply its explicit ordinary binary directory and digest before launch")
        node_path = Path(selected_node).resolve(strict=True)
        if not node_path.is_file():
            raise ValueError("selected Node is not a regular file")
        node_digest = sha(node_path.read_bytes())
        if args.expected_node_sha256 and node_digest != args.expected_node_sha256:
            raise ValueError("selected Node binary differs from the expected digest")
        node_version = command("ordinary-node-version", [node_path, "--version"], source).decode().strip()
        result["ordinary_node"] = {"path": str(node_path), "sha256": node_digest,
                                   "bytes": node_path.stat().st_size, "version": node_version,
                                   "fixed_C5_provider_modified": False}
        prior = command("input-status", ["git", "status", "--porcelain=v1", "--untracked-files=all"], source)
        if prior:
            raise ValueError("complete pair requires a clean input checkout")
        # The exact source checkout already owns the fresh current controller. No clone.
        command("fsck", ["git", "fsck", "--full", "--strict"], repo)
        result["source_commit"] = command("commit", ["git", "rev-parse", "HEAD"], repo).decode().strip()
        result["source_tree"] = command("tree", ["git", "rev-parse", "HEAD^{tree}"], repo).decode().strip()
        require(result["source_commit"] == SOURCE_COMMIT and result["source_tree"] == SOURCE_TREE, "EXACT_PUBLIC_SOURCE_REQUIRED")
        owner = load_owner(repo)
        ordinary_before = ordinary_inventory(owner, runtime)
        write_json(evidence / "ORDINARY_BEFORE.json", ordinary_before)
        write_json(evidence / "PROC_OBSERVATION.json", proc)
        registry = (repo / "scripts/verify-package.sh").read_bytes()
        registered = owner.WG.verifier_registered_tests_v1(registry)
        physical = sorted(p.relative_to(repo).as_posix() for p in (repo / "tests").glob("*.test.sh"))
        if registered != physical:
            raise ValueError("current registry differs from physical test population")
        environment = owner.environment_identity(child_resolution=True)
        mapping = owner.WG.compile_verifier_graph_v1(registry, physical, environment)
        stream = owner.WG.verifier_command_stream_v1(mapping, registry)
        if b"".join(node["source"].encode() for node in mapping["nodes"]) != registry:
            raise ValueError("mapping does not reconstruct every exact registry byte")
        write_json(evidence / "FULL_MAPPING.json", mapping)
        write_json(evidence / "PHYSICAL_REGISTERED_TESTS.json", physical)
        (evidence / "commands.bin").write_bytes(stream)
        current = owner.verifier_preflight_currentness_v1()
        capture = {"retain_repro_assets": True, "stdin_file": None, "empty_stdin": True,
                   "capture_dist": True, "capture_portal_events": True, "retain_repro_events": True}
        plan = {"schema": PLAN_SCHEMA, "expected_currentness": current,
                "runs": [{"mode": mode, "output": str(captures / "work"),
                          "retention": str(captures / mode),
                          "base_environment_sha256": current["base_environment_sha256"],
                          "capture": capture} for mode in ("legacy", "dag")]}
        plan_path = evidence / "PLAN.json"
        write_json(plan_path, plan)
        with (evidence / "preflight.stdout").open("w") as stdout, (evidence / "preflight.stderr").open("w") as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                preflight_code = owner.preflight_verifier_pair_file_v1(plan_path)
        result.update(mapped_nodes=len(mapping["nodes"]), registered_tests=len(registered),
                      registration_complete=True, registry_bytes=len(registry), registry_sha256=sha(registry),
                      exact_registry_reassembly=True, preflight_exit=preflight_code,
                      subject_verifier_attempts=0, status="FULL_POPULATION_PREFLIGHT_ONLY")
        child_preflight = owner._CaptureChildren()
        child_preflight.close()
        if preflight_code:
            raise RuntimeError("maintained full-population pair preflight refused")
        write_json(out / "RESULT.json", result)
        if args.execute:
            result["runs"] = []
            started = time.monotonic_ns()
            for mode in ("legacy", "dag"):
                print("full current " + mode + " begin", flush=True)
                begin = time.monotonic_ns()
                result["subject_verifier_attempts"] += 1
                write_json(out / "RESULT.json", result)
                with (evidence / (mode + ".stdout")).open("w") as stdout, (evidence / (mode + ".stderr")).open("w") as stderr:
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = owner.run(mode, captures / "work", **capture, retention_plan=plan_path)
                result["runs"].append({"mode": mode, "exit": code, "elapsed_ns": time.monotonic_ns() - begin})
                write_json(out / "RESULT.json", result)
                if code and mode == "legacy":
                    raise RuntimeError("complete " + mode + " verifier returned " + str(code))
            result["pair_elapsed_ns"] = time.monotonic_ns() - started
            with (evidence / "compare.stdout").open("w") as stdout, (evidence / "compare.stderr").open("w") as stderr:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = owner._compare_sealed_captures(captures / "legacy", captures / "dag",
                                                         evidence / "RAW_COMPARISON.json", plan_path)
            result["raw_comparison_exit"] = code
            # A terminal nonzero DAG still has two sealed captures. Retain
            # their original raw comparison before declaring subject failure
            # so the separate receiver can validate the partial outcome.
            failed = next((row for row in result["runs"] if row["exit"]), None)
            if failed is not None:
                raise RuntimeError("complete " + failed["mode"] + " verifier returned " + str(failed["exit"]))
            result["status"] = "COMPLETE_CURRENT_PAIR_EXECUTED_RAW_RELATION_RECORDED"
            result["raw_equality_is_not_normative_acceptance"] = True
        after = command("input-status-after", ["git", "status", "--porcelain=v1", "--untracked-files=all"], source)
        if after != prior:
            raise ValueError("input source status changed")
        result["input_source_status_unchanged"] = True
        require(ordinary_inventory(owner, runtime) == ordinary_before, "ORDINARY_TOOLCHAIN_CHANGED_AFTER_OPERATION")
        result["ordinary_toolchain_unchanged"] = True
    except BaseException as exc:
        result.update(status="REFUSED_OR_FAILED", failure={"type": type(exc).__name__, "message": str(exc)})
        (evidence / "failure.txt").write_text(traceback.format_exc())
    write_json(out / "RESULT.json", result)
    write_public_summary(out, result)
    print(json.dumps({"role": "execute", "status": result["status"], "authority": "NONE"}), flush=True)
    return int(result["status"] == "REFUSED_OR_FAILED")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Exception, KeyboardInterrupt):
        print("FULL_REGISTRY_DRIVER_REFUSED", flush=True)
        raise SystemExit(1)
