"""Source-only test adapter. It never loads a private selection or a native store."""
import ast
import hashlib
import json
import os
from pathlib import Path
import types

REPO = None
SCRATCH = None
NATIVE = None
ROUTE = None
_MODULES = {}
PUBLIC_OWNERS = ('codex-recovery-native-reader.py', 'compaction-source-owner-codex-app.py',
    'compaction-result-observation.py', 'compaction-audit-pending.py',
    'bounded_file_custody.py', 'bounded_native_reader.py', 'bounded_source_owner.py')
CORE_FILES = ('skills/implementaudit/SKILL.md', 'skills/audit-state/SKILL.md',
    'skills/implementaudit/references/child-agents.md', 'skills/implementaudit/references/continuity.md')


def configure(repo_root, scratch):
    global REPO, SCRATCH, NATIVE, ROUTE
    REPO = Path(repo_root).resolve(strict=True)
    SCRATCH = Path(scratch).resolve(strict=True)
    NATIVE = REPO / 'source-peers/native-runtime/skills/implementaudit/scripts'
    ROUTE = REPO / 'source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py'
    for name in PUBLIC_OWNERS:
        if not (NATIVE / name).is_file():
            raise ValueError('public native peer missing: ' + name)
    if not ROUTE.is_file(): raise ValueError('public route peer missing')
    _MODULES.clear()


def source_path(name):
    if REPO is None: raise ValueError('test runtime requires --repo-root')
    if name == 'route-transaction.py': return ROUTE
    if name not in PUBLIC_OWNERS: raise ValueError('unselected source requested')
    return NATIVE / name


def source_text(name):
    path = source_path(name)
    size = path.stat().st_size
    if not 0 < size <= 512 * 1024: raise ValueError('source byte bound exceeded')
    with path.open('rb') as stream: raw = stream.read(size)
    if len(raw) != size: raise ValueError('source changed during test read')
    return raw.decode('utf-8')


def functions(name, selected, env):
    """Execute selected real owner definitions with explicitly supplied mocks."""
    nodes = [node for node in ast.parse(source_text(name)).body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in selected]
    if {node.name for node in nodes} != set(selected):
        raise ValueError('selected public function absent: ' + name)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source_path(name)), 'exec'), env)
    return env


def source_profile_constants():
    """Read the real profile declarations without importing an owner or store."""
    tree = ast.parse(source_text('compaction-result-observation.py'))
    names = ('NONPROTECTED_PROFILE', 'OWNED_STDIO_PROFILE')
    values = {}
    for name in names:
        nodes = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
        if len(nodes) != 1 or not isinstance(nodes[0].value, ast.Constant) or type(nodes[0].value.value) is not str:
            raise ValueError('profile literal declaration changed: ' + name)
        values[name] = nodes[0].value.value
    families = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'SOURCE_PROFILES']
    if (len(families) != 1 or not isinstance(families[0].value, ast.Tuple)
            or [n.id if isinstance(n, ast.Name) else None for n in families[0].value.elts] != list(names)):
        raise ValueError('source profile family declaration changed')
    values['SOURCE_PROFILES'] = tuple(values[name] for name in names)
    return values


def load(name):
    if name in _MODULES: return _MODULES[name]
    if name not in PUBLIC_OWNERS or name == 'compaction-audit-pending.py':
        raise ValueError('only inert public modules may be imported; use selected definitions for pending')
    source = source_text(name)
    if name == 'compaction-source-owner-codex-app.py':
        bindings = [node for node in ast.parse(source).body if isinstance(node, ast.Assign) and
            any(isinstance(target, ast.Name) and target.id == 'NONPROTECTED_SELECTION_PIN' for target in node.targets)]
        if len(bindings) != 1 or not isinstance(bindings[0].value, ast.Constant) or bindings[0].value.value is not None:
            raise ValueError('private source selection is forbidden in source-only regression')
    module = types.ModuleType('_public_native_test_' + name.replace('.', '_'))
    module.__file__ = str(source_path(name))
    exec(compile(source, module.__file__, 'exec', dont_inherit=True), module.__dict__)
    if name in ('bounded_native_reader.py', 'bounded_source_owner.py'):
        module.custody = load('bounded_file_custody.py')
    _MODULES[name] = module
    return module


