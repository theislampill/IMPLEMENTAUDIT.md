"""Disposable source-only fixtures. Never invoke a product source or hosted owner."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EPISODE = ROOT / 'qualification/dg16-r5-g1-hosted-episode'
BASE = 'b393a9057c249335e6cdf4ccbb898d192b0830b8'
C53 = 'c53ed7de85de22ce313233472c8d8f02ad8e9d02'
E76 = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
M5 = '205aeab7c93299b0666b261485ab5658d8e183de'
BRANCH = 'pro/dg16-g132-boot-nss-source-20261122-01'
BUILD = sorted(('scripts/package-contract.py', 'scripts/build-release-asset.sh',
                'scripts/write-release-checksums.sh', 'scripts/check-package-contract.sh'))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def historical_manifest():
    return git('show', BASE + ':' + (EPISODE.relative_to(ROOT) / 'SOURCE_MANIFEST.json').as_posix())


def load_owner(name, directory=EPISODE):
    spec = importlib.util.spec_from_file_location(name, directory / (name + '.py'))
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    return owner


def enc(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def desc(body):
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def source_row(commit, path):
    mode, _, oid = git('ls-tree', commit, '--', path).split(b'\t')[0].decode().split()
    return dict(path=path, mode=mode, git_blob=oid, **desc(git('cat-file', 'blob', oid)))


def source_manifests():
    # Reuse the exact public e76 manifest. Independently read every changed blob.
    old = json.loads(historical_manifest())
    assert old['commit'] == E76
    old_rows = {row['path']: row for row in old['members']}
    def rows_at(commit):
        rows = old_rows.copy()
        for path in git('diff', '--name-only', E76, commit).decode().splitlines():
            rows[path] = source_row(commit, path)
        return rows
    previous, current = rows_at(M5), rows_at(C53)
    changes = [dict(path=path, before=previous.get(path), after=current.get(path))
               for path in sorted(previous.keys() | current.keys()) if previous.get(path) != current.get(path)]
    parent = git('rev-parse', C53 + '^').decode().strip()
    manifest = dict(old, commit=C53, tree=git('rev-parse', C53 + '^{tree}').decode().strip(),
                    parent_commit=parent, parent_tree=git('rev-parse', parent + '^{tree}').decode().strip(),
                    file_count=len(current), total_bytes=sum(v['bytes'] for v in current.values()),
                    members=[current[path] for path in sorted(current)])
    canonical = sorted(p for p in current if p.startswith('skills/implementaudit/') or
                       p in ('.claude-plugin/marketplace.json', '.claude-plugin/plugin.json',
                             '.codex-plugin/plugin.json', 'package/implementaudit-package.json') or
                       p in {f'skills/{s}/SKILL.md' for s in ('audit-andon','audit-implement','audit-state','audit-assess')})
    assert (len(previous), len(current), len(changes), len(canonical)) == (1766, 1778, 16, 74)
    return manifest, previous, changes, canonical


def fixture(manifest, previous, changes, canonical, history, mutate=None):
    """Only historical bytes are real. All current identities/observations are synthetic."""
    mraw = enc(manifest)
    subject = dict(commit=C53, tree='d60733459425a059d961b6adc2aae9811bbb761c',
                   parent_commit='760aaff5c478ff7354d36da186d62daba983aa49',
                   parent_tree='f85b199c89e9f6938382ec5f7b2005f54acc8536', branch=BRANCH,
                   files=1778, bytes=167283667, manifest=desc(mraw))
    anchor = dict(issuer='SYNTHETIC-ROOT', receiver='SYNTHETIC-INDEPENDENT',
                  controller='SYNTHETIC-CONTROLLER', receipt_sha256=desc(b'SYNTHETIC CURRENT RECEIPT')['sha256'])
    observed = dict(commit=M5, tree='9ffbaf95080092bf4a45b8772a97ed16068544a7')
    historical = deepcopy(history['evidence_bodies'])
    evidence = {}
    def add(name, document):
        if mutate:
            mutate(name, document)
        evidence[name] = enc(document).decode()
        return desc(evidence[name].encode())
    def record(kind, actor, **fields):
        return dict(schema='dg16.maintained-source-' + kind + '.v1', subject=deepcopy(subject),
                    actor=actor, controller=anchor['controller'], receipt_sha256=anchor['receipt_sha256'], **fields)
    ph = add('PHYSICAL_PRODUCT_READBACK.json', record('physical-readback', anchor['receiver'],
             all_members_exact=True, clean=True, errors=[]))
    pub = add('PRODUCT_PUBLICATION_RECEIVING.json', record('publication-receiving', anchor['receiver'],
              repository='theislampill/IMPLEMENTAUDIT.md', exact_ref_readback=True))
    ind = add('INDEPENDENT_RECEIVING.json', record('independent-receiving', anchor['receiver'],
              physical=ph, publication=pub, decision='RECEIVE_EXACT_SOURCE_ONLY', original_awards=[]))
    verified_changes = deepcopy(changes)
    technical = json.loads(historical['M5_RECEIVING.json'])
    root = add('ROOT_PACKAGE_SOURCE_APPLICABILITY.json', record('package-applicability', anchor['issuer'],
               decision='ACCEPT_EXACT_NONPACKAGE_SOURCE_RELATION', observed_package_source=observed,
               previous_package_receiving=history['evidence']['M5_RECEIPT.json'],
               archives=technical['packages']['artifacts'], independent_receiving=ind,
               changes_vs_m5=verified_changes, changes_vs_e76=[r for r in verified_changes if not r['path'].startswith('tests/')],
               canonical_inputs=canonical.copy(), build_owners=BUILD.copy(), unchanged_members=1762,
               package_leg='NOT_TRIGGERED', current_build_or_copy_observations=0,
               full_Q04_Q05=False, native_discovery='UNVERIFIED', original_awards=[], effect_grant='NONE'))
    current = add('ROOT_SOURCE_CURRENTNESS.json', record('root-currentness', anchor['issuer'],
                  package_applicability=root, independent_receiving=ind, physical=ph, publication=pub,
                  decision='RECEIVE_SELECTED_SOURCE_AT_BOUND_RECEIPT', original_awards=[], effect_grant='NONE'))
    relation = dict(schema='dg16.maintained-nonpackage-applicability.v1',
                    selected_source=subject, observed_package_source=observed,
                    current_root_applicability=root, current_root_source_receiving=current, independent_receiving=ind,
                    retained_package_receiving=history['evidence']['M5_RECEIPT.json'],
                    changed_project_paths=[r['path'] for r in changes], unchanged_source_members=1762,
                    canonical_inputs=74, build_owners=4, package_leg='NOT_TRIGGERED', no_new_build_or_copy=True,
                    full_Q04_Q05=False, native_discovery='UNVERIFIED', original_awards=[])
    acq = dict(schema='dg16.current-source-maintained-package-acquisition.v5', authority='NONE',
               status='PASS', commit=C53, tree=subject['tree'], files=1778, bytes=167283667,
               manifest_sha256=desc(mraw)['sha256'], errors=[], original_awards=[], package_relation=relation,
               evidence_bodies=evidence, evidence={n: desc(b.encode()) for n,b in evidence.items()},
               historical_evidence_bodies=historical, historical_evidence=deepcopy(history['evidence']))
    basis = dict(current_subject=dict(commit=C53,tree=subject['tree']), maintained_source_authority=anchor,
                 source_inventory_sha256=desc(mraw)['sha256'], retained_package_relation=deepcopy(relation),
                 received_inputs={'SOURCE_ACQUISITION.json': desc(enc(acq))})
    return acq, basis, {'SOURCE_ACQUISITION.json': enc(acq)}
