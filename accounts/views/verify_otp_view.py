from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling
from accounts.serializers import VerifyOTPSerializer
from accounts.services import RegistrationService
from accounts.throttle.anonrate_throttle import VerifyThrottle


class VerifyOTPCreateUserView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [VerifyThrottle]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = RegistrationService.verify_otp_and_create_user(data["email"], data["otp"])
            return Response({"detail":"Account created successfully"}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
