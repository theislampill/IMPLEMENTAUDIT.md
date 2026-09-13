"""Synthetic behavioral controls; no native/secret configuration is loaded."""
import copy
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tomllib
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
MODULE = HERE.parents[1] / "skills/implementaudit/scripts/codex-recovery-config-transition.py"
FEATURE = "retain_client_developer_messages"
FIELD = "mcp_servers.node_repl.env.SKY_CUA_NATIVE_PIPE_DIRECTORY"
OLD = r"\\.\pipe\codex-computer-use-11111111-1111-4111-8111-111111111111"
NEW = r"\\.\pipe\codex-computer-use-22222222-2222-4222-8222-222222222222"
USER = "C:/fixture/codex/config.toml"
SYSTEM = "C:/fixture/system/config.toml"
ASAR = '2bd5b96a48232f3ccf3df6be50965920699ea3a1b4512dcdd770e209fd1f009e'
MEMBER = 'b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def jsha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def physical(value=OLD):
    return ("model = 'fixture-model'\n"
            "[features]\nretain_client_developer_messages = true\n"
            "[mcp_servers.node_repl.env]\n"
            "SKY_CUA_NATIVE_PIPE_DIRECTORY = '" + value + "'\n").encode()


def meta(raw, timestamp):
    return {"path": USER, "exists": True, "bytes": len(raw),
            "sha256": sha(raw), "mtime_ns": timestamp}


def native(raw):
    cfg = tomllib.loads(raw.decode())
    name = {"file": USER, "profile": None, "type": "user"}
    layer = {"name": name, "version": "sha256:" + jsha(cfg),
             "config": cfg, "disabledReason": None}
    return {"config": copy.deepcopy(cfg), "layers": [
        {"name": {"type": "sessionFlags"}, "version": "sha256:" + jsha({}),
         "config": {}, "disabledReason": None}, layer,
        {"name": {"file": SYSTEM, "type": "system"},
         "version": "sha256:" + jsha({}), "config": {}, "disabledReason": None}],
        "origins": {"features." + FEATURE: {"name": name, "version": layer["version"]}}}


def historical(raw):
    result = native(raw)
    return [{"cwd": cwd, "feature": True, "layers": [
        {"source": layer["name"], "version": layer["version"],
         "disabledReason": None, "feature": layer["config"].get("features", {}).get(FEATURE),
         "config_sha256": jsha(layer["config"]), "files":
         [meta(raw, 100)] if layer["name"].get("type") == "user" else
         [{"exists": False, "path": SYSTEM}] if layer["name"].get("type") == "system" else []}
        for layer in result["layers"]], "full_config_sha256": jsha(result["config"]),
        "feature_origin": result["origins"]["features." + FEATURE],
        "raw_config_persisted": False} for cwd in ["C:/fixture/repo", "C:/fixture"]]


def fixture():
    previous = historical(physical())
    raws = [[{"cwd": cwd, "result": native(physical(NEW))}
             for cwd in ["C:/fixture/repo", "C:/fixture"]] for _ in range(2)]
    files = [[{"metadata": meta(physical(NEW), 200), "content": physical(NEW)},
              {"metadata": {"exists": False, "path": SYSTEM}, "content": None}]
             for _ in range(2)]
    witness = {"schema": "implementaudit.config-pipe-transition.v1", "field": FIELD,
               "previous_value": OLD, "current_value": NEW, "user_config_path": USER,
               "producer": {"asar_sha256": ASAR, "member_sha256": MEMBER}}
    args = [previous, raws, files, witness]
    repin(args)
    return args


def repin(args):
    previous, raws, files, witness = args
    witness.update(previous_filtered_configs_sha256=jsha(previous),
                   current_native_results_sha256=jsha(raws[0]),
                   current_physical_metadata_sha256=jsha([e["metadata"] for e in files[0]]))


class TransitionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if MODULE.exists():
            spec = importlib.util.spec_from_file_location("config_transition_controls", MODULE)
            cls.mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = cls.mod
            spec.loader.exec_module(cls.mod)

    def run_helper(self, args):
        self.assertTrue(MODULE.exists(), "missing config transition validation capability")
        return self.mod.validate_config_transition(*args)

    def reject(self, mutate, repin_after=True):
        args = fixture()
        mutate(args)
        if repin_after:
            repin(args)
        self.assertTrue(MODULE.exists(), "missing config transition validation capability")
        with self.assertRaises(self.mod.ConfigTransitionRefusal):
            self.run_helper(args)

    def test_exact_pipe_transition_returns_current_not_rewritten_old(self):
        args = fixture()
        frozen = copy.deepcopy(args)
        filtered, evidence = self.run_helper(args)
        self.assertEqual(args, frozen)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["layers"][1]["files"][0], meta(physical(NEW), 200))
        self.assertNotEqual(filtered[0]["full_config_sha256"], args[0][0]["full_config_sha256"])
        self.assertEqual(evidence["status"], "EXACT_CONFIG_TRANSITION_ONLY_NO_AUTHORITY")
        self.assertNotIn("fixture-model", json.dumps(evidence))
        self.assertNotIn(NEW, json.dumps(evidence))
        self.assertEqual(evidence["reads_verified"], 2)

    def test_rejects_second_physical_field_change(self):
        def mutate(a):
            for read in a[2]:
                read[0]["content"] = read[0]["content"].replace(b"fixture-model", b"changed-model")
                read[0]["metadata"] = meta(read[0]["content"], 200)
        self.reject(mutate)

    def test_rejects_native_only_second_field_change(self):
        self.reject(lambda a: [r["result"]["config"].update(model="different") for read in a[1] for r in read])

    def test_rejects_effective_feature_false(self):
        self.reject(lambda a: [r["result"]["config"]["features"].update({FEATURE: False}) for read in a[1] for r in read])

    def test_rejects_feature_origin_source_change(self):
        self.reject(lambda a: [r["result"]["origins"]["features." + FEATURE]["name"].update(type="project") for read in a[1] for r in read])

    def test_rejects_feature_origin_unbound_version(self):
        self.reject(lambda a: [r["result"]["origins"]["features." + FEATURE].update(version="sha256:" + "a" * 64) for read in a[1] for r in read])

    def test_rejects_layer_reordering(self):
        self.reject(lambda a: [r["result"]["layers"].reverse() for read in a[1] for r in read])

    def test_rejects_layer_count_change(self):
        self.reject(lambda a: [r["result"]["layers"].pop() for read in a[1] for r in read])

    def test_rejects_layer_disabled_status_change(self):
        self.reject(lambda a: [r["result"]["layers"][1].update(disabledReason="disabled") for read in a[1] for r in read])

    def test_rejects_unrelated_layer_semantic_change(self):
        self.reject(lambda a: [r["result"]["layers"][0]["config"].update(approval_policy="never") for read in a[1] for r in read])

    def test_rejects_wrong_prior_uuid(self):
        self.reject(lambda a: a[3].update(previous_value=OLD.replace("11111111-", "33333333-")))

    def test_rejects_foreign_pipe_prefix(self):
        self.reject(lambda a: a[3].update(current_value=NEW.replace("codex-computer-use-", "foreign-")))

    def test_rejects_non_uuid_pipe(self):
        self.reject(lambda a: a[3].update(current_value=r"\\.\pipe\codex-computer-use-not-a-uuid"))

    def test_rejects_same_value_as_transition(self):
        self.reject(lambda a: a[3].update(previous_value=NEW))

    def test_rejects_duplicate_physical_value(self):
        def mutate(a):
            for read in a[2]:
                read[0]["content"] += ("# " + NEW + "\n").encode()
                read[0]["metadata"] = meta(read[0]["content"], 200)
        self.reject(mutate)

    def test_rejects_duplicate_native_value(self):
        self.reject(lambda a: [r["result"]["config"].update(other=NEW) for read in a[1] for r in read])

    def test_rejects_second_native_read_drift(self):
        self.reject(lambda a: a[1][1][0]["result"]["config"].update(model="drift"))

    def test_rejects_second_physical_read_mtime_drift(self):
        self.reject(lambda a: a[2][1][0]["metadata"].update(mtime_ns=201))

    def test_rejects_current_content_metadata_mismatch(self):
        self.reject(lambda a: [read[0]["metadata"].update(sha256="a" * 64) for read in a[2]])

    def test_rejects_current_size_metadata_mismatch(self):
        self.reject(lambda a: [read[0]["metadata"].update(bytes=1) for read in a[2]])

    def test_rejects_missing_layer_file_evidence(self):
        self.reject(lambda a: [read.pop() for read in a[2]])

    def test_rejects_duplicate_file_metadata(self):
        self.reject(lambda a: [read.append(copy.deepcopy(read[0])) for read in a[2]])

    def test_rejects_missing_cwd(self):
        self.reject(lambda a: [read.pop() for read in a[1]])

    def test_rejects_changed_cwd(self):
        self.reject(lambda a: [read[0].update(cwd="C:/foreign") for read in a[1]])

    def test_rejects_wrong_previous_record_digest(self):
        self.reject(lambda a: a[3].update(previous_filtered_configs_sha256="0" * 64), False)

    def test_rejects_wrong_current_record_digest(self):
        self.reject(lambda a: a[3].update(current_native_results_sha256="0" * 64), False)

    def test_rejects_wrong_physical_record_digest(self):
        self.reject(lambda a: a[3].update(current_physical_metadata_sha256="0" * 64), False)

    def test_rejects_wrong_producer_source_pin(self):
        self.reject(lambda a: a[3]["producer"].update(asar_sha256="0" * 64))

    def test_rejects_unsupported_field_exemption(self):
        self.reject(lambda a: a[3].update(field="mcp_servers"))

    def test_rejects_old_feature_already_false(self):
        self.reject(lambda a: a[0][0].update(feature=False))

    def test_rejects_wrong_old_physical_hash(self):
        self.reject(lambda a: a[0][0]["layers"][1]["files"][0].update(sha256="0" * 64))

    def test_rejects_wrong_old_semantic_hash(self):
        self.reject(lambda a: a[0][0].update(full_config_sha256="0" * 64))

    def test_rejects_user_version_not_derived_from_layer(self):
        self.reject(lambda a: [r["result"]["layers"][1].update(version="sha256:" + "0" * 64) for read in a[1] for r in read])




