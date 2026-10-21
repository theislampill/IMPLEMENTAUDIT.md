"""Constructed source-owner currentness lifetime controls, no native credit."""
import argparse
import contextlib
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

    def test_opening_uses_one_complete_currentness_pair(self):
        self.assertEqual(self.h.rt.read_current_episode_binding_v1(self.h.root,self.h.controller),
                         self.h.expected_opening())
        self.assertEqual(self.h.rt.current_controller.call_count,2)

    def test_missing_execution_remains_fenced_and_unavailable(self):
        original=self.h.git
        def read(repo,*args,**kwargs):
            if args[:2]==('for-each-ref','--format=%(objectname) %(refname)'): return ''
            return original(repo,*args,**kwargs)
        with patch.object(self.h.rt,'git',side_effect=read):
            self.assertIsNone(self.h.rt.read_current_ordinary_execution_v1(self.h.root,self.h.controller))
            self.assertEqual(self.h.rt.current_controller.call_count,2)

    def test_execution_view_refuses_late_receipt_publication_and_closed_reuse(self):
        original=self.h.git; present=False
        def read(repo,*args,**kwargs):
            if args[:2]==('for-each-ref','--format=%(objectname) %(refname)'):
                return ('9'*40+' '+args[2]) if present else ''
            return original(repo,*args,**kwargs)
        with patch.object(self.h.rt,'git',side_effect=read):
            with self.assertRaises((self.refusal,KeyError)):
                with self.h.rt.current_route_observation_v1(self.h.root,self.h.controller) as view:
                    self.assertEqual(view.ordinary_execution_bytes(),b'null')
                    present=True
            with self.assertRaises(self.refusal): view.ordinary_execution_bytes()

    def test_execution_receipt_and_attempt_keep_exact_custody(self):
        rt=self.h.rt; canonical=self.h.expected_result(); ref=rt._ordinary_execution_ref_v1(self.h.controller,canonical)
        attempt_ref=ref.replace('/ordinary-receivers/','/ordinary-receiver-attempts/')
        execution=dict(schema='implementaudit.ordinary-receiver-execution.v1',policy_digest='1'*64,
            opening_digest=canonical['opening']['opening_digest'],return_digest=canonical['child_return']['digest'],
            acceptance_digest=canonical['governor_decision']['digest'],argv=[],python_pin={},source_pin={},
            exit_code=0,stdout='actual output',stdout_sha256=hashlib.sha256(b'actual output').hexdigest(),
            stderr_sha256=hashlib.sha256(b'').hexdigest())
        receipt=dict(schema='implementaudit.ordinary-receiver-record.v2',accepted_record_oid=self.h.oid,
            opening_digest=canonical['opening']['opening_digest'],attempt_oid='7'*40,
            execution=execution,execution_digest=rt.digest_json(execution))
        self.h.objects['8'*40]=receipt
        self.h.objects['7'*40]=rt._ordinary_attempt_v2(canonical,execution['policy_digest'])
        refs={ref:'8'*40,attempt_ref:'7'*40}; original=self.h.git
        def read(repo,*args,**kwargs):
            if args[:2]==('for-each-ref','--format=%(objectname) %(refname)'):return refs[ref]+' '+ref
            if args[:2]==('rev-parse','--verify') and args[2] in refs:return refs[args[2]]
            return original(repo,*args,**kwargs)
        with patch.object(rt,'git',side_effect=read):
            with rt.current_route_observation_v1(self.h.root,self.h.controller) as view:
                value=json.loads(view.ordinary_execution_bytes())
            self.assertEqual((value['ref'],value['oid']),(ref,'8'*40))
            self.assertEqual(json.loads(base64.b64decode(value['wire']['bytes_b64'])),receipt)
            self.assertEqual(rt.current_controller.call_count,2)
            for changed_ref in (ref,attempt_ref):
                with self.subTest(changed_ref=changed_ref),self.assertRaises((self.refusal,KeyError)):
                    with rt.current_route_observation_v1(self.h.root,self.h.controller) as view:
                        view.ordinary_execution_bytes(); refs[changed_ref]='9'*40
                refs.update({ref:'8'*40,attempt_ref:'7'*40})

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

    def continuity(self, changed_helper=False, wrong_verify=False, receipt_raw=None, blob_error=False, source_changes=False):
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
            self.assertEqual(rest,(claim,validate))
            calls.append(args)
            if args==['--current-controller']:return '\t'.join(['cost-control',str(h.root),str(h.root),'2'*32])
            if args[0]=='--require-current-continuity':return receipt
            self.assertEqual(args,['--verify-resume-receipt',receipt])
            return 'wrong' if wrong_verify else receipt
        values=[b'a'*40,b'b'*40,b'',b'',b'',b'']
        response=types.SimpleNamespace(returncode=0,stderr=b'',stdout=json.dumps([base64.b64encode(x).decode() for x in values]).encode())
        self.current_owner_reads=[]
        with (patch.object(h.wg,'_native_static_owner_module_v1',side_effect=[
                    (owner,Path('owner.py'),b'owner'),(owner,Path('owner.py'),b'changed' if source_changes else b'owner')]),
                patch.object(h.wg,'_native_continuity_host_v1',return_value=object()),
                patch.object(h.wg,'_native_static_file_v1',side_effect=file_read),
                patch.object(h.wg,'_native_claim_call_v1',side_effect=call),
                patch.object(h.wg.subprocess,'run',return_value=response)):
            sources=[]
            actual=h.wg._native_continuity(h.root,h.root,_source_reads=sources,_current_reads=self.current_owner_reads)
        self.assertEqual(actual['receipt'],receipt)
        self.assertEqual(actual['continuity_helper_digest'],hashlib.sha256(claim).hexdigest())
        self.assertEqual(sources,[{'claim_sha256':hashlib.sha256(claim).hexdigest(),
                                   'validate_sha256':hashlib.sha256(validate).hexdigest()}])
        self.assertEqual(self.current_owner_reads,[dict(controller_result=['cost-control',str(h.root),str(h.root),'2'*32],receipt=receipt)])
        return calls

    def test_changed_terminal_source_emits_no_currentness_output(self):
        with self.assertRaisesRegex(self.h.wg.WorkGraphError,'static owner source changed'):
            self.continuity(source_changes=True)
        self.assertEqual(self.current_owner_reads,[])

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

