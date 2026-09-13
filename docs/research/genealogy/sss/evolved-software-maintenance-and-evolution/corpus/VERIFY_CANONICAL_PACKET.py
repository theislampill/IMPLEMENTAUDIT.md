#!/usr/bin/env python3
"""Read-only custody and structural verifier; stdlib only.

Usage: python VERIFY_CANONICAL_PACKET.py <directory-or-zip> [--output receipt.json]
Checks internal consistency and exact input-record conservation, not scholarly truth.
No files in the target are modified, and ZIP contents are never executed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile
from typing import Any
P='EVOLVED_SOFTWARE_MAINTENANCE_AND_EVOLUTION'
MAN=P+'_CANONICAL_FROZEN_MANIFEST.json'
REVISIONS={'A':'ESME-R2-2026-09-06','B':'ESME-2026-09-06-r1'}
INPUT_HASH={'A':'164c683b37e50e24ec374180de0112c1f763f8412b1a2d0705c268ae853134e0','B':'89d8623c470239d8237018010e59426610481e27d7e89beb5309be2a02dd7a60'}
REQUIRED=[P+'_'+x for x in ['CANONICAL_FROZEN_REPORT.md','CANONICAL_PROPERTY_LEDGER.json','CANONICAL_SOURCE_TABLE.json','CANONICAL_COMPOSITION_MODEL.json','CANONICAL_RESEARCH_COVERAGE.json','CANONICAL_AUDIT_INTAKE.md','CANONICAL_PUBLIC_DOCUMENTATION_INTAKE.md','CANONICAL_SYNTHESIS_INTAKE.md','RECONCILIATION_LEDGER.json','SOURCE_RECONCILIATION_LEDGER.json','CANONICAL_FROZEN_MANIFEST.json']]
def digest(b:bytes)->str:return hashlib.sha256(b).hexdigest()
class VerificationError(Exception):pass
class Checks:
 def __init__(self):self.count=0;self.categories=Counter()
 def require(self,condition:bool,category:str,detail:str)->None:
  self.count+=1;self.categories[category]+=1
  if not condition:raise VerificationError(f'{category}: {detail}')

def parse_json(b:bytes)->Any:
 def pairs(ps):
  d={}
  for k,v in ps:
   if k in d:raise VerificationError(f'JSON duplicate key: {k}')
   d[k]=v
  return d
 return json.loads(b.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(VerificationError('Non-finite JSON: '+x)))

def safe_name(n:str)->bool:
 p=PurePosixPath(n)
 return bool(n) and not p.is_absolute() and '..' not in p.parts and '\\' not in n and ':' not in n and not n.endswith('/')

def load_target(path:Path,c:Checks)->tuple[dict[str,bytes],dict]:
 if path.is_dir():
  members={}
  for f in path.rglob('*'):
   c.require(not f.is_symlink(),'path_safety',str(f))
   if f.is_file():
    n=f.relative_to(path).as_posix();c.require(safe_name(n),'path_safety',n);members[n]=f.read_bytes()
  return members,{'target_kind':'DIRECTORY','target':str(path),'archive_crc':'NOT_APPLICABLE'}
 b=path.read_bytes()
 with zipfile.ZipFile(io.BytesIO(b),'r') as z:
  names=z.namelist();c.require(len(names)==len(set(names)),'zip','duplicate member')
  c.require(all(safe_name(n) for n in names),'zip','unsafe member name')
  c.require(sum(i.file_size for i in z.infolist())<200_000_000,'zip','unexpected expanded size')
  c.require(z.testzip() is None,'zip','CRC failure')
  members={n:z.read(n) for n in names}
 return members,{'target_kind':'ZIP','target':str(path),'archive_bytes':len(b),'archive_sha256':digest(b),'archive_crc':'PASS','archive_reopened':True}

def verify_members(members:dict[str,bytes],c:Checks)->dict:
 c.require(set(REQUIRED)<=set(members),'mandatory_files','eleven mandatory payloads')
 man=parse_json(members[MAN]);c.require(man['state']=='FROZEN','manifest','state')
 c.require(man['lineage_id']==P,'manifest','lineage');c.require(man['research_cutoff']=='2026-09-06','manifest','cutoff')
 inventory=man['payload_inventory'];names=[x['filename'] for x in inventory]
 c.require(len(names)==len(set(names)),'manifest','duplicate inventory')
 c.require(set(names)|{MAN}==set(members),'manifest','exact archive membership')
 for q in inventory:
  b=members[q['filename']];c.require(len(b)==q['bytes'],'payload_bytes',q['filename']);c.require(digest(b)==q['sha256'],'payload_sha256',q['filename'])
 parsed={n:parse_json(b) for n,b in members.items() if n.endswith('.json')}
 for n,x in parsed.items():c.require(isinstance(x,dict),'json_utf8_parse',n)
 def get(s):return parsed[P+'_'+s+'.json']
 pl=get('CANONICAL_PROPERTY_LEDGER');sl=get('CANONICAL_SOURCE_TABLE');co=get('CANONICAL_COMPOSITION_MODEL');cv=get('CANONICAL_RESEARCH_COVERAGE');recon=get('RECONCILIATION_LEDGER');sr=get('SOURCE_RECONCILIATION_LEDGER');aux=get('CANONICAL_CRITICAL_AND_CASE_LEDGER');gen=get('CANONICAL_GENEALOGY_RECONCILIATION');syn=get('CANONICAL_SYNTHESIS_INTAKE')
 props=pl['properties'];sources=sl['sources'];rows=recon['rows'];srows=sr['rows']
 def keyed(xs,key,cat):
  ids=[x[key] for x in xs];c.require(len(ids)==len(set(ids)),'unique_ids',cat);return dict(zip(ids,xs))
 pp=keyed(props,'CANONICAL_PROPERTY_ID','properties');ss=keyed(sources,'CANONICAL_SOURCE_ID','sources');rr=keyed(rows,'INPUT_PROPERTY_KEY','input properties');srr=keyed(srows,'INPUT_SOURCE_KEY','input sources');rel=keyed(co['relations'],'CANONICAL_RELATION_ID','relations');cfg=keyed(co['alternative_configurations'],'CANONICAL_CONFIGURATION_ID','configurations')
 crit=keyed(aux['criticism_ledger'],'CANONICAL_CRITICISM_ID','criticisms');ten=keyed(aux['internal_tensions'],'CANONICAL_TENSION_ID','tensions');cases=keyed(aux['case_tests'],'CANONICAL_CASE_ID','cases');cer=keyed(aux['ceremony_stripping_ledger'],'CANONICAL_CEREMONY_ID','ceremonies');openqs=keyed(co['unresolved_composition_obligations'],'CANONICAL_OPEN_OBLIGATION_ID','open questions')
 c.require(set(pp)=={f'ESME-C{i:03d}' for i in range(1,len(pp)+1)},'namespace','property sequence')
 c.require(set(ss)=={f'ESME-CS{i:03d}' for i in range(1,len(ss)+1)},'namespace','source sequence')
 expectedprops={f'{lab}:ESME-{i:03d}' for lab,n in [('A',98),('B',74)] for i in range(1,n+1)}
 expectedsources={f'{lab}:ESME-S{i:03d}' for lab in 'AB' for i in range(1,68)}
 c.require(set(rr)==expectedprops,'input_coverage','172 properties exact');c.require(set(srr)==expectedsources,'input_coverage','134 sources exact')
 originals={};origprops={};origsources={}
 for lab in 'AB':
  b=members[f'inputs/PACKET_{lab}.zip'];c.require(digest(b)==INPUT_HASH[lab],'immutable_input_sha256',lab)
  with zipfile.ZipFile(io.BytesIO(b),'r') as z:
   c.require(z.testzip() is None,'input_zip_crc',lab)
   c.require(len(z.namelist())==9 and len(set(z.namelist()))==9,'input_zip_membership',lab)
   om=parse_json(z.read(P+'_FROZEN_MANIFEST.json'))
   c.require(om['revision']==REVISIONS[lab] and om['lineage_id']==P,'input_identity',lab)
   c.require(om.get('state',om.get('research_state'))=='FROZEN','input_identity',lab+' state')
   payloads=om.get('payloads',om.get('payload_inventory'));pn=[]
   for q in payloads:
    name=q.get('relative_filename',q.get('filename'));pn.append(name);bb=z.read(name)
    c.require(len(bb)==q['bytes'] and digest(bb)==q['sha256'],'input_payload_manifest',lab+':'+name)
   c.require(set(pn)|{P+'_FROZEN_MANIFEST.json'}==set(z.namelist()),'input_zip_membership',lab+' manifest')
   original={kind:parse_json(z.read(P+'_'+kind+'.json')) for kind in ['PROPERTY_LEDGER','SOURCE_TABLE','COMPOSITION_MODEL','RESEARCH_COVERAGE']}
   original['SYNTHESIS_TEXT']=z.read(P+'_SYNTHESIS_INTAKE.md').decode('utf8')
   originals[lab]=original
   for q in original['PROPERTY_LEDGER']['properties']:origprops[f'{lab}:{q["PROPERTY_ID"]}']=q
   for q in original['SOURCE_TABLE']['sources']:origsources[f'{lab}:{q["SOURCE_ID"]}']=q
 c.require(set(origprops)==expectedprops and set(origsources)==expectedsources,'input_coverage','embedded actual rows')
 for k,r in rr.items():
  c.require(r['FROZEN_ORIGINAL_RECORD']==origprops[k],'raw_property_conservation',k)
  ts=r['CANONICAL_TARGET_PROPERTY_IDS'];c.require(bool(ts) and len(ts)==len(set(ts)) and set(ts)<=set(pp),'property_mapping',k)
  c.require(bool(r['RECONCILIATION_RELATION_TYPES']) and set(r['RECONCILIATION_RELATION_TYPES'])<=set(recon['relation_vocabulary']),'relation_vocabulary',k)
  c.require(bool(r['MERGE_SPLIT_RATIONALE']) and bool(r['SEMANTIC_COMPARISON']['CANONICAL_FACET_DECISIONS']),'semantic_adjudication',k)
  for t in ts:c.require(k in pp[t]['INPUT_PROPERTY_KEYS'],'property_mapping_bidirectional',k+'->'+t)
  for sid in set(re.findall(r'ESME-S\d{3}',json.dumps(origprops[k]))):c.require(k[:2]+sid in origsources,'original_source_reference',k+':'+sid)
  if k.startswith('B:'):
   supplement=r['FROZEN_INTAKE_SUPPLEMENT'];c.require(supplement['HEADER'] in originals['B']['SYNTHESIS_TEXT'],'input_intake_conservation',k+' header')
   for name,val in supplement['FIELDS'].items():c.require(f'**{name}.** {val}' in originals['B']['SYNTHESIS_TEXT'],'input_intake_conservation',k+':'+name)
 for k,r in srr.items():
  c.require(r['FROZEN_ORIGINAL_RECORD']==origsources[k],'raw_source_conservation',k)
  ts=r['CANONICAL_SOURCE_IDS'];c.require(bool(ts) and len(ts)==len(set(ts)) and set(ts)<=set(ss),'source_mapping',k)
  for t in ts:c.require(k in ss[t]['INPUT_SOURCE_KEYS'],'source_mapping_bidirectional',k+'->'+t)
  c.require(not r['ACCESS_UPGRADE_APPLIED'],'source_access_boundary',k)
 for k,p in pp.items():
  c.require(p['INPUT_PROPERTY_KEYS'] and set(p['INPUT_PROPERTY_KEYS'])<=set(rr),'canonical_ancestry',k)
  for source in p['INPUT_PROPERTY_KEYS']:c.require(k in rr[source]['CANONICAL_TARGET_PROPERTY_IDS'],'property_mapping_bidirectional',k+'<-'+source)
  c.require(set(p['CONTRIBUTING_PACKET_A_PROPERTY_IDS']+p['CONTRIBUTING_PACKET_B_PROPERTY_IDS'])==set(p['INPUT_PROPERTY_KEYS']),'canonical_ancestry',k+' qualified sides')
  for f in ['CANONICAL_GLOBAL_KEY','CANONICAL_NAME','LINEAGE_ID','CANONICAL_ORIGIN_CLASS','HISTORICAL_ORIGIN','ORIGINAL_FORM','PROBLEM_ADDRESSED','FAILURE_MODE','MECHANISM','TRIGGER_CONTEXT','NON_TRIGGER_CHEAP_PATH','DEPENDENCIES_PRECONDITIONS','DOMAIN_PROFILE','EXPECTED_PAYOFF','DECISION_CONSUMER','ACTOR_AUTHORITY_BOUNDARY','COMMUNICATION_INTERACTION_REQUIREMENT','OBSERVABLE_POSTCONDITION','KNOWN_FAILURE_MODES','CRITICISMS','EVOLVED_FORM','CEREMONY_PROPERTY_JUDGEMENT','CANONICAL_DISPOSITION','EVIDENCE_STRENGTH_PARTITION','CANONICAL_SOURCE_IDS','CONTRARY_EVIDENCE','ASSUMPTION_SENSITIVITY','DUPLICATE_SUPERSESSION_LINKS','OPEN_QUESTIONS','EXAMINATION_STATUS','OMISSION_RETIREMENT_CONDITIONS','NEUTRAL_LATER_CROSSWALK_QUESTIONS','RECONCILIATION_RATIONALE']:
   c.require(f in p and p[f] is not None,'property_schema',k+':'+f)
  c.require(p['REQUIRED_INPUTS']==p['DEPENDENCIES_PRECONDITIONS'],'canonical_alias_consistency',k)
  c.require(p['CRITERION']==p['OBSERVABLE_POSTCONDITION'] and p['MECHANISM']==p['OPERATING_MECHANISM'],'canonical_alias_consistency',k)
  c.require(bool(p['CANONICAL_SOURCE_IDS']) and set(p['CANONICAL_SOURCE_IDS'])<=set(ss),'canonical_source_reference',k)
  for fid,valid in [('COMPOSITION_RELATION_IDS',rel),('CRITICISM_IDS',crit),('TENSION_IDS',ten),('CASE_IDS',cases),('CEREMONY_IDS',cer)]:c.require(set(p[fid])<=set(valid),'property_auxiliary_reference',k+':'+fid)
  c.require(len(p['INPUT_FIELD_VARIANTS'])==len(p['INPUT_PROPERTY_KEYS']),'field_variants',k)
  for v in p['INPUT_FIELD_VARIANTS']:
   original=origprops[v['INPUT_PROPERTY_KEY']]
   c.require(all(original.get(f)==x for f,x in v['FIELDS'].items()),'field_variant_conservation',k+':'+v['INPUT_PROPERTY_KEY'])
 for k,s in ss.items():
  c.require(s['INPUT_SOURCE_KEYS'] and set(s['INPUT_SOURCE_KEYS'])<=set(srr),'canonical_source_ancestry',k)
  for i in s['INPUT_SOURCE_KEYS']:c.require(k in srr[i]['CANONICAL_SOURCE_IDS'],'source_mapping_bidirectional',k+'<-'+i)
  for a in s['ACCESS_RECORDS']:
   o=origsources[a['INPUT_SOURCE_KEY']]
   c.require(a['ORIGINAL_ACCESS_LEVEL']==o['ACCESS_LEVEL'] and a['CLAIM_LOCATORS']==o['CLAIM_LOCATORS'],'source_access_conservation',k)
   c.require(not a['ACCESS_REPERFORMED_IN_RECONCILIATION'],'source_access_boundary',k)
 c.require({n['CANONICAL_PROPERTY_ID'] for n in co['nodes']}==set(pp),'composition_nodes','exact property set')
 for k,r in rel.items():
  c.require(bool(r['FROM_CANONICAL_PROPERTY_IDS']) and bool(r['TO_CANONICAL_PROPERTY_IDS']),'composition_reference',k+' endpoints')
  for t in r['FROM_CANONICAL_PROPERTY_IDS']+r['TO_CANONICAL_PROPERTY_IDS']:
   c.require(t in pp and k in pp[t]['COMPOSITION_RELATION_IDS'],'composition_reference',k+'->'+t)
  for f in ['RELATION_TYPE','CONTEXT_GUARD','COMPOSITION_MECHANISM','NEW_FAILURE_OR_COST','OMISSION_OR_CHEAPER_PATH','EVIDENCE_STATUS']:c.require(bool(r[f]),'composition_schema',k+':'+f)
 c.require(co['serial_pipeline_required'] is False,'composition_boundary','not serial')
 for x in co['composition_induced_properties']:
  k=x['CANONICAL_PROPERTY_ID'];c.require(pp[k]['CLASSIFICATION']['COMPOSITION_INDUCED'],'induced_derivation',k)
  for f in ['CANONICAL_PARENT_PROPERTY_IDS','CANONICAL_RELATION_IDS','COMPOSITION_SPECIFIC_FAILURE_WITNESS','INHERITED_PROPERTY_AND_GUARD_TEST','REQUIRED_OVERLAP_ADJUDICATION','CHEAPER_DISCHARGE']:c.require(bool(x[f]),'induced_derivation',k+':'+f)
  c.require(set(x['CANONICAL_PARENT_PROPERTY_IDS'])<=set(pp) and set(x['CANONICAL_RELATION_IDS'])<=set(rel),'induced_derivation_references',k)
 c.require({r['INPUT_PROPERTY_KEY'] for r in co['all_input_induced_derivation_accounts']}=={f'A:ESME-{i:03d}' for i in range(93,99)}|{f'B:ESME-{i:03d}' for i in range(72,75)},'induced_input_coverage','all nine')
 # Every criticism/tension/case/ceremony and original graph/configuration row is conserved.
 for kind,key,canonkind in [('criticism_ledger','CRITICISM_ID','criticism_ledger'),('internal_tensions','TENSION_ID','internal_tensions'),('ceremony_stripping_ledger','CEREMONY_ID','ceremony_stripping_ledger'),('cases','CASE_ID','case_tests')]:
  expected={}
  for lab,o in originals.items():
   container=o['COMPOSITION_MODEL'] if lab=='A' else o['PROPERTY_LEDGER']
   orig=(o['COMPOSITION_MODEL']['analytical_case_tests' if lab=='A' else 'case_tests'] if kind=='cases' else container[kind])
   expected.update({f'{lab}:{r[key]}':r for r in orig})
  seen=set()
  for x in aux[canonkind]:
   for entry in x['INPUT_RECORDS']:
    k=entry['INPUT_KEY'];c.require(k in expected and entry['FROZEN_ORIGINAL_RECORD']==expected[k],'raw_ancillary_conservation',kind+':'+k);seen.add(k)
  c.require(seen==set(expected),'ancillary_coverage',kind)
  if kind!='cases':
   mapname={'criticism_ledger':'criticism_reconciliation','internal_tensions':'tension_reconciliation','ceremony_stripping_ledger':'ceremony_reconciliation'}[kind]
  else:mapname='case_reconciliation'
  c.require({x['INPUT_KEY'] for x in aux[mapname]}==seen,'ancillary_mapping_coverage',kind)
 for origkind,ledgerkey,idkey in [('relations','relation_reconciliation','RELATION_ID'),('alternative_configurations','configuration_reconciliation','CONFIGURATION_ID')]:
  expected={f'{lab}:{x[idkey]}':x for lab,o in originals.items() for x in o['COMPOSITION_MODEL'][origkind]}
  field='INPUT_RELATION_KEY' if origkind=='relations' else 'INPUT_CONFIGURATION_KEY'
  c.require({x[field] for x in aux[ledgerkey]}==set(expected),'ancillary_coverage',origkind)
  for x in aux[ledgerkey]:c.require(x['FROZEN_ORIGINAL_RECORD']==expected[x[field]],'raw_ancillary_conservation',x[field])
  if origkind=='relations':
   c.require(sum(bool(x['CANONICAL_RELATION_IDS']) for x in aux[ledgerkey])==113,'relation_reconciliation','113 mapped, one absorbed')
   for x in aux[ledgerkey]:c.require(bool(x['CANONICAL_RELATION_IDS']) or (x['INPUT_RELATION_KEY']=='B:ESME-R024' and bool(x['REASON'])),'relation_reconciliation',x['INPUT_RELATION_KEY'])
 expectedopen={f'{lab}:{x.get("ID",x.get("OBLIGATION_ID"))}':x for lab,o in originals.items() for x in o['COMPOSITION_MODEL']['unresolved_composition_obligations']}
 seen=set()
 for x in co['unresolved_composition_obligations']:
  for v in x['INPUT_RECORDS']:
   c.require(v['FROZEN_ORIGINAL_RECORD']==expectedopen[v['INPUT_KEY']],'raw_open_conservation',v['INPUT_KEY']);seen.add(v['INPUT_KEY'])
 c.require(seen==set(expectedopen),'open_question_coverage','seven inputs')
 gnexpected={};geexpected={}
 for lab,o in originals.items():
  h=o['COMPOSITION_MODEL'] if lab=='A' else o['PROPERTY_LEDGER']
  gnexpected.update({f'{lab}:{x["NODE_ID"]}':x for x in h['genealogy_nodes']});geexpected.update({f'{lab}:{x["EDGE_ID"]}':x for x in h['genealogy_edges']})
 seen=set()
 for x in gen['canonical_genealogy_nodes']:
  for i in x['INPUT_NODES']:c.require(i['FROZEN_ORIGINAL_RECORD']==gnexpected[i['INPUT_NODE_KEY']],'genealogy_conservation',i['INPUT_NODE_KEY']);seen.add(i['INPUT_NODE_KEY'])
 c.require(seen==set(gnexpected),'genealogy_coverage','29 nodes')
 c.require({x['INPUT_EDGE_KEY'] for x in gen['genealogy_edge_evidence_adjudications']}==set(geexpected),'genealogy_coverage','40 edges')
 for x in gen['genealogy_edge_evidence_adjudications']:c.require(x['FROZEN_ORIGINAL_RECORD']==geexpected[x['INPUT_EDGE_KEY']],'genealogy_conservation',x['INPUT_EDGE_KEY'])
 # All typed canonical references, including those in exported JSON, resolve.
 valid={'ESME-C':set(pp),'ESME-CS':set(ss),'ESME-CR':set(rel),'ESME-CC':set(crit),'ESME-CT':set(ten),'ESME-CASE':set(cases),'ESME-CER':set(cer),'ESME-CFG':set(cfg),'ESME-CU':set(openqs),'ESME-CG':{n['CANONICAL_GENEALOGY_NODE_ID'] for n in gen['canonical_genealogy_nodes']}}
 pattern=re.compile(r'\b(ESME-(?:CASE|CER|CFG|CS|CR|CC|CT|CU|CG|C))(\d{3})\b')
 def walk(o,path=''):
  if isinstance(o,str):
   for m in pattern.finditer(o):c.require(m.group(0) in valid[m.group(1)],'typed_reference_resolution',path+':'+m.group(0))
  elif isinstance(o,list):
   for i,v in enumerate(o):walk(v,path+f'/{i}')
  elif isinstance(o,dict):
   for k,v in o.items():
    if k in ['FROZEN_ORIGINAL_RECORD','FROZEN_INTAKE_SUPPLEMENT','INPUT_FIELD_VARIANTS','INPUT_INTAKE_SUPPLEMENTS','SEMANTIC_FIELD_COMPARISON','original_family_partitions','original_evolution_under_criticism_A','input_external_context_nodes_A']:continue
    walk(v,path+'/'+k)
 for n,o in parsed.items():walk(o,n)
 # Counts, families and whole-denominator exports.
 dc=dict(Counter(p['CANONICAL_DISPOSITION'] for p in props));ec=dict(Counter(p['EXAMINATION_STATUS'] for p in props));lc=dict(Counter(t for p in props for t in p['EXAMINATION_LIMIT_CATEGORIES']))
 c.require(dc==pl['disposition_counts']==cv['disposition_counts']==man['disposition_counts'],'count_consistency','dispositions')
 c.require(ec==pl['examination_counts']==cv['examination_counts']==man['examination_counts'],'count_consistency','examination')
 c.require(lc==pl['evidence_limit_category_counts']==man['evidence_limit_category_counts'],'count_consistency','evidence limit categories')
 c.require(len(props)==pl['canonical_property_population']==recon['canonical_property_population']==man['canonical_property_population_total']==man['canonical_property_population_examined'],'count_consistency','properties')
 c.require(len(sources)==sl['canonical_source_population']==sr['canonical_source_population']==man['canonical_source_population_total'],'count_consistency','sources')
 c.require(len(rel)==co['counts']['relations']==man['composition_relation_count'],'count_consistency','relations')
 c.require(len(cfg)==co['counts']['alternative_configurations']==man['alternative_configuration_count'],'count_consistency','configurations')
 c.require(len(co['composition_induced_properties'])==man['composition_induced_property_count'],'count_consistency','induced')
 c.require(sum(p['CONDITIONALLY_CROSSWALK_WORTHY'] for p in props)==pl['conditionally_crosswalk_worthy_count']==man['conditionally_crosswalk_worthy_count'],'count_consistency','eligibility')
 for value,mfield,cofield in [(len(crit),'criticism_count','criticisms'),(len(ten),'internal_tension_count','tensions'),(len(cases),'case_test_count','case_tests')]:c.require(value==man[mfield]==co['counts'][cofield]==cv['canonical_counts'][cofield],'count_consistency',mfield)
 c.require(len(cer)==man['ceremony_group_count']==cv['canonical_counts']['ceremony_groups'],'count_consistency','ceremony groups')
 c.require(len(openqs)==man['unresolved_composition_question_count']==cv['canonical_counts']['open_composition_questions'],'count_consistency','open composition')
 c.require(dc.get('UNRESOLVED',0)==man['unresolved_primary_disposition_count'] and dc.get('CONTESTED',0)==man['contested_primary_disposition_count'],'count_consistency','unsettled primary')
 c.require(set(ec)<={'EXAMINED','EXAMINED_WITH_EVIDENCE_LIMIT'} and sum(ec.values())==len(pp),'examination_complete','all canonical records')
 c.require(all(not p['CLASSIFICATION']['RECONCILIATION_INDUCED_COMPOSITION_PROPERTY'] for p in props),'induced_origin','none invented without ancestry')
 c.require({f['FAMILY_ID'] for f in cv['families']}=={f'M{i}' for i in range(1,11)},'mandatory_family_coverage','ten semantic families')
 c.require(cv['mandatory_families_uncompleted']==0,'mandatory_family_coverage','zero incomplete')
 for f in cv['families']:
  c.require(f['STATUS']=='EXAMINED_RECONCILED' and bool(f['CANONICAL_PROPERTY_IDS']),'mandatory_family_coverage',f['FAMILY_ID'])
  c.require(set(f['CANONICAL_PROPERTY_IDS'])=={p['CANONICAL_PROPERTY_ID'] for p in props if f['FAMILY_ID'] in p['FAMILY_IDS']},'family_membership',f['FAMILY_ID'])
  c.require(bool(f['CRITICISM_IDS']),'family_critical_coverage',f['FAMILY_ID'])
 sp=keyed(syn['properties'],'canonical_property_id','synthesis entries');c.require(set(sp)==set(pp) and not syn['active_only_filter_applied'],'synthesis_coverage','all dispositions exported')
 for k,e in sp.items():
  p=pp[k]
  for a,b in [('canonical_global_key','CANONICAL_GLOBAL_KEY'),('disposition','CANONICAL_DISPOSITION'),('examination_status','EXAMINATION_STATUS'),('conditionally_crosswalk_worthy','CONDITIONALLY_CROSSWALK_WORTHY'),('subject_bearer','SUBJECT_BEARER'),('criterion','CRITERION'),('operating_mechanism','MECHANISM'),('trigger','TRIGGER_CONTEXT'),('non_trigger_cheap_path','NON_TRIGGER_CHEAP_PATH'),('required_inputs','REQUIRED_INPUTS'),('source_ids','CANONICAL_SOURCE_IDS'),('ancestry','INPUT_PROPERTY_KEYS'),('reconciliation_status','RECONCILIATION_STATUS'),('retirement_omission_condition','OMISSION_RETIREMENT_CONDITIONS')]:c.require(e[a]==p[b],'synthesis_field_parity',k+':'+a)
  for f in ['consumer','authority','assumptions','costs_failure_modes','conflicts','composition_relations','evidence_boundary','reconciliation_rationale']:c.require(f in e and e[f] is not None,'synthesis_schema',k+':'+f)
 for suffix in ['CANONICAL_AUDIT_INTAKE.md','CANONICAL_SYNTHESIS_INTAKE.md']:
  txt=members[P+'_'+suffix].decode('utf8');ids=re.findall(r'^## (ESME-C\d{3}) —',txt,re.M)
  c.require(len(ids)==len(set(ids)) and set(ids)==set(pp),'markdown_intake_coverage',suffix)
  for k,p in pp.items():c.require(f'## {k} — {p["CANONICAL_NAME"]}' in txt and p['CANONICAL_DISPOSITION'] in txt,'markdown_intake_identity',k)
 report=members[P+'_CANONICAL_FROZEN_REPORT.md'].decode('utf8')
 for ch in 'ABCDEFGHIJK':c.require(f'## {ch}.' in report,'report_sections',ch)
 for k,p in pp.items():c.require(f'| {k} |' in report and p['CANONICAL_NAME'] in report,'report_census',k)
 for k in ss:c.require(f'| {k} |' in report,'report_bibliography',k)
 c.require(all(v is False for v in co['external_boundary'].values()),'scope_boundary','all prohibited activities false')
 c.require(cv['external_research']['count']==sl['fresh_external_verification_count']==0,'scope_boundary','no external study silently introduced')
 c.require(not sl['original_access_reperformed'],'scope_boundary','no original-access upgrade')
 c.require(set(n for n in members if n.startswith('inputs/'))=={'inputs/PACKET_A.zip','inputs/PACKET_B.zip','inputs/CONTROLLING_RECONCILIATION_PROMPT.md'},'input_scope','only authorised inputs')
 # Known semantic decisions are asserted independently of generated prose.
 expectedmap={'A:ESME-093':['ESME-C102'],'A:ESME-094':['ESME-C103'],'A:ESME-095':['ESME-C049'],'A:ESME-096':['ESME-C058'],'A:ESME-097':['ESME-C105'],'A:ESME-098':['ESME-C098'],'B:ESME-072':['ESME-C102','ESME-C103'],'B:ESME-073':['ESME-C104'],'B:ESME-074':['ESME-C105']}
 for k,ts in expectedmap.items():c.require(rr[k]['CANONICAL_TARGET_PROPERTY_IDS']==ts,'required_overlap_adjudication',k)
 c.require(rr['A:ESME-017']['CANONICAL_TARGET_PROPERTY_IDS']==['ESME-C018'] and pp['ESME-C018']['CANONICAL_DISPOSITION']=='STRONGLY_RETAINED','polarity_preservation','recovery distinction')
 c.require(rr['A:ESME-087']['CANONICAL_TARGET_PROPERTY_IDS']==['ESME-C094'] and rr['B:ESME-070']['CANONICAL_TARGET_PROPERTY_IDS']==['ESME-C037'],'duplicate_adjudication','authority and characterisation')
 c.require(pp['ESME-C095']['CANONICAL_DISPOSITION']=='UNRESOLVED' and pp['ESME-C100']['CANONICAL_DISPOSITION']=='UNRESOLVED' and pp['ESME-C082']['CANONICAL_DISPOSITION']=='CONTESTED','unsettled_findings','not erased')
 c.require(len({i for r in rows for i in r['CANONICAL_TARGET_PROPERTY_IDS']})==len(pp),'orphan_canonical_rows','none')
 c.require(sum(len(r['CANONICAL_TARGET_PROPERTY_IDS']) for r in rows)==180,'denominator_bridge','180 edges')
 c.require(sum(len(r['CANONICAL_SOURCE_IDS']) for r in srows)==135,'source_denominator_bridge','135 resource edges')
 return {'revision':man['revision'],'canonical_properties':len(pp),'canonical_sources':len(ss),'input_property_rows':{'A':'98/98','B':'74/74','TOTAL':'172/172'},'input_source_rows':{'A':'67/67','B':'67/67','TOTAL':'134/134'},'orphan_input_rows':0,'orphan_input_source_rows':0,'disposition_counts':dc,'examination_counts':ec,'evidence_limit_category_counts':lc,'composition_relations':len(rel),'alternative_configurations':len(cfg),'composition_induced_properties':len(co['composition_induced_properties']),'criticisms':len(crit),'internal_tensions':len(ten),'cases':len(cases),'ceremonies':len(cer),'open_composition_questions':len(openqs),'mandatory_families':10,'uncompleted_mandatory_families':0,'manifested_payload_count':len(inventory),'archive_member_count':len(members),'json_payload_count':len(parsed),'scope_boundary':'NO_SIBLING_OR_TARGET_WORK','original_raw_records_preserved':True,'fresh_original_source_access_performed':False,'scholarly_truth_certified':False}

def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('target',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args();c=Checks()
 try:
  members,metadata=load_target(args.target,c);result=verify_members(members,c)
  receipt={'verification_status':'PASS','checks_passed':c.count,'checks_failed':0,'check_categories':dict(c.categories),**metadata,**result,'verification_limit':'Custody, exact record preservation and structural consistency only; no independent scholarly or empirical validation.'}
  out=json.dumps(receipt,ensure_ascii=False,indent=2)+'\n'
  if args.output:args.output.write_text(out,encoding='utf8')
  print(out,end='');return 0
 except (VerificationError,KeyError,ValueError,TypeError,OSError,zipfile.BadZipFile) as e:
  out=json.dumps({'verification_status':'FAIL','checks_attempted':c.count,'error':str(e)},indent=2)+'\n'
  if args.output:args.output.write_text(out,encoding='utf8')
  print(out,end='');return 1
if __name__=='__main__':sys.exit(main())
