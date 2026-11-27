"""Offline control: the pinned operation.load_selected accepts the real admitted source.

Run 46046841410 refused at prepare with SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY
because the operator's executor binding was not the one the pinned V24 engine
actually loads. This control loads the exact pinned operation.py through run.py's
own module loader and calls load_selected against a clean checkout of the admitted
source named by DG16_TEST_SOURCE_ROOT. No network, native command or effect.
"""
import ast
import os
from pathlib import Path
import subprocess
import types
import unittest

PACKET = Path(__file__).resolve().parents[1] / 'packet'
SOURCE_ENV = 'DG16_TEST_SOURCE_ROOT'


def constants(path):
    out = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


class LoadSelected(unittest.TestCase):
    def setUp(self):
        configured = os.environ.get(SOURCE_ENV)
        self.assertTrue(configured, SOURCE_ENV + ' must name a clean checkout of the admitted source')
        self.source = Path(configured).resolve(strict=True)
        run_path = PACKET / 'run.py'
        self.run = types.ModuleType('load_selected_control_run')
        self.run.__file__ = str(run_path)
        exec(compile(run_path.read_bytes(), str(run_path), 'exec'), self.run.__dict__)
        self.operation = self.run.load_module('operation')

    def test_source_is_the_admitted_commit(self):
        observed = subprocess.check_output(['git', '-C', str(self.source), 'rev-parse', 'HEAD', 'HEAD^{tree}'],
                                           text=True).split()
        composition = __import__('json').loads((PACKET / 'HOST_COMPOSITION.json').read_text())
        self.assertEqual(observed, [composition['source_commit'], self.operation.SOURCE_TREE])
        self.assertEqual(subprocess.check_output(['git', '-C', str(self.source), 'status', '--porcelain'], text=True), '')

    def test_pinned_load_selected_accepts_the_real_source(self):
        engine = self.operation.load_selected(self.source)
        derived = {name: dict(bytes=len(row[0]), sha256=self.operation.sha(row[0])) for name, row in engine.SOURCES.items()}
        self.assertEqual(derived, self.operation.EXECUTING_SOURCE_BINDINGS)
        self.assertEqual(engine.GenuineC5Session.__qualname__, self.operation.C5_ENTRYPOINT)

    def test_all_three_operator_copies_equal_the_loaded_engine(self):
        engine = self.operation.load_selected(self.source)
        derived = {name: dict(bytes=len(row[0]), sha256=self.operation.sha(row[0])) for name, row in engine.SOURCES.items()}
        self.assertEqual(constants(PACKET / 'g3_receiving.py')['EXECUTING_SOURCE_BINDINGS'], derived)
        self.assertEqual(constants(PACKET / 'proof_consumer.py')['EXECUTING_SOURCE_PINS'], derived)

    def test_runtime_selectors_match_the_loaded_engine(self):
        engine = self.operation.load_selected(self.source)
        self.run.load_module('runtime_preflight').selection(engine)

    def test_stale_binding_is_refused(self):
        stale = dict(self.operation.EXECUTING_SOURCE_BINDINGS)
        stale['scripts/work-graph-c5-executor.py'] = {
            'bytes': 83099, 'sha256': 'd9b9ad23eefaa62bb273970232dc5669ab40d465c6f9d5bf5f83b7048e8df1d8'}
        saved = self.operation.EXECUTING_SOURCE_BINDINGS
        self.operation.EXECUTING_SOURCE_BINDINGS = stale
        try:
            with self.assertRaisesRegex(ValueError, 'SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY'):
                self.operation.load_selected(self.source)
        finally:
            self.operation.EXECUTING_SOURCE_BINDINGS = saved


if __name__ == '__main__':
    unittest.main()
