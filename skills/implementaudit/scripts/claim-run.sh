#!/usr/bin/env bash
# Atomically claim native run roots and controller continuity.

set -u

base="${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"
controller_ref_readback_uncertain=0

claim_posix_python_reference() {
  local selected="$1" reference leaf="${1##*/}"
  [[ "$leaf" =~ ^python3(\.[0-9]+)?[tdm]?$ ]] || return 1
  # Identity must come from an existing host installation, not a caller's
  # renamed ELF file. Venv symlinks retain the installed binary identity.
  for reference in "/usr/bin/$leaf" "/usr/local/bin/$leaf" "/bin/$leaf" \
                   /usr/bin/python3 /usr/local/bin/python3 /bin/python3; do
    [ -f "$reference" ] && [ -x "$reference" ] && [ "$selected" -ef "$reference" ] && return 0
  done
  return 1
}

select_claim_python() {
  # Inspect executable identity before invocation: launcher/version probes can
  # themselves install a runtime. This is selection, not native authority.
  local candidates=() name candidate resolved lower magic native system_root powershell host bash_image cursor owner mode
  if [ "${IMPLEMENTAUDIT_PYTHON+x}" = x ]; then
    [ -n "$IMPLEMENTAUDIT_PYTHON" ] || return 1
    candidates=("$IMPLEMENTAUDIT_PYTHON")
  else
    for name in python python3; do
      candidate="$(type -P "$name")" || continue
      candidates+=("$candidate")
    done
  fi
  for candidate in "${candidates[@]}"; do
    case "$candidate" in /*|[A-Za-z]:[/\\]*) ;; *) continue ;; esac
    case "${OSTYPE:-}" in
      msys*|cygwin*) candidate="$(cygpath -u "$candidate")" || continue ;;
    esac
    resolved="$(readlink -f -- "$candidate" 2>/dev/null)" || continue
    [ -f "$resolved" ] && [ -s "$resolved" ] && [ -x "$resolved" ] || continue
    lower="$(printf '%s' "$resolved" | LC_ALL=C tr '[:upper:]' '[:lower:]')" || continue
    case "$lower" in */windowsapps/*|*/py.exe|*/py-manager.exe|*/pymanager.exe) continue ;; esac
    magic="$(LC_ALL=C od -An -tx1 -N4 -- "$resolved" 2>/dev/null)" || continue
    magic="${magic//[[:space:]]/}"
    case "${OSTYPE:-}" in
      msys*|cygwin*)
        case "$magic" in 4d5a*) ;; *) continue ;; esac
        native="$(cygpath -aw "$resolved")" || continue
        system_root="${SystemRoot:-${SYSTEMROOT:-}}"
        [ -n "$system_root" ] || continue
        powershell="$(cygpath -u "$system_root/System32/WindowsPowerShell/v1.0/powershell.exe")" || continue
        [ -f "$powershell" ] && [ -x "$powershell" ] || continue
        IMPLEMENTAUDIT_PYTHON_CANDIDATE="$native" MSYS2_ARG_CONV_EXCL='*' "$powershell" \
          -NoLogo -NoProfile -NonInteractive -Command '
