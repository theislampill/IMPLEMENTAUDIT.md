#!/usr/bin/env python3
"""Prospective complete A2 qualification against the unchanged selected product.

Importing this file imports no product/fixture and performs no original action.
Inputs are declared qualification fixtures. No synthetic issuer or receipt is
represented as an authentic grant, native event, OR observation or C02 event.
"""
from __future__ import annotations
import copy
import hashlib
import json

DISPOSITIONS=('ACTIVE','SATISFIED','SUPERSEDED','REVOKED','EXPIRED','AMBIGUOUS')
AUTHORITY='NO_CURRENTNESS_AUTHORITY'
FIXTURE_SHA256='d8d07242e5052693d9da07ae1b9f88cc0cf8fbb46e19b71099e10bfd640ea266'
HISTORY_LINE='Exact retained historical narrative.\n'
PINNED={'STATE':{'bytes':197555,'sha256':'9ab0c8d2d19b363a042c10d8fa31c51d8b2aeb4b0e98d35c040bcea2986c7be5'},
        'ROADMAP':{'bytes':3001,'sha256':'7d46caa78372fba5bb9e04f03c4e3fefae43ae8885a942c8b8c6304c9a3fef35'}}
LIMITS={'max_state_bytes':65536,'max_roadmap_bytes':65536}
PARTS=('PRESERVED_PAYLOAD','MONOTONIC_TRANSITION','DERIVED_BINDINGS','ARCHIVED_ONLY_HISTORY')
POINTER_FIELDS=('schema','controller','claim_id','run_root_identity','projection_generation_id','continuity_epoch',
    'invalidation_oid','predecessor_receipt_ref_oid','expected_receipt_ref_schema','projection_schema',
    'state_sha256','roadmap_sha256','protected_manifest_sha256','archive_manifest_sha256','exact_next_action')
STATE={'schema':'dg18.original-a2-prospective-observations.v1','authority':'NONE','award':None,
    'original_criterion':2,'original_denominator':14,'status':'NOT_EXECUTED','cases':[],
    'fixture_authority':'All additional dispositions, receipt bytes and transition proposals are explicitly qualification data; no issuer/native/OR/C02/N1 authority is supplied.'}
NATIVE_STATE={'schema':'dg18.original-a2-native-pointer-observations.v1','authority':'NONE','award':None,
    'status':'NOT_EXECUTED','cases':[],'scope':'Actual immutable Git archive/generation reader in disposable original fixture roots. Native currentness/controller authority is not manufactured.'}


def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def pin(raw):return {'bytes':len(raw),'sha256':sha(raw)}
def escaped(s):return s.replace('~','~0').replace('/','~1')


def leaves(value,path=()):
    if type(value) is dict and value:
        for key in sorted(value):yield from leaves(value[key],path+(key,))
    elif type(value) is list and value:
        for i,child in enumerate(value):yield from leaves(child,path+(i,))
    else:yield path,value


def pointer(path):return ''.join('/'+escaped(str(p)) for p in path)


def changed(value,path,omit=False):
    result=copy.deepcopy(value);target=result
    for part in path[:-1]:target=target[part]
    key=path[-1]
    if omit:del target[key]
    else:
        old=target[key]
        target[key]=(not old if type(old) is bool else old+1 if type(old) is int
                     else ['A2_SEMANTIC_CHANGE'] if type(old) is list
                     else {'A2_SEMANTIC_CHANGE':True} if type(old) is dict
                     else 'A2_SEMANTIC_CHANGE' if old is None else old+'::A2_SEMANTIC_CHANGE')
    return result


def source_bodies(fixture):
    bodies=copy.deepcopy(fixture['bodies'])
    bodies['STATE']['history'][0]['payload']['text']=HISTORY_LINE*5000
    return bodies


