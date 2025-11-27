from accounts.models import PasswordReset
from accounts.utils import generate_otp, send_otp_email
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PasswordResetService:

    def send_reset_otp(self, email):
        email = email.lower()

        # Only allow if user exists
        if not User.objects.filter(email__iexact=email).exists():
            raise ValueError("No user found with this email")

        otp = generate_otp()

        reset_obj, _ = PasswordReset.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "attempt_count": 0,
                "created_at": timezone.now(),
            }
        )

        send_otp_email(email, otp)
        return reset_obj
    
    def reset_password(self, email, otp, new_password):
        email = email.lower()

        try:
            reset_obj = PasswordReset.objects.get(email=email)
        except PasswordReset.DoesNotExist:
            raise ValueError("No reset request found")

        # check expiry
        if reset_obj.is_expired(10):
            reset_obj.delete()
            raise ValueError("OTP expired. Request a new one.")

        # brute force protection
        if reset_obj.attempt_count >= 5:
            reset_obj.delete()
            raise ValueError("Too many wrong attempts. Request a new OTP.")

        # verify OTP
        if reset_obj.otp != otp:
            reset_obj.attempt_count += 1
            reset_obj.save(update_fields=["attempt_count"])
            raise ValueError("Invalid OTP")

        # update user password
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValueError("User does not exist")

        user.set_password(new_password)
        user.save()

        # cleanup
        reset_obj.delete()

        return user
