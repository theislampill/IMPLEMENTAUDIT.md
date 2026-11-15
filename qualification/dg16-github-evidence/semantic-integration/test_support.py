"""INERT TEST DATA ONLY. No fixture is Root, adoption, grant or live evidence.

The production-bound positive verifier needs fresh external inputs. Fixtures
replace only that unavailable boundary; original deterministic functions and
filesystem checks remain real. No private key/certificate operation occurs.
"""
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import types
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CUSTODY = ROOT / 'handoff/dg16-g221-root-execution-inputs/g220-custody'
PUBLIC = CUSTODY / 'candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2'
RECEIVER = CUSTODY / 'candidate-e76-source-01/receiver/public_receiver.py'
AUTHORS = ['/root', '/root/dg16_contract_check']
REVIEWER = '/root/inert_fixture_review'


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def module(path, skip_audit=False):
    raw = path.read_bytes()
    tree = ast.parse(raw)
    if skip_audit:
        # Test-only: original functions, no permanent process-global audit hook.
        tree.body = [n for n in tree.body if not (isinstance(n, ast.Expr) and
            isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and
            n.value.func.attr == 'addaudithook')]
    result = types.ModuleType('INERT_TEST_' + path.stem)
    result.__file__ = str(path)
    exec(compile(tree, str(path), 'exec'), result.__dict__)
    return result


def retained_terminal():
    path = ROOT / 'handoff/dg16-pro-executor-20261115/evidence'
    archive = (path / 'G219_ARTIFACT.zip').read_bytes()
    assert desc(archive) == {'bytes':12857, 'sha256':'3c7913493f366a0e27fc380b7269b7bfb4560f31b9cdfeb5652632274a11c634'}
    metadata = json.loads((path / 'G219_PUBLIC_METADATA.json').read_bytes())
    R = module(RECEIVER, skip_audit=True)
    U = module(PUBLIC / 'host_utility.py')
    files = R.decode_zip(archive, 'terminal')
    log = ('\n'.join('2026-11-15T00:00:00.000Z ' + line for line in U.transport_lines(files)) + '\n').encode()
    binding = {'repository':metadata['run']['repository']['full_name'],
        'branch':metadata['run']['head_branch'], 'final_tree':metadata['commit']['tree']['sha'],
        'source_commit':metadata['commit']['parents'][0]['sha']}
    R.verified = lambda: (binding, {}, {}, {'host_utility.py':U}, {}, {})
    return R, U, archive, files, log, metadata, binding


def seal(directory):
    rows = []
    for path in sorted(directory.iterdir()):
        if path.name != 'SEAL.json':
            rows.append({'path':path.name,'mode':format(path.stat().st_mode & 0o777,'04o'),**desc(path.read_bytes())})
    raw = encode({'member_count':len(rows),'members':rows})
    if (directory / 'SEAL.json').exists():
        (directory / 'SEAL.json').unlink()
    (directory / 'SEAL.json').write_bytes(raw)
    (directory / 'SEAL.json').chmod(0o400)
    return desc(raw)['sha256']


def replace_fixture(path, raw):
    """Test tamper operation: replace bytes, then restore the selected mode."""
    mode=path.stat().st_mode & 0o777
    path.unlink()
    path.write_bytes(raw)
    path.chmod(mode)


