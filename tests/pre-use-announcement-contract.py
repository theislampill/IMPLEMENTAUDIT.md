#!/usr/bin/env python3
"""Source-contract regressions; these do not prove host/model conformance."""

from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import re
from pathlib import Path


SKILL = "skills/implementaudit/SKILL.md"
CHILD = "skills/implementaudit/references/child-agents.md"
TRANSCRIPT = "skills/implementaudit/references/transcript-contract.md"
REPORT = "skills/implementaudit/templates/child-agent-report.md"
FLAGS = (
    "VISIBLE_PRE_USE_ANNOUNCEMENT_REQUIRED=YES",
    "ORDINARY_CHILD_PRE_DISPATCH_ANNOUNCEMENT_REQUIRED=YES",
    "SKILL_PRE_USE_ANNOUNCEMENT_REQUIRED=YES",
    "GOVERNED_CHILD_LIFECYCLE_TELEMETRY_REQUIRED=YES",
    "PERIODIC_TOPOLOGY_IS_SUPPLEMENTAL_NOT_SUBSTITUTE=YES",
    "SILENT_CHILD_OR_SKILL_USE=CONFORMANCE_FAIL",
)
GOVERNED_PRELOAD_FIELDS = (
    "CHILD_TASK=<id>", "CHILD_TASK_KIND=GOVERNED_CHILD_SKILL",
    "CHILD_SKILL_SELECTED=<skill>", "STATUS=OPEN", "LOAD=UNVERIFIED",
)
ROLE_METHOD_FLAGS = (
    "GOVERNED_CHILD_ROLE_SELECTION != PROCEDURAL_SKILL_SELECTION",
    "GOVERNED_ROLE != PROCEDURAL_METHOD",
    "PROCEDURAL_SKILL_IS_NOT_GOVERNED_ADMISSION=YES",
    "PROCEDURAL_SKILL_MAY_AUGMENT_ADMITTED_GOVERNED_CHILD=YES",
    "PROCEDURAL_SKILL_MUST_NOT_BYPASS_GOVERNED_LIFECYCLE=YES",
    "INDEPENDENCE_REQUIREMENTS_SURVIVE_SKILL_COMPOSITION=YES",
    "ORDINARY_SKILL_USE_DOES_NOT_COUNT_AS_AUDIT_CHILD_USE=YES",
    "AUDIT_CHILD_USE_DOES_NOT_FORBID_APPLICABLE_ORDINARY_SKILLS=YES",
)
ROLE_METHOD_PARAGRAPHS = (
    "Governed role and procedural method selection are orthogonal and composable.",
    " ".join(ROLE_METHOD_FLAGS),
    "A governed child must first be lawfully admitted under its applicable actual package, transport, lifecycle, "
    "currentness, independence and authority gates. Ordinary procedural skill use is not governed admission, "
    "does not substitute for or bypass it, and never counts as audit-child use.",
    "Once admitted, a governed child may use applicable procedural skills inside that holon. "
    "The governed role does not forbid applicable ordinary skills.",
    "For each supporting procedural skill, the parent governor must visibly announce selection and purpose; "
    "the child must receive the actual acknowledgement before its own actual skill load and procedural use. "
    "Child-local commentary, silent nested use and retrospective acknowledgement are insufficient.",
    "A fresh audit-assess child receives its immutable digest-bound envelope and satisfies admission and "
    "fresh-context independence first, then selects and loads its own applicable methods. "
    "It must never inherit preparation context to obtain methods.",
    "Method composition preserves every governed lifecycle requirement, independence requirement and authority ceiling. "
    "It grants no mutation, currentness, result, lifecycle, release or closure authority.",
    "Loading an ordinary procedural method is not child delegation and does not relax "
    "CHILD_ROUTING=FORBIDDEN or CHILD_TO_CHILD_ROUTING=FORBIDDEN.",
    "Neither procedural method use nor governed child routing is required solely to demonstrate composition.",
    "Examples in principle only: verification in audit-assess; TDD or verification in audit-implement; "
    "debugging or verification in audit-andon. Applicability and existing authority ceilings control; "
    "these examples grant no audit-implement mutation permission and mandate no method or ceremonial child use.",
)


GENERIC_LOAD_CONTEXT = """This generic form is for independently required compaction or direct cognition
outside actual native delivery, when no native READY tuple exists. Actual full
selected skill LOAD and prospective visible parent acknowledgement are required
before bounded use. It grants no native delivery, host-stage, currentness, epoch,
recovery, lifecycle, mutation, release or closure authority and cannot release
actual native USE. Missing currentness, epoch or native qualification does not
block the independently required bounded entry."""
NATIVE_LOAD_CONTEXT = """This native form applies only to actual native delivery after independently
verified full selected skill LOAD. WORKER_TASK and LOAD_READY_SHA256 must bind
the true native worker and complete READY record. The generic form never
satisfies native readiness, liveness, ACK, same-worker USE or host-stage proof.
All existing native qualification, admission and result-authority gates remain
required in this context."""
NATIVE_TRANSCRIPT_LOAD_PREAMBLE = """A governed child route is user-visible only after the exact package gate,
resolver selection, and actual full child load have occurred. Follow the event form
in child-agents.md: one literal ini block, then its bounded named sentence.
The verified route event is separate from the earlier OPEN/LOAD=UNVERIFIED event:"""
NATIVE_TRANSCRIPT_FOLLOWING_OWNER = """The selected child is exactly one of `audit-state`, `audit-assess`,
`audit-implement`, or `audit-andon`, and the announced identity must equal the
resolved and loaded child. Child files merely being packaged or discoverable,
or governor reasoning producing similar words or conclusions, is not a route.
Those governor-only cases emit no selected-child announcement. Exact current
`NOT_REQUIRED` instead emits the explicit no-child projection:"""


def section(text: str, title: str, level: int = 2) -> str:
    # Use the same finite active-heading scan as the owner checks. An inert
    # comment/fence/quote heading cannot open or truncate an operative owner.
    text = text.replace("\r\n", "\n")
    headings = []
    procedural_prose_units(text, headings=headings)
    expected = "#" * level + " " + title
    starts = [line for line, value in headings if value == expected]
    assert len(starts) == 1, f"missing/duplicate section: {title}"
    start = starts[0]
    end = next((line for line, value in headings if line > start
                and len(value.split(" ", 1)[0]) <= level), len(text.splitlines()))
    return "".join(text.splitlines(keepends=True)[start + 1:end])


def require(text: str, phrase: str) -> None:
    assert " ".join(phrase.split()) in " ".join(text.split()), phrase


def block(text: str, rows: tuple[str, ...], *, language: str = "ini") -> None:
    blocks = [tuple(line.strip() for line in value.strip().splitlines())
              for value in re.findall(r"```" + re.escape(language) + r"\n(.*?)\n```", text, re.S)]
    assert rows in blocks, f"missing or reordered field block: {rows}"


def replace_phrase(text: str, old: str, new: str, *, fence_languages=('ini',)) -> str:
    return control_replace(text, old, new, count=0, flexible=True, fence_languages=fence_languages)


class QuotedParagraph:
    """Finite quote ownership shared by prose and native ini consumers."""

    def __init__(self) -> None:
        self.paragraph = False
        self.fence = None
        self.comment = False

    def consumes(self, line: str) -> bool:
        quote = re.match(r"^ {0,3}>[ \t]?(.*?)(?:\n)?$", line)
        if quote is None:
            self.fence, self.comment = None, False
            if not line.strip() or re.match(
                    r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|\d+[.)][ \t]+|`{3,}|~{3,}|<!--)", line):
                self.paragraph = False
            return self.paragraph
        content = quote[1]
        if self.fence is not None:
            closing = re.fullmatch(r" {0,3}(`{3,}|~{3,})[ \t]*", content)
            if closing and closing[1][0] == self.fence[0] and len(closing[1]) >= len(self.fence):
                self.fence = None
            self.paragraph = False
            return True
        if self.comment:
            if "-->" in content:
                self.comment = False
            self.paragraph = False
            return True
        if re.match(r"^ {0,3}<!--", content):
            self.comment = "-->" not in content
            self.paragraph = False
            return True
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", content)
        if marker:
            self.fence, self.paragraph = marker[1], False
            return True
        if not content.strip() or re.match(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|>)", content):
            self.paragraph = False
        elif not self.paragraph and re.match(r"^(?: {4}|\t)", content):
            self.paragraph = False
        else:
            self.paragraph = True
        return True


def procedural_prose_units(text: str, *, keep_markers: bool = False,
                          headings: list[tuple[int, str]] | None = None,
                          source_spans: list[tuple[int, int]] | None = None,
                          marker_spans: list[tuple[int, int] | None] | None = None,
                          fence_spans: list[dict] | None = None,
                          line_prefixes: list[tuple[int, int]] | None = None) -> tuple[tuple[str, str], ...]:
    # Only the new procedural clauses require active prose. Existing field
    # templates and custody checks keep their own fenced/quoted semantics.
    # Keep paragraph/numbered-item kinds and boundaries. Top-level indented
    # code is inert; contiguous numbered continuations remain prose. This is
    # the supported local grammar, not a general Markdown parser.
    units = []
    content = []
    content_spans = []
    kind = "paragraph"
    continuation_indent = 0
    current_marker = None

    def flush() -> None:
        nonlocal kind, continuation_indent, current_marker
        value = " ".join("".join(content).split())
        if value:
            units.append((kind, value))
            if source_spans is not None:
                source_spans.append((content_spans[0][0], content_spans[-1][1]))
            if marker_spans is not None:
                marker_spans.append(current_marker)
        content.clear()
        content_spans.clear()
        kind, continuation_indent = "paragraph", 0
        current_marker = None

    fence = None
    fence_record = None
    comment = False
    quote = QuotedParagraph()
    offset = 0  # Optional spans address the same LF-normalized source we scan.
    for line_number, line in enumerate(text.replace("\r\n", "\n").splitlines(keepends=True)):
        column = offset
        line_start = offset
        offset += len(line)
        if comment:
            end = line.find("-->")
            if end < 0:
                continue
            comment = False
            line = line[end + 3:]
            column += end + 3
        if fence is not None:
            closing = re.match(r"^ {0,3}(`{3,}|~{3,})[ \t]*(?:\n)?$", line)
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= len(fence):
                if fence_spans is not None:
                    fence_spans.append(dict(fence_record, body_end=column, end=offset,
                                            close_start=column + closing.start(1),
                                            close_end=column + closing.end(1)))
                fence = None
            continue
        if line_prefixes is not None:
            line_prefixes.append((line_start, column))
        if quote.consumes(line):
            flush()
            continue
        # An unquoted leading comment is an inert block boundary. Track it
        # before lazy quotation so its hidden headings/items stay hidden and
        # the real prose after its close remains visible. Inline comments
        # still split units below; they never splice a required clause.
        while re.match(r"^ {0,3}<!--", line):
            flush()
            end = line.find("-->", line.index("<!--") + 4)
            if end < 0:
                comment, line = True, ""
                break
            line = line[end + 3:]
            column += end + 3
        if comment:
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            fence = marker[1]
            fence_record = dict(start=column + marker.start(1), open_end=offset,
                                body_start=offset, marker=marker[1],
                                language=line[marker.end():].strip())
            flush()
            continue
        # A real unquoted heading or numbered item is a structural boundary,
        # not a lazy continuation of the preceding quoted paragraph. Explicit
        # quotes/comments/fences have already retained their inert ownership.
        heading = re.match(r"^ {0,3}#{1,6} ", line)
        numbered = re.match(r"^ {0,3}(\d+[.)])[ \t]+", line)
        if heading:
            flush()
            units.append(("heading", line.strip()))
            if source_spans is not None:
                source_spans.append((column, column + len(line)))
            if marker_spans is not None:
                start = column + line.index('#')
                marker_spans.append((start, start + len(line.strip().split(' ', 1)[0])))
            if headings is not None:
                headings.append((line_number, line.strip()))
            continue
        if not line.strip():
            flush()
            continue
        indent = len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip(" "))
        if numbered:
            flush()
            kind = "numbered:" + numbered[1] if keep_markers else "numbered"
            continuation_indent = len(numbered[0].expandtabs(4))
            current_marker = column + numbered.start(1), column + numbered.end(1)
            line = line[numbered.end():]
            column += numbered.end()
        elif indent >= 4 and (not content or
                (kind.startswith("numbered") and indent >= continuation_indent + 4)):
            # Indentation starts inert code at a paragraph boundary. A plain
            # active paragraph's contiguous indented continuation stays active.
            flush()
            continue
        while True:
            start = line.find("<!--")
            if start < 0:
                content.append(line)
                content_spans.append((column, column + len(line)))
                break
            if line[:start].strip():
                content.append(line[:start])
                content_spans.append((column, column + start))
            flush()
            end = line.find("-->", start + 4)
            if end < 0:
                comment = True
                break
            line = line[end + 3:]
            column += end + 3
    flush()
    return tuple(units)


def active_prose_match(text: str, pattern: str) -> tuple[int, int]:
    """Locate one mutation target in active LF-normalized source, not history."""
    spans = []
    units = procedural_prose_units(text, source_spans=spans)
    assert len(units) == len(spans), 'control: incomplete active source spans'
    matches = []
    for (kind, value), (start, end) in zip(units, spans):
        if kind != 'paragraph':
            continue
        raw = text[start:end]
        assert ' '.join(raw.split()) == value, 'control: active source span differs'
        matches.extend((start + match.start(), start + match.end())
                       for match in re.finditer(pattern, raw))
    assert len(matches) == 1, 'control: missing/duplicate active prose target'
    return matches[0]


class ControlSpan(str):
    """A contiguous test-fixture view with coordinates in its original source."""

    def __new__(cls, text, start=0, end=None):
        end = len(text) if end is None else end
        value = str.__getitem__(text, slice(start, end))
        result = str.__new__(cls, value)
        result.source = text.source if isinstance(text, cls) else text
        origin = text.start if isinstance(text, cls) else 0
        result.start, result.end = origin + start, origin + end
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, end, step = key.indices(len(self))
            if step == 1:
                return ControlSpan(self, start, end)
        return str.__getitem__(self, key)

    def strip(self, chars=None):
        first = len(self) - len(str.lstrip(self, chars))
        last = len(str.rstrip(self, chars))
        return self[first:max(first, last)]

    def rstrip(self, chars=None):
        return self[:len(str.rstrip(self, chars))]


def control_documents(documents):
    return {path: text.replace('\r\n', '\n') for path, text in documents.items()}


def control_source(text):
    """Reuse the finite scanner; retain active markers and complete fence spans."""
    spans, markers, fences = [], [], []
    units = procedural_prose_units(text, keep_markers=True, source_spans=spans,
                                   marker_spans=markers, fence_spans=fences)
    assert len(units) == len(spans) == len(markers)
    records = [dict(kind=kind, value=value, start=marker[0] if marker else span[0],
                    end=span[1], body_start=span[0], marker=marker)
               for (kind, value), span, marker in zip(units, spans, markers)]
    return records, fences


def control_matches(text, old, *, flexible=False, fence_languages=('ini',)):
    records, fences = control_source(text)
    pattern = r'\s+'.join(re.escape(part) for part in old.split()) if flexible else re.escape(old)
    # Operative prose already treats contiguous whitespace as equivalent. Keep
    # its source extent (including requested edge whitespace), while literal
    # fenced fields retain the existing exact or explicitly flexible pattern.
    prose_pattern = ''.join(r'\s+' if part.isspace() else re.escape(part)
                            for part in re.split(r'(\s+)', old))
    candidates = []
    if re.match(r'^#{1,6} ', old):
        for row in records:
            if row['kind'] == 'heading' and row['value'] == old.strip():
                end = row['end'] if old.endswith('\n') else row['start'] + len(text[row['start']:row['end']].rstrip('\n'))
                candidates.append((row['start'], end))
        return candidates
    if re.match(r'^\d+[.)] ', old):
        for row in records:
            if row['kind'].startswith('numbered:'):
                match = re.match(pattern, text[row['start']:row['end']])
                if match:
                    candidates.append((row['start'], row['start'] + match.end()))
        return candidates
    for row in records:
        if row['kind'] == 'heading':
            continue
        start, end = row['body_start'], row['end']
        raw = text[start:end]
        code_data = [(m.start(), m.end()) for m in re.finditer(r'(`+)(.*?)\1', raw, re.S)
                     if '`' in normalized_prose_unit(m[0])]
        for match in re.finditer(prose_pattern, raw):
            if not any(a <= match.start() and match.end() <= b for a, b in code_data):
                candidates.append((start + match.start(), start + match.end()))
    for fence in fences:
        if fence_languages is not None and fence['language'] not in fence_languages:
            continue
        for match in re.finditer(pattern, text[fence['start']:fence['end']]):
            candidates.append((fence['start'] + match.start(), fence['start'] + match.end()))
    return sorted(set(candidates))


def control_target(text, old, *, flexible=False, fence_languages=('ini',)):
    if isinstance(old, ControlSpan):
        source = text.source if isinstance(text, ControlSpan) else text
        assert source == old.source, 'control: stale source view'
        return old
    if old == text:
        return ControlSpan(text)
    matches = control_matches(text, old, flexible=flexible, fence_languages=fence_languages)
    assert len(matches) == 1, 'control: missing/duplicate active target: ' + repr(old[:80])
    return ControlSpan(text, *matches[0])


def control_replace(text, old, new, count=1, *, flexible=False, fence_languages=('ini',), block=False):
    if isinstance(old, ControlSpan):
        target = control_target(text, old)
        origin = text.start if isinstance(text, ControlSpan) else 0
        matches = [(target.start - origin, target.end - origin)]
    elif old == text:
        matches = [(0, len(text))]
    else:
        matches = control_matches(text, old, flexible=flexible, fence_languages=fence_languages)
        assert matches, 'control: ineffective active mutation: ' + repr(old[:80])
        if count:
            assert len(matches) >= count
            matches = matches[:count]
    changed = str(text)
    for start, end in reversed(matches):
        assert 0 <= start <= end <= len(text)
        replacement = new
        if block and re.match(r'^ {0,3}>', replacement):
            root = text.source if isinstance(text, ControlSpan) else text
            position = start + (text.start if isinstance(text, ControlSpan) else 0)
            line_start = root.rfind('\n', 0, position) + 1
            prefixes = []
            procedural_prose_units(root, line_prefixes=prefixes)
            quote_start = dict(prefixes).get(line_start, line_start)
            # A continuing multiline comment is already removed before the
            # quote scan. A same-line comment is removed later; start the newly
            # inserted quote on its own line without altering the comment.
            if root[quote_start:position].strip():
                replacement = '\n' + replacement
        changed = changed[:start] + replacement + changed[end:]
    return changed


def control_before(text, target, insertion, *, block=False):
    span = control_target(text, target)
    return control_replace(text, span[:0], insertion, block=block)


def control_append(span, insertion, *, block=False):
    assert isinstance(span, ControlSpan)
    return control_replace(span, span[len(span):], insertion, block=block)


def control_section(text, title, level=2):
    records, _ = control_source(text)
    expected = '#' * level + ' ' + title
    starts = [i for i, row in enumerate(records) if row['kind'] == 'heading' and row['value'] == expected]
    assert len(starts) == 1, 'control: missing/duplicate active section'
    index = starts[0]
    start = records[index]['end']
    end = next((row['start'] for row in records[index + 1:] if row['kind'] == 'heading'
                and len(row['value'].split(' ', 1)[0]) <= level), len(text))
    return ControlSpan(text, start, end)


def control_between(text, first, following, *, after_first=False):
    start = control_target(text, first, flexible=True)
    end = control_target(text, following.lstrip('\n'), flexible=True)
    origin = text.start if isinstance(text, ControlSpan) else 0
    return ControlSpan(text, (start.end if after_first else start.start) - origin, end.start - origin)


def control_event(text, language='ini'):
    _, fences = control_source(text)
    found = [row for row in fences if row['language'] == language]
    assert len(found) == 1, 'control: missing/duplicate active event fixture'
    row = found[0]
    return dict(row, block=ControlSpan(text, row['start'], row['end']).rstrip('\n'),
                opening=ControlSpan(text, row['start'], row['open_end']),
                body=ControlSpan(text, row['body_start'], row['body_end']),
                closing=ControlSpan(text, row['close_start'], row['close_end']))


def control_report_projection(text):
    """Use the same closed raw report-template owner and row schema as check()."""
    marker = 'Ordinary child-task custody (when this report carries an ordinary task):'
    assert text.count(marker) == 1, 'control: missing/duplicate report owner'
    start = text.index(marker) + len(marker)
    end = text.find('Populate dispatch fields', start)
    end = len(text) if end < 0 else end
    rows = list(re.finditer(r'(?m)^- visible_projection: (.+)$', text[start:end]))
    assert len(rows) == 1, 'control: missing/duplicate owned report projection'
    return ControlSpan(text, start + rows[0].start(), start + rows[0].end())