def six_disposition_extension(bodies):
    result=copy.deepcopy(bodies)
    for group in ('instructions','authorisations'):
        rows=result['STATE']['payload'][group]['value'];prototype=copy.deepcopy(rows[0])
        additions=[]
        for status in DISPOSITIONS:
            row=copy.deepcopy(prototype)
            row.update(record_id='a2-fixture-'+group+'-'+status.lower(),status=status,
                issuer='DECLARED_A2_QUALIFICATION_FIXTURE_ISSUER',
                subject='Preserve the declared '+status+' '+group+' disposition',
                scope='R0039/#215 A2 deterministic qualification only; no external authority',
                applicability='UNRESOLVED' if status=='AMBIGUOUS' else 'DOES_NOT_APPLY' if status in {'EXPIRED','REVOKED'} else 'APPLIES',
                expires_at='2000-01-01T00:00:00Z' if status=='EXPIRED' else None,
                supersedes=['a2-fixture-'+group+'-superseded'] if status=='ACTIVE' else [])
            additions.append(row)
        rows.extend(additions)
    return result


def render(bodies):
    result={};identity=bodies['STATE']['payload']['identity']['value']
    action=bodies['STATE']['payload']['continuation']['value']['next_action']
    for role in ('STATE','ROADMAP'):
        body=bodies[role];current=body['transition'] or body['continuity']
        frame=('# IMPLEMENTAUDIT '+role.title()+'\n\nCurrent epoch: '+current['continuity_epoch']+
            '\nCanonical projection generation: '+current['projection_generation_id']+
            '\n\n| Field | Value |\n|---|---|\n| Next action | '+action+' |\n\n'+
            '## Context epochs and instruction applicability\n\n'+
            '| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n'+
            '|---|---|---|---|---|---|\n| '+current['continuity_epoch']+' | '+current['boundary']+
            ' | not measured | `'+identity['candidate']+'` / `'+identity['tree']+'` | yes | exact source facts |\n\n```json\n')
        result[role]=frame.encode()+canonical(body)+b'\n```\n'
    return result


def owners(bodies,raw,artifacts):
    rows=[]
    for role in ('STATE','ROADMAP'):
        for name,group in bodies[role]['payload'].items():
            for path,value in leaves(group,('payload',name)):
                p=pointer(path)
                rows.append({'field':'/'+role+p,'owner':group['owner'],'source_kind':'PAIR','source_id':role,
                    'source_pointer':p,'source_sha256':sha(raw[role]),'value_sha256':sha(canonical(value))})
        for ref in bodies[role]['artifact_refs']:
            value=sha(artifacts[ref['artifact_id']])
            rows.append({'field':'/artifacts/'+ref['artifact_id'],'owner':ref['owner'],'source_kind':'ARTIFACT',
                'source_id':ref['artifact_id'],'source_pointer':'','source_sha256':value,'value_sha256':value})
    return sorted(rows,key=lambda r:r['field'])


def pair(bodies,fixture,frame_template=None):
    """Exact v2 qualification bytes; a template permits malformed body-only inputs.

    Invalid continuity inputs retain a valid original frame/fixture receipt whose
    hashes are refreshed. Product continuity vocabulary validation must refuse
    them; input preparation is not allowed to fail first in a fixture helper.
    """
    template=frame_template or bodies
    raw=render(template)
    if frame_template is not None:
        raw={r:raw[r].split(b'```json\n',1)[0]+b'```json\n'+canonical(bodies[r])+b'\n```\n' for r in raw}
    artifacts={k:v.encode() for k,v in fixture['artifact_texts'].items()}
    identity=template['STATE']['payload']['identity']['value'];current=template['STATE']['continuity']
    action=template['STATE']['payload']['continuation']['value']['next_action']
    fields=['implementaudit.continuity-receipt.v2',identity['controller_id'],'e'*40,identity['claim_id'],
        identity['candidate'],identity['tree'],sha(raw['STATE']),sha(raw['ROADMAP']),current['invalidation_oid'] or 'none',
        current['boundary'],current['continuity_epoch'],action]
    artifacts['receipt']=('\t'.join(fields)+'\n').encode()
    return raw['STATE'],raw['ROADMAP'],owners(bodies,raw,artifacts),artifacts


