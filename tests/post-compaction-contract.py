#!/usr/bin/env python3
"""Source-contract semantic preservation; runtime behavior has separate tests.

Reject loss of mandatory cognitive entry, contradictory authority promotion,
and lifecycle weakening in documents delivered to the governor and child.
This is not an agent compliance or native activation witness.
"""
from pathlib import Path
import argparse
import re

OWNERS = (
    "skills/implementaudit/SKILL.md",
    "skills/audit-state/SKILL.md",
    "skills/implementaudit/references/continuity.md",
    "skills/implementaudit/references/child-agents.md",
)
INVARIANTS = {
    "COMPACTION_IS_INDEPENDENT_AUDIT_STATE_TRIGGER": "YES",
    "POST_COMPACTION_AUDIT_STATE_REQUIRED": "YES",
    "AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_CANONICAL_CURRENTNESS": "YES",
    "AUDIT_STATE_EXECUTION_DOES_NOT_REQUIRE_VALID_MEASURED_EPOCH": "YES",
    "MISSING_CURRENTNESS_OR_EPOCH_MAY_LIMIT_RESULT_NOT_ROUTE": "YES",
    "AUDIT_STATE_RESULT_AUTHORITY_REMAINS_EVIDENCE_GATED": "YES",
    "NO_AUDIT_STATE_AFTER_COMPLETED_COMPACTION_RESUME": "CONFORMANCE_FAIL",
    "RETROACTIVE_CHILD_CREDIT": "NO",
}
SEAM_RULES = (
    "`status` is nonmutating",
    "UNRESOLVED_RESUME_OBSERVATION",
    "query or caller Boolean is not proof of a compaction occurrence",
    "assignments are scoped to boundary/version pairs",
    "B's JOIN cannot clear A",
    "A-dependent governor decisions remain held",
    "same-failed-scope retirement is `CONDITIONAL_UNQUALIFIED`",
    "actual same-child LOAD/USE/RETURN/result evidence and explicit governor acceptance",
    "caller `SUCCEEDED` is not a lifecycle witness",
    "deduplication of this delivery requires independent correlation to that exact proved occurrence",
    "source-descriptor identity or presence alone never correlates a delivery",
)
PRESENCE_ONLY_RULE = (
    "Where the exact proved occurrence is already retained, deduplicate it rather than adding an uncertain duplicate."
)
CONSUMER_RULES = (
    "actual same-child result and separate later governor acceptance",
    "bound physical read ranges before I/O",
    "physical row labels and embedded ordinals are distinct",
    "actual child identity is not a shared session_id",
    "opaque ACK association is not plaintext ACK semantics",
    "caller status, hashes or authored witness JSON cannot establish producer provenance",
    "actual source-profile qualification is required before pending consumption",
    "RETURN and acceptance alone leave pending",
    "only a successful validated JOIN consumes accepted observed versions",
    "unsupported evidence holds consumption, not mandatory audit-state execution",
    "production RETURN/JOIN must invoke the source-owned consumer",
    "native DISPOSE and failed-scope retirement remain separate",
)
FALSE_CONSUMER_RULES = (
    "Matching hashes alone prove actual child execution.",
    "Whole-file reading followed by filtering satisfies bounded-read custody.",
    "Physical row number is the native ordinal.",
    "Shared session_id is sufficient child identity.",
    "Matching opaque ACK bytes prove plaintext USE authorization.",
    "Caller-selected profile establishes host producer qualification.",
    "Acceptance alone consumes pending.",
    "An unwired validator is sufficient production integration.",
    "Native receipt proves the independent compaction result.",
    "Child-authored acceptance is valid governor acceptance.",
    "Unsupported evidence disables mandatory audit-state.",
)
OBSERVATION_RECORDS = {
    "O": (
        "implementaudit.compaction-obligation.v1",
        "schema, parent_identity, actual_child_identity, selected_child, observation_id, covered_boundary_versions, observation_source_cutoff, code_and_skill_pins, bounded_purpose, authority_ceiling",
        "selected_child=audit-state; authority_ceiling=NONE",
    ),
    "U": (
        "implementaudit.compaction-use-authorization.v1",
        "schema, action, parent_identity, actual_child_identity, obligation_digest, observation_id, load_observation_identity, selected_child, skill_source_pin, authority_ceiling",
        "action=AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION; selected_child=audit-state; authority_ceiling=NONE",
    ),
    "A": (
        "implementaudit.compaction-reconciliation-acceptance.v1",
        "schema, action, parent_identity, actual_child_identity, obligation_digest, observation_id, child_observation_exchange_identity, actual_result_digest, accepted_boundary_versions, observation_source_cutoff, authority_ceiling",
        "action=ACCEPT_BOUNDED_RECONCILIATION; authority_ceiling=NONE",
    ),
}
OBSERVATION_RULES = (
    "O is immutable before USE and contains no result or acceptance",
    "U is an actual public parent assistant commentary record",
    "writing U does not prove child observation",
    "full untruncated O/U host response precedes observe-child validation and substantive USE",
    "a helper cannot certify its own not-yet-produced host response",
    "actual same-child host call/result association is required",
    "R binds obligation_digest, observation_id, child_observation_exchange_identity, exact observed versions and result identity",
    "A is a distinct public parent assistant commentary record after actual R delivery",
    "accepted_boundary_versions exactly equals R's immutable observed scope",
    "new or conflicting U/A records require explicit reconciliation",
    "qualification requires a future genuine required boundary; no retroactive 14996 credit",
)
FALSE_OBSERVATION_RULES = (
    "Writing U alone proves child receipt and USE.",
    "A child echo of O/U proves actual host observation.",
    "A truncated O/U tool response qualifies full observation.",
    "Acceptance may cover a superset of R's observed scope.",
    "Synthetic typed records qualify the live producer.",
)
PROFILE_RULES = (
    "P fixes executable policy and selector identity before O",
    "Q is later immutable qualification data, not executable policy",
    "E admits only this exact episode under P and applicable Q",
    "Q/E arrival does not change assignment.code or O bytes/digest",
    "policy or selector changes still fail CHILD_OR_SOURCE_CHANGED",
    "Q may qualify from actual unconsumed C without prior E or successful JOIN",
    "C alone grants no episode admission",
    "global P/Q qualification does not authenticate arbitrary profile-shaped files",
    "owner flags, PASS labels and hashes are not source-origin authentication",
    "Q/E lookup uses deterministic owner-held keys, not request/env overrides or arbitrary paths",
    "same unchanged assignment may promote its original logical result/acceptance after exact E arrives",
    "no existing qualified host authenticator is established",
    "mandatory audit-state does not require Q or E",
    "actual acquisition qualification remains open",
)
FALSE_PROFILE_RULES = (
    "Global Q qualification authenticates every matching transcript.",
    "Arrival of Q must rewrite the profile selector.",
    "Remove selector hashing to admit the existing obligation.",
    "Q requires a successful E/JOIN first.",
    "Candidate C proves episode admission.",
    "H0 owner attribution authenticates transcript origin.",
    "Caller-selected E paths may authorize consumption.",
    "Reuse E for any same-format episode.",
    "Missing Q or E suppresses mandatory audit-state.",
    "An existing qualified host authenticator is already established.",
    "PASS_ACTUAL_PROFILE labels prove actual source origin.",
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate(documents):
    # The exact owner-specified discriminators are a normative public interface.
    # Check their scoped entry rather than accepting a title or stale quotation.
    for path, text in documents.items():
        normalized = " ".join(text.split())
        require("POST_COMPACTION_RECONCILIATION" in text, path + ": entry missing")
        require("NATIVE_AUTHORITATIVE_RECOVERY" in text, path + ": native scope missing")
        require("AUDIT_STATE_EXECUTION_ELIGIBILITY" in text and
                "AUDIT_STATE_RESULT_AUTHORITY" in text, path + ": eligibility/result conflated")
        require(not re.search(r"(?<!native )sole exception", normalized, re.I),
                path + ": universal sole-exception gate")
        for harmful in (
            r"post.compaction (?:audit.state|reconciliation) (?:is optional|may be skipped)",
            r"consider audit.state if warranted",
            r"post.compaction reconciliation requires (?:verified currentness|a valid measured epoch)",
            r"(?:dispatch|return alone) consumes? (?:the )?pending (?:audit|boundary)",
            r"audit.state execution (?:grants|establishes) canonical currentness",
        ):
            require(not re.search(harmful, normalized, re.I), path + ": contradictory rule")
    continuity = documents[OWNERS[2]]
    require(continuity.count("## Mandatory post-compaction reconciliation") == 1,
            "continuity: mandatory entry scope missing or ambiguous")
    require(continuity.count("## Native authoritative recovery:") == 1,
            "continuity: native entry scope missing or ambiguous")
    section = continuity.split("## Mandatory post-compaction reconciliation", 1)[-1].split("## Native authoritative recovery", 1)[0]
    for key, value in INVARIANTS.items():
        rows = re.findall(r"^" + key + r"=(.*)$", section, re.M)
        require(rows == [value], "continuity: missing/conflicting " + key)
    normalized_section = " ".join(section.split())
    consumer_heading = "### Actual result and governor acceptance consumer"
    require(section.count(consumer_heading) == 1,
            "continuity: actual result-consumer contract missing or ambiguous")
    consumer = " ".join(section.split(consumer_heading, 1)[1].split()).casefold()
    for rule in CONSUMER_RULES:
        require(rule.casefold() in consumer, "continuity: actual result-consumer rule lost: " + rule)
    for path, content in documents.items():
        normalized = " ".join(content.split()).casefold()
        for false_rule in FALSE_CONSUMER_RULES:
            require(false_rule.casefold() not in normalized, path + ": contradictory actual-result rule")
    for path in (OWNERS[1], OWNERS[3]):
        require("Actual result and governor acceptance consumer" in documents[path],
                path + ": result-consumer owner link lost")
    observation_heading = "#### Prospective O/U/observation/R/A chain"
    require(section.count(observation_heading) == 1,
            "continuity: prospective observation contract missing or ambiguous")
    observation = section.split(observation_heading, 1)[1]
    rows = re.findall(r"^\| (O|U|A) \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \|$", observation, re.M)
    require(len(rows) == 3 and {key: (schema, fields, literals) for key, schema, fields, literals in rows} == OBSERVATION_RECORDS,
            "continuity: prospective closed record schema/fields/literals changed")
    normalized_observation = " ".join(observation.split()).casefold()
    for rule in OBSERVATION_RULES:
        require(rule.casefold() in normalized_observation, "continuity: prospective observation rule lost: " + rule)
    for path, content in documents.items():
        normalized = " ".join(content.split()).casefold()
        for false_rule in FALSE_OBSERVATION_RULES:
            require(false_rule.casefold() not in normalized, path + ": contradictory prospective observation rule")
    profile_heading = "#### Fixed policy P, qualification Q and episode E"
    require(section.count(profile_heading) == 1,
            "continuity: fixed-policy/qualification/episode contract missing or ambiguous")
    profile = " ".join(section.split(profile_heading, 1)[1].split()).casefold()
    for rule in PROFILE_RULES:
        require(rule.casefold() in profile, "continuity: P/Q/E discriminator lost: " + rule)
    for path, content in documents.items():
        normalized = " ".join(content.split()).casefold()
        for false_rule in FALSE_PROFILE_RULES:
            require(false_rule.casefold() not in normalized, path + ": contradictory P/Q/E rule")
    for path in (OWNERS[1], OWNERS[3]):
        require("Fixed policy P, qualification Q and episode E" in " ".join(documents[path].split()),
                path + ": P/Q/E owner link lost")
    require(PRESENCE_ONLY_RULE.casefold() not in normalized_section.casefold(),
            "continuity: old proof presence cannot correlate a later delivery")
    for rule in SEAM_RULES:
        require(rule.casefold() in normalized_section.casefold(),
                "continuity: unresolved-resume/assignment rule lost: " + rule)
    for token in ("SessionStart(source=compact)", "compaction-audit-pending.py",
                  "register-source", "observe-child", "return_digest", "observation_id",
                  "compaction-audits-v1", "AUDIT_STATE_REQUIRED", "WAIT_EXISTING_AUDIT",
                  "NO_PENDING_AUDIT", "pending survives dispatch and RETURN",
                  "successful RETURN/JOIN", "actual observation scope/cutoff",
                  "independently proved completed compaction and resumption"):
        require(token in section, "continuity: missing pending discriminator " + token)
    for path in OWNERS[:2]:
        require("POST_COMPACTION_AUDIT_STATE_REQUIRED=YES" in documents[path],
                path + ": mandatory trigger not delivered")
    governor = documents[OWNERS[0]]
    children = documents[OWNERS[3]]
    for token in (
        "VISIBLE_PRE_USE_ANNOUNCEMENT_REQUIRED=YES",
        "ORDINARY_CHILD_PRE_DISPATCH_ANNOUNCEMENT_REQUIRED=YES",
        "SKILL_PRE_USE_ANNOUNCEMENT_REQUIRED=YES",
        "GOVERNED_CHILD_LIFECYCLE_TELEMETRY_REQUIRED=YES",
        "PERIODIC_TOPOLOGY_IS_SUPPLEMENTAL_NOT_SUBSTITUTE=YES",
        "SILENT_CHILD_OR_SKILL_USE=CONFORMANCE_FAIL",
    ):
        require(token in governor and token in children, "prior pre-use invariant lost: " + token)
    require(len(governor.encode("utf-8")) <= 22000, "governor bootstrap exceeds 22000 bytes")


def mutation_checks(documents):
    count = 0
    for key, value in INVARIANTS.items():
        changed = dict(documents)
        changed[OWNERS[2]] = changed[OWNERS[2]].replace(key + "=" + value, key + "=OPTIONAL")
        expect_rejected(changed, key)
        count += 1
    for path in OWNERS:
        for false_rule in (
            "Post-compaction reconciliation requires verified currentness.",
            "Post-compaction reconciliation requires a valid measured epoch.",
            "Consider audit-state if warranted.",
            "Dispatch consumes the pending boundary.",
            "Return alone consumes the pending audit.",
            "Audit-state execution establishes canonical currentness.",
        ):
            changed = dict(documents)
            changed[path] += "\n" + false_rule + "\n"
            expect_rejected(changed, path + ": " + false_rule)
            count += 1
    for token in ("observe-child", "successful RETURN/JOIN", "actual observation scope/cutoff",
                  "independently proved completed compaction and resumption",
                  "## Mandatory post-compaction reconciliation", "## Native authoritative recovery:"):
        changed = dict(documents)
        changed[OWNERS[2]] = changed[OWNERS[2]].replace(token, "REMOVED")
        expect_rejected(changed, token)
        count += 1
    for rule in SEAM_RULES:
        changed = dict(documents)
        # Match across wrapping without changing heading/flag layout. A title
        # elsewhere cannot rescue loss of the operative mandatory-section rule.
        pattern = r"\s+".join(re.escape(part) for part in rule.split())
        changed[OWNERS[2]], replaced = re.subn(pattern, "REMOVED", changed[OWNERS[2]], flags=re.I)
        require(replaced > 0, "mutation did not reach seam rule: " + rule)
        expect_rejected(changed, rule)
        count += 1
    # Restoring the rejected rule must fail even with the corrected clauses
    # still present. A token-only positive check would miss this contradiction.
    changed = dict(documents)
    heading = "## Mandatory post-compaction reconciliation"
    changed[OWNERS[2]] = changed[OWNERS[2]].replace(
        heading, heading + "\n\n" + PRESENCE_ONLY_RULE, 1)
    expect_rejected(changed, "restored presence-only delivery deduplication")
    count += 1
    for rule in CONSUMER_RULES:
        changed = dict(documents)
        pattern = r"\s+".join(re.escape(part) for part in rule.split())
        changed[OWNERS[2]], replaced = re.subn(pattern, "REMOVED", changed[OWNERS[2]], flags=re.I)
        require(replaced > 0, "mutation did not reach result-consumer rule: " + rule)
        expect_rejected(changed, rule)
        count += 1
    for false_rule in FALSE_CONSUMER_RULES:
        changed = dict(documents)
        changed[OWNERS[2]] += "\n" + false_rule + "\n"
        expect_rejected(changed, false_rule)
        count += 1
    for path in (OWNERS[1], OWNERS[3]):
        changed = dict(documents)
        changed[path] = changed[path].replace("Actual result and governor acceptance consumer", "REMOVED")
        expect_rejected(changed, path + ": missing result-consumer owner link")
        count += 1
    for rule in OBSERVATION_RULES:
        changed = dict(documents)
        pattern = r"\s+".join(re.escape(part) for part in rule.split())
        changed[OWNERS[2]], replaced = re.subn(pattern, "REMOVED", changed[OWNERS[2]], flags=re.I)
        require(replaced > 0, "mutation did not reach prospective rule: " + rule)
        expect_rejected(changed, rule)
        count += 1
    for false_rule in FALSE_OBSERVATION_RULES:
        changed = dict(documents)
        changed[OWNERS[2]] += "\n" + false_rule + "\n"
        expect_rejected(changed, false_rule)
        count += 1
    for label, record in OBSERVATION_RECORDS.items():
        original_row = "| " + label + " | " + " | ".join("`" + value + "`" for value in record) + " |"
        for column in range(3):
            weakened = list(record)
            weakened[column] = "CALLER_SELECTED"
            changed = dict(documents)
            replacement = "| " + label + " | " + " | ".join("`" + value + "`" for value in weakened) + " |"
            require(changed[OWNERS[2]].count(original_row) == 1, "record mutation target missing")
            changed[OWNERS[2]] = changed[OWNERS[2]].replace(original_row, replacement, 1)
            expect_rejected(changed, label + " changed record column " + str(column))
            count += 1
    for rule in PROFILE_RULES:
        changed = dict(documents)
        pattern = r"\s+".join(re.escape(part) for part in rule.split())
        changed[OWNERS[2]], replaced = re.subn(pattern, "REMOVED", changed[OWNERS[2]], flags=re.I)
        require(replaced > 0, "mutation did not reach P/Q/E rule: " + rule)
        expect_rejected(changed, rule)
        count += 1
    for false_rule in FALSE_PROFILE_RULES:
        changed = dict(documents)
        changed[OWNERS[2]] += "\n" + false_rule + "\n"
        expect_rejected(changed, false_rule)
        count += 1
    for path in (OWNERS[1], OWNERS[3]):
        changed = dict(documents)
        pattern = r"\s+".join(re.escape(part) for part in "Fixed policy P, qualification Q and episode E".split())
        changed[path] = re.sub(pattern, "REMOVED", changed[path])
        expect_rejected(changed, path + ": P/Q/E owner link removed")
        count += 1
    return count


def expect_rejected(documents, label):
    try:
        validate(documents)
    except ValueError:
        return
    raise AssertionError("semantic mutation accepted: " + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    documents = {path: (args.root / path).read_text(encoding="utf-8") for path in OWNERS}
    try:
        validate(documents)
        count = mutation_checks(documents) if args.mutations else 0
    except (ValueError, AssertionError) as error:
        parser.exit(1, "post-compaction-contract: " + str(error) + "\n")
    print(f"post-compaction-contract: source contracts pass; {count} negative mutations; no runtime qualification")


if __name__ == "__main__":
    main()
