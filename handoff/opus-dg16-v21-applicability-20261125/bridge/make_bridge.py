"""Emit BRIDGE.json and BRIDGE.md: per-changed-member applicability bridge, V21 vs retained 3e0f4b6d.

Commit lists are read from git (never typed). Classification/coverage text is the author's
analysis (Opus DG16 subagent), submitted for independent review; authority NONE.
usage: python -I make_bridge.py <repo> <outdir> <runs-summary.json>
"""
import hashlib, json, subprocess, sys
from pathlib import Path

repo, outdir, runs_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
RETAINED = '3e0f4b6d05eb086017ce721d40459fdbd68714dd'
HIST = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'
V21 = '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d'
V21_TREE = '53498df783ed441744ae5080982c2d5e59c34bbc'
runs = json.loads(runs_path.read_text())

def git(*a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, check=True, text=True).stdout

def blob(rev, path):
    raw = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{path}'], capture_output=True, check=True).stdout
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())

def commits(path, base=RETAINED):
    out = git('log', '--format=%H%x09%s', f'{base}..{V21}', '--', path).strip().splitlines()
    return [dict(commit=l.split('\t', 1)[0], subject=l.split('\t', 1)[1]) for l in out]

def run(label):
    r = runs[label]
    return f"{label}: rc={r['rc']} stderr_sha256={r['stderr_sha256']}"

SOL17 = 'Sol-DG17 2485bf5270c87026c275c33143a48aee99d4fa40 handoff/sol-dg17-20261122/CONTINUATION.md "Exact V21 joined source and artifact qualification": clean WSL composite-source wrapper rc 0 (85 composite cases, 20 C5 source receiving, 6 original14 history cases), stderr 24235e75815885fd0ec5eb1d8bf8cf8502fb14d01c1de0d60d5e1b0d452e1f73'
SOL18_ROT = 'Sol-DG18 7f954af15fd8958f0fe40a19ce0afd1b086deaaa handoff/astra-dg16-dg18/discussions/DG18-authentic-OR-and-cold-receiving.md "Sol-DG18 ordinary consumer receiving of V21" (Windows Py3.11): RealHelperIntegration.test_real_helper_migrates_real_main_receipt_and_separate_readers rc 0 stderr 0432353ae2901de77b68763b44d6fc52a5c1f56e544d83c22669265254a3e264'
SOL18_READ = 'Sol-DG18 7f954af1 same record: CanonicalReaderTests.test_actual_native_owner_pair_reads_are_ordered_and_token_bound rc 0 stderr 543b42af93a2d2f1cdd6c6382342698da999b790cc4acfef843897ac9ecca612'
SOL18_ARCH = 'Sol-DG18 7f954af1 same record: ArchiveQualification.test_actual_archive_gc_retention_typed_retrieval_and_no_current_authority rc 0 stderr b5916752ba42b16e60848dc22eaf45f0acca2cd1d9174ccbe56b5bba200b21b5'
PIN_OK = 'pin coherence verified: every changed byte/sha256 pin in this member equals the V21 sibling body (git show 338c4c36)'
NATIVE_NOTE = 'No native observation exists at V21 bytes. Historical native receiving bound e76a07b2 (DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1) and retained 3e0f4b6d; neither transfers.'
ROUTE_ABSENT = 'skills/implementaudit/scripts/route-transaction.py is absent at 3e0f4b6d, e76a07b2 and 338c4c36, so _observe_native_run_current_sources_v1 takes the FileNotFoundError branch (route_available=False; ROUTE_PRODUCER_UNAVAILABLE, as the unchanged case test_native_intake_uses_current_original14_not_retired_root expects)'

