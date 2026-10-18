#!/usr/bin/env python3
"""Reconstruct the published, canonically unallocated R0044 source qualification.

Repository-only, stdlib-only research utility. It does not execute archive code,
adjudicate research, infer private target decisions, install a runtime or grant
receiving/closure authority. Use the pinned Git objects for recovery, then check
the complete source projection or materialise a full member view.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile


COMMIT = "cacfe97da7656b472bf4f11e50c9d106a6c3f92a"
TRIAD_COMMIT = "0e175fe64cbd4846fbf8e06c8b2ede12295c514c"
TRIAD = "docs/research/implementaudit/triad-integration/"
OLD_TARGET = TRIAD + "DISPOSITIONS.json"
TC_FINDINGS = TRIAD + "COMPOSITION_FINDINGS.json"
BASE = "docs/research/genealogy/"
LINEAGE = BASE + "ama/evolved-multi-agent-systems/"
LEDGER = LINEAGE + "corpus/EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json"
EMAS_ZIP = LINEAGE + "packet/EVOLVED_MULTI_AGENT_SYSTEMS_FROZEN_PACKET.zip"
AMA_ZIP = BASE + "ama/packet/EVOLVED_AMA_FROZEN_PACKET.zip"
LINEAGE_MANIFEST = LINEAGE + "LINEAGE_MANIFEST.json"
TRIFECTA_MANIFEST = BASE + "ama/TRIFECTA_MANIFEST.json"
SOURCE_LOCK = BASE + "CORPUS_SOURCE_LOCK.json"
CORPUS_MANIFEST = BASE + "CORPUS_MANIFEST.json"
DEFAULT_INDEX = Path(__file__).resolve().parents[1] / "docs/research/implementaudit/r0044-member-dispositions.json"
PINS = {
    LINEAGE_MANIFEST: (5223, "cf32e7039686a14be8599647d2f57a80e424cd459fe4df452aef0571e8f734ba", "11d375c97c11a397dd43cdc16ec08cb1ad75530f"),
    LEDGER: (949484, "3a7ab2f6938ed69f31bbeac2dc574c3b6e189e300482ebcc904fb7151c86ae98", "70167088120a84aa17962e7862f1a755f9408280"),
    EMAS_ZIP: (370502, "84af391ed2c82514f0e22ff671a0945945dec608ffccfde485e2302374bab227", "3f7e0d4005d47337410020a8c3143789e5456f0d"),
    AMA_ZIP: (10534831, "1c9654ab3017ecccdd3b24810b20ac23a5b51a5c19c1a488b64a2684dade026f", "dcf8d8a13f3cae7300f8989bc4f3c09eef019cfe"),
    SOURCE_LOCK: (48135, "dbff42652b791ab88dc949332f9accf89f78fedc2603548179f0432e2edd806e", "d0d9452eef5b341f75dac5ca7e8bf7dc772015c5"),
    CORPUS_MANIFEST: (70644, "3b924991d8bf81b4eb9fdb39cf1dd2e57398aa612a449cde53e82abac56a13a2", "7742b5b4038a0663913dc5c3a7f48da360616857"),
    TRIFECTA_MANIFEST: (7024, "586f0fc16ef6808e4632ef5b351aaf4adca224f0c295e405ec8d6773b8000969", "b3ce2550b200937d7884caa302e2cf42adcf07ef"),
    OLD_TARGET: (2209426, "616584f2e13d41fd8afb116f2b81b035d2f4600a13814f7523ebff4010a05dab", "5e94bd9c4f899aa3cbc11fe7da8698620f379e8d"),
    TC_FINDINGS: (22814, "7f6930b34a88553bf6cac0b4d1f1ab1a8eb2a0847220be80bf1952f4e4a1af47", "e2c2eb857a3aeb4f21f0563d7631c594d43251c3"),
}
STATUSES = {
    "RETAINED_IN_EVOLVED_FORM": 28, "STRONGLY_RETAINED": 16,
    "REJECTED_OR_DISFAVOURED": 7, "ASSUMPTION_SENSITIVE": 8,
    "CONTEXT_DEPENDENT": 10, "UNRESOLVED": 1,
    "CEREMONY_NOT_GENERAL_PROPERTY": 2, "DOMAIN_SPECIFIC": 3,
    "USEFUL_BUT_EASILY_GAMED": 1,
}
PREPARED_COUNTS = {"PARTIALLY_ABSORBED": 27, "CONDITIONAL": 36,
                   "REJECTED_WITH_REASON": 9, "RESEARCH_ONLY": 1, "NON_TRIGGERED": 3}
EXPECTED_IDS = [f"EMAS-{i:03}" for i in range(1, 77)]
REGISTER = "EVOLVED_AMA_CONSTITUENT_PROPERTY_REGISTER.json"
INTAKE = "EVOLVED_AMA_INTER_CROSSWALK_INTAKE.json"
RELATIONS = "EVOLVED_AMA_DIRECTIONAL_RELATION_LEDGER.json"
MATRIX = "EVOLVED_AMA_INTRA_CROSSWALK_MATRIX.json"
PROFILES = "EVOLVED_AMA_SEMANTIC_PROFILES_AND_RULES.json"
GROUPS = "EVOLVED_AMA_CONVERGENCE_AND_COMPOSITION_CLUSTERS.json"
CONTEXT = "EVOLVED_AMA_CONSTITUENT_CONTEXT_INDEX.json"
SOURCES = "EVOLVED_AMA_SOURCE_REGISTER.json"

# Published, canonically unallocated R0044: separately consumed sealed target
# inputs. These identify private custody, not public download locations.
PREPARED_PINS = {
    "R0044_CROSSWALK.json": (3789326, "462803bc046c469dd9bd101c3c0cfc657fa3e80a79f70179128df90efe7c3d82"),  # canonically unallocated
    "PROPERTY_LEDGER.jsonl": (21635713, "9f2424c6f9cc15e91ec2b61026376bf4e7ee969236c02929059375be3f5fdfa4"),
    "GROUP_LEDGER.jsonl": (3479308, "e615a9fbb30c95bc262eb522fb4363ad7c00482205dccccf15716b2fe52eff00"),
    "RELATION_LOCATORS.jsonl": (28365949, "13eafa9e979f700394823f4d7beafa977c2b0f6601955d384283f1615081c9d1"),
    "TARGET_RELATION_DISPOSITIONS.jsonl": (4021017, "aeedffc24d8b536529fe02447ecdd41ae457503220a5b91eef89880836ab13f8"),
    "TARGET_RECONCILIATION.json": (3979013, "74035c789803c62d43f3535a73c641bef207bd4ecc8cfd8eba6458ff7d62ca39"),
    "FULL_CONTEXT_LEDGER.jsonl": (1624822, "1c63d87bc052c1cb417febc0e7d27faa8e23488b87dbf54da207fd3518edea66"),
    "EVOLVED_AMA_FROZEN_PACKET.zip": (10534831, "1c9654ab3017ecccdd3b24810b20ac23a5b51a5c19c1a488b64a2684dade026f"),
    "prior_preparation": (106569, "eae4e4c28b170bfb513661485cab1551ed970062abd83af9e93926a617a4232b"),
    "final_packet_binding": (14995, "c0c984488f7f8654688882f25acd0ded955cd371a6787c1c2cb39cd98f2e3570"),
    "prepared_source_clause_binding": (25242, "fa125b6b4f22cb7a24c34d9a99c68fad74a5904c4ad907b760586d037dae0cc0"),
    "SOURCE_MEMBER_MANIFEST.json": (9914, "0fa95214c232f94821c636e2a8ad7c96943dfc77191beb5cfba1d625b4de82bb"),
    "AMA_CONTINUATION_CANDIDATE.md": (22551, "94f9d6aefa4aad4f4dc31e5d75ea14d405ba29f17567cff32cf9a0374d1947ea"),
}
QUALIFIED_BASE = "b802705830d1ec86a20dce0001f5dc6a5470b68a"
QUALIFIED_BASE_TREE = "636f6b0ef368c1765030d57ee5d6a5387dc9a8e8"
TARGET_PROJECTION_SHA256 = "0468ff034e2546d686c008fce3fb8da0e826083e0cdf265a264366f6c3dd42ae"
TC10_PARENTS = ["ESPLE:ESPLE-023", "EBPM:EBPM-022", "EPM:EPM-043", "EPM:EPM-064", "EMAS:EMAS-072", "EAOSE:EAOSE-C124"]


def public_fields(record, names):
    """An allowlist, never an export of the enclosing private operational record."""
    return {name: record[name] for name in names if name in record}


def no_private_locations(value):
    text = canonical(value).decode("utf-8")
    require(re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/workspace/|/Users/|/home/|\\\\\\\\|01a[0-9a-f]{5}-", text) is None,
            "private host/session location in public projection")


def prepared_projection(input_map, source, corpus, preparation_row=1, repo_root=None):
    require(preparation_row == 1, "EMAS requires preparation row 1, not the host row")
    repo = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    base_tree = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', QUALIFIED_BASE + '^{tree}'], stderr=subprocess.PIPE).decode().strip()
    require(base_tree == QUALIFIED_BASE_TREE, "selected source base tree is unavailable or mismatched")
    paths = parse(input_map.read_bytes())
    raw = {}
    for name, (size, sha) in PREPARED_PINS.items():
        path = Path(paths[name])
        require(path.stat().st_size == size, "sealed input size differs: " + name)
        data = path.read_bytes()
        require(len(data) == size and digest(data) == sha, "sealed input differs: " + name)
        raw[name] = data
    crosswalk = parse(raw["R0044_CROSSWALK.json"])  # canonically unallocated
    preparation = parse(raw["prior_preparation"])
    prep = preparation["rows"][preparation_row]
    binding = parse(raw["final_packet_binding"])
    require(prep["ROW_ID"] == "EMAS" and prep["PROPERTY_CROSSWALK_CURRENT"]["property_count"] == 76,
            "wrong preparation population")
    require(binding["original_preparation"]["sha256"] == PREPARED_PINS["prior_preparation"][1], "mixed preparation binding")
    nested = next(r for r in binding["three_nested_original_archives"] if r["row"] == "EMAS")
    require(nested["sha256"] == PINS[EMAS_ZIP][1] and raw["EVOLVED_AMA_FROZEN_PACKET.zip"] == corpus.raw[AMA_ZIP],
            "mixed final source binding")
    member_manifest = parse(raw["SOURCE_MEMBER_MANIFEST.json"])
    require(member_manifest["packet"]["sha256"] == PINS[AMA_ZIP][1], "mixed source member manifest")
    for entry in member_manifest["members"]:
        data = corpus.ama.read(entry["member"])
        require(len(data) == entry["bytes"] and digest(data) == entry["sha256"], "source member differs")
    records = {name: [parse(line) for line in data.splitlines() if line] for name, data in raw.items() if name.endswith('.jsonl')}
    properties = {r["key"]: r for r in records["PROPERTY_LEDGER.jsonl"]}
    reconciliation = parse(raw["TARGET_RECONCILIATION.json"])
    secondary = {r["key"]: r["exact_original_limit"] for r in reconciliation["receiving_behavior_evidence"]["secondary_limits"]}
    routing = {}
    route_pins = {}
    for concern in reconciliation["receiving_behavior_evidence"]["concerns"]:
        pin = concern["source_packet"]
        name = "source-packet-" + pin["sha256"]
        require(Path(paths[name]).stat().st_size == pin["bytes"], "concern routing size differs")
        data = Path(paths[name]).read_bytes()
        require(len(data) == pin["bytes"] and digest(data) == pin["sha256"], "mixed concern routing input")
        row = pointer(parse(data), concern["source_packet_pointer"])
        primary = row.get("primary_properties", row.get("primary_source_properties", []))
        secondary_keys = row.get("secondary_route_keys", [])
        routing[concern["concern"]] = {"primary": primary, "secondary": secondary_keys,
            "input_alias": name, "selector": concern["source_packet_pointer"],
            "scope": "Exact prepared routing only; discovery is not behavioral coverage."}
        route_pins[name] = {"bytes": pin["bytes"], "sha256": pin["sha256"]}
    source_rows = {r["ama_key"]: r for r in source["rows"]}
    rows = []
    for row in crosswalk["rows"]:
        key = row["Property"]
        old = source_rows[key]
        full = properties[key]
        require(row["source_row_sha256"] == old["original_intake"]["canonical_record_sha256"] and
                full["original_intake_record"] == corpus.intake_by_key[key][1] and
                full["source_register_record"] == corpus.register[key], "mixed original/target member: " + key)
        require(row["Warranted_delta_acceptance_or_no_adoption_reason"] == full["current_candidate_target_record"] and
                row["Prepared_absorption_state"] == full["absorption_state"] and
                row["original_group_memberships"] == old["groups"] and
                row["AMA_directional_relation_ids"] == old["incident_direction_ids"], "target/full-record correspondence differs")
        state = row["Prepared_absorption_state"]
        continuation = public_fields(row, ["criterion", "trigger", "cheap_path", "assumptions", "evidence_ceiling",
            "source_ids", "source_roles", "original_group_memberships", "original_within_lineage_relation_ids",
            "exact_sibling_properties", "outside_AMA_TC_hypotheses", "outside_AMA_limit", "native_source_anchors",
            "load_consumer_path", "absorbed_portion", "residual", "first_missing_discriminator", "reason",
            "reconsideration_trigger", "next_action", "version_horizon", "historical_cell_implications",
            "release_cell_effect", "authority_earned", "authority_not_earned", "current_source_correction"])
        continuation["qualification_evidence"] = public_fields(row["qualification_evidence"],
            ["original_limits", "credit", "complete_qualification"])
        role = []
        for name in full["current_carrier_concerns"]:
            r = routing.get(name, {"primary": [], "secondary": []})
            role.append({"concern": name, "role": "PRIMARY" if key in r["primary"] else
                "SECONDARY_DISCOVERY_ONLY" if key in r["secondary"] else "NOT_ENUMERATED_IN_SELECTED_ROUTING_ROW",
                "input_alias": r.get("input_alias"), "selector": r.get("selector"),
                "limit": "Explicit membership only; an unenumerated role is unknown, not inferred secondary or qualified."})
        limit = public_fields(secondary.get(key, {}), ["key", "concern", "source_pointer", "source_row_sha256",
            "source_semantic_disposition", "prior_target_disposition", "prior_target_qualification_limit", "trigger",
            "cheap_path", "not_discriminated_by_grouped_witness", "remaining_conditional_action", "target_behavior_credit"])
        action = {"REJECTED_WITH_REASON": "Retain the rejection; do not implement the rejected general claim. If the corrected guarded form is selected, obtain its exact evidence.",
            "RESEARCH_ONLY": "Keep the current-profile claim unresolved. Select a precise profile and implementation only if that conformance claim is required, then obtain issuing-body and behavioral evidence.",
            "NON_TRIGGERED": "Keep the domain mechanism dormant. Reopen only if its specific representation, domain and fault-model prerequisites become an authorized requirement.",
            "CONDITIONAL": "Retain conditional use. Before relying on this mechanism, establish its own trigger, rights, model and receiving predicate; a related member or group result is insufficient.",
            "PARTIALLY_ABSORBED": "Retain the supported guidance and this member's residual separately. Qualify a selected operational claim through its actual owner before claiming behavior."}[state]
        rows.append({"id": old["id"], "ama_key": key, "original_source_status": row["External_status"],
            "original_intake_sha256": row["source_row_sha256"], "prepared_absorption": state,
            "prepared_native_disposition": row["Native_disposition"],
            "prepared_owner_ids_json_unallocated": canonical(row["Native_owners"]).decode(),
            "prepared_record_json_unallocated": canonical(full["current_candidate_target_record"]).decode(),
            "prepared_continuation_json_unallocated": canonical(continuation).decode(),
            "prepared_routing": role, "secondary_limit": limit,
            "corrected_carrier_routing": public_fields(full['corrected_full_corpus_record'],
                ['concern_routes', 'primary_decisions', 'decision_scope']),
            "incident_direction_ids": old["incident_direction_ids"],
            "current": {"disposition": "DOCUMENTARY_CONTINUATION_NO_RUNTIME_CHANGE",
                "supported_portion": ("Both full six-unit documentary alternatives were actually received at the frozen comparison source; cost ranking remains inconclusive. Final entitled acceptance is separate." if old['id'] == 'EMAS-001' else
                    "Original and prepared meaning preserved for actual receiving; no per-member runtime pass."),
                "current_owner_paths": sorted({a.split(':')[0] for a in row["native_source_anchors"] if a.startswith('skills/')}),
                "consumer": "Issue 231 owner for this 76-member disposition; scoped constituent input to issue 232 AMA-CONTINUATION.",
                "source_guard": row["trigger"], "source_authority": old["source_obligation"]["authority"],
                "residual": "Prepared conditional residual retained, not a demonstrated current defect: " + row["residual"],
                "first_missing_discriminator": {"selected_claim_evidence": old["source_obligation"]["required_evidence"],
                    "claim_and_authority": "An actual selected operational claim, entitled owner and applicable source/host identity are required before this residual becomes executable."},
                "next_lawful_action": action, "if_trigger_selected": old["source_obligation"]["required_evidence"],
                "otherwise": row["cheap_path"], "reentry_trigger": row["reconsideration_trigger"],
                "horizon": "Before any selected stronger operational claim; no future implementation date appointed.",
                "native_join": "NOT_ESTABLISHED", "owner_acceptance": "EXACT_SUBJECT_HUMAN_DECISION_REQUIRED"}})
    directions = {r["id"]: r for r in records["TARGET_RELATION_DISPOSITIONS.jsonl"]}
    locators = {r["id"]: r for r in records["RELATION_LOCATORS.jsonl"]}
    incident = corpus.incident()
    target_relations = []
    for original in incident:
        identity = original["relation_id"]
        loc = locators[identity]
        require(loc["full_record_canonical_sha256"] == digest(canonical(original)) and
                loc["relation_type"] == original["relation_type"], "mixed relation source")
        target_relations.append({**directions[identity], "original_record_sha256": loc["full_record_canonical_sha256"],
            "original_pointer": loc["full_record_locator"]})
    groups = []
    for group in records["GROUP_LEDGER.jsonl"]:
        if not any(k.startswith('EMAS:') for k in group["member_original_property_identities"]):
            continue
        projected = public_fields(group, ["group_id", "name", "semantic_group_basis", "member_original_property_identities",
            "source_cluster_locator", "absorption_state", "absorption_state_scope", "member_state_counts",
            "absorbed_portion", "residual", "first_missing_discriminator", "reason", "reconsideration_trigger",
            "plausible_next_action", "version_horizon", "release_cell_boundary", "authority_earned", "authority_not_earned"])
        groups.append({"id": group["group_id"], "record_json_unallocated": canonical(projected).decode()})
    contexts = [r for r in reconciliation["ama_context_target_dispositions"] if any(k.startswith('EMAS:') for k in r["property_keys"])]
    full_context = {r["id"]: r for r in records["FULL_CONTEXT_LEDGER.jsonl"]}
    for context in contexts:
        require(context["id"] in full_context, "missing full context owner")
    concern_ids = {identity for r in rows for identity in r['corrected_carrier_routing']['concern_routes']}
    concern_records = []
    for position, record in enumerate(reconciliation['corrected_receiver_dispositions']['rows']):
        if record['candidate_id'] not in concern_ids:
            continue
        projected = public_fields(record, ['candidate_id', 'short_id', 'concern', 'source_producer_classification',
            'proposed_receiver_classification', 'decision_authority', 'actual_contract_can_pass_while_concern_fails',
            'reason', 'proposed_acceptance_owners', 'source_disposition', 'material_binding_required',
            'new_durable_identity_proposed', 'canonical_adjudication_and_final_review_pending'])
        projected['primary_source_properties'] = record['exact_parent_provenance']['properties']
        projected['target_and_qualification'] = public_fields(record['target_and_qualification'],
            ['status', 'required_action_or_scope', 'secondary_credit', 'non_trigger_reason', 'reconsideration_trigger'])
        projected['historical_prepared_contract_anchors'] = [public_fields(a,
            ['rockstar', 'url', 'line_start', 'line_end', 'text', 'scope']) for a in record['exact_current_contract_anchors']]
        concern_records.append({'id': record['candidate_id'], 'source_input': 'TARGET_RECONCILIATION.json',
            'source_selector': f'/corrected_receiver_dispositions/rows/{position}',
            'source_record_sha256': digest(canonical(record)), 'record_json_unallocated': canonical(projected).decode()})
    require({r['id'] for r in concern_records} == concern_ids, "unresolved corrected carrier route")
    owner_paths = sorted({p for r in rows for p in r["current"]["current_owner_paths"]} |
        {'skills/implementaudit/SKILL.md', 'skills/implementaudit/references/issue-ready-work-orders.md',
         'skills/implementaudit/references/composed-evidence.md'})
    owners = []
    for path in owner_paths:
        entry = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-z', '--full-tree', QUALIFIED_BASE, '--', path], stderr=subprocess.PIPE)
        data = None
        if entry:
            entries = entry.rstrip(b'\0').split(b'\0')
            require(len(entries) == 1, "ambiguous source owner path")
            header, selected_path = entries[0].split(b'\t', 1)
            mode, kind, blob = header.split()
            require(selected_path.decode() == path and kind == b'blob' and mode in (b'100644', b'100755'), "invalid source owner entry")
            data = subprocess.check_output(['git', '-C', str(repo), 'cat-file', 'blob', blob.decode()], stderr=subprocess.PIPE)
        owners.append({"path": path, "base": QUALIFIED_BASE, "state": "PRESENT_SOURCE_ONLY" if data is not None else "ABSENT_AT_SELECTED_BASE",
            "sha256": digest(data) if data is not None else None,
            "limit": "Prepared line numbers are historical. Source availability does not establish applied or native behavior."})
    tc10 = crosswalk["bounded_cross_trifecta_hypotheses"][0]
    require(tc10['parents'] == TC10_PARENTS, "wrong TC10 parents")
    target = {
        "format": "r0044-target-continuation-v1", "input_custody": [{"alias_unallocated": k, "bytes": v[0], "sha256": v[1]} for k, v in PREPARED_PINS.items()],
        "additional_routing_custody": route_pins,
        "custody_limit": "Input aliases and digests identify private historical custody; they are not public content routes. All selected actionable meaning is projected below; original full source resolves through source_projection and member.",
        "preparation_binding": {"selector": "/rows/1", "row_id": prep['ROW_ID'], "property_count": 76,
            "prepared_state_counts": prep['PROPERTY_CROSSWALK_CURRENT']['prepared_state_counts'],
            "final_input_binding_sha256": PREPARED_PINS['final_packet_binding'][1], "nested_EMAS_sha256": nested['sha256'],
            "scope": "Prepared correspondence, not authoritative currentness or receiving."},
        "rows": rows, "target_relations": target_relations,
        "corrected_carrier_decisions": concern_records,
        "groups": groups, "context_dispositions_json_unallocated": canonical(contexts).decode(),
        "explicit_bridge_dispositions_json_unallocated": canonical(crosswalk['explicit_intra_AMA_bridges']).decode(),
        "bridge_scope": "48 prepared EMAS semantic bridge dispositions are distinct from 75 original touching hand bridges. Missing prepared bridge is not a no-material judgment; all 11960 target directions remain separately available.",
        "TC10": {"parents": tc10['parents'], "prepared_record_json_unallocated": canonical(tc10).decode(),
            "current_application": "Preserve fixed trial population, order, rights, information and cost unknowns. The analytical case-mix illustration is not measured benefit."},
        "current_source_owners": owners,
        "current_scope": {"runtime": "NO_CHANGE", "runtime_version": "0.4.0", "release_family": "v0.4.0.0",
            "source_base": QUALIFIED_BASE, "total_comparison_cost": "INCONCLUSIVE", "adequate_direct_path": True,
            "direct_required_units": ['M1','M2','M3','R1','R2','R3'], "split_required_units": ['M1','M2','M3','R1','R2','R3'],
            "historical_comparison_source": "ff66f450014e2581e87f37a4782aa0bb65f3c99a",
            "receiving_scope": "Complete documentary disposition and semantic continuation; entitled acceptance is separately recorded in the issue certificate after human approval.",
            "receiver_required": True, "owner_acceptance": "EXACT_SUBJECT_HUMAN_DECISION_REQUIRED", "native_join": "NOT_ESTABLISHED",
            "operational_residual": "No authenticated host principal, native LOAD/USE/JOIN, campaign consumption, currentness, epoch, strategic protocol, domain algorithm or general multi-agent benefit is established. Select and authorize an exact operational claim before its additional qualification.",
            "host_receipt": source['receiving_route']['host'], "eaa_input": source['receiving_route']['sibling_EAA'],
            "continuing_custody": "The issue 231 certificate and repository qualification/member reader retain this constituent; the issue 232 receiver retains only its scoped input. Old carriers remain retained. No general programme steward is appointed.",
            "predecessor_retirement": "NOT_AUTHORISED", "host_278_32_acceptance": "NOT_CLAIMED"}}
    no_private_locations(target)
    return target


def check_document(document):
    if document.get("format") != "r0044-full-disposition-v2":
        return check_index(document), document
    unsigned = dict(document)
    supplied = unsigned.pop("projection_sha256")
    require(digest(canonical(unsigned)) == supplied, "composed projection digest differs")
    target = document["target_continuation"]
    require(digest(canonical(target)) == TARGET_PROJECTION_SHA256, "prepared/current continuation differs from qualified projection")
    require(target['preparation_binding']['selector'] == '/rows/1', "wrong preparation row")
    require([r['id'] for r in target['rows']] == EXPECTED_IDS, "target member population differs")
    require(dict(Counter(r['prepared_absorption'] for r in target['rows'])) == PREPARED_COUNTS, "prepared states differ")
    require(target['TC10']['parents'] == TC10_PARENTS, "TC10 parent substituted")
    no_private_locations(target)
    result = check_index(document['source_projection'])
    result['target_scope'] = 'PINNED_PROJECTED_TARGET_MEANING_NOT_RAW_PRIVATE_CUSTODY_OR_NATIVE_ACCEPTANCE'
    result['target_sha256'] = TARGET_PROJECTION_SHA256
    return result, document['source_projection']


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reject_constant(value):
    raise ValueError("non-finite JSON value: " + value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def parse(data):
    return json.loads(data, object_pairs_hook=unique_object, parse_constant=reject_constant)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def seal(value):
    value["projection_sha256"] = digest(canonical(value))
    return value


def pointer(root, selector):
    require(selector.startswith("/"), "invalid JSON pointer")
    value = root
    for part in selector[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def pinned_bytes(path, data):
    size, sha, blob = PINS[path]
    require(len(data) == size and digest(data) == sha, "immutable bytes differ: " + path)
    actual_blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    require(actual_blob == blob, "Git blob differs: " + path)


def recover(repo, output):
    for path in PINS:
        commit = TRIAD_COMMIT if path.startswith(TRIAD) else COMMIT
        data = subprocess.check_output(["git", "-C", str(repo), "cat-file", "blob", commit + ":" + path])
        pinned_bytes(path, data)
        dest = output / path
        require(not dest.exists() or dest.read_bytes() == data,
                "refusing to replace different recovered bytes: " + str(dest))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return {"scope": "PINNED_PUBLIC_BLOB_RECOVERY", "commits": [COMMIT, TRIAD_COMMIT], "files": len(PINS)}


class Corpus:
    """Pinned complete inputs; archive scripts are data and are never run."""
    def __init__(self, root):
        self.raw = {}
        for path in PINS:
            data = (root / path).read_bytes()
            pinned_bytes(path, data)
            self.raw[path] = data
        self.ama = zipfile.ZipFile(io.BytesIO(self.raw[AMA_ZIP]))
        self.emas = zipfile.ZipFile(io.BytesIO(self.raw[EMAS_ZIP]))
        self.cache = {}
        lineage = parse(self.raw[LINEAGE_MANIFEST])
        trifecta = parse(self.raw[TRIFECTA_MANIFEST])
        self.verify_archive(self.emas, lineage["members"], "EVOLVED_MULTI_AGENT_SYSTEMS_FROZEN_MANIFEST.json")
        self.verify_archive(self.ama, trifecta["members"], "EVOLVED_AMA_FROZEN_MANIFEST.json")
        require(self.ama.read("constituents/EMAS.zip") == self.raw[EMAS_ZIP], "nested EMAS ZIP differs")
        require(self.emas.read("EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json") == self.raw[LEDGER],
                "public ledger and nested original differ")
        lock = parse(self.raw[SOURCE_LOCK])
        entry = lock["lineages"][20]
        require(entry["lineage_id"] == "EVOLVED_MULTI_AGENT_SYSTEMS" and
                entry["property_root"] == "properties" and entry["property_count"] == 76 and
                entry["packet_sha256"] == PINS[EMAS_ZIP][1], "source lock /lineages/20 differs")
        manifest = parse(self.raw[CORPUS_MANIFEST])
        require(manifest["counts"]["properties"] == 1405 and
                manifest["counts"]["lineages"] == 21 and manifest["counts"]["trifectas"] == 7,
                "wider original population differs")
        require(manifest["source_lock"]["sha256"] == PINS[SOURCE_LOCK][1], "corpus source-lock binding differs")
        files = {f["path"]: f for f in manifest["files"]}
        for path in [LEDGER, EMAS_ZIP, AMA_ZIP]:
            require(files[path]["bytes"] == PINS[path][0] and files[path]["sha256"] == PINS[path][1],
                    "corpus file binding differs: " + path)
        self.ledger = parse(self.raw[LEDGER])
        self.old_targets = {r["key"]: (i, r) for i, r in enumerate(parse(self.raw[OLD_TARGET])["properties"])}
        self.tc10 = next(r for r in parse(self.raw[TC_FINDINGS])["findings"] if r["id"] == "TC10")
        self.properties = self.ledger["properties"]
        require([p["PROPERTY_ID"] for p in self.properties] == EXPECTED_IDS, "source property population differs")
        require(dict(Counter(p["CURRENT_STATUS"] for p in self.properties)) == STATUSES, "source statuses differ")
        self.register = self.load(REGISTER)["property_by_key"]
        self.intake = self.load(INTAKE)["rows"]
        self.intake_by_key = {r["global_qualified_key"]: (i, r) for i, r in enumerate(self.intake)}
        self.relations = self.load(RELATIONS)["relations"]
        self.relation_by_id = {r["relation_id"]: r for r in self.relations}
        self.pairs = self.load(MATRIX)["pairs"]
        self.profiles = self.load(PROFILES)
        self.bridges = self.profiles["hand_adjudicated_directional_bridges"]
        self.groups = self.load(GROUPS)["clusters"]
        require(len(self.register) == 278 and len(self.groups) == 32 and len(self.relations) == 20152 and
                len(self.pairs) == 24592 and len(self.bridges) == 105, "AMA source population differs")
        require(len(self.intake_by_key) == 278, "duplicate or absent intake key")
        require(len(self.relation_by_id) == 20152, "duplicate or absent directional identity")
        group_map = {g["cluster_id"]: g for g in self.groups}
        for p in self.properties:
            key = "EMAS:" + p["PROPERTY_ID"]
            row = self.register[key]
            require(row["frozen_record"] == p, "AMA projection changes original: " + key)
            old = self.old_targets[key][1]
            intake_record = self.intake_by_key[key][1]
            require(old["source_row_sha256"] == digest(canonical(intake_record)) and
                    old["source_semantic_disposition"] == p["CURRENT_STATUS"], "public antecedent source correspondence differs")
            for profile in p["DOMAIN_PROFILE"].values():
                pointer(self.ledger, profile["PROFILE_REF"].removeprefix("#"))
            for group in row["cluster_ids"]:
                require(key in group_map[group]["member_properties"], "group membership differs: " + key)
        for relation in self.incident():
            require(relation["source_property"] in self.register and relation["target_property"] in self.register,
                    "unresolved relation endpoint")
            require(bool(relation["assumptions"]["joint_guard"]), "missing relation guard")
            reverse = relation["reverse_relation_id"]
            if reverse:
                other = self.relation_by_id[reverse]
                require(other["source_property"] == relation["target_property"] and
                        other["target_property"] == relation["source_property"], "reverse endpoint mismatch")

    @staticmethod
    def verify_archive(archive, records, embedded):
        names = archive.namelist()
        require(len(names) == len(set(names)) and set(names) == {r["member"] for r in records},
                "archive member population differs")
        require(archive.testzip() is None, "archive CRC failure")
        for record in records:
            data = archive.read(record["member"])
            require(len(data) == record["bytes"] and digest(data) == record["sha256"],
                    "archive member digest differs: " + record["member"])
        manifest = parse(archive.read(embedded))
        inventory = manifest["payload_inventory"]
        require({r["filename"] for r in inventory} == set(names) - {embedded}, "embedded manifest population differs")
        for record in inventory:
            data = archive.read(record["filename"])
            require(len(data) == record["bytes"] and digest(data) == record["sha256"],
                    "embedded payload digest differs: " + record["filename"])

    def load(self, member):
        if member not in self.cache:
            self.cache[member] = parse(self.ama.read(member))
        return self.cache[member]

    def incident(self, key=None):
        if key:
            return [r for r in self.relations if key in (r["source_property"], r["target_property"])]
        return [r for r in self.relations if any(r[k].startswith("EMAS:") for k in ("source_property", "target_property"))]

    def touching_pairs(self, key=None):
        return [(i, p) for i, p in enumerate(self.pairs)
                if (key in (p["left_property"], p["right_property"]) if key else
                    any(p[k].startswith("EMAS:") for k in ("left_property", "right_property")))]

    def touching_bridges(self, key=None):
        return [(i, b) for i, b in enumerate(self.bridges)
                if (key in (b["source"], b["target"]) if key else
                    b["source"].startswith("EMAS:") or b["target"].startswith("EMAS:"))]


def locator(path, selector, record, member=None):
    result = {"path": path, "pointer": selector, "canonical_record_sha256": digest(canonical(record))}
    if member:
        result["archive_member"] = member
    return result


def build(corpus):
    rows = []
    for i, original in enumerate(corpus.properties):
        identity = original["PROPERTY_ID"]
        key = "EMAS:" + identity
        ama = corpus.register[key]
        intake_index, intake = corpus.intake_by_key[key]
        relations = corpus.incident(key)
        pairs = corpus.touching_pairs(key)
        old_index, old_record = corpus.old_targets[key]
        rows.append({
            "id": identity, "original_global_key": "EVOLVED_MULTI_AGENT_SYSTEMS::" + identity,
            "ama_key": key, "name": original["PROPERTY_NAME"], "source_status": original["CURRENT_STATUS"],
            "full_original": locator(LEDGER, f"/properties/{i}", original),
            "full_ama_record": locator(AMA_ZIP, "/property_by_key/" + key, ama, REGISTER),
            "original_intake": locator(AMA_ZIP, f"/rows/{intake_index}", intake, INTAKE),
            "historical_target_candidate": {
                "commit": TRIAD_COMMIT,
                "full_record": locator(OLD_TARGET, f"/properties/{old_index}", old_record),
                "record_json_unallocated": canonical(old_record).decode("utf-8"),
                "record_format": "Canonical JSON string preserves the entire historical record unchanged; its key supplies the same-line unallocated identity scope. Member views decode it.",
                "status": "UNMERGED_PUBLIC_ANTECEDENT_NOT_THE_SEALED_R0044_PREPARATION_UNALLOCATED",
                "current_application": "NOT_IMPORTED; compare with later issue 231 and accepted main before any proposed delta.",
            },
            "source_obligation": {
                "trigger": original["TRIGGER_OR_CONTEXT"], "cheap_path": original["NON_TRIGGER_OR_CHEAP_PATH"],
                "mechanism": original["MATURE_OR_EVOLVED_FORM"], "postcondition": original["OBSERVABLE_POSTCONDITION"],
                "premises": original["DEPENDENCIES_OR_PRECONDITIONS"],
                "authority": original["ACTOR_AND_AUTHORITY_BOUNDARY"], "source_consumer": original["DECISION_OR_CONSUMER"],
                "required_evidence": original["EVIDENCE_NEEDED_AT_LATER_AUDIT"],
                "contrary_evidence": original["CONTRARY_EVIDENCE"], "open_questions": original["OPEN_QUESTIONS"],
                "assumption_sensitivity": original["ASSUMPTION_SENSITIVITY"],
                "source_rationale": original["DISPOSITION_RATIONALE"],
            },
            "groups": ama["cluster_ids"], "source_record_keys": ama["source_ids"],
            "within_lineage_relation_ids": ama["within_lineage_relation_ids"],
            "incident_direction_ids": [r["relation_id"] for r in relations],
            "explicit_pair_indices": [n for n, _ in pairs],
            "bridge_indices": [n for n, _ in corpus.touching_bridges(key)],
            "prepared_target_absorption": None, "prepared_native_disposition": None,
            "prepared_primary_or_secondary": None, "prepared_target_owner": None,
            "prepared_relation_dispositions": None,
            "target_preparation_status": "UNAVAILABLE_PRIVATE_PREPARATION",
            "current_qualification": "PUBLIC_SOURCE_RECONSTRUCTION_ONLY_TARGET_AND_NATIVE_ACCEPTANCE_PENDING",
            "selected_case_owners_from_issue": ["R0022", "R0035", "R0038 (published, canonically unallocated)"] if identity == "EMAS-001" else None,
            "next_lawful_action": {
                "now": "Recover the sealed, published but canonically unallocated R0044 crosswalk and its exact bound target/continuation records for " + key + ".",
                "if_source_trigger_is_selected": original["EVIDENCE_NEEDED_AT_LATER_AUDIT"],
                "otherwise": original["NON_TRIGGER_OR_CHEAP_PATH"],
                "horizon": "Before a target-specific adoption, native qualification or accepting transfer; preserve source custody meanwhile.",
            },
        })
    incident = corpus.incident()
    pairs = corpus.touching_pairs()
    bridges = corpus.touching_bridges()
    unpaired = [r for r in incident if not r["reverse_relation_id"]]
    result = {
        "format": "r0044-public-reconstruction-v1",
        "issue": "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/231",
        "authority": "Published R0044 is canonically unallocated; this newly derived public projection grants no admission or receiving authority.",
        "scope": "NEW_PUBLIC_SOURCE_PROJECTION_NOT_THE_MISSING_SEALED_R0044_CROSSWALK_UNALLOCATED",
        "source_commit": COMMIT, "source_lineage_literal": "Evolved Multi Agent Systems",
        "display_lineage": "Evolved Multi-Agent Systems", "alias": "EMAS",
        "canonical_record_hash_rule": "SHA-256 of UTF-8 JSON: sorted keys, ensure_ascii=False, separators comma/colon; distinct from raw file and ZIP digests.",
        "source_files": [{"path": p, "commit": TRIAD_COMMIT if p.startswith(TRIAD) else COMMIT,
                          "bytes": v[0], "sha256": v[1], "git_blob": v[2], "git_mode": "100644"} for p, v in PINS.items()],
        "complete_archive_member_routes": parse(corpus.raw[TRIFECTA_MANIFEST])["members"],
        "source_status_counts": STATUSES,
        "prepared_target_counts_reported_by_issue_only": PREPARED_COUNTS,
        "prepared_member_assignments_available": False,
        "population": {"EMAS": 76, "EAOSE": 132, "EAA": 70, "AMA_originals": 278,
                       "AMA_original_groups": 32, "all_originals": 1405, "historical_originals": 658,
                       "added_originals": 747, "trifectas": 7, "lineages": 21},
        "source_register_keys": sum(k.startswith("EMAS:") for k in corpus.load(SOURCES)["source_by_key"]),
        "source_register_key_limit": "Packet-local records, not independent studies; shared evidence counts once.",
        "relation_reconstruction": {
            "scope": "Original source relations only; prepared target dispositions unavailable.",
            "archive": AMA_ZIP, "directional_member": RELATIONS, "pair_member": MATRIX,
            "profile_and_bridge_member": PROFILES, "incident_direction_count": len(incident),
            "explicit_reverse_link_count": sum(bool(r["reverse_relation_id"]) for r in incident),
            "unpaired_direction_count": len(unpaired), "explicit_pair_count": len(pairs),
            "explicit_no_material_count": sum(p["relation_status"] == "NO_MATERIAL_RELATION" for _, p in pairs),
            "hand_adjudicated_bridge_count": len(bridges),
            "missing_bridge_means_no_relation": False,
            "directions_are_execution_edges": False,
            "reverse_rule": "Resolve the independently recorded reverse type and guard; a null reverse ID does not establish no reverse-endpoint record.",
        },
        "unpaired_directions": [{"id": r["relation_id"], "source": r["source_property"],
            "target": r["target_property"], "type": r["relation_type"],
            "full_source": locator(AMA_ZIP, f"/relations/{corpus.relations.index(r)}", r, RELATIONS),
            "independent_reverse_endpoint_ids": [o["relation_id"] for o in corpus.incident(r["source_property"])
                if o["source_property"] == r["target_property"] and o["target_property"] == r["source_property"]]}
            for r in unpaired],
        "guarded_source_bridges": [{"source_index": n, "source_record": b,
                                    "prepared_target_disposition": None} for n, b in bridges],
        "TC10": {"known_EMAS_parent_from_issue": "EMAS:EMAS-072", "selected_comparator": "EMAS:EMAS-001",
                 "existing_owners": ["R0022", "R0038 (published, canonically unallocated)", "R0035"],
                 "public_antecedent_commit": TRIAD_COMMIT, "public_antecedent_path": TC_FINDINGS,
                 "public_antecedent_record_json_unallocated": canonical(corpus.tc10).decode("utf-8"),
                 "complete_prepared_parent_guard_mapping": None,
                 "rule": "The full older public TC10 record is available. EMAS-001 does not replace EMAS-072 or qualify all parents; exact correspondence with the later sealed preparation remains unverified."},
        "receiving_route": {
            "host": "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/232#issuecomment-5638961873",
            "sibling_EAOSE": "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/232",
            "sibling_EAA": "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/232#issuecomment-6204277607",
            "accepting_event": "PENDING", "predecessor_retirement": "NOT_AUTHORISED",
            "scope": "One proposed 76-member constituent source return; neither the host 132 nor composition 278/32 is accepted here."},
        "rows": rows,
        "all_row_obligations": [
            "Read the complete original, domain profiles, AMA register, intake, source/access records, groups and incident guarded relations before a connected claim.",
            "Prepared target state, current semantic owner, primary/secondary routing, private residuals and target relation dispositions remain unknown until their sealed records are recovered.",
            "No source rejection becomes a promised feature; no absent bridge becomes an explicit negative; no packet digest establishes receiving.",
            "Only the affected premise expands a decision radius. Keep adequate direct paths, historical failures and unavailable private residuals visible.",
            "A source view is not a target disposition or native accepted JOIN. Full disposition is not full absorption; one comparison qualifies only its selected scope.",
        ],
    }
    return seal(result)


def check_index(index):
    require(index["format"] == "r0044-public-reconstruction-v1", "unsupported projection format")
    unsigned = dict(index)
    supplied = unsigned.pop("projection_sha256")
    require(supplied == digest(canonical(unsigned)), "projection content digest differs")
    require(index["source_commit"] == COMMIT and index["source_lineage_literal"] == "Evolved Multi Agent Systems",
            "source identity differs")
    require(index["prepared_member_assignments_available"] is False, "fabricated target availability")
    require(index["prepared_target_counts_reported_by_issue_only"] == PREPARED_COUNTS, "historical target counts changed")
    rows = index["rows"]
    require([r["id"] for r in rows] == EXPECTED_IDS, "missing, duplicated or reordered member")
    require(dict(Counter(r["source_status"] for r in rows)) == STATUSES, "original status census differs")
    for i, row in enumerate(rows):
        identity = EXPECTED_IDS[i]
        require(row["original_global_key"] == "EVOLVED_MULTI_AGENT_SYSTEMS::" + identity and
                row["ama_key"] == "EMAS:" + identity, "conflated original and navigation identity")
        require(row["full_original"]["path"] == LEDGER and row["full_original"]["pointer"] == f"/properties/{i}",
                "wrong complete-source selector")
        for field in ["full_original", "full_ama_record", "original_intake"]:
            require(re.fullmatch(r"[0-9a-f]{64}", row[field]["canonical_record_sha256"]) is not None,
                    "missing complete-record binding")
        for field in ["prepared_target_absorption", "prepared_native_disposition", "prepared_primary_or_secondary",
                      "prepared_target_owner", "prepared_relation_dispositions"]:
            require(row[field] is None, "unavailable private target decision invented: " + field)
        require(row["target_preparation_status"] == "UNAVAILABLE_PRIVATE_PREPARATION", "missing private gate")
        require(row["historical_target_candidate"]["commit"] == TRIAD_COMMIT and
                row["historical_target_candidate"]["status"] == "UNMERGED_PUBLIC_ANTECEDENT_NOT_THE_SEALED_R0044_PREPARATION_UNALLOCATED",
                "historical target candidate promoted into later preparation")
        obligation = row["source_obligation"]
        for field in ["trigger", "cheap_path", "mechanism", "postcondition", "authority", "source_consumer",
                      "required_evidence", "contrary_evidence", "open_questions", "assumption_sensitivity"]:
            require(bool(obligation[field]), "missing action-distinguishing source field: " + field)
        action = row["next_lawful_action"]
        require(action["if_source_trigger_is_selected"] == obligation["required_evidence"] and
                action["otherwise"] == obligation["cheap_path"] and bool(action["horizon"]), "action/guard mismatch")
        require(all(re.fullmatch(r"AMA-K\d{3}", g) for g in row["groups"]), "malformed group identity")
    relation = index["relation_reconstruction"]
    require(relation["missing_bridge_means_no_relation"] is False and relation["directions_are_execution_edges"] is False,
            "source relation promoted beyond its scope")
    require(index["TC10"]["known_EMAS_parent_from_issue"] == "EMAS:EMAS-072", "TC10 parent lost")
    return {"scope": "INDEX_STRUCTURE_ONLY", "members": len(rows), "projection_sha256": supplied,
            "limit": "Full source/semantic correspondence requires --custody-root; target/native acceptance remains pending."}


def member_view(corpus, index, identity):
    require(identity in EXPECTED_IDS, "unknown member: " + identity)
    row = index["rows"][EXPECTED_IDS.index(identity)]
    key = row["ama_key"]
    original = pointer(corpus.ledger, row["full_original"]["pointer"])
    ama = corpus.register[key]
    relations = corpus.incident(key)
    pairs = [p for _, p in corpus.touching_pairs(key)]
    endpoint_keys = {r[k] for r in relations for k in ["source_property", "target_property"]}
    endpoint_keys.update(p[k] for p in pairs for k in ["left_property", "right_property"])
    context = corpus.load(CONTEXT)
    sources = corpus.load(SOURCES)
    return {
        "scope": "FULL_ORIGINAL_AND_INCIDENT_SOURCE_VIEW_TARGET_PREPARATION_UNAVAILABLE",
        "source_commit": COMMIT, "id": identity, "original": original,
        "domain_profile_definitions": corpus.ledger["domain_profiles"],
        "ama_record": ama, "original_intake": corpus.intake_by_key[key][1],
        "source_records": {k: sources["source_by_key"][k] for k in ama["source_ids"]},
        "source_register_limits": {k: v for k, v in sources.items() if k != "source_by_key"},
        "incident_relations": relations,
        "relation_definitions": {k: v for k, v in corpus.load(RELATIONS).items() if k != "relations"},
        "independent_endpoint_records": {k: corpus.register[k] for k in sorted(endpoint_keys)},
        "explicit_pairs": pairs,
        "pair_scope": {k: v for k, v in corpus.load(MATRIX).items() if k != "pairs"},
        "guarded_bridges": [b for _, b in corpus.touching_bridges(key)],
        "groups": [g for g in corpus.groups if key in g["member_properties"]],
        "semantic_profiles": [p for p in corpus.profiles["profiles"] if key in p["member_keys"]],
        "within_lineage_relations": {k: context["within_lineage_relation_by_key"][k] for k in ama["within_lineage_relation_ids"]},
        "lineage_full_context": context["lineage_top_level_context"]["EMAS"],
        "tension_records": [t for t in corpus.load("EVOLVED_AMA_TENSION_LEDGER.json")["tensions"]
                            if t["id"] in ama["tension_ids"]],
        "target_preparation": {k: v for k, v in row.items() if k.startswith("prepared_") or k == "target_preparation_status"},
        "historical_target_candidate": {**row["historical_target_candidate"],
                                        "decoded_record": parse(row["historical_target_candidate"]["record_json_unallocated"])},
        "complete_context_routes": index["complete_archive_member_routes"],
        "context_route_rule": "All original context documents remain inside the pinned AMA ZIP. The selected materialised fields do not replace those full context records.",
        "current_public_continuation": row["next_lawful_action"],
        "receiving_route": index["receiving_route"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    recover_cmd = sub.add_parser("recover", help="recover exact Git blobs; fetch the named commit separately if absent")
    recover_cmd.add_argument("--repo-root", type=Path, required=True)
    recover_cmd.add_argument("--output", type=Path, required=True)
    build_cmd = sub.add_parser("build", help="derive a new public projection; no private target decisions")
    build_cmd.add_argument("--custody-root", type=Path, required=True)
    build_cmd.add_argument("--output", type=Path, required=True)
    compose_cmd = sub.add_parser("compose", help="join exact sealed preparation to the unchanged historical public projection")
    compose_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    compose_cmd.add_argument("--custody-root", type=Path, required=True)
    compose_cmd.add_argument("--input-map", type=Path, required=True)
    compose_cmd.add_argument("--preparation-row", type=int, default=1)
    compose_cmd.add_argument("--output", type=Path, required=True)
    compose_cmd.add_argument("--repo-root", type=Path, help="complete Git repository containing the selected current source base")
    for command in ["check", "member"]:
        cmd = sub.add_parser(command)
        cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
        cmd.add_argument("--custody-root", type=Path, required=command == "member")
        cmd.add_argument("--input-map", type=Path)
        cmd.add_argument("--repo-root", type=Path, help="source repository for optional sealed-target reconstruction")
        if command == "member":
            cmd.add_argument("--id", required=True)
            cmd.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "recover":
        result = recover(args.repo_root, args.output)
    elif args.command == "build":
        value = build(Corpus(args.custody_root))
        check_index(value)
        write_json(args.output, value)
        result = {"scope": "NEW_PUBLIC_PROJECTION", "members": 76, "projection_sha256": value["projection_sha256"]}
    elif args.command == "compose":
        previous = parse(args.index.read_bytes())
        source = previous.get("source_projection", previous)
        check_index(source)
        corpus = Corpus(args.custody_root)
        require(build(corpus) == source, "historical source projection differs")
        target = prepared_projection(args.input_map, source, corpus, args.preparation_row, args.repo_root)
        value = seal({"format": "r0044-full-disposition-v2",
            "authority": "Published, canonically unallocated R0044; complete disposition is not full absorption, native JOIN or entitled acceptance.",
            "layers": "source_projection is the unchanged historical public v1 object, including its then-unavailable target fields. target_continuation separately supplies the later preparation and current scoped disposition.",
            "source_projection": source, "target_continuation": target})
        write_json(args.output, value)
        result = {"scope": "COMPOSED_CANDIDATE_REQUIRES_INDEPENDENT_QUALIFICATION", "members": 76,
            "target_sha256": digest(canonical(target)), "projection_sha256": value['projection_sha256']}
    else:
        document = parse(args.index.read_bytes())
        result, index = check_document(document)
        require(not args.input_map or args.custody_root, "prepared custody check also requires public custody")
        if args.custody_root:
            corpus = Corpus(args.custody_root)
            require(build(corpus) == index, "projection differs from complete immutable source reconstruction")
            result["scope"] = "PINNED_PUBLIC_SOURCE_RECONSTRUCTION"
            result["relations"] = index["relation_reconstruction"]
            if args.input_map:
                require(document.get('target_continuation') == prepared_projection(args.input_map, index, corpus, repo_root=args.repo_root),
                        "target projection differs from exact sealed inputs")
                result['target_scope'] = 'PINNED_PREPARED_TARGET_RECONSTRUCTION_WITH_SEPARATE_CURRENT_DISPOSITION'
            if args.command == "member":
                view = member_view(corpus, index, args.id)
                if 'target_continuation' in document:
                    target = document['target_continuation']
                    row = target['rows'][EXPECTED_IDS.index(args.id)]
                    view['scope'] = 'FULL_SOURCE_PREPARED_TARGET_AND_SCOPED_CURRENT_DISPOSITION'
                    view['historical_target_preparation_at_v1'] = view.pop('target_preparation')
                    view['target_preparation'] = {**row,
                        'decoded_owner_ids': parse(row['prepared_owner_ids_json_unallocated']),
                        'decoded_target_record': parse(row['prepared_record_json_unallocated']),
                        'decoded_prepared_continuation': parse(row['prepared_continuation_json_unallocated'])}
                    ids = set(row['incident_direction_ids'])
                    view['prepared_incident_relations'] = [r for r in target['target_relations'] if r['id'] in ids]
                    view['prepared_groups'] = [parse(r['record_json_unallocated']) for r in target['groups'] if r['id'] in index['rows'][EXPECTED_IDS.index(args.id)]['groups']]
                    view['prepared_context_dispositions'] = [r for r in parse(target['context_dispositions_json_unallocated']) if row['ama_key'] in r['property_keys']]
                    view['prepared_corrected_carrier_decisions'] = [parse(r['record_json_unallocated']) for r in target['corrected_carrier_decisions'] if r['id'] in row['corrected_carrier_routing']['concern_routes']]
                    view['prepared_explicit_bridges'] = [r for r in parse(target['explicit_bridge_dispositions_json_unallocated']) if row['ama_key'] in (r['source'], r['target'])]
                    view['current_public_continuation'] = row['current']
                    view['current_source_owners'] = target['current_source_owners']
                    view['current_receiving_scope'] = target['current_scope']
                    view['TC10'] = target['TC10']
                write_json(args.output, view)
                result = {"scope": view["scope"], "id": args.id, "output_bytes": args.output.stat().st_size,
                          "sha256": digest(args.output.read_bytes())}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError, TypeError, OSError, zipfile.BadZipFile, subprocess.CalledProcessError) as exc:
        print("R0044_REJECTED: " + str(exc), file=sys.stderr)  # published, canonically unallocated
        sys.exit(1)
