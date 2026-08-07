#!/usr/bin/env bash
set -euo pipefail

# Evidence-version anchoring and bounded mutation-window check (#4).
#
#   check-evidence-anchor.sh --row "<evidence cell text>"
#       exit 0 when every `@<hex>` anchor token is a full 40-hex SHA
#       (legacy rows without anchors also pass); exit 1 otherwise.
#
#   check-evidence-anchor.sh --artifact <file> --tree <full-40-hex-sha>
#       the artifact must name the exact state it attests via an
#       `Anchor: <full-sha>` line (or `@<full-sha>` token). Exit 1 when
#       the artifact is unanchored or anchored to a DIFFERENT state —
#       a stale artifact is never accepted as current-state evidence.
#       Optional `--bound-surfaces <manifest>` keeps the artifact valid when
#       every anchor-to-current changed path is disjoint from the nonempty,
#       repo-relative path/glob manifest. Without it, exact equality remains.
#
#   check-evidence-anchor.sh --window <launch-intent-file> --now <sha>
#       an open verification window refuses an anchor-to-current-tree diff
#       that intersects a declared surface. Closed windows and complete diffs
#       proven disjoint pass. The existing repo-state.sh changed-files command
#       remains the sole complete working-tree enumerator.

fail() { printf 'check-evidence-anchor: %s\n' "$*" >&2; exit 1; }

mode="${1:-}"
case "$mode" in
  --capture-mutation-before|--mutation-landed)
    fail "retired receipt mode; use --mutation-window so capture, command, and verification share one process"
    ;;
esac
case "$mode" in
  --mutation-window)
    landed_path="${2:-}"
    [ "${3:-}" = "--expect" ] \
      || fail "usage: --mutation-window <path> --expect <spec> -- <command> [args...]"
    expectation="${4:-}"
    [ "${5:-}" = "--" ] && [ "$#" -ge 6 ] \
      || fail "usage: --mutation-window <path> --expect <spec> -- <command> [args...]"
    shift 5
    [ -f "$landed_path" ] && [ ! -L "$landed_path" ] \
      || fail "mutation target must be a regular non-symlink file: $landed_path"
    if command -v python >/dev/null 2>&1; then py_cmd=(python)
    elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
    elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
    else fail "python, python3, or py -3 is required for --mutation-window"
    fi
    "${py_cmd[@]}" - "$landed_path" "$expectation" "$@" <<'PY'
import hashlib
import pathlib
import re
import subprocess
import sys

def fail(message):
    print(f"check-evidence-anchor: {message}", file=sys.stderr)
    raise SystemExit(1)

def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, check=False)
    if result.returncode != 0:
        fail(f"git {' '.join(args)} failed")
    return result.stdout

path_arg = pathlib.Path(sys.argv[1])
spec = sys.argv[2]
command = sys.argv[3:]
root = pathlib.Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve()
head = git("rev-parse", "HEAD").decode().strip()
path = path_arg.resolve(strict=True)
try:
    relative = path.relative_to(root).as_posix()
except ValueError:
    fail("mutation target must resolve inside the current repository")
before_bytes = path.read_bytes()
try:
    before = before_bytes.decode("utf-8")
except UnicodeError:
    fail("mutation landed checks require UTF-8 text files")
before_sha = hashlib.sha256(before_bytes).hexdigest()
if spec.startswith("occurrences:"):
    parts = spec.split(":", 2)
    if len(parts) != 3 or not re.fullmatch(r"[0-9]+", parts[1]) or not parts[2]:
        fail("occurrences expects occurrences:<nonnegative-int>:<literal>")
    kind = "occurrences"
    expected = int(parts[1])
    literal = parts[2]
    prior = before.count(literal)
    if prior == expected:
        fail(f"mutation expectation was already true before the command: occurrences={prior}")
elif spec.startswith("anchor:"):
    kind = "anchor"
    literal = spec.split(":", 1)[1]
    if not literal:
        fail("anchor expects anchor:<literal>")
    if literal in before:
        fail("mutation expectation was already true before the command: anchor present")
elif spec.startswith("hunk:"):
    parts = spec.split(":", 2)
    if len(parts) != 3 or not re.fullmatch(r"[1-9][0-9]*", parts[1]) or not parts[2]:
        fail("hunk expects hunk:<one-based-line>:<literal>")
    kind = "hunk"
    number = int(parts[1])
    literal = parts[2]
    before_lines = before.splitlines()
    if number <= len(before_lines) and literal in before_lines[number - 1]:
        fail(f"mutation expectation was already true before the command: hunk line={number}")
