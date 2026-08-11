#!/usr/bin/env bash
set -euo pipefail


fail() { printf 'check-closure-surface: %s\n' "$*" >&2; exit 1; }

py_cmd=()
ensure_python() {
  [ "${#py_cmd[@]}" -eq 0 ] || return 0
  if command -v python >/dev/null 2>&1; then py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
  else fail "python, python3, or py -3 is required for structured closure validation"
  fi
}

if [ "${1:-}" = --residual-routing ]; then
  shift; [ "$#" -gt 0 ] || fail "--residual-routing requires one or more STATE ledgers"
  ensure_python
  "${py_cmd[@]}" - "$@" <<'PY'
import pathlib, re, sys
allowed = {"unresolved", "deferred", "transferred", "owner-assigned", "risk-accepted", "validated-resolved", "SUPERSEDED_BY_CONCURRENT_MUTATION"}
seen = {}
for name in sys.argv[1:]:
    path = pathlib.Path(name)
    if not path.is_file():
        raise SystemExit(f"check-closure-surface: residual ledger not found: {name}")
    run = str(path.resolve())
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) == 5 and cells[1] == "yes" and cells[2] in allowed:
            seen.setdefault(cells[0], []).append((run, cells[3]))
for identity, rows in seen.items():
    if len({run for run, _ in rows}) < 2:
        continue
    refs = [ref for _, ref in rows]
    if not any(re.search(r"(?:issue )?#\d+|/issues/\d+|tracker:[^ ]", ref, re.I) or re.fullmatch(r"owner-refusal:.+", ref, re.I) for ref in refs):
        raise SystemExit(f"check-closure-surface: repeated residual '{identity}' has no durable tracker or owner refusal")
print("check-closure-surface: residual routing ok")
PY
  exit $?
fi

if [ "${1:-}" = --automatic-effects ]; then
  shift
  [ "$#" -eq 4 ] \
    || fail "--automatic-effects requires <repo-root> <event> <ref> <mutation-plan>"
  effect_root="$1"; effect_event="$2"; effect_ref="$3"; effect_plan="$4"
  [ -d "$effect_root" ] || fail "automatic-effect repo root not found: $effect_root"
  [ -f "$effect_plan" ] || fail "automatic-effect mutation plan not found: $effect_plan"
  ensure_python
  "${py_cmd[@]}" - "$effect_root" "$effect_event" "$effect_ref" "$effect_plan" <<'PY'
import fnmatch
import pathlib
import re
import sys


root = pathlib.Path(sys.argv[1]).resolve()
event = sys.argv[2]
ref = sys.argv[3]
if ref.startswith("refs/heads/"):
    ref = ref[len("refs/heads/"):]
plan = pathlib.Path(sys.argv[4]).resolve()
workflow_root = root / ".github" / "workflows"
if event != "push" or not ref:
    raise SystemExit("check-closure-surface: automatic-effect preflight requires push and a nonempty branch ref")


def die(message):
    raise SystemExit(f"check-closure-surface: {message}")


def uncomment(line):
    quote = None
    result = []
    for char in line:
        if char in {"'", '"'}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        if char == "#" and quote is None:
            break
        result.append(char)
    return "".join(result).rstrip()


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


key_pattern = re.compile(r'(?:(?:"([^"]*)")|(?:\'([^\']*)\')|([A-Za-z0-9_-]+))\s*:\s*(.*)')


def mapping_entry(text):
    match = key_pattern.fullmatch(text)
    if not match:
        return None
    key = next(group for group in match.groups()[:3] if group is not None)
    return key, match.group(4)


def unsupported_collection_scalar(value):
    value = value.strip()
    if value.startswith(("*", "&", "!!", "!<")):
        return True
    if re.match(r"^![^\s]*\s+", value):
        return True
    return re.fullmatch(r"[|>](?:[1-9][+-]?|[+-][1-9]?)?", value) is not None


def reject_unsupported_collection_scalar(value, label):
    if not unsupported_collection_scalar(value):
        return
    if label in {"branches", "branches-ignore"}:
        die("unsupported aliased/tagged/block branch-filter scalar")
    die("unsupported YAML trigger scalar")


def inline_list(value, label):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        items = []
        buffer = []
        quote = None
        for char in value[1:-1]:
            if char in {"'", '"'}:
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
            if char == "," and quote is None:
                item = "".join(buffer).strip()
                reject_unsupported_collection_scalar(item, label)
                item = scalar(item)
                if item:
                    items.append(item)
                buffer = []
            else:
                buffer.append(char)
        if quote is not None:
            die("unterminated quote in inline YAML list")
        item = "".join(buffer).strip()
        reject_unsupported_collection_scalar(item, label)
        item = scalar(item)
        if item:
            items.append(item)
        return items
    if value.startswith("[") or value.endswith("]"):
        die("malformed inline YAML list")
    if value.startswith(("{", "*", "&", "!")) or "," in value:
        die("unsupported YAML trigger scalar")
    return [scalar(value)] if value else []


def pattern_matches(patterns, branch):
    matched = False
    for pattern in patterns:
        negative = pattern.startswith("!")
        candidate = pattern[1:] if negative else pattern
        if fnmatch.fnmatchcase(branch, candidate):
            matched = not negative
    return matched


def yaml_nodes(path):
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    nodes = []
    for number, line in enumerate(raw_lines, 1):
        prefix = line[:len(line) - len(line.lstrip())]
        if "\t" in prefix:
            die(f"workflow YAML uses tab indentation: {path}:{number}")
        text = uncomment(line).strip()
        if text and text != "---":
            nodes.append((len(prefix), text, number))
    return nodes


def child_block(nodes, index, parent_indent):
    result = []
    for node in nodes[index + 1:]:
        if node[0] <= parent_indent:
            break
        result.append(node)
    return result


def direct_mapping(nodes, label):
    if not nodes:
        return {}
    direct_indent = min(node[0] for node in nodes)
    entries = {}
    for index, (indent, text, number) in enumerate(nodes):
        if indent != direct_indent:
            continue
        parsed = mapping_entry(text)
        if parsed is None:
            die(f"malformed {label} mapping at line {number}: {text}")
        key, value = parsed
        if key in entries:
            die(f"duplicate {label} key '{key}'")
        entries[key] = (value, index, indent)
    return entries


def sequence_values(nodes, label):
    if not nodes:
        return []
    direct_indent = min(node[0] for node in nodes)
    values = []
    for indent, text, number in nodes:
        if indent != direct_indent:
            continue
        match = re.fullmatch(r"-\s*(.+)", text)
        if not match:
            die(f"malformed {label} sequence at line {number}: {text}")
        value = match.group(1).strip()
        reject_unsupported_collection_scalar(value, label)
        values.append(scalar(value))
    return values


def list_value(nodes, entry, label):
    value, index, indent = entry
    if value:
        return inline_list(value, label)
    return sequence_values(child_block(nodes, index, indent), label)


def top_mapping(nodes, path):
    top = [node for node in nodes if node[0] == 0]
    entries = {}
    for node in top:
        parsed = mapping_entry(node[1])
        if parsed is None:
            die(f"malformed top-level workflow mapping: {path}:{node[2]}")
        key, value = parsed
        if key in entries:
            die(f"duplicate top-level workflow key '{key}': {path}")
        entries[key] = (value, nodes.index(node), node[0])
    return entries


def trigger_matches(path, nodes):
    top = top_mapping(nodes, path)
    if "on" not in top:
        die(f"workflow has no top-level on mapping: {path}")
    on_value, on_index, on_indent = top["on"]
    if on_value:
        if on_value.startswith("{"):
            die(f"workflow trigger cannot be statically resolved: {path}")
        return event in inline_list(on_value, "trigger")

    block = child_block(nodes, on_index, on_indent)
    events = direct_mapping(block, "on")
    if event not in events:
        return False
    event_value, event_index, event_indent = events[event]
    if event_value and event_value not in {"{}", "null", "~"}:
        die(f"workflow {event} trigger cannot be statically resolved: {path}")

    event_block = child_block(block, event_index, event_indent)
    filters = direct_mapping(event_block, event)
    branch_filters = any(key in filters for key in {"branches", "branches-ignore"})
    tag_filters = any(key in filters for key in {"tags", "tags-ignore"})
    if tag_filters and not branch_filters:
        return False
    branches = list_value(event_block, filters["branches"], "branches") if "branches" in filters else None
    branches_ignore = list_value(event_block, filters["branches-ignore"], "branches-ignore") if "branches-ignore" in filters else []
    if branches is not None and (not branches or not pattern_matches(branches, ref)):
        return False
    if branches_ignore and pattern_matches(branches_ignore, ref):
        return False
    return True


def step_uses(nodes, path):
    top = top_mapping(nodes, path)
    if "jobs" not in top:
        return []
    jobs_value, jobs_index, jobs_indent = top["jobs"]
    if jobs_value:
        die(f"inline jobs mapping cannot be statically resolved: {path}")
    jobs_block = child_block(nodes, jobs_index, jobs_indent)
    jobs = direct_mapping(jobs_block, "jobs")
    uses = []
    for job, (job_value, job_index, job_indent) in jobs.items():
        if job_value:
            die(f"inline job mapping cannot be statically resolved: {path}:{job}")
        job_block = child_block(jobs_block, job_index, job_indent)
        properties = direct_mapping(job_block, f"job {job}")
        if "steps" not in properties:
            continue
        steps_value, steps_index, steps_indent = properties["steps"]
        if steps_value:
            die(f"inline steps cannot be statically resolved: {path}:{job}")
        steps_block = child_block(job_block, steps_index, steps_indent)
        if not steps_block:
            continue
        step_indent = min(node[0] for node in steps_block)
        step_starts = [index for index, node in enumerate(steps_block) if node[0] == step_indent]
        for position, start in enumerate(step_starts):
            indent, text, number = steps_block[start]
            if not text.startswith("-"):
                die(f"malformed steps sequence at {path}:{number}")
            end = step_starts[position + 1] if position + 1 < len(step_starts) else len(steps_block)
            step_nodes = steps_block[start:end]
            remainder = text[1:].strip()
            fields = {}
            if remainder:
                parsed = mapping_entry(remainder)
                if parsed is None:
                    die(f"malformed step mapping at {path}:{number}")
                fields[parsed[0]] = parsed[1]
            child_nodes = step_nodes[1:]
            if child_nodes:
                for key, entry in direct_mapping(child_nodes, "step").items():
                    if key in fields:
                        die(f"duplicate step key '{key}' at {path}:{number}")
                    fields[key] = entry[0]
            if "uses" in fields:
                raw_value = fields["uses"].strip()
                if raw_value.startswith(("*", "&", "!", "|", ">")):
                    die(f"unsupported aliased/tagged/block uses scalar at {path}:{number}")
                value = scalar(raw_value)
                if not value:
                    die(f"empty uses value at {path}:{number}")
                uses.append(value)
    return uses


