# OPC Scaffold — Windows dev launcher
param(
    [ValidateSet("all", "backend", "frontend", "worker", "beat", "e2e-smoke")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONPATH = $Root

function Start-Backend {
    Write-Host "Starting backend → http://localhost:8001/docs" -ForegroundColor Cyan
    Set-Location "$Root\backend"
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
}

function Start-Frontend {
    Write-Host "Starting frontend → http://localhost:3000" -ForegroundColor Cyan
    Set-Location "$Root\apps\web"
    npm run dev
}

function Start-Worker {
    Write-Host "Starting Celery worker..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    $pool = if ($IsWindows -or $env:OS -match "Windows") { "solo" } else { "prefork" }
    python -m celery -A workers.celery_app worker --loglevel=info -Q default,ingest --pool $pool
}

function Start-Beat {
    Write-Host "Starting Celery beat..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    python -m celery -A workers.celery_app beat --loglevel=info
}

function Start-E2ESmoke {
    Write-Host "Running E2E smoke tests..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    python -m pytest tests/test_e2e_ingest_analyze.py -q
}

switch ($Target) {
    "backend"  { Start-Backend }
    "frontend" { Start-Frontend }
    "worker"   { Start-Worker }
    "beat"     { Start-Beat }
    "e2e-smoke" { Start-E2ESmoke }
    "all" {
        Write-Host "Open terminals:" -ForegroundColor Yellow
        Write-Host "  .\scripts\dev.ps1 backend"
        Write-Host "  .\scripts\dev.ps1 worker"
        Write-Host "  .\scripts\dev.ps1 beat"
        Write-Host "  .\scripts\dev.ps1 frontend"
    }
}
