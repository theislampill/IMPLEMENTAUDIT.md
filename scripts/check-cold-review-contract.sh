#!/usr/bin/env bash
set -euo pipefail

# Independent cold-review gate (#51, IA-ACTION-COLD-REVIEW). Every handoff
# or executor-ready phase artifact passes an independent cold review —
# fresh-context reviewer, separate child agent preferred, bounded serial
# fresh-context fallback — recording PASS / GAP-REVISE / BLOCKED /
# OWNER DECISION before preflight, dispatch, or handoff; the roadmap/index
# stays a derivative projection of the audit object.
#
# Usage: check-cold-review-contract.sh [--repo-root <dir>]
#        check-cold-review-contract.sh --fixture <record.md>
#        check-cold-review-contract.sh --run-root <record-dir>

fail() {
  printf 'check-cold-review-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture=""
successor_root=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-root)
      [ "$#" -ge 2 ] || fail "--repo-root requires a directory argument"
      repo_root="$2"
      shift 2
      ;;
    --fixture)
      [ "$#" -ge 2 ] || fail "--fixture requires a file argument"
      fixture="$2"
      shift 2
      ;;
    --run-root)
      [ "$#" -ge 2 ] || fail "--run-root requires a directory argument"
      successor_root="$2"
      shift 2
      ;;
    *) fail "unknown argument: $1" ;;
  esac
done
[ -z "$fixture" ] || [ -z "$successor_root" ] \
  || fail "--fixture and --run-root are mutually exclusive"
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  [ -f "$file" ] || fail "missing file: $file"
  grep -Fqi -e "$text" "$file" || fail "missing in $file: $text"
}

# #86 review-integrity cases are deterministic record fixtures. This parser is
# also callable with --fixture so tests can prove the negative cases really
# fail rather than merely asserting that their prose says FAIL.
check_issue86_fixture() {
  local path="$1" py=()
  [ -e "$path" ] || fail "missing #86 review record: $path"
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else fail "python, python3, or py -3 is required for #86 fixture validation"
  fi
  "${py[@]}" - "$path" <<'PY'
import hashlib
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
base = path.resolve() if path.is_dir() else path.parent.resolve()
if path.is_dir():
    sources = sorted(path.rglob("*.md"))
else:
    sources = [path]
def contract_lines(source):
    result = []
    fenced = False
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            result.append(line)
    return result


source_text = {source: contract_lines(source) for source in sources}
lines = [
    line
    for source in sources
    for line in source_text[source]
    if re.match(
        r"^\s*(reviewer-attestation|cold-review-disposition|successor-review|lane-status)\s*:",
        line,
        re.I,
    )
]


def die(message):
    print(f"{path}: {message}", file=sys.stderr)
    raise SystemExit(1)


def exact_rows(prefix):
    near = [line for line in lines if re.match(rf"^\s*{re.escape(prefix[:-1])}\s*:", line, re.I)]
    exact = [line for line in lines if line.startswith(prefix)]
    if len(near) != len(exact):
        die(f"{prefix[:-1]} rows must use exact lowercase column-zero grammar")
    return exact


def fields(line, prefix, expected):
    parts = [part.strip() for part in line.split("|")]
    first = parts[0][len(prefix):].strip()
    parts = ([first] if first else []) + parts[1:]
    values = {}
    order = []
    for part in parts:
        if ":" not in part:
            die(f"{prefix[:-1]} malformed field: {part}")
        key, value = (item.strip() for item in part.split(":", 1))
        if key in values or key not in expected or not value:
            die(f"{prefix[:-1]} duplicate, unknown, or empty field: {key}")
        values[key] = value
        order.append(key)
    if order != list(expected):
        die(f"{prefix[:-1]} requires exact fields in order: {', '.join(expected)}")
    return values


def safe_file(rel, purpose):
    pure = pathlib.PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts or ":" in rel or "\\" in rel:
        die(f"{purpose} must be safe and record-root-relative")
    candidate = base / pathlib.Path(*pure.parts)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(base)
    except ValueError:
        die(f"{purpose} escapes the review record root")
    if not candidate.is_file() or candidate.is_symlink():
        die(f"{purpose} must resolve to a regular non-symlink file")
    return candidate


andon_occurrences = {}
andon_source = (base / "STATE.md") if path.is_dir() else path
if andon_source.is_file() and not andon_source.is_symlink():
    andon_lines = andon_source.read_text(encoding="utf-8").splitlines()
    headings = [index for index, line in enumerate(andon_lines) if line == "## Andon log"]
    if len(headings) > 1:
        die("canonical Andon surface requires exactly one ## Andon log section")
    section = []
    if headings:
        for line in andon_lines[headings[0] + 1:]:
            if line.startswith("## "):
                break
            section.append(line)
    for index, line in enumerate(section):
        if not line.startswith("|"):
            continue
        header = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "Occ" not in header or "Class" not in header:
            continue
        occ_index = header.index("Occ")
        class_index = header.index("Class")
        for row_line in section[index + 1:]:
            if not row_line.startswith("|"):
                break
            cells = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
            if not cells or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                continue
            if max(occ_index, class_index) >= len(cells):
                die("Andon row does not match its Occ/Class header")
            occurrence = cells[occ_index]
            klass = cells[class_index]
            if not re.fullmatch(r"o[1-9][0-9]*", occurrence):
                continue
            if occurrence in andon_occurrences and andon_occurrences[occurrence] != klass:
                die("Andon occurrence has conflicting classes")
            andon_occurrences[occurrence] = klass


def packet_contract(scope_path):
    scope_lines = scope_path.read_text(encoding="utf-8").splitlines()
    near = [line for line in scope_lines if re.match(r"^\s*review-packet-scope\s*:", line, re.I)]
    exact = [line for line in scope_lines if line.startswith("review-packet-scope:")]
    if len(near) != 1 or len(exact) != 1:
        die("packet_scope_file requires exactly one review-packet-scope row")
    row = fields(
        exact[0],
        "review-packet-scope:",
        ("scope", "technique", "evidence_mode"),
    )
    scope = row["scope"].split(",")
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9._/-]*", item) for item in scope):
        die("review-packet-scope scope must be comma-separated lowercase tokens")
    if len(set(scope)) != len(scope):
        die("review-packet-scope scope tokens must be unique")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", row["technique"]):
        die("review-packet-scope technique must be one lowercase token")
    if row["evidence_mode"] not in {"inline", "reference"}:
        die("review-packet-scope evidence_mode must be inline or reference")
    return frozenset(scope), row["technique"], row["evidence_mode"]