def live_fixture(workspace, now=2000000000):
    """Complete control-input fixture; original production receiver is a seam."""
    workspace = workspace.resolve()
    rdir, live, review, composition = [workspace / n for n in ('receiver','live','review','composition')]
    for path in (rdir, live, review, composition): path.mkdir(mode=0o700)
    context = {'repository':'theislampill/IMPLEMENTAUDIT.md',
        'branch':'pro/dg16-r5-full-g2-direct-host-99-20261115','run_id':'1234567','run_attempt':1,
        'workflow_commit':'1'*40,'workflow_tree':'4b825dc642cb6eb9a060e54bf8d69288fbee4904',
        'source_commit':'205aeab7c93299b0666b261485ab5658d8e183de',
        'source_tree':'9ffbaf95080092bf4a45b8772a97ed16068544a7'}
    proof = encode({'INERT_TEST_DATA_ONLY':True})
    request = {'schema':'dg16.full-correspondence-live-review-request.v1','authority':'NONE',
        **{k:context[k] for k in ('repository','branch','run_id','run_attempt','workflow_commit','source_commit','source_tree')},
        'policy_sha256':'3'*64,'policy_adoption_sha256':'4'*64,'proof':desc(proof),
        'private_observations':{'bytes':42,'sha256':'5'*64},'hold_seconds':300,
        'control_branch':context['branch'].replace('-host-','-control-'),
        'control_path':'qualification/dg16-full-g2-control/1234567-1',
        'created_utc_epoch':now-10,'expires_utc_epoch':now+290}
    request_raw = encode(request)
    common = {'request_sha256':desc(request_raw)['sha256'],'proof_sha256':desc(proof)['sha256'],
        'private_observations_sha256':'5'*64,'source_commit':context['source_commit'],
        'source_tree':context['source_tree'],'policy_sha256':'3'*64,'policy_adoption_sha256':'4'*64}
    review_body = {'schema':'dg16.full-correspondence-independent-live-review.v1','authority':'NONE',
        'decision':'PASS','blocking_findings':[],'reviewer':REVIEWER,
        'scope':'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE',**common}
    review_raw = encode(review_body)
    root = {'schema':'dg16.full-correspondence-root-consumption.v1','author':'/root',
        'decision':'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK','one_shot':True,
        'review_sha256':desc(review_raw)['sha256'],'reviewer':REVIEWER,'automatic_full_G2_award':False,
        'original_source_or_product_limits_changed':False,**common}
    root_raw = encode(root)
    control = {'schema':'dg16.full-correspondence-live-control.v1','publisher':'/root',
        'repository':context['repository'],'run_id':context['run_id'],'run_attempt':1,
        'workflow_commit':context['workflow_commit'],'request_sha256':common['request_sha256'],
        'proof_sha256':common['proof_sha256'],'private_observations_sha256':'5'*64,'decision':'CONSUME',
        'files':{'INDEPENDENT_REVIEW.json':desc(review_raw),'ROOT_CONSUMPTION.json':desc(root_raw)}}
    payload = {'CONTROL.json':encode(control),'INDEPENDENT_REVIEW.json':review_raw,'ROOT_CONSUMPTION.json':root_raw}
    runtime = {'workspace_root':str(workspace),'receiver_output_root':str(workspace/'output')}
    binding = {**{k:context[k] for k in ('repository','branch','source_commit','source_tree')},
        'final_tree':context['workflow_tree'],'control_branch':request['control_branch'],
        'composition_path':str(composition)}
    binding_raw = encode(binding)
    for name, raw in {'public_receiver.py':b'# INERT fixture seam; never a bound receiver\n',
        'BINDING.json':binding_raw,'SUCCESSOR_RUNTIME_BINDING.json':encode(runtime)}.items():
        (rdir/name).write_bytes(raw);(rdir/name).chmod(0o400)
    receiver_seal = seal(rdir)
    final = {'state':'FINAL','disposition':'PASS','reviewer':REVIEWER,'actual_live_evidence_reviewed':True,
        'receiver_binding_sha256':desc(binding_raw)['sha256'],
        'request_sha256':common['request_sha256'],'proof_sha256':common['proof_sha256']}
    (review/'INDEPENDENT_REVIEW.json').write_bytes(review_raw)
    (review/'FINAL.json').write_bytes(encode(final))
    for path in review.iterdir(): path.chmod(0o400)
    review_seal = seal(review)
    archive = b'INERT_TEST_PUBLIC_ARCHIVE_SEAM_ONLY'
    metadata = {'INERT_TEST_METADATA_ONLY':True}
    (live/'ARTIFACT.zip').write_bytes(archive)
    (live/'PUBLIC_METADATA.json').write_bytes(encode(metadata))
    files = {'REQUEST.json':request_raw,'PROOF.json':proof}
    R = types.SimpleNamespace(__file__=str(rdir/'public_receiver.py'),BINDING_SHA=desc(binding_raw)['sha256'],
        strict=json.loads,decode_zip=lambda raw,kind: files)
    live_control = module(PUBLIC/'live_control.py')
    R.verified = lambda: (binding, {}, {}, {'live_control.py':live_control}, {}, {})
    R.inspect = lambda *a, **k: {'authority':'NONE','original_acceptance':False,'review_issued':False,
        'root_consumption_issued':False,'kind':'live','INERT_TEST_INSPECT_SEAM':True}
    selected = {'schema':'dg16.current-g2.public-root-live-decision-input.v2','actor':'/root',
        'decision':'CONSUME_AFTER_ACTUAL_INDEPENDENT_REVIEW','receiver_seal_sha256':receiver_seal,
        'independent_review_directory':str(review),'independent_review_seal_sha256':review_seal,
        'independent_review_body_sha256':desc(review_raw)['sha256'],'request_sha256':common['request_sha256'],
        'proof_sha256':common['proof_sha256'],'actual_workflow_commit':context['workflow_commit'],
        'actual_run_id':context['run_id'],'actual_evidence_and_review_read':True,
        'current_control_branch_absence_received':True,'automatic_replay':False,
        'issuer_thread':'PRO-EXECUTOR-01','session':'PRO-EXECUTOR-01','independent_reviewer':REVIEWER}
    root_path = workspace/'INERT_ROOT_INPUT.json'
    root_path.write_bytes(encode(selected))
    return types.SimpleNamespace(**locals())


