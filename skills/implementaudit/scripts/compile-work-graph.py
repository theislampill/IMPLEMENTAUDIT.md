#!/usr/bin/env python3
"""Compile a deterministic, read-only frontier projection from WORK_GRAPH.json."""
from __future__ import annotations
import hashlib
import hmac
import copy
import contextlib
import base64
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
from typing import TypeAlias
JSONValue: TypeAlias = None | bool | int | str | list['JSONValue'] | dict[str, 'JSONValue']
INT64_MIN = -2 ** 63
INT64_MAX = 2 ** 63 - 1
KNOWN_STATES = ('DONE', 'ACTIVE', 'READY', 'BLOCKED')
DIGEST_RE = re.compile('^[0-9a-f]{64}$')
COMMIT_RE = re.compile('^[0-9a-f]{40}$')
RECEIPT_RE = re.compile('^refs/implementaudit/continuity-receipts/[^/@]+/G[0-9A-F]{4}@[0-9a-f]{40}$')
PREPARATION_KINDS = {'BRIEF', 'RECONNAISSANCE', 'RED_DESIGN', 'FIXTURE_DESIGN', 'ACCEPTANCE_PLAN', 'REVIEW_PLAN', 'DISPOSABLE_PROTOTYPE'}
PREPARATION_FORBIDDEN = {'SOURCE_MUTATION', 'GRAPH_MUTATION', 'LIFECYCLE_CREDIT', 'REF_MUTATION', 'PACKAGE_INSTALL_PUBLICATION', 'EXTERNAL_EFFECT'}
PRODUCT_DISPOSITIONS = {'CONSUMED', 'COMPOSED', 'INTEGRATED', 'SUPERSEDED', 'REJECTED', 'EXPLICITLY_DEFERRED_TO_NAMED_JOIN'}
PROXIMAL_SERIALIZATION_REASONS = {'HARD_PREREQUISITE', 'SHARED_WRITER_OR_RESOURCE', 'CURRENTNESS_OR_IDENTITY', 'IRREVERSIBLE_EFFECT_PRECONDITION', 'CONSEQUENCE_CONTROL', 'HOST_CAPACITY_OR_EXCLUSION'}
PROXIMAL_LANE_STATUSES = {'PASS', 'FAIL', 'PENDING'}

class WorkGraphError(ValueError):
    """The supplied WORK_GRAPH bytes do not satisfy the v1 contract."""

def _reject_float(token: str) -> float:
    raise WorkGraphError(f'floats are forbidden: {token}')

def _reject_constant(token: str) -> None:
    raise WorkGraphError(f'non-finite numbers are forbidden: {token}')

def _decode_int(token: str) -> int:
    if token == '-0':
        raise WorkGraphError('negative zero is forbidden')
    value = int(token, 10)
    if not INT64_MIN <= value <= INT64_MAX:
        raise WorkGraphError('integer outside signed 64-bit range')
    return value

