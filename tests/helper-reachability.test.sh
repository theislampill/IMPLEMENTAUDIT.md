#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-helper-reachability.sh"

if [ ! -f "$checker" ]; then
  printf 'helper-reachability.test: missing checker: %s\n' "$checker" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

make_candidate() {
  local name="$1"
  local candidate="$tmp/$name"
  mkdir -p "$candidate/scripts" "$candidate/package" "$candidate/tests" \
    "$candidate/fixtures/scarce-resource-rehearsal" \
    "$candidate/fixtures/run-root-example/phases"
  cp -R "$repo_root/skills" "$candidate/skills"
  cp "$repo_root/scripts/package-contract.py" "$candidate/scripts/package-contract.py"
  cp -R "$repo_root/.codex-plugin" "$candidate/"
  cp -R "$repo_root/.claude-plugin" "$candidate/"
  cp -R "$repo_root/hooks" "$candidate/"
  cp "$repo_root/package/implementaudit-package.json" "$candidate/package/implementaudit-package.json"
  cp "$repo_root/tests/scarce-resource-rehearsal-contract.test.sh" "$candidate/tests/"
  cp "$repo_root/fixtures/scarce-resource-rehearsal/cases.json" \
    "$candidate/fixtures/scarce-resource-rehearsal/"
  cp "$repo_root/fixtures/run-root-example/phases/phase-1.md" \
    "$candidate/fixtures/run-root-example/phases/"
  printf '%s\n' "$candidate"
}

track_candidate() {
  local candidate="$1"
  git -C "$candidate" init --quiet
  git -C "$candidate" -c core.longpaths=true -c core.autocrlf=false add --all
}

expect_fail() {
  local label="$1" pattern="$2" candidate="$3" output
  track_candidate "$candidate"
  if output="$(bash "$checker" --census-only --repo-root "$candidate" 2>&1)"; then
    printf 'helper-reachability.test: %s unexpectedly passed\n' "$label" >&2
    exit 1
  fi
  if ! grep -Fq -- "$pattern" <<<"$output"; then
    printf 'helper-reachability.test: %s failed for the wrong reason\n%s\n' "$label" "$output" >&2
    exit 1
  fi
}

mutate_route() {
  local candidate="$1" helper="$2" column="$3" value="$4"
  python - \
    "$candidate/skills/implementaudit/references/repo-state-comparison.md" \
    "$helper" "$column" "$value" <<'PY'
import sys
from pathlib import Path

path, helper, column_text, value = sys.argv[1:]
column = int(column_text)
lines = Path(path).read_text(encoding="utf-8").splitlines()
prefix = f"helper-route: scripts/{helper}|"
matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matches) != 1:
    raise SystemExit(f"expected one route row for {helper}, got {len(matches)}")
parts = lines[matches[0]].split("|")
parts[column] = value
lines[matches[0]] = "|".join(parts)
Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

delete_route() {
  local candidate="$1" helper="$2"
  python - \
    "$candidate/skills/implementaudit/references/repo-state-comparison.md" \
    "$helper" <<'PY'
import sys
from pathlib import Path

path, helper = sys.argv[1:]
lines = Path(path).read_text(encoding="utf-8").splitlines()
prefix = f"helper-route: scripts/{helper}|"
kept = [line for line in lines if not line.startswith(prefix)]
if len(kept) != len(lines) - 1:
    raise SystemExit(f"expected one route row for {helper}")
Path(path).write_text("\n".join(kept) + "\n", encoding="utf-8")
PY
}

positive_output="$(bash "$checker" --repo-root "$repo_root")"
grep -Eq 'HELPER_REACHABILITY=PASS population=([0-9]+) examined=\1 modes=5/5 enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2' \
  <<<"$positive_output" || {
    printf 'helper-reachability.test: live positive census did not prove complete role equality\n%s\n' "$positive_output" >&2
    exit 1
}

census_output="$(bash "$checker" --census-only --repo-root "$repo_root")"
grep -Eq 'HELPER_REACHABILITY_CENSUS=PASS population=([0-9]+) examined=\1 modes=5/5 enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2' \
  <<<"$census_output" || {
    printf 'helper-reachability.test: census-only result was not distinctly nonterminal\n%s\n' "$census_output" >&2
    exit 1
  }

# R001E must count the scarce-resource rehearsal as a distinct governed mode,
# rather than treating the authorization-record mode as its proxy.
grep -Fqx \
  'helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: R001E rehearsal mode is missing from the route population\n' >&2
    exit 1
  }
