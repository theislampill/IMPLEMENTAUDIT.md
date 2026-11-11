#!/usr/bin/env python3
"""Bounded canonical hot projection rendering; no native handles or publication.

Typed state and custody validation remain canonical at the rotation owner. They
are explicit injected preconditions, not duplicated field models in this module.
"""
from __future__ import annotations
from typing import Any, Mapping, Sequence
STATE_HOT_SECTIONS_V1 = (
    "# IMPLEMENTAUDIT State", "## Current phase", "## Audit object state",
    "## Runtime artifacts", "## Ledger", "## Andon log",
    "## Occurrence resolution and residuals", "## Execution identity",
    "## Context epochs and instruction applicability", "## AGENTS_UPDATE_DECISION",
    "## CONTINUITY_DECISION", "## Local git trace", "## Run terminal disposition",
)
ROADMAP_HOT_SECTIONS_V1 = (
    "# IMPLEMENTAUDIT Roadmap", "## Goal", "## Audit object",
    "## Action selection", "## Baseline ref", "## Run root",
    "## Planning evidence", "## Phases", "## Execution index (projection)",
    "## Scope boundaries", "## Scope-creep register",
)

class HotProjectionRenderer:
    def __init__(self, *, error_type, validate_fields, validate_dependencies):
        self._error_type = error_type
        self._validate_fields = validate_fields
        self._validate_dependencies = validate_dependencies


    def _hot_value_v1(self, value: object) -> str:
        if (type(value) is not str or not value or any(char in value for char in "\r\n|")):
            raise self._error_type("hot projection field is invalid")
        return value

    def _render_lines_v1(self, lines: Sequence[str]) -> bytes:
        raw = ("\n".join(lines).rstrip() + "\n").encode("utf-8")
        if len(raw) > 4096:
            raise self._error_type("hot projection exceeds v1 byte bound")
        return raw

    def _markdown_headings_v1(self, raw: bytes) -> tuple[str, ...]:
        try:
            lines = raw.decode("utf-8", "strict").splitlines()
        except UnicodeDecodeError as exc:
            raise self._error_type("hot template is not UTF-8") from exc
        return tuple(line for line in lines
                     if line.startswith("# ") or line.startswith("## "))

    def verify_hot_renderer_template_parity_v1(self,
            state_template: bytes, roadmap_template: bytes,
            state_rendered: bytes, roadmap_rendered: bytes) -> None:
        populations = (
            (state_template, state_rendered, STATE_HOT_SECTIONS_V1),
            (roadmap_template, roadmap_rendered, ROADMAP_HOT_SECTIONS_V1),
        )
        for template, rendered, expected in populations:
            if (type(template) is not bytes or type(rendered) is not bytes
                    or self._markdown_headings_v1(template) != expected
                    or self._markdown_headings_v1(rendered) != expected):
                raise self._error_type("hot renderer and canonical template sections disagree")

    def render_state_template_v1(self, fields: Mapping[str, object], graph: Any,
                                 custody: Any) -> bytes:
        self._validate_fields(fields)
        self._validate_dependencies(graph, custody)
        lines = [
            "# IMPLEMENTAUDIT State", "",
            "Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md`", "",
            "Bounded current/open projection; closed detail is immutable query history.", "",
            "## Current phase", "", "| Field | Value |", "|---|---|",
            f"| Run root | `{self._hot_value_v1(fields['implementaudit_base'])}/{self._hot_value_v1(fields['run_id'])}` |",
            f"| Phase | {self._hot_value_v1(fields['phase'])} |",
            f"| Status | {self._hot_value_v1(fields['status'])} |",
            f"| Audit object state | {self._hot_value_v1(fields['audit_object_state'])} |",
            f"| Route | {self._hot_value_v1(fields['route'])} |",
            f"| Owner/source | {self._hot_value_v1(fields['owner_source'])} |",
            f"| Baseline ref | `{self._hot_value_v1(fields['baseline_ref'])}` |",
            f"| Last check | {self._hot_value_v1(fields['last_check'])} |",
            f"| Next action | {self._hot_value_v1(fields['next_action'])} |", "",
            "## Audit object state", "",
            f"Audit object source: {self._hot_value_v1(fields['audit_object_source'])}", "",
            f"Latest auditing operation: {self._hot_value_v1(fields['latest_auditing_operation'])}", "",
            f"Terminal closure condition: {self._hot_value_v1(fields['terminal_closure_condition'])}", "",
            f"Handoff state: {self._hot_value_v1(fields['handoff_state'])}", "",
            "## Runtime artifacts", "", "| Artifact | Status | Notes |", "|---|---|---|",
        ]
        for artifact in fields["runtime_artifacts"]:
            lines.append(f"| `{artifact.path}` | {artifact.status} | {artifact.notes} |")
        lines.extend([
            "", "## Ledger", "",
            "| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |",
            "|---|---|---:|---|---|---|---|---|",
        ])
        for finding in fields["open_ledger"]:
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % finding)
        lines.extend([
            "", "## Andon log", "",
            "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |",
            "|---|---|---|---|---|---|---|---|",
        ])
        for andon in fields["open_andons"]:
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % andon)
        lines.extend([
            "", "## Occurrence resolution and residuals", "",
            f"Occurrence resolution: {self._hot_value_v1(fields['occurrence_resolution'])}", "",
            "| Residual | Consequential | Disposition | Owner / policy ref | Evidence |",
            "|---|---|---|---|---|",
        ])
        for residual in fields["open_residuals"]:
            lines.append("| %s | %s | %s | %s | %s |" % residual)
        lines.extend([
            "", "## Execution identity", "",
            f"Current execution identity: {self._hot_value_v1(fields['execution_identity'])}", "",
            "", "## Context epochs and instruction applicability", "",
            f"Current epoch: {self._hot_value_v1(fields['current_epoch'])}", "",
            f"Canonical projection generation: {self._hot_value_v1(fields['current_epoch'])}", "",
            f"Current-generation pointer: `{custody.current_generation_ref}@{custody.pointer_oid}`", "",
            "Migration marker: not published by migration-only projection", "",
            "Current continuity receipt: query on demand", "",
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |",
            "|---|---|---|---|---|---|",
            f"| {self._hot_value_v1(fields['current_epoch'])} | handoff-resume | current | `{graph.work_graph_path}` at `{graph.work_graph_digest}` | yes | current hot projection |",
            "", "| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ])
        for instruction in fields["active_instructions"]:
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % instruction)
        agents = fields["agents_update_decision"]
        continuity = fields["continuity_decision_record"]
        lines.extend([
            "", f"Exact archive: `{custody.archive_ref}` at `{custody.archive_digest}`", "",
            f"History query: `{custody.history_query}`", "",
            "## AGENTS_UPDATE_DECISION", "",
            f"Status: {agents.status}", "", f"Reason: {agents.reason}", "",
            f"Scope: {agents.target}", "", f"Evidence location: {agents.evidence}", "",
            "## CONTINUITY_DECISION", "",
            f"Status: {continuity.status}", "", f"Reason: {continuity.reason}", "",
            f"Destination: {continuity.target}", "", f"Evidence boundary: {continuity.evidence}", "",
            "", "## Local git trace", "", "Commit authorized: no", "",
            "Push authorized: no", "", "Tag/release/publication/provenance authorized: no",
            "", "## Run terminal disposition", "",
            "Current open state only; closed history remains in immutable events and exact archives.",
        ])
        return self._render_lines_v1(lines)

    def render_roadmap_template_v1(self, fields: Mapping[str, object], graph: Any,
                                   custody: Any) -> bytes:
        self._validate_fields(fields)
        self._validate_dependencies(graph, custody)
        lines = [
            "# IMPLEMENTAUDIT Roadmap", "",
            "Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/ROADMAP.md`", "",
            "## Goal", "", self._hot_value_v1(fields["next_action"]), "",
            "## Audit object", "",
            f"Audit object source: {self._hot_value_v1(fields['audit_object_source'])}", "",
            f"Terminal closure condition: {self._hot_value_v1(fields['terminal_closure_condition'])}", "",
            f"Current auditing operation: {self._hot_value_v1(fields['latest_auditing_operation'])}", "",
            "## Action selection", "", "Selected current actions:",
        ]
        lines.extend(f"- {self._hot_value_v1(row)}" for row in fields["action_selected"])
        lines.extend(["", "Omitted current actions:"])
        lines.extend(f"- {self._hot_value_v1(row)}" for row in fields["action_omitted"])
        lines.extend([
            "", f"Depth rationale: {self._hot_value_v1(fields['action_depth_rationale'])}", "",
            "## Baseline ref", "", f"`{self._hot_value_v1(fields['baseline_ref'])}`", "",
            "## Run root", "",
            f"IMPLEMENTAUDIT_BASE: {self._hot_value_v1(fields['implementaudit_base'])}", "",
            f"IMPLEMENTAUDIT_RUN_ROOT: {self._hot_value_v1(fields['implementaudit_base'])}/{self._hot_value_v1(fields['run_id'])}", "",
            f"IMPLEMENTAUDIT_BASELINE_REF: {self._hot_value_v1(fields['baseline_ref'])}", "",
            f"Canonical projection generation: {self._hot_value_v1(fields['current_epoch'])}", "",
            f"Current-generation pointer: `{custody.current_generation_ref}@{custody.pointer_oid}`", "",
            "Migration marker: not published by migration-only projection", "",
            "Current continuity receipt: query on demand", "",
            "## Planning evidence", "", "Current pointers only:",
        ])
        lines.extend(f"- {self._hot_value_v1(row)}" for row in fields["planning_evidence"])
        lines.extend([
            f"- Exact archive: `{custody.archive_ref}` at `{custody.archive_digest}`",
            f"- History query: `{custody.history_query}`",
            "", "## Phases", "",
            "| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |",
            "|---|---|---|---|---|---|---|---|",
        ])
        for index, node in enumerate(graph.active_nodes, 1):
            lines.append(f"| {index} | {self._hot_value_v1(node)} | {self._hot_value_v1(fields['controller_id'])} | - | captured | pending | not applicable | {self._hot_value_v1(fields['status'])} |")
        lines.extend([
            "", "## Execution index (projection)", "",
            f"- Current graph: `{graph.work_graph_path}` at `{graph.work_graph_digest}`",
            f"- Generation pointer: `{custody.current_generation_ref}@{custody.pointer_oid}`",
            f"- Generation manifest digest: `{custody.manifest_digest}`",
            "", "## Scope boundaries", "",
        ])
        lines.extend(f"- {self._hot_value_v1(row.subject)}"
                     for row in fields["active_instructions"])
        lines.extend(["", "## Scope-creep register", "",
                      "| # | Issue | Location | Recommendation | Status |",
                      "|---|---|---|---|---|"])
        for row in fields["open_scope_creep"]:
            lines.append("| %s | %s | %s | %s | %s |" % row)
        return self._render_lines_v1(lines)
