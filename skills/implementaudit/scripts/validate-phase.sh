#!/usr/bin/env bash
# validate-phase.sh — verify a phase spec has the required structure
#
# Usage: validate-phase.sh <path-to-phase-spec.md>
#
# Exits 0 if the spec has all required markers, sections, and non-placeholder content.
# Exits 1 with specific errors otherwise. Exits 2 for usage errors.

set -uo pipefail

if [ "${1:-}" = "--mutation-authority" ]; then
  phase_file="${2:-}"; shift 2 || true
  phase= step= repo_root= run_root=
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --phase) phase="${2:-}"; shift 2 ;;
      --step) step="${2:-}"; shift 2 ;;
      --repo-root) repo_root="${2:-}"; shift 2 ;;
      --run-root) run_root="${2:-}"; shift 2 ;;
      *) printf 'usage: validate-phase.sh --mutation-authority <phase-file> --step <N> --repo-root <repo-root> --run-root <run-root>\n' >&2; exit 2 ;;
    esac
  done
  case "$phase" in ''|*[!0-9]*) printf 'validate-phase: mutation authority phase must be a positive decimal\n' >&2; exit 1;; esac
  case "$step" in ''|*[!0-9]*) printf 'validate-phase: mutation authority step must be a positive decimal\n' >&2; exit 1;; esac
  [ "$phase" -gt 0 ] 2>/dev/null && [ "$step" -gt 0 ] 2>/dev/null || { printf 'validate-phase: mutation authority phase and step must be positive decimals\n' >&2; exit 1; }
  [ -n "$phase_file" ] && [ -n "$repo_root" ] && [ -n "$run_root" ] || { printf 'validate-phase: mutation authority requires phase, repo root and run root\n' >&2; exit 2; }
  bash "$0" "$phase_file" >/dev/null 2>&1 || { printf 'validate-phase: mutation authority requires an ordinary valid phase\n' >&2; exit 1; }
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else printf 'validate-phase: Python is required for mutation authority\n' >&2; exit 2; fi
  "${py[@]}" - "$phase_file" "$phase" "$step" "$repo_root" "$run_root" <<'PY'
import hashlib,json,os,re,stat,sys
from pathlib import Path
phase_file,phase_text,step_text,repo_text,run_text=sys.argv[1:]; phase_no=int(phase_text); step=int(step_text)
def die(s): print('validate-phase: mutation authority '+s,file=sys.stderr); raise SystemExit(1)
if any(part in ('.','..') for part in Path(phase_file).parts):
 die('phase path must be canonical without dot components')
repo=Path(os.path.abspath(repo_text)); run=Path(os.path.abspath(run_text)); phase=Path(os.path.abspath(phase_file))
try: run_rel=run.relative_to(repo).as_posix()
except ValueError: die('run root is outside supplied repository')
if phase != run/'phases'/f'phase-{phase_no}.md': die('phase path does not equal the run-root phase path')
for p in (phase, phase.parent, run):
 try:
  if stat.S_ISLNK(os.lstat(p).st_mode): die(f'custody path is a symlink: {p}')
 except OSError: die(f'custody path missing: {p}')
if not stat.S_ISREG(os.lstat(phase).st_mode): die('phase is not regular')
text=phase.read_text(encoding='utf-8')
def one(name):
 rows=re.findall(rf'(?m)^{re.escape(name)}:\s*(\S.*)$',text)
 if len(rows)!=1: die(f'expected exactly one {name}: field')
 return rows[0].strip()
pm=re.findall(r'(?m)^Phase:\s*([1-9][0-9]*)\b',text)
if len(pm)!=1 or int(pm[0])!=phase_no: die('Phase header does not equal requested phase')
if one('Run root')!=run_rel: die('Run root field does not equal supplied run root')
baseline=one('Baseline ref'); owner=one('Owner/source')
try: claim=(run/'.claimed').read_text(encoding='utf-8').splitlines()
except OSError: die('claim metadata is missing')
ids=[x.split('=',1)[1] for x in claim if x.startswith('claim_id=')]
if len(ids)!=1 or not re.fullmatch(r'[0-9a-f]{32}',ids[0]): die('claim metadata lacks one v2 claim_id')
roadmap=run/'ROADMAP.md'
if not roadmap.is_file() or len(re.findall(rf'(?m)^\|\s*{phase_no}\s*\|',roadmap.read_text(encoding='utf-8')))!=1: die('ROADMAP does not contain exactly one matching phase row')
def pathok(x):
 return isinstance(x,str) and bool(x) and not x.endswith('/') and not x.startswith('/') and '\\' not in x and not re.match(r'^[A-Za-z]:',x) and not any(ord(c)<32 for c in x) and all(y not in ('','.','..') for y in x.split('/'))
sm=re.search(r'(?ms)^##\s+Scope boundaries\b(.*?)(?=^##\s+|^---\s*$|\Z)',text)
if not sm: die('Scope boundaries section is missing')
rows=re.findall(r'(?m)^Mutation scope:\s*(\{[^\r\n]*\})\s*$',sm.group(1))
if len(rows)!=1: die('expected exactly one Mutation scope line')
def unique_pairs(pairs):
 d={}
 for k,v in pairs:
  if k in d: raise ValueError('duplicate JSON key')
  d[k]=v
 return d
