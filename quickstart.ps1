# Quick Start Script
# Run this after configuring GitHub Secrets

Write-Host "🚀 Mist SLE Automation - Quick Start" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python found" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
pip install pytest pytest-cov responses
Write-Host "✅ Test dependencies installed" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (Test-Path .env) {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Copy .env.example to .env and configure" -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "   Created .env from template. Please edit it with your credentials." -ForegroundColor Yellow
}
Write-Host ""

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some tests failed (this is expected until credentials are configured)" -ForegroundColor Yellow
} else {
    Write-Host "✅ All tests passed" -ForegroundColor Green
}
Write-Host ""

# Display next steps
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure GitHub Secrets (see docs/deployment_guide.md)" -ForegroundColor White
Write-Host "2. Edit .env file with your credentials for local testing" -ForegroundColor White
Write-Host "3. Test modules individually:" -ForegroundColor White
Write-Host "   python src/diagnostics.py --ap_id YOUR_AP_ID --sle throughput" -ForegroundColor Gray
Write-Host "4. Review README.md for full documentation" -ForegroundColor White
Write-Host "5. Deploy workflow to GitHub Actions" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "- README.md - Project overview" -ForegroundColor White
Write-Host "- docs/deployment_guide.md - Deployment steps" -ForegroundColor White
Write-Host "- docs/zendesk_integration.md - Zendesk details" -ForegroundColor White
Write-Host "- docs/splunk_integration.md - Splunk details" -ForegroundColor White
Write-Host "- PROJECT_SUMMARY.md - Complete project summary" -ForegroundColor White
Write-Host ""
Write-Host "Happy Automating! 🎊" -ForegroundColor Green