def _unique_object(pairs: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in pairs:
        if key in result:
            raise WorkGraphError(f'duplicate key: {key}')
        result[key] = value
    return result

def _validate_scalar_unicode(value: str, path: str) -> None:
    if any((55296 <= ord(char) <= 57343 for char in value)):
        raise WorkGraphError(f'{path}: string contains a non-scalar surrogate')

def validate_identity_json_v1(value: JSONValue, path: str='$') -> None:
    if value is None or type(value) is bool:
        return
    if type(value) is str:
        _validate_scalar_unicode(value, path)
        return
    if type(value) is int:
        if not INT64_MIN <= value <= INT64_MAX:
            raise WorkGraphError(f'{path}: integer outside signed 64-bit range')
        return
    if type(value) is list:
        for index, item in enumerate(value):
            validate_identity_json_v1(item, f'{path}[{index}]')
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise WorkGraphError(f'{path}: object key must be a string')
            _validate_scalar_unicode(key, f'{path}.<key>')
            validate_identity_json_v1(item, f'{path}.{key}')
        return
    raise WorkGraphError(f'{path}: floats and non-JSON values are forbidden')

def canonical_json_v1(value: JSONValue) -> bytes:
    validate_identity_json_v1(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def decode_strict_json_bytes(raw: bytes, source: str) -> JSONValue:
    if not isinstance(raw, bytes):
        raise WorkGraphError(f'{source}: input must be bytes')
    if raw.startswith(b'\xef\xbb\xbf'):
        raise WorkGraphError(f'{source}: UTF-8 BOM is forbidden')
    try:
        text = raw.decode('utf-8', 'strict')
    except UnicodeDecodeError as exc:
        raise WorkGraphError(f'{source}: invalid UTF-8') from exc
    try:
        value = json.loads(text, object_pairs_hook=_unique_object, parse_float=_reject_float, parse_int=_decode_int, parse_constant=_reject_constant)
        validate_identity_json_v1(value)
    except WorkGraphError:
        raise
    except json.JSONDecodeError as exc:
        raise WorkGraphError(f'{source}: invalid JSON: {exc.msg}') from exc
    except (ValueError, RecursionError) as exc:
        raise WorkGraphError(f'{source}: JSON parser or validation limit exceeded') from exc
    return value

def _require_object(value: JSONValue, path: str) -> dict[str, JSONValue]:
    if type(value) is not dict:
        raise WorkGraphError(f'{path}: object required')
    return value

def _require_string(value: JSONValue, path: str) -> str:
    if type(value) is not str or not value:
        raise WorkGraphError(f'{path}: non-empty string required')
    return value

def _require_string_list(value: JSONValue, path: str) -> list[str]:
    if type(value) is not list or not value:
        raise WorkGraphError(f'{path}: non-empty array required')
    result = [_require_string(item, path) for item in value]
    if len(result) != len(set(result)):
        raise WorkGraphError(f'{path}: duplicate value')
    return result

def _require_string_array(value: JSONValue, path: str) -> list[str]:
    if type(value) is not list:
        raise WorkGraphError(f'{path}: array required')
    result = [_require_string(item, path) for item in value]
    if len(result) != len(set(result)):
        raise WorkGraphError(f'{path}: duplicate value')
    return result

def _require_digest(value: JSONValue, path: str) -> str:
    result = _require_string(value, path)
    if not DIGEST_RE.fullmatch(result):
        raise WorkGraphError(f'{path}: 64-hex digest required')
    return result

def _require_commit(value: JSONValue, path: str) -> str:
    result = _require_string(value, path)
    if not COMMIT_RE.fullmatch(result):
        raise WorkGraphError(f'{path}: 40-hex identity required')
    return result

def _require_bool(value: JSONValue, path: str) -> bool:
    if type(value) is not bool:
        raise WorkGraphError(f'{path}: boolean required')
    return value

def _require_exact_members(value: dict[str, JSONValue], expected: set[str], path: str) -> None:
    if set(value) != expected:
        raise WorkGraphError(f'{path}: exact members required')

def _validate_product_result_v1(value: JSONValue, path: str, by_id: dict[str, dict[str, JSONValue]]) -> dict[str, JSONValue]:
    result = _require_object(value, path)
    if set(result) != {'product', 'disposition'}:
        raise WorkGraphError(f'{path}: product and one disposition required')
    product = _require_object(result['product'], f'{path}.product')
    if set(product) != {'commit', 'tree', 'review_sha256'}:
        raise WorkGraphError(f'{path}.product: exact identity members required')
    _require_commit(product['commit'], f'{path}.product.commit')
    _require_commit(product['tree'], f'{path}.product.tree')
    _require_digest(product['review_sha256'], f'{path}.product.review_sha256')
    disposition = _require_object(result['disposition'], f'{path}.disposition')
    if set(disposition) != {'kind', 'target'}:
        raise WorkGraphError(f'{path}.disposition: kind and target required')
    kind = _require_string(disposition['kind'], f'{path}.disposition.kind')
    target = _require_string(disposition['target'], f'{path}.disposition.target')
    if kind not in PRODUCT_DISPOSITIONS:
        raise WorkGraphError(f'{path}.disposition: unknown disposition {kind}')
    return result

def validate_product_authority_cli_path_v1(graph_bytes: bytes, graph_path: pathlib.Path, product_authority_path: pathlib.Path) -> None:
    """Bind the CLI's supplied authority file to the graph declaration."""
    decoded = decode_strict_json_bytes(graph_bytes, str(graph_path))
    graph = _require_object(decoded, str(graph_path))
    authority = graph.get('authority')
    if type(authority) is not dict:
        return
    source = authority.get('qualified_product_contract')
    if type(source) is not dict:
        return
    declared = source.get('path')
    if type(declared) is not str or not declared:
        return
    declared_path = pathlib.Path(declared)
    if not declared_path.is_absolute():
        declared_path = graph_path.resolve().parent / declared_path
    if declared_path.resolve() != product_authority_path.resolve():
        raise WorkGraphError('qualified product authority: declared source path mismatch')

def _validate_product_contract_v1(graph: dict[str, JSONValue], cells: list[dict[str, JSONValue]], by_id: dict[str, dict[str, JSONValue]], product_authority_bytes: bytes | None=None) -> dict[str, JSONValue] | None:
    topology_value = graph.get('integration_topology')
    topology = topology_value if type(topology_value) is dict else {}
    contract_value = topology.get('product_contract')
    authority_value = graph.get('authority')
    product_signal = any(('source_bearing' in cell for cell in cells)) or any((key in topology for key in ('qualified_products', 'composition_proposals'))) or product_authority_bytes is not None or (type(authority_value) is dict and 'qualified_product_contract' in authority_value)
    if contract_value is None:
        if product_signal:
            raise WorkGraphError('qualified product contract required for governed products')
        return None
    contract = _require_object(contract_value, '$.integration_topology.product_contract')
    expected_contract = {'authority_sha256', 'done_classification', 'non_cell_owners', 'join_owners', 'product_bindings', 'disposition_bindings', 'composition_authorizations', 'future_consumers'}
    if set(contract) != expected_contract:
        raise WorkGraphError('qualified product contract: exact members required')
    authority = _require_object(graph.get('authority'), '$.authority')
    source = _require_object(authority.get('qualified_product_contract'), '$.authority.qualified_product_contract')
    if set(source) != {'kind', 'path', 'bytes', 'sha256', 'receipt'}:
        raise WorkGraphError('qualified product authority: exact source identity required')
    if source['kind'] != 'GOVERNOR_VERIFIED_PRODUCT_BINDINGS':
        raise WorkGraphError('qualified product authority: governor-verified source required')
    _require_string(source['path'], 'qualified product authority path')
    if type(source['bytes']) is not int or source['bytes'] <= 0:
        raise WorkGraphError('qualified product authority: positive byte count required')
    _require_digest(source['sha256'], 'qualified product authority sha256')
    receipt = _require_string(source['receipt'], 'qualified product authority receipt')
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError('qualified product authority: current receipt required')
    authority_sha = _require_digest(contract['authority_sha256'], 'qualified product contract authority_sha256')
    expected_authority_sha = hashlib.sha256(canonical_json_v1(source)).hexdigest()
    if not hmac.compare_digest(authority_sha, expected_authority_sha):
        raise WorkGraphError('qualified product contract: authority source binding mismatch')
    if product_authority_bytes is None:
        raise WorkGraphError('qualified product contract: authoritative source bytes required')
    if len(product_authority_bytes) != source['bytes'] or not hmac.compare_digest(hashlib.sha256(product_authority_bytes).hexdigest(), str(source['sha256'])):
        raise WorkGraphError('qualified product contract: authoritative source identity mismatch')
    authority_document = _require_object(decode_strict_json_bytes(product_authority_bytes, str(source['path'])), 'qualified product authority document')
    expected_document = dict(contract)
    del expected_document['authority_sha256']
    if authority_document != expected_document:
        raise WorkGraphError('qualified product contract: authoritative source content mismatch')
    classification = _require_object(contract['done_classification'], 'qualified product done classification')
    done_ids = {str(cell['id']) for cell in cells if cell['state'] == 'DONE'}
    if set(classification) != done_ids:
        raise WorkGraphError('qualified product classification must cover every DONE cell')
    source_cells: set[str] = set()
    for cell_id in sorted(done_ids):
        category = classification[cell_id]
        if category not in {'SOURCE_PRODUCT', 'NON_SOURCE'}:
            raise WorkGraphError(f'cell {cell_id}: invalid qualified product classification')
        cell = by_id[cell_id]
        if type(cell.get('source_bearing')) is not bool:
            raise WorkGraphError(f'cell {cell_id}: explicit source_bearing classification required')
        expected_source = category == 'SOURCE_PRODUCT'
        if cell['source_bearing'] is not expected_source:
            raise WorkGraphError(f'cell {cell_id}: source_bearing classification mismatch')
        if expected_source:
            source_cells.add(cell_id)
    non_cell_owners = _require_string_array(contract['non_cell_owners'], 'qualified product non-cell owners')
    if non_cell_owners != sorted(non_cell_owners):
        raise WorkGraphError('qualified product non-cell owners must be sorted')
    join_owners = _require_string_array(contract['join_owners'], 'qualified product join owners')
    if join_owners != sorted(join_owners):
        raise WorkGraphError('qualified product join owners must be sorted')
    for owner in join_owners:
        if owner not in by_id or by_id[owner].get('class') != 'integration':
            raise WorkGraphError(f'qualified product contract: unresolved join owner {owner}')
    bindings_value = contract['product_bindings']
    if type(bindings_value) is not list or not bindings_value:
        raise WorkGraphError('qualified product bindings: non-empty array required')
    bindings: dict[tuple[str, str], dict[str, JSONValue]] = {}
    commits: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(bindings_value):
        binding = _require_object(value, f'qualified product binding {index}')
        if set(binding) != {'owner_kind', 'owner', 'commit', 'tree', 'review_sha256'}:
            raise WorkGraphError(f'qualified product binding {index}: exact members required')
        owner_kind = _require_string(binding['owner_kind'], 'product owner kind')
        owner = _require_string(binding['owner'], 'product owner')
        if owner_kind not in {'CELL', 'NON_CELL'}:
            raise WorkGraphError(f'qualified product binding {index}: unknown owner kind')
        if owner_kind == 'CELL' and owner not in source_cells:
            raise WorkGraphError(f'qualified product binding {index}: unknown source cell {owner}')
        if owner_kind == 'NON_CELL' and owner not in non_cell_owners:
            raise WorkGraphError(f'qualified product binding {index}: unknown non-cell owner {owner}')
        key = (owner_kind, owner)
        if key in bindings:
            raise WorkGraphError(f'duplicate qualified product owner: {owner_kind}/{owner}')
        commit = _require_commit(binding['commit'], 'qualified product binding commit')
        _require_commit(binding['tree'], 'qualified product binding tree')
        _require_digest(binding['review_sha256'], 'qualified product binding review')
        if commit in commits:
            raise WorkGraphError(f'qualified product emitted more than once: {commit}')
        bindings[key] = binding
        commits[commit] = binding
    expected_owners = {('CELL', owner) for owner in source_cells} | {('NON_CELL', owner) for owner in non_cell_owners}
    if set(bindings) != expected_owners:
        raise WorkGraphError('qualified product bindings do not cover authoritative owners')
    dispositions_value = contract['disposition_bindings']
    if type(dispositions_value) is not list or len(dispositions_value) != len(commits):
        raise WorkGraphError('qualified product dispositions must cover every product')
    dispositions: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(dispositions_value):
        disposition = _require_object(value, f'product disposition binding {index}')
        if set(disposition) != {'product_commit', 'kind', 'target'}:
            raise WorkGraphError(f'product disposition binding {index}: exact members required')
        product_commit = _require_commit(disposition['product_commit'], 'product disposition product_commit')
        if product_commit not in commits or product_commit in dispositions:
            raise WorkGraphError('product disposition: unknown or duplicate product')
        kind = _require_string(disposition['kind'], 'product disposition kind')
        target = _require_string(disposition['target'], 'product disposition target')
        if kind not in PRODUCT_DISPOSITIONS:
            raise WorkGraphError(f'product disposition: unknown disposition {kind}')
        if kind == 'CONSUMED' and target not in by_id:
            raise WorkGraphError(f'product disposition: unknown consumer {target}')
        if kind == 'COMPOSED' and (target not in commits or target == product_commit):
            raise WorkGraphError(f'product disposition: unknown composition {target}')
        if kind in {'SUPERSEDED', 'REJECTED'} and target not in commits:
            raise WorkGraphError(f'product disposition: unknown product identity {target}')
        if kind == 'EXPLICITLY_DEFERRED_TO_NAMED_JOIN' and target not in join_owners:
            raise WorkGraphError(f'product disposition: unresolved named join {target}')
        if kind == 'INTEGRATED':
            _require_commit(target, 'product disposition integration head')
        dispositions[product_commit] = disposition
    visiting_products: set[str] = set()
    visited_products: set[str] = set()

    def visit_product(commit: str) -> None:
        if commit in visiting_products:
            raise WorkGraphError(f'qualified product composition cycle includes {commit}')
        if commit in visited_products:
            return
        visiting_products.add(commit)
        disposition = dispositions[commit]
        if disposition['kind'] == 'COMPOSED':
            visit_product(str(disposition['target']))
        visiting_products.remove(commit)
        visited_products.add(commit)
    for commit in sorted(commits):
        visit_product(commit)
    for commit, disposition in dispositions.items():
        if disposition['kind'] == 'COMPOSED':
            target_disposition = dispositions[str(disposition['target'])]
            if target_disposition['kind'] in {'SUPERSEDED', 'REJECTED'}:
                raise WorkGraphError(f"product disposition: composition target is not current {disposition['target']}")
    authorizations_value = contract['composition_authorizations']
    if type(authorizations_value) is not list:
        raise WorkGraphError('composition authorizations: array required')
    authorizations: list[dict[str, JSONValue]] = []
    reviews = {str(binding['review_sha256']) for binding in bindings.values()}
    for index, value in enumerate(authorizations_value):
        item = _require_object(value, f'composition authorization {index}')
        if set(item) != {'owner', 'products', 'qualification_review_sha256', 'integration_authority'}:
            raise WorkGraphError(f'composition authorization {index}: exact members required')
        owner = _require_string(item['owner'], 'composition authorization owner')
        if owner not in by_id:
            raise WorkGraphError(f'composition authorization {index}: unknown cell {owner}')
        products = [_require_commit(product, 'composition authorization product') for product in _require_string_list(item['products'], 'composition authorization products')]
        if products != sorted(products) or any((product not in commits for product in products)):
            raise WorkGraphError(f'composition authorization {index}: unknown current product')
        review = _require_digest(item['qualification_review_sha256'], 'composition authorization review')
        if review not in reviews:
            raise WorkGraphError(f'composition authorization {index}: unbound qualification review')
        if item['integration_authority'] != receipt:
            raise WorkGraphError(f'composition authorization {index}: unresolved integration authority')
        if any((canonical_json_v1(item) == canonical_json_v1(prior) for prior in authorizations)):
            raise WorkGraphError('duplicate composition authorization')
        authorizations.append(item)
    consumers_value = contract['future_consumers']
    if type(consumers_value) is not list:
        raise WorkGraphError('future consumers: array required')
    future_consumers: list[dict[str, JSONValue]] = []
    for index, value in enumerate(consumers_value):
        item = _require_object(value, f'future consumer {index}')
        if set(item) != {'product_commit', 'cell_id'}:
            raise WorkGraphError(f'future consumer {index}: exact members required')
        product_commit = _require_commit(item['product_commit'], 'future consumer product')
        cell_id = _require_string(item['cell_id'], 'future consumer cell')
        if product_commit not in commits or cell_id not in by_id:
            raise WorkGraphError(f'future consumer {index}: unresolved binding')
        if dispositions[product_commit]['kind'] in {'SUPERSEDED', 'REJECTED'}:
            raise WorkGraphError(f'future consumer {index}: product is not current')
        if any((canonical_json_v1(item) == canonical_json_v1(prior) for prior in future_consumers)):
            raise WorkGraphError('duplicate future consumer')
        future_consumers.append(item)
    return {'authority': source, 'source_cells': sorted(source_cells), 'non_cell_owners': non_cell_owners, 'join_owners': join_owners, 'bindings': bindings, 'commits': commits, 'dispositions': dispositions, 'composition_authorizations': authorizations, 'future_consumers': future_consumers}

def _validate_preparation_v1(cell: dict[str, JSONValue], by_id: dict[str, dict[str, JSONValue]], groups: dict[str, JSONValue]) -> dict[str, JSONValue]:
    cell_id = str(cell['id'])
    value = _require_object(cell['preparation'], f'cell {cell_id} preparation')
    expected = {'kinds', 'effect_class', 'final_composed_only', 'execution_unavailable', 'rank', 'record'}
    if set(value) != expected:
        raise WorkGraphError(f'cell {cell_id}: incomplete preparation declaration')
    kinds = _require_string_list(value['kinds'], f'cell {cell_id} preparation kinds')
    if kinds != sorted(kinds) or not set(kinds) <= PREPARATION_KINDS:
        raise WorkGraphError(f'cell {cell_id}: invalid preparation kinds')
    if value['effect_class'] != 'READ_ONLY_EFFECT_FREE':
        raise WorkGraphError(f'cell {cell_id}: preparation must be effect-free')
    if type(value['final_composed_only']) is not bool or value['final_composed_only']:
        raise WorkGraphError(f'cell {cell_id}: final-composed-only preparation forbidden')
    unavailable = _require_object(value['execution_unavailable'], f'cell {cell_id} execution_unavailable')
    states = {name: str(item['state']) for name, item in by_id.items()}
    required_predecessors = {str(dep) for dep in cell['deps']}
    if cell['state'] == 'BLOCKED':
        if set(unavailable) != {'kind', 'dependencies'} or unavailable['kind'] != 'UNMET_DEPENDENCIES':
            raise WorkGraphError(f'cell {cell_id}: blocked preparation needs dependencies')
        declared = _require_string_list(unavailable['dependencies'], f'cell {cell_id} preparation dependencies')
        actual = sorted((str(dep) for dep in cell['deps'] if states[str(dep)] != 'DONE'))
        if declared != actual:
            raise WorkGraphError(f'cell {cell_id}: preparation dependency binding mismatch')
    elif cell['state'] == 'READY':
        if set(unavailable) != {'kind', 'group', 'holders'} or unavailable['kind'] != 'LIVE_HOLD':
            raise WorkGraphError(f'cell {cell_id}: ready preparation needs live hold')
        group = _require_string(unavailable['group'], f'cell {cell_id} preparation group')
        holders = _require_string_list(unavailable['holders'], f'cell {cell_id} preparation holders')
        members = groups.get(group)
        if type(members) is not list or cell_id not in members:
            raise WorkGraphError(f'cell {cell_id}: unresolved preparation hold')
        actual_holders = sorted((str(member) for member in members if states[str(member)] == 'ACTIVE'))
        if holders != actual_holders or not holders:
            raise WorkGraphError(f'cell {cell_id}: preparation live-holder mismatch')
        required_predecessors.update(holders)
    else:
        raise WorkGraphError(f'cell {cell_id}: state is not preparation-eligible')
    rank = _require_object(value['rank'], f'cell {cell_id} preparation rank')
    rank_fields = {'terminal_unlock_value', 'expected_reuse', 'cost', 'invalidation_risk'}
    if set(rank) != rank_fields or any((type(rank[name]) is not int or rank[name] < 0 for name in rank_fields)):
        raise WorkGraphError(f'cell {cell_id}: invalid preparation rank')
    record = _require_object(value['record'], f'cell {cell_id} preparation record')
    record_fields = {'graph_path', 'receipt', 'predecessors', 'interface_assumptions', 'inspected_paths', 'proposed_paths', 'allowed_work', 'forbidden_work', 'cost_boundary', 'invalidators', 'activation_revalidation'}
    if set(record) != record_fields:
        raise WorkGraphError(f'cell {cell_id}: incomplete preparation record')
    _require_string(record['graph_path'], f'cell {cell_id} graph_path')
    receipt = _require_string(record['receipt'], f'cell {cell_id} receipt')
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError(f'cell {cell_id}: invalid continuity receipt')
    predecessors = record['predecessors']
    if type(predecessors) is not list or not predecessors:
        raise WorkGraphError(f'cell {cell_id}: predecessor observations required')
    seen: set[str] = set()
    for index, item in enumerate(predecessors):
        predecessor = _require_object(item, f'cell {cell_id} predecessor {index}')
        if set(predecessor) != {'cell_id', 'state', 'identity'}:
            raise WorkGraphError(f'cell {cell_id}: invalid predecessor observation')
        predecessor_id = _require_string(predecessor['cell_id'], f'cell {cell_id} predecessor')
        if predecessor_id in seen or predecessor_id not in by_id:
            raise WorkGraphError(f'cell {cell_id}: fabricated or duplicate predecessor')
        seen.add(predecessor_id)
        if predecessor['state'] != by_id[predecessor_id]['state']:
            raise WorkGraphError(f'cell {cell_id}: stale predecessor state')
        identity = _require_object(predecessor['identity'], f'cell {cell_id} predecessor identity')
        predecessor_cell = by_id[predecessor_id]
        if predecessor_cell['state'] == 'DONE' and predecessor_cell.get('source_bearing') is True:
            product_result = _validate_product_result_v1(predecessor_cell.get('result'), f'cell {predecessor_id} result', by_id)
            product = _require_object(product_result['product'], 'predecessor product')
            expected_identity: dict[str, JSONValue] = {'kind': 'QUALIFIED_PRODUCT', 'commit': product['commit'], 'tree': product['tree'], 'review_sha256': product['review_sha256']}
        else:
            expected_identity = {'kind': 'UNAVAILABLE', 'reason': 'NOT_DONE' if predecessor_cell['state'] != 'DONE' else 'NON_SOURCE_PRODUCT'}
        if identity != expected_identity:
            raise WorkGraphError(f'cell {cell_id}: predecessor identity mismatch for {predecessor_id}')
    if seen != required_predecessors:
        missing = sorted(required_predecessors - seen)
        extra = sorted(seen - required_predecessors)
        raise WorkGraphError(f'cell {cell_id}: predecessor set mismatch; missing={missing}; extra={extra}')
    assumptions = _require_object(record['interface_assumptions'], f'cell {cell_id} interface assumptions')
    if not assumptions:
        raise WorkGraphError(f'cell {cell_id}: interface assumptions required')
    for key, digest in assumptions.items():
        _require_string(key, f'cell {cell_id} assumption key')
        _require_digest(digest, f'cell {cell_id} assumption {key}')
    _require_string_list(record['inspected_paths'], f'cell {cell_id} inspected_paths')
    _require_string_list(record['proposed_paths'], f'cell {cell_id} proposed_paths')
    allowed = _require_string_list(record['allowed_work'], f'cell {cell_id} allowed_work')
    if allowed != kinds:
        raise WorkGraphError(f'cell {cell_id}: allowed work must equal declared kinds')
    forbidden = set(_require_string_list(record['forbidden_work'], f'cell {cell_id} forbidden_work'))
    if forbidden != PREPARATION_FORBIDDEN:
        raise WorkGraphError(f'cell {cell_id}: incomplete forbidden-work boundary')
    _require_string(record['cost_boundary'], f'cell {cell_id} cost_boundary')
    invalidators = set(_require_string_list(record['invalidators'], f'cell {cell_id} invalidators'))
    if not {'TARGET_STATE', 'DEPENDENCY_RESULT', 'INTERFACE_ASSUMPTION'} <= invalidators:
        raise WorkGraphError(f'cell {cell_id}: incomplete invalidation boundary')
    activation = set(_require_string_list(record['activation_revalidation'], f'cell {cell_id} activation_revalidation'))
    if activation != {'CURRENTNESS', 'DEPENDENCY_RESULTS', 'INTERFACE_ASSUMPTIONS', 'CAUSAL_RED'}:
        raise WorkGraphError(f'cell {cell_id}: incomplete activation revalidation')
    return value

def _validate_graph(graph: dict[str, JSONValue], product_authority_bytes: bytes | None=None) -> list[dict[str, JSONValue]]:
    if graph.get('schema') != 'implementaudit.work-graph.v1':
        raise WorkGraphError('WORK_GRAPH.json: unsupported schema')
    population = _require_object(graph.get('population'), '$.population')
    declared_total = population.get('total_cells')
    if type(declared_total) is not int or declared_total < 0:
        raise WorkGraphError('$.population.total_cells: non-negative integer required')
    cells_value = graph.get('cells')
    if type(cells_value) is not list:
        raise WorkGraphError('$.cells: array required')
    cells: list[dict[str, JSONValue]] = []
    by_id: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(cells_value):
        cell = _require_object(value, f'$.cells[{index}]')
        cell_id = _require_string(cell.get('id'), f'$.cells[{index}].id')
        if cell_id in by_id:
            raise WorkGraphError(f'duplicate cell id: {cell_id}')
        state = cell.get('state')
        if state not in KNOWN_STATES:
            raise WorkGraphError(f'unknown cell state for {cell_id}: {state}')
        deps = cell.get('deps')
        if type(deps) is not list:
            raise WorkGraphError(f'cell {cell_id}: deps array required')
        seen_deps: set[str] = set()
        for dep in deps:
            dep_id = _require_string(dep, f'cell {cell_id} dependency')
            if dep_id in seen_deps:
                raise WorkGraphError(f'cell {cell_id}: duplicate dependency {dep_id}')
            seen_deps.add(dep_id)
        cells.append(cell)
        by_id[cell_id] = cell
    counts = {state: sum((cell['state'] == state for cell in cells)) for state in KNOWN_STATES}
    if len(cells) != declared_total or sum(counts.values()) != declared_total:
        raise WorkGraphError('frontier count does not equal population')
    for cell in cells:
        cell_id = str(cell['id'])
        for dep in cell['deps']:
            if dep not in by_id:
                raise WorkGraphError(f'cell {cell_id}: unknown dependency {dep}')
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(cell_id: str) -> None:
        if cell_id in visiting:
            raise WorkGraphError(f'dependency cycle includes {cell_id}')
        if cell_id in visited:
            return
        visiting.add(cell_id)
        for dep in by_id[cell_id]['deps']:
            visit(str(dep))
        visiting.remove(cell_id)
        visited.add(cell_id)
    for cell_id in sorted(by_id):
        visit(cell_id)
    groups = graph.get('serialization_groups')
    if type(groups) is not dict:
        raise WorkGraphError('$.serialization_groups: writer/resource holds required')
    for group, members in groups.items():
        _require_string(group, 'serialization group name')
        if not (group.startswith('W_') or group.startswith('R_') or group.startswith('RESOURCE_')):
            raise WorkGraphError(f'serialization group {group}: unknown hold kind')
        if type(members) is not list or not members:
            raise WorkGraphError(f'serialization group {group}: non-empty array required')
        seen_members: set[str] = set()
        for member in members:
            member_id = _require_string(member, f'serialization group {group}')
            if member_id not in by_id:
                raise WorkGraphError(f'serialization group {group}: unknown cell {member_id}')
            if member_id in seen_members:
                raise WorkGraphError(f'serialization group {group}: duplicate cell {member_id}')
            seen_members.add(member_id)
    for cell in cells:
        cell_id = str(cell['id'])
        if 'source_bearing' in cell and type(cell['source_bearing']) is not bool:
            raise WorkGraphError(f'cell {cell_id}: source_bearing must be boolean')
        if 'preparation' in cell:
            _validate_preparation_v1(cell, by_id, groups)
    product_contract = _validate_product_contract_v1(graph, cells, by_id, product_authority_bytes)
    for cell in cells:
        cell_id = str(cell['id'])
        if cell.get('source_bearing') is True:
            if cell['state'] != 'DONE':
                raise WorkGraphError(f'cell {cell_id}: unqualified source result forbidden')
            result = _validate_product_result_v1(cell.get('result'), f'cell {cell_id} result', by_id)
            if product_contract is None:
                raise WorkGraphError('qualified product contract required for governed products')
            bindings = product_contract['bindings']
            dispositions = product_contract['dispositions']
            assert type(bindings) is dict and type(dispositions) is dict
            binding = bindings.get(('CELL', cell_id))
            if type(binding) is not dict:
                raise WorkGraphError(f'cell {cell_id}: authoritative product binding missing')
            product = _require_object(result['product'], f'cell {cell_id} result.product')
            if product != {'commit': binding['commit'], 'tree': binding['tree'], 'review_sha256': binding['review_sha256']}:
                raise WorkGraphError(f'cell {cell_id}: product identity disagrees with authority')
            disposition = _require_object(result['disposition'], f'cell {cell_id} result.disposition')
            bound_disposition = dispositions.get(str(product['commit']))
            if type(bound_disposition) is not dict or disposition != {'kind': bound_disposition['kind'], 'target': bound_disposition['target']}:
                raise WorkGraphError(f'cell {cell_id}: product disposition disagrees with authority')
    frontier = graph.get('frontier')
    if frontier is not None:
        cached = _require_object(frontier, '$.frontier')
        expected_scalars = {'population': declared_total, 'done': counts['DONE'], 'active': counts['ACTIVE'], 'ready': counts['READY'], 'blocked': counts['BLOCKED']}
        if any((cached.get(key) != value for key, value in expected_scalars.items())):
            raise WorkGraphError('stale frontier projection')
        for key, state in (('active_ids', 'ACTIVE'), ('ready_ids', 'READY')):
            expected_ids = sorted((str(cell['id']) for cell in cells if cell['state'] == state))
            if cached.get(key) != expected_ids:
                raise WorkGraphError(f'stale frontier projection: {key}')
    digest = graph.get('digest')
    if digest is not None:
        if type(digest) is not str or not DIGEST_RE.fullmatch(digest):
            raise WorkGraphError('WORK_GRAPH.json: invalid digest')
        unsigned = dict(graph)
        del unsigned['digest']
        expected_digest = hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()
        if not hmac.compare_digest(digest, expected_digest):
            raise WorkGraphError('WORK_GRAPH.json: stale digest')
    return cells

def summarize_blocked_v1(cells: list[dict[str, JSONValue]]) -> dict[str, JSONValue]:
    states = {str(cell['id']): str(cell['state']) for cell in cells}
    summary: dict[str, JSONValue] = {}
    for cell in sorted(cells, key=lambda item: str(item['id'])):
        if cell['state'] != 'BLOCKED':
            continue
        summary[str(cell['id'])] = sorted((str(dep) for dep in cell['deps'] if states[str(dep)] != 'DONE'))
    return summary

def normalize_holds_v1(serialization_groups: JSONValue, kind: str) -> dict[str, JSONValue]:
    groups = _require_object(serialization_groups, '$.serialization_groups')
    if kind == 'writer':
        selected = lambda name: name.startswith('W_')
    elif kind == 'resource':
        selected = lambda name: name.startswith('R_') or name.startswith('RESOURCE_')
    else:
        raise WorkGraphError(f'unknown hold kind: {kind}')
    return {group: sorted((str(member) for member in members)) for group, members in sorted(groups.items()) if selected(group)}

def compile_preparation_frontier_v1(graph: dict[str, JSONValue], cells: list[dict[str, JSONValue]], graph_bytes: bytes) -> list[dict[str, JSONValue]]:
    graph_id = graph.get('graph_id')
    prepared = [cell for cell in cells if 'preparation' in cell]
    if not prepared:
        return []
    _require_string(graph_id, '$.graph_id')
    records: list[dict[str, JSONValue]] = []
    for cell in prepared:
        cell_id = str(cell['id'])
        declaration = _require_object(cell['preparation'], f'cell {cell_id} preparation')
        rank = _require_object(declaration['rank'], f'cell {cell_id} rank')
        source_record = _require_object(declaration['record'], f'cell {cell_id} preparation record')
        unavailable = _require_object(declaration['execution_unavailable'], f'cell {cell_id} unavailable')
        target_binding = {'cell_id': cell_id, 'state': cell['state'], 'deps': sorted((str(dep) for dep in cell['deps'])), 'unavailable': unavailable, 'predecessors': source_record['predecessors'], 'interface_assumptions': source_record['interface_assumptions'], 'inspected_paths': sorted((str(path) for path in source_record['inspected_paths'])), 'proposed_paths': sorted((str(path) for path in source_record['proposed_paths']))}
        record: dict[str, JSONValue] = {'schema': 'implementaudit.preparation-record.v1', 'graph': {'schema': graph['schema'], 'id': graph_id, 'path': source_record['graph_path'], 'bytes': len(graph_bytes), 'sha256': hashlib.sha256(graph_bytes).hexdigest()}, 'receipt': source_record['receipt'], 'cell_id': cell_id, 'observed_state': cell['state'], 'execution_unavailable': unavailable, 'predecessors': source_record['predecessors'], 'interface_assumptions': source_record['interface_assumptions'], 'inspected_paths': sorted((str(path) for path in source_record['inspected_paths'])), 'proposed_paths': sorted((str(path) for path in source_record['proposed_paths'])), 'allowed_work': declaration['kinds'], 'forbidden_work': sorted((str(item) for item in source_record['forbidden_work'])), 'rank': rank, 'cost_boundary': source_record['cost_boundary'], 'invalidators': source_record['invalidators'], 'activation_revalidation': source_record['activation_revalidation'], 'target_binding_sha256': hashlib.sha256(canonical_json_v1(target_binding)).hexdigest(), 'lifecycle_credit': 'NONE', 'implementation_evidence': 'NONE', 'authority_minted': 'NONE'}
        record['record_sha256'] = hashlib.sha256(canonical_json_v1(record)).hexdigest()
        records.append(record)
    return sorted(records, key=lambda record: (-int(_require_object(record['rank'], 'rank')['terminal_unlock_value']), -int(_require_object(record['rank'], 'rank')['expected_reuse']), int(_require_object(record['rank'], 'rank')['cost']), int(_require_object(record['rank'], 'rank')['invalidation_risk']), str(record['cell_id'])))

def validate_preparation_activation_v1(record: dict[str, JSONValue], *, current_receipt: str, current_graph_bytes: bytes, causal_red_passed: bool, current_product_authority_bytes: bytes | None=None) -> bool:
    """Fail closed unless every activation-time invalidator is re-observed."""
    if record.get('schema') != 'implementaudit.preparation-record.v1':
        raise WorkGraphError('preparation activation: unknown record schema')
    stored_hash = _require_digest(record.get('record_sha256'), 'preparation activation record_sha256')
    unsigned = dict(record)
    del unsigned['record_sha256']
    if not hmac.compare_digest(stored_hash, hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()):
        raise WorkGraphError('preparation activation: stale record digest')
    if not RECEIPT_RE.fullmatch(current_receipt) or current_receipt != record.get('receipt'):
        raise WorkGraphError('preparation activation: currentness revalidation failed')
    if type(causal_red_passed) is not bool or not causal_red_passed:
        raise WorkGraphError('preparation activation: causal RED not revalidated')
    try:
        current_projection = compile_frontier_projection(current_graph_bytes, current_product_authority_bytes)
    except WorkGraphError as exc:
        raise WorkGraphError(f'preparation activation: current graph revalidation failed: {exc}') from exc
    current_records = current_projection.get('preparation_frontier', [])
    if type(current_records) is not list:
        raise WorkGraphError('preparation activation: current preparation frontier missing')
    current = next((item for item in current_records if type(item) is dict and item.get('cell_id') == record.get('cell_id')), None)
    if current is None:
        raise WorkGraphError('preparation activation: current preparation record missing')
    if current.get('target_binding_sha256') != record.get('target_binding_sha256'):
        raise WorkGraphError('preparation activation: target binding changed')
    if canonical_json_v1(current.get('predecessors')) != canonical_json_v1(record.get('predecessors')):
        raise WorkGraphError('preparation activation: dependency results changed')
    if canonical_json_v1(current.get('interface_assumptions')) != canonical_json_v1(record.get('interface_assumptions')):
        raise WorkGraphError('preparation activation: interface assumptions changed')
    if canonical_json_v1(current.get('graph')) != canonical_json_v1(record.get('graph')):
        raise WorkGraphError('preparation activation: exact graph binding changed')
    return True

def compile_product_frontier_v1(graph: dict[str, JSONValue], cells: list[dict[str, JSONValue]], product_authority_bytes: bytes | None=None) -> dict[str, JSONValue] | None:
    by_id = {str(cell['id']): cell for cell in cells}
    contract = _validate_product_contract_v1(graph, cells, by_id, product_authority_bytes)
    if contract is None:
        return None
    bindings = contract['bindings']
    dispositions = contract['dispositions']
    assert type(bindings) is dict and type(dispositions) is dict
    entries: list[dict[str, JSONValue]] = []
    for cell in cells:
        if cell.get('source_bearing') is not True or cell['state'] != 'DONE':
            continue
        result = _validate_product_result_v1(cell['result'], f"cell {cell['id']} result", by_id)
        entries.append({'owner_kind': 'CELL', 'owner': cell['id'], **result})
    topology = graph.get('integration_topology')
    if type(topology) is dict and 'qualified_products' in topology:
        noncells = topology['qualified_products']
        if type(noncells) is not list:
            raise WorkGraphError('$.integration_topology.qualified_products: array required')
        seen_owners: set[str] = set()
        for index, item in enumerate(noncells):
            entry = _require_object(item, f'non-cell product {index}')
            if set(entry) != {'owner', 'result'}:
                raise WorkGraphError('non-cell product: owner and result required')
            owner = _require_string(entry['owner'], f'non-cell product {index} owner')
            if owner in seen_owners:
                raise WorkGraphError(f'duplicate non-cell product owner: {owner}')
            seen_owners.add(owner)
            result = _validate_product_result_v1(entry['result'], f'non-cell product {owner} result', by_id)
            binding = bindings.get(('NON_CELL', owner))
            if type(binding) is not dict:
                raise WorkGraphError(f'non-cell product {owner}: unknown authoritative owner')
            product = _require_object(result['product'], f'non-cell product {owner} product')
            if product != {'commit': binding['commit'], 'tree': binding['tree'], 'review_sha256': binding['review_sha256']}:
                raise WorkGraphError(f'non-cell product {owner}: identity disagrees with authority')
            disposition = _require_object(result['disposition'], f'non-cell product {owner} disposition')
            bound_disposition = dispositions.get(str(product['commit']))
            if type(bound_disposition) is not dict or disposition != {'kind': bound_disposition['kind'], 'target': bound_disposition['target']}:
                raise WorkGraphError(f'non-cell product {owner}: disposition disagrees with authority')
            entries.append({'owner_kind': 'NON_CELL', 'owner': owner, **result})
    if not entries:
        raise WorkGraphError('qualified product contract has no realised products')
    product_by_commit: dict[str, dict[str, JSONValue]] = {}
    for entry in entries:
        product = _require_object(entry['product'], 'product')
        commit = str(product['commit'])
        if commit in product_by_commit:
            raise WorkGraphError(f'qualified product emitted more than once: {commit}')
        product_by_commit[commit] = entry
    if set(product_by_commit) != set(contract['commits']):
        raise WorkGraphError('qualified product runtime entries do not cover authority census')
    integration_heads: set[str] = set()
    if type(topology) is dict and 'integration_heads' in topology:
        for head in _require_string_list(topology['integration_heads'], '$.integration_topology.integration_heads'):
            integration_heads.add(_require_commit(head, 'integration head'))
    for entry in entries:
        product = _require_object(entry['product'], 'product')
        disposition = _require_object(entry['disposition'], 'disposition')
        kind = str(disposition['kind'])
        target = str(disposition['target'])
        if kind == 'INTEGRATED' and target not in integration_heads:
            raise WorkGraphError(f"product {product['commit']}: unknown integration head {target}")
        if kind in {'SUPERSEDED', 'REJECTED'}:
            if target not in product_by_commit:
                raise WorkGraphError(f"product {product['commit']}: unknown product identity {target}")
            if kind == 'SUPERSEDED' and target == product['commit']:
                raise WorkGraphError(f"product {product['commit']}: self-supersession forbidden")
    entries.sort(key=lambda entry: (str(entry['owner_kind']), str(entry['owner']), str(_require_object(entry['product'], 'product')['commit'])))
    counts = {kind: 0 for kind in sorted(PRODUCT_DISPOSITIONS)}
    target_counts: dict[str, int] = {}
    for entry in entries:
        disposition = _require_object(entry['disposition'], 'disposition')
        kind = str(disposition['kind'])
        counts[kind] += 1
    future_consumers = contract['future_consumers']
    assert type(future_consumers) is list
    for item in future_consumers:
        assert type(item) is dict
        cell_id = str(item['cell_id'])
        target_counts[cell_id] = target_counts.get(cell_id, 0) + 1
    proposals: list[dict[str, JSONValue]] = []
    if type(topology) is dict and 'composition_proposals' in topology:
        raw_proposals = topology['composition_proposals']
        if type(raw_proposals) is not list:
            raise WorkGraphError('$.integration_topology.composition_proposals: array required')
        states = {str(cell['id']): str(cell['state']) for cell in cells}
        groups = _require_object(graph['serialization_groups'], '$.serialization_groups')
        seen_proposals: set[str] = set()
        current_commits = {commit for commit, entry in product_by_commit.items() if _require_object(entry['disposition'], 'disposition')['kind'] not in {'SUPERSEDED', 'REJECTED'}}
        for index, value in enumerate(raw_proposals):
            proposal = _require_object(value, f'composition proposal {index}')
            if set(proposal) != {'owner', 'products', 'qualification_review_sha256', 'integration_authority'}:
                raise WorkGraphError(f'composition proposal {index}: exact members required')
            owner = _require_string(proposal['owner'], f'composition proposal {index} owner')
            if owner in seen_proposals:
                raise WorkGraphError(f'duplicate composition proposal owner: {owner}')
            seen_proposals.add(owner)
            if owner not in by_id:
                raise WorkGraphError(f'composition proposal {index}: unknown cell {owner}')
            product_commits = [_require_commit(item, f'composition proposal {index} product') for item in _require_string_list(proposal['products'], f'composition proposal {index} products')]
            if product_commits != sorted(product_commits):
                raise WorkGraphError(f'composition proposal {index}: products must be sorted')
            if any((commit not in current_commits for commit in product_commits)):
                raise WorkGraphError(f'composition proposal {index}: unknown current product')
            _require_digest(proposal['qualification_review_sha256'], f'composition proposal {index} qualification review')
            authority = _require_string(proposal['integration_authority'], f'composition proposal {index} integration authority')
            if not RECEIPT_RE.fullmatch(authority):
                raise WorkGraphError(f'composition proposal {index}: unresolved integration authority')
            authorizations = contract['composition_authorizations']
            assert type(authorizations) is list
            if not any((canonical_json_v1(proposal) == canonical_json_v1(item) for item in authorizations)):
                raise WorkGraphError(f'composition proposal {index}: not present in authoritative bindings')
            cell = by_id[owner]
            if cell['state'] != 'READY' or any((states[str(dep)] != 'DONE' for dep in cell['deps'])):
                raise WorkGraphError(f'composition proposal {index}: dependencies do not permit composition')
            active_conflicts = sorted((str(member) for members in groups.values() if type(members) is list and owner in members for member in members if member != owner and states[str(member)] == 'ACTIVE'))
            if active_conflicts:
                raise WorkGraphError(f'composition proposal {index}: live hold conflict')
            proposals.append({'owner': owner, 'products': product_commits, 'qualification_review_sha256': proposal['qualification_review_sha256'], 'integration_authority': authority})
        proposals.sort(key=lambda item: (str(item['owner']), item['products']))
    ready = [str(cell['id']) for cell in cells if cell['state'] == 'READY']
    preparation_ids = [str(cell['id']) for cell in cells if 'preparation' in cell]
    summary = summarize_product_dispositions_v1([str(_require_object(entry['disposition'], 'disposition')['kind']) for entry in entries])
    return {'qualified_products': len(entries), 'current_products': len(entries) - counts['SUPERSEDED'] - counts['REJECTED'], 'integration_debt': counts['COMPOSED'] + counts['EXPLICITLY_DEFERRED_TO_NAMED_JOIN'], 'counts': counts, 'potentially_stranded': summary['potentially_stranded'], 'p0_execution_planning_escalation': summary['p0'], 'products': entries, 'composition_proposals': proposals, 'ready_preference': sorted(ready, key=lambda cell_id: (-target_counts.get(cell_id, 0), cell_id)), 'preparation_preference': sorted(preparation_ids, key=lambda cell_id: (-target_counts.get(cell_id, 0), cell_id))}

def summarize_product_dispositions_v1(dispositions: list[str | None]) -> dict[str, JSONValue]:
    counts = {kind: 0 for kind in PRODUCT_DISPOSITIONS}
    stranded = 0
    for index, kind in enumerate(dispositions):
        if kind is None:
            stranded += 1
        elif kind in counts:
            counts[kind] += 1
        else:
            raise WorkGraphError(f'product disposition {index}: unknown disposition {kind}')
    return {'total': len(dispositions), 'consumed': counts['CONSUMED'], 'composed': counts['COMPOSED'], 'integrated': counts['INTEGRATED'], 'superseded': counts['SUPERSEDED'], 'rejected': counts['REJECTED'], 'deferred': counts['EXPLICITLY_DEFERRED_TO_NAMED_JOIN'], 'potentially_stranded': stranded, 'p0': 'TRIGGERED' if stranded else 'NOT_TRIGGERED'}

def _proximal_no_authority_v1() -> dict[str, JSONValue]:
    return {key: 'NONE' for key in ('closure', 'done', 'lifecycle_credit', 'merge', 'package', 'publication', 'release')}

def _proximal_object_v1(value: JSONValue, path: str, fields: set[str], *, booleans: set[str]=frozenset(), digests: set[str]=frozenset()) -> dict[str, JSONValue]:
    result = _require_object(value, path)
    _require_exact_members(result, fields, path)
    for field in booleans:
        _require_bool(result[field], f'{path}.{field}')
    for field in digests:
        _require_digest(result[field], f'{path}.{field}')
    return result

def _proximal_candidate_v1(value: JSONValue, path: str) -> dict[str, JSONValue]:
    result = _proximal_object_v1(value, path, {'commit', 'tree', 'input_sha256', 'identity_frozen'}, booleans={'identity_frozen'}, digests={'input_sha256'})
    _require_commit(result['commit'], f'{path}.commit')
    _require_commit(result['tree'], f'{path}.tree')
    return result

def _proximal_currentness_v1(value: JSONValue, path: str) -> dict[str, JSONValue]:
    result = _proximal_object_v1(value, path, {'receipt', 'current'}, booleans={'current'})
    receipt = _require_string(result['receipt'], f'{path}.receipt')
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError(f'{path}.receipt: continuity receipt required')
    return result

def _proximal_digest_v1(value: dict[str, JSONValue]) -> dict[str, JSONValue]:
    value['digest'] = hashlib.sha256(canonical_json_v1(value)).hexdigest()
    return value

def compile_proximal_schedule_v1(request_bytes: bytes) -> dict[str, JSONValue]:
    """Compile one transient, exact-identity proximal scheduling decision."""
    path = 'proximal scheduling request'
    request = _proximal_object_v1(decode_strict_json_bytes(request_bytes, path), path, {'schema', 'candidate', 'currentness', 'minimum_recoverability_gate', 'diagnostic', 'resilience', 'relationships', 'capacity', 'information', 'workflow_serialization_reason'})
    if request['schema'] != 'implementaudit.proximal-scheduling-request.v1':
        raise WorkGraphError(f'{path}: unsupported schema')
    candidate = _proximal_candidate_v1(request['candidate'], f'{path}.candidate')
    currentness = _proximal_currentness_v1(request['currentness'], f'{path}.currentness')
    gate = _proximal_object_v1(request['minimum_recoverability_gate'], f'{path}.minimum_recoverability_gate', {'evidence_sha256', 'passed'}, booleans={'passed'}, digests={'evidence_sha256'})
    diagnostic_fields = {'bounded', 'recoverable', 'isolated', 'non_public', 'non_release_authoritative', 'non_lifecycle_authoritative', 'irreversible_effect_protected', 'authoritative_publication_protected', 'consequence_critical'}
    diagnostic = _proximal_object_v1(request['diagnostic'], f'{path}.diagnostic', diagnostic_fields, booleans=diagnostic_fields)
    resilience_fields = {'evidence_sha256', 'blast_radius_bounded', 'protected_non_targets_bounded', 'rollback_verified', 'retreat_available', 'before_after_observable', 'unknown_completion_contained'}
    resilience = _proximal_object_v1(request['resilience'], f'{path}.resilience', resilience_fields, booleans=resilience_fields - {'evidence_sha256'}, digests={'evidence_sha256'})
    relationship_fields = {'hard_prerequisite', 'writer_or_resource_exclusion', 'acceptance_prerequisite', 'informational_or_differential'}
    relationships = _proximal_object_v1(request['relationships'], f'{path}.relationships', relationship_fields, booleans=relationship_fields)
    capacity = _proximal_object_v1(request['capacity'], f'{path}.capacity', {'available', 'host_exclusion'}, booleans={'available', 'host_exclusion'})
    information_fields = {'delay_cost_material', 'decision_relevant', 'live_fidelity_higher_than_simulation', 'diagnostic_information_value_material', 'further_serialization_complexity_cost_material', 'further_serialization_coupling_cost_material', 'further_serialization_delay_cost_material', 'further_serialization_latent_failure_cost_material'}
    information = _proximal_object_v1(request['information'], f'{path}.information', information_fields, booleans=information_fields)
    effect_protected = all((diagnostic[key] is True for key in ('non_public', 'non_release_authoritative', 'non_lifecycle_authoritative', 'irreversible_effect_protected', 'authoritative_publication_protected')))
    safe_shape = all((diagnostic[key] is True for key in ('bounded', 'recoverable', 'isolated')))
    containment = all((resilience[key] is True for key in ('rollback_verified', 'retreat_available', 'before_after_observable', 'unknown_completion_contained')))
    impact_bounded = all((resilience[key] is True for key in ('blast_radius_bounded', 'protected_non_targets_bounded')))
    defensive_cost_fields = ('further_serialization_complexity_cost_material', 'further_serialization_coupling_cost_material', 'further_serialization_delay_cost_material', 'further_serialization_latent_failure_cost_material')
    defensive_cost_basis = sorted((key for key in defensive_cost_fields if information[key] is True))
    information_value = bool(defensive_cost_basis) and all((information[key] is True for key in ('delay_cost_material', 'decision_relevant', 'live_fidelity_higher_than_simulation', 'diagnostic_information_value_material')))
    actual_reasons = {'HARD_PREREQUISITE': relationships['hard_prerequisite'], 'SHARED_WRITER_OR_RESOURCE': relationships['writer_or_resource_exclusion'], 'CURRENTNESS_OR_IDENTITY': not currentness['current'] or not candidate['identity_frozen'], 'IRREVERSIBLE_EFFECT_PRECONDITION': not safe_shape or not effect_protected or (not impact_bounded), 'CONSEQUENCE_CONTROL': diagnostic['consequence_critical'] or (relationships['acceptance_prerequisite'] and (not information_value)), 'HOST_CAPACITY_OR_EXCLUSION': not capacity['available'] or capacity['host_exclusion']}
    workflow_reason = request['workflow_serialization_reason']
    if workflow_reason is not None and type(workflow_reason) is not str:
        raise WorkGraphError(f'{path}.workflow_serialization_reason: string or null required')
    pseudo = workflow_reason is not None and (workflow_reason not in PROXIMAL_SERIALIZATION_REASONS or actual_reasons.get(str(workflow_reason)) is not True)
    if pseudo:
        mode, reason, lanes = ('STOP_RECONCILE', 'WORKFLOW_PSEUDO_DEPENDENCY', [])
    elif actual_reasons['CURRENTNESS_OR_IDENTITY']:
        mode, reason, lanes = ('STOP_RECONCILE', 'CURRENTNESS_OR_IDENTITY', [])
    elif not gate['passed']:
        mode, reason, lanes = ('STOP_RECONCILE', 'MINIMUM_RECOVERABILITY_GATE', [])
    elif not containment:
        mode, reason, lanes = ('STOP_RECONCILE', 'RESILIENCE_EVIDENCE_OR_CONTAINMENT', [])
    elif not safe_shape or not effect_protected or (not impact_bounded):
        mode, reason, lanes = ('FULL_PREFLIGHT', 'IRREVERSIBLE_EFFECT_PRECONDITION', ['ACCEPTANCE'])
    elif diagnostic['consequence_critical']:
        mode, reason, lanes = ('FULL_PREFLIGHT', 'CONSEQUENCE_CONTROL', ['ACCEPTANCE'])
    elif relationships['hard_prerequisite']:
        mode, reason, lanes = ('SERIAL_EXECUTION', 'HARD_PREREQUISITE', ['ACCEPTANCE'])
    elif relationships['writer_or_resource_exclusion']:
        mode, reason, lanes = ('SERIAL_EXECUTION', 'SHARED_WRITER_OR_RESOURCE', ['ACCEPTANCE'])
    elif not capacity['available'] or capacity['host_exclusion']:
        mode, reason, lanes = ('SERIAL_EXECUTION', 'HOST_CAPACITY_OR_EXCLUSION', ['ACCEPTANCE'])
    elif relationships['acceptance_prerequisite'] and relationships['informational_or_differential'] and information_value:
        mode, reason, lanes = ('DIAGNOSTIC_PARALLEL_ACCEPTANCE', 'RISK_OF_DELAY_AND_INFORMATIONAL_DIFFERENTIAL', ['ACCEPTANCE', 'DIAGNOSTIC'])
    elif relationships['acceptance_prerequisite'] and information_value:
        mode, reason, lanes = ('DIAGNOSTIC_PARALLEL_ACCEPTANCE', 'RISK_OF_DELAY_AND_VALUE_OF_INFORMATION', ['ACCEPTANCE', 'DIAGNOSTIC'])
    elif relationships['acceptance_prerequisite']:
        mode, reason, lanes = ('SERIAL_EXECUTION', 'CONSEQUENCE_CONTROL', ['ACCEPTANCE', 'DIAGNOSTIC'])
    elif relationships['informational_or_differential']:
        mode, reason, lanes = ('ORDINARY_PARALLEL', 'INFORMATIONAL_DIFFERENTIAL', ['ACCEPTANCE', 'DIAGNOSTIC'])
    else:
        mode, reason, lanes = ('ORDINARY_PARALLEL', 'INDEPENDENT', ['ACCEPTANCE', 'DIAGNOSTIC'])
    strategy = {'FULL_PREFLIGHT': 'PREVENTION_FULL_PREFLIGHT', 'DIAGNOSTIC_PARALLEL_ACCEPTANCE': 'EARLY_DETECTION_ACTIVE_DEFENSE', 'ORDINARY_PARALLEL': 'ORDINARY_PARALLEL', 'SERIAL_EXECUTION': 'PREVENTION_FULL_PREFLIGHT', 'STOP_RECONCILE': 'STOP_RECONCILE'}[mode]
    if mode == 'SERIAL_EXECUTION' and reason == 'CONSEQUENCE_CONTROL':
        strategy = 'CONTAIN_AND_RECOVER'
    return _proximal_digest_v1({'schema': 'implementaudit.proximal-scheduling-projection.v1', 'request_sha256': hashlib.sha256(request_bytes).hexdigest(), 'candidate': candidate, 'currentness': currentness, 'minimum_recoverability_gate': gate, 'resilience_evidence_sha256': resilience['evidence_sha256'], 'proportionality': information, 'defensive_cost_basis': defensive_cost_basis, 'mode': mode, 'reason': reason, 'safety_strategy': strategy, 'lanes': lanes, 'authority': _proximal_no_authority_v1()})

def _proximal_projection_v1(projection_bytes: bytes) -> dict[str, JSONValue]:
    path = 'proximal scheduling projection'
    fields = {'schema', 'request_sha256', 'candidate', 'currentness', 'minimum_recoverability_gate', 'resilience_evidence_sha256', 'proportionality', 'defensive_cost_basis', 'mode', 'reason', 'safety_strategy', 'lanes', 'authority', 'digest'}
    result = _proximal_object_v1(decode_strict_json_bytes(projection_bytes, path), path, fields, digests={'request_sha256', 'resilience_evidence_sha256', 'digest'})
    if result['schema'] != 'implementaudit.proximal-scheduling-projection.v1':
        raise WorkGraphError(f'{path}: unsupported schema')
    _proximal_candidate_v1(result['candidate'], f'{path}.candidate')
    _proximal_currentness_v1(result['currentness'], f'{path}.currentness')
    if result['authority'] != _proximal_no_authority_v1():
        raise WorkGraphError(f'{path}: diagnostic authority is forbidden')
    mode = _require_string(result['mode'], f'{path}.mode')
    reason = _require_string(result['reason'], f'{path}.reason')
    strategy = _require_string(result['safety_strategy'], f'{path}.safety_strategy')
    if mode not in {'FULL_PREFLIGHT', 'DIAGNOSTIC_PARALLEL_ACCEPTANCE', 'ORDINARY_PARALLEL', 'SERIAL_EXECUTION', 'STOP_RECONCILE'}:
        raise WorkGraphError(f'{path}: unknown mode')
    lanes = _require_string_array(result['lanes'], f'{path}.lanes')
    defensive_cost_basis = _require_string_array(result['defensive_cost_basis'], f'{path}.defensive_cost_basis')
    allowed_costs = {'further_serialization_complexity_cost_material', 'further_serialization_coupling_cost_material', 'further_serialization_delay_cost_material', 'further_serialization_latent_failure_cost_material'}
    if defensive_cost_basis != sorted(defensive_cost_basis) or not set(defensive_cost_basis) <= allowed_costs:
        raise WorkGraphError(f'{path}.defensive_cost_basis: invalid cost basis')
    valid_reasons = {'FULL_PREFLIGHT': {'IRREVERSIBLE_EFFECT_PRECONDITION', 'CONSEQUENCE_CONTROL'}, 'DIAGNOSTIC_PARALLEL_ACCEPTANCE': {'RISK_OF_DELAY_AND_VALUE_OF_INFORMATION', 'RISK_OF_DELAY_AND_INFORMATIONAL_DIFFERENTIAL'}, 'ORDINARY_PARALLEL': {'INDEPENDENT', 'INFORMATIONAL_DIFFERENTIAL'}, 'SERIAL_EXECUTION': {'HARD_PREREQUISITE', 'SHARED_WRITER_OR_RESOURCE', 'HOST_CAPACITY_OR_EXCLUSION', 'CONSEQUENCE_CONTROL'}, 'STOP_RECONCILE': {'WORKFLOW_PSEUDO_DEPENDENCY', 'CURRENTNESS_OR_IDENTITY', 'MINIMUM_RECOVERABILITY_GATE', 'RESILIENCE_EVIDENCE_OR_CONTAINMENT'}}
    expected_strategy = {'FULL_PREFLIGHT': 'PREVENTION_FULL_PREFLIGHT', 'DIAGNOSTIC_PARALLEL_ACCEPTANCE': 'EARLY_DETECTION_ACTIVE_DEFENSE', 'ORDINARY_PARALLEL': 'ORDINARY_PARALLEL', 'SERIAL_EXECUTION': 'CONTAIN_AND_RECOVER' if reason == 'CONSEQUENCE_CONTROL' else 'PREVENTION_FULL_PREFLIGHT', 'STOP_RECONCILE': 'STOP_RECONCILE'}[mode]
    expected_lanes = {'FULL_PREFLIGHT': ['ACCEPTANCE'], 'DIAGNOSTIC_PARALLEL_ACCEPTANCE': ['ACCEPTANCE', 'DIAGNOSTIC'], 'ORDINARY_PARALLEL': ['ACCEPTANCE', 'DIAGNOSTIC'], 'SERIAL_EXECUTION': ['ACCEPTANCE', 'DIAGNOSTIC'] if reason == 'CONSEQUENCE_CONTROL' else ['ACCEPTANCE'], 'STOP_RECONCILE': []}[mode]
    if reason not in valid_reasons[mode] or strategy != expected_strategy or lanes != expected_lanes:
        raise WorkGraphError(f'{path}: mode/reason/strategy/lanes mismatch')
    unsigned = dict(result)
    digest = str(unsigned.pop('digest'))
    if not hmac.compare_digest(digest, hashlib.sha256(canonical_json_v1(unsigned)).hexdigest()):
        raise WorkGraphError(f'{path}: stale digest')
    return result

def _proximal_action_context_v1(context_bytes: bytes) -> dict[str, JSONValue]:
    path = 'proximal action-selection context'
    result = _proximal_object_v1(decode_strict_json_bytes(context_bytes, path), path, {'schema', 'currentness', 'action_population', 'qualification'})
    if result['schema'] != 'implementaudit.proximal-action-selection-context.v1':
        raise WorkGraphError(f'{path}: unsupported schema')
    currentness = _proximal_currentness_v1(result['currentness'], f'{path}.currentness')
    population = _proximal_object_v1(result['action_population'], f'{path}.action_population', {'target_action_sha256', 'actions'}, digests={'target_action_sha256'})
    raw_actions = population['actions']
    if type(raw_actions) is not list or not raw_actions or len(raw_actions) > 64:
        raise WorkGraphError(f'{path}.action_population.actions: bounded non-empty array required')
    actions: list[dict[str, JSONValue]] = []
    allowed_effects = {'BOUNDED_CORRECTION', 'COMPONENT_ACCEPTANCE', 'INSTALL_CUTOVER', 'IRREVERSIBLE_HIGH_CONSEQUENCE_AUTHORITY_TRANSFER'}
    for index, item in enumerate(raw_actions):
        action_path = f'{path}.action_population.actions[{index}]'
        action = _proximal_object_v1(item, action_path, {'action_sha256', 'effect_class'}, digests={'action_sha256'})
        effect = _require_string(action['effect_class'], f'{action_path}.effect_class')
        if effect not in allowed_effects:
            raise WorkGraphError(f'{action_path}.effect_class: unknown effect')
        actions.append(action)
    identities = [str(action['action_sha256']) for action in actions]
    if identities != sorted(set(identities)):
        raise WorkGraphError(f'{path}.action_population.actions: canonical unique order required')
    target = str(population['target_action_sha256'])
    if target not in identities:
        raise WorkGraphError(f'{path}.action_population.target_action_sha256: unknown action')
    target_effect = str(actions[identities.index(target)]['effect_class'])
    applicable = len(actions) >= 2
    applicability_reason = 'BOUNDED_ACTION_PAIR_PRESENT' if applicable else 'FEWER_THAN_TWO_BOUNDED_ACTIONS'
    if applicable:
        if result['qualification'] is None:
            raise WorkGraphError(f'{path}: applicable decision requires qualification')
        qualification = _proximal_qualification_request_v1(result['qualification'], f'{path}.qualification')
        if qualification['next_effect'] != target_effect:
            raise WorkGraphError(f'{path}: target action effect and qualification effect disagree')
    elif result['qualification'] is not None:
        raise WorkGraphError(f'{path}: NOT_REQUIRED cannot carry qualification')
    canonical_input = {'schema': result['schema'], 'currentness': currentness, 'action_population': {**population, 'actions': actions}, 'qualification': result['qualification']}
    return {**canonical_input, 'decision_sha256': hashlib.sha256(canonical_json_v1(canonical_input)).hexdigest(), 'applicable': applicable, 'applicability_reason': applicability_reason, 'target_effect_class': target_effect}

def _rederive_proximal_projection_v1(request_bytes: bytes, projection_bytes: bytes) -> dict[str, JSONValue]:
    expected = compile_proximal_schedule_v1(request_bytes)
    projection = _proximal_projection_v1(projection_bytes)
    if not hmac.compare_digest(canonical_json_v1(expected), canonical_json_v1(projection)):
        raise WorkGraphError('proximal scheduling projection: request/projection mismatch')
    return projection

def _proximal_evidence_applicability_v1(value: JSONValue, path: str) -> dict[str, JSONValue]:
    digest_fields = {'tested_product_input_sha256', 'source_dependency_slice_sha256', 'test_fixture_sha256', 'toolchain_environment_sha256', 'acceptance_contract_sha256'}
    result = _proximal_object_v1(value, path, digest_fields | {'authority_effect_class'}, digests=digest_fields)
    authority_effect_class = _require_string(result['authority_effect_class'], f'{path}.authority_effect_class')
    if authority_effect_class not in {'BOUNDED_CORRECTION', 'COMPONENT_ACCEPTANCE', 'INSTALL_CUTOVER', 'IRREVERSIBLE_HIGH_CONSEQUENCE_AUTHORITY_TRANSFER'}:
        raise WorkGraphError(f'{path}.authority_effect_class: unknown class')
    return result

def _proximal_qualification_request_v1(value: JSONValue, path: str) -> dict[str, JSONValue]:
    result = _proximal_object_v1(value, path, {'change_set_sha256', 'source_dependency_slice_sha256', 'affected_contracts', 'applicability', 'prior_evidence', 'semantic_invalidation_radius', 'next_effect', 'reversible', 'blast_radius_bounded', 'object_class', 'meaningful_join', 'workflow_requested_qualification', 'preparation'}, booleans={'reversible', 'blast_radius_bounded'}, digests={'change_set_sha256', 'source_dependency_slice_sha256'})
    contracts = _require_string_array(result['affected_contracts'], f'{path}.affected_contracts')
    if not contracts or contracts != sorted(set(contracts)):
        raise WorkGraphError(f'{path}.affected_contracts: sorted unique population required')
    applicability = _proximal_evidence_applicability_v1(result['applicability'], f'{path}.applicability')
    prior_value = result['prior_evidence']
    if type(prior_value) is not list:
        raise WorkGraphError(f'{path}.prior_evidence: array required')
    prior_evidence: list[dict[str, JSONValue]] = []
    seen: set[str] = set()
    for index, item in enumerate(prior_value):
        evidence_path = f'{path}.prior_evidence[{index}]'
        evidence = _proximal_object_v1(item, evidence_path, {'evidence_sha256', 'scope', 'applicability'}, digests={'evidence_sha256'})
        evidence_sha = str(evidence['evidence_sha256'])
        scope = _require_string(evidence['scope'], f'{evidence_path}.scope')
        if scope not in {'CAUSAL_ADVERSARIAL_SLICE', 'COMPONENT_ACCEPTANCE', 'WHOLE_PROJECTION_CUTOVER'}:
            raise WorkGraphError(f'{evidence_path}.scope: unknown scope')
        _proximal_evidence_applicability_v1(evidence['applicability'], f'{evidence_path}.applicability')
        if evidence_sha in seen:
            raise WorkGraphError(f'{path}.prior_evidence: duplicate evidence identity')
        seen.add(evidence_sha)
        prior_evidence.append(evidence)
    if [str(item['evidence_sha256']) for item in prior_evidence] != sorted(seen):
        raise WorkGraphError(f'{path}.prior_evidence: canonical evidence order required')
    radius = _require_string(result['semantic_invalidation_radius'], f'{path}.semantic_invalidation_radius')
    if radius not in {'NONE', 'LOCAL_SAME_OWNER_SLICE', 'SHARED_CURRENTNESS_AUTHORITY_SUBSTRATE', 'WHOLE_PROJECTION', 'UNKNOWN'}:
        raise WorkGraphError(f'{path}.semantic_invalidation_radius: unknown radius')
    next_effect = _require_string(result['next_effect'], f'{path}.next_effect')
    if next_effect not in {'BOUNDED_CORRECTION', 'COMPONENT_ACCEPTANCE', 'INSTALL_CUTOVER', 'IRREVERSIBLE_HIGH_CONSEQUENCE_AUTHORITY_TRANSFER'}:
        raise WorkGraphError(f'{path}.next_effect: unknown effect')
    if result['source_dependency_slice_sha256'] != applicability['source_dependency_slice_sha256']:
        raise WorkGraphError(f'{path}: source/dependency slice copies disagree')
    if next_effect != applicability['authority_effect_class']:
        raise WorkGraphError(f'{path}: next effect and authority/effect class disagree')
    object_class = _require_string(result['object_class'], f'{path}.object_class')
    if object_class not in {'INTERMEDIATE_COMPONENT', 'MEANINGFUL_JOIN_FROZEN_PROJECTION'}:
        raise WorkGraphError(f'{path}.object_class: unknown class')
    join = _proximal_object_v1(result['meaningful_join'], f'{path}.meaningful_join', {'proximity', 'available'}, booleans={'available'})
    proximity = _require_string(join['proximity'], f'{path}.meaningful_join.proximity')
    if proximity not in {'ABSENT', 'FUTURE', 'PROXIMAL', 'AVAILABLE'}:
        raise WorkGraphError(f'{path}.meaningful_join.proximity: unknown proximity')
    if (proximity == 'AVAILABLE') is not (join['available'] is True):
        raise WorkGraphError(f'{path}.meaningful_join: availability mismatch')
    preparation = _proximal_object_v1(result['preparation'], f'{path}.preparation', {'exact_input_identity_frozen', 'exact_input_long_gate_requested', 'whole_review_preparation_requested', 'final_whole_identity_frozen', 'consuming_join_available', 'prepared_artifact'}, booleans={'exact_input_identity_frozen', 'exact_input_long_gate_requested', 'whole_review_preparation_requested', 'final_whole_identity_frozen', 'consuming_join_available'})
    prepared_fields = {'contains_review_conclusion', 'preselects_independent_reviewer', 'guesses_final_identity', 'uses_mock_as_final', 'irreversible_or_public_effect', 'information_value_material'}
    prepared = _proximal_object_v1(preparation['prepared_artifact'], f'{path}.preparation.prepared_artifact', prepared_fields, booleans=prepared_fields)
    if preparation['consuming_join_available'] is not join['available']:
        raise WorkGraphError(f'{path}: preparation/consuming JOIN availability mismatch')
    expected_final_identity = object_class == 'MEANINGFUL_JOIN_FROZEN_PROJECTION' and join['available'] is True
    if preparation['final_whole_identity_frozen'] is not expected_final_identity:
        raise WorkGraphError(f'{path}: final whole identity state is contradictory')
    forbidden_preparation = {'contains_review_conclusion', 'preselects_independent_reviewer', 'guesses_final_identity', 'uses_mock_as_final', 'irreversible_or_public_effect'}
    if any((prepared[field] is True for field in forbidden_preparation)):
        raise WorkGraphError(f'{path}: unsafe or prejudging review preparation')
    if preparation['whole_review_preparation_requested'] is True and prepared['information_value_material'] is not True:
        raise WorkGraphError(f'{path}: review preparation lacks proportional value')
    if preparation['exact_input_long_gate_requested'] is True and preparation['exact_input_identity_frozen'] is not True:
        raise WorkGraphError(f'{path}: exact-input gate lacks a frozen identity')
    if preparation['final_whole_identity_frozen'] is True and preparation['exact_input_identity_frozen'] is not True:
        raise WorkGraphError(f'{path}: final whole identity is not an exact frozen input')
    requested = result['workflow_requested_qualification']
    if requested is not None:
        requested = _require_string(requested, f'{path}.workflow_requested_qualification')
        if requested not in {'CORRECTION_QUALIFICATION', 'COMPONENT_ACCEPTANCE', 'WHOLE_PROJECTION_CUTOVER_QUALIFICATION'}:
            raise WorkGraphError(f'{path}.workflow_requested_qualification: unknown mode')
    result['applicability'] = applicability
    result['prior_evidence'] = prior_evidence
    preparation['prepared_artifact'] = prepared
    result['preparation'] = preparation
    return result

def _proximal_evidence_dispositions_v1(prior: list[dict[str, JSONValue]], current: dict[str, JSONValue]) -> list[dict[str, JSONValue]]:
    """Revalidate buffered evidence without turning it into authority."""
    fields = ['tested_product_input_sha256', 'source_dependency_slice_sha256', 'test_fixture_sha256', 'toolchain_environment_sha256', 'acceptance_contract_sha256', 'authority_effect_class']
    dispositions: list[dict[str, JSONValue]] = []
    for item in prior:
        previous = item['applicability']
        changed = sorted((field for field in fields if previous[field] != current[field]))
        if not changed:
            disposition, reason = ('REUSE', 'EXACT_APPLICABILITY_TUPLE_UNCHANGED')
        elif set(changed) <= {'source_dependency_slice_sha256', 'test_fixture_sha256', 'toolchain_environment_sha256'} and all((previous[field] == current[field] for field in ('tested_product_input_sha256', 'acceptance_contract_sha256', 'authority_effect_class'))):
            disposition, reason = ('PARTIAL_RERUN', 'DEPENDENT_APPLICABILITY_SLICE_CHANGED')
        else:
            disposition, reason = ('DISCARD', 'EVIDENCE_APPLICABILITY_CHANGED')
        dispositions.append({'evidence_sha256': item['evidence_sha256'], 'scope': item['scope'], 'disposition': disposition, 'reason': reason, 'changed_fields': changed, 'authority': _proximal_no_authority_v1()})
    return dispositions

def _proximal_preparation_frontier_v1(request: dict[str, JSONValue]) -> dict[str, JSONValue]:
    preparation = request['preparation']
    states: list[str] = []
    if preparation['exact_input_identity_frozen'] is True and preparation['exact_input_long_gate_requested'] is True:
        states.append('EXACT_INPUT_EVIDENCE_RUNNABLE_NOW')
    if preparation['whole_review_preparation_requested'] is True:
        states.append('WHOLE_REVIEW_PREPARATION_RUNNABLE_NOW')
    if preparation['final_whole_identity_frozen'] is not True:
        states.append('FINAL_WHOLE_IDENTITY_BLOCKED')
    if request['prior_evidence'] and preparation['consuming_join_available'] is not True:
        states.append('EVIDENCE_AVAILABLE_NOT_CONSUMABLE')
    return {'states': sorted(states), 'authority': _proximal_no_authority_v1(), 'reason': 'SAFE_PREPARATION_BEFORE_CONSUMING_JOIN' if preparation['consuming_join_available'] is not True else 'CONSUMING_JOIN_AVAILABLE_FOR_FRESH_APPLICABILITY_CHECK'}

def derive_proximal_qualification_v1(value: JSONValue, path: str='proximal qualification') -> dict[str, JSONValue]:
    """Derive exact evidence depth for the next action, never lifecycle credit."""
    request = _proximal_qualification_request_v1(value, path)
    applicability = request['applicability']
    prior = request['prior_evidence']
    dispositions = _proximal_evidence_dispositions_v1(prior, applicability)
    retained = sorted((str(item['evidence_sha256']) for item in dispositions if item['disposition'] == 'REUSE'))
    invalidated = sorted((str(item['evidence_sha256']) for item in dispositions if item['disposition'] == 'DISCARD'))
    partial_rerun = sorted((str(item['evidence_sha256']) for item in dispositions if item['disposition'] == 'PARTIAL_RERUN'))
    retained_scopes = {str(item['scope']) for item in prior if item['applicability'] == applicability}
    radius = str(request['semantic_invalidation_radius'])
    next_effect = str(request['next_effect'])
    object_class = str(request['object_class'])
    join = request['meaningful_join']
    broad_reason: JSONValue = None
    reuse_reason: JSONValue = None
    if radius == 'UNKNOWN':
        mode, reason, required = ('STOP_RECONCILE', 'UNKNOWN_SEMANTIC_INVALIDATION_RADIUS', [])
    elif next_effect == 'INSTALL_CUTOVER' and (object_class != 'MEANINGFUL_JOIN_FROZEN_PROJECTION' or join['available'] is not True):
        mode, reason, required = ('STOP_RECONCILE', 'CUTOVER_JOIN_OR_FREEZE_NOT_ESTABLISHED', [])
    elif next_effect in {'INSTALL_CUTOVER', 'IRREVERSIBLE_HIGH_CONSEQUENCE_AUTHORITY_TRANSFER'} or radius == 'WHOLE_PROJECTION':
        mode, reason = ('WHOLE_PROJECTION_CUTOVER_QUALIFICATION', 'CUTOVER_FULL_PREFLIGHT')
        required = ['CUTOVER_PREFLIGHT']
        if 'WHOLE_PROJECTION_CUTOVER' not in retained_scopes:
            required.append('WHOLE_PROJECTION_REVIEW')
        required.sort()
        broad_reason = 'WHOLE_PROJECTION_OR_CUTOVER_AUTHORITY'
    elif request['reversible'] is not True or request['blast_radius_bounded'] is not True:
        mode, reason, required = ('STOP_RECONCILE', 'EFFECT_RECOVERY_OR_BLAST_RADIUS_UNPROVED', [])
    elif radius == 'SHARED_CURRENTNESS_AUTHORITY_SUBSTRATE':
        mode, reason = ('COMPONENT_ACCEPTANCE', 'SHARED_SUBSTRATE_DEPENDENCY_INVALIDATION')
        required = ['DEPENDENCY_SLICE_REQUALIFICATION', 'FRESH_COMPONENT_REVIEW']
        broad_reason = 'SHARED_CURRENTNESS_AUTHORITY_SUBSTRATE'
    elif radius == 'LOCAL_SAME_OWNER_SLICE':
        mode, reason = ('CORRECTION_QUALIFICATION', 'LOCAL_SAME_OWNER_SELECTIVE_INVALIDATION')
        required = ['AFFECTED_CAUSAL_ADVERSARIAL_SLICE', 'FRESH_COMPONENT_REVIEW']
    elif object_class == 'INTERMEDIATE_COMPONENT' and join['available'] is True and ('COMPONENT_ACCEPTANCE' in retained_scopes):
        mode, reason, required = ('COMPONENT_ACCEPTANCE', 'INTERMEDIATE_COMPONENT_TO_AVAILABLE_JOIN', ['JOIN_COMPOSITION_EVIDENCE'])
        reuse_reason = 'EXACT_APPLICABILITY_TUPLE_UNCHANGED'
    elif retained:
        if next_effect == 'COMPONENT_ACCEPTANCE':
            mode, reason = ('COMPONENT_ACCEPTANCE', 'UNCHANGED_APPLICABILITY_TUPLE_REUSE')
            required = [] if 'COMPONENT_ACCEPTANCE' in retained_scopes else ['FRESH_COMPONENT_REVIEW']
        else:
            mode, reason, required = ('CORRECTION_QUALIFICATION', 'UNCHANGED_APPLICABILITY_TUPLE_REUSE', [])
        reuse_reason = 'EXACT_APPLICABILITY_TUPLE_UNCHANGED'
    else:
        mode, reason, required = ('STOP_RECONCILE', 'NO_CURRENT_APPLICABLE_EVIDENCE_OR_INVALIDATION', [])
    requested = request['workflow_requested_qualification']
    if mode != 'STOP_RECONCILE' and requested is not None and (requested != mode):
        mode, reason, required = ('STOP_RECONCILE', 'WORKFLOW_QUALIFICATION_PSEUDO_DEPENDENCY', [])
        broad_reason = None
        reuse_reason = None
    return {'change_set_sha256': request['change_set_sha256'], 'source_dependency_slice_sha256': request['source_dependency_slice_sha256'], 'affected_contracts': request['affected_contracts'], 'applicability_sha256': hashlib.sha256(canonical_json_v1(applicability)).hexdigest(), 'semantic_invalidation_radius': radius, 'next_effect': next_effect, 'object_class': object_class, 'meaningful_join': join, 'mode': mode, 'reason': reason, 'required_evidence': required, 'retained_evidence_sha256': retained, 'invalidated_evidence_sha256': invalidated, 'partial_rerun_evidence_sha256': partial_rerun, 'evidence_dispositions': dispositions, 'preparation_frontier': _proximal_preparation_frontier_v1(request), 'authority': _proximal_no_authority_v1(), 'broad_rerun_reason': broad_reason, 'reuse_reason': reuse_reason}

def issue_proximal_advance_v1(context_bytes: bytes, request_bytes: bytes, projection_bytes: bytes) -> dict[str, JSONValue]:
    """Issue one no-lifecycle-authority token for an immediate decision."""
    context = _proximal_action_context_v1(context_bytes)
    if not context['applicable']:
        raise WorkGraphError('proximal advance: classification is not applicable')
    qualification = derive_proximal_qualification_v1(context['qualification'], 'proximal action-selection context.qualification')
    if qualification['mode'] == 'STOP_RECONCILE':
        raise WorkGraphError(f"proximal advance: qualification STOP_RECONCILE:{qualification['reason']} forbids continuation")
    projection = _rederive_proximal_projection_v1(request_bytes, projection_bytes)
    if context['currentness'] != projection['currentness']:
        raise WorkGraphError('proximal advance: context/projection currentness mismatch')
    if projection['mode'] == 'STOP_RECONCILE':
        raise WorkGraphError('proximal advance: STOP projection forbids continuation')
    return _proximal_digest_v1({'schema': 'implementaudit.proximal-advance-token.v1', 'scope': 'ONE_IMMEDIATE_DECISION', 'decision_sha256': context['decision_sha256'], 'applicability_reason': context['applicability_reason'], 'request_sha256': projection['request_sha256'], 'projection_digest': projection['digest'], 'candidate': projection['candidate'], 'currentness': projection['currentness'], 'minimum_recoverability_gate': projection['minimum_recoverability_gate'], 'mode': projection['mode'], 'reason': projection['reason'], 'lanes': projection['lanes'], 'qualification': qualification, 'authority': _proximal_no_authority_v1()})

def compile_proximal_action_selection_v1(context_bytes: bytes, request_bytes: bytes | None, projection_bytes: bytes | None, token_bytes: bytes | None) -> dict[str, JSONValue]:
    """Enforce the governor's transient proximal action-selection boundary."""
    context = _proximal_action_context_v1(context_bytes)
    if not context['applicable']:
        if any((value is not None for value in (request_bytes, projection_bytes, token_bytes))):
            raise WorkGraphError('proximal action selection: NOT_REQUIRED carries no classifier inputs')
        return _proximal_digest_v1({'schema': 'implementaudit.proximal-action-selection.v1', 'decision_sha256': context['decision_sha256'], 'applicable': False, 'decision': 'NOT_REQUIRED', 'applicability_reason': context['applicability_reason'], 'advance_allowed': True, 'currentness': context['currentness'], 'qualification': None, 'authority': _proximal_no_authority_v1()})
    if any((value is None for value in (request_bytes, projection_bytes, token_bytes))):
        raise WorkGraphError('proximal action selection: applicable decision requires request, classification, and advance token')
    assert request_bytes is not None
    assert projection_bytes is not None
    assert token_bytes is not None
    projection = _rederive_proximal_projection_v1(request_bytes, projection_bytes)
    expected_token = issue_proximal_advance_v1(context_bytes, request_bytes, projection_bytes)
    if not hmac.compare_digest(canonical_json_v1(expected_token), token_bytes):
        raise WorkGraphError('proximal action selection: advance token is stale, reused, or forged')
    return _proximal_digest_v1({'schema': 'implementaudit.proximal-action-selection.v1', 'decision_sha256': context['decision_sha256'], 'applicable': True, 'decision': 'PROXIMAL_CLASSIFICATION_SATISFIED', 'applicability_reason': context['applicability_reason'], 'advance_allowed': True, 'currentness': context['currentness'], 'request_sha256': projection['request_sha256'], 'projection_digest': projection['digest'], 'mode': projection['mode'], 'reason': projection['reason'], 'lanes': projection['lanes'], 'qualification': expected_token['qualification'], 'authority': _proximal_no_authority_v1()})

def _proximal_lane_v1(value: JSONValue, path: str) -> dict[str, JSONValue]:
    result = _proximal_object_v1(value, path, {'status', 'evidence_sha256'})
    status = _require_string(result['status'], f'{path}.status')
    if status not in PROXIMAL_LANE_STATUSES:
        raise WorkGraphError(f'{path}.status: invalid status')
    if status == 'PENDING':
        if result['evidence_sha256'] is not None:
            raise WorkGraphError(f'{path}: pending lane cannot carry evidence')
    else:
        _require_digest(result['evidence_sha256'], f'{path}.evidence_sha256')
    return result

def _proximal_contributors_v1(value: JSONValue, path: str) -> list[dict[str, JSONValue]]:
    if type(value) is not list:
        raise WorkGraphError(f'{path}: array required')
    allowed = {'CONTROLLER_CURRENTNESS', 'FIXTURE_COVERAGE', 'PRODUCT', 'REVIEW', 'CONTAINMENT'}
    result = []
    seen = set()
    for index, item in enumerate(value):
        contributor = _proximal_object_v1(item, f'{path}[{index}]', {'kind', 'evidence_sha256'}, digests={'evidence_sha256'})
        kind = _require_string(contributor['kind'], f'{path}[{index}].kind')
        if kind not in allowed or kind in seen:
            raise WorkGraphError(f'{path}: invalid or duplicate contributor')
        seen.add(kind)
        result.append(contributor)
    return result

def reconcile_proximal_results_v1(request_bytes: bytes, projection_bytes: bytes, results_bytes: bytes) -> dict[str, JSONValue]:
    """Reconcile distinct diagnostic/review evidence without merging authority."""
    projection = _rederive_proximal_projection_v1(request_bytes, projection_bytes)
    path = 'proximal reconciliation request'
    results = _proximal_object_v1(decode_strict_json_bytes(results_bytes, path), path, {'schema', 'candidate', 'currentness', 'diagnostic', 'acceptance', 'contributors', 'remaining_information_value_material'}, booleans={'remaining_information_value_material'})
    if results['schema'] != 'implementaudit.proximal-reconciliation-request.v1':
        raise WorkGraphError(f'{path}: unsupported schema')
    candidate = _proximal_candidate_v1(results['candidate'], f'{path}.candidate')
    currentness = _proximal_currentness_v1(results['currentness'], f'{path}.currentness')
    diagnostic = _proximal_lane_v1(results['diagnostic'], f'{path}.diagnostic')
    acceptance = _proximal_lane_v1(results['acceptance'], f'{path}.acceptance')
    admitted_lanes = set(projection['lanes'])
    if diagnostic['status'] != 'PENDING' and 'DIAGNOSTIC' not in admitted_lanes or (acceptance['status'] != 'PENDING' and 'ACCEPTANCE' not in admitted_lanes):
        raise WorkGraphError(f'{path}: evidence supplied for a non-admitted lane')
    contributors = _proximal_contributors_v1(results['contributors'], f'{path}.contributors')
    kinds = {str(item['kind']) for item in contributors}
    diagnostic_failed = diagnostic['status'] == 'FAIL'
    acceptance_failed = acceptance['status'] == 'FAIL'
    if diagnostic_failed != bool(kinds - {'REVIEW'}) or acceptance_failed != ('REVIEW' in kinds):
        raise WorkGraphError(f'{path}: lane result/contributor mismatch')
    if diagnostic['status'] == acceptance['status'] == 'PENDING':
        raise WorkGraphError(f'{path}: no lane evidence')
    pair = (diagnostic['status'], acceptance['status'])
    if candidate != projection['candidate']:
        disposition, andon, remaining = ('STOP_RECONCILE_STALE_IDENTITY', 'NONE', 'NONE')
    elif currentness != projection['currentness'] or not currentness['current']:
        disposition, andon, remaining = ('STOP_RECONCILE_STALE_CURRENTNESS', 'NONE', 'NONE')
    elif pair == ('PASS', 'PASS'):
        disposition, andon, remaining = ('ELIGIBLE_FOR_LATER_REQUIRED_GATES', 'NONE', 'NONE')
    elif pair == ('FAIL', 'PASS'):
        disposition, andon, remaining = ('STOP_COVERAGE_EVALUATOR_ANDON', 'COVERAGE_EVALUATOR_DISAGREEMENT', 'NONE')
    elif pair == ('PASS', 'FAIL'):
        disposition, andon, remaining = ('UNACCEPTED_CAUSAL_SUCCESS_RETAINED', 'NONE', 'NONE')
    elif pair == ('FAIL', 'FAIL'):
        disposition, andon, remaining = ('REJECT_RETAIN_BOTH_RECONCILE_CAUSALLY', 'NONE', 'NONE')
    elif pair == ('FAIL', 'PENDING'):
        disposition, andon = ('REJECT_CANDIDATE_REASSESS_ACCEPTANCE_LANE', 'NONE')
        remaining = 'CONTINUE_IF_INFORMATION_VALUE_MATERIAL' if results['remaining_information_value_material'] else 'STOP_SUPERSEDED_CLEANLY'
    elif pair == ('PENDING', 'FAIL'):
        disposition, andon = ('UNACCEPTED_REASSESS_DIAGNOSTIC_LANE', 'NONE')
        remaining = 'CONTINUE_IF_INFORMATION_VALUE_MATERIAL' if results['remaining_information_value_material'] else 'STOP_SUPERSEDED_CLEANLY'
    else:
        disposition, andon, remaining = ('WAIT_FOR_OTHER_LANE', 'NONE', 'NONE')
    return _proximal_digest_v1({'schema': 'implementaudit.proximal-reconciliation.v1', 'projection_digest': projection['digest'], 'candidate': candidate, 'currentness': currentness, 'diagnostic': diagnostic, 'acceptance': acceptance, 'contributors': contributors, 'disposition': disposition, 'andon': andon, 'remaining_lane': remaining, 'authority': _proximal_no_authority_v1()})

def compile_frontier_projection(graph_bytes: bytes, product_authority_bytes: bytes | None=None) -> dict[str, JSONValue]:
    decoded = decode_strict_json_bytes(graph_bytes, 'WORK_GRAPH.json')
    graph = _require_object(decoded, 'WORK_GRAPH.json')
    cells = _validate_graph(graph, product_authority_bytes)
    declared_total = _require_object(graph['population'], '$.population')['total_cells']
    counts = {state: sum((cell['state'] == state for cell in cells)) for state in KNOWN_STATES}
    projection: dict[str, JSONValue] = {'population': declared_total, 'counts': counts, 'active': sorted((str(cell['id']) for cell in cells if cell['state'] == 'ACTIVE')), 'ready': sorted((str(cell['id']) for cell in cells if cell['state'] == 'READY')), 'blocked_summary': summarize_blocked_v1(cells), 'writer_holds': normalize_holds_v1(graph['serialization_groups'], 'writer'), 'resource_holds': normalize_holds_v1(graph['serialization_groups'], 'resource')}
    preparation = compile_preparation_frontier_v1(graph, cells, graph_bytes)
    if preparation:
        projection['preparation_frontier'] = preparation
    products = compile_product_frontier_v1(graph, cells, product_authority_bytes)
    if products is not None:
        projection['product_frontier'] = products
    projection['digest'] = hashlib.sha256(canonical_json_v1(projection)).hexdigest()
    return projection

def compile_native_a_g_v1(request_bytes: bytes) -> dict[str, JSONValue]:
    """Compile typed dependency, invalidation, and execution-owner facts.

    This is preparation-only information.  It does not grant lifecycle or
    acceptance authority, and deliberately does not read fixture verdicts.
    """
    request = _require_object(decode_strict_json_bytes(request_bytes, 'native A/B/G request'), 'native A/B/G request')
    _require_exact_members(request, {'schema', 'dependency', 'invalidation', 'execution_owner'}, 'native A/B/G request')
    if request['schema'] != 'implementaudit.native-a-g.request.v1':
        raise WorkGraphError('native A/B/G request: unsupported schema')
    dependency = _require_object(request['dependency'], 'native dependency')
    _require_exact_members(dependency, {'cells', 'joins', 'host_capacity', 'operator_ceiling'}, 'native dependency')
    cells_value = dependency['cells']
    if type(cells_value) is not list:
        raise WorkGraphError('native dependency.cells: array required')
    host_capacity = dependency['host_capacity']
    if type(host_capacity) is not int or host_capacity < 0:
        raise WorkGraphError('native dependency.host_capacity: non-negative integer required')
    operator_ceiling = dependency['operator_ceiling']
    if type(operator_ceiling) is not int or operator_ceiling < 0:
        raise WorkGraphError('native dependency.operator_ceiling: non-negative integer required')
    cells: list[dict[str, JSONValue]] = []
    cells_by_id: dict[str, dict[str, JSONValue]] = {}
    for index, value in enumerate(cells_value):
        cell = _require_object(value, f'native dependency.cells[{index}]')
        _require_exact_members(cell, {'id', 'dependency', 'predecessors', 'writes', 'impact', 'state', 'resource_demand', 'rank', 'acceptance_boundary', 'resource_boundary', 'effect', 'authority_boundary', 'authorization_current', 'currentness_current'}, f'native dependency.cells[{index}]')
        cell_id = _require_string(cell['id'], f'native dependency.cells[{index}].id')
        if cell_id in cells_by_id:
            raise WorkGraphError(f'native dependency: duplicate cell id {cell_id}')
        dependency_type = _require_string(cell['dependency'], f'native dependency.cells[{index}].dependency')
        if dependency_type not in {'NONE', 'MAY_AFFECT', 'MUST_FINISH_BEFORE'}:
            raise WorkGraphError(f'native dependency: unknown type for {cell_id}')
        predecessors = _require_string_array(cell['predecessors'], f'native dependency.cells[{index}].predecessors')
        writes = _require_string_array(cell['writes'], f'native dependency.cells[{index}].writes')
        impact = _require_string(cell['impact'], f'native dependency.cells[{index}].impact')
        if impact not in {'KNOWN', 'UNKNOWN'}:
            raise WorkGraphError(f'native dependency: unknown impact for {cell_id}')
        state = _require_string(cell['state'], f'native dependency.cells[{index}].state')
        if state not in {'READY', 'ACTIVE', 'BLOCKED'}:
            raise WorkGraphError(f'native dependency: unknown state for {cell_id}')
        demand = cell['resource_demand']
        rank = cell['rank']
        if type(demand) is not int or demand < 0:
            raise WorkGraphError(f'native dependency: invalid demand for {cell_id}')
        if type(rank) is not int:
            raise WorkGraphError(f'native dependency: invalid rank for {cell_id}')
        for boundary in ('acceptance_boundary', 'resource_boundary', 'authority_boundary'):
            _require_string(cell[boundary], f'native dependency.cells[{index}].{boundary}')
        effect = _require_string(cell['effect'], f'native dependency.cells[{index}].effect')
        if effect not in {'REVERSIBLE', 'IRREVERSIBLE'}:
            raise WorkGraphError(f'native dependency: unknown effect for {cell_id}')
        _require_bool(cell['authorization_current'], f'native dependency.cells[{index}].authorization_current')
        _require_bool(cell['currentness_current'], f'native dependency.cells[{index}].currentness_current')
        if dependency_type == 'MUST_FINISH_BEFORE' and (not predecessors):
            raise WorkGraphError(f'native dependency: hard predecessor missing for {cell_id}')
        if dependency_type != 'MUST_FINISH_BEFORE' and predecessors:
            raise WorkGraphError(f'native dependency: non-hard predecessor supplied for {cell_id}')
        cells.append(cell)
        cells_by_id[cell_id] = cell
    for cell in cells:
        for predecessor in cell['predecessors']:
            if predecessor not in cells_by_id:
                raise WorkGraphError(f'native dependency: unknown predecessor {predecessor}')
    joins_value = dependency['joins']
    if type(joins_value) is not list:
        raise WorkGraphError('native dependency.joins: array required')
    joins: list[dict[str, JSONValue]] = []
    join_ids: set[str] = set()
    for index, value in enumerate(joins_value):
        join = _require_object(value, f'native dependency.joins[{index}]')
        _require_exact_members(join, {'id', 'requires'}, f'native dependency.joins[{index}]')
        join_id = _require_string(join['id'], f'native dependency.joins[{index}].id')
        if join_id in join_ids:
            raise WorkGraphError(f'native dependency: duplicate join id {join_id}')
        join_ids.add(join_id)
        required = _require_string_array(join['requires'], f'native dependency.joins[{index}].requires')
        if not required or any((cell_id not in cells_by_id for cell_id in required)):
            raise WorkGraphError(f'native dependency: join {join_id} has unknown or empty requirements')
        joins.append(join)
    if len(joins) != 1:
        raise WorkGraphError('native dependency: exactly one governed join required')
    execution_predecessors = [{'id': cell['id'], 'requires': sorted(cell['predecessors'])} for cell in cells if cell['dependency'] == 'MUST_FINISH_BEFORE']
    learning_ready = sorted((str(cell['id']) for cell in cells if cell['impact'] == 'KNOWN' and cell['dependency'] != 'MUST_FINISH_BEFORE'))
    dependency_blocked = sorted((str(cell['id']) for cell in cells if cell['impact'] == 'UNKNOWN'))
    writers: dict[str, list[str]] = {}
    for cell in cells:
        for path in cell['writes']:
            writers.setdefault(str(path), []).append(str(cell['id']))
    serialization_groups = {f'W_{path}': sorted(members) for path, members in sorted(writers.items()) if len(members) > 1}

    def boundary_groups(field: str, prefix: str) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for cell in cells:
            boundary = str(cell[field])
            if boundary != 'NONE':
                groups.setdefault(f'{prefix}_{boundary}', []).append(str(cell['id']))
        return {group: sorted(members) for group, members in sorted(groups.items())}
    acceptance_groups = boundary_groups('acceptance_boundary', 'A')
    resource_groups = boundary_groups('resource_boundary', 'R')
    authority_groups = boundary_groups('authority_boundary', 'AUTH')
    irreversible_groups = {'I_irreversible': sorted((str(cell['id']) for cell in cells if cell['effect'] == 'IRREVERSIBLE'))}
    if not irreversible_groups['I_irreversible']:
        irreversible_groups = {}
    capacity = min(host_capacity, operator_ceiling)
    active_occupancy = sum((int(cell['resource_demand']) for cell in cells if cell['state'] == 'ACTIVE'))
    free_capacity = max(0, capacity - active_occupancy)
    schedule_blocked: set[str] = set(dependency_blocked)
    candidates: list[dict[str, JSONValue]] = []
    for cell in cells:
        cell_id = str(cell['id'])
        if cell['state'] != 'READY':
            if cell['state'] == 'BLOCKED':
                schedule_blocked.add(cell_id)
            continue
        if cell['impact'] == 'UNKNOWN' or not cell['authorization_current'] or (not cell['currentness_current']) or (cell['effect'] == 'IRREVERSIBLE') or (cell['acceptance_boundary'] != 'NONE') or (cell['authority_boundary'] != 'NONE'):
            schedule_blocked.add(cell_id)
            continue
        if cell['dependency'] == 'MUST_FINISH_BEFORE':
            continue
        candidates.append(cell)
    selected, deferred_reasons, active_occupancy, free_capacity = _bounded_selection_v1(candidates, [cell for cell in cells if cell['state'] == 'ACTIVE'], capacity)
    deferred = list(deferred_reasons)
    dependency_projection: dict[str, JSONValue] = {'execution_predecessors': execution_predecessors, 'learning_ready': learning_ready, 'blocked': dependency_blocked, 'serialization_groups': serialization_groups, 'resource_queue': host_capacity < len(learning_ready), 'join': {'id': joins[0]['id'], 'required': True, 'authority': 'SOLE_GOVERNOR'}}
    conflict_projection: dict[str, JSONValue] = {'write': serialization_groups, 'acceptance': acceptance_groups, 'resource': resource_groups, 'irreversible_effect': irreversible_groups, 'authority': authority_groups}
    schedule_projection: dict[str, JSONValue] = {'capacity': capacity, 'active_occupancy': active_occupancy, 'free_capacity': free_capacity, 'selected': selected, 'deferred': sorted(deferred), 'blocked': sorted(schedule_blocked), 'lifecycle_credit': 'NONE', 'acceptance_credit': 'NONE', 'authority': 'SOLE_GOVERNOR'}
    invalidation = _require_object(request['invalidation'], 'native invalidation')
    _require_exact_members(invalidation, {'changed_paths', 'change_kind', 'consumers'}, 'native invalidation')
    changed_paths = set(_require_string_array(invalidation['changed_paths'], 'native invalidation.changed_paths'))
    if not changed_paths:
        raise WorkGraphError('native invalidation: changed paths required')
    change_kind = _require_string(invalidation['change_kind'], 'native invalidation.change_kind')
    if change_kind not in {'SOURCE', 'PACKAGE_MEMBERSHIP', 'HARNESS'}:
        raise WorkGraphError('native invalidation: unknown change kind')
    consumers_value = invalidation['consumers']
    if type(consumers_value) is not list:
        raise WorkGraphError('native invalidation.consumers: array required')
    invalidated: list[str] = []
    preserved: list[str] = []
    invalidation_blocked: list[str] = []
    consumer_ids: set[str] = set()
    for index, value in enumerate(consumers_value):
        consumer = _require_object(value, f'native invalidation.consumers[{index}]')
        _require_exact_members(consumer, {'id', 'kind', 'paths', 'impact'}, f'native invalidation.consumers[{index}]')
        consumer_id = _require_string(consumer['id'], f'native invalidation.consumers[{index}].id')
        if consumer_id in consumer_ids:
            raise WorkGraphError(f'native invalidation: duplicate consumer {consumer_id}')
        consumer_ids.add(consumer_id)
        kind = _require_string(consumer['kind'], f'native invalidation.consumers[{index}].kind')
        if kind not in {'SEMANTIC', 'WRITE', 'TEST', 'PACKAGE', 'INSTALL', 'HARNESS', 'REVIEW'}:
            raise WorkGraphError(f'native invalidation: unknown consumer kind {kind}')
        paths = set(_require_string_array(consumer['paths'], f'native invalidation.consumers[{index}].paths'))
        impact = _require_string(consumer['impact'], f'native invalidation.consumers[{index}].impact')
        if impact not in {'KNOWN', 'UNKNOWN'}:
            raise WorkGraphError(f'native invalidation: unknown consumer impact {consumer_id}')
        affected = bool(paths & changed_paths)
        if change_kind == 'PACKAGE_MEMBERSHIP' and kind in {'PACKAGE', 'INSTALL'}:
            affected = True
        if change_kind == 'HARNESS' and kind in {'HARNESS', 'REVIEW'}:
            affected = True
        if not affected:
            preserved.append(consumer_id)
        elif impact == 'UNKNOWN':
            invalidation_blocked.append(consumer_id)
        else:
            invalidated.append(consumer_id)
    invalidation_projection: dict[str, JSONValue] = {'invalidated': sorted(invalidated), 'preserved': sorted(preserved), 'blocked': sorted(invalidation_blocked), 'global_replay': False}
    owner_items = request['execution_owner']
    if type(owner_items) is not list or not owner_items:
        raise WorkGraphError('native execution_owner: non-empty array required')
    owner_projection: list[dict[str, JSONValue]] = []
    owner_ids: set[str] = set()
    mechanical_work = {'identity', 'hash', 'currentness', 'receipt_reconciliation'}
    for index, value in enumerate(owner_items):
        item = _require_object(value, f'native execution_owner[{index}]')
        required = {'id', 'identity_known', 'evidence_contradictory', 'substantive_cognition', 'work'}
        optional = {'specialist_holon', 'requester_role', 'requested_action'}
        if not required.issubset(item) or not set(item).issubset(required | optional):
            raise WorkGraphError(f'native execution_owner[{index}]: member mismatch')
        item_id = _require_string(item['id'], f'native execution_owner[{index}].id')
        if item_id in owner_ids:
            raise WorkGraphError(f'native execution_owner: duplicate id {item_id}')
        owner_ids.add(item_id)
        identity_known = _require_bool(item['identity_known'], f'native execution_owner[{index}].identity_known')
        contradictory = _require_bool(item['evidence_contradictory'], f'native execution_owner[{index}].evidence_contradictory')
        substantive = _require_bool(item['substantive_cognition'], f'native execution_owner[{index}].substantive_cognition')
        work = set(_require_string_array(item['work'], f'native execution_owner[{index}].work'))
        if not work:
            raise WorkGraphError(f'native execution_owner[{index}]: work required')
        if ('requester_role' in item) != ('requested_action' in item):
            raise WorkGraphError(f'native execution_owner[{index}]: paired routing fields required')
        if 'requester_role' not in item:
            raise WorkGraphError(f'native execution_owner[{index}]: routing fields required')
        requester_role = _require_string(item['requester_role'], f'native execution_owner[{index}].requester_role')
        requested_action = _require_string(item['requested_action'], f'native execution_owner[{index}].requested_action')
        if (requester_role, requested_action) not in {('GOVERNOR', 'ASSIGN'), ('CHILD', 'DISPATCH_CHILD')}:
            raise WorkGraphError(f'native execution_owner[{index}]: unknown routing pair')
        if not identity_known or contradictory:
            owner = 'BLOCK'
        elif requester_role == 'CHILD' and requested_action == 'DISPATCH_CHILD':
            owner = 'STOP_CHILD_TO_CHILD_DISPATCH'
        elif not substantive:
            owner = 'GOVERNOR_MECHANICAL' if work <= mechanical_work else 'BLOCK'
        elif 'specialist_holon' in item:
            holon = _require_string(item['specialist_holon'], f'native execution_owner[{index}].specialist_holon')
            owner = 'CHILD_SKILL:audit-andon' if holon == 'audit-andon' else 'BLOCK'
        else:
            owner = 'CHILD_TASK'
        owner_projection.append({'id': item_id, 'owner': owner, 'authority': 'SOLE_GOVERNOR'})
    return {'schema': 'implementaudit.native-a-g.projection.v1', 'dependency': dependency_projection, 'conflicts': conflict_projection, 'schedule': schedule_projection, 'invalidation': invalidation_projection, 'execution_owner': owner_projection}


# The v1 projection and native-a-g interfaces above retain their historical
# caller-fact boundary. The explicit native source and transition interfaces
# below do not silently upgrade those interfaces into native authentication.

NATIVE_FENCE = re.compile('(?m)^```implementaudit-work-graph\\r?\\n(.*?)\\r?\\n```[ \\t]*$', re.S)
NATIVE_NODE_FIELDS = {'id', 'parent', 'kind', 'state', 'requires', 'optional', 'reads', 'writes', 'acceptance', 'resources', 'authority', 'effect', 'authorization', 'independence', 'resource_demand', 'rank', 'route_scopes', 'logical_delivery', 'future_consumer', 'invalidators', 'independent_results', 'context', 'done_evidence'}

def _graph_hash(value):
    return hashlib.sha256(canonical_json_v1(value)).hexdigest()

def _seal_graph(value):
    result = copy.deepcopy(value)
    result['digest'] = _graph_hash(result)
    return result

def _check_graph_seal(value, schema):
    _require_object(value, schema)
    validate_identity_json_v1(value)
    if schema == 'implementaudit.native-work-graph.v1' and value.get('schema') == 'implementaudit.native-work-graph.v2':
        schema = 'implementaudit.native-work-graph.v2'
    if value.get('schema') != schema:
        raise WorkGraphError(f'unknown schema: expected {schema}')
    digest = value.get('digest')
    body = {key: item for key, item in value.items() if key != 'digest'}
    if not isinstance(digest, str) or digest != _graph_hash(body):
        raise WorkGraphError(f'{schema}: digest mismatch')
    if schema in {'implementaudit.native-work-graph.v1', 'implementaudit.native-work-graph.v2'}:
        documents = _require_object(value.get('source_documents'), 'native graph source documents')
        snapshot = {}
        for path, data in documents.items():
            if path not in {'STATE.md', 'ROADMAP.md'} and (not re.fullmatch('(?:plans|phases|tasks)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\\.md', path)):
                raise WorkGraphError('native graph: unsupported source document path')
            if any((part in {'.', '..'} for part in path.split('/'))) or type(data) is not str:
                raise WorkGraphError('native graph: invalid source document')
            snapshot[path] = data.encode('utf-8')
        if not {'STATE.md', 'ROADMAP.md'}.issubset(snapshot):
            raise WorkGraphError('native graph: missing source documents')
        binding = _require_object(value.get('binding'), 'native graph binding')
        _require_exact_members(binding, {'acquisition', 'controller', 'claim', 'receipt', 'epoch', 'candidate_head', 'candidate_tree', 'worktree_digest', 'continuity_helper_digest', 'source_digest', 'read_set', 'input_root_identity'}, 'native graph binding')
        if _replay_native_graph_v1(value) != value:
            raise WorkGraphError('native graph differs from source-derived projection')

def _replay_native_graph_v1(graph, completion=None):
    # This is captured-data replay only. It cannot issue a native acquisition witness.
    replay = None if 'route_scope' not in graph else _RouteScopeObservation(graph['route_scope'], _CAPTURED_ROUTE_REPLAY_KEY, receiver_binding=graph.get('receiver_binding'))
    return _compile_native_documents_v1({k: v.encode('utf-8') for k, v in graph['source_documents'].items()}, {k: v for k, v in graph['binding'].items() if k != 'source_digest'}, _route_observation=replay, _completion=completion)

def _native_strings(value, label):
    result = _require_string_array(value, label)
    if len(result) != len(set(result)):
        raise WorkGraphError(f'{label}: duplicate member')
    if any((not item.strip() or any((ord(c) < 32 for c in item)) for item in result)):
        raise WorkGraphError(f'{label}: non-empty printable strings required')
    return result

def _native_name(value, label):
    value = _require_string(value, label)
    if not value.strip() or any((ord(c) < 32 for c in value)):
        raise WorkGraphError(f'{label}: non-empty printable string required')
    return value

def _native_int(value, label, minimum=0):
    if type(value) is not int or not minimum <= value <= INT64_MAX:
        raise WorkGraphError(f'{label}: bounded integer >= {minimum} required')
    return value

def _native_enum(value, choices, label):
    if type(value) is not str or value not in choices:
        raise WorkGraphError(f'{label}: unknown token')
    return value

def _native_document(data, path, schema):
    try:
        text = data.decode('utf-8', 'strict')
    except UnicodeDecodeError as exc:
        raise WorkGraphError(f'{path}: invalid UTF-8') from exc
    matches = NATIVE_FENCE.findall(text)
    if len(matches) != 1 or text.count('```implementaudit-work-graph') != 1:
        raise WorkGraphError(f'{path}: exactly one native metadata block required')
    obj = _require_object(decode_strict_json_bytes(matches[0].encode(), path), path)
    if obj.get('schema') != schema:
        raise WorkGraphError(f'{path}: unknown native metadata schema')
    return obj

_NATIVE_STATIC_OWNER_SHA256 = '5e0dd0e11c6ad9c50ed10ffdb1fd06bda96b9e2e31d60a878ead0892a993271a'


_NATIVE_STATIC_OWNER_BYTES = 400009


NATIVE_SOURCE_MAX_ENTRIES = 1024


NATIVE_SOURCE_MAX_FILES = 256


NATIVE_SOURCE_MAX_FILE_BYTES = 256 * 1024


NATIVE_SOURCE_MAX_TOTAL_BYTES = 4 * 1024 * 1024


NATIVE_READ_MAX_ENTRIES = 4096


NATIVE_READ_MAX_FILE_BYTES = 16 * 1024 * 1024


NATIVE_READ_MAX_TOTAL_BYTES = 64 * 1024 * 1024


NATIVE_STATIC_MAX_DEPTH = 16


def _native_static_owner_module_v1():
    """Load exact source bytes, never execute an import-path reread."""
    import stat
    import types
    path = pathlib.Path(__file__).absolute().parents[3] / 'scripts' / 'operational-evidence.py'
    try:
        # This bootstrap admits code only by its fixed physical path AND bytes.
        # All subsequent native content reads use that owner's handle reader.
        for parent in (path.parent, *path.parents):
            info = parent.lstat()
            if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                    or getattr(info, 'st_file_attributes', 0) & 0x400):
                raise OSError('source owner parent aliases another object')
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or stat.S_ISLNK(before.st_mode) or path.resolve(strict=True) != path
                or getattr(before, 'st_file_attributes', 0) & 0x400):
            raise OSError('source owner aliases another object')
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        flags = (os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
                 | getattr(os, 'O_NONBLOCK', 0))
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            if identity(opened) != identity(before):
                raise OSError('source owner changed before read')
            raw = stream.read(_NATIVE_STATIC_OWNER_BYTES + 1)
            after = os.fstat(stream.fileno())
        final = path.lstat()
        if (identity(before) != identity(opened) or identity(opened) != identity(after)
                or identity(after) != identity(final)
                or len(raw) != _NATIVE_STATIC_OWNER_BYTES
                or hashlib.sha256(raw).hexdigest() != _NATIVE_STATIC_OWNER_SHA256):
            raise OSError('source owner byte identity changed')
        module = types.ModuleType('_implementaudit_r0035_static_owner')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        required = ('_run_git', '_read_repository_path', '_native_child_environment',
                    '_native_cleanup_private_closure', '_native_module_from_bytes')
        if any(not callable(getattr(module, name, None)) for name in required):
            raise OSError('fixed source owner lacks the required read contract')
        return module, path, raw
    except (OSError, ImportError) as exc:
        raise WorkGraphError('native static source owner is unavailable or changed') from exc


