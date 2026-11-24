import hashlib, json, subprocess
from pathlib import Path
Q = 'qualification/dg16-r5-full-g2'
WF = '.github/workflows/dg16-r5-full-g2.yml'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
size = lambda p: Path(p).stat().st_size


def diff(a, b, n=0):
    return subprocess.run(['git', 'diff', '--no-index', '-U%d' % n, '--', a, b],
                          capture_output=True, text=True, encoding='utf8').stdout.rstrip()


chain = json.load(open('tools/chain.json'))
L = []
w = L.append
w('# DELTA: rebound V03-only packet (2e72a912) vs frozen 3c22642a packet')
w('')
w('- Predecessor: `3c22642a:qualification/dg16-r5-full-g2/`, its workflow and decisions dir (copied unmodified to `orig/`).')
w('- Target source: `2e72a912136607e464e953c71fc8e2b44d047d92`, tree `192970f5103fc46d3c303a93d775eb83c04d2734`.')
w('- Branch: `engineering/opus-dg16-v03-2e72-20261124`; control branch: `engineering/opus-dg16-v03-2e72-20261124-control`.')
w('- Status: engineering proposal only. No push, no hosted run; run.py and pair_driver were not executed. Authority NONE.')
w('')
w('## Chained digests (bottom-up)')
w('')
w('| constant | value |')
w('|---|---|')
for k, v in chain.items():
    if not k.startswith('file:'):
        w('| %s | `%s` |' % (k, v))
w('')
w('| file | predecessor sha256 | rebound sha256 |')
w('|---|---|---|')
for p in sorted(Path(Q).iterdir()):
    o = Path('orig') / Q / p.name
    w('| %s | `%s` | `%s` |' % (p.name, sha(o) if o.exists() else '(new)', sha(p)))
w('| %s | `%s` | `%s` |' % (WF, sha('orig/' + WF), sha(WF)))
w('')
w('Byte-identical to the predecessor: finite_relation.py, full_output_relation.py, full_stdout.py, full_evidence.py, '
  'pending_relation.py, policy_control.py, host_utility.py.')
w('')
w('## (i) Identity and pin rebinding')
w('')
for name in ('capture_evidence.py', 'checkout_prepare.py', 'live_control.py', 'pair_diagnostics.py', 'pair_driver.py',
             'full_relation.py', 'RELATION_INPUTS.json', 'POLICY.json'):
    w('### ' + name)
    w('')
    w('```diff')
    w(diff('orig/%s/%s' % (Q, name), '%s/%s' % (Q, name)))
    w('```')
    w('')
w('full_relation.py: every hunk is a pin (REGISTRY_SHA, COMMAND_SHA, REPORT_PROFILE_SHA, 2094 to 2113) except line 61. '
  'Line 61 is RELATION_INPUT_BOUND, raised from `1024**2` to `2 * 1024**2`; see (iv).')
w('')
w('The workflow identity hunks are shown in full under (iii): the branch filter, the `github.ref` guard, the source checkout '
  '`ref`, the parent check, and the adapter digest repeated in every step. run.py pins are in the same run.py diff: '
  'BRANCH, SOURCE_COMMIT/TREE, MANIFEST_SHA, PAIR_DRIVER_SHA, DIAGNOSTICS_SHA, FULL_RELATION_SHA, RELATION_INPUTS_SHA, '
  'POLICY_SHA, LIVE_CONTROL_SHA, CHECKOUT_PREPARE_SHA, CAPTURE_EVIDENCE_SHA, and the manifest counts 1785/168345951 to 1972/173715501.')
w('')
w('## (ii) Regenerated data')
w('')
w('| file | predecessor | rebound | bytes | method and reproduction control |')
w('|---|---|---|---|---|')
w('| SOURCE_MANIFEST.json | `4f4e8f18…` | `%s` | %d | `tools/source_manifest.py`: every blob of `git ls-tree -r` (all modes 100644/100755) sorted by path, '
  '`json.dumps(sort_keys=True, indent=2)+"\\n"`. Control: it reproduces the 51416 file 4f4e8f18… byte for byte. 2e72 has 1972 files and 173,715,501 bytes. |'
  % (sha(Q + '/SOURCE_MANIFEST.json'), size(Q + '/SOURCE_MANIFEST.json')))
w('| CAPTURE_DIAGNOSTIC_CATALOG.json | `d8eeaa1a…` | `%s` | %d | `tools/catalog_rebind.py`, predecessor-catalog rebinding. Control: rebinding the '
  'd2f04874 catalog (source e91df006) to 51416 reproduces d8eeaa1a… byte for byte. |'
  % (sha(Q + '/CAPTURE_DIAGNOSTIC_CATALOG.json'), size(Q + '/CAPTURE_DIAGNOSTIC_CATALOG.json')))