def source_api():
    """Synthetic fixture adapter replacing the former private investigation wrapper."""
    owner = load('bounded_source_owner.py'); reader = load('bounded_native_reader.py')
    selection = {'root_thread_id': 'fixture-root', 'cli_version': '0.163.0-alpha.10.2',
        'native_version': 'codex-cli 0.163.0-alpha.10.2', 'cwd': str(SCRATCH)}
    return types.SimpleNamespace(owner=owner, reader=reader, ROOT_ID=selection['root_thread_id'],
        CLI_VERSION=selection['cli_version'], CWD=SCRATCH, ROOT_SOURCE=SCRATCH / 'fixture-root.jsonl',
        public_record=owner.public_record, physical=owner.physical, read_public=owner.read_public,
        bind_public=owner.bind_public, same_selection=owner.same_selection,
        validate_relation=lambda *args: owner.validate_relation(selection, *args))


def source_pins():
    values = {name: hashlib.sha256(source_text(name).encode()).hexdigest()
        for name in (*PUBLIC_OWNERS, 'route-transaction.py')}
    values['host-session-binding.py'] = hashlib.sha256(bounded_bytes(NATIVE / 'host-session-binding.py')).hexdigest()
    values.update({name: hashlib.sha256(bounded_bytes(REPO / name)).hexdigest() for name in CORE_FILES})
    return values


def bounded_bytes(path):
    size = path.stat().st_size
    if not 0 < size <= 512 * 1024: raise ValueError('fixture dependency byte bound exceeded')
    with path.open('rb') as stream: raw = stream.read(size)
    if len(raw) != size: raise ValueError('fixture dependency changed during read')
    return raw


def canonical_unbound_fixture(directory):
    """Materialize public dependencies only; deliberately leave RT absent first."""
    root = Path(directory)
    scripts = root / 'skills/implementaudit/scripts'; scripts.mkdir(parents=True)
    for name in PUBLIC_OWNERS: (scripts / name).write_bytes(bounded_bytes(source_path(name)))
    for name in ('compaction-prior-protocol.py', 'compaction-prior-mcp.py'):
        (scripts / name).write_bytes(bounded_bytes(NATIVE / name))
    (scripts / 'host-session-binding.py').write_bytes(bounded_bytes(NATIVE / 'host-session-binding.py'))
    for name in CORE_FILES:
        target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bounded_bytes(REPO / name))
    module = types.ModuleType('_owned_unbound_pending_fixture')
    module.__file__ = str(scripts / 'compaction-audit-pending.py')
    exec(compile(bounded_bytes(Path(module.__file__)), module.__file__, 'exec', dont_inherit=True), module.__dict__)
    return module, scripts


