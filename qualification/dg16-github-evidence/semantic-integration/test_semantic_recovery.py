"""Focused new-source tests. Positive fixtures confer no actual authority."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import test_support as F

PATH = Path(__file__).with_name('semantic_receiver.py')
S = None
if PATH.exists():
    spec = importlib.util.spec_from_file_location('new_semantic_receiver', PATH)
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)


class NewSource(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(S, 'new semantic_receiver.py implementation is missing')
        self.tmp = tempfile.TemporaryDirectory(prefix='INERT_TEST_',dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)

    def test_real_connector_log_wrapper_shape_preserves_exact_text(self):
        wrapper = {'content':[{'type':'text','text':'Action completed.'}],
            'structuredContent':{'content':'actual decoded shape\r\n\u03b1'},'isError':False}
        self.assertEqual(S.decode_log_wrapper(F.canonical(wrapper)),b'actual decoded shape\r\n\xce\xb1')

    def test_duplicate_nonfinite_partial_error_and_unknown_log_envelopes_refuse(self):
        wrapper = {'content':[{'type':'text','text':'Action completed.'}],
            'structuredContent':{'content':'x'},'isError':False}
        cases = [b'{"isError":false,"isError":true}',b'{"x":NaN}']
        for mutate in (lambda w:w.update(isError=True),lambda w:w.update(_meta={'partial':True}),
                       lambda w:w['structuredContent'].update(extra='unknown')):
            value = json.loads(json.dumps(wrapper));mutate(value);cases.append(F.canonical(value))
        for raw in cases:
            with self.subTest(raw=raw),self.assertRaises((ValueError,TypeError)):
                S.decode_log_wrapper(raw)

    def test_original_seven_member_log_join_accepts_only_complete_matching_envelopes(self):
        R,U,archive,files,log,metadata,binding = F.retained_terminal()
        joined = R.match_terminal_log(files,S.decode_log_wrapper(F.canonical({
            'content':[{'type':'text','text':'Action completed.'}],
            'structuredContent':{'content':log.decode()},'isError':False})))
        self.assertTrue(joined['all_seven_exact'])
        self.assertEqual(len(joined['members']),7)
        self.assertFalse(joined['currentness_or_award'])
        for bad in (b'\n'.join(log.splitlines()[:-1]),log+log.splitlines()[0]+b'\n',
                    log.replace(b'"bytes":',b'"bytes":1',1)):
            with self.subTest(kind=len(bad)),self.assertRaises(ValueError):
                R.match_terminal_log(files,bad)

    def test_retained_failed_archive_metadata_joins_without_relabeling_source(self):
        R,U,archive,files,log,metadata,binding = F.retained_terminal()
        got = R.metadata_bindings(metadata,'terminal',str(metadata['run']['id']),
            metadata['run']['head_sha'],F.desc(archive),binding)
        self.assertEqual(got['run_id'],'43623218185')
        self.assertEqual(got['archive'],{'bytes':12857,'sha256':'3c7913493f366a0e27fc380b7269b7bfb4560f31b9cdfeb5652632274a11c634'})
        altered = json.loads(json.dumps(metadata));altered['commit']['parents'].append({'sha':'f'*40})
        with self.assertRaisesRegex(ValueError,'ACTUAL_COMMIT_TREE_PARENT'):
            R.metadata_bindings(altered,'terminal',str(metadata['run']['id']),metadata['run']['head_sha'],F.desc(archive),binding)

    def test_inspect_adapter_calls_original_inspect_and_requires_terminal_log(self):
        R,U,archive,files,log,metadata,binding = F.retained_terminal()
        called = []
        R.inspect = lambda *a,**k: called.append((a,k)) or {
            'authority':'NONE','original_acceptance':False,'review_issued':False,'root_consumption_issued':False}
        context = {'run_id':str(metadata['run']['id']),'workflow_commit':metadata['run']['head_sha']}
        result = S.inspect_public(R,archive,'terminal',context,metadata,terminal_log=log)
        self.assertTrue(result['terminal_log_join']['all_seven_exact'])
        self.assertEqual(called[0][1]['archive'],F.desc(archive))
        with self.assertRaises(ValueError):
            S.inspect_public(R,archive,'terminal',context,metadata)
        with self.assertRaises(ValueError):
            S.inspect_public(R,archive,'live',context,metadata,terminal_log=log)

    def test_original_inspect_rejects_historical_code_mismatch(self):
        R,U,archive,files,log,metadata,binding = F.retained_terminal()
        binding['modules'] = {'run.py':{'sha256':'0'*64}}
        R.verified = lambda: (binding,{}, {},{'host_utility.py':U,'run.py':object(),'capture_evidence.py':object()}, {}, {})
        context = {'run_id':str(metadata['run']['id']),'workflow_commit':metadata['run']['head_sha']}
        with self.assertRaisesRegex(ValueError,'PUBLIC_CODE_BINDING'):
            S.inspect_public(R,archive,'terminal',context,metadata,terminal_log=log)

    def test_changed_original_source_refuses_before_loading(self):
        path = self.workspace/'owner.py';path.write_bytes(b'raise RuntimeError("must never execute")\n')
        with patch.object(S,'ORIGINAL_BINDER',path),self.assertRaisesRegex(ValueError,'ORIGINAL_BINDER'):
            S.bound_receiver_source(b'{}',b'{}')

    def test_bound_source_is_only_original_five_assignment_transform(self):
        runtime = {'workspace_root':str(self.workspace),'receiver_output_root':str(self.workspace/'out'),
            'maintained_source_root':str(self.workspace/'source')}
        binding = b'{"INERT_TEST_ONLY":true}\n'
        raw = S.bound_receiver_source(F.encode(runtime),binding)
        binder = F.module(F.CUSTODY/'author/bind_public_successor.py')
        literal = binder.literals(raw)
        self.assertEqual(literal['BINDING_SHA'],F.desc(binding)['sha256'])
        self.assertEqual(literal['RUNTIME_BINDING_SHA'],F.desc(F.encode(runtime))['sha256'])
        altered = raw.replace(b'def verified():',b'def verified_bypass():')
        with self.assertRaisesRegex(ValueError,'BOUND_RECEIVER_SOURCE'):
            S.require_bound_source(altered,F.encode(runtime),binding)

    def test_unbound_or_changed_installation_fails_closed(self):
        directory = self.workspace/'receiver';directory.mkdir()
        selected = {'directory':str(directory),'receiver_sha256':'1'*64,'seal_sha256':'2'*64,
            'binding_sha256':'3'*64,'runtime_sha256':'4'*64}
        with self.assertRaises((ValueError,FileNotFoundError)):
            S.load_receiver(selected,{})
        (directory/'public_receiver.py').write_text('raise RuntimeError("untrusted source")\n')
        with self.assertRaises((ValueError,FileNotFoundError)):
            S.load_receiver(selected,{})

    def test_self_consistent_forged_receiver_source_is_not_executed(self):
        runtime={'workspace_root':str(self.workspace),'receiver_output_root':str(self.workspace/'out'),
            'maintained_source_root':str(self.workspace/'source'),'issuer_thread':'PRO-EXECUTOR-01','session':'PRO-EXECUTOR-01'}
        context={'repository':'theislampill/IMPLEMENTAUDIT.md','branch':'pro/dg16-r5-full-g2-direct-host-99-20261115',
            'source_commit':'1'*40,'source_tree':'2'*40,'workflow_tree':'3'*40}
        binding={**{k:context[k] for k in ('repository','branch','source_commit','source_tree')},
            'final_tree':context['workflow_tree'],'control_branch':context['branch'].replace('-host-','-control-'),
            'session':'PRO-EXECUTOR-01'}
        directory=self.workspace/'receiver';directory.mkdir()
        marker=self.workspace/'UNTRUSTED_CODE_EXECUTED'
        raw=S.bound_receiver_source(F.encode(runtime),F.encode(binding))
        raw+=('\nPath('+repr(str(marker))+').write_text("executed")\n').encode()
        files={name:b'{}\n' for name in S.RECEIVER_NAMES}
        files.update({'public_receiver.py':raw,'SUCCESSOR_RUNTIME_BINDING.json':F.encode(runtime),'BINDING.json':F.encode(binding)})
        for name,body in files.items():
            (directory/name).write_bytes(body);(directory/name).chmod(0o400)
        selected={'directory':str(directory),'receiver_sha256':F.desc(raw)['sha256'],
            'binding_sha256':F.desc(files['BINDING.json'])['sha256'],
            'runtime_sha256':F.desc(files['SUCCESSOR_RUNTIME_BINDING.json'])['sha256'],'seal_sha256':F.seal(directory)}
        with self.assertRaisesRegex(ValueError,'BOUND_RECEIVER_SOURCE_CHANGED'):
            S.load_receiver(selected,context)
        self.assertFalse(marker.exists())
        (directory/'public_receiver.py').chmod(0o600)
        with self.assertRaisesRegex(ValueError,'IMMUTABLE_RECEIVER_MEMBER_MODE'):
            S.load_receiver(selected,context)

    def test_checked_file_rejects_symlink_hardlink_and_changed_path(self):
        path=self.workspace/'data';path.write_bytes(b'public')
        self.assertEqual(S.checked_file(path,6),b'public')
        with self.assertRaises(ValueError): S.checked_file(path,5)
        link=self.workspace/'link';link.symlink_to(path)
        with self.assertRaises(ValueError): S.checked_file(link,6)
        hard=self.workspace/'hard';os.link(path,hard)
        with self.assertRaises(ValueError): S.checked_file(path,6)

    def control(self):
        f=F.live_fixture(self.workspace)
        P,raw=F.control_preparer_fixture(S,f)
        return f,P,raw

    def verify_control(self,f,P,raw):
        with patch.object(S,'load_control_preparer',return_value=(P,raw)):
            return S.verify_original_control_inputs(f.R,str(f.live),F.refreshed_root_input(f),
                f.payload,F.AUTHORS,f.selected['independent_review_seal_sha256'],f.archive,f.metadata)

    def test_original_control_verification_prefix_accepts_complete_inert_inputs_without_issuing(self):
        f,P,raw=self.control()
        result=self.verify_control(f,P,raw)
        self.assertEqual(result['status'],'ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_PASSED_DATA_ONLY')
        self.assertFalse(result['root_consumption_issued'])
        self.assertFalse((self.workspace/'public-control-preparation').exists())
        self.assertEqual(result['request_sha256'],F.desc(f.request_raw)['sha256'])

    def test_original_control_rejects_missing_extra_or_changed_review_members(self):
        for case in ('missing','extra','changed','mode'):
            with self.subTest(case=case):
                with tempfile.TemporaryDirectory(dir=self.workspace) as d:
                    f=F.live_fixture(Path(d));P,raw=F.control_preparer_fixture(S,f)
                    if case=='missing':(f.review/'FINAL.json').unlink()
                    elif case=='extra':(f.review/'EXTRA').write_bytes(b'unknown')
                    elif case=='changed':F.replace_fixture(f.review/'FINAL.json',b'{}')
                    else:(f.review/'FINAL.json').chmod(0o600)
                    with self.assertRaises((AssertionError,ValueError,FileNotFoundError)):
                        self.verify_control(f,P,raw)

    def test_original_control_rejects_current_seal_with_invalid_final(self):
        for field,value in [('state','DRAFT'),('disposition','FAIL'),('actual_live_evidence_reviewed',False),
                            ('receiver_binding_sha256','a'*64),('request_sha256','b'*64),('proof_sha256','c'*64)]:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(dir=self.workspace) as d:
                    f=F.live_fixture(Path(d));f.final[field]=value
                    F.replace_fixture(f.review/'FINAL.json',F.encode(f.final))
                    f.selected['independent_review_seal_sha256']=F.seal(f.review)
                    P,raw=F.control_preparer_fixture(S,f)
                    with self.assertRaises(AssertionError): self.verify_control(f,P,raw)

    def test_original_control_rejects_root_fields_issuer_review_body_and_request_proof_changes(self):
        for field,value in [('schema','unknown'),('issuer_thread','old-issuer'),('actual_evidence_and_review_read',False),
                            ('current_control_branch_absence_received',False),('automatic_replay',True),
                            ('independent_review_body_sha256','a'*64),('request_sha256','b'*64),('proof_sha256','c'*64)]:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(dir=self.workspace) as d:
                    f=F.live_fixture(Path(d));f.selected[field]=value;P,raw=F.control_preparer_fixture(S,f)
                    with self.assertRaises(AssertionError):self.verify_control(f,P,raw)
        f,P,raw=self.control();del f.selected['actor']
        with self.assertRaises(AssertionError):self.verify_control(f,P,raw)

    def test_original_control_requires_all_actual_authors_and_distinct_reviewer(self):
        f,P,raw=self.control()
        for authors in ([F.AUTHORS[0]],F.AUTHORS+[F.REVIEWER]):
            with patch.object(S,'load_control_preparer',return_value=(P,raw)),self.assertRaises(ValueError):
                S.verify_original_control_inputs(f.R,str(f.live),F.refreshed_root_input(f),f.payload,authors,
                    f.selected['independent_review_seal_sha256'],f.archive,f.metadata)

    def test_optimized_interpreter_preserves_original_control_assertions(self):
        code = """
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
import semantic_receiver as S
import test_support as F
f=F.live_fixture(Path(sys.argv[2]))
f.final['state']='DRAFT'
F.replace_fixture(f.review/'FINAL.json',F.encode(f.final))
f.selected['independent_review_seal_sha256']=F.seal(f.review)
P,raw=F.control_preparer_fixture(S,f)
with patch.object(S,'load_control_preparer',return_value=(P,raw)):
    try:
        S.verify_original_control_inputs(f.R,str(f.live),F.refreshed_root_input(f),f.payload,F.AUTHORS,
            f.selected['independent_review_seal_sha256'],f.archive,f.metadata)
    except (AssertionError,ValueError):
        print('REFUSED')
    else:
        print('ACCEPTED_INVALID_FINAL')
