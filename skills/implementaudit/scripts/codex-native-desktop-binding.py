"""Bind the actual Windows parent executable to the reviewed physical package."""
import hashlib, ntpath, pathlib, re, subprocess, json
PACKAGE = pathlib.Path(r'C:\Program Files\WindowsApps\OpenAI.Codex_26.915.4065.0_x64__2p2nqsd0c76g0')
PACKAGE_VERSION='26.915.4065.0'
EXE=PACKAGE/'app/ChatGPT.exe'
ASAR=EXE.parent/'resources/app.asar'
EXE_SHA256='0d27aef4010466bd8d2a95f6483938cfdb8926f6668ecc1182facec9b85b75d2'
ASAR_SHA256='b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096'
EXE_VERSION='153.0.8010.48'
def norm(path): return ntpath.normcase(ntpath.normpath(str(path)))
def file_id(path):
    b=path.read_bytes()
    return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def observe_parent(actual_path):
    try:
        physical=pathlib.Path(actual_path).resolve(strict=True)
        root=physical.parent.parent
        # Derive the source location from the actual observed parent, not ASAR.
        source=physical.parent/'resources/app.asar'
        version=re.fullmatch(r'OpenAI\.Codex_([0-9.]+)_x64__2p2nqsd0c76g0',root.name)
        result={'resolved_executable_path':str(physical),'package_root':str(root),'package_version':version[1] if version else None,'derived_asar_path':str(source),'executable':file_id(physical),'asar':file_id(source)}
        # VersionInfo is read from that same resolved executable; no process
        # environment, authentication state, or raw command line is collected.
        escaped=str(physical).replace("'","''")
        script="$v=(Get-Item -LiteralPath '"+escaped+"').VersionInfo; @{file=$v.FileVersion;product=$v.ProductVersion} | ConvertTo-Json -Compress"
        r=subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
        if r.returncode: raise RuntimeError('version read failed')
        result['executable_version']=json.loads(r.stdout)
        return result
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        return {'read_error':True,'actual_path_sha256':hashlib.sha256(str(actual_path).encode()).hexdigest()}
def parent_matches(parent,reviewed_bundle):
    if not isinstance(parent,dict) or not isinstance(reviewed_bundle,dict): return False
    s=parent.get('source_binding')
    if not isinstance(s,dict) or s.get('read_error'): return False
    try:
        return all([
            norm(parent['path'])==norm(EXE),
            norm(s['resolved_executable_path'])==norm(EXE),
            norm(s['package_root'])==norm(PACKAGE),
            s['package_version']==PACKAGE_VERSION,
            norm(s['executable']['path'])==norm(EXE),
            s['executable']['sha256']==EXE_SHA256,
            s['executable_version']=={'file':EXE_VERSION,'product':EXE_VERSION},
            norm(s['derived_asar_path'])==norm(ntpath.join(ntpath.dirname(s['resolved_executable_path']),'resources','app.asar'))==norm(ASAR),
            norm(s['asar']['path'])==norm(ASAR)==norm(reviewed_bundle['path']),
            s['asar']['sha256']==ASAR_SHA256==reviewed_bundle['sha256'],
        ])
    except (KeyError,TypeError,ValueError): return False
