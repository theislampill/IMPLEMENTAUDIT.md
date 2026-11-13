#!/usr/bin/env python3
"""Lexical wire regressions; PureWindowsPath is not Windows host qualification."""
import ast
import pathlib
import types
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[2]
RUN = '.IMPLEMENTAUDIT/runs/path-regression-Ab12Cd'


def expression(path, function, predicate):
    module = ast.parse((SOURCE / path).read_bytes())
    owner = next(node for node in module.body
                 if isinstance(node, ast.FunctionDef) and node.name == function)
    selected = [node for node in ast.walk(owner) if predicate(node)]
    if len(selected) != 1:
        raise AssertionError('expected one source-owned path binding')
    node = selected[0]
    return compile(ast.Expression(node.test if isinstance(node, ast.Assert)
                                  else node.value), str(path), 'eval')


class PathSpelling(unittest.TestCase):
    """Exercise exact production expressions separately from filesystem custody."""

    @classmethod
    def setUpClass(cls):
        cls.author_guard = expression(
            'fixtures/controller-initialization/author_checkpoint.py', 'author',
            lambda node: isinstance(node, ast.Assert)
            and 'repo_root' in ast.unparse(node.test))
        cls.controller_record = expression(
            'skills/implementaudit/scripts/claim-run-rotation.py',
            'activate_controller_initialization',
            lambda node: isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'raw'
                    for target in node.targets))

    def author_accepts(self, path_type, repo, claimed_repo, claimed_run=RUN):
        return eval(self.author_guard, {
            'pathlib': types.SimpleNamespace(Path=path_type),
            'repo': path_type(repo), 'run': RUN,
            'claim': {'repo_root': claimed_repo, 'run_root': claimed_run}})

    def wire(self, root):
        return eval(self.controller_record, {
            'controller': 'path-regression',
            'context': {'claim_id': 'a' * 32, 'run_root': root}})

    def test_windows_author_accepts_git_slashes(self):
        self.assertTrue(self.author_accepts(pathlib.PureWindowsPath,
                        r'C:\Repo With Spaces', 'C:/Repo With Spaces'))

    def test_author_refuses_foreign_repository_and_run(self):
        for repo, claimed in [(r'C:\Repo', 'D:/Repo'),
                              (r'C:\Repo', 'C:/Other')]:
            with self.subTest(repo=repo, claimed=claimed):
                self.assertFalse(self.author_accepts(
                    pathlib.PureWindowsPath, repo, claimed))
        self.assertFalse(self.author_accepts(pathlib.PureWindowsPath,
                         r'C:\Repo', 'C:/Repo', RUN + '-foreign'))

    def test_posix_author_retains_case_and_literal_backslash(self):
        self.assertTrue(self.author_accepts(pathlib.PurePosixPath,
                        '/tmp/Repo\\Name', '/tmp/Repo\\Name'))
        self.assertFalse(self.author_accepts(pathlib.PurePosixPath,
                         '/tmp/Repo', '/tmp/repo'))
        self.assertFalse(self.author_accepts(pathlib.PurePosixPath,
                         '/tmp/Repo\\Name', '/tmp/Repo/Name'))

    def test_author_does_not_admit_other_lexical_aliases(self):
        for claimed in ('C:/Repo/.', 'C://Repo', 'c:/Repo', 'C:/repo'):
            with self.subTest(claimed=claimed):
                self.assertFalse(self.author_accepts(
                    pathlib.PureWindowsPath, r'C:\Repo', claimed))
        for claimed in ('/tmp//Repo', '/tmp/Repo/.'):
            with self.subTest(claimed=claimed):
                self.assertFalse(self.author_accepts(
                    pathlib.PurePosixPath, '/tmp/Repo', claimed))

    def test_windows_controller_record_uses_slash_wire_grammar(self):
        root = pathlib.PureWindowsPath(r'C:\Repo With Spaces') / RUN
        expected = ('implementaudit.controller-current.v1\tpath-regression\t'
                    + 'a' * 32 + '\tC:/Repo With Spaces/' + RUN + '\n')
        self.assertEqual(self.wire(root), expected.encode())

    def test_posix_controller_record_keeps_literal_backslash(self):
        root = pathlib.PurePosixPath('/tmp/Repo\\Name') / RUN
        expected = ('implementaudit.controller-current.v1\tpath-regression\t'
                    + 'a' * 32 + '\t/tmp/Repo\\Name/' + RUN + '\n')
        self.assertEqual(self.wire(root), expected.encode())


if __name__ == '__main__':
    unittest.main()