def _native_static_file_v1(owner, path, maximum, budget):
    import stat
    path = pathlib.Path(path).absolute()
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or stat.S_ISLNK(before.st_mode)
                or getattr(before, 'st_file_attributes', 0) & 0x400
                or before.st_size > maximum or before.st_size > budget['remaining']):
            raise OSError('native file type, alias or byte bound refused')
        # Root omitted intentionally: the owner traverses from the filesystem
        # anchor and opens every parent/leaf without following aliases.
        raw, kind = owner._read_repository_path(path, maximum=min(maximum, budget['remaining']))
        after = path.lstat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if kind != 'file' or identity(before) != identity(after) or len(raw) != before.st_size:
            raise OSError('native file changed during handle-bound read')
        budget['remaining'] -= len(raw)
        return raw, before.st_mode & 4095
    except (OSError, owner.OperationalEvidenceError) as exc:
        raise WorkGraphError('native static file custody or byte bound refused') from exc


def _native_windows_directory_rows_v1(owner, kernel, handle, requested, budget):
    """Query FILE_ID_BOTH_DIR_INFO on the held object, never its pathname."""
    import ctypes
    class DirectoryHeader(ctypes.Structure):
        _fields_ = [('next_offset', ctypes.c_uint32), ('index', ctypes.c_uint32),
            ('creation', ctypes.c_int64), ('access', ctypes.c_int64),
            ('write', ctypes.c_int64), ('change', ctypes.c_int64),
            ('end_of_file', ctypes.c_int64), ('allocation', ctypes.c_int64),
            ('attributes', ctypes.c_uint32), ('name_bytes', ctypes.c_uint32),
            ('ea_bytes', ctypes.c_uint32), ('short_name_bytes', ctypes.c_ubyte),
            ('short_name', ctypes.c_uint16 * 12), ('file_id', ctypes.c_uint64)]
    header_bytes = ctypes.sizeof(DirectoryHeader)
    if header_bytes != 104 or DirectoryHeader.file_id.offset != 96:
        raise OSError('Windows directory query layout unsupported')
    kernel.GetFileInformationByHandleEx.argtypes = [ctypes.c_void_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_uint32]
    kernel.GetFileInformationByHandleEx.restype = ctypes.c_int
    capacity = 64 * 1024
    storage = ctypes.create_string_buffer(capacity + 7)
    address = (ctypes.addressof(storage) + 7) & ~7
    rows, names = [], set()
    query_class = 0xB  # FileIdBothDirectoryRestartInfo, then continuation 0xA.
    pages = 0
    while True:
        pages += 1
        if pages > budget['maximum_entries'] + 2:
            raise OSError('native directory query page bound exceeded')
        ctypes.memset(address, 0, capacity)
        if not kernel.GetFileInformationByHandleEx(handle, query_class, address, capacity):
            error = ctypes.get_last_error()
            if error == 18:  # ERROR_NO_MORE_FILES
                break
            raise ctypes.WinError(error)
        query_class = 0xA
        raw = ctypes.string_at(address, capacity)
        position = 0
        while True:
            if position + header_bytes > capacity:
                raise OSError('native directory query record exceeds buffer')
            row = DirectoryHeader.from_buffer_copy(raw, position)
            end = position + header_bytes + row.name_bytes
            if not row.name_bytes or row.name_bytes % 2 or end > capacity:
                raise OSError('native directory query name bound refused')
            try:
                name = raw[position + header_bytes:end].decode('utf-16-le', 'strict')
            except UnicodeError as exc:
                raise OSError('native directory query name encoding refused') from exc
            if name not in {'.', '..'}:
                budget['entries'] += 1
                if budget['entries'] > budget['maximum_entries']:
                    raise OSError('native directory population bound exceeded')
                folded = name.casefold()
                if (folded in names or any(c in name for c in ('\\', '/', ':', '\0'))
                        or name.rstrip(' .') != name or pathlib.PureWindowsPath(name).is_reserved()
                        or row.attributes & 0x400):
                    raise OSError('native directory query alias/name refused')
                names.add(folded)
                directory = bool(row.attributes & 0x10)
                child = owner._windows_open_child_v1(handle, name, directory)
                try:
                    info = owner._snapshot_handle_info_v1(kernel, child)
                    if (info.attributes & 0x400 or info.attributes != row.attributes
                            or ((info.file_index_high << 32) | info.file_index_low) != row.file_id
                            or not directory and info.links != 1):
                        raise OSError('native directory member identity/type/alias changed')
                    if str(owner._windows_handle_name_v1(kernel, child)).casefold() != str(requested / name).casefold():
                        raise OSError('native directory member canonical name changed')
                    mode = (0o444 if info.attributes & 1 else 0o666) | (0o111 if directory else 0)
                    rows.append((name, directory, mode))
                finally:
                    kernel.CloseHandle(child)
            if not row.next_offset:
                break
            if (row.next_offset % 8 or row.next_offset < header_bytes + row.name_bytes
                    or position + row.next_offset + header_bytes > capacity):
                raise OSError('native directory query offset bound refused')
            position += row.next_offset
    return sorted(rows)


