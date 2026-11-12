#!/usr/bin/env python3
"""Proposed source-bound functional output relations; no execution authority.

The source/registry/runtime/invocation profile must be bound by the caller before
this pure relation is used. Report position is a declared functional output
slot, not an assertion that a byte has authenticated interpreter provenance.
Only declared temporal operands are replaced; all surrounding bytes survive.
"""
import hashlib
import os
import base64
import re


class Refusal(ValueError):
    pass


def demand(condition, code):
    if not condition:
        raise Refusal(code)


def descriptor(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


HEADER = re.compile(rb'(?m)^-{70}\nRan ([0-9]+) test(s?) in ([0-9]+\.[0-9]{3})s\n\n([^\n]*)\n')
TIMER_LINE = re.compile(rb'(?m)^Ran [^\n]*test[^\n]* in [^\n]*s$')
STATUS = re.compile(rb'OK(?: \((?:skipped=[1-9][0-9]*(?:, expected failures=[1-9][0-9]*)?|expected failures=[1-9][0-9]*)\))?')
VERBOSE_ID = re.compile(rb'(?m)^test[^ \n]+ \([^\n()]+\)')


def successful_status(raw):
    demand(STATUS.fullmatch(raw) is not None, 'UNSUPPORTED_REPORT_STATUS')
    skipped = re.search(rb'skipped=([0-9]+)', raw)
    expected = re.search(rb'expected failures=([0-9]+)', raw)
    return int(skipped.group(1)) if skipped else 0, int(expected.group(1)) if expected else 0


def progress(segment, slot, skipped, expected):
    n = slot['test_count']
    demand(type(n) is int and n > 0 and len(slot['tests']) == n, 'REPORT_SLOT_POPULATION')
    if slot['verbosity'] == 1:
        found = re.search(rb'(?:^|\n)([.sx]+)\n\Z', segment)
        demand(found is not None, 'REPORT_DOTS_MISSING')
        marks = found.group(1)
        demand(len(marks) == n and marks.count(b's') == skipped and marks.count(b'x') == expected,
               'REPORT_DOTS_POPULATION_OR_STATUS')
        return
    demand(slot['verbosity'] == 2, 'REPORT_VERBOSITY')
    actual_ids = [m.group(0).decode('utf-8') for m in VERBOSE_ID.finditer(segment)]
    demand(actual_ids == [t['printed_identity'] for t in slot['tests']], 'REPORT_IDENTITY_SEQUENCE')
    positions = []
    for test in slot['tests']:
        name = test['printed_identity']
        if test['description_first_line']:
            name += '\n' + test['description_first_line']
        token = (name + ' ... ').encode()
        start = segment.find(token, positions[-1][1] if positions else 0)
        demand(start >= 0, 'REPORT_DESCRIPTION_SEQUENCE')
        positions.append((start, start + len(token)))
    statuses = []
    for i, (_, end) in enumerate(positions):
        tail = segment[end:positions[i + 1][0] if i + 1 < len(positions) else len(segment)]
        # Source-bound diagnostics may be emitted during a test. They remain
        # byte-exact; only the terminal runner status is recognized here.
        lines = tail.rstrip(b'\n').split(b'\n')
        final = lines[-1]
        demand(final == b'ok' or final == b'expected failure' or
               re.fullmatch(rb"skipped '[^\n]*'", final) is not None,
               'REPORT_TEST_STATUS')
        statuses.append(final)
    demand(sum(s.startswith(b'skipped ') for s in statuses) == skipped and
           statuses.count(b'expected failure') == expected, 'REPORT_STATUS_COUNTS')


def report_elapsed_relation(raw, profile):
    """Return exact bytes modulo the adopted successful report elapsed fields.

    No whole output is inferred from counts. All slots must be present in the
    source-derived order, with complete progress identities/counts and statuses,
    before any replacement is performed. Raw duration values remain in the
    returned private observations and in the original sealed raw streams.
    """
    demand(type(raw) is bytes and len(raw) <= 128 * 1024 * 1024, 'WHOLE_STDERR_BOUND')
    demand(type(profile) is dict and profile.get('schema') == 'dg16.full-source-report-slots.proposed.v1',
           'REPORT_PROFILE_SCHEMA')
    slots = profile['slots']
    demand(len(slots) == profile['slot_count'] and all(s['ordinal'] == i for i, s in enumerate(slots)),
           'REPORT_PROFILE_ORDER')
    reports = list(HEADER.finditer(raw))
    demand(len(reports) == len(slots) == len(list(TIMER_LINE.finditer(raw))), 'REPORT_SLOT_MULTIPLICITY')
    edits, observations, previous_end = [], [], 0
    for slot, found in zip(slots, reports):
        count = int(found.group(1))
        demand(found.group(1) == str(count).encode() and count == slot['test_count'] and
               found.group(2) == (b'' if count == 1 else b's'), 'REPORT_DECLARED_COUNT')
        temporal = found.group(3)
        whole, fractional = temporal.split(b'.')
        demand(whole == str(int(whole)).encode(), 'REPORT_TIMER_FORMAT')
        milliseconds = int(whole) * 1000 + int(fractional)
        skipped, expected = successful_status(found.group(4))
        demand(skipped + expected <= count, 'REPORT_STATUS_POPULATION')
        progress(raw[previous_end:found.start()], slot, skipped, expected)
        observations.append({'ordinal': slot['ordinal'], 'test_count': count,
                             'elapsed_milliseconds': milliseconds,
                             'skipped': skipped, 'expected_failures': expected,
                             'raw_report': descriptor(raw[found.start():found.end()])})
        edits.append((found.start(3), found.end(3), b'<DECLARED_UNITTEST_DIAGNOSTIC_SECONDS>'))
        previous_end = found.end()
    normalized = raw
    for start, end, replacement in reversed(edits):
        normalized = normalized[:start] + replacement + normalized[end:]
    return normalized, observations

"""Source-bound class applicability; no test/native/permission authority."""

def required_report_live_flags(profile):
    return sorted({g['skip_guard']['environment_name'] for s in profile['slots']
                   for g in s.get('source_class_groups', []) if g['skip_guard'] is not None})


def produce_report_environment(profile, actual_pair_environment, plan_sha256):
    """Data only; the fixed actual pair owner performs the private write once."""
    demand(type(actual_pair_environment) is dict and all(type(k) is type(v) is str for k, v in actual_pair_environment.items()),
           'REPORT_ACTUAL_PAIR_ENVIRONMENT_REQUIRED')
    flags = required_report_live_flags(profile)
    demand(all(re.fullmatch('R0035_[A-Z0-9_]+_LIVE', flag) and flag not in actual_pair_environment for flag in flags),
           'REPORT_DEFAULT_CLASS_APPLICABILITY_NOT_ESTABLISHED')
    demand(type(plan_sha256) is str and re.fullmatch('[0-9a-f]{64}', plan_sha256), 'REPORT_PAIR_PLAN_PIN')
    base = hashlib.sha256(b'\0'.join(os.fsencode(k) + b'=' + os.fsencode(v)
                                   for k, v in sorted(actual_pair_environment.items()))).hexdigest()
    return dict(schema='dg16.fixed-pair-default-report-environment.v1', authority='NONE',
                source_commit=profile['source_commit'], source_tree=profile['source_tree'],
                base_environment_sha256=base, plan_sha256=plan_sha256, absent_live_flags=flags,
                original_awards=[])


def _frozen_class_environment(profile, environment_record, child_environment, captured_environment):
    flags = required_report_live_flags(profile)
    if not flags:
        return None
    demand(type(environment_record) is dict and set(environment_record) ==
           {'schema', 'authority', 'source_commit', 'source_tree', 'base_environment_sha256', 'plan_sha256', 'absent_live_flags', 'original_awards'},
           'REPORT_ACTUAL_PAIR_ENVIRONMENT_RECORD_REQUIRED')
    demand(environment_record['schema'] == 'dg16.fixed-pair-default-report-environment.v1' and
           environment_record['authority'] == 'NONE' and environment_record['source_commit'] == profile['source_commit'] and
           environment_record['source_tree'] == profile['source_tree'] and environment_record['absent_live_flags'] == flags and
           environment_record['original_awards'] == [], 'REPORT_PAIR_ENVIRONMENT_RECORD_SCOPE')
    demand(type(environment_record['plan_sha256']) is str and re.fullmatch('[0-9a-f]{64}', environment_record['plan_sha256']),
           'REPORT_PAIR_PLAN_PIN')
    demand(type(child_environment) is dict and set(child_environment) ==
           {'schema', 'base_environment_sha256', 'actual_environment_sha256', 'overrides'} and
           child_environment['schema'] == 'implementaudit.verifier-child-environment.v1' and type(captured_environment) is dict,
           'REPORT_MAINTAINED_CHILD_ENVIRONMENT_REQUIRED')
    overrides = child_environment['overrides']
    demand(type(overrides) is dict and all(type(k) is type(v) is str for k, v in overrides.items()), 'REPORT_CHILD_OVERRIDES_SHAPE')
    demand(environment_record['base_environment_sha256'] == child_environment['base_environment_sha256'] and
           type(child_environment['actual_environment_sha256']) is str and
           re.fullmatch('[0-9a-f]{64}', child_environment['actual_environment_sha256']) and
           child_environment['actual_environment_sha256'] == captured_environment.get('inherited_environment_sha256'),
           'REPORT_FROZEN_CAPTURE_ENVIRONMENT_JOIN')
    demand(not (set(flags) & set(overrides)), 'REPORT_LIVE_FLAG_OVERRIDE_REFUSED')
    return dict(base_environment_sha256=child_environment['base_environment_sha256'],
                actual_child_environment_sha256=child_environment['actual_environment_sha256'],
                pair_plan_sha256=environment_record['plan_sha256'], absent_live_flags=flags,
                applicability='UNEXECUTED_CLASSES_UNDER_FROZEN_DEFAULT_INVOCATION')


def _declared_report_plan(slot, profile, eligibility):
    groups = slot.get('source_class_groups')
    if groups is None:
        return None
    demand(type(groups) is list and groups and type(slot['test_count']) is int and
           slot['test_count'] > 0 and len(slot['tests']) == slot['test_count'], 'REPORT_DECLARED_GROUP_POPULATION')
    items, unexecuted, offset = [], [], 0
    for group in groups:
        demand(type(group) is dict and set(group) == {'class_identity', 'first_test', 'test_count', 'skip_guard'} and
               group['first_test'] == offset and type(group['test_count']) is int and group['test_count'] > 0,
               'REPORT_DECLARED_GROUP_ORDER')
        end = offset + group['test_count']
        demand(end <= slot['test_count'] and all(t['id'].rsplit('.', 1)[0] == group['class_identity'] for t in slot['tests'][offset:end]),
               'REPORT_DECLARED_CLASS_IDENTITIES')
        guard = group['skip_guard']
        if guard is None:
            items.extend(dict(kind='TEST', test_ordinal=i, test=slot['tests'][i]) for i in range(offset, end))
        else:
            demand(eligibility is not None and guard['enabled_value'] == '1' and
                   guard['disabled_requirement'] == 'ABSENT_IN_FROZEN_ACTUAL_CHILD_ENVIRONMENT' and
                   guard['environment_name'] in eligibility['absent_live_flags'], 'REPORT_CLASS_SKIP_WITHOUT_ACTUAL_ELIGIBILITY')
            source = profile['source_closure'].get(guard['source_path'])
            demand(type(source) is dict and {k: source[k] for k in ('bytes', 'sha256')} == guard['source'],
                   'REPORT_CLASS_GUARD_SOURCE_PIN')
            demand(type(guard['reason']) is str and 0 < len(guard['reason']) <= 1024, 'REPORT_CLASS_SKIP_REASON')
            item = dict(kind='CLASS_SKIP', class_identity=group['class_identity'], reason=guard['reason'],
                        declared_tests=slot['tests'][offset:end], declared_count=group['test_count'])
            items.append(item)
            unexecuted.append(dict(class_identity=group['class_identity'], declared_count=group['test_count'],
                                   declared_test_ids=[t['id'] for t in slot['tests'][offset:end]],
                                   class_attribution='SOURCE_DERIVED_UNDER_BOUND_ENVIRONMENT',source_guard_reason=guard['reason'],
                                   observed_runner_form='ONE_SKIP_MARKER' if slot['verbosity']==1 else 'VERBOSE_SETUPCLASS_SKIP',
                                   printed_reason_observed=slot['verbosity']==2,
                                   applicability='NOT_EXECUTED; NO_ORIGINAL_NATIVE_OR_ACCEPTANCE_CREDIT'))
        offset = end
    demand(offset == slot['test_count'], 'REPORT_DECLARED_GROUP_COVERAGE')
    ran = sum(item['kind'] == 'TEST' for item in items)
    skipped_classes = sum(item['kind'] == 'CLASS_SKIP' for item in items)
    demand(ran + sum(g['declared_count'] for g in unexecuted) == slot['test_count'], 'REPORT_DECLARED_POPULATION_ACCOUNTING')
    return dict(items=items, ran=ran, skipped_classes=skipped_classes, unexecuted=unexecuted)


def _source_inline_fragments(slot, profile):
    fragments = {}
    for row in slot.get('source_inline_stderr', []):
        demand(type(row) is dict and set(row) == {'test_ordinal', 'test_id', 'source_path', 'source', 'bytes', 'sha256', 'body_base64'},
               'REPORT_INLINE_SOURCE_FIELDS')
        i = row['test_ordinal']
        demand(type(i) is int and 0 <= i < slot['test_count'] and row['test_id'] == slot['tests'][i]['id'] and i not in fragments,
               'REPORT_INLINE_SOURCE_TEST_IDENTITY')
        source = profile['source_closure'].get(row['source_path'])
        demand(type(source) is dict and {k: source[k] for k in ('bytes', 'sha256')} == row['source'], 'REPORT_INLINE_SOURCE_PIN')
        try:
            body = base64.b64decode(row['body_base64'], validate=True)
        except (ValueError, TypeError):
            demand(False, 'REPORT_INLINE_SOURCE_ENCODING')
        demand(0 < len(body) <= 512 and b'\n' not in body and b'\r' not in body and descriptor(body) ==
               {k: row[k] for k in ('bytes', 'sha256')}, 'REPORT_INLINE_SOURCE_BODY')
        fragments[i] = body
    return fragments


def _applicable_progress(segment, slot, plan, skipped, expected, profile):
    if plan is None:
        progress(segment, slot, skipped, expected)
        return []
    method_skipped = skipped - plan['skipped_classes']
    demand(method_skipped >= 0 and method_skipped + expected <= plan['ran'], 'REPORT_STATUS_POPULATION')
    fragments = _source_inline_fragments(slot, profile)
    inline_observed = []
    if slot['verbosity'] == 1:
        found = re.search(rb'(?:^|\n)([^\n]*)\n\Z', segment)
        demand(found is not None, 'REPORT_DOTS_MISSING')
        raw = found.group(1); position = 0; marks = []
        for item in plan['items']:
            if item['kind'] == 'CLASS_SKIP':
                demand(raw[position:position + 1] == b's', 'REPORT_SOURCE_CLASS_SKIP_MARK')
                marks.append(b's'); position += 1
                continue
            ordinal = item['test_ordinal']; body = fragments.get(ordinal)
            emitted = body is not None and raw[position:position + len(body)] == body
            if emitted:
                inline_observed.append(dict(test_ordinal=ordinal, fragment=descriptor(body)))
                position += len(body)
            mark = raw[position:position + 1]
            demand(mark in (b'.', b's', b'x'), 'REPORT_SOURCE_PROGRESS_MARK')
            demand(body is None or emitted or mark == b's', 'REPORT_INLINE_SOURCE_FRAGMENT_MISSING')
            marks.append(mark); position += 1
        demand(position == len(raw) and len(marks) == plan['ran'] + plan['skipped_classes'] and
               marks.count(b's') == skipped and marks.count(b'x') == expected, 'REPORT_DOTS_POPULATION_OR_STATUS')
        return inline_observed
    demand(slot['verbosity'] == 2 and not fragments, 'REPORT_VERBOSITY_OR_INLINE_PROFILE')
    actual_ids = [m.group(0).decode('utf8') for m in re.finditer(rb'(?m)^(?:test[^ \n]+|setUpClass) \([^\n()]+\)', segment)]
    identities = [item['test']['printed_identity'] if item['kind'] == 'TEST' else
                  'setUpClass (' + item['class_identity'] + ')' for item in plan['items']]
    demand(actual_ids == identities, 'REPORT_IDENTITY_SEQUENCE')
    positions = []
    for item, identity in zip(plan['items'], identities):
        if item['kind'] == 'TEST' and item['test']['description_first_line']:
            identity += '\n' + item['test']['description_first_line']
        token = (identity + ' ... ').encode()
        start = segment.find(token, positions[-1][1] if positions else 0)
        demand(start >= 0, 'REPORT_DESCRIPTION_SEQUENCE'); positions.append((start, start + len(token)))
    statuses = []
    for i, (item, (_, end)) in enumerate(zip(plan['items'], positions)):
        tail = segment[end:positions[i + 1][0] if i + 1 < len(positions) else len(segment)]
        final = tail.rstrip(b'\n').split(b'\n')[-1]
        if item['kind'] == 'CLASS_SKIP':
            demand(final == ('skipped ' + repr(item['reason'])).encode(), 'REPORT_SOURCE_CLASS_SKIP_REASON')
        else:
            demand(final in (b'ok', b'expected failure') or re.fullmatch(rb"skipped '[^\n]*'", final) is not None, 'REPORT_TEST_STATUS')
        statuses.append(final)
    demand(sum(x.startswith(b'skipped ') for x in statuses) == skipped and statuses.count(b'expected failure') == expected,
           'REPORT_STATUS_COUNTS')
    return inline_observed


def report_elapsed_relation(raw, profile, *, environment_record=None, child_environment=None, captured_environment=None):
    """Only elapsed fields change; declared, executed and skipped scopes differ."""
    demand(type(raw) is bytes and len(raw) <= 128 * 1024 * 1024, 'WHOLE_STDERR_BOUND')
    demand(type(profile) is dict and profile.get('schema') == 'dg16.full-source-report-slots.proposed.v1', 'REPORT_PROFILE_SCHEMA')
    slots = profile['slots']
    demand(len(slots) == profile['slot_count'] and all(s['ordinal'] == i for i, s in enumerate(slots)), 'REPORT_PROFILE_ORDER')
    eligibility = _frozen_class_environment(profile, environment_record, child_environment, captured_environment)
    reports = list(HEADER.finditer(raw))
    demand(len(reports) == len(slots) == len(list(TIMER_LINE.finditer(raw))), 'REPORT_SLOT_MULTIPLICITY')
    edits, observations, previous_end = [], [], 0
    for slot, found in zip(slots, reports):
        plan = _declared_report_plan(slot, profile, eligibility)
        count = int(found.group(1)); expected_ran = slot['test_count'] if plan is None else plan['ran']
        demand(found.group(1) == str(count).encode() and count == expected_ran and
               found.group(2) == (b'' if count == 1 else b's'), 'REPORT_DECLARED_COUNT')
        temporal = found.group(3); whole, fractional = temporal.split(b'.')
        demand(whole == str(int(whole)).encode(), 'REPORT_TIMER_FORMAT')
        milliseconds = int(whole) * 1000 + int(fractional)
        skipped, expected = successful_status(found.group(4))
        if plan is None:
            demand(skipped + expected <= count, 'REPORT_STATUS_POPULATION')
        inline = _applicable_progress(raw[previous_end:found.start()], slot, plan, skipped, expected, profile)
        observations.append(dict(ordinal=slot['ordinal'], test_count=count, declared_test_count=slot['test_count'],
                                 declared_class_unexecuted=[] if plan is None else plan['unexecuted'],
                                 observed_class_skip_markers=0 if plan is None else plan['skipped_classes'],
                                 observed_method_skip_events=skipped if plan is None else skipped-plan['skipped_classes'],
                                 elapsed_milliseconds=milliseconds, skipped=skipped, expected_failures=expected,
                                 inline_source_stderr=inline, frozen_environment_eligibility=eligibility,
                                 raw_report=descriptor(raw[found.start():found.end()])))
        edits.append((found.start(3), found.end(3), b'<DECLARED_UNITTEST_DIAGNOSTIC_SECONDS>'))
        previous_end = found.end()
    normalized = raw
    for start, end, replacement in reversed(edits):
        normalized = normalized[:start] + replacement + normalized[end:]
    return normalized, observations
