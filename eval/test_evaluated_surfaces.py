#!/usr/bin/env python3
"""Behavior tests for exact evaluated-surface custody and invalidation."""
from __future__ import annotations

import copy
import ast
import contextlib
import hashlib
import importlib.util
import io
import os
import pathlib
import subprocess
import tempfile

import evaluated_surfaces as surfaces
import test_b3v4_campaign as b3_campaign_test
import test_candidate_matrix_campaign as matrix_campaign_test


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected failure containing {fragment!r}")


def _files(root, campaign):
    rows = []
    for index, role in enumerate(surfaces.required_roles(campaign)):
        path = root / f"surface-{index:02d}.bin"
        path.write_bytes(f"{campaign}:{role}\n".encode())
        row = {"role": role, "path": path.name}
        if role in surfaces.GIT_IDENTITY_ROLES[campaign]:
            row.update({"git_commit": "a" * 40, "git_tree": "b" * 40})
        rows.append(row)
    return rows


def main():
    production_forbidden = {
        "adapters", "hosts", "runner", "b3v4_campaign", "b3v4_rederive",
        "candidate_matrix_campaign", "candidate_matrix_rederive",
        "validate_b3v4_freeze", "validate_candidate_matrix_freeze",
        "lib.scoring", "eval.lib.scoring",
    }
    for name in ("evaluated_surfaces.py", "provisional_integration.py"):
        tree = ast.parse(pathlib.Path(__file__).with_name(name).read_text(
            encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        assert not imports & production_forbidden, (
            name, imports & production_forbidden)
    print("EVALUATED_SURFACE_STATIC_BOUNDARY=PASS")

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        for campaign in surfaces.CAMPAIGNS:
            sources = _files(root, campaign)
            manifest = surfaces.build_manifest(campaign, sources, root=root)
            assert surfaces.validate_manifest(manifest, campaign) == manifest
            assert surfaces.revalidate_manifest(manifest, root=root) == manifest

            # Every declared family is mandatory, including products, every
            # fixture, scorer/evaluator/adapter, prompts, authorization,
            # seed/rules, contracts, rederiver, executable pair, and host proof.
            for index, role in enumerate(surfaces.required_roles(campaign)):
                changed = copy.deepcopy(manifest)
                changed["entries"].pop(index)
                expect_error(role, lambda c=changed:
                             surfaces.validate_manifest(c, campaign))

            duplicate_role = copy.deepcopy(manifest)
            duplicate_role["entries"][-1]["role"] = \
                duplicate_role["entries"][0]["role"]
            expect_error("duplicate role", lambda:
                         surfaces.validate_manifest(duplicate_role, campaign))

            duplicate_path = copy.deepcopy(manifest)
            duplicate_path["entries"][-1]["path"] = \
                duplicate_path["entries"][0]["path"]
            expect_error("duplicate path", lambda:
                         surfaces.validate_manifest(duplicate_path, campaign))
            coercive = copy.deepcopy(manifest)
            coercive["entries"][0]["byte_length"] = True
            expect_error("byte length", lambda:
                         surfaces.validate_manifest(coercive, campaign))
            extra_claim = copy.deepcopy(manifest)
            extra_claim["entries"][0]["accepted"] = True
            expect_error("fields", lambda:
                         surfaces.validate_manifest(extra_claim, campaign))

            escaped = copy.deepcopy(sources)
            outside = root.parent / f"outside-{campaign}.bin"
            outside.write_bytes(b"outside\n")
            escaped[0]["path"] = "../" + outside.name
            expect_error("escapes", lambda:
                         surfaces.build_manifest(campaign, escaped, root=root))
            outside.unlink()

            # Git history is advisory identity: equal bytes and owned paths
            # remain reusable when only commit/tree history changes.
            history_only = copy.deepcopy(manifest)
            git_role = next(iter(surfaces.GIT_IDENTITY_ROLES[campaign]))
            git_entry = next(row for row in history_only["entries"]
                             if row["role"] == git_role)
            git_entry["git_commit"] = "c" * 40
            git_entry["git_tree"] = "d" * 40
            assert surfaces.compare_relevant_surfaces(
                manifest, history_only, campaign) is True

            # Same commit or a merge/conflict history cannot conceal one byte
            # of relevant-surface drift.
            drifted = copy.deepcopy(history_only)
            row = drifted["entries"][0]
            row["byte_length"] += 1
            row["sha256"] = hashlib.sha256(b"different").hexdigest()
            expect_error("byte drift", lambda:
                         surfaces.compare_relevant_surfaces(
                             manifest, drifted, campaign))
            retained = root / manifest["entries"][0]["path"]
            original = retained.read_bytes()
            retained.write_bytes(original + b"post-manifest mutation\n")
            expect_error("byte drift", lambda:
                         surfaces.revalidate_manifest(manifest, root=root))
            retained.write_bytes(original)

        b3 = surfaces.build_manifest(
            surfaces.B3_CAMPAIGN, _files(root, surfaces.B3_CAMPAIGN),
            root=root)
        matrix = surfaces.build_manifest(
            surfaces.MATRIX_CAMPAIGN, _files(root, surfaces.MATRIX_CAMPAIGN),
            root=root)
        expect_error("campaign", lambda:
                     surfaces.compare_relevant_surfaces(
                         b3, matrix, surfaces.B3_CAMPAIGN))

        # Aliased retained bytes are not a unique evaluated identity.
        target = root / "hardlink-source.bin"
        target.write_bytes(b"hardlink\n")
        alias = root / "hardlink-alias.bin"
        os.link(target, alias)
        source = _files(root, surfaces.B3_CAMPAIGN)
        source[0]["path"] = alias.name
        expect_error("hardlink", lambda:
                     surfaces.build_manifest(
                         surfaces.B3_CAMPAIGN, source, root=root))

        symlink = root / "surface-symlink.bin"
        try:
            symlink.symlink_to(target)
        except OSError:
            print("EVALUATED_SURFACE_SYMLINK=SKIP")
        else:
            source = _files(root, surfaces.B3_CAMPAIGN)
            source[0]["path"] = symlink.name
            expect_error("link or reparse", lambda:
                         surfaces.build_manifest(
                             surfaces.B3_CAMPAIGN, source, root=root))
            print("EVALUATED_SURFACE_SYMLINK=PASS")

        if os.name == "nt":
            target_dir = root / "surface-junction-target"
            target_dir.mkdir()
            (target_dir / "payload.bin").write_bytes(b"junction\n")
            junction = root / "surface-junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction),
                 str(target_dir)], capture_output=True, text=True)
            if made.returncode:
                print("EVALUATED_SURFACE_JUNCTION=SKIP")
            else:
                try:
                    source = _files(root, surfaces.B3_CAMPAIGN)
                    role_index = next(
                        index for index, row in enumerate(source)
                        if row["role"] == "product-candidate")
                    source[role_index]["path"] = str(
                        junction / "payload.bin").replace("\\", "/")
                    expect_error("link or reparse", lambda:
                                 surfaces.build_manifest(
                                     surfaces.B3_CAMPAIGN, source, root=root))
                finally:
                    os.rmdir(junction)
                print("EVALUATED_SURFACE_JUNCTION=PASS")

        # The CLI must normalize the already-validated campaign ANDON marker;
        # it must not index it as an ordinary attempt terminal.
        campaign_path = pathlib.Path(__file__).with_name(
            "candidate_matrix_campaign.py")
        spec = importlib.util.spec_from_file_location(
            "matrix_campaign_cli_andon", campaign_path)
        campaign = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(campaign)

        class StoppedDriver:
            def __init__(self, **_kwargs):
                pass

            @staticmethod
            def run_next():
                return {
                    "schema":
                        "implementaudit-candidate-matrix-campaign-andon-v1",
                    "mission_index": 4,
                    "stop_reason": "terminal publication failed",
                }

        campaign.CampaignDriver = StoppedDriver
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = campaign.main([
                "run-next", "packet.json", "--repo-root", str(root),
                "--campaign-root", str(root / "campaign"),
                "--candidate-checkout", str(root / "candidate"),
                "--runtime-root", str(root / "runtime"),
                "--l-attestation", str(root / "attestation.json"),
            ])
        assert exit_code == 2
        assert output.getvalue() == (
            '{"mission_index": 4, "overall_status": "ERROR", '
            '"stop_reason": "terminal publication failed"}\n')

        for helper, load in (
                (b3_campaign_test, b3_campaign_test.load_driver),
                (matrix_campaign_test, matrix_campaign_test.load_module)):
            with tempfile.TemporaryDirectory() as driver_tmp:
                driver_module = load()
                driver = (
                    helper.make_driver(
                        driver_module, driver_tmp,
                        b3_campaign_test.sealed_probe_outcome)
                    if helper is b3_campaign_test else
                    helper.make_driver(driver_module, driver_tmp))
                calls = []
                driver._validate_surfaces = lambda packet: calls.append(
                    packet["campaign"])
                driver.run_next()
                assert calls == [calls[0], calls[0], calls[0]]

    print("EVALUATED-SURFACES-PASS")


if __name__ == "__main__":
    main()
