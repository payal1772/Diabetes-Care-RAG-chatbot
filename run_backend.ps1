$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$App = Join-Path $Root "backend\app.py"

if (-not (Test-Path $Python)) {
    throw "Virtual environment Python not found at $Python. Create it first, then install backend\requirements.txt."
}

& $Python $App
