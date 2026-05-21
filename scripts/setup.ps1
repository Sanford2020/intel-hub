# OPC Scaffold — Windows setup
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "=== OPC Scaffold Setup (Windows) ===" -ForegroundColor Cyan

# Backend
Write-Host "`n--- Backend ---" -ForegroundColor Yellow
Set-Location "$Root\backend"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend/.env"
}
pip install -r requirements.txt -q
Write-Host "Backend dependencies installed (pip)"

# Frontend
Write-Host "`n--- Frontend ---" -ForegroundColor Yellow
Set-Location "$Root\apps\web"
if (-not (Test-Path ".env.local")) {
    Copy-Item ".env.example" ".env.local"
    Write-Host "Created apps/web/.env.local"
}
npm install
Write-Host "Frontend dependencies installed"

# Shared types
Write-Host "`n--- Shared Types ---" -ForegroundColor Yellow
Set-Location "$Root\packages\shared-types"
npm install
Write-Host "Shared types ready"

Set-Location $Root
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host @"

Next steps:
  1. Start DB/Redis:  docker compose up -d db redis
  2. Start backend:   .\scripts\dev.ps1 backend
  3. Start frontend:  .\scripts\dev.ps1 frontend
  4. Or both:         .\scripts\dev.ps1

"@
