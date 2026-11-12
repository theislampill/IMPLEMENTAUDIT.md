#!/usr/bin/env python3
"""Author an actual bounded fresh task; no receipt, verdict, or completed work."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess

NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md')

def author(repo, run, source, purpose, next_action, only=None):
    repo, source = pathlib.Path(repo).absolute(), pathlib.Path(source).absolute()
    root = repo / run
    helper = source/'skills/implementaudit/scripts/claim-run.sh'
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    def git(*args): return subprocess.check_output(['git','-C',str(repo),*args],env=env,text=True).strip()
    head,tree = git('rev-parse','HEAD'),git('rev-parse','HEAD^{tree}')
    claim = dict(line.split('=',1) for line in (root/'.claimed').read_text().splitlines())
    controller = (root/'.controller').read_text().strip().split('=',1)[1]
    assert claim['repo_root']==repo.as_posix() and claim['run_root']==run
    assert purpose.strip() and next_action.strip() and '\n' not in next_action and '|' not in next_action
    templates = source/'skills/implementaudit/templates'
    state = (templates/'STATE.md').read_text()
    for name,value in [('Run root',run),('Phase','1'),('Route','brownfield'),('Baseline ref',head),('Next action',next_action)]:
        state=state.replace(f'| {name} |  |',f'| {name} | {value} |')
    anchor='| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
    timestamp=claim['claimed_at_utc']
    state=state.replace(anchor,anchor+f'\n| G0001 | new-session | {timestamp} | actual source `{head}` / `{tree}` | yes | Fresh authorized task; Git readback completed by this author; no predecessor session inherited |')
    state += '\n## Initialization authorization and actual scope\n\n'+purpose.strip()+'\n\n'
    state += 'This is a newly authored task checkpoint. No work, review, continuity receipt, original acceptance, publication, or completed phase is asserted. Activation and the normal continuity checks remain required.\n'
    phase=f'''# Phase 1 — Receive this bounded fresh task

IMPLEMENTAUDIT_PHASE_START
Task: {purpose}
Type: brownfield
Run root: {run}
Baseline ref: {head}
Owner/source: {run}/STATE.md and the actual source at {head}
Audit object: the owner-authorized bounded initialization and receiving task
Depends on phases: none

## Work

Establish verified fresh execution custody, then perform the stated receiving task. Preserve predecessor evidence as history. No completed result is inferred from initialization.

## Implementation steps (ordered)

- Step 1: Receive the initialized root — target: {run}; change: publish only after the initialization validator and expected-old guards pass; verify: run the public activation and normal continuity entry points; expected: exact real receipt verifies against this source and state.
- Step 2: Perform the authorized next action — target: the bounded task in STATE.md; change: {next_action}; verify: capture the actual operation and final readback; expected: the specific receiving result is supported without a duplicate predecessor effect.

## Scope boundaries

In scope: this fresh run's initialization, normal continuity, and the explicitly stated receiving task.
Out of scope: original incident custody reconstruction, protected bodies, credentials, publication, product commits, installed-home changes, or acceptance awards.

## STOP conditions (plan-specific)

- Stop if this root's claim, controller token, source HEAD/tree or initializer source differs from the received binding.
- Stop if an existing partial file conflicts with the real author input; preserve both observations and do not replace the file automatically.

## Current state excerpts

- Actual target HEAD is {head}; tree is {tree}.
- Actual claim ID is {claim['claim_id']}; controller is {controller}.
- No phase or effect is completed in this authored initial checkpoint.

## Acceptance criteria

- [ ] All seven real task files pass the existing structural validator under the authenticated pending context.
- [ ] Normal invalidate, resume, verify and require calls obtain and verify actual fresh continuity.
- [ ] The declared next action has its own real result and no duplicated predecessor effect.

## Mandatory commands

- bash {helper} --require-current-continuity {controller} > <run-root>/evidence/require-currentness.txt 2>&1 — property: behavioral; scope: this exact fresh controller; coverage: full; capture: <run-root>/evidence/require-currentness.txt; expected: exit 0 only after real receipt verification.

## Evidence required

- Actual CLI command captures, source/claim/ref readback, and the declared receiving result.
- Markdown fallback: yes; sidecars are not an authorization dependency for this task.

## Rollback / defer path

Retain incomplete custody and fail closed; remove only the explicitly owned disposable fixture after its selected evidence has been retained. Do not roll back an original controller or published effect.

## Maintenance notes

- Keep this phase bound to the actual task and source. It does not substitute for a reviewer or a continuity receipt.

IMPLEMENTAUDIT_PHASE_VERIFY
No verification passage is claimed in the initial checkpoint.

AGENTS_UPDATE_DECISION
No durable repository instruction change is requested by this receiving task.

CONTINUITY_DECISION
Preserve the actual fresh receipt only after the normal owner emits it.

IMPLEMENTAUDIT_PHASE_DONE
Status: open
'''
    docs={'STATE.md':state,'PROTOCOL.md':(templates/'PROTOCOL.md').read_text(),
          'ROADMAP.md':f'# Roadmap — bounded fresh receiving task\n\n{purpose}\n\n| # | Phase | Depends on | Status |\n|---|---|---|---|\n| 1 | Receive verified fresh custody and perform the declared receiving task | none | open |\n\nThinking file: `<run-root>/THINKING.md`\n',
          'THINKING.md':f'# Thinking — actual bounded task\n\nTop objective: {purpose}\nRoute: brownfield; owner/source: this fresh run and the actual target source {head}.\nTop closure risks: incomplete initialization, stale source, copied receipt, or duplicated predecessor effect.\nCountermeasure: exact pending token, retained input population, normal continuity, actual result readback.\nRollback: preserve incomplete evidence and stop; no original authority rollback.\nEvidence strategy: structural validation is separate from normal continuity and task success.\nSidecars are optional and grant no authority.\n',
          'sidecars.md':'# Sidecars\n\nNo sidecar is requested or needed for this bounded initialization task. No indexing or sidecar mutation is performed. Markdown evidence and actual owner CLI results supply this task\'s records.\n',
          'tools.md':'# Tools\n\n'+json.dumps({'bash':shutil.which('bash'),'git':shutil.which('git'),'python':shutil.which('python3'),'claim_owner':str(helper)},indent=2)+'\n\nOnly the declared owner operations and bounded receiving task are authorized.\n',
          'context.md':f'# Context — real fresh task\n\nOwner-provided objective: {purpose}\n\nActual repository: {repo}\nActual HEAD: {head}\nActual tree: {tree}\nActual claim: {claim["claim_id"]}\nActual controller: {controller}\n\nExecuting claim helper SHA256: {hashlib.sha256(helper.read_bytes()).hexdigest()}\n\nNo original controller continuity, hosted identity, independent review, publication, or acceptance is inferred.\n',
          'phases/phase-1.md':phase}
    selected=list(docs) if only is None else [only]
    for name in selected:
        data=docs[name].encode();p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():
            if p.read_bytes()!=data: raise RuntimeError(f'preserved conflicting existing initialization file: {name}')
            continue
        with p.open('xb') as h:h.write(data);h.flush();os.fsync(h.fileno())
    return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in selected}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--run-root',required=True);p.add_argument('--source',required=True);p.add_argument('--purpose',required=True);p.add_argument('--next-action',required=True);p.add_argument('--only',choices=(*NAMES,'phases/phase-1.md'));p.add_argument('--activate',action='store_true');p.add_argument('--activate-only',action='store_true')
    a=p.parse_args()
    result={} if a.activate_only else author(a.repo,a.run_root,a.source,a.purpose,a.next_action,a.only)
    if a.activate or a.activate_only:
        helper=pathlib.Path(a.source).absolute()/'skills/implementaudit/scripts/claim-run.sh'
        controller=(pathlib.Path(a.repo)/a.run_root/'.controller').read_text().strip().split('=',1)[1]
        bash=shutil.which('bash')
        if bash is None:raise SystemExit('controller initialization requires Bash')
        bash=str(pathlib.Path(bash).absolute())
        inspect=subprocess.run([bash,str(helper),'--inspect-controller-initialization',controller,'--run-root',a.run_root],cwd=a.repo,capture_output=True,text=True,check=True)
        token=json.loads(inspect.stdout)['initialization_token']
        active=subprocess.run([bash,str(helper),'--activate-controller',controller,'--run-root',a.run_root,'--expected-initialization',token],cwd=a.repo,capture_output=True,text=True,check=True)
        result={'authored_files':result,'activation':json.loads(active.stdout),'normal_currentness':'NOT_YET_ASSERTED'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
