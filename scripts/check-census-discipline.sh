#!/usr/bin/env bash
# Deterministically exercise the issue #79 census-discipline control bank.
set -euo pipefail

fixture="${1:-fixtures/census-discipline/cases.json}"
[ -f "$fixture" ] || {
  printf 'check-census-discipline: fixture not found: %s\n' "$fixture" >&2
  exit 2
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-census-discipline: Python is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$fixture" <<'PY'
import collections
import copy
import json
import sys
from pathlib import Path


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def require_exact(value, keys, owner):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(f"{owner} keys invalid")
    return value


def nonempty_string(value):
    return type(value) is str and bool(value.strip())


def classify_enumeration(case):
    members = case["enumerated_members"]
    valid_members = (
        type(members) is list and bool(members) and
        all(nonempty_string(member) for member in members) and
        len(members) == len(set(members)))
    complete = (
        case["claim_mode"] == "census" and
        type(case["population_size"]) is int and
        type(case["examined_count"]) is int and valid_members and
        case["population_size"] == len(members) and
        case["examined_count"] == len(members))
    return "PASS" if complete else "FAIL"


def classify_distinct_hashes(case):
    rows = case["rows"]
    if type(rows) is not list or len(rows) < 2:
        return "FAIL"
    ids = []
    row_hashes = {}
    by_hash = collections.defaultdict(list)
    for row in rows:
        if type(row) is not dict or set(row) != {"id", "sha256"}:
            return "FAIL"
        if not nonempty_string(row["id"]) or not nonempty_string(row["sha256"]):
            return "FAIL"
        ids.append(row["id"])
        row_hashes[row["id"]] = row["sha256"]
        by_hash[row["sha256"]].append(row["id"])
    if len(ids) != len(set(ids)):
        return "FAIL"

    witness = case["discrimination_witness"]
    witnessed = False
    if type(witness) is dict and set(witness) == {
            "known_distinct_items", "observed_hashes"}:
        items = witness["known_distinct_items"]
        hashes = witness["observed_hashes"]
        witnessed = (
            type(items) is list and len(items) == 2 and
            len(set(items)) == 2 and all(item in row_hashes for item in items) and
            type(hashes) is list and len(hashes) == 2 and
            len(set(hashes)) == 2 and
            hashes == [row_hashes[item] for item in items])

    receipts = case["collision_receipts"]
    if type(receipts) is not list:
        return "FAIL"
    receipt_by_hash = {}
    for receipt in receipts:
        if type(receipt) is not dict or set(receipt) != {
                "sha256", "members", "reason"}:
            return "FAIL"
        if not nonempty_string(receipt["sha256"]) or \
                not nonempty_string(receipt["reason"]):
            return "FAIL"
        if type(receipt["members"]) is not list or len(receipt["members"]) < 2:
            return "FAIL"
        receipt_by_hash[receipt["sha256"]] = set(receipt["members"])

    uncovered = []
    for digest, members in by_hash.items():
        if len(members) > 1 and receipt_by_hash.get(digest) != set(members):
            uncovered.append(digest)
    if case["claims_distinct"] is not True:
        return "PASS"
    return "PASS" if witnessed and not uncovered else "FAIL"


def classify_dead_file(case):
    literal = case["literal_basename"]
    composed = case["stem_dirname"]
    move_run = case["red_first_move_run"]
    for method, owner in ((literal, "literal_basename"),
                          (composed, "stem_dirname")):
        require_exact(method, {"ran", "hits"}, owner)
        if type(method["ran"]) is not bool or type(method["hits"]) is not list:
            return "FAIL"
    require_exact(move_run, {"ran", "consumer_failed"}, "red_first_move_run")
    if type(move_run["ran"]) is not bool or \
            type(move_run["consumer_failed"]) is not bool:
        return "FAIL"

    proof_complete = (
        literal["ran"] is True and composed["ran"] is True and
        (case["suite_exists"] is False or move_run["ran"] is True))
    live_signal = bool(literal["hits"] or composed["hits"] or
                       move_run["consumer_failed"])
    warranted = "RETAIN" if live_signal else "ARCHIVE"
    return "PASS" if proof_complete and \
        case["proposed_disposition"] == warranted else "FAIL"


def classify_dismissed(case):
    anomaly = case["in_rubric_anomaly"]
    if not nonempty_string(anomaly) or case["global_verdict"] != "PASS":
        return "PASS"
    row = case["dismissed_observation"]
    complete = (
        type(row) is dict and set(row) == {"what", "why", "falsifier"} and
        all(nonempty_string(row[key]) for key in ("what", "why", "falsifier")) and
        row["what"].strip().casefold() == anomaly.strip().casefold())
    return "PASS" if complete else "FAIL"


def classify(case):
    kind = case.get("kind")
    if kind == "enumeration-authority":
        return classify_enumeration(case)
    if kind == "distinct-hash-census":
        return classify_distinct_hashes(case)
    if kind == "dead-file-proof":
        return classify_dead_file(case)
    if kind == "dismissed-observation":
        return classify_dismissed(case)
    raise ValueError(f"unsupported control kind: {kind!r}")


PUBLIC_DISPOSITIONS = {
    "present-correct",
    "discoverably-delegated",
    "historical-intentional",
    "not-user-facing",
    "missing",
}

PUBLIC_FIELD_TYPES = {
    **dict.fromkeys("""
        id kind expected topic owner_source readme_disposition docs_disposition
        route reference current_release current_runtime readme_release
        readme_runtime docs_release docs_runtime publication_state source_state
        generated_state live_state changelog_state release_ledger_state
        portal_metadata_state public_wording_state historical_release
        historical_context compatibility_alias public_copy public_copy_locale
        mutation_target claim existing_claim_boundary_result projection_result
        capability population_definition enumeration_source change_class
        coverage_claim readme_wording docs_wording intended_audience consumer_job
        declared_authority diagram relation_type relation_statement
        relation_evidence
    """.split(), str),
    **dict.fromkeys("""
        material supported exists discoverable maintained user_facing
        current_state_is_distinct generator_output_preserved
        canonical_literals_preserved owner_source_updated regenerated
        canonical_literal_preserved optional excluded unsupported_public_claim
        distinct_evidence_witness material_public_or_release_effect
        readme_or_public_docs_declared_success_carrier
        intended_current_complete_or_release_final_claim
        projection_record_present release_docs_close_claim owner_source_exists
        generated_output_updated regenerated_from_owner
        landed_postcondition_checked source_only_route_required
        generated_from_owner current_product relation_valid
    """.split(), bool),
    **dict.fromkeys("population_size examined_count".split(), int),
}
PUBLIC_STRING_LISTS = {
    "enumerated_members", "dispositioned_members", "known_distinct_topics",
    "readme_facts", "docs_facts",
}
PUBLIC_REQUIRED_STRINGS = set("""
    current_release current_runtime readme_release readme_runtime docs_release
    docs_runtime historical_release source_state generated_state live_state
    intended_audience consumer_job declared_authority diagram relation_type
    relation_statement relation_evidence
""".split())

PUBLIC_AUDIENCES = {
    "prospective-user", "source-only-user", "advanced-user", "operator",
    "contributor-maintainer", "release-reader", "evidence-auditor",
}
PUBLIC_JOB_ABSTRACTIONS = {
    "orientation": "product-explanation",
    "operation": "operational-guidance",
    "contribution": "maintainer-procedure",
    "chronology": "release-chronology",
    "qualification": "exact-evidence",
    "deep-reference": "deep-mechanism",
}
PUBLIC_PLACEMENT_ROLES = {
    "authoritative", "summary-link", "historical", "not-applicable",
}
PUBLIC_ABSTRACTIONS = {
    *PUBLIC_JOB_ABSTRACTIONS.values(), "concise-pointer",
}
PUBLIC_PLACEMENT_KEYS = {
    "placement_id", "surface", "owner_id", "role", "abstraction",
    "current", "discoverable", "entrypoint", "source_only",
    "authority_ref", "evidence", "requires_campaign_history",
}
PUBLIC_RELATION_TYPES = {
    "mandatory-flow", "conditional-flow", "optional-tooling",
    "authority-boundary", "evidence-boundary", "generated-surface",
    "terminal-state",
}


def public_case(case, keys):
    require_exact(case, {"id", "kind", "expected", *keys}, case.get("id"))
    for field in {"id", "kind", "expected", *keys}:
        expected_type = PUBLIC_FIELD_TYPES.get(field)
        if expected_type is not None and type(case[field]) is not expected_type:
            raise ValueError(f"{field} must be {expected_type.__name__}")
        if field in PUBLIC_REQUIRED_STRINGS and not case[field].strip():
            raise ValueError(f"{field} must be non-empty")
        if field in PUBLIC_STRING_LISTS and (
                type(case[field]) is not list or
                any(not nonempty_string(value) for value in case[field])):
            raise ValueError(f"{field} must be a list of non-empty strings")


def allowed(value, values, owner):
    if value not in values:
        raise ValueError(f"{owner} enum invalid")
    return value


def classify_public_projection(case):
    kind = case.get("kind")
    if kind == "topic-projection":
        public_case(case, {
            "topic", "owner_source", "material", "readme_disposition",
            "docs_disposition"})
        dispositions = {case["readme_disposition"], case["docs_disposition"]}
        complete = (
            nonempty_string(case["topic"]) and
            nonempty_string(case["owner_source"]) and
            dispositions <= PUBLIC_DISPOSITIONS and
            (case["material"] is False or "missing" not in dispositions))
    elif kind == "route-projection":
        public_case(case, {
            "route", "supported", "readme_disposition", "docs_disposition"})
        dispositions = {case["readme_disposition"], case["docs_disposition"]}
        complete = (
            nonempty_string(case["route"]) and
            dispositions <= PUBLIC_DISPOSITIONS and
            (case["supported"] is False or "missing" not in dispositions))
    elif kind == "reference-integrity":
        public_case(case, {"topic", "reference", "exists", "discoverable"})
        complete = (
            nonempty_string(case["topic"]) and
            nonempty_string(case["reference"]) and
            case["exists"] is True and case["discoverable"] is True)
    elif kind == "current-state-parity":
        public_case(case, {
            "current_release", "current_runtime", "readme_release",
            "readme_runtime", "docs_release", "docs_runtime"})
        complete = (
            case["readme_release"] == case["docs_release"] ==
            case["current_release"] and
            case["readme_runtime"] == case["docs_runtime"] ==
            case["current_runtime"])
    elif kind == "semantic-currency":
        public_case(case, {
            "publication_state", "source_state", "generated_state",
            "live_state", "changelog_state", "release_ledger_state",
            "portal_metadata_state"})
        allowed(case["publication_state"], {
            "prepublication", "postpublication"}, "publication_state")
        states_match = (
            case["source_state"] == case["generated_state"] ==
            case["live_state"])
        transition = (
            "postpublication-current" if
            case["publication_state"] == "postpublication" else
            "prepublication-current")
        complete = states_match and all(
            case[field] == transition for field in (
                "changelog_state", "release_ledger_state",
                "portal_metadata_state"))
    elif kind == "publication-transition":
        public_case(case, {"publication_state", "public_wording_state"})
        allowed(case["publication_state"], {
            "prepublication", "postpublication"}, "publication_state")
        allowed(case["public_wording_state"], {
            "prepublication-current", "postpublication-current"},
            "public_wording_state")
        transition = {
            "prepublication": "prepublication-current",
            "postpublication": "postpublication-current",
        }.get(case["publication_state"])
        complete = transition is not None and case["public_wording_state"] == transition
    elif kind == "delegation":
        public_case(case, {
            "readme_disposition", "reference", "exists", "maintained",
            "discoverable"})
        allowed(case["readme_disposition"], PUBLIC_DISPOSITIONS,
                "readme_disposition")
        complete = (
            case["readme_disposition"] == "discoverably-delegated" and
            nonempty_string(case["reference"]) and
            case["exists"] is True and case["maintained"] is True and
            case["discoverable"] is True)
    elif kind == "internal-disposition":
        public_case(case, {
            "user_facing", "readme_disposition", "docs_disposition",
            "owner_source", "reason"})
        allowed(case["readme_disposition"], PUBLIC_DISPOSITIONS,
                "readme_disposition")
        allowed(case["docs_disposition"], PUBLIC_DISPOSITIONS,
                "docs_disposition")
        complete = (
            case["user_facing"] is False and
            case["readme_disposition"] == "not-user-facing" and
            case["docs_disposition"] == "not-user-facing" and
            nonempty_string(case["owner_source"]) and
            nonempty_string(case["reason"]))
    elif kind == "historical-context":
        public_case(case, {
            "current_release", "historical_release", "historical_context",
            "compatibility_alias", "current_state_is_distinct"})
        complete = (
            case["current_release"] != case["historical_release"] and
            nonempty_string(case["historical_context"]) and
            nonempty_string(case["compatibility_alias"]) and
            case["current_state_is_distinct"] is True)
    elif kind == "language-owner-boundary":
        public_case(case, {
            "public_copy", "public_copy_locale", "generator_output_preserved",
            "canonical_literals_preserved"})
        complete = (
            nonempty_string(case["public_copy"]) and
            case["public_copy_locale"] == "en-GB" and
            case["generator_output_preserved"] is True and
            case["canonical_literals_preserved"] is True)
    elif kind == "owner-first-mutation":
        public_case(case, {
            "mutation_target", "owner_source_updated", "regenerated",
            "canonical_literal_preserved"})
        allowed(case["mutation_target"], {
            "generated-diagram-block", "canonical-literal",
            "ordinary-owner-source"}, "mutation_target")
        controlled = case["mutation_target"] != "ordinary-owner-source"
        complete = (
            not controlled or
            (case["owner_source_updated"] is True and
             case["regenerated"] is True and
             case["canonical_literal_preserved"] is True))
    elif kind == "existing-gate-composition":
        public_case(case, {
            "claim", "existing_claim_boundary_result", "projection_result"})
        complete = (
            nonempty_string(case["claim"]) and
            case["existing_claim_boundary_result"] == "PASS" and
            case["projection_result"] == "PASS")
    elif kind == "optional-exclusion":
        public_case(case, {
            "capability", "optional", "excluded", "unsupported_public_claim"})
        complete = (
            nonempty_string(case["capability"]) and
            case["optional"] is True and case["excluded"] is True and
            case["unsupported_public_claim"] is False)
    elif kind == "projection-census":
        public_case(case, {
            "population_definition", "population_size", "examined_count",
            "enumeration_source", "enumerated_members",
            "dispositioned_members"})
        members = case["enumerated_members"]
        dispositions = case["dispositioned_members"]
        complete = (
            nonempty_string(case["population_definition"]) and
            nonempty_string(case["enumeration_source"]) and
            type(members) is list and type(dispositions) is list and
            len(members) == len(set(members)) and
            len(dispositions) == len(set(dispositions)) and
            case["population_size"] == len(members) and
            case["examined_count"] == len(dispositions) and
            set(dispositions) == set(members))
    elif kind == "projection-discrimination":
        public_case(case, {
            "topics", "known_distinct_topics", "distinct_evidence_witness"})
        topics = case["topics"]
        rows_valid = (
            type(topics) is list and len(topics) >= 2 and
            all(type(row) is dict and set(row) == {
                "topic", "owner_source", "evidence"} and
                all(nonempty_string(row[field]) for field in row)
                for row in topics))
        by_topic = {row["topic"]: row for row in topics} if rows_valid else {}
        known = case["known_distinct_topics"]
        known_valid = (
            type(known) is list and len(known) >= 2 and
            len(known) == len(set(known)) and
            all(topic in by_topic for topic in known))
        collapsed = known_valid and len({by_topic[topic]["evidence"] for topic in known}) < len(known)
        complete = rows_valid and known_valid and (
            not collapsed or case["distinct_evidence_witness"] is True)
    elif kind == "activation-boundary":
        public_case(case, {
            "change_class", "material_public_or_release_effect",
            "readme_or_public_docs_declared_success_carrier",
            "intended_current_complete_or_release_final_claim",
            "projection_record_present"})
        activated = all(case[field] is True for field in (
            "material_public_or_release_effect",
            "readme_or_public_docs_declared_success_carrier",
            "intended_current_complete_or_release_final_claim"))
        complete = (
            nonempty_string(case["change_class"]) and
            case["projection_record_present"] is activated)
    elif kind == "partial-coverage":
        public_case(case, {
            "population_size", "examined_count", "coverage_claim",
            "release_docs_close_claim"})
        allowed(case["coverage_claim"], {"partial", "full"},
                "coverage_claim")
        complete = (
            type(case["population_size"]) is int and
            type(case["examined_count"]) is int and
            0 <= case["examined_count"] < case["population_size"] and
            case["coverage_claim"] == "partial" and
            case["release_docs_close_claim"] is False)
    elif kind == "generated-owner":
        public_case(case, {
            "owner_source_exists", "owner_source_updated",
            "generated_output_updated", "regenerated_from_owner",
            "landed_postcondition_checked"})
        complete = (
            case["owner_source_exists"] is True and
            case["owner_source_updated"] is True and
            case["generated_output_updated"] is True and
            case["regenerated_from_owner"] is True and
            case["landed_postcondition_checked"] is True)
    elif kind == "factual-parity":
        public_case(case, {
            "readme_wording", "docs_wording", "readme_facts", "docs_facts"})
        readme_facts = case["readme_facts"]
        docs_facts = case["docs_facts"]
        complete = (
            nonempty_string(case["readme_wording"]) and
            nonempty_string(case["docs_wording"]) and
            type(readme_facts) is list and type(docs_facts) is list and
            bool(readme_facts) and len(readme_facts) == len(set(readme_facts)) and
            len(docs_facts) == len(set(docs_facts)) and
            set(readme_facts) == set(docs_facts))
    elif kind == "audience-owner-fit":
        public_case(case, {
            "topic", "intended_audience", "consumer_job",
            "declared_authority", "source_only_route_required", "placements"})
        allowed(case["intended_audience"], PUBLIC_AUDIENCES,
                "intended_audience")
        allowed(case["consumer_job"], set(PUBLIC_JOB_ABSTRACTIONS),
                "consumer_job")
        placements = case["placements"]
        if type(placements) is not list or not placements:
            raise ValueError("placements must be a non-empty list")
        normalized = []
        for row in placements:
            if type(row) is not dict or set(row) != PUBLIC_PLACEMENT_KEYS:
                raise ValueError("placement keys invalid")
            for field in (
                    "placement_id", "surface", "owner_id", "role",
                    "abstraction", "authority_ref", "evidence"):
                if not nonempty_string(row[field]):
                    raise ValueError(f"placement {field} must be non-empty")
            for field in (
                    "current", "discoverable", "entrypoint", "source_only",
                    "requires_campaign_history"):
                if type(row[field]) is not bool:
                    raise ValueError(f"placement {field} must be bool")
            allowed(row["role"], PUBLIC_PLACEMENT_ROLES, "placement role")
            allowed(row["abstraction"], PUBLIC_ABSTRACTIONS,
                    "placement abstraction")
            normalized.append(row)
        placement_ids = [row["placement_id"] for row in normalized]
        if len(placement_ids) != len(set(placement_ids)):
            raise ValueError("placement identities must be unique")
        by_placement = {row["placement_id"]: row for row in normalized}
        if any(row["authority_ref"] not in by_placement for row in normalized):
            raise ValueError("placement authority_ref is unresolved")
        authorities = [
            row for row in normalized
            if row["role"] == "authoritative" and row["current"] is True]
        authority = authorities[0] if len(authorities) == 1 else None
        expected_abstraction = PUBLIC_JOB_ABSTRACTIONS[case["consumer_job"]]
        authority_valid = bool(authority) and (
            authority["owner_id"] == case["declared_authority"] and
            authority["abstraction"] == expected_abstraction and
            authority["discoverable"] is True and
            authority["authority_ref"] == authority["placement_id"] and
            authority["requires_campaign_history"] is False)
        current_roles_valid = all(
            row["role"] in {"authoritative", "summary-link"}
            for row in normalized if row["current"] is True)
        inactive_roles_valid = all(
            row["role"] in {"historical", "not-applicable"}
            for row in normalized if row["current"] is False)
        summary_links_valid = bool(authority) and all(
            row["abstraction"] == "concise-pointer" and
            row["discoverable"] is True and
            row["authority_ref"] == authority["placement_id"] and
            row["requires_campaign_history"] is False
            for row in normalized
            if row["current"] is True and row["role"] == "summary-link")
        entrypoints = [row for row in normalized if row["entrypoint"] is True]
        entrypoints_valid = bool(entrypoints) and all(
            row["current"] is True and row["discoverable"] is True and
            row["role"] in {"authoritative", "summary-link"} and
            row["requires_campaign_history"] is False
            for row in entrypoints)
        source_only_valid = (
            case["source_only_route_required"] is False or
            any(row["source_only"] is True for row in entrypoints))
        complete = (
            nonempty_string(case["topic"]) and
            nonempty_string(case["declared_authority"]) and
            authority_valid and current_roles_valid and inactive_roles_valid and
            summary_links_valid and entrypoints_valid and source_only_valid)
    elif kind == "diagram-projection":
        public_case(case, {
            "diagram", "owner_source", "generated_from_owner",
            "current_product", "relation_type", "relation_statement",
            "relation_evidence", "relation_valid"})
        allowed(case["relation_type"], PUBLIC_RELATION_TYPES, "relation_type")
        complete = (
            nonempty_string(case["diagram"]) and
            nonempty_string(case["owner_source"]) and
            nonempty_string(case["relation_statement"]) and
            nonempty_string(case["relation_evidence"]) and
            case["generated_from_owner"] is True and
            case["current_product"] is True and
            case["relation_valid"] is True)
    elif kind == "rendered-consumer-boundary":
        public_case(case, {
            "projection", "owner_source", "material_public_claim",
            "rendering_material_to_meaning", "source_or_generator_result",
            "consumer_surface", "consumer_matches_claim",
            "candidate_identity_bound", "rendered_consumer_result",
            "rendered_consumer_evidence", "semantic_detail_preserved",
            "source_backed_correction", "source_backed_correction_evidence",
            "cheap_path_reason"})
        for field in (
                "material_public_claim", "rendering_material_to_meaning",
                "consumer_matches_claim", "candidate_identity_bound",
                "semantic_detail_preserved", "source_backed_correction"):
            if case[field] is not None and type(case[field]) is not bool:
                raise ValueError(f"{field} must be bool or null")
        correction_evidence = case["source_backed_correction_evidence"]
        if correction_evidence is not None and not nonempty_string(correction_evidence):
            raise ValueError(
                "source_backed_correction_evidence must be a non-empty string or null")
        allowed(case["source_or_generator_result"], {"PASS", "FAIL"},
                "source_or_generator_result")
        allowed(case["rendered_consumer_result"], {
            "PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"},
            "rendered_consumer_result")
        rendered = case["rendering_material_to_meaning"]
        complete = (
            nonempty_string(case["projection"]) and
            nonempty_string(case["owner_source"]) and
            case["material_public_claim"] is True and
            type(rendered) is bool and
            case["source_or_generator_result"] == "PASS" and
            ((rendered and
             nonempty_string(case["consumer_surface"]) and
              case["consumer_matches_claim"] is True and
              case["candidate_identity_bound"] is True and
              case["rendered_consumer_result"] == "PASS" and
              nonempty_string(case["rendered_consumer_evidence"]) and
              ((case["semantic_detail_preserved"] is True and
                case["source_backed_correction"] is False and
                case["source_backed_correction_evidence"] is None) or
               (case["semantic_detail_preserved"] is False and
                case["source_backed_correction"] is True and
                nonempty_string(case["source_backed_correction_evidence"]))) and
              case["cheap_path_reason"] is None) or
             (not rendered and
              case["consumer_surface"] is None and
              case["consumer_matches_claim"] is None and
              case["candidate_identity_bound"] is None and
              case["rendered_consumer_result"] == "NOT_APPLICABLE" and
              case["rendered_consumer_evidence"] is None and
              case["semantic_detail_preserved"] is None and
              case["source_backed_correction"] is None and
              case["source_backed_correction_evidence"] is None and
              nonempty_string(case["cheap_path_reason"]))))
    else:
        raise ValueError(f"unsupported public-projection kind: {kind!r}")
    return "PASS" if complete else "FAIL"


path = Path(sys.argv[1])
bank = json.loads(
    path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
schema = bank.get("schema") if type(bank) is dict else None
if schema == "implementaudit-census-discipline-fixtures-v1":
    require_exact(bank, {"schema", "controls", "phase_cases"}, "fixture bank")
    if type(bank["phase_cases"]) is not list or not bank["phase_cases"]:
        raise ValueError("phase_cases must be a non-empty list")
    required_ids = {
        "R6-F1", "R6-F1n", "R6-F5", "R6-F5c", "R6-F6",
        "R6-F9", "R6-F10", "R6-F11", "R6-F11n",
    }
    classifier = classify
elif schema == "implementaudit-public-projection-fixtures-v1":
    require_exact(
        bank, {"schema", "controls", "held_out_mutations"}, "fixture bank")
    required_ids = {
        "R29-F1", "R29-F2", "R29-F3", "R29-F4", "R29-F5", "R29-F6",
        "R29-F7", "R29-F8", "R29-F9", "R29-F10", "R29-F10n",
        "R29-F11", "R29-F12", "R29-F13", "R29-F14", "R29-F15",
        "R29-F15a", "R29-F15b", "R29-F15c", "R29-F15d", "R29-F15e", "R29-F16",
         "R29-F17",
         "R29-F18",
         "R29-F19", "R29-F20", "R29-F21", "R29-F22", "R29-F23",
         "R29-F24", "R29-F25", "R29-F26", "R29-F27", "R29-F28",
         "R29-F29", "R29-F30", "R29-F31", "R29-F32", "R29-F33", "R29-F34",
         "R29-F35", "R29-F36", "R29-F37", "R29-F38", "R29-F39",
         "S3E-W04-F1", "S3E-W04-F2", "S3E-W04-F3", "S3E-W04-F4",
         "S3E-W04-F5",
    }
    classifier = classify_public_projection
else:
    raise ValueError("fixture bank schema invalid")
if type(bank["controls"]) is not list or not bank["controls"]:
    raise ValueError("controls must be a non-empty list")

ids = [case.get("id") for case in bank["controls"]]
if set(ids) != required_ids or len(ids) != len(set(ids)):
    raise ValueError("fixture control identity set invalid")

if schema == "implementaudit-public-projection-fixtures-v1":
    source_paths = {
        "s3e": Path("docs/portal/pages/research-lineage-s3e.html"),
        "css": Path("docs/portal/pages/research-lineage-evolved-css.html"),
    }
    if any(not source.is_file() for source in source_paths.values()):
        raise ValueError("S³E public source owner is missing")
    source_text = {
        key: source.read_text(encoding="utf-8")
        for key, source in source_paths.items()
    }
    source_anchors = {
        "canonical-title": (
            "s3e",
            "State Synthesis Substrate Engineering: Evolved-SSDDRFCSS"),
        "one-substrate-no-methodology-mode": (
            "s3e",
            "They do not create nine runtimes, selectable methodology modes, or a fixed ceremony."),
        "ordinary-work-cheap-path": (
            "css",
            "When one authoritative deterministic discriminator settles ordinary bounded work, use it and stop. No trigger means no added ceremony, record, or family machinery."),
        "current-package-projection-boundary": (
            "s3e",
            "The canonical plugin and standalone compatibility projections are mechanically checked independently; they are not literal member-for-member copies."),
    }

    def missing_source_anchors(text_by_owner):
        return [
            anchor_id for anchor_id, (owner, literal) in source_anchors.items()
            if literal not in text_by_owner[owner]
        ]

    missing = missing_source_anchors(source_text)
    if missing:
        raise ValueError(f"S³E public source anchor missing: {missing}")
    for anchor_id, (owner, literal) in source_anchors.items():
        mutated = dict(source_text)
        mutated[owner] = mutated[owner].replace(literal, "CORRUPTED", 1)
        if anchor_id not in missing_source_anchors(mutated):
            raise ValueError(f"S³E held-out source mutation false-passed: {anchor_id}")

failures = []
for case in bank["controls"]:
    actual = classifier(case)
    if actual != case.get("expected"):
        failures.append(
            f"{case['id']}: expected {case.get('expected')!r}, got {actual!r}")
if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

if schema == "implementaudit-public-projection-fixtures-v1":
    mutations = bank["held_out_mutations"]
    if type(mutations) is not list or not mutations:
        raise ValueError("held_out_mutations must be a non-empty list")
    mutation_ids = [row.get("id") for row in mutations]
    required_mutation_ids = {
        "R29-H1-material-type", "R29-H2-supported-type",
        "R29-H3-unknown-mutation-target", "R29-H4-unknown-disposition",
        "R29-H5-null-release-identities", "R29-H6-null-source-states",
        "R29-H7-non-string-historical-identities",
        "R29-H8-boolean-census-counts-and-integer-members",
        "R29-H9-integer-fact-lists",
        "R29-H10-blank-consumer-job", "R29-H11-non-list-placements",
        "R29-H12-unknown-placement-role",
        "R29-H13-duplicate-placement-identities",
        "R29-H14-unknown-diagram-relation",
        "R29-H15-integer-campaign-history",
        "R29-H16-unknown-rendered-result",
        "R29-H17-integer-semantic-preservation",
        "R29-H18-string-consumer-match",
        "R29-H19-missing-source-correction-evidence",
    }
    if set(mutation_ids) != required_mutation_ids or len(mutation_ids) != len(set(mutation_ids)):
        raise ValueError("held-out mutation identity set invalid")
    by_id = {case["id"]: case for case in bank["controls"]}
    activation_fields = (
        "material_public_or_release_effect",
        "readme_or_public_docs_declared_success_carrier",
        "intended_current_complete_or_release_final_claim")
    anti_triggers = dict(zip(
        activation_fields, ("R29-F15e", "R29-F15b", "R29-F15c")))
    for omitted, control_id in anti_triggers.items():
        case = by_id[control_id]
        if (case["kind"] != "activation-boundary" or
                case[omitted] is not False or
                any(case[field] is not True for field in activation_fields
                    if field != omitted) or
                case["projection_record_present"] is not False or
                case["expected"] != "PASS"):
            raise ValueError(f"{control_id} activation anti-trigger invalid")
        if case["projection_record_present"] is all(
                case[field] is True for field in activation_fields
                if field != omitted):
            raise ValueError(f"activation mutation removing {omitted} survives")
    for row in mutations:
        single_keys = {"id", "target_id", "field", "replacement", "expected"}
        multi_keys = {"id", "target_id", "changes", "expected"}
        variant_keys = {*multi_keys, "variants"}
        if (type(row) is not dict or
                set(row) not in (single_keys, multi_keys, variant_keys)):
            raise ValueError(f"{row.get('id')} held-out mutation keys invalid")
        if row["target_id"] not in by_id or row["expected"] != "ERROR":
            raise ValueError(f"{row['id']} held-out mutation contract invalid")
        changes = [
            {row["field"]: row["replacement"]}
            if set(row) == single_keys else row["changes"]]
        if "variants" in row:
            if type(row["variants"]) is not list or not row["variants"]:
                raise ValueError(f"{row['id']} mutation variants invalid")
            changes += row["variants"]
        for index, change_set in enumerate(changes):
            mutated = copy.deepcopy(by_id[row["target_id"]])
            if type(change_set) is not dict or not change_set:
                raise ValueError(f"{row['id']} mutation changes invalid")
            for field, replacement in change_set.items():
                if field not in mutated:
                    raise ValueError(f"{row['id']} mutation field missing")
                mutated[field] = replacement
            try:
                classifier(mutated)
            except ValueError:
                actual = "ERROR"
            else:
                actual = "CLASSIFIED"
            if actual != row["expected"]:
                failures.append(
                    f"{row['id']}[{index}]: expected {row['expected']!r}, got {actual!r}")
    if failures:
        sys.stderr.write("\n".join(failures) + "\n")
        raise SystemExit(1)

sys.stdout.write(
    f"check-census-discipline: ok ({len(ids)} controls; {schema})\n")
PY