NATIVE_PATH = ('Linux native path = qualification/dg16-r5-g1-hosted-episode/native_probe.py@b393a905 running the unchanged '
               'tests/work-graph-original14-receiving-cases.py::{test_native_intake_uses_current_original14_not_retired_root,'
               'test_native_intake_later_boundary_prevents_return}; these import only tests/native-work-graph-cases.py (compiler) and '
               'fixtures/canonical-state-rotation/canonical_reader_test.py, which copies skills/implementaudit/scripts and templates into a '
               'constructed repo, runs author_checkpoint.py --activate, claim-run.sh/claim-run-rotation.py/rotate-canonical-state.py rotation, '
               'read-canonical-pair.py --native-guards, and compiler native intake (operational-evidence.py static owner + continuity transport '
               'closure over the 8-file helper tuple), and execs protected_projection_v2_test.py only for render_pair/build_owner_map.')

rows = [
 dict(path='fixtures/canonical-state-rotation/native_input_adapter_test.py',
      change_class='b', status='COVERED',
      change='Test-only: adds test_null_wire_metadata_preserves_exact_usage_without_admitting_bad_metadata and, in test_archive_schema_is_bound_to_exact_window_calibration, admits rotation.NATIVE_INPUT_MODULE_SHA256 among v2 producers plus a live-to-historical calibration retention assertion.',
      reach='Not executed by native_probe (not imported by the two maintained case bodies or canonical_reader_test).',
      controls=['tests/canonical-state-rotation.test.sh:25 runs this file'],
      evidence=[run('canonical-state-rotation')],
      residual='None for the native predicates.'),
 dict(path='fixtures/canonical-state-rotation/native_preparation_test.py',
      change_class='b', status='COVERED',
      change='Test-only: adds OR_SOURCE_TEMPLATE and seven PreparationControls cases (prospective rotation source, selected template live-host gate, C02 capture grant/driver/owned transport, armed owned transport, unselected source refusal); PortableFactoryLoaderControls retargeted.',
      reach='Not executed by native_probe.',
      controls=['tests/canonical-state-rotation.test.sh:29 runs this file'],
      evidence=[run('canonical-state-rotation')],
      residual='None for the native predicates; the OR behaviour these tests control is DG18 scope.'),
 dict(path='fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py',
      change_class='b', status='COVERED',
      change='Fixture copies compaction-prior-protocol.py and compaction-prior-mcp.py into the constructed fixture (e61ead42). V21 bytes equal e76a07b2 and equal the historically admitted repair pin 33227 B / 528f1e693d0745b90a8ea2ededd570962f929e8f2c76b115c6e011386a03e0f7.',
      reach='Not executed by native_probe; this is the single historically admitted fixture repair.',
      controls=['NATIVE_SOURCE_APPLICABILITY.json@b393a905 fixture_repair (retained e166953f..., selected 528f1e69...)', 'native_prerequisite.py@b393a905:181-184 NATIVE_FIXTURE_REPAIR_SCOPE', 'tests/canonical-state-rotation.test.sh:30'],
      evidence=['git show 338c4c36:<path> | sha256sum = 528f1e693d0745b90a8ea2ededd570962f929e8f2c76b115c6e011386a03e0f7 (identical to e76a07b2)', run('canonical-state-rotation')],
      residual='Unchanged from the historical admission, including its declared limits: native_qualification=false, full_pair_consumption=REQUIRED_NOT_EXECUTED.'),
 dict(path='fixtures/canonical-state-rotation/protected_projection_v2_test.py',
      change_class='b', status='COVERED',
      change='Adds subtests in test_accepted_witness_covers_only_exact_observation_and_occurrence_scope and test_physical_source_selected_occurrence_prior_retry_and_refusal_are_protected (53a80108). Top-level AST delta is limited to ClassDef ProjectionV2Qualification; module-level render_pair/build_owner_map are unchanged.',
      reach='canonical_reader_test.make_real_generation execs this module as a factory on the native path, but uses only render_pair and build_owner_map, which are AST-identical; the test methods are not executed by native_probe.',
      controls=['tests/canonical-state-rotation.test.sh:13 runs this file'],
      evidence=['ast_delta.py 3e0f4b6d..338c4c36: only ClassDef:ProjectionV2Qualification differs', run('canonical-state-rotation')],
      residual='None for the native predicates.'),
 dict(path='fixtures/canonical-state-rotation/windows_qualification_test.py',
      change_class='b', status='COVERED',
      change='Test-only: adds WindowsRuntimeGitLayoutControls (ucrt64/mingw64 Git selection) (11c0dbd0).',
      reach='Not executed by native_probe; it controls os.name=="nt" branches only.',
      controls=['tests/canonical-state-rotation.test.sh:17 runs this file'],
      evidence=[run('canonical-state-rotation')],
      residual='Windows native behaviour stays DG18_SEPARATE, as the historical record says (windows_qualification).'),
 dict(path='fixtures/controller-initialization/author_checkpoint.py',
      change_class='c', status='PARTIAL',
      change='--activate/--activate-only now resolve bash once through shutil.which and pass the absolute path as argv[0], refusing when bash is absent; previously the literal "bash" (14adb7c4).',
      reach='Executed on the native path: CanonicalReaderTests.setUp runs author_checkpoint.py --activate.',
      controls=['tests/canonical-state-rotation.test.sh:19 (canonical_reader_test setUp in every case)', 'tests/continuity-contract.test.sh'],
      evidence=[run('canonical-state-rotation'), run('continuity-contract'), SOL18_READ],
      residual='Equivalence claim for independent review: on Linux, shutil.which(PATH) and execvp(PATH) resolve the same bash, so only argv[0] changes (bash ignores it for $0 when running a script). The missing-bash refusal changes the error, not the success path.'),
 dict(path='scripts/operational-evidence.py',
      change_class='c', status='OPEN', base=HIST,
      change='e76a07b2..V21 (3e0f4b6d..e76 is the historically reviewed 8ee4ae44 delta): purely additive data. There are 15 new _NATIVE_CONTINUITY_SOURCE_PROFILES_V1 rows and 15 new _NATIVE_CONTINUITY_TRANSPORT_PROFILES_V1 entries. _native_check_continuity_closure_v1 changes only by 14 helper pairs inside its os.name=="nt" tuple. There are no deletions.',
      reach='This is the native static owner and receiver (RECEIVER). On Linux, the V21 8-file helper tuple (claim-run.sh c059ad1b, validate-run-root.sh 9ff4ffb1, claim-run-rotation.py 824194fe, rotate-canonical-state.py 008d63f4, canonical_hot_projection.py 6ff0fe34, canonical_custody.py d52369e5, canonical_rotation_inputs.py 33c9ae52, read-canonical-pair.py 733964e5) is admitted only by the newly added last row ("prospective OR-rotation initializer and validator joined at a84b5b6c+8f59b2c8").',
      controls=['tests/operational-evidence-contract.test.sh', 'tests/work-graph-continuity-cases.py, tests/work-graph-source-observation-cases.py (registered by tests/native-work-graph.test.sh)', 'tests/composite-source-cases.py (tests/composite-source.test.sh)'],
      evidence=['ast_delta.py e76a07b2..338c4c36: +15 AugAssign source-profile rows, +15 transport-profile Assigns, FunctionDef _native_check_continuity_closure_v1 differs only in its nt tuple', PIN_OK + ' (compiler _NATIVE_STATIC_OWNER 441955/28d1b5d0 matches this file)', run('operational-evidence-contract'), run('wg-continuity-cases'), run('wg-source-observation-cases'), SOL17],
      residual='Native predicates fixed_receiver_identity, wrong_receiver_refusal and current_native_intake have not been observed at receiver 441955/28d1b5d0 with the V21 helper tuple. Historical native_prerequisite pins RECEIVER_SHA 5950164a/422801 and receiver_non_windows_ast_sha256 699eb268 (no producer). ' + NATIVE_NOTE),
 dict(path='scripts/work-graph-continuity-transport.py',
      change_class='c', status='OPEN',
      change='Additive: 16 new SOURCE_PROFILES_V1 entries (plus the _N07_PREDECESSOR_PROFILE alias) and 14 Windows core-8 pair constants. _windows_core_profile_v1 gains those pairs and is evaluated only under os.name=="nt". The bytes equal 3e0f4b6d at e76a07b2, so the historical record counted this member unchanged.',
      reach='Loaded by the compiler native continuity (pin _NATIVE_CONTINUITY_TRANSPORT 112819/4b7c944c). On Linux, the V21 tuple selects the new "composite-20261125-dg18-or-rotation-v1-core" profile. ORIGINAL14_SOURCE_PROFILES_V1 gains two mode-None overlays whose claim-run.sh (104155 B) cannot match the V21 32290-byte helper.',
      controls=['tests/work-graph-continuity-cases.py, tests/work-graph-source-observation-cases.py', 'tests/composite-source-cases.py'],
      evidence=['ast_delta.py e76a07b2..338c4c36: only Assign rows plus the nt-only _windows_core_profile_v1', PIN_OK, run('wg-continuity-cases'), run('wg-source-observation-cases'), SOL17],
      residual='Linux native continuity at V21 goes through a profile row with no native observation. This member was previously unchanged, so it is a new member of the native-relevant delta. ' + NATIVE_NOTE),
 dict(path='skills/implementaudit/scripts/canonical_hot_projection.py',
      change_class='c', status='OPEN',
      change='New refusals (53a80108). _v2_pending_rows: a SUPPORTED_RETRY original_occurrence_id must be the selected or a prior occurrence. parse_canonical_pair_v2: an accepted witness and a SUPPORTED_RETRY must bind an EVIDENCE artifact_ref of the pending row owner.',
      reach='This is the v2 canonical pair parser, used by rotation and pair reads on the native path (rotate-canonical-state pins it as 94767/6ff0fe34).',
      controls=['fixtures/canonical-state-rotation/protected_projection_v2_test.py new subtests (tests/canonical-state-rotation.test.sh:13)', 'canonical_reader_test (canonical-state-rotation.test.sh:19)', SOL18_ROT],
      evidence=[run('canonical-state-rotation'), SOL18_ROT, SOL18_READ],
      residual='This is a strict tightening. Conforming inputs (the unchanged v2/source.json fixture) are accepted in ordinary controls at V21, but the parser running inside the native intake at V21 is unobserved. Independent review is needed on whether the new owner-EVIDENCE binding can refuse a real native pending row that 3e0f4b6d accepted.'),
 dict(path='skills/implementaudit/scripts/canonical_rotation_inputs.py',
      change_class='b', status='COVERED',
      change='parse_exact_usage_v1 accepts params.usageMetadata == None (previously only absent or dict) (11538085). The AST delta is limited to that function.',
      reach='parse_exact_usage_v1 is reached only through the OR native-input lease/record routes (codex host usage), not the original14 cases. The internal rotate-canonical-state call sites build params without usageMetadata, where the old and new predicates agree.',
      controls=['native_input_adapter_test.test_null_wire_metadata_preserves_exact_usage_without_admitting_bad_metadata (canonical-state-rotation.test.sh:25)'],
      evidence=[run('canonical-state-rotation')],
      residual='The bytes are still a member of the 8-file continuity tuple admitted by operational-evidence.py (OPEN). The behaviour change belongs to DG18 OR scope.'),
 dict(path='skills/implementaudit/scripts/claim-run-rotation.py',
      change_class='c', status='PARTIAL',
      change='Pins move to V21 rotate-canonical-state.py (127141/008d63f4) and V21 validate-run-root.sh (126682/9ff4ffb1). Windows-only ucrt64 Git selection is added (nt branches). A second reviewed OR source-owner template (3d10e2cd) is added: the H0 shortcut is now evaluated after selector parsing, and native_preparation_for_owned_stdio_v1(owned_observation=) is new.',
      reach='Executed on the native path (claim, initialization, --invalidate-continuity). The OR selection code is unreachable there: _private_native_input_selection_v1 returns None at "if not path.exists()" because skills/implementaudit/scripts/compaction-source-owner-codex-app.py is absent at V21. The Linux-reachable delta is therefore the two pins.',
      controls=['tests/claim-run.test.sh', 'tests/canonical-state-rotation.test.sh (native_preparation_test, native_or_rotation_test, canonical_reader_test)', SOL18_ROT],
      evidence=[PIN_OK, run('claim-run'), run('canonical-state-rotation'), SOL18_ROT],
      residual='For review (DG18 OR scope, off the native-intake path): an H0 mechanical template without exactly one literal OWNED_STDIO_SELECTION_PIN now raises "private native selector is not one declared literal" instead of returning None. The pinned siblings carry their own residuals.'),
 dict(path='skills/implementaudit/scripts/claim-run.sh',
      change_class='c', status='PARTIAL',
      change='Pin-only: embedded expected claim-run-rotation.py identity 291624/128dfe66 -> 292218/824194fe.',
      reach='Executed on the native path. The only delta is the pin, which selects the V21 claim-run-rotation.py.',
      controls=['tests/claim-run.test.sh', 'tests/canonical-state-rotation.test.sh'],
      evidence=[PIN_OK, run('claim-run'), run('canonical-state-rotation'), SOL18_ROT],
      residual='The pin is coherence-only. The semantic residual lives in claim-run-rotation.py.'),
 dict(path='skills/implementaudit/scripts/compile-work-graph.py',
      change_class='c', status='PARTIAL', base=HIST,
      change='e76a07b2..V21 (3e0f..e76 is the historically reviewed 8ee4ae44 delta). The top-level AST differs only in: _NATIVE_STATIC_OWNER_{SHA256,BYTES} (to receiver 28d1b5d0/441955), _NATIVE_CONTINUITY_TRANSPORT_{SHA256,BYTES} (to 4b7c944c/112819), and _NATIVE_ROUTE_PRODUCER_PROFILES_V1, which consolidates 9 assignments into one literal and adds 15 producer profiles (all 21 e76 entries retained with equal values: 21 -> 36). Everything else is comment compaction.',
      reach='This is the native compiler (COMPILER). The route-producer table is unreachable in the native cases: ' + ROUTE_ABSENT + '. The Linux-reachable delta is the two pins.',
      controls=['tests/work-graph-compiler.test.sh', 'tests/native-work-graph.test.sh case files other than the two maintained native bodies', SOL17],
      evidence=['ast_delta.py e76a07b2..338c4c36: only the 5 Assign targets listed differ', PIN_OK, run('work-graph-compiler'), run('wg-continuity-cases'), run('wg-source-observation-cases'), SOL17],
      residual='The compiler logic is unchanged since the reviewed e76 delta. Its pins select the OPEN receiver and transport. native_prerequisite.py@b393a905 pins COMPILER_SHA 0aa4572a/262144; V21 is e65f13db/261264. compiler_normalized_ast_sha256 d655e326 has no qualified producer, so no V21 value exists.'),
 dict(path='skills/implementaudit/scripts/host-session-binding.py',
      change_class='b', status='COVERED',
      change='Windows store custody (windows_custody/security/private/store_directory/store_write), typed first-activation custody, and lookup_binding refactor (d10264be, 76d47406, 5900a598). os.name "nt" admitted.',
      reach='Not invoked by any native-path owner (no reference from claim-run.sh, claim-run-rotation.py, rotate-canonical-state.py, validate-run-root.sh, read-canonical-pair.py, compile-work-graph.py, operational-evidence.py or the case bodies). It is copied into the constructed scripts dir only.',
      controls=['tests/host-session-binding.test.sh', 'tests/host-session-binding-hardening.test.sh', 'tests/host-session-terminal.test.sh'],
      evidence=[run('host-session-binding'), run('host-session-binding-hardening'), run('host-session-terminal')],
      residual='Windows host Stop/binding native behaviour is DG17/DG18 scope, outside this Linux applicability.'),
 dict(path='skills/implementaudit/scripts/host-stop-interlock.py',
      change_class='b', status='COVERED',
      change='DG17 selected Stop v3: binding-owner-selected fallback argv, exact active binding, activation custody drift, Windows descendant containment (d10264be, 76d47406, 8caa0922, 5900a598, defa480b, 4a50065d).',
      reach='Not invoked by any native-path owner (same reference check as host-session-binding.py).',
      controls=['tests/host-session-binding.test.sh', 'tests/host-session-binding-hardening.test.sh', 'tests/host-session-terminal.test.sh', 'tests/nonterminal-yield-cases.py via tests/run-root-validation.test.sh'],
      evidence=[run('host-session-binding'), run('host-session-binding-hardening'), run('host-session-terminal'), run('run-root-validation')],
      residual='Windows Stop qualification is DG17 scope.'),
 dict(path='skills/implementaudit/scripts/read-canonical-pair.py',
      change_class='b', status='COVERED',
      change='Docstring/comment compaction. The top-level AST differs only in FunctionDef call, inside its os.name=="nt" branch (ucrt64 then mingw64 Git) (11c0dbd0, 14ed4c71).',
      reach='Executed on the native path (--native-guards), but the changed lines are Windows-only; the Linux behaviour is AST-identical.',
      controls=['windows_qualification_test.WindowsRuntimeGitLayoutControls (canonical-state-rotation.test.sh:17)', 'canonical_reader_test (canonical-state-rotation.test.sh:19)'],
      evidence=['ast_delta.py 3e0f4b6d..338c4c36: only FunctionDef:call differs', run('canonical-state-rotation'), SOL18_READ],
      residual='The bytes are still a member of the 8-file continuity tuple admitted by operational-evidence.py (OPEN).'),
 dict(path='skills/implementaudit/scripts/repo-state.sh',
      change_class='b', status='COVERED',
      change='5S census: link-object classification, rename membership, private-scratch exclusion, deterministic acquisition/text boundaries, hunk-based added-content detection, staged/committed evidence, normal pre-stop L4 route.',
      reach='Not invoked by any native-path owner. It is copied into the constructed scripts dir only; canonical_reader_test reads references/repo-state-comparison.md, not this script.',
      controls=['tests/repo-state.test.sh'],
      evidence=[run('repo-state')],
      residual='None for the native predicates.'),
 dict(path='skills/implementaudit/scripts/rotate-canonical-state.py',
      change_class='c', status='PARTIAL',
      change='Pins move to hot projection 94767/6ff0fe34 and native input module 27931/33c9ae52. Windows ucrt64 Git path and PATH (nt). full_or_calibration_contract_v1 is rewritten as a literal. _historical_or_calibrations_v1 is regenerated and retains the dc95 producer as _RETAINED_WINDOW_INPUT_SHA256. _check_native_input_record v2_producers adds dc95.',
      reach='Executed on the native path (rotation). The calibration and native-input-record changes govern OR/native-input manifests. The Linux-reachable delta in the original14 cases is the pins plus calibration membership checks.',
      controls=['native_input_adapter_test.test_archive_schema_is_bound_to_exact_window_calibration', 'tests/canonical-state-rotation.test.sh', SOL18_ROT, SOL18_ARCH],
      evidence=[PIN_OK, 'calib_equiv.sh (WSL Py3.12.3) imports both revisions: full_or_equal_except_module_pin=True; token_contract_equal=True; old_historical (5 rows) is a subset of new (7 rows); the 2 added rows are R0039-F1-CAL-v2 and R4-FRESH-NATIVE-OR-CANARY-v1 at 33c9ae52', run('canonical-state-rotation'), SOL18_ROT, SOL18_ARCH],
      residual='For review: the historical calibration set is a strict superset (+2 live rows at the new module pin), and dc95 v2-schema archive mapping is retained. The value equivalence of the full-OR literal is mechanically shown. There is no native observation of rotation at V21.'),
 dict(path='skills/implementaudit/scripts/validate-run-root.sh',
      change_class='c', status='OPEN',
      change='Substantial POSIX-reachable validator logic changes:\n- per-owner private TMPDIR with removal and a refusal if it is not removed;\n- OwnerTimeout -> OWNER_TIMEOUT disposition kind;\n- live-owner stop on exit;\n- current_andon_rows (case-insensitive headers, indented tables, unique row identity) shared by closure and handoff;\n- case-insensitive Andon heading;\n- DONE-phase "expected: output line" capture checks;\n- one unambiguous Current phase record;\n- NONTERMINAL_YIELD concurrent structural run with review-owner fence;\n- parallel sibling-run captures (max 4).\nIt also adds Windows job-object owner containment (nt).',
      reach='Executed on the native path: it is the validate half of the claim/validate helper pair evaluated by the compiler native continuity, and it is pinned by claim-run-rotation initialization.',
      controls=['tests/run-root-validation.test.sh (incl. nonterminal-yield-cases.py, turn-disposition-cases.py)', 'tests/claim-run.test.sh', 'tests/continuity-contract.test.sh', 'tests/evidence-anchoring.test.sh', 'tests/andon-class-contract.test.sh', 'tests/composite-source-cases.py OWNER_TIMEOUT cases'],
      evidence=[run('run-root-validation'), run('claim-run'), run('continuity-contract'), run('evidence-anchoring-shim'), run('andon-class-contract'), SOL17],
      residual='The changed validator semantics have not been observed inside the native continuity at V21. Independent review should check whether owner TMPDIR isolation, sibling-run parallel capture and current_andon_rows parsing are inert for the constructed original14 run root.'),
 dict(path='skills/implementaudit/templates/PROTOCOL.md',
      change_class='b', status='COVERED',
      change='Procedure text: prose compaction and a new normal-gate rule declaring Smoke "expected: output line <literal>" (a0fc7788). Also: finding-row anchor restored (7e2f9407), evidence-anchor route restored (329ff297), OR pin scope wording (b4335c33, be74fe66). No implementaudit-work-graph fences at either revision.',
      reach='Copied into the constructed run root by initialization and validated for required anchors by validate-run-root.sh. It contributes no native graph source (0 work-graph fences at 3e0f4b6d and 338c4c36).',
      controls=['tests/run-root-validation.test.sh', 'tests/continuity-contract.test.sh', 'tests/evidence-anchoring.test.sh', 'tests/andon-class-contract.test.sh', 'canonical_reader_test initialization (canonical-state-rotation.test.sh:19)'],
      evidence=[run('run-root-validation'), run('continuity-contract'), run('evidence-anchoring-shim'), run('andon-class-contract'), run('canonical-state-rotation')],
      residual='Agent-facing procedure change. Its enforcement lives in validate-run-root.sh (OPEN).'),
]

