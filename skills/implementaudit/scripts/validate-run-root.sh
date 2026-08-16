#!/usr/bin/env bash

set -uo pipefail

err_count=0
err() {
  printf 'validate-run-root: ERROR: %s\n' "$*" >&2
  err_count=$((err_count + 1))
}
warn() { printf 'validate-run-root: WARNING: %s\n' "$*" >&2; }
has_non_whitespace() { LC_ALL=C grep -q '[^[:space:]]' "$1" 2>/dev/null; }

if [ "${1:-}" = "--claim-only" ]; then
  run_arg="${2:-}"; [ "${3:-}" = "--repo-root" ] && repo_arg="${4:-}" || repo_arg=""
  [ -n "$run_arg" ] && [ -n "$repo_arg" ] && [ "$#" -eq 4 ] || { printf 'usage: validate-run-root.sh --claim-only <run-root> --repo-root <repo-root>\n' >&2; exit 2; }
  if command -v python >/dev/null 2>&1; then claim_py=(python)
  elif command -v python3 >/dev/null 2>&1; then claim_py=(python3)
  elif command -v py >/dev/null 2>&1; then claim_py=(py -3)
  else printf 'validate-run-root: Python is required for strict claim validation\n' >&2; exit 2; fi
  "${claim_py[@]}" - "$run_arg" "$repo_arg" <<'PY'
import datetime,os,re,stat,subprocess,sys
from pathlib import Path
run_arg,repo_arg=sys.argv[1:]
def die(s): print('validate-run-root: '+s,file=sys.stderr); raise SystemExit(1)
def canon(p): return os.path.normcase(os.path.abspath(p))
def unsafe(p):
 try: st=os.lstat(p)
 except OSError: die(f'custody path missing: {p}')
 return stat.S_ISLNK(st.st_mode) or bool(getattr(st,'st_file_attributes',0)&0x400)
def lexical_path(raw,base,label):
 if '\x00' in raw: die(f'{label} contains NUL')
 parts=re.split(r'[/\\]+',raw)
 if any(part in ('.','..') for part in parts): die(f'{label} contains a lexical dot alias')
 p=Path(raw)
 if not p.is_absolute():
  if base is None: die(f'{label} must be absolute')
  p=base/p
 chain=Path(p.anchor)
 for part in p.parts[1:]:
  chain=chain/part
  if unsafe(chain): die(f'{label} custody path is symlink/reparse: {chain}')
 return p
repo=lexical_path(repo_arg,None,'repo root')
run=lexical_path(run_arg,repo,'run root')
if not repo.is_dir(): die('repo root is not a regular custody directory')
try:
 top=subprocess.check_output(['git','-C',str(repo),'rev-parse','--show-toplevel'],text=True).strip()
 common=subprocess.check_output(['git','-C',str(repo),'rev-parse','--git-common-dir'],text=True).strip()
except subprocess.CalledProcessError: die('repo root is not a Git worktree')
if canon(top)!=canon(repo): die('supplied repo root is not the canonical Git worktree')
common=common if os.path.isabs(common) else os.path.join(str(repo),common)
try: rel=run.relative_to(repo)
except ValueError: die('run root is outside repository')
for p in [repo,*[repo/Path(*rel.parts[:i]) for i in range(1,len(rel.parts)+1)]]:
 if unsafe(p): die(f'custody path is symlink/reparse: {p}')
if not run.is_dir(): die('run root is not a directory')
claim=run/'.claimed'
if unsafe(claim) or not stat.S_ISREG(os.lstat(claim).st_mode): die('.claimed is not a regular custody file')
rows=claim.read_text(encoding='utf-8').splitlines()
if any(not x or '=' not in x for x in rows): die('.claimed has blank or malformed key')
pairs=[x.split('=',1) for x in rows]; keys=[x[0] for x in pairs]
want=['schema','claim_id','claimed_at_utc','mode','templates','repo_root','git_common_dir','run_base','run_root','run_name']
if keys!=want: die('.claimed v2 keys/order do not match strict schema')
d=dict(pairs)
if d['schema']!='implementaudit.run-claim.v2' or not re.fullmatch(r'[0-9a-f]{32}',d['claim_id']): die('.claimed v2 schema or claim_id invalid')
try:
 if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z',d['claimed_at_utc']): raise ValueError
 datetime.datetime.strptime(d['claimed_at_utc'],'%Y-%m-%dT%H:%M:%SZ')
except ValueError: die('.claimed claimed_at_utc is not RFC3339 UTC whole seconds')
if d['mode']!='full' or d['run_base']!='.IMPLEMENTAUDIT/runs': die('.claimed mode/base is not R0024 strict custody')
if canon(d['repo_root'])!=canon(repo) or canon(d['git_common_dir'])!=canon(common): die('.claimed repository or common-dir custody drift')
if d['run_root']!=rel.as_posix() or d['run_name']!=run.name or len(rel.parts)!=3 or rel.parts[:2]!=('.IMPLEMENTAUDIT','runs'): die('.claimed run identity drift')
if not re.fullmatch(r'[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}',d['run_name']): die('.claimed run name is not claim-run shaped')
templates='STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md'
if d['templates']!=templates: die('.claimed template promise drift')
for name in templates.split():
 p=run/name
 if unsafe(p) or not stat.S_ISREG(os.lstat(p).st_mode): die(f'claimed template is not regular custody: {name}')
print('validate-run-root: claim ok')
PY
  exit $?
fi

graph_python=()
case "${1:-}" in
  --graph-freshness|--graph-scope|--graph-parent)
    if command -v python >/dev/null 2>&1; then
      graph_python=(python)
    elif command -v python3 >/dev/null 2>&1; then
      graph_python=(python3)
    elif command -v py >/dev/null 2>&1; then
      graph_python=(py -3)
    else
      printf 'validate-run-root: python, python3, or py -3 is required for graph checks\n' >&2
      exit 2
    fi
    ;;
esac

if [ "${1:-}" = "--graph-scope" ] || [ "${1:-}" = "--graph-parent" ]; then
  graph_mode="$1"
  if { [ "$graph_mode" = "--graph-scope" ] && [ "$#" -lt 4 ]; } || \
     { [ "$graph_mode" = "--graph-parent" ] && [ "$#" -ne 5 ]; }; then
    printf 'usage: validate-run-root.sh %s <catalog.json> <repo-root> %s\n' \
      "$graph_mode" "$([ "$graph_mode" = "--graph-scope" ] && printf '<path> [path...]' || printf '<scope> <miss|ambiguity|cross-scope|relation-omission>')" >&2
    exit 2
  fi
  shift
  "${graph_python[@]}" - "$graph_mode" "$@" <<'PY'
import fnmatch, hashlib, json, os, re, subprocess, sys
from pathlib import Path, PurePosixPath

mode, catalog_arg, repo_arg, *args = sys.argv[1:]
repo = Path(repo_arg).resolve()

def stop(message, status=1):
    print(f"validate-run-root: {message}", file=sys.stderr)
    raise SystemExit(status)

