#!/usr/bin/env python3
"""Read-only supplied-value checks for audit-implement's exact v2 contract."""

import argparse
import datetime
import hashlib
import json
import sys
import os
import re
import stat


VERSION = "implementaudit.evidential-support.v2"
RELEASE = "REALISED_IMPLEMENTATION_OR_RELEASE"
NONRELEASE = "NON_RELEASE_PROPOSITION"
STATES = ("SUPPORTED", "CONDITIONAL", "UNRESOLVED", "NOT_SUPPORTED")
LEGACY = {"established": "SUPPORTED", "contradicted": "NOT_SUPPORTED",
          "insufficient": "UNRESOLVED", "qualification gap": "CONDITIONAL",
          "unresolved": "UNRESOLVED", "boundary not supportable": "NOT_SUPPORTED"}
REFUSALS = ("stale", "identity mismatch")
MAX_BYTES = 131072
PROOF_LIMIT = ("Validates supplied values only; does not authenticate host currentness, "
               "authority, evidence, semantic sufficiency, or native admission.")


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def keys(value, expected, label):
    require(type(value) is dict, label + " must be an object")
    require(set(value) == set(expected.split()), label + " has missing or unknown keys")


def string(value, label):
    require(type(value) is str and bool(value.strip()) and len(value) <= 4096,
            label + " must be a nonempty string of at most 4096 characters")


def choice(value, allowed, label):
    require(type(value) is str and value in allowed, label + " has an unsupported value")


def sequence(value, label, nonempty=False):
    require(type(value) is list and len(value) <= 128 and (value or not nonempty),
            label + " must be a bounded list" + (" with at least one item" if nonempty else ""))


def strings(value, label):
    sequence(value, label)
    for item in value:
        string(item, label + " item")


def sha(value, label, width=64):
    require(type(value) is str and re.fullmatch("[0-9a-f]{" + str(width) + "}", value),
            label + " must be a lowercase hexadecimal digest")


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def invalid_constant(value):
    raise Invalid("nonstandard JSON constant: " + value)


def read_json(path):
    selected = os.stat(path, follow_symlinks=False)
    require(stat.S_ISREG(selected.st_mode), "JSON input must be a regular file, not a symlink")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode), "JSON input must be a regular file")
        require((selected.st_dev, selected.st_ino) == (before.st_dev, before.st_ino),
                "JSON input changed before being read")
        require(before.st_size <= MAX_BYTES, "JSON input exceeds 131072 bytes")
        raw = stream.read(MAX_BYTES + 1)
        after = os.fstat(stream.fileno())
    require(len(raw) <= MAX_BYTES, "JSON input exceeds 131072 bytes")
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    require(all(getattr(before, field) == getattr(after, field) for field in fields),
            "JSON input changed while being read")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=invalid_constant)


def envelope(value):
    require(type(value) is dict, "envelope must be an object")
    branch = value.get("subject_class")
    choice(branch, (RELEASE, NONRELEASE), "subject_class")
    expected = ("contract_version child routing_owner entry subject_class semantic_need subject package "
                "evidence_set claims assumptions limitations defeaters unresolved_obligations mechanical "
                "currentness release_currentness maintainer_scope")
    keys(value, expected + (" candidate" if branch == RELEASE else ""), "envelope")
    for key, required in (("contract_version", VERSION), ("child", "audit-implement"),
                          ("routing_owner", "/implementaudit"), ("entry", "GOVERNOR")):
        choice(value[key], (required,), key)
    choice(value["semantic_need"], ("REQUIRED", "MECHANICALLY_SETTLED", "ORDINARY_REVERSIBLE"), "semantic_need")
    keys(value["subject"], "identity configuration proposition boundary consumer consequence decision_time", "subject")
    for key, item in value["subject"].items():
        string(item, "subject." + key)
    moment = datetime.datetime.fromisoformat(value["subject"]["decision_time"].replace("Z", "+00:00"))
    require(moment.tzinfo is not None, "decision_time must include a timezone")
    keys(value["package"], "identity sha256", "package")
    string(value["package"]["identity"], "package.identity")
    sha(value["package"]["sha256"], "package.sha256")
    mechanical = {name: "VERIFIED" for name in
                  ("identity", "hashes", "parity", "package", "reachability", "version", "authority", "custody")}
    mechanical.update(writer_conflict="CLEAR", required_tests="SATISFIED", known_invalidators="CLEAR")
    keys(value["mechanical"], " ".join(mechanical), "mechanical")
    for key, required in mechanical.items():
        choice(value["mechanical"][key], (required,), "mechanical." + key)
    keys(value["currentness"], "subject configuration evidence_set consumer decision_time", "currentness")
    for key, item in value["currentness"].items():
        choice(item, ("VERIFIED",), "currentness." + key)
    choice(value["release_currentness"], ("VERIFIED" if branch == RELEASE else "NOT_APPLICABLE",), "release_currentness")
    choice(value["maintainer_scope"], ("VERIFIED",), "maintainer_scope")
    if branch == RELEASE:
        keys(value["candidate"], "source commit tree artifact_sha256 package_sha256 install host", "candidate")
        for key, item in value["candidate"].items():
            if key in ("commit", "tree"):
                sha(item, "candidate." + key, 40)
            elif key.endswith("sha256"):
                sha(item, "candidate." + key)
            else:
                string(item, "candidate." + key)
    for key in ("assumptions", "limitations", "defeaters", "unresolved_obligations"):
        strings(value[key], key)
    evidence = value["evidence_set"]
    keys(evidence, "identity sha256 manifest", "evidence_set")
    string(evidence["identity"], "evidence_set.identity")
    sha(evidence["sha256"], "evidence_set.sha256")
    sequence(evidence["manifest"], "evidence_set.manifest")
    evidence_ids = set()
    for item in evidence["manifest"]:
        keys(item, "evidence_id sha256 scope common_source independence", "manifest item")
        for key in ("evidence_id", "scope", "common_source", "independence"):
            string(item[key], "manifest." + key)
        sha(item["sha256"], "manifest.sha256")
        require(item["evidence_id"] not in evidence_ids, "duplicate evidence_id")
        evidence_ids.add(item["evidence_id"])
    require(evidence["sha256"] == digest(evidence["manifest"]), "evidence manifest checksum mismatch")
    sequence(value["claims"], "claims", nonempty=True)
    claim_ids = set()
    for claim in value["claims"]:
        keys(claim, "claim_id subject_class proposition boundary evidence_ids", "envelope claim")
        choice(claim["subject_class"], (branch,), "claim.subject_class (mixed subjects refused)")
        for key in ("claim_id", "proposition", "boundary"):
            string(claim[key], "claim." + key)
        require(claim["claim_id"] not in claim_ids, "duplicate claim_id")
        claim_ids.add(claim["claim_id"])
        strings(claim["evidence_ids"], "claim.evidence_ids")
        require(len(set(claim["evidence_ids"])) == len(claim["evidence_ids"]), "duplicate evidence reference")
        require(set(claim["evidence_ids"]) <= evidence_ids, "unknown evidence reference")