def resolve_finding_refs(value):
    if value == "none":
        return
    for ref in value.split(","):
        ref = ref.strip()
        match = re.fullmatch(r"([A-Za-z0-9._/-]+)#([a-z0-9][a-z0-9._-]*)", ref)
        if not match:
            die("provisional finding references must use safe-file.md#anchor grammar")
        finding_file = safe_file(match.group(1), "provisional finding file")
        heading = re.compile(rf"^#{{1,6}}\s+{re.escape(match.group(2))}$")
        finding_lines = finding_file.read_text(encoding="utf-8").splitlines()
        heading_indexes = [index for index, line in enumerate(finding_lines) if heading.fullmatch(line)]
        if len(heading_indexes) != 1:
            die("provisional finding reference does not resolve to a contained heading")
        tail = [line for line in finding_lines[heading_indexes[0] + 1:] if line.strip()]
        expected = f"finding-record: id: {match.group(2)} | status: provisional"
        if not tail or tail[0] != expected:
            die("provisional finding reference does not resolve to an exact finding-record")


attestation_rows = exact_rows("reviewer-attestation:")
if len(attestation_rows) > 1:
    die("reviewer-attestation must appear at most once")
attestation = None
if attestation_rows:
    attestation = fields(
        attestation_rows[0],
        "reviewer-attestation:",
        (
            "reviewer_identity", "requested_model", "actual_model",
            "authoring_context_reuse", "other_reviewer_output_seen",
            "base_sha", "head_sha",
        ),
    )
    if attestation["authoring_context_reuse"] not in {"yes", "no"}:
        die("authoring_context_reuse must be yes or no")
    if attestation["other_reviewer_output_seen"] not in {"yes", "no"}:
        die("other_reviewer_output_seen must be yes or no")
    for key in ("base_sha", "head_sha"):
        if not re.fullmatch(r"[0-9a-f]{40}", attestation[key]):
            die(f"{key} must be full lowercase 40-hex")

