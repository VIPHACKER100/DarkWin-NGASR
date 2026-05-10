# DARKWIN - Dashboard Launcher
# ============================================================================
# Purpose: Start both Backend API and Frontend Dashboard.
# Developed by ARYAN AHIRWAR (VIPHACKER.100)
# ============================================================================

$ErrorActionPreference = "Continue"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   DARKWIN - Starting Dashboard Ecosystem           " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Start Backend in a new window
Write-Host "[INFO] Launching Backend API on http://localhost:5000..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python dashboards/backend/app.py"

# 2. Wait a few seconds for backend to initialize
Start-Sleep -Seconds 3

# 3. Start Frontend in a new window
Write-Host "[INFO] Launching Frontend Dashboard on http://localhost:3000..." -ForegroundColor Blue
Set-Location "dashboards/frontend-next"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
Set-Location "..\.."

Write-Host "`n[SUCCESS] Ecosystem is launching!" -ForegroundColor Green
Write-Host "  - Backend: http://localhost:5000"
Write-Host "  - Frontend: http://localhost:3000"
Write-Host "====================================================" -ForegroundColor Cyan
