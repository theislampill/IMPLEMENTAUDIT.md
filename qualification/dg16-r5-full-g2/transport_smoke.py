#!/usr/bin/env python3
"""One bounded hosted transport observation; no qualification or acceptance."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import time
import types

HERE = Path(__file__).resolve().parent
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'engineering/g2-production-transport-smoke-20261118-01'
SOURCE_PARENT = '9a349423b6ca3dda18115a07ed41b63970bc8b77'
CONTROL_BRANCH = 'pro/dg16-g2-reviewed-control-20261118-01'
CONTROL_COMMIT = '0fc8b8a0343925e72b24f4f98daad8ba988bd045'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
PINS = {'live_control.py': 'cd8262defc85c2541632fe00e51bc78c804b13a3a8a4501e39300b4269f866ff',
        'host_utility.py': '02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5'}
MARKER = 'TRANSPORT_SMOKE_NON_ACCEPTANCE'
FORBIDDEN = ('CONSUMPTION_RESERVED.json', 'CONTROL.json', 'INDEPENDENT_REVIEW.json', 'ROOT_CONSUMPTION.json')
LIMIT = 65536


class Refusal(ValueError):
    pass


class FetchComplete(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def load_pinned(path, expected):
    need(stat.S_ISREG(path.lstat().st_mode) and path.stat().st_size <= 131072, 'SOURCE_FILE_REFUSED')
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected, 'SOURCE_DIGEST_REFUSED')
    module = types.ModuleType('smoke_' + path.stem)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def initial_result():
    return {'schema': 'dg16.production-transport-smoke.v1', 'scope': MARKER,
            'status': 'REFUSED', 'code': 'SMOKE_NOT_COMPLETED', 'fetch_completed': False,
            'original_acceptance_awarded': False, 'full_G2_awarded': False, 'G132_awarded': False,
            'full_pair_executed': False, 'control_replayed': False, 'original_consumption': False,
            'branch_written': False, 'automatic_retry': False, 'operation_limit_seconds': 180,
            'repository': REPOSITORY, 'control_branch': CONTROL_BRANCH,
            'expected_control_commit': CONTROL_COMMIT, 'source_parent_expected': SOURCE_PARENT,
            'expected_source_sha256': PINS, 'source_hashes_verified': False,
            'commands': [], 'attempted_operations': [],
            'forbidden_files_absent': None}


class CaptureGate:
    def __init__(self, work, utility, deadline):
        self.utility, self.deadline = utility, deadline
        self.records, self.operations = None, []
        cache = str(work / 'control.git')
        self.allowed = [
            ['/usr/bin/git', 'init', '--bare', '--quiet', cache],
            ['/usr/bin/git', '-c', 'protocol.https.allow=always', 'ls-remote', '--exit-code', '--refs',
             REMOTE, 'refs/heads/' + CONTROL_BRANCH],
            ['/usr/bin/git', '-c', 'protocol.https.allow=always', '--git-dir', cache,
             'fetch', '--quiet', '--no-tags', '--depth=2', REMOTE, CONTROL_COMMIT]]

    def capture(self, label, argv, records, deadline, seconds):
        index = len(self.operations)
        need(index < 3 and argv == self.allowed[index], 'COMMAND_OUTSIDE_TRANSPORT_SCOPE')
        need(label == 'bounded-read-only-control' and deadline == self.deadline and
             0 < seconds <= 20 and time.monotonic() < deadline, 'CAPTURE_BOUND_REFUSED')
        if self.records is None:
            self.records = records
        need(records is self.records and len(records) == index, 'CAPTURE_RECORDS_CHANGED')
        self.operations.append(('init', 'ls-remote', 'fetch')[index])
        # Delegate unchanged: the production utility supplies its closed environment,
        # output limits, pidfd custody, complete streams, and child cleanup.
        code, out, err = self.utility.capture(label, argv, records, deadline, seconds=seconds)
        need(len(records) == index + 1 and len(out) <= 32768 and len(err) <= 32768, 'CAPTURE_RECORDS_CHANGED')
        need(code == 0, 'CAPTURE_NONZERO')
        if index == 1:
            need(out == (CONTROL_COMMIT + '\trefs/heads/' + CONTROL_BRANCH + '\n').encode(), 'CONTROL_HEAD_CHANGED')
        if index == 2:
            need(time.monotonic() < deadline, 'OPERATION_DEADLINE')
            # Never return fetch success to hold: its next command reads a parent.
            raise FetchComplete
        return code, out, err


def failure_code(exc):
    allowed = {'COMMAND_OUTSIDE_TRANSPORT_SCOPE', 'CAPTURE_BOUND_REFUSED', 'CAPTURE_RECORDS_CHANGED',
               'CAPTURE_NONZERO', 'CONTROL_HEAD_CHANGED', 'OPERATION_DEADLINE', 'SOURCE_FILE_REFUSED',
               'SOURCE_DIGEST_REFUSED', 'HOST_CONTEXT_REFUSED', 'OUTPUT_LOCATION_REFUSED',
               'NO_REPEAT_SMOKE', 'SUBREAPER_REFUSED', 'PROCESS_START_REFUSED', 'PIDFD_ACQUISITION_REFUSED',
               'CHILD_CLEANUP_UNCERTAIN', 'RUN_WATCHDOG', 'LIVE_CONTROL_GIT_BOUND',
               'LIVE_CONTROL_PRIVATE_LOG_BOUND', 'NO_REPEAT_LIVE_CONSUMPTION'}
    return str(exc) if type(exc).__name__ == 'Refusal' and str(exc) in allowed else 'SMOKE_OPERATION_REFUSED'


def observe(work, control, utility, deadline):
    result = initial_result()
    gate = CaptureGate(work, utility, deadline)
    request = json.dumps({'repository': REPOSITORY, 'control_branch': CONTROL_BRANCH,
                          'run_id': MARKER,
                          'control_path': 'qualification/dg16-full-g2-control/' + MARKER + '-1'}).encode()
    try:
        control.hold(work, request, deadline, gate, '/usr/bin/git')
    except FetchComplete:
        result.update(status='TRANSPORT_OBSERVED', code='FETCH_COMPLETED_STOPPED_BEFORE_PARENT', fetch_completed=True)
    except BaseException as exc:
        result['code'] = failure_code(exc)
    finally:
        absent = {name: not os.path.lexists(work / name) for name in FORBIDDEN}
        result.update(commands=gate.records or [], attempted_operations=gate.operations, forbidden_files_absent=absent)
        if not all(absent.values()):
            result.update(status='REFUSED', code='FORBIDDEN_OUTPUT_PRESENT', fetch_completed=False)
    return result


def alarm(_signum, _frame):
    raise Refusal('OPERATION_DEADLINE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output)
    result, ready = initial_result(), False
    try:
        run_id = os.environ.get('GITHUB_RUN_ID', '')
        need(re.fullmatch('[0-9]{1,20}', run_id), 'HOST_CONTEXT_REFUSED')
        runner = Path(os.environ['RUNNER_TEMP']).resolve(strict=True)
        need(output.absolute() == runner / ('g2-production-transport-smoke-' + run_id + '-1'), 'OUTPUT_LOCATION_REFUSED')
        need(not os.path.lexists(output), 'NO_REPEAT_SMOKE')
        output.mkdir(mode=0o700)
        ready = True
        need(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted'
             and os.environ.get('GITHUB_REPOSITORY') == REPOSITORY and os.environ.get('GITHUB_EVENT_NAME') == 'push'
             and os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH
             and os.environ.get('GITHUB_RUN_ATTEMPT') == '1', 'HOST_CONTEXT_REFUSED')
        workflow_commit = os.environ.get('GITHUB_SHA', '')
        need(re.fullmatch('[0-9a-f]{40}', workflow_commit), 'HOST_CONTEXT_REFUSED')
        signal.signal(signal.SIGALRM, alarm)
        signal.setitimer(signal.ITIMER_REAL, 180)
        deadline = time.monotonic() + 180
        control = load_pinned(HERE / 'live_control.py', PINS['live_control.py'])
        utility = load_pinned(HERE / 'host_utility.py', PINS['host_utility.py'])
        # Match the production caller's child-adoption precondition for capture.
        libc = ctypes.CDLL(None, use_errno=True)
        actual = ctypes.c_int()
        need(libc.prctl(36, 1, 0, 0, 0) == 0 and
             libc.prctl(37, ctypes.byref(actual), 0, 0, 0) == 0 and actual.value == 1, 'SUBREAPER_REFUSED')
        work = output / 'work'
        work.mkdir(mode=0o700)
        result = observe(work, control, utility, deadline)
        result.update(run_id=run_id, run_attempt=1, workflow_commit=workflow_commit,
                      source_hashes_verified=True,
                      subreaper_enabled_and_read_back=True,
                      smoke_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    except BaseException as exc:
        result.update(status='REFUSED', code=failure_code(exc), fetch_completed=False)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if ready:
            absent = {name: not os.path.lexists(output / 'work' / name) for name in FORBIDDEN}
            result['forbidden_files_absent'] = absent
            if not all(absent.values()):
                result.update(status='REFUSED', code='FORBIDDEN_OUTPUT_PRESENT', fetch_completed=False)
        raw = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
        need(len(raw) <= LIMIT, 'EVIDENCE_BOUND_REFUSED')
        if ready:
            with (output / 'RESULT.json').open('xb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        print('DG16_TRANSPORT_SMOKE ' + json.dumps(result, sort_keys=True, separators=(',', ':')))
    return 0 if result['status'] == 'TRANSPORT_OBSERVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
