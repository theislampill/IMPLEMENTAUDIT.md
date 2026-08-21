#!/usr/bin/env bash
# Atomically claim native run roots and controller continuity.

set -u

base="${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"

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
  local py=()
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else return 1; fi
  "${py[@]}" - "$gate" "$1" "$2" "$3" <<'PY'
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
 raise SystemExit(subprocess.run(['git','update-ref',ref,new,old],check=False).returncode)
finally:
 try:
  if os.name=='nt': os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
  else: fcntl.flock(fd,fcntl.LOCK_UN)
 finally: os.close(fd)
PY
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

publication_custody_io() {
  # Read-only Task-4 boundary: repository authority is this installed owner's
  # physical checkout, never the caller's cwd or a supplied path/ref.
  local owner_dir repo common refs ref c oid s rc rg root rr target_common run_rel
  local lines=() keys=(schema claim_id claimed_at_utc mode templates repo_root git_common_dir run_base run_root run_name)
  owner_dir="$(cd "$(dirname "$0")/../../.." && pwd -P)" || return 1
  repo="$(git -C "$owner_dir" rev-parse --path-format=absolute --show-toplevel)" || return 1
  common="$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)" || return 1
  mapfile -t refs < <(git -C "$repo" for-each-ref --format='%(refname)' refs/implementaudit/controllers/)
  [ "${#refs[@]}" = 1 ] || return 1
  ref="${refs[0]}"; c="${ref##*/}"
  case "$c" in ''|*[!a-z0-9-]*|-*) return 1;; esac
  oid="$(git -C "$repo" rev-parse --verify "$ref" 2>/dev/null)" || return 1
  IFS=$'\t' read -r s rc rg root <<< "$(git -C "$repo" cat-file blob "$oid")"
  rr="${root%/.IMPLEMENTAUDIT/runs/*}"
  target_common="$(git -C "$rr" rev-parse --path-format=absolute --git-common-dir)" || return 1
  [ "$s:$rc" = "implementaudit.controller-current.v1:$c" ] &&
    [ "$target_common" = "$common" ] || return 1
  bash "$(dirname "$0")/validate-run-root.sh" --claim-only "$root" --repo-root "$rr" >/dev/null 2>&1 || return 1
  mapfile -t lines < "$root/.claimed" || return 1
  [ "${#lines[@]}" = 10 ] || return 1
  local index key value
  for index in "${!keys[@]}"; do
    key="${keys[$index]}"; value="${lines[$index]}"
    case "$value" in "$key"=*) ;; *) return 1;; esac
  done
  [ "${lines[0]}" = "schema=implementaudit.run-claim.v2" ] || return 1
  [ "${lines[1]}" = "claim_id=$rg" ] || return 1
  run_rel="${root#"$rr"/}"
  [ "$run_rel" != "$root" ] || return 1
  [ "${lines[5]}" = "repo_root=$rr" ] && [ "${lines[6]}" = "git_common_dir=$target_common" ] &&
    [ "${lines[7]}" = "run_base=.IMPLEMENTAUDIT/runs" ] &&
    [ "${lines[8]}" = "run_root=$run_rel" ] &&
    [ "${lines[9]}" = "run_name=$(basename "$root")" ] || return 1
  printf 'implementaudit.publication-custody.v1\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$c" "$oid" "$rg" "$rr" "$target_common" "$root" "${lines[9]#run_name=}"
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
  generation_ref_state() {
    local candidate="$1" candidate_path common_dir
    if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
      printf 'RESOLVED\n'
      return
    fi
    candidate_path="$(git rev-parse --git-path "$candidate")" || return 1
    common_dir="$(git rev-parse --path-format=absolute --git-common-dir)" || return 1
    if [ -e "$candidate_path" ] || [ -L "$candidate_path" ] || \
       { [ -f "$common_dir/packed-refs" ] && awk -v r="$candidate" '$1 !~ /^#/ && $2 == r { found=1 } END { exit !found }' "$common_dir/packed-refs"; }; then
      printf 'BROKEN\n'
    else
      printf 'ABSENT\n'
    fi
  }
  load_current_generation() {
    pointer_state="$(generation_ref_state "$pref")" || return 1
    poid=''; precord=''
    [ "$pointer_state" = RESOLVED ] || return 0
    poid="$(git rev-parse --verify "$pref" 2>/dev/null)" || { pointer_state=BROKEN; return 0; }
    [ "$(git cat-file -t "$poid" 2>/dev/null)" = blob ] || { pointer_state=MALFORMED; return 0; }
    precord="$(git cat-file blob "$poid")" || { pointer_state=MALFORMED; return 0; }
    case "$precord" in *$'\n'*|*$'\r'*) pointer_state=MALFORMED;; esac
    case "$precord" in *$'\t'*) ;; *) pointer_state=MALFORMED;; esac
  }
  load_generation_migration() {
    marker_state="$(generation_ref_state "$mref")" || return 1
    moid=''; mrecord=''
    [ "$marker_state" = RESOLVED ] || return 0
    moid="$(git rev-parse --verify "$mref" 2>/dev/null)" || { marker_state=BROKEN; return 0; }
    [ "$(git cat-file -t "$moid" 2>/dev/null)" = blob ] || { marker_state=MALFORMED; return 0; }
    mrecord="$(git cat-file blob "$moid")" || { marker_state=MALFORMED; return 0; }
    case "$mrecord" in *$'\n'*|*$'\r'*) marker_state=MALFORMED;; esac
  }
  load_live_generation_state() {
    live_epoch="$(sed -n 's/^Current epoch: //p' "$state")"
    case "$live_epoch" in G[0-9A-F][0-9A-F][0-9A-F][0-9A-F]) ;; *) return 1;; esac
    live_next="$(awk -F'|' -v e="$live_epoch" -v h="$h" -v t="$t" 'function q(x){gsub(/^[ \t`]+|[ \t`]+$/, "", x);return x} q($2)=="Next action"{n=q($3)} q($2)==e&&q($6)=="yes"&&index($5,h)&&index($5,t){ok=1} END{if(ok&&n!=""&&n!="-"&&tolower(n)!="none"&&tolower(n)!="pending")print n;else exit 1}' "$state")" || return 1
  }
  load_generation_predecessor() {
    local predecessor="$1" predecessor_ref predecessor_oid predecessor_record predecessor_schema
    case "$predecessor" in *@*) predecessor_ref="${predecessor%@*}"; predecessor_oid="${predecessor##*@}";; *) return 1;; esac
    [[ "$predecessor_ref" =~ ^refs/implementaudit/continuity-receipts/$c/[A-Za-z0-9-]+$ ]] || return 1
    [[ "$predecessor_oid" =~ ^[0-9a-f]{40}$ ]] || return 1
    [ "$(git rev-parse --verify "$predecessor_ref" 2>/dev/null)" = "$predecessor_oid" ] || return 1
    [ "$(git cat-file -t "$predecessor_oid" 2>/dev/null)" = blob ] || return 1
    predecessor_record="$(git cat-file blob "$predecessor_oid")" || return 1
    case "$predecessor_record" in *$'\n'*|*$'\r'*) return 1;; esac
    predecessor_schema="${predecessor_record%%$'\t'*}"
    case "$predecessor_schema" in
      implementaudit.continuity-receipt.v2)
        IFS=$'\t' read -r predecessor_schema prc powner pclaim _ <<< "$predecessor_record"
        [ "$predecessor_schema:$prc:$powner:$pclaim" = "implementaudit.continuity-receipt.v2:$c:$oid:$rg" ] || return 1;;
      implementaudit.continuity-receipt.v3)
        IFS=$'\t' read -r predecessor_schema prc pclaim prun _ <<< "$predecessor_record"
        [ "$predecessor_schema:$prc:$pclaim:$prun" = "implementaudit.continuity-receipt.v3:$c:$rg:$run_identity" ] || return 1;;
      *) return 1;;
    esac
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
      if [ "$a" = require ]; then
        local pref="refs/implementaudit/current-generations/$c" mref="refs/implementaudit/current-generation-migrations/$c"
        local poid moid precord mrecord vrecord run_identity pointer_state marker_state live_epoch live_next
        local ps pc pclaim prun pgen pep pinv ppred pvref pproj psh prh pph pah pnext pextra
        local vs vc vclaim vrun vep vinv vpref vpoid vsh vrh vph vah vnext vpred vextra void
        local ms mc mclaim mrun mep mpref mpschema mvref mvoid mterminal mextra
        load_current_generation || return
        load_generation_migration || return
        if [ "$pointer_state" != ABSENT ] || [ "$marker_state" != ABSENT ]; then
          if [ "$pointer_state" != RESOLVED ]; then
            [ "$marker_state" = ABSENT ] || printf 'claim-run.sh: STOP_NO_ROOT_FALLBACK: migration marker exists without a readable current-generation pointer\n' >&2
            return 1
          fi
          if [ "$pointer_state" = MALFORMED ]; then
            [ "$marker_state" = ABSENT ] || printf 'claim-run.sh: STOP_NO_ROOT_FALLBACK: migration marker exists with a malformed current-generation pointer\n' >&2
            return 1
          fi
          if [ "$marker_state" = BROKEN ]; then
            printf 'claim-run.sh: STOP_NO_ROOT_FALLBACK: migration marker exists but is unreadable\n' >&2
            return 1
          fi
          if [ "$marker_state" = MALFORMED ]; then
            return 1
          fi
          IFS=$'\t' read -r ps pc pclaim prun pgen pep pinv ppred pvref pproj psh prh pph pah pnext pextra <<< "$precord"
          if ! { [ -n "$ps" ] && [ -n "$pc" ] && [ -n "$pclaim" ] && [ -n "$prun" ] &&
             [ -n "$pgen" ] && [ -n "$pep" ] && [ -n "$pinv" ] && [ -n "$ppred" ] &&
             [ -n "$pvref" ] && [ -n "$pproj" ] && [ -n "$psh" ] && [ -n "$prh" ] &&
             [ -n "$pph" ] && [ -n "$pah" ] && [ -n "$pnext" ] && [ -z "$pextra" ]; }; then
            [ "$marker_state" = ABSENT ] || return 1
            return 1
          fi
          run_identity="${root#"$repo"/}"
          [ "$run_identity" != "$root" ] || return 1
          [ "$ps:$pc:$pclaim:$prun" = "implementaudit.current-generation.v1:$c:$rg:$run_identity" ] || return 1
          [[ "$pgen" =~ ^g[0-9a-f]{4}$ && "$pep" =~ ^G[0-9A-F]{4}$ && "$pinv" =~ ^[0-9a-f]{40}$ ]] || return 1
          [ "$pvref" = "refs/implementaudit/continuity-receipts/$c/$pep" ] || return 1
          [ "$pproj" = implementaudit.canonical-state-projection.v1 ] || return 1
          [[ "$psh:$prh:$pph:$pah" =~ ^[0-9a-f]{64}:[0-9a-f]{64}:[0-9a-f]{64}:[0-9a-f]{64}$ ]] || return 1
          case "$pnext" in *$'\t'*|*$'\r'*|*$'\n'*) return 1;; esac
          load_live_generation_state || return 1
          [ "$pinv:$psh:$prh:$pep:$pnext" = "$ioid:$sh:$rh:$live_epoch:$live_next" ] || return 1
          load_generation_predecessor "$ppred" || return 1

          void="$(git rev-parse --verify "$pvref" 2>/dev/null)" || return 1
          [ "$(git cat-file -t "$void" 2>/dev/null)" = blob ] || return 1
          vrecord="$(git cat-file blob "$void")" || return 1
          case "$vrecord" in *$'\n'*|*$'\r'*) return 1;; esac
          IFS=$'\t' read -r vs vc vclaim vrun vep vinv vpref vpoid vsh vrh vph vah vnext vpred vextra <<< "$vrecord"
          [ -z "$vextra" ] &&
            [ "$vs:$vc:$vclaim:$vrun:$vep:$vinv:$vpref:$vpoid" = "implementaudit.continuity-receipt.v3:$c:$rg:$run_identity:$pep:$pinv:$pref:$poid" ] &&
            [ "$vsh:$vrh:$vph:$vah:$vnext:$vpred" = "$psh:$prh:$pph:$pah:$pnext:$ppred" ] &&
            [ "$ppred" != "$pvref@$void" ] || return 1

          if [ "$marker_state" = ABSENT ]; then
            printf 'claim-run.sh: FIRST_MIGRATION_INCOMPLETE: current-generation pointer and v3 receipt exist without a migration marker\n' >&2
            return 1
          fi
          IFS=$'\t' read -r ms mc mclaim mrun mep mpref mpschema mvref mvoid mterminal mextra <<< "$mrecord"
          [ -z "$mextra" ] &&
            [ "$ms:$mc:$mclaim:$mrun:$mep" = "implementaudit.current-generation-migration.v1:$c:$rg:$run_identity:$pep" ] &&
            [ "$mpref:$mpschema:$mvref:$mvoid:$mterminal" = "$pref:implementaudit.current-generation.v1:$pvref:$void:true" ] || return 1
          printf '%s@%s\n' "$pvref" "$void"
          return
        fi
      fi
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
            [ "$a" != require ] || return 1
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

