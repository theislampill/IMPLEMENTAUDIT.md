#!/usr/bin/env bash
set -euo pipefail

# Andon class-list consistency contract (#1): the abnormality class
# enumeration is duplicated across SKILL.md, templates/PROTOCOL.md, and
# references/transcript-contract.md. This test pins the three lists to one
# another (set equality) and asserts required membership of all thirteen
# official classes — WITHOUT asserting a fixed total, so future additions
# extend REQUIRED rather than break structurally. It also pins the boundary
# fixtures that make the new classes' discrimination rules testable.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then py=python;
elif command -v python3 >/dev/null 2>&1; then py=python3;
else echo "andon-class-contract: python required" >&2; exit 1; fi

"$py" - <<'PY'
import re
import sys

REQUIRED = {
    "failed-criterion", "regression", "hung-command", "substituted-command",
    "owner-unclear", "generated-artifact-mismatch", "stale-sidecar",
    "policy-conflict", "impossible-criterion", "evidence-mismatch",
    "transport-infrastructure", "misplacement", "false-closure",
}

def fail(msg):
    print("andon-class-contract: " + msg)
    sys.exit(1)

# transcript-contract.md owns the canonical fenced list.
tc = open("skills/implementaudit/references/transcript-contract.md",
          encoding="utf-8").read()
m = re.search(r"```text\n(failed-criterion\n.*?)```", tc, re.S)
if not m:
    fail("canonical fenced class list not found in transcript-contract.md")
canonical = {ln.strip() for ln in m.group(1).splitlines() if ln.strip()}

# SKILL.md and PROTOCOL.md enumerate the same classes in prose.
def prose_set(path, text):
    found = {c for c in canonical | REQUIRED
             if re.search(r"(?<![\w-])" + re.escape(c) + r"(?![\w-])", text)}
    return found

sk = open("skills/implementaudit/SKILL.md", encoding="utf-8").read()
pr = open("skills/implementaudit/templates/PROTOCOL.md",
          encoding="utf-8").read()
sk_set = prose_set("SKILL.md", sk)
pr_set = prose_set("PROTOCOL.md", pr)

for name, got in (("SKILL.md", sk_set),
                  ("templates/PROTOCOL.md", pr_set),
                  ("references/transcript-contract.md", canonical)):
    if got != canonical:
        fail("%s class set diverges from canonical: missing=%s extra=%s"
             % (name, sorted(canonical - got), sorted(got - canonical)))

missing = REQUIRED - canonical
if missing:
    fail("required classes absent from canonical list: %s" % sorted(missing))

# Boundary discrimination fixtures: each pair's fixture rows must exist in
# the contract with the expected class, so classification behavior (not
# just the enumeration) is pinned.
fixtures = [
    ("0xC0000142", "transport-infrastructure"),
    ("responsive host", "hung-command"),
    ("wrong instance/copy", "misplacement"),
    ("wrong layer of a generator relationship", "generated-artifact-mismatch"),
    ("closure accounting", "false-closure"),
    ("unsupporting evidence", "evidence-mismatch"),
    ("no verdict", "transport-infrastructure"),
]
table = tc[tc.find("Boundary fixtures"):]
if "Boundary fixtures" not in tc:
    fail("boundary fixtures section missing from transcript-contract.md")
for marker, cls in fixtures:
    row = next((ln for ln in table.splitlines()
                if marker.lower() in ln.lower()), None)
    if row is None:
        fail("boundary fixture row for %r not found" % marker)
    if "`%s`" % cls not in row:
        fail("fixture row %r does not classify as %s" % (marker, cls))

# Reissue disposition for a blocked review channel must be normative.
flat = re.sub(r"\s+", " ", tc)
if "reissue" not in flat.lower() or "never treat a blocked review" not in flat:
    fail("blocked-review-channel disposition (preserve + reissue, never "
         "accept/reject) missing")

print("andon-class-contract: ok (%d classes, 3 files consistent, "
      "%d boundary fixtures)" % (len(canonical), len(fixtures)))
PY
