#!/usr/bin/env python3
"""Standalone command-policy contract; no adapter, host, Git or model import."""
from __future__ import annotations
import ast
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parent / 'lib' / 'host_command_policy.py'

class HostCommandPolicyTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(),
                        'command classification still requires the adapter compilation unit')
        spec = importlib.util.spec_from_file_location('isolated_host_command_policy', MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.policy = module.HostCommandPolicy
        self.tmp = tempfile.TemporaryDirectory(prefix='command-policy-')
        self.addCleanup(self.tmp.cleanup)
        self.repo = self.tmp.name
        Path(self.repo, 'STATE.md').write_text('epoch\n', encoding='utf-8')
        self.profile = {'host': 'codex', 'attestation_id': 'local-test-profile',
                        'shell_dialect': 'posix',
                        'executables': {'cat': '/usr/bin/cat', 'echo': 'builtin:echo',
                                        'true': 'builtin:true', 'false': 'builtin:false',
                                        'rg': '/usr/bin/rg', 'bash': '/usr/bin/bash'}}

    def record(self, command, **changes):
        value = {'command': command, 'output': 'epoch\n', 'exit_code': 0,
                 'source': 'codex-command-completed', 'shell_dialect': 'posix',
                 'host_read_attestation_id': 'local-test-profile',
                 'wrapper_host_owned': False}
        value.update(changes)
        return value

    def classify(self, command, **changes):
        return self.policy.classify_command_target(
            self.record(command, **changes), 'STATE.md', self.repo, self.profile)

    def test_no_inward_infrastructure_imports(self):
        tree = ast.parse(MODULE.read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or '').split('.')[0])
        self.assertLessEqual(imports, {'__future__', 'os', 're', 'shlex'})
        self.assertNotIn('hosts', MODULE.read_text().split('class HostCommandPolicy')[1])

    def test_direct_read_is_positive(self):
        self.assertEqual(self.classify('cat STATE.md'), 'content-read')

    def test_mention_is_not_read(self):
        self.assertEqual(self.classify('echo STATE.md'), 'not-content-read')

    def test_unattested_command_fails_closed(self):
        self.assertEqual(self.classify('cat STATE.md', host_read_attestation_id=None), 'fail-closed')

    def test_foreign_host_cannot_supply_read_evidence(self):
        self.assertEqual(self.classify('cat STATE.md', source='claude-tool'), 'fail-closed')

    def test_dynamic_target_fails_closed(self):
        self.assertEqual(self.classify('cat "$TARGET"'), 'fail-closed')

    def test_false_branch_is_not_executed(self):
        self.assertEqual(self.classify('false && cat STATE.md', exit_code=1), 'not-content-read')

    def test_ambiguous_status_cannot_become_positive(self):
        self.assertEqual(self.classify('cat STATE.md; echo done'), 'fail-closed')

    def test_non_integer_exit_fails_closed(self):
        self.assertEqual(self.classify('cat STATE.md', exit_code=True), 'fail-closed')

    def test_read_inputs_are_not_mutated(self):
        record = self.record('cat STATE.md')
        original = copy.deepcopy((record, self.profile))
        self.policy.classify_command_target(record, 'STATE.md', self.repo, self.profile)
        self.assertEqual((record, self.profile), original)

    def test_alias_path_does_not_establish_identity(self):
        Path(self.repo, 'alias.md').symlink_to(Path(self.repo, 'STATE.md'))
        self.assertIsNone(self.policy._canonical_trace_path('alias.md', self.repo))

    def test_write_path_enumeration_has_no_write_effect(self):
        self.assertEqual(self.policy._command_write_paths(self.record('echo epoch > output.md')), ['output.md'])
        self.assertFalse(Path(self.repo, 'output.md').exists())

    def test_empty_attested_shell_is_not_a_content_read(self):
        for command in ('', ' ', '# STATE.md is a comment', '  # no operation'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, output=''), 'not-content-read')

    def test_zero_grep_limit_does_not_prove_search_input_read(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -m0 epoch STATE.md', 'grep -m 0 epoch STATE.md',
                        'grep --max-count=00 epoch STATE.md',
                        'grep --max-count 0 epoch STATE.md',
                        'grep -m1 -m0 epoch STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, output='', exit_code=1), 'not-content-read')
        for command in ('grep epoch STATE.md -m0', 'grep --max-c=0 epoch STATE.md'):
            with self.subTest(command=command):
                self.assertNotEqual(self.classify(command, output='', exit_code=1), 'content-read')

    def test_grep_limit_preserves_nonzero_and_pattern_file_reads(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -m1 epoch STATE.md', 'grep -m0 -m1 epoch STATE.md',
                        'grep -m0 -f STATE.md /dev/null', 'grep -m0 -fSTATE.md /dev/null'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, exit_code=1, output=''), 'content-read')

    def test_zero_count_spellings_do_not_prove_content_read(self):
        self.profile['executables'].update(head='/usr/bin/head', tail='/usr/bin/tail')
        for command in ('head -n0 STATE.md', 'head -c0 STATE.md',
                        'head --bytes=0 STATE.md', 'head --lines=00 STATE.md',
                        'tail -n0 STATE.md', 'tail --bytes=0 STATE.md',
                        'head -n1 -c0 STATE.md', 'tail -n1 -n0 STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, output=''), 'not-content-read')

    def test_nonzero_counts_and_signed_semantics_remain_reads(self):
        self.profile['executables'].update(head='/usr/bin/head', tail='/usr/bin/tail')
        for command in ('head -n1 STATE.md', 'head -c1 STATE.md',
                        'head --bytes=1 STATE.md', 'head -n0 -n1 STATE.md',
                        'head -c0 -n1 STATE.md', 'head -n-0 STATE.md',
                        'tail -n+0 STATE.md', 'tail -n+1 STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command), 'content-read')

    def test_unrecognised_reader_option_does_not_gain_read_credit(self):
        self.profile['executables']['head'] = '/usr/bin/head'
        for command in ('head --by=0 STATE.md', 'head --lin=0 STATE.md',
                        'head --future-option STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command), 'fail-closed')


class FreshReviewReadIdentityTests(unittest.TestCase):
    """FR-01..04: changes to operand/option/descriptor identity must be visible."""
    setUp = HostCommandPolicyTests.setUp
    record = HostCommandPolicyTests.record
    classify = HostCommandPolicyTests.classify

    def test_fr01_comma_is_part_of_operand_identity(self):
        for command in ('cat STATE.md,', 'cat "STATE.md,"',
                        'cat ./STATE.md,,', 'cat < STATE.md,'):
            with self.subTest(command=command):
                self.assertNotEqual(self.classify(command, output='DECOY\n'), 'content-read')

    def test_fr01_ordinary_and_literal_comma_target_neighbours(self):
        self.assertEqual(self.classify('cat "./STATE.md"'), 'content-read')
        Path(self.repo, 'STATE.md,').write_text('comma target\n')
        self.assertEqual(self.policy.classify_command_target(
            self.record('cat "STATE.md,"', output='comma target\n'),
            'STATE.md,', self.repo, self.profile), 'content-read')

    def test_fr02_clustered_zero_count_has_no_read_credit(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -nm0 epoch STATE.md', 'grep -nHm00 epoch STATE.md',
                        'grep -nm 0 epoch STATE.md', 'grep -nEm0 epoch STATE.md',
                        'grep -m1 -nm0 epoch STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, exit_code=1, output=''),
                                 'not-content-read')

    def test_fr02_clusters_preserve_limits_and_option_data(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -nm1 epoch STATE.md', 'grep -nm0 -m1 epoch STATE.md',
                        'grep -nm0 -f STATE.md decoy.md',
                        'grep -ne m0 STATE.md', 'grep -enm0 STATE.md',
                        'grep -nfSTATE.md decoy.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, exit_code=1, output=''), 'content-read')

    def test_fr03_quiet_multiple_operands_do_not_prove_target_read(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -q epoch decoy.md STATE.md',
                        'grep --quiet epoch decoy.md STATE.md',
                        'grep --silent epoch decoy.md STATE.md',
                        'grep -nq epoch decoy.md STATE.md',
                        'grep -qn epoch decoy.md STATE.md'):
            with self.subTest(command=command):
                self.assertNotEqual(self.classify(command, output=''), 'content-read')

    def test_fr03_single_operand_and_pattern_file_neighbours(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -q epoch STATE.md', 'grep -nq epoch STATE.md',
                        'grep -q -f STATE.md decoy.md other.md',
                        'grep -eq STATE.md', 'grep -F epoch decoy.md STATE.md',
                        'grep -q epoch < STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command), 'content-read')

    def test_terminal_search_options_do_not_credit_content(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -V epoch STATE.md', 'grep -nV epoch STATE.md',
                        'grep -Vn epoch STATE.md', 'grep --version epoch STATE.md',
                        'grep --help epoch STATE.md', 'rg -V epoch STATE.md',
                        'rg -h epoch STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, output='tool information\n'),
                                 'not-content-read')

    def test_search_options_are_command_specific_and_fail_closed(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -K epoch STATE.md', 'grep -nK epoch STATE.md',
                        'grep --future-option epoch STATE.md',
                        'grep --max-c=1 epoch STATE.md', 'grep -A1 epoch STATE.md',
                        'grep --glob x epoch STATE.md',
                        'grep --replace x epoch STATE.md',
                        'rg --future-option epoch STATE.md', 'rg -K epoch STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command), 'fail-closed')

    def test_search_option_data_and_terminators_preserve_reads(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -e --version STATE.md', 'grep -e -V STATE.md',
                        'grep -eV STATE.md', 'grep -enV STATE.md',
                        'grep -- --version STATE.md', 'grep -f STATE.md decoy.md',
                        'grep -nm1 epoch STATE.md', 'grep -r epoch STATE.md',
                        'rg -e --version STATE.md', 'rg -- --help STATE.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command, exit_code=1, output=''),
                                 'content-read')

    def test_readers_do_not_credit_unused_redirected_stdin(self):
        self.profile['executables'].update(grep='/usr/bin/grep', sed='/usr/bin/sed',
                                           head='/usr/bin/head', tail='/usr/bin/tail')
        for command in ('cat decoy.md', 'head -n1 decoy.md', 'tail -n1 decoy.md',
                        'sed -n p decoy.md', 'grep epoch decoy.md', 'rg epoch decoy.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md', output='DECOY\n'),
                                 'not-content-read')

    def test_readers_credit_implicit_and_explicit_stdin_consumption(self):
        self.profile['executables'].update(grep='/usr/bin/grep', sed='/usr/bin/sed',
                                           head='/usr/bin/head', tail='/usr/bin/tail')
        for reader in ('cat', 'head -n1', 'tail -n1', 'sed -n p', 'grep epoch', 'rg epoch'):
            for operands in ('', ' -', ' - decoy.md', ' decoy.md -'):
                command = reader + operands + ' < STATE.md'
                with self.subTest(command=command):
                    self.assertEqual(self.classify(command), 'content-read')

    def test_stdin_pattern_input_stays_distinct_from_search_input(self):
        self.profile['executables'].update(grep='/usr/bin/grep', sed='/usr/bin/sed')
        for command in ('grep -f - decoy.md', 'grep -nf- decoy.md',
                        'grep -m0 -f - decoy.md', 'grep -q -f - decoy.md other.md',
                        'sed -f - decoy.md', 'sed -f- decoy.md'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md'), 'content-read')
        for command in ('grep -m0 epoch', 'grep -m0 epoch -',
                        'grep -m0 -f decoy.md -'):
            with self.subTest(command=command):
                self.assertNotEqual(self.classify(command + ' < STATE.md', exit_code=1),
                                    'content-read')

    def test_quiet_search_does_not_credit_possibly_skipped_stdin(self):
        self.profile['executables']['grep'] = '/usr/bin/grep'
        for command in ('grep -q epoch decoy.md -', 'grep -q epoch - decoy.md',
                        'rg -q epoch decoy.md -'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md', output=''), 'fail-closed')
        for command in ('grep -q epoch', 'grep -q epoch -', 'rg -q epoch -'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md', output=''), 'content-read')

    def test_unsupported_reader_options_cannot_prove_stdin_use(self):
        self.profile['executables']['sed'] = '/usr/bin/sed'
        for command in ('cat --future-option', 'cat -K', 'sed --future-option p'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md'), 'fail-closed')
        for command in ('cat -n', 'cat --number', 'sed -n p'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command + ' < STATE.md'), 'content-read')

    def test_fr04_replaced_stdin_does_not_credit_earlier_file(self):
        for command in ('cat < STATE.md < decoy.md',
                        'cat 0< STATE.md 0< decoy.md',
                        'cat < STATE.md <<< decoy', 'cat < STATE.md 0<&-'):
            with self.subTest(command=command):
                self.assertNotEqual(self.classify(command, output='DECOY\n'), 'content-read')

    def test_fr04_final_stdin_and_unrelated_fds_preserve_read(self):
        for command in ('cat < decoy.md < STATE.md', 'cat 0< STATE.md',
                        'cat < STATE.md 2> error.log', 'cat < STATE.md 3< decoy.md',
                        'cat < STATE.md > copy.md', 'cat < STATE.md 0<&0'):
            with self.subTest(command=command):
                self.assertEqual(self.classify(command), 'content-read')


class FiniteConsumptionTests(unittest.TestCase):
    """A-owned R156 and same-family role controls; profiles are synthetic."""
    setUp = HostCommandPolicyTests.setUp
    record = HostCommandPolicyTests.record

    def check_commands(self, commands, expected, dialect='posix', exit_code=0):
        profile = copy.deepcopy(self.profile)
        profile['shell_dialect'] = dialect
        profile['executables'].update({name: '/usr/bin/' + name for name in
                                      ('sed', 'head', 'tail', 'grep', 'rg')})
        profile['executables'].update({'get-content': 'powershell:Get-Content',
                                      'type': 'builtin:type'})
        for command in commands:
            with self.subTest(command=command, dialect=dialect, exit_code=exit_code):
                record = self.record(command, shell_dialect=dialect,
                                     exit_code=exit_code)
                self.assertEqual(self.policy.classify_command_target(
                    record, 'STATE.md', self.repo, profile), expected)

    def test_r156_quit_cannot_credit_a_later_file_or_stdin(self):
        for program in ('q', 'Q'):
            for flags in ('', '-n ', '-e ', '--expression '):
                self.check_commands((f'sed {flags}{program} decoy.md STATE.md',
                                     f'sed {flags}{program} decoy.md - < STATE.md'),
                                    'fail-closed')

    def test_r156_quit_preserves_first_input_neighbours(self):
        for program in ('q', 'Q'):
            for flags in ('', '-n ', '-e ', '--expression '):
                self.check_commands((f'sed {flags}{program} STATE.md decoy.md',
                                     f'sed {flags}{program} - decoy.md < STATE.md',
                                     f'sed {flags}{program} < STATE.md'), 'content-read')

    def test_sed_known_draining_programmes_consume_later_inputs(self):
        for program in ("''", 'p', 'd', '=', '1,200p', "'1,$p'", "'$p'", "'p;d'"):
            self.check_commands((f'sed -n {program} decoy.md STATE.md',
                                 f'sed -n {program} decoy.md - < STATE.md'),
                                'content-read')

    def test_sed_composed_quit_limits_data_credit_to_first_input(self):
        self.check_commands(("sed -e p -e q decoy.md STATE.md",
                             "sed -e q -e p decoy.md - < STATE.md",
                             "sed 'p;q' decoy.md STATE.md"), 'fail-closed')
        self.check_commands(("sed -e p -e q STATE.md decoy.md",
                             "sed 'p;q' STATE.md decoy.md"), 'content-read')

    def test_sed_unknown_programme_is_not_a_general_sed_interpreter(self):
        self.check_commands(("sed '1q' decoy.md STATE.md", "sed 'q0' decoy.md STATE.md",
                             "sed 'n;q' decoy.md STATE.md", "sed 'b' STATE.md",
                             "sed 's/x/y/' STATE.md", "sed -f script.sed STATE.md",
                             "sed -f - STATE.md < script.sed"), 'fail-closed')
        self.check_commands(("sed -e '/STATE/p' notes.txt",), 'not-content-read')

    def test_sed_program_file_role_remains_separate(self):
        self.check_commands(('sed -f STATE.md decoy.md', 'sed -fSTATE.md decoy.md',
                             'sed --file STATE.md decoy.md',
                             'sed -f - decoy.md < STATE.md',
                             'sed -e q -f STATE.md decoy.md'), 'content-read')
        self.check_commands(('sed -e STATE.md decoy.md',), 'not-content-read')

    def test_sed_options_after_data_operands_are_refused(self):
        self.check_commands(('sed p decoy.md -e q STATE.md',
                             'sed p STATE.md -f script.sed'), 'fail-closed')
        self.check_commands(('sed -- p STATE.md', 'sed -n -- p STATE.md',
                             'sed -e p -- STATE.md'), 'content-read')

    def test_sed_closed_and_replaced_stdin_are_not_reads(self):
        self.check_commands(('sed q decoy.md - <&-',
                             'sed -n p < STATE.md < decoy.md',
                             'sed -n p < STATE.md 0<&-'), 'not-content-read')

    def test_external_patterns_do_not_prove_search_input_consumption(self):
        for dialect in ('posix', 'powershell', 'cmd'):
            for tool in ('grep', 'rg'):
                self.check_commands((f'{tool} -f empty.txt STATE.md',
                                     f'{tool} -f patterns.txt STATE.md',
                                     f'{tool} -f - STATE.md',
                                     f'{tool} -f patterns.txt -e epoch STATE.md'),
                                    'fail-closed', dialect, exit_code=1)
        self.check_commands(('grep -f empty.txt - < STATE.md',
                             'rg -f empty.txt - < STATE.md'), 'fail-closed', exit_code=1)

    def test_external_pattern_file_consumption_survives_search_refusal(self):
        for dialect in ('posix', 'powershell', 'cmd'):
            for tool in ('grep', 'rg'):
                self.check_commands((f'{tool} -f STATE.md decoy.md',
                                     f'{tool} -m0 -f STATE.md decoy.md',
                                     f'{tool} -q -f STATE.md decoy.md other.md'),
                                    'content-read', dialect, exit_code=1)

    def test_grep_inverted_empty_pattern_does_not_prove_search_consumption(self):
        for dialect in ('posix', 'powershell', 'cmd'):
            self.check_commands(("grep -v '' STATE.md", "grep -Fv '' STATE.md",
                                 "grep -v -e '' STATE.md", "grep -ev -v -e '' STATE.md",
                                 "grep --invert-match '' STATE.md"),
                                'fail-closed', dialect, exit_code=1)
        self.check_commands(("grep -v '' - < STATE.md",), 'fail-closed', exit_code=1)
        self.check_commands(("grep -v epoch STATE.md", "grep -e '' STATE.md",
                             "rg -v '' STATE.md"), 'content-read', exit_code=1)

    def test_powershell_zero_content_limits_do_not_prove_consumption(self):
        self.check_commands(('Get-Content -TotalCount 0 STATE.md',
                             'Get-Content STATE.md -TotalCount 00',
                             'Get-Content -Tail 0 -LiteralPath STATE.md'),
                            'not-content-read', 'powershell')

    def test_powershell_supported_parameter_roles_preserve_neighbours(self):
        self.check_commands(('Get-Content STATE.md', 'Get-Content -Path STATE.md',
                             'Get-Content -LiteralPath STATE.md',
                             'Get-Content -TotalCount 1 STATE.md',
                             'Get-Content -Tail 1 STATE.md',
                             'Get-Content -ReadCount 0 STATE.md',
                             'Get-Content -ReadCount 1 -Encoding utf8 STATE.md',
                             'Get-Content -Raw STATE.md',
                             'Get-Content -Delimiter epoch STATE.md'),
                            'content-read', 'powershell')
        self.check_commands(('Get-Content notes.txt -Delimiter STATE.md',),
                            'not-content-read', 'powershell')

    def test_powershell_filters_unknown_parameters_and_multiple_paths_are_refused(self):
        self.check_commands(('Get-Content -Exclude STATE.md STATE.md',
                             'Get-Content -Filter nope STATE.md',
                             'Get-Content -Include nope STATE.md',
                             'Get-Content -Wait STATE.md',
                             'Get-Content -Stream decoy STATE.md',
                             'Get-Content -Future STATE.md',
                             'Get-Content -TotalCount -1 STATE.md',
                             'Get-Content -TotalCount 0 -Tail 1 STATE.md',
                             'Get-Content -TotalCount 0 -TotalCount 1 STATE.md',
                             'Get-Content STATE.md,decoy.md',
                             'Get-Content -LiteralPath STATE.md,decoy.md',
                             'Get-Content decoy.md STATE.md'),
                            'fail-closed', 'powershell')
        # Unquoted '?' is outside the existing lexical grammar: refuse it.
        self.check_commands(('Get-Content -? STATE.md',), 'fail-closed', 'powershell')

    def test_cmd_type_information_and_multiple_operand_boundaries(self):
        # Retain the earlier unquoted-wildcard gate; do not widen cmd parsing.
        self.check_commands(('type /? STATE.md', 'type STATE.md /?'),
                            'fail-closed', 'cmd')
        self.check_commands(('type /Q STATE.md', 'type decoy.md STATE.md',
                             'type STATE.md decoy.md', 'type -- STATE.md'),
                            'fail-closed', 'cmd')
        self.check_commands(('type STATE.md', 'type "STATE.md"'), 'content-read', 'cmd')

    def test_non_posix_redirection_is_not_inherited_from_posix_grammar(self):
        for dialect, reader in (('powershell', 'Get-Content'), ('cmd', 'type')):
            self.check_commands((f'{reader} STATE.md < decoy.md',
                                 f'{reader} decoy.md < STATE.md',
                                 f'{reader} STATE.md <&-'), 'fail-closed', dialect)

    def test_incompatible_reader_dialects_stay_refused(self):
        for dialect, command in (('posix', 'Get-Content STATE.md'),
                                 ('posix', 'type STATE.md'),
                                 ('powershell', 'cat STATE.md'),
                                 ('cmd', 'sed p STATE.md')):
            self.check_commands((command,), 'fail-closed', dialect)

    def test_grep_and_rg_missing_search_inputs_are_not_no_match_successes(self):
        for dialect in ('posix', 'powershell', 'cmd'):
            for tool in ('grep', 'rg'):
                self.check_commands((f'{tool} epoch STATE.md',),
                                    'not-content-read', dialect, exit_code=2)
                self.check_commands((f'{tool} absent STATE.md',),
                                    'content-read', dialect, exit_code=1)


    def test_numeric_filenames_are_not_redirection_descriptors(self):
        self.check_commands(('cat 0 < STATE.md', "cat '0'< STATE.md",
                             r'cat \0< STATE.md', 'cat 2 > output.txt < STATE.md',
                             'sed q 0 < STATE.md'), 'not-content-read')
        self.check_commands(('cat 0< STATE.md', 'cat "STATE.md" 2>error.txt',
                             'cat < STATE.md 0<&0', 'cat < STATE.md 3<decoy.md'),
                            'content-read')

    def test_quoted_or_escaped_operators_do_not_create_reader_stages(self):
        self.check_commands(("true '&&' cat STATE.md", "true '&''&' cat STATE.md",
                             r'true \&\& cat STATE.md', "true ';' cat STATE.md",
                             "true '|' cat STATE.md"), 'not-content-read')
        self.check_commands(('true && cat STATE.md',), 'content-read')
        self.check_commands(("sed -n '1,200p' decoy.md - < STATE.md",), 'content-read')

    def test_inline_hash_is_part_of_filename_not_a_comment(self):
        self.check_commands(('cat STATE.md#decoy', 'cat "STATE.md#decoy"'),
                            'not-content-read')
        self.check_commands(('cat STATE.md # trailing comment',), 'content-read')
        self.check_commands(('# cat STATE.md',), 'not-content-read')

    def test_numeric_redirection_operand_boundary_is_refused(self):
        # Deliberately do not resolve an IO-number token as a redirection path.
        self.check_commands(('cat <0<STATE.md',), 'fail-closed')

    def test_literal_redirection_words_remain_argv_data(self):
        self.check_commands(("echo '<' STATE.md", "true '>' STATE.md"), 'not-content-read')
        self.check_commands(("cat '<' STATE.md",), 'content-read')
        self.assertEqual(self.policy._command_write_paths(
            self.record("echo '>' STATE.md")), [])
        self.assertEqual(self.policy._command_write_paths(
            self.record("echo '0' > copy.md")), ['copy.md'])

    def test_native_profiles_refuse_unmodelled_quote_and_escape_rules(self):
        self.check_commands(("type 'STATE.md'", r'type \STATE.md',
                             'type """STATE.md"""'),
                            'fail-closed', 'cmd')
        self.check_commands((r'type S\TATE.md',), 'not-content-read', 'cmd')
        self.check_commands(("Get-Content '''STATE.md'''", r'Get-Content \STATE.md',
                             'Get-Content """STATE.md"""'), 'fail-closed', 'powershell')
        self.check_commands(("rg -v '' STATE.md",), 'fail-closed', 'cmd', exit_code=1)

    def test_native_profiles_keep_only_simple_quoted_word_neighbours(self):
        self.check_commands(('type "STATE.md"', 'type STATE.md'), 'content-read', 'cmd')
        self.check_commands(("Get-Content 'STATE.md'", 'Get-Content "STATE.md"'),
                            'content-read', 'powershell')
        self.check_commands(("rg -v '' STATE.md",), 'content-read', 'powershell', exit_code=1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