$ErrorActionPreference = "Stop"
try {
  $item = [IO.FileInfo]::new($env:IMPLEMENTAUDIT_PYTHON_CANDIDATE)
  if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { exit 1 }
  $v = [Diagnostics.FileVersionInfo]::GetVersionInfo($item.FullName)
  if ($v.ProductName -cne "Python" -or $v.FileDescription -cne "Python" -or $v.ProductMajorPart -ne 3) { exit 1 }
  $tag = "$($v.ProductMajorPart).$($v.ProductMinorPart)"
  $registered = @()
  foreach ($hive in @([Microsoft.Win32.Registry]::CurrentUser, [Microsoft.Win32.Registry]::LocalMachine)) {
    foreach ($prefix in @("Software\Python\PythonCore", "Software\WOW6432Node\Python\PythonCore")) {
      foreach ($version in @($tag, "$tag-32", "$tag-64")) {
        $key = $hive.OpenSubKey("$prefix\$version\InstallPath", $false)
        if ($null -eq $key) { continue }
        try {
          $pythonHome = $key.GetValue("")
          if ($pythonHome -isnot [string] -or -not [IO.Path]::IsPathRooted($pythonHome)) { continue }
          $exe = $key.GetValue("ExecutablePath", [IO.Path]::Combine($pythonHome, "python.exe"))
          if ($exe -isnot [string] -or -not [IO.Path]::IsPathRooted($exe)) { continue }
          if ($item.FullName -ieq [IO.Path]::GetFullPath($exe)) { exit 0 }
          $registered += [IO.Path]::GetFullPath($pythonHome).TrimEnd([IO.Path]::DirectorySeparatorChar)
        } finally { $key.Dispose() }
      }
    }
  }
  # A venv launcher is admitted only against an installed Python template and
  # that installation home; arbitrary copied or metadata-forged PEs refuse.
  if ($item.Name -ine "python.exe" -or $item.Directory.Name -ine "Scripts") { exit 1 }
  $config = [IO.FileInfo]::new([IO.Path]::Combine($item.Directory.Parent.FullName, "pyvenv.cfg"))
  if (-not $config.Exists -or $config.Length -gt 8192 -or ($config.Attributes -band [IO.FileAttributes]::ReparsePoint)) { exit 1 }
  $stream = $config.OpenRead()
  try { $buffer = New-Object byte[] 8193; $count = $stream.Read($buffer, 0, $buffer.Length) } finally { $stream.Dispose() }
  if ($count -ne $config.Length -or $count -gt 8192) { exit 1 }
  $homes = [regex]::Matches([Text.Encoding]::UTF8.GetString($buffer, 0, $count), "(?m)^home\s*=\s*([^\r\n]+)\r?$")
  if ($homes.Count -ne 1) { exit 1 }
  $pythonHome = [IO.Path]::GetFullPath($homes[0].Groups[1].Value.Trim()).TrimEnd([IO.Path]::DirectorySeparatorChar)
  if ($registered -inotcontains $pythonHome) { exit 1 }
  $template = [IO.FileInfo]::new([IO.Path]::Combine($pythonHome, "Lib\venv\scripts\nt\python.exe"))
  if (-not $template.Exists -or $template.Length -ne $item.Length -or $item.Length -gt 1048576) { exit 1 }
  $hash = [Security.Cryptography.SHA256]::Create()
  try {
    $a = $item.OpenRead(); try { $actual = [BitConverter]::ToString($hash.ComputeHash($a)) } finally { $a.Dispose() }
    $b = $template.OpenRead(); try { $expected = [BitConverter]::ToString($hash.ComputeHash($b)) } finally { $b.Dispose() }
  } finally { $hash.Dispose() }
  if ($actual -cne $expected) { exit 1 }
} catch { exit 1 }
exit 0' >/dev/null 2>&1 || continue
        ;;
      *)
        # Receive the existing continuity transport's exact readonly startup
        # wrapper. Preserve -I/-S/-B rather than bypassing its private closure.
        case "$resolved" in /implementaudit-python/python|/implementaudit-python/python3)
          [ ! -w "$resolved" ] && [ ! -w /implementaudit-python ] || continue
          [ -f /implementaudit-python/cpython ] && [ ! -L /implementaudit-python/cpython ] \
            && [ ! -w /implementaudit-python/cpython ] || continue
          bash_image="$(readlink -f -- "$BASH")" || continue
          cmp -s -- "$resolved" <(printf '#!%s\nexec /implementaudit-python/cpython -I -S -B "$@"\n' "$bash_image") || continue
          for name in python3 python; do
            while IFS= read -r host; do
              host="$(readlink -f -- "$host" 2>/dev/null)" || continue
              claim_posix_python_reference "$host" || continue
              [ /implementaudit-python/cpython -ef "$host" ] || continue
              magic="$(LC_ALL=C od -An -tx1 -N4 -- "$host" 2>/dev/null)" || continue
              magic="${magic//[[:space:]]/}"
              case "$magic" in 7f454c46)
                printf '%s\n' "$resolved"
                return 0 ;;
              esac
            done < <(type -aP "$name")
          done
          continue ;;
        esac
        # Venv/system symlinks resolve to the actual versioned interpreter;
        # script shims and unversioned/foreign executables remain unqualified.
        claim_posix_python_reference "$resolved" || continue
        cursor="$resolved"
        while :; do
          read -r owner mode < <(stat -c '%u %a' -- "$cursor" 2>/dev/null) || break
          [ "$owner" = 0 ] && [[ "$mode" =~ ^[0-7]+$ ]] && (( (8#$mode & 0022) == 0 )) || break
          [ "$cursor" != / ] || break
          cursor="$(dirname "$cursor")" || break
        done
        [ "$cursor" = / ] && [ "$owner" = 0 ] && [[ "$mode" =~ ^[0-7]+$ ]] \
          && (( (8#$mode & 0022) == 0 )) || continue
        case "$magic" in 7f454c46) ;; *) continue ;; esac
        ;;
    esac
    printf '%s\n' "$resolved"
    return 0
  done
  return 1
}

reject_coordination_reparse() {
  local candidate="$1"
  [ ! -L "$candidate" ] || return 1
  if [ -e "$candidate" ] && command -v cmd.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    local candidate_win
    candidate_win="$(cygpath -aw "$candidate")" || return 1
    if MSYS2_ARG_CONV_EXCL='*' cmd.exe /d /c fsutil reparsepoint query "$candidate_win" >/dev/null 2>&1; then
      return 1
    fi
  fi
  return 0
}

update_controller_ref() {
  controller_ref_readback_uncertain=0
  local py update_result
  py="$(select_claim_python)" || return 1
  controller_ref_readback_uncertain=1
  update_result="$("$py" -I -B - "$gate" "$1" "$2" "$3" <<'PY'
import errno,os,stat,subprocess,sys,time
if os.name=='nt': import msvcrt
else: import fcntl
gate,ref,new,old=sys.argv[1:]
def unsafe(s): return not stat.S_ISREG(s.st_mode) or stat.S_ISLNK(s.st_mode) or bool(getattr(s,'st_file_attributes',0)&0x400) or s.st_nlink!=1 or s.st_size!=1
before=os.lstat(gate)
if unsafe(before): raise SystemExit(1)
fd=os.open(gate,os.O_RDWR|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0))
try:
 opened=os.fstat(fd)
 if os.name=='nt':
  while True:
   try: os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_NBLCK,1); break
   except OSError as e:
    if e.errno not in {errno.EACCES,errno.EAGAIN,errno.EDEADLK}: raise
    time.sleep(.05)
 else: fcntl.flock(fd,fcntl.LOCK_EX)
 current=os.lstat(gate)
 if unsafe(current) or (current.st_dev,current.st_ino)!=(opened.st_dev,opened.st_ino): raise SystemExit(1)
 # The gate is worktree-local; Git's prepare phase arbitrates shared refs.
 # An explicit transaction aborts on EOF unless this owner sends commit.
 with subprocess.Popen(['git','update-ref','--stdin'],stdin=subprocess.PIPE,stdout=subprocess.PIPE) as transaction:
  transaction.stdin.write(('start\nupdate '+ref+' '+new+' '+old+'\nprepare\n').encode('ascii'))
  transaction.stdin.flush()
  if transaction.stdout.readline(64)!=b'start: ok\n': raise SystemExit(1)
  prepared=transaction.stdout.readline(64)
  if prepared!=b'prepare: ok\n':
   transaction.stdin.close()
   result=transaction.wait()
   if prepared==b'' and result!=0:
    # Exact owner result: the native process ended and no commit was sent.
    print('NO_COMMIT\t'+ref+'\t'+new+'\t'+old)
    raise SystemExit(0)
   raise SystemExit(1)
  committed,_=transaction.communicate(b'commit\n')
  raise SystemExit(0 if committed==b'commit: ok\n' and transaction.returncode==0 else 1)
finally:
 try:
  if os.name=='nt': os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
  else: fcntl.flock(fd,fcntl.LOCK_UN)
 finally: os.close(fd)
PY
  )"
  local python_result=$? observed
  if [ "$python_result" -eq 0 ] && [ "$update_result" = "$(printf 'NO_COMMIT\t%s\t%s\t%s' "$1" "$2" "$3")" ]; then
    controller_ref_readback_uncertain=0
    return 1
  fi
  [ "$python_result" -eq 0 ] && [ -z "$update_result" ] || return 1
  # A successful interpreter return is not evidence that the ref was written.
  if observed="$(git rev-parse --verify "$1" 2>/dev/null)" && [ "$observed" = "$2" ]; then
    controller_ref_readback_uncertain=0
    return 0
  fi
  controller_ref_readback_uncertain=1
  return 1
}

