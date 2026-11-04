<#
.SYNOPSIS
  SprintLens Environment Initialization Script (PowerShell)
.DESCRIPTION
  Copies .env.example to .env if missing, verifies tools, and provides setup guidance.
#>

$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "       SprintLens - Local Environment Setup      " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Environment file check
if (-not (Test-Path ".env")) {
    Write-Host "[+] Creating .env from .env.example..." -ForegroundColor Green
    Copy-Item ".env.example" ".env"
} else {
    Write-Host "[i] .env file already exists." -ForegroundColor Yellow
}

# 2. Prerequisites Check
Write-Host "`n[+] Checking prerequisites..." -ForegroundColor Cyan

# Node.js
try {
    $nodeVersion = node -v
    Write-Host "  - Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  - Node.js: NOT FOUND (Please install Node.js >= 20)" -ForegroundColor Red
}

# pnpm
try {
    $pnpmVersion = pnpm.cmd -v
    Write-Host "  - pnpm: v$pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "  - pnpm: NOT FOUND (Please install pnpm: npm install -g pnpm)" -ForegroundColor Yellow
}

# Python
try {
    $pyVersion = python --version
    Write-Host "  - Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  - Python: NOT FOUND (Please install Python >= 3.11)" -ForegroundColor Red
}

# Docker
try {
    $dockerVersion = docker --version
    Write-Host "  - Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  - Docker: NOT FOUND (Please install Docker Desktop)" -ForegroundColor Red
}

Write-Host "`n[+] Setup check complete!" -ForegroundColor Cyan
Write-Host "To start the local PostgreSQL database, run: docker-compose up -d postgres" -ForegroundColor White

