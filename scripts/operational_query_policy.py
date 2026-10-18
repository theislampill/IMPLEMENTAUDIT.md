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
                 result_schema, why_schema, canonical_json, error, observation_liveness=None):
        self._families = tuple(families)
        self._states = tuple(states)
        self._snapshot_schemas = (snapshot_schema,) if type(snapshot_schema) is str else tuple(snapshot_schema)
        self._status_schema = status_schema
        self._result_schema = result_schema
        self._why_schema = why_schema
        self._canonical_json = canonical_json
        self._error = error
        self._observation_liveness = observation_liveness

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
            if type(value) is not dict or value.get("schema") not in {
                    "implementaudit-native-current-facts-v1", "implementaudit-native-current-facts-v2"}:
                self._error("OE_QUERY_SNAPSHOT_INVALID", "$.collections.native_current", "native producer schema differs")
            source = {"collection_schema": value["schema"],
                      "controller": value["controller"], "claim": value["claim"],
                      "continuity": value["continuity"], "hot": value["hot"]}
            base_ids = {}
            for key, kind in (("controller", "Controller"), ("claim", "CustodyClaim"),
                              ("continuity", "Receipt"), ("frontier", "WorkItem"),
                              ("route", "RouteObligation"), ("active_instructions", "Instruction"),
                              ("next_action", "NextAction")):
                if key == "frontier" and value["schema"] == "implementaudit-native-current-facts-v2":
                    kind = "DeclaredWorkGraphFrontier"
                base_ids[key] = record([key], "EXECUTION", kind, value[key], source)["id"]
            frontier = value["frontier"]
            for key, kind in (("writer_holds", "Writer"), ("resource_holds", "Resource")):
                # A complete empty owner-derived hold map remains an observation.
                record([key], "OWNERSHIP", kind, frontier[key], source)
            if value["schema"] == "implementaudit-native-current-facts-v2" and value["route_relation"] is not None:
                relation = value["route_relation"]
                graph = value["route_graph"]
                record(["route_relation"], "EXECUTION", "RouteAffectedNodes", relation,
                    {**source, "semantic_owner": "R0035", "graph_digest": graph["digest"]})
                node_ids = {}
                for node in graph["nodes"]:
                    node_ids[node["id"]] = record(["native_node", node["id"]], "EXECUTION", "GovernedWorkNode", node,
                        {**source, "semantic_owner": "R0035", "native_input_digest": node["input_digest"]})["id"]
                scope_ids = {}
                for scope in relation["uncovered_scopes"]:
                    scope_ids[scope] = record(["uncovered_route_scope", scope], "EXECUTION", "RouteCapability",
                        {"scope": scope, "code": "NATIVE_ROUTE_SCOPE_UNCOVERED"}, source, "UNVERIFIED")["id"]
                for node in graph["nodes"]:
                    edges = [("DEPENDS_ON", node_ids[target]) for target in node["requires"]]
                    edges += [("OPTIONALLY_DEPENDS_ON", node_ids[target]) for target in node["optional"]]
                    if node["parent"] is not None:
                        edges.append(("PART_OF", node_ids[node["parent"]]))
                    if node["id"] in relation["direct_nodes"]:
                        edges.append(("HAS_ROUTE_OBLIGATION", base_ids["route"]))
                    edges += [("HAS_UNCOVERED_ROUTE_SCOPE", scope_ids[scope])
                              for scope in node["route_scopes"] if scope in scope_ids]
                    for kind, target in edges:
                        edge = record(["native_relation", node["id"], kind, target], "EXECUTION", "Relation",
                            {"kind": kind, "native_node": node["id"]},
                            {**source, "semantic_owner": "R0035", "native_input_digest": node["input_digest"]})
                        edge.update(relation_type=kind, source_entity_id=node_ids[node["id"]],
                                    target_entity_id=target, confidence="owner-derived")
            else:
                record(["route_mapping_capability"], "EXECUTION", "RouteCapability",
                    {"code": "NATIVE_ROUTE_NODE_MAPPING_UNAVAILABLE"}, source, "UNVERIFIED")
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
        captured = remaining.pop("captured_owner", None)
        if captured is not None:
            projected.extend(project_captured_collection(captured)["records"])
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

        if self._observation_liveness is not None:
            records = self._observation_liveness(snapshot, records)
        return sorted(records, key=lambda row: (
            row["record"]["family"], row["record"]["id"],
            self._canonical_json(row["record"])))

    def evaluate_currentness(self, snapshot: dict) -> dict:
        """Report currentness without turning absence or degradation into success."""
        census = {family: Counter() for family in self._families}
        expired_projection = False
        for row in self._snapshot_query_records_v1(snapshot):
            record = row["record"]
            census[record["family"]][record["currentness"]["state"]] += 1
            expired_projection |= bool(record.get("liveness") and
                                       "CAPTURE_EXPIRED" in record["currentness"]["invalidators"])
        omitted = snapshot.get("missing_or_omitted_state", [])
        if type(omitted) is not list:
            self._error("OE_QUERY_SNAPSHOT_INVALID", "$.missing_or_omitted_state",
                   "omitted-state census must be an array")
        omitted = json.loads(self._canonical_json(omitted).decode("utf-8"))
        native = snapshot.get("collections", {}).get("native_current", {}).get("value")
        if type(native) is dict and native.get("route_relation") is None and not any(
                row.get("code") == "NATIVE_ROUTE_NODE_MAPPING_UNAVAILABLE" for row in omitted):
            omitted.append({"kind": "QUERY_NATIVE_CAPABILITY_UNVERIFIED", "family": "EXECUTION",
                "state": "UNVERIFIED", "code": "NATIVE_ROUTE_NODE_MAPPING_UNAVAILABLE"})
        for family in self._families:
            if not census[family]:
                omitted.append({"kind": "QUERY_FAMILY_ABSENT", "family": family,
                                "state": "UNVERIFIED", "code": "NO_RETAINED_FAMILY_RECORDS"})
        aggregate = snapshot.get("aggregate")
        if expired_projection:
            aggregate = "STALE" if aggregate not in {"INVALID", "SUPERSEDED"} else aggregate
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


# These are explicit frozen source consumers, not native acquisition adapters.
CAPTURE_KINDS = ("pending", "pending-decision", "route", "route-result", "host-binding",
                 "result-occurrence", "member-coverage", "child-visibility", "public-census")
CAPTURE_INPUT_MAX_BYTES = 8 * 1024 * 1024
CAPTURE_RECORD_MAX = 16384


def _public_require(condition, message):
    if not condition:
        raise ValueError(message)


def decode_public_census(value):
    """Bind the declared public census and complete captured comment pages.

    The normalized issue format is the retained R0038 title/body intake. Comment
    members retain the GitHub REST issue-comment object, including uninterpreted
    extra fields. Neither format supplies admission or original properties.
    """
    import re
    _public_require(type(value) is dict and set(value) == {
        "schema", "repository", "declared_members", "issues", "comments"} and
        value["schema"] == "implementaudit.public-census-input.v1", "public census envelope differs")
    repo = value["repository"]
    _public_require(type(repo) is str and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo),
                    "public repository identity differs")
    web = "https://github.com/" + repo + "/issues/"
    api = "https://api.github.com/repos/" + repo + "/issues/"
    declared, issues, comment_sets, comment_ids = {}, {}, {}, set()
    records, omissions = [], []
    def positive(number):
        return type(number) is int and number > 0
    def record(key, kind, observation, anchor):
        records.append({"key": key, "family": "RELEASE", "record_type": kind,
                        "observation": observation, "source_anchor": anchor})
    def omit(code, **detail):
        omissions.append({"family": "RELEASE", "reason": code, **detail})
    for name in ("declared_members", "issues", "comments"):
        _public_require(type(value[name]) is list, "public census population is not an array")
    for member in value["declared_members"]:
        _public_require(type(member) is dict and set(member) == {"id", "number"} and
                        positive(member["id"]) and positive(member["number"]), "declared public member differs")
        _public_require(member["number"] not in declared and member["id"] not in declared.values(),
                        "declared public member repeats")
        declared[member["number"]] = member["id"]
    for issue in value["issues"]:
        _public_require(type(issue) is dict and set(issue) == {
            "id", "number", "title", "state", "state_reason", "body", "comments", "created_at", "updated_at", "url"},
            "retained title/body issue format differs")
        number = issue["number"]
        _public_require(positive(number) and positive(issue["id"]) and declared.get(number) == issue["id"] and
                        number not in issues, "public issue is duplicate or outside declared membership")
        _public_require(type(issue["title"]) is str and re.match(r"^R[0-9A-Fa-f]{4}(?:\b|_)", issue["title"]) and
                        type(issue["body"]) is str and issue["state"] in ("open", "closed") and
                        (issue["state_reason"] is None or type(issue["state_reason"]) is str) and
                        type(issue["comments"]) is int and issue["comments"] >= 0 and
                        all(type(issue[k]) is str and issue[k] for k in ("created_at", "updated_at")) and
                        issue["url"] == web + str(number), "public issue field or source anchor differs")
        issues[number] = issue
        record(["issue", issue["id"]], "PublicContract", {
            "source": issue, "body_sha256": hashlib.sha256(issue["body"].encode("utf-8")).hexdigest(),
            "title_sha256": hashlib.sha256(issue["title"].encode("utf-8")).hexdigest(),
            "membership": "DECLARED_PUBLIC_TRACKER_ONLY"}, issue["url"])
    for group in value["comments"]:
        _public_require(type(group) is dict and set(group) == {"issue_number", "pages"} and
                        positive(group["issue_number"]) and group["issue_number"] in declared and
                        group["issue_number"] not in comment_sets and type(group["pages"]) is list,
                        "comment page group is duplicate or outside declared membership")
        number, pages = group["issue_number"], group["pages"]
        count = 0
        for index, page in enumerate(pages):
            _public_require(type(page) is list and len(page) <= 100 and
                            (index == len(pages) - 1 or len(page) == 100), "comment pagination differs")
            for comment in page:
                _public_require(type(comment) is dict and {
                    "id", "body", "created_at", "updated_at", "issue_url", "html_url", "url"} <= set(comment),
                    "REST issue-comment object is incomplete")
                identifier = comment["id"]
                _public_require(positive(identifier) and identifier not in comment_ids and type(comment["body"]) is str and
                                all(type(comment[k]) is str and comment[k] for k in ("created_at", "updated_at")) and
                                comment["issue_url"] == api + str(number) and
                                comment["html_url"] == web + str(number) + "#issuecomment-" + str(identifier) and
                                comment["url"] == api + "comments/" + str(identifier), "comment identity, body or source anchor differs")
                comment_ids.add(identifier)
                count += 1
                record(["comment", identifier], "PublicComment", {"source": comment, "issue_number": number,
                    "body_sha256": hashlib.sha256(comment["body"].encode("utf-8")).hexdigest()}, comment["html_url"])
        comment_sets[number] = count
        if not pages or len(pages[-1]) == 100:
            omit("COMMENT_PAGINATION_NOT_TERMINAL", issue_number=number, observed=count)
    for number in sorted(declared):
        if number not in issues:
            omit("DECLARED_ISSUE_NOT_CAPTURED", issue_number=number, issue_id=declared[number])
        if number not in comment_sets:
            omit("COMMENTS_NOT_CAPTURED", issue_number=number)
        elif number in issues and comment_sets[number] != issues[number]["comments"]:
            omit("COMMENT_COUNT_MISMATCH", issue_number=number, expected=issues[number]["comments"], observed=comment_sets[number])
    record(["census", repo], "PublicCensus", {
        "repository": repo, "declared": len(declared), "observed_issues": len(issues),
        "observed_comments": len(comment_ids), "state_counts": dict(sorted(Counter(x["state"] for x in issues.values()).items())),
        "authoritative_admission": None, "original_property_membership": None,
        "implemented_membership": None, "qualified_membership": None,
        "private_crosswalks": None, "pagination_scope": "DECLARED_ISSUE_COMMENT_PAGES_ONLY"}, web)
    omit("AUTHORITATIVE_ADMISSION_AND_ORIGINAL_PROPERTIES_NOT_SUPPLIED")
    return {"records": records, "omissions": omissions}


def project_captured_collection(member):
    """Project one byte-bound captured input without opening any source locator."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("captured JSON repeats a key")
            result[key] = value
        return result
    if (type(member) is not dict or set(member) != {"owner", "kind", "state", "input_text", "sha256"} or
            member["owner"] != "R0038-AS03-AS08" or member["state"] != "UNVERIFIED" or
            member["kind"] not in CAPTURE_KINDS or type(member["input_text"]) is not str):
        raise ValueError("captured member scope differs")
    raw = member["input_text"].encode("utf-8")
    if len(raw) > CAPTURE_INPUT_MAX_BYTES or hashlib.sha256(raw).hexdigest() != member["sha256"]:
        raise ValueError("captured input size or digest differs")
    value = json.loads(member["input_text"], object_pairs_hook=unique)
    kind = member["kind"]
    if kind == "public-census":
        decoded = decode_public_census(value)
    elif kind in ("pending", "pending-decision", "route", "route-result", "host-binding"):
        decoded = decode_route_capture(kind, value)
    else:
        decoded = decode_occurrence_capture(kind, value)
    if len(decoded["records"]) > CAPTURE_RECORD_MAX:
        raise ValueError("captured record population exceeds bounded review")
    def canonical(value):
        return _route_canonical(value)
    def identifier(key):
        return "r38:captured:" + kind + ":" + hashlib.sha256(canonical(key)).hexdigest()
    records = []
    for item in decoded["records"]:
        sources = (ROUTE_FORMAT_SOURCES.get(kind, []) if kind in CAPTURE_ROUTE_KINDS
                   else OCCURRENCE_FORMAT_SOURCES.get(kind, []))
        row = {"id": identifier(item["key"]), "family": item["family"], "record_type": item["record_type"],
               "native_owner_identity": "R0038-" + kind + "-consumer",
               "source_identity": {"input_sha256": member["sha256"], "anchor": item["source_anchor"],
                                   "format_sources": sources},
               "evidence_layer": "public" if kind == "public-census" else "evidence",
               "currentness": {"state": "UNVERIFIED", "invalidators": ["CAPTURE_AUTHENTICATION_NOT_ESTABLISHED"]},
               "observation": item["observation"], "establishes": []}
        if "relation_type" in item:
            row.update({"relation_type": item["relation_type"], "source_entity_id": identifier(item["source_key"]),
                        "target_entity_id": identifier(item["target_key"]), "confidence": "captured-source-structure"})
        records.append(row)
    ids = {row["id"] for row in records}
    if len(ids) != len(records) or any(row.get(key, row["id"]) not in ids for row in records
                                      for key in ("source_entity_id", "target_entity_id")):
        raise ValueError("captured projected identity repeats or relation endpoint is omitted")
    omissions = [{"kind": "CAPTURED_SOURCE_OMISSION", "state": "UNVERIFIED",
                  **{k: v for k, v in row.items() if k != "reason"}, "code": row["reason"]}
                 for row in decoded["omissions"]]
    for family in ("CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE"):
        omissions.append({"kind": "CAPTURE_SCOPE", "family": family, "state": "UNVERIFIED",
                          "code": "CAPTURE_AUTHENTICATION_NOT_ESTABLISHED" if any(r["family"] == family for r in records)
                          else "FAMILY_NOT_CAPTURED"})
    return {"records": sorted(records, key=lambda r: (r["family"], r["id"])),
            "omissions": sorted(omissions, key=canonical)}


"""Pure decoding of exact captured R0033/R003A owner formats for R0038.