def control_reflow(text, separator=' '):
    records, _ = control_source(text)
    changed = str(text)
    for row in reversed(records):
        if row['kind'] == 'heading':
            continue
        start, end = row['body_start'], row['end']
        raw = text[start:end]
        replacement = separator.join(raw.split()) + ('\n' if raw.endswith('\n') else '')
        changed = changed[:start] + replacement + changed[end:]
    return changed


def control_active_text(text):
    records, _ = control_source(text)
    return '\n\n'.join(str(text[row['body_start']:row['end']]).strip()
                       for row in records if row['kind'] != 'heading')


def control_active_owner_replace(text, owner, replacement):
    """Rebuild operative prose while retaining every intervening inert byte."""
    assert isinstance(owner, ControlSpan)
    records, _ = control_source(owner)
    active = [ControlSpan(owner, row['body_start'], row['end']).strip()
              for row in records if row['kind'] != 'heading']
    assert active, 'control: empty operative owner'
    segments, projection = [], ''
    for span in active:
        if projection:
            projection += '\n\n'
        start = len(projection)
        projection += span
        segments.append((start, len(projection), span))
    assert projection == control_active_text(owner)
    edits = []
    for order, (tag, first, last, new_first, new_last) in enumerate(
            SequenceMatcher(a=projection, b=replacement, autojunk=False).get_opcodes()):
        if tag == 'equal':
            continue
        payload = replacement[new_first:new_last]
        touched = [(max(first, a), min(last, b), a, span)
                   for a, b, span in segments if max(first, a) < min(last, b)]
        if touched:
            for index, (a, b, origin, span) in enumerate(touched):
                edits.append((span.start + a - origin, span.start + b - origin,
                              payload if index == 0 else '', order))
        elif payload:
            if first == len(projection) and not payload.strip():
                # Existing source gaps already separate this owner from its
                # following boundary; constructor padding must not duplicate them.
                continue
            if first == len(projection):
                position = owner.end
            else:
                containing = [(a, span) for a, b, span in segments if a <= first <= b]
                if containing:
                    a, span = containing[0]
                    position = span.start + first - a
                else:
                    position = next(span.start for a, b, span in segments if a > first)
            edits.append((position, position, payload, order))
    changed = str(text)
    origin = text.start if isinstance(text, ControlSpan) else 0
    for start, end, payload, order in sorted(edits, key=lambda edit: (edit[0], edit[1], edit[3]), reverse=True):
        local = ControlSpan(changed, start - origin, end - origin)
        changed = control_replace(changed, local, payload, block=True)
    return changed


def normalized_prose_unit(text: str) -> str:
    # Strip identifier markup, not arbitrary backtick-quoted prose. Compound
    # identifiers, placeholder fields and the resolver command are local forms.
    compound = {
        "AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY",
        "scripts/resolve-internal-skill.py --governor SKILL.md --child <child>",
        "pointer -> receipt v3 -> permanent marker",
        "CHILD_TASK=<stable logical name>",
        "PURPOSE=<bounded purpose>",
        "RETURNED != ACCEPTED != JOINED != PARENT COMPLETE",
        "GOVERNED_CHILD_ROLE_SELECTION != PROCEDURAL_SKILL_SELECTION",
        "GOVERNED_ROLE != PROCEDURAL_METHOD",
    }

    def identifier(match: re.Match) -> str:
        value = " ".join(match[1].split())
        if re.fullmatch(r"[\w./<>=!-]+", value, re.ASCII) or value in compound:
            return value
        return match[0]

    return " ".join(re.sub(r"`([^`]+)`", identifier, text).split())


def owned_heading_span(document: str, ancestry: tuple[str, ...],
                       following: str, *, keep_markers: bool = False) -> tuple[tuple[str, str], ...]:
    """Retain every active unit between exact finite owner identities."""
    units = procedural_prose_units(document, keep_markers=keep_markers)
    start_unit, end_unit = ("heading", ancestry[-1]), ("heading", following)
    assert units.count(start_unit) == 1, "owner: missing/duplicate active owning heading"
    assert units.count(end_unit) == 1, "owner: missing/duplicate active following heading"
    start, end = units.index(start_unit), units.index(end_unit)
    assert start < end, "owner: following heading precedes owner"
    stack = []
    for kind, value in units[:start + 1]:
        if kind != "heading":
            continue
        level = len(value.split(" ", 1)[0])
        stack = [item for item in stack if len(item.split(" ", 1)[0]) < level]
        stack.append(value)
    assert tuple(stack) == ancestry, "owner: active heading ancestry differs"
    # Do not stop at an arbitrary earlier heading. Unexpected headings remain
    # evidence inside this span for the owner's complete sequence check.
    return units[start + 1:end]


def check_owned_route_units(child_document: str, skill_document: str) -> None:
    # These are the finite complete owned units, frozen independently of the
    # supplied documents. Matching a prefix or a historical inline quotation
    # cannot discharge them. Substantive wording/additions require review;
    # supported whitespace and identifier markup alone may normalize.
    route_units = tuple((kind, normalized_prose_unit(value))
                        for kind, value in owned_heading_span(child_document,
                            ("# Child-Agent Review Loops", "## Governor-routed internal cognition",
                             "### Mandatory compaction entry and result ceiling"), "## Non-authority rule"))
    runtime_units = tuple((kind, normalized_prose_unit(value))
                          for kind, value in owned_heading_span(skill_document,
                              ("# /implementaudit", "## Runtime Loop"), "## Trace And Closure", keep_markers=True))
    # The next route owner is the genuine Non-authority rule, including its
    # unique immediate operative lead, rather than an injected stopping token.
    all_child_units = procedural_prose_units(child_document)
    boundary = ("heading", "## Non-authority rule")
    boundary_lead = ("paragraph", "Child agents are review loops, not independent authorization authorities.")
    boundary_index = all_child_units.index(boundary)
    assert all_child_units.count(boundary_lead) == 1 and boundary_index + 1 < len(all_child_units) and \
        all_child_units[boundary_index + 1] == boundary_lead, "owner: wrong following route owner"
    expected_route = []

    def exact(units: tuple[tuple[str, str], ...], label: str,
              expected: str, kind: str = "paragraph") -> int:
        value = (kind, normalized_prose_unit(expected))
        if units is route_units:
            expected_route.append(value)  # Only the independent literals below.
        assert units.count(value) == 1, label
        return units.index(value)

    exact(route_units, "route.mandatory-compaction-entry", """
`POST_COMPACTION_RECONCILIATION` has independent execution eligibility:
`AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY`.
Completed compaction plus governor resumption requires audit-state even when
canonical currentness, continuity, measured epoch or normal route admission is
absent. Follow `continuity.md`'s mandatory pending-boundary protocol. Use the
actual selected child bytes and prospective visible LOAD/ACK/USE sequence;
missing native qualification limits claims, never this bounded cognitive entry.
Source/identity uncertainty is returned explicitly, not promoted or guessed.
No governor state-dependent reconstruction/decision precedes that reconciliation.
Independent lawful ordinary children continue; no global cancellation or replay.
""")
    exact(route_units, "route.compaction-no-retrocredit", """
Prefer the existing compact hook's durable signal. A missing hook receipt plus
independently proved completion/resumption still requires the audit. Dispatch
and RETURN preserve pending; exact successful accepted RETURN/JOIN consumes
only observed boundary/version pairs. Later compaction needs its own pending
coverage; reuse an active child only when its actual later observation/cutoff
and return demonstrably include that boundary. This is not prior-worker credit.
An unknown, failed or incomplete child retains pending until lawful disposition.
The pending owner's read-only `status` query never creates an audit boundary.
Explicit post-compaction `resume` without hook/registration retains
`UNRESOLVED_RESUME_OBSERVATION` and routes bounded cognition with uncertainty;
the invocation is not proof of a unique compaction. Preserve ambiguous versions.
Assignments are per boundary/version pair: failed A stays assigned and pending
while distinct proved unassigned B may route. B's JOIN cannot clear A or release
A-dependent governor decisions. Only an active child with actual later observation
before its immutable RETURN may cover later unclaimed scope. Same-failed-scope
retirement/retry is `CONDITIONAL_UNQUALIFIED` until actual terminal/effect/release
evidence has a qualified consumer. A logical JOIN requires actual same-child
LOAD/USE/RETURN/result and explicit governor acceptance; caller `SUCCEEDED` is
not a lifecycle witness or native DISPOSE. Preserve missing consumer binding as
an operative qualification gap; it is not a new currentness/epoch route gate.
Apply `continuity.md` section **Actual result and governor acceptance consumer**
to actual same-child LOAD/USE/observation/result and separate later governor
acceptance of the exact result/scope. Actor, call, role/channel and ordering
evidence must come from qualified physical source observations. A shared
session_id is not child identity; physical rows are not embedded ordinals;
opaque ACK association does not prove plaintext delivery semantics. Bound payload
reads before I/O, not by filtering a whole-history read. Missing profile or
witness evidence holds consumption and affected decisions, not mandatory
audit-state execution or unrelated lawful children. Only validated successful
JOIN consumes scope; neither a result, acceptance nor caller status does so alone.
The prospective **O/U/observation/R/A chain** freezes the pending-owner O, emits
actual closed JSON parent-commentary U after full same-child LOAD and visible
route, obtains the held child's full host O/U response, then validates that
completed exchange before USE. Actual R binds the exchange; distinct later closed
JSON parent-commentary A binds exact R scope before JOIN. U cannot prove child
observation and A cannot extend immutable R coverage. Claimed read, ciphertext,
tool status, echo, synthetic profile or borrowed native receipts cannot promote
this chain. Qualification remains a future genuine-boundary edge without replay.
Apply **Fixed policy P, qualification Q and episode E** from `continuity.md`:
freeze policy/code before O; keep later Q/E outside code identity; derive Q from
actual unconsumed C without requiring E/JOIN, and admit each exact episode from
independently validated source origin. Global profile/PASS/owner labels cannot
authenticate child evidence. Data arrival cannot rebind assignment/O/R/A or
justify child replay; absent admission holds consumption, not mandatory audit.
""")
    exact(route_units, "route.compaction-result-ceiling", """
`NATIVE_AUTHORITATIVE_RECOVERY` below keeps its own v2/v3/v4 capsules, `.used`
OPEN fence, currentness/native proof and host-stage receipt owners. Independent
compaction reconciliation creates none of those authoritative facts. Its
result may report CURRENTNESS=UNRESOLVED or QUALIFIED_EPOCH=ABSENT and grants no
canonical currentness, recovery, epoch, lifecycle, mutation, release or closure.
Normal staged-capture qualification is not an execution prerequisite for the
independent bounded entry; unavailable formal stages remain UNVERIFIED.
""")
    normal = exact(route_units, "route.normal-native-gate", """
For normal native-authoritative routing, before loading one child, the governor verifies executing package,
plugin/standalone precedence, audit object, authority ceiling, and the
currentness/independence gate, then names exactly one child. Resolve with
`scripts/resolve-internal-skill.py --governor SKILL.md --child <child>`:
source/canonical layouts load `../<child>/SKILL.md`; standalone loads
`internal-procedures/<child>.md`. The resolver refuses missing/extra children or
ambiguous sibling layouts; never infer from discovery/search order. A child result returns here as evidence input;
the governor re-derives current state before any later route or transition.
Reject child claims of authority, closure, lifecycle change,
mutation, currentness, release, or `AUDIT_COMPLETE`.
""")
    admission = exact(route_units, "route.other-child-gates", """
Ordinary NATIVE_AUTHORITATIVE_RECOVERY `audit-state` routes require the native
boundary/currentness gate in `references/continuity.md`; its explicit v3 custody
and prospective v4 native-attempt variants remain scoped native alternatives. Route `audit-assess` only for a digest-bound
immutable packet under the independence contract in
`references/plan-lifecycle.md`. Route maintainer-only `audit-implement` only for an
exact candidate after mechanically verified release currentness under
`references/transcript-contract.md`; `NOT_APPLICABLE` is invalid there. Route
`audit-andon` from L4 only after a non-trivial Andon when bounded diagnosis can
change the response; it returns to L4/governor. An explicit direct cord-pull may
invoke the same bounded cognition and returns to the actual
caller without creating lifecycle, currentness, mutation, RXX or closure
authority. Cheap deterministic Andons bypass the child.
""")
    following = exact(route_units, "route.other-child-gates", """
At a material decision or boundary, including a returned new constraint,
explicitly consider audit-state, audit-assess, audit-implement and audit-andon.
""")
    # Close the entire admission span, including new paragraphs/headings.
    # No keyword blacklist can substitute for this absence of unreviewed units.
    assert admission == normal + 1 and following == admission + 1, "route.other-child-gates"
    exact(route_units, "route.other-child-gates", """
Keep cognition need, ordinary admission, explicit direct Andon entry and actual
route evidence separate in the existing task or route record; currentness=false
is not an all-child no-need result.
""")
    exact(route_units, "route.complete-owner", """
Independent cold source review is not admitted audit-assess; isolated source
preparation is not maintainer audit-implement qualification.
""")
    exact(route_units, "route.complete-owner", """
Completed compaction/resumption independently requires POST_COMPACTION_RECONCILIATION;
its execution does not establish admitted native recovery or currentness.
""")
    exact(route_units, "route.complete-owner", """
A substantive abnormality, a defeated countermeasure or changed routing
behaviour requires fresh governor consideration; an already-bound cheap known
failure bypasses diagnostic rerouting.
""")
    exact(route_units, "route.complete-owner", """
Use scoped NOT_TRIGGERED or UNKNOWN dispositions; unknown hidden use is not NO.
""")
    exact(route_units, "route.complete-owner", """
Missed consideration, a missed visible witness and unknown historical use
remain distinct, with no retroactive credit.
""")
    exact(route_units, "route.complete-owner", """
An explicit direct cord-pull permits bounded audit-andon cognition without
ordinary currentness or OPEN; it creates no R0033 OPEN, canonical authority or
normal route credit.
""")
    exact(route_units, "route.complete-owner", """
Select at most one exact child under its applicable currentness, native-proof,
independence and host-receipt gates; return changed constraints to the
governor, never child-to-child dispatch or ceremonial replay.
""")
    exact(route_units, "route.complete-owner", """
Announcement, load/use evidence, return, acceptance and JOIN are separate
facts.
""")
    exact(route_units, "route.native-refusal-scope", """
A missing native-authoritative gate refuses that native route, not independent
POST_COMPACTION_RECONCILIATION. Ordinary cheap-path actions stay on the
Execution Spine. Planning remains progressively owned by
`references/planning-depth.md`; execution/repair remains progressively owned by
the Runtime Loop and `references/plan-lifecycle.md`. A verifier failure in the
target package is a bound audit gate failure, not evidence that the executing
IMPLEMENTAUDIT package is partial.
""")
    assert len(expected_route) == 16 and route_units == tuple(expected_route), \
        "route.complete-owner: unexpected, missing, reordered or differently owned operative unit"
    zero = exact(runtime_units, "route.governor-compaction-entry", """
Continuity boundary: STOP new state-dependent governor decisions until reconciliation.
`POST_COMPACTION_RECONCILIATION`: completed compaction plus governor resumption independently requires audit-state.
`POST_COMPACTION_AUDIT_STATE_REQUIRED=YES`;
`AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY`.
Missing currentness/continuity/epoch/native admission limits results, never this route.
Follow `references/continuity.md`: hook pending -> visible OPEN/LOAD -> isolated USE -> successful RETURN/JOIN.
Keep independent lawful children running; no governor STATE/ROADMAP/WORK_GRAPH pre-reconstruction.
Actual observation scope/cutoff governs later coverage; dispatch/RETURN leave pending.
`NATIVE_AUTHORITATIVE_RECOVERY` remains separate: Genuine host-reported-compaction requires
MECHANICAL_CURRENTNESS (or qualified v3/v4 native custody); the governor
never substantively reads STATE/ROADMAP/WORK_GRAPH before OPEN. Bind a fresh host worker context,
OPEN_AUDIT_STATE with the one-use implementaudit.post-compaction-recovery.v2 capsule or exact v3/v4 successor,
receive the minimum frontier, RETURN, DISPOSE, RECONCILE, then prove post-return currentness before the exact typed edge.
No ordinary authority: the state owner publishes receipt/H0 lineage.
Keep `pointer -> receipt v3 -> permanent marker`, satisfied-one-shot refusal and `references/route-obligations.md`.
Native fences: `POST_BOUNDARY_NEW_EXECUTION=REFUSE_UNTIL_CURRENT`;
`PREBOUNDARY_PROCESS=WAIT_OR_TERMINATE_ONLY`; `STANDING_CONSTRAINT_ROLE=DO_NOT_PROMOTE_WITHOUT_LIVE_STATE`;
`POST_BOUNDARY_FIRST_SUBSTANTIVE_MESSAGE=VERIFIED_CONTINUITY_RECEIPT`. Each native owner action stays separate.
""", "numbered:0.")
    one = exact(runtime_units, "route.runtime-item-one-boundary", """
Safety read: `AGENTS.md`, README/CONTRIBUTING/docs/workflows, existing audit
docs, generator/source ownership, and authorization chain.
""", "numbered:1.")
    assert sum(kind == "numbered:0." for kind, _ in runtime_units) == 1 and \
        sum(kind == "numbered:1." for kind, _ in runtime_units) == 1, "route.runtime-item-marker-identity"
    assert zero == 0 and one == 1, \
        "route.runtime-complete-prefix: unexpected operative unit before genuine item 1"



def procedural_prose_parts(text: str) -> tuple[str, ...]:
    return tuple(value for kind, value in procedural_prose_units(text)
                 if kind in ("paragraph", "numbered"))



def check_route_admission(documents: dict[str, str]) -> None:
    """Normal native admission and mandatory compaction execution both hold."""
    route = section(documents[CHILD], "Governor-routed internal cognition")
    runtime = section(documents[SKILL], "Runtime Loop")

    def active(owner: str, label: str, *claims: str) -> None:
        # Preserve useful failure labels. These phrase diagnostics are never
        # sufficient: complete owned unit/block equality is required below.
        parts = tuple(part.replace("`", "") for part in procedural_prose_parts(owner))
        for claim in claims:
            assert any(" ".join(claim.split()) in part for part in parts), label

    active(route, "route.normal-native-gate",
           "For normal native-authoritative routing, before loading one child, the governor verifies executing package, "
           "plugin/standalone precedence, audit object, authority ceiling, and the currentness/independence gate, then names exactly one child.")
    active(route, "route.native-recovery-scope",
           "Ordinary NATIVE_AUTHORITATIVE_RECOVERY audit-state routes require the native boundary/currentness gate in references/continuity.md; "
           "its explicit v3 custody and prospective v4 native-attempt variants remain scoped native alternatives.")
    active(route, "route.mandatory-compaction-entry",
           "POST_COMPACTION_RECONCILIATION has independent execution eligibility:",
           "Completed compaction plus governor resumption requires audit-state even when canonical currentness, continuity, measured epoch or normal route admission is absent.")
    active(runtime, "route.governor-compaction-entry",
           "POST_COMPACTION_RECONCILIATION: completed compaction plus governor resumption independently requires audit-state.",
           "POST_COMPACTION_AUDIT_STATE_REQUIRED=YES")
    active(route, "route.compaction-pre-use",
           "Use the actual selected child bytes and prospective visible LOAD/ACK/USE sequence;",
           "missing native qualification limits claims, never this bounded cognitive entry.")
    active(route, "route.compaction-no-retrocredit",
           "This is not prior-worker credit.")
    active(route, "route.compaction-result-ceiling",
           "AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY",
           "Independent compaction reconciliation creates none of those authoritative facts.",
           "result may report CURRENTNESS=UNRESOLVED or QUALIFIED_EPOCH=ABSENT and grants no canonical currentness, recovery, epoch, lifecycle, mutation, release or closure.")
    active(runtime, "route.governor-result-ceiling",
           "AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY",
           "Missing currentness/continuity/epoch/native admission limits results, never this route.")
    active(route, "route.native-refusal-scope",
           "A missing native-authoritative gate refuses that native route, not independent POST_COMPACTION_RECONCILIATION.")
    active(route, "route.other-child-gates",
           "Route audit-assess only for a digest-bound immutable packet under the independence contract",
           "Route maintainer-only audit-implement only for an exact candidate after mechanically verified release currentness",
           "NOT_APPLICABLE is invalid there.",
           "Route audit-andon from L4 only after a non-trivial Andon when bounded diagnosis can change the response;",
           "currentness=false is not an all-child no-need result.")
    check_owned_route_units(documents[CHILD], documents[SKILL])



