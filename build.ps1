# Build script for Phone Agent
# Usage: .\build.ps1

Write-Host " Building Phone Agent executable..." -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
try {
    $null = Get-Command pyinstaller -ErrorAction Stop
} catch {
    Write-Host "[X] PyInstaller not found. Installing..." -ForegroundColor Red
    pip install pyinstaller
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path ".\build") {
    Remove-Item -Recurse -Force ".\build"
}
if (Test-Path ".\dist") {
    Remove-Item -Recurse -Force ".\dist"
}

# Build the executable
Write-Host "Building executable with PyInstaller..." -ForegroundColor Green
pyinstaller phone_agent.spec

# Check if build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[v] Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: .\dist\PhoneAgent.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Yellow
    Write-Host "   .\dist\PhoneAgent.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[X] Build failed. Please check the error messages above." -ForegroundColor Red
    Write-Host ""
    exit 1
}