No native owner imports, filesystem access, occurrence classification or effects.
The caller must mark every returned row UNVERIFIED with establishes=[]; matching
structure, hashes or source-owned labels never authenticate captured bytes.
"""
import base64 as _route_base64
import hashlib as _route_hashlib
import json as _route_json
import re as _route_re

CAPTURE_ROUTE_KINDS = ("pending", "pending-decision", "route", "route-result", "host-binding")
_route_commit = "fa14948894f583cc0b4e3be80e9283839c9992b5"
_route_pending_source = {"path": "skills/implementaudit/scripts/compaction-audit-pending.py", "commit": _route_commit, # source repo
    "blob": "9e1adfd6aef34906d857f6419709b4405cbcdea0", "sha256": "97e7516bc09d9263de995c108c9693b0e9dc69d1bccfd4effb5e397a22983d74"}
_route_route_source = {"path": "skills/implementaudit/scripts/route-transaction.py", "commit": _route_commit, # source repo
    "blob": "7969902b1bb8dae192a4dcef795d93ba216229b3", "sha256": "6e92da026b597bad2946ee7feff71e73ebaf91d0509ccb3a6d5ea1fabe7e08e3"}
_route_binding_source = {"path": "skills/implementaudit/scripts/host-session-binding.py", "commit": _route_commit, # source repo
    "blob": "df50bec5a5f852e2e01c5d61c7f3fe45cdefd378", "sha256": "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"}
_route_profile_source = {"path": "skills/implementaudit/scripts/compaction-result-profile.py", "commit": _route_commit, # source repo
    "blob": "57bc436862bd8fcfac4402186339dfc82acd952a", "sha256": "0b4e2595d52c108c35f1142322fc15e1716e440eeb75e2fbc5611af6031f9d6c"}
_route_observation_source = {"path": "skills/implementaudit/scripts/compaction-result-observation.py", "commit": _route_commit, # source repo
    "blob": "9d6a6e5c3a4d9e370f69576a7dbff12a2d3bb73d", "sha256": "0ff4589848b4bb37ebe0a4eaf33da8dc5956074b016d50046382ad7814287604"}
ROUTE_FORMAT_SOURCES = {"pending": [_route_pending_source, _route_profile_source, _route_observation_source],
    "pending-decision": [_route_pending_source], "route": [_route_route_source],
    "route-result": [_route_route_source], "host-binding": [_route_binding_source]}
_route_ceiling = {"authority": "NONE", "canonical_currentness": False, "recovery_authority": False,
    "epoch_authority": False, "effect_authority": False, "independent_children": "UNCHANGED",
    "actual_child_result_consumer": "UNQUALIFIED", "same_failed_scope_retry": "CONDITIONAL_UNQUALIFIED"}
_route_pending_kinds = {"COMPLETED_RESUMED_BOUNDARY", "AMBIGUOUS_MARKER_GROUP", "UNRESOLVED_SIGNAL", "UNRESOLVED_RESUME_OBSERVATION"}
_route_sequence = ["OPEN", "LOAD", "USE", "RETURN", "DISPOSE", "RECONCILE"]
_route_stages = ["LOAD", "USE", "DISPOSE"]
_route_children = {"audit-state", "audit-assess", "audit-implement", "audit-andon"}
_route_child_map = {"STALE_CONTEXT_RECONSTRUCTION": "audit-state", "IMMUTABLE_INDEPENDENT_REVIEW": "audit-assess",
    "MAINTAINER_QUALIFICATION": "audit-implement", "NONTRIVIAL_ANDON_DIAGNOSIS": "audit-andon"}
_route_proof_layers = {"source_core": "PRESENT", "package": "UNVERIFIED", "install": "UNVERIFIED", "host_activation": "UNVERIFIED"}
_route_expires = ["action-completion", "next-action-change", "scope-change", "read-set-change", "host-binding-generation-change",
    "continuity-receipt-change", "package-identity-change", "child-source-identity-change", "owner-evidence-change",
    "authority-evidence-change", "dependency-evidence-change", "effect-evidence-change", "contradiction-or-invalidation", "scope-expansion"]


def _route_require(condition, detail):
    if not condition:
        raise ValueError(detail)


def _route_canonical(value, ascii_only=False):
    return _route_json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=ascii_only, allow_nan=False).encode("utf-8")


def _route_digest(value, ascii_only=False):
    return _route_hashlib.sha256(value if type(value) is bytes else _route_canonical(value, ascii_only)).hexdigest()


def _route_checked_json(value):
    # Bound before encoding; reject cycles, ambiguous scalar types and surrogates.
    stack, active, nodes, text_bytes = [(False, value, 0)], set(), 0, 0
    while stack:
        leaving, item, depth = stack.pop()
        if leaving:
            active.remove(id(item)); continue
        nodes += 1
        _route_require(nodes <= 100000 and depth <= 48, "captured JSON exceeds node/depth bounds")
        if type(item) in (dict, list):
            _route_require(id(item) not in active and len(item) <= 4096, "captured JSON cycle or member bound")
            active.add(id(item)); stack.append((True, item, depth))
            if type(item) is dict:
                _route_require(all(type(key) is str for key in item), "captured JSON has a non-text key")
                stack.extend((False, key, depth + 1) for key in item)
                stack.extend((False, member, depth + 1) for member in item.values())
            else:
                stack.extend((False, member, depth + 1) for member in item)
        elif type(item) is str:
            try: text_bytes += len(item.encode("utf-8", "strict"))
            except UnicodeError as exc: raise ValueError("captured JSON contains invalid Unicode") from exc
            _route_require(text_bytes <= 8 * 1024 * 1024, "captured JSON exceeds byte bound")
        elif type(item) is int:
            _route_require(-(2**63) <= item < 2**63, "captured integer is outside canonical range")
        else:
            _route_require(item is None or type(item) is bool, "captured JSON contains an unsupported scalar")
    raw = _route_canonical(value)
    _route_require(len(raw) <= 8 * 1024 * 1024, "captured JSON exceeds encoded byte bound")
    return _route_json.loads(raw)  # Own the result; callers cannot mutate the input through rows.


def _route_closed(value, required, optional=(), label="record"):
    required = set(required.split() if type(required) is str else required)
    optional = set(optional.split() if type(optional) is str else optional)
    _route_require(type(value) is dict and required <= set(value) <= required | optional, label + " has wrong fields")
    return value


def _route_text(value, label, maximum=1024):
    _route_require(type(value) is str and 0 < len(value) <= maximum and all(ord(c) >= 32 for c in value), label + " is not bounded text")


def _route_raw_text(value, label, maximum=8192):
    # Error/frontier payloads are raw owner text, not identifier strings.
    _route_require(type(value) is str and len(value.encode("utf-8")) <= maximum, label + " is not bounded UTF-8 text")


def _route_int(value, label, minimum=0):
    _route_require(type(value) is int and minimum <= value < 2**63, label + " is not a bounded integer")


def _route_match(value, pattern, label):
    _route_require(type(value) is str and _route_re.fullmatch(pattern, value) is not None, label + " is malformed")


def _route_sha(value, label, prefixed=True):
    _route_match(value, ("sha256:" if prefixed else "") + "[0-9a-f]{64}", label)


def _route_oid(value, label):
    _route_match(value, "[0-9a-f]{40}(?:[0-9a-f]{24})?", label)


def _route_generation(value, label):
    _route_match(value, "G[0-9A-F]{4}", label)
    _route_require(int(value[1:], 16) > 0, label + " must be nonzero")


def _route_constants(value, expected, label):
    for key, member in expected.items():
        _route_require(key in value and type(value[key]) is type(member) and value[key] == member, label + "." + key + " differs")


def _route_key(*parts):
    return "r38-owner:" + _route_digest(list(parts))


def _route_record(records, kind, parts, record_type, observation, anchor, family="EXECUTION"):
    key = _route_key(kind, *parts)
    records.append({"key": key, "family": family, "record_type": record_type, "observation": observation,
                    "source_anchor": {**ROUTE_FORMAT_SOURCES[kind][0], "anchor": anchor}})
    return key


def _route_omission(omissions, reason, family="EXECUTION", **detail):
    omissions.append({"family": family, "reason": reason, **detail})


def _route_scope(rows, label, assigned=False):
    _route_require(type(rows) is list, label + " is not a list")
    by_id = {}
    for row in rows:
        _route_closed(row, "id version kind" + (" child_id" if assigned else ""), label=label)
        _route_text(row["id"], label + ".id"); _route_int(row["version"], label + ".version", 1)
        _route_require(row["kind"] in _route_pending_kinds, label + " has an unsupported pending kind")
        if assigned: _route_text(row["child_id"], label + ".child_id")
        _route_require(row["id"] not in by_id, label + " contains a duplicate identity")
        by_id[row["id"]] = row
    return by_id


def _route_source_record(source, label, full=True):
    fields = "path task_id session_id session_meta_sha256 physical sessions_root"
    if full: fields += " prefix_bytes prefix_sha256 provenance native_producer_runtime_equivalence"
    _route_closed(source, fields, "resume_observation_relations" if full else (), label)
    for key in ("path", "task_id", "session_id", "sessions_root"): _route_text(source[key], label + "." + key, 4096)
    _route_closed(source["physical"], "device inode", label=label + ".physical")
    for key in ("device", "inode"): _route_int(source["physical"][key], label + "." + key)
    _route_sha(source["session_meta_sha256"], label, False)
    if full:
        _route_int(source["prefix_bytes"], label + ".prefix_bytes", 1)
        _route_sha(source["prefix_sha256"], label, False)
        _route_constants(source, {"provenance": "HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX",
            "native_producer_runtime_equivalence": "UNVERIFIED"}, label)
        if "resume_observation_relations" in source:
            _route_require(type(source["resume_observation_relations"]) is dict, "resume relations are not a map")
            for rel in source["resume_observation_relations"].values():
                _route_closed(rel, "observation_version later_proved_scope observed_prefix_bytes observed_prefix_sha256 retroactive_child_credit", label="resume relation")
                _route_int(rel["observation_version"], "resume observation version", 1)
                _route_int(rel["observed_prefix_bytes"], "resume prefix bytes", 1)
                _route_sha(rel["observed_prefix_sha256"], "resume prefix hash", False)
                _route_scope(rel["later_proved_scope"], "resume later scope")
                _route_constants(rel, {"retroactive_child_credit": False}, "resume relation")


def _route_pending_observation(item, session):
    _route_closed(item, "id kind version consumed_version proof", label="pending observation")
    _route_text(item["id"], "pending id"); _route_int(item["version"], "pending version", 1)
    _route_int(item["consumed_version"], "consumed version")
    _route_require(item["consumed_version"] <= item["version"], "consumption exceeds observed version")
    kind, proof = item["kind"], item["proof"]
    _route_require(kind in _route_pending_kinds, "unsupported pending observation kind")
    if kind in {"COMPLETED_RESUMED_BOUNDARY", "AMBIGUOUS_MARKER_GROUP"}:
        _route_closed(proof, "source markers resume resume_turn native_producer_runtime_equivalence", label="boundary proof")
        _route_source_record(proof["source"], "boundary source", False)
        _route_require(proof["source"]["session_id"] == session, "boundary source session differs")
        _route_constants(proof, {"native_producer_runtime_equivalence": "UNVERIFIED"}, "boundary proof")
        _route_text(proof["resume_turn"], "resume turn")
        _route_require(type(proof["markers"]) is list and proof["markers"], "boundary markers are absent")
        for row in proof["markers"] + [proof["resume"]]:
            marker = row is not proof["resume"]
            _route_closed(row, "ordinal offset bytes sha256" + (" kind canonical" if marker else ""), label="boundary descriptor")
            for field in ("ordinal", "offset", "bytes"): _route_int(row[field], "descriptor " + field, int(field == "bytes"))
            _route_sha(row["sha256"], "descriptor hash", False)
            if marker:
                _route_require(type(row["canonical"]) is bool, "marker canonical flag is malformed")
                _route_require(row["kind"] in {"compacted", "event_msg", "response_item"} and
                    row["canonical"] == (row["kind"] != "response_item"), "marker kind/canonical pair differs")
        canonical_count = sum(row["canonical"] for row in proof["markers"])
        _route_require((kind == "COMPLETED_RESUMED_BOUNDARY") == (canonical_count == 1), "pending kind contradicts captured canonical marker count")
        _route_require(item["id"] == "boundary-" + _route_digest(proof), "boundary proof identity differs")
    elif kind == "UNRESOLVED_SIGNAL":
        _route_closed(proof, "host_session_id signal hook_source_sha256 binding_generation logical_occurrence_count completion resume delivery_count_is_not_occurrence_identity", label="signal proof")
        _route_constants(proof, {"host_session_id": session, "signal": "SessionStart/source=compact", "logical_occurrence_count": None,
            "completion": "UNRESOLVED", "resume": "UNRESOLVED", "delivery_count_is_not_occurrence_identity": True}, "signal proof")
        _route_sha(proof["hook_source_sha256"], "hook hash", False); _route_generation(proof["binding_generation"], "signal binding")
        _route_require(item["id"] == "unresolved-signal-" + _route_digest(session.encode()), "signal identity differs")
    else:
        _route_closed(proof, "host_session_id entry occurrence_proof logical_occurrence_count delivery_count_is_not_occurrence_identity observed_limits", label="resume proof")
        _route_constants(proof, {"host_session_id": session, "entry": "EXPLICIT_GOVERNOR_POST_COMPACTION_RESUME_OBSERVATION",
            "occurrence_proof": "UNRESOLVED", "logical_occurrence_count": None, "delivery_count_is_not_occurrence_identity": True}, "resume proof")
        if proof["observed_limits"] is not None:
            _route_closed(proof["observed_limits"], "currentness measured_epoch", label="resume observed limits")
        _route_require(item["id"] == "unresolved-resume-" + _route_digest(session.encode()), "resume identity differs")


def _route_file_pin(value, label, maximum=1024 * 1024):
    _route_closed(value, "path bytes sha256", label=label)
    _route_text(value["path"], label + " path", 4096)
    _route_int(value["bytes"], label + " bytes", 1)
    _route_require(value["bytes"] <= maximum, label + " exceeds captured artifact bound")
    _route_sha(value["sha256"], label + " raw-byte digest", False)


def _route_policy(value, code, omissions, child):
    if value == {}:
        _route_omission(omissions, "Incomplete captured fixed policy: descriptor/code digest is absent", "EVIDENCE", child_id=child)
        return False
    _route_closed(value, "descriptor code_and_skill_pins policy_digest", label="fixed policy")
    descriptor = _route_closed(value["descriptor"], "schema profile_id custody_namespace qualification_key authenticating_source_owner", label="policy descriptor")
    _route_constants(descriptor, {"schema": "implementaudit.compaction-fixed-acquisition-policy.v1",
        "profile_id": "codex-desktop-0.153.4-collaboration-public-v1", "custody_namespace": "result-observations-v1",
        "qualification_key": "qualification/Q.json", "authenticating_source_owner": None}, "fixed policy descriptor")
    _route_require(type(value["code_and_skill_pins"]) is dict and value["code_and_skill_pins"], "policy code pins are absent")
    for path, pin in value["code_and_skill_pins"].items():
        _route_text(path, "policy source path", 4096); _route_sha(pin, "policy source hash", False)
    if code is not None:
        _route_require(value["code_and_skill_pins"] == code, "policy code pins differ from assignment")
    _route_require(value["policy_digest"] == _route_digest({k: v for k, v in value.items() if k != "policy_digest"}), "fixed policy digest differs")
    return True


def _route_pending_return_bindings(assignment, state, omissions):
    child, returned, accepted = assignment["child_id"], assignment.get("return"), assignment.get("accepted")
    if returned is None:
        return
    _route_require(type(returned) is dict, "captured pending return is not an object")
    if "child_id" in returned:
        _route_require(returned["child_id"] == child, "return belongs to another assigned child")
    observed = assignment["observations"].get(returned.get("observation_id"))
    if "observation_id" in returned:
        _route_require(observed is not None, "return names an absent selected observation")
        observed_scope = _route_scope(observed["scope"], "selected return scope")
        claims = _route_scope(assignment["scope"], "return assignment scope")
        for identifier, row in observed_scope.items():
            current = state["observations"].get(identifier)
            claim = claims.get(identifier)
            _route_require(current is not None and claim is not None and row["kind"] == current["kind"] == claim["kind"] and
                row["version"] <= current["version"] and row["version"] <= claim["version"], "return coverage is foreign to assigned observation")
    identity = returned.get("identity")
    if "identity" in returned or "return_digest" in returned:
        _route_closed(returned, set("child_id identity return_digest status currentness measured_epoch frontier observation_id evidence".split()) | set(_route_ceiling), label="actual pending return")
        _route_constants(returned, {**_route_ceiling, "child_id": child}, "actual pending return")
        _route_require(returned["status"] in {"SUCCEEDED", "FAILED"} and returned["currentness"] in {"VERIFIED", "UNRESOLVED"} and
            returned["measured_epoch"] in {"VERIFIED", "UNRESOLVED"}, "captured result scalar variant differs")
        _route_require(type(returned["frontier"]) is str and 0 < len(returned["frontier"]) <= 1024, "captured result frontier is malformed")
        # These are the actual R/A fields even when acquisition has no C/Q/E.
        # Reuse the C/E structural checks without inventing source context.
        complete_acceptance = accepted if type(accepted) is dict and ("record" in accepted or "value" in accepted) else None
        _occurrence_result_acceptance(identity, complete_acceptance)
        _route_require(returned["return_digest"] == _route_digest(identity), "return digest differs from captured R identity")
        _route_require(observed is not None and identity["observation_id"] == returned["observation_id"] and
            identity["scope"] == observed["scope"] and observed["scope"], "R identity differs from selected observation scope")
        _route_closed(returned["evidence"], "bound_exchange use child_final parent_delivery", label="return evidence selectors")
        for name in ("bound_exchange", "use"):
            pair = _route_closed(identity[name], "call result", label="return " + name)
            selected = _route_closed(returned["evidence"][name], "call result", label="return selector " + name)
            for side in ("call", "result"):
                locator = pair[side]["locator"]
                if name == "bound_exchange":
                    _route_require(type(selected[side]) is dict and set(selected[side]) == set(locator) and
                        all(selected[side][key] == locator[key] for key in locator if key != "physical_line") and
                        selected[side].get("physical_line") in (None, locator.get("physical_line")), "return evidence selector differs from original bound occurrence")
                else:
                    _route_require(selected[side] == locator, "return USE selector differs from captured occurrence")
        for name in ("child_final", "parent_delivery"):
            locator, selected = identity[name]["locator"], returned["evidence"][name]
            _route_require(selected == locator, "return delivery selector differs")
    else:
        _route_omission(omissions, "Incomplete captured return: existing actual-result identity/digest fields are absent; no result binding is established", "EVIDENCE", child_id=child)
    if accepted is not None:
        if type(accepted) is not dict:
            raise ValueError("captured acceptance is not an object")
        if "record" in accepted or "value" in accepted:
            _route_closed(accepted, "record value", label="captured acceptance")
            av = _route_closed(accepted["value"], "schema action parent_identity actual_child_identity obligation_digest observation_id child_observation_exchange_identity actual_result_digest accepted_boundary_versions observation_source_cutoff authority_ceiling", label="acceptance value")
            _route_constants(av, {"schema": "implementaudit.compaction-reconciliation-acceptance.v1", "action": "ACCEPT_BOUNDED_RECONCILIATION", "authority_ceiling": "NONE"}, "acceptance value")
            _route_require(returned.get("status") == "SUCCEEDED", "acceptance has no successful adjacent return")
            for key in ("obligation_digest", "observation_id", "child_observation_exchange_identity", "actual_result_digest"):
                _route_sha(av[key], "acceptance " + key, False)
            if observed is not None:
                _route_require(av["observation_id"] == returned["observation_id"] and av["accepted_boundary_versions"] == observed["scope"] and
                    av["observation_source_cutoff"] == observed["source_cutoff"], "acceptance observation, scope or cutoff differs")
            if identity is not None:
                _route_require(all(av[key] == identity[key] for key in ("obligation_digest", "observation_id", "child_observation_exchange_identity")) and
                    av["actual_result_digest"] == returned["return_digest"], "acceptance differs from exact adjacent result")
            if identity is None:
                _occurrence_acceptance(av)
                _occurrence_pin(accepted["record"])
                _route_require(accepted["record"]["role"] == "parent", "acceptance record does not belong to parent")
            source = assignment.get("observation_source")
            if type(source) is dict:
                for key in ("parent_identity", "actual_child_identity"):
                    if key in source: _route_require(av[key] == source[key], "acceptance differs from captured source identity")
        else:
            _route_omission(omissions, "Incomplete captured acceptance: existing record/value envelope is absent", "EVIDENCE", child_id=child)
    prepared = assignment.get("prepared", {}).get(returned.get("observation_id"))
    if type(prepared) is dict and "obligation" in prepared:
        obligation = prepared["obligation"]
        _route_closed(obligation, "schema parent_identity actual_child_identity selected_child observation_id covered_boundary_versions observation_source_cutoff code_and_skill_pins bounded_purpose authority_ceiling", label="prepared obligation")
        _route_constants(obligation, {"schema": "implementaudit.compaction-obligation.v1", "selected_child": "audit-state", "authority_ceiling": "NONE"}, "prepared obligation")
        _route_require(observed is not None and obligation["observation_id"] == returned["observation_id"] and
            obligation["covered_boundary_versions"] == observed["scope"] and obligation["observation_source_cutoff"] == observed["source_cutoff"] and
            obligation["code_and_skill_pins"] == assignment["code"], "prepared obligation differs from selected observation")
        if "observation" in prepared: _route_require(prepared["observation"] == observed, "prepared observation differs")
        if "obligation_pin" in prepared:
            _route_file_pin(prepared["obligation_pin"], "prepared obligation raw-byte pin")
            if identity is not None: _route_require(identity["obligation_digest"] == prepared["obligation_pin"]["sha256"], "result obligation pin differs")
        if accepted and "value" in accepted:
            for key in ("parent_identity", "actual_child_identity"):
                _route_require(accepted["value"][key] == obligation[key], "acceptance differs from prepared obligation identity")
    else:
        _route_omission(omissions, "Prepared obligation/source attribution is absent from this captured return; available R/A/scope bindings were checked", "EVIDENCE", child_id=child)
    _route_omission(omissions, "Result/member pins name raw file bytes that were not opened; source records and accepting-parent execution remain unauthenticated", "EVIDENCE", child_id=child)


def _route_merge_episode(decoded, records, omissions, parts):
    translated = {_route_canonical(row["key"]): _route_key("pending-episode", *parts[:2], row["key"]) for row in decoded["records"]}
    existing = {row["key"]: row for row in records}
    for source in decoded["records"]:
        row = {**source, "key": translated[_route_canonical(source["key"])],
            "source_anchor": {**_route_observation_source, "anchor": "episode_value:983-989", "projection_anchor": source["source_anchor"]}}
        for name in ("source_key", "target_key"):
            if name in row: row[name] = translated[_route_canonical(source[name])]
        if row["key"] in existing:
            _route_require(existing[row["key"]] == row, "embedded episode gives conflicting meanings to one identity")
        else:
            records.append(row); existing[row["key"]] = row
    omissions.extend(decoded["omissions"])


def _route_acquisition(proposal, assignment, records, omissions, parts):
    acquisition = proposal["acquisition"]
    child = proposal["child_id"]
    if acquisition == {}:
        _route_omission(omissions, "Incomplete captured acquisition: existing policy/profile/candidate/lookup fields are absent", "EVIDENCE", child_id=child)
        return
    _route_closed(acquisition, "status policy profile candidate lookup episode_record_bound episode origin_validated host_producer_authenticated authority_ceiling unresolved_implementation_edge", "episode_candidate", "captured acquisition")
    _route_constants(acquisition, {"origin_validated": None, "host_producer_authenticated": False, "authority_ceiling": "NONE"}, "captured acquisition")
    _route_raw_text(acquisition["unresolved_implementation_edge"], "acquisition unresolved edge")
    code = assignment["code"] if assignment is not None else None
    _route_require(_route_policy(acquisition["policy"], code, omissions, child), "acquisition has no complete captured fixed policy")
    policy = acquisition["policy"]
    if assignment is not None and assignment.get("policy"):
        _route_require(assignment["policy"] == policy, "acquisition fixed policy differs from assignment")
    profile = acquisition["profile"]
    _route_require(profile == proposal["profile"], "JOIN profile differs from captured acquisition profile")
    qualified = profile.get("status") == "QUALIFICATION_RECORD_BOUND_ORIGIN_UNRESOLVED" if type(profile) is dict else False
    _route_closed(profile, "status policy_qualified qualification_record_bound policy_digest Q" +
        (" evidence review_pins unresolved_implementation_edge" if qualified else ""), label="captured production profile")
    _route_constants(profile, {"status": "QUALIFICATION_RECORD_BOUND_ORIGIN_UNRESOLVED" if qualified else "POLICY_QUALIFICATION_ABSENT",
        "policy_qualified": None, "qualification_record_bound": qualified, "policy_digest": policy["policy_digest"]}, "captured production profile")
    _route_file_pin(acquisition["candidate"], "captured candidate raw-byte pin", 2 * 1024 * 1024)
    _route_closed(acquisition["lookup"], "Q E", label="captured acquisition lookup")
    for name in ("Q", "E"): _route_text(acquisition["lookup"][name], "captured " + name + " locator", 4096)
    _route_require(type(acquisition["episode_record_bound"]) is bool, "episode bound flag is not boolean")
    bound = acquisition["episode_record_bound"]
    if qualified:
        _route_file_pin(profile["Q"], "captured Q raw-byte pin", 2 * 1024 * 1024)
        _route_require(profile["Q"]["path"] == acquisition["lookup"]["Q"], "captured Q pin differs from exact lookup")
        _route_file_pin(profile["evidence"], "qualification candidate raw-byte pin", 2 * 1024 * 1024)
        _route_require(type(profile["review_pins"]) is list and len(profile["review_pins"]) == 2, "qualification review pin population differs")
        for pin in profile["review_pins"]: _route_file_pin(pin, "qualification review raw-byte pin", 2 * 1024 * 1024)
        _route_raw_text(profile["unresolved_implementation_edge"], "profile unresolved edge")
        _route_require("episode_candidate" in acquisition, "qualified-record variant lacks existing episode value")
    else:
        _route_require(profile["Q"] is None and not bound and "episode_candidate" not in acquisition, "absent-Q acquisition claims an episode")
    expected_status = "EPISODE_BOUND_PENDING_ORIGIN_VALIDATOR" if bound else "QUALIFICATION_BOUND_PENDING_EPISODE_ORIGIN" if qualified else "CANDIDATE_ACQUIRED_PENDING_QUALIFICATION"
    _route_require(acquisition["status"] == expected_status, "acquisition status contradicts captured Q/E flags")
    if bound:
        _route_file_pin(acquisition["episode"], "captured E raw-byte pin", 2 * 1024 * 1024)
        _route_require(acquisition["episode"]["path"] == acquisition["lookup"]["E"], "captured E pin differs from exact lookup")
    else: _route_require(acquisition["episode"] is None, "unbound episode has a pin")
    if qualified:
        episode = _route_closed(acquisition["episode_candidate"], "policy_digest parent_identity actual_child_identity assignment_identity obligation_digest observation_id covered_boundary_versions O_U_exchange_USE_R_A_identities physical_source_and_cutoff_identities exact_result_digest exact_acceptance_digest authority_ceiling Q_digest actual_acquisition_and_custody_validation_evidence", label="captured episode value")
        _route_constants(episode, {"policy_digest": policy["policy_digest"], "Q_digest": profile["Q"]["sha256"], "authority_ceiling": "NONE",
            "actual_acquisition_and_custody_validation_evidence": {"candidate": acquisition["candidate"]},
            "exact_result_digest": proposal["return_digest"]}, "captured episode binding")
        _route_require(episode["assignment_identity"] == _route_digest({"child": episode["actual_child_identity"], "code": policy["code_and_skill_pins"]}), "episode assignment digest differs")
        accepted = proposal.get("acceptance") if "acceptance" in proposal else assignment.get("accepted") if assignment is not None else None
        if accepted:
            _route_require(episode["O_U_exchange_USE_R_A_identities"]["A"] == accepted and
                episode["exact_acceptance_digest"] == _route_digest(accepted), "episode acceptance differs from captured JOIN acceptance")
        if assignment is not None and type(assignment.get("return")) is dict:
            returned = assignment["return"]
            if "identity" in returned:
                _route_require(episode["O_U_exchange_USE_R_A_identities"]["R"] == returned["identity"], "episode R differs from captured return identity")
            if "observation_id" in returned:
                observed = assignment["observations"][returned["observation_id"]]
                _route_require(episode["observation_id"] == returned["observation_id"] and episode["covered_boundary_versions"] == observed["scope"] and
                    episode["physical_source_and_cutoff_identities"]["compaction_cutoff"] == observed["source_cutoff"], "episode differs from selected observation/cutoff")
        decoder = globals().get("decode_occurrence_capture")
        if callable(decoder):
            _route_merge_episode(decoder("result-occurrence", episode), records, omissions, parts)
        else:
            _route_omission(omissions, "Captured episode fields are present; pure occurrence companion is not linked for O/U/exchange/USE/R/A projection", "EVIDENCE", child_id=child)
    _route_omission(omissions, "Candidate/Q/E pins identify raw file bytes that were not opened; fixed policy has no authenticating source owner and supplies no native consumption credit", "EVIDENCE", child_id=child)


def _route_logical_join(value, records, omissions, parts, assignment=None):
    logical = value.get("status") == "VERIFIED_LOGICAL_JOIN_PENDING_PROFILE"
    _route_require(logical or value.get("status") == "JOINED_EVIDENCE_ONLY", "unsupported pending JOIN variant")
    fields = "status child_id return_digest pending_consumed host_producer_authenticated profile acquisition"
    fields += " proposed_consumption projected_pending acceptance" if logical else " covered"
    _route_closed(value, set(fields.split()) | set(_route_ceiling), label="pending JOIN")
    _route_constants(value, {**_route_ceiling, "pending_consumed": not logical, "host_producer_authenticated": not logical}, "pending JOIN")
    _route_text(value["child_id"], "JOIN child"); _route_sha(value["return_digest"], "JOIN return", False)
    _route_scope(value["proposed_consumption" if logical else "covered"], "JOIN coverage")
    if logical: _route_scope(value["projected_pending"], "counterfactual pending")
    for key in ("profile", "acquisition") + (("acceptance",) if logical else ()):
        _route_require(type(value[key]) is dict, "JOIN " + key + " is not captured object data")
    if assignment is not None:
        _route_require(value["child_id"] == assignment["child_id"], "JOIN belongs to another assigned child")
        returned = assignment.get("return")
        if type(returned) is dict:
            if "return_digest" in returned:
                _route_require(value["return_digest"] == returned["return_digest"], "JOIN return digest differs from adjacent return")
            observed = assignment["observations"].get(returned.get("observation_id"))
            if observed is not None:
                _route_require(value["proposed_consumption" if logical else "covered"] == observed["scope"], "JOIN coverage differs from selected observation")
            if logical and assignment.get("accepted"):
                _route_require(value["acceptance"] == assignment["accepted"], "JOIN acceptance differs from adjacent acceptance")
    _route_record(records, "pending", parts, "LogicalJoinProposal" if logical else "CompactionJoinObservation", value,
                  "join:589-612", "EVIDENCE")
    _route_acquisition(value, assignment, records, omissions, parts)
    _route_omission(omissions, "Captured JOIN supplies no native consuming acceptance or authenticated origin; historical projected pending never replaces actual pending", "EVIDENCE")


def _route_pending(value, records, omissions):
    if value.get("schema") != "implementaudit.compaction-audit-pending.v1":
        _route_logical_join(value, records, omissions, ["join", value.get("child_id"), value.get("return_digest"), value.get("status")]); return
    _route_closed(value, "schema session_id revision source source_problem signals unresolved_signal_version observations assignments active_child native_producer_runtime_equivalence", label="pending state")
    session = value["session_id"]; _route_text(session, "session")
    for key in ("revision", "signals", "unresolved_signal_version"): _route_int(value[key], key)
    _route_constants(value, {"native_producer_runtime_equivalence": "UNVERIFIED", "active_child": None}, "pending state")
    if value["source"] is not None:
        _route_source_record(value["source"], "pending source")
        _route_require(value["source"]["session_id"] == session, "pending source session differs")
    else: _route_omission(omissions, "Registered pending source is absent; signals remain pending")
    if value["source_problem"] is not None: _route_text(value["source_problem"], "source_problem", 8192)
    _route_require(type(value["observations"]) is dict and type(value["assignments"]) is dict, "pending populations are not maps")
    _route_record(records, "pending", [session, "state"], "PendingAuditState",
                  {k: v for k, v in value.items() if k not in {"observations", "assignments"}}, "state:155-193")
    boundary_keys, claimed = {}, {}
    for identifier, item in value["observations"].items():
        _route_pending_observation(item, session)
        _route_require(identifier == item["id"], "pending map identity differs")
        boundary_keys[identifier] = _route_record(records, "pending", [session, "boundary", identifier], "PendingCompaction",
            {**item, "pending": item["version"] > item["consumed_version"]}, "outstanding:242-244")
    for child, assignment in value["assignments"].items():
        _route_require(type(assignment) is dict and {"child_id", "scope", "code", "observations", "return", "join",
            "native_lifecycle", "reservation_request"} <= set(assignment), "assignment core fields are absent")
        _route_text(child, "assignment child"); _route_require(child == assignment["child_id"], "assignment child identity differs")
        _route_constants(assignment, {"native_lifecycle": "NOT_CLAIMED"}, "assignment")
        scopes = _route_scope(assignment["scope"], "assignment scope")
        for identifier, row in scopes.items():
            observed = value["observations"].get(identifier)
            _route_require(observed is not None and row["kind"] == observed["kind"] and row["version"] <= observed["version"], "assignment scope has a missing/foreign boundary")
            if row["version"] > observed["consumed_version"]:
                _route_require(identifier not in claimed, "conflicting pending scope owners")
                claimed[identifier] = child
        separated = {"observations", "prepared", "return", "join", "logical_join", "accepted", "admission_history", "hold_failures", "hold_refusals"}
        known = separated | {"child_id", "scope", "code", "native_lifecycle", "reservation_request", "policy", "observation_source", "bounded_purpose"}
        extra = sorted(set(assignment) - known)
        if extra: _route_omission(omissions, "Unknown nested assignment fields retained without interpretation", child_id=child, fields=extra)
        reservation_key = _route_record(records, "pending", [session, child, "reservation"], "ChildReservation",
            {k: v for k, v in assignment.items() if k not in separated}, "reserve:451-471")
        for identifier, row in scopes.items():
            link_key = _route_record(records, "pending", [session, child, "scope", identifier], "Relation", row, "scope_owners:247-261")
            records[-1].update(relation_type="SCOPED_TO", source_key=reservation_key, target_key=boundary_keys[identifier])
        for bucket, row_type in (("observations", "ChildScopeObservation"), ("prepared", "PreparedChildObservation"),
                                 ("hold_failures", "NativeRefusal"), ("hold_refusals", "NativeRefusal")):
            members = assignment.get(bucket, {})
            _route_require(type(members) is dict, "assignment " + bucket + " is not a map")
            for identifier, member in members.items():
                _route_text(identifier, "assignment member identity"); _route_require(type(member) is dict, "assignment member is not an object")
                if bucket == "observations":
                    _route_closed(member, "child_id scope code source_cutoff source_problem revision", label="child observation")
                    _route_require(member["child_id"] == child and identifier == _route_digest(member), "child observation identity differs")
                    _route_scope(member["scope"], "child observed scope"); _route_int(member["revision"], "child observation revision")
                _route_record(records, "pending", [session, child, bucket, identifier], row_type, member, "assignment observations:475-539", "EVIDENCE")
        for bucket, row_type in (("return", "ChildReturn"), ("accepted", "ParentAcceptanceObservation")):
            if assignment.get(bucket) is not None:
                _route_require(type(assignment[bucket]) is dict, "assignment " + bucket + " is not an object")
                _route_record(records, "pending", [session, child, bucket], row_type, assignment[bucket], "return/acceptance:540-612", "EVIDENCE")
                records[-1]["source_anchor"] = {**_route_observation_source, "anchor": "actual_result/acceptance:758-855"}
        _route_pending_return_bindings(assignment, value, omissions)
        for bucket in ("logical_join", "join"):
            if assignment.get(bucket) is not None:
                _route_logical_join(assignment[bucket], records, omissions, [session, child, bucket], assignment)
        history = assignment.get("admission_history", [])
        _route_require(type(history) is list, "admission history is not a list")
        for index, item in enumerate(history):
            _route_require(type(item) is dict, "admission history member is not an object")
            _route_logical_join(item, records, omissions, [session, child, "admission_history", index], assignment)
        _route_omission(omissions, "Captured assignment does not authenticate native child identity, source bytes, hold execution or receiving", "EVIDENCE", child_id=child)
    _route_omission(omissions, "Captured pending state supplies no authenticated host attribution or canonical currentness; no epoch is invented")


def _route_pending_decision(value, records, omissions):
    fields = "schema decision audit_state_required state_dependent_decisions_held pending available_scope assigned_scope active_child active_children source_problem signal_observations native_lifecycle native_producer_runtime_equivalence"
    _route_closed(value, set(fields.split()) | set(_route_ceiling), label="pending decision")
    _route_constants(value, {"schema": "implementaudit.compaction-audit-decision.v1", **_route_ceiling,
        "native_lifecycle": "NOT_CLAIMED", "native_producer_runtime_equivalence": "UNVERIFIED"}, "pending decision")
    pending = _route_scope(value["pending"], "pending decision population")
    available = _route_scope(value["available_scope"], "available decision population")
    assigned = _route_scope(value["assigned_scope"], "assigned decision population", True)
    _route_require(not set(available) & set(assigned), "scope is both available and assigned")
    for key, row in list(available.items()) + list(assigned.items()):
        _route_require(key in pending and {k: row[k] for k in ("id", "version", "kind")} == pending[key], "decision scope is missing/foreign")
    expected = [row for key, row in pending.items() if key not in assigned and (row["kind"] == "COMPLETED_RESUMED_BOUNDARY" or not assigned)]
    _route_require(value["available_scope"] == expected, "available scope contradicts assigned pending population")
    children = sorted({row["child_id"] for row in assigned.values()})
    _route_require(value["active_children"] == children and value["active_child"] == (children[0] if len(children) == 1 else None), "active child census differs")
    _route_constants(value, {"audit_state_required": bool(pending), "state_dependent_decisions_held": bool(pending),
        "decision": "AUDIT_STATE_REQUIRED" if available else "WAIT_EXISTING_AUDIT" if pending else "NO_PENDING_AUDIT"}, "pending decision")
    _route_int(value["signal_observations"], "signal observations")
    _route_record(records, "pending-decision", ["observation", _route_digest(value)], "PendingAuditDecision", value, "decision:264-277")
    _route_omission(omissions, "Decision has no host/session attribution fields; source state and native authentication are unverified")


def _route_unique(pairs):
    result = {}
    for key, value in pairs:
        _route_require(key not in result, "duplicate embedded JSON field")
        result[key] = value
    return result


def _route_embedded(value, identity=False, json_value=True):
    _route_closed(value, "bytes digest bytes_b64" + (" identity" if identity else ""), label="embedded bytes")
    _route_int(value["bytes"], "embedded byte count")
    _route_require(value["bytes"] <= 1000000, "embedded bytes exceed owner bound")
    _route_sha(value["digest"], "embedded digest")
    if identity: _route_text(value["identity"], "embedded source identity", 4096)
    _route_require(type(value["bytes_b64"]) is str, "embedded base64 is not text")
    try: raw = _route_base64.b64decode(value["bytes_b64"], validate=True)
    except (ValueError, TypeError) as exc: raise ValueError("embedded base64 is malformed") from exc
    _route_require(len(raw) == value["bytes"] and "sha256:" + _route_digest(raw) == value["digest"] and
        _route_base64.b64encode(raw).decode() == value["bytes_b64"], "embedded byte identity differs")
    if not json_value: return raw
    try: decoded = _route_json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=_route_unique)
    except (UnicodeError, ValueError, RecursionError) as exc: raise ValueError("embedded JSON is malformed") from exc
    return _route_checked_json(decoded)


def _route_packet(value, obligation, transaction):
    _route_closed(value, "schema obligation_id route_transaction_id source_event target_identity", label="route packet")
    _route_constants(value, {"schema": "implementaudit.route-packet.v1", "obligation_id": obligation, "route_transaction_id": transaction}, "route packet")
    _route_require(value["target_identity"] in _route_children, "packet has unknown governed child")
    event = _route_closed(value["source_event"], "schema source_identity provenance body kind reactivation", label="source event")
    _route_constants(event, {"schema": "implementaudit.source-event.v1"}, "source event")
    _route_match(event["source_identity"], "[A-Za-z0-9][A-Za-z0-9._:-]{0,255}", "source identity")
    p = _route_closed(event["provenance"], "schema event_id host_correlation_id", label="source provenance")
    _route_constants(p, {"schema": "implementaudit.source-event-provenance.v1", "event_id": event["source_identity"]}, "source provenance")
    _route_sha(p["host_correlation_id"], "source correlation")
    _route_require(type(event["body"]) is str and 0 < len(event["body"].encode()) <= 100000 and "\0" not in event["body"], "source event body is malformed")
    _route_require(event["kind"] in {"one-shot-action", "standing-constraint"}, "source event kind is unsupported")
    _route_closed(event["reactivation"], "reopen target_changed invalidating_evidence", label="reactivation")
    _route_require(all(type(v) is bool for v in event["reactivation"].values()), "reactivation is not boolean")


def _route_stage(value, ascii_identity=False):
    _route_closed(value, "schema owner_id host_id host_session_id binding_generation selected_child packet_digest obligation_id route_transaction_id stage event_id receipt_identity", label="host stage")
    _route_constants(value, {"schema": "implementaudit.host-holon-stage-receipt.v1"}, "host stage")
    for key in ("owner_id", "host_id", "host_session_id", "event_id"): _route_text(value[key], "host stage " + key)
    _route_generation(value["binding_generation"], "stage binding")
    _route_require(value["selected_child"] in _route_children and value["stage"] in _route_stages, "stage/child is unknown")
    for key in ("packet_digest", "obligation_id", "route_transaction_id", "receipt_identity"): _route_sha(value[key], key)
    body = {k: v for k, v in value.items() if k != "receipt_identity"}
    _route_require(value["receipt_identity"] == "sha256:" + _route_digest(body, ascii_identity), "stage receipt identity differs")


def _route_stage_compatibility(value, omissions):
    body = {k: v for k, v in value.items() if k != "receipt_identity"}
    if _route_digest(body, True) != _route_digest(body, False):
        _route_omission(omissions, "Frozen H0 stage identity uses ASCII escapes; frozen R0033 resolved-stage identity uses UTF-8. This captured H0 receipt is route-incompatible pending a shared owner canonicalization decision", "EVIDENCE",
                        receipt_identity=value["receipt_identity"])


def _route_execution(value, record, packet, records, omissions):
    _route_closed(value, "schema owner_id host_id host_session_id binding_generation selected_child route_transaction_id obligation_id packet_digest stages", label="resolved execution")
    _route_constants(value, {"schema": "implementaudit.resolved-holon-execution-evidence.v1",
        "host_id": record["host_id"], "host_session_id": record["host_session_id"], "binding_generation": record["host_binding_generation"],
        "selected_child": packet["target_identity"], "route_transaction_id": record["route_transaction_id"],
        "obligation_id": record["obligation_id"]}, "resolved execution")
    _route_require(type(value["stages"]) is list and len(value["stages"]) == 3, "resolved execution stage set differs")
    seen = set()
    for name, stage in zip(_route_stages, value["stages"]):
        _route_stage(stage)
        _route_constants(stage, {key: value[key] for key in ("owner_id", "host_id", "host_session_id", "binding_generation",
            "selected_child", "route_transaction_id", "obligation_id", "packet_digest")}, "resolved stage")
        _route_require(stage["stage"] == name and stage["receipt_identity"] not in seen, "resolved stage order/identity differs")
        seen.add(stage["receipt_identity"])
        _route_record(records, "route", [record["route_transaction_id"], "stage", name], "HostStageReceipt", stage, "resolved_execution:974-1014", "EVIDENCE")
    _route_omission(omissions, "Captured stage identities are unverified without original host-store resolution", "EVIDENCE")


def _route_lifecycle(record, records, omissions):
    life = record["lifecycle"]
    v4 = record.get("recovery_capsule", {}).get("schema") == "implementaudit.post-compaction-recovery.v4"
    _route_closed(life, "state required_record_oid delivery child_return governor_decision governor_decision_count source_event_status" + (" attempt_evidence" if v4 else ""),
                  "execution_evidence logical_task", "route lifecycle")
    abandoned = record["route_state"] == "ABANDONED"
    _route_require(life["state"] in ({"OPEN", "RETURNED"} if abandoned else {record["route_state"]}), "route lifecycle state differs")
    _route_oid(life["required_record_oid"], "required record")
    argv = record["action"]["argv"]
    _route_require(len(argv) == 2 and argv[0] == "route-trigger" and argv[1] in _route_child_map,
        "full route lifecycle has no exact mapped governed-child action")
    selected_child = _route_child_map[argv[1]]
    if "logical_task" in life:
        task = life["logical_task"]
        _route_match(task, "[a-z0-9][a-z0-9_-]{0,127}", "logical task")
        _route_require(task not in _route_children | {selected_child, record["route_transaction_id"], record["host_session_id"]} and
            _route_re.fullmatch("[0-9a-f]{32,64}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", task) is None,
            "logical task aliases a governed role, session, transaction or opaque identity")
    if v4:
        attempt = _route_closed(life["attempt_evidence"], "schema capsule_digest native_observation_identity source_reader_digest evidence evidence_digest", label="recovery attempt evidence")
        capsule, native = record["recovery_capsule"], record["recovery_capsule"]["native_observation"]
        _route_constants(attempt, {"schema": "implementaudit.qualified-recovery-attempt-evidence.v1",
            "capsule_digest": capsule["capsule_digest"], "native_observation_identity": native["observation_identity"]}, "recovery attempt evidence")
        for key in ("source_reader_digest", "evidence_digest", "native_observation_identity"):
            _route_sha(attempt[key], "recovery attempt " + key)
        _route_require(type(attempt["evidence"]) is dict, "native attempt evidence is not an object")
        _route_constants(attempt["evidence"], {**{key: native[key] for key in
            ("native_thread_id", "native_session_id", "native_turn_id", "epoch_identity")},
            "input_row_digest": native["row_digest"]}, "native attempt identity tuple")
        _route_require(attempt["evidence_digest"] == "sha256:" + _route_digest({k: v for k, v in attempt.items() if k != "evidence_digest"}), "recovery attempt digest differs")
        _route_record(records, "route", [record["route_transaction_id"], "attempt"], "RecoveryAttemptEvidence", attempt, "recovery_attempt_evidence_record_v1:3362-3384", "EVIDENCE")
        _route_omission(omissions, "Recovery attempt native evidence semantics require the frozen native-observer owner; captured identity agreement does not authenticate an attempt", "EVIDENCE")
    _route_closed(life["delivery"], "child packet", label="delivery")
    _route_embedded(life["delivery"]["child"], True, False)
    _route_require({k: life["delivery"]["child"][k] for k in ("identity", "digest")} == record["child_source"], "delivery child source differs")
    packet = _route_embedded(life["delivery"]["packet"])
    _route_packet(packet, record["obligation_id"], record["route_transaction_id"])
    _route_require(packet["target_identity"] == selected_child, "packet selected child differs from exact route action")
    status = life["state"]
    _route_constants(life, {"governor_decision_count": int(status == "SATISFIED")}, "route lifecycle")
    _route_require((life["child_return"] is not None) == (status in {"RETURNED", "SATISFIED"}) and
        (life["governor_decision"] is not None) == (status == "SATISFIED"), "route lifecycle return/decision presence differs")
    expected_status = "satisfied" if status == "SATISFIED" and packet["source_event"]["kind"] == "one-shot-action" else "active"
    _route_require(life["source_event_status"] == expected_status, "source-event lifecycle status differs")
    transaction = record["route_transaction_id"]
    _route_record(records, "route", [transaction, "lifecycle"], "RouteLifecycle", life, "validate_route_record_local:1841-1989")
    if life["child_return"] is not None:
        returned = _route_embedded(life["child_return"])
        _route_closed(returned, "schema obligation_id route_transaction_id packet_digest status payload", label="child return")
        _route_constants(returned, {"schema": "implementaudit.child-return.v1", "status": "RETURNED", "obligation_id": record["obligation_id"],
            "route_transaction_id": transaction, "packet_digest": life["delivery"]["packet"]["digest"]}, "child return")
        _route_require(type(returned["payload"]) is dict, "child return payload is not an object")
        raw_execution = returned["payload"].get("holon_execution_evidence")
        _route_require((raw_execution is None) == (life.get("execution_evidence") is None), "returned and resolved execution presence differs")
        _route_record(records, "route", [transaction, "return"], "ChildReturn", returned, "child_return_record:527-572", "EVIDENCE")
        if raw_execution is not None:
            _route_closed(raw_execution, "schema selected_child route_transaction_id obligation_id packet_digest stages", label="named execution evidence")
            _route_constants(raw_execution, {"schema": "implementaudit.holon-execution-evidence.v1", "selected_child": packet["target_identity"],
                "route_transaction_id": transaction, "obligation_id": record["obligation_id"], "packet_digest": life["delivery"]["packet"]["digest"]}, "named execution")
            _route_require(type(raw_execution["stages"]) is list and len(raw_execution["stages"]) == 3, "named stages differ")
            for name, row in zip(_route_stages, raw_execution["stages"]):
                _route_closed(row, "stage receipt_identity", label="named stage"); _route_sha(row["receipt_identity"], "named receipt")
                _route_require(row["stage"] == name, "named stage order differs")
            _route_require([r["receipt_identity"] for r in raw_execution["stages"]] ==
                [r.get("receipt_identity") for r in life["execution_evidence"].get("stages", [])], "named/resolved receipt identities differ")
    if life["governor_decision"] is not None:
        decision = _route_embedded(life["governor_decision"])
        _route_closed(decision, "schema obligation_id route_transaction_id return_digest outcome reason", label="governor decision")
        _route_constants(decision, {"schema": "implementaudit.governor-route-decision.v1", "outcome": "SATISFIED",
            "obligation_id": record["obligation_id"], "route_transaction_id": transaction, "return_digest": life["child_return"]["digest"]}, "governor decision")
        _route_text(decision["reason"], "governor decision reason")
        _route_record(records, "route", [transaction, "governor-decision"], "GovernorRouteDecision", decision, "governor_decision_record:575-593", "EVIDENCE")
    if life.get("execution_evidence") is not None:
        _route_require(life["execution_evidence"].get("packet_digest") == life["delivery"]["packet"]["digest"], "resolved packet differs")
        _route_execution(life["execution_evidence"], record, packet, records, omissions)
    else: _route_omission(omissions, "LOAD/USE/DISPOSE have no resolved host execution evidence", "EVIDENCE", route_transaction_id=transaction)


def _route_record_value(value, records, omissions):
    recovery = value.get("schema") == "implementaudit.route-recovery-decision.v1"
    shared = "schema predicate_version controller_id claim_id explicit_run_root host_id host_session_id host_binding_generation host_correlation_id scope action package child_source decision classification predecessor_record_oid route_transaction_id obligation_id route_state child_lifecycle_owned record_identity"
    ordinary = "continuity_generation continuity_receipt boundary evidence inputs invalidators expiry_fingerprint expires_on consumed_record_oid"
    _route_closed(value, shared + (" recovery_capsule continuity_current ordinary_effect_authority" if recovery else " " + ordinary),
                  "lifecycle disposition" if recovery else "lifecycle history_query presentation", "route record")
    _route_require(value["schema"] in {"implementaudit.route-decision.v1", "implementaudit.route-recovery-decision.v1"}, "unsupported route schema")
    for key in ("controller_id", "claim_id", "explicit_run_root", "host_id", "host_session_id"): _route_text(value[key], key, 4096)
    _route_generation(value["host_binding_generation"], "route host binding")
    for key in ("host_correlation_id", "route_transaction_id", "record_identity"): _route_sha(value[key], key)
    if value["predecessor_record_oid"] is not None: _route_oid(value["predecessor_record_oid"], "predecessor")
    _route_closed(value["scope"], "identity digest", label="route scope"); _route_text(value["scope"]["identity"], "scope identity")
    _route_sha(value["scope"]["digest"], "scope digest")
    _route_closed(value["action"], "identity digest class argv", label="route action")
    for key in ("identity", "class"): _route_text(value["action"][key], "action " + key)
    _route_sha(value["action"]["digest"], "action digest")
    _route_require(type(value["action"]["argv"]) is list and 0 < len(value["action"]["argv"]) <= 64, "route argv bound")
    for arg in value["action"]["argv"]: _route_text(arg, "route argv token", 4096)
    _route_closed(value["child_source"], "identity digest", label="child source")
    _route_text(value["child_source"]["identity"], "child source identity", 4096); _route_sha(value["child_source"]["digest"], "child source digest")
    _route_require(type(value["package"]) is dict, "route package is not an object")
    _route_require(value["decision"] in {"PENDING", "NOT_REQUIRED", "REQUIRED"} and value["classification"] in
        {"MECHANICALLY_REQUIRED", "MECHANICALLY_NOT_REQUIRED", "JUDGEMENT_REQUIRED"}, "route decision/classification is unknown")
    has_lifecycle = "lifecycle" in value
    _route_constants(value, {"child_lifecycle_owned": has_lifecycle}, "route record")
    if value["decision"] == "REQUIRED":
        _route_sha(value["obligation_id"], "obligation")
        allowed = {"OPEN", "RETURNED", "SATISFIED"} if has_lifecycle else {"UNSATISFIED"}
        if recovery and has_lifecycle and "disposition" in value: allowed = {"ABANDONED"}
        _route_require(value["route_state"] in allowed, "required route state differs")
    else: _route_constants(value, {"route_state": None, "obligation_id": None, "child_lifecycle_owned": False}, "non-required route")
    if recovery:
        _route_constants(value, {"decision": "REQUIRED", "classification": "MECHANICALLY_REQUIRED", "continuity_current": False,
            "ordinary_effect_authority": "NONE"}, "recovery route")
        capsule = _route_closed(value["recovery_capsule"], "schema custody native_observation native_invocation_digest event_id event_digest scope_digest selected_child return_contract package child_source continuity_current ordinary_effect_authority subject_cause_attested capsule_digest", "attempt_boundary", "recovery capsule")
        v4 = capsule["schema"] == "implementaudit.post-compaction-recovery.v4"
        _route_require(v4 or capsule["schema"] == "implementaudit.post-compaction-recovery.v3", "unsupported recovery capsule version")
        _route_require(("attempt_boundary" in capsule) == v4, "recovery attempt variant differs")
        _route_constants(value, {"predicate_version": "R0033.recovery-cognition.v2" if v4 else "R0033.recovery-cognition.v1"}, "recovery route")
        _route_constants(capsule, {"selected_child": "audit-state", "continuity_current": False, "ordinary_effect_authority": "NONE",
            "subject_cause_attested": False, "return_contract": "implementaudit.audit-state-minimum-frontier-return.v2" if v4 else "implementaudit.audit-state-minimum-frontier-return.v1"}, "recovery capsule")
        for key in ("custody", "native_observation", "package", "child_source"): _route_require(type(capsule[key]) is dict, "recovery " + key + " is not an object")
        for key in ("native_invocation_digest", "event_digest", "scope_digest", "capsule_digest"): _route_sha(capsule[key], "recovery " + key)
        _route_require(capsule["capsule_digest"] == "sha256:" + _route_digest({k: v for k, v in capsule.items() if k != "capsule_digest"}), "recovery capsule identity differs")
        _route_require(capsule["package"] == value["package"] and capsule["child_source"] == value["child_source"], "recovery source tuple differs")
        if "disposition" in value:
            d = _route_closed(value["disposition"], "schema old_record_oid old_record_identity route_transaction_id capsule_digest admission_identity reason evidence_digest source_transition_digest successor_package successor_child_source continuity_current ordinary_effect_authority recovery_cognition_accepted", "preserved_source_root", "recovery abandonment")
            _route_constants(d, {"schema": "implementaudit.recovery-abandonment.v1", "route_transaction_id": value["route_transaction_id"],
                "capsule_digest": capsule["capsule_digest"], "old_record_oid": value["predecessor_record_oid"],
                "continuity_current": False, "ordinary_effect_authority": "NONE", "recovery_cognition_accepted": False}, "abandonment")
            _route_require(d["reason"] in {"ADMISSION_REJECTED", "CHILD_REFUSED"}, "abandonment reason is unknown")
            for key in ("old_record_identity", "admission_identity", "evidence_digest", "source_transition_digest"): _route_sha(d[key], key)
            _route_record(records, "route", [value["route_transaction_id"], "abandonment"], "RecoveryAbandonment", d, "recovery_abandon_base_v1:3073-3118", "EVIDENCE")
        _route_omission(omissions, "Recovery nested native/custody/attempt semantics and predecessor evidence require the original owner; canonical currentness is absent")
    else:
        _route_constants(value, {"predicate_version": "R0033.route-predicate.v1", "expires_on": _route_expires}, "route record")
        _route_generation(value["continuity_generation"], "continuity generation"); _route_text(value["continuity_receipt"], "continuity receipt")
        boundary = _route_closed(value["boundary"], "kind event_id digest", label="route boundary")
        for key in ("kind", "event_id"): _route_text(boundary[key], "boundary " + key)
        _route_sha(boundary["digest"], "boundary digest"); _route_sha(value["expiry_fingerprint"], "expiry fingerprint")
        _route_require(type(value["inputs"]) is list and value["inputs"] and type(value["evidence"]) is dict and type(value["invalidators"]) is list, "route input/evidence population differs")
        names = []
        for item in value["inputs"]:
            _route_closed(item, "identity path digest status", label="route input")
            _route_text(item["identity"], "input identity"); _route_text(item["path"], "input path", 4096)
            _route_sha(item["digest"], "input digest"); _route_require(item["status"] in {"CURRENT", "STALE"}, "input state differs")
            names.append(item["identity"])
        _route_require(names == sorted(set(names)), "route inputs are not uniquely ordered")
        if value["consumed_record_oid"] is not None: _route_oid(value["consumed_record_oid"], "consumed record")
        if "presentation" in value:
            _route_closed(value["presentation"], "parent_holon consuming_frontier", label="route presentation")
            for member in value["presentation"].values(): _route_text(member, "route presentation", 240)
    _route_require(value["record_identity"] == "sha256:" + _route_digest({k: v for k, v in value.items() if k != "record_identity"}), "route record identity differs")
    _route_record(records, "route", [value["controller_id"], value["route_transaction_id"], "route"], "RouteObligation",
        {k: v for k, v in value.items() if k not in {"lifecycle", "disposition"}}, "record:208-218,2590-2601")
    if has_lifecycle: _route_lifecycle(value, records, omissions)
    _route_omission(omissions, "R0035 per-obligation affected-node mapping is not present in this owner format")
    _route_omission(omissions, "Native current-ref/predicate, binding authenticity and separate post-return currentness observation are unverified")


def _route_projection(value, state=None):
    _route_closed(value, "required_sequence completed selected_child route_transaction_id obligation_id identity_bound unverified child_authority child_can_route governor_reconciliation_required canonical_credit", label="holon lifecycle projection")
    _route_constants(value, {"required_sequence": _route_sequence, "identity_bound": True, "child_authority": "NONE", "child_can_route": False}, "holon projection")
    _route_require(value["selected_child"] in _route_children and type(value["completed"]) is list, "holon projection child/completed differs")
    _route_require(value["completed"] == [stage for stage in _route_sequence if stage in value["completed"]], "completed stages are duplicate/foreign/reordered")
    _route_require(len(set(value["completed"]) & set(_route_stages)) in {0, 3}, "projection contains a partial resolved stage set")
    if state is not None:
        base = {"UNSATISFIED": [], "OPEN": ["OPEN"], "RETURNED": ["OPEN", "RETURN"],
                "SATISFIED": ["OPEN", "RETURN", "RECONCILE"]}
        _route_require(state in base and [stage for stage in value["completed"] if stage not in _route_stages] == base[state], "projection completed stages contradict route state")
    expected = [stage for stage in _route_stages if stage not in value["completed"]]
    _route_require(value["unverified"] == expected, "unverified stages differ")
    reconciled = "RECONCILE" in value["completed"]
    _route_constants(value, {"governor_reconciliation_required": not reconciled, "canonical_credit": reconciled and not expected}, "holon projection")
    _route_sha(value["route_transaction_id"], "projection transaction"); _route_sha(value["obligation_id"], "projection obligation")


def _route_result(value, records, omissions):
    _route_require(value.get("schema") == "implementaudit.route-transaction-result.v1", "unsupported route result schema")
    status = value.get("status")
    core = "schema status decision route_state advance_allowed enforcement_available record_oid record_identity"
    if status == "UNAVAILABLE":
        _route_closed(value, "schema status decision advance_allowed enforcement_available error", label="route refusal")
        _route_constants(value, {"advance_allowed": False, "enforcement_available": False}, "route refusal")
        _route_require(value["decision"] in {"PENDING", "NOT_REQUIRED", "REQUIRED"}, "route refusal decision is unknown")
        _route_raw_text(value["error"], "route refusal error")
        _route_record(records, "route-result", ["refusal", _route_digest(value)], "NativeRefusal", value, "fail:241-252")
        _route_omission(omissions, "Captured native refusal supplies no record identity, currentness or effect authority")
        return
    if status == "ROUTE_COMPLETE":
        _route_closed(value, core + " governor_decision_count post_return_currentness holon_lifecycle history_read_performed idempotent", label="route completion")
        _route_constants(value, {"decision": "REQUIRED", "route_state": "SATISFIED", "advance_allowed": True,
            "enforcement_available": True, "governor_decision_count": 1, "post_return_currentness": "VERIFIED", "history_read_performed": False}, "route completion")
    elif status == "CURRENT":
        _route_closed(value, core + " classification admission_required obligation_id route_transaction_id selected_child governor_decision_count history_query history_read_performed mirror_claim mirror_status projection_status proof_layers host_activation_proven", "presentation", "current route result")
        _route_constants(value, {"enforcement_available": True, "history_read_performed": False, "proof_layers": _route_proof_layers, "host_activation_proven": False}, "current result")
        _route_require(value["decision"] in {"PENDING", "NOT_REQUIRED", "REQUIRED"}, "current result decision differs")
        _route_require(value["projection_status"] in {"CURRENT", "INVALID", "LEGACY_ABSENT", "UNAVAILABLE"} and
            value["mirror_status"] in {"IGNORED_ABSENT", "IGNORED_CORROBORATION", "IGNORED_CONTRADICTION"}, "route disagreement status differs")
        _route_require(value["classification"] in {"MECHANICALLY_REQUIRED", "MECHANICALLY_NOT_REQUIRED", "JUDGEMENT_REQUIRED"}, "current classification is unknown")
        required = value["decision"] == "REQUIRED"
        if required:
            _route_require(value["route_state"] in {"UNSATISFIED", "OPEN", "RETURNED", "SATISFIED"} and
                value["selected_child"] in _route_children, "current route state/child differs")
            for key in ("obligation_id", "route_transaction_id"): _route_sha(value[key], "current " + key)
        else:
            _route_constants(value, {"route_state": None, "selected_child": None, "obligation_id": None, "route_transaction_id": None}, "non-required current result")
        _route_constants(value, {"governor_decision_count": int(value["route_state"] == "SATISFIED"),
            "advance_allowed": required and value["route_state"] == "SATISFIED",
            "admission_required": value["decision"] == "NOT_REQUIRED"}, "current result")
        _route_require(value["history_query"] is None or type(value["history_query"]) is dict, "history query is not captured object data")
        _route_require(value["mirror_claim"] in {"ABSENT", "PENDING", "SATISFIED"}, "mirror claim is unknown")
        canonical = value["route_state"] if required else value["decision"]
        mirror = "IGNORED_ABSENT" if value["mirror_claim"] == "ABSENT" else "IGNORED_CORROBORATION" if value["mirror_claim"] == canonical else "IGNORED_CONTRADICTION"
        _route_constants(value, {"mirror_status": mirror}, "current mirror observation")
        if "presentation" in value:
            _route_closed(value["presentation"], "parent_holon consuming_frontier", label="current presentation")
            for member in value["presentation"].values(): _route_text(member, "current presentation", 240)
    elif status in {"CHILD_OPEN", "CHILD_RETURNED"}:
        extra = " obligation_id route_transaction_id delivery" if status == "CHILD_OPEN" else " child_return"
        _route_closed(value, core + extra + " holon_lifecycle history_read_performed", label="child route result")
        _route_constants(value, {"decision": "REQUIRED", "route_state": "OPEN" if status == "CHILD_OPEN" else "RETURNED",
            "advance_allowed": False, "enforcement_available": True, "history_read_performed": False}, "child route result")
        projection = value["holon_lifecycle"]
        _route_projection(projection, value["route_state"])
        if status == "CHILD_OPEN":
            _route_constants(value, {key: projection[key] for key in ("obligation_id", "route_transaction_id")}, "open result")
            _route_closed(value["delivery"], "child packet", label="open result delivery")
            _route_embedded(value["delivery"]["child"], True, False)
            packet = _route_embedded(value["delivery"]["packet"])
            _route_packet(packet, value["obligation_id"], value["route_transaction_id"])
            _route_require(packet["target_identity"] == projection["selected_child"], "open result selected child differs")
        else:
            returned = _route_embedded(value["child_return"])
            _route_closed(returned, "schema obligation_id route_transaction_id packet_digest status payload", label="returned result body")
            _route_constants(returned, {"schema": "implementaudit.child-return.v1", "status": "RETURNED",
                **{key: projection[key] for key in ("obligation_id", "route_transaction_id")}}, "returned result body")
            _route_sha(returned["packet_digest"], "returned result packet")
            _route_require(type(returned["payload"]) is dict, "returned result payload is not an object")
            _route_omission(omissions, "Return-result packet predecessor and nested execution evidence need the separately captured route lifecycle", "EVIDENCE")
    elif status in {"RECOVERY_UNSATISFIED", "RECOVERY_OPEN", "RECOVERY_RETURNED", "RECOVERY_SATISFIED"}:
        _route_closed(value, "schema status decision record_oid record_identity route_transaction_id obligation_id route_state advance_allowed continuity_current ordinary_effect_authority subject_cause_attested recovery_cognition_accepted owner_reconciliation_required idempotent", label="recovery result")
        _route_constants(value, {"decision": "REQUIRED", "route_state": status.removeprefix("RECOVERY_"), "advance_allowed": False,
            "continuity_current": False, "ordinary_effect_authority": "NONE", "subject_cause_attested": False,
            "recovery_cognition_accepted": status == "RECOVERY_SATISFIED", "owner_reconciliation_required": True}, "recovery result")
    elif status == "RECOVERY_ABANDONED":
        _route_closed(value, "schema status record_oid record_identity route_transaction_id route_state advance_allowed continuity_current ordinary_effect_authority recovery_cognition_accepted native_invocation_remains_consumed historical_source_retained", label="abandonment result")
        _route_constants(value, {"route_state": "ABANDONED", "advance_allowed": False, "continuity_current": False,
            "ordinary_effect_authority": "NONE", "recovery_cognition_accepted": False, "native_invocation_remains_consumed": True,
            "historical_source_retained": True}, "abandonment result")
    else: raise ValueError("unsupported route result status")
    _route_oid(value["record_oid"], "result record OID"); _route_sha(value["record_identity"], "result record identity")
    for key in ("route_transaction_id", "obligation_id"):
        if key in value and value[key] is not None: _route_sha(value[key], "result " + key)
    if "holon_lifecycle" in value: _route_projection(value["holon_lifecycle"], value["route_state"])
    for key in ("idempotent", "advance_allowed", "admission_required"):
        if key in value: _route_require(type(value[key]) is bool, "result " + key + " is not boolean")
    _route_record(records, "route-result", [value["record_oid"], status], "RouteResult", value, "results:3007-3013,4984-5006,5400-5435")
    _route_omission(omissions, "Captured result currentness, post-return checks and accepting-consumer execution remain unverified")


def _route_binding_record(value):
    _route_closed(value, "schema host_id host_session_id controller_id claim_id explicit_run_root repository_identity git_common_directory_identity worktree_identity binding_generation activation_event_id activation_receipt applicable_continuity_generation applicable_continuity_receipt status predecessor_generation supersession_or_tombstone_reason", label="host binding")
    _route_constants(value, {"schema": "implementaudit.host-session-binding.v1"}, "host binding")
    for key in ("host_id", "host_session_id", "controller_id", "claim_id", "explicit_run_root", "repository_identity",
                "git_common_directory_identity", "worktree_identity", "activation_event_id", "activation_receipt", "applicable_continuity_receipt"):
        _route_text(value[key], "binding " + key, 4096)
    _route_generation(value["binding_generation"], "binding generation")
    _route_generation(value["applicable_continuity_generation"], "applicable continuity generation")
    _route_require(value["status"] in {"ACTIVE", "SUPERSEDED", "TOMBSTONED"}, "binding status is unknown")
    ordinal = int(value["binding_generation"][1:], 16)
    expected = None if ordinal == 1 else "G" + format(ordinal - 1, "04X")
    _route_require(ordinal > 0 and value["predecessor_generation"] == expected, "binding predecessor generation differs")
    if value["supersession_or_tombstone_reason"] is not None: _route_text(value["supersession_or_tombstone_reason"], "binding transition reason")


def _route_host(value, records, omissions):
    schema = value.get("schema")
    if schema == "implementaudit.host-session-binding.v1":
        _route_binding_record(value)
        _route_record(records, "host-binding", [value["host_id"], value["host_session_id"], value["binding_generation"]], "HostSessionBinding", value, "validate_record:323-365")
    elif schema == "implementaudit.host-session-binding-state.v1":
        _route_closed(value, "schema host_id host_session_id records", label="binding state")
        _route_require(type(value["records"]) is list and value["records"], "binding state is empty")
        generations, active = [], []
        for item in value["records"]:
            _route_binding_record(item)
            _route_constants(item, {"host_id": value["host_id"], "host_session_id": value["host_session_id"]}, "binding state member")
            generations.append(item["binding_generation"])
            if item["status"] == "ACTIVE": active.append(item)
        _route_require(generations == sorted(set(generations)) and len(active) <= 1, "binding generation census differs")
        _route_require((active and active[0] is value["records"][-1]) or (not active and value["records"][-1]["status"] == "TOMBSTONED"), "binding active/tombstone frontier differs")
        _route_require(all(item["status"] == "SUPERSEDED" for item in value["records"][:-1]), "historical binding is not superseded")
        for item in value["records"]: _route_host(item, records, omissions)
    elif schema == "implementaudit.host-session-binding-result.v1":
        status = value.get("status")
        common = "schema status host_activation_proven proof_layers"
        if status == "UNAVAILABLE":
            _route_closed(value, "schema status enforcement_available error", label="host refusal")
            _route_constants(value, {"enforcement_available": False}, "host refusal")
            _route_raw_text(value["error"], "host refusal error")
            _route_record(records, "host-binding", ["refusal", _route_digest(value)], "NativeRefusal", value, "fail:57-70")
        elif status == "UNBOUND":
            _route_closed(value, "schema status enforcement_available", label="unbound result")
            _route_constants(value, {"enforcement_available": False}, "unbound result")
        elif status in {"BOUND", "TOMBSTONED"}:
            _route_closed(value, common + " binding" + (" enforcement_available" if status == "TOMBSTONED" else ""), label="binding result")
            _route_binding_record(value["binding"])
            _route_require(value["binding"]["status"] == ("TOMBSTONED" if status == "TOMBSTONED" else "ACTIVE"), "result/binding status differs")
            if status == "TOMBSTONED": _route_constants(value, {"enforcement_available": False}, "tombstone result")
            _route_host(value["binding"], records, omissions)
        elif status == "ATTRIBUTED":
            _route_closed(value, common + " binding_generation correlation_id", "obligation_id route_transaction_id", "attribution result")
            _route_generation(value["binding_generation"], "attribution generation"); _route_sha(value["correlation_id"], "attribution correlation")
            _route_require(("obligation_id" in value) == ("route_transaction_id" in value), "attribution route pair is incomplete")
            for key in ("obligation_id", "route_transaction_id"):
                if key in value: _route_text(value[key], "attribution " + key)
        elif status == "HOLON_STAGE_RECORDED":
            _route_closed(value, common + " binding_generation receipt", label="stage recording result")
            _route_generation(value["binding_generation"], "stage result binding")
            _route_stage(value["receipt"], True)
            _route_stage_compatibility(value["receipt"], omissions)
            _route_require(value["receipt"]["binding_generation"] == value["binding_generation"], "stage result generation differs")
            _route_record(records, "host-binding", [value["receipt"]["receipt_identity"]], "HostStageReceipt", value["receipt"], "record_holon_stage:825-877", "EVIDENCE")
        else: raise ValueError("unsupported host-binding result status")
        if status not in {"UNBOUND", "UNAVAILABLE"}: _route_constants(value, {"host_activation_proven": False, "proof_layers": _route_proof_layers}, "host result")
        _route_record(records, "host-binding", ["result", status, _route_digest(value)], "HostBindingResult", value, "lookup/validate_event:586-652")
    elif schema == "implementaudit.host-holon-stage-receipt.v1":
        _route_stage(value, True)
        _route_stage_compatibility(value, omissions)
        _route_record(records, "host-binding", [value["receipt_identity"]], "HostStageReceipt", value, "record_holon_stage:825-877", "EVIDENCE")
    else: raise ValueError("unsupported host-binding schema")
    _route_omission(omissions, "Host attribution/activation and general sensor payload are unverified; no event/resource/result-class fields are invented")


def decode_route_capture(kind, value):
    """Decode explicit captured data only; never establish owner truth or effects."""
    _route_require(kind in CAPTURE_ROUTE_KINDS, "unsupported route capture kind")
    value = _route_checked_json(value)
    _route_require(type(value) is dict, "captured owner envelope is not an object")
    records, omissions = [], []
    try:
        if kind == "pending": _route_pending(value, records, omissions)
        elif kind == "pending-decision": _route_pending_decision(value, records, omissions)
        elif kind == "route": _route_record_value(value, records, omissions)
        elif kind == "route-result": _route_result(value, records, omissions)
        else: _route_host(value, records, omissions)
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError("malformed captured " + kind + " structure") from exc
    keys = [row["key"] for row in records]
    _route_require(len(keys) == len(set(keys)), "captured projection has duplicate row identities")
    for row in records:
        if "source_key" in row:
            _route_require(row["source_key"] in keys and row["target_key"] in keys, "captured relation endpoint is absent")
    # Stable order is for derived rows only; native arrays/strings remain untouched.
    records.sort(key=lambda row: row["key"])
    unique = {_route_canonical(row): row for row in omissions}
    return {"records": records, "omissions": [unique[key] for key in sorted(unique)]}


"""Pure captured R0038 owner-format projections; no native reads or authority.

