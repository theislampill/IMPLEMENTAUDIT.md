#!/usr/bin/env python3
"""Pure source transforms for a prospective A12 campaign; no product imports."""
from __future__ import annotations

import ast
import difflib
import hashlib

OWNER_SHA256 = '9eebc5d5e57b47b0e4b4a2a846de1c0b55407713e14008a6de4d01e7a8c5e19e'

MUTANTS = (
    ('I-OMIT', 'invalidation', 'omission', 'rotation'),
    ('I-LATE', 'invalidation', 'reordering', 'rotation'),
    ('E-REUSE', 'fresh_epoch', 'omission', 'rotation'),
    ('E-LATE', 'fresh_epoch', 'reordering', 'rotation'),
    ('C-BLIND', 'cas', 'omission', 'pointer_conflict'),
    ('C-LATE', 'cas', 'reordering', 'pointer_conflict'),
    ('R-OMIT', 'ref_readback', 'omission', 'ref_conflict'),
    ('R-EARLY', 'ref_readback', 'reordering', 'rotation'),
    ('B-OMIT', 'blob_readback', 'omission', 'blob_corrupt'),
    ('B-EARLY', 'blob_readback', 'reordering', 'blob_clean'),
    ('J-OMIT', 'receipt_binding', 'omission', 'rotation'),
    ('J-EARLY', 'receipt_binding', 'reordering', 'rotation'),
    ('K-BLIND', 'compensating_cas', 'omission', 'compensating_conflict'),
    ('K-LATE', 'compensating_cas', 'reordering', 'compensating_conflict'),
)

BASELINES = (
    ('BASE-ROTATION', 'rotation'), ('BASE-RECOVERY', 'recovery'),
    ('BASE-OCCUPIED', 'occupied_epoch'), ('BASE-CAS', 'pointer_conflict'),
    ('BASE-REF-READBACK', 'ref_conflict'), ('BASE-BLOB', 'blob_clean'),
    ('BASE-BLOB-CORRUPTION', 'blob_corrupt'),
    ('BASE-COMPENSATION-CAS', 'compensating_conflict'),
)

LEGACY_METHODS = (
    'test_legacy_v2_currentness_is_preserved',
    'test_a_marker_without_pointer_cannot_fall_back_to_root_v2',
    'test_verify_cannot_accept_old_v2_after_a_marker_appears',
    'test_resume_cannot_mint_v2_around_a_broken_migrated_route',
    'test_second_genuine_boundary_is_admitted_while_receipt_is_stale',
    'test_separate_legacy_state_read_returns_exact_bytes',
)

