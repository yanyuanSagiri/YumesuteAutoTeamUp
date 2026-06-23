# Build Python script to exe
# Usage: .\build-python.ps1

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot

Write-Host "Building Python script..." -ForegroundColor Yellow
Set-Location $RootDir

# Clean previous build
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "Start.spec") { Remove-Item -Force "Start.spec" }

# Build
pyinstaller --onefile Start.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build complete: dist\Start.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}
