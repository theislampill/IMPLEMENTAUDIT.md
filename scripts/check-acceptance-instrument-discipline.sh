#!/usr/bin/env bash
# Deterministically exercise the issues #85 and #164 acceptance/instrument controls.
set -euo pipefail

fixture="${1:-fixtures/acceptance-instrument-discipline/cases.json}"
[ -f "$fixture" ] || {
  printf 'check-acceptance-instrument-discipline: fixture not found: %s\n' \
    "$fixture" >&2
  exit 2
}
repository=""
if [ "${2:-}" = "--repository" ] && [ -n "${3:-}" ] && [ "$#" -eq 3 ]; then
  repository="$3"
elif [ "$#" -gt 1 ]; then
  printf 'usage: %s [fixture] [--repository PATH]\n' "$0" >&2
  exit 2
fi

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-acceptance-instrument-discipline: python is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$fixture" "$repository" <<'PY'
import json
import re
import subprocess
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


MUTATION_KEYS = {
    "id", "surface", "event_order", "same_claim", "product_changed",
    "old_verdict", "new_verdict", "property_evidence",
    "original_witness", "witness_retained", "matrix",
    "authoritative_instrument", "held_out_passed", "population", "proof",
    "contract_change", "property_preserved", "record_complete", "expected",
}
MATRIX_KEYS = {
    "old_product_old_evaluator", "old_product_new_evaluator",
    "new_product_old_evaluator", "new_product_new_evaluator",
}
HELD_OUT_SET = {"positive", "negative", "boundary", "adjacent"}
CONTRACT_KEYS = {
    "owner", "effective_boundary", "migration_effect", "population_effect",
}
RECORD_KEYS = {
    "property_owner", "consumer", "changes", "residual_risk", "rollback",
    "stop_condition",
}
PARITY_KEYS = {"input", "primary_verdict", "secondary_verdict"}
POLICY_KEYS = {
    "id", "candidate_changed", "path_match", "semantic_owner_intersection",
    "validation_authority_used", "policy_delta", "baseline_equivalent",
    "external_owner_authority", "authoritative_contract",
    "original_witness_retained", "held_out_passed", "discovery_reachable",
    "migration_authority", "property_equivalent_or_stronger", "expected",
}
POLICY_DELTAS = {
    "unchanged", "strengthening", "repair", "new-policy", "weakening",
    "migration", "coupled",
}
POLICY_EVIDENCE_KEYS = {
    "candidate_identity", "parent_identity", "owner_delta", "authority",
    "witness", "evidence_population", "behaviour", "discovery",
    "residual_state", "rollback_boundary",
}
OWNER_DELTA_KEYS = {"changed_owners", "acceptance_owners", "operation"}
AUTHORITY_KEYS = {
    "source_identity", "owner_locator", "contract_locator",
    "effective_boundary",
}
IDENTITY_RELATIONSHIP_KEYS = {"candidate_parent", "authority_parent"}
POPULATION_KEYS = {
    "source_identity", "total_count", "examined_count",
}
BEHAVIOUR_KEYS = {"positive", "negative", "boundary", "adjacent"}
EXPECTED_BEHAVIOUR = {
    "positive": "PASS", "negative": "FAIL", "boundary": "FAIL",
    "adjacent": "FAIL",
}
PROMPT_KEYS = {
    "before_prompt", "after_prompt", "expected_answer_before",
    "expected_answer_after", "forbidden_mission_phrases", "distractors",
    "held_out_prompts",
}
SURFACES = {
    "unrelated-test", "product", "assertion", "golden", "threshold",
    "representation", "tolerance", "population", "denominator", "bypass",
    "skip", "mock", "prompt", "proxy-retention",
}
EVENTS = {"candidate-fail", "product-change", "contract-change", "evaluator-change"}
VERDICTS = {"NOT_RUN", "PASS", "FAIL"}


