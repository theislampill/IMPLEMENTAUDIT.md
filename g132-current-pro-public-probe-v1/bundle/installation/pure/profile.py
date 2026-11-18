# Exact bounded source projection; source module is never imported.
G1_HOST_PROFILES = ({'id': 'G1_UBUNTU24_20261101_360_1', 'facts': {'platform': 'linux', 'architecture': 'x86_64', 'os': {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'python_version': [3, 12, 3], 'image_os': 'ubuntu24', 'uid': 0, 'euid': 0, 'gid': 0, 'egid': 0, 'image_version': '20261101.360.1'}, 'core_tool_sha256': {'python3.12': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f', 'git': '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235', 'bwrap': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}}, {'id': 'G1_UBUNTU24_20261111_370_1', 'facts': {'platform': 'linux', 'architecture': 'x86_64', 'os': {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'python_version': [3, 12, 3], 'image_os': 'ubuntu24', 'uid': 0, 'euid': 0, 'gid': 0, 'egid': 0, 'image_version': '20261111.370.1'}, 'core_tool_sha256': {'python3.12': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f', 'git': '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235', 'bwrap': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}}, {'id': 'G1_UBUNTU24_20261111_127_1', 'facts': {'platform': 'linux', 'architecture': 'x86_64', 'os': {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'python_version': [3, 12, 3], 'image_os': 'ubuntu24', 'uid': 0, 'euid': 0, 'gid': 0, 'egid': 0, 'image_version': '20261111.127.1'}, 'core_tool_sha256': {'python3.12': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f', 'git': '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235', 'bwrap': '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'}})

def _g1_profile_need(condition):
    if not condition:raise ValueError('HOST_PROFILE_CHANGED')

def g1_host_policy_sha256():
    return sha((json.dumps(G1_HOST_PROFILES,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())

def select_g1_host_profile(facts):
    _g1_profile_need(type(facts) is dict and len(G1_HOST_PROFILES) == 3 and (len({row['id'] for row in G1_HOST_PROFILES}) == 3))
    keys = set(G1_HOST_PROFILES[0]['facts'])
    _g1_profile_need(set(facts) == keys and all((set(row['facts']) == keys for row in G1_HOST_PROFILES)))
    _g1_profile_need(type(facts['python_version']) is list and len(facts['python_version']) == 3 and all(type(v) is int for v in facts['python_version']))
    matches = [row for row in G1_HOST_PROFILES if all((type(facts[k]) is type(v) and facts[k] == v for k, v in row['facts'].items()))]
    _g1_profile_need(len(matches) == 1)
    return dict(schema='dg16.g1-finite-host-profile-selection.v1', authority='NONE', policy_sha256=g1_host_policy_sha256(), profile_id=matches[0]['id'], facts=json.loads(json.dumps(facts)), runtime_byte_qualification='DEFERRED_TO_EXISTING_CORE_INVENTORY_AND_C5_OWNER', native_qualification=False, original_awards=[])

def validate_g1_host_profile(value):
    _g1_profile_need(type(value) is dict and set(value) == {'schema', 'authority', 'policy_sha256', 'profile_id', 'facts', 'runtime_byte_qualification', 'native_qualification', 'original_awards'})
    selected = select_g1_host_profile(value['facts'])
    _g1_profile_need(json.dumps(value, sort_keys=True, allow_nan=False) == json.dumps(selected, sort_keys=True, allow_nan=False))
    return selected