w('| REPORT_SLOTS.json | `9359dd45…` | `%s` | %d | Supplied by `v03regen/regen.py`, which has its own byte-reproduction control. 112 slots, 2113 tests. |'
  % (sha(Q + '/REPORT_SLOTS.json'), size(Q + '/REPORT_SLOTS.json')))
w('| OUTPUT_ROLES.json | `8bf5fe91…` | `%s` | %d | Supplied by `v03regen/regen.py`. |'
  % (sha(Q + '/OUTPUT_ROLES.json'), size(Q + '/OUTPUT_ROLES.json')))
w('')
w('Catalog rebinding rule, derived from the d2f04874→51416 history:')
w('')
w('- **files:** every tracked `.py`/`.sh` except the predecessor exclusions (predecessor tree minus predecessor catalog: 4 historical files). '
  'Surviving files keep their id. New files are appended in path order. 2e72 has 573 files (+44).')
w('- **literals and prefixes:** the predecessor sha256/bytes are kept. A reference survives only on an exactly unchanged line, found with difflib '
  '`SequenceMatcher(autojunk=False)` over the predecessor→target lines, and it is remapped to the target line number. '
  '2e72: 1444 literals, 83 prefixes, 2 references dropped, no new literal patterns.')
w('- **tests:** sha256 of each `printed_identity` with `[slot, index]` references. Surviving ids are kept and gaps stay. '
  'New ids are appended from the predecessor count. 2e72 has 2097 identities.')
w('- **owner frames:** recomputed from the 2e72 owner code objects (`co_qualname`, `co_firstlineno`, last `co_lines`). Unchanged at 1545–2074.')
w('- **other fields:** owner_sha256 is e84ab863…; source commit/tree and report_slots_sha256 (ed2a62ec…) are rebound.')
w('- **Success path:** the catalog is required. pair_driver calls `load_catalog`/`compiled_owner`/`admit_owner` before either leg.')
w('')
w('COMMAND_SHA, mapped_nodes and registered_tests come from `tools/command_stream.py`. It repeats the pair_driver MAPPING phase: '
  '`verifier_registered_tests_v1`, `environment_identity(child_resolution=True)`, `compile_verifier_graph_v1` and '
  '`verifier_command_stream_v1`. It ran under WSL python3.12 on `git archive` copies in `/home/agent/opus-tmp/v03c`, '
  'with `env -i`, and the registry was not run.')
w('')
w('- Control on 51416: `50a794c8…`, 119 nodes, 91 tests.')
w('- 2e72: `de2ef1f15fd8e115cc61523feafd87e42a353ce277861ab2d08d0c033b8b950d` (49,666 bytes), 119 nodes, 91 tests. '
  'Registered equals physical and registry reassembly is exact.')
w('')
w('## (iii) Gate change and step removal')
w('')
w('Root decision 2 is implemented in `require_native_for_pair`. The function is kept, along with its reaped-children check '
  '(new code `PAIR_PRECONDITION_STEP_CHILDREN_NOT_REAPED`) and its `BANK_SECONDS+PAIR_RECEIVING_RESERVE` receiving-time check. '
  'Only the native `verify_current`/`projection` calls are removed.')
w('')
w('Removed because the route has no native files:')
w('')
w('- STEPS `native-bank`/`native-receive` and their two workflow steps.')
w('- `load_native`, `actual_native_adoption`, `prerequisite_host` and `native_closure_applicability`.')
w('- The nine-case bank program (`TESTS`/`CHILD`/`validate_bank`/`retain_bank_capture`) and `KNOWN_CODES`/`EXCEPTIONS`, which only it used.')
w('- `new_native_state`, `native_requirement`, `native_commands_summary`, `native_receipt`, `native_projection` and `native_operation`.')
w('- The native calls in `inventory` (profile `credentials`/`validate_host`), `observe_host`, `emit_bound_public`, '
  '`failed_leg_public_budget`, provision, finalize and the per-step projection.')
w('- The native, prerequisite and current-host pins, plus their workflow `paths` entries.')
w('')
w('Kept unchanged:')
w('')
w('- Live review: `prepare-review`, `hold` and live_control.')
w('- Closing readback: `finalize`, `closing_control_readback`, `pair_driver --recheck` and closing currentness.')
w('')
w('### run.py')
w('')
w('```diff')
w(diff('orig/%s/run.py' % Q, '%s/run.py' % Q))
w('```')
w('')
w('### workflow')
w('')
w('```diff')
w(diff('orig/' + WF, WF))
w('```')
w('')
w('## (iv) Items needing an explicit Root decision')
w('')
w('1. **REPORT_SLOTS size admission** (full_relation.py `load`). Superseded by the correction in (v). The general bound is back at 1 MiB, '
  'and only REPORT_SLOTS.json is admitted, at its exact pinned 1,083,198 bytes, under a 2 MiB ceiling. It grew because source_closure '
  'went from 979 to 1166 entries, 142 of them `handoff/sol-dg1{6,7}-20261122/**`.')