def sha(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        stop(f"cannot hash {path}: {exc}", 2)

def covers(row, path):
    root = row["root"]
    return ((root == "." or path.startswith(root + "/")) and
            any(fnmatch.fnmatchcase(path, p) for p in row["include"]) and
            not any(fnmatch.fnmatchcase(path, p) for p in row["exclude"]))

def inside(path, root):
    return path == root or root in path.parents

def sidecar(value, kind, base=None):
    path = Path(value)
    path = path if path.is_absolute() or base is None else base / path
    path, resolved = Path(os.path.abspath(path)), path.resolve()
    if path.is_symlink() or inside(path, repo) or inside(resolved, repo):
        stop(f"invalid graph catalogue: {kind} path is inside repo or is a symlink: {path}")
    return resolved

def unsafe(path):
    return path.is_symlink() or not inside(path.resolve(), repo)

def git_paths(*args):
    return set(subprocess.check_output(["git", "-C", str(repo), "ls-files", *args]).decode("utf-8").split("\0"))

def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON member")
    return value

def exact(value, names):
    return isinstance(value, dict) and set(value) == set(names.split())

config_names = (".graphifyignore", ".gitignore", ".graphifyinclude")

def scope_root(value):
    if (not isinstance(value, str) or "\\" in value or str(PurePosixPath(value)) != value or
            value != "." and (value.startswith("/") or ".." in PurePosixPath(value).parts)):
        raise ValueError("scope root")
    path = repo if value == "." else repo / value
    if (not path.is_dir() or not inside(path.resolve(), repo) or
            any(part.is_symlink() for part in (path, *path.parents) if inside(part, repo))):
        raise ValueError("scope root")
    return path

def config_keys(root):
    rel = root.relative_to(repo)
    dirs = [repo.joinpath(*rel.parts[:i]) for i in range(len(rel.parts) + 1)]
    return sorted((d / name).relative_to(repo).as_posix() for d in dirs for name in config_names)

catalog_path = sidecar(catalog_arg, "catalogue")

try:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"), object_pairs_hook=unique)
except (OSError, UnicodeError, ValueError) as exc:
    stop(f"invalid graph catalogue: {exc}")

hex40, hex64 = re.compile(r"^[0-9a-fA-F]{40}$"), re.compile(r"^[0-9a-fA-F]{64}$")
try:
    if not exact(payload, "schema scopes"):
        raise ValueError("catalogue members")
    rows = payload["scopes"]
    if type(payload.get("schema")) is not int or payload["schema"] != 1 or not isinstance(rows, list) or not rows:
        raise ValueError("schema/scopes")
    scopes = {}
    for row in rows:
        if not exact(row, "name parent root include exclude file_count files config graph graph_sha256 build"):
            raise ValueError("scope members")
        name = row["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", name) or name in scopes:
            raise ValueError("scope name")
        include, exclude, files = row["include"], row["exclude"], row["files"]
        build, config, root = row["build"], row["config"], scope_root(row["root"])
        if not exact(build, "commit tool version mode llm rules_sha256 scope_sha256"):
            raise ValueError(f"scope {name} build members")
        if (not isinstance(include, list) or not include or
                not isinstance(exclude, list) or
                not all(isinstance(p, str) for p in include + exclude)):
            raise ValueError(f"scope {name}")
        rules_sha = hashlib.sha256(json.dumps([sorted(include), sorted(exclude)], separators=(",", ":")).encode()).hexdigest()
        patterns = include + exclude
        if (include != sorted(set(include)) or exclude != sorted(set(exclude)) or
                not all(p and not p.startswith("/") and ".." not in PurePosixPath(p).parts for p in patterns) or
                not isinstance(files, dict) or row["file_count"] != len(files) or
                type(row["file_count"]) is not int or row["file_count"] < 0 or
                not all(isinstance(p, str) and hex64.fullmatch(v or "") for p, v in files.items()) or
                list(files) != sorted(files) or
                not all(covers(row, p) for p in files) or
                not isinstance(config, dict) or list(config) != config_keys(root) or
                not all(v is None or (isinstance(v, str) and hex64.fullmatch(v)) for v in config.values()) or
                not isinstance(row["graph"], str) or not hex64.fullmatch(row["graph_sha256"] or "") or
                row.get("parent") is not None and not isinstance(row.get("parent"), str) or
                not hex40.fullmatch(build.get("commit", "")) or
                not all(isinstance(build.get(k), str) and build[k] for k in ("tool", "version", "mode")) or
                build.get("rules_sha256") != rules_sha or
                build.get("llm") is not False):
            raise ValueError(f"scope {name}")
        contract_build = dict(build)
        del contract_build["scope_sha256"]
        contract = {
            "name": name,
            "parent": row.get("parent"),
            "root": row["root"],
            "include": include,
            "exclude": exclude,
            "file_count": row["file_count"],
            "files": files,
            "config": config,
            "build": contract_build,
        }
        scope_sha = hashlib.sha256(json.dumps(
            contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if build.get("scope_sha256") != scope_sha:
            raise ValueError(f"scope {name}")
        scopes[name] = row
    for name, row in scopes.items():
        parent = row.get("parent")
        if parent is not None:
            parent_row = scopes.get(parent)
            if (parent_row is None or not inside(scope_root(row["root"]), scope_root(parent_row["root"])) or
                    not set(row["files"]) < set(parent_row["files"]) or
                    not all(covers(parent_row, path) for path in row["files"])):
                raise ValueError(f"parent {name}")
        seen = {name}
        while parent is not None:
            if parent in seen:
                raise ValueError(f"parent cycle {name}")
            seen.add(parent)
            parent = scopes[parent].get("parent")
    for commit in {row["build"]["commit"] for row in rows}:
        if subprocess.call(["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "HEAD"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
            raise ValueError(f"build commit {commit}")
except (AttributeError, KeyError, TypeError, ValueError) as exc:
    stop(f"invalid graph catalogue: {exc}")

def normalise(value):
    value = str(value).replace("\\", "/").removeprefix("./")
    if (not value or Path(value).is_absolute() or re.match(r"^[A-Za-z]:/", value) or
            ".." in PurePosixPath(value).parts or value == ".git" or value.startswith(".git/")):
        stop(f"invalid query path: {value}", 2)
    return value

relation_omission = False
if mode == "--graph-scope":
    paths = [normalise(p) for p in args]
    candidates = [r for r in rows if all(covers(r, p) for p in paths)]
    if not candidates:
        stop("graph-route: wrong/overbroad-scope fallback=deterministic-live-file-census broaden=false llm=false")
    selected = min(candidates, key=lambda r: (r["file_count"], r["name"]))
    reason = "smallest-cover"
else:
    current, reason = args
    if current not in scopes:
        stop(f"unknown graph scope: {current}")
    if reason == "relation-omission":
        relation_omission, selected = True, scopes[current]
    elif reason not in {"miss", "ambiguity", "cross-scope"}:
        stop(f"invalid broadening reason: {reason}", 2)
    else:
        if scopes[current].get("parent") is None:
            stop(f"scope has no declared parent: {current}")
        selected = scopes[scopes[current]["parent"]]
        reason = f"parent:{reason}"

check_rows = ([selected] if relation_omission else [scopes[current], selected]) if mode == "--graph-parent" else [selected]
for selected in check_rows:
    graph = sidecar(selected["graph"], "graph", catalog_path.parent)
    if not graph.is_file():
        stop(f"stale-sidecar: missing graph {selected['name']}")
    try:
        graph_bytes = graph.read_bytes()
    except OSError as exc:
        stop(f"cannot read graph {graph}: {exc}", 2)
    if hashlib.sha256(graph_bytes).hexdigest().lower() != selected["graph_sha256"].lower():
        stop(f"stale-sidecar: graph-digest {selected['name']}")
    try:
        graph_payload = json.loads(graph_bytes, object_pairs_hook=unique)
    except (UnicodeError, ValueError):
        stop(f"stale-sidecar: invalid graph {selected['name']}")
    if (not isinstance(graph_payload, dict) or
            not isinstance(graph_payload.get("nodes"), list) or
            not isinstance(graph_payload.get("links", graph_payload.get("edges")), list) or
            not isinstance(graph_payload.get("graph"), dict)):
        stop(f"stale-sidecar: invalid graph {selected['name']}")
    if graph_payload["graph"].get("implementaudit_scope_sha256") != selected["build"]["scope_sha256"]:
        stop(f"stale-sidecar: graph-scope-binding {selected['name']}")
    sources = []
    for node in graph_payload["nodes"]:
        source = node.get("source_file") if isinstance(node, dict) else None
        if (not isinstance(source, str) or "\\" in source or
                str(PurePosixPath(source)) != source or source.startswith("/") or
                ".." in PurePosixPath(source).parts):
            stop(f"stale-sidecar: graph-population {selected['name']}")
        sources.append(source if selected["root"] == "." else f"{selected['root']}/{source}")
    if set(sources) != set(selected["files"]):
        stop(f"stale-sidecar: graph-population {selected['name']}")

    for rel, expected_digest in selected["config"].items():
        path = repo / rel
        if unsafe(path):
            stop(f"stale-sidecar: unsafe-path {rel}")
        if path.exists() and not path.is_file():
            stop(f"stale-sidecar: config-drift {rel}")
        actual = sha(path) if path.is_file() else None
        if actual != expected_digest:
            stop(f"stale-sidecar: config-drift {rel}")

    root = scope_root(selected["root"])
    for rel in config_keys(root):
        path = repo / rel
        active = path.is_file() and any(line.strip() and not line.lstrip().startswith("#") for line in path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if active and (path.name == ".graphifyinclude" or path.parent != repo):
            stop(f"stale-sidecar: unsupported-config {rel}")
    ignore = ".graphifyignore" if selected["config"][".graphifyignore"] else ".gitignore"
    if selected["config"][ignore] and any("**" in rule and not rule.lstrip().startswith(("#", "!")) for rule in (repo / ignore).read_text(encoding="utf-8", errors="ignore").splitlines()):
        stop(f"stale-sidecar: unsupported-ignore-pattern {ignore}")

    try:
        exclude = [f"--exclude-from={repo / ignore}"] if selected["config"][ignore] else []
        output = git_paths("--cached", "--others", "-z", *exclude)
        if exclude:
            output -= git_paths("--cached", "-i", "-z", *exclude)
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        stop(f"cannot census graph scope: {exc}", 2)
    covered = [p for p in output if p and covers(selected, p)]
    for rel in covered:
        path = repo / rel
        if unsafe(path):
            stop(f"stale-sidecar: unsafe-path {rel}")
    current = sorted(p for p in covered if (repo / p).is_file())
    expected = selected["files"]
    new = sorted(set(current) - set(expected))
    deleted = sorted(set(expected) - set(current))
    if new:
        stop(f"stale-sidecar: new {new[0]}")
    if deleted:
        stop(f"stale-sidecar: deleted {deleted[0]}")
    if mode == "--graph-scope" and any(p not in expected for p in paths):
        stop("graph-route: wrong/overbroad-scope query-path-not-indexed fallback=deterministic-live-file-census broaden=false llm=false")
    for rel in current:
        if sha(repo / rel).lower() != expected[rel].lower():
            stop(f"stale-sidecar: changed {rel}")

if relation_omission:
    print("graph-route: extractor/relation-model omission fallback=deterministic-live-file-census broaden=false llm=false")
    raise SystemExit(0)
build = selected["build"]
print(
    f"graph-scope: {selected['name']} graph={graph} files={selected['file_count']} "
    f"reason={reason} build={build['commit']} tool={build['tool']}@{build['version']} "
    f"mode={build['mode']} llm=false"
)
PY
  exit $?
fi

if [ "${1:-}" = "--graph-freshness" ]; then
  if [ "$#" -ne 3 ]; then
    printf 'usage: validate-run-root.sh --graph-freshness <graph.json> <repo-root>\n' >&2
    exit 2
  fi

  graph_path="$2"
  repo_path="$3"
  [ -f "$graph_path" ] || {
    printf 'validate-run-root: graph freshness input is not a file: %s\n' "$graph_path" >&2
    exit 2
  }

  built_at_commit="$("${graph_python[@]}" - "$graph_path" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    sys.stderr.write(f"validate-run-root: invalid graph freshness input: {exc}\n")
    raise SystemExit(1)

value = payload.get("built_at_commit")
if not isinstance(value, str) or not value:
    sys.stderr.write("validate-run-root: graph.json has no string built_at_commit\n")
    raise SystemExit(1)
sys.stdout.write(value + "\n")
PY
)"
  parse_status=$?
  [ "$parse_status" -eq 0 ] || exit 1

  if ! printf '%s\n' "$built_at_commit" | grep -Eq '^[0-9a-fA-F]{40}$'; then
    printf 'validate-run-root: graph.json built_at_commit must be one full 40-hex commit SHA\n' >&2
    exit 1
  fi

  live_head="$(git -C "$repo_path" rev-parse HEAD 2>/dev/null)" || {
    printf 'validate-run-root: cannot resolve git rev-parse HEAD for %s\n' "$repo_path" >&2
    exit 2
  }

  if [ "$(printf '%s' "$built_at_commit" | tr '[:upper:]' '[:lower:]')" != \
       "$(printf '%s' "$live_head" | tr '[:upper:]' '[:lower:]')" ]; then
    printf 'validate-run-root: stale-sidecar: built_at_commit %s != git rev-parse HEAD %s\n' \
      "$built_at_commit" "$live_head" >&2
    exit 1
  fi
  exit 0
fi

check_recurrence_decision() {
  local ledger="$1" findings invalid_lines missing_classes
  findings="$(awk -F'|' '
    function trim(v) { gsub(/^[ \t]+|[ \t]+$/, "", v); return v }
    function owner_source(v) {
      if (v !~ /owner\/source[ \t]*=/) return ""
      sub(/^.*owner\/source[ \t]*=[ \t]*/, "", v)
      sub(/[ \t;,)]+.*$/, "", v)
      gsub(/\\/, "/", v)
      while (v ~ /^\.\//) sub(/^\.\//, "", v)
      return v
    }
    /^Mechanism-replacement decision:/ {
      if ($0 ~ /^Mechanism-replacement decision:[ \t]*(replace-mechanism|continue|escalate-to-convergence-mode)[ \t]*\([^()]*[[:alnum:]][^()]*\)[ \t]*$/) {
        valid_decision[NR]=1
      } else {
        print "invalid\t" NR
      }
    }
    /^[ \t]*AUDIT_COMPLETE[ \t]*$/ {
      if (audit_complete_line == 0) audit_complete_line=NR
    }
    /^## Andon log/ { in_andon=1; new_format=0; next }
    in_andon && /^## / { in_andon=0; new_format=0 }
    in_andon && tolower($0) ~ /\|[ \t]*occ[ \t]*\|[ \t]*phase[ \t]*\|[ \t]*class[ \t]*\|/ {
      new_format=1; next
    }
    in_andon && new_format && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
      occ=trim($3); cls=trim($5)
      if (occ == "" || cls == "") next
      key=cls SUBSEP occ
      if (!(key in seen)) {
        seen[key]=1
        count[cls]++
        previous_owner[cls]=last_owner[cls]
        last_owner[cls]=owner_source($7)
        last_line[cls]=NR
      }
    }
    END {
      for (cls in count) {
        if (count[cls] < 3 || last_owner[cls] == "" || previous_owner[cls] != last_owner[cls]) continue
        found=0
        for (line in valid_decision) {
          if ((line + 0) > last_line[cls] &&
              (audit_complete_line == 0 || (line + 0) < audit_complete_line)) found=1
        }
        if (!found) print "missing\t" cls
      }
    }' "$ledger")"

  invalid_lines="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "invalid" { print $2 }' | tr '\n' ' ')"
  if [ -n "$invalid_lines" ]; then
    err "invalid Mechanism-replacement decision: line(s) $invalid_lines (allowed: replace-mechanism (<what>) / continue (<justification>) / escalate-to-convergence-mode (<shared invariant>))"
  fi
  missing_classes="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "missing" { print $2 }' | tr '\n' ' ')"
  if [ -n "$missing_classes" ]; then
    err "Andon class(es) $missing_classes reached 3 distinct linked occurrences with the last 2 repairs on one owner/source; add a following Mechanism-replacement decision:"
  fi
}

intent_value() { sed -n "s/^$2:[[:space:]]*//p" "$1" | head -n1; }
duration_seconds() {
  [[ "$1" =~ ^([0-9]+)([smhd]?)$ ]] || return
  case "${BASH_REMATCH[2]}" in '') m=1;; s) m=1;; m) m=60;; h) m=3600;; d) m=86400;; esac
  printf '%s\n' "$((BASH_REMATCH[1] * m))"
}
process_identity_matches() {
  local py
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else return 2; fi
  "${py[@]}" - "$@" <<'PY'
import json,sys
p,l,i,b,c=sys.argv[1:]
try:
 x=json.load(open(p,encoding="utf-8"))
except (OSError,UnicodeError,json.JSONDecodeError): raise SystemExit(1)
if isinstance(x,dict): x=[x]
keys={"lane_id","host_os","host_boot_id","pid","process_creation_time"}
ok=any(isinstance(r,dict) and keys<=r.keys() and r["lane_id"]==l and isinstance(r["host_os"],str) and r["host_os"] and str(r["pid"])==i and r["host_boot_id"]==b and r["process_creation_time"]==c for r in x)
raise SystemExit(not ok)
PY
}
intent_has_open_window() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*state:[[:space:]]*open[[:space:]]*$/ { found = 1 }
    END { exit !found }
  ' "$1"
}
intent_has_closed_window() {
  grep -Eq '^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$' "$1"
}
intent_has_invalid_closed_anchor() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*-[[:space:]]*surfaces:/ { closed_at = ""; next }
    in_window && /^[[:space:]]*closed_at:/ {
      closed_at = $0
      sub(/^[[:space:]]*closed_at:[[:space:]]*/, "", closed_at)
      next
    }
    in_window && /^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$/ {
      if (length(closed_at) != 40 || closed_at !~ /^[0-9a-f]+$/) bad = 1
    }
    END { exit !bad }
  ' "$1"
}
check_background_chains() {
  local root="$1" state="$2" chain id intent status budget signal expected timeout mode cadence why es ts polls line pid boot created rc
  [ -d "$root/background" ] || return
  for chain in "$root"/background/*; do
    [ -d "$chain" ] || continue; id="$(basename "$chain")"
    intent="$chain/launch-intent.md"; status="$chain/chain-status.txt"
    [ -f "$intent" ] || { err "background/$id missing launch-intent.md"; continue; }
    if intent_has_closed_window "$intent"; then
      [ -f "$chain/chain.done" ] \
        || err "background/$id closed verification window lacks chain.done"
      if intent_has_invalid_closed_anchor "$intent"; then
        err "background/$id closed verification window lacks a full-SHA closed_at"
      fi
    fi
    if [ -f "$state" ] &&
       grep -Eq '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*DONE[[:space:]]*\|' "$state" &&
       intent_has_open_window "$intent"; then
      err "background/$id verification window remains open at run-root closure"
    fi
    if ! grep -Eq '^(poll_budget|terminal_signal|expected_duration|transport_timeout|launch_mode|report_cadence):' "$intent"; then
      warn "background/$id legacy launch intent; #81 checks skipped"; continue
    fi
    budget="$(intent_value "$intent" poll_budget)"; signal="$(intent_value "$intent" terminal_signal)"
    expected="$(intent_value "$intent" expected_duration)"; timeout="$(intent_value "$intent" transport_timeout)"
    mode="$(intent_value "$intent" launch_mode)"; cadence="$(intent_value "$intent" report_cadence)"
    why="$(intent_value "$intent" report_cadence_justification)"; [ -n "$cadence" ] || cadence=on-failure-and-terminal
    [[ "$budget" =~ ^[1-9][0-9]*$ ]] || err "background/$id invalid poll_budget"
    [[ "$signal" =~ ^[^[:space:]]+$ ]] || err "background/$id invalid terminal_signal"
    case "$mode" in inline|detached);; *) err "background/$id invalid launch_mode";; esac
    case "$cadence" in per-item|on-failure-and-terminal|terminal-only);; *) err "background/$id invalid report_cadence";; esac
    [ "$cadence" != per-item ] || [[ "$why" =~ [[:alnum:]] ]] || err "background/$id per-item cadence lacks justification"
    es="$(duration_seconds "$expected" 2>/dev/null || :)"; ts="$(duration_seconds "$timeout" 2>/dev/null || :)"
    [ -n "$es" ] || err "background/$id invalid expected_duration"; [ -n "$ts" ] || err "background/$id invalid transport_timeout"
    if [ -n "$es" ] && [ -n "$ts" ] && [ "$mode" = inline ] && [ "$es" -ge "$ts" ]; then err "background/$id inline launch meets/exceeds ceiling"; fi
    [ -f "$status" ] || continue
    polls="$(grep -c '^probe:' "$status" 2>/dev/null || :)"
    if [[ "$budget" =~ ^[1-9][0-9]*$ ]] && [ "$polls" -gt "$budget" ] &&
       { [ ! -f "$state" ] || ! awk -v n="$budget" 'index(tolower($0),"hung-command")&&index(tolower($0),"supervision-overrun")&&index(tolower($0),"poll_budget " n " exceeded"){f=1} END{exit !f}' "$state"; }; then
      err "background/$id poll_budget exceeded without matching hung-command Andon"
    fi
    if [ "$cadence" = on-failure-and-terminal ] && grep -E '^report: item=.*outcome=' "$status" | grep -Evq 'outcome=failure([ |]|$)'; then err "background/$id default cadence narrated success"
    elif [ "$cadence" = terminal-only ] && grep -q '^report: item=' "$status"; then err "background/$id terminal-only narrated item"; fi
    awk '/^checkpoint:/{c=NR}/^wait: blocking/{if(!c||c>=NR)b=1}END{exit b}' "$status" || err "background/$id wait lacks checkpoint"
    grep -R -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$chain" 2>/dev/null && err "background/$id broad kill authority"
    if grep -R -E 'Get-Process([[:space:]]|$)' "$chain" 2>/dev/null | grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then err "background/$id broad Get-Process"; fi
    while IFS= read -r line; do
      pid="$(sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' <<<"$line")"; boot="$(sed -n 's/.*host_boot_id=\([^ |]*\).*/\1/p' <<<"$line")"; created="$(sed -n 's/.*process_creation_time=\([^ |]*\).*/\1/p' <<<"$line")"
      if [ -z "$pid" ] || [ -z "$boot" ] || [ -z "$created" ] || [ ! -f "$chain/process-started.json" ]; then err "background/$id kill lacks process-started.json identity"; continue; fi
      if process_identity_matches "$chain/process-started.json" "$id" "$pid" "$boot" "$created"; then :; else rc=$?; [ "$rc" -eq 2 ] && err "background/$id python required for kill ledger" || err "background/$id kill identity not ledger-owned"; fi
    done < <(grep '^kill:' "$status" 2>/dev/null || :)
  done
}