def archive_population(bodies,raw):
    whole=[];history=[]
    for role in ('STATE','ROADMAP'):
        common={'source_role':role,'source_sha256':sha(raw[role]),'source_bytes':len(raw[role]),'blob_oid':blob(raw[role])}
        whole.append({**common,'role':role+'_PREIMAGE','source_pointer':'','record_id':role+'.md',
            'record_sha256':common['source_sha256'],'owner':role+'.md'})
        for i,row in enumerate(bodies[role]['history']):
            history.append({**common,'role':'HISTORY_RECORD','source_pointer':'/history/'+str(i),
                'record_id':row['record_id'],'record_sha256':sha(canonical(row)),'owner':row['owner']})
    return whole+history


def transition(bodies,pair_value,recovery=False):
    current=bodies['STATE']['continuity'];controller=bodies['STATE']['payload']['identity']['value']['controller_id']
    epoch='G0003' if recovery else 'G0002'
    return {'schema_version':'implementaudit.canonical-state-transition.v2','boundary':'canonical-state-rotation',
        'reconciled':True,'transition_kind':'recovery' if recovery else 'rotation',
        'predecessor_generation_id':'G0001','projection_generation_id':epoch,'predecessor_epoch':'G0001','continuity_epoch':epoch,
        'failed_transition_receipt_ref_oid':None,'failed_transition_epoch':'G0002' if recovery else None,
        'failed_projection_generation_id':'G0002' if recovery else None,'invalidation_oid':'5'*40,
        'predecessor_receipt_ref_oid':current['expected_receipt_ref']+'@'+blob(pair_value[3]['receipt']),
        'expected_receipt_ref':'refs/implementaudit/continuity-receipts/'+controller+'/'+epoch,
        'expected_receipt_schema':'implementaudit.continuity-receipt.v3'}


def reference(bodies,pair_value,successor):
    """Complete independent input-derived population, not a product PASS bit."""
    raw=dict(zip(('STATE','ROADMAP'),pair_value[:2]));current=bodies['STATE']['continuity']
    identity=bodies['STATE']['payload']['identity']['value'];payload={r:copy.deepcopy(bodies[r]['payload']) for r in raw}
    population=archive_population(bodies,raw)
    pointers=[{**copy.deepcopy(row),'schema_version':'implementaudit.typed-archive-pointer.v2',
        'archive_ref':'refs/implementaudit/state-archives/'+identity['controller_id']+'/G0002','preparation_generation_id':'G0002',
        'archive_manifest_oid':'7'*40,'archive_manifest_sha256':'6'*64,'authority':'ARCHIVED_ONLY_HISTORY'} for row in population]
    generated=copy.deepcopy(bodies)
    for body in generated.values():
        body['history']=[];body['archive_pointers']=copy.deepcopy(pointers);body['continuity']=copy.deepcopy(current)
        body['transition']=copy.deepcopy(successor)
        for declaration in body['artifact_refs']:
            if declaration['role']=='CONTINUITY_RECEIPT':declaration['locator']=(successor or current)['expected_receipt_ref']
    output=render(generated)
    refs=[copy.deepcopy(ref) for r in ('STATE','ROADMAP') for ref in generated[r]['artifact_refs']]
    refs.sort(key=lambda row:row['artifact_id'])
    # The original five-field artifact declaration is retained exactly; the
    # source role is not an additional declaration field.
    manifest={'PRESERVED_PAYLOAD':{'payload':payload,'owner_map':copy.deepcopy(pair_value[2]),'source_hashes':{r:sha(raw[r]) for r in raw}},
        'MONOTONIC_TRANSITION':copy.deepcopy(successor),
        'DERIVED_BINDINGS':{'authority_ceiling':AUTHORITY,'predecessor_continuity':copy.deepcopy(current),
            'current_receipt_ref_oid':current['expected_receipt_ref']+'@'+blob(pair_value[3]['receipt']),
            'artifact_refs':refs,'state_sha256':sha(output['STATE']),'roadmap_sha256':sha(output['ROADMAP'])},
        'ARCHIVED_ONLY_HISTORY':copy.deepcopy(pointers)}
    return {'payload':payload,'owner_map':copy.deepcopy(pair_value[2]),'archive_population':population,
        'pointers':pointers,'manifest':manifest,'output':output,'refs':refs,'source_hashes':{r:sha(raw[r]) for r in raw}}


