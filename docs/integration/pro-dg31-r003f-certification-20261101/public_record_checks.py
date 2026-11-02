#!/usr/bin/env python3
"""Check the supplied immutable DG31 proof bytes offline, without executing them."""
import collections
import io
import json
import hashlib
import zipfile
from pathlib import Path
from record_checks import INPUT, OUT, ROOT, PKG, CARRIER, PROJECTION, load, sha, normalize, pointer, canon

CURRENT='4af2e43b4047cd577aa6b56eecd5b27c5f0e45e0'
HIST='cacfe97da7656b472bf4f11e50c9d106a6c3f92a'
PREFIX='docs/research/implementaudit/'
CACHE=ROOT/'public-source'

def main():
    checks=[]; failures=[]; sources={}; decoded={}; archive_members={}
    def check(name,ok,detail=None):
        checks.append({'check':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
        if not ok: failures.append(name)
    def data_at(commit,path):
        key=(commit,path)
        if key not in sources:
            if len(commit) != 40 or any(ch not in '0123456789abcdef' for ch in commit):
                raise ValueError('invalid immutable source commit')
            pp = Path(path)
            if pp.is_absolute() or '..' in pp.parts or '\\' in path:
                raise ValueError('unsafe source path')
            dest = CACHE / commit / path
            if dest.is_symlink() or not dest.is_file():
                raise ValueError('required immutable source is absent or not regular: ' + path)
            raw = dest.read_bytes()
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            sources[key]={'commit':commit,'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':blob,'local_path':str(dest),'role':[]}
        return Path(sources[key]['local_path']).read_bytes()
    def public(commit,path,role='reconstruction_dependency'):
        key=(commit,path)
        raw=data_at(commit,path)
        if role not in sources[key]['role']:sources[key]['role'].append(role)
        if key not in decoded:decoded[key]=json.loads(raw)
        return decoded[key]
    def pin(obj,role):
        data=data_at(obj['commit'],obj['path']);key=(obj['commit'],obj['path'])
        if role not in sources[key]['role']:sources[key]['role'].append(role)
        check('pin:'+obj['commit']+':'+obj['path'],('bytes' not in obj or len(data)==obj['bytes']) and ('sha256' not in obj or hashlib.sha256(data).hexdigest()==obj['sha256']))
    q=load(PROJECTION);p=load('private-primary/PROPERTY_CONTINUATION_LEDGER.json');g=load('private-primary/GROUP_CONTINUATION_LEDGER.json');c=load(CARRIER)
    props={r['key']:r for r in p['properties']}
    def walk(v,path=''):
        if isinstance(v,dict):
            yield path,v
            for k,x in v.items():yield from walk(x,path+'/'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):yield from walk(x,path+'/'+str(i))
    unique_pins={}
    for ptr,obj in walk(q):
        if 'commit' in obj and 'path' in obj:
            key=(obj['commit'],obj['path'])
            if key not in unique_pins or len(obj)>len(unique_pins[key]):unique_pins[key]=obj
    for obj in unique_pins.values():pin(obj,'projection_immutable_reference')
    packet=q['source_locator_resolution']['bwp_packet']
    z=zipfile.ZipFile(io.BytesIO(data_at(packet['commit'],packet['path'])))
    names=collections.defaultdict(list)
    for name in z.namelist():names[Path(name).name].append(name)
    for name,item in q['source_locator_resolution']['bwp_archive_members'].items():
        check('bwp_member_unique:'+name,len(names[name])==1)
        raw=z.read(names[name][0]);archive_members[name]=json.loads(raw)
        check('bwp_member_pin:'+name,len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'])
    def bound_source(binding):
        ref=binding['public_source_record']
        obj=archive_members[ref['member']] if 'source_packet' in ref else public(ref['commit'],ref['path'])
        return pointer(obj,ref['pointer'])
    for raw,projection in zip(p['properties'],q['properties']):
        for field in ['full_original_record','full_bwp_source_record','full_corrected_target_disposition']:
            binding=projection[field+'_binding'];row=bound_source(binding)
            check('immutable_binding:'+raw['key']+':'+field,sha(row)==binding['canonical_record_sha256'] and row==raw[field])
            older=binding['published_a08_binding_record'];ref=pointer(public(older['commit'],older['path']),older['pointer'])
            # R0040's historical EPM schema uses canonical_sha256. The sibling
            # EBPM/EWM lineage schema uses canonical_record_sha256. Preserve both.
            hash_field='canonical_sha256' if older['path'].endswith('/r0040-member-dispositions.json') else 'canonical_record_sha256'
            check('a08_binding:'+raw['key']+':'+field,ref.get(hash_field)==binding['canonical_record_sha256'])
    for raw,projection in zip(g['groups'],q['groups']):
        binding=projection['full_original_group_record_binding'];row=bound_source(binding)
        check('immutable_group_binding:'+raw['group_id'],sha(row)==binding['canonical_record_sha256'] and row==raw['full_original_group_record'])
        older=binding['published_a08_binding_record'];ref=pointer(public(older['commit'],older['path']),older['pointer'])
        check('a08_group_binding:'+raw['group_id'],ref.get('canonical_record_sha256')==binding['canonical_record_sha256'])
    selected=load(PKG+'SOURCE_REFERENCES.json')['unchanged_selected_receiving_sources']
    for obj in selected:pin({'commit':CURRENT,**{k:obj[k] for k in ['path','bytes','sha256']}},'retained_selected18_receiving')
    # The carrier's original four source URLs are separate immutable aliases.
    for url in c['sources']:
        tail=url.split('/blob/',1)[1];commit,path=tail.split('/',1)
        old=data_at(commit,path);now=data_at(CURRENT,path)
        sources[(commit,path)]['role'].append('original_carrier_source')
        check('carrier_source_equals_checkpoint:'+path,old==now)
    lineage_meta=q['source_locator_resolution']['original_lineage_ledgers']
    lineage_models={}
    for lin,meta in lineage_meta.items():
        path=meta['path'].replace('_PROPERTY_LEDGER.json','_COMPOSITION_MODEL.json')
        lineage_models[lin]=public(HIST,path,'within_lineage_relation_closure')
    relations=archive_members['EVOLVED_BWP_DIRECTIONAL_RELATION_LEDGER.json']['relations']
    check('relation_7068',len(relations)==7068 and len({r['id'] for r in relations})==7068)
    check('relation_index_ID_order',all(r['id']==f'BWP-R{i+1:05}' for i,r in enumerate(relations)))
    bridges=public(HIST,q['source_locator_resolution']['corrected_historical_explicit_bridges']['path'])
    for group in g['groups']:
        for record in group['material_relations']['records']:
            row=pointer(archive_members['EVOLVED_BWP_DIRECTIONAL_RELATION_LEDGER.json'],record['pointer'])
            check('relation_pointer:'+group['group_id']+':'+record['id'],row['id']==record['id'])
        for record in group['material_contexts']:
            row=pointer(archive_members[Path(record['path']).name],record['pointer'])
            ident=row.get('id',row.get('candidate_id',row.get('case_id')))
            check('material_context_pointer:'+group['group_id']+':'+record['id'],ident==record['id'],None if ident==record['id'] else {'actual':ident})
        for record in group['explicit_bridge_records']:
            row=pointer(bridges,record['pointer'])
            check('explicit_bridge_pointer:'+group['group_id']+':'+record['id'],row.get('id',row.get('relation_id'))==record['id'])
        for record in group['within_lineage_composition_reacquisition']:
            lineage=record['property'].split(':',1)[0]
            model=lineage_models[lineage]
            ids={r.get('id',r.get('RELATION_ID')) for r in model['relations']}
            check('within_lineage_relations:'+group['group_id']+':'+record['property'],set(record['relation_ids'])<=ids)
    bwp=public(CURRENT,PREFIX+'r003f-r0041-bwp-ledger.json')
    for guard in bwp['selected_guard_records']['records']:
        row=pointer(archive_members['EVOLVED_BWP_DIRECTIONAL_RELATION_LEDGER.json'],guard['json_pointer'])
        check('guard_exact:'+row['id'],row==guard['record'] and sha(row)==guard['record_sha256'])
    check('guard_ids_order_exact',[r['record']['id'] for r in bwp['selected_guard_records']['records']]==c['selected_guard_ids'])
    for lin in ['r003f','r0041']:
        member=public(CURRENT,PREFIX+lin+'-member-qualification.json')
        for row in member['rows']:
            original=props[row['id']]['full_original_record']
            check('source_semantics:'+row['id'],all(original[k]==v for k,v in row['source_semantics'].items()))
            for key in ['full_bwp_register','full_source_intake']:
                ref=row[key];source=pointer(archive_members[ref['member']],ref['pointer'])
                check('current_register_binding:'+row['id']+':'+key,sha(source)==ref['canonical_record_sha256'])
    received=public(CURRENT,PREFIX+'r003f-r0041-preparation-receiving.json')
    for name,r in received['actual_returns'].items():
        check('receiving_public_hash:'+name,sha(normalize(r['content']))==r['public_content_canonical_sha256'])
    for scope,selection in [('R003F','EBPM'),('R0041','EWM'),('R003F::BWP-LANE-CONTINUATION','embedded_member_context_phase')]:
        returned={r['key']:r for r in received['actual_returns'][selection]['content']['members']}
        for row in c['scopes'][scope]['members']:
            check('carrier_full_receiver:'+scope+':'+row['key'],normalize(row['current_receiver_full_record'])==normalize(returned[row['key']]))
    group_return=received['actual_returns']['embedded_group_case_phase']['content']['groups']
    check('carrier_41_group_receiving',normalize(c['full_group_current_receiving'])==normalize(group_return))
    check('carrier_31_context_applicability',normalize(c['current_context_applicability'])==normalize(received['current_context_applicability']))
    continuation=public(CURRENT,PREFIX+'r003f-r0041-continuation-qualification.json')
    check('carrier_finite_receiving_exact',normalize(c['new_current_finite_receiving'])==normalize(continuation['finite_current_source_qualifications']))
    for name,record in continuation['records'].items():
        content=normalize(record['content'])
        if 'projected_json_canonical_sha256' in record:
            check('continuation_record_hash:'+name,sha(content)==record['projected_json_canonical_sha256'])
    # Distinguish historical TC10 from actual supplied receiving stimuli; no replay.
    ebpm=public(CURRENT,PREFIX+'r003f-actual-receiving.json')
    tc=ebpm['source_context_observations']['TC10']
    tc_source=public(HIST,PREFIX+'triad-integration/COMPOSITION_FINDINGS.json','TC10_frozen_source')
    tc_candidates=[]
    for ptr,obj in walk(tc_source):
        if obj.get('id')=='TC10':tc_candidates.append((ptr,obj))
    check('TC10_frozen_source_exact',len(tc_candidates)==1 and tc_candidates[0][1]==tc)
    current053=next(r for r in public(CURRENT,PREFIX+'r003f-member-qualification.json')['rows'] if r['id']=='EBPM:EBPM-053')
    check('EBPM053_source_still_unresolved',current053['original_source_status']=='UNRESOLVED')
    summary={'authority':'NONE; bounded immutable content verification, no new research or runtime evidence','total_checks':len(checks),'failed_checks':failures,'materialized_file_count':len(sources),'materialized_bytes':sum(r['bytes'] for r in sources.values()),'archive_member_pin_count':len(q['source_locator_resolution']['bwp_archive_members']),'TC10_source_pointer':tc_candidates[0][0] if tc_candidates else None,'checks':checks}
    (OUT/'public-record-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    (OUT/'immutable-source-manifest.json').write_text(json.dumps({'files':list(sources.values())},indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},indent=2))
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit('Run verify_delivery.py with the supplied delivery directory.')
