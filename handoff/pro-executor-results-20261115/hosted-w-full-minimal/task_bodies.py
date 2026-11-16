#!/usr/bin/env python3
"""Exact existing new-task author; source identity rebound to the selected runtime.

Origins and byte hashes are in SOURCE_ORIGINS.json. This module issues no grant.
"""
import re

SOURCE_HEAD = '6b353b48b2fc8a6de0c6223f48d341c484c98191'

def require(ok,reason):
    if not ok: raise RuntimeError(reason)

def task_bodies(meta,authored,owner_source_text):
    """Author only actual new-task facts; do not import fixture receipt/history values."""
    def group(owner,value): return {'owner':owner,'value':value}
    def record(identifier,description,status='ACTIVE'):
        return {'record_id':identifier,'status':status,'description':description,
                'scope':'this newly created Windows qualification subject only','evidence_refs':['authorization']}
    instruction={'record_id':'external-new-task-authorization','issuer':'external owner approval reference',
        'subject':'Perform one fresh Windows resume receiving campaign using the pinned public source',
        'scope':'this disposable subject only; the adapter does not authenticate entitlement',
        'applicability':'APPLIES','status':'ACTIVE','evidence_refs':['authorization'],
        'issued_epoch':'G0001','expires_at':None,'supersedes':[]}
    frontier={'DONE':['actual-initialization'],'ACTIVE':['new-windows-campaign'],
              'READY':[],'BLOCKED':['independent-original-receiving']}
    state={
        'identity':group('claim-run.sh',{'controller_id':meta['controller'],'claim_id':meta['claim_id'],
            'run_root_identity':meta['run_relative'],'audit_object':'Fresh Windows whole-owner resume receiving task',
            'candidate':meta['head'],'tree':meta['tree'],'package':'Exact copied runtime at '+SOURCE_HEAD,
            'pull_request':None,'release':None}),
        'continuation':group('STATE.md',{'phase':'1','status':'open','next_action':meta['next_action'],
            'route':'ordinary','last_check':'Actual pending initialization activated; no acceptance awarded'}),
        'instructions':group('STATE.md',[dict(instruction,record_id='new-task-scope-instruction')]),
        'authorisations':group('STATE.md',[instruction]),
        'terminal':group('STATE.md',{'one_shots':[],'markers':[],'handoffs':[],'external_effects':[]}),
        'andons':group('STATE.md',[]),'original_reds':group('STATE.md',[]),
        'pending_boundaries':group('R0033/continuity',[]),
        'non_verdicts':group('STATE.md',[record('no-acceptance','New task measurements do not award original acceptance')]),
        'evidence_ceilings':group('STATE.md',[record('no-native-history','No historic H0, model session, C02 adjudication or original controller custody is asserted')]),
        'steers':group('STATE.md',[record('one-fresh-attempt','No old effect replay, automatic retry, cleanup or compensation')]),
        'rollback':group('STATE.md',{'status':'AVAILABLE','target':None,
            'conditions':['Stop and retain this newly owned subject after any uncertain effect; no automatic compensation'],
            'evidence_refs':['authorization']}),
        'runtime_artifacts':group('STATE.md',['receipt','authorization','initialization','public_owner_source','work_graph'])}
    roadmap={
        'frontier':group('WORK_GRAPH.json',frontier),
        'obligations':group('ROADMAP.md',[record('receive-fresh-operation','Retain actual whole-Job measurement and independent receiving evidence','OPEN')]),
        'deferrals':group('ROADMAP.md',[]),
        'dependencies':group('ROADMAP.md',[{'record_id':'receiving-dependency','source':'independent-original-receiving',
            'target':'new-windows-campaign','status':'BLOCKED','evidence_refs':['authorization']}]),
        'compensations':group('ROADMAP.md',[]),
        'planning':group('ROADMAP.md',{'goal':'Measure one actual fresh Windows owner resume within the maintained whole-Job contract',
            'action_selection':{'selected':['truthful new subject','actual first rotation','fresh manual invalidation','one maintained prepare/execute'],
                'omitted':['model session','historic H0','C02 adjudication','protected historical operations'],
                'rationale':'Only a fresh isolated Windows qualification episode is selected'},
            'scope_boundaries':['New disposable subject only','No retry','No original acceptance grant'],
            'baseline_ref':meta['head']})}
    bodies={}
    for role,payload in [('STATE',state),('ROADMAP',roadmap)]:
        lines=authored[role].decode().splitlines()
        require([line for line in lines if re.search(r'current\s+epoch\s*:',line,re.I)]==(['Current epoch: G0001'] if role=='STATE' else []),'ordinary author epoch shape differs')
        payload['native_guards']=group(role+'.md',{'schema_version':'implementaudit.native-guard-profile.v1',
            'lines':[line for line in lines if line!='Current epoch: G0001']})
        bodies[role]={'schema_version':'implementaudit.canonical-pair.v2','role':role,
            'pair_id':'actual-windows-'+meta['controller'],'payload':payload,'transition':None,'history':[],
            'archive_pointers':[],'artifact_refs':[],
            'continuity':{'projection_generation_id':'G0001','continuity_epoch':'G0001','invalidation_oid':None,
                'predecessor_receipt_ref_oid':None,'expected_receipt_ref':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001',
                'expected_receipt_schema':'implementaudit.continuity-receipt.v2','boundary':'new-session','reconciled':True}}
    bodies['STATE']['artifact_refs']=[{'artifact_id':'receipt','owner':'claim-run.sh','role':'CONTINUITY_RECEIPT',
        'locator':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001','object_format':'sha1'}]
    for name in ('authorization','initialization','public_owner_source'):
        bodies['STATE']['artifact_refs'].append({'artifact_id':name,'owner':'STATE.md','role':'EVIDENCE',
            'locator':'evidence/'+name+'.txt','object_format':'sha1'})
    bodies['ROADMAP']['artifact_refs']=[{'artifact_id':'work_graph','owner':'WORK_GRAPH.json','role':'WORK_GRAPH',
        'locator':'WORK_GRAPH.json','object_format':'sha1'}]
    bodies['STATE']['history']=[{'record_id':'source-captured-in-this-new-task','record_kind':'artifact.historical',
        'owner':'STATE.md','status':'PRESERVED','payload':{'text':owner_source_text,'evidence_refs':['public_owner_source'],
        'original_scope':'Exact reviewed source of claim-run-rotation.py captured earlier during this new task preparation',
        'current_applicability':'UNCHANGED','historical_refusal':None}}]
    return bodies,frontier
