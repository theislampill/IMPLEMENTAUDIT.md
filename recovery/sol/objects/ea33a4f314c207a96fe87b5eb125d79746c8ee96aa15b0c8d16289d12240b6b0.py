"""Source-only regression for the witnessed fetch scheduling correction."""
import argparse, ast, hashlib, json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('receipt',type=Path)
a=p.parse_args()
before=a.baseline.read_bytes();after=a.candidate.read_bytes()
assert hashlib.sha256(before).hexdigest()=='b4c9013c0c665df6c2e66c609f93d5a08c2e12905a7663d3d144419b64b69865'
b=ast.parse(before);c=ast.parse(after)
def fetch(tree):
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepare_source')
    hits=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='git'
          and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='fetch-selected-commit']
    assert len(hits)==1 and isinstance(hits[0].args[1],ast.List)
    return hits[0].args[1]
f=fetch(c);has_flag=(len(f.elts)>=2 and isinstance(f.elts[0],ast.Constant) and f.elts[0].value=='-c'
                    and isinstance(f.elts[1],ast.Constant) and f.elts[1].value=='maintenance.autoDetach=false')
rows=[dict(case='fetch-command-local-foreground-required',passed=has_flag)]
if has_flag:del f.elts[:2]
rows.append(dict(case='all-other-AST-including-detach-and-finalizer-unchanged',passed=ast.dump(b,include_attributes=False)==ast.dump(c,include_attributes=False)))
receipt=dict(status='PASS_SOURCE_ONLY' if all(r['passed'] for r in rows) else 'RED_MISSING_WITNESSED_COUNTERMEASURE',
             baseline_sha256=hashlib.sha256(before).hexdigest(),candidate_sha256=hashlib.sha256(after).hexdigest(),
             cases=rows,actual_Git_or_native_or_hosted_effects=0,whole_cell_or_original_awards=[])
a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
