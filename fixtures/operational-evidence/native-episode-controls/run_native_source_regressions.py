"""Run the 42 public native-source controls against an explicit repository root."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
MODULES = ('test_native_probe', 'test_current_source_owner', 'test_review_repairs', 'test_owner_hooks',
    'test_existing_owner_additions', 'test_canonical_episode_binding', 'test_episode_export', 'test_pending_integration')


def load_local(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def leaves(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite): yield from leaves(item)
        else: yield item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--scratch-parent', type=Path)
    parser.add_argument('--case', action='append', default=[], help='exact test id; repeat to select a focused adaptation check')
    parser.add_argument('--list', action='store_true', help='list all registered control ids without running them')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='native-source-regression-', dir=args.scratch_parent) as directory:
        support = load_local('native_test_support'); support.configure(args.repo_root, directory)
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(load_local(name)) for name in MODULES)
        tests = list(leaves(suite)); expected = json.loads((HERE / 'guard-golden.json').read_text())['test_ids']
        actual = sorted(test.id() for test in tests)
        if actual != expected or len(actual) != 42:
            raise ValueError('the complete 42-control population changed')
        if args.list:
            print(json.dumps({'scope': 'SOURCE_ONLY_NO_NATIVE_CREDIT', 'registered': 42, 'tests': actual}, indent=2)); return 0
        if args.case:
            unknown = set(args.case) - set(actual)
            if unknown: raise ValueError('unknown selected control: ' + ', '.join(sorted(unknown)))
            tests = [test for test in tests if test.id() in args.case]
        before = support.source_pins()
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
        if support.source_pins() != before: raise ValueError('public source changed during regression')
        print(json.dumps({'scope': 'SOURCE_ONLY_NO_NATIVE_CREDIT', 'registered': 42, 'executed': result.testsRun,
            'skipped': len(result.skipped), 'success': result.wasSuccessful(), 'source_sha256': before}, sort_keys=True))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__': raise SystemExit(main())