def _native_static_directory_v1(owner, path, budget):
    """Enumerate finitely while holding a non-alias directory chain."""
    import stat
    path = pathlib.Path(path).absolute()
    held = []
    kernel = None
    try:
        if os.name == 'nt':
            import ctypes
            kernel = owner._snapshot_windows_kernel_v1()
            if len(path.drive) != 2 or path.drive[1] != ':' or kernel.GetDriveTypeW(path.anchor) != 3:
                raise OSError('native directory needs a fixed local drive')
            handle = kernel.CreateFileW(path.anchor, 0x80000000, 1, None, 3, 0x02200000, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            held.append(handle)
            requested = pathlib.PureWindowsPath(path.anchor)
            for part in path.parts[1:]:
                if part in {'.', '..'} or ':' in part or part.rstrip(' .') != part or pathlib.PureWindowsPath(part).is_reserved():
                    raise OSError('native directory alias spelling refused')
                handle = owner._windows_open_child_v1(held[-1], part, True, hold_directory=True)
                held.append(handle)
                requested /= part
                info = owner._snapshot_handle_info_v1(kernel, handle)
                if info.attributes & 0x400 or not info.attributes & 0x10:
                    raise OSError('native directory reparse/type refused')
                if str(owner._windows_handle_name_v1(kernel, handle)).casefold() != str(requested).casefold():
                    raise OSError('native directory long-name alias refused')
            before = owner._snapshot_handle_info_v1(kernel, held[-1])
            rows = _native_windows_directory_rows_v1(owner, kernel, held[-1], requested, budget)
            after = owner._snapshot_handle_info_v1(kernel, held[-1])
            identity = lambda value: (value.attributes, value.volume_serial,
                value.file_index_high, value.file_index_low, value.links,
                value.creation_time.high, value.creation_time.low,
                value.write_time.high, value.write_time.low)
            if identity(before) != identity(after) or any(
                    owner._snapshot_handle_info_v1(kernel, h).attributes & 0x400 for h in held):
                raise OSError('native directory changed during held-handle query')
            return rows, 0o555 if before.attributes & 1 else 0o777
        elif (os.name == 'posix' and os.open in os.supports_dir_fd
                and hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY')):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_NONBLOCK
            held.append(os.open(path.anchor, flags))
            for part in path.parts[1:]:
                held.append(os.open(part, flags, dir_fd=held[-1]))
            scan_target = held[-1]
        else:
            raise OSError('native directory handle semantics unsupported')
        before = path.lstat()
        rows = []
        with os.scandir(scan_target) as entries:
            for entry in entries:
                budget['entries'] += 1
                if budget['entries'] > budget['maximum_entries']:
                    raise OSError('native directory population bound exceeded')
                info = entry.stat(follow_symlinks=False)
                if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400
                        or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))
                        or stat.S_ISREG(info.st_mode) and info.st_nlink != 1):
                    raise OSError('native member alias/type refused')
                rows.append((entry.name, stat.S_ISDIR(info.st_mode), info.st_mode & 4095))
        after = path.lstat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after):
            raise OSError('native directory changed during enumeration')
        if kernel is not None and any(owner._snapshot_handle_info_v1(kernel, h).attributes & 0x400 for h in held):
            raise OSError('native directory changed into a reparse point')
        return sorted(rows), before.st_mode & 4095
    except OSError as exc:
        raise WorkGraphError('native directory custody or population bound refused') from exc
    finally:
        for handle in reversed(held):
            kernel.CloseHandle(handle) if kernel is not None else os.close(handle)


