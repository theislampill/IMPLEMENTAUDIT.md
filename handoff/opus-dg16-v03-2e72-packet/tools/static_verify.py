"""Read-only consistency checks of the rebound packet against a disposable 2e72 source copy.
Loads only relation/capture-evidence modules (no run.py, no pair_driver, no verifier run)."""
import hashlib, importlib.util, json, re, sys, types
from pathlib import Path
packet, source = Path(sys.argv[1]), Path(sys.argv[2])
Q = packet / 'qualification/dg16-r5-full-g2'
sha = lambda b: hashlib.sha256(b).hexdigest(); f = lambda n: sha((Q / n).read_bytes())
def consts(name):
    return dict(re.findall(r"^([A-Z_0-9]+) ?= ?'([^']*)'", (Q / name).read_text(), re.M))
ok = []
def check(label, cond): ok.append((label, bool(cond))); print(('PASS ' if cond else 'FAIL ') + label)
run, drv, cap, chk = consts('run.py'), consts('pair_driver.py'), consts('capture_evidence.py'), consts('checkout_prepare.py')
for k, n in [('MANIFEST_SHA', 'SOURCE_MANIFEST.json'), ('PAIR_DRIVER_SHA', 'pair_driver.py'), ('DIAGNOSTICS_SHA', 'pair_diagnostics.py'),
             ('FULL_RELATION_SHA', 'full_relation.py'), ('RELATION_INPUTS_SHA', 'RELATION_INPUTS.json'), ('POLICY_SHA', 'POLICY.json'),
             ('POLICY_CONTROL_SHA', 'policy_control.py'), ('LIVE_CONTROL_SHA', 'live_control.py'), ('CHECKOUT_PREPARE_SHA', 'checkout_prepare.py'),
             ('CAPTURE_EVIDENCE_SHA', 'capture_evidence.py'), ('UTILITY_SHA', 'host_utility.py')]:
    check('run.py ' + k, run[k] == f(n))
for k, n in [('DIAGNOSTICS_SHA', 'pair_diagnostics.py'), ('FULL_RELATION_SHA', 'full_relation.py'), ('RELATION_INPUTS_SHA', 'RELATION_INPUTS.json'),
             ('POLICY_SHA', 'POLICY.json'), ('POLICY_CONTROL_SHA', 'policy_control.py'), ('CAPTURE_EVIDENCE_SHA', 'capture_evidence.py')]:
    check('pair_driver.py ' + k, drv[k] == f(n))
owner_raw = (source / 'scripts/qualify-work-graph-verifier.py').read_bytes()
check('owner pins', drv['OWNER_SHA256'] == cap['OWNER_SHA'] == chk['OWNER_SHA'] == sha(owner_raw))
check('compiler pin', chk['COMPILER_SHA'] == sha((source / 'skills/implementaudit/scripts/compile-work-graph.py').read_bytes()))
check('catalog pin', cap['CATALOG_SHA'] == f('CAPTURE_DIAGNOSTIC_CATALOG.json'))
wf = (packet / '.github/workflows/dg16-r5-full-g2.yml').read_text()
check('workflow adapter digest', set(re.findall(r"'([0-9a-f]{64})'", wf)) == {f('run.py')})
check('workflow source ref', '51416b2f' not in wf and 'ref: ' + run['SOURCE_COMMIT'] in wf and run['BRANCH'] in wf)
pol = json.loads((Q / 'POLICY.json').read_bytes()); ri = json.loads((Q / 'RELATION_INPUTS.json').read_bytes())
check('policy receiver bindings', pol['receiver_inputs_sha256'] == run['RELATION_INPUTS_SHA'] and pol['full_receiver_sha256'] == run['FULL_RELATION_SHA'])
check('relation inputs files', all(ri['files'][n] == {'bytes': (Q / n).stat().st_size, 'sha256': f(n)} for n in ri['files']))
# full_relation.load / source_profiles against the actual 2e72 source.
spec = importlib.util.spec_from_file_location('owner', source / 'scripts/qualify-work-graph-verifier.py')
owner = importlib.util.module_from_spec(spec); sys.modules['owner'] = owner; spec.loader.exec_module(owner)
def loader(name, expected):
    raw = (Q / name).read_bytes(); assert sha(raw) == expected
    m = types.ModuleType('pk_' + name.replace('.', '_')); m.__file__ = str(Q / name); exec(compile(raw, str(Q / name), 'exec'), m.__dict__); return m
