from pathlib import Path
import argparse,hashlib,json,os,sys
HERE=Path(__file__).absolute().parent
HOME=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\isolated-home-01')
PROFILE_SHA='472a770af65d9485fd30415bd0c0df91cd961b05efbf0b4ef48a94d15eba82b7'
OWNER='C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01\\OWNER_AUTHORIZATION.json'
OWNER_SHA='05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff'
def main():
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
 if not a.prepare:print('INERT: Root source-only --prepare required');return
 assert hashlib.sha256(Path(OWNER).read_bytes()).hexdigest()==OWNER_SHA
 raw=(HERE/'PROFILE.toml').read_bytes();assert hashlib.sha256(raw).hexdigest()==PROFILE_SHA
 assert not HOME.exists() and not HOME.is_symlink();HOME.mkdir()
 with (HOME/'config.toml').open('xb') as f:f.write(raw)
 assert (HOME/'config.toml').read_bytes()==raw
 print(json.dumps(dict(status='SOURCE_PROFILE_CREATED_NO_NATIVE_CONTEXT',home=str(HOME),config_sha256=PROFILE_SHA,auth_route='UNVERIFIED_NOT_COPIED',real_home_changed=False)))
if __name__=='__main__':main()
