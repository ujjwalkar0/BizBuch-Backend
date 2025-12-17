from django.conf import settings
from django.db import models


class ActivityPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_preferences",
    )

    notify_like = models.BooleanField(default=True)
    notify_comment = models.BooleanField(default=True)
    notify_follow = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
