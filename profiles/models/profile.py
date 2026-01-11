from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Basic Info
    display_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)  # S3 key for avatar image
    
    # Professional Info (in addition to User model fields)
    company_logo = models.CharField(max_length=255, blank=True, null=True)  # S3 key for company logo
    cover_image = models.CharField(max_length=255, blank=True, null=True)  # S3 key for cover/banner image
    
    # Skills
    skills = models.JSONField(default=list, blank=True)  # Array of skills

    # Privacy
    is_public = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name




