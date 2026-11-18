# Exact bounded source projection; source module is never imported.
SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'

SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'

NATIVE_STEPS=('initialize','discover','invalidate','read-state','read-roadmap','resume','verify','require')

STEPS=('prepare',*NATIVE_STEPS,'input-preflight','native-bank','prerequisites','g1','receive','g3-receive','g3-consume','g3-decide')

PUBLIC_NAMES=('RESULT.json','HOST.json','SOURCE.json','OPERATION.json','G3.json','NSS.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')

PUBLIC_FILE_BYTES=65536

PUBLIC_TOTAL_BYTES=262144

ENCODED_LINE_BYTES=262144

ENCODED_TOTAL_BYTES=1048576

class Refusal(Exception): pass

def need(value,code):
    if not value:raise Refusal(code)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')

def parse_json(raw):
    def pairs(values):
        result={}
        for key,value in values:
            need(key not in result,'DUPLICATE_JSON_KEY');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))

def integer(value,maximum=2**63-1):
    return value if type(value) is int and 0<=value<=maximum else None

def hash_value(value):
    return value if type(value) is str and re.fullmatch('[0-9a-f]{64}',value) else None

EFFECT_RECORDS=(('NSS_CONFIGURATION','NSS_CONFIGURATION.json',8192,'nss_configuration','public_state'),
    ('G3_EFFECT_STATE','G3_EFFECT_STATE.json',4096,'g3_receiving','validate_effect_state'),
    ('G3_ORIGINAL_RECEIPT','G3_ORIGINAL_DECISION_RECEIPT.json',16384,'g3_receiving','validate_original_receipt'))

def validated_effects(state):
    """Revalidate retained finite projections before primary publication."""
    records=state.get('closed_effect_observations')
    if records is None:
        return {name:dict(status='NOT_OBSERVED',bytes=None,sha256=None,public=None) for name,*_ in EFFECT_RECORDS}
    need(type(records) is dict and set(records)=={name for name,*_ in EFFECT_RECORDS},'EFFECT_RECORD_POPULATION')
    for label,record in records.items():
        need(type(record) is dict and set(record)=={'status','bytes','sha256','public'}
             and record['status'] in ('NOT_OBSERVED','EXACT_RECORD_SCHEMA_UNQUALIFIED',
                 'EXACT_CLOSED_RECORD_OBSERVED','UNREADABLE_OR_GUARD_REFUSED'),'EFFECT_RECORD_SHAPE')
        if record['status'].startswith('EXACT_'):
            need(integer(record['bytes'],16384) is not None and hash_value(record['sha256']) is not None,
                 'EFFECT_RECORD_BINDING')
        else:need(record['bytes'] is None and record['sha256'] is None,'EFFECT_RECORD_UNKNOWN')
        if record['status']=='EXACT_CLOSED_RECORD_OBSERVED':
            if label=='NSS_CONFIGURATION':
                # The projection is deliberately smaller than the private
                # journal. Its closed form is validated independently below.
                validate_nss_effect(record['public'])
            else:
                validator='validate_effect_state' if label=='G3_EFFECT_STATE' else 'validate_original_receipt'
                need(getattr(load_module('g3_receiving'),validator)(canonical(record['public']),
                     **({'retained_bodies':retained_m4_packet_bodies()} if label=='G3_ORIGINAL_RECEIPT' else {}))==record['public'],
                     'EFFECT_RECORD_PUBLIC_CHANGED')
        else:need(record['public'] is None,'EFFECT_RECORD_UNQUALIFIED_PUBLIC')
    return records

