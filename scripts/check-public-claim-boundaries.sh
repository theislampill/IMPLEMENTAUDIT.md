#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-public-claim-boundaries: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" <<'PY'
import re
import sys
from pathlib import Path

blocked_dirs = {
    ".git",
    ".IMPLEMENTAUDIT",
    "dist",
    "docs/audits",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
}
binary_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".skill", ".ico", ".pdf"}

unsupported_claims = [
    ("verified " + "install", "host install verification claim requires current host evidence"),
    ("install " + "verified", "host install verification claim requires current host evidence"),
    ("marketplace " + "verified", "marketplace verification claim requires host evidence"),
    ("verified " + "marketplace", "marketplace verification claim requires host evidence"),
    ("auto-update", "auto-update claim requires a tested updater mechanism"),
    ("auto-updates", "auto-update claim requires a tested updater mechanism"),
    ("auto-install", "auto-install claim requires a tested installer/updater mechanism"),
    ("automatically update", "automatic update claim requires a tested updater mechanism"),
    ("universal host support", "universal host support claim requires host evidence"),
    ("published " + "package", "package publication claim requires release/publication evidence"),
    ("package publication " + "verified", "package publication claim requires release/publication evidence"),
    ("attestation " + "generated", "attestation claim requires an attestation artifact"),
    ("signed " + "release", "signing claim requires a signature artifact"),
    ("sbom " + "generated", "SBOM claim requires an SBOM artifact"),
    ("spdx " + "generated", "SPDX claim requires an SPDX artifact"),
    ("mit " + "license", "license claim requires a LICENSE file or owner-selected license evidence"),
    ("apache " + "license", "license claim requires a LICENSE file or owner-selected license evidence"),
]
stale_current_release_claims = [
    (
        "r0024 / #167 remains open and was not shipped or qualified in this release",
        "current release surfaces must not retain the pre-R0024 exclusion claim",
    ),
    (
        "do not replace bytes under an already-published tag",
        "release policy must preserve bounded owner-authorised same-identity correction",
    ),
    (
        "current release-gate-verified public release is `v0.3.3.0`",
        "current release claim must not pin the superseded v0.3.3.0 public release",
    ),
    (
        "release-gate verified live public release remains `v0.2.9.0`",
        "current release claim must not pin the prior public release",
    ),
    (
        "last release-gate verified live public release `v0.2.9.0`",
        "current release claim must not pin the prior public release",
    ),
    (
        "live public v0.2.9.0 release",
        "current release install example must not point at the prior public release",
    ),
    (
        "install-codex-from-release.sh --tag v0.2.9.0 --version 0.2.9",
        "current release install example must not point at the prior public release",
    ),
]
negative_context = (
    "do not claim",
    "does not claim",
    "must not",
    "do not",
    "does not",
    "does not claim",
    "not claim",
    "not automatically",
    "not auto-update",
    "no ",
    "without evidence",
    "unless actually",
    "unless tested",
    "not verified",
    "unverified",
    "is not a",
    "are not",
    "does not prove",
    "do not have",
    "rejected",
    "remains an owner decision",
)

if Path("LICENSE").exists():
    unsupported_claims = [
        item for item in unsupported_claims if "license claim" not in item[1]
    ]

failures = []

# W04 source-coupled public boundaries. These anchors are independent of the
# declarative projection fixture so source plus fixture co-mutation cannot turn
# a canonical-title, no-mode, or cheap-path reversal into a pass.
s3e_source_paths = {
    "s3e": Path("docs/portal/pages/research-lineage-s3e.html"),
    "css": Path("docs/portal/pages/research-lineage-evolved-css.html"),
    "reference-index": Path("docs/portal/pages/reference-index.html"),
}
s3e_source_anchors = {
    "canonical-title": (
        "s3e", "State Synthesis Substrate Engineering: Evolved-SSDDRFCSS"),
    "one-substrate-no-methodology-mode": (
        "s3e", "They do not create nine runtimes, selectable methodology modes, or a fixed ceremony."),
    "ordinary-work-cheap-path": (
        "css", "When one authoritative deterministic discriminator settles ordinary bounded work, use it and stop. No trigger means no added ceremony, record, or family machinery."),
    "current-package-projection-boundary": (
        "s3e", "The canonical plugin and standalone compatibility projections are mechanically checked independently; they are not literal member-for-member copies."),
    "reference-index-current-package-projection": (
        "reference-index", "independently checked package projections"),
}


