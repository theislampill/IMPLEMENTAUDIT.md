"""Validate public data joins; actual custody remains a separate receiving act.

No subprocess, provider, native operation, currentness call or private-body
read occurs here. A consistent projection alone proves no native operation.
"""
import hashlib
import json
import re

KEYS=set('schema authority profile bank expected_tests expected_predicates status requirement started capture_custody_accepted capture_observation result result_disposition receiving currentness_before_bank currentness_after_bank qualified_for_pair_at_receiving closing_currentness_verified_before_teardown bank_watchdog_seconds elapsed_subtraction command_records historical_bank original_acceptance full_G2 C5 G1 G3'.split())
RECEIPT_KEYS=set('schema authority profile status source_commit source_tree receipt_transfer_authority while_same_checkout_current requirement_sha256 native_result_sha256 body_receiving_sha256 currentness_sha256 actual_case_count expected_case_count expected_predicate_count eligible_for_full_pair eligible_delta original_acceptance G1 C5 full_G2 G3 full_T14'.split())
HOST_KEYS=('os','architecture','kernel','uid','python_version','image_os','image_version','tools','boot_identity_sha256','credentials')

def need(value,code):
    if not value:raise ValueError(code)

def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')

def sha(value):return hashlib.sha256(encode(value)).hexdigest()
def digest(value):return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
def integer(value,low,high):return type(value) is int and low<=value<=high
def exact(value,keys,code):need(type(value) is dict and set(value)==set(keys),code)
def descriptor(value,limit):
    exact(value,('bytes','sha256'),'NATIVE_PUBLIC_DESCRIPTOR_SHAPE')
    need(integer(value['bytes'],0,limit) and digest(value['sha256']),'NATIVE_PUBLIC_DESCRIPTOR_BOUND')

def observed_result(result,I):
    exact(result,('schema','authority','source_commit','source_tree','profile','test_population','tests_run','success','rows','raw_result','native_operations_proven_by_summary','original_awards'),'NATIVE_PUBLIC_RESULT_KEYS')
    need(result['schema']=='dg16.g2-current-native-observed-result.v1' and result['authority']=='NONE'
         and result['source_commit']==I.H.SOURCE_COMMIT and result['source_tree']==I.H.SOURCE_TREE
         and result['profile']==I.P.PROFILE and result['test_population']==list(I.N.TESTS)
         and integer(result['tests_run'],1,2) and type(result['success']) is bool
         and result['native_operations_proven_by_summary'] is False and result['original_awards']==[],
         'NATIVE_PUBLIC_RESULT_IDENTITY')
    rows=result['rows']
    need(type(rows) is list and len(rows)==result['tests_run'],'NATIVE_PUBLIC_CASE_POPULATION')
    for index,row in enumerate(rows):
        exact(row,('test','outcome','tests_run','diagnostic_bytes','diagnostic_sha256'),'NATIVE_PUBLIC_CASE_KEYS')
        need(row['test']==I.N.TESTS[index] and row['outcome'] in ('PASS','FAIL')
             and integer(row['tests_run'],0,1) and integer(row['diagnostic_bytes'],0,4*1024**2)
             and digest(row['diagnostic_sha256']),'NATIVE_PUBLIC_CASE_SHAPE')
    need(result['success']==(len(rows)==2 and all(r['outcome']=='PASS' and r['tests_run']==1 for r in rows)),
         'NATIVE_PUBLIC_SUCCESS_FLAG')
    descriptor(result['raw_result'],4*1024**2)

