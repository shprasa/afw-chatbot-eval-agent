Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PY = "$env:USERPROFILE\anaconda3\python.exe"
& $env:PY (Join-Path (Split-Path $PSScriptRoot -Parent) 'rewrite_powerbi_exports.py')
