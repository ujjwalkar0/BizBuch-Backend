from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.throttle.login_throttle import LoginThrottle
from accounts.serializers import LoginSerializer
from uploads.services import generate_presigned_view

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Get profile photo presigned URL
        profile_photo = None
        if hasattr(user, 'profile') and user.profile.avatar:
            profile_photo = generate_presigned_view(user.profile.avatar)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_photo": profile_photo,
            }
        }, status=status.HTTP_200_OK)