def requirement(value,host,I,history):
    exact(value,('schema','authority','profile','historical_run_id','historical_source_commit','historical_source_tree','selected_source_commit','selected_source_tree','source_exact_match','host_exact_match','host_field_matches','observed_native_profile_sha256','historical_native_profile_sha256','source_dependency_applicability','historical_overall_closing_currentness','requires_fresh_changed_predicates','whole_nine_replay_selected','changed_host_requires_separate_qualification','historical_receipt_transfer'),'NATIVE_PUBLIC_REQUIREMENT_KEYS')
    observed=I.P.validate_host(host)
    matches=I.P.compare_historical(host,history['host_prerequisite'])
    expected=dict(schema='dg16.g2-current-native-requirement.v1',authority='NONE',profile=I.P.PROFILE,
        historical_run_id=history['run_id'],historical_source_commit=history['historical_source_commit'],
        historical_source_tree=history['historical_source_tree'],selected_source_commit=I.H.SOURCE_COMMIT,
        selected_source_tree=I.H.SOURCE_TREE,source_exact_match=False,host_exact_match=all(matches.values()),
        host_field_matches=matches,observed_native_profile_sha256=I.E.sha(I.E.encode(observed)),
        historical_native_profile_sha256=I.E.sha(I.E.encode(history['host_prerequisite'])),
        source_dependency_applicability=dict(manifest_sha256=I.N.APPLICABILITY_SHA,
            historical_manifest_sha256=I.H.NATIVE_CLOSURE_SHA,exact_directory_population=True,
            file_count=89,total_bytes=3200524,unchanged_members=87,changed_members=2,all_89_equal=False,
            unchanged_consumed_closure=False,
            applicability='REVIEWED_LINUX_SEMANTICS_PLUS_ACTUAL_CHANGED_PREDICATES_REQUIRED'),
        historical_overall_closing_currentness=False,requires_fresh_changed_predicates=True,
        whole_nine_replay_selected=False,changed_host_requires_separate_qualification=not all(matches.values()),
        historical_receipt_transfer=False)
    need(encode(value)==encode(expected),'NATIVE_PUBLIC_REQUIREMENT_BINDING')

def capture_records(rows,*,positive):
    """Receive the changed internal-refusal grammar without granting custody."""
    need(type(rows) is list and type(positive) is bool,'CAPTURE_RECORD_POPULATION')
    need(not positive or len(rows)>0,'CAPTURE_POSITIVE_POPULATION_EMPTY')
    failed=unstarted=0
    for row in rows:
        need(type(row) is dict and type(row.get('process_started')) is bool,'CAPTURE_RECORD_SHAPE')
        if not row['process_started']:
            exact(row,('name','process_started','returncode','start_errno','reason_code'),'CAPTURE_UNSTARTED_KEYS')
            need(row['returncode'] is None and integer(row['start_errno'],0,4096),'CAPTURE_UNSTARTED_SHAPE')
            unstarted+=1
            need(not positive,'CAPTURE_POSITIVE_UNSTARTED')
            continue
        need('internal_failure' in row,'CAPTURE_INTERNAL_FAILURE_FIELD_MISSING')
        failure=row['internal_failure']
        if failure is not None:
            exact(failure,('code','errno'),'CAPTURE_INTERNAL_FAILURE_KEYS')
            need(failure['code']=='PIDFD_ACQUISITION_REFUSED',
                 'CAPTURE_INTERNAL_FAILURE_CODE')
            need(integer(failure['errno'],0,4096),
                 'CAPTURE_INTERNAL_FAILURE_ERRNO')
            failed+=1
        if positive:
            need(type(row.get('returncode')) is int,'CAPTURE_POSITIVE_TERMINAL_STATUS_MISSING')
            need(failure is None and row.get('pidfd_acquired') is True and row.get('streams_complete') is True
                 and row.get('timeout') is False and row.get('output_bound_exceeded') is False
                 and type(row.get('cleanup')) is dict and row['cleanup'].get('echild') is True,
                 'CAPTURE_POSITIVE_CUSTODY_REFUSED')
    return dict(count=len(rows),internal_failures=failed,unstarted=unstarted,
        positive_custody_required=positive,authority='NONE')