def refreshed_root_input(f):
    raw = encode(f.selected)
    f.root_path.write_bytes(raw)
    return {'path':str(f.root_path),**desc(raw)}


def control_preparer_fixture(S, f):
    P,source = S.load_control_preparer(f.R,str(f.live),AUTHORS[0])
    # Missing authentic fresh bound receiver is the only verifier boundary seam.
    P.load = lambda path: f.R
    return P, source


def runtime_fixture(S, workspace, role='live', mode='receive', live_seconds=None):
    """Synthetic receipts at the external provenance seam, never actual facts."""
    now_ms=int(time.time()*1000)
    live_now=now_ms//1000 if live_seconds is None else now_ms//1000-290+live_seconds
    f=live_fixture(workspace,live_now)
    if role=='terminal':
        R,U,archive,files,log,metadata,binding=retained_terminal()
        f.R=R;f.archive=archive;f.metadata=metadata
        f.context.update(branch=metadata['run']['head_branch'],run_id=str(metadata['run']['id']),
            workflow_commit=metadata['run']['head_sha'],workflow_tree=metadata['commit']['tree']['sha'],
            source_commit=metadata['commit']['parents'][0]['sha'])
        R.inspect=lambda *a,**k: {'authority':'NONE','original_acceptance':False,
            'review_issued':False,'root_consumption_issued':False,'INERT_TEST_INSPECT_SEAM':True}
        frame=canonical({'content':[{'type':'text','text':'Action completed.'}],
            'structuredContent':{'content':log.decode()},'isError':False})
    else:
        frame=b'{}'
    (f.live/'ARTIFACT.zip').write_bytes(f.archive)
    (f.live/'PUBLIC_METADATA.json').write_bytes(encode(f.metadata))
    source={'channel_sha256':S.CHANNEL_SHA256,'journal_sha256':S.CHANNEL_JOURNAL_SHA256,
        'journal_path':str(ROOT/'qualification/dg16-github-evidence/journal.py'),'python_path':sys.executable}
    f.context.update(repository_id=1243475954,workflow_path='.github/workflows/dg16-r5-full-g2.yml',
        workflow_sha256='6'*64,job_name='full-registry-raw-pair',
        github_actor={'id':266501826,'login':'INERT-TEST'})
    artifact={'size_in_bytes':len(f.archive),'digest':'sha256:'+desc(f.archive)['sha256']}
    # The synthetic live fixture is not a provider metadata object. The unchanged
    # original inspect positive is unavailable; its boundary is explicitly a seam.
    public_metadata=f.metadata if role=='terminal' else {'artifact':artifact,'INERT_TEST_ONLY':True}
    f.metadata=public_metadata
    (f.live/'PUBLIC_METADATA.json').write_bytes(encode(public_metadata))
    job={'id':123456789,'run_id':int(f.context['run_id']),'run_attempt':1,
        'head_sha':f.context['workflow_commit'],'name':'full-registry-raw-pair','status':'completed'}
    operator={'schema':'dg16.github-public-provider-observation.v1','operator':'PRO-EXECUTOR-01',
        'successor':'PRO-EXECUTOR-01, designated by owner','authority':'NONE','purpose':'SOURCE_QUALIFICATION',
        'status':'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING','actor':'/root','role':role,
        'source':source,'context':f.context,'facts':{'public_metadata':public_metadata,'job':job},
        'public_metadata':public_metadata,'control_selection':None,'observed_start_ms':now_ms-100,
        'observed_end_ms':now_ms-70,'expires_ms':now_ms+100000,'original_acceptance':False,
        'private_or_cipher':False,'automatic_retry':False}
    operator['receipt_sha256']=desc(canonical(operator))['sha256']
    independent=json.loads(json.dumps(operator));independent.update(actor=REVIEWER,
        status='INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY',observed_start_ms=now_ms-60,
        observed_end_ms=now_ms-20,independent_operator_receipt_sha256=operator['receipt_sha256'])
    rehash(independent)
    body={'status':'EXACT_PUBLIC_BODY_RECEIVED','authority':'NONE','operator':'PRO-EXECUTOR-01',
        'purpose':operator['purpose'],'provider_receipt_sha256':operator['receipt_sha256'],
        'archive':desc(f.archive),'journal_path':str(f.live),'body_get_attempts':1,
        'signed_url_retained':False,'automatic_retry':False,'original_acceptance':False}
    receiver={'directory':str(f.rdir),'receiver_sha256':'1'*64,'seal_sha256':'2'*64,
        'binding_sha256':f.R.BINDING_SHA if role=='live' else '3'*64,'runtime_sha256':'4'*64}
    journal=workspace/'semantic-journals';journal.mkdir(mode=0o700)
    control=None
    if mode=='control':
        frame=canonical({'payload':{n:b.decode() for n,b in f.payload.items()},'source_authors':AUTHORS,
            'review_seal_sha256':f.review_seal,'root_decision_input':refreshed_root_input(f)})
        leaves=workspace/'INERT_LEAVES.json';leaves.write_bytes(encode({'members':[]}))
        control={'frame_sha256':desc(frame)['sha256'],'leaves_path':str(leaves),'leaves':desc(leaves.read_bytes())}
    selected={'mode':mode,'actor':'/root' if mode=='control' else REVIEWER,
        'source_sha256':desc(Path(S.__file__).read_bytes())['sha256'],'operator_receipt':operator,
        'independent_receipt':independent,'body_outcome':body,'receiver':receiver,'journal_parent':str(journal),
        'authorization_sha256':'a'*64,'expires_ms':now_ms+90000,'control':control}
    f.selected_runtime=selected;f.frame=frame;f.clock=[now_ms/1000];f.journal=journal
    return f


def rehash(receipt):
    receipt.pop('receipt_sha256',None)
    receipt['receipt_sha256']=desc(canonical(receipt))['sha256']
