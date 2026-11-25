"""Probe-input tests for compare_v2 rules (2)-(6) and the admission model. Usage: python -I test_compare_v2.py DIR"""
import hashlib
import importlib.util
import sys
import unittest

spec = importlib.util.spec_from_file_location('compare_v2', sys.argv.pop(1) + '/compare_v2.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

OWNER = b'owner-bytes\n'
TRANSPORT = b'transport\n'
BLOBS = {'scripts/operational-evidence.py': OWNER, 'scripts/work-graph-continuity-transport.py': TRANSPORT}


def run(old, new, role='compiler', blobs=BLOBS):
    rep, fa, fb = C.analyze(role, old.encode(), new.encode(), blobs.get)
    return rep, fa, fb


def table(src, name='X'):
    return C.Facts(C.ast.parse(src)).table(name)[0]


class Pins(unittest.TestCase):
    def test_verified_and_labelled(self):
        sha = hashlib.sha256(OWNER).hexdigest()
        rep, _, _ = run("_NATIVE_STATIC_OWNER_SHA256 = 'aa'\n_NATIVE_STATIC_OWNER_BYTES = 1\n",
                        f"_NATIVE_STATIC_OWNER_SHA256 = '{sha}'\n_NATIVE_STATIC_OWNER_BYTES = {len(OWNER)}\n")
        d = rep['differences']
        self.assertEqual([x['pin'] for x in d], ['pin_to:scripts/operational-evidence.py'] * 2)
        self.assertEqual([x['pin_verified'] for x in d], [True, True])

    def test_mismatch_flagged(self):
        rep, _, _ = run("_NATIVE_CONTINUITY_TRANSPORT_BYTES = 1\n", "_NATIVE_CONTINUITY_TRANSPORT_BYTES = 2\n")
        x = rep['differences'][0]
        self.assertTrue(x['owner_pin'])
        self.assertEqual(x['pin'], 'pin_to:scripts/work-graph-continuity-transport.py')
        self.assertIs(x['pin_verified'], False)
        self.assertEqual(x['pin_detail']['actual'], len(TRANSPORT))

    def test_missing_blob_not_verified(self):
        rep, _, _ = run("_NATIVE_STATIC_OWNER_BYTES = 1\n", "_NATIVE_STATIC_OWNER_BYTES = 2\n", blobs={})
        self.assertIs(rep['differences'][0]['pin_verified'], False)

    def test_other_constants_are_constant_only(self):
        rep, _, _ = run("_FOO_SHA256 = 'a'\nLIMIT_BYTES = 5\nN = 1\n", "_FOO_SHA256 = 'b'\nLIMIT_BYTES = 6\nN = 2\n")
        self.assertEqual(len(rep['differences']), 3)
        for x in rep['differences']:
            self.assertTrue(x['constant_only'])
            self.assertFalse(x['owner_pin'])
            self.assertIsNone(x['pin'])

    def test_allow_list_is_role_scoped(self):
        rep, _, _ = run("_NATIVE_STATIC_OWNER_BYTES = 1\n", "_NATIVE_STATIC_OWNER_BYTES = 2\n", role='receiver')
        self.assertFalse(rep['differences'][0]['owner_pin'])


class Tables(unittest.TestCase):
    def test_supported_forms(self):
        self.assertEqual(table("X = {'a': 1}\nX['b'] = 2\n"), {'a': 1, 'b': 2})
        self.assertEqual(table("X = (1,)\nX += (2, 3)\n"), [1, 2, 3])

    def test_name_resolution(self):
        self.assertEqual(table("K = 'k'\nV = 2 * 3\nX = {K: V}\n"), {'k': 6})
        self.assertIsNone(table("K = 'k'\nK = 'j'\nX = {K: 1}\n"))
        self.assertIsNone(table("X = {K: 1}\n"))
        self.assertIsNone(table("import os\nX = {os.sep: 1}\n"))

    def test_unsupported_writes_make_unknown(self):
        for src in ("X = (1,)\nX = X + (2,)\n",
                    "X = {}\nX.update({'a': 1})\n",
                    "X = []\nX.append(1)\n",
                    "X = []\nX.extend([1])\n",
                    "X = {'a': 1}\ndel X['a']\n",
                    "X = {'a': 1}\ndel X\n",
                    "Y = {'a': 1}\nX = {**Y}\n",
                    "X = {}\ndef f():\n    X['a'] = 1\n",
                    "X = {}\ndef f():\n    global X\n    X = {}\n",
                    "X = {}\ndef f():\n    X = 1\n",
                    "X = ()\nX, Y = (1,), 2\n",
                    "X = ()\nX: tuple = ()\n",
                    "X = ()\nif (X := (1,)):\n    pass\n",
                    "X = ()\nfor X in []:\n    pass\n",
                    "X = {}\nX.setdefault('a', 1)\n",
                    "X = {}\nsetattr(sys, 'X', 1)\n",
                    "X = ()\nX *= 2\n",
                    "X = (1, *Y)\n",
                    "X = {}\nexec('X = 1')\n",
                    "X = {}\nexec('X = 1', globals())\n",
                    "X = {}\nglobals()['X'] = 1\n",
                    "X = {}\nsetattr(sys.modules[__name__], 'X', 1)\n",
                    "X = {}\nsetattr(m, n, 1)\n"):
            with self.subTest(src=src):
                self.assertIsNone(table(src))

    def test_exec_into_other_module_kept(self):
        src = "X = {'a': 1}\ndef load(m, raw):\n    exec(compile(raw, 'p', 'exec'), m.__dict__)\n"
        self.assertEqual(table(src), {'a': 1})
        calls = C.Facts(C.ast.parse(src)).dynamic_calls()
        self.assertEqual([(c['call'], c['writes_this_module']) for c in calls], [('exec', False)])

    def test_readonly_use_kept(self):
        self.assertEqual(table("X = {'a': 1}\ndef f():\n    return X.get('a'), max(X.values())\n"), {'a': 1})

    def test_effect_report(self):
        rep, _, _ = run("X = {'a': 1}\nX['b'] = 2\n", "X = {'a': 1, 'b': 2, 'c': 3}\n")
        e = rep['table_effects']['X']
        self.assertEqual((e['old_entries'], e['new_entries'], e['added'], e['removed'], e['changed']), (2, 3, 1, 0, 0))
        rep, _, _ = run("X = {'a': 1}\n", "X = {'a': 1}\nX.update(b=2)\n")
        self.assertEqual(rep['table_effects']['X']['status'], 'UNKNOWN')


NT_OLD = "{imp}def f(p):\n    if os.name == 'nt' and p == 1:\n        return 1\n    return 0\n{tail}"
NT_NEW = "{imp}def f(p):\n    if os.name == 'nt' and p in (1, 2):\n        return 1\n    return 0\n{tail}"


class Windows(unittest.TestCase):
    def nt(self, imp='import os\n', tail=''):
        rep, _, _ = run(NT_OLD.format(imp=imp, tail=tail), NT_NEW.format(imp=imp, tail=tail), role='receiver')
        return rep

    def test_label_with_assumptions(self):
        rep = self.nt()
        self.assertTrue(rep['differences'][0]['windows_only'])
        self.assertTrue(rep['os_assumptions']['new']['holds'])
        self.assertEqual(len(rep['os_assumptions']['new']['assumptions']), 3)

    def test_refused(self):
        for imp, tail in (('', ''), ('import os\n', 'os = None\n'), ('import os\n', "os.name = 'nt'\n"),
                          ('import sys as os\n', ''), ('import os\nfrom x import os\n', ''),
                          ('import os\n', "setattr(os, 'name', 'nt')\n"), ('import os\n', 'def g(os):\n    pass\n')):
            with self.subTest(imp=imp, tail=tail):
                rep = self.nt(imp, tail)
                x = [d for d in rep['differences'] if 'If' in d['path']][0]
                self.assertFalse(x['windows_only'])
                self.assertTrue(x['windows_label_refused'])

    def test_nt_body(self):
        rep, _, _ = run("import os\nif os.name == 'nt':\n    A = 1\n", "import os\nif os.name == 'nt':\n    A = 2\n",
                        role='receiver')
        self.assertTrue(rep['differences'][0]['windows_only'])

    def test_non_nt_not_windows(self):
        rep, _, _ = run("import os\nif os.name == 'posix':\n    A = 1\n", "import os\nif os.name == 'posix':\n    A = 2\n",
                        role='receiver')
        self.assertFalse(rep['differences'][0]['windows_only'])


class Paths(unittest.TestCase):
    def test_unnamed_index_and_digest(self):
        rep, _, _ = run("A = 1\nprint(1)\n", "A = 1\nprint(2)\nprint(3)\n")
        paths = [d['path'] for d in rep['differences']]
        self.assertTrue(all('@' in p and '#' in p for p in paths), paths)
        self.assertIn('/Expr@1>1#', paths[0])
        self.assertTrue(paths[1].startswith('/Expr@2#'))


class Admission(unittest.TestCase):
    FN = ("import os\n"
          "def _native_check_continuity_closure_v1(value, repository, compiler_path, pair):\n"
          "    helper_pair = (pair.get('claim_sha256'), pair.get('validate_sha256'))\n"
          "    profiles = tuple(profile for profile in _NATIVE_CONTINUITY_SOURCE_PROFILES_V1\n"
          "                     if (profile[0][2], profile[1][2]) == helper_pair)\n"
          "    windows = profiles[0][0][3] is None\n"
          "    if windows and os.name != 'nt':\n"
          "        raise SystemExit\n")

    def test_row_order(self):
        old = "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 = (((0, 0, 'a', 1), (0, 0, 'b', 1)),)\n" + self.FN
        new = old + ("_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 += (((0, 0, 'c', 1), (0, 0, 'd', 1)),)\n"
                     "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 += (((0, 0, 'e', None), (0, 0, 'f', None)),)\n")
        _, fa, fb = run(old, new, role='receiver')
        adm = C.admission_model(fa, fb)
        self.assertEqual((adm['added_pairs'], adm['added_linux_admitted']), (2, 1))
        self.assertEqual(adm['added_windows_only_by_row_order'], [['e', 'f']])
        new2 = old + ("_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 += (((0, 0, 'e', 1), (0, 0, 'f', 1)),)\n"
                      "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 += (((0, 0, 'e', None), (0, 0, 'f', None)),)\n")
        _, fa, fb = run(old, new2, role='receiver')
        adm = C.admission_model(fa, fb)
        self.assertEqual((adm['added_pairs'], adm['added_linux_admitted']), (1, 1))
        self.assertEqual(adm['added_windows_only_by_row_order'], [])

    def test_profile_added_to_existing_windows_pair(self):
        old = "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 = (((0, 0, 'e', None), (0, 0, 'f', None)),)\n" + self.FN
        new = old + "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 += (((1, 1, 'e', None), (1, 1, 'f', None)),)\n"
        _, fa, fb = run(old, new, role='receiver')
        adm = C.admission_model(fa, fb)
        self.assertEqual((adm['added_profiles'], adm['added_pairs']), (1, 0))
        r = adm['added_profiles_to_existing_pairs'][0]
        self.assertEqual((r['new_profile_index'], r['first_profile_index'], r['linux_admitted']), (1, 0, False))
        self.assertIn('row order', r['note'])

    def test_model_mismatch_unknown(self):
        src = "_NATIVE_CONTINUITY_SOURCE_PROFILES_V1 = ()\n" + self.FN.replace('is None', 'is not None')
        _, fa, fb = run(src, src, role='receiver')
        self.assertEqual(C.admission_model(fa, fb)['status'], 'UNKNOWN')


class Report(unittest.TestCase):
    def test_fields(self):
        self.assertIn('not effect equality', C.EQUIVALENCE_NOTE)
        f = C.Facts(C.ast.parse('NATIVE_SOURCE_MAX_FILE_BYTES = 256 * 1024\n'))
        self.assertEqual(C.size_bounds(f, f)['new']['NATIVE_SOURCE_MAX_FILE_BYTES'], 262144)
        rep, _, _ = run('A = 1\n', 'A = 1\n')
        self.assertTrue(rep['byte_equal'] and rep['ast_equal'] and rep['differences'] == [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