def operative_paragraphs(text: str) -> tuple[str, ...]:
    """Bounded prose scan for composition; the separately owned route scan is unchanged."""
    paragraphs, current = [], []
    fence, comment = None, False
    quote = QuotedParagraph()

    def flush() -> None:
        if current:
            paragraphs.append(normalized_prose_unit(" ".join(current)))
            current.clear()

    for line in text.splitlines():
        if fence is not None:
            closing = re.fullmatch(r" {0,3}(`{3,}|~{3,})[ \t]*", line)
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= len(fence):
                fence = None
            continue
        if comment:
            end = line.find("-->")
            if end < 0:
                continue
            comment, line = False, line[end + 3:]
        if quote.consumes(line):
            flush()
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            flush()
            fence = marker[1]
            continue
        if not line.strip():
            flush()
            continue
        # Indentation starts code only at a paragraph boundary. An active
        # paragraph's indented continuation remains operative prose.
        if not current and re.match(r"^(?: {4}|\t)", line):
            continue
        while "<!--" in line:
            prefix, rest = line.split("<!--", 1)
            if prefix.strip():
                current.append(prefix)
            flush()  # A hidden region cannot manufacture a required clause.
            if "-->" not in rest:
                comment, line = True, ""
                break
            line = rest.split("-->", 1)[1]
        if line.strip():
            current.append(line)
    flush()
    return tuple(paragraphs)


def check_role_method_composition(documents: dict[str, str]) -> None:
    """Check this bounded source contract, not actual admission or model conduct."""
    owner = section(section(documents[CHILD], "Visible pre-use announcements"),
                    "Non-governed skill use", 3)
    active = operative_paragraphs(owner)
    starts = [index for index, paragraph in enumerate(active)
              if paragraph == ROLE_METHOD_PARAGRAPHS[0]]
    assert len(starts) == 1, "composition: missing/duplicate operative role/method contract"
    start = starts[0]
    following = "Reading selected skill guidance to determine or apply how to act is procedural skill use."
    assert sum(paragraph.count(following) for paragraph in active[start + 1:]) == 1, \
        "composition: ambiguous operative following procedural-read owner"
    ends = [index for index, paragraph in enumerate(active)
            if index > start and paragraph.startswith(following)]
    assert len(ends) == 1, "composition: missing/duplicate operative following procedural-read owner"
    end = ends[0]
    # Whole paragraphs, in their declared order, prevent a required prefix or
    # retained literal from concealing an appended waiver. Inert history is OK.
    assert active[start:end] == ROLE_METHOD_PARAGRAPHS, \
        "composition: missing, historical, reordered or conflicting operative paragraphs"


def native_event_block(text: str, rows: tuple[str, ...], sentence: str, *, optional_join: bool = False) -> str:
    """One operative ini event and its immediately accompanying named prose."""
    blocks, body, prose = [], [], []
    fence, language, comment = None, None, False
    quote = QuotedParagraph()
    end_line = -1
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if fence is not None:
            closing = re.fullmatch(r" {0,3}(`{3,}|~{3,})[ \t]*", line)
            if closing and closing[1][0] == fence[0] and len(closing[1]) >= len(fence):
                blocks.append((language, tuple(value.strip() for value in body)))
                body, fence, end_line = [], None, index
            else:
                body.append(line)
            continue
        if comment:
            if "-->" not in line:
                continue
            comment, line = False, line.split("-->", 1)[1]
        if quote.consumes(line):
            continue
        while "<!--" in line:
            prefix, rest = line.split("<!--", 1)
            prose.append(prefix)
            if "-->" not in rest:
                comment, line = True, ""
                break
            line = rest.split("-->", 1)[1]
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$", line)
        if marker:
            fence, language = marker[1], marker[2].strip()
        else:
            prose.append(line)
    assert fence is None, "native event: unclosed fence"
    allowed = [[("ini", rows)]]
    if optional_join:
        allowed.append([("ini", ("EVENT=JOIN",) + rows)])
    assert blocks in allowed, "native event: require one exact grouped ini field block"
    following = operative_paragraphs("\n".join(lines[end_line + 1:]))
    expected = normalized_prose_unit(sentence)
    assert following and following[0].startswith(expected), \
        "native event: missing immediate bounded natural statement naming the exact identity"
    return "\n".join(prose)


def check_owned_native_units(documents: dict[str, str]) -> None:
    """Check complete active clauses, independent of field presence or prefixes."""
    root = ("# Child-Agent Review Loops", "## Visible pre-use announcements")
    owners = (
        (root, "### Ordinary child dispatch", (
            """These are prospective operational requirements for the governor's real visible
commentary. A prepared file, child-only narration or later topology recap cannot
satisfy them. They grant no dispatch, routing, currentness or effect authority.""",
            """Every lifecycle, routing, child or skill event uses one fenced Markdown block
whose language is literally ini. One semantic event gets one block; text,
an untyped fence, disconnected inline fields and a combined event are invalid.
Immediately after the block, give one bounded natural sentence naming the exact
stable logical child/holon or selected skill and its purpose or observed result.
Use that event's exact identities; generic "this ordinary child" or "this skill"
does not name them. These are prospective event forms, never evidence that a
template's load, use, return, acceptance, JOIN or completion actually occurred.""",
        )),
        (root + ("### Ordinary child dispatch",), "### Non-governed skill use", (
            """Before every material ordinary holarchic child dispatch (producer, review,
preparation, recovery and parallel siblings), including reuse/follow-up dispatch,
emit this visible governor PRE-ACTION block before the host call:""",
            """Say: "I'm using the <CHILD_TASK> holon to <PURPOSE>."
Substitute the exact stable CHILD_TASK and bounded PURPOSE from that block.
Announce the stable logical name before host spawn; bind/report the returned
concrete host identity afterward. Missing host-generated ID never excuses silence.
A host-generated identity is unavailable before creation; the stable logical
name supplies the pre-action identity and remains linked to the returned host
identity. A follow-up uses that binding and announces its new bounded purpose
before dispatch. Announcing does not waive fresh-context or independence gates.""",
        )),
        (root + ("### Non-governed skill use",), "### Governed child lifecycle", (
            """Before every substantive non-governed skill use, emit this visible block before
loading or applying the skill:""",
            """Say: "I'm using the <skill> skill to <purpose>."
The sentence names that block's exact SKILL_SELECTED and bounded PURPOSE.
This includes substantive renewed use after a boundary; prior use is not a
standing substitute for the announcement attached to the next material use.
When a child selects a skill late, relay SKILL_SELECTED and bounded PURPOSE to
the governor and wait for its actual visible announcement acknowledgement before
loading or applying the skill. Child-local commentary or a final return cannot
substitute for the governor's user-visible pre-use announcement. This governs
substantive skill use, not every source-document read.""",
        )),
        (root + ("### Governed child lifecycle", "#### Before actual load"), "#### Only after actual load", (
            "After the applicable route prerequisites and before actual load, visibly emit:",
            '''Say: "I'm opening the <CHILD_TASK> holon for the <CHILD_SKILL_SELECTED> skill to <bounded route purpose>."''',
            """Selection/opening is not verified route narration. Bind the exact task/route
identity; the ordinary stable-name/returned-host binding also applies when host
creation precedes LOAD. Do not fabricate a host identity or stage receipt.""",
        )),
        (root + ("### Governed child lifecycle", "#### Only after actual load"), "##### Generic full-skill LOAD", (
            """Only independently verified real LOAD evidence for the full selected child
content permits the governor to emit:""",
        )),
        (root + ("### Governed child lifecycle", "#### Only after actual load", "##### Generic full-skill LOAD"), "##### Actual native delivery", (
            GENERIC_LOAD_CONTEXT,
            '''Say: "I'm using the <CHILD_TASK> holon with the <CHILD_SKILL_ROUTE> skill to <bounded reason for this route>."''',
        )),
        (root + ("### Governed child lifecycle", "#### Only after actual load", "##### Actual native delivery"), "### Returns and continuity", (
            NATIVE_LOAD_CONTEXT,
            '''Say: "I'm using the <CHILD_TASK> holon with the <CHILD_SKILL_ROUTE> skill to <bounded reason for this route>."''',
            """Use the actual loaded-child narration in transcript-contract.md.
Never infer actual LOAD from selection, OPEN, packaging or a returned result.
USE remains held until the actual parent announcement is acknowledged under
the existing qualified same-worker transport contract. USE, RETURN, DISPOSE
and GOVERNOR_ACCEPTANCE stay separate. Formal host-owned receipts and exact
route/obligation/packet identity remain required by their existing owners;
unobserved stages stay UNVERIFIED. The historical hidden audit-state conformance
defect remains a defect: no retrocredit or replay for telemetry. Later honest
reports preserve the defect without converting it to compliant prior behavior.
The existing ordinary-no-announcement control means no selected governed LOAD
marker; it does not exempt ordinary child or skill pre-use announcements.""",
        )),
        (root + ("### Returns and continuity",), "## Governor-routed internal cognition", (
            """RETURNED != ACCEPTED != JOINED != PARENT COMPLETE.
RETURNED means evidence arrived; ACCEPTED requires independent governor
adjudication; JOINED requires actual consumption by the named parent/frontier;
PARENT COMPLETE requires that parent's own acceptance and closure gates.
JOIN names the consuming parent/frontier and exact consumed result. Report each
transition only when it occurred; a returned result does not create acceptance,
JOIN, parent completion, currentness or authority.""",
            """Emit RETURNED, ACCEPTED, JOINED and PARENT_COMPLETE as separate observed events,
each in its own ini block with the exact child, parent, consuming frontier and
result. The natural sentence names that same child and consuming parent/frontier.
PARENT_COMPLETE reports the parent's own state, never automatic child credit.
The ordinary return projection below carries only one such observed transition;
governed returns retain their stronger exact route/obligation/packet custody.
Every return/JOIN record retains CHILD_TASK, STATUS=RETURNED, ACCEPTED, JOINED,
CONSUMING_PARENT and PARENT_COMPLETE. ACCEPTED, JOINED and PARENT_COMPLETE each
carry their own observed YES, NO or UNVERIFIED value; none follows from another.
Optional EVENT=JOIN names an actual JOIN event and never replaces STATUS=RETURNED.
STATUS records the returned product; the other fields preserve independent
adjudication, actual consumption and the parent's own completion evidence.""",
            """After compaction, handoff or successor change, reacquire these operational
obligations and exact parent/task/host bindings before the next dispatch or skill
use. Keep the continuity STOP and applicable currentness/recovery prerequisites;
an announcement cannot authorize hot reads or ordinary re-entry.
Preserve literal ini grouping, stable named sentences, separate pre-load and
verified-load events, actual same-worker USE acknowledgement and separate
RETURNED/ACCEPTED/JOINED/PARENT_COMPLETE evidence at every successor execution.
Restating this contract does not repair earlier owner-restatement or telemetry
failures; a fresh successor witness requires actual execution evidence.
Periodic topology is supplemental, never a substitute for the pre-action
blocks, actual verified-load narration, or separate return/acceptance/JOIN facts.""",
        )),
    )
    for ancestry, following, expected in owners:
        observed = tuple((kind, normalized_prose_unit(value))
                         for kind, value in owned_heading_span(documents[CHILD], ancestry, following))
        if ancestry[-1] == "### Non-governed skill use":
            # The complete selection owner ends at the unique genuine role/
            # method owner. Its separately maintained complete paragraph checks
            # and procedural-read formatting contract continue below it.
            boundary = ("paragraph", ROLE_METHOD_PARAGRAPHS[0])
            assert observed.count(boundary) == 1, "native skill selection: ambiguous following owner"
            observed = observed[:observed.index(boundary)]
        frozen = tuple(("paragraph", " ".join(value.split())) for value in expected)
        assert observed == frozen, "native complete active owner: " + ancestry[-1]

    # The thin governor's one complete operative paragraph remains independently
    # fixed. Its source stays at 21945 bytes; the existing ini flags and event
    # fields retain their separate checks in check().
    governor = owned_heading_span(documents[SKILL],
        ("# /implementaudit", "## Visible pre-use announcements"), "## Governor-routed internal cognition")
    expected_governor = """Before every material ordinary holarchic child dispatch, including reuse/follow-up dispatch,
emit one ini block with PARENT_HOLON=<parent>, CHILD_TASK=<stable logical name>,
CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK, STATUS=OPEN, PURPOSE=<bounded purpose>.
Say: "I'm using the <CHILD_TASK> holon to <PURPOSE>."
Announce the stable logical name before host spawn; bind/report the returned concrete host identity afterward.
Missing host-generated ID never excuses silence.
Before every substantive non-governed skill use, emit one ini block with SKILL_SELECTED=<skill> and
PURPOSE=<bounded purpose>. Say: "I'm using the <skill> skill to <purpose>."
Before actual load, emit one ini block with CHILD_TASK=<id>,
CHILD_TASK_KIND=GOVERNED_CHILD_SKILL, CHILD_SKILL_SELECTED=<skill>, STATUS=OPEN, LOAD=UNVERIFIED.
Only after actual load of the full selected child, emit a separate ini block with
CHILD_TASK=<id>, CHILD_SKILL_ROUTE=<skill>, LOAD=VERIFIED, then its bounded named reason;
USE, RETURN, DISPOSE and GOVERNOR_ACCEPTANCE stay separate under references/child-agents.md.
RETURNED != ACCEPTED != JOINED != PARENT COMPLETE; JOIN names the consuming parent/frontier.
After compaction, handoff or successor change, reacquire this contract before the next dispatch or skill use.
Periodic topology is supplemental, never a substitute. Preserve historical defects without retrocredit or replay."""
    assert tuple((kind, normalized_prose_unit(value)) for kind, value in governor) == (
        ("paragraph", " ".join(expected_governor.split())),), "native complete active governor owner"


