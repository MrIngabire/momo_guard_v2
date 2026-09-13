$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
& "$root\.venv\Scripts\Activate.ps1"
Set-Location $PSScriptRoot
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000