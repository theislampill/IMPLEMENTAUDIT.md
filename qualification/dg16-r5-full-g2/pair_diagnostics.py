"""Closed causal observations for the adapter; never an acceptance receipt."""
import hashlib
import json
import traceback

PHASES = ('STARTED', 'ORDINARY_NODE', 'SOURCE_CHECK', 'OWNER_LOAD',
          'ORDINARY_INVENTORY', 'FULL_POLICY_PREFLIGHT', 'REPORT_RUNTIME_PREFLIGHT', 'MAPPING', 'PREFLIGHT_CURRENTNESS', 'PLAN_PREFLIGHT',
          'PROCESS_PROFILE', 'LEGACY_CAPTURE', 'LEGACY_DECLARED_ARTIFACT_CAPTURE', 'LEGACY_EXIT_STATUS',
          'DAG_CAPTURE', 'DAG_DECLARED_ARTIFACT_CAPTURE', 'RAW_COMPARE',
          'CLOSING', 'COMPLETE', 'RECEIVE_OPEN', 'RECEIVE_MAPPING',
          'RECEIVE_CURRENTNESS', 'RECEIVE_CAPTURES', 'RECEIVE_RAW_COMPARE',
          'RECEIVE_FULL_RELATION', 'RECEIVE_CLOSING', 'RECEIVE_COMPLETE')
ERRORS = ('AssertionError', 'RuntimeError', 'ValueError', 'OSError', 'TimeoutError',
          'WorkGraphError', 'ContinuityTransportError', 'FileNotFoundError',
          'PermissionError', 'KeyboardInterrupt', 'SystemExit', 'OTHER')
