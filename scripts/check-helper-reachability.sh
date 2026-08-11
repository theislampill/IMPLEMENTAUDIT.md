#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -eq 2 ] || { printf 'check-helper-reachability: usage: [--repo-root <dir>]\n' >&2; exit 2; }
  repo_root="$(cd "$2" && pwd)"
elif [ "$#" -ne 0 ]; then
  printf 'check-helper-reachability: usage: [--repo-root <dir>]\n' >&2
  exit 2
fi

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-helper-reachability: python, python3, or py -3 is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$repo_root" <<'PY'
import ast
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
builder = root / "scripts" / "build-release-asset.sh"
skill_root = root / "skills" / "implementaudit"
contract = skill_root / "references" / "repo-state-comparison.md"
for path in (builder, skill_root, contract):
    if not path.exists():
        raise SystemExit(f"check-helper-reachability: missing owner: {path}")

builder_text = builder.read_text(encoding="utf-8")
match = re.search(r"(?ms)^required_archive\s*=\s*\[(.*?)^\]", builder_text)
if not match:
    raise SystemExit("check-helper-reachability: required_archive manifest is unreadable")

archive_entries = re.findall(r'"([^"]+)"', match.group(1))
helpers = sorted(
    entry.removeprefix("scripts/")
    for entry in archive_entries
    if re.fullmatch(r"scripts/[^/]+\.sh", entry)
)
if len(helpers) != len(set(helpers)):
    raise SystemExit("check-helper-reachability: duplicate helper in required_archive")

contract_text = contract.read_text(encoding="utf-8")
rows = {}
mode_rows = {}
for line_number, line in enumerate(contract_text.splitlines(), 1):
    if line.startswith("helper-mode: "):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) not in {4, 5}:
            raise SystemExit(
                f"check-helper-reachability: malformed helper mode at line {line_number}"
            )
        helper = parts[0].removeprefix("helper-mode: ")
        key = (helper, parts[1])
        if key in mode_rows:
            raise SystemExit(f"check-helper-reachability: duplicate mode applicability row: {' '.join(key)}")
        mode_rows[key] = {
            "arguments": parts[2], "boundary": parts[3],
            "caller": parts[4] if len(parts) == 5 else "-",
        }
        continue
    if not line.startswith("helper-route: "):
        continue
    parts = [part.strip() for part in line.split("|")]
    if len(parts) != 7:
        raise SystemExit(
            f"check-helper-reachability: malformed helper route at line {line_number}"
        )
    helper = parts[0].removeprefix("helper-route: ")
    if helper in rows:
        raise SystemExit(f"check-helper-reachability: duplicate applicability row: {helper}")
    rows[helper] = {
        "class": parts[1], "trigger": parts[2], "owner": parts[3],
        "caller": parts[4], "arguments": parts[5], "boundary": parts[6],
    }

missing = sorted(set(helpers) - set(rows))
extra = sorted(set(rows) - set(helpers))
if missing:
    suffix = f" (population={len(helpers)} examined={len(rows)})" if len(helpers) != len(rows) else ""
    raise SystemExit(
        "check-helper-reachability: missing applicability rows: "
        + ", ".join(missing) + suffix
    )
if extra:
    raise SystemExit(
        "check-helper-reachability: applicability rows not in package: "
        + ", ".join(extra)
    )

class_names = {
    "A": "automatic", "R": "required-procedural", "O": "optional-advisory",
    "S": "standalone-diagnostic", "I": "internal-library",
}
owner_aliases = {
    "P": "templates/PROTOCOL.md",
    "R": "references/repo-state-comparison.md",
    "C": "references/child-agents.md",
    "S": "SKILL.md",
    "V": "scripts/validate-run-root.sh",
}
mandatory_re = re.compile(
    r"(?i)(?:^|[-_ ])(?:must|mandatory|required|block|gate)(?:$|[-_ .,;:`])"
)
def field_is_anchored(value, content):
    for part in value.lower().replace("artefact", "artifact").split("/"):
        words = [w for w in re.split(r"[^a-z0-9]+", part)
                 if len(w) >= 3 and w not in {"none", "only", "never", "automatic"}]
        if words and all(word in content for word in words):
            return True
    return False

