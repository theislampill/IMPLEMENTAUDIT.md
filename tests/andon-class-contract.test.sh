#!/usr/bin/env bash
set -euo pipefail

# Andon class-list consistency contract (#1): the abnormality class
# enumeration is duplicated across SKILL.md, templates/PROTOCOL.md, and
# references/transcript-contract.md. This test pins the three lists to one
# another (set equality) and asserts required membership of all thirteen
# official classes — WITHOUT asserting a fixed total, so future additions
# extend REQUIRED rather than break structurally. It also pins the boundary
# fixtures that make the new classes' discrimination rules testable.
#
# Class sets are extracted from each file's ENUMERATION REGION, not the
# whole file: class tokens also occur in ordinary prose (SKILL.md's dogfood
# rule names evidence-mismatch; PROTOCOL.md says "regression test" and
# discusses transport-infrastructure), and a whole-file membership grep let
# an enumeration omission pass whenever the token appeared anywhere else
# (Fable review of PR #22). Region extraction fails closed when the
# enumeration cannot be located. Built-in negative controls re-run this
# checker against mutated copies covering exactly those blind spots.
#
# Usage: andon-class-contract.test.sh [TARGET_ROOT]
# With no argument: check the repo and run the negative controls.
# With TARGET_ROOT: check that tree only (inner negative-control run).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_root="${1:-$repo_root}"
cd "$target_root"

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

# SKILL.md and PROTOCOL.md enumerate the same classes in prose. Membership
# is tested inside the ENUMERATION REGION ONLY — never the whole file — so
# an incidental prose mention can never mask an omission from the list.
def enumeration_region(name, text, pattern):
    m = re.search(pattern, text, re.S)
    if not m:
        fail("%s enumeration region not found (pattern %r)"
             % (name, pattern))
    return m.group(0)

def prose_set(region):
    return {c for c in canonical | REQUIRED
            if re.search(r"(?<![\w-])" + re.escape(c) + r"(?![\w-])",
                         region)}

sk = open("skills/implementaudit/SKILL.md", encoding="utf-8").read()
pr = open("skills/implementaudit/templates/PROTOCOL.md",
          encoding="utf-8").read()
sk_set = prose_set(enumeration_region(
    "SKILL.md", sk, r"`Class:` is an abnormality class.*?\n\n"))
pr_set = prose_set(enumeration_region(
    "templates/PROTOCOL.md", pr, r"exactly one official class from.*?\)"))

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

# ---------------------------------------------------------------------------
# Negative controls (outer run only): the checker must FAIL on an
# enumeration edited in exactly one file, even when the same token still
# appears in that file's ordinary prose. Each control encodes a blind spot
# the whole-file grep actually had (Fable review of PR #22).
if [ "$#" -eq 0 ]; then
  files=(skills/implementaudit/SKILL.md
         skills/implementaudit/templates/PROTOCOL.md
         skills/implementaudit/references/transcript-contract.md)

  make_tree() {  # copy the three owner files into a scratch tree
    local tree="$1" f
    for f in "${files[@]}"; do
      mkdir -p "$tree/$(dirname "$f")"
      cp "$repo_root/$f" "$tree/$f"
    done
  }

  mutate() {  # $1=tree $2=relfile $3=region-kind $4=token $5=replacement
    "$py" - "$1/$2" "$3" "$4" "$5" <<'PY'
import re
import sys

path, kind, token, repl = sys.argv[1:5]
text = open(path, encoding="utf-8").read()
patterns = {
    "SKILL": r"`Class:` is an abnormality class.*?\n\n",
    "PROTOCOL": r"exactly one official class from.*?\)",
    "TC": r"```text\nfailed-criterion\n.*?```",
}
m = re.search(patterns[kind], text, re.S)
if not m:
    raise SystemExit("mutation region not found in " + path)
seg = m.group(0)
tok = re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")
if not tok.search(seg):
    raise SystemExit("token %s not in %s region" % (token, kind))
seg = tok.sub(repl, seg, count=1)
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text[:m.start()] + seg + text[m.end():])
PY
  }

  expect_fail() {  # $1=tree $2=label
    if bash "$repo_root/tests/andon-class-contract.test.sh" "$1" \
        >/dev/null 2>&1; then
      echo "andon-class-contract: NEGATIVE CONTROL FAILED — checker" \
           "accepted a tree with $2" >&2
      rm -rf "$ctrl_tmp"
      exit 1
    fi
  }

  ctrl_tmp="$(mktemp -d)"
  trap 'rm -rf "$ctrl_tmp"' EXIT

  make_tree "$ctrl_tmp/c1"
  mutate "$ctrl_tmp/c1" skills/implementaudit/SKILL.md \
         SKILL evidence-mismatch ""
  expect_fail "$ctrl_tmp/c1" \
      "evidence-mismatch dropped from the SKILL.md enumeration"

  make_tree "$ctrl_tmp/c2"
  mutate "$ctrl_tmp/c2" skills/implementaudit/templates/PROTOCOL.md \
         PROTOCOL regression ""
  expect_fail "$ctrl_tmp/c2" \
      "regression dropped from the PROTOCOL.md enumeration"

  make_tree "$ctrl_tmp/c3"
  mutate "$ctrl_tmp/c3" skills/implementaudit/templates/PROTOCOL.md \
         PROTOCOL transport-infrastructure "transport infrastructure"
  expect_fail "$ctrl_tmp/c3" \
      "a spelling alias of transport-infrastructure in PROTOCOL.md"

  echo "andon-class-contract: negative controls ok (3 mutations rejected)"
fi
