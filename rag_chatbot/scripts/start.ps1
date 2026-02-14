Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    throw "Missing rag_chatbot/.env. Run scripts/setup.ps1 first."
}

docker compose up --build -d

Write-Host "Backend:  http://localhost:8000/health"
Write-Host "Frontend: http://localhost:8501"
