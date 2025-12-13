from django.db import models
from posts.models.post import Post
from django.conf import settings

User = settings.AUTH_USER_MODEL

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
