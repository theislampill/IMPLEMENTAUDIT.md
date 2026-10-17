#!/usr/bin/env python3
"""Read-only snapshot projections; no collection, transport, history IO or publication.

The existing evidence owner supplies immutable vocabulary and canonical-value /
error contracts. Neither these callbacks nor this module grant mutation authority.
"""
from __future__ import annotations
import json
import hashlib
from collections import Counter

class SnapshotQueryPolicy:
    def __init__(self, *, families, states, snapshot_schema, status_schema,
                 result_schema, why_schema, canonical_json, error):
        self._families = tuple(families)
        self._states = tuple(states)
        self._snapshot_schemas = (snapshot_schema,) if type(snapshot_schema) is str else tuple(snapshot_schema)
        self._status_schema = status_schema
        self._result_schema = result_schema
        self._why_schema = why_schema
        self._canonical_json = canonical_json
        self._error = error

    def project_collector(self, name, value):
        """One projection for query/diff/render; original observations stay intact.

        This method projects captured values. It never authenticates an input,
        renews its validity, infers a missing owner, or changes native state.
        """
        records = []
        def record(identity, family, kind, observation, source, state="CURRENT"):
            identifier = "r38:" + name + ":" + hashlib.sha256(
                self._canonical_json(identity)).hexdigest()
            row = {"id": identifier, "family": family, "record_type": kind,
                   "native_owner_identity": "R0038-C02" if name == "repository" else "R0038-C03",
                   "source_identity": source,
                   "evidence_layer": "repository" if name == "repository" else "controller",
                   "currentness": {"state": state, "invalidators": (
                       [] if state == "CURRENT" else ["OBSERVATION_STATE:" + state])},
                   "observation": observation, "establishes": []}
            records.append(row)
            return row
        if name == "repository":
            if (type(value) is not dict or value.get("schema") != "implementaudit-repository-collection-v1"
                    or type(value.get("facts")) is not list or type(value.get("repository")) is not dict):
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections.repository", "repository producer schema differs")
            source = {"collection_schema": value["schema"],
                      "commit": value["repository"]["commit"], "tree": value["repository"]["tree"]}
            record(["repository"], "CODE", "Repository", value["repository"], source)
            file_ids = {}
            unique_facts = {}
            for fact in value["facts"]:
                if (type(fact) is not dict or type(fact.get("kind")) is not str or
                        fact.get("state") not in self._states or type(fact.get("provenance")) is not dict):
                    self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections.repository.facts", "malformed repository observation")
                # Identical repeated import statements describe one edge. Keep
                # different observations under the same logical key as a refusal.
                identity = [fact["kind"], fact.get("path"), fact.get("source"),
                            fact.get("target"), fact.get("package_name")]
                key = self._canonical_json(identity)
                if key in unique_facts:
                    if unique_facts[key] != fact:
                        self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections.repository.facts", "ambiguous repository fact identity")
                    continue
                unique_facts[key] = fact
                kind = "File" if "path" in fact else "Relation"
                row = record(identity, "CODE", kind, fact,
                             {**source, "anchor": fact.get("path", fact.get("source")),
                              "provenance": fact["provenance"]}, fact["state"])
                if fact["kind"] == "FILE":
                    file_ids[fact["path"]] = row["id"]
            for row in records:
                fact = row["observation"]
                if (fact.get("kind") == "PYTHON_IMPORT" and
                        fact["source"] in file_ids and fact["target"] in file_ids):
                    row.update({"relation_type": "DEPENDS_ON", "confidence": "mechanical",
                                "source_entity_id": file_ids[fact["source"]],
                                "target_entity_id": file_ids[fact["target"]]})
            for capability in value.get("capabilities", []):
                state = {"SUPPORTED": "CURRENT", "NOT_APPLICABLE": "UNSUPPORTED",
                         "PARTIAL": "UNVERIFIED", "PARSER_ERROR": "PARSER_ERROR"}.get(
                             capability.get("state"), "UNSUPPORTED")
                record(["capability", capability["capability"]], "CODE", "Capability",
                       capability, source, state)
            for bucket, messages in value.get("diagnostics", {}).items():
                for message in messages:
                    record(["diagnostic", bucket, message], "CODE", "Diagnostic",
                           {"bucket": bucket, "message": message}, source,
                           "UNSUPPORTED" if bucket == "skipped" else "UNKNOWN")
        elif name == "native_current":
            if type(value) is not dict or value.get("schema") != "implementaudit-native-current-facts-v1":
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections.native_current", "native producer schema differs")
            source = {"collection_schema": value["schema"],
                      "controller": value["controller"], "claim": value["claim"],
                      "continuity": value["continuity"], "hot": value["hot"]}
            for key, kind in (("controller", "Controller"), ("claim", "CustodyClaim"),
                              ("continuity", "Receipt"), ("frontier", "WorkItem"),
                              ("route", "RouteObligation"), ("active_instructions", "Instruction"),
                              ("next_action", "NextAction")):
                record([key], "EXECUTION", kind, value[key], source)
            frontier = value["frontier"]
            for key, kind in (("writer_holds", "Writer"), ("resource_holds", "Resource")):
                # A complete empty owner-derived hold map remains an observation.
                record([key], "OWNERSHIP", kind, frontier[key], source)
        return records


    def _snapshot_query_records_v1(self, snapshot: object) -> list[dict]:
        """Return record-shaped snapshot members with stable logical paths."""
        if type(snapshot) is not dict or snapshot.get("schema_version") not in self._snapshot_schemas:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$snapshot",
                   "query input is not an R0038 snapshot payload")
        observed_families = snapshot.get("families")
        if (type(observed_families) not in (list, tuple)
                or tuple(observed_families) != self._families):
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.families",
                        "snapshot must retain the six frozen families as a sequence")
        if type(snapshot.get("missing_or_omitted_state", [])) is not list:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.missing_or_omitted_state",
                        "omitted-state census must be an array")
        collections = snapshot.get("collections")
        if type(collections) is not dict:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                   "snapshot collections must be an object")
        records = []
        identities = set()
        projected = []
        remaining = dict(collections)
        for name in ("repository", "native_current"):
            member = remaining.get(name)
            if type(member) is dict and "value" in member and member.get("state") == "CURRENT":
                if member.get("sha256") != hashlib.sha256(self._canonical_json(member["value"])).hexdigest():
                    self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections." + name, "collection digest differs")
                projected.extend(self.project_collector(name, member["value"]))
                remaining.pop(name)
        # Projections contain nested observations, so walking stops at their
        # record boundary. This also avoids treating native source fields as rows.
        containers = [remaining, projected]

        # Walk containers iteratively as well as relation lineage. Container
        # depth is not relation depth and must not consume Python call frames.
        # Active-path identity detects non-JSON cycles without rejecting a
        # shared inert container encountered on two independent paths.
        active_containers = set()
        stack = [(containers, False)]
        while stack:
            value, leaving = stack.pop()
            if type(value) not in (dict, list):
                continue
            identity = id(value)
            if leaving:
                active_containers.remove(identity)
                continue
            if identity in active_containers:
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                            "snapshot collections contain a container cycle")
            if type(value) is dict:
                currentness = value.get("currentness")
                if ("family" in value or "currentness" in value or
                        {"id", "record_type"} <= set(value)):
                    if (type(value.get("id")) is not str or not value["id"] or
                            value.get("family") not in self._families or type(currentness) is not dict or
                            currentness.get("state") not in self._states or
                            type(currentness.get("invalidators")) is not list or
                            any(type(item) is not str or not item for item in currentness["invalidators"]) or
                            (currentness["state"] == "CURRENT" and currentness["invalidators"])):
                        self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections", "partial or inconsistent record cannot be omitted")
                if (type(value.get("id")) is str and value.get("family") in self._families and
                        type(currentness) is dict and
                        currentness.get("state") in self._states and
                        type(currentness.get("invalidators")) is list):
                    record_id = value["id"]
                    if record_id in identities:
                        self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                                    f"duplicate record identity: {record_id}")
                    identities.add(record_id)
                    records.append({
                        "path": f"record:{record_id}",
                        "record": json.loads(self._canonical_json(value).decode("utf-8")),
                    })
                    continue
                if any(type(key) is not str for key in value):
                    self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                                "collection object keys must be text")
                children = [value[key] for key in sorted(value)]
            else:
                children = value
            active_containers.add(identity)
            stack.append((value, True))
            stack.extend((child, False) for child in reversed(children))

        return sorted(records, key=lambda row: (
            row["record"]["family"], row["record"]["id"],
            self._canonical_json(row["record"])))

    def evaluate_currentness(self, snapshot: dict) -> dict:
        """Report currentness without turning absence or degradation into success."""
        census = {family: Counter() for family in self._families}
        for row in self._snapshot_query_records_v1(snapshot):
            record = row["record"]
            census[record["family"]][record["currentness"]["state"]] += 1
        omitted = snapshot.get("missing_or_omitted_state", [])
        if type(omitted) is not list:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.missing_or_omitted_state",
                   "omitted-state census must be an array")
        omitted = json.loads(self._canonical_json(omitted).decode("utf-8"))
        for family in self._families:
            if not census[family]:
                omitted.append({"kind": "QUERY_FAMILY_ABSENT", "family": family,
                                "state": "UNVERIFIED", "code": "NO_RETAINED_FAMILY_RECORDS"})
        aggregate = snapshot.get("aggregate")
        if aggregate == "COMPLETE" and omitted:
            aggregate = "DEGRADED"
        return {
            "schema": self._status_schema,
            "snapshot_id": snapshot.get("snapshot_id"),
            "aggregate": aggregate,
            "families": list(self._families),
            "family_state_census": {
                family: dict(sorted(census[family].items())) for family in self._families},
            "missing_or_omitted_state": sorted(
                json.loads(self._canonical_json(omitted).decode("utf-8")),
                key=self._canonical_json),
            "authority_ceiling": "READ_ONLY_OBSERVATION",
            "establishes": [],
        }

    def query_family(self, snapshot: dict, family: str, current_only: bool = False) -> dict:
        """Return one deterministic family view and an explicit omission census."""
        if family not in self._families:
            self._error("OE_QUERY_FILTER_INVALID", "$.family", "unsupported family")
        if type(current_only) is not bool:
            self._error("OE_QUERY_FILTER_INVALID", "$.current_only", "must be boolean")
        rows = [
            row for row in self._snapshot_query_records_v1(snapshot)
            if row["record"]["family"] == family]
        omitted = Counter()
        if current_only:
            retained = []
            for row in rows:
                state = row["record"]["currentness"]["state"]
                if state == "CURRENT":
                    retained.append(row)
                else:
                    omitted[state] += 1
            rows = retained
        missing = json.loads(self._canonical_json(
            snapshot.get("missing_or_omitted_state", [])).decode("utf-8"))
        if not rows and not omitted:
            missing.append({"kind": "QUERY_FAMILY_ABSENT", "family": family,
                            "state": "UNVERIFIED", "code": "NO_RETAINED_FAMILY_RECORDS"})
        return {
            "schema": self._result_schema,
            "snapshot_id": snapshot.get("snapshot_id"),
            "family": family,
            "current_only": current_only,
            "rows": rows,
            "omitted_state_census": dict(sorted(omitted.items())),
            "missing_or_omitted_state": sorted(
                missing,
                key=self._canonical_json),
            "authority_ceiling": "READ_ONLY_OBSERVATION",
            "establishes": [],
        }

    def explain_history_why_v1(self, snapshot: dict, record_id: str) -> dict:
        """Explain retained relation lineage; never infer an absent cause."""
        if type(record_id) is not str or not record_id:
            self._error("OE_QUERY_FILTER_INVALID", "$.record_id",
                   "record identity must be non-empty text")
        records = [row["record"] for row in self._snapshot_query_records_v1(snapshot)]
        by_id = {row["id"]: row for row in records}
        if record_id not in by_id:
            return {
                "schema": self._why_schema, "record_id": record_id,
                "status": "UNKNOWN", "chain": [], "relations": [],
                "contrary_evidence": [],
                "authority_ceiling": "READ_ONLY_OBSERVATION", "establishes": []}
        outgoing = {}
        for relation in records:
            if not {"relation_type", "source_entity_id", "target_entity_id"} <= set(
                    relation):
                continue
            for field in ("relation_type", "source_entity_id", "target_entity_id"):
                if type(relation[field]) is not str or not relation[field]:
                    self._error("OE_QUERY_SNAPSHOT_INVALID", "$.relations." + field,
                                "why relation fields must be non-empty text")
            outgoing.setdefault(relation["source_entity_id"], []).append(relation)
        for rows in outgoing.values():
            rows.sort(key=lambda row: (
                row["target_entity_id"], row["relation_type"], row["id"]))
        order = []
        retained_relations = []
        code_cycle_relations = []
        active = set()
        complete = set()

        # An explicit DFS stack preserves the recursive order without making
        # valid retained lineage depend on Python's interpreter recursion limit.
        active.add(record_id)
        order.append(by_id[record_id])
        stack = [(record_id, iter(outgoing.get(record_id, [])))]
        while stack:
            identity, relations = stack[-1]
            relation = next(relations, None)
            if relation is None:
                active.remove(identity)
                complete.add(identity)
                stack.pop()
                continue
            target = relation["target_entity_id"]
            if target not in by_id:
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.relations",
                            "why relation endpoint is absent")
            retained_relations.append(relation)
            if target in active:
                # Repository imports may form cycles. Retain the observed edge
                # and stop traversal without granting work-DAG/lineage meaning.
                if (relation.get("family") == "CODE" and
                        relation.get("native_owner_identity") == "R0038-C02" and
                        relation.get("observation", {}).get("kind") == "PYTHON_IMPORT" and
                        relation["relation_type"] == "DEPENDS_ON"):
                    code_cycle_relations.append(relation["id"])
                    continue
                self._error("OE_WHY_CYCLE", "$.relations",
                            "why lineage contains a reachable cycle")
            if target in complete:
                continue
            active.add(target)
            order.append(by_id[target])
            stack.append((target, iter(outgoing.get(target, []))))

        for row in order:
            evidence = row.get("contrary_evidence", [])
            if type(evidence) is not list or any(type(item) is not str or not item for item in evidence):
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.contrary_evidence",
                            "contrary evidence must be an array of non-empty identities")
        contrary = sorted({
            item for row in order
            for item in row.get("contrary_evidence", [])
            if type(item) is str and item})
        return {
            "schema": self._why_schema, "record_id": record_id,
            "status": "FOUND", "chain": order,
            "code_cycle_relations": sorted(code_cycle_relations),
            "relations": retained_relations, "contrary_evidence": contrary,
            "authority_ceiling": "READ_ONLY_OBSERVATION", "establishes": []}