canonical_generation() {
  local value="$1" digits ordinal
  if [[ "$value" =~ ^G([0-9A-F]{4})$ ]]; then
    digits="${BASH_REMATCH[1]}"
    ordinal=$((16#$digits))
    [ "$ordinal" -ge 1 ] || return 1
  elif [[ "$value" =~ ^e([1-9][0-9]*)$ ]]; then
    digits="${BASH_REMATCH[1]}"
    [ "${#digits}" -le 5 ] || return 1
    ordinal=$((10#$digits))
    [ "$ordinal" -le 65535 ] || return 1
  else
    return 1
  fi
  printf 'G%04X\n' "$ordinal"
}

controller_io() {
  local a="$1" c="$2" repo common ref oid s rc rg root rr target_common; shift 2
  repo="$(git rev-parse --path-format=absolute --show-toplevel)" || return
  common="$(cd "$(git rev-parse --path-format=absolute --git-common-dir)" && pwd -P)" || return
  if [ "$a" = current ] && [ -z "$c" ]; then
    local x=(); mapfile -t x < <(git for-each-ref --format='%(refname)' refs/implementaudit/controllers/)
    [ "${#x[@]}" = 1 ] || { printf 'claim-run.sh: ambiguous controller population: %s\n' "${#x[@]}" >&2; return 1; }
    c="${x[0]##*/}"
  fi
  case "$c" in ''|*[!a-z0-9-]*|-*) return 1;; esac
  [ "${#c}" -le 48 ] || return 1; ref="refs/implementaudit/controllers/$c"
  load() {
    oid="$(git rev-parse --verify "$ref" 2>/dev/null)" || return
    IFS=$'\t' read -r s rc rg root <<< "$(git cat-file blob "$oid")"
    rr="${root%/.IMPLEMENTAUDIT/runs/*}"
    target_common="$(cd "$(git -C "$rr" rev-parse --path-format=absolute --git-common-dir)" && pwd -P)" || return
    [ "$s:$rc" = "implementaudit.controller-current.v1:$c" ] &&
      [ "$target_common" = "$common" ] &&
      bash "$(dirname "$0")/validate-run-root.sh" --claim-only "$root" --repo-root "$rr" >/dev/null 2>&1 &&
      grep -Fxq "claim_id=$rg" "$root/.claimed"
  }
  load_invalidation() {
    iref="refs/implementaudit/continuity-invalidations/$c"
    ioid="$(git rev-parse --verify "$iref" 2>/dev/null || printf none)"
    [ "$ioid" = none ] && return 0
    IFS=$'\t' read -r is ic io irg ib ie <<< "$(git cat-file blob "$ioid")"
    [ "$is:$ic:$io:$irg" = "implementaudit.continuity-invalidation.v1:$c:$oid:$rg" ] &&
      case "$ib" in host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap) true;; *) false;; esac &&
      [ -n "$ie" ]
  }
  case "$a" in
    bind)
      [ "$#" = 2 ] && [ "$base" = .IMPLEMENTAUDIT/runs ] || return 1
      local expect="$1" run="$2" old new newclaim zero=0000000000000000000000000000000000000000
      newclaim="$(sed -n 's/^claim_id=//p' "$repo/$run/.claimed")"; [ -n "$newclaim" ] || return
      old="$(git rev-parse --verify "$ref" 2>/dev/null || printf %s "$zero")"
      if [ "$old" != "$zero" ]; then
        IFS=$'\t' read -r s rc rg _ <<< "$(git cat-file blob "$old")"
        [ -n "$expect" ] && [ "$s:$rc:$rg" = "implementaudit.controller-current.v1:$c:$expect" ] || return 1
      else [ -z "$expect" ] || return 1; fi
      new="$(printf 'implementaudit.controller-current.v1\t%s\t%s\t%s/%s\n' "$c" "$newclaim" "$repo" "$run" | git hash-object -w --stdin)" &&
        update_controller_ref "$ref" "$new" "$old" ;;
    current)
      load || return; printf '%s\t%s\t%s\t%s\n' "$c" "$rr" "$root" "$rg" ;;
    invalidate)
      load || return; [ "$repo" = "$rr" ] || return 1
      local b="$1" event="$2" iref="refs/implementaudit/continuity-invalidations/$c" old new zero=0000000000000000000000000000000000000000
      case "$b" in host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap):;; *) return 1;; esac
      case "$event" in ''|*$'\t'*|*$'\r'*|*$'\n'*) return 1;; esac
      old="$(git rev-parse --verify "$iref" 2>/dev/null || printf %s "$zero")"
      if [ "$old" != "$zero" ]; then
        IFS=$'\t' read -r is ic io irg ib ie <<< "$(git cat-file blob "$old")"
        [ "$is" = implementaudit.continuity-invalidation.v1 ] || return 1
        if [ "$ic:$io:$irg:$ib:$ie" = "$c:$oid:$rg:$b:$event" ]; then printf '%s@%s\n' "$iref" "$old"; return; fi
      fi
      new="$(printf 'implementaudit.continuity-invalidation.v1\t%s\t%s\t%s\t%s\t%s\n' "$c" "$oid" "$rg" "$b" "$event" | git hash-object -w --stdin)" &&
        update_controller_ref "$iref" "$new" "$old" || return
      printf '%s@%s\n' "$iref" "$new" ;;
    resume|verify|require)
      load || return; [ "$repo" = "$rr" ] || return 1
      local state="$root/STATE.md" road="$root/ROADMAP.md" token rref roid h t sh rh iref ioid is ic io irg ib ie
      h="$(git rev-parse HEAD)"; t="$(git rev-parse 'HEAD^{tree}')"
      sh="$(sha256sum "$state" | cut -d' ' -f1)"; rh="$(sha256sum "$road" | cut -d' ' -f1)"
      load_invalidation || return
      if [ "$a" = resume ]; then
        local b="$1" e="$2" next newr zero=0000000000000000000000000000000000000000
        case "$b" in host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap):;; *) return 1;; esac
        e="$(canonical_generation "$e")" || return
        [ "$ioid" = none ] || [ "$ib" = "$b" ] || return 1
        next="$(awk -F'|' -v e="$e" -v b="$b" -v h="$h" -v t="$t" 'function q(x){gsub(/^[ \t`]+|[ \t`]+$/, "", x);return x} /^Current epoch:/{ce=$0} q($2)=="Next action"{n=q($3)} q($2)==e&&q($3)==b&&q($6)=="yes"&&index($5,h)&&index($5,t){ok=1} END{if(ce=="Current epoch: "e&&ok&&n!=""&&n!="-"&&tolower(n)!="none"&&tolower(n)!="pending")print n;else exit 1}' "$state")" || return
        rref="refs/implementaudit/continuity-receipts/$c/$e"
        newr="$(printf 'implementaudit.continuity-receipt.v2\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$oid" "$rg" "$h" "$t" "$sh" "$rh" "$ioid" "$b" "$e" "$next" | git hash-object -w --stdin)" &&
          git update-ref "$rref" "$newr" "$zero" || return
        token="$rref@$newr"
      else
        if [ "$a" = require ]; then
          e2="$(sed -n 's/^Current epoch: //p' "$state")"
          case "$e2" in ''|*[!a-zA-Z0-9-]*) return 1;; esac
          rref="refs/implementaudit/continuity-receipts/$c/$e2"; roid="$(git rev-parse --verify "$rref" 2>/dev/null)" || return
          token="$rref@$roid"
        else token="$1"; rref="${token%@*}"; roid="${token##*@}"; fi
        [ "$(git rev-parse --verify "$rref" 2>/dev/null)" = "$roid" ] || return
        record="$(git cat-file blob "$roid")"; s="${record%%$'\t'*}"
        case "$s" in
          implementaudit.continuity-receipt.v1)
            IFS=$'\t' read -r s rc owner rg2 h2 t2 sh2 rh2 b2 e2 _ <<< "$record"
            [ "$ioid" = none ] && [ "$s:$rc:$owner:$rg2:$h2:$t2:$sh2:$rh2" = "implementaudit.continuity-receipt.v1:$c:$oid:$rg:$h:$t:$sh:$rh" ] || return ;;
          implementaudit.continuity-receipt.v2)
            IFS=$'\t' read -r s rc owner rg2 h2 t2 sh2 rh2 io2 b2 e2 next2 <<< "$record"
            [ "$s:$rc:$owner:$rg2:$h2:$t2:$sh2:$rh2:$io2" = "implementaudit.continuity-receipt.v2:$c:$oid:$rg:$h:$t:$sh:$rh:$ioid" ] || return
            [ "$io2" = none ] || [ "$ib" = "$b2" ] || return
            state_next="$(awk -F'|' -v e="$e2" -v b="$b2" -v h="$h" -v t="$t" 'function q(x){gsub(/^[ \t`]+|[ \t`]+$/, "", x);return x} /^Current epoch:/{ce=$0} q($2)=="Next action"{n=q($3)} q($2)==e&&q($3)==b&&q($6)=="yes"&&index($5,h)&&index($5,t){ok=1} END{if(ce=="Current epoch: "e&&ok&&n!=""&&n!="-"&&tolower(n)!="none"&&tolower(n)!="pending")print n;else exit 1}' "$state")" || return
            [ "$state_next" = "$next2" ] || return ;;
          *) return 1;;
        esac
        [ "$rref" = "refs/implementaudit/continuity-receipts/$c/$e2" ] || return
      fi
      printf '%s\n' "$token" ;;
    *) return 1 ;;
  esac
}

