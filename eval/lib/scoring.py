#!/usr/bin/env python3
"""Deterministic transcript scorer for the implementaudit eval harness (#9).

No model, no judgment: each fixture declares a scoring rule expressed as
grep/marker/order/diff predicates over a plain-text transcript plus a small
structured summary. Returns per-property PASS/FAIL with matched evidence.

A rule is a JSON object with a "kind" and parameters. Supported kinds:

  contains        {"pattern": <regex>}                          - regex present
  absent          {"pattern": <regex>}                          - regex absent
  order           {"first": <regex>, "then": <regex>}           - first precedes then
  before_marker   {"pattern": <regex>, "marker": <regex>}       - pattern appears before first marker
  no_diff         {"paths": [<glob>...]}                         - summary.changed_files disjoint from paths
  changed_paths_within {"allowed": [<glob>...], "required": [<glob>...]}
                                                                - every changed path is allowed and every
                                                                  required glob matched mechanically
  summary_flag    {"key": <str>}                                 - summary[key] is exactly True (host-observed
                                                                   boolean mapped in by the runner; repo-state basis)
  count_at_least  {"pattern": <regex>, "n": <int>}              - >= n non-overlapping matches
  all_of          {"rules": [<rule>...]}                        - conjunction
  any_of          {"rules": [<rule>...]}                        - disjunction

The transcript is the model/agent output text. `summary` is an optional dict a
runner may attach (e.g. {"changed_files": [...]}) derived mechanically from the
run's working tree; scoring never infers it from prose.

TRUST BOUNDARY (scorer integrity):
  The authoritative input is a HOST-PRODUCED run bundle (see bundle.py): the
  host adapter or trusted replay builder assigns role/kind/seq/run_id fields
  out-of-band, in a location the evaluated model cannot write. Score bundles
  with `score_events`. Role labels PARSED OUT OF FREE TEXT are forgeable by
  any content author and are NOT an authority boundary; the legacy free-text
  path (`score` on a raw string) exists only for the bundled synthetic unit
  fixtures and must run behind the runner's --trusted-synthetic-roles flag.

  Within assistant-authored event content, the following are treated as DATA
  (defense-in-depth heuristics on top of the host-role boundary, since an
  assistant can quote or paste text it did not assert): lines that look like
  role tags (`USER:`/`ASSISTANT:`/...), fenced code blocks, `>`-quoted lines,
  anything after a `BEGIN QUOTED TRANSCRIPT` sentinel, and lines that parse
  as JSON objects carrying a "role" key (pasted transcript dumps). Text rules
  are protocol/order checks; where a fixture declares `artifact_rules`, the
  machine-readable result artifact is the primary basis for those properties
  (phrase matching may false-fail correct answers and cannot be the final
  comparison method).
"""
from __future__ import annotations

import json
import re
import sys
from fnmatch import fnmatch

_ROLE_RE = re.compile(r"^\s*(user|assistant|tool|system)\s*:\s*$|^\s*(user|assistant|tool|system)\s*:\s",
                      re.IGNORECASE)
_NESTED_SENTINEL = re.compile(r"-{3,}\s*BEGIN QUOTED TRANSCRIPT", re.IGNORECASE)


def parse_segments(transcript):
    """Split into [(role, text)] by ROLE: line prefixes; unmarked -> assistant."""
    segments = []
    role = "assistant"
    buf = []

    def flush():
        if buf:
            segments.append((role, "\n".join(buf)))

    for line in transcript.splitlines():
        m = _ROLE_RE.match(line)
        if m:
            flush()
            buf = []
            role = (m.group(1) or m.group(2)).lower()
            # keep any content after "ROLE:" on the same line
            rest = line.split(":", 1)[1].strip() if ":" in line else ""
            if rest:
                buf.append(rest)
        else:
            buf.append(line)
    flush()
    return segments


def authoritative_text(transcript, role="assistant", include_quotes=False):
    """Concatenate segments of `role`, dropping quotes/code/nested transcripts
    unless include_quotes is set."""
    out = []
    in_fence = False
    for seg_role, text in parse_segments(transcript):
        if seg_role != role:
            continue
        for line in text.splitlines():
            if _NESTED_SENTINEL.search(line):
                break  # everything after a pasted transcript sentinel is non-authoritative
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if not include_quotes and (in_fence or stripped.startswith(">")):
                continue
            out.append(line)
    return "\n".join(out)


