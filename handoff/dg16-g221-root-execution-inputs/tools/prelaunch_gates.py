#!/usr/bin/env python3
"""Read-only pre-launch gates for one host publication. Authority NONE; it publishes nothing and grants nothing.

  1. REFS ABSENT       neither the host branch nor the control branch exists on the remote (git ls-remote, read-only).
  2. RECIPIENT VALID   the PUBLIC certificate is inside its validity period now, and is exactly one CERTIFICATE block.
  3. LAUNCH MARGIN     latest_job_start = notAfter - job_minutes (G220 ADMISSION.json: 14:51:46Z - 270 min = 10:21:46Z).
                       The gate requires  latest_job_start - now >= margin_seconds  (default 420, the
                       effective_prework_seconds of the host capability intent in protected_preflight.py), so the
                       capability pre-work budget still fits before the last admissible job start.
A PASS here is an observation for Root's admission record; it is not the admission.

usage: prelaunch_gates.py --host-branch B --control-branch B --recipient-cert PEM
         [--remote URL] [--job-minutes 270] [--margin-seconds 420] [--now 2026-11-15T09:00:00Z] [--skip-remote] [--out FILE]
Requires: git (unless --skip-remote) and openssl on PATH. Exit status 0 only when every evaluated gate passes.
"""
import argparse, datetime, hashlib, json, subprocess, sys
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('--host-branch', required=True); p.add_argument('--control-branch', required=True)
p.add_argument('--recipient-cert', type=Path, required=True)
p.add_argument('--remote', default='https://github.com/theislampill/IMPLEMENTAUDIT.md.git')
p.add_argument('--job-minutes', type=int, default=270); p.add_argument('--margin-seconds', type=int, default=420)
p.add_argument('--now'); p.add_argument('--skip-remote', action='store_true'); p.add_argument('--out', type=Path)
a = p.parse_args()
utc = datetime.timezone.utc
now = datetime.datetime.strptime(a.now, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc) if a.now else datetime.datetime.now(utc).replace(microsecond=0)
iso = lambda t: t.strftime('%Y-%m-%dT%H:%M:%SZ')
gates = []


def gate(name, ok, detail): gates.append(dict(gate=name, ok=bool(ok), detail=detail)); print('%s  %s :: %s' % ('PASS' if ok else 'FAIL', name, json.dumps(detail, sort_keys=True)))


if a.skip_remote:
    gates.append(dict(gate='REFS_ABSENT', ok=None, detail='NOT EVALUATED (--skip-remote)')); print('SKIP  REFS_ABSENT :: not evaluated')
else:
    refs = ['refs/heads/' + a.host_branch, 'refs/heads/' + a.control_branch]
    run = subprocess.run(['git', 'ls-remote', '--heads', a.remote, *refs], capture_output=True, text=True, timeout=60)
    found = [line.split('\t')[1] for line in run.stdout.splitlines() if '\t' in line]
    gate('REFS_ABSENT', run.returncode == 0 and not found, dict(remote=a.remote, queried=refs, found=found, exit=run.returncode))
cert = a.recipient_cert.read_bytes()
shape = cert.count(b'-----BEGIN CERTIFICATE-----') == 1 and cert.count(b'-----BEGIN') == 1 and b'PRIVATE' not in cert and len(cert) <= 8192
dates = subprocess.run(['openssl', 'x509', '-noout', '-startdate', '-enddate'], input=cert, capture_output=True, timeout=30)
fields = dict(line.split('=', 1) for line in dates.stdout.decode().splitlines() if '=' in line)
when = lambda text: datetime.datetime.strptime(text.strip(), '%b %d %H:%M:%S %Y %Z').replace(tzinfo=utc)
if dates.returncode != 0 or not shape:
    gate('RECIPIENT_VALID', False, dict(openssl_exit=dates.returncode, one_public_certificate_block=shape))
else:
    start, end = when(fields['notBefore']), when(fields['notAfter'])
    latest = end - datetime.timedelta(minutes=a.job_minutes)
    gate('RECIPIENT_VALID', start <= now < end, dict(sha256=hashlib.sha256(cert).hexdigest(), bytes=len(cert), not_before=iso(start), not_after=iso(end), now=iso(now)))
    gate('LAUNCH_MARGIN', (latest - now).total_seconds() >= a.margin_seconds,
         dict(latest_job_start=iso(latest), job_minutes=a.job_minutes, seconds_until_latest_job_start=int((latest - now).total_seconds()), required_margin_seconds=a.margin_seconds))
result = dict(authority='NONE', observed_utc=iso(now), host_branch=a.host_branch, control_branch=a.control_branch, gates=gates,
              all_evaluated_gates_pass=all(g['ok'] for g in gates if g['ok'] is not None))
if a.out: a.out.write_text(json.dumps(result, indent=1) + '\n')
sys.exit(0 if result['all_evaluated_gates_pass'] else 1)