disposition_rows = exact_rows("cold-review-disposition:")
if len(disposition_rows) > 1:
    die("cold-review-disposition must appear at most once")
if disposition_rows:
    disposition = disposition_rows[0].split(":", 1)[1].strip()
    if disposition not in {"PASS", "GAP-REVISE", "BLOCKED", "OWNER DECISION"}:
        die("invalid cold-review disposition")
    if attestation is None:
        die("cold-review disposition requires reviewer-attestation")
    if attestation["authoring_context_reuse"] == "yes":
        die("authoring-context reuse is self-critique and cannot discharge cold review")

successors = []
for line in exact_rows("successor-review:"):
    row = fields(
        line,
        "successor-review:",
        (
            "attempt", "predecessor_failure_origin", "failure_determinism", "origin_detail",
            "predecessor_occurrence",
            "predecessor_packet_scope_file", "predecessor_packet_scope_sha256",
            "packet_scope_file", "packet_scope_sha256", "packet_alteration", "andon_class",
            "provisional_findings_carried",
        ),
    )
    if row["predecessor_failure_origin"] != "transport-infrastructure":
        die("successor predecessor_failure_origin must reuse transport-infrastructure")
    if row["failure_determinism"] not in {"content-deterministic", "transient"}:
        die("failure_determinism must be content-deterministic or transient")
    if not re.fullmatch(r"[1-9][0-9]*", row["attempt"]):
        die("successor attempt must be a positive integer")
    occurrence = row["predecessor_occurrence"]
    if not re.fullmatch(r"o[1-9][0-9]*", occurrence):
        die("predecessor_occurrence must be an exact occurrence token")
    if andon_occurrences.get(occurrence) != "transport-infrastructure":
        die("predecessor_occurrence must resolve to a transport-infrastructure Andon row")
    predecessor_scope_path = safe_file(
        row["predecessor_packet_scope_file"], "predecessor_packet_scope_file"
    )
    if not re.fullmatch(r"[0-9a-f]{64}", row["predecessor_packet_scope_sha256"]):
        die("predecessor_packet_scope_sha256 must be lowercase 64-hex")
    if hashlib.sha256(predecessor_scope_path.read_bytes()).hexdigest() != row["predecessor_packet_scope_sha256"]:
        die("predecessor_packet_scope_sha256 does not match predecessor packet bytes")
    scope_path = safe_file(row["packet_scope_file"], "packet_scope_file")
    if not re.fullmatch(r"[0-9a-f]{64}", row["packet_scope_sha256"]):
        die("packet_scope_sha256 must be lowercase 64-hex")
    if hashlib.sha256(scope_path.read_bytes()).hexdigest() != row["packet_scope_sha256"]:
        die("packet_scope_sha256 does not match packet_scope_file bytes")
    if row["andon_class"] != "transport-infrastructure":
        die("successor retry must cite the transport-infrastructure Andon class")
    row["predecessor_packet_contract"] = packet_contract(predecessor_scope_path)
    row["packet_contract"] = packet_contract(scope_path)
    resolve_finding_refs(row["provisional_findings_carried"])
    successors.append(row)

successor_groups = {}
for row in successors:
    key = row["predecessor_occurrence"]
    successor_groups.setdefault(key, []).append(row)
for key, group in successor_groups.items():
    attempts = [int(row["attempt"]) for row in group]
    if len(set(attempts)) != len(attempts):
        die("successor attempts must be unique within one failure origin")
    if sorted(attempts) != list(range(1, len(group) + 1)):
        die("successor attempts must be contiguous from 1 within one predecessor occurrence")
    determinism = {row["failure_determinism"] for row in group}
    if len(determinism) != 1:
        die("one predecessor occurrence cannot change failure_determinism")
    predecessor_packets = {
        (row["predecessor_packet_scope_file"], row["predecessor_packet_scope_sha256"])
        for row in group
    }
    if len(predecessor_packets) != 1:
        die("one predecessor occurrence must bind one refused predecessor packet")
    if next(iter(determinism)) != "content-deterministic":
        continue
    group.sort(key=lambda row: int(row["attempt"]))
    transitions = [(None, group[0])] + list(zip(group, group[1:]))
    for previous, current in transitions:
        before_contract = (
            current["predecessor_packet_contract"]
            if previous is None
            else previous["packet_contract"]
        )
        before_scope, before_technique, before_evidence = before_contract
        after_scope, after_technique, after_evidence = current["packet_contract"]
        changes = []
        if after_scope != before_scope:
            if not after_scope < before_scope:
                die("content-deterministic retry scope change must be a strict narrowing")
            changes.append("scope-narrowed")
        if after_technique != before_technique:
            changes.append("technique-reworded")
        if after_evidence != before_evidence:
            if not (before_evidence == "inline" and after_evidence == "reference"):
                die("content-deterministic retry evidence mode may only move inline to reference")
            changes.append("evidence-by-reference")
        if not changes:
            die("content-deterministic refusal cannot respawn a materially unaltered packet")
        expected_alteration = "+".join(changes)
        if current["packet_alteration"] != expected_alteration:
            die("packet_alteration does not match the inspectable review-packet-scope delta")