assert len(rows) == 20 and len({r['path'] for r in rows}) == 20
for r in rows:
    base = r.pop('base', RETAINED)
    r['retained'] = blob(RETAINED, r['path'])
    r['current'] = blob(V21, r['path'])
    r['commits_since_retained'] = commits(r['path'])
    if base != RETAINED:
        r['commits_since_historical_e76'] = commits(r['path'], HIST)
        r['delta_base'] = HIST
    else:
        r['delta_base'] = RETAINED

counts = {s: sum(r['status'] == s for r in rows) for s in ('COVERED', 'PARTIAL', 'OPEN')}
doc = dict(schema='dg16.v21-native-applicability-bridge.v1', authority='NONE',
           ruling='Root at 24c4684 handoff/astra-dg16-dg18/discussions/DG16-DG17-reader-bindings.md',
           retained_source_commit=RETAINED, historical_source_commit=HIST, product_commit=V21, product_tree=V21_TREE,
           applicability_input_sha256='9a073972b3f0599b1ddc9ce98a9643ef27414fa6b168fa7aa1b0b7bd24326033',
           native_path=NATIVE_PATH,
           classes={'a': 'non-semantic', 'b': 'semantic, off the Linux native-intake path (or Windows-only branch)', 'c': 'semantic on the native-relevant path'},
           statuses={'COVERED': 'class a/b with a passing registered control at V21',
                     'PARTIAL': 'class c whose Linux-reachable delta is pin-coherence only or mechanically shown equivalent; ordinary controls pass at V21; no native observation at V21',
                     'OPEN': 'class c with Linux-reachable behaviour change; native predicate uncovered and left open'},
           native_predicates_at_v21=dict(status='OPEN', predicates=['fixed_receiver_identity', 'wrong_receiver_refusal', 'current_native_intake', 'later_invalidation_refusal', 'host_and_diagnosed_intake / ordinary_host_source_currentness_custody'], note=NATIVE_NOTE),
           local_runs=dict(environment='fresh WSL Ubuntu clone of 338c4c36 (git clone --no-checkout + checkout; clean status), python3 3.12.3, env -i, private TMPDIR; tests/native-work-graph.test.sh (maintained native case bodies) and the native probe deliberately NOT run', results=runs),
           counts=counts, members=rows, original_awards=[])
