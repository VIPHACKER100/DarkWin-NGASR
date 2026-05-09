# DARKWIN - Environment Setup Script (Windows)
# ============================================================================
# Purpose: Initialize DARKWIN environment on Windows.
# Author: ARYAN AHIRWAR (VIPHACKER.100)
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   DARKWIN - Next-Gen Security Research Platform    " -ForegroundColor Cyan
Write-Host "               Windows Setup Script                 " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check Python Version
Write-Host "`n[INFO] Checking Python version..." -ForegroundColor Blue
$pythonVersion = python --version 2>$null
if ($null -eq $pythonVersion) {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "[SUCCESS] Found $pythonVersion" -ForegroundColor Green

# 2. Setup Virtual Environment
Write-Host "`n[INFO] Setting up virtual environment..." -ForegroundColor Blue
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "[SUCCESS] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[INFO] Virtual environment already exists" -ForegroundColor Yellow
}

# 3. Install Dependencies
Write-Host "`n[INFO] Installing Python dependencies..." -ForegroundColor Blue
& ".\.venv\Scripts\pip.exe" install --upgrade pip setuptools wheel
& ".\.venv\Scripts\pip.exe" install --upgrade "typing-extensions>=4.11.0" "pydantic-core>=2.18.0"
if (Test-Path "requirements.txt") {
    & ".\.venv\Scripts\pip.exe" install -r requirements.txt
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
}

# 4. Install package in editable mode
Write-Host "`n[INFO] Installing DarkWin in editable mode..." -ForegroundColor Blue
& ".\.venv\Scripts\pip.exe" install -e .
Write-Host "[SUCCESS] DarkWin installed" -ForegroundColor Green

# 5. Check External Tools (Informational)
Write-Host "`n[INFO] Checking for external security tools..." -ForegroundColor Blue
$tools = @("nmap", "subfinder", "httpx", "nuclei", "ffuf", "amass", "katana", "sqlmap", "dalfox", "masscan")
foreach ($tool in $tools) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        Write-Host "[SUCCESS] Found $tool" -ForegroundColor Green
    } else {
        Write-Host "[WARN] $tool NOT found. Install it manually if needed." -ForegroundColor Yellow
    }
}

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host " Setup Completed Successfully!                      " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "`nTo start using DARKWIN:"
Write-Host "  1. .\.venv\Scripts\Activate.ps1"
Write-Host "  2. python core/darkwin.py --help"
Write-Host "====================================================" -ForegroundColor Cyan
