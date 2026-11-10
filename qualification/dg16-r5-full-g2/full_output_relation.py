#!/usr/bin/env python3
"""Proposed source-bound functional output relations; no execution authority.

The source/registry/runtime/invocation profile must be bound by the caller before
this pure relation is used. Report position is a declared functional output
slot, not an assertion that a byte has authenticated interpreter provenance.
Only declared temporal operands are replaced; all surrounding bytes survive.
"""
import hashlib
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
