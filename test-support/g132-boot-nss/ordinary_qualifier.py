#!/usr/bin/python3.12
"""Distinct ordinary boot NSS observation; no original or provider admission.

Reuse the retained setup, namespace and input owners without changing their
resource limits or the R2 temporary-lease cleanup discriminator. Boot NSS is a
separate administrative lifecycle. Its receipts never discharge original runtime,
private input, model, child-custody or native admission obligations.
"""
import argparse
from contextlib import contextmanager, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import types

ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = '760aaff5c478ff7354d36da186d62daba983aa49'
OPERATION = 'G132_BOOT_NSS_20261122_01'
REF = 'refs/heads/pro/dg16-g132-boot-nss-20261122-01'
WORKFLOW = 'theislampill/IMPLEMENTAUDIT.md/.github/workflows/dg16-g132-boot-nss.yml@' + REF
LEGACY = 'test-support/g132-host-profile-successor/ordinary_qualifier.py'
LEGACY_PIN = dict(bytes=14021, sha256='e316224f5492241b529161d37b4dbce5c63f6cfc038d0c750db82aae3de13a8e')
SETUP_PIN = dict(bytes=91535, sha256='37c14d5c8ff0f6f3f8d252049be4fa0d90b4217861c3fb4dd0a740cc9248f592')
NSS_PIN = dict(bytes=20327, sha256='a6a8ed4f7dca60904be936c393dffa049c2f948f8a15a87148c538280b416ee7')
LIMITS = dict(address_bytes=1610612736, cpu_seconds=120, file_bytes=268435456,
              descriptors=256, wall_seconds=240, report_bytes=2097152)


def need(value, reason):
    if not value:
        raise ValueError(reason)


def identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink, value.st_size,
            value.st_uid, value.st_gid, value.st_mtime_ns, value.st_ctime_ns)


@contextmanager
def held_bytes(path, maximum, expected=None):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= maximum,
             'boot ordinary bounded file kind/size differs')
        raw = os.pread(fd, maximum + 1, 0)
        opening = identity(before)
        need(len(raw) == before.st_size and identity(os.fstat(fd)) == opening == identity(os.lstat(path)),
             'boot ordinary opening file binding differs')
        if expected is not None:
            need(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == expected,
                 'boot ordinary source pin differs')
        yield raw
        need(identity(os.fstat(fd)) == opening == identity(os.lstat(path))
             and os.pread(fd, maximum + 1, 0) == raw, 'boot ordinary closing file binding differs')
    finally:
        os.close(fd)


@contextmanager
def legacy():
    path = ROOT / LEGACY
    with held_bytes(path, LEGACY_PIN['bytes'], LEGACY_PIN) as raw:
        module = types.ModuleType('g132_boot_pinned_existing_utility')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        need(module.SETUP_PIN == SETUP_PIN and module.LIMITS == LIMITS
             and module.BASE_COMMIT == BASE_COMMIT, 'boot ordinary retained owner binding differs')
        yield module


@contextmanager
def owner(name, pin):
    with legacy() as previous, previous.owner(name, pin) as module:
        yield module


def write_receipt(path, row, maximum):
    with legacy() as previous:
        previous.write_receipt(path, row, maximum)


def hosted_context():
    expected = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                    GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md', GITHUB_RUN_ATTEMPT='1',
                    GITHUB_EVENT_NAME='push', GITHUB_JOB='qualify', GITHUB_REF=REF,
                    ImageOS='ubuntu24', ImageVersion='20261116.376.1')
    need(all(os.environ.get(k) == v for k, v in expected.items()), 'boot ordinary provider context differs')
    need((os.getuid(), os.geteuid(), os.getgid(), os.getegid()) == (0, 0, 0, 0), 'boot ordinary root identity required')
    host = os.environ.get('GITHUB_SHA', '')
    run = os.environ.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[0-9a-f]{40}', host) and os.environ.get('GITHUB_WORKFLOW_SHA') == host
         and os.environ.get('GITHUB_WORKFLOW_REF') == WORKFLOW
         and re.fullmatch('[1-9][0-9]{0,19}', run), 'boot ordinary run/workflow identity differs')
    with open('/proc/sys/kernel/random/boot_id', 'rb') as stream:
        boot = stream.read(65).decode('ascii').strip()
    need(re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot), 'boot ordinary boot identity absent')
    return dict(expected, run_id=run, boot_id=boot, host_commit=host, workflow_ref=WORKFLOW)


