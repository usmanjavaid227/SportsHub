# ChallengeHub - Technical Architecture Documentation

## 🏗️ System Architecture Overview

ChallengeHub is built using Django's Model-View-Template (MVT) architecture with a RESTful API layer for enhanced functionality.

## 🎯 Architecture Components

### 1. Presentation Layer
- **Templates**: HTML templates with Django template engine
- **Static Files**: CSS, JavaScript, images
- **Frontend Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS for dynamic interactions

### 2. Application Layer
- **Views**: Django views handling HTTP requests
- **Forms**: Django forms for data validation
- **Serializers**: DRF serializers for API responses
- **Middleware**: Custom middleware for authentication and logging

### 3. Business Logic Layer
- **Models**: Django ORM models for data management
- **Services**: Business logic services
- **Utilities**: Helper functions and utilities
- **Validators**: Custom validation logic

### 4. Data Layer
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: Django ORM for database operations
- **Migrations**: Database schema management
- **Caching**: Redis for session and data caching

## 🗄️ Database Design

### Entity Relationships

```
User (1) ←→ (1) Profile
User (1) ←→ (N) Challenge (as creator)
User (1) ←→ (N) Challenge (as opponent)
User (1) ←→ (N) Challenge (as winner)
Ground (1) ←→ (N) Challenge
TimeSlot (1) ←→ (N) Challenge
User (1) ←→ (N) News (as author)
User (1) ←→ (N) Notification
```

### Database Tables