# The companion is the existing claim owner implementation. Exit 3 means only
# physical absence of both migration authorities; every other refusal is final.
rotation_io() {
  local rotation_py
  rotation_py="$(select_claim_python)" || {
    printf 'claim-run.sh: a supported physical Python 3 interpreter is required; set IMPLEMENTAUDIT_PYTHON to its absolute path\n' >&2
    return 1
  }
  # Select the companion before any of its code can run. These literals belong
  # to this shell source; a new companion requires a reviewed paired binding.
  "$rotation_py" -B -c '
import sys
script_import_path = bool(sys.path and sys.path[0] == "")
if script_import_path:
    sys.path.pop(0)
import hashlib
import importlib.machinery
import os
from pathlib import Path
import stat
import types

argument_path = sys.argv[1]
path = Path(os.path.abspath(argument_path))
expected_bytes = 259408
expected_sha256 = "551b1a798161fdd20cb9eebd56fb1d8a0245ec48a74f05b29f6253d8228c49cb"
nodes = []
descriptor = None
def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_ctime_ns, info.st_mtime_ns)
def directory_identity(info):
    if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ValueError("ancestor is not an ordinary directory")
    return info.st_dev, info.st_ino, info.st_mode
try:
    if os.name == "posix":
        if (not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")
                or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd):
            raise ValueError("retained source directory capability is unavailable")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        parent = None
        for name in (path.anchor, *path.parts[1:-1]):
            current = os.open(name, flags, dir_fd=parent)
            nodes.append((parent, name, current, directory_identity(os.fstat(current))))
            parent = current
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
    else:
        for ancestor in reversed(path.parents):
            nodes.append((ancestor, directory_identity(os.lstat(ancestor))))
        before = os.lstat(path)
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or getattr(before, "st_file_attributes", 0) & 0x400
            or before.st_size != expected_bytes):
        raise ValueError("is not the selected bounded single-link regular file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = (os.open(path.name, flags, dir_fd=parent) if os.name == "posix"
                  else os.open(path, flags))
    with os.fdopen(descriptor, "rb") as stream:
        descriptor = None
        opened = os.fstat(stream.fileno())
        raw = stream.read(expected_bytes + 1)
        after = os.fstat(stream.fileno())
        current = (os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                   if os.name == "posix" else os.lstat(path))
        if not identity(before) == identity(opened) == identity(after) == identity(current):
            raise ValueError("identity changed during bounded capture")
        if os.name == "posix":
            for ancestor, name, held, selected in nodes:
                live = os.stat(name, dir_fd=ancestor, follow_symlinks=False)
                if directory_identity(live) != selected or directory_identity(os.fstat(held)) != selected:
                    raise ValueError("directory identity changed during capture")
        else:
            for ancestor, selected in nodes:
                if directory_identity(os.lstat(ancestor)) != selected:
                    raise ValueError("directory identity changed during capture")
        if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise ValueError("bytes differ from the selected owner")
