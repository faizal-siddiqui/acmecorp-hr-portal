# Salary Management System - Setup and Run script for PowerShell

$ErrorActionPreference = "Stop"

Write-Host ">>> Starting setup for Salary Management System..." -ForegroundColor Cyan

# 1. Install root dependencies
Write-Host ">>> Installing root dependencies..." -ForegroundColor Cyan
npm install

# 2. Install frontend dependencies
Write-Host ">>> Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location apps/web
npm install
Pop-Location

# 3. Install backend dependencies
Write-Host ">>> Installing backend dependencies (using uv)..." -ForegroundColor Cyan
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: 'uv' could not be found. Please install it first: https://github.com/astral-sh/uv" -ForegroundColor Red
    exit 1
}
Push-Location apps/api
uv sync --extra dev
Pop-Location

# 4. Setup environment files
Write-Host ">>> Setting up environment files..." -ForegroundColor Cyan
if (!(Test-Path "apps/api/.env")) {
    Copy-Item "apps/api/.env.example" "apps/api/.env"
    Write-Host "  [OK] Created apps/api/.env"
} else {
    Write-Host "  [INFO] apps/api/.env already exists, skipping."
}

if (!(Test-Path "apps/web/.env.local")) {
    Copy-Item "apps/web/.env.example" "apps/web/.env.local"
    Write-Host "  [OK] Created apps/web/.env.local"
} else {
    Write-Host "  [INFO] apps/web/.env.local already exists, skipping."
}

# 5. Seed the database
Write-Host ">>> Seeding the database (10000 records)..." -ForegroundColor Cyan
npm run seed

# 6. Run the app
Write-Host ">>> Setup complete! Starting development servers..." -ForegroundColor Green
npm run dev