#### Users Table
```sql
CREATE TABLE accounts_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    phone VARCHAR(24),
    city VARCHAR(100) DEFAULT 'Tampere',
    bio TEXT,
    role VARCHAR(10) DEFAULT 'allrounder',
    experience_level VARCHAR(20) DEFAULT 'intermediate',
    preferred_batting_style VARCHAR(20),
    preferred_bowling_style VARCHAR(30),
    years_playing INTEGER DEFAULT 0,
    avatar VARCHAR(100),
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

#### Profiles Table
```sql
CREATE TABLE accounts_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES accounts_user(id) ON DELETE CASCADE,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    rating DECIMAL(10,2) DEFAULT 1000.0,
    batting_rating DECIMAL(10,2) DEFAULT 1000.0,
    bowling_rating DECIMAL(10,2) DEFAULT 1000.0,
    runs INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    balls_bowled INTEGER DEFAULT 0,
    fcm_token VARCHAR(300)
);
```

#### Challenges Table
```sql
CREATE TABLE matches_challenge (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES accounts_user(id) ON DELETE CASCADE,
    opponent_id INTEGER REFERENCES accounts_user(id) ON DELETE SET NULL,
    ground_id INTEGER REFERENCES grounds_ground(id) ON DELETE SET NULL,
    time_slot_id INTEGER REFERENCES matches_timeslot(id) ON DELETE SET NULL,
    status VARCHAR(10) DEFAULT 'OPEN',
    challenge_type VARCHAR(8),
    condition_text VARCHAR(255),
    metric VARCHAR(20),
    target_value INTEGER,
    over_count INTEGER,
    scheduled_at TIMESTAMP,
    creator_score INTEGER,
    opponent_score INTEGER,
    winner_id INTEGER REFERENCES accounts_user(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Grounds Table
```sql
CREATE TABLE grounds_ground (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(300),
    lat DECIMAL(9,6),
    lng DECIMAL(9,6),
    approved BOOLEAN DEFAULT FALSE
);
```

#### TimeSlots Table
```sql
CREATE TABLE matches_timeslot (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_challenges INTEGER DEFAULT 1,
    created_by_id INTEGER REFERENCES accounts_user(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, start_time, end_time)
);
```

#### News Table
```sql
CREATE TABLE news_news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    image VARCHAR(100),
    author_id INTEGER REFERENCES accounts_user(id) ON DELETE CASCADE,
    published BOOLEAN DEFAULT FALSE,
    featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP
);
```

#### Notifications Table
```sql
CREATE TABLE notifications_notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES accounts_user(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    body TEXT,
    link VARCHAR(300),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 API Architecture

### RESTful API Design

#### Base URL Structure
```
/api/v1/
├── auth/
│   ├── login/
│   ├── logout/
│   └── register/
├── challenges/
│   ├── list/
│   ├── create/
│   ├── {id}/
│   ├── {id}/accept/
│   └── {id}/cancel/
├── users/
│   ├── profile/
│   ├── leaderboard/
│   └── {id}/
├── grounds/
│   ├── list/
│   └── {id}/
├── timeslots/
│   ├── list/
│   ├── create/
│   └── {id}/
└── admin/
    ├── challenges/
    ├── grounds/
    └── timeslots/
```

#### API Response Format
```json
{
    "status": "success|error",
    "data": {},
    "message": "Optional message",
    "errors": [],
    "pagination": {
        "count": 100,
        "next": "http://api.example.com/endpoint/?page=2",
        "previous": null
    }
}
```

#### Authentication
- **Token-based**: JWT tokens for API authentication
- **Session-based**: Django sessions for web interface
- **Permissions**: Role-based access control

## 🚀 Performance Architecture

### Caching Strategy
```python
# Redis Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Database Optimization
- **Indexes**: Strategic database indexes for performance
- **Query Optimization**: Select_related and prefetch_related
- **Connection Pooling**: Database connection management
- **Query Caching**: Frequently accessed data caching

### Static File Optimization
- **CDN Integration**: Content delivery network
- **File Compression**: Gzip compression
- **Image Optimization**: Automatic image resizing
- **Browser Caching**: Cache headers for static files

## 🔐 Security Architecture

### Authentication & Authorization
```python
# Security Middleware Stack
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Security Features
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Protection**: Cross-site scripting prevention
- **SQL Injection Prevention**: ORM-based query protection
- **File Upload Security**: Secure file handling
- **Password Security**: Strong password requirements

### Data Protection
- **Input Validation**: Server-side validation
- **Data Sanitization**: Clean user input
- **Encryption**: Sensitive data encryption
- **Audit Logging**: User action tracking

## 📱 Frontend Architecture

### Template Structure
```
templates/
├── base.html                 # Base template
├── home.html                 # Home page
├── auth/
│   ├── login.html
│   ├── register.html
│   └── password_reset.html
├── challenges/
│   ├── list.html
│   ├── create.html
│   ├── detail.html
│   └── edit.html
├── profile.html
├── leaderboard.html
└── admin/
    ├── timeslots.html
    └── grounds.html
```

### Static File Organization
```
static/
├── css/
│   ├── bootstrap.min.css
│   ├── custom.css
│   └── responsive.css
├── js/
│   ├── jquery.min.js
│   ├── bootstrap.min.js
│   ├── custom.js
│   └── api.js
└── img/
    ├── logo.png
    ├── default-avatar.png
    └── backgrounds/
```

### JavaScript Architecture
```javascript
// API Client
class ChallengeAPI {
    static async createChallenge(data) {
        const response = await fetch('/api/challenges/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }
}

// Form Validation
class FormValidator {
    static validateChallengeForm(formData) {
        const errors = {};
        if (!formData.opponent) {
            errors.opponent = 'Opponent is required';
        }
        return errors;
    }
}
```

## 🔄 Real-time Features

### WebSocket Integration
```python
# WebSocket Consumer
class ChallengeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'challenges'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
    async def challenge_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'challenge_update',
            'data': event['data']
        }))
```

### Notification System
```python
# Notification Service
class NotificationService:
    @staticmethod
    def send_challenge_notification(user, challenge, action):
        notification = Notification.objects.create(
            user=user,
            title=f"Challenge {action}",
            body=f"Challenge with {challenge.creator.username} has been {action}",
            link=f"/challenges/{challenge.id}/"
        )
        # Send real-time notification
        send_websocket_notification(user, notification)
```

## 📊 Monitoring & Logging

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'challengehub.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
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
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Performance Monitoring
```python
# Custom Middleware for Performance Tracking
class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        
        # Log performance metrics
        logger.info(f"Request {request.path} took {end_time - start_time:.2f}s")
        return response
```

## 🚀 Deployment Architecture

### Production Environment
```
Load Balancer (Nginx)
    ↓
Application Servers (Gunicorn + Django)
    ↓
Database Server (PostgreSQL)
    ↓
Cache Server (Redis)
    ↓
File Storage (AWS S3 / Local)
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

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
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/challengehub
      - REDIS_URL=redis://redis:6379/0
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=challengehub
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🔧 Configuration Management

### Environment Variables
```bash
# Production Environment
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/challengehub
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=challengehub.com,www.challengehub.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Settings Management
```python
# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['challengehub.com', 'www.challengehub.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

## 📈 Scalability Considerations

### Horizontal Scaling
- **Load Balancing**: Multiple application servers
- **Database Sharding**: Distribute data across databases
- **CDN Integration**: Global content delivery
- **Microservices**: Break down monolithic structure

### Vertical Scaling
- **Server Resources**: Increase CPU, RAM, storage
- **Database Optimization**: Query optimization, indexing
- **Caching Strategy**: Multi-level caching
- **Code Optimization**: Performance improvements

## 🔄 Backup & Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
pg_dump challengehub > backup_$(date +%Y%m%d_%H%M%S).sql
aws s3 cp backup_*.sql s3://challengehub-backups/
```

### File Backup
```bash
# Media files backup
rsync -av /app/media/ /backup/media/
aws s3 sync /backup/media/ s3://challengehub-media/
```

### Recovery Procedures
1. **Database Recovery**: Restore from latest backup
2. **File Recovery**: Restore media files from backup
3. **Application Recovery**: Redeploy from version control
4. **Data Validation**: Verify data integrity

---

This technical architecture documentation provides a comprehensive overview of the ChallengeHub system's technical implementation, ensuring maintainability, scalability, and performance.
