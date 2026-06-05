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
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
}
binary_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".skill", ".ico", ".pdf"}

legacy = "Super" + "goal"
legacy_lower = legacy.lower()
legacy_dir = "." + legacy_lower
memory_marker = "MEMORY" + "_SAVED"
child_file = "CHILD" + "_AGENTS.md"

forbidden_tokens = [
    (legacy, "forbidden external comparator identity"),
    (legacy_lower, "forbidden external comparator identity"),
    (legacy_dir, "forbidden external comparator artifact path"),
    (memory_marker, "user-memory-first learning marker is not an ImplementAudit repo contract"),
    (child_file, "nonstandard child-agent instruction filename must not be claimed canonical"),
    (child_file.lower(), "nonstandard child-agent instruction filename must not be claimed canonical"),
]

unsupported_claims = [
    ("verified " + "install", "host install verification claim requires current host evidence"),
    ("install " + "verified", "host install verification claim requires current host evidence"),
    ("marketplace " + "verified", "marketplace verification claim requires host evidence"),
    ("verified " + "marketplace", "marketplace verification claim requires host evidence"),
    ("published " + "package", "package publication claim requires release/publication evidence"),
    ("package publication " + "verified", "package publication claim requires release/publication evidence"),
    ("attestation " + "generated", "attestation claim requires an attestation artifact"),
    ("signed " + "release", "signing claim requires a signature artifact"),
    ("sbom " + "generated", "SBOM claim requires an SBOM artifact"),
    ("spdx " + "generated", "SPDX claim requires an SPDX artifact"),
    ("mit " + "license", "license claim requires a LICENSE file or owner-selected license evidence"),
    ("apache " + "license", "license claim requires a LICENSE file or owner-selected license evidence"),
]
negative_context = (
    "do not claim",
    "does not claim",
    "not claim",
    "no ",
    "without evidence",
    "unless actually",
    "unless tested",
    "not verified",
    "unverified",
    "is not a",
    "are not",
    "remains an owner decision",
)

if Path("LICENSE").exists():
    unsupported_claims = [
        item for item in unsupported_claims if "license claim" not in item[1]
    ]

failures = []
for path in Path(".").rglob("*"):
    if not path.is_file():
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

    for token, reason in forbidden_tokens:
        if token in text or token.lower() in lowered:
            failures.append(f"{path}: {reason}: {token}")
    for phrase, reason in unsupported_claims:
        for line_no, line in enumerate(lowered.splitlines(), start=1):
            if phrase in line and not any(context in line for context in negative_context):
                failures.append(f"{path}:{line_no}: {reason}: {phrase}")

if failures:
    raise SystemExit("\n".join(failures))

print("check-host-claims: ok")
PY
