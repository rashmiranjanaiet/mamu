Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Join-Path $PSScriptRoot ".."
Set-Location $root

$venvPython = Join-Path $root ".venv311\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Missing .venv311. Create it with: py -3.11 -m venv rag_chatbot\.venv311"
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

$backendArgs = @(
    "-m", "uvicorn", "backend.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--app-dir", "."
)
$frontendArgs = @(
    "-m", "streamlit", "run", "frontend/app.py",
    "--server.address=0.0.0.0",
    "--server.port=8501",
    "--server.headless=true",
    "--browser.gatherUsageStats=false"
)

$backend = Start-Process -FilePath $venvPython -ArgumentList $backendArgs -PassThru -WindowStyle Hidden -WorkingDirectory $root
$frontend = Start-Process -FilePath $venvPython -ArgumentList $frontendArgs -PassThru -WindowStyle Hidden -WorkingDirectory $root

Set-Content -Path ".backend.pid" -Value $backend.Id
Set-Content -Path ".frontend.pid" -Value $frontend.Id

Write-Host "Backend PID:  $($backend.Id)"
Write-Host "Frontend PID: $($frontend.Id)"
Write-Host "Backend:  http://localhost:8000/health"
Write-Host "Frontend: http://localhost:8501"
