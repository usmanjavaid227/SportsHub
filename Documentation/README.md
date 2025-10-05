# ChallengeHub - Cricket Challenge Platform

## 🏏 Overview

ChallengeHub is a comprehensive Django-based web application designed for cricket enthusiasts to create, manage, and participate in cricket challenges. The platform facilitates match scheduling, player management, ground booking, and real-time challenge tracking with an integrated rating system.

## 🚀 Features

### Core Features
- **User Authentication & Profiles**: Complete user registration, login, and profile management with cricket-specific fields
- **Challenge Management**: Create, accept, edit, and delete cricket challenges with one active challenge restriction
- **Ground Management**: Admin-approved cricket grounds with location tracking and approval workflow
- **Time Slot Booking**: Predefined time slots for challenge scheduling with capacity management
- **Rating System**: Elo-style rating system for players with separate batting/bowling ratings
- **Leaderboard**: Player rankings based on performance with real-time updates
- **News System**: Admin-managed news and updates with featured content
- **Notifications**: Real-time notifications for challenge updates and system events
- **Admin Panel**: Comprehensive admin interface for system management and oversight
- **User Journey Optimization**: Streamlined user onboarding and engagement workflows
- **Data Flow Management**: Efficient data processing from input to output with real-time updates

### Challenge Types
1. **Batter Challenge**: "I will hit X sixes in this over"
2. **Bowler Challenge**: "I won't concede more than X sixes"
3. **Full Challenge**: Both players bat and bowl, winner decided after completion
4. **Open Challenges**: Public challenges that any player can accept
5. **Single Wicket Challenge**: Specialized single wicket format challenges

### User Roles
- **Regular Users**: Can create challenges (one at a time), accept challenges, view leaderboard, manage profile
- **Admin Users**: Full system access, ground approval, time slot management, score confirmation, user management
- **Superuser**: Complete system control with advanced administrative capabilities

## 🏗️ System Architecture

### Technology Stack
- **Backend**: Django 5.2.6
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Django's built-in authentication system
- **API**: Django REST Framework
- **Real-time**: Django Channels (WebSocket support)
- **Image Processing**: Pillow, OpenCV
- **Data Analysis**: NumPy

### Project Structure
```
ChallengeHub/
├── tampere_cricket/          # Main Django project
│   ├── accounts/             # User management app
│   ├── matches/              # Challenge management app
│   ├── grounds/              # Ground management app
│   ├── news/                 # News management app
│   ├── notifications/        # Notification system
│   └── tampere_cricket/     # Project settings
├── templates/                # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │     Profile    │    │   Challenge     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │◄──►│ user (FK)       │    │ id (PK)         │
│ username        │    │ matches_played │    │ creator (FK)    │
│ email           │    │ wins           │    │ opponent (FK)   │
│ first_name      │    │ losses         │    │ ground (FK)     │
│ last_name       │    │ rating         │    │ status          │
│ phone           │    │ batting_rating │    │ challenge_type  │
│ city            │    │ bowling_rating │    │ condition_text  │
│ bio             │    │ runs           │    │ metric          │
│ role            │    │ wickets       │    │ target_value    │
│ experience_level│    │ balls_faced    │    │ over_count      │
│ avatar          │    │ balls_bowled   │    │ scheduled_at    │
│ is_staff        │    │ fcm_token      │    │ time_slot (FK)  │
│ is_superuser    │    └─────────────────┘    │ creator_score   │
└─────────────────┘                          │ opponent_score  │
                                             │ winner (FK)     │
┌─────────────────┐    ┌─────────────────┐    │ created_at      │
│     Ground      │    │   TimeSlot      │    │ updated_at      │
├─────────────────┤    ├─────────────────┤    └─────────────────┘
│ id (PK)         │    │ id (PK)         │
│ name            │    │ date            │
│ address         │    │ start_time      │
│ lat             │    │ end_time        │
│ lng             │    │ is_active       │
│ approved        │    │ max_challenges  │
└─────────────────┘    │ created_by (FK) │
                        │ created_at      │
┌─────────────────┐    └─────────────────┘
│      News       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ content         │
│ summary         │
│ image           │
│ author (FK)     │
│ published       │
│ featured        │
│ created_at      │
│ updated_at      │
│ published_at    │
└─────────────────┘

┌─────────────────┐
│  Notification   │
├─────────────────┤
│ id (PK)         │
│ user (FK)       │
│ title           │
│ body            │
│ link            │
│ is_read         │
│ created_at      │
└─────────────────┘
```

### Key Relationships
- **User ↔ Profile**: One-to-One relationship
- **User ↔ Challenge**: One-to-Many (creator, opponent, winner)
- **Ground ↔ Challenge**: One-to-Many
- **TimeSlot ↔ Challenge**: One-to-Many
- **User ↔ News**: One-to-Many (author)
- **User ↔ Notification**: One-to-Many

## 🔄 Workflow Diagrams