def missing_s3e_source_anchors(text_by_owner):
    return [
        anchor_id for anchor_id, (owner, literal) in s3e_source_anchors.items()
        if owner not in text_by_owner or literal not in text_by_owner[owner]
    ]


s3e_source_text = {}
if any(not source.is_file() for source in s3e_source_paths.values()):
    failures.append("S³E public source owner is missing")
else:
    s3e_source_text = {
        key: source.read_text(encoding="utf-8")
        for key, source in s3e_source_paths.items()
    }
    missing = missing_s3e_source_anchors(s3e_source_text)
    if missing:
        failures.append(f"S³E public source anchor missing: {missing}")
    for anchor_id, (owner, literal) in s3e_source_anchors.items():
        mutated = dict(s3e_source_text)
        mutated[owner] = mutated[owner].replace(literal, "CORRUPTED", 1)
        if anchor_id not in missing_s3e_source_anchors(mutated):
            failures.append(f"S³E held-out source mutation false-passed: {anchor_id}")

stale_projection_patterns = (
    re.compile(r"\b\d+ archive members\b"),
    re.compile(r"\b\d+ Codex-installed payload files\b"),
    re.compile(r"\b\d+/\d+ package projection\b"),
)
for stale_projection_pattern in stale_projection_patterns:
    for owner, text in s3e_source_text.items():
        match = stale_projection_pattern.search(text)
        if match:
            failures.append(
                f"{s3e_source_paths[owner]}: stale package projection claim: "
                f"{match.group(0)}"
            )

readme_path = Path("README.md")
if not readme_path.is_file():
    failures.append("README.md is missing")
else:
    readme_flat = " ".join(readme_path.read_text(encoding="utf-8").split())
    required_public_tag_boundary = (
        "may the following public-tag form be treated as current; until then, "
        "use the locally qualified asset route shown above"
    )
    if required_public_tag_boundary not in readme_flat:
        failures.append(
            "README.md: prepublication local-asset guidance does not clearly "
            "separate the following post-publication URL command"
        )

# Proof-level discipline (#53, IA-PROOF-LEVELS): on active/current surfaces,
# verdict-class wording must carry a same-line proof-level qualification
# (docs/audits/RETENTION.md taxonomy PL1-PL7). docs/audits/archive/** is
# exempt history; docs/maintenance/** is retained historical rationale;
# claim-boundary negative fixtures are self-declared counter-examples.
proof_verdict_re = re.compile(
    r"\b(V0_\d+_\d+_\d+_[A-Z_]*PROVEN[A-Z_]*|PROVEN_WITH_WEAKNESSES|PROVEN|SURPASSED)\b"
)
proof_qualifier_re = re.compile(
    r"(?i)(proof[- ]level|\bPL[1-7]\b|source[- ]milestone|"
    r"structural (validation|evidence|only)|fixture[- ]demonstrat|"
    r"behaviorally observed|fresh-executor proven|not (yet )?(behaviorally|executor))"
)
proof_exempt_prefixes = (
    "docs/audits/archive/",
    "docs/maintenance/",
    "fixtures/claim-boundaries/negative-",
    "tests/claim-boundary-proof-levels.test.sh",
)