def result(value, packet, packet_digest):
    require(type(value) is dict, "result must be an object")
    release = packet["subject_class"] == RELEASE
    legacy = value.get("legacy_disposition") if release else None
    refusal = legacy in REFUSALS
    expected = "contract_version subject_class envelope_sha256 authority rationale limitations gaps progression_advice"
    keys(value, expected + (" legacy_disposition" if release else "") +
         ("" if refusal else " support_state claims"), "result")
    choice(value["contract_version"], (VERSION,), "result.contract_version")
    choice(value["subject_class"], (packet["subject_class"],), "result.subject_class")
    choice(value["authority"], ("NONE",), "result.authority")
    sha(value["envelope_sha256"], "result.envelope_sha256")
    require(value["envelope_sha256"] == packet_digest, "result is bound to a different envelope")
    for key in ("rationale", "progression_advice"):
        string(value[key], "result." + key)
    for key in ("limitations", "gaps"):
        strings(value[key], "result." + key)
    if release:
        choice(legacy, tuple(LEGACY) + REFUSALS, "legacy_disposition")
    if refusal:
        return legacy
    choice(value["support_state"], STATES, "support_state")
    if release:
        require(value["support_state"] == LEGACY[legacy], "legacy support mapping mismatch")
    sequence(value["claims"], "result.claims", nonempty=True)
    seen, states = set(), []
    for claim in value["claims"]:
        keys(claim, "claim_id support_state rationale limitations gaps conditions defeaters", "result claim")
        string(claim["claim_id"], "result.claim_id")
        require(claim["claim_id"] not in seen, "duplicate result claim_id")
        seen.add(claim["claim_id"])
        choice(claim["support_state"], STATES, "claim.support_state")
        states.append(claim["support_state"])
        string(claim["rationale"], "claim.rationale")
        for key in ("limitations", "gaps", "conditions", "defeaters"):
            strings(claim[key], "claim." + key)
        require(bool(claim["conditions"]) == (claim["support_state"] == "CONDITIONAL"),
                "CONDITIONAL requires named conditions; other states cannot hide conditions")
        if claim["support_state"] == "UNRESOLVED":
            require(claim["gaps"], "UNRESOLVED requires named gaps")
    require(seen == {claim["claim_id"] for claim in packet["claims"]}, "result claim identities differ from envelope")
    require(value["support_state"] == max(states, key=STATES.index), "summary overstates claim-level support")
    if legacy == "contradicted":
        require(any(claim["defeaters"] for claim in value["claims"]), "contradicted requires named defeaters")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__ + " " + PROOF_LIMIT, allow_abbrev=False)
    parser.add_argument("--envelope", required=True, help="exact governor envelope JSON; validates pre-load when used alone")
    parser.add_argument("--result", help="child return JSON; must be paired with --current-envelope")
    parser.add_argument("--current-envelope", help="fresh governor envelope JSON; must be paired with --result")
    args = parser.parse_args()
    if (args.result is None) != (args.current_envelope is None):
        parser.error("--result and --current-envelope must be paired")
    output = {"validation": "VALUE_VALIDATION", "authority": "NONE", "proof_limit": PROOF_LIMIT,
              "mode": "POST_RETURN" if args.result is not None else "PRE_LOAD"}
    code = 0
    try:
        packet = read_json(args.envelope)
        envelope(packet)
        packet_digest = digest(packet)
        if args.result is None:
            output.update(status="VALID" if packet["semantic_need"] == "REQUIRED" else "BYPASS",
                          envelope_sha256=packet_digest)
        else:
            require(packet["semantic_need"] == "REQUIRED", "mechanically settled or ordinary work must bypass child consumption")
            current = read_json(args.current_envelope)
            envelope(current)
            require(current == packet, "envelope drift: return to governor before reading semantic result")
            refusal = result(read_json(args.result), packet, packet_digest)
            output.update(status="REFUSED" if refusal else "VALID", envelope_sha256=packet_digest)
            if refusal:
                output["legacy_disposition"] = refusal
                code = 1
    except (ValueError, OSError, RecursionError) as exc:
        output.update(status="INVALID", error=str(exc))
        code = 2
    sys.stdout.write(json.dumps(output, sort_keys=True) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
