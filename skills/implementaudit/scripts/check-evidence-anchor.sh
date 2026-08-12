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
#   check-evidence-anchor.sh --window <launch-intent-file> --now <sha> [--planned-paths-env]
#       an open verification window refuses an anchor-to-current-tree diff
#       that intersects a declared surface. Closed windows and complete diffs
#       proven disjoint pass. Its window-specific repo-state route includes
#       ignored and .IMPLEMENTAUDIT/ path identities as live declared surfaces.
#
#   check-evidence-anchor.sh --window-transition <open|close> <launch-intent-file> --entry <n> --repo-root <repo>
#       publishes a prepared/open verification-window transition with complete
#       identity evidence while holding the persistent governed-writer gate.

fail() { printf 'check-evidence-anchor: %s\n' "$*" >&2; exit 1; }

mode="${1:-}"
case "$mode" in
  --capture-mutation-before|--mutation-landed)
    fail "retired receipt mode; use --mutation-window so capture, command, and verification share one process"
    ;;
esac
case "$mode" in
  --window-transition)
    transition="${2:-}"
    intent="${3:-}"
    [ "$transition" = open ] || [ "$transition" = close ] \
      || fail "usage: --window-transition <open|close> <launch-intent-file> --entry <n> --repo-root <repo>"
    [ "${4:-}" = "--entry" ] && [ "${6:-}" = "--repo-root" ] && [ "$#" -eq 7 ] \
      || fail "usage: --window-transition <open|close> <launch-intent-file> --entry <n> --repo-root <repo>"
    entry="${5:-}"
    repo="${7:-}"
    if command -v python >/dev/null 2>&1; then py_cmd=(python)
    elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
    elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
    else fail "python, python3, or py -3 is required for --window-transition"
    fi
    repo_state="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/repo-state.sh"
    run_validator="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/validate-run-root.sh"
    bash_exe="$BASH"
    if command -v cygpath >/dev/null 2>&1; then bash_exe="$(cygpath -w "$bash_exe")"; fi
    "${py_cmd[@]}" - "$transition" "$intent" "$entry" "$repo" "$repo_state" "$run_validator" "$bash_exe" <<'PY'
import hashlib
import errno
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath

if os.name == "nt":
    import msvcrt
else:
    import fcntl

transition, intent_raw, entry_raw, repo_raw, repo_state, run_validator, bash_exe = sys.argv[1:]


def fail(message):
    print(f"check-evidence-anchor: {message}", file=sys.stderr)
    raise SystemExit(1)


def is_reparse(st):
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)


def unique_regular(path):
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISREG(st.st_mode) and not stat.S_ISLNK(st.st_mode) and not is_reparse(st) and st.st_nlink == 1


def bash_path(path):
    return os.fspath(path).replace("\\", "/") if os.name == "nt" else os.fspath(path)


def sync_directory(path):
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel32.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    handle = create(str(path), 0x40000000, 0x7, None, 3, 0x02000000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(), f"open directory for fsync: {path}")
    try:
        if not kernel32.FlushFileBuffers(ctypes.c_void_p(handle)):
            raise OSError(ctypes.get_last_error(), f"fsync directory: {path}")
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(handle))


def normalize_surface(surface):
    normalized = surface.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (not normalized or pure.is_absolute() or ".." in pure.parts
            or normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized)):
        fail(f"verification window contains unsafe surface: {surface}")
    canonical = str(pure)
    if canonical in {"", "."}:
        fail(f"verification window contains unsafe surface: {surface}")
    if normalized.endswith("/"):
        canonical += "/"
    return canonical


try:
    entry_number = int(entry_raw)
except ValueError:
    fail("--entry must be a positive integer")
if entry_number <= 0 or str(entry_number) != entry_raw:
    fail("--entry must be a canonical positive integer")

repo = Path(os.path.abspath(repo_raw))
intent = Path(os.path.abspath(intent_raw))
head = subprocess.run(["git", "-C", os.fspath(repo), "rev-parse", "--show-toplevel"], text=True, capture_output=True, check=False)
if head.returncode != 0 or Path(os.path.abspath(head.stdout.strip())) != repo:
    fail("--repo-root is not the exact current Git worktree root")
