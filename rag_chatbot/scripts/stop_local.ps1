Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Join-Path $PSScriptRoot ".."
Set-Location $root

foreach ($pidFile in @(".backend.pid", ".frontend.pid")) {
    if (Test-Path $pidFile) {
        $procId = Get-Content $pidFile
        if ($procId) {
            try {
                Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop
                Write-Host "Stopped PID $procId"
            } catch {
                Write-Host "PID $procId already stopped"
            }
        }
        Remove-Item $pidFile -Force
    }
}
