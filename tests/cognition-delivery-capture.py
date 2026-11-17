#!/usr/bin/env python3
"""Bounded real delivery-capture controls; no route or host authority is issued."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def worker(source, directory, case):
    spec = importlib.util.spec_from_file_location('delivery_capture_owner', source)
    route = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = route
    spec.loader.exec_module(route)
    path = directory / 'input'
    data = b'exact delivery source\n'
    path.write_bytes(data)
    original_lstat = os.lstat
    observed = 0

    def scheduled_lstat(selected, *args, **kwargs):
        nonlocal observed
        result = original_lstat(selected, *args, **kwargs)
        if os.fspath(selected) == str(path):
            observed += 1
            if observed == 2:
                path.unlink()
                os.mkfifo(path, 0o600)
                (directory / 'intervention').write_text('regular lstat returned; FIFO replaces opening target\n')
        return result

    # Resolve performs the first pathname lstat. Return the second genuine
    # regular-file observation, then replace only this owned test input.
    if case == 'fifo-after-lstat':
        route.os.lstat = scheduled_lstat
    kwargs = {} if case == 'stable-default' else {'max_bytes': (len(data) if case == 'bound-exact' else len(data) - 1 if case == 'over-bound' else 64)}
    raw, physical = route.child_delivery_snapshot(path, 'delivery capture test', **kwargs)
    assert raw == data and physical[2] == len(data)
    print(json.dumps({'status': 'CAPTURED', 'bytes': len(raw)}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py')
    parser.add_argument('--worker-directory', type=Path)
    parser.add_argument('--case', choices=('stable', 'stable-default', 'bound-exact', 'over-bound', 'fifo-after-lstat'))
    args = parser.parse_args()
    if args.worker_directory is not None:
        assert args.case
        return worker(args.source, args.worker_directory, args.case)
    results = []
    with tempfile.TemporaryDirectory(prefix='cognition-delivery-capture-') as raw:
        for case in ('stable', 'stable-default', 'bound-exact', 'over-bound', 'fifo-after-lstat'):
            directory = Path(raw) / case
            directory.mkdir()
            command = [sys.executable, '-B', __file__, '--source', str(args.source),
                       '--worker-directory', str(directory), '--case', case]
            # subprocess.run kills and reaps the sole owned worker on timeout.
            # The worker opens no subprocesses, owners, Git refs or native routes.
            result = subprocess.run(command, capture_output=True, text=True, timeout=3)
            assert not result.stderr, (case, result.stderr)
            payload = json.loads(result.stdout)
            if case in ('stable', 'stable-default', 'bound-exact'):
                assert result.returncode == 0 and payload == {'status': 'CAPTURED', 'bytes': 22}
            elif case == 'over-bound':
                assert result.returncode == 2 and payload['status'] == 'UNAVAILABLE'
                assert payload['decision'] == 'PENDING' and payload['advance_allowed'] is False
                assert payload['enforcement_available'] is False
                assert payload['error'] == 'delivery capture test exceeds its exact source bound'
            else:
                assert (directory / 'intervention').is_file(), 'replacement schedule did not execute'
                assert result.returncode == 2 and payload['status'] == 'UNAVAILABLE'
                assert payload['decision'] == 'PENDING' and payload['advance_allowed'] is False
                assert payload['enforcement_available'] is False
                assert payload['error'] == 'delivery capture test is not an unaliased regular delivery input'
            results.append({'case': case, 'exit': result.returncode})
    print(json.dumps({'scope': 'ACTUAL_DELIVERY_CAPTURE_ONLY', 'controls': results,
                      'native_authority': False}, sort_keys=True))


if __name__ == '__main__':
    main()