def unknown_mutations(bodies):
    """Declared finite-state negatives; every changed body reaches actual parse."""
    cases=[]
    def add(label,alter,reason):
        b=copy.deepcopy(bodies);alter(b);cases.append((label,b,reason))
    def setpath(path,value):
        def alter(b):
            t=b
            for p in path[:-1]:t=t[p]
            t[path[-1]]=value
        return alter
    for state in ('DONE','ACTIVE','READY','BLOCKED'):
        def frontier(b,state=state):
            value=b['ROADMAP']['payload']['frontier']['value'];value['UNKNOWN_FRONTIER']=value.pop(state)
        add('frontier/'+state,frontier,'frontier has missing or unknown fields')
    for group in ('instructions','authorisations'):
        rows=bodies['STATE']['payload'][group]['value']
        for index,row in enumerate(rows):
            for field,reason in (('status','instruction status'),('applicability','applicability')):
                add(group+'/'+row['record_id']+'/'+field,
                    setpath(('STATE','payload',group,'value',index,field),'UNKNOWN_A2_STATE'),reason)
    current=bodies['STATE']['continuity']
    reasons={'projection_generation_id':'epoch/generation','continuity_epoch':'epoch/generation',
        'invalidation_oid':'predecessor invalidation','predecessor_receipt_ref_oid':'receipt token',
        'expected_receipt_ref':'receipt ref scope mismatch','expected_receipt_schema':'receipt schema',
        'boundary':'source continuity boundary','reconciled':'source reconciliation'}
    for key in sorted(current):
        def invalid(b,key=key):
            for body in b.values():body['continuity'][key]='UNKNOWN_A2_STATE'
        add('continuity/'+key,invalid,reasons[key])
        def omit(b,key=key):
            for body in b.values():del body['continuity'][key]
        add('continuity-omission/'+key,omit,'predecessor continuity has missing or unknown fields')
    for group in ('one_shots','markers','handoffs','external_effects'):
        for field,reason in (('status','terminal status'),('kind','terminal record kind mismatch')):
            add('terminal/'+group+'/'+field,setpath(('STATE','payload','terminal','value',group,0,field),'UNKNOWN_A2_STATE'),reason)
    add('steer/status',setpath(('STATE','payload','steers','value',0,'status'),'UNKNOWN_A2_STATE'),'protected status')
    for group in ('reservation','result','consumption','historical_refusal','currentness','retry'):
        add('pending/'+group,setpath(('STATE','payload','pending_boundaries','value',0,group,'state'),'UNKNOWN_A2_STATE'),'')
    return cases


class Observations:
    def __init__(self,M,active,recorder,state):self.M=M;self.active=active;self.recorder=recorder;self.state=state
    def invoke(self,label,family,expect,function,*args,reason='',**kwargs):
        self.active['label']=label
        self.active['bucket']='baseline' if label.startswith('baseline/') else 'extended'
        row={'id':label,'family':family,'expected':expect,'api_first':len(self.recorder.rows)+1}
        self.state['cases'].append(row)
        try:
            result=function(*args,**kwargs)
        except BaseException as exc:
            row.update(api_last=len(self.recorder.rows),exception={'type':type(exc).__name__,'text':str(exc)})
            if expect=='refusal' and type(exc) is self.M.ProjectionV2Error and (not reason or reason in str(exc)):
                row['observed']='EXPECTED_PRODUCT_REFUSAL';return None
            row['observed']='UNEXPECTED_EXCEPTION';raise
        else:
            row.update(api_last=len(self.recorder.rows),observed='EXPECTED_RETURN' if expect=='return' else 'SURVIVED')
            if expect=='refusal':return None
            return result
        finally:self.active['label']=None

    def check(self,label,condition,details=None):
        self.state.setdefault('checks',[]).append({'id':label,'passed':bool(condition),'details':details})
        if not condition:raise AssertionError('A2 complete-population check failed: '+label)