else:
    fail("unknown mutation expectation (expected occurrences, anchor, or hunk)")

result = subprocess.run(command, check=False)
if result.returncode != 0:
    fail(f"mutation command exited {result.returncode}")
if not path.is_file() or path.is_symlink():
    fail("mutation command did not leave a regular non-symlink target")
after_bytes = path.read_bytes()
try:
    text = after_bytes.decode("utf-8")
except UnicodeError:
    fail("mutation landed checks require UTF-8 text files")
after_sha = hashlib.sha256(after_bytes).hexdigest()
if before_sha == after_sha:
    fail("mutation not landed: before and after bytes are identical")

if kind == "occurrences":
    observed = text.count(literal)
    if observed != expected:
        fail(f"mutation not landed: occurrences observed={observed} expected={expected}")
    detail = f"occurrences-before={prior} occurrences-after={observed}"
elif kind == "anchor":
    if literal not in text:
        fail("mutation not landed: anchor absent")
    detail = "anchor=absent-to-present"
else:
    lines = text.splitlines()
    if number > len(lines) or literal not in lines[number - 1]:
        observed = "missing-line" if number > len(lines) else repr(lines[number - 1])
        fail(f"mutation not landed: hunk line={number} observed={observed}")
    detail = f"hunk-line={number}"

print(
    f"check-evidence-anchor: mutation landed target={relative} head={head} "
    f"command-exit=0 {detail} before-sha256={before_sha} after-sha256={after_sha}"
)
PY
    ;;
  --row)
    row="${2:-}"
    bad="$(printf '%s' "$row" | grep -oE '@[0-9a-f]{7,}' \
      | grep -vE '^@[0-9a-f]{40}$' || true)"
    [ -z "$bad" ] || fail "anchor(s) not full 40-hex SHAs: $bad"
    printf 'check-evidence-anchor: row ok\n'
    ;;
  --artifact)
    artifact="${2:-}"
    [ "${3:-}" = "--tree" ] || fail "usage: --artifact <file> --tree <sha>"
    tree="${4:-}"
    bound_surfaces=""
    if [ "$#" -gt 4 ]; then
      [ "$#" -eq 6 ] && [ "${5:-}" = "--bound-surfaces" ] \
        || fail "usage: --artifact <file> --tree <sha> [--bound-surfaces <manifest>]"
      bound_surfaces="${6:-}"
      [ -f "$bound_surfaces" ] && [ ! -L "$bound_surfaces" ] \
        || fail "bound-surfaces manifest must be a regular non-symlink file: $bound_surfaces"
    fi
    printf '%s' "$tree" | grep -qE '^[0-9a-f]{40}$' \
      || fail "--tree must be a full 40-hex SHA"
    [ -f "$artifact" ] || fail "artifact not found: $artifact"
    # Every anchor-shaped token must be EXACTLY 40 hex — the same format
    # rule --row enforces. Without this, `Anchor: <sha><extra-hex>` was
    # accepted via first-40-chars truncation while the identical token in
    # a row was flagged (Fable review of PR #23).
    malformed="$(grep -oE '(Anchor: *|@)[0-9a-f]{7,}' "$artifact" \
      | sed -E 's/^(Anchor: *|@)//' | grep -vE '^[0-9a-f]{40}$' || true)"
    [ -z "$malformed" ] || fail \
      "artifact $artifact carries anchor token(s) that are not full 40-hex SHAs: $(printf '%s' "$malformed" | tr '\n' ' ')"
    anchor="$(grep -oE '(Anchor: *|@)[0-9a-f]{40}' "$artifact" \
      | grep -oE '[0-9a-f]{40}' | head -n 1 || true)"
    [ -n "$anchor" ] || fail \
      "artifact $artifact names no full-SHA anchor — unanchored artifacts are not current-state evidence"
    if [ -n "$bound_surfaces" ]; then
      bound_digest_lines="$(grep -Ec '^Bound-Surfaces-SHA256: [0-9a-f]{64}$' "$artifact" || true)"
      [ "$bound_digest_lines" -eq 1 ] \
        || fail "artifact must bind exactly one Bound-Surfaces-SHA256 when --bound-surfaces is used"
      declared_bound_digest="$(sed -n 's/^Bound-Surfaces-SHA256: //p' "$artifact")"
      actual_bound_digest="$(sha256sum "$bound_surfaces" | awk '{print $1}')"
      [ "$declared_bound_digest" = "$actual_bound_digest" ] \
        || fail "bound-surfaces manifest digest does not match the artifact declaration"
      if command -v python >/dev/null 2>&1; then py_cmd=(python)
      elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
      elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
      else fail "python, python3, or py -3 is required for --bound-surfaces"
      fi
      "${py_cmd[@]}" - "$anchor" "$tree" "$bound_surfaces" <<'PY'
