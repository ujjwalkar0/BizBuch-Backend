from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from profiles.models import ProfileFollow, Profile
from profiles.serializers import ProfileCompactSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Follows"])
class FollowingListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCompactSerializer

    def get_queryset(self):
        return Profile.objects.filter(
            user__following__follower_id=self.kwargs["pk"]
        )
