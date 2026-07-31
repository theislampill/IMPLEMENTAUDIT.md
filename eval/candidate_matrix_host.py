#!/usr/bin/env python3
"""Matrix-only host policy layered on the shared Codex adapter.

The shared lifecycle stays unchanged. Matrix-specific policy materializes
prompt-bound fixture state and quarantines only files that actually contain a
credential shape, preserving non-sensitive create-once identity records.
"""
from __future__ import annotations

import json
import os
import pathlib

import candidate_matrix_fixture_setup as fixture_setup
import hosts


class MatrixCodexAdapter(hosts.CodexAdapter):
    def run_mission(self, fixture_id, *args, **kwargs):
        self._matrix_fixture_id = fixture_id
        return super().run_mission(fixture_id, *args, **kwargs)

    def stage_payload(self, repo):
        digest = super().stage_payload(repo)
        fixture_id = getattr(self, "_matrix_fixture_id", None)
        fixture = json.load(open(
            os.path.join(hosts.HERE, "fixtures", fixture_id, "fixture.json"),
            encoding="utf-8"))
        fixture_setup.prepare_fixture(
            fixture_id, pathlib.Path(repo), pathlib.Path(self.product_checkout),
            fixture.get("matrix_precondition"))
        return digest

    def _quarantine_if_leak(self, root, quarantine_name, only=None):
        if only is None:
            return super()._quarantine_if_leak(
                root, quarantine_name, only=only)
        hits = []
        for name in only:
            path = os.path.join(root, name)
            if not os.path.isfile(path):
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            pattern = next(
                (item for item in self._cred_patterns()
                 if item.search(text)), None)
            if pattern is not None:
                hits.append((pattern.pattern, name))
        if not hits:
            return None
        qdir = os.path.join(root, quarantine_name)
        os.makedirs(qdir, exist_ok=True)
        for _pattern, name in hits:
            source = os.path.join(root, name)
            destination = os.path.join(qdir, name)
            if os.path.lexists(destination):
                raise hosts.framework.AdapterError(
                    "credential quarantine destination already exists")
            os.replace(source, destination)
        return hits[0]
