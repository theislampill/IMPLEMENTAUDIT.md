"""compare.py v2: explicit current-source comparison of the DG16 compiler and receiver (DRAFT; needs independent review).

v1 (compare.py) and its outputs are kept unchanged. v2 changes, from the independent review:
  (2) owner_pin uses an explicit allow-list {name -> (pinned path, sha256|bytes)}; each new value is verified
      against the actual blob at the new commit and labelled pin_to:<path> with pin_verified true/false.
      Any other constant change is constant_only, never a pin.
  (3) table replay: a tracked table becomes UNKNOWN (None) on any write outside the supported module-level
      forms (NAME = literal, NAME[k] = v, NAME += literal) anywhere in the file: NAME = NAME + ..., mutating
      method calls, del, **spread, writes inside functions, global NAME, walrus, unpacking, annotated writes.
      Name keys/values are resolved to module-level constants (single binding, no other writes) or UNKNOWN.
  (4) windows_only carries checked assumptions: module-level `import os` binds stdlib os, `os` is not
      otherwise bound anywhere, `os.name` is never written; the label is refused if any check fails.
  (5) report states AST equality is not effect equality, gives raw byte identity and size bounds.
  (6) unnamed statements in replaced blocks carry their list index and a dump digest in the path.
Not a producer of the historical digests d655e326/699eb268/b3b7032e (not reproduced).
Usage: compare_v2.py GIT_DIR OLD_COMMIT NEW_COMMIT OUT.json
"""
import ast
import copy
import difflib
import hashlib
import json
import subprocess
import sys

VERSION = 'compare_v2'
PATHS = {'compiler': 'skills/implementaudit/scripts/compile-work-graph.py',
         'receiver': 'scripts/operational-evidence.py'}
BLOCKS = ('body', 'orelse', 'handlers', 'finalbody', 'cases')
PIN_ALLOW = {'compiler': {
    '_NATIVE_STATIC_OWNER_SHA256': ('scripts/operational-evidence.py', 'sha256'),
    '_NATIVE_STATIC_OWNER_BYTES': ('scripts/operational-evidence.py', 'bytes'),
    '_NATIVE_CONTINUITY_TRANSPORT_SHA256': ('scripts/work-graph-continuity-transport.py', 'sha256'),
    '_NATIVE_CONTINUITY_TRANSPORT_BYTES': ('scripts/work-graph-continuity-transport.py', 'bytes'),
}}
READONLY_METHODS = {'get', 'keys', 'values', 'items', 'copy', 'count', 'index', '__contains__', '__len__',
                    '__getitem__'}
BOUND_NAMES = ('NATIVE_SOURCE_MAX_ENTRIES', 'NATIVE_SOURCE_MAX_FILES', 'NATIVE_SOURCE_MAX_FILE_BYTES',
               'NATIVE_SOURCE_MAX_TOTAL_BYTES')
EQUIVALENCE_NOTE = ('AST equality is not effect equality. Equal ASTs exclude comments/formatting but say nothing '
                    'about imported modules, files read at run time, environment or interpreter behaviour; '
                    'unequal ASTs are classified only by the stated static rules. Table effects are a static '
                    'replay of module-level literals, not an execution.')
WINDOWS_ASSUMPTIONS = ('module-level `import os` (no alias) is present, so `os` is the stdlib module',
                       '`os` is not bound by any other statement, import, argument, handler, target or global',
                       '`os.name` is never assigned or deleted and setattr(os, ...) is never called')
UNKNOWN = None


def key(n):
    return ast.dump(n, include_attributes=False)


def digest(n):
    # ast.unparse text, not ast.dump: dump output changes across Python versions (empty fields omitted in 3.13+)
    return hashlib.sha256(ast.unparse(n).encode()).hexdigest()[:12]


def masked(n):
    class M(ast.NodeTransformer):
        def visit_Constant(self, c):
            return ast.Constant('<C>')
    return key(M().visit(copy.deepcopy(n)))


def name_of(n):
    name = getattr(n, 'name', None)
    if name is None and isinstance(n, ast.Assign):
        name = ','.join(ast.unparse(t) for t in n.targets)
    if name is None and isinstance(n, (ast.AnnAssign, ast.AugAssign)):
        name = ast.unparse(n.target)
    return name


def label(n):
    name = name_of(n)
    return f'{type(n).__name__}:{name}' if name else type(n).__name__


def seg(n, idx):
    s = f'{label(n)}@{idx}'
    return s if name_of(n) else f'{s}#{digest(n)}'


