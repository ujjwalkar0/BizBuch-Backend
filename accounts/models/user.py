from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # Onboarding
    has_completed_onboarding = models.BooleanField(default=False)
    
    # Professional Info
    headline = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Senior Software Engineer at Google"
    current_position = models.CharField(max_length=255, blank=True, null=True)  # Job title
    company = models.CharField(max_length=255, blank=True, null=True)  # Current company name
    industry = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Technology", "Finance"
    
    # Contact & Links
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    
    # Verification & Status
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('personal', 'Personal'),
            ('business', 'Business'),
            ('creator', 'Creator'),
        ],
        default='personal'
    )
    
    # Additional
    joined_date = models.DateTimeField(default=timezone.now)
    open_to_work = models.BooleanField(default=False)
    open_to_hire = models.BooleanField(default=False)