non_verdict = []
for line in exact_rows("lane-status:"):
    value = line[len("lane-status:"):].strip()
    if value == "executed":
        continue
    if value.startswith("status: REVIEWER_RUNTIME_NON_VERDICT"):
        non_verdict.append(fields(
            line,
            "lane-status:",
            (
                "status", "predecessor_failure_origin", "failure_determinism",
                "origin_detail", "predecessor_occurrence", "provisional_findings",
                "substantive_verdict_consumed",
            ),
        ))
    else:
        die("unknown lane-status")

for row in non_verdict:
    if row["status"] != "REVIEWER_RUNTIME_NON_VERDICT":
        die("invalid runtime non-verdict status")
    if row["predecessor_failure_origin"] != "transport-infrastructure":
        die("runtime non-verdict must reuse transport-infrastructure")
    if row["failure_determinism"] not in {"content-deterministic", "transient"}:
        die("runtime non-verdict failure_determinism is invalid")
    occurrence = row["predecessor_occurrence"]
    if andon_occurrences.get(occurrence) != "transport-infrastructure":
        die("runtime non-verdict predecessor_occurrence must resolve to its transport Andon")
    if row["provisional_findings"] == "none":
        die("runtime non-verdict must preserve provisional findings")
    resolve_finding_refs(row["provisional_findings"])
    if row["substantive_verdict_consumed"] != "no":
        die("runtime non-verdict cannot consume the substantive verdict")
    if not any(
        s["predecessor_occurrence"] == occurrence
        and s["predecessor_failure_origin"] == row["predecessor_failure_origin"]
        and s["failure_determinism"] == row["failure_determinism"]
        and s["origin_detail"] == row["origin_detail"]
        and s["provisional_findings_carried"] == row["provisional_findings"]
        for s in successors
    ):
        die("replacement packet did not carry the provisional findings")
PY
}

if [ -n "$fixture" ]; then
  check_issue86_fixture "$fixture"
  exit 0
fi
if [ -n "$successor_root" ]; then
  [ -d "$successor_root" ] || fail "--run-root is not a directory: $successor_root"
  check_issue86_fixture "$successor_root"
  exit 0
fi

# --- SKILL.md stage map carries the gate ---
skill="skills/implementaudit/SKILL.md"
for text in \
  "Stage 6.2 - Independent cold review" \
  "does not reuse the authoring context" \
  "separate child agent where the host supports subagents" \
  "bounded" \
  "serial fresh-context pass" \
  "PASS / GAP-REVISE / BLOCKED / OWNER DECISION" \
  "No handoff, preflight, or dispatch proceeds without a disposition" \
  "Self-critique is" \
  "preserved, not replaced"
do
  require "$skill" "$text"
done

# Stage 6 self-critique must remain intact (preserved, not replaced).
require "$skill" "Stage 6 - Plan review and self-critique"
require "$skill" "Stage 6.5 - Pre-flight smoke"

# --- planning-depth stage list includes the new stage ---
require "skills/implementaudit/references/planning-depth.md" \
  "Stage 6.2 - Independent cold review"

# --- plan-lifecycle owns the disposition and independence contract ---
plan_ref="skills/implementaudit/references/plan-lifecycle.md"
for text in \
  "Self-critique and independent cold review are distinct gates" \
  "does not reuse" \
  "fresh-context reviewer subagent" \
  "bounded serial fresh-context pass" \
  "GAP-REVISE" \
  "OWNER DECISION" \
  "without a recorded disposition" \
  "authoring action" \
  "does not satisfy the gate" \
  "never requires a" \
  "no arbitrary revision caps"