grep -Fq 'native audit object opens a scarce-resource phase' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: R001E rehearsal caller/trigger is missing\n' >&2
    exit 1
  }

missing_mode="$(make_candidate missing-mode)"
sed -i '/^helper-mode: validate-run-root.sh|--graph-parent|/d' \
  "$missing_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M1 \
  'missing mode applicability rows: validate-run-root.sh --graph-parent' \
  "$missing_mode"

unimplemented_mode="$(make_candidate unimplemented-mode)"
printf '%s\n' \
  'helper-mode: validate-run-root.sh|--graph-invented|<catalog>|invented' \
  >>"$unimplemented_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M2 \
  'mode applicability not implemented: validate-run-root.sh --graph-invented' \
  "$unimplemented_mode"

missing_mode_dispatch="$(make_candidate missing-mode-dispatch)"
sed -i 's/--graph-scope <catalog> <repo> <path> \[path\.\.\.\]/--graph-scope is available/' \
  "$missing_mode_dispatch/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M3 \
  'mode arguments absent: validate-run-root.sh --graph-scope' \
  "$missing_mode_dispatch"

missing_rehearsal_mode="$(make_candidate missing-rehearsal-mode)"
sed -i '/^helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|/d' \
  "$missing_rehearsal_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M4 \
  'missing mode applicability rows: check-authorization-binding.sh --phase --rehearsal --launch' \
  "$missing_rehearsal_mode"
grep -Fq 'One audit object; no event, no sweep.' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: same-object/no-event contract is missing\n' >&2
    exit 1
  }

missing_row="$(make_candidate missing-row)"
delete_route "$missing_row" check-authorization-binding.sh
expect_fail R30-F1 'missing applicability rows: check-authorization-binding.sh' "$missing_row"

self_reference="$(make_candidate self-reference)"
mutate_route "$self_reference" check-authorization-binding.sh 3 scripts/check-authorization-binding.sh
expect_fail R30-F2 'dispatch owner cannot be the helper itself: check-authorization-binding.sh' "$self_reference"

missing_dispatch="$(make_candidate missing-dispatch)"
mutate_route "$missing_dispatch" check-authorization-binding.sh 3 references/goal-format.md
expect_fail R30-F5 'dispatch owner does not name helper check-authorization-binding.sh' "$missing_dispatch"

presence_only="$(make_candidate presence-only)"
printf '\ncheck-authorization-binding.sh exists in the package and has direct tests.\n' \
  >>"$presence_only/skills/implementaudit/references/goal-format.md"
mutate_route "$presence_only" check-authorization-binding.sh 3 references/goal-format.md
expect_fail R30-F3/F4 \
  'procedural route absent: check-authorization-binding.sh' \
  "$presence_only"

bogus_trigger="$(make_candidate bogus-trigger)"
mutate_route "$bogus_trigger" check-authorization-binding.sh 2 none
expect_fail R30-F5 \
  'unanchored trigger: check-authorization-binding.sh: none' \
  "$bogus_trigger"

decoy_trigger="$(make_candidate decoy-trigger)"
mutate_route "$decoy_trigger" check-authorization-binding.sh 2 final
expect_fail R30-F5 \
  'unanchored trigger: check-authorization-binding.sh: final' \
  "$decoy_trigger"

bogus_arguments="$(make_candidate bogus-arguments)"
mutate_route "$bogus_arguments" check-authorization-binding.sh 5 bogus-arguments
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: bogus-arguments' \
  "$bogus_arguments"

decoy_arguments="$(make_candidate decoy-arguments)"
mutate_route "$decoy_arguments" check-authorization-binding.sh 5 'state invocation authorization'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: state invocation authorization' \
  "$decoy_arguments"

swapped_arguments="$(make_candidate swapped-arguments)"
mutate_route "$swapped_arguments" check-authorization-binding.sh 5 \
  '--auth <state> --invocation <auth> --state <invocation>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <state> --invocation <auth> --state <invocation>' \
  "$swapped_arguments"

omitted_flag="$(make_candidate omitted-flag)"
mutate_route "$omitted_flag" check-authorization-binding.sh 5 \
  '--auth <a> <i> --state <s>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <a> <i> --state <s>' \
  "$omitted_flag"

truncated_arguments="$(make_candidate truncated-arguments)"
mutate_route "$truncated_arguments" check-authorization-binding.sh 5 '--auth <a>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <a>' \
  "$truncated_arguments"

