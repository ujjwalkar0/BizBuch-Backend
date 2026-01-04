from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    
    content = models.TextField(blank=True)
    image = models.CharField(max_length=255)
    poll = models.JSONField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    feelings = models.CharField(max_length=100, blank=True)
    privacy = models.CharField(max_length=50, default="public")

    created_at = models.DateTimeField(auto_now_add=True)

    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.author.username}'s Post"