outdir.mkdir(parents=True, exist_ok=True)
jraw = (json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + '\n').encode()
(outdir / 'BRIDGE.json').write_bytes(jraw)

def short(c):
    return c['commit'][:8]
lines = ['# V21 native-source applicability bridge (per changed member)', '',
         f'Authority NONE. Ruling: {doc["ruling"]}. Product {V21} / tree {V21_TREE}; retained native-qualified source {RETAINED}; historical adopted source {HIST}. Input rows sha256 `{doc["applicability_input_sha256"]}`.', '',
         NATIVE_PATH, '',
         'Classes: a = non-semantic; b = semantic, off the Linux native-intake path or Windows-only; c = semantic on the native-relevant path.',
         'COVERED = a/b with a passing registered control at V21. PARTIAL = c whose Linux-reachable delta is pin-coherence only or mechanically equivalent (no native observation at V21). OPEN = c with Linux-reachable behaviour change; the native predicate stays open.', '',
         f'Counts: COVERED {counts["COVERED"]}, PARTIAL {counts["PARTIAL"]}, OPEN {counts["OPEN"]}. The native predicates at V21 (fixed_receiver_identity, wrong_receiver_refusal, current_native_intake, later_invalidation_refusal, host/currentness custody) remain OPEN.', '',
         '| # | Member | Commits (3e0f4b6d..V21) | Class | Status | Covering controls / evidence | Residual semantic difference |',
         '| ---: | --- | --- | :---: | :---: | --- | --- |']