def check(documents: dict[str, str]) -> None:
    # Scope the obligations to their operational owners. A token in a later
    # topology report, historical note or unrelated section cannot discharge it.
    skill = section(documents[SKILL], "Visible pre-use announcements")
    child = section(documents[CHILD], "Visible pre-use announcements")
    for owner in (skill, child):
        block(owner, FLAGS, language="text")  # Invariant declarations are not emitted events.
    for phrase in (
        "Before every material ordinary holarchic child dispatch",
        "including reuse/follow-up dispatch",
        "PARENT_HOLON=<parent>", "CHILD_TASK=<stable logical name>",
        "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "STATUS=OPEN",
        "PURPOSE=<bounded purpose>",
        "I'm using the <CHILD_TASK> holon to <PURPOSE>.",
        "Announce the stable logical name before host spawn",
        "bind/report the returned concrete host identity afterward",
        "Missing host-generated ID never excuses silence",
        "Before every substantive non-governed skill use",
        "SKILL_SELECTED=<skill>",
        "I'm using the <skill> skill to <purpose>.",
        "Before actual load", "CHILD_TASK=<id>",
        "CHILD_TASK_KIND=GOVERNED_CHILD_SKILL", "CHILD_SKILL_SELECTED=<skill>",
        "LOAD=UNVERIFIED", "Only after actual load",
        "CHILD_SKILL_ROUTE=<skill>", "LOAD=VERIFIED",
        "USE, RETURN, DISPOSE and GOVERNOR_ACCEPTANCE stay separate",
        "RETURNED != ACCEPTED != JOINED != PARENT COMPLETE",
        "JOIN names the consuming parent/frontier",
        "After compaction, handoff or successor change",
        "before the next dispatch or skill use",
        "Periodic topology is supplemental, never a substitute",
    ):
        require(skill.replace("`", ""), phrase)
    for phrase in (
        "emit one ini block with PARENT_HOLON=<parent>",
        "Before every substantive non-governed skill use, emit one ini block with SKILL_SELECTED=<skill>",
        "Before actual load, emit one ini block with CHILD_TASK=<id>",
        "Only after actual load of the full selected child, emit a separate ini block with CHILD_TASK=<id>, CHILD_SKILL_ROUTE=<skill>, LOAD=VERIFIED, then its bounded named reason;",
    ):
        require("\n".join(operative_paragraphs(skill)), phrase)
    skill_before, skill_after = skill.split("Only after actual load", 1)
    skill_before = skill_before.split("Before actual load", 1)[1]
    # The thin governor lists exact fields for its explicitly grouped ini event.
    assert tuple(value for value in re.findall(r"`([^`\r\n]+)`", skill_before)
                 if "=" in value) == GOVERNED_PRELOAD_FIELDS, \
        "governor before-load fields must match the exact visible contract"
    assert "LOAD=VERIFIED" not in skill_before and "CHILD_SKILL_ROUTE=" not in skill_before
    require(skill_before, "LOAD=UNVERIFIED")
    require(skill_after, "CHILD_SKILL_ROUTE=<skill>")
    require(skill_after, "LOAD=VERIFIED")

    ordinary = section(child, "Ordinary child dispatch", 3)
    active_child = "\n".join(operative_paragraphs(child))
    for phrase in (
        "Every lifecycle, routing, child or skill event uses one fenced Markdown block whose language is literally ini.",
        "One semantic event gets one block; text, an untyped fence, disconnected inline fields and a combined event are invalid.",
        "Immediately after the block, give one bounded natural sentence naming the exact stable logical child/holon or selected skill and its purpose or observed result.",
        'Use that event\'s exact identities; generic "this ordinary child" or "this skill" does not name them.',
        "These are prospective event forms, never evidence that a template's load, use, return, acceptance, JOIN or completion actually occurred.",
    ):
        require(active_child, phrase)
    require(ordinary, "Before every material ordinary holarchic child dispatch")
    require(ordinary, "producer, review, preparation, recovery and parallel siblings")
    require(ordinary, "including reuse/follow-up dispatch")
    require(ordinary, "emit this visible governor PRE-ACTION block before the host call")
    native_event_block(ordinary, (
        "PARENT_HOLON=<parent>", "CHILD_TASK=<stable logical name>",
        "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "STATUS=OPEN",
        "PURPOSE=<bounded purpose>",
    ), 'Say: "I\'m using the `<CHILD_TASK>` holon to <PURPOSE>."')
    require("\n".join(operative_paragraphs(ordinary)),
            "Substitute the exact stable CHILD_TASK and bounded PURPOSE from that block.")
    for phrase in (
        "Announce the stable logical name before host spawn",
        "bind/report the returned concrete host identity afterward",
        "Missing host-generated ID never excuses silence",
    ):
        require(ordinary, phrase)

    skills = section(child, "Non-governed skill use", 3)
    require(skills, "Before every substantive non-governed skill use")
    require(skills, "emit this visible block before loading or applying the skill")
    selection_spans = []
    selection_units = procedural_prose_units(skills, source_spans=selection_spans)
    selection_boundaries = [span[0] for (kind, value), span in zip(selection_units, selection_spans)
                            if kind == 'paragraph' and normalized_prose_unit(value) == ROLE_METHOD_PARAGRAPHS[0]]
    assert len(selection_boundaries) == 1, 'native skill selection: ambiguous active role/method owner'
    selection = skills[:selection_boundaries[0]]
    native_event_block(selection, ("SKILL_SELECTED=<skill>", "PURPOSE=<bounded purpose>"),
                       'Say: "I\'m using the `<skill>` skill to <purpose>."')
    require(skills, "The sentence names that block's exact SKILL_SELECTED and bounded PURPOSE.")
    require(skills, "relay SKILL_SELECTED and bounded PURPOSE to the governor")
    require(skills, "wait for its actual visible announcement acknowledgement before loading or applying the skill")
    require(skills, "Child-local commentary or a final return cannot substitute for the governor's user-visible pre-use announcement")
    require(skills, "substantive skill use, not every source-document read")
    procedural_parts = procedural_prose_parts(skills)
    for phrase in (
        "Reading selected skill guidance to determine or apply how to act is procedural skill use.",
        "This includes reading to decide applicability even when the decision is to take no further action under that skill.",
        "Selection, a drafted announcement, or a message to the governor is not acknowledgement;",
        "wait for the governor's actual visible announcement acknowledgement before that procedural read.",
        'Calling the read "data" afterward does not erase procedural application.',
        "A later acknowledgement permits future use only and gives no retroactive pre-use conformance credit.",
        "Source-only inspection of a skill as the audit subject is exempt only when its contents do not determine or govern the child's own procedure.",
        "This does not require announcements for arbitrary source-document reads or change the stronger governed child lifecycle below.",
    ):
        assert any(" ".join(phrase.split()) in part for part in procedural_parts), phrase

    check_role_method_composition(documents)

    governed = section(child, "Governed child lifecycle", 3)
    for name in ("audit-state", "audit-assess", "audit-implement", "audit-andon"):
        require(governed, name)
    before = section(governed, "Before actual load", 4)
    after = section(governed, "Only after actual load", 4)
    assert governed.index("#### Before actual load") < governed.index("#### Only after actual load")
    native_event_block(before, GOVERNED_PRELOAD_FIELDS,
                       'Say: "I\'m opening the `<CHILD_TASK>` holon for the `<CHILD_SKILL_SELECTED>` skill to <bounded route purpose>."')
    assert "CHILD_SKILL_ROUTE=" not in before and "LOAD=VERIFIED" not in before
    generic_loaded = section(after, "Generic full-skill LOAD", 5)
    native_loaded = section(after, "Actual native delivery", 5)
    native_event_block(generic_loaded, (
        "CHILD_TASK=<id>", "CHILD_SKILL_ROUTE=<skill>", "LOAD=VERIFIED",
    ), 'Say: "I\'m using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>."')
    native_event_block(native_loaded, (
        "CHILD_TASK=<id>", "CHILD_SKILL_ROUTE=<skill>", "LOAD=VERIFIED",
        "WORKER_TASK=<actual worker>", "LOAD_READY_SHA256=<full READY digest>",
    ), 'Say: "I\'m using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>."')
    require("\n".join(operative_paragraphs(after)),
            "Only independently verified real LOAD evidence for the full selected child content permits the governor to emit:")
    for phrase in (
        "independently verified real LOAD evidence",
        "Never infer actual LOAD from selection, OPEN, packaging or a returned result",
        "USE remains held until the actual parent announcement is acknowledged",
        "USE, RETURN, DISPOSE and GOVERNOR_ACCEPTANCE stay separate",
        "host-owned receipts", "no retrocredit or replay for telemetry",
        "historical hidden audit-state conformance defect remains a defect",
    ):
        require(governed, phrase)

    returns = section(child, "Returns and continuity", 3)
    for phrase in (
        "RETURNED != ACCEPTED != JOINED != PARENT COMPLETE",
        "RETURNED means evidence arrived",
        "ACCEPTED requires independent governor adjudication",
        "JOINED requires actual consumption by the named parent/frontier",
        "PARENT COMPLETE requires that parent's own acceptance and closure gates",
        "JOIN names the consuming parent/frontier",
        "After compaction, handoff or successor change",
        "before the next dispatch or skill use",
        "Periodic topology is supplemental, never a substitute",
    ):
        require(returns, phrase)
    active_returns = "\n".join(operative_paragraphs(returns))
    for phrase in (
        "Emit RETURNED, ACCEPTED, JOINED and PARENT_COMPLETE as separate observed events, each in its own ini block with the exact child, parent, consuming frontier and result.",
        "The natural sentence names that same child and consuming parent/frontier.",
        "PARENT_COMPLETE reports the parent's own state, never automatic child credit.",
        "Preserve literal ini grouping, stable named sentences, separate pre-load and verified-load events, actual same-worker USE acknowledgement and separate RETURNED/ACCEPTED/JOINED/PARENT_COMPLETE evidence at every successor execution.",
        "Restating this contract does not repair earlier owner-restatement or telemetry failures; a fresh successor witness requires actual execution evidence.",
        "Every return/JOIN record retains CHILD_TASK, STATUS=RETURNED, ACCEPTED, JOINED, CONSUMING_PARENT and PARENT_COMPLETE.",
        "ACCEPTED, JOINED and PARENT_COMPLETE each carry their own observed YES, NO or UNVERIFIED value; none follows from another.",
        "Optional EVENT=JOIN names an actual JOIN event and never replaces STATUS=RETURNED.",
    ):
        require(active_returns, phrase)

    # Preserve the load-bearing route semantics when detail moves from the
    # size-limited bootloader to the already packaged reference.
    check_owned_native_units(documents)
    check_route_admission(documents)
    route = section(documents[CHILD], "Governor-routed internal cognition")
    for phrase in (
        "currentness/independence gate", "never infer from discovery/search order",
        "the governor re-derives current state before any later route or transition",
        "NOT_APPLICABLE", "Cheap deterministic Andons bypass the child",
        "A verifier failure in the target package is a bound audit gate failure",
    ):
        require(route, phrase)
    require(documents[TRANSCRIPT], "Pre-action selection is required separately")
    require(documents[TRANSCRIPT], "never claims verified LOAD or a CHILD_SKILL_ROUTE")
    narration = section(documents[TRANSCRIPT], "Child-skill routing observability")
    generic_narration = section(narration, "Generic full-skill LOAD", 3)
    native_event_block(generic_narration, (
        "CHILD_TASK=<id>", "CHILD_SKILL_ROUTE=<selected-child>", "LOAD=VERIFIED",
    ), "I'm using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>.")
    generic_units = tuple(normalized_prose_unit(part) for part in operative_paragraphs(generic_narration))
    assert generic_units == (normalized_prose_unit(GENERIC_LOAD_CONTEXT),
        "I'm using the <CHILD_TASK> holon with the <CHILD_SKILL_ROUTE> skill to <bounded reason for this route>."), \
        "generic full-skill LOAD context or bounded statement differs"
    # Source spans and policy-fixed complete units own this boundary. Inert
    # delimiter text, active prefixes and candidate wording cannot shorten it.
    native_document = documents[TRANSCRIPT].replace("\r\n", "\n")
    native_spans = []
    native_units = procedural_prose_units(native_document, source_spans=native_spans)
    assert len(native_units) == len(native_spans), "native transcript owner: incomplete source spans"
    owning = ("heading", "### Actual native delivery")
    assert native_units.count(owning) == 1, "native transcript owner: missing/duplicate active owning heading"
    start = native_units.index(owning)
    boundaries = [index for index, (kind, value) in enumerate(native_units)
                  if kind == "paragraph" and normalized_prose_unit(value) == normalized_prose_unit(NATIVE_TRANSCRIPT_FOLLOWING_OWNER)]
    assert len(boundaries) == 1, "native transcript owner: missing/duplicate complete active following paragraph"
    end = boundaries[0]
    assert start < end, "native transcript owner: following paragraph precedes owner"
    ancestry = ("# Transcript Contract", "## Child-skill routing observability", "### Actual native delivery")
    for position in (start, end):
        stack = []
        for kind, value in native_units[:position + 1]:
            if kind != "heading":
                continue
            level = len(value.split(" ", 1)[0])
            stack = [item for item in stack if len(item.split(" ", 1)[0]) < level]
            stack.append(value)
        assert tuple(stack) == ancestry, "native transcript owner: active ancestry or ordering differs"
    assert tuple((kind, normalized_prose_unit(value)) for kind, value in native_units[start + 1:end]) == (
        ("paragraph", normalized_prose_unit(NATIVE_LOAD_CONTEXT)),
        ("paragraph", normalized_prose_unit(NATIVE_TRANSCRIPT_LOAD_PREAMBLE)),
        ("paragraph", "I'm using the <CHILD_TASK> holon with the <CHILD_SKILL_ROUTE> skill to <bounded reason for this route>.")), \
        "actual native delivery context must retain complete custody and gates"
    loaded = native_document[native_spans[start][1]:native_spans[end][0]]
    native_event_block(loaded, (
        "CHILD_TASK=<id>", "CHILD_SKILL_ROUTE=<selected-child>", "LOAD=VERIFIED",
        "WORKER_TASK=<actual worker>", "LOAD_READY_SHA256=<full READY digest>",
    ), "I'm using the `<CHILD_TASK>` holon with the `<CHILD_SKILL_ROUTE>` skill to <bounded reason for this route>.")
    require("\n".join(operative_paragraphs(loaded)),
            "The verified route event is separate from the earlier OPEN/LOAD=UNVERIFIED event:")
    require("\n".join(operative_paragraphs(loaded)),
            "resolver selection, and actual full child load have occurred.")
    no_child = native_document[native_spans[end][1]:].split("That branch performs", 1)[0]
    native_event_block(no_child, (
        "PARENT_HOLON=<parent>", "CONSUMING_FRONTIER=<exact frontier>", "CHILD_SKILL_ROUTE=NOT_REQUIRED",
    ), "The `<PARENT_HOLON>` parent uses no internal child at `<CONSUMING_FRONTIER>` because the exact current R0033 route is NOT_REQUIRED.")

    # A later ordinary return projection must not weaken the exact dispatch
    # contract. Check its emitted fields independently; a correct earlier block
    # or duplicate template cannot conceal a conflicting operational template.
    custody = section(documents[CHILD], "Ordinary child-task placement and custody")
    require(custody, "Use the exact ordinary pre-dispatch announcement above before dispatch. For each meaningful return,")
    require(custody, "Selection without actual start remains SELECTED in custody; this observation does not replace pre-dispatch STATUS=OPEN.")
    require(custody, "parent-visible event:")
    active_custody = native_event_block(custody, (
        "PARENT_HOLON=<parent>", "CHILD_TASK=<identity>",
        "HOLON_PATH=<root-to-task path>",
        "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "PURPOSE=<bounded purpose>",
        "AUTHORITY=<delegated ceiling>", "STATUS=RETURNED",
        "ACCEPTED=<YES|NO|UNVERIFIED>", "JOINED=<YES|NO|UNVERIFIED>",
        "CONSUMING_PARENT=<exact consuming parent>", "CONSUMING_FRONTIER=<exact frontier>",
        "RESULT=<exact result>", "PARENT_COMPLETE=<YES|NO|UNVERIFIED>",
    ), 'Say: "The `<CHILD_TASK>` holon returned <exact result> for the `<CONSUMING_PARENT>` parent at `<CONSUMING_FRONTIER>` with <observed acceptance/JOIN/parent-completion disposition>."', optional_join=True)
    assert "parent-visible line:" not in active_custody, "ordinary custody: conflicting inline event"
    require("\n".join(operative_paragraphs(custody)),
            "Bind the exact consuming frontier and result; a parent name alone is insufficient.")
    report = documents[REPORT]
    start = "Ordinary child-task custody (when this report carries an ordinary task):"
    assert report.count(start) == 1, "ordinary report custody block missing or duplicated"
    report = report.split(start, 1)[1].split("Populate dispatch fields", 1)[0]
    projections = re.findall(r"(?m)^- visible_projection: (.+)$", report)
    assert len(projections) == 1, "ordinary report requires one visible projection"
    assert tuple(field.strip() for field in projections[0].split("/")) == (
        "PARENT_HOLON", "CHILD_TASK", "HOLON_PATH", "CHILD_TASK_KIND", "PURPOSE",
        "AUTHORITY", "STATUS", "ACCEPTED", "JOINED", "CONSUMING_PARENT",
        "CONSUMING_FRONTIER", "RESULT", "PARENT_COMPLETE",
    ), "ordinary report visible projection must retain the canonical parent and kind"


def controls(documents: dict[str, str]) -> int:
    documents = control_documents(documents)
    mutations: list[tuple[str, str, str, str]] = []
    for path in (SKILL, CHILD):
        for flag in FLAGS:
            mutations.append((f"drop-{Path(path).name}-{flag}", path, flag, ""))
    for label, path, old, new in (
        ("ordinary-after-action", CHILD, "before the host call", "after the host call"),
        ("ordinary-parent-omitted", CHILD, "PARENT_HOLON=<parent>", "PARENT_UNBOUND=YES"),
        ("ordinary-kind-misclassified", CHILD, "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "CHILD_TASK_KIND=GOVERNED_CHILD_SKILL"),
        ("skill-after-use", CHILD, "before loading or applying the skill", "after applying the skill"),
        ("non-child-skill-unselected", CHILD, "SKILL_SELECTED=<skill>\nPURPOSE=<bounded purpose>", "SKILL_UNSELECTED=YES\nPURPOSE=<bounded purpose>"),
        ("child-local-announcement-substitutes-for-governor", CHILD, "wait for its actual visible announcement acknowledgement before loading or applying the skill", "use child-local commentary immediately and report to the governor later"),
        ("reuse-silent", CHILD, "including reuse/follow-up dispatch", "excluding reuse/follow-up dispatch"),
        ("logical-name-late", CHILD, "before host spawn", "after host spawn"),
        ("generated-id-excuses-silence", CHILD, "Missing host-generated ID never excuses silence", "Missing host-generated ID excuses silence"),
        ("host-identity-unbound", CHILD, "bind/report the returned concrete host identity afterward", "retain only the logical name"),
        ("selected-is-route", CHILD, "CHILD_SKILL_SELECTED=<skill>", "CHILD_SKILL_ROUTE=<skill>"),
        ("load-preverified", CHILD, "STATUS=OPEN\nLOAD=UNVERIFIED", "STATUS=OPEN\nLOAD=VERIFIED"),
        ("bootloader-load-preverified", SKILL, "`STATUS=OPEN`, `LOAD=UNVERIFIED`", "`STATUS=OPEN`, `LOAD=VERIFIED`"),
        ("verified-before-load", CHILD, "#### Only after actual load", "#### Before presumed load"),
        ("use-before-parent-ack", CHILD, "USE remains held until the actual parent announcement is acknowledged", "USE may start before parent acknowledgement"),
        ("stages-inferred", CHILD, "USE, RETURN, DISPOSE and GOVERNOR_ACCEPTANCE stay separate", "RETURN establishes all lifecycle stages"),
        ("retrocredit", CHILD, "no retrocredit or replay for telemetry", "replay for telemetry"),
        ("return-is-acceptance", CHILD, "RETURNED != ACCEPTED != JOINED != PARENT COMPLETE", "RETURNED = ACCEPTED = JOINED = PARENT COMPLETE"),
        ("join-without-consumer", CHILD, "JOIN names the consuming parent/frontier", "JOIN needs no consumer"),
        ("parent-complete-on-join", CHILD, "PARENT COMPLETE requires that parent's own acceptance and closure gates", "PARENT COMPLETE follows automatically from JOINED"),
        ("successor-silent", CHILD, "before the next dispatch or skill use", "at the next periodic topology report"),
        ("topology-substitute", SKILL, "Periodic topology is supplemental, never a substitute", "Periodic topology replaces pre-action announcements"),
        ("recovery-exception-expanded", CHILD, "variants remain scoped native alternatives", "variants waive all currentness gates"),
    ):
        mutations.append((label, path, old, new))
    for name in ("audit-state", "audit-assess", "audit-implement", "audit-andon"):
        mutations.append((f"governed-lifecycle-omits-{name}", CHILD, name, "unnamed-child"))
    for label, path, old, new in mutations:
        changed = dict(documents)
        changed[path] = replace_phrase(changed[path], old, new,
            fence_languages=('text',) if old in FLAGS else ('ini',))
        try:
            check(changed)
        except AssertionError:
            print(f"REJECTED {label}")
        else:
            raise AssertionError(f"false green: {label}")

    # Each operational owner must independently reject the shortened key.
    # Keep correct text elsewhere in two controls to catch substring/any-block
    # regressions, including the original correlated source/checker weakness.
    governed_mutations = 0
    for path in (SKILL, CHILD):
        correct = "CHILD_TASK_KIND=GOVERNED_CHILD_SKILL"
        short = "KIND=GOVERNED_CHILD_SKILL"
        for variant in ("short-key", "historical-decoy", "same-section-decoy",
                        "prefixed-key", "duplicate-short-key"):
            changed = dict(documents)
            replacement = "EXTRA_" + correct if variant == "prefixed-key" else short
            if variant == "duplicate-short-key":
                replacement = correct + ("`, `" if path == SKILL else "\n") + short
            changed[path] = replace_phrase(documents[path], correct, replacement)
            if variant == "historical-decoy":
                changed[path] += "\n## Historical telemetry note\n`" + correct + "`\n"
            elif variant == "same-section-decoy":
                if path == SKILL:
                    decoy = "Reference: `" + "`, `".join(GOVERNED_PRELOAD_FIELDS) + "`.\n"
                    changed[path] = control_replace(changed[path], "Only after actual load", decoy + "Only after actual load")
                else:
                    decoy = "```text\n" + "\n".join(GOVERNED_PRELOAD_FIELDS) + "\n```\n\n"
                    changed[path] = control_replace(changed[path], "#### Only after actual load", decoy + "#### Only after actual load")
            label = f"governed-{Path(path).name}-{variant}"
            try:
                check(changed)
            except AssertionError:
                print(f"REJECTED {label}")
                governed_mutations += 1
            else:
                raise AssertionError(f"false green: {label}")

        # Internal/formal envelope KIND outside the visible owner stays valid.
        internal = dict(documents)
        internal[path] += "\n## Internal host envelope\n```text\nKIND=GOVERNED_CHILD_SKILL\n```\n"
        check(internal)
        print(f"PASS unrelated internal KIND in {Path(path).name}")

    # Keep exact required words present but move the instruction outside the
    # relevant pre-action section: whole-file substring checks would false-green.
    for heading, phrase in (
        ("Ordinary child dispatch", "emit this visible governor PRE-ACTION block before the host call"),
        ("Non-governed skill use", "emit this visible block before loading or applying the skill"),
    ):
        changed = dict(documents)
        changed[CHILD] = replace_phrase(documents[CHILD], phrase, "emit periodic topology") + "\n## Historical note\n" + phrase + "\n"
        try:
            check(changed)
        except AssertionError:
            print(f"REJECTED moved-pre-action-{heading}")
        else:
            raise AssertionError(f"false green: moved-pre-action-{heading}")
    changed = dict(documents)
    contract = control_section(changed[CHILD], "Visible pre-use announcements")
    changed[CHILD] = control_replace(changed[CHILD],
        contract, "\n```text\n" + "\n".join(FLAGS) +
        "\n```\nThe thin governor reports periodic topology for visibility.\n\n", 1)
    assert all(flag in changed[CHILD] for flag in FLAGS)
    try:
        check(changed)
    except AssertionError:
        print("REJECTED vague-topology-only-with-all-six-literals")
    else:
        raise AssertionError("false green: vague topology with all six literals")
    wrapped = dict(documents)
    wrapped[CHILD] = replace_phrase(
        wrapped[CHILD], "Missing host-generated ID never excuses silence",
        "Missing host-generated ID\nnever excuses silence")
    check(wrapped)
    print("PASS equivalent prose line wrapping")
    return len(mutations) + governed_mutations + 3


def ordinary_projection_controls(documents: dict[str, str]) -> int:
    # These controlled source inputs exercise the checker's actual decision.
    # The correct primary pre-dispatch block remains present in every case.
    documents = control_documents(documents)
    custody = control_section(documents[CHILD], "Ordinary child-task placement and custody")
    mutations = (
        ("later-visible-short-kind", CHILD,
         "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "KIND=ORDINARY"),
        ("later-visible-missing-parent", CHILD,
         "PARENT_HOLON=<parent>\n", ""),
        ("later-visible-missing-kind", CHILD,
         "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK\n", ""),
        ("combined-dispatch-return-observed-status", CHILD,
         "Use the exact ordinary pre-dispatch announcement above before dispatch. For each meaningful return,",
         "For dispatch and each meaningful return,"),
        ("selected-custody-replaces-dispatch-open", CHILD,
         "this observation does not replace pre-dispatch STATUS=OPEN",
         "this observation replaces pre-dispatch STATUS=OPEN"),
        ("report-visible-short-kind", REPORT,
         "HOLON_PATH / CHILD_TASK_KIND / PURPOSE", "HOLON_PATH / KIND / PURPOSE"),
        ("report-visible-missing-parent", REPORT,
         "visible_projection: PARENT_HOLON / CHILD_TASK", "visible_projection: CHILD_TASK"),
        ("report-visible-missing-kind", REPORT,
         "HOLON_PATH / CHILD_TASK_KIND / PURPOSE", "HOLON_PATH / PURPOSE"),
    )
    false_greens = []
    for label, path, old, new in mutations:
        changed = dict(documents)
        owner = custody if path == CHILD else control_report_projection(documents[REPORT])
        mutated = replace_phrase(owner, old, new, fence_languages=None if path == REPORT else ('ini',))
        changed[path] = control_replace(documents[path], owner, mutated)
        try:
            check(changed)
        except AssertionError:
            print(f"REJECTED {label}")
        else:
            print(f"FALSE_GREEN {label}")
            false_greens.append(label)
    duplicate = dict(documents)
    duplicate[CHILD] = control_replace(documents[CHILD],
        custody, custody + "\nFor dispatch and each meaningful return, use the parent-visible line: "
        "`CHILD_TASK=<identity>; KIND=ORDINARY; STATUS=<observed status>`.\n", 1)
    try:
        check(duplicate)
    except AssertionError:
        print("REJECTED later-conflicting-duplicate-with-correct-decoy")
    else:
        print("FALSE_GREEN later-conflicting-duplicate-with-correct-decoy")
        false_greens.append("later-conflicting-duplicate-with-correct-decoy")

    # Internal custody vocabulary and supplemental return metadata are valid.
    check(documents)
    print("PASS canonical pre-dispatch and supplemental return projection")
    internal = dict(documents)
    internal[CHILD] += "\n## Internal host envelope\n```text\nKIND=ORDINARY\n```\n"
    check(internal)
    print("PASS internal KIND and task_kind: ORDINARY")
    wrapped = dict(documents)
    wrapped[CHILD] = control_replace(documents[CHILD],
        "CHILD_TASK=<identity>\n", "  CHILD_TASK=<identity>  \n", 1)
    assert wrapped[CHILD] != documents[CHILD]
    check(wrapped)
    print("PASS equivalent return-template line wrapping")
    assert not false_greens, f"false green ordinary projection controls: {false_greens}"
    return len(mutations) + 1


def quoted_history_controls(documents: dict[str, str]) -> int:
    # Quoted evidence cannot add an operative template or repair a wrong one.
    documents = control_documents(documents)
    custody = control_section(documents[CHILD], "Ordinary child-task placement and custody")
    canonical = ("PARENT_HOLON=<parent>\nCHILD_TASK=<identity>\n"
                 "HOLON_PATH=<root-to-task path>\n"
                 "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK\nPURPOSE=<bounded purpose>\n"
                 "AUTHORITY=<delegated ceiling>\nSTATUS=RETURNED\n"
                 "ACCEPTED=<YES|NO|UNVERIFIED>\nJOINED=<YES|NO|UNVERIFIED>\n"
                 "CONSUMING_PARENT=<exact consuming parent>\nCONSUMING_FRONTIER=<exact frontier>\n"
                 "RESULT=<exact result>\nPARENT_COMPLETE=<YES|NO|UNVERIFIED>")
    invalid_quote = (
        "> Historical superseded example, quoted only as evidence of the prior defect: "
        "parent-visible line: `CHILD_TASK=<identity>; KIND=ORDINARY; STATUS=<observed status>`. "
        "This is not an operative template.\n")
    valid_quote = (
        "> Historical quoted record: parent-visible line: `PARENT_HOLON=old-parent; "
        "CHILD_TASK=old-task; CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK; STATUS=RETURNED`. "
        "Quoted evidence only.\n")
    canonical_quote = "> Historical template, quoted evidence only:\n> ```ini\n> " + canonical.replace("\n", "\n> ") + "\n> ```\n"
    cases = [
        ("historical-invalid-projection-blockquote-in-custody", True, custody + "\n" + invalid_quote),
        ("historical-valid-projection-blockquote-in-custody", True, custody + "\n" + valid_quote),
        ("indented-nested-historical-blockquote", True, custody + "\n   > " + invalid_quote),
        ("multiline-historical-blockquote", True,
         custody + "\n" + valid_quote.replace("CHILD_TASK=old-task; ", "CHILD_TASK=old-task;\n> ")),
    ]
    for label, old, new in (
        ("wrong-key", "CHILD_TASK_KIND=", "KIND="),
        ("wrong-kind-value", "CHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK", "CHILD_TASK_KIND=GOVERNED_CHILD_SKILL"),
        ("prefixed-key", "CHILD_TASK_KIND=", "EXTRA_CHILD_TASK_KIND="),
        ("missing-parent", "PARENT_HOLON=<parent>\n", ""),
        ("wrong-field-order", "PARENT_HOLON=<parent>\nCHILD_TASK=<identity>", "CHILD_TASK=<identity>\nPARENT_HOLON=<parent>"),
        ("duplicate-field", "PARENT_HOLON=<parent>", "PARENT_HOLON=<parent>\nPARENT_HOLON=<parent>"),
        ("wrong-return-status", "STATUS=RETURNED", "STATUS=OPEN"),
    ):
        cases.append((label + "-with-correct-quoted-decoy", False,
                      control_replace(custody, old, new) + "\n" + canonical_quote))
    # Keep explicit quotation handling separate from active/fenced instructions.
    conflict = "For ordinary dispatch, use the parent-visible line: `CHILD_TASK=<identity>; KIND=ORDINARY; STATUS=<observed status>`.\n"
    cases.extend((
        ("active-conflict-with-quoted-history", False, custody + "\n" + valid_quote + "\n" + conflict),
        ("fenced-active-conflict-with-quoted-history", False,
         custody + "\n" + valid_quote + "\n```text\n" + conflict + "```\n"),
        ("fenced-literal-quote-marker-is-not-blockquote", False,
         custody + "\n```text\n> " + conflict + "```\n"),
        ("tilde-fenced-literal-quote-marker", False,
         custody + "\n~~~text\n> " + conflict + "~~~\n"),
        ("quoted-only-template-cannot-replace-operative", False,
         replace_phrase(custody, canonical, "NO_OPERATIVE_TEMPLATE") + "\n" + canonical_quote),
        ("quote-boundary-cannot-splice-template", False,
         control_replace(custody, "PARENT_HOLON=<parent>\nCHILD_TASK=<identity>",
                         "PARENT_HOLON=<parent>\n> quoted separator\nCHILD_TASK=<identity>", 1)),
    ))
    mismatches = []
    for label, expected, owner in cases:
        assert owner != custody, label
        changed = dict(documents)
        changed[CHILD] = control_replace(documents[CHILD], custody, owner)
        try:
            check(changed)
            accepted, reason = True, ""
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f"MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}")
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f"quoted history controls: {mismatches}"
    return sum(not expected for _, expected, _ in cases)


def procedural_skill_read_cases(documents: dict[str, str]) -> list[tuple[str, bool, dict[str, str]]]:
    # Source mutations test the procedural-read boundary, not actual model conduct.
    documents = control_documents(documents)
    owner = control_section(control_section(documents[CHILD], "Visible pre-use announcements"),
                    "Non-governed skill use", 3)
    mutations = (
        ("procedural-read-classification-dropped",
         "Reading selected skill guidance to determine or apply how to act is procedural skill use.",
         "Reading selected skill guidance is always source data."),
        ("read-to-decide-inapplicability-exempt",
         "This includes reading to decide applicability even when the decision is to take no further action under that skill.",
         "Reading to decide applicability is exempt if the decision is to take no further action under that skill."),
        ("selection-as-acknowledgement",
         "Selection, a drafted announcement, or a message to the governor is not acknowledgement;",
         "Selection counts as acknowledgement;"),
        ("draft-as-acknowledgement",
         "Selection, a drafted announcement, or a message to the governor is not acknowledgement;",
         "A drafted announcement counts as acknowledgement;"),
        ("pending-message-as-acknowledgement",
         "Selection, a drafted announcement, or a message to the governor is not acknowledgement;",
         "A message to the governor counts as acknowledgement while the reply is pending;"),
        ("procedural-read-before-actual-ack",
         "wait for the governor's actual visible announcement acknowledgement before that procedural read.",
         "Read first and wait for the governor's actual visible announcement acknowledgement afterward."),
        ("posthoc-data-label-erases-application",
         'Calling the read "data" afterward does not erase procedural application.',
         'Calling the read "data" afterward erases procedural application.'),
        ("prospective-acknowledgement-grants-retrocredit",
         "A later acknowledgement permits future use only and gives no retroactive pre-use conformance credit.",
         "A later acknowledgement grants retroactive pre-use conformance credit."),
        ("source-only-audit-exemption-lost",
         "Source-only inspection of a skill as the audit subject is exempt only when its contents do not determine or govern the child's own procedure.",
         "Source-only inspection of a skill as the audit subject always requires a pre-use announcement."),
        ("applied-subject-still-exempt",
         "contents do not determine or govern the child's own procedure.",
         "contents determine or govern the child's own procedure."),
        ("arbitrary-source-reads-gated",
         "This does not require announcements for arbitrary source-document reads or change the stronger governed child lifecycle below.",
         "This requires announcements for all source-document reads."),
        ("governed-lifecycle-collapsed",
         "This does not require announcements for arbitrary source-document reads or change the stronger governed child lifecycle below.",
         "This replaces the stronger governed child lifecycle below."),
    )
    cases = []
    for label, old, new in mutations:
        changed = dict(documents)
        changed[CHILD] = control_replace(documents[CHILD], owner, replace_phrase(owner, old, new))
        cases.append((label, False, changed))
    lead = control_target(owner, "Reading selected skill guidance to determine or apply how to act is procedural skill use.", flexible=True)
    boundary = owner[lead.start - owner.start:]
    changed = dict(documents)
    changed[CHILD] = control_active_owner_replace(documents[CHILD], boundary, "")
    cases.append(("procedural-read-clarification-absent", False, changed))
    moved = dict(changed)
    moved[CHILD] += "\n## Unrelated historical source note\n" + control_active_text(boundary)
    cases.append(("procedural-boundary-moved-outside-owner", False, moved))

    cases.append(("canonical-procedural-and-source-only-boundary", True, dict(documents)))
    wrapped = dict(documents)
    wrapped[CHILD] = control_replace(documents[CHILD], boundary, control_reflow(boundary, '\n'))
    cases.append(("equivalent-procedural-boundary-line-wrapping", True, wrapped))
    for label, example in (
        ("source-only-skill-audit-data",
         "Example: inspecting a SKILL.md solely as the audit subject, without using it to determine the inspector's procedure, is exempt."),
        ("ordinary-unrelated-source-data",
         "Example: an ordinary source-code read that applies no skill guidance needs no skill-use announcement."),
    ):
        changed = dict(documents)
        changed[CHILD] = control_replace(documents[CHILD], owner, control_append(owner, example + "\n\n"))
        cases.append((label, True, changed))
    return cases


def procedural_skill_read_controls(documents: dict[str, str]) -> int:
    mismatches = []
    cases = procedural_skill_read_cases(documents)
    for label, expected, changed in cases:
        try:
            check(changed)
            accepted, reason = True, ""
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f"MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}")
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f"procedural skill read controls: {mismatches}"
    return sum(not expected for _, expected, _ in cases)