def run(F,active,recorder):
    STATE['status']='STARTED';M=F.MODULE;obs=Observations(M,active,recorder,STATE)
    fixture_raw=F.FIXTURE.read_bytes();obs.check('exact-pinned-fixture',sha(fixture_raw)==FIXTURE_SHA256,pin(fixture_raw))
    fixture=json.loads(fixture_raw);base=source_bodies(fixture);extended=six_disposition_extension(base)
    baseline=pair(base,fixture);extended_pair=pair(extended,fixture)
    obs.check('original-fixture-factory-equals-independent-large-input',baseline==F.fixture_pair(base))
    obs.check('extended-fixture-factory-equals-independent-input',extended_pair==F.fixture_pair(extended))
    obs.check('full-original-large-source-pins',dict(zip(('STATE','ROADMAP'),map(pin,baseline[:2])))==PINNED)
    base_fields={r['field']:r for r in baseline[2]};ext_fields={r['field']:r for r in extended_pair[2]}
    obs.check('owner-denominator-222-to-342',len(base_fields)==222 and len(baseline[2])==222 and len(ext_fields)==342 and len(extended_pair[2])==342)
    obs.check('original-payload-leaves-survive-extension',all(r['source_kind']!='PAIR' or all(ext_fields[f][k]==r[k] for k in ('owner','source_kind','source_id','source_pointer','value_sha256')) for f,r in base_fields.items()))
    disposition_rows={group:[{'record_id':r['record_id'],'status':r['status'],'issuer':r['issuer'],'scope':r['scope'],
        'applicability':r['applicability'],'supersedes':r['supersedes']} for r in extended['STATE']['payload'][group]['value']] for group in ('instructions','authorisations')}
    obs.check('all-six-dispositions-each-group',all({r['status'] for r in rows}==set(DISPOSITIONS) for rows in disposition_rows.values()))
    STATE['population']={'original':{'owner_rows':222,'pair_leaves':219,'artifacts':3,'source_pair':PINNED},
        'extended':{'owner_rows':342,'pair_leaves':339,'artifacts':3,'source_pair':dict(zip(('STATE','ROADMAP'),map(pin,extended_pair[:2])))},
        'source_roles':list(base),'groups':{r:sorted(base[r]['payload']) for r in base},'six_dispositions':disposition_rows,
        'original_leaf_bindings_preserved':True,'fixture_statuses_are_not_authentic_grants':True}
    def parse(p):return M.parse_canonical_pair_v2(p[0],p[1],owner_map=p[2],artifacts=p[3])
    pre=obs.invoke('baseline/parse','positive','return',parse,baseline)
    ref_base=reference(base,baseline,None)
    obs.check('baseline-full-payload-and-owner-map',pre['payload']==ref_base['payload'] and pre['owner_map']==baseline[2] and pre['archive_population']==ref_base['archive_population'])
    draft=obs.invoke('baseline/draft','positive','return',M.derive_hot_pair_v2,pre,transition=None,archive_pointers=ref_base['pointers'],**LIMITS)
    obs.check('baseline-full-manifest-and-pair',draft['protected_manifest']==ref_base['manifest'] and draft['state_bytes']==ref_base['output']['STATE'] and draft['roadmap_bytes']==ref_base['output']['ROADMAP'])
    obs.invoke('baseline/verify','positive','return',M.verify_projection_equivalence_v2,pre,draft)
    pre=obs.invoke('extended/parse','positive','return',parse,extended_pair)
    successor=transition(extended,extended_pair);ref=reference(extended,extended_pair,successor)
    obs.check('extended-complete-owner-payload-archive-denominators',pre['payload']==ref['payload'] and pre['owner_map']==extended_pair[2] and pre['archive_population']==ref['archive_population'])
    candidates={}
    for name,t in (('draft',None),('rotation',successor),('recovery',transition(extended,extended_pair,True))):
        expected=reference(extended,extended_pair,t)
        c=obs.invoke('extended/'+name,'positive','return',M.derive_hot_pair_v2,pre,transition=t,archive_pointers=expected['pointers'],**LIMITS)
        obs.check('complete-'+name+'-manifest',set(c['protected_manifest'])==set(PARTS) and c['protected_manifest']==expected['manifest'])
        obs.check('complete-'+name+'-pair',c['state_bytes']==expected['output']['STATE'] and c['roadmap_bytes']==expected['output']['ROADMAP'])
        obs.invoke('extended/'+name+'/verify','positive','return',M.verify_projection_equivalence_v2,pre,c);candidates[name]=c
    candidate=candidates['rotation']
    payload_leaves=list(leaves(ref['payload']));manifest_leaves=list(leaves(ref['manifest']))
    obs.check('all-339-payload-leaves',len(payload_leaves)==339)
    STATE['catalog']={'owner_fields':[r['field'] for r in extended_pair[2]],
        'payload_leaves':[{'path':pointer(p),'value_sha256':sha(canonical(v))} for p,v in payload_leaves],
        'manifest_leaves':[{'path':pointer(p),'value_sha256':sha(canonical(v))} for p,v in manifest_leaves],
        'manifest_parts':{part:sum(1 for p,v in manifest_leaves if p[0]==part) for part in PARTS},
        'archive_records':ref['archive_population'],'limits':LIMITS}
    # Full source/owner input denominator, including all three external artifacts.
    for index,row in enumerate(extended_pair[2]):
        p=list(extended_pair);p[2]=p[2][:index]+p[2][index+1:]
        obs.invoke('owner/omit/'+row['field'],'owner-row-omission','refusal',parse,tuple(p))
        for column in sorted(row):
            p=list(extended_pair);p[2]=copy.deepcopy(p[2]);p[2][index][column]='A2_SEMANTIC_CHANGE'
            obs.invoke('owner/change/'+row['field']+'/'+column,'owner-column-semantic-change','refusal',parse,tuple(p))
    # Every exact protected leaf is separately omitted and semantically changed.
    for path,value in payload_leaves:
        for omission in (True,False):
            mutated=copy.deepcopy(candidate);mutated['payload']=changed(candidate['payload'],path,omit=omission)
            obs.invoke('payload/'+('omit' if omission else 'change')+pointer(path),'payload-leaf-omission' if omission else 'payload-leaf-semantic-change',
                'refusal',M.verify_projection_equivalence_v2,pre,mutated)
    # Complete four-part manifest field population is derived from input, checked
    # against product output, then each exact leaf receives both discriminators.
    for path,value in manifest_leaves:
        for omission in (True,False):
            mutated=copy.deepcopy(candidate);mutated['protected_manifest']=changed(ref['manifest'],path,omit=omission)
            obs.invoke('manifest/'+('omit' if omission else 'change')+pointer(path),'manifest-leaf-omission' if omission else 'manifest-leaf-semantic-change',
                'refusal',M.verify_projection_equivalence_v2,pre,mutated)
    unknown=unknown_mutations(extended)
    for label,bodies,reason in unknown:
        malformed=pair(bodies,fixture,frame_template=extended)
        obs.invoke('unknown/'+label,'unknown-or-missing-vocabulary','refusal',parse,malformed,reason=reason)
    for key in sorted(successor):
        for omission in (True,False):
            t=copy.deepcopy(successor)
            if omission:del t[key]
            else:t[key]='UNKNOWN_A2_TRANSITION'
            obs.invoke('transition/'+('omit/' if omission else 'unknown/')+key,'transition-omission-or-unknown','refusal',M.derive_hot_pair_v2,
                pre,transition=t,archive_pointers=ref['pointers'],**LIMITS)
    # Raw input relations must still be closed on the larger six-disposition input.
    relation_mutations=[]
    for group in ('instructions','authorisations'):
        for target in ('self','absent-record','oneshot-1'):
            b=copy.deepcopy(extended);row=b['STATE']['payload'][group]['value'][-6]
            row['supersedes']=[row['record_id'] if target=='self' else target]
            relation_mutations.append((group+'/'+target,b))
        b=copy.deepcopy(extended);rows=b['STATE']['payload'][group]['value'];a=rows[-6];z=rows[-4]
        a['supersedes']=[z['record_id']];z['supersedes']=[a['record_id']]
        relation_mutations.append((group+'/cycle',b))
    for target in ('absent-record','TC11-admission-history','phase-0','compensation-1'):
        b=copy.deepcopy(extended);b['ROADMAP']['payload']['compensations']['value'][0]['for_record']=target
        relation_mutations.append(('compensation/'+target,b))
    b=copy.deepcopy(extended);values=b['ROADMAP']['payload']['planning']['value']['action_selection'];values['omitted'].append(values['selected'][0])
    relation_mutations.append(('planning-selected-and-omitted',b))
    b=copy.deepcopy(extended);b['ROADMAP']['payload']['dependencies']['value'][0]['target']='absent-phase'
    relation_mutations.append(('dependency-absent-frontier',b))
    b=copy.deepcopy(extended);b['ROADMAP']['payload']['frontier']['value']['READY']=['phase-1']
    relation_mutations.append(('frontier-duplicate-state',b))
    for label,b in relation_mutations:
        obs.invoke('relation/'+label,'closed-relation-refusal','refusal',parse,pair(b,fixture))
    # A schema-valid changed scope with recomputed owner/receipt/hash metadata
    # must still fail equivalence to the immutable original extended preimage.
    for group in ('instructions','authorisations'):
        for index in range(len(extended['STATE']['payload'][group]['value'])-6,len(extended['STATE']['payload'][group]['value'])):
            b=copy.deepcopy(extended);row=b['STATE']['payload'][group]['value'][index];row['scope']+='; CHANGED AUTHORITY SCOPE'
            changed_pair=pair(b,fixture);other=obs.invoke('rebound/'+group+'/'+row['status']+'/parse','self-consistent-rebinding','return',parse,changed_pair)
            other_ref=reference(b,changed_pair,transition(b,changed_pair))
            forged=obs.invoke('rebound/'+group+'/'+row['status']+'/derive','self-consistent-rebinding','return',M.derive_hot_pair_v2,other,
                transition=transition(b,changed_pair),archive_pointers=other_ref['pointers'],**LIMITS)
            obs.invoke('rebound/'+group+'/'+row['status']+'/reject','self-consistent-rebinding','refusal',M.verify_projection_equivalence_v2,pre,forged)
    # All source/history descriptors are necessary independently of the manifest.
    for i,row in enumerate(ref['pointers']):
        pointers=ref['pointers'][:i]+ref['pointers'][i+1:]
        obs.invoke('archive/omit-record/'+str(i),'archive-pointer-population','refusal',M.derive_hot_pair_v2,pre,transition=successor,archive_pointers=pointers,**LIMITS)
        for key in sorted(row):
            for omission in (True,False):
                pointers=copy.deepcopy(ref['pointers'])
                if omission:del pointers[i][key]
                else:pointers[i][key]='UNKNOWN_A2_POINTER'
                obs.invoke('archive/'+('omit' if omission else 'change')+'/'+str(i)+'/'+key,'archive-pointer-field','refusal',M.derive_hot_pair_v2,
                    pre,transition=successor,archive_pointers=pointers,**LIMITS)
    # A different valid prospective invalidation remains allowed by pure algebra.
    # This guards against accidentally strengthening the oracle into false refusal.
    other_t=copy.deepcopy(successor);other_t['invalidation_oid']='4'*40
    other=obs.invoke('valid-prospective-invalidation','allowed-transition-algebra','return',M.derive_hot_pair_v2,
        pre,transition=other_t,archive_pointers=ref['pointers'],**LIMITS)
    obs.invoke('valid-prospective-invalidation/verify','allowed-transition-algebra','return',M.verify_projection_equivalence_v2,pre,other)
    counts={}
    for row in STATE['cases']:counts[row['family']]=counts.get(row['family'],0)+1
    expected={'positive':10,'owner-row-omission':342,'owner-column-semantic-change':342*7,
        'payload-leaf-omission':339,'payload-leaf-semantic-change':339,
        'manifest-leaf-omission':len(manifest_leaves),'manifest-leaf-semantic-change':len(manifest_leaves),
        'unknown-or-missing-vocabulary':len(unknown),'transition-omission-or-unknown':30,
        'closed-relation-refusal':15,'self-consistent-rebinding':36,
        'archive-pointer-population':4,'archive-pointer-field':4*15*2,'allowed-transition-algebra':2}
    obs.check('exact-complete-family-counts',counts==expected,{'observed':counts,'required':expected})
    obs.check('all-declared-calls-observed',all(r['api_last']>=r['api_first'] for r in STATE['cases']))
    obs.check('all-original-adverse-outcomes-retained-no-survivor',all(r['observed'] in {'EXPECTED_RETURN','EXPECTED_PRODUCT_REFUSAL'} for r in STATE['cases']))
    STATE.update(status='ALL_DECLARED_A2_OBSERVATIONS_RETAINED',case_count=len(STATE['cases']),family_counts=counts,
        expected_family_counts=expected,authority='NONE',award=None)
    return STATE


