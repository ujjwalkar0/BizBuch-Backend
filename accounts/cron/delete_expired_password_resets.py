from django.utils import timezone
from datetime import timedelta
from accounts.models import PasswordReset

def delete_expired_password_resets():
    cutoff = timezone.now() - timedelta(minutes=10)
    PasswordReset.objects.filter(created_at__lt=cutoff).delete()