The caller binds capture-file bytes and wraps every row UNVERIFIED with no
establishes claims. These functions check supplied structure and relations;
they never authenticate physical source, select a native event, or grant JOIN.
"""
import copy as _occurrence_copy
import datetime as _occurrence_datetime
import hashlib as _occurrence_hashlib
import json as _occurrence_json
import pathlib as _occurrence_pathlib
import re as _occurrence_re


CAPTURE_OCCURRENCE_KINDS = ('result-occurrence', 'member-coverage', 'child-visibility')
_occurrence_commit = 'fa14948894f583cc0b4e3be80e9283839c9992b5'
OCCURRENCE_FORMAT_SOURCES = {
    'result-occurrence': [{'path': 'skills/implementaudit/scripts/compaction-result-observation.py', # source repo
        'commit': _occurrence_commit, 'blob': '9d6a6e5c3a4d9e370f69576a7dbff12a2d3bb73d',
        'sha256': '0ff4589848b4bb37ebe0a4eaf33da8dc5956074b016d50046382ad7814287604'}],
    'member-coverage': [{'path': 'skills/implementaudit/scripts/compile-work-graph.py', # source repo
        'commit': _occurrence_commit, 'blob': '3d18c445e5d41e80c515c9251da2260af8c53947',
        'sha256': '37c5d68830e9f2d0034ada3f661de7b48393c8ab265f611ef5412e8f41ffba8f'},
        {'path': 'scripts/check-auto-loom-coverage.py', 'commit': _occurrence_commit, # source repo
        'blob': '2ab7671676a7a39d5092d6cf85a244fd608818c6',
        'sha256': '3607a7a7b78848017ccf5adc4f4940cafdda55bbc51e723226482f2e15cebe02'}],
    'child-visibility': [dict(_route_route_source),
        dict(_route_binding_source),
        {'path': 'skills/implementaudit/references/child-agents.md', 'commit': _occurrence_commit,
        'blob': '97b0c03a5c7ff3a90178522f85d44083819df21b',
        'sha256': '1362ec8c9236b931177035e7ff859fb921d0a5a4159c2dd6666a5d6217f8fd58'}],
}
_occurrence_limit = 2 * 1024 * 1024
_occurrence_stages = ('OPEN', 'LOAD', 'USE', 'RETURN', 'DISPOSE', 'RECONCILE')
_occurrence_roles = ('audit-state', 'audit-assess', 'audit-implement', 'audit-andon')


def _occurrence_require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _occurrence_canonical(value):
    return _route_canonical(value)


def _occurrence_sha(value):
    return _occurrence_hashlib.sha256(_occurrence_canonical(value)).hexdigest()


def _occurrence_host_stage_sha(value):
    # H0 emits receipt identities with json.dumps' default ASCII escaping.
    # RT's resolved-record validator uses its different UTF-8 digest_json.
    raw = _route_canonical(value, True)
    return _occurrence_hashlib.sha256(raw).hexdigest()


def _occurrence_shape(value, keys, reason, closed=True):
    expected = set(keys.split())
    _occurrence_require(type(value) is dict and (set(value) == expected if closed else expected <= set(value)), reason)
    return value


def _occurrence_text(value):
    return type(value) is str and bool(value.strip()) and len(value.encode('utf-8')) <= 4096 and not any(ord(c) < 32 for c in value)


def _occurrence_hash(value, prefixed=False):
    return type(value) is str and _occurrence_re.fullmatch(('sha256:' if prefixed else '') + '[0-9a-f]{64}', value) is not None


def _occurrence_scalar(value, active=None, depth=0):
    active = set() if active is None else active
    _occurrence_require(depth <= 48, 'CAPTURE_DEPTH_BOUND')
    if type(value) in (dict, list):
        _occurrence_require(id(value) not in active, 'CAPTURE_CYCLE')
        active.add(id(value))
        if type(value) is dict:
            _occurrence_require(all(type(k) is str for k in value), 'CAPTURE_SCALAR')
            for key in value:
                _occurrence_scalar(key, active, depth + 1)
        for part in (value.values() if type(value) is dict else value):
            _occurrence_scalar(part, active, depth + 1)
        active.remove(id(value))
    else:
        _occurrence_require(value is None or type(value) in (str, int, bool), 'CAPTURE_SCALAR')
        if type(value) is str:
            try:
                value.encode('utf-8')
            except UnicodeError as exc:
                raise ValueError('CAPTURE_SCALAR') from exc


def _occurrence_row(out, key, family, record_type, observation, anchor):
    row = {'key': key, 'family': family, 'record_type': record_type,
           'observation': observation, 'source_anchor': anchor}
    out['records'].append(row)
    return key


def _occurrence_relation(out, relation, source, target, anchor):
    _occurrence_row(out, ['relation', relation, source, target], 'EXECUTION', 'Relation',
                    {'relation': relation}, anchor)
    out['records'][-1].update(relation_type=relation, source_key=source, target_key=target)


def _occurrence_omit(out, reason, family='EXECUTION', **fields):
    out['omissions'].append({'family': family, 'reason': reason, **fields})


def _occurrence_scope(value):
    _occurrence_require(type(value) is list and 0 < len(value) <= 64, 'BOUNDARY_SCOPE')
    seen = set()
    for item in value:
        _occurrence_shape(item, 'id version kind', 'BOUNDARY_SCOPE')
        _occurrence_require(_occurrence_text(item['id']) and _occurrence_text(item['kind']) and
                            type(item['version']) is int and item['version'] > 0 and item['id'] not in seen, 'BOUNDARY_SCOPE')
        seen.add(item['id'])


def _occurrence_artifact(pin):
    _occurrence_shape(pin, 'path bytes sha256', 'ARTIFACT_PIN')
    _occurrence_require(_occurrence_text(pin['path']) and type(pin['bytes']) is int and
                        0 < pin['bytes'] <= _occurrence_limit and _occurrence_hash(pin['sha256']), 'ARTIFACT_PIN')


def _occurrence_physical(value):
    _occurrence_shape(value, 'device inode', 'PHYSICAL_IDENTITY')
    _occurrence_require(all(type(v) is int and v >= 0 for v in value.values()), 'PHYSICAL_IDENTITY')


def _occurrence_locator(value):
    _occurrence_shape(value, 'offset bytes sha256 embedded_ordinal physical_line', 'RECORD_LOCATOR')
    _occurrence_require(type(value['offset']) is int and value['offset'] >= 0 and
                        type(value['bytes']) is int and 0 < value['bytes'] <= 262144 and
                        _occurrence_hash(value['sha256']) and type(value['embedded_ordinal']) is int and
                        value['embedded_ordinal'] >= 0 and (value['physical_line'] is None or
                        type(value['physical_line']) is int and value['physical_line'] > 0), 'RECORD_LOCATOR')


def _occurrence_pin(pin, sources=None):
    _occurrence_shape(pin, 'path physical role locator timestamp message_or_call_id', 'SOURCE_OCCURRENCE')
    _occurrence_locator(pin['locator'])
    _occurrence_physical(pin['physical'])
    _occurrence_require(_occurrence_text(pin['path']) and pin['role'] in ('parent', 'child') and _occurrence_text(pin['timestamp']) and
                        (pin['message_or_call_id'] is None or _occurrence_text(pin['message_or_call_id'])), 'SOURCE_OCCURRENCE')
    if sources is None:
        return
    source = sources[pin['role']]
    _occurrence_require(pin['path'] == source['path'] and pin['physical'] == source['physical'], 'SOURCE_OCCURRENCE_BINDING')
    start, end = pin['locator']['offset'], pin['locator']['offset'] + pin['locator']['bytes']
    _occurrence_require(any(w['offset'] <= start and end <= w['offset'] + w['bytes'] for w in source['allowed_ranges']),
                        'SOURCE_OCCURRENCE_OUTSIDE_ALLOWED_RANGE')
    if pin['role'] == 'child':
        _occurrence_require(pin['locator']['embedded_ordinal'] >= source['history_start_ordinal'], 'INHERITED_CHILD_OCCURRENCE')


def _occurrence_before(first, second):
    try:
        earlier = _occurrence_datetime.datetime.fromisoformat(first['timestamp'].replace('Z', '+00:00'))
        later = _occurrence_datetime.datetime.fromisoformat(second['timestamp'].replace('Z', '+00:00'))
        _occurrence_require(earlier < later, 'OCCURRENCE_ORDER')
    except (ValueError, TypeError) as exc:
        raise ValueError('OCCURRENCE_ORDER') from exc
    if first['path'] == second['path']:
        _occurrence_require(first['locator']['offset'] + first['locator']['bytes'] <= second['locator']['offset'], 'OCCURRENCE_ORDER')


def _occurrence_parent_child(parent, child):
    _occurrence_shape(parent, 'thread_id agent_path', 'PARENT_IDENTITY')
    _occurrence_shape(child, 'thread_id parent_thread_id agent_path', 'CHILD_IDENTITY')
    _occurrence_require(all(_occurrence_text(v) for v in (*parent.values(), *child.values())) and parent['agent_path'] == '/root' and
                        child['parent_thread_id'] == parent['thread_id'] and child['thread_id'] != parent['thread_id'] and
                        child['agent_path'].startswith('/root/'), 'PARENT_CHILD_BINDING')


def _occurrence_acceptance(value):
    _occurrence_shape(value, 'schema action parent_identity actual_child_identity obligation_digest observation_id '
        'child_observation_exchange_identity actual_result_digest accepted_boundary_versions observation_source_cutoff authority_ceiling',
        'ACCEPTANCE_SHAPE')
    _occurrence_require(value['schema'] == 'implementaudit.compaction-reconciliation-acceptance.v1' and
                        value['action'] == 'ACCEPT_BOUNDED_RECONCILIATION' and value['authority_ceiling'] == 'NONE', 'ACCEPTANCE_CEILING')
    for field in ('obligation_digest', 'observation_id', 'child_observation_exchange_identity', 'actual_result_digest'):
        _occurrence_require(_occurrence_hash(value[field]), 'ACCEPTANCE_IDENTITY')
    _occurrence_parent_child(value['parent_identity'], value['actual_child_identity'])
    _occurrence_scope(value['accepted_boundary_versions'])


def _occurrence_exchange(pair, sources=None):
    _occurrence_shape(pair, 'call result', 'EXACT_EXCHANGE_PAIR')
    for pin in pair.values():
        _occurrence_pin(pin, sources)
        _occurrence_require(pin['role'] == 'child', 'EXACT_CHILD_EXCHANGE')
    _occurrence_before(pair['call'], pair['result'])
    _occurrence_require(pair['call']['message_or_call_id'] == pair['result']['message_or_call_id'] and
                        _occurrence_text(pair['call']['message_or_call_id']), 'CALL_RESULT_ASSOCIATION')


def _occurrence_result_acceptance(r, a=None, sources=None):
    """CRO actual_result/acceptance:758-855, from supplied R/A fields alone.

    Pending can retain R before A, C, Q or E exists. Full C/E source context
    adds its allowed-range/history checks; its absence removes no structural,
    member-closure, original-exchange, local-source or delivery-order check.
    Raw file and record pins remain unauthenticated; no locator is opened.
    """
    _occurrence_shape(r, 'obligation_digest observation_id child_observation_exchange_identity scope result_pin '
        'result_physical members child_final parent_delivery bound_exchange use authorization_record hold_history', 'RESULT_IDENTITY_SHAPE')
    for field in ('obligation_digest', 'observation_id', 'child_observation_exchange_identity'):
        _occurrence_require(_occurrence_hash(r[field]), 'RESULT_IDENTITY')
    _occurrence_scope(r['scope'])
    _occurrence_artifact(r['result_pin']); _occurrence_physical(r['result_physical'])
    _occurrence_require(r['result_pin']['bytes'] <= 1048576, 'RESULT_ARTIFACT_BYTE_BOUND')
    _occurrence_require(type(r['members']) is list and 0 < len(r['members']) <= 32, 'RESULT_MEMBER_CLOSURE')
    # Check only the captured path relation, with its source spelling intact.
    # Physical alias/reparse checks still require unavailable native bytes.
    path_type = (_occurrence_pathlib.PureWindowsPath if
                 _occurrence_pathlib.PureWindowsPath(r['result_pin']['path']).is_absolute()
                 else _occurrence_pathlib.PurePosixPath)
    result_path = path_type(r['result_pin']['path'])
    _occurrence_require(result_path.is_absolute() and '..' not in result_path.parts, 'FOREIGN_RESULT_MEMBER')
    member_paths, member_physical = {result_path}, {_occurrence_canonical(r['result_physical'])}
    total = r['result_pin']['bytes']
    for member in r['members']:
        _occurrence_shape(member, 'pin physical', 'RESULT_MEMBER_SHAPE')
        _occurrence_artifact(member['pin']); _occurrence_physical(member['physical'])
        _occurrence_require(member['pin']['bytes'] <= 1048576, 'RESULT_ARTIFACT_BYTE_BOUND')
        loc = _occurrence_canonical(member['physical'])
        member_path = path_type(member['pin']['path'])
        _occurrence_require(member_path.is_absolute() and '..' not in member_path.parts and
                            member_path.is_relative_to(result_path.parent), 'FOREIGN_RESULT_MEMBER')
        _occurrence_require(member_path not in member_paths and loc not in member_physical, 'DUPLICATE_RESULT_MEMBER')
        member_paths.add(member_path); member_physical.add(loc); total += member['pin']['bytes']
    _occurrence_require(total <= _occurrence_limit, 'RESULT_CLOSURE_BYTE_BOUND')
    held = _occurrence_shape(r['hold_history'], 'path physical prefix_bytes prefix_sha256 physical_records history_start_ordinal '
        'host_producer_authenticated original_bind', 'HOLD_PREFIX_SHAPE')
    _occurrence_physical(held['physical'])
    _occurrence_require(held['host_producer_authenticated'] is False and _occurrence_text(held['path']) and
                        _occurrence_hash(held['prefix_sha256']) and type(held['prefix_bytes']) is int and
                        0 < held['prefix_bytes'] <= _occurrence_limit and type(held['physical_records']) is int and
                        0 < held['physical_records'] <= 64 and type(held['history_start_ordinal']) is int and
                        held['history_start_ordinal'] >= 0, 'HOLD_PREFIX_BINDING')
    if sources is not None:
        _occurrence_require(held['path'] == sources['child']['path'] and held['physical'] == sources['child']['physical'] and
                            held['history_start_ordinal'] == sources['child']['history_start_ordinal'], 'HOLD_PREFIX_BINDING')
    _occurrence_require(r['bound_exchange'] == held['original_bind'], 'BOUND_EXCHANGE_NOT_ORIGINAL')
    for pair in (r['bound_exchange'], r['use']):
        _occurrence_exchange(pair, sources)
    original = r['bound_exchange']
    _occurrence_require(original['result']['locator']['offset'] + original['result']['locator']['bytes'] == held['prefix_bytes'],
                        'ORIGINAL_COMPLETION_OUTSIDE_CUTOFF')
    for pin in (r['child_final'], r['parent_delivery'], r['authorization_record']):
        _occurrence_pin(pin, sources)
    _occurrence_require(r['child_final']['role'] == 'child' and all(p['role'] == 'parent' for p in
                        (r['parent_delivery'], r['authorization_record'])), 'RETURN_PARENT_ROLE')
    # resolve_record takes every role's pins from one context source. R itself
    # retains enough path/physical/history operands to check that local binding.
    for pin in (*original.values(), *r['use'].values(), r['child_final']):
        _occurrence_require(pin['path'] == held['path'] and pin['physical'] == held['physical'] and
                            pin['locator']['embedded_ordinal'] >= held['history_start_ordinal'], 'SOURCE_OCCURRENCE_BINDING')
    parent = r['parent_delivery']
    _occurrence_require(r['authorization_record']['path'] == parent['path'] and
                        r['authorization_record']['physical'] == parent['physical'], 'SOURCE_OCCURRENCE_BINDING')
    for first, second in ((original['result'], r['use']['call']), (r['use']['result'], r['child_final']),
                          (r['child_final'], parent)):
        _occurrence_before(first, second)
    if a is not None:
        _occurrence_shape(a, 'record value', 'ACCEPTANCE_RECORD_SHAPE')
        _occurrence_acceptance(a['value']); _occurrence_pin(a['record'], sources)
        _occurrence_require(a['record']['role'] == 'parent', 'RETURN_PARENT_ROLE')
        _occurrence_require(a['record']['path'] == parent['path'] and a['record']['physical'] == parent['physical'],
                            'SOURCE_OCCURRENCE_BINDING')
        _occurrence_before(parent, a['record'])
        av = a['value']
        _occurrence_require(r['scope'] == av['accepted_boundary_versions'], 'RESULT_OR_ACCEPTANCE_SCOPE')
        _occurrence_require(all(r[k] == av[k] for k in
                            ('obligation_digest', 'observation_id', 'child_observation_exchange_identity')), 'RESULT_ACCEPTANCE_BINDING')
        _occurrence_require(av['actual_result_digest'] == _occurrence_sha(r), 'RESULT_ACCEPTANCE_DIGEST')
        if sources is not None:
            _occurrence_require(av['observation_source_cutoff'] == sources['compaction_cutoff'], 'RESULT_OR_ACCEPTANCE_SCOPE')


def _occurrence_result(value, out):
    schema = value.get('schema')
    if schema == 'implementaudit.compaction-reconciliation-result.v1':
        _occurrence_shape(value, 'schema obligation_digest observation_id child_observation_exchange_identity '
            'exact_observed_boundary_versions code_and_skill_pins status currentness measured_epoch frontier members authority_ceiling', 'RESULT_SHAPE')
        for field in ('obligation_digest', 'observation_id', 'child_observation_exchange_identity'):
            _occurrence_require(_occurrence_hash(value[field]), 'RESULT_IDENTITY')
        _occurrence_scope(value['exact_observed_boundary_versions'])
        _occurrence_require(value['status'] in ('SUCCEEDED', 'FAILED') and value['currentness'] in ('VERIFIED', 'UNRESOLVED') and
                            value['measured_epoch'] in ('VERIFIED', 'UNRESOLVED') and value['authority_ceiling'] == 'NONE' and
                            type(value['frontier']) is str and 0 < len(value['frontier']) <= 1024 and
                            type(value['code_and_skill_pins']) is dict, 'RESULT_FIELDS')
        members = value['members']
        _occurrence_require(type(members) is list and 0 < len(members) <= 32, 'RESULT_MEMBER_CLOSURE')
        for member in members:
            _occurrence_artifact(member)
            _occurrence_require(member['bytes'] <= 1048576, 'RESULT_ARTIFACT_BYTE_BOUND')
        _occurrence_require(len({m['path'] for m in members}) == len(members), 'DUPLICATE_RESULT_MEMBER')
        root = _occurrence_row(out, [schema, value['observation_id']], 'EVIDENCE', 'EvidenceRecord', value, '$')
        for member in members:
            key = _occurrence_row(out, ['artifact', member], 'EVIDENCE', 'Artifact', member, '$.members')
            _occurrence_relation(out, 'HAS_MEMBER', root, key, '$.members')
        _occurrence_omit(out, 'ORIGINAL_OCCURRENCE_AND_ACCEPTANCE_NOT_IN_RESULT_ARTIFACT')
        return
    if schema == 'implementaudit.compaction-reconciliation-acceptance.v1':
        _occurrence_acceptance(value)
        _occurrence_row(out, [schema, value['observation_id'], value['actual_result_digest']], 'EVIDENCE', 'Receipt', value, '$')
        _occurrence_omit(out, 'ACTUAL_ACCEPTING_PARENT_SOURCE_NOT_IN_CAPTURE')
        return
    episode_value = schema is None and 'Q_digest' in value
    if episode_value:
        # CRO episode_value:983-989 deliberately has no schema or producer
        # environment fields. Reuse its retained C fields without inventing them.
        _occurrence_shape(value, 'policy_digest parent_identity actual_child_identity assignment_identity obligation_digest '
            'observation_id covered_boundary_versions O_U_exchange_USE_R_A_identities physical_source_and_cutoff_identities '
            'exact_result_digest exact_acceptance_digest authority_ceiling Q_digest actual_acquisition_and_custody_validation_evidence',
            'EPISODE_VALUE_SHAPE')
        _occurrence_require(_occurrence_hash(value['Q_digest']) and value['authority_ceiling'] == 'NONE', 'EPISODE_VALUE_CEILING')
        acquired = _occurrence_shape(value['actual_acquisition_and_custody_validation_evidence'], 'candidate', 'EPISODE_CANDIDATE_PIN')
        pin = _occurrence_shape(acquired['candidate'], 'path bytes sha256', 'EPISODE_CANDIDATE_PIN')
        # custody_record uses MAX_TOTAL, independently of the 1 MiB default
        # artifact_preflight bound on result/member/obligation bytes.
        _occurrence_require(_occurrence_text(pin['path']) and type(pin['bytes']) is int and
                            0 < pin['bytes'] <= 2 * 1024 * 1024 and _occurrence_hash(pin['sha256']), 'EPISODE_CANDIDATE_PIN')
        schema = 'episode_value'  # Derived row key discriminator only; raw value is unchanged.
    else:
        _occurrence_shape(value, 'schema policy_digest producer_environment_identity parent_identity actual_child_identity '
            'assignment_identity obligation_digest observation_id covered_boundary_versions O_U_exchange_USE_R_A_identities '
            'physical_source_and_cutoff_identities exact_result_digest exact_acceptance_digest source_origin_validation '
            'host_producer_authenticated authority_ceiling', 'ACQUISITION_SHAPE')
        _occurrence_require(schema == 'implementaudit.compaction-unconsumed-acquisition.v1', 'KNOWN_RESULT_OCCURRENCE_FORMAT')
        _occurrence_require(value['source_origin_validation'] == 'UNESTABLISHED' and value['host_producer_authenticated'] is False and
                            value['authority_ceiling'] == 'NONE', 'ACQUISITION_CEILING')
    for field in ('policy_digest', 'assignment_identity', 'obligation_digest', 'observation_id', 'exact_result_digest', 'exact_acceptance_digest'):
        _occurrence_require(_occurrence_hash(value[field]), 'ACQUISITION_IDENTITY')
    _occurrence_scope(value['covered_boundary_versions'])
    parent, child = value['parent_identity'], value['actual_child_identity']
    _occurrence_parent_child(parent, child)
    sources = value['physical_source_and_cutoff_identities']
    _occurrence_shape(sources, 'parent child compaction_cutoff records', 'ACQUISITION_SOURCE_SHAPE')
    for role in ('parent', 'child'):
        source = _occurrence_shape(sources[role], 'path metadata allowed_ranges physical metadata_payload_digest history_start_ordinal', 'SOURCE_CONTEXT')
        _occurrence_locator(source['metadata']); _occurrence_physical(source['physical'])
        _occurrence_require(_occurrence_text(source['path']) and source['metadata']['offset'] == 0 and
                            _occurrence_hash(source['metadata_payload_digest']) and type(source['history_start_ordinal']) is int and
                            source['history_start_ordinal'] >= 0 and type(source['allowed_ranges']) is list and
                            0 < len(source['allowed_ranges']) <= 64, 'SOURCE_CONTEXT')
        for window in source['allowed_ranges']:
            _occurrence_shape(window, 'offset bytes', 'SOURCE_RANGE')
            _occurrence_require(type(window['offset']) is int and window['offset'] >= 0 and type(window['bytes']) is int and
                                0 < window['bytes'] <= _occurrence_limit, 'SOURCE_RANGE')
    if not episode_value:
        env = _occurrence_shape(value['producer_environment_identity'], 'profile_id parent_metadata child_metadata', 'PRODUCER_FORMAT')
        _occurrence_require(env['profile_id'] == 'codex-desktop-0.153.4-collaboration-public-v1' and
                            all(env[role + '_metadata'] == sources[role]['metadata_payload_digest'] for role in ('parent', 'child')),
                            'PRODUCER_FORMAT_BINDING')
    pins = sources['records']
    _occurrence_require(type(pins) is list and 0 < len(pins) <= 64, 'PHYSICAL_RECORD_POPULATION')
    selected, physical = set(), {}
    for pin in pins:
        _occurrence_pin(pin, sources)
        location = _occurrence_canonical([pin['path'], pin['physical'], pin['locator']['offset']])
        full_pin = _occurrence_canonical(pin)
        _occurrence_require(full_pin not in selected, 'DUPLICATE_PHYSICAL_OCCURRENCE')
        selected.add(full_pin)
        # CRO deduplicates full pins; optional physical_line labels can differ
        # for the same physical bytes. Preserve every pin without multiplying
        # the occurrence. All intrinsic source facts must still agree.
        intrinsic = {**pin, 'locator': {k: v for k, v in pin['locator'].items() if k != 'physical_line'}}
        if location in physical:
            _occurrence_require(physical[location]['physical_occurrence'] == intrinsic, 'CONFLICTING_PHYSICAL_OCCURRENCE')
            physical[location]['captured_pins'].append(pin)
        else:
            physical[location] = {'physical_occurrence': intrinsic, 'captured_pins': [pin]}
    values = _occurrence_shape(value['O_U_exchange_USE_R_A_identities'], 'O U exchange USE R A', 'EXCHANGE_POPULATION')
    _occurrence_artifact(values['O'])
    # CRO delivery_packet:280-286 uses artifact(O)'s default 1 MiB bound.
    # Custody candidate/Q/E pins retain their independent 2 MiB bound.
    _occurrence_require(values['O']['bytes'] <= 1048576, 'OBLIGATION_ARTIFACT_BYTE_BOUND')
    r, a = values['R'], values['A']
    _occurrence_require(a is not None, 'ACCEPTANCE_RECORD_SHAPE')
    _occurrence_result_acceptance(r, a, sources)
    _occurrence_exchange(values['exchange'], sources)
    original = r['bound_exchange']
    _occurrence_require(r['use'] == values['USE'] and r['authorization_record'] == values['U'], 'EXCHANGE_IDENTITY')
    _occurrence_before(values['exchange']['result'], original['call'])
    def references(item):
        if type(item) is dict:
            if set(item) == {'path', 'physical', 'role', 'locator', 'timestamp', 'message_or_call_id'}:
                _occurrence_require(_occurrence_canonical(item) in selected, 'REFERENCED_OCCURRENCE_OMITTED')
            else:
                for nested in item.values(): references(nested)
        elif type(item) is list:
            for nested in item: references(nested)
    references(values)
    av = a['value']
    _occurrence_require(value['covered_boundary_versions'] == r['scope'], 'RESULT_OR_ACCEPTANCE_SCOPE')
    _occurrence_require(value['obligation_digest'] == values['O']['sha256'] == r['obligation_digest'] and
                        value['observation_id'] == r['observation_id'] and av['parent_identity'] == parent and
                        av['actual_child_identity'] == child, 'RESULT_ACCEPTANCE_BINDING')
    _occurrence_require(value['exact_result_digest'] == _occurrence_sha(r) and
                        value['exact_acceptance_digest'] == _occurrence_sha(a), 'RESULT_ACCEPTANCE_DIGEST')
    root = _occurrence_row(out, [schema, value['observation_id'], value['exact_result_digest']], 'EVIDENCE', 'EvidenceRecord', value, '$')
    result_key = _occurrence_row(out, ['result', value['exact_result_digest']], 'EVIDENCE', 'EvidenceRecord', r, '$.O_U_exchange_USE_R_A_identities.R')
    _occurrence_relation(out, 'HAS_RESULT', root, result_key, '$.O_U_exchange_USE_R_A_identities.R')
    for occurrence in physical.values():
        key = _occurrence_row(out, ['physical-occurrence', occurrence['physical_occurrence']], 'EVIDENCE',
                              'SourceOccurrence', occurrence, '$.physical_source_and_cutoff_identities.records')
        if any(pin in original.values() for pin in occurrence['captured_pins']):
            _occurrence_relation(out, 'SELECTS_ORIGINAL_OCCURRENCE', result_key, key, '$.O_U_exchange_USE_R_A_identities.R.bound_exchange')
        if len(occurrence['captured_pins']) > 1:
            _occurrence_omit(out, 'CORRELATED_SOURCE_PIN_LABELS_NOT_INDEPENDENT', 'EVIDENCE',
                             source_anchor='$.physical_source_and_cutoff_identities.records', occurrence_key=key)
    for member in r['members']:
        key = _occurrence_row(out, ['artifact', member], 'EVIDENCE', 'Artifact', member, '$.O_U_exchange_USE_R_A_identities.R.members')
        _occurrence_relation(out, 'HAS_MEMBER', result_key, key, '$.O_U_exchange_USE_R_A_identities.R.members')
    _occurrence_omit(out, 'PRIOR_RETRY_CLASSIFICATION_NOT_EXPORTED')
    _occurrence_omit(out, 'PHYSICAL_SOURCE_AND_MEMBER_BYTES_NOT_READ', 'EVIDENCE')


def _occurrence_strings(value, reason):
    _occurrence_require(type(value) is list and all(_occurrence_text(x) for x in value) and len(set(value)) == len(value), reason)
    return value


# Pure supplied-data checks from pinned compile-work-graph.py. This snippet uses
# the existing _occurrence_ utilities and never resolves paths, refs or authority.
_occurrence_preparation_kinds = frozenset((
    'BRIEF', 'RECONNAISSANCE', 'RED_DESIGN', 'FIXTURE_DESIGN',
    'ACCEPTANCE_PLAN', 'REVIEW_PLAN', 'DISPOSABLE_PROTOTYPE'))
_occurrence_preparation_forbidden = frozenset((
    'SOURCE_MUTATION', 'GRAPH_MUTATION', 'LIFECYCLE_CREDIT', 'REF_MUTATION',
    'PACKAGE_INSTALL_PUBLICATION', 'EXTERNAL_EFFECT'))
_occurrence_product_dispositions = frozenset((
    'CONSUMED', 'COMPOSED', 'INTEGRATED', 'SUPERSEDED', 'REJECTED',
    'EXPLICITLY_DEFERRED_TO_NAMED_JOIN'))


def _occurrence_work_commit(value):
    return type(value) is str and _occurrence_re.fullmatch(r'[0-9a-f]{40}', value) is not None


def _occurrence_work_receipt(value):
    # WG defines literal receipt syntax, not H0's generation-currentness rule.
    return type(value) is str and _occurrence_re.fullmatch(
        r'refs/implementaudit/continuity-receipts/[^/@]+/G[0-9A-F]{4}@[0-9a-f]{40}', value) is not None


def _occurrence_preparation_list(value, reason):
    _occurrence_strings(value, reason)
    _occurrence_require(bool(value), reason)
    return value


def _occurrence_work_product_result(value):
    _occurrence_shape(value, 'product disposition', 'WORK_PRODUCT_RESULT')
    product = _occurrence_shape(value['product'], 'commit tree review_sha256', 'WORK_PRODUCT_IDENTITY')
    _occurrence_require(_occurrence_work_commit(product['commit']) and _occurrence_work_commit(product['tree']) and
                        _occurrence_hash(product['review_sha256']), 'WORK_PRODUCT_IDENTITY')
    disposition = _occurrence_shape(value['disposition'], 'kind target', 'WORK_PRODUCT_DISPOSITION')
    _occurrence_require(_occurrence_text(disposition['kind']) and disposition['kind'] in _occurrence_product_dispositions and
                        _occurrence_text(disposition['target']), 'WORK_PRODUCT_DISPOSITION')
    return value


def _occurrence_work_product_source(source):
    _occurrence_shape(source, 'kind path bytes sha256 receipt', 'WORK_PRODUCT_AUTHORITY_SOURCE')
    _occurrence_require(source['kind'] == 'GOVERNOR_VERIFIED_PRODUCT_BINDINGS' and _occurrence_text(source['path']) and
                        type(source['bytes']) is int and source['bytes'] > 0 and _occurrence_hash(source['sha256']) and
                        _occurrence_work_receipt(source['receipt']), 'WORK_PRODUCT_AUTHORITY_SOURCE')
    return source


def _occurrence_work_product_observations(graph, cells, local, out,
                                          by_owner=None, by_disposition=None, authorizations=None):
    """Compare supplied realised products/proposals; never compute a frontier.

    Pinned WG compile_product_frontier_v1 owns these record predicates. Missing
    comparison inputs stay omissions, independently of the absent authority bytes.
    """
    topology = graph.get('integration_topology')
    topology = topology if type(topology) is dict else {}
    realised = {}
    for cell_id, result in local.items():
        commit = result['product']['commit']
        _occurrence_require(commit not in realised, 'WORK_PRODUCT_RUNTIME_IDENTITY')
        realised[commit] = (result, ['work-product', cell_id])
    if 'qualified_products' in topology:
        noncells = topology['qualified_products']
        _occurrence_require(type(noncells) is list, 'WORK_PRODUCT_NONCELL')
        owners = set()
        for index, entry in enumerate(noncells):
            _occurrence_shape(entry, 'owner result', 'WORK_PRODUCT_NONCELL')
            owner = entry['owner']
            _occurrence_require(_occurrence_text(owner) and owner not in owners, 'WORK_PRODUCT_NONCELL_OWNER')
            owners.add(owner)
            result = _occurrence_work_product_result(entry['result'])
            anchor = '$.integration_topology.qualified_products[' + str(index) + ']'
            if by_owner is None:
                _occurrence_omit(out, 'NON_CELL_PRODUCT_BINDINGS_NOT_CAPTURED', 'EVIDENCE', source_anchor=anchor, owner=owner)
            else:
                binding = by_owner.get(('NON_CELL', owner))
                _occurrence_require(binding is not None and result['product'] ==
                                    {k: binding[k] for k in ('commit', 'tree', 'review_sha256')}, 'WORK_PRODUCT_NONCELL_BINDING')
                disposition = by_disposition[binding['commit']]
                _occurrence_require(result['disposition'] == {k: disposition[k] for k in ('kind', 'target')},
                                    'WORK_PRODUCT_NONCELL_DISPOSITION')
            commit = result['product']['commit']
            _occurrence_require(commit not in realised, 'WORK_PRODUCT_RUNTIME_IDENTITY')
            key = _occurrence_row(out, ['work-product', 'NON_CELL', owner], 'EVIDENCE', 'WorkNonCellProduct', entry, anchor)
            realised[commit] = (result, key)
    expected_noncells = {owner for kind, owner in by_owner if kind == 'NON_CELL'} if by_owner is not None else set()
    complete = by_owner is not None and ('qualified_products' in topology or not expected_noncells)
    if complete:
        expected_commits = {binding['commit'] for binding in by_owner.values()}
        _occurrence_require(bool(realised) and set(realised) == expected_commits, 'WORK_PRODUCT_RUNTIME_CENSUS')
    elif expected_noncells:
        _occurrence_omit(out, 'PRODUCT_NONCELL_REALISATIONS_NOT_CAPTURED', 'EVIDENCE',
                         source_anchor='$.integration_topology.qualified_products', owners=sorted(expected_noncells))
    elif realised:
        _occurrence_omit(out, 'PRODUCT_RUNTIME_BINDING_CENSUS_NOT_CAPTURED', 'EVIDENCE', source_anchor='$.integration_topology.product_contract')
    heads = None
    if 'integration_heads' in topology:
        declared = _occurrence_preparation_list(topology['integration_heads'], 'WORK_PRODUCT_INTEGRATION_HEAD')
        _occurrence_require(all(_occurrence_work_commit(head) for head in declared), 'WORK_PRODUCT_INTEGRATION_HEAD')
        heads = set(declared)
        _occurrence_row(out, ['work-integration-heads'], 'EVIDENCE', 'IntegrationHeads',
                        {'integration_heads': declared}, '$.integration_topology.integration_heads')
    missing_heads = False
    for commit, (result, _) in realised.items():
        kind, target = result['disposition']['kind'], result['disposition']['target']
        if kind == 'INTEGRATED':
            if heads is None:
                missing_heads = True
            else:
                _occurrence_require(target in heads, 'WORK_PRODUCT_INTEGRATION_HEAD')
        if kind == 'SUPERSEDED':
            _occurrence_require(target != commit, 'WORK_PRODUCT_SELF_SUPERSESSION')
        if kind in ('SUPERSEDED', 'REJECTED'):
            if complete:
                _occurrence_require(target in realised, 'WORK_PRODUCT_RUNTIME_TARGET')
            elif target not in realised:
                _occurrence_omit(out, 'PRODUCT_RUNTIME_TARGET_NOT_CAPTURED', 'EVIDENCE', product_commit=commit, target=target)
    if missing_heads:
        _occurrence_omit(out, 'PRODUCT_INTEGRATION_HEADS_NOT_CAPTURED', 'EVIDENCE', source_anchor='$.integration_topology.integration_heads')
    if 'composition_proposals' not in topology:
        return
    proposals = topology['composition_proposals']
    _occurrence_require(type(proposals) is list, 'WORK_PRODUCT_PROPOSAL')
    owners = set()
    authorised = {_occurrence_canonical(item) for item in authorizations} if authorizations is not None else None
    for index, proposal in enumerate(proposals):
        _occurrence_shape(proposal, 'owner products qualification_review_sha256 integration_authority', 'WORK_PRODUCT_PROPOSAL')
        owner = proposal['owner']
        _occurrence_require(_occurrence_text(owner) and owner in cells and owner not in owners, 'WORK_PRODUCT_PROPOSAL_OWNER')
        owners.add(owner)
        products = _occurrence_preparation_list(proposal['products'], 'WORK_PRODUCT_PROPOSAL_PRODUCTS')
        _occurrence_require(products == sorted(products) and all(_occurrence_work_commit(commit) for commit in products),
                            'WORK_PRODUCT_PROPOSAL_PRODUCTS')
        missing_products = []
        for commit in products:
            if commit in realised:
                _occurrence_require(realised[commit][0]['disposition']['kind'] not in ('SUPERSEDED', 'REJECTED'),
                                    'WORK_PRODUCT_PROPOSAL_PRODUCTS')
            elif complete:
                raise ValueError('WORK_PRODUCT_PROPOSAL_PRODUCTS')
            else:
                missing_products.append(commit)
        _occurrence_require(_occurrence_hash(proposal['qualification_review_sha256']) and
                            _occurrence_work_receipt(proposal['integration_authority']), 'WORK_PRODUCT_PROPOSAL_IDENTITY')
        anchor = '$.integration_topology.composition_proposals[' + str(index) + ']'
        if authorised is None:
            _occurrence_omit(out, 'COMPOSITION_AUTHORIZATION_INPUT_NOT_CAPTURED', 'EVIDENCE', source_anchor=anchor, owner=owner)
        else:
            _occurrence_require(_occurrence_canonical(proposal) in authorised, 'WORK_PRODUCT_PROPOSAL_AUTHORIZATION')
        if missing_products:
            _occurrence_omit(out, 'COMPOSITION_PRODUCT_REALISATION_NOT_CAPTURED', 'EVIDENCE', source_anchor=anchor, products=missing_products)
        cell = cells[owner]
        _occurrence_require(cell['state'] == 'READY' and all(cells[dep]['state'] == 'DONE' for dep in cell['deps']),
                            'WORK_PRODUCT_PROPOSAL_DEPENDENCIES')
        _occurrence_require(not any(member != owner and cells[member]['state'] == 'ACTIVE'
                            for members in graph['serialization_groups'].values() if owner in members for member in members),
                            'WORK_PRODUCT_PROPOSAL_HOLD')
        key = _occurrence_row(out, ['work-composition-proposal', owner], 'EXECUTION', 'CompositionProposal', proposal, anchor)
        _occurrence_relation(out, 'PROPOSED_BY', key, ['work-cell', owner], anchor)
        for commit in products:
            if commit in realised:
                _occurrence_relation(out, 'PROPOSES_PRODUCT', key, realised[commit][1], anchor)
        _occurrence_omit(out, 'PRODUCT_COMPOSITION_ACTIVATION_NOT_ESTABLISHED', source_anchor=anchor, owner=owner)


def _occurrence_work_products(graph, cells, out):
    """Check supplied product bindings without the external authority bytes.

    The owner also requires the exact source file bytes and receipt authority.
    Neither is obtained by checking these local shapes and equality relations.
    """
    local = {}
    for cell_id, cell in cells.items():
        if cell.get('source_bearing') is True:
            _occurrence_require(cell['state'] == 'DONE', 'WORK_PRODUCT_SOURCE_STATE')
            result = _occurrence_work_product_result(cell.get('result'))
            local[cell_id] = result
            product_key = _occurrence_row(out, ['work-product', cell_id], 'EVIDENCE', 'WorkProduct', result, '$.cells.result')
            _occurrence_relation(out, 'HAS_PRODUCT', ['work-cell', cell_id], product_key, '$.cells.result')
    topology = graph.get('integration_topology')
    topology = topology if type(topology) is dict else {}
    contract = topology.get('product_contract')
    authority = graph.get('authority')
    source = authority.get('qualified_product_contract') if type(authority) is dict else None
    signal = any('source_bearing' in cell for cell in cells.values()) or any(
        key in topology for key in ('qualified_products', 'composition_proposals')) or (
        type(authority) is dict and 'qualified_product_contract' in authority)
    if contract is None:
        if source is not None:
            _occurrence_work_product_source(source)
        if signal:
            _occurrence_omit(out, 'PRODUCT_AUTHORITY_INPUTS_NOT_CAPTURED', 'EVIDENCE', source_anchor='$.integration_topology.product_contract')
        _occurrence_work_product_observations(graph, cells, local, out)
        return
    _occurrence_shape(contract, 'authority_sha256 done_classification non_cell_owners join_owners product_bindings '
        'disposition_bindings composition_authorizations future_consumers', 'WORK_PRODUCT_CONTRACT')
    _occurrence_work_product_source(source)
    _occurrence_require(_occurrence_hash(contract['authority_sha256']) and contract['authority_sha256'] == _occurrence_sha(source),
                        'WORK_PRODUCT_AUTHORITY_BINDING')
    classification = contract['done_classification']
    done = {key for key, cell in cells.items() if cell['state'] == 'DONE'}
    _occurrence_require(type(classification) is dict and set(classification) == done, 'WORK_PRODUCT_CLASSIFICATION')
    for key in done:
        category = classification[key]
        _occurrence_require(category in ('SOURCE_PRODUCT', 'NON_SOURCE') and type(cells[key].get('source_bearing')) is bool and
                            cells[key]['source_bearing'] is (category == 'SOURCE_PRODUCT'), 'WORK_PRODUCT_CLASSIFICATION')
    for field in ('non_cell_owners', 'join_owners'):
        owners = _occurrence_strings(contract[field], 'WORK_PRODUCT_OWNERS')
        _occurrence_require(owners == sorted(owners), 'WORK_PRODUCT_OWNERS')
    _occurrence_require(all(owner in cells and cells[owner].get('class') == 'integration' for owner in contract['join_owners']),
                        'WORK_PRODUCT_JOIN_OWNER')
    bindings = contract['product_bindings']
    _occurrence_require(type(bindings) is list and bool(bindings), 'WORK_PRODUCT_BINDINGS')
    by_owner, by_commit = {}, {}
    for binding in bindings:
        _occurrence_shape(binding, 'owner_kind owner commit tree review_sha256', 'WORK_PRODUCT_BINDING')
        _occurrence_require(binding['owner_kind'] in ('CELL', 'NON_CELL') and _occurrence_text(binding['owner']) and
                            _occurrence_work_commit(binding['commit']) and _occurrence_work_commit(binding['tree']) and
                            _occurrence_hash(binding['review_sha256']), 'WORK_PRODUCT_BINDING')
        owner = (binding['owner_kind'], binding['owner'])
        _occurrence_require(owner not in by_owner and binding['commit'] not in by_commit, 'WORK_PRODUCT_BINDING_POPULATION')
        by_owner[owner], by_commit[binding['commit']] = binding, binding
    expected_owners = {('CELL', cell_id) for cell_id in local} | {('NON_CELL', owner) for owner in contract['non_cell_owners']}
    _occurrence_require(set(by_owner) == expected_owners, 'WORK_PRODUCT_BINDING_POPULATION')
    dispositions = contract['disposition_bindings']
    _occurrence_require(type(dispositions) is list and len(dispositions) == len(by_commit), 'WORK_PRODUCT_DISPOSITIONS')
    by_disposition = {}
    for disposition in dispositions:
        _occurrence_shape(disposition, 'product_commit kind target', 'WORK_PRODUCT_DISPOSITION')
        commit, kind, target = (disposition[k] for k in ('product_commit', 'kind', 'target'))
        _occurrence_require(_occurrence_work_commit(commit) and commit in by_commit and commit not in by_disposition and
                            _occurrence_text(kind) and kind in _occurrence_product_dispositions and _occurrence_text(target),
                            'WORK_PRODUCT_DISPOSITION')
        if kind == 'CONSUMED':
            _occurrence_require(target in cells, 'WORK_PRODUCT_DISPOSITION_TARGET')
        elif kind == 'COMPOSED':
            _occurrence_require(target in by_commit and target != commit, 'WORK_PRODUCT_DISPOSITION_TARGET')
        elif kind in ('SUPERSEDED', 'REJECTED'):
            _occurrence_require(target in by_commit, 'WORK_PRODUCT_DISPOSITION_TARGET')
        elif kind == 'EXPLICITLY_DEFERRED_TO_NAMED_JOIN':
            _occurrence_require(target in contract['join_owners'], 'WORK_PRODUCT_DISPOSITION_TARGET')
        else:
            _occurrence_require(_occurrence_work_commit(target), 'WORK_PRODUCT_DISPOSITION_TARGET')
        by_disposition[commit] = disposition
    visited = set()
    for commit in by_commit:
        path, cursor = set(), commit
        while cursor not in visited:
            _occurrence_require(cursor not in path, 'WORK_PRODUCT_COMPOSITION_CYCLE')
            path.add(cursor)
            disposition = by_disposition[cursor]
            if disposition['kind'] != 'COMPOSED':
                break
            cursor = disposition['target']
            _occurrence_require(by_disposition[cursor]['kind'] not in ('SUPERSEDED', 'REJECTED'), 'WORK_PRODUCT_COMPOSITION_CURRENTNESS')
        visited.update(path)
    for cell_id, result in local.items():
        binding = by_owner[('CELL', cell_id)]
        _occurrence_require(result['product'] == {k: binding[k] for k in ('commit', 'tree', 'review_sha256')} and
                            result['disposition'] == {k: by_disposition[binding['commit']][k] for k in ('kind', 'target')},
                            'WORK_PRODUCT_RESULT_BINDING')
    authorizations = contract['composition_authorizations']
    _occurrence_require(type(authorizations) is list, 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION')
    seen, reviews = set(), {binding['review_sha256'] for binding in bindings}
    for authorization in authorizations:
        _occurrence_shape(authorization, 'owner products qualification_review_sha256 integration_authority', 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION')
        products = _occurrence_preparation_list(authorization['products'], 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION')
        _occurrence_require(_occurrence_text(authorization['owner']) and authorization['owner'] in cells and products == sorted(products) and
                            all(_occurrence_work_commit(product) and product in by_commit for product in products) and
                            _occurrence_hash(authorization['qualification_review_sha256']) and authorization['qualification_review_sha256'] in reviews and
                            authorization['integration_authority'] == source['receipt'], 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION')
        identity = _occurrence_canonical(authorization)
        _occurrence_require(identity not in seen, 'WORK_PRODUCT_COMPOSITION_AUTHORIZATION'); seen.add(identity)
    consumers = contract['future_consumers']
    _occurrence_require(type(consumers) is list, 'WORK_PRODUCT_FUTURE_CONSUMER')
    seen = set()
    for consumer in consumers:
        _occurrence_shape(consumer, 'product_commit cell_id', 'WORK_PRODUCT_FUTURE_CONSUMER')
        _occurrence_require(_occurrence_work_commit(consumer['product_commit']) and consumer['product_commit'] in by_commit and
                            _occurrence_text(consumer['cell_id']) and consumer['cell_id'] in cells and
                            by_disposition[consumer['product_commit']]['kind'] not in ('SUPERSEDED', 'REJECTED'), 'WORK_PRODUCT_FUTURE_CONSUMER')
        identity = _occurrence_canonical(consumer)
        _occurrence_require(identity not in seen, 'WORK_PRODUCT_FUTURE_CONSUMER'); seen.add(identity)
    _occurrence_work_product_observations(graph, cells, local, out, by_owner, by_disposition, authorizations)
    contract_key = _occurrence_row(out, ['work-product-contract'], 'EVIDENCE', 'WorkProductContract', contract, '$.integration_topology.product_contract')
    source_key = _occurrence_row(out, ['work-product-authority-source'], 'EVIDENCE', 'Artifact', source, '$.authority.qualified_product_contract')
    _occurrence_relation(out, 'DECLARES_SOURCE', contract_key, source_key, '$.authority.qualified_product_contract')
    _occurrence_omit(out, 'PRODUCT_AUTHORITY_BYTES_NOT_CAPTURED', 'EVIDENCE', source_anchor='$.authority.qualified_product_contract')
    _occurrence_omit(out, 'PRODUCT_QUALIFICATION_NOT_ESTABLISHED', 'EVIDENCE', source_anchor='$.integration_topology.product_contract')


def _occurrence_preparation(cell, cells, groups, out, anchor):
    """Validate and project the owner's complete supplied preparation record."""
    value = _occurrence_shape(cell['preparation'], 'kinds effect_class final_composed_only execution_unavailable rank record',
                              'PREPARATION_DECLARATION')
    kinds = _occurrence_preparation_list(value['kinds'], 'PREPARATION_KINDS')
    _occurrence_require(kinds == sorted(kinds) and set(kinds) <= _occurrence_preparation_kinds, 'PREPARATION_KINDS')
    _occurrence_require(value['effect_class'] == 'READ_ONLY_EFFECT_FREE' and value['final_composed_only'] is False,
                        'PREPARATION_EFFECT_BOUNDARY')
    unavailable, predecessors_required = value['execution_unavailable'], set(cell['deps'])
    if cell['state'] == 'BLOCKED':
        _occurrence_shape(unavailable, 'kind dependencies', 'PREPARATION_DEPENDENCY_BINDING')
        dependencies = _occurrence_preparation_list(unavailable['dependencies'], 'PREPARATION_DEPENDENCY_BINDING')
        actual = sorted(dep for dep in cell['deps'] if cells[dep]['state'] != 'DONE')
        _occurrence_require(unavailable['kind'] == 'UNMET_DEPENDENCIES' and dependencies == actual, 'PREPARATION_DEPENDENCY_BINDING')
    elif cell['state'] == 'READY':
        _occurrence_shape(unavailable, 'kind group holders', 'PREPARATION_HOLD_BINDING')
        _occurrence_require(unavailable['kind'] == 'LIVE_HOLD' and _occurrence_text(unavailable['group']), 'PREPARATION_HOLD_BINDING')
        holders = _occurrence_preparation_list(unavailable['holders'], 'PREPARATION_HOLDER_BINDING')
        members = groups.get(unavailable['group'])
        _occurrence_require(type(members) is list and cell['id'] in members, 'PREPARATION_HOLD_BINDING')
        actual = sorted(member for member in members if cells[member]['state'] == 'ACTIVE')
        _occurrence_require(holders == actual and bool(actual), 'PREPARATION_HOLDER_BINDING')
        predecessors_required.update(holders)
    else:
        raise ValueError('PREPARATION_STATE')
    rank = _occurrence_shape(value['rank'], 'terminal_unlock_value expected_reuse cost invalidation_risk', 'PREPARATION_RANK')
    _occurrence_require(all(type(v) is int and v >= 0 for v in rank.values()), 'PREPARATION_RANK')
    record = _occurrence_shape(value['record'], 'graph_path receipt predecessors interface_assumptions inspected_paths proposed_paths '
        'allowed_work forbidden_work cost_boundary invalidators activation_revalidation', 'PREPARATION_RECORD')
    _occurrence_require(_occurrence_text(record['graph_path']) and type(record['cost_boundary']) is str and
                        bool(record['cost_boundary']), 'PREPARATION_RECORD')
    _occurrence_require(_occurrence_work_receipt(record['receipt']), 'PREPARATION_RECEIPT')
    predecessors = record['predecessors']
    _occurrence_require(type(predecessors) is list and bool(predecessors), 'PREPARATION_PREDECESSOR_SET')
    seen = set()
    for predecessor in predecessors:
        _occurrence_shape(predecessor, 'cell_id state identity', 'PREPARATION_PREDECESSOR')
        identity = predecessor['cell_id']
        _occurrence_require(_occurrence_text(identity) and identity in cells and identity not in seen, 'PREPARATION_PREDECESSOR_SET')
        seen.add(identity); observed = cells[identity]
        _occurrence_require(predecessor['state'] == observed['state'], 'PREPARATION_PREDECESSOR_STATE')
        if observed['state'] == 'DONE' and observed.get('source_bearing') is True:
            product = _occurrence_work_product_result(observed.get('result'))['product']
            expected = {'kind': 'QUALIFIED_PRODUCT', **product}
        else:
            expected = {'kind': 'UNAVAILABLE', 'reason': 'NOT_DONE' if observed['state'] != 'DONE' else 'NON_SOURCE_PRODUCT'}
        _occurrence_require(type(predecessor['identity']) is dict and predecessor['identity'] == expected, 'PREPARATION_PREDECESSOR_IDENTITY')
    _occurrence_require(seen == predecessors_required, 'PREPARATION_PREDECESSOR_SET')
    assumptions = record['interface_assumptions']
    _occurrence_require(type(assumptions) is dict and bool(assumptions) and
                        all(_occurrence_text(k) and _occurrence_hash(v) for k, v in assumptions.items()), 'PREPARATION_INTERFACE_ASSUMPTIONS')
    for field in ('inspected_paths', 'proposed_paths'):
        _occurrence_preparation_list(record[field], 'PREPARATION_PATHS')
    allowed = _occurrence_preparation_list(record['allowed_work'], 'PREPARATION_ALLOWED_WORK')
    _occurrence_require(allowed == kinds, 'PREPARATION_ALLOWED_WORK')
    forbidden = _occurrence_preparation_list(record['forbidden_work'], 'PREPARATION_FORBIDDEN_WORK')
    _occurrence_require(set(forbidden) == _occurrence_preparation_forbidden, 'PREPARATION_FORBIDDEN_WORK')
    invalidators = _occurrence_preparation_list(record['invalidators'], 'PREPARATION_INVALIDATORS')
    _occurrence_require({'TARGET_STATE', 'DEPENDENCY_RESULT', 'INTERFACE_ASSUMPTION'} <= set(invalidators), 'PREPARATION_INVALIDATORS')
    activation = _occurrence_preparation_list(record['activation_revalidation'], 'PREPARATION_REVALIDATION')
    _occurrence_require(set(activation) == {'CURRENTNESS', 'DEPENDENCY_RESULTS', 'INTERFACE_ASSUMPTIONS', 'CAUSAL_RED'}, 'PREPARATION_REVALIDATION')
    preparation_key = _occurrence_row(out, ['work-preparation', cell['id']], 'EXECUTION', 'WorkPreparation', value, anchor)
    _occurrence_relation(out, 'HAS_PREPARATION', ['work-cell', cell['id']], preparation_key, anchor)
    for index, predecessor in enumerate(predecessors):
        predecessor_key = _occurrence_row(out, ['preparation-predecessor', cell['id'], predecessor['cell_id']], 'EXECUTION',
            'PreparationPredecessor', predecessor, anchor + '.record.predecessors[' + str(index) + ']')
        _occurrence_relation(out, 'HAS_PREDECESSOR_OBSERVATION', preparation_key, predecessor_key, anchor + '.record.predecessors')
        _occurrence_relation(out, 'OBSERVES_PREDECESSOR', predecessor_key, ['work-cell', predecessor['cell_id']], anchor + '.record.predecessors')
    if unavailable['kind'] == 'LIVE_HOLD':
        _occurrence_relation(out, 'HELD_BY_GROUP', preparation_key, ['work-group', unavailable['group']], anchor + '.execution_unavailable')
        for holder in unavailable['holders']:
            _occurrence_relation(out, 'HELD_BY_MEMBER', preparation_key, ['work-cell', holder], anchor + '.execution_unavailable')
    else:
        for dep in unavailable['dependencies']:
            _occurrence_relation(out, 'BLOCKED_BY_DEPENDENCY', preparation_key, ['work-cell', dep], anchor + '.execution_unavailable')
    _occurrence_omit(out, 'PREPARATION_ACTIVATION_NOT_ESTABLISHED', source_anchor=anchor, member=cell['id'])


