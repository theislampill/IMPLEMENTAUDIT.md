#!/usr/bin/env bash
set -euo pipefail

# Evidence-version anchoring consumer check (#4). Read-only.
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
#
#   check-evidence-anchor.sh --window <launch-intent-file> --now <sha>
#       an open verification window refuses an anchor-to-current-tree diff
#       that intersects a declared surface. Closed windows and complete diffs
#       proven disjoint pass. The existing repo-state.sh changed-files command
#       remains the sole complete working-tree enumerator.

fail() { printf 'check-evidence-anchor: %s\n' "$*" >&2; exit 1; }

mode="${1:-}"
case "$mode" in
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
    fail "usage: --row \"<text>\" | --artifact <file> --tree <sha> | --window <launch-intent-file> --now <sha>"
    ;;
esac