CASES = tuple(
    [{'id': name, 'scenario': scenario, 'mutant': None} for name, scenario in BASELINES]
    + [{'id': name, 'scenario': scenario, 'mutant': name, 'gate': gate, 'operator': operator}
       for name, gate, operator, scenario in MUTANTS]
    + [{'id': 'LEGACY-' + str(i + 1), 'scenario': 'legacy', 'mutant': None,
        'method': method} for i, method in enumerate(LEGACY_METHODS)]
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def function_text(source, name):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(nodes) != 1 or nodes[0].decorator_list:
        raise ValueError('one undecorated original function required: ' + name)
    node = nodes[0]
    return ''.join(source.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('source patch cardinality differs: ' + repr(old[:100]))
    return text.replace(old, new, 1)


def indent(text, spaces):
    return ''.join((' ' * spaces + line if line.strip() else line) for line in text.splitlines(keepends=True))


def build_variant(owner_raw, mutant):
    """Return complete before/after bodies and diff without evaluating product code."""
    if sha(owner_raw) != OWNER_SHA256:
        raise ValueError('immutable original owner source differs')
    source = owner_raw.decode('utf-8')
    if mutant not in {row[0] for row in MUTANTS}:
        raise ValueError('undeclared mutation')
    changes = {}

    def get(name):
        if name not in changes:
            original = function_text(source, name)
            changes[name] = {'before': original, 'after': original, 'activation': None}
        return changes[name]['after']

    def put(name, text, activation):
        changes[name]['after'] = text
        changes[name]['activation'] = activation

    if mutant in {'I-OMIT', 'I-LATE'}:
        name = 'allocate_epoch'; text = get(name)
        text = replace_once(text, '    updates[context["invalidation_ref"]] = (invalidation_oid, observed["invalidation"])\n', '')
        put(name, text, '    updates[epoch_ref(context, epoch)] = (epoch_oid, None)')
        if mutant == 'I-LATE':
            name = 'complete_epoch'; text = get(name)
            early = '    stage_observation(context, record, record["expected_pointer_oid"])\n'
            late = '''    # DECLARED MUTANT: publish invalidation only after the first finalize-stage admission.
    late_old = prepared["predecessor"]["invalidation_oid"]
    late_old = None if late_old == "none" else late_old
    late_observed = authorities(context)
    update_refs(context, {context["invalidation_ref"]: (transition["invalidation_oid"], late_old)},
                transition_guards(context, late_observed, record, epoch_oid, exclude=("invalidation",)),
                observation=observation)
'''
            text = replace_once(text, early, early + late)
            put(name, text, early.strip())
    elif mutant == 'E-REUSE':
        name = 'allocate_epoch'; text = get(name)
        text = replace_once(text, '    epoch = next_epoch(predecessor["continuity_epoch"])\n',
                            '    epoch = predecessor["continuity_epoch"]\n')
        put(name, text, '    epoch = predecessor["continuity_epoch"]')
    elif mutant == 'E-LATE':
        name = 'allocate_epoch'; text = get(name)
        selection = '    epoch = next_epoch(predecessor["continuity_epoch"])\n'
        text = replace_once(text, selection, '    epoch = predecessor["continuity_epoch"]\n')
        identity = '    ref = receipt_ref(context, epoch)\n'
        # The actual fresh selection now occurs after a dependent receipt-ref identity.
        # The original freshness and transition-algebra oracles are not changed.
        text = replace_once(text, identity, identity + selection)
        put(name, text, '    epoch = next_epoch(predecessor["continuity_epoch"])')
    elif mutant in {'C-BLIND', 'C-LATE', 'K-BLIND', 'K-LATE'}:
        name = 'update_refs'; text = get(name)
        selected_kind = 'recovery' if mutant.startswith('K-') else 'rotation'
        text = replace_once(text, '    repo = context["repo"]\n',
            '    repo = context["repo"]\n'
            + '    mutated_pointer = context["pointer_ref"] in updates and _a12_active_transition_kind == '
            + repr(selected_kind) + '\n')
        check = '''        if read_refs(repo, expected) != expected:
            raise CASFailure("expected-old authority or namespace guard changed")
'''
        text = replace_once(text, check,
            '        if not mutated_pointer:\n' + indent(check, 4))
        old = '            chunks.append(b"update " + ref.encode() + b"\\0" + new.encode() + b"\\0" + (old or ZERO).encode() + b"\\0")\n'
        new = '''            # DECLARED MUTANT: an empty old-value field removes Git's pointer comparison.
            old_field = b"" if mutated_pointer and ref == context["pointer_ref"] else (old or ZERO).encode()
            chunks.append(b"update " + ref.encode() + b"\\0" + new.encode() + b"\\0" + old_field + b"\\0")
'''
        text = replace_once(text, old, new)
        if mutant.endswith('LATE'):
            anchor = '        # A process exit code alone never establishes whether publication landed.\n'
            text = replace_once(text, anchor,
                '        if mutated_pointer:\n' + indent(check, 4) + anchor)
        put(name, text, '            old_field = b"" if mutated_pointer and ref == context["pointer_ref"] else (old or ZERO).encode()')
    elif mutant in {'R-OMIT', 'R-EARLY'}:
        name = 'update_refs'; text = get(name)
        block = '''        after = read_refs(repo, expected)
        landed = all(after[ref] == new for ref, (new, _) in updates.items())
        intact = all(after[ref] == oid for ref, oid in guards.items())
        if not landed or not intact:
            raise CASFailure("publication did not have one exact verified effect") from failure
'''
        text = replace_once(text, block,
            '        if context["pointer_ref"] not in updates:\n' + indent(block, 4))
        if mutant == 'R-EARLY':
            early = block.replace(' from failure', '')
            text = replace_once(text, '        chunks = [b"start\\0"]\n',
                '        if context["pointer_ref"] in updates:\n' + indent(early, 4) + '        chunks = [b"start\\0"]\n')
            put(name, text, '            after = read_refs(repo, expected)')
        else:
            put(name, text, '        if context["pointer_ref"] not in updates:')
    elif mutant in {'B-OMIT', 'B-EARLY'}:
        name = 'write_blob'; text = get(name)
        check = '''    if read_blob(context["repo"], oid) != raw:
        raise RotationError("written authority blob failed exact readback")
'''
        text = replace_once(text, check, '')
        effect = '    oid = git(context["repo"], "hash-object", "-w", "--stdin", input_bytes=raw).decode().strip()\n'
        if mutant == 'B-EARLY':
            early = '    oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()\n' + check
            text = replace_once(text, effect, early + effect)
            put(name, text, '    if read_blob(context["repo"], oid) != raw:')
        else:
            put(name, text, '    return oid')
    elif mutant == 'J-OMIT':
        name = 'complete_epoch'; text = get(name)
        text = replace_once(text,
            '               pointer["continuity_epoch"], pointer["invalidation_oid"], context["pointer_ref"], pointer_oid,\n',
            '               pointer["continuity_epoch"], pointer["invalidation_oid"], context["pointer_ref"],\n')
        put(name, text, '    receipt_oid = write_blob(context, ("\\t".join(receipt) + "\\n").encode())')
    elif mutant == 'J-EARLY':
        name = 'complete_epoch'; text = get(name)
        begin = text.index('    receipt = [RECEIPT_SCHEMA,')
        end_marker = '    receipt_matches_pointer(context, read_receipt(context, token), pointer, pointer_oid)\n'
        end = text.index(end_marker, begin) + len(end_marker)
        receipt_block = text[begin:end]
        text = text[:begin] + text[end:]
        site = '    updates = {}\n    updates[context["pointer_ref"]] = (pointer_oid, record["expected_pointer_oid"])\n'
        text = replace_once(text, site, receipt_block + site)
        put(name, text, '    receipt_oid = write_blob(context, ("\\t".join(receipt) + "\\n").encode())')
    else:
        raise ValueError('mutation implementation absent')

    for name, row in changes.items():
        before, after = row['before'], row['after']
        if before == after:
            raise ValueError('identity mutation: ' + name)
        tree = ast.parse(after)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef) or tree.body[0].name != name:
            raise ValueError('mutation escaped its exact function')
        compile(after, '<declared-A12-' + mutant + '-' + name + '>', 'exec')
        row['before_sha256'] = sha(before.encode()); row['after_sha256'] = sha(after.encode())
        row['activation_lines'] = [i for i, line in enumerate(after.splitlines(), 1)
                                   if line.strip() == row['activation'].strip()]
        if not row['activation_lines']:
            raise ValueError('activation statement is absent: ' + name)
        row['patch'] = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                             fromfile='original/' + name + '.py', tofile=mutant + '/' + name + '.py'))
    return {'schema': 'dg18.a12.exact-source-mutation.v1', 'mutant': mutant,
            'original_owner_sha256': OWNER_SHA256, 'functions': changes,
            'original_product_changed': False, 'actual_execution': False}