def boot_binding(context, commit, tree):
    need(re.fullmatch('[0-9a-f]{40}', commit) and re.fullmatch('[0-9a-f]{40}', tree), 'boot source identities required')
    return dict(context, source_commit=commit, source_tree=tree, operation=OPERATION)


def boot_join(row, context, commit, tree):
    need(row.get('schema') == 'g132.boot-nss-prepare.v1' and row.get('operation') == OPERATION
         and row.get('authority') == 'NONE' and row.get('context') == context
         and row.get('source_commit') == commit and row.get('source_tree') == tree
         and row.get('nss_pin') == NSS_PIN and row.get('setup_pin') == SETUP_PIN
         and row.get('descriptor_restoration') is True
         and row.get('selected_gate_observation') == 'OBSERVED_SELECTED_GATE_PASS' and 'failure' not in row,
         'boot ordinary provisioning receipt identity/custody differs')
    received = row.get('configuration', {})
    need(received.get('schema') == 'g132.boot-nss.v1' and received.get('authority') == 'NONE'
         and received.get('context') == boot_binding(context, commit, tree)
         and received.get('state') == 'CONFIGURED_AND_READ_BACK'
         and all(received.get(k) is True for k in ('configured', 'exchange_attempted', 'descriptor_restoration'))
         and all(received.get(k) is False for k in ('original_execution', 'raw_bytes_exported', 'deletion_attempted',
                 'restoration_attempted', 'vm_disposal_observed', 'children_spawned', 'predecessor_process_custody_recovered'))
         and received.get('administrative_disposition') == 'RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL'
         and 'failure' not in received, 'boot ordinary provisioning did not establish its bounded lifecycle')
    return True


def configured_join(prepared, current):
    need(current.get('schema') == 'g132.boot-nss.v1' and current.get('authority') == 'NONE'
         and current.get('state') == 'CONFIGURED_CURRENT_READBACK'
         and current.get('configured') is True and current.get('descriptor_restoration') is True
         and current.get('predecessor_process_custody_recovered') is False and 'failure' not in current
         and all(current.get(k) == prepared.get(k) for k in ('context', 'before_pin', 'after_pin',
                 'configured_target', 'retained_original', 'private_preimage', 'journal',
                 'administrative_disposition', 'state_directory')),
         'boot ordinary configured state no longer joins its exact preparation receipt')
    return True


def selected_inputs_match(host):
    return (len(host.get('pins', [])) == 12 and all(x.get('match') is True for x in host['pins'])
            and len(host.get('system_aliases', [])) == 4 and all(x.get('match') is True for x in host['system_aliases'])
            and host.get('nss', {}).get('result', {}).get('match') is True
            and host.get('selected_bookends_equal') is True)


def output_directory(context, create):
    parent = Path(os.environ['RUNNER_TEMP'])
    need(parent.is_absolute() and parent.resolve() == parent, 'boot ordinary output parent alias refused')
    path = parent / ('g132-boot-nss-observation-' + context['run_id'] + '-1')
    if create:
        path.mkdir(mode=0o700)
    value = path.lstat()
    need(stat.S_ISDIR(value.st_mode) and stat.S_IMODE(value.st_mode) == 0o700
         and (value.st_uid, value.st_gid) == (0, 0), 'boot ordinary output directory custody differs')
    return path


class OrdinaryDeadline(BaseException):
    pass


def interrupted(signum, frame):
    raise OrdinaryDeadline('boot ordinary bounded wall/signal interruption')