is_terminal_phase_status() {
  case "$1" in
    done|done\ *|verified|verified\ *|pass|pass\ *|'focused pass'|'focused pass '*|complete|complete\ *|complete\;*|completed|completed\ *|closed|closed\ *) return 0 ;;
    *) return 1 ;;
  esac
}

is_nonterminal_phase_status() {
  case "$1" in
    open|ready|ready_to_dispatch|in_phase|in\ progress|in\ progress\ *|in_progress|in_progress\ *|paused|blocked|interrupted|pending|dispatchable|finding_closure_pending|audit_handoff|handoff) return 0 ;;
    *) return 1 ;;
  esac
}

check_done_phase_captures() {
  local phase="$1" status phase_n capture target repo_prefix
  status="$(awk '
    /^IMPLEMENTAUDIT_PHASE_DONE[[:space:]]*$/ { done=1; next }
    done && /^Status:[[:space:]]*/ {
      sub(/^Status:[[:space:]]*/, ""); print tolower($0); exit
    }
  ' "$phase")"
  if is_terminal_phase_status "$status"; then
    :
  elif is_nonterminal_phase_status "$status"; then
    return 0
  elif [ -f "$run_root/ROADMAP.md" ]; then
    phase_n="$(basename "$phase" | sed -n 's/^phase-\([0-9][0-9]*\)\.md$/\1/p')"
    status="$(awk -F'|' -v n="$phase_n" '
      function trim(v) { gsub(/^[ \t]+|[ \t]+$/, "", v); return v }
      /^\|/ {
        if (!phase_table) {
          first=tolower(trim($2)); second=tolower(trim($3)); status_col=0
          if (first == "phase" || (first == "#" && second == "phase")) {
            for (i=2; i<NF; i++) if (tolower(trim($i)) == "status") status_col=i
            if (status_col) phase_table=1
          }
          next
        }
        if (trim($2) == n) { print tolower(trim($status_col)); exit }
        next
      }
      phase_table && NF && $0 !~ /^[ \t]*$/ { phase_table=0 }
    ' "$run_root/ROADMAP.md")"
    is_terminal_phase_status "$status" || return 0
  else
    return 0
  fi
  repo_prefix=""
  case "$run_root" in
    */.IMPLEMENTAUDIT/*) repo_prefix="${run_root%%/.IMPLEMENTAUDIT/*}" ;;
    .IMPLEMENTAUDIT/*) repo_prefix="." ;;
  esac
  while IFS= read -r capture; do
    capture="${capture#\`}"; capture="${capture%\`}"
    case "$capture" in
      '<run-root>') target="$run_root" ;;
      '<run-root>/'*) target="$run_root/${capture#<run-root>/}" ;;
      /*|[A-Za-z]:*) target="$capture" ;;
      "$run_root"/*) target="$capture" ;;
      *.IMPLEMENTAUDIT/*)
        capture=".IMPLEMENTAUDIT/${capture#*.IMPLEMENTAUDIT/}"
        target="${repo_prefix:+$repo_prefix/}$capture"
        ;;
      evidence/*) target="$run_root/$capture" ;;
      ./evidence/*) target="$run_root/${capture#./}" ;;
      *) continue ;;
    esac
    if [ ! -f "$target" ]; then
      err "DONE phase $(basename "$phase") declared capture is missing: $capture"
    elif ! has_non_whitespace "$target"; then
      err "DONE phase $(basename "$phase") declared capture is blank: $capture"
    fi
  done < <(sed -n '/^## Mandatory commands/,/^## / {
    s/.*;[[:space:]]*capture:[[:space:]]*\([^;]*\);.*/\1/p
  }' "$phase")
}