import fnmatch
import pathlib
import re
import subprocess
import sys

def fail(message):
    print(f"check-evidence-anchor: {message}", file=sys.stderr)
    raise SystemExit(1)

anchor, current, manifest_arg = sys.argv[1:]
head = subprocess.run(
    ["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=False
)
if head.returncode != 0 or head.stdout.strip() != current:
    fail("--tree must equal current HEAD when --bound-surfaces is used")
for name, value in (("artifact anchor", anchor), ("offered tree", current)):
    check = subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if check.returncode != 0:
        fail(f"{name} is not a local commit")

manifest = pathlib.Path(manifest_arg)
patterns = []
for raw in manifest.read_text(encoding="utf-8").splitlines():
    pattern = raw.strip()
    if not pattern or pattern.startswith("#"):
        continue
    pure = pathlib.PurePosixPath(pattern.replace("\\", "/"))
    if (pure.is_absolute() or ".." in pure.parts or pattern.startswith("/")
            or re.match(r"^[A-Za-z]:", pattern)):
        fail(f"unsafe bound surface: {pattern}")
    patterns.append(pure.as_posix())
if not patterns:
    fail("bound-surfaces manifest contains no path or glob")

diff = subprocess.run(
    ["git", "diff", "--name-only", "-z", anchor, current],
    capture_output=True,
    check=False,
)
if diff.returncode != 0:
    fail("anchor-to-current changed-path enumeration failed")
changed = [part.decode("utf-8") for part in diff.stdout.split(b"\0") if part]
intersections = sorted(
    path for path in changed
    if any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)
)
if intersections:
    fail("REFUSED: anchor-to-current diff intersects bound surfaces: " + ", ".join(intersections))
print(
    "check-evidence-anchor: artifact retained; anchor-to-current diff disjoint "
    f"changed={len(changed)} bound-surfaces={len(patterns)}"
)
PY
      exit 0
    fi
    if [ "$anchor" != "$tree" ]; then
      fail "REFUSED: artifact is anchored to $anchor but offered for $tree — re-gather evidence on the current state"
    fi
    printf 'check-evidence-anchor: artifact anchored to the offered tree\n'
    ;;
  --window)
    intent="${2:-}"
    [ "${3:-}" = "--now" ] || fail "usage: --window <launch-intent-file> --now <sha>"
    now="${4:-}"
    [ -f "$intent" ] || fail "launch intent not found: $intent"
    if command -v python >/dev/null 2>&1; then
      py_cmd=(python)
    elif command -v python3 >/dev/null 2>&1; then
      py_cmd=(python3)
    elif command -v py >/dev/null 2>&1; then
      py_cmd=(py -3)
    else
      fail "python, python3, or py -3 is required for --window"
    fi
    repo_state="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/repo-state.sh"
    "${py_cmd[@]}" - "$intent" "$now" "$repo_state" "$BASH" <<'PY'
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

intent_path = Path(sys.argv[1])
now = sys.argv[2]
repo_state = sys.argv[3]
bash_exe = sys.argv[4]
sha_re = re.compile(r"^[0-9a-f]{40}$")


def fail(message):
    print(f"check-evidence-anchor: {message}", file=sys.stderr)
    raise SystemExit(1)


if not sha_re.fullmatch(now):
    fail("--now must be a full 40-hex SHA")

text = intent_path.read_text(encoding="utf-8")
windows = []
current = None
in_windows = False
for raw in text.splitlines():
    if raw == "verification_window:":
        in_windows = True
        continue
    if in_windows and raw and not raw[0].isspace():
        in_windows = False
        current = None
    if not in_windows:
        continue
    match = re.match(r"^\s*-\s*surfaces:\s*\[(.*)\]\s*$", raw)
    if match:
        surfaces = [
            item.strip().strip("'\"`")
            for item in match.group(1).split(",")
            if item.strip()
        ]
        current = {"surfaces": surfaces}
        windows.append(current)
        continue
    match = re.match(r"^\s*(opened_at|closed_at|chain|state):\s*(.*?)\s*$", raw)
    if match and current is not None:
        current[match.group(1)] = match.group(2).strip().strip("'\"`")