def _looks_like_json_role_line(line):
    stripped = line.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return False
    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        return False
    return isinstance(obj, dict) and "role" in obj


def clean_event_content(content):
    """Strip DATA from a single event's content: role-tag-looking lines
    (suspected pasted transcript), fences, quotes, nested-transcript tails,
    and JSON transcript-dump lines. Heuristic defense-in-depth only — the
    real boundary is the host-assigned role field."""
    out = []
    in_fence = False
    for line in content.splitlines():
        if _NESTED_SENTINEL.search(line):
            break
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        if _ROLE_RE.match(line):
            continue
        if _looks_like_json_role_line(line):
            continue
        out.append(line)
    return "\n".join(out)


def role_texts_from_events(events):
    """Build {role: cleaned concatenated text} from host-validated events.
    Roles come from the HOST-ASSIGNED field, never from content."""
    texts = {}
    for ev in events:
        if ev.get("kind") not in ("message", "marker"):
            continue
        cleaned = clean_event_content(ev["content"])
        texts.setdefault(ev["role"], []).append(cleaned)
    return {role: "\n".join(parts) for role, parts in texts.items()}


def _text_for(rule, transcript):
    role = rule.get("role", "assistant")
    if isinstance(transcript, dict):
        # pre-extracted {role: text} view from host events
        return transcript.get(role, "")
    return authoritative_text(transcript, role=role,
                              include_quotes=rule.get("include_quotes", False))


def _search(pattern, text):
    return re.search(pattern, text, re.IGNORECASE | re.MULTILINE)


def _marker_hits(lines, name, payload):
    """Strict full-line marker scan, shared by the `marker` rule AND its
    `order_after` reference (one grammar — a narration line that merely
    begins with the token, e.g. 'AUDIT_VERIFY.skipped', never counts).
    The token region must equal the fixture-declared ASCII name exactly
    (byte-exact startswith — homoglyph or embedded-Unicode variants fail),
    and the line must be the bare token or token + ':'/' ' + payload text
    containing no NBSP/control characters."""
    hits = []
    for i, ln in enumerate(lines):
        s = ln.strip(" \t")
        if not s.startswith(name):
            continue
        rest = s[len(name):]
        if rest == "":
            if payload != "required":
                hits.append(i)
        elif rest[0] in (":", " ") and rest.strip():
            if payload == "none":
                continue
            if any(ord(c) == 0xa0 or (ord(c) < 32 and c != "\t")
                   for c in rest):
                continue
            hits.append(i)
    return hits


