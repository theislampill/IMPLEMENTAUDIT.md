"""Verify and reassemble the checkpoint's bounded archive parts; never extract."""
from pathlib import Path
import hashlib
import json


def digest(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    for archive in manifest['archives']:
        name = archive['name']
        assert Path(name).name == name, name
        parts = archive.get('transport_parts', [])
        if not parts:
            raw = (root / name).read_bytes()
        else:
            content = []
            for part in parts:
                assert Path(part['name']).name == part['name'], part['name']
                piece = (root / part['name']).read_bytes()
                assert digest(piece) == {k: part[k] for k in ('bytes', 'sha256')}, part['name']
                content.append(piece)
            raw = b''.join(content)
        assert digest(raw) == {k: archive[k] for k in ('bytes', 'sha256')}, name
        destination = root / name
        if parts and not destination.exists():
            with destination.open('xb') as stream:
                stream.write(raw)
        else:
            assert destination.read_bytes() == raw, name
        print(name, len(raw), hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    main()
