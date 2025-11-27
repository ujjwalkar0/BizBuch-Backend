from django.db import models
from django.utils import timezone
from datetime import timedelta

class PasswordReset(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    attempt_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self, minutes=10):
        return timezone.now() > (self.created_at + timedelta(minutes=minutes))

    def __str__(self):
        return f"PasswordReset({self.email})"
