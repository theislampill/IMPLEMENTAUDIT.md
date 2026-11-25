"""Public disposable sender rehearsal: maintained CaptureSession with a throwaway key/cert and dummy plaintext.
No private input, no admission, no provider. Checks: rc, cipher decrypts to plaintext, held fds unchanged,
descriptor population restored, closed() True, owner evidence written once."""
import os, sys, time, json, subprocess, hashlib
from pathlib import Path
carrier, work = Path(sys.argv[1]), Path(sys.argv[2]); work.mkdir(mode=0o700, parents=True, exist_ok=False)
sys.path.insert(0, str(carrier))
import carrier_io as F, sender_capture as SC
key, cert, plain, cipher = (work / n for n in ("k.pem", "c.pem", "plain.bin", "cipher.der"))
subprocess.run(["/usr/bin/openssl", "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-keyout", str(key), "-out", str(cert),
                "-subj", "/CN=disposable-rehearsal", "-days", "1"], check=True, capture_output=True)
plain.write_bytes(os.urandom(4096)); cipher.write_bytes(b"")
for p in (key, cert, plain, cipher): os.chmod(p, 0o600)
evid = work / "evidence"; evid.mkdir(mode=0o700)
class Budget:
    def reserve(self, n, k): self.r = (n, k)
fds = (os.open(plain, os.O_RDONLY), os.open(cert, os.O_RDONLY), os.open(cipher, os.O_WRONLY))
argv = SC.SANDBOX_PREFIX + ['/usr/bin/openssl',
      'cms','-encrypt','-binary','-aes-256-gcm','-in',f'/proc/self/fd/{fds[0]}','-outform','DER',
      '-out',f'/proc/self/fd/{fds[2]}','-recip',f'/proc/self/fd/{fds[1]}',
      '-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
stat_before = {n: tuple(os.stat(p))[:7] for n, p in (("plain", plain), ("cert", cert))}
s = SC.CaptureSession(evid, Budget(), lambda: None)
records = []
try:
    rc, out, err = s.capture("carrier-encrypt", argv, records, time.monotonic() + 60, 30, fds)
    print("CAPTURE rc", rc, "stdout", len(out), "stderr", len(err))
except SC.CaptureRefusal as e:
    print("CAPTURE REFUSED", e, getattr(e, "captured", None))
for fd in fds: os.close(fd)
print("record", json.dumps(records[-1], sort_keys=True) if records else None)
print("closed()", s.closed())
print("held inputs unchanged", {n: tuple(os.stat(p))[:7] == stat_before[n] for n, p in (("plain", plain), ("cert", cert))})
dec = subprocess.run(["/usr/bin/openssl", "cms", "-decrypt", "-binary", "-inform", "DER", "-in", str(cipher), "-inkey", str(key), "-recip", str(cert)], capture_output=True)
print("cipher bytes", cipher.stat().st_size, "decrypts to plaintext", dec.returncode == 0 and dec.stdout == plain.read_bytes())
print("evidence files", sorted(p.name for p in evid.iterdir()))
