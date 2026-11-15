#!/usr/bin/env python3
"""Public source harness: composer -> binder -> seven prepared receiver files.

Pure data assembly through the ORIGINAL Sol binder API (bind_public). Root-only inputs
(physical composition seal, distinct-review selection, author/reviewer identity) are either the
externally received records (actual modes) or clearly-labelled TEST inputs (g220-test).
Nothing here is a Root act, a seal, an admission or an effect grant.

pro-executor-actual uses the approved selection adapter and ORIGINAL frozen
structural files. Its binder argument must be the exact original binder, never
a regenerated pin-chain copy. Authentication of every supplied issuer, path,
review and adoption remains external; matching data does not establish it.

argv: <mode: g220-actual | g220-test | pro-executor-actual> <binder.py>
      <candidate-dir> <composition-dir> <issuer-dir> <out-dir> <json-out>
      [--composition-path P] [--candidate-path P] [--runtime F]
"""
import argparse, hashlib, importlib.util, json, os, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('mode', choices=['g220-actual', 'g220-test', 'pro-executor-actual']); p.add_argument('binder', type=Path)
p.add_argument('candidate', type=Path); p.add_argument('composition', type=Path); p.add_argument('issuer', type=Path)
p.add_argument('out', type=Path); p.add_argument('report', type=Path)
p.add_argument('--composition-path'); p.add_argument('--candidate-path'); p.add_argument('--runtime', type=Path)
p.add_argument('--author', default='/root'); p.add_argument('--reviewer'); p.add_argument('--install', action='store_true')
a = p.parse_args()
if a.mode == 'pro-executor-actual' and not __debug__:
    p.error('PRO_EXECUTOR_REQUIRES_ASSERTIONS')
