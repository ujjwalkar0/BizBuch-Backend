from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_otp_email(email, otp, username=None):
    subject = "Your verification code"
    message = render_to_string("emails/otp.txt", {"otp": otp, "username": username})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
