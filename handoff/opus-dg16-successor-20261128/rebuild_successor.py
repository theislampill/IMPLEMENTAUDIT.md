#!/usr/bin/env python3
"""Deterministic builder for the DG16 IMAGE23 successor operator (successor of 2af600fa).

LOCAL ONLY. This tool never pushes, never contacts GitHub, never creates a remote ref
and never issues a Root record. Linux only: it loads the pinned C5 engine from an
fc2e416c checkout (--source-root) exactly as packet/operation.py load_selected does.

Base: 2af600fad0e80fa71d9f808741bd74db792308b2 (create-event operator; branch
engineering/pro-dg16-image23-main-20261127-02 is SPENT by run 46046841410).
Intended successor changes (nothing else):
  * branch literals ...-20261127-02[-control] -> --branch NAME[-control] (22 occurrences);
    the workflow trigger (on: create, job if, env guard) is otherwise unchanged;
  * the stale EXECUTING_SOURCE_BINDINGS / EXECUTING_SOURCE_PINS row for
    scripts/work-graph-c5-executor.py in operation.py, g3_receiving.py and
    proof_consumer.py, replaced by the value derived from the actually loaded engine;
  * the three Root records (inserted verbatim, never rewritten);
  * every pin depending on the above.

Usage
  rebuild_successor.py --repo R --source-root SRC [--branch NAME] draft --issued 2026-11-28T00:00:00Z --out DRAFTS
  rebuild_successor.py --repo R --source-root SRC [--branch NAME] build --records DIR \
      [--local-branch local/NAME] [--tests] [--test-logs D] [--report out.json]

Exit codes: 0 built; 2 refused; 3 phase 1 (bootstrap admission missing or binding another manifest).
"""
import argparse
import ast
import copy
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import types

BASE_COMMIT = '2af600fad0e80fa71d9f808741bd74db792308b2'
BASE_TREE = 'd5d74ad65deda04df7e59adf66de7a320a85ef90'
SOURCE_COMMIT = 'fc2e416c5da38eb370045561f5281a846785ec3e'
SOURCE_TREE = 'a9914d446d2a3e0653c972cf50197186e23555d8'
OLD_MAIN = 'engineering/pro-dg16-image23-main-20261127-02'  # literal in the base (spent by run 46046841410)
SPENT_BRANCHES = ('engineering/pro-dg16-image23-main-20261127-01', 'engineering/pro-dg16-image23-main-20261127-02')
DEFAULT_BRANCH = 'engineering/dg16-image23-main-20261128-01'
BRANCH_PREFIX = 'engineering/dg16-image23-main-'
NEW_MAIN = DEFAULT_BRANCH  # set from --branch in main()
OLD_CONTROL = OLD_MAIN + '-control'
NEW_CONTROL = NEW_MAIN + '-control'  # always derived: NAME-control
SOURCE_BRANCH = 'engineering/pro-dg16-image23-source-20261127-01'
EXPECTED_LITERAL_OCCURRENCES = 22  # occurrences of the -02 literal in 13 files of 2af600fa (workflow 7)
SOURCE_ROOT = None  # --source-root: checkout of fc2e416c
EXECUTOR_NAME = 'scripts/work-graph-c5-executor.py'
EXECUTOR_STALE = {'bytes': 83099, 'sha256': 'd9b9ad23eefaa62bb273970232dc5669ab40d465c6f9d5bf5f83b7048e8df1d8'}
# Independently reported by the coordinator; the builder DERIVES the value from the loaded engine and refuses on mismatch.
EXECUTOR_EXPECTED = {'bytes': 108100, 'sha256': '5c74e75e6a88121918d0c254c5964f6efe950c09fcc5560ef698080254839b20'}
BINDING_CONSTANTS = {'packet/operation.py': 'EXECUTING_SOURCE_BINDINGS', 'packet/g3_receiving.py': 'EXECUTING_SOURCE_BINDINGS',
                     'packet/proof_consumer.py': 'EXECUTING_SOURCE_PINS'}
ENGINE = {}  # filled by derive_engine()
# New offline control added to the successor (not part of the packet manifest); its bytes are pinned here.
LOAD_SELECTED_TEST = 'qualification/dg16-r5-g1-hosted-episode-v21/tests/test_load_selected.py'
LOAD_SELECTED_TEST_SHA256 = 'bc90f3d5a4499ca3a91eb239dd712908c68acf9c167cd90d636e2ed3f7e22e36'
# Policy currentness at build time (refusals, not warnings).
MIN_REMAINING_MS = 60 * 60 * 1000
MAX_FUTURE_ISSUE_MS = 10 * 60 * 1000
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
Q = 'qualification/dg16-r5-g1-hosted-episode-v21/'
P = Q + 'packet/'
E = Q + 'entry/'
WF = '.github/workflows/dg16-r5-g1-hosted-episode-v21.yml'
SUCCESSOR = 'owner-appointed continuing Root dg16-dg17-successor-20261127'
ISSUER = 'R5_ROOT_GOVERNOR'
ROOT_RECORDS = {
    'G1_HOST_PROFILE_POLICY.json': E + 'G1_HOST_PROFILE_POLICY.json',
    'COMPOSITION_ROOT_ADMISSION.json': P + 'public-inputs/COMPOSITION_ROOT_ADMISSION.json',
    'BOOTSTRAP_ADMISSION.json': E + 'BOOTSTRAP_ADMISSION.json',
}
POLICY_WINDOW_MS = 390 * 60 * 1000
DRAFT_PROFILE_IDS = ['G1_UBUNTU24_20261122_23_1']  # final decision: policy agrees with the 23.1-only workflow
PATHS_BLOCK = (',\n      "paths": [\n        ".github/workflows/dg16-r5-g1-hosted-episode-v21.yml",\n'
               '        "qualification/dg16-r5-g1-hosted-episode-v21/**"\n      ]')
# Files that may change; anything else changing is a refusal.
ALLOWED_CHANGES = {
    WF,
    E + 'BOOTSTRAP_ADMISSION.json', E + 'G1_HOST_PROFILE_POLICY.json', E + 'PUBLIC_PACKET_MANIFEST.json',
    E + 'admit_public_inputs.py', E + 'bootstrap_entry.py', E + 'core_prepare_entry.py', E + 'public_export.py',
    P + 'HOST_COMPOSITION.json', P + 'INDEPENDENT_PROOF_PINS.json', P + 'PUBLIC_INPUT_INDEX.json',
    P + 'g3_receiving.py', P + 'host_composition.py', P + 'proof_consumer.py', P + 'public_inputs.py', P + 'run.py',
    P + 'operation.py', LOAD_SELECTED_TEST,
    P + 'public-inputs/COMPOSITION_ROOT_ADMISSION.json',
}
# Third-party / retained bodies that this tool must never rewrite (Root records are inserted verbatim).
PROTECTED_PREFIXES = (P + 'public-inputs/', P + 'retained-m4/')
AUTHOR = ('Opus 5.5 (DG16)', 'noreply@anthropic.com')
# Opus/coordinator decision (owner standing approval): the workflow accepts both measured images.
# Each pair is (decoded step text before, after); exactly one occurrence each, any other image still refuses.
IMAGE_23 = '20261122.23.1'
IMAGE_376 = '20261116.376.1'
IMAGE_EDITS = {
    'dispatch': ('\n  20261122.23.1) mode=main ;;\n', '\n  20261122.23.1|20261116.376.1) mode=main ;;\n'),
    'main_guard': ('\n[[ "${ImageVersion-}" == 20261122.23.1 ]] || refuse IMAGEVERSION\n',
                   '\n[[ "${ImageVersion-}" == 20261122.23.1 || "${ImageVersion-}" == 20261116.376.1 ]] || refuse IMAGEVERSION\n'),
}
ACCEPT_376 = False  # final decision: 23.1-only workflow (early refusal at dispatch); no image edits are allowed
# Known core blocker for 376 outside the workflow (not changeable here: it is in the admitted source):
# runtime_preflight.EXPECTED and the selected source package
# fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-image23-python312.json pin /etc/ld.so.cache
# 38836/b6068d03...; the 376 (HOST02) measurement in package-...-host02-python312.json is 38396/347fdaed...
LDSO_376 = {'bytes': 38396, 'sha256': '347fdaed89f5b040c24b9d44f4b0700e8de4ef0585eb7e3d1ec6d3bdf664cd84'}
COMMIT_DATE = '1795824000 +0000'  # 2026-11-28T00:00:00Z, fixed
HEX64 = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')