def _occurrence_graph(value, out):
    _occurrence_shape(value, 'schema population cells serialization_groups', 'WORK_GRAPH_SHAPE', closed=False)
    _occurrence_require(type(value['population']) is dict and type(value['population'].get('total_cells')) is int and
                        value['population']['total_cells'] >= 0 and type(value['cells']) is list and
                        len(value['cells']) == value['population']['total_cells'], 'frontier count does not equal population')
    cells, states = {}, ('DONE', 'ACTIVE', 'READY', 'BLOCKED')
    for cell in value['cells']:
        _occurrence_shape(cell, 'id state deps', 'WORK_CELL_SHAPE', closed=False)
        _occurrence_require(_occurrence_text(cell['id']) and cell['id'] not in cells and cell['state'] in states, 'WORK_CELL_IDENTITY')
        _occurrence_strings(cell['deps'], 'WORK_CELL_DEPENDENCIES'); cells[cell['id']] = cell
        if 'source_bearing' in cell:
            _occurrence_require(type(cell['source_bearing']) is bool, 'WORK_CELL_SOURCE_BEARING')
    indegree = {key: len(cell['deps']) for key, cell in cells.items()}
    outgoing = {key: [] for key in cells}
    for key, cell in cells.items():
        for dep in cell['deps']:
            _occurrence_require(dep in cells, 'unknown dependency')
            outgoing[dep].append(key)
    ready = [key for key in cells if not indegree[key]]; visited = 0
    while ready:
        key = ready.pop(); visited += 1
        for other in outgoing[key]:
            indegree[other] -= 1
            if not indegree[other]: ready.append(other)
    _occurrence_require(visited == len(cells), 'dependency cycle')
    groups = value['serialization_groups']
    _occurrence_require(type(groups) is dict, 'SERIALIZATION_GROUPS')
    for group, members in groups.items():
        _occurrence_require(_occurrence_text(group) and group.startswith(('W_', 'R_', 'RESOURCE_')), 'SERIALIZATION_GROUP_NAME')
        _occurrence_strings(members, 'GROUP_MEMBERS')
        _occurrence_require(members and all(member in cells for member in members), 'unknown group member')
    if value.get('digest') is not None:
        _occurrence_require(_occurrence_hash(value['digest']) and value['digest'] == _occurrence_sha({k: v for k, v in value.items() if k != 'digest'}), 'WORK_GRAPH_DIGEST')
    if value.get('frontier') is not None:
        cached = value['frontier']
        _occurrence_require(type(cached) is dict and cached.get('population') == len(cells) and
            all(type(cached.get(s.lower())) is int and cached[s.lower()] == sum(c['state'] == s for c in cells.values()) for s in states) and
            all(cached.get(s.lower() + '_ids') == sorted(k for k, c in cells.items() if c['state'] == s) for s in ('ACTIVE', 'READY')), 'stale frontier projection')
    root = _occurrence_row(out, ['work-graph'], 'EXECUTION', 'WorkGraph', value, '$')
    _occurrence_work_products(value, cells, out)
    for index, (key, cell) in enumerate(cells.items()):
        _occurrence_row(out, ['work-cell', key], 'EXECUTION', 'WorkItem', cell, '$.cells')
        for dep in cell['deps']:
            _occurrence_relation(out, 'DEPENDS_ON', ['work-cell', key], ['work-cell', dep], '$.cells.deps')
        if 'preparation' in cell:
            _occurrence_preparation(cell, cells, groups, out, '$.cells[' + str(index) + '].preparation')
        if 'result' in cell and cell.get('source_bearing') is not True:
            _occurrence_omit(out, 'OWNER_OPTIONAL_CONTRACT_NOT_VALIDATED', source_anchor='$.cells', member=key)
    for group, members in groups.items():
        group_key = _occurrence_row(out, ['work-group', group], 'OWNERSHIP', 'Group', {'name': group, 'members': members}, '$.serialization_groups')
        for member in members:
            _occurrence_relation(out, 'HAS_MEMBER', group_key, ['work-cell', member], '$.serialization_groups')
    if any(k not in {'schema', 'population', 'cells', 'serialization_groups', 'frontier', 'digest'} for k in value):
        _occurrence_omit(out, 'OWNER_OPTIONAL_CONTRACT_NOT_VALIDATED', source_anchor='$')
    _occurrence_omit(out, 'INDEPENDENT_GRAPH_POPULATION_AND_GROUP_CENSUS_NOT_IN_CAPTURE')