FLAGS = ('registered_physical_equality', 'exact_registry_reassembly')
REFUSAL_CODES = ('ADAPTER_MEMBER_CHANGED', 'ADAPTER_MEMBER_SHAPE', 'ATTEMPT_COUNT', 'BUILD_CHECKSUM_ROLE_ORDER', 'BUILD_DECLARED_SLOT_POPULATION', 'BUILD_DISTINCT_ALLOCATION_ROLES', 'BUILD_MEMBER_ORDER', 'BUILD_ROOT_ROLE', 'CANONICAL_ROLE_ENCODING', 'CANONICAL_ROLE_POPULATION', 'CAPTURE_DIGEST', 'CAPTURE_NODE_POPULATION', 'CAPTURE_NODE_STATUS', 'CAPTURE_RESULT_SCHEMA', 'CLOSING_EXTERNAL_CAPTURE_CHANGED', 'CLOSING_FINAL_CURRENTNESS', 'CLOSING_OPEN_CURRENTNESS', 'CLOSING_ORDINARY_PROVIDER_CHANGED', 'CLOSING_PATH', 'CLOSING_PROOF_BINDING', 'CLOSING_RECEIVER_RECORD_CHANGED', 'CLOSING_RECEIVING_OR_ADOPTION_CHANGED', 'CLOSING_SEALED_CAPTURE_CHANGED', 'CLOSING_SOURCE_RUNTIME_CHANGED', 'CLOSING_UNSEALED_WORKSPACE', 'COMBINED_ROUTE_CAPTURE_BOUND', 'COMPOSITION_CLOSURE', 'COMPOSITION_COMMAND', 'COMPOSITION_FIELDS', 'COMPOSITION_MEMBER_BINDING', 'COMPOSITION_MEMBER_FIELDS', 'COMPOSITION_MEMBER_POPULATION', 'COMPOSITION_POPULATION', 'COMPOSITION_REPOSITORY_ROLE', 'COMPOSITION_SOURCE_COUPLING', 'COMPOSITION_SOURCE_OR_AUTHORITY', 'COMPOSITION_SOURCE_ROLE', 'COMPOSITION_STARTUP_OR_COUPLING', 'D48_CAPTURE_ENCODING', 'D48_CAPTURE_FIELDS', 'D48_DECLARED_SLOT_POPULATION', 'D48_TRANSACTION_COUPLING', 'D48_TRANSACTION_ROLE', 'DECLARED_ARTIFACTS_CHANGED_DURING_RELATION', 'DECLARED_UNITTEST_RUNTIME_SOURCE_MISMATCH', 'DIAGNOSTIC_DURATION_DOMAIN', 'DISTRO_NODE_ONLY', 'DUPLICATE_CANONICAL_ROLE', 'DUPLICATE_JSON_KEY', 'DUPLICATE_PENDING_REPORT', 'EXACTLY_ONE_OPERATION_ROLE', 'EXACT_INDEPENDENT_CODE_REVIEW_REQUIRED', 'EXACT_PUBLIC_SOURCE_REQUIRED', 'EXACT_ROOT_POLICY_ADOPTION_REQUIRED', 'EXPLICIT_SINGLE_PROC_PROFILE_MISMATCH', 'EXTERNAL_AGGREGATE_READBACK', 'EXTERNAL_BUFFER_BINDING', 'EXTERNAL_BYTES_CHANGED', 'EXTERNAL_BYTE_BOUND', 'EXTERNAL_CAPTURE_ENVELOPE', 'EXTERNAL_CAPTURE_MANIFEST_BOUND', 'EXTERNAL_CAPTURE_POPULATION', 'EXTERNAL_COMBINED_BYTE_BOUND', 'EXTERNAL_CONTAINER_CHANGED', 'EXTERNAL_CONTAINER_MEMBER_KIND', 'EXTERNAL_CONTAINER_POPULATION', 'EXTERNAL_DIRECTORY_CHANGED', 'EXTERNAL_DIRECTORY_OWNER', 'EXTERNAL_ENVELOPE_CHANGED', 'EXTERNAL_FILE_CHANGED', 'EXTERNAL_FILE_KIND_OR_OWNER', 'EXTERNAL_MANIFEST_BOUND', 'EXTERNAL_NAMED_MEMBER_CHANGED', 'EXTERNAL_NAMESPACE_BOUND', 'EXTERNAL_ORIGINAL_CHANGED_DURING_CAPTURE', 'EXTERNAL_PHYSICAL_OR_BYTE_READBACK', 'EXTERNAL_REPORT_READBACK', 'EXTERNAL_ROLE_BINDING', 'EXTERNAL_ROOT_CHANGED', 'FINAL_RECEIVING_CURRENTNESS', 'FULL_CAPTURE_CHANGED_DURING_RELATION', 'FULL_DAG_NODE_TERMINALS', 'FULL_NODE_POPULATION', 'FULL_POLICY_OR_INPUT_BINDING', 'FULL_POLICY_SOURCE', 'FULL_POPULATION_NOT_COMPLETE', 'FULL_PUBLIC_PROOF_BOUND', 'FULL_RECEIVER_CAPTURE_REBOUND', 'FULL_RECEIVER_CLOSING_CURRENTNESS', 'FULL_RECEIVER_OPEN_CURRENTNESS', 'FULL_ROUTE_ACTUAL_TRACE', 'FULL_ROUTE_COMMAND', 'FULL_ROUTE_MODE', 'FULL_STREAM_RAW_BINDING', 'FULL_WHOLE_FIELDS_OR_CURRENTNESS', 'FULL_WHOLE_SOURCE_OR_COMMAND', 'INDEPENDENT_ROUTES_SHARE_PENDING_ALLOCATION', 'INSTALL_DECLARED_ROLE', 'MAINTAINED_OWNER_CHANGED', 'MATERIALIZATION_ACTUAL_COMMAND', 'MATERIALIZATION_COMMAND_POPULATION', 'MATERIALIZATION_HEAD_READBACK', 'MATERIALIZATION_MANIFEST_SOURCE', 'MATERIALIZATION_RECORD', 'MATERIALIZATION_SOURCE_BINDING', 'MATERIALIZED_COMPLETE_POPULATION', 'MATERIALIZED_SOURCE_BYTES_OR_MODE', 'NONFINITE_JSON', 'NO_REPEAT_EXTERNAL_CAPTURE', 'NO_REPEAT_PUBLIC_SUMMARY', 'NO_REPEAT_RECEIVING', 'ORDINARY_INTERPRETER_SELECTION', 'ORDINARY_PROVIDER_AGGREGATE', 'ORDINARY_PROVIDER_CHANGED', 'ORDINARY_PROVIDER_FILE_BOUND', 'ORDINARY_PROVIDER_KIND', 'ORDINARY_PROVIDER_OWNERSHIP', 'ORDINARY_PROVIDER_ROOT', 'ORDINARY_PROVIDER_ROOT_CHANGED', 'ORDINARY_TOOLCHAIN_CHANGED_AFTER_OPERATION', 'ORDINARY_TOOLCHAIN_CHANGED_AFTER_RECEIVE', 'ORDINARY_TOOLCHAIN_CHANGED_BEFORE_RECEIVE', 'ORDINARY_TOOL_MISSING', 'PENDING_ACTION_ROLE', 'PENDING_ARTIFACT_ROOT_ROLE', 'PENDING_ATOMIC_DELIVERY_VERSION', 'PENDING_ATOMIC_RESIDUE_POPULATION', 'PENDING_ATOMIC_REVISION', 'PENDING_ATOMIC_SUCCESSOR_BYTES', 'PENDING_ATOMIC_UNRELATED_FIELD', 'PENDING_AUXILIARY_POPULATION', 'PENDING_BEFORE_REPLACE_PREIMAGE', 'PENDING_BINDING_STORE', 'PENDING_BIND_OUTPUT', 'PENDING_COMMAND_CONTEXT', 'PENDING_COMMAND_PATH_BINDING', 'PENDING_COMMAND_SHAPE', 'PENDING_CONSTRUCTED_BINDING', 'PENDING_CONTROL_COUNT', 'PENDING_CONTROL_POPULATION', 'PENDING_CRASH_OPERAND', 'PENDING_DURABILITY_REPORT', 'PENDING_DURATION_DOMAIN', 'PENDING_FIRST_INITIALIZATION', 'PENDING_LOADER_SELECTION', 'PENDING_NORMALIZED_NAMESPACE', 'PENDING_PHYSICAL_DESCRIPTOR_TYPE', 'PENDING_PHYSICAL_ENCODING', 'PENDING_PHYSICAL_FIELDS', 'PENDING_PHYSICAL_IDENTITY_ALIAS', 'PENDING_PHYSICAL_KIND', 'PENDING_PHYSICAL_NAMESPACE', 'PENDING_PHYSICAL_NUMBERS', 'PENDING_PHYSICAL_PREIMAGE_ABSENT', 'PENDING_PHYSICAL_RAW_DIGEST', 'PENDING_PHYSICAL_ROW', 'PENDING_PHYSICAL_UNBOUND_FILE', 'PENDING_PREIMAGE_BINDING', 'PENDING_PREIMAGE_NAMESPACE', 'PENDING_PROCESS_COUNT', 'PENDING_PROCESS_FIELDS_OR_ENCODING', 'PENDING_PROCESS_POPULATION', 'PENDING_READONLY_PHYSICAL_ASSERTION', 'PENDING_REPORT_FIELDS_SOURCE_OR_AUTHORITY', 'PENDING_REPORT_FILE_BINDING', 'PENDING_REPORT_NOT_COMPLETE', 'PENDING_REPORT_POPULATION', 'PENDING_REPORT_RAW_BINDING', 'PENDING_SCRIPT_OR_EXIT', 'PENDING_SECOND_BINDING', 'PENDING_STDOUT_JSON_ENCODING', 'PENDING_STORE_ABSENCE_ROLE', 'PENDING_STREAM_COPY_BINDING', 'PENDING_TRANSCRIPT_REFERENCE', 'PENDING_WORKER_EXIT', 'PENDING_WORKER_ROLE', 'POLICY_DECISION_POPULATION', 'POLICY_RECORD_BOUND', 'POLICY_RECORD_DUPLICATE_KEY', 'POLICY_RECORD_NONFINITE', 'PRIVATE_BYTES_CHANGED', 'PRIVATE_FILE_CHANGED', 'PRIVATE_FILE_SHAPE', 'PRIVATE_JSON_SHAPE', 'PRIVATE_RELATION_METADATA_BOUND', 'PROFILE_ACTUAL_SOURCE_PIN', 'PROFILE_FROZEN_SOURCE_PIN', 'PROJECTION_COMPARISON_BOUND', 'PROJECTION_KEY_TYPE', 'PROJECTION_VALUE_TYPE', 'PUBLIC_ADOPTION_READBACK', 'PUBLIC_OPERATION_BOUND', 'PUBLIC_PROOF_BYTE_BOUND', 'PUBLIC_PROOF_BYTE_OFFSET', 'PUBLIC_PROOF_DESCRIPTOR', 'PUBLIC_PROOF_EQUALITY_DIGEST', 'PUBLIC_PROOF_FIXED_FIELDS', 'PUBLIC_PROOF_OVERALL_EQUALITY', 'PUBLIC_PROOF_RELATION', 'PUBLIC_PROOF_REPORT_COUNTS', 'PUBLIC_PROOF_REPORT_POPULATION', 'PUBLIC_PROOF_SCOPE_POPULATION', 'PUBLIC_PROOF_WITNESS', 'RAW_COMPARISON_EXIT', 'RAW_COMPARISON_EXIT_MISMATCH', 'RAW_COMPARISON_READBACK_CHANGED', 'RAW_RELATION_EQUALITY', 'RAW_RELATION_PREDICATES', 'RAW_RELATION_SCHEMA', 'RECEIVER_COMPLETE_MAPPING_READBACK', 'RECEIVER_STATUS', 'RECEIVE_CAPTURE_CHANGED', 'RECEIVE_CLOSING_CURRENTNESS', 'RECEIVE_CURRENTNESS', 'RECEIVE_MODE', 'RECEIVE_PATH', 'RECEIVE_PLAN_PROFILE', 'RELATION_INPUT_BOUND', 'RELATION_INPUT_CHANGED', 'RELATION_INPUT_POPULATION', 'RELATION_PROFILE_SOURCE', 'RELATION_SOURCE_MANIFEST', 'RELATION_SOURCE_OR_RUNTIME_CHANGED', 'RELATION_STATIC_REPORT_POPULATION', 'RELOCATED_SOURCE_FALLBACK_FORBIDDEN', 'REPORT_DECLARED_COUNT', 'REPORT_DESCRIPTION_SEQUENCE', 'REPORT_DOTS_MISSING', 'REPORT_DOTS_POPULATION_OR_STATUS', 'REPORT_IDENTITY_SEQUENCE', 'REPORT_PROFILE_ORDER', 'REPORT_PROFILE_SCHEMA', 'REPORT_SLOT_MULTIPLICITY', 'REPORT_SLOT_POPULATION', 'REPORT_STATUS_COUNTS', 'REPORT_STATUS_POPULATION', 'REPORT_TEST_STATUS', 'REPORT_TIMER_FORMAT', 'REPORT_VERBOSITY', 'REPOSITORY_COST_ASSERTION', 'REPOSITORY_COST_COUNTER_DOMAIN', 'REPOSITORY_COST_FIELDS', 'REPOSITORY_COST_METRIC_FIELDS', 'REPOSITORY_COST_POPULATION', 'REPOSITORY_COST_SOURCE_OR_RESULT', 'RUNTIME_METADATA_BOUND', 'RUNTIME_METADATA_SHAPE', 'RUNTIME_PUBLIC_SHAPE', 'RUNTIME_SOURCE_BYTES_CHANGED', 'RUNTIME_SOURCE_CLOSING_MISMATCH', 'RUNTIME_SOURCE_OBSERVATION_REFUSED', 'RUNTIME_SOURCE_PHYSICAL_CHANGED', 'SOURCE_PACK_ALLOCATION_ROLE', 'SOURCE_PACK_SLOT_POPULATION', 'STDOUT_INPUT_PROFILE', 'TURN_ALLOCATION_COUPLING', 'TURN_CASE_PATH_ROLE', 'TURN_REPORT_CASE', 'TURN_REPORT_POPULATION', 'UNKNOWN_CANONICAL_ARTIFACT_REFERENCE', 'UNKNOWN_PENDING_COMMAND_PATH', 'UNKNOWN_PENDING_STDOUT_PATH', 'UNKNOWN_PENDING_STREAM_REFERENCE', 'UNSEALED_WORKSPACE_REMAINS', 'UNSUPPORTED_REPORT_STATUS', 'WHOLE_ELAPSED_DOMAIN', 'WHOLE_STDERR_BOUND')


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def fresh(role):
    assert role in ('execute', 'receive')
    return {'schema': 'dg16.full-pair-causal-observation.v1', 'role': role,
            'scope': 'UNSEALED_ADAPTER_PROGRESS_NOT_EXECUTION_OR_ACCEPTANCE',
            'phase': 'STARTED' if role == 'execute' else 'RECEIVE_OPEN',
            'last_completed': None, 'observed': {key: None for key in FLAGS}, 'failure': None}


