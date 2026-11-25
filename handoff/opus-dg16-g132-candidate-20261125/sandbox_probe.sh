# Disposable proof: fixed openssl cms encryption inside a bwrap sandbox restricted to the three held fds.
set -u
B=/home/agent/opus-tmp/confine-proof; rm -rf $B; mkdir -p $B; cd $B; umask 077
openssl req -x509 -newkey rsa:3072 -nodes -keyout k.pem -out c.pem -subj /CN=disposable -days 1 2>/dev/null
head -c 4096 /dev/urandom > plain.bin; : > cipher.der
SB=(/usr/bin/bwrap --unshare-all --die-with-parent --new-session --clearenv --cap-drop ALL
    --ro-bind /usr /usr --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/bin /bin
    --proc /proc --dev /dev --tmpfs /tmp --setenv PATH /usr/bin:/bin --setenv LC_ALL C --setenv OPENSSL_CONF /dev/null)
echo "== probes inside the sandbox"
"${SB[@]}" /bin/sh -c 'id; grep -E "NoNewPrivs|CapEff" /proc/self/status; ls /var/run/docker.sock 2>&1 | head -1; ls /etc 2>&1 | head -1; sudo -n true 2>&1 | head -1; cat /proc/net/route 2>/dev/null | wc -l; ls /home 2>&1 | head -1' 3<plain.bin
echo "== encryption with held fds 3,4,5"
"${SB[@]}" /usr/bin/openssl cms -encrypt -binary -aes-256-gcm -in /proc/self/fd/3 -outform DER -out /proc/self/fd/5 -recip /proc/self/fd/4 \
  -keyopt rsa_padding_mode:oaep -keyopt rsa_oaep_md:sha256 -keyopt rsa_mgf1_md:sha256 3<plain.bin 4<c.pem 5>>cipher.der
echo "rc=$?"
openssl cms -decrypt -binary -inform DER -in cipher.der -inkey k.pem -recip c.pem > dec.bin 2>/dev/null && cmp -s dec.bin plain.bin && echo "cipher $(stat -c %s cipher.der) bytes decrypts to plaintext: yes"
echo "bwrap $(sha256sum /usr/bin/bwrap | cut -c1-16) $(bwrap --version)"
