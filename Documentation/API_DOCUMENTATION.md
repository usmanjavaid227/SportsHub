# ChallengeHub - API Documentation

## 🌐 API Overview

ChallengeHub provides a comprehensive RESTful API for managing cricket challenges, user profiles, and system administration with advanced workflow management and real-time features.

**Base URL**: `http://localhost:8000/api/`
**API Version**: v1
**Authentication**: Token-based (JWT) or Session-based
**Features**: User journey optimization, data flow management, active challenge restrictions

## 🔐 Authentication

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    }
}
```

### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password1": "secure_password",
    "password2": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Logout
```http
POST /api/auth/logout/
Authorization: Bearer <token>
```

## 👤 User Management

### Get User Profile
```http
GET /api/users/profile/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "city": "Tampere",
        "bio": "Cricket enthusiast",
        "role": "allrounder",
        "experience_level": "intermediate",
        "preferred_batting_style": "right_handed",
        "preferred_bowling_style": "right_arm_medium",
        "years_playing": 5,
        "avatar": "/media/avatars/john_avatar.jpg",
        "profile": {
            "matches_played": 10,
            "wins": 7,
            "losses": 3,
            "rating": 1250.5,
            "batting_rating": 1200.0,
            "bowling_rating": 1300.0,
            "runs": 250,
            "wickets": 15,
            "win_percentage": 70.0
        }
    }
}
```

### Update User Profile
```http
PUT /api/users/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "city": "Tampere",
    "bio": "Updated bio",
    "role": "batter",
    "experience_level": "advanced",
    "preferred_batting_style": "left_handed",
    "preferred_bowling_style": "left_arm_spin",
    "years_playing": 6
}
```

### Get Public Profile
```http
GET /api/users/{user_id}/
```

### Get Leaderboard
```http
GET /api/users/leaderboard/
```

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "username": "john_doe",
            "rating": 1250.5,
            "matches_played": 10,
            "wins": 7,
            "win_percentage": 70.0
        },
        {
            "id": 2,
            "username": "jane_smith",
            "rating": 1200.0,
            "matches_played": 8,
            "wins": 5,
            "win_percentage": 62.5
        }
    ]
}
```

## 🏏 Challenge Management

### List Challenges
```http
GET /api/challenges/
```

**Query Parameters:**
- `status`: Filter by status (OPEN, PENDING, ACCEPTED, COMPLETED, CANCELLED)
- `creator`: Filter by creator ID
- `opponent`: Filter by opponent ID
- `ground`: Filter by ground ID
- `page`: Page number for pagination
- `limit`: Number of items per page

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "creator": {
                "id": 1,
                "username": "john_doe",
                "rating": 1250.5
            },
            "opponent": {
                "id": 2,
                "username": "jane_smith",
                "rating": 1200.0
            },
            "ground": {
                "id": 1,
                "name": "Tampere Cricket Ground",
                "address": "123 Cricket Street"
            },
            "status": "ACCEPTED",
            "challenge_type": "BATTING",
            "condition_text": "I will hit 3 sixes in this over",
            "metric": "SIXES",
            "target_value": 3,
            "over_count": 1,
            "scheduled_at": "2024-01-15T10:00:00Z",
            "creator_score": null,
            "opponent_score": null,
            "winner": null,
            "created_at": "2024-01-10T09:00:00Z",
            "updated_at": "2024-01-10T09:30:00Z"
        }
    ],
    "pagination": {
        "count": 25,
        "next": "http://api.example.com/challenges/?page=2",
        "previous": null
    }
}
```

### Create Challenge
```http
POST /api/challenges/
Authorization: Bearer <token>
Content-Type: application/json

{
    "opponent": 2,
    "challenge_type": "BATTING",
    "condition_text": "I will hit 3 sixes in this over",
    "metric": "SIXES",
    "target_value": 3,
    "over_count": 1,
    "time_slot": 1,
    "ground": 1,
    "scheduled_date": "2024-01-15"
}
```

### Get Challenge Details
```http
GET /api/challenges/{challenge_id}/
```

### Update Challenge
```http
PUT /api/challenges/{challenge_id}/
Authorization: Bearer <token>
Content-Type: application/json

{
    "condition_text": "Updated challenge condition",
    "target_value": 4
}
```

### Accept Challenge
```http
POST /api/challenges/{challenge_id}/accept/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "ACCEPTED",
        "message": "Challenge accepted successfully"
    }
}
```

### Cancel Challenge
```http
DELETE /api/challenges/{challenge_id}/
Authorization: Bearer <token>
```

### Create Open Challenge
```http
POST /api/challenges/open/
Authorization: Bearer <token>
Content-Type: application/json

{
    "challenge_type": "BOWLING",
    "condition_text": "I won't concede more than 2 sixes",
    "metric": "SIXES",
    "target_value": 2,
    "over_count": 1,
    "time_slot": 1,
    "ground": 1,
    "scheduled_date": "2024-01-15"
}
```

## 🏟️ Ground Management

### List Grounds
```http
GET /api/grounds/
```

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "name": "Tampere Cricket Ground",
            "address": "123 Cricket Street, Tampere",
            "lat": 61.4991,
            "lng": 23.7871,
            "approved": true
        }
    ]
}
```

### Get Ground Details
```http
GET /api/grounds/{ground_id}/
```

## ⏰ Time Slot Management