def arguments_are_anchored(value, helper, content):
    token_re = re.compile(r"--[a-z0-9][a-z0-9-]*|<[^>]+>|\.\.\.|[a-z0-9][a-z0-9-]*")
    expected = [] if value.lower() == "none" else token_re.findall(value.lower())
    candidates = re.findall(r"`([^`]*" + re.escape(helper) + r"[^`]*)`",
                            content, re.I | re.S)
    candidates.extend(
        line.split("#", 1)[0] for line in content.splitlines()
        if helper in line and "`" not in line and
        re.match(r"\s*(?:bash|source|exec)\b", line, re.I)
    )
    for candidate in candidates:
        match = re.search(re.escape(helper), candidate, re.I)
        actual = token_re.findall(candidate[match.end():].lower()) if match else []
        if actual == expected:
            return True
    return False

def shell_code(content):
    cleaned = []
    for line in content.splitlines():
        quote = None
        escaped = False
        kept = []
        for index, char in enumerate(line):
            if escaped:
                kept.append(char)
                escaped = False
                continue
            if char == "\\" and quote != "'":
                kept.append(char)
                escaped = True
                continue
            if char in {"'", '"'}:
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
                kept.append(char)
                continue
            if char == "#" and quote is None and (index == 0 or line[index - 1].isspace()):
                break
            kept.append(char)
        cleaned.append("".join(kept))
    return "\n".join(cleaned)

def shell_parser_code(content):
    """Return shell syntax without heredoc bodies (which are data, not arms)."""
    kept = []
    lines = iter(content.splitlines())
    for line in lines:
        kept.append(line)
        tags = re.findall(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", line)
        for tag in tags:
            for body_line in lines:
                if body_line.strip() == tag:
                    break
    return "\n".join(kept)

def caller_invokes(helper, content):
    content = shell_code(content)
    def command_uses(target, path_prefix=False):
        prefix = r'''(?:[^\s"']*/)?''' if path_prefix else ""
        operand = rf'''["']?{prefix}{target}["']?(?=\s|$)'''
        direct = rf"(?m)^\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:[^\s]+|\"[^\"]*\"|'[^']*')\s+)*(?:(?:if|while|until|!)\s+)?(?:bash|source|exec)?\s*{operand}"
        substitution = rf'''(?mx)^\s*[a-z_][a-z0-9_]*\s*=\s*["']?\$\(\s*(?:bash|source|exec)\s+{operand}'''
        return bool(re.search(direct, content, re.I) or
                    re.search(substitution, content, re.I))

    if command_uses(re.escape(helper), path_prefix=True):
        return True
    assignment = None
    for line in content.splitlines():
        candidate = re.match(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(.+?)\s*$", line, re.I)
        if not candidate:
            continue
        value = candidate.group(2)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if re.search(rf"(?:^|/){re.escape(helper)}$", value):
            assignment = candidate
            break
    if not assignment:
        return False
    variable = re.escape(assignment.group(1))
    return command_uses(rf"\${{?{variable}}}?")

def packaged_path(raw, helper, role):
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts:
        raise SystemExit(f"check-helper-reachability: invalid {role}: {helper}: {raw}")
    if rel.as_posix() not in archive_entries:
        raise SystemExit(f"check-helper-reachability: unshipped {role}: {helper}: {raw}")
    path = skill_root / rel
    try:
        path.resolve().relative_to(skill_root.resolve())
    except (OSError, ValueError):
        raise SystemExit(f"check-helper-reachability: invalid {role}: {helper}: {raw}")
    if not path.is_file():
        raise SystemExit(f"check-helper-reachability: missing {role}: {helper}: {raw}")
    return path

implemented_mode_sets = {}
graph_helper = "validate-run-root.sh"
graph_text = (skill_root / "scripts" / graph_helper).read_text(encoding="utf-8")
implemented_mode_sets[graph_helper] = sorted(set(re.findall(r"--graph-[a-z0-9-]+", graph_text)))
rehearsal_helper = "check-authorization-binding.sh"
rehearsal_text = (skill_root / "scripts" / rehearsal_helper).read_text(encoding="utf-8")
rehearsal_mode = "--phase --rehearsal --launch"
rehearsal_code = shell_code(shell_parser_code(rehearsal_text))
rehearsal_arms = all(re.search(rf"(?m)^\s*{re.escape(flag)}\)", rehearsal_code)
                     for flag in rehearsal_mode.split())
transport_match = re.search(
    r'''(?ms)python\s+-\s+"\$phase"\s+"\$rehearsal"\s+"\$launch"\s+<<['"]?([A-Za-z_][A-Za-z0-9_]*)['"]?\s*\n(.*?)^\1\s*$''',
    rehearsal_text,
)

UNKNOWN_CONSTANT = object()
MAX_STATIC_NUMBER = 1_000_000

def bounded_scalar(node):
    """Evaluate only small scalar literals; never allocate candidate containers."""
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, (str, bytes)):
            return value if len(value) <= 256 else UNKNOWN_CONSTANT
        if isinstance(value, (bool, int, float, complex)) or value is None:
            return value if not isinstance(value, (int, float, complex)) or abs(value) <= MAX_STATIC_NUMBER else UNKNOWN_CONSTANT
        return UNKNOWN_CONSTANT
    if isinstance(node, ast.UnaryOp):
        value = bounded_scalar(node.operand)
        if value is UNKNOWN_CONSTANT:
            return value
        try:
            if isinstance(node.op, ast.Not):
                return not value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.USub):
                return -value
        except (TypeError, ValueError, OverflowError):
            pass
        return UNKNOWN_CONSTANT
    if isinstance(node, ast.BinOp):
        left, right = bounded_scalar(node.left), bounded_scalar(node.right)
        if left is UNKNOWN_CONSTANT or right is UNKNOWN_CONSTANT:
            return UNKNOWN_CONSTANT
        if not isinstance(left, (bool, int, float, complex)) or not isinstance(right, (bool, int, float, complex)):
            return UNKNOWN_CONSTANT
        try:
            if isinstance(node.op, ast.Add):
                value = left + right
            elif isinstance(node.op, ast.Sub):
                value = left - right
            elif isinstance(node.op, ast.Mult):
                value = left * right
            elif isinstance(node.op, ast.Div):
                value = left / right
            elif isinstance(node.op, ast.FloorDiv):
                value = left // right
            elif isinstance(node.op, ast.Mod):
                value = left % right
            else:
                return UNKNOWN_CONSTANT
            return value if abs(value) <= MAX_STATIC_NUMBER else UNKNOWN_CONSTANT
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            return UNKNOWN_CONSTANT
    return UNKNOWN_CONSTANT

