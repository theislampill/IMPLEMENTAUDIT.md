"""New runtime controls using explicit external-provenance/receiver seams."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
import test_support as F

spec=importlib.util.spec_from_file_location('new_semantic_runtime',Path(__file__).with_name('semantic_receiver.py'))
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


class Runtime(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(getattr(S,'run',None)),'new receiving runtime is missing')
        self.tmp=tempfile.TemporaryDirectory(prefix='INERT_RUNTIME_',dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.workspace=Path(self.tmp.name)

    def execute(self,f,frame_hook=None,writer_hook=None,control=False):
        _,writer=S.source_owners()
        calls=[]
        def frame(maximum,seconds):
            intents=list(f.journal.glob('*/INTENT.json'))
            self.assertEqual(len(intents),1)
            intent=json.loads(intents[0].read_bytes())
            self.assertEqual(intent['operator_receipt_sha256'],f.selected_runtime['operator_receipt']['receipt_sha256'])
            self.assertEqual(intent['authorization_sha256'],'a'*64)
            self.assertGreater(seconds,0);self.assertLessEqual(seconds,45)
            calls.append(intent)
            if frame_hook:frame_hook()
            return f.frame
        resolver=types.SimpleNamespace(read_ephemeral_frame=frame)
        if writer_hook:
            base=writer
            class ControlledWriter(base):
                def write(self,name,raw):
                    super().write(name,raw)
                    writer_hook(name,raw)
            writer=ControlledWriter
        with patch.object(S,'load_receiver',return_value=f.R),patch.object(S,'source_owners',return_value=(resolver,writer)),\
             patch.object(S.time,'time',side_effect=lambda:f.clock[0]):
            if control:
                preparer=F.control_preparer_fixture(S,f)
                with patch.object(S,'load_control_preparer',return_value=preparer):result=S.run(f.selected_runtime)
            else:result=S.run(f.selected_runtime)
        return result,calls

    def test_live_receiving_returns_data_only_and_earlier_request_deadline(self):
        f=F.runtime_fixture(S,self.workspace,live_seconds=5)
        result,calls=self.execute(f)
        self.assertEqual(result['status'],'PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY')
        self.assertEqual(result['expires_ms'],f.request['expires_utc_epoch']*1000)
        self.assertEqual(len(calls),1)
        self.assertFalse(result['original_acceptance'])
        self.assertFalse(result['observation']['review_issued'])
        self.assertTrue((Path(result['journal_path'])/'FINAL.json').exists())

    def test_terminal_receiving_joins_all_seven_and_selects_exact_job_before_frame(self):
        f=F.runtime_fixture(S,self.workspace,role='terminal')
        result,calls=self.execute(f)
        self.assertEqual(result['status'],'PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY')
        self.assertTrue(result['observation']['terminal_log_join']['all_seven_exact'])
        self.assertEqual(calls[0]['job_log_request'],{'repo_full_name':'theislampill/IMPLEMENTAUDIT.md','job_id':123456789})
        self.assertEqual(calls[0]['job_log_tool'],'mcp__codex_apps__github_fetch_workflow_job_logs')
        self.assertNotIn(f.frame.decode(),(Path(result['journal_path'])/'FINAL.json').read_text())

    def test_terminal_wrong_job_refuses_before_readiness(self):
        f=F.runtime_fixture(S,self.workspace,role='terminal')
        for r in (f.selected_runtime['operator_receipt'],f.selected_runtime['independent_receipt']):
            r['facts']['job']['head_sha']='0'*40;F.rehash(r)
        f.selected_runtime['independent_receipt']['independent_operator_receipt_sha256']=f.selected_runtime['operator_receipt']['receipt_sha256']
        F.rehash(f.selected_runtime['independent_receipt'])
        f.selected_runtime['body_outcome']['provider_receipt_sha256']=f.selected_runtime['operator_receipt']['receipt_sha256']
        result,calls=self.execute(f)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY');self.assertEqual(calls,[])

    def test_one_shot_replay_never_reads_another_frame(self):
        f=F.runtime_fixture(S,self.workspace)
        first,first_calls=self.execute(f)
        second,second_calls=self.execute(f)
        self.assertEqual(first['status'],'PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY')
        self.assertEqual(second['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(len(first_calls),1);self.assertEqual(second_calls,[])

    def test_request_expiry_during_frame_returns_unknown_without_final(self):
        f=F.runtime_fixture(S,self.workspace,live_seconds=5)
        result,calls=self.execute(f,frame_hook=lambda:f.clock.__setitem__(0,f.request['expires_utc_epoch']))
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(len(calls),1)
        self.assertEqual(len(list(f.journal.glob('*/UNKNOWN.json'))),1)
        self.assertEqual(list(f.journal.glob('*/FINAL.json')),[])

    def test_final_durable_write_crossing_request_deadline_returns_unknown(self):
        f=F.runtime_fixture(S,self.workspace,live_seconds=5)
        def advance(name,raw):
            if name=='FINAL.json':f.clock[0]=f.request['expires_utc_epoch']
        result,calls=self.execute(f,writer_hook=advance)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(result['stage'],'final-durable-write')
        self.assertEqual(len(list(f.journal.glob('*/FINAL.json'))),1)
        self.assertEqual(len(list(f.journal.glob('*/UNKNOWN.json'))),1)

    def test_changed_archive_after_frame_returns_unknown(self):
        f=F.runtime_fixture(S,self.workspace)
        result,calls=self.execute(f,frame_hook=lambda:(f.live/'ARTIFACT.zip').write_bytes(b'altered'))
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(len(list(f.journal.glob('*/UNKNOWN.json'))),1)

    def test_live_log_substitution_and_terminal_incomplete_wrapper_refuse(self):
        for role,frame in [('live',b'{"unexpected":"log"}'),('terminal',b'{"isError":false}')]:
            with self.subTest(role=role),tempfile.TemporaryDirectory(dir=self.workspace) as d:
                f=F.runtime_fixture(S,Path(d),role=role);f.frame=frame
                result,calls=self.execute(f)
                self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')

    def test_receipt_tamper_misattribution_parent_expiry_and_body_mismatch_refuse_before_frame(self):
        changes=[lambda s:s['operator_receipt'].update(receipt_sha256='b'*64),
            lambda s:s.update(actor='/root'),
            lambda s:s.update(authorization_sha256=None),
            lambda s:s.update(expires_ms=s['operator_receipt']['observed_start_ms']),
            lambda s:s['body_outcome']['archive'].update(sha256='b'*64)]
        for change in changes:
            with self.subTest(change=changes.index(change)),tempfile.TemporaryDirectory(dir=self.workspace) as d:
                f=F.runtime_fixture(S,Path(d));change(f.selected_runtime)
                result,calls=self.execute(f)
                self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY');self.assertEqual(calls,[])

    def test_control_runtime_preserves_original_checks_and_publisher_interface(self):
        f=F.runtime_fixture(S,self.workspace,mode='control')
        result,calls=self.execute(f,control=True)
        self.assertEqual(result['status'],'LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY')
        self.assertEqual(result['provider_effects'],0)
        self.assertEqual(result['original_control_checks']['status'],'ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_PASSED_DATA_ONLY')
        inputs=result['publication_inputs']
        self.assertEqual(set(inputs),{'request_raw','files','create_tree','publication_request','source_authors'})
        self.assertEqual(inputs['files'],{n:b.decode() for n,b in f.payload.items()})
        self.assertEqual(result['expires_ms'],min(f.request['expires_utc_epoch']*1000,f.selected_runtime['expires_ms']))
        self.assertFalse(result['original_acceptance'])

    def test_control_runtime_rejects_changed_frame_before_original_evidence_checks(self):
        f=F.runtime_fixture(S,self.workspace,mode='control');f.frame=b'{}'
        result,calls=self.execute(f,control=True)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(list(f.journal.glob('*/PUBLICATION_REQUEST.json')),[])

    def test_control_runtime_rejects_review_final_mismatch_and_writes_no_decision(self):
        f=F.runtime_fixture(S,self.workspace,mode='control')
        f.final['actual_live_evidence_reviewed']=False
        F.replace_fixture(f.review/'FINAL.json',F.encode(f.final))
        f.selected['independent_review_seal_sha256']=F.seal(f.review)
        frame=json.loads(f.frame)
        frame['review_seal_sha256']=f.selected['independent_review_seal_sha256']
        frame['root_decision_input']=F.refreshed_root_input(f)
        f.frame=F.canonical(frame)
        f.selected_runtime['control']['frame_sha256']=F.desc(f.frame)['sha256']
        result,calls=self.execute(f,control=True)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(list(f.journal.glob('*/ROOT_CONSUMPTION.json')),[])


if __name__=='__main__':
    unittest.main(verbosity=2)