def validate_nss_effect(value):
    fields={'schema','authority','phase','replacement','configured','temporary_creation_recorded','temporary_removal_recorded',
        'temporary_false_meaning',
        'failure_code','before','after','changed_rows','original_gate_unchanged','ownership_changed',
        'product_source_changed','disposition'}
    module=load_module('nss_configuration')
    need(type(value) is dict and set(value)==fields
         and value['schema']=='dg16.g1-nss-effect-observation.v1' and value['authority']=='NONE'
         and value['phase'] in module.PHASES and value['replacement'] in ('NOT_STARTED','STARTED_OUTCOME_UNKNOWN','COMPLETED')
         and (value['configured'] is None or type(value['configured']) is bool)
         and type(value['temporary_creation_recorded']) is bool and type(value['temporary_removal_recorded']) is bool
         and value['temporary_false_meaning']=='NO_DURABLE_COMPLETION_OBSERVATION_NOT_PROOF_OF_ABSENCE'
         and (value['failure_code'] is None or value['failure_code'] in module.REFUSALS
             or value['failure_code']=='NSS_CONFIGURATION_UNCLASSIFIED_REFUSAL')
         and value['changed_rows']==['passwd'] and value['original_gate_unchanged'] is True
         and value['ownership_changed'] is False and value['product_source_changed'] is False
         and value['disposition']=='RETAIN_CONFIGURED_FILE_UNTIL_VM_DISPOSAL','NSS_EFFECT_PUBLIC_SCHEMA')
    for name in ('before','after'):
        row=value[name]
        need(row is None or type(row) is dict and set(row)=={'bytes','sha256','physical_sha256'}
             and integer(row['bytes'],65536) is not None and hash_value(row['sha256']) is not None
             and hash_value(row['physical_sha256']) is not None,'NSS_EFFECT_PUBLIC_OBSERVATION')
    need((value['replacement']=='COMPLETED')==(value['configured'] is True)
         and (value['replacement']!='STARTED_OUTCOME_UNKNOWN' or value['configured'] is None)
         and (value['replacement']!='NOT_STARTED' or value['configured'] is False),'NSS_EFFECT_PUBLIC_CONTRADICTION')
    return value

def validate_transport(files):
    need(set(files)==set(PUBLIC_NAMES),'PUBLIC_FILE_ALLOWLIST_REFUSED')
    total=0;encoded_total=0;lines=[]
    for name in PUBLIC_NAMES:
        raw=files[name];need(type(raw) is bytes and len(raw)<=PUBLIC_FILE_BYTES,'PUBLIC_FILE_BOUND')
        need(canonical(parse_json(raw))==raw,'PUBLIC_CANONICAL_JSON_REFUSED')
        total+=len(raw)
        line=('DG16_G1_HOSTED_EVIDENCE '+name+' '+base64.b64encode(raw).decode('ascii'))
        encoded_total+=len(line.encode('ascii'))+1
        need(len(line.encode('ascii'))+1<=ENCODED_LINE_BYTES,'PUBLIC_ENCODED_LINE_BOUND');lines.append(line)
    # Reserve the other quarter for the one earlier root request. The job's
    # original aggregate envelope never grows across the two publication phases.
    need(total<=PUBLIC_TOTAL_BYTES-65536-32768 and encoded_total<=ENCODED_TOTAL_BYTES-262144-131072,'PUBLIC_AGGREGATE_BOUND')
    manifest=parse_json(files['ARTIFACT_MANIFEST.json'])
    expected=dict(schema='dg16.g1-hosted-artifacts.v1',members=[dict(name=name,bytes=len(raw),sha256=digest(raw))
        for name,raw in sorted(files.items()) if name!='ARTIFACT_MANIFEST.json'])
    need(manifest==expected,'PUBLIC_MANIFEST_DIFFERS')
    return lines

FAILURE_OBSERVATION_NAMES=('RETENTION_FAILURE.json','ARTIFACT_MANIFEST.json')

