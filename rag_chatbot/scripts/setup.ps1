Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created rag_chatbot/.env from .env.example"
} else {
    Write-Host "rag_chatbot/.env already exists"
}

docker --version | Out-Null
docker compose version | Out-Null

Write-Host "Environment setup complete."
Write-Host "Next: edit rag_chatbot/.env and set OPENAI_API_KEY."
