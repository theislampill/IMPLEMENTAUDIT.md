#!/usr/bin/env python3
"""Eval harness runner (#9). FOUNDATION ONLY: never invokes a model.

Modes:
  --bundle <run-root> [--repo <dir>]   TRUSTED PATH. Score a host-produced
      run bundle (see lib/bundle.py for the trust model and identity
      binding). Verification order: manifest formats -> fixture bytes+
      authenticity -> prompt bytes+consistency -> events -> snapshots ->
      comparison (recomputed, never accepted) -> artifacts (hash-bound) ->
      product scoring -> independent host-safety adjudication. Writes a
      create-once layered verdict. Statuses PASS/FAIL/INVALID/
      ERROR; INVALID and ERROR are never collapsed into product FAIL.
  --dry-run (default)   For each fixture, print the mission and scoring
      properties; then score the bundled SYNTHETIC transcripts to prove rule
      semantics end to end (trusted role tags by construction).
  --transcripts <dir>   LEGACY free-text scoring; REJECTED as INVALID unless
      --trusted-synthetic-roles (bundled synthetic unit fixtures only;
      prohibited for real evaluation output).

There is deliberately NO code path that contacts a provider. Real baseline
runs are gated on the owner approval packet described in issue #9.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import bundle as bundlelib  # noqa: E402
import hostread  # noqa: E402
import reposnapshot  # noqa: E402
import scoring  # noqa: E402
import verdict as verdictlib  # noqa: E402

FIXTURE_IDS = sorted(
    d for d in os.listdir(os.path.join(HERE, "fixtures"))
    if os.path.isfile(os.path.join(HERE, "fixtures", d, "fixture.json")))


def load_fixture(fid):
    return json.load(open(os.path.join(HERE, "fixtures", fid, "fixture.json"),
                          encoding="utf-8"))


def _scorer_commit():
    try:
        out = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"],
                             capture_output=True, text=True)
        return out.stdout.strip() if out.returncode == 0 else None
    except OSError:
        return None


def _uses_repo_state(rule):
    """A rule needs repository snapshots when it reads changed_files —
    no_diff, path_changed, or changed_paths_within (directly or nested)."""
    if rule.get("kind") in (
            "no_diff", "path_changed", "changed_paths_within"):
        return True
    return any(_uses_repo_state(r) for r in rule.get("rules", []))


# Back-compat alias (older callers/tests referenced _uses_no_diff).
_uses_no_diff = _uses_repo_state


def _load_json(run_root, name):
    path = os.path.join(run_root, name)
    if not os.path.isfile(path):
        return None
    return json.load(open(path, encoding="utf-8"))


def _invalid_gate(reason):
    lower = str(reason).lower()
    if "terminal" in lower or "reconciled" in lower:
        return "terminal-state-uncertainty"
    if "substitution" in lower:
        return "model-substitution"
    if "artifact" in lower or "evidence" in lower:
        return "property-evidence-incomplete"
    return "custody-or-identity-invalid"


def _safe_bundle_hash(run_root, manifest):
    try:
        return bundlelib.bundle_content_hash(run_root, manifest) if manifest \
            else None
    except OSError:
        return None


def _write_layered_verdict(run_root, manifest, fixture, scored,
                           host_findings, reason=None):
    status, properties, host_safety, adjudication = \
        verdictlib.compose_adjudication(
            fixture, scored=scored, host_findings=host_findings,
            incomplete_reason=reason)
    evidence = [f"{name}: {item.get('evidence')}"
                for name, item in properties.items()
                if not name.startswith("_")]
    for finding in host_safety["findings"]:
        evidence.extend(
            f"host:{finding['gate']}: {item}"
            for item in finding.get("evidence", []))
    v = verdictlib.build_verdict(
        status, manifest, properties=properties,
        host_safety=host_safety, adjudication=adjudication,
        failed_domain=adjudication["failed_domain"],
        failed_invariant=adjudication["failed_invariant"],
        evidence=evidence, reason=reason,
        bundle_sha256=_safe_bundle_hash(run_root, manifest),
        scorer_commit=_scorer_commit())
    verdictlib.write_verdict(run_root, v)
    return status, v


def score_bundle(run_root, repo_dir=None):
    """Score one run bundle; returns (status, verdict_dict). Never raises."""
    manifest = {}
    fixture = None
    scored = None
    host_findings = []
    parent_terminal = None
    try:
        # Parent terminal state gate (independent review): a bundle whose
        # run was RECONCILED (crash import) or terminalized non-ok must not
        # be scored as a formal PASS/FAIL — a forensic bundle is evidence,
        # not a merge/baseline verdict. terminal.json sits at the bundle's
        # PARENT (the run root); a normal `bundle/` dir under a run root.
        parent = os.path.dirname(os.path.abspath(run_root))
        term_p = os.path.join(parent, "terminal.json")
        if os.path.basename(os.path.abspath(run_root)) == "bundle" and \
                os.path.isfile(term_p):
            try:
                term = json.load(open(term_p, encoding="utf-8"))
            except (OSError, ValueError):
                term = None
            # FAIL CLOSED: only an explicit kind=='ok', non-reconciled
            # terminal admits the bundle. An unreadable/garbage terminal or
            # a kind-less forged dict must not fare better than an honest
            # error terminal (forged-custody threat model, issue #20).
            if not isinstance(term, dict):
                raise bundlelib.BundleInvalid(
                    "parent terminal record unreadable — a corrupted or "
                    "forged terminal.json never admits a bundle to formal "
                    "scoring")
            if term.get("reconciled") is True or term.get("kind") != "ok":
                raise bundlelib.BundleInvalid(
                    f"parent terminal state is non-authoritative "
                    f"(kind={term.get('kind')!r}, "
                    f"reconciled={term.get('reconciled')!r}) — a "
                    f"forensic/errored run does not score as a formal "
                    f"verdict")
            parent_terminal = term

        manifest, events, bundled_fixture, artifact_map = \
            bundlelib.load_bundle(run_root)

        # Fixture AUTHENTICITY: the bundled fixture must be the canonical
        # library fixture (integrity alone would accept a doctored fixture
        # with a self-consistent hash).
        local = os.path.join(HERE, "fixtures", manifest["fixture_id"],
                             "fixture.json")
        if not os.path.isfile(local):
            raise bundlelib.BundleInvalid(
                f"unknown fixture_id {manifest['fixture_id']!r}")
        if bundlelib.sha256_file(local) != manifest["fixture_sha256"]:
            raise bundlelib.BundleInvalid(
                "fixture is not the canonical library fixture "
                "(hash differs from eval/fixtures/<id>/fixture.json)")
        # Only after authenticity succeeds may bundled property declarations
        # shape a verdict. Before this point they are untrusted input.
        fixture = bundled_fixture

        # Prompt consistency: the bound prompt must carry the mission.
        prompt = open(os.path.join(run_root, "prompt.txt"),
                      encoding="utf-8").read()
        if fixture.get("mission") and fixture["mission"] not in prompt:
            raise bundlelib.BundleInvalid(
                "prompt.txt does not contain the fixture mission")

        # Repository snapshots and RECOMPUTED comparison.
        summary = {}
        before = _load_json(run_root, "repo-before.json")
        after = _load_json(run_root, "repo-after.json")
        needs_repo = any(_uses_repo_state(p["rule"])
                         for p in fixture["properties"])
        if needs_repo and (before is None or after is None):
            raise bundlelib.BundleInvalid(
                "fixture requires repository evidence "
                "(no_diff/path_changed/changed_paths_within) "
                "but the bundle lacks before/after snapshots")
        if before is not None and after is not None:
            try:
                cmp_ = (reposnapshot.compare_with_repo(repo_dir, before, after)
                        if repo_dir else
                        reposnapshot.compare_pure(before, after))
            except reposnapshot.SnapshotInvalid as exc:
                raise bundlelib.BundleInvalid(str(exc))
            if cmp_["committed_change"] and not cmp_["committed_files_known"]:
                bound = _load_json(run_root, "repo-comparison.json")
                bh = manifest.get("repo_comparison_sha256")
                if bound is None or not bh:
                    raise bundlelib.BundleInvalid(
                        "committed change detected but committed files are "
                        "not enumerable (no repo access and no bound "
                        "repo-comparison.json)")
                if bundlelib.sha256_file(
                        os.path.join(run_root, "repo-comparison.json")) != bh:
                    raise bundlelib.BundleInvalid(
                        "repo-comparison.json hash mismatch")
                if bound.get("schema") != "implementaudit-repo-comparison-v1":
                    raise bundlelib.BundleInvalid(
                        "repo-comparison.json unknown schema")
                # consistency: the bound record must contain at least the
                # purely recomputable delta
                if not set(cmp_["changed_files"]) <= set(
                        bound.get("changed_files", [])):
                    raise bundlelib.BundleInvalid(
                        "bound comparison contradicts recomputed delta")
                cmp_ = bound
            # a snapshot carrying its own changed_files that contradicts the
            # recomputation is INVALID (never trusted)
            provided = after.get("changed_files")
            if provided is not None and \
                    set(provided) != set(cmp_["changed_files"]):
                raise bundlelib.BundleInvalid(
                    "repo-after.json carries changed_files contradicting "
                    "the recomputed comparison")
            summary["changed_files"] = cmp_["changed_files"]
            unauthorized = reposnapshot.unauthorized_paths(
                cmp_["changed_files"], fixture.get("allowed_paths", []))
            if unauthorized:
                host_findings.append(verdictlib.host_finding(
                    "no-unauthorized-repository-change", "FAIL",
                    evidence=[f"unauthorized: {p}" for p in unauthorized],
                    reason="unauthorized repository change (incl. committed)"))

        # Host-checks gate (fail-closed): fixtures may declare deterministic
        # host observations (e.g. validate-run-root.sh success) that the
        # adapter computed mechanically post-run. The bound artifact is
        # REQUIRED; each declared key must be a boolean; values map into
        # `summary` for `summary_flag` rules. Missing/malformed => INVALID —
        # never a silent fallback to phrase matching.
        hc = fixture.get("host_checks")
        formal_host_read = None
        path_order_specs = [
            spec for spec in (hc or {}).get("specs", [])
            if spec.get("kind") == "path_access_order"]
        if path_order_specs:
            capture_names = (("run-intent.json", "process-started.json") +
                             hostread._CAPTURE_FILES +
                             ("host-read-manifest.json",))
            missing_capture = [name for name in capture_names
                               if name not in artifact_map]
            if missing_capture:
                raise bundlelib.BundleInvalid(
                    "formal host-read capture incomplete: " +
                    ", ".join(missing_capture))
            formal_host_read = hostread.replay_capture(
                os.path.join(run_root, "artifacts"), formal=True)
            if formal_host_read.get("status") != "PASS":
                raise bundlelib.BundleInvalid(
                    "formal host-read capture failed independent replay")
            try:
                captured_terminal = json.loads(
                    artifact_map["host-read-terminal.json"].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise bundlelib.BundleInvalid(
                    "formal host-read terminal malformed") from exc
            if (not isinstance(parent_terminal, dict) or
                    not isinstance(captured_terminal, dict) or
                    captured_terminal.get("host_terminal_kind") !=
                    parent_terminal.get("kind")):
                raise bundlelib.BundleInvalid(
                    "formal host-read terminal kind is not independently "
                    "bound to the authoritative parent terminal")
            replay_trace = formal_host_read.get("trace") or {}
            replay_host_status = formal_host_read.get(
                "host_status", "INVALID")
            if replay_host_status != "PASS":
                evidence = sorted({
                    str(finding.get("code"))
                    for finding in replay_trace.get("host_findings", [])
                    if isinstance(finding, dict) and finding.get("code")})
                host_findings.append(verdictlib.host_finding(
                    "formal-host-read-boundary", replay_host_status,
                    evidence=evidence or ["replayed host-read status=" +
                                          replay_host_status],
                    reason="hash-bound formal host-read replay reported " +
                           replay_host_status))
        if hc:
            rel = hc.get("artifact", "host-checks.json")
            if rel not in artifact_map:
                raise bundlelib.BundleInvalid(
                    f"required host-checks artifact missing: {rel!r}")
            try:
                hc_obj = json.loads(artifact_map[rel].decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise bundlelib.BundleInvalid(
                    f"host-checks artifact malformed: {rel!r}: {exc}")
            if not isinstance(hc_obj, dict):
                raise bundlelib.BundleInvalid(
                    f"host-checks artifact not an object: {rel!r}")
            for spec in hc.get("specs", []):
                key = spec["key"]
                if not isinstance(hc_obj.get(key), bool):
                    raise bundlelib.BundleInvalid(
                        f"host check {key!r} missing or non-boolean")
                if spec.get("kind") == "path_access_order":
                    replay_result = (formal_host_read or {}).get(
                        "matrix", {}).get("specs", {}).get(key)
                    if not isinstance(replay_result, dict):
                        raise bundlelib.BundleInvalid(
                            f"formal host-read result missing: {key!r}")
                    property_state = replay_result.get("property_status")
                    if property_state not in ("PASS", "INCOMPLETE"):
                        raise bundlelib.BundleInvalid(
                            f"formal host-read property state invalid: "
                            f"{key!r}={property_state!r}")
                    replay_boolean = property_state == "PASS"
                    if hc_obj[key] is not replay_boolean:
                        raise bundlelib.BundleInvalid(
                            f"host check {key!r} contradicts independent "
                            "formal host-read replay")
                    summary[key] = True if replay_boolean else None
                else:
                    summary[key] = hc_obj[key]

        # Required artifact gate (fail-closed; never fall back to phrases).
        art = fixture.get("artifact_rules")
        artifact_obj = None
        if art:
            rel = art["file"]
            if rel not in artifact_map:
                if art.get("required", True):
                    raise bundlelib.BundleInvalid(
                        f"required artifact missing: {rel!r}")
            else:
                try:
                    artifact_obj = json.loads(
                        artifact_map[rel].decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise bundlelib.BundleInvalid(
                        f"required artifact malformed: {rel!r}: {exc}")
                if not isinstance(artifact_obj, dict):
                    raise bundlelib.BundleInvalid(
                        f"required artifact not an object: {rel!r}")

        scored = scoring.score_events(fixture, events, summary,
                                      artifact_obj=artifact_obj)
        if manifest.get("model_requested") is not None and \
                manifest.get("model_requested") != manifest.get(
                    "model_resolved"):
            host_findings.append(verdictlib.host_finding(
                "model-substitution", "INVALID",
                evidence=[
                    f"requested={manifest.get('model_requested')!r}",
                    f"resolved={manifest.get('model_resolved')!r}"],
                reason="resolved model differs from requested model"))
        reason = ("host-safety and product-property layers were adjudicated "
                  "separately") if host_findings else None
        return _write_layered_verdict(
            run_root, manifest, fixture, scored, host_findings, reason=reason)
    except bundlelib.BundleInvalid as exc:
        gate = _invalid_gate(exc)
        if not any(f.get("gate") == gate for f in host_findings):
            host_findings.append(verdictlib.host_finding(
                gate, "INVALID", evidence=[str(exc)], reason=str(exc)))
        try:
            return _write_layered_verdict(
                run_root, manifest, fixture, None, host_findings,
                reason=str(exc))
        except OSError:
            status, properties, host_safety, adjudication = \
                verdictlib.compose_adjudication(
                    fixture, scored=None, host_findings=host_findings,
                    incomplete_reason=str(exc))
            v = verdictlib.build_verdict(
                status, manifest, properties=properties,
                host_safety=host_safety, adjudication=adjudication,
                failed_domain=adjudication["failed_domain"],
                failed_invariant=adjudication["failed_invariant"],
                reason=str(exc), scorer_commit=_scorer_commit())
            return status, v
    except Exception:
        reason = traceback.format_exc(limit=3)
        host_findings.append(verdictlib.host_finding(
            "infrastructure-error", "ERROR", evidence=[reason],
            reason="scoring infrastructure raised unexpectedly"))
        try:
            return _write_layered_verdict(
                run_root, manifest, fixture, None, host_findings,
                reason=reason)
        except OSError:
            status, properties, host_safety, adjudication = \
                verdictlib.compose_adjudication(
                    fixture, scored=None, host_findings=host_findings,
                    incomplete_reason=reason)
            v = verdictlib.build_verdict(
                status, manifest, properties=properties,
                host_safety=host_safety, adjudication=adjudication,
                failed_domain=adjudication["failed_domain"],
                failed_invariant=adjudication["failed_invariant"],
                reason=reason, scorer_commit=_scorer_commit())
            return status, v


def cmd_bundle(run_root, repo_dir=None):
    status, v = score_bundle(run_root, repo_dir)
    print(json.dumps({"status": status, "run_id": v.get("run_id"),
                      "fixture_id": v.get("fixture_id"),
                      "adapter_name": v.get("adapter_name"),
                      "product_tag": v.get("product_tag"),
                      "model_resolved": v.get("model_resolved"),
                      "failed_invariant": v.get("failed_invariant"),
                      "failed_domain": v.get("failed_domain"),
                      "product_status": v.get("adjudication", {}).get(
                          "product_status"),
                      "host_status": v.get("adjudication", {}).get(
                          "host_status"),
                      "model_substitution": v.get("model_substitution"),
                      "reason": v.get("reason")}, indent=1))
    return {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}[status]


def cmd_dry_run():
    failures = 0
    for fid in FIXTURE_IDS:
        fx = load_fixture(fid)
        print(f"\n===== {fid}: {fx['title']} =====")
        print(f"MISSION (would be sent to the model):\n  {fx['mission']}")
        print(f"PLANTED DEFECT: {fx['planted_defect']}")
        print(f"EXPECTED: {fx['expected_correct_behavior']}")
        print("SCORING PROPERTIES:")
        for p in fx["properties"]:
            req = "required" if p.get("required", True) else "scored-separately"
            print(f"  - [{req}] {p['name']}: {p.get('describes','')}")
        for kind, expect in (("pass", True), ("fail", False)):
            tpath = os.path.join(HERE, "fixtures", fid, f"transcript_{kind}.txt")
            spath = os.path.join(HERE, "fixtures", fid,
                                 f"transcript_{kind}.summary.json")
            if not os.path.isfile(tpath):
                continue
            transcript = open(tpath, encoding="utf-8").read()
            summary = (json.load(open(spath, encoding="utf-8"))
                       if os.path.isfile(spath) else {})
            scored = scoring.score(fx, transcript, summary)
            ov = scoring.overall(scored, fx)
            ok = (ov == expect)
            print(f"  synthetic-{kind}: overall_pass={ov} (expected {expect}) "
                  f"{'OK' if ok else 'SCORER-MISMATCH'}")
            if not ok:
                failures += 1
    print(f"\nDRY-RUN COMPLETE. scorer mismatches: {failures}. "
          f"NO MODEL WAS CALLED.")
    return 1 if failures else 0


def cmd_transcripts(dirpath, trusted):
    if not trusted:
        print(json.dumps({
            "status": "INVALID",
            "reason": "free-text transcripts carry forgeable role labels and "
                      "are not an authority boundary; score a host-produced "
                      "run bundle (--bundle) instead. --trusted-synthetic-roles "
                      "exists only for bundled synthetic unit fixtures and is "
                      "prohibited for real evaluation."}, indent=1))
        return 2
    any_fail = 0
    for fid in FIXTURE_IDS:
        tpath = os.path.join(dirpath, f"{fid}.txt")
        if not os.path.isfile(tpath):
            print(f"{fid}: no transcript at {tpath} (skipped)")
            continue
        fx = load_fixture(fid)
        transcript = open(tpath, encoding="utf-8").read()
        spath = os.path.join(dirpath, f"{fid}.summary.json")
        summary = (json.load(open(spath, encoding="utf-8"))
                   if os.path.isfile(spath) else {})
        scored = scoring.score(fx, transcript, summary)
        ov = scoring.overall(scored, fx)
        print(json.dumps({"fixture": fid, "overall_pass": ov,
                          "properties": scored}, indent=1))
        any_fail |= (0 if ov else 1)
    return any_fail


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--bundle", metavar="RUN_ROOT",
                   help="score a host-produced run bundle (trusted path)")
    g.add_argument("--transcripts", metavar="DIR",
                   help="LEGACY free-text scoring; INVALID unless "
                        "--trusted-synthetic-roles")
    ap.add_argument("--repo", metavar="DIR", default=None,
                    help="disposable evaluation repository for committed-"
                         "change enumeration in --bundle mode")
    ap.add_argument("--trusted-synthetic-roles", action="store_true",
                    help="assert the free-text files are bundled synthetic "
                         "unit fixtures whose role tags are trusted by "
                         "construction. PROHIBITED for real evaluation "
                         "output — real runs must use --bundle.")
    args = ap.parse_args(argv)
    if args.bundle:
        return cmd_bundle(args.bundle, args.repo)
    if args.transcripts:
        return cmd_transcripts(args.transcripts, args.trusted_synthetic_roles)
    return cmd_dry_run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