argument_self_anchor="$(make_candidate argument-self-anchor)"
mutate_route "$argument_self_anchor" check-authorization-binding.sh 5 \
  '<check-authorization-binding>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: <check-authorization-binding>' \
  "$argument_self_anchor"

bogus_boundary="$(make_candidate bogus-boundary)"
mutate_route "$bogus_boundary" check-authorization-binding.sh 6 none
expect_fail R30-F5 \
  'unanchored boundary: check-authorization-binding.sh: none' \
  "$bogus_boundary"

decoy_boundary="$(make_candidate decoy-boundary)"
mutate_route "$decoy_boundary" check-authorization-binding.sh 6 final
expect_fail R30-F5 \
  'unanchored boundary: check-authorization-binding.sh: final' \
  "$decoy_boundary"

bad_class="$(make_candidate bad-class)"
mutate_route "$bad_class" check-authorization-binding.sh 1 U
expect_fail R30-F1 'invalid applicability class U for check-authorization-binding.sh' "$bad_class"

missing_caller="$(make_candidate missing-caller)"
mutate_route "$missing_caller" check-respec-impact-set.sh 4 scripts/missing-caller.sh
expect_fail R30-F11 'unshipped caller: check-respec-impact-set.sh: scripts/missing-caller.sh' "$missing_caller"

repo_only_caller="$(make_candidate repo-only-caller)"
mutate_route "$repo_only_caller" check-respec-impact-set.sh 4 ../../tests/helper-reachability.test.sh
expect_fail R30-F11 \
  'invalid caller: check-respec-impact-set.sh: ../../tests/helper-reachability.test.sh' \
  "$repo_only_caller"

mention_only_caller="$(make_candidate mention-only-caller)"
mutate_route "$mention_only_caller" check-respec-impact-set.sh 4 R
expect_fail R30-F11 \
  'caller is not a shipped script: check-respec-impact-set.sh: references/repo-state-comparison.md' \
  "$mention_only_caller"

mention_only_script="$(make_candidate mention-only-script)"
printf '\n# bash scripts/check-respec-impact-set.sh\ntrue # bash scripts/check-respec-impact-set.sh\n' \
  >>"$mention_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$mention_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$mention_only_script"

echo_only_script="$(make_candidate echo-only-script)"
printf '\necho bash scripts/check-respec-impact-set.sh\n' \
  >>"$echo_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$echo_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$echo_only_script"

printf_only_script="$(make_candidate printf-only-script)"
printf "\nprintf '%%s\\n' 'bash scripts/check-respec-impact-set.sh'\n" \
  >>"$printf_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$printf_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$printf_only_script"

bash_parse_only="$(make_candidate bash-parse-only)"
printf '\nbash -n scripts/check-respec-impact-set.sh\n' \
  >>"$bash_parse_only/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$bash_parse_only" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$bash_parse_only"

exec_echo_only="$(make_candidate exec-echo-only)"
printf '\nexec echo scripts/check-respec-impact-set.sh\n' \
  >>"$exec_echo_only/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$exec_echo_only" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$exec_echo_only"

bash_command_echo="$(make_candidate bash-command-echo)"
printf "\nbash -c 'echo scripts/check-respec-impact-set.sh'\n" \
  >>"$bash_command_echo/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$bash_command_echo" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$bash_command_echo"

prefix_collision="$(make_candidate prefix-collision)"
printf '\nbash scripts/not-check-respec-impact-set.sh\n' \
  >>"$prefix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$prefix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$prefix_collision"

suffix_collision="$(make_candidate suffix-collision)"
printf '\nbash scripts/check-respec-impact-set.sh-not\n' \
  >>"$suffix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$suffix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$suffix_collision"

variable_prefix_collision="$(make_candidate variable-prefix-collision)"
printf '\nfake_checker="scripts/not-check-respec-impact-set.sh"\nbash "$fake_checker"\n' \
  >>"$variable_prefix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$variable_prefix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$variable_prefix_collision"

variable_suffix_collision="$(make_candidate variable-suffix-collision)"
printf '\nfake_checker="scripts/check-respec-impact-set.sh-not"\nbash "$fake_checker"\n' \
  >>"$variable_suffix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$variable_suffix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$variable_suffix_collision"

mandatory_advisory="$(make_candidate mandatory-advisory)"
mutate_route "$mandatory_advisory" lane-survivor-inventory.sh 6 must-block-closure
expect_fail R30-F8 'advisory/standalone row implies mandatory enforcement: lane-survivor-inventory.sh' "$mandatory_advisory"