### List Time Slots
```http
GET /api/timeslots/
```

**Query Parameters:**
- `date`: Filter by specific date (YYYY-MM-DD)
- `active`: Filter by active status (true/false)

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "date": "2024-01-15",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "is_active": true,
            "max_challenges": 2,
            "current_count": 1,
            "is_available": true
        }
    ]
}
```

### Get Time Slots for Date
```http
GET /api/timeslots/date/{date}/
```

### Get Calendar Availability
```http
GET /api/calendar-availability/
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "2024-01-15": {
            "total_slots": 3,
            "available_slots": 2,
            "booked_slots": 1,
            "color": "green"
        },
        "2024-01-16": {
            "total_slots": 2,
            "available_slots": 0,
            "booked_slots": 2,
            "color": "red"
        }
    }
}
```

## 📰 News Management

### List News
```http
GET /api/news/
```

**Query Parameters:**
- `featured`: Filter featured news (true/false)
- `published`: Filter published news (true/false)
- `page`: Page number for pagination

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "title": "New Cricket Season Begins",
            "summary": "Exciting new season with updated rules",
            "content": "Full news article content...",
            "image": "/media/news_images/season2024.jpg",
            "author": {
                "id": 1,
                "username": "admin"
            },
            "published": true,
            "featured": true,
            "created_at": "2024-01-10T09:00:00Z",
            "published_at": "2024-01-10T10:00:00Z"
        }
    ]
}
```

### Get News Details
```http
GET /api/news/{news_id}/
```

## 🔔 Notifications

### List Notifications
```http
GET /api/notifications/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "title": "Challenge Accepted",
            "body": "Your challenge has been accepted by jane_smith",
            "link": "/challenges/1/",
            "is_read": false,
            "created_at": "2024-01-10T09:30:00Z"
        }
    ]
}
```

### Mark Notification as Read
```http
PUT /api/notifications/{notification_id}/read/
Authorization: Bearer <token>
```

### Mark All Notifications as Read
```http
PUT /api/notifications/read-all/
Authorization: Bearer <token>
```

## 👨‍💼 Admin Endpoints

### Admin Challenge Management
```http
GET /api/admin/challenges/
Authorization: Bearer <admin_token>
```

### Confirm Challenge Scores
```http
POST /api/admin/challenges/{challenge_id}/confirm-scores/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "creator_score": 15,
    "opponent_score": 12,
    "winner": "creator"
}
```

### Time Slot Management
```http
POST /api/admin/timeslots/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "date": "2024-01-20",
    "start_time": "10:00:00",
    "end_time": "11:00:00",
    "max_challenges": 2
}
```

### Ground Management
```http
PUT /api/admin/grounds/{ground_id}/approve/
Authorization: Bearer <admin_token>
```

## 📊 Statistics & Analytics

### User Statistics
```http
GET /api/users/{user_id}/stats/
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "matches_played": 10,
        "wins": 7,
        "losses": 3,
        "win_percentage": 70.0,
        "rating": 1250.5,
        "batting_rating": 1200.0,
        "bowling_rating": 1300.0,
        "runs": 250,
        "wickets": 15,
        "balls_faced": 300,
        "balls_bowled": 200,
        "average_runs_per_match": 25.0,
        "average_wickets_per_match": 1.5
    }
}
```

### Platform Statistics
```http
GET /api/admin/statistics/
Authorization: Bearer <admin_token>
```

## 🔍 Search & Filtering

### Search Challenges
```http
GET /api/challenges/search/
```

**Query Parameters:**
- `q`: Search query
- `challenge_type`: Filter by challenge type
- `status`: Filter by status
- `date_from`: Filter from date
- `date_to`: Filter to date

### Advanced Filtering
```http
GET /api/challenges/?status=OPEN&challenge_type=BATTING&ground=1&page=1&limit=10
```

## 📱 WebSocket Events

### Real-time Notifications
```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/challenges/');

// Listen for challenge updates
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'challenge_update') {
        // Handle challenge update
        updateChallengeDisplay(data.data);
    }
};
```

### Available Events
- `challenge_created`: New challenge created
- `challenge_accepted`: Challenge accepted
- `challenge_completed`: Challenge completed
- `notification`: New notification received

## 🚨 Error Handling

### Error Response Format
```json
{
    "status": "error",
    "message": "Error description",
    "errors": {
        "field_name": ["Specific error message"]
    },
    "code": "ERROR_CODE"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Form validation failed
- `PERMISSION_DENIED`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `AUTHENTICATION_REQUIRED`: Authentication required
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## 🔧 Rate Limiting

### Rate Limits
- **Authentication**: 5 requests per minute
- **API Calls**: 100 requests per hour per user
- **File Uploads**: 10 uploads per hour per user
- **Challenge Creation**: 3 challenges per day per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📝 API Versioning

### Version Header
```http
Accept: application/vnd.challengehub.v1+json
```

### Version in URL
```
/api/v1/challenges/
/api/v2/challenges/  # Future version
```

## 🔐 Security Considerations

### HTTPS Only
All API endpoints require HTTPS in production.

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "https://challengehub.com",
    "https://www.challengehub.com",
]
```

### Input Validation
All input data is validated and sanitized before processing.

### SQL Injection Prevention
All database queries use Django ORM to prevent SQL injection.

---

This comprehensive API documentation provides all the necessary information for developers to integrate with the ChallengeHub platform effectively.