def git_result(repository, *arguments):
    return subprocess.run(
        ["git", "-C", repository, *arguments], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def require_git_object(repository, identity, owner, object_type=None):
    suffix = "^{commit}" if object_type == "commit" else ""
    resolved = git_result(repository, "cat-file", "-e", identity + suffix)
    if resolved.returncode != 0:
        raise ValueError(f"{owner}: identity does not resolve in evaluation repository")
    if object_type == "blob":
        actual = git_result(repository, "cat-file", "-t", identity)
        if actual.returncode != 0 or actual.stdout.strip() != "blob":
            raise ValueError(f"{owner}: population source is not a blob")


def validate_repository_evidence(evidence, metadata, case_id, repository):
    if not repository:
        raise ValueError(f"{case_id}: evaluation repository required")
    repository_probe = git_result(repository, "rev-parse", "--absolute-git-dir")
    if repository_probe.returncode != 0:
        raise ValueError(f"{case_id}: evaluation repository invalid")

    candidate = evidence["candidate_identity"]
    parent = evidence["parent_identity"]
    authority = evidence["authority"]
    witness = evidence["witness"]
    relationship = require_exact(
        metadata["identity_relationship"], IDENTITY_RELATIONSHIP_KEYS,
        f"{case_id} identity relationship")
    if relationship != {
            "candidate_parent": "direct-parent",
            "authority_parent": "tree-object-at-owner-locator"}:
        raise ValueError(f"{case_id}: identity relationship unsupported")
    if candidate == parent:
        raise ValueError(f"{case_id}: candidate equals parent")
    if authority is None:
        raise ValueError(f"{case_id}: repository evidence authority missing")
    authority_identity = authority["source_identity"]
    if authority_identity in {candidate, parent}:
        raise ValueError(f"{case_id}: authority is candidate or parent substitution")
    if witness is None:
        raise ValueError(f"{case_id}: retained witness missing")

    for label, identity in (("candidate", candidate), ("parent", parent)):
        require_git_object(repository, identity, f"{case_id} {label}", "commit")
    require_git_object(repository, authority_identity, f"{case_id} authority")

    parents = git_result(repository, "rev-list", "--parents", "-n", "1", candidate)
    if parents.returncode != 0 or parent not in parents.stdout.split()[1:]:
        raise ValueError(f"{case_id}: declared candidate parent relationship invalid")
    independent = git_result(
        repository, "rev-parse",
        f"{parent}:{authority['owner_locator']}")
    if (independent.returncode != 0 or
            independent.stdout.strip() != authority_identity):
        raise ValueError(f"{case_id}: declared authority relationship invalid")

    population = require_exact(
        metadata["population"], POPULATION_KEYS,
        f"{case_id} evidence population")
    source_identity = population["source_identity"]
    if not re.fullmatch(r"[0-9a-f]{40}", source_identity):
        raise ValueError(f"{case_id}: population source identity invalid")
    require_git_object(
        repository, source_identity, f"{case_id} population source", "blob")
    source = git_result(repository, "cat-file", "-p", source_identity)
    if source.returncode != 0:
        raise ValueError(f"{case_id}: population source unreadable")
    enumerated = [line.strip() for line in source.stdout.splitlines() if line.strip()]
    if (not enumerated or len(enumerated) != len(set(enumerated)) or
            any(not re.fullmatch(r"[0-9a-f]{40}", value)
                for value in enumerated)):
        raise ValueError(f"{case_id}: population source enumeration invalid")
    identities = evidence["evidence_population"]
    if (type(population["total_count"]) is not int or
            type(population["examined_count"]) is not int or
            type(identities) is not list or identities != enumerated or
            population["total_count"] != len(enumerated) or
            population["examined_count"] != len(enumerated)):
        raise ValueError(f"{case_id}: population coverage incomplete")
    for identity in identities:
        require_git_object(repository, identity, f"{case_id} population member")
    if witness["identity"] not in identities:
        raise ValueError(f"{case_id}: retained witness absent from population")


def result(activation, classification, route, disposition):
    return {
        "activation": activation,
        "classification": classification,
        "route": route,
        "disposition": disposition,
    }


def validate_mutation_case(case, index):
    if type(case) is not dict:
        raise ValueError(f"mutation case {index} must be an object")
    owner = case.get("id", f"mutation case {index}")
    required_keys = (
        MUTATION_KEYS | {"prompt_contract"}
        if case.get("surface") == "prompt" else MUTATION_KEYS)
    require_exact(case, required_keys, owner)
    if type(case["id"]) is not str or not case["id"]:
        raise ValueError(f"mutation case {index} identity invalid")
    if case["surface"] not in SURFACES:
        raise ValueError(f"{case['id']}: unsupported evaluator surface")
    events = case["event_order"]
    if (type(events) is not list or any(type(item) is not str for item in events)
            or len(events) != len(set(events)) or not set(events) <= EVENTS):
        raise ValueError(f"{case['id']}: event order invalid")
    for key in ("same_claim", "product_changed", "witness_retained",
                "property_preserved", "record_complete"):
        if type(case[key]) is not bool:
            raise ValueError(f"{case['id']}: {key} must be boolean")
    failed_at = events.index("candidate-fail") if "candidate-fail" in events else -1
    product_changed_after_failure = (
        "product-change" in events and
        events.index("product-change") > failed_at >= 0)
    if case["product_changed"] != product_changed_after_failure:
        raise ValueError(f"{case['id']}: product change state inconsistent")
    if case["old_verdict"] not in VERDICTS or case["new_verdict"] not in VERDICTS:
        raise ValueError(f"{case['id']}: verdict invalid")
    if (type(case["property_evidence"]) is not list or
            any(type(item) is not str or not item.strip()
                for item in case["property_evidence"])):
        raise ValueError(f"{case['id']}: property evidence invalid")
    if type(case["original_witness"]) is not str:
        raise ValueError(f"{case['id']}: original witness invalid")
    if type(case["authoritative_instrument"]) is not str:
        raise ValueError(f"{case['id']}: authoritative instrument invalid")
    held_out = case["held_out_passed"]
    if (type(held_out) is not list or
            any(type(item) is not str for item in held_out) or
            len(held_out) != len(set(held_out)) or not set(held_out) <= HELD_OUT_SET):
        raise ValueError(f"{case['id']}: held-out controls invalid")
    matrix = case["matrix"]
    if matrix is not None:
        require_exact(matrix, MATRIX_KEYS, f"{case['id']} matrix")
        if any(value not in {"PASS", "FAIL"} for value in matrix.values()):
            raise ValueError(f"{case['id']}: matrix verdict invalid")
    population = require_exact(
        case["population"], {"before", "after", "scope_evidence"},
        f"{case['id']} population")
    if (type(population["before"]) is not int or population["before"] < 0 or
            type(population["after"]) is not int or population["after"] < 0 or
            type(population["scope_evidence"]) is not bool):
        raise ValueError(f"{case['id']}: population invalid")
    proof = require_exact(
        case["proof"], {"old", "new", "parity"}, f"{case['id']} proof")
    if (proof["old"] not in {"none", "live", "mock"} or
            proof["new"] not in {"none", "live", "mock"} or
            type(proof["parity"]) is not bool):
        raise ValueError(f"{case['id']}: proof level invalid")
    contract = case["contract_change"]
    if contract is not None:
        require_exact(contract, CONTRACT_KEYS, f"{case['id']} contract change")
        if any(type(value) is not str or not value.strip()
               for value in contract.values()):
            raise ValueError(f"{case['id']}: contract change incomplete")
    contract_changed_after_failure = (
        "contract-change" in events and
        events.index("contract-change") > failed_at >= 0)
    if (contract is not None) != contract_changed_after_failure:
        raise ValueError(f"{case['id']}: contract change state inconsistent")
    if case["surface"] == "prompt":
        prompt = require_exact(
            case["prompt_contract"], PROMPT_KEYS, f"{case['id']} prompt contract")
        for key in ("before_prompt", "after_prompt", "expected_answer_before",
                    "expected_answer_after"):
            if type(prompt[key]) is not str or not prompt[key].strip():
                raise ValueError(f"{case['id']}: {key} invalid")
        for key in ("forbidden_mission_phrases", "distractors", "held_out_prompts"):
            values = prompt[key]
            if (type(values) is not list or not values or
                    any(type(value) is not str or not value.strip()
                        for value in values) or len(values) != len(set(values))):
                raise ValueError(f"{case['id']}: {key} invalid")
    require_exact(
        case["expected"], {"activation", "classification", "route", "disposition"},
        f"{case['id']} expected result")


def classify_mutation(case, mutation_record, parity_witness):
    events = case["event_order"]
    failed_at = events.index("candidate-fail") if "candidate-fail" in events else -1
    evaluator_changed = (
        "evaluator-change" in events and
        events.index("evaluator-change") > failed_at)
    contract_changed = (
        "contract-change" in events and
        events.index("contract-change") > failed_at)
    triggered = (
        case["same_claim"] and failed_at >= 0 and
        (contract_changed or evaluator_changed))

    held_out = set(case["held_out_passed"]) == HELD_OUT_SET
    evidence = bool(case["property_evidence"])
    witness = bool(case["original_witness"].strip()) and case["witness_retained"]
    population = case["population"]
    population_sound = (
        population["before"] == population["after"] or population["scope_evidence"])
    proof = case["proof"]
    needs_parity = bool(case["authoritative_instrument"].strip()) or proof["new"] == "mock"
    parity_sound = (
        not needs_parity or
        (parity_witness is not None and
         parity_witness["primary_verdict"] == parity_witness["secondary_verdict"]))
    if needs_parity and proof["parity"] != parity_sound:
        raise ValueError(f"{case['id']}: parity flag contradicts structured witness")
    proof_sound = proof["old"] == "live" and (
        proof["new"] == "live" or (
            proof["new"] == "mock" and proof["parity"])) and (
        not case["authoritative_instrument"].strip() or
        parity_sound)
    matrix = case["matrix"]
    matrix_values = (
        matrix["old_product_old_evaluator"],
        matrix["old_product_new_evaluator"],
        matrix["new_product_old_evaluator"],
        matrix["new_product_new_evaluator"],
    ) if matrix else ()
    product_effect = ("FAIL", "FAIL", "PASS", "PASS")
    evaluator_effect = ("FAIL", "PASS", "FAIL", "PASS")
    product_isolating = matrix_values == product_effect
    evaluator_isolating = matrix_values == evaluator_effect
    matrix_discriminating = set(matrix_values) == {"PASS", "FAIL"}
    matrix_equivalent = bool(matrix) and (
        matrix["old_product_old_evaluator"] == matrix["old_product_new_evaluator"] and
        matrix["new_product_old_evaluator"] == matrix["new_product_new_evaluator"])
    independent_instrument = bool(case["authoritative_instrument"].strip())
    prompt_sound = True
    if case["surface"] == "prompt":
        prompt = case["prompt_contract"]
        scored_prompts = [
            prompt["before_prompt"], prompt["after_prompt"],
            *prompt["held_out_prompts"],
        ]
        forbidden = [
            prompt["expected_answer_before"],
            prompt["expected_answer_after"],
            *prompt["forbidden_mission_phrases"],
            *prompt["distractors"],
        ]
        answer_change_supported = (
            prompt["expected_answer_before"] == prompt["expected_answer_after"] or
            bool(case["authoritative_instrument"].strip()) or
            (contract_changed and case["contract_change"] is not None))
        def exposed(token, mission):
            characters = [re.escape(char) for char in token.casefold()
                          if char.isalnum()]
            if not characters:
                return False
            pattern = (
                r"(?<![a-z0-9])" + r"[^a-z0-9]*".join(characters) +
                r"(?![a-z0-9])")
            return re.search(pattern, mission.casefold()) is not None
        prompt_sound = (
            answer_change_supported and
            not any(exposed(token, mission)
                    for mission in scored_prompts for token in forbidden))
    supported_core = (
        evidence and witness and held_out and population_sound and proof_sound and
        case["property_preserved"] and mutation_record is not None and prompt_sound)

    if not triggered:
        product_repair = (
            failed_at >= 0 and "product-change" in events and
            events.index("product-change") > failed_at and
            case["product_changed"] and case["old_verdict"] == "FAIL" and
            case["new_verdict"] == "PASS" and evidence and witness and held_out and
            population_sound and proof_sound and case["property_preserved"])
        if product_repair:
            return result(
                "NO_R35_ACTIVATION", "PRODUCT_DEFECT", "PRODUCT_REPAIR", "PASS")
        return result(
            "NO_R35_ACTIVATION", "NOT_APPLICABLE", "ORDINARY_PATH", "PASS")

    contract = case["contract_change"]
    contract_route = (
        contract is not None and contract_changed)
    if (contract_route and not case["product_changed"] and supported_core and
            not matrix and
            case["old_verdict"] == "FAIL" and case["new_verdict"] == "PASS"):
        return result(
            "TRIGGERED", "PRODUCT_DEFECT", "CHANGED_CONTRACT",
            "PASS_NEW_CONTRACT_ONLY")

    if contract_changed:
        classification = "COUPLED_CHANGE" if case["product_changed"] else "UNRESOLVED"
        return result(
            "TRIGGERED", classification, "ISOLATE_EFFECTS", "UNRESOLVED")

    if case["product_changed"]:
        if supported_core and product_isolating:
            return result("TRIGGERED", "COUPLED_CHANGE", "ISOLATED", "PASS")
        return result(
            "TRIGGERED", "COUPLED_CHANGE", "ISOLATE_EFFECTS", "UNRESOLVED")

    if (case["surface"] == "representation" and supported_core and
            matrix_equivalent and matrix_discriminating and
            case["old_verdict"] == case["new_verdict"]):
        return result(
            "TRIGGERED", "PRODUCT_DEFECT", "REPRESENTATION_PRESERVING",
            "PASS_REFACTOR_ONLY")

    if (evaluator_changed and case["old_verdict"] == "FAIL" and
            case["new_verdict"] == "PASS"):
        if (supported_core and
                (evaluator_isolating or (independent_instrument and not matrix))):
            return result(
                "TRIGGERED", "EVALUATOR_DEFECT", "EVALUATOR_REPAIR", "PASS")
        return result("TRIGGERED", "UNRESOLVED", "PROXY_GREEN", "FAIL")

    return result(
        "TRIGGERED", "UNRESOLVED", "INDEPENDENT_ADJUDICATION", "UNRESOLVED")


def validate_policy_case(case, index):
    require_exact(case, POLICY_KEYS, f"policy case {index}")
    if type(case["id"]) is not str or not case["id"]:
        raise ValueError(f"policy case {index} identity invalid")
    for key in (
            "candidate_changed", "path_match", "semantic_owner_intersection",
            "validation_authority_used", "baseline_equivalent",
            "external_owner_authority", "authoritative_contract",
            "original_witness_retained", "discovery_reachable",
            "migration_authority", "property_equivalent_or_stronger"):
        if type(case[key]) is not bool:
            raise ValueError(f"{case['id']}: {key} must be boolean")
    if case["policy_delta"] not in POLICY_DELTAS:
        raise ValueError(f"{case['id']}: policy delta invalid")
    held_out = case["held_out_passed"]
    if (type(held_out) is not list or len(held_out) != len(set(held_out)) or
            not set(held_out) <= HELD_OUT_SET):
        raise ValueError(f"{case['id']}: held-out controls invalid")
    require_exact(
        case["expected"],
        {"activation", "classification", "route", "disposition"},
        f"{case['id']} expected result")


def classify_policy(case, evidence):
    owner_delta = evidence["owner_delta"]
    owner_intersection = (
        set(owner_delta["changed_owners"]) &
        set(owner_delta["acceptance_owners"]))
    activated = (
        evidence["candidate_identity"] != evidence["parent_identity"] and
        bool(owner_intersection))
    if not activated:
        return result(
            "NO_R35_ACTIVATION", "PRODUCT_ONLY", "ORDINARY_PATH", "PASS")

    authority = evidence["authority"]
    authority_valid = (
        authority is not None and
        authority["source_identity"] != evidence["candidate_identity"])
    witness = evidence["witness"]
    witness_retained = (
        witness is not None and
        witness["identity"] in evidence["evidence_population"])
    behaviour = evidence["behaviour"]
    baseline = behaviour["baseline"]
    candidate = behaviour["candidate"]
    baseline_sound = baseline == EXPECTED_BEHAVIOUR
    candidate_sound = candidate == EXPECTED_BEHAVIOUR
    candidate_weaker = baseline_sound and not candidate_sound
    discovery = evidence["discovery"]
    discovery_reachable = bool(discovery["candidate_route"].strip())
    migration_authorised = (
        authority_valid and
        discovery["migration_authority_identity"] == authority["source_identity"])
    operation = owner_delta["operation"]

    if candidate_weaker or operation == "weakening":
        return result(
            "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
            "CANDIDATE_CONTROLLED_POLICY_WEAKENING",
            "REJECT_SELF_AUTHENTICATED_GREEN", "FAIL")

    if operation == "move" or not discovery_reachable:
        if migration_authorised and witness_retained and candidate_sound:
            return result(
                "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
                "AUTHORISED_POLICY_CHANGE", "AUTHORITATIVE_OWNER_MIGRATION",
                "PASS")
        return result(
            "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
            "CANDIDATE_CONTROLLED_POLICY_WEAKENING", "OWNER_UNREACHABLE",
            "FAIL")

    if operation == "additive":
        if baseline_sound and candidate_sound:
            return result(
                "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
                "POLICY_STRENGTHENING", "BASELINE_RETAINED",
                "PASS_SUPPLEMENTARY_ONLY")

    if (operation == "repair" and authority_valid and witness_retained and
            candidate_sound):
        return result(
            "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
            "AUTHORISED_POLICY_CHANGE", "INDEPENDENT_PROPERTY_ADJUDICATION",
            "PASS")

    if (operation == "new" and baseline is None and authority_valid and
            witness_retained and candidate_sound):
        return result(
            "CANDIDATE_CONTROLLED_VALIDATION_POLICY",
            "NEW_POLICY_NO_BASELINE_EQUIVALENT",
            "EXTERNAL_OWNER_AND_PROPERTY_DISCRIMINATION", "PASS")

    return result(
        "CANDIDATE_CONTROLLED_VALIDATION_POLICY", "COUPLED_OR_UNRESOLVED",
        "ISOLATE_OR_ADJUDICATE", "UNRESOLVED")


def classify(case):
    kind = case.get("kind")
    if kind == "regex-predicate":
        matched = re.search(
            case["pattern"], case["input"], re.IGNORECASE | re.DOTALL)
        return "PASS" if matched else "FAIL"

    if kind == "prompt-independence":
        instruction = case["instruction"].casefold()
        leaked = any(
            phrase.casefold() in instruction
            for phrase in case["forbidden_instruction_phrases"])
        return "FIXTURE_DEFECT" if leaked else "PASS"

    if kind == "instrument-liveness":
        all_failed = (
            case["declared_member_count"] > 0 and
            case["pass_count"] == 0 and
            case["failure_count"] == case["declared_member_count"])
        missing_actuals = (
            not case["actuals"] or
            all(actual is None for actual in case["actuals"]))
        if all_failed and missing_actuals:
            return {
                "disposition": "ANDON",
                "class": "evidence-mismatch",
                "blocker": "instrument-suspect",
                "finding_count": 0,
            }
        return {
            "disposition": "FINDING",
            "finding_count": case["failure_count"],
        }

    if kind == "instrument-parity":
        witnessed = (
            bool(case["canned_input"]) and
            case["formal_verdict"] is not None and
            case["secondary_verdict"] is not None and
            case["formal_verdict"] == case["secondary_verdict"])
        return (
            "MAY_DRIVE_ANALYSIS_OR_REPAIR" if witnessed
            else "DIAGNOSTICS_ONLY")

    if kind == "stimulus-repair":
        complete = (
            case["repair_class"] == "STIMULUS" and
            bool(case["ambiguity_or_unsatisfiability"].strip()) and
            case["pre_repair_transcript_still_fails"] is True and
            case["held_out_negative_still_fails"] is True)
        return "PASS" if complete else "FAIL"

    raise ValueError(f"unsupported control kind: {kind!r}")


def classify_state_synthesis(case):
    keys = {"id", "triggered", "authoritative_discriminator",
            "decision_consumer", "required_function", "current_state",
            "evaluator_fit", "evidence_boundaries", "independent_basis",
            "recovery", "expected"}
    action_keys = {"automated_action", "false_alarm_cost",
                   "missed_detection_cost", "detection_latency",
                   "diagnosis_confidence", "reversibility", "action_authority"}
    if "automated_action" in case:
        keys |= action_keys
    require_exact(case, keys, case.get("id", "state synthesis case"))
    for key in keys - {"id", "expected"}:
        if type(case[key]) is not bool:
            raise ValueError(f"{case['id']}: {key} must be boolean")
    if not case["triggered"]:
        return "PASS" if case["authoritative_discriminator"] else "FAIL"
    required = ("decision_consumer", "required_function", "current_state",
                "evaluator_fit", "evidence_boundaries", "independent_basis",
                "recovery")
    if not all(case[key] for key in required):
        return "FAIL"
    if case.get("automated_action"):
        action_required = action_keys - {"automated_action"}
        return "PASS" if all(case[key] for key in action_required) else "FAIL"
    return "PASS"


path = Path(sys.argv[1])
repository = sys.argv[2]
fixture = json.loads(
    path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
require_exact(
    fixture,
    {"schema", "controls", "instrument_parity", "mutation_cases",
     "mutation_records", "phase_cases", "policy_cases", "policy_evidence",
     "policy_evidence_context", "state_synthesis_cases"},
    "fixture bank")
if fixture["schema"] != "implementaudit-acceptance-instrument-discipline-fixtures-v2":
    raise ValueError("fixture bank schema invalid")
if type(fixture["controls"]) is not list or not fixture["controls"]:
    raise ValueError("fixture controls must be a non-empty list")
if type(fixture["phase_cases"]) is not list or not fixture["phase_cases"]:
    raise ValueError("fixture phase_cases must be a non-empty list")
if type(fixture["mutation_cases"]) is not list or not fixture["mutation_cases"]:
    raise ValueError("fixture mutation_cases must be a non-empty list")
if type(fixture["policy_cases"]) is not list or not fixture["policy_cases"]:
    raise ValueError("fixture policy_cases must be a non-empty list")
state_synthesis_cases = fixture["state_synthesis_cases"]
if type(state_synthesis_cases) is not list or not state_synthesis_cases:
    raise ValueError("fixture state_synthesis_cases must be a non-empty list")
policy_evidence = fixture["policy_evidence"]
if type(policy_evidence) is not dict:
    raise ValueError("fixture policy_evidence must be an object")
policy_evidence_context = require_exact(
    fixture["policy_evidence_context"],
    {"default_classification", "repository_evidence"},
    "policy evidence context")
if policy_evidence_context["default_classification"] != "contract-fixture":
    raise ValueError("policy evidence default must be explicit contract-fixture")
repository_evidence = policy_evidence_context["repository_evidence"]
if type(repository_evidence) is not dict:
    raise ValueError("repository evidence context must be an object")
mutation_records = fixture["mutation_records"]
if type(mutation_records) is not dict:
    raise ValueError("fixture mutation_records must be an object")
for record_id, record in mutation_records.items():
    require_exact(record, RECORD_KEYS, f"{record_id} mutation record")
    if any(type(record[key]) is not str or not record[key].strip()
           for key in RECORD_KEYS - {"changes"}):
        raise ValueError(f"{record_id}: mutation record incomplete")
    if (type(record["changes"]) is not list or not record["changes"] or
            any(change not in EVENTS - {"candidate-fail"}
                for change in record["changes"]) or
            len(record["changes"]) != len(set(record["changes"]))):
        raise ValueError(f"{record_id}: mutation record changes invalid")
instrument_parity = fixture["instrument_parity"]
if type(instrument_parity) is not dict:
    raise ValueError("fixture instrument_parity must be an object")
for parity_id, witness in instrument_parity.items():
    require_exact(witness, PARITY_KEYS, f"{parity_id} parity witness")
    if any(type(value) is not str or not value.strip() for value in witness.values()):
        raise ValueError(f"{parity_id}: parity witness incomplete")

ids = []
failures = []
for index, case in enumerate(fixture["controls"]):
    if type(case) is not dict or type(case.get("id")) is not str:
        raise ValueError(f"control {index} identity invalid")
    ids.append(case["id"])
    actual = classify(case)
    if actual != case.get("expected"):
        failures.append(
            f"{case['id']}: expected {case.get('expected')!r}, got {actual!r}")

if len(ids) != len(set(ids)):
    raise ValueError("control identities duplicate")

required_ids = {
    "F1-paraphrase-must-pass",
    "F2-negation-must-fail",
    "F2n-genuine-emission",
    "F3-leaked-answer",
    "F3n-post-fix-B1",
    "F4-broken-instrument",
    "F4m-missing-actuals",
    "F4n-genuine-mismatch",
    "F5-instrument-parity",
    "F5n-parity-witness-present",
    "F6-stimulus-repair",
    "F6n-stimulus-repair-complete",
}
if set(ids) != required_ids:
    raise ValueError("fixture control identity set invalid")

required_fixtures = {
    "F1-paraphrase-must-pass": "E5c-paraphrase-control",
    "F2-negation-must-fail": "B2n-polarity-control",
    "F2n-genuine-emission": "genuine-emission",
    "F3-leaked-answer": "B1L-leak-check",
    "F3n-post-fix-B1": "post-fix-B1",
    "F4-broken-instrument": "broken-instrument",
    "F4m-missing-actuals": "broken-instrument-missing-actuals",
    "F4n-genuine-mismatch": "genuine-mismatch",
    "F5-instrument-parity": "instrument-parity",
    "F5n-parity-witness-present": "parity-witness-present",
    "F6-stimulus-repair": "stimulus-repair",
    "F6n-stimulus-repair-complete": "stimulus-repair-complete",
}
actual_fixtures = {case["id"]: case.get("fixture")
                   for case in fixture["controls"]}
if actual_fixtures != required_fixtures:
    raise ValueError("fixture family mapping invalid")

mutation_ids = []
for index, case in enumerate(fixture["mutation_cases"]):
    validate_mutation_case(case, index)
    mutation_ids.append(case["id"])
    record = mutation_records.get(case["id"])
    events = case["event_order"]
    failed_at = events.index("candidate-fail") if "candidate-fail" in events else -1
    expected_changes = {
        event for event in EVENTS - {"candidate-fail"}
        if event in events and events.index(event) > failed_at >= 0
    }
    if record is not None and set(record["changes"]) != expected_changes:
        raise ValueError(f"{case['id']}: mutation record change inventory mismatch")
    if case["record_complete"] != (record is not None):
        raise ValueError(f"{case['id']}: record completeness is not structural")
    parity_witness = instrument_parity.get(case["id"])
    needs_parity = bool(case["authoritative_instrument"].strip()) or case["proof"]["new"] == "mock"
    if needs_parity != (parity_witness is not None):
        raise ValueError(f"{case['id']}: independent instrument parity missing or phantom")
    actual = classify_mutation(case, record, parity_witness)
    if actual != case["expected"]:
        failures.append(
            f"{case['id']}: expected {case['expected']!r}, got {actual!r}")

if len(mutation_ids) != len(set(mutation_ids)):
    raise ValueError("mutation control identities duplicate")
if set(mutation_records) - set(mutation_ids):
    raise ValueError("mutation record identity has no case")
if set(instrument_parity) - set(mutation_ids):
    raise ValueError("parity witness identity has no case")

policy_ids = []
for index, case in enumerate(fixture["policy_cases"]):
    validate_policy_case(case, index)
    policy_ids.append(case["id"])
    evidence = policy_evidence.get(case["id"])
    if evidence is None:
        raise ValueError(f"{case['id']}: policy evidence missing")
    require_exact(evidence, POLICY_EVIDENCE_KEYS, f"{case['id']} policy evidence")
    for key in ("candidate_identity", "parent_identity"):
        if not re.fullmatch(r"[0-9a-f]{40}", evidence[key]):
            raise ValueError(f"{case['id']}: {key} invalid")
    require_exact(evidence["owner_delta"], OWNER_DELTA_KEYS, f"{case['id']} owner delta")
    for key in ("changed_owners", "acceptance_owners"):
        values = evidence["owner_delta"][key]
        if (type(values) is not list or
                any(type(value) is not str or not value.strip() for value in values) or
                len(values) != len(set(values))):
            raise ValueError(f"{case['id']}: owner delta {key} invalid")
    if evidence["owner_delta"]["operation"] not in {
            "none", "additive", "repair", "new", "weakening", "move", "coupled"}:
        raise ValueError(f"{case['id']}: owner delta operation invalid")
    authority = evidence["authority"]
    if authority is not None:
        require_exact(authority, AUTHORITY_KEYS, f"{case['id']} authority")
        if (not re.fullmatch(r"[0-9a-f]{40}", authority["source_identity"]) or
                any(not authority[key].strip() for key in AUTHORITY_KEYS - {"source_identity"})):
            raise ValueError(f"{case['id']}: authority incomplete")
    witness = evidence["witness"]
    if witness is not None:
        require_exact(witness, {"identity"}, f"{case['id']} witness")
        if not re.fullmatch(r"[0-9a-f]{40}", witness["identity"]):
            raise ValueError(f"{case['id']}: witness identity invalid")
    population = evidence["evidence_population"]
    if (type(population) is not list or
            any(not re.fullmatch(r"[0-9a-f]{40}", value)
                for value in population)):
        raise ValueError(f"{case['id']}: evidence population invalid")
    if case["id"] in repository_evidence:
        metadata = require_exact(
            repository_evidence[case["id"]],
            {"classification", "identity_relationship", "population"},
            f"{case['id']} repository evidence context")
        if metadata["classification"] != "repository-evidence":
            raise ValueError(f"{case['id']}: repository classification invalid")
        validate_repository_evidence(
            evidence, metadata, case["id"], repository)
    behaviour = require_exact(
        evidence["behaviour"], {"baseline", "candidate"},
        f"{case['id']} policy behaviour")
    for owner in ("baseline", "candidate"):
        values = behaviour[owner]
        if values is None and owner == "baseline":
            continue
        require_exact(values, BEHAVIOUR_KEYS, f"{case['id']} {owner} behaviour")
        if any(value not in {"PASS", "FAIL"} for value in values.values()):
            raise ValueError(f"{case['id']}: {owner} behaviour invalid")
    discovery = require_exact(
        evidence["discovery"],
        {"baseline_route", "candidate_route", "migration_authority_identity"},
        f"{case['id']} discovery")
    if any(type(value) is not str for value in discovery.values()):
        raise ValueError(f"{case['id']}: discovery invalid")
    if any(type(evidence[key]) is not str or not evidence[key].strip()
           for key in ("residual_state", "rollback_boundary")):
        raise ValueError(f"{case['id']}: residual or rollback missing")
    actual = classify_policy(case, evidence)
    if actual != case["expected"]:
        failures.append(
            f"{case['id']}: expected {case['expected']!r}, got {actual!r}")

required_policy_ids = {
    "R35-CP1-deleted-assertion-registry",
    "R35-CP2-candidate-skip-guidance",
    "R35-CP3-product-only-cheap-path",
    "R35-CP4-policy-strengthening",
    "R35-CP5-legitimate-policy-repair",
    "R35-CP6-new-policy-no-baseline",
    "R35-CP7-support-file-path-only",
    "R35-CP8-undiscoverable-owner",
    "R35-CP8-authoritative-migration",
    "R35-CP-coupled-unresolved",
}
if len(policy_ids) != len(set(policy_ids)) or set(policy_ids) != required_policy_ids:
    raise ValueError("policy control identity set invalid")
if set(policy_evidence) != required_policy_ids:
    raise ValueError("policy evidence identity set invalid")
if set(repository_evidence) - required_policy_ids:
    raise ValueError("repository evidence context identity has no policy case")

required_mutation_ids = {
    "R35-unrelated-test-no-trigger",
    "R35-pre-candidate-red-first-no-trigger",
    "R35-legitimate-product-repair",
    "R35-legitimate-evaluator-repair",
    "R35-legitimate-prompt-repair",
    "R35-legitimate-expected-answer-correction",
    "R35-authorised-contract-recalibration",
    "R35-authorised-contract-only-recalibration",
    "R35-representation-preserving-refactor",
    "R35-coupled-change-unisolated",
    "R35-coupled-change-isolated",
    "R35-product-contract-coupled-unisolated",
    "R35-product-contract-evaluator-unisolated",
    "R35-unresolved-ambiguous",
    "R35-assertion-weakening",
    "R35-golden-regeneration",
    "R35-tolerance-widening",
    "R35-population-removal",
    "R35-denominator-manipulation",
    "R35-bypass-flag",
    "R35-skip-list",
    "R35-mock-promotion",
    "R35-prompt-easing",
    "R35-expected-answer-easing",
    "R35-original-witness-discarded",
    "R35-incomplete-trigger-record",
    "R35-proxy-retained-property-lost",
    "R35-completed-form-failing-held-out",
}
if set(mutation_ids) != required_mutation_ids:
    raise ValueError("mutation control identity set invalid")

state_ids = []
for case in state_synthesis_cases:
    state_ids.append(case.get("id"))
    actual = classify_state_synthesis(case)
    if actual != case["expected"]:
        failures.append(f"{case['id']}: expected {case['expected']!r}, got {actual!r}")
required_state_ids = {
    "S3E-W01-automated-action-complete-risk-envelope",
    "S3E-W01-automated-action-incomplete-risk-envelope",
    "S3E-W01-complete-triggered-state",
    "S3E-W01-cheap-authoritative-discriminator",
    "S3E-W01-health-proxy-not-required-function",
    "S3E-W01-correlated-review-not-independent",
    "S3E-W01-incomplete-proof-boundary",
}
if len(state_ids) != len(set(state_ids)) or set(state_ids) != required_state_ids:
    raise ValueError("state-synthesis control identity set invalid")

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write(
    "check-acceptance-instrument-discipline: ok "
    f"({len(ids)} instrument + {len(mutation_ids)} mutation + "
    f"{len(policy_ids)} policy + {len(state_ids)} state-synthesis controls)\n")
PY