def native_case(A,active,recorder):
    class NativePointerSupplement(A.ArchiveQualification):
        def test_complete_immutable_pointer_binding_omission_and_change(self):
            NATIVE_STATE['status']='STARTED'
            subject=self.subject(name='supplement-pointer')
            self.assertEqual(dict(zip(('STATE','ROADMAP'),map(pin,subject['source']))),PINNED)
            prepared=A.prepare(subject);t=A.transition(subject,prepared)
            final=A.M.finalize_canonical_projection(subject['repo'],subject['run'],prepared,t)
            pointer_value=final['pointer'];self.assertEqual(set(pointer_value),set(POINTER_FIELDS))
            before=A.M.read_canonical_generation(subject['repo'],subject['run'],pointer_value)
            self.assertEqual(len(before['protected_manifest']['PRESERVED_PAYLOAD']['owner_map']),222)
            self.assertEqual(len(before['archive_manifest']['entries']),6)
            refs_before=A.git(subject['repo'],'for-each-ref','--format=%(refname) %(objectname)')
            for key in POINTER_FIELDS:
                for omission in (True,False):
                    bad=copy.deepcopy(pointer_value)
                    if omission:del bad[key]
                    elif key in {'state_sha256','roadmap_sha256','protected_manifest_sha256','archive_manifest_sha256'}:bad[key]='0'*64
                    elif key=='invalidation_oid':bad[key]='b'*40
                    elif key=='predecessor_receipt_ref_oid':bad[key]=bad[key].split('@')[0]+'@'+'b'*40
                    elif key in {'projection_generation_id','continuity_epoch'}:bad[key]='G0003'
                    elif key=='expected_receipt_ref_schema':bad[key]['ref']=bad[key]['ref'].replace('G0002','G0003')
                    elif key=='controller':bad[key]='other-controller'
                    elif key=='claim_id':bad[key]='other-claim'
                    elif key=='run_root_identity':bad[key]='.IMPLEMENTAUDIT/runs/other-controller'
                    else:bad[key]=str(bad[key])+'-changed'
                    label='native-pointer/'+('omit/' if omission else 'change/')+key;active['label']=label
                    row={'id':label,'field':key,'mutation':'omission' if omission else 'semantic-change',
                        'api_first':len(recorder.rows)+1};NATIVE_STATE['cases'].append(row)
                    try:
                        A.M.read_canonical_generation(subject['repo'],subject['run'],bad)
                    except A.M.RotationError as exc:
                        row.update(observed='EXPECTED_PRODUCT_REFUSAL',exception={'type':type(exc).__name__,'text':str(exc)})
                    except BaseException as exc:
                        row.update(observed='UNEXPECTED_EXCEPTION',exception={'type':type(exc).__name__,'text':str(exc)})
                        raise
                    else:row['observed']='SURVIVED'
                    finally:row['api_last']=len(recorder.rows);active['label']=None
            after=A.M.read_canonical_generation(subject['repo'],subject['run'],pointer_value)
            refs_after=A.git(subject['repo'],'for-each-ref','--format=%(refname) %(objectname)')
            self.assertEqual(before,after);self.assertEqual(refs_before,refs_after)
            self.assertEqual(len(NATIVE_STATE['cases']),30)
            self.assertTrue(all(r['observed']=='EXPECTED_PRODUCT_REFUSAL' and r['api_last']>=r['api_first'] for r in NATIVE_STATE['cases']))
            NATIVE_STATE.update(status='ALL_NATIVE_POINTER_OBSERVATIONS_RETAINED',case_count=30,
                pointer=copy.deepcopy(pointer_value),prepared=copy.deepcopy(prepared),
                refs_before=refs_before.decode(),refs_after=refs_after.decode(),
                original_222_owner_population=True,source_pair=PINNED,
                native_archive_and_immutable_reader=True,native_currentness_or_issuer_authority=False)
    return NativePointerSupplement