mode=full
if [ "${1:-}" = "--micro" ]; then
  mode=micro
  shift
elif [ "${1:-}" = "--ledger" ]; then
  mode=ledger
  shift
fi
run_root="${1:-}"
if [ -z "$run_root" ]; then
  if [ "$mode" = micro ]; then
    printf 'usage: validate-run-root.sh --micro <run-root>\n' >&2
  elif [ "$mode" = ledger ]; then
    printf 'usage: validate-run-root.sh --ledger <markdown-ledger>\n' >&2
  else
    printf 'usage: validate-run-root.sh <run-root>\n' >&2
  fi
  exit 2
fi
[ "$mode" != ledger ] || {
  [ -f "$run_root" ] || { printf 'validate-run-root: not a file: %s\n' "$run_root" >&2; exit 2; }
  check_recurrence_decision "$run_root"
  if [ "$err_count" -gt 0 ]; then
    printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
    exit 1
  fi
  printf 'validate-run-root: ok\n'
  exit 0
}
[ -d "$run_root" ] || { printf 'validate-run-root: not a directory: %s\n' "$run_root" >&2; exit 2; }

claim="$run_root/.claimed"
claim_mode=""
if [ "$mode" = micro ] && [ ! -f "$claim" ]; then
  err "micro root is missing .claimed metadata"
