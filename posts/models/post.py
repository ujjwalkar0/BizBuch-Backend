from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)

    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Post"