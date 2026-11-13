"""Closed prospective request and same-job earned host qualification.

No function launches a process, issues a Root record, or grants pair authority.
The immutable host adapter supplies and reconsumes actual raw evidence.
"""
import re
E = _HOST_EVIDENCE_IO
P = _G2_NATIVE_PROFILE
need = E.need
ISSUER = '01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'
REQUEST_SCHEMA = 'dg16.prospective-current-host-qualification-request.v1'
BANK_SCHEMA = 'dg16.current-host-native-bank-actual-result.v1'
OBSERVED_SCHEMA = 'dg16.current-host-native-bank-observed-result.v1'
SOURCE_BINDINGS = ('profile_sha256','probe_sha256','native_receiver_sha256','native_admission_sha256',
    'integration_sha256','qualification_sha256','utility_sha256','source_manifest_sha256',
    'source_applicability_sha256','receiver_inputs_sha256','policy_sha256','pair_driver_sha256')
BANK_TESTS = (
 'test_actual_later_invalidation_prevents_return',
 'test_derivative_snapshot_change_after_use_prevents_return',
 'test_native_intake_later_boundary_prevents_return',
 'test_native_intake_rejects_opaque_fixture_work_graph',
 'test_native_intake_rejects_unowned_nested_record',
 'test_native_intake_uses_current_original14_not_retired_root',
 'test_protected_document_change_after_use_prevents_return',
 'test_real_original14_documents_reach_unchanged_graph_parser',
 'test_valid_original14_owner_does_not_supply_missing_graph_document')
PORT_TESTS = ('test_native_intake_uses_current_original14_not_retired_root',
              'test_native_intake_later_boundary_prevents_return')