owner_overclaim="$(make_candidate owner-overclaim)"
printf '\nlane-survivor-inventory.sh\nmust gate closure.\n' \
  >>"$owner_overclaim/skills/implementaudit/references/child-agents.md"
expect_fail R30-F8 \
  'advisory owner overclaim: lane-survivor-inventory.sh' \
  "$owner_overclaim"

future_helper="$(make_candidate future-helper)"
cp "$future_helper/skills/implementaudit/scripts/detect-stack.sh" \
  "$future_helper/skills/implementaudit/scripts/future-helper.sh"
expect_fail R30-F20 'missing applicability rows: future-helper.sh' "$future_helper"

extra_row="$(make_candidate extra-row)"
printf '%s\n' \
  'helper-route: scripts/ghost-helper.sh|S|owner-diagnosis|R|-|none|never-automatic' \
  >>"$extra_row/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-F11 'applicability rows not in package: ghost-helper.sh' "$extra_row"

printf 'helper-reachability.test: retained controls passed (dynamic full-role census + modes 5/5 + R30-F1-F5/F8/F11/F20/M1-M4 controls)\n'

# These tests exercise the maintained classifier, not a parallel declaration bank.
python -B - "$repo_root" "$checker" "$tmp" "$BASH" <<'PY'
import ast,json,os,pathlib,re,shutil,subprocess,sys
repo,checker,temp,bash=map(pathlib.Path,sys.argv[1:])
env=dict(os.environ);env["PYTHONDONTWRITEBYTECODE"]="1"
results=[]
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.encode())
def stage(root):
    assert root.resolve().is_relative_to(temp.resolve())
    for args in (["init","-q"],["-c","core.longpaths=true","-c","core.autocrlf=false","add","--all"]):
        p=subprocess.run(["git","-C",str(root),*args],env=env,capture_output=True,text=True,timeout=20)
        assert p.returncode==0,p.stderr
def make(name):
    root=temp/("typed-"+name);root.mkdir()
    shutil.copytree(repo/"skills",root/"skills")
    for rel in ("scripts/package-contract.py","package/implementaudit-package.json",
                ".codex-plugin/plugin.json",".claude-plugin/plugin.json",".claude-plugin/marketplace.json","hooks/hooks.json"):
        dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/rel,dst)
    return root
def owner(root):return root/"skills/implementaudit/references/repo-state-comparison.md"
def append(root,text):
    p=owner(root);write(p,p.read_text(encoding="utf-8")+"\n"+text+"\n")
def replace(root,rel,old,new):
    p=root/rel;s=p.read_text(encoding="utf-8");assert old in s,(rel,old);write(p,s.replace(old,new))
def function_replace(root,rel,name,old,new):
    p=root/rel;s=p.read_text(encoding="utf-8");lines=s.splitlines(True)
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name)
    part="".join(lines[node.lineno-1:node.end_lineno]);assert old in part,(rel,name,old)
    write(p,"".join(lines[:node.lineno-1])+part.replace(old,new)+"".join(lines[node.end_lineno:]))
def syntax_replace(root,rel,name,old,new,branch=None):
    """Mutate one proved current expression/statement, independent of formatting."""
    p=root/rel;s=p.read_text(encoding="utf-8");tree=ast.parse(s)
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name]
    assert len(functions)==1,(rel,name,"function population")
    scope=functions[0]
    if branch is not None:
        expected=ast.dump(ast.parse(branch,mode="eval").body,include_attributes=False)
        branches=[node for node in scope.body if isinstance(node,ast.If) and ast.dump(node.test,include_attributes=False)==expected]
        assert len(branches)==1,(rel,name,"branch population")
        scope=branches[0]
    expected=ast.parse(old).body[0]
    if isinstance(expected,ast.Expr):expected=expected.value
    matches=[node for node in ast.walk(scope) if ast.dump(node,include_attributes=False)==ast.dump(expected,include_attributes=False)]
    assert len(matches)==1,(rel,name,old,"mutation population",len(matches))
    node=matches[0];raw=s.encode("utf-8");lines=raw.splitlines(keepends=True)
    start=sum(map(len,lines[:node.lineno-1]))+node.col_offset
    end=sum(map(len,lines[:node.end_lineno-1]))+node.end_col_offset
    changed=raw[:start]+new.encode("utf-8")+raw[end:]
    assert changed!=raw
    ast.parse(changed)
    write(p,changed.decode("utf-8"))
