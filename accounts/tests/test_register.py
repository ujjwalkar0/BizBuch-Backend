from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock

from accounts.models import PendingUser
from accounts.services.registration_service import RegistrationService
from core.errors import AppError
from core.exceptions import AppException

from rest_framework.settings import api_settings

User = get_user_model()


class TestRegisterSendOTP(APITestCase):

    def setUp(self):
        self.register_url = reverse("register_send_otp")
        self.resend_url = reverse("resend_otp")

        self.valid_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        self._original_throttles = api_settings.DEFAULT_THROTTLE_CLASSES
        api_settings.DEFAULT_THROTTLE_CLASSES = []

    def tearDown(self):
        api_settings.DEFAULT_THROTTLE_CLASSES = self._original_throttles

    # ✅ 1. SUCCESS CASE
    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["message"], "OTP sent to email.")

        self.assertTrue(
            PendingUser.objects.filter(email="test@example.com").exists()
        )

    # ❌ EMAIL ALREADY REGISTERED
    def test_register_email_already_registered(self):
        User.objects.create(
            username="existinguser",
            email="test@example.com",
            password="testpass"
        )

        response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "EMAIL_ALREADY_REGISTERED"
        )

    # ❌ USERNAME TAKEN
    def test_register_username_taken(self):
        User.objects.create(
            username="testuser",
            email="other@example.com",
            password="testpass"
        )

        response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "USERNAME_TAKEN"
        )

    # ❌ PASSWORD MISMATCH
    def test_register_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload["confirm_password"] = "WrongPassword123!"

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "VALIDATION_ERROR"
        )

        self.assertIn(
            "confirm_password",
            response.data["error"]["message"]
        )

    # ❌ 5. INVALID EMAIL FORMAT
    def test_register_invalid_email(self):
        payload = self.valid_payload.copy()
        payload["email"] = "invalid-email"

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "VALIDATION_ERROR"
        )

        self.assertIn(
            "email",
            response.data["error"]["message"]
        )

    # ❌ 6. MISSING REQUIRED FIELD
    def test_register_missing_fields(self):
        payload = {}

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "VALIDATION_ERROR"
        )

        self.assertIn(
            "username",
            response.data["error"]["message"]
        )

    # ❌ 7. WEAK PASSWORD
    def test_register_weak_password(self):
        payload = self.valid_payload.copy()
        payload["password"] = "123"
        payload["confirm_password"] = "123"

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["error"]["code"],
            "VALIDATION_ERROR"
        )

        self.assertIn(
            "password",
            response.data["error"]["message"]
        )

    def test_register_existing_pending_expired(self):
        PendingUser.objects.create(
            email="test@example.com",
            username="testuser",
            password="pass",
            otp="123",
            resend_count=0,
            attempt_count=0
        )

        with patch("accounts.models.PendingUser.is_expired", return_value=True):
            response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "OTP_EXPIRED")
        self.assertFalse(PendingUser.objects.filter(email="test@example.com").exists())

    def test_register_existing_pending_max_resend(self):
        PendingUser.objects.create(
            email="test@example.com",
            username="testuser",
            password="pass",
            otp="123",
            resend_count=3,
            attempt_count=0
        )

        response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "OTP_MAX_RESENDS")

    def test_register_existing_pending_success_resend(self):
        PendingUser.objects.create(
            email="test@example.com",
            username="testuser",
            password="pass",
            otp="123",
            resend_count=1,
            attempt_count=0
        )

        with patch(
            "accounts.services.registration_service.generate_otp",
            return_value="999"
        ), patch(
            "accounts.services.registration_service.send_otp_email"
        ), patch(
            "accounts.services.registration_service.is_otp_verification_enabled",
            return_value=True
        ):

            response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 202)

        pending = PendingUser.objects.get(email="test@example.com")
        self.assertEqual(pending.otp, "999")
        self.assertEqual(pending.resend_count, 2)
        
    def test_register_email_send_failure(self):
        with patch(
            "accounts.services.registration_service.is_otp_verification_enabled",
            return_value=True
        ), patch(
            "accounts.services.registration_service.send_otp_email",
            side_effect=Exception
        ):
            response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "EMAIL_SEND_FAILED")

    def test_register_recaptcha_failure(self):
        with patch(
            "accounts.services.registration_service.RegistrationService.register",
            side_effect=AppException(AppError.RECAPTCHA_FAILED)
        ):
            response = self.client.post(self.register_url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "RECAPTCHA_FAILED")

    def test_resend_otp_not_found(self):
        response = self.client.post(
            self.resend_url,
            {"email": "notfound@mail.com"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "OTP_NOT_FOUND")

    def test_resend_otp_expired(self):
        PendingUser.objects.create(
            email="test@example.com",
            username="testuser",
            password="pass",
            otp="123",
            resend_count=0,
            attempt_count=0
        )

        with patch("accounts.models.PendingUser.is_expired", return_value=True):
            response = self.client.post(
                self.resend_url,
                {"email": "test@example.com"},
                format="json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "OTP_EXPIRED")

    def test_resend_otp_success(self):
        PendingUser.objects.create(
            email="test@example.com",
            username="testuser",
            password="pass",
            otp="123",
            resend_count=1,
            attempt_count=0
        )

        with patch("accounts.utils.generate_otp", return_value="888"), \
             patch("accounts.utils.send_otp_email"):

            response = self.client.post(
                self.resend_url,
                {"email": "test@example.com"},
                format="json"
            )

        self.assertEqual(response.status_code, 200)

        pending = PendingUser.objects.get(email="test@example.com")
        self.assertEqual(pending.otp, "888")
        self.assertEqual(pending.resend_count, 2)