def procedural_clause_cases(documents: dict[str, str]) -> list[dict]:
    # Retain the eight review witnesses and directly affected producer cases.
    # Build from supplied source; no preparation files are needed at runtime.
    documents = control_documents(documents)
    child = CHILD
    text = documents[child]
    owner = control_section(control_section(text, "Visible pre-use announcements"), "Non-governed skill use", 3)
    lead = control_target(owner, "Reading selected skill guidance to determine or apply how to act is procedural skill use.", flexible=True)
    boundary_span = owner[lead.start - owner.start:]
    boundary = control_active_text(boundary_span)
    paragraphs = [" ".join(part.split()) for part in boundary.split("\n\n")]
    flat = "\n\n".join(paragraphs)

    def mutation(label, expected, rationale, replacement):
        changed = dict(documents)
        changed[child] = control_active_owner_replace(text, boundary_span, replacement + "\n")
        return {"label": label, "expected_accept": expected, "rationale": rationale,
                "documents": changed}

    cases = [
        {"label": "canonical_new_source", "expected_accept": True,
         "rationale": "Canonical active source must satisfy the bounded check.", "documents": dict(documents)},
        mutation("active_boundary_with_unrelated_historical_quote", True,
                 "An inert quote does not override the retained active discriminator.",
                 boundary + "\n\n> Historical example only: a child once mislabeled applied procedural guidance as data.\n"),
        mutation("new_boundary_absent", False,
                 "Earlier general loading/application text alone does not supply the new discriminator.", ""),
        mutation("sole_new_boundary_is_blockquoted_history", False,
                 "Only source-only historical evidence remains; quoted guidance must not discharge the active discriminator.",
                 "Historical source excerpt retained solely as evidence, with no operative effect:\n\n" +
                 "\n>\n".join("> " + paragraph for paragraph in paragraphs) + "\n"),
        mutation("sole_new_boundary_is_html_comment", False,
                 "Hidden historical source data does not impose the current procedural-read rule.",
                 "<!-- Archived wording for historical comparison only.\n" + flat + "\n-->\n"),
        mutation("sole_new_boundary_is_archived_fenced_example", False,
                 "An explicitly non-operative historical example must not discharge the current discriminator.",
                 "Archived example only; this excerpt is source data and has no operative effect:\n\n```text\n" + flat + "\n```\n"),
        mutation("read_to_decide_exempt_without_decoy", False,
                 "The concrete selection/applicability bypass must be rejected.",
                  replace_phrase(boundary, "skill use. This includes reading to decide applicability even when the decision\nis to take no further action under that skill.",
                                  "skill use, except when checking whether the skill applies.")),
        mutation("ack_is_optional_without_decoy", False,
                 "Removing the required actual ACK cannot preserve the active new rule.",
                  replace_phrase(boundary, "actual visible announcement acknowledgement before that procedural read.",
                                  "eventual announcement, which need not precede the procedural read.")),
    ]

    # The following historical fixtures concatenate complete blocks. Preserve
    # the original owner's separating blank line after projecting active prose.
    boundary += '\n\n'
    ack = "wait for the governor's actual visible announcement acknowledgement before that procedural read."
    replace = replace_phrase

    def add(label: str, expected: bool, replacement: str, rationale: str) -> None:
        changed = dict(documents)
        changed[CHILD] = control_active_owner_replace(documents[CHILD], boundary_span, replacement)
        assert changed[CHILD] != documents[CHILD], label
        cases.append({"label": label, "expected_accept": expected, "rationale": rationale, "documents": changed})

    histories = {
        "quote": "> Historical evidence only.\n" + "".join("> " + line for line in boundary.splitlines(keepends=True)) + "\n",
        "comment": "<!-- Historical evidence only.\n" + boundary + "-->\n\n",
        "fence": "Archived example, not operative.\n```text\n" + boundary + "```\n\n",
    }
    for kind, history in histories.items():
        add("active_plus_" + kind + "_history", True, boundary + history,
            "Adding inert historical guidance must preserve the complete active clauses.")
        add("active_ack_loss_with_" + kind + "_decoy", False,
            replace(boundary, ack, "Actual acknowledgement is optional.") + history,
            "An inert exact ACK clause must not repair its absence from active prose.")
    add("active_plus_mixed_inert_delimiters", True,
        '<!-- A hidden ``` fence and > quote marker.\n-->\n\n'
        '```text\nArchived <!-- unclosed comment and > quote marker.\n```\n\n'
        '> Quoted <!-- comment and ``` fence markers are inert.\n\n' + boundary,
        "Markers inside one inert region must not consume later complete active prose.")
    add("active_prose_after_inline_comments", True,
        "<!-- historical note -->" + boundary.replace('Calling the read',
        '<!-- first note --><!-- second note -->Calling the read', 1),
        "Active complete clauses outside same-line comments remain operative.")
    add("active_prose_after_multiline_comment", True,
        "<!-- historical note\n> ``` remains comment data\n-->" + boundary,
        "A comment close restores active prose without interpreting its hidden markers.")
    add("equivalent_active_line_wrapping", True, "\n".join(boundary.split()) + "\n\n",
        "Whitespace normalization must continue to accept complete active clauses across lines.")
    split = "Reading selected skill guidance to determine or apply how to act is procedural skill use."
    split_span = control_target(boundary, split, flexible=True)
    for kind, separator in (
        ("quote", "\n> historical separator\n\n"),
        ("comment", "<!-- historical separator -->"),
        ("fence", "\n```text\nhistorical separator\n```\n"),
    ):
        add("active_clause_cannot_splice_across_" + kind, False,
            control_replace(boundary, split_span, "Reading selected skill guidance to determine or apply how to act is procedural"
                             + separator + " skill use."),
            "Removing an inert region must not manufacture one contiguous required clause.")
    add("lazy_quote_paragraph_only", False,
        "> Historical paragraph, non-operative:\n" + boundary.replace("\n\n", "\n") + "\n",
        "Unmarked continuation lines in the same quoted paragraph remain historical data.")
    add("lazy_quote_then_active_blank_boundary", True,
        "> Historical paragraph only.\nUnmarked historical continuation.\n\n" + boundary,
        "An unquoted blank line ends the witnessed lazy historical paragraph.")
    add("tilde_fenced_only", False, "Archived example.\n~~~text\n" + boundary + "~~~\n\n",
        "A tilde fenced historical copy must not supply active clauses.")
    add("fence_short_closer_does_not_restore_prose", False,
        "Archived example.\n````text\n```\n" + boundary + "````\n\n",
        "A shorter fence marker cannot close the outer historical example.")
    add("fence_other_marker_does_not_restore_prose", False,
        "Archived example.\n~~~text\n```\n" + boundary + "~~~\n\n",
        "The other fence character cannot close the historical example.")
    add("unclosed_html_history_only", False, "<!-- Historical example.\n" + boundary,
        "An unterminated historical comment cannot provide active clauses.")
    add("unclosed_fenced_history_only", False, "Archived example.\n```text\n" + boundary,
        "An unterminated historical fence cannot provide active clauses.")
    return cases


def procedural_clause_controls(documents: dict[str, str]) -> int:
    cases = procedural_clause_cases(documents)
    mismatches = []
    for case in cases:
        try:
            check(case["documents"])
            accepted, reason = True, ""
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != case["expected_accept"]:
            mismatches.append(case["label"])
            print(f"MISMATCH {case['label']}: expected_accept={case['expected_accept']}; accepted={accepted}; {reason}")
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {case['label']}")
    assert not mismatches, f"procedural clause controls: {mismatches}"
    return sum(not case["expected_accept"] for case in cases)



def compaction_route_controls(documents: dict[str, str]) -> int:
    """Exercise the real checker against the scoped admission/entry conjunction."""
    documents = control_documents(documents)
    def rejected(label: str, changed: dict[str, str], expected: str) -> None:
        try:
            check(changed)
        except AssertionError as exc:
            assert expected in str(exc), f"wrong rejection for {label}: {exc}"
            print(f"REJECTED {label}")
        else:
            raise AssertionError(f"false green: {label}")

    # The stale oracle accepted discretionary compaction once its obsolete
    # gate phrases were restored. Retaining those phrases must not suffice.
    legacy = dict(documents)
    for old, new in (
        ("For normal native-authoritative routing, before loading one child",
         "Before loading one child"),
        ("variants remain scoped native alternatives", "variants are the sole recovery exception"),
        ("A missing native-authoritative gate refuses that native route, not independent POST_COMPACTION_RECONCILIATION.",
         "A missing gate refuses child loading."),
        ("Completed compaction plus governor resumption requires audit-state even when",
         "Completed compaction plus governor resumption may optionally use audit-state if"),
    ):
        legacy[CHILD] = replace_phrase(legacy[CHILD], old, new)
    rejected("stale-oracle-with-discretionary-compaction", legacy, "route.normal-native-gate")

    check(documents)
    print("PASS scoped-native-gates-and-mandatory-compaction-entry")
    mutations = (
        ("normal-gate-deleted", CHILD, "currentness/independence gate",
         "optional gate", "route.normal-native-gate"),
        ("normal-package-check-weakened", CHILD, "the governor verifies executing package",
         "the governor may skip executing package", "route.normal-native-gate"),
        ("normal-precedence-removed", CHILD, "plugin/standalone precedence,",
         "", "route.normal-native-gate"),
        ("native-alternatives-broadened", CHILD, "variants remain scoped native alternatives",
         "variants waive all currentness gates", "route.native-recovery-scope"),
        ("compaction-exempts-all-children", CHILD,
         "Completed compaction plus governor resumption requires audit-state even when",
         "Completed compaction plus governor resumption requires every audit child even when",
         "route.mandatory-compaction-entry"),
        ("compaction-discretionary-in-reference", CHILD,
         "Completed compaction plus governor resumption requires audit-state even when",
         "Completed compaction plus governor resumption may use audit-state only if",
         "route.mandatory-compaction-entry"),
        ("compaction-discretionary-in-governor", SKILL,
         "completed compaction plus governor resumption independently requires audit-state.",
         "completed compaction plus governor resumption optionally selects audit-state.",
         "route.governor-compaction-entry"),
        ("compaction-missing-prospective-announcement", CHILD,
         "actual selected child bytes and prospective visible LOAD/ACK/USE sequence",
         "selected child bytes and later retrospective announcement",
         "route.compaction-pre-use"),
        ("compaction-retroactive-credit", CHILD, "This is not prior-worker credit.",
         "This grants prior-worker credit.", "route.compaction-no-retrocredit"),
        ("compaction-result-authority-promoted", CHILD,
         "grants no canonical currentness, recovery, epoch, lifecycle, mutation, release or closure.",
         "grants canonical currentness, recovery, epoch, lifecycle, mutation, release and closure.",
         "route.compaction-result-ceiling"),
        ("execution-equals-result-authority", SKILL,
         "AUDIT_STATE_EXECUTION_ELIGIBILITY != AUDIT_STATE_RESULT_AUTHORITY",
         "AUDIT_STATE_EXECUTION_ELIGIBILITY = AUDIT_STATE_RESULT_AUTHORITY",
         "route.governor-result-ceiling"),
        ("missing-native-gate-permits-native-route", CHILD,
         "A missing native-authoritative gate refuses that native route, not independent POST_COMPACTION_RECONCILIATION.",
         "A missing native-authoritative gate permits native routing after compaction.",
         "route.native-refusal-scope"),
        ("compaction-exempts-review-independence", CHILD,
         "Route `audit-assess` only for a digest-bound immutable packet under the independence contract",
         "After compaction route `audit-assess` without an immutable packet or independence",
         "route.other-child-gates"),
        ("compaction-exempts-maintainer-currentness", CHILD,
         "after mechanically verified release currentness",
         "after compaction regardless of release currentness",
         "route.other-child-gates"),
        ("compaction-exempts-andon-trigger", CHILD,
         "from L4 only after a non-trivial Andon",
         "after compaction without an Andon",
         "route.other-child-gates"),
    )
    for label, path, old, new, expected in mutations:
        changed = dict(documents)
        changed[path] = replace_phrase(changed[path], old, new)
        rejected(label, changed, expected)

    # Correct words retained only as historical quotation cannot restore a gate.
    quoted = dict(documents)
    gate = ("For normal native-authoritative routing, before loading one child, the governor verifies executing package, "
            "plugin/standalone precedence, audit object, authority ceiling, and the currentness/independence gate, then names exactly one child.")
    quoted[CHILD] = replace_phrase(quoted[CHILD], gate, "> Historical gate: " + gate + "\n")
    rejected("normal-gate-only-in-historical-quote", quoted, "route.normal-native-gate")

    wrapped = dict(documents)
    wrapped[CHILD] = replace_phrase(
        wrapped[CHILD], "For normal native-authoritative routing, before loading one child",
        "For normal native-authoritative routing,\nbefore loading one child")
    check(wrapped)
    print("PASS equivalent-scoped-gate-line-wrapping")
    return len(mutations) + 2