sha = lambda b: hashlib.sha256(b).hexdigest()
desc = lambda b: dict(bytes=len(b), sha256=sha(b))
encode = lambda v: (json.dumps(v, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')
PREFIX = 'qualification/dg16-r5-full-g2/'
APPROVED_SEMANTIC_SHA256 = '9ad95ee8a9c696548501a0404d1029ab5ff79f070a88c2e22f9a44619c47716b'
DECISIONS = ('INDEPENDENT_COLD_REVIEW.json', 'ROOT_POLICY_ADOPTION.json',
             'NATIVE_INDEPENDENT_REVIEW.json', 'ROOT_NATIVE_APPLICABILITY_ADOPTION.json')

receiver = a.candidate / 'receiver'
if a.mode == 'pro-executor-actual':
    semantic_path = Path(__file__).resolve().parents[3] / 'qualification/dg16-github-evidence/semantic-integration/semantic_receiver.py'
    semantic_raw = semantic_path.read_bytes()
    if sha(semantic_raw) != APPROVED_SEMANTIC_SHA256:
        raise ValueError('APPROVED_SEMANTIC_PIN')
    spec = importlib.util.spec_from_file_location('approved_semantic', semantic_path)
    S = importlib.util.module_from_spec(spec)
    exec(compile(semantic_raw, str(semantic_path), 'exec', dont_inherit=True, optimize=0), S.__dict__)
    adapter_path = semantic_path.with_name('binding_adapter.py')
    adapter = S.module(S.pinned(adapter_path, S.BINDING_ADAPTER_SHA256, 'BINDING_ADAPTER_PIN'),
                       adapter_path, 'approved_binding_adapter')
    original_binder = S.pinned(a.binder.resolve(strict=True), S.ORIGINAL_BINDER_SHA256, 'ORIGINAL_BINDER_PIN')
    receiver = S.ORIGINAL_RECEIVER.parent
else:
    spec = importlib.util.spec_from_file_location('binder', a.binder); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
structural = {n: (receiver / n).read_bytes() for n in ('public_receiver.py', 'admission_gate.py', 'native_public.py', 'BINDING_TEMPLATE.json')}
template = json.loads(structural['BINDING_TEMPLATE.json'])
pub_root = a.candidate / 'candidate/public'
public = {q.relative_to(pub_root).as_posix(): q.read_bytes() for q in sorted(pub_root.rglob('*')) if q.is_file()}
runtime_raw = (a.runtime or a.issuer / 'PUBLIC_RUNTIME.json').read_bytes(); rt = json.loads(runtime_raw)
host_adoption = public[PREFIX + 'PROTECTED_RECIPIENT.json']
if a.mode == 'pro-executor-actual':
    B = adapter.prepare_binder(original_binder, sha(host_adoption), S.strict(host_adoption, 16384)['recipient'])
composition_raw = (a.composition / 'COMPOSITION.json').read_bytes(); c = json.loads(composition_raw)
pg_raw = (a.composition / 'POLICY_GATE_READBACK.json').read_bytes(); ng_raw = (a.composition / 'NATIVE_GATE_READBACK.json').read_bytes()
decisions = {n: (a.composition / 'public/qualification/dg16-r5-full-g2-decisions' / n).read_bytes() for n in DECISIONS}
candidate_seal = (a.candidate / 'SEAL.json').read_bytes()
composition_seal_path = a.composition / 'SEAL.json'
notes = []
if a.mode in ('g220-actual', 'pro-executor-actual'):
    composition_seal = composition_seal_path.read_bytes()                      # External physical-seal input
    selection_raw = (a.issuer / 'FINAL_REVIEW_SELECTION.json').read_bytes()    # External review-selection input
    selection = json.loads(selection_raw); author, reviewer = selection['author'], selection['reviewer']
else:
    members = []
    for q in sorted(a.composition.rglob('*')):
        if q.is_file() and q.name != 'SEAL.json':
            raw = q.read_bytes(); members.append(dict(bytes=len(raw), mode='0400', path=q.relative_to(a.composition).as_posix(), sha256=sha(raw)))
    seal = dict(schema='FABLE-TEST-ONLY.not-root-issued.composition-seal.v0', actor='FABLE_TEST_INPUT_NOT_ROOT', TEST_ONLY=True,
                effect_grant=False, final_tree=c['final_tree'], member_count=len(members), members=members, original_awards=[],
                source_commit=c['source_commit'], source_tree=c['source_tree'],
                warning='Scratch test input for pure logic only. The actual physical composition seal is a Root act and will have a different digest.')
    composition_seal = encode(seal)
    if not composition_seal_path.exists():
        composition_seal_path.write_bytes(composition_seal)
    author, reviewer = a.author, a.reviewer
    notes.append('TEST composition seal sha256=' + sha(composition_seal))
composition_path = a.composition_path or str(a.composition)
candidate_path = a.candidate_path or str(a.candidate)
b = dict(template)
b.update(candidate_path=candidate_path, composition_path=composition_path, candidate_seal_sha256=sha(candidate_seal),
         code_review_seal_sha256=c['independent_review_seal_sha256'], native_review_seal_sha256=c['native_review_seal_sha256'],
         composition_seal_sha256=sha(composition_seal), composition_sha256=sha(composition_raw), policy_gate_sha256=sha(pg_raw),
         native_gate_sha256=sha(ng_raw), final_tree=c['final_tree'], session=B.ISSUER,
         branch=c['branch'], control_branch=c['control_branch'],
         modules={n[len(PREFIX):]: desc(raw) for n, raw in public.items() if n.startswith(PREFIX)},
         successor_runtime_binding=desc(runtime_raw), composition_review_reviewer=reviewer)
for key, name in zip(('public_review_sha256', 'public_adoption_sha256', 'public_native_review_sha256', 'public_native_adoption_sha256'), DECISIONS):
    b[key] = sha(decisions[name])
if a.mode == 'g220-test':
    selection = dict(schema='dg16.direct-host-public-combined-review-selection.v1', actor='/root', issuer_thread=B.ISSUER, session=B.ISSUER,
                     status='ACTUAL_DISTINCT_REVIEWER_SELECTED_FOR_FINAL_BINDING', author=author, reviewer=reviewer,
                     **{k: b[k] for k in ('source_commit', 'source_tree', 'branch', 'control_branch', 'candidate_seal_sha256', 'composition_seal_sha256', 'final_tree')},
                     effect_grant=False, native_currentness=False, original_awards=[])
    selection_raw = encode(selection)
    notes.append('TEST review selection (bound to the TEST composition seal; cannot join an actual Root seal)')
b['composition_review_selection'] = desc(selection_raw)
binding_raw = encode(b)
inputs = dict(host_adoption=host_adoption, runtime=runtime_raw, binding=binding_raw, review_selection=selection_raw,
              composition=composition_raw, policy_gate=pg_raw, native_gate=ng_raw, decisions=decisions, author=author)
report = dict(mode=a.mode, notes=notes, authority='NONE', effect_grant=False,
              input_provenance='NOT_AUTHENTICATED_BY_HARNESS',
              binder_sha256=sha(a.binder.read_bytes()), binding=desc(binding_raw),
              template_changed_template_keys=sorted(k for k in template if template[k] != b[k]))


def adverse(label, mutate, expect):
    trial = dict(inputs); trial['decisions'] = dict(decisions); pub = dict(public); st = dict(structural)
    mutate(trial, pub, st)
    try:
        B.bind_public(st, pub, trial); return dict(control=label, status='UNEXPECTED_PASS')
    except ValueError as exc:
        return dict(control=label, status='EXPECTED_REFUSAL' if str(exc) == expect else 'REFUSED_OTHER', code=str(exc), expected=expect)


try:
    out = B.bind_public(structural, public, inputs)
    report['bind_public'] = 'PASS'; report['outputs'] = {n: desc(raw) for n, raw in sorted(out.items())}
except ValueError as exc:
    out = None; report['bind_public'] = 'REFUSED:' + str(exc)
if out is not None and a.mode == 'g220-test':
    def stale_template(t, pub, st): st['BINDING_TEMPLATE.json'] = st['BINDING_TEMPLATE.json'].replace(b'-host-20-', b'-host-19-')
    def stale_adoption(t, pub, st):
        t['host_adoption'] = t['host_adoption'].replace(b'-host-20-', b'-host-19-'); pub[PREFIX + 'PROTECTED_RECIPIENT.json'] = t['host_adoption']
    def stale_preflight(t, pub, st): pub[PREFIX + 'protected_preflight.py'] = pub[PREFIX + 'protected_preflight.py'].replace(
        b'c93292cb249539432ab4fa25d279da3fcede464106ed3392633fe05da52a4511', b'e653951703aa71933569ba2e4e40877eae469a53ef43de5178abc20f340d53bb')
    def same_reviewer(t, pub, st): t['author'] = reviewer
    def changed_decision(t, pub, st): t['decisions']['ROOT_POLICY_ADOPTION.json'] = t['decisions']['ROOT_POLICY_ADOPTION.json'] + b' '
    def wrong_runtime(t, pub, st): t['runtime'] = t['runtime'].replace(b'"output_fresh": true', b'"output_fresh": false')
    report['adverse'] = [adverse('stale -19 binding template', stale_template, 'FROZEN_PUBLIC_BINDING_TEMPLATE'),
                         adverse('stale -19 host adoption', stale_adoption, 'ACTUAL_HOST_ONLY_ADOPTION'),
                         adverse('historical e653 preflight bytes in public map', stale_preflight, 'HOST_PIN_CHAIN'),
                         adverse('author == reviewer', same_reviewer, 'ACTUAL_DISTINCT_REVIEWER'),
                         adverse('decision body changed', changed_decision, 'DECISION_BODY_JOIN'),
                         adverse('runtime not fresh', wrong_runtime, 'FRESH_PUBLIC_ONLY_RUNTIME')]
if out is not None:
    a.out.mkdir(parents=True, exist_ok=False)
    for name, raw in out.items():
        (a.out / name).write_bytes(raw); os.chmod(a.out / name, 0o400)
a.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps(report, indent=2, sort_keys=True))
if a.mode == 'pro-executor-actual' and out is None:
    raise SystemExit(1)