_NATIVE_FIXED_GIT_READ_BOOTSTRAP = r'''
import base64, hashlib, json, pathlib, sys, types
request = json.loads(sys.stdin.buffer.read(2 * 1024 * 1024))
raw = base64.b64decode(request['source'], validate=True)
if hashlib.sha256(raw).hexdigest() != request['sha256']:
    raise SystemExit('source identity mismatch')
module = types.ModuleType('_r0035_fixed_git_source_owner')
module.__file__ = request['path']
exec(compile(raw, request['path'], 'exec'), module.__dict__)
commands = [('rev-parse', 'HEAD'), ('rev-parse', 'HEAD^{tree}'),
            ('diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--raw', '--no-abbrev', '-z', 'HEAD'),
            ('status', '--porcelain=v1', '-z', '--untracked-files=all'),
            ('ls-files', '--others', '--exclude-standard', '-z'),
            ('diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--name-only', '-z', 'HEAD')]
values = []
for command in commands:
    value = module._run_git(pathlib.Path(request['repository']), *command, text=False).stdout
    if len(value) > 16 * 1024 * 1024:
        raise SystemExit('native Git output bound exceeded')
    values.append(base64.b64encode(value).decode('ascii'))
sys.stdout.write(json.dumps(values, separators=(',', ':')))
'''


def _native_continuity_host_v1():
    """Keep host-only primitives independent of optional route acquisition.

    These three primitives retain the selected R0033 source bodies. The local
    refusal type is WorkGraphError; no producer module or policy is loaded.
    """
    import shutil
    import stat
    from pathlib import Path
    from types import SimpleNamespace

    def fail(message):
        raise WorkGraphError(message)

    def trusted_host_executable(repo: Path, name: str) -> Path:
        selected: str | None = None
        if os.name == "nt" and name == "bash":
            for key in ("ProgramFiles", "ProgramFiles(x86)"):
                if root := os.environ.get(key):
                    candidate = Path(root) / "Git" / "bin" / "bash.exe"
                    if candidate.is_file():
                        selected = str(candidate)
                        break
        if selected is None:
            selected = shutil.which(name)
        if selected is None:
            fail(f"trusted host executable is unavailable: {name}")
        resolved = Path(selected).resolve()
        try:
            resolved.relative_to(repo)
        except ValueError:
            pass
        else:
            fail("system action executable resolves inside target-repository custody")
        if os.name == "nt":
            roots = [
                Path(value).resolve()
                for key in ("ProgramFiles", "ProgramFiles(x86)", "SystemRoot")
                if (value := os.environ.get(key))
            ]
            if not any(str(resolved).casefold().startswith(str(root).casefold() + os.sep.casefold()) for root in roots):
                fail("system action executable is outside trusted host custody")
        else:
            cursor = resolved
            while True:
                info = os.lstat(cursor)
                if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    fail("system action executable is outside root-owned host custody")
                if cursor.parent == cursor:
                    break
                cursor = cursor.parent
        return resolved

    def sanitized_action_environment() -> dict[str, str]:
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("GIT_", "LD_", "DYLD_"))
            and not key.startswith("BASH_FUNC_")
            and key not in {"BASH_ENV", "BASHOPTS", "CDPATH", "ENV", "SHELLOPTS"}
        }
        if os.name == "nt":
            candidates: list[Path] = []
            if program_files := os.environ.get("ProgramFiles"):
                git_root = Path(program_files) / "Git"
                candidates.extend((git_root / "cmd", git_root / "bin", git_root / "usr" / "bin"))
            if system_root := os.environ.get("SystemRoot"):
                candidates.extend((Path(system_root) / "System32", Path(system_root)))
            environment["PATH"] = os.pathsep.join(str(path.resolve()) for path in candidates if path.is_dir())
        else:
            environment["PATH"] = "/usr/bin:/bin"
        environment.update(
            {
                "GIT_ATTR_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": "NUL" if os.name == "nt" else "/dev/null",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_EXTERNAL_DIFF": "",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_PAGER": "cat",
                "LC_ALL": "C",
                "PAGER": "cat",
            }
        )
        return environment

    def bash_script_path(path: Path) -> str:
        resolved = str(path.resolve())
        if os.name != "nt":
            return resolved
        drive, tail = os.path.splitdrive(resolved)
        if len(drive) != 2 or drive[1] != ":":
            fail("shell action path is not on an exact local drive")
        return f"/{drive[0].lower()}{tail.replace(os.sep, '/')}"

    return SimpleNamespace(trusted_host_executable=trusted_host_executable,
                           sanitized_action_environment=sanitized_action_environment,
                           bash_script_path=bash_script_path)


def _native_claim_call_v1(owner, route, repo, arguments, claim_raw, validate_raw):
    pair = (hashlib.sha256(claim_raw).hexdigest(), hashlib.sha256(validate_raw).hexdigest())
    if pair not in (_NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE, _NATIVE_COMBINED_CURRENT_PAIR_V1):
        transport, sources, _ = _native_six_source_transport_v1(owner, claim_raw, validate_raw)
        try:
            observed = transport.call_readonly_v1(owner, repository=str(repo), sources=sources,
                                                 arguments=tuple(arguments), route=route)
        except transport.ContinuityTransportError as exc:
            raise WorkGraphError(str(exc)) from exc
        if observed['returncode'] or len(observed['stdout']) > 8192 or len(observed['stderr']) > 16384:
            raise WorkGraphError('native continuity owner refused or changed')
        return observed['stdout'].decode('utf-8', 'strict').strip()
    import contextlib
    import io
    import tempfile
    environment = owner._native_child_environment(route)
    # R0011 needs actual Git/common-directory identity, not a disposable view.
    # Its fixed current/require/verify commands do not scan worktree filters.
    # Deny inherited shell/Python startup hooks and object/network side effects.
    environment.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
                       GIT_TERMINAL_PROMPT='0', GIT_CONFIG_SYSTEM=os.devnull)
    config = {'core.fsmonitor': 'false', 'core.hooksPath': os.devnull,
              'protocol.allow': 'never', 'protocol.ext.allow': 'never',
              'credential.helper': '', 'core.sshCommand': '', 'submodule.recurse': 'false'}
    environment['GIT_CONFIG_COUNT'] = str(len(config))
    for index, (key, value) in enumerate(config.items()):
        environment['GIT_CONFIG_KEY_' + str(index)] = key
        environment['GIT_CONFIG_VALUE_' + str(index)] = value
    stream_builder = getattr(owner, '_native_r0011_stdin_script_v1', None)
    script = stream_builder(claim_raw, validate_raw, arguments) if callable(stream_builder) else None
    if script is not None:
        if type(script) is not bytes or not 0 < len(script) <= 3 * 1024 * 1024:
            raise WorkGraphError('native continuity source stream is malformed')
        with contextlib.redirect_stdout(io.StringIO()):
            bash = route.trusted_host_executable(repo, 'bash')
        # source repo: the fixed primary owns this exact loaded-byte transport.
        # argv0 and all original readonly owner calls remain unchanged. No
        # temporary path can replace bytes between their hash and evaluation.
        result = subprocess.run([str(bash), '-c', 'eval "$(cat)"',
            'implementaudit-r0035-current', hashlib.sha256(claim_raw).hexdigest(),
            hashlib.sha256(validate_raw).hexdigest(), *arguments], input=script,
            cwd=repo, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30, check=False)
        marker = ('implementaudit-native-r0011-child-v1\t' + hashlib.sha256(claim_raw).hexdigest()
                  + '\t' + hashlib.sha256(validate_raw).hexdigest()).encode()
        if (result.returncode or len(result.stdout) > 8192 or len(result.stderr) > 16384
                or result.stderr.splitlines().count(marker) != 1):
            raise WorkGraphError('native continuity owner refused or changed')
        return result.stdout.decode('utf-8', 'strict').strip()
    closure = pathlib.Path(tempfile.mkdtemp(prefix='implementaudit-r0035-current-'))
    expected = [(closure / 'claim-run.sh', claim_raw), (closure / 'validate-run-root.sh', validate_raw)]
    try:
        for path, raw in expected:
            with path.open('xb') as stream:
                stream.write(raw)
        with contextlib.redirect_stdout(io.StringIO()):
            bash = route.trusted_host_executable(repo, 'bash')
            paths = [route.bash_script_path(path) for path, raw in expected]
        result = subprocess.run([str(bash), '-c', owner._NATIVE_R0011_CHILD_BOOTSTRAP,
            'implementaudit-r0035-current', *paths,
            hashlib.sha256(claim_raw).hexdigest(), hashlib.sha256(validate_raw).hexdigest(),
            *arguments], cwd=repo, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        expected_marker = ('implementaudit-native-r0011-child-v1\t' + hashlib.sha256(claim_raw).hexdigest()
                           + '\t' + hashlib.sha256(validate_raw).hexdigest()).encode()
        if (result.returncode or len(result.stdout) > 8192 or len(result.stderr) > 16384
                or result.stderr.splitlines().count(expected_marker) != 1):
            raise WorkGraphError('native continuity owner refused or changed')
        return result.stdout.decode('utf-8', 'strict').strip()
    finally:
        owner._native_cleanup_private_closure(closure, expected)


def _native_source_snapshot(run_root):
    owner, owner_path, owner_raw = _native_static_owner_module_v1()
    root = pathlib.Path(run_root).absolute()
    budget = dict(entries=0, maximum_entries=NATIVE_SOURCE_MAX_ENTRIES, remaining=NATIVE_SOURCE_MAX_TOTAL_BYTES)
    # Inspect the declared root through held handles even when it has no specs.
    root_rows, _ = _native_static_directory_v1(owner, root, budget)
    root_types = {name: directory for name, directory, mode in root_rows}
    result = {}
    for name in ('STATE.md', 'ROADMAP.md'):
        result[name] = _native_static_file_v1(owner, root / name, NATIVE_SOURCE_MAX_FILE_BYTES, budget)[0]
    stack = [(root / name, 1) for name in ('plans', 'phases', 'tasks') if name in root_types]
    while stack:
        directory, depth = stack.pop()
        if depth > NATIVE_STATIC_MAX_DEPTH:
            raise WorkGraphError('native source directory depth bound exceeded')
        rows, _ = _native_static_directory_v1(owner, directory, budget)
        for name, is_directory, mode in rows:
            path = directory / name
            if is_directory:
                stack.append((path, depth + 1))
            elif name.endswith('.md'):
                if len(result) >= NATIVE_SOURCE_MAX_FILES:
                    raise WorkGraphError('native source document population bound exceeded')
                result[path.relative_to(root).as_posix()] = _native_static_file_v1(owner, path, NATIVE_SOURCE_MAX_FILE_BYTES, budget)[0]
    _, final_path, final_raw = _native_static_owner_module_v1()
    if final_path != owner_path or final_raw != owner_raw:
        raise WorkGraphError('native static source owner changed during acquisition')
    return dict(sorted(result.items()))

# This exact R0011 pair shares load_final_v3_receipt only for the LF-exact
# 18-field domain. Its legacy TSV-pointer branch is not equivalent. Unknown
# helper or receipt bytes retain separate verification; no saved authority token.
_NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE = (
    '07e09843b2831149dc43e5f0dc458e82ae5cf9614b116393ac774ddea19390c7',
    'fe005aea40d8eb2ea860c62f0caf1fb78ba678381ab6444e4f7b8202e82b77e5')

# The same owner emits its controller tuple only after the full require branch.
# No supplied tuple replaces owner acquisition; other source pairs keep both calls.
_NATIVE_COMBINED_CURRENT_PAIR_V1 = (
    '9665ba20e02c02882f3172549e90d78e790c6c0133cd31749a30e1d29c3cc0ce',
    'fe005aea40d8eb2ea860c62f0caf1fb78ba678381ab6444e4f7b8202e82b77e5')


# A separate exact-source transport profile, never a new optimisation pair.
_NATIVE_SIX_SOURCE_PAIR_V1 = (
    '50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383',
    'd8b046b5417dce13ed66a5ac5fffaf3d18fae40c97d42aef8b38470500d575a6')
_NATIVE_CONTINUITY_TRANSPORT_SHA256 = '0dfdd58d07784164581e265d0db8a52cc08270e791bf29e6d9e1f9814113a171'
_NATIVE_CONTINUITY_TRANSPORT_BYTES = 51541


def _native_six_source_transport_v1(owner, claim_raw, validate_raw):
    """Acquire one exact repository-only source composition before dispatch."""
    import types
    path = pathlib.Path(__file__).absolute().parents[3] / 'scripts/work-graph-continuity-transport.py'
    raw, transport_mode = _native_static_file_v1(owner, path, 64 * 1024, dict(remaining=64 * 1024))
    if (len(raw) != _NATIVE_CONTINUITY_TRANSPORT_BYTES
            or hashlib.sha256(raw).hexdigest() != _NATIVE_CONTINUITY_TRANSPORT_SHA256):
        raise WorkGraphError('native continuity transport source identity changed')
    module = types.ModuleType('_implementaudit_native_continuity_transport')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    root = pathlib.Path(__file__).absolute().parent
    profiles = module.source_profiles_for_helpers_v1(claim_raw, validate_raw)
    if not profiles:
        raise WorkGraphError('native continuity helpers are not an explicitly selected source domain')
    sources, identity = [], []
    budget = dict(remaining=1024 * 1024)
    for index, (name, _, _, _) in enumerate(profiles[0]):
        source = root / name
        data, mode = _native_static_file_v1(owner, source, max(p[index][1] for p in profiles), budget)
        identity.append((name, len(data), hashlib.sha256(data).hexdigest(), mode))
        sources.append((str(source), data))
    if not any(len(identity) == len(profile) and all(actual[:3] == expected[:3] and (expected[3] is None or actual[3] == expected[3])
                       for actual, expected in zip(identity, profile)) for profile in profiles):
        raise WorkGraphError('native continuity closure source identity changed')
    if (sources[0][1], sources[1][1]) != (claim_raw, validate_raw):
        raise WorkGraphError('native continuity source set crossed its helper acquisition')
    return module, tuple(sources), (path, raw, transport_mode)


def _native_equivalent_receipt_domain_v1(owner, repo, receipt):
    """Classify immutable bytes returned by the exact helper, not caller proof."""
    try:
        raw = owner._native_blob(repo, receipt.rsplit('@', 1)[1],
                                 '$native.continuity_receipt_domain', maximum=512 * 1024)
        if (type(raw) is not bytes or len(raw) > 512 * 1024 or
                not raw.startswith(b'implementaudit.continuity-receipt.v3\t') or
                not raw.endswith(b'\n') or raw.count(b'\n') != 1 or
                raw.count(b'\t') != 17 or any(not field for field in raw[:-1].split(b'\t')) or
                any(value < 0x20 and value not in (0x09, 0x0A) or value == 0x7F for value in raw)):
            return False
        raw.decode('utf-8', 'strict')
        return True
    except (Exception, SystemExit):
        # An unavailable discriminator cannot authorize the shortcut.
        return False


def _native_continuity(repo_root, run_root, *, _source_reads=None, _current_reads=None, _closure_reads=None):
    import base64
    if _source_reads is not None and type(_source_reads) is not list:
        raise WorkGraphError('native continuity source output must be a private list')
    if _current_reads is not None and type(_current_reads) is not list:
        raise WorkGraphError('native currentness output must be a private list')
    if _closure_reads is not None and type(_closure_reads) is not list:
        raise WorkGraphError('native closure output must be a private list')
    owner, owner_path, owner_raw = _native_static_owner_module_v1()
    host = _native_continuity_host_v1()
    repo = pathlib.Path(repo_root).absolute()
    helper = pathlib.Path(__file__).absolute().with_name('claim-run.sh')
    validate = helper.with_name('validate-run-root.sh')
    budget = dict(remaining=512 * 1024)
    claim_raw = _native_static_file_v1(owner, helper, 256 * 1024, budget)[0]
    validate_raw = _native_static_file_v1(owner, validate, 256 * 1024, budget)[0]
    helper_pair = (hashlib.sha256(claim_raw).hexdigest(), hashlib.sha256(validate_raw).hexdigest())
    transport = None
    closure = None
    if helper_pair not in (_NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE, _NATIVE_COMBINED_CURRENT_PAIR_V1):
        transport, transport_sources, transport_source = _native_six_source_transport_v1(owner, claim_raw, validate_raw)
    def call(arguments):
        nonlocal closure
        if transport is None:
            return _native_claim_call_v1(owner, host, repo, arguments, claim_raw, validate_raw)
        try:
            observed = transport.call_readonly_v1(owner, repository=str(repo),
                sources=transport_sources, arguments=tuple(arguments), route=host)
        except transport.ContinuityTransportError as exc:
            raise WorkGraphError('native continuity transport refused: ' + exc.code) from exc
        if observed['returncode'] or len(observed['stdout']) > 8192 or len(observed['stderr']) > 16384:
            raise WorkGraphError('native continuity owner refused or changed')
        if closure is not None and observed['closure'] != closure:
            raise WorkGraphError('native continuity executed source closure changed')
        closure = observed['closure']
        return observed['stdout'].decode('utf-8', 'strict').strip()
    if helper_pair == _NATIVE_COMBINED_CURRENT_PAIR_V1:
        observed = call(['--observe-current-continuity']).split('\t')
        if len(observed) != 6 or observed[0] != 'implementaudit.current-continuity-observation.v1':
            raise WorkGraphError('native combined continuity observation is malformed')
        current, receipt = observed[1:5], observed[5]
    else:
        current = call(['--current-controller']).split('\t')
        receipt = None
    if len(current) != 4 or pathlib.Path(current[1]).absolute() != repo or pathlib.Path(current[2]).absolute() != pathlib.Path(run_root).absolute():
        raise WorkGraphError('native continuity root mismatch')
    if receipt is None:
        receipt = call(['--require-current-continuity', current[0]])
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError('native continuity receipt format mismatch')
    if (helper_pair not in (_NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE, _NATIVE_COMBINED_CURRENT_PAIR_V1) or
            not _native_equivalent_receipt_domain_v1(owner, repo, receipt)):
        verified = call(['--verify-resume-receipt', receipt])
        if verified != receipt:
            raise WorkGraphError('native continuity receipt readback mismatch')
    request = dict(source=base64.b64encode(owner_raw).decode('ascii'), sha256=_NATIVE_STATIC_OWNER_SHA256,
                   path=str(owner_path), repository=str(repo))
    environment = owner._native_child_environment(host)
    result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', _NATIVE_FIXED_GIT_READ_BOOTSTRAP],
        input=json.dumps(request).encode(), cwd=repo, env=environment, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=180, check=False)
    if result.returncode or result.stderr or len(result.stdout) > 112 * 1024 * 1024:
        raise WorkGraphError('native fixed-source Git read failed or exceeded its bound')
    values = json.loads(result.stdout.decode('ascii'))
    if type(values) is not list or len(values) != 6:
        raise WorkGraphError('native fixed-source Git result is malformed')
    head_raw, tree_raw, diff, status, untracked, changed_paths = [base64.b64decode(v, validate=True) for v in values]
    head, tree = head_raw.decode('ascii').strip(), tree_raw.decode('ascii').strip()
    if not COMMIT_RE.fullmatch(head) or not COMMIT_RE.fullmatch(tree):
        raise WorkGraphError('native fixed-source Git identity is malformed')
    paths = [os.fsdecode(p) for p in untracked.split(b'\0') if p]
    changed = [os.fsdecode(p) for p in changed_paths.split(b'\0') if p]
    if (len(paths) + len(changed) > NATIVE_READ_MAX_ENTRIES
            or len(paths) != len(set(paths)) or len(changed) != len(set(changed))):
        raise WorkGraphError('native worktree change population bound exceeded')
    other = []
    budget = dict(remaining=NATIVE_READ_MAX_TOTAL_BYTES)
    changed_records = []
    for relative in sorted(set(paths + changed)):
        if owner._repository_path_policy(relative) is not None:
            raise WorkGraphError('native worktree source policy refuses this path')
        pure = pathlib.PurePosixPath(relative)
        if pure.is_absolute() or any(part in {'', '.', '..'} for part in pure.parts):
            raise WorkGraphError('native worktree path escapes its repository')
        target = repo.joinpath(*pure.parts)
        try:
            target.lstat()
        except FileNotFoundError:
            if relative in paths:
                raise WorkGraphError('native untracked member disappeared')
            parent = target.parent
            while True:
                try:
                    parent.lstat()
                    break
                except FileNotFoundError:
                    parent = parent.parent
            _native_static_directory_v1(owner, parent, dict(entries=0, maximum_entries=NATIVE_READ_MAX_ENTRIES))
            changed_records.append([relative, 'MISSING'])
            continue
        data, mode = _native_static_file_v1(owner, target, NATIVE_READ_MAX_FILE_BYTES, budget)
        digest = hashlib.sha256(data).hexdigest()
        if relative in paths:
            other.append([relative, digest])
        if relative in changed:
            changed_records.append([relative, mode, digest])
    if (_native_static_file_v1(owner, helper, 256 * 1024, dict(remaining=256 * 1024))[0] != claim_raw
            or _native_static_file_v1(owner, validate, 256 * 1024, dict(remaining=256 * 1024))[0] != validate_raw):
        raise WorkGraphError('native continuity helper source changed')
    if transport is not None:
        for path, raw in transport_sources:
            if _native_static_file_v1(owner, path, len(raw), dict(remaining=len(raw)))[0] != raw:
                raise WorkGraphError('native continuity closure changed after execution')
        path, raw, mode = transport_source
        if _native_static_file_v1(owner, path, len(raw), dict(remaining=len(raw))) != (raw, mode):
            raise WorkGraphError('native continuity transport changed after execution')
        closure = dict(schema='implementaudit.native-continuity-closure.v1', execution=closure,
            transport=dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), mode=mode))
    _, final_path, final_raw = _native_static_owner_module_v1()
    if final_path != owner_path or final_raw != owner_raw:
        raise WorkGraphError('native static owner source changed during continuity')
    if _source_reads is not None:
        # Output only, recorded after actual loaded-byte execution and fences.
        # No supplied value is consulted as currentness or source authority.
        _source_reads.append(dict(claim_sha256=helper_pair[0], validate_sha256=helper_pair[1]))
    if _closure_reads is not None:
        _closure_reads.append(closure)
    if _current_reads is not None:
        _current_reads.append(dict(controller_result=list(current), receipt=receipt))
    return dict(acquisition='NATIVE_CONTINUITY_VERIFIED', controller=current[0], claim=current[3], receipt=receipt,
        epoch=receipt.split('/')[-1].split('@')[0], candidate_head=head, candidate_tree=tree,
        worktree_digest=_graph_hash([_graph_hash([hashlib.sha256(diff).hexdigest(), changed_records]), hashlib.sha256(status).hexdigest(), other]),
        continuity_helper_digest=hashlib.sha256(claim_raw).hexdigest())

def _native_semantics(value, label):
    values = _native_strings(value, label)
    for item in values:
        if not re.fullmatch('(?:path|semantic|scope):[^\\s]+', item):
            raise WorkGraphError(f'{label}: typed path/semantic/scope identity required')
        if item.startswith('path:'):
            path = item[5:]
            if '\\' in path or path.startswith('/') or ':' in path or any((p in {'', '.', '..'} for p in path.split('/'))):
                raise WorkGraphError(f'{label}: canonical relative POSIX path required')
    return values

