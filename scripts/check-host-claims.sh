#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-host-claims: %s\n' "$*" >&2
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
portal_public_phrases = [
    ("complete glossary", "public portal must not frame runtime terminology as a glossary"),
    ("full terminology", "public portal must not frame runtime terminology as a glossary"),
    ("external-comparator", "public portal must not use comparator framing"),
    ("external staged-goal comparator", "public portal must not use comparator framing"),
    ("staged-goal comparator", "public portal must not use comparator framing"),
    ("generic staged-goal runner", "public portal must not use comparator framing"),
    ("comparator adaptation", "public portal must not use comparator framing"),
]
current_reader_phrases = [
    ("three invocation shapes", "current reader docs must name four invocation shapes"),
    ("three valid invocation shapes", "current reader docs must name four invocation shapes"),
    ("three invocation modes", "current reader docs must name four invocation shapes"),
]
current_reader_paths = [
    Path("README.md"),
    Path("AGENTS.md"),
    Path("docs/portal/site.json"),
]
if Path("docs/portal/pages").is_dir():
    current_reader_paths.extend(
        p for p in sorted(Path("docs/portal/pages").rglob("*")) if p.is_file()
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
    if path.as_posix() == "scripts/check-host-claims.sh":
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

if failures:
    raise SystemExit("\n".join(failures))

print("check-host-claims: ok")
PY