def _occurrence_binding(value):
    _occurrence_shape(value, 'campaign event state', 'COVERAGE_BINDING')
    _occurrence_require(all(_occurrence_text(v) for v in value.values()), 'COVERAGE_BINDING')
    return value


def _occurrence_coverage(value, out):
    if 'facts' in value:
        _occurrence_shape(value, 'facts projection', 'COVERAGE_PAIR_SHAPE')
        facts, projection = value['facts'], value['projection']
    else:
        facts, projection = value, None
    _occurrence_shape(facts, 'binding currentness evidence_scope root subject parents edges views history', 'COVERAGE_FACTS', closed=False)
    binding = _occurrence_binding(facts['binding'])
    _occurrence_require(facts['currentness'] is None or type(facts['currentness']) is bool, 'COVERAGE_CURRENTNESS')
    _occurrence_require(_occurrence_text(facts['evidence_scope']) and type(facts['parents']) is dict and
                        _occurrence_text(facts['root']) and _occurrence_text(facts['subject']), 'COVERAGE_FACTS')
    ancestors, cursor = [], facts['subject']
    while cursor is not None:
        _occurrence_require(_occurrence_text(cursor) and cursor not in ancestors and cursor in facts['parents'], 'ancestry-unresolved')
        ancestors.append(cursor)
        if cursor == facts['root']:
            _occurrence_require(facts['parents'][cursor] is None, 'ancestry-unresolved'); break
        cursor = facts['parents'][cursor]
    _occurrence_require(ancestors[-1] == facts['root'], 'ancestry-unresolved')
    _occurrence_strings(facts['views'], 'projection-population')
    _occurrence_require(facts['views'] and type(facts['history']) is list, 'COVERAGE_HISTORY')
    for historical in facts['history']:
        _occurrence_shape(historical, 'binding evidence_scope authority', 'COVERAGE_HISTORY', closed=False)
        _occurrence_binding(historical['binding'])
        _occurrence_require(_occurrence_text(historical['evidence_scope']) and historical['authority'] == 'NONE', 'historical-scope')
    edges = {}
    _occurrence_require(type(facts['edges']) is list, 'edge-population')
    gates = {'identity', 'authority', 'independence', 'writer', 'resource', 'prerequisites'}
    directions = {'INWARD', 'OUTWARD', 'FORWARD', 'BACKWARD'}
    eligible, joined, expected = set(), set(), {}
    for edge in facts['edges']:
        _occurrence_shape(edge, 'id at direction state gates accepted joined_into evidence_scope', 'COVERAGE_EDGE', closed=False)
        _occurrence_require(_occurrence_text(edge['id']) and edge['id'] not in edges, 'edge-population')
        _occurrence_require(edge['at'] in ancestors, 'edge-ancestor')
        _occurrence_require(edge['state'] in ('PENDING', 'ACTIVE', 'DONE', 'RETURNED', 'JOINED') and
                            _occurrence_text(edge['direction']) and edge['direction'] in directions and
                            type(edge['accepted']) is bool and (edge['joined_into'] is None or _occurrence_text(edge['joined_into'])) and
                            type(edge['gates']) is dict and gates <= set(edge['gates']) and
                            all(_occurrence_text(k) and v in ('SATISFIED', 'MISSING', 'UNKNOWN') for k, v in edge['gates'].items()), 'COVERAGE_EDGE')
        _occurrence_require(_occurrence_text(edge['evidence_scope']) and (edge['state'] == 'DONE' or
                            all(_occurrence_text(edge.get(k)) for k in ('owner', 'consumer', 'reconsider', 'next_action'))), 'pending-custody')
        absent_custody = [k for k in ('owner', 'consumer', 'reconsider', 'next_action') if k not in edge]
        if edge['state'] == 'DONE' and absent_custody:
            _occurrence_omit(out, 'DONE_CUSTODY_FIELDS_ABSENT', member=edge['id'], fields=absent_custody,
                             source_anchor='$.facts.edges')
        _occurrence_require(edge['gates'].get('native_currentness') != 'SATISFIED' or facts['currentness'] is True, 'native-currentness')
        _occurrence_require(edge['state'] not in ('RETURNED', 'JOINED') or edge['direction'] == 'BACKWARD', 'edge-direction')
        if edge['state'] == 'JOINED':
            _occurrence_require(edge['accepted'] and edge['joined_into'] in ancestors, 'join-acceptance'); joined.add(edge['id'])
        else:
            _occurrence_require(edge['joined_into'] is None, 'join-acceptance')
        pending = {k: v for k, v in edge['gates'].items() if v != 'SATISFIED'}
        disposition = {'ACTIVE': 'ACTIVE', 'DONE': 'RETAINED', 'RETURNED': 'PENDING_JOIN', 'JOINED': 'RETAINED'}.get(edge['state'], 'BLOCKED' if pending else 'ELIGIBLE')
        if disposition == 'ELIGIBLE': eligible.add(edge['id'])
        edges[edge['id']], expected[edge['id']] = edge, (pending, disposition)
    if projection is not None:
        _occurrence_shape(projection, 'binding authority evidence_scope invariants directions ancestors edges new_actions backward_joins views', 'COVERAGE_PROJECTION', closed=False)
        _occurrence_require(_occurrence_binding(projection['binding']) == binding, 'projection-freshness')
        _occurrence_require(projection['authority'] == 'NONE' and projection['evidence_scope'] == facts['evidence_scope'], 'evidence-scope')
        invariants = {'AUTO_LOOM_SCOPE': 'FULL_RECURSIVE_CAMPAIGN_HOLARCHY', 'LOCAL_FORWARD_ONLY': 'INSUFFICIENT',
            'OUTWARD_STARVATION': 'CONFORMANCE_CONCERN', 'FUTURE_JOIN_PRECOMPUTATION_REQUIRED': 'YES', 'BLOCK_EDGE_NOT_FUTURE_GRAPH': 'YES'}
        _occurrence_require(projection['invariants'] == invariants, 'invariant-contract')
        _occurrence_strings(projection['directions'], 'direction-population')
        _occurrence_require(set(projection['directions']) == directions, 'direction-population')
        _occurrence_require(projection['ancestors'] == ancestors, 'ancestor-coverage')
        _occurrence_require(type(projection['edges']) is list and len(projection['edges']) == len(edges) and
                            all(type(r) is dict and _occurrence_text(r.get('id')) for r in projection['edges']) and
                            {r['id'] for r in projection['edges']} == set(edges), 'edge-population')
        for row in projection['edges']:
            edge = edges[row['id']]
            _occurrence_require(_occurrence_binding(row.get('binding')) == binding, 'edge-freshness')
            _occurrence_require(row.get('eligibility') == expected[row['id']][1] and row.get('pending') == expected[row['id']][0], 'edge-disposition')
            _occurrence_require(row.get('authority') == 'NONE' and all(row.get(k) == edge.get(k) for k in
                                ('direction', 'owner', 'consumer', 'reconsider', 'next_action', 'evidence_scope')), 'pending-custody')
        for field in ('new_actions', 'backward_joins'):
            _occurrence_strings(projection[field], 'duplicate-action')
        _occurrence_require(set(projection['new_actions']) <= eligible, 'ineligible-new-action')
        _occurrence_require(set(projection['backward_joins']) == joined, 'accepted-backward-joins')
        if facts.get('prior') is not None:
            _occurrence_require(type(facts['prior']) is dict, 'COVERAGE_PRIOR')
            prior = _occurrence_binding(facts['prior'].get('binding'))
            _occurrence_require(prior['campaign'] == binding['campaign'], 'prior-campaign')
            _occurrence_require(prior != binding or not projection['new_actions'], 'unchanged-event-redispatch')
        views = projection['views']
        _occurrence_require(type(views) is list and len(views) == len(facts['views']) and
                            all(type(v) is dict and _occurrence_text(v.get('name')) for v in views) and
                            {v['name'] for v in views} == set(facts['views']), 'projection-population')
        for view in views:
            vb = _occurrence_binding(view.get('binding'))
            _occurrence_require(view.get('authority') == 'NONE', 'authority-widening')
            if view.get('status') == 'CURRENT':
                _occurrence_require(vb == binding, 'projection-freshness')
                _occurrence_require(view.get('evidence_scope') == facts['evidence_scope'], 'evidence-scope')
            else:
                _occurrence_require(view.get('status') == 'HISTORICAL' and {'binding': vb,
                    'evidence_scope': view.get('evidence_scope'), 'authority': 'NONE'} in facts['history'], 'historical-scope')
        _occurrence_require(any(v['status'] == 'CURRENT' for v in views), 'current-projection-missing')
    else:
        _occurrence_omit(out, 'COVERAGE_PROJECTION_ABSENT')
    root = _occurrence_row(out, ['coverage', binding], 'EXECUTION', 'Coverage', value, '$')
    for ancestor in ancestors:
        _occurrence_row(out, ['coverage-ancestor', binding, ancestor], 'EXECUTION', 'WorkItem',
                        {'id': ancestor, 'parent': facts['parents'][ancestor]}, '$.facts.parents')
    for identity, edge in edges.items():
        key = _occurrence_row(out, ['coverage-edge', binding, identity], 'EXECUTION', 'CoverageEdge', edge, '$.facts.edges')
        _occurrence_relation(out, 'SCOPED_AT', key, ['coverage-ancestor', binding, edge['at']], '$.facts.edges.at')
    _occurrence_omit(out, 'SUPPLIED_COVERAGE_CONSISTENCY_IS_NOT_DISPATCH_ACCEPTANCE_OR_CAUSAL_EVIDENCE')


