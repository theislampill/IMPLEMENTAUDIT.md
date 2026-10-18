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
    selection = {'root_thread_id': 'fixture-root', 'cli_version': '0.163.0-alpha.10.2', 'cwd': str(SCRATCH)}
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
