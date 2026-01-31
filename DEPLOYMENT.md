# Deployment Guide - Render

This guide will help you deploy CAMPUSPHERE to Render.

## Prerequisites

- GitHub account
- Render account (free tier available at https://render.com)
- Your code pushed to GitHub repository

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all deployment files are in place (already included):
- ✅ `requirements.txt` with all dependencies including `gunicorn`
- ✅ `render.yaml` for service configuration
- ✅ `.gitignore` to exclude sensitive files
- ✅ `build.sh` for build automation
- ✅ Updated `settings.py` with production configurations

### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name**: `campusphere-db`
   - **Database**: `campusphere`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users (e.g., Singapore, Oregon)
   - **Plan**: Free (or Starter for better performance)
4. Click **"Create Database"**
5. Wait for database to be created
6. **Important**: Copy the **Internal Database URL** (starts with `postgresql://`)

### 4. Create Web Service (Backend)

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `campusphere-backend` (or your preferred name)
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     gunicorn campusphere.wsgi:application
     ```
   - **Plan**: Free (or Starter for better performance)

4. **Add Environment Variables** (click "Add Environment Variable"):

   ```
   PYTHON_VERSION = 3.11.0
   
   DATABASE_URL = <paste the Internal Database URL from step 3>
   
   SECRET_KEY = <generate using command below>
   
   DEBUG = False
   
   ALLOWED_HOSTS = .onrender.com
   
   CORS_ALLOWED_ORIGINS = https://your-frontend-name.onrender.com
   
   DJANGO_SETTINGS_MODULE = campusphere.settings
   ```

   **To generate SECRET_KEY**, run locally:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. Click **"Create Web Service"**

6. Wait for deployment (first deploy takes 5-10 minutes)

7. Once deployed, your backend will be at: `https://campusphere-backend.onrender.com`

### 5. Create Static Site (Frontend)

1. Click **"New +"** → **"Static Site"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `campusphere-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`

4. Click **"Create Static Site"**

5. Your frontend will be at: `https://campusphere-frontend.onrender.com`

### 6. Update Frontend API URLs

You need to update all API endpoints in your frontend to point to your Render backend:

1. **Update `frontend/auth.js`**:
   ```javascript
   const API_BASE_URL = 'https://campusphere-backend.onrender.com';
   ```

2. **Update all HTML files** that make API calls:
   - Replace `http://localhost:8000` with `https://campusphere-backend.onrender.com`
   - Files to update:
     - `login.html`
     - `dashboards/admin-dashboard.html`
     - `dashboards/approvals.html`
     - `dashboards/faculty-dashboard/faculty-dashboard.html`
     - `dashboards/student-dashboard/*.html`

3. **Push the changes**:
   ```bash
   git add .
   git commit -m "Update API URLs for production"
   git push origin main
   ```

   Render will automatically redeploy your frontend.

### 7. Update CORS Settings

Go back to your backend service on Render and update the environment variable:

```
CORS_ALLOWED_ORIGINS = https://campusphere-frontend.onrender.com,https://campusphere-backend.onrender.com
```

Save and your backend will redeploy.

### 8. Create Superuser (Admin Account)

1. Go to your backend service on Render
2. Click on **"Shell"** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin account

### 9. Test Your Deployment

1. Visit your frontend URL
2. Try logging in
3. Test creating events, clubs, etc.
4. Check all features work correctly

## Post-Deployment

### Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor CPU, memory, bandwidth usage
- **Health Checks**: Render automatically monitors service health

### Updating Your App

Simply push to GitHub:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect changes and redeploy.

### Custom Domain (Optional)

1. Go to your service settings
2. Click **"Add Custom Domain"**
3. Follow instructions to configure DNS
4. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` accordingly

## Troubleshooting

### Build Fails

**Check:**
- All dependencies in `requirements.txt`
- Build command is correct
- Python version is specified

**View logs** in Render dashboard to see exact error.

### Database Connection Issues

**Check:**
- `DATABASE_URL` is set correctly
- Database and web service are in same region
- Internal database URL is used (not external)

### Static Files Not Loading

**Check:**
- `collectstatic` runs in build command
- `STATIC_ROOT` and `STATIC_URL` configured
- WhiteNoise middleware is added

### CORS Errors

**Check:**
- Frontend URL is in `CORS_ALLOWED_ORIGINS`
- Include protocol (https://)
- No trailing slashes

### 502 Bad Gateway

**Causes:**
- App crashed on startup
- Wrong start command
- Python errors in code

**Solution:**
- Check logs for Python errors
- Verify gunicorn command
- Check all imports work

### Database Migrations

If you need to run migrations manually:
1. Go to Shell in Render dashboard
2. Run: `python manage.py migrate`

### Reset Database

**Warning**: This deletes all data!
```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

## Performance Tips

### Free Tier Limitations

- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-50 seconds
- Database has connection limits

### Upgrade Considerations

For production use, consider:
- **Starter Plan ($7/month)**: No sleep, better performance
- **Database Plan ($7/month)**: More connections, better reliability
- **Redis**: Add caching for better performance

### Optimization

1. **Enable caching** in Django settings
2. **Optimize queries** (use `select_related`, `prefetch_related`)
3. **Add database indexes** on frequently queried fields
4. **Use CDN** for static files (CloudFlare, AWS S3)

## Security Checklist

- ✅ `DEBUG = False` in production
- ✅ Strong `SECRET_KEY`
- ✅ `ALLOWED_HOSTS` configured
- ✅ HTTPS enabled (automatic on Render)
- ✅ CORS properly configured
- ✅ Environment variables used for secrets
- ✅ `.env` file not in git
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection enabled
- ✅ CSRF protection enabled

## Support

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Project Issues**: https://github.com/ishansurdi/campus-resource/issues

## Cost Estimate

### Free Tier (Development)
- Web Service: Free (with sleep)
- PostgreSQL: Free (limited connections)
- Static Site: Free
- **Total**: $0/month

### Starter (Production)
- Web Service: $7/month
- PostgreSQL: $7/month
- Static Site: Free
- **Total**: $14/month

---

**Last Updated**: January 31, 2026