if not windows:
    fail(f"{intent_path} contains no verification_window entries")

head = subprocess.run(
    ["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=False
)
if head.returncode != 0:
    fail("--window must run inside the repository whose tree is being verified")
head_sha = head.stdout.strip()
if head_sha != now:
    fail(f"--now {now} does not equal current HEAD {head_sha}")

open_moved = []
for index, window in enumerate(windows, 1):
    surfaces = window.get("surfaces", [])
    opened = window.get("opened_at", "")
    closed = window.get("closed_at", "")
    state = window.get("state", "")
    chain = window.get("chain", "")
    if not surfaces or not chain or state not in {"open", "closed"}:
        fail(f"verification_window entry {index} is incomplete or invalid")
    if not sha_re.fullmatch(opened):
        fail(f"verification_window entry {index} opened_at must be a full 40-hex SHA")
    verify = subprocess.run(
        ["git", "rev-parse", "--verify", f"{opened}^{{commit}}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if verify.returncode != 0:
        fail(f"verification_window entry {index} opened_at is not a local commit: {opened}")
    if Path(intent_path).parent.name != chain:
        fail(f"verification_window entry {index} chain does not match its directory: {chain}")
    if state == "closed":
        marker = intent_path.parent / "chain.done"
        if not marker.is_file():
            fail(f"verification_window entry {index} is closed without {marker}")
        if not sha_re.fullmatch(closed):
            fail(f"verification_window entry {index} closed_at must be a full 40-hex SHA")
        verify_closed = subprocess.run(
            ["git", "rev-parse", "--verify", f"{closed}^{{commit}}"],
            text=True,
            capture_output=True,
            check=False,
        )
        if verify_closed.returncode != 0:
            fail(f"verification_window entry {index} closed_at is not a local commit: {closed}")
        if closed == opened:
            continue
        if closed == now:
            changed = subprocess.run(
                [bash_exe, repo_state, "changed-files", opened],
                text=True,
                capture_output=True,
                check=False,
            )
        else:
            changed = subprocess.run(
                ["git", "diff", "--name-only", opened, closed],
                text=True,
                capture_output=True,
                check=False,
            )
        if changed.returncode != 0:
            fail(f"closing diff enumeration failed for {opened}..{closed}: {changed.stderr.strip()}")
        changed_paths = [line for line in changed.stdout.splitlines() if line]
        intersecting = sorted(
            path
            for path in changed_paths
            if any(fnmatch.fnmatchcase(path, surface) for surface in surfaces)
        )
        if intersecting:
            fail(
                "AUTH_EXCEEDED: closed verification window moved from "
                f"{opened} to {closed}; surfaces=[{', '.join(surfaces)}]; "
                f"intersecting=[{', '.join(intersecting)}]"
            )
        continue
    if now == opened:
        continue
    changed = subprocess.run(
        [bash_exe, repo_state, "changed-files", opened],
        text=True,
        capture_output=True,
        check=False,
    )
    if changed.returncode != 0:
        fail(f"complete changed-files enumeration failed for {opened}: {changed.stderr.strip()}")
    changed_paths = [line for line in changed.stdout.splitlines() if line]
    intersecting = sorted(
        path
        for path in changed_paths
        if any(fnmatch.fnmatchcase(path, surface) for surface in surfaces)
    )
    if intersecting:
        fail(
            "AUTH_EXCEEDED: open verification window moved from "
            f"{opened} to {now}; surfaces=[{', '.join(surfaces)}]; "
            f"intersecting=[{', '.join(intersecting)}]"
        )
    open_moved.append((opened, surfaces))

if open_moved:
    rendered = "; ".join(
        f"{opened} -> {now} surfaces=[{', '.join(surfaces)}]"
        for opened, surfaces in open_moved
    )
    print(f"check-evidence-anchor: window diff disjoint ({rendered})")
else:
    print("check-evidence-anchor: window anchor current or closed")
PY
    ;;
  *)
    fail "usage: --row \"<text>\" | --artifact <file> --tree <sha> | --window <launch-intent-file> --now <sha> | --mutation-window <path> --expect <spec> -- <command> [args...]"
    ;;
esac