full = loader('full_relation.py', run['FULL_RELATION_SHA'])
check('policy/inputs canonical encoding', (Q / 'POLICY.json').read_bytes() == full.encode(pol) and (Q / 'RELATION_INPUTS.json').read_bytes() == full.encode(ri))
relation = full.load(Q, ri, loader, lambda p, limit=None: json.loads(Path(p).read_bytes()))
check('full_relation.load (112/2113, registry pin)', True)
facts, peers = full.source_profiles(source, owner, relation)
check('source_profiles: %d closure/role pins equal actual 2e72 bytes' % len(facts['members']), True)
reg = (source / 'scripts/verify-package.sh').read_bytes()
check('REGISTRY_SHA', full.REGISTRY_SHA == sha(reg) == pol['full_applicability']['registry_sha256'])
# capture_evidence success-path admission against the actual owner.
cev = loader('capture_evidence.py', run['CAPTURE_EVIDENCE_SHA'])
cat = cev.load_catalog(); compiled = cev.compiled_owner(source, cat); cev.admit_owner(owner, compiled)
check('capture_evidence load_catalog/compiled_owner/admit_owner', True)
# manifest vs actual tree (same rules as run.py verify_source, minus .git).
m = json.loads((Q / 'SOURCE_MANIFEST.json').read_bytes())
files = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
check('manifest population == source files', files == {r['path'] for r in m['members']})
check('run.py manifest counts', ("m['file_count']==%d" % m['file_count']) in (Q / 'run.py').read_text() and str(m['total_bytes']) in (Q / 'run.py').read_text())

# ---- Correction 2026-11-24 (Root review of d2303ee9): appended to static_verify.py checks ----
import shutil, tempfile
consumers = sorted(p for p in Q.iterdir() if p.suffix == '.py') + [packet / '.github/workflows/dg16-r5-full-g2.yml']
check('(a) no PRO-EXECUTOR-01 in any consumer', not any(b'PRO-EXECUTOR-01' in p.read_bytes() for p in consumers))
pc = loader('policy_control.py', run['POLICY_CONTROL_SHA'])
lc = loader('live_control.py', run['LIVE_CONTROL_SHA'])
need_authors = {'/root/opus_dg16', '/root/opus_dg16_subagent'}
check('author exclusions include both successor authors and all 15 originals (policy, live)',
      need_authors <= set(pc.CURRENT_AUTHORS) and need_authors <= set(lc.CURRENT_AUTHORS)
      and len(pc.CURRENT_AUTHORS) == len(lc.CURRENT_AUTHORS) == 17 and set(pc.CURRENT_AUTHORS) == set(lc.CURRENT_AUTHORS))
dumps = lambda v: (json.dumps(v, sort_keys=True, indent=2) + '\n').encode()
H = lambda c: c * 64
bindings = {'source_commit': run['SOURCE_COMMIT'], 'source_tree': run['SOURCE_TREE'], 'policy_sha256': run['POLICY_SHA'],
            'receiver_inputs_sha256': run['RELATION_INPUTS_SHA'], 'adapter_sha256': f('run.py'),
            'pair_driver_sha256': run['PAIR_DRIVER_SHA']}


def policy_payload(reviewer, successor='Astra Root'):
    review = {'schema': 'dg16.full-correspondence-code-review.v1', 'decision': 'PASS', 'authority': 'NONE',
              'blocking_findings': [], 'scope': 'EXACT_IMMUTABLE_FULL_CORRESPONDENCE_CODE_AND_POLICY', **bindings,
              'reviewer': reviewer, 'candidate_seal_sha256': H('a')}
    review_raw = dumps(review)
    adoption = {'schema': 'dg16.full-correspondence-root-policy-adoption.v1', 'author': '/root', 'successor': successor,
                'decision': 'ADOPT_FOR_ONE_EXACT_PROSPECTIVE_EPISODE', 'one_shot': True, 'candidate_seal_sha256': H('a'),
                'independent_review_sha256': sha(review_raw), 'independent_reviewer': reviewer,
                'finite_rules_unchanged': 13, 'finite_narrowings_unchanged': 6,
                'new_rules': [r['id'] for r in pol['new_rules']], 'full_applicability': pol['full_applicability'],
                'product_limits_changed': False, 'original_acceptance_granted': False, **bindings,
                'independent_review_seal_sha256': H('b')}
    return {'INDEPENDENT_COLD_REVIEW.json': review_raw, 'ROOT_POLICY_ADOPTION.json': dumps(adoption)}


def refused(fn, code):
    try:
        fn()
    except Exception as exc:
        return str(exc) == code
    return False


check('(b) policy gate accepts a synthetic non-author reviewer',
      pc.validate(policy_payload('/root/synthetic_independent'), bindings, pol)['decision'] == 'EXACT_ROOT_ADOPTION_AND_INDEPENDENT_REVIEW_RECEIVED')
check('(b) policy gate refuses every CURRENT_AUTHORS reviewer (%d)' % len(pc.CURRENT_AUTHORS),
      all(refused(lambda a=a: pc.validate(policy_payload(a), bindings, pol), 'EXACT_INDEPENDENT_CODE_REVIEW_REQUIRED')
          for a in pc.CURRENT_AUTHORS))
check('(b) policy gate refuses the predecessor successor literal',
      refused(lambda: pc.validate(policy_payload('/root/synthetic_independent', 'PRO-EXECUTOR-01, designated by owner'),
                                  bindings, pol), 'EXACT_ROOT_POLICY_ADOPTION_REQUIRED'))
request = {'expires_utc_epoch': 2000000000, 'hold_seconds': 3600, 'run_id': '1', 'workflow_commit': 'c' * 40,
           'proof': {'sha256': H('d')}, 'private_observations': {'sha256': H('e')}, 'source_commit': run['SOURCE_COMMIT'],
           'source_tree': run['SOURCE_TREE'], 'policy_sha256': run['POLICY_SHA'], 'policy_adoption_sha256': H('f')}