except (OSError, ValueError) as exc:
    print("claim-run.sh: companion source " + str(exc), file=sys.stderr)
    raise SystemExit(1)
finally:
    if descriptor is not None:
        os.close(descriptor)
    if os.name == "posix":
        for _, _, held, _ in reversed(nodes):
            os.close(held)

# Preserve script invocation semantics while compiling only the verified buffer.
sys.argv = [argument_path, *sys.argv[2:]]
if script_import_path:
    sys.path.insert(0, str(path.parent))
module = types.ModuleType("__main__")
module.__file__ = str(path)
module.__package__ = None
module.__spec__ = None
module.__cached__ = None
module.__loader__ = importlib.machinery.SourceFileLoader("__main__", str(path))
sys.modules["__main__"] = module
exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize), module.__dict__)
' "$(dirname "$0")/claim-run-rotation.py" "$@"
}

controller='' supersede='' deferred='' boundary='' event=''
case "${1:-}" in
  --rotate-canonical-state|--recover-canonical-state|--read-current-state|--read-canonical-state|--resolve-canonical-generation|--resolve-retained-continuity-predecessor|--resolve-resume-generation|--read-resume-state|--prepare-c02-correction|--append-c02-correction|--apply-c02-correction)
    rotation_operation="$1"; controller="${2:-}"; shift 2
    case "$rotation_operation" in
      --rotate-canonical-state) rotation_operation=rotate ;;
      --recover-canonical-state) rotation_operation=recover ;;
      --read-current-state) rotation_operation=read ;;
      --read-canonical-state) rotation_operation=read-role ;;
      --resolve-canonical-generation) rotation_operation=resolve ;;
      --resolve-retained-continuity-predecessor) rotation_operation=resolve-retained-predecessor ;;
      --resolve-resume-generation) rotation_operation=resolve-resume ;;
      --read-resume-state) rotation_operation=read-resume ;;
      --prepare-c02-correction) rotation_operation=c02-prepare ;;
      --append-c02-correction) rotation_operation=c02-append ;;
      --apply-c02-correction) rotation_operation=c02-apply ;;
    esac
    rotation_io "$rotation_operation" "$controller" "$@"; exit $? ;;
  --current-controller) controller_io current "${2:-}"; exit $? ;;
  --resume-controller)
    controller="${2:-}"; shift 2; boundary='' epoch='' expected_pointer='' expected_invalidation=''
    while [ "$#" -gt 0 ]; do
      [ "$#" -ge 2 ] || { printf 'claim-run.sh: resume argument is missing a value\n' >&2; exit 1; }
      case "$1" in
        --boundary) boundary="$2" ;;
        --epoch) epoch="$2" ;;
        --expected-pointer) [ -z "$expected_pointer" ] || exit 1; expected_pointer="$2" ;;
        --expected-invalidation) [ -z "$expected_invalidation" ] || exit 1; expected_invalidation="$2" ;;
        *) printf 'claim-run.sh: unknown resume argument: %s\n' "$1" >&2; exit 1 ;;
      esac
      shift 2
    done
    rotation_io resume "$controller" "$boundary" "$epoch" "$expected_pointer" "$expected_invalidation"; rotation_status=$?
    [ "$rotation_status" -eq 3 ] || exit "$rotation_status"
    [ -z "$expected_pointer$expected_invalidation" ] || { printf 'claim-run.sh: migrated resume tokens cannot route through legacy continuity\n' >&2; exit 1; }
    controller_io resume "$controller" "$boundary" "$epoch"; exit $? ;;
  --verify-resume-receipt)
    receipt_arg="${2:-}"; controller="${receipt_arg%@*}"; controller="${controller#refs/implementaudit/continuity-receipts/}"; controller="${controller%/*}"
    rotation_io verify "$controller" "$receipt_arg"; rotation_status=$?
    [ "$rotation_status" -eq 3 ] || exit "$rotation_status"
    controller_io verify "$controller" "$receipt_arg"; exit $? ;;
  --require-current-continuity)
    rotation_io require "${2:-}"; rotation_status=$?
    [ "$rotation_status" -eq 3 ] || exit "$rotation_status"
    controller_io require "${2:-}"; exit $? ;;
  --invalidate-continuity)
    controller="${2:-}"; shift 2; deferred=invalidate
    while [ "$#" -gt 0 ]; do case "$1" in --boundary) boundary="${2:-}"; shift 2;; --event) event="${2:-}"; shift 2;; *) printf 'claim-run.sh: unknown invalidation argument: %s\n' "$1" >&2; exit 1;; esac; done ;;
  --controller)
    controller="${2:-}"; shift 2
    if [ "${1:-}" = --supersede-claim ]; then supersede="${2:-}"; shift 2; fi ;;
