from django.urls import path
from accounts.views import (
            RegisterSendOTPView, 
            ResendOTPView, 
            VerifyOTPCreateUserView, 
            LoginView, 
            ResetPasswordView, 
            ForgotPasswordView
        )

urlpatterns = [
    path("register/", RegisterSendOTPView.as_view(), name="register_send_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("verify-otp/", VerifyOTPCreateUserView.as_view(), name="verify_otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view()),
]