def check_proof_wording(path, text):
    posix = path.as_posix()
    if any(posix.startswith(prefix) for prefix in proof_exempt_prefixes):
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not proof_verdict_re.search(line):
            continue
        if proof_qualifier_re.search(line):
            continue
        if any(context in line.lower() for context in negative_context):
            continue
        failures.append(
            f"{posix}:{line_no}: verdict-class wording requires a same-line "
            f"proof-level qualification (docs/audits/RETENTION.md PL1-PL7): "
            f"{line.strip()[:100]}"
        )
portal_public_phrases = [
    ("complete glossary", "public portal must not frame runtime terminology as a glossary"),
    ("full terminology", "public portal must not frame runtime terminology as a glossary"),
    ("better " + "than x", "public portal must not frame capability as product-vs-product superiority"),
    ("beats every", "public portal must not frame capability as universal superiority"),
    ("defeats", "public portal must not frame capability as product-vs-product superiority"),
    ("sur" + "passes all", "public portal must not frame capability as universal superiority"),
]
current_reader_phrases = [
    ("three invocation shapes", "current reader docs must name four invocation shapes"),
    ("three valid invocation shapes", "current reader docs must name four invocation shapes"),
    ("three invocation modes", "current reader docs must name four invocation shapes"),
]
current_reader_paths = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("AGENTS.md"),
    Path("docs/portal/site.json"),
]
if Path("docs/portal/pages").is_dir():
    current_reader_paths.extend(
        p for p in sorted(Path("docs/portal/pages").rglob("*")) if p.is_file()
    )


def is_frozen_research_source(path):
    """Exact source material is evidence, not a live repository claim surface."""
    posix = path.as_posix()
    if not posix.startswith("docs/research/genealogy/"):
        return False
    return "/corpus/" in f"/{posix}" or posix.startswith(
        "docs/research/genealogy/method/source-prompts/"
    )

for path in current_reader_paths:
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8").lower()
    except UnicodeDecodeError:
        continue
    for phrase, reason in current_reader_phrases:
        for line_no, line in enumerate(text.splitlines(), start=1):
            if phrase in line:
                failures.append(f"{path}:{line_no}: {reason}: {phrase}")

for path in Path(".").rglob("*"):
    if not path.is_file():
        continue
    if path.as_posix() == "scripts/check-public-claim-boundaries.sh":
        continue
    if is_frozen_research_source(path):
        continue
    if len(path.parts) >= 2 and path.parts[0] == "docs" and path.parts[1] == "audits":
        continue
    if any(part in blocked_dirs for part in path.parts):
        continue
    if path.suffix.lower() in binary_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    lowered = text.lower()

    if len(path.parts) >= 3 and path.parts[0] == "docs" and path.parts[1] == "portal":
        for phrase, reason in portal_public_phrases:
            for line_no, line in enumerate(lowered.splitlines(), start=1):
                if phrase in line:
                    failures.append(f"{path}:{line_no}: {reason}: {phrase}")

    for phrase, reason in stale_current_release_claims:
        for line_no, line in enumerate(lowered.splitlines(), start=1):
            if phrase in line:
                failures.append(f"{path}:{line_no}: {reason}: {phrase}")

    for phrase, reason in unsupported_claims:
        for line_no, line in enumerate(lowered.splitlines(), start=1):
            if phrase in line and not any(context in line for context in negative_context):
                failures.append(f"{path}:{line_no}: {reason}: {phrase}")

    check_proof_wording(path, text)

# Active audit surfaces: INDEX.md and RETENTION.md are current/active pages
# (only docs/audits/archive/** is exempt history) — the proof-wording rule
# applies to them even though the legacy claim scans skip docs/audits.
for extra in (Path("docs/audits/INDEX.md"), Path("docs/audits/RETENTION.md")):
    if extra.is_file():
        check_proof_wording(extra, extra.read_text(encoding="utf-8"))

if failures:
    raise SystemExit("\n".join(failures))

sys.stdout.write("check-public-claim-boundaries: ok\n")
PY