def _native_validate_node(node, path):
    _require_object(node, path)
    _require_exact_members(node, NATIVE_NODE_FIELDS, path)
    _native_name(node['id'], path + '.id')
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.:/-]*', node['id']):
        raise WorkGraphError(f'{path}: invalid stable node identity')
    if node['parent'] is not None:
        _native_name(node['parent'], path + '.parent')
    _native_enum(node['kind'], {'PLAN', 'PHASE', 'TASK', 'JOIN'}, path + '.kind')
    _native_enum(node['state'], {'OPEN', 'ACTIVE', 'DONE'}, path + '.state')
    for key in ('requires', 'optional', 'route_scopes', 'invalidators'):
        _native_strings(node[key], path + '.' + key)
    if set(node['requires']) & set(node['optional']):
        raise WorkGraphError(f'{path}: required/optional overlap')
    for key in ('reads', 'writes', 'acceptance', 'resources', 'authority'):
        _native_semantics(node[key], path + '.' + key)
    _native_enum(node['effect'], {'READ_ONLY', 'PREPARATION', 'MUTATION', 'EXTERNAL'}, path + '.effect')
    _native_enum(node['authorization'], {'PERMITTED', 'MISSING', 'UNKNOWN'}, path + '.authorization')
    _native_enum(node['independence'], {'KNOWN', 'UNKNOWN'}, path + '.independence')
    _native_int(node['resource_demand'], path + '.resource_demand')
    _native_int(node['rank'], path + '.rank', INT64_MIN)
    _require_bool(node['independent_results'], path + '.independent_results')
    if node['logical_delivery'] is not None:
        _native_name(node['logical_delivery'], path + '.logical_delivery')
    if node['state'] == 'DONE':
        if type(node['done_evidence']) is not str or not DIGEST_RE.fullmatch(node['done_evidence']):
            raise WorkGraphError(f'{path}: DONE requires source evidence digest')
    elif node['done_evidence'] is not None:
        raise WorkGraphError(f'{path}: non-DONE cannot carry DONE evidence')
    future = node['future_consumer']
    if future is not None:
        _require_object(future, path + '.future_consumer')
        _require_exact_members(future, {'node', 'condition'}, path + '.future_consumer')
        for key in future:
            _native_name(future[key], path + '.future_consumer.' + key)
    if node['effect'] == 'PREPARATION' and future is None:
        raise WorkGraphError(f'{path}: preparation requires bounded future consumer')
    context = _require_object(node['context'], path + '.context')
    _require_exact_members(context, {'locality', 'governor_cost', 'child_cost', 'return_cost', 'useful_value'}, path + '.context')
    _native_enum(context['locality'], {'GOVERNOR', 'CHILD', 'EITHER'}, path + '.context.locality')
    for key in ('governor_cost', 'child_cost', 'return_cost', 'useful_value'):
        _native_int(context[key], path + '.context.' + key)

def _native_validate_context(context):
    _require_object(context, 'native context')
    _require_exact_members(context, {'host_capacity', 'operator_ceiling', 'reserve', 'route_facts', 'outstanding_deliveries'}, 'native context')
    for key in ('host_capacity', 'reserve'):
        _native_int(context[key], 'native context.' + key)
    if context['operator_ceiling'] is not None:
        _native_int(context['operator_ceiling'], 'native operator_ceiling')
    scopes = set()
    if type(context['route_facts']) is not list:
        raise WorkGraphError('route facts: array required')
    for fact in context['route_facts']:
        _require_object(fact, 'route fact')
        _require_exact_members(fact, {'schema', 'scope', 'obligation', 'generation', 'binding', 'continuity', 'status', 'satisfaction', 'expected_satisfaction', 'source_digest'}, 'route fact')
        if fact['schema'] != 'implementaudit.work-graph-route-fact.v1':
            raise WorkGraphError('route fact: unknown schema')
        for key in ('scope', 'generation', 'binding', 'continuity'):
            _native_name(fact[key], 'route fact.' + key)
        if fact['obligation'] is not None or fact['status'] != 'NOT_REQUIRED':
            _native_name(fact['obligation'], 'route fact.obligation')
        if fact['scope'] in scopes:
            raise WorkGraphError('route fact: duplicate scope')
        scopes.add(fact['scope'])
        _native_enum(fact['status'], {'BLOCKED', 'SATISFIED', 'NOT_REQUIRED', 'UNKNOWN'}, 'route fact.status')
        for key in ('satisfaction', 'expected_satisfaction'):
            if fact[key] is not None:
                _native_name(fact[key], 'route fact.' + key)
        if type(fact['source_digest']) is not str or not DIGEST_RE.fullmatch(fact['source_digest']):
            raise WorkGraphError('route fact: source digest required')
    if type(context['outstanding_deliveries']) is not list:
        raise WorkGraphError('outstanding deliveries: array required')
    deliveries = set()
    for delivery in context['outstanding_deliveries']:
        _require_object(delivery, 'delivery hold')
        _require_exact_members(delivery, {'id', 'state', 'source_digest'}, 'delivery hold')
        _native_name(delivery['id'], 'delivery hold.id')
        if delivery['id'] in deliveries:
            raise WorkGraphError('duplicate logical delivery hold')
        deliveries.add(delivery['id'])
        _native_enum(delivery['state'], {'PENDING', 'UNKNOWN', 'COMMITTED'}, 'delivery hold.state')
        if type(delivery['source_digest']) is not str or not DIGEST_RE.fullmatch(delivery['source_digest']):
            raise WorkGraphError('delivery hold: source digest required')

_NATIVE_ROUTE_PRODUCER_SHA256 = '8ed51e393f4f8a3be631e48255e9aeca59dcf120a803f1601a034e5ab9e02389'


_NATIVE_ROUTE_PRODUCER_BYTES = 371304
_NATIVE_ROUTE_PRODUCER_PROFILES_V1 = {
    _NATIVE_ROUTE_PRODUCER_SHA256: _NATIVE_ROUTE_PRODUCER_BYTES,
    'ad0367c90db2a23580a2f37ecb6b87d2b774e04ce524a95bf159f038062fafa4': 375105,
    # Combined source, still subject to separate actual acceptance.
    'ba0e378b9f4744b5109317ad10ae98487d12d16060ec737aeb18f55e34fb2451': 375105,
    # Exact retained-source-map receiving delta from R0033 donor79316011.
    '1bf45fa3104dcde045fcd528d57b601323e9476dcb735afdd88b1c27dde8e9ca': 375946,
    # Exact nonblocking delivery capture received from R0033 donor899d32f8.
    'd060782e690d163e2b0db014be429c64cf976e7b1e8d554113ee8f4843a3b1bb': 376700,
    # Exact recovered historical receiver; native admission remains separate.
    '8ca0ed9e1313ff2e60a89b88e56f7bf1a52bf6f179f70df1b0b18f1dde0346f8': 384034,
    # DG07 exact original14 recovery receiving and safe binder source pair.
    '87bce990c85c7db9134c788eb14d9d5d5b38c55091fa47b256396ffc99316bbe': 385106,
    '9d5190969b8667395f170cc18ceecd9576644bbdf5f87e14abd62b926680fc8f': 385331,
    # DG07 exact original14 recovery receiving and safe binder source pair.
    'aa60038b82ec1333e55fb19603df42262665dd671360a224c252145d062f6921': 384881,
    '82ac79404b0a4f3feb9ec2263ae2b86bfe274f13353ac6348ac30e91bf00310e': 385651,
}


_NATIVE_ROUTE_OBSERVATION_KEY = object()


_CAPTURED_ROUTE_REPLAY_KEY = object()


class _RouteScopeObservation:
    """In-process acquisition/replay witness, never accepted from JSON."""
    __slots__ = ('value', 'key', 'receiver_binding')

    def __init__(self, value, key, *, receiver_binding=None):
        if key is not _NATIVE_ROUTE_OBSERVATION_KEY and key is not _CAPTURED_ROUTE_REPLAY_KEY:
            raise WorkGraphError('route observation must be issued by its owner acquisition or captured replay')
        self.value = copy.deepcopy(value)
        self.key = key
        self.receiver_binding = copy.deepcopy(receiver_binding)


def _route_observation_value(observation):
    if (type(observation) is not _RouteScopeObservation or
            (observation.key is not _NATIVE_ROUTE_OBSERVATION_KEY and
             observation.key is not _CAPTURED_ROUTE_REPLAY_KEY)):
        raise WorkGraphError('caller route data cannot replace owner acquisition')
    return copy.deepcopy(observation.value)


def _native_receiver_binding_v1(observation):
    """Validate captured binding semantics; only live owner intake authenticates."""
    scope = _route_observation_value(observation)
    value = copy.deepcopy(observation.receiver_binding)
    if value is None:
        return None
    _require_exact_members(value, {'schema', 'producer', 'executor', 'route_record_oid',
        'route_scope_digest', 'policy', 'record', 'source_pins', 'authority_ceiling', 'establishes'}, 'receiver binding')
    if (value['schema'] != 'implementaudit.ordinary-receiver-binding.v1' or value['producer'] != 'R0033'
            or value['executor'] != 'execute_current_ordinary_receiver_v2' or value['authority_ceiling'] != 'NONE'
            or value['establishes'] != [] or value['route_record_oid'] != scope['route']['record_oid']
            or value['route_scope_digest'] != scope['digest'] or scope['route']['route_state'] != 'SATISFIED'
            or scope['route']['decision'] != 'REQUIRED'):
        raise WorkGraphError('receiver binding is not the current accepted fixed executor')

    def decode_wire(wire):
        _require_exact_members(wire, {'bytes', 'digest', 'bytes_b64'}, 'receiver binding bytes')
        if (type(wire['bytes']) is not int or not 0 < wire['bytes'] <= 1024 * 1024
                or type(wire['bytes_b64']) is not str or len(wire['bytes_b64']) > 1398104):
            raise WorkGraphError('receiver binding bytes exceed their bound')
        try:
            raw = base64.b64decode(wire['bytes_b64'], validate=True)
        except (ValueError, TypeError) as exc:
            raise WorkGraphError('receiver binding bytes are malformed') from exc
        if (len(raw) != wire['bytes'] or base64.b64encode(raw).decode() != wire['bytes_b64']
                or wire['digest'] != 'sha256:' + hashlib.sha256(raw).hexdigest()):
            raise WorkGraphError('receiver binding bytes changed')
        return raw, decode_strict_json_bytes(raw, 'receiver binding document')

    raw, record = decode_wire(value['record'])
    _require_object(record, 'receiver canonical record')
    if (hashlib.sha256(raw).hexdigest() != scope['source']['record_sha256']
            or hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != value['route_record_oid']
            or record.get('record_identity') != scope['route']['record_identity']
            or any(record.get(k) != scope['route'][k] for k in ('controller_id', 'decision', 'route_state', 'obligation_id', 'route_transaction_id'))):
        raise WorkGraphError('receiver binding canonical source differs')
    lifecycle = _require_object(record.get('lifecycle'), 'receiver canonical lifecycle')
    delivery = _require_object(lifecycle.get('delivery'), 'receiver canonical delivery')
    _, packet = decode_wire(delivery.get('packet'))
    _require_object(packet, 'receiver packet')
    event = _require_object(packet.get('source_event'), 'receiver source event')
    if type(event.get('body')) is not str:
        raise WorkGraphError('receiver mission text is missing')
    mission = decode_strict_json_bytes(event['body'].encode(), 'receiver mission')
    _require_exact_members(mission, {'schema', 'policy_digest', 'scope', 'mission', 'authority_ceiling'}, 'receiver mission')
    policy = _require_object(value['policy'], 'receiver policy')
    _require_exact_members(policy, {'schema', 'profile_id', 'selection_pin', 'instance_selection', 'provider', 'code_pins',
        'receiver_argv', 'receiver_node', 'consumer', 'artifact_root', 'root_thread_id', 'root_agent_path'}, 'receiver policy')
    _require_object(policy['code_pins'], 'receiver policy code pins')
    if (mission['schema'] != 'implementaudit.ordinary-review-mission.v1' or mission['authority_ceiling'] != 'NONE'
            or mission['scope'] != scope['scope'] or mission['policy_digest'] != _graph_hash(policy)
            or policy['schema'] != 'implementaudit.ordinary-native-policy.v1' or packet.get('target_identity') != 'audit-assess'
            or packet.get('obligation_id') != scope['route']['obligation_id'] or packet.get('route_transaction_id') != scope['route']['route_transaction_id']
            or type(scope['source']['producer_sha256']) is not str
            or scope['source']['producer_sha256'] not in _NATIVE_ROUTE_PRODUCER_PROFILES_V1
            or policy['code_pins'].get('implementaudit/scripts/route-transaction.py') != scope['source']['producer_sha256']):
        raise WorkGraphError('receiver policy differs from the accepted route')
    names = {'implementaudit/scripts/bounded_file_custody.py', 'implementaudit/scripts/compaction-source-owner-codex-app.py'}
    _require_exact_members(value['source_pins'], names, 'receiver source pins')
    if type(record.get('inputs')) is not list:
        raise WorkGraphError('receiver canonical inputs are missing')
    inputs = {}
    for item in record['inputs']:
        _require_exact_members(item, {'identity', 'path', 'digest', 'status'}, 'receiver canonical input')
        if type(item['path']) is not str or item['path'] in inputs:
            raise WorkGraphError('receiver canonical input identity is ambiguous')
        inputs[item['path']] = item
    for key, digest in value['source_pins'].items():
        _require_digest(digest, 'receiver source digest')
        item = inputs.get('skills/' + key, {})
        if item.get('status') != 'CURRENT' or item.get('digest') != 'sha256:' + digest or policy['code_pins'].get(key) != digest:
            raise WorkGraphError('receiver source is not a current canonical input')
    for key in ('receiver_node', 'consumer'):
        _native_name(policy[key], 'receiver policy.' + key)
    if policy['receiver_node'] == policy['consumer']:
        raise WorkGraphError('receiver and JOIN must be distinct')
    return value


def _native_fixed_receiver_matches_v1(node, nodes, relation, binding):
    if binding is None:
        return False
    policy = binding['policy']
    consumer = nodes.get(policy['consumer'], {})
    return (node['id'] == policy['receiver_node'] and node['kind'] == 'TASK'
        and node['effect'] == 'MUTATION' and node['context']['locality'] == 'GOVERNOR'
        and node['writes'] == ['semantic:r0033-ordinary-receiver-receipt']
        and node['resources'] == ['semantic:writer:r0033-ordinary-receiver-receipt'] and node['authority'] == []
        and node['id'] in relation['affected_nodes'] and node['id'] not in relation['direct_nodes']
        and consumer.get('kind') == 'JOIN' and consumer.get('requires') == [node['id']] and consumer.get('optional') == [])


def _native_validate_route_scope_v1(value, binding):
    """Validate the captured interface, not the authenticity of its caller."""
    _check_graph_seal(value, 'implementaudit.current-route-scope.v1')
    _require_exact_members(value, {
        'schema', 'authority_ceiling', 'establishes', 'route', 'scope',
        'boundary', 'owner', 'host', 'source', 'expiry_fingerprint',
        'satisfaction', 'digest',
    }, 'current route scope')
    if value['authority_ceiling'] != 'READ_ONLY_CURRENT_ROUTE_FACT' or value['establishes'] != []:
        raise WorkGraphError('current route scope: foreign authority')
    route = _require_object(value['route'], 'current route')
    _require_exact_members(route, {
        'controller_id', 'controller_record_oid', 'ref', 'record_oid',
        'record_identity', 'decision', 'classification', 'route_transaction_id',
        'obligation_id', 'route_state',
    }, 'current route')
    owner = _require_object(value['owner'], 'current route owner')
    _require_exact_members(owner, {
        'controller_id', 'claim_id', 'explicit_run_root',
        'continuity_generation', 'continuity_receipt',
    }, 'current route owner')
    expected = dict(controller_id=binding['controller'], claim_id=binding['claim'],
                    continuity_generation=binding['epoch'], continuity_receipt=binding['receipt'])
    if any(owner.get(key) != item for key, item in expected.items()) or route['controller_id'] != owner['controller_id']:
        raise WorkGraphError('current route scope: stale or foreign graph continuity')
    for key, item in owner.items():
        _native_name(item, 'current route owner.' + key)
    host = _require_object(value['host'], 'current route host')
    _require_exact_members(host, {'host_id', 'host_session_id', 'host_binding_generation', 'host_correlation_id'}, 'current route host')
    for key, item in host.items():
        _native_name(item, 'current route host.' + key)
    if not re.fullmatch('G[0-9A-F]{4}', host['host_binding_generation']):
        raise WorkGraphError('current route scope: invalid host generation')
    scope = _require_object(value['scope'], 'current route scope identity')
    _require_exact_members(scope, {'identity', 'digest'}, 'current route scope identity')
    _native_name(scope['identity'], 'current route scope identity')
    if scope['digest'] != 'sha256:' + _graph_hash({'identity': scope['identity']}):
        raise WorkGraphError('current route scope: contradictory scope digest')
    boundary = _require_object(value['boundary'], 'current route boundary')
    _require_exact_members(boundary, {'kind', 'event_id', 'digest'}, 'current route boundary')
    for key in ('kind', 'event_id'):
        _native_name(boundary[key], 'current route boundary.' + key)
    if boundary['digest'] != 'sha256:' + _graph_hash({k: boundary[k] for k in ('kind', 'event_id')}):
        raise WorkGraphError('current route scope: contradictory boundary digest')
    source = _require_object(value['source'], 'current route source')
    _require_exact_members(source, {'predicate_version', 'record_schema', 'producer_sha256', 'record_sha256'}, 'current route source')
    if (source['predicate_version'] != 'R0033.route-predicate.v1'
            or source['record_schema'] != 'implementaudit.route-decision.v1'
            or type(source['producer_sha256']) is not str
            or source['producer_sha256'] not in _NATIVE_ROUTE_PRODUCER_PROFILES_V1
            or type(source['record_sha256']) is not str
            or not DIGEST_RE.fullmatch(source['record_sha256'])):
        raise WorkGraphError('current route scope: source identity differs')
    for key in ('controller_record_oid', 'record_oid'):
        if type(route[key]) is not str or not COMMIT_RE.fullmatch(route[key]):
            raise WorkGraphError('current route scope: invalid route object identity')
    if route['ref'] != 'refs/implementaudit/route-decisions/' + route['controller_id']:
        raise WorkGraphError('current route scope: foreign route ref')
    for item in (route['record_identity'], route['route_transaction_id'],
                 host['host_correlation_id'], value['expiry_fingerprint']):
        if type(item) is not str or not re.fullmatch('sha256:[0-9a-f]{64}', item):
            raise WorkGraphError('current route scope: malformed canonical identity')
    _native_enum(route['decision'], {'REQUIRED', 'NOT_REQUIRED', 'PENDING'}, 'current route decision')
    allowed_classes = {'REQUIRED': {'MECHANICALLY_REQUIRED', 'JUDGEMENT_REQUIRED'}, 'NOT_REQUIRED': {'MECHANICALLY_NOT_REQUIRED'}, 'PENDING': {'JUDGEMENT_REQUIRED'}}[route['decision']]
    if route['classification'] not in allowed_classes:
        raise WorkGraphError('current route scope: contradictory classification')
    if route['decision'] == 'REQUIRED':
        if type(route['obligation_id']) is not str or not re.fullmatch('sha256:[0-9a-f]{64}', route['obligation_id']):
            raise WorkGraphError('current route scope: invalid obligation')
        _native_enum(route['route_state'], {'UNSATISFIED', 'OPEN', 'RETURNED', 'SATISFIED'}, 'current route state')
    elif route['obligation_id'] is not None or route['route_state'] is not None:
        raise WorkGraphError('current route scope: non-required route owns an obligation')
    if route['route_state'] == 'SATISFIED':
        if type(value['satisfaction']) is not str or not re.fullmatch('sha256:[0-9a-f]{64}', value['satisfaction']):
            raise WorkGraphError('current route scope: immutable acceptance identity absent')
    elif value['satisfaction'] is not None:
        raise WorkGraphError('current route scope: non-satisfied route carries satisfaction')
    return value


def _native_route_scope_module_v1():
    """Fixed sibling source only: no module, path, callback or Boolean override."""
    import stat
    import types
    path = pathlib.Path(__file__).resolve().with_name('route-transaction.py')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode)
                or getattr(before, 'st_file_attributes', 0) & 0x400):
            raise WorkGraphError('native route producer is not a non-aliased regular file')
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or identity(opened) != identity(before):
                raise WorkGraphError('native route producer source identity changed')
            raw = stream.read(max(_NATIVE_ROUTE_PRODUCER_PROFILES_V1.values()) + 1)
            after = os.fstat(stream.fileno())
        named = path.lstat()
    except OSError as exc:
        raise WorkGraphError('native route producer is unavailable') from exc
    if (identity(before) != identity(opened) or identity(opened) != identity(after)
            or identity(after) != identity(named)
            or _NATIVE_ROUTE_PRODUCER_PROFILES_V1.get(hashlib.sha256(raw).hexdigest()) != len(raw)):
        raise WorkGraphError('native route producer source identity changed')
    module = types.ModuleType('_implementaudit_r0035_route_scope_owner')
    module.__file__ = str(path)
    try:
        exec(compile(raw, str(path), 'exec'), module.__dict__)
    except ImportError as exc:
        raise WorkGraphError('native route producer dependency is unavailable or mismatched') from exc
    if not callable(getattr(module, 'read_current_route_scope_v1', None)):
        raise WorkGraphError('native route producer interface is unavailable')
    return module, path, raw


def _native_route_relation_v1(nodes, context, binding, route_scope, source_digest):
    _native_validate_route_scope_v1(route_scope, binding)
    scope = route_scope['scope']['identity']
    direct = {name for name, node in nodes.items() if scope in node['route_scopes']}
    if not direct:
        raise WorkGraphError('current canonical route scope is absent from the graph population')
    affected = set(direct)
    while True:
        expanded = affected | {name for name, node in nodes.items()
            if affected.intersection(node['requires'] + node['optional'])}
        if expanded == affected:
            break
        affected = expanded
    # Match the existing diff owner's ordering: dependency closure first,
    # then ancestry. An invalidated ancestor alone does not change a sibling's
    # input digest or invent an extra dependency edge.
    for name in tuple(affected):
        cursor = nodes[name]['parent']
        while cursor is not None:
            affected.add(cursor)
            cursor = nodes[cursor]['parent']
    scopes = sorted({item for node in nodes.values() for item in node['route_scopes']})
    uncovered = [item for item in scopes if item != scope]
    return {
        'schema': 'implementaudit.route-affected-nodes.v1',
        'owner': 'R0035', 'authority': 'NONE', 'establishes': [],
        'route_scope_digest': route_scope['digest'],
        'route_record_oid': route_scope['route']['record_oid'],
        'obligation_id': route_scope['route']['obligation_id'],
        'route_transaction_id': route_scope['route']['route_transaction_id'],
        'scope': copy.deepcopy(route_scope['scope']),
        'route_state': route_scope['route']['route_state'],
        'satisfaction': route_scope['satisfaction'],
        'graph_generation': binding['epoch'], 'receipt': binding['receipt'],
        'graph_source_digest': source_digest,
        'node_population': sorted(nodes),
        'node_scopes': {name: sorted(node['route_scopes']) for name, node in sorted(nodes.items())},
        'direct_nodes': sorted(direct), 'affected_nodes': sorted(affected),
        'independent_nodes': sorted(set(nodes) - affected),
        'covered_scopes': [scope], 'uncovered_scopes': uncovered,
        'uncovered_nodes': sorted(name for name, node in nodes.items()
            if set(node['route_scopes']).intersection(uncovered)),
        'population_rule': 'ALL_ENUMERATED_NATIVE_SOURCE_NODES',
        'affected_rule': 'DIRECT_SCOPE_THEN_REQUIRED_OPTIONAL_DEPENDENTS_AND_ANCESTORS',
        'context_route_fact_authority': 'CAPTURED_ONLY_NOT_CONSUMED_AS_NATIVE',
    }


def export_native_route_relation_v1(graph):
    """Project the exact owner relation; captured graphs remain captured data."""
    _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    if graph['schema'] != 'implementaudit.native-work-graph.v2':
        raise WorkGraphError('native graph has no owner-backed route relation')
    return _seal_graph(dict(copy.deepcopy(graph['route_relation']), graph_digest=graph['digest']))


def validate_native_route_relation_v1(graph, relation):
    if relation != export_native_route_relation_v1(graph):
        raise WorkGraphError('affected-node relation differs from the complete owner projection')
    return relation


def bind_native_route_relation_v1(graph, canonical_work_graph_bytes):
    """Bind the derivative relation to the existing current WORK_GRAPH owner.

    Dynamic route IDs must never be written into the receipt's own preimage.
    The canonical work graph therefore carries only declared route scopes;
    this post-currentness relation remains a read-only derivative.
    """
    relation = export_native_route_relation_v1(graph)
    canonical = _require_object(decode_strict_json_bytes(canonical_work_graph_bytes, 'WORK_GRAPH.json'), 'WORK_GRAPH.json')
    cells = _validate_graph(canonical)
    actual = {cell['id']: cell for cell in cells}
    nodes = {node['id']: node for node in graph['nodes']}
    if set(actual) != set(nodes):
        raise WorkGraphError('route relation population differs from canonical WORK_GRAPH')
    for name, node in nodes.items():
        cell = actual[name]
        scopes = _native_strings(cell.get('route_scopes'), 'canonical cell route_scopes')
        optional = _native_strings(cell.get('optional_deps', []), 'canonical cell optional_deps')
        if (set(scopes) != set(node['route_scopes']) or set(cell['deps']) != set(node['requires'])
                or set(optional) != set(node['optional'])):
            raise WorkGraphError('route relation scope/dependency binding differs from canonical WORK_GRAPH')
    relation.pop('digest')
    relation['canonical_work_graph_sha256'] = hashlib.sha256(canonical_work_graph_bytes).hexdigest()
    relation['canonical_work_graph_schema'] = canonical['schema']
    return _seal_graph(relation)


def _native_route_block(fact, acquisition, *, scope=None, route_observation=None, binding=None):
    if acquisition == 'NATIVE_CONTINUITY_VERIFIED':
        if route_observation is None:
            return 'ROUTE_PRODUCER_UNAVAILABLE'
        route_scope = _route_observation_value(route_observation)
        if scope != route_scope['scope']['identity']:
            return 'ROUTE_SCOPE_UNCOVERED'
        # Source metadata names scopes only. Dynamic transaction/obligation
        # identities come from the owner AFTER currentness; putting those
        # receipt-derived IDs into STATE would create a digest cycle.
        _native_validate_route_scope_v1(route_scope, binding)
        route = route_scope['route']
        satisfied = route['decision'] == 'NOT_REQUIRED' or route['route_state'] == 'SATISFIED'
        return None if satisfied else 'ROUTE_UNSATISFIED'
    satisfied = fact is not None and (fact['status'] == 'NOT_REQUIRED' or (fact['status'] == 'SATISFIED' and fact['satisfaction'] is not None and (fact['satisfaction'] == fact['expected_satisfaction'])))
    return None if satisfied else 'ROUTE_UNSATISFIED'

def _native_validate_binding(binding, nodes):
    """Validate a complete captured binding, without authenticating its caller.

    Only read_native_run_v1's live continuity gate can acquire native identity.
    A resealable serialized record cannot replace that gate.
    """
    _require_object(binding, 'native binding')
    identity = {'controller', 'claim', 'receipt', 'epoch', 'candidate_head', 'candidate_tree', 'worktree_digest', 'continuity_helper_digest'}
    _require_exact_members(binding, identity | {'acquisition', 'read_set', 'input_root_identity'}, 'native binding')
    _native_enum(binding['acquisition'], {'CONSTRUCTED_FILESYSTEM', 'NATIVE_CONTINUITY_VERIFIED'}, 'native binding.acquisition')
    if binding['acquisition'] == 'CONSTRUCTED_FILESYSTEM':
        if any((binding[key] is not None for key in identity)):
            raise WorkGraphError('native binding: constructed acquisition cannot carry native identity')
    else:
        for key in identity:
            _native_name(binding[key], 'native binding.' + key)
        for key in ('candidate_head', 'candidate_tree'):
            if not re.fullmatch('[0-9a-f]{40}', binding[key]):
                raise WorkGraphError('native binding: invalid Git identity')
        for key in ('worktree_digest', 'continuity_helper_digest'):
            if not DIGEST_RE.fullmatch(binding[key]):
                raise WorkGraphError('native binding: invalid identity digest')
        if not RECEIPT_RE.fullmatch(binding['receipt']):
            raise WorkGraphError('native binding: invalid continuity receipt')
        if binding['epoch'] != binding['receipt'].split('/')[-1].split('@')[0]:
            raise WorkGraphError('native binding: receipt/epoch mismatch')
    if type(binding['input_root_identity']) is not str or not DIGEST_RE.fullmatch(binding['input_root_identity']):
        raise WorkGraphError('native binding: input root identity required')
    reads = _require_object(binding['read_set'], 'native binding.read_set')
    expected = {p for n in nodes.values() for p in n['reads'] + n['invalidators'] if p.startswith('path:')}
    _require_exact_members(reads, expected, 'native binding.read_set')
    for record in reads.values():
        _require_object(record, 'native binding read record')
        _require_exact_members(record, {'status', 'sha256'}, 'native binding read record')
        _native_enum(record['status'], {'MISSING', 'PRESENT_FILE', 'PRESENT_DIRECTORY'}, 'native binding read status')
        if record['status'] == 'MISSING':
            if record['sha256'] is not None:
                raise WorkGraphError('native binding: missing input cannot have a content digest')
        elif type(record['sha256']) is not str or not DIGEST_RE.fullmatch(record['sha256']):
            raise WorkGraphError('native binding: present input needs a content digest')

