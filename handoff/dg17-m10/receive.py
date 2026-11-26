"""Read-only transport decoder. External provider/Root/actor authentication precedes any verdict."""
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract import (BASE, CARRIER, MAX_ZIP, OWNER, REPO, admit_result, binary, control_data,
                      decode, digest, keys, need, regular, sha, subject_files, unpack_zip, wire)

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def embedded(record):
    raw=binary(record['raw'])
    need(git_blob(raw)==record['oid'],'canonical Git blob identity')
    return raw
def delivered(value):
    raw=binary(value['bytes_b64'])
    need(len(raw)==value['bytes'] and value['digest']=='sha256:'+sha(raw),'canonical embedded bytes')
    return raw
def verify_artifact(phase,raw,expected_zip_sha,operator,run_id,job_id):
    need(phase in ('open','final') and sha(raw)==expected_zip_sha,'download differs from external artifact digest')
    names={'evidence.json'}
    if phase=='open':
        names.update({'subject-manifest.json','subject.zip','appointment.json'})
    members=unpack_zip(raw,names)
    e=decode(members['evidence.json'])
    need(e['schema']=='dg17.m10.'+phase+'.v1' and e['external_authentication_required'] is True,'artifact type/nonverdict')
    keys(e,'schema provider actual_context observations owner_commands records oracle_sha256 external_authentication_required')
    pins=decode(regular(Path(__file__).parent/'pins.json',65536))
    need(e['oracle_sha256']==pins['oracle'],'wrong oracle identity')
    p=e['provider']
    keys(p,'repository run_id attempt job_id job_key operator source started_at')
    need(all(type(p[k]) is int for k in ('run_id','job_id','attempt')),'provider integer types')
    d=e['actual_context']
    need(p==d['provider'] and (p['repository'],p['source'],p['operator'],p['run_id'],p['attempt'],p['job_id'],p['job_key'])==
         (REPO,BASE,operator,run_id,1,job_id,'canonical'),'foreign provider envelope')
    keys(d,'provider tools event host session subjects run_root receipt claim controller_oid generation ids route_ref open_oid packet_digest child_digest deadline opened_at opened_monotonic')
    records=e['records']
    expected_records={'controller','invalidation','continuity','initialization','checkpoint','binding','attribution','request',
                      'packet','required','opening','owner-0','owner-1'}
    if phase=='final':
        expected_records.update({'received-carrier','return-record','complete-record','owner-2','owner-3','owner-4','owner-5',
                                 'oracle-input','terminal-status'})
    need(set(records)==expected_records,'incomplete or extra records')
    for k in ('continuity','controller','invalidation'):
        embedded(records[k])
    stages=('required','opening') if phase=='open' else ('required','opening','return-record','complete-record')
    last=None
    parsed={}
    for key in stages:
        row=records[key]
        actual=decode(embedded(row))
        need(row['ref']==d['route_ref'] and actual['predecessor_record_oid']==last and
             actual['decision']=='REQUIRED' and all(actual[k]==v for k,v in d['ids'].items()),
             'canonical lineage or identity')
        parsed[key]=actual
        last=row['oid']
    opening=parsed['opening']
    packet_raw=delivered(opening['lifecycle']['delivery']['packet'])
    child=delivered(opening['lifecycle']['delivery']['child'])
    need(records['opening']['oid']==d['open_oid'] and opening['route_state']=='OPEN' and
         decode(packet_raw)==records['packet'] and records['packet']['target_identity']=='audit-assess'
         and d['packet_digest']=='sha256:'+sha(packet_raw) and d['child_digest']=='sha256:'+sha(child)
         and opening['package']['source_digests']['route-transaction.py']=='sha256:'+OWNER,'OPEN source bookend')
    if phase=='open':
        manifest=decode(members['subject-manifest.json'])
        subjects=subject_files(manifest,members['subject.zip'])
        app=decode(members['appointment.json'])
        need(app['subject_manifest']==sha(members['subject-manifest.json']) and app['subject_zip']==sha(members['subject.zip'])
             and app['source']==BASE and opening['lifecycle']['logical_task']==app['reviewer_task'],'review appointment')
        inputs={i['path']:i['digest'] for i in records['request']['inputs']}
        need(all(inputs['m10-subject/'+k]=='sha256:'+sha(v) for k,v in subjects.items()),'subject request digest')
        return dict(phase=phase,packet_digest=d['packet_digest'],members=sorted(names),authority='NONE')
    need('failure' not in records and records['terminal-status']==dict(status='STRUCTURAL_OBSERVATIONS_COLLECTED',authority='NONE'),
         'terminal nonverdict')
    commands=['decide','open','return','admit-current','complete','admit-current']
    obs=[x for x in e['observations'] if x['event'] in set(commands)]
    need(e['owner_commands']==commands==[x['event'] for x in obs] and obs[3]['argv']==obs[5]['argv'],
         'owner command sequence')
    values=[]
    for i,command in enumerate(commands):
        owner=records['owner-'+str(i)]
        raw_result=binary(owner['raw'])
        need(owner['command']==command and owner['exit_code']==obs[i]['exit_code'] and
             sha(raw_result)==obs[i]['stdout_sha256'],'owner command stream')
        values.append(decode(raw_result))
    o=records['oracle-input']
    need(o['recorded_owner_commands']==commands and o['open_provider_scope']==p,'oracle sequence/provider')
    for arm,index,key,pos in [('negative',3,'return-record',False),('positive',5,'complete-record',True)]:
        stage=o[arm]
        oid=records[key]['oid']
        admit_result(stage['exit_code'],stage['payload'],stage['before_record_oid'],stage['after_record_oid'],
                     oid,pos,d['ids'])
        need(stage['payload']==values[index] and stage['source_sha256']==OWNER and stage['provider_scope']==p
             and stage['exit_code']==records['owner-'+str(index)]['exit_code'],'observation source mismatch')
    carrier=records['received-carrier']
    bodies={k:binary(v) for k,v in carrier['bytes'].items()}
    need(set(bodies)==set(CARRIER),'carrier member set')
    expected=carrier['bindings']
    need(all(expected[k]==v for k,v in {**p,**d['ids'],'packet_digest':d['packet_digest'],
         'open_oid':d['open_oid'],'deadline':d['deadline'],'child_digest':d['child_digest'],'owner_sha256':OWNER}.items()),
         'carrier differs from open custody')
    control_data(bodies,expected,operator,carrier['parents'],carrier['oid'],carrier['oid'],carrier['received_at'])
    # These wire checks cannot authenticate a provider, control writer or fresh reviewer.
    for key in ('return-record','complete-record'):
        life=parsed[key]['lifecycle']
        need(delivered(life['delivery']['packet'])==packet_raw and delivered(life['delivery']['child'])==child and
             delivered(life['child_return'])==bodies['child-return.json'],'canonical delivery/return bytes')
    need(delivered(parsed['complete-record']['lifecycle']['governor_decision'])==bodies['decision.json'] and
         parsed['return-record']['lifecycle']['governor_decision'] is None,'canonical decision bytes')
    expected_joins={
        'returned_packet_digest':d['packet_digest'],'satisfied_packet_digest':d['packet_digest'],
        'returned_child_return_digest':'sha256:'+sha(bodies['child-return.json']),
        'satisfied_child_return_digest':'sha256:'+sha(bodies['child-return.json']),
        'satisfied_governor_return_digest':decode(bodies['decision.json'])['return_digest']}
    need(o['canonical_record_joins']==expected_joins and o['return_result_record_oid']==records['return-record']['oid']
         and o['complete_result_record_oid']==records['complete-record']['oid'],'canonical oracle data mismatch')
    return dict(phase=phase,packet_digest=d['packet_digest'],carrier_oid=carrier['oid'],authority='NONE',
                external_root_write_and_actual_reviewer_join_required=True)
if __name__=='__main__':
    if len(sys.argv)!=7:
        raise SystemExit('usage: receive.py open|final DOWNLOADED_ZIP PROVIDER_ZIP_SHA256 OPERATOR_OID RUN_ID JOB_ID')
    phase,path,expected,operator,run,job=sys.argv[1:]
    digest(expected)
    print(wire(verify_artifact(phase,regular(path,MAX_ZIP),expected,operator,int(run),int(job))).decode())