def validate(value):
    assert type(value) is dict and set(value) == {'schema', 'role', 'scope', 'phase', 'last_completed', 'observed', 'failure'}
    assert value['schema'] == 'dg16.full-pair-causal-observation.v1' and value['role'] in ('execute', 'receive')
    assert value['scope'] == 'UNSEALED_ADAPTER_PROGRESS_NOT_EXECUTION_OR_ACCEPTANCE'
    assert value['phase'] in PHASES and (value['last_completed'] is None or value['last_completed'] in PHASES)
    assert set(value['observed']) == set(FLAGS)
    assert all(x is None or type(x) is bool for x in value['observed'].values())
    failure = value['failure']
    if failure is not None:
        assert set(failure) == {'exception_class', 'errno', 'refusal_code', 'private_message', 'private_trace', 'retained_prefix', 'retained_trace'}
        assert failure['exception_class'] in ERRORS
        assert failure['errno'] is None or type(failure['errno']) is int and 0 <= failure['errno'] <= 4096
        assert failure['refusal_code'] is None or failure['refusal_code'] in REFUSAL_CODES
        assert type(failure['retained_prefix']) is bool
        for name in ('private_message', 'private_trace', 'retained_trace'):
            row = failure[name]
            assert set(row) == {'bytes', 'sha256'} and type(row['bytes']) is int and row['bytes'] >= 0
            assert type(row['sha256']) is str and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256'])
        assert failure['retained_trace']['bytes'] <= 131072
    return value