controller='' supersede='' deferred='' boundary='' event=''
case "${1:-}" in
  --publication-custody) publication_custody_io; exit $? ;;
  --current-controller) controller_io current "${2:-}"; exit $? ;;
  --resume-controller)
    controller="${2:-}"; shift 2; boundary='' epoch=''
    while [ "$#" -gt 0 ]; do case "$1" in --boundary) boundary="${2:-}"; shift 2;; --epoch) epoch="${2:-}"; shift 2;; *) printf 'claim-run.sh: unknown resume argument: %s\n' "$1" >&2; exit 1;; esac; done
    controller_io resume "$controller" "$boundary" "$epoch"; exit $? ;;
  --verify-resume-receipt)
    receipt_arg="${2:-}"; controller="${receipt_arg%@*}"; controller="${controller#refs/implementaudit/continuity-receipts/}"; controller="${controller%/*}"
    controller_io verify "$controller" "$receipt_arg"; exit $? ;;
  --require-current-continuity) controller_io require "${2:-}"; exit $? ;;
  --invalidate-continuity)
    controller="${2:-}"; shift 2; deferred=invalidate
    while [ "$#" -gt 0 ]; do case "$1" in --boundary) boundary="${2:-}"; shift 2;; --event) event="${2:-}"; shift 2;; *) printf 'claim-run.sh: unknown invalidation argument: %s\n' "$1" >&2; exit 1;; esac; done ;;
  --controller)
    controller="${2:-}"; shift 2
    if [ "${1:-}" = --supersede-claim ]; then supersede="${2:-}"; shift 2; fi ;;
esac

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