def _compile_native_documents_v1(snapshot, binding, *, acquire_only=False, _route_observation=None, _completion=None):
    before = copy.deepcopy(binding)
    route_scope = _route_observation_value(_route_observation) if _route_observation is not None else None
    if route_scope is not None:
        _native_validate_route_scope_v1(route_scope, before)
    receiver_binding = _native_receiver_binding_v1(_route_observation) if _route_observation is not None else None
    if route_scope is not None and before.get('acquisition') != 'NATIVE_CONTINUITY_VERIFIED':
        raise WorkGraphError('constructed bindings cannot claim owner route acquisition')
    for path in snapshot:
        if path not in {'STATE.md', 'ROADMAP.md'} and (not re.fullmatch('(?:plans|phases|tasks)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\\.md', path)):
            raise WorkGraphError('native source document path is unsupported')
        if any((part in {'.', '..'} for part in path.split('/'))):
            raise WorkGraphError('native source document path escapes root')
    state = _native_document(snapshot['STATE.md'], 'STATE.md', 'implementaudit.native-state.v1')
    _require_exact_members(state, {'schema', 'campaign', 'root', 'original_scope', 'nodes', 'event', 'context'}, 'native STATE')
    for key in ('campaign', 'root', 'original_scope'):
        _native_name(state[key], 'native STATE.' + key)
    inventory = set(_native_strings(state['nodes'], 'native STATE.nodes'))
    event = _require_object(state['event'], 'native event')
    _require_exact_members(event, {'id', 'kind', 'subject'}, 'native event')
    _native_name(event['id'], 'native event.id')
    _native_enum(event['kind'], {'RETURN', 'JOIN', 'REDERIVE', 'REMINDER', 'INTERRUPTION'}, 'native event.kind')
    _native_name(event['subject'], 'native event.subject')
    _native_validate_context(state['context'])
    roadmap = _native_document(snapshot['ROADMAP.md'], 'ROADMAP.md', 'implementaudit.native-roadmap.v1')
    _require_exact_members(roadmap, {'schema', 'phases'}, 'native ROADMAP')
    phases = set(_native_strings(roadmap['phases'], 'native ROADMAP.phases'))
    nodes = {}
    for path, data in sorted(snapshot.items()):
        if path in {'STATE.md', 'ROADMAP.md'}:
            continue
        document = _native_document(data, path, 'implementaudit.native-spec.v1')
        _require_exact_members(document, {'schema', 'nodes'}, path)
        if type(document['nodes']) is not list or not document['nodes']:
            raise WorkGraphError(f'{path}: nonempty nodes required')
        for value in document['nodes']:
            _native_validate_node(value, path)
            if value['id'] in nodes:
                raise WorkGraphError('native population: duplicate node')
            node = copy.deepcopy(value)
            node['source_path'] = path
            node['source_digest'] = hashlib.sha256(data).hexdigest()
            nodes[node['id']] = node
    if inventory != set(nodes):
        raise WorkGraphError('native population disagrees with complete source enumeration')
    if phases != {n['id'] for n in nodes.values() if n['kind'] == 'PHASE'}:
        raise WorkGraphError('native ROADMAP phase population mismatch')
    if state['root'] not in nodes or event['subject'] not in nodes:
        raise WorkGraphError('native ancestry root/subject missing')
    if nodes[state['root']]['kind'] != 'PLAN':
        raise WorkGraphError('native ancestry root must be a plan')
    for node in nodes.values():
        chain, cursor = (set(), node['id'])
        while cursor is not None:
            if cursor not in nodes or cursor in chain:
                raise WorkGraphError('native ancestry missing or cyclic')
            chain.add(cursor)
            parent = nodes[cursor]['parent']
            if parent is None and cursor != state['root']:
                raise WorkGraphError('native ancestry ends outside campaign root')
            cursor = parent
        for dep in node['requires'] + node['optional']:
            if dep not in nodes or dep == node['id']:
                raise WorkGraphError('native dependency unknown or self-cycle')
        future = node['future_consumer']
        if future is not None and (future['node'] not in nodes or future['node'] == node['id']):
            raise WorkGraphError('native future consumer missing or self-cycle')
    visiting, visited, order = (set(), set(), [])

    def visit(name):
        if name in visiting:
            raise WorkGraphError('native dependency cycle')
        if name in visited:
            return
        visiting.add(name)
        for dep in nodes[name]['requires'] + nodes[name]['optional']:
            visit(dep)
        visiting.remove(name)
        visited.add(name)
        order.append(name)
    try:
        for name in sorted(nodes):
            visit(name)
    except RecursionError as exc:
        raise WorkGraphError('native graph traversal depth exceeded') from exc
    if acquire_only:
        return dict(nodes=[nodes[name] for name in sorted(nodes)])
    _native_validate_binding(before, nodes)
    routes = {f['scope']: f for f in state['context']['route_facts']}
    source_inventory = [dict(path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) for path, data in sorted(snapshot.items())]
    source_digest = _graph_hash(source_inventory)
    route_relation = None if route_scope is None else _native_route_relation_v1(nodes, state['context'], before, route_scope, source_digest)
    held = {d['id']: d for d in state['context']['outstanding_deliveries']}
    for name in order:
        node = nodes[name]
        declared = node['state']
        reasons = []
        if any((nodes[d]['state'] != 'DONE' for d in node['requires'])):
            if declared == 'DONE' and any((nodes[d]['declared_state'] != 'DONE' for d in node['requires'])):
                raise WorkGraphError('native DONE contradicts open required dependency')
            reasons.append('DEPENDENCY')
        if node['authorization'] != 'PERMITTED':
            reasons.append('AUTHORIZATION')
        if node['independence'] != 'KNOWN':
            reasons.append('INDEPENDENCE_UNKNOWN')
        receiver_available = _native_fixed_receiver_matches_v1(node, nodes, route_relation, receiver_binding)
        if node['effect'] in {'MUTATION', 'EXTERNAL'} and not receiver_available:
            reasons.append('EFFECT_EXECUTOR_UNAVAILABLE')
        if node['logical_delivery'] in held:
            reasons.append('LOGICAL_DELIVERY_HELD')
        read_paths = sorted({p for p in node['reads'] + node['invalidators'] if p.startswith('path:')})
        read_set = {p: before['read_set'][p] for p in read_paths}
        if any((record['status'] == 'MISSING' for record in read_set.values())):
            reasons.append('MISSING_INPUT')
        for scope in node['route_scopes']:
            reason = _native_route_block(routes.get(scope), before['acquisition'], scope=scope, route_observation=_route_observation, binding=before)
            if reason is not None:
                reasons.append(reason)
        fact_identity = {key: value for key, value in node.items()}
        node['input_digest'] = _graph_hash(dict(fact=fact_identity, campaign=state['campaign'], original_scope=state['original_scope'], required={d: nodes[d]['input_digest'] for d in node['requires']}, optional={d: nodes[d]['input_digest'] for d in node['optional']}, read_set=read_set, unresolved_semantic_worktree=before['worktree_digest'] if any((not p.startswith('path:') for p in node['reads'] + node['invalidators'])) else None, route_facts=[routes.get(scope) for scope in node['route_scopes']], **({'route_owner': route_scope} if route_scope is not None and route_scope['scope']['identity'] in node['route_scopes'] else {}), **({'receiver_binding': receiver_binding} if receiver_available else {}), delivery=held.get(node['logical_delivery'])))
        completed = declared == 'DONE'
        if _completion is not None:
            result = _completion.get(name, {})
            completed = result.get('status') == 'PASS'
            if declared == 'DONE' and not completed:
                reasons.append('UNBOUND_SOURCE_COMPLETION')
            if result and not completed:
                reasons.append('COMPLETION_' + result['status'])
            node['input_digest'] = _graph_hash([node['input_digest'], {d: _completion.get(d) for d in node['requires'] + node['optional']}])
        node['declared_state'] = declared
        node['state'] = 'ACTIVE' if declared == 'ACTIVE' else 'BLOCKED' if reasons else 'DONE' if completed else 'READY'
        node['blocked_reasons'] = sorted(set(reasons))
    before['source_digest'] = source_digest
    return _seal_graph(dict(schema='implementaudit.completion-projection.v1' if _completion is not None else 'implementaudit.native-work-graph.v2' if route_scope is not None else 'implementaudit.native-work-graph.v1', **({'route_scope': route_scope, 'route_relation': route_relation} if route_scope is not None else {}), **({'receiver_binding': receiver_binding} if receiver_binding is not None else {}), binding=before, campaign=state['campaign'], root=state['root'], original_scope=state['original_scope'], event=event, context=state['context'], source_inventory=source_inventory, source_documents={path: data.decode('utf-8') for path, data in snapshot.items()}, nodes=[nodes[name] for name in sorted(nodes)], population={s: sum((n['state'] == s for n in nodes.values())) for s in KNOWN_STATES}, authority='NONE'))

def _native_input_policy_v1(owner, root, relative, git_policy):
    reason = owner._repository_path_policy(relative)
    if reason is not None:
        raise WorkGraphError('native declared input policy refused: ' + reason)
    if git_policy:
        # One literal path, quiet bounded output, isolated Git configuration.
        # --no-index also covers ignored files that happen to be tracked.
        result = owner._run_git(root, 'check-ignore', '--no-index', '--quiet', '--',
            relative, text=False, allowed_returncodes=(0, 1))
        if result.returncode == 0:
            raise WorkGraphError('native declared input policy refused: git-ignored-path')


def _acquire_native_read_set(nodes, input_root):
    import stat
    owner, owner_path, owner_raw = _native_static_owner_module_v1()
    root = pathlib.Path(input_root).absolute()
    git_policy = (root / '.git').exists() or (root / '.git').is_symlink()
    budget = dict(entries=0, maximum_entries=NATIVE_READ_MAX_ENTRIES, remaining=NATIVE_READ_MAX_TOTAL_BYTES)
    _native_static_directory_v1(owner, root, budget)
    paths = sorted({p for n in nodes for p in n['reads'] + n['invalidators'] if p.startswith('path:')})
    _native_semantics(paths, 'native read set')
    if len(paths) > NATIVE_READ_MAX_ENTRIES:
        raise WorkGraphError('native declared read population bound exceeded')
    result = {}
    for identity in paths:
        _native_input_policy_v1(owner, root, identity[5:], git_policy)
        path = root.joinpath(*pathlib.PurePosixPath(identity[5:]).parts)
        try:
            info = path.lstat()
        except FileNotFoundError:
            # A missing leaf is allowed only behind a physically acquired parent.
            parent = path.parent
            while True:
                try:
                    parent.lstat()
                    break
                except FileNotFoundError:
                    parent = parent.parent
            _native_static_directory_v1(owner, parent, budget)
            result[identity] = dict(status='MISSING', sha256=None)
            continue
        if stat.S_ISREG(info.st_mode):
            raw, mode = _native_static_file_v1(owner, path, NATIVE_READ_MAX_FILE_BYTES, budget)
            result[identity] = dict(status='PRESENT_FILE', sha256=_graph_hash([mode, hashlib.sha256(raw).hexdigest()]))
        elif stat.S_ISDIR(info.st_mode):
            members = []
            stack = [(path, 0)]
            root_mode = None
            while stack:
                directory, depth = stack.pop()
                if depth > NATIVE_STATIC_MAX_DEPTH:
                    raise WorkGraphError('native input directory depth bound exceeded')
                rows, directory_mode = _native_static_directory_v1(owner, directory, budget)
                if root_mode is None:
                    root_mode = directory_mode
                for name, is_directory, mode in rows:
                    member = directory / name
                    _native_input_policy_v1(owner, root, member.relative_to(root).as_posix(), git_policy)
                    relative = member.relative_to(path).as_posix()
                    if is_directory:
                        members.append([relative, 'DIRECTORY', mode])
                        stack.append((member, depth + 1))
                    else:
                        raw, mode = _native_static_file_v1(owner, member, NATIVE_READ_MAX_FILE_BYTES, budget)
                        members.append([relative, mode, hashlib.sha256(raw).hexdigest()])
            result[identity] = dict(status='PRESENT_DIRECTORY', sha256=_graph_hash([root_mode, sorted(members)]))
        else:
            raise WorkGraphError('native input is not a regular non-aliased file or directory')
    _, final_path, final_raw = _native_static_owner_module_v1()
    if final_path != owner_path or final_raw != owner_raw:
        raise WorkGraphError('native static source owner changed during input acquisition')
    return result

# Explicitly constructed intake preserves the self-contained R0035 diagnostic.
# These original portable readers acquire no repository/native currentness. They
# are selected only when repo_root is absent, never after a native-owner refusal.
def _constructed_source_snapshot_v1(run_root):
    root = pathlib.Path(run_root)
    if root.is_symlink() or not root.is_dir():
        raise WorkGraphError('native source root is missing or a symlink')
    files = [root / 'STATE.md', root / 'ROADMAP.md']
    for name in ('plans', 'phases', 'tasks'):
        directory = root / name
        if directory.is_symlink():
            raise WorkGraphError('native source directory is a symlink')
        if not directory.exists():
            continue
        for base, dirs, names in os.walk(directory, followlinks=False):
            for item in dirs + names:
                if (pathlib.Path(base) / item).is_symlink():
                    raise WorkGraphError('native source contains a symlink')
            files.extend((pathlib.Path(base) / n for n in names if n.endswith('.md')))
    result = {}
    for path in sorted(files):
        if path.is_symlink() or not path.is_file():
            raise WorkGraphError(f'native source missing or symlink: {path.name}')
        try:
            result[path.relative_to(root).as_posix()] = path.read_bytes()
        except OSError as exc:
            raise WorkGraphError(f'native source unreadable: {path.name}') from exc
    return result


def _acquire_constructed_read_set_v1(nodes, input_root):
    root = pathlib.Path(input_root).resolve()
    result = {}
    paths = sorted({p for n in nodes for p in n['reads'] + n['invalidators'] if p.startswith('path:')})
    _native_semantics(paths, 'native read set')
    for identity in paths:
        relative = pathlib.PurePosixPath(identity[5:])
        path = root.joinpath(*relative.parts)
        for count in range(1, len(relative.parts) + 1):
            if root.joinpath(*relative.parts[:count]).is_symlink():
                raise WorkGraphError('native input symlink is unsupported')
        if not path.exists():
            result[identity] = dict(status='MISSING', sha256=None)
        elif path.is_file():
            result[identity] = dict(status='PRESENT_FILE', sha256=_graph_hash([path.stat().st_mode & 4095, hashlib.sha256(path.read_bytes()).hexdigest()]))
        elif path.is_dir():
            members = []
            for base, dirs, names in os.walk(path, followlinks=False):
                for name in sorted(dirs + names):
                    member = pathlib.Path(base) / name
                    if member.is_symlink():
                        raise WorkGraphError('native input directory contains symlink')
                    if member.is_dir():
                        members.append([member.relative_to(path).as_posix(), 'DIRECTORY', member.stat().st_mode & 4095])
                    elif member.is_file():
                        members.append([member.relative_to(path).as_posix(), member.stat().st_mode & 4095, hashlib.sha256(member.read_bytes()).hexdigest()])
                    else:
                        raise WorkGraphError('native input contains non-regular file')
            result[identity] = dict(status='PRESENT_DIRECTORY', sha256=_graph_hash([path.stat().st_mode & 4095, sorted(members)]))
        else:
            raise WorkGraphError('native input is not a regular file or directory')
    return result