def compare_scalars(operation, left, right):
    try:
        if isinstance(operation, ast.Eq): return left == right
        if isinstance(operation, ast.NotEq): return left != right
        if isinstance(operation, ast.Is): return left is right
        if isinstance(operation, ast.IsNot): return left is not right
        if isinstance(operation, ast.Lt): return left < right
        if isinstance(operation, ast.LtE): return left <= right
        if isinstance(operation, ast.Gt): return left > right
        if isinstance(operation, ast.GtE): return left >= right
    except (TypeError, ValueError):
        pass
    return UNKNOWN_CONSTANT

def constant_truth(node):
    """Return a statically known truth value without executing source."""
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return bool(node.elts)
    if isinstance(node, ast.Dict):
        return bool(node.keys)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in {"dict", "list", "set", "tuple"}
            and not node.args and not node.keywords):
        return False
    if isinstance(node, ast.BoolOp):
        values = [constant_truth(item) for item in node.values]
        if isinstance(node.op, ast.And):
            if False in values: return False
            return True if all(value is True for value in values) else None
        if True in values: return True
        return False if all(value is False for value in values) else None
    if isinstance(node, ast.Compare):
        left = bounded_scalar(node.left)
        if left is UNKNOWN_CONSTANT:
            return None
        for operation, comparator in zip(node.ops, node.comparators):
            right = bounded_scalar(comparator)
            if right is UNKNOWN_CONSTANT:
                return None
            outcome = compare_scalars(operation, left, right)
            if outcome is UNKNOWN_CONSTANT or not outcome:
                return None if outcome is UNKNOWN_CONSTANT else False
            left = right
        return True
    value = bounded_scalar(node)
    return None if value is UNKNOWN_CONSTANT else bool(value)

