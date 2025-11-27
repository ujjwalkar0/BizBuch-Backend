import random
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def generate_otp(length=6):
    low = 10**(length-1)
    return str(random.randint(low, 10**length - 1))

def send_otp_email(email, otp, username=None):
    subject = "Your verification code"
    message = render_to_string("emails/otp.txt", {"otp": otp, "username": username})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

def verify_recaptcha_token(token):
    """
    Implement server-side reCAPTCHA verification here.
    Return True if token valid, False otherwise.
    Placeholder - implement if you use reCAPTCHA.
    """
    # Example: use requests to call Google's endpoint with settings.RECAPTCHA_SECRET_KEY
    return True
