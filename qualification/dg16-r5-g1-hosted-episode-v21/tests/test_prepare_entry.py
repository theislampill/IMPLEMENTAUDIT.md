"""Offline entry-to-core regression controls; no native operation or issuance.

The exact entry loads its real pinned core and executes the real preparation
gate. Root ownership is a TEST-ONLY boundary represented by the real bounded
public reader; it is not claimed in this unprivileged local fixture.
A separately pinned TEST-ONLY D4 helper replaces host observation and
stops at host_context after the real gate and selector, before every effect.
The gate, its actual module/data readers, and the entry's final wrapper remain
unstubbed. The frozen original operator can be selected for red evidence.
"""
import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest import mock

EP='qualification/dg16-r5-g1-hosted-episode-v21'
OP=Path(os.environ.get('DG16_PREPARE_TEST_OPERATOR',str(Path(__file__).resolve().parents[3])))

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value

class PrepareEntryControls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='TEST_ONLY_prepare_entry_');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.packet=self.root/'fixed-root/packet'
        shutil.copytree(OP/EP/'packet',self.packet)
        self.workspace=self.root/'workspace';self.entrydir=self.workspace/'packet'/EP/'entry';self.entrydir.mkdir(parents=True)
        self.entrypath=self.entrydir/'core_prepare_entry.py'
        shutil.copy2(OP/EP/'entry/core_prepare_entry.py',self.entrypath)
        shutil.copy2(OP/EP/'entry/G1_HOST_PROFILE_POLICY.json',self.entrydir/'G1_HOST_PROFILE_POLICY.json')
        self.entry=load(self.entrypath,'prepare_entry_regression')
        reader=load(self.packet/'public_inputs.py','prepare_fixture_public_reader')
        def read_owned_fixture(path,limit,digest):
            raw=reader.read_exact(path,limit)
            self.assertEqual(sha(raw),digest)
            return raw
        self.entry.read=read_owned_fixture  # TEST-ONLY root-ownership boundary
        self.env=mock.patch.dict(os.environ,{'GITHUB_WORKSPACE':str(self.workspace)});self.env.start();self.addCleanup(self.env.stop)
        self.helper('''def prepare(core, source, output, **kwargs):
    def stop_after_real_gate(*args, **kwargs):
        raise ValueError('TEST_ONLY_POST_PACKET_GATE')
    core.host_context=stop_after_real_gate
    return dict(binding={}, evidence={})
''')

    def helper(self,text):
        raw=text.encode();(self.entrydir/'host_profile_binding.py').write_bytes(raw)
        self.entry.D4_BINDER_SHA256=sha(raw)  # explicit TEST-ONLY physical boundary

    def invoke(self):
        self.entry.main=lambda:self.entry.prepare_core(self.packet)
        self.entry.__name__='__main__'
        tail=next(n for n in ast.parse(self.entrypath.read_bytes()).body if isinstance(n,ast.If) and '__name__' in ast.unparse(n.test))
        out=io.StringIO()
        with contextlib.redirect_stdout(out),self.assertRaises(SystemExit) as ended:
            exec(compile(ast.Module(body=[tail],type_ignores=[]),str(self.entrypath),'exec'),self.entry.__dict__)
        self.assertEqual(ended.exception.code,1)
        self.assertFalse((self.packet.parent/'source').exists())
        self.assertFalse((self.packet.parent/'output').exists())
        value=json.loads(out.getvalue());self.assertEqual(value['authority'],'NONE');self.assertEqual(value['original_awards'],[])
        return value

    def change_declared_modules(self,mutate):
        path=self.packet/'run.py';text=path.read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODULE_PINS' for t in n.targets))
        value=ast.literal_eval(node.value);mutate(value);lines=text.splitlines(keepends=True)
        lines[node.lineno-1:node.end_lineno]=['MODULE_PINS = '+repr(value)+'\n'];path.write_text(''.join(lines))
        self.entry.CORE_RUN_SHA256=sha(path.read_bytes())  # only the disposable test copy

    def test_actual_entry_accepts_exact17_gate_then_reaches_existing_next_boundary(self):
        core=load(self.packet/'run.py','real_packet_gate');self.assertEqual(len(core.MODULE_PINS),17)
        self.assertIn(self.invoke()['code'],('TEST_ONLY_POST_PACKET_GATE','PUBLIC_INPUT_HELD_ROLE_01'))

    def test_missing_declared_module_is_refused_by_real_gate(self):
        self.change_declared_modules(lambda values:values.pop('source_admission'))
        self.assertEqual(self.invoke()['code'],'PACKET_MODULE_POPULATION_REFUSED')

    def test_extra_declared_module_is_refused_by_real_gate(self):
        self.change_declared_modules(lambda values:values.update(unadmitted_module='0'*64))
        self.assertEqual(self.invoke()['code'],'PACKET_MODULE_POPULATION_REFUSED')

    def test_actual_module_body_drift_is_refused_by_real_gate(self):
        path=self.packet/'runtime_preflight.py';path.write_bytes(path.read_bytes()+b'\n')
        self.assertEqual(self.invoke()['code'],'PACKET_MODULE_PIN_REFUSED')

    def test_actual_data_body_drift_is_refused_by_real_gate(self):
        path=self.packet/'ORIGINAL_SCOPE.json';path.write_bytes(path.read_bytes()+b' ')
        self.assertEqual(self.invoke()['code'],'G3_DATA_PIN_REFUSED')

    def test_exact_pinned_core_refusal_is_projected_from_d4_boundary(self):
        self.helper("def prepare(core, *args, **kwargs):\n    raise core.Refusal('HOSTED_IDENTITY_REFUSED')\n")
        self.assertEqual(self.invoke()['code'],'HOSTED_IDENTITY_REFUSED')

    def test_unlisted_core_exception_payload_stays_generic(self):
        self.helper("def prepare(core, *args, **kwargs):\n    raise core.Refusal('UNLISTED_PRIVATE_MARKER')\n")
        value=self.invoke();self.assertEqual(value['code'],'PREPARE_INTERNAL_REFUSAL')
        self.assertNotIn('UNLISTED_PRIVATE_MARKER',json.dumps(value))

    def test_core_refusal_subclass_does_not_gain_enum_projection(self):
        self.helper("def prepare(core, *args, **kwargs):\n    class Other(core.Refusal): pass\n    raise Other('HOSTED_IDENTITY_REFUSED')\n")
        self.assertEqual(self.invoke()['code'],'PREPARE_INTERNAL_REFUSAL')

if __name__=='__main__':unittest.main()