def _occurrence_lifecycle(value, out):
    schema = value.get('schema')
    prefix = 'implementaudit.'
    short = schema[len(prefix):] if type(schema) is str and schema.startswith(prefix) else None
    core = 'selected_child route_transaction_id obligation_id packet_digest'
    host = 'owner_id host_id host_session_id binding_generation'
    observed = []
    if short in ('holon-execution-evidence.v1', 'resolved-holon-execution-evidence.v1', 'host-holon-stage-receipt.v1'):
        resolved = short != 'holon-execution-evidence.v1'
        standalone = short == 'host-holon-stage-receipt.v1'
        keys = 'schema ' + core + (' ' + host if resolved else '')
        _occurrence_shape(value, keys + (' stage event_id receipt_identity' if short == 'host-holon-stage-receipt.v1' else ' stages'), 'CHILD_VISIBILITY_SHAPE')
        _occurrence_require(value['selected_child'] in _occurrence_roles and all(_occurrence_hash(value[k], True) for k in
                            ('route_transaction_id', 'obligation_id', 'packet_digest')), 'CHILD_DELIVERY_IDENTITY')
        if resolved:
            _occurrence_require(all(_occurrence_text(value[k]) for k in host.split()), 'HOST_STAGE_IDENTITY')
        if standalone:
            _occurrence_require(_occurrence_re.fullmatch(r'G[0-9A-F]{4}', value['binding_generation']) is not None and
                                value['binding_generation'] != 'G0000', 'HOST_STAGE_GENERATION')
        stages = [value] if short == 'host-holon-stage-receipt.v1' else value['stages']
        _occurrence_require(type(stages) is list and (len(stages) == 1 if short == 'host-holon-stage-receipt.v1' else len(stages) == 3), 'STAGE_SEQUENCE')
        _occurrence_require(all(type(r) is dict for r in stages), 'STAGE_SEQUENCE')
        names = [r.get('stage') for r in stages]
        _occurrence_require(names[0] in ('LOAD', 'USE', 'DISPOSE') if len(stages) == 1 else names == ['LOAD', 'USE', 'DISPOSE'], 'STAGE_SEQUENCE')
        seen = set()
        for receipt in stages:
            _occurrence_shape(receipt, 'schema ' + core + ' ' + host + ' stage event_id receipt_identity' if resolved else 'stage receipt_identity', 'STAGE_SHAPE')
            _occurrence_require(_occurrence_hash(receipt['receipt_identity'], True) and receipt['receipt_identity'] not in seen, 'STAGE_RECEIPT_IDENTITY')
            seen.add(receipt['receipt_identity'])
            if resolved:
                _occurrence_require(receipt['schema'] == prefix + 'host-holon-stage-receipt.v1' and
                                    all(receipt[k] == value[k] for k in (core + ' ' + host).split()), 'STAGE_CONTEXT')
                body = {k: v for k, v in receipt.items() if k != 'receipt_identity'}
                expected = _occurrence_host_stage_sha(body) if standalone else _occurrence_sha(body)
                _occurrence_require(_occurrence_text(receipt['event_id']) and receipt['receipt_identity'] ==
                                    'sha256:' + expected, 'STAGE_RECEIPT_DIGEST')
                if _occurrence_host_stage_sha(body) != _occurrence_sha(body):
                    _occurrence_omit(out, 'CROSS_OWNER_RECEIPT_ENCODING_DIFFERS', 'EVIDENCE', stage=receipt['stage'],
                                     selected_contract='HOST_ASCII_ESCAPED' if standalone else 'ROUTE_UTF8',
                                     source_anchor='$' if standalone else '$.stages')
            observed.append((receipt['stage'], receipt))
        _occurrence_row(out, ['child-role', value['selected_child'], value['route_transaction_id'], value['obligation_id']],
                        'OWNERSHIP', 'ChildRole', {k: value[k] for k in core.split()}, '$.selected_child')
    elif short == 'child-return.v1':
        _occurrence_shape(value, 'schema obligation_id route_transaction_id packet_digest status payload', 'CHILD_RETURN_SHAPE')
        _occurrence_require(value['status'] == 'RETURNED' and type(value['payload']) is dict and
                            all(_occurrence_hash(value[k], True) for k in ('obligation_id', 'route_transaction_id', 'packet_digest')), 'CHILD_RETURN_IDENTITY')
        nested = value['payload'].get('holon_execution_evidence')
        if nested is not None:
            _occurrence_require(type(nested) is dict and all(nested.get(k) == value[k] for k in
                                ('obligation_id', 'route_transaction_id', 'packet_digest')), 'CHILD_RETURN_DELIVERY')
            _occurrence_lifecycle(nested, out)
        observed = [('RETURN', {'stage': 'RETURN', 'returned': value})]
    elif short == 'governor-route-decision.v1':
        _occurrence_shape(value, 'schema obligation_id route_transaction_id return_digest outcome reason', 'GOVERNOR_DECISION_SHAPE')
        _occurrence_require(value['outcome'] == 'SATISFIED' and _occurrence_text(value['reason']) and
                            all(_occurrence_hash(value[k], True) for k in ('obligation_id', 'route_transaction_id', 'return_digest')), 'GOVERNOR_DECISION_IDENTITY')
        observed = [('RECONCILE', {'stage': 'RECONCILE', 'decision': value})]
        _occurrence_omit(out, 'EXACT_RETURN_BYTES_NOT_IN_GOVERNOR_DECISION_CAPTURE')
    elif schema is None and 'required_sequence' in value:
        _occurrence_shape(value, 'required_sequence completed selected_child route_transaction_id obligation_id identity_bound unverified '
            'child_authority child_can_route governor_reconciliation_required canonical_credit', 'LIFECYCLE_PROJECTION_SHAPE')
        _occurrence_require(value['required_sequence'] == list(_occurrence_stages) and value['selected_child'] in _occurrence_roles and
                            all(_occurrence_hash(value[k], True) for k in ('route_transaction_id', 'obligation_id')) and
                            value['identity_bound'] is True and value['child_authority'] == 'NONE' and value['child_can_route'] is False, 'LIFECYCLE_IDENTITY')
        completed = _occurrence_strings(value['completed'], 'LIFECYCLE_SEQUENCE')
        _occurrence_require(completed == [s for s in _occurrence_stages if s in completed] and
                            set(completed) - {'LOAD', 'USE', 'DISPOSE'} in (set(), {'OPEN'}, {'OPEN', 'RETURN'}, {'OPEN', 'RETURN', 'RECONCILE'}) and
                            set(completed) & {'LOAD', 'USE', 'DISPOSE'} in (set(), {'LOAD', 'USE', 'DISPOSE'}), 'LIFECYCLE_SEQUENCE')
        missing = [s for s in ('LOAD', 'USE', 'DISPOSE') if s not in completed]
        _occurrence_require(value['unverified'] == missing and value['governor_reconciliation_required'] is ('RECONCILE' not in completed) and
                            value['canonical_credit'] is ('RECONCILE' in completed and not missing), 'LIFECYCLE_CREDIT')
        observed = [(stage, {'stage': stage, 'source_projection': value}) for stage in completed]
        for stage in missing:
            _occurrence_omit(out, 'SOURCE_REPORTED_STAGE_UNVERIFIED', stage=stage)
        _occurrence_row(out, ['child-role', value['selected_child'], value['route_transaction_id'], value['obligation_id']],
                        'OWNERSHIP', 'ChildRole', {'selected_child': value['selected_child']}, '$.selected_child')
    else:
        raise ValueError('KNOWN_CHILD_VISIBILITY_FORMAT_REQUIRED')
    root = _occurrence_row(out, ['child-visibility', schema or 'holon_lifecycle_projection', _occurrence_sha(value)], 'EXECUTION', 'LifecycleObservation', value, '$')
    for stage, evidence in observed:
        key = _occurrence_row(out, ['lifecycle-stage', stage, _occurrence_sha(evidence)], 'EXECUTION', 'LifecycleEvent', evidence, '$.stages' if 'stages' in value else '$')
        _occurrence_relation(out, 'REPORTS_STAGE', root, key, '$')
    _occurrence_omit(out, 'PROCEDURAL_METHOD_NOT_REPRESENTED_IN_OWNER_FORMAT', 'OWNERSHIP')
    _occurrence_omit(out, 'ACCEPTANCE_JOIN_PARENT_COMPLETION_NOT_ESTABLISHED')


