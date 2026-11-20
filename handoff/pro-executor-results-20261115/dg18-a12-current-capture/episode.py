#!/usr/bin/env python3
"""Prospective A12 case body; original runtime is imported only by main execution."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
import traceback
import zlib


def local(name):
    spec = importlib.util.spec_from_file_location('dg18_a12_child_' + name, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module


def loose_body(repo, oid):
    path = Path(repo) / '.git/objects' / oid[:2] / oid[2:]
    if not os.path.lexists(path): return {'present': False, 'oid': oid}
    if not path.is_file() or path.is_symlink(): return {'present': True, 'oid': oid, 'unsafe_type': True}
    raw = path.read_bytes()
    try:
        decoded = zlib.decompress(raw); header, content = decoded.split(b'\0', 1)
        kind, size = header.decode().split(' ', 1)
        return {'present': True, 'oid': oid, 'kind': kind, 'size_matches': int(size) == len(content),
                'identity_matches': hashlib.sha1(decoded).hexdigest() == oid, 'raw': content, 'compressed': raw}
    except (zlib.error, ValueError, UnicodeError) as exc:
        return {'present': True, 'oid': oid, 'decode_error': type(exc).__name__, 'compressed': raw}


def json_safe(value, recorder):
    if value is None or isinstance(value, (str, int, float, bool)): return value
    if isinstance(value, bytes): return {'retained_bytes': recorder.body(value)}
    if isinstance(value, Path): return str(value)
    if isinstance(value, dict): return {str(k): json_safe(v, recorder) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [json_safe(v, recorder) for v in value]
    return {'observed_python_type': type(value).__module__ + '.' + type(value).__name__,
            'not_serialized_as_authority': True}


def record_blob(recorder, snapshot, oid):
    item = snapshot['objects'].get(oid)
    if not item or item.get('kind') != 'blob' or not item.get('identity_matches') or not item.get('size_matches'):
        raise ValueError('observed authority blob does not have exact physical identity')
    return (recorder.root / item['body']['path']).read_bytes()


def publication_violations(before, after, updates, context, recorder):
    """Unchanged state oracle: derives relations from actual ref/object/file bytes."""
    violations = []
    for ref, (new, old) in updates.items():
        if after['refs'].get(ref) != new or before['refs'].get(ref) == new: continue
        try:
            raw = record_blob(recorder, after, new)
            if ref.startswith(context['epoch_ref_prefix']):
                epoch = json.loads(raw); expected = epoch['transition']['invalidation_oid']
                if after['refs'].get(context['invalidation_ref']) != expected:
                    violations.append({'predicate':'EPOCH_VISIBLE_WITHOUT_ITS_INVALIDATION','ref':ref,'oid':new})
            elif ref == context['pointer_ref']:
                pointer = json.loads(raw)
                if after['refs'].get(context['invalidation_ref']) != pointer['invalidation_oid']:
                    violations.append({'predicate':'POINTER_VISIBLE_WITHOUT_ITS_INVALIDATION','ref':ref,'oid':new})
                # Actual owner namespace is supplied in the observation, not guessed.
                epoch_ref = context['epoch_ref_prefix'] + pointer['continuity_epoch']
                if epoch_ref not in after['refs']:
                    violations.append({'predicate':'POINTER_VISIBLE_WITHOUT_ALLOCATED_EPOCH','ref':ref,'oid':new})
                root = Path(context['run_root']).relative_to(context['repo']).as_posix()
                files = {row['path']: row for row in after['files']}
                for name, key in (('STATE.md','state_sha256'),('ROADMAP.md','roadmap_sha256'),
                                  ('protected-state.json','protected_manifest_sha256'),('archive-manifest.json','archive_manifest_sha256')):
                    member = root + '/state-generations/' + pointer['projection_generation_id'] + '/' + name
                    if member not in files or files[member]['body']['sha256'] != pointer[key]:
                        violations.append({'predicate':'POINTER_VISIBLE_WITHOUT_EXACT_PAIR_MEMBER','path':member,'oid':new})
            elif ref.startswith('refs/implementaudit/continuity-receipts/'):
                fields = raw.rstrip(b'\n').decode().split('\t')
                if fields[0] == 'implementaudit.continuity-receipt.v3':
                    if len(fields) != 14:
                        violations.append({'predicate':'RECEIPT_BINDING_FIELD_OMITTED','ref':ref,'fields':len(fields)})
                    elif after['refs'].get(fields[6]) != fields[7]:
                        violations.append({'predicate':'RECEIPT_VISIBLE_BEFORE_EXACT_POINTER','ref':ref,'bound_pointer':fields[7],
                                           'actual_pointer':after['refs'].get(fields[6])})
                    else:
                        pointer = json.loads(record_blob(recorder, after, fields[7]))
                        expected = [fields[0], context['controller'], context['claim_id'], context['run_root_identity'],
                            pointer['continuity_epoch'], pointer['invalidation_oid'], context['pointer_ref'], fields[7],
                            pointer['state_sha256'], pointer['roadmap_sha256'], pointer['protected_manifest_sha256'],
                            pointer['archive_manifest_sha256'], pointer['exact_next_action'], pointer['predecessor_receipt_ref_oid']]
                        if fields != expected:
                            violations.append({'predicate':'RECEIPT_DOES_NOT_BIND_EXACT_POINTER_FIELDS','ref':ref})
            elif ref == context['marker_ref']:
                fields = raw.decode().split('\t')
                if len(fields) != 10 or after['refs'].get(fields[7]) != fields[8]:
                    violations.append({'predicate':'MARKER_WITHOUT_ITS_RECEIPT','ref':ref})
        except (ValueError, KeyError, UnicodeError, IndexError) as exc:
            violations.append({'predicate':'PUBLISHED_AUTHORITY_BODY_INVALID','ref':ref,'error':type(exc).__name__})
    return violations


def oracle(observation):
    """Pure frozen decision over observation data; contains no mutant-id branch."""
    violations = list(observation['violations']); scenario = observation['scenario']
    result = observation.get('operation_result'); error = observation.get('operation_exception')
    current = observation.get('currentness')
    if scenario in {'rotation','recovery'}:
        status, epoch = ('ROTATED','G0002') if scenario == 'rotation' else ('RECOVERED_PRIOR','G0003')
        if not isinstance(result, dict) or result.get('status') != status or result.get('continuity_epoch') != epoch:
            violations.append({'predicate':'VALID_ORIGINAL_TRANSITION_DID_NOT_COMPLETE','expected_status':status,'expected_epoch':epoch})
        if not current or current.get('exit_code') != 0 or not observation.get('separate_consumers_exact'):
            violations.append({'predicate':'CURRENTNESS_AND_SEPARATE_CONSUMERS_NOT_JOINED'})
        if scenario == 'recovery' and not observation['postcas_fault_fired']:
            violations.append({'predicate':'DECLARED_RECOVERY_STIMULUS_NOT_REACHED'})
    elif scenario in {'pointer_conflict','ref_conflict','compensating_conflict'}:
        if not observation.get('stimulus') or observation['stimulus'].get('kind') != 'competing-pointer':
            violations.append({'predicate':'CONFLICT_STIMULUS_NOT_REACHED'})
        if error is None:
            violations.append({'predicate':'CONFLICTING_PUBLICATION_WAS_NOT_REFUSED'})
        if current and current.get('exit_code') == 0:
            violations.append({'predicate':'CONFLICT_WAS_PROMOTED_TO_CURRENTNESS'})
        if scenario == 'compensating_conflict' and not observation['postcas_fault_fired']:
            violations.append({'predicate':'DECLARED_RECOVERY_STIMULUS_NOT_REACHED'})
    elif scenario == 'occupied_epoch':
        if not observation.get('stimulus') or observation['stimulus'].get('kind') != 'occupied-epoch':
            violations.append({'predicate':'OCCUPIED_SLOT_STIMULUS_NOT_REACHED'})
        if error is None: violations.append({'predicate':'OCCUPIED_EPOCH_WAS_NOT_REFUSED'})
    elif scenario == 'blob_clean':
        if error is not None or not observation.get('blob_return_exact') or not observation.get('original_blob_reader_exact'):
            violations.append({'predicate':'VALID_NEW_BLOB_ROUNDTRIP_DID_NOT_COMPLETE'})
    elif scenario == 'blob_corrupt':
        if not observation.get('blob_corruption_fired'):
            violations.append({'predicate':'ON_DISK_CORRUPTION_STIMULUS_NOT_REACHED'})
        if error is None or observation.get('blob_return_exact'):
            violations.append({'predicate':'CORRUPTED_OBJECT_DID_NOT_STOP_WRITER'})
    elif scenario == 'legacy':
        if observation.get('legacy_method_passed') is not True:
            violations.append({'predicate':'UNCHANGED_ORIGINAL_LEGACY_METHOD_FAILED'})
    else:
        raise ValueError('undeclared oracle scenario')
    return {'passed': not violations, 'violations': violations}


def causal_discriminator(gate, observation):
    predicates={row['predicate'] for row in observation['violations']}
    if gate=='invalidation':return 'EPOCH_VISIBLE_WITHOUT_ITS_INVALIDATION' in predicates
    if gate=='fresh_epoch':return observation.get('freshness_refusal') is True
    if gate in {'cas','compensating_cas'}:return 'COMPETING_POINTER_OVERWRITTEN' in predicates
    if gate=='ref_readback':return ('UPDATE_RETURNED_WITHOUT_EXACT_EFFECT_AND_GUARDS' in predicates
                                  or observation.get('ref_before_effect_refusal') is True)
    if gate=='blob_readback':return ('BLOB_WRITER_RETURNED_UNVERIFIED_OBJECT' in predicates
        or (observation.get('blob_original_absence') is True and observation.get('probe_write_effects')==0
            and observation.get('blob_missing_read_refusal') is True))
    if gate=='receipt_binding':return bool(predicates & {'RECEIPT_BINDING_FIELD_OMITTED','RECEIPT_VISIBLE_BEFORE_EXACT_POINTER'})
    return False


def classify(mutant, reached, evaluation, error, finalization_error, cleanup, recording_complete, causal=False):
    if error is not None or finalization_error is not None or evaluation is None or not cleanup or not recording_complete:
        return 'ERROR'
    if mutant:
        return 'UNREACHED' if not reached else 'SURVIVED' if evaluation['passed'] else 'KILLED' if causal else 'UNRESOLVED'
    return 'BASELINE_PASS' if evaluation['passed'] else 'BASELINE_FAIL'


class Episode:
    def __init__(self, case, factory, recorder, capture, catalogue):
        self.case = case; self.factory = factory; self.rec = recorder; self.cap = capture; self.catalogue = catalogue
        self.fixture_case = None; self.owner = None; self.variant = None; self.coverage = {}; self.originals = {}
        self.state = {'scenario':case['scenario'], 'violations':[], 'postcas_fault_fired':False,
                      'blob_corruption_fired':False, 'stimulus':None, 'target_gate_calls':0,
                      'operation_result':None, 'operation_exception':None, 'currentness':None,
                      'separate_consumers_exact':False, 'setup_complete':False}
        self.active_kind = None; self.pending_ref_fault = None; self.probe_raw = None;self.active_update=None

    def snapshot(self, label):
        row = self.rec.snapshot(self.fixture.repo, self.fixture.run_root, label)
        stimulus = self.state.get('stimulus')
        if stimulus and stimulus.get('kind') == 'competing-pointer':
            actual = row['refs'].get(self.context['pointer_ref'])
            if actual != stimulus['oid']:
                self.state['violations'].append({'predicate':'COMPETING_POINTER_OVERWRITTEN',
                    'snapshot':row['index'], 'expected':stimulus['oid'], 'actual':actual})
        return row

    def install_variant(self):
        if not self.case['mutant']: return
        raw = Path(self.owner.__file__).read_bytes()
        self.variant = self.catalogue.build_variant(raw, self.case['mutant'])
        self.cap.write_json(self.rec.root / 'MUTATION.json', self.variant)
        for name, row in self.variant['functions'].items():
            before = self.rec.root / 'source-variant' / (name + '.original.py')
            after = self.rec.root / 'source-variant' / (name + '.mutant.py')
            self.cap.write_new(before, row['before'].encode()); self.cap.write_new(after, row['after'].encode())
            self.cap.write_new(after.with_suffix('.patch'), row['patch'].encode())
            namespace = {}; exec(compile(row['after'], str(after), 'exec'), self.owner.__dict__, namespace)
            self.originals[name] = getattr(self.owner, name); setattr(self.owner, name, namespace[name])
            self.coverage[str(after)] = {'name':name, 'lines':set(), 'calls':0, 'activation_lines':row['activation_lines']}
        def trace(frame, event, arg):
            row = self.coverage.get(frame.f_code.co_filename)
            if row is not None:
                if event == 'call': row['calls'] += 1
                if event == 'line': row['lines'].add(frame.f_lineno)
                return trace
            return None
        sys.settrace(trace)

    def competing_pointer(self, when):
        if self.state['stimulus'] is not None: raise ValueError('stimulus cannot be repeated')
        before = self.snapshot('before-' + when)
        ref = self.context['pointer_ref']; old = before['refs'].get(ref)
        # A real retained G0001 receipt blob is deliberately a distinct incomplete publication.
        conflict = self.fixture.receipt.split('@')[1]
        if old == conflict: raise ValueError('conflict is not distinct')
        self.fixture.git('update-ref', ref, conflict, old or '0' * 40)
        raw = self.rec.snapshot(self.fixture.repo, self.fixture.run_root, 'actual-' + when)
        if raw['refs'].get(ref) != conflict: raise ValueError('competing pointer actual effect not observed')
        self.state['stimulus'] = {'kind':'competing-pointer', 'when':when, 'ref':ref, 'old':old, 'oid':conflict,
            'source':'actual same-subject legacy G0001 receipt blob; intentionally incomplete as a pointer',
            'snapshot':raw['index'], 'valid_complete_winner_claim':False}
        self.rec.event('actual-stimulus', **self.state['stimulus'])

    def install_observers(self):
        owner = self.owner; rec = self.rec; owner._a12_active_transition_kind = None
        selected = {name:getattr(owner,name) for name in ('allocate_epoch','complete_epoch','update_refs','write_blob','git','git_process')}
        original_helper_read = self.fixture_case.helper.read_canonical_generation

        def allocate(context, prepared, observed, **kwargs):
            self.state['target_gate_calls'] += 1 if self.case.get('gate') in {'invalidation','fresh_epoch'} else 0
            if self.case['scenario'] == 'occupied_epoch' and self.state['stimulus'] is None:
                ref = owner.epoch_ref(context, owner.next_epoch(prepared['predecessor']['continuity_epoch']))
                before = self.snapshot('before-occupied-epoch-stimulus')
                if ref in before['refs']: raise ValueError('fresh control slot already occupied before stimulus')
                oid = self.fixture.receipt.split('@')[1]
                self.fixture.git('update-ref', ref, oid, '0' * 40)
                self.state['stimulus'] = {'kind':'occupied-epoch','ref':ref,'oid':oid,
                    'source':'actual retained legacy receipt; occupied slot is deliberately not a valid new epoch'}
                self.rec.event('actual-stimulus', **self.state['stimulus'])
            before = self.snapshot('allocate-entry')
            rec.event('owner-call', function='allocate_epoch', prepared=json_safe(prepared,rec), observed=json_safe(observed,rec), kwargs=json_safe(kwargs,rec))
            try:
                result = selected['allocate_epoch'](context,prepared,observed,**kwargs)
                rec.event('owner-return', function='allocate_epoch', result=json_safe(result,rec)); return result
            except BaseException as exc:
                if str(exc)=='fresh epoch or receipt ref was already allocated':self.state['freshness_refusal']=True
                rec.event('owner-exception', function='allocate_epoch', type=type(exc).__name__, message=str(exc)); raise
            finally:
                after = self.snapshot('allocate-exit')
                if self.case['scenario'] == 'occupied_epoch':
                    new_objects = sorted(set(after['objects']) - set(before['objects']))
                    if new_objects:
                        self.state['violations'].append({'predicate':'OCCUPIED_EPOCH_ADMISSION_WROTE_NEW_AUTHORITY_OBJECTS',
                            'before_snapshot':before['index'],'after_snapshot':after['index'],'new_objects':new_objects})

        def complete(context, record, epoch_oid, **kwargs):
            prior = self.active_kind; self.active_kind = record['transition']['transition_kind']
            owner._a12_active_transition_kind = self.active_kind
            if self.case.get('gate') == 'receipt_binding': self.state['target_gate_calls'] += 1
            rec.event('owner-call', function='complete_epoch', record=json_safe(record,rec), epoch_oid=epoch_oid)
            self.snapshot('complete-entry-' + record['transition']['continuity_epoch'])
            try:
                result = selected['complete_epoch'](context,record,epoch_oid,**kwargs)
                rec.event('owner-return', function='complete_epoch', result=json_safe(result,rec)); return result
            except BaseException as exc:
                rec.event('owner-exception', function='complete_epoch', type=type(exc).__name__, message=str(exc)); raise
            finally:
                self.snapshot('complete-exit-' + record['transition']['continuity_epoch'])
                self.active_kind = prior; owner._a12_active_transition_kind = prior

        def update(context, updates, guards, **kwargs):
            pointer = context['pointer_ref'] in updates
            target_kind = 'recovery' if self.case['scenario'] == 'compensating_conflict' else 'rotation'
            if pointer and self.active_kind == target_kind and self.case.get('gate') in {'cas','compensating_cas','ref_readback'}:
                self.state['target_gate_calls'] += 1
            if pointer and self.active_kind == target_kind and self.state['stimulus'] is None:
                if self.case['scenario'] in {'pointer_conflict','compensating_conflict'}:
                    self.competing_pointer('before-real-pointer-CAS')
                elif self.case['scenario'] == 'ref_conflict': self.pending_ref_fault = dict(updates)
            before = self.snapshot('update-entry')
            call = rec.event('owner-call', function='update_refs', transition_kind=self.active_kind,
                             updates=json_safe(updates,rec), guards=json_safe(guards,rec))
            returned = False;prior_update=self.active_update;self.active_update={'git_transactions':0,'pointer':pointer}
            try:
                result = selected['update_refs'](context,updates,guards,**kwargs); returned = True
                rec.event('owner-return', function='update_refs', call_index=call['index'], result=json_safe(result,rec)); return result
            except BaseException as exc:
                if (pointer and self.active_update['git_transactions']==0
                        and str(exc)=='publication did not have one exact verified effect'
                        and before['refs'].get(context['pointer_ref'])==updates[context['pointer_ref']][1]
                        and updates[context['pointer_ref']][0]!=updates[context['pointer_ref']][1]):
                    self.state['ref_before_effect_refusal']=True
                    rec.event('actual-ref-read-before-effect-refusal',call_index=call['index'],
                        before_snapshot=before['index'],actual_git_transaction_attempts=0,
                        old=updates[context['pointer_ref']][1],requested_new=updates[context['pointer_ref']][0])
                rec.event('owner-exception', function='update_refs', call_index=call['index'], type=type(exc).__name__, message=str(exc)); raise
            finally:
                self.pending_ref_fault = None; after = self.snapshot('update-exit')
                if returned:
                    got = dict(after['refs'], HEAD=after['head'])
                    if any(got.get(ref) != pair[0] for ref,pair in updates.items()) or any(got.get(ref) != oid for ref,oid in guards.items()):
                        self.state['violations'].append({'predicate':'UPDATE_RETURNED_WITHOUT_EXACT_EFFECT_AND_GUARDS',
                            'call_index':call['index'],'after_snapshot':after['index']})
                self.state['violations'].extend(publication_violations(before,after,updates,self.observer_context,rec))
                self.active_update=prior_update

        def write_blob(context, raw):
            if self.case.get('gate') == 'blob_readback' and raw == self.probe_raw: self.state['target_gate_calls'] += 1
            call = rec.event('owner-call', function='write_blob', raw=rec.body(raw))
            try:
                oid = selected['write_blob'](context,raw)
                physical = loose_body(context['repo'],oid)
                exact = (physical.get('kind') == 'blob' and physical.get('identity_matches') and
                         physical.get('size_matches') and physical.get('raw') == raw)
                rec.event('owner-return', function='write_blob', call_index=call['index'], oid=oid,
                          physical=json_safe(physical,rec), exact=bool(exact))
                if not exact:
                    self.state['violations'].append({'predicate':'BLOB_WRITER_RETURNED_UNVERIFIED_OBJECT','call_index':call['index'],'oid':oid})
                return oid
            except BaseException as exc:
                rec.event('owner-exception', function='write_blob', call_index=call['index'], type=type(exc).__name__, message=str(exc)); raise

        def git_call(repo, *args, **kwargs):
            result = selected['git'](repo,*args,**kwargs)
            if args==('hash-object','-w','--stdin') and kwargs.get('input_bytes')==self.probe_raw:
                self.state['probe_write_effects']=self.state.get('probe_write_effects',0)+1
            if (self.case['scenario'] == 'blob_corrupt' and not self.state['blob_corruption_fired']
                    and args == ('hash-object','-w','--stdin') and kwargs.get('input_bytes') == self.probe_raw):
                oid = result.decode().strip(); path = Path(repo)/'.git/objects'/oid[:2]/oid[2:]
                previous, info = self.cap.regular_bytes(path)
                other = self.probe_raw + b'\nA12 declared actual on-disk readback corruption\n'
                corrupt = zlib.compress(b'blob ' + str(len(other)).encode() + b'\0' + other)
                path.chmod(0o644); path.write_bytes(corrupt); path.chmod(info.st_mode & 0o7777)
                actual, _ = self.cap.regular_bytes(path)
                if actual != corrupt: raise ValueError('actual object corruption did not land')
                self.state['blob_corruption_fired'] = True
                rec.event('actual-object-corruption', oid=oid, path=str(path), original=rec.body(previous),
                          actual=rec.body(actual), decoded_actual=rec.body(other), native_failure_claim=False)
            return result

        def git_process(repo, *args, **kwargs):
            if self.active_update is not None and args==('update-ref','--stdin','-z'):
                self.active_update['git_transactions']+=1
            result = selected['git_process'](repo,*args,**kwargs)
            if self.pending_ref_fault is not None and args == ('update-ref','--stdin','-z') and result.returncode == 0:
                self.pending_ref_fault = None
                self.competing_pointer('after-Git-before-owner-ref-readback')
            return result

        def helper_read(repo, run_root, pointer):
            result = original_helper_read(repo,run_root,pointer)
            if self.case['scenario'] in {'recovery','compensating_conflict'} and not self.state['postcas_fault_fired']:
                raw = owner.canonical(pointer); oid = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                if pointer['continuity_epoch'] == 'G0002' and owner.read_ref(repo,self.context['pointer_ref']) == oid:
                    self.state['postcas_fault_fired'] = True
                    self.snapshot('actual-G0002-post-CAS-before-declared-helper-fault')
                    rec.event('declared-post-CAS-helper-fault', pointer_oid=oid, actual_original_read_completed=True,
                              native_failure_claim=False, repeat=False)
                    raise RuntimeError('declared one-shot A12 post-CAS helper failure on disposable subject')
            return result

        owner.allocate_epoch=allocate; owner.complete_epoch=complete; owner.update_refs=update
        owner.write_blob=write_blob; owner.git=git_call; owner.git_process=git_process
        self.fixture_case.helper.read_canonical_generation=helper_read

    def consumers(self):
        self.rec.scope='unchanged-original-CLI-oracle'
        current=self.fixture.claim('--require-current-continuity',self.factory.CONTROLLER)
        self.state['currentness']={'exit_code':current.returncode,'stdout':self.rec.body(current.stdout),'stderr':self.rec.body(current.stderr)}
        result=self.state.get('operation_result')
        if not isinstance(result,dict) or 'pointer_token' not in result or 'receipt_token' not in result: return
        verify=self.fixture.claim('--verify-resume-receipt',result['receipt_token'])
        resolve=self.fixture.claim('--resolve-canonical-generation',self.factory.CONTROLLER)
        rows=[]; exact=current.returncode==0 and current.stdout.decode().strip()==result['receipt_token'] and verify.returncode==0 and resolve.returncode==0
        resolution=None
        if resolve.returncode==0:
            resolution=json.loads(resolve.stdout)
            exact=exact and resolution['pointer_token']==result['pointer_token'] and resolution['receipt_token']==result['receipt_token']
        for role in ('STATE','ROADMAP'):
            response=self.fixture.claim('--read-current-state',self.factory.CONTROLLER,role,'--expected-pointer',result['pointer_token'])
            item={'role':role,'exit_code':response.returncode,'stdout':self.rec.body(response.stdout),'stderr':self.rec.body(response.stderr)}
            if resolution is not None:
                path=Path(resolution[role.lower()+'_path'])
                if not path.is_absolute(): path=self.fixture.repo/path
                expected,info=self.cap.regular_bytes(path);item['actual_file']=self.rec.body(expected)
                exact=exact and response.returncode==0 and response.stdout==expected
            else: exact=False
            rows.append(item)
        self.state['separate_consumers_exact']=bool(exact)
        self.rec.event('original-consumer-join', exact=bool(exact), verify_exit=verify.returncode,
            resolve_exit=resolve.returncode, resolution=json_safe(resolution,self.rec), components=rows)

    def execute(self):
        scenario=self.case['scenario']; legacy=scenario=='legacy'
        if legacy:
            self.fixture_case=self.factory.ReaderControls(self.case['method'])
        else:
            self.fixture_case=self.factory.RealHelperIntegration('test_real_helper_migrates_real_main_receipt_and_separate_readers')
        self.fixture_case.setUp(); self.fixture=self.fixture_case.fixture
        self.state['setup_complete']=True
        self.rec.event('original-setup-complete', repository=str(self.fixture.repo), run_root=str(self.fixture.run_root),
            subject_head=self.fixture.head,subject_tree=self.fixture.tree,legacy_receipt=self.fixture.receipt)
        if legacy:
            self.rec.snapshot(self.fixture.repo,self.fixture.run_root,'legacy-before-original-method')
            self.rec.scope='original-legacy-method'
            getattr(self.fixture_case,self.case['method'])()
            self.state['legacy_method_passed']=True
            self.rec.snapshot(self.fixture.repo,self.fixture.run_root,'legacy-after-original-method')
            return
        self.owner=self.fixture_case.owner; self.context=self.fixture_case.context
        self.observer_context={k:self.context[k] for k in ('controller','claim_id','run_root_identity','pointer_ref','marker_ref','invalidation_ref','repo','run_root')}
        example=self.owner.epoch_ref(self.context,'G0002')
        self.observer_context['epoch_ref_prefix']=example[:-len('G0002')]
        self.rec.event('original-owner-bindings', context=json_safe(self.context,self.rec),
            owner_source=self.cap.digest(Path(self.owner.__file__).read_bytes()),
            helper_source=self.cap.digest(Path(self.fixture_case.helper.__file__).read_bytes()),
            epoch_ref_prefix=self.observer_context['epoch_ref_prefix'])
        self.snapshot('genuine-legacy-G0001-preimage')
        self.install_variant();self.install_observers();self.rec.scope='original-owner-with-declared-variant'
        try:
            if scenario in {'blob_clean','blob_corrupt'}:
                self.probe_raw=self.owner.canonical({'schema':'dg18.a12.disposable-blob-roundtrip.v1',
                    'controller':self.context['controller'],'claim_id':self.context['claim_id'],
                    'purpose':'new authority-write readback stimulus; no live currentness claim'})
                expected_oid=hashlib.sha1(b'blob '+str(len(self.probe_raw)).encode()+b'\0'+self.probe_raw).hexdigest()
                if loose_body(self.fixture.repo,expected_oid)['present']:raise ValueError('new blob stimulus already exists')
                self.state['blob_original_absence']=True;self.state['probe_write_effects']=0
                self.rec.event('new-blob-input',body=self.rec.body(self.probe_raw),expected_oid=expected_oid,original_absence=True)
                oid=self.owner.write_blob(self.context,self.probe_raw)
                self.state['operation_result']={'oid':oid}
                physical=loose_body(self.fixture.repo,oid)
                self.state['blob_return_exact']=bool(physical.get('identity_matches') and physical.get('raw')==self.probe_raw)
                try:
                    actual=self.owner.read_blob(self.fixture.repo,oid)
                    self.state['original_blob_reader_exact']=actual==self.probe_raw
                    self.rec.event('original-blob-reader',oid=oid,returned=self.rec.body(actual))
                except self.owner.RotationError as exc:
                    self.state['original_blob_reader_exact']=False
                    self.rec.event('original-blob-reader-refusal',oid=oid,type=type(exc).__name__,message=str(exc))
            else:
                self.state['operation_result']=self.fixture_case.rotate()
        except self.owner.RotationError as exc:
            self.state['operation_exception']={'type':type(exc).__name__,'message':str(exc),'original_rotation_error':True}
            if isinstance(exc,self.owner.CustodyError):self.state['unrelated_custody_failure']=True
            if str(exc)=='Git operation failed: cat-file':self.state['blob_missing_read_refusal']=True
            self.rec.event('operation-refusal',**self.state['operation_exception'])
        self.snapshot('terminal-owner-effect')
        self.consumers()
        self.snapshot('after-unchanged-CLI-consumers')

    def finish(self):
        sys.settrace(None);failure=None;archive=None;cleanup=False
        case=self.fixture_case
        fixture=getattr(case,'fixture',None) if case is not None else None
        if fixture is not None and fixture.repo.exists():
            try:
                self.rec.snapshot(fixture.repo,fixture.run_root,'final-retained-subject')
                archive=self.cap.archive_tree(fixture.repo,self.rec.root/'FIXTURE.zip')
                self.cap.write_json(self.rec.root/'FIXTURE_INDEX.json',archive)
            except BaseException as exc:
                failure={'type':type(exc).__name__,'message':str(exc),'scope':'fixture-retention'}
        # If retention failed, preserve the surviving fixture for the nonauthoritative finalizer.
        if case is not None and (fixture is None or archive is not None):
            try:
                cleanups_ok=case.doCleanups()
                cleanup=bool(cleanups_ok and fixture is not None and not os.path.lexists(fixture.repo))
            except BaseException as exc:
                failure={'type':type(exc).__name__,'message':str(exc),'scope':'fixture-cleanup'}
        coverage={path:{**row,'lines':sorted(row['lines'])} for path,row in self.coverage.items()}
        self.cap.write_json(self.rec.root/'MUTATION_COVERAGE.json',coverage)
        self.rec.finish()
        return archive,cleanup,failure,coverage


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--case',required=True)
    parser.add_argument('--preflight',type=Path,required=True);args=parser.parse_args()
    capture=local('capture'); catalogue=local('mutations')
    case=next((c for c in catalogue.CASES if c['id']==args.case),None)
    if case is None: raise ValueError('undeclared case')
    source=capture.safe_dir(args.source);output=capture.safe_dir(args.output)
    pre=json.loads(args.preflight.read_bytes())
    if pre.get('product_commit')!=capture.SOURCE_COMMIT or pre.get('cases')!=list(catalogue.CASES) or pre.get('source_path')!=str(source):
        raise ValueError('child lacks exact selected preflight')
    if output!=args.preflight.parent/'cases'/case['id']:raise ValueError('child output differs from declared one-case slot')
    for name in ('capture.py','episode.py','mutations.py'):
        if capture.digest(Path(__file__).with_name(name).read_bytes())!=pre['capture_sources'][name]:
            raise ValueError('child source changed after preflight')
    capture.write_json(output/'CASE_INTENT.json',{**capture.CONTEXT,'case':case,'time_ns':time.time_ns(),
        'preflight':capture.digest(args.preflight.read_bytes()),'source':str(source),'retry':False})
    fixtures=output/'fixtures';fixtures.mkdir(mode=0o700)
    os.environ['R0039_CLAIM_EVIDENCE_DIR']=str(fixtures)
    os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
    recorder=capture.Recorder(output);original_run=subprocess.run;original_popen=subprocess.Popen
    subprocess.run=recorder.run;subprocess.Popen=recorder.popen
    episode=None;error=None;archive=None;cleanup=False;coverage={};finalization_error=None
    try:
        spec=importlib.util.spec_from_file_location('dg18_a12_unchanged_claim_factory',source/capture.ORIGINAL_TEST)
        factory=importlib.util.module_from_spec(spec);sys.modules[spec.name]=factory;spec.loader.exec_module(factory)
        episode=Episode(case,factory,recorder,capture,catalogue);episode.execute()
    except BaseException as exc:
        error={'type':type(exc).__name__,'message':str(exc),'classification':'ERROR_NOT_MUTATION_KILL'}
        traceback.print_exc()
    finally:
        if episode is not None:
            try:archive,cleanup,finalization_error,coverage=episode.finish()
            except BaseException as exc:finalization_error={'type':type(exc).__name__,'message':str(exc),'scope':'case-finalization'}
        else:
            try:recorder.finish()
            except BaseException as exc:finalization_error={'type':type(exc).__name__,'message':str(exc),'scope':'setup-finalization'}
        subprocess.run=original_run;subprocess.Popen=original_popen;sys.settrace(None)
    observation=episode.state if episode is not None else {'scenario':case['scenario'],'violations':[]}
    if observation.get('unrelated_custody_failure'):
        error={'type':'CustodyError','classification':'UNRELATED_CUSTODY_FAILURE_NOT_A_MUTATION_KILL',
               'original':observation.get('operation_exception')}
    evaluation=oracle(observation) if episode is not None and observation.get('setup_complete') and error is None else None
    reached=bool(case['mutant'] and episode is not None and episode.state['target_gate_calls']>0 and coverage and all(
        row['calls']>0 and set(row['activation_lines']) & set(row['lines']) for row in coverage.values()))
    recording=recorder.completeness()
    causal=causal_discriminator(case.get('gate'),observation)
    disposition=classify(case['mutant'],reached,evaluation,error,finalization_error,cleanup,recording['complete'],causal)
    result={**capture.CONTEXT,'case':case,'disposition':disposition,'mutation_reached':reached,
        'observation':observation,'oracle':evaluation,'execution_error':error,'finalization_error':finalization_error,
        'fixture_cleanup_complete':cleanup,'fixture_archive':None if archive is None else {k:v for k,v in archive.items() if k!='members'},
        'command_count':len(recorder.commands),'event_count':len(recorder.events),'snapshot_count':len(recorder.snapshots),
        'recording_completeness':recording,
        'causal_discriminator_established':causal,
        'original_source_was_physically_mutated':False,'award':None}
    capture.write_json(output/'CASE_RESULT.json',result)
    print(json.dumps({'case':case['id'],'disposition':disposition,'mutation_reached':reached,'award':None},sort_keys=True))
    return 0 if disposition in {'BASELINE_PASS','KILLED'} else 1


if __name__=='__main__':
    raise SystemExit(main())
