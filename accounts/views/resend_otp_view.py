from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.serializers import ResendOTPSerializer
from accounts.services import RegistrationService
from accounts.throttle.register_throttle import RegisterThrottle


class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterThrottle]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            RegistrationService.resend_otp(email)
            return Response({"detail": "OTP resent"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
