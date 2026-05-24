from .base import *

DEBUG = False

# ✅ Use test database
DATABASES["default"]["NAME"] = "test_bizbuch"

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [],
}

# ✅ Fast password hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ✅ Disable real email sending
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ✅ Disable OTP email
OTP_VERIFICATION_ENABLED = False