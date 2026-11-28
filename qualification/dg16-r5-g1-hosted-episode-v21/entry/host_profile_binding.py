"""Conditional D4 producer, proposed for Root's prospective-profile decision.

This is not the legacy post-observation same-host tool adoption. It matches a
fresh observation to an already issued, separately authenticated Root policy.
The trusted policy descriptor is supplied only by the pinned prepare entry;
the policy file cannot nominate its own trusted hash. None keeps D4 refused.

No command, network, carrier, extra hold, grant or award is produced here.
The caller must retain both returned bodies before its first prepare effect.
"""
import hashlib
import json
import os
import re
import time

HELD = 'PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE'
MAX_BODY = 65536
SOURCE_COMMIT = 'd208cb84a9d69ad03709de6102f1adde3cf3df7f'
SOURCE_TREE = '8ba23825751d374c6e343485d9ff1a9e0401e75a'


def _need(ok, code):
    if not ok:
        raise ValueError(code)


def _encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def _descriptor(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _need(key not in result, 'D4_POLICY_JSON')
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError('D4_POLICY_JSON')
    try:
        value = json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)
        _need(_encode(value) == raw, 'D4_POLICY_JSON')
    except (UnicodeError, TypeError, json.JSONDecodeError):
        raise ValueError('D4_POLICY_JSON') from None
    return value


def _policy(raw, trusted_pin, owner, now_ms):
    _need(type(trusted_pin) is dict and set(trusted_pin) == {'bytes', 'sha256'}
          and type(trusted_pin['bytes']) is int and 0 < trusted_pin['bytes'] <= MAX_BODY
          and type(trusted_pin['sha256']) is str
          and re.fullmatch('[0-9a-f]{64}', trusted_pin['sha256']), 'D4_POLICY_PIN')
    _need(type(raw) is bytes and _descriptor(raw) == trusted_pin, 'D4_POLICY_PIN')
    value = _parse(raw)
    fields = {'schema', 'issuer', 'successor', 'decision', 'semantics', 'source_commit', 'source_tree',
              'operation', 'finite_host_policy_sha256', 'profile_ids', 'issued_unix_ms', 'expires_unix_ms',
              'core_or_native_effect_grant', 'original_awards'}
    _need(type(value) is dict and set(value) == fields, 'D4_POLICY_SCOPE')
    _need(value['schema'] == 'dg16.g1-prospective-host-profile-policy.v2'
          and value['issuer'] == 'R5_ROOT_GOVERNOR'
          and value['successor'] == 'owner-appointed continuing Root dg16-dg17-successor-20261127'
          and value['decision'] == 'ADOPT_FINITE_EXACT_PROFILES_CONDITIONALLY'
          and value['semantics'] == 'PROSPECTIVE_PROFILE_MATCH_BEFORE_PREPARE'
          and value['core_or_native_effect_grant'] is False and value['original_awards'] == [],
          'D4_POLICY_SCOPE')
    _need(value['source_commit'] == SOURCE_COMMIT and value['source_tree'] == SOURCE_TREE,
          'D4_POLICY_SOURCE')
    _need(type(now_ms) is int and type(value['issued_unix_ms']) is int
          and type(value['expires_unix_ms']) is int
          and 0 <= value['issued_unix_ms'] <= now_ms < value['expires_unix_ms'] <= 10**16,
          'D4_POLICY_TIME')
    _need(value['finite_host_policy_sha256'] == owner.g1_host_policy_sha256()
          and type(value['profile_ids']) is list
          and 0 < len(value['profile_ids']) <= len(owner.G1_HOST_PROFILES)
          and all(type(item) is str for item in value['profile_ids'])
          and value['profile_ids'] == sorted(set(value['profile_ids']))
          and all(sum(row['id'] == item for row in owner.G1_HOST_PROFILES) == 1
                  for item in value['profile_ids']),
          'D4_POLICY_PROFILE')
    return value