def run(name,root,exit_code,pattern="",program=checker):
    stage(root)
    p=subprocess.run([str(bash),str(program),"--census-only","--repo-root",str(root)],env=env,capture_output=True,text=True,timeout=30)
    ok=p.returncode==exit_code and pattern in p.stdout+p.stderr
    results.append({"id":name,"exit":p.returncode,"expected":exit_code,"ok":ok,"stdout":p.stdout,"stderr":p.stderr})
    if not ok:
        print(json.dumps(results[-1]),flush=True)
        raise AssertionError(name)
    print("helper-reachability: "+name+" passed",flush=True)
    return p.stdout
def diagnostic(root,name="typed-diagnostic.py",explained=True):
    write(root/"skills/implementaudit/scripts"/name,'#!/usr/bin/env python3\nif __name__ == "__main__":\n    print(1)\n')
    if explained:
        append(root,'## Typed fixture diagnostic\n\nThe standalone-diagnostic command is `python -B <skill-dir>/scripts/'+name+'`. It is not automatic.\nhelper-route: scripts/'+name+'|S|fixture-diagnosis|R#typed-fixture-diagnostic|-|none|not-auto')
    else:
        append(root,name+'\nhelper-route: scripts/'+name+'|S|diagnosis|R|-|none|not-auto')
base=make("full")
output=run("actual-full-role-population",base,0,"full_path_sets=equal projections=2")
count=int(re.search(r"population=(\d+)",output).group(1))
# BEGIN owner-flow regression controls (census-only; authored runtime fixtures).
import runpy,shlex
table="skills/implementaudit/references/repo-state-comparison.md"
for role,rel,helper,arguments,refusal in (
    ("S",table,"resolve-durable-identity.py","--canonical <identity>","advisory/standalone"),
    ("R","skills/implementaudit/references/child-agents.md","compile-work-graph.py",
     "<graph.json> <product-authority.json>","Python procedural invocation absent"),
):
    operand="<skill-dir>/scripts/"+helper
    before="python -B "+operand+" "+arguments
    quoted="python -c \"'"+operand+" "+arguments+"'\""
    code=ast.parse(shlex.split(quoted)[2])
    assert len(code.body)==1 and isinstance(code.body[0],ast.Expr)
    assert isinstance(code.body[0].value,ast.Constant) and isinstance(code.body[0].value.value,str)
    for case,command,expected in (
        ("py-3-script","py -3 "+operand+" "+arguments,0),
        ("bounded-script-options","python -I -S -B "+operand+" "+arguments,0),
        ("c-string-is-not-script",quoted,1),
        ("c-comment-is-not-script",'python -c "pass # '+operand+' '+arguments+'"',1),
        ("m-is-not-script","python -m foreign_module "+operand+" "+arguments,1),
        ("unknown-interpreter-option","python --unknown "+operand+" "+arguments,1),
        ("earlier-foreign-script","python <skill-dir>/foreign.py "+operand+" "+arguments,1),
        ("helper-operand-suffix","python "+operand+".foreign "+arguments,1),
    ):
        p=make("owner-flow-"+role+"-"+case)
        replace(p,rel,chr(96)+before+chr(96),chr(96)+command+chr(96))
        run("owner-flow-"+role+"-"+case,p,expected,
            "population="+str(count)+" examined="+str(count)+" modes=5/5" if expected==0 else
            "unanchored arguments" if role=="R" and case=="helper-operand-suffix" else refusal)

