"""Read pinned public inputs and project Python source as bytes. Import performs no I/O."""

import __future__
import ast
import builtins
from collections import defaultdict
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import symtable
from types import MappingProxyType


class Refusal(ValueError):
    """The supplied input or projection cannot satisfy the declared contract."""


@dataclass(frozen=True)
class InputBundle:
    baseline: Mapping[str, bytes]
    owners: Mapping[str, bytes]
    full_before: Mapping[str, bytes]
    composer: bytes
    runtime: bytes
    reverse_map: bytes
    generator: bytes


@dataclass(frozen=True)
class ProjectionBasis:
    roots: tuple[str, ...]
    supplied: tuple[str, ...]
    declarations: tuple[str, ...]
    external_names: tuple[str, ...]
    functions: Mapping[str, str]
    source_pin: Mapping
    projection_pin: Mapping
    projection: bytes
    compiler_flags: int
    runtime_pin: Mapping


_GROUPS = ("baseline", "owners", "full_before")
_SINGLETONS = ("composer", "runtime", "reverse_map", "generator")
_OWNERS = frozenset(("g3_receiving.py", "host_utility.py", "nss_configuration.py",
                     "operation.py", "proof_consumer.py", "run.py"))
_FAMILIES = frozenset(("compose", "g3", "profile", "proof", "run"))
# CurrentSources.module in this exact runtime inherits postponed annotations.
_RUNTIME_PIN = MappingProxyType({
    "bytes": 38161, "sha256": "46a3e27dccb0b30dc75b4d20b7dca659ec5f4f8ae2a3e04c9ec175e577d3b743",
})
_COMPILER_FLAGS = __future__.annotations.compiler_flag
# Common namespace from CurrentSources.module; family-specific bindings must be supplied.
_RUNTIME_NAMES = frozenset(("ast", "hashlib", "json", "re", "base64", "datetime",
                            "io", "zipfile", "stat"))
_HEADER = b"# Exact bounded source projection; source module is never imported.\n"