fi
if [ -f "$claim" ]; then
  claim_mode="$(awk -F= '$1 == "mode" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  case "$claim_mode" in
    full|micro) : ;;
    *) err ".claimed has invalid mode '$claim_mode' (expected full or micro)" ;;
  esac
  if [ "$claim_mode" = micro ] && [ "$mode" != micro ]; then
    err ".claimed records mode=micro; validate this declared narrowing with --micro"
  elif [ "$claim_mode" = full ] && [ "$mode" = micro ]; then
    err ".claimed records mode=full; --micro cannot narrow a full claim"
  fi

  claimed_templates="$(awk -F= '$1 == "templates" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  for f in $claimed_templates; do
    [ -f "$run_root/$f" ] || err "claimed $f is missing — sentinel/artifact drift"
  done
fi

if [ "$mode" = micro ]; then
  [ -f "$run_root/STATE.md" ] || err "missing required artifact: STATE.md"
else
  root_done=no
  if grep -Eq '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*DONE[[:space:]]*\|' \
    "$run_root/STATE.md" 2>/dev/null; then
    root_done=yes
  fi
  template_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../templates" && pwd)"
  for f in STATE.md PROTOCOL.md; do
    if [ ! -f "$run_root/$f" ]; then err "missing required artifact: $f"
    elif ! has_non_whitespace "$run_root/$f"; then err "required artifact is blank: $f"; fi
  done
  for f in ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    artifact_status="$(awk -F'|' -v artifact="<run-root>/$f" '
      function trim(v) { gsub(/^[ \t`]+|[ \t`]+$/, "", v); return v }
      trim($2) == artifact { print tolower(trim($3)); exit }
    ' "$run_root/STATE.md" 2>/dev/null)"
    if [ ! -f "$run_root/$f" ]; then err "missing planning artifact: $f (required for dispatched phase runs)"
    elif ! has_non_whitespace "$run_root/$f"; then err "planning artifact is blank: $f"; fi
    if [ "$root_done" = yes ] && [ "$artifact_status" = complete ] &&
       [ -f "$run_root/$f" ] &&
       cmp -s "$run_root/$f" "$template_dir/$f"; then
      err "planning artifact remains an unfilled template at DONE: $f"
    fi
  done
