import json

def selected_profile(base):
    selected = json.loads((base / 'config' / 'selection.json').read_text())['profile']
    profiles = json.loads((base / 'config' / 'profiles.json').read_text())
    return {'name': selected, **profiles[selected]}