def guard_ast_digest(node):
    """Ignore locations and newly added empty generic-type metadata only."""
    def stable(value):
        if isinstance(value, ast.AST):
            return [type(value).__name__, {key: stable(item) for key, item in ast.iter_fields(value)
                if key != 'type_params' or item}]
        if isinstance(value, list): return [stable(item) for item in value]
        return value
    return hashlib.sha256(json.dumps(stable(node), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def ordinary_cli_definition_closure(text):
    """Check actual ordinary CLI dependencies, not unrelated imported-only APIs.

    The only excluded call is the exact fresh-profile branch of the pinned
    provider guard. Both pinned CLI entries obtain their runtime through the
    pinned selection owner, whose exact ordinary profile excludes that branch.
    Unknown source shapes and any genuinely reachable late definition refuse.
    """
    tree = ast.parse(text)
    guards = [n for n in tree.body if isinstance(n, ast.If) and '__main__' in ast.unparse(n.test)]
    if len(guards) != 1:
        raise ValueError('CLI_GUARD_POPULATION')
    guard = guards[0]
    dispatch = tree.body.index(guard)
    groups = {}
    for index, node in enumerate(tree.body):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            groups.setdefault(node.name, []).append((index, node))
    # Resolve the binding that actually exists at dispatch. An imported-only
    # redefinition after dispatch cannot stand in for a missing earlier one.
    definitions = {name: next((v for v in reversed(values) if v[0] < dispatch), values[0])
                   for name, values in groups.items()}
    pins = {'_ordinary_selection_v1': 'f61a7760c52b2adb5e50c327bd9d8213551b46d3a146804773f329ab20ec58df', '_ordinary_modules_v1': 'b0dce0205e6ea8f8bbd4266d9d32fd6521dd8302168b92feb3524509a54bf81e', 'ordinary_receiver_check_v1': '53dc1d0ea52d826e2fa6b53be81c3ef8d1d46e81d581631ee026b7397cd7a7f9', 'execute_ordinary_receiver_v1': 'cf8095b65ada47263113f7dfcd231f0a4b462f2c5f38303adc6b15f0402bfb42', '_ordinary_provider_guard_v1': 'f44779c99d9f67cd72506e6b888875913f3caabca92d428f28a076c5f2221b1c', '__ordinary_cli_guard__': 'f1495caea4e203f81ac3bed53d946581a60362828b180b82c103b84d5ab54176'}
    if guard_ast_digest(guard) != pins['__ordinary_cli_guard__']:
        raise ValueError('CLI_ARGUMENTS_OR_DISPATCH_CHANGED')
    for name, expected in pins.items():
        if name == '__ordinary_cli_guard__':
            continue
        if name not in definitions or guard_ast_digest(definitions[name][1]) != expected:
            raise ValueError('CLI_CRITICAL_SOURCE_CHANGED:' + name)
    constants = {n.targets[0].id: n.value.value for n in tree.body[:dispatch]
                 if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                 and isinstance(n.value, ast.Constant)}
    if constants.get('FRESH_CANARY_PROFILE') != 'codex-app-server-0.166.0-linux-fresh-canary-v1':
        raise ValueError('CLI_EXCLUDED_PROFILE_CHANGED')
    provider = ast.parse(ast.unparse(definitions['_ordinary_provider_guard_v1'][1])).body[0]
    excluded = ast.parse("if selected['profile_id'] == FRESH_CANARY_PROFILE:\n    return _fresh_canary_provider_guard_v1(runtime)").body[0]
    matches = [n for n in provider.body if ast.dump(n) == ast.dump(excluded)]
    if len(matches) != 1:
        raise ValueError('CLI_EXCLUDED_BRANCH_SHAPE')
    provider.body.remove(matches[0])
    roots = ('ordinary_receiver_check_v1', 'execute_ordinary_receiver_v1')
    parents = {name: None for name in roots}
    queue = list(roots)
    while queue:
        name = queue.pop(0)
        index, node = definitions[name]
        if index >= dispatch:
            raise ValueError('CLI_REACHABLE_LATE_DEFINITION:' + name)
        if name == '_ordinary_provider_guard_v1':
            node = provider
        for reference in ast.walk(node):
            if (isinstance(reference, ast.Name) and isinstance(reference.ctx, ast.Load)
                    and reference.id in definitions and reference.id not in parents):
                parents[reference.id] = name
                queue.append(reference.id)
    return dict(entries=list(roots), dependencies=sorted(parents),
                excluded_branch='EXACT_FRESH_PROFILE_BRANCH_REJECTED_BY_PINNED_ORDINARY_SELECTION',
                after_dispatch_imported_only=sorted(n for n, (index, _) in definitions.items() if index > dispatch))
