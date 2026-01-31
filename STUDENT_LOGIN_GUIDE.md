# Student Login Guide

## Overview
Students can login to the CAMPUSPHERE system using credentials issued by administrators.

## How It Works

### 1. Admin Creates Student Account
The admin must first create a student account with:
- **Username** (Student ID)
- **Password**
- **Role**: Student
- **Email**
- **Optional**: First name, last name, department

### 2. Student Login Process

**URL**: `http://localhost:3000/login.html?role=student`

**Steps**:
1. Student navigates to the login page
2. Selects "Student" from the role dropdown (or uses the direct link)
3. Enters their **Username** (e.g., ishansurdi2105) **OR Email** (both issued by admin)
4. Enters their **Password** (provided in welcome email)
5. Clicks "Sign In to Portal"

**Example Credentials** (as sent in email):
```
Username: ishansurdi2105
Password: 1cLpNrUD3Um-rA
Email: ishansurdi2105@campus.edu
```

Student can login with **either** username or email.

### 3. Authentication Flow

```
Student enters credentials
    ↓
Frontend sends POST to /api/auth/login/
    ↓
Backend authenticates against AdminUser model
    ↓
If valid: Returns JWT tokens (access + refresh)
    ↓
Frontend stores tokens in localStorage
    ↓
Student is redirected to /dashboards/student-dashboard/student-dashboard.html
```

### 4. Protected Routes

The student dashboard is protected and requires:
- Valid JWT token in localStorage
- Role must be "student"

If authentication fails, user is redirected to login page.

## API Endpoint

**POST** `/api/auth/login/`

**Request Body**:
```json
{
  "username": "ishansurdi2105",
  "password": "1cLpNrUD3Um-rA",
  "role": "student"
}
```

**Note**: The `username` field accepts **either username or email**. These examples work:
```json
// Using username
{"username": "ishansurdi2105", "password": "...", "role": "student"}

// Using email
{"username": "ishansurdi2105@campus.edu", "password": "...", "role": "student"}
```

**Response** (Success):
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "S12345",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "student_id": "S12345",
    "department": "Computer Science"
  }
}
```

## Student Dashboard Features

Once logged in, students can access:
- ✅ Dashboard overview
- ✅ My Profile
- ✅ Clubs (view and join)
- ✅ Events (register and view)
- ✅ Applications (submit and track)
- ✅ Chats (communicate)
- ✅ Documents (access)
- ✅ Notifications
- ✅ Settings
- ✅ Help
- ✅ Logout

## Creating Student Accounts (Admin)

Admins can create student accounts via:

1. **Django Admin Panel**: `/admin/`
2. **API Endpoint**: `/api/auth/register/`

**Example (Python/Django shell)**:
```python
from authentication.models import AdminUser

# Create a student account
student = AdminUser.objects.create_user(
    username='S12345',
    email='student@example.com',
    password='securepassword',
    first_name='John',
    last_name='Doe',
    role='student',
    student_id='S12345',
    department='Computer Science'
)
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Students can only access student routes
- **Protected Routes**: Dashboard requires valid authentication
- **Secure Logout**: Clears all tokens from localStorage

## Troubleshooting

### Issue: "Invalid credentials"
- Verify the username and password are correct
- Check that the account exists in the database
- Ensure the account is_active = True

### Issue: "User is not authorized as student"
- The account role must be set to "student"
- Check the role field in the database

### Issue: Redirected to login after accessing dashboard
- JWT token may have expired
- Check localStorage for access_token
- Try logging in again

## Next Steps

1. Start the backend server: `cd backend && python manage.py runserver`
2. Open frontend: `http://localhost:3000/login.html?role=student`
3. Create student accounts via admin panel
4. Test student login and dashboard access
