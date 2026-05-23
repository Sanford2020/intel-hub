# OPS-03 — Worker / Beat observation orchestrator (Windows)
param(
    [double]$DurationHours = 24,
    [string]$Api = "http://127.0.0.1:8001",
    [string]$SampleCsv = "docs/operations/worker-observation-2026-05-samples.csv",
    [string]$WorkerLog = "docs/operations/worker-observation-2026-05-worker.log",
    [string]$BeatLog = "docs/operations/worker-observation-2026-05-beat.log",
    [switch]$SkipStart
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONPATH = $Root
$env:SMOKE_EMAIL = if ($env:SMOKE_EMAIL) { $env:SMOKE_EMAIL } else { "admin@example.com" }
$env:SMOKE_PASSWORD = if ($env:SMOKE_PASSWORD) { $env:SMOKE_PASSWORD } else { "change-me" }

$DurationMinutes = [math]::Max(1, [math]::Round($DurationHours * 60))
$Iterations = $DurationMinutes
$IntervalSec = 60

function Ensure-DockerInfra {
    Push-Location $Root
    docker compose up -d db redis | Out-Null
    Pop-Location
}

function Start-BackgroundProcess {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string[]]$Command,
        [string]$LogPath
    )
    $logFull = Join-Path $Root $LogPath
    $logDir = Split-Path -Parent $logFull
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    if (Test-Path $logFull) { Remove-Item $logFull -Force }
    $argList = ($Command | ForEach-Object { if ($_ -match '\s') { "`"$_`"" } else { $_ } }) -join ' '
    $psi = @{
        FilePath = $Command[0]
        ArgumentList = $Command[1..($Command.Length - 1)]
        WorkingDirectory = $WorkingDirectory
        RedirectStandardOutput = $logFull
        RedirectStandardError = $logFull
        PassThru = $true
        WindowStyle = 'Hidden'
    }
    Write-Host "Starting $Name -> $logFull" -ForegroundColor Cyan
    return Start-Process @psi
}

Write-Host "=== OPS-03 Worker/Beat observation ===" -ForegroundColor Yellow
Write-Host "Duration: $DurationHours h ($Iterations samples @ ${IntervalSec}s)" -ForegroundColor Yellow
Write-Host "CSV: $SampleCsv" -ForegroundColor Yellow

Ensure-DockerInfra

$samplePath = Join-Path $Root $SampleCsv
if (Test-Path $samplePath) { Remove-Item $samplePath -Force }

if (-not $SkipStart) {
    $backend = Start-BackgroundProcess -Name "backend" -WorkingDirectory (Join-Path $Root "backend") -Command @(
        "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"
    ) -LogPath "docs/operations/worker-observation-2026-05-backend.log"

    Start-Sleep -Seconds 5

    $worker = Start-BackgroundProcess -Name "worker" -WorkingDirectory (Join-Path $Root "backend") -Command @(
        "python", "-m", "celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "-Q", "default,ingest", "--pool", "solo"
    ) -LogPath $WorkerLog

    $beatSchedule = Join-Path $Root "docs/operations/celerybeat-schedule-ops03"
    if (Test-Path $beatSchedule) { Remove-Item $beatSchedule -Force }
    $beat = Start-BackgroundProcess -Name "beat" -WorkingDirectory (Join-Path $Root "backend") -Command @(
        "python", "-m", "celery", "-A", "workers.celery_app", "beat", "--loglevel=info", "--schedule", $beatSchedule
    ) -LogPath $BeatLog

    Write-Host "Backend PID $($backend.Id) · Worker PID $($worker.Id) · Beat PID $($beat.Id)" -ForegroundColor Green
}

Write-Host "Sampling stats + queue depth..." -ForegroundColor Cyan
Push-Location $Root
python scripts/observe-loop.py `
    --api $Api `
    --interval $IntervalSec `
    --iterations $Iterations `
    --out $SampleCsv
$exitCode = $LASTEXITCODE
python scripts/summarize-observation.py $SampleCsv
Pop-Location

Write-Host "Observation complete (exit=$exitCode). Review $SampleCsv and logs under docs/operations/." -ForegroundColor Green
exit $exitCode