@contextlib.contextmanager
def observe_native_run_v1(run_root, repo_root=None, *, input_root=None, expected_current=None,
                          _continuity_sources=None, _episode_outputs=None, _continuity_closures=None):
    """Hold the existing native owner checks around a caller's read-only use.

    Omitting repo_root is explicitly constructed filesystem evidence. Supplying
    it requires the genuine existing continuity owner before AND after intake.
    Neither path authenticates physical host capacity or effect capabilities.
    Only immutable projection bytes are yielded; all terminal guards execute
    after use, before the enclosing observation can be accepted. An optional
    corroborating current tuple is a constraint rechecked by R0033, never facts
    supplied in place of acquisition. Retained PENDING requests may be stale.
    """
    read_sources = _constructed_source_snapshot_v1 if repo_root is None else _native_source_snapshot
    read_inputs = _acquire_constructed_read_set_v1 if repo_root is None else _acquire_native_read_set
    source_output = {} if _continuity_sources is None else {'_source_reads': _continuity_sources}
    if _continuity_closures is not None:
        source_output['_closure_reads'] = _continuity_closures
    current_reads = []
    if _episode_outputs is not None:
        source_output['_current_reads'] = current_reads
    before = _native_continuity(repo_root, run_root, **source_output) if repo_root is not None else dict(acquisition='CONSTRUCTED_FILESYSTEM', controller=None, claim=None, receipt=None, epoch=None, candidate_head=None, candidate_tree=None, worktree_digest=None, continuity_helper_digest=None)
    snapshot = read_sources(run_root)
    preliminary = _compile_native_documents_v1(snapshot, before, acquire_only=True)
    input_root = pathlib.Path(input_root if input_root is not None else repo_root if repo_root is not None else run_root)
    read_set = read_inputs(preliminary['nodes'], input_root)
    bound = dict(before, read_set=read_set, input_root_identity=hashlib.sha256(os.fsencode(str(input_root.resolve()))).hexdigest())
    route_observation = None
    producer = None
    # Route absence retains the existing v1 unavailable result. A present
    # producer must satisfy the fixed source pin; caller facts cannot enable it.
    route_source = pathlib.Path(__file__).resolve().with_name('route-transaction.py')
    route_available = False
    if repo_root is not None and any(node['route_scopes'] for node in preliminary['nodes']):
        try:
            route_source.lstat()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise WorkGraphError('native route producer is unavailable') from exc
        else:
            route_available = True
    combined_route_read = False
    shared_currentness = False
    receiver_binding = None
    with contextlib.ExitStack() as owner_read:
        if expected_current is not None and not route_available:
            raise WorkGraphError('current corroboration requires the native route owner')
        if route_available:
            producer, producer_path, producer_raw = _native_route_scope_module_v1()
            transaction = getattr(producer, 'current_route_observation_v1', None)
            shared = getattr(producer, '_observe_current_route_from_owner_v1', None)
            if current_reads and shared is not None:
                if len(current_reads) != 1 or not callable(shared):
                    raise WorkGraphError('native actual-currentness composition is malformed')
                def close_currentness():
                    if _native_continuity(repo_root, run_root, **source_output) != before or len(current_reads) != 2:
                        raise WorkGraphError('native continuity changed during intake')
                    return producer._current_controller_from_owner_read_v1(pathlib.Path(repo_root), before['controller'],
                        current_reads[1]['controller_result'], current_reads[1]['receipt'])
                transaction = lambda repo, controller, **kw: shared(repo, controller, current_reads[0],
                    kw.get('expected_current'), close_currentness)
                shared_currentness = True
            if transaction is not None:
                if not callable(transaction):
                    raise WorkGraphError('native route transaction interface is malformed')
                # This callable comes only from the fixed, byte-verified sibling
                # owner. No caller callback/module or serialized witness enters.
                corroboration = {} if expected_current is None else {'expected_current': expected_current}
                observed = owner_read.enter_context(transaction(pathlib.Path(repo_root), before['controller'], **corroboration))
                acquired_bytes = observed.scope_bytes()
                if type(acquired_bytes) is not bytes:
                    raise WorkGraphError('native route transaction did not yield immutable bytes')
                acquired_route = decode_strict_json_bytes(acquired_bytes, 'native route transaction scope')
                receiver_reader = getattr(observed, 'ordinary_receiver_binding_bytes', None)
                if receiver_reader is not None:
                    if not callable(receiver_reader):
                        raise WorkGraphError('native receiver binding interface is malformed')
                    receiver_bytes = receiver_reader()
                    if type(receiver_bytes) is not bytes:
                        raise WorkGraphError('native receiver binding is not immutable bytes')
                    receiver_binding = decode_strict_json_bytes(receiver_bytes, 'native receiver binding')
                combined_route_read = True
            else:
                if expected_current is not None:
                    raise WorkGraphError('current corroboration requires the enclosing route interface')
                acquired_route = producer.read_current_route_scope_v1(pathlib.Path(repo_root), before['controller'])
            if pathlib.Path(acquired_route['owner']['explicit_run_root']).resolve() != pathlib.Path(run_root).resolve():
                raise WorkGraphError('route producer returned a foreign run root')
            _native_validate_route_scope_v1(acquired_route, before)
            route_observation = _RouteScopeObservation(acquired_route, _NATIVE_ROUTE_OBSERVATION_KEY,
                                                       receiver_binding=receiver_binding)
        projection = _compile_native_documents_v1(snapshot, bound, _route_observation=route_observation)
        projection_raw = json.dumps(projection, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode('utf-8')
        with contextlib.ExitStack() as episode_read:
            episode = None
            if _episode_outputs is not None and receiver_binding is not None and combined_route_read:
                # Source pins were derived by the live R0033 owner from the
                # accepted mission. No caller source, module or fact enables it.
                source_owner = episode_read.enter_context(producer._ordinary_fixed_source_owner_v2(
                    pathlib.Path(repo_root), receiver_binding['source_pins']))
                policy = source_owner.ordinary_policy_v1()
                if (policy != receiver_binding['policy'] or
                        policy.get('code_pins', {}).get('implementaudit/scripts/compile-work-graph.py') !=
                        hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()):
                    raise WorkGraphError('native episode policy differs from the current receiver binding')
                actual_owner = dict(repository=str(pathlib.Path(repo_root).absolute()), controller=before['controller'],
                    module_pin=dict(path=str(producer_path), bytes=len(producer_raw), sha256=hashlib.sha256(producer_raw).hexdigest()))
                raw = episode_read.enter_context(source_owner._ordinary_episode_observation_v1((observed, projection_raw, actual_owner)))
                if type(raw) is not bytes:
                    raise WorkGraphError('native episode owner did not yield immutable bytes')
                episode = decode_strict_json_bytes(raw, 'native ordinary episode')
            if _episode_outputs is not None:
                _episode_outputs.append(episode)
            yield projection_raw
            if episode is not None:
                if source_owner.ordinary_policy_v1() != policy:
                    raise WorkGraphError('native episode policy changed during observation')
                # Unavailable branches retain their complete original fresh
                # acquisition; only a real AVAILABLE episode shares the live read.
                if episode['status'] != 'AVAILABLE' and source_owner.acquire_selected_ordinary_episode_v1() != episode:
                    raise WorkGraphError('native episode availability changed during observation')
        if route_observation is not None and _route_observation_value(route_observation) != acquired_route:
            raise WorkGraphError('provisional native route observation was mutated')
        if route_observation is not None and route_observation.receiver_binding != receiver_binding:
            raise WorkGraphError('provisional native receiver binding was mutated')
        if read_sources(run_root) != snapshot:
            raise WorkGraphError('native source changed during intake')
        if read_inputs(projection['nodes'], input_root) != read_set:
            raise WorkGraphError('native inputs changed during intake')
        if repo_root is not None and not shared_currentness and _native_continuity(repo_root, run_root, **source_output) != before:
            raise WorkGraphError('native continuity changed during intake')
        if producer is not None and not combined_route_read:
            if producer.read_current_route_scope_v1(pathlib.Path(repo_root), before['controller']) != acquired_route:
                raise WorkGraphError('native route changed during intake')
        # Every projection remains provisional until the owner context exits;
        # it freshly checks semantic inputs/receipts/refs and rejects mutation.
    if producer is not None:
        _, final_path, final_raw = _native_route_scope_module_v1()
        if final_path != producer_path or final_raw != producer_raw:
            raise WorkGraphError('native route producer changed during intake')


@contextlib.contextmanager
def _observe_native_sources_v2(run_root, repo_root, input_root, expected_current, *, version, episode):
    """Private envelope composition; every sink is created by this owner."""
    if repo_root is None:
        raise WorkGraphError('native source observation requires actual repository continuity')
    sources, episodes, closures = [], [], []
    with observe_native_run_v1(run_root, repo_root, input_root=input_root,
            expected_current=expected_current, _continuity_sources=sources,
            _episode_outputs=episodes if episode else None,
            _continuity_closures=closures if version == 2 else None) as raw:
        if (len(sources) != 1 or (version == 2 and len(closures) != 1) or (episode and len(episodes) != 1) or
                set(sources[0]) != {'claim_sha256', 'validate_sha256'} or
                any(type(v) is not str or not DIGEST_RE.fullmatch(v) for v in sources[0].values())):
            raise WorkGraphError('native executed-source observation is absent or malformed')
        if version == 1 and (sources[0]['claim_sha256'], sources[0]['validate_sha256']) not in (_NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE, _NATIVE_COMBINED_CURRENT_PAIR_V1):
            raise WorkGraphError('complete continuity composition requires the v2 source observation')
        graph = decode_strict_json_bytes(raw, 'native source observation projection')
        if graph['binding']['continuity_helper_digest'] != sources[0]['claim_sha256']:
            raise WorkGraphError('native projection differs from executed continuity source')
        label = 'episode-source' if episode else 'source'
        value = dict(schema=f'implementaudit.native-run-{label}-observation.v{version}',
                     projection=graph, continuity_sources=dict(sources[0]))
        if version == 2:
            value['continuity_closure'] = closures[0]
        if episode:
            value['ordinary_episode'] = episodes[0]
        yield json.dumps(value, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    if len(sources) != 2 or sources[1] != sources[0]:
        raise WorkGraphError('native executed continuity sources changed during observation')
    if version == 2 and (len(closures) != 2 or closures[1] != closures[0]):
        raise WorkGraphError('native executed continuity closure changed during observation')


@contextlib.contextmanager
def observe_native_run_sources_v1(run_root, repo_root, *, input_root=None, expected_current=None):
    """Retain the exact historical two-source envelope; six sources require v2."""
    with _observe_native_sources_v2(run_root, repo_root, input_root, expected_current,
                                   version=1, episode=False) as raw:
        yield raw


@contextlib.contextmanager
def observe_native_run_episode_sources_v1(run_root, repo_root, *, input_root=None, expected_current=None):
    """Retain the historical episode envelope for its two-source composition."""
    with _observe_native_sources_v2(run_root, repo_root, input_root, expected_current,
                                   version=1, episode=True) as raw:
        yield raw


@contextlib.contextmanager
def observe_native_run_sources_v2(run_root, repo_root, *, input_root=None, expected_current=None):
    """Observe the complete executed source closure, provisional until exit."""
    with _observe_native_sources_v2(run_root, repo_root, input_root, expected_current,
                                   version=2, episode=False) as raw:
        yield raw


@contextlib.contextmanager
def observe_native_run_episode_sources_v2(run_root, repo_root, *, input_root=None, expected_current=None):
    """Observe graph, complete continuity closure and ordinary episode together."""
    with _observe_native_sources_v2(run_root, repo_root, input_root, expected_current,
                                   version=2, episode=True) as raw:
        yield raw


def read_native_run_v1(run_root, repo_root=None, *, input_root=None):
    """Return a projection only after the complete native observation closes."""
    with observe_native_run_v1(run_root, repo_root, input_root=input_root) as raw:
        projection = decode_strict_json_bytes(raw, 'native run observation')
    return projection

def _semantic_overlap(left, right):
    for a in left:
        for b in right:
            if a == b or (a.startswith('path:') and b.startswith('path:') and (a.startswith(b + '/') or b.startswith(a + '/'))):
                return True
    return False

def _bounded_selection_v1(candidates, active, capacity, *, semantic=False):
    """One bounded selection loop shared by the recovered and native routes."""
    occupied = sum((max(1, int(c['resource_demand'])) for c in active))
    free = max(0, capacity - occupied)
    selected, deferred, holds, remaining = ([], {}, list(active), free)
    overlap = _semantic_overlap if semantic else lambda a, b: bool(set(a) & set(b))

    def resources(cell):
        if 'resources' in cell:
            return cell['resources'] + cell.get('acceptance', []) + cell.get('authority', [])
        return [] if cell['resource_boundary'] == 'NONE' else [cell['resource_boundary']]
    for cell in sorted(candidates, key=lambda item: (-int(item['rank']), str(item['id']))):
        demand = max(1, int(cell['resource_demand']))
        conflict = any((overlap(cell['writes'], old['writes']) or overlap(cell['writes'], old.get('reads', [])) or overlap(cell.get('reads', []), old['writes']) or overlap(resources(cell), resources(old)) for old in holds))
        reason = 'CONFLICT' if conflict else 'CAPACITY' if demand > remaining else None
        if reason:
            deferred[str(cell['id'])] = reason
            continue
        selected.append(str(cell['id']))
        remaining -= demand
        holds.append(cell)
    return (selected, deferred, occupied, free)

def cheap_path_v1(total_cells, ready_cells, capacity):
    for name, value in (('total', total_cells), ('ready', ready_cells), ('capacity', capacity)):
        _native_int(value, name)
    if ready_cells > total_cells:
        raise WorkGraphError('cheap path census contradiction')
    graph_required = total_cells >= 3 and ready_cells >= 2 and (capacity >= 2)
    return dict(graph_required=graph_required, mode='GRAPH_CANDIDATE' if graph_required else 'CHEAP_SERIAL', authority='NONE')

def select_native_frontier_v1(graph):
    _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    return _select_native_frontier_v1(graph)

def _select_native_frontier_v1(graph):
    context = graph['context']
    capacity = max(0, context['host_capacity'] - context['reserve'])
    if context['operator_ceiling'] is not None:
        capacity = min(capacity, context['operator_ceiling'])
    nodes = graph['nodes']
    active = [n for n in nodes if n['state'] == 'ACTIVE']
    candidates, placements, value_deferred = ([], {}, {})
    for node in nodes:
        if node['state'] != 'READY' or node['kind'] not in {'TASK', 'JOIN'}:
            continue
        costs = node['context']
        choices = []
        if costs['locality'] in {'GOVERNOR', 'EITHER'}:
            choices.append((costs['governor_cost'], 'GOVERNOR'))
        if costs['locality'] in {'CHILD', 'EITHER'}:
            choices.append((costs['child_cost'] + costs['return_cost'], 'DELEGATED_EXECUTOR_CANDIDATE'))
        cost, placement = min(choices)
        if cost > costs['useful_value']:
            value_deferred[node['id']] = 'CONTEXT_COST'
            continue
        placements[node['id']] = placement
        candidates.append(node)
    selected, deferred, occupied, free = _bounded_selection_v1(candidates, active, capacity, semantic=True)
    deferred.update(value_deferred)
    identity = _graph_hash([graph['digest'], graph['event'], selected])
    mode = cheap_path_v1(sum((n['kind'] in {'TASK', 'JOIN'} for n in nodes)), len(candidates), free)
    return dict(schema='implementaudit.native-dispatch.v1', graph_digest=graph['digest'], event=copy.deepcopy(graph['event']), dispatch_id=identity, selected=selected, inputs={n['id']: n['input_digest'] for n in nodes if n['id'] in selected}, capacity=capacity, active_occupancy=occupied, free_capacity=free, deferred=dict(sorted(deferred.items())), blocked={n['id']: n['blocked_reasons'] for n in nodes if n['state'] == 'BLOCKED'}, placements={name: placements[name] for name in selected}, mode=mode['mode'], graph_required=mode['graph_required'], authority='NONE')

def derive_completion_frontier_v1(graph, outcomes):
    """Pure contract overlay, never accepted-result custody or dispatch authority."""
    _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    _require_object(outcomes, 'completion outcomes')
    nodes = {n['id']: n for n in graph['nodes']}
    for name, value in outcomes.items():
        if name not in nodes or nodes[name]['kind'] not in {'TASK', 'JOIN'}:
            raise WorkGraphError('completion cannot grant ancestor or foreign scope')
        _require_object(value, 'completion outcome')
        _require_exact_members(value, {'status', 'digest'}, 'completion outcome')
        _native_enum(value['status'], {'PASS', 'FAIL', 'PARTIAL', 'NONVERDICT', 'UNKNOWN', 'PENDING', 'INTERRUPTED', 'TRANSPORT_FAILURE', 'RECOVERY_CUSTODY_UNVERIFIED'}, 'completion status')
        _require_digest(value['digest'], 'completion digest')
    projection = _replay_native_graph_v1(graph, outcomes)
    dispatch = _select_native_frontier_v1(projection)
    dispatch.update(schema='implementaudit.completion-frontier.v1', source_graph_digest=graph['digest'], states={n['id']: n['state'] for n in projection['nodes']}, native_dispatch_authorized=False)
    return dispatch

def diff_native_graphs_v1(previous, current):
    for graph in (previous, current):
        _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    old, new = ({n['id']: n for n in g['nodes']} for g in (previous, current))
    global_keys = ('acquisition', 'controller', 'claim', 'receipt', 'epoch', 'candidate_head', 'candidate_tree', 'continuity_helper_digest', 'input_root_identity')
    global_change = any((previous['binding'][key] != current['binding'][key] for key in global_keys))
    changed = {name for name in old.keys() | new.keys() if name not in old or name not in new or old[name]['input_digest'] != new[name]['input_digest'] or global_change}
    for name in list(changed):
        for source in (old, new):
            cursor = source.get(name, {}).get('parent')
            while cursor is not None:
                changed.add(cursor)
                cursor = source[cursor]['parent']
    return dict(invalidated=sorted(changed), preserved=sorted((old.keys() & new.keys()) - changed), removed=sorted(old.keys() - new.keys()), added=sorted(new.keys() - old.keys()), recompute_required=previous['digest'] != current['digest'], authority='NONE')

def reconcile_native_results_v1(dispatched_graph, current_graph, dispatch, results, join_id):
    """Read-only result normalization. Current graph must be freshly reacquired
    by the consumer; a supplied hash is not native currentness authentication.
    """
    for graph in (dispatched_graph, current_graph):
        _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    if dispatch != select_native_frontier_v1(dispatched_graph):
        raise WorkGraphError('dispatch differs from exact derived selection')
    nodes = {n['id']: n for n in dispatched_graph['nodes']}
    if join_id not in nodes or nodes[join_id]['kind'] != 'JOIN':
        raise WorkGraphError('unknown JOIN consumer')
    join = nodes[join_id]
    required, optional = (set(join['requires']), set(join['optional']))
    if type(results) is not list:
        raise WorkGraphError('results: array required')
    mapped = {}
    statuses = {'PASS', 'FAIL', 'PARTIAL', 'NONVERDICT', 'UNKNOWN', 'PENDING', 'INTERRUPTED', 'TRANSPORT_FAILURE'}
    fields = {'schema', 'node', 'dispatch_id', 'graph_digest', 'input_digest', 'status', 'terminal', 'exit_code', 'evidence_digest', 'independence_key', 'scope'}
    for result in results:
        _require_object(result, 'result')
        _require_exact_members(result, fields, 'result')
        if result['schema'] != 'implementaudit.work-result.v1':
            raise WorkGraphError('result: unknown schema')
        name = result['node']
        if name not in nodes or name not in dispatch['selected'] or name not in required | optional:
            raise WorkGraphError('result: unknown or undispatched contributor')
        if name in mapped:
            raise WorkGraphError('result: duplicate contributor')
        if result['dispatch_id'] != dispatch['dispatch_id'] or result['graph_digest'] != dispatched_graph['digest'] or result['input_digest'] != nodes[name]['input_digest']:
            raise WorkGraphError('result: stale graph/dispatch/source identity')
        _native_enum(result['status'], statuses, 'result.status')
        _require_bool(result['terminal'], 'result.terminal')
        if result['exit_code'] is not None:
            _native_int(result['exit_code'], 'result.exit_code', INT64_MIN)
        if result['evidence_digest'] is not None and (type(result['evidence_digest']) is not str or not DIGEST_RE.fullmatch(result['evidence_digest'])):
            raise WorkGraphError('result: invalid evidence digest')
        _native_name(result['independence_key'], 'result.independence_key')
        if _native_strings(result['scope'], 'result.scope') != [name]:
            raise WorkGraphError('result: scope cannot grant whole-parent credit')
        if result['status'] == 'PASS' and (not result['terminal'] or result['exit_code'] != 0 or result['evidence_digest'] is None):
            raise WorkGraphError('result: contradictory PASS envelope')
        if result['status'] == 'PENDING' and result['terminal']:
            raise WorkGraphError('result: contradictory terminal PENDING')
        mapped[name] = result
    delta = diff_native_graphs_v1(dispatched_graph, current_graph)
    if delta['recompute_required']:
        return dict(status='RECOMPUTE_REQUIRED', **delta)
    return _join_native_results_v1(current_graph, mapped, join_id)

def _join_native_results_v1(graph, mapped, join_id):
    nodes = {n['id']: n for n in graph['nodes']}
    join = nodes[join_id]
    required, optional = set(join['requires']), set(join['optional'])
    missing = sorted(required - mapped.keys())
    all_settled = not missing and all((mapped[name]['terminal'] for name in required))
    status = 'PENDING'
    if all_settled:
        if any((mapped[name]['status'] in {'FAIL', 'TRANSPORT_FAILURE'} for name in required)):
            status = 'FAIL'
        elif any((mapped[name]['status'] != 'PASS' for name in required)):
            status = 'NONVERDICT'
        else:
            status = 'SATISFIED_AT_DECLARED_RESULT_CONTRACT'
        if join['independent_results']:
            keys = [mapped[name]['independence_key'] for name in required]
            evidence = [mapped[name]['evidence_digest'] for name in required]

            def sources(name):
                closure, pending = (set(), [name])
                while pending:
                    item = pending.pop()
                    if item in closure:
                        continue
                    closure.add(item)
                    pending.extend(nodes[item]['requires'] + nodes[item]['optional'])
                reads = [p for item in closure for p in nodes[item]['reads'] + nodes[item]['invalidators']]
                evidence = {nodes[item]['done_evidence'] for item in closure if nodes[item]['done_evidence'] is not None}
                return (closure, reads, evidence)
            closures = {name: sources(name) for name in required}
            common = any((bool(closures[a][0] & closures[b][0]) or _semantic_overlap(closures[a][1], closures[b][1]) or bool(closures[a][2] & closures[b][2]) for a in required for b in required if a < b))
            if len(set(keys)) != len(keys) or (None not in evidence and len(set(evidence)) != len(evidence)) or common:
                status = 'NONVERDICT' if status != 'FAIL' else status
    return dict(schema='implementaudit.native-join.v1', status=status, all_required_settled=all_settled, required=sorted(required), optional=sorted(optional), missing=missing, omitted_optional=sorted(optional - mapped.keys()), retained_scopes={name: result['scope'] for name, result in sorted(mapped.items())}, graph_digest=graph['digest'], consumer=join_id, authority='NONE', lifecycle_credit='NONE')

def _recursive_context_v1(graph, plan, subject):
    nodes = {n['id']: n for n in graph['nodes']}
    ancestors, cursor = ([], subject)
    while cursor is not None:
        ancestors.append(cursor)
        cursor = nodes[cursor]['parent']
    if ancestors[-1] != graph['root']:
        raise WorkGraphError('recursive ancestry root mismatch')
    consumers = {}
    for name in plan['selected']:
        node = nodes[name]
        consumers[name] = node['future_consumer'] or dict(node=node['parent'] or graph['root'], condition='scoped result reconsideration')
    directions = {'INWARD': sorted((n['id'] for n in graph['nodes'] if n['parent'] == ancestors[0])), 'OUTWARD': sorted((n['id'] for n in graph['nodes'] if n['parent'] in ancestors[1:] and n['id'] not in ancestors)), 'FORWARD': sorted((n['id'] for n in graph['nodes'] if n['future_consumer'] is not None)), 'BACKWARD': sorted((n['id'] for n in graph['nodes'] if n['kind'] == 'JOIN'))}
    return dict(plan, schema='implementaudit.recursive-transition.v1', campaign=graph['campaign'], root=graph['root'], original_scope=graph['original_scope'], ancestors=ancestors, directions=directions, consumers=consumers)

def compile_recursive_transition_v1(graph, history):
    _check_graph_seal(graph, 'implementaudit.native-work-graph.v1')
    if type(history) is not list:
        raise WorkGraphError('event history: array required')
    plan = select_native_frontier_v1(graph)
    result = _recursive_context_v1(graph, plan, graph['event']['subject'])
    seen = set()
    replay = False
    for receipt in history:
        _require_object(receipt, 'event receipt')
        fields = {'event_id', 'graph_digest', 'dispatch_id', 'consumed'}
        _require_exact_members(receipt, fields | ({'source_graph'} if 'source_graph' in receipt else set()), 'event receipt')
        _native_name(receipt['event_id'], 'event receipt identity')
        _native_strings(receipt['consumed'], 'event receipt consumed')
        for key in ('graph_digest', 'dispatch_id'):
            if type(receipt[key]) is not str or not DIGEST_RE.fullmatch(receipt[key]):
                raise WorkGraphError('event receipt digest required')
        if receipt['event_id'] in seen:
            raise WorkGraphError('duplicate event receipt')
        seen.add(receipt['event_id'])
        if 'source_graph' in receipt:
            prior = receipt['source_graph']
            prior_plan = select_native_frontier_v1(prior)
            if receipt['event_id'] != prior['event']['id'] or receipt['graph_digest'] != prior['digest'] or receipt['dispatch_id'] != prior_plan['dispatch_id'] or (receipt['consumed'] != prior_plan['selected']):
                raise WorkGraphError('event receipt differs from source-derived complete consumption')
            if graph['event']['kind'] == 'REMINDER' and receipt['consumed'] == plan['selected'] and (prior['event']['subject'] == graph['event']['subject']) and all((prior[k] == graph[k] for k in ('campaign', 'root', 'original_scope', 'context'))) and (not diff_native_graphs_v1(prior, graph)['invalidated']):
                replay = True
        elif receipt['event_id'] != graph['event']['id'] and graph['event']['kind'] == 'REMINDER' and set(receipt['consumed']) & set(plan['selected']):
            raise WorkGraphError('unchanged reminder consumption is unbound without its source graph')
        if receipt['event_id'] == graph['event']['id']:
            if receipt['graph_digest'] != graph['digest'] or receipt['dispatch_id'] != plan['dispatch_id'] or receipt['consumed'] != plan['selected']:
                raise WorkGraphError('event identity reused with changed graph or incomplete consumption')
            replay = True
    if replay:
        result.update(selected=[], mode='NO_REDISPATCH')
    return _seal_graph(result)

def check_recursive_execution_v1(graph, history, transition, executions, consumptions):
    """Consume source-bound records, not a caller-resealed population.

    The pure checker does not attest process execution or native history
    custody. Actual portable consumers must inspect their output bytes; native
    callers additionally need the current governor's accepted-result custody.
    """
    _check_graph_seal(transition, 'implementaudit.recursive-transition.v1')
    if transition != compile_recursive_transition_v1(graph, history):
        raise WorkGraphError('recursive transition differs from source-derived graph/history')
    if type(executions) is not list or type(consumptions) is not list:
        raise WorkGraphError('execution and consumption arrays required')
    expected = set(transition['selected'])
    nodes = {n['id']: n for n in graph['nodes']}
    done, used = ({}, {})
    for record in executions:
        _require_object(record, 'execution')
        _require_exact_members(record, {'node', 'dispatch_id', 'graph_digest', 'input_digest', 'input_root_identity', 'read_set', 'output_digest', 'exit_code'}, 'execution')
        if record['node'] not in expected or record['node'] in done:
            raise WorkGraphError('unknown or duplicate execution')
        if record['dispatch_id'] != transition['dispatch_id'] or type(record['exit_code']) is not int or record['exit_code'] != 0:
            raise WorkGraphError('stale or failed execution')
        node = nodes[record['node']]
        reads = {p: graph['binding']['read_set'][p] for p in node['reads'] + node['invalidators'] if p.startswith('path:')}
        if record['graph_digest'] != graph['digest'] or record['input_digest'] != node['input_digest'] or record['input_root_identity'] != graph['binding']['input_root_identity'] or (record['read_set'] != reads):
            raise WorkGraphError('execution input binding mismatch')
        if type(record['output_digest']) is not str or not DIGEST_RE.fullmatch(record['output_digest']):
            raise WorkGraphError('execution output digest required')
        done[record['node']] = record
    if set(done) != expected:
        raise WorkGraphError('missing execution for selected useful work')
    for record in consumptions:
        _require_object(record, 'consumption')
        _require_exact_members(record, {'node', 'consumer', 'condition', 'input_digest', 'input_root_identity', 'read_set_digest', 'output_digest', 'decision_before', 'decision_after'}, 'consumption')
        name = record['node']
        if name not in expected or name in used:
            raise WorkGraphError('unknown or duplicate consumer input')
        if record['consumer'] != transition['consumers'][name]['node'] or record['condition'] != transition['consumers'][name]['condition'] or record['output_digest'] != done[name]['output_digest']:
            raise WorkGraphError('consumer identity/condition/output mismatch')
        if record['input_digest'] != done[name]['input_digest'] or record['input_root_identity'] != done[name]['input_root_identity'] or record['read_set_digest'] != _graph_hash(done[name]['read_set']):
            raise WorkGraphError('consumer input binding mismatch')
        for key in ('decision_before', 'decision_after'):
            _native_name(record[key], 'consumer.' + key)
        if record['decision_before'] == record['decision_after']:
            raise WorkGraphError('consumer has no decision-changing return')
        used[name] = record
    if set(used) != expected:
        raise WorkGraphError('missing consumer for selected useful work')
    status = 'PORTABLE_RECORDS_CONSUMED' if expected else 'NO_REDISPATCH_AT_SUPPLIED_HISTORY' if transition['mode'] == 'NO_REDISPATCH' else 'NO_ELIGIBLE_EXECUTION'
    return dict(schema='implementaudit.recursive-execution.v1', status=status, event_receipt=dict(event_id=transition['event']['id'], graph_digest=transition['graph_digest'], dispatch_id=transition['dispatch_id'], consumed=transition['selected'], source_graph=copy.deepcopy(graph)) if expected else None, consumed=sorted(used), authority='NONE', native_campaign_proven=False, evidence_scope='SOURCE_BOUND_EXECUTION_AND_CONSUMPTION_RECORDS', process_attestation='EXTERNAL_TO_PURE_CHECKER')

def verifier_registered_tests_v1(registry_bytes):
    """Discover test invocations from the actual canonical owner, not a count."""
    try:
        text = registry_bytes.decode('utf-8', 'strict')
    except (AttributeError, UnicodeDecodeError) as exc:
        raise WorkGraphError('verifier registry: UTF-8 bytes required') from exc
    tests = re.findall('(?m)^bash (tests/[A-Za-z0-9_.-]+\\.test\\.sh)(?:[ \\t]|$)', text)
    if len(tests) != len(set(tests)):
        raise WorkGraphError('verifier registration: duplicate test')
    return sorted(tests)

def compile_verifier_graph_v1(registry_bytes, test_paths, environment):
    """Map every registry byte to one ordered executable node.

    Arbitrary prelude shell state, inline Python, conditional release identity,
    cleanup and assertions stay together. Tail grammar is deliberately narrow;
    unknown syntax refuses reassembly. This is a conservative serial graph, not
    a proof that verifier bodies have independently closed read/write sets.
    """
    registered = verifier_registered_tests_v1(registry_bytes)
    if sorted(_native_strings(test_paths, 'verifier test paths')) != registered:
        raise WorkGraphError('verifier registration population mismatch')
    _require_object(environment, 'verifier environment')
    validate_identity_json_v1(environment)
    text = registry_bytes.decode('utf-8')
    if 'r0035_verifier_' in text or '\x00' in text:
        raise WorkGraphError('verifier registry conflicts with transport namespace')
    boundary = 'bash scripts/generate-readme-diagrams.sh --check\n'
    if text.count(boundary) != 1:
        raise WorkGraphError('verifier grammar: unique composed-prelude boundary required')
    at = text.index(boundary)
    if at == 0 or (at and text[at - 1] != '\n'):
        raise WorkGraphError('verifier grammar: prelude boundary must start a line')
    if re.search('(?m)^bash tests/', text[:at]):
        raise WorkGraphError('verifier grammar: test hidden in composed prelude')
    lines = text[at:].splitlines(keepends=True)
    chunks = [('PRELUDE', 'COMPOSED_PRELUDE', text[:at], None)]
    index = 0
    commands_seen = {}
    while index < len(lines):
        source = lines[index]
        index += 1
        if not source.strip():
            name, kind, old, command = chunks[-1]
            chunks[-1] = (name, kind, old + source, command)
            continue
        while source.rstrip('\r\n').endswith('\\'):
            if index == len(lines):
                raise WorkGraphError('verifier grammar: truncated continuation')
            source += lines[index]
            index += 1
        logical = source.replace('\\\n', '')
        try:
            words = shlex.split(logical, comments=False, posix=True)
        except ValueError as exc:
            raise WorkGraphError('verifier grammar: malformed command') from exc
        if len(words) >= 2 and words[0] == 'bash' and re.fullmatch('(?:scripts|tests)/[A-Za-z0-9_.-]+\\.sh', words[1]):
            if re.search('[;|&<>`]|\\$\\(', logical):
                raise WorkGraphError('verifier grammar: compound tail command')
            command = words[1]
            occurrence = commands_seen.get(command, 0)
            commands_seen[command] = occurrence + 1
            name = f'COMMAND:{command}:{occurrence}'
            kind = 'TEST' if command.startswith('tests/') else 'CHECK'
        elif words == ['git', 'diff', '--check']:
            name, kind, command = ('FINAL_DIFF', 'FINAL_CHECK', 'git diff --check')
        elif logical == "printf 'verify-package: ok\\n'\n" and index == len(lines):
            name, kind, command = ('TERMINAL', 'TERMINAL', 'printf')
        else:
            raise WorkGraphError('verifier grammar: unknown tail command')
        chunks.append((name, kind, source, command))
    if chunks[-1][1] != 'TERMINAL':
        raise WorkGraphError('verifier grammar: exact terminal operation required')
    nodes, offset, prior, test_nodes = ([], 0, None, {})
    for name, kind, source, command in chunks:
        encoded = source.encode('utf-8')
        if any((n['id'] == name for n in nodes)):
            raise WorkGraphError('verifier graph: duplicate node')
        node = dict(id=name, kind=kind, source=source, source_sha256=hashlib.sha256(encoded).hexdigest(), byte_start=offset, byte_end=offset + len(encoded), requires=[] if prior is None else [prior], command=command, environment_digest=_graph_hash(environment), writer_resource_constraint='SHARED_SHELL_AND_REPOSITORY_SERIAL', independence='UNQUALIFIED_TRANSITIVE_READ_WRITE_SETS', evidence=['raw_stdout', 'raw_stderr', 'process_exit', 'node_start_end'], invalidators=['registry_bytes', 'candidate_source', 'environment', 'order', 'currentness'], result_contract='PASS_EXIT_ZERO_OR_FAIL_OR_UNSETTLED_DEPENDENCY')
        if kind == 'TEST':
            if command in test_nodes:
                raise WorkGraphError('verifier registration: duplicate test node')
            test_nodes[command] = name
        nodes.append(node)
        offset += len(encoded)
        prior = name
    if sorted(test_nodes) != registered or offset != len(registry_bytes):
        raise WorkGraphError('verifier registry coverage mismatch')
    return _seal_graph(dict(schema='implementaudit.verifier-work-graph.v1', registry_sha256=hashlib.sha256(registry_bytes).hexdigest(), covered_bytes=offset, environment=environment, nodes=nodes, test_nodes=test_nodes, ordering='LEGACY_SERIAL_PRESERVED', selective_reuse='UNQUALIFIED_READ_SETS_REFUSE_REUSE', canonical_route_changed=False, authority='NONE'))

def verifier_command_stream_v1(graph, current_registry_bytes):
    _check_graph_seal(graph, 'implementaudit.verifier-work-graph.v1')
    if graph['registry_sha256'] != hashlib.sha256(current_registry_bytes).hexdigest():
        raise WorkGraphError('verifier graph: stale registry')
    rebuilt = compile_verifier_graph_v1(current_registry_bytes, sorted(graph['test_nodes']), graph['environment'])
    if rebuilt != graph:
        raise WorkGraphError('verifier graph differs from current owner derivation')
    return b''.join((node['id'].encode() + b'\x00' + node['source'].encode() + b'\x00' for node in graph['nodes']))
VERIFIER_LEAF_CONTRACTS_V1 = {'scripts/check-readme-toc.sh': dict(sha256='9b8cc45e887b29ffb904b17643ef0e0564db8fb7eb475685e294dbcc2dea8638', reads=['README.md'], probes=[]), 'scripts/check-agents-bootstrap-budget.sh': dict(sha256='be6cb923382263f35b87a0b65f42fc57fd438fd091dc4fa2baf3533d0eb4e078', reads=['AGENTS.md'], probes=['docs/audits/RETENTION.md', 'tests/agents-bootstrap-budget.test.sh'])}  # source repo
VERIFIER_REGISTRY_CONTRACTS_V1 = {**VERIFIER_LEAF_CONTRACTS_V1, 'scripts/check-validation-registry.sh': dict(sha256='c7c6b0f26111c44c4caaf5e1ffc20979e48cc15ca83600f3fea16514e9d02fee', reads=['scripts/verify-package.sh', '.github/workflows/validate.yml'], probes=[], membership='tests/*.test.sh')}  # source repo

def compile_verifier_reuse_v1(graph, registry, acquired, issued):
    """Derive a bounded task plan. The real acquirer owns input facts; the
    consumer supplies only intact successes from its live issuance custody.
    This pure function authenticates neither execution nor native currentness.
    """
    verifier_command_stream_v1(graph, registry)
    _require_exact_members(acquired, {'schema', 'scope', 'binding', 'inputs'}, 'verifier acquisition')
    _require_string(acquired['scope'], 'verifier acquisition scope')
    contracts = {'CONTROLLED_TASK_LEAVES_V1': VERIFIER_LEAF_CONTRACTS_V1, 'CONTROLLED_TASK_REGISTRY_V1': VERIFIER_REGISTRY_CONTRACTS_V1}.get(acquired['scope'])
    if acquired['schema'] != 'implementaudit.verifier-acquisition.v1' or contracts is None:
        raise WorkGraphError('unsupported verifier acquisition scope')
    _require_object(acquired['binding'], 'verifier binding')
    _require_object(issued, 'issued verifier keys')
    names = {'COMMAND:' + path + ':0' for path in contracts}
    _require_exact_members(acquired['inputs'], names, 'verifier input population')
    if not set(issued).issubset(names):
        raise WorkGraphError('foreign issued verifier population')
    nodes = []
    for node in graph['nodes']:
        if node['id'] not in names:
            continue
        contract = contracts[node['command']]
        if node['source'].strip() != 'bash ' + node['command']:
            raise WorkGraphError('unsupported verifier invocation')
        inputs = acquired['inputs'][node['id']]
        _require_exact_members(inputs, {'program_sha256', 'image_digest'}, 'verifier leaf input')
        if inputs['program_sha256'] != contract['sha256']:
            raise WorkGraphError('unsupported verifier checker contract')
        if not isinstance(inputs['image_digest'], str) or not re.fullmatch('[0-9a-f]{64}', inputs['image_digest']):
            raise WorkGraphError('invalid verifier image identity')
        key = _graph_hash([graph['digest'], acquired['scope'], acquired['binding'], node, contract, inputs])
        nodes.append(dict(node=node['id'], key=key, decision='CONSUME_PRIOR_SUCCESS' if issued.get(node['id']) == key else 'EXECUTE'))
    if {n['node'] for n in nodes} != names:
        raise WorkGraphError('verifier mapped scope population mismatch')
    return _seal_graph(dict(schema='implementaudit.verifier-reuse-plan.v1', scope=acquired['scope'], graph_digest=graph['digest'], nodes=nodes, omitted_canonical_nodes=len(graph['nodes']) - len(nodes), authority='NONE'))

def _native_operation_output_v1(operation, run_root, repo_root, operands):
    """Accept operation bytes only after the enclosing source checks close."""
    def load_json(path):
        return decode_strict_json_bytes(pathlib.Path(path).read_bytes(), path)
    with observe_native_run_v1(run_root, repo_root) as raw:
        current = decode_strict_json_bytes(raw, 'native run observation')
        if operation == '--select-native':
            result = select_native_frontier_v1(current)
        elif operation == '--recursive-native':
            result = compile_recursive_transition_v1(current, load_json(operands[0]))
        elif operation == '--reconcile-native':
            result = reconcile_native_results_v1(load_json(operands[0]), current,
                load_json(operands[1]), load_json(operands[2]), operands[3])
        else:
            raise WorkGraphError('unknown native operation')
        output = canonical_json_v1(result)
    return output

def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] in {'--select-native', '--recursive-native', '--reconcile-native'}:
        try:
            expected = {'--select-native': 4, '--recursive-native': 5, '--reconcile-native': 8}[argv[1]]
            if len(argv) != expected:
                raise WorkGraphError('native operation requires RUN_ROOT REPO_ROOT and its exact contract inputs')
            output = _native_operation_output_v1(argv[1], argv[2], argv[3], argv[4:])
            sys.stdout.buffer.write(output)
            return 0
        except (OSError, WorkGraphError) as exc:
            print(f'compile-work-graph: {exc}', file=sys.stderr)
            return 2
    if len(argv) > 1 and argv[1] in {'--inspect-native', '--native-run'}:
        try:
            expected = 3 if argv[1] == '--inspect-native' else 4
            if len(argv) != expected:
                raise WorkGraphError('usage: --inspect-native RUN_ROOT or --native-run RUN_ROOT REPO_ROOT')
            graph = read_native_run_v1(argv[2], None if expected == 3 else argv[3])
            sys.stdout.buffer.write(canonical_json_v1(graph))
            return 0
        except (OSError, WorkGraphError) as exc:
            print(f'compile-work-graph: {exc}', file=sys.stderr)
            return 2
    proximal_mode = argv[1] if len(argv) > 1 and argv[1].startswith('--proximal-') else None
    native_mode = len(argv) > 1 and argv[1] == '--native-a-g'
    supported_modes = {'--proximal-schedule': {3}, '--proximal-advance': {5}, '--proximal-action-selection': {3, 6}, '--proximal-reconcile': {5}}
    invalid_mode = proximal_mode is not None and proximal_mode not in supported_modes
    invalid_arity = proximal_mode is not None and (not invalid_mode) and (len(argv) not in supported_modes[proximal_mode])
    if invalid_mode or invalid_arity or (native_mode and len(argv) != 3) or (proximal_mode is None and (not native_mode) and (len(argv) not in {2, 3})):
        print('usage: compile-work-graph.py WORK_GRAPH.json [PRODUCT_AUTHORITY.json]\n   or: compile-work-graph.py --proximal-schedule REQUEST.json\n   or: compile-work-graph.py --proximal-advance CONTEXT.json REQUEST.json PROJECTION.json\n   or: compile-work-graph.py --proximal-action-selection CONTEXT.json [REQUEST.json PROJECTION.json ADVANCE_TOKEN.json]\n   or: compile-work-graph.py --proximal-reconcile REQUEST.json PROJECTION.json RESULTS.json\n   or: compile-work-graph.py --native-a-g REQUEST.json', file=sys.stderr)
        return 2
    path = pathlib.Path(argv[2] if proximal_mode or native_mode else argv[1])
    try:
        if native_mode:
            projection = compile_native_a_g_v1(path.read_bytes())
        elif proximal_mode == '--proximal-schedule':
            projection = compile_proximal_schedule_v1(path.read_bytes())
        elif proximal_mode == '--proximal-advance':
            projection = issue_proximal_advance_v1(path.read_bytes(), pathlib.Path(argv[3]).read_bytes(), pathlib.Path(argv[4]).read_bytes())
        elif proximal_mode == '--proximal-action-selection':
            context_bytes = path.read_bytes()
            token_path = None if len(argv) == 3 else pathlib.Path(argv[5])
            inputs = (None, None, None) if token_path is None else (pathlib.Path(argv[3]).read_bytes(), pathlib.Path(argv[4]).read_bytes(), token_path.read_bytes())
            projection = compile_proximal_action_selection_v1(context_bytes, *inputs)
        elif proximal_mode == '--proximal-reconcile':
            projection = reconcile_proximal_results_v1(path.read_bytes(), pathlib.Path(argv[3]).read_bytes(), pathlib.Path(argv[4]).read_bytes())
        else:
            raw = path.read_bytes()
            authority_path = pathlib.Path(argv[2]) if len(argv) == 3 else None
            authority_bytes = authority_path.read_bytes() if authority_path else None
            if authority_path is not None:
                validate_product_authority_cli_path_v1(raw, path, authority_path)
            projection = compile_frontier_projection(raw, authority_bytes)
    except OSError as exc:
        print(f'compile-work-graph: {path}: {exc}', file=sys.stderr)
        return 2
    except WorkGraphError as exc:
        print(f'compile-work-graph: {exc}', file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_json_v1(projection))
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
