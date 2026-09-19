#!/usr/bin/env python3
"""Automatic-effect preflight policy and bounded read-only CLI.

Restricted maintained-form YAML interpretation is preserved, not promoted to a
general YAML verifier. No network, Git mutation or workflow execution occurs.
"""
from __future__ import annotations
import fnmatch
import pathlib
import re
import sys

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
    reject_unsupported_collection_scalar(value, label)
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
    return parse_yaml_nodes(path.read_text(encoding="utf-8"), path)


def parse_yaml_nodes(text, path="<workflow>"):
    """Parse the same bounded YAML surface from caller-supplied text; no IO."""
    raw_lines = text.splitlines()
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


def trigger_matches(path, nodes, event, ref):
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



def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 4:
        die("automatic-effect preflight requires <repo-root> <event> <ref> <mutation-plan>")
    root = pathlib.Path(argv[0]).resolve()
    event = argv[1]
    ref = argv[2]
    if ref.startswith("refs/heads/"):
        ref = ref[len("refs/heads/"):]
    plan = pathlib.Path(argv[3]).resolve()
    workflow_root = root / ".github" / "workflows"
    if event != "push" or not ref:
        raise SystemExit("check-closure-surface: automatic-effect preflight requires push and a nonempty branch ref")


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
            if trigger_matches(path, nodes, event, ref):
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
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
