"""Closed owner-domain and physical-order controls; fixture evidence only."""
import copy
import unittest

from native_test_support import load, functions
import test_episode_export as export_fixture


class ExportSemanticsControls(unittest.TestCase):
    def setUp(self):
        self.obs = load('compaction-result-observation.py')
        self.fixture = export_fixture.FrozenExportTests()

    def validate(self, value):
        return self.obs.validate_frozen_episode_export_v1(self.fixture.reseal(value))

    def test_unresolved_signal_is_preserved_without_consumption(self):
        env = functions('compaction-audit-pending.py',
            {'decision','outstanding','available_scope','scope_owners'},
            {'require':self.obs.require,'CEILING':{}})
        value = self.fixture.available()
        signal = {'id':'unresolved-signal-fixture','kind':'UNRESOLVED_SIGNAL','version':1}
        observation = {**signal,'consumed_version':0,'assignment_children':[]}
        value['pending']['observations'].append(observation)
        value['pending']['pending_scope'] = [signal]
        decision = env['decision']({'observations':{signal['id']:observation},'assignments':{},
            'source_problem':None,'signals':1})
        self.assertTrue(decision['audit_state_required'])
        self.assertEqual(self.validate(value)['pending']['pending_scope'],decision['pending'])
        changed = copy.deepcopy(value)
        changed['pending']['observations'][-1]['kind'] = 'CALLER_INVENTED_KIND'
        changed['pending']['pending_scope'][-1]['kind'] = 'CALLER_INVENTED_KIND'
        with self.assertRaises(ValueError): self.validate(changed)

    def test_covered_and_assigned_scope_bind_pending_kind_and_version(self):
        value = self.fixture.available()
        self.validate(value)
        for mutation in ('covered-kind','assignment-kind','assignment-version','assignment-absent'):
            changed=copy.deepcopy(value)
            if mutation=='covered-kind': changed['pending']['observations'][0]['kind']='AMBIGUOUS_MARKER_GROUP'
            else:
                changed['pending']['assignment_scope']=copy.deepcopy(changed['pending']['assignment_scope'])
                extra={'id':'later','kind':'UNRESOLVED_RESUME_OBSERVATION','version':1}
                changed['pending']['observations'].append({**extra,'consumed_version':0,'assignment_children':[]})
                changed['pending']['pending_scope']=[copy.deepcopy(extra)]
                changed['pending']['assignment_scope'].append(copy.deepcopy(extra))
                if mutation=='assignment-kind': changed['pending']['assignment_scope'][-1]['kind']='AMBIGUOUS_MARKER_GROUP'
                elif mutation=='assignment-version': changed['pending']['assignment_scope'][-1]['version']=2
                else: changed['pending']['assignment_scope'][-1]['id']='absent'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.validate(changed)
        newer=copy.deepcopy(value)
        newer['pending']['observations'][0]['version']=2
        newer['pending']['pending_scope']=[{k:newer['pending']['observations'][0][k] for k in ('id','kind','version')}]
        self.assertEqual(self.validate(newer)['pending']['observations'][0]['consumed_version'],1)

    def test_occurrence_ranges_and_order_match_original_source_guards(self):
        value=self.fixture.available()
        self.validate(value)
        touching=copy.deepcopy(value)
        touching['occurrences']['occurrences'][0]['records']['call']['locator']['bytes']=5
        self.validate(touching)  # Exact end-before-next is inclusive.
        for mutation in ('pair-overlap','cross-pair-overlap','reversed-time','invalid-time','reversed-ordinal'):
            changed=copy.deepcopy(value)
            rows=changed['occurrences']['occurrences']
            if mutation=='pair-overlap': rows[0]['records']['call']['locator']['bytes']=6
            elif mutation=='cross-pair-overlap': rows[0]['records']['result']['locator']['bytes']=6
            elif mutation=='reversed-time': rows[0]['records']['result']['timestamp']='2026-10-18T00:00:01Z'
            elif mutation=='invalid-time': rows[0]['records']['call']['timestamp']='not-a-source-timestamp'
            else:
                loc=rows[0]['records']['result']['locator'];loc['embedded_ordinal']=9;loc['physical_line']=10
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.validate(changed)
