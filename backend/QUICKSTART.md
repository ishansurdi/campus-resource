# QUICK START GUIDE

## Option 1: Using PowerShell Script (Recommended)

```powershell
# Run the setup script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_venv.ps1
```

## Option 2: Manual Setup

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies one by one (avoiding psycopg2-binary issue)
pip install Django==5.0.1
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1
pip install python-decouple==3.8
pip install django-cors-headers==4.3.1

# 5. For PostgreSQL, try this Windows-compatible version:
pip install psycopg2==2.9.9

# 6. Run setup
python setup.py

# 7. Start server
python manage.py runserver
```

## Test Credentials

- **Username:** admin
- **Password:** Admin@123

## API Endpoints

- Health: http://localhost:8000/api/auth/health/
- Login: http://localhost:8000/api/auth/login/
- Admin Panel: http://localhost:8000/admin/

## Troubleshooting

### psycopg2 Installation Issues

If psycopg2 still fails on Windows, you can either:

1. **Install PostgreSQL** (includes required libraries)
2. **Use SQLite for development** (update settings.py temporarily)
3. **Install pre-built wheel:**
   ```powershell
   pip install https://github.com/nwcell/psycopg2-windows/releases/download/2.9.9/psycopg2-2.9.9-cp311-cp311-win_amd64.whl
   ```

### For SQLite (Development Only)

Update `backend/campusphere/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
