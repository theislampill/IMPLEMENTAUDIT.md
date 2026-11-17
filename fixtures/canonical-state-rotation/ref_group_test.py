#!/usr/bin/env python3
"""Fresh grouped Windows ref observations preserve Git and physical checks."""
import os
import unittest
from unittest import mock

import windows_custody_test as windows


@unittest.skipUnless(os.name == 'nt', 'actual Windows ref custody required')
class RefGroup(unittest.TestCase):
    setUp = windows.GitObjectCustody.setUp
    git = windows.GitObjectCustody.git

    def population(self):
        self.first = self.git('hash-object', '-w', '--stdin', data=b'first').decode().strip()
        self.second = self.git('hash-object', '-w', '--stdin', data=b'second').decode().strip()
        self.refs = ['refs/implementaudit/current-generations/group-a',
                     'refs/implementaudit/current-generations/group-b']
        for ref, oid in zip(self.refs, (self.first, self.second)):
            self.git('update-ref', ref, oid)

    def read(self, scope, refs=None):
        self.assertTrue(callable(getattr(scope, 'refs', None)), 'grouped ref observation absent')
        return scope.refs(self.refs if refs is None else refs)

    def test_present_population_has_one_git_verification_and_no_value_cache(self):
        self.population()
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope:
            original, calls = scope.read_command, []
            def observed(*args):
                calls.append(args)
                return original(*args)
            with mock.patch.object(scope, 'read_command', side_effect=observed):
                self.assertEqual(self.read(scope), dict(zip(self.refs, (self.first, self.second))))
            checks = [args for args in calls if args[0] == 'show-ref']
            self.assertEqual(len(checks), 1)
            self.git('update-ref', self.refs[0], self.second, self.first)
            self.assertEqual(self.read(scope), dict.fromkeys(self.refs, self.second))

    def test_packed_loose_override_and_exact_absence(self):
        self.population()
        self.git('pack-refs', '--all')
        self.git('update-ref', self.refs[0], self.second, self.first)
        absent = 'refs/implementaudit/current-generations/absent'
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope:
            self.assertEqual(self.read(scope, self.refs + [absent]),
                             dict.fromkeys(self.refs, self.second) | {absent: None})

    def test_large_population_uses_bounded_fresh_groups(self):
        self.population()
        refs = ['refs/implementaudit/current-generations/group-' + str(index) for index in range(65)]
        self.git('update-ref', '--stdin', data=''.join('update ' + ref + ' ' + self.first + '\n'
                                                     for ref in refs).encode())
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope:
            original, calls = scope.read_command, []
            def observed(*args):
                if args[0] == 'show-ref':
                    calls.append(args)
                return original(*args)
            with mock.patch.object(scope, 'read_command', side_effect=observed):
                self.assertEqual(self.read(scope, refs), dict.fromkeys(refs, self.first))
            self.assertEqual([len(args) - 3 for args in calls], [64, 1])

    def test_loose_change_after_git_observation_refuses(self):
        self.population()
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope:
            original = scope.read_command
            def race(*args):
                result = original(*args)
                if args[0] == 'show-ref':
                    self.git('update-ref', self.refs[0], self.second, self.first)
                return result
            with mock.patch.object(scope, 'read_command', side_effect=race), self.assertRaises(OSError):
                self.read(scope)

    def test_packed_change_after_git_observation_refuses(self):
        self.population()
        self.git('pack-refs', '--all')
        packed = self.repo / '.git/packed-refs'
        original_bytes = packed.read_bytes()
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope:
            original = scope.read_command
            def race(*args):
                result = original(*args)
                if args[0] == 'show-ref':
                    packed.write_bytes(original_bytes.replace(self.first.encode(), self.second.encode()))
                return result
            with mock.patch.object(scope, 'read_command', side_effect=race), self.assertRaises(OSError):
                self.read(scope)

    def test_symbolic_dangling_and_duplicate_packed_are_not_admitted(self):
        self.population()
        path = self.repo / '.git' / self.refs[0]
        original = path.read_bytes()
        for raw in (b'ref: refs/heads/main\n', b'9' * 40 + b'\n', b'not-an-oid\n'):
            path.write_bytes(raw)
            with self.subTest(raw=raw), self.custody.git_scope(self.repo, self.exe, self.env) as scope:
                with self.assertRaises(OSError):
                    self.read(scope)
        path.write_bytes(original)
        packed = self.repo / '.git/packed-refs'
        packed.write_bytes((self.first + ' ' + self.refs[0] + '\n').encode() * 2)
        with self.custody.git_scope(self.repo, self.exe, self.env) as scope, self.assertRaises(OSError):
            self.read(scope)

    def test_partial_duplicate_or_foreign_git_output_refuses(self):
        self.population()
        for body in ((self.first + ' ' + self.refs[0] + '\n').encode(),
                     ((self.first + ' ' + self.refs[0] + '\n') * 2).encode(),
                     (self.first + ' refs/heads/foreign\n').encode()):
            with self.subTest(body=body), self.custody.git_scope(self.repo, self.exe, self.env) as scope:
                original = scope.read_command
                def substitute(*args):
                    result = original(*args)
                    if args[0] == 'show-ref':
                        result.stdout = body
                    return result
                with mock.patch.object(scope, 'read_command', side_effect=substitute), self.assertRaises(OSError):
                    self.read(scope)


if __name__ == '__main__':
    unittest.main()
