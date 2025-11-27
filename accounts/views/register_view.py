from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.serializers import RegisterSerializer
from accounts.services import RegistrationService
from accounts.throttle.register_throttle import RegisterThrottle
from accounts.utils import verify_recaptcha_token


service = RegistrationService()

class RegisterSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterThrottle]
    serializer_class = RegisterSerializer


    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            pending = service.register(
                username=data["username"],
                email=data["email"],
                raw_password=data["password"],
                first_name=data.get("first_name",""),
                last_name=data.get("last_name",""),
                recaptcha_token=data.get("recaptcha_token"),
                recaptcha_validator=verify_recaptcha_token
            )
            return Response({"detail":"OTP sent to email"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

