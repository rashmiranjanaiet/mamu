Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true)]
    [string]$PdfPath
)

$root = Join-Path $PSScriptRoot ".."
Set-Location $root

$venvPython = Join-Path $root ".venv311\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Missing .venv311 environment."
}
if (-not (Test-Path $PdfPath)) {
    throw "PDF not found: $PdfPath"
}

$env:PYTHONPATH = "."
& $venvPython "scripts/ingest_book.py" $PdfPath
