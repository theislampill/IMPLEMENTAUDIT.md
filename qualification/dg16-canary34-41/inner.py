#!/usr/bin/env python3
"""One hosted wrapper observation. No full-pair, recipient, crypto or acceptance."""
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).absolute().parent
COMMIT = '205aeab7c93299b0666b261485ab5658d8e183de'
TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
BRANCH = 'refs/heads/pro/dg16-g2-canary-34-41-r3-20261114'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
LIMIT = 128 * 1024**2
CANARY_COMMAND = ['/usr/bin/bash', 'tests/native-work-graph.test.sh']


def need(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, maximum):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
             'SOURCE_FILE_TYPE_OR_BOUND')
        chunks, total = [], 0
        while total <= maximum:
            block = os.read(fd, min(1024**2, maximum + 1 - total))
            if not block:
                break
            chunks.append(block)
            total += len(block)
        raw = b''.join(chunks)
        after = os.fstat(fd)
        identity = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_nlink, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
        need(len(raw) == before.st_size and identity(before) == identity(after), 'SOURCE_FILE_CHANGED')
        return raw
    finally:
        os.close(fd)


def load(name, pins, **injected):
    path = HERE / (name + '.py')
    raw = read(path, 1024**2)
    need(dict(bytes=len(raw), sha256=sha(raw)) == pins[path.name], 'MODULE_PIN')
    spec = importlib.util.spec_from_file_location('canary_' + name, path)
    module = importlib.util.module_from_spec(spec)
    module.__dict__.update(injected)
    sys.modules[spec.name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def context(environment):
    need(environment.get('GITHUB_REPOSITORY') == REPOSITORY and
         environment.get('GITHUB_REF') == BRANCH and
         environment.get('GITHUB_EVENT_NAME') == 'push' and
         environment.get('GITHUB_RUN_ATTEMPT') == '1' and
         environment.get('GITHUB_RUN_ID', '').isdigit(), 'HOSTED_CONTEXT_REFUSED')
    return {k: environment[k] for k in ('GITHUB_REPOSITORY', 'GITHUB_REF', 'GITHUB_EVENT_NAME',
                                       'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_SHA')}


def check_source(owner, manifest):
    observed = owner.source_identity(read_only=True)
    need((observed['head'], observed['tree']) == (COMMIT, TREE), 'PRODUCT_IDENTITY')
    need(manifest['commit'] == COMMIT and manifest['tree'] == TREE, 'MANIFEST_IDENTITY')
    expected = {r['path']: r for r in manifest['members']}
    need(len(expected) == manifest['file_count'] == 1766 and
         set(observed['members']) == set(expected) and
         observed['status_digest'] == sha(b''), 'PRODUCT_POPULATION')
    for name, row in expected.items():
        actual = observed['members'][name]
        need(actual.get('tracked') is True and actual.get('bytes') == row['bytes'] and
             actual.get('sha256') == row['sha256'] and
             actual.get('mode') == (int(row['mode'], 8) & 0o7777), 'PRODUCT_MEMBER')
    return observed


def selected_profile(profile):
    need(profile['source_commit'] == COMMIT and profile['source_tree'] == TREE and
         profile['slot_count'] == 111 and len(profile['slots']) == 111, 'REPORT_SOURCE')
    selected = copy.deepcopy(profile)
    selected['slots'] = selected['slots'][34:42]
    need([x['test_count'] for x in selected['slots']] == [5, 15, 24, 9, 26, 22, 7, 20], 'REPORT_DENOMINATORS')
    for index, row in enumerate(selected['slots']):
        need(row['ordinal'] == 34 + index and row['wrapper'] == 'tests/native-work-graph.test.sh',
             'REPORT_SELECTION')
        row['ordinal'] = index
    selected['slot_count'] = 8
    return selected


def write(path, value):
    raw = (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()
    need(len(raw) <= 65536, 'PUBLIC_REPORT_BOUND')
    with path.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def write_private(path,raw):
    need(not path.exists(),'PRIVATE_MEMBER_ALREADY_EXISTS')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o600)


# Exact original helper body except the three explicitly Root-approved command-role expressions.
require = need

@contextlib.contextmanager
def ordinary_verifier_child_mask(owner, mode):
    """Only the original verifier fork child gets022; private parent stays077."""
    require(mode == 'canary', 'ORDINARY_CHILD_MODE')
    parent=os.getpid();original_fork=owner.os.fork
    launch_code=owner._CaptureChildren.launch.__code__;calls=[0]
    def parent_mask():
        rows=[line.split()[1] for line in Path('/proc/self/status').read_text().splitlines() if line.startswith('Umask:')]
        require(len(rows)==1 and int(rows[0],8)==0o077, 'PRIVATE_PARENT_UMASK')
    parent_mask()
    def product_fork():
        frame=sys._getframe(1)
        command=frame.f_locals.get('command')
        expected=['/usr/bin/bash','tests/native-work-graph.test.sh']
        require(os.getpid()==parent and frame.f_code is launch_code and
                type(frame.f_locals.get('self')) is owner._CaptureChildren and
                type(command) is list and command[:2]==expected and
                len(command)==2 and calls[0]==0,
                'ORIGINAL_VERIFIER_FORK_ONLY')
        parent_mask();calls[0]+=1
        pid=original_fork()
        if pid==0:
            os.umask(0o022)
        return pid
    owner.os.fork=product_fork
    try:
        yield
    finally:
        owner.os.fork=original_fork
        parent_mask()






def execute(source, output, public_context=None):
    episode = context(os.environ if public_context is None else public_context)
    dependencies_raw = read(HERE / 'DEPENDENCIES.json', 32768)
    dependencies = json.loads(dependencies_raw)
    pins = dependencies['files']
    # Complete source dependency readback before executing any of those modules.
    for name, descriptor in pins.items():
        raw = read(HERE / name, 2 * 1024**2)
        need(dict(bytes=len(raw), sha256=sha(raw)) == descriptor, 'DEPENDENCY_PIN')
    U = load('host_utility', pins)
    E = load('evidence_io', pins)
    P = load('native_profile', pins, _HOST_EVIDENCE_IO=E)
    H = load('host_inventory', pins, _PROFILE=P)
    C = load('checkout_prepare', pins)
    R = load('full_output_relation', pins)
    # New job produces actual host facts here. No prior fact packet or freshness timer.
    if public_context is not None:
        os.environ.clear()
        os.environ.update(C.intended_environment(Path('/usr/bin'), output))
        os.environ.update({k: public_context[k] for k in ('ImageOS','ImageVersion')})
    paths, host_before = H.inventory(U)
    need(all(hasattr(os, x) for x in ('pidfd_open', 'memfd_create', 'P_PIDFD')),
         'REQUIRED_PYTHON_BINDINGS_ABSENT')
    owner = C.load_owner(source, U.checked_file)
    manifest = json.loads(read(HERE / 'SOURCE_MANIFEST.json', 1024**2))
    profile = selected_profile(json.loads(read(HERE / 'REPORT_SLOTS.json', 2 * 1024**2)))
    need(not R.required_report_live_flags(profile), 'UNEXPECTED_LIVE_REPORT_GUARD')
    need(not output.exists() and output.is_absolute() and source.is_absolute() and
         source != output and source not in output.parents, 'FRESH_OUTPUT_REQUIRED')
    output.mkdir(mode=0o700)
    private = output / 'private'
    private.mkdir(mode=0o700)
    public = output / 'public'
    public.mkdir(mode=0o700)
    (output / 'ordinary-home').mkdir(mode=0o700)
    # Reuse the maintained sole gc.auto correction before any source Git context.
    # Its complete-context environment has these original private path roles.
    (private / 'ordinary-venv' / 'bin').mkdir(mode=0o700, parents=True)
    (private / 'full-pair' / 'ordinary-home').mkdir(mode=0o700, parents=True)
    preparation = C.initial_record()
    try:
        C.prepare(source, output, preparation, U.checked_file, write_private)
        C.readback(output, preparation, U.checked_file)
    except BaseException:
        # Preserve the maintained refusal/ambiguous mutation disposition as data.
        C.validate_record(preparation)
        write(public / 'RESULT.json', dict(schema='dg16.hosted-wrapper-canary.v1',
            authority='NONE', original_awards=[], source_commit=COMMIT, source_tree=TREE,
            status='UNQUALIFIED', phase='CHECKOUT_PREPARATION', episode=episode,
            checkout_preparation=preparation, wrapper_run=False))
        raise
    before = check_source(owner, manifest)
    environment = C.intended_environment(Path('/usr/bin'), output)
    actual_environment = owner.environment_identity(environment, child_resolution=True)
    owner.validate_child_resolution(actual_environment)
    # The maintained host validator pins /usr/bin/python3 -> /usr/bin/python3.14.
    # Refuse any earlier `python` resolution that could change the wrapper interpreter.
    import shutil
    first = shutil.which('python', path=environment['PATH']) or shutil.which('python3', path=environment['PATH'])
    need(first is not None and Path(first).resolve() == Path(paths['python3']), 'WRAPPER_INTERPRETER')
    need(paths['bash'] == CANARY_COMMAND[0], 'CANARY_BASH_IDENTITY')
    stdout_path, stderr_path = private / 'stdout', private / 'stderr'
    children = owner._CaptureChildren()
    result = dict(schema='dg16.hosted-wrapper-canary.v1', authority='NONE', original_awards=[],
                  source_commit=COMMIT, source_tree=TREE, episode=episode,
                  scope='UNCHANGED_TEN_PROGRAM_WRAPPER_EIGHT_REPORT_SLOTS_34_TO_41_128_DECLARED_METHODS',
                  status='UNQUALIFIED', phase='CHILD_CAPTURE', exit_code=None,
                  child_umask='022', private_parent_umask='077',
                  host_before=host_before, checkout_preparation=preparation,
                  dependency_manifest_sha256=sha(dependencies_raw),
                  raw_retention='PRIVATE_RUNNER_DIRECTORY_ONLY; NO_UPLOAD_NO_CRYPTO_NO_DURABLE_RETRIEVAL_CLAIM',
                  original_subset='110/2057 NOT_FULFILLED', full_pair='111/2068 NOT_EXECUTED')
    caught = None
    try:
        with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
            with ordinary_verifier_child_mask(owner, 'canary'):
                result['exit_code'] = children.launch(CANARY_COMMAND.copy(),
                    stdout=stdout, stderr=stderr, environment=environment,
                    base_environment=dict(os.environ), stdin_bytes=None)
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
        children.require_quiescent()
        result['phase'] = 'POST_READBACK'
        need(check_source(owner, manifest) == before, 'SOURCE_CURRENTNESS_CHANGED')
        _, host_after = H.inventory(U)
        need(host_after == host_before, 'HOST_CURRENTNESS_CHANGED')
        need(owner.environment_identity(environment, child_resolution=True) == actual_environment,
             'CHILD_ENVIRONMENT_CHANGED')
        result['host_after'] = host_after
        result['streams'] = {}
        for name, path in [('stdout', stdout_path), ('stderr', stderr_path)]:
            raw = read(path, LIMIT)
            result['streams'][name] = dict(bytes=len(raw), sha256=sha(raw))
        need(result['exit_code'] == 0, 'WRAPPER_NONZERO')
        _, observations = R.report_elapsed_relation(read(stderr_path, LIMIT), profile)
        result['reports'] = [dict(legacy_ordinal=34 + i, declared=x['declared_test_count'],
            ran=x['test_count'], skipped=x['skipped'], expected_failures=x['expected_failures'],
            elapsed_milliseconds=x['elapsed_milliseconds'], raw_report=x['raw_report'])
            for i, x in enumerate(observations)]
        result['status'] = 'CANARY_REPORT_RELATION_PASS_ONLY'
        result['phase'] = 'REPORT_RECEIVING_COMPLETE'
    except BaseException as exc:
        caught = exc
        # No raw exception message/traceback is public: it could contain diagnostics.
        result['failure_class'] = type(exc).__name__
        allowed = {'PRIVATE_PARENT_UMASK', 'ORIGINAL_VERIFIER_FORK_ONLY', 'WRAPPER_NONZERO', 'REPORT_DOTS_POPULATION_OR_STATUS', 'REPORT_SLOT_MULTIPLICITY',
                   'REPORT_DECLARED_COUNT', 'REPORT_IDENTITY_SEQUENCE', 'SOURCE_CURRENTNESS_CHANGED',
                   'HOST_CURRENTNESS_CHANGED', 'CHILD_ENVIRONMENT_CHANGED'}
        result['failure_code'] = exc.args[0] if exc.args and exc.args[0] in allowed else 'UNCLASSIFIED_PRIVATE_REFUSAL'
        result['status'] = 'UNQUALIFIED'
    finally:
        try:
            children.close()
        except BaseException as exc:
            caught = caught or exc
            result['status'] = 'UNQUALIFIED'
            result['failure_class'] = type(exc).__name__
        result['cleanup'] = {key: children.status[key] for key in
            ('primary_exit', 'quiescence', 'flag_restored', 'owned_pidfd_signals', 'live_children_refused')}
        result['cleanup']['other_child_exits_count'] = len(children.status['other_child_exits'])
        # A report is terminal only after the maintained owner proves ECHILD/restoration.
        result['cleanup_qualified'] = not children.active and children.status.get('flag_restored') is True
        if not result['cleanup_qualified']:
            result['status'] = 'UNQUALIFIED'
        write(public / 'RESULT.json', result)
    return 0 if caught is None and result['status'] == 'CANARY_REPORT_RELATION_PASS_ONLY' else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--job-context', type=Path, required=True)
    args = parser.parse_args()
    try:
        packet = json.loads(read(args.job_context, 4096))
        need(type(packet) is dict and set(packet) == {'schema','source_commit','source_tree','job'}, 'PUBLIC_CONTEXT_FIELDS')
        need(packet['schema'] == 'dg16.canary.public-job-context.v1' and packet['source_commit'] == COMMIT and packet['source_tree'] == TREE, 'PUBLIC_CONTEXT_SOURCE')
        job = packet['job']
        need(type(job) is dict and set(job) == {'GITHUB_REPOSITORY','GITHUB_REF','GITHUB_EVENT_NAME','GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','ImageOS','ImageVersion'}, 'PUBLIC_JOB_FIELDS')
        context(job)
        need(all(type(job[k]) is str and 0 < len(job[k]) <= 128 and all(c.isascii() and (c.isalnum() or c in '._-') for c in job[k]) for k in ('ImageOS','ImageVersion')), 'PUBLIC_IMAGE_FIELDS')
        return execute(args.source, args.output, job)
    except BaseException:
        # Pre-child failures produce no invented operation or raw diagnostics.
        print('DG16_CANARY {"status":"UNQUALIFIED","phase":"PREFLIGHT"}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