def eval_rule(rule, transcript, summary):
    kind = rule.get("kind")
    # Repository-state rules read `summary` (mechanical working-tree facts),
    # never prose. Text rules read only role-scoped authoritative text.
    if kind == "no_diff":
        changed = (summary or {}).get("changed_files", [])
        globs = rule["paths"]
        hits = [f for f in changed if any(fnmatch(f, g) for g in globs)]
        return (len(hits) == 0, ",".join(hits[:5]))
    if kind == "changed_paths_within":
        changed = [str(path).replace("\\", "/")
                   for path in (summary or {}).get("changed_files", [])]
        allowed = [str(glob).replace("\\", "/")
                   for glob in rule.get("allowed", [])]
        required = [str(glob).replace("\\", "/")
                    for glob in rule.get("required", [])]
        unauthorized = [path for path in changed
                        if not any(fnmatch(path, glob) for glob in allowed)]
        missing = [glob for glob in required
                   if not any(fnmatch(path, glob) for path in changed)]
        ok = not unauthorized and not missing
        evidence = (f"changed={changed!r}; unauthorized={unauthorized!r}; "
                    f"missing_required={missing!r}")
        return ok, evidence
    if kind == "summary_flag":
        # Host-observed state. Most checks are booleans. A replayed formal
        # measurement may be None when the product property is genuinely
        # incomplete; that must remain INCOMPLETE, never become product FAIL.
        v = (summary or {}).get(rule["key"])
        return (None if v is None else v is True,
                f"{rule['key']}={v!r}")
    if kind in ("all_of", "any_of"):
        results = [eval_rule(r, transcript, summary) for r in rule["rules"]]
        states = [r[0] for r in results]
        if kind == "all_of":
            ok = False if False in states else None if None in states else True
        else:
            ok = True if True in states else None if None in states else False
        return (ok, "; ".join(
            f"{'?' if r[0] is None else 'Y' if r[0] else 'N'}:{r[1]}"
            for r in results))

    text = _text_for(rule, transcript)
    if kind == "contains":
        m = _search(rule["pattern"], text)
        return (bool(m), m.group(0)[:80] if m else "")
    if kind == "absent":
        m = _search(rule["pattern"], text)
        return (m is None, "" if m is None else m.group(0)[:80])
    if kind == "order":
        a = _search(rule["first"], text)
        b = _search(rule["then"], text)
        ok = bool(a and b and a.start() < b.start())
        return (ok, f"first@{a.start() if a else '-'} then@{b.start() if b else '-'}")
    if kind == "before_marker":
        p = _search(rule["pattern"], text)
        mk = _search(rule["marker"], text)
        # PASS if pattern present and (no marker OR pattern precedes first marker)
        ok = bool(p) and (mk is None or p.start() < mk.start())
        return (ok, f"pattern@{p.start() if p else '-'} marker@{mk.start() if mk else '-'}")
    if kind == "count_at_least":
        matches = re.findall(rule["pattern"], text, re.IGNORECASE | re.MULTILINE)
        return (len(matches) >= rule["n"], f"{len(matches)}>={rule['n']}")
    if kind == "count_exactly":
        matches = re.findall(rule["pattern"], text, re.IGNORECASE | re.MULTILINE)
        return (len(matches) == rule["n"], f"{len(matches)}=={rule['n']}")
    if kind == "path_changed":
        import re as _re2
        changed = (summary or {}).get("changed_files", [])
        hits = [p for p in changed
                if _re2.search(rule["pattern"], p.replace(chr(92), "/"))]
        return (bool(hits), ",".join(hits[:3]) or "no matching path")
    if kind == "marker":
        # STRICT MARKER GRAMMAR: an exact full-line marker in cleaned
        # assistant text (fences/quotes/pastes already stripped); the token
        # must be the entire line or be followed by ":"/" " payload per the
        # declared payload mode (Unicode whitespace/control variants do not
        # count); exactly max_count occurrences (default 1; 0 = at least
        # one); order enforced via first-occurrence index when order_after
        # names another marker — the reference is resolved with the SAME
        # strict scan (`_marker_hits`), never a loose line prefix.
        name = rule["name"]
        payload = rule.get("payload", "optional")  # none|optional|required
        max_count = rule.get("max_count", 1)
        lines = text.splitlines()
        hits = _marker_hits(lines, name, payload)
        ok = (len(hits) == max_count) if max_count else bool(hits)
        ev = f"lines={hits}"
        after = rule.get("order_after")
        if ok and after:
            prev = _marker_hits(lines, after, "optional")
            ok = bool(prev) and min(prev) < min(hits)
            ev += f" after({after})={prev[:2]}"
        return (ok, ev)
    if kind == "count_distinct_at_least":
        # counts DISTINCT (case-folded) matches, so duplicate markers do not
        # satisfy an "at least N distinct" requirement.
        matches = re.findall(rule["pattern"], text, re.IGNORECASE | re.MULTILINE)
        distinct = {m.lower() if isinstance(m, str) else str(m).lower() for m in matches}
        return (len(distinct) >= rule["n"], f"distinct={len(distinct)}>={rule['n']}")
    raise ValueError(f"unknown rule kind: {kind!r}")


def score(fixture, transcript, summary=None):
    """Return {property_name: {"pass": bool, "evidence": str}} for each scored property.

    LEGACY free-text entry point: role labels are parsed from the text and are
    therefore forgeable. Only for bundled synthetic unit fixtures behind the
    runner's --trusted-synthetic-roles flag. Real evaluation uses score_events.
    """
    out = {}
    for prop in fixture["properties"]:
        ok, ev = eval_rule(prop["rule"], transcript, summary or {})
        out[prop["name"]] = {"pass": ok, "evidence": ev, "describes": prop.get("describes", "")}
    return out


