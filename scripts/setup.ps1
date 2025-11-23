# Quick Setup Script for Pulselytics
# Run this script to set up backend and install dependencies

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Pulselytics Quick Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "[2/6] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Found: Node $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "[3/6] Setting up backend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\backend"

if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "  Installing Python dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\pip.exe" install -r requirements.txt --quiet

if (-not (Test-Path ".env")) {
    Write-Host "  Creating .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

Write-Host "  ✓ Backend setup complete!" -ForegroundColor Green

# Setup Frontend
Write-Host "[4/6] Setting up frontend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing Node dependencies (this may take a few minutes)..." -ForegroundColor Cyan
    npm install --silent
}

if (-not (Test-Path ".env")) {
    Write-Host "  Creating .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

Write-Host "  ✓ Frontend setup complete!" -ForegroundColor Green

# Setup root Python environment
Write-Host "[5/6] Setting up root Python environment..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot"

if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "  Installing scraper dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\pip.exe" install -r requirements.txt --quiet

Write-Host "  ✓ Root environment setup complete!" -ForegroundColor Green

# Final instructions
Write-Host "[6/6] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend API Server:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\activate" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor White
Write-Host ""
Write-Host "2. Start Frontend (in new terminal):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "3. Run Scrapers (in new terminal):" -ForegroundColor Yellow
Write-Host "   .\venv\Scripts\activate" -ForegroundColor White
Write-Host "   python scrape_youtube.py --channel NASA --max-videos 20" -ForegroundColor White
Write-Host ""
Write-Host "4. Open Dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
