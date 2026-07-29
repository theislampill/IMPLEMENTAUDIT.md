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
import test_b3v4_freeze as b3_freeze_test
import test_candidate_matrix_freeze as matrix_freeze_test
import test_b3v4_campaign as b3_campaign_test
import test_candidate_matrix_campaign as matrix_campaign_test
import b3v4_rederive
import candidate_matrix_rederive


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected failure containing {fragment!r}")


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    except Exception as exc:
        raise AssertionError(
            f"owner rejection escaped as {type(exc).__name__}: {exc}") from exc
    raise AssertionError("invalid owner scalar accepted")


def expect_independent_invalid(module, action):
    try:
        action()
    except module.EvidenceInvalid:
        return
    except Exception as exc:
        raise AssertionError(
            f"independent owner rejection escaped as "
            f"{type(exc).__name__}: {exc}") from exc
    raise AssertionError("independent validator accepted invalid owner scalar")


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


def _entry(packet, role):
    return next(
        row for row in packet["evaluated_surfaces"]["entries"]
        if row["role"] == role)


def _semantic_owner_negative_matrix():
    validators = (
        (b3_freeze_test.valid_packet(),
         b3_freeze_test.load_validator(), surfaces.B3_CAMPAIGN),
        (matrix_freeze_test.valid_packet(),
         matrix_freeze_test.load_module(), surfaces.MATRIX_CAMPAIGN),
    )
    for packet, validator, campaign in validators:
        validator.validate_structure(packet)
        roles = packet["evaluated_surface_owners"]["roles"]

        missing = copy.deepcopy(packet)
        missing["evaluated_surface_owners"]["roles"].pop(
            next(iter(roles)))
        expect_error("coverage", lambda p=missing:
                     validator.validate_structure(p))

        extra = copy.deepcopy(packet)
        extra["evaluated_surface_owners"]["roles"]["not-a-role"] = {
            "kind": "frozen-not-a-role", "sha256": "a" * 64}
        expect_error("coverage", lambda p=extra:
                     validator.validate_structure(p))

        wrong_kind = copy.deepcopy(packet)
        wrong_kind["evaluated_surface_owners"]["roles"]["scorer"]["kind"] = \
            "packet-artifact-evaluator"
        expect_error("kind", lambda p=wrong_kind:
                     validator.validate_structure(p))

        swapped = copy.deepcopy(packet)
        owner_roles = swapped["evaluated_surface_owners"]["roles"]
        owner_roles["scorer"], owner_roles["evaluator"] = \
            owner_roles["evaluator"], owner_roles["scorer"]
        expect_error("kind", lambda p=swapped:
                     validator.validate_structure(p))

        # Owner and manifest cannot be mutually rebound to an arbitrary file.
        rebound = copy.deepcopy(packet)
        owner = rebound["evaluated_surface_owners"]["roles"][
            "prompt-template"]
        owner["path"] = "surface/arbitrary.bin"
        owner["sha256"] = "d" * 64
        row = _entry(rebound, "prompt-template")
        row["path"] = owner["path"]
        row["sha256"] = owner["sha256"]
        expect_error("path policy", lambda p=rebound:
                     validator.validate_structure(p))

        # A correct digest cannot be reassigned to the opposite semantic
        # product owner, even when the manifest is rebound with it.
        if campaign == surfaces.B3_CAMPAIGN:
            wrong_owner = copy.deepcopy(packet)
            candidate = wrong_owner["evaluated_surface_owners"]["roles"][
                "product-candidate"]
            candidate["path"] = "surface/control/SKILL.md"
            _entry(wrong_owner, "product-candidate")["path"] = \
                candidate["path"]
            expect_error("path policy", lambda p=wrong_owner:
                         validator.validate_structure(p))

        # Canonical packet projections are not caller-authored blobs. Extra,
        # reordered, or coercively changed bytes cannot be legalized by
        # rebinding the manifest digest.
        projected = copy.deepcopy(packet)
        raw = surfaces.projection_bytes(
            projected, campaign, "acceptance-rules")
        noncanonical = b'{ "extra":true, "projection":' + raw + b"}\n"
        row = _entry(projected, "acceptance-rules")
        row["byte_length"] = len(noncanonical)
        row["sha256"] = hashlib.sha256(noncanonical).hexdigest()
        expect_error("owner/manifest", lambda p=projected:
                     validator.validate_structure(p))

        substituted = copy.deepcopy(packet)
        other = matrix_freeze_test.valid_packet() \
            if campaign == surfaces.B3_CAMPAIGN else \
            b3_freeze_test.valid_packet()
        substituted["evaluated_surface_owners"] = copy.deepcopy(
            other["evaluated_surface_owners"])
        expect_error("campaign", lambda p=substituted:
                     validator.validate_structure(p))

        # Every closed owner class rejects every non-string JSON scalar before
        # comparison, regex, path, or string operations.
        exemplars = (
            ("acceptance-rules", ("kind",)),
            ("artifact-contract", ("kind",)),
            ("scorer", ("kind", "artifact", "git_commit", "git_tree")),
            (next(role for role in roles if role.startswith("fixture-")),
             ("kind", "fixture_id")),
            ("independent-rederiver",
             ("kind", "git_commit", "git_tree")),
            ("native-executable", ("kind",)),
            ("product-candidate", ("kind", "packet_owner", "path")),
            ("host-attestation", ("kind", "path")),
            ("adapter", ("kind", "sha256", "git_commit", "git_tree")),
            ("prompt-template", ("kind", "path", "sha256")),
        )
        independent = (
            b3v4_rederive if campaign == surfaces.B3_CAMPAIGN
            else candidate_matrix_rederive)
        for role, fields in exemplars:
            for field in fields:
                for scalar in (True, 7, None, [], {}):
                    malformed = copy.deepcopy(packet)
                    malformed["evaluated_surface_owners"]["roles"][role][
                        field] = scalar
                    expect_value_error(
                        lambda p=malformed: validator.validate_structure(p))
                    expect_independent_invalid(
                        independent,
                        lambda p=malformed, m=independent:
                        m._validate_freeze_contract(p))

        with tempfile.TemporaryDirectory(
                prefix="virtual-projection-shadow-") as tmp:
            shadow_root = pathlib.Path(tmp)
            (shadow_root / "evaluated-surface-projections").mkdir()
            expect_error(
                "shadow or residue",
                lambda p=packet, c=campaign, r=shadow_root:
                surfaces.validate_packet_surfaces(p, c, root=r))
            expect_independent_invalid(
                independent,
                lambda p=packet, m=independent, r=shadow_root:
                m._validate_freeze_contract(p, r))


