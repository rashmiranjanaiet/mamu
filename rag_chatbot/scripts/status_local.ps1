Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Join-Path $PSScriptRoot ".."
Set-Location $root

function Show-Status([string]$name, [string]$pidFile) {
    if (-not (Test-Path $pidFile)) {
        Write-Host "${name}: not running (no pid file)"
        return
    }
    $procId = Get-Content $pidFile
    try {
        $proc = Get-Process -Id ([int]$procId) -ErrorAction Stop
        Write-Host "${name}: running (PID $($proc.Id))"
    } catch {
        Write-Host "${name}: not running (stale pid file)"
    }
}

Show-Status -name "Backend" -pidFile ".backend.pid"
Show-Status -name "Frontend" -pidFile ".frontend.pid"