esac

# Resolve migrated ownership before any legacy preflight can consult inherited
# Git directory/worktree environment. Only exact physical absence falls through.
if [ "$deferred" = invalidate ]; then
  rotation_io invalidate "$controller" "$boundary" "$event"; rotation_status=$?
  [ "$rotation_status" -eq 3 ] || exit "$rotation_status"
fi

mode=full
if [ "${1:-}" = "--micro" ]; then
  mode=micro
  shift
fi

case "$mode" in
  full) template_set="STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md" ;;
  micro) template_set="STATE.md" ;;
esac

slug="$(printf '%s' "${1:-}" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -c 'a-z0-9' '-' \
  | sed -E 's/-+/-/g; s/^-//; s/-$//' \
  | cut -c1-48 \
  | sed -E 's/-$//')"
[ -n "$slug" ] || slug="run"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  preflight_repo="$(git rev-parse --path-format=absolute --show-toplevel)" || exit 1
  reject_coordination_reparse "$preflight_repo/.IMPLEMENTAUDIT" || {
    printf "claim-run.sh: run and coordination custody contains a symlink or reparse point: '%s/.IMPLEMENTAUDIT'\n" "$preflight_repo" >&2
    exit 1
  }
  gate_dir="$preflight_repo/.IMPLEMENTAUDIT/.r36-locks"
  gate="$gate_dir/namespace.gate"
  reject_coordination_reparse "$gate_dir" || {
    printf "claim-run.sh: governed-writer namespace custody contains a symlink or reparse point: '%s'\n" "$gate_dir" >&2
    exit 1
  }
  mkdir -p "$gate_dir" || exit 1
  if [ ! -e "$gate" ]; then
    ( set -C; printf '\0' > "$gate" ) 2>/dev/null || true
  fi
  [ -f "$gate" ] && [ ! -L "$gate" ] && [ "$(wc -c < "$gate" | tr -d ' ')" = 1 ] \
    && [ "$(find "$gate" -maxdepth 0 -links 1 -print 2>/dev/null)" = "$gate" ] || {
    printf "claim-run.sh: governed-writer namespace gate is unsafe: '%s'\n" "$gate" >&2
    exit 1
  }