fi

if [ "$mode" = full ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r phase; do check_done_phase_captures "$phase"; done \
    < <(find "$run_root/phases" -type f -name 'phase-*.md' -print | sort)
fi

state="$run_root/STATE.md"
if [ -f "$state" ]; then
  if [ "$mode" = full ]; then
    status_line="$(grep -E '^\| Status \|' "$state" | head -1 || true)"
    if [ -z "$status_line" ]; then
      err "STATE.md has no '| Status |' row in the Current phase table"
    else
      status_value="$(printf '%s' "$status_line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')"
      case "$status_value" in
        open|READY_TO_DISPATCH|IN_PHASE|PAUSED|BLOCKED|INTERRUPTED|DONE) : ;;
        *) err "STATE.md Status '$status_value' is not a contract token (open / READY_TO_DISPATCH / IN_PHASE / PAUSED / BLOCKED / INTERRUPTED / DONE)" ;;
      esac
    fi
  fi

  if ! grep -qi '^## Andon log' "$state"; then
    err "STATE.md is missing the '## Andon log' section"
  elif grep -qi '| Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    missing_occ="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        occ=$3; gsub(/^[ \t]+|[ \t]+$/, "", occ)
        if (occ == "") { n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$missing_occ" ]; then
      err "STATE.md Andon log new-format rows missing an Occ occurrence id: row(s) $(printf '%s' "$missing_occ" | tr '\n' ' ')"
    fi
    multi_class="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        cls=$5; gsub(/^[ \t]+|[ \t]+$/, "", cls)
        if (cls != "" && cls !~ /^[A-Za-z-]+$/) {
          n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$multi_class" ]; then
      err "STATE.md Andon log row(s) with a non-single-token Class (exactly one class per row; plural defects record one row per class sharing an Occ id): row(s) $(printf '%s' "$multi_class" | tr '\n' ' ')"
    fi
  elif ! grep -qi '| Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    err "STATE.md Andon log table is missing the contract columns (# | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome; legacy shape without Occ also accepted)"
  fi
  check_recurrence_decision "$state"

  if [ "$mode" = micro ]; then
    terminal_line="$(awk 'NF { last=$0 } END { print last }' "$state")"
    case "$terminal_line" in
      AUDIT_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF) : ;;
      IMPLEMENTAUDIT_RUN_COMPLETE)
        grep -qx 'AUDIT_COMPLETE' "$state" || err "STATE.md ends with IMPLEMENTAUDIT_RUN_COMPLETE but has no preceding AUDIT_COMPLETE"
        ;;
      *) err "micro STATE.md final nonblank line is not a terminal marker (AUDIT_COMPLETE / IMPLEMENTAUDIT_RUN_COMPLETE / AUDIT_HANDOFF / ANDON_HANDOFF)" ;;
    esac

    if find "$run_root/phases" -type f -name 'phase-*.md' -print -quit 2>/dev/null | grep -q .; then
      err "micro root contains phase specs; phased dispatch requires a full run root"
    fi
    if [ -f "$run_root/ROADMAP.md" ] && grep -Eq '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$run_root/ROADMAP.md"; then
      err "micro root contains a ROADMAP phase table; phased dispatch requires a full run root"
    fi
    if grep -R -E -q '^(Stage 6\.i|Stage 6\.2|Independent cold-review disposition|Review disposition):' "$run_root" \
      --exclude='.claimed' 2>/dev/null; then
      err "micro root contains a Stage 6.i (legacy 6.2) disposition; executor-facing review requires a full run root"
    fi
    extra_micro_files="$(cd "$run_root" && find . -type f \
      ! -path './.claimed' ! -path './STATE.md' ! -path './deferrals.jsonl' \
      -print 2>/dev/null || true)"
    if [ -n "$extra_micro_files" ]; then
      err "micro root contains undeclared extra payload: $(printf '%s' "$extra_micro_files" | tr '\n' ' ')"
    fi
    if grep -Eqi '(second-order|higher-order) retrospective.*(reduced|waived|fewer) obligations' "$state"; then
      err "retrospective meta-tier cannot reduce governed-run obligations"
    fi
  fi
fi


if [ -f "$claim" ]; then
  run_base="$(dirname "$run_root")"
  for sibling in "$run_base"/*; do
    [ -d "$sibling" ] || continue
    [ "$sibling" = "$run_root" ] && continue
    sibling_state="$sibling/STATE.md"
    if [ ! -f "$sibling_state" ] || ! grep -Eq \
      '^(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF|COMPLETE|HANDOFF|SUPERSEDED_BY:[[:space:]].+|PARALLEL:[[:space:]].+)$' \
      "$sibling_state"; then
      err "newly claimed root has undispositioned sibling: $(basename "$sibling")"
    fi
  done
fi

if [ -f "$state" ] && grep -qi '^## Occurrence resolution and residuals' "$state"; then
  occ_res="$(awk '/^## Occurrence resolution and residuals/{f=1;next} f&&/^Occurrence resolution:/{sub(/^Occurrence resolution:[ \t]*/,"");print;exit}' "$state")"
  case "$occ_res" in
    not-applicable|unresolved|partially-resolved|resolved) : ;;
    *) err "STATE.md Occurrence resolution '$occ_res' is not a contract token (not-applicable / unresolved / partially-resolved / resolved)" ;;
  esac
  bad_disp="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if (d !~ /^(unresolved|deferred|transferred|owner-assigned|risk-accepted|validated-resolved|SUPERSEDED_BY_CONCURRENT_MUTATION)$/) print r
    }' "$state")"
  if [ -n "$bad_disp" ]; then
    err "STATE.md residual row(s) with invalid disposition: $(printf '%s' "$bad_disp" | tr '\n' ' ') (allowed: unresolved / deferred / transferred / owner-assigned / risk-accepted / validated-resolved / SUPERSEDED_BY_CONCURRENT_MUTATION)"
  fi
  no_ref="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      o=$5; gsub(/^[ \t]+|[ \t]+$/, "", o)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if ((d == "transferred" || d == "risk-accepted") &&
          (o == "" || o ~ /^-+$/)) print r
    }' "$state")"
  if [ -n "$no_ref" ]; then
    err "STATE.md residual row(s) with transferred/risk-accepted but no owner/policy ref: $(printf '%s' "$no_ref" | tr '\n' ' ') (transferred names the receiving owner; risk-accepted cites the policy)"
  fi
fi