def direct_effects(path, relative, nodes):
    effects = {f"workflow-run:{relative}"}
    if any(value.lower().startswith("actions/deploy-pages@") for value in step_uses(nodes, path)):
        effects.add("deployment:github-pages")
    return effects


workflows = []
effects = set()
for directory in (root / ".github", workflow_root):
    if directory.is_symlink():
        die(f"workflow directory must not be a symlink: {directory}")
if workflow_root.exists() and not workflow_root.is_dir():
    die(f"workflow path is not a directory: {workflow_root}")
if workflow_root.is_dir():
    for path in sorted(workflow_root.iterdir()):
        if path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        if path.is_symlink():
            die(f"workflow must be a non-symlink regular file: {path}")
        if not path.is_file():
            die(f"workflow must be a regular file: {path}")
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError):
            die(f"workflow escapes the canonical repository root: {path}")
        nodes = yaml_nodes(path)
        if trigger_matches(path, nodes):
            relative = path.relative_to(root).as_posix()
            workflows.append(relative)
            effects.update(direct_effects(path, relative, nodes))

plan_lines = plan.read_text(encoding="utf-8").splitlines()
records = [line for line in plan_lines if line.startswith("automatic-effect-preflight:")]
if len(records) != 1:
    if effects:
        die("automatic-effect-preflight record missing for matching workflow effects")
    die("automatic-effect-preflight trigger read missing")

segments = records[0].split("|")
segments[0] = segments[0][len("automatic-effect-preflight:"):]
fields = {}
order = []
for segment in segments:
    if ":" not in segment:
        die("automatic-effect-preflight has a malformed field")
    key, value = segment.split(":", 1)
    key, value = key.strip(), value.strip()
    if key in fields:
        die(f"automatic-effect-preflight has duplicate field '{key}'")
    fields[key] = value
    order.append(key)
expected_order = ["event", "ref", "workflows", "effects", "post-state-readback", "excluded-outcomes"]
if order != expected_order:
    die("automatic-effect-preflight fields must use canonical order")
if fields["event"] != event or fields["ref"] != ref:
    die("automatic-effect-preflight event/ref does not match the authorized mutation")

expected_workflows = ",".join(sorted(workflows)) if workflows else "none"
expected_effects = ",".join(sorted(effects)) if effects else "none"
if fields["workflows"] != expected_workflows:
    die(f"automatic-effect-preflight workflows mismatch (expected {expected_workflows})")
if fields["effects"] != expected_effects:
    die(f"automatic-effect-preflight effects mismatch (expected {expected_effects})")

readbacks = {"workflow-runs@pushed-sha"} if workflows else set()
if any(effect.startswith("deployment:") for effect in effects):
    readbacks.add("deployments@pushed-sha")
expected_readback = ",".join(sorted(readbacks)) if readbacks else "trigger-read-only"
if fields["post-state-readback"] != expected_readback:
    die(f"automatic-effect-preflight readback mismatch (expected {expected_readback})")
excluded = fields["excluded-outcomes"].lower()
if not excluded:
    die("automatic-effect-preflight excluded-outcomes must be nonempty")
if any(effect.startswith("deployment:") for effect in effects) and "deployment" in excluded:
    die("automatic-effect-preflight excludes a configured deployment effect")
if any(effect.startswith("workflow-run:") for effect in effects) and re.search(r"(?:no|without)[ -]+workflow[ -]+run", excluded):
    die("automatic-effect-preflight excludes a configured workflow-run effect")
if effects and re.search(r"(?:no|without)[ -]+automatic[ -]+effects?", excluded):
    die("automatic-effect-preflight excludes configured automatic effects")
if any(effect.lower() in {item.strip() for item in excluded.split(",")} for effect in effects):
    die("automatic-effect-preflight excludes a configured automatic effect")
print("check-closure-surface: automatic effects ok")
PY
  exit $?
fi

file="${1:-}"
[ -f "$file" ] || fail "record file not found: ${file:-<none>}"
shift
impact_set=""
closure_evidence=""
superseded_plans=()
steer_dir=""
plan_cycle_records=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --impact-set)
      [ "$#" -ge 2 ] || fail "--impact-set requires a file"
      impact_set="$2"; shift 2 ;;
    --closure-evidence)
      [ "$#" -ge 2 ] || fail "--closure-evidence requires a file"
      closure_evidence="$2"; shift 2 ;;
    --superseded-plan)
      [ "$#" -ge 2 ] || fail "--superseded-plan requires a file"
      superseded_plans+=("$2"); shift 2 ;;
    --steer-dir)
      [ "$#" -ge 2 ] || fail "--steer-dir requires a directory"
      steer_dir="$2"; shift 2 ;;
    --plan-cycle-record)
      [ "$#" -ge 2 ] || fail "--plan-cycle-record requires a file"
      plan_cycle_records+=("$2"); shift 2 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

rank() {
  case "$1" in
    source) echo 0;; generated-artifact) echo 1;; package) echo 2;;
    installed-payload) echo 3;; running-local-service) echo 4;;
    deployed-service) echo 5;; api) echo 6;; user-visible) echo 7;;
    publication) echo 8;; *) echo -1;;
  esac
}

field() {
  printf '%s\n' "$1" | tr '|' '\n' | while IFS= read -r seg; do
    k="$(printf '%s' "$seg" | sed -n 's/^[[:space:]]*\([a-z_-]*\):.*/\1/p')"
    if [ "$k" = "$2" ]; then
      printf '%s' "$seg" | sed "s/^[[:space:]]*$2:[[:space:]]*//; s/[[:space:]]*$//"
      return
    fi
  done
}

field_count() {
  printf '%s\n' "$1" | tr '|' '\n' | sed -n "s/^[[:space:]]*$2:[[:space:]].*/x/p" | wc -l | tr -d '[:space:]'
}

rows=0
coverage_rows=0
seen_ids=""
while IFS= read -r line; do
  case "$line" in resource-exhausted:*)
    qid="$(field "$line" resource-exhausted)"
    qclass="$(field "$line" class)"
    blocker="$(field "$line" blocker)"
    reported="$(field "$line" reported_reset)"
    backoff="$(field "$line" backoff_probe_at)"
    next_probe="$(field "$line" next_probe_at)"
    capacity="$(field "$line" capacity_probe)"
    probe_evidence="$(field "$line" probe_evidence)"
    terminal="$(field "$line" terminal)"
    [ -n "$qid" ] || fail "resource-exhausted row has no identity"
    [ "$qclass" = transport-infrastructure ] \
      || fail "resource-exhausted $qid: class must be transport-infrastructure"
    [ "$blocker" = resource-exhausted ] \
      || fail "resource-exhausted $qid: blocker must be resource-exhausted"
    printf '%s' "$reported" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z ADVISORY$' \
      || fail "resource-exhausted $qid: reported_reset must be canonical UTC and labelled ADVISORY"
    reported_ts="${reported%% *}"
    printf '%s' "$backoff" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' \
      || fail "resource-exhausted $qid: invalid backoff_probe_at"
    expected_next="$reported_ts"
    if [[ "$backoff" < "$expected_next" ]]; then expected_next="$backoff"; fi
    [ "$next_probe" = "$expected_next" ] \
      || fail "resource-exhausted $qid: next_probe_at must equal min(reported_reset, backoff_probe_at)"
    case "$capacity" in succeeded|failed) : ;;
      *) fail "resource-exhausted $qid: blocked/resume decision requires a completed cheap capacity probe";;
    esac
    [ -n "$probe_evidence" ] && [ "$probe_evidence" != none ] \
      || fail "resource-exhausted $qid: capacity probe has no checkable evidence"
    case "$capacity:$terminal" in
      succeeded:resumed|failed:blocked) : ;;
      succeeded:blocked) fail "resource-exhausted $qid: successful probe must resume before an advisory reset";;
      failed:resumed) fail "resource-exhausted $qid: failed probe cannot justify resumption";;
      *) fail "resource-exhausted $qid: invalid terminal '$terminal'";;
    esac
    continue
    ;;
  esac
  if printf '%s' "$line" | grep -qiE '^[[:space:]]*claim:'; then
    case "$line" in claim:*) : ;; *)
      fail "malformed claim row (key must be exactly lowercase 'claim:'): ${line%%|*}";;
    esac
  fi
  case "$line" in claim:*) : ;; *) continue;; esac
  rows=$((rows + 1))
  cid="$(field "$line" claim)"
  case " $seen_ids " in *" $cid "*)
    fail "duplicate Claim-ID '$cid' — each closure claim has one row";;
  esac
  seen_ids="$seen_ids $cid"
  surface="$(field "$line" surface)"
  status="$(field "$line" status)"
  esurface="$(field "$line" 'evidence-surface')"
  coverage="$(field "$line" coverage)"
  range_note="$(field "$line" range)"
  omission="$(field "$line" omission)"
  if [ -n "$coverage" ]; then
    coverage_rows=$((coverage_rows + 1))
    case "$coverage" in full|partial) : ;;
      *) fail "claim $cid: invalid coverage '$coverage' (expected full or partial)";;
    esac
  fi
  if [ "$coverage" = partial ]; then
    [ -n "$range_note" ] && [ -n "$omission" ] \
      || fail "claim $cid: partial coverage requires range and omission"
    [ "$status" != verified ] \
      || fail "claim $cid: partial coverage cannot support verified closure"
  fi
  if [ "$coverage" = full ] \
     && printf '%s' "$line" | grep -qi 'warning:[[:space:]]*truncated output'; then
    fail "claim $cid: truncation marker contradicts coverage full"
  fi
  [ "$(rank "$surface")" -ge 0 ] || fail "claim $cid: unknown required surface '$surface'"
  case "$status" in
    verified|failed|unverified|not-applicable) : ;;
    *) fail "claim $cid: invalid verification status '$status'";;
  esac
  if [ "$status" = verified ]; then
    [ -n "$esurface" ] || fail "claim $cid: verified with no evidence-surface — an uninspectable surface must be unverified/deferred"
    er="$(rank "$esurface")"
    sr="$(rank "$surface")"
    [ "$er" -ge 0 ] || fail "claim $cid: unknown evidence-surface '$esurface'"
    if [ "$er" -lt "$sr" ]; then
      fail "claim $cid: layer promotion — '$surface' claim verified only by lower-layer '$esurface' evidence"
    fi
  fi