w('2. **POLICY.json.** In rule `unittest_report_diagnostic_elapsed`, only the count token changed (`2094`→`2113`). '
  'The top-level `author` is still the original rule author. `successor_rebinding` records `rebinding_author` /root/opus_dg16, '
  '`delegated_builder` /root/opus_dg16_subagent and the count provenance; see (v).')
w('3. **The decisions dir is empty on purpose.** An independent reviewer and Root must author `INDEPENDENT_COLD_REVIEW.json` and '
  '`ROOT_POLICY_ADOPTION.json`, bound to adapter `%s`, pair_driver `%s`, policy `%s` and receiver_inputs `%s`. Until then '
  '`actual_policy_adoption` refuses at provision. They were not fabricated.'
  % (chain['ADAPTER_SHA'], chain['PAIR_DRIVER_SHA'], chain['POLICY_SHA'], chain['RELATION_INPUTS_SHA']))
w('4. **Workflow parent check:** the packet commit must have exactly one parent, 2e72a912.')
w('5. **POLICY guard text:** it still says that a different candidate "requires fresh explicit source applicability"; Root must evaluate that for 2e72.')
w('')
w('## (v) Correction after Root review of d2303ee9')
w('')
w('1. **Root identity.** The predecessor literal `PRO-EXECUTOR-01, designated by owner` is replaced by `Astra Root` in the pre-run '
  'adoption consumer (policy_control.py `validate`, `successor`) and in the live control/consumption consumer (live_control.py '
  '`validate`, both CONTROL.json and ROOT_CONSUMPTION.json `successor`). The `/root` decision-author format is unchanged.')
w('2. **Author exclusions.** `CURRENT_AUTHORS` in policy_control.py and live_control.py, the only author-exclusion sites in the '
  'V03 route, keep all 15 original identities and add `/root/opus_dg16` (rebinding author) and `/root/opus_dg16_subagent` '
  '(delegated builder). Both reviewer checks refuse every one of the 17 identities.')
w('3. **POLICY.json.** `author` is the original rule author. `successor_rebinding` now separates `rule_author`, `rebinding_author`, '
  '`delegated_builder` and `count_provenance` ("measured slot population of REPORT_SLOTS ed2a62ec on 2e72a912 by regenerator acdcbeae"). '
  'The ambiguous `by` member is removed.')
w('4. **Size bound.** RELATION_INPUT_BOUND is 1 MiB again for every input. REPORT_SLOTS.json alone is admitted before reading, and only '
  'when the pinned `REPORT_PROFILE_BYTES` (1,083,198), the RELATION_INPUTS declared size and the `lstat` size all match, under '
  '`REPORT_PROFILE_CEILING` (2 MiB). The existing digest check and post-read identity checks are unchanged.')
w('')
w('### full_relation.py (load hunk, vs predecessor)')
w('')
w('```diff')
fr = diff('orig/%s/full_relation.py' % Q, '%s/full_relation.py' % Q, 1)
w('\n'.join(line for line in fr.split('\n')[:40]))
w('```')
w('')
for name in ('policy_control.py', 'live_control.py'):
    w('### %s (vs predecessor)' % name)
    w('')
    w('```diff')
    w(diff('orig/%s/%s' % (Q, name), '%s/%s' % (Q, name)))
    w('```')
    w('')
w('### POLICY.json successor_rebinding')
w('')
w('```json')
w(json.dumps(json.load(open(Q + '/POLICY.json'))['successor_rebinding'], indent=2, sort_keys=True))
w('```')
w('')
w('### Refreshed digests')
w('')
w('| artifact | sha256 |')
w('|---|---|')
for label, key in (('adapter (run.py)', 'ADAPTER_SHA'), ('pair_driver.py', 'PAIR_DRIVER_SHA'), ('POLICY.json', 'POLICY_SHA'),
                   ('RELATION_INPUTS.json (receiver_inputs)', 'RELATION_INPUTS_SHA'), ('full_relation.py', 'FULL_RELATION_SHA'),
                   ('workflow', 'WORKFLOW_SHA')):
    w('| %s | `%s` |' % (label, chain[key]))
