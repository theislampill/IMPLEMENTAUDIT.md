"""Constructed controls for finite profiles and actual core inventory logic.

These are not native host observations or programme awards.
"""
import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

PACKET = Path(__file__).resolve().parents[1] / 'packet'
OLD_GIT = '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'
NEW_GIT = '08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801'
PYTHON = 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'
BWRAP = '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'


def load(name):
    spec = importlib.util.spec_from_file_location('successor_' + name, PACKET / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FiniteProfiles(unittest.TestCase):
    def setUp(self):
        self.owner = load('host_utility')
        self.core = load('run')

    def facts(self, image):
        facts = copy.deepcopy(self.owner.G1_HOST_PROFILES[0]['facts'])
        facts['image_version'] = image
        return facts

    def inventory(self, image, git_sha, bwrap_sha=BWRAP):
        pins = {'python3.12': PYTHON, 'git': git_sha, 'bash': 'b' * 64, 'bwrap': bwrap_sha}
        owner = SimpleNamespace(
            G1_HOST_PROFILES=self.owner.G1_HOST_PROFILES,
            g1_profile_from_inventory=self.owner.g1_profile_from_inventory,
            validate_g1_profile_binding=lambda *args: None,
            trusted=lambda name: ('/usr/bin/' + name, {'sha256': pins[name]}))
        state = {'context': {}, 'host_profile_binding': {}, 'host_observations': []}
        with patch.multiple(self.core.os, getuid=lambda: 0, geteuid=lambda: 0,
                            getgid=lambda: 0, getegid=lambda: 0,
                            uname=lambda: SimpleNamespace(machine='x86_64', release='test-only')):
            with patch.dict(self.core.os.environ, {'ImageOS': 'ubuntu24', 'ImageVersion': image}):
                with patch.object(self.core.sys, 'version_info', (3, 12, 3)), \
                     patch.object(self.core.sys, 'executable', '/usr/bin/python3.12'), \
                     patch.object(self.core, 'read_regular', return_value=b'ID=ubuntu\nVERSION_ID="24.04"\n'), \
                     patch.object(self.core, 'read_boot_identity', return_value=b'12345678-1234-1234-1234-123456789abc\n'), \
                     patch.object(self.core.resource, 'getrlimit', return_value=(4096, 4096)):
                    return self.core.inventory(state, owner)

    def test_old_profiles_and_old_git_remain_valid(self):
        self.assertEqual(len(self.owner.G1_HOST_PROFILES), 5)
        for image in ('20261101.360.1', '20261111.370.1', '20261111.127.1'):
            with self.subTest(image=image):
                self.owner.validate_g1_host_profile(self.owner.select_g1_host_profile(self.facts(image)))
                self.inventory(image, OLD_GIT)

    def test_current_finite_profiles_select_and_match_actual_git_pin(self):
        for image in ('20261116.133.1', '20261116.376.1'):
            with self.subTest(image=image):
                selected = self.owner.select_g1_host_profile(self.facts(image))
                self.assertEqual(selected['facts']['image_version'], image)
                self.assertFalse(selected['native_qualification'])
                self.inventory(image, NEW_GIT)

    def test_old_git_refuses_under_current_profiles(self):
        for image in ('20261116.133.1', '20261116.376.1'):
            with self.subTest(image=image), self.assertRaisesRegex(Exception, 'SELECTED_TOOL_BYTES_CHANGED'):
                self.inventory(image, OLD_GIT)

    def test_current_git_does_not_rewrite_historical_profiles(self):
        with self.assertRaisesRegex(Exception, 'SELECTED_TOOL_BYTES_CHANGED'):
            self.inventory('20261111.370.1', NEW_GIT)

    def test_unknown_image_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'HOST_PROFILE_CHANGED'):
            self.inventory('20261116.999.1', NEW_GIT)

    def test_wrong_python_privilege_and_tool_bytes_are_refused(self):
        for name, value in (('uid', 1000), ('euid', False), ('python_version', [3, 12, 4])):
            facts = self.facts('20261116.133.1'); facts[name] = value
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, 'HOST_PROFILE_CHANGED'):
                self.owner.select_g1_host_profile(facts)
        with self.assertRaisesRegex(Exception, 'SELECTED_TOOL_BYTES_CHANGED'):
            self.inventory('20261116.133.1', '0' * 64)
        with self.assertRaisesRegex(Exception, 'LAUNCHER_BYTES_CHANGED'):
            self.inventory('20261116.133.1', NEW_GIT, '0' * 64)


if __name__ == '__main__':
    unittest.main(verbosity=2)
