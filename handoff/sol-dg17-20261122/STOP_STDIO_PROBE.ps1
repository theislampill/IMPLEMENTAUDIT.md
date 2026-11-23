param(
 [Parameter(Mandatory=$true)][string]$Python,
 [Parameter(Mandatory=$true)][string]$Scratch,
 [switch]$Headless,
 [switch]$DetachedBom
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version 2
Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public static class WireProbeConsole { [DllImport("kernel32.dll")] public static extern uint GetConsoleCP(); [DllImport("kernel32.dll")] public static extern bool FreeConsole(); }'
function Need($ok,$why){if(!$ok){throw $why}}
function Hex([byte[]]$raw){[BitConverter]::ToString($raw).Replace('-','').ToLowerInvariant()}
function Save($path,[byte[]]$raw){
 $f=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$f.Write($raw,0,$raw.Length);$f.Flush($true)}finally{$f.Dispose()}
}
function Wait-Task($clock,$task){
 $remaining=5000-$clock.ElapsedMilliseconds
 Need ($remaining -gt 0 -and $task.Wait([int]$remaining)) 'fixture deadline'
}
function Read-Bytes($clock,$stream){
 $log=[IO.MemoryStream]::new();$buffer=[byte[]]::new(512)
 try{
  do{
   $pending=$stream.ReadAsync($buffer,0,$buffer.Length)
   Wait-Task $clock $pending
   $n=$pending.GetAwaiter().GetResult()
   Need ($log.Length+$n -le 1024) 'fixture output limit'
   $log.Write($buffer,0,$n)
  }while($n -gt 0)
  ,$log.ToArray()
 }finally{$log.Dispose()}
}
function Probe($label,[byte[]]$payload){
 Need ($payload.Length -le 512) 'fixture input limit'
 $info=[Diagnostics.ProcessStartInfo]::new($Python,('-I -S -B "'+$echo+'"'))
 $info.WorkingDirectory=$Scratch;$info.UseShellExecute=$false;$info.CreateNoWindow=$true
 $info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
 $info.EnvironmentVariables.Clear()
 foreach($pair in @{SystemRoot='C:\Windows';WINDIR='C:\Windows';PATH='C:\Windows\System32';TEMP=$Scratch;TMP=$Scratch}.GetEnumerator()){
  $info.EnvironmentVariables[$pair.Key]=$pair.Value
 }
 $process=[Diagnostics.Process]::new();$process.StartInfo=$info;$started=$false
 $clock=[Diagnostics.Stopwatch]::StartNew()
 try{
  $started=$process.Start()
  Need $started 'fixture did not start'
  $writer=$process.StandardInput;$pipe=$writer.BaseStream
  $autoFlush=$writer.AutoFlush;$writerPreamble=Hex $writer.Encoding.GetPreamble()
  if($payload.Length -gt 0){
   $pending=$pipe.WriteAsync($payload,0,$payload.Length)
   Wait-Task $clock $pending;[void]$pending.GetAwaiter().GetResult()
   $pending=$pipe.FlushAsync()
   Wait-Task $clock $pending;[void]$pending.GetAwaiter().GetResult()
  }
  $pipe.Dispose()
  $observed=[Text.Encoding]::ASCII.GetString((Read-Bytes $clock $process.StandardOutput.BaseStream))
  $stderr=Read-Bytes $clock $process.StandardError.BaseStream
  $remaining=5000-$clock.ElapsedMilliseconds
  Need ($remaining -gt 0 -and $process.WaitForExit([int]$remaining) -and $process.ExitCode -eq 0 -and $stderr.Length -eq 0) 'fixture exit'
  Need ($observed -match '^(?:[0-9a-f]{2})*$') 'nonhex echo'
  $expected=Hex $payload
  [ordered]@{
   case=$label;console_cp=[WireProbeConsole]::GetConsoleCP();input_encoding=$writer.Encoding.CodePage
   output_encoding=[Console]::OutputEncoding.CodePage;writer_auto_flush=$autoFlush
   writer_encoding_preamble_hex=$writerPreamble;accounted_bytes=$payload.Length
   received_bytes=[int]($observed.Length/2);accounted_hex=$expected;received_hex=$observed
   exact_match=($observed -ceq $expected)
  }
 }finally{
  if($started -and !$process.HasExited){$process.Kill();[void]$process.WaitForExit(250)}
  $process.Dispose()
 }
}
$file=[IO.File]::OpenRead($Python);$sha=[Security.Cryptography.SHA256]::Create()
try{Need ((Hex $sha.ComputeHash($file)) -ceq '5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec') 'fixture interpreter identity'}
finally{$sha.Dispose();$file.Dispose()}
$utf=[Text.UTF8Encoding]::new($false,$true)
$line='{"id":1,"method":"initialize","params":{"clientInfo":{"name":"implementaudit-stop-discovery","version":"1"},"capabilities":{"experimentalApi":true}}}'
$frame=$utf.GetBytes($line+[char]10)
Need ($frame.Length -eq 150) 'initialize byte count'
$echo=Join-Path $Scratch 'byte-echo.py'
Save $echo ($utf.GetBytes(([string]::Join([char]10,@(
 'import sys',
 'raw = sys.stdin.buffer.read(513)',
 'if len(raw) > 512: sys.exit(4)',
 'sys.stdout.buffer.write(raw.hex().encode("ascii"))',
 ''
)))))
$original=[Console]::InputEncoding
$cp=[WireProbeConsole]::GetConsoleCP()
$cases=@()
$detachedGate=$null
if($Headless -or $DetachedBom){
 if($DetachedBom){
  Need ($cp -ne 0) 'private console unavailable for BOM control'
  [Console]::InputEncoding=[Text.Encoding]::GetEncoding(65001)
  Need ((Hex ([Console]::InputEncoding.GetPreamble())) -ceq 'efbbbf') 'cached BOM not established'
 }
 [void][WireProbeConsole]::FreeConsole()
 Need ([WireProbeConsole]::GetConsoleCP() -eq 0) 'fixture still has a console'
 if($DetachedBom){
  Need ((Hex ([Console]::InputEncoding.GetPreamble())) -ceq 'efbbbf') 'cached BOM missing after detach'
  $corrected=$false
  try{
   [Console]::InputEncoding=$utf
   $corrected=[Console]::InputEncoding.GetPreamble().Length -eq 0
  }catch{}
  if($corrected){
   $detachedGate='CORRECTED'
   $cases+=Probe 'detached-bom-guarded' $frame
  }else{
   $detachedGate='REFUSED_BEFORE_FIXTURE_START'
  }
 }else{
  $cases+=Probe 'no-console-stock' $frame
  Need ([Console]::InputEncoding.GetPreamble().Length -eq 0) 'no-console encoding requires supported correction'
  $cases+=Probe 'no-console-guarded' $frame
 }
}else{
 Need ($cp -ne 0) 'private console unavailable'
 try{
  $cases+=Probe 'private-console-stock' $frame
  [Console]::InputEncoding=[Text.Encoding]::GetEncoding(65001)
  $cases+=Probe 'stock-codepage-65001' $frame
  $cases+=Probe 'stock-codepage-65001-no-write' ([byte[]]::new(0))
  [Console]::InputEncoding=[Text.UTF8Encoding]::new($true,$true)
  $cases+=Probe 'explicit-utf8-bom' $frame
  [Console]::InputEncoding=[Text.UTF8Encoding]::new($false,$true)
  $cases+=Probe 'explicit-utf8-no-bom' $frame
  [Console]::InputEncoding=[Text.Encoding]::GetEncoding(437)
  $cases+=Probe 'stock-codepage-437' $frame
  [Console]::InputEncoding=[Text.Encoding]::GetEncoding(65001)
  if([Console]::InputEncoding.GetPreamble().Length){[Console]::InputEncoding=$utf}
  Need ([Console]::InputEncoding.GetPreamble().Length -eq 0) 'correction did not remove preamble'
  $cases+=Probe 'guarded-correction' $frame
 }finally{[Console]::InputEncoding=$original}
}
foreach($item in $cases){
 if($item.case -in @('stock-codepage-65001','stock-codepage-65001-no-write','explicit-utf8-bom')){
  Need ($item.received_hex -ceq ('efbbbf'+$item.accounted_hex)) 'preamble discriminator missing'
 }elseif($item.case -notin @('private-console-stock')){
  Need $item.exact_match 'zero-extra-byte control failed'
 }
}
$result=[ordered]@{
 schema='sol-dg17.stdin-preamble-probe.v1';ps=$PSVersionTable.PSVersion.ToString()
 clr=$PSVersionTable.CLRVersion.ToString();console_before=$cp;console_after=[WireProbeConsole]::GetConsoleCP();detached_bom_gate=$detachedGate;rows=$cases
}
Save (Join-Path $Scratch 'observations.json') ($utf.GetBytes((ConvertTo-Json -InputObject $result -Depth 6)))