def multi_origin_material(pipe, timestamp):
    """Independently assembled full native fixture; no observed-read claim."""
    raw = physical(pipe)
    result = native(raw)
    result['origins']['model'] = {
        'name': copy.deepcopy(result['layers'][1]['name']),
        'version': result['layers'][1]['version'], 'metadata': {'rank': 7}}
    result['origins']['stable.system'] = {
        'name': copy.deepcopy(result['layers'][2]['name']),
        'version': result['layers'][2]['version'], 'metadata': {'rank': 3}}
    rows = [{'cwd': cwd, 'result': copy.deepcopy(result)}
            for cwd in ('C:/fixture/repo', 'C:/fixture')]
    files = [{'metadata': meta(raw, timestamp), 'content': raw},
             {'metadata': {'exists': False, 'path': SYSTEM}, 'content': None}]
    return rows, files


class OriginInverseControls(unittest.TestCase):
    setUpClass = TransitionControls.__dict__['setUpClass']

    def args(self):
        args = fixture()
        rows, files = multi_origin_material(NEW, 200)
        args[1] = [rows, copy.deepcopy(rows)]
        args[2] = [files, copy.deepcopy(files)]
        repin(args)
        return args

    def test_full_inverse_restores_multiple_exact_user_origins(self):
        # Catches feature-only inversion even when filtered config equality passes.
        args = self.args(); frozen = copy.deepcopy(args)
        self.mod.validate_config_transition(*args)
        rows, files, binding = self.mod.derive_previous_material(args[0], args[1][0], args[2][0], args[3])
        expected_rows, expected_files = multi_origin_material(OLD, 100)
        self.assertEqual(rows, expected_rows)
        self.assertEqual(files, expected_files)
        self.assertEqual(binding['native_results_sha256'], jsha(expected_rows))
        self.assertEqual(binding['physical_metadata_sha256'], jsha([f['metadata'] for f in expected_files]))
        self.assertEqual(args, frozen)

    def test_feature_only_full_inverse_preserves_prior_control(self):
        args = fixture()
        rows, _, binding = self.mod.derive_previous_material(args[0], args[1][0], args[2][0], args[3])
        expected = [{'cwd': cwd, 'result': native(physical(OLD))}
                    for cwd in ('C:/fixture/repo', 'C:/fixture')]
        self.assertEqual(rows, expected)
        self.assertEqual(binding['native_results_sha256'], jsha(expected))

    def test_unrelated_origin_and_extra_metadata_are_preserved(self):
        args = self.args()
        rows, _, _ = self.mod.derive_previous_material(args[0], args[1][0], args[2][0], args[3])
        for old, now in zip(rows, args[1][0]):
            self.assertEqual(old['result']['origins']['stable.system'], now['result']['origins']['stable.system'])
            self.assertEqual(old['result']['origins']['model']['metadata'], {'rank': 7})

    def test_wrong_ambiguous_or_unknown_origin_binding_refused(self):
        for case in ('source', 'version', 'unknown', 'shape', 'ambiguous'):
            with self.subTest(case=case):
                args = self.args()
                for read in args[1]:
                    for row in read:
                        origin = row['result']['origins']['model']
                        if case == 'source': origin['name']['file'] = 'C:/other/config.toml'
                        elif case == 'version': origin['version'] = 'sha256:' + '0' * 64
                        elif case == 'unknown': origin['name'] = {'type': 'unknown'}
                        elif case == 'shape': row['result']['origins']['model'] = []
                        else: origin['name']['profile'] = 'unbound-profile'
                repin(args)
                with self.assertRaises(self.mod.ConfigTransitionRefusal):
                    self.mod.derive_previous_material(args[0], args[1][0], args[2][0], args[3])

    def test_inverse_requires_exact_relation_before_derivation(self):
        args = self.args()
        args[3]['current_native_results_sha256'] = '0' * 64
        with self.assertRaises(self.mod.ConfigTransitionRefusal):
            self.mod.derive_previous_material(args[0], args[1][0], args[2][0], args[3])