fi

if [ "$deferred" = invalidate ]; then
  controller_io invalidate "$controller" "$boundary" "$event"; exit $?
fi

mkdir -p "$base" || {
  printf "claim-run.sh: cannot create base dir '%s'\n" "$base" >&2
  exit 1
}

run_root="$(mktemp -d "$base/${slug}-XXXXXX" 2>/dev/null)" || {
  printf "claim-run.sh: mktemp failed to claim a run dir under '%s'\n" "$base" >&2
  exit 1
}

claimed_at_utc="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  claim_repo="$(git rev-parse --path-format=absolute --show-toplevel)" || exit 1
  claim_common="$(git rev-parse --path-format=absolute --git-common-dir)" || exit 1
  claim_id="$(LC_ALL=C od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
  claim_name="$(basename "$run_root")"
  { printf 'schema=implementaudit.run-claim.v2\nclaim_id=%s\nclaimed_at_utc=%s\nmode=%s\ntemplates=%s\n' "$claim_id" "$claimed_at_utc" "$mode" "$template_set"; printf 'repo_root=%s\ngit_common_dir=%s\nrun_base=%s\nrun_root=%s\nrun_name=%s\n' "$claim_repo" "$claim_common" "$base" "$run_root" "$claim_name"; } > "$run_root/.claimed"
