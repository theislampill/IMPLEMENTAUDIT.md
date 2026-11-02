#!/usr/bin/env python3
"""Read-only DG31 record reconstruction checks; no acceptance or closure authority."""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path

# Configured by verify_delivery.py; imports have no filesystem effects.
ROOT = Path('.')
INPUT = ROOT / 'input'
OUT = Path('.')
PKG = 'evidence/original-certification-resumption-20261031/pro-package/'
CARRIER = PKG + 'evidence/lanes/closure_challenge/library_recovery/original_package/acceptance/ebpm-ewm-bwp-full-records.json'
PROJECTION = 'public-projection/r003f-r0041-preparation-recovery.json'
PRIVATE_ROOT = None  # Resolved from the unchanged private evidence path map.

def load(path):
    return json.loads((INPUT / path).read_text(encoding='utf-8'))

def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sha(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items() if not k.startswith('__published_identity_')}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    if isinstance(obj, str):
        slash = obj.replace('\\', '/')
        if PRIVATE_ROOT and PRIVATE_ROOT in slash:
            return slash.replace(PRIVATE_ROOT, 'historical-private-run/')
    return obj

def difference(a, b, pointer=''):
    if type(a) is not type(b):
        return [pointer + ':type']
    if isinstance(a, dict):
        diff = [pointer + '/' + k + ':missing' for k in sorted(a.keys() - b.keys())]
        diff += [pointer + '/' + k + ':extra' for k in sorted(b.keys() - a.keys())]
        for k in sorted(a.keys() & b.keys()):
            diff += difference(a[k], b[k], pointer + '/' + k)
        return diff
    if isinstance(a, list):
        diff = [pointer + ':length'] if len(a) != len(b) else []
        for i, (av, bv) in enumerate(zip(a,b)):
            diff += difference(av,bv,pointer+'/'+str(i))
        return diff
    return [] if a == b else [pointer + ':value']

def pointer(obj, path):
    if path == '': return obj
    assert path.startswith('/'), path
    for p in path[1:].split('/'):
        p = p.replace('~1','/').replace('~0','~')
        obj = obj[int(p)] if isinstance(obj,list) else obj[p]
    return obj

def count(values):
    return dict(sorted(collections.Counter(values).items()))

