<#
PowerShell launcher for Cabal_Auto GUI
Usage:
  .\run_venv.ps1               # use .venv -> Scripts\python.exe, fallback to venv\Scripts\python.exe, then system python
  .\run_venv.ps1 -VenvPath .venv
  .\run_venv.ps1 -Args ""
#>
param(
    [string]$VenvPath = ".venv",
    [string]$Args = ""
)

function Get-PythonFromVenv($path) {
    $py = Join-Path $path "Scripts\python.exe"
    if (Test-Path $py) { return $py }
    return $null
}

$possible = @('.venv','venv')
if ($VenvPath -and (Test-Path $VenvPath)) { $possible = @($VenvPath) + $possible }

$python = $null
foreach ($p in $possible) {
    $candidate = Get-PythonFromVenv $p
    if ($candidate) { $python = $candidate; break }
}

if (-not $python) {
    Write-Host "No virtualenv found in .venv or venv. Falling back to system python."
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $python) { Write-Host "No 'python' on PATH. Please install Python or provide -VenvPath."; exit 1 }
}

Write-Host "Using python: $python"
& $python e:\Cabal_Auto\app_gui.py $Args
