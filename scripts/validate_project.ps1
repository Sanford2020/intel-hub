# Intel Hub — one-shot project validation (Windows PowerShell)
param(
    [switch]$SkipDocker,
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$Quick
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Passed = @()
$Failed = @()

function Write-Step {
    param([string]$Label, [string]$Message)
    Write-Host "[$Label] $Message" -ForegroundColor Cyan
}

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-ValidationStep {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    Write-Step $Label "running..."
    try {
        & $Action
        if ($LASTEXITCODE -ne 0) {
            throw "exit code $LASTEXITCODE"
        }
        $script:Passed += $Label
        Write-Host "[$Label] PASS" -ForegroundColor Green
    } catch {
        $script:Failed += "${Label}: $($_.Exception.Message)"
        Write-Host "[$Label] FAIL — $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "=== Intel Hub validate_project ===" -ForegroundColor Yellow
Write-Host "Root: $Root"
Write-Host ""

if (-not $SkipDocker) {
    if (-not (Test-CommandExists "docker")) {
        $Failed += "docker: command not found (use -SkipDocker to ignore)"
        Write-Host "[docker] FAIL — docker not found" -ForegroundColor Red
    } else {
        Invoke-ValidationStep "docker-config" {
            Set-Location $Root
            docker compose config | Out-Null
        }
    }
} else {
    Write-Host "[docker] SKIPPED" -ForegroundColor DarkYellow
}

if (-not $SkipBackend) {
    if (-not (Test-CommandExists "python")) {
        $Failed += "backend: python not found"
        Write-Host "[backend] FAIL — python not found" -ForegroundColor Red
    } else {
        Invoke-ValidationStep "backend-pytest" {
            Set-Location "$Root\backend"
            $env:PYTHONPATH = $Root
            python -m pytest tests/ -q
        }
    }
} else {
    Write-Host "[backend] SKIPPED" -ForegroundColor DarkYellow
}

if (-not $SkipFrontend) {
    if (-not (Test-CommandExists "npm")) {
        $Failed += "frontend: npm not found"
        Write-Host "[frontend] FAIL — npm not found" -ForegroundColor Red
    } else {
        Invoke-ValidationStep "frontend-type-check" {
            Set-Location "$Root\apps\web"
            npm run type-check
        }
        if (-not $Quick) {
            Invoke-ValidationStep "frontend-build" {
                Set-Location "$Root\apps\web"
                npm run build
            }
        } else {
            Write-Host "[frontend-build] SKIPPED (-Quick)" -ForegroundColor DarkYellow
        }
    }
} else {
    Write-Host "[frontend] SKIPPED" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Yellow
Write-Host "PASSED ($($Passed.Count)): $($Passed -join ', ')"
if ($Failed.Count -gt 0) {
    Write-Host "FAILED ($($Failed.Count)):" -ForegroundColor Red
    foreach ($item in $Failed) {
        Write-Host "  - $item" -ForegroundColor Red
    }
    exit 1
}

Write-Host "All checks passed." -ForegroundColor Green
exit 0
