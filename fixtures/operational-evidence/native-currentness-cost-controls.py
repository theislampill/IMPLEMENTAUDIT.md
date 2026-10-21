"""Constructed source-owner currentness lifetime controls, no native credit."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT

def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m

class CurrentnessCostControls(unittest.TestCase):
    def setUp(self):
        f=load(ROOT/'fixtures/operational-evidence/native-route-cost-controls.py','currentness_harness')
        f.PEERS=SOURCE/'source-peers/route-graph/skills/implementaudit/scripts'
        self.temp=tempfile.TemporaryDirectory(prefix='currentness-cost-');self.addCleanup(self.temp.cleanup)
        self.h=f.Harness(Path(self.temp.name));self.refusal=f.Refusal
        scope=self.h.patched();scope.__enter__();self.addCleanup(scope.__exit__,None,None,None)

    def test_one_enclosing_currentness_pair_preserves_full_result(self):
        result=self.h.rt.read_current_ordinary_result_v1(self.h.root,self.h.controller)
        self.assertEqual(result,self.h.expected_result())
        self.assertEqual(self.h.rt.current_controller.call_count,2,
                         'one actual currentness acquisition at each end of the enclosing read')

    def test_standalone_pure_validator_keeps_both_currentness_reads(self):
        self.assertEqual(self.h.rt.validate_pure_current_route(self.h.root,self.h.controller),self.h.summary())
        self.assertEqual(self.h.rt.current_controller.call_count,2)

    def test_each_current_field_change_after_use_refuses(self):
        for key in self.h.current:
            with self.subTest(key=key):
                old=copy.deepcopy(self.h.current)
                with self.assertRaises(self.refusal):
                    with self.h.rt.current_route_observation_v1(self.h.root,self.h.controller) as view:
                        view.scope_bytes()
                        self.h.current[key]='foreign'
                self.h.current=old

    def test_full_semantic_input_and_source_checks_remain_after_use(self):
        for kind in ('input','package','child','route'):
            with self.subTest(kind=kind):
                original=self.h.input.read_bytes()
                old=(self.h.source_digest,self.h.child_digest,self.h.oid)
                with self.assertRaises(self.refusal):
                    with self.h.rt.current_route_observation_v1(self.h.root,self.h.controller) as view:
                        view.ordinary_result_bytes()
                        if kind=='input':self.h.input.write_bytes(b'changed')
                        elif kind=='package':self.h.source_digest='sha256:'+'9'*64
                        elif kind=='child':self.h.child_digest='sha256:'+'9'*64
                        else:self.h.oid='9'*40
                self.h.input.write_bytes(original)
                self.h.source_digest,self.h.child_digest,self.h.oid=old

    def test_change_during_provisional_projection_never_returns_a_valid_result(self):
        original=self.h.rt._ordinary_result_from_read_v1
        def changed(*args):
            value=original(*args)
            self.h.current['continuity_receipt']='foreign'
            return value
        with patch.object(self.h.rt,'_ordinary_result_from_read_v1',side_effect=changed):
            with self.assertRaises(self.refusal):
                self.h.rt.read_current_ordinary_result_v1(self.h.root,self.h.controller)

    def test_expected_context_constraint_remains_exact_at_entry(self):
        keys=('controller_id','controller_record_oid','claim_id','explicit_run_root',
              'continuity_generation','continuity_receipt','boundary_kind','boundary_event_id','next_action')
        expected={k:self.h.current[k] for k in keys}
        for key in keys:
            with self.subTest(key=key):
                bad=dict(expected);bad[key]='foreign'
                with self.assertRaises(self.refusal):
                    with self.h.rt.current_route_observation_v1(self.h.root,self.h.controller,bad):
                        self.fail('foreign context yielded a view')

    def continuity(self, changed_helper=False, wrong_verify=False, receipt_raw=None, blob_error=False):
        h=self.h
        owner=ROOT/'source-peers/native-runtime/skills/implementaudit/scripts'
        claim=(owner/'claim-run.sh').read_bytes()
        validate=(owner/'validate-run-root.sh').read_bytes()
        if changed_helper:claim+=b'\n# different source must retain separate verification\n'
        calls=[]
        receipt='refs/implementaudit/continuity-receipts/cost-control/G0001@'+'3'*40
        if receipt_raw is None:
            receipt_raw=b'implementaudit.continuity-receipt.v3\t'+b'\t'.join([b'field']*17)+b'\n'
        self.receipt_reads=[]
        def blob(repo,oid,label,maximum):
            self.assertEqual((repo,oid,maximum),(h.root,'3'*40,512*1024))
            self.receipt_reads.append(oid)
            if blob_error:raise OSError('constructed receipt object unavailable')
            return receipt_raw
        owner=types.SimpleNamespace(_native_child_environment=lambda host:{},_native_blob=blob)
        def file_read(owner,path,*args):
            return (claim if path.name=='claim-run.sh' else validate,0o644)
        def call(owner,host,repo,args,*rest):
            calls.append(args)
            if args==['--current-controller']:return '\t'.join(['cost-control',str(h.root),str(h.root),'2'*32])
            if args[0]=='--require-current-continuity':return receipt
            self.assertEqual(args,['--verify-resume-receipt',receipt])
            return 'wrong' if wrong_verify else receipt
        values=[b'a'*40,b'b'*40,b'',b'',b'',b'']
        response=types.SimpleNamespace(returncode=0,stderr=b'',stdout=json.dumps([base64.b64encode(x).decode() for x in values]).encode())
        with (patch.object(h.wg,'_native_static_owner_module_v1',return_value=(owner,Path('owner.py'),b'owner')),
                patch.object(h.wg,'_native_continuity_host_v1',return_value=object()),
                patch.object(h.wg,'_native_static_file_v1',side_effect=file_read),
                patch.object(h.wg,'_native_claim_call_v1',side_effect=call),
                patch.object(h.wg.subprocess,'run',return_value=response)):
            actual=h.wg._native_continuity(h.root,h.root)
        self.assertEqual(actual['receipt'],receipt)
        self.assertEqual(actual['continuity_helper_digest'],hashlib.sha256(claim).hexdigest())
        return calls

    def test_exact_require_helper_does_not_repeat_its_same_receipt_verifier(self):
        calls=self.continuity()
        self.assertEqual([c[0] for c in calls],['--current-controller','--require-current-continuity'])
        self.assertEqual(self.receipt_reads,['3'*40])

    def test_legacy_TSV_receipt_keeps_original_verifier_refusal(self):
        legacy=b'implementaudit.continuity-receipt.v3\t'+b'\t'.join([b'field']*13)+b'\n'
        with self.assertRaisesRegex(self.h.wg.WorkGraphError,'receipt readback mismatch'):
            self.continuity(receipt_raw=legacy,wrong_verify=True)

    def test_unqualified_receipt_bytes_cannot_skip_verification(self):
        valid=b'implementaudit.continuity-receipt.v3\t'+b'\t'.join([b'field']*17)+b'\n'
        cases=[valid[:-1],valid+b'\n',valid.replace(b'\n',b'\r\n'),
               valid.replace(b'field',b'',1),valid.replace(b'field',b'\x00',1),
               valid.replace(b'field',b'\x7f',1),valid.replace(b'field',b'\xff',1),
               valid.replace(b'.v3',b'.v2',1),valid.replace(b'field',b'fi\neld',1)]
        for raw in cases:
            with self.subTest(raw=repr(raw[:60])),self.assertRaisesRegex(self.h.wg.WorkGraphError,'receipt readback mismatch'):
                self.continuity(receipt_raw=raw,wrong_verify=True)
        with self.assertRaisesRegex(self.h.wg.WorkGraphError,'receipt readback mismatch'):
            self.continuity(blob_error=True,wrong_verify=True)

    def test_other_helper_source_keeps_separate_verification(self):
        calls=self.continuity(changed_helper=True)
        self.assertEqual([c[0] for c in calls],['--current-controller','--require-current-continuity','--verify-resume-receipt'])
        self.assertEqual(self.receipt_reads,[])
        with self.assertRaisesRegex(self.h.wg.WorkGraphError,'receipt readback mismatch'):
            self.continuity(changed_helper=True,wrong_verify=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=ROOT);p.add_argument('--source-root',type=Path)
    args,rest=p.parse_known_args();ROOT=args.repo_root.resolve();SOURCE=(args.source_root or ROOT).resolve()
    unittest.main(argv=[__file__,*rest])
