# 🔧 Troubleshooting 401 Unauthorized Error

## ✅ Password Reset Complete

The password for user `ishansurdi2105` has been reset to: `1cLpNrUD3Um-rA`

## 🔐 Login Credentials

**Option 1 - Login with Username:**
```
Username: ishansurdi2105
Password: 1cLpNrUD3Um-rA
```

**Option 2 - Login with Email:**
```
Email: ishansurdi2105@gmail.com
Password: 1cLpNrUD3Um-rA
```

## 🧪 Test Login

### Method 1: Using Test Page
1. Open: `http://localhost:8000/test-student-login.html`
2. Click "Test Backend Connection" - should show ✅ Backend is running
3. Enter credentials and click "Test Login"

### Method 2: Using Login Page
1. Open: `http://localhost:8000/login.html?role=student`
2. Enter: `ishansurdi2105` (or `ishansurdi2105@gmail.com`)
3. Password: `1cLpNrUD3Um-rA`
4. Click "Sign In to Portal"

### Method 3: Using cURL
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ishansurdi2105",
    "password": "1cLpNrUD3Um-rA",
    "role": "student"
  }'
```

## ❌ Common 401 Errors and Fixes

### Error: "Invalid password"
- **Cause**: Password doesn't match
- **Fix**: Run `python reset_password.py` in backend folder

### Error: "No account found with this username"
- **Cause**: Username doesn't exist
- **Fix**: Check username with `python check_user.py`

### Error: "No account found with this email"
- **Cause**: Email doesn't exist or mismatch
- **Fix**: Verify email with `python check_user.py`

### Error: "Account is disabled"
- **Cause**: User account is_active = False
- **Fix**: Run in Django shell:
```python
from authentication.models import AdminUser
user = AdminUser.objects.get(username='ishansurdi2105')
user.is_active = True
user.save()
```

## 🔍 Verify Backend Status

1. **Check if backend is running:**
   ```
   http://localhost:8000/admin/
   ```
   Should show Django admin login page

2. **Check API endpoint:**
   ```
   http://localhost:8000/api/auth/login/
   ```
   Should return: `{"detail":"Method \"GET\" not allowed."}`

3. **Check CORS:**
   - Open browser console
   - Should NOT see CORS errors
   - If you do, check `.env` file has:
     ```
     CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
     ```

## 🛠️ Backend Commands

### Reset password:
```bash
cd backend
python reset_password.py
```

### Check user exists:
```bash
cd backend
python check_user.py
```

### Access Django shell:
```bash
cd backend
python manage.py shell
```

### Create new student:
```python
from authentication.models import AdminUser

user = AdminUser.objects.create_user(
    username='newstudent',
    email='student@example.com',
    password='securepassword',
    role='student'
)
```

## ✅ All Students in Database

Current students:
1. **workpallavisurdi** (workpallavisurdi@gmail.com) - Jui
2. **ishansurdi** (ishansurdi@gmail.com) - Varun  
3. **ishansurdi2105** (ishansurdi2105@gmail.com) - Ishan Surdi ← Password reset

## 📝 Next Steps

1. ✅ Backend is running on port 8000
2. ✅ User exists: ishansurdi2105
3. ✅ Password reset to: 1cLpNrUD3Um-rA
4. ✅ Account is active
5. 🔜 Try logging in now!

If login still fails, check browser console for specific error messages.
