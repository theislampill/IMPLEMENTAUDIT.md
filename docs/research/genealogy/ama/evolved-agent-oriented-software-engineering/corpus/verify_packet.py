#!/usr/bin/env python3
"""Verify the canonical AOSE corpus and optional enclosing ZIP.
Usage: python verify_packet.py /path/to/directory_or_packet.zip
This verifies machine consistency and custody, not independent correctness of research.
No third-party packages, network access or repository access are needed.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, re, tempfile, zipfile
P='EVOLVED_AGENT_ORIENTED_SOFTWARE_ENGINEERING'
EXPECTED={'A':('EAOSE-R1-2026-09-07',469408,'18307c9d436757eb102ba73da31e00ce78bd08596ee7437bba4a7750810f4b87',113,90),'B':('EAOSE-2026-09-07-R1',409921,'6338c0582fc2dcd521a0325a5b73f16a2eb412ef9332f43819a9572c63ec1bce',83,62)}
REQUIRED=['CANONICAL_FROZEN_REPORT.md','CANONICAL_PROPERTY_LEDGER.json','CANONICAL_SOURCE_TABLE.json','CANONICAL_COMPOSITION_MODEL.json','CANONICAL_RESEARCH_COVERAGE.json','RECONCILIATION_LEDGER.json','SOURCE_RECONCILIATION_LEDGER.json','COMPOSITION_INDUCED_RECONCILIATION.json','CANONICAL_AUDIT_INTAKE.md','CANONICAL_PUBLIC_DOCUMENTATION_INTAKE.md','CANONICAL_SYNTHESIS_INTAKE.md','CANONICAL_COMPLETENESS_REVIEW.md']
AXES={'METHODOLOGY_AND_LIFECYCLE_SCOPE','STAKEHOLDER_GOAL_AND_REQUIREMENT_SEMANTICS','AGENT_ABSTRACTION_JUSTIFICATION','ROLE_ORGANISATION_AND_AGENT_MAPPING','INTERACTION_SPECIFICATION_AND_PROTOCOL_SEMANTICS','DESIGN_TO_IMPLEMENTATION_CORRESPONDENCE','VERIFICATION_VALIDATION_AND_TEST_ORACLE','TOOL_SUPPORT_AND_MANUAL_OBLIGATIONS','DEPLOYMENT_EVOLUTION_AND_TRACEABILITY','COMPARATIVE_EVIDENCE_COST_AND_NON_AGENT_ALTERNATIVE'}
def digest(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def verify(root:pathlib.Path, require_manifest:bool=True)->dict:
 checks=[]
 def test(name,condition,detail=None):
  checks.append(dict(check=name,result='PASS' if condition else 'FAIL',detail=detail))
 def read(kind):return json.loads((root/(P+'_'+kind+'.json')).read_text(encoding='utf-8'))
 test('Required substantive payload inventory',all((root/(P+'_'+f)).is_file() for f in REQUIRED))
 parsed={}
 for path in sorted(root.glob('*.json')):
  try:parsed[path.name]=json.loads(path.read_text(encoding='utf-8'));test('JSON parse: '+path.name,True)
  except (ValueError,UnicodeError) as e:test('JSON parse: '+path.name,False,str(e))
 L=read('CANONICAL_PROPERTY_LEDGER');S=read('CANONICAL_SOURCE_TABLE');R=read('RECONCILIATION_LEDGER');SR=read('SOURCE_RECONCILIATION_LEDGER');C=read('CANONICAL_COMPOSITION_MODEL');I=read('COMPOSITION_INDUCED_RECONCILIATION');V=read('CANONICAL_RESEARCH_COVERAGE');E=read('CANONICAL_CRITICAL_EVIDENCE')
 pp=L['properties'];ss=S['sources'];pids={p['PROPERTY_ID'] for p in pp};sids={s['SOURCE_ID'] for s in ss};pd={p['PROPERTY_ID']:p for p in pp};keys={p['SEMANTIC_KEY']:p for p in pp}
 pmap={r['qualified_input_id']:r['canonical_targets'] for r in R['mappings']};smap={r['qualified_input_id']:r['canonical_target'] for r in SR['mappings']}
 test('Unique canonical property IDs and contiguous new namespace',len(pids)==len(pp) and pids=={f'EAOSE-C{i:03d}' for i in range(1,len(pp)+1)})
 test('Unique canonical source IDs and contiguous new namespace',len(sids)==len(ss) and sids=={f'EAOSE-CS{i:03d}' for i in range(1,len(ss)+1)})
 test('Derived canonical populations',L['population_total']==L['population_examined']==len(pp)==R['canonical_population'] and S['source_count']==len(ss)==SR['canonical_source_population'])
 test('Disposition count partition',dict(collections.Counter(p['CANONICAL_DISPOSITION'] for p in pp))==L['disposition_counts'] and sum(L['disposition_counts'].values())==len(pp))
 test('Examination partition',dict(collections.Counter(p['EXAMINATION_STATUS'] for p in pp))==L['examination_counts'] and all(p['EXAMINATION_STATUS'].startswith('EXAMINED') for p in pp))
 test('Property reconciliation exactly 196 unique inputs',len(R['mappings'])==len(pmap)==196 and set(pmap)=={f'{l}:EAOSE-{i:03d}' for l,n in [('A',113),('B',83)] for i in range(1,n+1)})
 test('Source reconciliation exactly 152 unique inputs',len(SR['mappings'])==len(smap)==152 and set(smap)=={f'{l}:{prefix}-S{i:03d}' for l,prefix,n in [('A','EAOSE',90),('B','AOSE',62)] for i in range(1,n+1)})
 test('No orphan property inputs',all(ts and set(ts)<=pids for ts in pmap.values()))
 test('No orphan source inputs',all(t in sids for t in smap.values()))
 test('Every canonical property has ancestry',all(p['A_ANCESTRY'] or p['B_ANCESTRY'] or p['ORIGIN_CLASS']=='RECONCILIATION_INDUCED_ANALYTICAL_RESULT' for p in pp))
 test('Property ancestry reverse consistency',all(set(p['A_ANCESTRY']+p['B_ANCESTRY'])=={q for q,t in pmap.items() if p['PROPERTY_ID'] in t} for p in pp))
 test('Source ancestry reverse consistency',all(set(s['A_ANCESTRY']+s['B_ANCESTRY'])=={q for q,t in smap.items() if s['SOURCE_ID']==t} for s in ss))
 test('Property/source cross references',all(set(p['CANONICAL_SOURCE_IDS'])<=sids for p in pp) and all(set(s['SUPPORTED_PROPERTY_IDS'])<=pids for s in ss))
 test('Reverse source support contains every canonical binding',all(p['PROPERTY_ID'] in next(s for s in ss if s['SOURCE_ID']==sid)['SUPPORTED_PROPERTY_IDS'] for p in pp for sid in p['CANONICAL_SOURCE_IDS']))
 mandatory={'PROPERTY_ID','PROPERTY_NAME','ORIGIN_CLASS','HISTORICAL_ORIGIN','ORIGINAL_FORM','BEARER','PROBLEM','CRITERION','FAILURE_MODE','MECHANISM','TRIGGER','NON_TRIGGER','REQUIRED_INPUTS','DOMAIN_PROFILE','EXPECTED_PAYOFF','CONSUMER','AUTHORITY','COMMUNICATION','OBSERVABLE_POSTCONDITION','CRITICISMS','EVOLVED_FORM','CEREMONY_JUDGEMENT','CANONICAL_DISPOSITION','EVIDENCE_PARTITIONS','CANONICAL_SOURCE_IDS','CONTRARY_EVIDENCE','ASSUMPTION_SENSITIVITY','DUPLICATE_OR_SUPERSESSION_LINKS','OPEN_QUESTIONS','EXAMINATION_STATUS','OMISSION_OR_RETIREMENT_CONDITION','LATER_CROSSWALK_QUESTIONS','RECONCILIATION_RATIONALE','DISPOSITION_ADJUDICATION'}
 test('Required canonical property fields',all(mandatory<=set(p) and all(p[k] is not None for k in mandatory) for p in pp))
 test('Ten real domain-profile axes per property',all(set(p['DOMAIN_PROFILE'])==AXES and all(d['contributions'] and all('Not separately specified' not in str(c['value']) for c in d['contributions']) for d in p['DOMAIN_PROFILE'].values()) for p in pp))
 test('Dependency references',all(set(p['DEPENDENCY_PROPERTY_IDS'])<=pids-{p['PROPERTY_ID']} for p in pp))
 rids={r['RELATION_ID'] for r in C['relations']};ccids={r['CRITICISM_ID'] for r in E['criticisms']};ttids={r['TENSION_ID'] for r in E['tensions']}
 test('Unique composition relation IDs and independent edge count',len(rids)==len(C['relations'])==C['canonical_edge_count'] and C['mechanical_edge_union_performed'] is False)
 test('Composition property/source references',all(set(r['SOURCE_PROPERTY_IDS']+r['TARGET_PROPERTY_IDS'])<=pids and set(r['SOURCE_IDS'])<=sids for r in C['relations']))
 test('Every property has a guarded composition relation',all(p['COMPOSITION_RELATION_IDS'] and set(p['COMPOSITION_RELATION_IDS'])<=rids for p in pp))
 test('Composition reverse references',all(r['RELATION_ID'] in pd[x]['COMPOSITION_RELATION_IDS'] for r in C['relations'] for x in r['SOURCE_PROPERTY_IDS']+r['TARGET_PROPERTY_IDS']))
 test('Critical/tension references',all(set(p['CRITICISM_IDS'])<=ccids and set(p['TENSION_IDS'])<=ttids for p in pp) and all(set(r['PROPERTY_IDS'])<=pids and set(r['SOURCE_IDS'])<=sids for r in E['criticisms']+E['tensions']))
 test('All 44 input criticisms and 24 tensions accounted',len(E['criticism_input_accounting'])==44 and len(E['tension_input_accounting'])==24)
 test('All 40 input cases retained',len(E['cases'])==40 and len({c['INPUT_ID'] for c in E['cases']})==40 and all(set(c['CANONICAL_PROPERTY_IDS'])<=pids and set(c['CANONICAL_SOURCE_IDS'])<=sids for c in E['cases']))
 test('Empirical/formal unit references',all(set(r['CANONICAL_PROPERTY_IDS'])<=pids and set(r['CANONICAL_SOURCE_IDS'])<=sids for r in E['empirical_unit_records']+E['formal_result_records']))
 test('All 353 inherited B source-claim bindings preserved',len(E['inherited_source_claim_bindings'])==353 and all(set(r['CANONICAL_PROPERTY_TARGETS'])<=pids and set(r['CANONICAL_SOURCE_IDS'])<=sids for r in E['inherited_source_claim_bindings']))
 reqproposals={'A:EAOSE-079','A:EAOSE-080','A:EAOSE-081','A:EAOSE-113','B:EAOSE-073','B:EAOSE-074','B:EAOSE-075','B:EAOSE-076','B:EAOSE-080','B:EAOSE-081','B:EAOSE-082','B:EAOSE-083'}
 pro={r['QUALIFIED_INPUT_ID']:r for r in I['input_proposal_records']}
 test('Every required composition proposal adjudicated',reqproposals<=set(pro) and all(r['CANONICAL_DISPOSITION'] and set(r['CANONICAL_TARGETS'])<=pids and set(r['PARENT_MECHANISMS'])<=pids for r in pro.values()))
 test('Zero distinct induced properties is consistent',I['retained_distinct_induced_count']==len(I['retained_distinct_induced_ids'])==0 and C['composition_induced_property_ids']==[] and not any(p['ORIGIN_CLASS']=='ANALYTICAL_COMPOSITION_INDUCED' for p in pp))
 test('Operational coupling retained as a relation bundle',len(I['relational_bundles'])==1 and C['relational_bundles']==I['relational_bundles'] and pro['A:EAOSE-079']['CANONICAL_DISPOSITION']==pro['B:EAOSE-073']['CANONICAL_DISPOSITION']=='relation-only')
 test('Additional induced search completed',I['search_complete'] and len(I['new_search_candidates'])==7 and all(r['ADJUDICATION'] and set(r['CANONICAL_TARGETS'])<=pids for r in I['new_search_candidates']))
 dup={q for p in pp for q in p['DUPLICATE_INPUT_ALIASES']}
 test('Six duplicate input aliases not additional active properties',dup=={'A:EAOSE-042','A:EAOSE-080','A:EAOSE-113','B:EAOSE-074','B:EAOSE-075','B:EAOSE-081'} and L['disposition_counts'].get('DUPLICATE_CANDIDATE',0)==0)
 test('Rejected analytical universals preserved',pro['B:EAOSE-080']['CANONICAL_DISPOSITION']=='rejected' and pro['B:EAOSE-082']['CANONICAL_DISPOSITION']=='rejected' and not keys['fragment_feasibility']['ACTIVE_MECHANISM'] and not keys['automatic_improvement']['ACTIVE_MECHANISM'])
 test('Two distinct whole-method unresolved scopes',keys['whole_evolved']['PROPERTY_ID']!=keys['whole_named']['PROPERTY_ID'] and keys['whole_evolved']['CANONICAL_DISPOSITION']==keys['whole_named']['CANONICAL_DISPOSITION']=='UNRESOLVED' and 'newly synthesised' in keys['whole_evolved']['CRITERION'] and 'complete AOSE methodologies' in keys['whole_named']['CRITERION'])
 test('Conventional branch preserved',any('Conventional software' in c['NAME'] for c in C['alternative_configurations']))
 test('All configuration references resolve',all(set(c['REQUIRED_MECHANISMS']+c['OMITTED_MECHANISMS'])<=pids and c['TRIGGER'] and c['AUTHORITY_ASSUMPTIONS'] and c['EVIDENCE_REQUIREMENTS'] and c['SUBSTITUTION_RETIREMENT_PATH'] for c in C['alternative_configurations']))
 test('Nine operative states kept distinct',set(C['conceptual_distinctions'])=={'intention','obligation','authority','permission','capability','issued_action','executed_action','observed_effect','accepted_outcome'})
 test('Changed support not automatically conclusion falsity','without logically falsifying' in keys['selective_revalidation']['CRITERION'])
 test('Contemporary responsiveness remains sourced',keys['plan_responsiveness']['ORIGIN_CLASS']!='ANALYTICAL_COMPOSITION_INDUCED' and 'FV05' in keys['plan_responsiveness']['FRESH_VERIFICATION_IDS'] and 'not composition-induced' in keys['plan_responsiveness']['EVIDENCE_BOUNDARY'])
 a=V['archival_provenance']
 test('Historical66 neither recovered nor fabricated',a['HISTORICAL_66_ROW_ROSTER_RECOVERED'] is False and a['HISTORICAL_66_ROW_ROSTER_FABRICATED'] is False and a['ARCHIVAL_66_QUALIFICATION_PRESERVED'] and a['current_input_denominator']==196)
 test('All ten mandatory families examined',len(V['families'])==10 and {f['FAMILY_ID'] for f in V['families']}=={f'O{i}' for i in range(1,11)} and V['uncompleted_mandatory_families']==0 and not V['uncompleted_burdens'] and all(f['PROPERTY_IDS'] and f['SOURCE_IDS'] for f in V['families']))
 test('Family/source/property/critic references',all(set(f['PROPERTY_IDS'])<=pids and set(f['SOURCE_IDS'])<=sids and set(f['CRITICISM_IDS'])<=ccids for f in V['families']))
 gn={n['NODE_ID'] for n in V['genealogy']['nodes']}
 test('All 49 genealogy-node observations preserved',len(V['genealogy']['input_node_accounting'])==49 and all(set(t)<=gn for t in V['genealogy']['input_node_accounting'].values()))
 test('Genealogy references resolve',all(e['SOURCE'] in gn and e['TARGET'] in gn for e in V['genealogy']['edges']) and all(set(n['PROPERTY_IDS'])<=pids and set(n['SOURCE_IDS'])<=sids for n in V['genealogy']['nodes']))
 test('Original 54 requirements + 4 owner-history items audited',len(V['requirements_audit'])==58 and sum(r['ORIGIN']=='ORIGINAL_PROMPT_CLAUSE_INDEX' for r in V['requirements_audit'])==54 and all(r['CANONICAL_DISPOSITION'] and r['B_EVIDENCE_LOCATOR'] for r in V['requirements_audit']))
 test('All 36 controlling prompt sections audited',len(V['controlling_reconciliation_requirement_audit'])==36 and {r['SECTION'] for r in V['controlling_reconciliation_requirement_audit']}==set(range(36)))
 report=(root/(P+'_CANONICAL_FROZEN_REPORT.md')).read_text(encoding='utf-8');syn=(root/(P+'_CANONICAL_SYNTHESIS_INTAKE.md')).read_text(encoding='utf-8');audit=(root/(P+'_CANONICAL_AUDIT_INTAKE.md')).read_text(encoding='utf-8');public=(root/(P+'_CANONICAL_PUBLIC_DOCUMENTATION_INTAKE.md')).read_text(encoding='utf-8')
 test('Complete unique synthesis intake export',re.findall(r'^## (EAOSE-C\d{3}) —',syn,re.M)==[p['PROPERTY_ID'] for p in pp])
 test('Complete unique audit intake export',re.findall(r'^## (EAOSE-C\d{3}) —',audit,re.M)==[p['PROPERTY_ID'] for p in pp])
 test('Full property census in report',all('| '+p['PROPERTY_ID']+' |' in report for p in pp))
 test('Report counts match ledgers',f'{len(pp)}/{len(pp)} examined' in report and f'{len(C["relations"])} newly derived guarded relations' in report and f'{len(ss)} canonical source records' in report and 'No distinct induced property survives' in report)
 test('No stale removed canonical property ID',not any('EAOSE-C133' in text for text in [report,syn,audit,public]))
 test('Public documentation boundary','IMPLEMENTAUDIT' not in public and 'No distinct induced property survives' in public and 'Conventional software remains a legitimate configuration' in public)
 test('Scope declarations forbid sibling/target contamination',any('No sibling corpora' in s for s in V['scope_boundaries']) and any('No AMA' in s for s in V['scope_boundaries']))
 # Verify immutable original payloads and original local JSON-pointer references.
 for label,(rev,size,h,np,ns) in EXPECTED.items():
  zpath=root/'inputs'/f'PACKET_{label}.zip'
  test(f'{label} immutable original ZIP exists',zpath.is_file())
  if not zpath.is_file():continue
  b=zpath.read_bytes();test(f'{label} input bytes and SHA256',len(b)==size and digest(b)==h)
  with zipfile.ZipFile(zpath) as z:
   test(f'{label} input CRC and nine-member inventory',z.testzip() is None and len(z.namelist())==9)
   m=json.loads(z.read(P+'_FROZEN_MANIFEST.json'));test(f'{label} actual manifest revision',m['revision']==rev)
   checks0=[len(z.read(r['filename']))==r['bytes'] and digest(z.read(r['filename']))==r['sha256'] for r in m['payloads']]
   test(f'{label} all eight original payload hashes',len(checks0)==8 and all(checks0))
   pl=json.loads(z.read(P+'_PROPERTY_LEDGER.json'));sl=json.loads(z.read(P+'_SOURCE_TABLE.json'))
   test(f'{label} actual property/source populations',len(pl['properties'])==np and len(sl['sources'])==ns and pl['population_examined']==np)
   test(f'{label} every current property ID verified', {p['PROPERTY_ID'] for p in pl['properties']}=={f'EAOSE-{i:03d}' for i in range(1,np+1)})
   if label=='B':
    def ptr(doc,path):
     v=doc
     for k in path.lstrip('#/').split('/'):v=v[int(k)] if isinstance(v,list) else v[k]
     return v
    good=True
    for p in pl['properties']:
     for val in p['DOMAIN_PROFILE'].values():
      if isinstance(val,dict) and 'BASE_REF' in val:
       try:ptr(pl,val['BASE_REF'])
       except (KeyError,IndexError,TypeError,ValueError):good=False
    test('B preserved local domain-profile pointers resolve in original B ledger',good)
 mf=root/(P+'_CANONICAL_FROZEN_MANIFEST.json')
 if require_manifest:
  test('Manifest exists',mf.is_file())
  if mf.is_file():
   m=json.loads(mf.read_text());actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file()};expected={r['filename'] for r in m['payloads']}|{mf.name}
   test('Manifest inventory excludes circular self/ZIP hashing',mf.name not in {r['filename'] for r in m['payloads']} and not any(r['filename'].endswith('CANONICAL_FROZEN_PACKET.zip') for r in m['payloads']))
   test('Exact payload member inventory',actual==expected,{'actual_count':len(actual),'expected_count':len(expected)})
   test('All manifest payload bytes and hashes',all((root/r['filename']).is_file() and len((root/r['filename']).read_bytes())==r['bytes'] and digest((root/r['filename']).read_bytes())==r['sha256'] for r in m['payloads']))
 failures=[c for c in checks if c['result']=='FAIL']
 return dict(state='PASS' if not failures else 'FAIL',checks_run=len(checks),checks=checks,failures=failures,counts=dict(properties=len(pp),examined=L['population_examined'],sources=len(ss),input_properties=len(pmap),input_sources=len(smap),dispositions=L['disposition_counts'],examination=L['examination_counts'],relations=len(C['relations']),configurations=len(C['alternative_configurations']),criticisms=len(E['criticisms']),tensions=len(E['tensions']),cases=len(E['cases']),induced=I['retained_distinct_induced_count'],unresolved=L['disposition_counts'].get('UNRESOLVED',0),contested=L['disposition_counts'].get('CONTESTED',0)),limit='Machine reference/count/custody validation plus explicit semantic-boundary assertions; not an independent proof of scholarly correctness or completeness outside the declared reconciliation scope.')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('path',type=pathlib.Path);ap.add_argument('--preflight',action='store_true',help='Do not require final manifest');args=ap.parse_args()
 if args.path.is_dir():out=verify(args.path,not args.preflight)
 else:
  b=args.path.read_bytes()
  with tempfile.TemporaryDirectory(prefix='aose_verify_') as td:
   root=pathlib.Path(td)
   with zipfile.ZipFile(args.path) as z:
    if z.testzip() is not None:raise ValueError('Enclosing archive failed CRC')
    for n in z.namelist():
     target=(root/n).resolve()
     if not target.is_relative_to(root.resolve()):raise ValueError('Unsafe archive path')
    z.extractall(root)
   out=verify(root,not args.preflight);out['enclosing_archive']=dict(bytes=len(b),sha256=digest(b),crc='PASS',fresh_extraction=True)
 print(json.dumps(out,ensure_ascii=False,indent=2))
 raise SystemExit(0 if out['state']=='PASS' else 1)
if __name__=='__main__':main()
