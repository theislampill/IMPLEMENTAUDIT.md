#!/usr/bin/env python3
"""Finite static control for the dogfood wrapper's per-run output ownership."""
import argparse
from pathlib import Path
import re

OUTPUTS = (
    'dogfood-bootstrap-host-activation.out', 'dogfood-bootstrap.out',
    'dogfood-bootstrap-transcript.out', 'dogfood-bootstrap-chunking.out',
    'dogfood-bootstrap-real-home.out', 'dogfood-bootstrap-real-home-generic.out',
    'dogfood-bootstrap-real-home-host.out',
)

def check(source: str) -> None:
    if 'tmp="$(mktemp -d)"' not in source or "trap 'rm -rf \"$tmp\"' EXIT" not in source:
        raise ValueError('owned temporary directory and cleanup are required')
    if re.search(r'/tmp/dogfood-bootstrap[^\s]*\.out', source):
        raise ValueError('shared dogfood output is forbidden')
    for name in OUTPUTS:
        expected = '\"$tmp/' + name + '\"'
        occurrences = [line for line in source.splitlines() if name in line]
        if not occurrences or any(expected not in line for line in occurrences):
            raise ValueError('all consumers must use the quoted per-run output: ' + name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, required=True)
    args = parser.parse_args()
    source = (args.repo_root / 'tests/dogfood-bootstrap-contract.test.sh').read_text()
    check(source)
    for name in OUTPUTS:
        mutation = source.replace('\"$tmp/' + name + '\"', '/tmp/' + name, 1)
        try:
            check(mutation)
        except ValueError:
            continue
        raise AssertionError('shared-output mutation escaped: ' + name)
    print('test output isolation: valid wrapper and seven negative controls passed')

if __name__ == '__main__':
    main()
