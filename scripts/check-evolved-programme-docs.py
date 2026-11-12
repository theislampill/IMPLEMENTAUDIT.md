#!/usr/bin/env python3
"""Check the versioned documentary projection without adjudicating the science."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


PROGRAMME = Path("docs/research/genealogy/current-programme/v1/PROGRAMME.json")
FIXTURE = Path("fixtures/public-projection/evolved-programme-v1.json")
INTEGRATION = Path("docs/research/implementaudit/evolved-programme-v1")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ACCEPTED_VERDICTS = {"ACCEPT", "ACCEPTED_AT_DECLARED_SCOPE", "ACCEPT_WITH_NONMATERIAL_ERRATUM"}
PROGRAMME_REFERENCE = "../../genealogy/current-programme/v1/PROGRAMME.json"
PRIVATE_LOCATION = re.compile(r"(?:/workspace/|/home/agent/|libfile_|oai-library://|[?&](?:sig|token|X-Amz-Signature)=)", re.I)


def load(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def validate(programme: dict, fixture: dict) -> list[str]:
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(programme.get("schema") == "implementaudit.evolved-programme-documentation.v1", "programme schema")
    require(programme.get("counts") == {"families": 8, "lineages": 24, "syntheses": 8, "scientific_units": 32, "potential_integration_responsibilities": 32}, "scientific unit denominators")
    original = programme.get("historical_original_corpus", {})
    require([original.get(k) for k in ("families", "lineages", "property_rows")] == [4, 12, 658], "historical original corpus was relabelled")
    units = programme.get("units", [])
    require([u.get("unit_id") for u in units] == fixture["unit_order"], "32 unique ordered scientific identities")
    by_id = {u.get("unit_id"): u for u in units}
    require(len(by_id) == 32, "duplicate or missing unit")
    lineage_total = 0
    for unit in units:
        uid = unit.get("unit_id", "")
        require(unit.get("name") == fixture["unit_names"].get(uid), f"{uid}: canonical name/ordinal drift")
        require(unit.get("family") == uid.split("-")[0], f"{uid}: family drift")
        is_lineage = "-L" in uid
        require(unit.get("kind") == ("lineage" if is_lineage else "synthesis"), f"{uid}: lineage/synthesis conflation")
        if is_lineage:
            require(unit.get("historical_property_rows") == fixture["historical_lineage_rows"].get(uid), f"{uid}: original denominator drift")
            lineage_total += unit.get("historical_property_rows", 0)
        require(unit.get("native_implementation_credit") is False, f"{uid}: science promoted to runtime")
        require(unit.get("source_access") == "private_custody_metadata_only", f"{uid}: protected source access misrepresented")
        require(unit.get("body_publication_clearance") == "not_verified_do_not_publish", f"{uid}: publication clearance changed without a new version")
        status = unit.get("scientific_status")
        require(status in {"qualified_at_declared_scope", "unfinished", "historical_qualified_outcome_preserved_receipts_missing"}, f"{uid}: unknown scientific status")
        if status == "qualified_at_declared_scope":
            subject = unit.get("frozen_subject") or {}
            qualification = unit.get("qualification_receipt") or {}
            require(bool(HEX64.fullmatch(subject.get("sha256", ""))), f"{uid}: missing subject identity")
            require(bool(HEX64.fullmatch(qualification.get("sha256", ""))), f"{uid}: missing qualification identity")
            reviews = unit.get("accepted_reviews", [])
            require(len(reviews) == 2 and {r.get("role") for r in reviews} == {"fidelity", "adversarial"}, f"{uid}: missing distinct review roles")
            require(len({(r.get("receipt") or {}).get("sha256") for r in reviews}) == 2, f"{uid}: repeated receipt is not two reviews")
            for review in reviews:
                require(review.get("accepted_subject_sha256") == subject.get("sha256"), f"{uid}: review bound to another subject")
                require(bool(HEX64.fullmatch((review.get("receipt") or {}).get("sha256", ""))), f"{uid}: missing review identity")
                require(review.get("receipt_bytes_verified") is True, f"{uid}: unverified review promoted")
                require(review.get("reported_verdict") in ACCEPTED_VERDICTS, f"{uid}: nonaccepting review promoted")
        elif status == "unfinished":
            require(unit.get("qualification_receipt") is None and not unit.get("accepted_reviews"), f"{uid}: unfinished unit has implied final acceptance")
        if unit.get("qualification_origin") == "local_cohort_B":
            require(unit.get("central_selection") == "not_observed_for_this_newer_local_synthesis", f"{uid}: local qualification promoted to central application")
    require(lineage_total == programme.get("historical_all_lineage_property_rows") == 1629, "historical rows double-counted or changed")
    families = programme.get("families", [])
    require([f.get("family") for f in families] == fixture["families"], "eight-family population/order")
    complete = []
    for family in families:
        fid = family["family"]
        ids = [f"{fid}-L{i}" for i in range(1, 4)] + [f"{fid}-S"]
        require(family.get("lineages") == ids[:3] and family.get("synthesis") == ids[3], f"{fid}: four-unit composition")
        if not all(key in by_id for key in ids):
            continue
        members = [by_id[key] for key in ids]
        original_sum = sum(u["historical_property_rows"] for u in members[:3])
        require(original_sum == family.get("historical_lineage_property_rows") == members[3]["historical_property_rows"], f"{fid}: synthesis is not a fourth added property population")
        actual_complete = all(u.get("scientific_status") == "qualified_at_declared_scope" and u.get("subject_receiving") == "EXACT_BYTES_VERIFIED" and len(u.get("accepted_reviews", [])) == 2 for u in members)
        require(family.get("complete_scientific_receipt_set_received") is actual_complete, f"{fid}: incomplete receiving promoted")
        require(family.get("authoritative_native_integration") == "not_granted", f"{fid}: documentary receiving granted native integration")
        if actual_complete:
            complete.append(fid)
    require(set(complete) == set(fixture["expected_complete_receiving"]), "complete-family documentary population drift")
    if "SPR-L1" in by_id:
        spr = by_id["SPR-L1"]
        require(spr.get("scientific_status") == "historical_qualified_outcome_preserved_receipts_missing" and spr.get("qualification_receipt") is None and not spr.get("accepted_reviews"), "SPR-L1 missing original proof concealed")
    for key in ("SPR-L2", "SPR-L3"):
        if key in by_id:
            require(by_id[key].get("subject_receiving") == "DESCRIPTOR_VERIFIED_BYTES_NOT_ACQUIRED_IN_THIS_LANE", f"{key}: descriptor silently became acquired bytes")
    disclosure = programme.get("disclosure", {})
    require(disclosure.get("protected_bodies_included") is False and disclosure.get("private_source_or_download_locations_included") is False, "protected disclosure flags")
    require(not PRIVATE_LOCATION.search(json.dumps(programme)), "private location in public programme")
    require(programme.get("received_snapshot_counts", {}).get("central_totals_recomputed_by_C") is False, "C recomputed central qualification")
    return errors


def validate_integration(registry: dict, programme: dict, fixture: dict, root: Path) -> list[str]:
    errors = []
    rows = registry.get("rows", [])
    if [row.get("scientific_unit_id") for row in rows] != fixture["unit_order"]:
        errors.append("integration map does not cover exact 32 units")
    if registry.get("executor_ready") is not False or registry.get("new_issues_authorized") is not False:
        errors.append("rough registry promoted to issued/executor-ready work")
    units = {u["unit_id"]: u for u in programme["units"]}
    for row in rows:
        uid = row["scientific_unit_id"]
        if uid not in units:
            errors.append(f"{uid}: unknown scientific unit")
            continue
        if row.get("scientific_unit_name") != units[uid]["name"] or row.get("scientific_status") != units[uid]["scientific_status"]:
            errors.append(f"{uid}: scientific/integration map mismatch")
        if row.get("outline_status") != "ROUGH_ONLY_NOT_EXECUTOR_READY" or row.get("proven_current_native_defect") is not False:
            errors.append(f"{uid}: rough candidate promoted to a proved defect")
        if row.get("programme_identity_source") != PROGRAMME_REFERENCE:
            errors.append(f"{uid}: programme identity source is not the public registry")
        for target in [row.get("programme_identity_source", ""), *row.get("sources", [])]:
            if re.match(r"https?://", target):
                continue
            local = (root / INTEGRATION / target.split("#", 1)[0]).resolve()
            if not target or not local.is_relative_to(root.resolve()) or not local.is_file():
                errors.append(f"{uid}: broken local registry source {target}")
    return errors


def check_files(root: Path, programme: dict, fixture: dict) -> list[str]:
    errors = []
    site = load(root / "docs/portal/site.json")
    nav = [p for g in site["nav"] for p in g["pages"]]
    for page_id in fixture["expected_public_pages"]:
        if nav.count(page_id) != 1:
            errors.append(f"{page_id}: missing or repeated navigation")
            continue
        page = site["pages"][page_id]
        if PROGRAMME.as_posix() not in page["sources"]:
            errors.append(f"{page_id}: missing programme source binding")
    registry = load(root / INTEGRATION / "RLGWO_REGISTRY.json")
    errors.extend(validate_integration(registry, programme, fixture, root))
    files = list((root / PROGRAMME.parent).rglob("*.md")) + list((root / INTEGRATION).glob("*.md"))
    files += [root / PROGRAMME, root / INTEGRATION / "RLGWO_REGISTRY.json"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        if PRIVATE_LOCATION.search(text):
            errors.append(f"{path.relative_to(root)}: private location in public file")
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            local = target.split("#", 1)[0]
            if local and not (path.parent / local).resolve().exists():
                errors.append(f"{path.relative_to(root)}: broken local source link {target}")
    return errors


def negative_controls(programme: dict, fixture: dict, root: Path) -> int:
    def missing_unit(data): data["units"].pop()
    def duplicate_ordinal(data): data["units"][0]["name"] = data["units"][1]["name"]
    def bad_denominator(data): data["historical_all_lineage_property_rows"] += 1629
    def wrong_subject(data): data["units"][0]["accepted_reviews"][0]["accepted_subject_sha256"] = "0" * 64
    def missing_review(data): data["units"][0]["accepted_reviews"].pop()
    def runtime_upgrade(data): data["units"][0]["native_implementation_credit"] = True
    def central_upgrade(data): next(u for u in data["units"] if u["unit_id"] == "CSS-S")["central_selection"] = "selected"
    def false_complete(data): next(f for f in data["families"] if f["family"] == "SPR")["complete_scientific_receipt_set_received"] = True
    def private_location(data): data["disclosure"]["unsafe_locator"] = "/workspace/private/body.json"
    def negated_acceptance(data): data["units"][0]["accepted_reviews"][0]["reported_verdict"] = "NOT_ACCEPTED_AT_DECLARED_SCOPE"
    def rejected_acceptance(data): data["units"][0]["accepted_reviews"][0]["reported_verdict"] = "REJECTED_NO_ACCEPTANCE"
    mutations = [missing_unit, duplicate_ordinal, bad_denominator, wrong_subject, missing_review, runtime_upgrade, central_upgrade, false_complete, private_location, negated_acceptance, rejected_acceptance]
    for mutation in mutations:
        changed = copy.deepcopy(programme)
        mutation(changed)
        if not validate(changed, fixture):
            raise ValueError(f"negative control unexpectedly accepted: {mutation.__name__}")
    registry = load(root / INTEGRATION / "RLGWO_REGISTRY.json")
    for field, target in (("programme_identity_source", "../science/REGISTRY_32_UNITS.json"), ("programme_identity_source", "AUDIT.md"), ("sources", "missing-source.json")):
        changed = copy.deepcopy(registry)
        changed["rows"][0][field] = [target] if field == "sources" else target
        if not validate_integration(changed, programme, fixture, root):
            raise ValueError(f"negative registry-source control unexpectedly accepted: {field}={target}")
    return len(mutations) + 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        programme = load(args.root / PROGRAMME)
        fixture = load(args.root / FIXTURE)
        errors = validate(programme, fixture)
        if not errors:
            errors.extend(check_files(args.root, programme, fixture))
        if errors:
            for error in errors:
                print(f"evolved-programme-docs: FAIL: {error}")
            return 1
        controls = negative_controls(programme, fixture, args.root) if args.self_test else 0
        print(f"evolved-programme-docs: PASS: 8 families, 32 scientific units, 32 rough responsibilities; negative controls={controls}; no scientific requalification")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"evolved-programme-docs: FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