# The declared owner is checked even when the unchanged caller is valid.
# A different real owner selector is legitimate; equality is not the contract.
for role,helper,owner_source,valid_owner in (
    ("I","child-load-visibility.py","scripts/child-parent-visibility.py","shared"),
    ("A","host-session-binding.py","scripts/compaction-audit-pending.py","main"),
):
    for selector,expected in (("NO_SUCH_OWNER_FUNCTION",1),(valid_owner,0)):
        p=make("owner-flow-"+role+"-"+selector)
        row=next(line for line in owner(p).read_text(encoding="utf-8").splitlines()
                 if line.startswith("helper-route: scripts/"+helper+"|"))
        fields=row.split("|");caller=fields[4];fields[3]=owner_source+"#"+selector
        assert fields[3]!=caller
        tree=ast.parse((p/"skills/implementaudit"/owner_source).read_bytes())
        functions={node.name for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        assert (selector in functions)==(expected==0) and caller.partition("#")[2] in functions
        replace(p,table,row,"|".join(fields))
        run("owner-flow-"+role+"-"+selector,p,expected,
            "Python dispatch owner function absent" if expected else "full_path_sets=equal projections=2")

owner_flow_runtime_witnesses=[]
def branch_fixture(overwrite):
    p=make("owner-flow-branch-"+str(overwrite));scripts=p/"skills/implementaudit/scripts"
    caller,wanted,a,b="review_branch_caller.py","review_wanted.py","review_other_a.py","review_other_b.py"
    prefix='from pathlib import Path\nimport importlib.util\ndef load(flag):\n    target = Path(__file__).with_name("review_wanted.py")\n'
    branches=('    if flag:\n        target = Path(__file__).with_name("review_other_a.py")\n'
              '    else:\n        target = Path(__file__).with_name("review_other_b.py")\n') if overwrite else ''
    suffix=('    spec = importlib.util.spec_from_file_location("review_fixture", target)\n'
            '    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module\n')
    write(scripts/caller,prefix+branches+suffix)
    for name in (wanted,a,b):write(scripts/name,"VALUE = "+repr(name)+"\n")
    rows=["## Review branch fixture\n"]
    for name in (caller,a,b):
        rows.extend(["The standalone-diagnostic command is `python -B <skill-dir>/scripts/"+name+"`. It is not automatic.",
                     "helper-route: scripts/"+name+"|S|diagnosis|R#review-branch-fixture|-|none|not-auto"])
    rows.append("helper-route: scripts/"+wanted+"|I|selected-load|scripts/"+caller+"#load|scripts/"+caller+"#load|module|indirect-only")
    append(p,"\n".join(rows))
    load=runpy.run_path(str(scripts/caller))["load"]
    observed=[load(flag).VALUE for flag in (False,True)]
    assert observed==([b,a] if overwrite else [wanted,wanted])
    owner_flow_runtime_witnesses.append({"overwrite":overwrite,"flags":[False,True],"loaded":observed})
    return p
p=branch_fixture(False)
run("owner-flow-branch-direct",p,0,"population="+str(count+4)+" examined="+str(count+4)+" modes=5/5")
p=branch_fixture(True)
run("owner-flow-branch-both-overwrite",p,1,"Python caller edge unresolved: review_wanted.py")
print("helper-reachability: authored branch runtime witnesses "+json.dumps(owner_flow_runtime_witnesses),flush=True)
# END owner-flow regression controls.
p=make("python-unclassified");write(p/"skills/implementaudit/scripts/unrouted-control.py","print(1)\n")
run("heldout-python",p,1,"missing applicability rows")
for name in ("unknown.opaque","unknown"):
    p=make(name);write(p/"skills/implementaudit/scripts"/name,"unknown executable\n")
    run("unknown-type-"+name,p,1,"UNKNOWN_EXECUTABLE_TYPE")
p=make("same-count");(p/"skills/implementaudit/scripts/detect-stack.sh").unlink();write(p/"skills/implementaudit/scripts/replacement.py","print(1)\n")
run("count-preserving-substitution",p,1,"missing applicability rows")
p=make("lower");(p/"skills/implementaudit/scripts/detect-stack.sh").unlink()
replace(p,"skills/implementaudit/references/repo-state-comparison.md",
        next(l for l in owner(p).read_text(encoding="utf-8").splitlines() if l.startswith("helper-route: scripts/detect-stack.sh|"))+"\n","")
run("dynamic-lower",p,0,"population="+str(count-1)+" examined="+str(count-1))
p=make("higher");diagnostic(p)
run("dynamic-higher",p,0,"population="+str(count+1)+" examined="+str(count+1))
direct=subprocess.run([sys.executable,"-B",str(p/"skills/implementaudit/scripts/typed-diagnostic.py")],cwd=p,env=env,capture_output=True,text=True,timeout=10)
assert direct.returncode==0 and direct.stdout=="1\n" and not direct.stderr
p=make("unexplained");diagnostic(p,explained=False)
run("F1-unexplained-dormancy",p,1,"advisory/standalone")
p=make("echo-invocation");diagnostic(p)
replace(p,"skills/implementaudit/references/repo-state-comparison.md","`python -B <skill-dir>/scripts/typed-diagnostic.py`","`echo python -B <skill-dir>/scripts/typed-diagnostic.py`")
run("F1-echo-is-not-invocation",p,1,"advisory/standalone")
p=make("split-command");diagnostic(p)
replace(p,"skills/implementaudit/references/repo-state-comparison.md",
 chr(96)+"python -B <skill-dir>/scripts/typed-diagnostic.py"+chr(96),
 chr(96)+"echo python -B <skill-dir>/scripts/typed-diagnostic.py"+chr(96)+" and "+chr(96)+"python -B <skill-dir>/scripts/typed-diagnostic.py --foreign"+chr(96))
run("F1-split-argument-and-command-anchor",p,1,"advisory/standalone")
p=make("wrong-interpreter");diagnostic(p)
replace(p,"skills/implementaudit/references/repo-state-comparison.md","`python -B <skill-dir>/scripts/typed-diagnostic.py`","`bash <skill-dir>/scripts/typed-diagnostic.py`")
run("F1-wrong-interpreter",p,1,"advisory/standalone")
p=make("missing-role-explanation");diagnostic(p)
replace(p,"skills/implementaudit/references/repo-state-comparison.md","The standalone-diagnostic command is","The listed command is")
run("F1-unexplained-role",p,1,"advisory/standalone")
p=make("nested-name");write(p/"skills/implementaudit/scripts/nested/detect-stack.sh","#!/usr/bin/env bash\ntrue\n")
run("nested-fullpath",p,1,"nested/detect-stack.sh")
p=make("duplicate");append(p,next(l for l in owner(p).read_text(encoding="utf-8").splitlines() if l.startswith("helper-route: scripts/detect-stack.sh|")))
run("duplicate-member-row",p,1,"duplicate applicability row")
p=make("extra");append(p,"helper-route: scripts/ghost.py|S|diagnosis|R|-|none|not-auto")
run("extra-member-row",p,1,"applicability rows not in package")
p=make("missing-override");text=owner(p).read_text(encoding="utf-8");row=next(l for l in text.splitlines() if l.startswith("helper-role: ") and "codex-compact-interlock.py" in l)
write(owner(p),text.replace(row+"\n",""))
run("missing-standalone-override",p,1,"unshipped dispatch owner")
p=make("duplicate-role");append(p,next(l for l in owner(p).read_text(encoding="utf-8").splitlines() if l.startswith("helper-role: ")))
run("duplicate-role-row",p,1,"duplicate role row")
p=make("unknown-role");replace(p,"skills/implementaudit/references/repo-state-comparison.md","helper-role: standalone_compatibility|","helper-role: invented_role|")
run("unknown-role",p,1,"invalid role/member")
p=make("dormant-explanation")
doc=p/"skills/implementaudit/references/host-session-binding.md";text=doc.read_text(encoding="utf-8")
write(doc,text.split("## Standalone hook compatibility",1)[0]+"## Standalone hook compatibility\n\nscripts/codex-compact-interlock.py\nscripts/codex-recovery-prompt-input.py\nscripts/host-stop-interlock.py\n")
run("dormant-without-explanation",p,1,"unproved dormant role")
p=make("hook-counterpart");path=p/"hooks/hooks.json";data=json.loads(path.read_text(encoding="utf-8"));del data["hooks"]["UserPromptSubmit"];write(path,json.dumps(data))
run("missing-canonical-hook-counterpart",p,1,"hook caller does not invoke")
p=make("hook-windows-target");path=p/"hooks/hooks.json";data=json.loads(path.read_text(encoding="utf-8"))
entry=data["hooks"]["UserPromptSubmit"][0]["hooks"][0];entry["commandWindows"]=entry["commandWindows"].replace("scripts"+chr(92)+"codex-","scripts"+chr(92)+"nested"+chr(92)+"codex-");write(path,json.dumps(data))
run("foreign-Windows-hook-path",p,1,"hook caller does not invoke")
p=make("bad-owner");replace(p,"skills/implementaudit/references/repo-state-comparison.md","skills/audit-implement/SKILL.md#canonical-return-envelope-consumer","../audit-implement/SKILL.md#canonical-return-envelope-consumer")
run("role-owner-parent-escape",p,1,"invalid dispatch owner")
p=make("missing-child-command");replace(p,"skills/audit-implement/SKILL.md",
        "`python -B <skill-dir>/scripts/validate-audit-implement-return.py",
        "`available <skill-dir>/scripts/validate-audit-implement-return.py")
run("child-owner-exact-command",p,1,"Python procedural invocation absent")
p=make("unknown-loader")
function_replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","shared",
 "spec = importlib.util.spec_from_file_location('shared_child_visibility', path)",
 "spec = unknown_factory(path)")
