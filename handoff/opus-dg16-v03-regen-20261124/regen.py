#!/usr/bin/env python3
"""Deterministic regenerator for the DG16 full-G2 source-derived profiles.

Writes REPORT_SLOTS.json (dg16.full-source-report-slots.proposed.v1) and
OUTPUT_ROLES.json (dg16.full-output-role-profile.proposed.v1) from a source
checkout.  Stdlib only.  Test populations are enumerated by loading each
declared program in a child interpreter with unittest's runners patched so
that no test method ever executes (the runner call is intercepted and the
suite is captured instead).

Must run under CPython 3.11 or 3.12: guard_ast_sha256 hashes ast.dump()
output, whose format changed in 3.13.

usage: regen.py --source CHECKOUT --commit SHA --tree SHA --out DIR
               [--closure-membership-from PRIOR_REPORT_SLOTS.json]
"""
import argparse
import ast
import base64
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REGISTRY = 'scripts/verify-package.sh'
WG_VERIFIER_WRAPPER = 'tests/work-graph-verifier.test.sh'

# Authored constant text (copied literally; not source-derived).
RS_SCHEMA = 'dg16.full-source-report-slots.proposed.v1'
RS_STATUS = 'STATIC_DERIVATION_REQUIRES_COLD_REVIEW_OF_COMPLETE_INVOCATION_CLOSURE'
RS_LIMITS = [
    "Not an observed report sequence or emitter-identity attestation.",
    "Each actual report population/order/count/progress identity must match before any substitution.",
    "Every unmatched stderr byte remains exact; missing or additional complete report blocks refuse.",
    "Declared methods remain in the denominator. Source-bound class skips are explicitly unexecuted; actual Ran and class-skip markers require frozen captured-environment eligibility. Inline public-source stderr remains byte-exact; only report timers are replaced.",
]
OR_SCHEMA = 'dg16.full-output-role-profile.proposed.v1'
OR_STATUS = 'STATIC_SOURCE_DERIVATION_NOT_AN_EXECUTION_OR_ACCEPTANCE'
DISABLED_REQUIREMENT = 'ABSENT_IN_FROZEN_ACTUAL_CHILD_ENVIRONMENT'