"""
        result=subprocess.run([sys.executable,'-I','-O','-B','-c',code,str(Path(__file__).parent),str(self.workspace)],
            capture_output=True,text=True,check=True)
        self.assertEqual(result.stdout,'REFUSED\n')

    def test_control_preparation_preserves_original_payload_tree_and_publication_request(self):
        f=F.live_fixture(self.workspace)
        with patch.object(S.time,'time',return_value=f.now):
            got=S.prepare_control(f.R,f.archive,f.context,f.metadata,f.payload,[],
                source_authors=F.AUTHORS,review_seal_sha256=f.review_seal)
        self.assertEqual({n:got[n] for n in f.payload},f.payload)
        request=json.loads(got['PUBLICATION_REQUEST.json']);tree=json.loads(got['CreateTree.json'])
        self.assertEqual(request['sole_parent'],f.context['workflow_commit'])
        self.assertEqual(request['admission'],'ROOT_MUST_PERSIST_EXACT_ONE_SHOT_EFFECT_GRANT_BEFORE_PROVIDER_WRITE')
        self.assertEqual([r['path'] for r in tree['tree_elements']],
            [f.request['control_path']+'/'+n for n in sorted(f.payload)])
        self.assertFalse(request['automatic_retry']);self.assertEqual(request['original_awards'],[])
        self.assertFalse((self.workspace/'public-control-preparation').exists())

    def test_control_preparation_refuses_unreviewed_changed_payload_overlay_and_expiry(self):
        f=F.live_fixture(self.workspace)
        cases=[({'CONTROL.json':f.payload['CONTROL.json']},[],F.AUTHORS),
            (f.payload,[{'path':'unexpected','mode':'100644','git_blob':'1'*40}],F.AUTHORS),
            (f.payload,[],[F.AUTHORS[0]])]
        with patch.object(S.time,'time',return_value=f.now):
            for payload,leaves,authors in cases:
                with self.subTest(authors=authors),self.assertRaises((ValueError,AssertionError)):
                    S.prepare_control(f.R,f.archive,f.context,f.metadata,payload,leaves,
                        source_authors=authors,review_seal_sha256=f.review_seal)
        with patch.object(S.time,'time',return_value=f.request['expires_utc_epoch']),self.assertRaises(ValueError):
            S.prepare_control(f.R,f.archive,f.context,f.metadata,f.payload,[],
                source_authors=F.AUTHORS,review_seal_sha256=f.review_seal)

    def test_stop_is_only_local_preparation_and_issues_no_review_consumption_or_publication_request(self):
        f=F.live_fixture(self.workspace)
        control=json.loads(f.payload['CONTROL.json']);control.update(decision='STOP',files={})
        payload={'CONTROL.json':F.encode(control)}
        with patch.object(S.time,'time',return_value=f.now):
            got=S.prepare_control(f.R,f.archive,f.context,f.metadata,payload,[],
                source_authors=F.AUTHORS,review_seal_sha256=None)
        self.assertEqual(got['CONTROL.json'],payload['CONTROL.json'])
        self.assertNotIn('PUBLICATION_REQUEST.json',got)
        self.assertNotIn('INDEPENDENT_REVIEW.json',got)

    def test_control_readback_runs_original_validator_and_never_issues_decisions(self):
        f=F.live_fixture(self.workspace)
        selected={'receiver':{'INERT_TEST_ONLY':True},'context':f.context,'request_raw':f.request_raw.decode(),
            'payload':{n:b.decode() for n,b in f.payload.items()},'source_authors':F.AUTHORS,
            'expires_ms':f.request['expires_utc_epoch']*1000}
        with patch.object(S,'load_receiver',return_value=f.R),patch.object(S.time,'time',return_value=f.now):
            got=S.validate_published_control(selected)
            self.assertEqual(got['decision'],'CONSUME')
            self.assertFalse(got['review_issued']);self.assertFalse(got['root_consumption_issued'])
            selected['payload']['ROOT_CONSUMPTION.json']='{}'
            with self.assertRaises(ValueError):S.validate_published_control(selected)


if __name__=='__main__':
    unittest.main(verbosity=2)