def terminating_call(node):
    if not isinstance(node, ast.Call):
        return False
    call = node.func
    if isinstance(call, ast.Name):
        return call.id in {"exit", "quit"}
    return (isinstance(call, ast.Attribute) and isinstance(call.value, ast.Name)
            and (call.value.id, call.attr) in {
                ("sys", "exit"), ("os", "_exit"),
            })

def terminates_route(node):
    if isinstance(node, (ast.Raise, ast.Return)):
        return True
    if isinstance(node, ast.Assert) and constant_truth(node.test) is False:
        return True
    return isinstance(node, ast.Expr) and terminating_call(node.value)

def expression_terminates(node):
    """Return whether evaluating this expression must execute an explicit exit."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Lambda):
        return expression_terminates(node.func.body)
    if isinstance(node, ast.Lambda):
        return False
    if isinstance(node, ast.GeneratorExp):
        return bool(node.generators) and expression_terminates(node.generators[0].iter)
    if terminating_call(node):
        return True
    if isinstance(node, ast.IfExp):
        if expression_terminates(node.test):
            return True
        truth = constant_truth(node.test)
        branch = node.body if truth is True else node.orelse if truth is False else None
        return branch is not None and expression_terminates(branch)
    if isinstance(node, ast.BoolOp):
        for item in node.values:
            if expression_terminates(item):
                return True
            truth = constant_truth(item)
            if isinstance(node.op, ast.And) and truth is not True:
                break
            if isinstance(node.op, ast.Or) and truth is not False:
                break
        return False
    if isinstance(node, ast.Compare):
        if expression_terminates(node.left):
            return True
        left = bounded_scalar(node.left)
        for operation, comparator in zip(node.ops, node.comparators):
            if expression_terminates(comparator):
                return True
            right = bounded_scalar(comparator)
            if left is UNKNOWN_CONSTANT or right is UNKNOWN_CONSTANT:
                break
            outcome = compare_scalars(operation, left, right)
            if outcome is not True:
                break
            left = right
        return False
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
        if not node.generators:
            return False
        generator = node.generators[0]
        if expression_terminates(generator.iter):
            return True
        if (len(node.generators) != 1 or generator.ifs
                or constant_truth(generator.iter) is not True):
            return False
        projections = ([node.elt] if not isinstance(node, ast.DictComp)
                       else [node.key, node.value])
        return any(expression_terminates(item) for item in projections)
    return any(
        expression_terminates(child)
        for child in ast.iter_child_nodes(node)
        if isinstance(child, ast.expr)
    )

def decorator_terminates(node):
    """A decorator lambda is created, then immediately applied to the class/function."""
    return (expression_terminates(node.body) if isinstance(node, ast.Lambda)
            else expression_terminates(node))

def definition_expressions(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        annotations = [
            *(argument.annotation for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
              if argument.annotation is not None),
            *(argument.annotation for argument in [node.args.vararg, node.args.kwarg]
              if argument is not None and argument.annotation is not None),
        ]
        return [
            *node.args.defaults,
            *(item for item in node.args.kw_defaults if item is not None),
            *annotations,
            *([node.returns] if node.returns is not None else []),
        ]
    if isinstance(node, ast.ClassDef):
        return [*node.bases, *(item.value for item in node.keywords)]
    return []

def normal_path_nodes(statements):
    """Return ordered statements on the normal non-exception route."""
    result = []
    for node in statements:
        result.append(node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (any(decorator_terminates(item) for item in node.decorator_list)
                    or any(expression_terminates(item) for item in definition_expressions(node))):
                return result, True
            if isinstance(node, ast.ClassDef):
                _, terminated = normal_path_nodes(node.body)
                if terminated:
                    return result, True
            continue
        if terminates_route(node):
            return result, True
        if isinstance(node, ast.If):
            if expression_terminates(node.test):
                return result, True
            truth = constant_truth(node.test)
            branch = node.orelse if truth is False else node.body if truth is True else []
            nested, terminated = normal_path_nodes(branch)
            result.extend(nested)
            if terminated:
                return result, True
            continue
        if isinstance(node, ast.Try):
            nested, terminated = normal_path_nodes(node.body)
            result.extend(nested)
            if not terminated:
                nested, terminated = normal_path_nodes(node.orelse)
                result.extend(nested)
            final_nodes, final_terminated = normal_path_nodes(node.finalbody)
            result.extend(final_nodes)
            if terminated or final_terminated:
                return result, True
            continue
        if isinstance(node, (ast.With, ast.AsyncWith)):
            if any(expression_terminates(item.context_expr) for item in node.items):
                return result, True
            nested, terminated = normal_path_nodes(node.body)
            result.extend(nested)
            if terminated:
                return result, True
            continue
        if isinstance(node, ast.While):
            if expression_terminates(node.test):
                return result, True
            truth = constant_truth(node.test)
            if truth is False:
                nested, terminated = normal_path_nodes(node.orelse)
                result.extend(nested)
                if terminated:
                    return result, True
            elif truth is True:
                nested, _ = normal_path_nodes(node.body)
                result.extend(nested)
                return result, True
            continue
        if isinstance(node, (ast.For, ast.AsyncFor)):
            if expression_terminates(node.iter):
                return result, True
            continue
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr) and expression_terminates(child):
                return result, True
    return result, False

def statement_call(node):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        return node.value
    if (isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.value, ast.Call)):
        return node.value
    return None

def target_binds(target, name):
    if isinstance(target, ast.Name):
        return target.id == name
    if isinstance(target, (ast.Tuple, ast.List)):
        return any(target_binds(item, name) for item in target.elts)
    return False

def binds_name(node, name):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name == name
    if isinstance(node, ast.Assign):
        return any(target_binds(target, name) for target in node.targets)
    if isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.For, ast.AsyncFor)):
        return target_binds(node.target, name)
    if isinstance(node, ast.Delete):
        return any(target_binds(target, name) for target in node.targets)
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return any(item.optional_vars is not None and target_binds(item.optional_vars, name)
                   for item in node.items)
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return any((alias.asname or alias.name.split(".")[0]) == name for alias in node.names)
    return any(
        isinstance(item, ast.NamedExpr) and target_binds(item.target, name)
        for item in ast.walk(node)
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda))
    )

def is_launch_subprocess(node):
    call = statement_call(node)
    if not (call and isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "completed"
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "subprocess" and call.func.attr == "run"
            and call.args and isinstance(call.args[0], ast.Subscript)
            and isinstance(call.args[0].value, ast.Name)
            and call.args[0].value.id == "launch"):
        return False
    slice_node = call.args[0].slice
    return isinstance(slice_node, ast.Constant) and slice_node.value == "argv"

def has_launch_subprocess(body):
    if not body:
        return False
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return False
    live, _ = normal_path_nodes(tree.body)
    return any(is_launch_subprocess(node) for node in live)

def has_mediated_execution(body):
    """Require executable bridge -> thread start/join -> stub-run edges."""
    if not body:
        return False
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return False

    def is_call(node, base, attribute):
        call = statement_call(node)
        return (call is not None and isinstance(node, ast.Expr)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == base and call.func.attr == attribute)

    live, _ = normal_path_nodes(tree.body)
    bridges = []
    thread_bindings = []
    starts = []
    launches = []
    joins = []
    current_stub_function = None
    for position, node in enumerate(live):
        if binds_name(node, "run_bounded_stub"):
            current_stub_function = (
                node if isinstance(node, ast.FunctionDef)
                and node.name == "run_bounded_stub" else None
            )
        if is_call(node, "bridge_path", "write_text"):
            bridges.append(position)
        if is_call(node, "mediator_thread", "start"):
            starts.append(position)
        if is_launch_subprocess(node):
            launches.append(position)
        if is_call(node, "mediator_thread", "join"):
            joins.append(position)
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "mediator_thread"):
            continue
        value = node.value
        if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                and isinstance(value.func.value, ast.Name)
                and value.func.value.id == "threading" and value.func.attr == "Thread"):
            continue
        target_bound = any(keyword.arg == "target"
                           and isinstance(keyword.value, ast.Name)
                           and keyword.value.id == "run_bounded_stub"
                           for keyword in value.keywords)
        if target_bound and current_stub_function is not None:
            thread_bindings.append((position, current_stub_function))
    if not all(len(items) == 1 for items in (bridges, thread_bindings, starts, launches, joins)):
        return False
    bridge_position = bridges[0]
    thread_position, stub_function = thread_bindings[0]
    start_position = starts[0]
    launch_position = launches[0]
    join_position = joins[0]
    if any(binds_name(node, "mediator_thread")
           for node in live[thread_position + 1:join_position]):
        return False
    stub_live, _ = normal_path_nodes(stub_function.body if stub_function else [])
    stub_runs = bool(stub_function) and any(
        isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "result"
        and (call := statement_call(node)) is not None
        and isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name) and call.func.value.id == "subprocess"
        and call.func.attr == "run" and call.args
        and isinstance(call.args[0], ast.Name) and call.args[0].id == "command"
        for node in stub_live
    )
    positions = (
        bridge_position, thread_position, start_position,
        launch_position, join_position,
    )
    return (
        stub_runs and list(positions) == sorted(positions)
    )

transport_body = transport_match.group(2) if transport_match else ""
rehearsal_transport = (
    has_launch_subprocess(transport_body)
    and has_mediated_execution(transport_body)
)
if rehearsal_arms and rehearsal_transport:
    implemented_mode_sets[rehearsal_helper] = [rehearsal_mode]
else:
    implemented_mode_sets[rehearsal_helper] = []

for helper, mode in mode_rows:
    if helper not in helpers or mode not in implemented_mode_sets.get(helper, []):
        raise SystemExit(
            f"check-helper-reachability: mode applicability not implemented: {helper} {mode}"
        )
for helper, implemented_modes in implemented_mode_sets.items():
    declared_modes = sorted(mode for row_helper, mode in mode_rows if row_helper == helper)
    missing_modes = sorted(set(implemented_modes) - set(declared_modes))
    if missing_modes:
        raise SystemExit(
            "check-helper-reachability: missing mode applicability rows: "
            + ", ".join(f"{helper} {mode}" for mode in missing_modes)
        )

mode_owner = "\n".join(
    line for line in contract_text.splitlines()
    if not line.startswith(("helper-route: ", "helper-mode: "))
)
for helper, mode in mode_rows:
    row = mode_rows[(helper, mode)]
    mode_flags = mode.split()
    mode_args = row["arguments"].split()
    mode_command = f"{mode} {row['arguments']}"
    if len(mode_flags) > 1:
        if len(mode_flags) != len(mode_args):
            raise SystemExit(
                f"check-helper-reachability: mode argument arity mismatch: {helper} {mode}"
            )
        mode_command = " ".join(
            f"{flag} {argument}" for flag, argument in zip(mode_flags, mode_args)
        )
    if not arguments_are_anchored(mode_command, helper, mode_owner):
        raise SystemExit(
            f"check-helper-reachability: mode arguments absent: {helper} {mode}"
        )
    if not field_is_anchored(row["boundary"], mode_owner.lower()):
        raise SystemExit(
            f"check-helper-reachability: mode boundary absent: {helper} {mode}"
        )
    mode_caller = row["caller"]
    if mode_caller != "-":
        caller_path = packaged_path(mode_caller, helper, "mode caller")
        caller_content = shell_code(caller_path.read_text(encoding="utf-8"))
        if not caller_invokes(helper, caller_content):
            raise SystemExit(
                f"check-helper-reachability: mode caller does not invoke {helper}: {mode_caller}"
            )
        mode_flags = r"\s+" + r"\s+".join(re.escape(flag) + r"\s+[^\s]+" for flag in mode.split())
        if not re.search(re.escape(helper) + r'["\']?' + mode_flags, caller_content):
            raise SystemExit(
                f"check-helper-reachability: mode caller does not invoke exact mode: {helper} {mode}"
            )

for helper in helpers:
    row = rows[helper]
    class_code = row["class"]
    if class_code not in class_names:
        raise SystemExit(
            f"check-helper-reachability: invalid applicability class {class_code} for {helper}"
        )
    applicability = class_names[class_code]
    for field in ("trigger", "arguments", "boundary"):
        if not row[field] or row[field] == "-":
            raise SystemExit(f"check-helper-reachability: empty {field} for {helper}")

    owner_text = owner_aliases.get(row["owner"], row["owner"])
    owner_rel = Path(owner_text)
    own_rel = Path("scripts") / helper
    if owner_rel == own_rel:
        raise SystemExit(
            f"check-helper-reachability: dispatch owner cannot be the helper itself: {helper}"
        )
    owner = packaged_path(owner_text, helper, "dispatch owner")
    owner_lines = owner.read_text(encoding="utf-8").splitlines()
    non_route_lines = [line for line in owner_lines if not line.startswith(("helper-route: ", "helper-mode: "))]
    owner_content = "\n".join(non_route_lines)
    helper_lines = [index for index, line in enumerate(non_route_lines) if helper in line]
    if not helper_lines:
        raise SystemExit(
            f"check-helper-reachability: dispatch owner does not name helper {helper}: {owner_text}"
        )
    if applicability == "required-procedural":
        action = r"(?:bash|run|supply|dispatch(?:es)?|invoke|enforce|requires?|claim(?: it)? with)"
        contexts = ["\n".join(non_route_lines[max(0, i - 4):i + 5])
                    for i in helper_lines]
        procedural = [context for context in contexts if re.search(
            rf"(?:{action}.{{0,120}}{re.escape(helper)}|{re.escape(helper)}.{{0,120}}{action})",
            context, re.I | re.S
        )]
        if not procedural:
            raise SystemExit(
                f"check-helper-reachability: procedural route absent: {helper}"
            )
        field_contexts = [context.lower().replace("artefact", "artifact")
                          .replace(helper.lower(), "") for context in procedural]
        for field in ("trigger", "boundary"):
            if not any(field_is_anchored(row[field], context) for context in field_contexts):
                raise SystemExit(
                    f"check-helper-reachability: unanchored {field}: {helper}: {row[field]}"
                )
        if not any(arguments_are_anchored(row["arguments"], helper, context)
                   for context in procedural):
            raise SystemExit(
                f"check-helper-reachability: unanchored arguments: {helper}: {row['arguments']}"
            )
        if not any(
            field_is_anchored(row["trigger"], context.lower().replace("artefact", "artifact")
                              .replace(helper.lower(), ""))
            and field_is_anchored(row["boundary"], context.lower().replace("artefact", "artifact")
                                  .replace(helper.lower(), ""))
            and arguments_are_anchored(row["arguments"], helper, context)
            for context in procedural
        ):
            raise SystemExit(
                f"check-helper-reachability: route fields do not co-occur: {helper}"
            )
    if applicability in {"optional-advisory", "standalone-diagnostic"}:
        advisory_text = " ".join(
            (row["trigger"], row["arguments"], row["boundary"])
        )
        if mandatory_re.search(advisory_text):
            raise SystemExit(
                f"check-helper-reachability: advisory/standalone row implies mandatory enforcement: {helper}"
            )
        if any(mandatory_re.search(" ".join(non_route_lines[max(0, i - 1):i + 2]))
               for i in helper_lines):
            raise SystemExit(
                f"check-helper-reachability: advisory owner overclaim: {helper}"
            )

    caller_rel = owner_aliases.get(row["caller"], row["caller"])
    if applicability in {"automatic", "internal-library"}:
        if caller_rel == "-":
            raise SystemExit(
                f"check-helper-reachability: {applicability} helper lacks caller: {helper}"
            )
        caller_path = packaged_path(caller_rel, helper, "caller")
        if not (Path(caller_rel).as_posix().startswith("scripts/") and
                Path(caller_rel).suffix == ".sh"):
            raise SystemExit(
                f"check-helper-reachability: caller is not a shipped script: {helper}: {caller_rel}"
            )
        caller_content = caller_path.read_text(encoding="utf-8")
        if not caller_invokes(helper, caller_content):
            raise SystemExit(
                f"check-helper-reachability: caller does not invoke {helper}: {caller_rel}"
            )
    elif caller_rel != "-":
        raise SystemExit(
            f"check-helper-reachability: nonautomatic helper declares caller: {helper}"
        )

print(
    "HELPER_REACHABILITY=PASS "
    f"population={len(helpers)} examined={len(rows)} "
    f"modes={len(mode_rows)}/{sum(len(modes) for modes in implemented_mode_sets.values())} "
    "enumeration=build-release-asset.required_archive"
)
PY