def fail(message):
    raise SystemExit('regen: ' + message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


# --------------------------------------------------------------------------
# Source access: bytes from the checkout, modes from the commit's tree.
# --------------------------------------------------------------------------
class Source:
    def __init__(self, root, commit, tree, git_dir=None):
        self.root = os.path.abspath(root)
        git = ['git', '--git-dir=' + git_dir] if git_dir else ['git', '-C', self.root]
        out = subprocess.run([*git, 'rev-parse', commit + '^{commit}', commit + '^{tree}'],
                             capture_output=True, check=True).stdout.decode().split()
        if out[0] != commit or out[1] != tree:
            fail('commit/tree mismatch: %r' % out)
        self.commit, self.tree = commit, tree
        listing = subprocess.run([*git, 'ls-tree', '-r', '-z', '--full-tree', commit],
                                 capture_output=True, check=True).stdout
        self.entries = {}
        for record in listing.split(b'\0'):
            if not record:
                continue
            meta, path = record.split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            if kind == 'blob':
                self.entries[path.decode('utf-8')] = (mode, blob)
        self._cache = {}

    def exists(self, path):
        return path in self.entries

    def read(self, path):
        if path not in self._cache:
            mode, blob = self.entries[path]
            if mode == '120000':
                fail('symlink member not supported: ' + path)
            with open(os.path.join(self.root, *path.split('/')), 'rb') as handle:
                raw = handle.read()
            if hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest() != blob:
                fail('checkout bytes differ from commit blob: ' + path)
            self._cache[path] = raw
        return self._cache[path]

    def text(self, path):
        return self.read(path).decode('utf-8')

    def pin(self, path):
        raw = self.read(path)
        return {'bytes': len(raw), 'mode': self.entries[path][0], 'sha256': sha256(raw)}


# --------------------------------------------------------------------------
# Registry -> wrappers -> declared unittest report slots.
# --------------------------------------------------------------------------
PY_PATH = re.compile(r'[A-Za-z0-9_./${}-]+\.py\b')
ROOT_PREFIX = re.compile(r'^"?\$\{?(?:repo_root|root)\}?/')


def registry_wrappers(src):
    wrappers = []
    for line in src.text(REGISTRY).splitlines():
        match = re.fullmatch(r'bash (tests/[A-Za-z0-9_.-]+\.test\.sh)', line)
        if match:
            wrappers.append(match.group(1))
    return wrappers


def emits_unittest_report(text):
    return 'unittest.main' in text or 'TextTestRunner' in text


def slot_lines(src, wrapper):
    """Lines naming a repository Python program that reaches a unittest runner.

    The bodies of `elif`/`else` branches are alternative interpreter spellings
    of the first branch (command -v chains) and never additional reports.
    """
    lines = src.text(wrapper).splitlines()
    found = []
    frames = []  # one entry per open if-block: True once an elif/else branch began
    heredoc = None
    for index, line in enumerate(lines):
        words = line.strip()
        if heredoc is not None:
            if (words if heredoc[1] else line) == heredoc[0]:
                heredoc = None
            continue
        opened = re.search(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2", line)
        if opened and '<<<' not in line:
            heredoc = (opened.group(3), opened.group(1) == '-')
        if re.match(r'(elif|else)\b', words) and frames:
            frames[-1] = True
        alternate = any(frames)
        if re.match(r'if\b', words):
            frames.append(False)
        if (re.search(r'(^|;\s*)fi\s*$', words)) and frames:
            frames.pop()
        if alternate:
            continue
        for match in PY_PATH.finditer(line):
            path = re.sub(r'^\$\{?(?:repo_root|root)\}?/', '', match.group(0))
            if path.startswith('./'):
                path = path[2:]
            if src.exists(path) and path.endswith('.py') and emits_unittest_report(src.text(path)):
                found.append((index + 1, line, path))
                break
    return found


def invocation_argv(line, program, repo):
    """Interpreter flags and program arguments of one wrapper line."""
    tokens = shlex.split(line)
    position = next(i for i, token in enumerate(tokens) if token.endswith(program))
    flags = [t for t in tokens[:position] if re.fullmatch(r'-[A-Za-z]+', t) and t != '-3']
    arguments = []
    for token in tokens[position + 1:]:
        if token == '$@':
            continue
        token = re.sub(r'^\$\{?(?:repo_root|root)\}?', repo, token)
        if '$' in token:
            fail('unresolved shell expansion in invocation: ' + line)
        arguments.append(token)
    return flags, arguments


# --------------------------------------------------------------------------
# Child enumerator.  Runs inside a disposable copy of the source.
# --------------------------------------------------------------------------
CHILD = r'''
import ast, hashlib, json, os, runpy, sys, unittest
spec = json.loads(sys.argv[1])
os.chdir(spec['repo'])
program = spec['program_path']
if not sys.flags.isolated:
    sys.path[0] = os.path.dirname(program)
class Captured(BaseException):
    pass
captured = {}
def leaves(suite):
    if isinstance(suite, unittest.TestSuite):
        for item in suite:
            yield from leaves(item)
    else:
        yield suite
def fake_run(self, test):
    captured.update(tests=list(leaves(test)), verbosity=self.verbosity, via='TextTestRunner')
    raise Captured()
def fake_run_tests(self):
    captured.update(tests=list(leaves(self.test)), verbosity=self.verbosity, via='TestProgram')
    raise Captured()
unittest.TextTestRunner.run = fake_run
unittest.TestProgram.runTests = fake_run_tests
sys.argv = [program, *spec['arguments']]
module_globals = None
if spec['mode'] == 'main':
    try:
        runpy.run_path(program, run_name='__main__')
    except Captured:
        pass
else:
    # Static helper suite: load the module without its __main__ block and
    # build the named classes exactly as the helper does.
    source = open(program, 'rb').read()
    tree = ast.parse(source, program)
    tree.body = [n for n in tree.body if not (isinstance(n, ast.If) and '__name__' in ast.unparse(n.test))]
    import types
    module = types.ModuleType('__main__'); module.__file__ = program
    sys.modules['__main__'] = module
    exec(compile(tree, program, 'exec'), module.__dict__)
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    for name in spec['classes']:
        suite.addTests(loader.loadTestsFromTestCase(getattr(module, name)))
    captured.update(tests=list(leaves(suite)), verbosity=spec['verbosity'], via='STATIC')
if 'tests' not in captured:
    raise SystemExit('NO_RUNNER_REACHED')
rows = []
for test in captured['tests']:
    if type(test).__module__.startswith('unittest'):
        raise SystemExit('LOADER_FAILURE ' + test.id())
    rows.append(dict(id=test.id(), printed_identity=str(test), description_first_line=test.shortDescription()))

def guard_of(cls):
    owner = next((k for k in cls.__mro__ if 'setUpClass' in k.__dict__), None)
    if owner is None or owner is unittest.TestCase:
        return None
    function = owner.__dict__['setUpClass']
    function = getattr(function, '__func__', function)
    code = function.__code__
    path = os.path.realpath(code.co_filename)
    tree = ast.parse(open(path, 'rb').read(), path)
    node = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'setUpClass' and
                 (n.decorator_list[0].lineno if n.decorator_list else n.lineno) == code.co_firstlineno), None)
    if node is None or not node.body or not isinstance(node.body[0], ast.If):
        return None
    test = node.body[0]
    t = test.test
    if not (isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], ast.NotEq) and
            isinstance(t.comparators[0], ast.Constant) and isinstance(t.left, ast.Call) and
            ast.unparse(t.left.func) == 'os.environ.get' and len(t.left.args) == 1 and
            len(test.body) == 1 and isinstance(test.body[0], ast.Raise) and isinstance(test.body[0].exc, ast.Call) and
            ast.unparse(test.body[0].exc.func) == 'unittest.SkipTest' and len(test.body[0].exc.args) == 1 and
            not test.orelse):
        return None
    scope = dict(function.__globals__); scope['cls'] = cls
    evaluate = lambda e: eval(compile(ast.Expression(e), path, 'eval'), scope)
    raw = open(path, 'rb').read()
    return dict(environment_name=evaluate(t.left.args[0]), enabled_value=t.comparators[0].value,
                disabled_requirement=spec['disabled_requirement'], reason=evaluate(test.body[0].exc.args[0]),
                function_first_line=code.co_firstlineno,
                guard_ast_sha256=hashlib.sha256(ast.dump(test).encode()).hexdigest(),
                source_path=os.path.relpath(path, os.path.realpath(spec['repo'])).replace(os.sep, '/'),
                source=dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))

groups = []
for index, test in enumerate(captured['tests']):
    identity = test.id().rsplit('.', 1)[0]
    if groups and groups[-1]['class_identity'] == identity:
        groups[-1]['test_count'] += 1
        continue
    groups.append(dict(class_identity=identity, first_test=index, test_count=1, skip_guard=guard_of(type(test))))
sys.stdout = sys.__stdout__
print('\0REGEN_RESULT\0' + json.dumps(dict(tests=rows, verbosity=captured['verbosity'], via=captured['via'],
                                            groups=groups)))
'''


def main_block(tree):
    return [n for n in tree.body if isinstance(n, ast.If) and '__name__' in ast.unparse(n.test)]


def called_functions(nodes):
    return {n.func.id for b in nodes for n in ast.walk(b) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def classify(src, program):
    """Structural derivation of how the program selects its reported suite."""
    tree = ast.parse(src.read(program))
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    block = main_block(tree)
    reach = list(block)
    for name in called_functions(block):
        if name in functions:
            reach.append(functions[name])
    text = '\n'.join(ast.unparse(n) for n in reach)
    if 'unittest.main' in text:
        return dict(mode='main', derivation='DEFAULT_MODULE_OR_EXPLICIT_CLASS_SELECTION')
    if 'TextTestRunner' in text:
        if re.search(r"add_argument\('--suite', choices=", text) and "add_argument('--case'" in text:
            return dict(mode='main', derivation='EXACT_NAMED_SUITE_AND_OPTIONAL_CASE')
        exact = re.search(r"len\(actual\) != ([0-9]+)", text)
        if exact and 'guard-golden.json' in text:
            return dict(mode='main', derivation='EXACT_%s_PLUS_PINNED_ADDITIVE_GROUPS' % exact.group(1))
        if re.search(r'if args\.test else unittest\.defaultTestLoader\.loadTestsFromTestCase\(\w+\)', text):
            return dict(mode='main', derivation='DEFAULT_COMPLETE_CLASS')
        kinds = re.search(r'loadTestsFromTestCase\(kind\) for kind in \(([\w, ]+)\)', text)
        if kinds and len([k for k in kinds.group(1).split(',') if k.strip()]) == 2:
            return dict(mode='main', derivation='TWO_EXPLICIT_SOURCE_CONTROL_CLASSES')
        fail('unclassified runner shape: ' + program)
    # The runner is reached only through a helper the default main path calls.
    for name, function in functions.items():
        body = ast.unparse(function)
        if 'TextTestRunner' not in body:
            continue
        loop = re.search(r'for cases in \(([\w, ]+)\):', body)
        verbosity = re.search(r'TextTestRunner\(verbosity=([0-9])\)', body)
        if loop and 'consumer' in name:
            classes = [k.strip() for k in loop.group(1).split(',') if k.strip()]
            return dict(mode='static', classes=classes, verbosity=int(verbosity.group(1)) if verbosity else 1,
                        derivation='ONE_DEFAULT_CONSUMER_BOUNDARY_SUITE')
    fail('no reachable runner: ' + program)


def enumerate_slot(work_repo, program, flags, arguments, shape, python):
    spec = dict(repo=work_repo, program_path=os.path.join(work_repo, *program.split('/')), arguments=arguments,
                mode=shape['mode'], classes=shape.get('classes'), verbosity=shape.get('verbosity'),
                disabled_requirement=DISABLED_REQUIREMENT)
    child = os.path.join(os.path.dirname(work_repo), 'regen_child.py')
    environment = {k: v for k, v in os.environ.items() if not re.fullmatch(r'R00[0-9A-Z]+_.*', k)}
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    environment['TMPDIR'] = os.path.join(os.path.dirname(work_repo), 'tmp')
    process = subprocess.run([python, *sorted(set(flags) | {'-B'}), child, json.dumps(spec)], cwd=work_repo,
                             capture_output=True, env=environment, timeout=900)
    marker = b'\0REGEN_RESULT\0'
    if marker not in process.stdout:
        fail('enumeration failed for %s %r: rc=%s\n%s' % (program, arguments, process.returncode,
                                                         process.stderr.decode(errors='replace')[-3000:]))
    return json.loads(process.stdout.split(marker, 1)[1])


def materialize(src, base):
    """Disposable copy of every tracked file (exact bytes and executable bits)."""
    repo = os.path.join(base, 'repo')
    for path in sorted(src.entries):
        target = os.path.join(repo, *path.split('/'))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as handle:
            handle.write(src.read(path))
        os.chmod(target, 0o755 if src.entries[path][0] == '100755' else 0o644)
    os.makedirs(os.path.join(base, 'tmp'))
    with open(os.path.join(base, 'regen_child.py'), 'w', encoding='utf-8') as handle:
        handle.write(CHILD)
    return repo


def report_slots(src, work_repo, python, log):
    direct = [line for _, line, _ in slot_lines(src, REGISTRY)
              if re.match(r'\s*(?:[A-Z_]+=\S+\s+)*(?:python3?|py|"\$\{?py[A-Za-z_]*)', line)]
    if direct:
        fail('registry invokes a unittest program directly; this derivation covers wrapper lines only')
    slots, occurrences = [], {}
    for wrapper in registry_wrappers(src):
        node = 'COMMAND:%s:%d' % (wrapper, occurrences.get(wrapper, 0))
        occurrences[wrapper] = occurrences.get(wrapper, 0) + 1
        for number, line, program in slot_lines(src, wrapper):
            shape = classify(src, program)
            flags, arguments = invocation_argv(line, program, work_repo)
            result = enumerate_slot(work_repo, program, flags, arguments, shape, python)
            slot = dict(ordinal=len(slots), wrapper=wrapper, registry_node=node, line=number,
                        invocation=line.strip(), program=program, stream='stderr', verbosity=result['verbosity'],
                        derivation=shape['derivation'], test_count=len(result['tests']), tests=result['tests'])
            if wrapper == WG_VERIFIER_WRAPPER:
                slot['source_class_groups'] = result['groups']
            log('slot %3d %-55s %4d tests v%d %s' % (slot['ordinal'], program[-55:], slot['test_count'],
                                                     slot['verbosity'], shape['derivation']))
            slots.append(slot)
    return slots


# --------------------------------------------------------------------------
# Source-inline stderr: a test-method shell fragment `printf '<literal>' >&2`
# whose bytes reach the report stream between progress marks.
# --------------------------------------------------------------------------
PRINTF_STDERR = re.compile(r"^printf '([^'%]*)' >&2$", re.M)


def printf_bytes(fmt):
    out, i = bytearray(), 0
    simple = {'n': 10, 't': 9, 'r': 13, 'a': 7, 'b': 8, 'f': 12, 'v': 11, '\\': 92}
    while i < len(fmt):
        c = fmt[i]
        if c == '\\' and i + 1 < len(fmt):
            octal = re.match(r'[0-7]{1,3}', fmt[i + 1:])
            if octal:
                out.append(int(octal.group(0), 8) & 0xff); i += 1 + len(octal.group(0)); continue
            if fmt[i + 1] in simple:
                out.append(simple[fmt[i + 1]]); i += 2; continue
        out.extend(c.encode('utf-8')); i += 1
    return bytes(out)


def inline_stderr(src, slot):
    tree = ast.parse(src.read(slot['program']))
    methods = {}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for function in cls.body:
            if isinstance(function, ast.FunctionDef):
                methods[(cls.name, function.name)] = function
    rows = []
    for ordinal, test in enumerate(slot['tests']):
        module, cls, name = test['id'].rsplit('.', 2)
        function = methods.get((cls, name)) if module == '__main__' else None
        if function is None:
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for match in PRINTF_STDERR.finditer(node.value):
                    body = printf_bytes(match.group(1))
                    if body and b'\n' not in body and b'\r' not in body:
                        pin = src.pin(slot['program'])
                        rows.append(dict(test_ordinal=ordinal, test_id=test['id'], source_path=slot['program'],
                                         source={'bytes': pin['bytes'], 'sha256': pin['sha256']},
                                         bytes=len(body), sha256=sha256(body),
                                         body_base64=base64.b64encode(body).decode()))
    return rows


# --------------------------------------------------------------------------
# source_closure: predecessor membership plus every file changed since the
# predecessor's source commit (the observed 51416 transition rule), plus any
# member a slot itself names.  Pins are always recomputed from this source.
# --------------------------------------------------------------------------
def changed_paths(src, old, new, git_dir):
    git = ['git', '--git-dir=' + git_dir] if git_dir else ['git', '-C', src.root]
    out = subprocess.run([*git, 'diff', '--name-only', '--no-renames', '-z', old, new],
                         capture_output=True, check=True).stdout
    return [p.decode('utf-8') for p in out.split(b'\0') if p]


def source_closure(src, slots, predecessor, git_dir, log):
    members = set(predecessor['source_closure'])
    changed = changed_paths(src, predecessor['source_commit'], src.commit, git_dir)
    members |= set(changed)
    required = {REGISTRY} | {s['program'] for s in slots} | {s['wrapper'] for s in slots}
    for s in slots:
        required |= {g['skip_guard']['source_path'] for g in s.get('source_class_groups', []) if g['skip_guard']}
        required |= {r['source_path'] for r in s.get('source_inline_stderr', [])}
    added_required = sorted(required - members)
    members |= required
    dropped = sorted(p for p in members if not src.exists(p))
    members -= set(dropped)
    log('closure: predecessor %d, changed-since-predecessor %d, required-not-covered %d, dropped-absent %d -> %d'
        % (len(predecessor['source_closure']), len(changed), len(added_required), len(dropped), len(members)))
    return {p: src.pin(p) for p in sorted(members)}, dict(changed=sorted(changed), added_required=added_required,
                                                         dropped=dropped)


def build_report_slots(src, work_repo, python, predecessor, git_dir, log):
    slots = report_slots(src, work_repo, python, log)
    for slot in slots:
        rows = inline_stderr(src, slot)
        if rows:
            slot['source_inline_stderr'] = rows
    closure, closure_notes = source_closure(src, slots, predecessor, git_dir, log)
    return dict(authority='NONE', limits=RS_LIMITS, registry_sha256=sha256(src.read(REGISTRY)), schema=RS_SCHEMA,
                slot_count=len(slots), slots=slots, source_closure=closure, source_commit=src.commit,
                source_tree=src.tree, status=RS_STATUS), closure_notes


# --------------------------------------------------------------------------
# OUTPUT_ROLES.  Values are evaluated from the named producer sources in a
# child interpreter (definitions only; no producer main and no subprocess).
# --------------------------------------------------------------------------
ROLES_CHILD = r'''
import ast, contextlib, hashlib, importlib.util, io, json, os, subprocess, sys, types
spec = json.loads(sys.argv[1])
repo = spec['repo']
os.chdir(repo)
def refuse(*a, **k):
    raise RuntimeError('ROLE_EXTRACTION_SUBPROCESS_REFUSED')
def definitions(path, name):
    """Module with every top-level statement except its __main__ block."""
    tree = ast.parse(open(path, 'rb').read(), path)
    tree.body = [n for n in tree.body if not (isinstance(n, ast.If) and '__name__' in ast.unparse(n.test))]
    module = types.ModuleType(name); module.__file__ = path
    sys.modules[name] = module
    exec(compile(tree, path, 'exec'), module.__dict__)
    return module, tree
result = {}

# pending durability report constants and its source-bound refusal profile
pending, _ = definitions(os.path.join(repo, 'tests/cognition-pending-durability.py'), 'pending_role_source')
pins = pending.source_pins(pending.Path(repo))
result['pending'] = dict(ceiling=pending.CEILING, limitations=pending.LIMITATIONS, pins=pins,
                         profile=pending.reservation_refusal_profile(pins))

# historical six-source composition inputs (names from copy_continuity_engine)
path = os.path.join(repo, 'tests/work-graph-historical-fixture.py')
historical = importlib.util.spec_from_file_location('historical_role_source', path)
H = importlib.util.module_from_spec(historical); sys.modules['historical_role_source'] = H
historical.loader.exec_module(H)
tree = ast.parse(open(path, 'rb').read())
engine = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'copy_continuity_engine')
loop = [n for n in engine.body if isinstance(n, ast.For) and 'copy_input' in ast.unparse(n)][0]
names = ast.literal_eval(loop.iter)
prefix = ast.literal_eval(loop.body[0].value.args[0].left)
rows = []
for name in names:
    raw = H.input_bytes(prefix + name)
    rows.append([name, len(raw), hashlib.sha256(raw).hexdigest(), H.input_mode(prefix + name)])
result['composition_sources'] = rows

# turn-disposition case population: the producer's own case() calls, recorded only
path = os.path.join(repo, 'tests/turn-disposition-cases.py')
module, tree = definitions(path, 'turn_role_source')
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
case = next(n for n in ast.walk(main) if isinstance(n, ast.FunctionDef) and n.name == 'case')
record = ast.parse("results.append({'case': name, 'disposition': disposition, 'expected_accept': expected, 'pass': True})\nreturn").body
first = case.body[0]
case.body = ([first] if isinstance(first, ast.If) and 'r37_regressions_only' in ast.unparse(first) else []) + record
ast.fix_missing_locations(tree)
exec(compile(ast.Module(body=[main], type_ignores=[]), path, 'exec'), module.__dict__)
subprocess.check_output = lambda *a, **k: spec['commit'] + '\n'
subprocess.run = subprocess.Popen = subprocess.call = subprocess.check_call = refuse
sys.argv = [path]
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    module.main()
result['turn_cases'] = [dict(case=r['case'], disposition=r['disposition'], expected_accept=r['expected_accept'])
                        for r in json.loads(buffer.getvalue())['results']]
print('\0REGEN_RESULT\0' + json.dumps(result))
'''


def shell_logical_lines(text):
    """(first line number, logical line) outside heredoc bodies, continuations joined."""
    out, heredoc, pending, start = [], None, '', 0
    for index, line in enumerate(text.splitlines(), 1):
        if heredoc is not None:
            if (line.strip() if heredoc[1] else line) == heredoc[0]:
                heredoc = None
            continue
        if not pending:
            start = index
        if line.rstrip().endswith('\\'):
            pending += line.rstrip()[:-1] + ' '
            continue
        logical, pending = pending + line, ''
        opened = re.search(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2", logical)
        if opened and '<<<' not in logical:
            heredoc = (opened.group(3), opened.group(1) == '-')
        out.append((start, logical))
    return out


STDOUT_REDIRECT = re.compile(r'(?<![0-9&])>(?!&2)|&>|\|')
ROOT_TOKEN = '\0ROOT\0'


def expand(token, variables):
    def value(match):
        name = match.group(1) or match.group(2)
        if name not in variables:
            raise KeyError(name)
        return variables[name]
    return re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)', value, token)


BUILD_ROLES = {  # authored role labels of the wrappers whose release builds reach stdout
    'tests/release-asset.test.sh': 'release_asset', 'tests/release-asset-install.test.sh': 'codex_install',
    'tests/release-asset-install-claude.test.sh': 'claude_install', 'tests/plugin-install.test.sh': 'plugin_install',
    REGISTRY: 'release_check'}


def wrapper_build_entries(text):
    """Ordered ('build', dir) / ('checksum', manifest) writes printed to stdout at top level."""
    variables, loops, entries, depth = {}, [], [], 0
    for _, line in shell_logical_lines(text):
        words = line.strip()
        if re.match(r'[A-Za-z_][A-Za-z0-9_]*\(\)\s*\{', words) or re.match(r'function\b', words):
            depth += 1
        if depth:
            if words == '}':
                depth -= 1
            continue
        loop = re.fullmatch(r'for ([A-Za-z_]+) in ([^;$`"]+); do', words)
        if loop:
            loops.append((loop.group(1), loop.group(2).split(), len(entries)))
            continue
        if re.fullmatch(r'for .*; do', words):
            loops.append((None, None, len(entries)))
            continue
        if words == 'done' and loops:
            name, values, begin = loops.pop()
            if name is not None:
                body = entries[begin:]
                del entries[begin:]
                for value in values:
                    entries.extend((kind, target.replace('\0' + name + '\0', value)) for kind, target in body)
            continue
        scope = {**variables, **{n: '\0' + n + '\0' for n, _, _ in loops if n}}
        assignment = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*)=(?:("?)\$\(mktemp -d\)\2|"([^"`]*)")', words)
        if assignment:
            if assignment.group(3) is None:
                variables[assignment.group(1)] = ROOT_TOKEN
            else:
                try:
                    if '$(' in assignment.group(3):
                        raise KeyError(assignment.group(1))
                    variables[assignment.group(1)] = expand(assignment.group(3), scope)
                except KeyError:
                    variables.pop(assignment.group(1), None)
            continue
        if not words.startswith('bash ') or STDOUT_REDIRECT.search(words):
            continue
        tokens = shlex.split(words)
        try:
            if tokens[1].endswith('scripts/build-release-asset.sh') and len(tokens) == 3 and not tokens[2].startswith('-'):
                entries.append(('build', expand(tokens[2], scope)))
            elif tokens[1].endswith('scripts/write-release-checksums.sh') and '--check' not in tokens:
                entries.append(('checksum', expand(tokens[-1], scope)))
        except KeyError:
            fail('unresolved release-build operand: ' + words)
    return entries


def build_groups(src):
    """Release builds / checksum writes that reach the registry stdout, in registry order."""
    groups = []
    for number, line in shell_logical_lines(src.text(REGISTRY)):
        words = line.strip()
        if words == 'bash scripts/build-release-asset.sh --check':
            groups.append(dict(role=BUILD_ROLES[REGISTRY], subdir='', checksums=['CHECKSUMS.txt']))
            continue
        match = re.fullmatch(r'bash (tests/[A-Za-z0-9_.-]+\.test\.sh)', words)
        if not match:
            continue
        wrapper = match.group(1)
        entries = wrapper_build_entries(src.text(wrapper))
        if not entries:
            continue
        builds = [target for kind, target in entries if kind == 'build']
        if len(builds) != 1 or not builds[0].startswith(ROOT_TOKEN + '/') or wrapper not in BUILD_ROLES:
            fail('unsupported release-build population in ' + wrapper)
        checksums = []
        for kind, target in entries:
            target = target + '/CHECKSUMS.txt' if kind == 'build' else target
            relative = target[len(ROOT_TOKEN) + 1:]
            if not target.startswith(ROOT_TOKEN + '/') or '\0' in relative:
                fail('unresolved checksum destination in ' + wrapper)
            checksums.append(relative)
        groups.append(dict(role=BUILD_ROLES[wrapper], subdir=builds[0][len(ROOT_TOKEN) + 1:], checksums=checksums))
    return groups


def repository_cost_metrics(src):
    tree = ast.parse(src.read('fixtures/operational-evidence/repository-fence-cost-controls.py'))
    calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and
                    n.func.attr == 'measured' and isinstance(n.func.value, ast.Name) and n.func.value.id == 'self' and
                    n.args and isinstance(n.args[0], ast.Constant)), key=lambda n: (n.lineno, n.col_offset))
    return list(dict.fromkeys(n.args[0].value for n in calls))


def build_output_roles(src, work_repo, python, predecessor):
    child = os.path.join(os.path.dirname(work_repo), 'regen_roles_child.py')
    with open(child, 'w', encoding='utf-8') as handle:
        handle.write(ROLES_CHILD)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=os.path.join(os.path.dirname(work_repo), 'tmp'))
    process = subprocess.run([python, '-B', child, json.dumps(dict(repo=work_repo, commit=src.commit))], cwd=work_repo,
                             capture_output=True, env=environment, timeout=900)
    marker = b'\0REGEN_RESULT\0'
    if marker not in process.stdout:
        fail('role extraction failed: ' + process.stderr.decode(errors='replace')[-3000:])
    values = json.loads(process.stdout.split(marker, 1)[1])
    pending = values['pending']
    return dict(build_groups=build_groups(src), historical_composition_sources=values['composition_sources'],
                pending_ceiling=pending['ceiling'], pending_limitations=pending['limitations'],
                pending_reservation_profile=pending['profile'], pending_source_pins=pending['pins'],
                repository_cost_metrics=repository_cost_metrics(src), schema=OR_SCHEMA, source_commit=src.commit,
                # UNKNOWN derivation: membership and source_pack_slots are inherited from the predecessor.
                source_files={p: src.pin(p) for p in sorted(predecessor['source_files']) if src.exists(p)},
                source_pack_slots=predecessor['source_pack_slots'], source_tree=src.tree, status=OR_STATUS,
                turn_disposition_cases=values['turn_cases'])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--tree', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--predecessor-report-slots', required=True,
                        help='prior frozen REPORT_SLOTS.json; source_closure membership is inherited from it')
    parser.add_argument('--predecessor-output-roles', required=True,
                        help='prior frozen OUTPUT_ROLES.json; source_files membership and source_pack_slots')
    parser.add_argument('--git-dir', help='git directory when --source is not itself readable by this git')
    parser.add_argument('--python', default=sys.executable, help='interpreter for the enumeration children')
    parser.add_argument('--work', help='parent directory for the disposable source copy')
    args = parser.parse_args()
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        fail('run under CPython 3.11/3.12 (ast.dump format is part of guard_ast_sha256)')
    log = lambda message: print(message, file=sys.stderr, flush=True)
    src = Source(args.source, args.commit, args.tree, args.git_dir)
    with open(args.predecessor_report_slots, 'rb') as handle:
        prior_slots = json.loads(handle.read())
    with open(args.predecessor_output_roles, 'rb') as handle:
        prior_roles = json.loads(handle.read())
    base = tempfile.mkdtemp(prefix='regen-', dir=args.work)
    try:
        work_repo = materialize(src, base)
        slots, notes = build_report_slots(src, work_repo, args.python, prior_slots, args.git_dir, log)
        roles = build_output_roles(src, work_repo, args.python, prior_roles)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    os.makedirs(args.out, exist_ok=True)
    for name, value in (('REPORT_SLOTS.json', slots), ('OUTPUT_ROLES.json', roles)):
        raw = encode(value)
        with open(os.path.join(args.out, name), 'wb') as handle:
            handle.write(raw)
        log('%s %d bytes sha256 %s' % (name, len(raw), sha256(raw)))
    with open(os.path.join(args.out, 'CLOSURE_NOTES.json'), 'wb') as handle:
        handle.write(encode(dict(predecessor_source_commit=prior_slots['source_commit'], **notes)))


if __name__ == '__main__':
    main()