def _pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _json(raw):
    if type(raw) is not bytes:
        raise Refusal("JSON input must be bytes")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Refusal(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise Refusal(f"non-finite JSON constant: {value}")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refusal("invalid UTF-8 JSON") from exc


def _path(value, *, absolute):
    if type(value) is not str or not value or "\x00" in value:
        raise Refusal("invalid path")
    path = Path(value)
    if (path.is_absolute() != absolute or str(path) != value or value.startswith("//")
            or not path.name or ".." in path.parts):
        raise Refusal(f"path alias or wrong path kind: {value}")
    return path


def _contract(spec, locations):
    roles = set(_GROUPS + _SINGLETONS)
    if type(spec) is not dict or set(spec) != roles:
        raise Refusal("wrong pin-table roles")
    if type(locations) is not dict or set(locations) != roles | {"destination"}:
        raise Refusal("wrong location roles")
    paths = {role: _path(name, absolute=True) for role, name in locations.items()}
    path_list = list(paths.values())
    for index, path in enumerate(path_list):
        for other in path_list[:index]:
            if path.is_relative_to(other) or other.is_relative_to(path):
                raise Refusal("aliased or overlapping input/output paths")
    if any(type(spec[group]) is not dict for group in _GROUPS):
        raise Refusal("expected group member tables")
    if len(spec["baseline"]) != 175 or set(spec["owners"]) != _OWNERS or set(spec["full_before"]) != _FAMILIES:
        raise Refusal("wrong declared input population")
    entries = {}
    group_members = {}
    for group in _GROUPS:
        members = set()
        for name, descriptor in spec[group].items():
            member = _path(name + ".py" if group == "full_before" else name, absolute=False)
            members.add(member)
            entries[(group, name)] = (paths[group] / member, descriptor)
        group_members[paths[group]] = frozenset(members)
    for role in _SINGLETONS:
        entries[(role, None)] = (paths[role], spec[role])
    for _, descriptor in entries.values():
        if (type(descriptor) is not dict or set(descriptor) != {"bytes", "sha256"}
                or type(descriptor["bytes"]) is not int or descriptor["bytes"] < 0
                or type(descriptor["sha256"]) is not str
                or re.fullmatch("[0-9a-f]{64}", descriptor["sha256"]) is None):
            raise Refusal("invalid byte descriptor")
    if spec["generator"]["sha256"] == "45138b8e537a7a7f24b6b6ce68f0978b42cd5f44d5b3f4bb6e37997f58c2b3f1":
        raise Refusal("historical missing generator cannot fill the new generator role")
    return entries, group_members, paths["destination"]


@contextmanager
def _directory(path):
    """Walk from the filesystem root, refusing symlinks at every component."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        yield descriptor
    finally:
        os.close(descriptor)


def _observation(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _stat(path):
    with _directory(path.parent) as directory:
        return os.stat(path.name, dir_fd=directory, follow_symlinks=False)


def _absent(destination):
    try:
        _stat(destination)
    except FileNotFoundError:
        return
    raise Refusal("destination already exists")


def _inventory(root, members):
    # Enumerate only the exact directories implied by the public member table.
    expected = defaultdict(set)
    for member in members:
        for child in (member, *member.parents):
            if child != Path("."):
                expected[child.parent].add(child.name)
    observations = {}
    for parent, names in expected.items():
        with _directory(root / parent) as directory, os.scandir(directory) as children:
            observations[parent] = _observation(os.fstat(directory))
            seen = set()
            for child in children:
                if child.name not in names:
                    raise Refusal("undeclared physical member")
                seen.add(child.name)
            if seen != names:
                raise Refusal("missing physical member")
    return observations


def _read_member(path, pin):
    with _directory(path.parent) as directory:
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        descriptor = os.open(path.name, flags, dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise Refusal("non-regular or hard-linked input")
        if info.st_size != pin["bytes"]:
            raise Refusal("changed input size")
        chunks = bytearray()
        while len(chunks) < info.st_size:
            block = os.read(descriptor, min(64 * 1024, info.st_size - len(chunks)))
            if not block:
                raise Refusal("changed input length during read")
            chunks.extend(block)
        observed = _observation(info)
        if _observation(os.fstat(descriptor)) != observed:
            raise Refusal("input changed during read")
        raw = bytes(chunks)
        if _pin(raw) != pin:
            raise Refusal("changed input bytes")
        return raw, observed
    finally:
        os.close(descriptor)


def receive_inputs(spec, locations):
    """Receive two explicit UTF-8 JSON documents; return only closed, immutable data."""
    entries, trees, destination = _contract(_json(spec), _json(locations))
    grouped = {role: {} for role in _GROUPS}
    singles = {}
    observations = {}
    identities = set()
    try:
        _absent(destination)
        inventories = {root: _inventory(root, members) for root, members in trees.items()}
        for (role, member), (path, pin) in entries.items():
            raw, observed = _read_member(path, pin)
            if observed[:2] in identities:
                raise Refusal("duplicate physical input identity")
            identities.add(observed[:2])
            observations[path] = observed
            if path.suffix == ".json" or role == "reverse_map":
                _json(raw)
            if member is None:
                singles[role] = raw
            else:
                grouped[role][member] = raw
        for root, members in trees.items():
            if _inventory(root, members) != inventories[root]:
                raise Refusal("changed closing directory observation")
        for path, before in observations.items():
            if _observation(_stat(path)) != before:
                raise Refusal("changed closing input observation")
        _absent(destination)
    except OSError as exc:
        raise Refusal(f"input/output path observation failed: {exc.strerror}") from exc
    return InputBundle(**{role: MappingProxyType(data) for role, data in grouped.items()}, **singles)


def _names(names, label):
    if not isinstance(names, (tuple, list)) or any(type(name) is not str or not name.isidentifier() for name in names):
        raise Refusal(f"invalid {label} names")
    if len(set(names)) != len(names):
        raise Refusal(f"duplicate {label} names")
    return tuple(names)


def _targets(node):
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Tuple):
        names = []
        for element in node.elts:
            names.extend(_targets(element))
        return tuple(names)
    raise Refusal("unsupported assignment target")


def _declared(node):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return (node.name,)
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        try:
            return _targets(node.targets[0])
        except Refusal:
            pass
    return ()


class _SymbolReads(ast.NodeTransformer):
    """Expose implicit reads and comprehension-local targets in a separate analysis tree."""

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            # symtable marks a plain augmented target as assigned. It also reads
            # the old value in this same lexical scope.
            old = ast.Name(id=node.target.id, ctx=ast.Load())
            node.value = ast.Tuple(elts=[old, node.value], ctx=ast.Load())
        return node

    def visit_ListComp(self, node):
        self.generic_visit(node)
        return ast.GeneratorExp(elt=node.elt, generators=node.generators)

    visit_SetComp = visit_ListComp

    def visit_DictComp(self, node):
        self.generic_visit(node)
        pair = ast.Tuple(elts=[node.key, node.value], ctx=ast.Load())
        return ast.GeneratorExp(elt=pair, generators=node.generators)


def _symbols(text, *, target_context=True):
    try:
        tree = ast.parse(text)
        if any(isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.AugAssign))
               for n in ast.walk(tree)):
            text = ast.unparse(_SymbolReads().visit(tree))
        if target_context:
            # symtable has no compiler-flags argument. Only this analysis copy
            # receives the directive; projected bytes retain the historical header.
            text = "from __future__ import annotations\n" + text
        return symtable.symtable(text, "<source projection>", "exec")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise Refusal("unsupported source syntax") from exc


class _Module:
    def __init__(self, raw):
        if type(raw) is not bytes:
            raise Refusal("source must be UTF-8 bytes")
        self.raw = raw
        try:
            self.tree = ast.parse(raw.decode("utf-8"))
        except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
            raise Refusal("invalid UTF-8 Python source") from exc
        self.lines = raw.splitlines(keepends=True)
        self.offsets = [0]
        for line in self.lines:
            self.offsets.append(self.offsets[-1] + len(line))
        self.bindings = defaultdict(list)
        self.names = {}
        for node in self.tree.body:
            accepted = _declared(node)
            # Index unsupported bindings too, so they cannot hide a duplicate or
            # be accidentally classified as a builtin or a free external name.
            table = _symbols(self.segment(node).decode("utf-8"), target_context=False)
            identifiers = [s.get_name() for s in table.get_symbols()
                           if s.is_assigned() or s.is_imported() or s.is_namespace()]
            if isinstance(node, ast.ImportFrom) and any(a.name == "*" for a in node.names):
                raise Refusal("unsupported wildcard import")
            bound = set(identifiers) | set(accepted)
            self.names[node] = accepted if bound == set(accepted) else ()
            for name in bound:
                self.bindings[name].append(node)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported = set()
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if name in imported:
                        self.bindings[name].append(node)
                    imported.add(name)

    def segment(self, node):
        line = node.lineno
        column = node.col_offset
        decorators = getattr(node, "decorator_list", ())
        if decorators:
            line = decorators[0].lineno
            while line > 0 and self.lines[line - 1][column:column + 1] != b"@":
                line -= 1
            if line == 0:
                raise Refusal("unsupported decorator source span")
        start = self.offsets[line - 1] + column
        end = self.offsets[node.end_lineno - 1] + node.end_col_offset
        return self.raw[start:end]

    def resolve(self, name):
        choices = self.bindings.get(name, ())
        if len(choices) > 1:
            raise Refusal(f"ambiguous module binding: {name}")
        return choices[0] if choices else None

    def declaration(self, name):
        node = self.resolve(name)
        if node is None or name not in self.names[node]:
            raise Refusal(f"missing or unsupported declaration: {name}")
        names = self.names[node]
        if len(set(names)) != len(names):
            raise Refusal(f"ambiguous duplicate assignment target: {name}")
        for sibling in names:
            self.resolve(sibling)
        if any(isinstance(child, (ast.Import, ast.ImportFrom)) for child in ast.walk(node)):
            raise Refusal(f"import in selected declaration: {name}")
        return node

    def render(self, nodes):
        ordered = [node for node in self.tree.body if node in nodes]
        payload = _HEADER + b"\n\n".join(self.segment(node) for node in ordered) + b"\n"
        projected = ast.parse(payload.decode("utf-8")).body
        if [ast.dump(n) for n in projected] != [ast.dump(n) for n in ordered]:
            raise Refusal("selected declaration AST changed")
        return ordered, payload


def project_exact(raw, declarations):
    """Apply the fixed historical segment recipe using an explicit declaration list."""
    names = _names(declarations, "declaration")
    if not names:
        raise Refusal("empty declaration list")
    module = _Module(raw)
    return module.render({module.declaration(name) for name in names})[1]


def _references(table):
    names = {s.get_name() for s in table.get_symbols() if s.is_global() and s.is_referenced()}
    for child in table.get_children():
        names.update(_references(child))
    return names


def _class_fallbacks(root):
    # A class namespace uses LOAD_NAME: a local read can still reach the module
    # when that class has not bound its local yet. Functions use lexical locals.
    fallback = set()
    for node in ast.walk(root):
        if not isinstance(node, ast.ClassDef):
            continue
        class_table = next(t for t in _symbols(ast.unparse(node)).get_children()
                           if t.get_type() == "class" and t.get_name() == node.name)
        local_names = {s.get_name() for s in class_table.get_symbols() if s.is_local()}
        bound = {"__module__", "__qualname__"}
        for statement in node.body:
            # Only immediate definition-time references run in the class body.
            # ast.unparse removes class indentation; emitted text remains original.
            table = _symbols(ast.unparse(statement))
            references = {s.get_name() for s in table.get_symbols() if s.is_referenced()}
            locals_in_class = {s.get_name() for s in table.get_symbols() if s.is_assigned()}
            if isinstance(statement, (ast.If, ast.For, ast.While, ast.Try, ast.With,
                                      ast.AsyncFor, ast.AsyncWith, ast.TryStar, ast.Match)):
                if locals_in_class:
                    raise Refusal("unsupported conditional class binding")
            fallback.update((references & local_names) - bound)
            if isinstance(statement, ast.Delete):
                bound.difference_update(locals_in_class)
            elif not (isinstance(statement, ast.AnnAssign) and statement.value is None):
                bound.update(locals_in_class)
    return fallback


def _target_compiler_check(raw):
    # Match the pinned runtime's flags explicitly, independent of this tool's
    # own module/compiler settings. Only compilation metadata is inspected.
    try:
        unit = compile(raw, "<projection source>", "exec", flags=_COMPILER_FLAGS, dont_inherit=True)
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise Refusal("unsupported target compiler context") from exc
    for name in __future__.all_feature_names:
        flag = getattr(__future__, name).compiler_flag
        if (unit.co_flags & flag) != (_COMPILER_FLAGS & flag):
            raise Refusal(f"source compiler feature unavailable in projection: {name}")


def _runtime_nodes(node):
    """Visit executable source expressions, skipping postponed annotation expressions."""
    yield node
    for field, value in ast.iter_fields(node):
        if field in ("annotation", "returns"):
            continue
        children = value if isinstance(value, list) else (value,)
        for child in children:
            if isinstance(child, ast.AST):
                yield from _runtime_nodes(child)


def _shadows_globals(table):
    if "globals" in table.get_identifiers():
        entry = table.lookup("globals")
        if entry.is_local() or entry.is_assigned() or entry.is_free() or entry.is_imported():
            return True
    return any(_shadows_globals(child) for child in table.get_children())


def _namespace_keys(node, table, module, supplied):
    # An explicitly named entry in the module dictionary is independent of
    # local variables and cannot fall back to a builtin absent from that dict.
    nodes = tuple(_runtime_nodes(node))
    allowed = set()
    keys = set()
    for item in nodes:
        if not isinstance(item, ast.Subscript) or not isinstance(item.value, ast.Call):
            continue
        call = item.value
        if not isinstance(call.func, ast.Name) or call.func.id != "globals":
            continue
        key = item.slice
        if (call.args or call.keywords or not isinstance(item.ctx, ast.Load)
                or not isinstance(key, ast.Constant) or type(key.value) is not str
                or not key.value.isidentifier() or key.value.startswith("__")):
            raise Refusal("unsupported module namespace key or mutation")
        allowed.add(call.func)
        keys.add(key.value)
    for item in nodes:
        if isinstance(item, ast.Name) and item.id in ("globals", "locals", "vars") and item not in allowed:
            raise Refusal("unsupported namespace access or copy")
        if isinstance(item, ast.Attribute) and item.attr in ("__globals__", "globals", "FunctionType"):
            raise Refusal("unsupported namespace access or function rebinding")
        if (isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
                and item.func.id == "getattr" and len(item.args) >= 2
                and isinstance(item.args[1], ast.Constant) and item.args[1].value == "__globals__"):
            raise Refusal("unsupported indirect module namespace access")
    if keys and ("globals" in supplied or "globals" in module.bindings or _shadows_globals(table)):
        raise Refusal("shadowed module namespace builtin")
    return keys


def _function_hashes(ordered):
    result = {}

    def visit(node, parent):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parent = parent + "." + node.name if parent else node.name
            if parent in result:
                raise Refusal(f"ambiguous function/class name: {parent}")
            result[parent] = hashlib.sha256(ast.dump(node).encode()).hexdigest()
        for child in ast.iter_child_nodes(node):
            visit(child, parent)

    for node in ordered:
        visit(node, "")
    return MappingProxyType(result)


def projection_basis(raw, roots, supplied):
    """Compute the source-ordered closure; resolve names without evaluating source."""
    roots = _names(roots, "root")
    supplied = _names(supplied, "supplied")
    if not roots or set(roots).intersection(supplied):
        raise Refusal("empty roots or root also supplied")
    module = _Module(raw)
    _target_compiler_check(raw)
    todo = list(roots)
    selected = set()
    external = set()
    while todo:
        root = todo.pop()
        node = module.declaration(root)
        if node in selected:
            continue
        if set(module.names[node]).intersection(supplied):
            raise Refusal("selected tuple would redefine a supplied name")
        selected.add(node)
        table = _symbols(module.segment(node).decode("utf-8"))
        keys = _namespace_keys(node, table, module, supplied)
        dependencies = keys | _references(table) | _class_fallbacks(node)
        for name in sorted(dependencies):
            if name in supplied:
                external.add(name)
                continue
            binding = module.resolve(name)
            if binding is not None and name in module.names[binding]:
                todo.append(name)
                continue
            if binding is None and (name in _RUNTIME_NAMES or (name not in keys and name in vars(builtins))):
                external.add(name)
                continue
            if isinstance(binding, ast.Import) and name in _RUNTIME_NAMES and any(
                    alias.name == name and (alias.asname is None or alias.asname == name)
                    for alias in binding.names):
                external.add(name)
                continue
            raise Refusal(f"unexplained or unsupported external: {name}")
    ordered, payload = module.render(selected)
    declarations = tuple(name for node in ordered for name in module.names[node])
    return ProjectionBasis(roots, supplied, declarations, tuple(sorted(external)),
                           _function_hashes(ordered), MappingProxyType(_pin(raw)),
                           MappingProxyType(_pin(payload)), payload, _COMPILER_FLAGS, _RUNTIME_PIN)