class CurrentOwnerParserControls(unittest.TestCase):
    def setUp(self):
        self.rt=load(SOURCE/'source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py','current_owner_parser')
        self.temp=tempfile.TemporaryDirectory(prefix='current-owner-parser-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.ctrl='constructed-owner';self.claim='2'*32
        self.receipt='refs/implementaudit/continuity-receipts/'+self.ctrl+'/G0001@'+'3'*40
        self.parts=[self.ctrl,str(self.root),str(self.root),self.claim]
        self.invalidation=['implementaudit.continuity-invalidation.v1',self.ctrl,'unused','unused','manual-resume','boundary']

    def receipt_fields(self,version):
        if version==3:
            fields=['unused']*18
            for i,v in {0:'implementaudit.continuity-receipt.v3',1:self.ctrl,2:self.claim,3:self.root.name,
                4:'G0001',5:'4'*40,6:'refs/implementaudit/current-generations/'+self.ctrl,16:'next'}.items():fields[i]=v
        else:
            fields=['unused']*12
            for i,v in {0:'implementaudit.continuity-receipt.v2',1:self.ctrl,3:self.claim,8:'4'*40,
                9:'manual-resume',10:'G0001',11:'next'}.items():fields[i]=v
        return fields

    @contextlib.contextmanager
    def io(self,raw):
        def fail(message,**kw):raise ValueError(message)
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(self.rt,'fail',side_effect=fail))
            stack.enter_context(patch.object(self.rt,'git_blob_bytes',side_effect=lambda repo,oid,*a,**k:
                raw if oid=='3'*40 else ('\t'.join(self.invalidation)+'\n').encode()))
            stack.enter_context(patch.object(self.rt,'git',return_value='1'*40))
            stack.enter_context(patch.object(self.rt,'trusted_host_executable',return_value=self.root/'bash'))
            self.calls=stack.enter_context(patch.object(self.rt,'run',side_effect=lambda *a,**k:
                '\t'.join(self.parts) if k['label']=='controller currentness' else self.receipt))
            yield

    def test_real_parser_preserves_v2_and_strict_v3_complete_current_tuple(self):
        expected=dict(controller_id=self.ctrl,repository_identity=str(self.root),explicit_run_root=str(self.root),
            claim_id=self.claim,continuity_receipt=self.receipt,continuity_generation='G0001',
            controller_record_oid='1'*40,boundary_kind='manual-resume',boundary_event_id='boundary',next_action='next')
        for version in (2,3):
            with self.subTest(version=version),self.io(('\t'.join(self.receipt_fields(version))+'\n').encode()):
                self.assertEqual(self.rt.current_controller(self.root,self.ctrl,environment={}),expected)
                self.assertEqual(self.calls.call_count,2)
                self.assertEqual(self.rt._current_controller_from_owner_read_v1(self.root,self.ctrl,self.parts,self.receipt),expected)
                self.assertEqual(self.calls.call_count,2,'parsing actual owner output must not launch another owner')

    def test_legacy_v3_and_wrong_receipt_domains_still_refuse(self):
        fields=self.receipt_fields(3);valid=('\t'.join(fields)+'\n').encode()
        cases=[('\t'.join(fields[:14])+'\n').encode(),valid+b'\n',valid.replace(b'\t',b'\n',1),valid.replace(b'\t',b'\x00',1)]
        for index in (0,1,2,3,4,6):
            changed=list(fields);changed[index]='foreign';cases.append(('\t'.join(changed)+'\n').encode())
        for raw in cases:
            with self.subTest(raw=raw[:60]),self.io(raw):
                with self.assertRaises(ValueError):self.rt._current_controller_from_owner_read_v1(self.root,self.ctrl,self.parts,self.receipt)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=ROOT);p.add_argument('--source-root',type=Path)
    args,rest=p.parse_known_args();ROOT=args.repo_root.resolve();SOURCE=(args.source_root or ROOT).resolve()
    unittest.main(argv=[__file__,*rest])