do
  require "$plan_ref" "$text"
done

# --- child-agents carries the reviewer lane ---
child_ref="skills/implementaudit/references/child-agents.md"
for text in \
  "## Independent cold-review lane" \
  "deliberately excludes the authoring session" \
  "cold reader and weak executor" \
  "PASS / GAP-REVISE / BLOCKED /" \
  "non-authoritative"
do
  require "$child_ref" "$text"
done

# --- templates: projection and record home ---
roadmap="skills/implementaudit/templates/ROADMAP.md"
for text in \
  "| Review | Status |" \
  "independent cold-review disposition" \
  "## Execution index (projection)" \
  "derivative, never canonical" \
  "corrected to match them"
do
  require "$roadmap" "$text"
done

require "skills/implementaudit/templates/THINKING.md" \
  "Independent cold-review disposition (PASS / GAP-REVISE / BLOCKED / OWNER DECISION)"

# --- #86: auditable reviewer identity and origin-scoped retry ---
report_template="skills/implementaudit/templates/child-agent-report.md"
for text in \
  "Reviewer attestation:" \
  "requested_model:" \
  "actual_model:" \
  "authoring_context_reuse:" \
  "other_reviewer_output_seen:" \
  "predecessor_failure_origin:" \
  "packet_alteration:"
do
  require "$report_template" "$text"
done
for text in \
  "Report state: FINAL" \
  "REVIEWER_RUNTIME_NON_VERDICT" \
  "does not consume the substantive verdict" \
  "reviewer corrects a defective probe" \
  "predecessor_occurrence" \
  "safe-file.md#heading"
do
  require "$child_ref" "$text"
done
for text in \
  "content-deterministic refusal" \
  "do not reissue an unaltered packet" \
  "transient channel failure" \
  "reissue to the same reviewer identity"
do
  require "skills/implementaudit/references/transcript-contract.md" "$text"
done

for positive in \
  issue-86-attested-pass.md \
  issue-86-altered-packet-respawn.md \
  issue-86-runtime-non-verdict-replacement.md \
  issue-86-reviewer-selfcorrected-probe.md \
  issue-86-transient-channel-respawn.md
do
  check_issue86_fixture "fixtures/cold-review/$positive" >/dev/null \
    || fail "#86 positive fixture rejected: $positive"
done
for negative in \
  issue-86-negative-self-review-labeled.md \
  issue-86-negative-deterministic-respawn.md
do
  if check_issue86_fixture "fixtures/cold-review/$negative" >/dev/null 2>&1; then
    fail "#86 negative fixture false-greened: $negative"
  fi
done

# --- adapted routing fixture carries the semantics ---
require "fixtures/audit-object-routing/plan-lifecycle.md" "independent cold review"
require "fixtures/audit-object-routing/plan-lifecycle.md" "derivative of the audit"

# --- positive fixtures ---
pos="fixtures/cold-review/independent-review-confirms-handoff.md"
for text in \
  "no \"review\" keyword anywhere" \
  "separate" \
  "fresh-context child agent" \
  "disposition PASS" \
  "before preflight" \
  "distinct gates"
do
  require "$pos" "$text"
done

proj="fixtures/cold-review/projection-index-derivative.md"
for text in \
  "derivative, never canonical" \
  "phase specs govern" \
  "status theater"
do
  require "$proj" "$text"
done

# --- negative fixtures declare their failing disposition ---
for negative in \
  "fixtures/cold-review/negative-self-critique-only-preflight.md" \
  "fixtures/cold-review/negative-same-context-review.md" \
  "fixtures/cold-review/negative-projection-contradicts-object.md" \
  "fixtures/cold-review/negative-review-keyword-gate.md"
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when reviewed: FAIL"
done

# --- no command-mode advertisement (including review-plan) in new surfaces ---
if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap|review-plan|review)\b' \
  fixtures/cold-review "$plan_ref" "$child_ref" \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-cold-review-command-mode-hit.txt; then
  cat /tmp/implementaudit-cold-review-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-cold-review-command-mode-hit.txt
  fail "command-mode identity advertised in cold-review surfaces"
fi
rm -f /tmp/implementaudit-cold-review-command-mode-hit.txt

printf 'check-cold-review-contract: ok\n'