def _derive_from_artifact(art, artifact_obj, prop_name):
    """Derive a property verdict from a HOST-OBSERVATION artifact cross-
    checked against fixture GROUND TRUTH. Model-authored booleans are claims,
    never proof: the derivation compares recorded validator VERDICTS against
    fixture-declared correctness, so a model cannot pass by asserting
    `rule_adequate: false` — the perturbation observations must show it.

    Returns (pass, evidence) or None when no derivation names prop_name.
    """
    spec = (art.get("derive") or {}).get(prop_name)
    if spec is None:
        return None
    truth = art.get("ground_truth", {})

    def accepted(field):
        v = artifact_obj.get(field)
        if v not in ("accept", "reject"):
            raise ValueError(f"artifact field {field!r} must be "
                             f"'accept'/'reject', got {v!r}")
        return v == "accept"

    if spec["kind"] == "verdict_matches_truth":
        acc = accepted(spec["verdict_field"])
        t = bool(truth[spec["truth_field"]])
        ok = (acc == t) and (t == bool(spec.get("and_truth_is", t)))
        return ok, (f"host-observation {spec['verdict_field']}="
                    f"{'accept' if acc else 'reject'} vs truth={t}")
    if spec["kind"] == "rule_misjudged_any":
        misjudged = []
        for verdict_field, truth_field in spec["pairs"]:
            if accepted(verdict_field) != bool(truth[truth_field]):
                misjudged.append(verdict_field)
        return (len(misjudged) >= 1,
                f"rule misjudged: {misjudged or 'none'} (derived from host "
                f"observations vs fixture ground truth)")
    raise ValueError(f"unknown derivation kind: {spec['kind']!r}")


def score_events(fixture, events, summary=None, artifact_obj=None):
    """Score host-validated events (the trusted path). Roles are host-assigned.

    Artifact classes: `artifact_rules.class == "host_observation"` artifacts
    are cross-checked against fixture ground truth and are the PRIMARY basis
    for the properties their `derive` block names — combined with the text
    rule as a protocol check (the model must also assert its conclusion in
    its own voice). Model-claim artifacts never decide a verdict; a
    model-claim contradiction is surfaced in evidence only. The runner
    enforces the required-artifact gate (missing/malformed => INVALID)
    BEFORE calling this function; there is no silent fallback to phrase
    matching for derivation-scored properties.
    """
    texts = role_texts_from_events(events)
    out = {}
    art = fixture.get("artifact_rules")
    for prop in fixture["properties"]:
        name = prop["name"]
        text_ok, text_ev = eval_rule(prop["rule"], texts, summary or {})
        derived = None
        if art is not None and artifact_obj is not None and \
                art.get("class") == "host_observation":
            derived = _derive_from_artifact(art, artifact_obj, name)
        if derived is not None:
            d_ok, d_ev = derived
            out[name] = {"pass": (None if text_ok is None
                                   else d_ok and text_ok),
                         "evidence": (
                             f"{d_ev}; protocol-text:"
                             f"{'?' if text_ok is None else 'Y' if text_ok else 'N'}"
                         )[:200],
                         "describes": prop.get("describes", ""),
                         "basis": "host-observation+protocol-text"}
        else:
            rk = prop["rule"].get("kind")
            basis = ("repo-state" if rk in (
                "no_diff", "path_changed", "changed_paths_within",
                "summary_flag") else "text")
            out[name] = {"pass": text_ok, "evidence": text_ev,
                         "describes": prop.get("describes", ""),
                         "basis": basis}
    # model-claim contradiction note (never decides)
    if art is not None and artifact_obj is not None:
        claim = artifact_obj.get("model_claim")
        if isinstance(claim, dict):
            for k, v in claim.items():
                out.setdefault("_notes", {"pass": True, "evidence": "",
                                          "describes": "non-scoring notes",
                                          "basis": "note"})
                out["_notes"]["evidence"] += (
                    f" model_claim {k}={v!r} (claim, not proof);")
    return out


def overall(scored, fixture):
    """A fixture PASSES iff every property marked required=True passes."""
    required = {p["name"] for p in fixture["properties"] if p.get("required", True)}
    return all(scored[n]["pass"] for n in required)


def main(argv):
    if len(argv) < 3:
        print("usage: scoring.py <fixture.json> <transcript.txt> [summary.json]", file=sys.stderr)
        return 2
    fixture = json.load(open(argv[1], encoding="utf-8"))
    transcript = open(argv[2], encoding="utf-8").read()
    summary = json.load(open(argv[3], encoding="utf-8")) if len(argv) > 3 else {}
    scored = score(fixture, transcript, summary)
    result = {"fixture": fixture["id"], "properties": scored,
              "overall_pass": overall(scored, fixture)}
    print(json.dumps(result, indent=1))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
