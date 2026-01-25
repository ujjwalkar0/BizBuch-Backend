from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from accounts.serializers import TokenValidateSerializer
from uploads.services import generate_presigned_view


class TokenValidateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenValidateSerializer(data=request.data)

        if not serializer.is_valid():
            print("Token validation errors:", serializer.errors)
            return Response(
                {
                    "valid": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        # Get profile photo presigned URL
        profile_photo = None
        if hasattr(user, 'profile') and user.profile.avatar:
            profile_photo = generate_presigned_view(user.profile.avatar)

        return Response(
            {
                "valid": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_photo": profile_photo,
                },
            },
            status=status.HTTP_200_OK,
        )