request_raw = dumps(request)


def live_payload(reviewer, successor='Astra Root'):
    common = {'request_sha256': sha(request_raw), 'proof_sha256': H('d'), 'private_observations_sha256': H('e'),
              'source_commit': run['SOURCE_COMMIT'], 'source_tree': run['SOURCE_TREE'],
              'policy_sha256': run['POLICY_SHA'], 'policy_adoption_sha256': H('f')}
    review = dumps({'schema': 'dg16.full-correspondence-independent-live-review.v1', 'authority': 'NONE', 'decision': 'PASS',
                    'blocking_findings': [], 'scope': 'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE',
                    **common, 'reviewer': reviewer})
    root = dumps({'schema': 'dg16.full-correspondence-root-consumption.v1', 'author': '/root', 'successor': successor,
                  'decision': 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK', 'one_shot': True,
                  'review_sha256': sha(review), 'reviewer': reviewer, 'automatic_full_G2_award': False,
                  'original_source_or_product_limits_changed': False, **common})
    control = dumps({'schema': 'dg16.full-correspondence-live-control.v1', 'publisher': '/root', 'repository': lc.REPOSITORY,
                     'successor': successor, 'run_id': '1', 'run_attempt': 1, 'workflow_commit': 'c' * 40,
                     'request_sha256': sha(request_raw), 'proof_sha256': H('d'), 'private_observations_sha256': H('e'),
                     'decision': 'CONSUME', 'files': {'INDEPENDENT_REVIEW.json': lc.descriptor(review),
                                                      'ROOT_CONSUMPTION.json': lc.descriptor(root)}})
    return {'CONTROL.json': control, 'INDEPENDENT_REVIEW.json': review, 'ROOT_CONSUMPTION.json': root}


check('(b) live control accepts a synthetic non-author reviewer',
      lc.validate(live_payload('/root/synthetic_independent'), request_raw, now=1)['decision'] == 'CONSUME')
check('(b) live control refuses every CURRENT_AUTHORS reviewer (%d)' % len(lc.CURRENT_AUTHORS),
      all(refused(lambda a=a: lc.validate(live_payload(a), request_raw, now=1), 'ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED')
          for a in lc.CURRENT_AUTHORS))
check('(b) live control refuses the predecessor successor literal',
      refused(lambda: lc.validate(live_payload('/root/synthetic_independent', 'PRO-EXECUTOR-01, designated by owner'),
                                  request_raw, now=1), 'LIVE_CONTROL_BINDING'))
reader = lambda p, limit=None: json.loads(Path(p).read_bytes())


def scratch_load(mutate):
    d = Path(tempfile.mkdtemp(prefix='v03-size-'))
    try:
        q = d / 'q'
        shutil.copytree(Q, q)
        inputs = json.loads((q / 'RELATION_INPUTS.json').read_bytes())
        mutate(q, inputs)

        def scratch_loader(name, expected):
            raw = (q / name).read_bytes(); assert sha(raw) == expected
            m = types.ModuleType('sc_' + name.replace('.', '_')); m.__file__ = str(q / name)
            exec(compile(raw, str(q / name), 'exec'), m.__dict__); return m
        full.load(q, inputs, scratch_loader, reader)
        return 'LOADED'
    except Exception as exc:
        return str(exc)
    finally:
        shutil.rmtree(d)


def resize(name, target):
    def m(q, inputs):
        raw = (q / name).read_bytes()
        raw = raw[:-1] + b' ' * (target - len(raw)) + b'\n' if target > len(raw) else raw[:target - 1] + b'\n'
        (q / name).write_bytes(raw)
        inputs['files'][name] = {'bytes': len(raw), 'sha256': sha(raw)}
    return m


check('(c) REPORT_SLOTS at exactly 1,083,198 bytes is admitted',
      (Q / 'REPORT_SLOTS.json').stat().st_size == 1083198 and scratch_load(lambda q, i: None) == 'LOADED')
check('(c) REPORT_SLOTS at 1,083,199 bytes is refused', scratch_load(resize('REPORT_SLOTS.json', 1083199)) == 'RELATION_INPUT_BOUND')
check('(c) REPORT_SLOTS at 1,083,197 bytes is refused', scratch_load(resize('REPORT_SLOTS.json', 1083197)) == 'RELATION_INPUT_BOUND')
others = [n for n in ri['files'] if n != 'REPORT_SLOTS.json']
check('(c) every other input (%d) at 1 MiB + 1 is refused' % len(others),
      all(scratch_load(resize(n, 1024**2 + 1)) == 'RELATION_INPUT_BOUND' for n in others))
check('(c) every other input (%d) at exactly 1 MiB passes the bound (fails later only on content)' % len(others),
      all(scratch_load(resize(n, 1024**2)) != 'RELATION_INPUT_BOUND' for n in others))

print('ALL_PASS' if all(c for _, c in ok) else 'SOME_FAIL')
