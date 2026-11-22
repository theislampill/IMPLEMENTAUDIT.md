"""Source-only controls for the genuine pinned run supplier and public validator."""
import json
from pathlib import Path
import tempfile
import unittest

from test_joint_source import BASE, CORE, INSTALL, N, NSS_CODES, nss_record, pin, runtime_class


class RuntimeSupplierTests(unittest.TestCase):
    member = 'tree/' + CORE + 'nss_configuration.py'
    phases = ('RESERVED', 'PREIMAGE_RETAINED', 'TEMPORARY_CREATED', 'REPLACE_OUTCOME_UNKNOWN',
              'CONFIGURED_AND_READ_BACK', 'CONFIGURATION_REFUSED')

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='g132-runtime-source-control-')
        self.addCleanup(temp.cleanup)
        cls = runtime_class((BASE/'source/current_pro_interfaces.py').read_bytes())
        self.owner = object.__new__(cls)
        self.owner.root = Path(temp.name)
        self.owner.index = {'files': {}}
        self.owner.phase = {'members': {}}
        self.owner._plan = json.loads((INSTALL/'PURE_SOURCE_PLAN.json').read_bytes())
        self.owner._modules = {}
        for name in ('pure/run.py', 'pure/g3.py'):
            self.fixture(name, (INSTALL/name).read_bytes())
        self.original = (N/CORE/'nss_configuration.py').read_bytes()
        self.set_nss(self.original)
        self.run = self.owner.module('run')
        self.load = self.run.validate_nss_effect.__globals__['load_module']

    def fixture(self, name, raw, *, repin=True):
        path = self.owner.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.chmod(0o600)
        path.write_bytes(raw)
        path.chmod(0o400)
        if repin:
            self.owner.index['files'][name] = pin(raw)

    def set_nss(self, raw):
        self.fixture('phase/' + self.member, raw)
        self.owner.phase['members'][self.member] = pin(raw)

    def test_public_validator_and_exact_data_surface(self):
        data = self.load('nss_configuration')
        self.assertEqual(set(vars(data)), {'PHASES', 'REFUSALS'})
        self.assertEqual(data.PHASES, self.phases)
        self.assertIs(type(data.REFUSALS), frozenset)
        self.assertEqual(len(data.REFUSALS), 24)
        self.assertTrue(set(NSS_CODES) <= data.REFUSALS)
        for phase in self.phases:
            value = dict(nss_record(None), phase=phase)
            self.assertEqual(self.run.validate_nss_effect(value), value)
        for code in (*NSS_CODES, 'NSS_CONFIGURATION_UNCLASSIFIED_REFUSAL'):
            value = nss_record(code)
            self.assertEqual(self.run.validate_nss_effect(value), value)
        for value in (nss_record('UNIT_UNKNOWN'), dict(nss_record(None), phase='UNIT_UNKNOWN')):
            with self.assertRaisesRegex(self.run.Refusal, '^NSS_EFFECT_PUBLIC_SCHEMA$'):
                self.run.validate_nss_effect(value)

    def test_g3_dispatch_and_unsupported_names(self):
        self.assertIs(self.load('g3_receiving'), self.owner.module('g3'))
        for name in ('g3', 'os', 'ctypes', '../nss_configuration', 'nss_configuration.py', None):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, '^PURE_MODULE_ONLY$'):
                self.load(name)

    def test_cached_run_rereads_pinned_phase_body(self):
        value = nss_record(NSS_CODES[0])
        self.assertEqual(self.run.validate_nss_effect(value), value)
        self.fixture('phase/' + self.member, self.original + b'\n', repin=False)
        self.assertIs(self.owner.module('run'), self.run)
        with self.assertRaisesRegex(ValueError, '^FIXED_SOURCE_PIN$'):
            self.run.validate_nss_effect(value)
        self.fixture('phase/' + self.member, self.original + b'\n')
        with self.assertRaisesRegex(ValueError, '^PHASE_BODY_JOIN$'):
            self.run.validate_nss_effect(value)
        self.owner.phase['members'].clear()
        with self.assertRaisesRegex(ValueError, '^FIXED_PHASE_MEMBER$'):
            self.run.validate_nss_effect(value)

    def test_body_is_data_only(self):
        self.set_nss(b"raise RuntimeError('UNIT_NSS_BODY_MUST_NEVER_EXECUTE')\n"
                     b"PHASES = ('UNIT_PHASE',)\nREFUSALS = frozenset({'UNIT_CODE'})\n")
        self.assertEqual(vars(self.load('nss_configuration')),
                         {'PHASES': ('UNIT_PHASE',), 'REFUSALS': frozenset({'UNIT_CODE'})})

    def test_missing_duplicate_and_dynamic_bindings(self):
        p = "PHASES = ('P',)\n"
        r = "REFUSALS = frozenset({'R'})\n"
        cases = {
            'missing phases': r, 'missing refusals': p, 'duplicate phases': p+r+p,
            'duplicate refusals': p+r+r, 'annotated rebind': p+r+"PHASES: tuple = ('X',)\n",
            'conditional rebind': p+r+"if True:\n    PHASES = ('X',)\n",
            'import rebind': p+r+'import other as PHASES\n',
            'function rebind': p+r+'def REFUSALS(): pass\n',
            'chained targets': "PHASES = OTHER = ('X',)\n"+r,
            'dynamic phase': 'PHASES = tuple()\n'+r, 'phase list': "PHASES = ['P']\n"+r,
            'wrong callee': p+"REFUSALS = set({'R'})\n",
            'attribute callee': p+"REFUSALS = builtins.frozenset({'R'})\n",
            'extra argument': p+"REFUSALS = frozenset({'R'}, {'X'})\n",
            'keyword constructor': p+"REFUSALS = frozenset(value={'R'})\n",
            'non-set argument': p+"REFUSALS = frozenset(('R',))\n",
            'dynamic item': p+"REFUSALS = frozenset({f()})\n",
            'duplicate member': p+"REFUSALS = frozenset({'R', 'R'})\n",
            'non-string phase': "PHASES = (1,)\n"+r,
        }
        for case, raw in cases.items():
            self.set_nss(raw.encode())
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, '^NSS_DATA_'):
                self.load('nss_configuration')
