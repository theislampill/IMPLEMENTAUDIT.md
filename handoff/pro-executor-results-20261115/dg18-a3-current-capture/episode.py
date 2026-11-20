#!/usr/bin/env python3
"""Prospective complete A3 discriminator against the unchanged current product.

No effect occurs on import. This is a new declared disposable fixture, not a
reconstruction of historical evidence or an authenticated native occurrence.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import zipfile

CANARY_PATH = 'evidence/archived-only/phase-999.md'
MISSING_CAPTURE = 'evidence/A3_CANARY_CAPTURE_NEVER_CREATED.txt'
CANARY = (
    '# Original A3 archived-content discriminator\n\n'
    'This is declared historical evidence, not an active phase.\n\n'
    '## Mandatory commands\n'
    '- command: true; capture: <run-root>/evidence/A3_CANARY_CAPTURE_NEVER_CREATED.txt; expected: exit 0\n\n'
    '## Historical terminal record\n'
    'IMPLEMENTAUDIT_PHASE_DONE\n'
    'Status: done\n'
).encode()
SCHEMA = 'dg18.prospective-original-a3-full-discriminator.v1'


def identity(raw):
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def write_new(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as handle:
        handle.write(raw);handle.flush();os.fsync(handle.fileno())


def archive_canary_binding(manifest,objects):
    """Data-only indexing of actual archive bytes; not an owner replacement."""
    if (manifest.get('schema')!='implementaudit.state-archive.v1' or
        manifest.get('authority_ceiling')!='ARCHIVED_ONLY_HISTORY' or
        manifest.get('discovery')!='EXCLUDED_FROM_CURRENT_AND_RECURSIVE_POPULATIONS' or
        manifest.get('retention')!='NO_DELETE_WITHOUT_ACCEPTED_RETENTION_SUCCESSOR'):
        raise ValueError('actual archive classification differs')
    entries=manifest['entries']
    if len({row['artifact_id'] for row in entries})!=len(entries):
        raise ValueError('duplicate archive artifact identity')
    for row in entries:
        raw=objects[row['blob_oid']];got=identity(raw)
        if (got['git_blob']!=row['blob_oid'] or got['bytes']!=row['byte_length'] or
            got['sha256']!=row['sha256']):
            raise ValueError('actual archive member readback differs')
    selected=[row for row in entries if row['source_path']==CANARY_PATH]
    if len(selected)!=1 or selected[0]['role']!='EVIDENCE' or objects[selected[0]['blob_oid']]!=CANARY:
        raise ValueError('exact canary is not an actual archived EVIDENCE member')
    return {'entry':selected[0],'canary':identity(CANARY),'archive_member_count':len(entries),
            'authority_ceiling':manifest['authority_ceiling'],'discovery':manifest['discovery']}


def build_case(original, evidence_root, set_phase):
    """Build one new case on the exact existing fixture; do not execute it."""
    evidence_root=Path(evidence_root)

    class ProspectiveA3ArchiveIsolation(original.CanonicalReaderTests):
        def setUp(self):
            self.a3={'schema':SCHEMA,'authority':'NONE','original_criterion':3,'original_denominator':14,
                     'prospective_fixture':True,'native_host_occurrence':False,'checks':[],
                     'snapshots':[],'commands':[],'archives':[],'method_completed':False}
            super().setUp()
            self.addCleanup(self.retain_final)

        def check(self,condition,label):
            self.assertTrue(condition,label)
            self.a3['checks'].append(label)

        def store_content(self,raw):
            descriptor=identity(raw)
            path=evidence_root/'content'/descriptor['sha256']
            if path.exists():self.assertEqual(path.read_bytes(),raw)
            else:write_new(path,raw)
            return {'content_path':path.relative_to(evidence_root).as_posix(),**descriptor}

        def refs(self):
            return self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit/').splitlines()

        def snapshot(self,label):
            files=[]
            roots=[self.run,*sorted(self.repo.glob('a3-read-*'))]
            for folder in roots:
                for path in sorted(folder.rglob('*')):
                    info=path.lstat()
                    self.assertFalse(stat.S_ISLNK(info.st_mode),'linked fixture snapshot member')
                    if not stat.S_ISREG(info.st_mode):continue
                    files.append({'path':path.relative_to(self.repo).as_posix(),
                                  'mode':oct(info.st_mode&0o7777),**self.store_content(path.read_bytes())})
            record={'label':label,'refs':self.refs(),'files':files,
                    'file_count':len(files),'file_bytes':sum(row['bytes'] for row in files)}
            path=evidence_root/'snapshots'/(label+'.json');write_new(path,canonical(record))
            self.a3['snapshots'].append({'label':label,'path':path.relative_to(evidence_root).as_posix(),**identity(path.read_bytes())})
            return record

        def observed(self,label,result,success,diagnostic=None):
            record={'label':label,'exit_code':result.returncode,'stdout':self.store_content(result.stdout),
                    'stderr':self.store_content(result.stderr),'expected_success':success}
            self.a3['commands'].append(record)
            self.check((result.returncode==0)==success,label+' exact success/refusal')
            if diagnostic is not None:self.check(diagnostic in result.stderr,label+' original diagnostic')
            return result

        def current_views(self,label,resolved):
            set_phase(label)
            before=self.refs()
            self.output=self.repo/('a3-read-'+label);self.output.mkdir()
            self.observed(label+' native reader',self.read('--native-guards'),True)
            for role in ('STATE','ROADMAP'):
                raw=(self.output/(role+'.md')).read_bytes()
                self.check(raw==Path(resolved[role.lower()+'_path']).read_bytes(),label+' exact '+role+' current bytes')
                self.check(hashlib.sha256(raw).hexdigest()==resolved['pointer'][role.lower()+'_sha256'],label+' '+role+' pointer digest')
            self.check(json.loads((self.output/'resolution.json').read_bytes())==resolved,label+' exact resolution')
            state=(self.output/'native-STATE.md').read_text()
            self.check(state.count('Current epoch:')==1,label+' single derived live epoch')
            self.check('Current epoch: '+resolved['pointer']['continuity_epoch']+'\n' in state,label+' current epoch selected')
            archived_view=self.output/'native-records'/CANARY_PATH
            self.check(archived_view.read_bytes()==CANARY,label+' exact nested evidence view retained')
            self.check(not (self.output/'native-records/phases/phase-999.md').exists(),label+' canary excluded from current phase view')
            self.observed(label+' run-root validator',self.validate(),True)
            phase=original.command(['bash',self.scripts/'validate-phase.sh','--mutation-authority',
                self.run/'phases/phase-1.md','--phase','1','--step','1','--repo-root',self.repo,'--run-root',self.run],self.repo)
            self.observed(label+' original phase authority',phase,True)
            self.check(json.loads(phase.stdout)['operation']=='replace',label+' exact declared phase operation')
            self.check(self.refs()==before,label+' reader and validators preserve every authority ref')
            return self.snapshot(label)

        def actual_archive(self,label,resolved):
            pointer=resolved['pointer'];generation=pointer['projection_generation_id']
            self.check(resolved['schema']=='implementaudit.canonical-generation-resolution.v1',label+' resolution schema')
            self.check(pointer['schema']=='implementaudit.current-generation.v1',label+' pointer schema')
            self.check(generation==label==pointer['continuity_epoch'] and label in {'G0002','G0003'},label+' selected generation')
            self.check(resolved['controller']==pointer['controller']==original.CONTROLLER,label+' controller identity')
            for key in ('claim_id','run_root_identity'):
                self.check(resolved[key]==pointer[key],label+' resolved '+key+' identity')
            self.check(pointer['run_root_identity']==self.run.relative_to(self.repo).as_posix(),label+' physical run identity')
            manifest_path=self.run/'state-generations'/generation/'archive-manifest.json'
            self.check(Path(resolved['archive_manifest_path'])==manifest_path,label+' exact manifest path')
            resolved_raw=manifest_path.read_bytes()
            self.check(hashlib.sha256(resolved_raw).hexdigest()==pointer['archive_manifest_sha256'],label+' manifest pointer digest')
            manifest=json.loads(resolved_raw)
            self.check(manifest['schema']=='implementaudit.state-archive.v1',label+' archive schema')
            self.check(manifest['preparation_generation_id']==generation,label+' archive generation')
            for key in ('controller','claim_id','run_root_identity'):
                self.check(manifest[key]==pointer[key]==manifest['predecessor'][key],label+' archive '+key+' identity')
            predecessor=manifest['predecessor']
            self.check(predecessor['receipt_ref']+'@'+predecessor['receipt_oid']==pointer['predecessor_receipt_ref_oid'],label+' archive predecessor receipt')
            # Original rotate-canonical-state._identity owns this exact ref role;
            # archive_ref is not a field of the current-generation pointer.
            ref='refs/implementaudit/state-archives/'+pointer['controller']+'/'+generation
            oid=self.git('rev-parse',ref)
            raw=original.command(['git','cat-file','blob',oid],self.repo)
            self.observed(label+' archive read',raw,True)
            self.check(raw.stdout==resolved_raw,label+' exact resolved manifest readback')
            self.check(identity(raw.stdout)['git_blob']==oid,label+' manifest object identity')
            objects={}
            for row in manifest['entries']:
                got=original.command(['git','cat-file','blob',row['blob_oid']],self.repo)
                self.observed(label+' archive member '+row['artifact_id'],got,True)
                objects[row['blob_oid']]=got.stdout
            received=archive_canary_binding(manifest,objects)
            item={'label':label,'ref':ref,'oid':oid,'token':ref+'@'+oid,
                  'manifest':self.store_content(raw.stdout),'canary_binding':received,
                  'members':[{**row,'retained_bytes':self.store_content(objects[row['blob_oid']])} for row in manifest['entries']]}
            self.a3['archives'].append(item)
            return item

        def retain_final(self):
            set_phase('final-retention')
            self.snapshot('final-retained-fixture')
            paths=[]
            for folder in (self.repo/'.git/objects',self.repo/'.git/refs',self.run):
                paths.extend(p for p in folder.rglob('*') if p.is_file() and not p.is_symlink())
            for folder in self.repo.glob('a3-read-*'):
                paths.extend(p for p in folder.rglob('*') if p.is_file() and not p.is_symlink())
            paths.extend(p for p in (self.repo/'.git/HEAD',self.repo/'.git/config',self.repo/'.git/packed-refs') if p.is_file())
            archive=evidence_root/'original-a3-full-conjunction.fixture.zip'
            with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as target:
                for path in sorted(set(paths)):target.write(path,path.relative_to(self.repo).as_posix())
            with zipfile.ZipFile(archive) as target:
                self.assertIsNone(target.testzip());self.assertEqual(len(target.namelist()),len(set(target.namelist())))
            self.a3.update(retained_fixture={'name':archive.name,**identity(archive.read_bytes())},
                source_identity={p.name:identity(p.read_bytes()) for p in sorted(self.scripts.iterdir()) if p.is_file()},
                fixture_repository=str(self.repo),fixture_run_root=str(self.run),
                final_refs=self.refs(),award=None)
            write_new(evidence_root/'original-a3-full-conjunction.json',canonical(self.a3))

        def test_complete_archive_isolation(self):
            set_phase('real-G0002-construction')
            first=self.make_real_generation(native=True,extra_artifacts={CANARY_PATH:CANARY})
            self.a3['first_resolution']=first
            self.check(first['pointer']['continuity_epoch']=='G0002','original factory published actual G0002')
            self.check(not (self.run/MISSING_CAPTURE).exists(),'missing historical capture really absent')
            archive2=self.actual_archive('G0002',first)
            self.current_views('G0002-archive-canary-excluded',first)

            set_phase('same-bytes-current-phase-adversary')
            phase=self.run/'phases/phase-999.md'
            self.check(not phase.exists(),'current phase canary destination initially absent')
            before=self.refs();write_new(phase,CANARY)
            try:
                self.snapshot('identical-canary-in-current-phase-population')
                rejected=self.validate()
                self.observed('identical canary in current phase population',rejected,False,
                    b'DONE phase phase-999.md declared capture is missing:')
                self.check(self.refs()==before,'recursive validator refusal does not alter authority refs')
            finally:
                phase.unlink()
            self.check((self.run/CANARY_PATH).read_bytes()==CANARY,'archived-origin canary unchanged after negative control')
            self.observed('validator after removal of only new current-phase stimulus',self.validate(),True)
            self.snapshot('current-phase-adversary-removed')

            set_phase('declared-fixture-manual-resume')
            event=self.claim('--invalidate-continuity',original.CONTROLLER,'--boundary','manual-resume',
                             '--event','prospective-A3-disposable-fixture-boundary')
            self.observed('declared fixture invalidation',event,True)
            pending_result=self.claim('--resolve-resume-generation',original.CONTROLLER)
            self.observed('exact pending resume source',pending_result,True)
            pending=json.loads(pending_result.stdout);self.a3['pending_source']=pending
            self.check(pending['pointer_token']==first['pointer_token'],'pending source binds exact actual G0002 pointer')
            self.check(pending['invalidation_token']==event.stdout.decode().strip(),'pending source binds actual new invalidation')
            self.check(pending['next_continuity_epoch']=='G0003','next epoch actually selected as G0003')
            self.observed('pending boundary refuses currentness',self.claim('--require-current-continuity',original.CONTROLLER),False)
            self.snapshot('pending-boundary-no-current-generation')
            resumed=self.claim('--resume-controller',original.CONTROLLER,'--boundary','manual-resume','--epoch',pending['next_continuity_epoch'],
                '--expected-pointer',pending['pointer_token'],'--expected-invalidation',pending['invalidation_token'])
            self.observed('actual G0003 owner resume',resumed,True)
            resolved_result=self.claim('--resolve-canonical-generation',original.CONTROLLER)
            self.observed('actual G0003 resolution',resolved_result,True)
            second=json.loads(resolved_result.stdout);self.a3['second_resolution']=second
            self.check(second['receipt_token']==resumed.stdout.decode().strip(),'G0003 receipt is the actual owner return')
            self.check(second['pointer_token']!=first['pointer_token'],'actual new current pointer differs')
            self.check(second['marker_oid']==first['marker_oid'],'permanent original marker unchanged')
            for role in ('STATE','ROADMAP'):
                self.check(Path(first[role.lower()+'_path']).is_file() and Path(second[role.lower()+'_path']).is_file(),role+' old and new physical projections coexist')
            archive3=self.actual_archive('G0003',second)
            self.current_views('G0003-only-current',second)

            set_phase('old-and-archive-tokens-refused')
            before=self.refs()
            for label,token in [('old-G0002',first['pointer_token']),('archive-G0002',archive2['token']),('archive-G0003',archive3['token'])]:
                for role in ('STATE','ROADMAP'):
                    self.observed(label+' cannot read current '+role,
                        self.claim('--read-canonical-state',original.CONTROLLER,'--role',role,'--expected-pointer',token),False,
                        b'current pointer changed between separate reads')
            self.observed('old G0002 receipt not current',self.claim('--verify-resume-receipt',first['receipt_token']),False,
                          b'receipt does not name the current generation')
            self.observed('actual G0003 receipt is current',self.claim('--verify-resume-receipt',second['receipt_token']),True)
            current=self.claim('--require-current-continuity',original.CONTROLLER)
            self.observed('sole current receipt is actual G0003',current,True)
            self.check(current.stdout.decode().strip()==second['receipt_token'],'only actual G0003 receipt selected')
            self.check(self.refs()==before,'old/archive token refusals preserve all authority refs')
            self.snapshot('old-and-archive-tokens-refused')

            set_phase('automatic-discovery-without-live-pointer')
            before=self.refs()
            pointer_ref,pointer_oid=second['pointer_token'].split('@')
            self.git('update-ref','-d',pointer_ref,pointer_oid)
            try:
                self.snapshot('live-pointer-absent-archive-not-current')
                self.observed('absent live pointer cannot resolve archives as current',
                    self.claim('--resolve-canonical-generation',original.CONTROLLER),False)
                self.observed('absent live pointer cannot admit archived or old receipt currentness',
                    self.claim('--require-current-continuity',original.CONTROLLER),False)
                self.output=self.repo/'a3-read-absent-live-pointer';self.output.mkdir()
                self.observed('automatic reader does not discover archive as live',self.read('--native-guards'),False)
                self.check(not list(self.output.iterdir()),'refused automatic reader publishes no live pair')
                self.observed('validator cannot fall back to archive or retired root',self.validate(),False,
                    b'canonical pair selection refused; root compatibility fallback is forbidden')
            finally:
                self.git('update-ref',pointer_ref,pointer_oid,'0'*40)
            self.check(self.refs()==before,'exact live pointer restored with expected-absent CAS and no other authority change')
            self.observed('currentness after exact fixture pointer restoration',
                self.claim('--verify-resume-receipt',second['receipt_token']),True)

            set_phase('retired-root-poison')
            saved={role:((self.run/(role+'.md')).read_bytes(),stat.S_IMODE((self.run/(role+'.md')).stat().st_mode)) for role in ('STATE','ROADMAP')}
            try:
                for role in ('STATE','ROADMAP'):
                    path=self.run/(role+'.md');path.chmod(0o600)
                    path.write_bytes(('# Deliberately invalid retired '+role+' compatibility bytes\nNo live epoch or valid native guards.\n').encode())
                self.snapshot('retired-root-pair-poisoned')
                self.current_views('G0003-despite-retired-root-poison',second)
            finally:
                for role,(raw,mode) in saved.items():
                    path=self.run/(role+'.md');path.write_bytes(raw);path.chmod(mode)
            self.check(all((self.run/(role+'.md')).read_bytes()==raw for role,(raw,_) in saved.items()),'retired compatibility pair restored exactly after discriminator')
            self.observed('final original validator',self.validate(),True)
            self.check(not phase.exists() and not (self.run/MISSING_CAPTURE).exists(),'only declared temporary phase stimulus removed; no missing history capture invented')
            self.check(self.git('rev-parse',archive2['ref'])==archive2['oid'] and self.git('rev-parse',archive3['ref'])==archive3['oid'],
                       'both original archive anchors survive all probes')
            self.a3['method_completed']=True

    return ProspectiveA3ArchiveIsolation
