import os
from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from accounts.models import PendingUser
from accounts.utils import generate_otp, send_otp_email
from profiles.models import Profile

from core.errors import AppError
from core.exceptions import AppException


User = get_user_model()

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
MAX_RESENDS = 3


def is_otp_verification_enabled():
    return os.environ.get('OTP_VERIFICATION_ENABLED', 'True').lower() in ('true', '1', 'yes')


class RegistrationService:

    @staticmethod
    def register(
        username,
        email,
        raw_password,
        first_name="",
        last_name="",
        recaptcha_token=None,
        recaptcha_validator=None
    ):
        email = email.lower()

        # 🔒 Recaptcha validation
        if recaptcha_token and recaptcha_validator:
            if not recaptcha_validator(recaptcha_token):
                raise AppException(AppError.RECAPTCHA_FAILED)

        # 🔍 Check existing users
        if User.objects.filter(email=email).exists():
            raise AppException(AppError.EMAIL_ALREADY_REGISTERED)

        if User.objects.filter(username__iexact=username).exists():
            raise AppException(AppError.USERNAME_TAKEN)

        hashed_password = make_password(raw_password)

        pending = PendingUser.objects.filter(email=email).first()

        # 🔁 Existing pending user (resend logic)
        if pending:
            if pending.is_expired(OTP_EXPIRY_MINUTES):
                pending.delete()
                raise AppException(AppError.OTP_EXPIRED)

            if pending.resend_count >= MAX_RESENDS:
                raise AppException(AppError.OTP_MAX_RESENDS)

            pending.otp = generate_otp()
            pending.resend_count += 1
            pending.attempt_count = 0
            pending.created_at = timezone.now()
            pending.username = username
            pending.password = hashed_password
            pending.first_name = first_name
            pending.last_name = last_name
            pending.save()

        # 🆕 New pending user
        else:
            pending = PendingUser.objects.create(
                email=email,
                username=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                otp=generate_otp(),
                attempt_count=0,
                resend_count=0,
                created_at=timezone.now()
            )

        # 📧 Send OTP (safe)
        if is_otp_verification_enabled():
            try:
                send_otp_email(email, pending.otp, username=username)
            except Exception:
                raise AppException(AppError.EMAIL_SEND_FAILED)
        return pending
    
    @staticmethod
    def resend_otp(email):
        email = email.lower()

        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            raise AppException(AppError.OTP_NOT_FOUND)

        if pending.is_expired(OTP_EXPIRY_MINUTES):
            pending.delete()
            raise AppException(AppError.OTP_EXPIRED)

        if pending.resend_count >= MAX_RESENDS:
            raise AppException(AppError.OTP_MAX_RESENDS)

        pending.otp = generate_otp()
        pending.resend_count += 1
        pending.attempt_count = 0
        pending.created_at = timezone.now()
        pending.save()

        try:
            send_otp_email(email, pending.otp, username=pending.username)
        except Exception:
            pass

        return pending

    @staticmethod
    def verify_otp_and_create_user(email, otp):
        email = email.lower()

        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            raise AppException(AppError.OTP_NOT_FOUND)

        if is_otp_verification_enabled():
            if pending.is_expired(OTP_EXPIRY_MINUTES):
                pending.delete()
                raise AppException(AppError.OTP_EXPIRED)

            if pending.attempt_count >= MAX_OTP_ATTEMPTS:
                pending.delete()
                raise AppException(AppError.OTP_MAX_ATTEMPTS)

            if pending.otp != otp:
                pending.attempt_count += 1
                pending.save(update_fields=["attempt_count"])
                raise AppException(AppError.OTP_INVALID)

        # 🔒 Atomic user creation
        with transaction.atomic():
            user = User.objects.create(
                username=pending.username,
                email=pending.email,
                first_name=pending.first_name,
                last_name=pending.last_name,
                password=pending.password,
            )

            Profile.objects.create(
                user=user,
                display_name=user.username
            )

            pending.delete()

        return user

    @staticmethod
    def cleanup_expired(minutes=OTP_EXPIRY_MINUTES):
        cutoff = timezone.now() - timedelta(minutes=minutes)
        PendingUser.objects.filter(created_at__lt=cutoff).delete()