def role_method_composition_cases(documents: dict[str, str]) -> list[tuple[str, bool, dict[str, str]]]:
    documents = control_documents(documents)
    text = documents[CHILD]
    owner = control_section(control_section(text, "Visible pre-use announcements"), "Non-governed skill use", 3)
    contract_span = control_between(owner, ROLE_METHOD_PARAGRAPHS[0],
        "Reading selected skill guidance to determine or apply how to act is procedural skill use.")
    contract = control_active_text(contract_span)
    cases = [("admitted-composition-and-fresh-assessor-own-methods", True, dict(documents))]

    def add(label: str, expected: bool, replacement: str) -> None:
        changed = dict(documents)
        changed[CHILD] = control_active_owner_replace(text, contract_span, replacement + "\n\n")
        assert changed[CHILD] != text or expected, label
        cases.append((label, expected, changed))

    for flag in ROLE_METHOD_FLAGS:
        add("missing-invariant-" + flag.split("=")[0].strip(), False,
            replace_phrase(contract, flag, "OMITTED_COMPOSITION_INVARIANT"))
    for label, old, new in (
        ("role-and-method-conflated", ROLE_METHOD_PARAGRAPHS[0],
         "Governed role selection determines which ordinary procedural method must be used."),
        ("method-substitutes-for-admission", "Ordinary procedural skill use is not governed admission, does not substitute for or bypass it, and never counts as audit-child use.",
         "Ordinary procedural skill use substitutes for governed admission and counts as audit-child use."),
        ("method-grants-audit-child-credit", "and never counts as audit-child use.",
         "and counts as audit-child use."),
        ("blanket-method-ban", ROLE_METHOD_PARAGRAPHS[3],
         "An admitted governed child must not use any ordinary procedural skill."),
        ("silent-nested-method-load", ROLE_METHOD_PARAGRAPHS[4],
         "A governed child may load supporting procedural skills silently and report them afterward."),
        ("child-local-ack-substitute", "the parent governor must visibly announce selection and purpose;",
         "child-local commentary supplies selection and purpose without the parent governor;"),
        ("retrospective-method-credit", "the child must receive the actual acknowledgement before its own actual skill load and procedural use.",
         "The child may load and use the method first and obtain retrospective acknowledgement later."),
        ("assessor-inherits-preparation-context", "It must never inherit preparation context to obtain methods.",
         "It may inherit preparation context to obtain methods."),
        ("assessor-method-before-envelope", "A fresh audit-assess child receives its immutable digest-bound envelope and satisfies admission and fresh-context independence first, then selects and loads its own applicable methods.",
         "An audit-assess child selects and loads inherited methods before its immutable envelope and admission checks."),
        ("lifecycle-weakened-by-method", "every governed lifecycle requirement, independence requirement and authority ceiling.",
         "only the requirements chosen by its procedural method."),
        ("independence-waived-by-method", "independence requirement and authority ceiling.",
         "authority ceiling while waiving fresh-context independence."),
        ("method-grants-authority", "It grants no mutation, currentness, result, lifecycle, release or closure authority.",
         "It grants mutation and currentness authority when the procedural method requests them."),
        ("method-is-child-delegation", ROLE_METHOD_PARAGRAPHS[7],
         "A procedural method load authorizes child delegation and relaxes CHILD_ROUTING=FORBIDDEN."),
        ("mandatory-method-or-ceremonial-child", ROLE_METHOD_PARAGRAPHS[8],
         "Both procedural method use and a governed child route are mandatory to demonstrate composition."),
        ("TDD-grants-audit-implement-mutation", "these examples grant no audit-implement mutation permission and mandate no method or ceremonial child use.",
         "TDD grants audit-implement mutation permission and every example must be used."),
    ):
        add(label, False, replace_phrase(contract, old, new))
    for gate in ("actual package", "transport", "lifecycle", "currentness", "independence", "authority"):
        admission = ROLE_METHOD_PARAGRAPHS[2]
        add("admission-gate-waived-" + gate.replace(" ", "-"), False,
            replace_phrase(contract, admission, admission + " The " + gate + " gate may be waived by a procedural method."))
    add("literals-without-operative-composition", False,
        ROLE_METHOD_PARAGRAPHS[0] + "\n\n" + "\n".join("`" + flag + "`" for flag in ROLE_METHOD_FLAGS))
    histories = {
        "quote": "\n".join("> " + line for line in contract.splitlines()),
        "comment": "<!-- Historical source only.\n" + contract + "\n-->",
        "fence": "Archived source only.\n```text\n" + contract + "\n```",
        "indented-code": "\n".join("    " + line for line in contract.splitlines()),
        "inline-quotation": 'Superseded historical quotation only: "' + " ".join(contract.split()) + '"',
    }
    for kind, history in histories.items():
        add("composition-only-in-" + kind, False, history)
    add("active-admission-prefix-with-compaction-waiver", False,
        replace_phrase(contract, ROLE_METHOD_PARAGRAPHS[2], ROLE_METHOD_PARAGRAPHS[2] +
                       " After compaction audit-assess may skip its immutable packet and independence gates."))
    # Preserve the three independently observed false-acceptance witnesses.
    witnesses = (
        "An ordinary procedural skill may substitute for governed child admission and its successful use counts as audit-child use.",
        "An audit-assess child may inherit preparation context to obtain its procedural methods before independent admission.",
        "Selecting a governed audit role forbids every ordinary procedural skill inside that child.",
    )
    for index, witness in enumerate(witnesses, 1):
        add(f"retained-RED-witness-{index}", False, contract + "\n\n" + witness)
    # Exact independent review witnesses C02-C08, retained in the normal entry.
    witness = "An ordinary procedural skill may substitute for governed child admission and its successful use counts as audit-child use."
    for label, expected, insertion in (
        ("C02-unadorned-operative-waiver-negative", False, witness),
        ("C03-active-paragraph-with-indented-continuation-negative", False,
         witness.replace(" and its", "\n    and its")),
        ("C04-active-waiver-with-trailing-inert-comment-negative", False,
         witness + " <!-- This comment adds no permission. -->"),
        ("C05-inert-blockquote-history-positive", True,
         "> Superseded historical statement: " + witness),
        ("C06-inert-indented-code-positive", True, "    " + witness),
        ("C07-active-waiver-with-following-owner-prefix-negative", False,
         "Reading selected skill guidance has an exception: " + witness),
        ("C08-inert-following-owner-prefix-before-active-waiver-negative", False,
         "<!-- Reading selected skill guidance: cross-reference only. -->\n\n" + witness),
    ):
        add(label, expected, contract + "\n\n" + insertion)
    duplicate_boundary = dict(documents)
    end = contract_span.end
    duplicate_boundary[CHILD] = (text[:end] +
        "Reading selected skill guidance to determine or apply how to act is procedural skill use. " +
        witness + " " + text[end:])
    cases.append(("composition-duplicate-following-owner-in-same-active-paragraph", False, duplicate_boundary))
    moved = dict(documents)
    moved[CHILD] = control_active_owner_replace(text, contract_span, '') + "\n## Historical composition note\n" + contract + "\n"
    cases.append(("composition-moved-outside-owner", False, moved))
    add("equivalent-admitted-and-fresh-assessor-line-wrapping", True,
        "\n\n".join("\n".join(paragraph.split()) for paragraph in contract.split("\n\n")))
    add("active-composition-with-inert-opposite-history", True,
        contract + "\n\n> Superseded opposite claims, retained only as history:\n" +
        "\n".join("> " + witness for witness in witnesses))
    return cases


def role_method_composition_controls(documents: dict[str, str]) -> int:
    mismatches = []
    cases = role_method_composition_cases(documents)
    for label, expected, changed in cases:
        try:
            check(changed)
            accepted, reason = True, ""
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f"MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}")
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f"role/method composition controls: {mismatches}"
    return sum(not expected for _, expected, _ in cases)


def native_statement_cases(documents: dict[str, str]) -> list[tuple[str, bool, dict[str, str]]]:
    """Controlled source changes exercise the existing check(), never a parallel oracle."""
    documents = control_documents(documents)
    cases = [("native-canonical-ini-events", True, dict(documents))]
    child = control_section(documents[CHILD], "Visible pre-use announcements")
    governed = control_section(child, "Governed child lifecycle", 3)
    route = control_section(documents[TRANSCRIPT], "Child-skill routing observability")
    loaded_end = control_target(route, NATIVE_TRANSCRIPT_FOLLOWING_OWNER, flexible=True)
    no_child_start = control_target(route, "`NOT_REQUIRED` instead emits", flexible=True)
    no_child_end = control_target(route, "That branch performs", flexible=True)
    owners = (
        ("ordinary", CHILD, control_section(child, "Ordinary child dispatch", 3)),
        ("skill", CHILD, control_section(child, "Non-governed skill use", 3)),
        ("governed-open", CHILD, control_section(governed, "Before actual load", 4)),
        ("governed-loaded", CHILD, control_section(control_section(governed, "Only after actual load", 4), "Generic full-skill LOAD", 5)),
        ("return", CHILD, control_section(documents[CHILD], "Ordinary child-task placement and custody")),
        ("transcript-loaded", TRANSCRIPT, control_section(route, "Generic full-skill LOAD", 3)),
        ("transcript-no-child", TRANSCRIPT, route[no_child_start.end - route.start:no_child_end.start - route.start]),
    )

    def add(label: str, path: str, owner: str, replacement: str, expected: bool = False) -> None:
        changed = dict(documents)
        assert owner != replacement, label
        changed[path] = control_replace(documents[path], owner, replacement)
        assert changed[path] != documents[path], label
        cases.append((label, expected, changed))

    for label, path, owner in owners:
        event = control_event(owner)
        for bad_language in ("text", "", "INI"):
            add(f"native-{label}-fence-{bad_language or 'untyped'}", path, owner,
                control_replace(owner, event['opening'], event['marker'] + bad_language + "\n"))
        inline = "`" + "; ".join(event['body'].rstrip('\n').splitlines()) + "`"
        add(f"native-{label}-disconnected-inline-fields", path, owner,
            control_replace(owner, event['block'], inline))
        separated = "\n\n".join("```ini\n" + field + "\n```" for field in event['body'].rstrip('\n').splitlines())
        add(f"native-{label}-split-event", path, owner, control_replace(owner, event['block'], separated))
        add(f"native-{label}-duplicate-event", path, owner,
            control_replace(owner, event['block'], event['block'] + "\n\n" + event['block']))
        add(f"native-{label}-commented-only-event", path, owner,
            control_replace(owner, event['block'], "<!--\n" + event['block'] + "\n-->"))
    ordinary = owners[0][2]
    for label, replacement in (
        ("generic-child", "I'm using this ordinary child to <PURPOSE>."),
        ("host-id-instead-of-stable-child", "I'm using the `<host-id>` holon to <PURPOSE>."),
        ("unbound-purpose", "I'm using the `<CHILD_TASK>` holon to do work."),
    ):
        target = control_target(ordinary,
            "I'm using the `<CHILD_TASK>` holon to <PURPOSE>.", flexible=True)
        add("native-ordinary-" + label, CHILD, ordinary,
            control_replace(ordinary, target, replacement))
    add("native-skill-generic-name", CHILD, owners[1][2],
        control_replace(owners[1][2], "I'm using the `<skill>` skill to <purpose>.", "I'm using this skill to <purpose>."))
    # Locate the actual active clause. An identical or differently formatted
    # historical copy must neither select the target nor be rewritten with it.
    start, end = active_prose_match(ordinary,
        r"Substitute\s+the\s+exact\s+stable\s+`?CHILD_TASK`?\s+and\s+bounded\s+`?PURPOSE`?\s+from\s+that\s+block\.")
    add('native-ordinary-identity-purpose-binding-lost', CHILD, ordinary,
        ordinary[:start] + 'Use any convenient child name and purpose.' + ordinary[end:])
    for label, path, old, new in (
        ("native-selected-skill-binding-lost", CHILD,
         "The sentence names that block's exact SKILL_SELECTED and bounded PURPOSE.", "The sentence may name another selected skill."),
        ("native-lifecycle-states-combined", CHILD,
         "Emit RETURNED, ACCEPTED, JOINED and PARENT_COMPLETE as separate observed events, each in its own `ini` block with the exact child, parent, consuming frontier and result.",
         "Emit RETURNED, ACCEPTED, JOINED and PARENT_COMPLETE together in one combined event."),
        ("native-successor-format-loss", CHILD,
         "Preserve literal `ini` grouping, stable named sentences, separate pre-load and verified-load events, actual same-worker USE acknowledgement and separate RETURNED/ACCEPTED/JOINED/PARENT_COMPLETE evidence at every successor execution.",
         "A successor may use untyped prose and inherit earlier LOAD and USE credit."),
        ("native-retroactive-owner-restatement-credit", CHILD,
         "Restating this contract does not repair earlier owner-restatement or telemetry failures; a fresh successor witness requires actual execution evidence.",
         "Restating this contract repairs earlier owner-restatement and telemetry failures and proves successor execution."),
        ("native-template-mints-lifecycle-credit", CHILD,
         "These are prospective event forms, never evidence that a template's load, use, return, acceptance, JOIN or completion actually occurred.",
         "These templates prove that every lifecycle transition occurred."),
        ("native-parent-name-without-frontier", CHILD,
         "Bind the exact consuming frontier and result; a parent name alone is insufficient.",
         "A parent name alone establishes the consuming frontier and result."),
        ("native-transcript-merges-open-loaded", TRANSCRIPT,
         "The verified route event is separate from the earlier OPEN/LOAD=UNVERIFIED event:",
         "The verified route event replaces the earlier OPEN event even before actual load:"),
        ("native-reference-partial-load-as-verified", CHILD,
         "Only independently verified real LOAD evidence for the full selected child content permits the governor to emit:",
         "A partial selected child snippet permits the governor to emit:"),
        ("native-transcript-partial-load-as-verified", TRANSCRIPT,
         "resolver selection, and actual full child load have occurred.",
         "resolver selection and a partial snippet read have occurred."),
    ):
        add(label, path, documents[path], replace_phrase(documents[path], old, new))
    for label, path, owner in (owners[2], owners[3], owners[4], owners[5]):
        field = "CHILD_TASK=<identity>" if label == "return" else "CHILD_TASK=<id>"
        add(f"native-{label}-child-identity-omitted", path, owner, control_replace(owner, field + "\n", ""))
    for key in ("CONSUMING_FRONTIER=<exact frontier>", "RESULT=<exact result>"):
        add("native-return-missing-" + key.split("=")[0], CHILD, owners[4][2],
            control_replace(owners[4][2], key + "\n", ""))
    add("native-return-status-combines-transitions", CHILD, owners[4][2],
        control_replace(owners[4][2], "STATUS=RETURNED", "STATUS=RETURNED/ACCEPTED/JOINED/PARENT_COMPLETE"))
    add("native-return-sentence-omits-consuming-frontier", CHILD, owners[4][2],
        control_replace(owners[4][2], " parent at `<CONSUMING_FRONTIER>` with ", " parent with "))
    add("native-return-sentence-generic-child", CHILD, owners[4][2],
        control_replace(owners[4][2], 'Say: "The `<CHILD_TASK>` holon returned ', 'Say: "This ordinary child returned '))
    returned_event = control_event(owners[4][2])
    joined = control_replace(owners[4][2], returned_event['opening'], returned_event['opening'] + 'EVENT=JOIN\n')
    add("native-return-optional-event-join-with-required-status", CHILD, owners[4][2], joined, True)
    for field in ("STATUS=RETURNED", "ACCEPTED=<YES|NO|UNVERIFIED>", "JOINED=<YES|NO|UNVERIFIED>",
                  "CONSUMING_PARENT=<exact consuming parent>", "PARENT_COMPLETE=<YES|NO|UNVERIFIED>"):
        add("native-return-event-join-missing-" + field.split("=")[0], CHILD, owners[4][2],
            control_replace(joined, field + "\n", ""))
    projection = control_report_projection(documents[REPORT])
    for key in ("ACCEPTED", "JOINED", "CONSUMING_PARENT", "CONSUMING_FRONTIER", "RESULT", "PARENT_COMPLETE"):
        add("native-report-projection-missing-" + key, REPORT, documents[REPORT],
            control_replace(documents[REPORT], projection, control_replace(projection, " / " + key, "")))
    for label, old, new in (
        ("ordinary-inline-directive", "emit one `ini` block with `PARENT_HOLON=<parent>`", "visibly emit `PARENT_HOLON=<parent>`"),
        ("skill-inline-directive", "emit one `ini` block with `SKILL_SELECTED=<skill>`", "visibly emit `SKILL_SELECTED=<skill>`"),
        ("preload-inline-directive", "Before actual load, emit one `ini` block with", "Before actual load, emit"),
        ("verified-load-not-separate", "emit a separate `ini` block with", "emit in the earlier OPEN block with"),
        ("ordinary-generic-child", "I'm using the `<CHILD_TASK>` holon to <PURPOSE>.", "I'm using this ordinary child to <PURPOSE>."),
    ):
        add("native-governor-" + label, SKILL, documents[SKILL],
            replace_phrase(documents[SKILL], old, new))
    native_child = control_section(control_section(governed, "Only after actual load", 4), "Actual native delivery", 5)
    native_transcript = control_section(route, "Actual native delivery", 3)
    native_transcript = native_transcript[:loaded_end.start - native_transcript.start]
    for label, path, owner in (("governed-loaded", CHILD, native_child), ("transcript-loaded", TRANSCRIPT, native_transcript)):
        for field in ("WORKER_TASK=<actual worker>", "LOAD_READY_SHA256=<full READY digest>"):
            add("native-" + label + "-missing-" + field.split("=")[0], path, owner,
                control_replace(owner, field + "\n", ""))
    # Each complete source owner is checked independently: a valid generic
    # three-field event cannot repair missing native custody or grant authority.
    for label, path, owner in (("generic-child", CHILD, owners[3][2]), ("generic-transcript", TRANSCRIPT, owners[5][2])):
        add("context-" + label + "-full-load-without-native-READY", path, owner,
            control_replace(owner, GENERIC_LOAD_CONTEXT, "\n".join(GENERIC_LOAD_CONTEXT.split())), True)
        add("context-" + label + "-invented-native-custody", path, owner,
            control_replace(owner, "LOAD=VERIFIED\n", "LOAD=VERIFIED\nWORKER_TASK=<actual worker>\nLOAD_READY_SHA256=<full READY digest>\n"))
        for defect, changed in (
            ("partial-skill-read", GENERIC_LOAD_CONTEXT.replace("Actual full\nselected skill LOAD", "Partial skill reading")),
            ("ack-after-use", "Generic skill use may precede actual visible parent acknowledgement."),
            ("native-authority-credit", "The generic form grants native READY, host-stage, currentness, epoch and recovery authority and releases native USE."),
            ("compaction-gated-on-native", GENERIC_LOAD_CONTEXT.replace("does not\nblock", "blocks")),
        ):
            add("context-" + label + "-" + defect, path, owner, control_replace(owner, GENERIC_LOAD_CONTEXT, changed))
    for label, path, owner in (("actual-native-child", CHILD, native_child), ("actual-native-transcript", TRANSCRIPT, native_transcript)):
        add("context-" + label + "-full-native-custody", path, owner,
            control_replace(owner, NATIVE_LOAD_CONTEXT, "\n".join(NATIVE_LOAD_CONTEXT.split())), True)
        add("context-" + label + "-generic-form-as-native", path, owner,
            control_replace(owner, "WORKER_TASK=<actual worker>\nLOAD_READY_SHA256=<full READY digest>\n", ""))
        for defect, changed in (
            ("partial-load", NATIVE_LOAD_CONTEXT.replace("verified full selected skill LOAD", "presumed partial skill reading")),
            ("generic-bypasses-native-proof", "The generic form satisfies native readiness, liveness, ACK and same-worker USE without a native READY tuple."),
        ):
            add("context-" + label + "-" + defect, path, owner, control_replace(owner, NATIVE_LOAD_CONTEXT, changed))
        opening = control_event(owner)['opening']
        for language in ("text", ""):
            add("context-" + label + "-fence-" + (language or "untyped"), path, owner,
                control_replace(owner, opening, "```" + language + "\n"))
    for label, path, owner in owners[:4]:
        paragraphs = [raw for kind, raw in procedural_prose_units(owner) if kind == 'paragraph']
        sentence = next(re.search(r'Say: "([^\n]+?)"', raw)[0] for raw in paragraphs if re.search(r'Say: "([^\n]+?)"', raw))
        sentence_span = control_target(owner, sentence, flexible=True)
        event = control_event(owner)
        # Apply both edits in the original owner coordinates; the sentence is
        # after the event, so removing it cannot move the event's closing fence.
        origin = owner.start
        a, b = sentence_span.start - origin, sentence_span.end - origin
        replacement = str(owner)[:a] + str(owner)[b:]
        close = event['body_end']
        replacement = replacement[:close] + sentence + '\n' + replacement[close:]
        add(f"native-{label}-sentence-inside-fence", path, owner, replacement)
    waiver = "The generic full-skill LOAD form satisfies actual native delivery and releases native USE without READY, ACK or liveness proof."
    history_prefixes = (
        ("comment", "<!-- The selected child is exactly one -->"),
        ("quote", "> The selected child is exactly one"),
        ("indented", "    The selected child is exactly one"),
    )
    for kind, history in history_prefixes:
        add("owner-boundary-" + kind + "-history-waiver", TRANSCRIPT, native_transcript,
            str(native_transcript) + history + "\n\n" + waiver + "\n\n")
        add("owner-boundary-" + kind + "-harmless-history", TRANSCRIPT, native_transcript,
            str(native_transcript) + history + "\n\n", True)
    for label, insertion in (
        ("plain-active-waiver", waiver),
        ("alternate-active-waiver", "Native delivery may proceed before parent acknowledgement; its worker and READY evidence are optional."),
        ("active-prefix-is-not-boundary", "The selected child is exactly one exception: " + waiver),
        ("intervening-active-heading", "#### An unreviewed native permission"),
        ("intervening-numbered-waiver", "1. " + waiver),
    ):
        add("owner-boundary-" + label, TRANSCRIPT, native_transcript, str(native_transcript) + insertion + "\n\n")
    native_section = control_section(route, "Actual native delivery", 3)
    complete_boundary = control_target(native_section, NATIVE_TRANSCRIPT_FOLLOWING_OWNER, flexible=True)
    no_child_intro = "Those governor-only cases emit no selected-child announcement. Exact current `NOT_REQUIRED` instead emits the explicit no-child projection:"
    for label, replacement in (
        ("missing-genuine-paragraph", no_child_intro),
        ("shortened-genuine-paragraph", "The selected child is exactly one.\n\n" + no_child_intro),
        ("duplicate-genuine-paragraph", NATIVE_TRANSCRIPT_FOLLOWING_OWNER + "\n\n" + NATIVE_TRANSCRIPT_FOLLOWING_OWNER),
        ("genuine-prefix-plus-active-waiver", NATIVE_TRANSCRIPT_FOLLOWING_OWNER + " " + waiver),
        ("genuine-boundary-moved-under-other-owner", "### A different active owner\n\n" + NATIVE_TRANSCRIPT_FOLLOWING_OWNER),
    ):
        add("owner-boundary-" + label, TRANSCRIPT, native_section,
            control_replace(native_section, complete_boundary, replacement))
    for kind, history in (
        ("comment", "<!--\n" + NATIVE_TRANSCRIPT_FOLLOWING_OWNER + "\n-->"),
        ("quote", "\n".join("> " + line for line in NATIVE_TRANSCRIPT_FOLLOWING_OWNER.splitlines())),
        ("indented", "\n".join("    " + line for line in NATIVE_TRANSCRIPT_FOLLOWING_OWNER.splitlines())),
    ):
        add("owner-boundary-complete-" + kind + "-history", TRANSCRIPT, native_transcript,
            str(native_transcript) + history + "\n\n", True)
    reflowed_owner = "\n".join(NATIVE_TRANSCRIPT_FOLLOWING_OWNER.split())
    if str(complete_boundary) == reflowed_owner:
        reflowed_owner = " ".join(NATIVE_TRANSCRIPT_FOLLOWING_OWNER.split())
    add("owner-boundary-genuine-paragraph-reflow", TRANSCRIPT, native_section,
        control_replace(native_section, complete_boundary, reflowed_owner), True)
    return cases


