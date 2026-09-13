#!/usr/bin/env python3
"""Check source-contract relations; this is not an Auto-LOOM runtime model."""

import argparse
from copy import deepcopy
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile


CHILD_PATH = "skills/implementaudit/references/child-agents.md"
GOVERNOR_PATH = "skills/implementaudit/SKILL.md"
PLANNING_PATH = "skills/implementaudit/references/planning-depth.md"
COVERAGE_PATH = "scripts/check-auto-loom-coverage.py"
RUNTIME_HEADING = "#### Auto-LOOM runtime directions"
DEVELOPMENT_HEADING = "### Auto-LOOM development and continuing improvement"


def normalize(value):
    return " ".join(value.replace("`", "").split()).casefold()


def section(text, heading):
    """Scope claims to their owner section, not matching words elsewhere."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(starts) != 1:
        return ""
    depth = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for i in range(starts[0] + 1, end):
        match = re.match(r"^(#+) ", lines[i])
        if match and len(match[1]) <= depth:
            end = i
            break
    return "\n".join(lines[starts[0] + 1:end])


def table_rows(text, names):
    rows = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        fields = [part.strip() for part in line.strip().strip("|").split("|")]
        if fields[0] in names:
            if fields[0] in rows:
                return {}
            rows[fields[0]] = [normalize(field) for field in fields[1:]]
    return rows


def sequence(text, label):
    match = re.search(re.escape(label) + r":\s*```text\s*(.*?)```", text, re.S)
    return [normalize(step) for step in match[1].split("->")] if match else []


RUNTIME_ROWS = {
    "INWARD": (
        r"fission current work into bounded child tasks\.",
        r"only when useful and admissible\.",
    ),
    "OUTWARD": (
        r"advance independent lateral sibling work\.",
        r"independence and actual authority remain required\.",
    ),
    "FORWARD": (
        r"prepare future descendant work\.",
        r"actual preparation prerequisites must hold; downstream authority is deferred\.",
    ),
    "BACKWARD": (
        r"join partial or full returned work into its parent or ancestor\.",
        r"verify applicable results/evidence and reconcile; return alone grants no authority\.",
    ),
}
DEVELOPMENT_ROWS = {
    "PRODROMAL": (r"emerging proto-practice from work already being done\.",),
    "SUBLIMATION": (r"explicit coherent abstraction of the emerging practice\.",),
    "CONDENSATION": (
        r"concrete contracts, mechanisms, properties, cells, tests, source loci and acceptance criteria\.",
    ),
    "ACTUALISATION": (
        r"actual implementation, integration, installation, qualification and release, each at its applicable evidence and authority boundary\.",
    ),
}
RUNTIME_CYCLE = [
    "join/reconcile results and evidence",
    "re-derive state",
    "re-derive auto-dag",
    "expose newly eligible work",
    "recursive dispatch",
]
IMPROVEMENT_CYCLE = [
    "executed auto-loom n",
    "observed anomaly/opportunity",
    "improvement candidate",
    "sublimation",
    "condensation",
    "existing authority/review/tests/qualification",
    "actualisation auto-loom n+1",
]


def violations(child, planning):
    failures = []
    runtime = section(child, RUNTIME_HEADING)
    development = section(planning, DEVELOPMENT_HEADING)
    for label, text, expected in (
        ("runtime", runtime, RUNTIME_ROWS),
        ("development", development, DEVELOPMENT_ROWS),
    ):
        rows = table_rows(text, expected)
        if label == "development" and list(rows) != list(expected):
            failures.append("development.first-maturation-order")
        for name, patterns in expected.items():
            cells = rows.get(name, [])
            if len(cells) != len(patterns) or any(
                re.fullmatch(pattern, cell) is None
                for pattern, cell in zip(patterns, cells)
            ):
                failures.append(f"{label}.{name}.meaning-or-boundary")

    if sequence(runtime, "Runtime cycle") != RUNTIME_CYCLE:
        failures.append("runtime.ordered-join-state-dag-dispatch")
    if sequence(development, "Improvement cycle") != IMPROVEMENT_CYCLE:
        failures.append("development.executed-evidence-to-qualified-successor")

    claims = [
        ("runtime.return-direction", runtime,
         "Returning results is BACKWARD, not OUTWARD."),
        ("runtime.edge-scoped-block", runtime,
         "Block only the affected edge; defer authority without blocking admissible learning."),
        ("runtime.root-control", runtime,
         "The thin root governor retains dispatch, JOIN, acceptance and currentness authority; children propose further fission."),
        ("runtime.eligibility", runtime,
         "Recheck actual prerequisites, identity, authority, writer/resource conflicts and capacity before dispatch; partial JOIN need not wait for unrelated returns."),
        ("development.separate-axis", development,
         "These developmental stages describe abstraction and maturity, separately from the runtime directions in child-agents.md."),
        ("development.first-maturation-explicit", development,
         "The first maturation proceeds through the following stages in order."),
        ("development.reject-category-errors", development,
         "PRODROMAL is not FORWARD; SUBLIMATION is not state re-derivation; CONDENSATION is not JOIN."),
        ("development.proposal-is-not-actualisation", development,
         "A proposal or retained contract is not ACTUALISATION."),
        ("development.continues-after-actualisation", development,
         "PRODROMAL practice bootstraps reflexive, evidence-driven self-improvement that continues after ACTUALISATION."),
        ("development.value-admission", development,
         "Apply the engineering-value admission and control lifecycle above to each candidate: require its live driver, owner, consumer, cheapest sufficient discriminator, marginal value and stopping condition."),
        ("development.dispositions", development,
         "Preserve reject, defer and no-change outcomes; recurrence or a candidate never mandates a change."),
        ("development.existing-governance", development,
         "Use existing authority, currentness, review, tests and qualification controls; this loop adds no controller or gate and permits no unattended self-rewrite."),
        ("planning.backward-future-projection", planning,
         "Here, lowercase backward describes projecting future work earlier: it is runtime FORWARD preparation, not BACKWARD return/JOIN."),
    ]
    for label, text, claim in claims:
        if normalize(claim) not in normalize(text):
            failures.append(label)
    return failures


def controls(child, planning):
    """Mutate relationships while retaining vocabulary wherever possible."""
    count = 0

    def reject(label, original, before, after, expected, is_planning=False):
        nonlocal count
        pattern = re.compile(r"\s+".join(re.escape(part) for part in before.split()), re.I)
        if len(pattern.findall(original)) != 1:
            raise AssertionError(f"control setup is not unique: {label}")
        changed = pattern.sub(lambda match: after, original, count=1)
        found = violations(child, changed) if is_planning else violations(changed, planning)
        if expected not in found:
            raise AssertionError(f"accepted or wrong rejection for {label}: {found}")
        count += 1

    for name in RUNTIME_ROWS:
        row = next(line for line in child.splitlines() if line.startswith(f"| {name} |"))
        reject(f"remove-{name}", child, row, "", f"runtime.{name}.meaning-or-boundary")
    for name in DEVELOPMENT_ROWS:
        row = next(line for line in planning.splitlines() if line.startswith(f"| {name} |"))
        reject(f"remove-{name}", planning, row, "", f"development.{name}.meaning-or-boundary", True)

    # Swaps retain every direction/action word but assign the wrong relation.
    swapped = child.replace("| OUTWARD |", "| SWAP |", 1).replace(
        "| BACKWARD |", "| OUTWARD |", 1).replace("| SWAP |", "| BACKWARD |", 1)
    assert "runtime.OUTWARD.meaning-or-boundary" in violations(swapped, planning)
    count += 1
    lines = planning.splitlines()
    indices = [i for i, line in enumerate(lines) if any(line.startswith(f"| {name} |") for name in DEVELOPMENT_ROWS)]
    lines[indices[0]], lines[indices[1]] = lines[indices[1]], lines[indices[0]]
    assert "development.first-maturation-order" in violations(child, "\n".join(lines))
    count += 1
    reject("state-before-join", child,
           "JOIN/reconcile results and evidence\n-> re-derive state",
           "re-derive state\n-> JOIN/reconcile results and evidence",
           "runtime.ordered-join-state-dag-dispatch")
    reject("dispatch-before-dag", child,
           "re-derive Auto-DAG\n-> expose newly eligible work\n-> recursive dispatch",
           "recursive dispatch\n-> expose newly eligible work\n-> re-derive Auto-DAG",
           "runtime.ordered-join-state-dag-dispatch")
    reject("forward-with-unmet-prerequisites", child,
           "actual preparation prerequisites must hold", "actual preparation prerequisites may be unmet",
           "runtime.FORWARD.meaning-or-boundary")
    reject("return-confers-authority", child,
           "return alone grants no authority", "return alone grants authority",
           "runtime.BACKWARD.meaning-or-boundary")
    for name, wrong in (("PRODROMAL", "FORWARD preparation."),
                        ("SUBLIMATION", "State re-derivation."),
                        ("CONDENSATION", "JOIN of returned work."),
                        ("ACTUALISATION", "A retained proposal.")):
        row = next(line for line in planning.splitlines() if line.startswith(f"| {name} |"))
        reject(f"misclassify-{name}", planning, row, f"| {name} | {wrong} |",
               f"development.{name}.meaning-or-boundary", True)
    reject("qualification-after-actualisation", planning,
           "existing authority/review/tests/qualification\n-> ACTUALISATION Auto-LOOM n+1",
           "ACTUALISATION Auto-LOOM n+1\n-> existing authority/review/tests/qualification",
           "development.executed-evidence-to-qualified-successor", True)
    reject("unobserved-improvement", planning, "observed anomaly/opportunity\n-> improvement candidate",
           "unobserved supposition\n-> improvement candidate",
           "development.executed-evidence-to-qualified-successor", True)
    for label, before, after in (
        ("continues-after-actualisation", "continues after ACTUALISATION", "ends at ACTUALISATION"),
        ("proposal-is-not-actualisation", "is not ACTUALISATION.", "is ACTUALISATION."),
        ("dispositions", "Preserve reject, defer and no-change outcomes", "Require every candidate to change source"),
        ("existing-governance", "permits no unattended self-rewrite", "permits unattended self-rewrite"),
        ("value-admission", "cheapest sufficient discriminator, marginal value and stopping condition",
         "a methodology label alone"),
    ):
        reject(label, planning, before, after, f"development.{label}", True)
    reject("global-block", child, "Block only the affected edge", "Block the entire graph",
           "runtime.edge-scoped-block")
    reject("child-authority", child, "The thin root governor retains dispatch, JOIN",
           "Every child retains dispatch, JOIN", "runtime.root-control")
    reject("backward-projection-conflated", planning,
           "it is runtime FORWARD preparation, not BACKWARD return/JOIN",
           "it is runtime BACKWARD return/JOIN, not FORWARD preparation",
           "planning.backward-future-projection", True)

    # Harmless formatting and row order must not change the source relations.
    assert not violations(child.replace("\n", "\r\n"), planning.replace("\n", "\r\n"))
    assert not violations(child.replace(" | ", "  |  "), planning.replace(" | ", "  |  "))
    lines = child.splitlines()
    indices = [i for i, line in enumerate(lines) if any(line.startswith(f"| {name} |") for name in RUNTIME_ROWS)]
    old_rows = [lines[i] for i in indices]
    for i, row in zip(indices, reversed(old_rows)):
        lines[i] = row
    assert not violations("\n".join(lines), planning)
    return count, 3



COVERAGE_INVARIANTS = {
    "AUTO_LOOM_SCOPE": "FULL_RECURSIVE_CAMPAIGN_HOLARCHY",
    "LOCAL_FORWARD_ONLY": "INSUFFICIENT",
    "OUTWARD_STARVATION": "CONFORMANCE_CONCERN",
    "FUTURE_JOIN_PRECOMPUTATION_REQUIRED": "YES",
    "BLOCK_EDGE_NOT_FUTURE_GRAPH": "YES",
}


def coverage_contract_violations(governor, child, planning):
    """Protect the required source relations; behavioral cases use the real CLI."""
    runtime = section(child, RUNTIME_HEADING)
    failures = []
    for key, value in COVERAGE_INVARIANTS.items():
        if f"{key}={value}" not in runtime:
            failures.append(f"coverage.contract.{key}")
    if "AUTO_LOOM_SCOPE=FULL_RECURSIVE_CAMPAIGN_HOLARCHY" not in governor:
        failures.append("coverage.governor-scope")
    for label, text, claim in (
        ("ancestors", runtime,
         "After each material RETURN/JOIN or state/DAG re-derivation, traverse known ancestors through the existing campaign root."),
        ("reconsider", runtime,
         "At every ancestor, reconsider applicable siblings and future JOIN, admission, census, qualification and release prerequisites."),
        ("pending", runtime,
         "Each edge retains its actual eligibility or exact missing input, entitled owner, future consumer/JOIN and reconsideration trigger."),
        ("freshness", runtime,
         "Current projections bind the same campaign, material event and state; stale, mixed or foreign projections cannot count as current coverage."),
        ("historical", runtime,
         "Explicitly historical projections retain only their original evidence scope and do not satisfy current coverage."),
        ("accepted-join", runtime,
         "A returned product earns BACKWARD credit only after actual acceptance/JOIN, never OUTWARD."),
        ("no-replay", runtime,
         "An unchanged event does not redispatch work; retain completed qualification/publication evidence without replay or authority widening."),
        ("future-preparation", planning,
         "Precompute applicable future ancestor-JOIN prerequisites now when their actual preparation inputs and authority permit; block only the affected edge."),
    ):
        if normalize(claim) not in normalize(text):
            failures.append(f"coverage.contract.{label}")
    if COVERAGE_PATH not in runtime:
        failures.append("coverage.consumer-link")
    return failures


def coverage_case():
    """Literal, hand-derived dispositions; no expectation calls the consumer."""
    binding = {"campaign": "fixture-v041", "event": "material-join-2", "state": "state-2"}
    old = {"campaign": "fixture-v041", "event": "material-join-1", "state": "state-1"}
    facts = {
        "binding": binding, "root": "campaign", "subject": "recovery",
        "parents": {"recovery": "integration", "integration": "campaign", "campaign": None},
        "views": ["auto_loom", "current_boundary", "runtime_directions_latest"],
        "history": [{"binding": old, "evidence_scope": "SOURCE_ONLY", "authority": "NONE"}],
        "currentness": False, "evidence_scope": "SOURCE_ONLY",
        "prior": None, "edges": [],
    }
    proposal = {
        "binding": deepcopy(binding), "invariants": deepcopy(COVERAGE_INVARIANTS),
        "directions": ["INWARD", "OUTWARD", "FORWARD", "BACKWARD"],
        "ancestors": ["recovery", "integration", "campaign"], "edges": [],
        "views": [
            {"name": "auto_loom", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
            {"name": "current_boundary", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
            {"name": "runtime_directions_latest", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
        ],
        "new_actions": ["rlgwo-prep", "future-source-join"],
        "backward_joins": ["accepted-source"],
        "evidence_scope": "SOURCE_ONLY", "authority": "NONE",
    }

    def add(identity, ancestor, direction, state, gates, want, pending, owner, consumer,
            reconsider, next_action, scope="SOURCE_ONLY", accepted=False, joined_into=None):
        common = {
            "id": identity, "direction": direction, "owner": owner, "consumer": consumer,
            "reconsider": reconsider, "next_action": next_action, "evidence_scope": scope,
        }
        facts["edges"].append({
            **common, "at": ancestor, "state": state, "gates": gates,
            "accepted": accepted, "joined_into": joined_into,
        })
        proposal["edges"].append({
            **common, "binding": deepcopy(binding), "eligibility": want,
            "pending": pending, "authority": "NONE",
        })

    clear = {"identity": "SATISFIED", "authority": "SATISFIED",
             "independence": "SATISFIED", "writer": "SATISFIED", "resource": "SATISFIED",
             "prerequisites": "SATISFIED"}
    add("native-recovery", "recovery", "INWARD", "PENDING",
        {**clear, "native_currentness": "MISSING"}, "BLOCKED", {"native_currentness": "MISSING"},
        "native-owner", "recovery-join", "native-currentness-receipt", "await-currentness",
        scope="NONE")
    add("rlgwo-prep", "integration", "OUTWARD", "PENDING", dict(clear), "ELIGIBLE", {},
        "rlgwo-owner", "crosswalk-join", "new-source-or-owner-disposition", "prepare-crosswalk")
    add("future-source-join", "campaign", "FORWARD", "PENDING", dict(clear), "ELIGIBLE", {},
        "source-owner", "future-b4-qualification-join", "integrated-identity-freeze", "prepare-gate-matrix")
    add("a-through-k-admission", "integration", "OUTWARD", "PENDING",
        {**clear, "independence": "UNKNOWN", "authority": "MISSING"}, "BLOCKED",
        {"independence": "UNKNOWN", "authority": "MISSING"},
        "admission-owner", "a-through-k-join", "per-lane-independence-and-authority", "await-lane-admission")
    add("material-census", "campaign", "FORWARD", "PENDING",
        {**clear, "writer": "MISSING"}, "BLOCKED", {"writer": "MISSING"},
        "census-owner", "material-census-join", "shared-writer-release", "await-writer")
    add("publication-done", "campaign", "FORWARD", "DONE", dict(clear), "RETAINED", {},
        "publication-owner", "public-consumer-readback", "applicability-change-only", "retain-completed-proof",
        scope="PUBLICATION_EVIDENCE")
    add("returned-source", "integration", "BACKWARD", "RETURNED", dict(clear), "PENDING_JOIN", {},
        "root", "source-join", "root-acceptance-join", "await-acceptance")
    add("accepted-source", "integration", "BACKWARD", "JOINED", dict(clear), "RETAINED", {},
        "root", "source-join", "changed-source-applicability", "retain-partial-join",
        accepted=True, joined_into="integration")
    add("four-child-active", "integration", "INWARD", "ACTIVE", dict(clear), "ACTIVE", {},
        "four-child-owner", "four-child-join", "material-return", "retain-active-owner")
    return facts, proposal


def coverage_controls(repo_root):
    """Catch loss of ancestry/freshness/edge limits through the maintained CLI."""
    checker = repo_root / COVERAGE_PATH
    negatives = positives = 0
    with tempfile.TemporaryDirectory(prefix="auto-loom-coverage-") as directory:
        root = Path(directory)
        facts_path, proposal_path = root / "facts.json", root / "proposal.json"

        def run(label, facts, proposal, expected=None):
            nonlocal negatives, positives
            facts_bytes = (json.dumps(facts, indent=2) + "\n").encode()
            proposal_bytes = (json.dumps(proposal, indent=2) + "\n").encode()
            facts_path.write_bytes(facts_bytes)
            proposal_path.write_bytes(proposal_bytes)
            result = subprocess.run(
                [sys.executable, str(checker), "--facts", str(facts_path),
                 "--projection", str(proposal_path)], capture_output=True, text=True,
            )
            assert not result.stderr, (label, result.stderr)
            report = json.loads(result.stdout)
            assert facts_path.read_bytes() == facts_bytes, f"consumer mutated facts: {label}"
            assert proposal_path.read_bytes() == proposal_bytes, f"consumer mutated projection: {label}"
            assert report["authority"] == "NONE", (label, report)
            if expected is None:
                assert result.returncode == 0 and not report["issues"], (label, report)
                assert report["status"] == "CONSISTENT_SOURCE_COVERAGE_ONLY", (label, report)
                positives += 1
            else:
                assert result.returncode != 0 and expected in report["issues"], (label, report)
                negatives += 1
            return report

        facts, proposal = coverage_case()
        run("multi-ancestor-blocked-recovery-eligible-sibling-future-join", facts, proposal)

        # Matching projections cannot supply a missing subject/root/ancestor identity.
        for name, identity, expected in (
            ("subject", "recovery", "invalid-input"),
            ("campaign-root", "campaign", "invalid-input"),
            ("ancestor", "integration", "ancestry-unresolved"),
        ):
            for label, blank in (("empty", ""), ("whitespace", " \t\n")):
                unnamed_facts, unnamed = deepcopy(facts), deepcopy(proposal)
                unnamed_facts["parents"] = {
                    blank if node == identity else node:
                    blank if parent == identity else parent
                    for node, parent in facts["parents"].items()
                }
                for field in ("subject", "root"):
                    if unnamed_facts[field] == identity:
                        unnamed_facts[field] = blank
                for edge in unnamed_facts["edges"]:
                    for field in ("at", "joined_into"):
                        if edge[field] == identity:
                            edge[field] = blank
                unnamed["ancestors"] = [
                    blank if node == identity else node for node in proposal["ancestors"]
                ]
                run(f"{label}-{name}-identity", unnamed_facts, unnamed, expected)

        named_facts, named = deepcopy(facts), deepcopy(proposal)
        named_facts["parents"]["campaign"] = "campaign-root"
        named_facts["parents"]["campaign-root"] = None
        named_facts["root"] = "campaign-root"
        named_facts["currentness"] = None
        named["ancestors"].append("campaign-root")
        run("four-named-ancestors-unknown-currentness-independent-preparation", named_facts, named)

        # Retention needs the original scope; two absent/invalid values are no scope.
        for identity in ("publication-done", "accepted-source"):
            position = next(i for i, edge in enumerate(facts["edges"]) if edge["id"] == identity)
            for label, scope in (
                ("missing", None), ("null", None), ("empty", ""),
                ("whitespace", " \t\n"), ("non-string", 0),
            ):
                unscoped_facts, unscoped = deepcopy(facts), deepcopy(proposal)
                for edge in (unscoped_facts["edges"][position], unscoped["edges"][position]):
                    if label == "missing":
                        del edge["evidence_scope"]
                    else:
                        edge["evidence_scope"] = scope
                run(f"retained-{identity}-{label}-original-scope", unscoped_facts, unscoped,
                    "invalid-input")

            explicit_facts, explicit = deepcopy(facts), deepcopy(proposal)
            explicit_facts["edges"][position]["evidence_scope"] = "NONE"
            explicit["edges"][position]["evidence_scope"] = "NONE"
            run(f"retained-{identity}-explicit-NONE-scope", explicit_facts, explicit)
            missing_projection = deepcopy(proposal)
            del missing_projection["edges"][position]["evidence_scope"]
            run(f"retained-{identity}-missing-projected-scope", facts, missing_projection,
                "evidence-scope")

        # Removing ancestor traversal while retaining all labels/literals is a bug.
        local = deepcopy(proposal)
        local["ancestors"] = ["recovery"]
        local["edges"] = local["edges"][:1]
        local["new_actions"] = []
        local["backward_joins"] = []
        assert local["invariants"] == COVERAGE_INVARIANTS and len(local["directions"]) == 4
        run("labels-and-five-literals-local-only", facts, local, "ancestor-coverage")

        for label, target, field, value in (
            ("stale-current-view", "view", "event", "material-join-1"),
            ("mixed-current-state", "view", "state", "state-1"),
            ("foreign-current-campaign", "view", "campaign", "foreign-campaign"),
            ("stale-edge-decision", "edge", "event", "material-join-1"),
        ):
            changed = deepcopy(proposal)
            row = changed["views"][-1] if target == "view" else changed["edges"][1]
            row["binding"][field] = value
            run(label, facts, changed, "projection-freshness" if target == "view" else "edge-freshness")

        historical = deepcopy(proposal)
        historical["views"][-1]["status"] = "HISTORICAL"
        historical["views"][-1]["binding"] = deepcopy(facts["history"][0]["binding"])
        run("explicit-historical-retention-original-scope", facts, historical)
        widened = deepcopy(historical)
        widened["views"][-1]["evidence_scope"] = "RUNTIME_QUALIFIED"
        run("historical-evidence-cannot-widen", facts, widened, "historical-scope")
        all_historical = deepcopy(historical)
        for view in all_historical["views"]:
            view["status"] = "HISTORICAL"
            view["binding"] = deepcopy(facts["history"][0]["binding"])
        run("historical-retention-is-not-current-coverage", facts, all_historical, "current-projection-missing")

        # False global currentness blocking must fail, while real edge blocks stand.
        blanket = deepcopy(proposal)
        blanket["edges"][1]["eligibility"] = "BLOCKED"
        blanket["edges"][1]["pending"] = {"native_currentness": "MISSING"}
        run("blanket-native-block-suppresses-eligible-sibling", facts, blanket, "edge-disposition")
        for index, label in ((0, "native-currentness"), (3, "unknown-independence"), (4, "shared-writer")):
            changed = deepcopy(proposal)
            changed["edges"][index]["eligibility"] = "ELIGIBLE"
            changed["edges"][index]["pending"] = {}
            changed["new_actions"].append(changed["edges"][index]["id"])
            run(f"real-{label}-block-preserved", facts, changed, "edge-disposition")
        unknown = deepcopy(proposal)
        unknown["edges"][3]["pending"]["independence"] = "MISSING"
        run("unknown-stays-unknown", facts, unknown, "pending-inputs")
        contradictory = deepcopy(facts)
        contradictory["edges"][0]["gates"]["native_currentness"] = "SATISFIED"
        admitted = deepcopy(proposal)
        admitted["edges"][0]["eligibility"] = "ELIGIBLE"
        admitted["edges"][0]["pending"] = {}
        admitted["new_actions"].append("native-recovery")
        run("native-gate-cannot-override-false-currentness", contradictory, admitted, "native-currentness")
        admission = deepcopy(proposal)
        admission["edges"][1]["evidence_scope"] = "THIRTEEN_LANES_ADMITTED"
        run("shared-source-is-not-lane-admission", facts, admission, "evidence-scope")

        returned = deepcopy(proposal)
        returned["backward_joins"].append("returned-source")
        run("returned-not-accepted-no-backward-credit", facts, returned, "accepted-backward-joins")
        outward = deepcopy(proposal)
        outward["edges"][7]["direction"] = "OUTWARD"
        run("accepted-partial-join-never-outward", facts, outward, "edge-direction")
        missing_join = deepcopy(facts)
        missing_join["edges"][7]["accepted"] = False
        run("joined-label-does-not-invent-acceptance", missing_join, proposal, "join-acceptance")

        repeated_facts = deepcopy(facts)
        repeated_facts["prior"] = {"binding": deepcopy(facts["binding"])}
        repeated = deepcopy(proposal)
        repeated["new_actions"] = []
        first = run("unchanged-event-no-redispatch", repeated_facts, repeated)
        second = run("unchanged-event-deterministic-readback", repeated_facts, repeated)
        assert first == second, "unchanged input produced a different acceptance report"
        run("unchanged-event-replay-rejected", repeated_facts, proposal, "unchanged-event-redispatch")
        for identity in ("publication-done", "four-child-active"):
            replay = deepcopy(proposal)
            replay["new_actions"].append(identity)
            run(f"no-replay-{identity}", facts, replay, "ineligible-new-action")
        mint = deepcopy(proposal)
        mint["authority"] = "CURRENTNESS"
        run("projection-cannot-mint-authority", facts, mint, "authority-widening")
        pending = deepcopy(proposal)
        pending["edges"][4]["reconsider"] = ""
        run("blocked-edge-needs-reconsideration-trigger", facts, pending, "pending-custody")
        absent = deepcopy(proposal)
        absent["views"] = absent["views"][:2]
        run("unreported-latest-projection-is-not-coverage", facts, absent, "projection-population")
        broken_path = deepcopy(facts)
        del broken_path["parents"]["integration"]
        run("unknown-ancestor-is-not-campaign-root", broken_path, proposal, "ancestry-unresolved")

        # A non-applicable edge is not imported from a foreign holarchy.
        foreign_facts = deepcopy(facts)
        foreign_facts["edges"][0]["at"] = "foreign-root"
        run("foreign-edge-owner", foreign_facts, proposal, "edge-ancestor")
        missing_gates = deepcopy(facts)
        del missing_gates["edges"][1]["gates"]["authority"]
        run("missing-authority-fact-is-not-satisfied", missing_gates, proposal, "invalid-input")
        duplicated = deepcopy(proposal)
        duplicated["edges"].append(deepcopy(duplicated["edges"][0]))
        run("duplicate-edge-does-not-close-census", facts, duplicated, "edge-population")
    return negatives, positives


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--coverage-only", action="store_true",
                        help="run the global coverage delta without replaying old controls")
    args = parser.parse_args()
    child = (args.repo_root / CHILD_PATH).read_text(encoding="utf-8")
    planning = (args.repo_root / PLANNING_PATH).read_text(encoding="utf-8")
    governor = (args.repo_root / GOVERNOR_PATH).read_text(encoding="utf-8")
    failures = violations(child, planning) + coverage_contract_violations(governor, child, planning)
    if not (args.repo_root / COVERAGE_PATH).is_file():
        failures.append("coverage.acceptance-consumer-missing")
    if failures:
        raise SystemExit("auto-loom-semantics: FAIL: " + ", ".join(failures))
    negatives, positives = (0, 0) if args.coverage_only else controls(child, planning)
    coverage_negatives, coverage_positives = coverage_controls(args.repo_root)
    print(f"auto-loom-semantics: ok ({negatives} negative controls, {positives} positive controls; source contract only)")
    print(f"auto-loom-coverage: ok ({coverage_negatives} negative controls, {coverage_positives} positive controls; read-only acceptance consumer, no runtime conformance)")


if __name__ == "__main__":
    main()
