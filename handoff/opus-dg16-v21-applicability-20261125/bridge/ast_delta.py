"""Top-level AST delta between two revisions of one Python file (comments/docstring-free view).

usage: python3 -I ast_delta.py <repo> <old-rev> <new-rev> <path>
Prints each differing top-level statement (by ast.dump) as a short label, so that a
reviewer can see whether the change is pin/data only or touches function bodies.
Docstrings are stripped so documentation-only edits do not register.
"""
import ast, difflib, hashlib, subprocess, sys

repo, old, new, path = sys.argv[1:5]

def strip_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree

def stmts(rev):
    raw = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{path}'], capture_output=True, check=True).stdout
    tree = strip_docstrings(ast.parse(raw))
    out = []
    for node in tree.body:
        label = type(node).__name__
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            label += ':' + node.name
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            label += ':' + ast.unparse(target)[:80]
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            label += ':' + ast.unparse(node)[:80]
        else:
            label += ':' + ast.unparse(node)[:60].replace('\n', ' ')
        out.append((label, hashlib.sha256(ast.dump(node).encode()).hexdigest()[:12]))
    whole = hashlib.sha256(ast.dump(tree).encode()).hexdigest()
    return out, whole

a, wa = stmts(old)
b, wb = stmts(new)
print(f'{path}: whole_ast_equal={wa == wb} old_stmts={len(a)} new_stmts={len(b)}')
sm = difflib.SequenceMatcher(a=[x[1] for x in a], b=[x[1] for x in b], autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    for x in a[i1:i2]:
        print('  -', x[0])
    for x in b[j1:j2]:
        print('  +', x[0])
