$ErrorActionPreference = 'Stop'
$bundle = '/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g2-production-issuer-01/root-operation-driver'
$destination = '/home/agent/dg16-g2-current04-public-20261109/root-operation-driver-01'
& 'C:\WINDOWS\system32\wsl.exe' --distribution Ubuntu --user agent --exec /usr/bin/python3 -I -B "$bundle/operator_setup.py" install $bundle $destination
if ($LASTEXITCODE -ne 0) { throw 'Driver installation refused or completion unknown. Reconcile this attempt; do not rerun blindly.' }