def _operation(policy, context):
    value = policy['operation']
    _need(type(value) is dict and set(value) == {'repository', 'branch', 'workflow_path', 'job_name', 'run_attempt'},
          'D4_POLICY_OPERATION')
    _need(value['repository'] == context['repository'] == 'theislampill/IMPLEMENTAUDIT.md'
          and value['branch'] == context['branch']
          and type(value['run_attempt']) is int and value['run_attempt'] == context['run_attempt'] == 1
          and type(value['workflow_path']) is str and type(value['job_name']) is str
          and re.fullmatch(r'\.github/workflows/[A-Za-z0-9][A-Za-z0-9_-]{0,100}\.ya?ml', value['workflow_path'])
          and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,79}', value['job_name'])
          and os.environ.get('GITHUB_JOB') == value['job_name']
          and os.environ.get('GITHUB_WORKFLOW_SHA') == context['workflow_commit']
          and os.environ.get('GITHUB_WORKFLOW_REF') == value['repository'] + '/' + value['workflow_path']
              + '@refs/heads/' + value['branch'], 'D4_POLICY_OPERATION')
    return {key: context[key] for key in ('repository', 'branch', 'run_id', 'run_attempt', 'workflow_commit')} | {
        'workflow_path': value['workflow_path'], 'job_name': value['job_name']}


def _snapshot(core, owner, source, output):
    context = core.host_context(output, source)
    profile = owner.observe_g1_host_profile()
    owner.validate_g1_host_profile(profile)
    boot = core.validate_boot_identity(core.read_boot_identity())
    host = {key: profile['facts'][key] for key in ('uid', 'euid', 'gid', 'egid')}
    host['boot_id'] = boot.decode('ascii').rstrip('\n')
    return dict(context=context, profile=profile, boot=boot, host_identity=host)


def prepare(core, source, output, *, root_policy_pin=None, read_policy=None):
    """Return a verified binding and raw evidence; never create output or run prepare.

    `core` is the exact externally pinned run.py, whose load_module() authenticates
    the unchanged maintained host_utility.py. The pinned caller supplies the Root
    descriptor only after actual issuance/receiving. `read_policy` is the existing
    entry's fixed-checkout, bounded identity/pin reader for its adjacent policy file, outside the core
    packet census. This function cannot issue a policy or select its own pin.
    """
    _need(root_policy_pin is not None, HELD)
    _need(callable(read_policy), 'D4_POLICY_READER_REQUIRED')
    try:
        raw = read_policy()
    except OSError:
        raise ValueError('D4_POLICY_BODY_UNAVAILABLE') from None
    owner = core.load_module('host_utility')
    start_ms = int(time.time() * 1000)
    policy = _policy(raw, root_policy_pin, owner, start_ms)
    first = _snapshot(core, owner, source, output)
    context = _operation(policy, first['context'])
    _need(first['profile']['profile_id'] in policy['profile_ids'], 'D4_PROFILE_NOT_ADOPTED')
    closing = _snapshot(core, owner, source, output)
    _need(closing == first, 'D4_LIVE_OBSERVATION_CHANGED')
    closing_ms = int(time.time() * 1000)
    _need(closing_ms >= start_ms, 'D4_OBSERVATION_CLOCK')
    _policy(raw, root_policy_pin, owner, closing_ms)
    _operation(policy, closing['context'])
    _need(read_policy() == raw, 'D4_POLICY_BODY_CHANGED')
    observation = dict(schema='dg16.g1-prospective-host-profile-observation.v1', authority='NONE',
        semantics='LIVE_MATCH_TO_PREISSUED_ROOT_POLICY', context=context,
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, root_policy=_descriptor(raw),
        host_profile=first['profile'], host_identity=first['host_identity'],
        observed_unix_ms=closing_ms, original_awards=[])
    observation_raw = _encode(observation)
    _need(len(observation_raw) <= MAX_BODY, 'D4_OBSERVATION_BOUND')
    binding = dict(schema='dg16.g1-finite-host-profile-adoption-binding.v1', context=context,
        source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, host_profile=first['profile'],
        host_identity=first['host_identity'], observation=_descriptor(observation_raw), adoption=_descriptor(raw))
    owner.validate_g1_profile_binding(binding, closing['context'], SOURCE_COMMIT, SOURCE_TREE,
        closing['profile'], hashlib.sha256(closing['boot']).hexdigest())
    return dict(binding=binding, evidence=dict(observation=observation_raw, adoption=raw))
