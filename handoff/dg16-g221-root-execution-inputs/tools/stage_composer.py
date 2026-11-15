#!/usr/bin/env python3
"""Advance a composer stage by pinning already-issued inputs. Authority NONE; composer logic is not touched.

The composer (compose.py -> compose-candidate-bound.py -> compose-final-bound.py) is one program whose only differences
between stages are pinned constants. G220's stages differ in exactly these lines (see g220-custody/author/):
  PINS['candidate']               sha256 of the ISSUED candidate seal        (compose -> candidate-bound)
  ACTUAL_REVIEW_SEAL_SHA256       sha256 of the ISSUED review seal           (candidate-bound -> final)
and a successor episode additionally re-pins
  PINS['runtime']                 sha256 of the ISSUED PUBLIC_RUNTIME.json
  PINS['witness']                 sha256 of the host witness root.json (unchanged when the witness is reused)
  ACTUAL_CANDIDATE_MEMBER_COUNT   member_count of the issued candidate seal
Only the constants whose input file is supplied are rewritten; every other byte (including the stage files' mixed
line endings) is preserved.

usage: stage_composer.py --in <composer.py> --out <fresh composer.py>
         [--candidate-seal F] [--runtime F] [--witness F] [--review-seal F]
"""
import argparse, ast, hashlib, json, re
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('--in', dest='source', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
for name in ('candidate-seal', 'runtime', 'witness', 'review-seal'): p.add_argument('--' + name, type=Path)
a = p.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
EOL = b'[^' + bytes([13, 10]) + b']*'          # one physical line, whatever its terminator
text = a.source.read_bytes(); before = sha(text); report = {}


def assign(source, name, render):
    pattern = re.compile(b'(?m)^' + name.encode() + b' = (' + EOL + b')')
    found = pattern.findall(source)
    assert len(found) == 1, 'ASSIGNMENT_' + name
    match = pattern.search(source)
    return source[:match.start(1)] + render(match.group(1).decode()).encode() + source[match.end(1):]


def pins(old):
    value = ast.literal_eval(old)
    assert repr(value) == old, 'PINS_LINE_NOT_REPR_STABLE'
    for key, path in (('candidate', a.candidate_seal), ('runtime', a.runtime), ('witness', a.witness)):
        if path is not None: value[key] = sha(path.read_bytes()); report['PINS.' + key] = value[key]
    return repr(value)


def constant(name, value):
    report[name] = value
    return lambda old: repr(value)


text = assign(text, 'PINS', pins)
if a.candidate_seal is not None:
    text = assign(text, 'ACTUAL_CANDIDATE_MEMBER_COUNT', constant('ACTUAL_CANDIDATE_MEMBER_COUNT', json.loads(a.candidate_seal.read_bytes())['member_count']))
if a.review_seal is not None:
    text = assign(text, 'ACTUAL_REVIEW_SEAL_SHA256', constant('ACTUAL_REVIEW_SEAL_SHA256', sha(a.review_seal.read_bytes())))
ast.parse(text)
with a.out.open('xb') as handle: handle.write(text)
print(json.dumps(dict(authority='NONE', before=before, after=sha(text), out=str(a.out), pinned=report), indent=1))
