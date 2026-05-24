from rest_framework.generics import GenericAPIView
from rest_framework import status, permissions
from accounts.serializers import RegisterSerializer
from accounts.services import RegistrationService
from accounts.throttle.register_throttle import RegisterThrottle
from accounts.utils import verify_recaptcha_token
from core.response import success_response


class RegisterSendOTPView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterThrottle]
    serializer_class = RegisterSerializer
    

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        RegistrationService.register(
            username=data["username"],
            email=data["email"],
            raw_password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            recaptcha_token=data.get("recaptcha_token"),
            recaptcha_validator=verify_recaptcha_token
        )

        return success_response(
            data={"message": "OTP sent to email."},
            status=status.HTTP_202_ACCEPTED
        )