try:
    relative = intent.relative_to(repo)
except ValueError:
    fail("launch intent is outside the governed repository")
parts = relative.parts
if (len(parts) != 6 or parts[0:2] != (".IMPLEMENTAUDIT", "runs")
        or parts[3] != "background" or parts[5] != "launch-intent.md"):
    fail("launch intent is outside the governed run topology")
run = repo.joinpath(*parts[:3])
chain = parts[4]
cursor = repo
for part in parts:
    cursor /= part
    try:
        st = os.lstat(cursor)
    except OSError:
        fail("launch intent custody is incomplete")
    if stat.S_ISLNK(st.st_mode) or is_reparse(st):
        fail("launch intent custody contains an alias")
if not unique_regular(intent):
    fail("launch intent is not a unique regular file")
validated = subprocess.run(
    [bash_exe, bash_path(run_validator), "--claim-only", bash_path(run), "--repo-root", bash_path(repo)],
    text=True, capture_output=True, check=False,
)
if validated.returncode != 0:
    fail("launch intent run-root claim is not valid")

gate = repo / ".IMPLEMENTAUDIT" / ".r36-locks" / "namespace.gate"
if not unique_regular(gate) or gate.stat().st_size != 1:
    fail("governed-writer namespace gate is unavailable or unsafe")