def limits():
    for which, key in ((resource.RLIMIT_AS, 'address_bytes'), (resource.RLIMIT_CPU, 'cpu_seconds'),
                       (resource.RLIMIT_FSIZE, 'file_bytes'), (resource.RLIMIT_NOFILE, 'descriptors')):
        value = LIMITS[key]
        resource.setrlimit(which, (value, value))
    signal.signal(signal.SIGALRM, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    signal.alarm(LIMITS['wall_seconds'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', choices=('boot-nss', 'namespace', 'inputs', 'nss-finalize'), required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--source-tree', required=True)
    args = parser.parse_args(argv)
    context = hosted_context()  # Refuse non-hosted invocation before effects or limit changes.
    binding = boot_binding(context, args.source_commit, args.source_tree)
    limits()
    schema = {'boot-nss': 'g132.boot-nss-prepare.v1', 'namespace': 'g132.host-profile-namespace.v1',
              'inputs': 'g132.boot-nss-inputs.v1', 'nss-finalize': 'g132.boot-nss-finalize.v1'}[args.step]
    result = dict(schema=schema, operation=OPERATION, authority='NONE', context=context,
                  source_commit=args.source_commit, source_tree=args.source_tree, setup_pin=SETUP_PIN,
                  nss_pin=NSS_PIN, limits=LIMITS, source_commands=[], original_execution=False,
                  private_inputs_selected=False, provider_acquired=False, session_constructed=False,
                  native_admission=False, overall_admission='UNQUALIFIED',
                  copied_runtime_provisioning='UNPERFORMED_SEPARATE_ORIGINAL_OWNER',
                  selected_gate_observation='REFUSED')
    output, success = None, False
    try:
        with legacy() as previous, previous.owner('qualify-work-graph-c5-setup.py', SETUP_PIN) as setup:
            previous.source_identity(setup, args.source_commit, args.source_tree, result['source_commands'])
            output = output_directory(context, create=args.step == 'boot-nss')
            baseline = setup.fds()
            with previous.owner('hosted-boot-nss.py', NSS_PIN) as nss:
                if args.step == 'boot-nss':
                    result['configuration'] = nss.provision_hosted(binding)
                    success = result['configuration']['configured'] is True
                else:
                    # Read-only actual NSS observation never repairs a prior failed
                    # provisioning process or relaxes its receipt/custody gate.
                    result['configuration_before'] = nss.verify_configured(binding)
                    with held_bytes(output / 'boot-nss.json', 65536) as raw:
                        prepared = json.loads(raw)
                        boot_join(prepared, context, args.source_commit, args.source_tree)
                        configured_join(prepared['configuration'], result['configuration_before'])
                        result['boot_receipt'] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                        if args.step == 'namespace':
                            capture = io.StringIO()
                            try:
                                with redirect_stdout(capture):
                                    result['namespace_return_code'] = setup.main()
                            finally:
                                setup.emergency_cleanup()
                            need(len(capture.getvalue().encode()) <= 32768, 'boot namespace report exceeds bound')
                            result['namespace'] = json.loads(capture.getvalue())
                            success = previous.namespace_join(result, context, args.source_commit, args.source_tree)
                        elif args.step == 'inputs':
                            with held_bytes(output / 'namespace.json', 65536) as namespace_raw:
                                prior = json.loads(namespace_raw)
                                need(prior.get('operation') == OPERATION, 'boot namespace operation differs')
                                previous.namespace_join(prior, context, args.source_commit, args.source_tree)
                                result['namespace_receipt'] = dict(bytes=len(namespace_raw), sha256=hashlib.sha256(namespace_raw).hexdigest())
                                current = setup.hosted_current_owner(ROOT)
                                result['host_inputs'] = setup.receive_hosted_inputs(current)
                                current.CHECK()
                                success = selected_inputs_match(result['host_inputs'])
                        else:
                            success = True
                        result['configuration_after'] = nss.verify_configured(binding)
                        configured_join(prepared['configuration'], result['configuration_after'])
            if args.step != 'namespace':
                # setup.main permanently lowers namespace hard limits. Its source
                # files remain held/bookended; no second Git child is added there.
                previous.source_identity(setup, args.source_commit, args.source_tree, result['source_commands'])
            result['descriptor_restoration'] = setup.fds() == baseline
            need(result['descriptor_restoration'], 'boot ordinary descriptor restoration differs')
            need(hosted_context() == context, 'boot ordinary closing host context differs')
        result['selected_gate_observation'] = 'OBSERVED_SELECTED_GATE_PASS' if success else 'REFUSED'
    except BaseException as error:
        success = False
        result['failure'] = dict(type=type(error).__name__, reason=str(error)[:512])
        if type(getattr(error, 'record', None)) is dict:
            result['nss_failure_record'] = error.record
    finally:
        signal.alarm(0)
    if output is not None:
        write_receipt(output / (args.step + '.json'), result,
                      LIMITS['report_bytes'] if args.step == 'inputs' else 65536)
    print(json.dumps(dict(operation=OPERATION, step=args.step, success=success,
                         output=str(output) if output else None, overall_admission='UNQUALIFIED'), sort_keys=True))
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