class NativeObserverLoaderControls(unittest.TestCase):
    """Exercise the real adjacent-source loader without creating an observer."""
    def setUp(self):
        path = MODULE.with_name('route-transaction.py')
        spec = importlib.util.spec_from_file_location('typed_observer_loader_controls', path)
        self.route = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.route)
        self.reader = MODULE.with_name('codex-recovery-native-reader.py').resolve()

    def test_configured_reader_digest_loads_the_actual_adjacent_module(self):
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                module = self.route.recovery_native_observer_module_v1()
        except SystemExit as exc:
            self.fail('Selected observer failed its actual loader: ' + str(exc) + ' ' + output.getvalue())
        self.assertEqual(Path(module.__file__).resolve(), self.reader)
        self.assertTrue(callable(module.NativeRecoveryObserver))
        self.assertEqual(output.getvalue(), '')

    def test_actual_loader_refuses_untyped_wrong_or_reformatted_digests(self):
        raw = sha(self.reader.read_bytes())
        for label, value in (
            ('raw-only', raw), ('wrong-hash', 'sha256:' + '0' * 64),
            ('double-prefix', 'sha256:sha256:' + raw), ('wrong-algorithm', 'sha512:' + raw),
            ('prefix-case', 'SHA256:' + raw), ('hash-case', 'sha256:' + raw.upper()),
            ('trailing-space', 'sha256:' + raw + ' '), ('missing-hash', 'sha256:')):
            with self.subTest(label=label), patch.object(self.route, 'RECOVERY_NATIVE_READER_DIGEST', value):
                output = io.StringIO()
                with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as caught:
                    self.route.recovery_native_observer_module_v1()
                self.assertEqual(caught.exception.code, 2)
                result = json.loads(output.getvalue())
                self.assertEqual(result['status'], 'UNAVAILABLE')
                self.assertEqual(result['error'], 'native observer source differs')
                self.assertEqual(result['decision'], 'REQUIRED')
                self.assertFalse(result['advance_allowed'])
                self.assertFalse(result['enforcement_available'])