try: scope=json.loads(rows[0],object_pairs_hook=unique_pairs)
except (json.JSONDecodeError,ValueError): die('Mutation scope is not unique-key JSON')
if list(scope)!=['in','out'] or not all(isinstance(scope.get(k),list) for k in ('in','out')): die('Mutation scope keys must be exactly in, out')
for k in ('in','out'):
 if not all(pathok(x) for x in scope[k]) or len(scope[k])!=len(set(scope[k])) or scope[k]!=sorted(scope[k],key=lambda x:x.encode()): die(f'Mutation scope {k} paths must be unique sorted literals')
steps=re.findall(r'(?m)^- Step\s+([1-9][0-9]*):',text)
if len(steps)!=len(set(steps)): die('Step numbers are not unique')
rows=re.findall(rf'(?m)^- Step\s+{step}:.*\n  mutation-authority:\s*(\{{[^\r\n]*\}})\s*$',text)
if len(rows)!=1: die('requested Step must carry exactly one immediate mutation-authority line')
try: auth=json.loads(rows[0],object_pairs_hook=unique_pairs)
except (json.JSONDecodeError,ValueError): die('mutation-authority is not unique-key JSON')
if list(auth)!=['operation','source','destination']: die('mutation-authority keys/order must be operation, source, destination')
op,source,dest=auth['operation'],auth['source'],auth['destination']
if op not in {'replace','patch','delete','move'} or not pathok(source): die('invalid operation or source')
if (op=='move' and (not pathok(dest) or dest==source)) or (op!='move' and dest is not None): die('invalid destination')
if source not in scope['in'] or source in scope['out'] or (dest is not None and (dest not in scope['in'] or dest in scope['out'])): die('authority paths are outside Mutation scope')
binding={'schema':'implementaudit.phase-mutation-authority-binding.v1','claim_id':ids[0],'run_root':run_rel,'phase':phase_no,'step':step,'owner_source':owner,'baseline_ref':baseline,'operation':op,'source':source,'destination':dest,'mutation_scope':scope}
digest=hashlib.sha256(json.dumps(binding,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
print(json.dumps({'schema':'implementaudit.phase-mutation-authority.v1','phase':phase_no,'step':step,'run_root':run_rel,'operation':op,'source':source,'destination':dest,'mutation_scope':scope,'authority_binding_sha256':digest},separators=(',',':'),ensure_ascii=False))
PY
  exit $?
fi

fail() {
  printf 'validate-phase: %s\n' "$*" >&2
  exit 1
}

phase_file="${1:-}"
[ -n "$phase_file" ] || { printf 'usage: validate-phase.sh <phase-file> | --explain\n' >&2; exit 2; }

if [ "$phase_file" = "--explain" ]; then
  cat <<'EXPLAIN'
validate-phase: a filled phase spec requires —
  markers: IMPLEMENTAUDIT_PHASE_START, IMPLEMENTAUDIT_PHASE_VERIFY,
           AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, IMPLEMENTAUDIT_PHASE_DONE
  header fields: Task, Type, Run root, Baseline ref, Owner/source,
                 Audit object, Depends on phases
  sections: ## Current state excerpts; ## Work;
            ## Acceptance criteria (>=1 non-placeholder `- [ ]` item);
            ## Mandatory commands (>=1 non-placeholder `- <command>` list item
            with expected success shape);
            ## Evidence required (>=1 non-placeholder `- <evidence>` item);
            ## Rollback / defer path; ## Maintenance notes
  reconstructibility (#50): vague step language always fails; newly authored
            specs carry ## Implementation steps (ordered, each step with
            target: exact file/symbol, verify: command, expected shape),
            ## Scope boundaries with Out of scope:, and plan-specific
            ## STOP conditions; specs without ordered steps pass as legacy
            with a warning
  unit sizing (#83): new specs with 3+ `- Unit N:` items carry
            `unit_independence` and approved `change_class`; legacy specs warn
  lossless capture (#74): newly authored mandatory-command rows carry
            `coverage: full`, a matching whole-output `capture:` path, and no
            live tail/head pipeline; historical rows pass with a warning
  census discipline (#79): `claim:` evidence rows using completeness
            language carry full-capture plus population/count/enumerator
            metadata; honest samples stay partial-corpus claims
  sidecar status: literal `Markdown fallback:` field (any value)
Canonical filled examples (source repo only): fixtures/run-root-example/phases/phase-1.md (brownfield)
and (source repo only) fixtures/phase-design/dmadv-greenfield-phase.md (greenfield);
the blank skeleton ships as templates/phase-goal.txt.
EXPLAIN
  exit 0
fi

[ -f "$phase_file" ] || fail "phase file not found: $phase_file"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

errors=0

err() {
  printf 'validate-phase: ERROR: %s\n' "$*" >&2
  errors=$((errors + 1))
}

# ---------------------------------------------------------------------------
# Marker checks (required transcript anchors)
# ---------------------------------------------------------------------------
for marker in \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  CONTINUITY_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE
do
  grep -q "$marker" "$phase_file" || err "missing marker: $marker"
done

# ---------------------------------------------------------------------------
# Inline field checks (must appear in the IMPLEMENTAUDIT_PHASE_START block)
# ---------------------------------------------------------------------------
for field in \
  "Run root:" \
  "Baseline ref:" \
  "Owner/source:" \
  "Task:" \
  "Type:"
do
  grep -qi "^${field}" "$phase_file" || err "missing field: $field"
done

# Depends on phases must be present (even if value is "none")
grep -qi "^Depends on phases:" "$phase_file" || err "missing field: Depends on phases"

# ---------------------------------------------------------------------------
# Section checks (## headings)
# ---------------------------------------------------------------------------
for section in \
  "Work" \
  "Current state excerpts" \
  "Acceptance criteria" \
  "Mandatory commands" \
  "Evidence required" \
  "Rollback" \
  "Maintenance notes"
do
  grep -qi "^## .*${section}" "$phase_file" || err "missing section: ## ${section}"
done

# Rollback / defer path section
grep -qi "^## Rollback" "$phase_file" || err "missing section: ## Rollback / defer path"

# Graphify / ActiveGraph / Markdown fallback status
grep -qi "Markdown fallback:" "$phase_file" || err "missing literal field \`Markdown fallback:\` (any value) - see the sidecar status block in templates/phase-goal.txt"

# ---------------------------------------------------------------------------
# Python checks: non-placeholder content validation
# ---------------------------------------------------------------------------
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  py_cmd=()
fi

PLACEHOLDER_TERMS='{{|tbd|todo|n/a|placeholder|criterion 1|criterion 2|work bullet|command 1|evidence 1|why one sentence|one line task'

if [ "${#py_cmd[@]}" -gt 0 ]; then
  python_errors=0

  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")

def die(message):
    sys.stderr.write("validate-phase: " + message + "\n")
    raise SystemExit(1)

def field(name):
    found = re.findall(rf"(?mi)^{re.escape(name)}:\s*(\S.*)$", text)
    if len(found) > 1:
        die(f"duplicate field: {name}")
    return found[0].strip() if found else None

def section(name):
    found = re.search(
        rf"(?ms)^##\s+{name}\b(.*?)(?=^##\s+|^---\s*$|\Z)", text)
    return found.group(1) if found else ""

independence = field("unit_independence")
change_class = field("change_class")
new_format = bool(re.search(r"(?mi)^##\s+Implementation steps", text))

unit_count = len(re.findall(
    r"(?mi)^\s*-\s+Unit\s+\d+\s*:", section("Work")))

if bool(independence) != bool(change_class):
    die("unit_independence and change_class must be declared together")

if unit_count >= 3 and not independence:
    if new_format:
        die("3+ declared units require unit_independence and change_class")
    sys.stderr.write(
        "validate-phase: WARNING legacy spec — 3+ unit declarations lack "
        "unit_independence and change_class; newly authored specs require both\n")
    raise SystemExit(0)

if not independence:
    raise SystemExit(0)

if not (independence == "independent"
        or re.fullmatch(r"ordered\([^()\r\n]+\)", independence)):
    die("unit_independence must be independent or ordered(<reason>)")

approved = set("reversible-local reversible-local-multi reversible-deployed "
               "irreversible-local irreversible-external unknown".split())
if change_class not in approved:
    die("invalid change_class")

external_command = re.compile(
    r"(?i)\b(publish|release|deploy|docker\s+push|kubectl\s+apply|terraform\s+apply)\b")
if change_class in {"reversible-local", "reversible-local-multi"} \
        and external_command.search(section("Mandatory commands")):
    die("reversible-local cannot authorize external mutation commands")

if change_class in {"irreversible-external", "unknown"} and re.search(
        r"(?i)\b(per\s+batch|one\s+review\s+per\s+batch|amortiz\w*)\b", text):
    die("irreversible-external keeps full ceremony per unit")
PY

  # Check: acceptance criteria section has at least 1 non-placeholder item
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|criterion [0-9]|work bullet|"
    r"command [0-9]|evidence [0-9]|why one sentence|one.?line.?task",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_ac = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Acceptance criteria", stripped, re.IGNORECASE):
        in_ac = True
        continue
    if in_ac and re.match(r"^##\s+", stripped):
        break
    if not in_ac:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Acceptance criteria needs at least one non-placeholder `- [ ] criterion` list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Acceptance criteria needs at least one non-placeholder list item (- [ ] ...)"
  python_errors=0

  # Check: mandatory commands section has at least 1 non-placeholder item and
  # each command item states an expected success shape.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|command [0-9]",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
SHARED_FIELD_NAMES = {
    "claim", "coverage", "capture", "range", "omission",
    "population_definition", "population_size", "examined_count",
    "enumeration_source",
}


def die(message):
    sys.stderr.write("validate-phase: " + message + "\n")
    raise SystemExit(1)


def section_items(name):
    result = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if re.match(rf"^##\s+{name}\b", stripped, re.I):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+|^---\s*$", stripped):
            break
        if in_section and stripped.startswith("-"):
            result.append(stripped[1:].strip())
        elif in_section and result and line[:1].isspace() and stripped:
            result[-1] += " " + stripped
    return result


def shared_fields(item):
    """Parse the #74/#79 evidence-row fields once and reject near misses."""
    result = {}
    for raw_segment in item.split(";"):
        segment = raw_segment.strip()
        match = re.match(
            r"^([A-Za-z][A-Za-z0-9_ -]*?)\s*([:=])\s*(.*)$", segment)
        if not match:
            continue
        raw_name, separator, raw_value = match.groups()
        normalized = re.sub(r"[-\s]+", "_", raw_name.casefold())
        if normalized not in SHARED_FIELD_NAMES:
            continue
        raw_prefix = segment[:match.start(2)]
        if separator != ":" or raw_prefix != raw_prefix.rstrip() or \
                raw_name.casefold() != normalized:
            die(f"malformed evidence field `{raw_name}{separator}`; "
                f"use `{normalized}: <value>`")
        if normalized in result:
            die(f"duplicate evidence field `{normalized}:` in row: {item}")
        result[normalized] = raw_value.strip()
    return result


def usable(raw):
    return bool(raw) and not raw.startswith("{{") and raw.casefold() not in {
        "tbd", "todo", "n/a", "placeholder"}


def require_coverage_shape(item, fields):
    coverage = fields.get("coverage", "").casefold()
    if coverage and coverage not in {"full", "partial"}:
        die("invalid coverage tag (allowed: full / partial): " + item)
    if coverage == "partial":
        missing = [name for name in ("range", "omission")
                   if not usable(fields.get(name, ""))]
        if missing:
            die("`coverage: partial` requires explicit `range:` and "
                "`omission:`: " + item)
    if coverage == "full" and re.search(
            r"warning:\s*truncated output", item, re.I):
        die("truncation marker contradicts `coverage: full`: " + item)

missing_expected = []
items = [item for item in section_items("Mandatory commands")
         if item and not PLACEHOLDER.search(item)]
for item in items:
    if not re.search(
            r"\b(expected|expects|exit 0|passes|pass|no errors|outputs?|"
            r"last ~?10 lines)\b", item, re.I):
        missing_expected.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Mandatory commands needs at least one non-placeholder `- <command>` list item (bare lines are not counted)\n")
    raise SystemExit(1)
if missing_expected:
    sys.stderr.write(
        "validate-phase: ## Mandatory commands items must include expected success shape; missing: "
        + "; ".join(missing_expected[:3])
        + "\n"
    )
    raise SystemExit(1)

# Evidence property tags (#3): every command declares which property class
# it exercises (structural / behavioral / provenance). Newly authored specs
# (any tagged item present) REQUIRE tags on every item; a fully untagged
# spec is treated as legacy and warned, not failed. Authorization is not an
# evidence property and is not accepted as one.
TAG = re.compile(r"property:\s*(structural|behavioral|provenance)\b",
                 re.IGNORECASE)
# \b-anchored: a PREFIX of a valid class ("structurally", "behavioralish")
# is an invalid tag, not an untagged/legacy item (Fable review of PR #25).
BAD_TAG = re.compile(r"property:\s*(?!(?:structural|behavioral|provenance)\b)\w+",
                     re.IGNORECASE)
tagged = [i for i in items if TAG.search(i)]
badly = [i for i in items if BAD_TAG.search(i)]
if badly:
    sys.stderr.write(
        "validate-phase: invalid evidence property tag (allowed: "
        "structural / behavioral / provenance; authorization is a separate "
        "gate, not a property): " + "; ".join(badly[:3]) + "\n")
    raise SystemExit(1)
if tagged and len(tagged) != len(items):
    untagged = [i for i in items if not TAG.search(i)]
    sys.stderr.write(
        "validate-phase: ## Mandatory commands mixes tagged and untagged "
        "items — every command in a newly authored spec declares "
        "`property: structural|behavioral|provenance`; untagged: "
        + "; ".join(untagged[:3]) + "\n")
    raise SystemExit(1)
# A property tag without a scope is the mis-scoped-validator hazard the
# tag exists to prevent: the class says WHAT KIND of evidence, the scope
# says what the check actually tests (and implicitly what it does not).
noscope = [i for i in tagged
           if not re.search(r"scope:\s*\S", i, re.IGNORECASE)]
if noscope:
    sys.stderr.write(
        "validate-phase: property-tagged command lacks `scope:` (the "
        "plain-language statement of what this check actually tests): "
        + "; ".join(noscope[:3]) + "\n")
    raise SystemExit(1)
if not tagged:
    sys.stderr.write(
        "validate-phase: WARNING legacy spec — mandatory commands carry no "
        "`property:` evidence tags (structural / behavioral / provenance); "
        "newly authored specs must tag every command\n")

# Lossless verification capture (#74). Parse mandatory-command rows with the
# same field grammar used below for claim-capable evidence rows.
mandatory_rows = [(item, shared_fields(item)) for item in items]
covered = [(item, fields) for item, fields in mandatory_rows
           if "coverage" in fields]
for item, fields in mandatory_rows:
    require_coverage_shape(item, fields)
if covered and len(covered) != len(mandatory_rows):
    missing = [item for item, fields in mandatory_rows
               if "coverage" not in fields]
    sys.stderr.write(
        "validate-phase: ## Mandatory commands mixes coverage-tagged and "
        "untagged items — every newly authored row declares "
        "`coverage: full|partial`; untagged: "
        + "; ".join(missing[:3]) + "\n")
    raise SystemExit(1)
if not covered:
    sys.stderr.write(
        "validate-phase: WARNING legacy coverage bank — mandatory commands "
        "carry no `coverage: full|partial`; newly authored rows declare "
        "coverage and a capture file\n")

WHOLE_CAPTURE = re.compile(
    r"(?<!\S)(?P<operator>1?>|&>)[ \t]*"
    r"(?!&[0-9])(?P<target>[^;\s]+)",
    re.IGNORECASE,
)
TEE_CAPTURE = re.compile(
    r"(?<!\S)tee[ \t]+(?P<target>[^;|\s]+)", re.IGNORECASE)
PIPELINE = re.compile(r"(?<!\|)\|(?!\|)")
WINDOW_EXCERPT = re.compile(
    r"\|\s*(?:tail|head)\b|\|\s*Select-Object\b|"
    r"(?:^|[;&]\s*)(?:tail|head)\b|(?:^|\s)-Tail\s+\d+\b|"
    r"Select-Object\s+-Last\b",
    re.IGNORECASE,
)
PIPEFAIL = re.compile(r"set\s+-[a-z]*o\s+pipefail", re.IGNORECASE)


def preserved_pipestatus(command, last_pipe_end):
    """Require PIPESTATUS[0] to be the first post-pipeline command and exit."""
    tail = command[last_pipe_end:]
    separator = tail.find(";")
    if separator < 0:
        return False
    suffix = tail[separator + 1:].lstrip()
    if re.match(
            r"exit\s+[\"']?\$\{PIPESTATUS\[0\]\}[\"']?(?:\s|;|$)",
            suffix):
        return True
    assignment = re.match(
        r"([A-Za-z_]\w*)\s*=\s*\$\{PIPESTATUS\[0\]\}\s*;", suffix)
    if not assignment:
        return False
    variable = re.escape(assignment.group(1))
    return bool(re.match(
        rf"\s*exit\s+[\"']?\$\{{?{variable}\}}?[\"']?(?:\s|;|$)",
        suffix[assignment.end():]))


def captures_all_streams(match, command):
    if match.re is WHOLE_CAPTURE:
        if match.group("operator") == "&>":
            return True
        return bool(re.match(
            r"\s+2>&1(?=\s|;|\||$)", command[match.end():]))
    prefix = command[:match.start()]
    return bool(re.search(r"2>&1\s*\|\s*$", prefix))


def has_one_verification_producer(command):
    working = command.strip()
    setup = re.match(
        r"^set\s+-[a-z]*o\s+pipefail\s*;\s*", working, re.I)
    if setup:
        working = working[setup.end():]

    direct_status = re.search(
        r";\s*exit\s+[\"']?\$\{PIPESTATUS\[0\]\}[\"']?\s*$",
        working)
    if direct_status:
        working = working[:direct_status.start()]
    else:
        assigned_status = re.search(
            r";\s*([A-Za-z_]\w*)\s*=\s*\$\{PIPESTATUS\[0\]\}\s*;"
            r"\s*exit\s+[\"']?\$\{?([A-Za-z_]\w*)\}?[\"']?\s*$",
            working)
        if assigned_status and assigned_status.group(1) == assigned_status.group(2):
            working = working[:assigned_status.start()]

    background = re.search(r"(?<![>&])&(?![>&])", working)
    return not background and all(
        token not in working for token in (";", "&&", "||"))


for item, fields in covered:
    value = fields["coverage"].casefold()
    command = item.split(" — ", 1)[0]
    capture_value = fields.get("capture", "")
    if not usable(capture_value):
        sys.stderr.write(
            "validate-phase: coverage-tagged mandatory command lacks a "
            "concrete `capture:` file: " + item + "\n")
        raise SystemExit(1)
    if re.search(r"(?<!\S)\*>[ \t]*\S+", command):
        sys.stderr.write(
            "validate-phase: PowerShell `*>` requires explicit shell context; "
            "use the cross-shell `> capture 2>&1` form in phase rows: "
            + item + "\n")
        raise SystemExit(1)
    capture_matches = list(WHOLE_CAPTURE.finditer(command))
    capture_matches.extend(TEE_CAPTURE.finditer(command))
    targets = [match.group("target").strip("'\"")
               for match in capture_matches]
    if capture_value.strip("'\"") not in targets:
        sys.stderr.write(
            "validate-phase: `coverage: full` requires whole capture; add "
            "whole-output capture redirection to the declared `capture:` "
            "file: " + item + "\n")
        raise SystemExit(1)
    pipes = list(PIPELINE.finditer(command))
    window = WINDOW_EXCERPT.search(command)
    if window and pipes:
        matching_capture_before_window = any(
            match.group("target").strip("'\"") ==
            capture_value.strip("'\"") and match.start() < window.start()
            for match in capture_matches)
        if not matching_capture_before_window:
            sys.stderr.write(
                "validate-phase: whole capture must write the declared file "
                "before the truncating stage: " + item + "\n")
            raise SystemExit(1)
    whole_capture_matches = [
        match for match in capture_matches
        if match.group("target").strip("'\"") ==
        capture_value.strip("'\"") and captures_all_streams(match, command)]
    if not whole_capture_matches:
        sys.stderr.write(
            "validate-phase: whole capture must preserve both stdout and "
            "stderr in the declared file: " + item + "\n")
        raise SystemExit(1)
    if pipes:
        pipefail = PIPEFAIL.search(command[:pipes[0].start()])
        if not pipefail and not preserved_pipestatus(command, pipes[-1].end()):
            sys.stderr.write(
                "validate-phase: preserve producer exit authority: enable "
                "`set -o pipefail` before the first pipe or immediately "
                "preserve `${PIPESTATUS[0]}` as the exit verdict: "
                + item + "\n")
            raise SystemExit(1)
    if not has_one_verification_producer(command):
        sys.stderr.write(
            "validate-phase: a coverage-full row permits one verification "
            "producer, optional leading pipefail setup, and immediate "
            "PIPESTATUS exit propagation only: " + item + "\n")
        raise SystemExit(1)
    if window and not pipes:
        sys.stderr.write(
            "validate-phase: mandatory command captures only a tail/head "
            "window instead of whole output: " + item + "\n")
        raise SystemExit(1)
    if value == "partial":
        sys.stderr.write(
            "validate-phase: mandatory commands require `coverage: full`; "
            "partial capture is diagnostic only: " + item + "\n")
        raise SystemExit(1)

# Census discipline (#79) shares the parser and coverage diagnostics above.
# A complete claim needs both a faithful capture and a reconciled mechanical
# denominator. An honest M-of-N sample may carry the same full field group
# without being promoted to a whole-population claim.
CENSUS_FIELDS = (
    "population_definition", "population_size", "examined_count",
    "enumeration_source",
)
CENSUS_WORD = re.compile(
    r"\b(?:all|every|complete|no\s+remaining|none\s+remaining)\b", re.I)
N_OF_N = re.compile(r"\b(\d+)\s+of\s+\1\b|\b(\d+)\s*/\s*\2\b", re.I)
MECHANICAL = re.compile(
    r"^(?:git\s+(?:ls-tree|ls-files)\b|"
    r"rg\s+--files\b|find\b|fd\b|os\.walk\s*\(|"
    r"(?:pathlib\.)?path\s*\(.+\)\.(?:glob|rglob)\s*\(|"
    r"glob(?:\.glob)?\s*\(|gh\s+\S+\s+list\b|get-childitem\b)", re.I)
TRUNCATING_ENUMERATOR = re.compile(
    r"(?<!\|)\|(?!\|)|(?:^|\s)-Tail\s+\d+\b|"
    r"Select-Object\s+-Last\b",
    re.I,
)
NATIVE_ENUMERATOR_LIMIT = re.compile(
    r"(?:^|\s)(?:--max-results|--max-count|-m)(?:=|\s)|"
    r"(?:^|\s)-quit(?:\s|$)",
    re.I,
)


def explicit_members(source):
    match = re.fullmatch(
        r"explicit[- ]list\s*(?:\((.*)\)|\[(.*)\]|:\s*(.+))", source,
        re.I)
    if not match:
        return None
    payload = next(group for group in match.groups() if group is not None)
    members = [member.strip() for member in payload.split(",")]
    if not members or any(not member for member in members):
        die("census explicit list contains an empty member")
    if len(members) != len(set(members)):
        die("census explicit list contains duplicate members")
    return members

for item in section_items("Evidence required"):
    fields = shared_fields(item)
    require_coverage_shape(item, fields)
    claim = fields.get("claim", "")
    census_claim = bool(claim and (
        CENSUS_WORD.search(claim) or N_OF_N.search(claim)))
    census_present = [name for name in CENSUS_FIELDS if name in fields]

    if census_present and len(census_present) != len(CENSUS_FIELDS):
        missing = [name for name in CENSUS_FIELDS if not usable(
            fields.get(name, ""))]
        die("census field group is incomplete; missing: " + ", ".join(missing))

    if census_claim and not census_present:
        die("census claim requires non-placeholder `population_definition:`, "
            "`population_size:`, `examined_count:`, and "
            "`enumeration_source:` on the same evidence row")

    if not census_present:
        continue

    missing = [name for name in CENSUS_FIELDS
               if not usable(fields.get(name, ""))]
    if missing:
        die("census field group is incomplete; missing: " + ", ".join(missing))

    coverage = fields.get("coverage", "").casefold()
    if not usable(fields.get("capture", "")) or not coverage:
        if census_claim:
            die("census claim requires `coverage: full` and a concrete "
                "`capture:`")
        die("census field group requires `coverage: full|partial` and a "
            "concrete `capture:`")
    if census_claim and coverage != "full":
        die("census claim requires `coverage: full`; partial capture cannot "
            "establish a complete denominator")

    if not fields["population_size"].isdigit() or \
            not fields["examined_count"].isdigit():
        die("census `population_size:` and `examined_count:` must be integers")
    population_size = int(fields["population_size"])
    examined_count = int(fields["examined_count"])
    if population_size < 1 or examined_count < 0:
        die("census counts must use population_size >= 1 and "
            "examined_count >= 0")
    if examined_count > population_size:
        die("census claim is invalid when examined_count > population_size")
    if census_claim and examined_count < population_size:
        die("census claim is invalid when examined_count < population_size; "
            "rewrite it as an honest M-of-N claim")

    source = fields["enumeration_source"].strip()
    if source.casefold().startswith("command(") and source.endswith(")"):
        source = source[len("command("):-1].strip()
    if source.startswith("`") and source.endswith("`"):
        source = source[1:-1].strip()
    if TRUNCATING_ENUMERATOR.search(source):
        die("census enumeration_source cannot truncate or pipe the enumerated set")
    if NATIVE_ENUMERATOR_LIMIT.search(source):
        die("census enumeration_source contains a native result limit")
    if re.match(r"^gh\s+\S+\s+list\b", source, re.I):
        limit = re.search(r"(?:^|\s)--limit(?:=|\s+)(\d+)\b", source, re.I)
        if not limit:
            die("gh list census requires an explicit --limit above the "
                "declared population")
        if int(limit.group(1)) <= population_size:
            die("gh list --limit must be strictly greater than population_size")
    members = explicit_members(source)
    if members is not None and len(members) != population_size:
        die("census enumerated member count does not match population_size")
    if members is None and not MECHANICAL.search(source):
        die("census `enumeration_source:` must name a mechanical command or "
            "explicit list")

ACCEPTANCE = re.compile(r"acceptance:\s*(free-text|non-textual)\b",
                        re.I)
BAD_ACCEPTANCE = re.compile(
    r"acceptance:\s*(?!(?:free-text|non-textual)\b)\S+", re.I)
behavioral = [i for i in tagged
              if TAG.search(i).group(1).casefold() == "behavioral"]
bad_acceptance = [i for i in behavioral if BAD_ACCEPTANCE.search(i)]
if bad_acceptance:
    sys.stderr.write(
        "validate-phase: bad `acceptance:`: "
        + "; ".join(bad_acceptance[:3]) + "\n")
    raise SystemExit(1)
declared_acceptance = [i for i in behavioral if ACCEPTANCE.search(i)]
if declared_acceptance and len(declared_acceptance) != len(behavioral):
    missing = [i for i in behavioral if not ACCEPTANCE.search(i)]
    sys.stderr.write(
        "validate-phase: missing `acceptance:`: "
        + "; ".join(missing[:3]) + "\n")
    raise SystemExit(1)
if behavioral and not declared_acceptance:
    sys.stderr.write(
        "validate-phase: WARNING legacy acceptance bank\n")

free_text = [i for i in declared_acceptance
             if ACCEPTANCE.search(i).group(1).casefold() == "free-text"]
required_control_fields = (
    "paraphrase_control",
    "inversion_control",
    "forbidden_instruction_phrases",
)
for field in required_control_fields:
    missing = []
    for item in free_text:
        match = re.search(
            rf"(?:^|;\s*){field}:\s*([^;]*)", item, re.I)
        value = match.group(1).strip() if match else ""
        if not value or value.startswith("{{") or value.casefold() in {
                "tbd", "todo", "n/a", "placeholder"}:
            missing.append(item)
    if missing:
        sys.stderr.write(
            f"validate-phase: missing `{field}:`: "
            + "; ".join(missing[:3]) + "\n")
        raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Mandatory commands needs non-placeholder list items with expected success shape"
  python_errors=0

  # Check (#50): executor reconstructibility — vague language always fails;
  # ordered implementation steps with per-step verification, scope boundaries,
  # and plan-specific STOP conditions are required on newly authored specs;
  # specs without an Implementation steps section pass as legacy with warning.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()

VAGUE = re.compile(
    r"update the relevant files?|make it work|fix things|as needed\b|"
    r"handle (it )?appropriately|the relevant modules?\b",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|step [0-9]+ title|stop_condition",
    re.IGNORECASE,
)

def section_items(heading_re):
    items, in_s = [], False
    for line in lines:
        s = line.strip()
        if re.match(heading_re, s, re.IGNORECASE):
            in_s = True
            continue
        if in_s and re.match(r"^##\s+|^---\s*$", s):
            break
        if not in_s:
            continue
        if s.startswith("-"):
            items.append(s[1:].strip())
        elif s and items:
            items[-1] += " " + s
    return [i for i in items if i]

work_items = section_items(r"^##\s+Work\b")
step_items_raw = section_items(r"^##\s+Implementation steps")
vague_hits = [i for i in work_items + step_items_raw if VAGUE.search(i)]
if vague_hits:
    sys.stderr.write(
        "validate-phase: vague step language is not executable by a fresh "
        "executor; name exact files/symbols and the precise change: "
        + "; ".join(vague_hits[:3]) + "\n")
    raise SystemExit(1)

if not re.search(r"(?mi)^##\s+Implementation steps", text):
    sys.stderr.write(
        "validate-phase: WARNING legacy spec — no ordered `## Implementation "
        "steps` section; newly authored specs carry ordered steps with "
        "per-step verification (see templates/phase-goal.txt)\n")
    raise SystemExit(0)

steps = [i for i in step_items_raw if not PLACEHOLDER.search(i)]
if not steps:
    sys.stderr.write(
        "validate-phase: ## Implementation steps needs at least one "
        "non-placeholder step item\n")
    raise SystemExit(1)

PATHISH = re.compile(r"[\w-]+[./][\w./\\-]+")
bad_target = [s for s in steps
              if not (re.search(r"target:\s*\S", s, re.IGNORECASE)
                      and PATHISH.search(s))]
if bad_target:
    sys.stderr.write(
        "validate-phase: each implementation step names its exact target "
        "(file path, plus symbol when symbol precision is material): "
        + "; ".join(bad_target[:3]) + "\n")
    raise SystemExit(1)

EXPECTED = re.compile(
    r"\b(expected|expects|exit 0|passes|pass|no errors|outputs?)\b",
    re.IGNORECASE,
)
no_verify = [s for s in steps
             if not (re.search(r"verify:\s*\S", s, re.IGNORECASE)
                     and EXPECTED.search(s))]
if no_verify:
    sys.stderr.write(
        "validate-phase: each implementation step carries its own verify: "
        "command with expected success shape — commands only at the end of "
        "the phase do not reconstruct multi-step work: "
        + "; ".join(no_verify[:3]) + "\n")
    raise SystemExit(1)

if (not re.search(r"(?mi)^##\s+Scope boundaries", text)
        or not re.search(r"(?mi)^Out of scope:", text)):
    sys.stderr.write(
        "validate-phase: new-format spec requires ## Scope boundaries with "
        "an `Out of scope:` line\n")
    raise SystemExit(1)

stop_items = [i for i in section_items(r"^##\s+STOP conditions")
              if not PLACEHOLDER.search(i)]
if not stop_items:
    sys.stderr.write(
        "validate-phase: new-format spec requires ## STOP conditions with at "
        "least one non-placeholder item\n")
    raise SystemExit(1)
GENERIC_STOP = re.compile(
    r"^(stop )?(if )?(something|anything) (goes wrong|fails|breaks)\.?$"
    r"|^(stop )?(if )?(an )?unexpected errors? occurs?\.?$"
    r"|^stop (if|when) (there is|you see) (a problem|an error)\.?$",
    re.IGNORECASE,
)
ANCHORED = re.compile(r"`[^`]+`|[\w-]+[./][\w./\\-]+")
if (all(GENERIC_STOP.match(i) for i in stop_items)
        or not any(ANCHORED.search(i) for i in stop_items)):
    sys.stderr.write(
        "validate-phase: boilerplate STOP conditions do not reflect this "
        "phase's actual risks; tie at least one STOP to a concrete file, "
        "command, marker, or assumption of this phase\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "reconstructibility checks failed: ordered steps / scope boundaries / plan-specific STOP conditions (see --explain)"
  python_errors=0

  # Check: current-state excerpts section has at least one non-placeholder item.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|current state",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_section = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Current state excerpts", stripped, re.IGNORECASE):
        in_section = True
        continue
    if in_section and re.match(r"^##\s+", stripped):
        break
    if not in_section:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Current state excerpts needs at least one non-placeholder list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Current state excerpts needs at least one non-placeholder list item"
  python_errors=0

  # Check: evidence required section has at least 1 non-placeholder item
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|evidence [0-9]",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_ev = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Evidence required", stripped, re.IGNORECASE):
        in_ev = True
        continue
    if in_ev and re.match(r"^##\s+", stripped):
        break
    if not in_ev:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Evidence required needs at least one non-placeholder `- <evidence>` list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Evidence required needs at least one non-placeholder list item (- <evidence>)"
  python_errors=0

  # Check: maintenance notes section has at least one non-placeholder item.
  "${py_cmd[@]}" - "$phase_file" <<'PY' || python_errors=$((python_errors + 1))
import re, sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"^\{\{|^tbd$|^todo$|^n/a$|^placeholder$|maintenance note",
    re.IGNORECASE,
)

lines = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
items = []
in_section = False
for line in lines:
    stripped = line.strip()
    if re.match(r"^##\s+Maintenance notes", stripped, re.IGNORECASE):
        in_section = True
        continue
    if in_section and re.match(r"^---\s*$|^##\s+", stripped):
        break
    if not in_section:
        continue
    if stripped.startswith("-"):
        item = stripped[1:].strip()
        if item and not PLACEHOLDER.search(item):
            items.append(item)

if not items:
    sys.stderr.write("validate-phase: ## Maintenance notes needs at least one non-placeholder list item\n")
    raise SystemExit(1)
PY
  [ "$python_errors" -eq 0 ] || err "## Maintenance notes needs at least one non-placeholder list item"
fi

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
if (( errors > 0 )); then
  printf 'validate-phase: %d error(s); see templates/phase-goal.txt in the skill directory for the canonical filled shape\n' "$errors" >&2
  exit 1
fi

budget="$(sed -nE 's/^Scarce resource budget:[[:space:]]*(.*[^[:space:]])?[[:space:]]*$/\1/p' "$phase_file")"
if [ -n "$budget" ] && [ "$budget" != "none" ]; then
  phase_field() {
    local name="$1" values
    values="$(sed -nE "s/^${name}:[[:space:]]*(.*[^[:space:]])?[[:space:]]*$/\\1/p" "$phase_file")"
    [ "$(printf '%s\n' "$values" | sed '/^$/d' | wc -l)" -eq 1 ] || fail "non-none budget requires one ${name}"
    values="$(printf '%s\n' "$values" | sed '/^$/d')"
    [ "$values" != "none" ] || fail "non-none scarce budget requires ${name}"
    printf '%s\n' "$values"
  }
  rehearsal="$(phase_field 'Rehearsal receipt')"
  launch="$(phase_field 'Rehearsal launch')"
  producer_stub="$(phase_field 'Rehearsal producer stub')"
  for field in 'Rehearsal command hash' 'Rehearsal terminal artifact' 'Rehearsal environment keys'; do phase_field "$field" >/dev/null; done
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$producer_stub" \
    "$script_dir/check-authorization-binding.sh" --phase "$phase_file" --rehearsal "$rehearsal" --launch "$launch" ||
    fail "rehearsal failed; repair manually and re-run"
fi

printf 'validate-phase: ok\n'