def main():
    p = load('private-primary/PROPERTY_CONTINUATION_LEDGER.json')
    g = load('private-primary/GROUP_CONTINUATION_LEDGER.json')
    q = load(PROJECTION)
    c = load(CARRIER)
    failures = []
    checks = []
    def check(name, ok, detail=None):
        checks.append({'check':name, 'pass': bool(ok), **({'detail':detail} if detail is not None else {})})
        if not ok: failures.append(name)
    identities = load('private-primary/IDENTITIES.json')
    for item in identities['raw_private'] + [identities['original_full_records'],identities['normalized_public']]:
        data=(INPUT/item['path']).read_bytes()
        check('byte_identity:'+item['path'],len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'])

    props={r['key']:r for r in p['properties']}
    groups={r['group_id']:r for r in g['groups']}
    check('property_unique_234',len(props)==len(p['properties'])==234)
    check('property_lineage_denominators',count(k.split(':')[0] for k in props)=={'EBPM':73,'EPM':84,'EWM':77})
    check('group_unique_41',len(groups)==len(g['groups'])==41)
    check('group_exact_ids',list(groups)==[f'BWP-K{i:03}' for i in range(1,42)])
    check('projection_property_identity_order',[r['key'] for r in q['properties']]==list(props))
    check('projection_group_identity_order',[r['group_id'] for r in q['groups']]==list(groups))
    memberships=[(gr['group_id'],key) for gr in g['groups'] for key in gr['member_original_property_identities']]
    reverse=[(gid,r['key']) for r in p['properties'] for gid in r['group_ids']]
    check('membership_exact_608_unique_pairs',len(memberships)==len(set(memberships))==608)
    check('membership_reciprocity',set(memberships)==set(reverse) and len(reverse)==608)
    check('all_members_have_group',set(key for gid,key in memberships)==set(props))
    check('carrier_group_map_exact',c['group_membership_map']=={k:v['member_original_property_identities'] for k,v in groups.items()})
    check('carrier_groups_exact',[r['group_id'] for r in c['full_group_current_receiving']]==list(groups))
    for gr in g['groups']:
        gs={key:props[key]['absorption_state'] for key in gr['member_original_property_identities']}
        check('group_member_states:'+gr['group_id'],gs==gr['member_absorption_states'])
        check('group_state_counts:'+gr['group_id'],count(gs.values())==gr['member_absorption_counts'])

    recon_differences={}
    contexts={}
    occurrences=[]
    for i,(raw,projected) in enumerate(zip(p['properties'],q['properties'])):
        reconstructed=normalize(copy.deepcopy(projected))
        for field in ['full_original_record','full_bwp_source_record','full_corrected_target_disposition']:
            binding = reconstructed.pop(field+'_binding')
            check('duplicate_binding:'+raw['key']+':'+field,sha(raw[field])==binding['canonical_record_sha256'])
            reconstructed[field]=normalize(raw[field])
        qual=raw['first_missing_discriminator']['receiving_qualification']
        refs=reconstructed['first_missing_discriminator']['receiving_qualification']
        check('qual_count:'+raw['key'],len(qual)==len(refs))
        expanded=[]
        for j,(ctx,ref) in enumerate(zip(qual,refs)):
            original_hash=sha(ctx)
            contexts[original_hash]=ctx
            actual=pointer(q,ref['context_pointer'])
            check('qual_pointer:'+raw['key']+':'+str(j),ref['context_sha256']==original_hash and normalize(ctx)==normalize(actual))
            expanded.append(normalize(actual))
            occurrences.append({'property_key':raw['key'],'property_pointer':f'/properties/{i}','occurrence_index':j,'original_occurrence_pointer':f'/properties/{i}/first_missing_discriminator/receiving_qualification/{j}','context_sha256':original_hash,'context_pointer':f'/qualification_contexts/{original_hash}/content'})
        reconstructed['first_missing_discriminator']['receiving_qualification']=expanded
        diff=difference(normalize(raw),reconstructed)
        if diff: recon_differences[raw['key']]=diff
    relation_occurrences=0
    for raw,projected in zip(g['groups'],q['groups']):
        reconstructed=normalize(copy.deepcopy(projected))
        binding=reconstructed.pop('full_original_group_record_binding')
        check('group_duplicate_binding:'+raw['group_id'],sha(raw['full_original_group_record'])==binding['canonical_record_sha256'])
        reconstructed['full_original_group_record']=normalize(raw['full_original_group_record'])
        relations=reconstructed['material_relations']
        ids=relations.pop('record_ids')
        relations.pop('reconstruction_rule')
        relations.pop('every_original_pointer_checked')
        relations['records']=[{'id':rid,'pointer':'/relations/'+str(int(rid.split('R')[-1])-1)} for rid in ids]
        relation_occurrences+=len(ids)
        diff=difference(normalize(raw),reconstructed)
        if diff: recon_differences[raw['group_id']]=diff
    check('all_primary_fields_reconstructed_after_declared_normalization',not recon_differences,recon_differences)
    check('context_31_unique',len(contexts)==len(q['qualification_contexts'])==31)
    check('context_353_occurrences',len(occurrences)==len(q['qualification_occurrences'])==353)
    check('context_occurrence_table_exact',occurrences==q['qualification_occurrences'])
    for digest,ctx in contexts.items():
        item=q['qualification_contexts'][digest]
        check('context_digest:'+digest,item['original_context_sha256']==digest and sha(item['content'])==item['public_projection_sha256'])
        check('context_twenty_fields:'+digest,len(ctx)==len(item['content'])==20)
        check('context_no_behavior_credit:'+digest,ctx['behavior_pass_from_this_join'] is False and item['content']['behavior_pass_from_this_join'] is False)
    check('carrier_context_dictionary_exact',c['original_qualification_context_full_records']==q['qualification_contexts'])
    check('carrier_context_ids_exact',c['original_qualification_context_ids']==sorted(contexts))
    for sc, prefix in [('R003F','EBPM'),('R0041','EWM'),('R003F::BWP-LANE-CONTINUATION',None)]:
        members=c['scopes'][sc]['members']
        expected=[r['key'] for r in p['properties'] if not prefix or r['key'].startswith(prefix+':')]
        check('carrier_population:'+sc,[r['key'] for r in members]==expected)
        for row in members:
            raw=props[row['key']]
            check('carrier_source_state:'+sc+':'+row['key'],row['original_status']==raw['full_original_record']['CURRENT_STATUS'])
            check('carrier_preparation_state:'+sc+':'+row['key'],row['prepared_state']==raw['absorption_state'])
            fields={'group_ids':'group_ids','current_product_carriers':'current_product_carriers','absorbed_portion':'absorbed_portion','residual':'residual','first_missing_discriminator':'first_missing_discriminator','reconsideration_trigger':'reconsideration_trigger','lawful_next_action':'plausible_next_action','version_horizon':'version_horizon'}
            for target,source in fields.items():
                # Carrier intentionally retains normalized public context references.
                qrow=q['properties'][list(props).index(row['key'])]
                check('carrier_field:'+sc+':'+row['key']+':'+target,normalize(row[target])==normalize(qrow[source]))
    actual_member=load(PKG+'evidence/lanes/workflow_process/CURRENT_MEMBER_DISPOSITIONS.json')
    actual_bwp=load(PKG+'evidence/lanes/workflow_process/CURRENT_BWP_RESIDUALS.json')
    for family,payload,rowskey in [('EBPM',actual_member,'rows'),('BWP',actual_bwp,'members')]:
        receipt=load(PKG+'evidence/root_receiving/'+family+'_ROOT_CURRENT_RECEIVING.json')
        payload_pin=receipt['accepted_full_payload']
        payload_bytes=(INPUT/PKG/payload_pin['path']).read_bytes()
        check('root_receipt_payload:'+family,len(payload_bytes)==payload_pin['bytes'] and hashlib.sha256(payload_bytes).hexdigest()==payload_pin['sha256'])
        rows={r['key']:r for r in payload[rowskey]}
        expected_keys={k for k in props if k.startswith('EBPM:')} if family=='EBPM' else set(props)
        check('root_receipt_member_keys:'+family,{r['key'] for r in receipt['accepted_members']}==expected_keys)
        for r in receipt['accepted_members']:
            check('root_receipt_member_record:'+family+':'+r['key'],sha(rows[r['key']])==r['full_record_sha256'])
        if family=='BWP':
            actual_groups={r['group_id']:r for r in payload['groups']}
            for r in receipt['accepted_groups']:
                check('root_receipt_group_record:'+r['group_id'],sha(actual_groups[r['group_id']])==r['full_record_sha256'])
            for r in payload['members']:
                source=q['properties'][list(props).index(r['key'])]
                check('actual_bwp_member_projection_fields:'+r['key'],all(normalize(v)==normalize(source[k]) for k,v in r.items()))
            for r in payload['groups']:
                source=q['groups'][list(groups).index(r['group_id'])]
                check('actual_bwp_group_projection_fields:'+r['group_id'],all(normalize(v)==normalize(source[k]) for k,v in r.items()))

    # Same file name at different cuts can mean different bytes; references stay qualified.
    sources=[]
    locator=q['source_locator_resolution']
    for role,obj in [('bwp_packet',locator['bwp_packet']), *[(f'lineage_{k}',v) for k,v in locator['original_lineage_ledgers'].items()],('historical_target',locator['corrected_historical_target']),('historical_explicit_bridges',locator['corrected_historical_explicit_bridges'])]:
        sources.append({'role':role,**obj})
    source_receipts=load(PKG+'SOURCE_REFERENCES.json')['unchanged_selected_receiving_sources']
    for obj in source_receipts:
        sources.append({'role':'retained_receiving_source','commit':'4af2e43b4047cd577aa6b56eecd5b27c5f0e45e0','path':obj['path'],'bytes':obj['bytes'],'sha256':obj['sha256'],'historical_url':obj['immutable_public_url']})
    # Additional composition models are historical lineage content referred by every group.
    tree=json.loads((ROOT/'public-tree.json').read_text())
    models=sorted({path for gr in g['groups'] for rec in gr['within_lineage_composition_reacquisition'] for path in rec['models']})
    tree_paths={x['path']:x for x in tree['tree']}
    for path in models:
        matches=[t for t in tree_paths if t.endswith('/'+path.rsplit('/',1)[-1]) and '/corpus/' in t]
        sources.append({'role':'within_lineage_composition','historical_locator':path,'checkpoint_candidates':[{'path':m,'git_blob':tree_paths[m]['sha'],'bytes':tree_paths[m].get('size')} for m in matches]})

    summary={
        'authority':'NONE; documentary verification only, no acceptance or closure',
        'input_root':str(INPUT),
        'total_checks':len(checks),'failed_checks':failures,
        'population':{'EBPM':73,'EWM_bridge':77,'EPM_bridge':84,'BWP_distinct':234,'groups':41,'memberships':608,'repeated_memberships':374},
        'source_status_counts_by_lineage':{lin:count(r['full_original_record']['CURRENT_STATUS'] for r in p['properties'] if r['key'].startswith(lin+':')) for lin in ['EBPM','EWM','EPM']},
        'preparation_counts_by_lineage':{lin:count(r['absorption_state'] for r in p['properties'] if r['key'].startswith(lin+':')) for lin in ['EBPM','EWM','EPM']},
        'preparation_counts_all':count(r['absorption_state'] for r in p['properties']),
        'target_disposition_counts':count(r['full_corrected_target_disposition']['disposition'] for r in p['properties']),
        'context_count':len(contexts),'context_occurrences':len(occurrences),'material_relation_occurrences':relation_occurrences,
        'unique_material_relation_ids':len({x['id'] for gr in g['groups'] for x in gr['material_relations']['records']}),
        'material_context_occurrences':sum(len(gr['material_contexts']) for gr in g['groups']),
        'explicit_bridge_occurrences':sum(len(gr['explicit_bridge_records']) for gr in g['groups']),
        'selected_guard_ids':c['selected_guard_ids'],
        'K031_state_counts':groups['BWP-K031']['member_absorption_counts'],
        'EBPM053':{'source_state':props['EBPM:EBPM-053']['full_original_record']['CURRENT_STATUS'],'preparation_state':props['EBPM:EBPM-053']['absorption_state'],'target_disposition':props['EBPM:EBPM-053']['full_corrected_target_disposition']['disposition'],'groups':props['EBPM:EBPM-053']['group_ids']},
        'schema_shapes':{
          'raw_property_top_keys':list(p),'raw_property_row_keys':list(p['properties'][0]),
          'raw_group_top_keys':list(g),'raw_group_row_keys':list(g['groups'][0]),
          'projection_top_keys':list(q),'carrier_top_keys':list(c),
        },
        'all_checks':checks,
    }
    (OUT/'record-verification.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (OUT/'required-public-sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['all_checks','schema_shapes']},indent=2))
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit('Run verify_delivery.py with the supplied delivery directory.')