def native_statement_controls(documents: dict[str, str]) -> int:
    cases = native_statement_cases(documents)
    mismatches = []
    for label, expected, changed in cases:
        try:
            check(changed)
            accepted, reason = True, ""
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f"MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}")
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f"native statement controls: {mismatches}"
    return sum(not expected for _, expected, _ in cases)


def route_control_fixture(documents: dict[str, str]) -> dict[str, str]:
    child, skill = documents[CHILD], documents[SKILL]
    # Validate the actual complete owners before constructing mutation targets.
    # Inert history may add raw paragraphs or duplicate raw heading text. Build
    # these controls from the validated active route units; expected policy still
    # comes only from check_owned_route_units' independent sixteen literals.
    check_owned_route_units(child, skill)
    active_route = owned_heading_span(child,
        ("# Child-Agent Review Loops", "## Governor-routed internal cognition",
         "### Mandatory compaction entry and result ceiling"), "## Non-authority rule")
    paragraphs = [value for kind, value in active_route]
    child = child.replace('\r\n', '\n')
    owner = control_between(child, '### Mandatory compaction entry and result ceiling\n',
                            '## Non-authority rule\n', after_first=True)
    child = control_replace(child, owner, '\n' + '\n\n'.join(paragraphs) + '\n\n')
    documents = dict(documents)
    documents[CHILD] = child
    return documents


def source_convergence_cases(documents: dict[str, str]) -> list[tuple[str, bool, dict[str, str]]]:
    # Breaks caught: active owner additions/removal/relocation, erased heading or
    # item evidence, and historical timing/worker/reacquisition substitutions.
    # Source paragraphs below locate mutations; they never generate expected
    # owner values for the consumer being checked.
    documents = route_control_fixture({path: text.replace('\r\n', '\n')
                                       for path, text in documents.items()})
    cases = []
    child, skill = documents[CHILD], documents[SKILL]
    def owner(text, first, following):
        return control_between(text, first, following, after_first=True)

    def add(label, expected, path, old, new, *, block=False):
        assert old != new, label
        changed = dict(documents)
        changed[path] = control_replace(documents[path], old, new, flexible=True, block=block)
        assert changed[path] != documents[path], label
        cases.append((label, expected, changed))

    route_start = '### Mandatory compaction entry and result ceiling\n'
    route_end = '## Non-authority rule\n'
    route = owner(child, route_start, route_end)
    paragraphs = [value for kind, value in procedural_prose_units(route)]
    normal, admission, consideration, separation = paragraphs[3:7]
    waiver = 'For this operative route, audit-assess may now bypass packet binding and independence after compaction.'
    for label, target in (
        ('admission_waiver_after_consideration', consideration),
        ('admission_waiver_after_separation_rule', separation),
    ):
        add(label, False, CHILD, target, target + '\n\n' + waiver)
    add('admission_waiver_after_inline_comment_separator', False, CHILD, consideration,
        consideration + '<!-- retained note --> ' + waiver)
    for level in (3, 4):
        add('normal_gate_moved_under_historical_heading_' + str(level), False, CHILD, normal,
            'The operative normal route has no admission gate.\n\n' + '#' * level + ' Historical gate excerpt only; superseded\n\n' + normal)
    quote_heading = '> Retained historical note.\n#### Operative exception\n' + waiver
    for label, expected, suffix in (
        ('admission_quote_cannot_hide_operative_heading', False, quote_heading),
        ('same_heading_without_preceding_quote', False, '#### Operative exception\n' + waiver),
        ('same_heading_after_unquoted_blank_boundary', False, '> Retained historical note.\n\n#### Operative exception\n' + waiver),
        ('same_heading_and_waiver_actually_quoted', True, '> Retained historical note.\n> #### Operative exception\n> ' + waiver),
    ):
        add(label, expected, CHILD, admission, admission + '\n\n' + suffix)
    for label, target, extra in (
        ('mandatory_currentness_prerequisite_subsequent', paragraphs[0], 'For this mandatory compaction entry, audit-state execution must wait until canonical currentness and a qualified epoch are present.'),
        ('mandatory_extended_to_assess_subsequent', paragraphs[0], 'The same independent compaction entry also admits audit-assess without its packet or independence gate.'),
        ('result_authority_promoted_subsequent', paragraphs[2], 'This reconciliation result now establishes canonical currentness and native recovery authority.'),
    ):
        add(label, False, CHILD, target, target + '\n\n' + extra)

    neutral = 'This local instruction changes the next decision without any further review.'
    # Exercise every finite owner boundary, including the genuine next owner.
    for index in range(17):
        before = paragraphs[:index]
        after = paragraphs[index:]
        for form, expected, extra in (
            ('active', False, neutral),
            ('quoted', True, '> ' + neutral),
        ):
            replacement = '\n\n'.join(before + [extra] + after)
            add(f'closed-route-boundary-{index:02d}-{form}', expected, CHILD, route,
                '\n' + replacement + '\n\n\n')
    for form, expected, extra in (
        ('comment', True, '<!-- ' + neutral + '\n## Non-authority rule\n-->'),
        ('fence', True, '~~~text\n## Non-authority rule\n' + neutral + '\n~~~'),
        ('indent', True, '    ## Non-authority rule\n    ' + neutral),
        ('heading-2', False, '## An unexpected owner\n\n' + neutral),
        ('heading-3', False, '### An unexpected owner\n\n' + neutral),
        ('heading-4', False, '#### An unexpected owner\n\n' + neutral),
        ('comment-suffix', False, '<!-- retained note --> ' + neutral),
        ('quote-heading', False, '> Retained historical note.\n#### Active instruction\n' + neutral),
        ('quote-then-comment-hides-no-heading', True, '> Retained historical note.\n<!--\n## Non-authority rule\n-->'),
        ('quote-then-comment-keeps-active-suffix', False, '> Retained historical note.\n<!-- retained note -->\n' + neutral),
        ('quote-then-comment-quoted-suffix', True, '> Retained historical note.\n<!-- retained note -->\n> ' + neutral),
    ):
        add('closed-route-end-' + form, expected, CHILD, route, route + extra + '\n\n')
    add('closed-route-wrong-parent-ancestry', False, CHILD, '## Governor-routed internal cognition\n',
        '## An unrelated owner\n### Governor-routed internal cognition\n')
    add('closed-route-duplicate-owner-heading', False, CHILD, route_start, route_start + '\n' + route_start)
    add('closed-route-duplicate-end-heading', False, CHILD, route_end, route_end + '\n' + route_end)
    add('closed-route-truncated-by-early-end', False, CHILD, paragraphs[15],
        route_end + '\n' + paragraphs[15])
    end_lead = 'Child agents are review loops, not independent authorization authorities.'
    add('closed-route-wrong-end-owner-clause', False, CHILD, end_lead,
        'This heading now owns a different local policy.')
    end_span = control_target(child, route_end)
    add('closed-route-end-without-owned-content', False, CHILD, child,
        control_replace(child, end_span, '') + '\n' + route_end)
    add('closed-route-quoted-note-before-genuine-end', True, CHILD, route_end,
        '> Retained historical note.\n' + route_end, block=True)

    runtime = owner(skill, '## Runtime Loop\n', '\n1. Safety read:')
    add('runtime_result_authority_promoted_subsequent', False, SKILL, runtime,
        runtime + '\n\nThis reconciliation result now grants native route authority.\n')
    item_one = ('1. Safety read: `AGENTS.md`, README/CONTRIBUTING/docs/workflows, existing audit\n'
                '   docs, generator/source ownership, and authorization chain.')
    for label, expected, prefix in (
        ('runtime-inert-quoted-item-one', True, '> ' + item_one.replace('\n', '\n> ') + '\n\n'),
        ('runtime-inert-fenced-item-one', True, '~~~text\n' + item_one + '\n~~~\n\n'),
        ('runtime-inert-comment-item-one', True, '<!--\n' + item_one + '\n-->\n\n'),
        ('runtime-inert-indented-item-one', True, '    ' + item_one.replace('\n', '\n    ') + '\n\n'),
        ('runtime-quoted-note-before-genuine-item-one', True, '> Retained historical note.\n'),
        ('runtime-quote-comment-before-genuine-item-one', True, '> Retained historical note.\n<!--\n1. Historical marker only.\n-->\n'),
        ('runtime-heading-after-quote-before-item-one', False, '> Retained historical note.\n#### Active rule\n' + neutral + '\n\n'),
        ('runtime-fake-item-one-before-genuine', False, item_one + '\n\n' + neutral + '\n\n'),
        ('runtime-foreign-numbered-item-before-one', False, '7. ' + neutral + '\n\n'),
        ('runtime-comment-active-suffix-before-one', False, '<!-- retained note --> ' + neutral + '\n\n'),
    ):
        add(label, expected, SKILL, item_one, '\n' + prefix + item_one)
    zero = control_target(runtime, '0. Continuity boundary:', flexible=True)
    add('runtime-wrong-item-zero-marker', False, SKILL, zero[:1], '9')
    add('runtime-wrong-item-one-marker', False, SKILL, item_one, item_one.replace('1. Safety read:', '2. Safety read:', 1))
    add('runtime-wrong-item-one-owner-clause', False, SKILL, item_one, '1. A different local instruction.')
    add('runtime-wrong-heading-ancestry', False, SKILL, '## Runtime Loop\n', '## Another owner\n### Runtime Loop\n')

    ordinary = owner(child, '### Ordinary child dispatch\n', '### Non-governed skill use\n')
    skills = owner(child, '### Non-governed skill use\n', '### Governed child lifecycle\n')
    before = owner(child, '#### Before actual load\n', '#### Only after actual load\n')
    after = owner(child, '#### Only after actual load\n', '### Returns and continuity\n')
    returns = owner(child, '### Returns and continuity\n', '## Governor-routed internal cognition\n')
    def lead(text):
        spans = []
        units = procedural_prose_units(text, source_spans=spans)
        first = next(index for index, (kind, value) in enumerate(units) if kind == 'paragraph')
        start, end = spans[first]
        return ControlSpan(text, start, end).strip()

    ordinary_lead = lead(ordinary)
    skill_lead = lead(skills)
    add('H09-ordinary-prospective-rule-only-historical', False, CHILD, ordinary_lead,
        '<!-- Historical timing requirement:\n' + ordinary_lead + '\n-->\n\nEmit the following event only after the host dispatch has returned; do not announce this dispatch prospectively.')
    add('H10-skill-prospective-rule-only-historical', False, CHILD, skill_lead,
        '<!-- Historical timing requirement:\n' + skill_lead + '\n-->\n\nLoad and apply the selected skill first, then emit the following event as its retrospective summary.')
    add('H12-open-instruction-after-full-load', False, CHILD,
        'After the applicable route prerequisites and before actual load, visibly emit:',
        'Complete the actual full child load first; only then visibly emit this opening event:')
    add('H15-use-ack-any-worker-substitution', False, CHILD,
        'existing qualified same-worker transport contract', 'transport contract of any available worker, including a replacement')
    handoff = ('After compaction, handoff or successor change, reacquire these operational\n'
               'obligations and exact parent/task/host bindings before the next dispatch or skill\n'
               'use. Keep the continuity STOP and applicable currentness/recovery prerequisites;\n'
               'an announcement cannot authorize hot reads or ordinary re-entry.')
    add('H29-handoff-reacquisition-only-comment', False, CHILD, handoff,
        '<!-- ' + handoff + ' -->\nAfter a handoff, use the predecessor parent/task/host bindings directly for the next dispatch without reacquisition.')
    selection_end = control_target(skills, ROLE_METHOD_PARAGRAPHS[0], flexible=True).start - skills.start
    selection = skills[:selection_end]
    for label, span in (('ordinary', ordinary), ('skill', selection), ('open', before), ('verified', after), ('handoff', returns)):
        for form, expected, extra in (
            ('active-addition', False, neutral),
            ('comment-history', True, '<!-- ' + neutral + ' -->'),
            ('quoted-history', True, '> ' + neutral),
            ('indented-history', True, '    ' + neutral),
        ):
            add('native-complete-owner-' + label + '-' + form, expected, CHILD, span,
                control_append(span, extra + '\n\n', block=True))
    governor = owner(skill, '## Visible pre-use announcements\n', '## Governor-routed internal cognition\n')
    add('native-governor-active-addition', False, SKILL, governor, governor + neutral + '\n\n')
    return cases


def source_convergence_controls(documents: dict[str, str]) -> int:
    mismatches = []
    cases = source_convergence_cases(documents)
    for label, expected, changed in cases:
        try:
            check(changed)
            accepted, reason = True, ''
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f'MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}')
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f'source convergence controls: {mismatches}'
    return sum(not expected for _, expected, _ in cases)


def boundary_correction_cases(documents: dict[str, str]) -> list[tuple[str, bool, dict[str, str]]]:
    # The independent literal booleans express active/inert policy, not parser
    # output. Raw document text locates changes; it never supplies expectations.
    documents = control_documents(documents)
    cases = []
    child = documents[CHILD]
    waiver = 'This active local instruction waives the required next gate.'

    def add(label, expected, key, old, new, *, block=False):
        assert old != new, label
        changed = dict(documents)
        changed[key] = control_replace(changed[key], old, new, block=block)
        cases.append((label, expected, changed))

    forms = (
        ('heading', '> ### Historical note\n', False),
        ('empty', '>\n', False),
        ('quoted-blank', '> Historical note.\n>\n', False),
        ('comment', '> <!-- Historical note. -->\n', False),
        ('multiline-comment', '> <!--\n> Historical note.\n> -->\n', False),
        ('fence', '> ```text\n> Historical note.\n> ```\n', False),
        ('tilde-fence', '> ~~~text\n> Historical note.\n> ~~~\n', False),
        ('indent', '>     Historical note.\n', False),
        ('lazy-paragraph', '> Historical note.\n', True),
    )
    for owner, key, endpoint in (
        ('route', CHILD, '## Non-authority rule\n'),
        ('native', CHILD, '### Non-governed skill use\n'),
        ('runtime', SKILL, '1. Safety read:'),
    ):
        endpoint_span = control_target(documents[key], endpoint, flexible=True)
        for form, prefix, expected in forms:
            add('boundary-' + owner + '-' + form, expected, key, documents[key],
                control_before(documents[key], endpoint_span, prefix + waiver + '\n\n', block=True))
        for form, prefix, _expected in forms:
            if form in ('multiline-comment', 'tilde-fence', 'lazy-paragraph'):
                continue
            add('boundary-' + owner + '-' + form + '-explicitly-quoted', True, key, documents[key],
                control_before(documents[key], endpoint_span, prefix + '> ' + waiver + '\n\n', block=True))

    # Appending a quote without a blank line keeps the old raw chunk count;
    # active owner classification must still discriminate these two forms.
    route_owner = control_section(child, 'Mandatory compaction entry and result ceiling', 3)
    route_records, _ = control_source(route_owner)
    last = [row for row in route_records if row['kind'] == 'paragraph'][-1]
    head = ControlSpan(route_owner, last['body_start'], last['end']).rstrip('\n')
    for label, prefix, expected in (('empty', '>\n', False), ('lazy', '> Historical note.\n', True)):
        add('boundary-route-raw-shape-' + label, expected, CHILD, head,
            head + '\n' + prefix + waiver)

    active_spans = []
    active_units = procedural_prose_units(child, source_spans=active_spans)
    for label, heading in (
        ('ordinary', '### Ordinary child dispatch\n'),
        ('skill', '### Non-governed skill use\n'),
        ('opening', '#### Before actual load\n'),
        ('full-load', '#### Only after actual load\n'),
        ('return', '### Returns and continuity\n'),
    ):
        first = active_units.index(('heading', heading.strip())) + 1
        assert active_units[first][0] == 'paragraph', 'control: missing active owner lead'
        start, end = active_spans[first]
        paragraph = child[start:end].rstrip('\n')
        end = start + len(paragraph)
        for ticks in ('`', '``'):
            add('boundary-whole-code-' + label + '-' + str(len(ticks)), False, CHILD, child,
                child[:start] + ticks + paragraph.replace('`', '') + ticks + child[end:])

    # The same quote grammar owns actual ini recognition and the immediately
    # accompanying sentence, not only the complete-owner comparison.
    ordinary_event = control_event(control_section(child, 'Ordinary child dispatch', 3))['block']
    for form, prefix, _expected in forms:
        if form in ('quoted-blank', 'lazy-paragraph'):
            continue
        add('boundary-event-after-quoted-' + form, True, CHILD, ordinary_event, prefix + ordinary_event, block=True)
        add('boundary-extra-event-after-quoted-' + form, False, CHILD, ordinary_event,
            ordinary_event + '\n\n' + prefix + '```ini\nSTATUS=OPEN\n```')
    sentence = 'Say: "I\'m using the `<CHILD_TASK>` holon to <PURPOSE>."'
    target = control_target(child, sentence, flexible=True)
    add('boundary-named-statement-whole-code', False, CHILD, child,
        control_replace(child, target, '`' + sentence.replace('`', '') + '`'))
    start, end = active_prose_match(child, r'exact\s+stable\s+`?CHILD_TASK`?\s+and\s+bounded\s+`?PURPOSE`?')
    identity_binding = child[start:end]
    replacement = ('exact stable CHILD_TASK and bounded PURPOSE' if '`' in identity_binding
                   else 'exact stable `CHILD_TASK` and bounded `PURPOSE`')
    add('boundary-identifier-markup', True, CHILD, child, child[:start] + replacement + child[end:])
    return cases