def header(n):
    d = {f: (key(v) if isinstance(v, ast.AST) else [key(x) if isinstance(x, ast.AST) else repr(x) for x in v]
             if isinstance(v, list) else repr(v))
         for f, v in ast.iter_fields(n) if f not in BLOCKS}
    return json.dumps(d, sort_keys=True)


def short(s, limit=4000):
    return s if len(s) <= limit else s[:limit] + f'...<{len(s)} chars>'


# ---------------------------------------------------------------- module facts (constants, tables, os)
class Facts:
    def __init__(self, tree):
        self.tree = tree
        self.parent = {}
        self.fn_depth = {}
        self._index(tree, None, 0)
        self.const_cache = {}

    def _index(self, node, parent, depth):
        self.parent[id(node)] = parent
        self.fn_depth[id(node)] = depth
        inner = depth + (1 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)) else 0)
        for child in ast.iter_child_nodes(node):
            self._index(child, node, inner)

    # names bound anywhere, by any construct, mapped to the binding nodes
    def bindings(self, name):
        out = []
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, (ast.Store, ast.Del)):
                out.append(n)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    bound = a.asname or (a.name.split('.')[0] if isinstance(n, ast.Import) else a.name)
                    if bound == name:
                        out.append(n)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
                out.append(n)
            elif isinstance(n, ast.arg) and n.arg == name:
                out.append(n)
            elif isinstance(n, ast.ExceptHandler) and n.name == name:
                out.append(n)
            elif isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names:
                out.append(n)
            elif hasattr(ast, 'MatchAs') and isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name == name:
                out.append(n)
            elif hasattr(ast, 'MatchMapping') and isinstance(n, ast.MatchMapping) and n.rest == name:
                out.append(n)
        return out

    def module_const(self, name, seen=()):
        if name in self.const_cache:
            return self.const_cache[name]
        res = (False, None)
        if name not in seen:
            b = self.bindings(name)
            if len(b) == 1 and isinstance(b[0], ast.Name):
                stmt = self.parent[id(b[0])]
                if (isinstance(stmt, ast.Assign) and stmt in self.tree.body and len(stmt.targets) == 1
                        and stmt.targets[0] is b[0]):
                    res = self.eval(stmt.value, seen + (name,))
        self.const_cache[name] = res
        return res

    def eval(self, e, seen=()):
        """Static constant evaluation; (ok, value). Unsupported or unresolvable -> (False, None)."""
        if isinstance(e, ast.Constant):
            return True, e.value
        if isinstance(e, (ast.Tuple, ast.List)):
            vals = []
            for x in e.elts:
                if isinstance(x, ast.Starred):
                    return False, None
                ok, v = self.eval(x, seen)
                if not ok:
                    return False, None
                vals.append(v)
            return True, tuple(vals)
        if isinstance(e, ast.Name):
            return self.module_const(e.id, seen)
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, (ast.USub, ast.UAdd)):
            ok, v = self.eval(e.operand, seen)
            if ok and type(v) is int:
                return True, -v if isinstance(e.op, ast.USub) else v
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Mult, ast.Add, ast.Sub, ast.LShift)):
            ok1, a = self.eval(e.left, seen)
            ok2, b = self.eval(e.right, seen)
            if ok1 and ok2 and type(a) is int and type(b) is int and 0 <= b < 4096:
                return True, {ast.Mult: a * b, ast.Add: a + b, ast.Sub: a - b, ast.LShift: a << b}[type(e.op)]
        return False, None

    # -------------------------------------------------------------- tables
    @staticmethod
    def table_stmt_name(n):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
            if isinstance(t, ast.Name) and isinstance(n.value, (ast.Dict, ast.Tuple, ast.List)):
                return t.id
            if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                return t.value.id
        if (isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add) and isinstance(n.target, ast.Name)
                and isinstance(n.value, (ast.Tuple, ast.List))):
            return n.target.id
        return None

    def table(self, name):
        """Replay one module-level table; UNKNOWN (None) on any write outside the supported forms."""
        supported = [n for n in self.tree.body if self.table_stmt_name(n) == name]
        if not supported:
            return UNKNOWN, 'not a module-level table'
        allowed = set()
        for n in supported:
            allowed.add(id(n.targets[0] if isinstance(n, ast.Assign) else n.target))
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript):
                allowed.add(id(n.targets[0].value))
        for n in ast.walk(self.tree):
            if isinstance(n, (ast.Global, ast.Nonlocal)) and name in n.names:
                return UNKNOWN, f'global/nonlocal {name} at line {n.lineno}'
            if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, (ast.Store, ast.Del)) \
                    and id(n) not in allowed:
                return UNKNOWN, f'other write to {name} at line {n.lineno}'
            if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == name \
                    and isinstance(n.ctx, (ast.Store, ast.Del)) and id(n) not in allowed:
                return UNKNOWN, f'item write/delete on {name} at line {n.lineno}'
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == name and n.func.attr not in READONLY_METHODS):
                return UNKNOWN, f'method {n.func.attr} on {name} at line {n.lineno}'
            why = self.dynamic_write(n, name)
            if why:
                return UNKNOWN, why
            if isinstance(n, (ast.Import, ast.ImportFrom)) and any((a.asname or a.name.split('.')[0]) == name for a in n.names):
                return UNKNOWN, f'import binds {name} at line {n.lineno}'
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
                return UNKNOWN, f'def binds {name} at line {n.lineno}'
        val = None
        for n in supported:
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                v = n.value
                if isinstance(v, ast.Dict):
                    val = {}
                    for k, x in zip(v.keys, v.values):
                        if k is None:
                            return UNKNOWN, f'**spread in {name} at line {n.lineno}'
                        ok1, kk = self.eval(k)
                        ok2, xx = self.eval(x)
                        if not (ok1 and ok2):
                            return UNKNOWN, f'unresolvable entry in {name} at line {n.lineno}'
                        val[kk] = xx
                else:
                    ok, xs = self.eval(v)
                    if not ok:
                        return UNKNOWN, f'unresolvable element in {name} at line {n.lineno}'
                    val = list(xs)
            elif isinstance(n, ast.Assign):
                if not isinstance(val, dict):
                    return UNKNOWN, f'item assignment on non-dict {name} at line {n.lineno}'
                ok1, kk = self.eval(n.targets[0].slice)
                ok2, xx = self.eval(n.value)
                if not (ok1 and ok2):
                    return UNKNOWN, f'unresolvable item assignment on {name} at line {n.lineno}'
                val[kk] = xx
            else:
                if not isinstance(val, list):
                    return UNKNOWN, f'+= on non-sequence {name} at line {n.lineno}'
                ok, xs = self.eval(n.value)
                if not ok:
                    return UNKNOWN, f'unresolvable += element in {name} at line {n.lineno}'
                val.extend(xs)
        return val, 'replayed'

    @staticmethod
    def dynamic_write(n, name):
        """Dynamic constructs that could write this module's globals -> reason string, else None.
        exec/eval with an explicit globals mapping other than globals()/vars() run in that other namespace
        (here: freshly created modules' __dict__) and are listed separately as not targeting this module."""
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)):
            return None
        f = n.func.id
        if f in ('exec', 'eval'):
            g = n.args[1] if len(n.args) > 1 else next((k.value for k in n.keywords if k.arg == 'globals'), None)
            if g is None or (isinstance(g, ast.Call) and isinstance(g.func, ast.Name) and g.func.id in ('globals', 'vars')):
                return f'{f} into this module namespace at line {n.lineno}'
            return None
        if f == 'globals' or (f == 'vars' and not n.args):
            return f'{f}() at line {n.lineno}'
        if f in ('setattr', 'delattr'):
            target = n.args[1] if len(n.args) > 1 else None
            if not (isinstance(target, ast.Constant) and target.value != name) or 'sys.modules' in ast.unparse(n):
                return f'{f} that may target {name} at line {n.lineno}'
        return None

    def dynamic_calls(self):
        out = []
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                    'exec', 'eval', 'globals', 'vars', 'setattr', 'delattr'):
                out.append(dict(call=n.func.id, line=n.lineno,
                                writes_this_module=self.dynamic_write(n, '<no-table>') is not None,
                                text=short(ast.unparse(n), 200)))
        return out

    # -------------------------------------------------------------- os assumptions
    def os_assumptions(self):
        checks = {}
        top = [n for n in self.tree.body if isinstance(n, ast.Import)
               and any(a.name == 'os' and a.asname is None for a in n.names)]
        checks['module_level_import_os'] = bool(top)
        others = []
        for b in self.bindings('os'):
            if b in top:
                continue
            if isinstance(b, ast.Import) and all((a.asname is None and a.name.split('.')[0] == 'os')
                                                 or (a.asname or a.name.split('.')[0]) != 'os' for a in b.names):
                continue  # `import os` / `import os.path` re-bind the same stdlib module
            others.append(getattr(b, 'lineno', None))
        checks['os_not_otherwise_bound'] = not others
        writes = []
        for n in ast.walk(self.tree):
            if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == 'os'
                    and n.attr == 'name' and isinstance(n.ctx, (ast.Store, ast.Del))):
                writes.append(n.lineno)
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('setattr', 'delattr')
                    and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id == 'os'):
                writes.append(n.lineno)
        checks['os_name_not_written'] = not writes
        return dict(assumptions=list(WINDOWS_ASSUMPTIONS), checks=checks, other_os_bindings=others,
                    os_name_writes=writes, holds=all(checks.values()))