else
  printf 'claimed_at_utc=%s\nmode=%s\ntemplates=%s\n' "$claimed_at_utc" "$mode" "$template_set" > "$run_root/.claimed"
fi
if [ ! -f "$run_root/.claimed" ]; then
  printf "claim-run.sh: cannot write claim sentinel '%s/.claimed'\n" "$run_root" >&2
  rmdir "$run_root" 2>/dev/null || true
  exit 1
fi

if [ -n "$controller" ]; then
  ( set -C; printf 'controller_id=%s\n' "$controller" > "$run_root/.controller" ) 2>/dev/null || {
    rm -f "$run_root/.claimed"; rmdir "$run_root" 2>/dev/null; exit 1
  }
  controller_io bind "$controller" "$supersede" "$run_root" || {
    if [ "$controller_ref_readback_uncertain" = 1 ]; then
      printf "claim-run.sh: controller ref readback is unverified; retained claim: '%s'\n" "$run_root" >&2
      exit 1
    fi
    rm -f "$run_root/.controller" "$run_root/.claimed"; rmdir "$run_root" 2>/dev/null; exit 1
  }
fi

for sibling in "$base"/*; do
  [ -d "$sibling" ] || continue
  [ "$sibling" = "$run_root" ] && continue
  sibling_state="$sibling/STATE.md"
  if [ ! -f "$sibling_state" ] || ! grep -Eq \
    '^(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF|COMPLETE|HANDOFF|SUPERSEDED_BY:[[:space:]].+|PARALLEL:[[:space:]].+)$' \
    "$sibling_state"; then
    printf 'claim-run: undispositioned sibling root: %s\n' "$sibling" >&2
  fi
done

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if ! git check-ignore -q "$base" 2>/dev/null; then
    printf 'claim-run: note: %s is not gitignored here; consider adding ".IMPLEMENTAUDIT/" to .git/info/exclude (local-only) so run artifacts stay out of commits and evidence\n' "$base" >&2
  fi
fi

printf '%s\n' "$run_root"
