from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from profiles.models import Profile
from profiles.serializers import ProfileCompactSerializer
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Profiles"])
class ProfileListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCompactSerializer
    filter_backends = [SearchFilter]
    search_fields = ["display_name"]

    def get_queryset(self):
        return Profile.objects.filter(is_public=True).exclude(user=self.request.user).select_related("user")