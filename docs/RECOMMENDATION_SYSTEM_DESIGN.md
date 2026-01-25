# Recommendation System Design - BizBuch

## Overview

This document outlines the architecture decisions and implementation plan for adding a recommendation engine to the BizBuch social networking platform.

---

## Current Architecture

### Existing Event Hooks

The codebase already has an event-driven pattern with service hooks:

**PostRecommendationService** (`intelligence/services/post_recommendation_service.py`):
- `on_comment_added(comment)` - Triggered when a comment is added
- `on_new_like(post)` - Triggered when a post is liked
- `on_successfull_onboarding(user, topics)` - Triggered after user onboarding

**NotificationService** (`activity/services/notification_service.py`):
- `on_comment_added(comment)` - Creates activity for post owner
- `on_post_liked(like)` - Creates activity for post author
- `on_user_followed(follow)` - Creates activity for followed user

### Current Flow (Synchronous)

```
User Action → Django Service → NotificationService.on_*() → ActivityService → DB
                            → PostRecommendationService.on_*() → (TODO)
```

**Problem:** All processing happens synchronously in the request cycle.

---

## Architecture Options

### Option 1: Same Project with Celery + Redis (Phase 1 - Recommended Start)

**Pros:**
- Simple to develop and debug
- No new infrastructure (already have Redis)
- Shared database access
- Easier deployment

**Cons:**
- Recommendation logic can be CPU/memory heavy
- Scaling recommendations means scaling everything

**Best for:** MVP, small user base (<50k users)

```
User Action → Django Service → Celery Task → Compute Recommendations → Cache in Redis
```

### Option 2: Separate Microservice with Kafka (Phase 2 - Scale)

**Pros:**
- Independent scaling
- Can use different tech stack (Python ML libs, Go/Rust)
- Doesn't block main API
- Event replay for ML model retraining
- Multiple consumers for same events

**Cons:**
- More infrastructure complexity
- Network latency
- Data sync challenges

**Best for:** Production scale, ML-heavy recommendations

```
User Action → Django Service → Kafka Producer
                                    ↓
                          ┌─────────┴─────────┐
                          ↓                   ↓
              Notification Consumer    Recommendation Consumer
              (Django)                 (Separate Microservice)
```

---

## Recommended Phased Approach

### Phase 1: Celery + Redis (Start Here)

1. Keep recommendation logic in a separate Django app (`recommendations/` or use existing `intelligence/`)
2. Run heavy computation in Celery workers
3. Cache results in Redis

**Implementation:**
```python
# In services (e.g., like_service.py)
from intelligence.tasks import update_recommendations_task

class LikeService:
    @staticmethod
    def like_post(user, post_id):
        # ... existing code ...
        
        # Async recommendation update
        update_recommendations_task.delay(user.id, post_id, 'like')
```

```python
# intelligence/tasks.py
from celery import shared_task

@shared_task
def update_recommendations_task(user_id, post_id, action_type):
    # Heavy computation here
    PostRecommendationService.compute_recommendations(user_id, post_id, action_type)
```

### Phase 2: Extract to Microservice with Kafka

**When to move to Phase 2:**
- Recommendation computation takes >5 seconds
- You need ML models (TensorFlow, PyTorch)
- You have dedicated ML/data engineers
- Core API is slowing down

**Events to Publish:**

| Event | Topic | Payload |
|-------|-------|---------|
| User liked post | `user.activity` | `{event: "liked", user_id, post_id, timestamp}` |
| User commented | `user.activity` | `{event: "commented", user_id, post_id, comment_id, timestamp}` |
| User followed | `user.activity` | `{event: "followed", follower_id, following_id, timestamp}` |
| User viewed post | `user.activity` | `{event: "viewed", user_id, post_id, duration, timestamp}` |
| User onboarded | `user.lifecycle` | `{event: "onboarded", user_id, topics[], timestamp}` |

---

## Communication Patterns

| Pattern | Use Case |
|---------|----------|
| **Celery + Redis** | Background jobs, simple async tasks |
| **RabbitMQ** | Request-reply pattern, reliable delivery, dead-letter queues |
| **Kafka** | High-volume event streaming, event replay, multiple consumers |

### When to Use What

| Scenario | Choice |
|----------|--------|
| Simple async notifications | Celery + Redis |
| Feed generation fan-out | Celery + Redis or Kafka |
| Real-time recommendations | Kafka |
| ML model training pipeline | Kafka (event replay) |
| Analytics/tracking | Kafka |

---

## Docker Services Needed

### Phase 1 (Celery)
No new services - use existing Redis as broker.

Add Celery worker to docker-compose:
```yaml
celery_worker:
  build: .
  command: celery -A mysite worker --loglevel=info
  volumes:
    - .:/app
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
  depends_on:
    - redis
    - db
  networks:
    bizbuch_network:
      ipv4_address: 172.28.0.20
```

### Phase 2 (Kafka)
```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:latest
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
  networks:
    bizbuch_network:
      ipv4_address: 172.28.0.21

kafka:
  image: confluentinc/cp-kafka:latest
  depends_on:
    - zookeeper
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  ports:
    - "9092:9092"
  networks:
    bizbuch_network:
      ipv4_address: 172.28.0.22

kafka-ui:
  image: provectuslabs/kafka-ui:latest
  depends_on:
    - kafka
  environment:
    KAFKA_CLUSTERS_0_NAME: local
    KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
  ports:
    - "8080:8080"
  networks:
    bizbuch_network:
      ipv4_address: 172.28.0.23
```

---

## Recommendation Service Structure (Microservice)

```
recommendation-service/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI or Flask app
│   ├── config.py
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── activity_consumer.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── recommendation_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── feed_service.py
│   │   └── similarity_service.py
│   └── api/
│       ├── __init__.py
│       └── recommendations.py
```

---

## API Contract (Between Django & Recommendation Service)

### Get Recommendations
```
GET /api/recommendations/{user_id}/feed
Response: {
    "post_ids": [123, 456, 789],
    "scores": [0.95, 0.87, 0.82]
}
```

### Get Similar Users
```
GET /api/recommendations/{user_id}/similar-users
Response: {
    "user_ids": [10, 20, 30],
    "scores": [0.9, 0.8, 0.7]
}
```

---

## Data Required for Recommendations

### User Signals
- Posts liked
- Posts commented on
- Users followed
- Posts viewed (duration)
- Posts shared
- Onboarding topics selected

### Post Metadata
- Author
- Topics/tags
- Engagement metrics (likes, comments, shares)
- Created timestamp
- Content type (text, image, video)

### User Profile
- Industry
- Job title
- Location
- Interests (from onboarding)

---

## Next Steps

1. [ ] Set up Celery with existing Redis
2. [ ] Move `PostRecommendationService` logic to Celery tasks
3. [ ] Implement basic recommendation algorithm (collaborative filtering)
4. [ ] Add caching layer for computed recommendations
5. [ ] Monitor performance and decide on Kafka migration
6. [ ] (Future) Extract to separate microservice when needed

---

## Related Files

- `intelligence/services/post_recommendation_service.py` - Current recommendation hooks
- `activity/services/notification_service.py` - Notification event handlers
- `posts/services/like_service.py` - Like service with hooks
- `posts/services/comment_service.py` - Comment service with hooks
- `profiles/services/follow_service.py` - Follow service with hooks

---

*Document created: January 25, 2026*
*Last updated: January 25, 2026*
