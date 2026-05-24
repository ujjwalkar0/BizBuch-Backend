from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.throttle.login_throttle import LoginThrottle
from accounts.serializers import LoginSerializer
from core.response import error_response, success_response
from accounts.serializers.user_serializer import UserSerializer

# views.py
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))
            message = first_error[0] if isinstance(first_error, list) else str(first_error)
            return error_response(
                code="VALIDATION_ERROR",
                message=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return success_response(data={
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })