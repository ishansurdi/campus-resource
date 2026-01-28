# CAMPUSPHERE Backend

Django REST API with PostgreSQL and JWT Authentication

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create PostgreSQL Database
```bash
psql -U postgres
CREATE DATABASE campusphere_db;
\q
```

### 3. Run Setup Script
```bash
python setup.py
```

### 4. Start Development Server
```bash
python manage.py runserver
```

## Test Credentials

**Admin:**
- Username: `admin`
- Password: `Admin@123`

## API Endpoints

- `POST /api/auth/login/` - Login with JWT
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `GET /api/auth/health/` - Health check

## Login Example

```json
POST /api/auth/login/
{
  "username": "admin",
  "password": "Admin@123",
  "role": "admin"
}
```

Returns JWT access and refresh tokens with user data.