done < "$file"

# #89 publication identity is prospective and deterministic. A publication
# claim is never kept verified merely because its label still resolves: the
# evidence digest must equal a hash-bound current-digest receipt. Drift is
# retained explicitly as SUPERSEDED.
if grep -Eq '^claim:.*\|[[:space:]]*surface:[[:space:]]*publication([[:space:]]*\||$)|^publication-identity:' "$file"; then
  ensure_python
  publication_error=""
  if ! publication_error="$("${py_cmd[@]}" - "$file" <<'PY'
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

record = Path(sys.argv[1]).resolve()
base = record.parent
sha_re = re.compile(r"[0-9a-f]{64}")


def die(message: str) -> None:
    print(message)
    raise SystemExit(1)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate:{key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"constant:{value}")


def fields(line: str, first_key: str) -> dict[str, str]:
    parts = [part.strip() for part in line.split("|")]
    values: dict[str, str] = {}
    for index, part in enumerate(parts):
        if ":" not in part:
            die(f"publication identity malformed field: {part!r}")
        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()
        if index == 0 and key != first_key:
            die(f"publication identity row must begin with {first_key}:")
        if key in values:
            die(f"publication identity duplicate field: {key}")
        values[key] = value
    return values


claims: dict[str, dict[str, str]] = {}
identities: dict[str, dict[str, str]] = {}
for raw in record.read_text(encoding="utf-8").splitlines():
    if raw.startswith("claim:"):
        values = fields(raw, "claim")
        if values.get("surface") == "publication":
            claim_id = values.get("claim", "")
            if not claim_id or claim_id in claims:
                die("publication claim id is missing or duplicated")
            claims[claim_id] = values
    elif raw.startswith("publication-identity:"):
        values = fields(raw, "publication-identity")
        claim_id = values.get("publication-identity", "")
        if not claim_id or claim_id in identities:
            die("publication identity claim id is missing or duplicated")
        identities[claim_id] = values

if set(claims) != set(identities):
    missing = sorted(set(claims) - set(identities))
    dangling = sorted(set(identities) - set(claims))
    die(f"publication identity rows must match publication claims; missing={missing} dangling={dangling}")