class Refused(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise Refused(msg)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def pretty(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def strict_json(raw, code):
    def pairs(rows):
        out = {}
        for k, v in rows:
            need(k not in out, code + ': duplicate key ' + k)
            out[k] = v
        return out
    def nonfinite(_):
        raise Refused(code + ': non-finite')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refused(code + ': ' + str(exc)) from None


def iso_to_ms(text):
    t = datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    return int(t.timestamp()) * 1000


def ms_to_iso(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


# ----------------------------------------------------------------------------- git

class Git:
    def __init__(self, repo):
        self.repo = repo

    def run(self, *args, data=None, env=None):
        full = dict(os.environ)
        full.update(env or {})
        r = subprocess.run(['git', '-C', self.repo] + list(args), input=data, capture_output=True, env=full)
        if r.returncode != 0:
            raise Refused('git %s failed: %s' % (' '.join(args[:3]), r.stderr.decode(errors='replace').strip()))
        return r.stdout

    def text(self, *args, **kw):
        return self.run(*args, **kw).decode().strip()

    def ls_tree(self, treeish, *paths):
        out = self.run('ls-tree', '-r', '-z', treeish, '--', *paths)
        rows = {}
        for item in out.split(b'\0'):
            if not item:
                continue
            meta, path = item.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            rows[path.decode()] = (mode, kind, oid)
        return rows

    def blob(self, oid):
        return self.run('cat-file', 'blob', oid)

    def grep_count(self, treeish, literal):
        r = subprocess.run(['git', '-C', self.repo, 'grep', '-o', '-F', '-e', literal, treeish],
                           capture_output=True)
        if r.returncode == 1:
            return 0, []
        need(r.returncode == 0, 'git grep failed')
        lines = [l for l in r.stdout.decode().split('\n') if l]
        return len(lines), sorted({l.split(':')[1] for l in lines})

    def grep_any(self, treeish, literals):
        if not literals:
            return []
        args = ['git', '-C', self.repo, 'grep', '-l', '-F']
        for l in sorted(literals):
            args += ['-e', l]
        r = subprocess.run(args + [treeish], capture_output=True)
        if r.returncode == 1:
            return []
        need(r.returncode == 0, 'git grep failed')
        return [l.split(':', 1)[1] for l in r.stdout.decode().split('\n') if l]


# ----------------------------------------------------------------------------- python constants

def py_constants(raw):
    tree = ast.parse(raw.decode('utf-8'))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


# ----------------------------------------------------------------------------- pin propagation

def replace_in_json(raw, stale, current_len, path):
    """stale: hash -> new hash. current_len: new hash -> length. Structural; format must roundtrip."""
    value = json.loads(raw)
    need(pretty(value) == raw, 'pin-bearing JSON does not roundtrip in pretty format: ' + path)
    def walk(node):
        if isinstance(node, dict):
            for k in list(node):
                v = node[k]
                if isinstance(v, str):
                    nv = HEX64.sub(lambda m: stale.get(m.group(0), m.group(0)), v)
                    if nv != v:
                        node[k] = nv
                        if k == 'sha256' and 'bytes' in node and nv in current_len:
                            node['bytes'] = current_len[nv]
                else:
                    walk(v)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                if isinstance(v, str):
                    node[i] = HEX64.sub(lambda m: stale.get(m.group(0), m.group(0)), v)
                else:
                    walk(v)
    walk(value)
    return pretty(value)


def replace_in_text(raw, stale, current_len):
    text = raw.decode('utf-8')
    for old, new in stale.items():
        if old not in text:
            continue
        n = str(current_len[new])
        text = re.sub(r"('bytes':\s*)\d+(,\s*'sha256':\s*')" + old, lambda m: m.group(1) + n + m.group(2) + new, text)
        text = re.sub(r"(bytes=)\d+(,\s*sha256=')" + old, lambda m: m.group(1) + n + m.group(2) + new, text)
        text = text.replace(old, new)
    return text.encode('utf-8')


def propagate(files, base_files, frozen):
    """Fixpoint: rewrite every stale digest of every scope file to its current digest."""
    history = {p: [sha(base_files.get(p, files[p]))] for p in files}
    for p in files:
        if sha(files[p]) != history[p][-1]:
            history[p].append(sha(files[p]))
    for _ in range(30):
        stale, current_len = {}, {}
        for p, raw in files.items():
            cur = sha(raw)
            current_len[cur] = len(raw)
            for h in history[p][:-1]:
                if h != cur:
                    stale[h] = cur
        changed = False
        for p in sorted(files):
            raw = files[p]
            if not any(h in raw.decode('utf-8', 'replace') for h in stale):
                continue
            if p in frozen or p.startswith(PROTECTED_PREFIXES):
                hits = sorted(h for h in stale if h in raw.decode('utf-8', 'replace'))
                raise Refused('stale digest(s) %s inside protected/Root body %s (Root must re-issue it)' % (
                    ','.join(h[:12] for h in hits), p))
            new = replace_in_json(raw, stale, current_len, p) if p.endswith('.json') else replace_in_text(raw, stale, current_len)
            if new != raw:
                files[p] = new
                history[p].append(sha(new))
                changed = True
        if not changed:
            return history
    raise Refused('pin propagation did not converge')


# ----------------------------------------------------------------------------- Root record checks

def host_profiles(files):
    c = py_constants(files[P + 'host_utility.py'])
    rows = c['G1_HOST_PROFILES']
    digest = sha((json.dumps(rows, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode())
    return rows, digest


def workflow_accepted_images(wf_raw):
    w = json.loads(wf_raw)
    steps = {s.get('id'): s for s in w['jobs']['qualify']['steps']}
    dispatch = [v for line in re.findall(r'\n  ([0-9.|]+)\) mode=main ;;', steps['dispatch']['run']) for v in line.split('|')]
    guard_line = [l for l in steps['main_guard']['run'].split('\n') if 'refuse IMAGEVERSION' in l]
    need(len(guard_line) == 1, 'main_guard image line')
    guard = re.findall(r'"\$\{ImageVersion-\}" == ([0-9.]+)', guard_line[0])
    return sorted(set(dispatch) & set(guard)), dispatch, guard


def check_policy(raw, files, warnings):
    code = 'G1_HOST_PROFILE_POLICY'
    need(type(raw) is bytes and 0 < len(raw) <= 65536, code + ': size')
    value = strict_json(raw, code)
    need(compact(value) == raw, code + ': not the canonical encoding required by host_profile_binding._parse (D4_POLICY_JSON)')
    fields = {'schema', 'issuer', 'successor', 'decision', 'semantics', 'source_commit', 'source_tree', 'operation',
              'finite_host_policy_sha256', 'profile_ids', 'issued_unix_ms', 'expires_unix_ms',
              'core_or_native_effect_grant', 'original_awards'}
    need(type(value) is dict and set(value) == fields, code + ': D4_POLICY_SCOPE fields')
    need(value['schema'] == 'dg16.g1-prospective-host-profile-policy.v2' and value['issuer'] == ISSUER
         and value['successor'] == SUCCESSOR and value['decision'] == 'ADOPT_FINITE_EXACT_PROFILES_CONDITIONALLY'
         and value['semantics'] == 'PROSPECTIVE_PROFILE_MATCH_BEFORE_PREPARE'
         and value['core_or_native_effect_grant'] is False and value['original_awards'] == [], code + ': D4_POLICY_SCOPE values')
    need(value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE, code + ': D4_POLICY_SOURCE')
    i, x = value['issued_unix_ms'], value['expires_unix_ms']
    need(type(i) is int and type(x) is int and 0 <= i < x <= 10 ** 16, code + ': D4_POLICY_TIME shape')
    rows, digest = host_profiles(files)
    ids = value['profile_ids']
    need(value['finite_host_policy_sha256'] == digest, code + ': finite_host_policy_sha256 != host_utility G1_HOST_PROFILES digest')
    need(type(ids) is list and 0 < len(ids) <= len(rows) and all(type(t) is str for t in ids)
         and ids == sorted(set(ids)) and all(sum(r['id'] == t for r in rows) == 1 for t in ids), code + ': D4_POLICY_PROFILE')
    op = value['operation']
    need(type(op) is dict and set(op) == {'repository', 'branch', 'workflow_path', 'job_name', 'run_attempt'}, code + ': D4_POLICY_OPERATION fields')
    need(op == dict(repository=REPOSITORY, branch=NEW_MAIN, workflow_path=WF, job_name='qualify', run_attempt=1),
         code + ': D4_POLICY_OPERATION must be the exact successor operation (repo, %s, %s, qualify, 1)' % (NEW_MAIN, WF))
    # Execute the real pinned consumer (_policy and _operation) from the built tree.
    mod = types.ModuleType('hpb_check')
    exec(compile(files[E + 'host_profile_binding.py'], 'host_profile_binding.py', 'exec'), mod.__dict__)
    owner = types.SimpleNamespace(G1_HOST_PROFILES=rows, g1_host_policy_sha256=lambda: digest)
    pin = dict(bytes=len(raw), sha256=sha(raw))
    for now in (i, x - 1):
        try:
            mod._policy(raw, pin, owner, now)
        except ValueError as exc:
            raise Refused(code + ': real host_profile_binding._policy refused: ' + str(exc)) from None
    for now in (i - 1, x):
        try:
            mod._policy(raw, pin, owner, now)
            raise Refused(code + ': _policy accepted outside its window')
        except ValueError:
            pass
    fake_commit = '0' * 40
    ctx = dict(repository=REPOSITORY, branch=NEW_MAIN, run_id='1', run_attempt=1, workflow_commit=fake_commit)
    saved = {k: os.environ.get(k) for k in ('GITHUB_JOB', 'GITHUB_WORKFLOW_SHA', 'GITHUB_WORKFLOW_REF')}
    os.environ.update(GITHUB_JOB='qualify', GITHUB_WORKFLOW_SHA=fake_commit,
                      GITHUB_WORKFLOW_REF=REPOSITORY + '/' + WF + '@refs/heads/' + NEW_MAIN)
    try:
        mod._operation(value, ctx)
    except ValueError as exc:
        raise Refused(code + ': real host_profile_binding._operation refused: ' + str(exc)) from None
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    # Non-refusing observations.
    if x - i != POLICY_WINDOW_MS:
        warnings.append('policy window is %d min, policy04 design used 390 min' % ((x - i) // 60000))
    now_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    need(x > now_ms + MIN_REMAINING_MS, code + ': expires %s is not more than 60 min after now %s' % (ms_to_iso(x), ms_to_iso(now_ms)))
    need(i <= now_ms + MAX_FUTURE_ISSUE_MS, code + ': issued %s is more than 10 min after now %s' % (ms_to_iso(i), ms_to_iso(now_ms)))
    accepted, _, _ = workflow_accepted_images(files[WF])
    by_id = {r['id']: r['facts']['image_version'] for r in rows}
    for t in ids:
        if by_id[t] not in accepted:
            warnings.append('profile %s (image %s) is adopted by the policy but the workflow dispatch/main_guard steps '
                            'accept only %s: a runner on that image refuses at DISPATCH_IMAGEVERSION/MAIN04_IMAGEVERSION'
                            % (t, by_id[t], accepted))
    rp = py_constants(files[P + 'runtime_preflight.py'])['EXPECTED']['/etc/ld.so.cache']
    if IMAGE_376 in accepted and any(by_id[t] == IMAGE_376 for t in ids) and \
            {k: rp[k] for k in ('bytes', 'sha256')} != LDSO_376:
        warnings.append('image %s passes the workflow and D4, but the core runtime_preflight.EXPECTED (and the admitted source '
                        'package image23 startup_pins) bind /etc/ld.so.cache %d/%s while the measured 376 (HOST02) tuple is '
                        '%d/%s: a 376 runner is expected to refuse later at RUNTIME_SELECTOR_PREFLIGHT_REFUSED'
                        % (IMAGE_376, rp['bytes'], rp['sha256'][:12], LDSO_376['bytes'], LDSO_376['sha256'][:12]))
    return value


def check_composition(raw, files, index):
    code = 'COMPOSITION_ROOT_ADMISSION'
    need(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024, code + ': PUBLIC_INPUT_BODY_BOUND')
    value = strict_json(raw, code)
    need(type(value) is dict, code + ': PUBLIC_INPUT_BODY_SHAPE')
    row = index['roles']['1']
    need(row['name'] == 'COMPOSITION_ROOT_ADMISSION.json' and row['issuer_field'] == 'issuer' and row['subject_field'] is None
         and value.get('issuer') == row['issuer'] == ISSUER, code + ': PUBLIC_INPUT_ISSUER_MISMATCH')
    need(set(value) == {'schema', 'issuer', 'successor', 'source_commit', 'source_tree', 'workflow_branch', 'control_branch',
                        'source_branch', 'run_attempt', 'automatic_retry', 'original_awards', 'prospective_operation',
                        'component_scope', 'input_route', 'input_sha256'}, code + ': CORE_ADMISSION_FIELDS')
    need(value['schema'] == 'dg16.current-core-host-root-admission.v2' and value['issuer'] == ISSUER
         and value['successor'] == SUCCESSOR and value['component_scope'] == 'CORE_G1_Q06_NATURAL_L04_SEPARATE'
         and value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE
         and value['workflow_branch'] == NEW_MAIN and value['run_attempt'] == 1 and value['automatic_retry'] is False
         and value['original_awards'] == []
         and value['input_route'] == 'PINNED_PUBLIC_INPUT_SELECTOR_NO_CARRIER_NO_PRIVATE_SENDER'
         and value['prospective_operation'] == 'ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE',
         code + ': ROOT_ADMISSION_SCOPE_REFUSED')
    # Not checked by any consumer, but bound by HOST_COMPOSITION and required for a coherent record:
    need(value['control_branch'] == NEW_CONTROL and value['source_branch'] == SOURCE_BRANCH,
         code + ': control_branch/source_branch must be %s / %s' % (NEW_CONTROL, SOURCE_BRANCH))
    expected = {}
    for key, r in index['roles'].items():
        if key != '1':
            expected[r['name']] = sha(files[P + 'public-inputs/' + r['name']])
    for r in index['support']:
        expected[r['name']] = sha(files[P + 'public-inputs/' + r['name']])
    need(value['input_sha256'] == expected, code + ': ROOT_ADMISSION_BODY_BINDING (input_sha256 must equal the current bodies)')
    return value


def check_bootstrap(raw, manifest_raw):
    code = 'BOOTSTRAP_ADMISSION'
    need(type(raw) is bytes and len(raw) <= 16384, code + ': BOOTSTRAP_ADMISSION_PIN bound')
    value = strict_json(raw, code)
    need(type(value) is dict and set(value) == {'schema', 'issuer', 'successor', 'operation', 'source_commit', 'source_tree',
         'workflow_branch', 'run_attempt', 'automatic_retry', 'original_awards', 'manifest_sha256'}, code + ': BOOTSTRAP_ADMISSION_SCOPE fields')
    need(type(value['run_attempt']) is int and value['automatic_retry'] is False, code + ': BOOTSTRAP_ADMISSION_SCOPE types')
    need(value == bootstrap_expected(manifest_raw), code + ': BOOTSTRAP_ADMISSION_SCOPE (must equal the exact admission dict '
         'with workflow_branch=%s and manifest_sha256=%s)' % (NEW_MAIN, sha(manifest_raw)))
    return value


def bootstrap_expected(manifest_raw):
    return dict(schema='dg16.fixed-root-bootstrap-admission.v1', issuer=ISSUER, successor=SUCCESSOR,
                operation='CREATE_EXCLUSIVE_ROOT_ISLAND_AND_EXACT_PUBLIC_PACKET_ONLY', source_commit=SOURCE_COMMIT,
                source_tree=SOURCE_TREE, workflow_branch=NEW_MAIN, run_attempt=1, automatic_retry=False,
                original_awards=[], manifest_sha256=sha(manifest_raw))


# ----------------------------------------------------------------------------- full pin-chain verification

def deep_replace(node, old, new):
    if isinstance(node, dict):
        return {deep_replace(k, old, new): deep_replace(v, old, new) for k, v in node.items()}
    if isinstance(node, list):
        return [deep_replace(v, old, new) for v in node]
    if isinstance(node, str):
        return node.replace(old, new)
    return node


def verify(files, base_files, history, records_present):
    checks = []
    def ok(cond, msg):
        need(cond, 'VERIFY: ' + msg)
        checks.append(msg)
    f = files
    # Workflow: structurally equal to the base with exactly the two intended changes.
    wf_new, wf_old = json.loads(f[WF]), json.loads(base_files[WF])
    expect = deep_replace(copy.deepcopy(wf_old), OLD_MAIN, NEW_MAIN)
    if ACCEPT_376:
        for st in expect['jobs']['qualify']['steps']:
            if st.get('id') in IMAGE_EDITS:
                before, after = IMAGE_EDITS[st['id']]
                assert st['run'].count(before) == 1
                st['run'] = st['run'].replace(before, after)
    ok(wf_new == expect, 'workflow == base with exactly: branch literal renamed%s '
       '(all other steps/if/permissions/timeouts unchanged)' % (', dispatch+main_guard accept 23.1|376.1' if ACCEPT_376 else ''))
    accepted, d_vals, g_vals = workflow_accepted_images(f[WF])
    want = sorted([IMAGE_23, IMAGE_376] if ACCEPT_376 else [IMAGE_23])
    ok(sorted(d_vals) == sorted(g_vals) == accepted == want, 'workflow accepts exactly images %s in both dispatch and main_guard' % want)
    ok(wf_new['on'] == {'create': None}, 'workflow on == create (unchanged trigger)')
    job = wf_new['jobs']['qualify']
    ok(job['if'] == ("github.repository == '%s' && github.event_name == 'create' && github.ref == 'refs/heads/%s' && "
                     "github.event.ref_type == 'branch' && github.event.ref == '%s' && github.run_attempt == '1'") % (REPOSITORY, NEW_MAIN, NEW_MAIN),
       'job if guard exact (repository, create, exact ref, ref_type branch, event.ref, run_attempt==1)')
    ok(job['env'] == {'DG16_CREATED_BRANCH_EVENT': "${{ github.event_name == 'create' && github.event.ref_type == 'branch' && "
                      "github.event.ref == '%s' }}" % NEW_MAIN}, 'job env created-branch guard exact')
    for rel, const in sorted(BINDING_CONSTANTS.items()):
        ok(py_constants(f[Q + rel])[const] == ENGINE['bindings'], '%s.%s == engine-derived SOURCES bindings' % (rel, const))
    ok(wf_new['permissions'] == {'actions': 'read', 'contents': 'read'} and job['timeout-minutes'] == 330, 'permissions/timeouts')
    # Literals.
    for p in files:
        if p not in ROOT_RECORDS.values():
            ok(OLD_MAIN.encode() not in f[p], 'no old branch literal in ' + p) if OLD_MAIN.encode() in base_files.get(p, b'') else None
    ok(not any(x.encode() in f[p] for x in SPENT_BRANCHES for p in f), 'no spent branch literal anywhere in scope')
    ok(sum(f[p].count(NEW_MAIN.encode()) for p in f) == EXPECTED_LITERAL_OCCURRENCES,
       'new branch literal occurs exactly %d times in scope' % EXPECTED_LITERAL_OCCURRENCES)
    ok(sum(f[p].count(SOURCE_BRANCH.encode()) for p in f) == sum(base_files.get(p, b'').count(SOURCE_BRANCH.encode()) for p in f),
       'source branch literal count unchanged')
    c = {name: py_constants(f[path]) for name, path in (
        ('run', P + 'run.py'), ('g3', P + 'g3_receiving.py'), ('hc', P + 'host_composition.py'), ('pi', P + 'public_inputs.py'),
        ('core', E + 'core_prepare_entry.py'), ('export', E + 'public_export.py'), ('admit', E + 'admit_public_inputs.py'),
        ('boot', E + 'bootstrap_entry.py'))}
    for k in ('run', 'core', 'export', 'admit', 'boot'):
        ok(c[k]['BRANCH'] == NEW_MAIN, k + '.BRANCH == new main')
    ok(c['g3']['JOB_BRANCH'] == NEW_MAIN and c['g3']['CONTROL_BRANCH'] == NEW_CONTROL, 'g3_receiving JOB_BRANCH/CONTROL_BRANCH')
    ok(("pins['initial_control_branch']=='%s'" % NEW_CONTROL).encode() in f[P + 'proof_consumer.py'], 'proof_consumer control literal')
    run = c['run']
    ok(run['SOURCE_BRANCH'] == SOURCE_BRANCH, 'run.SOURCE_BRANCH unchanged')
    for m, pin in run['MODULE_PINS'].items():
        ok(pin == sha(f[P + m + '.py']), 'run.MODULE_PINS[%s]' % m)
    for n, pin in run['G3_DATA_PINS'].items():
        ok(pin == sha(f[P + n]), 'run.G3_DATA_PINS[%s]' % n)
    ok(run['MANIFEST_SHA'] == sha(f[P + 'SOURCE_MANIFEST.json']), 'run.MANIFEST_SHA (source manifest)')
    ipp = json.loads(f[P + 'INDEPENDENT_PROOF_PINS.json'])
    pol = f[ROOT_RECORDS['G1_HOST_PROFILE_POLICY.json']]
    ok(ipp['consumer_sha256'] == sha(f[P + 'proof_consumer.py']) and ipp['scope_module_sha256'] == sha(f[P + 'g3_receiving.py'])
       and ipp['scope_sha256'] == sha(f[P + 'ORIGINAL_SCOPE.json']) and ipp['adverse_sha256'] == sha(f[P + 'ADVERSE_APPLICABILITY.json'])
       and ipp['host_profile_policy'] == dict(bytes=len(pol), sha256=sha(pol)) and ipp['initial_control_branch'] == NEW_CONTROL
       and ipp['source_commit'] == SOURCE_COMMIT and ipp['source_tree'] == SOURCE_TREE, 'INDEPENDENT_PROOF_PINS chain')
    hc = json.loads(f[P + 'HOST_COMPOSITION.json'])
    ok(hc['workflow_branch'] == NEW_MAIN and hc['control_branch'] == NEW_CONTROL and hc['source_branch'] == SOURCE_BRANCH
       and hc['public_input_index'] == dict(path='PUBLIC_INPUT_INDEX.json', sha256=sha(f[P + 'PUBLIC_INPUT_INDEX.json'])),
       'HOST_COMPOSITION branches + public_input_index pin')
    ok(c['hc']['BINDING_SHA256'] == sha(f[P + 'HOST_COMPOSITION.json']), 'host_composition.BINDING_SHA256')
    ok(c['pi']['INDEX_SHA256'] == sha(f[P + 'PUBLIC_INPUT_INDEX.json']), 'public_inputs.INDEX_SHA256')
    index = json.loads(f[P + 'PUBLIC_INPUT_INDEX.json'])
    for r in list(index['roles'].values()) + index['support']:
        body = f[P + 'public-inputs/' + r['name']]
        ok(r['bytes'] == len(body) and r['sha256'] == sha(body), 'PUBLIC_INPUT_INDEX row ' + r['name'])
    ok(c['core']['CORE_RUN_SHA256'] == sha(f[P + 'run.py']) and c['core']['SELECTOR_SHA256'] == sha(f[P + 'public_inputs.py'])
       and c['core']['ROOT_POLICY_PIN'] == dict(bytes=len(pol), sha256=sha(pol))
       and c['core']['D4_BINDER_SHA256'] == sha(f[E + 'host_profile_binding.py']), 'core_prepare_entry pins')
    ok(c['export']['CORE_RUN_SHA256'] == sha(f[P + 'run.py']), 'public_export.CORE_RUN_SHA256')
    ok(c['admit']['SELECTOR_SHA256'] == sha(f[P + 'public_inputs.py']), 'admit_public_inputs.SELECTOR_SHA256')
    man_raw = f[E + 'PUBLIC_PACKET_MANIFEST.json']
    man = json.loads(man_raw)
    packet_files = {p[len(P):] for p in f if p.startswith(P)}
    ok(set(man['members']) == packet_files, 'manifest members == packet population')
    for name, row in man['members'].items():
        ok(row == dict(bytes=len(f[P + name]), mode=256, sha256=sha(f[P + name])), 'manifest member ' + name)
    boot = c['boot']
    ok(boot['PLACEMENT_DESCRIPTOR'] == dict(bytes=len(f[P + 'root_placement.py']), sha256=sha(f[P + 'root_placement.py'])),
       'bootstrap_entry.PLACEMENT_DESCRIPTOR')
    ok(boot['MANIFEST_SHA256'] == sha(man_raw), 'bootstrap_entry.MANIFEST_SHA256 == sha(PUBLIC_PACKET_MANIFEST)')
    if records_present:
        ok(boot['ADMISSION_SHA256'] == sha(f[ROOT_RECORDS['BOOTSTRAP_ADMISSION.json']]), 'bootstrap_entry.ADMISSION_SHA256')
        ok(json.loads(f[ROOT_RECORDS['BOOTSTRAP_ADMISSION.json']])['manifest_sha256'] == sha(man_raw),
           'BOOTSTRAP_ADMISSION.manifest_sha256 == sha(PUBLIC_PACKET_MANIFEST)')
    # No stale digest anywhere in scope.
    stale = {h for p, hs in history.items() for h in hs if h != sha(f[p])}
    for p in f:
        found = set(HEX64.findall(f[p].decode('utf-8', 'replace'))) & stale
        ok(not found, 'no stale build digest in ' + p)
    changed = sorted(p for p in f if f[p] != base_files.get(p))
    ok(set(changed) <= ALLOWED_CHANGES, 'changed files within allowed set')
    return checks, changed


# ----------------------------------------------------------------------------- live consumer checks (Linux)

def live_checks(git, tree, files):
    """Load the exact pinned run.py and call the real consumers on an exported packet."""
    out = []
    if not sys.platform.startswith('linux'):
        return ['SKIPPED (not linux)']
    with tempfile.TemporaryDirectory(prefix='dg16succ-live-') as tmp:
        data = git.run('archive', '--format=tar', tree, Q)
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            tf.extractall(tmp, filter='data') if hasattr(tarfile, 'data_filter') else tf.extractall(tmp)
        packet = os.path.join(tmp, P)
        run_path = os.path.join(packet, 'run.py')
        run = types.ModuleType('dg16succ_live_run')
        run.__file__ = run_path
        exec(compile(open(run_path, 'rb').read(), run_path, 'exec'), run.__dict__)
        run.require_complete_packet()
        out.append('run.require_complete_packet() accepted')
        S = run.load_module('public_inputs')
        sel = S.admit(packet)
        out.append('public_inputs.admit(packet) accepted (index %s)' % sel['index_sha256'][:12])
        HC = run.load_module('host_composition')
        HC.binding()
        out.append('host_composition.binding() accepted')
        HC.check_admission(sel['bodies'][1], sel['bodies'], sel['support'], {'branch': NEW_MAIN})
        out.append('host_composition.check_admission(role1, ..., branch=%s) accepted' % NEW_MAIN)
        try:
            HC.check_admission(sel['bodies'][1], sel['bodies'], sel['support'], {'branch': OLD_MAIN})
            raise Refused('LIVE: check_admission accepted the OLD branch')
        except Refused:
            raise
        except Exception:
            out.append('host_composition.check_admission refuses old branch')
        hu = run.load_module('host_utility')
        pol_raw = files[ROOT_RECORDS['G1_HOST_PROFILE_POLICY.json']]
        pol = json.loads(pol_raw)
        need(hu.g1_host_policy_sha256() == pol['finite_host_policy_sha256'], 'LIVE: host_utility policy digest mismatch')
        hpb = types.ModuleType('dg16succ_live_hpb')
        exec(compile(files[E + 'host_profile_binding.py'], 'host_profile_binding.py', 'exec'), hpb.__dict__)
        core_pin = py_constants(files[E + 'core_prepare_entry.py'])['ROOT_POLICY_PIN']
        hpb._policy(pol_raw, core_pin, hu, pol['issued_unix_ms'])
        hpb._policy(pol_raw, core_pin, hu, pol['expires_unix_ms'] - 1)
        out.append('host_profile_binding._policy(policy, core ROOT_POLICY_PIN, real host_utility) accepted at issued and expires-1')
        RP = run.load_module('root_placement')
        man_raw = files[E + 'PUBLIC_PACKET_MANIFEST.json']
        RP.manifest(man_raw)
        adm = RP.parse(files[ROOT_RECORDS['BOOTSTRAP_ADMISSION.json']])
        need(adm == bootstrap_expected(man_raw) and RP.sha(man_raw) == adm['manifest_sha256'], 'LIVE: bootstrap admission')
        out.append('root_placement.manifest(manifest) accepted; bootstrap admission dict equals root_placement.bootstrap expectation')
        OP = run.load_module('operation')
        engine = OP.load_selected(__import__('pathlib').Path(os.path.realpath(SOURCE_ROOT)))
        out.append('operation.load_selected(fc2e416c) with the built pinned operation.py: PASS (15 bindings, entry %s)'
                   % engine.GenuineC5Session.__qualname__)
        RT = run.load_module('runtime_preflight')
        RT.selection(engine)
        out.append('runtime_preflight.selection(engine): PASS (native/startup/runtime pins == engine SPEC)')
        setup_raw = open(os.path.join(os.path.realpath(SOURCE_ROOT), run.SETUP), 'rb').read()
        need(sha(setup_raw) == run.SETUP_SHA, 'LIVE: SETUP_SHA differs from the source setup owner')
        out.append('run.SETUP_SHA == sha256(source %s)' % run.SETUP)
        out.append('base 2af600fa operation.load_selected: ' + ENGINE['base_load_selected'])
        out.extend(gate_behaviour(files[WF]))
    return out


def gate_behaviour(wf_raw):
    """Execute the real dispatch and main_guard scripts under bash with a synthetic exact context per image."""
    w = json.loads(wf_raw)
    steps = {s.get('id'): s for s in w['jobs']['qualify']['steps']}
    want = {IMAGE_23, IMAGE_376} if ACCEPT_376 else {IMAGE_23}
    out = []
    with tempfile.TemporaryDirectory(prefix='dg16succ-gate-') as tmp:
        for image in (IMAGE_23, IMAGE_376, '20261116.133.1', '20261122.23.2', '20261122.23.1x', ''):
            env = dict(PATH='/usr/bin:/bin', GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                       GITHUB_REPOSITORY=REPOSITORY, GITHUB_REF='refs/heads/' + NEW_MAIN, GITHUB_EVENT_NAME='create',
                       DG16_CREATED_BRANCH_EVENT='true', GITHUB_RUN_ATTEMPT='1', GITHUB_JOB='qualify', ImageOS='ubuntu24',
                       GITHUB_SHA='a' * 40, GITHUB_WORKFLOW_SHA='a' * 40, GITHUB_RUN_ID='123456789',
                       GITHUB_WORKFLOW_REF=REPOSITORY + '/' + WF + '@refs/heads/' + NEW_MAIN,
                       GITHUB_OUTPUT=os.path.join(tmp, 'out'), ImageVersion=image)
            row = []
            for sid, prefix in (('dispatch', 'DISPATCH_'), ('main_guard', 'MAIN04_')):
                r = subprocess.run(['bash', '-c', steps[sid]['run']], env=env, capture_output=True)
                accepted = r.returncode == 0
                need(accepted == (image in want), 'GATE: %s %s image %r rc=%d' % (sid, 'refused' if r.returncode else 'accepted', image, r.returncode))
                if not accepted:
                    need(r.stderr.decode().strip() == 'REFUSED: ' + prefix + 'IMAGEVERSION', 'GATE: %s wrong refusal for %r: %r' % (sid, image, r.stderr))
                row.append('%s=%s' % (sid, 'accept' if accepted else 'REFUSED ' + prefix + 'IMAGEVERSION'))
            out.append('gate %r: %s' % (image, ', '.join(row)))
    return out


# ----------------------------------------------------------------------------- tests

TEST_LINE = re.compile(r'^(test\S*) \((\S+)\)(?: \.\.\.|\n.*?\.\.\.)? .*?(ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$', re.M)


def run_suite(git, commit, source_root, tag, logdir):
    results = {}
    with tempfile.TemporaryDirectory(prefix='dg16succ-tests-') as tmp:
        wt = os.path.join(tmp, 'wt')
        git.run('worktree', 'add', '--detach', wt, commit)
        try:
            tests = os.path.join(wt, Q, 'tests')
            env = {k: v for k, v in os.environ.items() if k not in ('DG16_TEST_SOURCE_ROOT',)}
            if source_root:
                env['DG16_TEST_SOURCE_ROOT'] = source_root
            for name in sorted(os.listdir(tests)):
                if not (name.startswith('test_') and name.endswith('.py')):
                    continue
                r = subprocess.run([sys.executable, '-I', '-B', os.path.join(tests, name), '-v'], cwd=tmp, env=env,
                                   capture_output=True, timeout=1800)
                log = r.stdout.decode(errors='replace') + r.stderr.decode(errors='replace')
                if logdir:
                    with open(os.path.join(logdir, '%s-%s.log' % (tag, name)), 'w') as fh:
                        fh.write(log)
                cases = {}
                for m in re.finditer(r'^(test\w*) \(([\w.]+)\)\s*(?:\n[^\n]*?)?\.\.\. (ok|FAIL|ERROR|skipped[^\n]*|expected failure|unexpected success)$', log, re.M):
                    cases[m.group(2) + '.' + m.group(1)] = m.group(3).split(' ')[0]
                last = [l for l in log.strip().split('\n') if l][-1] if log.strip() else ''
                results[name] = dict(rc=r.returncode, summary=last, cases=cases)
        finally:
            git.run('worktree', 'remove', '--force', wt)
    return results


def compare_suites(base, succ):
    report, regressions = {}, []
    for name in sorted(set(base) | set(succ)):
        b, s = base.get(name), succ.get(name)
        need(s is not None, 'test file missing in successor: ' + name)
        if b is None:
            need(s['rc'] == 0 and s['cases'] and all(v == 'ok' for v in s['cases'].values()),
                 'new successor control %s is not green: %s' % (name, s['summary']))
            report[name] = dict(base_rc=None, successor_rc=s['rc'], base='ABSENT (new control)', successor=s['summary'],
                                cases=len(s['cases']), base_ok=None, successor_ok=len(s['cases']), newly_ok=sorted(s['cases']))
            continue
        need(set(b['cases']) == set(s['cases']), 'test case population differs in ' + name)
        for case in sorted(s['cases']):
            if b['cases'][case] == 'ok' and s['cases'][case] != 'ok':
                regressions.append(name + ':' + case)
        fixed = [k for k in s['cases'] if s['cases'][k] == 'ok' and b['cases'][k] != 'ok']
        report[name] = dict(base_rc=b['rc'], successor_rc=s['rc'], base=b['summary'], successor=s['summary'],
                            cases=len(s['cases']), base_ok=sum(v == 'ok' for v in b['cases'].values()),
                            successor_ok=sum(v == 'ok' for v in s['cases'].values()), newly_ok=fixed)
    return report, regressions


# ----------------------------------------------------------------------------- build

def load_base(git):
    need(git.text('rev-parse', BASE_COMMIT + '^{commit}') == BASE_COMMIT, 'base commit missing')
    need(git.text('rev-parse', BASE_COMMIT + '^{tree}') == BASE_TREE, 'base tree mismatch')
    rows = git.ls_tree(BASE_COMMIT, Q, WF)
    need(all(m == '100644' and k == 'blob' for m, k, _ in rows.values()), 'unexpected modes in scope')
    files = {p: git.blob(oid) for p, (_, _, oid) in rows.items()}
    return rows, files


def load_operation_module(raw, name):
    mod = types.ModuleType(name)
    mod.__file__ = name + '.py'
    exec(compile(raw, name + '.py', 'exec'), mod.__dict__)
    return mod


def derive_engine(base_files):
    """Load the pinned engine from the fc2e416c checkout exactly as operation.load_selected does."""
    need(SOURCE_ROOT is not None and sys.platform.startswith('linux'), 'engine derivation needs Linux and --source-root')
    src = os.path.realpath(SOURCE_ROOT)
    head = subprocess.run(['git', '-C', src, 'rev-parse', 'HEAD', 'HEAD^{tree}'], capture_output=True, text=True).stdout.split()
    need(head == [SOURCE_COMMIT, SOURCE_TREE], '--source-root must be a clean checkout of %s' % SOURCE_COMMIT)
    dirty = subprocess.run(['git', '-C', src, 'status', '--porcelain', '--untracked-files=all'], capture_output=True, text=True).stdout
    need(dirty == '', '--source-root checkout is not clean')
    op = load_operation_module(base_files[P + 'operation.py'], 'dg16succ_base_operation')
    path = os.path.join(src, 'scripts/load-work-graph-c5-executor.py')
    raw = open(path, 'rb').read()
    need(sha(raw) == op.LOADER_SHA256, 'LOADER_PIN_DIFFERS')
    loader = types.ModuleType('dg16succ_loader')
    loader.__file__ = path
    exec(compile(raw, path, 'exec'), loader.__dict__)
    need(loader.R5_HOSTED_PROFILE == op.PROFILE and loader.R5_IMAGE23_RUNTIME_SOURCE_REVISION == op.REVISION, 'PROFILE_SELECTION_DIFFERS')
    engine = loader._Engine(op.PROFILE, source_revision=op.REVISION).load()
    need(open(path, 'rb').read() == raw, 'LOADER_CHANGED_DURING_LOAD')
    engine.CHECK()
    derived = {name: dict(bytes=len(row[0]), sha256=sha(row[0])) for name, row in engine.SOURCES.items()}
    need(engine.GenuineC5Session.__qualname__ == op.C5_ENTRYPOINT and op.REVISION == op.C5_SOURCE_REVISION, 'ENTRYPOINT_OR_REVISION')
    try:
        op.load_selected(__import__('pathlib').Path(src))
        base_result = 'PASS'
    except ValueError as exc:
        base_result = 'REFUSED %s (message sha256 %s)' % (exc, sha(str(exc).encode()))
    ENGINE.update(engine=engine, bindings=derived, base_load_selected=base_result,
                  loader=dict(sha256=sha(raw), profile=op.PROFILE, revision=op.REVISION))
    # Every operator copy must differ from the engine ONLY in the executor row, and only by the known stale value.
    for rel, const in sorted(BINDING_CONSTANTS.items()):
        pinned = py_constants(base_files[Q + rel])[const]
        diff = sorted(k for k in set(pinned) | set(derived) if pinned.get(k) != derived.get(k))
        need(diff == [EXECUTOR_NAME] and pinned[EXECUTOR_NAME] == EXECUTOR_STALE,
             'engine/operator binding difference in %s is %s, expected only the stale executor row' % (rel, diff))
    need(derived[EXECUTOR_NAME] == EXECUTOR_EXPECTED, 'engine-derived executor binding %s differs from the reported %s'
         % (derived[EXECUTOR_NAME], EXECUTOR_EXPECTED))
    return derived


def successor_edits(base_files):
    files = dict(base_files)
    count = sum(raw.count(OLD_MAIN.encode()) for raw in files.values())
    need(count == EXPECTED_LITERAL_OCCURRENCES, 'expected %d old branch literal occurrences, found %d' % (EXPECTED_LITERAL_OCCURRENCES, count))
    need(not any(NEW_MAIN.encode() in raw for raw in files.values()), 'new branch literal already present')
    for p, raw in files.items():
        if p in ROOT_RECORDS.values():
            continue
        if OLD_MAIN.encode() in raw:
            files[p] = raw.replace(OLD_MAIN.encode(), NEW_MAIN.encode())
    wf = files[WF].decode()
    need(json.loads(wf)['on'] == {'create': None}, 'base workflow trigger is not exactly on: create')
    if ACCEPT_376:
        for step, (before, after) in sorted(IMAGE_EDITS.items()):
            b, a = json.dumps(before)[1:-1], json.dumps(after)[1:-1]
            need(wf.count(b) == 1, 'workflow %s image text not found exactly once' % step)
            wf = wf.replace(b, a)
    files[WF] = wf.encode()
    derived = ENGINE['bindings']
    old_row = "'%s': {'bytes': %d, 'sha256': '%s'}" % (EXECUTOR_NAME, EXECUTOR_STALE['bytes'], EXECUTOR_STALE['sha256'])
    new_row = "'%s': {'bytes': %d, 'sha256': '%s'}" % (EXECUTOR_NAME, derived[EXECUTOR_NAME]['bytes'], derived[EXECUTOR_NAME]['sha256'])
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_load_selected.py')
    test_raw = open(test_path, 'rb').read()
    need(sha(test_raw) == LOAD_SELECTED_TEST_SHA256, 'test_load_selected.py next to the builder differs from its pin')
    need(LOAD_SELECTED_TEST not in files, 'load_selected control already exists in the base')
    files[LOAD_SELECTED_TEST] = test_raw
    for rel in sorted(BINDING_CONSTANTS):
        text = files[Q + rel].decode('utf-8')
        need(text.count(old_row) == 1, 'stale executor row not found exactly once in ' + rel)
        files[Q + rel] = text.replace(old_row, new_row).encode('utf-8')
    return files


def build_tree(git, base_rows, files, changed):
    with tempfile.TemporaryDirectory(prefix='dg16succ-index-') as tmp:
        env = {'GIT_INDEX_FILE': os.path.join(tmp, 'index')}
        git.run('read-tree', BASE_COMMIT, env=env)
        for p in changed:
            oid = git.text('hash-object', '-w', '--stdin', data=files[p])
            git.run('update-index', '--add', '--cacheinfo', '%s,%s,%s' % (base_rows.get(p, ('100644',))[0], oid, p), env=env)
        return git.text('write-tree', env=env)


def commit_message(files, policy):
    rec = {n: sha(files[p]) for n, p in ROOT_RECORDS.items()}
    return ('Prepare DG16 IMAGE23 create-event successor with engine-derived executor binding\n\n'
            'Successor of 2af600fad0e80fa71d9f808741bd74db792308b2, whose branch %s\n'
            'is spent (run 46046841410 refused SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY at prepare).\n'
            'Changes, and nothing else:\n'
            '- main/control branch literals -> %s(-control); on: create, job if,\n'
            '  env guard, permissions, timeouts and every step otherwise unchanged (23.1 only);\n'
            '- executor binding for %s in operation.py, g3_receiving.py and\n'
            '  proof_consumer.py -> %d/%s, derived by loading the pinned\n'
            '  engine (loader %s) from %s;\n'
            '- new offline control tests/test_load_selected.py (pinned load_selected on the real source);\n'
            '- Root-issued records inserted verbatim:\n'
            '  G1_HOST_PROFILE_POLICY.json      %s\n'
            '    profile_ids %s, issued %s, expires %s\n'
            '  COMPOSITION_ROOT_ADMISSION.json  %s\n'
            '  BOOTSTRAP_ADMISSION.json         %s\n'
            '- dependent pins recomputed (manifest %s).\n\n'
            'Intended trigger (not performed by this commit or its builder):\n'
            '  git push origin <this commit>:refs/heads/%s\n\n'
            'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n') % (
        OLD_MAIN, NEW_MAIN, EXECUTOR_NAME, ENGINE['bindings'][EXECUTOR_NAME]['bytes'], ENGINE['bindings'][EXECUTOR_NAME]['sha256'],
        ENGINE['loader']['sha256'][:12], SOURCE_COMMIT[:12],
        rec['G1_HOST_PROFILE_POLICY.json'], ','.join(policy['profile_ids']), ms_to_iso(policy['issued_unix_ms']),
        ms_to_iso(policy['expires_unix_ms']), rec['COMPOSITION_ROOT_ADMISSION.json'], rec['BOOTSTRAP_ADMISSION.json'],
        sha(files[E + 'PUBLIC_PACKET_MANIFEST.json']), NEW_MAIN)


def assemble(base_files, policy_raw, comp_raw, boot_raw, warnings):
    """Successor content. Phase A excludes the bootstrap admission (it binds the manifest); phase B inserts it."""
    files = successor_edits(base_files)
    frozen = set(ROOT_RECORDS.values())
    files[ROOT_RECORDS['G1_HOST_PROFILE_POLICY.json']] = policy_raw
    files[ROOT_RECORDS['COMPOSITION_ROOT_ADMISSION.json']] = comp_raw
    policy = check_policy(policy_raw, files, warnings)
    files.pop(ROOT_RECORDS['BOOTSTRAP_ADMISSION.json'])
    history = propagate(files, base_files, frozen)
    check_composition(comp_raw, files, json.loads(files[P + 'PUBLIC_INPUT_INDEX.json']))
    man_raw = files[E + 'PUBLIC_PACKET_MANIFEST.json']
    if boot_raw is None:
        return files, history, policy, man_raw, 'PHASE1_BOOTSTRAP_ADMISSION_REQUIRED', None
    try:
        check_bootstrap(boot_raw, man_raw)
    except Refused as exc:
        return files, history, policy, man_raw, 'PHASE1_BOOTSTRAP_ADMISSION_MISMATCH', str(exc)
    files[ROOT_RECORDS['BOOTSTRAP_ADMISSION.json']] = boot_raw
    second = propagate(files, base_files, frozen)
    for p, hs in second.items():
        merged = history.setdefault(p, [])
        for h in hs:
            if h not in merged:
                merged.append(h)
    need(files[E + 'PUBLIC_PACKET_MANIFEST.json'] == man_raw, 'manifest changed after bootstrap insertion')
    return files, history, policy, man_raw, 'COMPLETE', None


def cmd_build(args, git):
    report = dict(base_commit=BASE_COMMIT, base_tree=BASE_TREE, warnings=[])
    base_rows, base_files = load_base(git)
    derive_engine(base_files)
    report['engine'] = dict(loader=ENGINE['loader'], executor_binding=ENGINE['bindings'][EXECUTOR_NAME],
                            bindings=len(ENGINE['bindings']), base_load_selected=ENGINE['base_load_selected'])
    present = {}
    for name in ROOT_RECORDS:
        src = os.path.join(args.records, name)
        if os.path.exists(src):
            with open(src, 'rb') as fh:
                present[name] = fh.read()
    need('G1_HOST_PROFILE_POLICY.json' in present and 'COMPOSITION_ROOT_ADMISSION.json' in present,
         'records dir must contain at least G1_HOST_PROFILE_POLICY.json and COMPOSITION_ROOT_ADMISSION.json')
    files, history, policy, man_raw, state, why = assemble(
        base_files, present['G1_HOST_PROFILE_POLICY.json'], present['COMPOSITION_ROOT_ADMISSION.json'],
        present.get('BOOTSTRAP_ADMISSION.json'), report['warnings'])
    report['checks_policy'] = ('PASS: real host_profile_binding._policy (accepts at issued and expires-1, refuses at '
                               'issued-1 and expires) and _operation; D4 scope/source/time/profile/operation; canonical encoding')
    report['checks_composition'] = ('PASS: public_inputs role-1 provenance (issuer) + host_composition.check_admission replica '
                                    '(fields, scope, workflow_branch, body binding) + control/source branch')
    report['manifest_sha256'] = sha(man_raw)
    expected_boot = compact(bootstrap_expected(man_raw))
    report['expected_bootstrap_admission'] = dict(sha256=sha(expected_boot), bytes=len(expected_boot), body=expected_boot.decode())
    if state != 'COMPLETE':
        report['phase'] = state
        if why:
            report['refusal'] = why
        emit(report, args)
        return 3
    report['checks_bootstrap'] = ('PASS: root_placement.bootstrap admission replica (size, unique keys, field set, types, '
                                  'exact dict incl. workflow_branch and manifest_sha256)')
    checks, changed = verify(files, base_files, history, True)
    report['verification_checks'] = len(checks)
    tree = build_tree(git, base_rows, files, changed)
    env = dict(GIT_AUTHOR_NAME=AUTHOR[0], GIT_AUTHOR_EMAIL=AUTHOR[1], GIT_AUTHOR_DATE=COMMIT_DATE,
               GIT_COMMITTER_NAME=AUTHOR[0], GIT_COMMITTER_EMAIL=AUTHOR[1], GIT_COMMITTER_DATE=COMMIT_DATE)
    sign = subprocess.run(['git', '-C', git.repo, 'config', '--get', 'commit.gpgsign'], capture_output=True).stdout.strip()
    need(sign not in (b'true', b'1', b'yes', b'on'), 'commit.gpgsign is enabled; a signature would make the commit non-deterministic')
    commit = git.text('commit-tree', tree, '-p', BASE_COMMIT, '-F', '-', data=commit_message(files, policy).encode(), env=env)
    rows2 = git.ls_tree(commit, Q, WF)
    files2 = {p: git.blob(oid) for p, (_, _, oid) in rows2.items()}
    need(files2 == files, 'committed tree differs from verified content')
    need(git.text('rev-parse', commit + '^') == BASE_COMMIT, 'parent mismatch')
    whole = git.run('diff', '--name-only', BASE_COMMIT, commit).decode().split()
    need(set(whole) == set(changed), 'whole-tree diff differs from scope diff')
    stale_global = {h for p, hs in history.items() for h in hs if h != sha(files[p])}
    hits = git.grep_any(commit, stale_global)
    need(not hits, 'stale digest(s) anywhere in the whole tree: %s' % hits)
    n_old, where_old = git.grep_count(commit, OLD_MAIN)
    need(n_old == 0, 'old branch literal remains in whole tree: %s' % where_old)
    n_new, where_new = git.grep_count(commit, NEW_MAIN)
    need(n_new == EXPECTED_LITERAL_OCCURRENCES, 'new literal count in whole tree %d' % n_new)
    report.update(commit=commit, tree=tree, parent=BASE_COMMIT, changed_files=changed,
                  pins={p: dict(old=sha(base_files[p]) if p in base_files else None, new=sha(files[p]),
                               old_bytes=len(base_files[p]) if p in base_files else None, new_bytes=len(files[p]))
                        for p in changed},
                  root_records={n: dict(sha256=sha(files[p]), bytes=len(files[p])) for n, p in ROOT_RECORDS.items()},
                  new_literal_files=where_new,
                  verification='PASS (%d checks + whole-tree stale-digest/literal scan)' % len(checks),
                  intended_trigger='git push origin %s:refs/heads/%s' % (commit, NEW_MAIN))
    report['live_consumer_checks'] = live_checks(git, tree, files)
    if args.local_branch:
        need(args.local_branch.startswith('local/') and NEW_MAIN not in args.local_branch,
             'local branch must be under local/ and must not carry the trigger branch name')
        git.run('update-ref', 'refs/heads/' + args.local_branch, commit)
        report['local_branch'] = args.local_branch
    if args.tests:
        logdir = args.test_logs
        if logdir:
            os.makedirs(logdir, exist_ok=True)
        base_res = run_suite(git, BASE_COMMIT, SOURCE_ROOT, 'base', logdir)
        succ_res = run_suite(git, commit, SOURCE_ROOT, 'successor', logdir)
        suites, regressions = compare_suites(base_res, succ_res)
        report['tests'] = suites
        report['test_regressions'] = regressions
        report['successor_suite_rc'] = max(r['rc'] for r in succ_res.values())
        report['base_suite_rc'] = max(r['rc'] for r in base_res.values())
        if regressions:
            report['phase'] = 'REFUSED_TEST_REGRESSION'
            emit(report, args)
            return 2
    report['phase'] = 'BUILT'
    emit(report, args)
    return 0


def emit(report, args):
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        with open(args.report, 'w') as fh:
            fh.write(text + '\n')
    print(text)


def cmd_draft(args, git):
    """Write proposed Root records (DRAFTS): only branch names, manifest digest, profile_ids and times differ from 709bbc75."""
    _, base_files = load_base(git)
    derive_engine(base_files)
    issued = iso_to_ms(args.issued)
    expires = issued + POLICY_WINDOW_MS
    old = {n: base_files[p] for n, p in ROOT_RECORDS.items()}
    for raw in old.values():
        need(compact(json.loads(raw)) == raw, 'base Root record is not in canonical compact form')
    pol = json.loads(old['G1_HOST_PROFILE_POLICY.json'])
    pol['operation']['branch'] = NEW_MAIN
    pol['profile_ids'] = sorted(args.profile_ids)
    pol['issued_unix_ms'] = issued
    pol['expires_unix_ms'] = expires
    comp = json.loads(old['COMPOSITION_ROOT_ADMISSION.json'])
    comp['workflow_branch'] = NEW_MAIN
    comp['control_branch'] = NEW_CONTROL
    warnings = []
    files, _, _, man_raw, state, _ = assemble(base_files, compact(pol), compact(comp), None, warnings)
    need(state == 'PHASE1_BOOTSTRAP_ADMISSION_REQUIRED', 'unexpected draft state')
    boot = json.loads(old['BOOTSTRAP_ADMISSION.json'])
    boot['workflow_branch'] = NEW_MAIN
    boot['manifest_sha256'] = sha(man_raw)
    need(boot == bootstrap_expected(man_raw), 'draft bootstrap differs from expectation')
    os.makedirs(args.out, exist_ok=True)
    out = {}
    for name, value in (('G1_HOST_PROFILE_POLICY.json', pol), ('COMPOSITION_ROOT_ADMISSION.json', comp),
                        ('BOOTSTRAP_ADMISSION.json', boot)):
        raw = compact(value)
        with open(os.path.join(args.out, name), 'wb') as fh:
            fh.write(raw)
        out[name] = dict(sha256=sha(raw), bytes=len(raw))
    print(json.dumps(dict(drafts=out, manifest_sha256=sha(man_raw), issued=ms_to_iso(issued), expires=ms_to_iso(expires),
                          warnings=warnings, note='DRAFT: Root sets real issued/expires and issues the records; rerun build'),
                     indent=2, sort_keys=True))
    return 0


def set_branch(name):
    """Validate and select the successor main branch; the control branch is always NAME-control."""
    global NEW_MAIN, NEW_CONTROL
    need(type(name) is str and not any(name == x or name.startswith(x) for x in SPENT_BRANCHES),
         'branch %r is a spent operator branch; a new one-use branch name is required' % name)
    need(name.startswith(BRANCH_PREFIX) and len(name) > len(BRANCH_PREFIX), 'branch must start with ' + BRANCH_PREFIX)
    need(re.fullmatch(r'engineering/[A-Za-z0-9][A-Za-z0-9/_-]{0,150}', name) is not None and '..' not in name
         and '//' not in name and not name.endswith('-control') and not name.endswith('/'),
         'branch name shape refused (also must satisfy host_utility branch regex and not end in -control)')
    NEW_MAIN, NEW_CONTROL = name, name + '-control'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', required=True, help='local git repository containing 2af600fa')
    ap.add_argument('--source-root', required=True, help='clean checkout of fc2e416c (engine derivation, load_selected, tests)')
    ap.add_argument('--branch', default=DEFAULT_BRANCH,
                    help='successor main branch (control = NAME-control); must start with %s; default %s' % (BRANCH_PREFIX, DEFAULT_BRANCH))
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('draft')
    d.add_argument('--issued', required=True, help='policy issued time, e.g. 2026-11-28T00:00:00Z (expires = +390 min)')
    d.add_argument('--profile-ids', nargs='+', default=DRAFT_PROFILE_IDS)
    d.add_argument('--out', required=True)
    b = sub.add_parser('build')
    b.add_argument('--records', required=True, help='directory with the Root-issued record files')
    b.add_argument('--local-branch', help='optional LOCAL ref under local/ to point at the commit')
    b.add_argument('--tests', action='store_true', help='run the offline suite on base and successor (Linux)')
    b.add_argument('--test-logs', help='directory for per-file test logs')
    b.add_argument('--report', help='write the JSON report here')
    args = ap.parse_args(argv)
    global NEW_MAIN, NEW_CONTROL, SOURCE_ROOT
    SOURCE_ROOT = args.source_root
    try:
        set_branch(args.branch)
    except Refused as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2
    git = Git(args.repo)
    try:
        return cmd_draft(args, git) if args.cmd == 'draft' else cmd_build(args, git)
    except Refused as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