LIMITS = dict(bank_seconds=600,command_records=32,command_metadata_bytes=128*1024,private_bytes=64*1024**2,file_bytes=4*1024**2,entries=4096)
TARGET_KEYS = (*P.HOST_FIELDS,'image_os','image_version','uid','credentials')
SELECTED_HOST = {'architecture': 'x86_64', 'credentials': {'egid': 1001, 'euid': 1001, 'gid': 1001, 'sgid': 1001, 'suid': 1001, 'uid': 1001}, 'image_os': 'ubuntu26', 'image_version': '20261111.82.6', 'kernel': '7.0.0-1016-aws', 'os': {'ID': 'ubuntu', 'VERSION_ID': '26.04'}, 'python_version': [3, 14, 4], 'tools': {'bash': {'available': True, 'bytes': 1540520, 'canonical': '/usr/bin/bash', 'requested': '/usr/bin/bash', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': '450c68376d14e5040d36cce58605c35b2211d244f3079297440dc9d602ee4994'}, 'bwrap': {'available': True, 'bytes': 80424, 'canonical': '/usr/bin/bwrap', 'requested': '/usr/bin/bwrap', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': 'a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361'}, 'git': {'available': True, 'bytes': 4771424, 'canonical': '/usr/bin/git', 'requested': '/usr/bin/git', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': '8fb7c4c2a0e5ec847626098c2a375ff01d6a9e5f81352e3ae56f30b41ec850cd'}, 'python3': {'available': True, 'bytes': 7468968, 'canonical': '/usr/bin/python3.14', 'requested': '/usr/bin/python3', 'root_owned_nonwritable_chain': True, 'setid_or_file_capabilities': False, 'sha256': 'be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd'}}, 'uid': 1001}


def hex64(v):
    return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None


def target_host(host):
    P.validate_host(host)
    return {k:host[k] for k in TARGET_KEYS}


def validate_request(raw, pin, bindings, host, episode):
    need(hex64(pin),'G2_CURRENT_HOST_REQUEST_UNISSUED')
    need(type(raw) is bytes and 0<len(raw)<=16384 and E.sha(raw)==pin,'G2_CURRENT_HOST_REQUEST_PIN')
    value=E.parse(raw)
    need(type(bindings) is dict and set(bindings)==set(SOURCE_BINDINGS)
         and all(hex64(v) for v in bindings.values()),'G2_CURRENT_HOST_REQUEST_SOURCE_BINDINGS')
    need(type(episode) is dict and set(episode)==set('repository branch run_id run_attempt workflow_commit'.split())
         and episode['repository']=='theislampill/IMPLEMENTAUDIT.md'
         and type(episode['branch']) is str
         and re.fullmatch('pro/dg16-r5-full-g2-direct-host-[0-9]+-[0-9]{8}',episode['branch'])
         and type(episode['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',episode['run_id'])
         and type(episode['run_attempt']) is int and episode['run_attempt']==1
         and type(episode['workflow_commit']) is str and re.fullmatch('[0-9a-f]{40}',episode['workflow_commit']),
         'G2_CURRENT_HOST_REQUEST_EPISODE')
    expected=dict(schema=REQUEST_SCHEMA,actor='/root',issuer_thread=ISSUER,
        decision='REQUEST_ONE_FRESH_CURRENT_HOST_QUALIFICATION',one_shot=True,
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,repository=episode['repository'],
        branch=episode['branch'],control_branch=episode['branch'].replace('-host-','-control-'),
        source_bindings=bindings,target_host=SELECTED_HOST,bank_tests=list(BANK_TESTS),
        current_port_tests=list(PORT_TESTS),limits=LIMITS,
        boot_policy='BIND_ACTUAL_PRE_SETUP_BOOT_AND_HOLD_THIS_JOB',
        scope='QUALIFICATION_ONLY_NO_PAIR_OR_PROVIDER_AUTHORITY',effect_grant=False,original_awards=[])
    need(type(value) is dict and set(value)==set(expected)
         and E.encode(value)==E.encode(expected),
         'G2_CURRENT_HOST_PROSPECTIVE_REQUEST_REFUSED')
    selected=target_host(host)
    need(selected==SELECTED_HOST,'G2_CURRENT_HOST_SELECTED_TUPLE_REFUSED')
    return dict(schema='dg16.current-host-request-admission.v1',request_sha256=pin,
        selected_host_sha256=E.sha(E.encode(selected)),host_sha256=E.sha(E.encode(host)),
        boot_identity_sha256=host['boot_identity_sha256'],credentials_sha256=E.sha(E.encode(host['credentials'])),
        episode=episode,source_bindings=bindings,qualified=False)


def require_same_admission(opened, current):
    need(type(opened) is dict and E.encode(opened)==E.encode(current),'G2_CURRENT_HOST_ADMISSION_CHANGED')


def require_bank(value):
    need(type(value) is dict and value.get('schema')==BANK_SCHEMA
         and value.get('source_commit')==SOURCE_COMMIT and value.get('source_tree')==SOURCE_TREE
         and value.get('test_population')==list(BANK_TESTS)
         and type(value.get('tests_run')) is int and value['tests_run']==9
         and value.get('success') is True and value.get('original_awards')==[],
         'G2_CURRENT_HOST_NINE_CASE_BANK_NOT_RECEIVED')
    rows=value.get('rows')
    need(type(rows) is list and len(rows)==9 and [r.get('test') for r in rows]==list(BANK_TESTS)
         and all(r.get('outcome')=='PASS' and type(r.get('tests_run')) is int and r['tests_run']==1 for r in rows),
         'G2_CURRENT_HOST_NINE_CASE_POPULATION_OR_OUTCOME')
    return rows


def current_port(value):
    # This in-memory view is never written as a pretend two-case execution.
    # Every row is selected from the exact complete nine-case body received first.
    rows=require_bank(value)
    by_name={r['test']:r for r in rows}
    result=dict(value)
    result.update(schema='dg16.focused-native-actual-result.v1',test_population=list(PORT_TESTS),
                  tests_run=2,rows=[by_name[n] for n in PORT_TESTS],success=True)
    return result


def earn(admission, value, result_raw, host, context, custody_sha256, support_raw):
    rows=require_bank(value)
    need(E.parse(result_raw)==value,'G2_CURRENT_HOST_EARNED_RAW_VALUE_MISMATCH')
    need(admission['qualified'] is False and admission['host_sha256']==E.sha(E.encode(host))
         and admission['episode']==context['source_custody']['workflow_context'],
         'G2_CURRENT_HOST_EARNED_SUBJECT_MISMATCH')
    need(hex64(custody_sha256),'G2_CURRENT_HOST_EARNED_CUSTODY')
    port=current_port(value)
    record=dict(schema='dg16.earned-current-host-native-qualification.v1',authority='NONE',
        status='RECEIVED_FRESH_NINE_CASE_CURRENT_HOST',scope='THIS_JOB_VM_CONTROLLER_AND_SOURCE_ONLY',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,request_sha256=admission['request_sha256'],
        request_admission_sha256=E.sha(E.encode(admission)),host_sha256=admission['host_sha256'],
        boot_identity_sha256=admission['boot_identity_sha256'],credentials_sha256=admission['credentials_sha256'],
        workflow_context_sha256=E.sha(E.encode(admission['episode'])),controller=context['controller'],
        continuity_receipt_sha256=E.sha(context['initial_receipt'].encode()),runtime_sha256=context['runtime_sha256'],
        source_closure_sha256=E.sha(support_raw['SOURCE_CLOSURE.json']),
        source_custody_sha256=E.sha(support_raw['SOURCE_CUSTODY.json']),
        raw_bank_result=dict(bytes=len(result_raw),sha256=E.sha(result_raw)),
        test_population=list(BANK_TESTS),tests_run=9,current_port_tests=list(PORT_TESTS),
        current_port_rows_sha256=E.sha(E.encode(port['rows'])),
        capture_sha256=E.sha(support_raw['CAPTURE.json']),
        before_currentness_sha256=E.sha(support_raw['BEFORE_CURRENTNESS.json']),
        after_currentness_sha256=E.sha(support_raw['AFTER_CURRENTNESS.json']),
        custody_sha256=custody_sha256,historical_receipt_transfer=False,original_awards=[])
    validate_earned(record,admission,dict(raw_result=record['raw_bank_result'],success=True,tests_run=9))
    return record


def validate_earned(record, admission, observed):
    keys=set('schema authority status scope source_commit source_tree request_sha256 request_admission_sha256 host_sha256 boot_identity_sha256 credentials_sha256 workflow_context_sha256 controller continuity_receipt_sha256 runtime_sha256 source_closure_sha256 source_custody_sha256 raw_bank_result test_population tests_run current_port_tests current_port_rows_sha256 capture_sha256 before_currentness_sha256 after_currentness_sha256 custody_sha256 historical_receipt_transfer original_awards'.split())
    need(type(record) is dict and set(record)==keys,'G2_CURRENT_HOST_EARNED_RECORD_KEYS')
    fixed=dict(schema='dg16.earned-current-host-native-qualification.v1',authority='NONE',
        status='RECEIVED_FRESH_NINE_CASE_CURRENT_HOST',scope='THIS_JOB_VM_CONTROLLER_AND_SOURCE_ONLY',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,request_sha256=admission['request_sha256'],
        request_admission_sha256=E.sha(E.encode(admission)),host_sha256=admission['host_sha256'],
        boot_identity_sha256=admission['boot_identity_sha256'],credentials_sha256=admission['credentials_sha256'],
        workflow_context_sha256=E.sha(E.encode(admission['episode'])),
        test_population=list(BANK_TESTS),tests_run=9,current_port_tests=list(PORT_TESTS),
        historical_receipt_transfer=False,original_awards=[])
    need(all(type(record[k]) is type(v) and record[k]==v for k,v in fixed.items()),'G2_CURRENT_HOST_EARNED_RECORD_BINDING')
    need(observed['success'] is True and observed['tests_run']==9 and record['raw_bank_result']==observed['raw_result'],
         'G2_CURRENT_HOST_EARNED_BANK_BINDING')
    need(type(record['controller']) is str and record['controller']=='r5-full-g2-'+admission['episode']['run_id']+'-a1',
         'G2_CURRENT_HOST_EARNED_CONTROLLER')
    digest_fields=keys-set(fixed)-{'controller','raw_bank_result'}
    need(all(hex64(record[k]) for k in digest_fields),'G2_CURRENT_HOST_EARNED_RECORD_DIGEST')
    raw=record['raw_bank_result']
    need(type(raw) is dict and set(raw)=={'bytes','sha256'} and type(raw['bytes']) is int
         and 0<raw['bytes']<=4*1024**2 and hex64(raw['sha256']),'G2_CURRENT_HOST_EARNED_RAW_DESCRIPTOR')


def source_bindings(H, probe_sha256, applicability_sha256):
    # The outer adapter pins the request, so its own digest is deliberately excluded.
    return dict(profile_sha256=H.NATIVE_PROFILE_SHA,probe_sha256=probe_sha256,
        native_receiver_sha256=H.NATIVE_RECEIVER_SHA,native_admission_sha256=H.NATIVE_ADMISSION_SHA,
        integration_sha256=H.NATIVE_INTEGRATION_SHA,qualification_sha256=H.CURRENT_HOST_SHA,
        utility_sha256=H.UTILITY_SHA,source_manifest_sha256=H.MANIFEST_SHA,
        source_applicability_sha256=applicability_sha256,receiver_inputs_sha256=H.RELATION_INPUTS_SHA,
        policy_sha256=H.POLICY_SHA,pair_driver_sha256=H.PAIR_DRIVER_SHA)


def validate_public_admission(admission, pin, bindings, host, branch):
    # Closed consistency only. No raw request, custody or native authority is proved here.
    need(type(admission) is dict and set(admission)==set('schema request_sha256 selected_host_sha256 host_sha256 boot_identity_sha256 credentials_sha256 episode source_bindings qualified'.split()),
         'G2_CURRENT_HOST_PUBLIC_ADMISSION_KEYS')
    ep=admission['episode']
    need(type(ep) is dict and set(ep)==set('repository branch run_id run_attempt workflow_commit'.split())
         and ep['repository']=='theislampill/IMPLEMENTAUDIT.md' and ep['branch']==branch
         and type(ep['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',ep['run_id'])
         and type(ep['run_attempt']) is int and ep['run_attempt']==1
         and type(ep['workflow_commit']) is str and re.fullmatch('[0-9a-f]{40}',ep['workflow_commit']),
         'G2_CURRENT_HOST_PUBLIC_EPISODE')
    selected=target_host(host)
    need(hex64(pin) and selected==SELECTED_HOST,'G2_CURRENT_HOST_PUBLIC_TARGET')
    expected=dict(schema='dg16.current-host-request-admission.v1',request_sha256=pin,
        selected_host_sha256=E.sha(E.encode(selected)),host_sha256=E.sha(E.encode(host)),
        boot_identity_sha256=host['boot_identity_sha256'],credentials_sha256=E.sha(E.encode(host['credentials'])),
        episode=ep,source_bindings=bindings,qualified=False)
    need(E.encode(admission)==E.encode(expected),'G2_CURRENT_HOST_PUBLIC_ADMISSION_BINDING')
    return admission