### Challenge Creation Workflow
```
User Login → Profile Check → Create Challenge → Select Type → Choose Opponent/Ground → Schedule Time → Submit → Status: OPEN/PENDING
```

### Challenge Acceptance Workflow
```
View Challenge → Check Eligibility → Accept Challenge → Status: ACCEPTED → Admin Score Confirmation → Status: COMPLETED → Rating Update
```

### User Registration Workflow
```
Register → Email Verification → Complete Profile → Set Preferences → Start Using Platform
```

### Admin Management Workflow
```
Admin Login → Ground Approval → Time Slot Management → Challenge Monitoring → Score Confirmation → System Maintenance
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ChallengeHub
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   # Username: admin
   # Email: admin@example.com
   # Password: admin123
   ```

6. **Load Sample Data (Optional)**
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Open browser: `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
For production, update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'challengehub_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📱 API Endpoints

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration

### Challenge Endpoints
- `GET /api/challenges/` - List all challenges
- `POST /api/challenges/` - Create new challenge
- `GET /api/challenges/{id}/` - Get challenge details
- `PUT /api/challenges/{id}/` - Update challenge
- `DELETE /api/challenges/{id}/` - Delete challenge
- `POST /api/challenges/{id}/accept/` - Accept challenge

### User Endpoints
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile
- `GET /api/users/leaderboard/` - Get leaderboard

### Admin Endpoints
- `GET /api/admin/timeslots/` - Manage time slots
- `POST /api/admin/timeslots/` - Create time slot
- `PUT /api/admin/timeslots/{id}/` - Update time slot
- `DELETE /api/admin/timeslots/{id}/` - Delete time slot

## 🎯 Usage Guide

### For Regular Users

1. **Registration & Profile Setup**
   - Register with email and password
   - Complete profile with cricket experience details
   - Upload profile picture

2. **Creating Challenges**
   - Navigate to "Create Challenge"
   - Choose challenge type (Batter/Bowler/Full)
   - Select opponent or create open challenge
   - Choose ground and time slot
   - Submit challenge

3. **Accepting Challenges**
   - Browse available challenges
   - View challenge details
   - Accept if eligible

4. **Managing Profile**
   - Update personal information
   - View statistics and ratings
   - Check notifications

### For Administrators

1. **Ground Management**
   - Approve/reject ground submissions
   - Manage ground information
   - Set availability

2. **Time Slot Management**
   - Create time slots for different dates
   - Set maximum challenges per slot
   - Activate/deactivate slots

3. **Challenge Oversight**
   - Monitor all challenges
   - Confirm scores and results
   - Update player ratings

4. **News Management**
   - Create and publish news articles
   - Manage featured content
   - Update platform announcements

## 🔐 Security Features

- **Authentication**: Django's built-in authentication system
- **Authorization**: Role-based access control
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Form validation and sanitization
- **File Upload Security**: Image upload restrictions
- **Password Security**: Strong password requirements

## 📊 Performance Features

- **Database Optimization**: Select_related and prefetch_related queries
- **Caching**: Template and database query caching
- **Image Optimization**: Automatic image resizing and compression
- **Pagination**: Efficient data loading for large datasets
- **AJAX Support**: Real-time updates without page refresh

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test matches

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage
- Unit tests for models and forms
- Integration tests for views
- API endpoint testing
- User authentication testing

## 🚀 Deployment

### Production Deployment Checklist

1. **Environment Setup**
   - Set `DEBUG = False`
   - Configure production database
   - Set up static file serving
   - Configure media file handling

2. **Security Configuration**
   - Update `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Set up HTTPS
   - Configure CORS settings

3. **Database Migration**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. **Web Server Configuration**
   - Configure Nginx/Apache
   - Set up Gunicorn/uWSGI
   - Configure SSL certificates

## 📈 Monitoring & Analytics

### Built-in Monitoring
- Django Debug Toolbar (development)
- Database query monitoring
- Performance metrics
- Error logging

### Recommended Tools
- **Sentry**: Error tracking and monitoring
- **Google Analytics**: User behavior analytics
- **New Relic**: Application performance monitoring
- **LogRocket**: User session recording

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test
4. Commit changes: `git commit -m 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Create Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Write unit tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Contact

### Getting Help
- Check the documentation
- Search existing issues
- Create new issue with detailed description
- Contact: support@challengehub.com

### Common Issues
1. **Database Connection Issues**: Check database configuration
2. **Static Files Not Loading**: Run `python manage.py collectstatic`
3. **Permission Errors**: Check file permissions and user groups
4. **Import Errors**: Ensure all dependencies are installed

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Basic challenge management
- User authentication
- Admin panel
- Rating system

### Planned Features
- Mobile app integration
- Advanced analytics
- Tournament management
- Social features
- Payment integration

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Note**: This is a comprehensive documentation for the ChallengeHub cricket challenge platform. For specific implementation details, refer to the source code and inline comments.