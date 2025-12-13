from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    has_completed_onboarding = models.BooleanField(default=False)