def decode_occurrence_capture(kind, value):
    """Decode one explicit captured owner format, preserving the source claim ceiling.

    member-coverage accepts the existing work-graph object, existing coverage
    facts, or a capture-only {facts, projection} packing of the owner's two inputs.
    The packing creates no native schema. Raw source fields remain inert data.
    """
    _occurrence_require(kind in CAPTURE_OCCURRENCE_KINDS, 'UNKNOWN_OCCURRENCE_CAPTURE_KIND')
    _occurrence_scalar(value)
    _occurrence_require(type(value) is dict, 'CAPTURE_OBJECT_REQUIRED')
    _occurrence_require(len(_occurrence_canonical(value)) <= _occurrence_limit, 'CAPTURE_BYTE_BOUND')
    out = {'records': [], 'omissions': []}
    if kind == 'result-occurrence':
        _occurrence_result(value, out)
    elif kind == 'member-coverage':
        if value.get('schema') == 'implementaudit.work-graph.v1':
            _occurrence_graph(value, out)
        else:
            _occurrence_coverage(value, out)
    else:
        _occurrence_lifecycle(value, out)
    _occurrence_omit(out, 'CAPTURE_DOES_NOT_AUTHENTICATE_OWNER_OR_NATIVE_CURRENTNESS', 'EVIDENCE')
    # Multiple references to the same exact occurrence are one fact, never
    # independent corroboration. Conflicting meanings under one key refuse.
    unique = {}
    for row in out['records']:
        key = _occurrence_canonical(row['key'])
        if key in unique:
            prior = unique[key]
            _occurrence_require({k: v for k, v in row.items() if k != 'source_anchor'} ==
                                {k: v for k, v in prior.items() if k != 'source_anchor'}, 'CONFLICTING_CAPTURE_RECORD_IDENTITY')
        else:
            unique[key] = row
    out['records'] = list(unique.values())
    return _occurrence_copy.deepcopy(out)
