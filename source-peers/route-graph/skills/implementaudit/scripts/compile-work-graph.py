"""Compile a deterministic, read-only frontier projection from WORK_GRAPH.json."""


from __future__ import annotations


import hashlib


import hmac


import copy


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
        # This is captured-data replay only. It cannot issue a native acquisition witness.
        replay = None
        if schema == 'implementaudit.native-work-graph.v2':
            replay = _RouteScopeObservation(value.get('route_scope'), _CAPTURED_ROUTE_REPLAY_KEY)
        if _compile_native_documents_v1(snapshot, {k: v for k, v in binding.items() if k != 'source_digest'}, _route_observation=replay) != value:
            raise WorkGraphError('native graph differs from source-derived projection')


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


_NATIVE_STATIC_OWNER_SHA256 = 'd49fbe1f0508b3a72aa4dcef089ad6533a98e7eb4850dc318ff825779a0b49b0'


_NATIVE_STATIC_OWNER_BYTES = 333516


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
        flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            raw = stream.read(_NATIVE_STATIC_OWNER_BYTES + 1)
            after = os.fstat(stream.fileno())
        final = path.lstat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
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


def _native_claim_call_v1(owner, route, repo, arguments, claim_raw, validate_raw):
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


def _native_continuity(repo_root, run_root):
    import base64
    owner, owner_path, owner_raw = _native_static_owner_module_v1()
    route, route_path, route_raw = _native_route_scope_module_v1()
    repo = pathlib.Path(repo_root).absolute()
    helper = pathlib.Path(__file__).absolute().with_name('claim-run.sh')
    validate = helper.with_name('validate-run-root.sh')
    budget = dict(remaining=512 * 1024)
    claim_raw = _native_static_file_v1(owner, helper, 256 * 1024, budget)[0]
    validate_raw = _native_static_file_v1(owner, validate, 256 * 1024, budget)[0]
    current = _native_claim_call_v1(owner, route, repo, ['--current-controller'], claim_raw, validate_raw).split('\t')
    if len(current) != 4 or pathlib.Path(current[1]).absolute() != repo or pathlib.Path(current[2]).absolute() != pathlib.Path(run_root).absolute():
        raise WorkGraphError('native continuity root mismatch')
    receipt = _native_claim_call_v1(owner, route, repo, ['--require-current-continuity', current[0]], claim_raw, validate_raw)
    if not RECEIPT_RE.fullmatch(receipt):
        raise WorkGraphError('native continuity receipt format mismatch')
    verified = _native_claim_call_v1(owner, route, repo, ['--verify-resume-receipt', receipt], claim_raw, validate_raw)
    if verified != receipt:
        raise WorkGraphError('native continuity receipt readback mismatch')
    request = dict(source=base64.b64encode(owner_raw).decode('ascii'), sha256=_NATIVE_STATIC_OWNER_SHA256,
                   path=str(owner_path), repository=str(repo))
    environment = owner._native_child_environment(route)
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
    _, final_path, final_raw = _native_static_owner_module_v1()
    if final_path != owner_path or final_raw != owner_raw:
        raise WorkGraphError('native static owner source changed during continuity')
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


_NATIVE_ROUTE_PRODUCER_SHA256 = '0d4faa89878a8072409536ed2f4802576f2adb4ec5ee28755d0489b396bcc895'


_NATIVE_ROUTE_PRODUCER_BYTES = 341797


_NATIVE_ROUTE_OBSERVATION_KEY = object()


_CAPTURED_ROUTE_REPLAY_KEY = object()


class _RouteScopeObservation:
    """In-process acquisition/replay witness, never accepted from JSON."""
    __slots__ = ('value', 'key')

    def __init__(self, value, key):
        if key is not _NATIVE_ROUTE_OBSERVATION_KEY and key is not _CAPTURED_ROUTE_REPLAY_KEY:
            raise WorkGraphError('route observation must be issued by its owner acquisition or captured replay')
        self.value = copy.deepcopy(value)
        self.key = key


def _route_observation_value(observation):
    if (type(observation) is not _RouteScopeObservation or
            (observation.key is not _NATIVE_ROUTE_OBSERVATION_KEY and
             observation.key is not _CAPTURED_ROUTE_REPLAY_KEY)):
        raise WorkGraphError('caller route data cannot replace owner acquisition')
    return copy.deepcopy(observation.value)


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
            or source['producer_sha256'] != _NATIVE_ROUTE_PRODUCER_SHA256
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
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode)
                or getattr(before, 'st_file_attributes', 0) & 0x400):
            raise WorkGraphError('native route producer is not a non-aliased regular file')
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            raw = stream.read(_NATIVE_ROUTE_PRODUCER_BYTES + 1)
            after = os.fstat(stream.fileno())
        named = path.lstat()
    except OSError as exc:
        raise WorkGraphError('native route producer is unavailable') from exc
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if (identity(before) != identity(opened) or identity(opened) != identity(after)
            or identity(after) != identity(named)
            or len(raw) != _NATIVE_ROUTE_PRODUCER_BYTES
            or hashlib.sha256(raw).hexdigest() != _NATIVE_ROUTE_PRODUCER_SHA256):
        raise WorkGraphError('native route producer source identity changed')
    module = types.ModuleType('_implementaudit_r0035_route_scope_owner')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
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