def _projection_publication_red():
    packet = b3_freeze_test.valid_packet()
    with tempfile.TemporaryDirectory(
            prefix="evaluated-projection-publication-") as tmp:
        base = pathlib.Path(tmp)
        root = base / "root"
        outside = base / "outside"
        root.mkdir()
        outside.mkdir()
        projection = root / "evaluated-surface-projections"

        if os.name == "nt":
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(projection), str(outside)],
                capture_output=True, text=True)
            if made.returncode:
                print("PROJECTION_PARENT_JUNCTION=SKIP")
            else:
                try:
                    expect_error(
                        "shadow or residue",
                        lambda: surfaces.build_manifest_from_packet(
                            copy.deepcopy(packet), surfaces.B3_CAMPAIGN,
                            root=root))
                    assert not tuple(outside.iterdir()), (
                        "projection rejection wrote outside the surface root")
                finally:
                    os.rmdir(projection)
                print("PROJECTION_PARENT_JUNCTION=PASS")

        try:
            projection.symlink_to(outside, target_is_directory=True)
        except OSError:
            print("PROJECTION_PARENT_SYMLINK=SKIP")
        else:
            try:
                expect_error(
                    "shadow or residue",
                    lambda: surfaces.build_manifest_from_packet(
                        copy.deepcopy(packet), surfaces.B3_CAMPAIGN, root=root))
                assert not tuple(outside.iterdir()), (
                    "symlink rejection wrote outside the surface root")
            finally:
                projection.unlink()
            print("PROJECTION_PARENT_SYMLINK=PASS")

        projection.mkdir()
        leaf = projection / "acceptance-rules.json"
        raw = surfaces.projection_bytes(
            packet, surfaces.B3_CAMPAIGN, "acceptance-rules")
        source = base / "hardlink-source.json"
        source.write_bytes(raw)
        os.link(source, leaf)
        expect_error(
            "shadow or residue",
            lambda: surfaces.build_manifest_from_packet(
                copy.deepcopy(packet), surfaces.B3_CAMPAIGN, root=root))
        assert source.read_bytes() == raw
        assert leaf.exists()
        print("PROJECTION_LEAF_HARDLINK=PASS")
        leaf.unlink()
        source.unlink()

        leaf.write_bytes(raw)
        expect_error(
            "shadow or residue",
            lambda: surfaces.build_manifest_from_packet(
                copy.deepcopy(packet), surfaces.B3_CAMPAIGN, root=root))
        assert leaf.read_bytes() == raw
        assert tuple(projection.iterdir()) == (leaf,)
        leaf.unlink()
        print("PROJECTION_LEAF_PREEXISTING=PASS")

        # Even an empty physical parent is a shadow of the virtual namespace.
        expect_error(
            "shadow or residue",
            lambda: surfaces.build_manifest_from_packet(
                copy.deepcopy(packet), surfaces.B3_CAMPAIGN, root=root))
        projection.rmdir()
        print("PROJECTION_EMPTY_PARENT_SHADOW=PASS")

        # A later retained-input rejection cannot leave projection residue
        # because the virtual entries have no filesystem publication step.
        rollback_root = base / "rollback-root"
        rollback_root.mkdir()
        expect_error(
            "cannot be read",
            lambda: surfaces.build_manifest_from_packet(
                copy.deepcopy(packet), surfaces.B3_CAMPAIGN,
                root=rollback_root))
        assert not (rollback_root / "evaluated-surface-projections").exists()
        print("PROJECTION_REJECTION_NO_RESIDUE=PASS")