run("unknown-Python-loader",p,1,"Python caller edge unresolved")
p=make("forged-importlib")
replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","import importlib.util","import fabricated as importlib")
run("untrusted-loader-namespace",p,1,"Python caller edge unresolved")
p=make("unbound-path")
replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","from pathlib import Path","")
run("unbound-Path-is-not-pathlib",p,1,"Python caller edge unresolved")
p=make("dead-loader")
function_replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","shared",
 "global _shared","global _shared\n    return None")
run("dead-Python-loader",p,1,"Python caller edge unresolved")
p=make("API-unused")
function_replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","encode",
 "return shared().encode(value)","return shared()")
run("API-import-only-is-not-use",p,1,"Python caller edge unresolved")
p=make("API-absent")
replace(p,"skills/implementaudit/scripts/child-load-visibility.py","def encode(value):","def missing_encode(value):")
run("API-export-absent",p,1,"Python caller edge unresolved")
p=make("resolver-missing-argument")
resolver_argv='[sys.executable, str(resolver), "--governor", str(governor), "--child", mapped_child]'
syntax_replace(p,"skills/implementaudit/scripts/route-transaction.py","resolved_child_delivery_path",
 resolver_argv,'[sys.executable, str(resolver), "--governor", str(governor)]')
run("resolver-missing-child-argument",p,1,"Python caller edge unresolved")
p=make("wrong-interpreter-source")
syntax_replace(p,"skills/implementaudit/scripts/route-transaction.py","resolved_child_delivery_path",
 resolver_argv,'["unowned-python", str(resolver), "--governor", str(governor), "--child", mapped_child]')
