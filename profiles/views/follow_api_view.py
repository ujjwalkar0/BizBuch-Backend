from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from accounts.models import User
from profiles.services import FollowService
from profiles.serializers import FollowActionSerializer, FollowResponseSerializer


@extend_schema(tags=["Follows"])
class FollowProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowActionSerializer

    @extend_schema(
        request=FollowActionSerializer,
        responses=FollowResponseSerializer,
        description="Follow a user profile",
    )

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)

        try:
            FollowService.follow(request.user, target_user)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=400
            )

        return Response({"detail": "Followed successfully"})
