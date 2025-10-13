# 🚀 SportsHub Heroku Deployment Guide

This guide will help you deploy your Django SportsHub project to Heroku using your GitHub Student Developer Pack.

## 📋 Prerequisites

1. **Heroku CLI** installed on your system
2. **Git** installed and configured
3. **GitHub Student Developer Pack** access
4. Your Django SportsHub project ready for deployment

## 🔧 Files Created/Updated

The following files have been created or updated for Heroku deployment:

### ✅ Files Created:
- `Procfile` - Tells Heroku how to run your app
- `runtime.txt` - Specifies Python version
- `HEROKU_DEPLOYMENT_GUIDE.md` - This deployment guide

### ✅ Files Updated:
- `requirements.txt` - Added Heroku-specific packages
- `tampere_cricket/settings.py` - Updated for production deployment
- All templates updated with SportsHub branding

## 🚀 Step-by-Step Deployment

### Step 1: Install Heroku CLI (if not already installed)

**Windows:**
```bash
# Download and install from: https://devcenter.heroku.com/articles/heroku-cli
# Or use chocolatey:
choco install heroku-cli
```

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit for SportsHub Heroku deployment"
```

### Step 4: Create Heroku App

```bash
# Replace 'your-app-name' with your desired app name
heroku create your-sportshub-app

# Example:
heroku create sportshub-cricket-app
```

### Step 5: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Step 6: Set Environment Variables

```bash
# Set a secure secret key
heroku config:set SECRET_KEY="your-super-secret-key-here-make-it-long-and-random"

# Set debug to False for production
heroku config:set DEBUG=False

# Optional: Set other environment variables
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
```

### Step 7: Deploy to Heroku

```bash
# If your default branch is 'main':
git push heroku main

# If your default branch is 'master':
git push heroku master
```

### Step 8: Run Database Migrations

```bash
heroku run python manage.py migrate
```

### Step 9: Collect Static Files

```bash
heroku run python manage.py collectstatic --noinput
```

### Step 10: Create Superuser (Optional)

```bash
heroku run python manage.py createsuperuser
```

### Step 11: Open Your App

```bash
heroku open
```

## 🔍 Troubleshooting Commands

### View Logs
```bash
heroku logs --tail
```

### Check App Status
```bash
heroku ps
```

### Access Heroku Shell
```bash
heroku run bash
```

### Check Environment Variables
```bash
heroku config
```

### Restart App
```bash
heroku restart
```

## 📝 Important Notes

### Security Considerations:
1. **Never commit your SECRET_KEY** to version control
2. **Use environment variables** for sensitive data
3. **Set DEBUG=False** in production
4. **Use HTTPS** (Heroku provides this automatically)

### Database:
- Your app will automatically use PostgreSQL on Heroku
- SQLite will be used in local development
- No manual database configuration needed

### Static Files:
- WhiteNoise handles static file serving
- Files are automatically compressed
- CDN can be added later if needed

### Media Files:
- For production, consider using AWS S3 or similar
- Heroku's filesystem is ephemeral

## 🎯 Post-Deployment Checklist

- [ ] App opens successfully
- [ ] Database migrations completed
- [ ] Static files loading correctly
- [ ] User registration/login works
- [ ] Admin panel accessible
- [ ] All features working as expected
- [ ] SportsHub branding displays correctly

## 🔄 Future Updates

To deploy updates:

```bash
git add .
git commit -m "Your update message"
git push heroku main  # or master
```

## 📞 Support

If you encounter issues:

1. Check logs: `heroku logs --tail`
2. Verify environment variables: `heroku config`
3. Check database connection: `heroku run python manage.py dbshell`
4. Restart the app: `heroku restart`

## 🎉 Success!

Your SportsHub Django app should now be live on Heroku! The URL will be something like:
`https://your-sportshub-app.herokuapp.com`

## 🏆 SportsHub Features

Your deployed app includes:
- **Cricket Challenge System** - Create and accept challenges
- **Leaderboard** - Track player rankings
- **Ground Management** - Find and book cricket grounds
- **News & Updates** - Stay informed about cricket events
- **User Profiles** - Manage your cricket profile
- **Admin Dashboard** - Comprehensive statistics and management

Remember to update your domain settings and email configurations for production use.

## 🎯 Quick Commands Summary

```bash
# Complete deployment in one go:
heroku login
heroku create sportshub-cricket-app
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku open
```

Your SportsHub cricket platform is now ready to serve the Tampere cricket community! 🏏