class NativeTargetBindingControls(unittest.TestCase):
    """Cold source controls for one exact proposed tuple, never native proof."""
    BINARY = '081e4de4be8e38fac6ed4d95e3b1a0b9f6d31c090ddc36e1696b349fe406f575'
    OLD_BINARY = '3d6ca7085c932b62ef4ee4877e92f15b050fb94b2eb8e6c10a346a06248c6004'
    EARLIER_BINARY = 'ccdc9eb9dd71fbcfb03ad42c4eca2b0d6ff6fbd32ebe9416550e6244561e559b'
    CURRENT_ASAR = '2bd5b96a48232f3ccf3df6be50965920699ea3a1b4512dcdd770e209fd1f009e'
    CURRENT_MEMBER = 'b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4'

    def setUp(self):
        def load(name):
            path = MODULE.with_name(name)
            spec = importlib.util.spec_from_file_location('cold_target_' + name.replace('-', '_'), path)
            value = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(value)
            return value
        self.reader = load('codex-recovery-native-reader.py')
        self.binding = load('codex-native-desktop-binding.py')
        self.config = load('codex-recovery-config-transition.py')

    def observer(self):
        return self.reader.NativeRecoveryObserver(binary='C:/synthetic/current/codex.exe',
            home=Path.home() / '.codex', repo='C:/synthetic/repo', controller_cwd='C:/synthetic/repo',
            plugin_root='C:/synthetic/plugin', plugin_id='implementaudit@fixture', task='synthetic-task')

    def parent_fixture(self):
        root = r'C:\Program Files\WindowsApps\OpenAI.Codex_26.908.4834.0_x64__2p2nqsd0c76g0'
        exe, asar = root + r'\app\ChatGPT.exe', root + r'\app\resources\app.asar'
        return {'path': exe, 'source_binding': {'resolved_executable_path': exe,
            'package_root': root, 'package_version': '26.908.4834.0',
            'derived_asar_path': asar, 'executable': {'path': exe,
                'sha256': 'ca98461fd573f8b9912f48080b0f40f3b44788d1074493f4285e68169503fc23'},
            'asar': {'path': asar, 'sha256': self.CURRENT_ASAR},
            'executable_version': {'file': '152.0.7977.83', 'product': '152.0.7977.83'}}}

    def test_selected_binary_reaches_the_exact_read_only_request_boundary(self):
        # Restoring the stale digest must fail before the supported requests.
        class RequestsSelected(Exception): pass
        observer = self.observer()
        def boundary(methods):
            cwd = str(observer.repo)
            self.assertEqual(methods, [('config/read', {'cwd': cwd, 'includeLayers': True}, 'ConfigRead'),
                ('config/read', {'cwd': cwd, 'includeLayers': True}, 'ConfigRead'),
                ('hooks/list', {'cwds': [cwd]}, 'HooksList'),
                ('thread/read', {'threadId': 'synthetic-task', 'includeTurns': False}, 'ThreadRead')])
            raise RequestsSelected()
        with patch.object(self.reader, 'file_observation', return_value={'sha256': self.BINARY}), \
             patch.object(observer, '_read_native', side_effect=boundary):
            try:
                observer.native_snapshot()
            except RequestsSelected:
                pass
            except self.reader.Refusal as exc:
                self.fail('Selected target refused before actual request selection: ' + str(exc))
            else:
                self.fail('Expected captured request boundary')

    def test_old_and_unselected_binary_fail_before_any_request(self):
        observer = self.observer()
        for digest in (self.OLD_BINARY, self.EARLIER_BINARY, '0' * 64, self.BINARY[:-1] + '0'):
            with self.subTest(digest=digest), \
                 patch.object(self.reader, 'file_observation', return_value={'sha256': digest}), \
                 patch.object(observer, '_read_native', side_effect=AssertionError('native request reached')):
                with self.assertRaisesRegex(self.reader.Refusal, '^native executable changed$'):
                    observer.native_snapshot()

    def test_selected_parent_matches_its_own_derived_bundle(self):
        parent = self.parent_fixture()
        self.assertTrue(self.binding.parent_matches(parent, parent['source_binding']['asar']))

    def test_complete_predecessor_parent_is_not_a_current_binding(self):
        root = r'C:\Program Files\WindowsApps\OpenAI.Codex_26.903.9818.0_x64__2p2nqsd0c76g0'
        exe, asar = root + r'\app\ChatGPT.exe', root + r'\app\resources\app.asar'
        parent = self.parent_fixture(); source = parent['source_binding']
        parent['path'] = exe
        source.update(resolved_executable_path=exe, package_root=root,
                      package_version='26.903.9818.0', derived_asar_path=asar,
                      executable={'path': exe, 'sha256': '49e7e8f5db0a4c8a12a666b70dac40e0e88a1873d02e8aafb82c3e8cabeca49c'},
                      asar={'path': asar, 'sha256': '5d9b0399491060b2756fca70c2e5cca746fa8eb38372b7ad8f236dc69bda0bc6'})
        self.assertFalse(self.binding.parent_matches(parent, source['asar']))

    def test_partial_parent_or_reviewed_bundle_is_refused(self):
        for field in ('resolved_executable_path', 'package_root', 'package_version',
                      'derived_asar_path', 'executable', 'asar', 'executable_version'):
            with self.subTest(missing=field):
                parent = self.parent_fixture(); bundle = copy.deepcopy(parent['source_binding']['asar'])
                parent['source_binding'].pop(field)
                self.assertFalse(self.binding.parent_matches(parent, bundle))
        parent = self.parent_fixture(); bundle = parent['source_binding']['asar']
        for value in (None, {}, {'path': bundle['path']}, {'sha256': bundle['sha256']}):
            with self.subTest(bundle=value):
                self.assertFalse(self.binding.parent_matches(parent, value))

    def test_foreign_or_mixed_parent_tuple_is_refused(self):
        # Each negative is paired with the complete selected-tuple positive.
        for field in ('parent', 'resolved', 'root', 'package_version', 'exe_hash',
                      'exe_version', 'derived_asar', 'asar_hash', 'bundle_path', 'bundle_hash'):
            with self.subTest(field=field):
                parent = self.parent_fixture(); s = parent['source_binding']; bundle = copy.deepcopy(s['asar'])
                if field == 'parent': parent['path'] = 'C:/foreign/ChatGPT.exe'
                elif field == 'resolved': s['resolved_executable_path'] = 'C:/foreign/ChatGPT.exe'
                elif field == 'root': s['package_root'] = 'C:/foreign'
                elif field == 'package_version': s['package_version'] = '26.903.8094.0'
                elif field == 'exe_hash': s['executable']['sha256'] = '23796d3d11d19cd4cc0aef5b00b33f362cdcda98aa82607c27b9011f3c8e095f'
                elif field == 'exe_version': s['executable_version']['file'] = '0.0.0.0'
                elif field == 'derived_asar': s['derived_asar_path'] = 'C:/foreign/app.asar'
                elif field == 'asar_hash': s['asar']['sha256'] = '3b8e61c9b7afefeda3166f251270724a138af15eb947b7c3907691a695bce66c'
                elif field == 'bundle_path': bundle['path'] = 'C:/foreign/app.asar'
                else: bundle['sha256'] = '0' * 64
                self.assertFalse(self.binding.parent_matches(parent, bundle))

    def test_current_producer_allows_only_the_existing_exact_pipe_relation(self):
        args = fixture()
        args[3]['producer'] = {'asar_sha256': self.CURRENT_ASAR, 'member_sha256': self.CURRENT_MEMBER}
        original = copy.deepcopy(args)
        try:
            filtered, evidence = self.config.validate_config_transition(*args)
        except self.config.ConfigTransitionRefusal as exc:
            self.fail('Current source tuple refused: ' + str(exc))
        self.assertEqual(args, original)
        self.assertEqual(filtered[0]['full_config_sha256'], jsha(native(physical(NEW))['config']))
        self.assertEqual(evidence['field'], FIELD)

    def test_historical_or_mixed_producer_cannot_authorize_current_relation(self):
        old_asar = '3b8e61c9b7afefeda3166f251270724a138af15eb947b7c3907691a695bce66c'
        old_member = '9b958b85fea7d13c2f05b08600c0cb7fbbbf2b0b39bccdf2501f5f1002c94fa1'
        prior_asar = '5d9b0399491060b2756fca70c2e5cca746fa8eb38372b7ad8f236dc69bda0bc6'
        prior_member = '471f06dfcda15de10196f701504244c6f412d7ed401c155efc56a427a89a3195'
        for asar, member in ((old_asar, old_member), (old_asar, self.CURRENT_MEMBER),
                             (self.CURRENT_ASAR, old_member), (self.CURRENT_ASAR, '0' * 64),
                             (prior_asar, prior_member), (prior_asar, self.CURRENT_MEMBER),
                             (self.CURRENT_ASAR, prior_member)):
            with self.subTest(asar=asar, member=member):
                args = fixture(); args[3]['producer'] = {'asar_sha256': asar, 'member_sha256': member}
                with self.assertRaises(self.config.ConfigTransitionRefusal):
                    self.config.validate_config_transition(*args)

    def test_partial_current_producer_cannot_authorize_relation(self):
        for producer in ({}, {'asar_sha256': self.CURRENT_ASAR},
                         {'member_sha256': self.CURRENT_MEMBER}):
            with self.subTest(producer=producer):
                args = fixture(); args[3]['producer'] = producer
                with self.assertRaises(self.config.ConfigTransitionRefusal):
                    self.config.validate_config_transition(*args)

if __name__ == "__main__":unittest.main(verbosity=2)
