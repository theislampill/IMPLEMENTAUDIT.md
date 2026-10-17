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
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    for command in ["check", "member"]:
        cmd = sub.add_parser(command)
        cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
        cmd.add_argument("--custody-root", type=Path, required=command == "member")
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
    else:
        index = parse(args.index.read_bytes())
        result = check_index(index)
        if args.custody_root:
            corpus = Corpus(args.custody_root)
            require(build(corpus) == index, "projection differs from complete immutable source reconstruction")
            result["scope"] = "PINNED_PUBLIC_SOURCE_RECONSTRUCTION"
            result["relations"] = index["relation_reconstruction"]
            if args.command == "member":
                view = member_view(corpus, index, args.id)
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
