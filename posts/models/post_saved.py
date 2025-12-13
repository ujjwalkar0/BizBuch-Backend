from django.db import models
from posts.models.post import Post
from django.conf import settings

User = settings.AUTH_USER_MODEL

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
