# ChallengeHub - Deployment Guide

## 🚀 Production Deployment Guide

This guide covers deploying ChallengeHub to production environments with proper security, performance, and scalability considerations. The platform includes advanced workflow management, user journey optimization, and efficient data flow processing.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Python**: 3.8 or higher
- **Database**: PostgreSQL 12+ or MySQL 8+
- **Web Server**: Nginx 1.18+
- **Application Server**: Gunicorn or uWSGI
- **Cache**: Redis 6+
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 20GB SSD

### Software Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev
sudo apt install postgresql postgresql-contrib
sudo apt install nginx redis-server
sudo apt install git curl wget

# CentOS/RHEL
sudo yum install python39 python39-devel
sudo yum install postgresql-server postgresql-contrib
sudo yum install nginx redis
sudo yum install git curl wget
```

## 🏗️ Environment Setup

### 1. Create Application User
```bash
sudo adduser challengehub
sudo usermod -aG sudo challengehub
su - challengehub
```

### 2. Clone Repository
```bash
git clone https://github.com/your-org/challengehub.git
cd challengehub
```

### 3. Create Virtual Environment
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

### PostgreSQL Configuration
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE challengehub_db;
CREATE USER challengehub_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE challengehub_db TO challengehub_user;
\q
```

### Database Configuration
```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'challengehub_db',
        'USER': 'challengehub_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🔧 Application Configuration

### 1. Environment Variables
Create `.env` file:
```bash
# Production Environment
DEBUG=False
SECRET_KEY=your-super-secret-key-here
SECRET_KEY_FILE=/etc/challengehub/secret_key.txt
DATABASE_URL=postgresql://challengehub_user:secure_password@localhost:5432/challengehub_db
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=challengehub.com,www.challengehub.com,api.challengehub.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Static Files
STATIC_ROOT=/var/www/challengehub/static/
MEDIA_ROOT=/var/www/challengehub/media/

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/challengehub/django.log
```

### 2. Django Settings
```python
# settings/production.py
import os
from pathlib import Path
from .base import *

# Security
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Static Files
STATIC_ROOT = os.getenv('STATIC_ROOT', '/var/www/challengehub/static/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/var/www/challengehub/media/')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.getenv('LOG_FILE', '/var/log/challengehub/django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'challengehub': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🌐 Web Server Configuration

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/challengehub
server {
    listen 80;
    server_name challengehub.com www.challengehub.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name challengehub.com www.challengehub.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/challengehub.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/challengehub.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Static Files
    location /static/ {
        alias /var/www/challengehub/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/challengehub/media/;
        expires 1M;
        add_header Cache-Control "public";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # WebSocket Support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /login/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/challengehub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Application Server Configuration

### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "challengehub"
group = "challengehub"
tmp_upload_dir = None
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
```

### Systemd Service
```ini
# /etc/systemd/system/challengehub.service
[Unit]
Description=ChallengeHub Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=challengehub
Group=challengehub
WorkingDirectory=/home/challengehub/challengehub
Environment=PATH=/home/challengehub/challengehub/venv/bin
Environment=DJANGO_SETTINGS_MODULE=tampere_cricket.settings.production
ExecStart=/home/challengehub/challengehub/venv/bin/gunicorn --config gunicorn.conf.py tampere_cricket.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable challengehub
sudo systemctl start challengehub
sudo systemctl status challengehub
```

## 🔒 SSL Certificate Setup

### Let's Encrypt SSL
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain Certificate
sudo certbot --nginx -d challengehub.com -d www.challengehub.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Logging

### Log Rotation
```bash
# /etc/logrotate.d/challengehub
/var/log/challengehub/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 challengehub challengehub
    postrotate
        systemctl reload challengehub
    endscript
}
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Create monitoring script
cat > /home/challengehub/monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Status ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h /)"
echo "=== Services ==="
systemctl status nginx postgresql redis challengehub
echo "=== Application Logs ==="
tail -n 20 /var/log/challengehub/django.log
EOF

chmod +x /home/challengehub/monitor.sh
```

## 🔄 Backup Strategy

### Database Backup
```bash
# /home/challengehub/backup_db.sh
#!/bin/bash
BACKUP_DIR="/home/challengehub/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/challengehub_db_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump challengehub_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "challengehub_db_*.sql.gz" -mtime +7 -delete
```

### Media Files Backup
```bash
# /home/challengehub/backup_media.sh
#!/bin/bash
BACKUP_DIR="/home/challengehub/backups/media"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /var/www/challengehub/media/

# Keep only last 7 days
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
```

### Automated Backups
```bash
# Add to crontab
crontab -e

# Daily backups at 2 AM
0 2 * * * /home/challengehub/backup_db.sh
0 2 * * * /home/challengehub/backup_media.sh
```

## 🚀 Deployment Scripts

### Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart challengehub
sudo systemctl reload nginx

echo "Deployment completed successfully!"
```

### Health Check Script
```bash
#!/bin/bash
# health_check.sh

# Check if services are running
systemctl is-active --quiet nginx || echo "Nginx is not running"
systemctl is-active --quiet postgresql || echo "PostgreSQL is not running"
systemctl is-active --quiet redis || echo "Redis is not running"
systemctl is-active --quiet challengehub || echo "ChallengeHub is not running"

# Check application health
curl -f http://localhost:8000/health/ || echo "Application health check failed"
```

## 🔧 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash challengehub
RUN chown -R challengehub:challengehub /app
USER challengehub

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tampere_cricket.wsgi:application"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://challengehub_user:secure_password@db:5432/challengehub_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - media_data:/app/media
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=challengehub_db
      - POSTGRES_USER=challengehub_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - media_data:/var/www/media
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  media_data:
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check database connectivity
   psql -h localhost -U challengehub_user -d challengehub_db
   ```

2. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   
   # Check file permissions
   sudo chown -R www-data:www-data /var/www/challengehub/static/
   ```

3. **Application Not Starting**
   ```bash
   # Check logs
   sudo journalctl -u challengehub -f
   
   # Check configuration
   python manage.py check --deploy
   ```

4. **Performance Issues**
   ```bash
   # Check system resources
   htop
   
   # Check database performance
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

### Log Analysis
```bash
# Application logs
tail -f /var/log/challengehub/django.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u challengehub -f
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_challenge_status ON matches_challenge(status);
CREATE INDEX idx_challenge_creator ON matches_challenge(creator_id);
CREATE INDEX idx_challenge_opponent ON matches_challenge(opponent_id);
CREATE INDEX idx_challenge_scheduled ON matches_challenge(scheduled_at);
CREATE INDEX idx_user_rating ON accounts_profile(rating);
```

### Cache Configuration
```python
# Redis cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

### CDN Configuration
```python
# AWS S3 configuration for static files
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
```

---

This comprehensive deployment guide ensures a secure, scalable, and maintainable production environment for the ChallengeHub platform.
