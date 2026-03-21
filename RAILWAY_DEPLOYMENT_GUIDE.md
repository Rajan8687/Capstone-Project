# Railway Deployment Guide for InsightWrite

## Step-by-Step Railway Deployment

### Step 1: Prerequisites
1. Create a Railway account at https://railway.app
2. Install Railway CLI (optional but recommended):
   ```bash
   npm install -g @railway/cli
   ```

### Step 2: Prepare Your Code (IMPORTANT CHANGES)

#### A. Update settings.py for Production
I've created `railway_settings.py` - you need to use this OR update your existing settings.py:

**Key Changes Needed:**

1. **Add WhiteNoise** (for serving static files):
   ```python
   # Add to MIDDLEWARE after SecurityMiddleware
   'whitenoise.middleware.WhiteNoiseMiddleware',
   ```

2. **Update Database Configuration**:
   ```python
   import dj_database_url
   import os
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME', default='insightwrite'),
           'USER': config('DB_USER', default='postgres'),
           'PASSWORD': config('DB_PASSWORD', default='postgres'),
           'HOST': config('DB_HOST', default='localhost'),
           'PORT': config('DB_PORT', default='5432'),
       }
   }
   
   # Use Railway's DATABASE_URL if available
   if os.environ.get('DATABASE_URL'):
       DATABASES['default'] = dj_database_url.parse(
           os.environ.get('DATABASE_URL'),
           conn_max_age=600,
           ssl_require=True
       )
   ```

3. **Update Static Files**:
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```

4. **Update Celery Redis**:
   ```python
   REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
   CELERY_BROKER_URL = REDIS_URL
   CELERY_RESULT_BACKEND = REDIS_URL
   ```

5. **Update ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['*']  # Railway handles this, or use your domain
   ```

6. **Security Settings for Production**:
   ```python
   if not DEBUG:
       SECURE_SSL_REDIRECT = True
       SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
       SESSION_COOKIE_SECURE = True
       CSRF_COOKIE_SECURE = True
   ```

### Step 3: Update requirements.txt
Add these packages (already done):
```
dj-database-url==2.1.0
whitenoise==6.6.0
gunicorn==21.2.0
```

### Step 4: Create Railway Configuration Files
Already created:
- `railway.toml` - Deployment config
- `nixpacks.toml` - Build config
- `railway_settings.py` - Production settings

### Step 5: Deploy to Railway

#### Method 1: Railway Dashboard (Easiest)

1. **Go to Railway Dashboard**: https://railway.app/dashboard

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your `capstone-project` repository

3. **Add PostgreSQL Database**:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will auto-provide DATABASE_URL

4. **Add Redis** (optional, for Celery):
   - Click "New" → "Database" → "Add Redis"
   - Railway will auto-provide REDIS_URL

5. **Add Environment Variables**:
   Go to your project → Variables tab, add:
   ```
   SECRET_KEY = your-secret-key-here (generate a strong one)
   DEBUG = False
   ```

6. **Deploy**:
   - Railway will auto-deploy when you push to GitHub
   - Or click "Deploy" in the dashboard

#### Method 2: Railway CLI

```bash
# Login to Railway
railway login

# Link your project
railway link

# Add PostgreSQL
railway add --database postgres

# Add Redis (optional)
railway add --database redis

# Set environment variables
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set DEBUG="False"

# Deploy
railway up

# Get your domain
railway domain
```

### Step 6: Run Migrations and Create Superuser

After deployment, run these commands in Railway:

1. **Open Railway Dashboard** → Your Project → "..." menu → "Run Command"

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Collect Static Files** (if not done automatically):
   ```bash
   python manage.py collectstatic --noinput
   ```

### Step 7: Important Post-Deployment Steps

1. **Update CORS** in settings.py:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       # Add your Railway domain:
       "https://your-project.up.railway.app",
   ]
   ```

2. **Add Custom Domain** (optional):
   - Railway Dashboard → Your Project → Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

3. **Verify Deployment**:
   - Visit your Railway URL
   - Test login/signup
   - Check static files are loading
   - Test database operations

### Step 8: Troubleshooting

**Issue: Static files not loading**
- Check `railway.toml` has `collectstatic` command
- Verify WhiteNoise is in MIDDLEWARE
- Check `STATIC_ROOT` and `STATIC_URL` settings

**Issue: Database connection error**
- Verify PostgreSQL is provisioned
- Check DATABASE_URL environment variable
- Run migrations manually

**Issue: 500 errors**
- Check logs in Railway Dashboard (Deploy → View Logs)
- Verify all environment variables are set
- Check DEBUG=False in production

**Issue: Celery not working**
- Add Redis service in Railway
- Verify REDIS_URL environment variable
- Check Celery worker is running

### Files Changed for Railway Deployment

1. ✅ `requirements.txt` - Added gunicorn, whitenoise, dj-database-url
2. ✅ `railway.toml` - Deployment configuration
3. ✅ `nixpacks.toml` - Build configuration
4. ✅ `railway_settings.py` - Production-ready settings

### Your Railway URL
After deployment, your site will be at:
`https://your-project-name.up.railway.app`

### Maintenance Commands
```bash
# View logs
railway logs

# Restart service
railway restart

# Run Django shell
railway run python manage.py shell

# Database backup (manual)
railway run python manage.py dumpdata > backup.json
```

## Summary
- Railway auto-provisions PostgreSQL and Redis
- Static files served via WhiteNoise
- Gunicorn as WSGI server
- Auto-deploy on Git push
- Free tier available (limited hours)