# #87 execution identity is prospective. Legacy roots without a row remain
# valid. New rows use the sibling-harness vocabulary exactly once; a requested
# versus actual mismatch is transport, never an independent/bound executor.
if [ -f "$state" ] && grep -qi '^[[:space:]]*model-identity:' "$state"; then
  identity_total="$(grep -Eic '^[[:space:]]*model-identity:' "$state")"
  identity_valid="$(grep -Ec '^model-identity: requested_model: [^|[:space:]][^|]* \| actual_model: [^|[:space:]][^|]* \| evidence: (self-report|host-event:[^|[:space:]][^|]*) \| claims: (bound|IDENTITY_UNBOUND)$' "$state" || true)"
  [ "$identity_total" -eq "$identity_valid" ] \
    || err "STATE.md model-identity row must use exact requested_model / actual_model / evidence / claims grammar"
  has_transport="$(awk -F'|' '
    /^## Andon log/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      c=$5; gsub(/^[ \t]+|[ \t]+$/, "", c)
      if (c == "transport-infrastructure") found=1
    }
    END { print found ? "yes" : "no" }
  ' "$state")"
  while IFS= read -r identity_line; do
    [ -n "$identity_line" ] || continue
    requested="$(printf '%s\n' "$identity_line" | sed -E 's/^model-identity: requested_model: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    actual="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| actual_model: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    identity_evidence="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| evidence: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    claims="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| claims: ([^|]+)$/\1/; s/[[:space:]]+$//')"
    if [ "$requested" = "$actual" ]; then
      [ "$claims" = bound ] \
        || err "STATE.md equal requested_model/actual_model must keep claims bound"
    else
      [ "$claims" = IDENTITY_UNBOUND ] \
        || err "STATE.md model substitution must mark claims IDENTITY_UNBOUND"
      [ "$has_transport" = yes ] \
        || err "STATE.md model substitution requires a transport-infrastructure Andon row"
      event_bound="$(awk -F'|' -v token="$identity_evidence" '
        /^## Andon log/ { f=1; next }
        f && /^## / { f=0 }
        f && /^\|/ {
          c=$5; gsub(/^[ \t]+|[ \t]+$/, "", c)
          e=$8; gsub(/^[ \t]+|[ \t]+$/, "", e)
          if (c == "transport-infrastructure" && e == token) found=1
        }
        END { print found ? "yes" : "no" }
      ' "$state")"
      [ "$event_bound" = yes ] \
        || err "STATE.md model substitution evidence must bind the transport-infrastructure Andon evidence cell"
    fi
  done < <(grep -E '^model-identity:' "$state" || true)
fi

# #86 cold-review provenance is prospective. Legacy roots without a row stay
# valid. Once declared, every disposition resolves a contained attestation;
# an authoring-context report is retained as self-critique but cannot satisfy
# the independent cold-review gate.
if [ -f "$state" ] && grep -qi '^[[:space:]]*cold-review[[:space:]]*:' "$state"; then
  cold_py=()
  if command -v python >/dev/null 2>&1; then cold_py=(python)
  elif command -v python3 >/dev/null 2>&1; then cold_py=(python3)
  elif command -v py >/dev/null 2>&1; then cold_py=(py -3)
  else
    err "python, python3, or py -3 is required for cold-review attestation validation"
  fi
  if [ "${#cold_py[@]}" -gt 0 ]; then
    cold_error=""
    if ! cold_error="$("${cold_py[@]}" - "$run_root" "$state" <<'PY'
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
state = pathlib.Path(sys.argv[2])
lines = state.read_text(encoding="utf-8").splitlines()


def die(message):
    print(message)
    raise SystemExit(1)


near = [line for line in lines if re.match(r"^\s*cold-review\s*:", line, re.I)]
exact = [line for line in lines if line.startswith("cold-review:")]
if len(near) != len(exact):
    die("STATE.md cold-review rows must use exact lowercase column-zero grammar")

row_re = re.compile(
    r"^cold-review: disposition: (PASS|GAP-REVISE|BLOCKED|OWNER DECISION) "
    r"\| attestation: ([A-Za-z0-9._/-]+) "
    r"\| base_sha: ([0-9a-f]{40}) \| head_sha: ([0-9a-f]{40})$"
)
keys = (
    "reviewer_identity", "requested_model", "actual_model",
    "authoring_context_reuse", "other_reviewer_output_seen",
    "base_sha", "head_sha",
)

for line in exact:
    match = row_re.fullmatch(line)
    if not match:
        die("STATE.md cold-review row must use exact disposition and attestation grammar")
    disposition = match.group(1)
    rel = match.group(2)
    declared_base = match.group(3)
    declared_head = match.group(4)
    pure = pathlib.PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts or ":" in rel or "\\" in rel:
        die("cold-review attestation path must be safe and run-root-relative")
    artifact_path = root / pathlib.Path(*pure.parts)
    artifact = artifact_path.resolve()
    try:
        artifact.relative_to(root)
    except ValueError:
        die("cold-review attestation escapes the run root")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        die("cold-review attestation must resolve to a regular non-symlink file")
    report = artifact.read_text(encoding="utf-8").splitlines()
    if report.count("Reviewer attestation:") != 1:
        die("cold-review artifact requires exactly one Reviewer attestation header")
    header_index = report.index("Reviewer attestation:")
    block = report[header_index + 1:header_index + 1 + len(keys)]
    if len(block) != len(keys):
        die("cold-review artifact has an incomplete Reviewer attestation block")
    values = {}
    for index, key in enumerate(keys):
        key_near = [item for item in report if re.match(rf"^\s*-\s*{re.escape(key)}\s*:", item, re.I)]
        key_exact = [item for item in report if item.startswith(f"- {key}:")]
        if len(key_near) != 1 or len(key_exact) != 1:
            die(f"cold-review attestation requires exactly one exact {key} field")
        if block[index] != key_exact[0]:
            die("cold-review attestation fields must form one exact ordered header block")
        value = block[index].split(":", 1)[1].strip()
        if not value:
            die(f"cold-review attestation {key} is empty")
        values[key] = value
    if values["authoring_context_reuse"] not in {"yes", "no"}:
        die("cold-review authoring_context_reuse must be yes or no")
    if values["other_reviewer_output_seen"] not in {"yes", "no"}:
        die("cold-review other_reviewer_output_seen must be yes or no")
    if values["authoring_context_reuse"] == "yes":
        die("authoring-context reuse labels self-critique and cannot discharge cold review")
    for key in ("base_sha", "head_sha"):
        if not re.fullmatch(r"[0-9a-f]{40}", values[key]):
            die(f"cold-review {key} must be full lowercase 40-hex")
    if values["base_sha"] != declared_base or values["head_sha"] != declared_head:
        die("cold-review attestation base/head must match the STATE review identity")

    report_state_near = [item for item in report if re.match(r"^\s*Report state\s*:", item, re.I)]
    report_state_exact = [item for item in report if item == "Report state: FINAL"]
    if len(report_state_near) != 1 or len(report_state_exact) != 1:
        die("cold-review artifact requires exactly one Report state: FINAL")

    identity_re = re.compile(
        r"^model-identity: requested_model: ([^|\s][^|]*) \| "
        r"actual_model: ([^|\s][^|]*) \| evidence: "
        r"(?:self-report|host-event:[^|\s][^|]*) \| "
        r"claims: (bound|IDENTITY_UNBOUND)$"
    )
    identities = []
    for state_line in lines:
        identity_match = identity_re.fullmatch(state_line)
        if identity_match:
            identities.append(tuple(item.strip() for item in identity_match.groups()))
    matching_identity = [
        item for item in identities
        if item[0] == values["requested_model"] and item[1] == values["actual_model"]
    ]
    if len(matching_identity) != 1:
        die("cold-review attestation model pair must match one canonical STATE model-identity row")
    expected_claims = "bound" if values["requested_model"] == values["actual_model"] else "IDENTITY_UNBOUND"
    if matching_identity[0][2] != expected_claims:
        die("cold-review attestation model pair conflicts with STATE identity claims")
    if disposition == "PASS" and expected_claims != "bound":
        die("cold-review PASS requires bound requested_model and actual_model identity")

    allowed = {"PASS", "GAP-REVISE", "BLOCKED", "OWNER DECISION"}
    nonempty = [item for item in report if item.strip()]
    terminal = [item for item in report if item in allowed]
    if len(terminal) != 1 or not nonempty or nonempty[-1] != disposition:
        die("cold-review artifact requires one exact final disposition matching STATE")
    for prefix in ("Verdict:", "Disposition:", "cold-review-disposition:"):
        near_rows = [item for item in report if re.match(rf"^\s*{re.escape(prefix[:-1])}\s*:", item, re.I)]
        exact_rows = [item for item in report if item.startswith(prefix)]
        if len(near_rows) != len(exact_rows):
            die(f"cold-review artifact {prefix[:-1]} rows require exact grammar")
        for item in exact_rows:
            value = item.split(":", 1)[1].strip()
            if value not in allowed or value != disposition:
                die("cold-review artifact contains a contradictory disposition")

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    repo = git("rev-parse", "--show-toplevel")
    if repo.returncode != 0:
        die("cold-review identity requires a containing Git repository")
    for key, sha in (("base_sha", declared_base), ("head_sha", declared_head)):
        resolved = git("cat-file", "-t", sha)
        if resolved.returncode != 0 or resolved.stdout.strip() != "commit":
            die(f"cold-review {key} does not resolve to a commit")
    if declared_base == declared_head:
        die("cold-review base_sha must strictly precede head_sha")
    ancestry = git("merge-base", "--is-ancestor", declared_base, declared_head)
    if ancestry.returncode != 0:
        die("cold-review base_sha must be an ancestor of head_sha")
