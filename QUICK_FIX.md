# 🚨 IMMEDIATE ACTION REQUIRED - Create Admin User

## Your Production Database Has No Users!

The 401 error is because the admin user doesn't exist in your production database yet.

---

## ✅ Solution: Create Admin User on Render

### **Option 1: Using Render Shell (Recommended)**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on `campus-resource` service (your backend)
3. Click on the **"Shell"** tab at the top
4. Run these commands:
```bash
cd backend
python create_production_admin.py
```

### **Option 2: Using Django Management Command**

In the Render Shell:
```bash
cd backend
python manage.py shell
```

Then paste this:
```python
from authentication.models import AdminUser

admin = AdminUser.objects.create_user(
    username='admin',
    email='admin@campusphere.edu',
    password='Admin@123',
    first_name='System',
    last_name='Administrator',
    role='admin',
    employee_id='EMP001',
    department='Information Technology',
    is_staff=True,
    is_superuser=True,
    is_active=True,
    two_factor_enabled=False
)
print("✅ Admin created!")
```

Press Ctrl+D to exit the shell.

---

## 🔑 After Creating Admin User

### Login Credentials:
- **Username:** `admin`
- **Password:** `Admin@123`
- **URL:** https://campusphere-frontend-5sm4.onrender.com/login.html

### Steps:
1. Go to the login page
2. Select role: **Admin**
3. Enter username: `admin`
4. Enter password: `Admin@123`
5. Click "Sign In to Portal"

✅ You should now be able to login!

---

## 🔄 What Was Updated

The repository has been updated to work with both local and production:

### Frontend Changes:
- ✅ Added `config.js` - automatically detects if running locally or on Render
- ✅ Added `api-helper.js` - helper function for API URLs
- ✅ Updated all HTML files to use dynamic API URLs
- ✅ Updated 13 frontend files

### Backend Changes:
- ✅ Updated `settings.py` with default values and CORS for both environments
- ✅ Updated `render.yaml` with correct production URLs
- ✅ Updated `.env.example` with production database URL

### New Files:
- ✅ `create_production_admin.py` - Script to create admin in production
- ✅ `PRODUCTION_SETUP.md` - Complete deployment guide

---

## 📊 How It Works Now

### Local Development:
- Frontend detects `localhost` → uses `http://localhost:8000`
- Backend connects to local PostgreSQL or production database

### Production (Render):
- Frontend detects `onrender.com` → uses `https://campus-resource-8pw5.onrender.com`
- Backend connects to production PostgreSQL

**No code changes needed!** It automatically switches based on the environment.

---

## 🎯 Next Steps

1. ✅ **FIRST:** Create admin user using instructions above
2. ✅ Login and change the default password
3. Create faculty users
4. Create student users
5. Configure university profile
6. Set up clubs and events

---

## ⚠️ Important Notes

- The changes have been pushed to GitHub
- Render will automatically deploy the updates
- Wait 2-3 minutes for Render to redeploy
- Then create the admin user
- The production database URL is secure (only accessible from Render services)

---

## 🆘 If You Still Have Issues

Check:
1. ✅ Did you create the admin user? (most common issue)
2. ✅ Did Render finish deploying? (check deployment logs)
3. ✅ Is the backend running? Visit: https://campus-resource-8pw5.onrender.com/api/auth/health/

**Need Help?** Check `PRODUCTION_SETUP.md` for detailed troubleshooting.