def validate_failure_files(files):
    need(set(files)==set(FAILURE_OBSERVATION_NAMES),'FALLBACK_ALLOWLIST_REFUSED')
    raw=files['RETENTION_FAILURE.json'];value=parse_json(raw)
    expected_keys={'schema','authority','status','original_acceptance','original_G1_award','original_G3_award','reason',
        'automatic_original_awards','whole_DG16_awarded','closed_effect_observations',
        'run_id','workflow_commit','selected_source_commit','selected_source_tree','private_record_bindings','completed_steps',
        'operation_started','producer_owner_invoked','raw_receiving_complete','separate_step_receiving_complete','bank_started',
        'bank_received','g3_prepared','g3_received','child_terminal_confirmed','all_step_children_reaped','operation_result_status',
        'observations_convey_currentness','unknown_means_no_effect','raw_private_outputs_published'}
    need(canonical(value)==raw and len(raw)<=24576 and type(value) is dict and set(value)==expected_keys
         and value.get('schema')=='dg16.g1-hosted-retention-failure.v1' and value.get('authority')=='NONE'
         and value.get('status')=='UNQUALIFIED' and value['reason']=='PRIMARY_VALIDATED_PUBLIC_EXPORT_UNAVAILABLE'
         and all(value[k] is False for k in ('automatic_original_awards','whole_DG16_awarded',
             'observations_convey_currentness','unknown_means_no_effect','raw_private_outputs_published'))
         and re.fullmatch('[0-9]{1,20}',value['run_id']) and re.fullmatch('[0-9a-f]{40}',value['workflow_commit'])
         and value['selected_source_commit']==SOURCE_COMMIT and value['selected_source_tree']==SOURCE_TREE,
         'FALLBACK_SCHEMA_REFUSED')
    effects=validated_effects(dict(closed_effect_observations=value['closed_effect_observations']))
    original=effects['G3_ORIGINAL_RECEIPT']['public'];gates=(original or {}).get('gate_decisions',{})
    need(original is None or original['run_id']==value['run_id'],'ORIGINAL_RECEIPT_JOB_BINDING')
    expected_g1=None if original is None else gates['G1']['disposition']=='ACCEPTED_AT_DECLARED_SCOPE'
    expected_g3=None if original is None else gates['G3']['disposition']=='ACCEPTED_AT_DECLARED_SCOPE'
    expected_rows=None if original is None else any(row['disposition']=='ACCEPTED_AT_DECLARED_SCOPE' for row in original['original_rows'])
    need(value['original_G1_award'] is expected_g1 and value['original_G3_award'] is expected_g3
         and value['original_acceptance'] is expected_rows,'FALLBACK_ROOT_DECISION_BINDING')
    for key in ('operation_started','producer_owner_invoked','raw_receiving_complete','separate_step_receiving_complete',
                'bank_started','bank_received','g3_prepared','g3_received','child_terminal_confirmed','all_step_children_reaped'):
        need(value[key] is None or type(value[key]) is bool,'FALLBACK_FLAG_REFUSED')
    completed=value['completed_steps']
    need(completed is None or type(completed) is list and len(completed)<=len(STEPS)
         and completed==list(STEPS[:len(completed)]),'FALLBACK_STEP_POPULATION_REFUSED')
    need(value['operation_result_status'] in ('UNESTABLISHED','INCOMPLETE','UNQUALIFIED','RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE'),
         'FALLBACK_STATUS_REFUSED')
    records=value['private_record_bindings']
    need(type(records) is dict and set(records)=={'STATE','G1_RESULT','G1_RECEIVING','G3_EFFECT_STATE',
        'NSS_CONFIGURATION','G3_ORIGINAL_RECEIPT'},'FALLBACK_RECORD_POPULATION')
    for row in records.values():
        need(type(row) is dict and set(row)=={'status','bytes','sha256'}
             and row['status'] in ('EXACT_BOUNDED_RECORD_OBSERVED','NOT_OBSERVED','UNREADABLE_OR_GUARD_REFUSED'),
             'FALLBACK_RECORD_SHAPE')
        if row['status']=='EXACT_BOUNDED_RECORD_OBSERVED':
            need(type(row['bytes']) is int and 0<=row['bytes']<=4*1024**2
                 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']),'FALLBACK_RECORD_BINDING')
        else:need(row['bytes'] is None and row['sha256'] is None,'FALLBACK_UNKNOWN_BINDING')
    expected=canonical(dict(schema='dg16.g1-hosted-failure-artifacts.v1',members=[
        dict(name='RETENTION_FAILURE.json',bytes=len(raw),sha256=digest(raw))]))
    need(files['ARTIFACT_MANIFEST.json']==expected,'FALLBACK_MANIFEST_REFUSED')
    lines=['DG16_G1_FAILURE_EVIDENCE '+name+' '+base64.b64encode(files[name]).decode('ascii') for name in FAILURE_OBSERVATION_NAMES]
    need(sum(map(len,files.values()))<=32768 and sum(len(line)+1 for line in lines)<=131072,'FALLBACK_TRANSPORT_BOUND')
    return lines