# ---------------------------------------------------------------- statement diff
def is_nt_eq(e, op=ast.Eq):
    return (isinstance(e, ast.Compare) and len(e.ops) == 1 and isinstance(e.ops[0], op)
            and isinstance(e.left, ast.Attribute) and isinstance(e.left.value, ast.Name)
            and e.left.value.id == 'os' and e.left.attr == 'name'
            and isinstance(e.comparators[0], ast.Constant) and e.comparators[0].value == 'nt')


def nt_guard(test):
    if is_nt_eq(test):
        return True
    return isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And) and is_nt_eq(test.values[0])


def has_blocks(n):
    return any(isinstance(getattr(n, f, None), list) for f in BLOCKS)


class Differ:
    def __init__(self, role, fa, fb, os_ok, blob_lookup):
        self.role, self.fa, self.fb, self.os_ok, self.lookup = role, fa, fb, os_ok, blob_lookup
        self.out = []
        self.refs = set()

    def lists(self, old, new, path, ctx):
        sm = difflib.SequenceMatcher(None, [key(n) for n in old], [key(n) for n in new], autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                continue
            a, b = list(enumerate(old[i1:i2], i1)), list(enumerate(new[j1:j2], j1))
            bmap = {}
            for j, n in b:
                bmap.setdefault(label(n), []).append((j, n))
            used = set()
            for i, n in a:
                cands = [(j, m) for j, m in bmap.get(label(n), []) if j not in used]
                if cands:
                    j, m = cands[0]
                    used.add(j)
                    s = f'{label(n)}@{i}>{j}' + ('' if name_of(n) else f'#{digest(n)}>{digest(m)}')
                    self.node(n, m, path + '/' + s, ctx)
                else:
                    self.emit('removed', path + '/' + seg(n, i), n, None, ctx)
            for j, n in b:
                if j not in used:
                    self.emit('added', path + '/' + seg(n, j), None, n, ctx)

    def node(self, a, b, path, ctx):
        if key(a) == key(b):
            return
        if type(a) is type(b) and has_blocks(a):
            if header(a) != header(b):
                self.emit('header_changed', path, a, b, ctx, header_only=True)
            for f in BLOCKS:
                la, lb = getattr(a, f, None), getattr(b, f, None)
                if not (isinstance(la, list) and isinstance(lb, list)):
                    continue
                sub = ctx
                if isinstance(a, ast.If) and f == 'body' and nt_guard(a.test) and nt_guard(b.test):
                    sub = ctx + ['nt_body']
                if isinstance(a, ast.If) and f == 'orelse' and is_nt_eq(a.test, ast.NotEq) and is_nt_eq(b.test, ast.NotEq):
                    sub = ctx + ['nt_body']
                if f == 'handlers':
                    for i, (x, y) in enumerate(zip(la, lb)):
                        self.node(x, y, f'{path}.handlers[{i}]', sub)
                    for i, x in enumerate(la[len(lb):], len(lb)):
                        self.emit('removed', f'{path}.handlers[{i}]#{digest(x)}', x, None, sub)
                    for i, y in enumerate(lb[len(la):], len(la)):
                        self.emit('added', f'{path}.handlers[{i}]#{digest(y)}', None, y, sub)
                else:
                    self.lists(la, lb, path + '.' + f, sub)
            return
        self.emit('changed', path, a, b, ctx)

    def emit(self, kind, path, a, b, ctx, header_only=False):
        def text(n):
            if n is None:
                return None
            if header_only:
                n = copy.deepcopy(n)
                for f in BLOCKS:
                    if isinstance(getattr(n, f, None), list):
                        setattr(n, f, [ast.Pass()] if f == 'body' else [])
            return ast.unparse(n)
        structural_nt = 'nt_body' in ctx
        if (kind == 'header_changed' and isinstance(a, ast.If) and isinstance(b, ast.If)
                and nt_guard(a.test) and nt_guard(b.test)
                and key(a.test.values[0] if isinstance(a.test, ast.BoolOp) else a.test)
                == key(b.test.values[0] if isinstance(b.test, ast.BoolOp) else b.test)):
            structural_nt = True
        windows = structural_nt and self.os_ok
        const_only = a is not None and b is not None and masked(a) == masked(b) and not header_only
        pin = None
        allow = PIN_ALLOW.get(self.role, {})
        if (const_only and isinstance(a, ast.Assign) and isinstance(b, ast.Assign) and len(b.targets) == 1
                and isinstance(b.targets[0], ast.Name) and b.targets[0].id in allow
                and isinstance(b.value, ast.Constant)):
            path_to, field = allow[b.targets[0].id]
            raw = self.lookup(path_to)
            actual = None if raw is None else (hashlib.sha256(raw).hexdigest() if field == 'sha256' else len(raw))
            pin = dict(pin_to=path_to, field=field, value=b.value.value, actual=actual,
                       pin_verified=actual is not None and actual == b.value.value)
        for n in (a, b):
            if n is not None:
                self.refs.update(x.id for x in ast.walk(n) if isinstance(x, ast.Name))
        old, new = text(a), text(b)
        self.out.append(dict(
            kind=kind, path=path, constant_only=const_only, owner_pin=pin is not None,
            pin=('pin_to:' + pin['pin_to']) if pin else None, pin_verified=pin['pin_verified'] if pin else None,
            pin_detail=pin, windows_only=windows,
            windows_label_refused=structural_nt and not self.os_ok,
            old=short(old) if old else None, new=short(new) if new else None,
            old_sha256=hashlib.sha256(old.encode()).hexdigest() if old else None,
            new_sha256=hashlib.sha256(new.encode()).hexdigest() if new else None))


def jsonable(v):
    if isinstance(v, dict):
        return {repr(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v


def path_names(path):
    """Base names of the named segments of a difference path, e.g. '/Assign:X['k']@3' -> {'X'}."""
    names = set()
    for s in path.split('/'):
        for suffix in ('.body', '.orelse', '.finalbody', '.cases'):
            if s.endswith(suffix):
                s = s[:-len(suffix)]
        s = s.split('.handlers[', 1)[0]
        if ':' in s:
            n = s.split(':', 1)[1].split('@', 1)[0]
            for part in n.split(','):
                names.add(part.split('[', 1)[0])
    return names


def table_effects(fa, fb, out, refs=()):
    names = set()
    for stmt_list in (fa.tree.body, fb.tree.body):
        for n in stmt_list:
            t = Facts.table_stmt_name(n)
            if t:
                names.add(t)
    touched = {n for n in names if n in refs or any(n in path_names(d['path']) for d in out)}
    effects = {}
    for name in sorted(touched):
        a, why_a = fa.table(name)
        b, why_b = fb.table(name)
        if a is None or b is None or type(a) is not type(b):
            effects[name] = dict(status='UNKNOWN', old_reason=why_a, new_reason=why_b)
            continue
        if isinstance(a, dict):
            added = [k for k in b if k not in a]
            removed = [k for k in a if k not in b]
            changed = [k for k in a if k in b and a[k] != b[k]]
            preserved = not removed and not changed
        else:
            added = [e for e in b if e not in a]
            removed = [e for e in a if e not in b]
            changed = []
            preserved = b[:len(a)] == a
        effects[name] = dict(status='REPLAYED', kind=type(a).__name__, old_entries=len(a), new_entries=len(b),
                             equal=a == b, old_preserved=preserved, added=len(added), removed=len(removed),
                             changed=len(changed),
                             added_sha256=[hashlib.sha256(repr(x).encode()).hexdigest() for x in added],
                             removed_items=[short(repr(x), 400) for x in removed],
                             changed_keys=[repr(k) for k in changed])
    return effects


def admission_model(fa, fb):
    """Receiver continuity-source admission (static model of _native_check_continuity_closure_v1).

    Model, checked against the function source: profiles matching helper_pair = (row0 sha256, row1 sha256) are
    selected in table order; `windows = profiles[0][0][3] is None`, and windows refuses unless os.name == 'nt'.
    So a pair is Linux-admitted iff the FIRST profile with that pair has a non-None row-0 mode."""
    expected_stmts = [key(ast.parse(s).body[0]) for s in (
        'profiles = tuple(profile for profile in _NATIVE_CONTINUITY_SOURCE_PROFILES_V1'
        ' if (profile[0][2], profile[1][2]) == helper_pair)',
        'windows = profiles[0][0][3] is None')]
    expected_test = key(ast.parse("windows and os.name != 'nt'", mode='eval').body)

    def check(f):
        fn = [n for n in f.tree.body if isinstance(n, ast.FunctionDef) and n.name == '_native_check_continuity_closure_v1']
        if len(fn) != 1:
            return False
        stmts = {key(n) for n in ast.walk(fn[0]) if isinstance(n, ast.stmt)}
        tests = {key(n.test) for n in ast.walk(fn[0]) if isinstance(n, ast.If)}
        return all(s in stmts for s in expected_stmts) and expected_test in tests
    if not (check(fa) and check(fb)):
        return dict(status='UNKNOWN', reason='function source does not match the model')
    ta, _ = fa.table('_NATIVE_CONTINUITY_SOURCE_PROFILES_V1')
    tb, _ = fb.table('_NATIVE_CONTINUITY_SOURCE_PROFILES_V1')
    if ta is None or tb is None:
        return dict(status='UNKNOWN', reason='profile table UNKNOWN')

    def first_by_pair(t):
        firsts, counts = {}, {}
        for p in t:
            pair = (p[0][2], p[1][2])
            firsts.setdefault(pair, p)
            counts[pair] = counts.get(pair, 0) + 1
        return firsts, counts
    fa_, _ = first_by_pair(ta)
    fb_, cb = first_by_pair(tb)
    new_pairs = [p for p in fb_ if p not in fa_]
    rows = []
    for pair in new_pairs:
        first = fb_[pair]
        none_rows = [p for p in tb if (p[0][2], p[1][2]) == pair and p[0][3] is None]
        rows.append(dict(pair=list(pair), profiles_for_pair=cb[pair], linux_admitted=first[0][3] is not None,
                         first_profile_row0_mode=first[0][3], has_mode_none_profile=bool(none_rows),
                         note=('Windows-only only because the first profile for this pair has row-0 mode None '
                               '(row order); an earlier non-None profile for the same pair would admit it on Linux '
                               'and these mode-None rows would then accept any mode') if first[0][3] is None else None))
    ROW_ORDER_NOTE = ('Windows-only only because the first profile for this pair has row-0 mode None (row order); '
                      'an earlier non-None profile for the same pair would admit it on Linux and the mode-None '
                      'rows would then accept any mode')
    old_keys = [repr(p) for p in ta]
    added_profiles = [(i, p) for i, p in enumerate(tb) if repr(p) not in old_keys]
    to_existing = []
    for i, p in added_profiles:
        pair = (p[0][2], p[1][2])
        if pair in fa_:
            first = fb_[pair]
            to_existing.append(dict(pair=list(pair), new_profile_index=i, new_profile_row0_mode=p[0][3],
                                    first_profile_index=next(j for j, q in enumerate(tb) if q is first),
                                    first_profile_row0_mode=first[0][3], linux_admitted=first[0][3] is not None,
                                    note=ROW_ORDER_NOTE if first[0][3] is None else None))
    # whitespace-normalized: Python 3.13+ dedents docstrings at compile time
    return dict(status='MODELLED', model=' '.join(admission_model.__doc__.split('\n\n')[1].split()),
                added_profiles=len(added_profiles),
                added_profiles_to_existing_pairs=to_existing,
                old_pairs=len(fa_), new_pairs_total=len(fb_), added_pairs=len(new_pairs),
                added_linux_admitted=sum(r['linux_admitted'] for r in rows),
                added_windows_only_by_row_order=[r['pair'] for r in rows if not r['linux_admitted']],
                changed_first_profile_for_old_pairs=sorted(repr(p) for p in fa_ if fb_.get(p) != fa_[p]),
                added=rows)


def analyze(role, ra, rb, blob_lookup):
    ta, tb = ast.parse(ra), ast.parse(rb)
    fa, fb = Facts(ta), Facts(tb)
    osa, osb = fa.os_assumptions(), fb.os_assumptions()
    d = Differ(role, fa, fb, osa['holds'] and osb['holds'], blob_lookup)
    d.lists(ta.body, tb.body, '', [])
    out = d.out
    hunks = sum(1 for line in difflib.unified_diff(ra.decode('utf-8', 'replace').splitlines(),
                                                   rb.decode('utf-8', 'replace').splitlines(), n=0, lineterm='')
                if line.startswith('@@'))
    summary = dict(total=len(out), owner_pin=sum(x['owner_pin'] for x in out),
                   owner_pin_verified=sum(1 for x in out if x['pin_verified']),
                   constant_only_not_pin=sum(1 for x in out if x['constant_only'] and not x['owner_pin']),
                   windows_only=sum(x['windows_only'] for x in out),
                   windows_label_refused=sum(x['windows_label_refused'] for x in out),
                   other=sum(1 for x in out if not x['owner_pin'] and not x['windows_only']))
    rep = dict(byte_equal=ra == rb, text_hunks=hunks, ast_equal=key(ta) == key(tb),
               dynamic_calls=dict(old=fa.dynamic_calls(), new=fb.dynamic_calls()),
               os_assumptions=dict(old=osa, new=osb), summary=summary, differences=out,
               table_effects=table_effects(fa, fb, out, d.refs))
    return rep, fa, fb


def size_bounds(fa, fb):
    out = {}
    for side, f in (('old', fa), ('new', fb)):
        out[side] = {}
        for n in BOUND_NAMES:
            ok, v = f.module_const(n)
            out[side][n] = v if ok else 'UNKNOWN'
    return out


def scope_check(report):
    comp, recv = report['files']['compiler'], report['files']['receiver']
    holds = (all(x['owner_pin'] and x['pin_verified'] for x in comp['differences'])
             and all(x['windows_only'] for x in recv['differences']))
    linux = []
    for role, f in (('compiler', comp), ('receiver', recv)):
        for x in f['differences']:
            if x['owner_pin']:
                linux.append(dict(file=role, item=x['path'].lstrip('/'), kind='pin', pin=x['pin'],
                                  pin_verified=x['pin_verified']))
        for name, e in f['table_effects'].items():
            if e['status'] != 'REPLAYED' or not e['equal']:
                linux.append(dict(file=role, item=name, kind='table', status=e['status'],
                                  entries=f"{e.get('old_entries')}->{e.get('new_entries')}",
                                  added=e.get('added'), removed=e.get('removed'), changed=e.get('changed')))
        tables = set(f['table_effects'])
        for x in f['differences']:
            covered = x['owner_pin'] or x['windows_only'] or bool(path_names(x['path']) & tables)
            if not covered:
                linux.append(dict(file=role, item=x['path'].lstrip('/'), kind='uncovered_' + x['kind']))
    adm = recv.get('admission')
    windows = [dict(file=r, item=x['path'].lstrip('/'), kind=x['kind'])
               for r, f in (('compiler', comp), ('receiver', recv)) for x in f['differences'] if x['windows_only']]
    parts = []
    for item in linux:
        if item['kind'] == 'table':
            parts.append(f"{item['file']}:{item['item']}:{item['entries']}")
        elif item['kind'] == 'pin':
            parts.append(f"{item['file']}:{item['item'].split('@')[0]}:pin_verified={item['pin_verified']}")
        else:
            parts.append(f"{item['file']}:{item['item']}:{item['kind']}")
    row_order = []
    if adm and adm.get('status') == 'MODELLED':
        parts.append(f"receiver:new_linux_admitted_pairs:{adm['added_linux_admitted']}")
        row_order = ([dict(pair=p, kind='new_pair') for p in adm['added_windows_only_by_row_order']]
                     + [dict(pair=r['pair'], kind='profile_added_to_existing_pair', new_profile_index=r['new_profile_index'],
                             first_profile_index=r['first_profile_index'])
                        for r in adm['added_profiles_to_existing_pairs'] if not r['linux_admitted']])
        if row_order:
            parts.append(f"receiver:windows_only_by_row_order_profiles:{len(row_order)}")
    parts.append(f'windows_only_differences:{len(windows)}')
    return dict(historical_scope_label='TWO_LINUX_SEMANTICALLY_EQUIVALENT_EXCEPT_NEW_STATIC_OWNER_PINS',
                historical_scope_label_holds=holds,
                new_scope_label=None if holds else 'LINUX_SEMANTIC_DIFFERENCES[' + '; '.join(parts) + ']',
                linux_semantic_differences=linux, windows_only_differences=windows,
                windows_only_by_row_order=row_order)


def git(repo, *a):
    return subprocess.check_output(['git', '--git-dir', repo, *a])


def blob_or_none(repo, commit, path):
    try:
        return subprocess.check_output(['git', '--git-dir', repo, 'cat-file', 'blob', f'{commit}:{path}'],
                                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def compare(repo, old_c, new_c):
    report = dict(schema='dg16.owner-ast-difference-report.draft.v2', tool=VERSION, authority='NONE',
                  status='DRAFT_REQUIRES_INDEPENDENT_REVIEW', old_commit=old_c, new_commit=new_c,
                  python=sys.version.split()[0], equivalence_note=EQUIVALENCE_NOTE, files={})
    facts = {}
    for role, p in PATHS.items():
        ra, rb = git(repo, 'cat-file', 'blob', f'{old_c}:{p}'), git(repo, 'cat-file', 'blob', f'{new_c}:{p}')
        rep, fa, fb = analyze(role, ra, rb, lambda path: blob_or_none(repo, new_c, path))
        facts[role] = (fa, fb)
        report['files'][role] = dict(
            path=p,
            old=dict(git_blob=git(repo, 'rev-parse', f'{old_c}:{p}').decode().strip(),
                     sha256=hashlib.sha256(ra).hexdigest(), bytes=len(ra)),
            new=dict(git_blob=git(repo, 'rev-parse', f'{new_c}:{p}').decode().strip(),
                     sha256=hashlib.sha256(rb).hexdigest(), bytes=len(rb)), **rep)
    bounds = size_bounds(*facts['compiler'])
    report['size_bounds'] = dict(
        source='module-level constants of the compiler at each commit; applicability to these two files is '
               'informational, not asserted', values=bounds,
        files={r: dict(old_bytes=f['old']['bytes'], new_bytes=f['new']['bytes'],
                       old_within_NATIVE_SOURCE_MAX_FILE_BYTES=(f['old']['bytes'] <= bounds['old']['NATIVE_SOURCE_MAX_FILE_BYTES'])
                       if isinstance(bounds['old']['NATIVE_SOURCE_MAX_FILE_BYTES'], int) else 'UNKNOWN',
                       new_within_NATIVE_SOURCE_MAX_FILE_BYTES=(f['new']['bytes'] <= bounds['new']['NATIVE_SOURCE_MAX_FILE_BYTES'])
                       if isinstance(bounds['new']['NATIVE_SOURCE_MAX_FILE_BYTES'], int) else 'UNKNOWN')
               for r, f in report['files'].items()})
    report['files']['receiver']['admission'] = admission_model(*facts['receiver'])
    report['scope'] = scope_check(report)
    return report


def main():
    repo, old_c, new_c, dest = sys.argv[1:5]
    rep = compare(repo, old_c, new_c)
    raw = (json.dumps(rep, sort_keys=True, indent=1, ensure_ascii=True) + '\n').encode()
    with open(dest, 'wb') as fh:
        fh.write(raw)
    print(dest, hashlib.sha256(raw).hexdigest(), len(raw))
    for role, f in rep['files'].items():
        print(f"  {role}: byte_equal={f['byte_equal']} {f['old']['bytes']}->{f['new']['bytes']} text_hunks={f['text_hunks']} "
              f"ast_equal={f['ast_equal']} os_assumptions_hold={f['os_assumptions']['old']['holds'] and f['os_assumptions']['new']['holds']} {f['summary']}")
        for d in f['differences']:
            flags = ''.join(c for c, on in (('P', d['owner_pin']), ('V', d['pin_verified']), ('W', d['windows_only']),
                                            ('K', d['constant_only']), ('R', d['windows_label_refused'])) if on)
            print(f"    [{flags or '-':4s}] {d['kind']:14s} {d['path']}" + (f"  {d['pin']}" if d['pin'] else ''))
        for name, e in f['table_effects'].items():
            print(f"    TABLE {name}: " + (f"{e['kind']} {e['old_entries']}->{e['new_entries']} added={e['added']} "
                  f"removed={e['removed']} changed={e['changed']} old_preserved={e['old_preserved']}"
                  if e['status'] == 'REPLAYED' else f"UNKNOWN ({e['old_reason']} / {e['new_reason']})"))
    adm = rep['files']['receiver']['admission']
    print('  ADMISSION', {k: v for k, v in adm.items() if k not in ('added', 'model')})
    print('  SIZE_BOUNDS', json.dumps(rep['size_bounds'], sort_keys=True))
    print('  SCOPE holds=', rep['scope']['historical_scope_label_holds'])
    print('  NEW_SCOPE_LABEL', rep['scope']['new_scope_label'])


if __name__ == '__main__':
    main()
