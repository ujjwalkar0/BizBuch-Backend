from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from uploads.serializers import (
    PresignUploadRequestSerializer,
    PresignUploadResponseSerializer,
)
from uploads.services import generate_presigned_upload


class PresignUploadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    serializer_class = PresignUploadRequestSerializer

    def post(self, request):
        serializer = PresignUploadRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        result = generate_presigned_upload(
            user_id=request.user.id,
            content_type=serializer.validated_data["contentType"],
        )

        return Response(
            PresignUploadResponseSerializer(result).data
        )