FACT_COUNTS = ('declared_slots', 'header_matches', 'timer_lines', 'canonical_timer_lines', 'rule_lines',
               'unframed_canonical_timer_lines', 'unframed_without_rule_line', 'unframed_without_blank_status_tail')
FACT_INDICATIONS = ('FRAMED_REPORTS_FEWER_THAN_DECLARED', 'FRAMED_REPORTS_MORE_THAN_DECLARED',
                    'CANONICAL_TIMER_LINE_OUTSIDE_FRAME', 'NONCANONICAL_TIMER_LINE', 'RULE_LINES_EXCEED_FRAMED_REPORTS')


def validate_facts(value):
    """Closed private count/shape record of one refused report multiplicity; never public."""
    assert type(value) is dict and set(value) == {'schema', 'scope', 'stream', 'indications', *FACT_COUNTS}
    assert value['schema'] == 'dg16.report-slot-multiplicity-private-facts.v1'
    assert value['scope'] == 'PRIVATE_COUNT_AND_SHAPE_ONLY_NOT_REPORT_EXECUTION_OR_ACCEPTANCE'
    row = value['stream']
    assert type(row) is dict and set(row) == {'bytes', 'sha256'} and type(row['bytes']) is int and 0 <= row['bytes'] <= 134217728
    assert type(row['sha256']) is str and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256'])
    assert all(type(value[key]) is int and 0 <= value[key] <= 134217728 for key in FACT_COUNTS)
    declared, headers, timers, canonical = (value[key] for key in FACT_COUNTS[:4])
    assert headers <= canonical <= timers and headers <= value['rule_lines'] and not headers == declared == timers
    assert value['unframed_canonical_timer_lines'] == canonical - headers
    assert max(value['unframed_without_rule_line'], value['unframed_without_blank_status_tail']) <= canonical - headers
    assert value['indications'] == [name for name, present in zip(FACT_INDICATIONS, (
        headers < declared, headers > declared, canonical > headers, timers > canonical, value['rule_lines'] > headers)) if present]
    return value