run("unowned-Python-interpreter",p,1,"Python caller edge unresolved")
p=make("wrong-fullpath-caller")
lib=p/"skills/implementaudit/scripts/child-load-visibility.py"
write(p/"skills/implementaudit/scripts/nested/child-load-visibility.py",lib.read_text(encoding="utf-8"))
append(p,"helper-route: scripts/nested/child-load-visibility.py|I|selected-load|scripts/child-parent-visibility.py#encode|scripts/child-parent-visibility.py#encode|api:encode|indirect-only")
syntax_replace(p,"skills/implementaudit/scripts/child-parent-visibility.py","shared",
 "Path(__file__).resolve().with_name('child-load-visibility.py')",
 "Path(__file__).resolve().parent / 'nested' / 'child-load-visibility.py'")
run("same-basename-does-not-prove-caller",p,1,"Python caller edge unresolved")
# The exact maintained shared() consumer actually loads and uses its selected
# dependency on a harmless literal; corrupting that dependency is a refusal.
p=make("actual-source-loader")
driver="import importlib.util,pathlib,sys,json; p=pathlib.Path(sys.argv[1]); s=importlib.util.spec_from_file_location('actual_parent_consumer',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.loads(m.encode({'probe':1})))"
target=p/"skills/implementaudit/scripts/child-parent-visibility.py"
actual=subprocess.run([sys.executable,"-B","-c",driver,str(target)],cwd=p,env=env,capture_output=True,text=True,timeout=10)
assert actual.returncode==0 and actual.stdout.strip()=="{'probe': 1}" and not actual.stderr
dep=p/"skills/implementaudit/scripts/child-load-visibility.py";dep.write_bytes(dep.read_bytes()+b"\n# changed bounded source witness\n")
adverse=subprocess.run([sys.executable,"-B","-c",driver,str(target)],cwd=p,env=env,capture_output=True,text=True,timeout=10)
assert adverse.returncode!=0 and "Shared visibility source differs" in adverse.stderr
p=make("projection-divergence")
syntax_replace(p,"scripts/package-contract.py","artifact_payload_entries","return entries",
 "return [entry for entry in entries if entry[0] != 'skills/implementaudit/scripts/detect-stack.sh']",
 branch='role == "canonical_plugin"')
shutil.copyfile(checker,p/"scripts/check-helper-reachability.sh")
run("projection-parity",p,1,"executable projection parity differs",p/"scripts/check-helper-reachability.sh")
p=make("foreign-builder");f=p/"scripts/package-contract.py";write(f,f.read_text(encoding="utf-8")+"\nraise RuntimeError('UNTRUSTED_BUILDER_EXECUTED')\n")
run("foreign-builder-is-not-executed",p,1,"package owner differs")
print("helper-reachability: typed source/role controls complete; actual loader positive/refusal passed",flush=True)
PY


printf 'helper-reachability.test: ok (complete existing and typed-role controls)\n'
