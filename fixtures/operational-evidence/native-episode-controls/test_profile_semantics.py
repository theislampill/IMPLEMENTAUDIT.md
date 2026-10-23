"""Current public-profile seams; constructed records grant no native credit."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from native_test_support import load, SCRATCH

TURN = '11111111-1111-1111-1111-111111111111'
REVISION = 'retained_22222222-2222-2222-2222-222222222222'
PHYSICAL = {'device': 1, 'inode': 2}


class ProfileSemanticsControls(unittest.TestCase):
    def setUp(self):
        self.obs = load('compaction-result-observation.py')
        self.reader = load('bounded_native_reader.py')
        self.child_path = str(SCRATCH / 'profile-fixture-child.jsonl')

    def row(self, ordinal, payload, kind='response_item', metadata=None):
        value = {'type': kind, 'ordinal': ordinal,
            'timestamp': '2026-10-18T12:00:%02dZ' % ordinal, 'payload': payload}
        if metadata is not None: value['metadata'] = metadata
        return value

    def public(self, ordinal=2, phase='commentary', text='bounded fixture', profile=None):
        content = {'type': 'output_text', 'text': text}
        if profile in (None, self.obs.NONPROTECTED_PROFILE): content.update(annotations=[], logprobs=[])
        return self.row(ordinal, {'type': 'message', 'id': 'fixture-message', 'role': 'assistant',
            'phase': phase, 'content': [content]}, metadata={'client_authored': False,
            'retained_source': {'complete': True, 'id': {'message_id': 'fixture-message',
                'role': 'assistant', 'turn_id': TURN}, 'revision': REVISION}})

    def record(self, value):
        n = value['ordinal']
        return {'row': value, 'locator': {'offset': 100*n, 'bytes': 100,
            'sha256': hashlib.sha256(self.obs.canonical(value)).hexdigest(),
            'embedded_ordinal': n, 'physical_line': n+1}}

    def pin(self, value):
        return {'path': self.child_path, 'physical': dict(PHYSICAL), 'role': 'child',
            'locator': dict(value['locator']), 'timestamp': value['row']['timestamp'],
            'message_or_call_id': value['row']['payload'].get('id', value['row']['payload'].get('call_id'))}

    def context(self, profile):
        return {'profile_id': profile, 'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED',
            'child': {'path': self.child_path, 'physical': dict(PHYSICAL), 'history_start_ordinal': 1},
            'actual_child_identity': {'thread_id': 'fixture-child', 'parent_thread_id': 'fixture-parent',
                'agent_path': '/root/fixture-task'}}

    def history(self, profile, public_row):
        obs = self.obs
        records = [self.record(self.row(0, {}, 'session_meta')),
            self.record(self.row(1, {'type': 'task_started', 'turn_id': TURN}, 'event_msg')),
            self.record(public_row)]
        for n, payload in (
            (3, {'type':'custom_tool_call','name':'exec','call_id':'load','input':'bounded-load'}),
            (4, {'type':'custom_tool_call_output','call_id':'load'}),
            (5, {'type':'custom_tool_call','name':'exec','call_id':'exchange','input':'bounded-exchange'}),
            (6, {'type':'custom_tool_call_output','call_id':'exchange'}),
            (7, {'type':'custom_tool_call','name':'exec','call_id':'bind','input':'bounded-bind'})):
            metadata = {'client_authored':False,'fallback_token_limit_override':12000} if n in (4,6) else None
            records.append(self.record(self.row(n, payload, metadata=metadata)))
        by_offset = {r['locator']['offset']:r for r in records}
        prepared = {'authorization':{'load_identity':{'call':self.pin(records[3]),'result':self.pin(records[4])}},
            'obligation':{'observation_id':'a'*64}}
        exchange = {'identity':'e'*64,'records':{'call':self.pin(records[5]),'result':self.pin(records[6])}}
        prefix = {'path':self.child_path,'physical':dict(PHYSICAL),'prefix_bytes':800,
            'prefix_sha256':'f'*64,'physical_records':8,'history_start_ordinal':1,'host_producer_authenticated':False}
        def resolve(ctx, role, locator):
            r = by_offset[locator['offset']]; return r['row'], self.pin(r)
        with patch.object(obs,'hold_records',return_value=(records,prefix)), \
             patch.object(obs,'bind_entry_record',return_value=records[-1]), \
             patch.object(obs,'prior_record_occurrences',return_value=(set(),[])), \
             patch.object(obs,'resolve_record',side_effect=resolve):
            return obs.history_with_priors(self.context(profile),prepared,exchange,{},str(SCRATCH),
                'fixture-parent','fixture-owner',{}, {})

    def test_retained_metadata_reaches_history_without_relaxing_provenance(self):
        obs = self.obs
        for profile in (obs.NONPROTECTED_PROFILE, obs.CURRENT_BOUNDARY_PROFILE):
            with self.subTest(profile=profile):
                self.history(profile, self.public(profile=profile))
                for mutation in ('client', 'incomplete', 'foreign-turn', 'extra'):
                    value = self.public(profile=profile)
                    if mutation == 'client': value['metadata']['client_authored'] = True
                    elif mutation == 'incomplete': value['metadata']['retained_source']['complete'] = False
                    elif mutation == 'foreign-turn': value['metadata']['retained_source']['id']['turn_id'] = TURN.replace('1','3')
                    else: value['metadata']['untrusted'] = True
                    with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.history(profile,value)
        value = self.public()
        self.assertFalse(obs.current_record_metadata(value, self.context('unsupported'), TURN))
        tool = self.row(4,{'type':'custom_tool_call_output','call_id':'load'},
            metadata={'client_authored':False,'fallback_token_limit_override':12000})
        self.assertTrue(obs.current_record_metadata(tool,self.context(obs.NONPROTECTED_PROFILE),TURN))
        tool['metadata']['fallback_token_limit_override'] = 12001
        self.assertFalse(obs.current_record_metadata(tool,self.context(obs.NONPROTECTED_PROFILE),TURN))

    def result(self, phase, profile, directory, tamper_delivery=False):
        obs = self.obs
        scope = [{'id':'fixture-boundary','version':1,'kind':'COMPLETED_RESUMED_BOUNDARY'}]
        binding = {'obligation_digest':'a'*64,'observation_id':'b'*64,
            'child_observation_exchange_identity':'e'*64,'exact_observed_boundary_versions':scope}
        def artifact(name, raw):
            p = directory/name; p.write_bytes(raw)
            return {'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        member = artifact('member.txt',b'bounded source-only result\n')
        result_pin = artifact('result.json',obs.canonical({'schema':'implementaudit.compaction-reconciliation-result.v1',
            **binding,'code_and_skill_pins':{},'status':'SUCCEEDED','currentness':'UNRESOLVED',
            'measured_epoch':'UNRESOLVED','frontier':'fixture-only unknown currentness retained',
            'members':[member],'authority_ceiling':'NONE'}))
        bind_pair = {k:self.pin(self.record(self.row(n,{'type':t,'call_id':'bind'})))
            for k,n,t in (('call',7,'custom_tool_call'),('result',8,'custom_tool_call_output'))}
        use_call = self.record(self.row(9,{'type':'custom_tool_call','name':'exec','call_id':'use',
            'input':'// COMPACTION_OBSERVATION_EXCHANGE='+'e'*64+'\nbounded USE'}))
        use_result = self.record(self.row(10,{'type':'custom_tool_call_output','call_id':'use'}))
        use_pair = {'call':self.pin(use_call),'result':self.pin(use_result)}
        returned = {'schema':'implementaudit.compaction-result-return.v1',**binding,
            'result_bytes_identity':result_pin,'authority_ceiling':'NONE'}
        final_text = '```json\n'+json.dumps(returned)+'\n```'
        final = self.record(self.public(11,phase,final_text,profile))
        envelope = 'Message Type: FINAL_ANSWER\nTask name: /root\nSender: /root/fixture-task\nPayload:\n'
        delivered = self.record(self.row(12,{'type':'agent_message','author':'/root/fixture-task',
            'recipient':'/root','content':[{'type':'input_text','text':envelope+final_text+('!' if tamper_delivery else '')}]}))
        by_offset = {r['locator']['offset']:r for r in (use_call,use_result,final,delivered)}
        def resolve(ctx, role, locator):
            r=by_offset[locator['offset']]; p=self.pin(r); p['role']=role
            return r['row'],p
        exchange={'identity':'e'*64,'evidence':{}}
        prepared={'exchange':exchange,'bound_response':{},'bind_request':{},'obligation_pin':{'sha256':'a'*64},
            'obligation':{'observation_id':'b'*64,'covered_boundary_versions':scope,'code_and_skill_pins':{}},
            'authorization':{'record':{}}}
        evidence={'bound_exchange':{k:v['locator'] for k,v in bind_pair.items()},
            'use':{k:v['locator'] for k,v in use_pair.items()},'child_final':final['locator'],
            'parent_delivery':delivered['locator']}
        with patch.object(obs,'completed_exchange',return_value=exchange), \
             patch.object(obs,'hold_history',return_value={'original_bind':bind_pair}), \
             patch.object(obs,'resolve_record',side_effect=resolve), \
             patch.object(obs,'command_response',return_value=('',use_pair)):
            return obs.actual_result(self.context(profile),prepared,evidence,str(SCRATCH),
                'fixture-parent','fixture-owner',{})

    def test_current_final_phase_reaches_bound_result_and_delivery(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            result=self.result('final_answer',self.obs.NONPROTECTED_PROFILE,Path(directory))
            self.assertEqual((result['status'],result['currentness']),('SUCCEEDED','UNRESOLVED'))
            self.assertEqual(len(result['identity']['members']),1)
            self.reader.project_items({'data':[{'turnId':TURN,'item':{'id':'fixture-message',
                'type':'agentMessage','text':'fixture','phase':'final_answer'}}]}, {'turnId':TURN,'itemIds':['fixture-message']})
            with self.assertRaisesRegex(ValueError,'ACTUAL_FINAL_RETURN_DELIVERY_ASSOCIATION'):
                self.result('final_answer',self.obs.NONPROTECTED_PROFILE,Path(directory),tamper_delivery=True)

    def test_profile_final_phases_remain_distinct(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            result=self.result('final_answer',self.obs.CURRENT_BOUNDARY_PROFILE,Path(directory))
            self.assertEqual(result['status'],'SUCCEEDED')
            for profile, phases in ((self.obs.NONPROTECTED_PROFILE,('final','analysis','commentary')),
                                    (self.obs.CURRENT_BOUNDARY_PROFILE,('final','analysis','commentary'))):
                for phase in phases:
                    with self.subTest(profile=profile,phase=phase), self.assertRaisesRegex(ValueError,'ACTUAL_ASSISTANT_ROLE_OR_PHASE'):
                        self.result(phase,profile,Path(directory))

    def test_qualified_terminal_format_binds_raw_and_native_without_normalization(self):
        owner=load('bounded_source_owner.py')
        raw_row=self.public(11,'final_answer','exact public terminal')
        raw=owner.public_record(raw_row)
        params={'turnId':TURN,'itemIds':['fixture-message']}
        native_result={'data':[{'turnId':TURN,'item':{'id':'fixture-message','type':'agentMessage',
            'text':'exact public terminal','phase':'final_answer'}}]}
        native=self.reader.project_items(native_result,params)[0]
        owner.bind_public(raw,native)
        self.assertEqual(raw['phase'],native['phase'])
        self.assertEqual(raw['body_sha256'],native['body_sha256'])
        wrong=copy.deepcopy(native_result);wrong['data'][0]['item']['text']+=' changed'
        with self.assertRaisesRegex(ValueError,'NATIVE_PUBLIC_ID_BODY_PHASE_TURN_DIFFERS'):
            owner.bind_public(raw,self.reader.project_items(wrong,params)[0])
        for phase in ('final','analysis',None):
            wrong=copy.deepcopy(native_result);wrong['data'][0]['item']['phase']=phase
            with self.subTest(phase=phase), self.assertRaises(ValueError): self.reader.project_items(wrong,params)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            p=Path(directory)/'owned-public.jsonl'
            header=b'{"type":"session_meta","payload":{}}\n'
            wire=self.obs.canonical(raw_row)+b'\n';p.write_bytes(header+wire)
            if os.name != 'nt':
                # This physical native-reader owner is Windows-only. The pure
                # phase/body controls above remain portable; do not fake custody.
                with self.assertRaisesRegex(OSError,'LEXICAL_LOCAL_ABSOLUTE_PATH_REQUIRED'):
                    owner.physical(p)
                return
            source={'physical':owner.physical(p),'cutoff_bytes':p.stat().st_size,'header_prefix':{'bytes':len(header)}}
            locators,_=owner.discover_public(source)
            selected=owner.read_public(p,source['physical'],locators[0],source['cutoff_bytes'])
            owner.bind_public(selected,native)
