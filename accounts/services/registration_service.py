from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from accounts.models import PendingUser
from accounts.utils import generate_otp, send_otp_email

User = get_user_model()

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
MAX_RESENDS = 3

class RegistrationService:
    """
    Single responsibility: handle register -> create/update PendingUser and send OTP.
    """

    def register(self, username, email, raw_password, first_name="", last_name="", recaptcha_token=None, recaptcha_validator=None):
        email = email.lower()
        # recaptcha validation
        if recaptcha_token and recaptcha_validator and not recaptcha_validator(recaptcha_token):
            raise ValueError("reCAPTCHA failed")

        # Prevent creating pending if a real user with same email/username already exists
        if User.objects.filter(email__iexact=email).exists():
            raise ValueError("Email already registered")
        if User.objects.filter(username__iexact=username).exists():
            raise ValueError("Username already taken")

        # Hash password immediately
        hashed = make_password(raw_password)

        otp = generate_otp()
        pending, _ = PendingUser.objects.update_or_create(
            email=email,
            defaults={
                "username": username,
                "password": hashed,
                "first_name": first_name,
                "last_name": last_name,
                "otp": otp,
                "attempt_count": 0,
                "resend_count": 0,
                "created_at": timezone.now()
            }
        )

        # Send email (use Celery in prod)
        send_otp_email(email, otp, username=username)
        return pending

    def resend_otp(self, email):
        email = email.lower()
        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            raise ValueError("No pending registration found")

        if pending.is_expired(OTP_EXPIRY_MINUTES):
            pending.delete()
            raise ValueError("OTP expired. Please register again.")

        if pending.resend_count >= MAX_RESENDS:
            raise ValueError("Too many resends. Try later.")

        new_otp = generate_otp()
        pending.otp = new_otp
        pending.resend_count += 1
        pending.attempt_count = 0
        pending.created_at = timezone.now()
        pending.save()

        send_otp_email(email, new_otp, username=pending.username)
        return pending

    def verify_otp_and_create_user(self, email, otp):
        email = email.lower()
        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            raise ValueError("No pending registration found")

        # expired
        if pending.is_expired(OTP_EXPIRY_MINUTES):
            pending.delete()
            raise ValueError("OTP expired. Please register again.")

        # brute force protection
        if pending.attempt_count >= MAX_OTP_ATTEMPTS:
            pending.delete()
            raise ValueError("Too many invalid attempts, please register again.")

        # check otp
        if pending.otp != otp:
            pending.attempt_count += 1
            pending.save(update_fields=["attempt_count"])
            raise ValueError("Invalid OTP")

        # create user using already-hashed password — use create() to avoid double-hash
        user = User.objects.create(
            username=pending.username,
            email=pending.email,
            first_name=pending.first_name,
            last_name=pending.last_name,
            password=pending.password,  # already hashed
        )

        # cleanup
        pending.delete()
        return user

    def cleanup_expired(self, minutes=OTP_EXPIRY_MINUTES):
        cutoff = timezone.now() - timedelta(minutes=minutes)
        PendingUser.objects.filter(created_at__lt=cutoff).delete()