fd = os.open(gate, os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
released = False
try:
    opened = os.fstat(fd)
    os.lseek(fd, 0, os.SEEK_SET)
    if os.name == "nt":
        while True:
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                break
            except OSError as error:
                if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                time.sleep(0.05)
    else:
        fcntl.flock(fd, fcntl.LOCK_EX)
    current = os.lstat(gate)
    if ((opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)
            or not stat.S_ISREG(current.st_mode) or current.st_nlink != 1):
        fail("governed-writer namespace gate identity changed")

    lines = intent.read_text(encoding="utf-8").splitlines(keepends=True)
    entries = []
    active = False
    current_entry = None
    for index, raw in enumerate(lines):
        text = raw.rstrip("\r\n")
        if text == "verification_window:":
            active = True
            continue
        if active and text and not text[0].isspace():
            active = False
            current_entry = None
        if not active:
            continue
        match = re.match(r"^(\s*)-\s*surfaces:\s*\[(.*)\]\s*$", text)
        if match:
            surfaces = [normalize_surface(item.strip().strip("'\"`")) for item in match.group(2).split(",") if item.strip()]
            current_entry = {"surfaces": surfaces, "lines": {}, "indent": match.group(1) + "  "}
            entries.append(current_entry)
            continue
        match = re.match(r"^\s*(opened_at|closed_at|chain|state|opening_identity_receipt|opening_identity_sha256|closing_identity_receipt|closing_identity_sha256):\s*(.*?)\s*$", text)
        if match and current_entry is not None:
            key = match.group(1)
            if key in current_entry["lines"]:
                fail(f"verification_window entry contains duplicate key: {key}")
            current_entry[key] = match.group(2).strip().strip("'\"`")
            current_entry["lines"][key] = index
    if entry_number > len(entries):
        fail("selected verification_window entry does not exist")
    selected = entries[entry_number - 1]
    required = {"opened_at", "closed_at", "chain", "state", "opening_identity_receipt", "opening_identity_sha256", "closing_identity_receipt", "closing_identity_sha256"}
    if set(selected["lines"]) != required or not selected["surfaces"] or selected.get("chain") != chain:
        fail("selected verification_window entry is incomplete or bound to another chain")
    expected_state = "prepared" if transition == "open" else "open"
    if selected.get("state") != expected_state:
        fail(f"{transition} transition requires state {expected_state}")
    if transition == "open" and any(selected.get(key) != "none" for key in required - {"chain", "state"}):
        fail("prepared verification_window entry already contains transition evidence")
    if transition == "close" and not (intent.parent / "chain.done").is_file():
        fail("close transition requires chain.done")

    now_result = subprocess.run(["git", "-C", os.fspath(repo), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
    now = now_result.stdout.strip()
    if now_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", now):
        fail("current repository commit identity is unavailable")
    label = "opening" if transition == "open" else "closing"
    receipt_name = f"{label}-identities-{entry_number}.nul"
    receipt = intent.parent / receipt_name
    if receipt.exists():
        fail(f"{label} identity receipt already exists")
    environment = os.environ.copy()
    environment["IMPLEMENTAUDIT_WINDOW_SURFACES_JSON"] = json.dumps(selected["surfaces"], separators=(",", ":"))
    captured = subprocess.run(
        [bash_exe, bash_path(repo_state), "window-identities", "--records", "--surfaces-env"],
        cwd=os.fspath(repo), env=environment, capture_output=True, check=False,
    )
    if captured.returncode != 0 or not captured.stdout:
        detail = captured.stderr.decode(errors="replace").strip()
        fail(f"{label} identity capture failed: {detail or 'empty capture'}")
    with receipt.open("xb") as handle:
        handle.write(captured.stdout); handle.flush(); os.fsync(handle.fileno())
    receipt_digest = hashlib.sha256(captured.stdout).hexdigest()
    updates = {
        "state": transition == "open" and "open" or "closed",
        ("opened_at" if transition == "open" else "closed_at"): now,
        ("opening_identity_receipt" if transition == "open" else "closing_identity_receipt"): receipt_name,
        ("opening_identity_sha256" if transition == "open" else "closing_identity_sha256"): receipt_digest,
    }
    for key, value in updates.items():
        ending = "\r\n" if lines[selected["lines"][key]].endswith("\r\n") else "\n"
        lines[selected["lines"][key]] = f"{selected['indent']}{key}: {value}{ending}"
    temporary = intent.with_name(intent.name + ".transition.tmp")
    if temporary.exists():
        fail("transition temporary path is already occupied")
    with temporary.open("x", encoding="utf-8", newline="") as handle:
        handle.writelines(lines); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, intent)
    sync_directory(intent.parent)
finally:
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        if os.name == "nt":
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
        released = True
    finally:
        os.close(fd)
if not released:
    fail("governed-writer namespace gate release failed")
print(f"check-evidence-anchor: verification window {transition} transition committed entry={entry_number} at={now}")
PY
    ;;
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
    [ "${3:-}" = "--now" ] || fail "usage: --window <launch-intent-file> --now <sha> [--planned-paths-env]"
    now="${4:-}"
    planned_paths=0
    if [ "$#" -eq 5 ] && [ "${5:-}" = "--planned-paths-env" ]; then
      planned_paths=1
    elif [ "$#" -ne 4 ]; then
      fail "usage: --window <launch-intent-file> --now <sha> [--planned-paths-env]"
    fi
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
    bash_exe="$BASH"
    if command -v cygpath >/dev/null 2>&1; then bash_exe="$(cygpath -w "$bash_exe")"; fi
    "${py_cmd[@]}" - "$intent" "$now" "$repo_state" "$bash_exe" "$planned_paths" <<'PY'
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

intent_path = Path(sys.argv[1])
now = sys.argv[2]
repo_state = sys.argv[3]
bash_exe = sys.argv[4]
planned_paths_enabled = sys.argv[5] == "1"
sha_re = re.compile(r"^[0-9a-f]{40}$")


def fail(message):
    print(f"check-evidence-anchor: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize_surface(surface):
    normalized = surface.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (not normalized or pure.is_absolute() or ".." in pure.parts
            or normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized)):
        fail(f"verification window contains unsafe surface: {surface}")
    canonical = str(pure)
    if canonical in {"", "."}:
        fail(f"verification window contains unsafe surface: {surface}")
    if normalized.endswith("/"):
        canonical += "/"
    return canonical


def surface_matches(path, surface):
    return path.startswith(surface) if surface.endswith("/") else fnmatch.fnmatchcase(path, surface)


def planned_path_population():
    if not planned_paths_enabled:
        return []
    raw = os.environ.get("IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON", "")
    try:
        paths = json.loads(raw)
    except json.JSONDecodeError:
        fail("planned path population is not valid JSON")
    if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
        fail("planned path population must be a nonempty JSON string array")
    # The repository root itself is a valid planned durability target even
    # though it is not a valid user-declared surface. It cannot intersect a
    # narrower repo-relative declaration; descendant paths remain explicit.
    normalized = ["." if path == "." else normalize_surface(path) for path in paths]
    if len(set(normalized)) != len(normalized):
        fail("planned path population contains duplicate paths")
    return sorted(normalized)


def window_changed_paths(opened):
    changed = subprocess.run(
        [bash_exe, repo_state, "window-changed-files", "--null", opened],
        capture_output=True,
        check=False,
    )
    if changed.returncode != 0:
        fail(f"complete window changed-files enumeration failed for {opened}: {changed.stderr.decode(errors='replace').strip()}")
    try:
        return sorted({part.decode("utf-8") for part in changed.stdout.split(b"\0") if part})
    except UnicodeDecodeError:
        fail(f"complete window changed-files enumeration returned a non-UTF-8 path for {opened}")


def normalized_surface_population(surfaces, label):
    if not surfaces or any(not isinstance(surface, str) for surface in surfaces):
        fail(f"{label} has no valid declared surfaces")
    normalized = [normalize_surface(surface) for surface in surfaces]
    if len(set(normalized)) != len(normalized):
        fail(f"{label} contains duplicate declared surfaces")
    return sorted(normalized)


def identity_records(payload, label, expected_surfaces):
    records = {}
    try:
        raw_records = [part.decode("utf-8") for part in payload.split(b"\0") if part]
    except UnicodeDecodeError:
        fail(f"{label} returned a non-UTF-8 record")
    if not raw_records:
        fail(f"{label} contains no receipt header")
    try:
        header = json.loads(raw_records[0])
    except json.JSONDecodeError:
        fail(f"{label} contains malformed receipt header JSON")
    if (not isinstance(header, dict)
            or set(header) != {"schema", "surfaces"}
            or header.get("schema") != "verification-window-identity-receipt-v1"
            or not isinstance(header.get("surfaces"), list)):
        fail(f"{label} has an invalid receipt header")
    declared_population = normalized_surface_population(header["surfaces"], label)
    expected_population = normalized_surface_population(expected_surfaces, "verification window")
    if declared_population != expected_population:
        fail(f"{label} declared surfaces do not match the verification window: receipt={declared_population} expected={expected_population}")
    for raw in raw_records[1:]:
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            fail(f"{label} contains malformed identity JSON")
        if set(record) != {"path", "type", "extent", "sha256"}:
            fail(f"{label} identity record has an invalid schema")
        path = normalize_surface(record["path"])
        if record["type"] not in {"regular", "directory", "symlink"}:
            fail(f"{label} identity record has an unsupported type: {record['type']}")
        if not isinstance(record["extent"], int) or record["extent"] < 0:
            fail(f"{label} identity record has an invalid extent: {path}")
        if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            fail(f"{label} identity record has an invalid digest: {path}")
        if path in records:
            fail(f"{label} contains a duplicate identity path: {path}")
        records[path] = (record["type"], record["extent"], record["sha256"])
    return records


def window_identity_records(surfaces):
    command = [bash_exe, repo_state, "window-identities", "--records", "--surfaces-env"]
    environment = os.environ.copy()
    environment["IMPLEMENTAUDIT_WINDOW_SURFACES_JSON"] = json.dumps(surfaces)
    identities = subprocess.run(
        command,
        capture_output=True,
        check=False,
        env=environment,
    )
    if identities.returncode != 0:
        fail(f"complete window identity enumeration failed: {identities.stderr.decode(errors='replace').strip()}")
    try:
        return identity_records(identities.stdout, "complete window identity enumeration", surfaces)
    except UnicodeDecodeError:
        fail("complete window identity enumeration returned a non-UTF-8 record")


def receipt_records(receipt_name, expected_digest, label, surfaces):
    receipt = Path(receipt_name)
    if (not receipt_name or receipt.is_absolute() or ".." in receipt.parts
            or receipt_name.startswith("/") or re.match(r"^[A-Za-z]:", receipt_name)):
        fail(f"verification window {label} identity receipt is unsafe: {receipt_name}")
    receipt_path = intent_path.parent / receipt
    if not receipt_path.is_file() or receipt_path.is_symlink():
        fail(f"verification window {label} identity receipt is not a regular file: {receipt_path}")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        fail(f"verification window {label} identity receipt digest is invalid")
    payload = receipt_path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_digest:
        fail(f"verification window {label} identity receipt digest does not match")
    try:
        return identity_records(payload, f"verification window {label} identity receipt", surfaces)
    except UnicodeDecodeError:
        fail(f"verification window {label} identity receipt contains a non-UTF-8 path")


def intersecting_paths(paths, surfaces):
    return sorted(
        path for path in paths
        if any(surface_matches(path, surface) for surface in surfaces)
    )


def identity_delta(before, after):
    return (set(before) - set(after)) | (set(after) - set(before)) | {
        path for path in set(before) & set(after)
        if before[path] != after[path]
    }


if not sha_re.fullmatch(now):
    fail("--now must be a full 40-hex SHA")

planned_paths = planned_path_population()

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
            normalize_surface(item.strip().strip("'\"`"))
            for item in match.group(1).split(",")
            if item.strip()
        ]
        current = {"surfaces": surfaces}
        windows.append(current)
        continue
    match = re.match(
        r"^\s*(opened_at|closed_at|chain|state|opening_identity_receipt|opening_identity_sha256|closing_identity_receipt|closing_identity_sha256):\s*(.*?)\s*$",
        raw,
    )
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
    opening_receipt = window.get("opening_identity_receipt", "")
    opening_digest = window.get("opening_identity_sha256", "")
    if state == "prepared" and planned_paths_enabled:
        if (not surfaces or not chain or any(window.get(key, "") != "none" for key in (
                "opened_at", "closed_at", "opening_identity_receipt", "opening_identity_sha256",
                "closing_identity_receipt", "closing_identity_sha256"))):
            fail(f"verification_window entry {index} has invalid prepared transition state")
        if Path(intent_path).parent.name != chain:
            fail(f"verification_window entry {index} chain does not match its directory: {chain}")
        continue
    if not surfaces or not chain or state not in {"open", "closed"} or not opening_receipt or not opening_digest:
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
    opening_records = receipt_records(opening_receipt, opening_digest, "opening", surfaces)
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
        closing_receipt = window.get("closing_identity_receipt", "")
        closing_digest = window.get("closing_identity_sha256", "")
        if not closing_receipt or not closing_digest:
            fail(f"verification_window entry {index} is closed without a closing identity receipt")
        recorded_closing_records = receipt_records(closing_receipt, closing_digest, "closing", surfaces)
        if closed == now:
            window_changed_paths(opened)
            closing_records = window_identity_records(surfaces)
        else:
            window_changed_paths(opened)
            closing_records = recorded_closing_records
        intersecting = intersecting_paths(
            identity_delta(opening_records, closing_records),
            surfaces,
        )
        if intersecting:
            fail(
                "AUTH_EXCEEDED: closed verification window moved from "
                f"{opened} to {closed}; surfaces=[{', '.join(surfaces)}]; "
                f"intersecting=[{', '.join(intersecting)}]"
            )
        continue
    window_changed_paths(opened)
    current_records = window_identity_records(surfaces)
    intersecting = intersecting_paths(
        identity_delta(opening_records, current_records),
        surfaces,
    )
    if intersecting:
        fail(
            "AUTH_EXCEEDED: open verification window moved from "
            f"{opened} to {now}; surfaces=[{', '.join(surfaces)}]; "
            f"intersecting=[{', '.join(intersecting)}]"
        )
    planned_intersections = intersecting_paths(planned_paths, surfaces)
    if planned_intersections:
        fail(
            "AUTH_EXCEEDED: planned mutation intersects open verification window; "
            f"surfaces=[{', '.join(surfaces)}]; "
            f"intersecting=[{', '.join(planned_intersections)}]"
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
    fail "usage: --row \"<text>\" | --artifact <file> --tree <sha> | --window <launch-intent-file> --now <sha> [--planned-paths-env] | --window-transition <open|close> <launch-intent-file> --entry <n> --repo-root <repo> | --mutation-window <path> --expect <spec> -- <command> [args...]"
    ;;
esac
