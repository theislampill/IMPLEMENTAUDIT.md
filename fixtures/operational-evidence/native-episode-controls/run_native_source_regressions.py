"""Run the original 42, seven profile/export, and 25 added source-only controls."""
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


# Additive source-only groups; the original 42 + 4 profile + 3 export remain exact.
CURRENT_SOURCE_GROUPS = (
    ('test_source_owner_bounds', 'SourceOwnerBoundsControls', (
        'test_all_issuer_readers_accept_delivered_module_length',
        'test_all_issuer_readers_accept_exact_code_ceiling',
        'test_all_issuer_readers_refuse_above_ceiling_before_evaluation',
        'test_all_issuer_readers_refuse_replacement_before_open',
        'test_all_issuer_readers_refuse_wrong_digest',
        'test_fifo_is_refused_before_any_content_read',
        'test_supplied_declared_length_must_match_the_real_file',
    )),
    ('test_current_native_relation', 'CurrentNativeRelationControls', (
        'test_authorization_admits_load_during_spawn_rpc',
        'test_authorization_keeps_legacy_load_after_reply',
        'test_authorization_keeps_strict_load_call_result_order',
        'test_authorization_keeps_strict_order_for_other_header_or_profile',
        'test_authorization_rejects_load_before_or_at_activation',
        'test_authorization_rejects_route_before_reply_or_load_result',
        'test_before_remains_strict_across_sources_and_physical_intervals',
        'test_fresh_boundary_admits_activation_during_spawn_rpc',
        'test_fresh_boundary_keeps_legacy_completed_rpc_order',
        'test_fresh_boundary_preserves_spawn_identity_and_freshness',
        'test_fresh_boundary_refuses_mutated_header_bytes_or_digest',
        'test_fresh_boundary_rejects_reversed_or_equal_causal_edges',
        'test_fresh_boundary_uses_actual_header_and_qualified_profile',
        'test_relation_matches_each_entity_to_its_own_version',
        'test_relation_rejects_foreign_identity_and_parent',
        'test_relation_rejects_native_header_version_and_cwd_drift',
        'test_relation_rejects_unbound_or_malformed_running_version',
        'test_same_version_relation_stays_valid',
    )),
)

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
        profile_tests = list(leaves(unittest.defaultTestLoader.loadTestsFromModule(load_local('test_profile_semantics'))))
        profile_ids = sorted(test.id() for test in profile_tests)
        if profile_ids != ['test_profile_semantics.ProfileSemanticsControls.' + name for name in (
                'test_current_final_phase_reaches_bound_result_and_delivery',
                'test_profile_final_phases_remain_distinct',
                'test_qualified_terminal_format_binds_raw_and_native_without_normalization',
                'test_retained_metadata_reaches_history_without_relaxing_provenance')]:
            raise ValueError('current-profile regression population changed')
        tests += profile_tests
        actual = sorted(actual + profile_ids)
        export_tests = list(leaves(unittest.defaultTestLoader.loadTestsFromModule(load_local('test_export_semantics'))))
        export_ids = sorted(test.id() for test in export_tests)
        if export_ids != ['test_export_semantics.ExportSemanticsControls.' + name for name in (
                'test_covered_and_assigned_scope_bind_pending_kind_and_version',
                'test_occurrence_ranges_and_order_match_original_source_guards',
                'test_unresolved_signal_is_preserved_without_consumption')]:
            raise ValueError('export-semantic regression population changed')
        tests += export_tests
        actual = sorted(actual + export_ids)
        for module_name, class_name, methods in CURRENT_SOURCE_GROUPS:
            group = list(leaves(unittest.defaultTestLoader.loadTestsFromModule(load_local(module_name))))
            group_ids = sorted(test.id() for test in group)
            expected_group = [module_name + '.' + class_name + '.' + name for name in methods]
            if group_ids != expected_group:
                raise ValueError('current source-only regression population changed: ' + module_name)
            tests += group
            actual = sorted(actual + group_ids)
        if args.list:
            print(json.dumps({'scope': 'SOURCE_ONLY_NO_NATIVE_CREDIT', 'registered': len(actual), 'tests': actual}, indent=2)); return 0
        if args.case:
            unknown = set(args.case) - set(actual)
            if unknown: raise ValueError('unknown selected control: ' + ', '.join(sorted(unknown)))
            tests = [test for test in tests if test.id() in args.case]
        before = support.source_pins()
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
        if support.source_pins() != before: raise ValueError('public source changed during regression')
        print(json.dumps({'scope': 'SOURCE_ONLY_NO_NATIVE_CREDIT', 'registered': len(actual), 'executed': result.testsRun,
            'skipped': len(result.skipped), 'success': result.wasSuccessful(), 'source_sha256': before}, sort_keys=True))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__': raise SystemExit(main())
