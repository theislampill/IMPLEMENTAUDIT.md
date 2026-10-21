"""Constructed composition controls; real owner validators, bounded I/O doubles.

No native acquisition, host qualification, performance or lifecycle credit.
The independent ordinary fixture predates this observation implementation.
"""
import argparse
import contextlib
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT


def load(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class OrdinaryObservationControls(unittest.TestCase):
    def setUp(self):
        fixture = load(ROOT/'fixtures/operational-evidence/ordinary-native-controls.py', 'ordinary_fixture')
        self.value = fixture.available_export()
        base = SOURCE/'source-peers/native-runtime/skills/implementaudit/scripts'
        self.owner = load(base/'compaction-source-owner-codex-app.py', 'ordinary_observation_owner')
        self.obs = load(base/'compaction-result-observation.py', 'ordinary_observation_contract')
        self.helper = load(base/'bounded_source_owner.py', 'ordinary_observation_helper')
        self.temp = tempfile.TemporaryDirectory(prefix='ordinary-observation-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @contextlib.contextmanager
    def boundary(self):
        value = self.value; owner = self.owner; obs = self.obs
        canonical = dict(status='SATISFIED', canonical_route=value['owner']['canonical_route'],
            opening=value['owner']['opening'], scope=value['owner']['scope'], packet=value['result']['packet'],
            child_return=value['result']['return'], governor_decision=value['acceptance']['decision'])
        review = self.root/'review.json'; review.write_bytes(b'constructed review')
        receiving = self.root/'receiving.json'; receiving.write_bytes(b'constructed receiving')
        self.actual_owner = dict(repository=str(self.root),controller=canonical['canonical_route']['controller_id'],
            module_pin=dict(path=str(self.root/'route-transaction.py'),bytes=10,sha256='1'*64))
        selected = dict(episode_owner=copy.deepcopy(self.actual_owner),
            receiving=dict(review_evidence_path=str(review), receiving_evidence_path=str(receiving), graph_owner={}))
        self.selected=selected
        self.canonical = canonical
        self.receipt = copy.deepcopy(value['receiving']['process'])
        self.policy = copy.deepcopy(value['custody']['policy'])
        self.review_pin = copy.deepcopy(value['custody']['review_evidence']); self.review_pin['path'] = str(review)
        self.receiving_pin = copy.deepcopy(value['custody']['receiving_evidence']); self.receiving_pin['path'] = str(receiving)
        view = types.SimpleNamespace(
            ordinary_result_bytes=lambda: obs.canonical(self.canonical),
            ordinary_execution_bytes=lambda: obs.canonical(self.receipt))
        graph = {'fixture': 'independently supplied current graph'}
        artifacts = {key: value['receiving'][key if key != 'work_result' else 'result']
                     for key in ('dispatch','work_result','join')}
        artifacts['graph'] = graph
        document = dict(schema='implementaudit.ordinary-receiving-evidence.v1',
            records=dict(join=value['receiving']['record']['locator']),
            **{key: dict(path=key) for key in artifacts})
        context = {role: value['custody']['sources'][role] for role in ('parent','child')}
        context.update(parent_identity=dict(thread_id=value['result']['actual_child_identity']['parent_thread_id']),
                       actual_child_identity=value['result']['actual_child_identity'])
        self.public_check = Mock()
        helpers = types.SimpleNamespace(_recheck_ordinary_native_v1=self.public_check,
                                        _bind_episode_owner_v1=self.helper._bind_episode_owner_v1)
        runtime = (selected, None, None, helpers, None)
        def documents(contract, selection, path):
            return (document, copy.deepcopy(self.receiving_pin)) if path == str(receiving) else ({}, copy.deepcopy(self.review_pin))
        def artifact(contract, selection, pin):
            if pin['path'] in artifacts: return obs.canonical(artifacts[pin['path']]), copy.deepcopy(self.artifact_physical)
            return b'constructed member bytes', copy.deepcopy(self.member_physical)
        self.member_physical = copy.deepcopy(value['result']['members'][0]['physical'])
        self.artifact_physical = dict(device=1,inode=4)
        def reconcile(prior, current, dispatch, results, consumer):
            self.assertEqual(prior, graph); self.assertEqual(current, graph)
            self.assertEqual(dispatch, value['receiving']['dispatch'])
            self.assertEqual(results, [value['receiving']['result']])
            self.assertEqual(consumer, self.policy['consumer'])
            return copy.deepcopy(value['receiving']['join'])
        graph_owner = types.SimpleNamespace(reconcile_native_results_v1=reconcile,
            read_native_run_v1=Mock(side_effect=AssertionError('duplicate graph acquisition')))
        self.provider = []
        @contextlib.contextmanager
        def provider(*args):
            self.provider.append('entry'); yield; self.provider.append('exit')
        replacements = dict(
            ORDINARY_SELECTION_PIN={'fixture': 'private selection'},
            _ordinary_selection_v1=lambda: selected,
            _ordinary_modules_v1=lambda s: (runtime, obs, value['owner']['code_pins']),
            ordinary_policy_v1=lambda: copy.deepcopy(self.policy),
            _ordinary_canonical_v1=Mock(side_effect=AssertionError('duplicate route acquisition')),
            _ordinary_h0_current_v1=Mock(), _ordinary_provider_guard_v1=provider,
            _ordinary_review_v1=lambda *a, **k: (copy.deepcopy(value['owner']),copy.deepcopy(value['result']),
                copy.deepcopy(value['acceptance']),copy.deepcopy(value['occurrences']),context,
                copy.deepcopy(value['custody']['public_records'][:3]),copy.deepcopy(self.review_pin)),
            _ordinary_document_v1=documents, _ordinary_artifact_v1=artifact,
            _np_module=lambda *a: graph_owner,
            _ordinary_public_v1=lambda *a: copy.deepcopy(value['custody']['public_records'][3]))
        with contextlib.ExitStack() as stack:
            for name, replacement in replacements.items(): stack.enter_context(patch.object(owner,name,replacement))
            yield view, obs.canonical(graph), copy.deepcopy(self.actual_owner)

    def test_available_projection_retains_real_semantic_validation_and_provider_lifetime(self):
        with self.boundary() as native:
            with self.owner._ordinary_episode_observation_v1(native) as raw:
                actual = json.loads(raw)
                self.assertEqual(actual['status'],'AVAILABLE')
                for key in ('owner','result','acceptance','receiving','lifecycle','occurrences'):
                    self.assertEqual(actual[key],self.value[key])
                self.assertEqual(self.provider,['entry'])
                self.public_check.assert_not_called()
                self.assertEqual(self.obs.validate_ordinary_episode_export_v1(actual),actual)
            self.assertEqual(self.provider,['entry','exit'])
            self.public_check.assert_called_once()

    def test_late_route_receipt_policy_document_member_and_native_changes_refuse(self):
        for field in ('route','receipt','policy','review','receiving','member','artifact','native'):
            with self.subTest(field=field),self.boundary() as native:
                with self.assertRaises((ValueError,KeyError)):
                    with self.owner._ordinary_episode_observation_v1(native):
                        if field=='route': self.canonical['status']='RETURNED'
                        elif field=='receipt': self.receipt['oid']='9'*40
                        elif field=='policy': self.policy['artifact_root']='changed'
                        elif field=='review': self.review_pin['sha256']='9'*64
                        elif field=='receiving': self.receiving_pin['sha256']='9'*64
                        elif field=='member': self.member_physical['inode']=99
                        elif field=='artifact': self.artifact_physical['inode']=99
                        else: self.public_check.side_effect=ValueError('native public body changed')

    def test_public_acquisition_has_no_fact_or_view_operand(self):
        with self.assertRaises(TypeError): self.owner.acquire_selected_ordinary_episode_v1({'trusted': True})

    def test_selected_owner_controller_repository_and_source_must_match_actual_observation(self):
        for field in ('controller','repository','path','bytes','sha256','floating_bytes','boolean_bytes'):
            with self.subTest(field=field),self.boundary() as native:
                selected=self.selected['episode_owner']
                if field=='controller':selected[field]='foreign-controller'
                elif field=='repository':selected[field]=str(self.root/'foreign-repository')
                elif field=='path':selected['module_pin'][field]=str(self.root/'foreign-route.py')
                elif field=='bytes':selected['module_pin'][field]+=1
                elif field=='floating_bytes':selected['module_pin']['bytes']=float(selected['module_pin']['bytes'])
                elif field=='boolean_bytes':selected['module_pin']['bytes']=True
                else:selected['module_pin'][field]='0'*64
                with self.assertRaisesRegex(ValueError,'ORDINARY_SELECTED_EPISODE_OWNER_DIFFERS'):
                    with self.owner._ordinary_episode_observation_v1(native):pass
                self.assertEqual(self.provider,[],'selected owner must be checked before native-provider acquisition')

    @contextlib.contextmanager
    def native_boundary(self):
        value=self.value; helper=self.helper; obs=self.obs
        child=value['result']['actual_child_identity']; parent_id=child['parent_thread_id']; child_id=child['thread_id']
        selected=dict(root_thread_id=parent_id,root_agent_path='/root',session_root=str(self.root),
                      cwd=str(self.root),cli_version='constructed')
        threads={}; headers={}
        for role,ident in (('parent',parent_id),('child',child_id)):
            path=self.root/('rollout-'+ident+'.jsonl');path.write_bytes(b'constructed physical source')
            if role=='parent':selected['root_source']=str(path)
            meta=dict(id=ident,session_id=parent_id,parent_thread_id=None if role=='parent' else parent_id,
                agent_path='/root' if role=='parent' else child['agent_path'],cli_version='constructed',cwd=str(self.root),
                thread_source='subagent' if role=='child' else 'cli')
            headers[ident]=dict(physical=dict(path=str(path),device=1,inode=1 if role=='parent' else 2),
                header_prefix=dict(bytes=1,sha256='1'*64),metadata=meta,cutoff_bytes=100)
            threads[ident]=dict(id=ident,path=str(path),sessionId=ident,parentThreadId=meta['parent_thread_id'],
                source_kind='subAgent' if role=='child' else 'cli',threadSource=meta['thread_source'],
                cliVersion='constructed',cwd=str(self.root),ephemeral=False,historyMode='paginated')
        subject=dict(parent_identity=dict(thread_id=parent_id),actual_child_identity=child,
                     sources={role:copy.deepcopy(headers[ident]) for role,ident in (('parent',parent_id),('child',child_id))})
        context=dict(profile_id=obs.NONPROTECTED_PROFILE,parent_identity=subject['parent_identity'],
                     actual_child_identity=child,_native_subject=subject)
        public=value['custody']['public_records']; rows={}
        for item in public:
            rows[item['pin']['message_or_call_id']]=dict(type='response_item',payload=dict(type='message',id=item['message_id'],
                role='assistant',phase=item['phase'],content=[dict(type='output_text',text=item['body'],annotations=[],logprobs=[])]),
                metadata=dict(client_authored=False,retained_source=dict(complete=True,revision=item['revision'],
                id=dict(message_id=item['message_id'],role='assistant',turn_id=item['turn_id']))))
        pins=[x['pin'] for x in public]+[value['occurrences']['spawn'][k] for k in ('call','output')]+[value['occurrences']['activation']]
        self.raw_drift=False
        def resolve(contract,ctx,role,locator):
            pin=next(x for x in pins if x['role']==role and x['locator']==locator)
            row=copy.deepcopy(rows.get(pin['message_or_call_id'],{}))
            if self.raw_drift and row:row['metadata']['retained_source']['complete']=False
            return row,copy.deepcopy(pin)
        responses=[dict(threads=[copy.deepcopy(threads[child_id])]),dict(thread=copy.deepcopy(threads[parent_id])),
                   dict(thread=copy.deepcopy(threads[child_id]))]
        responses += [dict(items=[dict(id=x['message_id'],turn_id=x['turn_id'],phase=x['phase'],
                        body_bytes=len(x['body'].encode()),body_sha256=x['body_sha256'])]) for x in public]
        self.responses=responses;self.headers=headers
        api=Mock(side_effect=lambda *a:dict(responses=copy.deepcopy(self.responses)))
        with patch.object(helper,'header',side_effect=lambda thread:copy.deepcopy(headers[thread['id']])):
            yield (selected,None,None,helper,None),context,public,value['occurrences'],api,resolve

    def test_native_exit_batches_all_seven_exact_reads_and_allows_append(self):
        with self.native_boundary() as args:
            self.helper._recheck_ordinary_native_v1(args[0],self.obs,*args[1:])
            args[4].assert_called_once()
            methods=args[4].call_args.args[1]
            self.assertEqual([row[0] for row in methods],['thread/list','thread/read','thread/read']+['thread/items/read']*4)
            for header in self.headers.values():header['cutoff_bytes']+=100
            self.helper._recheck_ordinary_native_v1(args[0],self.obs,*args[1:])

    def test_native_exit_refuses_changed_catalog_relation_body_population_and_physical_source(self):
        for field in ('catalog_duplicate','parent','body','turn','phase','population','physical','header','raw'):
            with self.subTest(field=field),self.native_boundary() as args:
                if field=='catalog_duplicate':self.responses[0]['threads']*=2
                elif field=='parent':self.responses[2]['thread']['parentThreadId']='foreign'
                elif field in ('body','turn','phase'):
                    self.responses[3]['items'][0][dict(body='body_sha256',turn='turn_id',phase='phase')[field]]='changed'
                elif field=='population':self.responses.pop()
                elif field=='physical':next(iter(self.headers.values()))['physical']['inode']=99
                elif field=='header':next(iter(self.headers.values()))['header_prefix']['sha256']='9'*64
                else:self.raw_drift=True
                with self.assertRaises(ValueError):self.helper._recheck_ordinary_native_v1(args[0],self.obs,*args[1:])

    def test_raw_record_changed_during_native_api_read_refuses(self):
        with self.native_boundary() as args:
            def changed(*call):self.raw_drift=True;return dict(responses=copy.deepcopy(self.responses))
            args[4].side_effect=changed
            with self.assertRaises(ValueError):self.helper._recheck_ordinary_native_v1(args[0],self.obs,*args[1:])

    def test_public_batch_preserves_three_exact_records_in_one_native_call(self):
        with self.native_boundary() as args:
            runtime,context,public,_,api,resolve=args
            api.side_effect=lambda *a:dict(responses=copy.deepcopy(self.responses[3:6]))
            specs=[(p['pin']['role'],p['pin']['locator'],p['phase']) for p in public[:3]]
            with patch.object(self.owner,'_np_call',api),patch.object(self.owner,'_ordinary_resolve_v1',resolve):
                result=self.owner._ordinary_publics_v1(runtime,self.obs,context,specs)
            self.assertEqual(result,public[:3]);api.assert_called_once()
            self.assertEqual([m[0] for m in api.call_args.args[1]],['thread/items/read']*3)

    def test_public_batch_refuses_partial_wrong_or_changed_native_records(self):
        for field in ('partial','body','order','raw'):
            with self.subTest(field=field),self.native_boundary() as args:
                runtime,context,public,_,api,resolve=args
                responses=copy.deepcopy(self.responses[3:6])
                if field=='partial':responses.pop()
                elif field=='body':responses[1]['items'][0]['body_sha256']='0'*64
                elif field=='order':responses.reverse()
                def response(*a):
                    if field=='raw':self.raw_drift=True
                    return dict(responses=responses)
                api.side_effect=response
                specs=[(p['pin']['role'],p['pin']['locator'],p['phase']) for p in public[:3]]
                with patch.object(self.owner,'_np_call',api),patch.object(self.owner,'_ordinary_resolve_v1',resolve):
                    with self.assertRaises(ValueError):self.owner._ordinary_publics_v1(runtime,self.obs,context,specs)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--repo-root',type=Path,default=ROOT)
    parser.add_argument('--source-root',type=Path)
    args,rest=parser.parse_known_args(); ROOT=args.repo_root.resolve(strict=True)
    SOURCE=(args.source_root or ROOT).resolve(strict=True)
    unittest.main(argv=[__file__,*rest])