def _compile_native_documents_v1(snapshot, binding, *, acquire_only=False, _route_observation=None):
    before = copy.deepcopy(binding)
    route_scope = _route_observation_value(_route_observation) if _route_observation is not None else None
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
        if node['effect'] in {'MUTATION', 'EXTERNAL'}:
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
        node['input_digest'] = _graph_hash(dict(fact=fact_identity, campaign=state['campaign'], original_scope=state['original_scope'], required={d: nodes[d]['input_digest'] for d in node['requires']}, optional={d: nodes[d]['input_digest'] for d in node['optional']}, read_set=read_set, unresolved_semantic_worktree=before['worktree_digest'] if any((not p.startswith('path:') for p in node['reads'] + node['invalidators'])) else None, route_facts=[routes.get(scope) for scope in node['route_scopes']], **({'route_owner': route_scope} if route_scope is not None and route_scope['scope']['identity'] in node['route_scopes'] else {}), delivery=held.get(node['logical_delivery'])))
        node['declared_state'] = declared
        node['state'] = 'ACTIVE' if declared == 'ACTIVE' else 'BLOCKED' if reasons else 'DONE' if declared == 'DONE' else 'READY'
        node['blocked_reasons'] = sorted(set(reasons))
    source_inventory = [dict(path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) for path, data in sorted(snapshot.items())]
    before['source_digest'] = _graph_hash(source_inventory)
    return _seal_graph(dict(schema='implementaudit.native-work-graph.v2' if route_scope is not None else 'implementaudit.native-work-graph.v1', **({'route_scope': route_scope, 'route_relation': route_relation} if route_scope is not None else {}), binding=before, campaign=state['campaign'], root=state['root'], original_scope=state['original_scope'], event=event, context=state['context'], source_inventory=source_inventory, source_documents={path: data.decode('utf-8') for path, data in snapshot.items()}, nodes=[nodes[name] for name in sorted(nodes)], population={s: sum((n['state'] == s for n in nodes.values())) for s in KNOWN_STATES}, authority='NONE'))


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


def read_native_run_v1(run_root, repo_root=None, *, input_root=None):
    """Acquire all supported native documents, then derive a sealed projection.

    Omitting repo_root is explicitly constructed filesystem evidence. Supplying
    it requires the genuine existing continuity owner before AND after intake.
    Neither path authenticates physical host capacity or effect capabilities.
    """
    before = _native_continuity(repo_root, run_root) if repo_root is not None else dict(acquisition='CONSTRUCTED_FILESYSTEM', controller=None, claim=None, receipt=None, epoch=None, candidate_head=None, candidate_tree=None, worktree_digest=None, continuity_helper_digest=None)
    snapshot = _native_source_snapshot(run_root)
    preliminary = _compile_native_documents_v1(snapshot, before, acquire_only=True)
    input_root = pathlib.Path(input_root if input_root is not None else repo_root if repo_root is not None else run_root)
    read_set = _acquire_native_read_set(preliminary['nodes'], input_root)
    bound = dict(before, read_set=read_set, input_root_identity=hashlib.sha256(os.fsencode(str(input_root.resolve()))).hexdigest())
    route_observation = None
    producer = None
    if repo_root is not None:
        producer, producer_path, producer_raw = _native_route_scope_module_v1()
        acquired_route = producer.read_current_route_scope_v1(pathlib.Path(repo_root), before['controller'])
        if pathlib.Path(acquired_route['owner']['explicit_run_root']).resolve() != pathlib.Path(run_root).resolve():
            raise WorkGraphError('route producer returned a foreign run root')
        _native_validate_route_scope_v1(acquired_route, before)
        route_observation = _RouteScopeObservation(acquired_route, _NATIVE_ROUTE_OBSERVATION_KEY)
    projection = _compile_native_documents_v1(snapshot, bound, _route_observation=route_observation)
    if _native_source_snapshot(run_root) != snapshot:
        raise WorkGraphError('native source changed during intake')
    if _acquire_native_read_set(projection['nodes'], input_root) != read_set:
        raise WorkGraphError('native inputs changed during intake')
    if repo_root is not None and _native_continuity(repo_root, run_root) != before:
        raise WorkGraphError('native continuity changed during intake')
    if producer is not None:
        if producer.read_current_route_scope_v1(pathlib.Path(repo_root), before['controller']) != acquired_route:
            raise WorkGraphError('native route changed during intake')
        _, final_path, final_raw = _native_route_scope_module_v1()
        if final_path != producer_path or final_raw != producer_raw:
            raise WorkGraphError('native route producer changed during intake')
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
