#!/usr/bin/env python3
"""Constructed admission controls use temporary copies and never issue authority."""
import copy,hashlib,json,os,shutil,subprocess,tempfile,types,unittest
from pathlib import Path
PACKET=Path(__file__).resolve().parents[1]/'packet'
SOURCE_ENV='DG16_TEST_SOURCE_ROOT'

def pretty(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def pin(raw):return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

class SourceAdmissionCases(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='runtime-source-bridge-controls-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.packet=self.root/'packet';shutil.copytree(PACKET,self.packet)
        path=self.packet/'source_admission.py';self.assertTrue(path.is_file(),'the explicit successor source bridge is not implemented')
        self.A=types.ModuleType('source_admission_controls');self.A.__file__=str(path)
        exec(compile(path.read_bytes(),str(path),'exec'),self.A.__dict__)
        self.record_path=self.packet/'public-inputs/SOURCE_SUCCESSOR_ADMISSION.json'
        self.proposal=json.loads(self.record_path.read_bytes())
        # Test-only fixture is reset to unissued state; no production receipt.
        self.proposal.update(state='HELD_PENDING_INDEPENDENT_ROOT_REVIEW', issuer=None, decision=None)
        raw=pretty(self.proposal);self.record_path.write_bytes(raw);self.A.ADMISSION_PIN=pin(raw)

    def admit_for_test(self,record=None):
        # Exact TEST-ONLY bytes and pin on a copied module, never real issued records.
        value=copy.deepcopy(record or self.proposal)
        value.update(state='ADMITTED_PROSPECTIVELY',issuer='R5_ROOT_GOVERNOR',decision='ADMIT_EXACT_RUNTIME_SUCCESSOR_SOURCE_RELATION')
        raw=pretty(value);self.record_path.write_bytes(raw);self.A.ADMISSION_PIN=pin(raw)
        return value

    def source_fixture(self):
        configured=os.environ.get(SOURCE_ENV)
        self.assertTrue(configured, SOURCE_ENV+' must explicitly name the exact admitted source fixture')
        origin=Path(configured).resolve(strict=True)
        observed=subprocess.check_output(['git','-C',str(origin),'rev-parse','HEAD','HEAD^{tree}'],text=True).splitlines()
        self.assertEqual(observed,[self.proposal['subject']['commit'],self.proposal['subject']['tree']])
        source=self.root/'source';source.mkdir()
        for row in self.proposal['native_members']+self.proposal['package_dependencies']:
            target=source/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():
                raw=(origin/row['path']).read_bytes()
                self.assertEqual(pin(raw),dict(bytes=row['bytes'],sha256=row['sha256']))
                target.write_bytes(raw);target.chmod(0o755 if row['mode']=='100755' else 0o644)
        return source

    def test_admitted_constructed_bridge_receives_exact_retained_evidence(self):
        self.admit_for_test();source=self.source_fixture()
        value=self.A.receive(self.packet,source=source)
        self.assertEqual(value['subject'],self.proposal['subject'])
        self.assertEqual((len(value['native_members']),len(value['package_dependencies'])),(89,79))
        self.assertFalse(value['historical_job_ran_successor_source'])

    def test_unissued_proposal_refuses(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_ADMISSION_HELD'):
            self.A.receive(self.packet)

    def test_wrong_subject_refuses_even_with_test_only_pin(self):
        value=self.admit_for_test();value['subject']['commit']='0'*40
        self.admit_for_test(value)
        with self.assertRaisesRegex(ValueError,'SOURCE_ADMISSION_SUBJECT'):
            self.A.receive(self.packet)

    def test_missing_bridge_refuses(self):
        self.record_path.unlink()
        with self.assertRaises((OSError,ValueError)):self.A.receive(self.packet)

    def test_changed_relevant_member_refuses(self):
        self.admit_for_test();source=self.source_fixture()
        path=source/self.proposal['native_members'][0]['path'];path.write_bytes(path.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError,'SOURCE_CURRENT_MEMBER'):
            self.A.receive(self.packet,source=source)

    def test_flipped_retained_disposition_refuses(self):
        self.admit_for_test()
        path=self.packet/'public-inputs/COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'
        value=json.loads(path.read_bytes());name=next(iter(value['reviewed_changed_member_rows']))
        value['reviewed_changed_member_rows'][name]='COVERED' if value['reviewed_changed_member_rows'][name]!='COVERED' else 'PARTIAL'
        path.write_bytes(pretty(value))
        with self.assertRaisesRegex(ValueError,'SOURCE_RETAINED_EVIDENCE'):
            self.A.receive(self.packet)

    def test_currentness_drift_after_initial_capture_refuses(self):
        self.admit_for_test();source=self.source_fixture();changed=False
        target=source/self.proposal['native_members'][0]['path'];reader=self.A.read_ordinary
        def read_and_change(path,limit):
            nonlocal changed
            raw,identity=reader(path,limit)
            if Path(path)==target and not changed:
                changed=True;target.write_bytes(raw+b'\n')
            return raw,identity
        self.A.read_ordinary=read_and_change
        with self.assertRaisesRegex(ValueError,'SOURCE_CURRENT_(MEMBER|CLOSING)'):
            self.A.receive(self.packet,source=source)
        self.assertTrue(changed)

if __name__=='__main__':unittest.main()