def boundary_correction_controls(documents: dict[str, str]) -> int:
    cases = boundary_correction_cases(route_control_fixture(documents))
    mismatches = []
    for label, expected, changed in cases:
        try:
            check(changed)
            accepted, reason = True, ''
        except AssertionError as exc:
            accepted, reason = False, str(exc)
        if accepted != expected:
            mismatches.append(label)
            print(f'MISMATCH {label}: expected_accept={expected}; accepted={accepted}; {reason}')
        else:
            print(f"{'PASS' if accepted else 'REJECTED'} {label}")
    assert not mismatches, f'boundary correction controls: {mismatches}'
    return sum(not expected for _, expected, _ in cases)


def native_identity_history_cases(documents):
    ordinary_fixture = '\nBefore every material ordinary holarchic child dispatch (producer, review,\npreparation, recovery and parallel siblings), including reuse/follow-up dispatch,\nemit this visible governor PRE-ACTION block before the host call:\n\n```ini\nPARENT_HOLON=<parent>\nCHILD_TASK=<stable logical name>\nCHILD_TASK_KIND=ORDINARY_HOLARCHIC_CHILD_TASK\nSTATUS=OPEN\nPURPOSE=<bounded purpose>\n```\n\nSay: "I\'m using the `<CHILD_TASK>` holon to <PURPOSE>."\nSubstitute the exact stable CHILD_TASK and bounded PURPOSE from that block.\nAnnounce the stable logical name before host spawn; bind/report the returned\nconcrete host identity afterward. Missing host-generated ID never excuses silence.\nA host-generated identity is unavailable before creation; the stable logical\nname supplies the pre-action identity and remains linked to the returned host\nidentity. A follow-up uses that binding and announces its new bounded purpose\nbefore dispatch. Announcing does not waive fresh-context or independence gates.\n\n'
    identity = 'Substitute the exact stable CHILD_TASK and bounded PURPOSE from that block.'
    formatted = 'Substitute the exact stable `CHILD_TASK` and bounded `PURPOSE` from that block.'
    loss = 'Use any convenient child name and purpose.'
    history_paragraph = ordinary_fixture.split('Say:', 1)[1].strip()
    specifications = (
        ('identity-history-HB20', '<!-- Archived sentence: ' + identity + ' -->', True),
        ('identity-history-HB21', '<!-- Archived note: identities were previously reviewed. -->', True),
        ('identity-history-same-plain', '<!-- ' + identity + ' -->', False),
        ('identity-history-same-formatted', '<!-- ' + formatted + ' -->', True),
        ('identity-history-reversed-format', '<!-- ' + formatted + ' -->', False),
        ('identity-history-two-copies', '<!-- ' + identity + ' -->\n<!-- ' + formatted + ' -->', True),
        ('identity-history-quoted', '> ' + identity, True),
        ('identity-history-indented', '    ' + identity, True),
        ('identity-history-full-paragraph', '<!-- Say:' + history_paragraph + ' -->', True),
        ('identity-history-exact-named-paragraph', '<!-- Say: ' + history_paragraph + ' -->', True),
    )
    # Locate the supplied actual owner; use a fixed reviewed fixture for the
    # mutations. Neither the expected clause nor expected loss comes from check.
    original = documents[CHILD].replace('\r\n', '\n')
    owner = control_section(original, 'Ordinary child dispatch', 3)
    cases = []
    for name, history, use_format in specifications:
        active = ordinary_fixture.replace(identity, formatted) if use_format else ordinary_fixture
        active_identity = formatted if use_format else identity
        assert active.count(active_identity) == 1
        negative = active.replace(active_identity, loss, 1)
        valid_docs, negative_docs = dict(documents), dict(documents)
        valid_docs[CHILD] = control_replace(original, owner, '\n' + history + '\n' + active)
        negative_docs[CHILD] = control_replace(original, owner, '\n' + history + '\n' + negative)
        cases.append((name, valid_docs, negative_docs))
    return cases


def native_identity_history_controls(documents: dict[str, str]) -> int:
    cases = native_identity_history_cases(documents)
    for label, valid, expected_negative in cases:
        check(valid)
        generated = next(changed for name, expected, changed in native_statement_cases(valid)
                         if name == 'native-ordinary-identity-purpose-binding-lost')
        assert generated == expected_negative, label + ': mutation changed history or missed the active clause'
        try:
            check(generated)
        except AssertionError:
            pass
        else:
            raise AssertionError(label + ': active identity loss was accepted')
        print('PASS ' + label)
        print('REJECTED ' + label + '-active-loss')
    return len(cases)


def source_convergence_history_controls(documents):
    child = documents[CHILD].replace('\r\n', '\n')
    spans = []
    units = procedural_prose_units(child, source_spans=spans)
    copies = []
    for heading in ('### Ordinary child dispatch', '### Non-governed skill use',
                    '#### Before actual load', '#### Only after actual load', '### Returns and continuity'):
        index = units.index(('heading', heading))
        assert units[index + 1][0] == 'paragraph'
        start, end = spans[index + 1]
        copies.extend((heading, child[start:end].strip()))
    copies.extend(('existing qualified same-worker transport contract',
                   'After compaction, handoff or successor change, reacquire these operational\n'
                   'obligations and exact parent/task/host bindings before the next dispatch or skill\n'
                   'use. Keep the continuity STOP and applicable currentness/recovery prerequisites;\n'
                   'an announcement cannot authorize hot reads or ordinary re-entry.'))
    history = '<!-- Archived owner and clause targets:\n' + '\n\n'.join(copies) + '\n-->'
    valid = dict(documents)
    ordinary = control_target(child, '### Ordinary child dispatch\n')
    valid[CHILD] = control_before(child, ordinary, history + '\n\n')
    check(valid)
    print('PASS source-convergence-history-valid')
    expected = {name: False for name in (
        'H09-ordinary-prospective-rule-only-historical',
        'H10-skill-prospective-rule-only-historical',
        'H12-open-instruction-after-full-load',
        'H15-use-ack-any-worker-substitution',
        'H29-handoff-reacquisition-only-comment')}
    for owner in ('ordinary', 'skill', 'open', 'verified', 'handoff'):
        for form, accepted in (('active-addition', False), ('comment-history', True),
                               ('quoted-history', True), ('indented-history', True)):
            expected['native-complete-owner-' + owner + '-' + form] = accepted
    generated = {name: (accepted, changed) for name, accepted, changed in source_convergence_cases(valid)}
    for name, accepted in expected.items():
        declared, changed = generated[name]
        assert declared is accepted, name + ': literal test disposition changed'
        assert changed[CHILD].count(history) == 1, name + ': historical targets changed'
        try:
            check(changed)
            observed = True
        except AssertionError:
            observed = False
        assert observed is accepted, name + ': wrong active owner mutation'
        print(('PASS ' if accepted else 'REJECTED ') + 'source-convergence-history-' + name)
    return sum(not accepted for accepted in expected.values())


def shared_range_regression_controls(documents):
    documents = control_documents(documents)
    item_one = ('1. Safety read: `AGENTS.md`, README/CONTRIBUTING/docs/workflows, existing audit\n'
                '   docs, generator/source ownership, and authorization chain.')
    negative = 0
    for name, target, history, wrong in (
        ('zero-inline', '0. Continuity boundary:', '<!-- S05 retained item-zero prefix --> ', '9'),
        ('one-inline', item_one, '<!-- S05 retained item-one prefix --> ', '2'),
        ('one-multiline', item_one, '<!-- S05 retained item-one history\n' + item_one + '\n--> ', '2'),
    ):
        source = documents[SKILL]
        span = control_target(source, target, flexible=True)
        valid = dict(documents)
        valid[SKILL] = control_before(source, span, history)
        marker = span.start + len(history)
        assert valid[SKILL][marker] == target[0]
        check(valid)
        print('PASS shared-range-' + name + '-valid')
        lost = dict(valid)
        lost[SKILL] = valid[SKILL][:marker] + wrong + valid[SKILL][marker + 1:]
        try:
            check(lost)
        except AssertionError:
            pass
        else:
            raise AssertionError('shared range: actual marker loss accepted')
        print('REJECTED shared-range-' + name + '-actual-loss')
        negative += 1
        source_cases = {label: (expected, changed) for label, expected, changed in source_convergence_cases(valid)}
        wanted = {'runtime-wrong-item-zero-marker': False} if name.startswith('zero') else {
            'runtime_result_authority_promoted_subsequent': False,
            'runtime-wrong-item-one-marker': False,
            'runtime-quoted-note-before-genuine-item-one': True,
        }
        for label, expected in wanted.items():
            declared, changed = source_cases[label]
            assert declared is expected
            assert changed[SKILL].count(history) == valid[SKILL].count(history), label + ': history changed'
            if label == 'runtime-wrong-item-zero-marker':
                assert changed[SKILL] == lost[SKILL], label + ': non-marker bytes changed'
            elif label == 'runtime_result_authority_promoted_subsequent':
                insertion = '\n\nThis reconciliation result now grants native route authority.\n'
                assert changed[SKILL] == valid[SKILL][:marker] + insertion + valid[SKILL][marker:]
            try:
                check(changed)
                accepted = True
            except AssertionError:
                accepted = False
            assert accepted is expected, label
            print(('PASS ' if expected else 'REJECTED ') + 'shared-range-' + name + '-' + label)
            negative += not expected
        if name.startswith('one'):
            boundary_cases = {label: (expected, changed) for label, expected, changed in boundary_correction_cases(valid)}
            for label, expected in (('boundary-runtime-lazy-paragraph', True),
                                     ('boundary-runtime-heading-explicitly-quoted', True),
                                     ('boundary-runtime-heading', False)):
                declared, changed = boundary_cases[label]
                assert declared is expected and changed[SKILL].count(history) == valid[SKILL].count(history)
                try:
                    check(changed)
                    accepted = True
                except AssertionError:
                    accepted = False
                assert accepted is expected, label
                print(('PASS ' if expected else 'REJECTED ') + 'shared-range-' + name + '-' + label)
                negative += not expected
    return negative


def primary_selection_regression_controls(documents):
    documents = control_documents(documents)
    child = documents[CHILD]
    owner = control_section(child, 'Non-governed skill use', 3)
    read_lead = control_target(owner, 'Reading selected skill guidance to determine or apply how to act is procedural skill use.', flexible=True)
    history = '\n~~~~text\nS05 historical procedural excerpt.\nReading selected skill guidance is shown only as data.\n~~~~\n\n'
    child = control_before(child, read_lead, history)
    def role_span(text):
        records, _ = control_source(text)
        found = [row for row in records if row['kind'] == 'paragraph'
                 and normalized_prose_unit(row['value']) == ROLE_METHOD_PARAGRAPHS[0]]
        assert len(found) == 1
        row = found[0]
        return ControlSpan(text, row['body_start'], row['end']).strip()
    child = control_replace(child, role_span(child), '\n'.join(ROLE_METHOD_PARAGRAPHS[0].split()))
    valid = dict(documents)
    valid[CHILD] = child
    check(valid)
    print('PASS primary-selection-wrapped-owner-with-inert-fence')
    changes = [
        ('skill-timing-loss', replace_phrase(child,
            'Before every substantive non-governed skill use, emit this visible block before loading or applying the skill:',
            'Load the selected skill before announcing its use.')),
        ('role-admission-waiver', replace_phrase(child, ROLE_METHOD_PARAGRAPHS[2],
            'An ordinary procedural method substitutes for governed admission.')),
        ('extra-selection-event-block', control_before(child, role_span(child),
            '\n~~~~text\nAn extra block in the native selection event owner.\n~~~~\n\n')),
        ('role-boundary-only-in-history', control_replace(child, role_span(child),
            '<!-- ' + ROLE_METHOD_PARAGRAPHS[0] + ' -->\nThe operative role boundary is absent.')),
    ]
    for label, changed_child in changes:
        changed = dict(valid)
        changed[CHILD] = changed_child
        assert history in changed_child
        try:
            check(changed)
        except AssertionError:
            pass
        else:
            raise AssertionError('primary selection: accepted ' + label)
        print('REJECTED primary-selection-' + label)
    return len(changes)


def template_target_regression_controls(documents):
    documents = control_documents(documents)
    child = documents[CHILD]
    historical_event = control_event(control_section(child, 'Before actual load', 4))['block']
    returned = control_event(control_section(child, 'Ordinary child-task placement and custody'))
    history = '<!-- S05 historical governed event, not this return:\n' + historical_event + '\n-->\n'
    valid = dict(documents)
    valid[CHILD] = control_before(child, returned['block'], history)
    check(valid)
    generated = dict((name, changed) for name, expected, changed in native_statement_cases(valid))
    changed = generated['native-return-child-identity-omitted']
    assert changed[CHILD].count(history) == valid[CHILD].count(history)
    try:
        check(changed)
    except AssertionError:
        pass
    else:
        raise AssertionError('return target selected historical child type')
    print('PASS template-target-cross-role-return-history')
    print('REJECTED template-target-actual-return-child-loss')
    history = '~~~~text\nS05 historical projection fragments: / ACCEPTED / JOINED / CONSUMING_PARENT / CONSUMING_FRONTIER / RESULT / PARENT_COMPLETE\n~~~~\n'
    valid = dict(documents)
    valid[REPORT] = history + documents[REPORT]
    check(valid)
    generated = dict((name, changed) for name, expected, changed in native_statement_cases(valid))
    changed = generated['native-report-projection-missing-PARENT_COMPLETE']
    assert changed[REPORT].startswith(history)
    try:
        check(changed)
    except AssertionError:
        pass
    else:
        raise AssertionError('projection target selected unrelated fenced history')
    print('PASS template-target-owned-report-projection')
    print('REJECTED template-target-actual-projection-field-loss')
    return 2


def reflow_target_controls(documents):
    documents = control_documents(documents)
    child = documents[CHILD]
    role_owner = control_between(control_section(child, 'Non-governed skill use', 3),
        ROLE_METHOD_PARAGRAPHS[0],
        'Reading selected skill guidance to determine or apply how to act is procedural skill use.')
    full_role = '\n\n'.join('\n'.join(paragraph.split()) for paragraph in ROLE_METHOD_PARAGRAPHS)
    full = control_active_owner_replace(child, role_owner, full_role)
    specifications = [
        ('full-role', full, role_method_composition_cases, 'missing-invariant-GOVERNED_CHILD_ROLE_SELECTION !'),
    ]
    for name, phrase, replacement, builder, negative_label in (
        ('role-first', ROLE_METHOD_PARAGRAPHS[0], '\n'.join(ROLE_METHOD_PARAGRAPHS[0].split()),
         source_convergence_cases, 'native-complete-owner-skill-active-addition'),
        ('ordinary-named', 'Say: "I\'m using the \x60<CHILD_TASK>\x60 holon to <PURPOSE>."',
         '\n'.join('Say: "I\'m using the \x60<CHILD_TASK>\x60 holon to <PURPOSE>."'.split()),
         native_statement_cases, 'native-ordinary-generic-child'),
        ('identity-clause', 'Substitute the exact stable CHILD_TASK and bounded PURPOSE from that block.',
         '\n'.join('Substitute the exact stable CHILD_TASK and bounded PURPOSE from that block.'.split()),
         boundary_correction_cases, 'boundary-whole-code-ordinary-1'),
        ('skill-named', "I'm using the \x60<skill>\x60 skill to <purpose>.",
         '\n'.join("I'm using the \x60<skill>\x60 skill to <purpose>.".split()),
         native_statement_cases, 'native-skill-generic-name'),
        ('return-frontier', ' parent at \x60<CONSUMING_FRONTIER>\x60 with ',
         ' parent\nat\n\x60<CONSUMING_FRONTIER>\x60\nwith ',
         native_statement_cases, 'native-return-sentence-omits-consuming-frontier'),
    ):
        if name == 'identity-clause':
            # The fixed same-policy clause permits these two identifier forms.
            start, end = active_prose_match(child,
                r'Substitute\s+the\s+exact\s+stable\s+\x60?CHILD_TASK\x60?\s+and\s+bounded\s+\x60?PURPOSE\x60?\s+from\s+that\s+block\.')
            target = ControlSpan(child, start, end)
        else:
            target = control_target(child, phrase, flexible=True)
        specifications.append((name, control_replace(child, target, replacement), builder, negative_label))
    for name, changed_child, builder, negative_label in specifications:
        valid = dict(documents)
        valid[CHILD] = changed_child
        check(valid)
        generated = {label: (expected, changed) for label, expected, changed in builder(valid)}
        expected, negative = generated[negative_label]
        assert expected is False
        try:
            check(negative)
        except AssertionError:
            pass
        else:
            raise AssertionError('reflow target lost operative mutation: ' + negative_label)
        print('PASS reflow-target-' + name + '-valid')
        print('REJECTED reflow-target-' + name + '-active-loss')
    return len(specifications)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--native-statement-controls-only", action="store_true",
                        help="run grouped ini identity/timing/return/continuity source controls")
    parser.add_argument("--role-method-composition-controls-only", action="store_true",
                        help="run only the new governed-role/procedural-method source controls")
    parser.add_argument("--compaction-route-controls-only", action="store_true",
                        help="run only the scoped native/compaction admission controls")
    parser.add_argument("--ordinary-projection-controls-only", action="store_true",
                        help="run changed-context return-template controls without replaying prior controls")
    parser.add_argument("--quoted-history-controls-only", action="store_true",
                        help="run quote-boundary controls without replaying prior control suites")
    parser.add_argument("--procedural-skill-read-controls-only", action="store_true",
                        help="run procedural-read discriminator controls without replaying prior suites")
    parser.add_argument("--procedural-clause-controls-only", action="store_true",
                        help="run active procedural-clause regressions without replaying prior control suites")
    args = parser.parse_args()
    try:
        documents = {path: (args.repo_root / path).read_text(encoding="utf-8")
                     for path in (SKILL, CHILD, TRANSCRIPT, REPORT)}
        check(documents)
        count = native_statement_controls(documents)
        count += native_identity_history_controls(documents)
        if args.native_statement_controls_only:
            print(f"pre-use-announcement-contract: PASS native statement source contract; {count} negative controls")
            return 0
        count += role_method_composition_controls(documents)
        if args.role_method_composition_controls_only:
            print(f"pre-use-announcement-contract: PASS role/method source contract; {count} negative controls")
            return 0
        count += compaction_route_controls(documents)
        if not args.compaction_route_controls_only:
            count += procedural_clause_controls(documents)
            if not args.procedural_clause_controls_only:
                count += procedural_skill_read_controls(documents)
                if not args.procedural_skill_read_controls_only:
                    count += quoted_history_controls(documents)
                    if not args.quoted_history_controls_only:
                        count += ordinary_projection_controls(documents)
                        if not args.ordinary_projection_controls_only:
                            count += controls(documents)
        count += source_convergence_controls(documents)
        count += source_convergence_history_controls(documents)
        count += boundary_correction_controls(documents)
        count += shared_range_regression_controls(documents)
        count += primary_selection_regression_controls(documents)
        count += template_target_regression_controls(documents)
        count += reflow_target_controls(documents)
    except (AssertionError, OSError) as exc:
        print(f"pre-use-announcement-contract: FAIL: {exc}")
        return 1
    print(f"pre-use-announcement-contract: PASS source contract; {count} negative controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