w('| policy_control.py | `%s` |' % chain['file:policy_control.py'])
w('| live_control.py | `%s` |' % chain['file:live_control.py'])
w('')
w('RELATION_INPUTS is unchanged at 4dfea8a5… because it pins the five rule modules and three data files, not full_relation.py itself.')
w('')
w('**Added static checks (all pass):**')
w('')
w('- (a) No consumer contains `PRO-EXECUTOR-01`.')
w('- (b) Synthetic decisions are checked against `policy_control.validate` and `live_control.validate`. A non-author reviewer is accepted; '
  'each of the 17 CURRENT_AUTHORS reviewers is refused (`EXACT_INDEPENDENT_CODE_REVIEW_REQUIRED` / `ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED`); '
  'and the predecessor successor literal is refused.')
w('- (c) Run in scratch copies: REPORT_SLOTS at 1,083,199 and 1,083,197 bytes is refused (`RELATION_INPUT_BOUND`), and so is each of the '
  'other 7 inputs at 1 MiB + 1. At exactly 1 MiB they pass the bound.')
w('')
w('## Files dropped from the packet (not loaded by the V03 route)')
w('')
w('- **Native:** native_admission.py, native_integration.py, native_prerequisite.py, native_probe.py, native_profile.py, current_host.py, '
  'evidence_io.py (loaded only by `load_native`), EARNED_NATIVE_PREREQUISITE_04.json, NATIVE_SOURCE_APPLICABILITY.json and '
  'UNCHANGED_BANK_SOURCE_CLOSURE.json. Decisions: CURRENT_HOST_QUALIFICATION_REQUEST.json, NATIVE_INDEPENDENT_REVIEW.json and '
  'ROOT_NATIVE_APPLICABILITY_ADOPTION.json.')
w('- **Protected/private** (205aeab7 lane; never referenced by run.py or the workflow): protected_bridge.py, protected_preflight.py, '
  'bound_child.py, fs_carrier.py, fs_command.py, fs_io.py, fs_protocol.py, fs_runner.py, fs_transport.py, full_g2_hooks.py, '
  'test_stream_diagnostics.py, PROTECTED_RECIPIENT.json/.pem and UNISSUED_REQUIREMENTS.json.')
w('- **Predecessor decisions:** INDEPENDENT_COLD_REVIEW.json and ROOT_POLICY_ADOPTION.json are bound to 51416 and must be re-issued.')
w('')
w('## Remaining dependencies on native/protected/private inputs')
w('')
w('**None in any code path.** A grep of run.py for native, current_host, prerequisite and protected finds only inert strings:')
w('')
w('- schema/label strings: `dg16.linux-native-source-manifest.v2`, `dg16.linux-native-private-episode.v1`, `DG16_LINUX_NATIVE_EPISODE`;')
w('- setup_sudo comments and scope string;')
w('- the function name `require_native_for_pair`, kept per Root;')
w('- two pre-existing null placeholders: `PROBE.protected_capability: None` and `FAILURE.protected_streams: None`.')
w('')
w('`host_utility.public_codec` keeps an optional compaction branch that fires only when `native_prerequisite` is present, and it is never set. '
  'The relation modules mention `source-peers/native-runtime` only as source paths and data.')
w('')
w('These ordinary host requirements are inherited:')
w('')
w('- ubuntu-26.04, x86_64, trusted bwrap/bash/python3/git;')
w('- unittest.runner 3.14.4 with sha `51780085…`;')
w('- apt python3-venv/ripgrep/nodejs and zopfli 0.2.3.post1;')
w('- read access to the control branch for the live review.')
w('')
w('## Static verification')
w('')
w('`tools/static_verify.py` reads files and loads only the full_relation, capture_evidence and owner modules. It ran under WSL '
  'against a 2e72 archive copy and printed **ALL_PASS**. It checked:')
w('')
w('- every run.py and pair_driver pin equals its file hash;')
w('- owner and compiler pins, and the workflow adapter digest and ref;')
w('- canonical encoding of POLICY and RELATION_INPUTS;')
w('- `full_relation.load`, and `source_profiles` with 1173 closure/role pins equal to the actual 2e72 bytes;')
w('- capture_evidence `load_catalog`/`compiled_owner`/`admit_owner` against the e84ab863 owner;')
w('- the manifest equals the source file population.')
w('')
w('Control: on the original packet against 51416, every check passes except the deliberate "no 51416 in workflow" check.')
w('')
w('UNKNOWN until a hosted run: the actual 49 portal / 19 repro populations, the pending control lists and stdout role populations. '
  'Their producers (portal-event-capture.py, repro-event-capture.py, cognition-pending-*.py) are byte-identical from 51416 to 2e72.')
Path('DELTA.md').write_bytes(('\n'.join(L) + '\n').encode('utf8'))
print('lines', len(L))