PY
)"; then
      [ -n "$cold_error" ] || cold_error="cold-review attestation validation failed"
      err "$cold_error"
    fi
  fi
fi

# The repository-side #86 successor/non-verdict parser is mandatory whenever a
# live record root carries those prospective rows. Direct Markdown files are
# the record surface; nested installs, frozen repositories, and fixture corpora
# retain their own custody and must not activate the current root's parser.
# Installed consumers without the repo checker still fail closed for an actual
# direct live row instead of silently treating the contract as optional.
if grep -E -q '^(successor-review:|lane-status: status: REVIEWER_RUNTIME_NON_VERDICT)' \
  "$run_root"/*.md 2>/dev/null; then
  validator_repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." 2>/dev/null && pwd || true)"
  live_cold_checker="$validator_repo_root/scripts/check-cold-review-contract.sh" # source repo checker; absent from installed skill by design
  if [ -z "$validator_repo_root" ] || [ ! -f "$live_cold_checker" ] || [ -L "$live_cold_checker" ]; then
    err "live successor/non-verdict rows require the repository cold-review checker"
  elif ! bash "$live_cold_checker" --run-root "$run_root" >/dev/null; then
    err "live successor/non-verdict contract failed"
  fi
fi

if [ -f "$state" ] && grep -qi '^## Context epochs and instruction applicability' "$state"; then
  current_epoch="$(sed -n 's/^Current epoch: //p' "$state")"
  if ! printf '%s\n' "$current_epoch" | grep -Eq '^(e[1-9][0-9]*|G[0-9A-F]{4})$' \
      || [ "$current_epoch" = G0000 ]; then
    err "STATE.md Current epoch must be a positive legacy eNN identity or canonical G plus uppercase HEX4"
  fi
  bad_epoch_id="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      e=$2; gsub(/^[ \t]+|[ \t]+$/, "", e)
      if (e ~ /^[eGg]/ &&
          (e !~ /^(e[1-9][0-9]*|G[0-9A-F]{4})$/ || e == "G0000")) print e
    }' "$state")"
  if [ -n "$bad_epoch_id" ]; then
    err "STATE.md epoch row(s) use malformed durable generation identities: $(printf '%s' "$bad_epoch_id" | tr '\n' ' ')"
  fi
  bad_prov="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*(e[1-9][0-9]*|G[0-9A-F]{4})[[:space:]]*\|/ {
      p=$3; gsub(/^[ \t]+|[ \t]+$/, "", p)
      e=$2; gsub(/^[ \t]+|[ \t]+$/, "", e)
      if (p !~ /^(host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap)$/) print e
    }' "$state")"
  if [ -n "$bad_prov" ]; then
    err "STATE.md epoch row(s) with invalid boundary provenance: $(printf '%s' "$bad_prov" | tr '\n' ' ') (allowed: host-reported-compaction / new-session / handoff-resume / manual-resume / inferred-context-gap; never fabricate a compaction)"
  fi
  bad_instr="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      k=$4; gsub(/^[ \t]+|[ \t]+$/, "", k)
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      okk = (k ~ /^(one-shot-action|standing-constraint|standing-authorization|persistent-objective|query-or-information-request)$/)
      oks = (s ~ /^(active|satisfied|superseded|revoked|expired|ambiguous)$/)
      if (!okk || !oks) print n
    }' "$state")"
  if [ -n "$bad_instr" ]; then
    err "STATE.md instruction row(s) with invalid kind/status token: $(printf '%s' "$bad_instr" | tr '\n' ' ') (kind: one-shot-action / standing-constraint / standing-authorization / persistent-objective / query-or-information-request; status: active / satisfied / superseded / revoked / expired / ambiguous)"
  fi
  no_ev="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      ev=$9; gsub(/^[ \t]+|[ \t]+$/, "", ev)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      if (s ~ /^(satisfied|superseded|revoked|expired)$/ &&
          (ev == "" || ev ~ /^-+$/)) print n
    }' "$state")"
  if [ -n "$no_ev" ]; then
    err "STATE.md instruction row(s) with terminal status but no status evidence: $(printf '%s' "$no_ev" | tr '\n' ' ') (satisfied/superseded/revoked/expired require evidence — a bare terminal claim is the replay hazard #35 forbids)"
  fi
fi

if [ -f "$state" ]; then
  short_anchors="$(grep -oE '@[0-9a-f]{7,}' "$state" 2>/dev/null \
    | grep -vE '^@[0-9a-f]{40}$' || true)"
  if [ -n "$short_anchors" ]; then
    err "STATE.md evidence anchor(s) not full 40-hex SHAs: $(printf '%s' "$short_anchors" | tr '\n' ' ')"
  fi
fi

if [ -f "$run_root/ROADMAP.md" ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r n; do
    [ -f "$run_root/phases/phase-$n.md" ] || err "ROADMAP names phase $n but phases/phase-$n.md is missing"
  done < <(grep -oE '^\| *[0-9]+ *\|' "$run_root/ROADMAP.md" 2>/dev/null | grep -oE '[0-9]+' | sort -un)
fi

check_background_chains "$run_root" "$state"

if [ -f "$run_root/respec-impact-set.md" ]; then
  respec_checker="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-respec-impact-set.sh"
  respec_output="$(bash "$respec_checker" "$run_root/respec-impact-set.md" 2>&1)" \
    || err "respec-impact-set.md invalid: $respec_output"
fi

if [ "$err_count" -gt 0 ]; then
  printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
  exit 1
fi
printf 'validate-run-root: ok\n'
