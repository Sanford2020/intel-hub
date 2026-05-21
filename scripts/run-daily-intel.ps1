# Intel Hub — one-shot daily intelligence loop (ingest → analyze → briefing [→ Feishu])
param(
    [string]$Api = "http://127.0.0.1:8000",
    [int]$IngestLimit = 20,
    [switch]$SkipIngest,
    [switch]$SkipAnalyze,
    [switch]$SkipBriefing
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONPATH = $Root

Write-Host "=== Intel Hub run-daily-intel ===" -ForegroundColor Yellow
Write-Host "API: $Api"

# Health
try {
    $health = Invoke-RestMethod -Uri "$Api/api/v1/health" -Method Get -TimeoutSec 10
    Write-Host "[health] OK — $($health.data.app_name) $($health.data.version)" -ForegroundColor Green
} catch {
    Write-Host "[health] FAIL — start backend: .\scripts\dev.ps1 backend" -ForegroundColor Red
    exit 1
}

if (-not $SkipIngest) {
    Write-Host "[ingest] Queueing RSS/social ingest (limit=$IngestLimit, async)..." -ForegroundColor Cyan
    python "$Root\scripts\batch-ingest-rss.py" --api $Api --limit $IngestLimit --async
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "[ingest] Queueing AI HOT / HN / Reddit fast path..." -ForegroundColor Cyan
    python "$Root\scripts\ingest-social-fast.py" --api $Api
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "[ingest] SKIPPED" -ForegroundColor DarkGray
}

function Invoke-CeleryTask {
    param([string]$TaskName, [string]$Label)
    Write-Host "[$Label] Enqueue $TaskName ..." -ForegroundColor Cyan
    Set-Location "$Root\backend"
    python -c @"
from workers.celery_app import celery_app
r = celery_app.send_task('$TaskName')
print('task_id=' + r.id)
"@
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$Label] FAIL — is Worker running? .\scripts\dev.ps1 worker" -ForegroundColor Red
        exit 1
    }
}

if (-not $SkipAnalyze) {
    Invoke-CeleryTask -TaskName "workers.tasks.analyze.dispatch.dispatch_unanalyzed_articles" -Label "analyze"
} else {
    Write-Host "[analyze] SKIPPED" -ForegroundColor DarkGray
}

if (-not $SkipBriefing) {
    Invoke-CeleryTask -TaskName "workers.tasks.briefings.generate.generate_daily_briefing" -Label "briefing"
} else {
    Write-Host "[briefing] SKIPPED" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Done (tasks queued; Worker must be running) ===" -ForegroundColor Green
Write-Host "Briefing UI: http://localhost:3000/briefing"
Write-Host "API preview:  $Api/api/v1/briefings/daily?hours=24"
Write-Host "Tip: wait 1-3 min for analyze, then refresh /briefing"