def _projection_open_window_red():
    packet = b3_freeze_test.valid_packet()
    with tempfile.TemporaryDirectory(
            prefix="evaluated-projection-open-window-") as tmp:
        base = pathlib.Path(tmp)
        root = base / "root"
        outside = base / "outside"
        root.mkdir()
        outside.mkdir()
        projection = root / "evaluated-surface-projections"
        original_open = surfaces.os.open
        swapped = False

        def swap_inside_open(path, flags, *args, **kwargs):
            nonlocal swapped
            candidate = pathlib.Path(path)
            if candidate.parent == projection:
                swapped = True
                os.rmdir(projection)
                made = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(projection),
                     str(outside)], capture_output=True, text=True)
                assert made.returncode == 0, made.stderr
            return original_open(path, flags, *args, **kwargs)

        surfaces.os.open = swap_inside_open
        try:
            expect_error(
                "cannot be read",
                lambda: surfaces.build_manifest_from_packet(
                    copy.deepcopy(packet), surfaces.B3_CAMPAIGN, root=root))
            assert not swapped, (
                "virtual projection invoked a pathname open callback")
            assert not tuple(outside.iterdir()), (
                "swap inside pathname open wrote outside residue")
        finally:
            surfaces.os.open = original_open
            if projection.exists():
                os.rmdir(projection)
        print("PROJECTION_OPEN_WINDOW_ZERO_WRITE=PASS")


def main():
    evaluated_surface_forbidden = {
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
        forbidden = (
            evaluated_surface_forbidden
            if name == "evaluated_surfaces.py" else
            {"adapters", "hosts", "runner", "lib.scoring",
             "eval.lib.scoring"})
        assert not imports & forbidden, (name, imports & forbidden)
    print("EVALUATED_SURFACE_STATIC_BOUNDARY=PASS")
    _semantic_owner_negative_matrix()
    print("EVALUATED_SURFACE_SEMANTIC_OWNER_MATRIX=PASS")
    _projection_publication_red()
    if os.name == "nt":
        _projection_open_window_red()

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

        # Governing RED R4: distinct case spellings that open the same NTFS
        # file are one physical identity and cannot fill two roles.
        if os.name == "nt":
            case_target = root / "Case-Only-Surface.bin"
            case_target.write_bytes(b"one physical file\n")
            source = _files(root, surfaces.B3_CAMPAIGN)
            source[0]["path"] = case_target.name
            source[1]["path"] = case_target.name.swapcase()
            expect_error("physical alias", lambda:
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
                "--launch-readiness", str(root / "readiness.json"),
                "--launch-context", str(root / "launch-context.json"),
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
                driver_module.freeze.validate_structure = lambda packet: packet
                calls = []
                driver._validate_surfaces = lambda packet: calls.append(
                    packet["campaign"])
                driver.run_next()
                assert calls == [calls[0], calls[0], calls[0]]

    print("EVALUATED-SURFACES-PASS")


if __name__ == "__main__":
    main()
