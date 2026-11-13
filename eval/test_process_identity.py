#!/usr/bin/env python3
"""Process identity regressions: real owned processes and explicit read faults.

The live controls derive their expected birth from the process's own /proc/self
view. Fault controls substitute one read boundary; they do not claim an actual
PID recycle, namespace transition, or kernel fault occurred.
"""
from __future__ import annotations

import contextlib
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

import reconcile


def own_birth():
    raw = Path('/proc/self/stat').read_text()
    ticks = int(raw.rsplit(') ', 1)[1].split()[19])
    boot = next(int(line.split()[1]) for line in
                Path('/proc/stat').read_text().splitlines()
                if line.startswith('btime '))
    return round(boot + ticks / os.sysconf('SC_CLK_TCK'), 2)


@contextlib.contextmanager
def live_child():
    # EOF is the normal shutdown; the timeout is a child-owned final fallback.
    # These controls never signal an arbitrary numeric PID.
    code = '''import json, os, pathlib, select, sys
raw = pathlib.Path('/proc/self/stat').read_text()
ticks = int(raw.rsplit(') ', 1)[1].split()[19])
boot = next(int(x.split()[1]) for x in pathlib.Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
ns = os.stat('/proc/self/ns/pid')
print(json.dumps(dict(pid=os.getpid(), birth=round(boot + ticks / os.sysconf('SC_CLK_TCK'), 2), namespace=[ns.st_dev, ns.st_ino])), flush=True)
select.select([sys.stdin], [], [], 10)
'''
    child = subprocess.Popen([sys.executable, '-c', code], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    try:
        row = json.loads(child.stdout.readline())
        if row['pid'] != child.pid:
            raise AssertionError('owned child did not report its local PID')
        yield child, row
    finally:
        child.stdin.close()
        child.wait(timeout=12)
        child.stdout.close()
        child.stderr.close()


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux proc/pidfd controls')
class ProcessIdentityControls(unittest.TestCase):
    def test_actual_self_birth_uses_own_proc_identity(self):
        expected = own_birth()
        self.assertEqual(reconcile.process_creation_time(os.getpid()), expected)
        record = reconcile.process_identity(os.getpid())
        self.assertEqual(record['process_creation_time'], expected)
        self.assertEqual(reconcile.original_process_alive(record), (True, 'alive'))

    def test_actual_owned_live_child_birth_and_exit(self):
        with live_child() as (child, actual):
            self.assertEqual(reconcile.process_creation_time(child.pid), actual['birth'])
            record = reconcile.process_identity(child.pid)
            self.assertEqual(reconcile.original_process_alive(record), (True, 'alive'))
            self.assertIsNone(child.poll())
        self.assertIsNone(reconcile.process_creation_time(child.pid))
        self.assertFalse(reconcile.original_process_alive(record)[0])

    def test_nearby_but_different_recorded_birth_is_not_original(self):
        record = reconcile.process_identity(os.getpid())
        self.assertIsNotNone(record['process_creation_time'])
        record['process_creation_time'] += .5
        self.assertFalse(reconcile.original_process_alive(record)[0])

    def test_nonfinite_or_boolean_birth_is_not_original(self):
        record = reconcile.process_identity(os.getpid())
        for value in (float('nan'), float('inf'), True):
            with self.subTest(value=value):
                self.assertFalse(reconcile.original_process_alive(
                    dict(record, process_creation_time=value))[0])

    def test_different_actual_pidfd_is_rejected_without_effect(self):
        with live_child() as (child, _):
            actual_open = os.pidfd_open
            with mock.patch.object(os, 'pidfd_open',
                                   side_effect=lambda _pid, flags=0:
                                   actual_open(child.pid, flags)):
                self.assertIsNone(reconcile.process_creation_time(os.getpid()))
            self.assertIsNone(child.poll())

    def test_namespace_disagreement_is_unreadable(self):
        observe = getattr(reconcile, '_proc_snapshot', None)

        def changed(path):
            snapshot = observe(path)
            if path != '/proc/self':
                snapshot = dict(snapshot, namespace=(snapshot['namespace'][0],
                                                     snapshot['namespace'][1] + 1))
            return snapshot

        with mock.patch.object(reconcile, '_proc_snapshot', side_effect=changed,
                               create=True):
            self.assertIsNone(reconcile.process_creation_time(os.getpid()))

    def test_disappearance_during_identity_read_is_unreadable(self):
        observe = getattr(reconcile, '_proc_snapshot', None)

        def disappeared(path):
            if path != '/proc/self':
                raise ProcessLookupError(errno.ESRCH, 'explicit disappearance fixture')
            return observe(path)

        with mock.patch.object(reconcile, '_proc_snapshot', side_effect=disappeared,
                               create=True):
            self.assertIsNone(reconcile.process_creation_time(os.getpid()))

    def test_start_tick_change_between_bookends_is_unreadable(self):
        read = getattr(reconcile, '_read_proc_member', None)
        count = 0

        def changed(fd, name):
            nonlocal count
            raw = read(fd, name)
            if name == 'stat':
                count += 1
                if count == 2:
                    head, rest = raw.rsplit(b') ', 1)
                    fields = rest.split()
                    fields[19] = str(int(fields[19]) + 1).encode()
                    return head + b') ' + b' '.join(fields)
            return raw

        with mock.patch.object(reconcile, '_read_proc_member', side_effect=changed,
                               create=True):
            self.assertIsNone(reconcile.process_creation_time(os.getpid()))

    def test_ambiguous_pidfd_fields_are_unreadable(self):
        read = getattr(reconcile, '_pidfd_fields', None)

        def ambiguous(fd):
            row = read(fd)
            return dict(row, Pid=row['Pid'] * 2)

        with mock.patch.object(reconcile, '_pidfd_fields', side_effect=ambiguous,
                               create=True):
            self.assertIsNone(reconcile.process_creation_time(os.getpid()))

    def test_missing_pidfd_support_is_unreadable(self):
        with mock.patch.object(os, 'pidfd_open',
                               side_effect=OSError(errno.ENOSYS, 'explicit unavailable fixture')):
            self.assertIsNone(reconcile.process_creation_time(os.getpid()))

    def test_repeated_lookup_closes_all_descriptors(self):
        before = sorted(os.listdir('/proc/self/fd'))
        for _ in range(3):
            self.assertEqual(reconcile.process_creation_time(os.getpid()), own_birth())
        self.assertEqual(sorted(os.listdir('/proc/self/fd')), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
