# Pulselytics Cleanup and Organization Script
# Organizes files into proper directory structure

Write-Host "Cleaning up and organizing Pulselytics workspace..." -ForegroundColor Cyan

# Create directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
$dirs = @('docs', 'scripts')
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  Created $dir/" -ForegroundColor Green
    } else {
        Write-Host "  $dir/ already exists" -ForegroundColor Gray
    }
}

# Move documentation files (core + AI/meta docs)
Write-Host "`nOrganizing documentation..." -ForegroundColor Yellow
$docFiles = @(
    'ANALYTICS_ENHANCEMENTS.md',
    'API_INTEGRATION_GUIDE.md',
    'API_SETUP.md',
    'DATABASE_SETUP.md',
    'IMPLEMENTATION_SUMMARY.md',
    'INSTAGRAM_API_SETUP.md',
    'NEW_FEATURES.md',
    'SETUP_COMPLETE.md',
    'SETUP_SUMMARY.md',
    # Additional AI/meta docs at repo root
    'AI_ENHANCEMENT_PLAN.md',
    'AI_FEATURES_IMPLEMENTED.md',
    'AI_TRANSFORMATION_GUIDE.md',
    'FEATURE_STATUS.md',
    'PROJECT_SUMMARY.md',
    'QUICK_FEATURE_GUIDE.md',
    'START_HERE.md',
    'DATA_POPULATION_SUMMARY.md'
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs\" -Force
        Write-Host "  Moved $file to docs/" -ForegroundColor Green
    }
}

# Move script files
Write-Host "`nOrganizing scripts..." -ForegroundColor Yellow
$scriptFiles = @(
    'scrape_facebook.py',
    'scrape_facebook_api.py',
    'scrape_instagram.py',
    'scrape_instagram_api.py',
    'scrape_twitter.py',
    'scrape_twitter_api.py',
    'scrape_youtube.py',
    'scrape_youtube_api.py',
    'analyze_data.py',
    'common.py',
    'seed_demo_data.py',
    'setup.ps1',
    'populate_demo_data.py'
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "scripts\" -Force
        Write-Host "  Moved $file to scripts/" -ForegroundColor Green
    }
}

# Remove temporary files
Write-Host "`nRemoving temporary files..." -ForegroundColor Yellow
$tempFiles = @(
    '_tmp_check_dates.py',
    'check_data.py',
    'test_youtube_api.py'
)

foreach ($file in $tempFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "  Removed $file" -ForegroundColor Green
    }
}

# Remove QUICKSTART_NEW.md (keep only QUICKSTART.md)
if (Test-Path 'QUICKSTART_NEW.md') {
    Remove-Item 'QUICKSTART_NEW.md' -Force
    Write-Host "  Removed QUICKSTART_NEW.md (duplicate)" -ForegroundColor Green
}

# Remove Python cache directories and nested virtualenvs accidentally committed
Write-Host "`nRemoving cache directories..." -ForegroundColor Yellow
$cacheDirs = @(
    '__pycache__',
    'backend\__pycache__',
    'scripts\__pycache__',
    'frontend\__pycache__'
)
foreach ($dir in $cacheDirs) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force
        Write-Host "  Removed $dir/" -ForegroundColor Green
    }
}

# Remove nested venv folders if present (keep top-level venv)
Write-Host "`nRemoving nested virtual environments if present..." -ForegroundColor Yellow
$nestedVenvs = @('backend\venv', 'frontend\venv')
foreach ($v in $nestedVenvs) {
    if (Test-Path $v) {
        Remove-Item -Path $v -Recurse -Force
        Write-Host "  Removed $v/" -ForegroundColor Green
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "`nOrganized structure:" -ForegroundColor Cyan
Write-Host "  backend/       - Flask API server"
Write-Host "  frontend/      - React dashboard"
Write-Host "  scripts/       - Scraper and utility scripts"
Write-Host "  docs/          - Documentation files"
Write-Host "  data/          - CSV data files"
Write-Host "  venv/          - Python virtual environment"
Write-Host "  README.md      - Main documentation"
Write-Host "  QUICKSTART.md  - Quick start guide"
Write-Host "  requirements.txt - Python dependencies"
