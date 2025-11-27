from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from accounts.serializers import ResetPasswordSerializer
from accounts.services import PasswordResetService

reset_service = PasswordResetService()

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            reset_service.reset_password(
                email=data["email"],
                otp=data["otp"],
                new_password=data["new_password"]
            )
            return Response(
                {"detail": "Password reset successful"},
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
