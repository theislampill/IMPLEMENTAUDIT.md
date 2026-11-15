
async function runBoundDispatcher(path,manifestHelperPath,manifestHelperPin,expected) {
 // expected must come from the actual pinned bind_dispatcher output / its
 // independently received INSTALL_MANIFEST, never from this file's readback.
 if(!expected || Object.keys(expected).sort().join(",")!=="bytes,sha256" ||
    !Number.isSafeInteger(expected.bytes) || expected.bytes<=0 || expected.bytes>1048576 ||
    typeof expected.sha256!=="string" || !/^[0-9a-f]{64}$/.test(expected.sha256))
   throw Error("Exact independently selected dispatcher descriptor required");
 const loader=load("G132_LOADER");
 const tail="sys.argv=[str(p),*sys.argv[3:]]; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})";
 if(typeof loader!=="string" || !loader.endsWith(tail) || loader.indexOf(tail)!==loader.length-tail.length)
   throw Error("Exact pinned physical reader required");
 const reader=loader.slice(0,-tail.length)+"import json; print(json.dumps({'source':raw.decode('utf-8'),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}))";
 const acquired=await H.cmd([H.PY,"-I","-B","-c",reader,path,expected.sha256],{max_output_tokens:18000,login:false,workdir:"/"});
 if(acquired.exit_code!==0 || acquired.session_id!==undefined)throw Error("Dispatcher read refused or incomplete");
 const held=JSON.parse(acquired.output);
 if(held.bytes!==expected.bytes || held.sha256!==expected.sha256 || typeof held.source!=="string")
   throw Error("Exact bound dispatcher changed");
 const js=held.source;
 const forwarded=[];
 const shim=Object.create(null);
 shim.exec_command=async function(input){
  const prefix="$PSNativeCommandArgumentPassing='Standard'; & ",suffix="; exit $LASTEXITCODE";
  if(typeof input.cmd!=="string"||!input.cmd.startsWith(prefix)||!input.cmd.endsWith(suffix))throw Error("Exact generated command envelope required");
  const body=input.cmd.slice(prefix.length,-suffix.length);let tokens=[],at=0;
  while(at<body.length){
   if(body[at]!=="'")throw Error("Only literal quoted argv accepted");at++;let token="",closed=false;
   while(at<body.length){if(body[at]==="'"){if(body[at+1]==="'"){token+="'";at+=2;}else{at++;closed=true;break;}}else{token+=body[at++];}}
   if(!closed||/[\r\n\0]/.test(token))throw Error("Invalid literal token");tokens.push(token);
   if(at<body.length){if(body[at]!==" "||body[at+1]!=="'")throw Error("Additional shell syntax refused");at++;}
  }
  const prefixArgs=["C:\\Windows\\System32\\wsl.exe","--distribution","Ubuntu","--user","agent","--cd","/","--exec"];
  if(JSON.stringify(tokens.slice(0,8))!==JSON.stringify(prefixArgs))throw Error("Wrong fixed transport prefix");
  const argv=tokens.slice(8);
  if(argv[0]!=="/usr/bin/python3"||argv[1]!=="-I"||argv[2]!=="-B"||argv[3]!=="-c"||argv[4]!==load("G132_LOADER")||argv[5]!==manifestHelperPath||argv[6]!==manifestHelperPin)throw Error("Wrong pinned interpreter/loader/entry");
  if(!["initialize","ready","reserve","chunk","complete","publish","finish"].includes(argv[7]))throw Error("Wrong helper action");
  const r=await tools.exec_command({...input,cmd:argv.map(H.quote).join(" "),login:false,workdir:"/"});
  forwarded.push({action:argv[7],ordinal:argv[8],exit_code:r.exit_code,session_id:r.session_id});
  return r;
 };
 shim.write_stdin=async input=>tools.write_stdin(input);
 shim.mcp__codex_apps__github_fetch=async input=>tools.mcp__codex_apps__github_fetch(input);
 await (new (Object.getPrototypeOf(async function(){}).constructor)("tools","notify","text","setTimeout",js))(shim,notify,text,setTimeout);
 store("G132_BOUND_DISPATCH_TRANSPORT",{dispatch_source:expected,helper_path:manifestHelperPath,helper_sha256:manifestHelperPin,actual_forwarded:forwarded,source_bytes_modified:false});
}
runBoundDispatcher;
