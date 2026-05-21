#!/usr/bin/env pwsh
# Sync external integrations: opc-methodology skills + agency-agents
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Vendor = Join-Path $Root ".vendor"

Write-Host "=== OPC Scaffold: Sync Integrations ===" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $Vendor | Out-Null

# --- OPC Methodology skills ---
$OpcRepo = Join-Path $Vendor "opc-methodology"
if (-not (Test-Path $OpcRepo)) {
    Write-Host "Cloning opc-methodology..." -ForegroundColor Yellow
    git clone --depth 1 https://github.com/easychen/opc-methodology.git $OpcRepo
} else {
    Write-Host "Updating opc-methodology..." -ForegroundColor Yellow
    git -C $OpcRepo pull --ff-only
}

$OpcTarget = Join-Path $Root "skills\opc"
New-Item -ItemType Directory -Force -Path $OpcTarget | Out-Null
Copy-Item -Recurse -Force (Join-Path $OpcRepo "skills\*") $OpcTarget
Write-Host "OPC skills -> skills/opc/" -ForegroundColor Green

# --- Agency Agents ---
$AgencyRepo = Join-Path $Vendor "agency-agents"
if (-not (Test-Path $AgencyRepo)) {
    Write-Host "Cloning agency-agents..." -ForegroundColor Yellow
    git clone --depth 1 https://github.com/msitarzewski/agency-agents.git $AgencyRepo
} else {
    Write-Host "Updating agency-agents..." -ForegroundColor Yellow
    git -C $AgencyRepo pull --ff-only
}

$AgencyTarget = Join-Path $Root "agents\agency"
New-Item -ItemType Directory -Force -Path $AgencyTarget | Out-Null
$Divisions = @(
    "engineering", "design", "product", "marketing",
    "project-management", "testing", "strategy", "support"
)
foreach ($div in $Divisions) {
    $src = Join-Path $AgencyRepo $div
    if (Test-Path $src) {
        Copy-Item -Recurse -Force $src (Join-Path $AgencyTarget $div)
        Write-Host "  agency/$div" -ForegroundColor Gray
    }
}
Write-Host "Agency agents -> agents/agency/" -ForegroundColor Green

Write-Host "`n=== Sync Complete ===" -ForegroundColor Green
Write-Host "Business: skills/opc/opc-orchestrator/SKILL.md"
Write-Host "Personas: agents/agency/engineering/"
Write-Host "Runtime:  POST /api/v1/agents/runs"