def validate_admission(payload,*,integration,gate,binding,composition):
    """Join retained decisions to exact code; caller receives actual authorship."""
    I=integration
    observed=I.A.validate(payload,I.bindings(),I.history()['host_prerequisite'])
    need(type(gate) is dict and encode(gate)==encode(observed),'NATIVE_GATE_RECOMPUTATION')
    adoption=I.E.parse(payload[I.A.FILES[1]])
    expected=dict(candidate_seal_sha256=observed['candidate_seal_sha256'],
        native_review_seal_sha256=adoption['independent_review_seal_sha256'],
        public_native_review_sha256=observed['review_sha256'],
        public_native_adoption_sha256=observed['adoption_sha256'])
    for key,value in expected.items():
        need(type(binding.get(key)) is str and binding[key]==value and
             type(composition.get(key)) is str and composition[key]==value,
             'NATIVE_COMPOSITION_DECISION_BINDING')
    return observed

def validate(value,*,kind,host,integration,projection_failure=False):
    I=integration
    need(kind in ('live','terminal'),'NATIVE_PUBLIC_KIND')
    need(type(projection_failure) is bool,'NATIVE_PUBLIC_FAILURE_FLAG')
    if value is None:
        need(kind=='terminal' and projection_failure,'NATIVE_PUBLIC_UNAVAILABLE_WITHOUT_FAILURE')
        return dict(schema='dg16.current-native-public-data-receiving.v1',authority='NONE',
            status='UNAVAILABLE_PROJECTION_FAILURE_RETAINED',eligible_summary=False,actual_cases=None,
            projection_sha256=None,fresh_currentness_or_native_authority=False,
            private_body_authenticity='UNAVAILABLE_FROM_THIS_PROJECTION',original_awards=[])
    exact(value,KEYS,'NATIVE_PUBLIC_KEYS')
    need(value['schema']=='dg16.full-registry-current-native-prerequisite.v2'
         and value['authority']=='NONE' and value['profile']==I.P.PROFILE
         and value['bank']=='tests/work-graph-original14-receiving-cases.py'
         and value['expected_tests']==list(I.N.TESTS) and value['expected_predicates']==list(I.N.PREDICATES)
         and value['status'] in I.STATUSES and value['result_disposition'] in I.DISPOSITIONS
         and type(value['bank_watchdog_seconds']) is int and value['bank_watchdog_seconds']==I.H.NATIVE_BANK_SECONDS
         and type(value['elapsed_subtraction']) is int and value['elapsed_subtraction']==0,
         'NATIVE_PUBLIC_IDENTITY')
    for key in ('started','capture_custody_accepted','currentness_before_bank','currentness_after_bank',
                'qualified_for_pair_at_receiving','closing_currentness_verified_before_teardown'):
        need(type(value[key]) is bool,'NATIVE_PUBLIC_BOOLEAN')
    need(all(value[k] is False for k in ('original_acceptance','full_G2','C5','G1','G3')),'NATIVE_PUBLIC_NO_AWARDS')
    history=I.history()
    expected_history=dict(source_commit=history['historical_source_commit'],source_tree=history['historical_source_tree'],
        applicability_source_commit=I.HISTORICAL_COMMIT,applicability_source_tree=I.HISTORICAL_TREE,
        receipt_sha256=I.H.PREREQUISITE_SHA,tests_run=9,transferred=False)
    need(encode(value['historical_bank'])==encode(expected_history),'NATIVE_PUBLIC_HISTORICAL_BINDING')
    req=value['requirement']
    if req is not None:requirement(req,host,I,history)
    commands=value['command_records']
    exact(commands,('count','bytes','sha256','all_recorded_cleanup_echild','scope'),'NATIVE_PUBLIC_COMMAND_KEYS')
    need(integer(commands['count'],0,I.H.NATIVE_COMMAND_COUNT) and integer(commands['bytes'],3,I.H.NATIVE_COMMAND_BYTES)
         and digest(commands['sha256']) and type(commands['all_recorded_cleanup_echild']) is bool
         and commands['scope']=='EXACT_COMMAND_RECORDS_RETAINED_JOB_PRIVATE','NATIVE_PUBLIC_COMMAND_BOUND')
    capture=value['capture_observation'];result=value['result'];received=value['receiving']
    if capture is not None:
        exact(capture,('primary_returncode','streams_complete','stdout_bytes','stdout_sha256','stderr_bytes','stderr_sha256'),'NATIVE_PUBLIC_CAPTURE_KEYS')
        need((capture['primary_returncode'] is None or type(capture['primary_returncode']) is int)
             and type(capture['streams_complete']) is bool,'NATIVE_PUBLIC_CAPTURE_SHAPE')
        for stream in ('stdout','stderr'):
            need(integer(capture[stream+'_bytes'],0,32768) and digest(capture[stream+'_sha256']),'NATIVE_PUBLIC_CAPTURE_BOUND')
    else:need(result is None and value['capture_custody_accepted'] is False,'NATIVE_PUBLIC_CAPTURE_MISSING')
    if result is not None:observed_result(result,I)
    eligible=False
    if received is not None:
        exact(received,RECEIPT_KEYS,'NATIVE_PUBLIC_RECEIPT_KEYS')
        need(req is not None and result is not None and capture is not None
             and all(value[k] is True for k in ('started','capture_custody_accepted','currentness_before_bank','currentness_after_bank'))
             and capture['streams_complete'] is True and commands['count']>=5,'NATIVE_PUBLIC_RECEIPT_PREREQUISITES')
        eligible=result['success']
        status='RECEIVED_CURRENT_CHANGED_NATIVE_PREDICATES' if eligible else 'RECEIVED_FAILED_CURRENT_NATIVE_EVIDENCE'
        fixed=dict(schema='dg16.full-registry-current-native-receiving.v2',authority='NONE',profile=I.P.PROFILE,
            status=status,source_commit=I.H.SOURCE_COMMIT,source_tree=I.H.SOURCE_TREE,receipt_transfer_authority=False,
            while_same_checkout_current=True,requirement_sha256=sha(req),native_result_sha256=sha(result),
            actual_case_count=result['tests_run'],expected_case_count=2,expected_predicate_count=5,
            eligible_for_full_pair=eligible,eligible_delta='EXACT_CURRENT_NATIVE_PREREQUISITE_ONLY_NO_ORIGINAL_AWARD',
            original_acceptance=False,G1=False,C5=False,full_G2=False,G3=False,full_T14=False)
        need(all(type(received[k]) is type(v) and received[k]==v for k,v in fixed.items())
             and digest(received['body_receiving_sha256']) and digest(received['currentness_sha256'])
             and value['status']==value['result_disposition']==status and req['host_exact_match'] is True,
             'NATIVE_PUBLIC_RECEIPT_JOIN')
        need(capture['primary_returncode']==(0 if eligible else 1),'NATIVE_PUBLIC_RECEIPT_CAPTURE_RETURN')
    else:
        need(not value['status'].startswith('RECEIVED_') and not value['result_disposition'].startswith('RECEIVED_'),
             'NATIVE_PUBLIC_RECEIPT_MISSING')
    need(value['qualified_for_pair_at_receiving']==eligible,'NATIVE_PUBLIC_ELIGIBILITY_JOIN')
    need(not value['closing_currentness_verified_before_teardown'] or eligible,'NATIVE_PUBLIC_CLOSING_WITHOUT_RECEIPT')
    if kind=='live':
        need(eligible and commands['all_recorded_cleanup_echild'] is True,'NATIVE_PUBLIC_LIVE_NOT_ELIGIBLE')
    return dict(schema='dg16.current-native-public-data-receiving.v1',authority='NONE',
        status=value['status'],eligible_summary=eligible,actual_cases=0 if result is None else result['tests_run'],
        projection_sha256=sha(value),fresh_currentness_or_native_authority=False,
        private_body_authenticity='REQUIRES_ACTUAL_BOUND_HOST_AND_INDEPENDENT_RECEIVING',original_awards=[])
