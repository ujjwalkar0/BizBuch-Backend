from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from accounts.serializers import ForgotPasswordSerializer
from ..services import PasswordResetService

reset_service = PasswordResetService()

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            reset_service.send_reset_otp(email)
            return Response(
                {"detail": "Password reset OTP sent"},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
