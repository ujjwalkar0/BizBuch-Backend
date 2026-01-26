# BizBuch Backend

A Django-based social networking platform backend with real-time chat, posts, profiles, and activity feeds.

## 🚀 Features

- **User Authentication** - Registration, login, password reset with OTP verification
- **Profiles** - User profiles with work experience, education, skills, and locations
- **Posts** - Create, like, and comment on posts
- **Chat** - Real-time messaging with WebSocket support
- **Activity Feed** - Notifications for likes, comments, follows, and connections
- **Connections** - Follow users and manage connections
- **Onboarding** - User onboarding flow with topic selection

## 🛠️ Tech Stack

- **Framework**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL 15
- **Cache/Message Broker**: Redis 7
- **ASGI Server**: Daphne (WebSocket support)
- **Object Storage**: MinIO (S3-compatible)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)

## 🏃 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd BizBuch-Backend

# Start all services
docker compose up -d

# View logs
docker compose logs -f web
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs/
- **pgAdmin**: http://localhost:5050
- **RedisInsight**: http://localhost:5540
- **MinIO Console**: http://localhost:9001

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit with your settings

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `DB_HOST` | PostgreSQL host | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `bizbuch` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `REDIS_HOST` | Redis host | `redis` |
| `AWS_ACCESS_KEY_ID` | MinIO/S3 access key | - |
| `AWS_SECRET_ACCESS_KEY` | MinIO/S3 secret key | - |
| `AWS_S3_ENDPOINT_URL` | S3 endpoint URL | - |
| `AWS_S3_BUCKET` | S3 bucket name | `bizbuch` |
| `OTP_VERIFICATION_ENABLED` | Enable OTP verification | `False` |

## 📁 Project Structure

```
BizBuch-Backend/
├── accounts/          # User authentication & management
├── activity/          # Notifications & activity feed
├── chat/              # Real-time messaging
├── core/              # Core middleware & utilities
├── intelligence/      # Recommendation services
├── onboarding/        # User onboarding flow
├── posts/             # Posts, likes, comments
├── profiles/          # User profiles & connections
├── uploads/           # File upload services (S3)
├── mysite/            # Django project settings
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🐳 Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Rebuild after dependency changes
docker compose up --build web

# Restart web service (for code changes)
docker compose restart web

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Access Django shell
docker compose exec web python manage.py shell

# View logs
docker compose logs -f web
```

## 🧪 Running Tests

```bash
# Using Docker
docker compose exec web python manage.py test

# Local
python manage.py test
```

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Contributors

- BizBuch Team
