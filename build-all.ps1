# YumesuteAutoTeamUp Build Script
# Usage: .\build-all.ps1

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot
$ElectronDir = Join-Path $RootDir "electron-app"
$ResourcesDir = Join-Path $ElectronDir "resources"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  YumesuteAutoTeamUp Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Build Python script
Write-Host "`n[1/4] Building Python script..." -ForegroundColor Yellow
Set-Location $RootDir

if (Test-Path "dist\Start.exe") {
    Write-Host "  -> dist\Start.exe exists, skipping" -ForegroundColor Gray
} else {
    pyinstaller --onefile Start.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  -> Python build failed!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  -> Done" -ForegroundColor Green

# Step 2: Copy resources
Write-Host "`n[2/4] Copying resources..." -ForegroundColor Yellow

if (-not (Test-Path $ResourcesDir)) {
    New-Item -ItemType Directory -Path $ResourcesDir | Out-Null
}

Copy-Item "dist\Start.exe" -Destination $ResourcesDir -Force
Write-Host "  -> Copied Start.exe" -ForegroundColor Gray

$DataDir = Join-Path $ResourcesDir "data"
if (Test-Path $DataDir) {
    Remove-Item -Recurse -Force $DataDir
}
Copy-Item "data" -Destination $DataDir -Recurse -Force
Write-Host "  -> Copied data folder" -ForegroundColor Gray

Write-Host "  -> Done" -ForegroundColor Green

# Step 3: Install Electron dependencies
Write-Host "`n[3/4] Checking Electron dependencies..." -ForegroundColor Yellow
Set-Location $ElectronDir

if (-not (Test-Path "node_modules")) {
    Write-Host "  -> Installing..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  -> npm install failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  -> Dependencies exist" -ForegroundColor Gray
}
Write-Host "  -> Done" -ForegroundColor Green

# Step 4: Build Electron app
Write-Host "`n[4/4] Building Electron app..." -ForegroundColor Yellow

$env:ELECTRON_BUILDER_BINARIES_MIRROR = "https://npmmirror.com/mirrors/electron-builder-binaries/"

npm run build:win
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> Electron build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  -> Done" -ForegroundColor Green

# Done
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$OutputDir = Join-Path $ElectronDir "dist"
Write-Host "`nOutput: $OutputDir" -ForegroundColor Yellow

$SetupFile = Get-ChildItem -Path $OutputDir -Filter "*.exe" | Select-Object -First 1
if ($SetupFile) {
    Write-Host "Installer: $($SetupFile.FullName)" -ForegroundColor Yellow
}

explorer $OutputDir
