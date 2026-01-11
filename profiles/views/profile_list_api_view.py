from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from profiles.models import Profile
from profiles.serializers import ProfileCompactSerializer
from rest_framework.filters import SearchFilter

class ProfileListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCompactSerializer
    queryset = Profile.objects.filter(is_public=True).select_related("user")

    filter_backends = [SearchFilter]
    search_fields = ["display_name"]