def save(directory, value):
    raw = (json.dumps(validate(value), sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    assert len(raw) <= 4096
    path = directory / (value['role'].upper() + '_PROGRESS.json')
    temporary = path.with_suffix('.next')
    with temporary.open('xb') as stream:
        stream.write(raw)
        stream.flush()
    temporary.replace(path)


def advance(directory, value, phase):
    assert phase in PHASES
    value['last_completed'] = value['phase']
    value['phase'] = phase
    save(directory, value)


def failed(directory, value, error):
    message = str(error).encode('utf-8', 'backslashreplace')
    trace = traceback.format_exc().encode('utf-8', 'backslashreplace')
    retained = trace[:131072]
    name = type(error).__name__
    number = getattr(error, 'errno', None)
    if type(number) is not int or not 0 <= number <= 4096:
        number = None
    value['failure'] = {'exception_class': name if name in ERRORS else 'OTHER', 'errno': number,
                        'refusal_code': str(error) if str(error) in REFUSAL_CODES else None,
                        'private_message': desc(message), 'private_trace': desc(trace),
                        'retained_prefix': len(trace) != len(retained), 'retained_trace': desc(retained)}
    path = directory / (value['role'].lower() + '-failure.txt')
    with path.open('xb') as stream:
        stream.write(retained)
    save(directory, value)
    facts = getattr(error, 'private_facts', None)
    if facts is not None and value['role'] == 'receive' and value['failure']['refusal_code'] == 'REPORT_SLOT_MULTIPLICITY':
        # Supplementary and private. The recorded primary failure above is already complete and is never altered.
        try:
            raw = (json.dumps(validate_facts(facts), sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
            assert len(raw) <= 2048
            with (directory / 'receive-report-slot-multiplicity.json').open('xb') as stream:
                stream.write(raw)
        except (AssertionError, ValueError, KeyError, TypeError, OSError):
            pass