local_identity = {
    "publication-identity",
    "live-digest-file",
    "live-file-sha256",
    "live-digest",
    "disposition",
}
hosted_fields = (
    "publication-kind", "release-id", "tag", "asset-id", "asset-name",
    "asset-size", "asset-digest", "qualified-repository", "qualified-commit",
    "qualified-tree", "qualified-package-file", "release-url", "asset-url",
    "download-url", "public-readback-file", "public-readback-sha256",
    "downloaded-asset-file", "disposition",
)
hosted_identity = {"publication-identity", *hosted_fields}
for claim_id, claim in claims.items():
    identity = identities[claim_id]
    evidence_digest = claim.get("evidence-digest", "")
    if not sha_re.fullmatch(evidence_digest):
        die(f"claim {claim_id}: publication evidence-digest must be lowercase SHA-256")
    publication_kind = claim.get("publication-kind", "local-digest")
    if publication_kind not in {"local-digest", "hosted-release-asset"}:
        die(f"claim {claim_id}: publication-kind must be local-digest or hosted-release-asset")

    if publication_kind == "hosted-release-asset":
        if set(identity) != hosted_identity or identity.get("publication-kind") != publication_kind:
            if set(identity) == local_identity:
                die(f"claim {claim_id}: hosted release asset requires release/tag/asset/qualification/public-readback identity")
            die(f"claim {claim_id}: hosted release asset requires repository/package/download/public-URL evidence")
        if any(not re.fullmatch(r"\S+", identity[key]) for key in ("release-id", "tag", "asset-id")):
            die(f"claim {claim_id}: hosted release identity token is empty or malformed")
        asset_name = identity["asset-name"]
        if not asset_name or Path(asset_name).name != asset_name or "/" in asset_name or "\\" in asset_name:
            die(f"claim {claim_id}: asset-name must be a bare filename")
        if not re.fullmatch(r"[0-9]+", identity["asset-size"]) or not sha_re.fullmatch(identity["asset-digest"]):
            die(f"claim {claim_id}: hosted asset size or digest is malformed")
        if any(not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", identity[key]) for key in ("qualified-commit", "qualified-tree")):
            die(f"claim {claim_id}: qualified commit or tree identity is malformed")

        def contained(key, label, directory=False, suffix=""):
            name = identity[key]
            noun = "directory" if directory else "file"
            if not name or Path(name).name != name or "/" in name or "\\" in name or (suffix and not name.endswith(suffix)):
                die(f"claim {claim_id}: {key} must be a contained bare {noun}")
            path = base / name
            if path.is_symlink() or not (path.is_dir() if directory else path.is_file()):
                die(f"claim {claim_id}: {label} is missing or not a regular contained {noun}")
            return path

        repository = contained("qualified-repository", "qualified repository", True)
        git_command = ["git", "--no-replace-objects", "-C", str(repository), "rev-parse"]
        commit = identity["qualified-commit"]
        resolved = subprocess.run(
            [*git_command, "--verify", f"{commit}^{{commit}}"], capture_output=True, text=True
        ).stdout.strip()
        if resolved != commit:
            die(f"claim {claim_id}: qualified commit '{commit}' does not resolve in qualified repository")
        actual_tree = subprocess.run(
            [*git_command, f"{commit}^{{tree}}"], capture_output=True, text=True
        ).stdout.strip()
        if identity["qualified-tree"] != actual_tree:
            die(
                f"claim {claim_id}: qualified tree '{identity['qualified-tree']}' "
                f"does not match commit tree '{actual_tree}'"
            )

        package_file = contained("qualified-package-file", "qualified package")
        downloaded_file = contained("downloaded-asset-file", "downloaded asset")
        if package_file == downloaded_file:
            die(f"claim {claim_id}: downloaded asset must be an independent file readback")
        package_data = package_file.read_bytes()
        downloaded_data = downloaded_file.read_bytes()
        measured_size = len(package_data)
        measured_digest = hashlib.sha256(package_data).hexdigest()
        if int(identity["asset-size"]) != measured_size:
            die(
                f"claim {claim_id}: asset-size '{identity['asset-size']}' "
                f"does not match measured size '{measured_size}'"
            )
        if identity["asset-digest"] != measured_digest:
            die(f"claim {claim_id}: asset-digest does not match measured digest '{measured_digest}'")
        if downloaded_data != package_data:
            die(f"claim {claim_id}: downloaded asset bytes do not match qualified package")

        readback = contained("public-readback-file", "public readback", suffix=".json")
        readback_data = readback.read_bytes()
        readback_sha = identity["public-readback-sha256"]
        if not sha_re.fullmatch(readback_sha) or hashlib.sha256(readback_data).hexdigest() != readback_sha:
            die(f"claim {claim_id}: public readback SHA-256 mismatch")
        try:
            payload = json.loads(
                readback_data.decode("utf-8"),
                object_pairs_hook=unique_object,
                parse_constant=reject_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            die(f"claim {claim_id}: public-readback-file is not valid UTF-8 JSON")
        public_keys = (
            "release_id", "tag", "asset_id", "asset_name", "asset_size",
            "asset_digest", "qualified_commit", "qualified_tree", "release_url",
            "asset_url", "download_url",
        )
        if type(payload) is not dict or set(payload) != set(public_keys):
            die(f"claim {claim_id}: public readback must contain the exact release/asset/qualification fields")
        if type(payload["asset_size"]) is not int or payload["asset_size"] < 0:
            die(f"claim {claim_id}: public readback field type is invalid")
        for public_key in public_keys:
            identity_key = public_key.replace("_", "-")
            expected = int(identity[identity_key]) if public_key == "asset_size" else identity[identity_key]
            if payload[public_key] != expected:
                die(
                    f"claim {claim_id}: public readback {public_key} '{payload[public_key]}' "
                    f"does not match identity '{identity[identity_key]}'"
                )

        release_match = re.fullmatch(
            rf"https://api\.github\.com/repos/([^/?#]+)/([^/?#]+)/releases/{re.escape(identity['release-id'])}",
            identity["release-url"],
        )
        if not release_match:
            die(f"claim {claim_id}: release-url does not bind repository and release-id")
        owner, repo = release_match.groups()
        if identity["asset-url"] != f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{identity['asset-id']}":
            die(f"claim {claim_id}: asset-url does not bind repository and asset-id")
        expected_download_url = (
            f"https://github.com/{owner}/{repo}/releases/download/"
            f"{identity['tag']}/{identity['asset-name']}"
        )
        if identity["download-url"] != expected_download_url:
            die(f"claim {claim_id}: download-url does not bind repository, tag, and asset-name")
        disposition = identity["disposition"]
        status = claim.get("status", "")
        if evidence_digest == identity["asset-digest"]:
            if disposition != "verified":
                die(f"claim {claim_id}: stable hosted asset digest must use disposition verified")
        elif status == "verified" or disposition != "SUPERSEDED":
            die(f"claim {claim_id}: hosted asset digest drift is SUPERSEDED and cannot remain verified")
        continue

    if set(identity) != local_identity:
        die(f"claim {claim_id}: publication identity fields must be exactly {sorted(local_identity)}")
    live_digest = identity["live-digest"]
    file_digest = identity["live-file-sha256"]
    if not sha_re.fullmatch(live_digest) or not sha_re.fullmatch(file_digest):
        die(f"claim {claim_id}: live digest fields must be lowercase SHA-256")
    name = identity["live-digest-file"]
    if not name or Path(name).name != name or "/" in name or "\\" in name:
        die(f"claim {claim_id}: live-digest-file must be a contained bare filename")
    live_file = base / name
    if not live_file.is_file() or live_file.is_symlink():
        die(f"claim {claim_id}: live digest file is missing or not a regular contained file")
    data = live_file.read_bytes()
    if hashlib.sha256(data).hexdigest() != file_digest:
        die(f"claim {claim_id}: live digest file SHA-256 mismatch")
    try:
        observed = data.decode("ascii").strip()
    except UnicodeDecodeError:
        die(f"claim {claim_id}: live digest file must contain ASCII SHA-256")
    if not sha_re.fullmatch(observed) or observed != live_digest:
        die(f"claim {claim_id}: live digest field does not match the bound file")
    disposition = identity["disposition"]
    status = claim.get("status", "")
    if evidence_digest == live_digest:
        if disposition != "verified":
            die(f"claim {claim_id}: stable publication digest must use disposition verified")
    else:
        if status == "verified" or disposition != "SUPERSEDED":
            die(f"claim {claim_id}: publication digest drift is SUPERSEDED and cannot remain verified")
PY
  )"; then
    fail "$publication_error"
  fi
fi

# #87 closure identity fields are prospective. Once any field is present, the
# complete exact grammar is mandatory. Start/verify drift cannot close as
# unchanged, and repeated equivalent draws require a declared sampling budget.
if grep -Eqi '^[[:space:]]*(AUDIT_START_ANCHOR|AUDIT_VERIFY_ANCHOR|REANCHOR_DISPOSITION|REANCHOR_EVIDENCE|equivalent_config_attempts|stochasticity_budget|stochasticity_budget_anchor|stochasticity_budget_path|terminal_qualification):' "$file"; then
  exact_value() {
    local key="$1" required="${2:-yes}" near exact
    near="$(grep -Eic "^[[:space:]]*${key}[[:space:]]*:" "$file" || true)"
    exact="$(grep -Ec "^${key}: " "$file" || true)"
    [ "$near" -eq "$exact" ] || fail "$key must use exact case and column-zero grammar"
    [ "$exact" -le 1 ] || fail "$key must appear at most once"
    if [ "$required" = yes ]; then
      [ "$exact" -eq 1 ] || fail "$key must appear exactly once"
    fi
    if [ "$exact" -eq 1 ]; then sed -n "s/^${key}: //p" "$file"; fi
  }

  start_anchor="$(exact_value AUDIT_START_ANCHOR)"
  verify_anchor="$(exact_value AUDIT_VERIFY_ANCHOR)"
  disposition="$(exact_value REANCHOR_DISPOSITION)"
  reanchor_evidence="$(exact_value REANCHOR_EVIDENCE)"
  printf '%s' "$start_anchor" | grep -Eq '^[0-9a-f]{40}$' \
    || fail "AUDIT_START_ANCHOR must be a full lowercase 40-hex SHA"
  printf '%s' "$verify_anchor" | grep -Eq '^[0-9a-f]{40}$' \
    || fail "AUDIT_VERIFY_ANCHOR must be a full lowercase 40-hex SHA"
  current_head="$(git rev-parse HEAD 2>/dev/null || true)"
  [ "$verify_anchor" = "$current_head" ] \
    || fail "AUDIT_VERIFY_ANCHOR must equal current HEAD"
  git cat-file -e "${start_anchor}^{commit}" 2>/dev/null \
    || fail "AUDIT_START_ANCHOR must resolve to a local commit"
  if [ "$start_anchor" = "$verify_anchor" ]; then
    [ "$disposition" = unchanged ] \
      || fail "equal closure anchors require REANCHOR_DISPOSITION: unchanged"
    [ "$reanchor_evidence" = none ] \
      || fail "unchanged closure anchors require REANCHOR_EVIDENCE: none"
    if grep -Eqi '^[[:space:]]*reanchor-finding:' "$file" \
      || grep -Eqi '^[[:space:]]*residual:.*\|[[:space:]]*disposition:[[:space:]]*SUPERSEDED_BY_CONCURRENT_MUTATION([[:space:]]*\||[[:space:]]*$)' "$file"; then
      fail "unchanged closure anchors cannot carry reanchor-finding or concurrent-mutation residual rows"
    fi
  else
    [ "$disposition" = per-finding ] \
      || fail "moved closure anchor requires REANCHOR_DISPOSITION: per-finding"
    [ "$reanchor_evidence" = structured-rows ] \
      || fail "moved closure anchor requires REANCHOR_EVIDENCE: structured-rows"
    ensure_python
    reanchor_error=""
    if ! reanchor_error="$("${py_cmd[@]}" - "$file" "$verify_anchor" <<'PY'
import hashlib
import os
import pathlib
import re
import sys

record = pathlib.Path(sys.argv[1]).resolve()
verify = sys.argv[2]
lines = record.read_text(encoding="utf-8").splitlines()

def die(message):
    print(message)
    raise SystemExit(1)

def segments(line, prefix, required):
    parts = [part.strip() for part in line.split("|")]
    identity = parts[0][len(prefix):].strip()
    if not identity:
        die(f"{prefix[:-1]} row has no identity")
    values = {}
    for part in parts[1:]:
        if ":" not in part:
            die(f"{prefix[:-1]} {identity}: malformed field")
        key, value = (item.strip() for item in part.split(":", 1))
        if key in values or key not in required:
            die(f"{prefix[:-1]} {identity}: duplicate or unknown field {key}")
        values[key] = value
    if set(values) != set(required) or any(not values[key] for key in required):
        die(f"{prefix[:-1]} {identity}: requires exactly {', '.join(required)}")
    return identity, values

claim_ids = []
for line in lines:
    if line.startswith("claim:"):
        identity = line.split("|", 1)[0][len("claim:"):].strip()
        claim_ids.append(identity)

near_rows = [line for line in lines if re.match(r"^\s*(reanchor-finding|residual)\s*:", line, re.I)]
exact_rows = [line for line in lines if line.startswith("reanchor-finding:") or line.startswith("residual:")]
if len(near_rows) != len(exact_rows):
    die("reanchor finding/residual rows must use exact lowercase column-zero grammar")

found = {}
for line in exact_rows:
    if line.startswith("reanchor-finding:"):
        identity, values = segments(
            line, "reanchor-finding:", ("disposition", "evidence-file", "evidence-sha256")
        )
        if values["disposition"] != "reanchored":
            die(f"reanchor-finding {identity}: disposition must be reanchored")
    else:
        if "| disposition: SUPERSEDED_BY_CONCURRENT_MUTATION" not in line:
            continue
        identity, values = segments(
            line, "residual:", ("consequential", "disposition", "evidence-file", "evidence-sha256")
        )
        if values["consequential"] != "yes" or values["disposition"] != "SUPERSEDED_BY_CONCURRENT_MUTATION":
            die(f"residual {identity}: requires consequential yes and SUPERSEDED_BY_CONCURRENT_MUTATION")
    if identity in found:
        die(f"finding {identity}: duplicate re-anchor disposition")
    found[identity] = values

if set(found) != set(claim_ids) or len(found) != len(claim_ids):
    die("moved closure requires exactly one structured re-anchor or consequential residual row per claim")

base = record.parent.resolve()
for identity, values in found.items():
    rel = values["evidence-file"]
    pure = pathlib.PurePosixPath(rel.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts or re.match(r"^[A-Za-z]:", rel):
        die(f"finding {identity}: unsafe evidence-file")
    evidence = (base / pathlib.Path(*pure.parts)).resolve()
    try:
        evidence.relative_to(base)
    except ValueError:
        die(f"finding {identity}: evidence-file escapes the record directory")
    if not evidence.is_file() or evidence.is_symlink():
        die(f"finding {identity}: evidence-file must resolve to a regular non-symlink file")
    data = evidence.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", values["evidence-sha256"]) or digest != values["evidence-sha256"]:
        die(f"finding {identity}: evidence SHA-256 mismatch")
    text = data.decode("utf-8").splitlines()
    required_lines = {
        f"Anchor: {verify}",
        f"Finding: {identity}",
        f"Disposition: {values['disposition']}",
    }
    if not required_lines.issubset(set(text)):
        die(f"finding {identity}: evidence artifact is not bound to finding, disposition, and VERIFY anchor")
PY
)"; then
      [ -n "$reanchor_error" ] || reanchor_error="structured re-anchor validation failed"
      fail "$reanchor_error"
    fi
  fi

  attempts="$(exact_value equivalent_config_attempts)"
  terminal_qualification="$(exact_value terminal_qualification)"
  budget="$(exact_value stochasticity_budget no)"
  budget_anchor="$(exact_value stochasticity_budget_anchor no)"
  budget_path="$(exact_value stochasticity_budget_path no)"
  printf '%s' "$attempts" | grep -Eq '^[1-9][0-9]*/(0|[1-9][0-9]*)$' \
    || fail "equivalent_config_attempts must be N_total/N_passing"
  total="${attempts%%/*}"
  passing="${attempts##*/}"
  [ "$passing" -le "$total" ] \
    || fail "equivalent_config_attempts passing count exceeds total"
  case "$terminal_qualification" in QUALIFIED|PROVISIONAL) : ;;
    *) fail "terminal_qualification must be QUALIFIED or PROVISIONAL" ;;
  esac
  budget_count=""
  if [ -n "$budget" ] && [ "$budget" != none ]; then
    printf '%s' "$budget" | grep -Eq '^[1-9][0-9]*$' \
      || fail "stochasticity_budget must be none or a positive integer"
    budget_count="$budget"
    [ "$budget_anchor" = "$start_anchor" ] \
      || fail "stochasticity_budget must be predeclared at AUDIT_START_ANCHOR"
    [ -n "$budget_path" ] || fail "numeric stochasticity_budget requires stochasticity_budget_path"
    case "$budget_path" in
      /*|*\\*|*:*|*/|.|..|./*|../*|*/./*|*/../*)
        fail "stochasticity_budget_path must be a safe repo-relative path"
        ;;
    esac
    [ "$(git cat-file -t "$start_anchor:$budget_path" 2>/dev/null || true)" = blob ] \
      || fail "stochasticity_budget_path must identify a tracked file at AUDIT_START_ANCHOR"
    budget_declaration="$(git show "$start_anchor:$budget_path" 2>/dev/null || true)"
    [ "$(printf '%s\n' "$budget_declaration" | grep -Ec "^stochasticity_budget: $budget$")" -eq 1 ] \
      || fail "stochasticity budget is not present in its tracked start-anchor declaration"
  elif [ -n "$budget_anchor" ] || [ -n "$budget_path" ]; then
    fail "stochasticity_budget_anchor/path require a numeric stochasticity_budget"
  fi
  if [ "$terminal_qualification" = QUALIFIED ] && [ "$passing" -eq 0 ]; then
    fail "a zero-pass equivalent configuration cannot be QUALIFIED"
  fi
  if [ "$total" -eq 1 ] && [ "$passing" -eq 1 ]; then
    [ "$terminal_qualification" = QUALIFIED ] \
      || fail "single 1/1 attempt is QUALIFIED, not PROVISIONAL"
  elif [ "$total" -gt 1 ] && { [ -z "$budget_count" ] || [ "$total" -gt "$budget_count" ]; }; then
    [ "$terminal_qualification" = PROVISIONAL ] \
      || fail "repeated equivalent attempts without an adequate predeclared budget must be PROVISIONAL"
  fi
fi

# #78 blocker rows are prospective and coexist with legacy claim-only records.
# Scope and still-runnable work are always explicit. A negative-capability
# assertion needs two case-normalized method identities, distinct method
# classes, and evidence bound to every method. Repeating or merely renaming a
# probe never manufactures confidence.
while IFS= read -r line; do
  if printf '%s' "$line" | grep -qiE '^[[:space:]]*blocker:'; then
    case "$line" in blocker:*) : ;; *)
      fail "malformed blocker row (key must be exactly lowercase 'blocker:'): ${line%%|*}";;
    esac
  fi
  case "$line" in blocker:*) : ;; *) continue;; esac
  bid="$(field "$line" blocker)"
  [ "$(field_count "$line" blocker)" = 1 ] && [ -n "$bid" ] \
    || fail "blocker row requires exactly one identity"
  for key in justification negative-capability probe_methods probe_evidence falsification_attempted terminal next_probe_or_abandon; do
    [ "$(field_count "$line" "$key")" -le 1 ] \
      || fail "blocker $bid: duplicate $key"
  done
  for key in blocked_scope unblocked_work; do
    [ "$(field_count "$line" "$key")" = 1 ] \
      || fail "blocker $bid: requires exactly one $key"
    [ -n "$(field "$line" "$key")" ] \
      || fail "blocker $bid: $key must be nonempty"
  done
  unblocked="$(field "$line" unblocked_work)"
  if [ "$unblocked" = none ]; then
    justification="$(field "$line" justification)"
    [ "$(field_count "$line" justification)" = 1 ] \
      && [ -n "$justification" ] && [ "$justification" != none ] \
      || fail "blocker $bid: unblocked_work none requires justification"
  fi
  negative="$(field "$line" negative-capability)"
  if [ -n "$negative" ] && [ "$negative" != true ] && [ "$negative" != false ]; then
    fail "blocker $bid: negative-capability must be true or false"
  fi
  if [ "$negative" = true ]; then
    methods="$(field "$line" probe_methods)"
    [ "$(field_count "$line" probe_methods)" = 1 ] && [ -n "$methods" ] \
      || fail "blocker $bid: negative capability requires probe_methods"
    probe_evidence="$(field "$line" probe_evidence)"
    [ "$(field_count "$line" probe_evidence)" = 1 ] && [ -n "$probe_evidence" ] \
      || fail "blocker $bid: negative capability requires probe_evidence"
    ensure_python
    probe_error=""
    if ! probe_error="$("${py_cmd[@]}" - "$methods" "$probe_evidence" <<'PY'
import re
import sys

methods = [part.strip() for part in sys.argv[1].split(",")]
if len(methods) < 2 or any(not part for part in methods):
    raise SystemExit("requires at least two nonempty probe methods")
normalized_methods = [part.casefold() for part in methods]
if len(set(normalized_methods)) != len(normalized_methods):
    raise SystemExit("probe methods must be distinct after case normalization")

entries = [part.strip() for part in sys.argv[2].split(";")]
if len(entries) != len(methods) or any(not part for part in entries):
    raise SystemExit("probe evidence must bind exactly one entry to every method")
classes = []
evidence_values = []
for index, entry in enumerate(entries):
    match = re.fullmatch(r"([^:;=]+)::([a-z0-9][a-z0-9-]*)=>(.+)", entry)
    if not match:
        raise SystemExit("probe evidence entries require method::method-class=>evidence")
    method, method_class, evidence = (part.strip() for part in match.groups())
    if method.casefold() != normalized_methods[index]:
        raise SystemExit("probe evidence method does not match probe_methods order")
    if not evidence or evidence.casefold() == "none":
        raise SystemExit("probe evidence must be nonempty and checkable")
    classes.append(method_class.casefold())
    evidence_values.append(evidence.casefold())
if len(set(classes)) != len(classes):
    raise SystemExit("probe method classes must be structurally distinct")
if len(set(evidence_values)) != len(evidence_values):
    raise SystemExit("probe evidence values must be distinct")
PY
)"; then
      [ -n "$probe_error" ] || probe_error="probe evidence validation failed"
      fail "blocker $bid: $probe_error"
    fi
    falsification="$(field "$line" falsification_attempted)"
    [ "$(field_count "$line" falsification_attempted)" = 1 ] \
      && [ -n "$falsification" ] && [ "$falsification" != none ] \
      || fail "blocker $bid: negative capability requires falsification_attempted"
  fi
  if [ "$(field "$line" terminal)" = blocked-non-verdict ]; then
    next_action="$(field "$line" next_probe_or_abandon)"
    [ "$(field_count "$line" next_probe_or_abandon)" = 1 ] \
      && [ -n "$next_action" ] && [ "$next_action" != none ] \
      || fail "blocker $bid: blocked-non-verdict requires next_probe_or_abandon"
  fi
done < "$file"

# #78 plan-cycle accounting is explicit only when a plan declares it. `none`
# carries no implicit cap. A numeric overrun needs a recorded OWNER_DECISION.
if [ "${#plan_cycle_records[@]}" -gt 0 ]; then
  ensure_python
  for cycle_file in "${plan_cycle_records[@]}"; do
    [ -f "$cycle_file" ] || fail "plan cycle record not found: $cycle_file"
    cycle_error=""
    if ! cycle_error="$("${py_cmd[@]}" - "$cycle_file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

def values(key):
    near = [line for line in lines if re.match(rf"^\s*{re.escape(key)}\s*:", line, re.I)]
    exact = [line.split(":", 1)[1].strip() for line in lines
             if line.startswith(key + ":")]
    if len(near) != len(exact):
        raise SystemExit(f"{key} must use exact uppercase grammar")
    if len(exact) != 1:
        raise SystemExit(f"{key} must appear exactly once")
    return exact[0]

bound = values("CYCLE_BOUND")
consumed_text = values("CYCLES_CONSUMED")
if not re.fullmatch(r"[0-9]+", consumed_text):
    raise SystemExit("CYCLES_CONSUMED must be a nonnegative integer")
consumed = int(consumed_text)
if bound == "none":
    pass
elif re.fullmatch(r"[0-9]+", bound):
    if consumed > int(bound):
        decisions = [line.split(":", 1)[1].strip() for line in lines
                     if line.startswith("BOUND_OVERRUN:")]
        if decisions != ["OWNER_DECISION"]:
            raise SystemExit("declared cycle-bound overrun requires BOUND_OVERRUN: OWNER_DECISION")
else:
    raise SystemExit("CYCLE_BOUND must be none or a nonnegative integer")
PY
)"; then
      [ -n "$cycle_error" ] || cycle_error="plan cycle validation failed"
      fail "$cycle_file: $cycle_error"
    fi
  done
fi

[ "$rows" -gt 0 ] || fail "no closure claim rows found"
[ "$coverage_rows" -eq 0 ] || [ "$coverage_rows" -eq "$rows" ] \
  || fail "closure record mixes coverage-tagged and untagged claim rows"

# #88 external-state schemas are prospective: only the new record prefixes,
# explicit #88 claim fields, and schema headings enter this validator. Existing
# claim rows and the source-to-publication rank ladder above retain their behavior.
schema_required=0
if grep -Eqi '^[[:space:]]*(external-mutation-record|external-authorization-grant|artifact-identity|collision-receipt|external-evidence):|external-(kind|mutation|mutation-record|authorization-grant):[[:space:]]|^## Suggested Commit Message When No Commit Authorized$' "$file"; then
  schema_required=1
fi
if [ "$schema_required" -eq 1 ]; then
  ensure_python
  schema_error=""
  if ! schema_error="$("${py_cmd[@]}" - "$file" <<'PY'
import ast
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import sys


path = os.path.abspath(sys.argv[1])
with open(path, "r", encoding="utf-8") as handle:
    lines = handle.read().splitlines()


def die(message):
    print(message)
    raise SystemExit(1)


def parse_segments(line, prefix, label, expected_fields):
    parts = line.split("|")
    identity = parts[0][len(prefix):].strip()
    if not identity:
        die(f"{label} has no identity")
    fields = {}
    order = []
    for segment in parts[1:]:
        if ":" not in segment:
            die(f"{label} {identity}: malformed field '{segment.strip()}'")
        raw_key, raw_value = segment.split(":", 1)
        key = raw_key.strip()
        value = raw_value.strip()
        if key in fields:
            die(f"{label} {identity}: duplicate field '{key}'")
        fields[key] = value
        order.append(key)
    for key in expected_fields:
        if key not in fields:
            die(f"{label} {identity}: missing {key}")
    unexpected = [key for key in order if key not in expected_fields]
    if unexpected:
        die(f"{label} {identity}: unexpected field '{unexpected[0]}'")
    if order != expected_fields:
        die(f"{label} {identity}: fields must use the canonical one-line order")
    return identity, fields


def loose_fields(line):
    fields = {}
    raw_keys = []
    for segment in line.split("|")[1:]:
        if ":" not in segment:
            continue
        raw_key, raw_value = segment.split(":", 1)
        key = raw_key.strip()
        raw_keys.append(key)
        if key not in fields:
            fields[key] = raw_value.strip()
    return fields, raw_keys


def token_in(command, token):
    return re.search(r"(?<![A-Za-z0-9_-])" + re.escape(token) + r"(?![A-Za-z0-9_-])", command) is not None


def valid_timestamp(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        return False
    try:
        dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def scalar_text(value):
    if isinstance(value, (dict, list)):
        return None
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


class DuplicateKey(ValueError):
    pass


class NonStandardConstant(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_constant(value):
    raise NonStandardConstant(value)


def readback_argv(command, runner):
    if runner == "python":
        try:
            expression = ast.parse(command, mode="eval").body
            if not isinstance(expression, ast.Call):
                return None
            function = expression.func
            if not (
                isinstance(function, ast.Attribute)
                and function.attr == "run"
                and isinstance(function.value, ast.Name)
                and function.value.id == "subprocess"
            ):
                return None
            if len(expression.args) != 1:
                return None
            argv = ast.literal_eval(expression.args[0])
            if not isinstance(argv, (list, tuple)) or not argv or not all(isinstance(item, str) for item in argv):
                return None
            keywords = {item.arg: ast.literal_eval(item.value) for item in expression.keywords if item.arg}
            if len(keywords) != len(expression.keywords):
                return None
            if set(keywords) - {"capture_output", "text", "check"}:
                return None
            if keywords.get("capture_output") is not True:
                return None
            return list(argv)
        except (SyntaxError, ValueError):
            return None

    shell_command = command.strip()
    if runner == "powershell" and shell_command.startswith("& "):
        shell_command = shell_command[2:].lstrip()
    if runner == "powershell" and re.search(r"[@$(){}\[\]]", shell_command):
        return None
    if re.search(r"[;&|`<>\r\n]|\$\(", shell_command):
        return None
    try:
        return shlex.split(shell_command, posix=True)
    except ValueError:
        return None


def api_endpoint_matches(endpoint, target_kind, target_id):
    escaped_id = re.escape(target_id)
    patterns = {
        "issue": rf"(?:^|/)issues/{escaped_id}(?:$|[/?])",
        "pr": rf"(?:^|/)pulls/{escaped_id}(?:$|[/?])",
        "milestone": rf"(?:^|/)milestones/{escaped_id}(?:$|[/?])",
        "label": rf"(?:^|/)labels/{escaped_id}(?:$|[/?])",
        "release": rf"(?:^|/)releases/(?:tags/)?{escaped_id}(?:$|[/?])",
        "release-asset": rf"(?:^|/)releases/assets/{escaped_id}(?:$|[/?])",
    }
    return re.search(patterns[target_kind], endpoint) is not None


def parse_readonly_options(arguments, value_flags, switch_flags):
    parsed = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in switch_flags:
            parsed.append((argument, None))
            index += 1
            continue
        if argument in value_flags:
            if index + 1 >= len(arguments):
                return None
            parsed.append((argument, arguments[index + 1]))
            index += 2
            continue
        equal_flag = next((
            flag for flag in value_flags
            if flag.startswith("--")
            and argument.startswith(flag + "=")
            and argument != flag + "="
        ), None)
        if equal_flag is not None:
            parsed.append((equal_flag, argument[len(equal_flag) + 1:]))
            index += 1
            continue
        return None
    return parsed


def approved_readback_query(command, runner, target_kind, target_id):
    argv = readback_argv(command, runner)
    if not argv:
        return False
    write_flags = {"--method", "-X", "--input", "--field", "-f", "--raw-field", "-F"}
    for argument in argv:
        if argument in write_flags:
            return False
        if any(argument.startswith(flag + "=") for flag in {"--method", "--input", "--field", "--raw-field"}):
            return False
        if any(argument.startswith(flag) and argument != flag for flag in {"-X", "-f", "-F"}):
            return False
    direct_forms = {
        "issue": ["gh", "issue", "view", target_id],
        "pr": ["gh", "pr", "view", target_id],
        "release": ["gh", "release", "view", target_id],
    }
    if target_kind in direct_forms and argv[:4] == direct_forms[target_kind]:
        return parse_readonly_options(
            argv[4:],
            {"--json", "--jq", "--template"},
            {"--comments", "--web"},
        ) is not None
    if target_kind == "label" and argv[:3] == ["gh", "label", "list"]:
        label_args = argv[3:]
        label_options = parse_readonly_options(
            label_args,
            {"--search", "--json", "--jq", "--template", "--limit", "--order", "--sort"},
            {"--web"},
        )
        if label_options is None:
            return False
        search_values = [value for flag, value in label_options if flag == "--search"]
        return search_values == [target_id]
    if len(argv) >= 3 and argv[:2] == ["gh", "api"]:
        endpoint = argv[2]
        if endpoint.startswith("-"):
            return False
        return api_endpoint_matches(endpoint, target_kind, target_id) and parse_readonly_options(
            argv[3:],
            {"--jq", "--template", "--hostname", "--cache"},
            {"--paginate", "--slurp", "--include", "--verbose"},
        ) is not None
    return False


def effective_mutation(command, runner):
    argv = readback_argv(command, runner)
    if not argv or len(argv) < 4 or argv[0] != "gh":
        return None
    direct_actions = {
        "issue": {"close", "reopen", "edit", "comment", "delete"},
        "pr": {"merge", "close", "reopen", "edit", "comment", "review"},
        "label": {"create", "edit", "delete"},
        "release": {"create", "edit", "delete"},
    }
    target_kind = argv[1]
    action = argv[2]
    target_id = argv[3]
    if target_kind not in direct_actions or action not in direct_actions[target_kind] or target_id.startswith("-"):
        return None
    return action, target_kind, target_id


prefix_labels = {
    "external-mutation-record:": "external-mutation-record",
    "external-authorization-grant:": "external-authorization-grant",
    "artifact-identity:": "artifact-identity",
    "collision-receipt:": "collision-receipt",
    "external-evidence:": "external-evidence",
}
for line in lines:
    stripped = line.lstrip()
    for prefix, label in prefix_labels.items():
        if stripped.lower().startswith(prefix.lower()) and not line.startswith(prefix):
            die(f"malformed {label} row (key must be exactly lowercase '{prefix}')")


claims = {}
claim_order = []
for line in lines:
    if not line.startswith("claim:"):
        continue
    claim_id = line.split("|", 1)[0][len("claim:"):].strip()
    fields, raw_keys = loose_fields(line)
    claims[claim_id] = fields
    claim_order.append(claim_id)
    external_keys = {"external-kind", "external-mutation", "external-mutation-record", "external-authorization-grant"}
    external_key_variants = [key for key in raw_keys if key.lower() in external_keys]
    for key in external_key_variants:
        if key not in external_keys:
            die(f"claim {claim_id}: malformed external field '{key}'")
    for key in ("external-kind", "external-mutation", "external-mutation-record", "external-authorization-grant"):
        if len([raw_key for raw_key in raw_keys if raw_key == key]) > 1:
            die(f"claim {claim_id}: duplicate field '{key}'")


mutation_fields = [
    "runner", "target-kind", "target-id", "mutation-command",
    "mutation-exit", "mutation-evidence", "readback-command",
    "readback-exit", "readback-file", "readback-sha256",
    "readback-field", "expected-value", "observed-value",
    "readback-evidence",
]
mutation_records = {}
mutation_effects = {}
record_dir = os.path.realpath(os.path.dirname(path))
target_kinds = {"issue", "pr", "milestone", "label", "release", "release-asset"}

grant_fields = ["record-file", "record-sha256"]
authorization_grants = {}
for line in lines:
    if not line.startswith("external-authorization-grant:"):
        continue
    grant_id, fields = parse_segments(
        line, "external-authorization-grant:", "external authorization grant", grant_fields
    )
    if grant_id in authorization_grants:
        die(f"duplicate external-authorization-grant ID '{grant_id}'")
    record_name = fields["record-file"]
    if not record_name or os.path.basename(record_name) != record_name or "/" in record_name or "\\" in record_name:
        die(f"authorization grant {grant_id}: record-file must be a bare relative filename")
    record_path = os.path.join(record_dir, record_name)
    if os.path.islink(record_path) or not os.path.isfile(record_path):
        die(f"authorization grant {grant_id}: record-file is missing, symlinked, or non-regular")
    record_data = open(record_path, "rb").read()
    record_sha = fields["record-sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", record_sha) or hashlib.sha256(record_data).hexdigest() != record_sha:
        die(f"authorization grant {grant_id}: record SHA-256 is malformed or mismatched")
    try:
        rows = [raw.split(":", 1) for raw in record_data.decode("utf-8").splitlines() if raw.strip()]
    except UnicodeDecodeError:
        die(f"authorization grant {grant_id}: record-file must be UTF-8")
    if any(len(row) != 2 for row in rows):
        die(f"authorization grant {grant_id}: record line is malformed")
    pairs = [(key.strip(), value.strip()) for key, value in rows]
    grant = dict(pairs)
    required = {"source", "grant_quote", "lifecycle", "action", "binds", "target_kind", "target_id"}
    if len(grant) != len(pairs) or any(not grant.get(key) for key in required) or grant["lifecycle"] != "standing-authorization":
        die(f"authorization grant {grant_id}: grant source or binding metadata is incomplete")
    bound_keys = [key.strip() for key in grant["binds"].split(",") if key.strip()]
    if len(bound_keys) != len(set(bound_keys)) or not {"target_kind", "target_id"}.issubset(bound_keys):
        die(f"authorization grant {grant_id}: binds must uniquely include target_kind,target_id")
    if grant["target_kind"] not in target_kinds or not re.fullmatch(r"\S+", grant["target_id"]):
        die(f"authorization grant {grant_id}: target binding is invalid")
    authorization_grants[grant_id] = grant

for line in lines:
    if not line.startswith("external-mutation-record:"):
        continue
    record_id, fields = parse_segments(
        line, "external-mutation-record:", "external mutation", mutation_fields
    )
    if record_id in mutation_records:
        die(f"duplicate external-mutation-record ID '{record_id}'")
    mutation_records[record_id] = fields

    runner = fields["runner"]
    if runner not in {"python", "bash", "powershell"}:
        die(f"external mutation {record_id}: invalid runner '{runner}'")
    target_kind = fields["target-kind"]
    if target_kind not in target_kinds:
        die(f"external mutation {record_id}: invalid target-kind '{target_kind}'")
    target_id = fields["target-id"]
    if not re.fullmatch(r"\S+", target_id):
        die(f"external mutation {record_id}: target-id must be one nonempty token")
    mutation_command = fields["mutation-command"]
    readback_command = fields["readback-command"]
    if re.search(r"\becho\b", mutation_command, re.IGNORECASE):
        die(f"external mutation {record_id}: mutation-command cannot use echo as evidence")
    effect = effective_mutation(mutation_command, runner)
    if effect is None:
        die(f"external mutation {record_id}: mutation-command is not an approved structural mutation")
    effective_action, effective_kind, effective_id = effect
    if effective_kind != target_kind or effective_id != target_id:
        die(
            f"external mutation {record_id}: mutation-command effective target "
            f"{effective_kind} '{effective_id}' does not match declared {target_kind} '{target_id}'"
        )
    mutation_effects[record_id] = effect
    if runner == "python" and "subprocess.run" not in mutation_command:
        die(f"external mutation {record_id}: python mutation-command must use subprocess.run")
    if fields["mutation-exit"] != "0":
        die(f"external mutation {record_id}: mutation-exit must be 0, got '{fields['mutation-exit']}'")
    if not fields["mutation-evidence"]:
        die(f"external mutation {record_id}: mutation-evidence must be nonempty")

    if mutation_command == readback_command:
        die(f"external mutation {record_id}: readback-command must be distinct from mutation-command")
    if re.search(r"\becho\b", readback_command, re.IGNORECASE):
        die(f"external mutation {record_id}: readback-command cannot use echo")
    if not approved_readback_query(readback_command, runner, target_kind, target_id):
        die(f"external mutation {record_id}: readback-command is not an approved read-only {target_kind} query")
    if fields["readback-exit"] != "0":
        die(f"external mutation {record_id}: readback-exit must be 0, got '{fields['readback-exit']}'")
    if not fields["readback-evidence"]:
        die(f"external mutation {record_id}: readback-evidence must be nonempty")
    if fields["readback-evidence"] == fields["mutation-evidence"]:
        die(f"external mutation {record_id}: readback-evidence must differ from mutation-evidence")

    witness_name = fields["readback-file"]
    if not re.fullmatch(r"[^/\\]+\.json", witness_name) or witness_name in {".", ".."}:
        die(f"external mutation {record_id}: readback-file must be a bare relative JSON basename, got '{witness_name}'")
    witness_path = os.path.abspath(os.path.join(record_dir, witness_name))
    try:
        contained = os.path.commonpath([record_dir, witness_path]) == record_dir
    except ValueError:
        contained = False
    if not contained:
        die(f"external mutation {record_id}: readback-file escapes the record directory")
    if os.path.islink(witness_path):
        die(f"external mutation {record_id}: readback-file '{witness_name}' must not be a symlink")
    if not os.path.isfile(witness_path):
        die(f"external mutation {record_id}: readback-file '{witness_name}' is not a regular file")
    canonical_witness = os.path.realpath(witness_path)
    try:
        canonical_contained = os.path.commonpath([record_dir, canonical_witness]) == record_dir
    except ValueError:
        canonical_contained = False
    if not canonical_contained:
        die(f"external mutation {record_id}: canonical readback-file escapes the record directory")

    expected_sha = fields["readback-sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        die(f"external mutation {record_id}: readback-sha256 must be 64 lowercase hex")
    try:
        with open(canonical_witness, "rb") as witness:
            witness_bytes = witness.read()
    except OSError:
        die(f"external mutation {record_id}: readback-file '{witness_name}' is not readable")
    actual_sha = hashlib.sha256(witness_bytes).hexdigest()
    if actual_sha != expected_sha:
        die(f"external mutation {record_id}: readback SHA-256 does not match {witness_name}")

    readback_field = fields["readback-field"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", readback_field):
        die(f"external mutation {record_id}: readback-field must name one top-level field")
    try:
        payload = json.loads(
            witness_bytes.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except DuplicateKey as error:
        die(f"external mutation {record_id}: readback JSON contains duplicate object key '{error.args[0]}'")
    except NonStandardConstant as error:
        die(f"external mutation {record_id}: readback JSON contains non-standard constant '{error.args[0]}'")
    except (UnicodeError, json.JSONDecodeError):
        die(f"external mutation {record_id}: readback-file is not valid UTF-8 JSON")
    if not isinstance(payload, dict):
        die(f"external mutation {record_id}: readback JSON must be a top-level object")
    if readback_field not in payload:
        die(f"external mutation {record_id}: readback JSON has no top-level field '{readback_field}'")
    parsed = scalar_text(payload[readback_field])
    if parsed is None:
        die(f"external mutation {record_id}: readback field '{readback_field}' must be scalar")
    observed = fields["observed-value"]
    expected = fields["expected-value"]
    if parsed != observed:
        die(f"external mutation {record_id}: parsed readback field '{readback_field}' value '{parsed}' does not match observed '{observed}'")
    if observed != expected:
        die(f"external mutation {record_id}: observed value '{observed}' does not match expected '{expected}'")


referenced_grants = set()
for claim_id in claim_order:
    fields = claims[claim_id]
    opted_in = any(key in fields for key in ("external-kind", "external-mutation", "external-mutation-record", "external-authorization-grant"))
    if not opted_in:
        continue
    explicit_mutation = fields.get("external-mutation") == "true"
    external_kind = fields.get("external-kind")
    if external_kind not in {"observation", "mutation"}:
        die(f"claim {claim_id}: verified external surface requires external-kind observation or mutation")
    if explicit_mutation and external_kind != "mutation":
        die(f"claim {claim_id}: external-mutation true requires external-kind mutation")
    if external_kind == "mutation":
        record_id = fields.get("external-mutation-record", "")
        if not record_id:
            die(f"claim {claim_id}: external mutation requires external-mutation-record")
        if record_id not in mutation_records:
            die(f"claim {claim_id}: external-mutation-record '{record_id}' does not resolve exactly once")
        grant_id = fields.get("external-authorization-grant", "")
        if not grant_id:
            die(f"claim {claim_id}: external mutation requires external-authorization-grant")
        if grant_id not in authorization_grants:
            die(f"claim {claim_id}: external-authorization-grant '{grant_id}' does not resolve exactly once")
        referenced_grants.add(grant_id)
        grant = authorization_grants[grant_id]
        action, target_kind, target_id = mutation_effects[record_id]
        if grant["action"] != action:
            die(
                f"authorization grant {grant_id}: action '{grant['action']}' "
                f"does not bind mutation action '{action}'"
            )
        if grant["target_kind"] != target_kind:
            die(
                f"authorization grant {grant_id}: target_kind '{grant['target_kind']}' "
                f"does not bind mutation target kind '{target_kind}'"
            )
        if grant["target_id"] != target_id:
            die(
                f"authorization grant {grant_id}: target_id '{grant['target_id']}' "
                f"does not bind mutation target '{target_id}'"
            )

unused_grants = sorted(set(authorization_grants) - referenced_grants)
if unused_grants:
    die(f"external authorization grant rows must be referenced by mutation claims; dangling={unused_grants}")


artifact_fields = ["sha256"]
artifacts = {}
for line in lines:
    if not line.startswith("artifact-identity:"):
        continue
    name, fields = parse_segments(line, "artifact-identity:", "artifact identity", artifact_fields)
    digest = fields["sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        die(f"artifact identity '{name}': sha256 must be 64 lowercase hex")
    artifacts.setdefault(name, []).append(digest)


receipt_fields = ["hashes", "reason"]
receipts = {}
for line in lines:
    if not line.startswith("collision-receipt:"):
        continue
    name, fields = parse_segments(line, "collision-receipt:", "collision receipt", receipt_fields)
    if name in receipts:
        die(f"duplicate collision-receipt for '{name}'")
    hashes = fields["hashes"].split(",") if fields["hashes"] else []
    if any(not re.fullmatch(r"[0-9a-f]{64}", item) for item in hashes):
        die(f"collision receipt '{name}': hashes must be comma-separated 64 lowercase hex values")
    if len(hashes) != len(set(hashes)):
        die(f"collision receipt '{name}' hash set does not exactly match observed hashes")
    if not fields["reason"]:
        die(f"collision receipt '{name}': reason must be nonempty")
    receipts[name] = set(hashes)


for name, hashes in artifacts.items():
    observed_hashes = set(hashes)
    if len(observed_hashes) > 1 and name not in receipts:
        die(f"artifact identity '{name}' has {len(observed_hashes)} distinct hashes but no collision receipt")
    if name in receipts and receipts[name] != observed_hashes:
        die(f"collision receipt '{name}' hash set does not exactly match observed hashes")
for name in receipts:
    if name not in artifacts or len(set(artifacts[name])) < 2:
        die(f"collision receipt '{name}' does not name an observed collision")


external_evidence_fields = [
    "bytes", "mtime", "liveness", "still-producing", "use",
    "closure-bytes", "closure-mtime",
]
evidence_ids = set()
for line in lines:
    if not line.startswith("external-evidence:"):
        continue
    evidence_id, fields = parse_segments(
        line, "external-evidence:", "external evidence", external_evidence_fields
    )
    if evidence_id in evidence_ids:
        die(f"duplicate external-evidence ID '{evidence_id}'")
    evidence_ids.add(evidence_id)
    if not re.fullmatch(r"[0-9]+", fields["bytes"]):
        die(f"external evidence {evidence_id}: bytes must be a nonnegative integer")
    if not valid_timestamp(fields["mtime"]):
        die(f"external evidence {evidence_id}: invalid mtime '{fields['mtime']}' (expected RFC3339 UTC whole-second timestamp)")
    if fields["liveness"] not in {"snapshot", "terminal"}:
        die(f"external evidence {evidence_id}: invalid liveness '{fields['liveness']}'")
    if fields["still-producing"] not in {"true", "false"}:
        die(f"external evidence {evidence_id}: still-producing must be true or false")
    if fields["use"] not in {"orientation", "terminal"}:
        die(f"external evidence {evidence_id}: use must be orientation or terminal")
    closure_bytes = fields["closure-bytes"]
    closure_mtime = fields["closure-mtime"]
    if closure_bytes != "none" and not re.fullmatch(r"[0-9]+", closure_bytes):
        die(f"external evidence {evidence_id}: closure-bytes must be a nonnegative integer or none")
    if closure_mtime != "none" and not valid_timestamp(closure_mtime):
        die(f"external evidence {evidence_id}: invalid closure-mtime '{closure_mtime}'")
    if fields["use"] == "terminal":
        if fields["liveness"] == "snapshot" and fields["still-producing"] == "true":
            die(f"external evidence {evidence_id}: still-producing snapshot cannot support terminal use")
        if closure_bytes == "none" or closure_mtime == "none":
            die(f"external evidence {evidence_id}: terminal use requires closure bytes and mtime")
        if closure_bytes != fields["bytes"] or closure_mtime != fields["mtime"]:
            die(f"external evidence {evidence_id}: closure re-stat does not match original bytes and mtime")


heading = "## Suggested Commit Message When No Commit Authorized"
heading_indexes = [index for index, line in enumerate(lines) if line == heading]
if len(heading_indexes) > 1:
    die("proposed commit message: duplicate canonical headings")
if heading_indexes:
    index = heading_indexes[0] + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines) or not re.fullmatch(r"```[A-Za-z0-9_-]*", lines[index]):
        die("proposed commit message: missing fenced block boundaries")
    index += 1
    block = []
    while index < len(lines) and lines[index] != "```":
        block.append(lines[index])
        index += 1
    if index >= len(lines):
        die("proposed commit message: missing fenced block boundaries")
    block_text = "\n".join(block)
    makes_claim = bool(re.search(r"[0-9]|\b(?:pass|fail|fixed|verified|closed|refuted|machine-checked)\b", block_text, re.IGNORECASE))
    anchors = []
    malformed_anchor = False
    for block_line in block:
        if "Evidence anchor:" not in block_line:
            continue
        match = re.fullmatch(r"Evidence anchor: claim:([A-Za-z0-9._-]+)", block_line)
        if match:
            anchors.append(match.group(1))
        else:
            malformed_anchor = True
    if malformed_anchor and not makes_claim:
        die("proposed commit message: exactly one well-formed Evidence anchor is allowed")
    if makes_claim and (malformed_anchor or len(anchors) != 1):
        die("proposed commit message: digit or verdict claim requires exactly one Evidence anchor: claim:<Claim-ID>")
    if anchors:
        if malformed_anchor or len(anchors) != 1:
            die("proposed commit message: exactly one well-formed Evidence anchor is allowed")
        claim_id = anchors[0]
        if claim_id not in claims:
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' is unresolved")
        claim = claims[claim_id]
        if claim.get("status") != "verified":
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' is not verified")
        if claim.get("evidence-surface") not in {"source", "generated-artifact", "package", "installed-payload", "running-local-service", "deployed-service", "api", "user-visible", "publication"}:
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' has no checkable evidence surface")
PY
)"; then
    [ -n "$schema_error" ] || schema_error="external-state schema validation failed without a diagnostic"
    fail "$schema_error"
  fi
fi

# #78 decision-time ledger. Absence means no decision was declared. When the
# sibling ledger exists, validate each append-only JSONL row strictly and
# refuse terminal closure while a row remains pending or unresolved.
deferrals_file="$(dirname "$file")/deferrals.jsonl"
if [ -e "$deferrals_file" ]; then
  [ -f "$deferrals_file" ] && [ ! -L "$deferrals_file" ] \
    || fail "deferrals ledger must be a regular non-symlink file: $deferrals_file"
  ensure_python
  deferral_error=""
  if ! deferral_error="$("${py_cmd[@]}" - "$deferrals_file" <<'PY'
import datetime as dt
import json
import sys

path = sys.argv[1]
keys = ["ts", "phase", "what", "why", "owner", "unblock", "disposition"]
allowed = {
    "pending", "unresolved", "deferred", "transferred", "owner-assigned",
    "risk-accepted", "validated-resolved",
}
owners = {"this-run", "executor", "owner", "other"}


def die(message):
    print(message)
    raise SystemExit(1)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            die(f"duplicate key '{key}'")
        result[key] = value
    return result


with open(path, "r", encoding="utf-8") as handle:
    for line_number, raw in enumerate(handle, 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(
                raw,
                object_pairs_hook=unique_object,
                parse_constant=lambda value: die(f"non-standard constant '{value}'"),
            )
        except (UnicodeError, json.JSONDecodeError) as error:
            die(f"row {line_number}: invalid UTF-8 JSON: {error}")
        if not isinstance(row, dict):
            die(f"row {line_number}: expected one JSON object")
        if list(row) != keys:
            die(f"row {line_number}: keys must use the canonical order")
        if not all(isinstance(row[key], str) and row[key].strip() for key in keys):
            die(f"row {line_number}: every field must be a nonempty string")
        if not row["phase"].isdigit():
            die(f"row {line_number}: phase must be a nonnegative integer string")
        try:
            dt.datetime.strptime(row["ts"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            die(f"row {line_number}: ts must be RFC3339 UTC whole seconds")
        if row["owner"] not in owners:
            die(f"row {line_number}: invalid owner '{row['owner']}'")
        disposition = row["disposition"]
        if disposition not in allowed:
            die(f"row {line_number}: invalid disposition '{disposition}'")
        if disposition == "risk-accepted" and not row["unblock"].startswith("policy:"):
            die(f"row {line_number}: risk-accepted requires a policy: reference")
        if disposition == "transferred" and row["owner"] == "this-run":
            die(f"row {line_number}: transferred disposition must name a receiving owner")
        if disposition in {"pending", "unresolved"}:
            die(f"row {line_number}: nonterminal disposition '{disposition}' blocks closure")
PY
)"; then
    [ -n "$deferral_error" ] || deferral_error="deferrals ledger validation failed without a diagnostic"
    fail "deferrals.jsonl: $deferral_error"
  fi
fi
if grep -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$file"; then
  fail "kill authority uses executable name, image, pattern, or broad host-process enumeration instead of process-started.json identity"
fi
if grep -E 'Get-Process([[:space:]]|$)' "$file" |
   grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then
  fail "kill authority uses broad Get-Process enumeration without -Id"
fi
if [ -n "$impact_set" ]; then
  checker="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-respec-impact-set.sh"
  bash "$checker" "$impact_set" >/dev/null \
    || fail "impact set is not terminal"
fi
if [ -n "$closure_evidence" ]; then
  [ -f "$closure_evidence" ] || fail "closure evidence not found: $closure_evidence"
  if grep -Eqi '(^|[|:[:space:]])(Pending\.|remains pending|IN PROGRESS|TBD)([|[:space:]]|$)' "$closure_evidence"; then
    fail "closure evidence retains a pending or in-progress marker: $closure_evidence"
  fi
fi

for plan in "${superseded_plans[@]}"; do
  [ -f "$plan" ] || fail "superseded plan not found: $plan"
  grep -Eq '^SUPERSEDED_BY: [^[:space:]].* — .+' "$plan" \
    || fail "superseded plan lacks SUPERSEDED_BY path and reason: $plan"
  bad_unchecked="$(grep -nE '^[[:space:]]*-[[:space:]]+\[[[:space:]]\]' "$plan" \
    | grep -Ev '\|[[:space:]]*RECONCILIATION:[[:space:]]*(STALE|TODO|BLOCKED)[[:space:]]*$' \
    | head -n 1 || true)"
  [ -z "$bad_unchecked" ] \
    || fail "superseded plan has unchecked item without reconciliation: $bad_unchecked"
done

if [ -n "$steer_dir" ]; then
  [ -d "$steer_dir" ] || fail "steer directory not found: $steer_dir"
  undeclared=0
  while IFS= read -r -d '' steer; do
    if ! grep -Eqi '^supersedes:[[:space:]]+[^[:space:]]' "$steer"; then
      undeclared=$((undeclared + 1))
    fi
  done < <(find "$steer_dir" -maxdepth 1 -type f \( -iname '*steer*.md' -o -iname '*advisory*.md' \) -print0)
  if [ "$undeclared" -gt 2 ]; then
    printf 'check-closure-surface: warning: %d steer/advisory artifacts lack declared precedence\n' "$undeclared" >&2
  fi
fi
printf 'check-closure-surface: ok (%d claim row(s))\n' "$rows"
