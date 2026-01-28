# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv .venv

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Green
.\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Green
pip install Django==5.0.1
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1
pip install python-decouple==3.8
pip install django-cors-headers==4.3.1

# Try to install psycopg2-binary, if fails try psycopg2
Write-Host "`nInstalling PostgreSQL adapter..." -ForegroundColor Green
try {
    pip install psycopg2-binary==2.9.9
    Write-Host "psycopg2-binary installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "psycopg2-binary failed, trying alternative..." -ForegroundColor Yellow
    pip install psycopg2==2.9.9
}

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "`nTo activate virtual environment in future, run:" -ForegroundColor Yellow
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. python setup.py" -ForegroundColor White
Write-Host "2. python manage.py runserver" -ForegroundColor White
