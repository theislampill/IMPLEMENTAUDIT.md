#!/usr/bin/env python3
"""Finite observer controls. Constructed equality is not a host qualification."""
import copy
import hashlib
import json
from pathlib import Path
import types
import unittest

PACKET=Path(__file__).resolve().parents[1]/'packet'

class RuntimePreflightCases(unittest.TestCase):
    def owner(self):
        path=PACKET/'runtime_preflight.py'
        self.assertTrue(path.is_file(), 'the full-twelve early runtime observer is not implemented')
        module=types.ModuleType('runtime_preflight_controls');module.__file__=str(path)
        exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
        return module

    def constructed(self, owner):
        # Explicitly constructed input to the comparator, no filesystem/host claim.
        return {name:dict(kind='FILE',**copy.deepcopy(pin),capture_sha256=hashlib.sha256(name.encode()).hexdigest(),
                         error_class=None,error_sha256=None) for name,pin in owner.EXPECTED.items()}

    def test_all_twelve_exact_constructed_selectors_pass_comparison(self):
        owner=self.owner();opening=self.constructed(owner)
        value=owner.compare(opening,copy.deepcopy(opening))
        self.assertEqual(value['status'],'MATCH')
        self.assertEqual(len(value['selectors']),12)
        self.assertEqual(owner.public(value),value)

    def test_changed_actual_hash_is_preserved_and_refused(self):
        owner=self.owner();opening=self.constructed(owner);closing=copy.deepcopy(opening)
        name='/lib/x86_64-linux-gnu/libpthread.so.0'
        closing[name]['sha256']='f'*64
        value=owner.compare(opening,closing)
        self.assertEqual(value['status'],'REFUSED')
        actual=next(row for row in value['selectors'] if row['path']==name)
        self.assertEqual(actual['closing']['sha256'],'f'*64)
        self.assertFalse(actual['match']);self.assertEqual(owner.public(value),value)

    def test_identical_bytes_with_changed_physical_capture_refuse(self):
        owner=self.owner();opening=self.constructed(owner);closing=copy.deepcopy(opening)
        closing['/etc/ld.so.cache']['capture_sha256']='0'*64
        self.assertEqual(owner.compare(opening,closing)['status'],'REFUSED')

    def test_missing_and_extra_selector_populations_refuse(self):
        owner=self.owner();original=self.constructed(owner)
        missing=copy.deepcopy(original);missing.pop('/etc/ld.so.cache')
        extra=copy.deepcopy(original);extra['/tmp/unadmitted']=copy.deepcopy(original['/etc/ld.so.cache'])
        for bad in (missing,extra):
            with self.assertRaisesRegex(ValueError,'RUNTIME_SELECTOR_POPULATION'):
                owner.compare(original,bad)

    def test_missing_file_is_preserved_and_refused(self):
        owner=self.owner();opening=self.constructed(owner);closing=copy.deepcopy(opening)
        closing['/etc/ld.so.cache'].update(kind='MISSING',bytes=None,sha256=None,mode=None,resolved=None,link=None)
        value=owner.compare(opening,closing)
        self.assertEqual(value['status'],'REFUSED')
        self.assertEqual(owner.public(value),value)

    def test_public_tamper_cannot_promote_refusal_to_match(self):
        owner=self.owner();opening=self.constructed(owner);closing=copy.deepcopy(opening)
        closing['/etc/ld.so.cache']['sha256']='f'*64
        value=owner.compare(opening,closing);value['status']='MATCH'
        with self.assertRaisesRegex(ValueError,'RUNTIME_PUBLIC_PROJECTION'):
            owner.public(value)

if __name__=='__main__':unittest.main()
