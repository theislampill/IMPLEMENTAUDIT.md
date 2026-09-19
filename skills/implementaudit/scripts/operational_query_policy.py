#!/usr/bin/env python3
"""Read-only snapshot projections; no collection, transport, history IO or publication.

The existing evidence owner supplies immutable vocabulary and canonical-value /
error contracts. Neither these callbacks nor this module grant mutation authority.
"""
from __future__ import annotations
import json
from collections import Counter

class SnapshotQueryPolicy:
    def __init__(self, *, families, states, snapshot_schema, status_schema,
                 result_schema, why_schema, canonical_json, error):
        self._families = tuple(families)
        self._states = tuple(states)
        self._snapshot_schema = snapshot_schema
        self._status_schema = status_schema
        self._result_schema = result_schema
        self._why_schema = why_schema
        self._canonical_json = canonical_json
        self._error = error


    def _snapshot_query_records_v1(self, snapshot: object) -> list[dict]:
        """Return record-shaped snapshot members with stable logical paths."""
        if type(snapshot) is not dict or snapshot.get("schema_version") != (
                self._snapshot_schema):
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$snapshot",
                   "query input is not an R0038 snapshot payload")
        try:
            observed_families = tuple(snapshot.get("families", ()))
        except TypeError:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.families",
                        "snapshot does not retain the six frozen families")
        if observed_families != self._families:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.families",
                   "snapshot does not retain the six frozen families")
        collections = snapshot.get("collections")
        if type(collections) is not dict:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                   "snapshot collections must be an object")
        records = []
        identities = set()

        def visit(value):
            if type(value) is dict:
                currentness = value.get("currentness")
                if (type(value.get("id")) is str and value.get("family") in self._families and
                        type(currentness) is dict and
                        currentness.get("state") in self._states and
                        type(currentness.get("invalidators")) is list):
                    identity = value["id"]
                    if identity in identities:
                        self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections",
                               f"duplicate record identity: {identity}")
                    identities.add(identity)
                    records.append({
                        "path": f"record:{identity}",
                        "record": json.loads(self._canonical_json(value).decode("utf-8")),
                    })
                    return
                for key in sorted(value):
                    visit(value[key])
            elif type(value) is list:
                for row in value:
                    visit(row)

        visit(collections)
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
        return {
            "schema": self._status_schema,
            "snapshot_id": snapshot.get("snapshot_id"),
            "aggregate": snapshot.get("aggregate"),
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
        return {
            "schema": self._result_schema,
            "snapshot_id": snapshot.get("snapshot_id"),
            "family": family,
            "current_only": current_only,
            "rows": rows,
            "omitted_state_census": dict(sorted(omitted.items())),
            "missing_or_omitted_state": sorted(
                json.loads(self._canonical_json(
                    snapshot.get("missing_or_omitted_state", [])).decode("utf-8")),
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
            outgoing.setdefault(relation["source_entity_id"], []).append(relation)
        for rows in outgoing.values():
            rows.sort(key=lambda row: (
                row["target_entity_id"], row["relation_type"], row["id"]))
        order = []
        retained_relations = []
        active = set()
        complete = set()

        def visit(identity):
            if identity in active:
                self._error("OE_WHY_CYCLE", "$.relations",
                       "why lineage contains a reachable cycle")
            if identity in complete:
                return
            active.add(identity)
            record = by_id.get(identity)
            if record is not None:
                order.append(record)
            for relation in outgoing.get(identity, []):
                target = relation["target_entity_id"]
                if target not in by_id:
                    self._error("OE_QUERY_SNAPSHOT_INVALID", "$.relations",
                           "why relation endpoint is absent")
                retained_relations.append(relation)
                visit(target)
            active.remove(identity)
            complete.add(identity)

        visit(record_id)
        contrary = sorted({
            item for row in order
            for item in row.get("contrary_evidence", [])
            if type(item) is str and item})
        return {
            "schema": self._why_schema, "record_id": record_id,
            "status": "FOUND", "chain": order,
            "relations": retained_relations, "contrary_evidence": contrary,
            "authority_ceiling": "READ_ONLY_OBSERVATION", "establishes": []}