for i, r in enumerate(rows, 1):
    cm = ', '.join(short(c) for c in r['commits_since_retained'])
    if 'commits_since_historical_e76' in r:
        cm += '<br>since e76: ' + ', '.join(short(c) for c in r['commits_since_historical_e76'])
    ev = '<br>'.join(r['controls'] + r['evidence']).replace('|', '/')
    lines.append(f'| {i} | `{r["path"]}` | {cm} | {r["change_class"]} | {r["status"]} | {ev} | {r["residual"].replace("|", "/")} |')
lines += ['', '## Change and reach notes', '']
for i, r in enumerate(rows, 1):
    lines += [f'**{i}. `{r["path"]}`** ({r["retained"]["bytes"]} B `{r["retained"]["sha256"][:12]}` -> {r["current"]["bytes"]} B `{r["current"]["sha256"][:12]}`)', '',
              f'- Change: {r["change"]}', f'- Native reach: {r["reach"]}', '']
lines += ['## Commit subjects', '']
seen = {}
for r in rows:
    for c in r['commits_since_retained']:
        seen[c['commit']] = c['subject']
for k, v in seen.items():
    lines.append(f'- `{k[:8]}` {v}')
lines += ['', '## Local ordinary runs (fresh WSL clone of V21)', '', doc['local_runs']['environment'], '']
for k, v in runs.items():
    lines.append(f'- `{k}`: rc {v["rc"]}, stdout `{v["stdout_sha256"]}`, stderr `{v["stderr_sha256"]}`')
mraw = ('\n'.join(lines) + '\n').encode()
(outdir / 'BRIDGE.md').write_bytes(mraw)
for name, raw in (('BRIDGE.json', jraw), ('BRIDGE.md', mraw)):
    print(name, len(raw), hashlib.sha256(raw).hexdigest())
print(json.dumps(counts))
